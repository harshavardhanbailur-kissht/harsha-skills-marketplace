# Performance Benchmarks Quick Reference 2025-2026

## Runtime Performance (Requests Per Second)

```
JavaScript Runtimes (HTTP Throughput):
  Bun 1.2+:    30,000-52,000 RPS  ⭐⭐⭐⭐⭐ (2-3.5x Node)
  Deno 2.x:    22,000-29,000 RPS  ⭐⭐⭐⭐   (1.5-2.2x Node)
  Node.js 22:  13,000-20,000 RPS  ⭐⭐⭐     (Baseline)

Web Frameworks (on Node.js):
  Encore.ts:   1st (9x faster than Express)
  Elysia:      2nd (4x faster)
  Hono:        3rd (3x faster, 40% less memory)
  Fastify:     4th (2.3x faster, 30% less memory)
  Express:     Baseline
```

## Frontend Framework Performance

```
Lighthouse Scores & Bundle Size:

SolidJS:    98 Lighthouse | 7KB bundle   | 42.8 ops/sec | ⭐ Best
Svelte 5:   96 Lighthouse | 15-20KB      | 38+ ops/sec  | ⭐
Vue 4:      94 Lighthouse | 25-30KB      | 35+ ops/sec  | ⭐
React 19:   88 Lighthouse | 72KB         | 28.4 ops/sec |
Angular:    85 Lighthouse | 80+KB        | —            |
```

## Framework Build Performance

```
Build Time Comparison (Production):

Rspack:         0.087-0.974s   ⭐⭐⭐⭐⭐
esbuild:        Fastest        ⭐⭐⭐⭐⭐
Turbopack:      <1s (HMR <10ms)⭐⭐⭐⭐
Vite 6:         0.446-5.772s   ⭐⭐⭐

Full-Stack Build Performance:

SvelteKit:      Incredibly fast    ⭐⭐⭐⭐⭐
Remix:          Fast               ⭐⭐⭐⭐
Next.js 15:     Variable           ⭐⭐⭐
Astro:          Slow (10k+ routes) ⭐⭐
```

## TTFB (Time to First Byte)

```
Remix:           136ms    ⭐⭐⭐⭐⭐
SvelteKit:       100-200ms⭐⭐⭐⭐⭐
Nuxt 3:          438ms    ⭐⭐⭐
Astro (static):  <500ms   ⭐⭐⭐⭐
Next.js 15:      150-300ms⭐⭐⭐⭐
```

## Database/ORM Performance

```
Query Latency (Simple queries):
All modern ORMs: Similar (single-digit ms difference)

Complex Joins:
Drizzle:  14x faster (single SQL vs N+1)
Prisma:   Standard (good DX)
TypeORM:  Depends on optimization

Bundle Size:
Drizzle:  7KB    (zero dependencies)  ⭐⭐⭐⭐⭐
Kysely:   Small  (SQL-first)          ⭐⭐⭐⭐
Prisma:   Larger (Rust engine)        ⭐⭐⭐
```

## PostgreSQL Connection Poolers

```
Latency:       PgCat > PgBouncer ≈ Supavisor
Throughput:    PgCat: 59K tps (best)
CPU Efficiency:PgCat (multi-threaded)

Recommendation:
- Simple:      PgBouncer (proven, single-threaded)
- Scale:       PgCat (multi-threaded)
- SaaS:        Supavisor (multi-tenancy)
```

## Edge Function Performance

```
Cold Start Time:

Cloudflare Workers:   <5ms      ⭐⭐⭐⭐⭐
Vercel Edge:          10-50ms   ⭐⭐⭐⭐
Deno Deploy:          10-30ms   ⭐⭐⭐⭐
Fastly Compute:       Variable  ⭐⭐⭐

Global Latency (P50):
Cloudflare:  10-30ms (300+ PoP)
Vercel:      10-30ms (region-dependent)
Deno Deploy: Slightly higher
```

## TypeScript Compilation

```
Speed Relative to tsc (baseline):

Oxc:    40x faster (parsing/transpiling)   ⭐⭐⭐⭐⭐
SWC:    10x faster (transpiling)           ⭐⭐⭐⭐
tsc:    Baseline (full type checking)      ⭐⭐⭐
Babel:  1/20th of Oxc                      ⭐

Bundle Size:
Oxc:    2MB        ⭐⭐⭐⭐⭐
SWC:    37MB       ⭐⭐⭐
Babel:  170 packages
```

## CSS Framework Performance

```
Bundle Size & Type Safety:

Tailwind 4:     Small bundle | Limited types    | Fast
StyleX:         Tiny bundle  | Good types      | Fast
Panda CSS:      Medium       | Excellent types | Moderate
Vanilla-Extract:Small        | Excellent types | Moderate
```

## Image Optimization

```
Speed (Fast to Slow):

Sharp:     Fastest (libvips-backed)    ⭐⭐⭐⭐⭐
Squoosh:   50% slower (pure Node)      ⭐⭐⭐
Next/image:Hybrid (Sharp + Squoosh)    ⭐⭐⭐⭐
Cloudflare Images: CDN-managed         ⭐⭐⭐⭐

Quality & Compression:
AVIF:      25-35% smaller than WebP
WebP:      25-30% smaller than JPEG
JPEG:      Universal support
```

## Recommended Stacks (2025-2026)

### Performance-First Stack
- Runtime: Bun
- Web Framework: Elysia
- Frontend: SolidJS
- Build tool: Turbopack
- ORM: Drizzle
- CSS: StyleX or Vanilla-Extract

### Balanced (Ecosystem + Performance)
- Runtime: Node.js 22
- Web Framework: Fastify/Hono
- Frontend: React 19
- Meta-framework: Next.js 15
- Build tool: Vite 6
- ORM: Prisma
- CSS: Tailwind 4

### Enterprise-Safe Stack
- Runtime: Node.js 22
- Web Framework: Fastify
- Frontend: React 19
- Meta-framework: Next.js 15
- ORM: Prisma
- CSS: Tailwind 4
- DB pooler: PgBouncer

## Key Insights

1. **3-5x Performance Gaps Exist:** Between fastest (Bun/SolidJS) and standard (Node/React)
2. **Rust Tools Win:** SWC/Oxc/Turbopack show consistent 10-40x performance improvements
3. **Ecosystem Trade-offs:** React/Node ecosystem often worth the performance hit
4. **Cold Start Critical:** Edge functions under 5ms (Cloudflare) vs 50+ (older serverless)
5. **Type Safety Trend:** SolidJS, TypeScript ORMs, CSS-in-JS with types gaining adoption
6. **Zero-Runtime Movement:** StyleX, Vanilla-Extract, Panda CSS showing build-time extraction preference

## Version Notes

- Node.js: Testing was 22.x latest
- React: 19.x benchmarks
- TypeScript: 5.x+ (SWC comparisons assume transpile-only)
- PostgreSQL: 17/18 performance tested
- All data from March 2026 searches

---

**Use this reference for quick lookups during architecture decisions.**
