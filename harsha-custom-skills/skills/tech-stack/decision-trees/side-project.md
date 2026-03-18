# Decision Tree: Side Project / MVP

## Philosophy

The goal is **$0/month** until you have paying users. Every dollar spent before product-market fit is wasted. Free tiers in 2025/2026 are generous enough to build and launch a real product.

Your stack should prioritize:
1. **Speed to market** — Ship in 2–4 weeks
2. **Zero costs** — No surprises, no infrastructure bills
3. **Minimal maintenance** — Less time ops, more time product
4. **Learning first** — Pick technologies that improve your skills
5. **Easy pivoting** — Can change direction without being locked in

---

## THE $0 STACK (Default for 90% of Side Projects)

This covers the vast majority of side projects and MVPs:

| Category | Service | Free Tier Limits | Cost | Notes |
|----------|---------|-----------------|------|-------|
| **Frontend Hosting** | Cloudflare Pages or Vercel | Unlimited bandwidth, 500 builds/mo | $0 | Best free hosting available |
| **Serverless Functions** | Cloudflare Workers | 100k requests/day (3M/mo) | $0 | Most generous compute free tier |
| **Database** | Supabase Free | 500MB Postgres, 50k MAU | $0 | Includes Auth + Storage |
| **Authentication** | Supabase Auth | 50k MAU, social login, email | $0 | Included with Supabase |
| **File Storage** | Supabase Storage | 1GB file storage | $0 | Included with Supabase |
| **Email** | Resend | 3,000 emails/month | $0 | Transactional emails only |
| **Error Tracking** | Sentry Free | 5,000 errors/month | $0 | Error tracking |
| **CI/CD** | GitHub Actions | 2,000 minutes/month | $0 | Auto-deploy on push |
| **DNS + SSL** | Cloudflare | Free DNS + SSL + CDN | $0 | Always free |
| **Domain** | — | — | ~$10/year | Only required cost |
| **Total Monthly** | | | **$0/mo** | **$10/year domain only** |

**Why this stack?**
- Single database (Supabase) solves 3 problems: Postgres + Auth + Storage
- Vercel/Cloudflare Pages: zero-config deployments on git push
- GitHub: single source of truth for code + CI/CD
- Cloudflare Workers: serverless compute if needed (Workers actually run more efficiently than Vercel Functions)

**Real example:** A simple note-taking app:
```yaml
Frontend: Next.js deployed to Vercel Free
Backend: Supabase (no separate API needed)
Database: PostgreSQL on Supabase
Auth: Supabase Auth (email signup)
Hosting Cost: $0/month
```

---

## ALTERNATIVE $0 STACKS BY USE CASE

### Use Case 1: API-Only Project (No Frontend)

For building APIs that other apps consume.

```yaml
Framework: Hono (runs on Cloudflare Workers)
Database: Turso Free (5GB, 500M reads/mo)
Auth: API keys (simple) or Better Auth ($0)
Hosting: Cloudflare Workers Free (100k req/day)
Testing: Vitest (local) + GitHub Actions (CI)
Monitoring: Sentry Free (error tracking only)
Total Cost: $0/month
Timeline: 1–2 weeks
When to use: Building a public API, webhook service, bot backend
```

**Example:** Build a JSON API for your side project users
```yaml
Language: TypeScript
API: Hono (lightweight, runs on Cloudflare Workers)
Database: Turso (SQLite-compatible)
Auth: Bearer token or API key
Deployment: Cloudflare Workers (scales globally)
Cost: $0 (all free tiers)
```

**Common API projects:**
- Proxy service (data aggregation, transformations)
- Webhook handlers (for Stripe, GitHub, Slack events)
- Public data API (weather, sports scores, etc.)

### Use Case 2: Static Site / Blog

For content-focused projects (blog, documentation, portfolio).

```yaml
Framework: Astro (content-focused, minimal JS)
CMS: Markdown files in Git (free)
CMS Alternative: Keystatic (visual editor, Git-based)
Hosting: Cloudflare Pages or GitHub Pages
Comments: Giscus (free, GitHub-based)
Analytics: Umami (self-hosted, free) or Plausible Community
Search: Pagefind (client-side, instant)
Total Cost: $0/month
Timeline: 1–3 weeks
When to use: Blog, docs, portfolio, marketing site
```

**Why Astro for blogs?**
- Zero JavaScript by default (fast)
- Markdown + Git = your CMS
- Island Architecture: only hydrate interactive parts
- Built-in RSS, sitemap, image optimization

