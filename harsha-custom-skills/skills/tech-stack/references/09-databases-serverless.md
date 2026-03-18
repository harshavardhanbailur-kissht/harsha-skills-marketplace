# Serverless & Edge Databases Guide 2025-2026

**Last Updated:** February 2026
**Scope:** Supabase, Neon, Turso, PlanetScale, D1, Convex, Firebase
**Research Date:** February 19, 2026

---

## Executive Summary

The serverless and edge database market has matured significantly in 2025-2026. Postgres-based solutions (Supabase, Neon) dominate for traditional apps, SQLite edge databases (Turso) excel for distributed/AI workloads, MySQL (PlanetScale) offers MySQL-specific branching, and reactive databases (Convex) serve real-time collaborative apps. Firebase remains strong for mobile but faces stiff competition on cost and flexibility.

**Key Trend:** Data sovereignty and avoiding vendor lock-in are now mainstream concerns, with open-source alternatives gaining adoption.

---

## Platform Comparison Matrix

| **Factor** | **Supabase** | **Neon** | **Turso** | **PlanetScale** | **D1** | **Convex** | **Firebase** |
|---|---|---|---|---|---|---|---|
| **Base DB** | PostgreSQL | PostgreSQL | SQLite | MySQL (Vitess) | SQLite | Proprietary | Firestore/RTDB |
| **Model** | Serverless Managed | Serverless (compute) | Edge + Sync | Serverless Managed | Edge (Cloudflare) | Reactive Backend | NoSQL |
| **Free Tier** | 500 MB, 50k MAU | 3 projects, 0.25CU | 5 GB read/write | - | 5M reads/day | Developer plan | 1 GB storage, 50k reads/day |
| **Pro Plan** | $25/mo | $19/mo (Launch) | $4.99/mo (Dev) | $5/mo (single-node) | $5/mo | Pay-as-you-go | $0.18/100k reads |
| **Branching** | Limited | Excellent (CoW) | Supported | Excellent | Limited | No | No |
| **Edge Support** | Edge Functions | No | Excellent | No | Native | Regional | Regional |
| **Realtime** | ✓ WebSocket-based | ✗ | Sync (offline-first) | ✗ | ✗ | ✓ Reactive | ✓ Firestore |
| **Auth** | Built-in JWT | None | None | None | None | Built-in | Built-in |
| **File Storage** | S3-compatible | None | None | None | None | None | Cloud Storage |
| **Vendor Lock-in** | 3 (Medium) | 2 (Low) | 1 (Very Low) | 2 (Low) | 4 (High) | 3 (Medium) | 5 (Very High) |
| **Self-Hosting** | ✓ Docker | ✗ | ✓ (libSQL) | ✓ (Vitess) | ✗ | ✓ Open-source | ✗ |

---

## Detailed Platform Analysis

---

### 1. SUPABASE: The Firebase Alternative

**Overview:** Full-stack PostgreSQL development platform (Database + Auth + Storage + Realtime + Edge Functions).

#### Pricing & Free Tier

**Free Plan ($0)**
- 2 projects (auto-paused after 7 days inactivity)
- 500 MB database storage
- 50,000 monthly active users (MAU)
- 1 GB file storage
- 2 GB storage egress
- 500,000 Edge Function invocations/month
- 2 GB database egress

**Pro Plan ($25/month base)**
- 8 GB database included
- 100k MAU
- 100 GB storage included
- Daily backups
- No auto-pause
- Usage-based billing for overages
- Real-world cost: $35-75/month once usage fees included

**Team Plan ($599/month)**
- Pro features + team collaboration

**Enterprise**
- Custom pricing, dedicated support, HIPAA compliance

#### Underlying Database

**PostgreSQL 15+** with:
- Row Level Security (RLS)
- Full-text search
- JSON/JSONB support
- Vector extensions (pgvector)
- PostGIS support
- pg_cron for scheduling

#### Serverless Model

- Dedicated compute instances (not truly serverless, but auto-scaling)
- Always-on availability model
- 99.9% uptime SLA (Standard), 99.99% (Enterprise)
- Connection pooling via Supavisor

#### Edge Support

- **Edge Functions:** Deploy JavaScript globally in seconds
- Rust/Deno runtime, WebAssembly support
- S3-compatible mount for persistent storage
- Cache-first patterns supported
- Recent update: 97% faster cold starts with persistent storage

#### Branching

- Limited branching support (development branches on Pro+)
- Not copy-on-write like Neon
- Primarily for database snapshots rather than Git-like development workflow

#### Realtime Features

- **Postgres Changes (LISTEN/NOTIFY):** WebSocket subscriptions to row/schema changes
- Real-time multiplayer synchronization
- Automatic conflict resolution
- Requires explicit column subscriptions

#### Auth Integration

