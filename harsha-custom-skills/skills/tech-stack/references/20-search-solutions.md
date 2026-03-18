# Search Solutions: Comprehensive Comparison 2025-2026

A deep technical analysis of search platforms including Meilisearch, Typesense, Algolia, Elasticsearch, Orama, and PostgreSQL full-text search (pg_trgm).

---

## Executive Summary

This document provides a comprehensive analysis of six major search solutions to help architects make informed decisions. The landscape has evolved significantly, with self-hosted options becoming viable alternatives to SaaS platforms for mid-market use cases.

**Key Trend:** Open-source solutions (Meilisearch, Typesense) now offer feature parity with enterprise platforms (Algolia, Elasticsearch) at a fraction of the cost, making deployment model choice increasingly about operational complexity rather than capability gaps.

---

## 1. MEILISEARCH

### Solution Type
- **Category:** Modern, developer-friendly search engine
- **License:** MIT (open source)
- **Deployment:** Self-hosted or managed cloud platform
- **Language:** Rust
- **Architecture:** HTTP REST API first, built for ease of use

### Pricing (2025-2026)

#### Cloud Hosted (Meilisearch Platform)
- **Free Tier:** 14-day free trial; self-hosted version is permanently free
- **Build Plan:** $30/month (usage-based pricing)
- **Pro Plan:** $300/month (usage-based pricing)
- **Enterprise:** Custom pricing for dedicated resources
- **Pricing Model:** Resource-based pricing option available; pay for resources, not per-query

#### Self-Hosted
- **Cost:** Completely free (open source)
- **Infrastructure:** Minimal—can run on $5/month VPS with 1GB RAM for small datasets

### Performance (Search Latency)

| Dataset Size | Typical Latency | Notes |
|---|---|---|
| <100K documents | <10ms | Excellent |
| 100K-1M documents | 10-50ms | Fast |
| 1M-10M documents | 50-200ms | Good, depends on RAM |
| >10M documents | 200ms-1s+ | Depends on hardware |

**Memory Impact:** Search speed is proportional to RAM-to-database-size ratio. A big database with small RAM = slow search; small database with ample RAM = very fast search.

**Real-Time Indexing:** Supported; asynchronous indexing prevents blocking search operations.

### Features

#### Core Search Capabilities
- ✅ **Typo Tolerance:** Full support with configurable sensitivity; can be disabled for specific fields
- ✅ **Facets & Filters:** Full faceted navigation and complex filtering
- ✅ **Geo-Search:** Geographic radius search fully supported
- ✅ **Synonyms:** Synonym definition and expansion built-in
- ✅ **Ranking & Relevance:** Customizable ranking rules

#### Advanced Features
- ✅ **Hybrid Search:** Combines full-text and vector search (requires embedder integration)
- ✅ **Vector/Semantic Search:** AI-powered semantic search via OpenAI, HuggingFace embedders
- ✅ **Multitenancy:** Tenant isolation and multi-index support
- ✅ **Analytics:** Built-in search analytics
- ✅ **Localization:** Support for 100+ languages

### SDKs & Libraries

**Official SDKs Available:**
- JavaScript/TypeScript (npm: `meilisearch`)
- Python (pip: `meilisearch` or `meilisearch-python-sdk`)
- .NET / C#
- Go
- Java
- PHP
- Ruby
- Rust

**API:** RESTful HTTP API with comprehensive endpoint coverage
**Framework Integrations:** Strapi, Next.js, Astro, Laravel plugins available

### Self-Hosting Requirements

#### Recommended System Specifications
- **CPU:** No direct impact on search speed; more cores allow concurrent query handling
  - Default: Uses max 50% of available cores for indexing
  - Example: 12-core CPU = indexer uses 6 cores
- **RAM:** Critical for performance
  - Minimum: 512MB for tiny datasets
  - Recommended: 10x dataset disk size for optimal performance
  - Scaling: RAM consumption scales linearly with dataset size
- **Disk:** 10x the size of your raw dataset for search indices
  - Example: 100MB dataset = 1GB disk space
- **Indexing Memory:** Adapts to use maximum 2/3 of available RAM
  - For 4GB machine: Don't set limit to 4GB; allocate ~2.5GB maximum

#### Deployment Options
- Docker containers (official images available)
- Kubernetes (Helm charts supported)
- Binary installation (single executable)
- VPS deployment (verified: $5/month hosting viable for small-to-medium datasets)

#### Operational Simplicity
- Single binary deployment
- No external dependencies required
- Simple HTTP API
- Built-in dashboard available

### Index Size Limits
- **Cloud Platform:** Scales to multi-GB indices
- **Self-Hosted:** Limited only by available RAM and disk storage
- **Practical Limits:** Typically 10-100GB per instance; sharding recommended for larger indices
- **Index Management:** Automatic synchronization across replicas possible

