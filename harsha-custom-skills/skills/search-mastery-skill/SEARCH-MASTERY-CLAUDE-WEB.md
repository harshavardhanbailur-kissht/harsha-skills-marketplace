# Search Mastery — Complete Knowledge Base for Claude

**Use this as Project Knowledge in Claude.ai Projects.**
49 references | 94,000+ lines condensed | 15 recipes | 10 blueprints | 10 playbooks | Full benchmarks

---

## INSTRUCTIONS FOR CLAUDE

You are a search technology expert. When the user asks ANY question about search, retrieval, indexing, ranking, RAG, embeddings, or related topics, use this knowledge base to provide precise, modern-first recommendations.

### Tier System (2026 Priority)

Always lead with the best modern approach, then offer alternatives:

- **Tier 1 — State-of-the-Art:** Hybrid (BM25 + embeddings + reranker), SPLADE, ColBERT, agentic RAG, Matryoshka embeddings, ColPali. Recommend first.
- **Tier 2 — Production-Proven:** Elasticsearch, Meilisearch, Typesense, Algolia, pgvector, two-tower, standard RAG. Solid defaults.
- **Tier 3 — Legacy/Niche:** Pure BM25 alone, TF-IDF, Fuse.js without semantic, Lunr.js. Always flag upgrade path.

### Master Router

**Step 1: Classify intent**

| User intent | Start with | Then deepen with |
|---|---|---|
| **BUILD** new search | Stack Blueprints → pick blueprint | Recipes for implementation code |
| **IMPLEMENT** a specific feature | Recipes → pick recipe | Deep Reference for customization |
| **IMPROVE** existing search | Migration Playbooks → pick playbook | Benchmark Matrix for data-driven decisions |
| **FIX** broken search | Debug tree below → identify failure mode | Deep Reference for root cause |
| **COMPARE** approaches | Benchmark Matrix | Deep References for nuance |
| **LEARN** a concept | Topic lookup table below | Cross-references for companions |
| **SCALE** search | Deep Refs: Search at Scale + Architecture + Caching | Blueprint #10 |
| **BUILD RAG** pipeline | Recipe #4 (agentic RAG) | Deep Refs: RAG + Agentic RAG + Embeddings + Reranking |

**Step 2: Route by scenario**

BUILD scenarios:

| Scenario | Blueprint # | Recipe # | Key Topics |
|---|---|---|---|
| SaaS app search (10K-500K docs) | #1 | #1 (hybrid), #6 (autocomplete) | Server engines, Hybrid, Search UX, Autocomplete |
| AI knowledge base / RAG | #2 | #4 (agentic RAG), #2 (reranker) | RAG, Agentic RAG, Embeddings, Reranking |
| E-commerce product search | #3 | #5 (e-commerce), #13 (multi-stage) | E-commerce, Personalization, Reranking, UX |
| Enterprise workplace search | #4 | #13 (multi-stage) | Enterprise, Federated, Privacy |
| Blog/docs site search | #5 | #3 (client-side semantic) | Client-side libraries, Embeddings |
| Real-time log/event search | #6 | #15 (real-time CDC) | Real-time, Server engines, Indexing |
| Multi-language global search | #7 | #7 (multilingual) | Multilingual, Embeddings |
| Medical/legal domain search | #8 | #12 (SPLADE domain) | Domain-specific, SPLADE, Reranking |
| Image + text multimodal | #9 | #8 (ColPali) for docs | Multimodal, ColPali, Embeddings |
| High-scale platform (100M+) | #10 | #13 (multi-stage), #2 (reranker) | Scale, Production architectures, Architecture, Caching |

IMPROVE quick-wins:

| Problem | Single Best Action | Expected Gain |
|---|---|---|
| Results aren't relevant | Add cross-encoder reranker | +5-10 NDCG points |
| Pure keyword, missing synonyms | Migrate to hybrid search | +15-30% recall |
| Domain terms not matching | Add SPLADE | +8-12 NDCG on domain |
| RAG answers are wrong | Upgrade to agentic RAG | +15-25% accuracy |
| Manual synonyms are a mess | Add query understanding | Eliminate synonym maintenance |
| No idea if search is good | Add observability | Baseline + improvement path |
| Outgrowing client-side search | Migrate to server-side | Handle 100x more data |
| Elasticsearch, no vectors | Add hybrid to ES | +15-30% relevance |
| Postgres FTS, want AI search | Add pgvector hybrid | Semantic + keyword in one DB |
| Single-stage, want better ranking | Multi-stage pipeline | +10-20 NDCG points |

