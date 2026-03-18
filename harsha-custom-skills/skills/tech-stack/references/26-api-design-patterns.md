# API Design Patterns: Comprehensive Tech Stack Guide (2025-2026)

**Last Updated:** February 2026
**Research Scope:** REST, GraphQL, tRPC, gRPC, gRPC-Web, OpenAPI, Hono RPC
**Focus:** Production readiness, real-world patterns, decision logic

---

## Executive Summary

The API landscape in 2025-2026 reflects a **specialization trend** rather than winner-take-all consolidation:

- **REST**: Still dominant (85% of Android apps), best for simple CRUD and public APIs
- **GraphQL**: Maturing (61% enterprise adoption), excels with complex data shapes
- **tRPC**: Rising for monolithic full-stack TypeScript apps, eliminates schema friction
- **gRPC**: Penetrating microservices/AI pipelines, benchmarks show 10x performance gains
- **OpenAPI 3.2**: Newly released, solving REST tooling gaps
- **Hono RPC**: Edge-native alternative to tRPC for serverless

**2025 Verdict:** Hybrid approach dominates. Netflix uses gRPC + GraphQL + REST depending on layer.

---

## 1. REST API (Representational State Transfer)

### Best For
- Public/third-party APIs (cannot enforce TypeScript on consumers)
- Simple CRUD operations with stable schemas
- Ecosystem maturity: 30+ years of industry standards
- Maximum HTTP caching efficiency (browser, CDN, middleware)
- Backend-to-backend integration in polyglot teams
- Mobile apps with predictable data needs

### Performance Characteristics
- **Latency**: ~250ms baseline (typical benchmark)
- **Bandwidth**: 25-30% larger payloads than gRPC (JSON overhead)
- **Caching**: Native HTTP GET caching, CDN-friendly by design
- **Scalability**: Excellent at scale when properly cached
- **Trade-off**: Simple requests fast, complex data relationships require multiple round-trips (N+1 queries)

### Type Safety & Code Generation

| Tool | Approach | 2025 Status |
|------|----------|-----------|
| OpenAPI 3.2 | Code-first or schema-first generation | Newly released, improved |
| Fern | OpenAPI → SDKs in 10+ languages | Enterprise-grade, Stripe uses |
| oRPC | TypeScript + OpenAPI bridge | v1.0 released Dec 2025 |
| ts-rest | Contract-first TypeScript | Growing adoption |

**Limitation**: Type information doesn't flow unless you use external tools. Runtime validation required for safety.

### Tooling & Development Experience

- **API Design**: Postman, Insomnia, SwaggerUI
- **Documentation**: OpenAPI 3.2, Swagger
- **Testing**: Jest, Supertest, REST Client extensions
- **Monitoring**: Generic HTTP tools (curl, Network tabs)
- **Mock Servers**: Prism, Mirage JS

**2025 Trend**: REST frameworks adding automatic OpenAPI generation (FastAPI model).

### Learning Curve
- **HTTP basics**: 1-2 weeks for junior developers
- **RESTful design principles**: 2-4 weeks to master
- **Production considerations** (caching, versioning, errors): 2-3 months
- **Enterprise adoption**: Fastest (existing team knowledge)

### Client Libraries
- Language agnostic (curl, fetch, axios, requests, etc.)
- No special runtime required
- Downside: No type safety without code generation

### Caching Strategy
**CDN-Friendly**: YES (native HTTP GET caching)

**Optimal Pattern**:
```
GET /api/users/123         → Cache-Control: public, max-age=3600
GET /api/users/123/posts   → Cache-Control: public, max-age=300
POST /api/posts            → Cache-Control: no-cache (mutations)
```

**2025 Benchmarks**:
- 83% of enterprises use HTTP/2 or HTTP/3
- Brotli compression achieves 25% smaller payloads than gzip
- ETag + 304 responses reduce bandwidth significantly

### File Uploads
**Native Support**: YES (multipart/form-data)

Simple and battle-tested:
```
POST /api/uploads
Content-Type: multipart/form-data

[binary file data]
```

**Production Pattern**: Direct S3 upload via pre-signed URLs to avoid server bottleneck.

### Real-Time Capabilities
**Subscriptions**: NOT native
- Polling (inefficient, 1-5s latency)
- WebSocket upgrade (separate protocol, not RESTful)
- Server-Sent Events (push, one-way)

**2025 Verdict**: Separate concern from REST. Use WebSocket or SSE layer.

### Versioning Strategies
- URL path: `/api/v2/users`
- Accept header: `Accept: application/vnd.api+json;version=2`
- Domain: `api-v2.example.com`

