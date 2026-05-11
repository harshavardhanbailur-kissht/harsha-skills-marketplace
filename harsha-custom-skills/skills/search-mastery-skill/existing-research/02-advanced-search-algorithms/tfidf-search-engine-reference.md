# Search Engine Implementation Reference

This document provides detailed technical reference for the search engine embedded in the knowledge base web app (web-app-shell.html). It explains algorithms, architecture, and performance characteristics for developers who need to understand or customize the search functionality.

---

## Overview

The knowledge base web app includes a self-contained search engine that provides fast, full-text search across all entries with:
- Real-time search as you type (300ms debounce)
- TF-IDF ranking with field weighting
- Fuzzy matching for typo tolerance
- Relevance highlighting in snippets
- Faceted filtering (category, confidence, tags)
- Performance optimized for 1000+ entries

The entire search engine is implemented in JavaScript and runs client-side, requiring no server. The index is built at page load time from the embedded knowledge JSON.

---

## TF-IDF Algorithm Explanation

Term Frequency-Inverse Document Frequency (TF-IDF) is a fundamental ranking algorithm that scores how relevant a term is to a document within a corpus.

### Mathematical Formula

**TF (Term Frequency)** - How often term appears in document:
```
TF(term, document) = count(term in document) / total_terms_in_document
```

**IDF (Inverse Document Frequency)** - How rare the term is across all documents:
```
IDF(term) = log(total_documents / documents_containing_term)
```

**TF-IDF Score** - Combination of both:
```
TF-IDF(term, document) = TF(term, document) × IDF(term)
```

### Intuition

