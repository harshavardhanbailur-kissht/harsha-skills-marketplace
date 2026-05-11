# Search Architecture Encyclopedia: From Single-Node to Planet-Scale

## Complete Reference for Production Search System Design

This comprehensive guide covers architecture patterns used in production search systems across every major scale tier. Each pattern is grounded in real-world implementations from companies like Google, LinkedIn, Elasticsearch, Amazon, and other tech leaders.

---

## Part 1: Indexing Architecture

### 1.1 Forward Index vs. Inverted Index

The choice between forward and inverted indices fundamentally shapes retrieval performance and use cases.

**Forward Index Architecture:**
- Maps documents to content: Document → [Word1, Word2, Word3]
- Efficient when you already know the document ID
- Good for storage (single pass through all words in a document)
- Poor for search (must scan all documents for a query term)

**Inverted Index Architecture:**
- Maps content to documents: Word → [Doc1, Doc3, Doc7]
- Allows direct lookup from query terms to matching documents
- Standard for full-text search engines
- Enables extremely fast retrieval without document scanning

**Hybrid Approach (Modern Systems):**
```
Modern search systems use BOTH:
├── Forward Index: For computing inner products, storing document vectors
├── Inverted Index: For pinpointing documents that must be evaluated
└── Two-stage retrieval: Inverted index narrows candidates, forward index ranks them
```

The inverted index is the backbone of full-text search, allowing Elasticsearch, Solr, and similar engines to evaluate search queries by quickly locating documents containing the words in a query, then ranking these documents by relevance.

### 1.2 Real-Time vs. Batch Indexing

**Real-Time Indexing (Near-Real-Time NRT):**
- Documents available for search within milliseconds to seconds
- Elasticsearch default: 1-second refresh interval
- Refresh process: buffered writes → new segment → searchable
- Trade-off: indexing throughput vs. search latency

**Refresh Interval Configuration:**
```
# Default (general purpose): 1 second
PUT /my_index/_settings
{
  "refresh_interval": "1s"
}

# Optimized for writes (observability, logs): 30-60 seconds
PUT /observability_index/_settings
{
  "refresh_interval": "30s"
}

# Disable auto-refresh, control manually
PUT /batch_index/_settings
{
  "refresh_interval": "-1"
}
```

**Batch Indexing:**
- Collects documents in memory, indexes periodically
- Much higher throughput (1-5 minute intervals typical)
- Documents not searchable until batch completes
- Optimal for data warehouses, historical analysis

**Idle Index Behavior:**
- Elasticsearch stops refreshing idle indices after 30 seconds of no search traffic
- Parameter: `index.search.idle.after` (default: 30s)
- Saves CPU/memory for indices with bursty query patterns

### 1.3 Write-Ahead Log (WAL) for Index Durability

WAL is the foundation of durable distributed search systems.

**Basic WAL Mechanism:**
```
Application → Write WAL Entry → Write Index → Acknowledge to Client
              (SYNC to disk)    (async ok)
```

**WAL Segment Structure:**
- PostgreSQL: 16 MB segment files
- Prometheus: 128 MB segment files (configurable)
- Each segment contains sequential write operations
- New segment created when current fills

**Crash Recovery:**
```
System Failure
    ↓
Restart
    ↓
Replay WAL from last checkpoint
    ↓
Reapply uncommitted transactions
    ↓
Full consistency restored
```

**Durability Guarantees:**
- Changes written to WAL before data pages modified
- In crash scenarios, WAL replayed to restore state
- All modifications flushed to persistent storage
- Provides atomic transaction semantics

### 1.4 Index Segments, Merging, and Compaction

Inverted indices in production systems are organized as immutable segments for concurrent access and efficient compaction.

**Segment Architecture:**
```
Index (Logical View)
├── Segment_0: [Early documents, immutable]
├── Segment_1: [Middle documents, immutable]
├── Segment_2: [Recent documents, in-memory buffer]
└── Segment_3: [Being merged from Segment_0, Segment_1]
```

**Segment Creation Process:**
1. New writes buffered in memory (memtable)
2. When buffer fills (threshold reached)
3. Flush to disk as new immutable segment
4. Segment added to searchable index

**Segment Merging:**
```
Merging reduces fragment count, improving query performance:

Before: [Seg0: 1000 docs] [Seg1: 500 docs] [Seg2: 100 docs] = 3 segments
   ↓ (merge operation)
After:  [Seg0: 1600 docs] = 1 segment

Benefits:
├── Fewer segments to search
├── Better cache locality
├── Faster group operations (aggregations)
└── Reduces file descriptor usage
```

**Compaction Levels (LSM-Tree Pattern):**
```
L0 (In-Memory):     Very fast writes, many segments
   ↓ (compact when threshold reached)
L1 (Hot Tier):      Slower writes, fewer segments, warmer data
   ↓
L2 (Cold Tier):     Rare updates, single merged segment
   ↓
L3 (Archive):       Immutable, highly compressed
```

Write-Through: Record rewritten 3-10 times before settling in coldest level.

### 1.5 Concurrent Read/Write Patterns

Production search indices must support high-concurrency workloads.

**Copy-on-Write Semantics:**
```
Read Snapshot 1 ← Points to Segments [A, B, C] ← Immutable
Concurrent
Write thread ← Modifies memtable → Creates Segment D
Read Snapshot 2 ← Points to Segments [A, B, C, D] ← New index version
```

**Snapshot Isolation:**
- Each search query sees consistent index snapshot
- New writes don't interfere with in-flight searches
- Readers don't block writers (wait-free reads)
- Writers might briefly wait for segment flush

**Lock-Free Data Structures:**
- Posting lists: Read with atomic CAS operations
- Segment metadata: Version-based consistency
- Bloom filters: Atomic updates for false positive reduction

### 1.6 Near-Real-Time (NRT) Search Refresh Intervals

**Default Refresh Strategy:**
- Elasticsearch refreshes indices every 1 second
- But only indices receiving at least 1 search in last 30 seconds
- Idle indices stop auto-refreshing to save resources

**Configuration Decisions:**

| Use Case | Interval | Rationale |
|----------|----------|-----------|
| User search (general) | 1s | Balance freshness & throughput |
| Social media feeds | 200ms | High visibility requirement |
| Observability/logs | 30-60s | Write throughput critical |
| Analytics (batch) | 5min+ | Throughput maximized |
| Dormant indices | -1 (disabled) | Manual refresh only |

**Trade-offs with Refresh Intervals:**
```
Smaller intervals (100ms-500ms):
  ✓ Fresh results visible quickly
  ✗ High CPU from frequent segment flushes
  ✗ More segments to search (slower queries)
  ✗ More GC pressure (more object allocation)

Larger intervals (30s-60s):
  ✓ Higher indexing throughput (fewer flushes)
  ✓ Fewer segments, faster search
  ✓ Lower CPU utilization
  ✗ Stale results (visible delay)

Tuning Formula: refresh_interval = (acceptable_staleness) / 2
```

---

## Part 2: Tokenization & Text Analysis

### 2.1 Tokenizer Types

Text analysis is the first step in creating searchable indices. Different tokenizers suit different languages and use cases.

**Standard Tokenizer (Default):**
```
Input:  "The quick brown fox jumps over lazy dog!"
Output: ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]

Rules:
├── Split on whitespace and punctuation
├── Lowercase (if lowercase filter applied)
└── Remove punctuation marks
```

**Whitespace Tokenizer:**
```
Input:  "hello-world user@example.com"
Output: ["hello-world", "user@example.com"]

Use case: When punctuation is semantically meaningful
```