### REST + Mobile Optimization (2025)
- **Advantage**: Stable endpoints, simple caching
- **Disadvantage**: Over-fetching; 85% of Android apps still use REST despite alternatives
- **Pattern**: Separate mobile endpoints for lightweight responses

---

## 2. GraphQL

### Best For
- Complex, interconnected data models (e.g., Shopify product catalog)
- Multiple client shapes from single backend (web vs mobile vs TV)
- Real-time collaborative features (docs, comments, presence)
- Internal APIs with sophisticated query requirements
- **NOT**: Simple CRUD, public third-party APIs, strict caching needs

### Performance Characteristics
- **Latency**: 15-30% faster than REST for complex queries (reduced round-trips)
- **Bandwidth**: 30-50% less data transferred (precise selection)
- **Mobile**: 60% reduction in data usage (GitHub case study)
- **Trade-off**: Single POST request prevents HTTP caching; complexity limits DoS protection

**2025 Benchmarks**:
- REST responses 340% larger than GraphQL for same data
- 61% enterprise adoption (up from 30% in 2023)

### Type Safety & Code Generation

**Strongly Typed**: Schema-driven, generates TS/JS types automatically

Tools:
- **Apollo Client**: Full type generation from introspection
- **Relay**: Compile-time query validation
- **TypeGraphQL**: Code-first SDL generation
- **GraphQL Code Generator**: 20+ language support

**Advantage**: Caught type errors at compile time (unlike REST).

### Tooling & Development Experience

- **Query IDE**: Apollo Sandbox, GraphiQL, GraphQL Playground
- **Schema Design**: Apollo Studio, GraphQL Code Generator
- **Testing**: Jest, Cypress, Testing Library
- **Monitoring**: Apollo Observability, DataDog, New Relic
- **Mock**: GraphQL Mock Service Worker, Faker

**2025 Maturity**: Enterprise tooling excellent; learning curve steeper.

### Learning Curve
- **GraphQL concepts**: 1-2 weeks (queries, mutations, subscriptions)
- **Schema design patterns**: 3-4 weeks
- **Performance & N+1 prevention**: 2-3 months
- **Enterprise adoption**: 6-12 weeks (bigger team ramp-up)

**Barrier**: Understanding `resolvers` and `batch loaders` for optimization.

### Client Libraries
- **JavaScript**: Apollo Client, Urql, SWR + GraphQL
- **React**: TanStack Query + graphql-request
- **Mobile**: Apollo for iOS/Android
- **Language agnostic**: Yes, any language

**Advantage**: Type safety across language boundaries with code generation.

### Caching Strategy
**CDN-Friendly**: PARTIAL (with workarounds)

**Native Problem**: All queries POST → no HTTP GET caching

**2025 Solutions**:

1. **Persisted Queries** (Recommended):
   - Replace full query with short hash
   - `POST /graphql?extensions={"persistedQuery":{"sha256Hash":"abcd1234"}}`
   - Enables CDN caching by query hash
   - Saves 30% bandwidth, increases cache hit to 85%+

2. **GET Queries for Reading**:
   - Encode query in URL hash: `/graphql?query=...`
   - Allows browser/CDN caching
   - Limited by URL length (~2KB)

3. **Edge Caching**:
   - Hash request body (SHA256) as cache key
   - Cloudflare, Fastly, WunderGraph support
   - Cache-Control: `public, max-age=60` with mutation purging

4. **Static Query Patterns**:
   - Most frontends query same fields repeatedly
   - Cache entire result per query + variables
   - Similar to REST endpoint caching

**2025 Recommendation**: Persisted queries + edge cache = production-grade.

### File Uploads
**Not Native**: Requires extension

**Pattern 1 - Pre-signed URLs** (preferred):
```graphql
mutation {
  getUploadUrl {
    url
    fields
  }
}
```
Then POST directly to S3.

**Pattern 2 - Multipart Upload**:
```graphql
mutation($file: Upload!) {
  uploadFile(file: $file) {
    id
    url
  }
}
```
Uses `graphql-upload` middleware. Simpler but slower.

### Real-Time Capabilities
**Subscriptions**: YES (native)

**Transports**:
- **WebSocket**: Full bidirectional, most common
- **SSE**: Simpler, stateless, HTTP-friendly
- **Long polling**: Legacy, not recommended

**2025 Pattern** - Subscriptions over SSE:
```graphql
subscription {
  postAdded {
    id
    title
    author { name }
  }
}
```

**Scalability Challenge**: Subscriptions require stateful connections. Solutions:
- Redis pub/sub for multi-instance
- Ably.com for managed subscriptions
- Apollo Federation with GraphQL Gateway

