# MRD Personal Knowledge Assistant

A personal AI assistant powered by Retrieval-Augmented Generation (RAG) that understands my projects, resume, GitHub activity, and technical background.

Instead of hardcoding information, the assistant builds a knowledge base from my own data and uses semantic search + LLM reasoning to answer questions naturally.

The goal is simple:

> Anyone should be able to ask questions about me and receive AI-generated answers as if they were talking directly to me.

Everything runs **locally and free**: FAISS for vectors, a local embedding model, and Ollama for generation. No paid APIs.

---

## Features

- Resume understanding (PDF)
- GitHub repository knowledge
- Contribution history support
- Semantic retrieval with FAISS
- AI-generated answers with Ollama (Llama 3)
- Web chat interface (FastAPI backend + vanilla HTML/JS frontend)
- Interactive CLI chat mode
- Graceful handling of missing data and offline Ollama

## Tech Stack

| Layer | Technology |
|---|---|
| Embeddings | BAAI/bge-small-en-v1.5 (sentence-transformers) |
| Vector DB | FAISS (IndexFlatIP) |
| LLM | Ollama (llama3) |
| Backend | Python, FastAPI |
| Frontend | HTML / CSS / JavaScript |

## Project Structure

```text
Personal_Knowledge_Assistant
├── data/
│   ├── resume/resume.pdf
│   ├── github/            # fetched raw READMEs + readme_meta.json
│   └── linkedin/          # private LinkedIn CSV exports (git-ignored)
│       ├── Repo.md
│       └── contribution-history.txt
├── src/
│   ├── config.py          # centralized paths & model constants
│   ├── ingest.py          # load PDF / markdown / txt sources
│   ├── chunk.py           # text cleaning + section-aware chunking
│   ├── linkedin.py        # LinkedIn CSV export ingestion
│   ├── embed.py           # BGE embeddings (lazy-loaded singleton)
│   ├── vectorstore.py     # FAISS index + metadata persistence
│   ├── retrieve.py        # top-k retrieval layer
│   ├── rag.py             # prompt construction + Ollama call
│   └── github_fetch.py    # fetch repos/readmes from the GitHub API
├── backend/
│   ├── app.py             # FastAPI server (/chat endpoint)
│   └── schemas.py         # request/response models
├── frontend/
│   ├── index.html         # chat UI
│   ├── script.js
│   └── styles.css
├── tests/
│   └── test_pipeline.py   # minimal self-checks (no model needed)
├── storage/faiss_index/   # generated: index.faiss + chunks.json
├── llm.py                 # MRDAI facade (used by backend & CLI)
├── main.py                # build index + interactive CLI chat
└── requirements.txt
```

## How It Works

1. `github_fetch.py` fetches the **canonical README of every repository** via the GitHub REST API (`GET /repos/{user}/{repo}/readme` — never HTML scraping). The token is read from the `GITHUB_TOKEN` env var or a `.env` file (see `.env.example`), but the pipeline works without one for public repos.
2. `main.py` loads all sources (`ingest.py`), splits them into chunks preserving section structure (`chunk.py`), embeds them (`embed.py`), and stores everything in FAISS (`vectorstore.py`). The resume PDF is chunked losslessly by section as well.
3. On each question, the query is embedded, top-k chunks are retrieved, combined into a prompt, and sent to Ollama.
4. The answer is returned via CLI or the `/chat` API to the web frontend.

### README fetching (`src/github_fetch.py`)

- Lets GitHub pick the default README regardless of name, case, or extension (`README.md`, `README.rst`, `README.txt`, plain `README`, ...).
- Stores each raw README **byte-exact** at `data/github/{repo}.md`; no headers or cleaning are injected before chunking.
- Provenance metadata (source URL, fetched timestamp, SHA-256 content hash, README type, GitHub SHA) lives in `data/github/readme_meta.json`.
- Content hashes detect change: identical content is not rewritten; changed (stale) files are replaced.
- Retries with backoff on network/5xx errors, honors timeouts, and reports rate limits clearly.
- Detects truncated responses and falls back to the raw download URL for non-UTF-8 files (e.g., UTF-16) with BOM-aware decoding.
- Rejects empty/suspiciously short READMEs and removes stale local copies for repos whose README disappeared upstream.

### LinkedIn CSV ingestion (`src/linkedin.py`)

Drop your LinkedIn export ZIP contents into `data/linkedin/` (kept private via `.gitignore`). The importer:

- Discovers every `.csv` recursively; nothing is hardcoded — categories come from file names, rendering is schema-driven.
- Handles UTF-8/UTF-16/BOM encodings, quoted fields, commas and newlines inside fields, empty values, ragged rows, and Connections-style preamble notes.
- Converts each record into semantic text (`LinkedIn positions record: Company Name: ... Title: ...`) with metadata for source file, category, and exact CSV row range.
- Deduplicates identical records across exports by content hash.
- One malformed file never blocks the others; failures are reported per file.

### Lossless chunking (READMEs and resume)

Both READMEs and the resume use a lossless splitter with a hard guarantee: **the concatenation of all chunks contains the complete original text** — every heading, paragraph, list row, table row, code line, and single-line item appears exactly once, in order.

- Headings stay attached to their sections; each chunk records its `section` title in metadata.
- Fenced code blocks are never split open, and `#` lines inside them are not treated as headings.
- Tables and lists are kept as contiguous blocks.
- Small sections are packed together instead of being dropped; oversized blocks are split at line boundaries.
- Chunk metadata includes repo name, path, section title, chunk index, plus fetch provenance for README chunks.
- `tests/test_pipeline.py` verifies losslessness, truncation retries, encoding fallbacks, stale replacement, and more; run `tests/verify_index.py` after a rebuild to check index consistency and retrieval quality.

## Setup

Requires Python 3.10+, [Ollama](https://ollama.com), and a local clone of this repo.

```bash
pip install -r requirements.txt

# one-time: pull the LLM
ollama pull llama3

# optional: fetch fresh GitHub data (set GITHUB_TOKEN to avoid rate limits)
copy .env.example .env          # then put your token in it (git-ignored)
python src/github_fetch.py

# build/rebuild the FAISS knowledge base, then start the CLI chat
python main.py
```

### Web UI

```bash
# terminal 1 (keep ollama serve running)
ollama serve

# terminal 2
uvicorn backend.app:app --port 8000
```

Open `frontend/index.html` in a browser (or serve it with any static server).

### Run checks

```bash
python tests/test_pipeline.py    # or: pytest tests
```

## Notes & Limitations

- The first question after startup is slow while models load; later ones are fast.
- If Ollama isn't running you get a friendly message instead of a crash — start it with `ollama serve`.
- If `storage/faiss_index/` is missing or out of sync with your data, rebuild with `python main.py`.
- Answers are grounded in retrieved context but LLM output can still be inaccurate; verify important details.
