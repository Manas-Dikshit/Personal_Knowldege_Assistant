import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.linkedin import chunk_linkedin

tmp = Path(tempfile.mkdtemp())
rows = "\n".join(f"Skill{i}," for i in range(50))
(tmp / "Skills.csv").write_text("Name,\n" + rows + "\n", encoding="utf-8")

chunks, stats = chunk_linkedin(tmp)
print("chunks:", len(chunks), "records:", stats["records"])
for c in chunks[:4]:
    print({k: v for k, v in c["metadata"].items()})
