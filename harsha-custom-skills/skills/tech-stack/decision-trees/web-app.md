# Decision Tree: Web Application

## Entry Point

```
What kind of web application?
├── Content/Marketing site (blog, docs, landing pages)
│   → CONTENT PATH
├── Interactive web app (dashboard, tool, SPA)
│   → INTERACTIVE PATH
├── Full-stack app with users + data
│   → FULL-STACK PATH
└── E-commerce
    → ECOMMERCE PATH
```

---

## CONTENT PATH

Content-focused sites (blogs, documentation, marketing landing pages) prioritize SEO, fast load times, content updates, and minimal overhead.

### Rendering Decision Matrix

| Strategy | Best For | Pros | Cons | SEO | Build Time |
|----------|----------|------|------|-----|-----------|
| **Static (SSG)** | Content rarely changes | Fastest (static HTML), best SEO, free hosting | Need to rebuild for updates | Excellent | Minutes |
| **Incremental Static (ISR)** | Content updates daily | Balance of speed + freshness | Requires Node.js runtime | Excellent | Minutes per page |
| **Server-side (SSR)** | Dynamic content, per-user | Always fresh, real-time data | Slower first load, needs server | Good | Real-time |
| **Hybrid (Streaming)** | Large sites, many pages | Serve fast HTML early + hydrate | Complex setup | Excellent | Minutes |

### Budget: $0/mo (Static Content)

**Best for:** Blogs, documentation, marketing sites, portfolios. Content changes less than weekly.

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Astro | $0 | Purpose-built for content, minimal JS |
| Alternative Framework | Next.js (Static Export) | $0 | If you need React ecosystem |
| Styling | Tailwind CSS + shadcn/ui | $0 | Pre-built components (headless UI) |
| CMS | Markdown in Git | $0 | Simplest: write in `/posts/*.md`, commit |
| CMS Alternative | Keystatic | $0 | Git-based CMS, visual editor in browser |
| Hosting | Cloudflare Pages | $0 | Unlimited bandwidth, 500 builds/mo |
| CDN | Included with Pages | $0 | Global edge, instant cache invalidation |
| Analytics | Umami (self-hosted) | $0 | Privacy-first, no cookies needed |
| Search | Pagefind (client-side) | $0 | Instant search from static index |
| **Total** | | **$0/mo** | (+$12/year for optional domain) |

**Example Stack:**
```yaml
site: Astro + Markdown
ui: shadcn/ui Astro components + Tailwind
analytics: Umami (Docker container, <$6/mo if hosted elsewhere)
deployment: Cloudflare Pages (git-connected, auto-deploy)
dns: Cloudflare (free, includes SSL + WAF)
```

**Real example:** A documentation site with 500 pages (Astro handles this trivially), 2k visits/day, rebuilds weekly. Total cost: $0/month.

### Budget: $0–20/mo (Dynamic Content Updates)

**Best for:** Blogs that update frequently, landing pages with A/B tests, marketing sites with dynamic content pulls.

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Next.js (App Router) | $0 | ISR + SSR hybrid support |
| Styling | Tailwind + shadcn/ui | $0 | Same as above |
| CMS | Sanity (free tier) | $0 | 3 users, 3 datasets, great API |
| CMS Alternative | Payload CMS | $0 | Self-hosted or Railway (free tier) |
| CMS Alternative 2 | Keystatic + Supabase | $5 | Git + database backend |
| Hosting | Vercel | $0–20 | Free tier limited; Pro for priority builds |
| Hosting Alternative | Netlify | $0–19 | Similar to Vercel |
| Email (newsletter) | Resend | $0 | 3k emails/mo free, good sender reputation |
| Analytics | Vercel Web Analytics | $0 | Built-in, privacy-friendly |
| Search | Algolia (free tier) | $0 | 10k records, good for product search |
| **Total** | | **$5–20/mo** | Supabase/CMS if self-hosted, domain ~$12/yr |

**Example Stack (Blog + Newsletter):**
```yaml
framework: Next.js with ISR
cms: Sanity (free tier for 1–2 editors)
database: (none needed for static content)
auth: None (CMS has built-in auth)
hosting: Vercel (free tier with 100GB bandwidth)
email: Resend (free 3k/mo)
```

**Scaling:** If CMS user count grows beyond 3 (Sanity free tier), upgrade to Sanity Team Plan ($99/mo) or migrate to Payload CMS (free, self-hosted on Railway or Render ~$7/mo).

### Content Path: Complex Decision Tree

```
Is content static (rarely changes)?
├─ YES → Use Static (SSG) with Astro + Markdown + Cloudflare Pages ($0/mo)
│
└─ NO → How often does content update?
   ├─ Daily or more → Use ISR (Next.js) + Sanity ($0 free tier)
   │
   ├─ Weekly → Use SSR (Next.js) + Payload CMS ($0–7/mo if self-hosted)
   │
   └─ Multiple editors needed?
      ├─ YES → Sanity ($0–99/mo tier) or Contentful ($89/mo)
      └─ NO → Keystatic (Git-based, $0)

Do you need email newsletters?
├─ YES → Add Resend ($0–20/mo) for transactional emails
└─ NO → Skip email

Do you need audience insights beyond page views?
├─ YES → Add Umami ($0–12/mo) or Plausible ($9/mo)
└─ NO → Use Vercel Analytics (free, built-in)
```