### GraphQL Subscriptions vs REST Alternatives
- **Better than**: REST polling (instant updates)
- **vs WebSocket**: GraphQL adds type safety, structured queries
- **vs tRPC SSE**: Similar performance, less TypeScript coupling

---

## 3. tRPC (TypeScript Remote Procedure Call)

### Philosophy
**"RPC + Inference = Type Safety Without Schema"**

Eliminates the gap between server code and client code through shared TypeScript types.

### Best For
- **Internal full-stack monorepos** (React + Next.js/Node backend)
- **TypeScript-only teams**
- **Rapid iteration** (schema friction eliminated)
- **Startups/scale-ups** (teams < 50 engineers)
- **Replacing lightweight GraphQL** usage in single-org contexts
- **NOT**: Public APIs, polyglot teams, multi-org consumption

### Performance Characteristics
- **Latency**: 5-10% faster than REST (binary optional, no schema parsing)
- **Bandwidth**: Similar to REST (JSON default, but can stream binary)
- **Throughput**: Batching via httpBatchStreamLink
- **Real-time**: SSE subscriptions (new in v11), WebSocket support

**v11 2025 Features**:
- Non-JSON data (FormData, Blob, File, Uint8Array)
- HTTP Batch Stream Link (streaming responses)
- SSE Subscriptions (simpler than WebSocket)
- Simplified router syntax

### Type Safety & Code Generation
**Zero Code Generation**: Types inferred at compile time

**How it Works**:
```typescript
// Server
export const appRouter = {
  user: { get: publicProcedure.input(z.string()).query(async (opts) => {...}) }
};

// Client (automatic)
type AppRouter = typeof appRouter;
const client = createTRPCClient<AppRouter>({...});

client.user.get("123"); // ✅ TypeScript knows exact return type
```

**Advantage**: Breaking changes caught at compile time across full stack.

### Tooling & Development Experience
- **Type Inference**: Built into TypeScript compiler
- **Testing**: Works with Jest, Vitest (type-safe helpers)
- **Dev Experience**: Hot reload in Next.js built-in
- **Debugging**: Standard TS source maps
- **Documentation**: Auto-generated from type signatures

**Limitation**: IDE support lags GraphQL tooling (no dedicated IDEs).

### Learning Curve
- **Basic tRPC setup**: 2-3 days
- **Procedures + validation**: 1 week
- **Middleware + auth**: 2 weeks
- **Real-time subscriptions**: 3-4 weeks
- **Team adoption**: Fast if TypeScript competency exists (1-2 weeks)

### Client Libraries
- **React**: `@trpc/react-query` (v5 with Suspense support in v11)
- **Next.js**: Native integration
- **Vue**: `@trpc/vue-query`
- **Svelte**: `@trpc/sveltekit`
- **Node.js**: Direct procedure calls (no network overhead)

**2025 Change**: Full TanStack React Query v5 integration → Suspense support

### Caching Strategy
**Not Built-in**: Relies on TanStack Query

**Pattern**:
```typescript
const { data } = trpc.user.get.useQuery(id, {
  staleTime: 1000 * 60 * 5, // 5 minutes
});
```

**CDN-Friendly**: NO (JSON POST, custom protocol)

**Workaround for public APIs**:
- Expose REST layer alongside tRPC (common pattern)
- Cache at application layer (TanStack Query)
- Not suitable for browser caching

### File Uploads
**v11 Native Support**: YES (FormData, File, Blob)

**Pattern**:
```typescript
export const appRouter = {
  uploadFile: publicProcedure
    .input(z.instanceof(File))
    .mutation(async ({ input: file }) => {
      // Handle file
      return { success: true };
    })
};
```

**Preferred**: Pre-signed S3 URLs via tRPC endpoint.

### Real-Time Capabilities
**Subscriptions**: YES (new in v11)

**Transports**:
- **SSE**: Recommended (simpler, stateless, HTTP-friendly)
- **WebSocket**: Full bidirectional

**SSE Example**:
```typescript
export const appRouter = {
  onPostAdded: publicProcedure.subscription(() => {
    return observable(emit => {
      const unsub = db.posts.subscribe(post => emit.next(post));
      return unsub;
    });
  })
};
```

**Advantage over GraphQL subscriptions**: Less infrastructure complexity, same type safety.

### tRPC + Next.js Pattern (2025)
**Monolithic Full-Stack Architecture**:

```
app/
├── api/
│   ├── trpc/
│   │   └── [trpc].ts           # Catch-all tRPC route
│   └── uploadFile.ts           # Multipart handler (non-tRPC)
├── components/
│   └── UserList.tsx            # useQuery hook
└── server/
    └── routers/
        └── user.ts             # Procedures
```

