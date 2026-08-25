# Manas Ranjan Dikshit — Portfolio

![Portfolio Screenshot](public/projects/portfolio-screenshot.png)

A modern, interactive developer portfolio built with Next.js 15, TypeScript, Tailwind, Prisma, shadcn/ui, and Framer Motion.

This site showcases my projects, experience, skills, and a playful UI — all driven by a single data file.

---

## Tech Stack

- Next.js 15, TypeScript 5
- Tailwind CSS 4, shadcn/ui, Lucide Icons
- Framer Motion (motion.dev)
- Prisma ORM 6, Zod, Better Auth
- TanStack Query, Zustand, Day.js, Lodash
- Umami (optional analytics)

---

## Content: edit in one place

All portfolio content lives in `src/lib/portfolio-data.ts`.

- Personal: name, title, bio, resume URL
- Social + Contact
- Education & Experience
- Projects (title, description, images, tech, links)
- Skills (name + level)
- Achievements

Sections like Hero, Projects, About, Stats, Testimonials, and Footer read from this file without changing the component structure.

---

## Run locally

Prereqs: Node 18+ and npm.

1) Install

```bash
npm install
```

2) Environment (optional but recommended for live GitHub/analytics)

Create `.env.local` at project root. For my profile:

```bash
NEXT_PUBLIC_GITHUB_USERNAME=Manas-Dikshit
# Optional: enables authenticated GitHub GraphQL for richer stats
GITHUB_TOKEN=

# Optional: Umami analytics (or leave empty to show 0 values)
NEXT_PUBLIC_UMAMI_WEBSITE_ID=
UMAMI_API_KEY=
```

The app gracefully falls back to zeroed stats if these are not set.

3) Prisma client (only needed if you use DB-backed features)

```bash
npx prisma generate
```

4) Start dev server

```bash
npm run dev
```

Visit http://localhost:3000

---

## Deploy

Deploy on Vercel (recommended):

1. Push this repo to GitHub
2. Import the repo in Vercel
3. Add the environment variables in Project Settings (optional)
4. Deploy

---

## Connect with me

| Platform   | Link |
| ---------- | ----- |
| GitHub     | https://github.com/Manas-Dikshit |
| LinkedIn   | https://www.linkedin.com/in/manas-ranjan-dikshit |
| Instagram  | https://www.instagram.com/manasss01_?igsh=aXYxZXdjN3IwMzY3 |
| Email      | mailto:manasdikshit48@gmail.com |

---

## Notes

- GitHub stats: If `GITHUB_TOKEN` is not set, the site returns a safe, empty stats payload so the UI never breaks.
- Portfolio views (Umami): Without keys, the card shows 0 visits.
- Projects section: reads from `portfolio-data.ts` and preserves the original card layout.

If you like this project, feel free to fork it and make it yours! :)

