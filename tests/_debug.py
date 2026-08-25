import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from llm import mrd_ai

result = mrd_ai.ask_with_sources("What is your CGPA?")
print("answer:", result["answer"][:120])
print("sources:", result["sources"])
