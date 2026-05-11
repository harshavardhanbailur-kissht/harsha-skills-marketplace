# Search Caching, Edge Computing, and Performance Optimization: Comprehensive Reference

**Last Updated:** March 1, 2026

## Table of Contents

1. [Search Result Caching](#search-result-caching)
2. [Index Caching Strategies](#index-caching-strategies)
3. [Edge and CDN Search](#edge-and-cdn-search)
4. [Redis for Search](#redis-for-search)
5. [Embedding and Vector Caching](#embedding-and-vector-caching)
6. [Performance Patterns](#performance-patterns)
7. [Latency Budget Management](#latency-budget-management)
8. [Pre-computation Strategies](#pre-computation-strategies)
9. [Benchmarking Search Performance](#benchmarking-search-performance)
10. [Cost Optimization](#cost-optimization)

---

## Search Result Caching

### Overview

Search result caching is one of the most effective techniques for improving user-facing search latency. By storing previously computed results, systems can serve frequent queries with near-instant response times. However, cache management introduces complexity around freshness guarantees, invalidation strategies, and cache key design.

### Query Result Caching Strategies

#### Fixed TTL (Time-To-Live)

Fixed TTL is the simplest and most widely used approach for cache invalidation. Cached search result pages are associated with a fixed time-to-live (TTL) value to bound the staleness of search results presented to users. Results automatically expire after a specified duration, at which point the query must be re-evaluated against the current index.

**Advantages:**
- Simple to implement
- Predictable memory usage
- Low operational overhead

**Disadvantages:**
- Cannot adapt to index update frequency
- May serve stale results for frequently-updated content
- Wastes cache space on infrequently-accessed results that don't change

#### Adaptive TTL Strategies

Research has demonstrated that [Adaptive Time-to-Live Strategies for Query Result Caching](https://link.springer.com/chapter/10.1007/978-3-642-28997-2_34) can significantly improve cache effectiveness. Rather than using a fixed TTL for all queries, adaptive approaches set TTL values on a per-query basis:

- **Query popularity-based TTL**: High-traffic queries receive longer TTL, reducing unnecessary re-computation
- **Content change rate-based TTL**: Queries over frequently-updated data receive shorter TTL
- **Temporal patterns**: TTL adjusted based on time-of-day or seasonality patterns
- **Predictive approaches**: ML models predict which queries are likely to have stale results

Studies show selective invalidation can lower unnecessary query evaluations by up to 30% while maintaining similar freshness compared to baseline fixed-TTL schemes.

#### Timestamp-Based Invalidation

[Timestamp-based cache invalidation](https://www.cl.cam.ac.uk/~ey204/teaching/ACS/R212_2015_2016/papers/alici_sigir_2011.pdf) uses generation timestamps to detect when cached results become stale due to index updates.

**Mechanism:**
- Maintain generation timestamp for each cached query result
- Track update times of posting lists and documents
- Compare result generation time with relevant document/posting list update times
- Invalidate cache entry if any contributing data has been modified

**Key Insight:** Index updates only affect cached results for queries that match updated documents. By tracking which documents contributed to each result, systems can invalidate only affected cached entries rather than clearing the entire cache.

**Benefits:**
- Reduces cache invalidation churn
- Balances freshness with cache hit rate
- Particularly effective for indexes with non-uniform update patterns (e.g., news sites where some content updates frequently while other content is static)

### Cache Key Design

Cache keys determine whether multiple queries can share the same cached result. Poor key design leads to cache fragmentation; overly aggressive key normalization reduces hit rates.

#### Query Normalization

Query normalization transforms semantically equivalent queries into identical cache keys:

1. **Whitespace normalization**: Collapse multiple spaces, tabs, newlines
2. **Case normalization**: Convert to consistent case (usually lowercase for text queries)
3. **Operator normalization**: Standardize boolean operators (AND, OR, NOT)
4. **Query expansion equivalence**: Recognize that `title:query` and `query` may be semantically similar depending on configuration
5. **Stop word handling**: Decide whether to include/exclude stop words in cache key
6. **Synonym resolution**: Map query terms to canonical forms (optional, impacts hit rate vs. overhead)

#### Hierarchy and Multi-Level Keys

Effective cache key design often uses hierarchical keys:

```
cache_key = f"{index_version}:{query_hash}:{filter_hash}:{sort_hash}:{user_context_hash}"
```

- **Index version**: Changes when index is rebuilt or incompatible changes occur
- **Query hash**: Normalized query terms and operators
- **Filter hash**: Applied filters (facets, ranges, etc.)
- **Sort hash**: Ranking/sorting preferences
- **User context hash**: Optional personalization signals

This approach allows partial cache sharing while maintaining correctness.

#### Partial Result Caching

For queries returning large result sets, caching individual result pages or result batches provides finer-grained control:

- Cache page 0-20 with one key, page 20-40 with another
- Allows queries with different result window offsets to share a common prefix
- Reduces memory overhead for result sets where users rarely view beyond first few pages
- Can cache top-K results (typically K=100) and derive paginated results from cache

### Cache Invalidation Strategies

#### Event-Driven Invalidation

Event-driven invalidation triggers cache updates in response to specific system events, providing real-time data consistency by invalidating caches immediately when underlying data changes:

1. **Document update events**: When a document is indexed/updated, invalidate queries matching that document
2. **Bulk update events**: When bulk indexing completes, invalidate queries potentially affected by new/modified documents
3. **Index operation events**: On index refresh, optimize, or merge operations
4. **Configuration changes**: When query processing configuration changes (analyzers, filters, etc.)

**Implementation Pattern:**
```
Index Write Operation
  → Generate invalidation events
    → Identify affected cached query keys
      → Invalidate cache entries
        → Return to user with fresh results
```

#### TTL + Invalidation Hybrid

Modern systems often combine TTL with selective invalidation:

- Short default TTL (e.g., 30 seconds) catches most index updates
- Explicit invalidation handles critical updates requiring immediate propagation
- Reduces stale results while limiting invalidation overhead
- Balances consistency requirements with performance needs

### Freshness-Latency Trade-offs

The choice of caching strategy represents a fundamental trade-off:

| Strategy | Latency | Freshness | Cache Hit Rate | Complexity |
|----------|---------|-----------|-----------------|------------|
| No caching | Baseline | 100% fresh | N/A | Low |
| Fixed 1m TTL | 100x reduction | Possibly stale | 80-90% | Low |
| Adaptive TTL | 80-100x reduction | 95%+ fresh | 85-95% | Medium |
| Event invalidation | 50-100x reduction | Near real-time | 85-90% | High |
| Hybrid approach | 80-100x reduction | Near real-time | 90%+ | High |

---

## Index Caching Strategies

### Overview

Indexes in search engines like Elasticsearch are memory-intensive structures. Effective caching at the index level is crucial for performance. Modern search systems use a multi-tiered caching strategy spanning OS page cache, memory-mapped files, and JVM heap memory.

### In-Memory vs. Disk-Based Indexes

#### In-Memory Indexes

Complete indexes loaded in RAM provide lowest latency:
- **Latency:** Sub-millisecond queries possible
- **Memory cost:** High (100GB+ for large indexes)
- **Use case:** Real-time applications where sub-100ms latency is critical

#### Disk-Based with OS Page Cache

Most production systems rely on memory-mapped (mmap) indexes with OS page cache:
- **Latency:** 1-50ms for index hits, longer for page misses
- **Memory cost:** Much lower than in-memory (only hot pages in RAM)
- **Use case:** Most production search workloads

### Memory-Mapped Files (mmap)

#### How mmap Works

Memory mapping allows files to be accessed like in-memory arrays while the OS handles actual memory management:

1. File is mapped to process address space
2. Reading mapped address triggers page fault if page not in RAM
3. OS loads page from disk into physical RAM
4. Process continues with zero-copy access
5. OS may page out data if memory pressure occurs

#### Lucene's HybridDirectory

[Lucene's HybridDirectory](https://github.com/elastic/elasticsearch/issues/27748) class decides which index files to memory-map based on file extensions:

```
Index File Types:
├── Highly accessed (mmap): .cfs, .cfe, .fdt, .fdx
├── Sequential read (.tim, .tip): NIO if seeking, else mmap
├── Metadata (.segments): Always NIO
└── Deleted docs (.liv): Tiny, mmap for performance
```

This hybrid approach balances performance (mmap for frequently accessed metadata) with resource efficiency.

#### mmap Challenges and Limitations

[Current mmap limitations in Elasticsearch](https://github.com/elastic/elasticsearch/issues/27748) include:

1. **Read-ahead overhead**: Linux kernel automatically reads 128KB+ of data in anticipation of sequential access. For random index access patterns, this wastes page cache space by loading unneeded data.

2. **Missing madvise() support**: Linux offers `madvise()` hints to control kernel read-ahead behavior (MADV_RANDOM, MADV_SEQUENTIAL), but JVM doesn't expose these controls.

3. **Page cache competition**: OS competes between mmap read-ahead and actual needed data, causing memory pressure and reduced efficiency.

4. **Cache coherency**: Multiple Lucene readers accessing the same mmap index must coordinate, potentially causing false sharing.

### OS Page Cache

The operating system's page cache (also called filesystem cache) is the primary caching mechanism for disk-based search indexes:

#### How Page Cache Works

```
Search Query
  ↓
Lucene Reader requests index data
  ↓
Does page exist in RAM?
  ├─ YES → Serve from cache (sub-microsecond)
  └─ NO  → Page fault → OS loads page from disk (10-100ms)
    ↓
Application code continues
```

#### Page Cache Tuning

**VM Pressure Tuning:**
```bash
# Linux kernel tuning for search workloads
vm.swappiness = 10          # Prefer cache over swap
vm.dirty_ratio = 15         # Don't wait too long to flush
vm.dirty_background_ratio = 5  # Start async flush earlier
```

**Benefits of larger page cache:**
- Hit rate improves exponentially with cache size
- Search latency p99 improves significantly
- Less JVM GC pressure

### JVM Heap Management for Elasticsearch

#### Recommended Heap Sizing

[Elasticsearch heap sizing best practices](https://www.elastic.co/search-labs/blog/elasticsearch-heap-size-jvm-garbage-collection):

**Golden rule:** Set heap to 50% of total system RAM, with a maximum of approximately 31GB.

```
Example: 128GB system
├─ Elasticsearch JVM heap: 31GB (50% cap, would be 64GB)
├─ OS page cache: ~97GB
└─ Other system processes: Remaining
```

**Why not 31GB?**
- JVM uses compressed object pointers (CompressedOops) up to 32GB
- Beyond 32GB, pointers expand, increasing memory usage
- 32GB is practical maximum for efficient pointer compression

#### Heap vs. Page Cache Tradeoff

Critically, [many Lucene data structures have moved from JVM heap to disk](https://www.elastic.co/blog/significantly-decrease-your-elasticsearch-heap-memory-usage), relying on the OS page cache:

| Component | Heap | Page Cache |
|-----------|------|-----------|
| Index segments | mmap | mmap + page cache |
| Fielddata | JVM | Off-heap (prefer doc values) |
| Doc values | Disk-resident | Page cache |
| Metadata | Heap | Heap (small) |

**Impact:** A smaller heap (say 16-24GB) often outperforms a larger heap (31GB) because it allows the OS to use more page cache.

#### GC Tuning for Search

```
Elasticsearch GC Configuration:
├─ Garbage collector: G1GC (default in recent versions)
├─ Max pause time: 50-200ms (lower = fewer long pauses)
├─ Heap sizing: Consistent -Xms and -Xmx
└─ Monitoring: Track full GC frequency
```

High garbage collection frequency indicates:
- Heap sized too small for workload
- Too much in-heap caching (move to off-heap alternatives)
- Memory leaks in custom code

### Multiple Cache Layers in Elasticsearch

[Elasticsearch caching deep dive](https://www.elastic.co/blog/elasticsearch-caching-deep-dive-boosting-query-speed-one-cache-one-at-a-time) identifies multiple caching layers:

1. **Request Cache**: Caches full query results in heap (per-shard)
2. **Query Cache**: Caches filter results across queries
3. **Doc Values Cache**: OS page cache for numeric field values
4. **Field Cache**: Deprecated; avoid
5. **Segment Cache**: Caches Lucene segment metadata

Each cache serves different purposes and requires different tuning strategies.

---

## Edge and CDN Search

### Overview

Traditional search architectures serve all users from centralized data centers, incurring network latency proportional to user distance. Edge computing and CDN strategies push search processing closer to users, dramatically reducing latency.

### Cloudflare Workers for Search

#### Architecture Overview

[Cloudflare Workers](https://workers.cloudflare.com/) represents a modern approach to edge computing for search:

- **Deployment**: Code deployed to 330+ global Cloudflare edge locations
- **Runtime**: V8 isolates (not containers)
- **Cold start**: <1ms (vs. 100-1000ms for Lambda)
- **Time to First Byte**: <50ms for users worldwide
- **Programming model**: JavaScript/TypeScript, WebAssembly supported

#### EdgeSearch: Full-Text Search at the Edge

[EdgeSearch](https://github.com/wilsonzlin/edgesearch) demonstrates serverless full-text search with Cloudflare Workers:

**Architecture:**
```
User Query
  ↓
Cloudflare Edge Location (nearest to user)
  ├─ Parse query in WebAssembly
  ├─ Bitwise operations on pre-computed Roaring bitmaps
  └─ Return results to user
  ↓
~30-50ms latency (vs. 200-500ms centralized)
```

**Key innovations:**
- Bitwise operations across bit sets containing document IDs
- Roaring bitmaps for space-efficient set operations
- Pre-computed result bitmaps for common queries/filters
- WebAssembly for near-native performance

**Advantages:**
- No cold starts (Isolates warm in <1ms)
- Natural distribution to edge
- Scales without managing servers
- Integrated with Cloudflare's SSL/caching

#### Cloudflare KV and Cache API

**KV Store:**
- Global key-value store replicated across all edge locations
- Automatic geographic replication of frequently-accessed data
- Eventually consistent (reads-after-writes within seconds)
- Use for: Index segments, query result bitmaps, configuration

**Cache API:**
- Write directly to local edge cache
- Sub-millisecond latency for cached objects
- Use for: Per-edge caching of hot query results, temporary data structures

### Algolia's Global Distribution

#### Distributed Search Network (DSN)

[Algolia's Distributed Search Network](https://www.algolia.com/distributed-secure/global-infrastructure) provides global search with automatic query routing:

**Architecture:**
```
User Query
  ↓
Automatic routing to nearest DSN server
  ├─ Full index replica in region 1
  ├─ Full index replica in region 2
  └─ Full index replica in region N
  ↓
Return results from nearest region
```

**Key characteristics:**
- 17 global regions covered
- Complete data replication (not just caching)
- Each region has fully-loaded indexes in memory
- Automatic query routing based on user location

#### Index Replication Architecture

Unlike traditional CDNs that cache popular content, [Algolia replicates full indexes](https://highscalability.com/the-architecture-of-algolias-distributed-search-network/):

1. **Primary cluster** performs indexing and configuration management
2. **Replica clusters** in each region:
   - Receive data after primary finishes indexing
   - Build identical indexes locally
   - Serve search queries independently
   - Guaranteed to have all data available locally

**Benefits vs. cache-based CDN:**
- No "miss" scenario requiring fallback to origin
- Consistent latency across all regions
- Better for real-time search where freshness matters
- Slightly higher infrastructure cost due to full replication

#### DSN Query Routing

Algolia's automatic query routing selects the best server based on:
- User's geographic location
- Network latency to each region
- Server health/availability
- User's configured replica preferences

Result: Users experience sub-100ms search latency globally.

### Fastly Compute@Edge

[Fastly's Compute platform](https://www.fastly.com/products/edge-compute) offers serverless edge computing:

**Specifications:**
- **Startup time**: 35.4 microseconds (Lucet WebAssembly runtime)
- **Cold starts**: Zero (workers always warm)
- **Runtime**: WebAssembly System Interface (WASI)
- **Languages**: Any WASI-supporting language (Rust, C, JavaScript, etc.)

**Search Use Cases:**
1. **Result stitching**: Combine results from multiple backend search services
2. **Query transformation**: Normalize queries before sending to backends
3. **Result filtering**: Apply user-specific filters at edge
4. **Personalization**: Inject user-specific signals for ranking

**Data Persistence:**
- Fastly KV Store for edge-side data
- Automatic replication to all edge locations
- Strong consistency within a POP

**Security Model:**
- WebAssembly sandboxing isolates each request
- Security vulnerabilities in code contained to request sandbox
- No privilege escalation possible

### Pre-computed Results at CDN

Rather than computing search results in real-time, systems can pre-compute and cache results for anticipated queries:

#### Static Result Caching

For predictable search patterns:
```
Offline (batch process):
├─ Identify top 1000 queries by volume
├─ Compute results for each query
├─ Generate result JSON
├─ Push to CDN edge locations
  ↓
Online:
├─ User query → CDN edge lookup
├─ Hit? Return cached JSON in <50ms
├─ Miss? Fall back to search backend
```

**Cache invalidation strategy:**
- Results expire on schedule (e.g., daily at 2am)
- On bulk index updates, invalidate related result sets
- Selective invalidation for results affected by doc updates

#### Dynamic Result Computation at Edge

For less predictable queries, edge functions can compute results:

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleSearch(event.request));
});

async function handleSearch(request) {
  const { query } = new URL(request.url).searchParams;

  // Check local edge cache
  const cached = await caches.default.match(`result:${query}`);
  if (cached) return cached;

  // Compute locally if possible
  if (isSimpleQuery(query)) {
    const results = await computeLocalSearch(query);
    return new Response(JSON.stringify(results));
  }

  // Fall back to origin
  return fetch(`${ORIGIN}?query=${query}`);
}
```

---

## Redis for Search

### Overview

Redis has evolved from a simple cache to a powerful search platform. RediSearch module adds full-text search capabilities, while Redis's sorted sets enable autocomplete and ranking.

### RediSearch Module

[RediSearch](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/search/) provides full-text search with inverted indexes:

**Indexing:**
```
Index (schema definition)
  ├─ Field definitions (type, tokenizer, stopwords)
  ├─ Documents (stored and indexed)
  └─ Inverted index + document metadata

Creation:
FT.CREATE products ON HASH PREFIX 1 product:
  SCHEMA
    name TEXT WEIGHT 5
    description TEXT
    category TAG
    price NUMERIC
```

**Query capabilities:**
- Full-text search with boolean operators
- Faceted search by TAG fields
- Numeric range queries
- Geospatial queries
- Aggregations and sorting

### Caching Search Results in Redis

#### String-Based Result Caching

Simple approach for caching complete result sets:

```
Key: "search:products:query:electronics:page:0"
Value: JSON array of results
TTL: 300 seconds

Query → Check Redis
  ├─ HIT → Return cached JSON
  └─ MISS → Execute search → Store in Redis → Return
```

**Advantages:**
- Simple to implement
- Redis handles expiration automatically
- JSON fast to serialize/deserialize

**Disadvantages:**
- Page boundaries don't align well (page 0-10 != page 5-15)
- Wasted memory storing overlapping results

#### Partial Result Caching with Sorted Sets

More sophisticated approach storing granular results:

```
Key: "search:results:query:electronics"
Value: Sorted Set with members = documents, scores = relevance

Members: [doc1, doc2, doc3, ...]
Scores:  [0.95, 0.87, 0.76, ...]

Pagination:
ZREVRANGE "search:results:query:electronics" 0 20
→ Returns top 20 results
```

**Benefits:**
- Single cache entry serves all pagination offsets
- Sorting already done (O(1) for top-K)
- Memory efficient (documents stored once)
- Can easily implement top-N pagination

### Autocomplete with Redis

#### Sorted Set Approach

[Redis autocomplete](https://upstash.com/blog/redis-autocomplete-popularity-ranking) using sorted sets:

```
Data structure:
  Key: "autocomplete:products"
  Type: Sorted Set
  Members: product names
  Scores: popularity/frequency scores

Building:
  ZADD autocomplete:products 100 "apple"
  ZADD autocomplete:products 95 "applesauce"
  ZADD autocomplete:products 87 "apricot"

Prefix lookup:
  ZRANGEBYLEX autocomplete:products "[app" "[app\xff"
  → Returns all items starting with "app"
  → Order by score for ranking
```

**Limitations:**
- Lexicographic range queries only
- No fuzzy matching
- Scoring fixed (can't adjust per-request)

#### RediSearch Trie-Based Approach

[RediSearch autocomplete](https://redislabs.awsworkshop.io/40_modernization/30_assisting/page_20_auto_suggestion.html) uses dedicated trie structure:

```
Advantages over sorted sets:
├─ Space efficient (no string duplication for common prefixes)
├─ Fuzzy matching support
├─ Per-term scoring flexibility
├─ Phonetic/typo-tolerance matching
└─ Can handle large catalogs without memory bloat
```

**Example:**
```
FT.SUGADD autocomplete:products 100 "apple"
FT.SUGGET autocomplete:products "app"
  → Suggestions: ["apple", "applesauce", "apricot"]
  → Scores: [100, 95, 87]
```

#### Caching Autocomplete Results

[Soulmate](https://github.com/seatgeek/soulmate) demonstrates autocomplete caching pattern:

```
Redis cache structure:
├─ Suggestion trie (permanent, loaded at startup)
├─ Result cache (expires after 10 minutes)
│  ├─ Key: "cache:suggestion:app"
│  ├─ Value: JSON array of suggestions
│  └─ TTL: 600 seconds
└─ Metrics (for optimization)

Lookup flow:
1. Check result cache
2. If miss, compute from trie
3. Store in cache
4. Return suggestions

ZINTERSTORE usage for filtering:
├─ Compute intersection of multiple suggestion sets
└─ Result = suggestions matching ALL criteria
```

### Redis for Query/Session Caching

Beyond just results, Redis caches intermediate computations:

1. **Parsed queries**: Cache query AST/parse trees
   - Key: `query:hash:parsed`
   - Value: Serialized query structure
   - Avoids re-parsing common queries

2. **Filter sets**: Cache pre-computed filter results
   - Key: `filter:category:electronics`
   - Value: Document IDs matching filter
   - Reused across multiple queries

3. **User sessions**: Cache search context
   - Key: `session:user123`
   - Value: Last query, filters, sorting preferences
   - Improves perceived responsiveness

---

## Embedding and Vector Caching

### Overview

As vector search becomes fundamental to modern search systems, caching embeddings is critical for performance. Computing embeddings is computationally expensive (requiring ML inference), so effective caching strategies directly impact system performance.

### Query Embedding Caching

#### In-Memory Embedding Cache

[LangChain's query embedding cache](https://docs.langchain.com/oss/python/integrations/text_embedding):

```python
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import RedisStore

store = RedisStore(redis_client=redis)
cache = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings,
    store,
    namespace="langchain_embeddings"
)

# First call: computes embedding and caches
embedding1 = cache.embed_query("what is vector search?")

# Second call: retrieves from cache
embedding2 = cache.embed_query("what is vector search?")
# Instant return, no ML inference
```

**Implementation options:**
1. **Redis**: Low latency, distributed, suitable for multi-service deployments
2. **Local memory**: Sub-microsecond latency, single-process only
3. **Disk (SQLite)**: Persistent across restarts, slower than memory

#### Cache Key Design for Embeddings

Embeddings must cache based on:
- **Model version**: Different models produce different embeddings
- **Input text**: Exact text match required
- **Normalization**: Consistent text preprocessing

```
cache_key = hashlib.sha256(
    f"{model_name}:{model_version}:{normalize(text)}".encode()
).hexdigest()
```

### Pre-computed Embeddings

#### Offline Embedding Pre-computation

For static documents, compute embeddings during indexing:

```
Index pipeline:
1. Document arrives
2. Tokenize and normalize
3. Compute embedding (all documents this step)
4. Store: document + embedding in index
5. Build vector index (HNSW, IVF, etc.)
```

**Processing considerations:**
- Batch documents together (improves GPU utilization)
- Pre-sort by length to minimize padding
- Use FP16 precision to reduce memory/bandwidth
- Cache intermediate results to recover from failures

#### Embedding Materialization

Store embeddings persistently with documents:

```json
{
  "id": "doc123",
  "title": "Vector Search Basics",
  "text": "...",
  "embedding": [0.1234, -0.5678, ...],  // Pre-computed
  "metadata": {...}
}
```

**Benefits:**
- Search queries skip embedding computation
- Faster vector index lookups
- Embedding version tracking (for model upgrades)

**Storage cost:**
- 1536-dim OpenAI embedding = 6.1 KB (float32)
- 1B documents = 6.1 TB storage
- Manageable with modern databases (Weaviate, Pinecone, Milvus)

### GPU Memory Management for Embeddings

#### Model Loading and Caching

Keeping models loaded in GPU memory is critical:

```python
# DON'T do this (reloads model each inference):
for query in queries:
    model = load_model()  # Seconds overhead
    embedding = model.encode(query)

# DO this (model stays in memory):
model = load_model()  # Load once
embeddings = [model.encode(q) for q in queries]  # Reuse
```

**Cold start cost:**
- Model loading: 1-5 seconds
- First inference: 100-500ms
- Subsequent inferences: 10-50ms

**Solution:** Keep frequently-used models pinned to GPU:

```python
class EmbeddingService:
    def __init__(self):
        self.model = load_model().to("cuda")  # Pinned in GPU
        self.cache = {}

    def embed(self, text):
        if text in self.cache:
            return self.cache[text]
        embedding = self.model.encode(text)
        self.cache[text] = embedding
        return embedding
```

### Batch Inference Caching

#### Batch Size Optimization

[Large-scale batch inference](https://blog.skypilot.co/large-scale-embedding/) optimization:

**Batch composition:**
- Sort sentences by length before batching
- Tokenizers pad to longest item in batch
- Grouping similar-length inputs reduces padding waste by 20-40%

**Example:**
```
Inefficient batching:
Batch 1: ["a", "this is a long sentence", "b"]
         → pad all to length 25 = 3*25=75 tokens

Efficient batching:
Batch 1: ["a", "b", "cat"]
         → pad to length 3 = 3*3=9 tokens
Batch 2: ["this is a longer sentence", "another medium sentence"]
         → pad to length 25 = 2*25=50 tokens
```

Sorting by length reduces wasted computation by significant margins.

#### Micro-batching for Latency

[Request batching with micro-batching windows](https://www.anyscale.com/blog/turbocharge-langchain-now-guide-to-20x-faster-embedding/):

```python
from queue import Queue
import threading
import time

class MicroBatcher:
    def __init__(self, batch_size=32, max_wait_ms=10):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.queue = Queue()
        self.results = {}
        threading.Thread(target=self._process_batches, daemon=True).start()

    def embed(self, text):
        request_id = uuid.uuid4()
        self.queue.put((request_id, text))

        # Wait for result (usually <10ms due to micro-batching)
        while request_id not in self.results:
            time.sleep(0.001)
        return self.results.pop(request_id)

    def _process_batches(self):
        while True:
            batch = []
            start_time = time.time()

            # Collect batch_size items or timeout
            while len(batch) < self.batch_size:
                try:
                    request = self.queue.get(timeout=self.max_wait_ms/1000)
                    batch.append(request)
                except:
                    break

            if batch:
                embeddings = model.encode([text for _, text in batch])
                for (req_id, _), emb in zip(batch, embeddings):
                    self.results[req_id] = emb
```

**Benefits:**
- Maintains <20ms request latency
- Achieves 20-30x throughput improvement vs. serial processing
- Balances latency and throughput

#### Precision Optimization

[Mixed precision inference](https://zilliz.com/ai-faq/how-do-i-optimize-embedding-models-for-inference-speed) for faster computation:

```
FP32 (32-bit float):
├─ Highest accuracy
├─ Largest memory usage
└─ Slowest computation

FP16 (16-bit half-precision):
├─ 2x faster on NVIDIA GPUs with Tensor Cores
├─ 50% memory reduction
└─ Negligible quality degradation for embeddings

Typical results for embeddings:
├─ FP32 embedding: 50ms
├─ FP16 embedding: 25ms
├─ Quality loss: <0.1% in downstream tasks
```

**Implementation:**
```python
with torch.cuda.amp.autocast():
    embeddings = model.encode(texts)  # Uses FP16 internally
```

---

## Performance Patterns

### Cold Start Optimization

#### What are Cold Starts?

[Cold starts in system design](https://www.designgurus.io/answers/detail/what-are-cold-starts-and-warm-starts-in-system-design):

A cold start occurs when:
1. New process/container/function instance initializes
2. Runtime loads code, dependencies, libraries
3. Database connections established
4. Caches populated
5. System ready to serve requests

**Cost:**
- Serverless functions: 100-1000ms overhead
- Containers: 500-2000ms overhead
- Traditional servers: 1-5 seconds overhead

#### Cold Start Causes in Search

Search-specific cold start sources:
1. **Index loading**: Mmapped indexes require page-ins
2. **Connection pool establishment**: Database connections
3. **Cache warming**: Pre-load hot filters/queries
4. **Model loading**: ML models for ranking/embeddings
5. **Network latency**: DNS, connection establishment

#### Warm-up Strategies

[Solving OpenSearch cold start](https://opensearch.org/blog/cold-start-search/) suggests:

1. **Scheduled warm-up requests**:
   ```
   Every 5 minutes: Send synthetic queries to keep index "warm"
   Effect: Keeps index pages in OS page cache
   ```

2. **Connection pool persistence**:
   ```
   Keep database connections open between requests
   Use connection pooling (e.g., pgbouncer for PostgreSQL)
   Effect: Eliminates connection establishment cost
   ```

3. **Segment warming**:
   ```
   On deployment, force index refresh to load segments
   Trigger a few queries to load common paths
   Effect: Eager page-in before production traffic
   ```

4. **Refresh interval tuning**:
   ```
   OpenSearch refresh_interval controls when new documents appear
   Too frequent (1s) = overhead
   Too infrequent (30s) = staleness
   Optimal: Adjust based on index update rate
   ```

**Case study results:** Reducing cold start from 2000ms to 100ms (95% reduction) by combining optimization techniques.

### Connection Pooling

#### Why Connection Pooling Matters

[Connection pooling fundamentals](https://www.tint.ai/technical-blog/how-did-we-divide-our-node-api-latency-by-leveraging-our-database-connection-pool):

Without pooling, each request pays:
- TCP handshake: 10-50ms
- TLS handshake: 50-100ms (if encrypted)
- Database authentication: 1-10ms
- **Total per-request: 60-160ms**

With pooling, idle connection reuse:
- Handshakes already done: 0ms
- Connection ready to use: <1ms
- **Total per-request: <1ms**

**Impact:** On 1000 concurrent users, connection pooling eliminates 60-160 seconds of latency per second.

#### Connection Pool Configuration

```
Pool size = (number_of_backend_services) × (service_concurrency)

Example: 4 Elasticsearch nodes, max 10 concurrent searches each
Pool size = 4 × 10 = 40 connections

Connections in Java search client:
├─ Min pool size: 5-10 (minimum always-open connections)
├─ Max pool size: 50-100 (maximum concurrent requests)
├─ Idle timeout: 5-10 minutes (close unused)
├─ Max wait time: 100-500ms (fail fast if pool exhausted)
└─ Connection reset: Every 30 minutes
```

#### Connection Pooling Across Serverless Functions

For serverless search:

```python
# Connection OUTSIDE handler = reused across invocations
search_client = create_search_client()

@serverless_handler
def search(event):
    # Reuse search_client from closure
    results = search_client.query(event['query'])
    return results
```

**Important:** Connection pool persists across warm function invocations, reducing handshake overhead.

### Query Parsing Optimization

#### Parsing Pipeline

[Query processing stages](https://medium.com/towards-data-engineering/understanding-sql-query-processing-parsing-optimization-and-execution-explained-7c38864fdc45):

1. **Tokenization**: Break query into tokens
   - Cost: 0.1-1ms for typical queries
   - Opportunity: Cache tokens for repeated queries

2. **Syntax analysis**: Verify grammar
   - Cost: 0.2-1ms
   - Opportunity: Pre-validate common query patterns

3. **Semantic validation**: Verify field names exist, types compatible
   - Cost: 0.5-2ms
   - Opportunity: Cache field metadata in process memory

4. **Query expansion**: Apply synonyms, stemming, etc.
   - Cost: 1-5ms (depends on analysis chain)
   - Opportunity: Pre-compute expansions for top queries

#### Parsing Cache

```
Cache parsed queries:
Key: "parsed:query:{hash(query)}"
Value: Query AST / execution plan
TTL: Permanent (until query changes)

Payoff:
  Parsing 10ms × 1000 queries/sec = 10 seconds/second overhead
  With cache: <1% overhead from new queries
```

### Result Serialization

#### JSON Serialization Cost

Result serialization is often overlooked but significant:

```
Serialization overhead:
├─ 100 results × 2KB each = 200KB JSON
├─ JSON encoding (algorithm): 1-5ms
├─ Network transfer (50Mbps): 32ms
├─ JSON decoding (client): 2-5ms
└─ Total: 35-42ms (can be 20% of total latency)
```

#### Optimization Strategies

1. **Sparse results**: Only include necessary fields
   ```json
   // DON'T include everything:
   {
     "id": "123",
     "title": "...",
     "full_text": "...",  // Usually not needed in results
     "all_metadata": {...}  // Extra memory overhead
   }

   // DO include what's needed:
   {
     "id": "123",
     "title": "...",
     "score": 0.95
   }
   ```

2. **Compression**: Use gzip/brotli
   ```
   Uncompressed: 200KB JSON
   Gzip: 45KB (22% original)
   Brotli: 40KB (20% original)

   Trade-off: Compression time 2-5ms vs transfer time savings 32ms
   Net savings: 25-30ms on slow networks
   ```

3. **Streaming**: Return results progressively
   ```
   Rather than: [wait 100ms] → send all 200KB at once
   Stream: [send first 10 results at 10ms] → [stream remaining results]
   User perceives responsiveness sooner
   ```

4. **Binary formats**: Use MessagePack/Protocol Buffers
   ```
   JSON (text): 200KB
   MessagePack: 120KB (60% reduction)
   Serialization: Faster due to known schema
   Trade-off: Requires client library
   ```

---

## Latency Budget Management

### Understanding Latency Percentiles

[Latency percentile fundamentals](https://oneuptime.com/blog/post/2025-09-15-p50-vs-p95-vs-p99-latency-percentiles/view):

**P50 (Median):** 50% of requests are faster, 50% are slower
- Represents typical user experience
- Use for: Detecting broad regressions

**P95 (95th percentile):** 95% of requests are faster, 5% are slower
- Represents most users
- Use for: SLO targets, user experience targets

**P99 (99th percentile):** 99% of requests are faster, 1% are slower
- Represents worst-case users
- Use for: Architectural bottleneck detection

#### Interpreting Latency Signals

| Pattern | Interpretation | Action |
|---------|---|---|
| P50 stable, P95↑ P99↑ | Queueing/contention | Add capacity, optimize bottleneck |
| P50↑ P95↑ P99↑ | More work per request | Optimize query, reduce payload |
| P50 stable, P99 spikes | Occasional outliers | GC pause? retry? I/O stall? |
| All metrics rising | System overloaded | Scale, reduce load |

### Latency Budget Allocation

For a target of 200ms p95 search latency:

```
Latency budget: 200ms

Allocation:
├─ Network (client to server): 10ms (geo-distributed)
├─ Query parsing: 5ms
├─ Index lookup/retrieval: 100ms
├─ Ranking/scoring: 40ms
├─ Result serialization: 15ms
├─ Batch processing/queueing: 10ms
├─ Buffer/margin: 20ms
└─ Total: 200ms
```

Each component must hit its target:
- Index retrieval budget = 100ms max
- Ranking budget = 40ms max
- Etc.

If any component exceeds budget, reduce latency elsewhere or increase overall target.

### Search Latency Breakdown

[Query latency components](https://questdb.com/glossary/query-latency/) in practice:

```
Total Query Latency = Queueing + Parsing + Planning + Execution + Serialization

Queueing (0-50ms):
└─ Time request spends waiting for available worker

Parsing (1-5ms):
├─ Tokenize query
├─ Syntax check
└─ Semantic validation

Planning (2-10ms):
├─ Choose index strategy
├─ Determine shard targets
└─ Build execution plan

Execution (100-500ms):
├─ Shard retrieval (parallel)
├─ Result merging
├─ Filtering and scoring
└─ Top-K selection

Serialization (5-20ms):
├─ Format results (JSON/MessagePack)
├─ Compress (gzip)
└─ Network serialization
```

### Setting Service Level Objectives (SLOs)

Example SLO for search service:

```
Service Level Objective:
├─ p50 latency: < 100ms (typical fast response)
├─ p95 latency: < 200ms (good response)
├─ p99 latency: < 500ms (acceptable worst case)
├─ Availability: > 99.5% (43 minutes downtime/month)
└─ Error rate: < 0.1% (no user sees errors)

Error budget for latency:
├─ Monthly latency "error" = requests exceeding SLO
├─ If p95 > 200ms for 1 hour of 730 hours
├─ Error budget = (1 hour / 730 hours) × 100% = 0.137%
├─ SLO burn rate = 1h of p95 breach = 100% burn in 1 hour
└─ Alert when burn rate > 4x (on track to break SLO in ~6 days)
```

### Tail Latency Management

[Tail latency in distributed systems](https://last9.io/blog/tail-latency/):

In distributed search, tail latency (p99, p99.9) is amplified:

```
Single shard p99: 500ms
Search across 10 shards (parallel):
├─ Expected p99: ~500ms (whichever shard is slowest)
├─ Actual p99: ~600-700ms (network variance + retries)
└─ p99.9: can be several seconds
```

**Tail latency causes:**
1. Garbage collection pauses (100-500ms)
2. Page cache misses requiring disk I/O (10-100ms)
3. Lock contention on hot resources
4. Network packet loss/retransmission
5. Noisy neighbor CPU stealing (cloud environments)

**Mitigation strategies:**

1. **Hedged requests**: Send same request to multiple shards, use first response
   ```
   Request to shard 1
   Wait 50ms
   If no response: also request shard 2
   Return whichever responds first

   Impact: Reduce p99 from 500ms to 100-150ms
   Cost: 2-3% extra requests
   ```

2. **Queue prioritization**: Fast queries bypass queues
   ```
   Queue 1: Large/complex queries
   Queue 2: Fast/simple queries (prioritized)
   Effect: Reduce p99 variance from contention
   ```

3. **GC tuning**: Reduce pause times
   ```
   G1GC MaxGCPauseMillis: 50ms (more frequent, shorter pauses)
   vs.
   G1GC MaxGCPauseMillis: 200ms (infrequent, long pauses)
   ```

4. **Connection timeouts**: Fail fast on slow connections
   ```
   Connection timeout: 100ms (fail and retry)
   vs.
   Connection timeout: 10s (wait for slow connection)
   ```

---

## Pre-computation Strategies

### Materialized Views for Search

[Materialized views for performance](https://codeopinion.com/speeding-up-queries-with-materialized-views/) move computation from read-time to write-time:

#### How They Work

```
Traditional approach:
Read Query → Expensive Computation → Return results (slow)

Materialized view approach:
Write event → Pre-compute result → Store
Read query → Return pre-computed result (fast)
```

#### Search-Specific Materialized Views

For common search queries:

```
Materialized view: "Popular products by category"
├─ Update trigger: When product catalog changes
├─ Computation:
│  ├─ Group products by category
│  ├─ Rank by popularity score
│  └─ Return top 20 per category
├─ Storage: JSON documents in search index
└─ Query time: Instant lookup

Example:
GET /products/_search?q=category:electronics
→ Returns pre-ranked results from materialized view
```

**Benefits:**
- Eliminates expensive joins/aggregations at query time
- Consistent ranking (computed once)
- Predictable latency

**Update strategy:**
```
Trigger points for re-computation:
├─ On product update (delta update the view)
├─ Bulk updates complete (full re-computation)
├─ Scheduled (e.g., hourly) for non-critical views
└─ Lazy (update on-demand if stale)
```

### Query Anticipation

Anticipating user queries enables pre-computation:

#### Pattern Recognition

```
User behavior analysis:
├─ Most frequent queries (80/20 rule)
│  ├─ "laptops under $1000"
│  ├─ "iphones"
│  ├─ "electronics on sale"
│  └─ Top 100 queries = 50% of traffic
├─ Seasonal patterns
│  ├─ "gift ideas" (Nov-Dec)
│  ├─ "back to school" (Aug-Sep)
│  └─ "summer gear" (Jun-Aug)
└─ Emerging trends
   ├─ New products
   ├─ Viral categories
   └─ Marketing campaigns
```

#### Pre-computation Scheduling

```
Offline batch process (hourly):
1. Identify top 1000 queries from logs
2. Filter out changed filters/facets
3. Execute queries and cache results
4. Push to CDN/Redis for fast access

Result: 80% of queries served from pre-computed results
        <50ms latency (cache hit)
```

### Batch Pre-computation During Off-Peak

#### Off-Peak Processing

```
Search traffic pattern:
├─ Peak hours (9am-5pm): 10,000 QPS
├─ Off-peak (11pm-7am): 2,000 QPS
├─ Capacity: 15,000 QPS available

Off-peak opportunity:
├─ Use spare capacity to pre-compute results
├─ Lower cost (use spot instances)
├─ Doesn't impact peak latency
├─ Warm up caches before peak hours
```

#### Pre-computation Tasks

```
Scheduled during 2am-6am daily:

1. Recompute top 10,000 query results
2. Pre-compute facet counts for filters
3. Generate trending/popular lists
4. Rebuild materialized views
5. Warm Redis/caches
6. Optimize index (merge segments)

Result:
├─ Peak hour cache hit rate: 80%+
├─ Peak hour p95 latency: 100-150ms
├─ Peak hour p99 latency: 300-400ms
```

---

## Benchmarking Search Performance

### Rally: Elasticsearch Benchmarking

[Rally](https://github.com/elastic/rally) is the official macrobenchmarking framework for Elasticsearch:

#### Features

```
Rally capabilities:
├─ Cluster setup and teardown
├─ Benchmark data generation
├─ Track management (predefined benchmarks)
├─ Metrics collection
│  ├─ Latency (p50, p90, p95, p99)
│  ├─ Throughput (queries/sec)
│  ├─ Indexing rate
│  └─ Storage overhead
├─ Comparison across versions
└─ Results reporting
```

#### Basic Rally Workflow

```bash
# Setup
esrally create-track --track=my-track --data-sources=my-data.json

# Run benchmark
esrally race --track=my-track --target-hosts=localhost:9200

# Compare versions
esrally compare --baseline=version1 --contender=version2
```

#### Rally Metrics Output

```
Metric                      p50      p95      p99    Mean
query latency (ms)         45.2    98.3    234.8   67.1
bulk indexing (docs/s)  50000   48000    45000  48900
search throughput (ops/s)  1200    1150    1100   1180
jvm_gc_time (ms)           5.1    15.3     42.1    8.2
```

### Load Testing Tools Comparison

| Tool | Use Case | Strengths | Weaknesses |
|------|----------|-----------|-----------|
| **Rally** | Elasticsearch | Official, ES metrics, easy setup | ES-specific |
| **Gatling** | High load | [Asynchronous, handles 1000s of concurrent users](https://www.ioriver.io/terms/cache-invalidation), high throughput | Steeper learning curve |
| **k6** | API testing | Developer-friendly, JavaScript, fast iteration | Lower scale than Gatling |
| **JMeter** | Protocol variety | Supports many protocols, GUI, large community | Resource-heavy |
| **Locust** | Python-based | Python scripting, distributed, flexible | Slower than Gatling |

### Load Testing Methodology

#### Baseline Establishment

```
Phase 1: Establish baseline (1-2 hours)
├─ Run steady-state load (e.g., 5000 QPS)
├─ Let system stabilize (15-30 min)
├─ Collect metrics:
│  ├─ Latency: p50, p95, p99, p99.9
│  ├─ Throughput: actual QPS
│  ├─ Error rate: timeouts, failures
│  └─ Resource usage: CPU, memory, disk I/O
└─ Document baseline metrics
```

#### Ramp-up Testing

```
Phase 2: Ramp to saturation (30-60 min)
├─ Start at 1000 QPS
├─ Increase by 1000 QPS every 3 minutes
├─ Monitor for degradation:
│  ├─ p95 latency increasing
│  ├─ Error rate increasing
│  ├─ CPU approaching 80%+
│  └─ Memory pressure
├─ Stop when system shows degradation
└─ Record saturation point (e.g., 12,000 QPS p95 > 500ms)
```

#### Stress Testing

```
Phase 3: Stress beyond saturation (10-15 min)
├─ Continue increasing load past saturation
├─ Verify system doesn't crash
├─ Measure recovery behavior
├─ Identify breaking point
└─ Useful for: Circuit breaker testing, timeout tuning
```

### Realistic Load Patterns

Production load isn't uniform:

```
Realistic load model:
├─ Query distribution:
│  ├─ 80% common queries (top 100)
│  ├─ 15% moderately common queries
│  └─ 5% rare/one-off queries
├─ Temporal patterns:
│  ├─ Weekday: higher traffic during business hours
│  ├─ Weekend: lower traffic, different patterns
│  └─ Seasonal: back-to-school, holidays, etc.
├─ Burst patterns:
│  ├─ Campaign launches
│  ├─ Viral events
│  └─ Search advertising spikes
└─ Failure modes:
   ├─ Backend timeout: What happens?
   ├─ Network latency increase: Effect on latency?
   └─ Cascading failures: Do other services fail?
```

---

## Cost Optimization

### Right-Sizing Search Infrastructure

#### Capacity Planning

```
Cost drivers in search infrastructure:
├─ Compute (CPU cores): ~$0.05-0.10 per core-hour
├─ Memory (GB): ~$0.01 per GB-hour
├─ Storage (indexed data): ~$0.02-0.05 per GB-month
├─ Network egress: ~$0.10 per GB
└─ Managed service premium: 2-3x more expensive

Example monthly cost (1TB index, 10K QPS):
├─ Dedicated EC2: $5K-8K
├─ Elasticsearch Service: $15K-20K
└─ Algolia (managed): $20K-30K
```

#### Replication Factor Optimization

```
Index configuration:
├─ 1 primary shard + 2 replicas (3 copies total)
│  ├─ Cost: 3x index storage
│  ├─ Availability: Very high (survives 2 node failures)
│  └─ Use case: Production, critical searches
├─ 1 primary shard + 1 replica (2 copies total)
│  ├─ Cost: 2x index storage
│  ├─ Availability: High (survives 1 node failure)
│  └─ Use case: Standard production
├─ 1 primary shard, 0 replicas
│  ├─ Cost: 1x index storage
│  ├─ Availability: Low (no redundancy)
│  └─ Use case: Development, non-critical searches
```

**Optimization:** Use replication_factor=1 for non-critical data, reduce to 2 for standard production.

### Spot Instances

[EC2 Spot Instances](https://aws.amazon.com/blogs/compute/introducing-price-capacity-optimized-allocation-strategy-for-ec2-spot-instances/) provide massive cost savings:

```
Savings:
├─ On-Demand: $0.20/hour
├─ Spot (varies): $0.04-0.08/hour (60-80% discount)
└─ Savings Plans 1-year: $0.12/hour (40% discount)

Workload mapping:
├─ Stateless search shards: Use Spot
├─ Coordinator nodes: Use On-Demand (must be available)
├─ Master nodes: Use On-Demand (need quorum)
└─ Data nodes: Can use Spot with rebalancing
```

#### Spot Instance Strategy for Search

```
Hybrid cluster:
├─ Master nodes: 3× On-Demand (quorum requirement)
├─ Coordinator nodes: 2× On-Demand (query routing)
├─ Data nodes:
│  ├─ 10× Spot (primary shards)
│  ├─ Auto-recovery enabled
│  ├─ Rebalancing on node loss
│  └─ Cost: 80% of On-Demand cluster

Failure handling:
├─ Spot instance interrupted
├─ Shard rebalanced to Spot node with capacity
├─ Replica promotes to primary if needed
└─ User experiences no downtime
```

**Pitfall:** Spot instances can be interrupted with 2-minute notice. Use for replicable work, not master nodes.

### Auto-scaling Search Clusters

Dynamic scaling based on load:

```
Auto-scaling policy:
├─ Scale-up trigger:
│  ├─ P95 latency > 200ms for 2 minutes
│  ├─ CPU utilization > 70% for 2 minutes
│  └─ Add 2-4 nodes (takes ~5 min to warm up)
├─ Scale-down trigger:
│  ├─ P95 latency < 100ms for 10 minutes
│  ├─ CPU utilization < 30% for 10 minutes
│  └─ Remove 1-2 nodes (graceful shutdown)
└─ Constraints:
   ├─ Minimum: 3 nodes (quorum)
   ├─ Maximum: 50 nodes (cost limit)
   └─ Scale changes: Max 1 every 5 minutes
```

**Cost impact:** Auto-scaling can reduce 24/7 cluster cost by 30-40% by downsizing during off-peak hours.

### Serverless Search

Serverless search (AWS Lambda, Google Cloud Functions) offers per-query billing:

```
Cost model:
├─ Per query: $0.000002 per query + compute
├─ Compute: $0.0000166667 per GB-second
├─ Example 100KB query, 50ms execution:
│  ├─ Query cost: $0.000002
│  ├─ Compute: 0.256GB-seconds × $0.0000166667 = $0.000004
│  └─ Total: $0.000006 per query

vs. Dedicated cluster:
├─ 10,000 QPS × $0.000006 = $0.06/sec = $5184/day
├─ Plus: Dedicated 5-node cluster = $500/day
└─ Total: $5684/day

Dedicated cluster:
├─ $500/day for 10K QPS average (much lower)
```

**Serverless is cost-effective for:**
- Bursty traffic (only pay when used)
- Low-traffic applications (<1000 QPS)
- Development/testing

**Dedicated clusters better for:**
- Consistent high traffic (amortized cost lower)
- Predictable workloads

### Data Tiering and Warm/Cold Storage

Modern search engines support storage tiers:

```
Tier structure:
├─ Hot tier (last 7 days)
│  ├─ Fast SSDs, high cost
│  ├─ SLA: <100ms query latency
│  ├─ Use case: Current searches
│  └─ Cost: $0.05/GB-month
├─ Warm tier (7-90 days)
│  ├─ HDD storage, medium cost
│  ├─ SLA: <1s query latency
│  ├─ Use case: Recent historical searches
│  └─ Cost: $0.01/GB-month
└─ Cold tier (>90 days)
   ├─ Archival storage, very low cost
   ├─ SLA: 10-60s query latency (restore on demand)
   ├─ Use case: Archival, compliance
   └─ Cost: $0.001/GB-month
```

**Example:** 1TB hot + 10TB warm + 100TB cold
```
Hot:     1TB × $0.05 = $50/month
Warm:   10TB × $0.01 = $100/month
Cold:  100TB × $0.001 = $100/month
Total: $250/month (vs. $2500 if all hot tier)
```

---

## Conclusion

Effective search performance requires optimization at every layer:

1. **Caching layers** reduce redundant computation (result cache, index cache, OS page cache)
2. **Edge computing** brings search closer to users (Cloudflare Workers, Fastly, Algolia DSN)
3. **Redis specialization** enables fast autocomplete and real-time filtering
4. **Embedding caching** eliminates ML inference for repeated queries
5. **Performance patterns** (cold starts, connection pooling, query parsing) compound improvements
6. **Latency budgets** allocate optimization targets per component
7. **Pre-computation** shifts expensive work to off-peak hours
8. **Benchmarking** validates optimization effectiveness
9. **Cost management** balances performance with financial constraints

The most effective systems combine multiple strategies:
- Static result caching for the 80% of common queries
- Distributed search (Algolia/custom) for global latency
- Redis for sub-millisecond autocomplete
- Spot instances for non-critical search nodes
- Pre-computed results refreshed during off-peak
- Careful p95/p99 latency monitoring and alerting

Modern search demands integration across infrastructure, application, and operational layers. Invest in measurement first—you can't optimize what you don't measure.

---

## References and Sources

### Search Result Caching
- [Adaptive Time-to-Live Strategies for Query Result Caching in Web Search Engines](https://link.springer.com/chapter/10.1007/978-3-642-28997-2_34)
- [Timestamp-based Result Cache Invalidation for Web Search Engines](https://www.cl.cam.ac.uk/~ey204/teaching/ACS/R212_2015_2016/papers/alici_sigir_2011.pdf)
- [Cache Invalidation Strategies](https://www.ioriver.io/terms/cache-invalidation)
- [The Hardest Part of Caching: Understanding What to Cache and When to Invalidate](https://stellate.co/blog/the-hardest-part-of-caching)
- [Redis Cache Invalidation Glossary](https://redis.io/glossary/cache-invalidation/)

### Index Caching and Memory Management
- [Elasticsearch Heap Size and JVM Garbage Collection](https://www.elastic.co/search-labs/blog/elasticsearch-heap-size-jvm-garbage-collection)
- [Elasticsearch Caching Deep Dive](https://www.elastic.co/blog/elasticsearch-caching-deep-dive-boosting-query-speed-one-cache-at-a-time)
- [Significantly Decrease Elasticsearch Heap Memory Usage](https://www.elastic.co/blog/significantly-decrease-your-elasticsearch-heap-memory-usage)
- [Deep Dive into Elasticsearch Memory Management](https://medium.com/@yago82/deep-dive-into-elasticsearch-memory-management-885177fc0747)
- [Elasticsearch mmap File Cache Trashing Issue](https://github.com/elastic/elasticsearch/issues/27748)

### Edge and CDN Search
- [Handling Data at the Edge with Cloudflare Workers](https://launchdarkly.com/blog/handling-data-at-the-edge-with-cloudflare-workers/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [EdgeSearch: Serverless Full-Text Search](https://github.com/wilsonzlin/edgesearch)
- [What is Edge Computing - Cloudflare](https://www.cloudflare.com/learning/serverless/glossary/what-is-edge-computing/)
- [Algolia Global Infrastructure for Search Speed and Reliability](https://www.algolia.com/distributed-secure/global-infrastructure)
- [The Architecture of Algolia's Distributed Search Network](https://highscalability.com/the-architecture-of-algolias-distributed-search-network/)
- [Algolia Distributed Search Network (DSN) Documentation](https://www.algolia.com/doc/guides/scaling/distributed-search-network-dsn)
- [Fastly Compute@Edge](https://docs.developers.optimizely.com/feature-experimentation/docs/fastly-compute-at-edge)
- [Fastly Edge Compute Products](https://www.fastly.com/products/edge-compute)

### Redis for Search
- [Redis Autocomplete with Sorted Sets](https://patshaughnessy.net/2011/11/29/two-ways-of-using-redis-to-build-a-nosql-autocomplete-search-index)
- [Search Autocompletion with Redis](https://thorstenball.com/blog/2012/06/08/search-autocompletion-with-redis/)
- [Building Smart Autocomplete with Redis Sorted Sets](https://upstash.com/blog/redis-autocomplete-popularity-ranking)
- [RediSearch Module Documentation](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/search/)

### Embedding and Vector Caching
- [LangChain Embedding Model Integrations](https://docs.langchain.com/oss/python/integrations/text_embedding)
- [Embedding Infrastructure at Scale](https://introl.com/blog/embedding-infrastructure-scale-vector-generation-production-guide-2025)
- [OpenAI Vector Embeddings API](https://developers.openai.com/api/docs/guides/embeddings/)
- [Turbocharge LangChain: 20x Faster Embedding](https://www.anyscale.com/blog/turbocharge-langchain-now-guide-to-20x-faster-embedding/)
- [Large-Scale AI Batch Inference: 9x Faster Embedding Generation](https://blog.skypilot.co/large-scale-embedding/)
- [Optimizing Embedding Models for Inference Speed](https://zilliz.com/ai-faq/how-do-i-optimize-embedding-models-for-inference-speed)
- [High-Performance Embedding Model Inference Guide](https://www.baseten.co/resources/guide/high-performance-embedding-model-inference/)

### Performance Patterns
- [Cold Start Optimization: A Guide For Developers](https://www.movestax.com/post/cold-start-optimization-a-guide-for-developers)
- [Cold Start Performance: The Hidden Latency Problem](https://www.zoyla.app/resources/cold-start-performance)
- [Solving the Cold Start Search Problem in OpenSearch](https://opensearch.org/blog/cold-start-search/)
- [AWS Lambda Cold Start: 7 Proven Fixes 2026](https://www.agilesoftlabs.com/blog/2026/02/aws-lambda-cold-start-7-proven-fixes)
- [Connection Pooling for API Latency](https://www.tint.ai/technical-blog/how-did-we-divide-our-node-api-latency-by-leveraging-our-database-connection-pool)

### Latency Budget Management
- [P50, P95, P99 Latencies Explained](https://oneuptime.com/blog/post/2025-09-15-p50-vs-p95-vs-p99-latency-percentiles/view)
- [Understanding P50 Latency](https://sreschool.com/blog/p50-latency/)
- [Understanding P95 Latency](https://sreschool.com/blog/p95-latency/)
- [What Is P99 Latency](https://aerospike.com/blog/what-is-p99-latency/)
- [Tail Latency in Large-Scale Distributed Systems](https://last9.io/blog/tail-latency/)

### Pre-computation Strategies
- [Materialized Views in BigQuery](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [Speeding Up Queries with Materialized Views](https://codeopinion.com/speeding-up-queries-with-materialized-views/)
- [Performance Tuning with Materialized Views in Azure Synapse](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-materialized-view-performance-tuning)
- [Why, How, and When To Use Materialized Views](https://materialize.com/blog/why-use-a-materialized-view/)

### Benchmarking Search Performance
- [Rally: Macrobenchmarking Framework for Elasticsearch](https://github.com/elastic/rally)
- [Benchmarking Elasticsearch with Rally](https://logz.io/blog/rally/)
- [Announcing Rally: Benchmarking Tool for Elasticsearch](https://www.elastic.co/blog/announcing-rally-benchmarking-for-elasticsearch/)
- [Rally Documentation](https://esrally.readthedocs.io/)
- [Elasticsearch Benchmarks](https://elasticsearch-benchmarks.elastic.co/)

### Cost Optimization
- [Spot + Serverless: A Smarter Way to Scale and Save](https://www.cloudoptimo.com/blog/spot-serverless-a-smarter-way-to-scale-and-save-in-cloud/)
- [Price-Capacity-Optimized Allocation Strategy for EC2 Spot Instances](https://aws.amazon.com/blogs/compute/introducing-price-capacity-optimized-allocation-strategy-for-ec2-spot-instances/)
- [Cost Optimization and Resilience for EKS with Spot Instances](https://aws.amazon.com/blogs/compute/cost-optimization-and-resilience-eks-with-spot-instances/)
- [Auto Scaling Groups with Multiple Instance Types and Purchase Options](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html)

---

**Document Version:** 1.0
**Last Updated:** March 1, 2026
**Author:** Research Compilation
**Status:** Reference Material
