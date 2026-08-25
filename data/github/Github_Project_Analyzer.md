# GitHub Repository Portfolio Analyzer

Analyzes every repository in a GitHub account (public + private, forks,
archived) and produces a ranked, evidence-based Top-10 list — plus a full
engineering scorecard for every repo — to help you decide what belongs on
your GitHub profile, resume, and job applications.

No AI/LLM APIs are used. All detection is static analysis: file structure,
manifests, config files, and source-code pattern matching.

## Features

- Fetches **all** repos via `GET /user/repos?visibility=all` (public, private, forks, archived)
- Parallel cloning + parallel analysis (configurable worker pool)
- Detects: tech stack (~70 frameworks/DBs/infra/AI libraries), architecture
  style, AI/ML capabilities, code quality signals, DevOps maturity,
  deployment platforms, and git activity health
- Configurable weighted scoring engine (0–100), producing an Engineering
  Score, Resume Score, and Portfolio Score per repo
- Three report formats: `ranking.json`, `ranking.md`, and an interactive
  dark-themed `ranking.html` dashboard (search, filters, charts, radar
  breakdown per repo)
- Bonus insights: top AI/backend/full-stack/DevOps/ML projects, repos
  needing improvement, duplicates, missing README/LICENSE/tests/deployment,
  and suggested repos to pin

## Project Structure

```
portfolio-analyzer/
    src/
        github/            # GitHub API client, repo fetcher, cloner
        analyzer/          # All detectors + scoring engine + orchestrator
        report/            # json / markdown / html report generators
        models/            # Typed dataclasses (Repository, Score, findings)
        utils/             # Logging, filesystem indexing
        config.py          # Settings loader (.env-driven)
        main.py            # Pipeline entry point
    tests/                 # Unit tests (pytest)
    cache/                 # Logs + internal cache
    cloned_repositories/   # Shallow clones land here
    reports/               # Generated ranking.json / .md / .html
    .env.example
    requirements.txt
```

## Setup

```bash
cd portfolio-analyzer
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set GITHUB_USERNAME and GITHUB_TOKEN (needs `repo` scope for private repos)
```

## Run

```bash
python -m src.main
```

Example terminal output:

```
Found 134 repositories

Cloning   : 100%|████████████████████| 134/134
Analyzing : 100%|████████████████████| 134/134

Top Projects

 1. KnowledgeSender                        96
 2. VoiceUp-India                          94
 3. StudentSync                            92
 ...

Reports written to: reports/
  - ranking.json
  - ranking.md
  - ranking.html
```

Open `reports/ranking.html` in a browser for the interactive dashboard.

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `GITHUB_USERNAME` | — | Your GitHub username |
| `GITHUB_TOKEN` | — | Personal Access Token with `repo` scope |
| `TOP_PROJECTS` | 10 | Size of the final ranked list |
| `MAX_WORKERS` | 8 | Parallelism for cloning + analysis |
| `CACHE_ENABLED` | true | Reserved for future response caching |
| `RECLONE` | false | Force re-clone even if already present locally |
| `INCLUDE_FORKS` | true | Include forked repos in analysis |
| `INCLUDE_ARCHIVED` | true | Include archived repos in analysis |
| `CLONE_DEPTH` | 1 | Git shallow-clone depth |

## Scoring Model

Each repo is scored across 10 weighted categories (default weights sum to
100 — see `src/config.py::DEFAULT_SCORE_WEIGHTS`, fully adjustable):

Problem Solving · Architecture · Code Quality · Documentation · Deployment ·
Testing · DevOps · AI/ML Complexity · Innovation · Production Readiness

From the raw breakdown, three top-level scores are derived:

- **Engineering Score** — the raw weighted total (0–100)
- **Resume Score** — reweighted toward documentation, production-readiness,
  deployment, testing, and code quality (what a recruiter skims for)
- **Portfolio Score** — reweighted toward innovation, architecture, and
  AI/ML complexity (what showcases engineering depth)

## Testing

```bash
pytest tests/ -v
```

Covers filesystem indexing, tech-stack/AI/architecture detectors, and the
scoring engine (including monotonicity — a stronger repo must never score
lower than a weaker one — and score bounding).

## Extending

- **New technology detection**: add a pattern to the relevant signature
  dict in `src/analyzer/tech_stack_detector.py` — no new parser needed.
- **New scoring category**: add a `_score_*` function in
  `src/analyzer/scoring_engine.py`, register it in `_SCORERS`, and add the
  weight to `DEFAULT_SCORE_WEIGHTS`.
- **New report format**: add a module under `src/report/` following the
  existing generators' signature (`list[RepositoryAnalysis] -> file`).

## Notes

- Cloning uses `--depth 1` for speed; git history analysis falls back to
  GitHub-API-derived recency (`pushed_at`) when a shallow clone can't
  expose full commit history.
- The GitHub token is injected into the clone URL in-memory only — it is
  never written to disk or logged (stderr from failed clones is scrubbed).
- Designed to scale to hundreds/thousands of repos: bounded per-file read
  sizes, single filesystem walk per repo, and a configurable thread pool
  for both cloning and analysis phases.
