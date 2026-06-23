from typing import List, Dict, Optional
from dataclasses import dataclass

import numpy as np

from src.embed import embed_query
from src.vectorstore import VectorStore


@dataclass
class RetrievalResult:
    """
    Represents a retrieved chunk.
    """
    text: str
    score: float
    metadata: Dict


class RAGQueryEngine:
    """
    Retrieval layer for the RAG pipeline.

    Responsibilities
    ----------------
    - Embed user queries
    - Retrieve top-k chunks from the vector store
    - Return structured results
    - Build context for generation
    """

    def __init__(
        self,
        dim: int,
        default_k: int = 5
    ):
        self.store = VectorStore(dim=dim)
        self.default_k = default_k

    def retrieve(
        self,
        question: str,
        k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve top-k relevant chunks.

        Parameters
        ----------
        question : str
            User query.

        k : int, optional
            Number of chunks to retrieve.

        Returns
        -------
        List[RetrievalResult]
        """

        if not question or not question.strip():
            return []

        k = k or self.default_k

        query_embedding = embed_query(question)

        query_embedding = (
            np.asarray([query_embedding])
            .astype("float32")
        )

        results = self.store.search(
            query_embedding,
            k=k
        )

        retrieved_chunks = []

        for item in results:

            retrieved_chunks.append(
                RetrievalResult(
                    text=item.get("text", ""),
                    score=float(item.get("score", 0.0)),
                    metadata=item.get("metadata", {})
                )
            )

        return retrieved_chunks

    def build_context(
        self,
        question: str,
        k: Optional[int] = None
    ) -> str:
        """
        Combine retrieved chunks into a context string.
        """

        chunks = self.retrieve(
            question,
            k=k
        )

        if not chunks:
            return ""

        context_parts = []

        for chunk in chunks:
            context_parts.append(
                chunk.text.strip()
            )

        return "\n\n".join(context_parts)

    def ask(
        self,
        question: str,
        k: Optional[int] = None
    ) -> Dict:
        """
        Retrieve relevant context and return both
        context and sources.
        """

        chunks = self.retrieve(
            question,
            k=k
        )

        context = "\n\n".join(
            chunk.text
            for chunk in chunks
        )

        sources = []

        for chunk in chunks:

            source_info = {
                "score": round(chunk.score, 4),
                **chunk.metadata
            }

            sources.append(source_info)

        return {
            "question": question,
            "context": context,
            "chunks": chunks,
            "sources": sources
        }


# --------------------------------------------------------------------
# Example
# --------------------------------------------------------------------

if __name__ == "__main__":

    engine = RAGQueryEngine(
        dim=384
    )

    question = "What projects involve FastAPI?"

    response = engine.ask(
        question,
        k=5
    )

    print("\nQUESTION:\n")
    print(response["question"])

    print("\nCONTEXT:\n")
    print(response["context"])

    print("\nSOURCES:\n")

    for source in response["sources"]:
        print(source)