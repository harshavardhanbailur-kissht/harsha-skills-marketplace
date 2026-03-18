# Decision Tree: SaaS Product

## Entry Point

A SaaS product combines web app + backend + user management + billing + monitoring.
This tree gives complete stacks at each scale tier.

```
What stage is your SaaS?
├── Idea / MVP (validate fast, $0 budget)
│   → STAGE 0
├── Launched, first paying customers (1–1k users)
│   → STAGE 1
├── Growing, product-market fit (1k–10k users)
│   → STAGE 2
├── Scaling (10k–100k users)
│   → STAGE 3
└── Large scale (100k+ users)
    → STAGE 4
```

---

## STAGE 0: MVP ($0/month)

**Goal:** Ship in 2–4 weeks. Validate the idea. Spend nothing.

| Category | Choice | Why | Cost |
|----------|--------|-----|------|
| Frontend | Next.js (App Router) + Tailwind + shadcn/ui | Fastest full-stack DX | $0 |
| Backend | Next.js API Routes | No separate service needed | $0 |
| Database | Supabase Free | 500MB Postgres + Auth + Storage + Realtime | $0 |
| Auth | Supabase Auth | Included, 50k MAU, social + email login | $0 |
| ORM | Drizzle | Lightweight, serverless-friendly, great types | $0 |
| Payments | Stripe (test mode) or LemonSqueezy | Don't integrate until you have demand | $0 |
| Hosting | Vercel Free | Auto-deploy from GitHub | $0 |
| Email | Resend Free | 3k transactional emails/month | $0 |
| Monitoring | Sentry Free | 5k errors/month | $0 |
| Analytics | Plausible CE (self-host) or Vercel Analytics | Basic traffic tracking | $0 |
| CI/CD | GitHub Actions | 2k min/month free | $0 |
| **Total** | | | **$0/mo** |

**What you get for $0:** Full-stack app with auth, database, email, error tracking,
auto-deploys, and free SSL/CDN.

---

## STAGE 1: First Customers ($25–75/month)

**Goal:** Reliable for paying users. Start collecting revenue. Keep costs low.

| Category | Choice | Why | Cost |
|----------|--------|-----|------|
| Frontend | Next.js + Tailwind + shadcn/ui | Same as MVP, proven | $0 |
| Backend | Next.js API Routes + Hono (if complex) | Separate API only if needed | $0 |
| Database | Supabase Pro | No auto-pause, 8GB, daily backups | $25/mo |
| Auth | Supabase Auth or Clerk Free (10k MAU) | Clerk if need pre-built components | $0–25 |
| ORM | Drizzle | Migrations + type safety | $0 |
| Payments | Stripe | 2.9% + $0.30/transaction | % only |
| Hosting | Vercel Pro | 1TB bandwidth, team features | $20/mo |
| Email | Resend Free → AWS SES | Upgrade when hitting 3k/mo limit | $0–5 |
| Monitoring | Sentry Free | Upgrade at 5k errors | $0 |
| Storage | Supabase Storage (included) | 100GB on Pro | $0 |
| DNS/CDN | Cloudflare Free | DNS + DDoS + basic WAF | $0 |
| **Total** | | | **$45–75/mo** |

**Key decisions at this stage:**
- Don't separate frontend and backend yet
- Don't add Redis/caching yet (Postgres handles it)
- Don't add search (use `pg_trgm` in Postgres)
- DO set up proper error tracking and backups

---

## STAGE 2: Product-Market Fit ($100–300/month)

**Goal:** Scale infrastructure to match growing demand. Add team tooling.

| Category | Choice | Why | Cost |
|----------|--------|-----|------|
| Frontend | Next.js + shadcn/ui | Same, battle-tested | $0 |
| Backend | Hono or Fastify (separate service) | API complexity warrants separation | $0 |
| Database | Neon Scale ($69) or Supabase Pro ($25+overages) | Neon branching helps development | $25–70 |
| Auth | Clerk Pro ($25/mo) or Better Auth ($0) | Pre-built org management saves dev time | $0–25 |
| ORM | Drizzle | Serverless-compatible, edge-ready | $0 |
| Payments | Stripe + billing portal | Subscription management, webhooks | % only |
| Hosting | Vercel Pro + Railway (API) | Separate API service for reliability | $25–40 |
| Email | AWS SES ($0.10/1k) + React Email | Templates + cheap delivery | $5–20 |
| Monitoring | Sentry Team ($26) | Source maps, performance monitoring | $26 |
| Storage | Cloudflare R2 | $0 egress, cheaper than S3 | $1–10 |
| Search | Meilisearch (self-hosted on Railway) | Great UX, free, easy to run | $5–10 |
| Caching | Upstash Redis (serverless) | Session cache, rate limiting | $0–10 |
| Background Jobs | Inngest or Trigger.dev (free tier) | Reliable async processing | $0–25 |
| CI/CD | GitHub Actions | Still free tier sufficient | $0 |
| DNS/CDN | Cloudflare Free | Upgrade to Pro if need WAF rules | $0–20 |
| **Total** | | | **$100–280/mo** |

