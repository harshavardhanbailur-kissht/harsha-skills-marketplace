# Backend Node.js/Bun/Deno: Runtimes & Frameworks

**Research Date:** February 2026
**Scope:** Production-ready Node.js, Bun, and Deno backend runtimes and frameworks
**Status:** Active research; includes live benchmarks and 2025-2026 feature parity

## Executive Summary (5-line TL;DR)
- Node.js 22 LTS remains production default: mature ecosystem, 13-20K RPS baseline, best library compatibility
- Bun 1.2+ offers 2-3.5x faster throughput (30-52K RPS) but ecosystem gaps remain for production workloads
- Fastify is the performance framework choice (2.3x Express), Hono for edge/multi-runtime portability
- Deno 2.x improves Node.js compatibility significantly; viable for new greenfield projects with security focus
- Express remains appropriate for prototypes and teams prioritizing ecosystem over raw performance

---

## RESEARCH METADATA

### Sources Consulted
- [Node.js Official Release Blog](https://nodejs.org/en/blog/announcements/v22-release-announce)
- [Bun Runtime Releases](https://github.com/oven-sh/bun/releases)
- [Deno 2.0 Launch](https://deno.com/blog/v2.0)
- [Express 5 Released](https://www.infoq.com/news/2025/01/express-5-released/)
- [Fastify Benchmarks](https://fastify.dev/benchmarks/)
- [Hono Official Docs](https://hono.dev/)
- [NestJS Releases](https://github.com/nestjs/nest/releases)
- [Elysia Framework](https://elysiajs.com/)
- [tRPC v11 Announcement](https://trpc.io/blog/announcing-trpc-v11)
- [Koa Framework](https://koajs.com/)
- [AdonisJS Docs](https://adonisjs.com/)
- [Nitro Server Engine](https://nitro.build/)

### Key Disclaimer
Benchmark data varies by test methodology. "Hello world" endpoints differ significantly from database-heavy operations. Cold start times are measured for serverless contexts only.

---

## RUNTIME COMPARISON: Node.js vs Bun vs Deno

| Feature | Node.js 22 LTS | Bun 1.2+ | Deno 2 |
|---------|---|---|---|
| **Release Date** | Oct 2024 | Rolling (1.2 in 2025) | Oct 2024 |
| **Type Support** | Native TS via tsx/tsx-loader | Native TypeScript | Native TypeScript |
| **npm Compatibility** | Native | ~95% (improving) | 100% via `npm:` specifier |
| **Startup Performance** | 30% improvement v20→v22 | 3–5x faster than Node | Comparable to Node 22 |
| **Memory Usage** | Baseline | 40% less than Node (varies) | Similar to Node |
| **WebSocket** | Default (v22) | Built-in | Web Standard API |
| **Native Fetch** | Yes (v18+) | Yes | Yes |
| **Test Runner** | Experimental (node --test) | Built-in, fast | Deno.test |
| **Package Manager** | npm/pnpm/yarn | bun install (90% faster cache-hit) | deno install (15% faster cold) |
| **SQLite Support** | Via npm packages | Built-in (Bun.SQLiteDatabase) | Via npm packages |
| **Edge Compatibility** | Limited | Limited (Bun Deploy beta) | Full (Deno Deploy) |
| **Production Ready** | ✓ Stable | ⚠ Greenfield projects | ✓ Stable |
| **Ecosystem Size** | Massive (npm) | Growing (~70K packages) | Growing |

### Node.js 22 LTS Highlights
- **Stability:** Oct 2024 release; Active LTS until Oct 2025, Maintenance until Apr 2027
- **Performance:** 30% startup improvement; Maglev JIT enabled by default
- **Features:** Default WebSocket, experimental `node --run`, stable watch mode
- **Security:** Stricter TLS defaults (stronger ciphers only)
- **Future:** Server Components support planned for 2025

### Bun 1.2+ Highlights
- **Speed:** 3–5x faster startup; ~40% lower memory in some scenarios
- **Node Compat:** Jumped from ~85% to ~95% in 2025; bun_modules isolation improving
- **Postgres Client:** Native @bun/pg (fast!)
- **TypeBox Validation:** 18x faster than Zod at runtime
- **Caution:** No formal LTS; breaking changes possible; not recommended for enterprise legacy migration

### Deno 2.0 Highlights
- **npm Compatibility:** Run existing Node projects; deno install/add/remove commands
- **Speed:** 15% faster `deno install` than npm (cold cache); 90% faster (hot cache)
- **Node-API Support:** sqlite3, esbuild, duckdb work natively
- **Deploy Platform:** Deno Deploy (managed, global edge deployment)
- **Migration Path:** Incremental Deno adoption in existing Node projects

---

## FRAMEWORK PERFORMANCE BENCHMARKS

Methodology: Simple GET endpoint benchmark (hello-world style). Real apps with databases/queries will show different results.

| Framework | Version | Req/sec | Latency (ms) | Cold Start (ms) | Bundle (KB) | TypeScript Quality |
|-----------|---------|---------|---|---|---|---|
| **Fastify** | 5.0+ | ~87,000 | 1.2 | 45 | 85 | ★★★★★ |
| **Hono** | 4.0+ (Node) | ~35,000* | 2.8 | 38 | 32 | ★★★★★ |
| **Hono** | 4.0+ (Bun) | ~120,000† | 0.8 | 8 | 32 | ★★★★★ |
| **Express** | 5.0 | ~25,000 | 3.5 | 55 | 125 | ★★★★☆ |
| **Koa** | 2.15+ | ~65,000 | 1.5 | 42 | 60 | ★★★★☆ |
| **NestJS** | 10.4+ | ~15,000 | 6.2 | 120 | 450 | ★★★★★ |
| **Elysia** | 1.0+ (Bun) | ~140,000 | 0.7 | 5 | 28 | ★★★★★ |
| **AdonisJS** | 6.0+ | ~12,000 | 8.1 | 95 | 520 | ★★★★★ |

**Notes:**
- *Hono on Node uses an adapter layer (Web Standards → Node streams); slower than native frameworks
- †Hono on Bun exploits native Web Standard APIs; best of both worlds
- NestJS and AdonisJS include heavier feature sets; slower but enterprise-ready
- Elysia requires Bun; not compatible with Node.js

**Variance:** Benchmarks depend on methodology. Complex database queries will flatten these differences. Real-world apps rarely hit theoretical maximums.

---

## FEATURE COMPARISON MATRIX

| Feature | Fastify | Hono | Express 5 | NestJS | Elysia | Koa | AdonisJS | Nitro |
|---------|---------|------|-----------|--------|--------|-----|----------|-------|
| **Runtime Support** | Node | Multi | Node | Node | Bun | Node | Node | Node/Bun/Deno/Edge |
| **Validation** | JSON Schema (fast) | Zod/Valibot | No built-in | class-validator | TypeBox (fastest) | No | VineJS | Zod/Valibot |
| **ORM Integration** | Via plugins | Direct | Via middleware | Prisma/TypeORM native | Manual | Via koa-orm | Lucid (built-in) | Via plugins |
| **Authentication** | Via plugins | Via middleware | Via passport | @nestjs/passport | Manual | Via koajwt | Built-in (multi-auth) | Via plugins |
| **WebSocket** | Via @fastify/websocket | Native | Via ws package | @nestjs/websockets | Native | Via ws | Built-in | Via Nitro hooks |
| **Real-time Streaming** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **GraphQL** | Via plugin | Via middleware | Via apollo-server | @nestjs/graphql | Manual | Via apollo-koa | Via plugins | Manual |
| **REST Auto-Docs** | Via @fastify/swagger | Via @honojs/swagger | Via swagger-ui-express | @nestjs/swagger | Manual OpenAPI | Via koaswagger | Lucid migrations | Via auto-generate |
| **Testing Framework** | Via tap/jest | Via vitest/bun-test | Via jest | Jest native | Bun.test | Via jest/vitest | AdonisJS runner | Via vitest |
| **Middleware Ecosystem** | Large (~500 packages) | Growing (~200) | Massive (~5000) | Via modules | Emerging | Large (~800) | Built-in | Composable |
| **Learning Curve** | Medium | Low | Very Low | High | Medium | Low | High | Medium |

---

## SERVERLESS & EDGE COMPATIBILITY MATRIX

| Platform | Node.js | Fastify | Hono | Elysia | NestJS | Nitro | AdonisJS |
|----------|---------|---------|------|--------|--------|-------|----------|
| **AWS Lambda** | ✓ | ✓ (via serverless) | ✓✓ (native Web API) | ✗ (Bun-only) | ⚠ (cold start slow) | ✓✓ | ⚠ |
| **Cloudflare Workers** | ✗ | ✗ | ✓✓ | ✗ | ✗ | ✓ | ✗ |
| **Vercel Functions** | ✓ | ✓ | ✓ | ✗ | ⚠ | ✓✓ | ⚠ |
| **Deno Deploy** | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| **AWS Lambda@Edge** | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| **Netlify Functions** | ✓ | ✓ | ✓ | ✗ | ⚠ | ✓ | ⚠ |
| **Google Cloud Functions** | ✓ | ✓ | ✓ | ✗ | ⚠ | ✓ | ⚠ |
| **Fly.io** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Docker** | ✓ | ✓ | ✓ | ✓ (bun image) | ✓ | ✓ | ✓ |

**Legend:** ✓ = Works | ✓✓ = Optimized | ⚠ = Works with caveats | ✗ = Incompatible

---

## DECISION TREE: "Which Node.js Framework?"

```
START: Choosing a Node.js/Bun/Deno Backend
│
├─ PERFORMANCE IS CRITICAL (>50K req/sec needed)?
│  ├─ YES + Using Bun?
│  │  └─> Elysia (140K req/sec, native TypeScript, Eden Treaty type-safety)
│  │
│  └─ YES + Using Node.js?
│     ├─ Edge-first deployment (Cloudflare/Lambda@Edge)?
│     │  └─> Hono (native Web Standards, multi-runtime, 35K req/sec on Node)
│     │
│     └─ Traditional VPS/Docker?
│        └─> Fastify (87K req/sec, JSON schema validation, stable ecosystem)
│
├─ ENTERPRISE PATTERNS + DDD (Dependency Injection, Decorators)?
│  ├─ YES + Already know NestJS?
│  │  └─> NestJS 10+ (decorators, modules, testing support, GraphQL native)
│  │
│  └─ YES + Prefer Laravel-like structure?
│     └─> AdonisJS 6 (built-in auth, ORM, sessions, opinionated)
│
├─ FULL-STACK MONOREPO WITH TYPE SAFETY?
│  ├─ YES + Want tRPC (RPC-style, React/Next.js)?
│  │  └─> tRPC v11 (end-to-end types, React Query integration, RSC support)
│  │
│  ├─ YES + Only Bun + need Web API surface?
│  │  └─> Elysia + Eden Treaty (type-safe client generation, fastest validation)
│  │
│  └─ YES + Multi-runtime (Nuxt, full-stack)?
│     └─> Nitro (standalone deployment, auto-API routes, multi-platform)
│
├─ MINIMAL + FAMILIAR (MOST DEVELOPERS KNOW THIS)?
│  └─> Express 5 (finally released, promise support, ReDoS fixes)
│
├─ MINIMALIST + MODERN ASYNC (NO CALLBACKS)?
│  └─> Koa 2 (middleware stack model, clean async/await, 65K req/sec)
│
└─ MIGRATING FROM EXPRESS?
   ├─ Need 3x speed boost?
   │  └─> Fastify (similar middleware, JSON schema, straightforward migration)
   │
   └─ Need edge + multi-runtime?
      └─> Hono (Web Standards API, same route patterns, drop-in compatible)
```

---

## EXPRESS MIGRATION PATHS

### Express 4 → Express 5
**When:** Only if your team is already on Express and wants to stay within the ecosystem.

**Key Changes:**
- Node 18+ required (dropped 16.x, 17.x support)
- Regex ReDoS mitigations: `/:foo(\\d+)` no longer works; use query params instead
- Promise rejection handling: `async` middleware now automatic; no need for try-catch wrapper
- `req.acceptsCharset()` → `req.acceptsCharsets()` (pluralized methods)
- Status code enforcement: invalid codes (e.g., 1234) now throw errors

**Migration Effort:** 4–8 hours for medium app (audit regex patterns, update method calls)

### Express 4 → Fastify 5
**When:** You want ~3x performance and don't mind refactoring middleware.

**Key Differences:**
- Fastify uses reply object for responses (not res); `reply.send()` instead of `res.json()`
- Middleware pattern similar but different: `fastify.register()` instead of `app.use()`
- JSON Schema validation replaces body parser; auto-validates & coerces
- Hooks (onRequest, onSend) instead of middleware chain

**Migration Effort:** 16–40 hours (significant refactor; benefit is real)

**Community Tools:** [fastify-express](https://github.com/fastify/fastify-express) wraps Express middleware for Fastify

### Express 4 → Hono
**When:** You need multi-runtime support or edge deployment.

**Key Differences:**
- Web Standards API (Request, Response) instead of Express req/res
- Routing syntax identical: `app.get('/path', handler)`
- Middleware via `app.use(middleware)` works similar
- Same code runs on Node, Bun, Deno, Cloudflare, AWS Lambda@Edge

**Migration Effort:** 12–24 hours (API surface compatible; test on target runtime)

**Advantage:** Single codebase for Node + Cloudflare + Lambda@Edge deployment

---

## THE tRPC QUESTION: When to Use tRPC vs REST vs GraphQL

### tRPC (Type-Safe RPC)
**Use when:**
- Full-stack TypeScript monorepo (Next.js, Remix, Nuxt + backend)
- Need automatic type inference end-to-end (no API docs needed)
- Team is small-to-medium (easier coordination)
- React/Vue Query integration is valuable

**Don't use when:**
- Mobile apps need API (tRPC is not spec-compliant; hard to implement clients in Swift/Kotlin)
- Multiple backend languages (Go, Rust, Python teams)
- Need introspectable schema (GraphQL playground, API docs tooling)

**Performance:** Zero runtime overhead if using client-side libraries; server-side is RPC-like (no GraphQL parsing)

**v11 Highlights:** RSC support, non-JSON data (FormData, Blobs), SSE subscriptions, TanStack Query 5 integration

### REST API (Traditional)
**Use when:**
- Mobile + web + third-party integrations
- Public API (swagger/OpenAPI docs, versioning)
- Teams using different languages
- Mature tooling required (rate limiting, caching, webhooks)

**Advantage:** Simplicity; cacheable by HTTP semantics

**Disadvantage:** Manual type definitions; versioning overhead

### GraphQL
**Use when:**
- Complex data relationships (blog + comments + authors + tags)
- Multiple consumers with different data needs
- Federated across services (@apollo/gateway)
- Need fine-grained authorization per field

**Disadvantage:** Learning curve; query complexity; caching harder; slower on large response sets

### Comparison
| Aspect | tRPC | REST | GraphQL |
|--------|------|------|---------|
| **Type Safety** | Automatic (monorepo) | Manual + OpenAPI | Automatic via schema |
| **Mobile Support** | Hard | Easy | Hard (heavy responses) |
| **Caching** | Query-based | HTTP semantics | Per-field caching required |
| **Learning** | Very Low | Very Low | High |
| **Overfetch** | No | Possible | No (exact query) |
| **Underfetch** | No | No | Possible (N+1 queries) |

**Verdict for 2025:** Use tRPC in monorepos; REST for public APIs; GraphQL for complex data graphs.

---

## MONOREPO PATTERNS WITH TYPESCRIPT BACKENDS

### Pattern 1: Turborepo + tRPC + pnpm
**Best for:** Next.js + Node backend in single repo

```
monorepo/
├── packages/
│  ├── api/          (tRPC server)
│  ├── client/       (Frontend consuming tRPC)
│  ├── shared/       (Types, constants)
│  └── database/     (Prisma, migrations)
├── turbo.json
└── pnpm-workspace.yaml
```

**Tooling:** turbo build, turbo dev, pnpm install (fast)

### Pattern 2: Nx + Fastify + NestJS
**Best for:** Multi-service microservices

```
monorepo/
├── apps/
│  ├── api-user/     (NestJS user service)
│  ├── api-payment/  (Fastify payment service)
│  └── web/          (React)
├── libs/
│  ├── shared-types/
│  ├── db-models/
│  └── auth/
└── nx.json
```

**Tooling:** nx serve api-user, nx build api-user, nx graph (visualize)

### Pattern 3: pnpm Workspaces + Elysia + Bun
**Best for:** Greenfield Bun projects (speed-focused)

```
monorepo/
├── packages/
│  ├── backend/      (Elysia on Bun)
│  ├── frontend/     (React)
│  └── types/        (Shared TypeScript)
├── bun.lockb        (Bun lock file)
└── pnpm-workspace.yaml
```

**Developer Experience:** bun install (instant); bun run (any script); zero config

---

## FRAMEWORK DEEP DIVES

### Fastify 5 (Node.js Standard)
- **Plugins:** Ecosystem of 500+ plugins; JSON schema validation built-in (18x faster than runtime validators)
- **Decorators:** Extend request/reply with custom methods
- **Async Errors:** Automatic error boundary; no try-catch wrapper needed
- **When:** You want Express-like DX with 3x performance; VPS/Docker deployment

### Hono (Multi-Runtime Darling)
- **Web Standards:** Request, Response, Headers use native APIs (runs on Workers, Lambda@Edge, Deno)
- **Middleware:** Compatible with Express-style middleware via adapter
- **Performance Note:** On Node, Hono uses adapter (slower). On Bun/Cloudflare, it's native (fastest)
- **When:** Edge-first, multi-runtime requirement, or Lambda@Edge needed

### NestJS 10+ (Enterprise DDD)
- **TypeScript First:** Classes, decorators, dependency injection native
- **Testing:** Test utilities in core; mock modules easily
- **GraphQL:** @nestjs/graphql native; federation support
- **When:** Large teams, complex domain logic, need testing framework built-in

### Elysia (Bun's Native Child)
- **Eden Treaty:** Generates type-safe client code from route definitions (like tRPC but framework-native)
- **TypeBox Validation:** 18x faster than Zod (AOT compilation in Bun)
- **Only Bun:** Not compatible with Node.js; greenfield projects only
- **When:** New Bun project, type safety is top priority, validation performance matters

### AdonisJS 6 (Laravel for Node)
- **Full-Featured:** Auth, ORM (Lucid), validation (VineJS), sessions, file uploads all built-in
- **Opinionated:** Folder structure, naming conventions; less flexibility than Express
- **MVC-Focused:** Controllers, routes, models, migrations like Laravel
- **When:** Need Django/Laravel-like structure; full-stack app with minimal glue code

### Nitro (Nuxt's Server Engine)
- **Standalone:** Use outside Nuxt; independent server framework
- **Zero-Config:** Auto-routes from file structure; /api/hello.ts → POST /api/hello
- **Multi-Platform:** Deploy to Node, Bun, Deno, Cloudflare, AWS Lambda, Vercel, Netlify
- **When:** Fullstack Nuxt app or need multi-platform deployment with zero config

---

## GAPS & LIMITATIONS

### Gap 1: TypeScript DX Still Behind Go/Rust
- **Problem:** Runtime validation often manual or via third-party libs (Zod, Valibot)
- **Status:** Elysia (TypeBox AOT) and tRPC help; still not native like Go interfaces
- **Workaround:** Use Elysia or strict tRPC schemas

### Gap 2: Bun Production Gaps
- **Problem:** No formal LTS; API stability not guaranteed; ecosystem smaller than Node
- **Status:** 95% npm compat; Bun 1.2+ much better; still risky for existing projects
- **Workaround:** Use Bun for new services, not legacy migration

### Gap 3: Deno Ecosystem Smaller Than npm
- **Problem:** Only 2+ million npm packages vs Node's 2.5+ million
- **Status:** Deno 2's `npm:` support narrowing gap; most packages work
- **Workaround:** Use Deno for greenfield; Node for legacy

### Gap 4: Edge Runtime Constraints
- **Problem:** Workers/Lambda@Edge can't run long-lived processes or full ORM (no migrations)
- **Status:** Hono, Nitro handle these; still a coordination problem
- **Workaround:** Use Prisma Data Proxy or external migration tools

### Gap 5: WebSocket Across Runtimes
- **Problem:** Node's native WebSocket doesn't work on Cloudflare Workers
- **Status:** Most frameworks abstract; Hono handles it; still pain point
- **Workaround:** Use Server-Sent Events (SSE) for edge, WebSocket for Node

---

## SOURCE REGISTRY

### Official Documentation
1. [Node.js 22 LTS Release](https://nodejs.org/en/blog/announcements/v22-release-announce)
2. [Bun Runtime](https://bun.sh/)
3. [Deno 2.0 Blog](https://deno.com/blog/v2.0)
4. [Express 5 Release Notes](https://www.infoq.com/news/2025/01/express-5-released/)
5. [Fastify Official Docs](https://fastify.dev/)
6. [Hono Documentation](https://hono.dev/)
7. [NestJS Official Docs](https://nestjs.com/)
8. [Elysia Framework](https://elysiajs.com/)
9. [tRPC Official](https://trpc.io/)
10. [Koa Middleware Framework](https://koajs.com/)
11. [AdonisJS Documentation](https://adonisjs.com/)
12. [Nitro Server Engine](https://nitro.build/)

### Benchmark & Comparison Articles
- [Fastify Benchmarks](https://fastify.dev/benchmarks/)
- [Hono vs Fastify (Better Stack)](https://betterstack.com/community/guides/scaling-nodejs/hono-vs-fastify/)
- [Node.js Framework Benchmarks 2025 (Medium)](https://medium.com/@louisbertson/benchmarking-node-js-frameworks-choose-your-framework-for-2025-4a2fa089dcf3)
- [Bun vs Node.js 2025 (Strapi)](https://strapi.io/blog/bun-vs-nodejs-performance-comparison-guide)
- [Deno 2 Node Compatibility (The New Stack)](https://thenewstack.io/deno-2-arrives-with-long-term-support-node-js-compatibility/)

### Migration & Integration
- [Express 5 Migration Guide (ShubhaBlogs)](https://shubhadipbhowmik.vercel.app/blog/express-5-migration-guide/)
- [NestJS to tRPC Integration](https://www.nestjs-trpc.io/)
- [Nitro Standalone Usage (Vue School)](https://vueschool.io/lessons/unlocking-nitro-mystery-p2-what-is-nitro-to-nuxt)

---

## FINAL RECOMMENDATIONS BY CONTEXT

### Startup / MVP Speed
**→ Hono + Vercel** (edge-first, type-safe, multi-platform out of box)

### Existing Express Shop → Modernize
**→ Express 5** (stay put, get fixes) **or Fastify** (3x perf, measured migration path)

### Enterprise Monorepo / Microservices
**→ NestJS 10** (DDD patterns, testing, enterprise maturity) **+ tRPC** (type-safe client)

### Bun Greenfield / Type Safety Obsessed
**→ Elysia + Bun** (fastest validation, native types, Eden Treaty client gen)

### Public REST API / Mobile Backend
**→ Fastify** (stable, performant) **or AdonisJS** (full-featured, Laravel-like)

### Full-Stack Nuxt / Next.js + Backend
**→ Nitro** (Nuxt) **or tRPC + Fastify** (Next.js monorepo)

---

**Last Updated:** February 2026
**Next Review:** Q2 2026 (Node 24 LTS candidates, Bun 1.3+ stability, Deno 2.1 features)

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->

---
## Related References
- [Background Jobs & Events](./50-background-jobs-events.md) — BullMQ, Temporal, event-driven patterns
- [API Design Patterns](./26-api-design-patterns.md) — REST, GraphQL, tRPC, gRPC comparison
- [Testing Strategies](./53-testing-strategies.md) — Node.js testing: Vitest, Playwright, k6
- [Monorepo Tooling](./49-monorepo-dx-tooling.md) — Turborepo, pnpm workspaces for Node.js
