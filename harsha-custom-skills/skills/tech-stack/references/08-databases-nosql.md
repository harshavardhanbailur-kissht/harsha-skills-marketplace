# NoSQL Databases — Architecture & Selection Guide (2025/2026)

> **Last Updated:** February 2026
> **Scope:** Technical decision-making for production workloads
> **Audience:** Full-stack architects, engineering leads, SREs

---

## Executive Summary

As of February 2026, the NoSQL landscape has undergone significant consolidation and licensing shifts. **Redis transitioned to source-available licensing**, spawning the Linux Foundation-backed **Valkey** fork. **MongoDB remains dominant** but PostgreSQL JSONB competes heavily for semi-structured data. **DynamoDB** offers serverless simplicity with hidden cost pitfalls. **Cassandra 5.0** matured with SAI and vector search, while **ScyllaDB** emerged as the ultra-high-performance alternative. **Dragonfly** challenges Redis with multi-threaded architecture.

This guide provides decision logic, version details, pricing models, and comparative analysis for each technology.

---

## 1. Redis, Valkey, & Alternatives

### 1.1 The Licensing Situation (2024-2026)

**Redis's Tri-License Model (Current)**
- **RSALv2** (Redis Source Available License v2): Source-available but not OSI-approved. Prohibits offering Redis as managed service.
- **SSPLv1** (Server Side Public License): Similar restrictions; adoption sparse outside MongoDB.
- **AGPLv3**: OSI-approved copyleft. Requires disclosure of modifications if offered as network service. Enterprise legal teams often reject due to copyleft requirements.

**Timeline:**
- March 2024: Redis changed from pure BSD to tri-license model
- March 2024: **Valkey fork** launched, backed by Linux Foundation
- May 2025: Redis added AGPLv3 as additional option for Redis 8
- December 2025: Redis 8 GA (see 1.2 below)

**Impact:** ~75% of surveyed Redis users considered migration due to licensing. AWS and Google Cloud backed Valkey with dedicated engineering resources.

### 1.2 Redis (Commercial/Licensed)

| Aspect | Details |
|--------|---------|
| **Current Version** | 8.6 (GA) with Redis 8.0/7.4/7.2/6.2 support in Enterprise |
| **Type** | In-memory key-value store, advanced data structures |
| **Licensing** | RSALv2, SSPLv1, or AGPLv3 (choose one) |
| **Data Model** | Strings, Lists, Sets, Sorted Sets, Hashes, Streams, JSON, HyperLogLog, Bitmap, Geo, Vector Set (beta) |
| **Query Language** | Redis CLI / protocol; Redis Query Engine for aggregations |
| **Transactions** | MULTI/EXEC (optimistic locking with WATCH) |
| **Replication** | Master-slave asynchronous |
| **Scaling** | Redis Cluster (horizontal), Sentinel (HA) |
| **Performance** | ~100K-200K ops/sec per node; 87% faster commands in v8 |
| **Managed Services** | AWS ElastiCache (Flex/Serverless), Google Cloud Memorystore, Azure Cache |

**Redis 8 Features (December 2025):**
- 30+ performance improvements (up to 87% faster commands)
- 2x throughput improvement per node
- 16x more query processing power (Redis Query Engine)
- 8 new data structures (JSON, time series, 5 probabilistic types)
- Improved replication (18% faster)

**Cost Model (ElastiCache):**
- On-demand: $0.017/GB-hour (cache tier) + network costs
- Provisioned: Reduced Reserved Instance pricing (30-55% discount)

### 1.3 Valkey (Open Source, Linux Foundation)

| Aspect | Details |
|--------|---------|
| **Current Version** | 8.1.1+ (active development) |
| **Type** | In-memory key-value store (Redis OSS 7.2 fork) |
| **Licensing** | **BSD 3-Clause (permanent, per Linux Foundation charter)** |
| **Data Model** | Compatible with Redis OSS 7.2 (no JSON, limited newer features) |
| **Query Language** | Redis CLI / protocol |
| **Transactions** | MULTI/EXEC with WATCH |
| **Scaling** | Redis Cluster protocol (compatible) |
| **Performance** | **37% higher SET throughput, 16% higher GET vs Redis 8.0** on Graviton |
| **Managed Services** | AWS ElastiCache (Valkey tier), MemoryDB (Beta), Google Cloud Memorystore |

