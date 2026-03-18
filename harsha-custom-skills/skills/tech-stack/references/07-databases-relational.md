# Relational Databases: PostgreSQL, MySQL, SQLite, CockroachDB, MariaDB
## Comprehensive Reference Document (2025/2026)

**Last Updated:** February 2026
**Research Scope:** Database versions, features, ACID compliance, pricing, managed services, and decision logic

## Executive Summary (5-line TL;DR)
- PostgreSQL is the default relational DB for 90%+ of projects: JSON/JSONB, full-text search, extensions, free
- MySQL 8.0+ still dominates WordPress/PHP ecosystems; Aurora MySQL for AWS-heavy enterprise stacks
- SQLite is ideal for embedded, mobile, edge, and single-server apps (Turso/libSQL for distributed SQLite)
- CockroachDB/TiDB for global distributed SQL when you truly need multi-region writes (most don't)
- Managed options: Neon (serverless PG, branching), Supabase (PG + auth + realtime), RDS (enterprise standard)

---

## Table of Contents
1. [Core Database Comparison](#core-database-comparison)
2. [Database Feature Matrix](#database-feature-matrix)
3. [Detailed Database Profiles](#detailed-database-profiles)
4. [SQLite Renaissance: Production Patterns](#sqlite-renaissance-production-patterns)
5. [PostgreSQL Deep Dive](#postgresql-deep-dive)
6. [Managed Service Pricing Comparison](#managed-service-pricing-comparison)
7. [Decision Logic Framework](#decision-logic-framework)
8. [Cost Optimization Strategies](#cost-optimization-strategies)

---

## Core Database Comparison

### Quick Overview Table

| Database | Current Version | Type | Primary Use Case | Production Readiness |
|----------|-----------------|------|------------------|----------------------|
| PostgreSQL | 17.x (latest: 17.7) | Open Source | High concurrency, complex queries | ⭐⭐⭐⭐⭐ Enterprise-grade |
| MySQL | 8.4 LTS (8.4.8) | Open Source | Web applications, scalability | ⭐⭐⭐⭐⭐ Battle-tested |
| SQLite | 3.45.0+ | Embedded | Single-user, edge, mobile | ⭐⭐⭐⭐⭐ New production patterns |
| CockroachDB | 24.x+ (serverless) | Distributed SQL | Global scale, HA requirements | ⭐⭐⭐⭐ Specialized |
| MariaDB | 11.8 LTS | MySQL-compatible | MySQL migration path | ⭐⭐⭐⭐ Community-driven |

---

## Database Feature Matrix

### ACID Compliance

**PostgreSQL:**
- Status: Fully ACID-compliant since 2001
- Implementation: MVCC (Multiversion Concurrency Control) for optimal concurrent access
- Strength: Strongest ACID guarantees, robust data integrity
- Ideal for: Financial systems, data warehouses, mission-critical applications
- Advanced features: Nested transactions, savepoints, advisory locks

**MySQL (InnoDB):**
- Status: ACID-compliant with InnoDB storage engine (required)
- Implementation: MVCC for InnoDB (limited in other engines)
- Strength: Good ACID compliance when using InnoDB (default in MySQL 8.x)
- Caveat: ACID compliance depends on storage engine selection
- Note: MyISAM and other engines lack ACID support

**SQLite:**
- Status: Fully ACID-compliant
- Implementation: Single-threaded, file-locking based
- Strength: Zero-configuration, reliable for single-process access
- Limitation: Limited concurrent write capability due to file-level locks
- 2025 Update: Improved with new threading modes for better concurrency

**CockroachDB:**
- Status: Fully ACID-compliant with distributed transactions
- Implementation: Multi-region, MVCC with distributed consensus (Raft)
- Strength: Global ACID guarantees across geographic regions
- Unique: Serializable isolation level by default

**MariaDB:**
- Status: ACID-compliant (MySQL-compatible implementation)
- Implementation: InnoDB-based (default)
- Strength: MySQL-compatible with additional enterprise features
- Compatibility: Drop-in replacement for MySQL 8.x applications

---

### JSON Support

**PostgreSQL:**
- JSON type: Both `JSON` and `JSONB` types available
- JSONB advantages: Binary format, indexable, faster queries
- Full-Text Search: Native `to_tsvector()` function for JSON content
- GIN indexes: Efficient indexing for JSONB queries
- Extensions: PGroonga for advanced JSON full-text search
- Use case: Document storage, semi-structured data, API responses
- PostgreSQL 17: Added SQL/JSON `JSON_TABLE` command for better developer experience

**MySQL:**
- JSON type: Native `JSON` data type
- Functions: `JSON_SEARCH()`, `JSON_EXTRACT()`, `JSON_CONTAINS()`
- Indexing: Multi-value indexes (MySQL 8.0.17+) for JSON arrays
- Limitation: Limited native full-text search on JSON columns
- Use case: API responses, document storage, flexible schemas
- MySQL 8.4: Improved JSON manipulation and querying capabilities

**SQLite:**
- JSON Support: Native JSON functions in SQLite 3.38.0+
- Functions: `json_extract()`, `json_array()`, `json_object()`
- Limitation: No built-in JSON indexing
- Use case: Mobile apps, embedded JSON data, simple queries
- Turso/libSQL: Enhanced JSON support with native vector search

**CockroachDB:**
- JSON type: Native `JSONB` support (PostgreSQL-compatible)
- Full-Text Search: Can use PostgreSQL extensions
- Indexing: GIN indexes available
- Use case: Document storage, distributed applications

**MariaDB:**
- JSON type: Native JSON support (MySQL-compatible)
- Functions: Full JSON function library
- Use case: API responses, document storage
- Note: Similar capabilities to MySQL 8.4

---

### Full-Text Search

**PostgreSQL:**
- Native support: `tsvector` and `tsquery` types
- Languages: Multiple language configurations available
- Ranking: `ts_rank()` and `ts_rank_cd()` functions
- Indexes: GiST and GIN indexes for fast queries
- Advanced: Can combine with JSON for JSON content search
- Extensions: PGroonga for language-agnostic full-text search
- Performance: Efficient for moderate to large text datasets

**MySQL:**
- Native support: `FULLTEXT` index type
- Methods: Two modes (boolean mode and natural language mode)
- Limitations: Configurable minimum word length, stopwords
- Use case: Basic full-text search needs
- Integration: Can search multiple columns simultaneously
- Performance: Good for moderate datasets, alternative to Elasticsearch

**SQLite:**
- FTS5: Full-text search module available (FTS5)
- Capability: Advanced tokenization, phrase queries, ranking
- Use case: Mobile apps, embedded search functionality
- Integration: Separate module, must be explicitly enabled

**CockroachDB:**
- No native full-text search
- Workaround: Use PostgreSQL extensions or Elasticsearch integration

**MariaDB:**
- FULLTEXT support inherited from MySQL
- Methods: Boolean and natural language modes
- Performance: Suitable for most web applications

---

### Replication & High Availability

**PostgreSQL:**
- Types: Streaming (physical) and logical replication
- Streaming: Real-time WAL (Write-Ahead Logging) transfer
- Logical: Per-table replication, cross-version compatible
- Slots: Replication slots ensure no data loss during failover
- PostgreSQL 17: Enhanced logical replication with improved slot management
- Extensions: pglogical, Citus for advanced replication patterns
- Use case: Multi-datacenter, heterogeneous systems, logical filtering

**MySQL:**
- Native replication: Master-slave (primary-replica) architecture
- Binlog-based: Event-based replication
- Group Replication: Built-in HA with automatic failover
- Limitation: Unidirectional by default (though multi-source replication available)
- MySQL 8.4: Improved replication performance and reliability
- Topology: Supports multi-source replication for analytics

**SQLite:**
- Native replication: Not available
- Alternative: Litestream for asynchronous replication to S3
- Alternative: LiteFS for multi-region replication
- Use case: Small deployments, edge databases

**CockroachDB:**
- Native: Multi-region replication built-in
- Consistency: Synchronous replication across regions
- Failover: Automatic with no manual intervention
- Geographic: Optimized for global distribution

**MariaDB:**
- Replication: MySQL-compatible multi-source replication
- Galera Cluster: Synchronous multi-master replication option
- Performance: Active-active clustering with automatic failover

---

### Connection Pooling

**PostgreSQL:**
- PgBouncer: Industry-standard connection pooler
- Modes: Session, transaction, statement modes available
- Implementation: External service or managed (Supabase Supavisor)
- Pool size: Typically 20-50 connections per 1GB RAM
- Benefit: Reduces connection overhead, improves scalability
- Limitation: PgBouncer doesn't support prepared statements (in transaction mode)
- Supabase Supavisor (2025): New cloud-native pooler supporting 1M+ connections

**MySQL:**
- Connection pooling: Less built-in than PostgreSQL
- ProxySQL: Third-party solution for query routing and pooling
- MaxScale: MariaDB's official connection pooling solution
- Pooling level: Often handled at application level

**SQLite:**
- Single process: Connection pooling not applicable
- Application layer: Handled within single application instance
- Advantage: Zero connection management overhead

**CockroachDB:**
- Connection pooling: Handled automatically by CockroachDB
- Multi-node: Automatic connection distribution across cluster

**MariaDB:**
- MaxScale: Official pooling and routing solution
- Connection management: Application-level pooling recommended

---

### Extensions & Plugins

**PostgreSQL (Most Extensible):**
- **pg_vector**: AI embeddings, semantic search, vector similarity (0.8.0 = 9x faster)
- **PostGIS**: Geospatial data, GIS operations (v3.6.1 as of 2025)
- **Citus**: Distributed sharding and multi-tenant functionality
- **pglogical**: Logical replication with filtering
- **TimescaleDB**: Time-series optimization
- **JSON extensions**: PGroonga (full-text search on JSON)
- **Text search**: Full-text search capabilities (integrated)
- **Partitioning**: Native table partitioning support
- Total: 1000+ extensions available in PostgreSQL community

**MySQL:**
- Plugins: Limited plugin architecture
- Common: mysql_audit, validate_password, rsa_password_plugin
- Limitations: Fewer extensions than PostgreSQL
- Workaround: Often handled at application layer

**SQLite:**
- Extensions: Limited official extension system
- Loadable extensions: Custom functions can be loaded
- Turso/libSQL: Offers enhanced extension support
- libSQL vector: Native vector search extension

**CockroachDB:**
- PostgreSQL compatibility: Can use PostgreSQL-compatible extensions
- Limitations: Some extensions not fully supported in distributed mode

**MariaDB:**
- Plugins: MySQL-compatible plugin system
- MariaDB Vector: Native vector search (MariaDB 11.8 LTS first LTS with it)
- Storage engines: InnoDB, MyISAM, Aria, ColumnStore
- Compatibility: MySQL extension compatibility where applicable

---

### Maximum Database Size

| Database | Maximum Size | Details |
|----------|--------------|---------|
| PostgreSQL | Unlimited (theoretically) | 32TB per table, multiple tablespaces for distribution |
| MySQL | 16EB (exabytes) in theory | Practical limit ~1-10TB per instance (hardware dependent) |
| SQLite | 281TB (with 64KB pages) | 17.5TB (default 4KB pages); increased from earlier limits |
| CockroachDB | Unlimited | Distributed across nodes |
| MariaDB | 16EB (MySQL-compatible limit) | Practical limits similar to MySQL |

---

### Concurrent Connection Limits

| Database | Default Limit | Practical Max | Notes |
|----------|--------------|---------------|-------|
| PostgreSQL | 100 connections | 1000+ with tuning | Per-instance setting, configurable |
| MySQL | 151 connections | 10,000+ with tuning | `max_connections` setting |
| SQLite | 1 (single process) | N/A | File-based, single writer at a time |
| CockroachDB | Unlimited | 100,000+ | Distributed, scales with nodes |
| MariaDB | 151 connections (default) | 10,000+ with tuning | MySQL-compatible limits |

---

### Licensing

| Database | License Type | Commercial Support | Enterprise Features |
|----------|-------------|-------------------|-------------------|
| PostgreSQL | PostgreSQL License (BSD-like) | Multiple vendors (EDB, Crunchy, etc.) | No license restrictions |
| MySQL | GPL v2 / Commercial | Oracle support available | Dual-licensed for enterprises |
| SQLite | Public Domain | Professional support via Turso | No licensing restrictions |
| CockroachDB | Business Source License (v1.1) / Commercial | Cockroach Labs | Proprietary enterprise features |
| MariaDB | GPL v2 / Commercial | MariaDB Corporation | Open source core with paid support |

---

## Detailed Database Profiles

### PostgreSQL 17.x (2025 Latest: 17.7)

**Version Release Date:** October 2024
**Latest Patch:** 17.7 (November 2025)

**Key 2025 Features:**

1. **Performance**
   - Memory footprint reduction: Vacuum process uses 20x less memory
   - Bulk loading: 2x faster COPY with `ON_ERROR` option
   - High concurrency: Optimizations for concurrent workloads
   - Index performance: Query execution improvements

2. **Backup & Recovery**
   - Incremental backups: Store only changes since last backup
   - Faster recovery with smaller storage footprint

3. **Data Manipulation**
   - MERGE enhancements: RETURNING clause, view updates
   - MERGE PARTITIONS and SPLIT PARTITIONS commands
   - Improved partition management

4. **JSON Processing**
   - SQL/JSON `JSON_TABLE` command for better developer experience

5. **Logical Replication**
   - Preserved replication slots during pg_upgrade
   - Full subscription state preservation for seamless upgrades

6. **Monitoring**
   - EXPLAIN with I/O timing (SERIALIZE, MEMORY options)
   - `pg_wait_events` system view
   - Index vacuuming progress visibility

7. **Security**
   - Direct TLS handshake option: `sslnegotiation=direct`
   - Reduced connection negotiation round-trips

**Strengths:**
- Most feature-rich open-source database
- Excellent for complex queries and analytics
- Superior ACID compliance with MVCC
- Largest extension ecosystem
- Ideal for data integrity and multi-user scenarios

**Best For:**
- Financial systems, data warehouses, enterprise applications
- Complex relational data with complex queries
- Multi-tenant SaaS with row-level security (RLS)
- AI/ML applications (with pg_vector)
- Geographic/mapping applications (with PostGIS)

**Limitations:**
- Steeper learning curve than MySQL
- Vertical scaling more common than horizontal
- Disk I/O intensive for very large datasets

---

### MySQL 8.4 LTS (Latest: 8.4.8, Jan 2026)

**Version Release Date:** April 2024 (LTS)
**Latest Patch:** 8.4.8 (January 2026)
**Support:** 5 years premier, 3 years extended

**Key 2025 Features:**

1. **Compatibility**
   - CMake 4 support for future compatibility
   - Enhanced library support (libcurl, ICU, zstd)

2. **Multi-Source Replication**
   - For analytics and consolidation workloads

3. **Group Replication**
   - Continuous availability with automatic failover

4. **Default Character Set**
   - UTF8MB4 as default for full emoji and multilingual support

**Strengths:**
- Most widely deployed database globally
- Excellent for web applications and LAMP stack
- Good horizontal scaling with sharding
- Fast for read-heavy workloads
- Mature ecosystem and tooling

**Best For:**
- Web applications, content management systems
- High-concurrency read-heavy workloads
- SaaS platforms with simple to moderate schema complexity
- Multi-source replication scenarios (analytics)

**Limitations:**
- Less powerful for complex analytics queries
- ACID compliance only with InnoDB
- Full-text search limitations
- Scaling beyond single instance requires sharding

---

### SQLite 3.45.0+ (2025 Renaissance)

**Current Version:** 3.45.0+ (as of early 2025)
**License:** Public Domain

**2025 Production Patterns:**

The SQLite ecosystem has exploded in 2025 with new tooling making it viable for cloud-scale applications:

1. **libSQL (Production-Ready Fork)**
   - Maintained by Turso, fully backwards compatible
   - Native vector search capabilities
   - Async-first architecture option
   - Intended for mission-critical workloads

2. **Turso Database (Next Evolution)**
   - Rust rewrite of SQLite with async-first design
   - Not yet production-ready but rapidly evolving
   - Planned features: Concurrent writes, vector search, WASM

3. **LiteFS (Live Replication)**
   - FUSE-based file system for multi-node replication
   - Per-transaction change tracking (LTX format)
   - Distributed lease coordination (Consul)
   - Best for: Full control, Kubernetes-friendly, hard SLOs on consistency tokens

4. **Litestream (Disaster Recovery)**
   - Standalone asynchronous replication to S3 or cloud storage
   - Incremental backup with transaction-level granularity
   - New LTX format with compaction (2025 update)
   - VFS for read replicas with on-demand hydration
   - Best for: Single-node applications needing durability

**Why SQLite in 2025:**

```
IF:
  - Application: Single-user or low-concurrency
  - Scale: <1M records, <10GB data
  - Cost: Want to eliminate database costs
  - Latency: Need sub-millisecond local access
  - Deployment: Edge, serverless, mobile, embedded
THEN:
  - SQLite + Turso/libSQL is the optimal choice
ELSE:
  - Consider PostgreSQL or MySQL
```

**Maximum Database Size:** 17.5TB (default), 281TB (with 64KB pages)

**Key Advantages:**
- Zero-configuration, single file, embedded
- Microsecond query latency (local access)
- No server overhead, no network round-trips
- Excellent for edge computing and distributed edge databases
- Turso free tier: 500M row reads, 10M row writes, 5GB storage
- libSQL: Full SQLite compatibility plus vector search

**2025 Use Cases:**
- Edge databases with Turso/libSQL and LiteFS/Litestream replication
- Mobile and desktop applications
- IoT and embedded systems
- Local-first applications (with cloud backup via Litestream)
- Multi-region read-replicas with Turso

**When SQLite Beats PostgreSQL:**
1. Cost elimination: Turso free tier covers many small projects entirely
2. Latency-sensitive: Sub-millisecond local access vs network latency
3. Simplicity: No server management, migrations, or DevOps overhead
4. Edge deployment: Deploy to edge networks with Turso
5. Developer velocity: Simpler schema, less operational complexity

**Limitations:**
- Single writer at a time (traditional SQLite)
- Limited horizontal scaling
- Not ideal for high-concurrency write scenarios
- Requires Turso/LiteFS for multi-region replication

---

## SQLite Renaissance: Production Patterns

### The Shift in 2025

The traditional view of SQLite as "development-only" has fundamentally changed with three key innovations:

1. **libSQL/Turso**: Production-grade fork with additional features
2. **LiteFS**: Multi-region replication without server complexity
3. **Litestream**: Disaster recovery to cloud storage

### Architecture Pattern: Edge + Central

```
Global application with edge databases
```

### Cost Comparison: SQLite vs PostgreSQL (2025 Pricing)

**Small Application (500K records, 1GB):**

| Approach | Monthly Cost | Notes |
|----------|--------------|-------|
| Turso Free | $0 | 500M reads, 10M writes, 5GB storage |
| Turso Hobby ($4.99) | $4.99 | Upgrading from free tier |
| Neon Free (Postgres) | $0 | 100 CU-hours/month (double in Oct 2025) |
| Neon Pro (Postgres) | $15-50+ | Paid compute units |
| Supabase Free (Postgres) | $0 | 500MB DB, project pauses after 7 days |
| AWS RDS t3.micro | $15-25+ | Cheapest managed option |

**Verdict:** Turso/SQLite typically 5-10x cheaper for small projects

**When SQLite (Turso/libSQL) Wins in 2025:**

1. High-traffic read-heavy, low-write: SQLite shines with local caching
2. Cost-constrained startup: Free tier coverage is unmatched
3. Mobile-first or offline-first: SQLite native on device
4. Latency-critical (p50 < 10ms): Local SQLite beats any network call
5. Global read replicas: Turso edge databases cheaper than PostgreSQL replicas

### Production SQLite Stack (2025)

**Recommended Setup:**
1. Local Database: libSQL or SQLite 3.45.0+
2. Cloud Sync: Turso (libSQL-compatible)
3. High Availability: LiteFS (multi-region replication)
4. Disaster Recovery: Litestream → S3
5. Monitoring: SQLite query logging + alerting

---

## PostgreSQL Deep Dive

### AI/ML with pg_vector

**pg_vector Extension (0.8.0 in 2025):**

- **Storage:** Vector columns for embeddings (768-dim, 1536-dim, custom)
- **Distance Metrics:** L2 (Euclidean), Inner Product, Cosine similarity
- **Indexes:** HNSW (Hierarchical Navigable Small World) - fast approximate nearest neighbor
- **Performance:** 9x faster query processing in 0.8.0 vs previous versions
- **Cost Efficiency:** 40-80% cheaper than specialized vector databases for <100M vectors

**Managed Cloud Support (2025):**
- AWS RDS for PostgreSQL: pgvector available
- Google Cloud AlloyDB: pgvector + ScaNN index (Google Research)
- Azure Database for PostgreSQL: pgvector support
- Supabase: pgvector included in all tiers
- Neon: pgvector available

**Common Use Cases:**
1. Semantic Search: Find similar documents using embeddings
2. RAG (Retrieval-Augmented Generation): Store document embeddings for LLM context
3. Recommendation Systems: User-item similarity calculations
4. Duplicate Detection: Find near-duplicate records
5. Image Search: Store and search image embeddings

### PostGIS: Geospatial Data

**PostGIS 3.6.1 (November 2025):**

- **Spatial Data Types:** Points, lines, polygons, multigeometries
- **Operations:** Distance calculations, area measurements, spatial joins, containment tests
- **Indexes:** GiST-based R-Tree for fast spatial queries
- **Coordinate Systems:** PROJ 8.2.1 for geographic transformations
- **3D Support:** Volumetric analysis and 3D geometries
- **Raster Support:** Grid-based spatial data analysis
- **MVT Support:** MapBox Vector Tiles for web mapping
- **New (3.6.1):** pgSphere for spherical geometry management

**Use Cases:**
- Mapping and navigation applications
- Geographic information systems (GIS)
- Location-based services (nearby stores, restaurants)
- Real estate and property analytics
- Environmental monitoring
- Urban planning

### Citus: Distributed PostgreSQL

**Citus 13.0 (2025):**

**Sharding Options:**
1. Hash sharding: Distribute by hash of shard key
2. Range sharding: Partition by value ranges
3. Schema-based sharding: Full database schemas across nodes

**Architecture:**
- Coordinator node: Routes queries
- Worker nodes: Store shards, execute queries in parallel
- Every node is a full PostgreSQL database

**Key Features (Citus 13.0):**
- Correlated subquery pushdown (uses PostgreSQL 17 capabilities)
- Distributed planning for complex queries
- Multi-tenant isolation
- Real-time analytics on large datasets

**Use Cases:**
1. Multi-tenant SaaS: Isolate tenant data by shard
2. Time-series Analytics: Shard by tenant_id + time
3. Operational Analytics: Fast queries on large datasets
4. Real-time Reporting: Sub-second queries on billions of rows

### NOTIFY/LISTEN: Real-Time Features

**PostgreSQL Event Notifications:**

**Use Cases:**
1. Real-time Messaging: Pub/sub between applications
2. Cache Invalidation: Tell all servers to refresh caches
3. Live Updates: Notify web clients of database changes
4. Workflow Triggers: Start processes based on events
5. Change Notification: Alert subscribers to data modifications

**Advantages:**
- Built into PostgreSQL, no external message queue
- Zero configuration
- Low latency (milliseconds)
- Scales to millions of listeners per connection

### Row-Level Security (RLS) for Multi-Tenancy

**PostgreSQL RLS: Database-Level Isolation**

RLS enables policies that automatically filter rows based on current user context. This provides database-level enforcement preventing SQL bypass and per-row filtering with automatic WHERE clauses.

**Best Practices:**
- Use application context variables (set_config)
- Test policies thoroughly with different roles
- Never use superuser connections in applications
- Combine with column-level security for sensitive data

---

## Managed Service Pricing Comparison (2025/2026)

### Comprehensive Pricing Table

| Service | Database | Free Tier | Lowest Paid | Pricing Model | Notes |
|---------|----------|-----------|-------------|---------------|-------|
| **Turso** | SQLite | 500M reads, 10M writes, 5GB | $4.99/mo | Usage-based | Most generous free tier |
| **Neon** | PostgreSQL | 100 CU-hrs/mo (doubled Oct 2025) | $15/mo | Compute + storage | Recently reduced pricing 15-25% |
| **Supabase** | PostgreSQL | 500MB DB, 50K MAU | $25/mo | Hybrid: base fee + usage | Project pauses after 7 days idle |
| **PlanetScale** | MySQL | Removed (as of 2025) | $34/mo | Usage-based | Free tier discontinued |
| **Xata** | PostgreSQL | 15GB storage, free tier | Dev instance $18/mo | Instance hours + storage | Removed search/files Jan 2025 |
| **AWS RDS** | PostgreSQL/MySQL | 750 hrs/yr Free Tier | $13-20/mo | Instance + storage | Very flexible |
| **Render** | PostgreSQL | Free static site only | $15/mo | Usage or fixed | Limited DB options |
| **Railway** | PostgreSQL | $5 credits/30 days | $20/mo Pro | Usage-based | Good for iteration |
| **Vercel Postgres** | PostgreSQL | N/A | Free with Vercel | Bundled | Only if using Vercel |
| **CockroachDB** | Distributed SQL | $15/mo free tier | $29/mo | Usage-based (RUs + storage) | Serverless from zero |

---

### Free Tier Leaders (2025)

**Best for Building:** Turso (500M reads!)
- 500 million row reads per month
- 10 million row writes per month
- 5GB storage
- No credit card required
- No automatic pause
- Commercial use allowed

**Best PostgreSQL Free:** Neon
- 100 CU-hours per month (doubled Oct 2025)
- 100 projects with separate allowances
- No auto-pause feature
- No credit card required

---

## Decision Logic Framework

### IF/THEN Decision Tree for Database Selection

**DECISION 1: Scale & Complexity**
- Simple schema, <100K records: Consider SQLite (Turso) or MySQL
- Complex schema, multi-table joins: PostgreSQL strongly recommended
- Global scale, multi-region: CockroachDB

**DECISION 2: Concurrency Requirements**
- Single-user or low (<10 concurrent): SQLite is excellent and cheapest
- Medium concurrency (10-1000): PostgreSQL or MySQL with pooling
- Very high concurrency (1000+): PostgreSQL + Citus, or MySQL + sharding

**DECISION 3: Cost & Operations**
- Minimize cost, can use SQLite: Turso free ($0-29/mo)
- Want managed PostgreSQL: Neon free ($0) or $15+/mo
- Want managed MySQL: AWS RDS free ($0) or $13+/mo
- Don't manage servers: CockroachDB Basic ($15+/mo) or Supabase

**DECISION 4: Feature Requirements**
- Need geospatial (PostGIS): PostgreSQL only
- Need AI embeddings (pg_vector): PostgreSQL or MariaDB 11.8+
- Need distributed sharding: PostgreSQL + Citus, CockroachDB, or MySQL
- Need multi-tenancy with RLS: PostgreSQL (best)
- Need complex full-text search: PostgreSQL (built-in + extensions)

**DECISION 5: Replication & HA**
- Single region, acceptable downtime: No replication needed
- Single region, high availability: PostgreSQL streaming, MySQL Group, or CockroachDB
- Multi-region global distribution: CockroachDB (native), PostgreSQL logical, or Turso + LiteFS
- Disaster recovery only: Litestream (SQLite to S3) or pg_basebackup

**DECISION 6: Deployment Model**
- Serverless/FaaS: SQLite (Turso) best, or managed PostgreSQL (Neon, Supabase)
- Kubernetes/self-hosted: PostgreSQL or MySQL
- Edge/global distribution: Turso (edge databases) or PostgreSQL with replicas
- Traditional VPS/cloud: Any option works; PostgreSQL recommended

---

### Decision Matrix by Use Case

**Startup MVP:** Turso (SQLite) - Free tier, $0-10/month, minimal ops
**E-commerce Platform:** PostgreSQL - Complex schema, transactions, $30-200/month
**Social Network:** PostgreSQL or CockroachDB - High concurrency, $100-500+/month
**Real-Time Analytics:** PostgreSQL + Citus - Distributed queries, $200-1000+/month
**SaaS Multi-Tenant:** PostgreSQL with RLS - Strict isolation, $50-500+/month
**Mobile App:** SQLite locally + Turso - Offline-first sync, $0-15/month
**Geographic/Mapping:** PostgreSQL + PostGIS - Geospatial only, $30-200+/month
**AI/ML Workload:** PostgreSQL + pg_vector - Vector search, $30-500+/month

---

## Cost Optimization Strategies

### Strategy 1: Choose SQLite When Appropriate

Cost savings of 90-99% for suitable workloads. Criteria: <1000 concurrent connections/sec, <50GB data, single region acceptable.

### Strategy 2: Connection Pooling

PgBouncer can reduce database connections 10-50x, eliminating connection exhaustion issues. Supabase Supavisor (2025) supports 1M+ connections.

### Strategy 3: Read Replicas vs Scaled Primary

For read-heavy workloads (>80% reads): Read replicas cheaper and safer than upgrading single instance.

### Strategy 4: Scheduled Scaling

Time-based scaling for predictable traffic can save 40-60% with automated up/down scaling during peak/off-peak hours.

### Strategy 5: Database Query Optimization

Proper indexing often eliminates need to scale vertically. 400x performance improvement common with strategic indexes.

### Strategy 6: Archive Old Data

Partition tables and archive >90 day data to S3. Can reduce monthly database cost from $1000+ to $300 for growing tables.

### Strategy 7: Managed Service Selection

Managed services cost 10-100x less than self-hosted when including operational labor (DBA costs ~$17k/month).

### Strategy 8: Database Right-Sizing

- Don't assume linear scaling (indexed queries scale logarithmically)
- Don't buy for peak traffic 365 days/year (use auto-scaling)
- Optimize queries first (90% of slowness is bad queries, not hardware)
- Match redundancy to actual SLA requirement (not maximum possible)

### Strategy 9: Consolidation & Multi-Tenancy

Single database with row-level security can save 95%+ vs separate database per tenant ($30,000/month → $200-500/month).

### Strategy 10: Caching to Reduce Database Load

Cache-aside pattern can reduce database queries 99% (1000 qps → 10 qps), allowing 10x smaller instance.

---

## Licensing & Commercial Considerations

**PostgreSQL:** PostgreSQL License (BSD-like) - Free, no restrictions
**MySQL:** GPL v2 / Commercial - Free open source, dual licensed
**SQLite:** Public Domain - Free, commercial use allowed, no restrictions
**CockroachDB:** Business Source License - Free source, commercial restrictions
**MariaDB:** GPL v2 / Commercial - Free open source, MySQL-compatible

---

## Conclusion & 2025 Recommendations

### Default Recommendations by Scenario

1. **Building first MVP:** Turso (free) or Neon PostgreSQL
2. **Startup with moderate scale:** PostgreSQL (Neon/Supabase) or SQLite+Turso
3. **Enterprise application:** PostgreSQL (self-hosted or AWS RDS)
4. **E-commerce platform:** PostgreSQL
5. **High-traffic social network:** PostgreSQL + Citus or MySQL + sharding
6. **Global SaaS:** CockroachDB or PostgreSQL + logical replication
7. **Real-time analytics:** PostgreSQL + Citus
8. **AI/ML workload:** PostgreSQL with pg_vector
9. **Geographic applications:** PostgreSQL with PostGIS
10. **Cost-optimized small project:** Turso (SQLite)

### 2025 Trends

1. **SQLite explosion:** Turso/libSQL/LiteFS making SQLite production-viable
2. **PostgreSQL dominance:** Clear winner for features and flexibility
3. **Managed services:** Making self-hosting less attractive
4. **Pricing wars:** Neon, Turso dropping prices significantly
5. **Vector search:** pg_vector becoming standard for AI/ML
6. **Edge databases:** SQLite-based databases moving data to edge
7. **Global distribution:** CockroachDB and logical replication
8. **Cost consciousness:** Smaller companies choosing SQLite to eliminate DB costs

---

## References & Sources

### PostgreSQL
- [PostgreSQL 17 Release Notes](https://www.postgresql.org/docs/release/17.0/)
- [PostgreSQL Replication Documentation](https://www.postgresql.org/docs/current/runtime-config-replication.html)
- [Row-Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

### MySQL
- [MySQL 8.4 Release Notes](https://dev.mysql.com/doc/relnotes/mysql/8.4/en/)

### SQLite & Turso
- [libSQL Documentation](https://docs.turso.tech/libsql)
- [Turso Pricing](https://turso.tech/pricing)
- [Litestream Project](https://litestream.io/)

### CockroachDB
- [CockroachDB Pricing](https://www.cockroachlabs.com/pricing/)

### Managed Services Pricing
- [Neon Pricing](https://neon.com/pricing)
- [Supabase Pricing](https://supabase.com/pricing)
- [AWS RDS Pricing](https://aws.amazon.com/rds/pricing/)

### PostgreSQL Extensions
- [pg_vector GitHub](https://github.com/pgvector/pgvector)
- [PostGIS Official](https://postgis.net/)
- [Citus Distributed PostgreSQL](https://www.citusdata.com/)

### Analysis & Comparisons
- [SQLite vs PostgreSQL Comparison](https://www.datacamp.com/blog/sqlite-vs-postgresql-detailed-comparison)
- [ACID Compliance Comparison](https://www.dronahq.com/acid-compliance/)

---

**Document Version:** 1.0
**Last Updated:** February 2026
**Next Review:** Q2 2026

*This reference document provides comprehensive information for database selection decisions as part of the Claude Code Tech-Stack Advisor skill.*

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->

---
## Related References
- [Multi-Tenancy Patterns](./56-multi-tenancy-patterns.md) — RLS, schema isolation, tenant data strategies
- [Serverless Databases](./09-databases-serverless.md) — Neon, Supabase, PlanetScale managed PostgreSQL
- [ORMs & Query Builders](./25-orm-query-builders.md) — Prisma, Drizzle, TypeORM comparison
- [Performance Benchmarks](./47-performance-benchmarks.md) — Database throughput and latency data
- [Observability & Tracing](./55-observability-tracing.md) — Database query monitoring and alerting
