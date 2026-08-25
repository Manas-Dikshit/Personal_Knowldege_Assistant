import json
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import numpy as np

from src.config import INDEX_PATH, METADATA_PATH


class VectorStore:
    """
    FAISS-backed vector store.

    If an index already exists on disk it is loaded and its dimension
    takes precedence; `dim` is only required when building a fresh index.
    """

    def __init__(
        self,
        dim: Optional[int] = None,
        index_path: Path = INDEX_PATH,
        metadata_path: Path = METADATA_PATH
    ):
        self.dim = dim

        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        # each item:
        # {
        #   "text": "...",
        #   "metadata": {...}
        # }
        self.documents: List[Dict] = []

        if self.index_path.exists():
            self.load()
            return

        if dim is None:
            raise ValueError(
                "No existing index found; a 'dim' is required to create one."
            )

        self.index = faiss.IndexFlatIP(dim)

    def add(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: Optional[List[Dict]] = None
    ) -> None:
        """
        Add vectors and corresponding chunks.
        """

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
        )

        if len(texts) != len(embeddings):
            raise ValueError(
                f"texts ({len(texts)}) and embeddings "
                f"({len(embeddings)}) length mismatch."
            )

        if self.index.d != embeddings.shape[1]:
            raise ValueError(
                f"Embedding dim {embeddings.shape[1]} does not match "
                f"index dim {self.index.d}."
            )

        if len(embeddings) == 0:
            return

        self.index.add(embeddings)

        if metadata is None:
            metadata = [{} for _ in texts]

        for text, meta in zip(texts, metadata):

            self.documents.append(
                {
                    "text": text,
                    "metadata": meta
                }
            )

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5
    ) -> List[Dict]:
        """
        Retrieve top-k results.
        """

        if self.index.ntotal == 0:
            return []

        k = max(1, min(k, self.index.ntotal))

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
        ).reshape(1, -1)

        if query_embedding.shape[1] != self.index.d:
            raise ValueError(
                f"Query dim {query_embedding.shape[1]} does not match "
                f"index dim {self.index.d}."
            )

        scores, indices = self.index.search(
            query_embedding,
            k
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0]
        ):

            if idx < 0 or idx >= len(self.documents):
                continue

            doc = self.documents[idx]

            results.append(
                {
                    "text": doc["text"],
                    "score": float(score),
                    "metadata": doc["metadata"]
                }
            )

        return results

    def save(self) -> None:
        """
        Persist index and metadata.
        """

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        self.metadata_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(self.index_path)
        )

        with open(
            self.metadata_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.documents,
                f,
                ensure_ascii=False,
                indent=2
            )

    def load(self) -> None:
        """
        Load index and metadata. The stored index's dim wins over any
        passed-in value so stale callers can't corrupt the store.
        """

        self.index = faiss.read_index(
            str(self.index_path)
        )

        self.dim = int(self.index.d)

        if self.metadata_path.exists():

            with open(
                self.metadata_path,
                "r",
                encoding="utf-8"
            ) as f:

                self.documents = json.load(f)

            # Index and metadata must stay in sync.
            if len(self.documents) != self.index.ntotal:
                raise RuntimeError(
                    f"Corrupted index: {self.index.ntotal} vectors but "
                    f"{len(self.documents)} documents. Rebuild with "
                    "'python main.py'."
                )

        elif self.index.ntotal > 0:
            raise RuntimeError(
                f"Missing metadata file for existing index "
                f"({self.index.ntotal} vectors). Rebuild with 'python main.py'."
            )

        else:
            self.documents = []

    def __len__(self) -> int:
        return self.index.ntotal