**Why Choose Valkey?**
- ✅ Guaranteed open-source forever (Linux Foundation stewardship)
- ✅ 20-33% cheaper on AWS ElastiCache vs Redis OSS pricing
- ✅ Better performance on modern CPUs (Graviton, ARM)
- ✅ Backed by AWS, Google Cloud, Oracle, Ericsson
- ❌ No JSON, streams, or advanced data structures yet
- ❌ Smaller ecosystem; fewer modules available

**Migration Path:** Drop-in replacement for Redis OSS 7.2; existing clients need no code changes.

### 1.4 Dragonfly DB

| Aspect | Details |
|--------|---------|
| **Current Version** | 1.2+ |
| **Type** | Modern in-memory data store (Redis compatible) |
| **Licensing** | Source Available (Business Source License) |
| **Architecture** | **Multi-threaded, fiber-based concurrency** (vs Redis single-threaded) |
| **Data Model** | Redis-compatible; uses shared hash table |
| **Scaling** | Vertical scaling within single instance (terabyte-sized in-memory) |
| **Performance** | **25x throughput vs Redis single-process (3.8M QPS), 10-15M QPS in pipeline mode** |
| **Managed Services** | Self-hosted, limited cloud offerings (early stage) |

**Dragonfly vs Redis Benchmark (c6gn.16xlarge):**
| Metric | Redis | Dragonfly |
|--------|-------|-----------|
| Read-heavy ops/sec | 600K | 10M+ |
| Write-heavy ops/sec | 400K | 3.8M |
| Tail latency | ~10ms | <1ms |
| CPU cores utilized | 1 | 16 |
| Memory efficiency | Baseline | Similar |

