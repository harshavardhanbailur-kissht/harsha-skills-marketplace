# Migration Paths: When & How to Switch Stacks

## Executive Summary

Tech stack migrations are expensive, risky, and often unavoidable. The key is knowing when they're worth the cost.

**Critical Statistics:**
- Most common migrations: Firebase→Supabase, Heroku→Railway, Vercel→self-hosted, MongoDB→PostgreSQL
- Cost savings from successful migrations: 70-95% in many cases
- Failure rate: 15-25% of migrations fail or partially succeed
- Average timeline: 3-9 months for medium-sized applications
- Hidden costs: 20-40% more engineering time than initial estimates

**The Golden Rule:**
Don't migrate unless the business case justifies it. A working system is a working system. Cost savings alone rarely justify the disruption unless they exceed 40-60% annually and the organization has capacity to absorb risk.

---

## Top 10 Migration Paths

### 1. Firebase → Supabase

**Why Teams Migrate:**
- Firebase costs 3-10x more at scale (authentication, storage, functions)
- Vendor lock-in concerns
- Need for SQL database control
- Better performance requirements than Realtime Database
- Data sovereignty/GDPR requirements

**Step-by-Step Strategy:**

1. **Audit Phase (Week 1-2)**
   - Identify all Firebase services in use (Auth, Firestore, Storage, Functions, Hosting)
   - Document data schema and volumes
   - List all custom rules and security configurations
   - Measure current costs at `firebase.google.com/pricing`

2. **Parallel Setup (Week 2-3)**
   - Create Supabase project in target region
   - Set up PostgreSQL schema (replicate Firestore structure)
   - Configure authentication (migrate from Firebase Auth)
   - Set up storage buckets with same naming scheme

3. **Data Migration (Week 3-5)**
   - Export Firestore data as JSON using Firebase CLI
   - Transform JSON to PostgreSQL format (most complex step)
   - Use Supabase's pgloader or custom scripts
   - Validate data integrity with sampling (1-5% row spot checks)

4. **Application Changes (Week 4-6)**
   - Replace Firebase SDK with `@supabase/supabase-js`
   - Update authentication logic
   - Rewrite queries from Firestore syntax to PostgreSQL
   - Update storage references (usually 1:1 compatible)

5. **Testing & Validation (Week 6-7)**
   - Test in staging environment with production-like data
   - Performance benchmarking (especially queries)
   - Security testing (RLS policies)
   - User acceptance testing

6. **Cutover (Week 7-8)**
   - Enable dual-write (write to both Firebase and Supabase)
   - Monitor for data consistency issues
   - Switch read traffic gradually using feature flags
   - Keep Firebase running for 2-4 weeks as rollback

**Cost Savings:**
- Firebase at $10K/month → Supabase at $1-2K/month = 80-90% savings
- Typical ROI: 6-12 months
- Additional savings from self-managed infrastructure: 30-50%

**Common Gotchas:**
- Firebase Realtime Database has no direct Supabase equivalent (migrate to Supabase Realtime with limitations)
- Firestore's document-oriented queries don't map 1:1 to SQL
- Firebase storage paths may conflict with Supabase bucket naming
- Security rules syntax is completely different (Firebase → PostgreSQL RLS)
- Timezone handling in timestamps causes silent data corruption

**Timeline:** 6-8 weeks for small-to-medium app | 12-16 weeks for large applications

---

### 2. Heroku → Railway

**Why Teams Migrate:**
- Heroku cost 4-8x higher than alternatives
- Heroku "sunsetting" free tier and dyno hours
- Better performance on equivalent spec
- Railway's pricing more transparent and predictable
- Container-native approach gives more control

**Step-by-Step Strategy:**

1. **Pre-Migration Assessment (Day 1-2)**
   - Export Heroku dynos configuration
   - Document all add-ons in use (database, cache, monitoring)
   - List environment variables
   - Check buildpack requirements
   - Audit database size and growth rate

2. **Database Migration (Day 2-4)**
   - Use Heroku's built-in backup tools
   - Download database dump (`heroku pg:backups:download`)
   - Create Railway PostgreSQL service
   - Restore dump to Railway database
   - Verify data integrity with queries

3. **Application Setup (Day 4-6)**
   - Create Railway project and link GitHub repo
   - Railway auto-detects buildpack from Procfile
   - Configure environment variables in Railway dashboard
   - Set up custom domains and SSL
   - Configure any Redis/cache services needed

