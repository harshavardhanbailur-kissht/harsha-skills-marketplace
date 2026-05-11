# Benchmark Matrix Reference Guide

## What's in This Directory

**`benchmark-matrix.md`** - The comprehensive 1,500+ line reference document consolidating all retrieval approach comparisons into one authoritative source.

## Quick Navigation

### For Specific Questions

| Question | Go to Section |
|----------|---------------|
| "What's the best retrieval approach for my use case?" | Section 1 (Head-to-Head) + Section 9 (Decision Summary) |
| "Which embedding model should I use?" | Section 2 (MTEB Comparison) + Section 9 (Scenario Matrix) |
| "Should I add reranking?" | Section 3 (Reranker Comparison) |
| "What search engine to choose?" | Section 4 (Search Engine Comparison) |
| "Client-side search libraries?" | Section 5 |
| "Visual document retrieval?" | Section 6 (ColPali) |
| "RAG system benchmarks?" | Section 7 (RAG Comparison) + Section 8 (Tradeoff Matrix) |
| "How much will this cost?" | Section 8 (Tier breakdown) + Section 11 (Cost Calculator Examples) |

### By Role

- **Product Managers:** Section 8 + Section 9 (Quick Reference)
- **ML Engineers:** Sections 1-7 (All benchmarks) + Section 10 (Methodology)
- **Infrastructure Teams:** Section 4 + Section 9 (Implementation Checklist)
- **Startups:** Section 9 (MVP scenario)
- **Enterprises:** Section 9 (Enterprise scenario) + Section 10

## Key Metrics at a Glance

### Retrieval Quality Hierarchy
```
BM25:                0.222 MRR@10 (35% NDCG@10) — Baseline
Dense (E5-large):    0.367 MRR@10 (48% NDCG@10)
Hybrid (RRF):        0.390 MRR@10 (53% NDCG@10)
ColBERT v2:          0.397 MRR@10 (54% NDCG@10)
Hybrid + Reranker:   0.450 MRR@10 (57%+ NDCG@10)
RankGPT-4:           0.500 MRR@10 (65%+ NDCG@10)
```

### Cost Tiers (per 1M queries)
```
Tier 1 (Basic):         $0.01-0.05
Tier 2 (Good):          $0.05-0.15
Tier 3 (Excellent):     $0.15-0.40
Tier 4 (SOTA):          $0.30-1.00+
```

### Search Engine Latency (p99)
```
Fastest:     Redis (1-10ms), Typesense (5-30ms), Vespa (10-50ms)
Fast:        Pinecone (30-80ms), Qdrant (20-100ms)
Medium:      Elasticsearch (50-200ms), Weaviate (50-150ms)
```

## Benchmark Data Sources

All numbers backed by:
- **MS MARCO:** Microsoft's official ranking benchmark (archived 2023)
- **BEIR:** Heterogeneous IR benchmark with 15+ datasets (updated Feb 2025)
- **MTEB:** Massive Text Embedding Benchmark (leaderboard updated monthly)
- **ViDoRe v3:** Vision Document Retrieval (26K pages, 3K queries, 6 languages)
- **CRAG:** Comprehensive RAG benchmark (4,409 questions, 5 domains)
- **FRAMES:** End-to-end RAG evaluation framework (2025)

See Section 10 for full methodology and data freshness status.

## How to Use This Document

### Scenario 1: "I need to build a search system in 2 weeks"
1. Read Section 1 (Approaches)
2. Jump to Section 9 (Decision Summary) → Look up "Startup (fast shipping)"
3. Implement that stack

### Scenario 2: "We want to optimize retrieval costs"
1. Check Section 1 head-to-head table
2. Calculate your current quality/cost ratio
3. See Section 8 (Quality-Cost-Latency) for ROI analysis
4. Use Section 11 (Cost Calculator) to model changes

### Scenario 3: "Should we add a reranker?"
1. Read Section 3 (Reranker Comparison)
2. Check your current top-K retrieval quality
3. Use the reranking strategy matrix to estimate ROI
4. Test on 5% of queries first

### Scenario 4: "Choosing between commercial vs open-source models"
1. Section 2 (Embedding Models) has pricing column
2. Section 9 (Decision Summary) compares MTEB scores
3. Consider multilingual requirements (Section 9 language table)
4. Test both on your corpus before committing

## Commonly Ignored Gems in This Document

- **Section 7 Question Type Breakdown:** Shows naive RAG fails on numeric (25%) and boolean (35%) questions — explains why you see bad results on certain question types
- **Section 11 Cost Calculator:** Three realistic examples with actual infrastructure costs
- **Section 13 One-Pagers by Role:** Pinpoints exactly which sections matter to your role
- **Section 9 Implementation Checklist:** Pre-flight checklist before choosing a system

## What This Document Doesn't Cover

- **Code examples:** See references/01-retrieval-approaches/ for implementations
- **Deployment runbooks:** See references/10-production-guide/ for step-by-step setup
- **Real customer case studies:** See references/case-studies/ for industry examples
- **LLM generation optimization:** This matrix focuses on retrieval layer only

## Updates & Maintenance

- **Last verified:** March 1, 2026
- **Update frequency:** Quarterly (or when major benchmark updates happen)
- **MTEB leaderboard:** Updated monthly; check if your favorite model changed
- **Model pricing:** Recheck every 6 months; embeddings market is competitive

## Feedback & Contributions

Found an error? New benchmark data? Outdated pricing?
- Compare against official leaderboards (links in Section 16)
- If discrepancy found, cite source with date
- Submit via reference system

---

**Tip:** Bookmark this file. It's the single place you should go when:
- Comparing retrieval approaches
- Choosing an embedding model
- Estimating RAG system costs
- Justifying reranking to stakeholders
- Auditing search infrastructure decisions