**Why Next.js + tRPC Dominates 2025**:
1. Zero API contract friction
2. Deploy entire stack as one unit (Vercel)
3. Type safety end-to-end
4. Server Functions eliminate some API layers
5. ISR/SSG with co-located data fetching

**Migration Path**: REST layer for public API, tRPC internally.

### When tRPC Eliminates REST/GraphQL

**Use tRPC Instead of REST** when:
- ✅ Monorepo, internal API
- ✅ Team is TypeScript-native
- ✅ No third-party consumers
- ✅ Rapid iteration priority
- ❌ Public API → use REST + OpenAPI
- ❌ Multi-org consumption → use GraphQL + federation

**Use tRPC Instead of GraphQL** when:
- ✅ Single shape per client (not multi-client)
- ✅ No federation needs
- ✅ Simpler schema sufficient
- ❌ Complex interconnected data → GraphQL better
- ❌ Strict caching requirements → GraphQL+persisted queries better

---

## 4. gRPC

### Best For
- **Microservices** (service-to-service, not browser clients)
- **Real-time streaming** (video, audio, data pipelines)
- **High-performance** systems (finance, trading, metrics)
- **Polyglot teams** (Go, Python, Java, Rust all equal)
- **Mobile apps** (via gRPC-Web proxy)
- **NOT**: Browser clients directly, simple CRUD

### Performance Characteristics
- **Latency**: 5-25ms vs 250ms REST (25-50x faster)
- **Bandwidth**: 30-50% smaller (Protocol Buffers binary)
- **Throughput**: HTTP/2 multiplexing, 100x connections per socket
- **CPU**: 65% less server CPU than REST

**2025 Benchmarks**:
- 1 KB payload: 5.5× faster
- 100 KB payload: 8.5× faster
- 1 MB payload: 10× faster

### Type Safety & Code Generation
**Strong**: Protocol Buffers schema enforced

**Workflow**:
```protobuf
// user.proto
service UserService {
  rpc GetUser(UserId) returns (User);
}

message User {
  string id = 1;
  string name = 2;
}
```

**Code Gen**: `protoc` generates stubs in Go, Java, Python, Node.js, etc.

**Advantage**: Schema is language-agnostic, supports 10+ languages equally.

### Tooling & Development Experience
- **Schema Design**: Protocol Buffers (third-generation, mature)
- **Code Generation**: Built-in `protoc`
- **IDEs**: Full support in VSCode, IntelliJ (gRPC plugin)
- **Debugging**: gRPCurl (curl for gRPC), Postman (beta gRPC support)
- **Testing**: testdata.pb, table-driven tests

**Limitation**: Human-readable formats harder (use gRPCurl, not browser).

### Learning Curve
- **Protobuf syntax**: 1 week
- **gRPC service design**: 2-3 weeks
- **Streaming patterns**: 2-3 weeks
- **Interceptors & middleware**: 3-4 weeks
- **Team adoption**: Moderate (new paradigm, tool learning)

### Client Libraries
- **Go**: `grpc-go` (official, most mature)
- **Python**: `grpcio` (excellent)
- **Node.js**: `@grpc/grpc-js` (native, no C++ bindings required)
- **Java**: `grpc-java`
- **Rust**: `tonic`
- **Web browsers**: gRPC-Web (proxy required)

**Advantage**: Identical API across languages.

### Caching Strategy
**Not Native**: HTTP/2 semantics don't map to traditional caching

**Workarounds**:
- Application-level caching (Redis)
- Protocol Buffer etag in request/response
- Streaming, not caching (preferred pattern)

**CDN-Friendly**: NO (custom protocol)

### File Uploads
**Native Support**: YES (client streaming)

**Pattern**:
```protobuf
service FileService {
  rpc Upload(stream FileChunk) returns (UploadResponse);
}

message FileChunk {
  bytes data = 1;
  int32 sequence = 2;
}
```

**Advantage**: Efficient chunking, backpressure control built-in.

### Real-Time Capabilities
**Subscriptions**: YES (streaming)

**Types**:
- **Server streaming**: Server pushes updates
- **Client streaming**: Client sends multiple messages
- **Bidirectional streaming**: Full duplex

**Example** - Real-time metrics:
```protobuf
service MetricsService {
  rpc Subscribe(SubscribeRequest) returns (stream Metric);
}
```

**Scalability**: Stateful connections, handled via interceptors.

### gRPC-Web (Browser Support)
**Requirement**: Proxy translator (Envoy, gRPC-Web server)

**Why**: HTTP/2 not supported in browsers, proxy translates HTTP/1.1 → HTTP/2 → gRPC.

**2025 Status**:
- Protobuf 27.1 with modernized codegen
- TypeScript support native
- Interceptors for auth/retry
- Still requires proxy deployment (unlike REST)

