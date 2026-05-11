# STACK BLUEPRINTS: 10 Complete Search Architectures

Complete recommended technology stacks for 10 common search scenarios. Each blueprint includes architecture, technology reasoning, cost estimates, performance targets, and scaling paths.

---

## Blueprint 1: SaaS App Search (10K–500K docs)

**Scenario:** MVP startup building product/content search. Budget-conscious, small engineering team (2–4 engineers). Fast iteration, minimal ops overhead.

**Target Scale:** 10K–500K documents, 100–10K QPS, <100ms latency, single-region.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer                                           │
│ React + InstantSearch (Algolia client library)          │
│ Real-time filtering + facets + autocomplete             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Search Engine: Typesense                                 │
│ (Self-hosted or managed tier)                           │
│ • Full-text indexing                                     │
│ • Faceted search (30+ facets)                           │
│ • Typo tolerance                                         │
│ • Sub-second queries                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Data Pipeline                                            │
│ • CSV/JSON uploads via web UI                           │
│ • Typesense API for incremental updates                 │
│ • Simple retry logic (no message queue needed yet)      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Analytics (Optional)                                     │
│ • Segment + Mixpanel (free tier) for user behavior      │
│ • Search quality metrics via custom logging             │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Search Engine** | Typesense | Simpler than Elasticsearch, better defaults, instant deploy (no config tuning). Free tier covers startup phase. |
| **Frontend UI** | React + InstantSearch | Industry standard. Works with Typesense via connector library. Instant, interactive results. |
| **Data Ingestion** | Direct API | No Kafka/RabbitMQ yet. Bulk indexing API + periodic CSV imports sufficient. |
| **Monitoring** | CloudWatch (AWS) logs | Free tier adequate. Typesense dashboard covers uptime. |
| **Deployment** | Docker on AWS Lightsail or Render | ~$10–20/month. Easy scaling when ready. |

### Cost Estimate (Monthly at 100K docs, 1K QPS)

| Item | Cost |
|------|------|
| Typesense (self-hosted on Lightsail) | $15 |
| AWS Lightsail 2GB RAM instance | $12 |
| Data transfer | $3 |
| Segment free + Mixpanel | $0 |
| **Total** | **$30** |

### Performance Targets

- **Query Latency:** p50=10ms, p99=50ms
- **Throughput:** 1–5K QPS sustained
- **Index Freshness:** 1–5 min (batch updates)
- **Availability:** 99.5% (single instance acceptable for MVP)

### Scaling Path (10x → 100K–5M docs)

1. **At 500K docs:** Add read replicas to Typesense (built-in HA mode). Cost +$15/month.
2. **At 2M docs:** Migrate to Elasticsearch for advanced ranking + ML features. Reindex via Logstash pipeline.
3. **At 5M docs:** Add distributed Elasticsearch cluster (3 nodes). Introduce Kafka for real-time ingestion. Cost jumps to $200–500/month.

### See Also

→ See: `references/01-typesense-setup/`
→ See: `references/02-react-instantsearch-guide/`
→ See: `references/03-search-quality-metrics/`
→ See: `references/04-cost-optimization/`

---

## Blueprint 2: AI-First Knowledge Base (RAG)

**Scenario:** Company building an AI assistant to answer questions over internal docs, wikis, and help center. Intent: augment LLM with retrieved context.

**Target Scale:** 10K–100K documents, 50–500 QPS, <500ms end-to-end (retrieval + LLM), multi-region desired.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer                                           │
│ React/Next.js + custom chat UI                          │
│ Real-time streaming responses                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Orchestration: LangChain (Python)                        │
│ • Query rewriting + retrieval chain                      │
│ • Context window management                             │
│ • Tool calling for multi-step QA                        │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌──────────────────┴──────────────────┐
       ↓                                      ↓
┌─────────────────────────┐    ┌────────────────────────┐
│ Dense Retrieval         │    │ Reranking              │
│ Qdrant Vector DB        │    │ Cohere Rerank v3       │
│ • HNSW ANN              │    │ • Cross-encoder        │
│ • Hybrid text+vector    │    │ • Relevance scoring    │
└─────────────────────────┘    └────────────────────────┘
       ↓                                      ↓
       └──────────────────┬──────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Embeddings Model                                         │
│ Cohere embed-v3 (multilingual, 1024-dim)               │
│ • 10K free embeddings/month                             │
│ • $1/M tokens after                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ LLM: OpenAI GPT-4 / Anthropic Claude                     │
│ • Few-shot examples in system prompt                     │
│ • Context injection from retrieved docs                 │
│ • Chain-of-thought for reasoning                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Data Ingestion Pipeline                                 │
│ • Langchain document loader (Slack, Sheets, Confluence) │
│ • Recursive text splitter (1K token chunks, 200 overlap) │
│ • Batch embedding + Qdrant upsert                       │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Vector DB** | Qdrant | Battle-tested for RAG. Hybrid BM25+dense search. Free tier. API-first. |
| **Embeddings** | Cohere embed-v3 | Multilingual, optimized for semantic search. Best cost/quality. OpenAI too expensive for volume. |
| **Reranker** | Cohere Rerank v3 | Cross-encoder that re-scores top-K results. 10–50ms overhead, massive accuracy gain. |
| **Orchestration** | LangChain | Abstraction over retrieval chain logic. Easy swaps (model, DB, retriever). |
| **LLM** | Claude 3.5 Sonnet | Strong reasoning + longer context window (200K). Better for doc QA than GPT-4. |