DEBUG — Diagnose search failures:
```
Exact terms exist but not found → Tokenization/analyzer issue
Synonyms/paraphrases missed → No semantic layer → Add hybrid search
Spelling errors kill results → No spell correction → Add autocomplete/fuzzy
Non-English queries fail → Missing lang support → Add multilingual embeddings
Long queries return garbage → No query understanding → Add query rewriting
Good results ranked poorly → No reranker → Add cross-encoder
Results are slow → Caching/ANN/architecture issue
Always measure before/after with NDCG, MRR metrics
```

### Cross-Reference Map

| Reading about | Also check | Why |
|---|---|---|
| Classical algorithms (BM25) | Hybrid, SPLADE | Modern lexical = SPLADE, not raw BM25 alone |
| AI/ML search | Embeddings, ColBERT | Embedding choice critical; ColBERT often beats bi-encoders |
| Client-side search | Embeddings | transformers.js enables client-side semantic |
| Server-side engines | Hybrid, Reranking | Every engine needs hybrid + reranking |
| Hybrid search | SPLADE, Reranking | SPLADE replaces BM25 in hybrid; reranking is final boost |
| RAG patterns | Agentic RAG, Reranking, Multi-hop | Modern RAG = agentic + reranked + multi-hop |
| E-commerce search | Personalization, Reranking | Product search needs personalization + reranking |
| Enterprise search | Federated, Privacy | Enterprise = federated + access-controlled |
| Embeddings | ColBERT, SPLADE | Dense vs sparse vs late-interaction are competing paradigms |

### Anti-Patterns → Quick Fix

| Anti-Pattern | Fix |
|---|---|
| Pure BM25, no semantic | Add hybrid search |
| Pure vector, no keyword | Add BM25 to hybrid |
| No reranker | Add cross-encoder |
| ES for 500 docs | Use MiniSearch/Orama |
| Fuse.js for 10M docs | Migrate to server-side |
| One embedding, never tested | Benchmark on MTEB |
| Building without metrics | Add observability first |
| OCR pipeline for doc search | Use ColPali instead |
| Naive RAG, no self-correction | Upgrade to agentic |
| Manual synonym lists | Use SPLADE |

---

## STACK BLUEPRINTS (Condensed)

### Blueprint 1: SaaS App Search (10K–500K docs)
**Stack:** Typesense + React InstantSearch + CSV/API ingestion
**Cost:** ~$30/month | **Latency:** p50=10ms, p99=50ms | **Scale to:** 5M docs via ES migration

### Blueprint 2: AI Knowledge Base / RAG
**Stack:** Qdrant + LangChain + Cohere Rerank v3 + OpenAI/Claude LLM + BGE-M3 embeddings
**Cost:** ~$277/month | **Latency:** <500ms retrieval+LLM | **Scale to:** 1M docs

### Blueprint 3: E-Commerce Product Search
**Stack:** Elasticsearch + ML reranking + OpenAI embeddings + React InstantSearch + Kafka CDC
**Cost:** ~$540/month | **Latency:** p50=30ms, p99=100ms | **Scale to:** 50M products

### Blueprint 4: Enterprise Workplace Search
**Stack:** Elasticsearch + custom connectors (Slack, GDocs, Jira) + RBAC + LangChain RAG
**Cost:** ~$2,310/month | **Latency:** <1s | **Scale to:** 10M+ docs

### Blueprint 5: Blog/Documentation Site Search
**Stack:** Pagefind (static) or Orama (dynamic) — entirely client-side, zero backend
**Cost:** ~$1/month (CDN only) | **Latency:** 0ms (client-side) | **Scale to:** 1M pages via server migration

### Blueprint 6: Real-Time Event/Log Search
**Stack:** Elasticsearch/OpenSearch + Kafka + Debezium CDC + Grafana dashboards
**Cost:** ~$3,350/month | **Latency:** <5s search, <10s ingest | **Scale to:** 100TB/day

### Blueprint 7: Multi-Language Global Search
**Stack:** Elasticsearch + BGE-M3 embeddings + language detection + per-language analyzers
**Cost:** ~$750/month | **Latency:** <150ms p99 | **Scale to:** 2M docs, 40 languages

### Blueprint 8: Medical/Legal Domain Search
**Stack:** Elasticsearch + SPLADE (domain-tuned) + bge-reranker + domain ontology
**Cost:** ~$520/month | **Latency:** <500ms | **Scale to:** 500K docs

### Blueprint 9: Image + Text Multimodal Search
**Stack:** Vespa + CLIP/SigLIP embeddings + ColPali for docs + GPU reranking
**Cost:** ~$3,550/month | **Latency:** <200ms | **Scale to:** 500M images