**JWT-Based System:**
- Access tokens (short-lived, 5 min - 1 hour)
- Refresh tokens (long-lived, refreshed once)
- Session ID tracking via UUID claim
- OAuth 2.0 providers (Google, GitHub, Discord, etc.)
- Multi-factor authentication (MFA) support
- SAML/SSO for Enterprise
- Row Level Security (RLS) integration with auth context
- Custom access token hooks

#### File Storage

- S3-compatible bucket interface
- Default Supabase Storage or bring-your-own S3
- Signed URLs for temporary access
- Integration with Edge Functions
- Storage limits: 1 GB free → 100 GB on Pro

#### Backup & Restore

- Free tier: 7-day retention
- Pro+: Daily backups, 30-day retention
- Point-in-time recovery available
- Automated backups to S3

#### Reliability & Outages (2025-2026)

- **Uptime:** 99.9% (Standard), 99.99% (Enterprise)
- **Recent Incidents:**
  - June 12, 2025: Global outage (Cloudflare connectivity)
  - Feb 15-16, 2026: Supavisor cluster degradation (elevated latency)
  - Feb 2026: Edge Functions protocol issues in specific regions
- **90-day stats:** 27 incidents (13 major, 14 minor), median duration 1h 52m

#### Vendor Lock-in: **3/5 (Medium)**

Mitigating factors:
- Open-source backend (self-hostable via Docker)
- Standard PostgreSQL (portable)
- Export/import tools available

Lock-in factors:
- Auth system proprietary
- Migration tooling limited
- RLS integration tight

#### Self-Hosting Viability

**Excellent:** Fully self-hostable via Docker in <30 minutes.
- Recommended: Dokploy, EasyPanel for UI
- NGINX reverse proxy for multi-domain hosting
- All features available except managed cloud benefits
- Active community deployments in 2025

#### Developer Experience

- Auto-generated REST API from schema
- GraphQL support (community-maintained)
- JavaScript/TypeScript SDKs
- Intuitive Dashboard with SQL editor
- Instant API routes via PostgREST
- VS Code extensions

#### vs Firebase Comparison

| Aspect | Supabase | Firebase |
|---|---|---|
| **Database** | PostgreSQL (relational) | Firestore (NoSQL) |
| **Cost at Scale** | Cheaper for read-heavy (predictable) | More expensive (per-doc pricing) |
| **Developer Learning** | SQL required | NoSQL (Firestore query syntax) |
| **Performance** | Up to 4x faster reads (benchmarks) | Better for real-time sync |
| **Flexibility** | High (SQL + extensions) | Lower (NoSQL constraints) |
| **Migration** | Tools available | Complex, data transformation needed |
| **Pricing Transparency** | Clear, predictable | Hidden charges possible |

---

### 2. NEON: Serverless PostgreSQL

**Overview:** Postgres with separation of storage and compute, enabling autoscaling and branching.

#### Pricing & Free Tier

**Free Plan**
- 3 projects
- 0.25 Compute Unit (CU) included
- Auto-scale up to 2 CU
- Scale-to-zero (5-min idle timeout)
- 3 GB storage included
- 10 branches

**Launch Plan ($19/month)**
- 0.5 CU included
- Compute-hours based usage
- Autoscale up to 2 CU
- 25% cheaper compute pricing (2025 reduction)

**Scale Plan ($69/month)**
- 1 CU included
- Autoscale to higher limits
- Advanced support

**Business Plan ($700/month)**
- Custom compute, priority support

**Cost Comparison:**
- Entry-level (0.25CU, 1GB, 9h/day): ~$7.66/mo (30% of Supabase)
- New launch (1-4CU, 20GB): ~40% of Aurora, 70% of Supabase

#### Underlying Database

- PostgreSQL 15+
- Same as Supabase (standard Postgres)
- Direct SQL access
- Full extension support

#### Serverless Model

**Storage-Compute Separation:**
- Storage layer: Decoupled, persistent
- Compute layer: Ephemeral, stateless
- Enables true autoscaling

**Autoscaling Architecture:**
- Monitors CPU utilization and memory pressure
- Auto-adds resources when threshold crossed
- Auto-removes after idle period
- Scale-to-zero billing (pay only when active)

#### Edge Support

- **No native edge support**
- Designed for centralized workloads
- Regional compute endpoints
- Can be paired with Cloudflare Workers or Vercel Edge

#### Branching (Key Differentiator)

**Copy-on-Write (CoW) Branching:**
- Create instant branches (schema + data snapshot)
- Branches created in ~1 second regardless of DB size
- 500k branches created/day on Neon platform
- Two types:
  - **Schema-only:** Schema copied, no data
  - **Data branches:** Full snapshot at point-in-time

**Use Cases:**
- Testing migrations without production data
- Ephemeral CI/CD environments
- Development sandboxes
- Time-travel recovery

#### Realtime Features

- **No built-in realtime**
- Requires polling or external tools (Supabase Realtime, etc.)
- Webhook support available

#### Auth Integration

