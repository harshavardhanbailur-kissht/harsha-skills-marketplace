---
name: tech-stack-advisor
description: >
  Comprehensive tech-stack recommendation engine that outputs the optimal, lowest-cost,
  highest-performance stack based on project constraints. Covers frontend, backend, databases,
  auth, hosting, mobile, payments, email, storage, monitoring, CI/CD, and more.

  USE THIS SKILL WHEN:
  - User asks "what tech stack should I use" or "recommend a stack"
  - User is starting a new project and needs architecture guidance
  - User asks to compare frameworks, databases, hosting, or any technology
  - User says "what's the best database for...", "should I use X or Y"
  - User asks about costs, pricing, free tiers, or hosting options
  - User needs a full-stack recommendation for a SaaS, MVP, API, or mobile app
  - User mentions: stack, framework, database, hosting, deploy, architecture, infrastructure
  - User asks about specific tech categories: auth, payments, email, CDN, CMS, ORM, state management
  - Even if user only asks about ONE piece (e.g., "which database?"), use this skill — the
    answer often depends on the rest of the stack
---

# Tech Stack Advisor

A decision engine for recommending complete, production-ready technology stacks. Every
recommendation is grounded in researched benchmarks, real pricing data, and battle-tested
patterns — not hype or training-data popularity bias.

## How This Skill Works

This skill operates in two modes:

**Quick Mode** — User asks about a specific technology or comparison. Load the relevant
reference file(s), synthesize, and answer with concrete numbers.

**Full Stack Mode** — User needs a complete stack recommendation. Walk through the
constraint-gathering questions, then output a complete stack with cost estimates.

## Before You Recommend Anything

Search the web to verify:
- `"[technology] latest version 2026"` — confirm you have the current version
- `"[technology] pricing 2026"` — pricing changes frequently
- `"[technology] known issues 2026"` — catch recent problems

Reference files contain data as of February 2026. Technology moves fast — always
verify pricing and version numbers before presenting them as current.

## Constraint-Gathering Questions

When a user needs a full stack recommendation, determine these six constraints.
Ask only what isn't obvious from context — don't interrogate.

1. **Project Type** → Determines which decision tree to load
   - Web app, Mobile app, API/microservice, SaaS product, Side project/MVP, Desktop app

2. **Scale Target** → Determines infrastructure tier
   - MVP (<1k users), Growing (1k–10k), Scaling (10k–100k), Large (100k+)

3. **Monthly Budget** → The hard constraint everything else bends around
   - $0 (free tier only), <$50/mo, <$500/mo, No limit

4. **Team Size & Skills** → Determines complexity ceiling
   - Solo dev, Small (2–5), Medium (5–20), Large (20+)
   - Language preference: TypeScript, Python, Go, Rust, or flexible

5. **Deployment Preference** → Determines hosting approach
   - Serverless, Containers/PaaS, VPS/self-hosted, No preference

6. **Special Requirements** → Unlocks specific reference files
   - Real-time/WebSockets, AI/ML integration, Mobile (native/cross-platform),
     Enterprise SSO/SAML, Edge deployment, Offline-first, Multi-tenant SaaS,
     Internationalization (i18n), Feature flags/progressive delivery, Background jobs/events

7. **Compliance Requirements** → Determines architecture constraints (often overrides all else)
   - HIPAA (healthcare), SOC 2 (B2B enterprise), PCI-DSS (payments),
     GDPR/CCPA (privacy), FedRAMP (government), CMMC (DoD), CJIS (law enforcement)
   - If ANY compliance is required, load `decision-trees/compliance-driven.md` FIRST —
     compliance constraints often eliminate entire categories of providers

## Core Decision Logic

Once constraints are known, apply these rules in order. Each rule narrows the
recommendation space. The goal is ONE clear recommendation per category, not a
menu of options.

### STEP 0: Compliance Check (Always First)

```
IF user mentions healthcare, patient data, PHI, medical    → Load compliance-driven.md → HIPAA PATH
IF user mentions enterprise B2B, SOC 2, security audit     → Load compliance-driven.md → SOC 2 PATH
IF user mentions payments, credit cards, PCI               → Load compliance-driven.md → PCI-DSS PATH
IF user mentions EU users, GDPR, privacy, data residency   → Load compliance-driven.md → GDPR PATH
IF user mentions government, federal, FedRAMP, DoD, CJIS   → Load compliance-driven.md → FEDRAMP PATH
IF multiple compliance requirements                        → Load compliance-driven.md → MULTI-COMPLIANCE PATH
IF no compliance mentioned                                 → Proceed to database selection
```

