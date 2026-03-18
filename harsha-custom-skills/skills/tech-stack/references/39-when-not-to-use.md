# When NOT to Use: Counter-Recommendations Guide

## Executive Summary (5-line TL;DR)
- Don't use Next.js for content sites (use Astro), non-JS teams (use Django/Rails), or simple APIs (use Fastify/Hono)
- Don't use Vercel at scale: $500+/mo common; Coolify on Hetzner is 10-50x cheaper for moderate traffic
- Don't use Supabase for HIPAA without Team plan BAA, offline-first mobile, or complex multi-tenant SaaS
- Don't use Cloudflare Workers for CPU-heavy tasks (>10ms), WebSocket servers, or jobs needing >128MB RAM
- The monolith on a VPS ($4-20/mo) beats microservices for 90% of B2B SaaS under 100K users

## Purpose

This file exists to counter the natural bias toward Supabase/Vercel/Next.js/Cloudflare in this skill. Every technology has failure modes. This guide documents when the "default" recommendations are wrong and what to use instead.

The skill's bias toward modern JavaScript/TypeScript ecosystems is NOT arbitrary—it reflects real advantages for most web projects. However, defaulting to these choices in inappropriate contexts costs projects money, velocity, and maintainability. This file corrects that bias.

---

## When NOT to Use Next.js

### The Problem

Next.js is recommended by default for web apps, but it's the wrong choice for many scenarios. It adds complexity and overhead where simpler solutions exist.

### Don't Use Next.js When:

#### 1. Content-heavy sites (blogs, docs, marketing)

**Problem:**
- Next.js is overkill for static/mostly-static content
- Slow incremental builds with large content trees (100+ pages)
- Ships unnecessary JavaScript to every visitor
- Complexity in deployment and caching strategies
- Content updates require rebuilds or ISR setup

**Use instead:**
- **Astro** (content-first framework, 90% less JS shipped, 50% faster builds, zero JavaScript by default)
- **Hugo** (static site generator, instant builds, pure Go binary)
- **11ty** (JavaScript-based but simple, flexible, zero JS output)
- **Zola** (Rust-based, fast, perfect for blogs)

**Example:** A marketing site with 50+ pages, landing pages, and blog posts. Next.js will ship 200KB of JavaScript per page. Astro will ship 0KB (or 5-10KB if you add interactive components). The content loads identically; the Astro version is faster and cheaper to host.

#### 2. Server-rendered apps with heavy backend logic

**Problem:**
- Next.js API routes are edge-case toys, not production backends
- No native background job system
- No ORM/database migration tools
- Limited middleware/auth patterns
- No admin panel generation
- Single-language stack sometimes forces awkward patterns

**Use instead:**
- **Django + HTMX** (full framework, ORM, admin panel, background jobs via Celery, migrations, 10 years of patterns)
- **Rails + Hotwire** (convention-over-configuration, 20 years of CRUD patterns, built-in testing, mailers, background jobs)
- **Laravel + Livewire** (modern PHP, excellent DX, cheapest hosting, component-first approach)
- **FastAPI + React** (if you need Python async performance, separate frontend)

**Example:** An internal admin dashboard with 20 tables, complex business logic, multi-tenant auth, and background report generation. Django Admin Panel gives you CRUD UIs for free. Next.js requires building every admin page manually. Over 6 months, this is 10-20% of your project time.

#### 3. Cost-sensitive projects at scale

**Problem:**
- Vercel pricing balloons with traffic (bandwidth, serverless invocations, build time)
- Real cost trap: $20/mo Vercel Pro → $500-2000+/mo at moderate traffic
- Each build takes time/minutes (costs money on Pro/Enterprise)
- Database queries are separate costs
- Bandwidth egress charged on pay-as-you-go tiers