**Custom Pattern Tokenizer:**
```json
{
  "tokenizer": {
    "custom_email": {
      "type": "pattern",
      "pattern": "[\\W_]+"
    }
  }
}
```

**Language-Specific Tokenizers:**
- Arabic: Diacritic-aware, handles dialects
- Hindi: Handles agglutination, no whitespace boundaries
- CJK: Character bigrams, no word boundaries
- Thai: Dictionary-based segmentation

### 2.2 Stemming vs. Lemmatization Trade-offs

**Stemming (Fast, Aggressive):**
```
running → runn
quickly → quick
university → univers  (overstemming!)

Algorithm: Rule-based suffix removal
├── Porter Stemmer: Classic, language-agnostic
├── Snowball: Evolved Porter, handles more languages
└── Hunspell: Morphological analysis

Trade-offs:
✓ Very fast (minimal CPU overhead)
✓ Better recall (jumping ≈ jump)
✗ Less accurate (university → univers)
✗ Risk of collision (operate → oper, operator → oper)
```

**Lemmatization (Slow, Accurate):**
```
running → run
quickly → quick
university → university

Algorithm: Dictionary-based + morphological analysis
├── POS tagging: Identify part of speech
├── Dictionary lookup: Find canonical form
└── Rules: Handle exceptions

Trade-offs:
✓ Accurate results (valid lemmas only)
✓ No overstemming issues
✗ Slower (2-5x vs. stemming)
✗ Dictionary required (language-specific)
✗ May hurt recall on typos
```

**Production Decision Matrix:**

| System | Stemming | Lemmatization |
|--------|----------|---------------|
| Google (web search) | Yes | Yes (for disambiguation) |
| E-commerce (Elasticsearch) | Yes | For product titles |
| Legal documents | No | Yes (precision required) |
| Social media | Yes | Skip (hashtags matter) |
| Machine translation | Yes | Yes (both applied) |

### 2.3 Stop Words: When They Help and When They Hurt

**Stop Word Removal (Traditional Approach):**
```
Common stop words: the, a, an, and, or, but, is, are, ...

Before: "the quick brown fox"
After:  "quick brown fox"

Benefits:
├── Reduce index size by 20-30%
├── Fewer false positives
└── Faster queries (fewer postings to scan)

Problems:
├── "to be or not to be" → "be" (loses meaning!)
├── "New York" → "new" (loses geography context)
└── Breaks phrase queries: "Where are you" → "where you"
```

**Modern Trend: Skip Stop Words**
- Disk space cheap, index compression effective
- Phrase queries important for relevance
- Keep "to", "of", "and" for semantic meaning
- Use stop words selectively for specific use cases

**Best Practice Configuration:**
```json
{
  "analyzer": {
    "my_analyzer": {
      "type": "standard",
      "stopwords": []  // Don't remove
    }
  },
  "filter": {
    "stop_filter": {
      "type": "stop",
      "stopwords": ["very", "much", "quite"]  // Only specific words
    }
  }
}
```

### 2.4 Synonyms and Thesaurus Expansion

**Synonym Expansion:**
```
Query: "tv"
Expanded: tv OR television OR telly OR screen

During indexing:
- Document: "Watch television"
- Expanded tokens: [watch, television, tv, telly]

Result: Query "tv" matches documents with "television"
```

**Implementation Options:**

```
Expansion at Index Time:
  ✓ Faster queries (synonyms indexed)
  ✗ Larger index (duplicate documents)
  ✗ Stale synonyms (require reindex to update)

Expansion at Query Time:
  ✓ Easy to update synonyms
  ✓ Smaller index
  ✗ Slower queries (expand every search)
  ✗ Harder to control precision/recall

Hybrid: Index common synonyms, expand rare ones at query time
```

**Thesaurus Management (Large Scale):**
```
Structured thesaurus:
├── Synonym groups: {tv, television, telly, screen}
├── Bidirectional links: (laptop ← desktop) ← computer
├── Weighted relationships: cat → feline (0.95), pet (0.8)
└── Domain-specific: liver (organ) vs. liver (region)
```

### 2.5 Multi-Language Search Architecture

**Language Identification:**
```
Incoming query → Language detector (fasttext, BERT) → Language ID
                                                           ↓
                                              Load language-specific analyzer
```

**Per-Language Analyzer Configuration:**
```json
{
  "analyzer": {
    "en_analyzer": {
      "type": "standard",
      "stopwords": "_english_"
    },
    "ar_analyzer": {
      "type": "standard",
      "stopwords": "_arabic_"
    },
    "hi_analyzer": {
      "type": "icu_analyzer",
      "language": "hi"
    }
  }
}
```

**CJK-Specific Challenges:**
```
Chinese: "我爱搜索" (wo ai sousuo - "I love search")
├── No whitespace between words
├── Complex character analysis needed
└── Solution: Character bigrams or ICU analyzer

Japanese: "検索エンジン" (kensaku enjin - "search engine")
├── Mix of kanji, hiragana, katakana
└── Solution: MeCab tokenizer with morphological analysis

Korean: "검색 엔진" (geomseag engin)
├── Spaces present, but compound words matter
└── Solution: Komoran or Mecab for proper segmentation
```

**Hindi Morphology:**
```
"जाना" (jana - "to go")
├── Root: ज (ja)
├── Suffix: -ना (-na, infinitive marker)
└── Variations: जा सकता हूँ (can go), गया था (went)

Challenge: Agglutination without whitespace
"करना" (to do) + "सकना" (can) = "कर सकना"

Solution: Multilingual transformers (mBERT, XLM-RoBERTa)
```

### 2.6 N-gram Analysis for Partial Matching

**N-gram Fundamentals:**
```
Text: "search"

Bigrams (n=2): se, ea, ar, rc, ch
Trigrams (n=3): sea, ear, arc, rch
4-grams (n=4): sear, earc, arch

Purpose: Find partial matches without wildcards
```

**Edge N-grams for Autocomplete:**
```
Word: "elasticsearch"

Edge bigrams: e, el, ela, elas, elast, ...
  ↓
Index: [e, el, ela, elas, elast, elasti, elastic, elastiс, ...]

Query: "elast"
  ↓
Direct postings lookup (no regex!)
  ↓
Fast autocomplete results
```

**N-gram Index Configuration:**
```json
{
  "analyzer": {
    "autocomplete": {
      "type": "custom",
      "tokenizer": "edge_ngram_tokenizer",
      "filter": ["lowercase"]
    }
  },
  "tokenizer": {
    "edge_ngram_tokenizer": {
      "type": "edge_ngram",
      "min_gram": 2,
      "max_gram": 20,
      "token_chars": ["letter", "digit"]
    }
  }
}
```

**Wildcard Search with N-grams:**
```
Query: "test*ing"
├── Extract common n-grams: "est", "ing"
├── Look up postings for both n-grams
├── Intersect matching documents
└── Post-filter against original pattern
```

---

## Part 3: Distributed Search Architecture

### 3.1 Sharding Strategies

Sharding distributes data across nodes to scale horizontally. Three main strategies balance consistency, flexibility, and performance.

**Hash-Based Sharding:**
```
shard_id = hash(document_id) % num_shards

Document 1 → hash(1) % 5 = Shard 3
Document 2 → hash(2) % 5 = Shard 1
Document 3 → hash(3) % 5 = Shard 4

Advantages:
├── Even data distribution
├── Fast lookups (one hash)
└── No range scans needed

Disadvantages:
├── Rebalancing requires rehashing all data
├── Hard to query ranges (e.g., dates)
└── Hot shards possible if hash biased
```

