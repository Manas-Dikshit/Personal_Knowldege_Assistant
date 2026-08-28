# MRD AI Architecture

Everything runs **locally and free**: BGE embeddings for vectors, FAISS for storage/retrieval, and Ollama (Llama 3) for generation. No paid APIs.

```mermaid
flowchart TB
    %% ================= STYLING =================
    classDef source fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,color:#78350f
    classDef ingest fill:#dbeafe,stroke:#3b82f6,stroke-width:2px,color:#1e3a8a
    classDef storage fill:#fce7f3,stroke:#ec4899,stroke-width:2px,color:#831843
    classDef query  fill:#dcfce7,stroke:#22c55e,stroke-width:2px,color:#14532d
    classDef answer fill:#ede9fe,stroke:#8b5cf6,stroke-width:2.5px,color:#4c1d95
    classDef ui     fill:#e2e8f0,stroke:#64748b,stroke-width:2px,color:#1e293b
    classDef backend fill:#cffafe,stroke:#06b6d4,stroke-width:2px,color:#164e63
    classDef user   fill:#f1f5f9,stroke:#334155,stroke-width:3px,color:#0f172a

    %% ================= DATA SOURCES =================
    subgraph SOURCES["1 · Data Sources"]
        A1["Resume.pdf"]
        A2["GitHub Repositories<br/>README fetch — github_fetch.py"]
        A3["LinkedIn Exports<br/>CSV ingestion — linkedin.py"]
    end

    %% ================= INDEXING PIPELINE (OFFLINE) =================
    subgraph IDX["2 · Indexing Pipeline (offline build)"]
        direction LR
        B["ingest.py<br/>load PDF / md / txt"]
        C["chunk.py<br/>lossless, section-aware split"]
        E["embed.py<br/>BGE-small embeddings"]
        V["vectorstore.py<br/>FAISS + metadata persistence"]
    end

    %% ================= STORAGE =================
    subgraph SR["3 · Persistent Storage"]
        FAISS[("FAISS Index<br/>storage/faiss_index<br/>index.faiss + chunks.json")]
    end

    %% ================= QUERY PIPELINE (RUNTIME) =================
    subgraph RQ["4 · Query Pipeline (runtime, on each question)"]
        direction LR
        QE["Embed the query<br/>same BGE model"]
        RV["retrieve.py<br/>top-k semantic search"]
        PR["rag.py<br/>prompt construction"]
        OL["Ollama · llama3<br/>generation"]
        ANS["Human-like Answer"]
    end

    %% ================= INTERFACES =================
    subgraph IF["5 · User Interfaces"]
        direction LR
        U["You"]
        CLI["CLI Chat<br/>main.py"]
        WEB["Web Chat<br/>HTML / CSS / JS"]
    end

    %% ================= BACKEND =================
    subgraph BK["Backend"]
        direction LR
        API["FastAPI<br/>backend/app.py<br/>/chat endpoint"]
        FAC["MRD AI RAG Engine<br/>llm.py · facade"]
    end

    %% ================= FLOW: INDEX =================
    A1 --> B
    A2 --> B
    A3 --> B
    B --> C --> E --> V --> FAISS

    %% ================= FLOW: QUERY =================
    U --> CLI
    U --> WEB
    CLI --> FAC
    WEB --> API --> FAC
    FAC --- QE
    QE --> RV
    FAISS -. top-k.-> RV
    RV --> PR --> OL --> ANS
    ANS --> U

    %% ================= CLASSES =================
    class A1,A2,A3 source
    class B,C,E,V ingest
    class FAISS storage
    class QE,RV,PR,OL query
    class ANS answer
    class U user
    class CLI,WEB ui
    class API,FAC backend
    class SOURCES,IDX,SR,RQ,IF,BK source
```

## Pipeline walkthrough

| Stage | Script | What it does |
|---|---|---|
| **1. Data Sources** | `github_fetch.py`, `linkedin.py` | Collects the raw material: the resume PDF, the canonical README of every GitHub repo (byte-exact, via the GitHub REST API), and LinkedIn CSV exports (deduplicated). |
| **2. Indexing** | `ingest.py` → `chunk.py` → `embed.py` → `vectorstore.py` | Loads every source, splits it into **lossless** section-aware chunks (code blocks, tables and lists stay intact), embeds each chunk with **BGE-small**, and writes the vectors plus metadata to disk. |
| **3. Storage** | — | FAISS `IndexFlatIP` with `chunks.json` (original text + section + repo + provenance metadata). Rebuild with `python main.py`. |
| **4. Query** | `retrieve.py` → `rag.py` → Ollama | The user's question is embedded with the *same* BGE model, the **top-k** most similar chunks are retrieved from FAISS, assembled into a grounded prompt, and handed to **Llama 3** in Ollama. |
| **5. Interfaces** | `main.py`, `backend/app.py`, `frontend/` | Both the interactive CLI and the web chat route through the `llm.py` facade; the web path adds a FastAPI `/chat` API in front of it. The answer flows back to you. |