**Use instead:**
- **Self-host on Hetzner + Coolify** (€4-20/mo for VPS, Coolify is open-source Vercel, deploy any Docker container)
- **Cloudflare Pages + Workers** ($0-5/mo for most projects, free bandwidth)
- **Railway** ($5-50/mo base cost, predictable, includes database)
- **Fly.io** ($3/mo minimum, predictable pricing, full Docker support)

**Cost comparison for 500K pageviews/month:**
- Vercel Pro: ~$100-300/mo (builds, bandwidth, functions)
- Cloudflare Pages: ~$0/mo (within free tier limits)
- Hetzner CX22 + Coolify: ~€4-20/mo ($5-25/mo)
- Railway: ~$15-30/mo

#### 4. Simple SPAs / dashboards

**Problem:**
- Server-side rendering (SSR) complexity unnecessary for auth-gated dashboards
- Build complexity adds friction with minimal benefit
- Simpler alternatives have better hot reload/DX

**Use instead:**
- **Vite + React** (or Vue/Svelte with Vite, faster builds, faster HMR, simpler deployment)
- **SvelteKit** (if you want both SPA and SSR flexibility with better DX)
- **Remix** (better data fetching than Next.js for SPA-like apps)

**Example:** A SaaS dashboard with 10 pages, all behind auth, mostly client-side state. Vite + React builds in <1s. Next.js builds in 10-30s. No benefit from SSR (all pages are auth-gated anyway).

#### 5. Non-JavaScript teams

**Problem:**
- Forcing Python/Ruby/Go teams into JavaScript ecosystem
- Increases hiring difficulty, slows onboarding
- Ops complexity for teams without Node.js expertise
- Build tooling unfamiliar to backend teams

**Use instead:**
- **FastAPI + React** (Python async backend, separate frontend, teams work in parallel)
- **Django + HTMX** (Python, minimal JavaScript, one monolith, 95% of apps can work this way)
- **Rails + Hotwire** (Ruby, minimal JavaScript, turbocharged HTML)
- **Go + Templ + HTMX** (Go backend with HTML templates, minimal JS)
- **Phoenix + LiveView** (Elixir, real-time HTML, no separate frontend)

**Example:** A team of 3 Python engineers needs to build a web app. Force them to learn Next.js = 2 weeks lost. Use Django + HTMX = immediate productivity, familiar deployment patterns.

#### 6. Embedded widgets / microfrontends

**Problem:**
- Next.js is a full application framework, not embeddable
- Shipping Next.js as a widget creates bundle conflicts, slow load times
- Single-page-app assumptions break in embedded contexts

