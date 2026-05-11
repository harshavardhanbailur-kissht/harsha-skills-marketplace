# Classical Search Algorithms Reference Index

## Navigation

This directory contains comprehensive documentation of classical search algorithms used in information retrieval systems.

### Main Reference Document

**File:** `classical-search-algorithms-encyclopedia.md`
- **Length:** 1,810 lines
- **Size:** 48 KB
- **Content:** Complete technical encyclopedia with formulas, implementations, and production guidance

## Sections Overview

### 1. BM25 & BM25F (Ranking Functions)
- **Location:** Lines 33-169
- **Topics:** Mathematical formulas, parameter tuning (k1, b), field weighting, Elasticsearch defaults
- **Complexity:** O(k log n) query time
- **Best For:** Web search, e-commerce, general full-text search

### 2. TF-IDF (Vector Space Model)
- **Location:** Lines 171-262
- **Topics:** Variants (raw, log, augmented), IDF smoothing, normalization (L1/L2), ML integration
- **Complexity:** O(k log V) query time
- **Best For:** Machine learning pipelines, text classification, similarity computation

### 3. Inverted Index (Data Structure)
- **Location:** Lines 264-380
- **Topics:** Dictionary, posting lists, compression (delta, variable-byte, Golomb, FOR), skip pointers
- **Complexity:** O(N·M·log M) construction
- **Best For:** Backbone of all full-text search systems

### 4. Fuzzy Matching Algorithms
- **Location:** Lines 382-571
- **Subsections:**
  - Levenshtein Distance (O(mn), DP-based)
  - Damerau-Levenshtein (includes transpositions)
  - Bitap Algorithm (bitmask operations, Fuse.js)
  - Jaro-Winkler (prefix-weighted, name matching)
  - Trigram/N-gram (PostgreSQL pg_trgm)
  - Soundex & Metaphone (phonetic matching)

### 5. String Matching Algorithms
- **Location:** Lines 573-741
- **Subsections:**
  - Boyer-Moore (O(n/m) average, O(nm) worst)
  - Knuth-Morris-Pratt KMP (O(n+m) guaranteed)
  - Rabin-Karp (rolling hash, O(n+m) average)
  - Aho-Corasick (multi-pattern, O(n+z))
- **Best For:** Exact pattern matching, text searching, DNA sequences

### 6. Boolean Search Models
- **Location:** Lines 743-818
- **Topics:** AND/OR/NOT operations, short-circuit evaluation, CNF optimization, extended Boolean
- **Complexity:** O(n+m) with proper optimization
- **Best For:** Precise logical queries, advanced search syntax

### 7. Probabilistic Models
- **Location:** Lines 820-920
- **Subsections:**
  - Binary Independence Model (BIM)
  - Language Models for IR
  - Divergence from Randomness (DFR)
- **Best For:** Ranking functions, information retrieval research

### 8. Advanced Data Structures
- **Location:** Lines 922-1011
- **Subsections:**
  - Suffix Trees (O(m) pattern matching)
  - Suffix Arrays (space-efficient alternative)
  - LCP Array (Longest Common Prefix)
- **Best For:** Complex string algorithms, text indexing, bioinformatics

### 9. Decision Trees & Comparison
- **Location:** Lines 1013-1115
- **Contents:**
  - Algorithm selection flowchart
  - Complexity comparison matrix
  - Time/space/use-case analysis
- **Value:** Quick reference for choosing the right algorithm

### 10. Production Benchmarks
- **Location:** Lines 1117-1260
- **Data Sources:**
  - Elasticsearch/Lucene performance metrics
  - Real-world search system benchmarks
  - Fuzzy matching latencies
  - E-commerce, enterprise, academic search examples
- **Metrics:** Query latency (p50/p95/p99), throughput, index sizes

### 11. Implementation Pseudocode
- **Location:** Lines 1262-1350
- **Templates:**
  - Inverted Index Construction
  - BM25 Scoring Function
  - Boolean Query Intersection
- **Languages:** Language-agnostic pseudocode

### 12. Tuning Parameters by Scenario
- **Location:** Lines 1352-1410
- **Scenarios:**
  - Small E-commerce (< 1M products)
  - Large Product Datasets (1B+ items)
  - News/Content Search
  - Scientific/Academic Search
  - Search-as-You-Type (Autocomplete)

## Quick Reference Tables

### Algorithm Complexity Comparison
- **Query Time:** O(n/m) to O(nm) depending on algorithm
- **Space:** O(m) to O(mn)
- **Construction:** O(N·M·log M) for indexing

### Parameter Defaults (Production)
```
BM25:  k1=1.2, b=0.75
TF-IDF: No tunable parameters
Levenshtein Threshold: 1-2 for < 10 chars, 2+ for longer
Jaro-Winkler: prefix_length up to 4
```

### Use Case Matrix
| Algorithm | Web Search | E-commerce | Fuzzy | Names | Code | DNA |
|-----------|-----------|-----------|-------|-------|------|-----|
| BM25      | Excellent | Excellent | -     | Good  | Good | Fair|
| TF-IDF    | Good      | Good      | -     | Fair  | Fair | Fair|
| Levenshtein| -         | -         | Good  | Fair  | Good | Good|
| Jaro-W    | -         | -         | Fair  | Excellent| Fair| Fair|
| Boyer-Moore| -        | -         | -     | Fair  | Excellent| Excellent|
| Aho-Corasick| Good    | Good      | -     | -     | Excellent| Excellent|

## Research Sources

All content cross-referenced from:
- Elastic Blog (Elasticsearch documentation)
- Wikipedia (comprehensive algorithm descriptions)
- Stanford NLP Book (probabilistic IR)
- Academic databases and papers
- Production system documentation

## For Claude Skill Compilation

This encyclopedia is designed to serve as a knowledge base for:
1. Search algorithm specialists
2. Information retrieval engineers
3. Database optimization professionals
4. Machine learning practitioners
5. Students of algorithms and IR

## Document Statistics

- **Total Lines:** 1,810
- **Total Words:** 3,500+
- **Mathematical Formulas:** 40+
- **Pseudocode Examples:** 8+
- **Complexity Analyses:** 20+
- **Production Benchmarks:** 15+
- **Decision Trees:** 2
- **Tables:** 5+

## Format Notes

- All mathematical formulas in clear notation
- Pseudocode uses standard algorithm description format
- Examples use concrete data where possible
- References include clickable markdown links
- Complexity stated as Big-O notation

## Last Updated

March 1, 2026

## Usage

Start with the Table of Contents in the main encyclopedia file. Use the decision trees section to select appropriate algorithms for your use case, then reference the detailed sections for implementation guidance and tuning parameters.
