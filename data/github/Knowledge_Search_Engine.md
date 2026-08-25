# Knowledge Search Engine

A search engine that doesn't show you links — it shows you the **best** links.

Enter a topic (and optional context), and the system searches multiple trusted sources
in parallel, scores every result for authority/popularity/freshness/trust, removes
duplicates, and returns a ranked, categorized shortlist. It is not a chatbot, not a RAG
system, and not a course marketplace — it's a quality filter on top of the open web.

```
User: "Learn FastAPI for production backend"
  → searches GitHub, Stack Overflow, Dev.to, Hashnode, Reddit (keyless)
  → and Google / YouTube / official docs (when API keys are configured)
  → scores, dedupes, ranks
  → returns: Official Docs, Videos, GitHub Repos, Articles, Blogs, Communities
```

## Project overview

- **Frontend**: Next.js 14 App Router, TypeScript, Tailwind, dark glassmorphism UI
- **Backend**: Next.js Route Handlers (Node runtime), Zod-validated
- **Architecture**: Provider pattern + Factory, independent Ranking Engine, pluggable cache
- **No fake data**: every provider hits a real, live API. Providers that need a paid/keyed
  API (Google, YouTube) simply return zero results until you add the key — the pipeline
  degrades gracefully rather than faking a response.

## Features

- 8 registered search providers (5 work with zero configuration)
- Query expansion (acronym expansion + intent-suffix fan-out) before searching
- Quality scoring engine: base source score, official-source bonus, popularity
  (stars/views/upvotes, log-scaled), freshness decay, trusted-domain bonus, spam penalty
- URL + fuzzy-title deduplication across sources
- Category grouping: Official Docs, Videos, GitHub, Articles, Blogs, Reference,
  Community, Tools, Libraries
- TTL cache (in-memory by default, Redis when `REDIS_URL` is set) — identical searches
  are served instantly without re-hitting upstream APIs
- Sliding-window rate limiting on `/api/search`
- Live pipeline-progress UI, collapsible result categories, quality-score rings,
  copy/bookmark/open actions on every result card

## Architecture

See [Architecture.md](./Architecture.md), [Providers.md](./Providers.md),
[Ranking.md](./Ranking.md), [Caching.md](./Caching.md), and
[SearchPipeline.md](./SearchPipeline.md) for deep dives. Short version:

```
src/
  app/                Next.js routes (pages + API route handlers)
  providers/           One class per search source + ProviderFactory registry
  ranking/              Scoring engine, deduplication, grouping
  cache/                Cache adapter (memory / Redis)
  services/             SearchPipelineService — orchestrates the full request
  utils/                Query expansion, Zod validation
  config/               Scoring weights, curated official-docs site list
  repositories/         Search history (in-memory, swappable for a DB)
  components/, hooks/   Frontend UI
```

Adding a new search source means writing one `BaseProvider` subclass and registering it
in `ProviderFactory` — no other file needs to change.

## Installation

```bash
git clone https://github.com/Manas-Dikshit/Knowledge_Search_Engine.git
cd knowledge-search-engine
npm install
cp .env.example .env.local   # then fill in whichever keys you want to enable
npm run dev
```

Open http://localhost:3000. With zero configuration, GitHub, Dev.to, Hashnode, Stack
Overflow, and Reddit are already live and working.

## Environment variables

| Variable | Required | Enables | Where to get it |
|---|---|---|---|
| `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_CX` | No | Google web search + Official Docs meta-provider | [Programmable Search Engine](https://programmablesearchengine.google.com/) + [Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `YOUTUBE_API_KEY` | No | YouTube video search | [Cloud Console](https://console.cloud.google.com/apis/credentials) (enable "YouTube Data API v3") |
| `GITHUB_TOKEN` | No | Raises GitHub rate limit from 60/hr → 5,000/hr | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `ENABLE_REDDIT` | No | Toggles Reddit provider (`true` by default) | — |
| `REDIS_URL` | No | Shared cache across instances (falls back to in-memory) | Your Redis instance |

Full details in [.env.example](./.env.example).

## Search flow

1. **Input validation** — Zod schema on `POST /api/search`
2. **Query expansion** — acronym expansion + intent suffixes (`tutorial`, `best practices`, `github example`, ...)
3. **Parallel search** — every configured provider is called concurrently, each with an
   8s timeout and isolated error handling (one failing provider never breaks the response)
4. **Normalization** — providers already return the shared `RawProviderResult` shape
5. **Deduplication** — exact URL match, then fuzzy title-similarity across sources
6. **Ranking** — quality score computed per result (see [Ranking.md](./Ranking.md))
7. **Grouping** — sorted results bucketed into categories, capped per category
8. **Response** — cached (default 6h TTL) and returned

## API endpoints

See [API.md](./API.md) for full request/response shapes.

- `POST /api/search` — run a search
- `GET /api/providers` — list every registered provider and whether it's configured
- `GET /api/status` — health check, cache stats, providers configured count
- `GET /api/cache` / `DELETE /api/cache` — inspect or clear the cache
- `GET /api/history` — recent search history

## Technology stack

Next.js 14 (App Router) · TypeScript (strict) · Tailwind CSS · Zod · `lru-cache` ·
`ioredis` (optional) · zero external UI/chart libraries — the score ring and pipeline
progress are hand-built SVG/CSS.

## Deployment

Works unmodified on Vercel, Docker, a bare Ubuntu VPS, or localhost. See
[Deployment.md](./Deployment.md) for step-by-step instructions for each target.

## Future improvements

- Additional keyless providers (arXiv for academic papers, Product Hunt for tools)
- Persisted search history + user accounts (swap `SearchHistoryRepository` for a real DB —
  the interface is already there)
- LLM-based query understanding to replace the rule-based query expansion
- A/B-testable ranking weight profiles per topic category (e.g. weight GitHub stars
  higher for library searches, weight freshness higher for framework-version searches)
- WebSocket-based live pipeline progress instead of the current client-side stage simulation

## Contributing

1. Fork the repo and create a feature branch
2. New search source? Add a `BaseProvider` subclass in `src/providers/` and register it
   in `ProviderFactory.ts` — see [Providers.md](./Providers.md)
3. Run `npm run typecheck && npm run build` before opening a PR
4. Describe the source's rate limits and whether it needs an API key in your PR

## License

MIT
