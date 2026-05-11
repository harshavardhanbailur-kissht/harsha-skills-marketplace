# Comprehensive Search & Retrieval Benchmark Matrix

**Last Updated:** March 2026
**Benchmark Data Sources:** MS MARCO, BEIR, MTEB, ViDoRe v3, CRAG, FRAMES
**Purpose:** Single authoritative reference for comparing all retrieval approaches with real benchmark numbers.

---

## 1. Retrieval Approaches Head-to-Head

This master comparison table consolidates performance metrics across the most common production retrieval methods.

| Approach | MS MARCO MRR@10 | BEIR NDCG@10 (avg) | Latency (ms/query) | Index Size | Cost/1M Queries | Best For |
|----------|:---------------:|:------------------:|:------------------:|:-----------:|:---------------:|----------|
| **BM25 (Baseline)** | 0.222 | ~35% | 3.2 | 100MB (ref) | $0.001 | Exact keyword matching, cost-critical |
| **Dense (bi-encoder, E5-large-v2)** | 0.367 | ~48% | 5-8 | 64GB | $0.05-0.10 | Semantic search, general purpose |
| **SPLADE v3** | ~0.40 | ~52% | 10.3 | 120GB | $0.03 | Hybrid-like performance, keyword aware |
| **ColBERT v2 / PLAID** | 0.397 | ~54% | 15-35 (vanilla) / 8-10 (PLAID) | 25-35GB | $0.08-0.15 | High accuracy, moderate cost |
| **Hybrid BM25+Dense (RRF)** | ~0.39 | ~53% | 12-15 | 164GB | $0.04-0.06 | Best recall + precision balance |
| **Hybrid BM25+SPLADE** | ~0.42 | ~55% | 18-20 | 220GB | $0.05-0.08 | Maximum lexical coverage |
| **Hybrid + Cross-Encoder Reranker** | ~0.45+ | ~57%+ | 30-50 | 164GB + model | $0.10-0.20 | Maximum accuracy, production RAG |

### Key Insights

- **Accuracy vs Cost Curve:** BM25 → Dense → Hybrid → Hybrid+Reranker shows 2x improvement per level, but cost increases exponentially
- **PLAID Acceleration:** 20.8x speedup over vanilla ColBERT on CPU with zero quality loss (35.2ms → 1.7ms on 100 passages)
- **Hybrid Sweet Spot:** RRF fusion improves recall 15-30% over single methods with minimal added complexity; RRF(k=60) requires no tuning
- **Index Size Trade-off:** Dense embeddings (768-1536D) require 10x more space than sparse vectors but enable faster query-time operations
- **Cross-Encoder Reranker:** Adds 15-30ms per candidate but boosts MRR@10 by 0.05-0.08 points; most effective with top-100 retrieval

### When to Use Each

- **BM25 Only:** <100ms latency budget, highly technical queries, minimal infrastructure
- **Dense Only:** Semantic similarity priority, <500K documents, multilingual queries
- **SPLADE Only:** Cost-sensitive with good accuracy needs, term expansion beneficial
- **ColBERT v2:** <50ms latency, high accuracy priority, willingness to index tokens
- **Hybrid RRF:** Production systems requiring balanced recall/precision, >100K documents
- **Hybrid + Reranker:** Complex queries, RAG applications, maximum accuracy acceptable

---

## 2. Embedding Model Comparison (MTEB 2025-2026)

Current leaderboard shows dramatic improvement across all model classes. This table covers the major contenders for production RAG systems.

| Model | MTEB Score | Dimensions | Speed (tokens/sec) | Size (params) | Multilingual | Cost/1M Tokens | Best For |
|-------|:----------:|:----------:|:------------------:|:----------:|:----------:|:-------:|----------|
| **Cohere embed-v4** | 65.2 | 1536 | ~50K | Proprietary | Yes (100+) | $0.12 | Commercial multimodal (text+image), highest accuracy |
| **OpenAI text-embedding-3-large** | 64.6 | 3072 | ~30K | Proprietary | Yes | $0.13 | Commercial standard, excellent balance |
| **Voyage-Large-2** | 54.8* | 1536 | ~40K | Proprietary | Yes | ~$0.10 | Production RAG systems |
| **Qwen3-Embedding-8B** | 70.58 (multilingual) | 4096 | ~25K | 8B | Yes (100+) | Free (OSS) | Multilingual-first applications, sovereign cloud |
| **BGE-M3** | 63.0 | 4096 | ~20K | 568M | Yes (100+) | Free (OSS) | Hybrid (dense+sparse+multi-vec), multilingual |
| **E5-mistral-7b-instruct** | ~62 | 4096 | ~15K | 7B | Yes | Free (OSS) | English-dominant systems, high quality |
| **GTE-Qwen2-7B-instruct** | ~61 | 4096 | ~12K | 7B | Yes | Free (OSS) | Chinese + English primary use, production |
| **multilingual-e5-large-instruct** | ~58 | 1024 | ~40K | 560M | Yes (100+) | Free (OSS) | Low-resource languages, efficient inference |
| **Nomic Embed Text v2 (MoE)** | ~59 | 768 | ~60K | 1.3B (MoE) | Yes (100+) | Free (OSS) | Cost-critical, ~100 languages with MoE routing |
| **all-MiniLM-L6-v2 (Baseline)** | ~56 | 384 | ~200K | 22M | Limited | Free (OSS) | Baseline comparison, CPU-only systems |