4. **Zero-Downtime Cutover (Day 6-7)**
   - Update database connection string (but don't deploy yet)
   - Deploy to Railway in parallel (don't touch DNS)
   - Run smoke tests on Railway environment
   - Switch DNS pointer to Railway IP
   - Monitor error logs for 24 hours
   - Keep Heroku running 1 week for rollback

5. **Post-Migration (Day 7-14)**
   - Monitor Railway dashboard for CPU/memory patterns
   - Adjust dyno equivalents if needed
   - Cancel Heroku project after 2 weeks
   - Implement cost monitoring alerts

**Cost Savings:**
- Heroku Standard dyno ($25/month) + database ($9+/month) = ~$60+/month
- Railway equivalent (0.5 vCPU + database) = $10-15/month
- Savings: 70-90% depending on configuration
- Typical ROI: 1-2 months

**Common Gotchas:**
- Heroku's auto-scaling doesn't have Railway equivalent (use separate autoscaling service)
- Buildpack differences may cause build failures
- Environment variable migration is manual (no automated sync)
- Worker dynos need to be manually configured as separate services
- Cold start times may differ significantly
- File system differences (Heroku ephemeral → need persistent volumes)

**Timeline:** 1-2 weeks for typical applications | 3-4 weeks for complex deployments

---

### 3. Vercel → Coolify/Hetzner

**Why Teams Migrate:**
- Vercel costs 5-10x more at scale (per-request and compute)
- Need for more control over infrastructure
- Better performance from dedicated servers
- Private deployment (no Vercel data collection)
- Compliance/data residency requirements

**Step-by-Step Strategy:**

1. **Assessment (Day 1)**
   - Audit current Next.js/frontend tech
   - Measure Vercel monthly costs
   - Document environment variables and secrets
   - Check for Vercel-specific dependencies (OG image generation, etc.)

2. **Infrastructure Setup (Day 2-3)**
   - Rent Hetzner VPS (minimum 4GB RAM for Next.js)
   - Install Docker and docker-compose
   - Set up Coolify dashboard on server
   - Configure domain DNS pointing (keep TTL low)
   - Set up SSL certificates (Coolify handles auto-renewal)

3. **Application Preparation (Day 3-4)**
   - Add custom Docker build for Next.js app
   - Set up environment variables in Coolify
   - Configure database service if needed
   - Set up file persistence for uploads

4. **Deployment (Day 4-5)**
   - Push application to GitHub/GitLab
   - Connect repository to Coolify project
   - Deploy staging version first
   - Run load tests to verify performance
   - Switch production traffic with DNS failover

5. **Post-Migration (Day 5-7)**
   - Monitor resource usage and auto-scale settings
   - Set up error tracking and alerting
   - Optimize build times (may be 2-3x slower than Vercel)
   - Configure backup strategy

**Cost Savings:**
- Vercel at high scale: $500-2000+/month
- Hetzner + Coolify equivalent: $30-100/month
- Savings: 85-95%
- One-time setup cost: 8-40 engineering hours

**Common Gotchas:**
- Cold starts on Hetzner are 5-10 seconds (vs Vercel's <100ms)
- Deployment time increases 3-5x (Hetzner builder slower than Vercel)
- No built-in analytics dashboard (integrate third-party)
- ISP blocking concerns if using residential IP
- Coolify complexity learning curve (2-3 weeks)
- OG image generation requires headless browser (add 500MB to image)

**Timeline:** 1 week for simple Next.js sites | 3-4 weeks for complex setups with multiple services

---

### 4. MongoDB → PostgreSQL

**Why Teams Migrate:**
- MongoDB costs 2-4x more for same performance
- SQL queries offer better optimization control
- JSON support in PostgreSQL (JSONB) handles flexible schemas
- Better ACID guarantees and data integrity
- PostgreSQL ecosystem more mature (better tooling)
- Regulatory requirements demand relational structure

**Step-by-Step Strategy:**

1. **Schema Design (Week 1-2)**
   - Analyze MongoDB collections structure
   - Design relational schema (denormalize strategically)
   - Map document arrays to junction tables
   - Plan JSONB columns for flexible data
   - Create migration mapping document

2. **Data Transformation (Week 2-3)**
   - Write ETL script using Mongo → PostgreSQL adapters
   - Use tools: `mongo-to-postgres` npm package or Airbyte
   - Handle nested documents and arrays
   - Test with 10% of production data
   - Validate row counts and data samples

3. **Migration Execution (Week 3-4)**
   - Export MongoDB as BSON/JSON backup
   - Transform data using transformation script
   - Load into PostgreSQL staging
   - Perform full data validation (checksums, counts, samples)
   - Test application with new schema

4. **Application Updates (Week 4-6)**
   - Replace MongoDB driver (`mongoose`) with PostgreSQL client (`pg` or ORM)
   - Rewrite queries (collection operations → SQL SELECT/JOIN/INSERT)
   - Update indexes from MongoDB indexes to PostgreSQL B-tree indexes
   - Test migration with production data volume

5. **Testing & Cutover (Week 6-7)**
   - Load testing to find slow queries
   - Optimize queries with EXPLAIN ANALYZE
   - Run feature testing against new database
   - Implement feature flag for dual-write pattern
   - Cutover during low-traffic window

**Cost Savings:**
- MongoDB Atlas at scale (clusters): $500-2000+/month
- PostgreSQL (RDS or self-hosted): $100-500/month
- Savings: 50-75% (less dramatic than other migrations)
- ROI timeline: 6-12 months

**Common Gotchas:**
- Array queries (`$elemMatch`, `$in`) need LATERAL joins or unnest
- Denormalization becomes necessary for performance (violates normalization)
- Transaction semantics differ (PostgreSQL is stricter)
- ObjectID generation requires different logic (use UUID or sequences)
- Large documents need JSONB strategy (mixing relational + JSON)
- Aggregation pipeline syntax incompatible with PostgreSQL (rewrite entire pipeline)
- Query performance may degrade initially (requires index tuning)

**Timeline:** 4-7 weeks for small-medium apps | 8-12 weeks for complex schemas

---

### 5. AWS → Hetzner/DigitalOcean

**Why Teams Migrate:**
- AWS cost opaque and runs 5-10x higher at scale
- Hetzner/DO pricing transparent and 80-90% cheaper
- AWS lock-in with proprietary services (Lambda, DynamoDB, S3)
- Simpler infrastructure requirements (VPS sufficient)
- Data residency in EU (Hetzner) for compliance

**Step-by-Step Strategy:**

1. **AWS Audit (Week 1)**
   - Export all IAM policies and roles
   - Document all services in use (EC2, RDS, S3, Lambda, SQS, etc.)
   - Calculate true AWS costs using AWS Cost Explorer
   - Identify candidates for migration (keep managed services if beneficial)
   - Create inventory of security groups and networking

2. **Infrastructure Planning (Week 1-2)**
   - Map AWS services to DigitalOcean/Hetzner equivalents:
     - EC2 → Droplet
     - RDS → Managed Database or self-hosted
     - S3 → Spaces or MinIO
     - Lambda → Docker container
     - SQS → Redis Queue or self-hosted
   - Design networking topology
   - Plan for disaster recovery

3. **Migration Execution (Week 2-5)**
   - Provision DigitalOcean/Hetzner infrastructure
   - Migrate databases using backup/restore
   - Copy S3 data to Spaces/MinIO (use `rclone` for massive volumes)
   - Containerize Lambda functions
   - Migrate DNS to new provider

4. **Application Changes (Week 5-6)**
   - Update S3 SDK calls to DigitalOcean Spaces API (usually compatible)
   - Replace Lambda with container tasks (Kubernetes or systemd)
   - Update database connection strings
   - Replace SQS with Redis or self-hosted queue
   - Test all integrations

5. **Testing & Failover (Week 6-7)**
   - Load testing new infrastructure
   - Failover testing to verify redundancy
   - Gradual traffic switching (using load balancer)
   - Monitor for 1-2 weeks before full cutoff

**Cost Savings:**
- AWS with multi-service architecture: $2000-10000+/month
- Hetzner equivalent: $200-500/month
- Savings: 80-95%
- One-time migration cost: 40-120 engineering hours

**Common Gotchas:**
- S3 API compatibility isn't perfect (cross-region replication doesn't exist in Spaces)
- Lambda serverless benefits lost (need to manage containers)
- AWS CloudFormation not transferable
- Multi-region failover more complex on DigitalOcean
- No managed message queue (DIY with RabbitMQ or Redis)
- Security groups need manual translation to firewall rules
- Data transfer costs from AWS egress can be expensive (plan data download in advance)

**Timeline:** 4-8 weeks for moderate complexity | 8-16 weeks for highly distributed systems

---

### 6. Auth0 → Clerk or Self-Hosted

**Why Teams Migrate:**
- Auth0 pricing: $0 (free tier) → $15K+/year (enterprise)
- Clerk pricing: flat $25-99/month regardless of users
- Self-hosted: one-time setup cost, zero per-user cost
- Privacy concerns (Auth0 data processing)
- Feature limitations at certain tiers

**Step-by-Step Strategy:**

1. **Audit Current Setup (Day 1)**
   - Document all Auth0 actions and rules
   - List all integrations (social providers, MFA, etc.)
   - Export user database if possible
   - Check custom database connections

2. **Choose Destination (Day 1-2)**
   - Clerk: fastest path, minimal changes (OAuth-compatible)
   - Self-hosted: use Keycloak, Authentik, or Ory Hydra
   - Evaluate: user count, feature needs, compliance requirements

3. **For Clerk Migration (Day 2-5)**
   - Create Clerk project
   - Update SDK import statements (minimal changes)
   - Migrate user data using Clerk's import API
   - Test OAuth flows with social providers
   - Update environment variables
   - Deploy and verify

4. **For Self-Hosted Migration (Week 1-3)**
   - Deploy Keycloak/Authentik on VPS
   - Configure providers and scopes
   - Migrate user database and attributes
   - Update application to use new OAuth endpoint
   - Test social login integrations
   - Set up monitoring and backups

5. **Cutover (Day 5-6 for Clerk, Week 3-4 for self-hosted)**
   - Dual-run during overlap period
   - Switch new user signups to new provider
   - Gradual migration of existing users
   - Monitor for 2 weeks

**Cost Savings:**
- Auth0 at 100K users: $15K-30K+/year
- Clerk at 100K users: $300-1200/year = 91-95% savings
- Self-hosted: $100-300/year (hosting) + 40 hours setup = breaks even in 6-12 months
- Clerk ROI: immediate

**Common Gotchas:**
- Clerk doesn't support all Auth0 advanced features (check feature parity)
- User data export from Auth0 is limited (custom attributes may need manual mapping)
- Self-hosted requires DevOps knowledge (Keycloak is complex)
- Social provider configuration differs across platforms
- Session management token formats differ
- JWT claims structure varies (rewrite validation logic)
- Custom flows/rules need to be rewritten using new platform's scripting

**Timeline:** 1-2 weeks for Clerk | 3-5 weeks for self-hosted Keycloak

---

### 7. Next.js → Astro (for Content Sites)

**Why Teams Migrate:**
- Astro ships zero JavaScript by default (massive performance gain)
- Astro is 10-50x faster for static/semi-static sites
- Next.js over-engineered for content-heavy sites
- Reduced hosting costs (static files only)
- Simpler mental model (islands architecture)

**Step-by-Step Strategy:**

1. **Assessment (Day 1)**
   - Analyze Next.js pages (which are truly static vs. interactive)
   - Count client-side interactive components
   - Measure current Core Web Vitals
   - Determine if migration is justified (is site >50% static?)

2. **Project Setup (Day 1-2)**
   - Create new Astro project
   - Set up same styling system (Tailwind, CSS Modules, etc.)
   - Configure integrations (React for islands, MDX for markdown)

3. **Page Migration (Week 1-2)**
   - Convert static pages to `.astro` files
   - Move layouts and components
   - Migrate markdown content to Astro's `content/` directory
   - Update image optimization (use Astro Image component)

4. **Component Migration (Week 2-3)**
   - Identify components that need interactivity (use React islands)
   - Convert pure-presentation components to Astro components
   - Configure client: directives (`client:load`, `client:idle`, etc.)
   - Test interactive features

5. **Testing & Optimization (Week 3-4)**
   - Test all pages and forms
   - Optimize images (Astro has built-in optimization)
   - Run Lighthouse audits
   - Test mobile responsiveness

**Performance Gains:**
- Typical improvement: Core Web Vitals 50-80% better
- Page load time: 60-80% faster
- Hosting costs: 70-90% lower (static files vs. serverless)

**Common Gotchas:**
- Astro components can't share state without JavaScript (use Context API or props)
- Data fetching timing is different (at build time, not request time)
- Client-side routing requires re-architecture
- Form submissions need API endpoints (use Astro API routes)
- Dynamic pages need revalidation strategy (ISR equivalent)
- React component hydration mismatch errors common
- SEO setup requires careful meta tag handling

**Timeline:** 2-4 weeks for content-heavy sites | 4-6 weeks for sites with significant interactivity

---

### 8. Monolith → Microservices (When Necessary)

**Only migrate if you have EXPLICIT problems:**
- Single service causes cascading failures
- Different parts scale at wildly different rates
- Teams stepping on each other's code (4+ teams)
- Technology requirements diverge significantly

**Why Most Migrations Fail:**
Microservices introduce 10x complexity: distributed transactions, network latency, debugging nightmare, deployment overhead. Only justified if monolith is genuinely constraining growth.

**Step-by-Step Strategy:**

1. **Strangler Fig Pattern (Month 1-2)**
   - Identify first service candidate (usually user service or auth)
   - Extract service with API facade
   - Keep monolith calling new service
   - Don't delete monolith until all services extracted

2. **Service Extraction (Month 2-6)**
   - Extract one service per month maximum
   - Each service: own database, own deployment
   - Use async messaging (RabbitMQ, Kafka) for cross-service communication
   - Define clear API contracts

3. **Infrastructure (Month 1-3)**
   - Set up Kubernetes (if scaling demands it) or Docker Compose
   - Implement service discovery
   - Set up centralized logging (ELK stack)
   - Implement distributed tracing (Jaeger)
   - Set up monitoring and alerting

4. **Testing Strategy (Ongoing)**
   - Contract testing between services
   - Chaos engineering to test failure modes
   - Integration testing (expensive, minimize)
   - Load testing each service independently

**Cost Implications:**
- Infrastructure costs: +30-100% (more VMs, monitoring, complexity)
- Engineering costs: +200-400% (debugging, coordination, deployment)
- Time to market: -30% (parallel development)
- Only justified at >50 engineers or extreme scaling needs

**Common Gotchas:**
- Distributed transaction nightmare (saga pattern, compensating transactions)
- Cross-service debugging is 10x harder
- Network latency adds 50-200ms per call (vs in-process: 1ms)
- Deployment coordination complexity (service A requires service B version)
- Testing matrix explosion (n services = exponential test combinations)
- Data consistency issues (eventual consistency headaches)

**Timeline:** 6-18 months for proper extraction | 2-3 years for fully distributed culture

---

### 9. Stripe → LemonSqueezy/Paddle (for SaaS)

**Why Teams Migrate:**
- Stripe takes 2.9% + $0.30 (payment + fees)
- LemonSqueezy/Paddle all-in: 8-10% (includes payment processing, tax, compliance)
- LemonSqueezy/Paddle handles tax compliance (EU VAT, etc.) automatically
- Better for product licensing and software distribution
- Simpler dashboard and reporting

**Step-by-Step Strategy:**

1. **Pre-Migration Analysis (Day 1)**
   - Calculate Stripe costs (take-rate analysis)
   - Model LemonSqueezy costs at your volume
   - Analyze tax compliance overhead (is someone spending 10 hours/month on this?)
   - Export Stripe customer and payment data

2. **Account Setup (Day 1-2)**
   - Create LemonSqueezy/Paddle account
   - Configure products/pricing
   - Set up API keys and webhooks
   - Test payment flows in staging

3. **Webhook Migration (Day 2-3)**
   - Map Stripe webhook events to LemonSqueezy events
   - Update webhook handlers (event structure differs)
   - Test webhook delivery and retry logic
   - Validate signature verification

4. **SDK/API Update (Day 3-4)**
   - Replace Stripe.js with LemonSqueezy SDK
   - Update checkout flow (LemonSqueezy embeds, not redirect)
   - Update subscription management API calls
   - Test pause/resume/cancel flows

5. **Data Migration (Day 4-5)**
   - Migrate existing customers and subscriptions
   - Backfill historical invoices and payments
   - Verify payment records match
   - Test reporting accuracy

6. **Cutover (Day 5-6)**
   - New customers on LemonSqueezy
   - Existing customers migrated over 2-4 weeks
   - Parallel run for 1 month (keep Stripe active)
   - Monitor payment success rates

**Cost Savings:**
- Stripe at $10K/month: $290/month take-rate
- LemonSqueezy at $10K/month: $800/month all-in
- Net: might be slightly more expensive, but includes:
  - Automatic VAT compliance (worth $2K-5K/year in professional services)
  - Affiliate management (no separate tool needed)
  - Product licensing (no integration needed)
  - Better product-focused dashboard

**Common Gotchas:**
- LemonSqueezy doesn't support ACH transfers (US-only, limited payment methods)
- Paddle/LemonSqueezy webhook delivery less reliable than Stripe
- Limited customization compared to Stripe
- Dunning (failed payment retry) less sophisticated
- No equivalent to Stripe Radar for fraud detection
- Customer portal less powerful
- Reporting and analytics less granular

**Timeline:** 1-2 weeks for straightforward implementation

---

### 10. Self-Hosted → Managed (When Scaling Demands It)

**Why Teams Migrate:**
- Operational burden exceeds engineering capacity
- Database scaling requires expert knowledge
- Downtime costs exceed managed service cost (usually after $50K ARR)
- Security compliance requirements demand managed service
- Team size <5 people (can't do on-call rotations)

**Step-by-Step Strategy:**

1. **Capacity Planning (Week 1)**
   - Measure current database/infrastructure load
   - Project growth 12-24 months
   - Model managed service costs vs. current hosting
   - Define SLA requirements (99.5%? 99.9%?)

2. **Service Selection (Week 1-2)**
   - Compare managed providers (AWS RDS, Heroku Postgres, etc.)
   - Consider: performance, compliance, failover strategy
   - Evaluate pricing at 2x and 5x current scale

3. **Parallel Infrastructure (Week 2-4)**
   - Provision managed services (database, hosting, caching)
   - Set up connection pooling
   - Configure automated backups
   - Test disaster recovery procedure

4. **Migration (Week 4-5)**
   - Backup self-hosted database
   - Restore to managed service
   - Update connection strings
   - Test application with managed database
   - Run load tests

5. **Cutover (Week 5-6)**
   - Switch application to managed database
   - Monitor for 1-2 weeks
   - Decommission self-hosted infrastructure

**Cost Implications:**
- Self-hosted costs: $100-500/month (VPS) + 10-20 hours/month ops
- Managed service: $300-2000/month (depending on scale)
- Breakeven point: when ops burden = managed service cost (usually $50K+ ARR)
- Value gained: 99.9% uptime SLA, automated backups, scaling

**Common Gotchas:**
- Managed services slower to scale (provision time)
- Connection pooling required (self-hosted didn't need it)
- Less configuration control (can't tune kernel parameters)
- Vendor lock-in increases as you adopt more managed services
- Failover times longer with managed services (typically 30-120 seconds)

**Timeline:** 2-4 weeks for database migration

---

## Zero-Downtime Migration Patterns

### Pattern 1: Dual-Write with Feature Flags

**How It Works:**
```
1. Deploy code that writes to BOTH old and new systems simultaneously
2. Initially read from old system (feature flag controls this)
3. Run validation process comparing old/new writes
4. Switch reads to new system (via feature flag)
5. Run background process to catch any missed reads
6. Remove old system after 2-4 weeks
```

**Best For:** Database migrations, service replacements

**Implementation Example:**
```javascript
// Write to both systems
async function saveUser(user) {
  const oldResult = await oldDatabase.save(user);
  const newResult = await newDatabase.save(user);

  // Validate consistency
  if (oldResult.id !== newResult.id) {
    logger.error('Consistency check failed', {oldResult, newResult});
  }

  return oldResult; // Read from old for now
}

// Later, switch reads via feature flag
async function getUser(id) {
  if (featureFlags.useNewDatabase) {
    return newDatabase.get(id);
  }
  return oldDatabase.get(id);
}
```

**Timeline:** 1-3 weeks

---

### Pattern 2: Replication-Based (CDC)

**How It Works:**
```
1. Enable Change Data Capture on old system
2. Stream changes to new system in real-time
3. Verify consistency with batch sampling
4. Switch over during low-traffic window
5. Keep old system running 1 week for rollback
```

**Best For:** Data-heavy migrations (MongoDB→PostgreSQL, database migrations)

**Tools:**
- Postgres: `logical replication` (built-in)
- MongoDB: Change Streams (built-in)
- General: Debezium, Maxwell, Airbyte

**Timeline:** 2-4 weeks

---

### Pattern 3: Gradual Cohort Migration

**How It Works:**
```
1. Identify user segments (by geography, signup date, account age)
2. Migrate 5% of users to new system
3. Monitor error rates, performance for 1 week
4. If healthy, migrate next 25%
5. Continue rolling out: 25% → 25% → 20%
6. Keep rollback plan for each cohort
```

**Best For:** Service migrations (Heroku→Railway, Vercel→self-hosted)

**Timeline:** 3-6 weeks

---

### Pattern 4: Strangler Fig

**How It Works:**
```
1. Deploy new system alongside old
2. Route new requests to new system
3. Keep old system for existing functionality
4. Gradually migrate features (month by month)
5. Retire old system after 6-12 months
```

**Best For:** Monolith→Microservices, framework upgrades

**Timeline:** 3-12 months

---

## Data Migration Tools Comparison

| Tool | Cost | Best For | Limitations |
|------|------|----------|-------------|
| **Airbyte** | Free (open-source) to $10K+/year | Small-medium migrations, ETL pipelines | Slower than Fivetran, self-hosted ops burden |
| **Fivetran** | $1K-10K+/month | Enterprise-grade, hands-off | Expensive, black box connector logic |
| **Stitch** (now Talend) | $500-5K+/month | Recurring data sync, analytics | Less mature connector ecosystem |
| **AWS DMS** | $0.50/hour (task) | AWS-centric, large-scale | Limited non-AWS source/target support |
| **Airbyte Cloud** | $500-5K+/year | Managed Airbyte, no ops | Limited connector availability vs. self-hosted |
| **Custom Script** | Dev time only | Complex transformations | High maintenance, fragile |

**Recommendation:** Use Airbyte for one-off migrations, Fivetran for recurring sync

---

## When NOT to Migrate

**Situation 1: System Works Well & No Cost Pressure**
- Don't migrate. A working system is stable and predictable.
- Cost of migration (3-9 months) exceeds cost savings before year 2.
- Risk of catastrophic failure too high.

**Situation 2: Organization Has <3 Engineers**
- Don't migrate. You lack capacity for post-migration firefighting.
- Wait until team grows or hire fractional DevOps consultant.

**Situation 3: Active Feature Development**
- Don't migrate. Feature work will be blocked during migration.
- Plan migration during slow period (Q4 often good).
- If urgent (compliance, security), pause features.

**Situation 4: Poor Test Coverage**
- Don't migrate. You can't validate equivalence between old/new.
- Spend 2-3 weeks improving test coverage first.
- Migrations without tests fail 40% of the time.

**Situation 5: Unclear Business Case**
- Don't migrate. Cost savings unclear, timeline uncertain.
- Do detailed ROI analysis first (break-even point, payback period).
- Require >40% savings to justify migration risk.

**Situation 6: Critical System Stability**
- Don't migrate. 99.99% uptime system undergoing migration = severe risk.
- Migrate non-critical systems first to build competency.
- De-risk: use strangler fig or dual-run approaches.

---

## Migration Cost & Timeline Estimates

### Small Apps (<10K Users, <1GB Data)

| Migration | Timeline | Cost (Dev Hours) | Annual Savings | ROI Breakeven |
|-----------|----------|-----------------|---|---|
| Firebase → Supabase | 4-6 weeks | 40-60 | $3K-8K | 2-4 months |
| Heroku → Railway | 1-2 weeks | 20-30 | $2K-5K | 1-3 months |
| Vercel → Coolify | 2-3 weeks | 30-50 | $5K-10K | 2-4 months |
| Auth0 → Clerk | 1-2 weeks | 15-25 | $5K-10K | 1-2 months |
| Stripe → Lemon | 1-2 weeks | 20-30 | $500-2K | 3-6 months |

### Medium Apps (10K-100K Users, 1-10GB Data)

| Migration | Timeline | Cost (Dev Hours) | Annual Savings | ROI Breakeven |
|-----------|----------|-----------------|---|---|
| Firebase → Supabase | 6-8 weeks | 60-100 | $5K-15K | 3-6 months |
| Heroku → Railway | 2-3 weeks | 40-60 | $4K-10K | 2-4 months |
| MongoDB → PostgreSQL | 6-8 weeks | 80-120 | $3K-8K | 6-12 months |
| AWS → Hetzner | 6-8 weeks | 80-120 | $10K-30K | 3-6 months |

### Large Apps (100K+ Users, 10GB+ Data)

| Migration | Timeline | Cost (Dev Hours) | Annual Savings | ROI Breakeven |
|-----------|----------|-----------------|---|---|
| Firebase → Supabase | 10-14 weeks | 120-180 | $15K-40K | 4-8 months |
| MongoDB → PostgreSQL | 10-14 weeks | 140-200 | $8K-20K | 8-16 months |
| AWS → Hetzner | 12-16 weeks | 160-240 | $50K-150K | 4-8 months |
| Monolith → Microservices | 6-18 months | 800-2000 | $50K-200K | 12-36 months |

**Cost Multiplier Factors:**
- Poor documentation: +30-50% cost
- Complex custom integrations: +40-80% cost
- Multiple data sources: +20-40% cost
- Zero-downtime requirement: +30-50% cost
- Regulatory compliance: +50-100% cost
- Team inexperience with target tech: +50-100% cost

---

## Decision Logic: Should You Migrate?

```
START
  │
  ├─ Is system broken or causing production issues?
  │  ├─ YES → Fix issues first, then evaluate migration
  │  └─ NO → Continue
  │
  ├─ Does organization have capacity (team size >3)?
  │  ├─ NO → Wait or hire
  │  └─ YES → Continue
  │
  ├─ Is cost savings >40% annually?
  │  ├─ NO → Don't migrate (risk not justified)
  │  └─ YES → Continue
  │
  ├─ Will payback period be <18 months?
  │  ├─ NO → Re-evaluate costs or timeline
  │  └─ YES → Continue
  │
  ├─ Is there compliance/security mandate?
  │  ├─ YES → Migrate (non-negotiable)
  │  └─ NO → Continue
  │
  ├─ Do we have >80% test coverage?
  │  ├─ NO → Improve testing first (2-3 weeks)
  │  └─ YES → Continue
  │
  ├─ Can we afford 2-3 weeks of slower feature work?
  │  ├─ NO → Schedule during slower business period
  │  └─ YES → Continue
  │
  ├─ Can we execute zero-downtime migration?
  │  ├─ YES → Use dual-write or CDC pattern
  │  └─ NO → Plan maintenance window (30 minutes acceptable?)
  │
  └─ DECISION: MIGRATE
     ├─ Plan 30% time buffer into timeline
     ├─ Assign 1 senior engineer full-time
     ├─ Keep rollback plan active 2-4 weeks
     └─ Monitor aggressively post-migration
```

---

## Pricing Stability Note

<!-- PRICING_STABILITY: high | last_verified: 2026-03 | check_interval: 12_months -->

**Important:** Pricing and cost estimates in this document are based on March 2026 data. Verify current pricing:

- **Firebase:** `firebase.google.com/pricing`
- **Supabase:** `supabase.com/pricing`
- **Heroku:** `heroku.com/pricing`
- **Railway:** `railway.app/pricing`
- **DigitalOcean:** `digitalocean.com/pricing`
- **Hetzner:** `hetzner.com/cloud/pricing`
- **Vercel:** `vercel.com/pricing`
- **Coolify:** `coolify.io/pricing`
- **Stripe:** `stripe.com/pricing`
- **LemonSqueezy:** `lemonsqueezy.com/pricing`
- **Auth0:** `auth0.com/pricing`
- **Clerk:** `clerk.com/pricing`

**Re-verify estimates every 12 months** as vendor pricing changes 5-15% annually.

---

## Key Takeaways

1. **Don't migrate for its own sake.** A working system has value.
2. **Migrations cost 3-9 months and 40-240 engineering hours.** Require 40%+ savings.
3. **Zero-downtime is possible:** dual-write, CDC, gradual cohorts, strangler fig.
4. **Most common migrations:** Firebase→Supabase, Heroku→Railway, AWS→Hetzner.
5. **Common failure modes:** poor test coverage, capacity constraints, unclear business case.
6. **Always build 30% time buffer** into project timeline.
7. **Keep rollback plan active 2-4 weeks** post-migration.
8. **Verify pricing before committing** to migration (vendor pricing shifts annually).

---

## Related References
- [Vendor Lock-In Analysis Reference Guide](./51-vendor-lock-in-analysis.md) — Exit strategy planning for technology choices
- [Serverless Hosting: Comprehensive Tech-Stack Recommendation](./11-serverless-hosting.md) — Evaluating serverless migration targets
- [Container Hosting & PaaS Platform Comparison](./12-container-hosting-paas-platform-comparison.md) — PaaS migration options and comparison
- [Startup to Enterprise Architecture Evolution](./46-startup-to-enterprise-architecture.md) — Planned migrations during scaling
- [Resilience Patterns Reference Guide](./52-resilience-patterns-reference.md) — Maintaining stability during migration

---

## Related Documentation
- Tech Stack Selection Guide (when to choose initial stack)
- Deployment Best Practices (zero-downtime patterns in detail)
- Cost Optimization Framework (full financial modeling)
