# Decision Tree: API Service / Microservice

## Entry Point

Start here to determine your API architecture pattern and technology stack.

```
What kind of API?
├── REST API (public, documented, external clients)
│   → REST PATH
├── Internal API (TypeScript monorepo, shared types)
│   → tRPC PATH
├── High-performance microservice (>50k req/sec)
│   → PERFORMANCE PATH
├── AI/ML API (model serving, inference, RAG)
│   → AI PATH
├── GraphQL API (multiple clients, flexible queries)
│   → GRAPHQL PATH
└── Unsure / have multiple services
    → ARCHITECTURE DECISION MATRIX
```

---

## ARCHITECTURE DECISION MATRIX

Use this table to pick your API architecture pattern:

| Scenario | Best Pattern | Why | Limitations |
|----------|------------|-----|------------|
| Single TypeScript frontend + backend | **tRPC** | Zero serialization overhead, full type safety, fastest DX | TypeScript-only, internal use |
| Public API with many external clients | **REST** | Universal language support, standard documentation, OpenAPI | Verbose, higher bandwidth |
| Mobile app + web + partner integrations | **GraphQL** | Single endpoint, clients fetch only needed fields | Complexity, requires client updates |
| Microservices internal communication (low-latency) | **gRPC** | Binary protocol (5-10x smaller), HTTP/2 multiplexing | Language-specific, steeper learning curve |
| Edge functions / serverless (Cloudflare, Lambda) | **Hono/REST** | Multi-runtime support, lightweight | Limited stateful features |
| Real-time data (WebSockets, subscriptions) | **GraphQL** or **REST + WebSockets** | GraphQL subscriptions native; REST needs separate layer | Additional complexity |
| Simple CRUD + minimal clients | **REST** | Lowest complexity, easy documentation | Over-engineered for simple cases |

---

## MICROSERVICES vs MONOLITH DECISION

**When to stay monolithic:**
- Team size: <10 engineers
- Single product with unified business logic
- QPS requirement: <10k requests/sec
- Shared database is acceptable
- Deployment frequency: < 5x per day

**Cost at monolith scale:**
- Single Node.js instance: $20–50/mo handles 1M req/day
- Single database: $25–100/mo handles most growth
- Monolith stays cheaper until you hit 100k–500k daily requests