*Note: Voyage-Large-2 appears on BEIR leaderboard; MTEB score estimated from cross-task performance.

### MTEB Leaderboard Trends (2025-2026)

- **Commercial Models Dominate:** Top 3 are all closed-source (Cohere, OpenAI, Voyage)
- **Open-Source Closing Gap:** BGE-M3 (63.0) only 2.2 points behind OpenAI text-3-large (64.6)
- **Multilingual Leaders:** Qwen3-8B (70.58), BGE-M3 (63.0) outperform English-only models
- **Parameter Efficiency:** Nomic Embed v2 achieves 59 MTEB with only 1.3B params via MoE routing
- **Dimension Wars:** 4096D models (Qwen3, BGE-M3, E5-mistral) achieve better accuracy but 4x storage vs 1024D

### Practical Selection Guide

| Use Case | Recommended Model | Rationale |
|----------|-------------------|-----------|
| **Budget-Zero, High Accuracy** | Qwen3-8B | Best MTEB (70.58), free, supports 100+ languages |
| **Production SaaS** | OpenAI text-3-large | Reliable API, excellent balance, no infrastructure |
| **Multilingual at Scale** | BGE-M3 | Hybrid (dense+sparse), true 100+ language support |
| **Cost-Critical (OSS)** | multilingual-e5-large-instruct | 560M params, 40K tok/sec, 100+ languages |
| **English-Only Speed** | all-MiniLM-L6-v2 | 22M params, 200K tok/sec, runs on edge devices |
| **Sovereign Cloud (no US)** | Qwen3-8B or BGE-M3 | Both open-source, no external API calls |

---

## 3. Reranker Comparison

Reranking is the highest-ROI optimization for RAG systems. Costs grow with top-K size, not query count.

| Reranker | MS MARCO MRR@10 | BEIR NDCG@10 | Latency (ms/doc) | Cost/1M Reranks | Speed Tier | Best For |
|----------|:---------------:|:------------:|:----------------:|:---------------:|:----------:|----------|
| **No Reranker (Baseline)** | ~0.35 | ~48% | 0 | $0 | — | Cost baseline |
| **bge-reranker-v2 (OSS)** | ~0.40 | ~54% | 2-4 | Free | Fast (GPU) | Open-source RAG, on-prem |
| **cross-encoder/ms-marco-MiniLM** | ~0.39 | ~53% | 3-5 | Free | Fast (CPU/GPU) | Lightweight reranker, baseline |
| **Jina Reranker v2** | ~0.42 | ~57.06 | 3-6 | ~$0.50/1M | Medium | Multilingual, solid balance |
| **Jina Reranker v3** | ~0.44 | 61.94 | 2-4 | ~$0.50/1M | Fast | State-of-art, 0.6B params |
| **Cohere Rerank v3** | ~0.43 | ~59% | 5-8 | ~$1.00/1M | Slower | Commercial, requires API |
| **Cohere Rerank 3.5** | ~0.45 | ~60% | 595-603 (avg) | ~$1.00/1M | Slowest | Latest commercial offering |
| **RankGPT-4 (GPT-4)** | ~0.50+ | ~65%+ | 100-200 | ~$5-10/1M | Very Slow | Maximum accuracy, cost prohibitive |

### Reranking Strategy Matrix

| Top-K Retrieved | Recommended Reranker | Typical Latency Added | Quality Gain |
|:---------------:|:--------------------:|:---------------------:|:------------:|
| 10 | None | 0ms | — |
| 50 | bge-reranker-v2 | 100-200ms | MRR+0.03 |
| 100 | Jina v3 or BGE v2 | 200-400ms | MRR+0.05 |
| 1000 | Jina v3 (batch mode) | 2-4s | MRR+0.08 |
| 10000+ | RankGPT-4 (if budget) | 30-60s | MRR+0.10+ |

### Cost-Quality Tradeoff Examples

- **Naive RAG:** Dense retrieval (top 10) → No reranking = $0.05/query, MRR ~0.36
- **Standard RAG:** Hybrid (top 50) → BGE-reranker = $0.06/query, MRR ~0.40
- **Advanced RAG:** Hybrid (top 100) → Jina-v3 = $0.08/query, MRR ~0.43
- **Maximum Accuracy:** Hybrid (top 100) → RankGPT-4 = $1.20/query, MRR ~0.50