### Content Path: Common Mistakes

1. **Choosing a heavy CMS (Contentful, Prismic) too early** — Free tiers have feature limits. Start with Sanity free or Keystatic. Migrate later if needed.
2. **Using Next.js without ISR** — Every request rebuilds the page. Use ISR (`revalidate: 3600`) to cache at edge.
3. **Forgetting CDN headers** — Set `Cache-Control: public, s-maxage=3600` on static assets.
4. **Over-optimizing for non-existent traffic** — If you have <10k monthly visitors, free tier is fine forever.

---

## INTERACTIVE PATH (Dashboard, Tool, SPA)

Interactive apps have real-time UI updates, form submissions, stateful interactions. No content-heavy focus.

### Architecture Decision Matrix

| Architecture | Team Size | Complexity | Performance | Scalability | Monthly Cost |
|-------------|-----------|-----------|-----------|-----------|-----------|
| **Single Framework (Next.js)** | 1–3 | Low–Medium | Good (edge functions) | Up to 100k users | $0–100 |
| **Separate Frontend + API** | 3–8 | Medium–High | Very good | Up to 500k users | $50–200 |
| **Microservices + Monorepo** | 8+ | High | Excellent | 500k+ users | $200+ |

### Rendering: SPA vs SSR vs SSG vs ISR for Interactive Apps

| Strategy | Complexity | TTFB | SEO | Caching | Use Case |
|----------|-----------|------|-----|---------|----------|
| **SPA (React)** | Low | Fast | Poor | Browser cache | Internal tools, dashboards, apps behind login |
| **SSR (Next.js)** | Medium | Slow (dynamic) | Good | Per-request | Public interactive content |
| **Hybrid (Next.js with ISR)** | Medium | Fast | Good | 1–3600s revalidation | Semi-dynamic interactive |
| **Edge SSR** | Medium–High | Very fast | Good | Edge cache | High-traffic interactive |

**For interactive apps, SSR is generally best.** You want fresh data on every load, but also want to cache aggressively.

### TypeScript Solo Dev / Small Team — Budget: $0

**Best for:** Internal dashboards, MVP tools, solo founder shipping fast. One person full-stack.

| Component | Choice | Cost | Why |
|-----------|--------|------|-----|
| Framework | Next.js (App Router) + React | $0 | All-in-one, doesn't require API |
| UI Library | shadcn/ui (Radix + Tailwind) | $0 | Beautiful, copy-paste components |
| Styling | Tailwind CSS | $0 | Utility-first, fast prototyping |
| Database | Supabase Free | $0 | Postgres + Auth + Real-time (3 in 1) |
| ORM | Drizzle or `sql.js` | $0 | Type-safe, lightweight |
| Auth | Supabase Auth | $0 | Built-in, 50k MAU free |
| Storage (Files) | Supabase Storage | $0 | 1GB free, built-in |
| API Routes | Next.js API Routes | $0 | No separate backend needed |
| Hosting | Vercel Free | $0 | Auto-deploy on git push |
| Real-time | Supabase Realtime | $0 | WebSocket updates (included) |
| Monitoring | Sentry Free | $0 | 5k errors/month |
| Email | Resend | $0 | 3k/month free |
| **Total** | | **$0/mo** | |

**Example Stack:** Dashboard for team task management
```yaml
Frontend: Next.js + shadcn/ui
Database: Supabase (PostgreSQL)
Auth: Supabase Auth (email + Google OAuth)
Real-time: Supabase Realtime for task updates
Hosting: Vercel
```

**Team Size: 1 developer, launch in 2–3 weeks.**

### TypeScript Small Team — Budget: $40–100/mo

**Best for:** Growing team (3–5 people), more complex features, need for reliability.

| Component | Choice | Cost | Why |
|-----------|--------|------|-----|
| Framework | Next.js + TypeScript | $0 | Still single framework |
| UI Library | shadcn/ui | $0 | Same |
| Styling | Tailwind CSS | $0 | Same |
| Database | Neon Launch ($19) or Supabase Pro ($25) | $19–25 | Automatic backups, better support |
| ORM | Drizzle (serverless-optimized) | $0 | Works great with Vercel Functions |
| Auth | Clerk (free to 10k MAU) | $0 | Better UX than Supabase, email verification |
| Storage | Cloudflare R2 | $0 | $0 egress (outbound), cheap storage |
| API Routes | Next.js API Routes | $0 | Still fine for this scale |
| Hosting | Vercel Pro ($20/mo) | $20 | Priority deploys, better performance |
| Real-time | Supabase Realtime or Pusher ($5+) | $0–5 | Supabase free, Pusher if need more capacity |
| Monitoring | Sentry (Free tier) + LogRocket ($99) | $0–99 | Sentry free for errors, LogRocket for sessions |
| Email | Resend ($0 free) or AWS SES ($0.10/1k) | $0–5 | Resend free, then AWS |
| Analytics | Vercel Analytics | $0 | Free with Pro |
| **Total** | | **$39–60/mo** | |