**Use instead:**
- **Preact** (3KB framework, embeddable, no build step necessary)
- **Svelte** (compiled components, small output, naturally embeddable)
- **Web Components** (framework-agnostic, can use with any site)
- **Htmx** (if you don't need client-side reactivity, load fragments from server)

**Example:** A third-party widget embedded in 100+ partner sites. Next.js = 200KB+ JavaScript per partner site. Preact = 10-20KB total. The Preact version loads 10x faster.

### The Monolith Argument

For most B2B SaaS products under 100K users, a Django/Rails monolith is:
- **Faster to build** (batteries included: ORM, admin, auth, migrations, background jobs, email)
- **Cheaper to run** ($4-20/mo VPS vs $50-200/mo Vercel/Railway)
- **Easier to maintain** (one language, one deployment, one debugging context)
- **Better onboarding** (frameworks have 10-20 years of documentation)
- **Less operational debt** (fewer moving pieces)

The monolith "design pattern" fell out of favor because startups over-rotated on microservices. Most monoliths scale fine to $100M+ in revenue (Shopify, GitHub, Stripe all started monolithic).

---

## When NOT to Use Vercel

### Don't Use Vercel When:

#### 1. Cost matters at scale

**Problem:**
- Vercel Hobby: Free but no commercial use (unclear enforcement)
- Vercel Pro: $20/seat/mo + bandwidth overages + serverless invocation costs
- Bandwidth: Overages after free tier (~100GB/mo on Pro)
- Build time: Slow builds on higher concurrency cost more
- At 500K pageviews/mo with 1MB avg page size: $100-300/mo in unexpected costs

**Cost breakdown example:**
```
500K pageviews = 500GB total data ~= $50-100/mo in bandwidth
100 deployments/month (2-3 per day) = $100-200/mo in function invocations
Vercel Pro: $20/mo minimum
Total: $170-320/mo for a modest project
```

**Use instead:**
- **Cloudflare Pages** ($0/mo for most projects, unlimited bandwidth, generous free tier)
- **Coolify on Hetzner** (€4/mo + PostgreSQL = €8-20/mo, deploy anything)
- **Railway** ($5/mo minimum, includes 512MB RAM + database, predictable billing)
- **Fly.io** ($3/mo minimum, full Docker containers, great for side projects)

#### 2. Long-running processes (>60 seconds)

**Problem:**
- Vercel serverless functions timeout at 60s (Pro) or 300s (Enterprise)
- No persistent background processes
- WebSockets require workarounds (Supabase realtime or third-party)
- Can't do: Video processing, large file operations, complex data processing

**Use instead:**
- **Railway** (any container, no timeout limits, built-in background job support)
- **Fly.io** (Docker containers with 30GB RAM, full process control)
- **Hetzner VPS** (€4-20/mo, unlimited processes, full control)
- **AWS Lambda** (15 minute timeout, but still serverless)

#### 3. Non-Next.js projects

**Problem:**
- Vercel is optimized for Next.js; other frameworks get second-class treatment
- Remix: Works but not first-class
- SvelteKit: Works but cold starts slower
- Astro: Works but SSR/ISR support is basic
- Django/Rails: Possible but convoluted (requires Docker)

**Use instead:**
- **Cloudflare Pages** (SvelteKit, Astro, Remix, Qwik first-class support, better DX)
- **Railway** (any Docker container, no framework bias)
- **Netlify** (better Astro/SvelteKit support than Vercel historically)

#### 4. Docker/container needs

**Problem:**
- Vercel doesn't support custom Docker images
- Can't optimize container size or runtime
- Can't use specialized languages/runtimes

**Use instead:**
- **Railway** (native Docker support, any image)
- **Fly.io** (Dockerfile support, global deployments)
- **Render** (Docker support, cheaper than Vercel at scale)
- **DigitalOcean App Platform** (Docker support, simpler than Kubernetes)

#### 5. HIPAA/FedRAMP compliance

**Problem:**
- Vercel has no BAA (Business Associate Agreement)
- Not FedRAMP authorized
- Not suitable for healthcare/government projects
- Supabase also has no BAA

**Use instead:**
- **AWS** (BAA available, FedRAMP authorized, most compliant)
- **GCP** (BAA available, good for healthcare)
- **Azure** (BAA available, FedRAMP authorized)
- **Aptible** (small startup specialized in healthcare, BAA included)

#### 6. Self-hosted/open-source philosophy

**Problem:**
- Vendor lock-in concerns (can't easily migrate away)
- Proprietary deployment mechanisms
- Not suitable for open-source projects needing deployment guidance

**Use instead:**
- **Coolify on Hetzner** (open-source Vercel alternative, you own the infrastructure)
- **Kamal** (by 37signals, open-source deployment tool, any VPS)
- **Dokku** (open-source PaaS, easier than manual deployment)

---

## When NOT to Use Supabase

### Don't Use Supabase When:

#### 1. Mobile-first with offline sync

**Problem:**
- Supabase has no built-in offline-first architecture
- Realtime is server-first; no local-first data sync
- Building offline sync on top of Supabase requires 3-6 months of engineering
- Native apps need different patterns than web

**Use instead:**
- **Firebase** (offline sync is first-class feature, mobile SDKs battle-tested)
- **Turso** (SQLite on edge, embed in mobile app, sync to cloud)
- **PowerSync + Supabase** (adds offline-first sync layer on top of Supabase)
- **Realm** (mobile database, sync to backend)

#### 2. Schema-flexible / document data

**Problem:**
- Supabase is PostgreSQL (relational, schema-enforced, rigid)
- Rapid prototyping with unknown schema = 10 migrations per day
- GraphQL support exists but isn't first-class
- Nested document queries are awkward in SQL

**Use instead:**
- **MongoDB Atlas** (document model, flexible schema, great DX for prototyping)
- **Firebase/Firestore** (deeply nested documents, real-time sync, mobile-friendly)
- **DynamoDB** (AWS serverless document DB, pay per request)
- **Supabase + MongoDB** (use Mongo for flexible data, separate Postgres for structured data)

#### 3. HIPAA compliance

**Problem:**
- Supabase does NOT offer BAA
- Cannot be used for HIPAA-covered entities or business associates
- No compliance roadmap for HIPAA published

**Use instead:**
- **AWS RDS + Cognito** (AWS has BAA, managed Postgres)
- **MongoDB Atlas** (BAA available on paid plans)
- **PlanetScale Enterprise** (MySQL, BAA available)
- **Custom Postgres** on HIPAA-compliant infrastructure

#### 4. Edge-first architecture

**Problem:**
- Supabase runs in specific regions (can't be everywhere)
- Edge compute (Cloudflare Workers, Fastly) requires separate database
- Latency to Supabase from edge can be 50-500ms depending on region

**Use instead:**
- **Turso** (SQLite replicas at edge, 10ms latency, distributed by default)
- **Cloudflare D1** (edge database, works with Workers, global distribution)
- **Neon** (serverless Postgres, better latency than Supabase, compute autoscales)
- **PlanetScale** (MySQL with global scale, edge-friendly)

#### 5. Complex queries / analytics

**Problem:**
- Supabase is transactional (OLTP), not analytical (OLAP)
- Complex aggregations slow down primary database
- No query optimization for analytical workloads
- Running analytics queries blocks transactions

**Use instead:**
- **ClickHouse** (analytics database, 1000x faster for aggregations)
- **DuckDB** (embedded analytics, SQL queries on files/Parquet)
- **BigQuery** (Google's data warehouse, scales to 100TB+)
- **Supabase + ClickHouse** (use both: Supabase for app, ClickHouse for analytics)

#### 6. Simple key-value or caching

**Problem:**
- PostgreSQL is overkill for simple key-value data
- Supabase adds latency and cost for simple lookups
- Better solutions exist for simple use cases

**Use instead:**
- **Upstash Redis** (serverless Redis, $0.50/mo, 10K commands free)
- **Cloudflare KV** (free tier: 100K writes/day, $0.50/mo overage)
- **Vercel KV** (same as Upstash but integrated)
- **SQLite + Litestream** (simple, local, perfect for single-server apps)

#### 7. Maximum simplicity (single-file projects)

**Problem:**
- Supabase requires hosted infrastructure (auth, database, storage)
- Overhead of managing Supabase credentials for side projects
- Over-engineered for simple apps

**Use instead:**
- **PocketBase** (single Go binary, SQLite, auth, file storage, admin panel, one command to run)
- **SQLite + Litestream** (replicate SQLite to S3, runs on $4/mo VPS)
- **Firebase** (if you don't want to host anything)
- **Turso** (free SQLite database, embed in app)

#### 8. Enterprise with existing PostgreSQL

**Problem:**
- Supabase adds an abstraction layer that may not be wanted
- Existing Postgres knowledge doesn't translate to Supabase patterns
- Vendor lock-in to Supabase's abstractions

**Use instead:**
- **Neon** (pure serverless Postgres, no wrapper, better DX for Postgres experts)
- **AWS RDS** (managed Postgres, 10-20 years of maturity, enterprise support)
- **CloudSQL** (Google's managed Postgres, integrates with GCP)
- **Render** (Postgres hosting, $15/mo, simpler UX than AWS)

#### 9. Team > 10 with complex auth requirements

**Problem:**
- Supabase Auth is good for small teams/solo devs
- Enterprise auth needs missing: SAML only on Pro/Enterprise, limited SCIM support
- Multi-tenant auth patterns not built-in
- Custom auth logic requires writing functions

**Use instead:**
- **Auth0** (enterprise SAML/OIDC/LDAP, SCIM, MFA, passwordless, 15 years of auth patterns)
- **Okta** (enterprise identity, IAM, provisioning)
- **Keycloak** (open-source Auth0 alternative, self-hosted)
- **Supabase + Auth0** (use Auth0 for identity, Supabase for data)

### When Supabase IS the Right Choice

Be fair: Supabase is excellent for:
- Solo devs / small teams (1-5 people) building web apps
- Need database + auth + storage + realtime in ONE platform
- Want generous free tier ($0/mo for small projects)
- PostgreSQL is the right choice (relational data)
- Rapid prototyping / MVP building
- No enterprise auth/compliance requirements

---

## When NOT to Use Cloudflare (Workers/Pages/D1)

### Don't Use Cloudflare Workers When:

#### 1. CPU-intensive tasks

**Problem:**
- Cloudflare Workers: 10ms CPU time limit on free, 50ms on paid
- Can't do: Image processing, PDF generation, complex algorithms, machine learning
- Context: 10-50ms is only ~10-50 million JavaScript operations

**Use instead:**
- **Railway** (full Node.js, 30s execution time)
- **Fly.io** (full Node.js, 30s execution time)
- **AWS Lambda** (15 minute timeout, more CPU power)
- **VPS on Hetzner** (unlimited CPU, €4-20/mo)

#### 2. Long-running processes (>30 seconds)

**Problem:**
- Cloudflare Workers: Maximum 30 second execution time (even paid)
- Can't do: Video processing, large file operations, complex ML, data processing
- No async job processing built-in

**Use instead:**
- **VPS (Hetzner)** (unlimited runtime, €4-20/mo, can run background jobs)
- **Railway** (Docker containers, no timeout)
- **Modal** (specialized for ML/heavy compute)
- **Temporal** (workflow orchestration for long processes)

#### 3. Large data processing

**Problem:**
- Cloudflare Workers: 128MB memory limit
- No filesystem access (no /tmp for temporary files)
- Can't load large files into memory

**Use instead:**
- **VPS** (4GB+ RAM, full filesystem)
- **AWS ECS/Lambda** (more memory, /tmp storage)
- **Railway** (more memory, full container control)
- **Modal** (specialized for ML/data processing)

#### 4. Persistent connections (WebSockets)

**Problem:**
- Cloudflare Workers: WebSockets require Durable Objects (not free tier)
- Durable Objects: Complex programming model, $0.15 per million requests, plus compute
- Complex to debug, different concurrency model

**Use instead:**
- **Fly.io** (native WebSocket support, much simpler)
- **Railway** (full Node.js, native WebSocket support)
- **Hetzner VPS** (full control, simple WebSocket support)
- **Firebase Realtime** (if you need managed WebSockets without complexity)

#### 5. Traditional server-side rendering

**Problem:**
- Cloudflare Workers runtime is NOT Node.js
- Limited API compatibility with Node.js npm packages
- Some packages use Node-specific APIs that don't work
- SSR libraries often need tweaking for Workers

**Use instead:**
- **Railway** (full Node.js, any npm package works)
- **Vercel** (if Next.js)
- **Fly.io** (full Node.js runtime)
- **AWS Lambda** (Node.js 20+)

#### 6. D1 (Cloudflare's database) for production

**Problem:**
- D1 is young (launched 2023), still missing features
- 10GB max per database (too small for growing projects)
- No: Triggers, stored procedures, extensions, full-text search, complex indexing
- Migration story immature
- Backup/restore features basic

**Use instead:**
- **Neon** (serverless Postgres, production-ready, 256GB per database)
- **Supabase** (PostgreSQL, mature, 300GB+ on plans)
- **PlanetScale** (MySQL, production-ready, unlimited database size)
- **Turso** (SQLite, edge-distributed, better than D1 for edge workloads)

### When Cloudflare IS the Right Choice

Cloudflare excels at:
- **Edge computing** (10-50ms worldwide latency for simple logic)
- **CDN** (static site delivery, image optimization, caching)
- **Static sites** (Cloudflare Pages is free, fast, no framework overhead)
- **Lightweight APIs** (simple data transformation, minimal CPU/memory)
- **DNS** (best DNS provider, free tier excellent)
- **Reverse proxy/WAF** (put in front of any backend, DDoS protection)
- **Rate limiting / security rules** (flexible rules, no infrastructure needed)

---

## The Self-Hosted Alternative (Often Ignored)

### Hetzner + Coolify: The €4-20/mo Alternative to Everything

**The Math:**
```
VPS:         Hetzner CX22 (2 vCPU, 4GB RAM) = €4.49/mo
PaaS:        Coolify (open-source Vercel/Railway alternative)
Database:    PostgreSQL (on same VPS or separate)
SSL:         Let's Encrypt (free, auto-renewed by Coolify)
Monitoring:  Uptime Kuma (self-hosted, free)
Backup:      Hetzner snapshots (€0.01/GB/mo)

What you get:
- Deploy any Docker container
- Automatic SSL/HTTPS
- GitHub integration (push to deploy)
- Multiple apps on one server
- PostgreSQL database
- Redis cache
- Monitoring and uptime tracking
- Backup strategies

Cost Comparison (12 months):
Vercel Pro:         $240/mo base + overages = ~$1,500-3,000/year
Railway:            $20-100/mo = $240-1,200/year
Hetzner + Coolify:  €5-20/mo = $60-240/year
Self-host on Mac:   $0 (just electricity, no scaling)
```

### Coolify vs Vercel/Railway (Trade-offs)

**Coolify Wins:**
- Cost (€4-20/mo vs $20-100/mo)
- Docker support (any image)
- No timeout limits
- Full control of infrastructure
- Data sovereignty (data stays in EU on Hetzner)
- No vendor lock-in

**Coolify Loses:**
- Requires DevOps knowledge (container management, deployment)
- Auto-scaling is manual/complex (run bigger machine)
- No built-in CDN (add Cloudflare separately)
- 1-person job to maintain if something breaks
- Database backups are your responsibility

**When Coolify Works:**
- Cost-sensitive projects ($4-50/mo budget is tight)
- Predictable traffic (don't need auto-scaling)
- Team has DevOps person
- Comfortable with Linux/Docker
- Long-term projects (setup cost amortizes over years)

**When Coolify is Wrong:**
- Team has zero DevOps experience
- Traffic is unpredictable (need auto-scaling)
- Can't afford 2 hours debugging deployment issues
- Running >5 apps becomes infrastructure headache
- Enterprise SLA requirements (no single-VPS support)

### Other Self-Hosted Options

**Kamal (by 37signals):**
- Deploy to any VPS via Docker
- Simpler than Coolify, less features
- Good for Rails teams
- Minimal configuration

**Dokku:**
- "Heroku on your server"
- Simpler than Coolify, simpler than Kamal
- Good for small projects
- Limited multi-app support

**Docker Compose:**
- No PaaS layer
- Full control, minimal abstraction
- More work, but maximum flexibility
- Best for teams comfortable with Docker

---

## Framework Alternative Matrix

| Default Recommendation | When It's Wrong | Use Instead | Why |
|---|---|---|---|
| Next.js | Content sites | Astro | 90% less JS, faster builds |
| Next.js | Backend-heavy CRUD | Django + HTMX | Batteries included, faster to build |
| Next.js | Rapid B2B SaaS | Rails + Hotwire | Convention > configuration, 20 years of patterns |
| Next.js | PHP teams | Laravel + Livewire | Stay in ecosystem, cheapest hosting |
| Next.js | Cost-sensitive | Astro + static hosting | Free tier sufficient for millions of users |
| Next.js | Large org | Django/Rails monolith | Single language, easier to scale org |
| Next.js | Embedded widget | Preact | 3KB vs 200KB JavaScript |
| Vercel | Cost matters | Coolify + Hetzner | 10-50x cheaper |
| Vercel | Long processes | Railway or Fly.io | No timeout limits |
| Vercel | Non-Next.js | Cloudflare Pages | Better support for other frameworks |
| Vercel | HIPAA needs | AWS + Cognito | BAA available |
| Supabase | Mobile offline | Firebase | Built-in offline sync |
| Supabase | HIPAA needs | AWS RDS + Cognito | BAA available |
| Supabase | Document data | MongoDB Atlas | Flexible schema, 10x faster prototyping |
| Supabase | Key-value only | Upstash Redis | Overkill to use Postgres for KV |
| Supabase | Edge-first | Turso | SQLite replicas at edge |
| Supabase | Solo dev simplicity | PocketBase | Single binary, SQLite, all-in-one |
| Cloudflare Workers | CPU-intensive | Railway or Fly.io | No CPU limits |
| Cloudflare Workers | WebSockets | Fly.io | Native support, simpler code |
| Cloudflare Workers | Long processes | VPS or Lambda | >30s execution needed |
| Cloudflare D1 | Production DB | Neon or Turso | Mature, more features, larger limits |

---

## Decision Tree: When to Ignore Defaults

```
START: Should I use the skill's default recommendations?
│
├─ Cost-sensitive? (Monthly budget < $50/mo)
│  └─ YES → Use Coolify + Hetzner (self-host)
│  └─ NO → Continue
│
├─ Content site (blog, docs, marketing)?
│  └─ YES → Use Astro + Cloudflare Pages (free)
│  └─ NO → Continue
│
├─ Backend-heavy CRUD app?
│  └─ YES → Use Django/Rails (not Next.js)
│  └─ NO → Continue
│
├─ Mobile-first with offline sync?
│  └─ YES → Use Firebase (not Supabase)
│  └─ NO → Continue
│
├─ Enterprise with HIPAA/compliance?
│  └─ YES → Use AWS + managed services (not Supabase/Vercel)
│  └─ NO → Continue
│
├─ Solo dev, maximum simplicity?
│  └─ YES → Use PocketBase (not Supabase)
│  └─ NO → Continue
│
├─ CPU-intensive or long-running jobs?
│  └─ YES → Use Railway/Fly.io (not Vercel/Workers)
│  └─ NO → Continue
│
├─ Team with Python/Ruby/Go experience?
│  └─ YES → Use Django/Rails/FastAPI (not Next.js)
│  └─ NO → Continue
│
└─ DEFAULT → Use the skill's recommendations
   (Next.js + Supabase + Vercel is genuinely great for
    most web apps where none of the above apply)
```

---

## The Honesty Section: When Defaults ARE Right

The skill's recommendations (Next.js + Supabase + Vercel) are genuinely excellent for:

1. **Small teams (1-5 people) building web apps**
   - Developer experience is top-tier
   - Rapid feedback loop
   - Deploy in seconds
   - No DevOps knowledge needed
   - Free tier covers MVP

2. **Startups building MVPs**
   - Speed > cost (spend time, not money)
   - Generous free tier
   - Scaling is future problem
   - Can migrate later if needed

3. **Projects with unpredictable traffic**
   - Auto-scaling matters
   - Pay-per-use model aligns with usage
   - No capacity planning needed

4. **Teams comfortable with JavaScript/TypeScript**
   - Full-stack JavaScript (one language)
   - Ecosystem is mature and large
   - Most tutorials/examples use this stack
   - Easy to hire for

5. **Web apps with realtime features**
   - Supabase Realtime is excellent
   - Next.js API routes work well with realtime
   - Vercel deployment is friction-free

6. **Medium-scale SaaS ($1-100K MRR)**
   - Cost is manageable ($200-500/mo)
   - DX allows rapid feature development
   - Team is probably JavaScript-experienced
   - Auto-scaling saves engineering time

**The Bias is Justified:**
These defaults work for ~70% of web app projects. The skill doesn't need to recommend them because they're cutting-edge; the skill recommends them because they're genuinely productive for most contexts. The bias only becomes a problem when applied to the remaining ~30% of projects with different constraints.

---

## When to Override the Skill

### Conservative Override Checklist

Use this to decide when to confidently recommend something else:

- [ ] I have a specific constraint (cost, compliance, language)
- [ ] I understand the alternative's trade-offs
- [ ] The alternative solves the constraint better than defaults
- [ ] I can articulate why the default is wrong here
- [ ] The team can handle the alternative (skill level, experience)

### Example: The Real Cost Override

"This client is a nonprofit with $0 budget. Skip Next.js/Vercel entirely. Build a Django monolith on Hetzner ($5/mo). Use HTMX for interactivity. Ship in 3 months instead of 6. Total cost: $150/year instead of $2,400/year."

This override is:
- ✅ Justified (cost constraint is real)
- ✅ Understood (Django patterns are solid)
- ✅ Articulate (can explain trade-offs: simpler, cheaper, slower to scale if hypothetical)
- ✅ Realistic (nonprofit likely has Python devs or can hire them)

### Example: The Bad Override

"Use Rust instead of Next.js because Rust is faster."

This override is:
- ❌ Not justified (no constraint mentioned)
- ❌ Not understood (no mention of team experience, hiring timeline)
- ❌ Not articulate (speed isn't actually the constraint)
- ❌ Not realistic (hiring Rust devs for a web app is extreme)

---

## Related References
- [Real-World Cost Traps & Billing Horror Stories](./40-cost-traps-real-world.md) — Financial consequences of wrong tech choices
- [Startup to Enterprise Architecture Evolution](./46-startup-to-enterprise-architecture.md) — When to switch stacks as you scale
- [Migration Paths: When & How to Switch Stacks](./42-migration-paths.md) — Technical process for leaving a stack
- [Vendor Lock-In Analysis Reference Guide](./51-vendor-lock-in-analysis.md) — Avoiding lock-in in technology choices
- [MASTER COST REFERENCE MATRIX](./32-master-cost-reference-matrix.md) — Cost implications of technology decisions

---

## Pricing Stability Note

<!-- PRICING_STABILITY: moderate | last_verified: 2026-03 | check_interval: 6_months -->

This guide reflects pricing and feature sets as of March 2026. Pricing changes ~2x per year for hosted services. Revisit this file every 6 months:

- Check Vercel Pro pricing (historically increased)
- Check Supabase free tier limits (generous but changing)
- Check Cloudflare Workers CPU limits (improving)
- Check Hetzner pricing (very stable, rarely changes)
- Check Railway pricing model (simplified in 2025)

If you update pricing or features, update the date above and note the changes.

---

## Summary

This guide exists because **every technology has failure modes**. The skill's defaults are genuinely great for most projects. But for the projects where they're wrong, using the defaults anyway is expensive.

The decision to override should be:
1. **Data-driven** (specific constraint, not preference)
2. **Honest** (acknowledge trade-offs)
3. **Humble** (you might be wrong; revisit quarterly)

The skill's bias toward modern full-stack JavaScript is not arbitrary. It reflects real advantages in DX, ecosystem, and community. Questioning that bias productively means understanding WHY it's biased, not ignoring it.