### Real-Time Indexing
- **Update Latency:** Milliseconds to seconds depending on document size
- **Asynchronous Indexing:** Prevents query blocking during updates
- **Bulk Operations:** Supported for efficient batch indexing

---

## 2. TYPESENSE

### Solution Type
- **Category:** Ultra-fast, lightweight search engine
- **License:** MIT (open source, with enterprise licensing option)
- **Deployment:** Self-hosted or managed Typesense Cloud
- **Language:** C++ (native binary)
- **Architecture:** In-memory search optimized for speed

### Pricing (2025-2026)

#### Cloud Hosted (Typesense Cloud)
- **Free Tier:** No traditional free tier; self-hosted is free
- **Pricing Model:** Resource-based (memory, CPU, bandwidth)
  - **Memory:** Core pricing factor (0.5GB to 1024GB options)
  - **CPU:** Shared vCPU with burst or dedicated vCPU
  - **Starting Price:** ~$7/month for 0.5GB configuration
  - **Bandwidth:** Additional charges for data transfer
- **Support Plans:**
  - Developer: $160/month
  - Business: $400/month
  - Enterprise: $700/month

#### Self-Hosted
- **Cost:** Completely free (open source, MIT license)
- **Infrastructure:** Very lightweight; single binary, minimal footprint

### Performance (Search Latency)

| Metric | Value |
|---|---|
| **Typical Latency** | <50ms |
| **At 1M+ Records** | ~50ms sustained |
| **Typo Correction** | Built-in, enabled by default |
| **Index In-Memory** | 100% in-memory + disk copy |

**Architecture Advantage:** Single lightweight C++ binary with entire index in-memory delivers exceptional latency consistency.

**Real-Time Indexing:** Supported with minimal blocking

### Features

#### Core Search Capabilities
- ✅ **Typo Tolerance:** Automatic, configurable; can be disabled
- ✅ **Facets & Filters:** Full faceted navigation and advanced filtering
- ✅ **Geo-Search:** Geographic radius and proximity search
- ✅ **Synonyms:** Synonym expansion and definition
- ✅ **Ranking:** Customizable relevance ranking

#### Advanced Features
- ✅ **Vector Search:** Semantic search via automatic embedding generation
- ✅ **Hybrid Search:** Combines keyword and vector search
- ✅ **Natural Language Search:** LLM-powered intent detection and query understanding
- ✅ **Image Search:** Search images via text descriptions (CLIP model)
- ✅ **Voice Search:** Voice query support
- ✅ **Collection JOINs:** SQL-like relationships between collections
- ✅ **Synonyms:** Configurable synonym definitions
- ✅ **Analytics:** Search performance and usage metrics

### SDKs & Libraries

**Official SDKs:**
- JavaScript/TypeScript (npm: `typesense`)
- Python (pip: `typesense`)
- Ruby
- Java
- Go
- PHP
- Dart

**API:** RESTful HTTP + WebSocket support for real-time updates
**Framework Support:** Extensive integration guides for popular frameworks

### Self-Hosting Requirements

#### System Specifications
- **CPU:** Affects concurrent query throughput, not individual query speed
- **RAM:** Critical—entire index stored in memory
  - Minimum: 512MB for small datasets
  - Scales with index size (proportional)
  - Production: Typically 4-16GB per node
- **Disk:** Persistent copy of index for durability
- **Network:** Low bandwidth requirements

#### Deployment
- **Binary:** Single lightweight native executable
- **Simplicity:** Minimal setup required
- **Clustering:** High-availability clustering available
- **Docker:** Official images available
- **Kubernetes:** Deployable via manifests

#### Operational Benefits
- Single self-contained binary (no JVM, no external processes)
- Very low resource overhead compared to Elasticsearch
- Simple HTTP API
- Fast startup/restart

### Index Size Limits
- **Self-Hosted:** Limited by available RAM on node
- **Cloud:** Up to 1024GB memory (custom sizing)
- **Clustering:** Horizontal scaling via collection-level sharding
- **Practical Deployment:** 100GB+ indices possible with adequate RAM

### Real-Time Indexing
- Asynchronous indexing supported
- WebSocket streaming updates available
- Typical indexing latency: Milliseconds per document

---

## 3. ALGOLIA

### Solution Type
- **Category:** Enterprise SaaS search platform with AI/ML features
- **Deployment:** SaaS only (cloud hosted by Algolia)
- **Language:** Proprietary, multi-language infrastructure
- **Architecture:** Distributed, globally replicated infrastructure

### Pricing (2025-2026)

#### Pricing Tiers