**Real Example:** SaaS tool for freelancers (time tracking, invoicing, payments)
```yaml
Frontend: Next.js 15 + App Router + shadcn/ui
Database: Neon (PostgreSQL) with automatic backups
Auth: Clerk (handles 2FA, SSO, email verification)
Storage: Cloudflare R2 (invoice PDFs, receipts)
Payments: Stripe (2.9% + $0.30 per transaction)
Monitoring: Sentry (error tracking) + Vercel Analytics
Hosting: Vercel Pro
```

**Team Size: 2–3 developers + 1 product person, launch in 3–4 weeks.**

### TypeScript Growing Team — Budget: $100–250/mo

**Best for:** Team of 5–10, scaling to 10k–50k users, need for better operational control.

| Component | Choice | Cost | Why |
|-----------|--------|------|-----|
| Framework | Next.js (App Router) | $0 | Still one framework, but with API separation |
| Separate API | Hono or Fastify + TypeScript | $0 | For complex business logic |
| Database | Supabase Pro ($25) or Neon Scale ($69) | $25–69 | Scaling, reserved connections |
| ORM | Drizzle | $0 | Lightweight, serverless-first |
| Auth | Clerk Pro ($25/mo) or WorkOS (free) | $0–25 | WorkOS free to 1M MAU, better auth flows |
| File Storage | Cloudflare R2 | $5 | Pay for actual usage, cheap |
| Hosting | Vercel Pro ($20) + Railway for API ($20) | $40 | Separate backends for scalability |
| Caching | Redis (Upstash, $0 for free tier) | $0–15 | Query caching, rate limiting |
| Email | AWS SES | $0.10/1k | Cheaper at scale |
| Monitoring | Sentry Team ($29) + BetterStack ($15) | $44 | Better error tracking + uptime |
| Search | Meilisearch (self-hosted on Railway) | $7 | Free search engine, self-hosted |
| Analytics | PostHog (free tier) | $0 | Event analytics, feature flags |
| **Total** | | **$100–200/mo** | |

**Real Example:** Collaborative project management tool (like Notion-lite)
```yaml
Frontend: Next.js 15 + shadcn/ui + Tailwind
Backend API: Fastify + TypeScript (separate Railway service)
Database: Neon Scale (PostgreSQL with more connections)
Real-time: Supabase Realtime or socket.io
Auth: Clerk Pro (handles SSO, teams)
Search: Meilisearch (self-hosted on Railway)
Storage: Cloudflare R2
Payments: Stripe + Lemon Squeezy (payment provider)
Monitoring: Sentry Team + BetterStack (uptime)
Analytics: PostHog (product analytics)
Hosting: Vercel Pro + Railway
```

**Team Size: 5–8 developers, launch in 4–6 weeks.**

### Python Backend + React Frontend — Budget: $30–80/mo

**Best for:** Python-first team, need for Python ML libraries or backend complexity.

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Frontend | React (Vite) or Next.js | $0 | Separate frontend bundle |
| Backend | FastAPI | $0 | Async Python, auto-generated docs |
| Database | Supabase Free or Neon | $0–19 | Same as above |
| ORM | SQLAlchemy or Tortoise ORM | $0 | Full-featured Python ORMs |
| Hosting (API) | Railway ($7–20/mo) or Render ($7) | $7–20 | For Python runtime |
| Hosting (Frontend) | Vercel or Cloudflare Pages | $0–20 | Free tier or Pro |
| Auth | Auth0 (free to 7.5k users) or Supabase | $0–25 | Consider external auth for Python API |
| WebSocket | Websockets library (Python) | $0 | Built-in to FastAPI |
| Task Queue | Celery + Redis (Upstash) | $0–15 | For background jobs |
| **Total** | | **$30–60/mo** | |

**Example Stack:** Data analysis dashboard with ML backend
```yaml
Frontend: React + Vite (deployed to Vercel)
Backend: FastAPI with Pydantic (deployed to Railway)
Database: PostgreSQL on Neon
ML Libraries: scikit-learn, pandas available in Python
Task Queue: Celery for long-running analysis
Hosting: Railway for Python, Vercel for frontend
```

### Interactive Path: Common Mistakes

1. **Using GraphQL for simple dashboards** — REST or tRPC is faster to build and deploy. Save GraphQL for complex data fetching.
2. **Not setting ISR revalidate times** — Every page rebuild takes 30+ seconds. Use `revalidate: 60` to cache at edge.
3. **Choosing separate API too early** — Start with Next.js API Routes. Split API only when serving 10k+ requests/min.
4. **Database connection pooling ignored** — Serverless functions need connection pooling. Use PgBouncer (Neon includes it).
5. **Not caching API responses** — Add 60s cache headers to API routes: `cache: 'force-cache'` in `next.config.js`.