---

## 4. Search Engine Comparison

Infrastructure choice affects cost, latency, and feature availability. This table covers production-ready options.

| Engine | Throughput (QPS) | p99 Latency (ms) | Hybrid Support | Vector Support | Managed Option | Price Tier | Best For |
|--------|:----------------:|:----------------:|:--------------:|:--------------:|:--------------:|:----------:|----------|
| **Elasticsearch** | 1K-10K | 50-200 | Yes (native) | Yes (plugins) | Cloud ($100+/mo) | **High** | Enterprise search, logs, analytics |
| **Meilisearch** | 5K-50K | 10-50 | Limited | Limited | SaaS ($25+/mo) | **Low** | Fast typo-tolerant search, mobile |
| **Typesense** | 10K-100K | 5-30 | Limited | Yes (native) | Cloud ($99+/mo) | **Low** | Typo tolerance, typo-tolerant UX |
| **Qdrant** | 5K-50K | 20-100 | Limited | Yes (native) | Cloud ($25+/mo) | **Medium** | Vector-first, hybrid add-ons |
| **Weaviate** | 1K-10K | 50-150 | Yes (native) | Yes (native) | Cloud ($100+/mo) | **Medium-High** | Rich schema, GraphQL, multimedia |
| **Pinecone** | 10K-100K | 30-80 | Limited | Yes (native) | Serverless ($8.25/1M reads) | **Medium** | Zero-ops vector DB, autoscaling |
| **pgvector (PostgreSQL)** | 1K-5K | 50-200 | Yes (native) | Yes (extension) | Self-hosted (free) | **Low** | Integrated DB, compliance-focused |
| **Vespa** | 10K-100K | 10-50 | Yes (native) | Yes (native) | Self-hosted (free) | **Low** | Large-scale, feature-rich |
| **Redis** | 10K-100K | 1-10 | Limited | Yes (native) | Cloud ($20+/mo) | **Low-Medium** | In-memory speed, caching layer |
| **MongoDB Atlas Vector Search** | 5K-50K | 20-100 | Limited | Yes (native) | Cloud ($57+/mo) | **Medium** | Document store + vectors |

### Throughput & Latency Benchmarks (2025 Real-World)

- **Highest Latency:** Elasticsearch (50-200ms), Weaviate (50-150ms) due to complex scoring
- **Lowest Latency:** Redis (1-10ms), Typesense (5-30ms), Vespa (10-50ms)
- **Highest Throughput:** Pinecone, Vespa, Typesense (10K-100K QPS) at serverless scale
- **Lowest Throughput:** Elasticsearch, pgvector, Weaviate (1K-10K QPS) on single nodes

### Feature Parity Matrix

| Feature | Elasticsearch | Qdrant | Weaviate | Pinecone | Vespa | Meilisearch |
|---------|:-----:|:-------:|:----------:|:--------:|:-----:|:----------:|
| BM25 + Dense Hybrid | ✓ | Partial | ✓ | ✗ | ✓ | ✗ |
| Sparse Vector Support | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| Cross-Encoder Reranking | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| Graph/Relations | ✗ | Partial | ✓ | ✗ | ✓ | ✗ |
| Full-Text Typo Tolerance | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Metadata Filtering | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ACID Transactions | Partial | Partial | ✗ | ✗ | ✓ | ✗ |
| Managed Service | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |

### Pricing Reality Check (1M Documents, 1K QPS Average)

| Engine | Setup Cost | Monthly Cost | Annual Cost |
|--------|:----------:|:----------:|:----------:|
| **Pinecone** | $0 | $300-800 | $3.6K-9.6K |
| **Meilisearch Cloud** | $0 | $25-300 | $300-3.6K |
| **Elasticsearch Cloud** | $0 | $500-2K | $6K-24K |
| **Weaviate Cloud** | $0 | $200-1K | $2.4K-12K |
| **PostgreSQL + pgvector** | $100 | $0-500 | $100-6K |
| **Self-hosted Qdrant** | $1K (setup) | $200-800 | $2.4K-11.6K |

→ See: references/04-search-engines/

---

## 5. Client-Side Library Comparison

For browser-based search, these libraries provide instant, offline-first retrieval.

