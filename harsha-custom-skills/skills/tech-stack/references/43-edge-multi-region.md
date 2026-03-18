# Edge Computing & Multi-Region Architecture

## Executive Summary

Edge computing distributes code execution to servers geographically close to end users, achieving sub-50ms response times. Origin architecture centralizes all logic in one region. Understanding when to employ edge versus origin deployments is critical for building globally performant applications.

**Key Performance Metrics:**
- Edge functions achieve 60-80% TTFB (Time to First Byte) reduction for international users
- Origin single-region deployments average 200-800ms P95 latency for users >5000km away
- Edge achieves sub-50ms response times within 100km radius of edge location
- Multi-region origin deployments can reach 40-120ms P99 latency globally

**Ideal Edge Use Cases:**
- Authentication validation and token verification
- A/B testing and feature flags
- Geo-routing and request redirects
- Personalization based on headers/geolocation
- Response caching and CDN integration
- Request filtering and rate limiting
- Static site generation at request time
- API gateway logic and request transformation

**Ideal Origin Use Cases:**
- Complex business logic requiring transaction management
- Payment processing and financial transactions
- Webhook handling and event processing
- Heavy computation (ML, image processing, data transformation)
- Direct database connections with transaction semantics
- Session state management
- Server-side rendering with data dependencies
- Long-running background jobs

---

## Edge vs Origin Decision Matrix

### Quick Reference Table

| Requirement | Edge | Origin | Notes |
|-------------|------|--------|-------|
| **Auth validation** | ✅ Best | ⚠️ Works | Edge prevents unnecessary origin calls |
| **A/B testing** | ✅ Best | ⚠️ Works | Edge can route before origin sees request |
| **Geo-routing** | ✅ Best | ⚠️ Works | Cloudflare, Fastly excel here |
| **Personalization** | ✅ Best | ⚠️ Works | Edge has request headers instantly |
| **Caching** | ✅ Best | ⚠️ Works | Edge caches, reduces origin load |
| **Business logic** | ❌ No | ✅ Best | Too complex for edge runtime |
| **Payments** | ❌ No | ✅ Only | Security/audit requirements mandate origin |
| **Webhooks** | ❌ No | ✅ Only | Need persistent storage and retries |
| **ML inference** | ❌ No | ✅ Best | Edge has CPU/memory limits |
| **Database writes** | ❌ No | ✅ Only | Transactions require origin connection |
| **Global users** | ✅ Best | ⚠️ Latency | Edge solves latency naturally |
| **Single region** | ❌ Overkill | ✅ Best | No latency advantage |
| **Data residency** | ❌ No | ✅ Only | GDPR/HIPAA compliance |
| **Real-time sync** | ❌ No | ✅ Only | WebSocket not supported in edge |
| **Long processes** | ❌ No | ✅ Only | Edge functions timeout (30-50s max) |

### Decision Flow

```
START
  ↓
[Global user base?]
  NO → Use single-region origin (cost-effective)
  YES ↓
[Compliance data residency required?]
    YES → Multi-region origin in allowed zones only
    NO ↓
[Dynamic content + stateful?]
    YES → Multi-region origin (Fly.io, Railway)
    NO ↓
[Mostly static/cached?]
    YES → Edge + CDN (Cloudflare Pages/Workers)
    NO ↓
[WebSocket/real-time?]
    YES → Multi-region origin
    NO ↓
[CPU-intensive computation?]
    YES → Origin or serverless (Lambda)
    NO ↓
[Frequent origin cache hits?]
    YES → Edge with stale-while-revalidate
    NO ↓
→ HYBRID: Edge for auth/routing + Origin for logic
```

---

## Edge Computing Provider Comparison

### Feature Comparison Table

| Feature | Cloudflare Workers | AWS Lambda@Edge | Vercel Edge Functions | Deno Deploy |
|---------|-------------------|-----------------|----------------------|-------------|
| **Cold Start** | <1ms | ~216ms | ~1ms | <1ms |
| **Runtime** | V8 isolates | Node.js VM | Web APIs (subset) | Deno/TypeScript |
| **Memory Limit** | 128MB | 3GB | 128MB (Pro) | 512MB (Pro) |
| **CPU Limit** | Shared | 2 vCPU | Shared | Shared |
| **Max Duration** | 30s (default) | 30s | 30s (configurable to 120s) | 60s |
| **Pricing** | $0.15/M requests + compute | $0.60/M requests | Included (Pro: $20/mo) | $25-100/mo |
| **Global Replication** | Automatic (200+ POP) | Requires manual setup | Automatic | Automatic |
| **Environment Secrets** | ✅ Wrangler + UI | ✅ CloudFormation | ✅ .env | ✅ Deno Deploy UI |
| **Database Access** | Via KV/D1/SQL | Via Lambda VPC | Via `fetch()` | Via `fetch()` |
| **WebSocket** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Streaming Response** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **npm Package Support** | ⚠️ Limited (bundling) | ✅ Full | ⚠️ Limited | ⚠️ Limited |
| **TypeScript** | ✅ Native | ⚠️ Via compilation | ✅ Native | ✅ Native |
| **Requests/month free tier** | 100k | 1M | Included | 1M |

### Cold Start Latency Breakdown

```
Cloudflare Workers:
  - Isolate reuse: <1ms
  - First boot: 5-15ms
  - Isolate creation: 1-3ms overhead
  - V8 JIT compilation: concurrent in background

AWS Lambda@Edge:
  - VM boot: 50-100ms
  - Runtime init: 50-150ms
  - Code load from S3: variable (50-100ms)
  - Total cold start: ~200-300ms
  - Warm start: <50ms

Vercel Edge Functions:
  - Isolate reuse: <1ms
  - Regional distribution: auto-scaling
  - Total cold start: 1-5ms
  - Uses Cloudflare infrastructure
```