### Cost Estimate (Monthly at 50K docs, 200 QPS)

| Item | Cost |
|------|------|
| Qdrant Cloud (512MB, 1000 vectors) | $20 |
| Cohere Embed (2M tokens/month at $1/M) | $2 |
| Cohere Rerank (500K reranks/month) | $50 |
| Claude 3.5 Sonnet (avg 2K input + 500 output tokens/query) | $180 |
| Compute (Docker on AWS/GCP) | $25 |
| **Total** | **$277** |

### Performance Targets

- **Retrieval Latency:** p50=50ms, p99=200ms (Qdrant)
- **Rerank Latency:** p50=30ms, p99=80ms
- **LLM Generation:** p50=800ms, p99=2s (streaming)
- **End-to-End:** p99=3s
- **Answer Quality:** MRR@10 > 0.8, RAGAS score > 0.7

### Scaling Path (10x → 100K–1M docs)

1. **At 100K docs:** Upgrade Qdrant to higher tier. Introduce caching layer (Redis) for popular Q&A pairs.
2. **At 500K docs:** Switch to self-hosted Qdrant cluster. Implement query decomposition (HyDE). Add fallback LLM.
3. **At 1M docs:** Add multi-stage retrieval (BM25 → dense → rerank → LLM). Use prompt engineering to trade cost/quality.

### See Also

→ See: `references/05-rag-fundamentals/`
→ See: `references/06-vector-db-comparison/`
→ See: `references/07-prompt-engineering-qa/`
→ See: `references/08-retrieval-metrics/`

---

## Blueprint 3: E-Commerce Product Search

**Scenario:** Online store with 50K–5M products. Need rich filtering, faceting, merchandising, and ML-powered ranking. Team of 4–8 engineers.

**Target Scale:** 50K–5M products, 5K–50K QPS, <100ms latency, near real-time inventory sync.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer                                           │
│ Next.js + React component library                       │
│ • Search bar (typeahead)                                │
│ • Facet sidebar (price, brand, color, size)            │
│ • Sorting + merchandising UI                            │
│ • InstantSearch or custom Apollo client                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Search API Gateway                                       │
│ Node.js / FastAPI backend                               │
│ • Query rewriting (typo correction)                      │
│ • Personalization (user ID → signals)                    │
│ • A/B testing wrapper                                    │
│ • Rate limiting (API key auth)                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Search Engine: Elasticsearch (or OpenSearch)             │
│ • Product index (SKU, title, description, attributes)  │
│ • Numeric/categorical facets                            │
│ • BM25 + custom script scoring                          │
│ • Autocomplete via completion suggester                 │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌──────────────────┴──────────────────┐
       ↓                                      ↓
┌─────────────────────────┐    ┌────────────────────────┐
│ ML Ranking Pipeline     │    │ Feature Store          │
│ (Python + scikit-learn) │    │ Tecton / Vertex AI     │
│ • Two-tower retrieval   │    │ • User behavior        │
│ • LambdaMART or XGBoost │    │ • Product signals      │
│ • Real-time serving     │    │ • Historical CTR/sales │
└─────────────────────────┘    └────────────────────────┘
       ↓                                      ↓
       └──────────────────┬──────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Ingestion Pipeline                                       │
│ • Product feed (CSV/API from inventory system)          │
│ • Kafka for inventory updates (real-time stock)         │
│ • Logstash → Elasticsearch bulk indexing                │
│ • 2–5 min reindex cadence                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Analytics & Monitoring                                   │
│ • ELK Stack (Elasticsearch logs + Kibana)               │
│ • Custom dashboards (query latency, MRR, CVR)           │
│ • A/B testing framework (Statsig or LaunchDarkly)       │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Search Engine** | Elasticsearch 8+ | Industry standard for e-commerce. Rich faceting, script scoring, powerful query DSL. Algolia too expensive at 5M SKUs. |
| **ML Ranking** | XGBoost + LambdaMART | Proven for e-commerce. Captures CTR, revenue, freshness signals. Retrains weekly. |
| **Feature Store** | Tecton (managed) | Centralized feature engineering. Real-time + batch pipelines. Reduces ML engineering overhead. |
| **Ingestion** | Kafka + Logstash | Decouples product feed from search. Kafka handles spikes. Logstash transforms before ES indexing. |
| **Analytics** | Kibana + custom Grafana | Kibana for ad-hoc search debugging. Grafana for SLO monitoring. |

### Cost Estimate (Monthly at 500K products, 20K QPS)

| Item | Cost |
|------|------|
| Elasticsearch (self-hosted, 3 data nodes, 32GB each) | $150 |
| Kafka cluster (3 brokers) | $80 |
| Logstash pipeline (t3.medium) | $30 |
| Feature store (Tecton standard) | $200 |
| ML training (weekly, GPU batch job) | $50 |
| Monitoring (Grafana Cloud) | $30 |
| **Total** | **$540** |

### Performance Targets

- **Query Latency:** p50=15ms, p99=80ms (Elasticsearch)
- **Throughput:** 20–50K QPS sustained
- **Index Freshness:** 2–5 min (near real-time)
- **ML Model Latency:** <30ms (batch scoring)
- **Metrics:** MRR@10 > 0.75, CVR +15% vs. baseline ranking

### Scaling Path (10x → 5M products)