**Key decisions at this stage:**
- Separate API from frontend (reliability + independent scaling)
- Add proper caching (Upstash Redis for sessions, rate limiting)
- Add background jobs (email sequences, webhooks, data processing)
- Consider search if users need it (Meilisearch is free and excellent)
- Start monitoring costs monthly

---

## STAGE 3: Scaling ($300–1,000/month)

**Goal:** Handle 10k–100k users. Optimize cost per user. Add enterprise features.

| Category | Choice | Why | Cost |
|----------|--------|-----|------|
| Frontend | Next.js + shadcn/ui | Same | $0 |
| Backend | Fastify or NestJS | Enterprise patterns, middleware ecosystem | $0 |
| Database | Neon Scale or dedicated Postgres (Railway/Supabase) | Need connection pooling, read replicas | $70–150 |
| Auth | WorkOS ($0 to 1M MAU) + Clerk (consumers) | Enterprise SSO + consumer auth split | $0–200 |
| ORM | Drizzle or Prisma | Prisma if team prefers, Drizzle if edge | $0 |
| Payments | Stripe | Consider annual plans for cash flow | % only |
| Hosting | Vercel Pro + Railway Pro | Or migrate API to Hetzner + Coolify | $40–100 |
| Email | AWS SES | Volume pricing kicks in | $10–50 |
| Monitoring | Sentry Business ($80) + Axiom ($50) | APM + structured logging | $80–130 |
| Storage | Cloudflare R2 + BunnyCDN | R2 for files, BunnyCDN for assets | $10–50 |
| Search | Meilisearch (dedicated) or Typesense Cloud | Self-hosted or managed depending on ops capacity | $10–50 |
| Caching | Upstash Redis Pro | Higher throughput, global replication | $10–50 |
| Background Jobs | Inngest Pro or Trigger.dev Pro | Reliable at scale, dashboards | $25–100 |
| CI/CD | GitHub Actions + self-hosted runners | Save on build minutes | $0–20 |
| Security | Cloudflare Pro WAF | Rate limiting, bot protection | $20 |
| **Total** | | | **$300–900/mo** |

**Key decisions at this stage:**
- Add enterprise SSO (WorkOS makes this trivial)
- Implement proper rate limiting (Cloudflare WAF + Upstash)
- Add audit logging (enterprise customers expect this)
- Consider self-hosting on Hetzner to cut hosting costs 50-70%
- Set up cost monitoring dashboards

---

## STAGE 4: Large Scale ($1,000–5,000+/month)

**Goal:** Optimize cost per user. Reserved capacity. Compliance.

| Category | Choice | Why | Cost |
|----------|--------|-----|------|
| Database | Dedicated Postgres (AWS RDS RI or Supabase Enterprise) | Reserved instances save 30-70% | $200–500 |
| Auth | WorkOS + custom (Auth.js at this scale saves $$$) | Clerk at 100k MAU = $1,825/mo | $0–500 |
| Hosting | AWS/GCP with reserved instances OR Hetzner dedicated | Reserved = 30-50% savings | $100–500 |
| Email | AWS SES (volume) | $0.02/1k at high volume | $20–100 |
| Monitoring | DataDog or Grafana Cloud + Sentry | Comprehensive APM | $200–500 |
| CDN | Cloudflare Enterprise or BunnyCDN | Volume pricing | $50–200 |
| **Total** | | | **$1,000–5,000/mo** |

**Optimization strategies at this scale:**
- Reserved instances everywhere (30-70% savings)
- Self-host what you can (auth, search, monitoring)
- Multi-region for latency (not just redundancy)
- Cost per user should be <$0.05/mo at this scale

---

## B2B vs B2C SaaS Differences

### B2B SaaS (Selling to Businesses)

Additional requirements:
- **SSO/SAML** → WorkOS (simplest) or Keycloak (self-hosted)
- **Audit Logs** → WorkOS Audit Logs or custom (Postgres + event sourcing)
- **RBAC** → Clerk Organizations or custom implementation
- **Data Residency** → EU hosting option (Hetzner Frankfurt, AWS eu-west)
- **SOC 2 / HIPAA** → Supabase Enterprise or AWS with compliance modules
- **Admin Dashboard** → Payload CMS or custom with Tremor/shadcn charts

### B2C SaaS (Selling to Consumers)

Additional requirements:
- **Social Login** → Clerk or Supabase Auth (multiple providers)
- **Mobile App** → Expo (React Native) sharing API with web
- **Push Notifications** → Firebase Cloud Messaging (free)
- **In-App Purchases** → RevenueCat (manages Apple/Google billing)
- **Viral/Referral** → Custom implementation or Rewardful

---

## Billing Integration Patterns

### Subscription SaaS (Monthly/Annual)

