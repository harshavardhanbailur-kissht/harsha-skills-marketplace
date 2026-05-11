---
name: search-mastery-skill
description: >
  Comprehensive search technology knowledge base covering every type of search implementation,
  algorithm, architecture, and optimization strategy. Use this skill whenever the user mentions
  search, find, query, lookup, autocomplete, typeahead, full-text search, semantic search,
  vector search, hybrid search, fuzzy matching, relevance, ranking, indexing, Elasticsearch,
  Meilisearch, Typesense, Algolia, Solr, Fuse.js, MiniSearch, Lunr, pgvector, BM25, TF-IDF,
  embeddings, RAG, retrieval, information retrieval, search UX, faceted search, filtering,
  recommendations engine, e-commerce search, enterprise search, knowledge graph search,
  geospatial search, multilingual search, or any question about how to build, optimize,
  evaluate, or scale a search system. Also trigger when users ask about choosing between
  search libraries, comparing search engines, search architecture decisions, search quality
  metrics (NDCG, MRR, MAP), Learning-to-Rank, query understanding, spell correction,
  autocomplete, or any AI/ML approach to improving search. Also trigger for advanced
  research topics: generative retrieval, differentiable search index (DSI), ColPali,
  visual document retrieval, multi-hop retrieval, compositional search, learned index
  structures, agentic RAG, CRAG, self-reflective retrieval, SPLADE, learned sparse
  retrieval, late interaction models, ColBERT, PLAID, test-time compute for retrieval,
  inference scaling, neural reranking, cross-encoder distillation, or production search
  architectures from companies like Perplexity, Pinterest, Airbnb, Spotify, YouTube.
  This skill covers 49 reference categories (4 action guides + 45 deep references)
  with 94,000+ lines of research — use it liberally for ANY search-related question.
---

# Search Mastery Skill v3

49 references | 94,000+ lines | 15 recipes | 10 blueprints | 10 playbooks | Full benchmarks

## Three-Layer Architecture

This skill uses three layers. Route to the right layer based on what the user needs:

**Layer 1 — ACTION (start here for practical needs):**
- `references/00-search-recipes/` — 15 end-to-end implementation recipes with working code
- `references/00-stack-blueprints/` — 10 complete recommended stacks for common scenarios
- `references/00-migration-playbooks/` — 10 step-by-step upgrade guides
- `references/00-benchmark-matrix/` — Head-to-head data comparison of ALL approaches

**Layer 2 — ROUTING (this file):** Decision framework, tier system, cross-references

**Layer 3 — DEPTH (45 encyclopedic references, `references/01-45/`):**
Deep knowledge on each topic. Only load when Layer 1 doesn't have enough detail.

### Read-Order Rule
For BUILD/IMPLEMENT questions: **Recipe first → Blueprint → Deep reference if needed**
For IMPROVE/FIX questions: **Playbook first → Benchmark data → Deep reference if needed**
For LEARN/COMPARE questions: **Benchmark matrix → Deep reference → Cross-references**

---

## Tier System (2026 Priority)

Always lead with the best modern approach, then offer alternatives:

- **Tier 1 — State-of-the-Art:** Hybrid (BM25 + embeddings + reranker), SPLADE, ColBERT, agentic RAG, Matryoshka embeddings, ColPali. Recommend first.
- **Tier 2 — Production-Proven:** Elasticsearch, Meilisearch, Typesense, Algolia, pgvector, two-tower, standard RAG. Solid defaults.
- **Tier 3 — Legacy/Niche:** Pure BM25 alone, TF-IDF, Fuse.js without semantic, Lunr.js. Flag upgrade path via `00-migration-playbooks/`.

---

## Master Router

### Step 1: Classify intent

| User intent | Start with | Then deepen with |
|---|---|---|
| **BUILD** new search | `00-stack-blueprints/` → pick blueprint | `00-search-recipes/` for implementation code |
| **IMPLEMENT** a specific feature | `00-search-recipes/` → pick recipe | Relevant deep ref (01-45) for customization |
| **IMPROVE** existing search | `00-migration-playbooks/` → pick playbook | `00-benchmark-matrix/` for data-driven decisions |
| **FIX** broken search | Debug tree below → identify failure mode | Relevant deep ref (01-45) for root cause |
| **COMPARE** approaches | `00-benchmark-matrix/` | Deep refs for nuance |
| **LEARN** a concept | Topic lookup table below | Deep ref (01-45) directly |
| **SCALE** search | Deep ref 33 + 07 + 22 | `00-stack-blueprints/` Blueprint #10 |
| **BUILD RAG** pipeline | Recipe #4 (agentic RAG) | Deep refs 12 + 40 + 35 + 45 |

### Step 2: Route by scenario

