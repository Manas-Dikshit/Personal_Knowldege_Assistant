# FitCheck AI

AI-powered outfit & style analyzer. Upload or capture a photo, pick an occasion,
and get a stylist-style breakdown powered by Gemini 2.5 Flash Vision.

## What's implemented in this scaffold

- **Landing page** — hero, feature cards, how-it-works, footer (`app/page.tsx`)
- **Capture/upload flow** — `getUserMedia` camera (front/rear switching),
  drag-and-drop uploader, occasion picker (`app/analyze/page.tsx` +
  `components/camera`, `components/upload`)
- **API route** (`app/api/analyze/route.ts`) — validates the request with zod,
  rate-limits by IP via Upstash (sliding window, 10 req / 10 min), calls Gemini,
  and validates the model's JSON response against a strict schema before ever
  returning it to the client. The image is never written to disk.
- **Gemini integration** (`lib/gemini.ts`, `lib/prompt.ts`) — system prompt is
  explicitly scoped to clothing/styling only, never body or facial evaluation,
  and returns a structured rejection shape for low-quality/invalid photos
  instead of the model guessing.
- **Results dashboard** (`app/results/page.tsx`) — animated score circle,
  custom SVG radar chart, category bars, strengths/weaknesses/recommendations.
- **Security/perf baseline** — `middleware.ts` sets CSP/security headers,
  origin check on the API route, strict upload size/MIME validation,
  loading/error boundaries, offline detection.

## What's intentionally left as a next step

This is a real, extensible codebase — not a mock — but a handful of
larger subsystems from the original brief need infrastructure decisions
only you can make (which auth provider, which DB if any, PDF rendering
approach), so they're stubbed or omitted rather than faked:

- **Auth (Google/email login)** — not wired up. Guest/anonymous flow works
  end-to-end today. Add `next-auth` (or Clerk/Auth.js) and gate nothing —
  the product is designed to work fully anonymously.
- **PDF export / share** — buttons exist in the UI but aren't wired to a
  generator yet. `@react-pdf/renderer` or a headless-Chromium route
  (`/api/report/[id]`) are the two straightforward paths.
- **Image quality pre-checks** (blur/darkness detection) — currently
  delegated to Gemini itself via the rejection schema in the prompt, which
  is simpler and avoids shipping a CV model to the edge. A client-side
  brightness/blur heuristic could be added in `components/upload` to fail
  faster before the network round-trip.
- **Fonts** — Cabinet Grotesk/Satoshi and JetBrains Mono are referenced via
  CSS variables but not loaded (no network access in the environment this
  was generated in). Wire them up with `next/font/google` or licensed
  `next/font/local` files in `app/layout.tsx`.
- **Testing** — no test suite included; add Vitest + Playwright per your
  team's conventions.

## Setup

```bash
npm install
cp .env.example .env.local
# fill in GEMINI_API_KEY and UPSTASH_REDIS_REST_URL / _TOKEN
npm run dev
```

Deploy to Vercel, then set the same two env vars in the project settings.
No other configuration is required.

## Architecture notes

- Route Handlers only — no separate backend, per the brief.
- All AI calls happen server-side in `app/api/analyze/route.ts`; the
  `GEMINI_API_KEY` never reaches the client.
- Images are base64-encoded client-side, sent over HTTPS, decoded in
  memory on the server, forwarded to Gemini, and discarded — nothing
  touches disk or a database.