**Range-Based Sharding:**
```
Date-based (example):
├── Shard 0: Jan 1 - Mar 31
├── Shard 1: Apr 1 - Jun 30
├── Shard 2: Jul 1 - Sep 30
└── Shard 3: Oct 1 - Dec 31

Advantages:
├── Easy range queries (one or few shards)
├── Natural hot/cold separation
└── Simple rebalancing (time-based)

Disadvantages:
├── Uneven distribution (summer queries > winter)
├── Hot shard problem (recent data heavily accessed)
└── Limited sharding flexibility
```

**Custom Sharding (Geo, User Segment):**
```
Geographic:
├── Shard 0: North America
├── Shard 1: Europe
├── Shard 2: Asia-Pacific
└── Shard 3: Rest of World

User segment:
├── Shard 0: Free users
├── Shard 1: Premium users
├── Shard 2: Enterprise users

Advantages:
├── Collocate related data
├── Geographic optimization
└── Compliance (data residency)

Disadvantages:
├── Complex routing logic
├── Cross-shard queries required
└── Rebalancing complex
```

**Shard Sizing Guidance:**
```
Document Count: 10-50 billion per shard (gigabyte range)
Index Size: 20-40 GB per shard (hot), 50-100 GB acceptable
Replica Impact: Each replica = full shard size

Formula: num_shards = total_docs / 30_billion OR total_size_gb / 40

Example:
├── 300 billion documents
├── Desired shard size: 30B docs
├── Required shards: 300B / 30B = 10 shards

With replication factor 2:
├── 10 primary + 10 replicas = 20 total shards
└── 20 nodes × 2 shards each = balanced cluster
```

### 3.2 Replication: Leader-Follower vs. Peer-to-Peer

**Leader-Follower Replication (Elasticsearch, PostgreSQL):**
```
                Primary Shard
                    ↓ write
        [All writes go here]
              ↙  ↓  ↘
        Replica1  Replica2  Replica3
        (read-only replicas)

Consistency model: Strong consistency (all writes via primary)
Write flow:
  1. Client writes to primary shard
  2. Primary applies locally
  3. Primary sends to all replicas
  4. Replicas acknowledge
  5. Primary acknowledges to client

Advantages:
├── Simple consistency model
├── Single source of truth
└── Easy monitoring

Disadvantages:
├── Primary becomes bottleneck
├── Failover requires promotion (potential data loss)
└── Replica lag possible under high load
```

**Peer-to-Peer Replication (Cassandra, Dynamo):**
```
      Node A          Node B          Node C
     [Data]          [Data]          [Data]
       ↓ write         ↓              ↓
    Apply locally   Sync with A    Sync with A
       ↓              ↓              ↓
    All three nodes have data
    (read from any)

Consistency model: Eventual consistency (configurable)
Write options:
  1. Write one replica, others sync eventually (fastest)
  2. Write quorum (default Cassandra), balance latency/consistency
  3. Write all replicas (strongest, slowest)

Advantages:
├── No single point of failure
├── High availability
├── Scales horizontally
└── No bottleneck node

Disadvantages:
├── Complex conflict resolution
├── Eventual consistency risks
├── Harder to debug
```

**Elasticsearch's Hybrid Approach (PacificA Model):**
```
Writes:
├── Route to primary shard
├── Primary applies and replicates
└── Acknowledge when quorum updated

Reads:
├── Use adaptive replica selection
├── Route to fastest available replica
└── Can read from primary or replicas

Benefits:
├── Strong consistency for writes
├── Fast reads (any replica ok)
└── Automatic failover if primary fails
```

### 3.3 Query Routing and Scatter-Gather

**Query Routing:**
```
Client Query → Coordinator Node (any node) → Determine shards to query
                                              ↓
                                        Send to each shard → Get results
                                              ↓
                                        Merge results → Return to client
```

**Shard Targeting:**
```
User query: "find documents in Jan-Mar"
Query router:
  ├── Identify shards: [Shard_0 (Jan-Mar), Shard_1 (Apr-Jun), ...]
  ├── Single shard query: Route only to Shard_0 (FAST!)
  ├── Return results
  └── No broadcast to all shards needed

Date-based sharding advantage: Can skip shards entirely
```

**Scatter-Gather Pattern:**
```
Client Request
    ↓
Coordinator
    ↓
    ├─ Send to Shard_1 ────────┐
    ├─ Send to Shard_2 ────────┤─ Parallel requests
    └─ Send to Shard_3 ────────┘
         ↓        ↓        ↓
    Results_1 Results_2 Results_3
         ↓        ↓        ↓
         └─ Merge Sort ─┘
              ↓
        Final Result Set
        (combined top-K)
```

**Merge Sort for Relevance:**
```
Shard 1 returns:
  Doc_10 (score: 98.5)
  Doc_15 (score: 87.3)

Shard 2 returns:
  Doc_5 (score: 95.2)
  Doc_20 (score: 80.1)

Global merge:
  1. Doc_10 (98.5)
  2. Doc_5 (95.2)
  3. Doc_15 (87.3)
  4. Doc_20 (80.1)
```

**Coordinator Node Optimization:**
```
Deep pagination problem:
  Query 1-10: Coordinator fetches top 10 from each shard
  Query 990-1000: Coordinator must fetch top 1000 from each!

Solution:
  ├── Limit deep pagination (max 10,000 results)
  ├── Use search after (keyset pagination)
  └── Client-side caching for large result sets

Search After (Efficient pagination):
  Page 1: GET /index/_search?size=100
  Page 2: GET /index/_search?size=100&search_after=[last_doc_id, last_score]
```

### 3.4 Shard Allocation and Rebalancing

**Automatic Shard Allocation:**
```
Elasticsearch rebalancing algorithm:

For each node:
  ├── Calculate "weight" = number of shards
  ├── Identify heaviest node
  ├── Move shards to lighter nodes
  └── Repeat until balanced

Constraint: No primary + replica on same node
```

**Manual Shard Allocation (Advanced):**
```json
{
  "settings": {
    "index.routing.allocation.include._ip": "10.0.1.*"
  }
}

Result: Index shards only on nodes with IP in 10.0.1.0/24
```

**Rebalancing Triggers:**
- New node joins cluster
- Node fails (replicas moved to healthy nodes)
- Shard explicitly reassigned
- Disk threshold exceeded (move away from full disk)

**Rebalancing Costs:**
```
Moving 1 shard (50 GB):
├── Network: 50 GB transfer (seconds to minutes)
├── Disk I/O: Read source, write destination
├── CPU: Data serialization/deserialization
└── Query latency: Affected during transfer

Solution: Schedule rebalancing during low-traffic windows
```

### 3.5 Split-Brain Prevention

Split-brain occurs when network partition divides cluster into disconnected partitions, each thinking it's the healthy cluster.

**Scenario:**
```
Initial: Node_A, Node_B, Node_C (3 nodes, all healthy)
         ↓ (network partition)
Partition 1: Node_A (isolated)
Partition 2: Node_B, Node_C (connected)

Node_A thinks others failed
Node_B, Node_C think Node_A failed
  ↓
Both partitions accept writes
  ↓
Data divergence! (split-brain)
```

**Prevention: Quorum-Based Consensus:**
```
With 3 nodes:
├── Minimum master nodes: (3 / 2) + 1 = 2
├── Partition 1 (Node_A): 1 node, needs 2 → CANNOT be master
├── Partition 2 (Node_B, Node_C): 2 nodes → CAN be master

Result: Only healthy partition continues accepting writes
        Partition 1 stops (circuit breaker)
```

