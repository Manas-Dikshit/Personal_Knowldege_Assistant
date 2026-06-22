from src.ingest import load_all_data
from src.chunk import chunk_resume, chunk_readme, chunk_contribution
from src.embed import get_embeddings
from src.vectorstore import VectorStore
from src.retrieve import Retriever
from src.rag import RAG


def build_dataset():
    data = load_all_data()
    chunks = []

    chunks += chunk_resume(data["resume"])

    for r in data["readmes"]:
        c = chunk_readme(r["text"])
        chunks += [f"[{r['repo']}] {x}" for x in c]

    chunks += chunk_contribution(data["contribution"])

    return chunks


def main():
    print("Building knowledge base...")

    chunks = build_dataset()
    embeddings = get_embeddings(chunks)

    store = VectorStore(dim=embeddings.shape[1])
    store.add(embeddings, chunks)
    store.save()

    print("RAG READY")

    retriever = Retriever(dim=embeddings.shape[1])
    rag = RAG(retriever)

    print("\nAsk questions (type exit)\n")

    while True:
        q = input("You: ")

        if q == "exit":
            break

        answer = rag.generate(q)

        print("\n🤖", answer, "\n")


if __name__ == "__main__":
    main()