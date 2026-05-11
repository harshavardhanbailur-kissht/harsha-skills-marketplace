# Server-Side Search Engines Encyclopedia: Complete Architecture & Comparison Guide

**Version:** 1.0
**Last Updated:** March 2026
**Purpose:** Comprehensive reference for selecting, deploying, and optimizing server-side search infrastructure

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Elasticsearch / OpenSearch](#elasticsearch--opensearch)
3. [Modern Fast Engines: Meilisearch & Typesense](#modern-fast-engines-meilisearch--typesense)
4. [SaaS Search Solutions](#saas-search-solutions)
5. [Database Full-Text Search](#database-full-text-search)
6. [Lightweight & Specialized Alternatives](#lightweight--specialized-alternatives)
7. [Vector Search Engines](#vector-search-engines)
8. [Decision Framework](#decision-framework)
9. [Cost Analysis & Benchmarks](#cost-analysis--benchmarks)
10. [Migration Considerations](#migration-considerations)

---

## Executive Summary

The search engine landscape has fragmented dramatically since Elasticsearch's rise. Today's developers have vastly different options depending on use case, budget, and operational complexity tolerance. This guide helps navigate the decision space through architecture deep-dives, performance benchmarks, and cost analysis.

### Key Insight

**Do not use a distributed search engine for problems that a database can solve.**

For most teams building new applications:
- **<50GB data, simple search:** PostgreSQL FTS or SQLite FTS5
- **<1GB data, fast UX required:** Meilisearch or Typesense (self-hosted)
- **Production SaaS, complex relevance:** Algolia (premium pricing justified)
- **Enterprise, control required:** Elasticsearch or OpenSearch
- **Vector-first AI apps:** Qdrant or Weaviate

---

## Elasticsearch / OpenSearch

### Architecture Overview

Elasticsearch is built on **Apache Lucene**, a mature Java library that implements inverted indexing and relevance ranking. Modern Elasticsearch should be understood as a distributed system that coordinates many Lucene instances.

**Core concepts:**

- **Index:** Logical container for documents (analogous to a database table)
- **Shard:** A single Lucene instance; index can split across multiple shards for scale
- **Replica:** Copy of a shard for redundancy and read scaling
- **Node:** An Elasticsearch process (usually one per server)
- **Cluster:** Collection of nodes coordinating together

### Inverted Index Architecture

The inverted index maps terms → list of documents containing that term, plus metadata:

```
Term          | Document IDs | Positions
"elasticsearch" | [1, 3, 7]    | {1: [0], 3: [5, 12], 7: [2]}
"performance"   | [1, 2, 4]    | {1: [3], 2: [0], 4: [11]}
```

This structure enables sub-millisecond lookups for keyword queries on massive datasets.

### Scoring: BM25 Algorithm

Since Elasticsearch 5.0, **BM25** is the default similarity function (replacing TF-IDF). BM25 improves TF-IDF by:

1. **Term frequency saturation:** After a threshold, more occurrences add diminishing relevance
2. **Field length normalization:** Doesn't penalize long documents equally
3. **IDF smoothing:** Rare terms add more signal than common ones

Formula:
```
Score = Σ IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * |D| / avgdl))
```

Where:
- `f(qi, D)` = frequency of term qi in document D
- `k1` = term saturation threshold (default 1.2)
- `b` = field length normalization (default 0.75)
- `avgdl` = average document length

**Critical insight:** BM25 works best when queries use the same terminology as documents. It fails gracefully on synonyms or paraphrases—vector search complements it.

### Cluster Architecture at Scale

**Three node roles:**
- **Master nodes:** Coordinate cluster state changes (minimum 3 for production)
- **Data nodes:** Hold shards, execute queries
- **Ingest nodes:** Pre-process documents before indexing

**Shard sizing best practices:**

```
Target shard size: 20GB - 40GB (for time-series: even larger)
Number of shards = Data volume / Target shard size
Number of replicas = 1 for HA, 2 for high-availability SLA
```

**Why sharding matters:**

- Query parallelization: 3 shards on 3 nodes = ~3x query throughput
- But too many shards (>100 per node) = coordination overhead
- Each shard consumes 10-50MB heap memory regardless of data size

### Vector Search: kNN with HNSW (8.0+)

Elasticsearch added approximate nearest neighbor search using **HNSW** (Hierarchical Navigable Small World graphs).

**kNN vs traditional BM25:**

| Aspect | BM25 | kNN Vector |
|--------|------|-----------|
| Latency | 1-5ms | 20-100ms (index size dependent) |
| Recall on synonyms | 0% | 85%+ |
| Scalability | Billions | Billions (with efficiency trade-offs) |
| Relevance | Precision | Semantic understanding |

**Hybrid search approach (recommended):**

```json
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "title": {"query": "running shoes", "boost": 2}
          }
        },
        {
          "knn": {
            "embedding": {
              "vector": [0.2, 0.4, ...],
              "k": 50
            }
          }
        }
      ]
    }
  }
}
```

Use **Reciprocal Rank Fusion** to merge results fairly. This improved precision@5 by 17% over pure BM25 and 8% over pure vector search.

### OpenSearch vs Elasticsearch (2025 Update)

**Licensing:**
- Elasticsearch: Server Side Public License (SSPL) + Elastic License (not OSI-approved open source)
- OpenSearch: Apache 2.0 (true open source)

**Performance:**
- Elasticsearch: 40-140% faster on complex queries
- OpenSearch: Catching up with vector search improvements

**Vector search implementations:**
- OpenSearch: Multiple engines (HNSW, IVF, PQ) with quantization options
- Elasticsearch: HNSW with recent optimizations (BBQ, ACORN)

**When to choose OpenSearch:**
- Legal requirement for OSI-approved open source
- AWS-native infrastructure (native to AWS OpenSearch)
- Need for extensibility without commercial licensing

**When to choose Elasticsearch:**
- Require bleeding-edge ML/observability features
- Need enterprise support
- Cloud hosting preferred (Elastic Cloud)

### Production Deployment: JVM Tuning

Elasticsearch runs on Java and **JVM tuning is critical for cost and performance.**

**Heap sizing rule:**

```
Xmx = min(50% of available RAM, 31GB)
Xms = Xmx (set heap minimum = maximum)
```

**Why 31GB max?** Java uses pointer compression below 32GB, improving memory efficiency.

**Why 50% of RAM?** The other 50% serves as OS filesystem cache for hot index data. More heap doesn't help if data isn't cached.

**Real-world example:**
- 64GB server
- Heap: 31GB (reaches compression threshold)
- OS cache: 33GB (dramatically improves query latency)
- Better than 40GB heap + 24GB cache

**Garbage collection monitoring:**

Elasticsearch uses G1GC collector. Watch for:
- GC pause duration (keep <500ms in production)
- Full GC frequency (should be rare)
- Heap utilization (alert at 85%+)

### Operational Costs: The JVM Tax

Elasticsearch's JVM footprint makes operational costs high:

**Cost drivers:**
1. **Memory:** 31GB heap + overhead = 40-50GB per node
2. **Scaling complexity:** Sharding adds coordination overhead
3. **Replication:** 3x replication for HA triples storage cost
4. **Monitoring:** JVM pressure requires constant monitoring

**Cost optimization tactics:**
- Use larger shards (fewer total = less coordination)
- Appropriate replica count (1 for HA, not 3)
- Enable ILM (Index Lifecycle Management) for time-series data
- Use local SSD storage (more IOPS per $/GB)
- Right-size heap (don't guess)

### When to Use Elasticsearch

✅ **Good fit:**
- 100GB+ of searchable data
- Complex query requirements (bool queries, faceting, aggregations)
- Need for distributed search across multiple nodes
- Vector + keyword hybrid search required
- Enterprise features (security, audit logging, monitoring)

❌ **Not suitable:**
- <10GB of data (over-engineered)
- Simple LIKE queries on relational data
- Budget-constrained startups (operational complexity is expensive)
- Single-node use cases (PostgreSQL FTS is simpler)

---

## Modern Fast Engines: Meilisearch & Typesense

The emergence of Rust-based and C++-based search engines represents a major shift from the JVM-based paradigm.

### Meilisearch

**Technology:** Rust-based, in-memory with disk persistence

**Philosophy:** Zero-configuration defaults. Works great out-of-the-box.

#### Architecture

- **Inverted index** in RAM for instant search (<50ms target)
- **Memory-mapped files** for persistence without complex serialization
- **Single-node** by design (Meilisearch Cloud offers managed multi-node)
- **Typo tolerance** built-in via Levenshtein automata
- **Prefix search** enabled by default

#### Ranking System

Meilisearch uses **configurable ranking rules** rather than a pure algorithm:

```rust
Default ranking rules:
1. Sort by attribute (if specified in query)
2. Proximity of search words in document
3. Typo count (fewer typos = higher rank)
4. Word position (earlier in document = higher)
5. Exact match bonus
6. Attribute ranking (title > body > tags)
```

This is more transparent than BM25 but less sophisticated for complex relevance tuning.

#### Feature Set

- ✅ Typo tolerance (automatic)
- ✅ Faceted search and filtering
- ✅ Synonym support
- ✅ Custom search rules
- ✅ Multi-language support
- ✅ Instant search <50ms
- ❌ No distributed sharding
- ❌ Limited scaling (single node = single machine limit)

#### Deployment Options

**Self-hosted:**
```bash
# Docker
docker run -it --rm -p 7700:7700 getmeili/meilisearch

# Single binary
./meilisearch
```

**Meilisearch Cloud:**
- Starting: Free tier (10GB)
- Production: $25-250+/month depending on usage

#### Performance Characteristics

- **Indexing speed:** Fastest among modern engines (~300k docs/sec)
- **Query latency:** <50ms (50th percentile)
- **Memory usage:** Entire index in RAM
- **Dataset limit:** 80TB theoretical (Linux), practical limit ~100GB for single deployment

#### When to Use Meilisearch

✅ **Excellent for:**
- E-commerce product search (instant-search UX)
- Documentation/content search
- Startup minimum viable product (MVP)
- Developer-friendly search
- Rapid prototyping

❌ **Not ideal for:**
- Distributed search across regions
- High-volume indexing (>5M documents/day)
- Complex faceted analytics
- 24/7 production SLA (no HA without paid Cloud)

---

### Typesense

**Technology:** C++ in-memory engine, optimized for maximum throughput

**Philosophy:** High-performance simplicity with control over configuration.

#### Architecture

- **Entire index in RAM** (all data loaded into memory)
- **Raft consensus** for replication (not sharding)
- **In-place updates** (replicate full dataset to each node)
- **Single-pass search** implementation
- **Automatic typo tolerance** with configurable strictness

#### Ranking Mechanism

Typesense uses **field-weighted BM25 variant** with simpler defaults:

```
Ranking factors:
1. Text match score (field-weighted BM25)
2. Typo distance
3. Proximity
4. Sort criteria (custom_field asc/desc)
5. Dynamic fields (real-time computation)
```

More formula-driven than Meilisearch's rule-based approach.

#### Feature Set

- ✅ Extremely fast (<50ms, often <10ms)
- ✅ Automatic typo tolerance
- ✅ Geo-search (lat/lon based)
- ✅ Vector search support
- ✅ Synonyms and curation
- ✅ Advanced filtering
- ❌ No sharding (replication-only)
- ❌ All data must fit in RAM (tight memory constraint)

#### Deployment Options

**Self-hosted clustering:**
```yaml
# 3-node cluster with Raft consensus
nodes:
  - http://node1:8108
  - http://node2:8108
  - http://node3:8108
```

**Typesense Cloud:**
- Pay-per-usage model
- Starts $99/month for production tiers
- Includes replication and backups

#### Performance Characteristics

- **Query latency:** 5-50ms depending on index size
- **Indexing:** 100k-500k docs/sec
- **Memory:** Must fit entire index (limit ~500GB per cluster)
- **Availability:** Replication prevents single-node loss

#### When to Use Typesense

✅ **Excellent for:**
- High-traffic search (e-commerce, marketplaces)
- Performance-critical applications
- Geo-search requirements
- Need for higher control over relevance tuning

❌ **Not suitable:**
- Massive datasets (>500GB)
- Distributed search across regions
- Text-heavy content (academic papers, news)

---

### Meilisearch vs Typesense Comparison

| Factor | Meilisearch | Typesense |
|--------|------------|-----------|
| **Language** | Rust | C++ |
| **Setup complexity** | Minimal | Moderate |
| **Query latency** | <50ms | <10-50ms |
| **Indexing speed** | Fastest | Very fast |
| **Scaling approach** | Single-node | Replication (no sharding) |
| **Memory efficiency** | Good | Excellent |
| **Configuration** | Defaults-first | Flexible |
| **Geo-search** | Not native | Built-in |
| **Vector search** | Recent addition | Native |
| **Self-hosted cost** | Lowest | Low |
| **Managed service cost** | $25/month+ | $99/month+ |
| **Ideal use case** | Developer experience | Performance critical |

**Cost comparison at 100k documents:**
- Meilisearch self-hosted: $20/month (small VM)
- Typesense self-hosted: $20/month
- Algolia: $300-500/month
- Elasticsearch (managed): $100-300/month

---

## SaaS Search Solutions

### Algolia

**Model:** Fully managed search-as-a-service with global CDN

**Philosophy:** Trade operational burden for convenience and features.

#### Architecture

Algolia abstracts away infrastructure entirely:
- **Global distribution:** Records cached on CDN in 300+ data centers
- **Redundancy:** Automatic failover across regions
- **Indexing pipeline:** Built-in analytics and monitoring
- **Machine learning:** Neural search (re-ranking with AI)
- **Front-end widgets:** InstantSearch.js for rapid integration

#### Feature Parity with Others

- ✅ Sub-100ms latency globally (via CDN)
- ✅ Typo tolerance
- ✅ Faceted search
- ✅ Vector search (NeuralSearch)
- ✅ A/B testing
- ✅ Analytics dashboard
- ✅ Query-time rules (boost certain results)

#### Pricing Model (2025)

**Free "Build" tier:**
- 1 million records
- 10,000 searches/month
- No neural search

**Grow tier (usage-based):**
- $0.50 per 1,000 search requests
- $0.40 per 1,000 records stored
- Minimum ~$10/month for small projects

**Premium tier:**
- Custom pricing
- Higher limits
- Dedicated support

**Startup program:**
- $10,000 free search credits
- 20% discount on committed plans

#### Cost Analysis

A typical SaaS application with 1 million records and 1 million searches/month:

```
Records:      1M records × $0.0004 = $400/month
Searches:     1M searches × $0.0005 = $500/month
Total:        $900/month (without neural search)
```

Compare to:
- Self-hosted Elasticsearch: $300-500/month (infrastructure + ops)
- Self-hosted Meilisearch: $50/month (minimal)

**Algolia breakeven:** When operational burden of self-hosting > $400/month.

#### When to Use Algolia

✅ **Worth the premium:**
- Small teams (outsource search ops)
- Critical search UX (neural search valuable)
- Global distribution required
- A/B testing and analytics important
- Budget available ($300-1000+/month)

❌ **Not recommended:**
- Budget-sensitive startups
- Simple keyword search only
- High search volume (millions/month → cost explosion)
- Privacy-sensitive data (must be indexed in Algolia's system)

---

## Database Full-Text Search

For many teams, dedicated search engines are **unnecessary complexity**. Modern databases have excellent search capabilities.

### PostgreSQL Full-Text Search (FTS)

PostgreSQL includes native full-text search without additional tools.

#### Text Search Operators

```sql
-- Basic FTS query
SELECT * FROM documents
WHERE document_text @@ plainto_tsquery('running shoes');

-- Advanced tsvector with language support
SELECT id, title, ts_rank(document_tsvector, query) AS rank
FROM documents,
     plainto_tsquery('english', 'running shoes') query
WHERE document_tsvector @@ query
ORDER BY rank DESC;

-- Fuzzy matching with pg_trgm (trigrams)
SELECT * FROM documents
WHERE title % 'runing shoes'  -- typo-tolerant
ORDER BY similarity(title, 'running shoes') DESC;
```

#### GIN Index for Performance

```sql
-- Create GIN index (Generalized Inverted iNdex)
CREATE INDEX idx_documents_fts
  ON documents
  USING gin(document_tsvector);

-- For trigram fuzzy search
CREATE INDEX idx_title_trgm
  ON documents
  USING gin(title gin_trgm_ops);
```

**Performance characteristics:**

| Operation | Time | Notes |
|-----------|------|-------|
| Index creation | ~5 mins | (10M rows, one-time) |
| Exact phrase search | <100ms | (1M rows, GIN index) |
| Fuzzy search (pg_trgm) | <500ms | (10M rows) |
| Full-text ranking | <1s | (50M rows, complex query) |

Real-world case study: Optimized PostgreSQL FTS with GIN indexes achieved **~50x speed improvement** from unoptimized baseline on 10-million-row dataset.

#### When PostgreSQL FTS Wins

✅ **Perfect for:**
- <100 million rows
- Simple to moderate query complexity
- Already using PostgreSQL
- Privacy-critical data (stays in database)
- Limited budget
- Minimalist infrastructure

#### When to Move to Dedicated Search Engine

❌ **Switch when:**
- Queries become too slow (<100ms becomes unacceptable)
- Need advanced relevance tuning beyond BM25
- Complex faceting and filtering across dimensions
- Distributed search required
- Need vector search for semantic queries

### SQLite FTS5

**Surprising finding from 2024-2025 research:** SQLite FTS5 is dramatically faster than expected.

#### Architecture

```sql
-- Create FTS5 virtual table
CREATE VIRTUAL TABLE documents USING fts5(
  id,
  title,
  content,
  tokenize = 'porter',  -- Use porter stemming
  content_rowid = rowid
);

-- Enable BM25 ranking (same as Elasticsearch!)
SELECT *, rank FROM documents
WHERE documents MATCH 'running shoes'
ORDER BY rank;
```

#### Performance

One practitioner replaced Elasticsearch with SQLite FTS5:

> "Median latency crashed to single-digit milliseconds. A single, well-optimized SQLite file on disk delivers high performance without touching a JVM."

**Benchmark results:**
- Single-digit millisecond query latency
- Concurrent read access (WAL mode)
- Trivial operational burden
- Fits on laptop disk

#### Limitations

- Single-file database (limited write parallelism)
- Full-text only (no faceting, aggregations)
- Best for <50GB datasets
- No built-in clustering

#### When SQLite FTS5 Shines

✅ **Excellent for:**
- Embedded search (mobile, desktop)
- Single-machine deployments
- Simple full-text queries
- Minimal operational overhead
- <50GB datasets
- Free/cheap tier products

### Comparative Performance: Databases vs Dedicated Engines

Real-world latencies for a 10M document search:

```
SQLite FTS5:           5-20ms
PostgreSQL FTS (GIN):  50-200ms
PostgreSQL pg_trgm:    100-500ms
Elasticsearch:         10-100ms (highly dependent on cluster size)
Meilisearch:           <50ms
Typesense:             <20ms
Algolia:               50-150ms (global CDN latency)
```

**Critical insight:** Database search is slower than specialized engines, but for most applications, **50-200ms is perfectly acceptable** and avoids operational complexity.

---

## Lightweight & Specialized Alternatives

### Apache Solr (Legacy Powerhouse)

**Status:** Mature, actively developed, less fashionable than Elasticsearch

**When Solr still wins:**

1. **Complex search requirements:** Advanced full-text features, stemming, synonym expansion beyond Elasticsearch
2. **Enterprise ECM:** Widely integrated into document management platforms
3. **Faceted search at scale:** Solr's faceting is optimized differently than ES
4. **Java shop preferences:** Developer familiarity

**Comparison (2025):**
- DB-Engines ranking: Elasticsearch #1 (128.08), Solr #3 (32.40)
- Performance: Comparable to Elasticsearch on complex queries
- Cost: Similar operational burden (Java-based, JVM tuning required)
- Community: Smaller but passionate

**Verdict:** Unless you have existing Solr expertise or complex ECM needs, Elasticsearch is the safer choice for new projects. Solr's market position is declining.

### ZincSearch

**Technology:** Go-based lightweight alternative using Bluge indexing library

**Positioning:** 100x lighter resource footprint than Elasticsearch

**Characteristics:**
- Single binary (~50MB)
- Minimal dependencies
- RESTful API
- Real-time indexing
- Full-text search focus

**Limitations:**
- Much smaller community than Elasticsearch
- Fewer features (no vector search, limited aggregations)
- Less battle-tested at scale

**When to consider:**
- Need lightweight search in constrained environments
- Don't need enterprise features
- Willing to accept smaller ecosystem

**Reality check:** For most teams, the choice is binary: Elasticsearch (enterprise) or Meilisearch/Typesense (modern simple). ZincSearch occupies an uncomfortable middle ground.

---

## Vector Search Engines

Search is evolving beyond keyword matching toward **semantic understanding** via embeddings. Vector databases address this need.

### Vector Search Context

**Traditional BM25:** "athletic footwear" matches "shoe" only if words overlap

**Vector search:** Embedding representation captures semantic similarity
- "athletic footwear" and "running shoe" are close in vector space
- Enables paraphrases, synonyms, conceptual matching

**Trade-off:** Vector search slower (20-100ms) but with superior semantic recall.

### Comparison: Qdrant, Weaviate, Pinecone

#### Qdrant

**Focus:** High-performance, self-hosted vector database

- **Deployment:** Self-hosted or Qdrant Cloud ($0.014/hour hybrid)
- **Features:** Advanced filtering, HNSW indexing, multiple metrics
- **Scaling:** Horizontal (sharding available)
- **Performance:** Best-in-class latency
- **Pricing:** Free for <1GB, then cloud pricing

**When Qdrant wins:**
- Highest performance requirements
- Need on-premises control
- Advanced filtering on metadata
- Cost-conscious (self-hosted free)

#### Weaviate

**Focus:** Graph-like schema-driven vector search with modules

- **Deployment:** Self-hosted or managed
- **Features:** Hybrid search (keyword + vector), GraphQL API
- **Scaling:** Built-in replication
- **Ecosystem:** ML modules for transformers
- **Pricing:** $25/month Serverless, custom enterprise

**When Weaviate wins:**
- Need hybrid keyword + vector search
- GraphQL-native application
- Want semantic modules
- Flexible schema requirements

#### Pinecone

**Focus:** Fully managed, serverless vector database

- **Deployment:** Managed only (no self-hosting)
- **Features:** Simple, polished, very fast
- **Scaling:** Automatic
- **Abstraction:** Hides complexity entirely
- **Pricing:** Free plan (1M vectors), then $0.10/month per pod

**When Pinecone wins:**
- Want minimum operational burden
- Prefer fully managed solution
- Don't need self-hosted option
- Ready to pay for simplicity

### Vector-First vs Vector-As-Addition

**Vector-first engines** (Qdrant, Weaviate, Pinecone):
- Optimized for vector queries
- Keyword search secondary
- Better for pure semantic search

**Vector-as-addition** (Elasticsearch, Meilisearch, Typesense):
- Keyword search primary
- Vector search integrated recently
- Better for hybrid search

**Recommendation:**
- Pure semantic search → Pinecone or Qdrant
- Hybrid keyword+vector → Elasticsearch or Weaviate
- Simple full-text with vectors → Meilisearch or Typesense

---

## Decision Framework

### Step 1: Estimate Dataset Size

```
< 1 GB:      PostgreSQL FTS or SQLite FTS5
1-50 GB:     Meilisearch or Typesense (self-hosted)
50-200 GB:   Elasticsearch (self-hosted, 2-3 node cluster)
200 GB+:     Elasticsearch (larger cluster) or Algolia (SaaS)
```

### Step 2: Query Complexity Requirements

**Simple requirements:**
```
"Find documents containing these words"
→ Database FTS or Meilisearch
```

**Moderate requirements:**
```
Faceting, filtering, typo tolerance, relevance tuning
→ Typesense or Elasticsearch
```

**Complex requirements:**
```
Aggregations, complex bool queries, vector + keyword hybrid
→ Elasticsearch or Algolia
```

### Step 3: Scale & Performance

**Single-machine, <1000 QPS:**
- PostgreSQL FTS
- SQLite FTS5
- Meilisearch
- Typesense

**Multi-machine, 1000-100k QPS:**
- Elasticsearch (self-hosted)
- Algolia (SaaS)
- Qdrant (vector-primary)

**Global, extreme scale:**
- Algolia (proven at massive scale)
- Elasticsearch (AWS-managed or Elastic Cloud)
- Custom distributed system

### Step 4: Operational Capacity

**No ops team, want outsourced:**
→ **Algolia** (SaaS, fully managed)

**Small ops team, self-hosted okay:**
→ **Meilisearch** or **Typesense** (minimal tuning needed)

**Large ops team, control required:**
→ **Elasticsearch** (rich configuration options)

**Want to minimize infrastructure:**
→ **PostgreSQL FTS** (already running PostgreSQL)

### Step 5: Budget Constraints

**$0-50/month:**
- PostgreSQL FTS (free)
- SQLite FTS5 (free)
- Self-hosted Meilisearch ($20 VM)
- Self-hosted Typesense ($20 VM)
- Self-hosted Elasticsearch ($50+ for adequate resources)

**$50-300/month:**
- Self-hosted Elasticsearch (3-node cluster)
- Self-hosted Meilisearch Cloud
- Typesense self-hosted or cloud
- AWS/Azure managed Elasticsearch

**$300-1000+/month:**
- Algolia (growth tier)
- Elastic Cloud (premium tier)
- Custom enterprise solutions

### Decision Tree

```
START
  ↓
Is data already in PostgreSQL?
  YES → Try PostgreSQL FTS first
         Is performance acceptable?
         YES → Done (PostgreSQL FTS)
         NO → Upgrade to Elasticsearch
  NO → Continue
  ↓
Data size <50GB AND simple search?
  YES → Use Meilisearch or Typesense
  NO → Continue
  ↓
Data size <200GB AND self-hosted acceptable?
  YES → Use Elasticsearch
  NO → Continue
  ↓
Need managed, full-featured SaaS?
  YES → Use Algolia
  NO → Continue
  ↓
Vector search primary requirement?
  YES → Use Qdrant or Pinecone
  NO → Use Elasticsearch or Algolia
```

---

## Cost Analysis & Benchmarks

### Total Cost of Ownership (TCO) Comparison

For a typical e-commerce application with:
- 1 million products
- 1 million daily searches
- 99.9% availability requirement

#### PostgreSQL FTS

```
Infrastructure:      $50/month (RDS multi-AZ)
Operational labor:   $200/month (DBA part-time)
Total:              ~$250/month
```

**Pros:** Minimal cost, simplest
**Cons:** Limited to ~5-10ms query latency scaling limit

#### Self-hosted Elasticsearch

```
Infrastructure:      3-node cluster @ $400/month
  Node 1 (master):   $150/month (4GB RAM, 2 CPU)
  Node 2 (data):     $150/month (32GB RAM, 8 CPU)
  Node 3 (data):     $150/month (32GB RAM, 8 CPU)
Storage (EBS):       $100/month (500GB @ $0.20/GB)
Operational labor:   $1000/month (dedicated eng, JVM tuning)
Total:              ~$1500/month
```

**Pros:** Full control, enterprise features
**Cons:** Operational complexity, high labor cost

#### Elasticsearch (Elastic Cloud)

```
Managed cluster:     $800/month (equivalent resources)
  Cluster tier:      $500/month
  Storage & backup:  $300/month
Operational labor:   $200/month (minimal, vendor handles most)
Total:              ~$1000/month
```

**Pros:** Reduced ops burden, vendor support
**Cons:** Higher base cost than self-hosted

#### Meilisearch (self-hosted)

```
Infrastructure:      $50/month (2GB RAM, single VM)
Operational labor:   $100/month (minimal tuning)
Total:              ~$150/month
```

**Pros:** Cheapest operational cost
**Cons:** Scaling limited to single machine

#### Meilisearch Cloud

```
Meilisearch Cloud:   $100/month (production tier)
Operational labor:   $0/month
Total:              ~$100/month
```

**Pros:** Managed, no ops, affordable
**Cons:** Less control than self-hosted

#### Typesense Cloud

```
Typesense Cloud:     $200/month (production tier)
Operational labor:   $0/month
Total:              ~$200/month
```

**Pros:** Managed, high performance
**Cons:** More expensive than Meilisearch

#### Algolia

```
Search requests:     1M/month @ $0.50 per 1000 = $500
Records:             1M @ $0.40 per 1000 = $400
Basic analytics:     $0
Operational labor:   $0/month
Total:              ~$900/month
```

**Pros:** Fully managed, excellent support
**Cons:** Most expensive base cost

### Cost Comparison Summary

| Solution | $/month | Pros | Cons |
|----------|---------|------|------|
| PostgreSQL FTS | $250 | Simplest, cheapest | Limited scale |
| Meilisearch (self) | $150 | Cheap, managed | Single-node limit |
| Meilisearch Cloud | $100 | Managed, affordable | Less control |
| Typesense (self) | $150 | Fast, self-hosted | Single-node limit |
| Typesense Cloud | $200 | Managed, fast | Higher base cost |
| Elasticsearch (self) | $1500 | Full control | High ops cost |
| Elasticsearch (Cloud) | $1000 | Balanced | Still operational overhead |
| Algolia | $900 | Fully managed, SaaS | Highest base cost |

**Breakeven analysis:**

- **PostgreSQL → Meilisearch:** When query latency < 5ms becomes critical and PostgreSQL can't scale further
- **Meilisearch → Elasticsearch:** When data > 100GB or distributed search required
- **Self-hosted → SaaS:** When operational labor cost > managed service premium

---

## Performance Benchmarks

### Query Latency (p50, p99)

**1 million document searches, typical e-commerce queries:**

```
Engine              | p50    | p99    | Notes
PostgreSQL FTS      | 100ms  | 500ms  | Without aggressive caching
SQLite FTS5         | 10ms   | 50ms   | Single machine
Meilisearch         | 30ms   | 80ms   | Instant search focus
Typesense           | 15ms   | 50ms   | In-memory optimization
Elasticsearch       | 50ms   | 200ms  | Depends on cluster size
Algolia             | 100ms  | 200ms  | Global CDN overhead
```

### Indexing Throughput

**Documents per second:**

```
Engine              | Throughput  | Notes
Meilisearch         | 300k/sec    | Fastest
Typesense           | 100k/sec    | Consistent
Elasticsearch       | 50k/sec     | Varies with config
PostgreSQL FTS      | 10k/sec     | Limited by MVCC
Algolia             | Async       | Ingestion pipeline
```

### Memory Efficiency

**Memory used per million documents:**

```
Engine              | Memory   | Notes
SQLite FTS5         | 500MB    | Very efficient
PostgreSQL FTS      | 2GB      | Tuple overhead
Meilisearch         | 3-5GB    | Entire index in RAM
Typesense           | 5-10GB   | All data in memory
Elasticsearch       | 10-20GB  | Heavy JVM footprint
```

---

## Migration Considerations

### PostgreSQL → Elasticsearch

**When to migrate:**

1. Query latency unacceptable (<10ms required)
2. Data size approaching PostgreSQL limits (>200GB)
3. Complex faceting/aggregations needed
4. Distributed search required

**Migration path:**

```
1. Set up Elasticsearch cluster in parallel
2. Write documents to both PostgreSQL and Elasticsearch
3. Run dual reads (ES for search, PG for detailed queries)
4. Verify result quality matches expectations
5. Switch traffic to Elasticsearch
6. Keep PostgreSQL as system of record
7. Run in dual-write mode for 30+ days
8. Decommission duplicate data flow
```

**Effort:** 2-4 weeks for most applications

### Elasticsearch → Meilisearch

**When this makes sense:**

1. Operational costs are killing you
2. Data < 100GB
3. No complex aggregations required
4. Distributed search not critical

**Migration path:**

```
1. Export data from Elasticsearch (JSON)
2. Transform to Meilisearch format (usually same)
3. Bulk import to Meilisearch
4. Test search quality (may need to adjust ranking rules)
5. Parallel queries (ES + Meilisearch) for validation
6. Switch traffic
7. Monitor for 2 weeks
```

**Effort:** 1-2 weeks

### Multiple Search Engines (Polyglot Search)

Some teams run multiple search engines for different purposes:

```
PostgreSQL FTS → simple text search, relational queries
Elasticsearch → complex searches, analytics, large datasets
Vector DB → semantic search, recommendations
```

**Pros:**
- Right tool for job
- Optimize each independently

**Cons:**
- Operational complexity
- Data sync challenges
- Multiple indices to maintain

---

## Conclusion & Recommendations

### Quick Decision Guide (2025)

**Startup (MVP phase):**
→ PostgreSQL FTS (already running) or Meilisearch ($100/month)

**Growth (10M-100M docs):**
→ Meilisearch or Typesense (self-hosted) or Elasticsearch

**Scale (100M+ docs, multiple regions):**
→ Elasticsearch or Algolia (choose based on ops capacity)

**Vector-primary AI app:**
→ Qdrant or Pinecone (depending on managed vs self-hosted)

### The Search Engine Maturity Curve

```
Simple products    → Database FTS
                     ↓
Growing products   → Meilisearch/Typesense
                     ↓
Large platforms    → Elasticsearch
                     ↓
Enterprise        → Elasticsearch + Algolia (specialized)
```

### Future Trends (2026+)

1. **Vector search mainstream:** Every product will combine keyword + semantic search
2. **SaaS consolidation:** Algolia, Typesense, Meilisearch Cloud will compete heavily on price
3. **Self-hosted simplification:** OpenSearch and newer engines will erode Elasticsearch's dominance
4. **Database renaissance:** PostgreSQL vector extensions may eliminate need for separate vector DB
5. **Hybrid-first design:** Default assumption: keyword search + vector search, not either/or

---

## References & Further Reading

### Architecture Resources
- [Elasticsearch Architecture - Elastic Docs](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards)
- [Elasticsearch Architecture X: Exploration of the Inverted Index](https://braineanear.medium.com/elasticsearch-architecture-x-exploration-of-the-inverted-index-3928458a6a85)
- [Practical BM25 - The BM25 Algorithm and its Variables](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)

### Comparative Analysis
- [OpenSearch vs Elasticsearch: A Comprehensive Comparison in 2025](https://medium.com/@FrankGoortani/opensearch-vs-elasticsearch-a-comprehensive-comparison-in-2025-aff5a8533422)
- [Meilisearch vs Typesense](https://www.meilisearch.com/blog/meilisearch-vs-typesense)
- [Elasticsearch vs Typesense: A definitive comparison](https://www.meilisearch.com/blog/elasticsearch-vs-typesense)
- [Comparison with Alternatives - Typesense](https://typesense.org/docs/overview/comparison-with-alternatives.html)

### Performance & Benchmarks
- [search engine benchmarks Meilisearch Typesense Algolia performance comparison 2025](https://www.meilisearch.com/blog/algolia-vs-typesense)
- [Elasticsearch Shards & Replicas Guide](https://www.elastic.co/search-labs/blog/elasticsearch-shards-and-replicas-guide)
- [How many shards should I have in my Elasticsearch cluster?](https://www.elastic.co/blog/how-many-shards-should-i-have-in-my-elasticsearch-cluster)

### Database Full-Text Search
- [PostgreSQL Full-Text Search Docs](https://www.postgresql.org/docs/current/textsearch-indexes.html)
- [Implementing High-Performance Full Text Search in Postgres](https://risingwave.com/blog/implementing-high-performance-full-text-search-in-postgres/)
- [SQLite FTS5 Extension](https://sqlite.org/fts5.html)
- [I Replaced Elasticsearch with SQLite and Search Got 100x Faster](https://medium.com/@build_break_learn/i-replaced-elasticsearch-with-sqlite-and-our-search-got-100x-faster-5343a4458dd4)

### SaaS & Pricing
- [Algolia Pricing: Worth It or Consider Meilisearch?](https://www.meilisearch.com/blog/algolia-pricing)
- [Algolia Pricing 2025](https://www.g2.com/products/algolia/pricing)

### Vector Search
- [Introducing approximate nearest neighbor search in Elasticsearch 8.0](https://www.elastic.co/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0)
- [Vector DB Comparison: Pinecone vs Weaviate vs Qdrant](https://pr-peri.github.io/blogpost/2026/01/10/blogpost-vector-db-comparison.html)
- [Pinecone vs Qdrant vs Weaviate: Best vector database](https://xenoss.io/blog/vector-database-comparison-pinecone-qdrant-weaviate)

### Operational Guidance
- [JVM essentials for Elasticsearch: Metrics, memory, and monitoring](https://www.elastic.co/blog/jvm-essentials-for-elasticsearch)
- [5 Elasticsearch Cost Optimization Best Practices](https://bigdataboutique.com/blog/5-elasticsearch-cost-optimization-best-practices-ad641d)
- [ZincSearch - A lightweight alternative to Elasticsearch](https://github.com/zincsearch/zincsearch)

### Fuzzy & Trigram Search
- [Fuzzy Search with PostgreSQL Trigrams: Smarter Matching Beyond LIKE](https://medium.com/@vinodjagwani/fuzzy-search-with-postgresql-trigrams-smarter-matching-beyond-like-bce2bd3c4548)
- [You Don't Need Elasticsearch! Fuzzy Search with PostgreSQL and Spring Data](https://febrihasan.medium.com/you-dont-need-elasticsearch-fuzzy-search-with-postgresql-and-spring-data-96b4ff23d710)

### Hybrid Search
- [A Comprehensive Hybrid Search Guide](https://www.elastic.co/what-is/hybrid-search)
- [Elasticsearch hybrid search: Overview & hybrid search queries](https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch)

---

**Document created:** March 2026
**For:** Claude Skills Knowledge Base
**Status:** Production-ready reference guide

---

## See Also (Cross-References)

→ **references/00-stack-blueprints/** — Blueprint #1 (SaaS App), #3 (E-commerce), #6 (Real-time) show search engine architecture
→ **references/00-benchmark-matrix/** — Search engine performance comparison table with latency/cost metrics
→ **references/00-migration-playbooks/** — Playbook #5: ES → Hybrid ES demonstrates architecture upgrade path
→ **references/05-hybrid-search/** — Add hybrid keyword+vector search to any server-side engine
→ **references/45-neural-reranking-distillation/** — Add reranking layer to any search engine for refinement
→ **references/11-vector-databases/** — Vector databases as alternative or complement to keyword engines