**Configuration:**
```
3-node cluster:
  discovery.zen.minimum_master_nodes: 2

5-node cluster:
  discovery.zen.minimum_master_nodes: 3

Formula: quorum = (num_nodes / 2) + 1
```

### 3.6 Cross-Datacenter Replication

**Architecture Pattern:**
```
Datacenter A (Primary)          Datacenter B (Secondary)
├── Write-leader node           ├── Read replica
├── Replication log             ├── Applies remote log
└── Sends log entries ────────────→ [network link]
                                └── Replication lag possible
```

**Synchronous vs. Asynchronous:**
```
Synchronous (Strong consistency):
  Write → Primary applies → Sends to Secondary → Wait for ack → Return

Disadvantage: High latency (network RTT × 2)

Asynchronous (Eventual consistency):
  Write → Primary applies → Return → Send to Secondary (background)

Advantage: No remote latency impact
Disadvantage: Data loss possible if primary fails before secondary syncs
```

**Failover Handling:**
```
Primary datacenter fails:
  1. Detect failure (health checks, heartbeat timeout)
  2. Promote secondary to primary
  3. Accept writes on secondary
  4. When primary recovers: merge/replay logs
  5. Reestablish replication

Challenges:
├── Detect failure quickly (seconds, not minutes)
├── Handle out-of-order operations
└── Reconcile diverged data
```

---

## Part 4: Caching Strategies

### 4.1 Query Result Caching

Query result caching stores complete search results to avoid recomputation.

**LRU Caching (Least Recently Used):**
```
Cache size: 100 MB
Current cache: [Query_A: 50 MB], [Query_B: 40 MB], [Query_C: 9 MB]
New query: [Query_D: 5 MB]

Eviction: Remove Query_C (least recently used), add Query_D
Result cache: [Query_A: 50 MB], [Query_B: 40 MB], [Query_D: 5 MB]
```

**LFU Caching (Least Frequently Used):**
```
Query_A: accessed 100 times (frequency: high)
Query_B: accessed 2 times (frequency: low)
Query_C: accessed 50 times (frequency: medium)

When cache full: Evict Query_B (lowest frequency)
```

**TTL-Based Caching (Time To Live):**
```
Cache entry: [Query_X: result, timestamp: 2:00 PM, TTL: 5 minutes]

At 2:05 PM: Entry expired, remove from cache
```

**Hybrid Strategy (Production):**
```json
{
  "cache_config": {
    "strategy": "LRU",
    "max_size_mb": 500,
    "ttl_seconds": 300,
    "min_hits_to_cache": 3
  }
}

Rules:
├── Only cache queries hit 3+ times
├── Evict LRU when hitting 500 MB
├── Expire all entries after 5 minutes
└── Refresh on expiry if query still popular
```

### 4.2 Filter Caching (Bitset Caching)

Filter caching uses compressed bitsets to cache filter matching results.

**Bitset Structure:**
```
Document IDs: [1, 3, 5, 7, 9, 10, 12, ...]
Filter: "status = ACTIVE"

Matching docs: 3, 5, 7, 10, 12
Bitset representation: [0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, ...]
                       1  2  3  4  5  6  7  8  9  10 11 12

Bit 3 = 1 (doc 3 matches)
Bit 5 = 1 (doc 5 matches)
```

**Performance Benefits:**
```
Bitwise operations (same hardware):

Naive filter recomputation:
  Parse index structures + evaluate logic = expensive

Cached bitset AND:
  CPU: Performs bitwise AND of two 64-bit words in 1 cycle

Speedup: 3-50x depending on filter complexity
```

**Caching Rules:**
```
Segments are cached independently:
├── Segment size > 10,000 docs OR > 3% of total docs
├── Filter hit 2+ times in last 256 queries
└── Cache only non-scoring filters

Large segments cached first (maximum benefit)
```

**Complex Query Example:**
```
Query: (status = "ACTIVE") AND (price < 100) AND (rating > 4.0)

Execution:
  1. Lookup "status = ACTIVE" → BitSet_A (cached)
  2. Lookup "price < 100" → BitSet_B (cached)
  3. Lookup "rating > 4.0" → BitSet_C (cached)
  4. Compute: BitSet_A & BitSet_B & BitSet_C (CPU bitwise)
  5. Get matching documents (milliseconds)
```

### 4.3 Field Data Caching for Sorting/Aggregations

Field data (fieldvalue cache) holds term values in memory for sorting and aggregations.

**Fieldvalue Cache Structure:**
```
Field: "category"
├── Document 1: "electronics"
├── Document 2: "books"
├── Document 3: "electronics"
└── Document N: "toys"

Inverted structure (for sorting):
├── "books" → [2, 15, 89, ...]
├── "electronics" → [1, 3, 45, ...]
└── "toys" → [4, 12, 78, ...]

Sortable in-memory array: ["books", "electronics", "electronics", "toys", ...]
```

**Building Fieldvalue Cache:**
```
First sort request on field:
  1. Load all field values for segment (I/O intensive)
  2. Build sortable in-memory structure
  3. Cache in heap
  4. Subsequent sorts use cache (much faster)

Cache size: Can grow large (10-20% of heap typical)
```

**Aggregation Example:**
```
Aggregation: Histogram of prices per category

With fieldvalue cache:
  1. Iterate categories (cached)
  2. For each category, iterate documents
  3. Compute price histogram
  4. Fast (memory bandwidth bound)

Without cache:
  1. Read from inverted index repeatedly
  2. Deserialize and recompute
  3. Slow (CPU, disk I/O bound)
```

### 4.4 Cache Warming and Startup

Cache warming preloads hot data on startup to avoid cold-start latency.

**Manual Warmup:**
```json
{
  "cache_warming": {
    "top_queries": [
      {"query": "product type:*", "hits": 1000},
      {"query": "popular_category", "hits": 500},
      {"query": "featured_deals", "hits": 100}
    ],
    "field_cache_fields": ["category", "brand", "price"]
  }
}
```

**Automatic Warmup (Search-as-you-type):**
```
System records:
  ├── Popular filters (cached as query warm requests)
  ├── Frequent sorts (trigger fieldvalue cache build)
  └── Hot queries (warmup list periodically updated)

On node startup:
  1. Execute warmup queries
  2. Load frequently accessed field values
  3. Reach ~80% cold-start performance within seconds
```

**Adaptive Warming:**
```
Track query patterns:
  Query A (category = "electronics"): 1000 hits/min
  Query B (brand = "Sony"): 500 hits/min
  Query C (rare_field): 1 hit/min

Warmup ratio: Allocate cache space proportional to hit frequency
  100 MB cache → 67 MB for Query A, 33 MB for Query B
```

### 4.5 Cache Invalidation Strategies

Cache invalidation is notoriously difficult ("two hard problems in CS: naming and cache invalidation").

**Time-Based Invalidation (TTL):**
```
Cache entry: ["category:electronics", timestamp: 10:00, TTL: 5min]
At 10:05: Automatically expired

Pros: Simple, predictable staleness
Cons: Stale results for up to TTL duration
```

**Event-Based Invalidation:**
```
On document update:
  1. Parse which filters affected (status, category, etc.)
  2. Invalidate affected caches
  3. Keep unaffected caches

Example:
  Update doc: status: "active" → "inactive"
  Invalidate: cache["status=active"], cache["status=inactive"]
  Keep: cache["category=electronics"] (unaffected)
```