**CRITICAL:** Compliance constraints override cost and convenience preferences.
HIPAA requires BAA verification: Supabase (Team plan+), Vercel (Pro+), Railway (BAA add-on),
Fly.io (BAA available), Clerk (Enterprise), Sentry (Business+) — all now offer BAAs but
require specific plan tiers and configuration. Always verify BAA availability on current plan.
FedRAMP eliminates everything except AWS GovCloud/Azure Government/Google Cloud for Government.
Always check compliance BEFORE recommending any specific provider.

### STEP 1: Database Selection (the foundation — choose this first)

```
IF default for any project                         → PostgreSQL
IF embedded / single-server / read-heavy / edge    → SQLite (Turso)
IF full platform needed (auth+storage+DB+realtime) → Supabase (PostgreSQL)
IF serverless Postgres + branching for dev          → Neon
IF MySQL required (legacy/WordPress)               → PlanetScale or MySQL
IF global distribution + strong consistency        → CockroachDB
IF caching layer needed                            → Redis/Valkey or Upstash
IF reactive real-time collaborative app            → Convex
IF Cloudflare ecosystem committed                  → D1
IF mobile-first + offline required                 → Firebase Firestore
```

### Backend Selection

```
IF TypeScript + simple REST API + max ecosystem    → Express (but note: Fastify is faster)
IF TypeScript + performance matters                → Fastify or Hono
IF TypeScript + multi-runtime / edge deployment    → Hono
IF TypeScript + enterprise patterns + decorators   → NestJS
IF Python + high-perf async API                    → FastAPI
IF Python + rapid dev with admin + ORM + auth      → Django
IF CPU-bound + strict latency + cost-sensitive     → Go (Gin/Chi/Fiber)
IF maximum performance + memory safety             → Rust (Axum)
IF meta-framework handles backend (API routes)     → May not need separate backend
```

### Frontend + Meta-Framework Selection

```
IF content-heavy site, minimal interactivity       → Astro
IF full-stack React app, best ecosystem            → Next.js (watch Vercel costs)
IF Vue ecosystem + full-stack                      → Nuxt
IF smallest bundle + best DX                       → SvelteKit
IF strong nested routes + data loading opinions    → Remix / React Router v7
IF React + maximum self-hosting flexibility        → SvelteKit or Remix
```

### CSS / UI Library

```
IF React + max flexibility + accessibility         → shadcn/ui + Tailwind CSS
IF rapid enterprise prototyping                    → MUI or Ant Design
IF smallest bundle + headless                      → Radix UI + Tailwind
IF Vue project                                     → Radix Vue or PrimeVue
IF Svelte project                                  → Bits UI + Tailwind or shadcn-svelte
```

### Auth Selection

```
IF fastest setup + React/Next.js + budget exists   → Clerk (free to 50k MAU)
IF zero cost + self-hosted + willing to configure  → Better Auth or Auth.js v5
IF using Supabase already                          → Supabase Auth (free with Supabase)
IF enterprise SSO/SAML needed                      → WorkOS (1M MAU free) or Keycloak
IF Google/mobile ecosystem                         → Firebase Auth
IF maximum scale + cheapest per-MAU                → Auth.js self-hosted ($0)
```

### Hosting Selection

```
IF static site / SPA on budget                     → Cloudflare Pages (unlimited BW free)
IF Next.js app                                     → Vercel (best support, set spend limits)
IF API-first / heavy compute                       → Cloudflare Workers (100k req/day free)
IF container workloads + simple PaaS               → Railway or Render
IF cheapest self-managed VPS                       → Hetzner (€3.49/mo)
IF self-hosted with PaaS experience                → Coolify on Hetzner
IF enterprise + complex needs                      → AWS / GCP
IF global edge deployment                          → Fly.io
```

### Payments

```
IF maximum flexibility + custom checkout           → Stripe
IF want MoR (handles taxes for you) + simplicity   → LemonSqueezy
IF B2B SaaS                                        → Stripe
IF digital products / downloads                    → LemonSqueezy or Paddle
IF mobile subscriptions                            → RevenueCat + Stripe
```