- None (bring-your-own: Supabase Auth, NextAuth, Auth0, etc.)

#### File Storage

- None (use S3, Cloudinary, etc.)

#### Backup & Restore

- Point-in-time recovery available
- Automatic daily backups
- Retention: up to 30 days on higher tiers

#### Vendor Lock-in: **2/5 (Low)**

- Standard PostgreSQL (highly portable)
- Direct SQL access
- Export/import via pg_dump
- No proprietary extensions required

#### Developer Experience

- Web console for branching and management
- Neon CLI for local development (Neon Local)
- Direct psql connections
- SQL-first approach
- Integration with Vercel, Supabase, and other platforms

---

### 3. TURSO: Edge SQLite Database

**Overview:** Lightweight SQLite-compatible database replicated to edge globally. Local-first sync for offline-first apps.

#### Pricing & Free Tier

**Free Plan ($0)**
- 500M rows read/month
- 10M rows write/month
- 5 GB storage
- No credit card required
- Never expires
- Commercial use allowed

**Developer Plan ($4.99/month)**
- 2.5B rows read/month
- Upgrade path for growing projects

**Hobby Plan ($9/month)**
- Additional pricing flexibility

**Scaler & Pro Plans**
- Higher tier with custom limits

**Pricing Changes (Mar 31, 2025):**
- Free tier significantly increased
- New Developer plan introduced for gradual scaling

#### Underlying Database

- **SQLite-compatible** (via libSQL, Rust rewrite)
- Async-first architecture
- ACID guarantees
- JSON support
- BLOB support

#### Serverless Model

- **Edge-first:** Databases replicated to Cloudflare Workers locations globally
- Serverless access via HTTP
- No connection management required
- Pay-per-use (rows read/written)

#### Edge Support (Excellent)

- **Native edge replication** across Cloudflare network
- **Embedded Replicas:** Local SQLite files sync with cloud
- Zero-latency local reads
- Frame-based sync for changes
- **Offline Sync (Beta):** Write offline, sync when connected

#### Features (2025)

**Concurrent Writes:**
- Up to 4x throughput improvement over standard SQLite
- Removes SQLITE_BUSY errors

**Vector Search:**
- Native similarity search for AI/RAG workflows
- No extension required

**Data Synchronization:**
- Copy-on-write branches (super fast)
- Sync on-demand between devices
- Isolated branches for each user/agent

#### Branching

- Copy-on-write branches supported
- Per-user/agent isolation patterns
- Quick branch creation

#### Realtime Features

- **Sync-based (not true realtime):** Changes propagate on sync request
- Turso Sync protocol
- Row-level logical logging
- Last-Push-Wins conflict resolution

#### Auth Integration

- None (bring-your-own)

#### File Storage

- None (BLOB column support for small files)

#### Backup & Restore

- Automatic daily backups (7-day retention on Developer plan)
- Point-in-time recovery on higher tiers

#### Vendor Lock-in: **1/5 (Very Low)**

- **libSQL:** Open-source, can self-host
- Standard SQLite compatibility
- Portable data format
- Minimal lock-in, maximum portability

#### Developer Experience

- JavaScript/TypeScript SDKs (excellent)
- Prisma integration
- HTTP-based queries
- Local-first development workflow
- Great for AI agents and distributed systems

#### Use Cases

- Mobile/offline-first apps
- AI agents with per-agent databases
- Edge-distributed systems
- Point-of-sale systems
- Field data collection
- IoT applications

---

### 4. PLANETSCALE: MySQL at Scale

**Overview:** MySQL serverless database using Vitess sharding technology. Git-like branching for MySQL.

#### Pricing & Free Tier

**Free Tier:** Deprecated (moved to paid)

**Single-Node Plan ($5/month)**
- Entry-level Postgres databases
- 10 GB storage included
- $0.50/GB for additional storage
- Development branches: 1,440 hours/month included

**Development Branches ($5/month each)**
- Isolated development copies

**Metal Instances ($50/month)**
- M-10 configuration
- Reduced from $589/month
- For high-performance workloads

#### Underlying Database

- **MySQL 8.0+** via Vitess (sharding middleware)
- ACID transactions
- InnoDB storage engine
- Standard MySQL compatibility

#### Serverless Model

- **Vitess-based sharding:** Distributes load across horizontal partitions
- Managed infrastructure
- Auto-scaling at shard level
- High availability by default

#### Edge Support

- **No native edge support**
- Regional deployments
- Can be paired with edge functions

#### Branching (MySQL-Specific)

**Git-Like Database Branching:**
- Development branches (schema-only or with data)
- Production branches (multi-replica HA)
- Zero-downtime deployments
- Schema migration testing

**Production Branch Features:**
- Single primary + 2 replicas by default
- Automatic failover
- Read-only replica regions

#### Realtime Features

- None built-in
- Polling required for application-level sync

#### Auth Integration

- None (bring-your-own)

#### File Storage

- None

#### Backup & Restore