**Write-Through Invalidation:**
```
High-consistency requirement:

Write request:
  1. Update index
  2. Invalidate related caches
  3. Acknowledge to client

Trade-off: Cache miss on subsequent reads (if new data cached)
Solution: Write-behind: invalidate asynchronously
```

**Selective Invalidation:**
```
Invalidation patterns:

Full invalidation (safe, wasteful):
  Cache.clear_all()

Partial invalidation (smart):
  Identify affected queries:
  ├── Queries with "status" filter → invalidate these
  ├── Leave "category" filter caches intact
  └── Faster cache rebuild
```

---

## Part 5: Search Pipeline Architecture

### 5.1 Query Parsing and Analysis Pipeline

**Multi-Stage Pipeline:**
```
User Query
    ↓
[Stage 1: Parse]
    ├── Tokenize query: "quick brown fox" → ["quick", "brown", "fox"]
    ├── Parse operators: (term OR term) AND (NOT term)
    └── Build AST (abstract syntax tree)
    ↓
[Stage 2: Analyze]
    ├── Lowercase: "Quick" → "quick"
    ├── Stemming: "running" → "run"
    └── Stop word removal (optional)
    ↓
[Stage 3: Retrieval]
    ├── Look up each term in inverted index
    └── Combine postings lists (AND, OR, NOT)
    ↓
[Stage 4: Ranking]
    ├── Score each document (BM25, cosine similarity)
    └── Sort by relevance
    ↓
[Stage 5: Presentation]
    ├── Format results
    ├── Include snippets/highlights
    └── Return to user
```

### 5.2 Multi-Stage Retrieval (L0 → L1 → L2 Ranking)

Modern search systems use multi-stage retrieval to balance relevance and latency.

**L0 Ranking (Candidate Generation - Cheap):**
```
Goal: Generate ~10,000 candidate documents quickly
Algorithm: Fast, simple metrics

├── Inverted index lookup (milliseconds)
├── Simple scoring: TF-IDF, BM25
├── Light ML models (small, fast)
└── Result: Top 10,000 documents

Cost: Few milliseconds
Latency budget: 10-50 ms
```

**L1 Ranking (Calibration and Coarse Ranking - Medium):**
```
Goal: Reduce to ~1,000 relevant documents
Algorithm: Moderate complexity

├── Take L0 candidates
├── Apply moderate-complexity signals:
│   ├── User history
│   ├── CTR (click-through rate)
│   └── Engagement metrics
├── Calibrate diverse candidate sources
└── Result: Top 1,000 documents

Cost: Moderate computation
Latency budget: 50-200 ms
```

**L2 Ranking (Final Ranking - Expensive):**
```
Goal: Produce final ranked results
Algorithm: Complex, heavy models

├── Take L1 candidates
├── Apply heavy ML models:
│   ├── Deep neural networks
│   ├── Pairwise learning-to-rank
│   ├── Contextual personalization
│   └── Multi-objective ranking
├── Multiple models, ensemble combined
└── Result: Top 100 documents

Cost: Expensive computation
Latency budget: 200-500 ms
```

**LinkedIn's PYMK (People You May Know) Example:**

```
L0 Candidate Generation:
├── Graph-based: Common connections (fast degree queries)
├── Similarity-based: Embedding cosine similarity
├── Heuristic-based: Geographic proximity, school alumni
└── XGBoost light ranker → 5,000 candidates

L1 Calibration & Ranking:
├── Normalize diverse sources (graph, similarity, heuristic)
├── Apply calibration weights
├── XGBoost heavy ranker
└── Result: 500 candidates

L2 Heavy Ranking:
├── Multiple deep learning models:
│   ├── Connection likelihood prediction
│   ├── Message response prediction
│   ├── Engagement prediction
│   └── Long-term value prediction
├── Weighted ensemble combination
└── Final ranking: Top 100 recommendations
```

**End-to-End Latency Budget:**
```
User query arrives
    ↓ (5ms)
L0 Candidate Generation (10-50ms)
    ├── Inverted index lookup: 2-5ms
    ├── BM25 scoring: 5-10ms
    └── Light model: 3-10ms
    ↓ (5ms)
L1 Ranking (50-150ms)
    ├── Calibration: 10-30ms
    ├── Medium model: 40-100ms
    └── Merge/sort: 5-10ms
    ↓ (5ms)
L2 Ranking (100-300ms)
    ├── Feature extraction: 30-50ms
    ├── Multiple models: 50-200ms
    └── Ensemble: 10-30ms
    ↓ (5ms)
Return to client (5ms)
────────────────────────
Total: 180-530 ms (p50: ~250ms)
```

### 5.3 Feature Extraction for ML Ranking

**Online Feature Computation:**
```
Query-document pair → Feature extractor → 50-200 features

Example features:
├── Query-document matching:
│   ├── Query term coverage (% of query matched)
│   ├── Exact phrase match (boolean)
│   └── All terms in title (boolean)
│
├── Document quality:
│   ├── Freshness (days old)
│   ├── Authority score (PageRank)
│   └── Spam score (0-1)
│
├── Query-user context:
│   ├── User search history similar? (boolean)
│   ├── User CTR on similar docs (0-1)
│   └── User location match (boolean)
│
└── Ranking signals:
    ├── BM25 score
    ├── TF-IDF vector cosine
    └── Word2vec embedding distance
```

**Lookup Table Features:**
```
Feature: "document_authority"
Precomputed: PageRank scores stored in separate lookup table

At ranking time:
  Query: "machine learning"
  Candidate: doc_id = 12345
  Lookup: feature_table["pagerank"][12345] → 0.95

Cost: Single table lookup (~nanoseconds)
Not recomputed per query
```

### 5.4 Online vs. Offline Feature Computation

**Offline Feature Computation (Batch):**
```
Schedule: Runs every night (1-4 AM)
Latency requirement: None (hours acceptable)

Features computed:
├── PageRank (slow, graph-based)
├── Document embeddings (deep models)
├── Authority scores
└── Popularity metrics

Storage: Precomputed values stored in fast lookup tables

Query time:
  → Simple table lookups (nanoseconds)
  → Negligible latency impact
```

**Online Feature Computation (Real-time):**
```
At query/ranking time: Compute features immediately

Features:
├── Query term coverage (fast calculation)
├── Freshness (current timestamp - doc update time)
├── User-specific signals (fast DB lookup)

Cost: Must be fast (<10ms per feature)
Trade-off: Lose complex features (slow models)
```

**Hybrid Approach (Practical):**
```
Fast path (L0, L1):
  ├── Use offline precomputed features
  └── Table lookups only

Slow path (L2):
  ├── Include both offline + online features
  ├── Can afford more computation
  └── Better ranking accuracy

Result: Latency-optimized, accurate
```

### 5.5 A/B Testing Infrastructure for Search

**Canary Ranking (Gradual Rollout):**
```
Old ranking algorithm: 100% of traffic
                        ↓ Deploy new algorithm
New ranking: 0% → 5% → 10% → 25% → 50% → 100%

At each step: Monitor quality metrics
├── Click-through rate (CTR)
├── Dwell time on results
├── Zero-result rate (queries with no results)
└── Revenue/conversion impact

If regression detected: Rollback immediately
If improvement detected: Continue rollout
```

**A/B Test Structure:**
```
Control group (50%):    Old ranking algorithm
Treatment group (50%):  New ranking algorithm

User assignment: Sticky hash (same user always in same group)
  user_id = "alice"
  group = hash("alice" + "test_v2") % 100
  if group < 50: control_group
  else: treatment_group

Results (after 1 week):
├── Control: CTR = 0.045, dwell = 120s
├── Treatment: CTR = 0.048, dwell = 125s
├── Improvement: +6.7% CTR (statistically significant)
└── Decision: Ship to production
```