```
Payment Provider:  Stripe (most flexible) or LemonSqueezy (handles taxes)
Webhook Handler:   Listen for: checkout.session.completed, invoice.paid,
                   customer.subscription.updated, customer.subscription.deleted
Database Sync:     Store subscription status in your DB, Stripe is source of truth
Customer Portal:   Stripe Customer Portal (free, hosted by Stripe)
Pricing Page:      Build custom (shadcn/ui components) → Stripe Checkout
```

### Usage-Based Billing

```
Metering:          Track usage in your database (pg counters or Redis)
Billing:           Stripe Metered Billing or custom invoice generation
Reporting:         Stripe Revenue Recognition or custom dashboards
```

### One-Time Payments (Digital Products)

```
Provider:          LemonSqueezy (simplest, handles VAT/sales tax)
Alternative:       Stripe Payment Links (quick, no code needed)
Delivery:          Webhook → unlock content or send download link
```

---

## MULTI-TENANCY PATTERNS

This is one of the most critical architectural decisions for SaaS. Choose wrong and you'll rewrite it.

### Multi-Tenancy Isolation Levels

| Level | Isolation | Security | Cost | Complexity | Common Attacks |
|-------|-----------|----------|------|-----------|-----------------|
| **Row-Level (RLS)** | Logical (same database) | 85% (depends on code) | $0 | Low | SQL injection, unintended joins |
| **Schema-per-Tenant** | Logical (same DB, diff schemas) | 90% | $0–50 | Medium | Schema enumeration, backup confusion |
| **DB-per-Tenant** | Physical (separate databases) | 95% | 50–100% cost multiplier | High | Cross-DB leaks (backup exposure) |
| **Kubernetes Namespace** | Container-level | 80% | 20–50% | Very High | Container escape, shared kernel |

### Multi-Tenancy Decision Matrix

| Your Scale | Isolation Needs | Implementation | Cost | When to Upgrade |
|-----------|-----------------|-----------------|------|-----------------|
| **<100 customers** | Low (shared data OK) | Shared DB + RLS | $25–50/mo | 1000+ customers |
| **100–1k customers** | Medium (some isolation) | Shared DB + Organization schema | $50–200/mo | Enterprise deals |
| **1k–10k customers** | High (enterprise demands it) | DB per tenant OR strong RLS | $200–1000/mo | High-value accounts |
| **10k+ customers** | Very High (strict separation) | Hybrid: shared DB for SMB, DB per tenant for enterprise | $500–3000+/mo | Regulatory demand |

### Implementation Details

#### Option 1: Row-Level Security (RLS)

**How it works:**
```sql
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy: users can only see their own records
CREATE POLICY user_isolation ON users
  FOR SELECT USING (user_id = current_user_id());

-- Create policy: users can only see data for their organization
CREATE POLICY org_isolation ON posts
  FOR SELECT USING (organization_id = current_organization_id());
```

**Pros:**
- Cheapest (no extra infrastructure)
- Simplest to implement
- Single database to manage

**Cons:**
- Requires careful code review (easy to accidentally bypass)
- All tenants share database performance
- Debugging is harder (mixed data in logs)

**Cost:** $0 extra (included in database)
**Best for:** MVP to early growth (100–1000 customers)

---

#### Option 2: Schema-per-Tenant

**How it works:**
```sql
-- Create schema for each tenant
CREATE SCHEMA tenant_123;
CREATE SCHEMA tenant_456;

-- Each schema has same tables
CREATE TABLE tenant_123.users (...)
CREATE TABLE tenant_456.users (...)

-- Application logic:
SET search_path = tenant_123;
SELECT * FROM users;  -- Only gets tenant_123 users
```

**Pros:**
- Strong isolation (separate namespaces)
- Can backup/restore per tenant
- Can have different schemas per tenant (customization)

**Cons:**
- Schema migrations are complex (update 1000+ schemas)
- Connection pooling becomes tricky (one pool per schema)
- Debugging requires knowing which schema to check

**Cost:** $0–50/mo (slightly higher due to management overhead)
**Best for:** 100–5000 customers with varying feature sets

**Real-world tools:**
- **PgBoss** (Node.js) - Schema management library
- **django-tenants** (Python) - Automatic schema switching
- **Citus** (PostgreSQL extension) - Distributed schemas

---

#### Option 3: Database-per-Tenant

**How it works:**
```
Customer A → Database A (Postgres)
Customer B → Database B (Postgres)
Customer C → Database C (Postgres)

Central "Control DB" tracks which customer owns which DB
```

**Pros:**
- Maximum isolation (separate databases)
- Easy to backup/restore individual customers
- Can provision different hardware per customer
- Enterprise customers will demand this

**Cons:**
- 10–100x operational complexity
- Cross-tenant analytics is very hard
- Migrations are nightmare (update 10,000 databases)
- Cost multiplier: 50–100% higher infrastructure

**Cost:** $200–1000+/mo per tenant (highly dependent on size)
**Best for:** Enterprise SaaS with high-value customers

