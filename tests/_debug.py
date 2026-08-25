import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chunk import chunk_readme, _normalize_markdown

failures = []
total_src = 0
total_chunks = 0

for f in sorted(Path("data/github").glob("*.md")):
    src = f.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_readme(src)
    total_chunks += len(chunks)
    src_key = "".join(_normalize_markdown(src).split())
    total_src += len(src_key)
    rebuilt = "".join(
        "".join("".join(c["text"].split()) for c in chunks).split()
    )
    if src_key != rebuilt:
        failures.append((f.name, len(src_key), len(rebuilt)))

print(f"files: {len(list(Path('data/github').glob('*.md')))}")
print(f"total content chars: {total_src}")
print(f"total chunks produced: {total_chunks}")
if failures:
    print("FAILURES:")
    for name, a, b in failures:
        print(f"  {name}: src={a} rebuilt={b}")
    sys.exit(1)
print("ALL FILES LOSSLESS")