---

## Part 6: Performance Optimization

### 6.1 Index Compression: Posting List Encoding

Compression reduces disk space and improves cache hit rates.

**VInt Encoding (Variable-length integers):**
```
Small numbers: 1 byte
Medium numbers: 2-4 bytes
Large numbers: Up to 5 bytes

Number 5: Encoded as [0x05] (1 byte)
Number 300: Encoded as [0xAC, 0x02] (2 bytes)
Number 50000: Encoded as [0xD0, 0x86, 0x03] (3 bytes)
```

**Posting List Compression:**
```
Document IDs (uncompressed):
[10, 15, 25, 50, 75, 100, 150, 200, ...]

Delta encoding (compress gaps):
[10, 5, 10, 25, 25, 25, 50, 50, ...]
(smaller numbers compress better)

VInt compressed:
[0x0A, 0x05, 0x0A, 0x19, 0x19, 0x19, 0x32, 0x32, ...]

Compression ratio: Original 8 bytes (uint64) → 1-2 bytes per ID
Improvement: 4-8x space reduction
```

**DocValue Encoding (For Sorting/Aggregation):**
```
Field: "user_age"
Values: [25, 30, 25, 18, 50, 25, 42, ...]

Bit-packing: All values fit in 6 bits (0-63)
├── Store bitmask indicating which bits used
├── Pack multiple values per byte/word
└── Decompress on access

Compression: 8 bytes/value → 0.75 bytes/value (10.7x)
```

### 6.2 Query Optimization: Early Termination

Early termination stops scoring documents when top-K guaranteed.

**Basic Early Termination:**
```
Query: Find top-100 documents for query
Scoring: BM25 (decreasing order)

Assumption: Document IDs are ordered by frequency
            High-frequency terms appear first

Scoring loop:
  for each matching document (ordered):
    score = calculate_BM25(doc, query)
    if score < minimum_score_for_top_100:
      break  // Rest will score even lower

Result: Stop after 50K docs instead of 500M docs
```

**WAND Algorithm (Weak AND):**
```
Query: term_A AND term_B AND term_C

PostingLists:
├── term_A: [2, 5, 8, 12, ...] with max_score = 8.5
├── term_B: [1, 3, 8, 15, ...] with max_score = 7.2
└── term_C: [5, 8, 10, 20, ...] with max_score = 6.1

Advance term lists to common document:
  ├── Find smallest max_score: 6.1 (term_C)
  ├── If current doc's max possible score < top_K_threshold:
  │   └── Skip documents until sum ≥ threshold
  └── Dramatically reduces score computations
```

**MaxScore Algorithm:**
```
Similar to WAND but:
├── Maintains per-term upper bounds
├── Better at skipping documents
└── Requires posting lists sorted by impact score

Performance: 2-10x faster than WAND
Trade-off: More setup cost, better skipping
```

### 6.3 Top-K Retrieval Without Scoring All Documents

Scenarios: Billions of documents, top-100 only needed.

**Block-Max Index:**
```
Posting list organized in 4KB blocks:
├── Block 1: [doc_1, doc_2, doc_3, doc_4, doc_5]
│   max_score: 9.5
├── Block 2: [doc_6, doc_7, doc_8, doc_9, doc_10]
│   max_score: 8.2
└── Block 3: [doc_11, doc_12, ...]
    max_score: 7.1

Scoring:
  1. Check block 1 max_score (9.5) vs current top_K_threshold (say 5.0)
  2. If max_score > threshold: Score documents in block
  3. If max_score ≤ threshold: Skip entire block

Result: Skip 70-80% of documents (no scoring needed)
```

### 6.4 Memory Mapping vs. Heap Storage

**Memory Mapping (Preferred for large indices):**
```
Index file on disk
    ↓
Mapped into virtual memory address space
    ↓
OS handles disk ↔ RAM transfers (page faults)
    ↓
Java code reads mapped memory like RAM
```

**Advantages of Mmap:**
```
✓ Automatic paging (OS manages memory)
✓ Scales to 100+ GB indices
✓ Multiple processes can share (reduced memory)
✓ Cache-friendly (OS optimizes page loading)
✗ Unpredictable latency (page faults can stall)
```

**Heap Storage (Java GC):**
```
Everything in Java heap:
├── Index data in arrays/collections
├── GC manages memory
└── All accesses in RAM (no page faults)

Advantages:
✓ Predictable latency (no page faults)
✓ Faster for small indices (<20 GB)

Disadvantages:
✗ GC pauses (100-500 ms possible)
✗ High memory overhead (2-3x data size)
✗ JVM per process (can't share across processes)
```

**Production Recommendation:**
```
Elasticsearch: Uses Mmap for 80% of systems
├── Reason: Scales better, efficient OS paging
├── Tuning: Lower heap for OS page cache
└── Trade-off: Accept rare page fault latencies

High-frequency trading: Uses heap storage
├── Reason: Must avoid any latency unpredictability
├── Cost: Requires <40 GB indices (SSD helps)
└── Trade-off: Higher memory footprint
```

### 6.5 SSD-Optimized Index Storage

Modern indices leverage SSDs for performance.

**Sequential I/O Preferred:**
```
Random I/O on HDD: 100-200 IOPS
Sequential I/O on HDD: 100-150 MB/s

Random I/O on SSD: 10,000+ IOPS
Sequential I/O on SSD: 200-600 MB/s

Index organization: Keeps sequential reads where possible
├── Posting lists: Stored sequentially (delta-encoded)
├── Docvalues: Stored in column-oriented format
└── Avoid random access (expensive)
```

**SSD-Specific Optimizations:**
```
Write amplification reduction:
├── Batch writes together (fewer page rewrite cycles)
├── Use appropriate block size (4KB for SSD)
└── Avoid excessive updates (compaction preferred)

Cache optimization:
├── Smaller segment size (80% SSD performance on reads)
├── Keep hot indices on SSD, cold on HDD (tiering)
└── Monitor wear (SSDs have limited write cycles)
```

### 6.6 GPU-Accelerated Search

GPUs accelerate specific search operations.

**GPU-Friendly Operations:**
```
✓ Vector similarity search (embedding cosine similarity)
  - Dense matrix operations (thousands in parallel)
  - 10-100x speedup possible

✓ Batch scoring (rank 10,000 candidates)
  - Score all candidates in parallel
  - 5-20x speedup

✗ Single-document scoring
  - GPU launch overhead > speedup
  - CPU faster for singleton operations

✗ Complex filters
  - Irregular access patterns
  - Not SIMD-friendly
```

**GPU Architecture for Search:**
```
Incoming queries
    ↓
Batch queries (wait up to 100ms)
    ↓
Transfer to GPU
    ↓
GPU batch-scores 10,000 documents in parallel
    ↓
Transfer results back to CPU
    ↓
Merge and return results

Throughput: 1000 queries/sec (batched)
Latency: 100ms added (wait time)
Use case: High-throughput, latency-tolerant (recommendations, discovery)
```

---

## Part 7: Data Pipeline for Search

### 7.1 ETL: From Primary Database to Search Index

**Extract-Transform-Load Pipeline:**
```
Source Database (PostgreSQL, MySQL)
    ↓ [Extract]
   Raw data extracted
    ↓ [Transform]
   Normalize, clean, enrich
    ↓ [Load]
   Elasticsearch cluster
    ↓
   Search index ready
```