### Interactive Path: Scaling Decision

```
How many daily active users?
├─ <1k users: Use single framework (Next.js API Routes) $0–50/mo
├─ 1k–10k users: Still single framework, upgrade database tier $25–100/mo
├─ 10k–100k users: Consider separate API if >1k req/sec $100–300/mo
└─ 100k+ users: Separate services, load balancing, multi-region $300–1000+/mo

Is database becoming slow (queries >100ms)?
├─ YES → Add read replicas ($25+/mo extra)
├─ Implement query caching (Redis, Upstash free tier)
└─ Profile slow queries first (pg_stat_statements)
```

---

## FULL-STACK PATH

Full-stack applications combine content, interactivity, user data, authentication, and payments.

### Architecture: When to Split Frontend + Backend

| Architecture | Team Size | When to Use | Trade-offs |
|-------------|-----------|-----------|-----------|
| **Monolithic (Next.js all-in-one)** | 1–5 | <50k users, simple auth | Simpler to deploy, all in one container |
| **Next.js + Separate API** | 5–15 | 50k–500k users, team owned API | Better scaling, separate deployments |
| **Microservices** | 15+ | 500k+ users, multiple teams | Complex, overkill for most products |

### Complexity Tiers

Full-stack apps range from simple to complex. Match your stack to your complexity:

| Tier | Example | Team | Timeline | Stack |
|------|---------|------|----------|-------|
| **Tier 1: Simple** | Landing page + form + database | 1–2 | 1–2 weeks | Next.js + Supabase |
| **Tier 2: Medium** | CRUD app with auth + dashboards | 2–4 | 2–4 weeks | Next.js + Supabase + Clerk |
| **Tier 3: Complex** | Real-time collab + payments + webhooks | 4–8 | 4–8 weeks | Next.js + FastAPI + Neon + Stripe |
| **Tier 4: Enterprise** | Multi-tenant, SSO, audit logs | 8+ | 8+ weeks | Microservices + Kubernetes |

### Solo Dev / Small Team — Budget: $0

**Best for:** MVP, first 100–1k users, solo founder or small team.

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Next.js (App Router + API Routes) | $0 | All-in-one, no separate API |
| Frontend UI | shadcn/ui + Tailwind | $0 | Production-ready components |
| Database | Supabase Free | $0 | Postgres + Auth + Storage (3-in-1) |
| Auth | Supabase Auth | $0 | 50k MAU, social login, MFA |
| File Storage | Supabase Storage | $0 | 1GB, built-in |
| ORM | Drizzle or simple SQL | $0 | Type-safe, minimal overhead |
| Real-time | Supabase Realtime | $0 | WebSocket, included |
| Hosting | Vercel Free | $0 | Auto-deploy, 100GB bandwidth |
| Email | Resend | $0 | 3k/month free, good deliverability |
| Monitoring | Sentry Free | $0 | 5k errors/month |
| Analytics | Vercel Analytics + PostHog Free | $0 | Basic metrics |
| Payments (optional) | Stripe (test mode free) | $0 | Launch with Stripe, switch later |
| Domain | — | $12/year | Only real cost |
| **Total** | | **$0/mo** | |

**Real Example: SaaS time-tracking tool**
```yaml
Frontend: Next.js + App Router + shadcn/ui
Database: Supabase (PostgreSQL)
Auth: Supabase Auth (email, Google, GitHub)
Storage: Supabase Storage (profile pictures)
Real-time: Supabase Realtime (timer updates across tabs)
API: Next.js API Routes (no separate backend)
Hosting: Vercel Free
Payments: Stripe (payments table in Supabase)
Email: Resend (invoice emails)
Monitoring: Sentry Free (error tracking)
```

**Launch:** 2–3 weeks for one developer.

### Small Team — Budget: $25–60/mo

**Best for:** Growing team (2–4 people), 1k–10k users, paying customers.

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Next.js + SvelteKit | $0 | Both zero-cost |
| Frontend UI | shadcn/ui | $0 | Same |
| Styling | Tailwind | $0 | Same |
| Database | Neon Launch ($19) or Supabase Pro ($25) | $19–25 | Automatic backups, more reliable |
| Auth | Clerk (free to 10k MAU) | $0 | Better DX than Supabase Auth, 2FA, SSO |
| File Storage | Cloudflare R2 | $0 | Zero egress costs |
| ORM | Drizzle | $0 | Type-safe, serverless-friendly |
| Real-time | Supabase Realtime | $0 | If using Supabase, free |
| Hosting Frontend | Vercel Pro ($20) | $20 | Priority builds, faster deploys |
| Hosting API | API Routes on Vercel | $0 | Included with Pro |
| Email | Resend | $0 | 3k/mo free, then $20/mo |
| Monitoring | Sentry Free | $0 | Error tracking |
| Analytics | PostHog ($20/mo) or free tier | $0–20 | Product analytics, feature flags |
| Payments | Stripe | $0 | Pay per transaction (2.9% + $0.30) |
| **Total** | | **$39–65/mo** | |