1. **At 500K–1M products:** Partition index by category. Add dedicated ML nodes (compute separation).
2. **At 1M–3M products:** Implement tiered ranking (fast filter → stage 1 ML → stage 2 LambdaMART). Kafka consumer group scaling.
3. **At 3M–5M products:** Multi-region Elasticsearch (async replication). Distributed ML serving (Seldon/KServe). Budget: $2K–3K/month.

### See Also

→ See: `references/09-elasticsearch-scale/`
→ See: `references/10-ml-ranking-ecommerce/`
→ See: `references/11-feature-engineering/`
→ See: `references/12-search-ab-testing/`

---

## Blueprint 4: Enterprise Workplace Search

**Scenario:** 500-person company searching across Slack, Google Docs, Jira, GitHub, Email. Single unified search for knowledge discovery.

**Target Scale:** 1M+ documents (varied types), 1K–5K QPS, <1s latency, 99.99% uptime critical.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer                                           │
│ Chrome plugin + web UI (Next.js)                         │
│ • Unified search bar (Cmd+K)                             │
│ • Filter by source (Slack, Docs, Jira, etc.)           │
│ • People + content + conversations                      │
│ • Real-time collaboration context                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Search API Gateway (Enterprise)                          │
│ Node.js + gRPC backend                                  │
│ • Auth integration (SAML/OAuth)                          │
│ • Row-level security (only see docs you have access to) │
│ • Query routing to source-specific indices               │
│ • Rate limiting + audit logging                          │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌───────────────────┬───────────────────┐
       ↓                   ↓                   ↓
 ┌──────────┐      ┌──────────┐      ┌──────────┐
 │Slack     │      │Docs      │      │Jira      │
 │ Elastic  │      │ Elastic  │      │ Elastic  │
 │ Index    │      │ Index    │      │ Index    │
 └──────────┘      └──────────┘      └──────────┘
       ↓                   ↓                   ↓
┌─────────────────────────────────────────────────────────┐
│ Central Unified Elasticsearch Cluster                     │
│ • 6–10 nodes across 3 AZs                               │
│ • Separate index templates per source                    │
│ • Cross-index search via aliases                         │
│ • Snapshot repo for backup/recovery                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Connector Framework                                       │
│ • Slack: Bolt SDK + real-time Events API                │
│ • Google Docs: Drive API + periodic crawl               │
│ • Jira: REST API + webhook triggers                     │
│ • GitHub: GraphQL API + push events                     │
│ • Email: Connector server (OAuth) with IMAP             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Ingestion Orchestration (Airflow)                        │
│ • DAG per source (Slack hourly, Docs daily, Jira event) │
│ • Error handling + retry logic                           │
│ • Incremental sync (delta updates)                       │
│ • Monitoring alerts                                      │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Search Engine** | Elasticsearch 8.x | Handles 1M+ mixed-type documents well. Cross-index search. Role-based access control (RBAC) via Kibana. |
| **Connectors** | Custom (Bolt + Drive + Jira APIs) | Enterprise sources have official APIs. Custom connectors cheaper than third-party SaaS (Coveo, Algolia). |
| **Orchestration** | Apache Airflow | Manages complex DAGs. Retry logic built-in. Better than manual cron jobs. |
| **Auth/Security** | Elasticsearch + Okta SAML | Native LDAP/SAML in Enterprise tier. Row-level filtering via document-level security (DLS). |
| **HA/DR** | Multi-AZ Elasticsearch + automated snapshots | 99.99% uptime requires redundancy. Snapshots to S3 for disaster recovery. |

### Cost Estimate (Monthly at 1M docs, 3K QPS)

| Item | Cost |
|------|------|
| Elasticsearch Cloud (Enterprise, 200GB) | $800 |
| Airflow orchestration (managed, Astronomer) | $400 |
| Okta SSO integration | $2 (per user, ~500 users) = $1000 |
| Backup + snapshot storage (S3) | $50 |
| Compute for connectors (t3.large) | $60 |
| **Total** | **$2,310** |

### Performance Targets

- **Query Latency:** p50=200ms, p99=800ms (complex cross-index)
- **Throughput:** 3–5K QPS sustained
- **Index Freshness:** Slack (hourly), Docs (daily), Jira (real-time event)
- **Availability:** 99.99% (RTO 4h, RPO 1h)
- **Security:** 100% row-level filtering enforced

### Scaling Path (10x → 10M+ documents)

1. **At 2M docs:** Add secondary Elasticsearch cluster for geo-distribution (EU/US). Async replication.
2. **At 5M docs:** Separate "hot" (recent) from "cold" (archive) indices. ILM policies for auto-archival to cheaper tier.
3. **At 10M+ docs:** Distributed connectors (Kafka-based pull model). Introduce vector search for semantic "did you mean?" suggestions.

### See Also

→ See: `references/13-enterprise-connector-patterns/`
→ See: `references/14-document-level-security/`
→ See: `references/15-airflow-data-pipelines/`
→ See: `references/16-elasticsearch-ops/`

---

## Blueprint 5: Blog/Documentation Site Search

**Scenario:** Static site (Hugo, Jekyll, Next.js) or docs platform (Docusaurus, Sphinx) needs instant client-side search with no backend.