**When to Choose Dragonfly:**
- ✅ Need ultra-high throughput on single node (reduce cluster complexity)
- ✅ Have spare multi-core capacity
- ✅ Accept 2-3 year old technology (less battle-tested)
- ❌ Need Redis modules (Dragonfly doesn't support)
- ❌ Strict open-source requirements (Business Source License)

### 1.5 Upstash (Serverless Redis/Valkey)

| Aspect | Details |
|--------|---------|
| **Model** | Serverless, per-request billing |
| **Pricing Tiers** | Free (500K cmds/mo), Fixed (250MB-500GB), Pay-as-you-go |
| **Free Tier** | 500K commands/month, 100GB storage limit |
| **Fixed Plans** | $8-500/month (predictable, includes 10K-16K req/s) |
| **Bandwidth** | First 200GB/month free; $0.03/GB after |
| **Price Cap** | $120/month guaranteed max (standard tier) |
| **Performance Max** | 16K req/s (Fixed 100GB+), 10K req/s (lower tiers) |
| **Enterprise Add-on** | Prod Pack ($200/mo per DB) |
| **Best For** | Prototypes, variable workloads, edge functions, serverless apps |

**Cost Comparison (Example: 10M commands/month):**
- Upstash Fixed 5GB: ~$35/month
- AWS ElastiCache On-demand: ~$120-150/month (at scale)
- Self-hosted Redis: $5-10/month (no management/HA)

---

## 2. MongoDB

### 2.1 Overview & Licensing

| Aspect | Details |
|--------|---------|
| **Current Version** | 8.2 (latest), 8.0 GA (October 2025) |
| **Type** | Document database (NoSQL) |
| **Licensing** | **SSPL (Server Side Public License)** for server; OSL for tools |
| **Data Model** | JSON documents, schema-flexible |
| **Query Language** | MongoDB Query Language (MQL); Aggregation Pipeline |
| **Transactions** | ✅ Multi-document ACID across replica sets and sharded clusters |
| **Replication** | Master-slave (replica sets); automatic failover |
| **Scaling** | Horizontal via sharding; vertical via replica set upgrades |
| **Performance** | 36% faster reads, 59% faster updates (v8.0 vs v7.2) |

### 2.2 MongoDB 8.0 Features (October 2025)

**Performance Improvements:**
- 36% quicker reads
- 59% higher throughput for updates
- 200% faster time-series aggregations
- 50x faster resharding (data distribution)
- 20% faster concurrent writes during replication

**New Capabilities:**
- `$lookup` aggregation stage now works within transactions on sharded collections
- `bulkWrite` command (insert, update, delete across multiple collections in one request)
- Unshard collections and move unsharded collections between shards
- Fixed memory leak in TransactionCoordinator (long-running transaction stability)

### 2.3 MongoDB Atlas Pricing (2025/2026)

| Tier | Storage | Features | Price | Use Case |
|------|---------|----------|-------|----------|
| **M0 (Free)** | 512 MB → 5 GB | Shared compute, 100 ops/sec | $0 forever | Learning, prototypes |
| **Shared/Flex** | 5 GB → unlimited | Auto-scaling, usage-based | $8-15/month | Dev, variable workloads |
| **Dedicated M10** | 10 GB+ | Dedicated cluster, backups, monitoring | $57/month | Production baseline |
| **Dedicated M30+** | 100 GB+ | Enhanced monitoring, enterprise features | $170+ /month | Enterprise production |

**2025 Updates:**
- Atlas Charts now included free on all dedicated clusters
- M0 free tier includes new Free Charts (auto-refresh every 4 hours, 1 scheduled report/week)
- Flex tier enables efficient auto-scaling for variable workloads
- Free tier never expires; commercial use allowed

### 2.4 MongoDB vs PostgreSQL JSONB (Decision Matrix)

| Factor | MongoDB | PostgreSQL JSONB |
|--------|---------|------------------|
| **Schema Flexibility** | Excellent (schema-less) | Good (flexible, but structured) |
| **Query Complexity** | Great for nested documents | Excellent for relational + JSON |
| **Transactions** | Multi-doc ACID (replica set+) | Full ACID with rollback |
| **Joins** | Difficult (use `$lookup`) | Native, optimized |
| **Indexing** | Field-level indexes | Full JSONB indexing + GIN/GIST |
| **JSONB Performance** | N/A | Faster than MongoDB for JSON (benchmarks: 2x speedup) |
| **Consistency** | Eventual (unless replica set) | Strong by default |
| **Cost (Atlas)** | $57+/month (M10) | PaaS varies; self-hosted $0 |
| **Operational** | Managed by MongoDB | Self-managed or RDS |

**When to Choose MongoDB:**
- ✅ Rapid schema iteration (startup MVP)
- ✅ Complex nested documents (social graphs, user profiles)
- ✅ Horizontal scaling needed (multi-region)
- ✅ Write-heavy workloads (MongoDB optimized for writes)

**When to Choose PostgreSQL JSONB:**
- ✅ Strong consistency required
- ✅ Complex relational queries (multiple foreign keys)
- ✅ Cost-sensitive (cheaper self-hosted or RDS)
- ✅ Need transactions across relational + JSON data
- ✅ Reporting/analytics on structured fields

**Real-world Trend (2025):** 55.6% of developers use PostgreSQL (vs 24% MongoDB), with 73% job growth. Many teams now use both: Postgres for system-of-record, MongoDB for flexible analytics/logs.

---

## 3. DynamoDB

### 3.1 Overview

| Aspect | Details |
|--------|---------|
| **Type** | Fully managed key-value, serverless NoSQL |
| **Licensing** | Proprietary (AWS) |
| **Data Model** | Tables with partition key + sort key; JSON attributes |
| **Query Language** | Query, GetItem, Scan, BatchGetItem |
| **Transactions** | TransactWriteItems (up to 25 writes); eventual consistency |
| **Scaling** | Auto-scaling with On-Demand or Provisioned capacity |
| **Replication** | Multi-AZ by default; Global Tables for multi-region |
| **Performance** | Sub-10ms latency; auto-scales to millions of req/s |
| **Availability** | 99.99% SLA (Multi-AZ) |

### 3.2 Pricing Models (2025)

**On-Demand Mode:**
- Pay per request; ideal for unpredictable traffic
- Baseline rate (e.g., $1.25 per million read requests)
- November 2024 price reduction made on-demand 20-30% cheaper
- No capacity provisioning needed; automatic scaling

**Provisioned Capacity Mode:**
- Reserve RCU (read capacity units) and WCU (write capacity units)
- Cost: $0.00013 per RCU-hour, $0.00065 per WCU-hour
- Reserved Instances: 25-55% discount for 1-3 year commitments
- More economical if utilization > 70%

**Cost Comparison (Break-even):**
- If your table utilizes <30% of provisioned capacity → move to on-demand
- If utilization 75%+ → provisioned is 33% cheaper
- If utilization 20% → you pay 5x more per request than base rate

### 3.3 Hidden Costs & Pitfalls

**Global Tables (Multi-region):**
- Every write is replicated to additional regions
- You pay for replication writes (1 KB chunks, rounded up)
- Example: Write 3.5 KB item to 4 regions = charge for 4 × 4 KB = 16 KB
- **Cannot reserve replicated writes** (on-demand only)
- Concurrent writes to same item in different regions = pay for all attempts (last-write-wins conflict resolution)

**Item Size & Rounding:**
- Reads charged in **4 KB increments** (round up)
- Writes charged in **1 KB increments** (round up)
- Small size increases cause disproportionate cost spikes
- Example: Item grows from 990 bytes to 1001 bytes = 1 KB → 2 KB write charge (100% increase)

**Secondary Indexes:**
- Each index is a copy of table data (additional storage cost)
- Every base table write updates all indexes (WCU overhead)
- GSI projections determine index size
- Infrequent Access table class helps but not retroactive

**DynamoDB Streams & Point-in-Time Recovery:**
- Streams incur per-GB costs for data retention
- PITR enabled = additional storage charges
- Backups outside 35-day retention window = per-GB cost

**Scans vs Queries:**
- Scans read every item in table, charge for all (even if filtered)
- Queries use sort key efficiently, but still charged per 4 KB read
- Full table scans on 1 GB table = ~250 RCU cost

### 3.4 Single-Table Design

**Concept:** Store multiple entity types in one table using clever partition/sort keys.

**Benefits:**
- Reduced table overhead (fewer provisioned capacities)
- Simpler capacity forecasting
- Transactions across entity types (easier with single table)
- Batch operations more efficient

**Example Schema:**
```
Partition Key: UserID
Sort Key: Type#Timestamp

Items:
  "user#123" | "profile#2025-02-19"    → User profile data
  "user#123" | "order#order-001"       → User's order
  "user#123" | "comment#comment-042"   → User's comment
```

**Query:** `GetItem(UserID=123, SK begins_with "order#")` = fetch all orders for user.

**Trade-offs:**
- ✅ Cheaper (fewer tables, less overhead)
- ✅ Easier transactions
- ❌ More complex query logic
- ❌ Harder to scale individual entity types

---

## 4. Cassandra & ScyllaDB

### 4.1 Apache Cassandra

| Aspect | Details |
|--------|---------|
| **Current Version** | 5.0.6 (latest, Oct 2025); 5.1 in development; 6.0 (Accord consensus) coming 2026 |
| **Type** | Wide-column store, distributed, peer-to-peer |
| **Licensing** | **Apache 2.0 (true open source)** |
| **Data Model** | Tables with partition key, clustering columns, wide rows |
| **Query Language** | CQL (Cassandra Query Language, SQL-like) |
| **Transactions** | **Limited:** Single partition only; no cross-partition ACID |
| **Replication** | Multi-datacenter peer-to-peer (no master); tunable consistency |
| **Scaling** | Linear horizontal scaling; add nodes for capacity |
| **Performance** | 10K-100K ops/sec per node (depends on config) |
| **Consistency** | Tunable (eventual to strong, per query) |

**Cassandra 5.0 Features (2024):**
- **Storage Attached Indexes (SAI):** Flexible secondary indexing without limitations
- **Vector Search:** Native vector data type + ANN for AI workloads
- **Dynamic Data Masking:** Sensitive data obfuscation (PII masking)
- **Local Secondary Indexes:** Performance improvement over SSTable scans

**Cassandra 6.0 (Expected 2026):**
- **Accord Consensus Protocol:** Replaces Paxos for stronger consistency guarantees
- Improved cross-partition transaction support
- Better multi-datacenter consistency

### 4.2 ScyllaDB

| Aspect | Details |
|--------|---------|
| **Current Version** | 2025.1 (source-available, April 2025); enterprise versions up to 2024.2 |
| **Type** | Wide-column store (Cassandra-compatible) |
| **Licensing** | Source-Available License (BUSL-1.1, similar to MongoDB) |
| **Architecture** | **C++ (vs Cassandra's Java); shard-per-core with fibers** |
| **Data Model** | CQL-compatible; Cassandra-compatible format |
| **Scaling** | Vertical (single node can be massive) + horizontal |
| **Performance** | **3-10x faster than Cassandra; sub-millisecond latencies** |
| **Compatibility** | ~95% CQL compatible; DynamoDB API via Project Alternator |

**ScyllaDB Advantages:**
- ✅ **No Java GC pauses** (C++ eliminates stop-the-world)
- ✅ **Shard-per-core architecture** (maximize multi-core throughput)
- ✅ **Production-ready Global Secondary Indexes** (Cassandra still experimental)
- ✅ **Materialized Views** (better query flexibility)
- ✅ **Workload Prioritization** (operational + analytics on same cluster)
- ✅ **Tablets** (improved data distribution vs legacy vnodes)
- ✅ DynamoDB API compatibility (Project Alternator)
- ❌ Source-available license (commercial concerns for some orgs)
- ❌ Smaller ecosystem (fewer drivers, less tooling)

**Benchmark: 4 ScyllaDB nodes vs 40 Cassandra nodes** (same throughput)
- ScyllaDB achieves parity with 1/10th the nodes
- Cost savings: 10x reduction in infrastructure

---

## 5. Decision Logic (IF/THEN Rules)

### 5.1 IN-MEMORY KEY-VALUE (Cache/Session Store)

```
IF workload is cache/session with predictable traffic
  AND open source is required
  THEN use Valkey (AWS ElastiCache Valkey tier)
ELSE IF budget is ultra-tight
  AND throughput needs are moderate
  THEN use Upstash (serverless, pay-per-request)
ELSE IF need absolute max performance per node
  AND accept source-available license
  THEN use Dragonfly
ELSE IF have existing Redis investment
  AND willing to accept tri-license terms
  THEN stay with Redis (commercial support available)
ELSE
  DEFAULT: Valkey (safe, open, performant, backed by AWS/GCP)
```

### 5.2 DOCUMENT STORE (Flexible Schema)

```
IF need horizontal scaling across regions
  AND complex nested documents
  AND write-heavy workloads
  THEN use MongoDB Atlas

ELSE IF prioritize cost
  AND willing to use PostgreSQL
  AND data is semi-structured (not deeply nested)
  THEN use PostgreSQL JSONB

ELSE IF completely serverless required
  AND variability is extreme
  AND cost > $1K/month unacceptable
  THEN use MongoDB Atlas Flex or Firebase (Google)

ELSE
  DEFAULT: MongoDB (mature, widely adopted, good performance)
```

### 5.3 KEY-VALUE WITH QUERIES (DynamoDB alternative)

```
IF running on AWS
  AND need serverless completely
  AND can redesign for single-table patterns
  THEN use DynamoDB (be aware of hidden costs)

ELSE IF need flexible queries
  AND running multi-region
  AND cost is primary concern
  THEN use ScyllaDB (lower infra cost than Cassandra)

ELSE IF Cassandra experience in-house
  AND need tunable consistency
  AND willing to manage replication complexity
  THEN use Apache Cassandra 5.0+

ELSE
  DEFAULT: DynamoDB (if AWS-locked); ScyllaDB (if multi-cloud)
```

### 5.4 TIME-SERIES / HIGH-THROUGHPUT WRITES

```
IF Cassandra or ScyllaDB available
  AND time-series or log data
  AND 10K+ writes/sec
  AND eventual consistency acceptable
  THEN use ScyllaDB (3-10x better than Cassandra)

ELSE IF PostgreSQL TimescaleDB licensed
  AND need strong consistency
  AND <1K writes/sec acceptable
  THEN use TimescaleDB (better for analytics)

ELSE
  DEFAULT: ScyllaDB (unmatched throughput for distributed TSM)
```

### 5.5 VECTOR SEARCH (AI/ML Embeddings)

```
IF using MongoDB
  AND AI search needed (similar embeddings)
  THEN use MongoDB Vector Search (Atlas-native)

ELSE IF using Cassandra
  AND AI search needed
  THEN use Cassandra 5.0+ Vector Search

ELSE IF using ScyllaDB
  AND AI search needed
  THEN use ScyllaDB Vector Search (5.0+)

ELSE IF want dedicated vector DB
  AND budget > $50/month
  THEN use Pinecone or Weaviate

ELSE
  DEFAULT: PostgreSQL pgvector (if using Postgres already)
```

---

## 6. Managed Services Comparison

| Service | Provider | Best For | Pricing | Availability |
|---------|----------|----------|---------|--------------|
| **MongoDB Atlas** | MongoDB Inc. | Flexible schemas, global scale | M0 free, M10 $57/mo | 99.95% (dedicated) |
| **AWS DynamoDB** | Amazon | Serverless, AWS-locked | On-demand $1.25/M reads | 99.99% (Multi-AZ) |
| **AWS ElastiCache (Valkey/Redis)** | Amazon | High-speed caching | Flexible/on-demand | 99.99% (Multi-AZ) |
| **AWS MemoryDB** | Amazon | Durable in-memory DB | Provisioned only | 99.99% (Multi-AZ) |
| **Google Cloud Firestore** | Google | Real-time, mobile apps | Free tier, pay-per-operation | 99.95% |
| **Google Cloud Memorystore** | Google | Managed Redis/Memcached | $5-30/GB-month | 99.9% |
| **Upstash** | Third-party | Serverless Redis, edge | Free/fixed/PAYG | 99.99% |
| **Supabase** | Third-party | PostgreSQL + JSONB + extensions | Free tier, $25+ production | 99.9% |

---

## 7. Specific Version Matrix (February 2026)

| Database | Latest Version | LTS/Support | Key Features | EOL Expected |
|----------|---|---|---|---|
| **Redis** | 8.6 | 7.4 (LTS), 8.0 | AGPLv3 option, Query Engine 16x, 87% faster cmds | 2027 |
| **Valkey** | 8.1.1 | Rolling (Linux Foundation) | BSD 3-clause, 37% faster SET, no JSON yet | N/A (forever) |
| **Dragonfly** | 1.2+ | Rolling | Multi-threaded, 25x throughput vs Redis | Rolling updates |
| **MongoDB** | 8.2 | 8.0 (LTS until Oct 2027) | $lookup in transactions, bulkWrite, 59% faster writes | Oct 2026 (7.0) |
| **Cassandra** | 5.0.6 | 4.1 (LTS until Feb 2026) | SAI, Vector Search, Dynamic Data Masking | Oct 2025 (3.11 EOL) |
| **ScyllaDB** | 2025.1 | Enterprise 2024.2 | C++, sub-ms latency, DynamoDB API, Tablets | Rolling updates |
| **DynamoDB** | N/A (managed) | N/A | Global Tables, PITR, Flex scaling | Indefinite |

---

## 8. Licensing Summary Table

| Product | License Type | Open Source | Commercial Support | Migration Risk |
|---------|---|---|---|---|
| **Valkey** | BSD 3-Clause | ✅ Yes | Linux Foundation | Low (drop-in Redis replacement) |
| **Redis 8** | AGPLv3 / RSALV2 / SSPLV1 | ❌ Source-available | Redis Inc. | Medium (license compliance risk) |
| **Dragonfly** | BUSL-1.1 | ❌ Source-available | Dragonfly Inc. | Medium (emerging project) |
| **MongoDB** | SSPL | ❌ Source-available | MongoDB Inc. | Medium (SSPL restrictions) |
| **Cassandra** | Apache 2.0 | ✅ Yes | DataStax, Others | Low (true open source) |
| **ScyllaDB** | BUSL-1.1 | ❌ Source-available | ScyllaDB Inc. | Medium (BUSL-1.1 copyleft) |
| **DynamoDB** | Proprietary | ❌ No | Amazon | High (AWS vendor lock-in) |

---

## 9. Cost Estimation Model

### 9.1 Monthly Cost Scenarios

**Scenario 1: 10M reads/month, 1M writes/month, 5 GB data (Caching)**

| Technology | Infrastructure | Cost | Notes |
|---|---|---|---|
| Upstash (Fixed 5GB) | Serverless | $35 | Best value for variable |
| Valkey (ElastiCache) | 1x cache.r7g.large | $65 | On-demand pricing |
| Redis (ElastiCache) | 1x cache.r7g.large | $75 | 15% premium |
| Dragonfly (self-hosted) | 1x c6i.2xlarge | $120 | Only compute, not managed |

**Scenario 2: Document Store, 100 GB, highly variable traffic**

| Technology | Infrastructure | Cost | Notes |
|---|---|---|---|
| MongoDB Atlas M10 | 1x shared | $57 | Baseline production |
| MongoDB Atlas Flex | Auto-scaling | $8-50 | Variable based on usage |
| PostgreSQL RDS | db.t3.micro | $20-30 | Self-managed cheaper |
| Firebase Firestore | On-demand | $0-200 | Depends on ops |

**Scenario 3: High-throughput events, 1M writes/sec**

| Technology | Infrastructure | Cost | Notes |
|---|---|---|---|
| ScyllaDB (4 nodes) | i3.2xlarge × 4 | $800 | 1/10th Cassandra cost |
| Cassandra (40 nodes) | i3.2xlarge × 40 | $8000 | Equivalent throughput |
| DynamoDB (provisioned) | 500K WCU | $32,500 | Extremely expensive at scale |
| DynamoDB (on-demand) | N/A | $5,000+ | More reasonable than provisioned |

---

## 10. Recommended Decision Trees

### 10.1 "What should I pick for a new project in 2026?"

```
START
  ↓
[ Do you have >$100K/year data budget? ]
  │
  YES → [ Is it a startup/MVP? ]
  │     YES → MongoDB Atlas Free/Flex (fast iteration)
  │     NO  → [ Need strong consistency? ]
  │           YES → PostgreSQL + JSONB
  │           NO  → MongoDB Atlas (M10+)
  │
  NO  → [ Do you need real-time global scale? ]
        YES → [ Amazon customer? ]
              YES → DynamoDB (accept lock-in)
              NO  → MongoDB Atlas Flex
        NO  → [ Open source acceptable? ]
              YES → Cassandra or ScyllaDB
              NO  → PostgreSQL RDS / Supabase
```

### 10.2 "Redis vs Valkey vs Dragonfly for Caching?"

```
START
  ↓
[ Need GPL/true open source? ]
  │
  YES → Valkey (BSD, backed by Linux Foundation)
  │
  NO  → [ Extreme throughput (>1M ops/sec single node)? ]
        │
        YES → Dragonfly (but accept source-available license)
        │
        NO  → [ AWS ecosystem preferred? ]
              YES → Valkey on ElastiCache (20% cheaper than Redis)
              NO  → Valkey (default safe choice everywhere)
```

### 10.3 "DynamoDB Cost Killer: How to Avoid It?"

```
RISKS:
  1. Global Tables: 4x write costs for 4 regions
     → MITIGATION: Use on-demand, not provisioned

  2. Item size creep: 990 bytes → 1001 bytes = 2x write charge
     → MITIGATION: Audit schema; keep items <1 KB

  3. Indexes: Every index = copy of data + index writes
     → MITIGATION: Use sparse indexes; delete unused

  4. Scans vs Queries: Scan charges for all items read
     → MITIGATION: Always use Query with sort key filters

  5. Over-provisioned capacity: Unused RCU/WCU waste
     → MITIGATION: Use on-demand or auto-scaling + Reserved Instances

RECOMMENDATION: Use On-Demand mode; reserved instances only for 75%+ utilization tables.
```

---

## 11. Technology Maturity & Risk Assessment

| Technology | Maturity | Adoption | Operator Difficulty | Recommended For |
|---|---|---|---|---|
| **PostgreSQL + JSONB** | ⭐⭐⭐⭐⭐ (Mature) | 55.6% | Low | Default RDBMS choice |
| **MongoDB** | ⭐⭐⭐⭐⭐ (Mature) | 24% (NoSQL) | Low-Medium | Document workloads |
| **Redis / Valkey** | ⭐⭐⭐⭐⭐ (Mature) | 80%+ (caching) | Low | Caching, sessions, queues |
| **DynamoDB** | ⭐⭐⭐⭐⭐ (Mature) | AWS-only | Medium | AWS-native serverless |
| **Cassandra** | ⭐⭐⭐⭐ (Production) | High-scale clusters | High | Time-series, 10K+ writes/sec |
| **ScyllaDB** | ⭐⭐⭐⭐ (Maturing) | Growing | Medium | Cassandra replacement |
| **Dragonfly** | ⭐⭐⭐ (Emerging) | <5% | Medium | Advanced caching only |

---

## 12. Sources & References

- [Redis vs Valkey: Deep Dive for Enterprise Architects](https://andrewbaker.ninja/2026/01/04/redis-vs-valkey-a-deep-dive-for-enterprise-architects/)
- [Valkey vs Redis: How to Choose in 2026](https://betterstack.com/community/comparisons/redis-vs-valkey/)
- [MongoDB Licensing and Tri-License Model - Percona](https://www.percona.com/blog/the-redis-license-has-changed-what-you-need-to-know/)
- [MongoDB Atlas Pricing 2025](https://www.mongodb.com/pricing)
- [MongoDB Pricing Breakdown: A 2025 Cost Guide](https://cloudchipr.io/blog/mongodb-pricing)
- [MongoDB 8.0: Raising the Bar](https://www.mongodb.com/blog/post/mongodb-8-0-raising-the-bar)
- [MongoDB vs PostgreSQL in 2026](https://www.nucamp.co/blog/mongodb-vs-postgresql-in-2026-nosql-vs-sql-for-full-stack-apps)
- [DynamoDB Complete Guide 2025](https://www.knowi.com/blog/amazon-dynamodb-complete-guide-2025-architecture-pricing-use-cases-alternatives/)
- [Understanding DynamoDB Cost Spikes - ScyllaDB](https://www.scylladb.com/2025/08/05/blowing-up-your-dynamodb-bill/)
- [DynamoDB Pricing Demystified](https://www.nops.io/blog/amazon-dynamodb-pricing/)
- [AWS DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
- [Dragonfly vs Redis: Scalability and Performance](https://www.dragonflydb.io/blog/scaling-performance-redis-vs-dragonfly/)
- [DragonflyDB vs Redis: Deep Dive](https://medium.com/@mohitdehuliya/dragonflydb-vs-redis-a-deep-dive-towards-the-next-gen-caching-infrastructure-23186397b3d3/)
- [Upstash: Serverless Data Platform](https://upstash.com/pricing/redis)
- [Cassandra 5.0 Features](https://cassandra.apache.org/_/blog/Apache-Cassandra-5.0-Announcement.html)
- [Apache Cassandra 2025: Performance & Community](https://axonops.com/blog/cassandra-in-2025-a-year-in-review)
- [ScyllaDB vs Cassandra Comparison](https://www.scylladb.com/compare/scylladb-vs-apache-cassandra/)
- [ScyllaDB 2025.1 Release](https://www.scylladb.com/2025/04/08/announcing-scylladb-2025-1/)
- [AWS ElastiCache vs MemoryDB](https://oneuptime.com/blog/post/2026-02-12-compare-memorydb-vs-elasticache/view)
- [Postgres vs MongoDB: Complete Comparison 2025](https://www.bytebase.com/blog/postgres-vs-mongodb/)
- [Redis 8 GA: Features and Performance](https://redis.io/blog/redis-8-ga/)
- [JSONB Performance: PostgreSQL vs MongoDB](https://medium.com/@ArkProtocol1/jsonb-is-faster-than-you-think-we-benchmarked-postgres-vs-mongo-afad716d5074/)

---

## 13. Quick Reference: When NOT to Use

| Technology | ❌ NOT Suitable For | Better Alternative |
|---|---|---|
| **DynamoDB** | Complex multi-table joins, strong consistency required, cost-sensitive | PostgreSQL, Cassandra |
| **MongoDB** | Relational data with many joins, financial ledgers | PostgreSQL |
| **Redis** | Persistent data only (no backup), data volume > 256 GB | PostgreSQL, DynamoDB |
| **Cassandra** | Simple key-value, ACID transactions required, small data | DynamoDB, Redis |
| **Dragonfly** | Redis module dependencies (search, JSON), production stability critical | Redis, Valkey |
| **ScyllaDB** | Small clusters (<3 nodes), simple caching | Redis, Memcached |

---

**Document Version:** 1.0 (February 2026)
**Confidence Level:** High (sourced from Feb 2025 - Feb 2026 data)
**Next Review:** Q4 2026 (Redis 9, MongoDB 8.3, Cassandra 6.0 GA expected)

## Related References
- [Relational Databases Guide](./07-databases-relational.md) — SQL alternatives for structured data
- [Serverless Databases](./09-databases-serverless.md) — Managed, edge-optimized database services
- [ORM & Query Builders](./25-orm-query-builders.md) — Abstraction layers for database queries
- [Search Solutions](./20-search-solutions.md) — Full-text and vector search integration
- [Performance Benchmarks](./47-performance-benchmarks.md) — Real-world database performance metrics

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->