**Limitation**: Unary calls only (no client/bidirectional streaming).

---

## 5. gRPC-Web (Browser Clients)

### Best For
- **Browser-based gRPC** clients (React, Vue, Angular)
- **Type-safe web frontends** consuming internal gRPC services
- **Monorepos** with shared Protobuf schemas
- **High-performance web apps**

### Performance vs REST
- **Same 5-25ms baseline** as server-side gRPC (wire format benefit)
- **Proxy overhead**: +5-10ms for Envoy translation
- **Net effect**: Still 10× faster than REST for large payloads

### Deployment Architecture
```
Browser
  ↓ (HTTP/1.1)
Envoy Proxy (gRPC-Web translator)
  ↓ (HTTP/2)
gRPC Backend Services
```

**Common Setup**: Kubernetes Envoy sidecar, Docker compose with Envoy service.

### Learning Curve
- **Protobuf + gRPC basics**: 3-4 weeks
- **gRPC-Web integration**: 1 week
- **Proxy configuration (Envoy)**: 2-3 weeks (infrastructure concern)

### Limitations (2025)
- ❌ Client streaming not supported
- ❌ Bidirectional streaming not supported
- ✅ Server streaming supported
- ✅ Unary (request/response) supported
- ✅ Custom interceptors supported

**Verdict**: Good for RPC-style APIs, poor for event streaming from browser.

---

## 6. OpenAPI 3.2 (2025 Release)

### Purpose
**Schema-first REST documentation & code generation** standard.

### What Changed in 3.2 (Latest 2025)

| Feature | Impact |
|---------|--------|
| OAuth 2.0 Device Flow | IoT, limited input devices |
| QUERY HTTP method | Safe queries with payload |
| Webhook descriptions | Event-driven APIs |
| Improved tag structure | Taxonomy support, nesting |
| Streaming media types | Server-Sent Events native |

### Best For
- **Public REST APIs** requiring documentation
- **Enterprise API governance** (schema registry)
- **Code generation** in multiple languages
- **Third-party consumption** (auto-generate SDKs)

### Type Safety & Code Generation

**Code Generators** (2025):
- **Fern**: Stripe-quality SDKs (10+ languages)
- **OpenAPI.NET v3**: Full 3.2 support
- **openapi-generator**: Widely used, 50+ language support

**Workflow**:
1. Define OpenAPI 3.2 schema
2. Run code gen → SDKs auto-generated
3. Consume in client code (type-safe)

### Caching & Mobile
**CDN-Friendly**: YES (REST-based)

**Mobile Optimization**: Define separate endpoints:
```yaml
/api/user:
  summary: Full user object

/api/user/summary:
  summary: Lightweight version for mobile
```

---

## 7. Hono RPC

### Philosophy
**"tRPC for Edge"** - TypeScript type-safe RPC for serverless/edge platforms.

### Best For
- **Edge computing** (Cloudflare Workers, AWS Lambda@Edge)
- **Serverless** (Vercel, AWS Lambda)
- **Type-safe APIs** without heavy frameworks
- **Monorepos** (like tRPC)
- **NOT**: Long-running processes, WebSocket-heavy apps

### Performance
- **Cold starts**: Minimal (lightweight)
- **Latency**: Similar to tRPC (HTTP-based)
- **Deployment**: 50MB bundles (lean)

### Type Safety & Code Generation
**Zero Code Generation**: Like tRPC, types inferred

**RPC Pattern**:
```typescript
// Server
export const app = new Hono().post('/api/user/:id', async (c) => {
  return c.json(await getUser(c.req.param('id')));
});

// Client
const client = hc<typeof app>('https://example.com');
const user = await client.api.user[id].$get();
```

### Learning Curve
- **Basic setup**: 1-2 days
- **Middleware, validators**: 1 week
- **Team adoption**: Very fast (familiar for tRPC users)

### Integration with Full-Stack Frameworks
- **Next.js**: Full support via API routes
- **SvelteKit**: Excellent integration
- **TanStack**: Works seamlessly
- **Monorepos**: TypeScript project references

### When to Choose Hono RPC over tRPC
- ✅ Serverless-first, edge computing
- ✅ Minimal bundle size required
- ✅ Multi-framework support needed
- ❌ Long-running connections → tRPC better
- ❌ Complex subscriptions → tRPC better

---

## Comparison Matrix (2025)