## Output Format

When giving a full stack recommendation, use this structure:

```
## Recommended Stack for [Project Description]

| Category | Choice | Reason | Monthly Cost |
|----------|--------|--------|-------------|
| Frontend | [X] | [1-line] | $X |
| Backend | [X] | [1-line] | — |
| Database | [X] | [1-line] | $X |
| Auth | [X] | [1-line] | $X |
| Hosting | [X] | [1-line] | $X |
| Storage | [X] | [1-line] | $X |
| Email | [X] | [1-line] | $X |
| Monitoring | [X] | [1-line] | $X |
| **Total** | | | **$X/mo** |

### Why This Stack
[3-5 sentences: key trade-offs, what was optimized for, what was sacrificed]

### Alternatives Considered
[Table: alternative + why not chosen]

### Scaling Path
[What changes at 10x current scale]
```

## Reference File Loading

Load reference files on-demand based on what the user asks about. Never load all at once.

### By Topic

| User asks about... | Load these references |
|---------------------|---------------------|
| Frontend frameworks | `references/01-frontend-frameworks.md`, `references/02-frontend-meta-frameworks.md` |
| CSS / UI libraries | `references/03-css-ui-libraries.md` |
| Node.js backend | `references/04-backend-node.md` |
| Python backend | `references/05-backend-python.md` |
| Go / Rust backend | `references/06-backend-go-rust.md` |
| Relational databases | `references/07-databases-relational.md` |
| NoSQL databases | `references/08-databases-nosql.md` |
| Serverless databases | `references/09-databases-serverless.md` |
| Authentication | `references/10-auth-solutions.md` |
| Serverless hosting | `references/11-hosting-serverless.md` |
| Container hosting / PaaS | `references/12-hosting-containers.md` |
| VPS / cloud providers | `references/13-hosting-vps-cloud.md` |
| Cross-platform mobile | `references/14-mobile-cross-platform.md` |
| Native mobile | `references/15-mobile-native.md` |
| Real-time / WebSockets | `references/16-realtime-websockets.md` |
| File storage / CDN | `references/17-file-storage-cdn.md` |
| Email services | `references/18-email-services.md` |
| Payments / billing | `references/19-payments-billing.md` |
| Search solutions | `references/20-search-solutions.md` |
| Caching / queues / jobs | `references/21-caching-queues.md` |
| Monitoring / logging | `references/22-monitoring-logging.md` |
| CI/CD / DevOps | `references/23-ci-cd-devops.md` |
| Testing frameworks | `references/24-testing-frameworks.md` |
| ORMs / query builders | `references/25-orm-query-builders.md` |
| API design patterns | `references/26-api-design-patterns.md` |
| AI / ML integration | `references/27-ai-ml-integration.md` |
| Headless CMS | `references/28-cms-headless.md` |
| State management | `references/29-state-management.md` |
| Security | `references/30-security-essentials.md` |
| Desktop apps | `references/31-desktop-apps.md` |
| Costs / pricing | `references/32-cost-matrix.md` |
| HIPAA compliance | `references/33-compliance-hipaa.md` |
| SOC 2 compliance | `references/34-compliance-soc2.md` |
| PCI-DSS compliance | `references/35-compliance-pci-dss.md` |
| GDPR / CCPA privacy | `references/36-compliance-gdpr-ccpa.md` |
| FedRAMP / Government | `references/37-compliance-fedramp-gov.md` |
| Provider compliance matrix | `references/38-compliance-provider-matrix.md` |
| When NOT to use defaults | `references/39-when-not-to-use.md` |
| Cost traps & billing horror stories | `references/40-cost-traps-real-world.md` |
| AI-native architecture patterns | `references/41-ai-native-architecture.md` |
| Migration paths between stacks | `references/42-migration-paths.md` |
| Edge computing & multi-region | `references/43-edge-multi-region.md` |
| Security & zero trust | `references/44-security-zero-trust.md` |
| Emerging frameworks 2025-2026 | `references/45-emerging-frameworks.md` |
| Startup to enterprise evolution | `references/46-startup-to-enterprise.md` |
| Performance benchmarks | `references/47-performance-benchmarks.md` |
| DevOps & platform engineering | `references/48-devops-platform-engineering.md` |
| Monorepo tooling & DX | `references/49-monorepo-dx-tooling.md` |
| Background jobs & events | `references/50-background-jobs-events.md` |
| Vendor lock-in analysis | `references/51-vendor-lock-in-analysis.md` |
| Resilience & fault tolerance | `references/52-resilience-patterns.md` |
| Testing strategies deep dive | `references/53-testing-strategies.md` |
| i18n & internationalization | `references/54-i18n-internationalization.md` |
| Observability & distributed tracing | `references/55-observability-tracing.md` |
| Multi-tenancy architecture | `references/56-multi-tenancy-patterns.md` |
| Feature flags & experimentation | `references/57-feature-flags-experimentation.md` |
| API versioning & webhooks | `references/58-api-versioning-webhooks.md` |
| GraphQL & federation | `references/59-graphql-federation.md` |
| Data pipelines & ETL/ELT | `references/60-data-pipelines-etl.md` |

