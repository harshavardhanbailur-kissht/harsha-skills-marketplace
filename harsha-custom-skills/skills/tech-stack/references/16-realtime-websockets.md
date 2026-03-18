# Real-Time Solutions Tech Stack Reference (2025/2026)

**Last Updated:** February 2026
**Research Scope:** Socket.io, Ably, Pusher, Supabase Realtime, Liveblocks, PartyKit, SSE, WebTransport

---
## Executive Summary
**TL;DR:** Socket.io dominates real-time with 65% market share but adds 40KB bundle weight. For modern apps: use native WebSocket API + Hono for simple cases, Ably/Pusher for managed infrastructure, Supabase Realtime for Postgres-backed sync, and Liveblocks for collaborative editing. SSE is the forgotten winner for one-way server push at 1/10th the complexity. WebTransport (HTTP/3) is the future but browser support is still limited.

---


## EXECUTIVE SUMMARY

### Decision Tree Overview

```
START: Need Real-Time Updates?
├─ Server-to-Client Only?
│  ├─ YES → Use SSE (99% of cases)
│  │  └─ Cheaper, simpler, lower latency for notifications/feeds
│  └─ NO → Continue below
│
├─ Bidirectional Communication?
│  ├─ Simple Chat/Updates → WebSocket
│  │  ├─ Managed? → Pusher / Ably
│  │  └─ Self-Hosted? → Socket.io
│  │
│  ├─ Collaborative Editing → CRDT Required
│  │  ├─ Turnkey Solution? → Liveblocks
│  │  ├─ Edge-First? → PartyKit (Cloudflare)
│  │  └─ DB-Native? → Supabase Realtime
│
├─ High Latency Critical (<50ms)?
│  ├─ YES → WebTransport (Chrome/Edge only)
│  └─ NO → Continue with WebSocket options
│
├─ Enterprise Scale (100k+ concurrent)?
│  ├─ Ably → Global edge, message guarantees
│  └─ Pusher → Regional, single region
│
└─ Budget Constraint?
   ├─ Minimal → Supabase (free tier)
   ├─ Moderate → Socket.io (self-hosted)
   └─ Growth → Ably > Pusher > Liveblocks
```

---

## SOLUTIONS DETAILED COMPARISON

### 1. Socket.IO

**Type:** Self-hosted WebSocket library
**Protocol:** WebSocket (with fallback to long-polling)
**License:** MIT Open Source

#### Pricing & Scaling
- **Free Tier:** Yes (open source)
- **Per-Instance Limits:** 10,000–30,000 concurrent connections
- **10k Concurrent:** ~$2,000/month (AWS t3.large × 2 + Redis)
- **100k Concurrent:** ~$20,000/month (t3.xlarge × 5 + Redis cluster)
- **Scaling Overhead:** Requires Redis adapter, load balancer, sticky sessions

#### Performance
- **Latency:** 50–150ms (depends on infrastructure)
- **Presence:** Native support via built-in events
- **Rooms/Channels:** Yes, unlimited
- **Message History:** Not built-in (requires external DB)
- **Delivery Guarantee:** At-most-once (no persistence by default)

#### Features
- **Framework SDKs:** Node.js native, JavaScript/TypeScript client
- **Browser Support:** IE6+, graceful degradation
- **Edge Support:** No native edge support
- **Self-Hosting:** Full control, requires DevOps expertise
- **Scaling Challenges:**
  - Single-server limit ~30k connections
  - Redis becomes bottleneck at scale
  - Sticky sessions complicate deployment
  - Garbage collection pauses degrade performance

#### Best For
- Small-to-medium projects (10k concurrent max)
- Custom real-time requirements
- Teams with DevOps expertise
- Full self-control priority over operational overhead

#### When NOT to Use
- Large-scale deployments (100k+)
- Teams without infrastructure expertise
- Requiring message delivery guarantees
- Global latency requirements