| Library | Index Speed | Search Speed | Memory (10K docs) | Fuzzy Support | Prefix Search | Best For |
|---------|:----------:|:----------:|:---------------:|:----------:|:----------:|----------|
| **Fuse.js** | 500ms | 20-100ms | 8-15MB | ✓ (configurable) | ✓ | Balanced, fuzzy-first |
| **MiniSearch** | 200ms | 10-30ms | 5-10MB | ✓ (phonetic) | ✓ | Small-medium datasets |
| **FlexSearch** | 100ms | 1-5ms | 3-8MB | ✓ | ✓ | Speed-critical, large datasets |
| **Orama** | 300ms | 15-50ms | 6-12MB | ✓ | ✓ | Modern, well-maintained |
| **Pagefind** | 800ms | 5-20ms | 10-20MB | ✗ | ✓ | Static site search, low mem |
| **Lunr.js** | 400ms | 30-80ms | 7-12MB | ✓ | ✓ | Legacy, battle-tested |

### Performance Claims vs Reality

- **FlexSearch claims 1,000,000x faster** — true for specific microbenchmarks, marginal in real apps
- **Fuse.js slowness:** Real only on >100K documents or very high fuzzy threshold; acceptable for <10K
- **MiniSearch efficiency:** Excellent for document count < 50K; degrades past that
- **Library choice rarely dominates:** Network latency (JSON load) >> search algorithm latency

### Recommendation Engine

| Use Case | Recommended | Rationale |
|----------|-------------|-----------|
| **<1K docs, low spec phones** | FlexSearch | Minimal memory, 1-5ms search |
| **1K-10K docs, balanced UX** | Fuse.js | Best fuzzy, good speed, maintained |
| **10K+ docs, no fuzzy needed** | FlexSearch | Linear scaling, <50ms at 100K docs |
| **Static site (11ty, Hugo)** | Pagefind | Purpose-built, low overhead |
| **Learning / legacy codebase** | Lunr.js | Most documentation, stable API |

---

## 6. Visual Document Retrieval (ColPali Family)

Newest frontier: retrieve from scanned documents, PDFs, and images without OCR.

| Model | ViDoRe v3 NDCG@5 | Latency (ms/doc) | GPU Required | Index Size (10K pages) | Languages | Best For |
|-------|:---------------:|:----------------:|:----------:|:-----:|:-------:|----------|
| **ColPali-3.5B** | ~0.68 | 50-100 | Optional (CPU slow) | 180GB | English, French | Document image search, fast |
| **ColPali+ (Improved)** | ~0.72 | 40-80 | Optional | 200GB | English, French, Spanish, German | Multilingual documents |
| **ViDoRe v3 Ensemble** | ~0.78 | 150-250 | Required | 500GB | 6 languages | Enterprise document retrieval |

### ViDoRe v3 Benchmark Details

**Composition:** 10 datasets, 26,000+ pages, 3,000+ queries in 6 languages (English, French, Spanish, German, Chinese, Japanese)
**Domains:** Medical, Business, Scientific, Administrative documents
**Uniqueness:** Human-created & human-verified annotations (not synthetic)

### When Visual Document Retrieval Wins

- **Scanned documents** without OCR: 100% accuracy improvement
- **Complex layouts** (infographics, tables, mixed text/images): 30-50% improvement over text-only
- **Low-quality scans:** Handles noise better than OCR-first approaches
- **Cost:** ~$0.10-0.20/document (one-time indexing) vs. OCR+embedding+storage

### Limitation & Workaround

- **Latency:** ColPali indexes image embeddings (1000+ vectors/page); latency scales with page count
- **Solution:** Chunk documents into sections, use hierarchy for large documents

→ See: references/06-visual-retrieval/ColPali-family/

---

## 7. RAG Retrieval Comparison

End-to-end performance on realistic question-answering tasks with the CRAG benchmark (4,409 questions, 5 domains, 8 categories).

| Approach | CRAG Accuracy (%) | Latency (sec) | Cost/query | Complexity | Hallucination Rate |
|----------|:----------------:|:----------:|:--------:|:----------:|:-----:|
| **Naive RAG (Dense only)** | 44% | 0.5-1.0 | $0.05 | Low | 15-20% |
| **Advanced RAG (Hybrid+Rerank)** | 52% | 2-3 | $0.15 | Medium | 10-12% |
| **Self-RAG (Critique+Iterate)** | 58% | 3-5 | $0.25 | High | 6-8% |
| **CRAG Framework (Web+KG)** | 63% | 4-6 | $0.40 | High | 3-5% |
| **Agentic RAG (Multi-hop)** | 68% | 5-10 | $0.80 | Very High | 2-3% |
| **Industrial SOTA (44 API calls avg)** | 63% | 10-15 | $2.00+ | Extreme | 2-4% |

### Key Findings from CRAG Benchmark

- **LLM-Only Baseline (No RAG):** ≤34% accuracy
- **Simple RAG Boost:** +10 points (44%), minimal complexity
- **Reranking Boost:** +8 points (52%), moderate cost
- **Web Search Integration:** +11 points (63%), enables temporal/entity answers
- **Agentic Loop:** +5-10 points (68%), exponential cost

### Accuracy Breakdown by Question Type (CRAG)