**Example blog stack:**
```yaml
Framework: Astro
Content: Markdown files in /src/content/posts/
Editor: Visual Studio Code (free)
Comments: Giscus (GitHub discussions)
Newsletter: Resend Free ($0) or ConvertKit
Search: Pagefind
Hosting: Cloudflare Pages
Analytics: Umami (Docker, free)
```

### Use Case 3: Real-Time App (Chat, Collaboration)

For apps that need live updates across users.

```yaml
Framework: Next.js or SvelteKit
Database: Supabase Free (includes Realtime)
Auth: Supabase Auth
Real-time: Supabase Realtime (included free)
Hosting: Vercel Free
State: Zustand (simple) or TanStack Query
Total Cost: $0/month
Timeline: 2–3 weeks
When to use: Chat, collaborative editing, live notifications
```

**How Supabase Realtime works:**
- You insert data into Postgres
- Supabase watches the table for changes
- Broadcasts updates to all connected clients via WebSocket
- Zero config required

**Example: Simple chat app**
```yaml
Frontend: Next.js + shadcn/ui
Database: Supabase (messages table)
Real-time: Supabase Realtime (WebSocket)
Auth: Supabase Auth (email)
Hosting: Vercel Free
Cost: $0/month
```

### Use Case 4: AI-Powered App

For apps that use language models or AI APIs.

```yaml
Framework: Next.js
AI Provider: Groq Free tier or Gemini Flash Free
Database: Supabase Free (+ pg_vector extension)
Auth: Supabase Auth
Hosting: Vercel Free
Storage: Supabase Storage (for embeddings/files)
Monitoring: Sentry Free (error tracking)
Total Cost: $0/month* (*API credits may apply if high usage)
Timeline: 2–4 weeks
When to use: Chatbot, writing assistant, code generator
```

**Why Groq?**
- Free for personal projects
- Fast inference (>100 tokens/sec)
- Good for real-time apps (chat, streaming)

**Alternative: Use Vercel AI SDK**
```yaml
Framework: Next.js with Vercel AI SDK
Models: OpenAI (pay-as-you-go) or free alternatives (Groq, Cohere Free)
Database: Supabase Free (store conversation history)
Cost: $0 if using Groq, or ~$1–10/month if using OpenAI
```

**Example: AI writing assistant**
```yaml
Frontend: Next.js + shadcn/ui
AI: Groq API (free tier)
Database: Supabase (store drafts, prompts)
Real-time: Streaming with Vercel AI SDK
Hosting: Vercel Free
Cost: $0/month (Groq free tier)
```

### Use Case 5: Mobile App (Cross-Platform)

For shipping to iOS + Android.

```yaml
Framework: Expo (React Native)
Backend: Supabase Free
Auth: Supabase Auth
Push: Firebase Cloud Messaging (free)
Builds: EAS Build Free (30/mo)
Hosting: EAS Build (cloud compilation)
App Store: $99/year (Apple Dev) + $25 (Google Play)
Total Cost: $0/mo + $124/year (app store fees only)
Timeline: 3–4 weeks
When to use: Shipping to app stores, offline requirements
```

**Why Expo for MVP?**
- No native code needed initially
- EAS Build compiles in the cloud (no Mac required)
- Deploy to both platforms simultaneously
- OTA updates (deploy without app review)

**Example: Habit tracking app**
```yaml
Framework: Expo (React Native)
UI: Expo UI components + Tailwind
Database: Supabase (habits, logs)
Auth: Supabase Auth
Push: Firebase Cloud Messaging (free)
Offline: SQLite local cache
Sync: Background sync to Supabase
Hosting: EAS Build (free tier: 30 builds/mo)
Cost: $0/mo (+ $99/year Apple Dev)
```

### Use Case 6: Data Dashboard / Analytics

For visualizing data, building internal tools.

```yaml
Frontend: Next.js + React
Data Viz: Recharts (free, good) or Plotly (more features)
Database: Supabase Free
Auth: Supabase Auth (or Clerk free tier)
Hosting: Vercel Free
State: TanStack Query (for caching API responses)
Monitoring: PostHog Free (product analytics)
Total Cost: $0/month
Timeline: 2–3 weeks
When to use: Personal dashboard, analytics, internal tools
```