| Dimension | REST | GraphQL | tRPC | gRPC | Hono RPC |
|-----------|------|---------|------|------|----------|
| **Latency** | ~250ms | ~200ms | ~100ms | ~15ms | ~100ms |
| **Bandwidth** | 100% | 70% | 100% | 50% | 100% |
| **Type Safety** | Via codegen | Native schema | Native TypeScript | Protobuf | Native TypeScript |
| **Learning Curve** | 2-3 weeks | 4-6 weeks | 1-2 weeks | 4-6 weeks | 1-2 weeks |
| **CDN Caching** | ✅ Native | ⚠ Persisted queries | ❌ Custom only | ❌ Application | ❌ Custom only |
| **File Uploads** | ✅ multipart | ⚠ via extension | ✅ v11 native | ✅ streaming | ✅ FormData |
| **Real-Time** | ⚠ Polling/WebSocket | ✅ Subscriptions | ✅ SSE/WebSocket (v11) | ✅ Streaming | ⚠ Limited |
| **Public APIs** | ✅ Best | ✅ Good | ❌ No | ⚠ Proxy needed | ❌ No |
| **Polyglot** | ✅ Excellent | ✅ Excellent | ❌ TypeScript only | ✅ Excellent | ❌ TypeScript only |
| **Mobile** | ✅ Good | ✅ Best (60% savings) | ⚠ No native | ✅ Via gRPC-Web | ⚠ No native |

---

## Decision Logic (2025 Framework)

### DECISION TREE

```
START
│
├─ Is API public/multi-org?
│  ├─ YES → GraphQL (federation path) or REST + OpenAPI 3.2
│  │         └─ Complex data shapes? → GraphQL
│  │         └─ Simple CRUD? → REST
│  │
│  └─ NO (internal only)
│     ├─ Full-stack TypeScript monorepo?
│     │  ├─ YES → tRPC (if traditional server)
│     │  │        or Hono RPC (if edge/serverless)
│     │  │
│     │  └─ NO → Polyglot (Go, Python, Rust)?
│     │     ├─ YES, high-performance? → gRPC
│     │     ├─ YES, simple? → REST
│     │     └─ NO → tRPC
│     │
│     └─ Real-time requirements?
│        ├─ Heavy streaming? → gRPC, gRPC-Web
│        ├─ Chat/subscriptions? → GraphQL or tRPC v11
│        └─ Occasional updates? → tRPC v11 SSE

END
```

### IF/THEN Decision Rules

**Rule 1: Third-Party Consumers Exist**
- IF third-party developers must consume API
- THEN use REST + OpenAPI 3.2 (or GraphQL for complex data)
- ELSE use tRPC/Hono RPC (TypeScript) or gRPC (polyglot)

**Rule 2: Performance Critical (Latency < 50ms)**
- IF latency requirement < 50ms
- THEN use gRPC (or tRPC/Hono for TypeScript monorepo)
- ELSE REST acceptable

**Rule 3: Complex, Interconnected Data Model**
- IF schema involves 5+ deeply nested types
- THEN use GraphQL (query flexibility) or tRPC (monorepo alternative)
- ELSE REST acceptable

**Rule 4: Mobile App Primary Consumer**
- IF mobile data usage is concern
- THEN use GraphQL (60% bandwidth savings) or tRPC
- ELSE REST adequate

**Rule 5: Caching Critical (e.g., CDN requirement)**
- IF response caching across global CDN required
- THEN use REST (native HTTP caching)
- ELSE GraphQL (persisted queries) or tRPC (application layer)

**Rule 6: TypeScript Monorepo**
- IF entire codebase TypeScript, single team
- THEN tRPC (traditional) or Hono RPC (serverless/edge)
- ELSE gRPC (polyglot) or REST (simplest)

**Rule 7: Real-Time Subscriptions**
- IF subscriptions required
- THEN GraphQL (mature) or tRPC v11 (simpler)
- ELSE REST adequate

**Rule 8: File Uploads**
- IF native file upload support required
- THEN REST or tRPC v11 (FormData native)
- ELSE use pre-signed URLs (S3, GCS) + metadata endpoint

---

## Production Patterns (2025)

### Pattern 1: Hybrid Lambda + gRPC
**Use Case**: AI pipelines, high-frequency trading, media processing

```
Frontend (React)
  ↓ (HTTP)
Lambda/Container (REST/GraphQL gateway)
  ↓ (gRPC, HTTP/2)
gRPC microservices (Go, Rust backends)
  ↓
Async queue (Kafka, SQS)
  ↓
Background workers
```

### Pattern 2: Next.js + tRPC + Stripe
**Use Case**: Startups, e-commerce, SaaS

```
Next.js App
├─ App Router (/app/page.tsx)
├─ tRPC routes (/api/trpc/[trpc].ts)
├─ Separate REST layer for webhooks (/api/webhooks/stripe)
└─ Server components (RSC)
```

