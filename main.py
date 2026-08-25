from llm import MRDAI
from src.chunk import (
    chunk_resume,
    chunk_readme,
    chunk_contribution
)
from src.embed import get_embeddings
from src.ingest import load_all_data
from src.vectorstore import VectorStore


def build_documents():
    """
    Build chunked documents with metadata.
    """

    data = load_all_data()

    documents = []

    # Resume
    if data["resume"]["text"]:

        for chunk in chunk_resume(data["resume"]["text"]):
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

        for chunk in chunk_readme(repo["text"]):
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
    if data["contributions"]["text"]:

        for chunk in chunk_contribution(data["contributions"]["text"]):
            documents.append(
                {
                    "text": chunk,
                    "metadata": {
                        "source": "contributions"
                    }
                }
            )

    if not documents:
        raise RuntimeError(
            "No indexable content found. Check your data/ directory."
        )

    return documents


def build_index() -> int:
    """
    Create embeddings and populate FAISS. Returns the embedding dim.
    """

    print("\nBuilding knowledge base...\n")

    documents = build_documents()

    texts = [doc["text"] for doc in documents]
    metadata = [doc["metadata"] for doc in documents]

    embeddings = get_embeddings(texts)

    # Fresh index replaces any stale one on disk.
    store = VectorStore(
        dim=embeddings.shape[1],
        load_if_exists=False
    )
    store.add(
        embeddings=embeddings,
        texts=texts,
        metadata=metadata
    )
    store.save()

    print(f"Indexed {len(texts)} chunks.")
    print("Knowledge base ready.\n")

    return int(embeddings.shape[1])


def interactive_chat():
    """
    Start chat loop using the shared MRDAI pipeline.
    """

    assistant = MRDAI()

    print("MRD AI Ready")
    print("Type 'exit' to quit.\n")

    while True:

        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if question.lower() in {"exit", "quit"}:
            break

        answer = assistant.ask(question)

        print("\nMRD:", answer)
        print()


def main():
    build_index()
    interactive_chat()


if __name__ == "__main__":
    main()