**Target Scale:** 1K–100K pages, instant (0-latency), <5KB index file.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer                                           │
│ HTML/React with Cmd+K search modal                       │
│ • No external API calls                                  │
│ • Index loaded in browser (WASM optional)               │
│ • Instant highlighting + keyboard nav                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Search Index (Static Generation)                         │
│ Pagefind (if static) OR Orama (if dynamic)              │
│ • Generated at build time                               │
│ • Stored in /search/ directory                          │
│ • Gzip-compressed (1–5MB for 50K pages)                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Build Pipeline (CI/CD)                                   │
│ GitHub Actions / Netlify / Vercel                        │
│ • Run Pagefind at build time                            │
│ • Commit index to repo or upload to CDN                 │
│ • Deploy to static host (Netlify, Vercel, S3+CloudFront) │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Delivery                                                  │
│ Global CDN (Netlify / Vercel / CloudFront)              │
│ • Cache forever (index regenerated on each deploy)      │
│ • Sub-100ms delivery worldwide                          │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Index** | Pagefind (static) | Zero-config. WASM-based. Ships as <1MB binary. Perfect for Hugo/Jekyll/Docusaurus. No API needed. |
| **Search Lib** | Orama (if dynamic) | WASM + JS. Works for dynamic content. Smaller footprint than Lunr. Real-time indexing possible. |
| **UI** | Custom React modal or Algolia DocSearch | DocSearch is free for open-source docs. Custom modal if more control needed. |
| **CDN** | Netlify or Vercel | Auto-deploy on git push. Free tier adequate for most projects. Built-in image optimization. |

### Cost Estimate (Monthly at 50K pages)

| Item | Cost |
|------|------|
| Netlify (or Vercel) free tier | $0 |
| Custom domain + SSL | $0 (auto included) |
| CDN bandwidth (50K pages × 1MB × 10K monthly views) | ~$1 |
| **Total** | **$1** (or free with free tier) |

### Performance Targets

- **Query Latency:** p50=1ms, p99=5ms (client-side)
- **Page Load:** <50ms additional (search index in vendor bundle)
- **Availability:** 100% (no server dependency)
- **Search Quality:** Exact match + fuzzy + phrase search

### Scaling Path (10x → 1M pages)

1. **At 100K pages:** Index size ~10MB. Switch to gzip + lazy-load. Pagefind handles this natively.
2. **At 500K pages:** Split index by section (docs, guides, API). User loads relevant subset on demand.
3. **At 1M pages:** Move to backend API (Typesense or Meilisearch). Pagefind not suitable; trade simplicity for scale.

### See Also

→ See: `references/17-pagefind-integration/`
→ See: `references/18-static-site-build-pipelines/`
→ See: `references/19-algolia-docssearch/`
→ See: `references/20-cdn-caching-strategies/`

---

## Blueprint 6: Real-Time Event/Log Search

**Scenario:** SaaS platform, infrastructure tool, or analytics needs to search logs, events, APM traces in real-time. DevOps or security team.

**Target Scale:** 100GB–10TB logs/day, 1M+ events/sec, <5s search latency, 7–30 day retention.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Log Collection Layer                                     │
│ Filebeat (on servers) + syslog (network devices)        │
│ • Lightweight agent shipping logs to Kafka              │
│ • No loss (local buffering)                              │
│ • TLS encryption in transit                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Message Queue: Apache Kafka                              │
│ • Log topic (3 partitions, 7-day retention)             │
│ • 100K msg/sec throughput                               │
│ • Decouples producers from storage                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Processing & Enrichment                                  │
│ Logstash OR Kafka Streams                                │
│ • Parse JSON + extract fields (timestamp, level, msg)   │
│ • GeoIP enrichment (IP → city)                          │
│ • Rate limiting rules                                    │
│ • Send to Elasticsearch + real-time alerts              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Time-Series Search: Elasticsearch                        │
│ • ILM policy (daily indices, 30-day hot)               │
│ • 10–20 data nodes (for 10TB/day)                       │
│ • Sharding by time + tenant ID                          │
│ • Ad-hoc queries + saved searches                       │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌──────────────────┴──────────────────┐
       ↓                                      ↓
┌─────────────────────────┐    ┌────────────────────────┐
│ Visualization: Kibana   │    │ Alerting               │
│ • Real-time dashboards  │    │ • Elasticsearch alerts │
│ • Drill-down into logs  │    │ • PagerDuty/Slack     │
│ • Saved queries         │    │ • anomaly detection   │
└─────────────────────────┘    └────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Collection** | Filebeat + Logstash | Lightweight. Minimal overhead. Proven log shipping. Logstash for ETL. |
| **Queue** | Kafka | Handles 1M msgs/sec. Perfect decoupling. Topic replay for recovery. |
| **Storage** | Elasticsearch | Industry standard for logs. Time-series optimized in recent versions. Kibana included. |
| **Alerting** | Elasticsearch alerting + webhook | Native to ELK. Integrated with Slack/PagerDuty. Simple threshold rules. |

### Cost Estimate (Monthly at 10TB/day, 1M events/sec)

| Item | Cost |
|------|------|
| Elasticsearch (self-hosted, 15 data nodes, 1.5TB SSD each) | $900 |
| Kafka cluster (3 brokers, high throughput) | $300 |
| Logstash pipeline (3 processors, t3.xlarge each) | $150 |
| Kibana | $0 (included) |
| S3 archive (long-term cold storage, 100TB/month) | $2000 |
| **Total** | **$3,350** |

### Performance Targets

