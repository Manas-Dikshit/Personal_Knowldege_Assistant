import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.chunk import chunk_readme

md = "\n".join([
    "# Project",
    "",
    "Intro paragraph.",
    "",
    "### Code",
    "",
    "```python",
    "# not a heading",
    "def f():",
    "    pass",
    "```",
    "",
    "## Table",
    "",
    "| Col A | Col B |",
    "|-------|-------|",
    "| 1     | 2     |",
])

for c in chunk_readme(md):
    print(repr(c["section"]), "|", repr(c["text"][:70]))