**Example: Side project revenue dashboard**
```yaml
Frontend: Next.js + Recharts
Data: Pull from Stripe API (free)
Database: Supabase (cache Stripe data daily)
Auth: NextAuth.js (free) + GitHub OAuth
Real-time: Refresh every 24 hours
Hosting: Vercel Free
Cost: $0/month
```

---

## DECISION: SOLO DEV vs SMALL TEAM STACK

### Solo Developer Path

You're building alone. Prioritize:
1. Minimal setup (get shipping fast)
2. Simple deployments (git push = deploy)
3. No DevOps (use managed services)

**Solo Stack ($0/mo):**
```yaml
Framework: Next.js (one framework for everything)
Database: Supabase (all-in-one: DB + Auth + Storage)
Hosting: Vercel Free (auto-deploy on push)
Email: Resend Free (3k/mo)
Analytics: Vercel Analytics Free (built-in)
Monitoring: Sentry Free (error tracking)
Total: $0/month
Weekly time: 1–2 hours (mostly shipping, not ops)
```

**Why this for solo:**
- Single database (Supabase) handles auth, storage, real-time
- Vercel auto-deploys on git push (zero config)
- If something breaks, Vercel's dashboard shows what's wrong
- No server maintenance, no Docker, no Kubernetes

### Small Team Path (2–3 people)

You have co-founders or small team. Priorities:
1. Clean code (easy to handoff)
2. Monorepo or clear project structure
3. Communication tools (GitHub, Slack)
4. Minimal meetings (async first)

**Small Team Stack ($0–50/mo):**
```yaml
Monorepo: Turborepo (free, open source)
Frontend: Next.js
Backend: Next.js API Routes (or separate if needed)
Database: Supabase Pro ($25/mo) or Neon Launch ($19/mo)
Auth: Clerk Free (up to 10k MAU)
Hosting: Vercel Pro ($20/mo for priority builds)
Monitoring: Sentry Free
Testing: Vitest + GitHub Actions CI
Total: $25–50/month
```

**Why Turborepo for teams:**
- Monorepo structure: all code in one repo
- Shared components, utilities, types between frontend + backend
- Clear responsibilities (frontend dev, backend dev, design)
- One git push deploys frontend + backend

**Example team structure:**
```
my-startup/
├── apps/
│   ├── web/              # Next.js frontend
│   ├── api/              # Express/Hono API (optional)
│   └── mobile/           # Expo app (optional)
├── packages/
│   ├── ui/               # Shared components
│   ├── db/               # Drizzle schemas, migrations
│   └── types/            # Shared TypeScript types
├── turbo.json            # Turborepo config
└── package.json          # Root monorepo
```

---

## THE $0 STACK: DETAILED BREAKDOWN

### Why Supabase as Your "One Database"?

Supabase is PostgreSQL + Auth + Storage + Real-time. Three problems, one service.

**What you get for free:**
- PostgreSQL: 500MB (enough for 100k rows of typical data)
- Auth: 50k MAU (monthly active users)
- Real-time: WebSocket subscriptions
- Storage: 1GB for files (images, PDFs, videos)
- API: Automatically generated REST + GraphQL APIs