**Cost optimization:** Use branching databases:
```
Neon: Create branch for each tenant (read-only)
Cost: Base DB ($25) + branches ($0.10 each)
1000 customers = $125/mo (vs $25,000 with separate databases)
```

Turso: Embedded replicas per region
```
SQLite with replication to each edge location
Cost: $30/mo for unlimited replicas
Best for: Global low-latency access
```

---

#### Option 4: Hybrid Approach (Recommended for Mature SaaS)

**Implementation:**
```
Tier 1: Startup customers (100+)
  → Shared database + RLS
  → Cost: $25/mo database

Tier 2: Growing customers (1k–10k)
  → Schema per tenant
  → Cost: $25/mo database + $50 management

Tier 3: Enterprise customers (10–100)
  → Database per tenant (Neon branches)
  → Cost: $25 + (number of branches × $0.10)
```

**Advantages:**
- Cost-effective for SMB
- Enterprise-grade for big deals
- Easy to migrate customers up tiers

---

### Multi-Tenancy Challenges & Solutions

| Challenge | Problem | Solution |
|-----------|---------|----------|
| **Tenant data bleed** | Query returns wrong tenant's data | Mandatory WHERE org_id filter, test extensively |
| **Shared resource explosion** | One tenant's query slows everyone | Connection pooling limits, per-tenant query budgets |
| **Migration across tiers** | Moving from RLS to DB-per-tenant | Custom migration tool, validate data integrity |
| **Backup/restore** | Which tenant's data to restore? | Incremental backups per tenant, point-in-time recovery |
| **Performance debugging** | Which tenant caused the slowdown? | Add tenant_id to all logs, query profiling per tenant |
| **Regulatory requirement** | Customer demand DB separation | Offer enterprise tier with dedicated databases |

---

## PRICING & BILLING ARCHITECTURE DECISIONS

Your pricing model drives your technical architecture.

### Pricing Model Comparison

| Model | Complexity | Revenue | Cost | Best For |
|-------|-----------|---------|------|----------|
| **Flat Rate** | Low | Predictable | High (underutilized users) | Simple products, SMB |
| **Per-Seat** | Low | Predictable | Medium | Team/org software |
| **Tiered Features** | Medium | Higher than flat | Medium | Freemium → paid upgrade |
| **Usage-Based** | High | Highly variable | Low upfront, high ops | APIs, computing |
| **Hybrid** | Very High | Best but volatile | High ops | Enterprise + SMB both |

### Billing Architecture at Each Scale

#### MVP: No Billing (Free Forever)
```
Focus on product, not revenue
Use Stripe test mode
Build out payment flow
No webhooks, no metering
```

#### STAGE 1: Simple Subscription (Monthly/Annual)

**Database schema:**
```sql
CREATE TABLE subscriptions (
  id UUID,
  customer_id UUID,
  plan_id TEXT ('starter', 'pro', 'enterprise'),
  status TEXT ('active', 'paused', 'canceled'),
  current_period_start DATE,
  current_period_end DATE,
  stripe_subscription_id TEXT
);
```

**Webhook handlers needed:**
- `checkout.session.completed` → Create subscription
- `customer.subscription.updated` → Update plan
- `customer.subscription.deleted` → Downgrade/remove

**Cost:** $0–50/mo in Stripe fees (2.9% + $0.30 per transaction)

---

#### STAGE 2: Usage-Based Billing (API calls, storage, etc)

**Database schema:**
```sql
CREATE TABLE usage_events (
  id UUID,
  customer_id UUID,
  metric_name TEXT ('api_calls', 'storage_gb', 'users'),
  quantity INT,
  recorded_at TIMESTAMP,
  billing_period TEXT ('2024-03')
);

CREATE TABLE metered_charges (
  id UUID,
  subscription_id UUID,
  metric_name TEXT,
  quantity INT,
  unit_price DECIMAL,
  total_price DECIMAL,
  billing_period TEXT
);
```

**Implementation options:**

| Option | Effort | Accuracy | Cost |
|--------|--------|----------|------|
| **Track in application code** | 2 days | 90% (misses edge cases) | $0 |
| **Stripe Metering API** | 4 days | 95% | $0 (included with Stripe) |
| **Custom metering platform** | 2 weeks | 99% | $0–500/mo (infrastructure) |

**Real example:**
- GitHub Actions: $0.008 per minute for Linux, $0.016 for Windows
- Stripe: $0.005 per API call after 1M free
- Supabase: $1 per GB of storage over 500MB free

---

#### STAGE 3: Enterprise Billing (Custom quotes, annual)

**Requirements:**
- Manual invoicing capability
- Multi-year contracts
- Custom terms per deal (volume discounts, payment terms)
- Licensing model (per-user, per-org, per-feature)

**Tools:**
- Stripe Billing (handles most cases)
- Zuora (for extreme complexity)
- Custom invoice system (if <100 enterprise deals)

**Architecture:**
```
Sales team negotiates deal
  ↓
Custom subscription created in admin dashboard
  ↓
Annual invoice generated (PDF, email)
  ↓
License activated in product
  ↓
Quarterly reviews for renewal
```

