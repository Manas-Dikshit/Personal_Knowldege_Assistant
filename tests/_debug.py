import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.linkedin import parse_csv, load_linkedin_records

tmp = Path(tempfile.mkdtemp())
(tmp / "Broken.csv").write_text('Name,Value\n"a"a"b\n', encoding="utf-8")

try:
    h, r = parse_csv(tmp / "Broken.csv")
    print("parsed header:", h)
    print("rows:", r)
except Exception as e:
    print("raised:", type(e).__name__, ":", e)

# Also check what the full loader does with it
records, stats = load_linkedin_records(tmp)
print("records:", len(records), "stats:", stats)