| Plan | Free Tier | Cost | Details |
|---|---|---|---|
| **Build** | Yes | Free | 1M records, 10K requests/month; no credit card required |
| **Grow** | $0+ | Pay-as-you-go | Free tier + $0.50 per 1K additional requests |
| **Grow Plus** | — | $$ | Includes AI features (ranking, personalization) |
| **Elevate** | — | $$$+ | Full AI Search: NeuralSearch, Smart Groups, AI Collections (annual contract) |
| **Enterprise** | — | Custom | Custom features, SLAs, support |

**Key Pricing Factor:** Request-based billing; costs scale with search volume

### Performance (Search Latency)

| Metric | Value | Notes |
|---|---|---|
| **P50 Latency** | ~100ms | Global average |
| **P99 Latency** | <1s | Varies by region |
| **Global CDN** | Yes | Distributed edge caching |
| **Regional Failover** | Automatic | Built-in redundancy |

**Architecture:** Globally distributed infrastructure with edge caching minimizes latency for distributed users.

### Features

#### Core Search Capabilities
- ✅ **Typo Tolerance:** Advanced, context-aware correction
- ✅ **Facets & Filters:** Powerful faceted navigation and filtering
- ✅ **Geo-Search:** Geographic search with complex filters
- ✅ **Synonyms:** Synonym expansion and management
- ✅ **Ranking:** Rule-based ranking customization
- ✅ **Sorting:** Multi-field sorting

#### Enterprise Features
- ✅ **NeuralSearch:** Hybrid neural + full-text search (Elevate plan only)
- ✅ **Advanced Personalization:** User-based result personalization
- ✅ **A/B Testing:** Native A/B testing for search results
- ✅ **Analytics:** Comprehensive search analytics and insights
- ✅ **Dynamic Ranking:** Machine learning-based ranking
- ✅ **Auto-Scaling:** Automatic infrastructure scaling
- ✅ **Multi-Tenancy:** Enterprise-grade tenant isolation

**Limitation:** AI features (NeuralSearch) reserved for highest tier; requires event data

### SDKs & Libraries

**Official SDKs (10+ languages):**
- JavaScript/TypeScript (npm: `algoliasearch`)
- Python (pip: `algoliasearch`)
- Java, Go, Ruby, PHP, C#, Kotlin, Swift, React

**API:** RESTful HTTP + client-side libraries
**Framework Integrations:** InstantSearch libraries for React, Vue, Angular, etc.

### Self-Hosting
- **Not available:** Algolia is SaaS-only
- **Alternative:** Self-host Meilisearch or Typesense for similar feature set with lower cost

### Index Size Limits
- **Per Plan:** Varies by pricing tier
  - Build: 1M records
  - Grow+: No hard limit (pay-as-you-go)
  - Enterprise: Custom limits
- **Global Limit:** Designed for large-scale deployments (17,000+ customers)

### Real-Time Indexing
- Asynchronous indexing supported
- Real-time replica synchronization
- Typical update latency: Seconds

---

## 4. ELASTICSEARCH

### Solution Type
- **Category:** Distributed search and analytics platform
- **License:** SSPL/Elastic License 2.0 (proprietary); AGPL v3 OSS option
- **Deployment:** Self-hosted or Elastic Cloud SaaS
- **Language:** Java
- **Architecture:** Distributed, horizontally scalable cluster

### Pricing (2025-2026)

#### Elastic Cloud (SaaS)
- **Standard Plan:** $99/month
  - 4GB RAM + 120GB storage (~$95/month)
  - 8GB RAM + 240GB storage (~$190/month)
  - 16GB RAM + 480GB storage (~$380/month)
- **Platinum Plan:** $131/month
  - Full SIEM, machine learning, advanced security
- **Enterprise:** Custom pricing

**Billing Model:** Per GB RAM/hour for Elasticsearch, Kibana, and APM nodes

#### Free Tier
- **Free OSS:** Open-source AGPL v3 version with limited features
- **Basic Free Tier:** Cloud account with limited features and storage
- **Trial:** 14-day trial of paid features

#### Self-Hosted (Open Source)
- **Cost:** Free (AGPL v3 or Elastic License 2.0)
- **Infrastructure:** You provision and maintain
- **Operations:** Significant operational overhead

### Performance (Search Latency)

| Use Case | Latency | Notes |
|---|---|---|
| **Simple Search** | 50-200ms | Index size dependent |
| **Complex Aggregations** | 100ms-10s | Query complexity dependent |
| **Large Datasets** | Highly variable | Sharding and optimization critical |
| **Distributed** | +50-100ms | Network latency per shard |

**Performance Characteristics:** Highly dependent on shard count, query complexity, and cluster configuration. Requires tuning.

### Features

#### Core Search Capabilities
- ✅ **Full-Text Search:** Highly configurable text analysis
- ✅ **Facets & Filters:** Aggregations framework for faceting
- ✅ **Boolean Filters:** Complex boolean query combinations
- ✅ **Sorting:** Multi-field sorting
- ✅ **Fuzzy Search:** Fuzzy matching available