- Automatic backups included
- Point-in-time recovery available
- Retention: 30 days on higher tiers

#### Vendor Lock-in: **2/5 (Low)**

- Standard MySQL (portable)
- Vitess is open-source
- Export/import via mysqldump
- Can migrate to self-hosted MySQL

#### Developer Experience

- Web console
- GitHub integration for CI/CD
- MySQL-standard tooling works
- CLI available

#### Key Insight (2026)

PlanetScale signaled shift toward smaller entry points ($5 single-node). Good for MySQL users but faces competition from Postgres solutions on cost.

---

### 5. D1: Cloudflare's Serverless Database

**Overview:** SQLite database deeply integrated with Cloudflare Workers, deployed globally at edge.

#### Pricing & Free Tier

**Free Plan**
- 5M rows read/day
- 100k rows write/day
- 5 GB storage

**Paid Plan ($5/month)**
- 25B rows read included
- 50M rows write included
- 5 GB storage
- Additional: $0.001/M reads, $1/M writes, $0.75/GB storage

**Billing Note:** No charges for non-active databases (unlike traditional serverless).

#### Underlying Database

- **SQLite** (standard)
- ACID transactions
- JSON support
- Full-text search

#### Serverless Model

- **Query-based billing:** No compute/throughput charges
- Integrated with Workers ecosystem
- Global replication via Cloudflare network
- Near-zero latency from Worker code

#### Edge Support (Native)

- **D1 is edge-first**
- Database replicas distributed globally
- Read replication (no extra charges)
- No egress charges for local access

#### Branching

- Limited branching support
- Time-Travel backup (30-day recovery)

#### Realtime Features

- None (use Workers + polling for pseudo-realtime)

#### Auth Integration

- None (integrate with Worker auth logic)

#### File Storage

- None (use Cloudflare R2 for object storage)

#### Backup & Restore

- **Time Travel:** Restore to any minute in last 30 days
- Automatic backups included

#### Vendor Lock-in: **4/5 (High)**

- Tightly coupled to Cloudflare ecosystem
- SQLite portable, but D1 integration is proprietary
- Migration out requires export + new setup

#### Developer Experience

- Wrangler CLI integration
- Workers TypeScript SDK
- Query builder support (DrizzleORM, SQL.js)
- Deep integration with Cloudflare stack

#### Storage Limits (Increased 2025)

- **Free plan:** 500 MB per database, 10 databases max
- **Paid plan:** 10 GB per database (up from 2 GB), 50k databases max
- **Total account limit:** 1 TB (up from 250 GB)

#### Best For

- Cloudflare-native stacks
- Edge functions + database combo
- Simple OLTP workloads

---

### 6. CONVEX: Reactive Backend Database

**Overview:** Open-source reactive database where data mutations automatically update connected clients via TypeScript.

#### Pricing & Free Tier

**Free Developer Plan**
- Up to 6 people on team
- Resource limits
- Full feature access

**Starter Plan (Pay-as-you-go)**
- Pay only for extra resources beyond free quota
- Scaling up to Professional features
- Mid-tier option (introduced 2025)

**Professional Plan**
- Flat fee per seat
- Higher resource limits
- Additional usage charges

**Startup Program**
- Up to 1 year free
- 30% off usage up to $30k
- No seat fees

#### Underlying Database

- **Proprietary reactive data model**
- Not a traditional SQL database
- TypeScript-native query language
- Document-oriented storage

#### Serverless Model

- **Fully managed**
- Automatic scaling
- No infrastructure management
- Real-time synchronization built-in

#### Edge Support

- Regional deployments
- Caching layers for edge access
- Not edge-distributed like Turso

#### Branching

- No branching feature (not applicable to reactive model)

#### Realtime Features (Core Strength)

- **Automatic client sync:** Data changes propagate instantly
- **Reactive queries:** Components re-render when data changes
- **Conflict resolution:** Built-in
- **WebSocket subscriptions:** Automatic

#### Auth Integration

- Built-in authentication system
- Token management
- Session handling

#### File Storage

- None (use external storage)

#### Backup & Restore

- Automatic cloud backups
- Point-in-time recovery available

#### Vendor Lock-in: **3/5 (Medium)**

- Proprietary data model (harder to migrate)
- Open-source backend (self-hosting possible)
- Export/import tooling available

#### Developer Experience (Excellent for React/TypeScript Teams)

- TypeScript-first API
- React hooks for data binding
- Automatic component subscriptions
- Leptos support (Rust)
- AI-friendly (easy to reason about state)
- Components ecosystem (pre-built modules)

#### Adoption Status (2025-2026)

- Growing adoption in startups
- Strong in real-time collaborative apps
- Expansion into AI agents
- Competition from Replicache + traditional backends

#### When to Use Convex

- **Real-time collaborative apps** (Figma-like)
- **AI agents** with reactive backends
- **TypeScript/React teams** wanting full-stack type safety
- **Multiplayer games**
- **Chat applications**