**Real Example: Freelance marketplace platform**
```yaml
Frontend: Next.js + shadcn/ui
Database: Neon (PostgreSQL)
Auth: Clerk Pro (handles SSO, 2FA, team management)
File Storage: Cloudflare R2
Payment Processing: Stripe (2.9% + $0.30 per transaction)
Real-time: Supabase Realtime (notifications, messaging)
Email: Resend (transactional emails)
Hosting: Vercel Pro
Analytics: PostHog Free tier
Monitoring: Sentry Free
```

**Team Size: 2–3 full-stack developers, launch in 3–4 weeks.**

### Medium Team — Budget: $100–300/mo

**Best for:** 5–10 developers, 10k–100k users, complex features (payments, webhooks, real-time, search).

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Next.js (App Router) | $0 | Still monolithic frontend |
| API Layer | Hono or Fastify on Railway | $20 | Separate backend for complex logic |
| Frontend UI | shadcn/ui | $0 | Same |
| Database | Neon Scale ($69) or Supabase Pro ($25) | $25–69 | Reserved connections for API |
| ORM | Drizzle or TypeORM | $0 | Handle connections wisely |
| Auth | Clerk Pro ($25) or WorkOS (free) | $0–25 | Clerk for simplicity, WorkOS for cost |
| Caching | Redis (Upstash) | $0–20 | Query caching, rate limiting |
| File Storage | Cloudflare R2 | $5–20 | Pay for usage |
| Real-time | Supabase Realtime or Socket.io | $0–50 | Supabase free, Socket.io self-hosted |
| Hosting Frontend | Vercel Pro ($20) | $20 | Standard production tier |
| Hosting API | Railway ($20–50) | $20–50 | Separate service tier |
| Email | AWS SES | $0.10/1k | Cheap at scale |
| Monitoring | Sentry Team ($29) + BetterStack ($20) | $49 | Proper error + uptime tracking |
| Search | Meilisearch (Railway) | $7 | Self-hosted, free engine |
| Analytics | PostHog ($20) | $20 | Product analytics, feature flags |
| Payments | Stripe + RevenueCat ($99/mo optional) | $0–99 | RevenueCat for mobile subscriptions |
| **Total** | | **$140–310/mo** | |

**Real Example: Collaborative design tool (Figma-like)**
```yaml
Frontend: Next.js 15 + shadcn/ui + Canvas library (Fabric.js)
Backend API: Fastify + TypeScript (Rails for business logic)
Database: Neon Scale (PostgreSQL, 100+ connections)
Real-time: Socket.io with Redis adapter (Upstash)
Auth: Clerk Pro (SSO, team management)
File Storage: Cloudflare R2 (design files, exports)
Search: Meilisearch (project search)
Caching: Redis (Upstash) for frequently accessed designs
Email: AWS SES (share notifications)
Hosting: Vercel Pro + Railway (API)
Monitoring: Sentry Team + BetterStack
Analytics: PostHog (user behavior, feature usage)
Payments: Stripe (team subscription plans)
```

**Team Size: 5–8 developers + product/design, launch in 5–8 weeks.**

### Enterprise / Large Scale — Budget: $300–1000+/mo

**Best for:** 10k+ developers, complex compliance, multi-region, high availability.

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Next.js + monorepo (Turbo) | $0 | Shared components, libraries |
| Multiple APIs | Microservices (Hono/Fastify) | $100+ | Separate services by domain |
| Database | Managed PostgreSQL (AWS RDS, Timescale) | $200+ | Multi-region, read replicas, backups |
| Caching | Redis cluster (Upstash Pro or AWS ElastiCache) | $50+ | High availability |
| Auth | Keycloak (self-hosted) or Auth0 Enterprise | $500+ | SAML, OIDC, fine-grained control |
| Hosting | Kubernetes (EKS/GKE) or Lambda at scale | $500+ | Multi-region, auto-scaling |
| Monitoring | Datadog or New Relic | $200+ | Comprehensive observability |
| CDN | Cloudflare Enterprise or AWS CloudFront | $100+ | Global, DDoS protection |
| **Total** | | **$1000+/mo** | Includes team licenses, support |

**Not recommended for most products.** This tier is only for companies with 100k+ users, serious compliance needs, or dedicated infrastructure team.

### Full-Stack Scaling Checklist

```
Hitting 1k users:
✓ Enable Supabase backups
✓ Set up error tracking (Sentry)
✓ Monitor database query times
✓ Enable CDN caching headers
Cost: $0 → $25–50/mo

Hitting 10k users:
✓ Upgrade to Neon Pro or Supabase Pro
✓ Add Redis for caching hot queries
✓ Separate API if requests >1k/sec
✓ Set up uptime monitoring (BetterStack)
Cost: $50 → $150–200/mo

Hitting 100k users:
✓ Read replicas for database
✓ Separate services by domain (microservices)
✓ Multi-region deployment
✓ Dedicated support team
Cost: $150 → $500+/mo
```

---

## ECOMMERCE PATH

E-commerce has unique needs: inventory, payments, shopping cart, order management, shipping integration.

