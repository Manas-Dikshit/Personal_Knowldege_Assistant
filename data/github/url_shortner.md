# 🔗 URL Shortener API

A production-style URL shortening service with authentication, click analytics, QR codes, link expiration, Redis caching, and full container/cloud deployment. Built to demonstrate end-to-end backend engineering — from schema design to observability.
---

## ✨ Features

| Domain | Capability |
|---|---|
| **Core** | Shorten URLs with random or custom aliases; collision-safe alias suggestions |
| **Auth** | JWT (HTTP-only cookie / Bearer), bcrypt hashing, email password-reset (single-use tokens, session invalidation), rate-limited auth routes, user-owned links |
| **Analytics** | Per-redirect click tracking: total clicks, unique visitors, daily/weekly counts, last accessed, top URLs, plus breakdowns by browser, OS, device, country (geoip), and referrer |
| **QR codes** | On-demand QR generation — JSON data URL, raw PNG, or SVG; customizable size, colors, margin; optional avatar center logo (PNG); Redis-cached per style |
| **Link management** | Edit a link's destination URL after creation (`PATCH /urls/:id`); update/clear expiration; delete |
| **Expiration** | Expire links by date or after N days; expired links return `410 Gone` |
| **Performance** | Redis read-through cache for redirects with expiry-aware TTL |
| **Security** | Rate limiting, fail-fast env validation, ownership checks |
| **Frontend/UI**| Responsive React SPA, Tailwind CSS v4, Recharts for data visualization, dark mode theme, seamless animated global gradients, refined layout |
| **Ops** | `/health` readiness probe (DB + Redis), structured logging, request logging, graceful shutdown |
| **Docs & Tests** | Swagger/OpenAPI, Jest + Supertest test suites |

---

## 🧱 Tech Stack

- **Frontend:** React, Vite, Tailwind CSS v4, React Router
- **Runtime:** Node.js 20, Express 5
- **Database:** PostgreSQL + Prisma ORM 7 (with `@prisma/adapter-pg`)
- **Cache:** Redis (ioredis)
- **Auth:** JWT (HTTP-only cookie or Bearer), bcrypt
- **Email:** Nodemailer (Gmail SMTP) for password-reset links
- **Analytics:** ua-parser-js (browser/OS/device), geoip-lite (country)
- **QR / images:** qrcode + sharp (avatar logo compositing)
- **Logging:** Winston (structured) + Morgan (HTTP access)
- **Docs:** swagger-jsdoc + swagger-ui-express
- **Testing:** Jest, Supertest
- **Infra:** Docker, Docker Compose, Render Blueprint

---

## 🏛️ Architecture

```mermaid
flowchart LR
    Client -->|HTTP| API[Express API]
    API -->|rate limit / auth / validate| MW[Middleware]
    MW --> C[Controllers]
    C --> S[Services]
    S -->|read-through cache| R[(Redis)]
    S -->|Prisma ORM| DB[(PostgreSQL)]
    API -->|/health| Probe[(DB + Redis checks)]
```

**Layered request flow** — each layer has one job, which keeps logic testable and swappable:

```
Route ──> Middleware ──> Controller ──> Service ──> Prisma / Redis
(URL map)  (auth,        (HTTP shape:   (business    (persistence
           validation,    parse req,     logic,       + cache)
           rate limit)    send res)      aggregation)
```

### Redirect path (the hot path)

```mermaid
sequenceDiagram
    participant U as User
    participant API
    participant Redis
    participant DB as PostgreSQL
    U->>API: GET /:shortCode
    API->>Redis: GET shortCode
    alt cache hit
        Redis-->>API: url JSON
    else cache miss
        API->>DB: findUnique(shortCode)
        DB-->>API: url
        API->>Redis: SET shortCode (TTL ≤ expiry)
    end
    API->>API: expired? → 410 Gone
    API-->>U: 302 redirect
    API->>DB: record click (async, non-blocking)
```

### Data model

```mermaid
erDiagram
    User ||--o{ Url : owns
    Url  ||--o{ Click : receives
    User {
        string id PK "uuid"
        string email UK
        string password
        datetime passwordChangedAt
        datetime createdAt
    }
    Url {
        int id PK
        string originalUrl
        string shortCode UK
        int clicks
        datetime createdAt
        datetime expiresAt
        string userId FK
    }
    Click {
        int id PK
        int urlId FK
        datetime clickedAt
        string ipAddress
        string userAgent
        string browser
        string os
        string device
        string country
        string referrer
    }
```