- **Ingest Latency:** p99 < 5s (end-to-end from log → searchable)
- **Query Latency:** p50=500ms, p99=3s (recent 7-day data)
- **Availability:** 99.95% (acceptable for operations)
- **Retention:** 30 days hot, 1 year cold archive
- **Data Volume:** 10TB/day sustained

### Scaling Path (10x → 100TB/day)

1. **At 20TB/day:** Add secondary Kafka cluster (fan-out). Elasticsearch cluster to 25 nodes.
2. **At 50TB/day:** Implement ES CCR (cross-cluster replication) for multi-region. Upgrade to hot/warm/cold tiers.
3. **At 100TB/day:** Shard strategy by time+tenant. Archive old indices to S3 + Glacier. Budget: $10K+/month.

### See Also

→ See: `references/21-elk-stack-setup/`
→ See: `references/22-kafka-log-streaming/`
→ See: `references/23-elasticsearch-ilm-policies/`
→ See: `references/24-log-alerting-patterns/`

---

## Blueprint 7: Multi-Language Global Search

**Scenario:** International SaaS serving 20+ languages across 6+ regions. Need to search & rank without language degradation.

**Target Scale:** 100K–1M docs (polyglot), 500–5K QPS across regions, <150ms p99.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer (Regional)                                │
│ Next.js with i18n (next-intl)                            │
│ • Language auto-detection (Accept-Language header)      │
│ • Regional routing (CDN edge, Vercel geo)              │
│ • Right-to-left (RTL) support                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ API Gateway (Language-aware)                             │
│ FastAPI / Node.js                                        │
│ • Language detection (langdetect or fasttext)           │
│ • Query normalization (Unicode, diacritics)             │
│ • Route to language-specific OR unified index           │
│ • Analytics per language + region                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Multilingual Embeddings Model                            │
│ BGE-M3 or Multilingual-E5 (HuggingFace)                 │
│ • 100+ language coverage                                │
│ • 1024–1536 dimensions                                  │
│ • Self-hosted (optional) or API (Jina, Cohere)         │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌───────────────┬───────────────┬───────────────┐
       ↓               ↓               ↓               ↓
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │English   │   │Spanish   │   │Chinese   │   │Arabic    │
 │Elastic   │   │Elastic   │   │Qdrant    │   │Qdrant    │
 │Index     │   │Index     │   │Vector DB │   │Vector DB │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘
       ↓               ↓               ↓               ↓
┌─────────────────────────────────────────────────────────┐
│ Central Reranker (Language-Agnostic)                      │
│ mBERT or XLM-R cross-encoder                             │
│ • Language-independent relevance scoring                │
│ • Re-ranks top-K from all indices                        │
│ • Single pooled endpoint                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Ingestion Pipeline (Polyglot)                            │
│ • Detect language via fasttext (99% accurate)           │
│ • Route to language-specific index                      │
│ • Embed in native language                              │
│ • Bigram indices for CJK languages                       │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Embeddings** | BGE-M3 | Open-source, 100+ langs, best multilingual semantic search. No API costs. Can self-host. |
| **Reranker** | XLM-R cross-encoder | Language-agnostic. Ranks relevance across languages equally. Smaller footprint than mBERT. |
| **Storage** | Elasticsearch + Qdrant hybrid | Elasticsearch for text (languages vary), Qdrant for vectors (language-neutral). |
| **Language Detection** | fastText (Facebook) | <1ms latency. 176 languages. Pre-trained model. |

### Cost Estimate (Monthly at 200K docs, 1K QPS, 20 languages)

| Item | Cost |
|------|------|
| Elasticsearch (5 nodes, one per major language cluster) | $250 |
| Qdrant (1 cluster, shared across vectors) | $50 |
| Embedding model (self-hosted on t3.large GPU) | $150 |
| Reranker (shared, t3.xlarge) | $100 |
| Regional CDN + API gateways (3 regions) | $200 |
| **Total** | **$750** |

### Performance Targets

- **Query Latency:** p50=80ms, p99=150ms (multi-index, rerank)
- **Throughput:** 1–5K QPS (burst to 10K)
- **Embedding Quality (per language):** Cosine similarity > 0.75 for synonyms
- **Ranking Fairness:** MRR@10 consistent across top 5 languages

### Scaling Path (10x → 2M docs, 40 languages)

1. **At 500K docs:** Add language-specific Elasticsearch clusters (EU, APAC, Americas). Separate embeddings endpoints per region.
2. **At 1M docs:** Implement multi-stage retrieval per language (BM25 → dense → cross-lingual rerank).
3. **At 2M docs:** Language-specific ML ranking models. Cross-lingual transfer learning for low-resource languages.

### See Also

→ See: `references/25-multilingual-embeddings/`
→ See: `references/26-bge-m3-guide/`
→ See: `references/27-cross-lingual-ranking/`
→ See: `references/28-language-detection/`

---

## Blueprint 8: Medical/Legal Domain Search

**Scenario:** Healthcare platform, law firm, or regulatory database searching highly specialized corpus. Terminology precision critical. Rare entities matter.