---

### 7. FIREBASE: Google's Platform (2025 Update)

**Overview:** Google's matured Backend-as-a-Service with two NoSQL databases and comprehensive tooling.

#### Pricing & Free Tier (Spark Plan)

**Spark Plan (Free)**
- 1 GB stored data
- 50k reads/day
- 20k writes/day
- 20k deletes/day
- No active projects allowed (development only)

**Blaze Plan (Pay-as-you-go)**
- Required for production

#### Cost Breakdown (Per Operation)

| Operation | Cost |
|---|---|
| Reads | $0.18 per 100k |
| Writes | $0.18 per 100k |
| Deletes | $0.02 per 100k |
| Storage | $0.26 per GB/month |
| Egress (Internet) | $0.12 per GB |
| Egress (Google Cloud) | Free (same region) / $0.01 (different region) |

#### Firestore Enterprise Edition (New)

- Shift from per-document to per-unit (tranche) billing
- Separates real-time updates cost
- Lower per-operation costs at scale

#### Two Database Options

**Firestore (Recommended)**
- Document-oriented
- Real-time synchronization
- Offline support
- Automatic indexing
- Better for mobile apps

**Realtime Database (Legacy)**
- JSON tree structure
- WebSocket-based
- Lower latency for some use cases

#### Serverless Model

- Fully managed, auto-scaling
- No compute provisioning
- Billing per operation

#### Edge Support

- Regional deployments
- Not globally distributed like Turso

#### Realtime Features (Excellent)

- **Firestore Realtime Listeners:** Automatic client sync
- **Offline persistence:** Automatic local caching
- **Conflict resolution:** Server wins
- Native mobile SDKs

#### Auth Integration (Built-in)

- Firebase Authentication
- Email/password, OAuth, phone, custom tokens
- Session management
- MFA support

#### File Storage

- Cloud Storage integration
- Automatic authentication
- CDN caching

#### Backup & Restore

- Automated backups
- Point-in-time recovery via export
- Retain backups up to 30 days

#### Vendor Lock-in: **5/5 (Very High)**

- Proprietary Firestore data model
- No self-hosting option
- Deep Google Cloud integration
- Expensive to migrate away from

#### Developer Experience

- Mobile-first SDKs (iOS, Android)
- Web SDK
- Real-time by default
- Offline support excellent
- But: Firestore queries are limited compared to SQL

#### Firebase vs Supabase (2025 Verdict)

| Criteria | Firebase | Supabase | Winner |
|---|---|---|---|
| **Mobile Apps** | Superior offline/real-time | Good but requires more config | Firebase |
| **Web Apps** | Excellent | Excellent | Tie |
| **Complex Queries** | Limited (NoSQL) | Excellent (SQL) | Supabase |
| **Cost at Scale** | Higher (per-doc pricing) | Lower (predictable) | Supabase |
| **Vendor Lock-in** | Very high | Medium | Supabase |
| **Migration Difficulty** | Hard to leave | Easier to self-host | Supabase |
| **Google Integration** | Native | Limited | Firebase |

#### When to Choose Firebase (2025)

- Mobile-first apps (iOS/Android)
- Need native offline support
- Building within Google Cloud ecosystem
- Teams already using Google services
- Real-time is non-negotiable

#### When to Choose Supabase

- Traditional web apps
- Need PostgreSQL power
- Complex queries required
- Cost is concern
- Considering self-hosting

---

## REALTIME & SYNCHRONIZATION ANALYSIS

### 2025 Trends

**Change Data Capture (CDC)** is the new backbone of real-time systems:
- Captures every row change instantly
- Drives data pipelines
- Pub/Sub distribution model standard
- Market growth: 15%+ CAGR (2025-2033)

### Implementation Patterns

| **Pattern** | **Supabase** | **Neon** | **Turso** | **Convex** | **Firebase** |
|---|---|---|---|---|---|
| **Method** | WebSocket (LISTEN/NOTIFY) | Polling | Sync protocol | Reactive model | WebSocket listener |
| **Latency** | Sub-second | N/A | On-sync (configurable) | Real-time | Real-time |
| **Offline** | Requires custom | N/A | ✓ Built-in | ✓ Built-in | ✓ Built-in |
| **Conflict Resolution** | Application-level | N/A | Last-Push-Wins | Automatic | Server-wins |

### Tools Supporting Real-Time (2025)

- **PowerSync:** Postgres/MongoDB → SQLite sync
- **Realm:** Mobile database with cloud sync
- **Debezium:** CDC platform (Kafka-based)
- **Apache Kafka:** Streaming backend

---

## VENDOR LOCK-IN DEEP DIVE

### Lock-In Scores Explained