### By Project Type (Decision Trees)

| Project type | Load decision tree |
|-------------|-------------------|
| Web application | `decision-trees/web-app.md` |
| Mobile application | `decision-trees/mobile-app.md` |
| API / microservice | `decision-trees/api-service.md` |
| SaaS product | `decision-trees/saas-product.md` |
| Side project / MVP | `decision-trees/side-project.md` |
| Compliance-driven project | `decision-trees/compliance-driven.md` |

## Cost Awareness Rules

These rules prevent the most common cost mistakes:

1. **Always quote the free tier limits** — most services have them, and they matter
2. **Flag Vercel bill shock risk** — AI workloads, missing cache headers, bandwidth spikes
3. **Prefer $0-egress storage** — Cloudflare R2 over S3 unless AWS ecosystem locked
4. **Database is the biggest hidden cost** — connection pooling, idle compute, backup retention
5. **Auth costs explode at scale** — Clerk at 100k MAU = $1,825/mo vs Auth.js = $0
6. **Monitoring cost runaway** — error loops can generate $600+/mo in Sentry charges
7. **Always recommend spend limits** — on Vercel, AWS, and any usage-based platform

## The $0 Stack (Side Project Default)

When budget is $0, this stack covers most MVPs:

| Component | Service | Free Tier |
|-----------|---------|-----------|
| Hosting | Cloudflare Pages | Unlimited bandwidth |
| Functions | Cloudflare Workers | 100k requests/day |
| Database | Supabase Free | 500MB, 50k MAU |
| Auth | Supabase Auth | Included (50k MAU) |
| Storage | Supabase Storage | 1GB included |
| Email | Resend | 3,000/month |
| Monitoring | Sentry Free | 5,000 errors/month |
| CI/CD | GitHub Actions | 2,000 min/month |
| CDN | Cloudflare | Included |
| DNS + SSL | Cloudflare | Free |
| **Total** | | **$0/month** |

## Bias Correction Rules

This skill has a natural bias toward Supabase/Vercel/Next.js/Cloudflare. Apply
these counter-checks before finalizing any recommendation:

1. **Challenge Next.js** — If the project is content-heavy, backend-heavy CRUD, or non-JS team,
   check `references/39-when-not-to-use.md`. Django+HTMX, Rails+Hotwire, or Astro may be better.
2. **Challenge Vercel** — If cost at scale matters or long-running processes needed, check alternatives.
   Coolify on Hetzner is 10-50x cheaper at moderate traffic.
3. **Challenge Supabase** — If HIPAA required (verify Team plan+ for BAA), mobile-first offline,
   or document data needed, check alternatives. Supabase now offers BAA on Team plan+ but
   requires specific configuration. Check the counter-recommendation file.
4. **Challenge Cloudflare Workers** — If CPU-intensive, long-running, or WebSocket-heavy, Workers
   won't work. Railway, Fly.io, or VPS are better.
5. **Always present the monolith option** — For B2B SaaS under 100K users, a Django/Rails monolith
   on a $4-20/mo VPS is often the best answer. Don't default to microservices.

When in doubt, load `references/39-when-not-to-use.md` for the full counter-recommendation matrix.

## Anti-Patterns to Flag

When you see these in user plans, warn them:

- **Separate Redis when Postgres can do it** — `pg_trgm` for search, `LISTEN/NOTIFY` for
  pub/sub, `JSONB` for document storage. One database = lower monthly baseline.
