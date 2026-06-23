from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from src.embed import embed_query
from src.vectorstore import VectorStore


@dataclass
class RetrievedChunk:
    text: str
    score: float
    metadata: Dict


class Retriever:

    def __init__(
        self,
        dim: int,
        default_k: int = 5
    ):
        self.store = VectorStore(dim=dim)
        self.default_k = default_k

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[RetrievedChunk]:

        if not query.strip():
            return []

        k = k or self.default_k

        # Embed query
        query_embedding = embed_query(query)

        # Shape for FAISS
        query_embedding = (
            np.asarray([query_embedding])
            .astype(np.float32)
        )

        # Search vector store
        results = self.store.search(
            query_embedding,
            k=k
        )

        chunks = []

        for result in results:

            chunks.append(
                RetrievedChunk(
                    text=result["text"],
                    score=result["score"],
                    metadata=result["metadata"]
                )
            )

        return chunks

    def search(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Alias for compatibility.
        """
        return self.retrieve(
            query,
            k
        )

    def get_context(
        self,
        query: str,
        k: Optional[int] = None
    ) -> str:

        chunks = self.retrieve(
            query,
            k
        )

        return "\n\n".join(
            chunk.text
            for chunk in chunks
        )