---

## FEATURE FLAG STRATEGY

Feature flags let you ship code without releasing features—critical for coordinating teams.

### Feature Flag Types

| Type | Scope | Use Case | Cost |
|------|-------|----------|------|
| **Boolean** | ON/OFF | Kill switch, gradual rollout | $0–100/mo |
| **Percentage** | 10% of users | A/B test | $50–200/mo |
| **User-Specific** | List of IDs | Early access, beta | $50–200/mo |
| **Audience** | Rules (country, plan, etc) | Tier-specific features | $100–500/mo |
| **Multivariate** | Multiple values | Test variations | $200–500/mo |

### Feature Flag Tooling

| Tool | Cost | Deployment | Best For |
|------|------|-----------|----------|
| **LaunchDarkly** | $10–500/mo | Production release | Enterprise, large teams |
| **Statsig** | $0–200/mo | Product analytics + flags | Growth-focused teams |
| **PostHog** | $0 (self-host) or $20+/mo | Analytics + flags | Open source, cost-conscious |
| **Unleash** | Free (self-hosted) | On-premise | High control, self-hosted |
| **Google Firebase** | $0–50/mo | Mobile + web | Google ecosystem, mobile |
| **Custom (Redis + Code)** | $0 | Full control | Minimal overhead, small team |

### Feature Flag Architecture

**Simple implementation (MVP):**
```typescript
// featureFlags.ts
const flags = {
  newDashboard: ['user_123', 'user_456'],
  aiFeature: { percentage: 10 },  // 10% rollout
  darkMode: { plan: ['pro', 'enterprise'] }
};

// In app
if (hasFeature('newDashboard', userId)) {
  return <NewDashboard />;
}
```

**Production implementation:**
```typescript
// Fetch flags from service
const flagService = new LaunchDarkly({
  sdkKey: process.env.LD_SDK_KEY
});

const user = { key: userId, custom: { plan: 'pro' } };
const isEnabled = flagService.variation('newDashboard', user, false);

// Change without deploying!
// LaunchDarkly dashboard: toggle flag OFF
// All users instantly see old dashboard
```

**Recommended flow:**
1. Ship code behind flag (OFF by default)
2. Enable for internal team (1% rollout)
3. Expand to 10% → 50% → 100%
4. Remove flag and dead code

---

## TEAM SIZE SCALING TRIGGERS

Know when to hire and what to hire for.

| Team Size | Triggers for Growth | Hiring Priority | Estimated MRR |
|-----------|-------------------|-----------------|---------------|
| **1 person** | Building everything | None yet | $0–1k |
| **2 people** | Sales taking time, product backlog growing | Hire sales/ops | $1k–5k |
| **3–5 people** | Infrastructure becoming hard to manage, feature requests > velocity | Hire DevOps/SRE | $5k–20k |
| **5–10 people** | Customer support is 50% of time, product roadmap unclear | Hire customer success | $20k–100k |
| **10–20 people** | Engineering velocity slowing, unclear priorities | Hire product manager | $100k–500k |
| **20+ people** | Communication chaos, unclear decisions | Hire leadership/structure | $500k–5M |

### Scaling Infrastructure Triggers

| Metric | Trigger | Action | Cost Impact |
|--------|---------|--------|------------|
| **Database size** | >100GB | Add read replicas | +$100–200/mo |
| **QPS** | >1000 req/sec | Add caching layer (Redis) | +$50–200/mo |
| **Users** | >10k | Move to dedicated hosting | +$200–500/mo |
| **Storage** | >1TB | Migrate to S3/R2 | +$50–200/mo |
| **Team size** | >10 people | Add staging environment + CI/CD | +$100–300/mo |
| **Downtime tolerance** | <1 hour/quarter | Add redundancy, multi-region | +$500+/mo |

---

## INFRASTRUCTURE COST MODELING AT DIFFERENT SCALES

Critical for pricing strategy and fundraising conversations.

### Cost Per User at Each Scale (Monthly)

| User Count | Database | Hosting | Bandwidth | Cache | Monitoring | Email | **Total/User** |
|-----------|----------|---------|-----------|-------|-----------|-------|---------------|
| **100 users** | $25 | $20 | $2 | $0 | $0 | $5 | **$0.52/user** |
| **1,000 users** | $50 | $40 | $5 | $10 | $10 | $10 | **$0.125/user** |
| **10,000 users** | $150 | $100 | $20 | $50 | $50 | $50 | **$0.042/user** |
| **100,000 users** | $500 | $500 | $100 | $200 | $200 | $200 | **$0.018/user** |
| **1M users** | $2000 | $2000 | $500 | $1000 | $1000 | $1000 | **$0.0075/user** |

**Key insight:** Your unit costs drop 50-100x as you scale. Use this to set pricing:
- At 100 users: charge $5–10/user/mo
- At 10k users: can lower to $1–2/user/mo
- At 100k users: can do $0.10–0.50/user/mo