| Question Category | Naive RAG | Advanced RAG | Self-RAG | CRAG |
|------------------|:--------:|:----------:|:------:|:-----:|
| Factoid (single entity) | 65% | 75% | 82% | 88% |
| Boolean (yes/no) | 35% | 50% | 60% | 70% |
| Comparison | 40% | 48% | 56% | 62% |
| Numeric (calculations) | 25% | 35% | 45% | 55% |
| Complex (multi-step) | 15% | 28% | 42% | 58% |

### When to Use Each Tier

| Business Scenario | Recommended | Rationale |
|------------------|-------------|-----------|
| **Customer Support FAQ** | Naive RAG | High recall ok, 44% accuracy sufficient |
| **Legal Document Q&A** | Advanced RAG | 52% accuracy + hybrid recall critical |
| **Financial Analysis** | Self-RAG | Critique + fact-checking reduces liability risk |
| **News Summarization** | CRAG (Web) | Temporal answers, breaking news |
| **Research Synthesis** | Agentic RAG | Complex reasoning, multi-document aggregation |

→ See: references/07-rag-approaches/

---

## 8. Quality-Cost-Latency Tradeoff Matrix

Decision framework: map your SLA to retrieval architecture.

### Tier 1: Basic Search (Q<100K queries/month)

| Metric | Target | Example Stack |
|--------|:------:|:------:|
| **Quality (NDCG@10)** | 48-50% | BM25 only, or Dense (E5-large) |
| **Latency (p99)** | <200ms | Elasticsearch self-hosted |
| **Cost/1M queries** | $0.01-0.05 | BM25 + MiniSearch |
| **Typical Architecture** | Single vector DB or open-source | pgvector + BM25 |
| **Inference Cost** | Free (OSS) or minimal | Offline embeddings |

### Tier 2: Good Search (100K-10M queries/month)

| Metric | Target | Example Stack |
|--------|:------:|:------:|
| **Quality (NDCG@10)** | 52-54% | Hybrid (BM25+Dense) + light reranking |
| **Latency (p99)** | <100ms | Qdrant or Meilisearch managed |
| **Cost/1M queries** | $0.05-0.15 | Pinecone serverless + Jina-v2 |
| **Typical Architecture** | Managed vector DB + semantic layer | Pinecone + bge-reranker-v2 |
| **Inference Cost** | $10-50/month | Commercial embeddings |

### Tier 3: Excellent Search (10M-100M queries/month)

| Metric | Target | Example Stack |
|--------|:------:|:------:|
| **Quality (NDCG@10)** | 54-57% | Hybrid + ColBERT or advanced reranker |
| **Latency (p99)** | <80ms | Vespa or self-hosted Elasticsearch + GPU |
| **Cost/1M queries** | $0.15-0.40 | Elasticsearch + Jina-v3 |
| **Typical Architecture** | Multi-tier: BM25 + dense + GPU reranking | E.g.: Elasticsearch + PLAID |
| **Inference Cost** | $100-500/month | Multiple model serving |

### Tier 4: State-of-the-Art (100M+ queries/month, <50ms latency)

| Metric | Target | Example Stack |
|--------|:------:|:------:|
| **Quality (NDCG@10)** | 57%+ | Hybrid + cross-encoder + multi-stage |
| **Latency (p99)** | <50ms | Vespa with GPU reranking or in-house system |
| **Cost/1M queries** | $0.30-1.00 | Custom infrastructure + RankGPT optional |
| **Typical Architecture** | Tiered: BM25 (candidate) → Dense (ranking) → Reranker → Multi-step | Custom like Airbnb, Doordash |
| **Inference Cost** | $500-5K+/month | Multiple GPUs, custom models |

### Cost vs Quality Curve (Simplified)

```
Quality
  |     SOTA (57%+)  ╱─ Tier 4
  |  Excellent (54%) ╱─ Tier 3
  | Good (52%) ╱─ Tier 2
  | Basic (50%) ╱─ Tier 1
  |________╱_________ Cost
```

Each tier requires 2-5x cost increase to achieve 1-2% quality gain.

---

## 9. When to Use What (Decision Summary)

Fast-reference guide for choosing architectures by scenario.

### Decision Tree

```
Do you have < 100K documents?
  → YES: Use Fuse.js (client-side) or MiniSearch
  → NO: Continue

Do you need hybrid (lexical + semantic)?
  → NO: Dense only (E5-large or BGE-M3) → Meilisearch or MiniSearch
  → YES: Continue

Do you need extreme latency (<50ms)?
  → YES: ColBERT + PLAID (if accuracy matters) or BM25 only
  → NO: Continue

Do you have budget for managed services?
  → YES: Pinecone + Jina-v3 reranker
  → NO: Self-hosted Elasticsearch + bge-reranker

Do you need accuracy >55%?
  → YES: Add cross-encoder reranking (e.g., RankGPT or Jina-v3)
  → NO: Hybrid RRF is sufficient

Do you have multilingual/non-English data?
  → YES: BGE-M3 or Qwen3-8B for embeddings
  → NO: Any top embedding model works
```

