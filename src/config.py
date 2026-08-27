from pathlib import Path

# All paths are absolute so the app works from any working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"

RESUME_PATH = DATA_DIR / "resume" / "resume.pdf"
GITHUB_DIR = DATA_DIR / "github"
LINKEDIN_DIR = DATA_DIR / "linkedin"
INDEX_PATH = STORAGE_DIR / "faiss_index" / "index.faiss"
METADATA_PATH = STORAGE_DIR / "faiss_index" / "chunks.json"

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "llama3"
OLLAMA_URL = "http://localhost:11434/api/generate"

DEFAULT_K = 5
CHUNK_MAX_CHARS = 900

# ---------------------------------------------------------------------
# Source-aware ranking configuration
# ---------------------------------------------------------------------

# Priority weights per source — higher = more authoritative for that query type.
# Resume data is given highest priority for personal info questions,
# GitHub for project/skill questions, LinkedIn for profile/experience,
# Contributions for activity evidence.
SOURCE_PRIORITY = {
    "resume": 1.5,
    "github": 1.2,
    "linkedin": 1.1,
    "contributions": 1.0,
}

# Default reranking / dedup settings.
RERANK_ENABLED = True
RERANK_TOP_N = 20  # consider top N results for reranking/dedup
DEDUP_ENABLED = True
DEDUP_SCORE_TOLERANCE = 0.1  # score tolerance for near-duplicate removal