### Real Cost Breakdown at 10k Users

Assuming $50/mo ARPU (Average Revenue Per User):

```
Revenue:          10,000 users × $50 = $500,000/mo

Infrastructure Costs:
  Database        $150/mo (PostgreSQL)
  Hosting         $100/mo (APIs)
  Bandwidth       $20/mo
  Cache           $50/mo (Redis)
  Monitoring      $50/mo
  Email/SMS       $50/mo
  Total Tech:     ~$420/mo

Operational Costs:
  Customer Success        20% of revenue = $100k/mo
  Engineering            20% of revenue = $100k/mo
  Sales & Marketing      30% of revenue = $150k/mo
  Miscellaneous          10% of revenue = $50k/mo
  Total Ops:      ~$400k/mo

**Gross Margin: $500k - $0.4k = 99.9% (tech only)**
**Unit Economics: 20% net margin (after ops)**
```

---

## OBSERVABILITY & MONITORING AT SCALE

As you grow, observability moves from "nice to have" to "critical".

### Monitoring by Growth Stage

| Stage | Tools | Cost | Alert Setup |
|-------|-------|------|------------|
| **MVP** | Sentry Free + Console logs | $0 | Email alerts on errors |
| **Growing** | Sentry + CloudWatch | $50–100/mo | PagerDuty on critical errors |
| **Scaling** | Datadog + Grafana | $200–500/mo | SLO-based alerts, on-call rotation |
| **Enterprise** | Datadog + VictorOps + Splunk | $1000+/mo | Advanced anomaly detection |

### Key SaaS Metrics to Track

| Metric | Why | Target | Alert If |
|--------|-----|--------|----------|
| **Uptime** | Revenue impact | >99.9% | <99.5% |
| **API latency (p95)** | User experience | <500ms | >2sec |
| **Error rate** | Product quality | <0.1% | >1% |
| **Database conn pool** | Resource exhaustion | 50–70% used | >80% |
| **Session timeout (API)** | Auth issues | 0 unexpected | >0 |
| **Invoice delivery** | Revenue recognition | 100% delivered | <99% |
| **Webhook delivery** | Partner reliability | >99% | <95% |

---

## FEATURE FLAG STRATEGY AT SCALE

Feature flags enable shipping code without shipping features—essential for coordinated teams.

### Feature Flag Maturity Levels

**Level 1: Simple Boolean Flags (MVP)**
```json
{
  "flags": {
    "newDashboard": false,
    "betaAI": false
  }
}
```
Cost: $0
Limitations: Can't do gradual rollouts, analytics

**Level 2: Percentage-Based Rollouts**
```json
{
  "flags": {
    "newDashboard": { "percentage": 10 },  // 10% of users
    "betaAI": { "percentage": 50 }  // 50% of users
  }
}
```
Cost: $0–50/mo
Use case: A/B testing, gradual rollouts

**Level 3: Audience-Specific Rules**
```json
{
  "flags": {
    "newDashboard": {
      "audiences": [
        { "plan": "pro", "percentage": 100 },      // All pro users
        { "plan": "starter", "percentage": 20 }    // 20% of starters
      ]
    }
  }
}
```
Cost: $50–200/mo
Use case: Tier-based features, beta programs

**Level 4: Complex Rules + Analytics**
```json
{
  "flags": {
    "newDashboard": {
      "audiences": [
        { "plan": "pro", "percentage": 100 },
        { "country": "US", "signupDate": "2024-01-01", "percentage": 50 }
      ],
      "trackingMetrics": ["conversion", "latency", "error_rate"]
    }
  }
}
```
Cost: $100–500/mo (LaunchDarkly, Statsig)
Use case: Complex targeting, experimentation platform

### Feature Flag Deployment Workflow

```
Week 1: Ship code behind flag (OFF)
  - New dashboard code deployed
  - Feature behind flag { newDashboard: false }
  - No users see it yet

Week 2: Enable for internal team
  - { newDashboard: { audiences: [{ email: "@company.com" }] } }
  - Team tests, finds bugs
  - Iterate quickly

Week 3: Gradual rollout
  - Day 1: { percentage: 5 }  → 5% of users
  - Day 2: { percentage: 25 } → 25% of users
  - Day 3: { percentage: 50 } → 50% of users
  - Monitor error rate, latency, conversion

Week 4: Full rollout
  - { percentage: 100 } → All users
  - Monitor for 1 week

Week 5: Remove flag
  - Delete flag code
  - Remove from config
  - Simplify codebase
```

### Feature Flag Implementation by Tool

**Self-Hosted (Cost: $0 + ops)**
```typescript
// Simple Redis-backed flag service
const flags = await redis.hgetall('feature_flags');
if (flags.newDashboard === 'on') {
  // Show new dashboard
}
```
Pros: Zero cost, full control
Cons: No analytics, manual rollouts, DevOps work

