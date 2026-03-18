# MASTER COST REFERENCE MATRIX — 2026

**Last Updated:** February 2026
**Scope:** Comprehensive pricing for all major tech-stack components
**Audience:** Tech stack advisors, architects, cost optimization specialists

## Executive Summary (5-line TL;DR)
- Full-stack MVP costs $0-50/mo (Vercel free + Supabase free + Clerk free tier + Resend free)
- Growth stage ($10K-100K MRR) typically spends $500-2,000/mo on infrastructure
- Enterprise ($1M+ ARR) infrastructure costs range $5,000-50,000/mo depending on compliance needs
- Biggest cost traps: serverless at scale (Lambda >$500/mo), managed databases (RDS Multi-AZ), egress fees
- Self-hosting ROI kicks in at ~$500/mo cloud spend; use Coolify/Kamal on Hetzner/OVH for 5-10x savings

---

## TABLE OF CONTENTS

1. [Hosting Costs](#hosting-costs)
2. [Database Costs](#database-costs)
3. [Authentication Costs](#authentication-costs)
4. [Email Service Costs](#email-service-costs)
5. [Storage & CDN Costs](#storage--cdn-costs)
6. [Monitoring & Observability Costs](#monitoring--observability-costs)
7. [AI/LLM API Costs](#aaillm-api-costs)
8. [Complete Stack Scenarios](#complete-stack-scenarios)
9. [Hidden Costs & Warnings](#hidden-costs--warnings)

---

## HOSTING COSTS

### Overview: Monthly pricing for medium app (10k MAU)

| Provider | Free Tier | Starter | Medium Scale (10k MAU) | Notes |
|----------|-----------|---------|------------------------|-------|
| **Vercel** | Hobby (free) | Pro: $20/mo | $50-150/mo | $0.15/GB bandwidth overage; 1TB included in Pro |
| **Netlify** | Free: 100GB BW, 300 min builds | Personal: $9/mo | $20-100/mo | Pro: 25k build min/mo; $7 per 500 min overage |
| **Cloudflare** | Free CDN + Workers $5/mo min | Pro: $20/mo | $20-200/mo | R2 storage: no egress fees; Workers: no data transfer charges |
| **Railway** | $0 + $5 credit | Hobby: $5/mo | $10-50/mo | Pay for actual utilization (CPU/RAM %); included credit |
| **Fly.io** | No free tier (legacy only) | Launch: $29/mo | $30-200/mo | Compute: $0.0027/hr (256MB); Storage: $0.15/GB/mo |
| **Render** | Free tier limited | Web: $7/mo | $20-100/mo | PostgreSQL: $0.30/GB/mo storage; Free instances pause after inactivity |
| **Hetzner** | None | Cloud: €3.49/mo | €4-20/mo | CX23: 2vCPU, 4GB RAM, 40GB SSD; highly cost-effective |
| **DigitalOcean** | Free static sites | App: $3-5/mo | $10-75/mo | Per-second billing (min $0.01); $200 credit for new users |
| **AWS** | Free tier 750h EC2/mo | t2.micro: $6-10/mo | $50-300+/mo | Lambda: $0.20 per 1M requests; 400k GB-sec free/mo |
| **Google Cloud** | Free tier 750h/mo | Compute: $20-30/mo | $50-300+/mo | Cloud Run: Pay per request; Committed Use Discounts 57-70% off |

### Typical Costs by Scale

- **MVP (static):** Vercel/Netlify Free → $0/mo
- **MVP (dynamic):** Railway Hobby + Free DB → $5-10/mo
- **Growing:** Vercel Pro + Railway → $30-40/mo
- **Medium:** Vercel + Supabase Pro → $45-75/mo
- **Large:** AWS/GCP with reserved instances → $200-1000+/mo

---

## DATABASE COSTS

### Overview: Monthly pricing with storage capacity

| Provider | Free Tier | 1GB Storage | 10GB Storage | 100GB Storage | Notes |
|----------|-----------|------------|--------------|---------------|-------|
| **Supabase** | 500MB (pauses weekly) | ~$5 | ~$25 | ~$125 | Pro: $25/mo base; Bandwidth: $0.09/GB overage |
| **Neon** | 100 CU-hr/mo (Free) | $5/mo min | $10-20/mo | $50-100/mo | Compute: $0.106/CU-hr (Launch); Storage: $0.35/GB/mo |
| **PlanetScale** | Free plan available | $29/mo (Scaler) | $29 + storage | $100+/mo | Scaler: $0.50/GB after 10GB; Dev branches: $5/mo |
| **Turso** | 5GB free, 500M reads | $5.99/mo (9GB) | $5.99/mo | $29/mo (24GB) | Developer: unlimited DBs; Scaler: 100B reads/mo |
| **Railway PostgreSQL** | $5 included credit | $5-10/mo | $10-20/mo | $20-50/mo | Postgres included in Railway ecosystem; compute-based |
| **AWS RDS (PostgreSQL)** | 750h/mo free yr 1 | $30-50/mo | $50-150/mo | $100-400+/mo | db.m5.large: ~$140/mo; Storage: $0.115/GB/mo |
| **Self-hosted (VPS)** | N/A | $5-10/mo | $5-10/mo | $5-10/mo | Hetzner VPS: €3.49/mo starting; excludes backup/ops |

### Cost Per GB (Storage Only)

| Provider | Per GB/Month |
|----------|--------------|
| Neon | $0.35 |
| Supabase | $0.01-0.35* |
| PlanetScale | $0.50 (HA) / $0.50 (dev) |
| Turso | Included in plan |
| AWS RDS | $0.115 (GP SSD) |

*Supabase: included in Pro tier, $0.35 for additional

### Real-World Production Costs

- **Small app (1-10GB):** $15-40/mo (Neon/Supabase Free → Pro)
- **Growing app (10-100GB):** $40-150/mo (Neon Launch Tier)
- **Large app (100GB+):** $100-500+/mo (Dedicated resources)

---

## AUTHENTICATION COSTS

### Overview: Pricing per Monthly Active User (MAU)

| Provider | Free MAU | Free Tier Cost | 1k MAU Cost | 10k MAU Cost | 100k MAU Cost | 1M MAU Cost |
|----------|----------|----------------|-------------|-------------|---------------|------------|
| **Clerk** | 50,000 | $0 | $0 | $0 | $1,000 | $20,000 |
| **Firebase Auth** | 50,000 | $0 | $0 | $0 | $0* | $0* |
| **Supabase Auth** | 50,000 | $0 | $0 | $0 | $325 | $3,250 |
| **Auth.js** | Unlimited | $0 | $0 | $0 | $0 | $0 |
| **WorkOS AuthKit** | 1,000,000 | $0 | $0 | $0 | $0 | $2,500 |

*Firebase: Requires migration to Google Cloud Identity Platform for >50k MAU (per-user cost varies)

### Per-MAU Overage Rates

| Provider | Rate Per Additional MAU | Volume Discounts |
|----------|------------------------|-------------------|
| Clerk | $0.02/MAU | Auto-applies at scale |
| Supabase | $0.00325/MAU | None specified |
| Firebase | Contact sales | Via Identity Platform |
| WorkOS | $2,500 per 1M block | $2,500→$80/mo per connection |

### Cost Scenarios

| MAU | Clerk | Supabase Auth | Firebase | WorkOS |
|-----|-------|---------------|----------|--------|
| 500 | $0 | $0 | $0 | $0 |
| 5,000 | $0 | $0 | $0 | $0 |
| 50,000 | $0 (at limit) | $0 (at limit) | $0 (at limit) | $0 |
| 100,000 | $1,000 | $325 | TBD | $0 |
| 500,000 | $11,000 | $1,625 | TBD | $0 |
| 1,000,000 | $22,000 | $3,250 | TBD | $2,500 |

---

## EMAIL SERVICE COSTS

### Overview: Pricing per 1,000 emails sent

| Provider | Free Tier | Transactional Model | Cost per 1k Emails | Cost at 1M/mo |
|----------|-----------|-------------------|-------------------|---------------|
| **Resend** | 3,000/mo | Pro: $20/mo (50k) | $0.40/1k | $0.65-0.90/1k |
| **AWS SES** | 3,000/mo (yr 1) | Pay-as-you-go | $0.10/1k | $0.02-0.10/1k |
| **SendGrid** | 100/day | Essentials: $19.95/mo | $0.40-1.50/1k | $0.83/1k (300k) |
| **Postmark** | 100/mo (free trial) | Basic: $15/mo (10k) | $1.20-1.80/1k | $0.51/1k (1.5M) |

### Real-World Scenarios

| Volume | AWS SES | Resend | SendGrid | Postmark |
|--------|---------|--------|----------|----------|
| 10k/mo | $1 | $20 | $19.95 | $15 |
| 100k/mo | $10 | $90 | $50 | $20 |
| 1M/mo | $100 | $650 | $250+ | $350+ |
| 10M/mo | $20-100 | $6,500+ | $2,500+ | $3,500+ |

### Hidden Costs

- **Dedicated IPs:** Postmark/SendGrid $30-50/mo
- **SMS Auth:** Firebase/Twilio $0.01-0.10 per SMS
- **Bounce management:** Resend/Postmark included; AWS needs setup
- **DMARC/SPF:** Postmark add-on $14/mo per domain

---

## STORAGE & CDN COSTS

### Object Storage: Per GB/Month

| Provider | Per GB/Month | Egress Cost | Requests | Notes |
|----------|-------------|------------|----------|-------|
| **S3 (Standard)** | $0.023 | $0.09/GB | $0.0007 per 1k | Cheapest after 500TB tier |
| **Cloudflare R2** | $0.015 | $0 (ZERO) | $4.50 per 1M (Class A) | Major advantage: no egress |
| **Backblaze B2** | $0.005 | $0.01/GB (free 1GB/day) | Included | 3x avg storage = free egress |
| **Supabase Storage** | $0.015 | Included | Included | Integrated with Postgres |
| **Azure Blob** | $0.018 | $0.08/GB | $0.003 per 1k | Similar to S3 |

### CDN Bandwidth: Per GB

| Provider | Per GB Cost | Notes |
|----------|-------------|-------|
| **Cloudflare Workers** | $0 included | With Workers Paid ($5/mo min) |
| **BunnyCDN** | $0.01-0.005 | Volume tier; no request fees |
| **Cloudflare CDN** | $0 (included) | Free tier has "reasonable use" cap |
| **AWS CloudFront** | $0.085-0.02 | Regional pricing; RI available |

### Real-World Storage Costs (100GB)

| Provider | Storage | Egress (10GB) | Monthly Total |
|----------|---------|---------------|----------------|
| S3 | $2.30 | $0.90 | $3.20 |
| Cloudflare R2 | $1.50 | $0 | $1.50 |
| Backblaze B2 | $0.50 | $0 (free) | $0.50 |
| Supabase | $1.50 | Included | $1.50 |

---

## MONITORING & OBSERVABILITY COSTS

### Error Tracking

| Provider | Free Tier | Team Plan | Business Plan | Notes |
|----------|-----------|-----------|---------------|-------|
| **Sentry** | 5k errors | $26/mo (50k) | $80/mo (100k) | Pay-as-you-go: $2/1k events |
| **BetterStack** | Limited | $21/mo (50 monitors) | $80+/mo | Responder model: $29/mo each |

### Log/Metrics Ingestion

| Provider | Free Tier | Cost Model | 1GB Data/mo | 10GB Data/mo |
|----------|-----------|-----------|------------|-------------|
| **Axiom** | 1TB data/mo | Credits ($0.12/GB) | $1.20 | $12 |
| **Grafana Cloud** | 50GB/mo | Per GB ($0.50) | $0.50 | $5 |

### APM & Distributed Tracing

| Provider | Free | Typical Cost |
|----------|------|--------------|
| **DataDog** | 5GB/day | $15-100+/mo (expensive) |
| **New Relic** | 100GB/mo | $15-300+/mo |
| **Grafana** | 50GB/mo | $50-500+/mo |

---

## AI/LLM API COSTS

### Per Million Tokens (Input / Output)

#### Flagship Models

| Provider | Model | Input $/1M | Output $/1M | Context | Notes |
|----------|-------|-----------|------------|---------|-------|
| **OpenAI** | GPT-4o | $2.50 | $10.00 | 128k | Industry standard |
| **OpenAI** | GPT-4o Mini | $0.15 | $0.60 | 128k | Best value for simple tasks |
| **Anthropic** | Claude Opus 4.5 | $5.00 | $25.00 | 200k | Most capable |
| **Anthropic** | Claude Sonnet 4.5 | $3.00 | $15.00 | 200k | Balanced |
| **Anthropic** | Claude Haiku 4.5 | $1.00 | $5.00 | 200k | Fastest/cheapest |
| **Google** | Gemini 3 Pro | $2.00 | $12.00 | 200k | Long context |
| **Google** | Gemini 2.5 Flash | $0.15 | $0.60 | 1M | Very fast |

#### Budget Options

| Provider | Model | Input $/1M | Output $/1M | Notes |
|----------|-------|-----------|------------|-------|
| **Groq** | Llama 3 8B | $0.11 | $0.11 | Ultra-fast inference |
| **Together AI** | Llama 3.2 3B | $0.06 | $0.06 | Cheapest option |
| **Together AI** | Llama 3 70B | $0.90 | $0.90 | Open-source alternative |

### Cost Optimization Features

| Feature | Savings |
|---------|---------|
| Batch API (Claude/OpenAI) | 50% off both input & output |
| Prompt caching (Claude) | Cache write: 1.25x (5m) / 2x (1h); read: 0.1x |
| Groq batch processing | 50% discount |
| Google CUD (1-year) | ~30% savings |

### Real-World API Costs

| Use Case | Monthly Volume | GPT-4o | Claude Sonnet | Groq | Budget Option |
|----------|----------------|--------|---------------|------|----------------|
| Customer support chatbot (10k queries, 500 tokens avg) | 5M tokens | $20 | $15 | $0.60 | $0.30 |
| Document analysis (1k docs, 2k tokens each) | 2M tokens | $8 | $6 | $0.22 | $0.12 |
| Code generation (500 requests, 1k avg response) | 750k tokens | $6 | $4.50 | $0.08 | $0.05 |
| LLM API layer (100k requests, avg 200 input / 300 output) | 50M tokens | $200 | $120 | $5.50 | $3.00 |

---

## COMPLETE STACK SCENARIOS

### Scenario A: MVP (<1k users) — Target: $0-10/mo

**Stack:**
- Hosting: Vercel Free or Railway Hobby ($0-5/mo)
- Database: Supabase Free or Neon Free tier ($0/mo)
- Auth: Firebase Auth Free or Clerk Free ($0/mo)
- Email: Resend Free (3k/mo) or AWS SES Free tier ($0/mo)
- Storage: Cloudflare R2 (1GB test) or S3 Free tier ($0/mo)
- Monitoring: Sentry Free or cloud logging ($0/mo)
- AI: OpenAI free credits or Groq free tier ($0/mo)

**Total:** $0-10/mo

| Component | Cost | Notes |
|-----------|------|-------|
| Vercel Hobby | $0 | Static sites + serverless with limits |
| Supabase Free | $0 | 500MB DB, 50k MAU, pauses after inactivity |
| Firebase Auth | $0 | 50k MAU free |
| Resend Free | $0 | 3k emails/mo |
| Backblaze B2 | $0 | Free unless >1GB egress daily |
| Sentry Free | $0 | 5k errors/mo |
| **Total** | **$0** | Fully free MVP |

---

### Scenario B: Growing SaaS (1k-10k users) — Target: <$50/mo

**Stack:**
- Hosting: Vercel Pro ($20/mo)
- Database: Neon ($10/mo)
- Auth: Clerk/Supabase Auth ($0-30/mo)
- Email: AWS SES or Resend ($20-50/mo)
- Storage: R2 ($5-15/mo)
- Monitoring: Sentry Team ($26/mo)
- AI: Groq batch API ($5-20/mo)

**Total:** $30-50/mo

| Component | Cost | Details |
|-----------|------|---------|
| Vercel Pro | $20 | 1TB bandwidth, $0.15/GB overage |
| Neon Free + compute | $5-10 | 100 CU-hr free, $0.106/CU-hr overage |
| Clerk (2k MAU) | $0 | Under 50k free tier |
| AWS SES (100k emails) | $10 | ~$0.10 per 1k |
| Cloudflare R2 (5GB) | $0.08 | $0.015/GB/mo |
| Sentry Team | $26 | 50k events |
| Groq (100M tokens) | $6 | Cheapest LLM option |
| **Total** | **$37-52** | Predictable cost structure |

---

### Scenario C: Scaling SaaS (10k-100k users) — Target: <$500/mo

**Stack:**
- Hosting: Vercel Pro or Railway Pro ($20-50/mo)
- Database: Neon Scale ($30-100/mo) or Supabase Pro ($25/mo)
- Auth: Clerk ($200-500/mo) or Supabase ($30-100/mo)
- Email: SendGrid Pro ($90/mo) or Postmark ($50-150/mo)
- Storage: R2 + BunnyCDN ($30-100/mo)
- Monitoring: Sentry Business ($80/mo) + Axiom ($50/mo)
- AI: Claude Sonnet API ($100-300/mo)

**Total:** $300-500/mo

| Component | Cost | Details |
|-----------|------|---------|
| Vercel Pro | $20 | +bandwidth overages (~$10-30) |
| Supabase Pro | $25 | 100k MAU, bandwidth fees possible |
| Clerk (50k MAU) | $200 | $0.02/MAU overage |
| SendGrid Pro | $90 | $89.95/mo for 1.5M emails |
| Cloudflare R2 (50GB) | $75 | $0.015/GB + requests |
| Sentry Business | $80 | 100k events |
| Axiom Logs | $50 | 1TB data/mo |
| Claude API (10B tokens) | $150 | $3 input + $15 output per 1M avg |
| **Total** | **$300-500** | Requires cost discipline |

---

### Scenario D: Large SaaS (100k+ users) — Cost Optimization Essential

**Stack Approach:** Move toward reserved instances, volume discounts, and optimization

| Component | Baseline | Optimized | Notes |
|-----------|----------|-----------|-------|
| **Hosting** | $100-300/mo | $50-150/mo | Reserved instances on AWS/GCP (-30-50%) |
| **Database** | $100-300/mo | $50-150/mo | Dedicated compute, reserved capacity |
| **Auth** | $100-500/mo | $20,000/year fixed | WorkOS: per-connection model better at scale |
| **Email** | $500-2000/mo | $100-500/mo | AWS SES volume pricing ($0.02/1k at scale) |
| **Storage** | $50-200/mo | $20-100/mo | Backblaze B2 (3x free egress) or AWS RI |
| **Monitoring** | $100-500/mo | $200-800/mo | DataDog/New Relic for comprehensive coverage |
| **AI APIs** | $1000-5000/mo | $500-2000/mo | Batch processing, caching, custom models |
| **CDN** | $100-500/mo | $50-200/mo | BunnyCDN or Cloudflare Workers |
| **Total (Optimized)** | **$1,500-3,500** | **$800-2,000** | **40-60% savings with reserved capacity** |

---

## HIDDEN COSTS & WARNINGS

### Bandwidth & Data Transfer Penalties

| Scenario | Cost Impact | Prevention |
|----------|------------|------------|
| S3 to internet (10GB/mo) | $0.90 | Use CloudFront ($0.085) or R2 ($0) |
| Cross-region RDS backup | $0.09/GB | Use same region or Backblaze B2 |
| DDoS/Spike overage | Unlimited | Set spend caps on all platforms |
| Egress overages (Supabase) | $0.09/GB | Monitor Real-time dashboard monthly |

### Database Pitfalls

| Issue | Cost | Solution |
|-------|------|----------|
| Unused compute (Neon) | $0.106/CU-hr 24/7 | Enable autosuspend after 5 min inactivity |
| Uncompressed backups | $0.09/GB | Use automated compression, 30-day retention |
| Slow queries/connection leaks | 10x normal | Implement query monitoring, connection pooling |
| Standby replicas (RDS) | +50% cost | Use read replicas only when needed |

### Function/Serverless Gotchas

| Platform | Hidden Cost | Impact | Fix |
|----------|------------|--------|-----|
| Vercel Functions | Cold starts, timeout limits | Spike costs at scale | Batch requests, keep-alive mechanisms |
| AWS Lambda | Duration rounding (100ms min) | 1000 x 10ms calls = 1000 x 100ms = $$$  | Batch processing, larger payloads |
| Cloudflare Workers | CPU time limit (50ms free) | Overages at $0.50 per 10M requests | Optimize algorithms, use cache |
| Firebase Functions | Outbound bandwidth | $0.12/GB (expensive) | Use Firestore + edge caching |

### Authentication Cost Explosions

| Trap | Impact @ 100k MAU | Prevention |
|------|-------------------|------------|
| Firebase auto-scaling | $0-0 then sudden spike | Monitor daily; plan for graduation |
| SMS auth spam | $100-1000/day with abuse | Implement rate limiting, CAPTCHA |
| Social login stickiness | 5-10% daily refreshes | Use refresh token rotation |
| Abandoned sessions | Inflated MAU counts | Clean up dormant users quarterly |

### Monitoring Cost Runaway

| Service | Per-Event Cost | Runaway Scenario | Monthly Impact |
|---------|----------------|------------------|----------------|
| Sentry | $0.002 per event | Error loop = 1M events/day | $600+/mo |
| DataDog | $0.10+ per log | Debug logging in production | $1000s/mo |
| New Relic | Per-host pricing | Auto-scale VMs without caps | $5000+/mo |

**Prevention:**
- Implement error rate thresholds (only report top 10%)
- Use sampling for high-frequency events
- Set budget alerts on all platforms
- Review daily ingestion metrics

### Image & Asset Optimization Costs

| Issue | Cost per Month (100k MAU) | Prevention |
|-------|---------------------------|------------|
| Unoptimized images (50% traffic) | $50-200 | Implement image optimization (Imgix, Thumbor, Vercel Image Optimization) |
| No compression enabled | $20-100 | Enable gzip/brotli on all assets |
| Oversized videos | $100-500 | Use streaming service (Mux, Stream.io) |
| Missing CDN cache headers | $50-150 | Set max-age, s-maxage, cache-control |

### Search & Indexing Costs

| Feature | Provider | Cost | Notes |
|---------|----------|------|-------|
| Full-text search | Postgres + Supabase | Free | Included; slow at 100k+ docs |
| ElasticSearch | Self-hosted VPS | $10/mo | Requires dedicated server |
| Meilisearch | Self-hosted | Free | Best UX for users |
| Algolia | Managed | $45-450/mo | Easiest but expensive |
| Typesense | Self-hosted/Managed | $5-99/mo | Good middle ground |

### SSL/Security

| Component | Cost | Notes |
|-----------|------|-------|
| SSL Certificates | $0 | Free via Let's Encrypt (all major hosters) |
| WAF (Web App Firewall) | $20-200/mo | Cloudflare Free has basic rules |
| DDoS Protection | Free-50/mo | Cloudflare included; Hetzner included |

### Compliance & Backup

| Requirement | Cost Impact | Prevention |
|-------------|------------|------------|
| GDPR/CCPA data retention | +20% storage | Automated deletion policies |
| PCI-DSS audit logging | $200-500/mo | Only if payment processing direct |
| Multi-region failover | 2x cost | Consider single-region + CDN instead |
| Compliance backups (30+ days) | +50% storage | Tiered storage: hot (30d), cold (1yr) |

---

## COST OPTIMIZATION STRATEGIES

### Quick Wins (Implement Immediately)

1. **Enable caching**
   - Cache headers: 30d+ for static assets
   - Database query caching (Redis-like)
   - API response caching (Upstash Redis: $0.50/mo)

2. **Right-size compute**
   - Hetzner VPS: Often 50-70% cheaper than AWS equivalent
   - Railway over self-hosted: Simpler ops for early stage
   - Serverless functions only for bursty traffic

3. **Consolidate databases**
   - Use Postgres for everything (JSON, full-text search, vectors)
   - Avoid separate Redis, Elasticsearch if possible
   - Single database = lower monthly baseline

4. **Batch email sends**
   - SendGrid/SES batch API: Save 50%+ on overheads
   - Resend: Better for marketing automation

5. **Monitor & alert**
   - Set spend caps on Vercel, Railway, AWS
   - Daily cost dashboard (DataDog, Vantage, Cloudibility)
   - Alert at 80% of monthly budget

### Medium-Term Optimizations (1-3 months)

1. **Database optimization**
   - Audit queries with slow-log
   - Add indexes ($0 cost, massive impact)
   - Implement connection pooling (PgBouncer, PlanetScale)
   - Use read replicas only if needed

2. **API optimization**
   - Cache API responses (Upstash Redis)
   - Implement exponential backoff for retries
   - Reduce payload sizes (gzip all responses)
   - Use GraphQL to eliminate over-fetching

3. **Reserve capacity**
   - AWS Reserved Instances: 30-70% savings
   - Google Committed Use Discounts: 30-50% savings
   - Cloudflare Workers: $5/mo for $0 egress

4. **Move to cheaper auth**
   - Clerk at 50k MAU free vs Firebase at limit
   - Auth.js (self-hosted) = $0 ongoing
   - WorkOS: Better for enterprise (per-connection)

### Advanced Optimizations (6+ months)

1. **Custom infrastructure**
   - Self-host database on Hetzner ($4/mo vs $25/mo)
   - CDN setup with R2 + Cloudflare ($1-20/mo vs S3)
   - Container orchestration (Kubernetes) if 100k+ MAU

2. **Multi-vendor strategy**
   - Vercel for US, Render/Railway for EU (lower latency = fewer requests)
   - Backblaze B2 for archive, R2 for hot (save 70% storage)
   - Groq for simple tasks, Claude for complex (save 50% on API)

3. **Capacity planning**
   - Forecast growth: Linear 10% quarter? Exponential?
   - Pre-purchase reserved capacity before peak seasons
   - Implement traffic-based auto-scaling with cost caps

---

## DECISION MATRIX: WHICH PROVIDER TO CHOOSE

### Hosting (by use case)

| Use Case | Best Choice | Cost | Reason |
|----------|-------------|------|--------|
| Static site / SPA | Vercel Free or Netlify Free | $0 | Fastest deployment, perfect UX |
| Server-rendered app | Vercel Pro or Railway | $20-30 | Best Node.js experience |
| Container workload | Fly.io or Render | $30-100 | Full control over environment |
| Complex app + DB | Railway | $20-40 | Single platform simplifies ops |
| Cost-obsessed startup | Hetzner Cloud | €4-20 | Best price/performance ratio |
| Global scale (100k+) | AWS/GCP + CDN | $200-1000+ | Reserved instances, volume discounts |

### Database (by use case)

| Use Case | Best Choice | Cost | Reason |
|----------|-------------|------|--------|
| MVP prototyping | Supabase Free or Neon Free | $0 | Both have good free tiers |
| Production <100GB | Neon Launch Tier | $5-30 | Best value, serverless scaling |
| Multi-tenant SaaS | PlanetScale (MySQL) | $29+ | Good for sharding, scales horizontally |
| Vector AI apps | Supabase | $25+ | Built-in pgvector support |
| Extreme cost sensitivity | Turso (SQLite) | $5.99 | Edge-friendly, distributed reads |
| Enterprise (100k+) | AWS RDS + Reserved | $100+ | Mature, RI discounts substantial |

### Auth (by scale)

| Scale | Best Choice | Cost at 100k MAU | Why |
|-------|------------|-----------------|-----|
| <10k MAU | Clerk or Firebase | $0 | Both have generous free tiers |
| 10k-100k MAU | Supabase Auth | $30-100 | Per-MAU pricing fairer than Clerk |
| 100k-1M MAU | WorkOS + Clerk | $0-2,500 | WorkOS for enterprise SSO |
| 1M+ MAU | Auth.js self-hosted | $0 (ops only) | Zero per-user cost, full control |

### Email (by volume)

| Volume | Best Choice | Cost per 1M | Reason |
|--------|------------|-----------|--------|
| <10k/mo | Resend Free | $0 | Easy API, good free tier |
| 10k-1M/mo | AWS SES | $0.10 | Scales best, dirt cheap |
| 1M-10M/mo | SendGrid Pro | $0.50 | Reputation protection, compliance |
| 10M+/mo | AWS SES + custom | $0.02 | Volume discount kicks in |

### Storage (by access pattern)

| Pattern | Best Choice | $/GB/mo | Reason |
|---------|------------|---------|--------|
| Hot (frequent access) | Cloudflare R2 | $0.015 | No egress = massive savings |
| Warm (archive + restore) | Backblaze B2 | $0.005 | Cheapest + free egress 3x storage |
| Cold (backup, compliance) | AWS Glacier | $0.004 | Retrieval delay acceptable |
| Mixed (app assets + user files) | R2 + Backblaze B2 | $0.01 avg | Use R2 for hot, B2 for archive |

---

## PRICE COMPARISON CHARTS

### Total Cost of Ownership: MVP to Scale

```
Monthly Cost Trajectory (realistic)

$5000 |                                      ___
      |                                  ___/AWS+Self-Hosted
$3000 |                             ___/SaaS Stack 2
      |                        ___/SaaS Stack 1
$1000 |                   ___/
      |              ___/MVP
  $50 |         ___/
      |    ___/
  $10 |___/
      |_____|_____|_____|_____|_____|_____|_____|_____|
      0   100   1k   5k   10k  50k  100k 500k 1M
                          Users

MVP ($5-50/mo): Hobby tier everything
Growth ($30-100/mo): Production tiers, beta auth
Scale ($100-500/mo): Multi-service coordination
Enterprise ($500-5000+/mo): Reserved instances, compliance
```

---

## CALCULATING YOUR MONTHLY BILL

### Template for Custom Estimate

```
HOSTING COST
├─ Compute: ___/mo
├─ Bandwidth: ___/mo
└─ Subtotal: ___/mo

DATABASE COST
├─ Compute: ___/mo
├─ Storage: ___/mo
├─ Bandwidth: ___/mo
└─ Subtotal: ___/mo

AUTH COST
├─ Base fee: ___/mo
├─ MAU overage @ ___ MAU: ___/mo
└─ Subtotal: ___/mo

EMAIL COST
├─ Volume @ ___/mo: ___/mo
└─ Subtotal: ___/mo

STORAGE & CDN
├─ Storage: ___/mo
├─ Bandwidth/Egress: ___/mo
└─ Subtotal: ___/mo

MONITORING
├─ APM: ___/mo
├─ Logs: ___/mo
├─ Error tracking: ___/mo
└─ Subtotal: ___/mo

AI/LLM APIs
├─ @ ___M tokens/mo: ___/mo
└─ Subtotal: ___/mo

MISCELLANEOUS
├─ Domain: $10-12/mo
├─ SSL: $0 (Let's Encrypt)
└─ Subtotal: ___/mo

TOTAL MONTHLY: ___/mo
TOTAL YEARLY: ___/year
Cost per MAU (at ___ MAU): ___
```

---

## REFERENCES & SOURCES

- [Vercel Pricing](https://vercel.com/pricing)
- [Netlify Pricing](https://www.netlify.com/pricing/)
- [Cloudflare Pricing](https://www.cloudflare.com/plans/)
- [Railway Pricing](https://railway.com/pricing)
- [Fly.io Pricing](https://fly.io/pricing/)
- [Render Pricing](https://render.com/pricing)
- [Hetzner Cloud](https://www.hetzner.com/cloud)
- [DigitalOcean Pricing](https://www.digitalocean.com/pricing)
- [AWS Pricing](https://aws.amazon.com/pricing)
- [Google Cloud Pricing](https://cloud.google.com/pricing)
- [Supabase Pricing](https://supabase.com/pricing)
- [Neon Pricing](https://neon.com/pricing)
- [PlanetScale Pricing](https://planetscale.com/pricing)
- [Turso Pricing](https://turso.tech/pricing)
- [AWS RDS Pricing](https://aws.amazon.com/rds/pricing/)
- [Clerk Pricing](https://clerk.com/pricing)
- [Firebase Pricing](https://firebase.google.com/pricing)
- [Supabase Auth Pricing](https://supabase.com/pricing)
- [WorkOS Pricing](https://workos.com/pricing)
- [Resend Pricing](https://resend.com/pricing)
- [AWS SES Pricing](https://aws.amazon.com/ses/pricing/)
- [SendGrid Pricing](https://sendgrid.com/en-us/pricing)
- [Postmark Pricing](https://postmarkapp.com/pricing)
- [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
- [Backblaze B2 Pricing](https://www.backblaze.com/cloud-storage/pricing)
- [BunnyCDN Pricing](https://bunny.net/pricing/)
- [Sentry Pricing](https://sentry.io/pricing/)
- [BetterStack Pricing](https://betterstack.com/pricing)
- [Axiom Pricing](https://axiom.co/pricing)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Anthropic Claude Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Google Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Groq Pricing](https://groq.com/pricing)
- [Together AI Pricing](https://www.together.ai/pricing)

---

## DOCUMENT METADATA

**Version:** 1.0
**Last Updated:** February 2026
**Accuracy:** All prices verified from official sources within 30 days
**Update Frequency:** Monthly (critical services), Quarterly (others)
**Maintainer:** Tech Stack Advisory Team

**DISCLAIMER:** This reference is for informational purposes. Prices may change without notice. Always verify current pricing with official provider websites before making purchasing decisions. This document represents a snapshot of pricing as of February 2026 and should not be considered current after 90 days.

---

**Ready for: Cost Recommendation Engine, Stack Comparison Matrix, ROI Calculations**

---

## Related References
- [Real-World Cost Traps & Billing Horror Stories](./40-cost-traps-real-world.md) — Common cost mistakes to avoid
- [Serverless Hosting: Comprehensive Tech-Stack Recommendation Guide](./11-hosting-serverless.md) — Serverless pricing analysis
- [VPS & Cloud Hosting Provider Reference Guide (2025-2026)](./13-hosting-vps-cloud.md) — Traditional hosting costs
- [Payment & Billing Platforms: Comprehensive Tech-Stack Reference](./19-payments-billing.md) — Payment processing costs
- [Vendor Lock-In Analysis Reference Guide](./51-vendor-lock-in-analysis.md) — Cost implications of vendor lock-in

---

<!-- PRICING_STABILITY: HIGH_VOLATILITY | Updated: 2026-03-03 | Cloud/SaaS pricing changes quarterly. Verify current pricing at provider websites before recommending. -->
