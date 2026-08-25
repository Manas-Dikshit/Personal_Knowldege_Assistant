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
        dim: Optional[int] = None,
        default_k: int = 5
    ):
        self.store = VectorStore(dim=dim)
        self.default_k = default_k

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None
    ) -> List[RetrievedChunk]:

        if not query or not query.strip():
            return []

        if k is None:
            k = self.default_k

        # Embed query and shape for FAISS.
        query_embedding = np.asarray(
            [embed_query(query)],
            dtype=np.float32
        )

        results = self.store.search(
            query_embedding,
            k=k
        )

        return [
            RetrievedChunk(
                text=result["text"],
                score=result["score"],
                metadata=result["metadata"]
            )
            for result in results
        ]

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
