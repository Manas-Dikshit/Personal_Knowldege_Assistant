import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.retrieve import Retriever

r = Retriever()

# query -> expected source type(s) in top hits
checks = [
    ("LinkedIn work experience at The Good Shelf", "linkedin", "positions"),
    ("What degree did Manas study and where?", None, None),  # multi-source
    ("Is English a listed language and at what proficiency?", "linkedin", "languages"),
    ("Google cloud computing certification", "linkedin", "certifications"),
    ("Neutrino AI project chatbot mental health", "linkedin", "projects"),
    ("How many connections does Manas have on LinkedIn?", "linkedin", "connections"),
    ("What job titles is Manas seeking as an intern?", "linkedin", "job seeker preferences"),
    ("RabbitMQ skill", "linkedin", "skills"),
    ("President of AWS Cloud Club SUIIT", "linkedin", "positions"),
]

all_ok = True
for q, want_source, want_cat in checks:
    hits = r.retrieve(q, k=3)
    print(f"\nQ: {q}")
    ok = bool(hits)
    matched = False
    for h in hits:
        md = h.metadata
        if md["source"] == "linkedin":
            label = f"linkedin[{md['file']} / {md['category']} rows {md['row_start']}-{md['row_end']}]"
        elif md["source"] == "github":
            label = f"github[{md.get('repo')} / {md.get('section') or '(intro)'}]"
        else:
            label = f"{md['source']} / {md.get('section') or ''}"
        snippet = " ".join(h.text.split())[:85]
        print(f"  {h.score:.3f} [{label}] {snippet}")
        if (want_source and md["source"] == want_source
                and (want_cat is None or md.get("category") == want_cat)):
            matched = True
    if want_source:
        ok &= matched
        if not matched:
            print("  !! expected a", want_source, "hit in top-3")
    all_ok &= ok
    assert ok, f"failed: {q}"

print("\nALL LINKEDIN RETRIEVAL CHECKS PASSED")
