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

# Priority per source — higher = more authoritative for tied/borderline
# results. Resume/std profile data wins on conflict, then GitHub, then
# LinkedIn, then raw contribution logs.
SOURCE_PRIORITY = {
    "resume": 1.5,
    "github": 1.2,
    "linkedin": 1.1,
    "contributions": 1.0,
}

# How strongly source priority affects the final score: 0 disables the
# boost (pure semantic ordering), larger values push authoritative
# sources up harder. Scores stay bounded in [~0, 1] since the boost is
# multiplicative: score *= (1 + (priority - 1) * SOURCE_BOOST_STRENGTH).
SOURCE_BOOST_STRENGTH = 0.2

# Reranking / deduplication toggles.
RERANK_ENABLED = True
RERANK_TOP_N = 20  # how many candidates to fetch before ranking

DEDUP_ENABLED = True
# Token-containment overlap (fraction of the smaller chunk's tokens that
# appear in a kept one) above which two same-source chunks count as a
# near-duplicate. 1.0 = exact duplicates only.
DEDUP_THRESHOLD = 0.85

