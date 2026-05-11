# SEARCH AT SCALE: BILLION-SCALE SEARCH INFRASTRUCTURE

## A Comprehensive Reference on Distributed Search Architecture and Operations

---

## Table of Contents

1. [Scaling Dimensions](#scaling-dimensions)
2. [Distributed Search Architecture](#distributed-search-architecture)
3. [Sharding Strategies](#sharding-strategies)
4. [Elasticsearch at Scale](#elasticsearch-at-scale)
5. [Google-Scale Search](#google-scale-search)
6. [Vector Search at Scale](#vector-search-at-scale)
7. [Cost Optimization at Scale](#cost-optimization-at-scale)
8. [Operational Patterns](#operational-patterns)
9. [Real-Time Search at Scale](#real-time-search-at-scale)
10. [Case Studies: Enterprise Search Architecture](#case-studies-enterprise-search-architecture)

---

## 1. Scaling Dimensions

### 1.1 Data Volume at Billion Scale

Billion-scale search infrastructure operates with fundamental constraints that define all architectural decisions:

- **Document Count**: Systems handle 1 billion to 100+ billion documents or data points
  - Google Search indexes approximately 100 billion web pages
  - Each document requires storage for content, metadata, and inverted indices
  - Vector databases scale to billions of vectors (e.g., 1 billion = ~4-8 shards optimal sizing)

- **Index Size**: Terabyte to Petabyte scale
  - Raw document storage: hundreds of terabytes to petabytes
  - Inverted index overhead: typically 20-50% of raw data size
  - Replica copies multiply storage requirements
  - Dense vectors add significant storage (each dimension × float32 = 4 bytes)

- **Working Set Considerations**:
  - Hot data must fit in memory for fast access
  - Warm data resides in fast SSD tier
  - Cold data archived to cheaper storage
  - Typical working set: 10-20% of total data active at any time

### 1.2 Query Throughput

Production search systems handle massive concurrent query loads:

- **Query Per Second (QPS) Targets**:
  - Small systems: 1,000-10,000 QPS
  - Medium systems: 10,000-100,000 QPS
  - Large systems (Google scale): 100,000+ QPS
  - Peak traffic spikes can 2-3x baseline load

- **Query Complexity Variations**:
  - Simple keyword queries: <10ms latency
  - Complex boolean queries: 10-100ms latency
  - Aggregations with filtering: 50-500ms latency
  - NLP semantic queries: 100-1000ms latency

- **Concurrency Models**:
  - Typical query concurrency: 100-1000 simultaneous queries per node
  - Connection pooling prevents resource exhaustion
  - Request queuing manages overload conditions

### 1.3 Latency Requirements

Search latency directly impacts user experience and business metrics:

- **Percentile Targets**:
  - p50 (median): 10-100ms for interactive search
  - p95: 100-500ms acceptable for most use cases
  - p99: 500ms-2s for tail latencies
  - p99.9: Should not exceed 5-10s

- **Trade-offs with Accuracy**:
  - Faster results → reduced ranking precision
  - Slower results → more accurate but higher latency
  - Typical balance: 80-90% accuracy at <100ms latency

- **SLA Commitments**:
  - 99.9% of queries complete within 500ms
  - 99.95% availability for search cluster
  - Recovery time objective (RTO): <5 minutes
  - Recovery point objective (RPO): <1 hour

---

## 2. Distributed Search Architecture

### 2.1 Scatter-Gather Pattern

The scatter-gather pattern is the foundational design pattern for distributed search systems. It enables parallel processing across multiple nodes while aggregating results efficiently.

**Pattern Flow**:

```
Client Request
    ↓
Aggregator/Coordinator Node
    ├─→ Scatter to Shard 1 ──→ Local Search
    ├─→ Scatter to Shard 2 ──→ Local Search
    ├─→ Scatter to Shard 3 ──→ Local Search
    └─→ Scatter to Shard N ──→ Local Search
    ↑
    └─ Gather & Merge Results
    ↑
Client Response
```

**Key Characteristics**:

- **Root Controller/Coordinator**: Accepts incoming query request and orchestrates distribution
- **Independent Scatter**: Query broadcasts to all relevant shards simultaneously
- **Parallel Processing**: Each shard performs local search independently
- **Aggregation**: Coordinator merges partial results from all shards
- **Re-ranking**: Results re-ranked by relevance at coordination layer

**Advantages**:

- Latency parallelization: Overall latency = max(shard latencies), not sum
- Fault isolation: Single shard failure doesn't block entire query
- Horizontal scalability: Add shards without architectural changes
- Load distribution: Each shard handles subset of queries

**Challenges**:

- Network overhead: Must contact all shards per query
- Coordination complexity: Must handle partial failures, timeouts
- Memory pressure on coordinator: Must buffer results from all shards
- Skewed latency: Slowest shard determines overall latency (tail latency problem)

### 2.2 Routing Strategies

Effective routing directs queries to optimal shards and minimizes unnecessary scatter operations:

**Complete Scatter**:
- Query sent to all shards regardless of content
- Used when query affects all shards (broad searches)
- Example: keyword appearing in all documents
- Trade-off: Higher latency but complete coverage

**Selective Routing**:
- Query analyzed to identify relevant shards only
- Used with range-based or time-based sharding
- Example: Date range query routes to specific time-period shards
- Benefit: 50-90% reduction in latency by skipping irrelevant shards

**Query Rewriting**:
- Original query transformed based on known shard distribution
- Metadata about shard contents informs routing decisions
- Example: Search for city "New York" → route to geographic shard for region
- Optimization: Pre-computed shard indices track available terms/ranges

**Consistency Hashing**:
- Query parameters mapped to consistent hash → deterministic shard selection
- Enables deterministic routing without central coordination
- Benefits: Reduced latency for personalized/session-based queries
- Used when: Strong affinity between query and specific shard

### 2.3 Replica Strategies

Replicas provide fault tolerance, load distribution, and parallelism opportunities:

**Replication Topology**:

- **Full Replication**: Complete index copied to each node
  - Simplest to implement
  - Maximum query parallelism
  - High storage overhead (N × index size)
  - Used when: Index fits in memory, high redundancy required

- **Partial Replication**: Each shard replicated 1-3 times
  - Typical production setup: 3 replicas for fault tolerance
  - Trades storage for availability
  - Standard in Elasticsearch, Solr

- **No Replication**: Single copy of each shard
  - Minimum storage cost
  - No fault tolerance
  - Used for analytics/non-critical search

**Replica Placement**:

- **Geographic Distribution**: Replicas across data centers
  - Enables regional search with local latency
  - Tolerates entire data center failure
  - Increases write complexity

- **Rack-Aware**: Replicas across different server racks
  - Tolerates power/network failures
  - Reduces cross-rack traffic

- **Availability Zone**: Cloud-native distribution
  - One replica per AZ (usually 3 AZs)
  - Survives zone-level failures

**Query Load Balancing**:

- **Round-Robin**: Distribute queries evenly across replicas
- **Least Loaded**: Route to replica with fewest active queries
- **Latency-Based**: Route to fastest-responding replica
- **Stickiness**: Keep client queries on same replica for cache locality

### 2.4 Data Partitioning Models

How data maps to shards fundamentally affects routing complexity and cluster growth:

**Horizontal vs Vertical Partitioning**:

- **Horizontal**: Split rows (documents), each shard has subset of documents
  - Enables scale beyond single-node capacity
  - Each query must scatter to all shards
  - Standard approach for search

- **Vertical**: Split columns (fields), each shard stores different fields
  - Reduces I/O per query
  - Requires coordination across shards for result reconstruction
  - Less common in search systems

---

## 3. Sharding Strategies

Sharding decisions are critical because they affect query routing complexity, data skew, and cluster evolution.

### 3.1 Hash-Based Sharding

Documents distributed via hash function of key field.

**Mechanism**:
```
shard_id = hash(document_id) % num_shards
```

**Characteristics**:

- **Even Distribution**: Hash functions distribute documents evenly
- **Deterministic**: Same document always maps to same shard
- **Stateless Routing**: No cluster metadata needed for routing
- **Rebalancing Cost**: Adding shards requires rehashing all documents

**Advantages**:

- Simple to implement and understand
- Handles skewed data well through randomization
- Efficient for lookup-based queries

**Disadvantages**:

- Impossible to do range queries efficiently (requires scatter)
- Rebalancing requires touching every document
- Hot spots emerge if key distribution is non-uniform
- Difficult to implement locality (geographically)

**Use Cases**:

- User-based sharding (user_id → shard)
- Document ID-based sharding when ID is stable
- Cache-like systems where retrieval pattern is lookup-based

### 3.2 Range-Based Sharding

Documents distributed by value ranges of shard key.

**Mechanism**:
```
if key < 1000: shard 0
if 1000 <= key < 5000: shard 1
if 5000 <= key < 10000: shard 2
```

**Characteristics**:

- **Logical Ordering**: Keys within logical ranges
- **Efficient Range Queries**: Range scans hit single or adjacent shards
- **Manual Rebalancing**: Must manually adjust boundaries
- **Hot Spot Risk**: Ranges may become imbalanced

**Advantages**:

- Efficient for range queries
- Enables selective routing based on ranges
- Natural fit for time-series data
- Easier to understand shard contents

**Disadvantages**:

- Requires careful boundary tuning
- Rebalancing requires moving documents between shards
- Risk of hot spots (e.g., recent timestamps get more writes)
- Difficult with skewed distributions

**Use Cases**:

- Time-series data (logs, metrics) → shards by timestamp ranges
- Geographic data (zip codes) → shards by region ranges
- User tiers (free/premium) → shards by ID ranges
- Numeric ranges (prices, scores)

### 3.3 Time-Based Sharding (Temporal)

Special case of range sharding optimized for time-series data.

**Shard Per Time Period**:

```
logs-2025-03-01/primary/
logs-2025-03-02/primary/
logs-2025-03-03/primary/
...
```

**Characteristics**:

- **Rolling Window**: Old indices deleted after retention period
- **Predictable Shard Lifecycle**: New shard created daily/hourly
- **Write Locality**: All writes go to current shard
- **Query Routing**: Date filters enable selective shard access

**Advantages**:

- Perfect for append-only data (logs, events, metrics)
- Simple lifecycle management (delete old indices)
- High write throughput (concentrated on current index)
- Easy capacity planning (predictable growth)
- Clean separation between hot/warm/cold tiers

**Disadvantages**:

- Many small indices increase overhead
- Cross-time queries require multiple scatter operations
- Empty indices still consume resources
- Requires active lifecycle management

**ILM (Index Lifecycle Management)**:

- **Hot Phase**: Current/recent indices on fast hardware, high refresh
- **Warm Phase**: Older indices on cost-effective hardware, reduced refresh
- **Cold Phase**: Archive indices, rare queries acceptable
- **Frozen Phase**: Searchable snapshots for compliance
- **Delete Phase**: Remove indices beyond retention

### 3.4 Routing-Based Sharding

Explicit mapping of attributes to shards via application logic.

**Mechanism**:
```
shard_map = {
  'user_region:us-east': [shard_0, shard_1],
  'user_region:eu-west': [shard_2, shard_3],
  'user_region:asia-pacific': [shard_4, shard_5],
}
query_shard = shard_map[user_region]
```

**Characteristics**:

- **Application-Level Logic**: Sharding decisions in app code
- **Flexible Routing**: Can encode complex business logic
- **Minimal Scatter**: Route to minimal shards needed
- **Requires Coordination**: Central shard map must be maintained

**Advantages**:

- Can optimize for specific business requirements
- Enables geographic/tenant-based isolation
- Minimal shard scatter for targeted queries
- Can co-locate related data

**Disadvantages**:

- Couples application to shard topology
- Difficult to rebalance without app changes
- Requires coordination to update routing
- Potential for uneven distribution

**Use Cases**:

- Multi-tenant systems (tenant → specific shards)
- Geographic distribution (region → regional shards)
- Customer segmentation (customer_tier → shard tier)
- Feature flags controlling routing

### 3.5 Shard Sizing and Capacity

Target shard size is critical to cluster performance:

**Elasticsearch Guidance**:

- **Target Range**: 40-50GB per shard for typical workloads
- **Upper Bound**: Rarely exceed 50-65GB per shard
- **Lower Bound**: Minimum ~1GB (too many shards overhead)
- **Special Cases**: Vector search may be 10-20GB due to larger memory footprint

**Rationale**:

- **Memory for Caching**: Shard fits in available memory
- **Recovery Time**: <10 minutes to recover shard from replica
- **Query Performance**: Working set fits in OS page cache
- **Operational Overhead**: Not too many shards to manage

**Calculation**:

```
number_of_shards = ceil(total_data_size / target_shard_size)
                 = ceil(5TB / 50GB)
                 = ceil(100)
                 = 100 shards
```

**Over-Sharding Problems**:

- **Memory Overhead**: Each shard maintains segment metadata
- **CPU Overhead**: More shards = more coordination
- **Merge Pressure**: More small segments to manage
- **Query Latency**: More shards to scatter/gather
- **Network Overhead**: More remote calls

**Recommended Approach**:

```
Initial shards = total_data_size / 50GB
Monitor actual performance and adjust based on:
- Query latency (aim for p95 < 100ms)
- CPU utilization (aim for <70% at peak)
- Memory utilization (aim for 60-75% heap)
- Recovery time (should be <10 minutes)
```

---

## 4. Elasticsearch at Scale

Elasticsearch is the de facto standard for distributed search at scale, with proven production deployments handling petabytes of data.

### 4.1 Cluster Topology

Production Elasticsearch clusters separate node roles for optimal performance and stability:

**Node Types and Responsibilities**:

**Master Nodes**:
- Responsibilities: Cluster state management, shard allocation, failover decisions
- Count: Minimum 3 (odd number prevents split-brain)
- CPU: Medium (coordination overhead)
- Memory: 2-4GB sufficient (not querying)
- Storage: None (cluster metadata only)
- Isolation: Dedicated master nodes separate from data nodes

**Data Nodes**:
- Responsibilities: Store index shards, execute queries, aggregations
- Count: Scale horizontally with data volume
- CPU: High (query execution, aggregations)
- Memory: 8-64GB (larger = more cache, fewer nodes needed)
- Storage: Proportional to data (SSD for hot, HDD for warm/cold)
- Tuning: JVM heap = min(31GB, RAM/2)

**Coordinating Nodes**:
- Responsibilities: Query routing, result aggregation, client-facing
- Count: 2-4 for high-throughput scenarios
- CPU: High (scatter-gather coordination)
- Memory: 4-8GB
- Storage: None (routing layer)
- Use Case: Separates query routing from indexing burden

**Ingest Nodes**:
- Responsibilities: Document enrichment, pipeline execution before indexing
- Count: 1-3 (rarely bottleneck)
- CPU: Medium (data transformation)
- Memory: 4-8GB
- Storage: None (stateless)
- Use Case: Offloads data transformation from client applications

**Machine Learning Nodes** (Optional):
- Responsibilities: Anomaly detection, forecasting
- Count: 1-2
- CPU: Very high
- Memory: 8-16GB
- Storage: Model metadata

**Recommended Production Topology**:

```
3 dedicated Master Nodes (small, 2CPU, 4GB RAM)
├─ Manage cluster state
├─ Elect leader
└─ Handle failover

N Data Nodes (large, 8-16CPU, 32-64GB RAM)
├─ Store shards
├─ Execute queries
└─ Scale linearly with data

2-4 Coordinating Nodes (medium, 4-8CPU, 8GB RAM)
├─ Front-facing API
├─ Route queries
└─ Aggregate results

1-2 Ingest Nodes (small, 2CPU, 4GB RAM)
└─ Enrich documents
```

### 4.2 Index Lifecycle Management (ILM)

ILM automates the management of indices through their lifecycle, enabling efficient storage and cost optimization.

**ILM Phases**:

```
Index Created
    ↓
┌───────────────────────────────────────────────────┐
│ HOT PHASE (days 0-1)                              │
│ - Stored on high-performance hardware (NVMe SSD)  │
│ - High index refresh rate (1s)                    │
│ - Full replicas (3+)                              │
│ - All reads and writes                            │
└────────────────────────┬────────────────────────────┘
                         ↓
              [Rollover: size > 50GB or age > 1 day]
                         ↓
┌───────────────────────────────────────────────────┐
│ WARM PHASE (days 1-30)                            │
│ - Stored on cost-effective hardware (SATA SSD)    │
│ - Reduced refresh rate (30s)                      │
│ - Force merge to single segment                   │
│ - Occasional queries                              │
└────────────────────────┬────────────────────────────┘
                         ↓
              [Age > 30 days]
                         ↓
┌───────────────────────────────────────────────────┐
│ COLD PHASE (days 30-365)                          │
│ - Stored on archive hardware (HDD)                │
│ - Searchable but slower                           │
│ - Read replicas only                              │
│ - Rare queries                                    │
└────────────────────────┬────────────────────────────┘
                         ↓
              [Age > 365 days or manual trigger]
                         ↓
┌───────────────────────────────────────────────────┐
│ FROZEN PHASE (optional, for compliance)           │
│ - Searchable snapshots only                       │
│ - Retrieved from object storage                   │
│ - Extremely slow but archived                     │
└────────────────────────┬────────────────────────────┘
                         ↓
              [Delete or archive]
                         ↓
          [Index Deleted, Snapshot Remains]
```

**ILM Actions by Phase**:

| Action | Hot | Warm | Cold | Delete |
|--------|-----|------|------|--------|
| Set Priority | ✓ | ✓ | ✓ | |
| Rollover | ✓ | | | |
| Allocate | | ✓ | ✓ | |
| Force Merge | | ✓ | | |
| Delete | | | | ✓ |
| Searchable Snapshot | | | ✓ | |

**Example ILM Policy**:

```json
{
  "policy": "logs-lifecycle",
  "phases": {
    "hot": {
      "min_age": "0ms",
      "actions": {
        "rollover": {
          "max_primary_shard_size": "50gb",
          "max_age": "1d"
        },
        "set_priority": {
          "priority": 100
        }
      }
    },
    "warm": {
      "min_age": "1d",
      "actions": {
        "allocate": {
          "include": { "data": "warm" }
        },
        "set_priority": {
          "priority": 50
        },
        "force_merge": {
          "max_num_segments": 1
        }
      }
    },
    "cold": {
      "min_age": "30d",
      "actions": {
        "allocate": {
          "include": { "data": "cold" }
        },
        "set_priority": {
          "priority": 0
        }
      }
    },
    "delete": {
      "min_age": "365d",
      "actions": {
        "delete": {}
      }
    }
  }
}
```

### 4.3 Cross-Cluster Search (CCS)

Cross-cluster search enables federated queries across geographically distributed clusters or logical partitions.

**Architecture**:

```
Primary Cluster (Main Index)
├─ Cluster 1 (Region US-East)
├─ Cluster 2 (Region EU-West)
└─ Cluster 3 (Region Asia-Pacific)

Query Coordinator
│
├─→ Remote Cluster 1 (via CCS) ──→ Results
├─→ Remote Cluster 2 (via CCS) ──→ Results
└─→ Remote Cluster 3 (via CCS) ──→ Results
│
└─→ Merged Results to Client
```

**Cluster Link Configuration**:

```json
{
  "persistent": {
    "cluster": {
      "remote": {
        "cluster_us_east": {
          "seeds": ["10.0.1.100:9300"]
        },
        "cluster_eu_west": {
          "seeds": ["10.1.1.100:9300"]
        }
      }
    }
  }
}
```

**Cross-Cluster Query**:

```
GET cluster_us_east:logs-*,cluster_eu_west:logs-*/_search
{
  "query": {
    "match": { "message": "error" }
  }
}
```

**Key Features**:

- **Skip Unavailable**: `skip_unavailable: true` → continues if cluster unreachable
- **Minimize Roundtrips**: Batch shard fetching to reduce latency for distant clusters
- **Minimize Shards**: Query individual indices rather than wildcards
- **Failover**: Queries continue even if cluster becomes unavailable

**Use Cases**:

- Multi-region search (geographic distribution)
- Tenant isolation (per-tenant clusters)
- Index versioning (old/new indices in separate clusters)
- Federated search across organizational units

### 4.4 Scaling Considerations

Practical guidance for scaling Elasticsearch to handle massive workloads:

**Read-Heavy Clusters** (search-dominant):

- Increase data node count for query parallelism
- Allocate 50% more resources than write-heavy
- Use coordinating nodes to isolate query routing
- Implement result caching at application layer
- Consider read replicas per shard (3-5 copies)

**Write-Heavy Clusters** (indexing-dominant):

- Tune bulk indexing parameters
- Increase refresh interval (default 1s → 30-60s)
- Use async indexing where acceptable
- Avoid aggressive force merges during indexing
- Monitor segment merge queue

**Mixed Workloads**:

- Separate hot and warm nodes
- Isolate search from indexing operations
- Use different ILM policies based on time of day
- Implement query queuing and prioritization
- Monitor and rebalance load dynamically

**Growth Path**:

```
Phase 1: Single Node
└─ 512GB storage, 32GB heap
└─ ~100M documents

Phase 2: 3-Node Cluster
├─ 3 × 1TB storage, 8GB heap
├─ 1 shared master node, 2 data nodes
└─ ~1B documents

Phase 3: Production Cluster
├─ 3 dedicated master nodes
├─ 10-20 data nodes (as needed)
├─ 2-4 coordinating nodes
├─ Cross-cluster replication to standby
└─ 10-100B documents

Phase 4: Multi-Cluster Federation
├─ 3-5 regional clusters
├─ Cross-cluster search
├─ Geo-redundancy
└─ 100B+ documents
```

---

## 5. Google-Scale Search

Google's search infrastructure is the canonical example of billion-scale search, handling 100+ billion documents and 100,000+ queries per second.

### 5.1 PageRank Algorithm

PageRank is the foundational ranking algorithm that assigns importance scores to web pages based on link structure.

**Core Concept**:

```
PageRank(A) = (1-d)/N + d * (PageRank(T1)/C(T1) + ... + PageRank(Tn)/C(Tn))

Where:
- d = damping factor (typically 0.85)
- N = total number of pages
- T1...Tn = pages linking to A
- C(Ti) = outbound link count of page Ti
```

**Iterative Computation**:

```
Initial: PR(page) = 1/N for all pages

Iteration 1:
  For each page P:
    PR'(P) = (1-d)/N + d * sum(PR(T)/C(T) for T linking to P)

Iteration 2:
  Repeat computation with PR' values

Continue until convergence (typically 10-20 iterations)
```

**Key Insights**:

- **Link Quality**: Pages with fewer outbound links transfer more PageRank
- **Rank Propagation**: High-ranking pages boost their linked pages
- **Damping Factor**: Prevents rank concentration and models random navigation
- **Converges**: Iterative algorithm reaches stable state

### 5.2 MapReduce for Indexing

Google uses MapReduce to parallelize the massive computations required for web-scale indexing.

**MapReduce Programming Model**:

```
1. Input: Large dataset split across many machines
2. Map Phase:
   - Distribute data to map workers
   - Each worker processes local data partition
   - Output: (key, value) pairs
3. Shuffle & Sort:
   - Framework groups all values by key
   - Sorts pairs by key
4. Reduce Phase:
   - Distribute (key, [values]) to reduce workers
   - Each worker aggregates values for a key
   - Output: Final results
```

**PageRank Computation with MapReduce**:

```
Map Phase:
  For each page P with links [L1, L2, ..., Ln]:
    rank_delta = PR(P) / n
    Output: (L1, rank_delta), (L2, rank_delta), ..., (Ln, rank_delta)
    Also output: (P, [link_list])

Reduce Phase:
  For each page P with delta values [d1, d2, ..., dk]:
    PR'(P) = (1-d)/N + d * sum(d1 + d2 + ... + dk)
    Output: (P, PR'(P))
```

**Indexing with MapReduce**:

```
Map Phase:
  For each document D:
    Extract words [w1, w2, ..., wm]
    Output: (w1, D), (w2, D), ..., (wm, D)

Reduce Phase:
  For word W with documents [D1, D2, ..., Dk]:
    Output: (W, [D1, D2, ..., Dk])  -- Inverted index entry
```

**Advantages at Scale**:

- **Fault Tolerance**: Failed workers re-executed on different machines
- **Scalability**: Linear scaling across hundreds/thousands of machines
- **Simplicity**: Developers write map/reduce functions, framework handles distribution
- **Proven**: Used for Google's primary web indexing

**Limitations**:

- **High Latency**: Batch processing takes hours/days
- **I/O Intensive**: Reads entire dataset each pass
- **Not Real-Time**: Results available after batch completes

### 5.3 Bigtable for Serving

Bigtable is Google's distributed storage system that holds indexed data for query serving.

**Bigtable Architecture**:

```
Client Request
    ↓
Bigtable API Library
    ↓
Master Server (metadata, shard management)
├─→ Tablet Server 1 (range of keys)
├─→ Tablet Server 2 (range of keys)
└─→ Tablet Server N (range of keys)
    ↓
HDD Storage (GFS or Colossus)
```

**Key Characteristics**:

- **Sorted Map**: Stores (row, column, timestamp) → value
- **Tablets**: Key range partitions served by tablet servers
- **Column Families**: Related columns grouped for storage efficiency
- **Timestamps**: Version management for updates

**Data Model Example**:

```
Row Key: "google.com/web/news"
Columns:
  - content:html = "<html>...</html>"
  - content:text = "Google News..."
  - links:out = ["bbc.com", "cnn.com"]
  - metadata:updated = 1646092800
  - metadata:size = 45678
```

**Distributed Query Processing**:

```
Query: "Find all pages with keyword 'algorithm'"
    ↓
Tablet Server 1: scan rows a-f → matching pages
Tablet Server 2: scan rows g-n → matching pages
Tablet Server 3: scan rows o-z → matching pages
    ↓
Merge results → rank by PageRank → return top-K
```

**Scaling Properties**:

- **Automatic Sharding**: New tablets created as data grows
- **Load Balancing**: Moved hot tablets to less loaded servers
- **Replication**: 3 copies for fault tolerance
- **Compression**: Achieves 10:1 ratio on real data

### 5.4 Caffeine: Real-Time Indexing

Caffeine is Google's real-time indexing system that enables fresh results within seconds of content publication.

**Architecture**:

```
Web Crawler → Frontier Queue
                    ↓
              Fetch Service
                    ↓
        Parse & Extract (NLP, links, text)
                    ↓
          Caffeine Indexing Pipeline
                    ↓
          Content Update Service
                    ↓
        Index Servers (query-serving tier)
                    ↓
          Query Results (fresh content)
```

**Key Innovation**:

- **Continuous Crawling**: Not batch-based, continuous updates
- **Incremental Indexing**: Update only changed content
- **Fast Propagation**: Changes visible in search within seconds
- **Scalable**: Handles millions of updates per second

**Comparison with Traditional Batch Indexing**:

| Aspect | Batch (MapReduce) | Continuous (Caffeine) |
|--------|-------------------|----------------------|
| Latency | Hours to days | Seconds |
| Coverage | 100% | Near-100% |
| Complexity | Simple | Very complex |
| Cost | Lower (batch efficiency) | Higher (continuous resources) |
| Timeliness | Stale results | Fresh results |

---

## 6. Vector Search at Scale

Vector/semantic search introduces new challenges for billion-scale systems: storage, quantization, and approximate nearest neighbor efficiency.

### 6.1 FAISS: Facebook AI Similarity Search

FAISS is Meta's library for large-scale similarity search and clustering of dense vectors.

**Capabilities**:

- **Exact and Approximate**: Supports both for different accuracy/speed trade-offs
- **GPU Acceleration**: CUDA support for 10-100x speedup
- **Billions of Vectors**: Scales to billion-scale on single machine
- **Multiple Indexing Methods**: Different algorithms for different trade-offs

**Common Index Types**:

**Flat (Exact)**:
```
Index: Linear scan of all vectors
Search: L2 distance to all vectors
Latency: O(n)
Best for: <1M vectors where accuracy critical
```

**IVF (Inverted File)**:
```
Index: k-means clustering, vectors assigned to nearest centroid
Search: Search only nearby clusters (not all vectors)
Latency: O(k·m) where k=clusters, m=vectors per cluster
Speedup: 10-100x for 10k-100k clusters
```

**HNSW (Hierarchical Navigable Small World)**:
```
Index: Graph-based, multiple layers form small-world network
Search: Navigate hierarchy to nearest neighbors
Latency: O(log N) for N vectors
Memory: ~2x vector data size
Best for: Billion+ vectors where speed critical
```

**Product Quantization (PQ)**:

Reduces vector dimension/storage through lossy compression:

```
Original vector: 768 dimensions × 4 bytes = 3072 bytes
PQ(m=96, d=8):
  - Split into 96 chunks (8 dims each)
  - Quantize each chunk to 1 byte
  - Result: 96 bytes (32x reduction!)
  - Recall: ~95% with proper parameters
```

**FAISS at Scale**:

```python
# 1 billion vector index
import faiss

# Create index
d = 768  # dimension
index = faiss.IndexIVFPQ(
    faiss.IndexFlatL2(d),
    d,
    100000,  # 100k clusters
    96,      # 96 bytes per vector (PQ)
    8        # 8-bit subquantizer
)

# Add vectors
index.add(billion_vectors)

# Search
distances, indices = index.search(queries, k=10)
```

**Performance Characteristics**:

- **Memory**: ~96 bytes × 1B = ~96GB (vs 3TB uncompressed)
- **Latency**: ~5-20ms for k=10 on billion vectors
- **Throughput**: 1000s QPS per GPU
- **Accuracy**: 95%+ recall@10

### 6.2 ScaNN: Google's Scalable Nearest Neighbors

ScaNN is Google's solution for billion-scale approximate nearest neighbor search.

**Key Innovations**:

- **Anisotropic Vector Quantization**: Optimizes quantization for each query
- **Learned Index Structures**: Neural networks guide search
- **TensorFlow Integration**: Native ML framework integration

**Architecture**:

```
Training Phase:
  Vectors → Partition (k-means) → Per-partition quantizer
  Build: Index structure with learned routing

Serving Phase:
  Query → Route to nearest partitions
       → Quantized search within partitions
       → Dequantize top candidates
       → Return exact nearest neighbors
```

**Comparison with FAISS**:

| Aspect | FAISS | ScaNN |
|--------|-------|-------|
| Maturity | Mature, Meta production | Newer, Google production |
| Ease | Easy to use | More complex |
| GPU Support | Excellent | TensorFlow GPU |
| Accuracy | 90-95% | 95%+ |
| Latency | 5-20ms | 2-10ms |
| Memory | ~96B/vector | ~100B/vector |

**Use Cases**:

- **FAISS**: General-purpose similarity search, clustering
- **ScaNN**: High-QPS latency-critical semantic search

### 6.3 DiskANN: Disk-Based Approximate Nearest Neighbor

DiskANN enables billion-scale vector search on a single machine with disk storage, not requiring GPUs.

**Problem Solved**:

```
Existing Methods:
- DRAM-based: Scale to 100-200M vectors
- GPU-based: Expensive, requires specialized hardware
- Distributed: Complex coordination

DiskANN:
- Disk-based: Scale to billions on single machine
- SSD cost-effective: ~$0.10/GB
- Simple: Single machine, no coordination
```

**Architecture**:

```
Building Phase:
  Vectors → Build HNSW graph on disk
          → Optimize for SSD access patterns
          → Cache-friendly traversal

Searching Phase:
  Query → HNSW traversal (disk-backed)
       → Prefetch likely next candidates
       → Async I/O to hide latency
       → Return top-K nearest neighbors
```

**Performance on SIFT-1B**:

```
Hardware: Single workstation
  - CPU: 16-core
  - RAM: 64GB
  - SSD: 1TB

Results:
  - Index size: ~120GB (all 1B vectors)
  - Memory: 4GB (leaf data cache)
  - Latency: ~3-5ms (p50)
  - QPS: 5000+ (single machine!)
  - Recall@1: 95%+
```

**Trade-offs**:

```
vs FAISS + GPU:
  + Much cheaper (single machine vs GPU cluster)
  + No need for distributed system
  - Slower latency (3-5ms vs 1-2ms)
  - Disk I/O limits QPS

vs FAISS + Sharding:
  + Simpler (single machine)
  + Cheaper (no distributed coordination)
  - Slightly higher latency
  + Lower operational complexity
```

**Use Cases**:

- **Semantic Search**: Large document corpus
- **Recommendation**: Billions of items to recommend
- **Image Search**: Billion-scale image embeddings
- **Cost-Sensitive**: Need scale without expensive infrastructure

### 6.4 Vector Quantization Techniques

Quantization reduces storage and latency for vector search at the cost of accuracy.

**Product Quantization (PQ)**:

```
Original: 768-dim vector = 3072 bytes
Split: 8 segments of 96 dims each
Quantize: Each segment to 1 byte (256 centroids)
Result: 8 bytes total (384x reduction!)

Trade-off: 95%+ recall with 384x compression
```

**Scalar Quantization (SQ)**:

```
Original: 768-dim float32 vector = 3072 bytes
Quantize: Each dimension to 8-bit int = 768 bytes
Dequantize: For final refinement = 3072 bytes

Trade-off: 4x compression, 98%+ recall
Advantage: Simple, fast
```

**Binary Quantization**:

```
Original: 768-dim float32 = 3072 bytes
Binarize: Each dimension → 1 bit (sign)
Result: 96 bytes (32x compression!)
Hamming Distance: Ultra-fast comparison

Trade-off: ~85% recall, extreme speed
Use: Re-ranking stage, where approximate is acceptable
```

**Quantization Trade-offs**:

| Method | Compression | Recall | Speed |
|--------|-------------|--------|-------|
| None | 1x | 100% | 1x |
| SQ8 | 4x | 98%+ | 2x |
| PQ | 32x | 95%+ | 5x |
| Binary | 32x | 85%+ | 50x |

**Multi-Stage Ranking**:

```
Query Vector
    ↓
Stage 1: Binary Quantization
  → Fast 50M candidates
    ↓
Stage 2: Product Quantization
  → Medium 1M candidates
    ↓
Stage 3: Exact Similarity
  → Accurate 100 results
```

---

## 7. Cost Optimization at Scale

Billion-scale search infrastructure is expensive. Careful optimization can reduce TCO by 50-70%.

### 7.1 Storage Tiering Architecture

Hot-warm-cold tiering moves data between storage tiers based on access patterns.

**Storage Tiers**:

```
┌──────────────────────────────────────────┐
│ HOT TIER (Days 0-1)                      │
│ Hardware: NVMe SSD                       │
│ Cost: $10-15/GB/month                    │
│ Capacity: 10-50TB per node               │
│ Use: Recent/frequently accessed data     │
└──────────────────────────────────────────┘
         5-10% of total data

┌──────────────────────────────────────────┐
│ WARM TIER (Days 1-30)                    │
│ Hardware: SATA SSD                       │
│ Cost: $5-8/GB/month                      │
│ Capacity: 50-200TB per node              │
│ Use: Older but still queryable           │
└──────────────────────────────────────────┘
         20-30% of total data

┌──────────────────────────────────────────┐
│ COLD TIER (Days 30-365)                  │
│ Hardware: HDD                            │
│ Cost: $1-2/GB/month                      │
│ Capacity: 500TB-2PB per node             │
│ Use: Rarely accessed archive             │
└──────────────────────────────────────────┘
         60-70% of total data

┌──────────────────────────────────────────┐
│ FROZEN TIER (365+)                       │
│ Hardware: Cloud object storage           │
│ Cost: $0.02-0.05/GB/month                │
│ Access: Via searchable snapshots         │
│ Use: Compliance/legal hold               │
└──────────────────────────────────────────┘
         Varies by compliance needs
```

**Example: 100TB Cluster**

```
Data Distribution:
  Hot:   5TB × $12 = $60/month
  Warm:  25TB × $6 = $150/month
  Cold:  70TB × $1.50 = $105/month
  ─────────────────────────────────
  Total: $315/month

Without Tiering (all hot):
  100TB × $12 = $1200/month

Savings: 73%!
```

### 7.2 Compression Techniques

Data compression reduces storage footprint and network I/O.

**Compression Methods**:

**ZSTD (Zstandard)**:
```
Compression ratio: 2-3x (typical)
Speed: 300-500 MB/s compress, 1-2 GB/s decompress
Best for: General document storage
Tradeoff: Good compression + acceptable speed
```

**LZ4**:
```
Compression ratio: 1.5-2x
Speed: 1+ GB/s compress, 3+ GB/s decompress
Best for: High-throughput scenarios
Tradeoff: Speed over compression ratio
```

**Dictionary Compression**:
```
Learn common patterns in data
Compression ratio: 3-5x for structured data
Example: Common HTML tags, JSON fields
```

**Columnar Compression**:
```
Store columns separately instead of rows
Compression ratio: 5-10x for analytics
Works because: Repeated values in columns
Example: Parquet, ORC formats
```

**Elasticsearch Built-In**:

```
Index-level compression:
  codec: best_compression  (DEFLATE, ~20% overhead)
  codec: default           (LZ4, ~5% overhead)

Example ILM policy:
{
  "warm": {
    "actions": {
      "forcemerge": {"max_num_segments": 1},
      "set_settings": {
        "index.codec": "best_compression"
      }
    }
  }
}
```

**Compression Effectiveness**:

```
Raw Logs: 100GB
  Compressed (LZ4): 50GB (-50%)
  Compressed (ZSTD): 35GB (-65%)
  Compressed (Dictionary): 25GB (-75%)

Monthly Cost Reduction:
  Savings: 75GB × 100 nodes × $0.10/GB = $750/month
```

### 7.3 Data Lifecycle Management

Automated lifecycle policies reduce storage costs without manual intervention.

**Lifecycle Strategy**:

```
Day 0:   New data, write-heavy
         ├─ Stored on hot tier (NVMe)
         ├─ Full replicas (3)
         └─ Refresh every 1 second

Day 1:   Rolling window updated
         ├─ Move to warm tier (SSD)
         ├─ Force merge (reduce segments)
         └─ Reduce replicas to 2

Day 30:  Older data, query-rare
         ├─ Move to cold tier (HDD)
         ├─ Reduce refresh to never
         └─ Reduce replicas to 1

Day 365: Retention limit reached
         ├─ Snapshot to object storage
         ├─ Delete from cluster
         └─ Searchable via CCS if needed
```

**Automated ILM Policy**:

```json
{
  "policy": "cost-optimized-logs",
  "phases": {
    "hot": {
      "min_age": "0ms",
      "actions": {
        "rollover": {
          "max_primary_shard_size": "50gb",
          "max_age": "1d"
        },
        "set_priority": {"priority": 100}
      }
    },
    "warm": {
      "min_age": "1d",
      "actions": {
        "set_settings": {
          "index.number_of_replicas": 1,
          "index.refresh_interval": "30s"
        },
        "allocate": {
          "include": {"data": "warm"}
        },
        "force_merge": {
          "max_num_segments": 1
        },
        "set_settings": {
          "index.codec": "best_compression"
        }
      }
    },
    "cold": {
      "min_age": "30d",
      "actions": {
        "allocate": {
          "include": {"data": "cold"}
        },
        "set_settings": {
          "index.number_of_replicas": 0,
          "index.refresh_interval": "-1"
        }
      }
    },
    "delete": {
      "min_age": "365d",
      "actions": {
        "delete": {}
      }
    }
  }
}
```

### 7.4 Infrastructure Optimization

Hardware and cloud architecture choices significantly impact cost.

**Instance Type Selection**:

```
Data Nodes (Storage-optimized):
  AWS: i3en.3xlarge (24 cores, 96GB RAM, 7.5TB SSD)
  GCP: n2-highmem-32 (32 cores, 128GB RAM)
  Cost: ~$3-4/hour

Warm Nodes (General-purpose):
  AWS: m5.2xlarge (8 cores, 32GB RAM)
  Cost: ~$0.4/hour

Cold Nodes (Storage-optimized):
  AWS: d2.8xlarge (36 cores, 244GB RAM, 336TB HDD)
  Cost: ~$0.7/hour
```

**Reserved Capacity**:

```
On-Demand: $730/month per node (i3en.3xlarge)
1-Year Reserved: $410/month per node (-44%)
3-Year Reserved: $280/month per node (-62%)

For 100-node cluster:
  On-Demand: $73,000/month
  3-Year Reserved: $28,000/month
  Annual Savings: $540,000
```

**Spot Instances**:

```
Warm/Cold tiers: Use spot instances (50-70% discount)
Hot tier: Reserved/on-demand (uptime critical)
Risk: Spot interruption acceptable for non-critical data

Example:
  Warm nodes on spot: $0.12-0.15/hour (vs $0.4 on-demand)
  50-node warm cluster savings: $8,000+/month
```

**Serverless Search Options**:

```
Elasticsearch Serverless (Elastic Cloud):
  - Auto-scaling based on demand
  - Pay only for compute/storage used
  - No cluster management
  - Cost: $0.3-0.5 per GB-month (vs $1-3 self-managed)

Use Case: Unpredictable workloads, cost-sensitive

Trade-offs:
  + Lower cost for low utilization
  + No operational overhead
  - Higher per-GB for predictable high volume
  - Less customization
```

---

## 8. Operational Patterns

Operating billion-scale search systems requires sophisticated deployment, monitoring, and recovery strategies.

### 8.1 Blue-Green Deployments

Blue-green deployment enables zero-downtime updates and quick rollback capability.

**Architecture**:

```
                          Load Balancer
                                 |
                    ┌────────────┼────────────┐
                    ↓                         ↓
            ┌──────────────┐         ┌──────────────┐
            │    BLUE      │         │    GREEN     │
            │   (Active)   │         │   (Standby)  │
            ├──────────────┤         ├──────────────┤
            │ Version 1.2  │         │ Version 1.3  │
            │ 100% Traffic │         │ 0% Traffic   │
            │ 50 Nodes     │         │ 50 Nodes     │
            └──────────────┘         └──────────────┘
```

**Deployment Flow**:

```
1. Deploy to Green cluster (new version)
   ├─ Health checks
   ├─ Smoke tests
   └─ Index warming (pre-load hot data)

2. Verify Green is ready
   ├─ Replication lag < 1 second
   ├─ Query latency acceptable
   └─ Index sync complete

3. Switch traffic
   ├─ Load balancer → Green (100% traffic)
   └─ Blue → standby

4. Verify
   ├─ Monitor error rates
   ├─ Watch latency
   └─ Quick rollback if needed

5. After success
   ├─ Deprecate Blue
   ├─ Deploy next version to Blue
   └─ Swap for next release
```

**Advantages**:

- **Zero Downtime**: Traffic switches instantly
- **Quick Rollback**: Revert to Blue within seconds
- **Testing**: Fully test Green before switch
- **Clean Cutover**: No gradual rollout complexity

**Disadvantages**:

- **Infrastructure Cost**: Need 2 production clusters
- **Sync Complexity**: Keep Blue/Green in sync
- **Large Deployments**: Slow for hundred-node clusters

### 8.2 Canary Releases

Canary releases reduce risk by gradually shifting traffic to new versions.

**Canary Traffic Ramp**:

```
Time    Version 1.2         Version 1.3       Status
────────────────────────────────────────────────────
t=0     100%                0%                Deploy starts
t=5m    95%                 5%                Monitor metrics
t=15m   90%                 10%               Check error rates
t=30m   80%                 20%               Proceed?
t=60m   50%                 50%               Full parity
t=90m   20%                 80%               Performance OK?
t=120m  5%                  95%               Near complete
t=150m  0%                  100%              Fully migrated
```

**Metrics Monitored**:

```
- Error rate: Should stay < baseline + 0.5%
- Latency p95: Should stay < baseline + 20%
- Latency p99: Should stay < baseline + 50%
- CPU utilization: Should stay < baseline + 10%
- Memory utilization: Should stay < baseline + 10%
```

**Automatic Rollback**:

```
If any metric violates threshold:
  ├─ Trigger rollback
  ├─ Immediately shift traffic back to v1.2
  ├─ Alert on-call engineer
  └─ Pause further deployments (investigation)
```

**Advantages**:

- **Low Risk**: Gradual exposure to new version
- **Production Testing**: Real user loads, patterns
- **Quick Abort**: Stop at any traffic percentage
- **Cost Efficient**: No duplicate infrastructure

**Disadvantages**:

- **Slower**: Takes 1-3 hours vs instant blue-green
- **Complexity**: Need traffic control, monitoring
- **Database Migrations**: Complex with schema changes

### 8.3 Rolling Upgrades

Rolling upgrades update infrastructure incrementally without stopping the cluster.

**Rolling Node Replacement**:

```
Initial State: 100-node cluster, 3 replicas per shard

1. Stop Node 1 (99 nodes active)
   ├─ Drain connections
   ├─ Replicas re-balance (replica moved to other node)
   └─ Cluster recovers

2. Upgrade Node 1
   ├─ Update software
   ├─ Restart
   └─ Rejoin cluster

3. Repeat for Node 2, 3, ..., 100
   ├─ One node down at a time
   └─ Cluster stays operational

Total time: 100 nodes × 5 min per node = ~500 minutes (~8 hours)
```

**Shard Relocation Strategy**:

```
Option 1: Default Rebalancing
  - Cluster auto-rebalances when node down
  - Slow (rebuild shard from network)
  - Use for non-critical data

Option 2: Pre-Empty Shards
  - Move shards off node BEFORE upgrade
  - Fast (shards already available)
  - Use for critical hot tier

Option 3: Rolling Restart (preferred)
  - Use rolling_restart with drain timeout
  - Shards wait for node to come back
  - Works if <5min restart expected
```

**Advantages**:

- **Simple**: No complex orchestration
- **Works**: Standard for persistent data
- **Proven**: Used everywhere for decades

**Disadvantages**:

- **Slow**: 8+ hours for large cluster
- **Risk**: Temporary reduced redundancy
- **Coordination**: Must manage shard movement

### 8.4 Disaster Recovery

Disaster recovery ensures survivability of catastrophic failures.

**RPO/RTO Targets**:

```
Recovery Time Objective (RTO): 5-15 minutes
  - How long until service restored
  - Requires failover infrastructure ready

Recovery Point Objective (RPO): 1 hour
  - How much data loss acceptable
  - Requires replication/backup frequency
```

**Multi-Region Failover**:

```
Primary Region (US-East)
├─ Search cluster
└─ Real-time replication to Backup Region

Backup Region (US-West)
├─ Replica cluster
├─ Lags by < 5 seconds
└─ DNS failover configuration ready

Failure Scenario:
  1. Primary region power failure (all AZs down)
  2. Health checks detect unavailability (< 1 min)
  3. DNS failover to backup region (< 1 min)
  4. Queries routed to US-West cluster
  5. Data loss: < 5 seconds (RPO met)
  6. Downtime: 2-3 minutes (RTO met)
```

**Backup Strategy**:

```
Daily Snapshots:
├─ Full snapshot: Every 24 hours (full backup)
├─ Incremental: Every 6 hours (deltas only)
└─ Retention: 30 days rolling

Snapshot Storage:
├─ Primary: Object storage (S3, GCS)
├─ Secondary: Different region object storage
└─ Cross-region replication enabled

Recovery Process:
1. Identify snapshot to restore (which day/time)
2. Restore from snapshot (30 min - 2 hours)
3. Validate restored data
4. Switchover queries to restored cluster
```

**Data Durability Strategy**:

```
Three copies for data safety:

Copy 1: Primary replica (online, hot)
Copy 2: Secondary replica (online, warm)
Copy 3: Snapshot (offline, cold)

Failure scenarios:
- Primary node fails: Use secondary (immediate)
- Primary + secondary fail: Restore from snapshot (2 hour RTO)
- Snapshot corrupted: Secondary replica available

RPO:
- Between replicas: <1 second
- Snapshot: 6-24 hours depending on frequency
```

---

## 9. Real-Time Search at Scale

Real-time search requires near-instantaneous indexing of updates and immediate query visibility.

### 9.1 Kafka-Based Indexing Pipelines

Kafka provides the backbone for real-time indexing at scale.

**Architecture**:

```
Data Sources
├─ Databases
├─ File uploads
└─ Real-time events
    ↓
Kafka Topics (partitioned by document ID)
├─ topic: "content-updates"
│  ├─ Partition 0 (docs 0-333M)
│  ├─ Partition 1 (docs 333M-666M)
│  └─ Partition 2 (docs 666M-1B)
└─ Retention: 7 days
    ↓
Kafka Consumers (indexing workers)
├─ Consumer Group: "elasticsearch-indexers"
├─ Instance 1 → Partition 0 → ES Shard 0
├─ Instance 2 → Partition 1 → ES Shard 1
└─ Instance 3 → Partition 2 → ES Shard 2
    ↓
Elasticsearch Cluster
└─ Bulk index at high throughput
```

**Scaling Properties**:

```
Single Kafka Topic with 3 Partitions:
├─ Throughput: 1M messages/sec achievable
├─ Latency: <100ms end-to-end (P99)
└─ Availability: 99.95% (replication to 3 brokers)

Scaling to 10M events/sec:
├─ Partition Count: 10 (10 × 1M events/sec)
├─ Consumer Instances: 10 (one per partition)
└─ ES Shards: 10 (one consumer → one shard)
```

**Guarantee Levels**:

```
At-Most-Once:
  - Consumer offset committed before processing
  - Risk: Duplicate skip if consumer fails after commit
  - Use: Non-critical data, high throughput

At-Least-Once:
  - Consumer offset committed after processing
  - Risk: Duplicate indexing if failure after processing
  - Use: Most common, acceptable duplicates (ES deduplicates)

Exactly-Once:
  - Atomic: Offset + index update in single transaction
  - Risk: Complex, lower throughput
  - Use: Financial/compliance systems
```

### 9.2 Change Data Capture (CDC)

CDC captures database changes and streams them to search index for synchronization.

**CDC Approaches**:

**Query-Based CDC**:
```
SELECT * FROM products WHERE updated_at > last_update

Advantages:
  - Simple to implement
  - No database modifications

Disadvantages:
  - Misses deletes (no updated_at)
  - Polling interval = lag
  - CPU intensive (constant queries)

Typical Performance:
  - Polling interval: 5-60 seconds
  - Lag: 5-120 seconds
```

**Log-Based CDC** (Preferred):
```
Database writes → Transaction Log (binlog, WAL)
                    ↓
              CDC Tool (Debezium)
                    ↓
              Kafka Topics (changes)
                    ↓
              Indexing Pipeline
                    ↓
              Elasticsearch (synchronized)

Advantages:
  - Captures creates, updates, deletes
  - Real-time: <1 second lag
  - Less CPU than polling

CDC Tools:
  - PostgreSQL: Debezium connector, Logical Decoding
  - MySQL: Debezium, mysql-cdc
  - MongoDB: Change Streams
  - SQL Server: CDC + Debezium
```

**CDC Pipeline Example**:

```
PostgreSQL Transaction Log
├─ Write customer record: id=12345, name="Alice"
├─ Update customer record: id=12345, name="Alice Smith"
└─ Delete customer record: id=12345
    ↓
Debezium Connector
├─ Reads binlog entries
├─ Converts to JSON events
└─ Publishes to Kafka
    ↓
Kafka Topics
├─ cdc.customers.create: {"id": 12345, "name": "Alice"}
├─ cdc.customers.update: {"id": 12345, "name": "Alice Smith"}
└─ cdc.customers.delete: {"id": 12345}
    ↓
Flink Consumer
├─ Processes stream
├─ Transforms to ES docs
└─ Bulk indexes
    ↓
Elasticsearch
├─ Document 12345 created
├─ Document 12345 updated
└─ Document 12345 deleted
    ↓
Query Result: No document found (correct!)
```

### 9.3 Index Refresh vs Flush vs Merge

Understanding these operations is critical for optimizing real-time indexing.

**Refresh: In-Memory Index Segment**:

```
In-Memory Buffer
├─ New documents accumulated
├─ Not yet searchable
└─ Default interval: 1 second

Refresh Operation (1-5ms):
├─ Create new segment from buffer
├─ Make segment searchable
├─ Clear buffer
└─ More segments = more overhead

Multiple Segments:
├─ Segment 0: 1M documents (1 second old)
├─ Segment 1: 1M documents (2 seconds old)
├─ Segment 2: 1M documents (3 seconds old)
├─ ...
├─ Segment 999: 1M documents (999 seconds old)
└─ Total: 1000 segments to search (slow!)

Tuning:
  - Decrease refresh: index.refresh_interval = 1s (fresh, slow)
  - Increase refresh: index.refresh_interval = 30s (stale, fast)
  - Disable: index.refresh_interval = -1 (fastest, not searchable)
```

**Flush: Disk Persistence**:

```
Segment Exists in Memory
├─ Searchable (after refresh)
├─ Not yet on disk
├─ Risk: Lost if crash
└─ Default: sync every 5 seconds

Flush Operation (10-100ms):
├─ Write segment to disk
├─ Create checkpoint
├─ Enable recovery from checkpoint
├─ Allows low-level deletes

Tuning:
  - Frequent flush: Better durability, more disk I/O
  - Infrequent flush: Less I/O, crash risk
  - With replication: Less critical (replica survives)
```

**Merge: Segment Consolidation**:

```
Many Small Segments (overhead):
├─ 1000 segments × 1MB = memory overhead
├─ Search must check all 1000 (slow)
├─ Merging slows everything

Merge Operation (slow, background):
├─ Combine multiple segments
├─ Consolidate to fewer, larger segments
├─ Example: 1000 segments → 10 segments
├─ Frees space, improves search

Strategy:
  - Hot index: Aggressive merge (high refresh)
  - Warm index: Moderate merge (medium refresh)
  - Cold index: Force merge to 1 segment (then immutable)
```

**Real-Time Indexing Strategy**:

```
For Fresh Data (< 1 minute):
  index.refresh_interval = 1s      (1 second latency)
  index.translog.sync_interval = 5s (durable every 5s)

For Ingest Performance:
  index.refresh_interval = 30s     (30 second latency)
  Disable replicas during bulk load (enable after)

For Query Performance (old data):
  index.refresh_interval = -1      (no refresh)
  Force merge to 1 segment         (optimal search)
  Enable compression               (storage efficient)

Example ILM Policy:
  Hot:
    refresh: 1s
    replica: 2
  Warm:
    refresh: 30s
    force_merge: 1 segment
    replica: 1
  Cold:
    refresh: -1
    force_merge: 1 segment
    replica: 0
```

### 9.4 Near-Real-Time Visibility

Balancing freshness and performance requires careful tuning.

**Latency Budget**:

```
Event generated
    ↓ (1ms capture)
Message broker (Kafka)
    ↓ (10ms propagation)
Indexing worker receives
    ↓ (20ms processing)
Elasticsearch bulk request
    ↓ (50ms execution)
Index refresh (1000ms default)
    ↓
Query can see document
────────────────────────────────
Total: ~1.1 seconds (worst case)
Typical: ~0.1 seconds (with 1s refresh)
```

**Optimization Strategies**:

**1. Reduce Refresh Interval**:
```
Default: 1 second refresh
Cost: +20% indexing overhead per 50% reduction
Benefit: +50% freshness improvement per 50% reduction

Target: 100-500ms refresh (Goldilocks zone)
```

**2. Increase Bulk Size**:
```
Small batches: 100 docs per request
├─ Freshness: 50ms latency
├─ Throughput: ~2000 docs/sec/worker
└─ Network round-trips: High

Large batches: 10K docs per request
├─ Freshness: 500ms latency
├─ Throughput: ~20K docs/sec/worker
└─ Network round-trips: Low
```

**3. Pre-warm Indices**:
```
Query a hot index immediately after creation
├─ Forces segment opens
├─ Warms filesystem cache
└─ Improves subsequent queries
```

**4. Use Realtime GET**:
```
GET /index/_doc/12345?realtime=true
├─ Retrieves from index buffer (un-refreshed)
├─ Guaranteed to see last write
└─ Useful for verification after indexing
```

---

## 10. Case Studies: Enterprise Search Architecture

Real-world implementations reveal critical architectural decisions and trade-offs.

### 10.1 Google Search

**Scale**:
- 100+ billion documents
- 100,000+ queries per second
- Petabytes of index data
- Global data centers

**Architecture**:

```
Web Crawler
├─ Distributed crawlers
└─ Billions of crawl workers
    ↓
Caffeine (Real-time Indexing)
├─ Continuous updates
├─ Billions of updates/day
└─ Visible within seconds
    ↓
MapReduce Batch Processing
├─ PageRank computation
├─ Link analysis
└─ Run nightly (optimized)
    ↓
Bigtable (Distributed Storage)
├─ Inverted indices
├─ Document data
├─ Link graphs
└─ Serving layer
    ↓
Index Servers
├─ Query processing
├─ Ranking
└─ Results aggregation
```

**Key Decisions**:

- **Document Sharding**: Each document goes to one shard (simplifies updates)
- **Scatter-Gather**: Query broadcasts to all shards (complete coverage)
- **Ranking Offline**: PageRank computed offline, embedded in index
- **Real-Time Overlay**: Fresh content via Caffeine before batch PageRank

**Trade-offs**:

- **Completeness**: Cover all documents (at potential cost of freshness)
- **Freshness**: Visible within seconds (via Caffeine)
- **Ranking Quality**: Batch PageRank (high quality but delayed)
- **Cost**: Massive infrastructure (but world-scale problem)

### 10.2 Elasticsearch Deployments at Scale

**Case: Logging at 1M EPS (Events Per Second)**

```
Architecture:

Servers (100K machines)
└─ Produce 10 EPS each
    ↓
Kafka Cluster (3 brokers)
├─ 10 Partitions (1M EPS total)
├─ 7-day retention
└─ Replication factor 3
    ↓
Logstash Workers (10 instances)
├─ Parse, enrich documents
├─ Kafka partition assignment
└─ Bulk index to ES
    ↓
Elasticsearch Cluster (1000 nodes)
├─ 300 indices (1 per day × ~100 days)
├─ 3000 shards (3 per index × 100 days)
├─ 50GB per shard target
├─ 3 replicas per shard
└─ 150TB hot data, 1.5PB total
    ↓
Queries

Cost Analysis:
├─ Network: $300K/month (1M EPS × 1KB × replication)
├─ Compute: $400K/month (1000 nodes × $400/node/month)
├─ Storage: $150K/month (1.5PB × $0.1/GB/month)
└─ Total: ~$850K/month

Cost Optimization (50% reduction):
├─ ILM: Move 7-day to 30-day retention (-35%)
├─ Compression: best_compression codec (-25%)
├─ Tiering: Move to warm after 3 days (-20%)
├─ Deduplication: Remove redundant logs (-15%)
└─ Final: ~$425K/month
```

**Operational Practices**:

- **Index Per Day**: Simplifies lifecycle, enables clean deletion
- **Bulk Indexing**: 10K docs per request (balance freshness/throughput)
- **Shard Routing**: Route by host ID for cache locality
- **Multi-Index Queries**: Use aliases for transparent index management
- **Snapshot Policy**: Daily snapshots, 30-day retention

### 10.3 Vector Search: Recommendation System at Scale

**Case: Product Recommendations (1B items, 500M users)**

```
Architecture:

User Interactions
├─ Views, clicks, purchases
└─ 1B events/day
    ↓
Embedding Generation (Offline)
├─ DNN trained on interactions
├─ 768-dimensional embeddings
├─ Computed daily for all items
└─ 1B vectors × 768 dims × 4 bytes = 3TB
    ↓
FAISS Index (Compressed)
├─ IVF with PQ
├─ 1B vectors compressed to 100GB
├─ 100K clusters for faster search
├─ GPU-accelerated search
    ↓
Recommendation Ranking
├─ Top-100 similar items
├─ Re-rank by business logic (freshness, popularity)
├─ Return top-10 recommendations
    ↓
User Recommendations
```

**Serving Architecture**:

```
Request: "Recommend items like product X for user Y"
    ↓
1. Fetch embedding for product X (cache: 99% hit)
    ├─ Hit: <1ms
    └─ Miss: Compute embedding (~50ms)
    ↓
2. Query FAISS index
    ├─ Latency: 10-20ms (GPU-accelerated)
    ├─ Returns: 100 similar products
    └─ Memory: All 100GB in GPU memory
    ↓
3. Re-rank by business rules
    ├─ Freshness score
    ├─ Popularity
    ├─ Inventory
    └─ Latency: 5-10ms
    ↓
4. Return top-10 recommendations
    ├─ Total latency: 30-50ms
    └─ QPS: 100K+ on single GPU
```

**Cost Analysis**:

```
Hardware:
├─ GPU Cluster: 5 A100 GPUs
│  ├─ Cost: $4000/month each
│  └─ Total: $20K/month
├─ CPU for ranking: 10 nodes
│  └─ Cost: $4K/month
├─ Storage (backups): 1TB SSD
│  └─ Cost: $100/month
└─ Total: ~$24K/month

Throughput:
├─ Single GPU: 100K QPS
├─ 5 GPUs: 500K QPS
├─ With failover/warmup: 250K QPS sustainable

Cost Per Million Requests:
├─ $24K/month = $24K / (250K QPS × 2.6M seconds)
└─ ≈ $0.03 per million requests
```

### 10.4 Multi-Tenant Search Platform

**Case: SaaS Search (10K tenants, 100K total indices)**

```
Architecture:

Tenant 1 (1000 indices)
├─ Isolated ES cluster
├─ 10 nodes
└─ Data separation

Tenant 2 (2000 indices)
├─ Isolated ES cluster
├─ 20 nodes
└─ Data separation

Tenant 3 (1000 indices)
├─ Shared cluster (100 tenants)
├─ 50 nodes
└─ Shard-level isolation

...

Shared Cluster (lower-tier tenants)
├─ 100 tenants
├─ 100K total indices
├─ 1000 nodes
└─ Tight resource controls
```

**Isolation Strategy**:

```
Premium Tenants:
├─ Dedicated ES clusters
├─ SLA: 99.95% uptime
├─ Custom configurations
└─ Cost: $5K-50K/month

Mid-Tier Tenants:
├─ Shared cluster, dedicated shards
├─ SLA: 99.9% uptime
├─ Standard configurations
└─ Cost: $500-5K/month

Standard Tenants:
├─ Shared cluster, shared shards
├─ SLA: 99% uptime
├─ Noisy neighbor risk
└─ Cost: $50-500/month
```

**Multi-Tenancy Challenges**:

```
Resource Contention:
├─ Problem: One tenant's hot query affects others
├─ Solution: Query queuing, circuit breaker patterns
├─ Monitoring: Per-tenant resource tracking

Data Isolation:
├─ Problem: Tenant B shouldn't see Tenant A's data
├─ Solution: Query filtering by tenant_id
├─ Verification: Audit logs of cross-tenant reads

Cost Allocation:
├─ Problem: How much does each tenant cost?
├─ Solution: Per-shard metrics, weighted to nodes
├─ Billing: Cost per GB indexed, per query

Upgrades:
├─ Problem: Can't take shared cluster offline
├─ Solution: Rolling restarts, blue-green with shared cluster
└─ Complexity: Higher operational burden
```

---

## Summary: Key Principles for Billion-Scale Search

1. **Sharding is Fundamental**: Horizontal partitioning enables scale beyond single-node limits
2. **Scatter-Gather Parallelizes**: Broadcasting to shards reduces latency through parallelization
3. **Replication Enables Resilience**: 3+ copies survive failures and enable read scaling
4. **Tiering Reduces Cost**: Hot/warm/cold moves data between storage types based on access
5. **Compression is Essential**: ZSTD, PQ, SQ reduce storage by 2-10x
6. **Real-Time Requires Infrastructure**: Kafka pipelines, CDC, careful refresh tuning enable freshness
7. **Operational Excellence Scales**: Blue-green, canary, rolling upgrades enable safe changes
8. **Monitoring is Non-Negotiable**: Comprehensive metrics identify issues before they matter
9. **Cost Optimization is Continuous**: Automated lifecycle policies, tiering, compression yield 50%+ savings
10. **Trade-offs are Everywhere**: Speed vs accuracy, freshness vs cost, complexity vs simplicity

---

## References and Further Reading

### Architectural Patterns

- [Scatter-Gather Pattern - AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/scatter-gather.html)
- [Scatter-Gather - Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/BroadcastAggregate.html)
- [Understanding Database Sharding - DigitalOcean](https://www.digitalocean.com/community/tutorials/understanding-database-sharding)
- [Database Sharding: Strategies for Seamless Scaling - SimpleTalk](https://www.red-gate.com/simple-talk/databases/theory-and-design/database-sharding-strategies-for-seamless-scaling-and-performance-optimization/)

### Elasticsearch Documentation

- [Elasticsearch Scaling Considerations](https://www.elastic.co/docs/deploy-manage/production-guidance/scaling-considerations)
- [Index Lifecycle Management](https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management)
- [Cross-Cluster Search](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-cross-cluster-search.html)
- [Implementing Hot-Warm-Cold Architecture](https://www.elastic.co/blog/implementing-hot-warm-cold-in-elasticsearch-with-index-lifecycle-management)

### Vector Search

- [FAISS: A Library for Efficient Similarity Search - Meta Engineering](https://engineering.fb.com/2017/03/29/data-infrastructure/faiss-a-library-for-efficient-similarity-search/)
- [FAISS Documentation](https://faiss.ai/index.html)
- [FAISS vs ScaNN on Vector Search - Zilliz Blog](https://zilliz.com/blog/faiss-vs-scann-choosing-the-right-tool-for-vector-search)
- [DiskANN: Vector Search at Web Scale - Microsoft Research](https://www.microsoft.com/en-us/research/project/project-akupara-approximate-nearest-neighbor-search-for-large-scale-semantic-search/)

### Real-Time Indexing

- [Change Data Capture and Kafka - Aerospike](https://aerospike.com/blog/change-data-capture-cdc-guide/)
- [Building Faster Indexing with Apache Kafka and Elasticsearch - DoorDash](https://careersatdoordash.com/blog/open-source-search-indexing/)
- [Building Data Pipelines with Apache Kafka and Confluent](https://developer.confluent.io/courses/data-pipelines/kafka-data-ingestion-with-cdc/)

### Deployment Strategies

- [Blue-Green and Canary Deployments Explained - Harness](https://www.harness.io/blog/blue-green-canary-deployment-strategies)
- [Deployment Strategies: Blue-Green, Canary, Rolling - CircleCI](https://circleci.com/blog/canary-vs-blue-green-downtime/)

### Cost Optimization

- [Data Storage Optimization - Komprise](https://www.komprise.com/glossary_terms/data-storage-optimization/)
- [Tiered Storage Solutions - Wasabi](https://wasabi.com/blog/the-channel/tiered-storage-solutions-for-cloud-cost-optimization/)
- [Optimizing Costs in Elastic Cloud - Elastic Blog](https://www.elastic.co/blog/optimizing-costs-elastic-cloud-hot-warm-index-lifecycle-management)

### Google-Scale Infrastructure

- [Google Search System Design - System Design Handbook](https://www.systemdesignhandbook.com/guides/google-search-system-design/)
- [PageRank and MapReduce on Medium](https://medium.com/swlh/pagerank-on-mapreduce-55bcb76d1c99)
- [Case Study: Google - DEV Community](https://dev.to/grenishrai/case-study-google-597k)

---

**Document Created**: March 1, 2026
**Scope**: Billion-scale search infrastructure, architectural patterns, operational practices
**Audience**: Distributed systems engineers, search infrastructure architects, platform engineers
**Version**: 1.0