- **Choosing MongoDB when they need relations** — PostgreSQL with JSONB handles document
  patterns while keeping JOIN capability.
- **Overengineering auth** — For <10k MAU, any free tier works. Don't spend weeks on custom auth.
- **Kubernetes for <100k users** — Railway, Fly.io, or Coolify on Hetzner is simpler and cheaper.
- **Separate microservices too early** — A monolith on Railway ($20/mo) beats 5 services
  on AWS ($200+/mo) at MVP scale.
- **GraphQL when tRPC suffices** — If it's a TypeScript monorepo, tRPC gives end-to-end type
  safety with zero schema overhead.
- **Ignoring SQLite** — For read-heavy, single-server, edge, or embedded use cases, Turso/SQLite
  can be 5-10x cheaper than managed Postgres.
- **No feature flags for launches** — Ship behind flags with kill switches. Reverting a deploy
  takes 10+ minutes; flipping a flag takes seconds. See `references/57-feature-flags-experimentation.md`.
- **Single-tenant when multi-tenant works** — Separate DBs per tenant at <100 tenants is wasteful.
  PostgreSQL RLS handles most SaaS tenancy needs. See `references/56-multi-tenancy-patterns.md`.
- **Skipping i18n at launch** — Retrofitting i18n is 3-5x more expensive than building it in.
  If there's any chance of international users, set up next-intl/react-i18next from day one.
- **Monitoring without observability** — Logs and uptime checks aren't enough. Add OpenTelemetry
  traces to catch the root cause of slow endpoints. See `references/55-observability-tracing.md`.
- **No API versioning strategy** — Adding versioning after launch forces breaking changes on clients.
  Choose URL path versioning (simplest) or header versioning from day one. See `references/58-api-versioning-webhooks.md`.
- **GraphQL federation too early** — Apollo Federation adds massive complexity. Start with a monolithic
  schema; federate only when multiple teams own distinct domains. See `references/59-graphql-federation.md`.
- **ETL pipelines without observability** — Silent data pipeline failures corrupt downstream analytics
  for days. Wire up OpenTelemetry + dead-letter queues from the start. See `references/60-data-pipelines-etl.md`.

## Technology Lifecycle Awareness

Before recommending anything, check its current status:

- **Lucia Auth** → DEPRECATED (March 2025). Migrate to Better Auth or Auth.js v5.
- **PlanetScale free tier** → REMOVED (2024). Cheapest plan now Scaler at $39/mo.
- **Redis licensing** → Changed to tri-license (2024). Consider Valkey (Linux Foundation fork) or Upstash.
- **AWS Lambda cold start billing** → Changed Aug 2025. Now bills for INIT phase.
- **Netlify pricing** → Changed Sept 2025. New credit-based system.
- **GitHub Actions pricing** → New $0.002/min platform charge (2026) for private repos.
- **Vercel free tier** → Tightened bandwidth limits; AI workloads can trigger surprise bills.

Always search for `"[technology] deprecated 2026"` or `"[technology] pricing change 2026"`
before recommending tools that are known to have unstable pricing or licensing.

## Pricing Decay Prevention System

Reference files contain hardcoded pricing data that goes stale. Use this 4-layer system
to prevent recommending outdated prices:

### Layer 1: Stability Classification
Every reference file contains a metadata comment indicating pricing volatility:
```
<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->
<!-- PRICING_STABILITY: MODERATE | Updated: 2026-03-03 | Tool/platform pricing changes annually. Verify before critical decisions. -->
<!-- PRICING_STABILITY: HIGH_VOLATILITY | Updated: 2026-03-03 | Cloud/SaaS pricing changes quarterly. Verify current pricing at provider websites before recommending. -->
```
All 60 reference files now contain this metadata. Check the stability level before quoting prices.

### Layer 2: What to Hardcode vs. What to Search

**SAFE TO HARDCODE (stable for 12+ months):**
- Architecture patterns and decision logic (never expire)
- Compliance requirements (change with major regulatory versions only)
- Payment processing fees (Stripe 2.9%+30¢ stable since 2011)
- Open-source tools ($0 is always $0)
- Relative cost comparisons ("Hetzner is ~10x cheaper than Vercel at scale")