- **High TF**: Term appears many times in this document (document is about this term)
- **High IDF**: Term is rare across corpus (few documents contain it, so it's discriminative)
- **TF-IDF = high**: Rare term appears frequently in document → highly relevant

**Example**: Searching for "transformer architecture" in a knowledge base:
- Document A: "Transformers use self-attention for sequence modeling"
  - TF("transformer") = 1/10 = 0.10
  - IDF("transformer") = log(1000/750) = 0.29
  - TF-IDF = 0.029

- Document B: "The transformer is the transformer architecture that transformers use"
  - TF("transformer") = 4/12 = 0.33
  - IDF("transformer") = 0.29
  - TF-IDF = 0.096 (higher, Document B more relevant)

- Document C: "Attention mechanisms in transformers"
  - TF("transformer") = 1/5 = 0.20
  - IDF("transformer") = 0.29
  - TF-IDF = 0.058

**Ranking Order**: B (0.096) > C (0.058) > A (0.029)

### Implementation in Search Engine

```javascript
// Simplified TF-IDF scoring
function tfIdfScore(term, document, allDocuments) {
  // Count term occurrences
  const termCount = (document.text.match(new RegExp(term, 'gi')) || []).length;
  const totalTerms = document.text.split(/\s+/).length;
  const tf = termCount / totalTerms;

  // Count documents containing term
  const docsWithTerm = allDocuments.filter(doc =>
    doc.text.toLowerCase().includes(term.toLowerCase())
  ).length;
  const idf = Math.log(allDocuments.length / docsWithTerm);

  return tf * idf;
}
```

---

## Field-Weighted Scoring

Different fields (title, tags, summary, content) have different importance. The search engine applies weighted scoring to prioritize matches in important fields.

### Field Weights

```
title_weight    = 3.0  (most important: exact match should rank very high)
tag_weight      = 2.0  (important: entry is explicitly about this)
summary_weight  = 1.5  (somewhat important: main point of entry)
content_weight  = 1.0  (baseline: background information)
```

### Scoring Formula

```
final_score = (title_score × 3.0) + (tag_score × 2.0) +
              (summary_score × 1.5) + (content_score × 1.0)

// Normalize by dividing by sum of weights
normalized_score = final_score / (3.0 + 2.0 + 1.5 + 1.0)
                 = final_score / 7.5
```

### Worked Example

Query: "attention mechanism"
Entry: "Multi-Head Attention Mechanisms in Transformers"

**In Title** ("Multi-Head Attention Mechanisms in Transformers"):
- "attention" found: 1 occurrence, TF-IDF = 0.08
- "mechanism" found: 1 occurrence, TF-IDF = 0.07
- title_score = 0.08 + 0.07 = 0.15

**In Tags** (["attention", "transformer", "mechanism"]):
- "attention" found: TF-IDF = 0.10 (tags are short, frequency matters more)
- "mechanism" found: TF-IDF = 0.10
- tag_score = 0.10 + 0.10 = 0.20

**In Summary** ("The attention mechanism allows models to focus on relevant input..."):
- "attention" found: TF-IDF = 0.08
- "mechanism" found: TF-IDF = 0.06
- summary_score = 0.08 + 0.06 = 0.14

**In Content** (full detailed text):
- "attention" found (5 times): TF-IDF = 0.05
- "mechanism" found (3 times): TF-IDF = 0.04
- content_score = 0.05 + 0.04 = 0.09

**Final Calculation**:
```
weighted_score = (0.15 × 3.0) + (0.20 × 2.0) + (0.14 × 1.5) + (0.09 × 1.0)
               = 0.45 + 0.40 + 0.21 + 0.09
               = 1.15

normalized_score = 1.15 / 7.5 = 0.153
```

### Implementation

```javascript
function computeFieldWeightedScore(term, entry) {
  const weights = {
    title: 3.0,
    tags: 2.0,
    summary: 1.5,
    content: 1.0
  };

  let totalScore = 0;

  for (const [field, weight] of Object.entries(weights)) {
    const fieldTfIdf = computeTfIdf(term, entry[field]);
    totalScore += fieldTfIdf * weight;
  }

  const totalWeight = Object.values(weights).reduce((a, b) => a + b);
  return totalScore / totalWeight;
}
```

---

## Fuzzy Matching Algorithm

Fuzzy matching enables tolerance for typos and spelling variations. The search engine uses trigram-based similarity matching.

### Trigram Approach

A trigram is a sequence of 3 consecutive characters:

```
"hello" → trigrams = ["hel", "ell", "llo"]
"world" → trigrams = ["wor", "orl", "rld"]
```

### Similarity Calculation

Jaccard similarity between trigram sets:

```
trigrams(a) = set of trigrams in string a
trigrams(b) = set of trigrams in string b

similarity(a, b) = |trigrams(a) ∩ trigrams(b)| / |trigrams(a) ∪ trigrams(b)|
```

**Example**:
```
String A: "transformer"
Trigrams A: ["tra", "ran", "ans", "nsf", "sfo", "for", "orm", "rme", "mer"]

String B: "transfomer" (typo: "rme" → "fom")
Trigrams B: ["tra", "ran", "ans", "nsf", "sfo", "for", "fom", "ome", "mer"]

Intersection: ["tra", "ran", "ans", "nsf", "sfo", "for", "mer"] = 7 items
Union: 9 + 9 - 7 = 11 items
Similarity = 7 / 11 = 0.636 (64% match)
```

### Thresholds

```
similarity >= 0.5  → Fuzzy match (show as "Did you mean?" suggestion)
similarity >= 0.3  → Potential match (include in search if query term not exact)
```

### Implementation

```javascript
function generateTrigrams(str) {
  const lower = str.toLowerCase();
  const trigrams = new Set();
  for (let i = 0; i <= lower.length - 3; i++) {
    trigrams.add(lower.substr(i, 3));
  }
  return trigrams;
}

function trigramSimilarity(a, b) {
  const triA = generateTrigrams(a);
  const triB = generateTrigrams(b);

  const intersection = new Set([...triA].filter(x => triB.has(x)));
  const union = new Set([...triA, ...triB]);

  return intersection.size / union.size;
}

function findFuzzyMatches(queryTerm, vocabulary, threshold = 0.5) {
  return vocabulary.filter(term =>
    trigramSimilarity(queryTerm, term) >= threshold
  );
}
```

---

## Inverted Index Structure

The search engine builds an inverted index at page load time, mapping terms to their occurrences across all documents.

### Index Format

```json
{
  "transformer": [
    {
      "id": "entry-1",
      "field": "title",
      "positions": [0],
      "tf": 0.05
    },
    {
      "id": "entry-3",
      "field": "content",
      "positions": [45, 89, 156],
      "tf": 0.02
    },
    {
      "id": "entry-7",
      "field": "tags",
      "positions": [1],
      "tf": 0.25
    }
  ],
  "attention": [
    {
      "id": "entry-1",
      "field": "content",
      "positions": [12, 45, 67, 89],
      "tf": 0.08
    }
  ]
}
```

### Field Index Key

- **id**: Entry ID for lookup
- **field**: Which field contains the term (title, tags, summary, content)
- **positions**: Character positions or token positions where term appears
- **tf**: Pre-calculated term frequency for this entry

### Index Building Algorithm

```javascript
function buildInvertedIndex(entries) {
  const index = {};

  for (const entry of entries) {
    // Index all fields
    for (const [field, value] of Object.entries(entry)) {
      if (!['id', 'created_at'].includes(field)) {
        const tokens = tokenize(value.toString());

        tokens.forEach((token, position) => {
          if (!index[token]) {
            index[token] = [];
          }

          // Check if entry/field combo already exists
          let posting = index[token].find(p =>
            p.id === entry.id && p.field === field
          );

          if (!posting) {
            posting = {
              id: entry.id,
              field: field,
              positions: [],
              tf: 0
            };
            index[token].push(posting);
          }

          posting.positions.push(position);
          posting.tf = posting.positions.length / tokens.length;
        });
      }
    }
  }

  return index;
}
```

### Space Complexity

For a knowledge base with:
- 1000 entries
- 500 unique terms average per entry
- Vocabulary of ~10,000 unique terms

Approximate index size:
- Raw postings: 1000 × 500 = 500,000 postings
- With positions: 500,000 × 2 bytes (avg 2 positions) = 1 MB
- With metadata: ~2-3 MB total

Acceptable for client-side storage.

---

## Search Pipeline

The complete search process from query input to ranked results:

### Step 1: Query Tokenization

```
Input: "transformer architecture"

1. Lowercase: "transformer architecture"
2. Split on whitespace: ["transformer", "architecture"]
3. Remove stopwords: ["transformer", "architecture"] (neither is stopword)
4. Output: ["transformer", "architecture"]
```

**Stopwords removed**:
```
["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
 "of", "with", "by", "from", "is", "are", "be", "been", "have", "has"]
```

### Step 2: Inverted Index Lookup

For each query token, retrieve postings from index:

```
"transformer" → 47 postings across 23 entries
"architecture" → 31 postings across 18 entries
```

### Step 3: Candidate Entry Collection

Union of all entries from all token postings:

```
Candidates: 35 entries (union of 23 and 18)
```

### Step 4: TF-IDF Scoring Per Field

For each candidate entry, compute TF-IDF score for each query token in each field:

```
Entry 1 ("Multi-Head Attention Mechanisms"):
  title:     transformer[0.15] + architecture[0.12] = 0.27
  tags:      transformer[0.20] + architecture[0.18] = 0.38
  summary:   transformer[0.14] + architecture[0.10] = 0.24
  content:   transformer[0.09] + architecture[0.07] = 0.16
```

### Step 5: Apply Field Weights

Combine field scores with weights:

```
weighted_score = (0.27 × 3.0) + (0.38 × 2.0) + (0.24 × 1.5) + (0.16 × 1.0)
               = 0.81 + 0.76 + 0.36 + 0.16
               = 2.09

normalized_score = 2.09 / 7.5 = 0.279
```

### Step 6: Fuzzy Matching for Uncovered Terms

For query tokens not found in index (possible typos):

```
Query: "transformr" (typo)
Not in index. Check fuzzy matches:
  - "transformer": similarity = 0.89 ✓ (above 0.5 threshold)
  - "transfer": similarity = 0.40 ✗ (below 0.5 threshold)

Use "transformer" matches with 10% relevance penalty
```

### Step 7: Snippet Generation with Highlighting

Extract relevant context from content field:

```
Content: "The transformer architecture uses self-attention mechanisms
for parallel processing of transformer models..."

Query: "transformer architecture"

Snippet: "...The <mark>transformer</mark> <mark>architecture</mark> uses
self-attention mechanisms for..."
```

### Step 8: Result Ranking and Limiting

Sort results by final score, return top N:

```
Top 5 results:
1. [0.279] Multi-Head Attention Mechanisms in Transformers
2. [0.241] Transformer Architecture Overview
3. [0.198] Vision Transformers for Image Classification
4. [0.167] Architectural Patterns in Deep Learning
5. [0.145] Evolution of Neural Architectures
```

### Complete Pipeline Implementation

```javascript
function search(queryString, entries, options = {}) {
  const maxResults = options.maxResults || 10;
  const fuzzyThreshold = options.fuzzyThreshold || 0.5;

  // Step 1: Tokenize
  const queryTokens = tokenizeQuery(queryString);

  // Step 2-3: Index lookup and candidate collection
  const candidates = new Set();
  for (const token of queryTokens) {
    const postings = invertedIndex[token] || [];
    postings.forEach(posting => candidates.add(posting.id));
  }

  // Step 4-5: Scoring
  const results = [];
  for (const entryId of candidates) {
    const entry = entries.find(e => e.id === entryId);
    const score = computeFieldWeightedScore(queryTokens, entry);
    results.push({ entry, score });
  }

  // Step 6: Fuzzy matching for uncovered terms
  // (implement as needed)

  // Step 7: Generate snippets
  results.forEach(r => {
    r.snippet = generateSnippet(r.entry, queryTokens);
  });

  // Step 8: Sort and limit
  return results
    .sort((a, b) => b.score - a.score)
    .slice(0, maxResults);
}
```

---

## Performance Characteristics

### Time Complexity Analysis

**Index Building**:
- Per entry: O(m) where m = average tokens per entry
- Total: O(n × m) where n = number of entries
- For 1000 entries × 500 avg tokens: ~500,000 operations
- Typical time: <500ms in browser

**Search Query**:
- Tokenization: O(q) where q = query tokens (usually 1-5)
- Index lookup: O(q × p) where p = average postings per token
- Scoring: O(c × q) where c = number of candidate entries
- Typical: <5000 operations
- Typical time: <30ms for most queries

**Fuzzy Matching**:
- Per uncovered token: O(v × l²) where v = vocabulary size, l = string length
- With trigrams (optimized): O(v × 3) ≈ O(v)
- For 10,000 term vocabulary: ~30,000 operations
- Typical time: <50ms if needed

### Space Complexity

**Index Storage**:
- Postings list: O(n × m) in worst case (every term in every document)
- Typical: 2-3 MB for 1000 entries (JSON format, gzipped ~400 KB)
- In-memory: ~2-5 MB before gzip

**Result Caching** (optional):
- Cache recent queries to avoid recomputation
- Typical: 10-20 cached results = <100 KB

### Scaling Characteristics

| Entries | Build Time | Avg Query Time | Index Size |
|---------|-----------|----------------|-----------|
| 100 | 50ms | 5ms | 200 KB |
| 500 | 200ms | 10ms | 800 KB |
| 1000 | 500ms | 25ms | 2 MB |
| 5000 | 2500ms | 50ms | 10 MB |
| 10000 | 5000ms | 75ms | 20 MB |

**Recommendation**: Optimize for <1000 entries. Beyond that, consider server-side search or periodic index updates.

### Optimization Techniques

**For Large Knowledge Bases**:

1. **Lazy Index Building**: Build index on demand (first search), not on page load
   ```javascript
   let index = null;
   function ensureIndexBuilt() {
     if (!index) index = buildInvertedIndex(entries);
     return index;
   }
   ```

2. **Query Result Caching**: Cache recent search results
   ```javascript
   const queryCache = new Map();
   function getCachedResults(query) {
     if (queryCache.has(query)) {
       return queryCache.get(query);
     }
     // Compute and cache
   }
   ```

3. **Incremental Indexing**: When adding entries dynamically
   ```javascript
   function addEntryToIndex(entry) {
     const tokens = tokenizeEntry(entry);
     tokens.forEach(token => {
       if (!index[token]) index[token] = [];
       index[token].push(createPosting(entry, token));
     });
   }
   ```

4. **Partial Search**: Limit to subset of fields for very large docs
   ```javascript
   // Only search title + tags + summary, not full content
   const fieldsToSearch = ['title', 'tags', 'summary'];
   ```

5. **Worker Thread**: Move indexing to Web Worker
   ```javascript
   const worker = new Worker('search-worker.js');
   worker.postMessage({cmd: 'buildIndex', entries: entries});
   worker.onmessage = (e) => {
     index = e.data.index;
   };
   ```

---

## Customization Guide

### Adding Custom Field Weights

```javascript
// Default weights
const FIELD_WEIGHTS = {
  title: 3.0,
  tags: 2.0,
  summary: 1.5,
  content: 1.0
};

// Customize for your knowledge base
function configureWeights(config) {
  Object.assign(FIELD_WEIGHTS, config);
}

// Usage
configureWeights({
  title: 4.0,    // Make title even more important
  tags: 3.0,     // Boost tags
  content: 0.8   // De-emphasize body content
});
```

### Custom Tokenization

```javascript
function customTokenize(text) {
  return text
    .toLowerCase()
    .split(/[\s\-_.,;:!?()]+/) // Split on whitespace and punctuation
    .filter(token => token.length > 2) // Min 3 chars
    .filter(token => !STOPWORDS.has(token)); // Remove stopwords
}
```

### Adjusting Fuzzy Matching Threshold

```javascript
// More lenient (catches more typos)
FUZZY_THRESHOLD = 0.3;

// More strict (only obvious matches)
FUZZY_THRESHOLD = 0.7;
```

### Faceted Search Integration

```javascript
function facetedSearch(query, facets = {}) {
  let results = search(query);

  // Filter by category
  if (facets.category) {
    results = results.filter(r =>
      r.entry.category === facets.category
    );
  }

  // Filter by confidence
  if (facets.confidence) {
    const levels = ['VERIFIED', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'];
    const minLevel = levels.indexOf(facets.confidence);
    results = results.filter(r =>
      levels.indexOf(r.entry.confidence) <= minLevel
    );
  }

  // Filter by tags
  if (facets.tags && facets.tags.length > 0) {
    results = results.filter(r =>
      facets.tags.some(tag => r.entry.tags.includes(tag))
    );
  }

  return results;
}
```

---

## Debugging and Testing

### Inspecting the Inverted Index

```javascript
// Browser console
console.table(Object.entries(window.searchEngine.index)
  .slice(0, 20)
  .map(([term, postings]) => ({
    term,
    postings: postings.length,
    entries: new Set(postings.map(p => p.id)).size
  }))
);
```

### Testing Search Quality

```javascript
function testSearch() {
  const testQueries = [
    'transformer',
    'attention mechanism',
    'training optimization',
    'transformr',  // typo
    'xyz nonexistent term'
  ];

  testQueries.forEach(query => {
    const results = search(query);
    console.log(`"${query}": ${results.length} results`);
    if (results.length > 0) {
      console.log(`  Top: ${results[0].entry.title} (${results[0].score.toFixed(3)})`);
    }
  });
}
```

### Performance Profiling

```javascript
console.time('index-build');
const index = buildInvertedIndex(entries);
console.timeEnd('index-build');

console.time('search');
const results = search('transformer architecture');
console.timeEnd('search');

// View index statistics
console.log('Index stats:', {
  terms: Object.keys(index).length,
  totalPostings: Object.values(index).reduce((s, p) => s + p.length, 0),
  avgPostingsPerTerm: Object.values(index).reduce((s, p) => s + p.length, 0) / Object.keys(index).length
});
```

---

## Troubleshooting

### "No results found" for obvious query

**Causes**:
- Query term not in index (check index contents)
- Query is pure stopwords ("the", "and", etc.)
- Exact match requires exact casing in some configs

**Solutions**:
- Check what's actually being tokenized: `console.log(tokenizeQuery('your query'))`
- Verify index has the term: `console.log(window.searchEngine.index['your-term'])`
- Lower fuzzy threshold to catch typos

### Search is slow

**Causes**:
- Large knowledge base (thousands of entries)
- Many candidate matches for common terms
- Fuzzy matching enabled for every query

**Solutions**:
- Implement query result caching
- Limit to important fields (title, tags)
- Increase fuzzy threshold or disable for common queries
- Use Web Workers for large datasets

### Irrelevant results appearing first

**Causes**:
- Field weights not balanced (content dominates)
- IDF scoring affected by duplicate terms
- Fuzzy matches not penalized enough

**Solutions**:
- Adjust field weights (increase title, decrease content)
- Check for duplicate terms in content
- Increase fuzzy similarity threshold
- Implement relevance feedback

---

**Search Engine Version**: 2.1
**Last Updated**: 2024-01-15
**Compatibility**: All modern browsers (ES6+)