#### Advanced Features
- ✅ **Vector Search:** Native vector field support (v8.0+)
- ✅ **Machine Learning:** Built-in anomaly detection, forecasting
- ✅ **Geospatial Search:** Geographic queries and aggregations
- ✅ **Time-Series Data:** Specialized time-series data support
- ✅ **Analytics:** Real-time analytics and dashboards (Kibana)
- ✅ **Security:** RBAC, field-level security, audit logging (paid tiers)

**Note:** Typo tolerance and geo-search require configuration; not automatic

### SDKs & Libraries

**Official Clients (8+ languages):**
- JavaScript/Node.js (npm: `@elastic/elasticsearch`)
- Python (pip: `elasticsearch`)
- Java, Go, Ruby, PHP, .NET, Rust

**API:** RESTful HTTP only
**Query DSL:** JSON-based query language (steep learning curve)

### Self-Hosting Requirements

#### System Specifications (Production Cluster)
- **CPU:** Affects query throughput
  - Minimum: 2 cores per node
  - Recommended: 4-8 cores
- **RAM:** Critical—heap space directly impacts performance
  - Recommended: 50% of available RAM for Java heap
  - Minimum: 4GB heap (8GB total RAM)
  - Production: 16-32GB+ per node typical
  - Example: 64GB server = 32GB heap allocation
- **Disk:** Fast SSD storage required
  - Size: 3-5x index size (replication, logs, temporary)
  - IOPS: High-speed storage critical for performance
- **Network:** Fast interconnects for cluster communication

#### High Availability Cluster
- **Minimum 3 Nodes:** For fault tolerance
- **Per Node:** 4-16GB RAM minimum (production)
- **Total Cluster:** 12-48GB+ RAM for production deployments
- **Master Nodes:** Dedicated master nodes recommended for large clusters

#### Operational Complexity
- Complex cluster setup and configuration
- Requires ongoing monitoring and tuning
- Snapshot/restore for disaster recovery
- Index lifecycle management (ILM)
- Security hardening required (paid tiers)

#### Deployment Options
- Self-managed on VMs
- Docker/Kubernetes (ECK - Elasticsearch Cloud on Kubernetes)
- Hybrid (Elastic Cloud Enterprise - ECE)

### Index Size Limits
- **Per Shard:** Typically 40-50GB recommended maximum
- **Total Index:** No hard limit (scale with shards)
- **Large Indices:** 100GB-TB possible with proper sharding
- **Scaling:** Horizontal scaling requires operational expertise

### Real-Time Indexing
- Near-real-time search (refresh interval configurable, default 1s)
- Asynchronous indexing supported
- Bulk indexing for efficiency

---

## 5. ORAMA

### Solution Type
- **Category:** Client-side/edge search engine
- **License:** MIT (open source)
- **Deployment:** Browser (client-side), server, edge networks
- **Language:** TypeScript
- **Architecture:** Lightweight in-memory search for small-to-medium datasets

### Pricing (2025-2026)

#### Free Plan
- 150 index updates per month
- Unlimited hybrid search queries
- Unlimited AI-generated summaries
- Analytics (60-day retention)

#### Cloud Platform Plans
- **Pro Plan:** Higher limits, 365-day analytics retention
- **Premium Plan:** Advanced features, extended retention
- **Enterprise Plan:** Custom limits, custom retention periods
- **Model:** Flat-fee access to unlimited hybrid search
- **Specific Pricing:** Not disclosed in public documentation

#### Self-Hosted (Open Source)
- **Cost:** Free (MIT license)
- **Distribution:** NPM package for Node.js and browsers

### Performance (Search Latency)

| Deployment | Latency | Limitations |
|---|---|---|
| **Browser (Client-Side)** | <50ms | Limited to in-memory index; entire index in RAM |
| **Server/Node.js** | <50ms | Server-side resource constraints |
| **Edge Network** | <100ms | Global distribution, minimal latency |

**Constraint:** Entire search index must fit in user's browser RAM; practical limit ~3-5MB JSON index.

**Typical Use Case:** Small documentation sites, blog search, limited product catalogs

### Features

#### Core Search Capabilities
- ✅ **Full-Text Search:** Full-text indexing and search
- ✅ **Facets & Filters:** Faceted navigation and filtering
- ✅ **Typo Tolerance:** Fuzzy matching available
- ✅ **Sorting:** Custom sorting options
- ✅ **Boolean Queries:** Complex query combinations

#### Advanced Features
- ✅ **Hybrid Search:** Combines full-text and vector search
- ✅ **Vector/Semantic Search:** AI-powered semantic search
- ✅ **AI Answers:** Generate summaries from search results
- ✅ **Global Edge Network:** 300+ points of presence in 100+ countries
- ✅ **Analytics:** Search analytics built-in
- ✅ **Multilingual:** Support for multiple languages

