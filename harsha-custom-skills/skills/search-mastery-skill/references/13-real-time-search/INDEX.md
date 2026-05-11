# Real-Time Search Knowledge Base - Index

## Overview
This directory contains comprehensive knowledge on building, operating, and optimizing real-time search systems at scale. Covers millisecond-level indexing through streaming queries.

## Files

### real-time-search-encyclopedia.md (3,763 words)
**Comprehensive reference covering:**

1. **Real-Time Indexing Fundamentals**
   - Elasticsearch refresh_interval mechanics
   - Meilisearch instant indexing approach
   - Trade-offs between refresh frequencies

2. **Streaming Search Architecture**
   - Persistent queries (reverse search)
   - Percolate queries for product alerts
   - Ping servers for real-time content notification

3. **Change Data Capture (CDC)**
   - Debezium platform architecture
   - Kafka integration patterns
   - Event sourcing for index updates

4. **Client-Side Search**
   - Web Workers for non-blocking indexing
   - SharedArrayBuffer for zero-copy communication
   - js-worker-search library reference

5. **Real-Time Protocols**
   - WebSocket vs SSE comparison
   - When to use each for search
   - Implementation patterns

6. **Index Refresh Strategies**
   - Immediate vs batch refresh
   - Write-ahead logs for durability
   - Configurable refresh per use case

7. **Event-Driven Architecture**
   - CQRS pattern for search
   - Event sourcing foundations
   - Kafka + Elasticsearch patterns

8. **Auto-Complete at Scale**
   - Trie-based foundations
   - FST (Finite State Transducer) optimization
   - Memory efficiency (40-60% savings)
   - Server-side vs client-side approaches
   - Hybrid implementations

9. **Incremental Indexing**
   - Delta updates vs full rebuilds
   - Soft deletes strategy
   - Index fragmentation prevention
   - Segment merging

10. **Performance Budgets**
    - Latency percentiles (P50, P95, P99)
    - Throughput targets
    - OpenTelemetry instrumentation
    - SLO definition and enforcement

## Key Topics at a Glance

| Topic | Key Points | References |
|-------|-----------|------------|
| **Real-Time Indexing** | Elasticsearch: 1s default, configurable refresh. Meilisearch: <50ms search-as-you-type | Elastic, Meilisearch docs |
| **Streaming** | SSE for 95% of cases. WebSocket for bidirectional. | Svix, WebSocket.org |
| **CDC** | Debezium + Kafka for decoupled index updates | Debezium, Confluent |
| **Performance** | P50 < 100ms, P95 < 200ms, P99 < 500ms for search | OneUptime, Aerospike |
| **Auto-Complete** | FST-based saves 40-60% vs trie. Hybrid approach recommended | Medium articles |
| **Incremental Index** | Soft deletes, delta updates, periodic full rebuild | HCL Commerce docs |

## Quick Reference: Choosing Approaches

### For Real-Time Dashboards
- **Indexing:** Elasticsearch with 200ms refresh_interval
- **Streaming:** Server-Sent Events (SSE)
- **Performance Target:** P50 < 100ms, P99 < 200ms
- **Implementation:** Pattern 1 in encyclopedia

### For Product Search with Alerts
- **Indexing:** Meilisearch or Elasticsearch
- **Query Pattern:** Reverse search (Percolate)
- **CDC:** Debezium for product catalog changes
- **Performance Target:** P50 < 50ms, P99 < 100ms
- **Implementation:** Pattern 1 with reverse search

### For Auto-Complete at Scale
- **Data Structure:** FST (not trie)
- **Approach:** Hybrid (server + client-side FST)
- **Client:** Web Workers for index building
- **Performance Target:** < 10ms local, <50ms server
- **Implementation:** Pattern 2 in encyclopedia

### For High-Throughput Indexing
- **Strategy:** Event-driven with Kafka
- **Pattern:** CQRS + event sourcing
- **Refresh:** -1 (batch/manual)
- **Cleanup:** Periodic segment merging
- **Performance Target:** 100K-200K docs/sec (small documents)
- **Implementation:** Architecture diagram in encyclopedia

## Search Latency Targets

```
Real-time APIs:        P50 < 50ms,   P99 < 300ms
Web App APIs:          P50 < 200ms,  P99 < 1s
Search APIs (typical): P50 < 100ms,  P99 < 500ms
Dashboard updates:     P50 < 100ms,  P99 < 200ms
Auto-complete:        < 10ms (local), < 50ms (server)
```