**When to split into microservices:**
- Independent scaling needs (one service needs 10x more capacity)
- Team size >15 (Conway's Law: system architecture mirrors org structure)
- Different technology requirements per service (one needs Rust for speed, one needs Python for ML)
- Deployment bottlenecks (can't deploy without blocking other teams)
- Database per service requirement (strong data isolation, regulatory separation)

**Microservices cost multiplier:**
- Add 50-100% to infrastructure (more instances, more databases)
- Add 200% to operational overhead (observability, debugging, deployment)
- Only worth it when monolith becomes the bottleneck

---

## API GATEWAY PATTERNS

If you're building microservices, you need an API gateway:

| Pattern | Use Case | Tools | Cost |
|---------|----------|-------|------|
| **Reverse Proxy** | Simple load balancing, same service from multiple instances | Nginx (free), Traefik | $0 (self-hosted) |
| **API Gateway** | Route different endpoints to different services, handle auth | Kong, Traefik, AWS API Gateway | $10–200/mo |
| **Service Mesh** | Advanced routing, circuit breaking, observability between services | Istio, Linkerd | $500+/mo (operational overhead) |
| **Serverless API Gateway** | Edge-based routing, fast startup | Cloudflare Workers, AWS Lambda@Edge | $5–50/mo |

**Recommendation for startups:** Use a reverse proxy (Nginx/Traefik) until you have 5+ microservices. Then evaluate Kong.

---

## API VERSIONING APPROACH

Plan this BEFORE you need it:

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| **URL Path** | `/api/v1/users`, `/api/v2/users` | Clear, backward compatible | Maintain multiple code paths |
| **Header** | `Accept: application/vnd.myapi.v2+json` | Keep URL clean | Clients need to know about it |
| **Query Param** | `/api/users?version=2` | Optional, flexible | Confusing for clients |
| **Content Negotiation** | Based on JSON version field | Modern, flexible | Requires client intelligence |

**Best practice:** URL path versioning + deprecation policy
- Keep v1 supported for 12 months minimum
- Document sunset date clearly
- Provide migration guide to v2
- Use `/api/v1/` not `/v1/api/` (prefix the version)

**Real example stacks:**
- Stripe uses URL versioning: `/v1/charges`
- GitHub uses header versioning: `Accept: application/vnd.github.v3+json` (moved to `api.github.com/graphql`)
- Twilio uses URL versioning: `/2010-04-01/Accounts/{id}`

---

## API PATTERN SELECTION

```
IF TypeScript monorepo (shared types client+server) → tRPC (zero overhead, full type safety)
IF public API needing documentation                 → REST + OpenAPI (standard, discoverable)
IF multiple clients with different data needs       → GraphQL (mobile + web + partner APIs)
IF microservices internal communication             → gRPC (binary protocol, fastest)
IF lightweight HTTP API on edge/serverless          → Hono RPC (Hono's built-in typed RPC)
```

---

## REST PATH

### REST Framework Selection by Constraints

| Your Primary Constraint | Framework | Cost/Mo | Reasoning |
|-------------------------|-----------|---------|-----------|
| **Minimum cost** | Hono + Cloudflare Workers | $5–15 | $5/mo flat fee for unlimited requests |
| **Fastest development** | Next.js API Routes | $0–20 | Unified frontend/backend, zero setup |
| **Maximum performance** | Elysia (Bun) or Axum (Rust) | $10–30 | 50-100x faster than Node.js for CPU-bound |
| **Enterprise standards** | NestJS + Railway | $25–50 | TS decorators, DI, testing patterns |
| **Python ecosystem** | FastAPI + Railway | $25–50 | Great for ML/data teams, type hints native |
| **Lightweight microservice** | Chi (Go) + Hetzner VPS | $5–20 | 5x less memory, scales better on bare metal |
| **Maximum ecosystem size** | Express + Vercel | $20–50 | Largest npm ecosystem, most libraries |

### REST Framework Decision Tree

```
Do you have a TypeScript frontend?
  YES → Use tRPC instead (skip REST overhead)
  NO  → Continue

Need maximum performance (>50k req/sec per instance)?
  YES → Go (Chi) or Rust (Axum)
  NO  → Continue

Python team?
  YES → FastAPI
  NO  → Continue

Serverless/Edge deployment mandatory?
  YES → Hono (multi-runtime)
  NO  → Continue

Enterprise patterns required (large team, TS ecosystem)?
  YES → NestJS
  NO  → Fastify (best balance)
```

### By Language & Scale

#### TypeScript (Most Common)

| Scale | Framework | ORM | Hosting | Database | Monthly Cost |
|-------|-----------|-----|---------|----------|-------------|
| MVP | Hono | Drizzle | Cloudflare Workers | Supabase Free | $0–5 |
| Growing | Fastify | Drizzle | Railway | Neon Launch ($19) | $25–50 |
| Scaling | Fastify or NestJS | Prisma or Drizzle | Railway + Fly.io | Supabase Pro | $100–300 |
| Enterprise | NestJS | Prisma | AWS ECS/Lambda | AWS RDS | $500+ |

**Framework Selection:**
```
IF edge/serverless deployment needed   → Hono (multi-runtime: Node, Bun, Workers, Deno)
IF maximum ecosystem + plugins         → Fastify (2x faster than Express)
IF enterprise patterns + team >5       → NestJS (decorators, DI, modules)
IF legacy / quick prototype            → Express (largest ecosystem, slowest)
IF Bun runtime + max speed             → Elysia (Bun-native, fastest TypeScript)
```

#### Python

| Scale | Framework | ORM | Hosting | Database | Monthly Cost |
|-------|-----------|-----|---------|----------|-------------|
| MVP | FastAPI | SQLModel | Railway | Supabase Free | $0–5 |
| Growing | FastAPI | SQLAlchemy | Railway | Neon Launch | $25–50 |
| Scaling | Django | Django ORM | Hetzner + Coolify | PostgreSQL | $20–100 |
| Enterprise | Django/FastAPI | SQLAlchemy | AWS ECS | AWS RDS | $300+ |

**Framework Selection:**
```
IF async API + auto-docs + type safety   → FastAPI
IF admin panel + ORM + auth + batteries  → Django
IF lightweight microservice              → Flask or Starlette
IF FastAPI-like but more performant      → Litestar
```

#### Go

| Scale | Framework | Hosting | Database | Monthly Cost |
|-------|-----------|---------|----------|-------------|
| Any | Chi or Gin | Hetzner VPS (€4/mo) | PostgreSQL | $5–20 |
| Scaling | Chi + stdlib | Fly.io or Railway | Neon/Supabase | $30–100 |
| Enterprise | Chi or Fiber | AWS ECS | AWS RDS | $200+ |

**Why Go for APIs:** 5–20x less memory than Node.js/Python. A Go API on a €4 Hetzner VPS
handles traffic that would need a $50/mo Node.js setup.

#### Rust

| Scale | Framework | Hosting | Database | Monthly Cost |
|-------|-----------|---------|----------|-------------|
| Any | Axum | Hetzner VPS (€4/mo) | PostgreSQL | $5–15 |
| High-perf | Axum or Actix | Fly.io | Neon | $20–60 |

**Why Rust:** Maximum requests/sec, minimum memory. Worth the learning curve only
for CPU-bound, latency-critical services (payment processing, real-time bidding).

---

## HANDLING API AT DIFFERENT SCALES

Understanding performance characteristics helps you make the right architecture decision early.

### Scale Characteristics by Request Volume

**Scale 1: <100 requests/second (MVP - Growing)**
- Single instance needed
- Suitable frameworks: any (Express, Fastify, Django, FastAPI)
- Database: Single Postgres instance
- Caching: Not needed yet
- Cost: $20–50/mo
- Example: Small SaaS, <1k active users

**Scale 2: 100–1k requests/second (Growing - Scaling)**
- 2–5 instances needed
- Suitable frameworks: Fastify, Django, FastAPI, Go, Rust
- Database: Postgres with read replicas
- Caching: Redis for sessions + rate limiting
- Cost: $200–500/mo
- Example: Medium SaaS, 1k–10k users
- Common issue: Database becomes bottleneck

**Scale 3: 1k–10k requests/second (Scaling - Enterprise)**
- 10–50 instances needed
- Suitable frameworks: Go, Rust, Axum, Actix
- Database: Postgres + connection pooling, sharding
- Caching: Redis cluster, CDN
- Cost: $500–2k/mo
- Example: Large SaaS, 10k–100k users
- Common issue: Operational complexity explodes

**Scale 4: >10k requests/second (Enterprise)**
- 50+ instances, multiple regions
- Suitable frameworks: Rust, Go, specialized systems
- Database: Multi-region, read-write separation
- Caching: Multi-layer (CDN, Redis, query cache)
- Cost: $2k–10k+/mo
- Example: Stripe-scale, millions of users
- Common issue: Cost optimization becomes critical

### Performance Optimization by Scale

| Scale | Main Bottleneck | Solution | Complexity |
|-------|-----------------|----------|-----------|
| **<100 req/s** | Code efficiency | Profile + optimize endpoints | Low |
| **100–1k** | Database queries | Indexes, connection pooling, caching | Medium |
| **1k–10k** | Database + network | Read replicas, query optimization, CDN | High |
| **>10k** | Cost per request | Hardware selection (Rust vs Go), multi-region | Very High |

---

## tRPC PATH (TypeScript Monorepo)

tRPC is the best choice when your frontend and backend are tightly coupled and both in TypeScript.

### When to Use tRPC

✓ **Use tRPC if:**
- Frontend + backend both TypeScript
- Single team owns both
- Can deploy simultaneously
- Don't need REST API for public consumption
- Want maximum type safety

✗ **Don't use tRPC if:**
- Need public API for third-party integration
- Have separate frontend/backend teams
- Mobile apps need REST endpoints
- Partner APIs need documentation

### tRPC Architecture

```
Frontend (React/Vue/Svelte)
  ↓ (client type-safe call)
tRPC Router (type definitions)
  ↓ (network: JSON/HTTP)
Backend (Node.js/Fastify/Next.js)
  ↓
Database (Postgres + Drizzle)
```

**What makes tRPC special:**
```typescript
// Backend: Define your procedure
const router = t.router({
  users: t.procedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      return await db.users.findUnique({ id: input.id })
    })
})

// Frontend: Type safety automatically
const user = await trpc.users.query({ id: '123' })
//                         ^ types inferred, autocomplete works
```

**Database → Client type flow:**
```
Database schema (Drizzle)
  ↓ (infer types)
ORM types (User, Post, etc)
  ↓ (input to tRPC)
tRPC router types
  ↓ (sent to client)
React component types (full type safety!)
```

### tRPC Stack Recommendation

```
When:        Full TypeScript stack, shared types between client and server
Framework:   tRPC v11 + Fastify adapter or Next.js
Validation:  Zod (built-in with tRPC)
Database:    Drizzle + PostgreSQL (best schema inference)
Hosting:     Vercel (if Next.js) or Railway (standalone Fastify)
Database hosting: Neon (branch per developer, free)
```

### tRPC Performance Characteristics

| Metric | vs REST | vs GraphQL |
|--------|---------|-----------|
| Bandwidth | -40% (binary-friendly JSON) | -60% |
| Latency | Same (HTTP still overhead) | +20% (parsing) |
| Developer experience | +100% (full type safety) | -50% (boilerplate) |
| Learning curve | Medium (new paradigm) | Medium (RPC is simple) |

### Real-world tRPC Stack Example (Shadcn/UI)

Shadcn uses tRPC for internal tooling:
```
Frontend: Next.js App Router + React
tRPC: v11
Database: PostgreSQL + Drizzle ORM
Hosting: Vercel + Neon
Deployment: Automatic on git push
```

**Why this works:**
- Single team (Vercel)
- Tight frontend/backend coupling needed
- Type safety critical (component props must match API)
- Monorepo simplifies deployment

### tRPC Gotchas

| Gotcha | Impact | Solution |
|--------|--------|----------|
| **No REST API** | Can't integrate with mobile SDK | Use REST alongside tRPC |
| **Type explosion** | Circular types cause build errors | Use separate API layer |
| **No GraphQL introspection** | No client-side code generation | Use tRPC extensions for this |
| **Tight coupling** | Hard to change API without breaking frontend | Treat tRPC queries as public API |
| **Batch requests** | No automatic batching (different from GraphQL) | Use tRPC middleware for batching |

### Migration Path: REST → tRPC

If starting with REST and want to migrate:

```
Phase 1: Add tRPC router alongside REST
  /api/users (REST)
  /trpc/users (tRPC)

Phase 2: Migrate endpoints one by one
  /api/users → /trpc/users
  Update client queries
  Keep REST for external clients

Phase 3: Remove REST endpoints
  Once all clients migrated
  Keep deprecation period
```

---

## GraphQL PATH - DEEP DIVE

GraphQL is worth the complexity ONLY if you have specific requirements.

---

## PERFORMANCE PATH (High-Throughput)

### Performance Benchmarks (req/sec, single core, hello world)

| Framework | Language | Req/sec | Memory (idle) |
|-----------|----------|---------|---------------|
| Axum | Rust | ~400,000 | 2–5 MB |
| Actix Web | Rust | ~380,000 | 3–6 MB |
| Fiber | Go | ~350,000 | 5–10 MB |
| Gin | Go | ~300,000 | 5–10 MB |
| Elysia (Bun) | TypeScript | ~250,000 | 20–30 MB |
| Hono (Bun) | TypeScript | ~200,000 | 20–30 MB |
| Fastify | TypeScript | ~80,000 | 40–60 MB |
| Express | TypeScript | ~15,000 | 50–80 MB |
| FastAPI | Python | ~12,000 | 50–80 MB |
| Django | Python | ~3,000 | 80–120 MB |

**Decision rule:** If your API needs >50k req/sec per instance, consider Go or Rust.
For most apps, Fastify or Hono on Node.js is more than enough.

---

## AI PATH (Model Serving / Inference API)

```
IF wrapping LLM API (OpenAI/Anthropic/etc.)
  → Hono or FastAPI + Vercel AI SDK
  → Host on: Cloudflare Workers (cheapest) or Railway

IF serving custom ML model
  → FastAPI + vLLM (GPU) or Ollama (CPU)
  → Host on: RunPod, Modal, or AWS SageMaker

IF RAG (Retrieval-Augmented Generation)
  → FastAPI or Hono
  → Vector DB: pg_vector (free with Postgres) or Pinecone
  → Host on: Railway or Fly.io
```

### AI API Cost Optimization
```
IF simple tasks (classification, extraction)    → GPT-4o-mini or Gemini Flash ($0.15/1M tokens)
IF complex reasoning                            → Claude Sonnet ($3/$15 per 1M tokens)
IF cost-critical + acceptable quality drop      → Groq (Llama 3, $0.11/1M tokens)
IF privacy-critical                             → Ollama self-hosted ($0 API cost)
IF need multiple providers + fallback           → OpenRouter (routes across providers)
```

---

## GRAPHQL PATH - DEEP DIVE

GraphQL is worth the complexity ONLY if you have specific requirements.

### When to Use GraphQL (Real Requirements)

✓ **Strong case for GraphQL:**
- **Multiple clients with different data needs:** Web (needs full user profile), mobile (needs minimal data), partner API (needs custom subset)
- **Deep nested relationships:** API must traverse Author → Posts → Comments → Likes
- **Complex filtering:** Clients need flexible, complex query capabilities
- **Real-time subscriptions:** WebSocket-based live updates
- **Analytics/reporting:** Fine-grained field-level tracking

✗ **Weak case (just use REST):**
- Single client (web SPA)
- Simple CRUD operations
- Small team without GraphQL expertise
- <10 API clients
- Performance is critical (REST is faster)

### GraphQL Stack Recommendation

```
IF React/Next.js frontend     → Apollo Server + Apollo Client (best DX)
IF code-first schema (TS)     → Pothos (TypeScript, type-safe)
IF schema-first + speed       → GraphQL Yoga + Codegen (lighter weight)
IF Supabase/Postgres          → PostGraphile (auto-generated GraphQL from schema)

Hosting: Vercel, Railway, Fly.io, Hetzner
Database: Any (PostgreSQL, MySQL, MongoDB)
```

### GraphQL Architecture Decision

| Decision | Apollo Server | GraphQL Yoga | Pothos | PostGraphile |
|----------|---------------|-------------|--------|------------|
| **Setup time** | 1 day | 2 hours | 3 days | 1 hour (auto) |
| **Type Safety** | Medium | Medium | High (TS) | None (schema-first) |
| **Learning curve** | Steep (decorators) | Medium | Medium (plugin system) | Low (SQL) |
| **Scalability** | Excellent | Excellent | Good | Limited to DB |
| **Best for** | Large teams, complex APIs | Quick start, lightweight | Type-safe APIs, TS teams | Simple CRUD |
| **Cost** | $0 (open source) | $0 | $0 | $0 + DB |

### GraphQL vs REST: Real Cost Comparison

**Simple API (10 endpoints, CRUD)**
- REST: 2 days development, 1 endpoint per operation
- GraphQL: 4 days development, 1 endpoint for everything
- Winner: REST (50% faster)

**Complex API (50+ endpoints, multi-client)**
- REST: 20 days development (lots of duplication), unclear versioning
- GraphQL: 15 days development (reusable schema), clear evolution
- Winner: GraphQL (25% faster at scale)

**API serving 10+ different clients with different needs**
- REST: Each client needs custom endpoint (100 endpoints total)
- GraphQL: Each client queries same endpoint (1 endpoint)
- Winner: GraphQL (99% simpler)

### Common GraphQL Mistakes

| Mistake | Impact | Solution |
|---------|--------|----------|
| **N+1 query problem** | 100x slower than REST | Use DataLoader batching |
| **Resolver explosion** | Complex resolver code, bugs | Limit nested depth (3 levels max) |
| **No authorization per field** | Data leaks | Implement field-level permissions |
| **Unbounded queries** | DDoS attacks, cost explosion | Implement query depth + complexity limits |
| **Over-fetching** | Contradicts GraphQL benefit | Implement field-level caching |

### GraphQL Query Complexity Example

```graphql
# Dangerous: Unlimited nested depth
{
  user(id: 123) {
    posts {
      comments {
        author {
          posts {
            comments {
              author {
                # Could nest indefinitely
              }
            }
          }
        }
      }
    }
  }
}
```

**Solution: Limit query depth**
```typescript
// Only allow 3 levels deep max
const server = new ApolloServer({
  plugins: {
    didResolveOperation({ request }) {
      const depth = getQueryDepth(request.operationName);
      if (depth > 3) throw new Error('Query too deep');
    }
  }
});
```

### GraphQL Performance Tuning

| Optimization | Impact | Effort |
|-------------|--------|--------|
| **DataLoader** (batch queries) | 10–100x speed improvement | Medium |
| **Field resolver caching** | 5–10x improvement | Medium |
| **Persisted queries** | 30% bandwidth reduction | Medium |
| **Fragment caching** | 20% improvement | Low |
| **Query complexity limits** | Prevents abuse | Low |

### Real-world GraphQL Examples

**Example 1: Shopify API (Highly successful GraphQL)**
- Multiple client types: web, mobile, partner APIs
- Complex domain: Products → Variants → Inventory → Pricing
- Deep relationships: Order → LineItems → Product → Recommendations
- Result: Best-in-class API, partners love it

**Example 2: GitHub API (Mixed REST + GraphQL)**
- REST v3 for simple operations
- GraphQL v4 for complex queries
- Allows clients to choose
- Result: Gradual migration path

**Example 3: Stripe API (Pure REST, no GraphQL)**
- Simple resource model
- Consistent endpoints
- Webhooks handle real-time
- Result: Fastest implementation, lowest maintenance

---

## Cross-Cutting Concerns

### AUTHENTICATION FLOWS & DECISION MATRIX

Understanding which auth pattern applies to your API is critical.

| Auth Pattern | Use Case | Standard | Tools | Cost | Complexity |
|--------------|----------|----------|-------|------|------------|
| **Session Cookies** | Own frontend only (web browser) | RFC 6265 | Auth.js, Clerk | $0–25/mo | Low |
| **JWT (stateless)** | SPAs, mobile apps, own frontend | RFC 7519 | jsonwebtoken, jose | $0 | Medium |
| **API Keys** | Third-party developers, public API | Custom per company | Clerk + API Keys | $0–50/mo | Low |
| **OAuth 2.0 (Authorization Code)** | User login via third-party (Google, GitHub) | RFC 6749 | Auth0, Clerk | $0–500/mo | High |
| **OAuth 2.0 (Client Credentials)** | Machine-to-machine, backend services | RFC 6749 | Auth0, custom | $0–500/mo | Medium |
| **mTLS** | Service-to-service, highest security | TLS 1.3+ | ACME, cert-manager | $0 (self-hosted) | Very High |
| **API Gateway Auth** | Legacy, centralized token validation | Custom | AWS API Gateway, Kong | $50–500/mo | Medium |

**Decision flow:**
```
Is this only for your own frontend?
  YES → Session cookies (simplest, most secure)
  NO  → Continue

Do clients need to be authenticated directly?
  YES → Use OAuth 2.0 Authorization Code (user login)
  NO  → Use API Keys or OAuth 2.0 Client Credentials (service auth)

High security + service-to-service?
  YES → Consider mTLS
  NO  → API Keys or Client Credentials
```

**Real-world patterns:**
- **Stripe API:** API Keys per account (stateless, audit-friendly)
- **GitHub API:** Personal access tokens (API keys style) + OAuth for user login
- **AWS:** Long-term access keys + temporary STS credentials (rotating)
- **Google Cloud:** Service accounts with rotating JWT assertions

**Implementation roadmap:**
1. Start with session cookies (own frontend) + API keys for third parties
2. Add OAuth when you support user login (Clerk handles this)
3. Add mTLS only if you have high-security service-to-service needs

---

### RATE LIMITING STRATEGY

Rate limiting protects your API from abuse and cost overruns.

| Scope | Implementation | Cost | Precision |
|-------|----------------|------|-----------|
| **Per User** | Redis counter + key = user_id | $0.50–10/mo | Per-user limits |
| **Per IP** | IP-based counters | $0.50–10/mo | Shared limit across users |
| **Global** | Central counter (Redis) | $0–10/mo | Service-wide limit |
| **Distributed** | Token bucket across edge locations | $5–50/mo | Geographic awareness |
| **CDN-level** | Cloudflare/WAF rules | $0–200/mo | Network-level (most efficient) |

**How to implement by platform:**

```
IF Cloudflare Workers:
  → Upstash Ratelimit (serverless Redis)
  → Code: await ratelimit.limit(userId)

IF Node.js/Express:
  → npm install express-rate-limit
  → Store in memory (<10k users) or Redis (>10k)

IF Hono:
  → @hono/rate-limiter middleware
  → Works with memory, Redis, or Upstash

IF Fastify:
  → @fastify/rate-limit plugin
  → Auto-integrates with Redis

IF Go/Rust:
  → Implement custom using Redis
  → Or use API gateway (Kong, nginx)
```

**Rate limiting window sizes:**
- **1 request/second:** Anti-DDoS, authentication endpoints
- **10 requests/second:** API endpoints for normal users
- **100 requests/second:** Bulk operations, data exports
- **1,000 requests/minute:** High-volume endpoints (webhooks, sync)

**Real-world limits:**
- Stripe API: 100 requests/second per account
- GitHub API: 60 requests/minute (unauthenticated), 5,000/hour (authenticated)
- Twitter API: Varies by endpoint (1,500 requests/15 minutes for user endpoints)

---

### CACHING LAYER DECISIONS

Caching significantly reduces database load and response times.

| Cache Type | Use Case | Tools | Cost | TTL |
|-----------|----------|-------|------|-----|
| **Response Caching** | Entire response cacheable by all users | Cloudflare Cache, Vercel Edge | $0–50/mo | 1–24 hours |
| **User-Specific Cache** | Per-user data (after auth) | Redis/Upstash | $0.50–10/mo | 5–30 min |
| **Query Result Cache** | Heavy computation caching | Redis + pg materialized views | $0–20/mo | 5 min–1 hour |
| **Database Query Cache** | ORM query-level caching | Prisma Client Extensions | $0 | Per-query |
| **Computed Columns** | Pre-computed aggregates | PostgreSQL computed columns | $0 | On-write |
| **Edge Cache** | Static assets, API responses at edge | Cloudflare, Vercel Edge Config | $0–100/mo | 1–24 hours |

**Caching implementation hierarchy (by complexity):**

```
Level 1 (Easiest): HTTP response headers
  - Add Cache-Control: public, max-age=3600
  - Cloudflare auto-caches public responses
  - Cost: $0, Benefit: 60-80% reduction

Level 2 (Moderate): Redis for user data
  - Cache user profile after auth
  - Cache API rate limit counters
  - Cost: $0.50–5/mo, Benefit: 40-60% reduction

Level 3 (Advanced): Database query caching
  - Cache expensive JOIN results
  - Invalidate on INSERT/UPDATE
  - Cost: $0 (using Redis), Benefit: 50-70% reduction

Level 4 (Very Advanced): CDN with purging
  - Personalized responses at edge
  - Invalidate on user action
  - Cost: $20–100/mo, Benefit: 80-95% reduction
```

**Cache invalidation strategies:**

| Strategy | Complexity | Accuracy | Use Case |
|----------|-----------|----------|----------|
| **TTL only** | Low | 70% (stale reads) | Public data, non-critical |
| **TTL + manual purge** | Medium | 90% | User-modifiable data |
| **Event-driven invalidation** | High | 100% | Critical data (payment status) |
| **Cache-aside pattern** | Medium | 85% | Most production APIs |

**Redis cost estimation:**
- $0.50/mo: 10GB, 100k operations/sec (Upstash Hobby)
- $5/mo: 100GB, 1M operations/sec
- $50/mo: Managed Redis (AWS ElastiCache)

---

### API DOCUMENTATION STRATEGY

Good documentation is an extension of your API design.

| Documentation Type | Tools | Effort | Cost | Audience |
|-------------------|-------|--------|------|----------|
| **Auto-generated (OpenAPI)** | Scalar, Swagger UI | 2 hours setup | $0 | Developers |
| **Hosted docs** | Mintlify, ReadMe | 1 day setup | $25–500/mo | Public API users |
| **Interactive playground** | Apollo Studio (GraphQL), Postman | 4 hours | $0–30/mo | API testers |
| **Custom documentation** | VitePress, Docusaurus | 1 week | $0–50/mo | Complex APIs |

**OpenAPI/Swagger best practices:**
```yaml
# Generate from your code (TypeScript)
npm install @nestjs/swagger @nestjs/common swagger-ui-express

# Document every endpoint
@ApiOperation({ summary: 'Get user by ID' })
@ApiResponse({ status: 200, type: UserDto })
@Get('/:id')
getUser(@Param('id') id: string) { }

# Client libraries auto-generated
npx @openapitools/openapi-generator-cli generate \
  -i openapi.json -g typescript-axios
```

**Documentation hosting by scale:**
- MVP: Swagger UI (free, hosted on your domain)
- Growing: Mintlify (500k+ docs views/month, great UX)
- Scaled: ReadMe (premium features, community, analytics)

---

### DATABASE PER SERVICE CONSIDERATIONS

If you're building microservices, each service should own its database.

**Pros of database per service:**
- Independent scaling (payment service might need 10x replicas)
- Schema evolution doesn't block other teams
- Technology choice per service (one uses PostgreSQL, one uses MongoDB)
- Failure isolation (payment DB issue doesn't crash user service)

**Cons:**
- Distributed transactions become hard (need saga pattern or event sourcing)
- Cross-service queries require federated queries or data duplication
- Operational complexity increases (manage more databases)
- Cost multiplier (database per service = more infrastructure cost)

**Implementation patterns:**

| Pattern | Use Case | Complexity |
|---------|----------|-----------|
| **Shared DB + schemas** | <5 microservices, tight coupling OK | Low |
| **Shared DB + row-level isolation** | Multi-tenant, clear data boundaries | Medium |
| **DB per service** | 5+ services, high autonomy | High |
| **Event sourcing** | Complex domain, audit trail required | Very High |

**Data consistency across services:**
```
Option 1: Synchronous (API calls)
  - Service A calls Service B API
  - Fast but tight coupling, cascading failures

Option 2: Eventual consistency (message queue)
  - Service A publishes event (UserCreated)
  - Service B subscribes, processes asynchronously
  - Decoupled, but eventual consistency

Option 3: CQRS (Command Query Responsibility Segregation)
  - Commands go to service A (writes)
  - Queries read from service B's read model (cache)
  - Best for complex domains
```

---

## Hosting Decision for APIs

```
IF serverless + edge + cheapest                    → Cloudflare Workers ($5/mo for unlimited)
IF container + simple deployment                   → Railway ($5–20/mo)
IF global edge deployment                          → Fly.io ($29/mo+)
IF self-hosted + cheapest long-term                → Hetzner VPS (€4/mo) + Docker
IF self-hosted + PaaS experience                   → Coolify on Hetzner
IF AWS ecosystem                                   → Lambda (serverless) or ECS (containers)
IF need GPU (AI/ML)                                → RunPod, Modal, or AWS SageMaker
```

---

## MONITORING & OBSERVABILITY FOR APIs

Observability is three pillars: logs, metrics, traces (the "three pillars").

### Monitoring Stack by Scale

| Scale | Errors | Logs | Metrics | Uptime | Traces | Cost/Mo |
|-------|--------|------|---------|--------|--------|---------|
| **MVP** | Sentry Free | Console | None | Uptime Robot | None | $0–10 |
| **Growing** | Sentry Free | BetterStack Free | Prometheus | BetterStack | None | $20–50 |
| **Scaling** | Sentry Team | Axiom or Datadog | Grafana Cloud | Uptime Monitoring | Datadog APM | $100–300 |
| **Enterprise** | Datadog | Datadog Logs | Datadog Metrics | Datadog SLO | Datadog Traces | $500–2000+ |

### What to Monitor by Component

**Application Metrics:**
- Request latency (p50, p95, p99)
- Error rate (5xx errors, validation errors)
- Request volume (req/sec by endpoint)
- Database connection pool usage
- Cache hit/miss ratio
- Queue depth (background jobs)

**Infrastructure Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Database query time

**Business Metrics:**
- API requests (cost tracking if rate-limited)
- Active API keys / users
- Error categories (group by type)
- Webhook delivery success rate

### Observability Tools Comparison

| Tool | Logs | Metrics | Traces | Cost | Best For |
|------|------|---------|--------|------|----------|
| **Sentry** | Limited | No | Basic | $26/mo | Error tracking + user impact |
| **Grafana Cloud** | Yes | Yes | No (need Loki) | $20–200/mo | Open source monitoring |
| **Datadog** | Yes | Yes | Yes | $15–50/host | Complete observability |
| **New Relic** | Yes | Yes | Yes | $25–100/mo | APM + logs unified |
| **Axiom** | Yes | No | No | $10–100/mo | Structured logging |
| **BetterStack** | Yes | No | No | $21/mo | Uptime + logs budget |
| **OpenTelemetry** | Free | Free | Free | $0 (infra only) | Vendor-agnostic instrumentation |

### Minimum Viable Observability

Start here and upgrade as you scale:

```
Week 1: Add error tracking
  npm install @sentry/node
  Sentry.init({ dsn: process.env.SENTRY_DSN })
  Sentry.captureException(error)
  Cost: $0 (free tier covers 5k errors/mo)

Week 2: Add uptime monitoring
  Sign up for Uptime Robot or BetterStack
  Ping your API health endpoint every 5 min
  Cost: $0–21/mo

Week 3: Add request logging
  Log key events: user signup, payment, errors
  Use structured logging (JSON format)
  Cost: $0 (console logs) or $10–50/mo (centralized)

Month 2: Add metrics
  Track response time, error rate, request volume
  Use Prometheus + Grafana (or Grafana Cloud)
  Cost: $20–100/mo

Month 3: Add APM (Application Performance Monitoring)
  Full transaction tracing (request → database → response)
  Use Datadog or New Relic
  Cost: $100–300/mo
```

### Common Monitoring Mistakes

| Mistake | Impact | Solution |
|---------|--------|----------|
| Monitoring only errors | Miss slowdowns | Add latency percentiles (p95, p99) |
| No business metrics | Can't correlate with revenue | Track API requests, user signups |
| Over-alerting | Alert fatigue | Set thresholds at >2std dev from normal |
| Siloed monitoring | Team confusion | Centralize logs + metrics in one tool |
| No trace context | Hard to debug | Add request IDs to all logs |
| Monitoring only production | Miss issues early | Run same stack in staging |

### Distributed Tracing for Microservices

If you have multiple services calling each other:

```
Request comes in:
  trace_id = generate_uuid()

Service A processes:
  span_id = generate_uuid()
  log: { trace_id, span_id, event: 'user_lookup' }
  Call Service B...

Service B processes:
  span_id = generate_uuid()
  parent_span_id = from_header
  log: { trace_id, span_id, parent_span_id, event: 'db_query' }

Dashboard shows:
  User sees entire flow: Service A → DB → Service B → Cache → Response
  Total latency: 450ms (A: 100ms, B: 200ms, Cache: 50ms, Network: 100ms)
```

**Tools:** OpenTelemetry (standard), Jaeger (open source), or Datadog APM (enterprise).

---

## REAL-WORLD API ARCHITECTURE EXAMPLES

### Example 1: SaaS API (Stripe-like)

**Scale:** 10k–100k API clients

**Architecture:**
```
Clients (SDKs in 10+ languages)
  ↓
Cloudflare WAF (rate limiting, DDoS)
  ↓
Load Balancer (ELB or Fly.io)
  ↓
API Servers (Fastify/NestJS, 5–20 instances)
  ↓
Postgres (RDS, read replicas for analytics)
  ↓
Redis (session cache, rate limit counters)
  ↓
External: S3 (file storage), SQS (async jobs), SNS (webhooks)
```

**Tech Stack:**
- Framework: NestJS (enterprise patterns)
- Database: AWS RDS PostgreSQL
- Cache: AWS ElastiCache Redis
- Hosting: AWS ECS + ALB
- Monitoring: Datadog
- Cost: $2,000–5,000/mo

**Why this stack:**
- Fastify/NestJS mature, proven at scale
- RDS handles millions of queries/day
- Redis for rate limiting (critical)
- AWS for compliance + enterprise features

---

### Example 2: Lightweight Microservice (Payment processor)

**Scale:** 1k–10k requests/sec

**Architecture:**
```
Payments API (Rust/Axum)
  ↓
Load Balancer
  ↓
Axum Servers (1–5 instances, 1 CPU each)
  ↓
Postgres (minimal, mostly caching)
  ↓
Redis (rate limiting, job queue)
```

**Tech Stack:**
- Framework: Axum (Rust)
- Database: Neon Postgres (serverless)
- Cache: Upstash Redis
- Hosting: Fly.io
- Cost: $200–500/mo

**Why this stack:**
- Rust handles 100k+ req/sec per instance
- Minimal memory footprint
- Serverless databases for elastic scaling
- Cost 10x lower than Node.js equivalent

---

### Example 3: Internal GraphQL API (B2B SaaS)

**Scale:** 100–1k employees, 10k+ daily queries

**Architecture:**
```
Web/Mobile Clients (Apollo)
  ↓
Apollo Server (TypeScript, Next.js)
  ↓
Postgres (single instance, read replicas soon)
  ↓
Redis (session cache, query cache)
  ↓
S3 (file uploads)
```

**Tech Stack:**
- Framework: Apollo Server + Next.js API Routes
- Database: Supabase Postgres
- Cache: Upstash Redis
- ORM: Prisma with query cache
- Hosting: Vercel
- Cost: $100–300/mo

**Why this stack:**
- Apollo Server mature ecosystem
- Prisma handles N+1 query problems
- Vercel edge functions for performance
- Supabase auth + RLS simplifies auth

---

## MOVING FROM MONOLITH TO MICROSERVICES

**When ready to split:**

1. **Identify service boundaries:**
   - Services with independent scaling needs
   - Services owned by different teams
   - Services with different tech requirements

2. **Start with API Gateway:**
   ```
   Existing Monolith (50% traffic)
   New Service (50% traffic)
       ↑
   API Gateway (Kong or Traefik)
   ```

3. **Migrate slowly:**
   - Week 1: New service live, 5% traffic
   - Week 2: 25% traffic
   - Week 3: 50% traffic
   - Week 4: 100% traffic, keep monolith as backup

4. **Decouple data:**
   - Monolith owns its database
   - New service owns its database
   - Use event sourcing for data sync

**Cost of transition:**
- Additional infrastructure: 50% increase (2 databases, 2 services)
- Additional ops overhead: 200% increase (monitoring, debugging)
- Time investment: 3–6 months
- Only do this if you're hitting monolith bottlenecks