**Advantage:** Extremely lightweight (<2KB library); runs directly in browser

### SDKs & Libraries

**Official Support:**
- JavaScript/TypeScript (npm: `@orama/sdk`)
- Node.js
- Browser (vanilla JS)
- Framework integrations: Astro, Next.js, Nuxt support documented

**API:** JavaScript SDK with fluent query builder
**No REST API:** Client-side library only

### Self-Hosting

#### Browser Deployment
- **Distribution:** Ship compiled index with your application
- **Size:** Depends on dataset; typical 1-10MB for small sites
- **UX Impact:** Requires downloading entire index; larger indices degrade UX
- **Optimization:** Compress using gzip or brotli

#### Server/Node.js Deployment
- **Deployment:** npm install + startup
- **Resources:** Minimal (100MB RAM possible for small indices)
- **Scaling:** Vertical only; designed for single-server deployment

### Index Size Limits
- **Browser:** Practical limit 3-5MB JSON
  - Full body text = 3x increase
  - Example: 1000 documents @ 1KB average = ~3MB index
- **Server/Node.js:** Limited by available RAM
  - 512MB RAM supports ~100K documents
  - 4GB RAM supports ~1M documents
- **Cloud Platform:** Scales as needed with subscription tier

### Real-Time Indexing
- Browser: Indexes on data received
- Server: Asynchronous indexing available
- Update latency: Milliseconds to seconds

---

## 6. PostgreSQL FULL-TEXT SEARCH (pg_trgm + tsvector)

### Solution Type
- **Category:** Native PostgreSQL full-text search capability
- **Cost:** Free (included with PostgreSQL)
- **Extensions:** `pg_trgm` (trigrams), `tsvector` (full-text vectors)
- **Architecture:** Built-in to PostgreSQL, no separate service
- **Use Case:** "Good enough" for small-to-medium datasets

### Pricing
- **Cost:** $0 (included with PostgreSQL)
- **Infrastructure:** Existing PostgreSQL instance
- **No SaaS:** Self-hosted only (or managed PostgreSQL provider)

### Performance (Search Latency)

| Scenario | Latency | Method |
|---|---|---|
| **Full-Text Search (tsvector)** | 10-100ms | ~5x faster than pg_trgm |
| **Fuzzy/Trigram (pg_trgm)** | 50-500ms | Much slower for long documents |
| **Indexed Queries** | 10-50ms | With proper GIN/GIST indexing |
| **Large Tables (>10M rows)** | 100ms-5s | Depends on index selectivity |

**Critical Limitation:** pg_trgm becomes very slow when:
- Many rows match the trigram pattern
- Documents are long (requires "recheck" on every match)
- Query matches nearly all trigrams (can devolve to full table scan)

### Features

#### Full-Text Search (tsvector)
- ✅ **Language-Specific Processing:** Stemming, stop words for 20+ languages
- ✅ **Ranking:** Multiple ranking algorithms (TF, TF-IDF)
- ✅ **Phrase Search:** Proximity-based phrase search
- ✅ **Boolean Operators:** AND, OR, NOT combinations
- ✅ **Complex Queries:** Nested boolean expressions
- ✅ **Indexing:** Fast GIN indexes available

#### Fuzzy/Similarity Search (pg_trgm)
- ✅ **Fuzzy Matching:** Case-insensitive similarity search
- ✅ **Mid-String Matching:** Match anywhere in text
- ✅ **Short String Focus:** Optimized for short fields (names, emails)
- ✅ **Threshold Tuning:** Configurable similarity threshold
- ✅ **GIST/GIN Indexes:** Can be indexed for speed

#### NOT Available
- ❌ Typo Tolerance (fuzzy, but not "smart" correction)
- ❌ Faceted Search (requires application logic)
- ❌ Geo-Search (requires PostGIS extension)
- ❌ Semantic/Vector Search (no native vector support; v16 has PG Vector)
- ❌ Field-Level Ranking Control
- ❌ Analytics
- ❌ Synonyms

### SDKs & Libraries
- **Not Applicable:** Direct PostgreSQL SQL queries via any database client
- **Popular Clients:** psycopg2 (Python), pg (Node.js), sqlc (compiled SQL)
- **ORMs:** Sequelize, TypeORM, SQLAlchemy support through SQL functions
- **Example Query:**
  ```sql
  SELECT id, title, ts_rank(ts_col, plainto_tsquery('english', 'search term')) as rank
  FROM documents
  WHERE ts_col @@ plainto_tsquery('english', 'search term')
  ORDER BY rank DESC
  LIMIT 20;
  ```

### Self-Hosting Requirements
- **Infrastructure:** Any PostgreSQL 9.6+
- **Extensions:** Enable via `CREATE EXTENSION pg_trgm;`
- **Resource Impact:** Minimal; full-text indexes stored in main table
- **Maintenance:** Regular ANALYZE and VACUUM
- **Scaling:** Single instance up to ~10-50M documents practical

