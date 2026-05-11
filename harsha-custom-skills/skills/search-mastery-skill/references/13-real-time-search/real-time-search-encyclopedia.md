# Real-Time Search: Indexing, Querying, and Streaming at Speed
## Comprehensive Encyclopedia for Search Mastery

**Author:** Claude Research Agent
**Date:** 2026-03-01
**Length:** 3500+ words
**Scope:** Production-grade real-time search systems, architectures, and implementation patterns

---

## Table of Contents

1. [Real-Time Indexing Fundamentals](#real-time-indexing-fundamentals)
2. [Streaming Search Architecture](#streaming-search-architecture)
3. [Change Data Capture for Search](#change-data-capture-for-search)
4. [Client-Side Search with Web Workers](#client-side-search-with-web-workers)
5. [WebSocket and SSE Patterns](#websocket-and-sse-patterns)
6. [Index Refresh Strategies](#index-refresh-strategies)
7. [Event-Driven Search Architecture](#event-driven-search-architecture)
8. [Auto-Complete at Scale](#auto-complete-at-scale)
9. [Incremental Indexing](#incremental-indexing)
10. [Performance Budgets](#performance-budgets)
11. [Architecture Diagrams](#architecture-diagrams)
12. [Implementation Patterns](#implementation-patterns)

---

## Real-Time Indexing Fundamentals

### What Is Real-Time Indexing?

Real-time indexing refers to making newly added or updated documents immediately searchable without waiting for batch jobs or scheduled reindexing cycles. This is critical for applications where users expect current data—e-commerce product searches, news feeds, monitoring dashboards, and live collaboration tools.

### Elasticsearch Near Real-Time Search

Elasticsearch defines "near real-time" search as making documents available within 1 second of indexing. This is controlled by the `index.refresh_interval` parameter, which dictates how frequently the inverted index is refreshed.

**How Refresh Works:**

A refresh in Elasticsearch is the process of writing and opening a new segment, making all operations since the last refresh available for search. By default, Elasticsearch:

- Refreshes every 1 second
- But only on indices that have received a search request in the last 30 seconds
- Configurable via `index.refresh_interval` setting

**Configuration Example:**

```json
{
  "settings": {
    "index.refresh_interval": "100ms"  // Near-instant refresh
  }
}
```

**Trade-offs:**

| Interval | Use Case | Throughput Impact |
|----------|----------|------------------|
| 1s (default) | Balanced | Minimal |
| 100ms | Real-time dashboards | Moderate impact |
| 30s | High-throughput indexing | Minimal impact |
| -1 | Batch indexing | None until explicit refresh |

### Meilisearch Instant Indexing

Meilisearch takes a different approach to real-time indexing:

- **Search-as-you-type:** Results returned in <50 milliseconds
- **Automatic indexing:** Documents are automatically indexed when added
- **Incremental updates:** Real-time updates for new or modified data
- **Open-source:** Self-hosted with full customization

Meilisearch's architecture prioritizes instant availability by design, making it ideal for search-as-you-type interfaces and interactive applications.

---

## Streaming Search Architecture

### Persistent Queries (Reverse Search)

Traditional search flows from documents to queries. **Persistent search** (also called prospective search or reverse search) inverts this: you store queries first, then test incoming documents against them.

**Traditional vs. Prospective Search:**

```
Traditional Search:
1. Index documents
2. User submits query
3. Search returns matching documents

Prospective Search:
1. User saves a query/filter
2. Document arrives
3. Test document against stored queries
4. Notify users whose queries match
```

**Real-World Applications:**

- **Product alerts:** User saves filter "Nike sneakers < $100"; system notifies when new matching products arrive
- **Log alerting:** Incoming logs tested against alert conditions in real-time
- **Social media monitoring:** Track mentions matching saved search profiles

**Implementation with Elasticsearch Percolate:**

Elasticsearch implements persistent search via the Percolate Query:

```json
{
  "percolate": {
    "field": "query",
    "document": {
      "title": "Nike Air Force 1",
      "price": 85,
      "brand": "Nike"
    }
  }
}
```

This tests the incoming document against all stored queries, returning which ones match.

### Ping Servers and Content Notification

Real-time search relies on immediate knowledge of new content. Ping servers (used by blogging platforms) notify search engines instantly when new content is published:

- Reduced latency between publication and searchability
- Enables true prospective search without polling
- Critical infrastructure for real-time news and trending content

---

## Change Data Capture for Search

### Debezium + Kafka for Index Updates

Change Data Capture (CDC) is the automated process of detecting and streaming database changes to search indexes. Debezium is a platform built on Apache Kafka that captures changes from multiple databases.

**Architecture:**

```
Database → Debezium Source Connector → Kafka Topic → Sink Connector → Elasticsearch
```

**How It Works:**

1. Source connector monitors a database server
2. All changes are captured and written to Kafka topics
3. One topic per database table (typically)
4. Sink connectors consume from Kafka
5. Push updates to Elasticsearch or other systems

**Advantages:**

- **Decoupling:** Database changes flow through Kafka, not directly to search
- **Durability:** Kafka provides fault tolerance and replay capability
- **Flexibility:** Add multiple consumers without affecting the source
- **Scalability:** Handles high-volume changes at scale

**Use Cases Beyond Search:**

- Cache invalidation
- Index rebuilds
- Notifications
- Business logic triggering
- Data warehouse synchronization

**Implementation Pattern:**

```yaml
connector:
  class: "io.debezium.connector.postgresql.PostgresConnector"
  config:
    database.hostname: "postgres.local"
    database.port: 5432
    database.user: "replicator"
    database.dbname: "production"
    publication.name: "search_changes"
    topic.prefix: "search"
```

### Event Sourcing with CDC

When combined with event sourcing patterns, CDC becomes the foundation for maintaining search indexes that are always consistent with the source of truth:

1. All database changes are captured as events
2. Events flow through Kafka topics
3. Search index is a projection of the event stream
4. Multiple projections possible for different search needs

---

## Client-Side Search with Web Workers

### Why Web Workers for Search?

Building search indexes for client-side search (documentation sites, large datasets) is computationally intensive. Without workers:

- Building indexes blocks the main thread
- UI freezes during scrolling and interaction
- User experience degrades significantly

**Web Workers solve this:**

```javascript
// Main thread
const searchWorker = new Worker('search-worker.js');

// Pass data to worker
searchWorker.postMessage({
  type: 'build-index',
  documents: largeDataset
});

// Receive results without blocking UI
searchWorker.onmessage = (event) => {
  console.log('Index built, ready for search');
};
```

### SharedArrayBuffer for Zero-Copy Communication

Normally, Web Worker communication uses the Structured Clone algorithm, which copies data. For large datasets, this is expensive.

**SharedArrayBuffer** allows memory to be shared between threads without copying:

```javascript
// Create shared memory
const sharedBuffer = new SharedArrayBuffer(1024 * 1024); // 1MB
const sharedArray = new Float32Array(sharedBuffer);

// Pass to worker
worker.postMessage({ sharedBuffer });

// Both threads access the same memory—no copying
```

**Performance Impact:**

- Eliminates copying overhead (can save hundreds of milliseconds)
- Enables true parallel processing
- Requires cross-origin isolation for security

**Security Considerations:**

- Documents must be in a secure context (HTTPS)
- Cross-Origin-Opener-Policy headers required
- Cross-Origin-Embedder-Policy headers required

### Practical Implementation: js-worker-search

The `js-worker-search` library provides full-text client-side search with Web Worker support:

```javascript
import { search } from 'js-worker-search';

const index = search.indexArray(documents, ['title', 'content']);
const results = await index.search('query');
```

Benefits:
- Non-blocking index building
- Responsive UI during search
- Full-text search capabilities
- Works in all modern browsers

---

## WebSocket and SSE Patterns

### WebSocket vs. Server-Sent Events

Both enable real-time communication, but with different characteristics:

| Feature | WebSocket | SSE |
|---------|-----------|-----|
| Direction | Bidirectional | Server-to-client only |
| Data type | Text + binary | Text only |
| Protocol | ws:// | HTTP |
| Reconnection | Manual | Automatic |
| Complexity | Higher | Lower |
| Use case | Interactive, real-time games | Data streaming, updates |

### SSE for Real-Time Search Updates

SSE is ideal for 95% of real-time applications because:

- Built on HTTP (simpler, works everywhere)
- Automatic reconnection
- Lower overhead than WebSocket
- Stateless (scales horizontally with load balancer)
- Works through most proxies

**Implementation Pattern:**

```javascript
// Server
app.get('/search-stream', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Send updates as documents arrive
  searchIndex.on('document-indexed', (doc) => {
    res.write(`data: ${JSON.stringify(doc)}\n\n`);
  });
});

// Client
const eventSource = new EventSource('/search-stream');
eventSource.onmessage = (event) => {
  const doc = JSON.parse(event.data);
  updateSearchResults(doc);
};
```

### WebSocket for Collaborative Search

WebSocket is preferred when:

- Full bidirectional communication needed
- Multiple users collaborating on search refinement
- Server needs to push updates based on client actions
- Interactive features like voting or filtering

**Example: Collaborative Search Dashboard**

```javascript
// Client sends search query
socket.emit('search', {
  query: 'elasticsearch real-time',
  filters: { category: 'database' }
});

// Server pushes results as they arrive
socket.on('result', (doc) => {
  addToResultsList(doc);
});

// Other clients see live updates
socket.on('user-filtered', (filter) => {
  broadcastToAllClients(filter);
});
```

---

## Index Refresh Strategies

### Immediate vs. Batch Refresh

**Immediate Refresh (every document visible instantly):**

```json
{
  "index.refresh_interval": "100ms"
}
```

Pros:
- Data is immediately searchable
- Real-time dashboards work perfectly
- Reduced user confusion

Cons:
- Increased CPU usage
- More frequent segment merging
- Lower indexing throughput

**Batch Refresh (lower latency, higher throughput):**

```json
{
  "index.refresh_interval": "30s"
}
```

Pros:
- Higher indexing throughput
- Lower CPU overhead
- Fewer segments to merge

Cons:
- Documents not visible for up to 30 seconds
- Not suitable for real-time requirements

### Configurable Refresh for Different Use Cases

**Production Recommendation:**

```json
{
  "settings": {
    "index": {
      "refresh_interval": "1s"  // Default balanced approach
    }
  },
  "indices": {
    "logs-real-time": {
      "refresh_interval": "200ms"  // Dashboards need fast updates
    },
    "archive-search": {
      "refresh_interval": "-1"  // Manual refresh only
    }
  }
}
```

### Write-Ahead Logs (WAL)

Ensuring durability during frequent refreshes requires write-ahead logs:

1. Document received by indexer
2. Write to WAL before updating in-memory index
3. Refresh creates new segment
4. WAL entry marked as committed

This guarantees:
- No document loss even during crashes
- Consistency between in-memory and persisted state
- Ability to replay from WAL if needed

---

## Event-Driven Search Architecture

### CQRS Pattern for Search

Command Query Responsibility Segregation separates read and write operations:

```
Write Side (Commands):
- Accept document additions/updates
- Write to event log/Kafka
- Acknowledgment to client

Read Side (Queries):
- Search against read-optimized index
- Eventually consistent with writes
- Can denormalize data as needed
```

**Advantages:**

- Independent scaling of reads and writes
- Write side optimized for throughput
- Read side optimized for query performance
- Eventually consistent (acceptable for search)

### Event Sourcing for Search Index

All changes to documents are captured as immutable events:

```
Event Stream (Kafka):
├── DocumentCreated(id: 123, title: "...", timestamp: T1)
├── DocumentUpdated(id: 123, title: "...", timestamp: T2)
├── DocumentDeleted(id: 123, timestamp: T3)
└── ...
```

**Benefits:**

- Complete audit trail of all changes
- Ability to rebuild indexes from events
- Time-travel queries (search as-of-date)
- Decoupled from any single storage system

### Kafka + Elasticsearch Pattern

```
┌─────────────────────────────────────────────────┐
│ Write Service                                   │
│ - Accepts document changes                      │
│ - Publishes to Kafka                            │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────▼──────────┐
        │ Kafka Topic        │
        │ (events stream)    │
        └─────────┬──────────┘
                  │
     ┌────────────┴────────────┐
     │                         │
     ▼                         ▼
┌─────────────┐         ┌──────────────┐
│ Elasticsearch│        │ Other Consumers│
│ (search)    │        │ (cache, etc)   │
└─────────────┘         └────────────────┘
```

**Implementation Checklist:**

- Use Debezium for CDC or application-level event publishing
- Kafka topics configured for retention (7-30 days)
- Elasticsearch consumer group for idempotent updates
- Schema Registry for version compatibility
- Dead-letter queues for failed documents

---

## Auto-Complete at Scale

### Trie-Based Auto-Complete

Basic approach using prefix trees:

```
apple
├── app
│   ├── application
│   └── append
└── apply

For prefix "app":
- Navigate to "app" node
- Return all descendants
```

**Implementation:**

```javascript
class TrieNode {
  constructor() {
    this.children = new Map();
    this.suggestions = [];  // Top suggestions at this node
  }
}

class AutoCompleteEngine {
  search(prefix) {
    let node = this.root;
    for (const char of prefix) {
      node = node.children.get(char);
      if (!node) return [];
    }
    return node.suggestions;
  }
}
```

**Limitations:**

- Memory-intensive for large vocabularies
- No suffix compression
- Slow for deep prefixes

### Finite State Transducers (FST)

FSTs compress both prefixes AND suffixes, making them more memory-efficient:

```
Traditional Trie: "apple", "application", "apply"
├── a
│   └── p
│       ├── p
│       │   └── l
│       │       ├── e (apple)
│       │       └── i
│       │           └── c...
│       └── l
│           ├── y (apply)
│           └── ...

FST: Compresses suffixes
"apple" and "apply" share the "ap" prefix AND "l" suffix
Memory savings: 40-60% typical
```

**Why FSTs Are Superior:**

- Memory-optimized (can store millions of suggestions)
- O(1) character lookup at each node
- Pre-cached top results at each prefix
- Used by Elasticsearch "Completion Suggester"

**Elasticsearch Completion Suggester:**

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "completion"  // Uses FST internally
      }
    }
  }
}
```

### Prefix Search Optimization

```
├── Top suggestions cached at each node
│   - "apple" (50K searches)
│   - "application" (30K searches)
│   - "append" (15K searches)
│
├── Weighted FST
│   - Higher-frequency terms bubble up
│   - Faster access to popular completions
│
└── Fuzzy matching support
    - Levenshtein automata for typo tolerance
    - "aple" → "apple"
```

### Server-Side vs. Client-Side Auto-Complete

| Approach | Latency | Accuracy | Scalability |
|----------|---------|----------|-------------|
| Server-side | 50-100ms | Perfect (fresh) | Requires backend |
| Client-side FST | <10ms | Stale (download time) | Bandwidth cost |
| Hybrid | 20-50ms | Good (periodic refresh) | Best balance |

**Hybrid Implementation:**

```javascript
// Client: Download FST on page load
const fstData = await fetch('/api/completion-fst').then(r => r.arrayBuffer());
const fst = new FST(fstData);

// User typing: instant local results
input.addEventListener('input', (e) => {
  const suggestions = fst.search(e.target.value);
  renderSuggestions(suggestions);
});

// Periodic refresh (every hour)
setInterval(async () => {
  const newFst = await fetch('/api/completion-fst').then(r => r.arrayBuffer());
  fst.update(newFst);
}, 3600000);
```

---

## Incremental Indexing

### Delta Updates vs. Full Rebuilds

**Full Index Rebuild:**

```
Time: O(n) where n = total documents
Use: Initial indexing, periodic maintenance
Frequency: Monthly or less
```

**Delta Indexing:**

```
Time: O(m) where m = changed documents
Use: Regular updates
Frequency: Hourly or more frequently
Process:
1. Read changed data since last index
2. Index only the changes
3. Apply deletions
4. Merge with existing index
```

### Soft Deletes Strategy

When Lucene deletes documents, it marks them for deletion rather than removing immediately:

```
Index State:
├── Active: [doc1, doc2, doc4, doc7, doc9]
├── Marked for deletion: [doc3, doc5, doc6]  (still in memory)
└── Actual deletion: deferred to segment merge
```

**Soft Delete Pattern:**

```json
{
  "mapping": {
    "properties": {
      "deleted_at": {
        "type": "date"
      }
    }
  }
}
```

Query with soft delete filter:

```json
{
  "query": {
    "bool": {
      "filter": {
        "range": {
          "deleted_at": {
            "gte": "now/d"  // Include docs deleted today
          }
        }
      }
    }
  }
}
```

### Handling Index Fragmentation

Regular delta indexing without full rebuilds causes fragmentation:

```
Issue: Index segments scattered across files
Result: Slower queries, increased memory usage
Solution: Periodic segment merging

Recommendation:
- Run daily delta indexes
- Run full reindex monthly
- Merge segments during off-peak hours
```

---

## Performance Budgets

### Latency Percentiles

Understanding latency distributions is critical:

| Percentile | Meaning | User Impact |
|-----------|---------|------------|
| P50 | Median—typical user experience | "Is it fast?" |
| P95 | 95th percentile | Most users satisfied |
| P99 | 99th percentile—outliers | Worst-case users |

**Real-World Targets:**

```
Real-time APIs (chat, trading):
├── P50 < 50ms
├── P90 < 100ms
└── P99 < 300ms

Web App APIs (traditional web):
├── P50 < 200ms
├── P90 < 500ms
└── P99 < 1s

Search APIs (general):
├── P50 < 100ms
├── P95 < 200ms
└── P99 < 500ms
```

### Setting Performance Budgets

**OpenTelemetry Integration:**

```javascript
const { MeterProvider } = require('@opentelemetry/sdk-metrics');
const meter = new MeterProvider().getMeter('search-service');

const searchLatency = meter.createHistogram('search.latency', {
  unit: 'ms',
  description: 'Search query latency'
});

// Record latency
const start = Date.now();
const results = await performSearch(query);
searchLatency.record(Date.now() - start);
```

**SLO Definition:**

```
SLO: Search queries ≤ 100ms (P95)
Budget: 5% of errors/slowness allowed per month
- If 99.95% of queries meet SLO → we're tracking well
- If <99.95% → triggers incident response
```

### Throughput Targets

Indexing throughput depends on:

- Document size (KB per document)
- Refresh interval setting
- Hardware resources (CPU, disk I/O, memory)
- Number of shards

**Typical Benchmarks:**

```
Small documents (< 1KB):
├── Single thread: 10K-50K docs/second
├── 16 threads: 100K-200K docs/second
└── Distributed: 1M+ docs/second

Large documents (> 10KB):
├── Single thread: 1K-5K docs/second
├── 16 threads: 10K-50K docs/second
└── Distributed: 100K+ docs/second
```

### Monitoring and Alerting

```yaml
alerts:
  - name: HighSearchLatency
    condition: search_p99_latency > 500ms
    action: page on-call

  - name: IndexingThroughputDrop
    condition: indexing_rate < baseline * 0.8
    action: investigate resource usage

  - name: IndexFragmentation
    condition: deleted_docs_ratio > 0.2
    action: trigger segment merge
```

---

## Architecture Diagrams

### Real-Time Search with CDC

```
┌──────────────────────────────────────────────────────────┐
│ Source Systems                                           │
├──────────────────────────────────────────────────────────┤
│ PostgreSQL │ MySQL │ MongoDB │ DynamoDB                 │
└──────┬──────────────────────────────────┬────────────────┘
       │                                  │
       ▼                                  ▼
┌──────────────────────────────────────────────────────────┐
│ Debezium (CDC Platform)                                  │
├──────────────────────────────────────────────────────────┤
│ PostgresConnector │ MySQLConnector │ MongoConnector     │
└──────┬──────────────────────────────────┬────────────────┘
       │                                  │
       ▼                                  ▼
┌──────────────────────────────────────────────────────────┐
│ Kafka Topic: search-events                               │
├──────────────────────────────────────────────────────────┤
│ Partitions: 16 │ Replication: 3 │ Retention: 7 days    │
└──────┬──────────────────────────────────┬────────────────┘
       │                                  │
    ┌──┴──────┬───────────┬──────┐        │
    │          │           │      │        │
    ▼          ▼           ▼      ▼        ▼
 [ES Core] [ES Logs] [Cache] [Analytics] [Other Services]
```

### Event-Driven CQRS Search

```
┌────────────────────┐
│ Write Service      │
│ ├─ Receives update │
│ └─ Publishes event │
└────────┬───────────┘
         │
         ▼
    ┌─────────────┐
    │ Event Store │
    │ (Kafka)     │
    └────┬────────┘
         │
    ┌────┴──────────────────┐
    │                       │
    ▼                       ▼
┌────────────┐      ┌──────────────┐
│ Search     │      │ Analytics    │
│ Projection │      │ Projection   │
│ (ES)       │      │ (Data Lake)  │
└────────────┘      └──────────────┘
    │
    ▼
 [Query API]
```

### Client-Side Search with Web Workers

```
┌────────────────────────────┐
│ Main Thread (UI)           │
├────────────────────────────┤
│ ├─ User interaction        │
│ ├─ DOM updates             │
│ └─ Message passing         │
└──────┬──────────────────────┘
       │ postMessage
       ▼
┌────────────────────────────┐
│ Web Worker (Background)    │
├────────────────────────────┤
│ ├─ Build FST index         │
│ ├─ Execute search queries  │
│ └─ Return results via msg  │
└────────┬───────────────────┘
         │ postMessage
         ▼
┌────────────────────────────┐
│ SharedArrayBuffer (Shared) │
├────────────────────────────┤
│ ├─ Large datasets          │
│ ├─ Zero-copy access        │
│ └─ Atomic operations       │
└────────────────────────────┘
```

---

## Implementation Patterns

### Pattern 1: Real-Time Dashboard with SSE

```javascript
// Server: Stream updates as they arrive
app.get('/dashboard/search-updates', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');

  const sendUpdate = (data) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  // Send heartbeat to keep connection alive
  const heartbeat = setInterval(() => {
    res.write(': heartbeat\n\n');
  }, 30000);

  // Handle cleanup
  req.on('close', () => clearInterval(heartbeat));

  // Subscribe to index updates
  indexEmitter.on('document-indexed', sendUpdate);
  indexEmitter.on('query-result', sendUpdate);
});

// Client: Receive and render updates
const eventSource = new EventSource('/dashboard/search-updates');
eventSource.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  if (type === 'document-indexed') {
    addToIndex(data);
    updateStatistics();
  }
};
```

### Pattern 2: Hybrid Auto-Complete with FST Refresh

```javascript
class HybridAutoComplete {
  constructor() {
    this.fst = null;
    this.localCache = new Map();
    this.lastRefresh = 0;
    this.initializeAsync();
  }

  async initializeAsync() {
    // Load FST in background without blocking
    const response = await fetch('/api/completion/fst');
    const buffer = await response.arrayBuffer();
    this.fst = new FST(buffer);
    this.lastRefresh = Date.now();

    // Refresh every hour
    setInterval(() => this.refreshFST(), 3600000);
  }

  async search(prefix) {
    // Return from cache first
    if (this.localCache.has(prefix)) {
      return this.localCache.get(prefix);
    }

    // FST loaded and fresh
    if (this.fst && Date.now() - this.lastRefresh < 3600000) {
      const results = this.fst.search(prefix);
      this.localCache.set(prefix, results);
      return results;
    }

    // Fallback to server
    const results = await fetch(`/api/completion?q=${prefix}`)
      .then(r => r.json());
    this.localCache.set(prefix, results);
    return results;
  }

  async refreshFST() {
    try {
      const response = await fetch('/api/completion/fst');
      const buffer = await response.arrayBuffer();
      this.fst = new FST(buffer);
      this.lastRefresh = Date.now();
      this.localCache.clear(); // Clear cache on update
    } catch (error) {
      console.error('FST refresh failed, keeping current version');
    }
  }
}
```

### Pattern 3: Incremental Indexing with Soft Deletes

```javascript
class IncrementalIndexer {
  constructor(elasticsearch) {
    this.es = elasticsearch;
    this.lastIndexTime = null;
  }

  async indexIncrementalChanges() {
    const since = this.lastIndexTime || new Date(0);

    // Fetch updated documents
    const changes = await this.getChanges(since);

    if (changes.length === 0) return { indexed: 0, deleted: 0 };

    const bulk = [];

    for (const change of changes) {
      if (change.operation === 'delete') {
        // Soft delete: set timestamp
        bulk.push(
          { update: { _index: 'documents', _id: change.id } },
          { doc: { deleted_at: new Date() } }
        );
      } else {
        // Index or update document
        bulk.push(
          { index: { _index: 'documents', _id: change.id } },
          change.document
        );
      }
    }

    // Execute bulk operation
    const response = await this.es.bulk({ body: bulk });

    this.lastIndexTime = new Date();

    return {
      indexed: response.body.items.filter(i => !i.index?.error).length,
      deleted: response.body.items.filter(i => !i.update?.error).length
    };
  }

  async getChanges(since) {
    // Implementation depends on data source
    // Could query database changelog, Kafka, etc.
  }

  async shouldTriggerFullReindex() {
    const stats = await this.es.indices.stats({ index: 'documents' });
    const deletedRatio = stats.body.indices.documents.deleted /
                        stats.body.indices.documents.count;

    // Trigger if >20% deleted
    return deletedRatio > 0.2;
  }
}
```

---

## Performance Checklist

- [ ] **Refresh Interval:** Configured appropriately for use case (1s default, adjust for your needs)
- [ ] **Latency Budgets:** P50, P95, P99 targets established and monitored
- [ ] **Indexing Throughput:** Measured and alerts set for degradation
- [ ] **CDC Pipeline:** Data changes flow to search within SLA
- [ ] **Soft Deletes:** Implemented to avoid index fragmentation
- [ ] **Segment Merging:** Scheduled during off-peak hours
- [ ] **Web Workers:** Used for computationally expensive operations
- [ ] **Auto-Complete:** FST-based with periodic refresh
- [ ] **SSE/WebSocket:** Appropriate protocol selected for use case
- [ ] **Monitoring:** OpenTelemetry or similar instrumenting all operations
- [ ] **Fallbacks:** Graceful degradation when services unavailable
- [ ] **Testing:** Load testing at expected QPS and document size

---

## Key Takeaways

1. **Real-time search requires architectural decisions:** Choose between Elasticsearch refresh intervals, Meilisearch instant indexing, or CDC-based approaches
2. **Streaming architectures enable scale:** SSE for simple updates, WebSocket for interactive features
3. **Reverse search powers new UX:** Persistent queries enable product alerts and real-time notifications
4. **Auto-complete FSTs compress efficiently:** At scale, FSTs save 40-60% memory vs. tries
5. **Performance budgets prevent drift:** P50, P95, P99 targets must be established and enforced
6. **Event-driven architectures decouple:** CQRS + event sourcing enable independent evolution
7. **Client-side search offloads servers:** Web Workers + SharedArrayBuffer enable responsive UX
8. **Incremental indexing balances consistency:** Soft deletes and periodic rebuilds prevent fragmentation
9. **CDC platforms enable data flow:** Debezium + Kafka decouple sources from search indexes
10. **Monitoring is non-negotiable:** Latency, throughput, and index health must be continuously tracked

---

## References and Sources

- [Elasticsearch Near Real-Time Search](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search)
- [Elasticsearch Refresh Interval Documentation](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-refresh)
- [Meilisearch: Lightning-Fast Search Engine](https://www.meilisearch.com/)
- [Debezium: Change Data Capture Platform](https://debezium.io/)
- [Debezium CDC with Kafka Integration](https://www.conduktor.io/glossary/implementing-cdc-with-debezium)
- [Reverse Search in Elasticsearch: Product Alerts](https://medium.com/@halilbulentorhon/reverse-search-in-elasticsearch-product-alerts-and-rule-validation-with-percolate-6e7da5feb044)
- [WebSockets vs SSE for Real-Time Communication](https://www.svix.com/resources/faq/websocket-vs-sse/)
- [SSE Benefits for Real-Time Apps](https://dev.to/polliog/server-sent-events-beat-websockets-for-95-of-real-time-apps-heres-why-a4l)
- [Event Sourcing and CQRS with Kafka](https://developer.confluent.io/courses/event-sourcing/cqrs/)
- [Confluent: Event Sourcing CQRS Kafka Connection](https://www.confluent.io/blog/event-sourcing-cqrs-stream-processing-apache-kafka-whats-connection/)
- [FST in Autocomplete Systems](https://medium.com/search-it/role-of-fst-in-autocomplete-system-071b704e42cd)
- [Lucene FST Implementation](https://blog.mikemccandless.com/2010/12/using-finite-state-transducers-in.html)
- [FSTs vs Tries in Search](https://msfroh.github.io/lucene-university/docs/FiniteStateTransducers.html)
- [Incremental Indexing with Delta Updates](https://help.hcl-software.com/commerce/9.1.0/search/concepts/csdsearchcontentstructureindex.html)
- [Soft Deletes and Index Fragmentation](https://medium.com/rocksetcloud/updates-inserts-deletes-challenges-to-avoid-when-indexing-mutable-data-in-elasticsearch-c0eeff595865)
- [Web Workers and SharedArrayBuffer Performance](https://medium.com/@maximdevtool/web-workers-sharedarraybuffer-parallel-computing-for-heavy-algorithms-in-frontend-662391ae0558)
- [Web Workers Guide](https://medium.com/@subhasmitasahoo.247/web-worker-a5692a86765e)
- [js-worker-search Library](https://github.com/bvaughn/js-worker-search)
- [P50 P99 Latency Percentiles](https://oneuptime.com/blog/post/2025-09-15-p50-p95-p99-latency-percentiles/view)
- [Performance Budgets with OpenTelemetry](https://oneuptime.com/blog/post/2026-02-06-otel-performance-budgets-latency-histograms/view)
- [Understanding P99 Latency](https://aerospike.com/blog/what-is-p99-latency/)

---

**Document Version:** 1.0
**Last Updated:** 2026-03-01
**Status:** Complete - Ready for Knowledge Base Integration