**USE RANGES (moderate volatility, 6-month shelf life):**
- SaaS tool pricing (Clerk, Auth0, Supabase Pro, etc.) → Use "$X-Y/mo" ranges
- Cloud compute pricing (EC2, Cloud Run) → Use tier descriptions not exact cents
- Compliance automation tools (Vanta, Drata) → Use "~$X,000/yr" approximations

**ALWAYS SEARCH BEFORE QUOTING (high volatility):**
- Free tier limits (change frequently without notice)
- AI/LLM API pricing (changes monthly)
- Startup credits and promotions
- Any price that was recently changed (check lifecycle awareness section)

### Layer 3: Staleness Warnings
When presenting pricing from reference files, always add context:
```
Cost estimates based on [Month Year] data. Verify current pricing at [provider].
Pricing patterns and relative comparisons remain valid even if exact numbers shift.
```

### Layer 4: Search Verification
Before quoting ANY specific dollar amount in a recommendation:
1. Check the `PRICING_STABILITY` metadata in the reference file
2. If `HIGH_VOLATILITY` or `Updated` date > 3 months ago → Search current pricing
3. If `MODERATE` and `Updated` date > 6 months ago → Search current pricing
4. If `STABLE` → Hardcoded value is likely still accurate
5. For AI/LLM pricing → ALWAYS search regardless of metadata (prices change monthly)

## Progressive Summarization (Context Efficiency)

Reference files can be 30-80KB each. Loading multiple files consumes context fast.
Use this layered approach:

### Loading Strategy
1. **First pass: Load only SKILL.md** — Contains decision logic and file mapping
2. **Second pass: Load the relevant decision tree** — 150-250 lines, manageable
3. **Third pass: Load specific reference files only when needed** — Deep data

### When Loading Reference Files
- **Load the executive summary section first** (top of each file, ~20 lines)
- **Only load detailed sections** when the user asks follow-up questions
- **Never load more than 2-3 reference files** in a single response
- **For compliance, start with `38-compliance-provider-matrix.md`** — it's the quick-lookup
  table. Only load individual compliance files (33-37) for deep dives.

### Reference File Structure (all files follow this pattern)
```
## Executive Summary          ← Always read this (5-10 lines)
## [Topic] Overview           ← Read if user needs context
## Detailed Comparison Tables ← Read only for specific comparisons
## Decision Logic             ← Read when making recommendations
## Cost Breakdown            ← Read only when discussing pricing
## Common Mistakes           ← Skim for relevant warnings
```

### Priority Loading Order for Common Questions
| Question Type | Load First | Load If Needed |
|--------------|-----------|----------------|
| "What stack for my SaaS?" | SKILL.md + saas-product.md | Specific reference by category |
| "Which database?" | SKILL.md (DB section) | 07/08/09-databases-*.md |
| "I need HIPAA compliance" | compliance-driven.md + 38-provider-matrix.md | 33-compliance-hipaa.md |
| "Compare X vs Y" | The specific reference file for that category | 32-cost-matrix.md |
| "Cheapest option for..." | SKILL.md ($0 stack) + 32-cost-matrix.md | 39-when-not-to-use.md |
| "Monorepo setup" | 49-monorepo-dx-tooling.md | 23-ci-cd-devops.md |
| "Background jobs / queues" | 50-background-jobs-events.md | 21-caching-queues.md |
| "Vendor lock-in concerns" | 51-vendor-lock-in-analysis.md | 42-migration-paths.md |
| "Reliability / resilience" | 52-resilience-patterns.md | 22-monitoring-logging.md |
| "Testing strategy" | 53-testing-strategies.md | 24-testing-frameworks.md |
| "Scale to enterprise" | 46-startup-to-enterprise.md | 34-compliance-soc2.md |
| "i18n / multilingual" | 54-i18n-internationalization.md | 02-frontend-meta-frameworks.md |
| "Observability / tracing" | 55-observability-tracing.md | 22-monitoring-logging.md |
| "Multi-tenant / SaaS tenancy" | 56-multi-tenancy-patterns.md | 07-databases-relational.md |
| "Feature flags / A/B testing" | 57-feature-flags-experimentation.md | 22-monitoring-logging.md |
| "API versioning / webhooks" | 58-api-versioning-webhooks.md | 26-api-design-patterns.md |
| "GraphQL / federation" | 59-graphql-federation.md | 26-api-design-patterns.md |
| "Data pipelines / ETL" | 60-data-pipelines-etl.md | 07-databases-relational.md |