### Pattern 3: GraphQL Federation + REST
**Use Case**: Large enterprises, multi-team

```
GraphQL Apollo Gateway
├─ User subgraph (REST → GraphQL adapter)
├─ Product subgraph (gRPC → GraphQL adapter)
└─ Order subgraph (tRPC → GraphQL adapter)
```

### Pattern 4: Edge + Hono RPC
**Use Case**: Edge computing, Cloudflare Workers

```
Cloudflare Worker (Hono RPC)
  ├─ Authentication (JWT validation)
  ├─ Rate limiting
  └─ Route to origin or cache
```

---

## 2025-2026 Trends

1. **Hybrid approaches dominate**: 43% of teams use multiple patterns
   - Netflix: gRPC (video) + GraphQL (recommendations) + REST (auth)
   - Shopify: GraphQL + REST endpoints
   - GitHub: GraphQL + REST (legacy compatibility)

2. **Type safety becomes table-stakes**:
   - Code generation standard for REST (OpenAPI)
   - tRPC adoption rising in TypeScript teams
   - Protobuf parity in other languages

3. **Edge computing reshapes API design**:
   - Cloudflare Workers, Lambda@Edge
   - Hono RPC/tRPC gaining mindshare
   - Reduced latency requirements for home region

4. **AI agent consumption reshapes APIs**:
   - Structured outputs (OpenAPI) preferred
   - Function calling patterns (tRPC-like)
   - Real-time streaming (gRPC patterns)
   - Only 24% design APIs for agent consumption (adoption gap)

5. **Caching remains unsolved for dynamic APIs**:
   - GraphQL persisted queries maturing
   - REST still king for CDN efficiency
   - Application-layer caching growing

6. **Tooling convergence**:
   - Postman now supports gRPC
   - OpenAPI 3.2 adds gRPC-inspired features
   - One command generates SDKs (Fern, Buf)

---

## When NOT to Choose Each

### ❌ REST When:
- Complex, multi-client data shapes (too many endpoints)
- Real-time subscriptions required (use GraphQL/tRPC)
- Binary data common (use gRPC)
- Microservices with high latency sensitivity

### ❌ GraphQL When:
- Public third-party API (hard to reason about query costs)
- Caching critical without infrastructure (use REST)
- Simple CRUD operations (overkill)
- Team lacks query language expertise

### ❌ tRPC When:
- Public API required (use REST/GraphQL)
- Non-TypeScript team (use gRPC/REST)
- Strict OpenAPI compliance required (use REST)

### ❌ gRPC When:
- Browser clients primary (use gRPC-Web with proxy)
- Low-latency not critical (REST adequate)
- Simple API (high ceremony)
- Team unfamiliar with Protobuf

### ❌ Hono RPC When:
- Long-running connections required (use tRPC)
- Heavy WebSocket use (use Socket.io, tRPC)
- Non-edge deployment
- Multi-language consumers required

---

## Implementation Checklist (2025)

### For Production REST API
- [ ] OpenAPI 3.2 schema documented
- [ ] SDK auto-generation tested (Fern)
- [ ] Cache-Control headers set per endpoint
- [ ] ETag/304 support implemented
- [ ] Error standardization (RFC 7807)
- [ ] Rate limiting strategy defined

### For Production GraphQL
- [ ] Apollo Studio or equivalent observability
- [ ] Persisted queries + CDN caching configured
- [ ] Query depth limiting enforced
- [ ] N+1 query prevention (DataLoader)
- [ ] Subscription infrastructure scaled (Redis pub/sub or managed)
- [ ] Documentation (Apollo Sandbox, Spectaql)

### For Production tRPC
- [ ] TanStack Query configured
- [ ] Middleware auth/logging setup
- [ ] Validation (Zod) comprehensive
- [ ] File upload handling (pre-signed URLs or v11 FormData)
- [ ] Subscription transport chosen (SSE recommended)
- [ ] Type tests covering client/server

### For Production gRPC
- [ ] Protobuf v3+ schema finalized
- [ ] Interceptors for auth/observability
- [ ] Load balancing configured (K8s/LB)
- [ ] gRPC-Web proxy if browser support needed
- [ ] Health check services
- [ ] Observability (metrics, tracing)

### For Production Hono RPC
- [ ] Edge deployment tested (Cloudflare/AWS)
- [ ] Bundle size monitored
- [ ] Cold start performance profiled
- [ ] Middleware chain optimized
- [ ] Type safety via inference validated

---

## References & Sources

