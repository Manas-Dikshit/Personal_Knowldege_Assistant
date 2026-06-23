import json
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np


class VectorStore:
    """
    FAISS-backed vector store.
    """

    def __init__(
        self,
        dim: int,
        index_path: str = "storage/faiss_index/index.faiss",
        metadata_path: str = "storage/faiss_index/chunks.json"
    ):
        self.dim = dim

        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.index = faiss.IndexFlatIP(dim)

        # each item:
        # {
        #   "text": "...",
        #   "metadata": {...}
        # }
        self.documents: List[Dict] = []

        if self.index_path.exists():
            self.load()

    def add(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: List[Dict] | None = None
    ) -> None:
        """
        Add vectors and corresponding chunks.
        """

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32
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

        query_embedding = np.asarray(
            query_embedding,
            dtype=np.float32
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

            if idx < 0:
                continue

            if idx >= len(self.documents):
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
        Load index and metadata.
        """

        self.index = faiss.read_index(
            str(self.index_path)
        )

        if self.metadata_path.exists():

            with open(
                self.metadata_path,
                "r",
                encoding="utf-8"
            ) as f:

                self.documents = json.load(f)

        else:
            self.documents = []

    def __len__(self) -> int:
        return self.index.ntotal