**Target Scale:** 10K–500K documents (dense domain content), 100–1K QPS, <500ms latency, high result quality.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer (Domain-Specific)                         │
│ React UI with term disambiguation                        │
│ • Show top synonyms (e.g., MI, myocardial infarction)   │
│ • Link to domain ontologies (ICD-10, SNOMED CT)         │
│ • Citation + source tracking                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Query Expansion Engine                                   │
│ Domain thesaurus + synonym expansion                     │
│ • Medical: MI → myocardial infarction, heart attack     │
│ • Legal: LLC → limited liability company, LLC           │
│ • Pharmacology: ACE inhibitor → lisinopril, enalapril  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Sparse (BM25) Retrieval                                  │
│ Elasticsearch with domain analyzers                      │
│ • Preserve medical abbreviations (no lowercasing)       │
│ • n-gram indexing (CJK-style for compound terms)        │
│ • Boost on exact field matches                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Dense Retrieval (Domain-Specific Embeddings)             │
│ SciNCL or BioBERT embeddings                             │
│ • Pre-trained on PubMed / legal corpora                 │
│ • Captures domain terminology relations                  │
│ • Fine-tuned on query-document pairs                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Cross-Encoder Reranking (Multi-Stage)                    │
│ Custom fine-tuned domain cross-encoder                   │
│ • Trained on domain expert relevance judgments          │
│ • SPLADE-variant for sparse features + semantics        │
│ • Top-20 re-scoring                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Entity Recognition & Linking                             │
│ spaCy (medical) or LegalBERT NER                         │
│ • Identify drug names, procedures, conditions          │
│ • Link to SNOMED CT, RxNorm, ICD-10 codes               │
│ • Inject entity context into ranking                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Evaluation & Quality Metrics                             │
│ NDCG@10, MRR, RAGAS score on hold-out test set         │
│ • Domain expert annotation (500–1K query-doc pairs)     │
│ • Monthly reranking model updates                        │
│ • Failure analysis on low-quality queries                │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Embeddings** | BioBERT or SciNCL | Domain pre-trained. Captures medical/legal terminology. Better than generic BERT. |
| **Reranker** | Fine-tuned domain cross-encoder | Generic cross-encoders often miss domain nuances. Custom training on 500 relevance judgments essential. |
| **Entity Recognition** | spaCy (med) or LegalBERT NER | Proven for domain NER. spaCy has medical model. Reduces false positives. |
| **Thesaurus** | Custom curated + SNOMED CT / RxNorm | Domain ontologies are gold. Medical records companies (Athena, Epic) expose APIs. Legal uses LexisNexis. |

### Cost Estimate (Monthly at 100K medical docs, 500 QPS)

| Item | Cost |
|------|------|
| Elasticsearch (3 nodes, high RAM for dense docs) | $120 |
| BioBERT embedding model (self-hosted on p3.2xlarge GPU) | $300 |
| Fine-tuned cross-encoder (shared, t3.xlarge CPU) | $80 |
| Entity recognition (spaCy, CPU) | $20 |
| Expert annotation for reranking (outsourced, one-time) | $1000 (amortized) |
| Domain ontology licenses (SNOMED CT, RxNorm free) | $0 |
| **Total** | **$520/month** |

### Performance Targets

- **Query Latency:** p50=200ms, p99=500ms (multi-stage)
- **Throughput:** 500–1K QPS sustained
- **Ranking Quality:** NDCG@10 > 0.8, MRR > 0.85 (vs. expert baseline)
- **Entity Linking Accuracy:** >95% on common entities
- **Rare condition recall:** >70% (hard cases)

### Scaling Path (10x → 500K docs)

1. **At 200K docs:** Partition by specialty (cardiology, oncology). Separate domain models per partition.
2. **At 350K docs:** Federated search across specialties. Implement query-by-specialty routing.
3. **At 500K docs:** Knowledge graph (Neo4j) for entity relations (e.g., drug interactions). Graph-augmented ranking. Budget: $800+/month.

### See Also

→ See: `references/29-domain-embeddings/`
→ See: `references/30-cross-encoder-finetuning/`
→ See: `references/31-entity-recognition-linking/`
→ See: `references/32-domain-search-evaluation/`

---

## Blueprint 9: Image + Text Multimodal Search

**Scenario:** Visual commerce, design platform, or media platform searching across both images and text (e.g., Pinterest, product discovery, interior design).

**Target Scale:** 10M–100M images + metadata, 5K–50K QPS, <200ms latency, real-time ingestion.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Frontend Layer (Multimodal UI)                           │
│ React + WebGL canvas for image previews                  │
│ • Text search bar                                        │
│ • Image upload (reverse image search)                    │
│ • Filter by attributes (color, size, style)             │
│ • Search result mix (images + text results)              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Multimodal Search API                                    │
│ FastAPI + Redis caching                                  │
│ • Parse text query OR extract image embeddings          │
│ • Unified ranking of image + text results                │
│ • Personalization (user history)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
       ┌──────────────────┴──────────────────┐
       ↓                                      ↓
 ┌───────────────┐              ┌───────────────────┐
 │Text Search    │              │Image Search       │
 │Elasticsearch  │              │Qdrant Vector DB   │
 │• BM25 on text │              │• CLIP embeddings  │
 │• Metadata     │              │• Visual similarity│
 │• Filters      │              │• Similar searches │
 └───────────────┘              └───────────────────┘
       ↓                                      ↓
       └──────────────────┬──────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Multimodal Embeddings: CLIP / SigLIP                      │