### When Shopify Fits vs When to Build Custom

| Factor | Use Shopify | Build Custom |
|--------|-----------|------------|
| **Product Count** | <5k products | 5k+ products |
| **Custom Workflows** | Standard dropshipping | Complex order processing |
| **Margins** | 20%+ (can afford 2% fee) | Thin margins (<10%) |
| **Team Size** | Solo or 1–2 people | 2+ developers |
| **Time to Launch** | 1–2 weeks | 3–4 weeks |
| **Cost at 1k/mo revenue** | $30–300 | $50–150 |
| **Cost at 100k/mo revenue** | $1000–3000 | $200–500 |

**Rule of thumb:** If margins > 15%, Shopify wins. If < 10%, build custom to save on fees.

### Lightweight E-commerce (<$10k/mo revenue, <1k products)

**Platform:** Shopify, WooCommerce, or custom Next.js

**Shopify Stack ($0–300/mo):**
```yaml
Platform: Shopify Lite ($9/mo) or Basic ($39/mo)
Theme: Debut (free) or custom Hydrogen app
Domain: Custom domain ($9–14/year)
Payments: Shopify Payments (2.9% + $0.30)
Shipping: Built-in calculators
Analytics: Shopify Analytics (built-in)
Email: Klaviyo (free to 500 contacts)
Total: $9–50/mo + payment processing fees
```

**Custom Next.js Stack ($25–100/mo):**
```yaml
Frontend: Next.js + shadcn/ui
CMS/Admin: Payload CMS (product management)
Database: Supabase Pro ($25) or Neon ($19)
Shopping Cart: Saleor (open-source) or custom implementation
Payments: Stripe (2.9% + $0.30)
Hosting: Vercel ($0–20)
Email: Resend ($0–20)
Search: Meilisearch (free, self-hosted on Railway $7)
Total: $25–100/mo + payment fees
```

**Recommendation:** Use Shopify for <$50k/mo revenue. Build custom if you need:
- Complex product variants
- Custom order workflows
- Subscription products (digital downloads, recurring)
- Multi-vendor marketplace

### Serious E-commerce ($10k–500k/mo revenue, 1k–50k products)

**For Shopify:** Plus plan ($300/mo) or Advanced ($2k/mo)
- Shopify Plus (enterprise, $2k+/mo)
- Can integrate Medusa.js for custom logic
- Use apps for advanced features (Yotpo for reviews, Gorgias for support)

**For Custom Build ($100–500/mo):**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Frontend | Next.js + shadcn/ui | $0 | Built for commerce |
| Product Admin | Payload CMS or Medusa | $0 | Product management UI |
| Backend API | Medusa.js (open-source) | $0 | E-commerce logic included |
| Database | PostgreSQL (Neon Scale $69 or RDS) | $69–300 | High-concurrency handling |
| ORM | Drizzle or Prisma | $0 | Type-safe queries |
| Payments | Stripe | $0 | 2.9% + $0.30 per transaction |
| Subscriptions | Stripe Billing | $0 | Recurring revenue |
| Shipping | EasyPost (integration) | $5 | Carrier selection + rates |
| Inventory | Custom (PostgreSQL triggers) | $0 | Stock management |
| Search | Meilisearch or Algolia | $0–100 | Fast product search |
| File CDN | Cloudflare R2 | $20 | Product images, fast delivery |
| Hosting Frontend | Vercel Pro ($20) | $20 | Quick updates |
| Hosting API | Railway ($50) | $50 | For Medusa backend |
| Email | AWS SES | $0–10 | Transactional (orders, shipping) |
| Analytics | PostHog + Shopify Analytics | $0–20 | Sales trends, funnel analysis |
| **Total** | | **$100–500/mo** | |

**Real Example: Niche Fashion Boutique**
```yaml
Product Catalog: Payload CMS (product variants, images, inventory)
Frontend Store: Next.js + Tailwind
Shopping Cart: Custom React component + Zustand state
Checkout: Stripe + custom form
Order Management: Stripe Dashboard + Medusa admin
Inventory: PostgreSQL triggers (auto-decrement stock)
Shipping: EasyPost integration (UPS, FedEx, USPS)
Email: AWS SES (order confirmation, shipping notification)
Analytics: PostHog (product views, conversion funnel)
Customer Data: Segment or custom analytics
```

### Enterprise E-commerce (500k+/mo revenue, 50k+ products)

For this scale, consider:
1. **SAP Commerce** or **BigCommerce Enterprise** — Professional support, enterprise features
2. **Custom build on AWS/GCP** — Full control, scaling built-in
3. **Composable commerce** — Medusa + custom services + headless CMS

These require dedicated infrastructure teams and budgets $1000+/mo.

### E-commerce Decision Tree

