# TGS Mail Sender

A Next.js app that reads a CSV/Excel sheet, finds the email column on its own, and dispatches a templated email to every recipient through Zoho Mail — built to run on Vercel without blocking, timing out, or losing recipients.

## Why it's built this way (Vercel's real constraint)

Vercel serverless functions are **stateless and time-boxed** — even on Pro, a request-driven function eventually has to return. Sending a few hundred emails one-by-one inside a single request either times out or blocks the browser tab. So sending is **not a request-response operation** here — it's a durable, resumable job:

1. **Upload** parses the sheet and stores it in Redis (Upstash) — a REST-based store that works from stateless functions with no connection pooling headaches.
2. **Create job** loads the parsed rows into a Redis-backed **queue**, and returns immediately with a `jobId`. The browser is never blocked waiting for sends.
3. **Processing** happens in small, bounded **ticks** (≈8s of work, a handful of emails each) triggered three independent ways, so no single point of failure stalls a job:
   - **Self-chaining**: after a tick, the server fires an unawaited request at itself to run the next tick immediately — this is what makes sending feel continuous instead of once-a-minute.
   - **Vercel Cron** (`/api/cron/tick`, every minute) sweeps all active jobs as a safety net — if the self-chain ever breaks (a deploy lands mid-job, a cold start fails), the job resumes within 60s on its own.
   - **Manual "process now"** — the progress page can also nudge a job forward.
4. **Progress page** polls job status every 2s and renders a live manifest — no websockets needed for this scale.

## Algorithms / system design pieces

- **Email column auto-detection** (`lib/parseSheet.ts`): first tries header-name hints (`email`, `e-mail`, …); if none match, scores every column by the fraction of sampled cells matching an email pattern and picks the best one. Works even if the column is titled "Contact" or "Notes".
- **Per-cell extraction, not validation**: per your instruction, nothing is checked for deliverability. A cell just needs to contain something email-shaped; it's extracted and sent to, no MX/DNS/syntax gatekeeping beyond "is this shaped like an email".
- **De-duplication**: the same address appearing twice in a sheet is only enqueued once.
- **Idempotent, crash-safe queue**: recipients live in a Redis list; `LPOP count` atomically removes a batch, so two overlapping triggers (cron + self-chain + manual) can never grab and send to the same recipient twice. Every recipient's state (`pending` → `sent`/`retrying`/`failed`) is tracked in a Redis hash, so a mid-job crash never loses track of who's already been mailed.
- **Rate limiting** (`lib/rateLimiter.ts`): a two-tier limiter (per-minute burst cap + per-day cap, both env-configurable) reserves capacity atomically before each batch, so the job self-throttles to whatever Zoho's plan allows instead of getting the sending account flagged.
- **Retry with exponential backoff** (`lib/jobs.ts`): transient SMTP failures (timeouts, throttling, connection resets) are re-queued via a Redis sorted set scored by "next attempt time" (30s, 1m, 2m, 4m, 8m), capped at 5 attempts before being marked permanently failed. Hard SMTP rejections (mailbox doesn't exist, etc.) skip straight to failed — no point retrying those.
- **Distributed lock per job**: a short-lived Redis lock ensures only one tick processes a given job at a time, even though ticks can be triggered concurrently from three different places.
- **Template rendering**: `{{column}}` placeholders are filled from that recipient's row; an unknown placeholder resolves to blank instead of throwing, so one malformed row can't abort a batch.
- **Pause / Resume / Cancel**: pausing simply stops new ticks from picking up work (in-flight sends still finish cleanly); cancel drains the queue and retry set.

## Edge cases handled

| Situation | Behavior |
|---|---|
| Sheet is `.csv`, `.tsv`, `.xlsx`, `.xls`, `.xlsm`, `.ods` | All parsed (CSV via PapaParse, spreadsheet formats via SheetJS) |
| No column looks like an email | Upload is rejected with a clear message before any job is created |
| Auto-detected column is wrong | User can override it in the upload preview before sending |
| Blank cell in the email column | Row is skipped, not treated as an error |
| Duplicate address in the sheet | Sent once |
| Zoho throttles or rate-limits mid-job | Classified as transient, retried with backoff, job keeps moving |
| Zoho hard-rejects a specific address | Classified as permanent, marked failed, doesn't block the rest |
| Function hits its time budget mid-batch | Tick stops cleanly, releases the lock and any unused rate-limit tokens, next tick continues exactly where it left off |
| Two triggers fire at once (cron + self-chain) | Redis lock means the second one backs off instead of double-sending |
| Browser tab closed mid-job | Sending continues — cron sweep drives it forward independent of any open tab |
| Deploy/redeploy happens mid-job | New instance picks the job back up from Redis state; nothing in-memory is relied on |
| Upload not turned into a job within 30 min | Upload expires; user is asked to re-upload (avoids unbounded Redis growth) |

## Setup

1. `cp .env.example .env.local` and fill in:
   - `AUTH_USERNAME` / `AUTH_PASSWORD` — your login for the dashboard
   - `SESSION_SECRET` — any long random string
   - `ZOHO_MAIL_USER` / `ZOHO_MAIL_APP_PASSWORD` — generate the app password in Zoho Mail → Settings → Security → App Passwords (not your real password)
   - `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` — free Redis at [console.upstash.com](https://console.upstash.com)
   - `INTERNAL_TRIGGER_SECRET` — any random string, used so only this app can trigger its own processing route
2. `npm install`
3. `npm run dev` → open `http://localhost:3000`

## Deploying to Vercel

1. Push this to a GitHub repo, import it in Vercel.
2. Add all the env vars above in Project Settings → Environment Variables. Also add `CRON_SECRET` (any random string) — Vercel automatically sends it as a bearer token on cron requests once it's set.
3. `vercel.json` already defines the cron schedule (every minute) and function time budgets — no extra setup needed.
4. Deploy. First login uses `AUTH_USERNAME` / `AUTH_PASSWORD`.

### A note on Zoho sending limits

Zoho enforces its own daily/hourly sending caps depending on your plan. `EMAILS_PER_MINUTE` and `EMAILS_PER_DAY` in `.env` are this app's *self-imposed* pace — set them at or under whatever Zoho's actual limit is for your account so the sending domain's reputation stays healthy.