### Blueprint 10: High-Scale Platform (100M+ docs)
**Stack:** Vespa/custom + multi-stage pipeline + GPU reranking + multi-region + L2R
**Cost:** ~$18,300/month | **Latency:** <200ms p99 | **Scale to:** 1B docs

---

## RECIPES (Condensed)

### Recipe 1: Basic Hybrid Search (BM25 + Dense + RRF)
**When:** Starting any new search system. Universal default.
**Pattern:** BM25 retrieval (top-100) + Dense retrieval (top-100) → RRF fusion (k=60) → Return top-10
**Stack:** Any search engine + any embedding model + RRF merge
**Gain:** +15-30% recall over single method

### Recipe 2: Add Reranking to Any Search
**When:** Have search results but relevance is mediocre.
**Pattern:** Existing retrieval (top-100) → Cross-encoder reranker → Return top-10
**Best rerankers:** Jina Reranker v3 ($0.50/1M), bge-reranker-v2 (free), Cohere Rerank 3.5 ($1/1M)
**Gain:** +5-10 NDCG points, MRR +0.05-0.08

### Recipe 3: Client-Side Semantic Search (Browser AI)
**When:** Static site, want semantic search with zero server costs.
**Pattern:** transformers.js in browser + Orama/MiniSearch for indexing + pre-computed embeddings
**Gain:** Semantic matching on client-side, zero backend costs

### Recipe 4: RAG Pipeline with Agentic Retrieval (CRAG)
**When:** Building AI chatbot/assistant with document Q&A.
**Pattern:** Query → Retrieve (hybrid) → Evaluate relevance → If low: rewrite query + web search → Rerank → Generate answer with citations
**Gain:** 44% → 68% accuracy (Naive RAG → Agentic RAG)

### Recipe 5: E-Commerce Product Search
**When:** Product catalog with filtering, faceting, merchandising.
**Pattern:** Query understanding → Hybrid retrieval → Category-aware ranking → Personalization layer → Business rules (promoted products, inventory)
**Key features:** Facets, price filters, color/size, "did you mean", autocomplete

### Recipe 6: Autocomplete with Fuzzy Matching
**When:** Search-as-you-type, typeahead suggestions.
**Pattern:** Prefix trie + edge n-grams + fuzzy matching (Levenshtein ≤2) + popularity scoring
**Latency target:** <50ms for real-time feel

### Recipe 7: Multilingual Search
**When:** Users search in multiple languages.
**Pattern:** Language detection → Per-language analyzer + multilingual embeddings (BGE-M3 or Qwen3-8B) → Language-aware ranking
**Key:** Use multilingual embedding model, NOT separate indexes per language

### Recipe 8: Document Search Without OCR (ColPali Vision)
**When:** Searching scanned PDFs, images, documents with complex layouts.
**Pattern:** ColPali model encodes document pages as images → Late interaction matching → No OCR needed
**Gain:** 100% improvement over OCR-first on scanned docs, handles tables/charts/infographics

### Recipe 9: Search Quality Measurement (NDCG/MRR Pipeline)
**When:** Need to measure and track search quality over time.
**Pattern:** Golden test set (100+ queries with human-judged relevance) → Automated NDCG@10, MRR@10, MAP calculation → Dashboard → A/B test new changes
**Key metrics:** NDCG@10 (ranking quality), MRR@10 (first relevant result), Recall@100 (coverage)

### Recipe 10: PostgreSQL Full-Text + Vector Search
**When:** Already using PostgreSQL, want search without adding new infrastructure.
**Pattern:** pg_tsvector (BM25-like) + pgvector (dense embeddings) → RRF fusion in SQL
**Gain:** Hybrid search in a single database, zero new infra