**Managed (Cost: $50–500/mo)**
```typescript
// LaunchDarkly
import { LDClient } from '@launchdarkly/node-server-sdk';

const client = new LDClient(sdkKey);
const user = { key: userId, custom: { plan: 'pro' } };

if (await client.variation('newDashboard', user, false)) {
  // Show new dashboard
}
```
Pros: Analytics, targeting, experiments
Cons: Monthly cost, vendor lock-in

### Real-World Feature Flag Example: Slack

Slack uses feature flags to:
1. **Ship confidentially:** New features built for months before launch
2. **Gradual rollout:** Features rolled out to 1% → 10% → 100%
3. **A/B test:** Test different designs on different users
4. **Kill switch:** Disable broken features instantly if issues arise

Result: Can deploy new features daily without risk of breaking all users.

---

## SCALING TEAM STRUCTURE AT EACH STAGE

Knowing when to hire prevents both burnout and overspending.

### Startup Scaling Model

**Stage 0: Solo Founder (MVP)**
- 1 person: engineer + product + sales
- Works until: Revenue = $0–5k/mo
- Time until next hire: 6–12 months

**Stage 1: First Hire ($1k–10k MRR)**
- Add: Operations/Sales (1 person)
- Team: 2 people
- Founder now: Product + Engineering only
- Time until next hire: 3–6 months

**Stage 2: Product-Market Fit ($10k–50k MRR)**
- Add: Customer Success (1 person)
- Team: 3 people
- Founder: Product + strategic decisions
- Time until next hire: 2–3 months

**Stage 3: Scaling ($50k–200k MRR)**
- Add: DevOps/Infrastructure (1 person)
- Add: Sales (1 person)
- Team: 5 people
- Structure: Product, Engineering, Sales, Ops, CS

**Stage 4: Growth ($200k–1M MRR)**
- Add: Product Manager (1 person)
- Add: Senior Engineer (1 person)
- Add: Marketing (1 person)
- Team: 8–10 people

**Stage 5: Scale-Up ($1M+ MRR)**
- Add: Technical Leadership (CTO if founder not)
- Add: People Operations
- Add: Financial Operations
- Specialized teams per function

### Hiring Timeline vs Revenue

```
MRR Growth:     $0 → $5k → $25k → $100k → $500k → $1M+
Team Size:      1   → 2  → 5   → 10    → 20    → 50+
Time between hires: 6mo → 3mo → 2mo → 2mo → 1mo

Key insight: After PMF (Stage 2), hire ~1 person per $50k MRR gained
```

### Engineering Hiring Triggers

| Trigger | Action | Timing |
|---------|--------|--------|
| **Feature backlog > 3 sprints** | Hire engineer | Immediately |
| **Deployment takes >2 hours** | Hire DevOps | Within 1 month |
| **On-call fatigue** | Hire SRE | Within 2 weeks |
| **Velocity plateau** | Hire tech lead | Immediately |
| **Architectural problems** | Hire experienced architect | Immediately |

### Cost Per Team Role

| Role | Monthly Salary | Startup/Growth | Scale-Up | Enterprise |
|------|----------------|----------------|----------|-----------|
| **Software Engineer** | $6k–12k | $8k–10k | $10k–15k | $12k–20k |
| **DevOps/SRE** | $8k–15k | $10k–12k | $12k–18k | $15k–25k |
| **Product Manager** | $7k–13k | $9k–11k | $11k–16k | $13k–22k |
| **Customer Success** | $4k–8k | $5k–6k | $6k–10k | $8k–15k |
| **Sales** | $5k + 30% commission | $6k + 30% | $8k + 30% | $10k + 30% |
| **Ops/Finance** | $5k–10k | $6k–8k | $8k–12k | $10k–18k |

**All-in cost calculation:** Salary × 1.3 (benefits, tax, equipment)
Example: $8k engineer = $10.4k all-in cost

---

## SCALING INFRASTRUCTURE AT EACH STAGE

Infrastructure costs don't scale linearly with users.

### Infrastructure Scaling Factors

**MVP to Growing (100–1k users)**
- Database size: Linear growth (1 user ≈ 10KB data)
- CPU: Scales with concurrent users (1% CPU per 100 concurrent users)
- Cost per user: Decreases (shared infrastructure overhead)

**Growing to Scaling (1k–10k users)**
- Database size: Still linear
- CPU: Heavy spot (session management, caching)
- Database queries: Explosive growth (need caching)
- Cost per user: Continues to decrease

**Scaling to Enterprise (10k–100k+ users)**
- Database: Sharding required for sub-100ms latency
- Multi-region: Needed for global users
- Cost per user: Flattens (infrastructure overhead minimal)

### Infrastructure Cost Tracking

**Recommended:** Set up cost dashboards at Stage 1

```
Daily dashboard shows:
  - Database cost/day
  - Compute cost/day
  - Bandwidth cost/day
  - Total MRR
  - Cost per user (total cost / users)

Alert if: Cost per user increases (indicates efficiency problem)
```

