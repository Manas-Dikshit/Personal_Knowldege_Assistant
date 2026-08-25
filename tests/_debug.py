import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.retrieve import Retriever

r = Retriever()

queries = [
    "What is the L4SBOA project about?",
    "Which repository deals with counterfactual explanations in machine learning?",
    "What does the AQI HCHO model do?",
    "Tell me about the telehealth network framework",
    "How do I install or use DiCE?",
]

for q in queries:
    hits = r.retrieve(q, k=3)
    print(f"\nQ: {q}")
    for h in hits:
        repo = h.metadata.get("repo", "?")
        section = h.metadata.get("section", "") or "(no section)"
        idx = h.metadata.get("chunk_index")
        tot = h.metadata.get("total_chunks")
        snippet = " ".join(h.text.split())[:110]
        print(f"  {h.score:.3f} [{repo} / {section} ({idx}/{tot})] {snippet}")