**Batch ETL (Daily):**
```
Scheduled job: 2:00 AM - 4:00 AM

1. Extract phase:
   - Full table scan from primary DB
   - 5-50 million rows extracted

2. Transform phase:
   - Normalize dates, formats
   - Enrich with related data (joins)
   - Apply business rules
   - Tokenize text fields

3. Load phase:
   - Bulk insert into Elasticsearch
   - Build inverted indices
   - Optimize index segments

Advantages: Simple, high throughput
Disadvantages: Stale data (up to 24 hours), index unavailable during rebuild
```

### 7.2 Change Data Capture (CDC) for Real-Time Sync

CDC captures database changes and propagates to search index in near real-time.

**CDC Architecture:**
```
Source Database (PostgreSQL)
    ↓ [CDC log reader]
   Write-Ahead Log (WAL)
    ↓ [Debezium Connector]
   Kafka Topic
    ↓ [Stream Processor: Flink]
   Elasticsearch Index
    ↓
   Real-time sync (milliseconds)
```

**Change Types Captured:**
```
INSERT: New document added
  1. Index document in search

UPDATE: Document modified
  1. Determine changed fields
  2. Update search document
  3. Reindex if analysis fields changed

DELETE: Document removed
  1. Delete from search index
```

**Implementation Details:**
```
Debezium + Kafka + Flink:

1. Debezium reads PostgreSQL WAL
   └── Captures every INSERT, UPDATE, DELETE

2. Published to Kafka topics
   └── Fault-tolerant, distributed log

3. Flink stream processor
   ├── Consume Kafka events
   ├── Map to Elasticsearch operations
   └── Bulk index to ES

4. Elasticsearch index updated
   └── Real-time visibility (1-5 second lag)
```

### 7.3 Schema Evolution and Index Migration

Handling schema changes without downtime.

**Zero-Downtime Migration:**
```
Old index: my_index_v1
├── Schema: [title, description, category]

New schema needed: [title, description, category, tags, rating]

Process:
1. Create new index: my_index_v2
2. Start dual-writes:
   ├── Write to my_index_v1 (continue serving)
   └── Write to my_index_v2 (new schema)
3. Backfill: Copy data from v1 → v2, transform
4. Verify: Compare query results on v1 and v2
5. Switch: Point searches to v2
6. Cleanup: Delete v1 (after retention period)

Downtime: 0 seconds
```

**Index Alias Pattern:**
```
Alias: "myapp"
  ↓ Points to →
Index: my_index_v2

# Queries use alias
GET /myapp/_search

# Repoint alias during migration
POST /_aliases
{
  "actions": [
    {"remove": {"index": "my_index_v1", "alias": "myapp"}},
    {"add": {"index": "my_index_v2", "alias": "myapp"}}
  ]
}

Result: Atomic switch from v1 to v2 (milliseconds)
```

### 7.4 Handling Deletes and Updates

**Delete Operations:**
```
Delete from database:
  ├── Propagate to search index (CDC)
  ├── Remove document from index
  └── Delete reverse references

Soft delete (preferred):
  ├── Set flag: is_deleted = true
  ├── Filter out in queries
  ├── Easier to undelete if needed
  └── No full reindex required
```

**Update Operations:**
```
Update single field:

Option 1: Full document reindex
  ├── Fetch document
  ├── Update field
  ├── Reindex (analyze, tokenize)
  └── Slow (milliseconds per update)

Option 2: Partial update (if search doesn't need reanalysis)
  ├── Update numeric field directly
  ├── No re-tokenization needed
  └── Fast (microseconds per update)

Real scenario: Update price = fast, update description = full reindex
```

### 7.5 Data Freshness SLA Management

Managing expectations around data freshness.

**SLA Definition:**
```
99.9% of data updated within 5 minutes:
├── Capture change: <1 sec
├── CDC pipeline: <500ms
├── Index ingest: <3 sec
└── Search visible: <1 sec
Total: <5 seconds (p99)

Monitoring:
├── Max lag metric: max(current_time - last_update_timestamp)
├── Alert if > 5 minutes
└── Automate remediation (restart pipeline)
```

**Tiered Freshness:**
```
Critical data (pricing, inventory):
  ├── Update requirement: <10 seconds
  ├── Method: CDC + real-time indexing

Important data (product descriptions):
  ├── Update requirement: <1 hour
  ├── Method: CDC with batched indexing

Non-critical data (reviews, ratings):
  ├── Update requirement: <24 hours
  ├── Method: Batch ETL (nightly)
```

---

## Part 8: Monitoring & Observability

### 8.1 Search Latency Percentiles

Latency distribution matters more than averages.

**Percentile Understanding:**
```
p50 (50th percentile): Median latency
  → 50% of requests faster, 50% slower

p95 (95th percentile): 95% faster, 5% slower
  → User experience dominated by slow requests

p99 (99th percentile): 99% faster, 1% slower
  → Worst user experience (outliers)

Example:
  p50: 10ms
  p95: 25ms
  p99: 500ms

Interpretation:
  ├── Median request: 10ms (fast)
  ├── But 1% of users experience: 500ms (50x slower!)
  ├── This 1% dominates user complaints
  └── Average would hide this problem
```

**Monitoring Dashboard:**
```
Query latency histogram:
├── p50: 12ms ✓
├── p95: 45ms ✓
├── p99: 200ms ✗ (over threshold)
├── p99.9: 500ms ✗✗ (high outliers)

Alert triggers:
├── IF p99 > 200ms for 5 min → PAGE
├── IF p95 > 100ms for 10 min → WARN
```

### 8.2 Indexing Throughput Monitoring

Track indexing performance and bottlenecks.

**Key Metrics:**
```
Documents indexed per second:
├── Target: 10,000 docs/sec
├── Actual: 8,500 docs/sec (85% of target)
├── Bottleneck: Identify cause

Index size growth:
├── Expected: 1 GB/day
├── Actual: 1.2 GB/day (120%)
├── Investigation: More documents or larger documents?

Segment count:
├── Current: 127 segments
├── Target: 10-30 segments
├── Action: Trigger merge (large searc overhead)
```

**Indexing Bottleneck Analysis:**
```
Slow indexing diagnosis:

Check 1: CPU usage
  └── If high: Tokenization/analysis bottleneck

Check 2: Disk I/O
  └── If high: Segment flushing bottleneck (increase refresh interval)

Check 3: Network (if distributed)
  └── If high: Replication lag (increase batch size)

Check 4: Garbage collection
  └── If frequent GC pauses: Heap pressure (more shards needed)
```

### 8.3 Query Error Rates and Circuit Breakers

Graceful degradation under failure.

**Error Rate Monitoring:**
```
Target error rate: <0.1%
├── Timeout errors: <0.05%
├── Query syntax errors: <0.02%
├── Shard not available: <0.01%

If error rate exceeds threshold:
├── Page on-call engineer
├── Execute fallback strategy
└── Degrade gracefully
```

**Circuit Breaker Pattern:**
```
Circuit breaker states:

CLOSED (normal):
  ├── Requests flow through normally
  └── Monitor error rate

OPEN (circuit tripped):
  ├── Error rate exceeded threshold
  ├── Immediately reject requests
  └── Return fallback response (cached results, default UI)

HALF_OPEN (recovery attempt):
  ├── After 30 seconds, allow test request
  ├── If succeeds: Return to CLOSED
  └── If fails: Return to OPEN

Benefit: Fail fast, prevent cascading failures
```

### 8.4 Search Quality Dashboards

Monitoring search relevance and user satisfaction.

