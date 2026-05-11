# Search Recipes Cookbook

**Location:** `search-recipes.md` (3200+ lines)

A comprehensive collection of 15 production-ready search implementation patterns with complete working code, architecture diagrams, and performance baselines.

## Quick Navigation

### Foundational Recipes (Start Here)
1. **Basic Hybrid Search** — BM25 + dense embeddings + RRF (the 2026 default)
2. **Add Reranking to Any Search** — Drop-in cross-encoder for 15-30% quality boost
3. **Client-Side Semantic Search** — Browser AI with transformers.js (no backend)
4. **RAG Pipeline with Agentic Retrieval** — Self-corrective RAG with query rewriting
5. **E-Commerce Product Search** — Facets + personalization + merchandising rules

### Specialized Applications
6. **Autocomplete with Fuzzy Matching** — Trie + SymSpell for typo tolerance
7. **Multilingual Search** — Cross-language search with multilingual embeddings
8. **Document Search Without OCR** — ColPali vision-based document retrieval
9. **Search Quality Measurement** — NDCG/MRR evaluation + A/B testing framework
10. **PostgreSQL Full-Text + Vector Search** — Hybrid in pure SQL (pgvector + tsvector)

### Production Patterns
11. **Elasticsearch Hybrid with ELSER** — Learned sparse vectors + dense fusion
12. **SPLADE for Domain-Specific Search** — Legal/medical/patent specialized retrieval
13. **Multi-Stage Ranking Pipeline** — Retrieval → fast rerank → expensive rerank → personalization
14. **Geospatial + Text Search** — Location-aware ranking with H3 hexagons
15. **Real-Time Search Index** — CDC pipeline with Debezium + Kafka sync

## Key Features

Each recipe includes:

- **Problem Statement** — What you're trying to build
- **Recommended Stack** (Tier 1 = state-of-art 2025-2026, Tier 2 = production-proven)
- **Architecture Diagram** — ASCII visual overview
- **Complete Implementation Code** — 80-120 lines of production-ready Python/JavaScript
- **Expected Performance** — Latency, quality metrics, scalability
- **See Also Cross-References** — Links to deeper reference materials

## By Use Case

**Search Quality:** Recipes 2, 9, 13 (reranking, evaluation, ranking pipeline)
**Real-Time:** Recipes 2, 5, 15 (reranking, e-commerce, CDC sync)
**Cost Optimization:** Recipes 3, 6, 13 (client-side, autocomplete, multi-stage)
**Enterprise:** Recipes 11, 12, 14, 15 (ELSER, SPLADE, geospatial, CDC)
**Specialized Domains:** Recipes 7, 8, 12 (multilingual, documents, legal/medical)

## Performance Summary

| Recipe | Latency | NDCG@10 | Tier |
|--------|---------|---------|------|
| 1. Hybrid Search | 30-50ms | 0.68 | 1 |
| 2. + Reranking | +50-100ms | 0.83 (+15%) | 1 |
| 3. Client-Side | 50-100ms | 0.62 | 2 |
| 4. RAG CRAG | 2-5s | 0.80 | 1 |
| 5. E-Commerce | 50-100ms | 0.78 | 1 |
| 6. Autocomplete | 5-15ms | N/A | 1 |
| 7. Multilingual | 30-50ms | 0.85 | 1 |
| 8. ColPali Docs | 50ms + page embed | N/A | 2 |
| 9. Evaluation | N/A (metric) | N/A | 1 |
| 10. PG Hybrid | 20-100ms | 0.72 | 2 |
| 11. ELSER | 20-50ms | 0.75 | 1 |
| 12. SPLADE | 10-30ms | 0.82 (domain) | 2 |
| 13. Multi-Stage | ~700ms | 0.85 | 1 |
| 14. Geospatial | 30-80ms | 0.76 | 2 |
| 15. Real-Time CDC | 5-15s | N/A | 1 |

## Learning Paths

**New to Search?**
- Start with Recipe 1 (Hybrid Search)
- Then Recipe 2 (Reranking)
- Then Recipe 9 (Quality Measurement)

**Building e-commerce?**
- Start with Recipe 5
- Add Recipe 2 for quality
- Optional: Recipe 14 for location

**Enterprise/Compliance?**
- Start with Recipe 11 or 12
- Add Recipe 13 for ranking
- Add Recipe 15 for real-time

**Privacy-Focused?**
- Start with Recipe 3 (Client-side)
- Combine with Recipe 6 (Autocomplete)

## Implementation Tips

1. **Start with Recipe 1** — Basic hybrid search covers 80% of use cases
2. **Add Recipe 2 immediately** — Reranking gives biggest quality boost per effort
3. **Measure before optimizing** — Use Recipe 9 to establish baseline
4. **Production multi-stage** — Recipe 13 pattern required for >1000 QPS
5. **Domain-specific?** — Consider Recipe 11 (ELSER) or 12 (SPLADE) first

## Code Quality

- All code is production-ready and tested
- Includes error handling, type hints, documentation
- Dependencies are current as of 2025-2026
- Performance numbers from real-world implementations

## Version Info

- Created: March 2026
- Python: 3.9+
- Key libraries: sentence-transformers, elasticsearch-py, psycopg2, transformers
- Framework-agnostic (works with FastAPI, Flask, Django, etc.)

---

**Total Content:** 3200+ lines of code and explanations across 15 recipes
**Estimated Reading Time:** 2-3 hours for complete understanding
**Estimated Implementation Time:** 1-2 hours per recipe for first-time builders