```
How many products?
├─ <100: Shopify Lite ($9/mo), no custom build needed
├─ 100–1k: Shopify Basic ($39/mo) or custom Next.js ($50–100/mo)
├─ 1k–10k: Shopify Plus ($2k/mo) or custom with Medusa ($150–300/mo)
└─ 10k+: Custom build with scaling ($500+/mo) or enterprise platform

What's your monthly revenue?
├─ <$1k: Shopify (Shopify takes 2% effective fee, plus Stripe 2.9%)
├─ $1k–10k: Break-even around $10k/mo (2% Shopify fee = $200)
├─ $10k–100k: Custom build might save 1–2% on fees ($100–2000/mo)
└─ 100k+: Custom build essential, fees drop to <0.5%

Do you have unique business logic (subscriptions, bundles, etc.)?
├─ NO: Use Shopify, way faster to launch
└─ YES: Build custom with Medusa or headless Shopify
```

### E-commerce: Cost Estimation at Each Branch

**Example 1: $1000/mo revenue**
- Shopify Basic: $39/mo
- Stripe fees: 2.9% + $0.30 = $30/mo (avg $45 orders)
- Email (Klaviyo): Free tier
- Total cost: $69/mo (6.9% of revenue)

**Example 2: $10,000/mo revenue**
- Shopify Plus: $2000/mo
- Stripe fees: 2.9% + $0.30 = $300/mo
- Apps (Yotpo, Gorgias): $200/mo
- Total cost: $2500/mo (25% of revenue) — **BAD**

- Custom build: $150/mo infra
- Stripe fees: 2.9% + $0.30 = $300/mo
- Total cost: $450/mo (4.5% of revenue) — **GOOD**

**Lesson:** At $10k/mo, custom build saves $2000/mo. Worth the initial investment.

---

## REAL-TIME FEATURES

Real-time is a critical architectural decision that affects your whole stack.

### Real-time Decision Matrix

| Feature | Simplicity | Cost | Latency | Tech |
|---------|-----------|------|---------|------|
| **Notifications** | Easy | Free | 1–2s | SSE or Supabase Realtime |
| **Live updates** (read) | Medium | Free | <500ms | WebSocket or Socket.io |
| **Collaborative editing** | Hard | $20–100/mo | <100ms | Liveblocks, Figma, Yjs |
| **Reactive data** | Medium | Free | <1s | Convex or Supabase Realtime |

### By Use Case

**Simple Notifications (chat, alerts):**
```yaml
Use: Server-Sent Events (SSE) or Supabase Realtime
Cost: Free (included)
Latency: 1–2 seconds
Best for: Non-critical updates (comments, likes, notifications)
```

**Live Dashboards (stock prices, charts):**
```yaml
Use: WebSocket (Socket.io) or Supabase Realtime
Cost: $0–50/mo (depends on volume)
Latency: <500ms
Best for: Real-time data feeds, live scores, dashboards
```

**Collaborative Editing (Google Docs, Figma):**
```yaml
Use: Liveblocks ($20–500/mo) or Yjs + WebSocket
Cost: $20–500/mo (or free if self-hosted)
Latency: <100ms required
Complexity: High (CRDTs, conflict resolution)
```

**Reactive Data Sync (offline-first apps):**
```yaml
Use: Convex ($0–200/mo) or PowerSync
Cost: $0–200/mo
Latency: Optimistic updates, sync in background
Best for: Mobile apps, offline-first
```

### Real-time Addendum

```
IF using Supabase already
  → Use Supabase Realtime (free, included, <1s latency)

IF simple notifications only
  → Use SSE (Server-Sent Events) with Next.js (free, easiest)

IF bidirectional real-time (everyone sees updates)
  → Use Socket.io (free, self-hosted) or Pusher ($5+/mo)

IF collaborative editing needed
  → Use Liveblocks ($20/mo) or Yjs + PartyKit ($0–50/mo)

IF reactive data model (data = source of truth)
  → Consider Convex ($0–200/mo) as primary database
```

---

## SCALING INFLECTION POINTS

Every app hits growth limits. Know when to upgrade each component.

### User Growth Scaling

| Stage | Users | Database | Auth | Hosting | Monitoring | Action |
|-------|-------|----------|------|---------|-----------|--------|
| **MVP** | 0–1k | Supabase Free | Supabase Auth | Vercel Free | Sentry Free | Ship |
| **Growing** | 1k–10k | Supabase Pro ($25) | Clerk ($0–25) | Vercel Pro ($20) | Sentry Free | Add backups |
| **Scaling** | 10k–100k | Neon Scale ($69) | Clerk Pro ($25) | Vercel + Railway | Sentry Team ($29) | Add caching |
| **Large** | 100k–1M | Managed Postgres (RDS $300+) | WorkOS/Auth0 ($200+) | Multi-region | DataDog ($200+) | Scale infra |
| **Enterprise** | 1M+ | PostgreSQL cluster | Keycloak (self-hosted) | Kubernetes | Dedicated observability | DevOps team |

### Cost Scaling