**Cost scaling:**
- Free: 500MB + 50k MAU (launch here)
- Pro ($25/mo): 8GB + unlimited MAU (hit when you're serious)
- Scale ($200+/mo): 100GB+ (only with real revenue)

### Why Vercel or Cloudflare Pages?

Both are zero-cost for static/dynamic Next.js apps.

| Service | Best For | Auto-Deploy | Build Time | Edge Functions |
|---------|----------|-----------|-----------|----------------|
| **Vercel** | Next.js (especially App Router) | Git push | 1–2 min | Yes, free tier |
| **Cloudflare Pages** | Static + Workers | Git push | 30s | Yes, free tier (Workers) |
| **GitHub Pages** | Static only | Git push | Minutes | No (static only) |
| **Render** | Docker + Node | Git push | 5–10 min | $7/mo minimum |

**Recommendation:** Start with Vercel (best Next.js integration). Move to Cloudflare Pages if you want faster builds.

### Why GitHub Actions for CI?

Testing and linting before deploy.

**Free tier limits:**
- Private repos: 2,000 minutes/month
- Public repos: Unlimited
- Tip: Make your repo public (or use GitHub Free plan limit wisely)

**Example workflow (auto-run on every push):**
```yaml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run test
```

---

## WHEN TO UPGRADE FROM $0

**Don't upgrade preemptively.** Upgrade when you hit a real limit:

| Signal | What's Happening | Next Action | New Cost |
|--------|-----------------|------------|----------|
| **Supabase pauses** (7-day idle) | No active users | Maybe project isn't viable yet | Stay at $0 |
| **Hit 500MB database** | Real data accumulating | Supabase Pro ($25/mo) | +$25 |
| **Hit 3k emails/month** | Users are engaging | AWS SES ($0.10/1k emails) | +$0.50 typically |
| **Need team collaboration** | Co-founder joins | Vercel Pro ($20/mo) | +$20 |
| **First paying customer** | Revenue! | Celebrate, then upgrade database | Budget from revenue |
| **Hitting 50k MAU** | Real traction | Supabase Pro or Clerk paid | $25–50+ |
| **>1k concurrent users** | High traffic | Vertical scaling (bigger DB) or caching | $100+ |

### The $10k Revenue Milestone

When you hit $10k MRR (monthly recurring revenue):

```
Revenue: $10,000/mo
Stripe fees: -$300 (2.9% + $0.30)
Infrastructure: -$150 (Supabase Pro + Vercel Pro + monitoring)
Profit: $9,550
Infrastructure as % of revenue: 1.5% (excellent)
```

At this point:
- Upgrade Supabase to Pro ($25/mo) for reliability
- Upgrade Vercel to Pro ($20/mo) for priority builds
- Add monitoring: Sentry + BetterStack ($50/mo)
- Start tracking metrics: PostHog or Amplitude ($20/mo)
- **Total: ~$115/mo**

---

## FREE TIER GOTCHAS TO KNOW

### Supabase Free

**Auto-pause behavior:**
- If no database queries for 7 days → project pauses
- Workaround: Set up a cron job that pings the DB daily
- Or just keep using it (pause only happens if truly abandoned)

**Limits:**
- 2 free projects maximum per account
- 500MB database (about 100k rows of typical data)
- 2GB bandwidth/month (plenty for MVP)
- 50k MAU (monthly active users)

**When to upgrade:**
- Hitting 400MB+ (upgrade proactively)
- Hitting 40k+ MAU (real traction)
- Need dedicated support (Pro tier adds it)

### Vercel Free

**Commercial use:**
- Free tier technically "not for commercial use"
- In practice: nobody enforces this for small projects
- Real limit: 100GB bandwidth/month (plenty)

**Function limits:**
- 12 second timeout (for API Routes)
- 1MB response size
- Enough for most things, but streaming kills it

**When to upgrade ($20/mo):**
- Priority deploys (yours deploy faster than others)
- Better analytics (built-in)
- Team collaboration (invite teammates)
- Unlimited serverless function timeout

### Cloudflare Workers Free

**Daily reset:**
- 100k requests/day (resets at UTC midnight)
- Not monthly, daily
- If you spike above 100k, requests fail for rest of day

**CPU time:**
- 10ms CPU time per request (strict limit)
- Not wall-clock time, actual CPU
- Enough for most API calls

**Storage:**
- No Durable Objects on free tier ($5/mo to enable)
- KV storage: 100k read ops/day, 1k write ops/day

**When to upgrade:**
- Using Durable Objects (state machines, rate limiting) → $5/mo
- High read/write volume → standard pricing

### GitHub Actions Free

**Private repos:**
- 2,000 minutes/month (shared across all private repos)
- Tip: Make repo public or pay for more minutes

**Public repos:**
- Unlimited (can run CI forever)

**When to upgrade:**
- If minutes cost >$20/mo → use Render or Railway's CI

### Firebase/Firestore Free

**Read/write operations:**
- 50k reads/day, 20k writes/day
- At $0.06 per 100k reads, you'll hit bills fast if popular

**Breakeven point:**
- 100k reads/day = $60/mo
- If your side project gets this much traffic, you probably have revenue

**When to avoid Firebase:**
- Expect >10k reads/day → use Supabase instead
- Complex queries needed → Supabase Postgres is better

---

## SPEED-TO-SHIP FRAMEWORK

Prioritize shipping speed. Every extra technology adds days of setup.

### YES (Use These at MVP)

- **One database** (Supabase = DB + Auth + Storage, three problems solved)
- **One framework** (Next.js or SvelteKit, not both)
- **One styling approach** (Tailwind + shadcn/ui)
- **Stripe or LemonSqueezy** (don't build custom billing)
- **GitHub for everything** (code, CI/CD, project management, discussions)
- **Vercel or Cloudflare** (one-click deploy, no Docker/Kubernetes)
- **Supabase Auth** (built-in, works with OAuth)

### NO (Avoid These at MVP)

- ❌ **Kubernetes** — Use Vercel or Railway instead
- ❌ **Docker Compose** — Vercel handles deploys, no containers needed
- ❌ **Microservices** — One monolith scales to 100k users
- ❌ **GraphQL** — Use REST or tRPC (simpler to learn, faster to build)
- ❌ **Separate Redis** — PostgreSQL `pg_cron` handles async, `NOTIFY/LISTEN` for pub-sub
- ❌ **Elasticsearch** — Use PostgreSQL `pg_trgm` extension for full-text search
- ❌ **Custom auth** — Use Supabase Auth or Clerk
- ❌ **Multiple databases** — One Postgres handles everything
- ❌ **Message queues** — Use Postgres `LISTEN/NOTIFY` or simple cron
- ❌ **Terraform / Infrastructure as Code** — Just click "deploy" on Vercel
- ❌ **Load balancing** — Vercel handles it automatically
- ❌ **Monitoring tools** — Start with Sentry Free (error tracking only)

**Why these rules?** Each omitted tool saves 1–3 days of setup. Ship in 2 weeks, iterate.

---

## TECHNOLOGY PICKS BY VIBE

Choose based on what you want to learn or what feels natural.

### "I want the simplest possible stack"

```yaml
Framework: SvelteKit + Tailwind
Database: Supabase
Hosting: Cloudflare Pages
Why: SvelteKit is minimal boilerplate, excellent DX
Best for: Learning web dev, shipping fast
Downside: Smaller job market than React
Timeline: 2 weeks
```

**Real example:** A simple todo app with SvelteKit
```yaml
Frontend: SvelteKit (minimal, fast)
Database: Supabase (one command to set up)
Auth: Supabase Auth (free, built-in)
Styling: Tailwind + daisyUI (pre-built components)
Hosting: Cloudflare Pages (git push = deploy)
Deploy time: <2 minutes from commit
```

### "I want the most hireable/popular stack"

```yaml
Frontend: Next.js + Tailwind + shadcn/ui
Backend: Next.js API Routes
Database: Supabase
Hosting: Vercel
Why: Largest ecosystem, most tutorials, easiest to find help
Best for: Resume building, job market
Timeline: 2–3 weeks
```

**Real example:** A task management app (SaaS)
```yaml
Frontend: Next.js App Router + shadcn/ui
Database: Supabase (Postgres)
Auth: Clerk (free to 10k MAU, better UX)
Hosting: Vercel Free
Deploy: git push → live in 2 minutes
Easy to hire: Any React dev can contribute
```

### "I want maximum performance"

```yaml
Frontend: Astro (edge case: static site)
API: Hono on Cloudflare Workers
Database: Turso (SQLite on edge)
Why: Edge-first, sub-10ms responses, tiny bundle
Best for: High-traffic sites, performance obsessed
Timeline: 2–3 weeks
Caveat: More complex, fewer tutorials
```

**Real example:** A URL shortener (high traffic, low latency)
```yaml
Frontend: Astro (static HTML, minimal JS)
API: Hono on Cloudflare Workers (edge compute)
Database: Turso (SQLite, embedded in Workers)
Cache: Cloudflare Cache API (built-in CDN)
Latency: <10ms (served from edge)
Cost: $0 (Cloudflare free tier)
```

### "I'm a Python developer"

```yaml
Frontend: React or SvelteKit
Backend: FastAPI (async, modern)
Database: Supabase or PostgreSQL on Railway
Hosting: Railway ($7–20/mo) for backend
Why: Stay in Python, modern async framework
Timeline: 3–4 weeks
```

**Real example:** A data scraper + dashboard
```yaml
Backend: FastAPI + Pydantic (type-safe)
Database: PostgreSQL (Supabase or Neon)
Scheduled tasks: APScheduler (runs scrapes hourly)
Frontend: React + Vite (shipped separately)
Hosting: Railway for FastAPI ($7/mo), Vercel for React ($0)
Cost: $7/month
```

### "I want to build once, deploy everywhere (web + mobile)"

```yaml
Frontend (web): Next.js
Frontend (mobile): Expo (React Native)
Backend: Same API for both
Database: Supabase (both apps use same DB)
Shared code: TypeScript types, business logic
Why: One React codebase mindset, one database
Timeline: 4–6 weeks (more complex)
```

**Real example:** A note-taking app (web + iOS + Android)
```yaml
Web: Next.js + shadcn/ui
Mobile: Expo (React Native)
Backend: Supabase (all platforms query same DB)
Auth: Supabase Auth (shared between platforms)
Real-time: Supabase Realtime (notes sync across platforms)
Cost: $0/mo (+ $99/year Apple Dev)
```

---

## SIDE PROJECT MONETIZATION CHEAT SHEET

When you're ready to charge for your side project.

### Monetization Models

| Model | Best For | Payment Provider | Setup Time | Annual Revenue Potential |
|-------|---------|-----------------|-----------|----------------------|
| **Subscription (SaaS)** | Recurring value (tools, software) | Stripe | 2–3 days | $1k–100k+ |
| **One-time purchase** | Templates, courses, ebooks, themes | LemonSqueezy or Gumroad | 1 hour | $100–$10k |
| **Freemium** | Wide adoption → conversion | Stripe | 2–3 days | $500–$50k+ |
| **Usage-based** | APIs, compute-heavy tools, credits | Stripe Metered Billing | 3–5 days | $100–$10k |
| **Sponsorship** | Open source projects, content creators | GitHub Sponsors or Polar | 30 minutes | $100–$5k |
| **Marketplace** | Selling user-generated content | Stripe + custom platform | 1–2 weeks | $100–$100k+ |

### Subscription (Easiest for SaaS)

**Why subscriptions?**
- Predictable revenue
- High customer lifetime value
- Forces you to keep building

**Pricing tiers:**

| Tier | Price | Use Case | Profit Margin |
|------|-------|----------|-------------|
| **Hobby** | $9/mo | Casual users | 90% (minimal support) |
| **Pro** | $29/mo | Professionals | 85% (email support) |
| **Enterprise** | $99+/mo | Teams, SaaS customers | 80% (dedicated support) |

**Real example: Habit tracker SaaS**
```yaml
Hobby ($9/mo): Unlimited personal habits, basic analytics
Pro ($29/mo): Team sharing, advanced analytics, CSV export
Enterprise ($99+/mo): Custom integrations, API access, dedicated support

At 100 Pro users: $2,900/mo revenue
Costs: Supabase Pro ($25) + Vercel Pro ($20) + monitoring ($50) = $95/mo
Profit: $2,805/mo (96% margin)
```

### One-time Purchase (Fastest)

**Why one-time?**
- No recurring billing setup
- One customer = complete transaction
- Great for templates, courses

**Platforms:**
- **LemonSqueezy**: Best for digital products (tax handling included)
- **Gumroad**: Simple, no setup fees
- **Stripe (custom)**: More control, more work

**Example: Notion template pack**
```yaml
Price: $29
Work: 20 hours to create + 1 hour to list
Revenue at 100 sales: $2,900
Profit: ~$2,800 (minimal expenses)
Per-hour rate: $140/hour
```

### Freemium (User Growth → Monetization)

**Why freemium?**
- Huge user base (free tier)
- Some convert to paying (10–5% conversion typical)
- High lifetime value per converter

**Economics:**

```
Free users: 10,000/mo
Conversion rate: 1%
Paying users: 100/mo
Price: $29/mo
MRR: $2,900

Costs:
- Database (Supabase Pro): $25/mo
- Hosting: $20/mo
- Monitoring: $50/mo
- Email/support: $50/mo
Total: $145/mo

Gross profit: $2,755/mo
Margin: 95%
```

### Usage-based Billing (For APIs/Tools)

Perfect for: Image generation, API calls, data processing, storage.

**Example: Image optimization API**
```yaml
Price: $0.01 per image processed
Volume: 10,000 images/day
MRR: 10,000 × 0.01 × 30 = $3,000

Costs:
- Compute (Cloudflare Workers): $200/mo
- Storage (R2): $50/mo
- Database: $25/mo
Total: $275/mo

Profit: $2,725/mo
Margin: 91%
```

### GitHub Sponsors (For Open Source)

If you have a popular open-source project:

```yaml
Sponsors: 50 people
Avg sponsorship: $10/mo
MRR: $500/mo

Why it works: People want to support open source
Best for: Building personal brand, not primary income
```

---

## THE FASTEST PATH TO REVENUE

### Step 1: Build ($0, 2–4 weeks)

Use the $0 stack. Don't optimize. Don't add features.

```
Week 1–2: Core feature
Week 3: Polish + bug fixes
Week 4: Launch
Result: Basic, working MVP
```

**Checklist:**
- ✓ Core feature works (don't need all features)
- ✓ Can sign up + log in
- ✓ Can use the main feature
- ✓ No console errors
- ✓ Mobile-friendly

### Step 2: Validate ($0, 1–2 weeks)

Ship to real users. Learn what they want.

**Channels:**
- Twitter/X (tweet your launch)
- Product Hunt (1 day launch event)
- HackerNews (Show HN post)
- Relevant subreddits (r/web_design, r/sideproject, etc.)
- Niche forums (dev communities, industry-specific)

**Metrics:**
- Daily active users: Should grow week 1
- Session duration: >2 minutes is good
- Return rate: >10% coming back is promising

**Questions to answer:**
1. Do people use it (or just sign up and leave)?
2. What feature do they love most?
3. What's missing?
4. Would they pay for it?

### Step 3: Monetize ($0–25/mo, 1 week)

Add payments. Start with one tier.

**Setup:**
```
1. Add Stripe (test mode is free)
2. Create pricing page
3. Add "Upgrade" button
4. Implement paywall (feature gating)
5. Deploy
Time: 1–2 days with Stripe docs
```

**Pricing strategy:**
- Don't start cheap ($9/mo is respectable)
- You can lower price later
- But you can't raise price (customers leave)
- Price higher than you think ($29/mo often better than $9/mo)

**Real example: First pricing**
```yaml
Free: Read-only access
Pro: $29/mo (upload, export, advanced features)
Why $29? At 10 customers: $290/mo
At 100 customers: $2,900/mo
Even 1–2% conversion from free users covers your costs
```

### Step 4: First $100 MRR ($25–50/mo infra, 1–2 months)

When you have paying customers:

**Actions:**
- ✓ Upgrade Supabase to Pro ($25/mo) for reliability
- ✓ Add error tracking (Sentry is free)
- ✓ Monitor uptime (BetterStack free tier)
- ✓ Build towards 10 paid customers

**Infrastructure budget:**
- Supabase Pro: $25
- Monitoring: $15
- Miscellaneous: $10
- **Total: $50/mo**

**Goal:**
- Keep infra <50% of revenue
- At $100 MRR: Infra should cost <$50/mo
- If infra > revenue, something's wrong (either scale it better or pivot)

### Step 5: First $1k MRR ($50–150/mo infra, 3–6 months)

Now you can afford proper tooling.

**Upgrades:**
- Vercel Pro ($20/mo): Priority builds, team features
- Better monitoring: Sentry Team ($29/mo)
- Product analytics: PostHog ($20/mo)
- Uptime: BetterStack ($15/mo)
- Email (if needed): Resend Pro ($20/mo)

**Total infra: ~$100–150/mo**

**Revenue: $1,000/mo**
**Infrastructure as % of revenue: 10–15%** (excellent)

**At this point:**
- You have real validation (people pay)
- You have early customers (feedback loop)
- You can hire help (contractor, VA, or junior dev)
- Consider: Is this becoming a real business?

---

## SCALING TRIGGERS: When to Upgrade Each Component

### Database Scaling

**Supabase Free → Pro:**
- Hit 400MB storage (or approaching it)
- Hit 40k+ MAU
- Need automatic backups (Pro includes daily backups)

**Supabase Pro → Scale:**
- Hit 8GB storage
- Hitting Realtime concurrency limits
- Need read replicas

**Migration path:**
```
Free → Pro ($25/mo): 1-click upgrade in dashboard
Pro → Scale ($200+/mo): Contact Supabase sales for custom quote
Alternative: Move to AWS RDS PostgreSQL ($50+/mo)
```

### Hosting Scaling

**Vercel Free → Pro:**
- Need team collaboration (Pro includes team features)
- Hitting 100GB bandwidth/month (pro tip: add CDN headers)
- Need priority deploys (Pro builds are faster)

**Vercel Pro → Self-hosting:**
- >500k pageviews/month (Vercel might get expensive)
- Need custom server logic (Docker on Railway/Render)

**Cost comparison at 1M pageviews/month:**
- Vercel Pro: ~$50/mo (bandwidth isn't expensive)
- Self-hosted (Railway): $20–50/mo (similar or cheaper)

### Authentication Scaling

**Supabase Auth Free → Clerk:**
- Hit 50k MAU limit
- Want better UX (Clerk has better sign-up flow)
- Need team/org features

**Cost comparison:**
- Supabase Auth: Free (included with Supabase)
- Clerk Free: Free to 10k MAU, then $99/mo for Pro
- WorkOS: Free to 1M MAU (best for enterprise)

### Monitoring Scaling

**Sentry Free → Paid:**
- Hitting 5k errors/month (you have lots of bugs)
- Need replay functionality (see user session playback)
- Need alerting (Sentry notifies Slack, PagerDuty)

**Cost at scale:**
- Sentry Free: $0 (5k errors)
- Sentry Pro: $29/mo (50k errors)
- Sentry Team: $99/mo (unlimited errors, team features)

---

## COMMON SIDE PROJECT MISTAKES

1. **Over-engineering too early** — Build MVP first (2 weeks), optimize at 1k users
2. **Choosing wrong tech to "learn"** — Don't pick K8s to learn DevOps on your side project
3. **Monetizing too late** — Add pricing after validation (week 4–6), not before
4. **Free forever** — You work for free, your infrastructure costs money
5. **Ignoring analytics** — Add Sentry/PostHog day 1, you can't optimize what you don't measure
6. **Too many features at launch** — Ship with 1 core feature, add others after feedback
7. **No offsite backups** — Supabase includes backups, but test restore once
8. **Choosing framework you don't know** — Use what you know to ship fast
9. **Deployed to random VPS** — Use Vercel/Cloudflare/Railway (operational simplicity)
10. **Waiting for "perfect design"** — Launch with good-enough design, iterate on feedback

---

## SIDE PROJECT → REAL BUSINESS TRANSITION

When your side project hits ~$1k MRR, you might want to make it a real business.

### Decision: Continue as Side Project or Transition to Business?

| Factor | Side Project | Real Business |
|--------|-------------|-------------|
| **Hours/week** | 5–10 | 20–40 |
| **Revenue** | $0–$5k/mo | $5k+ |
| **Focus** | Hobby, learning | Primary income |
| **Team** | Solo | 1–2 people |
| **Investment** | $0–$50/mo | $1000+/mo |
| **Complexity** | Simple | Growing |

**Decision tree:**
```
Are you making $1k/mo yet?
├─ NO → Continue iterating, don't over-invest
└─ YES → Is there growth trajectory?
   ├─ Growing 10%/mo → Transition to business
   └─ Plateaued → Stay as side project or pivot
```

### Transition Checklist (If Making $1k+ MRR)

```
□ Incorporate as LLC or C-Corp ($500–2000)
□ Open business bank account ($0–25/mo)
□ Hire accountant ($100–300/mo)
□ Set aside taxes (30% of revenue)
□ Upgrade infrastructure for reliability
□ Hire help (contractor, VA)
□ Document your processes
□ Build in public (marketing)
```

### Read Next

When your side project hits $1k MRR, read `/decision-trees/saas-product.md` for the scaling path:

- $1k → $10k/mo: Operations, hiring, compliance
- $10k → $100k/mo: Product-market fit reinforcement, team building
- $100k+/mo: Serious business decisions (funding, partnerships, etc.)

---

## SIDE PROJECT DECISION TREE SUMMARY

```
START: What kind of side project?
│
├─ Simple idea (MVP for validation)
│  └─ Use $0 stack: Next.js + Supabase + Vercel
│
├─ API / Data project
│  └─ Hono + Turso + Cloudflare Workers ($0)
│
├─ Content / Blog
│  └─ Astro + Markdown + Cloudflare Pages ($0)
│
├─ Real-time app (Chat, Collab)
│  └─ Next.js + Supabase Realtime + Vercel ($0)
│
├─ AI-powered app
│  └─ Next.js + Groq/OpenAI + Supabase ($0–10/mo)
│
├─ Mobile app (cross-platform)
│  └─ Expo + Supabase + EAS Build ($0/mo + $99/yr Apple)
│
└─ Monetizing existing side project
   ├─ First upgrade: Supabase Pro ($25/mo)
   ├─ Second upgrade: Vercel Pro ($20/mo)
   ├─ Third upgrade: Monitoring ($50/mo)
   └─ At $1k/mo revenue: Consider hiring + business structure
```

**Rule:** Ship MVP in 2–4 weeks on $0/mo. Validate with real users. Add payments. Scale once you have traction.