**Key Quality Metrics:**
```
Click-through rate (CTR):
  ├── Clicks on search results / total searches
  ├── Target: 30-50% (vary by domain)
  ├── Regression: Indicates ranking issues

Zero-result rate:
  ├── Searches returning no results / total
  ├── Target: <5% (minimize)
  ├── High rate: Indicate coverage issues

Dwell time:
  ├── Time user spends on result before returning
  ├── Target: >60 seconds (relevance signal)
  ├── Drop indicates poor ranking

Bounce rate:
  ├── Users immediately returning to search
  ├── Target: <20%
  ├── High: Results not matching intent
```

**Heatmaps:**
```
Position bias: Users tend to click higher positions

Position 1: 40% click rate
Position 2: 25% click rate
Position 3: 15% click rate
Position 4: 12% click rate
Position 5: 8% click rate

After ranking change: Position 1 still dominates
  → Improvement attributable to better ranking, not position

Analysis: Compare expected vs. actual click distributions
```

### 8.5 Alerting Thresholds

Defining actionable alert levels.

**Alert Severity Levels:**
```
CRITICAL (Page immediately):
├── Error rate > 1%
├── p99 latency > 500ms
├── Index unavailable (0 shards available)
└── Requires immediate action

WARNING (Investigate within 30 minutes):
├── Error rate > 0.5%
├── p95 latency > 200ms
├── Segment count > 100
└── Possible issue, monitor trend

INFO (Log for analysis):
├── Error rate > 0.1%
├── p50 latency > 50ms
├── Segment merge running
└── Normal operation info
```

**False Positive Reduction:**
```
Bad alert: Trigger on any spike
  └── Results: 100 pages/week, alert fatigue

Good alert: Require sustained threshold
  └── Rule: Trigger if p99 > 500ms for 5+ minutes
  └── Result: Only real issues alert

Smart alert: Account for traffic patterns
  └── Peak hours: higher threshold
  └── Off-hours: lower threshold
  └── Weekends: different baseline
```

---

## Architecture Pattern Summary

### Single-Node Search System

```
┌─────────────────┐
│  Query Input    │
└────────┬────────┘
         │
    ┌────▼───────────────────┐
    │  Query Parser          │
    │  & Analysis            │
    └────┬───────────────────┘
         │
    ┌────▼───────────────────┐
    │  Inverted Index        │
    │  (In-Memory)           │
    └────┬───────────────────┘
         │
    ┌────▼───────────────────┐
    │  BM25 Scorer           │
    │  & Ranking             │
    └────┬───────────────────┘
         │
    ┌────▼───────────────────┐
    │  Result Formatting     │
    └────┬───────────────────┘
         │
    ┌────▼───────────────────┐
    │  Results to Client     │
    └──────────────────────────┘

Limitations:
├── No high availability
├── No horizontal scaling
└── Limited to single machine capacity
```

### Distributed Search System (Planet-Scale)

```
┌──────────────────────────────────────────────────────────────┐
│                    Client Applications                        │
└───────────────────────────┬──────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Query Router   │
                    │  (Coordinator)  │
                    └───────┬────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
       ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
       │ Shard 1 │     │ Shard 2 │     │ Shard 3 │
       │         │     │         │     │         │
       ├─────────┤     ├─────────┤     ├─────────┤
       │ Primary │     │ Primary │     │ Primary │
       │         │     │         │     │         │
       ├─────────┤     ├─────────┤     ├─────────┤
       │Replica 1│     │Replica 1│     │Replica 1│
       │Replica 2│     │Replica 2│     │Replica 2│
       └────┬────┘     └────┬────┘     └────┬────┘
            │               │               │
            └───────────────┼───────────────┘
                            │
                    ┌───────▼────────┐
                    │ Merge & Sort   │
                    │ Results        │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Return Results │
                    └────────────────┘

Features:
├── Fault tolerance (replicas)
├── Horizontal scaling (shards)
├── Load balancing (replicas)
├── Real-time availability
└── Planet-scale (100+ nodes)
```

---

## Production Configuration Examples

### Elasticsearch Cluster Configuration

```yaml
cluster:
  name: production-search-cluster
  max_shards_per_node: 1000

node:
  name: node-1
  roles: [master, data, ingest]

discovery:
  seed_hosts: ["node-1", "node-2", "node-3"]
  type: seed_providers

indices:
  memory:
    index_buffer_size: 30%

search:
  max_open_scroll_contexts: 500

http:
  port: 9200
  max_content_length: 100mb
```

### Index Configuration (High Write Throughput)

```json
{
  "settings": {
    "number_of_shards": 10,
    "number_of_replicas": 2,
    "refresh_interval": "30s",
    "index.codec": "best_compression",
    "index.store.type": "niofs"
  },
  "mappings": {
    "properties": {
      "timestamp": {
        "type": "date"
      },
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "category": {
        "type": "keyword"
      },
      "price": {
        "type": "scaled_float",
        "scaling_factor": 100
      }
    }
  }
}
```

### Monitoring Configuration

```json
{
  "monitoring": {
    "latency_slo": {
      "p50_ms": 20,
      "p95_ms": 100,
      "p99_ms": 200
    },
    "alerts": [
      {
        "name": "high_error_rate",
        "condition": "error_rate > 0.01",
        "duration": "5m",
        "severity": "critical"
      },
      {
        "name": "high_latency_p99",
        "condition": "p99_latency_ms > 500",
        "duration": "5m",
        "severity": "critical"
      }
    ]
  }
}
```

---

## Conclusion

Search system architecture spans from simple inverted indices to distributed planet-scale systems handling billions of documents. Key principles:

1. **Start simple**: Inverted index + BM25 handles most cases
2. **Scale horizontally**: Sharding, replication, coordination
3. **Optimize intelligently**: Compression, early termination, caching
4. **Monitor obsessively**: Latency percentiles, error rates, quality
5. **Evolve gradually**: Batch → CDC, single-stage → multi-stage ranking
6. **Test continuously**: A/B testing for ranking changes

The best architecture depends on specific requirements: freshness, scale, latency, accuracy, cost. Elasticsearch, Solr, OpenSearch, and proprietary systems at major tech companies all implement these patterns with different trade-offs optimized for their workloads.

---

## References

- [Inverted Index Architecture (Medium)](https://satyadeepmaheshwari.medium.com/inverted-index-the-backbone-of-modern-search-engines-8bfd19a9ff75)
- [Elasticsearch Distributed Architecture (Elastic Docs)](https://www.elastic.co/docs/deploy-manage/distributed-architecture/clusters-nodes-shards)
- [Near Real-Time Search (Elastic)](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search)
- [Tokenization and Stemming (IBM)](https://www.ibm.com/think/topics/stemming-lemmatization)
- [Query Caching and Bitsets (Elastic Blog)](https://www.elastic.co/blog/elasticsearch-caching-deep-dive-boosting-query-speed-one-cache-at-a-time)
- [Multi-Stage Ranking (LinkedIn Engineering)](https://www.linkedin.com/blog/engineering/recommendations/building-a-large-scale-recommendation-system-people-you-may-know)
- [Change Data Capture (Confluent)](https://www.confluent.io/learn/change-data-capture/)
- [Index Compression (Stanford NLP)](https://nlp.stanford.edu/IR-book/pdf/05comp.pdf)
- [Observability and Monitoring (Railway)](https://blog.railway.com/p/using-logs-metrics-traces-and-alerts-to-understand-system-failures)
- [Write-Ahead Logging (Architecture Weekly)](https://www.architecture-weekly.com/p/the-write-ahead-log-a-foundation)
