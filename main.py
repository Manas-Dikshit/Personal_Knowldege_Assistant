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

        resume_chunks = chunk_resume(data["resume"]["text"])
        total = len(resume_chunks)

        for i, chunk in enumerate(resume_chunks):
            documents.append(
                {
                    "text": chunk["text"],
                    "metadata": {
                        "source": "resume",
                        "section": chunk.get("section", ""),
                        "chunk_index": i + 1,
                        "total_chunks": total
                    }
                }
            )

    # GitHub repositories
    for repo in data["github"]:

        readme_chunks = chunk_readme(repo["text"])
        total = len(readme_chunks)

        for i, chunk in enumerate(readme_chunks):
            documents.append(
                {
                    "text": chunk["text"],
                    "metadata": {
                        "source": "github",
                        "repo": repo["repo"],
                        "path": repo["path"],
                        "section": chunk.get("section", ""),
                        "chunk_index": i + 1,
                        "total_chunks": total,
                        "source_url": repo.get("source_url", ""),
                        "fetched_at": repo.get("fetched_at", ""),
                        "content_hash": repo.get("content_hash", ""),
                        "readme_type": repo.get("readme_type", "")
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

    # LinkedIn exports (already chunked by the dedicated module)
    documents.extend(data["linkedin_chunks"])

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