### Index Size Limits
- **Table Size Limit:** PostgreSQL 32TB maximum per table
- **Practical Limits:** 100M-1B rows achievable with proper indexing
- **Index Size:** Full-text indices typically 20-40% of table size

### Real-Time Indexing
- Automatic: Indices updated on INSERT/UPDATE/DELETE
- Synchronous: Part of transaction
- Latency: None (synchronous with writes)

---

## Decision Logic Matrix: When to Use Each Solution

### Decision Tree

```
START: Need Search?
├─ YES → Continue to criteria
└─ NO  → Use simple LIKE/ILIKE with wildcards

HAVE EXISTING POSTGRESQL DATABASE?
├─ YES → Go to PostgreSQL Decision
└─ NO  → Continue to Commercial/OSS Decision

DATASET SIZE?
├─ SMALL (<100K docs) → Go to Orama/PostgreSQL consideration
├─ MEDIUM (100K-10M)  → All options viable
└─ LARGE (>10M)       → Go to Scalability Consideration

DEPLOYMENT PREFERENCE?
├─ MANAGED SaaS (No Ops)  → Algolia
├─ Self-Hosted (Full Control) → Go to Feature/Performance Trade
└─ Hybrid                  → Meilisearch Cloud or Typesense Cloud

FEATURES REQUIRED?
├─ ADVANCED (AI, Ranking, Personalization) → Algolia or Meilisearch
├─ STANDARD (Facets, Filters, Typo Tolerance) → All except PostgreSQL
└─ BASIC (Full-text only)  → PostgreSQL or Orama

```

### Decision Table: Feature-Price-Performance

| Solution | Best For | Avoid When |
|---|---|---|
| **Meilisearch** | Fast deployment, modern features, open-source, mid-market scale | Need enterprise support/SLAs (use Algolia instead) |
| **Typesense** | Ultra-low latency, lightweight operations, small team, C++ performance | Need global CDN or advanced ML ranking |
| **Algolia** | Enterprise SaaS, AI ranking/personalization, global reach, 10K+ customers | Budget-constrained; self-hosting preference; in-house ops team |
| **Elasticsearch** | Large-scale analytics, log aggregation, complex data, complex queries | Need simple search; small teams; low ops budget |
| **Orama** | Browser-based search, edge deployment, tiny datasets, AI summaries | Large datasets; backend search only; complex filtering needs |
| **PostgreSQL** | Already have PG, simple search needs, strong consistency required, <100M docs | Typo tolerance critical; faceted navigation required; global scaling |

---

## IF-THEN Decision Rules

### Rule 1: Search Latency Critical
```
IF search_latency_required < 50ms
  THEN prefer Typesense OR Meilisearch (in-memory)
  ELSE Elasticsearch acceptable (100-500ms typical)
ENDIF
```

### Rule 2: Cost Sensitive
```
IF budget_monthly < $100
  THEN use self-hosted Meilisearch OR Typesense
  ELSE Algolia or Elasticsearch Cloud acceptable
ENDIF
```

### Rule 3: Operations Team Size
```
IF ops_team_size == 0
  THEN Algolia (managed SaaS)
  ELSE IF ops_team_size < 3
    THEN Meilisearch Cloud or Typesense Cloud
    ELSE self-hosted options viable
  ENDIF
ENDIF
```

### Rule 4: Dataset Size
```
IF documents < 100K
  THEN consider Orama or PostgreSQL
  ELSE IF documents < 10M
    THEN Meilisearch, Typesense, or Elasticsearch
    ELSE Elasticsearch with sharding OR Algolia
  ENDIF
ENDIF
```

### Rule 5: AI/Semantic Search
```
IF requires_semantic_search == true
  THEN IF budget_exists == true
    THEN Algolia (Elevate) or Meilisearch
    ELSE Meilisearch self-hosted with embeddings
  ENDIF
ENDIF
```

### Rule 6: Existing Infrastructure
```
IF already_using_postgresql == true
  AND dataset_size < 50M
  AND typo_tolerance_not_required == true
  THEN pg_trvectorrgm sufficient
  ELSE consider dedicated search solution
ENDIF
```

### Rule 7: Multi-Geography
```
IF users_distributed_globally == true
  THEN prefer Algolia (global CDN) OR Meilisearch with regional deployment
  ELSE single-region solution acceptable
ENDIF
```

### Rule 8: Feature Completeness
```
IF needs_faceting == true
  AND needs_geo_search == true
  AND needs_typo_tolerance == true
  AND budget < $1000/month
  THEN Meilisearch (self-hosted or cloud)
  ELSE IF budget_unlimited
    THEN Algolia
  ENDIF
ENDIF
```

---

## Comparison Matrix: All Solutions