**1/5 (Turso):** Standard SQLite, open libSQL, minimal proprietary tie-ins
**2/5 (Neon, PlanetScale):** Standard SQL dialects, portable schemas
**3/5 (Supabase, Convex):** Some proprietary features, open-source core helps
**4/5 (D1):** SQLite portable but D1 integration proprietary
**5/5 (Firebase):** Firestore model completely non-standard, very difficult migration

### Mitigation Strategies (2025)

1. **Multi-Cloud Serverless:** Emerging pattern to avoid single vendor
2. **Open Standards:** GraphQL, REST APIs reduce SQL dialect lock-in
3. **Data Portability:** Regular exports to object storage
4. **Architecture Planning:** Decouple business logic from database specifics
5. **Hybrid Approaches:** Combine databases (e.g., Postgres for transactional + SQLite for edge)

### Migration Complexity (Production Workloads)

| **From → To** | **Difficulty** | **Timeline** | **Notes** |
|---|---|---|---|
| Firebase → Supabase | High | 2-4 weeks | Data transformation required |
| Supabase → Neon | Low | 1-2 days | Both Postgres, pg_dump works |
| Neon → PlanetScale | High | 1-2 weeks | MySQL incompatible with Postgres |
| Turso → Local SQLite | Very Low | <1 hour | File-based portability |
| D1 → Turso | Low | <1 day | Both SQLite |

---

## DECISION LOGIC & SELECTION MATRIX

### IF/THEN Rules for Platform Selection

```
IF mobile-first app + offline required
  THEN Firebase or Convex (if real-time)

IF need PostgreSQL power + self-hosting
  THEN Supabase or Neon

IF cost optimization + read-heavy
  THEN Neon (pay-per-compute) or Turso (pay-per-rows)

IF edge-distributed + offline
  THEN Turso (embedded replicas)

IF MySQL + branching + CI/CD
  THEN PlanetScale

IF Cloudflare ecosystem
  THEN D1

IF real-time collaborative app + TypeScript
  THEN Convex

IF avoiding vendor lock-in
  THEN Turso or Neon (self-hostable Postgres)

IF scaling from startup → enterprise
  THEN Supabase (most flexible growth path)
```

---

### Selection Flowchart Decision Tree

```
START
│
├─ "Is this a mobile app?"
│  ├─ YES → "Need offline?"
│  │         ├─ YES → Firebase
│  │         └─ NO → Supabase + native SDKs
│  └─ NO → "Do you need real-time collaboration?"
│          ├─ YES → Convex (TypeScript) or Supabase (if SQL needed)
│          └─ NO → "What database preference?"
│                   ├─ PostgreSQL → Supabase or Neon
│                   ├─ MySQL → PlanetScale
│                   └─ SQLite → Turso or D1
│
├─ "Is cost critical?"
│  ├─ YES → "Usage pattern?"
│  │         ├─ Read-heavy → Neon (autoscale down to zero)
│  │         ├─ Edge-distributed → Turso (pay-per-rows)
│  │         └─ Spiky → Convex (pay-as-you-go)
│  └─ NO → Supabase (predictable all-in-one cost)
│
└─ "Self-hosting required?"
   ├─ YES → Supabase (Docker), Neon (partial), or Turso (libSQL)
   └─ NO → Any platform is viable
```

---

## 2025-2026 MARKET TRENDS

### 1. **Postgres Renaissance**

Both Supabase and Neon report growing adoption:
- Traditional web apps moving from NoSQL back to SQL
- Developer familiarity with Postgres
- Cost advantages over Firebase at scale

### 2. **Edge Computing Convergence**

- SQLite becoming the edge database of choice (Turso, D1)
- Local-first sync patterns gaining adoption
- AI agents driving edge-distributed database demand

### 3. **Cost Awareness**

- Firebase Firestore pricing criticized for unpredictability
- Supabase/Neon gaining market share on cost-conscious projects
- Pay-as-you-go models replacing fixed pricing

### 4. **Open Source Advantages**

- Self-hosting Supabase becoming mainstream
- Neon's open-source internals building trust
- Turso's libSQL portability attractive

### 5. **Reactive Databases Emerging**

- Convex growing rapidly in startup ecosystem
- Real-time collaboration expected by default
- TypeScript-first backends resonating with modern teams

---

## IMPLEMENTATION RECOMMENDATIONS

### Small Startup (MVP Phase)

- **Primary:** Supabase Free Tier
- **Alt:** Turso Free ($0) if edge-distributed
- **Why:** All-in-one stack, low barrier to entry

### Growing Startup (10-100k MAU)

- **Primary:** Supabase Pro ($25-75/mo) or Neon Launch ($19/mo)
- **Why:** Cost optimization begins, branching helps
- **Consider:** Split database (Postgres + Turso) if edge needed

### Scale-Up (100k-1M MAU)

- **Primary:** Neon Scale ($69/mo) or Supabase with overages
- **Secondary:** Turso for edge (Embedded Replicas)
- **Why:** Cost per transaction becomes favorable

### Enterprise (1M+ MAU)