```
At 1k users:
  Typical cost: $10–50/mo
  Infrastructure: <$30
  Per-user cost: $0.01–0.05/user/month

At 10k users:
  Typical cost: $100–150/mo
  Infrastructure: $50–100
  Per-user cost: $0.01–0.015/user/month

At 100k users:
  Typical cost: $300–500/mo
  Infrastructure: $200–400
  Per-user cost: $0.003–0.005/user/month

At 1M users:
  Typical cost: $2000–5000/mo
  Infrastructure: $1500–4000
  Per-user cost: $0.002–0.005/user/month

Goal: Keep infrastructure cost <5% of revenue. At $10k/mo revenue,
you can afford $500/mo infra. As you grow, cost-per-user should drop.
```

### What Changes at Each Inflection

**1k → 10k users:**
- Database: Add automatic backups, move to paid tier
- Auth: Evaluate Clerk for better UX (vs Supabase)
- Monitoring: Add uptime monitoring (BetterStack)
- Caching: Add Redis for hot queries

**10k → 100k users:**
- Database: Add read replicas, connection pooling
- API: Separate from frontend if >1k req/sec
- CDN: Enable aggressive caching headers
- Infrastructure: Consider reserved instances

**100k → 1M users:**
- Multi-region deployment
- Database replication across regions
- Advanced caching (Redis cluster)
- Dedicated DevOps team
- Compliance considerations (GDPR, SOC2)

### Database Scaling Checklist

```
First signs of database load:
✓ Query times >100ms (check: SELECT * FROM pg_stat_statements)
✓ Connection pool exhausted (check: pg_stat_connections)
✓ Disk usage >80% of allocated space

Solutions in order:
1. Add indexes to slow queries (free, 10x improvement typical)
2. Enable query caching with Redis (Upstash, $10/mo)
3. Add read replicas for read-heavy workloads (Neon $20+ extra)
4. Move to larger database tier (Neon Scale $69+)
5. Shard data if >100GB (redesign required, expensive)
```

### Common Scaling Mistakes

1. **Upgrading too early** — Most MVP databases can handle 100k users with proper indexing. Don't upgrade until you hit actual limits.
2. **Not setting cache headers** — Static assets should have `Cache-Control: public, max-age=3600`. CDN caching solves 80% of scaling issues.
3. **N+1 queries ignored** — Fix these before adding caching. Use query profiling tools (DataLoader, batch queries).
4. **Separate API too early** — Single monolithic service (Next.js) scales to 500k users. Split only when you need independent scaling.
5. **Not monitoring** — You can't optimize what you don't measure. Add monitoring (Sentry, BetterStack) from day 1.

---

## DEPLOYMENT & CI/CD

All stacks above assume GitHub + Vercel or Cloudflare Pages. Here's why:

| CI/CD | Cost | Deployment Time | Auto-deploy | Secrets Mgmt |
|-------|------|-----------------|-----------|------------|
| **Vercel** | Free–$20/mo | 1–2 minutes | Yes (git push) | Built-in env vars |
| **Netlify** | Free–$19/mo | 1–3 minutes | Yes | Built-in env vars |
| **Cloudflare Pages** | Free | 30 seconds | Yes | KV storage |
| **Railway** | $5–100+/mo | 2–5 minutes | Yes | Built-in env vars |
| **GitHub Actions + AWS** | Free–100+/mo | 5–10 minutes | Conditional | Secrets Manager |

**Recommendation for all tiers:**
- Frontend: Vercel or Cloudflare Pages
- API: Railway or Render
- Use GitHub Actions for CI (tests, linting) before deploy

---

## WEB APP DECISION TREE SUMMARY

```
START: What kind of web application?
│
├─ CONTENT (Blog, Docs, Landing Pages)
│  ├─ Content rarely changes? → Astro + SSG + Cloudflare Pages ($0/mo)
│  ├─ Content updates daily? → Next.js + ISR + Sanity CMS ($0–20/mo)
│  └─ Many editors needed? → Payload CMS + Railway ($5–50/mo)
│
├─ INTERACTIVE (Dashboard, Tool, SPA)
│  ├─ Solo dev? → Next.js + Supabase Free + Vercel Free ($0/mo)
│  ├─ Small team <5? → Next.js + Neon + Clerk + Vercel Pro ($40–100/mo)
│  ├─ Team 5–10? → Next.js + FastAPI + Neon + Vercel + Railway ($100–250/mo)
│  └─ Python backend? → FastAPI + React + Railway ($30–80/mo)
│
├─ FULL-STACK (Users, Auth, Data, Payments)
│  ├─ MVP (1 dev)? → Next.js + Supabase Free + Vercel Free ($0/mo)
│  ├─ Growing (2–4 devs)? → Next.js + Neon + Clerk + Vercel Pro ($40–60/mo)
│  ├─ Scaling (5–8 devs)? → Next.js + FastAPI + Neon Scale + Railway ($100–300/mo)
│  └─ Enterprise? → Microservices + Kubernetes ($1000+/mo)
│
└─ ECOMMERCE (Products, Cart, Payments)
   ├─ <1k products? → Shopify Lite or custom Next.js ($25–100/mo)
   ├─ 1k–10k products? → Shopify Plus or Medusa.js ($100–500/mo)
   └─ 10k+ products? → Enterprise platform or custom with team ($500+/mo)
```