### Cost Analysis (Monthly, 10M requests)

```
Cloudflare Workers:
  - 10M requests × $0.15/M = $1.50
  - CPU time (assume 50ms avg): ~$0.10
  - Total: ~$2-3/month

AWS Lambda@Edge:
  - 10M requests × $0.60/M = $6.00
  - Data transfer costs: ~$0.50/GB (varies)
  - Total: ~$6-8/month

Vercel Edge Functions:
  - Pro plan: $20/month (unlimited requests)
  - Includes 6TB bandwidth
  - Total: $20/month (with all features)

Deno Deploy:
  - Standard: $25/month (10M requests)
  - Pro: $100/month (unlimited)
```

### Provider Recommendation Matrix

| Use Case | Best Choice | Why |
|----------|------------|-----|
| **Startups/MVP** | Vercel Edge (free tier) | Works with Vercel deployment, included free |
| **Cost-sensitive** | Cloudflare Workers | Sub-cent per request, generous free tier |
| **AWS ecosystem** | Lambda@Edge | Integrates with CloudFront, Route53 |
| **Real-time features** | Deno Deploy | WebSocket support, Deno ecosystem |
| **Maximum performance** | Cloudflare Workers | <1ms cold starts, V8 optimizations |
| **Full Node.js** | Lambda@Edge | Complete Node.js runtime available |

---

## Edge Function Limitations (Critical)

### What You CANNOT Do in Edge Functions