- **Primary:** Supabase Enterprise or Neon Business
- **Secondary:** Multi-database strategy (Postgres + specialized)
- **Backup:** Consider self-hosting Supabase for data sovereignty

### Collaborative/Real-Time Apps

- **Primary:** Convex
- **Alt:** Supabase with external realtime layer
- **Why:** Convex reactive model built for this use case

### Mobile-First Apps

- **Primary:** Firebase (if cost not concern)
- **Alt:** Supabase + sync layer (PowerSync)
- **Why:** Firebase offline support superior

### Distributed/Offline-First

- **Primary:** Turso with Embedded Replicas
- **Alt:** PowerSync + Postgres
- **Why:** Edge replication + local-first sync

---

## COST ESTIMATION EXAMPLES (2025 Pricing)

### Scenario: B2B SaaS, 100k MAU, read-heavy (10:1 ratio)

**Monthly Ops:** 500k reads, 50k writes

| **Platform** | **Base** | **Usage** | **Total** | **Notes** |
|---|---|---|---|---|
| **Supabase** | $25 | $10-20 | $35-45 | Predictable, includes storage |
| **Neon** | $19 | $5-15 | $24-34 | Scale-based, cheaper compute |
| **Firebase** | $0 | $90-120 | $90-120 | Read pricing unpredictable |
| **Turso** | $5 | $0-50 | $5-50 | Row-based, scales well |
| **D1** | $5 | $25-75 | $30-80 | Query-based, Cloudflare coupling |

**Winner:** Neon ($24-34) or Turso ($5-50)

### Scenario: Real-Time Collab App, 10k MAU, write-heavy (1:3 ratio)

**Monthly Ops:** 50k reads, 150k writes

| **Platform** | **Base** | **Usage** | **Total** |
|---|---|---|---|
| **Convex** | $0 | $50-150 | $50-150 |
| **Supabase** | $25 | $30-50 | $55-75 |
| **Firebase** | $0 | $120-180 | $120-180 |

**Winner:** Convex ($50-150) for real-time, Supabase ($55-75) for SQL

---

## OUTAGE & RELIABILITY COMPARISON

### 2025-2026 Incident Data

**Supabase**
- Uptime: 99.9% (Standard)
- 90-day incidents: 27 (13 major, 14 minor)
- Median MTTR: 1h 52m
- Recent: Cloudflare upstream issue (Jun 2025)

**Firebase**
- Uptime: 99.95% (better than Supabase)
- Fewer public incidents
- Google SLA backing

**Neon**
- Improving reliability through 2025
- Open-source architecture aids trust
- Fewer major incidents reported

**Turso**
- Emerging player, less incident history
- Global distribution improves resilience
- Embedded replicas = no single point of failure

### Reliability Recommendations

1. **For Mission-Critical:** Firebase (Google SLA) or Supabase Enterprise
2. **For Cost-Conscious:** Neon (improving track record)
3. **For Distributed:** Turso (inherently resilient)

---

## SELF-HOSTING & DATA SOVEREIGNTY

### Self-Hosting Viability (2025)

| **Platform** | **Viability** | **Complexity** | **Cost** |
|---|---|---|---|
| **Supabase** | Excellent | Docker (30 min) | Infrastructure only |
| **Neon** | Partial | Forking required | High |
| **Turso** | Good | libSQL open-source | Infrastructure only |
| **PlanetScale** | Moderate | Vitess setup complex | Infrastructure high |
| **D1** | Not available | N/A | N/A |
| **Firebase** | Not available | N/A | N/A |

### Supabase Self-Hosting (2025 Recommended Setup)

```bash
# Docker deployment (<30 min)
docker-compose up -d

# Recommended with:
- NGINX reverse proxy
- Dokploy or EasyPanel for UI
- Active 2025 community deployments
```

### Turso Self-Hosting (libSQL)

```bash
# Build from open-source
# Deploy on your infrastructure
# Full control, no vendor lock-in
```

---

## KEY FEATURES COMPARISON TABLE

| **Feature** | **Supabase** | **Neon** | **Turso** | **PlanetScale** | **D1** | **Convex** | **Firebase** |
|---|---|---|---|---|---|---|---|
| **REST API** | Auto | Via PostgREST | Via HTTP | Via REST | Via Workers | Type-safe | SDK only |
| **GraphQL** | Community | Community | No | No | No | No | No |
| **Row Level Security** | ✓ Native | ✓ Native | No | No | No | No | Via rules |
| **Full-Text Search** | ✓ PostgreSQL | ✓ PostgreSQL | ✓ SQLite | Limited | ✓ SQLite | No | No |
| **Vector Search** | ✓ pgvector | ✓ pgvector | ✓ Built-in | No | No | No | No |
| **Time-Travel** | Export-based | Backups | Branches | Branches | Time Travel | No | Export-based |
| **Multi-Tenant** | ✓ RLS | ✓ RLS | Branches | Branches | No | No | Firestore rules |
| **ACID Transactions** | ✓ Full | ✓ Full | ✓ Full | ✓ Full | ✓ SQLite | ✓ Optimistic | ✓ Per-doc |
| **Transactions (Multi-Shard)** | N/A | ✓ Cross-shard | N/A | No (Vitess) | N/A | ✓ | Limited |