**BUILD — Quick-start with blueprints:**

| Scenario | Blueprint # | Recipe # | Key Deep Refs |
|---|---|---|---|
| SaaS app search (10K-500K docs) | #1 | #1 (hybrid), #6 (autocomplete) | 04, 05, 06, 21 |
| AI knowledge base / RAG | #2 | #4 (agentic RAG), #2 (reranker) | 12, 40, 35, 45 |
| E-commerce product search | #3 | #5 (e-commerce), #13 (multi-stage) | 24, 28, 45, 06 |
| Enterprise workplace search | #4 | #13 (multi-stage) | 32, 19, 23 |
| Blog/docs site search | #5 | #3 (client-side semantic) | 03, 35 |
| Real-time log/event search | #6 | #15 (real-time CDC) | 13, 04, 26 |
| Multi-language global search | #7 | #7 (multilingual) | 20, 35 |
| Medical/legal domain search | #8 | #12 (SPLADE domain) | 08, 41, 45 |
| Image + text multimodal | #9 | #8 (ColPali) for docs | 17, 37, 35 |
| High-scale platform (100M+) | #10 | #13 (multi-stage), #2 (reranker) | 33, 44, 07, 22 |

**IMPROVE — Quick-wins with playbooks:**

| Problem | Single Best Action | Playbook # | Expected Gain |
|---|---|---|---|
| Results aren't relevant | Add cross-encoder reranker | #2 | +5-10 NDCG points |
| Pure keyword, missing synonyms | Migrate to hybrid search | #1 | +15-30% recall |
| Domain terms not matching | Add SPLADE | #6 | +8-12 NDCG on domain |
| RAG answers are wrong | Upgrade to agentic RAG | #7 | +15-25% accuracy |
| Manual synonyms are a mess | Add query understanding | #8 | Eliminate synonym maintenance |
| No idea if search is good | Add observability | #9 | Baseline + improvement path |
| Outgrowing client-side search | Migrate to server-side | #3 | Handle 100x more data |
| Elasticsearch, no vectors | Add hybrid to ES | #5 | +15-30% relevance |
| Postgres FTS, want AI search | Add pgvector hybrid | #10 | Semantic + keyword in one DB |
| Single-stage, want better ranking | Multi-stage pipeline | #4 | +10-20 NDCG points |

**DEBUG — Diagnose search failures:**
```
Exact terms exist but not found → Tokenization/analyzer ──→ Ref 01, Recipe #1
Synonyms/paraphrases missed → No semantic layer ──→ Playbook #1, Ref 05
Spelling errors kill results → No spell correction ──→ Ref 21, Recipe #6
Non-English queries fail → Missing lang support ──→ Ref 20, Recipe #7
Long queries return garbage → No query understanding ──→ Ref 10, Playbook #8
Good results ranked poorly → No reranker ──→ Playbook #2, Ref 45
Results are slow → Caching/ANN/architecture ──→ Ref 22 + 07, Benchmark matrix
Always measure before/after ──→ Ref 14 + 31, Playbook #9
```

### Step 3: Topic → Deep Reference Lookup

| Topic | Ref # |
|-------|-------|
| BM25, TF-IDF, inverted index, fuzzy matching | 01 |
| Vector search, ANN, HNSW, embeddings | 02 |
| Client-side search (Fuse.js, MiniSearch, Orama, Pagefind) | 03 |
| Server-side engines (ES, Meilisearch, Typesense, Algolia) | 04 |
| Hybrid search, RRF fusion | 05 |
| Search UX, Cmd+K, instant search, facets | 06 |
| Search architecture, sharding, distributed | 07 |
| Code/legal/medical/scientific search | 08 |
| Learning-to-Rank, LambdaMART | 09 |
| Query understanding, intent, NER, expansion | 10 |
| Vector databases (Pinecone, Qdrant, Weaviate, Milvus) | 11 |
| RAG patterns, chunking, retrieval pipelines | 12 |
| Real-time search, streaming, CDC | 13 |
| NDCG, MRR, MAP, evaluation metrics | 14 |
| Which search to choose (decision trees) | 15 |
| Geospatial search, R-tree, H3, PostGIS | 16 |
| Multimodal search, CLIP, image/video/audio | 17 |
| Knowledge graphs, Neo4j, GraphRAG | 18 |
| Federated search across sources | 19 |
| Multilingual search, CJK, mBERT, XLM-R | 20 |
| Autocomplete, typeahead, spell correction | 21 |
| Caching, edge search, Redis, CDN | 22 |
| Privacy-preserving search, SSE, PIR, GDPR | 23 |
| E-commerce search, merchandising | 24 |
| Conversational/generative search, GEO | 25 |
| Search indexing pipelines, ETL, crawlers | 26 |
| Search observability, monitoring | 27 |
| Search personalization, collaborative filtering | 28 |
| NL2SQL, text-to-SQL, semantic parsing | 29 |
| Recommendations vs search convergence | 30 |
| Search testing, A/B tests, golden sets | 31 |
| Enterprise search, Glean, Coveo | 32 |
| Search at scale, billion-doc, DiskANN | 33 |
| 2026 emerging trends, agentic search | 34 |
| Embeddings deep dive, MTEB, Matryoshka | 35 |
| Generative retrieval, DSI, model-as-index | 36 |
| ColPali, visual document retrieval | 37 |
| Multi-hop retrieval, HopRAG, IRCoT | 38 |
| Learned index structures, ALEX, PGM-Index | 39 |
| Agentic RAG, CRAG, Self-RAG | 40 |
| SPLADE, learned sparse retrieval | 41 |
| ColBERT, late interaction, PLAID | 42 |
| Test-time compute for retrieval, MIRAGE | 43 |
| Production architectures (Perplexity, Pinterest, Airbnb) | 44 |
| Neural reranking, cross-encoders, MonoT5, RankGPT | 45 |