## CDC Platforms

- **Debezium:** PostgreSQL, MySQL, MongoDB, Oracle, Cassandra
- **Kafka Connect:** Extensible framework
- **Native:** DynamoDB Streams, Kinesis, Change Feeds
- **Application-Level:** Event publishing from business logic

## FST vs Trie

| Characteristic | Trie | FST |
|---|---|---|
| Prefix compression | Yes | Yes |
| Suffix compression | No | Yes |
| Memory usage | Higher | 40-60% lower |
| Lookup complexity | O(k) per char | O(1) per char |
| Top-k caching | Manual | Built-in |
| Use in production | Elasticsearch completion, Solr | Elasticsearch completion, Solr, Rust fst crate |

## Architecture Patterns Included

1. **Real-Time Search with CDC:** PostgreSQL → Debezium → Kafka → Elasticsearch
2. **Event-Driven CQRS:** Write service → Event store → Projections (search, analytics)
3. **Client-Side Search:** Main thread ↔ Web Worker with SharedArrayBuffer
4. **Hybrid Auto-Complete:** Local FST + periodic server refresh
5. **SSE Dashboard:** Server-sent updates to real-time dashboard
6. **Incremental Indexing:** Delta updates with soft deletes, periodic rebuilds

## Implementation Patterns

Three complete patterns with code:

1. **Real-Time Dashboard with SSE** - Server streaming updates, client-side rendering
2. **Hybrid Auto-Complete with FST Refresh** - Local search + background updates
3. **Incremental Indexing with Soft Deletes** - Delta updates, fragmentation prevention

## Performance Checklist

- [ ] Refresh interval configured (1s default)
- [ ] Latency budgets established (P50, P95, P99)
- [ ] Indexing throughput measured
- [ ] CDC pipeline SLA met
- [ ] Soft deletes implemented
- [ ] Segment merging scheduled
- [ ] Web Workers for expensive operations
- [ ] FST-based auto-complete
- [ ] SSE or WebSocket chosen appropriately
- [ ] OpenTelemetry instrumentation active
- [ ] Fallback mechanisms in place
- [ ] Load testing completed

## When to Read Each Section

- **Just starting:** Read "Real-Time Indexing Fundamentals" and "Performance Budgets"
- **Building dashboards:** "Streaming Search Architecture" + "WebSocket and SSE Patterns"
- **High-volume indexing:** "Change Data Capture" + "Event-Driven Search Architecture"
- **Client-side features:** "Client-Side Search with Web Workers" + "Auto-Complete at Scale"
- **Operations:** "Index Refresh Strategies" + "Incremental Indexing"
- **Architecture planning:** All "Architecture Diagrams" + "Implementation Patterns"

## Key Insights

1. **No one-size-fits-all:** Choose refresh strategies based on throughput vs latency needs
2. **Streaming enables interactivity:** SSE/WebSocket make live updates possible
3. **CDC decouples:** Changes flow through Kafka, not direct database queries
4. **FSTs compress efficiently:** Use for auto-complete at scale
5. **Performance budgets prevent drift:** Establish P50/P95/P99 targets early
6. **Web Workers avoid blocking:** Offload expensive operations from UI thread
7. **Incremental indexing scales:** Use soft deletes and periodic rebuilds
8. **CQRS improves scalability:** Separate read and write projections
9. **Monitoring is essential:** Latency, throughput, index health must be tracked
10. **Eventual consistency acceptable:** Search indexes typically don't require strong consistency

## Search Speed Benchmarks (From Research)

| Component | Typical Performance |
|-----------|-------------------|
| Elasticsearch P99 search | 50-200ms |
| Meilisearch search-as-you-type | <50ms |
| FST auto-complete lookup | <1ms |
| Debezium to Elasticsearch lag | <1 second (typical) |
| SSE update latency | <100ms |
| Web Worker FST build | Varies (non-blocking) |
| Delta indexing throughput | 10K-100K docs/sec |

## Related Topics to Explore

- Full-text search fundamentals
- Search relevance and ranking
- Multi-language search
- Typo tolerance and fuzzy matching
- Search analytics and user insights
- Vector search and semantic matching
- Hybrid search (BM25 + vector)
- Search caching strategies

---

**Knowledge Base Version:** 1.0
**Last Updated:** 2026-03-01
**Audience:** Developers, architects, and SREs building real-time search systems
**Difficulty:** Intermediate to Advanced