**Sources:**
- [Scaling Socket.IO: Ably Topic](https://ably.com/topic/scaling-socketio)
- [Horizontal Scaling Guide](https://socket.io/docs/v4/tutorial/step-9/)

---

### 2. Pusher Channels

**Type:** Managed PaaS WebSocket
**Protocol:** WebSocket
**Free Tier:** Yes (Sandbox: 100 concurrent connections)

#### Pricing & Scaling (2025)
- **Sandbox:** Free (100 concurrent)
- **Startup:** $49/month (500 concurrent)
- **Pro:** $299/month (2,000 concurrent)
- **Business:** $499/month (5,000 concurrent)
- **Premium:** $999/month (10,000 concurrent)
- **Growth:** $1,999/month (15,000 concurrent)
- **Growth Plus:** $1,999/month (30,000 concurrent)
- **100k+ Concurrent:** Custom enterprise pricing

#### Performance
- **Latency:** 50–100ms (regional)
- **Presence:** Native support
- **Rooms/Channels:** Unlimited channels per connection
- **Message History:** 24 hours retention
- **Delivery Guarantee:** At-most-once

#### Features
- **Framework SDKs:** Node.js, Python, JavaScript, Go, Ruby
- **Browser Support:** IE5+, mobile-native SDKs
- **Edge Support:** Regional datacenters only
- **Self-Hosting:** No
- **Enterprise Features:** Webhook events, message history API

#### Advantages
- Fastest path to production
- Excellent ecosystem integrations
- Simple pricing model
- Good developer experience

#### Limitations
- Regional infrastructure (single region outages affect all)
- Higher pricing per connection than Ably
- No message persistence
- Limited at-most-once delivery semantics

#### Best For
- Standard web applications
- Chat and notifications
- Small-to-medium scale (5k–15k concurrent)
- Teams prioritizing velocity over features

**Sources:**
- [Pusher Channels Pricing](https://pusher.com/channels/pricing/)
- [Pusher vs Ably Comparison: Ably](https://ably.com/compare/ably-vs-pusher)

---

### 3. Ably Realtime

**Type:** Managed PaaS WebSocket with global edge
**Protocol:** WebSocket
**Free Tier:** Yes (200 concurrent connections, 6M monthly messages)

#### Pricing & Scaling (2025)
- **Free:** 200 concurrent, 6M messages/month
- **Standard:** $1/million connection-minutes (from $50–$500/month typical)
- **Pro:** Volume discounting at scale
- **Enterprise:** Custom SLAs, 99.999% uptime
- **Connection Minutes Pricing:** $1.00–$0.20 per million minutes (volume-based)
- **Message Pricing:** $0.50–$0.10 per million messages
- **10k Concurrent:** ~$5,000/month
- **100k Concurrent:** ~$50,000/month

#### Performance
- **Latency:** <65ms round-trip (99th percentile), <10ms intra-region
- **Presence:** Native CRDT-backed
- **Rooms/Channels:** Unlimited
- **Message History:** Persistent storage, queryable history
- **Delivery Guarantee:** Exactly-once with message ID deduplication
- **Uptime SLA:** 99.999% (enterprise)

#### Features
- **Framework SDKs:** JavaScript, Node.js, Python, Go, Java, Ruby
- **Browser Support:** All modern browsers
- **Edge Support:** Global edge network (200+ datacenters)
- **Self-Hosting:** No
- **Message Persistence:** Built-in, 24–365 days configurable
- **Multi-region Failover:** Automatic

#### Advantages
- Message delivery guarantees (exactly-once)
- Global edge network with sub-65ms latency
- Automatic failover across regions
- Superior SLAs for enterprise
- Persistence and message history
- Generous free tier

#### Limitations
- More complex pricing model
- Higher cost at very large scale vs self-hosted
- Smaller ecosystem vs Pusher

#### Best For
- Enterprise applications requiring guarantees
- Financial services, healthcare
- Global user bases
- Mission-critical real-time
- Applications needing message persistence

**Sources:**
- [Ably Pricing Overview](https://ably.com/docs/platform/pricing)
- [Ably Latency & Architecture](https://ably.com/docs/platform/architecture/latency)
- [Message Delivery Guarantees](https://ably.com/topic/pubsub-delivery-guarantees)
- [Ably vs Pusher: Ably](https://ably.com/compare/ably-vs-pusher)

---

### 4. Supabase Realtime

**Type:** PostgreSQL-native pub/sub via WebSocket
**Protocol:** WebSocket
**License:** Open Source (self-hostable)

#### Pricing & Scaling (2025)
- **Free Tier:**
  - 200 concurrent realtime connections
  - 50,000 monthly active users
  - 2 projects
  - Database storage: 500MB
- **Pro Tier:** $25/month per project
  - Additional connections: $10 per 1,000 peak connections
  - Message pricing: $2.50 per million messages
  - Only pay for usage exceeding free quota
- **10k Concurrent:** ~$100/month (connections)
- **100k Concurrent:** ~$1,000/month

#### Performance
- **Latency:** 50–150ms (depends on proximity)
- **Presence:** CRDT-backed, in-memory
- **Rooms/Channels:** Table-based subscriptions
- **Message History:** 3-day retention (Broadcast), queryable for DB changes
- **Delivery Guarantee:** At-most-once

#### Features
- **Framework SDKs:** JavaScript, Python, Dart, Kotlin, Swift
- **Database Integration:** Postgres subscriptions (real database change events)
- **Broadcast:** Ephemeral client-to-client messaging
- **Presence:** CRDT-backed state sync
- **Postgres Changes:** Automatic change notifications via RLS policies
- **Self-Hosting:** Yes (Elixir/Phoenix-based)
- **Edge Support:** Limited (via managed service only)

#### Capabilities
1. **Database Subscriptions** → Subscribe to table changes with RLS integration
2. **Broadcast** → Low-latency pub/sub for transient messages
3. **Presence** → Track user state across clients

#### Limitations
- Only 200 concurrent free (vs 500+ for competitors)
- Message retention: 3 days
- Single-region (unless self-hosted)
- No message delivery guarantees
- Row-level security required for fine-grained access

#### Best For
- Postgres-first applications
- Minimal budget (generous free tier)
- Applications needing DB change notifications
- Teams already on Supabase
- Self-hostable requirement

**Sources:**
- [Supabase Realtime Pricing](https://supabase.com/docs/guides/realtime/pricing)
- [Supabase Pricing Overview](https://supabase.com/pricing)
- [Realtime Architecture](https://supabase.com/docs/guides/realtime)

---

### 5. Liveblocks

**Type:** Managed CRDT collaboration platform
**Protocol:** WebSocket
**Free Tier:** Yes (500 monthly active rooms)

#### Pricing & Scaling (2025)
- **Free:** 500 monthly active rooms
- **Pro:** Pay-per-use for rooms above 500
- **Enterprise:** Multi-region, management API, SCIM/SSO, custom allocations
- **Billing Model:** Only pay for returning monthly active users (2025 update)
- **10k Concurrent:** ~$500–$2,000/month (user-dependent)
- **100k Concurrent:** ~$5,000–$20,000/month

#### Performance
- **Latency:** <50ms (edge regions)
- **Presence:** Native cursor sync, live awareness
- **Rooms/Channels:** Per-application rooms with CRDT
- **Message History:** Full document state + change history
- **Delivery Guarantee:** Exactly-once via CRDT

#### Features
- **Framework SDKs:** React, Vue, Svelte, vanilla JS
- **CRDT Engine:** Yjs integration native
- **Collaborative Components:** Comments, multiplayer, AI agents
- **Rich UI:** Pre-built components (cursors, selections, avatars)
- **Webhooks:** Trigger actions on edits
- **Self-Hosting:** No (managed only)

#### Capabilities
1. **Multiplayer Editing** → Yjs-powered real-time sync
2. **Comments & Notifications** → Thread-based collaboration
3. **Presence & Awareness** → Live cursors, selections, status
4. **AI Agents** → Built-in collaboration with AI
5. **Ready-Made UI Components** → Reduce development time

#### Limitations
- Managed only (no self-hosting)
- CRDT overhead vs simple pub/sub
- Pricing increases with user base
- Limited to web (React-focused)

#### Best For
- Collaborative document editing
- Design tools and whiteboards
- Real-time dashboards with collaborative features
- Teams wanting pre-built collaboration UI
- Applications requiring CRDT semantics

**Sources:**
- [Liveblocks Pricing](https://liveblocks.io/pricing)
- [Liveblocks 2025 Updates](https://liveblocks.io/blog/whats-new-in-liveblocks-april-edition-2025)
- [Liveblocks Yjs Integration](https://liveblocks.io/blog/introducing-liveblocks-yjs)

---

### 6. PartyKit (Cloudflare Durable Objects)

**Type:** Edge-first CRDT collaboration platform
**Protocol:** WebSocket
**License:** Open Source

#### Pricing & Scaling (2025)
- **Compute:** $0.50 per million requests
- **Durables:** $0.15 per million request-seconds + $1.25/GB-month storage
- **Typical Usage:** 10k concurrent = ~$200–$500/month
- **100k Concurrent:** ~$2,000–$5,000/month
- **Free Tier:** Cloudflare Workers free tier partially applies

#### Performance
- **Latency:** <10ms (edge network, 200+ global datacenters)
- **Presence:** Native via Durable Objects
- **Rooms/Channels:** Per-room Durable Objects
- **Message History:** Persistent storage via Durable Objects
- **Delivery Guarantee:** Exactly-once (state-machine backed)

#### Features
- **Framework SDKs:** TypeScript/JavaScript, Yjs support (y-partykit)
- **Edge Deployment:** Global Cloudflare edge network
- **Yjs Integration:** Native support via y-partykit
- **Durable Objects:** Stateful serverless at the edge
- **WebSocket Multiplexing:** 2025 enhancement for scale
- **Automatic Object Sharding:** 2025 enhancement for scale

#### Architecture
- Each "party" (room) runs in a separate Durable Object
- Durable Objects provide state persistence across requests
- Global replication via Cloudflare network
- Automatic failover and recovery

#### Advantages
- Extremely low latency (<10ms)
- Global edge deployment out of the box
- Yjs CRDT support native
- Cloudflare ecosystem integration
- Open source

#### Limitations
- Requires Cloudflare Workers (vendor lock-in)
- Smaller community than Liveblocks
- Learning curve for Durable Objects model
- Less pre-built UI than Liveblocks

#### Best For
- Ultra-low latency requirements
- Global edge deployment priority
- Collaborative editing on edge
- Teams using Cloudflare
- Building multiplayer games/apps
- Yjs-based CRDTs

**Sources:**
- [PartyKit Overview: Cloudflare](https://blog.cloudflare.com/cloudflare-acquires-partykit/)
- [PartyKit Docs: How It Works](https://docs.partykit.io/how-partykit-works/)
- [y-partykit API Reference](https://docs.partykit.io/reference/y-partykit-api/)

---

### 7. Server-Sent Events (SSE)

**Type:** HTTP-based server-to-client streaming
**Protocol:** HTTP/1.1 with Connection: keep-alive
**License:** Web Standard (W3C)

#### Pricing & Scaling
- **Free:** Native browser API
- **Server Cost:** Minimal (connection pooling)
- **10k Concurrent:** ~$500/month (simple Node.js/Python server)
- **100k Concurrent:** ~$5,000/month

#### Performance
- **Latency:** 50–100ms (HTTP protocol)
- **Data Format:** UTF-8 text only (no binary)
- **Throughput:** High-volume streaming capable
- **Connection Persistence:** Automatic reconnection

#### Features
- **Framework SDKs:** Vanilla JS (EventSource API)
- **Fallbacks:** None needed (HTTP-based)
- **Message Format:** Text-based event stream
- **Automatic Retry:** Browser-native exponential backoff
- **CORS:** Works across domains

#### Limitations
- **Unidirectional:** Server-to-client only
- **Text Only:** UTF-8 data (no binary)
- **Connection Limits:** Browser limits ~6 concurrent connections
- **No Presence:** Requires manual implementation
- **No Rooms:** Global broadcast (implement app-level filtering)

#### Use Cases (SSE is Perfect For)
1. **Notification Feeds** → Push alerts from server
2. **Live Dashboards** → Real-time metric updates
3. **Stock Tickers** → Continuous price streams
4. **Log Streaming** → Application event logs
5. **Activity Feeds** → Timeline updates

#### SSE vs WebSocket Decision Matrix

| Use Case | SSE | WebSocket |
|----------|-----|-----------|
| Notifications | ✅ Preferred | ⚠️ Overkill |
| Live Dashboard | ✅ Preferred | ⚠️ Overkill |
| Chat (2-way) | ❌ Insufficient | ✅ Required |
| Multiplayer | ❌ Insufficient | ✅ Required |
| Stock Feed | ✅ Preferred | ⚠️ Overkill |
| Collaborative Editing | ❌ Insufficient | ✅ Required |
| Cost Optimization | ✅ Cheaper | ⚠️ Expensive |

#### Best For
- Applications with server→client-only updates (95% of cases per 2025 analysis)
- Teams wanting simplicity over features
- Limited budget for infrastructure
- Mobile-friendly notifications
- Read-only real-time updates

#### When NOT to Use
- Bidirectional messaging (use WebSocket)
- Binary data transmission
- High-frequency client→server requests

**Sources:**
- [WebSockets vs SSE: Ably](https://ably.com/blog/websockets-vs-sse)
- [SSE vs WebSocket Comparison](https://www.freecodecamp.org/news/server-sent-events-vs-websockets/)
- [Polling vs SSE vs WebSocket: FreeCodeCamp](https://rxdb.info/articles/websockets-sse-polling-webrtc-webtransport.html)

---

### 8. WebTransport

**Type:** Low-latency UDP-based protocol over QUIC
**Protocol:** HTTP/3 + QUIC + UDP
**Status:** Draft standard (IETF), browser support: Chrome/Edge (Firefox 114+)

#### Pricing & Scaling
- **Free:** Open standard (no licensing)
- **Implementation Cost:** Server framework support required
- **10k Concurrent:** ~$1,000–$2,000/month
- **100k Concurrent:** ~$10,000–$20,000/month

#### Performance
- **Latency:** <50ms (35% improvement over WebSocket)
  - Median: 200ms
  - Optimal: Sub-100ms
- **Throughput:** Multiplexed streams + unreliable datagrams
- **Packet Loss:** Unreliable datagrams tolerate loss
- **Jitter:** Low variance due to QUIC

#### Features
- **Protocol:** HTTP/3 over QUIC
- **Multiplexing:** Multiple streams in single connection
- **Datagrams:** Unreliable fast transmission (trading reliability for speed)
- **TLS 1.3:** Built-in encryption
- **Connection Migration:** Seamless network switching

#### Browser Support (2025)
- ✅ Chrome 102+
- ✅ Edge 102+
- ✅ Firefox 114+
- ❌ Safari/iOS (adoption barrier)

#### Major Limitation
Safari/iOS incompatibility means ~50% of potential users excluded. Developers building with WebTransport must implement fallback strategies (WebSocket/SSE).

#### Best For
- Ultra-low latency applications
- Live streaming with sub-300ms latency
- Gaming and real-time graphics
- Teams accepting fallback complexity
- Forward-looking architecture

#### When to Wait
- Until Safari/iOS support available
- Non-critical real-time applications
- Projects requiring 95% browser support

**Sources:**
- [WebTransport API: MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebTransport_API)
- [Beyond WebSockets: WebTransport for 35% Latency Reduction](https://www.vroble.com/2025/11/beyond-websockets-mastering.html)
- [Future of WebSockets: WebSocket.org](https://websocket.org/guides/future-of-websockets/)

---

## COLLABORATIVE FEATURES: CRDT & Yjs

### CRDT (Conflict-free Replicated Data Type)

**What:** Data structure that resolves conflicts automatically without central coordination

**Key Properties:**
- Commutative: Order of operations doesn't matter
- Idempotent: Duplicate operations have no additional effect
- Convergent: All replicas eventually consistent

**Use Cases:**
- Multiplayer editing (Google Docs-like)
- Real-time whiteboards
- Collaborative design tools
- Live cursors and selections

### Yjs

**Status:** Most popular CRDT library (900k+ weekly npm downloads)
**Language:** TypeScript/JavaScript
**License:** MIT

**Yjs Providers (2025):**
1. **Liveblocks Yjs** → @liveblocks/yjs (turnkey)
2. **y-partykit** → PartyKit integration (edge-first)
3. **y-websocket** → Generic WebSocket backend
4. **y-indexeddb** → Browser persistence
5. **y-doc** → In-memory state

**Advantages:**
- Automatic conflict resolution
- Offline-first capable
- Minimal bandwidth (only deltas)
- Framework-agnostic

**Limitations:**
- Learning curve (CRDT concepts)
- Server-side complexity
- Larger bundle size (~50KB)

**Best For:**
- Document/text editing
- Shared whiteboards
- Real-time design tools
- Any multi-user editing scenario

**Sources:**
- [Yjs Documentation](https://docs.yjs.dev/)
- [Liveblocks Yjs Integration](https://liveblocks.io/blog/introducing-liveblocks-yjs)
- [y-partykit: PartyKit Docs](https://docs.partykit.io/reference/y-partykit-api/)

---

## DECISION LOGIC WITH IF/THEN RULES

### Rule 1: Unidirectional Communication
```
IF: Only server→client updates needed
    AND: Not requiring client→server messaging beyond initial request
THEN: Use SSE
  WHY: 95% simpler, cheaper, lower latency for one-way streams
  EXAMPLE: Notifications, dashboards, log streams, news feeds
```

### Rule 2: Simple Bidirectional
```
IF: Chat, real-time forms, or bidirectional updates needed
    AND: No CRDT/collaborative editing required
    AND: Budget available for managed service
THEN: Use Pusher or Ably
  IF: < 5k concurrent → Pusher (simpler ecosystem)
  IF: > 5k concurrent OR guarantees needed → Ably (global edge, persistence)
  IF: Cost-sensitive → Supabase Realtime (Postgres-native)
```

### Rule 3: Self-Hosted Bidirectional
```
IF: Full control required
    AND: Team has DevOps expertise
    AND: < 30k concurrent acceptable
THEN: Use Socket.IO
  NOTE: Requires Redis, load balancer, sticky sessions
  RISK: DevOps overhead > managed service cost above ~20k concurrent
```

### Rule 4: Collaborative Editing
```
IF: Multiplayer document/text editing needed
THEN: CRDT required

  IF: Turnkey solution preferred
  THEN: Use Liveblocks
    WHY: Pre-built UI, managed infrastructure, Yjs native

  ELSE IF: Edge-first + ultra-low latency
  THEN: Use PartyKit (y-partykit)
    WHY: <10ms latency, global edge, Cloudflare ecosystem

  ELSE IF: Database-integrated collaboration
  THEN: Use Supabase (with Yjs) + self-host Yjs backend
    WHY: Postgres-native, self-hostable, free tier
```

### Rule 5: Ultra-Low Latency (<50ms)
```
IF: Latency critical (<50ms required)
    AND: Browser compatibility acceptable
THEN: Consider WebTransport
  WARNING: Chrome/Edge/Firefox only (no Safari/iOS)
  PLAN: Implement WebSocket fallback for complete coverage
  EXAMPLE: Live gaming, real-time graphics, HFT dashboards
```

### Rule 6: Enterprise Scale (100k+ concurrent)
```
IF: 100k+ concurrent connections needed
THEN: Managed service required (self-hosting prohibitive)

  IF: Message delivery guarantees critical
  THEN: Ably
    WHY: 99.999% SLA, persistence, message ordering, global edge
    COST: ~$50k/month at 100k concurrent

  ELSE IF: Cost optimization
  THEN: Pusher custom pricing
    BUT: Single-region outage risk, no persistence

  ELSE IF: Edge deployment priority
  THEN: PartyKit (if < 50k current Durable Objects limit)
```

### Rule 7: Budget Constraint
```
IF: Minimal budget (< $100/month)
THEN:
  - Free tier priority: Supabase Realtime (200 concurrent)
  - Or: Self-host Socket.IO + cheap VPS

IF: Moderate budget ($100–$1k/month)
THEN:
  - Pusher (up to ~5k concurrent)
  - Or: Socket.IO self-hosted (~10–20k concurrent)
  - Or: Ably ($500–$5k depending on scale)

IF: Enterprise budget (> $1k/month)
THEN:
  - Ably (guarantees, global, persistence)
  - Or: Liveblocks (collaborative features)
  - Or: PartyKit (edge-first collaboration)
```

### Rule 8: Framework Compatibility
```
IF: React application
THEN: All options supported; Liveblocks offers best React integration

IF: Vue application
THEN: Socket.IO, Supabase, most others compatible
     Liveblocks has Svelte preference

IF: Python backend
THEN:
  - Ably SDK available
  - Pusher SDK available
  - Supabase SDK available
  - Socket.IO requires async handling (harder)

IF: Node.js/Express
THEN: Socket.IO native; others equally compatible
```

---

## COMPARISON MATRIX

| Criteria | Socket.IO | Pusher | Ably | Supabase | Liveblocks | PartyKit | SSE | WebTransport |
|----------|-----------|--------|------|----------|-----------|----------|-----|--------------|
| **Type** | Library | Managed | Managed | DB-native | CRDT SaaS | Edge | HTTP | QUIC |
| **Free Tier** | Yes | 100 conc | 200 conc | 200 conc | 500 rooms | Limited | N/A | N/A |
| **10k Concurrent** | $2k | $300 | $5k | $100 | $500–$2k | $300 | $500 | $1k |
| **100k Concurrent** | $20k+ | Custom | $50k | $1k | $5k–$20k | $2k–$5k | $5k | $10k |
| **Latency** | 50–150ms | 50–100ms | <65ms | 50–150ms | <50ms | <10ms | 50–100ms | <50ms |
| **Delivery Guarantee** | None | At-most | Exactly | At-most | Exactly | Exactly | At-most | None |
| **Message Persistence** | No | 24h | Configurable | 3d (Broadcast) | Full history | Via storage | No | No |
| **Presence** | Yes | Yes | Yes | Yes (CRDT) | Yes | Yes | No | No |
| **CRDT/Collab** | No | No | No | No | Yes (Yjs) | Yes (Yjs) | No | No |
| **Self-Hosted** | Yes | No | No | Yes | No | No | N/A | No |
| **Edge Support** | No | Regional | Global | Limited | Managed | Global | No | No |
| **SDKs** | JS/Node | Multi | Multi | Multi | React/Web | JS | Native | JS/Rust |
| **Browser Support** | IE5+ | All | All | All | Modern | Modern | All | Chrome/Edge/FF |
| **Enterprise SLA** | No | No | 99.999% | No | Custom | Custom | No | No |

---

## LATENCY COMPARISON (Real-World 2025)

```
WebTransport (QUIC):     ━━━━━━━━━━━ <50ms (Chrome only)
PartyKit (Edge):         ━━━━━━━━━━━━ <10ms global avg
Ably (Global Edge):      ━━━━━━━━━━━━━━ <65ms (99th pct)
Pusher (Regional):       ━━━━━━━━━━━━━━━ 50–100ms
Liveblocks (Edge):       ━━━━━━━━━━━━━━ <50ms
Socket.IO (Self):        ━━━━━━━━━━━━━━━━ 50–150ms (infra-dependent)
SSE (HTTP):              ━━━━━━━━━━━━━━━━ 50–100ms
Supabase Realtime:       ━━━━━━━━━━━━━━━━ 50–150ms
```

---

## COST ANALYSIS AT SCALE

### 10,000 Concurrent Users (Monthly)

| Solution | Cost | Infrastructure | Notes |
|----------|------|-----------------|-------|
| Socket.IO | $2,000 | AWS t3.large ×2 + Redis | DIY DevOps |
| Pusher | $300–$600 | Managed | Simple tier pricing |
| Ably | $5,000–$10,000 | Managed global | Includes persistence |
| Supabase | $100 | Managed | DB-native pricing |
| Liveblocks | $500–$2,000 | Managed | Per-room model |
| PartyKit | $300–$500 | Cloudflare workers | Per-request billing |

### 100,000 Concurrent Users (Monthly)

| Solution | Cost | Infrastructure | Notes |
|----------|------|-----------------|-------|
| Socket.IO | $20,000+ | Kubernetes cluster + Redis | DevOps intensive |
| Pusher | Custom | Regional | Enterprise negotiation |
| Ably | $50,000 | Managed global | Guaranteed delivery |
| Supabase | $1,000 | Managed | Scales with usage |
| Liveblocks | $5,000–$20,000 | Managed | Scales with users |
| PartyKit | $2,000–$5,000 | Cloudflare edge | Auto-scaling |

---

## DECISION QUICK REFERENCE

### Choose SSE IF:
- ✅ One-way updates only (server→client)
- ✅ Notifications, dashboards, feeds
- ✅ Minimal budget
- ✅ Simple implementation priority

### Choose Socket.IO IF:
- ✅ Small team (<5k concurrent)
- ✅ Full infrastructure control needed
- ✅ Custom messaging requirements
- ✅ DevOps capability available

### Choose Pusher IF:
- ✅ Fast time-to-market
- ✅ Standard chat/messaging features
- ✅ 5–15k concurrent ideal range
- ✅ Prefer simplicity over advanced features

### Choose Ably IF:
- ✅ Enterprise reliability critical
- ✅ Message guarantees required
- ✅ Global user base
- ✅ Scale-as-you-grow pricing

### Choose Supabase IF:
- ✅ Postgres-first architecture
- ✅ Minimal budget (free tier)
- ✅ DB change notifications core requirement
- ✅ Self-hosted option valuable

### Choose Liveblocks IF:
- ✅ Collaborative editing needed (Docs-like)
- ✅ Rich real-time UI required
- ✅ Time-to-market important
- ✅ React/web stack

### Choose PartyKit IF:
- ✅ Ultra-low latency (<10ms) critical
- ✅ Global edge deployment required
- ✅ Yjs/CRDT collaboration needed
- ✅ Cloudflare ecosystem preferred

### Choose WebTransport IF:
- ✅ Latency <50ms essential
- ✅ Chrome/Edge/Firefox coverage acceptable
- ✅ Can implement WebSocket fallback
- ✅ Gaming or real-time graphics app

---

## FRAMEWORK SDK SUPPORT MATRIX (2025)

| Framework | Socket.IO | Pusher | Ably | Supabase | Liveblocks | PartyKit |
|-----------|-----------|--------|------|----------|-----------|----------|
| **React** | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅ |
| **Vue** | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **Angular** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| **Svelte** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Next.js** | ✅ | ✅ | ✅ | ✅ | ✅✅ | ✅ |
| **Node.js** | ✅✅ | ✅ | ✅ | ✅ | N/A | ✅ |
| **Python** | ⚠️ | ✅ | ✅ | ✅ | N/A | N/A |
| **Go** | ⚠️ | ✅ | ✅ | ⚠️ | N/A | N/A |
| **Ruby** | ✅ | ✅ | ✅ | ⚠️ | N/A | N/A |
| **Java** | ⚠️ | ⚠️ | ✅ | ⚠️ | N/A | N/A |

Legend: ✅✅ = Excellent support, ✅ = Full support, ⚠️ = Limited, N/A = Not applicable

---

## ADDITIONAL RESOURCES

### Monitoring & Observability
- **Ably:** Built-in monitoring dashboard
- **Pusher:** Real-time analytics
- **Socket.IO:** Requires external tools (Prometheus, Grafana)
- **PartyKit:** Cloudflare analytics
- **Liveblocks:** Usage analytics

### Security Considerations
- All solutions support TLS 1.3 encryption
- Ably: Automatic message signing, encryption
- Pusher: Private channels, encrypted events
- Supabase: Row-level security (Postgres)
- Liveblocks: Webhook verification
- PartyKit: Cloudflare security

### Compliance & Data Residency
- **GDPR:** Ably (EU regions), PartyKit (Cloudflare global), Pusher (check)
- **HIPAA:** Ably Enterprise, others case-by-case
- **Data Residency:** Ably (regional choice), PartyKit (Cloudflare), Pusher (US/EU)

---

## CONCLUSION

The real-time landscape in 2025/2026 is mature with specialized solutions for every use case:

1. **95% of applications need SSE** (server→client only) — avoid over-engineering
2. **Standard bidirectional** → Pusher (simple) or Ably (reliable)
3. **Self-hosted + control** → Socket.IO (accept DevOps complexity)
4. **Collaborative editing** → Liveblocks (turnkey) or PartyKit (edge)
5. **Ultra-low latency** → WebTransport (with fallbacks) or PartyKit
6. **Budget-first** → Supabase Realtime or Socket.IO

Choose simplicity unless specific requirements demand complexity.

---

## RESEARCH SOURCES

1. [Ably Pricing Overview](https://ably.com/docs/platform/pricing)
2. [Ably vs Pusher Comparison](https://ably.com/compare/ably-vs-pusher)
3. [Pusher Channels Pricing](https://pusher.com/channels/pricing/)
4. [Liveblocks Pricing & Docs](https://liveblocks.io/pricing)
5. [PartyKit & Cloudflare Acquisition](https://blog.cloudflare.com/cloudflare-acquires-partykit/)
6. [Supabase Realtime Guide](https://supabase.com/docs/guides/realtime)
7. [Socket.IO Scaling Guide](https://ably.com/topic/scaling-socketio)
8. [WebSockets vs SSE](https://ably.com/blog/websockets-vs-sse)
9. [WebTransport Future](https://websocket.org/guides/future-of-websockets/)
10. [Yjs CRDT Documentation](https://docs.yjs.dev/)

**Document Version:** 2.0
**Last Updated:** February 2026
**Author:** Tech Stack Research
**Status:** Production Ready

## Related References
- [Relational Databases](./07-databases-relational.md) — Data persistence for real-time sync
- [Edge Computing & Multi-Region](./43-edge-multi-region.md) — Global deployment for sub-50ms latency
- [Observability & Tracing](./55-observability-tracing.md) — Monitoring WebSocket connections and latency
- [Background Jobs & Events](./50-background-jobs-events.md) — Event-driven architecture foundations
- [Performance Benchmarks](./47-performance-benchmarks.md) — Latency comparisons across solutions
- [Resilience Patterns](./52-resilience-patterns.md) — Handling WebSocket disconnections and retries

<!-- PRICING_STABILITY: MODERATE | Updated: 2026-03-03 | Tool/platform pricing changes annually. Verify before critical decisions. -->