│ • Text encoder (768-dim) + Image encoder (768-dim)      │
│ • Shared latent space (cosine similarity)                │
│ • Cross-modal search (text → images, images → text)     │
│ • Self-hosted or API (OpenAI CLIP, Jina)                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Image Processing Pipeline                                │
│ ImageMagick + CLIP encoder (GPU batch)                   │
│ • Resize to standard dimensions                          │
│ • Extract CLIP embeddings (batch 64)                     │
│ • OCR extraction (for text overlay in images)            │
│ • Upload to Qdrant + metadata to ES                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Ingestion (Real-Time)                                     │
│ Kafka + streaming image encoder                          │
│ • User uploads image → Kafka topic                       │
│ • Encoder service subscribes, generates embeddings       │
│ • Upsert to Qdrant + ES (1–2s end-to-end)               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Multimodal Reranking                                      │
│ CLIP-based scoring for final ranking                     │
│ • Blend text-to-image + text similarity scores           │
│ • Learn ranking weights from user clicks                 │
│ • Fast rerank (top 100)                                  │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Embeddings** | CLIP (OpenAI) or open-source ViT-B/32 | Standard for vision-language. Trained on 400M text-image pairs. Good zero-shot transfer. |
| **Vector DB** | Qdrant | HNSW efficient for high-dim (768) vectors. Built-in filtering on metadata. Scales to 100M. |
| **Text Search** | Elasticsearch | Hybrid search (BM25 + vector). Good for mixed queries. |
| **Image Processing** | Batch inference on GPU | GPU for CLIP encoding (1ms/image at batch 64). CPU bottleneck otherwise. |

### Cost Estimate (Monthly at 50M images, 20K QPS)

| Item | Cost |
|------|------|
| Qdrant (1TB vectors, cloud tier) | $500 |
| Elasticsearch (search metadata, 3 nodes) | $200 |
| CLIP GPU inference (2x V100, batch encoding jobs) | $400 |
| Kafka (streaming image uploads) | $150 |
| Image storage (S3, 50M images @ 1MB avg) | $1500 |
| CDN for image delivery (CloudFront) | $800 |
| **Total** | **$3,550** |

### Performance Targets

- **Text Search Latency:** p50=50ms, p99=150ms (ES)
- **Image Search Latency:** p50=80ms, p99=200ms (Qdrant + rerank)
- **Image Upload → Searchable:** <3s (ingestion + encode)
- **Throughput:** 20K QPS text, 5K QPS image uploads
- **Search Quality:** Recall@10 > 0.75 for visual similarity

### Scaling Path (10x → 500M images)

1. **At 100M images:** Shard Qdrant by category (apparel, furniture, etc.). Separate CLIP encoders per shard.
2. **At 250M images:** Multi-region Qdrant (HNSW replication). Local caching of popular embeddings (Redis).
3. **At 500M images:** Advanced: Quantized embeddings (8-bit) to reduce storage 10x. Approximate nearest neighbor trade-off. Budget: $10K+/month.

### See Also

→ See: `references/33-clip-multimodal-search/`
→ See: `references/34-image-embedding-pipelines/`
→ See: `references/35-qdrant-vector-operations/`
→ See: `references/36-multimodal-ranking/`

---

## Blueprint 10: High-Scale Search Platform (100M+ docs)

**Scenario:** Large-scale search service: job board, marketplace, news aggregator, or real estate. Heavy ML, complex ranking, global scale.

**Target Scale:** 100M–1B documents, 50K–500K QPS, <200ms p99, multiple regions, 99.99% uptime.

### Complete Stack

