from src.ingest import load_all_data
from src.chunk import chunk_resume, chunk_readme, chunk_contribution
from src.embed import get_embeddings, embed_single
from src.vectorstore import VectorStore
from src.query import RAGQueryEngine
import numpy as np


# -------------------------
# BUILD DATASET
# -------------------------
def build_dataset():
    data = load_all_data()
    all_chunks = []

    # Resume
    resume_chunks = chunk_resume(data["resume"])
    all_chunks.extend(resume_chunks)

    # GitHub READMEs
    for r in data["readmes"]:
        chunks = chunk_readme(r["text"])
        tagged = [f"[REPO: {r['repo']}] {c}" for c in chunks]
        all_chunks.extend(tagged)

    # Contribution history
    contrib_chunks = chunk_contribution(data["contribution"])
    all_chunks.extend(contrib_chunks)

    return all_chunks


# -------------------------
# SIMPLE ANSWER FORMATTER
# -------------------------
def format_answer(question, chunks):
    """
    Converts raw retrieved chunks into readable output
    (lightweight "reasoning layer" without LLM)
    """

    answer = []
    answer.append("\n🤖 Answer")
    answer.append("=" * 40)

    answer.append(f"\n🧠 Based on your data, here is what I found about: '{question}'\n")

    for i, c in enumerate(chunks, 1):
        clean = c.replace("\n", " ").strip()
        answer.append(f"{i}. {clean}")

    answer.append("\n" + "=" * 40)

    return "\n".join(answer)


# -------------------------
# MAIN
# -------------------------
def main():
    print("🔄 Building knowledge base...")

    chunks = build_dataset()

    print(f"✅ Total chunks created: {len(chunks)}")

    print("🔄 Creating embeddings...")

    embeddings = get_embeddings(chunks)

    print("🔄 Initializing vector store...")

    store = VectorStore(dim=embeddings.shape[1])

    store.add(embeddings, chunks)
    store.save()

    print("🎉 RAG SYSTEM READY!")

    # -------------------------
    # QUERY ENGINE
    # -------------------------
    engine = RAGQueryEngine(dim=embeddings.shape[1])

    print("\n💬 Ask anything about your resume / GitHub (type 'exit' to stop)\n")

    while True:
        question = input("You: ")

        if question.lower() == "exit":
            break

        results = engine.ask(question)

        output = format_answer(question, results)

        print(output)
        print("\n")


if __name__ == "__main__":
    main()