| Attribute | Meilisearch | Typesense | Algolia | Elasticsearch | Orama | PostgreSQL |
|---|---|---|---|---|---|---|
| **Free Tier** | Self-hosted | Self-hosted | Build plan (1M docs, 10K/mo) | AGPL v3 OSS | 150 updates/mo | Yes (included) |
| **Cost (100K docs)** | $30-300 | $7/mo | $0-50 | $99+/mo | Free-$$ | $0 |
| **Latency (p50)** | 10-50ms | <50ms | 100ms+ | 50-200ms | <50ms | 10-100ms |
| **Typo Tolerance** | ✅ Full | ✅ Full | ✅ Advanced | ⚠️ Limited | ✅ Fuzzy | ⚠️ pg_trgm only |
| **Facets** | ✅ | ✅ | ✅ | ✅ Aggs | ✅ | ❌ (manual) |
| **Geo-Search** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ (PostGIS) |
| **Vector/Semantic** | ✅ AI-powered | ✅ Auto-embed | ✅ NeuralSearch (Elevate) | ✅ | ✅ | ❌ (pg_vector) |
| **Self-Hostable** | ✅ | ✅ | ❌ | ✅ | ✅ (OSS) | ✅ |
| **SaaS Available** | ✅ | ✅ | ✅ | ✅ (Elastic Cloud) | ✅ | ❌ (third-party) |
| **Operational Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scalability** | Good | Good | Excellent | Excellent | Limited | Good |
| **Learning Curve** | Easy | Easy | Easy | Steep | Easy | Moderate |
| **SDKs Available** | 8+ | 7+ | 10+ | 8+ | 2 | Any PG client |

---

## Real-World Scenarios

### Scenario 1: E-Commerce Product Search (1M products, global)
**Constraints:** Typo tolerance critical, faceted navigation, fast search

**Recommendation:** **Algolia (Grow/Grow Plus plan)**
- Reasoning: Global distribution via CDN, built-in faceting, advanced typo correction, auto-scaling
- Cost: ~$200-500/month estimated
- Alternative: Meilisearch Cloud (good feature parity, lower cost ~$300/month)

### Scenario 2: Documentation Site Search (5K articles, small budget)
**Constraints:** No ops team, minimal budget, static content

**Recommendation:** **Orama (free or Pro plan)**
- Reasoning: Browser-based search, no backend needed, AI summaries, included analytics
- Cost: Free with cloud option
- Alternative: Self-hosted Meilisearch ($5/mo VPS) if need more docs

### Scenario 3: Log Aggregation + Analytics (100GB logs, internal)
**Constraints:** Complex analytics, must be self-hosted, existing Java stack

**Recommendation:** **Elasticsearch (self-hosted)**
- Reasoning: Purpose-built for logs, time-series data, complex aggregations, Kibana dashboards
- Cost: Infrastructure only (open source)
- Caveat: Requires dedicated ops expertise

### Scenario 4: Small SaaS App Search (500K documents, tight budget)
**Constraints:** Limited operations team, cost-sensitive, need faceting + filters

**Recommendation:** **Meilisearch (self-hosted on $5-10 VPS)**
- Reasoning: Simple deployment, good features, low cost, easy to manage
- Cost: ~$10-20/month infrastructure + minimal ops overhead
- Performance: <50ms latency easily achieved

### Scenario 5: Blog Search + SEO Integration (2K articles, existing PostgreSQL)
**Constraints:** Already use PostgreSQL, simple search needs, no budget

**Recommendation:** **PostgreSQL Full-Text Search (pg_tsvector)**
- Reasoning: Zero additional cost, built-in, tightly integrated with data, sufficient for small corpus
- Trade-off: No facets, limited typo tolerance, no AI features
- When to upgrade: If faceting or typo tolerance becomes critical

### Scenario 6: Mobile App Search (100K documents, low latency critical)
**Constraints:** Sub-50ms latency required, edge network preferred

**Recommendation:** **Typesense Cloud or Orama Cloud**
- Meilisearch: <50ms latency achievable
- Typesense: <50ms guaranteed (in-memory)
- Orama: Edge network provides global <100ms
- Cost: Starting ~$7-50/month

---

## Operational Complexity Ranking

1. **Algolia:** ⭐ Minimal (fully managed SaaS)
2. **Meilisearch Cloud:** ⭐⭐ Very low (hosted, minimal config)
3. **Typesense Cloud:** ⭐⭐ Very low (lightweight, minimal config)
4. **Orama Cloud:** ⭐⭐ Very low (serverless approach)
5. **PostgreSQL Full-Text:** ⭐⭐⭐ Low (no separate service, but SQL tuning needed)
6. **Meilisearch Self-Hosted:** ⭐⭐⭐ Moderate (simple binary, straightforward)
7. **Typesense Self-Hosted:** ⭐⭐⭐ Moderate (lightweight binary, easy setup)
8. **Elasticsearch Self-Hosted:** ⭐⭐⭐⭐⭐ High (cluster management, tuning, sharding)

