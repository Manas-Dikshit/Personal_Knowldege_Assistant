import sys
import tempfile
import csv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

tmp = Path(tempfile.mkdtemp())
content = "\n".join([
    "Notes:",
    '"Some long note about email visibility, and more."',
    "",
    "First Name,Last Name,Email Address,Company",
    "Ada,Lovelace,ada@example.com,Analytical Engines Inc",
    'Grace,"Hopper, Rear Admiral","navy@usn.mil","""Big Co""",\nUnited States Fleet"',
]) + "\n"
p = tmp / "Connections.csv"
p.write_text(content, encoding="utf-8")

from src.linkedin import parse_csv, load_linkedin_records

try:
    header, rows = parse_csv(p)
    print("header:", header)
    for row_number, values in rows:
        print(row_number, values)
except Exception as e:
    print("parse error:", type(e).__name__, e)

records, stats = load_linkedin_records(tmp)
print("stats:", {k: v for k, v in stats.items() if k != "skipped"})
for r in records:
    print("---")
    print(r["text"])