```
┌─────────────────────────────────────────────────────────┐
│ Global Frontend (Edge CDN)                               │
│ Cloudflare Workers + React SPA                           │
│ • Geo-routed to nearest region                           │
│ • Edge caching of popular queries                        │
│ • A/B testing (traffic splitting)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Request Router (Multi-Region)                            │
│ gRPC gateway (async latency-sensitive)                   │
│ • Route to nearest region based on geography             │
│ • Global RPS budgeting + rate limiting                   │
│ • Request deduplication (5-min window)                   │
└─────────────────────────────────────────────────────────┘
                          ↓
    ┌──────────────┬──────────────┬──────────────┐
    ↓              ↓              ↓              ↓
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ US East    │  │ US West    │  │ Europe     │  │ APAC       │
│ Cluster    │  │ Cluster    │  │ Cluster    │  │ Cluster    │
│(50M docs)  │  │(50M docs)  │  │(30M docs)  │  │(20M docs)  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
    ↓              ↓              ↓              ↓
     ┌──────────────┴─────────────────┬──────────┐
     ↓                                ↓          ↓
┌─────────────────┐     ┌─────────────────┐  ┌──────────┐
│ Stage 1: Filter │     │ Stage 2: ML Rank│  │ Stage 3: │
│ (Elasticsearch) │     │ (Feature Store) │  │ LambdaMART│
│ • Full-text     │     │ • User signals  │  │(Top 100) │
│ • Facets/filter │     │ • Item features │  │          │
│ • 100K→10K      │     │ • Context       │  │ Final    │
│                 │     │ • 10K→100       │  │ ranking  │
└─────────────────┘     └─────────────────┘  └──────────┘
     ↓                                ↓          ↓
     └──────────────┬─────────────────┴──────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Feature Store (Real-Time + Batch)                        │
│ Tecton or Feature Store service                          │
│ • User behavior (click, dwell, purchase)                │
│ • Item metadata (age, rating, price trend)              │
│ • Context (time, geo, device, session)                  │
│ • 50ms latency SLA (p99)                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ ML Training Pipeline (Offline)                           │
│ Spark + TensorFlow on Kubernetes                         │
│ • Weekly retraining on interaction data                  │
│ • A/B test new models before deploy                      │
│ • Canary rollout (10% traffic first)                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Data Pipeline (Offline + Real-Time)                      │
│ Kafka + Spark Streaming → Data Warehouse (Snowflake)    │
│ • Event ingestion (100M events/day)                      │
│ • Aggregation jobs (user-item signals)                   │
│ • Backfill for cold-start items                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Monitoring & Experimentation                             │
│ Grafana + Statsig                                        │
│ • Latency SLI < 200ms p99                               │
│ • CTR/conversion metrics (real-time)                     │
│ • Ranking quality (NDCG, MAP)                           │
│ • Online experiments (2K variants concurrent)            │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices & Reasoning

| Component | Choice | Reasoning |
|-----------|--------|-----------|
| **Retrieval** | Elasticsearch (sharded by category/geo) | Proven at scale. Partitioning strategy critical (100M docs need 1000+ shards). Query parallelization. |
| **Ranking** | Two-tower (retrieval) + LambdaMART (final) | Two-tower reduces 100K→1K fast. LambdaMART captures pairwise preferences (CTR, conversion). |
| **Feature Store** | Tecton (managed) | Eliminates feature engineering ops. Real-time + batch pipelines. RBAC for ML teams. |
| **Data Pipeline** | Kafka + Spark Streaming | Decouples event ingestion. Spark for aggregations. Structured for experimentation. |
| **Experiments** | Statsig or Eppo | Statistical rigor (sequential testing). Integration with feature store. Multi-armed bandit support. |

### Cost Estimate (Monthly at 100M docs, 200K QPS, 4 regions)

| Item | Cost |
|------|------|
| Elasticsearch (4 clusters × 30 nodes × 500GB) | $4000 |
| Kafka (distributed, 20 brokers) | $800 |
| Feature Store (Tecton, 1M requests/day) | $1500 |
| Spark for ML training + inference | $2000 |
| Data warehouse (Snowflake ent.) | $3000 |
| Monitoring + experimentation platform | $1000 |
| ML GPU compute (training weekly) | $1000 |
| CDN (global, 500TB/month transfer) | $5000 |
| **Total** | **$18,300** |

### Performance Targets

- **Stage 1 (Filter):** 100K→10K in <30ms (Elasticsearch)
- **Stage 2 (ML Rank):** 10K→100 in <100ms (feature retrieval + scoring)
- **Stage 3 (Final):** 100→10 in <30ms (LambdaMART)
- **End-to-End:** p50=80ms, p99=200ms
- **Throughput:** 200K QPS sustained, 500K burst
- **Ranking Quality:** CTR +25% vs. baseline, conversion +10%

### Scaling Path (10x → 1B docs)

1. **At 200M docs:** Implement cascade ranking (3+ stages). Distributed feature serving (Redis/Memcached layer).
2. **At 500M docs:** DNN-based ranking (learned dense retrieval). Cross-cluster federation for real-time sync. Add approximate KNN at scale.
3. **At 1B docs:** Hierarchical clustering (country → state → city). Cold-start item ranking via content-based or transfer learning. Budget: $50K+/month.

### See Also

→ See: `references/37-elasticsearch-petabyte-scale/`
→ See: `references/38-two-tower-retrieval/`
→ See: `references/39-feature-store-ops/`
→ See: `references/40-ranking-experiments/`

---

## Cross-Blueprint Reference Matrix

| Scenario | Scale | Latency | Cost | Complexity |
|----------|-------|---------|------|-----------|
| 1. SaaS App | 10K–500K | <100ms | $30 | Low |
| 2. RAG KB | 10K–100K | <500ms | $277 | Medium |
| 3. E-Commerce | 50K–5M | <100ms | $540 | Medium-High |
| 4. Enterprise WS | 1M+ | <1s | $2.3K | High |
| 5. Docs Site | 1K–100K | <50ms | $1 | Low |
| 6. Real-Time Logs | 100GB–10TB/day | <5s | $3.35K | High |
| 7. Multi-Language | 100K–1M | <150ms | $750 | Medium-High |
| 8. Medical/Legal | 10K–500K | <500ms | $520 | High |
| 9. Multimodal | 10M–100M | <200ms | $3.55K | Very High |
| 10. High-Scale | 100M–1B | <200ms | $18.3K | Very High |

---

## Quick Decision Tree

**Start here:**
- Need static-site instant search? → **Blueprint 5** (Docs Site)
- Building AI assistant? → **Blueprint 2** (RAG)
- E-commerce product catalog? → **Blueprint 3** (E-Commerce)
- DevOps logs/monitoring? → **Blueprint 6** (Real-Time Logs)
- Enterprise knowledge? → **Blueprint 4** (Workplace Search)
- MVP SaaS search? → **Blueprint 1** (SaaS App)
- Global multi-language? → **Blueprint 7** (Multi-Language)
- Specialized corpus (medical/legal)? → **Blueprint 8** (Domain Search)
- Visual + text search? → **Blueprint 9** (Multimodal)
- Marketplace/job board scale? → **Blueprint 10** (High-Scale)

---

## Final Notes

These blueprints represent real-world production deployments. Each can be adapted:
- Swap Elasticsearch for OpenSearch (open-source alternative)
- Replace cloud vector DBs with self-hosted Milvus or Weaviate
- Use smaller LLMs (Ollama) instead of API-based models for cost
- Implement hybrid search (BM25 + dense) for better recall in RAG

Next: See individual reference guides for deep dives on each component.
