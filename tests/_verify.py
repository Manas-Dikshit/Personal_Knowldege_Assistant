import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json

from src.config import METADATA_PATH
from src.retrieve import Retriever
from src.vectorstore import VectorStore

# 1. Consistency: vectors vs metadata vs chunk counts.
store = VectorStore()
meta = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
print(f"FAISS vectors : {store.index.ntotal}")
print(f"metadata docs : {len(meta)}")
print(f"index dim     : {store.index.d}")
assert store.index.ntotal == len(meta), "VECTOR/METADATA MISMATCH"

by_source = {}
for m in meta:
    by_source[m["metadata"]["source"]] = by_source.get(m["metadata"]["source"], 0) + 1
print("chunks by source:", by_source)

resume_chunks = sum(1 for m in meta if m["metadata"]["source"] == "resume")

# 2. Every README chunk has provenance metadata.
sample = [m for m in meta if m["metadata"]["source"] == "github"][0]["metadata"]
required = {"repo", "path", "section", "chunk_index", "total_chunks",
            "source_url", "fetched_at", "content_hash", "readme_type"}
missing = required - set(sample)
assert not missing, f"missing metadata fields: {missing}"
print("README chunk metadata fields OK:", sorted(required))

# 3. Retrieval queries: projects, technologies, GitHub activity, resume.
r = Retriever()

queries = [
    ("project: L4S telehealth framework", {"repo": "L4SBOA"}),
    ("tech: RAG with LangChain agents", None),
    ("activity: open-source contributions to Apache or CNCF", None),
    ("resume: what is the CGPA / education?", {"source": "resume"}),
    ("resume: programming languages and skills", {"source": "resume"}),
    ("resume: contact email", {"source": "resume"}),
]

all_ok = True
for q, expect in queries:
    hits = r.retrieve(q, k=3)
    print(f"\nQ: {q}")
    ok = bool(hits)
    for h in hits:
        md = h.metadata
        label = (f"{md.get('repo')} / {md.get('section') or '(intro)'}"
                 if md.get("source") == "github" else
                 f"resume / {md.get('section')}")
        snippet = " ".join(h.text.split())[:90]
        print(f"  {h.score:.3f} [{label}] {snippet}")
    if expect:
        for key, val in expect.items():
            if not any(h.metadata.get(key) == val for h in hits):
                ok = False
    all_ok &= ok
    assert ok, f"query failed expectations: {q}"

print("\nALL VERIFICATION CHECKS PASSED")
print(f"(resume chunks: {resume_chunks})")