### tRPC v11 (2025)
- [Announcing tRPC v11 | tRPC](https://trpc.io/blog/announcing-trpc-v11)
- [tRPC Releases | GitHub](https://github.com/trpc/trpc/releases)
- [tRPC Migrate from v10 to v11](https://trpc.io/docs/migrate-from-v10-to-v11)
- [TanStack React Query Integration | tRPC](https://trpc.io/blog/introducing-tanstack-react-query-client)

### GraphQL 2025 State
- [GraphQL in 2025: Pros & Cons | Medium](https://medium.com/@ignatovich.dm/graphql-in-2025-pros-cons-public-apis-and-use-cases-part-1-1588cb9e9f9a)
- [Review of GraphQL in 2025 | Medium](https://medium.com/codex/review-of-graphql-in-2025-3e4a8b443785)
- [GraphQL Performance | GraphQL Org](https://graphql.org/learn/performance/)
- [GraphQL Caching Strategies | Apollo GraphQL](https://www.apollographql.com/blog/caching-graphql-results-in-your-cdn)
- [GraphQL vs REST for Mobile | API7.ai](https://api7.ai/blog/graphql-vs-rest-api-comparison-2025)

### OpenAPI & REST 2025
- [OpenAPI 3.2 Release](https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2)
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0.html)
- [REST API Best Practices 2025 | Hevo](https://hevodata.com/learn/rest-api-best-practices/)
- [Building High-Performance REST APIs | JSON Console](https://jsonconsole.com/blog/building-high-performance-restful-apis-json-complete-developer-guide-2025)

### gRPC & gRPC-Web 2025
- [gRPC Performance Overview](https://grpc.io/)
- [gRPC in 2025: Why Top Companies Are Switching | Medium](https://medium.com/@miantalha.t08/grpc-in-2025-why-top-companies-are-switching-from-rest-36e3c6e2ec4c)
- [gRPC-Web Latest Features | GitHub](https://github.com/grpc/grpc-web/releases)
- [gRPC with TypeScript in 2025 | Caisy Blog](https://caisy.io/blog/grpc-typescript)

### Hono RPC 2025
- [Hono RPC Guide | Hono](https://hono.dev/docs/guides/rpc)
- [Hono RPC Blog Post | Yusuke Wada](https://blog.yusu.ke/hono-rpc/)
- [Hono Stacks Overview | Hono](https://hono.dev/docs/concepts/stacks)

### Comparisons 2025
- [REST vs GraphQL vs gRPC | Design Gurus](https://www.designgurus.io/blog/rest-graphql-grpc-system-design)
- [gRPC vs REST vs GraphQL: Ultimate API Showdown | Medium](https://medium.com/@sharmapraveen91/grpc-vs-rest-vs-graphql-the-ultimate-api-showdown-for-2025-developers-188320b4dc35)
- [When to use GraphQL vs REST vs tRPC | WunderGraph](https://wundergraph.com/blog/graphql-vs-federation-vs-trpc-vs-rest-vs-grpc-vs-asyncapi-vs-webhooks)
- [Choosing Frontend API Weapon | Medium](https://medium.com/@hnwagba/choosing-your-frontend-api-weapon-rest-graphql-trpc-or-websocket-personal-rant-edition-b64854ed3f17)
- [tRPC vs GraphQL | LogRocket](https://blog.logrocket.com/trpc-vs-graphql-better-projects/)

### Type Safety & Code Generation 2025
- [OpenAPI Code Generation | Fern](https://beta.buildwithfern.com/post/openapi-code-generation-enterprise)
- [oRPC v1.0 with OpenAPI | InfoQ](https://www.infoq.com/news/2025/12/orpc-v1-typesafe/)
- [Top API Development Tools 2025 | Strapi](https://strapi.io/blog/top-api-development-tools-for-2025)
- [Type-Safe REST Clients in TypeScript | Toasting Code](https://toastingcode.com/posts/building-type-safe-rest-clients-in-typescript-proven-patterns-and-tools-for-enterprise-apis/)

---

## Related References
- [API Versioning, Pagination, Rate Limiting & Webhooks: 2025-2026 Reference](./58-api-versioning-webhooks.md) — Advanced API patterns and features
- [GraphQL Ecosystem, Federation, and Architecture Patterns Reference Guide](./59-graphql-federation.md) — Deep dive into GraphQL architecture
- [Backend Node.js/Bun/Deno: Runtimes & Frameworks](./04-backend-node.md) — Runtime choice for API implementation
- [Backend Go & Rust: Backend Frameworks (2025-2026)](./06-backend-go-rust.md) — Alternative languages for APIs
- [Security Essentials: Complete Tech-Stack Reference (2025-2026)](./30-security-essentials.md) — API security patterns and best practices

---

**Document Version**: 26.1
**Last Updated**: February 19, 2026
**Status**: Production Reference
**Scope**: 2025-2026 Production Systems

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->
