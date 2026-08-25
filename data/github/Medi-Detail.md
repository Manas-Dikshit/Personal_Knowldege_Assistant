# Medicine Intelligence System

An AI-powered medicine information platform. Enter a medicine name or upload an image
(tablet strip, capsule strip, syrup bottle, injection, ointment, packaging, prescription)
and get structured **Basic** (general-public) and **Advanced** (clinical) information,
retrieved from medical knowledge sources and synthesized by an LLM with citations and
a confidence score.

> **Status of this repo:** this is a complete, runnable *architecture and vertical slice*.
> The AI providers (OCR / vision / embeddings / LLM) are implemented behind clean
> interfaces with **mock implementations** that return realistic, correctly-shaped data.
> This lets the full stack — UI, API, orchestration, retrieval contracts — run and be
> developed **today**, without GPUs or multi-gigabyte model downloads. Swapping in real
> models (Surya OCR, BiomedCLIP, BAAI/bge-large-en-v1.5, Qwen3-8B-Instruct, FAISS) is a
> matter of implementing the existing provider interfaces — see `docs/Model_Guide.md`.

## Why mock providers first

Real medical AI models are large (multi-GB weights), need a GPU for reasonable latency,
and depend on downloading licensed/public datasets (DrugBank, DailyMed, OpenFDA, RxNorm,
WHO ATC, MedlinePlus). None of that belongs in source control, and none of it can be
verified in a sandboxed build environment. So every AI capability is defined as an
interface (`OCRProvider`, `VisionClassifier`, `EmbeddingProvider`, `Retriever`,
`LLMProvider`) with a mock implementation registered by default. The moment a real
provider is implemented, it's swapped in via one line in `backend/app/core/config.py` —
nothing else in the app changes. This is the "AI inference layer abstracted behind
provider interfaces" requirement, made real rather than aspirational.

## Stack

- **Frontend:** Next.js 15 (App Router), TypeScript, Tailwind CSS, TanStack Query, React Hook Form + Zod
- **Backend:** FastAPI, Python 3.11+, Pydantic v2, dependency-injected provider architecture
- **Retrieval:** FAISS (interface ready; mock in-memory retriever ships by default)
- **LLM:** Qwen3-8B-Instruct (interface ready; mock LLM ships by default)

## Quick start (local dev)

```bash
# Frontend
cd src && npm install && npm run dev   # http://localhost:3000

# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local` (see `.env.example`).

## Repository layout

See `docs/Folder_Structure.md` for the full breakdown. See `docs/Architecture.md` for
the clean-architecture rationale and `docs/AI_Pipeline.md` for the end-to-end pipeline
this implements.

## Documentation index

| Doc | Purpose |
|---|---|
| `docs/Architecture.md` | Clean architecture, module boundaries, dependency rules |
| `docs/Installation.md` | Full local setup, env vars, troubleshooting first run |
| `docs/AI_Pipeline.md` | OCR → vision → retrieval → LLM pipeline, request lifecycle |
| `docs/Model_Guide.md` | How to replace each mock provider with the real model |
| `docs/Dataset_Guide.md` | Ingesting DrugBank/DailyMed/OpenFDA/RxNorm/WHO ATC/MedlinePlus |
| `docs/Vector_Database.md` | FAISS index design, chunking, metadata schema |
| `docs/Developer_Guide.md` | Coding standards, adding a feature, testing |
| `docs/Deployment_Guide.md` | Docker / Docker Compose / GPU / CPU / cloud |
| `docs/Folder_Structure.md` | Annotated directory tree |
| `docs/API_Documentation.md` | REST endpoints, request/response schemas |
| `docs/Contributing.md` | PR process, commit conventions |
| `docs/Troubleshooting.md` | Common issues |

## Medical disclaimer

This system provides informational content only and is **not** a substitute for
professional medical advice, diagnosis, or treatment. Every AI-generated response in
this app carries a disclaimer, a confidence score, and its retrieved sources — see
`docs/AI_Pipeline.md#explainability`.