---

## SUMMARY RECOMMENDATIONS

### Best Overall Platform (2025): **Supabase**

- Full-stack solution (database + auth + storage + functions)
- PostgreSQL power + reasonable pricing
- Self-hosting available for data sovereignty
- Active development and large community

### Best for Cost-Optimization: **Neon**

- Compute autoscaling (pay only when active)
- SQL-first approach
- 30% cheaper than Supabase at scale
- Excellent branching for development

### Best for Edge: **Turso**

- Embedded replicas for global distribution
- Offline-first sync capabilities
- Minimal vendor lock-in
- Lowest entry price ($0)

### Best for Collaborative Real-Time: **Convex**

- Reactive data model perfectly suited for multiplayer
- TypeScript-first, great DX
- Automatic conflict resolution
- Growing adoption in startup ecosystem

### Best for Mobile: **Firebase**

- Native offline support unmatched
- Superior real-time synchronization
- Deep mobile SDK integration
- Trade-off: Vendor lock-in and cost

### Best for Avoiding Lock-In: **Turso** or **Self-Hosted Supabase**

- Turso: File-based SQLite portability
- Supabase: Open-source, Docker-deployable

---

## SOURCES & REFERENCES

- [Supabase Pricing](https://supabase.com/pricing)
- [Supabase Review 2026](https://coldiq.com/tools/supabase)
- [Supabase Pricing Breakdown](https://www.srvrlss.io/provider/supabase/)
- [Neon Pricing & Cost Comparison](https://neon.com/)
- [ByteBase Neon vs Supabase](https://www.bytebase.com/blog/neon-vs-supabase/)
- [PlanetScale Pricing](https://planetscale.com/pricing)
- [PlanetScale $5 Announcement](https://planetscale.com/blog/5-dollar-planetscale-is-here)
- [Turso Database Features](https://turso.tech/)
- [Turso Pricing](https://turso.tech/pricing)
- [Turso Embedded Replicas](https://docs.turso.tech/features/embedded-replicas/introduction)
- [Cloudflare D1 Pricing](https://developers.cloudflare.com/d1/platform/pricing/)
- [D1 Overview](https://developers.cloudflare.com/d1/)
- [Convex Pricing](https://www.convex.dev/pricing)
- [Convex Architecture](https://docs.convex.dev/understanding/)
- [Firebase Pricing](https://firebase.google.com/pricing)
- [Firestore Pricing Guide](https://firebase.google.com/docs/firestore/pricing)
- [Firebase Cost Analysis](https://supertokens.com/blog/firebase-pricing)
- [Supabase Status & Uptime](https://status.supabase.com/)
- [Supabase SLA](https://supabase.com/sla)
- [Neon Branching](https://neon.com/docs/introduction/branching)
- [Supabase Self-Hosting](https://supabase.com/docs/guides/self-hosting)
- [Supabase vs Firebase 2025](https://www.leanware.co/insights/supabase-vs-firebase-complete-comparison-guide)
- [Supabase Auth JWT](https://supabase.com/docs/guides/auth/jwts)
- [Serverless Vendor Lock-in](https://www.serverless.com/blog/data-lockin-vendor-choice-portability)
- [Real-Time Synchronization 2025](https://skyvia.com/learn/what-is-data-synchronization)
- [Turso Edge Replication](https://turso.tech/blog/introducing-embedded-replicas-deploy-turso-anywhere-2085aa0dc242)

---

## Document Metadata

- **Research Date:** February 19, 2026
- **Data Currency:** As of February 2026
- **Next Review:** August 2026 (6-month cycle recommended)
- **Scope:** Pricing, features, and reliability as of publication date
- **Disclaimer:** Pricing and features subject to change; verify directly with providers before architectural decisions

---

*This guide is intended for architects and technical decision-makers evaluating serverless and edge database platforms in 2025-2026.*

## Related References
- [Relational Databases](./07-databases-relational.md) — Self-managed database options for comparison
- [NoSQL Databases](./08-databases-nosql.md) — Document and key-value alternatives
- [Serverless Hosting](./11-hosting-serverless.md) — Function and compute services for serverless stacks
- [Cost Traps & Real-World Challenges](./40-cost-traps-real-world.md) — Hidden costs and pricing surprises
- [Multi-Tenancy Patterns](./56-multi-tenancy-patterns.md) — Isolation strategies in shared databases

<!-- PRICING_STABILITY: HIGH_VOLATILITY | Updated: 2026-03-03 | Cloud/SaaS pricing changes quarterly. Verify current pricing at provider websites before recommending. -->
