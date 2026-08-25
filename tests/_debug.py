import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.retrieve import Retriever

r = Retriever()
queries = [
    "What internships or work positions has Manas held?",
    "Where did Manas work as a Technical Intern?",
    "Is Manas president of any club?",
]
for q in queries:
    hits = r.retrieve(q, k=3)
    print("Q:", q)
    for h in hits:
        md = h.metadata
        if md["source"] == "linkedin":
            label = f"linkedin[{md['file']}/{md['category']}]"
        elif md["source"] == "github":
            label = f"github[{md.get('repo')}]"
        else:
            label = f"{md['source']}/{md.get('section', '')}"
        print("  %.3f [%s] %s" % (h.score, label, " ".join(h.text.split())[:70]))
