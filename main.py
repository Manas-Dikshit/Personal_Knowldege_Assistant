from src.ingest import load_all_data
from src.chunk import (
    chunk_resume,
    chunk_readme,
    chunk_contribution
)
from src.embed import get_embeddings
from src.vectorstore import VectorStore
from src.retrieve import Retriever
from src.rag import RAG


def build_documents():
    """
    Build chunked documents with metadata.
    """

    data = load_all_data()

    documents = []

    # Resume
    resume_chunks = chunk_resume(
        data["resume"]["text"]
    )

    for chunk in resume_chunks:
        documents.append(
            {
                "text": chunk,
                "metadata": {
                    "source": "resume"
                }
            }
        )

    # GitHub repositories
    for repo in data["github"]:

        repo_chunks = chunk_readme(
            repo["text"]
        )

        for chunk in repo_chunks:

            documents.append(
                {
                    "text": chunk,
                    "metadata": {
                        "source": "github",
                        "repo": repo["repo"],
                        "path": repo["path"]
                    }
                }
            )

    # Contribution history
    contribution_chunks = chunk_contribution(
        data["contributions"]["text"]
    )

    for chunk in contribution_chunks:

        documents.append(
            {
                "text": chunk,
                "metadata": {
                    "source": "contributions"
                }
            }
        )

    return documents


def build_index():
    """
    Create embeddings and populate FAISS.
    """

    print("\nBuilding knowledge base...\n")

    documents = build_documents()

    texts = [
        doc["text"]
        for doc in documents
    ]

    metadata = [
        doc["metadata"]
        for doc in documents
    ]

    embeddings = get_embeddings(texts)

    store = VectorStore(
        dim=embeddings.shape[1]
    )

    store.add(
        embeddings=embeddings,
        texts=texts,
        metadata=metadata
    )

    store.save()

    print(f"Indexed {len(texts)} chunks.")
    print("Knowledge base ready.\n")

    return embeddings.shape[1]


def interactive_chat():
    """
    Start chat loop.
    """

    retriever = Retriever(
        dim=384
    )

    rag = RAG(
        retriever=retriever,
        model="llama3"
    )

    print("MRD AI Ready")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("You: ").strip()

        if question.lower() in {
            "exit",
            "quit"
        }:
            break

        try:

            answer = rag.generate(
                question
            )

            print("\nMRD:", answer)
            print()

        except Exception as e:

            print(
                f"\nError: {e}\n"
            )


def main():

    # Build FAISS index
    build_index()

    # Start chatbot
    interactive_chat()


if __name__ == "__main__":
    main()