---

## 📡 API Reference

Interactive docs at **`/api-docs`**. Summary:

### Auth
| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register account (email + password, min 8 chars); sets an HTTP-only session cookie |
| `POST` | `/auth/login` | Log in (sets an HTTP-only session cookie) |
| `POST` | `/auth/forgot-password` | Request a password-reset link via email (generic response — no account enumeration) |
| `POST` | `/auth/reset-password` | Reset password using a valid, single-use reset token |
| `GET` | `/auth/me` | Get the currently authenticated user |
| `POST` | `/auth/logout` | Log out (clears the session cookie) |

Auth routes are rate-limited (10 requests / 15 min per IP). A password reset invalidates all existing sessions.

### URLs
| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/shorten` | optional | Create short URL. Body: `{ url, customAlias?, expiresIn?, expiresAt? }` |
| `GET` | `/user` | required | List the caller's URLs |
| `GET` | `/stats/:shortCode` | — | Basic stats for a code |
| `PATCH` | `/urls/:id` | required | Edit the destination. Body: `{ originalUrl }` |
| `DELETE` | `/urls/:id` | required | Delete an owned URL (cascades its click history) |
| `GET` | `/:shortCode` | — | Redirect (`302`), or `410 Gone` if expired |

### Analytics
| Method | Path | Auth | Returns |
|---|---|---|---|
| `GET` | `/urls/:id/analytics` | required | `totalClicks, uniqueVisitors, lastAccessed, dailyClicks, weeklyClicks, clickHistory` + breakdowns `byBrowser, byOs, byDevice, byCountry, byReferrer` |
| `GET` | `/analytics/top-urls` | required | Top 10 most-clicked URLs |

### QR & Expiration
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/urls/:id/qrcode` | required | QR as base64 JSON (default), raw PNG (`?format=png`) or SVG (`?format=svg`). Styling: `size, color, bg, margin`; `logo=true` embeds the user's avatar (PNG only) |
| `PATCH` | `/urls/:id/expiration` | required | Set/clear expiry. Body: `{ expiresIn }` or `{ expiresAt }` (`null` clears) |

### Ops
| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Readiness probe — `200 UP` / `503 DEGRADED` with per-dependency status |

**Examples**
```bash
# Shorten with a 7-day expiry
curl -X POST $BASE/shorten -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","expiresIn":"7d"}'

# Styled QR as a PNG file (red on white, 500px, with avatar logo)
curl "$BASE/urls/1/qrcode?format=png&size=500&color=%23ff0000&logo=true" \
  -H "Authorization: Bearer $TOKEN" -o qr.png

# QR as SVG
curl "$BASE/urls/1/qrcode?format=svg" -H "Authorization: Bearer $TOKEN" -o qr.svg

# Full analytics with device/country/referrer breakdowns
curl "$BASE/urls/1/analytics" -H "Authorization: Bearer $TOKEN"

# Edit the destination behind an existing short code
curl -X PATCH $BASE/urls/1 -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"originalUrl":"https://new-example.com/page"}'

# Change expiration to an absolute date
curl -X PATCH $BASE/urls/1/expiration -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"expiresAt":"2026-12-31T23:59:59Z"}'
```

---

## 🚀 Local Setup

**Prerequisites:** Node.js 20+, PostgreSQL, Redis.

```bash
git clone <repo-url> && cd url
npm install
cp .env.example .env          # then fill in the values
npx prisma migrate dev        # create tables
npm run dev                   # nodemon on http://localhost:3000
```

Run the test suite:
```bash
npm test
```

---

## 🐳 Docker Setup

Spin up the API, PostgreSQL, and Redis together:

```bash
docker compose up --build
```

The app is served on `http://localhost:3000`. Compose injects all required env vars (see `docker-compose.yml`). Postgres and Redis data persist in named volumes.

---

## ☁️ Deployment (Render)

This repo ships a **`render.yaml` Blueprint** that provisions the web service, a Postgres database, and a Redis (Key Value) instance together.