### Scenario Matrix

| Scenario | Embedding | Retrieval | Reranker | Est. Quality | Est. Cost/1M |
|----------|-----------|-----------|----------|:----------:|:----------:|
| **MVP (low budget)** | all-MiniLM | Fuse.js + BM25 | None | 48% | $0.01 |
| **Startup (fast shipping)** | OpenAI text-3 | Meilisearch | None | 52% | $0.08 |
| **Growth (RAG product)** | BGE-M3 | Qdrant | bge-reranker | 54% | $0.12 |
| **Scale (high accuracy)** | Cohere-v4 | Elasticsearch | Jina-v3 | 56% | $0.35 |
| **Enterprise (maximum accuracy)** | Cohere-v4 | Vespa | RankGPT-4 | 59%+ | $2.00+ |

### Language-Specific Recommendations

| Language | Embedding Model | Notes |
|----------|-----------------|-------|
| **English Only** | OpenAI text-3-large or e5-mistral | Any model works equally well |
| **English + 1-2 others** | BGE-M3 | Supports 100+ languages uniformly |
| **Chinese-Heavy** | GTE-Qwen2 or Qwen3-8B | Native support, higher accuracy |
| **Multilingual (10+ languages)** | Qwen3-8B or multilingual-e5-large | True multilingual training |
| **Low-Resource Languages** | multilingual-e5-large-instruct | Designed for underrepresented languages |

### Document Type Recommendations

| Document Type | Best Approach | Why |
|---------------|---------------|-----|
| **Search Results / Web** | Hybrid (BM25+Dense) | Title + snippet matching critical |
| **PDFs / Long Form** | Dense + ColBERT | Paragraph-level semantics important |
| **Scanned Documents** | ColPali (visual) | Layout and images carry meaning |
| **Structured (JSON/CSV)** | BM25 + SQL filters | Exact match + metadata critical |
| **Multi-modal (text+image)** | Cohere embed-v4 | Native image support |
| **Code / Technical** | Dense with code-tuned model | Syntax structure matters |

---

## 10. Benchmark Sources & Methodology

### Datasets Used

1. **MS MARCO Passage Ranking (Microsoft):** 8.8M passages, 367K queries, 6.3M train triples. Standard for ranking evaluation.
   - Metric: MRR@10, NDCG@10, MAP@10
   - Link: https://microsoft.github.io/msmarco/

2. **BEIR (Heterogeneous IR, 2021):** 15+ datasets, zero-shot evaluation framework. Realistic retrieval scenarios.
   - Metric: NDCG@10, nDCG@100, MRR@10
   - Link: https://github.com/beir-cellar/beir

3. **MTEB (Massive Text Embedding Benchmark, 2022+):** 56+ text embedding tasks. Leaderboard updated monthly.
   - Metric: Overall MTEB score (average across retrieval, STS, clustering, reranking tasks)
   - Link: https://huggingface.co/spaces/mteb/leaderboard

4. **ViDoRe v3 (Vision Document Retrieval, 2025):** 10 datasets, 26K pages, 3K queries. Enterprise document focus.
   - Metric: NDCG@5, Recall@10
   - Link: https://github.com/illuin-tech/vidore-benchmark

5. **CRAG (Comprehensive RAG, 2024):** 4,409 questions, 5 domains, web + KG search integration.
   - Metric: Exact match accuracy, F1 score, hallucination rate
   - Link: https://github.com/facebookresearch/CRAG

6. **FRAMES (2025):** Evaluates RAG across Factuality, Retrieval, Reasoning dimensions.
   - Metrics: Precision@k, recall@k, MRR, nDCG, faithfulness, citation coverage
   - Covers latency and cost alongside accuracy

### How to Interpret Tables

- **Averages:** Most tables show averages; individual datasets may vary by 5-10 points
- **Confidence:** Green highlight = well-validated; Yellow = limited data points; Red = extrapolated
- **Latency:** Measured on standard hardware (RTX 4090 for GPU, single-threaded CPU); varies 2x with different setups
- **Cost:** Based on provider pricing as of March 2026; subject to change
- **Quality Metrics:** Normalized to 0-1.0 scale where applicable

### Data Freshness

| Benchmark | Last Verified | Update Frequency |
|-----------|:----------:|:------:|
| MS MARCO | Feb 2024 | Stable (archived in 2023) |
| BEIR | Feb 2025 | Quarterly |
| MTEB | Feb 2026 | Monthly (leaderboard) |
| ViDoRe v3 | Jan 2026 | Semi-annual |
| CRAG | Jul 2024 | Annual |
| FRAMES | Dec 2025 | Semi-annual |

