from src.retrieve import Retriever
from src.rag import RAG


class MRDAI:
    """
    Main entry point for the assistant.

    Responsibilities
    ----------------
    - Initialize retrieval layer
    - Initialize generation layer
    - Provide a clean ask() interface
    """

    def __init__(
        self,
        embedding_dim: int = 384,
        top_k: int = 5,
        model: str = "llama3"
    ):
        self.top_k = top_k

        self.retriever = Retriever(
            dim=embedding_dim,
            default_k=top_k
        )

        self.rag = RAG(
            retriever=self.retriever,
            model=model
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

        return self.rag.ask(
            question,
            k=self.top_k
        )


# Singleton instance
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