#### 1. **No Filesystem Access**
- No `/tmp` writes (except Cloudflare's temporary storage)
- No file uploads to disk
- Cannot read local files
- Limitation impacts: logging to disk, local caching, file processing

**Workaround:** Use object storage (S3, R2, Spaces) or KV stores

#### 2. **No Long-Running Processes**
- Timeout: 30-60 seconds maximum
- Request hangs after timeout with no graceful termination
- Cannot background process
- Limitation impacts: heavy computation, batch operations

**Workaround:** Offload to serverless (Lambda) or background jobs (Bull, RQ)

#### 3. **CPU Time Limits**
- Shared CPU with other tenants
- No predictable CPU allocation
- Computation throttled if overused
- Limitation impacts: ML inference, encryption, parsing

**Workaround:** Pre-compute results, use origin for CPU-heavy work

#### 4. **Memory Constraints**
- Cloudflare: 128MB per request
- Lambda@Edge: 3GB (but costs scale)
- Vercel: 128MB
- Limitation impacts: loading large datasets, caching large objects

**Workaround:** Stream data, paginate responses, use external caches

#### 5. **No Direct Database Connections**
- Cannot maintain persistent TCP connections
- Each request is stateless
- Connection pooling happens at API gateway layer
- Limitation impacts: complex queries, transactions, stored procedures

**Workaround:** Use serverless database SDKs (PlanetScale HTTP API, Turso libsql)

#### 6. **Limited npm Package Compatibility**
- Many packages require Node.js APIs not available in edge
- Browserified packages often bloat bundle size
- Native modules don't work
- Limitation impacts: heavy libraries, system-level packages

**Workaround:** Choose edge-compatible libraries (e.g., jose instead of jsonwebtoken)

#### 7. **No WebSocket Support**
- Edge functions work over HTTP/HTTPS only
- Cannot establish persistent connections
- Limitation impacts: real-time chat, live updates, gaming

**Workaround:** Use origin servers (Fly.io, Railway, VPS)

#### 8. **Environment Isolation**
- Secrets available globally (risk if code is compromised)
- No process isolation between requests
- Cache collisions possible if not carefully namespaced
- Limitation impacts: multi-tenant applications, sensitive data

**Workaround:** Encrypt sensitive data before storage, use request context for isolation

#### 9. **No Streaming Upload**
- Request body must be read entirely into memory
- Large file uploads impossible
- Limitation impacts: video uploads, large file handling

**Workaround:** Use presigned URLs to S3, direct browser uploads

#### 10. **Geographic Distribution Lag**
- New deployments take 30 seconds to several minutes to replicate
- Cannot guarantee immediate global availability
- Limitation impacts: critical hotfixes, time-sensitive deployments

**Workaround:** Version edge logic carefully, use feature flags for gradual rollout

---

## Multi-Region Database Strategies

### Database Technology Comparison

| Database | Architecture | Consistency | Writes | Latency | Pricing | Best For |
|----------|--------------|-------------|--------|---------|---------|----------|
| **CockroachDB** | Native distributed SQL | Strong consistency | Geo-replicated | 100-200ms cross-region | $0.00 (free tier) - $2K+/mo | Enterprise, ACID guarantees |
| **PlanetScale** | MySQL (Vitess) | Eventual consistency | Global write routing | 50-150ms | $29-500/mo | Scaling MySQL, sharding |
| **Neon** | Serverless Postgres | Strong consistency (regional) | Regional failover | 30-50ms intra-region | $0-500/mo | Serverless, auto-scaling |
| **Turso** | Edge SQLite | Eventually consistent | Regional replicas | <1ms edge reads | $4.99-79/mo | Edge computing, reads |
| **Supabase** | Managed Postgres | Strong consistency (regional) | Regional | 30-50ms intra-region | $25-1000/mo | Firebase alternative |
| **MongoDB Atlas** | Document database | Configurable | Global replicas | 50-200ms | $0.30/M reads - $1K+/mo | Flexible schema, global |

### Deep Dive: Multi-Region Patterns

#### Pattern 1: Single-Region Leader (Simplest)

```
┌─────────────────────────────────────────────┐
│         Global Application Requests         │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼────┐           ┌────────▼──┐
   │ Edge     │           │ Origin    │
   │ Cache    │           │ (Single   │
   │ + Routes │           │ Region)   │
   └────┬─────┘           └────────┬──┘
        │                          │
        └──────────────┬───────────┘
                       │
                ┌──────▼──────┐
                │  Primary DB │
                │  (Leader)   │
                └─────────────┘

Latency: 150-400ms P95 (international)
Consistency: Strong (immediate)
Complexity: Low
Scaling: Hits bottleneck at ~10K RPS
Use Case: Regional apps, startups
```

#### Pattern 2: Multi-Region Reads with Write Leader (Recommended for Global)

```
┌──────────────────────────────────────────────────────────┐
│                Global Requests                           │
└────────────┬──────────────────────────────────────────┬──┘
             │                                          │
         ┌───▼────┐                              ┌──────▼──┐
         │ US CDN │                              │ EU CDN  │
         │ + Edge │                              │ + Edge  │
         └───┬────┘                              └──────┬──┘
             │ read-only ops only                       │
         ┌───▼──────────────────────────────────┬──────┘
         │                                      │
    ┌────▼────┐    write-through         ┌─────▼──┐
    │ US Read │                          │ EU Read│
    │ Replica │                          │Replica │
    └────┬────┘                          └─────┬──┘
         │            ┌─────────────┐         │
         └───────────▶│ Primary DB  │◀────────┘
                      │  (Leader)   │
                      │  (Single    │
                      │  Region)    │
                      └─────────────┘

Latency: 30-80ms P95 (same-region reads)
Consistency: Eventual (3-5 seconds replication)
Complexity: Medium (async replication)
Scaling: 50K+ RPS possible
Use Case: Global apps with read-heavy workloads
```

#### Pattern 3: True Multi-Region (CockroachDB Style)

```
┌────────────────────────────────────────────────────────┐
│         Global Requests via Edge Layer                 │
└────┬─────────────────────┬──────────────┬──────────────┘
     │                     │              │
┌────▼────┐         ┌──────▼──┐   ┌──────▼──┐
│US Region│         │EU Region│   │AP Region│
│(Primary)│◀───────▶│(Replica)│◀─▶│(Replica)│
│         │         │         │   │         │
│┌───────┐│         │┌──────┐ │   │┌──────┐ │
││Primary││         ││Replica│ │   ││Replca│ │
││DB     ││         ││DB    │ │   ││DB    │ │
│└───────┘│         │└──────┘ │   │└──────┘ │
└────┬────┘         └─────────┘   └────────┘
     │ consensus via Raft (2+ regions replicate)

Latency: 50-150ms P95 (global)
Consistency: Strong (Raft consensus)
Complexity: High (operational)
Scaling: 100K+ RPS with proper sharding
Use Case: Enterprise, strict consistency
```

#### Pattern 4: Edge SQLite with Regional Sync

```
┌──────────────────────────────────────────────┐
│          Edge Function (Turso SQLite)        │
│  Local read: <1ms / Write: queued            │
└────────────┬─────────────────────────────────┘
             │ async sync
        ┌────▼─────────────────┐
        │   Turso Mirror DB    │
        │  (Edge-optimized)    │
        └────┬─────────────────┘
             │ replication
        ┌────▼──────────────────┐
        │  Regional Primary DB  │
        │  (PlanetScale, Neon)  │
        └───────────────────────┘

Latency: <1ms edge reads / 50-100ms writes (sync)
Consistency: Eventual (eventual strong at primary)
Complexity: Medium (conflict resolution)
Scaling: 100K+ requests, limited storage per edge
Use Case: Read-heavy edge patterns, offline-first
```

### CockroachDB Multi-Region Setup

```yaml
# Cloud configuration
regions:
  - us-east-1 (primary, voting replica)
  - eu-west-1 (voting replica)
  - ap-southeast-1 (non-voting replica)

# Write routing
- Writes always go to primary
- Reads can go to any replica (eventually consistent)
- Automatic failover if primary fails

# Latency characteristics
- Intra-region read: 5-10ms
- Cross-region read: 100-200ms
- Write confirmation: 200-400ms (waiting for quorum)

# Cost (annual)
- Small: $1,000-5,000
- Medium: $5,000-20,000
- Enterprise: $50,000+
```

### PlanetScale Multi-Region Setup

```yaml
# MySQL on Vitess
regions:
  - Primary US region (source of truth)
  - EU replica (read-only)
  - Asia replica (read-only)

# Configuration
- Connection pools per region
- Cross-region async replication
- Automatic write routing to primary

# Latency
- Same-region read: 20-40ms
- Cross-region read: 80-150ms
- Write: 50-100ms (to primary, then replicate)

# Pricing
- Hobby: $0 (10GB, 5 connections)
- Pro: $29 (100GB, 50 connections)
- Enterprise: $499+ (custom limits)
```

### Neon Serverless Postgres

```yaml
# Architecture
- Primary in us-east-1
- Instant reads via HTTP API
- Auto-scaling to zero

# Multi-region approach
- Deploy separate branch per region
- Cross-region queries via API gateway
- Serverless = pay per compute/storage

# Latency
- Same-region: 30-50ms (HTTP overhead)
- Cold start: <100ms
- Warm: <30ms

# Pricing
- Free: 3GB storage, 0.5 CPU-hours/month
- Pro: $10-350/month (usage-based)
```

### Turso Edge SQLite

```yaml
# Edge-native architecture
deployment: Turso edge nodes (200+ locations)
primary_db: Central PlanetScale or Postgres
sync_model: Async local-first

# Operations
- Edge nodes cache read-only copies
- Writes queued and synced to primary
- Eventual consistency (seconds to minutes)

# Latency
- Edge read: <1ms (SQLite)
- Write (async): 0-50ms queued, 100-200ms sync
- Conflict resolution: Last-write-wins or custom

# Pricing
- Free: 10GB storage, 5K requests/mo
- Pro: $4.99/mo + overages
- Enterprise: Custom
```

---

## CDN Architecture Patterns

### Pattern 1: Stale-While-Revalidate (SWR)

```
Request Timeline:
  Client request
    │
    ├─► Cache HIT (stale?) ──► Return cached + background refresh
    │                              (client gets instant response)
    │
    └─► Cache MISS ────────────► Fetch from origin
                                  (synchronous wait)

Benefits:
  - 85-95% origin reduction
  - P50 latency: 5-15ms
  - P95 latency: 20-50ms
  - User sees instant response even during revalidation

Implementation:
  Cache-Control: max-age=60, stale-while-revalidate=86400
  (Revalidate for 1 minute fresh, 24 hours stale)

Latency impact:
  Without SWR: P95 = 150-300ms (origin hit)
  With SWR: P95 = 20-50ms (cache hit, background refresh)
```

### Pattern 2: Cache Shielding

```
┌─────────────────┐
│  10K users      │
│  direct cache   │ (naive)
└────────┬────────┘
         │ all miss origin together
    ┌────▼──────────────────┐
    │  Origin (overwhelmed) │
    └───────────────────────┘

                vs.

┌──────────────────────────────────────┐
│  10K users hit shielding layer       │
│  (CDN edge cache)                    │
└────────────────┬─────────────────────┘
                 │ only shield cache misses origin
         ┌───────▼────────┐
         │  Shield cache  │ (regional)
         │  (1 node)      │
         └────────┬───────┘
                  │ 1 request per cache miss
           ┌──────▼────────┐
           │    Origin     │
           │ (protected)   │
           └───────────────┘

Benefit: Reduces thundering herd (1000 simultaneous misses → 1 origin request)
Implementation: Cloudflare, Fastly, AWS CloudFront
Improvement: 99% origin protection during cache storms
```

### Pattern 3: Asset Versioning

```
# Versioning strategies

Approach 1: Content Hash
  /assets/button-[abc123def].js  (hash changes if content changes)
  /assets/button-[older_hash].js (still available, immutable)

  Advantage: Browser caches forever (max-age=1 year)
  Disadvantage: Need build-time hashing

Approach 2: Timestamp
  /assets/button-1704067200000.js (timestamp in milliseconds)

  Advantage: Works without build tool support
  Disadvantage: Hash doesn't match content (false invalidation)

Approach 3: Semantic Versioning
  /assets/button-v1.0.0.js
  /assets/button-v1.0.1.js

  Advantage: Semantic meaning
  Disadvantage: Manual version management, collision risk

Recommendation: Content hash for CDN, timestamp for cache busting

Cache Header Strategy:
  Versioned assets: Cache-Control: max-age=31536000 (1 year)
  HTML/index: Cache-Control: no-cache (always revalidate)
  API responses: Cache-Control: max-age=60 (1 minute)
```

### Pattern 4: TTL (Time-to-Live) Strategies

```
Resource          TTL      Rationale
────────────────────────────────────────────────────
HTML (index)      0-60s    Frequent updates, need freshness
API responses     60-300s  Balance freshness vs origin load
Images/media      86400s   Immutable, long cache
JavaScript/CSS    86400s   Versioned, immutable
User data         0s       Cache-Control: private, no-cache
Dynamic content   1-10s    Real-time needs, minimal origin load

High-Traffic Optimization:
  Instead of max-age=0 (always revalidate):
  Cache-Control: max-age=10, stale-while-revalidate=3600
  (Serve stale 1 hour, revalidate background)

  Result: 95% cache hits, <100ms P95 latency
```

### Pattern 5: Predictive Prefetching

```
# Edge function prefetch logic

if (userCountry === 'US') {
  // Prefetch next page likely needed
  addHeader('Link', '</api/next-page>; rel=prefetch')
}

if (isPeakHour) {
  // During peak, prefetch more aggressively
  cacheTTL = 300 // 5 minutes
} else {
  cacheTTL = 60 // 1 minute
}

// Geo-based asset optimization
if (userCountry === 'IN') {
  // Smaller images for slower networks
  rewritePath('/image.jpg' → '/image-webp-mobile.jpg')
  addHeader('Cache-Control', 'max-age=86400')
}

Improvement: 30-40% reduction in critical path requests
```

---

## Data Residency for Compliance (GDPR, HIPAA, etc.)

### GDPR Data Residency Requirements

```yaml
# Rule: Personal data of EU residents must remain in EU
# (with limited exceptions)

Compliant Architecture:
  - Database: EU-hosted (AWS eu-west-1, Hetzner, etc.)
  - Backups: EU-only
  - Logs: EU retention
  - CDN caching: EU cache nodes only
  - Monitoring: EU data centers

Non-Compliant (Common Mistakes):
  ❌ Caching personal data in US CDN
  ❌ Storing EU user data in US region
  ❌ Logging to US-based aggregation
  ❌ Using US-only monitoring tools
  ❌ Replicating to US backup region

Implementation:
  1. Geo-fence database connections
  2. Block US CDN for EU users (403 Forbidden)
  3. Use EU-only services (Cloudflare Enterprise for EU restriction)
  4. Audit all third-party integrations
  5. Document Data Processing Agreement (DPA)

Provider Checklist:
  - Supabase EU (eu-central-1)
  - PlanetScale EU cluster
  - Neon EU region
  - Cloudflare Enterprise + EU restriction
```

### HIPAA Compliance Architecture

```yaml
# Rule: Healthcare data requires encryption, access controls, audit logging

Architecture:
  - Database: HIPAA-eligible (AWS RDS with encryption, Supabase Enterprise)
  - Encryption: At-rest (AES-256) + in-transit (TLS 1.3)
  - Access: Audit logging every access
  - Backups: Encrypted, retained 7 years
  - Network: Private VPC, no internet exposure
  - Edge: ❌ CANNOT use for PHI (edge = shared infrastructure)

Prohibited:
  ❌ Storing PHI in edge functions (shared isolates)
  ❌ Caching healthcare data
  ❌ Using public CDNs
  ❌ Third-party analytics on patient data

Solution:
  - Keep PHI at origin (single-tenant)
  - Use edge only for authentication, routing
  - Fetch PHI only via HTTPS direct calls
  - Log all access to encrypted audit trails

Provider Options:
  - AWS (HIPAA Eligible Services)
  - Azure Healthcare (HIPAA compliant)
  - Google Cloud (HIPAA service available)
```

### CCPA Data Residency

```yaml
# Rule: California resident data must respect deletion rights, transparency

Compliance:
  - Right to delete (erasure within 45 days)
  - Right to know (all data collected)
  - Right to opt-out (data sales)
  - Right to access (portable format)

Architecture:
  1. Data inventory: Track all data collected
  2. Soft deletes: Mark deleted, hard delete after 45 days
  3. Audit trail: Log all access/modifications
  4. Transparency: User dashboard showing all data
  5. Portability: Export to JSON/CSV

Edge Considerations:
  - Cache must be ephemeral (not persisted)
  - No long-term analytics at edge
  - User deletion must invalidate cache
  - Edge cannot store PII long-term

Provider:
  - Most US providers default to CCPA compliance
  - Add deletion mechanics
```

### Multi-Region Compliance Decision Logic

```
IF data is PII (names, emails):
  IF EU users → EU region mandatory (GDPR)
  IF HIPAA required → AWS/Azure HIPAA service
  IF CCPA → Deletion pipeline required
  → Cache data region ≤ primary region

IF data is sensitive:
  → No edge caching allowed
  → Origin only, encrypted
  → Audit logging required

IF data is public:
  → Can cache globally
  → Any CDN acceptable
```

---

## Latency Optimization Techniques

### Technique 1: Geo-Partitioning

```
Problem: User in Singapore accessing US-only database
  - Route: Singapore → US → query → US → Singapore
  - Latency: ~200ms network + ~100ms DB = ~400ms P99
  - Network round trips: 2

Solution: Partition data by region
  Database Topology:
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │ US Database  │     │ EU Database  │     │ Asia DB      │
    │  (NA data)   │     │  (EU data)   │     │  (Asia data) │
    └──────────────┘     └──────────────┘     └──────────────┘
         ▲                     ▲                     ▲
         │ local query         │ local query         │ local query
    ┌────┴──────────────────────┴──────────────────┴──────┐
    │         Edge Router (geolocation-based)            │
    │  Routes to nearest regional database                │
    └──────────────────────────────────────────────────────┘

Result:
  - Singapore user → Asia DB (local query)
  - Latency: ~30-50ms P99
  - Improvement: 400ms → 40ms (10x faster)

Implementation:
  1. Shard data by user's home region
  2. Edge function detects geolocation
  3. Routes to regional database
  4. Handle cross-region queries via federation

Trade-off: Higher complexity, distributed transactions harder
```

### Technique 2: Request Hedging

```
Problem: High variance latency (P50=30ms, P99=500ms)
  - Slow database queries sometimes block
  - Origin server occasionally overloaded
  - Result: Users wait >1 second for 1% of requests

Solution: Send request to multiple origins, return first response

Implementation:
  async function hedgedFetch(url, options = {}) {
    const delayMs = options.hedgeDelayMs || 50;

    // Start primary request
    const primary = fetch(url);

    // Start backup request after 50ms delay
    const backup = new Promise(resolve =>
      setTimeout(() => resolve(fetch(url)), delayMs)
    );

    // Return first successful response
    return Promise.race([primary, backup]);
  }

Diagram:
  Time  →

  User request
    │
    ├─► Origin 1 ─────────────────────────► Response (150ms)
    │                                        ▲
    │                                        │ Winner
    └─► Origin 2 (delayed 50ms) ───────────┐
        [after 50ms]                        │
                                            ├─ Return first
                                            │
                                   [backup still pending]
                                   [will timeout/cancel]

Results:
  - P50: ~30ms (primary fast)
  - P95: ~50ms (backup kicks in)
  - P99: ~100ms (hedging prevents >500ms tail)

  Improvement: P99 from 500ms → 100ms (5x)
  Downside: 2x request volume (cost tradeoff)

Real-world: Google, Netflix use hedging at scale
```

### Technique 3: Connection Pooling at Edge

```
Problem: New DB connection per request
  - TLS handshake: 50ms
  - DB handshake: 20ms
  - Query: 10ms
  - Total: 80ms per request (overhead = 75%)

Solution: Maintain persistent connection pools at edge

Architecture:
  ┌─────────────────────────────────────┐
  │     Edge Function Instance          │
  │  ┌──────────────────────────────┐   │
  │  │  Connection Pool             │   │
  │  │  (persistent 1000s ms)       │   │
  │  │  ┌─────────────────────────┐ │   │
  │  │  │ Conn 1: Ready           │ │   │
  │  │  │ Conn 2: Ready           │ │   │
  │  │  │ Conn 3: In use          │ │   │
  │  │  │ ... (up to limit)       │ │   │
  │  │  └─────────────────────────┘ │   │
  │  └──────────────────────────────┘   │
  │                                      │
  │  Request: Get connection → execute   │
  │  (no handshake overhead)             │
  └─────────────────────────────────────┘

Implementation (Cloudflare Workers):
  let pool = null;

  export default {
    async fetch(request) {
      // Reuse pool across requests
      pool = pool || createPool({
        host: 'db.example.com',
        max: 50, // concurrent connections
      });

      const result = await pool.query('SELECT ...');
      return new Response(JSON.stringify(result));
    }
  }

Impact:
  - First request: 80ms (include handshake)
  - Subsequent: 10ms (pool reuse)
  - Avg improvement: 60-70% latency reduction

Caveats:
  - Pool must be created carefully (isolate issues)
  - Connections may close (implement reconnect logic)
  - Memory overhead (50 connections × 10KB = 500KB per instance)
```

### Technique 4: Smart Prefetching Based on Patterns

```
Technique: Analyze user behavior, prefetch likely next requests

Example: Shopping site checkout
  1. Cart page → Edge caches next page (checkout)
  2. Checkout page → Edge caches order confirmation
  3. Confirmation → Edge caches invoice PDF

Implementation:
  export async function handleRequest(request) {
    const page = new URL(request.url).pathname;

    // Pattern: /cart → /checkout
    if (page === '/cart') {
      // Prefetch checkout early
      const prefetchResponse = fetch('/checkout');
    }

    // Pattern: /checkout → /order-complete
    if (page === '/checkout') {
      await caches.default.put(
        '/order-complete',
        await fetch('/order-complete')
      );
    }

    return fetch(request);
  }

Latency:
  Without prefetch:
    Cart page: 200ms
    Checkout: 200ms (user waits)
    Total: 400ms visible latency

  With prefetch:
    Cart page: 200ms (starts prefetch background)
    Checkout: <50ms (cached)
    Total: 200ms visible latency (2x faster)
```

---

## Architecture Decision Logic

### Comprehensive Decision Tree

```
START: Building new application

1. GEOGRAPHY ANALYSIS
   ├─► Single region users only?
   │   └─► Use single-region origin (simplest)
   │       Provider: Railway, Fly.io, Heroku
   │       CDN: Optional (CloudFlare for DDoS only)
   │
   └─► Global users (multiple countries)?
       │
       ├─► Static content (blogs, docs)?
       │   └─► EDGE ARCHITECTURE
       │       ├─ Cloudflare Pages + Workers
       │       ├─ Vercel Edge Functions
       │       └─ Edge cache: 85-95% hit rate
       │
       └─► Dynamic content (database-driven)?
           │
           ├─► Stateless APIs only?
           │   └─► EDGE + CDN
           │       ├─ Edge: Routing, auth, caching
           │       ├─ Origin: Regional API (Fly.io)
           │       └─ Database: Single-region leader
           │
           └─► Requires WebSocket/real-time?
               └─► MULTI-REGION ORIGIN
                   ├─ Fly.io (recommended)
                   ├─ Railway multi-region
                   └─ Database: Multi-region reads

2. DATA REQUIREMENTS
   ├─► Compliance required (GDPR/HIPAA)?
   │   └─► Single region or multi-region (restricted zones)
   │       ├─ EU users: EU region mandatory
   │       ├─ HIPAA: Origin only, no edge
   │       └─ Verify DPA with all services
   │
   └─► No compliance?
       └─► Can use global distribution

3. PERFORMANCE REQUIREMENTS
   ├─► P95 latency target < 100ms globally?
   │   └─► REQUIRED: Multi-region or edge
   │       ├─ Edge alone: 30-50ms (static/cached)
   │       ├─ Multi-region: 50-100ms (with optimization)
   │       ├─ Geo-partitioning: 40ms (database sharding)
   │       └─ Request hedging: 100ms P99
   │
   ├─► P95 latency target < 200ms globally?
   │   └─► Single-region + CDN adequate
   │       ├─ Cloudflare CDN: Good enough
   │       └─ May need prefetching/hedging
   │
   └─► P95 latency > 200ms acceptable?
       └─► Single-region origin (cost-effective)

4. COMPUTATION REQUIREMENTS
   ├─► Heavy computation (ML, processing)?
   │   └─► NOT edge functions
   │       ├─ Use Lambda, Cloud Run, origin
   │       └─ Queue for async (Bull, SQS)
   │
   └─► Light computation (auth, routing)?
       └─► OK for edge
           ├─ Authentication validation
           ├─ Request routing
           └─ Caching logic

5. BUDGET CONSTRAINTS
   ├─► Minimal budget (startup)?
   │   └─► Vercel (free tier edge)
   │       ├─ 100K requests/month included
   │       └─ Perfect for MVP
   │
   ├─► Small budget ($0-50/month)?
   │   └─► Cloudflare Workers
   │       ├─ $0.15/M requests
   │       └─ Generous free tier (100K)
   │
   ├─► Medium budget ($50-500/month)?
   │   └─► Fly.io for origin + Cloudflare
   │       ├─ Fly: $5-100/month (multi-region)
   │       ├─ Cloudflare: $20-200/month
   │       └─ Total: ~$100-200/month
   │
   └─► Large budget (enterprise)?
       └─► Multiple options
           ├─ AWS (Lambda@Edge + CloudFront + RDS)
           ├─ GCP (Cloud Run + Cloud CDN)
           └─ Custom architecture

6. RECOMMENDATION MATRIX

FINAL DECISIONS:

IF global users + static/hybrid content:
   → Edge Architecture (Cloudflare Pages/Workers)
   → Database: Single-region + replication
   → Latency: 30-50ms P95 (cached), 100-200ms (origin)
   → Cost: $20-100/month
   → Complexity: Low

IF global users + dynamic content + stateless APIs:
   → Hybrid (Edge + Multi-region origin)
   → Edge: Auth, routing, caching
   → Origin: Multiple regions (Fly.io)
   → Database: Single-region leader
   → Latency: 50-100ms P95
   → Cost: $100-300/month
   → Complexity: Medium

IF global users + real-time/WebSocket:
   → Multi-region origin only
   → Provider: Fly.io, Railway
   → Database: Multi-region reads
   → Latency: 50-150ms P95
   → Cost: $100-500/month
   → Complexity: Medium-High

IF single-region users:
   → Single-region origin
   → Provider: Railway, Fly.io, Heroku
   → CDN: Cloudflare (DDoS only)
   → Database: Single region
   → Latency: 30-50ms P95
   → Cost: $10-50/month
   → Complexity: Low

IF GDPR data residency required:
   → EU-region deployment mandatory
   → Edge not applicable (data sovereignty)
   → Provider: Supabase EU, Fly.io EU, Railway EU
   → Database: eu-central-1 or eu-west-1
   → Document DPA with all services
   → Latency: 30-50ms intra-EU
   → Cost: +20-30% premium
   → Complexity: Medium (compliance)

IF HIPAA compliance required:
   → Origin only (no edge)
   → Single-tenant infrastructure
   → Database: HIPAA-eligible (AWS, Azure)
   → Encryption: At-rest + in-transit mandatory
   → Audit logging: All access
   → Cost: $500-2000+/month
   → Complexity: High (compliance)

IF real-time/WebSocket + global users:
   → Multi-region origin mandatory
   → Provider: Fly.io (best), Railway
   → NOT: Edge functions (no WebSocket)
   → Database: Multi-region if needed
   → Latency: 50-150ms P95 (connection setup)
   → Cost: $200-1000+/month
   → Complexity: High

IF CPU-intensive workload + global:
   → Origin only
   → CPU: Lambda, Cloud Run, serverless
   → NOT: Edge (CPU limits)
   → Offload computation immediately
   → Queue results for edge serving
   → Cost: Highly variable (compute usage)
   → Complexity: High
```

---

## Database Latency Reference Guide

### Real-World Latency Measurements (2025)

```
Scenario: 10KB query response, US-based user

SINGLE REGION (US-East-1):
  Network round trip: 5-20ms
  Database query: 5-20ms
  Total P95: 30-50ms ✓ BEST

MULTI-REGION SAME COUNTRY (US-East-1 to US-West-2):
  Network round trip: 50-80ms
  Database query: 5-20ms
  Total P95: 60-100ms

MULTI-REGION DIFFERENT CONTINENT (US-East-1 to EU-West-1):
  Network round trip: 100-150ms
  Database query: 5-20ms
  Total P95: 120-170ms

MULTI-REGION OPPOSITE SIDE (US-East-1 to Asia-Southeast):
  Network round trip: 180-250ms
  Database query: 5-20ms
  Total P95: 200-270ms ❌ TOO SLOW

EDGE CACHED (Cloudflare):
  Network: <2ms (edge POP nearby)
  Cache lookup: <1ms
  Total P95: 1-10ms ✓ BEST

EDGE MISS (Origin call from edge):
  Edge → origin: 50-100ms
  Database query: 10-20ms
  Total P95: 60-120ms

With geo-partitioning (Asia user → Asia DB):
  Network round trip: 30-50ms
  Database query: 10-20ms
  Total P95: 40-70ms ✓ GOOD
```

---

## Pricing Stability & Provider Benchmarks

```yaml
# Pricing as of March 2026
# NOTE: Verify current pricing before commitment

Cloudflare Workers:
  - Requests: $0.15 per million (stable 3+ years)
  - CPU time: $0.50 per million CPU-seconds
  - KV storage: $0.50 per GB/month
  - Trend: Stable (price drops unlikely given market)
  - Lock-in: Medium (data export possible)

AWS Lambda@Edge:
  - Requests: $0.60 per million
  - Duration: $0.01 per 100,000 CPU-seconds
  - Data transfer: $0.085 per GB
  - Trend: Stable (AWS long-term price: -2%/year)
  - Lock-in: High (AWS ecosystem)

Vercel Edge Functions:
  - Free: Unlimited within Pro plan
  - Pro: $20/month (includes edge)
  - Enterprise: Custom pricing
  - Trend: Recently made free tier
  - Lock-in: Medium (Vercel ecosystem)

Fly.io:
  - Compute: $0.0000055 per CPU-second (~$16/mo per CPU)
  - Memory: $0.0000032 per MB-second (~$1/mo per GB)
  - Bandwidth: $0.02 per GB (first 100GB free)
  - Trend: Stable (Firecracker-based, efficient)
  - Lock-in: Low (standard containers, easy migrate)

PlanetScale (MySQL):
  - Starter: $0 (5GB, 1B reads, 1B writes)
  - Pro: $29-499 (custom scaling)
  - Trend: Stable (backing Vercel integration)
  - Lock-in: Medium (MySQL ecosystem, export possible)

Turso (Edge SQLite):
  - Free: 9GB storage, 5K requests/month
  - Pro: $4.99/month
  - Trend: Recently launched, pricing competitive
  - Lock-in: Low (SQLite standardized)

CockroachDB:
  - Serverless: $1/month + $0.25 per million requests
  - Dedicated: $12K+ annually
  - Trend: Enterprise pricing, stable
  - Lock-in: Medium (SQL standard, export possible)
```

<!-- PRICING_STABILITY: moderate | last_verified: 2026-03 | check_interval: 6_months -->

---

## Common Mistakes & How to Avoid Them

### Mistake 1: Using Edge for All Operations
**Problem:** Developers assume edge functions are always better
```javascript
// ❌ BAD: Querying entire database from edge
export async function handleRequest(request) {
  const users = await fetch('https://db.example.com/api/users');
  const filtered = users.filter(u => u.active);
  return new Response(JSON.stringify(filtered));
}
// Problem: 3GB memory limit on edge, can't handle 1M users
```

**Solution:** Move logic to origin
```javascript
// ✅ GOOD: Edge handles routing only
export async function handleRequest(request) {
  const response = await fetch('https://origin.example.com/api/active-users');
  return response;
}
// Origin does filtering efficiently with database indexes
```

### Mistake 2: Ignoring Eventual Consistency
**Problem:** Multi-region writes assume strong consistency
```javascript
// ❌ BAD: Write to primary, immediately read from replica
await writeToPrimary(data);
const result = await readFromReplica(data.id);
// Race condition: Replica might not have sync'd yet
```

**Solution:** Implement read-after-write consistency
```javascript
// ✅ GOOD: Read from primary after write
const writtenData = await writeToPrimary(data);
const result = writtenData; // Use write response, don't re-query
```

### Mistake 3: Overprovisioning Multi-Region
**Problem:** Building global architecture for single-region users
```
Cost analysis:
  Multi-region deployment: $500/month
  Single-region deployment: $50/month
  Actual users: All US-based
  Result: 10x cost for 0% benefit
```

**Solution:** Start single-region, scale globally when needed
```yaml
Phase 1 (0-1000 users): Single region ($50/mo)
Phase 2 (1000-10K users): Add CDN ($70/mo total)
Phase 3 (10K-100K users): Add multi-region ($200/mo)
Phase 4 (100K+ users): Optimize geo-distribution ($1K/mo)
```

### Mistake 4: Forgetting Cache Invalidation
**Problem:** Caching data without invalidation strategy
```javascript
// ❌ BAD: Cache response forever
Cache-Control: max-age=31536000 // 1 year
// User updates profile, cache doesn't update
```

**Solution:** Implement cache invalidation
```javascript
// ✅ GOOD: Short TTL + purge on update
Cache-Control: max-age=300 // 5 min
// On profile update:
await caches.default.delete('/api/profile');
```

### Mistake 5: Not Testing Latency Regionally
**Problem:** Testing from office location, missing global latency issues
```
Test result (office, us-west-2): 50ms latency
Production (user, ap-southeast-1): 300ms latency
→ User experience degraded, discovered late
```

**Solution:** Test from multiple regions
```bash
# Use speedtest tools from different regions
curl https://api.example.com --connect-timeout 5 \
  --w "Time: %{time_total}s\n"

# Or use services: Pingdom, New Relic Synthetics
```

---

## Implementation Checklist

### Edge Architecture Deployment

- [ ] Choose edge provider (Cloudflare, Vercel, Deno Deploy)
- [ ] Implement geolocation detection (for routing)
- [ ] Set up cache control headers (max-age, stale-while-revalidate)
- [ ] Configure environment secrets (API keys, tokens)
- [ ] Implement request logging (for debugging)
- [ ] Test cold starts (<100ms)
- [ ] Test cache hit rates (target >80%)
- [ ] Monitor CPU usage (alert if >80%)
- [ ] Set up error tracking (Sentry, LogRocket)
- [ ] Document rate limiting strategy

### Multi-Region Deployment

- [ ] Select database (CockroachDB, PlanetScale, Neon)
- [ ] Configure read replicas in target regions
- [ ] Implement connection pooling
- [ ] Test failover (kill primary, verify replica takes over)
- [ ] Set up replication monitoring
- [ ] Configure backup strategy (geo-replicated)
- [ ] Implement cross-region query routing
- [ ] Test write latency to primary
- [ ] Document recovery procedures
- [ ] Load test from multiple regions

### Performance Validation

- [ ] Measure P50, P95, P99 latency from each region
- [ ] Verify cache hit rates (>80% target)
- [ ] Test origin load (should be <50% CPU)
- [ ] Validate TTFBfrom different networks
- [ ] Test mobile performance (slow 4G)
- [ ] Monitor bandwidth usage (CDN cost)
- [ ] Verify compliance data residency
- [ ] Test disaster recovery (region failure)

---

## Related References
- [File Storage & CDN](./17-file-storage-cdn.md) — CDN integration with edge computing
- [Multi-Tenancy Architecture Patterns](./56-multi-tenancy-patterns.md) — Scaling across regions for multi-tenant systems
- [Relational Databases](./07-databases-relational.md) — Multi-region database strategies
- [Performance Benchmarks](./52-resilience-patterns.md) — Latency and performance measurement
- [Performance Benchmarks](./47-performance-benchmarks.md) — Global performance metrics and optimization

---

## References & Further Reading

- Cloudflare Workers Documentation: https://developers.cloudflare.com/workers/
- Vercel Edge Functions: https://vercel.com/docs/edge-functions
- Fly.io Architecture Guide: https://fly.io/docs/reference/architecture/
- PlanetScale Multi-Region: https://planetscale.com/docs/concepts/sharding
- CockroachDB Multi-Region: https://www.cockroachlabs.com/docs/stable/multiregion-overview
- GDPR Compliance: https://gdpr-info.eu/
- AWS Lambda@Edge: https://docs.aws.amazon.com/lambda/latest/dg/lambda-edge.html
- HTTP Caching Best Practices: https://web.dev/http-cache/