---

## Cost Projections (Annual)

| Solution | 100K Docs | 1M Docs | 10M Docs |
|---|---|---|---|
| **PostgreSQL** | $0 | $0 | $500 (more hardware) |
| **Meilisearch Self-Hosted** | $60 | $120 | $500 |
| **Typesense Self-Hosted** | $60 | $120 | $500 |
| **Meilisearch Cloud** | $360 | $3,600 | $36,000+ |
| **Typesense Cloud** | $84 | $1,200 | $12,000+ |
| **Algolia Build/Grow** | Free-$600 | $600-$2,400 | $2,400-$10,000+ |
| **Elasticsearch Cloud** | $1,188 | $1,188-$2,376 | $4,752+ |

---

## Migration Paths

### From PostgreSQL → Dedicated Search
- **To Meilisearch:** Extract data to JSON, bulk import via API
- **To Typesense:** Similar process, collection-based indexing
- **Timeline:** 1-2 hours for 1M documents

### From Elasticsearch → Meilisearch
- **Compatibility:** Not compatible; requires reindexing
- **Effort:** Significant (query syntax differs completely)
- **Timeline:** 2-4 weeks depending on complexity

### From Algolia → Self-Hosted
- **Export Data:** Algolia provides export tools
- **Reindex:** Bulk import to Meilisearch or Typesense
- **Risk:** Ensure query logic compatible before cutover

---

## Recommended Next Steps

1. **Identify your dataset size** (documents and average document size)
2. **Determine operation capability** (ops team size, self-hosted vs. SaaS preference)
3. **Define required features** (use feature matrix above)
4. **Calculate TCO** (subscription + infrastructure + operational costs)
5. **Prototype** with top 2-3 solutions (most offer free tiers or trials)
6. **Load test** with realistic query patterns
7. **Plan migration** from existing search solution

---

## Sources & References

- [Meilisearch Pricing](https://www.meilisearch.com/pricing)
- [Meilisearch Self-Hosted Documentation](https://www.meilisearch.com/docs/learn/self_hosted/getting_started_with_self_hosted_meilisearch)
- [Typesense Pricing](https://cloud.typesense.org/pricing)
- [Typesense Comparison](https://typesense.org/docs/overview/comparison-with-alternatives.html)
- [Algolia Pricing](https://www.algolia.com/pricing)
- [Algolia vs Meilisearch Analysis](https://www.meilisearch.com/blog/algolia-pricing)
- [Typesense Pricing Comparison](https://www.meilisearch.com/blog/typesense-pricing)
- [Elasticsearch Pricing](https://www.elastic.co/pricing)
- [Elasticsearch Cloud vs Self-Hosted](https://oneuptime.com/blog/post/2026-01-21-elastic-cloud-vs-self-hosted/view)
- [Orama Cloud Documentation](https://docs.orama.com/cloud/understanding-orama/pricing-limits)
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [PGroonga vs pg_trgm](https://pgroonga.github.io/reference/pgroonga-versus-textsearch-and-pg-trgm.html)
- [Postgres Trigram Performance](https://alexklibisz.com/2022/02/18/optimizing-postgres-trigram-search)
- [Algolia vs Typesense vs Meilisearch](https://medium.com/@sohail_saifii/algolia-vs-typesense-vs-meilisearch-the-search-solution-showdown-287b6d82ba02)
- [Typesense vs Alternatives](https://typesense.org/typesense-vs-algolia-vs-elasticsearch-vs-meilisearch/)
- [Meilisearch vs Typesense](https://www.meilisearch.com/blog/meilisearch-vs-typesense)

---

## Document Metadata

- **Created:** February 19, 2026
- **Technology Cutoff:** February 2025
- **Scope:** 6 major search solutions
- **Version:** 1.0
- **Target Audience:** Full-stack architects, engineering teams, technical decision-makers
- **Update Frequency:** Quarterly (due to rapid pricing/feature changes)

---

**Last Updated:** 2026-02-19 | **Status:** Production-Ready

## Related References
- [NoSQL Databases](./08-databases-nosql.md) — Vector databases for semantic search
- [Caching & Message Queues](./21-caching-queues.md) — Search result caching strategies
- [Performance Benchmarks](./47-performance-benchmarks.md) — Latency comparisons across search solutions
- [Data Pipelines & ETL](./60-data-pipelines-etl.md) — Indexing and search data synchronization
- [Relational Databases](./07-databases-relational.md) — PostgreSQL full-text search baseline

<!-- PRICING_STABILITY: HIGH_VOLATILITY | Updated: 2026-03-03 | Cloud/SaaS pricing changes quarterly. Verify current pricing at provider websites before recommending. -->