---

## Cross-Reference Map

When reading one reference, ALSO check these companions:

| Reading | Also check | Why |
|---|---|---|
| 01 (classical) | 05, 41 | Modern lexical = SPLADE, not raw BM25 alone |
| 02 (AI/ML) | 35, 42 | Embedding choice critical; ColBERT often beats bi-encoders |
| 03 (client-side) | 35 | transformers.js enables client-side semantic |
| 04 (server-side) | 05, 45 | Every engine needs hybrid + reranking |
| 05 (hybrid) | 41, 45 | SPLADE replaces BM25 in hybrid; reranking is final boost |
| 12 (RAG) | 40, 45, 38 | Modern RAG = agentic + reranked + multi-hop |
| 24 (e-commerce) | 28, 45 | Product search needs personalization + reranking |
| 32 (enterprise) | 19, 23 | Enterprise = federated + access-controlled |
| 35 (embeddings) | 42, 41 | Dense vs sparse vs late-interaction are competing paradigms |

---

## Anti-Patterns → Quick Fix

| Anti-Pattern | Fix | Read |
|---|---|---|
| Pure BM25, no semantic | Add hybrid search | Playbook #1, Ref 05 |
| Pure vector, no keyword | Add BM25 to hybrid | Ref 05, Recipe #1 |
| No reranker | Add cross-encoder | Playbook #2, Ref 45 |
| ES for 500 docs | Use MiniSearch/Orama | Ref 03, Blueprint #5 |
| Fuse.js for 10M docs | Migrate to server-side | Playbook #3, Ref 04 |
| One embedding, never tested | Benchmark on MTEB | Ref 35, Benchmark matrix |
| Building without metrics | Add observability first | Playbook #9, Ref 14 |
| OCR pipeline for doc search | Use ColPali instead | Ref 37, Recipe #8 |
| Naive RAG, no self-correction | Upgrade to agentic | Playbook #7, Ref 40 |
| Manual synonym lists | Use SPLADE | Playbook #6, Ref 41 |

---

## Existing Implementation Reference

Production code in `existing-research/`:
- **LAP Intelligence Hub** — Fuse.js v7.1.0, 1,839 Jira tickets, <50ms → `existing-research/LAP-RECOMMENDED_ENGINE.js`
- **BM25F Engine** — Custom BM25F, field boosting → `existing-research/LAP-BM25F_SEARCH_ENGINE.js`
- **Evaluation Report** — BM25F vs Fuse.js vs MiniSearch → `existing-research/LAP-RESEARCH_EVALUATION.md`

---

## Workflow

### Phase 1: Classify & Route
Use the Master Router above. Identify the user's intent → pick the right starting layer.

### Phase 2: Load (Read-Order Matters)
- **BUILD:** Blueprint → Recipe → Deep ref (only if customizing)
- **IMPROVE:** Playbook → Benchmark matrix → Deep ref (for root cause)
- **LEARN:** Deep ref directly → Cross-reference map for companions
- **COMPARE:** Benchmark matrix → then deep refs for nuance

### Phase 3: Recommend (Modern-First)
1. Lead with **Tier 1** approach — explain why it's best for this case
2. Cite **benchmark data** from `00-benchmark-matrix/` to justify the recommendation
3. Offer **Tier 2** alternative if constraints exist (budget, team skill, latency)
4. If user is on **Tier 3**, give the upgrade path from `00-migration-playbooks/`
5. Point to the **specific recipe** from `00-search-recipes/` for implementation
6. Always include: what to use, what NOT to use, trade-offs, how to measure success