**Real example: Stripe at different scales**
- MVP: $100/mo infrastructure
- 1k customers: $1k/mo
- 100k customers: $20k/mo
- 1M+ customers: $100k+/mo

Cost doesn't scale linearly because they optimize: caching, compression, hardware selection.

---

## REAL-WORLD SAAS PRICING MODELS & IMPLEMENTATION

Different pricing models require different technical architectures.

### Pricing Model Decision Tree

```
Are you selling to consumers (B2C)?
  YES → Freemium ($0 + upgrade to paid) or low flat rate
  NO  → Continue

Is your product usage highly variable?
  YES → Usage-based or hybrid (charge per action/compute/storage)
  NO  → Continue

Are you selling to teams/orgs?
  YES → Per-seat pricing ($X per user) or tiered
  NO  → Continue

Simple SaaS product?
  YES → Flat rate ($29/mo, $99/mo, $299/mo tiers)
  NO  → Custom pricing likely needed
```

### Common SaaS Pricing Implementations

**Flat Rate ($X/month):**
- Examples: Notion, Figma Pro, Linear Pro
- Implementation: Simple subscription in Stripe
- Effort: 2 days
- Revenue predictability: Highest (customers locked in)

**Per-Seat ($X per user/month):**
- Examples: Slack, Asana, Monday.com
- Implementation: Track active users, bill per count
- Effort: 1 week (seat counting logic)
- Revenue predictability: Medium (scales with team growth)

**Usage-Based ($ per action):**
- Examples: AWS, Twilio, SendGrid
- Implementation: Meter every action, batch billing
- Effort: 2–3 weeks (metering infrastructure)
- Revenue predictability: Low (highly variable)

**Freemium (Free tier + Paid upgrade):**
- Examples: Spotify, Slack, Zoom
- Implementation: Feature gating + upgrade trigger
- Effort: 2 weeks (feature flag infrastructure)
- Revenue predictability: Medium (% of free → paid)

### SaaS Pricing Mistakes to Avoid

| Mistake | Impact | Solution |
|---------|--------|----------|
| **Pricing too low** | Unsustainable unit economics | Raise before enterprise deals (they'll anchor expectations) |
| **Complex pricing structure** | Customer confusion, churn | Keep to 3 tiers max (Starter, Pro, Enterprise) |
| **Usage-based from start** | Operational complexity, unpredictable revenue | Start flat-rate, add usage later |
| **No trial period** | Lower conversion from free → paid | Offer 14-day free trial (best conversion rate) |
| **Annual-only pricing** | Excludes price-sensitive customers | Offer monthly + annual (annual = 2 months free) |
| **No annual discount** | Miss cash flow optimization | Annual = 20% discount vs monthly |

---

## SAAS OBSERVABILITY & KEY METRICS

### Business Metrics to Track

| Metric | Why | Formula | Tool |
|--------|-----|---------|------|
| **MRR** (Monthly Recurring Revenue) | Revenue health | Sum of all monthly subscriptions | Stripe, custom |
| **ARR** (Annual Recurring Revenue) | Growth indicator | MRR × 12 | Custom dashboard |
| **Churn Rate** | Product-market fit | (Customers lost / Start customers) × 100 | Custom |
| **LTV:CAC Ratio** | Profitability | Lifetime value / Customer acquisition cost | Custom |
| **Net Revenue Retention** | Expansion revenue | (Starting MRR + expansion - churn) / Starting MRR | Stripe analytics |
| **Trial-to-Paid Conversion** | Sales funnel health | (Paid signups / Free trial signups) × 100 | PostHog, Amplitude |
| **Payback Period** | Cash flow | CAC / Monthly margin | Custom |

### Technical Metrics to Track

| Metric | Why | Target | Tool |
|--------|-----|--------|------|
| **API Uptime** | Revenue impact | >99.9% | BetterStack, Sentry |
| **Page Load Time** | Conversion impact | <1 sec | WebVitals, Datadog |
| **Error Rate** | Product quality | <0.1% | Sentry, Datadog |
| **Database Latency (p95)** | User experience | <500ms | Datadog, CloudWatch |
| **Cost per 1M API calls** | Unit economics | <$10 (depends on infra) | CloudWatch, custom |

---

## SaaS Starter Kits (Skip the Boilerplate)

These open-source kits give you auth + billing + landing page out of the box:

| Kit | Stack | Auth | Payments | Cost |
|-----|-------|------|----------|------|
| **Next SaaS Starter** | Next.js + Postgres | Auth.js | Stripe | Free |
| **Payload + Stripe** | Payload CMS + Next.js | Payload Auth | Stripe | Free |
| **Supabase SaaS Starter** | Next.js + Supabase | Supabase Auth | Stripe | Free |
| **ShipFast** | Next.js + MongoDB | NextAuth | Stripe | $199 |
| **Supastarter** | Next.js/Nuxt + Supabase | Supabase Auth | Stripe/LS | $299 |

**Recommendation:** Start with a free starter kit. The $200–300 paid ones save maybe
a week of setup but lock you into their patterns.