### Recipe 11: Elasticsearch Hybrid with ELSER
**When:** Already on Elasticsearch, want to add semantic search.
**Pattern:** ES BM25 + ELSER (Elastic's sparse model) or dense_vector kNN → RRF in ES query DSL
**Gain:** +15-30% relevance without leaving ES ecosystem

### Recipe 12: SPLADE for Domain-Specific Search (Legal/Medical)
**When:** Domain with specialized vocabulary where general embeddings fail.
**Pattern:** Fine-tune SPLADE on domain corpus → Learned sparse vectors capture domain-specific term expansion → Hybrid with BM25
**Gain:** +8-12 NDCG points on domain queries vs general embeddings

### Recipe 13: Multi-Stage Ranking Pipeline
**When:** Need maximum accuracy for complex queries.
**Pattern:** Stage 1: BM25 (top-1000, <10ms) → Stage 2: Dense bi-encoder (top-100, <50ms) → Stage 3: Cross-encoder (top-10, <200ms)
**Gain:** +10-20 NDCG over single-stage, production pattern used by Google/Bing/Amazon

### Recipe 14: Geospatial + Text Search
**When:** Location-aware search (restaurants, real estate, services).
**Pattern:** PostGIS/H3 spatial index + text search → Distance-weighted scoring + text relevance → Geo-fenced results
**Key:** Combine spatial proximity with text relevance, not just filter

### Recipe 15: Real-Time Search Index (CDC + Debezium)
**When:** Database changes must appear in search within seconds.
**Pattern:** PostgreSQL/MySQL → Debezium CDC → Kafka → Search index (ES/Typesense)
**Gain:** Sub-second index freshness, no batch lag

---

## MIGRATION PLAYBOOKS (Condensed)

| # | From → To | When to Migrate | Expected Gain | Risk Level |
|---|-----------|-----------------|---------------|------------|
| 1 | BM25-Only → Hybrid | Missing synonyms, semantic gaps | +15-30% recall | Low |
| 2 | No Reranker → Cross-Encoder | Good recall, poor precision/ranking | +5-10 NDCG | Low |
| 3 | Fuse.js → Server-Side | >50K docs, slow client-side | Handle 100x data | Medium |
| 4 | Single-Stage → Multi-Stage | Need better ranking accuracy | +10-20 NDCG | Medium |
| 5 | Elasticsearch → Hybrid ES | ES keyword-only, want semantic | +15-30% relevance | Low |
| 6 | Pure Keyword → SPLADE | Domain vocabulary mismatch | +8-12 NDCG on domain | Medium |
| 7 | Naive RAG → Agentic RAG | 40%+ wrong RAG answers | +15-25% accuracy | High |
| 8 | Manual Synonyms → Query Understanding | Synonym list maintenance burden | Eliminate maintenance | Medium |
| 9 | No Metrics → Full Observability | No idea if search is good | Baseline + improvement path | Low |
| 10 | PostgreSQL FTS → pgvector Hybrid | Want AI search in existing Postgres | Semantic + keyword in one DB | Low |

---

## BENCHMARK MATRIX

### Retrieval Approaches Head-to-Head

| Approach | MS MARCO MRR@10 | BEIR NDCG@10 | Latency (ms) | Cost/1M Queries | Best For |
|----------|:---:|:---:|:---:|:---:|----------|
| BM25 (Baseline) | 0.222 | ~35% | 3.2 | $0.001 | Exact keyword, cost-critical |
| Dense (bi-encoder, E5-large) | 0.367 | ~48% | 5-8 | $0.05-0.10 | Semantic, general purpose |
| SPLADE v3 | ~0.40 | ~52% | 10.3 | $0.03 | Hybrid-like, keyword aware |
| ColBERT v2 / PLAID | 0.397 | ~54% | 8-10 (PLAID) | $0.08-0.15 | High accuracy, moderate cost |
| Hybrid BM25+Dense (RRF) | ~0.39 | ~53% | 12-15 | $0.04-0.06 | Best recall+precision balance |
| Hybrid + Cross-Encoder Reranker | ~0.45+ | ~57%+ | 30-50 | $0.10-0.20 | Maximum accuracy, production RAG |

**Key insight:** Each tier gives ~2x improvement but costs grow exponentially. Hybrid+Reranker is the sweet spot for most production systems.

### Embedding Models (MTEB 2025-2026)

| Model | MTEB Score | Dimensions | Multilingual | Cost | Best For |
|-------|:---:|:---:|:---:|:---:|----------|
| Cohere embed-v4 | 65.2 | 1536 | Yes (100+) | $0.12/1M tok | Commercial multimodal |
| OpenAI text-3-large | 64.6 | 3072 | Yes | $0.13/1M tok | Commercial standard |
| Qwen3-Embedding-8B | 70.58 | 4096 | Yes (100+) | Free (OSS) | Best multilingual, sovereign |
| BGE-M3 | 63.0 | 4096 | Yes (100+) | Free (OSS) | Hybrid (dense+sparse), multilingual |
| E5-mistral-7b | ~62 | 4096 | Yes | Free (OSS) | English-dominant |
| all-MiniLM-L6-v2 | ~56 | 384 | Limited | Free (OSS) | Baseline, CPU-only, edge |

**Practical selection:** Budget-zero → Qwen3-8B. Production SaaS → OpenAI text-3-large. Multilingual at scale → BGE-M3. English speed → all-MiniLM.

### Reranker Comparison

| Reranker | MRR@10 | BEIR NDCG | Latency/doc | Cost/1M | Best For |
|----------|:---:|:---:|:---:|:---:|----------|
| None (baseline) | ~0.35 | ~48% | 0 | $0 | Cost baseline |
| bge-reranker-v2 | ~0.40 | ~54% | 2-4ms | Free | OSS RAG, on-prem |
| Jina Reranker v3 | ~0.44 | 61.94 | 2-4ms | ~$0.50/1M | State-of-art, 0.6B params |
| Cohere Rerank 3.5 | ~0.45 | ~60% | 595ms | ~$1.00/1M | Latest commercial |
| RankGPT-4 | ~0.50+ | ~65%+ | 100-200ms | ~$5-10/1M | Maximum accuracy |

**Rule of thumb:** If top-5 precision >70%, reranking adds <2% — not worth it. Otherwise, add Jina v3 or bge-reranker for biggest bang/buck.

### Search Engine Comparison

| Engine | QPS | p99 Latency | Hybrid | Vector | Monthly Cost (1M docs) |
|--------|:---:|:---:|:---:|:---:|:---:|
| Elasticsearch | 1K-10K | 50-200ms | Yes | Yes | $500-2K |
| Meilisearch | 5K-50K | 10-50ms | Limited | Limited | $25-300 |
| Typesense | 10K-100K | 5-30ms | Limited | Yes | $99+ |
| Qdrant | 5K-50K | 20-100ms | Limited | Yes | $25+ |
| Weaviate | 1K-10K | 50-150ms | Yes | Yes | $200-1K |
| Pinecone | 10K-100K | 30-80ms | Limited | Yes | $300-800 |
| pgvector | 1K-5K | 50-200ms | Yes | Yes | $0-500 |
| Vespa | 10K-100K | 10-50ms | Yes | Yes | Self-hosted |

### RAG Accuracy Comparison (CRAG Benchmark)

| Approach | Accuracy | Latency | Cost/query | Hallucination |
|----------|:---:|:---:|:---:|:---:|
| Naive RAG (Dense only) | 44% | 0.5-1s | $0.05 | 15-20% |
| Advanced RAG (Hybrid+Rerank) | 52% | 2-3s | $0.15 | 10-12% |
| Self-RAG (Critique+Iterate) | 58% | 3-5s | $0.25 | 6-8% |
| CRAG Framework (Web+KG) | 63% | 4-6s | $0.40 | 3-5% |
| Agentic RAG (Multi-hop) | 68% | 5-10s | $0.80 | 2-3% |

### Client-Side Library Comparison

| Library | Search Speed | Memory (10K) | Fuzzy | Best For |
|---------|:---:|:---:|:---:|----------|
| Fuse.js | 20-100ms | 8-15MB | Yes | Balanced fuzzy-first |
| MiniSearch | 10-30ms | 5-10MB | Yes | Small-medium datasets |
| FlexSearch | 1-5ms | 3-8MB | Yes | Speed-critical |
| Orama | 15-50ms | 6-12MB | Yes | Modern, well-maintained |
| Pagefind | 5-20ms | 10-20MB | No | Static sites |

### Quality-Cost-Latency Tiers

| Tier | Quality (NDCG@10) | Latency | Cost/1M queries | Example Stack |
|------|:---:|:---:|:---:|----------|
| Basic (<100K q/mo) | 48-50% | <200ms | $0.01-0.05 | BM25 + MiniSearch |
| Good (100K-10M) | 52-54% | <100ms | $0.05-0.15 | Hybrid + bge-reranker |
| Excellent (10M-100M) | 54-57% | <80ms | $0.15-0.40 | Hybrid + ColBERT/Jina v3 |
| State-of-Art (100M+) | 57%+ | <50ms | $0.30-1.00 | Multi-stage + GPU reranking |

---

## DEEP REFERENCE ENCYCLOPEDIA (45 Topics)

### Classical & Foundational (01-03)

**01 — Classical Algorithms:** BM25 (k1=1.2, b=0.75), BM25F (field-weighted), TF-IDF, inverted indexes, fuzzy matching (Levenshtein, Damerau-Levenshtein), n-grams, stemming/lemmatization. BM25 remains the baseline to beat — 0.222 MRR@10 on MS MARCO. Modern upgrade: replace with SPLADE for automatic term expansion.

**02 — AI/ML Search:** Vector search fundamentals: HNSW (hierarchical navigable small world), IVF (inverted file index), ScaNN (Google), PQ (product quantization). Bi-encoder architecture: query → embedding, doc → embedding, cosine similarity. Key insight: bi-encoders are fast but lose fine-grained interaction — use cross-encoders or ColBERT for reranking.

**03 — Client-Side Libraries:** Fuse.js (most popular, fuzzy-first), MiniSearch (balanced), FlexSearch (fastest), Orama (modern successor), Pagefind (static sites), Lunr.js (legacy). New frontier: transformers.js enables in-browser semantic search with ONNX models. Best practice: use for <100K docs; migrate to server-side beyond that.

### Engines & Infrastructure (04-07)

**04 — Server-Side Engines:** Elasticsearch (enterprise standard, complex), Meilisearch (developer-friendly, fast), Typesense (typo-tolerant, simple), Algolia (managed, expensive), Solr (legacy). Key: all now support vector search. Modern recommendation: Typesense for startups, Elasticsearch for enterprise, Vespa for scale.

**05 — Hybrid Search:** RRF (Reciprocal Rank Fusion, k=60) is the universal fusion method. Combine BM25 + dense embeddings. No tuning needed for RRF. Alternative: linear interpolation (requires weight tuning). SPLADE can replace BM25 in hybrid for +2-5 NDCG. Always add hybrid — never ship pure keyword or pure vector alone.

**06 — Search UX & Psychology:** Cmd+K pattern, instant search (<100ms perceived), faceted navigation, zero-results handling, search suggestions, result highlighting. Key research: Nielsen Norman Group shows 50% of users use search as primary navigation. Mobile: voice search growing 20% YoY.

**07 — Search Architecture:** Sharding strategies (hash, range, time-based), replication, distributed search (scatter-gather), index design, schema optimization. Multi-tier: L1 cache (Redis) → L2 search engine → L3 deep retrieval. Production pattern: separate indexing and query paths.

### Specialized Domains (08-11)

**08 — Domain-Specific Search:** Code search (AST parsing, TreeSitter), legal (citation graphs, statute linking), medical (UMLS, MeSH ontology), scientific (citation-aware ranking). Key: domain search needs domain-specific tokenization, ontologies, and fine-tuned models — general embeddings underperform by 10-20%.

**09 — Learning-to-Rank:** LambdaMART (gradient boosted trees), RankNet, ListNet. Features: BM25 score, click-through rate, freshness, popularity. Modern alternative: neural L2R with cross-encoders. LambdaMART still wins in feature-rich environments (e-commerce). Cross-encoders win in text-only scenarios.

**10 — Query Understanding:** Intent classification, NER (named entity recognition), query expansion, spell correction, query rewriting with LLMs. Modern: use LLM to rewrite queries before retrieval (+3-5% accuracy on complex queries). Key: query understanding is most impactful when queries are short (<3 words).

**11 — Vector Databases:** Pinecone (serverless, zero-ops), Qdrant (OSS, flexible), Weaviate (GraphQL, schema-rich), Milvus (distributed, FAISS-based), Chroma (lightweight, dev-friendly). Selection: Pinecone for zero-ops, Qdrant for control, pgvector if already on PostgreSQL.

### RAG & Retrieval Patterns (12-15)

**12 — RAG Patterns:** Chunking strategies (fixed-size, semantic, recursive), context window management, citation generation, hallucination mitigation. Key: chunk size 256-512 tokens optimal for most use cases. Always overlap chunks by 10-20%. Parent-child chunking: retrieve child, return parent for context.

**13 — Real-Time Search:** Streaming indexing, CDC (Change Data Capture), Debezium, near-real-time vs batch. WebSocket-based live search. Key: Debezium + Kafka is the production standard for <5s index freshness. Alternative: database triggers for simpler setups.

**14 — Evaluation Metrics:** NDCG@10 (main ranking metric), MRR@10 (first relevant result), MAP (mean average precision), Recall@K (coverage), Precision@K (accuracy). Also: click-through rate, zero-result rate, time-to-first-click. Always create golden test sets (100+ queries with human judgments).

**15 — Implementation Decision Trees:** Document count, query volume, latency budget, team size, budget → recommended stack. Key decision points: <100K docs → client-side; <1M → managed service; <100M → self-hosted; >100M → custom infrastructure.

### Specialized Search Types (16-23)

**16 — Geospatial Search:** R-tree, H3 (Uber's hexagonal grid), PostGIS, geohash. Combine spatial proximity with text relevance. Production pattern: pre-filter by geo-fence, then rank by text relevance within bounds.

**17 — Multimodal Search:** CLIP (OpenAI), SigLIP (Google), image-to-text and text-to-image retrieval. Cohere embed-v4 supports native text+image. Key: shared embedding space maps images and text to same vector space for cross-modal search.

**18 — Knowledge Graph Search:** Neo4j, GraphRAG (Microsoft), knowledge graph enhanced retrieval. Combine structured graph traversal with unstructured text search. Key use case: multi-hop questions ("Who directed the movie starring the actor who won the 2023 Oscar?").

**19 — Federated Search:** Search across multiple sources (Slack, Google Docs, Jira, Email) with unified ranking. Challenges: different schemas, access control, latency normalization. Solutions: Glean, Coveo, or custom with per-source adapters + unified reranking.

**20 — Multilingual Search:** mBERT, XLM-R, BGE-M3, Qwen3-8B for multilingual embeddings. CJK tokenization (Chinese-Japanese-Korean needs special handling). Key: use single multilingual model (BGE-M3) instead of per-language models. Cross-lingual retrieval (search in English, find Chinese docs) works with multilingual embeddings.

**21 — Autocomplete & Spelling:** Prefix tries, edge n-grams, Levenshtein automata, phonetic matching (Soundex, Metaphone). Completion-as-you-type: return results in <50ms. Spelling correction: Symmetric Delete algorithm (SymSpell) for <1ms corrections.

**22 — Caching & Edge Search:** Redis for query cache, CDN-based search (Cloudflare Workers + KV), precomputed popular queries. Cache hit rates: 30-50% for popular queries. Edge search: sub-10ms globally via CDN.

**23 — Privacy-Preserving Search:** Searchable Symmetric Encryption (SSE), Private Information Retrieval (PIR), GDPR right-to-be-forgotten in search indexes. Differential privacy for search analytics. Key challenge: encrypted search is 10-100x slower than plaintext.

### Advanced Applications (24-35)

**24 — E-Commerce Search:** Merchandising rules, inventory-aware ranking, price/category facets, visual search, personalized ranking. Key: e-commerce search = retrieval + business rules + personalization. A 1% improvement in search relevance = 1-2% revenue increase.

**25 — Conversational/Generative Search:** Generative Engine Optimization (GEO), search as conversation, search-augmented generation. Key trend: search results are increasingly consumed by LLMs, not humans. Optimize for LLM consumption: structured data, clear citations.

**26 — Search Indexing Pipelines:** ETL for search, document processing, crawlers (Scrapy, Apache Nutch), incremental updates. Key: batch vs streaming indexing. CDC (Change Data Capture) is the modern standard for real-time.

**27 — Search Observability:** Monitoring search quality in production: zero-result rate, click-through rate, query latency distributions, abandoned searches. Tools: custom dashboards with Grafana, ELK stack for search logs. Key metric to alert on: zero-result rate spike.

**28 — Search Personalization:** Collaborative filtering, user embeddings, session-based personalization, A/B testing personalized vs generic results. Key: personalization helps most for ambiguous queries. Two-tower model (user tower + item tower) is the production standard.

**29 — NL2SQL / Text-to-SQL:** Convert natural language to SQL for structured data search. Models: GPT-4, specialized models (DIN-SQL, C3SQL). Key: combine NL2SQL for structured data with vector search for unstructured. Accuracy: 70-85% on standard benchmarks (Spider, Bird).

**30 — Recommendations vs Search:** Convergence of search and recommendations. Search = explicit intent, recommendations = implicit intent. Modern systems merge both via unified embedding space. Two-tower models serve both use cases.

**31 — Search Testing & QA:** Golden test sets, offline evaluation, online A/B testing, interleaving experiments. Key: always maintain 100+ query golden set with human relevance judgments. Run before every deployment. Automated regression detection.

**32 — Enterprise Search:** Unified search across silos, RBAC (role-based access control), document security trimming. Solutions: Glean, Coveo, custom. Key challenge: access control at query time — never expose documents user shouldn't see.

**33 — Search at Scale:** Billion-document search: DiskANN (Microsoft), sharding strategies, approximate nearest neighbors at scale. Key: at >100M docs, approximate methods (HNSW, IVF-PQ) are mandatory. DiskANN enables billion-scale on SSDs.

**34 — 2026 Emerging Trends:** Agentic search (LLMs as search orchestrators), multimodal-first search, search-augmented reasoning, test-time compute for retrieval. Key prediction: by 2027, most search queries will be answered by AI agents, not blue links.

**35 — Embeddings Deep Dive:** MTEB benchmark, Matryoshka embeddings (variable dimensions), embedding fine-tuning (Sentence Transformers), embedding compression (binary quantization). Key: Matryoshka allows 8x storage reduction with <2% quality loss. Always benchmark on YOUR data, not just MTEB.

### Cutting-Edge Research (36-45)

**36 — Generative Retrieval / DSI:** Differentiable Search Index — model IS the index. Encodes document IDs directly in neural network weights. Research frontier (Google DSI, GENRE). Not production-ready for large corpora but promising for specialized domains <1M docs.

**37 — Visual Document Retrieval / ColPali:** ColPali encodes document pages as images, enabling search without OCR. Late interaction matching. ViDoRe benchmark: NDCG@5 ~0.68-0.78. Key win: scanned documents, complex layouts (tables, charts, infographics) where OCR fails.

**38 — Multi-Hop Compositional Retrieval:** Answering complex questions requiring information from multiple documents. HopRAG, IRCoT (Interleaving Retrieval with Chain-of-Thought). Key: decompose complex query into sub-queries, retrieve for each, synthesize. Critical for research/analysis tasks.

**39 — Learned Index Structures:** ALEX, PGM-Index, Recursive Model Index. Replace B-trees with neural models that learn data distribution. 2-10x faster lookups on sorted data. Research frontier — not yet replacing B-trees in production databases.

**40 — Agentic RAG / Self-RAG / CRAG:** LLM agents that decide when and how to retrieve. Self-RAG: critique own retrieval, re-retrieve if poor. CRAG: combine web search + knowledge graphs when local retrieval fails. Key: 44% → 68% accuracy improvement over naive RAG. The future of RAG is agentic.

**41 — Learned Sparse Retrieval / SPLADE:** SPLADE learns which terms to expand queries with, replacing manual synonym lists. Sparse vectors (same format as BM25) but learned. SPLADE v3: 0.40 MRR@10 on MS MARCO — matches hybrid search quality with single model. Best for: domain-specific where BM25 vocabularies fail.

**42 — Late Interaction / ColBERT Evolution:** ColBERT: encode query and document tokens separately, match via MaxSim. PLAID: 20.8x speedup over vanilla ColBERT. ColBERT v2: 0.397 MRR@10. Key advantage: better than bi-encoders at fine-grained matching, faster than cross-encoders at inference.

**43 — Test-Time Compute for Retrieval / MIRAGE:** Scale inference compute to improve retrieval (like how chain-of-thought helps reasoning). MIRAGE: multiple retrieval attempts with self-verification. Key insight: spending 2-5x more compute at query time can improve accuracy by 5-10 points.

**44 — Production Search Architectures:** Real-world systems: Perplexity (Vespa + multi-model), Pinterest (SearchSage two-tower), Airbnb (multi-stage + personalization), Spotify (two-tower + contextual), YouTube (two-tower + engagement prediction). Key pattern: ALL use multi-stage pipelines with 3+ ranking stages.

**45 — Neural Reranking / Distillation:** Cross-encoders (slow but accurate), distilled models (MonoT5, TinyBERT rerankers), RankGPT (LLM-based). Knowledge distillation: train small fast model to mimic large accurate model. Production pattern: distill RankGPT into small cross-encoder for 10x speedup with 90% quality retention.

---

## DECISION QUICK-REFERENCE

### "What search should I use?" Decision Tree

```
< 100K documents?
  → YES: Client-side (Orama, MiniSearch, Fuse.js)
  → NO: Continue

Need hybrid (lexical + semantic)?
  → NO: Dense only → Meilisearch or Typesense
  → YES: Continue

Need extreme latency (<50ms)?
  → YES: ColBERT+PLAID or BM25 only
  → NO: Continue

Budget for managed services?
  → YES: Pinecone + Jina v3 reranker
  → NO: Self-hosted ES + bge-reranker

Need accuracy >55%?
  → YES: Add cross-encoder reranking
  → NO: Hybrid RRF is sufficient

Multilingual data?
  → YES: BGE-M3 or Qwen3-8B for embeddings
  → NO: Any top embedding model
```

### 2026 Recommended Default Stack

For most new projects in 2026, start with:
1. **Embedding:** OpenAI text-3-large (commercial) or BGE-M3 (OSS)
2. **Retrieval:** Hybrid BM25 + Dense with RRF fusion
3. **Reranking:** Jina Reranker v3 (best quality/cost)
4. **Engine:** Typesense (simple) or Elasticsearch (enterprise)
5. **Monitoring:** Track NDCG@10 + zero-result rate from day 1

---

*Condensed from 94,000+ lines of research across 49 reference categories. For implementation code, see the full search-mastery-skill reference files.*