1. Push to GitHub.
2. Render Dashboard → **New + → Blueprint** → select the repo.
3. Render reads `render.yaml`, creates all three resources, wires `DATABASE_URL` and `REDIS_URL` automatically, and generates `JWT_SECRET`.
4. After the first deploy, set **`BASE_URL`** to the service's public URL (e.g. `https://url-shortener-api.onrender.com`) so generated short links use the right host.

Key Blueprint choices:
- **Migrations run on deploy** via `npx prisma migrate deploy` (in `scripts/prestart.js`) — idempotent, non-interactive, and non-destructive. A failed migration aborts startup instead of serving a half-migrated schema.
- **Health checks** point at `/health`, which verifies both Postgres and Redis.
- **Graceful shutdown** on `SIGTERM` lets in-flight requests drain.

### Database migrations

Deploys apply pending migrations with `prisma migrate deploy` (never `db push`), so
migration files under `prisma/migrations/` are the source of truth.

**One-time baseline:** this project previously deployed with `db push`, so an
existing production database may already have the schema without the matching rows
in Prisma's `_prisma_migrations` table. On the first deploy of the migrate-based
flow, mark each already-applied migration as applied once, against the prod DB:

```bash
for m in \
  20260615114144_init \
  20260615123848_add_clicks \
  20260616120000_add_url_expiration \
  20260616130000_add_users_and_url_ownership \
  20260617000000_add_otp_and_email_verification \
  20260617150519_add_name_and_avatar \
  20260702000000_add_password_changed_at_and_click_index; do
  npx prisma migrate resolve --applied "$m"
done
```

After baselining, subsequent `migrate deploy` runs only apply genuinely new migrations.

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `JWT_SECRET` | ✅ | JWT signing secret (≥ 32 chars in production) |
| `REDIS_URL` | prod | Redis connection string (defaults to `redis://localhost:6379` in dev) |
| `BASE_URL` | recommended | Public origin used to build short URLs |
| `RESEND_API_KEY` | prod | API key for sending emails via Resend (required for real OTP delivery) |
| `EMAIL_FROM` | prod | Sender email address (e.g. `Shortly <onboarding@resend.dev>`) |
| `PORT` | — | Listen port (default `3000`) |
| `NODE_ENV` | — | `development` / `production` |
| `LOG_LEVEL` | — | Winston level override (`info`, `debug`, …) |

Startup runs **fail-fast validation** (`src/config/validateEnv.js`): missing required vars abort the boot with a clear message rather than failing later at runtime.

---

## 📂 Project Structure

```text
├── prisma/                  # Schema + migrations
├── src/
│   ├── app.js               # Express app, middleware, /health
│   ├── config/              # database, redis, logger, swagger, env validation
│   ├── controllers/         # HTTP layer (parse req / shape res)
│   ├── middlewares/         # auth, rate limit, validation, error handling
│   ├── routes/              # Route definitions + Swagger annotations
│   ├── services/            # Business logic (shortening, analytics, QR, expiry)
│   ├── utils/               # ApiError, catchAsync, constants
│   └── validators/          # URL + expiration validators
├── tests/                   # Jest + Supertest suites
├── Dockerfile
├── docker-compose.yml
├── render.yaml              # Render Blueprint
└── server.js                # Entry point (env validation, graceful shutdown)
```

---

## 🧪 Testing Strategy

- **Unit tests** (`url`, `analytics`, `qrcode`, `expiration`) mock Prisma and Redis, so they run fast in CI with no external services — ideal for validating business logic and aggregation wiring.
- **Integration tests** (`auth`, `redis`) exercise real Express routes via Supertest and a live database/cache to catch wiring and serialization issues.
- **Mocking strategy:** `jest.mock()` replaces `src/config/database` and `src/config/redis` at the module boundary, letting tests drive return values and assert call arguments without touching the network.

---

## 📈 Production & Operational Notes

- **Observability:** structured JSON logs (Winston) in production; HTTP access logs (Morgan) piped through the same pipeline; `/health` for uptime monitoring.
- **Scalability:** the redirect hot path is served from Redis; click writes are non-blocking; analytics use indexed aggregation queries. Horizontal scaling is safe because the app is stateless (all state in Postgres/Redis).
- **Resilience:** graceful shutdown, fail-fast config validation, and `410 Gone` semantics for expired links.

---

## 📝 License

ISC
