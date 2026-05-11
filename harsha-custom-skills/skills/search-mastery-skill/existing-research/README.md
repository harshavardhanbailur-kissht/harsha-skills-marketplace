# Search Deep Research — All Web Research on Search Engines & Advanced Search

All deep web research conducted across multiple chat windows on search engines, search features, advanced search algorithms, and search architecture. Strictly copy-pasted from original sources — no synthesis applied.

## Folder Structure

### 01-client-side-search-libraries/
Web research comparing client-side JavaScript search libraries (2025-2026).
- **client-side-search-2026-evaluation.md** — 430-line Opus deep research: Fuse.js vs Orama vs MiniSearch vs FlexSearch vs Lunr vs Pagefind. Benchmarks, npm stats, bundle sizes, production case studies (Mastodon 2025). Result: Fuse.js v7.1.0 at 78% confidence.
- **fuse-js-config-reference.md** — Production Fuse.js v7.1.0 config: field weights, extended search syntax, Web Worker setup, scaling guidance.

### 02-advanced-search-algorithms/
Deep research on search ranking algorithms and scoring systems.
- **advanced-search-algorithms-bm25f-production.md** — 1,197-line production reference: BM25F scoring, trigram fuzzy matching, faceted search, ranking pipelines, inverted index, autocomplete Trie, performance benchmarks.
- **tfidf-search-engine-reference.md** — 780-line TF-IDF reference: field-weighted scoring, inverted index structure, fuzzy matching, real-time search with 300ms debounce.
- **bm25f-auto-categorization-research.md** — Opus deep research on applying BM25F to auto-categorize Jira tickets into themes. Hybrid Rules + BM25F + LLM approach.
- **bm25f-theme-detection-rules.md** — 14 theme keyword lists with BM25F scoring thresholds and conflict resolution.

### 03-search-solutions-comparison/
Web research comparing managed/server-side search platforms.
- **search-solutions-2025-2026-comparison.md** — 6 platforms compared: Meilisearch, Typesense, Algolia, Elasticsearch, Orama, PostgreSQL. Pricing, performance, features, self-hosted vs SaaS analysis.

### 04-search-architecture/
Deep research on search system architecture patterns.
- **search-architecture-v4-3layer.md** — 1,371-line 3-layer architecture: Pagefind (instant) → BM25F+Fuzzy (fast) → Semantic (smart). Build-time indexing, Web Worker integration.
- **search-architecture-earlier.md** — Earlier version of multi-layer search architecture.
- **dashboard-architecture-2k-items.md** — Opus deep research on progressive loading, virtual scrolling, chunked JSON for 2K+ item dashboards.
- **knowledge-base-architecture-research.md** — Opus deep research on data storage for searchable knowledge bases: chunked JSON, SQLite, NDJSON. Migration paths at scale.

### 05-search-ux-psychology/
Web research on search interface UX and user behavior.
- **search-ux-psychology-research.md** — Academic research: query behavior (3-4 words avg), position bias (27-40% first result), reformulation rates (65%), conversion impact (2-3x for searchers). Sources: Baymard, Nielsen Norman, Algolia, Google.
- **dashboard-ux-search-first-patterns.md** — 1,225-line Opus research on search-first UX patterns, Cmd+K shortcut, dark theme (#0a0e27), tab navigation, accessibility.

### 06-search-implementation-code/
Working code implementations from the research.
- **search-engine.js** — Core search engine with BM25F, fuzzy matching, faceted search.
- **search-component.jsx** — React search UI component.
- **search-worker.js** — Web Worker for off-thread search indexing.
- **build-search-index.js** — Node.js build-time index generation script.
- **lap-hub-app-fusejs.js** — Complete Fuse.js integration in LAP Intelligence Hub dashboard.
- **web-app-shell-with-search.html** — Full HTML template with embedded search engine.
- **IMPLEMENTATION_GUIDE.md** — Step-by-step guide for integrating the search UI.

## Sources

Research conducted across 2 Cowork chat windows using Opus sub-agents with 7-Phase Epistemic Research Framework. Web sources include: Algolia docs, GitHub repos, npm trends, Baymard Institute, Nielsen Norman Group, Mastodon production evaluation, npm-compare.com, BestofJS, Semrush, Statista, ResearchGate, Springer.

## Stats
- 21 files, ~590 KB
- ~8,000+ lines of research + code
- 150+ web sources cited
- 6 categories covering libraries → algorithms → platforms → architecture → UX → implementation
