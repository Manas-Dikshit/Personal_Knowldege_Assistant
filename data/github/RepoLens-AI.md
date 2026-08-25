# RepoLens AI

> Understand any GitHub repository in under one minute using lightweight local AI.

RepoLens AI is a Chrome extension + local backend that reads a GitHub
repository's metadata, README, and structure, then uses a **locally
downloaded Hugging Face model** (`Qwen/Qwen2.5-1.5B-Instruct` by default)
to generate a beginner-friendly summary — entirely offline after setup.
No OpenAI, Claude, Gemini, Groq, Together AI, or Ollama involved.

## Features

- Automatic GitHub repository detection as you browse
- Real local AI inference via `transformers` + downloaded `.safetensors`
  weights — no cloud API calls for summarization
- Structured summary: overview, purpose, key features, tech stack,
  project structure, important files, how it works, suggested learning
  order, target audience, difficulty, and contribution-friendliness
- No hallucinated details — the model is instructed to say
  "Information not available in repository." when data is missing
- Clean, GitHub-themed dark mode popup UI
- Copy-to-clipboard and one-click refresh
- Structured logging and typed error handling throughout the backend
- Unit tests for the analyzer, prompt builder, and validators

## Folder Structure

```
repolens-ai/
├── backend/                 FastAPI backend + local model inference
│   ├── app/
│   │   ├── main.py          FastAPI app, routes, error handlers
│   │   ├── config.py        All configurable values (env-driven)
│   │   ├── logging_config.py
│   │   ├── schemas.py       Pydantic request/response models
│   │   ├── models/
│   │   │   └── inference.py Local HF model loader + generate()
│   │   ├── services/
│   │   │   ├── github_analyzer.py
│   │   │   ├── prompt_builder.py
│   │   │   └── summarizer.py
│   │   └── utils/
│   │       ├── errors.py
│   │       └── validators.py
│   ├── scripts/
│   │   └── download_models.py   Standalone model downloader
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── extension/                TypeScript Chrome extension (Manifest V3)
│   ├── manifest.json
│   ├── src/
│   │   ├── popup/            Popup UI (HTML/CSS/TS + markdown renderer)
│   │   ├── background/       Service worker
│   │   ├── content/          GitHub repo-page detector
│   │   └── utils/            Shared types + API client
│   ├── icons/
│   ├── package.json
│   ├── tsconfig.json
│   ├── .eslintrc.json
│   └── .prettierrc
└── docs/
    ├── ARCHITECTURE.md        Mermaid diagrams
    ├── DEPLOYMENT.md          Windows / Linux / macOS setup
    ├── CHROME_SETUP.md        Beginner-friendly extension guide
    └── TROUBLESHOOTING.md
```

## Architecture (short version)

```
Browser Extension → Backend (FastAPI) → Repository Analyzer (GitHub API)
                                       → Prompt Builder
                                       → Local Hugging Face Model
                                       → Generated Summary → Popup UI
```

Full diagrams (system, sequence, folder structure) live in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Quick Start

```bash
# 1. Backend setup
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # optional: set HF_TOKEN, tweak model, etc.

# 2. Download the model (one-time, ~1-3 GB depending on model)
python scripts/download_models.py

# 3. Run the backend
uvicorn app.main:app --host 127.0.0.1 --port 8765

# 4. In a second terminal: build the extension
cd ../extension
npm install
npm run build

# 5. Load extension/ as an unpacked extension in chrome://extensions
#    (Developer mode → Load unpacked → select the `extension` folder)

# 6. Open any GitHub repository and click "Analyze Repository"
```

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for OS-specific instructions
and [`docs/CHROME_SETUP.md`](docs/CHROME_SETUP.md) for a fully guided,
beginner-friendly walkthrough with screenshots-to-be.

## Python Version

Python **3.12+** is required (uses modern typing syntax like `str | None`).

## Configuration

All configurable values live in `backend/app/config.py`, sourced from
`backend/.env` (copy `backend/.env.example` to start). This includes the
model name/path, HF token, host/port, timeouts, max repository size, and
max README length.

## Running Tests

```bash
cd backend
pip install -r requirements.txt   # includes pytest, pytest-asyncio
pytest -q
```

## Model Details

| Setting | Default |
|---|---|
| Model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Alternative (faster/smaller) | `Qwen/Qwen2.5-0.5B-Instruct` |
| Download method | `huggingface_hub.snapshot_download` with `allow_patterns` |
| Files downloaded | `*.safetensors`, `*.json` (config/tokenizer), `tokenizer*`, `merges.txt`, `vocab.json` |
| Inference | `transformers` `AutoModelForCausalLM` + `AutoTokenizer`, `local_files_only=True` |
| Network required at inference time | No |

Switch models by setting `MODEL_NAME` in `backend/.env` and re-running
`python scripts/download_models.py`.

## Troubleshooting

See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for common issues:
missing model, backend unreachable, GitHub rate limits, invalid HF token,
and more.

## Future Improvements

- Multi-turn Q&A about the repository inside the popup
- Support for GitLab/Bitbucket
- Streaming token-by-token summary rendering
- Optional GPU batch pre-warming for teams analyzing many repos
- Packaged, signed `.crx` release instead of "load unpacked" only

## Screenshots

_Add screenshots of the popup (idle state, loading state, and completed
summary) here once you've built and loaded the extension._

- `docs/screenshots/popup-idle.png`
- `docs/screenshots/popup-loading.png`
- `docs/screenshots/popup-summary.png`

## License

MIT — see `LICENSE`