---

## 11. Cost Calculator Examples

### Example 1: Customer Support Chatbot (10K queries/day)

**Requirements:** Good accuracy (52%), <5 sec latency, $500/month budget

**Option A: Pinecone Serverless + BGE-M3**
- Embedding: 3.6M tokens/month @ free (OSS) = $0
- Retrieval: 300K queries/month × $8.25/1M = $2.47
- Reranking: 50K (top-10 only) × $0.50/1M = $0.03
- **Total: ~$5/month** ✓ Well within budget

**Quality Trade-off:** 54% NDCG@10, 0.5s latency
→ See: references/09-rag-cost-calculator/

### Example 2: Enterprise Legal Search (1M queries/month)

**Requirements:** Excellent accuracy (56%+), <100ms latency, $5K/month budget

**Option A: Elasticsearch + Jina-v3 Reranker**
- Indexing: 500K documents × E5-mistral = $2/month (batch)
- Cloud infrastructure: Elasticsearch cluster = $1,500/month
- Reranking: 1M × 100 docs × $0.50/1M reranks = $50/month
- **Total: ~$1,550/month** ✓ Under budget

**Option B: Self-hosted Vespa + BGE-reranker**
- Initial hardware: $10K (3x servers)
- Monthly operations: $800
- **Total: $800/month ongoing** ✓ Best long-term ROI

→ See: references/09-rag-cost-calculator/

### Example 3: Consumer Mobile App (100M queries/month)

**Requirements:** Instant search (<50ms), high accuracy (55%+), $50K/month budget

**Option: Multi-tier (Vespa + GPU Reranking)**
- Infrastructure: $30K/month (Vespa cluster + GPU rerankers)
- Embeddings: $5K/month (batch)
- Reranking: $10K/month (5% of queries get full RankGPT)
- **Total: ~$45K/month** ✓ Within budget

**Quality:** 56-58% NDCG@10, p99 latency <50ms

---

## 12. Implementation Checklist

Before choosing a retrieval approach, validate these prerequisites:

### Pre-Implementation

- [ ] **Benchmark your baseline:** Run BM25 on your corpus; it's your cost/quality reference
- [ ] **Measure query volume:** Peak QPS and monthly volume determine infrastructure tier
- [ ] **Identify your latency budget:** User-facing? <100ms. Batch processing? <1s per query
- [ ] **Quantify accuracy needs:** Medical/legal? Need >55%. General search? 50%+ ok
- [ ] **Check multilingual requirement:** If yes, immediately exclude monolingual-only models

### Benchmarking Your Data

1. **Index with BM25:** Baseline, typically 0.22 MRR@10
2. **Add dense (E5-large):** Expect 0.36-0.38 MRR@10 improvement
3. **Try hybrid RRF:** +0.02-0.05 points at 2x indexing cost
4. **Test reranker on top-100:** +0.05-0.08 points, 30-50ms latency added

### Go-Live Readiness

- [ ] **Cache embedding model outputs:** Avoid re-embedding identical queries
- [ ] **Monitor quality metrics:** Track MRR@10, NDCG@10, hallucination rate monthly
- [ ] **Set cost alerts:** 20% monthly variance indicates optimization opportunity
- [ ] **A/B test approach changes:** Never roll out new retrieval without shadow testing
- [ ] **Document query performance:** Slow queries (>200ms) often indicate suboptimal top-K size

---

## 13. Cross-References to Detailed Guides

Each section links to deeper reference materials for implementation-level details.

| Topic | Depth | Location |
|-------|:-----:|----------|
| **Retrieval Approaches** | Implementation | → See: references/01-retrieval-approaches/ |
| **Dense Embeddings** | Benchmarks + Tuning | → See: references/02-embeddings/dense-models/ |
| **Reranking Patterns** | How-To + Examples | → See: references/03-reranking/architecture-patterns/ |
| **Search Engines** | Setup + Deployment | → See: references/04-search-engines/ |
| **Client-Side Search** | React + Vue examples | → See: references/05-client-side-libraries/ |
| **Visual Retrieval** | ColPali tutorials | → See: references/06-visual-retrieval/ColPali-family/ |
| **RAG Frameworks** | LangChain + LlamaIndex | → See: references/07-rag-approaches/ |
| **Multi-Modal Embeddings** | Image + Text retrieval | → See: references/08-multimodal/ |
| **Cost Calculator** | Spreadsheet tool | → See: references/09-rag-cost-calculator/ |
| **Production Checklist** | Deployment runbook | → See: references/10-production-guide/ |

---

## 14. Quick Reference: One-Pagers by Role

### For Product Managers
- Want: Quality vs Cost trade-off
- See: Section 8 (Quality-Cost-Latency Matrix)
- Key question: "What accuracy level justifies the cost increase?"

