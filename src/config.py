from pathlib import Path

# All paths are absolute so the app works from any working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"

RESUME_PATH = DATA_DIR / "resume" / "resume.pdf"
GITHUB_DIR = DATA_DIR / "github"
INDEX_PATH = STORAGE_DIR / "faiss_index" / "index.faiss"
METADATA_PATH = STORAGE_DIR / "faiss_index" / "chunks.json"

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

DEFAULT_K = 5
CHUNK_MAX_CHARS = 900
