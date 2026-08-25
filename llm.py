from typing import Optional

from src.config import DEFAULT_K, LLM_MODEL
from src.rag import RAG
from src.retrieve import Retriever


class MRDAI:
    """
    Main entry point for the assistant.

    Provides a clean ask() interface. The embedding model and FAISS
    index are loaded lazily on first use so importing this module is cheap.
    """

    def __init__(
        self,
        top_k: int = DEFAULT_K,
        model: str = LLM_MODEL
    ):
        self.top_k = top_k
        self.model = model
        self._rag: Optional[RAG] = None

    def _ensure_ready(self) -> None:
        if self._rag is None:
            self._rag = RAG(
                retriever=Retriever(default_k=self.top_k),
                model=self.model
            )

    def ask(
        self,
        question: str
    ) -> str:
        """
        Generate an answer.
        """

        if not question or not question.strip():
            return "Please provide a question."

        try:
            self._ensure_ready()
        except (ValueError, RuntimeError) as exc:
            return (
                f"Knowledge base unavailable: {exc}. "
                "Build it first with 'python main.py'."
            )

        return self._rag.ask(
            question,
            k=self.top_k
        )


# Singleton instance (lazy: nothing loads until first ask()).
mrd_ai = MRDAI()


# ------------------------------------------------------------------
# Example
# ------------------------------------------------------------------

if __name__ == "__main__":

    while True:

        query = input("\nYou: ").strip()

        if query.lower() in {
            "exit",
            "quit"
        }:
            break

        response = mrd_ai.ask(query)

        print("\nMRD:", response)