### For ML Engineers
- Want: Benchmarks and ablation studies
- See: Sections 1-7 (all benchmark tables)
- Key question: "Which approach maximizes F1 score per dollar spent?"

### For Infrastructure Teams
- Want: Operational complexity and scaling
- See: Section 4 (Search Engine Comparison) + Section 9 (Decision Summary)
- Key question: "What is our p99 latency SLA and can this infrastructure meet it?"

### For Startups (Tight Budget)
- Want: Minimum viable approach
- See: Section 9, Scenario Matrix "MVP (low budget)"
- Key question: "Can we launch with <$100/month infrastructure cost?"

### For Enterprises (Compliance-Critical)
- Want: Explainability and reproducibility
- See: Section 9, Scenario Matrix "Enterprise" + Section 10 (Methodology)
- Key question: "Can we trace which documents contributed to each answer?"

---

## 15. Frequently Asked Questions

### Q: Should I wait for newer models or deploy now?
**A:** Model improvements follow a diminishing curve. Going from BM25 (0.22) → Dense (0.36) is 64% improvement. Dense → Hybrid (0.40) is 11% improvement. By the time a new model releases, you should already have ROI from current deployment. Deploy now, measure, optimize.

### Q: Is Cohere embed-v4 worth 5x the cost of BGE-M3?
**A:** Only if your domain heavily values multimodal (text+images). For text-only, BGE-M3 (63.0 MTEB) vs Cohere-v4 (65.2 MTEB) is <2 points — often within measurement error on real data. Test on your corpus; most find them equivalent for ranking tasks.

### Q: What's the latency breakdown: retrieval vs reranking vs generation?
**A:** Typical RAG query (top-100 reranking):
- Dense retrieval (top-100): 20-50ms
- Reranking (100 docs): 200-400ms
- LLM generation (1K tokens): 1-3 seconds
- **Total: 1.2-3.5 seconds** (LLM dominates)

Optimizing retrieval from 30ms → 10ms saves only 20ms (1.7%). Optimize LLM latency first.

### Q: Self-hosted or managed?
**A:**
- **Managed wins if:** <1K QPS, want zero ops, or unpredictable load spikes
- **Self-hosted wins if:** >10K QPS, stable traffic, or compliance requires on-prem
- **Breakeven:** ~5K QPS; above that, self-hosted ROI typically positive in 6-12 months

### Q: How much does query rewriting / classification help?
**A:** Query rewriting (expanding "photosynthesis" → "photosynthesis chlorophyll light energy") helps:
- Simple, short queries: +1-2% accuracy
- Complex, long queries: +3-5% accuracy
- Cost: 1-2x inference compared to direct retrieval

Recommendation: Add only if your baseline accuracy is >50%; otherwise optimize retrieval first.

### Q: Do I really need a cross-encoder reranker?
**A:**
- **YES if:** Accuracy critical (legal, medical), or your dense model shows >20% precision loss (many false positives)
- **NO if:** Speed critical (<100ms budget) or dense model already scores top-5 well

Rule of thumb: If your dense top-5 has >70% precision, reranking adds <2% improvement; not worth 30ms latency.

---

## 16. Recommended Reading (2025-2026)

### Seminal Papers
- ColBERT v2 (2021): [arxiv.org/abs/2004.12832](https://arxiv.org/abs/2004.12832)
- SPLADE v3 (2024): Available on Semantic Scholar
- CRAG Benchmark (2024): [arxiv.org/abs/2406.04744](https://arxiv.org/abs/2406.04744)
- ViDoRe v2 (2025): [arxiv.org/abs/2505.17166](https://arxiv.org/abs/2505.17166)

### Benchmark Leaderboards (Live)
- MTEB Leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- MS MARCO: https://microsoft.github.io/msmarco/
- BEIR: https://github.com/beir-cellar/beir
- ViDoRe: https://github.com/illuin-tech/vidore-benchmark

### Industry Articles (2025-2026)
- "Hybrid Search Explained" (Weaviate): https://weaviate.io/blog/hybrid-search-explained
- "Advanced RAG: From Naive Retrieval to Hybrid Search" (Dev.to)
- "Best Embedding Models 2025" (Ailog RAG): https://app.ailog.fr/en/blog/guides/choosing-embedding-models

---

## 17. Contributing & Updates

This matrix is living documentation. To report:

- **Inaccurate benchmarks:** Compare against official leaderboards; cite sources
- **Missing models:** Submit with MTEB/BEIR scores + pricing
- **New architectures:** Describe with end-to-end CRAG or FRAMES results

Last comprehensive update: March 2026
Next planned update: June 2026 (MTEB Q2 refresh)

---

**Document Version:** 1.2.0
**Compiled by:** Search Mastery Reference System
**License:** CC BY-SA 4.0 (Share with attribution, derivatives allowed)
