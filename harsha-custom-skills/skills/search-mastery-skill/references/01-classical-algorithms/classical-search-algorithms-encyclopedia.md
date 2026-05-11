# Classical Search Algorithms: A Comprehensive Encyclopedia

## Table of Contents

1. [BM25 & BM25F](#bm25--bm25f)
2. [TF-IDF](#tf-idf)
3. [Inverted Index](#inverted-index)
4. [Fuzzy Matching Algorithms](#fuzzy-matching-algorithms)
5. [String Matching Algorithms](#string-matching-algorithms)
6. [Boolean Search Models](#boolean-search-models)
7. [Probabilistic Models](#probabilistic-models)
8. [Advanced Data Structures](#advanced-data-structures)
9. [Decision Trees & Comparison](#decision-trees--comparison)
10. [Production Benchmarks](#production-benchmarks)

---

## BM25 & BM25F

### The Gold Standard of Probabilistic IR

BM25 (Okapi BM25) stands for "Best Matching 25" and represents the 25th iteration of the probabilistic model developed by Stephen E. Robertson and Karen Spärck Jones in the 1970s-1980s. It remains the dominant ranking function in modern search engines including Elasticsearch, Lucene, and Apache Solr.

### Mathematical Formula

The core BM25 ranking function for a query Q containing terms q₁, q₂, ..., qₙ is:

```
BM25(D, Q) = Σ IDF(qᵢ) · [f(qᵢ, D) · (k₁ + 1)] / [f(qᵢ, D) + k₁ · (1 - b + b · |D|/avg_len)]
```

Where:
- **f(qᵢ, D)** = raw term frequency of term qᵢ in document D
- **IDF(qᵢ)** = inverse document frequency of term qᵢ
- **|D|** = length of document D in words
- **avg_len** = average document length in the collection
- **k₁** = term frequency saturation parameter (tuning parameter)
- **b** = length normalization parameter (tuning parameter)

### IDF Component

The inverse document frequency component is typically calculated as:

```
IDF(qᵢ) = log((N - df(qᵢ) + 0.5) / (df(qᵢ) + 0.5))
```

Where:
- **N** = total number of documents in the collection
- **df(qᵢ)** = number of documents containing term qᵢ

### The k₁ Parameter (Term Frequency Saturation)

**Interpretation:** For documents of average length, k₁ represents the term frequency value that yields 50% of the maximum possible score for that term.

**Mathematical Behavior:**
- When tf ≤ k₁: The score curve rises steeply with increasing term frequency
- When tf > k₁: The score curve flattens, demonstrating saturation

**Default Value:** 1.2 (Elasticsearch/Lucene)

**Tuning Guidance:**
- **Increase toward 2.0:** Use when term frequency is highly informative, particularly for longer documents where repeated mentions genuinely indicate relevance (e.g., scientific papers, code documentation)
- **Decrease toward 0.5:** Use when you want to reduce the impact of raw term frequency and rely more on term importance (e.g., noisy user-generated content, short documents)

### The b Parameter (Document Length Normalization)

**Interpretation:** Controls how much document length affects the ranking score.

**Mathematical Behavior:**
- When b = 0: No length normalization applied; longer documents inherently score higher
- When b = 1: Full length normalization; penalizes longer documents proportionally
- When b = 0.5: Moderate normalization (Elasticsearch/Lucene default)

**Default Value:** 0.75 (Elasticsearch/Lucene)

**Tuning Guidance:**
- **Increase toward 1.0:** Use when documents have naturally varying lengths and you want to normalize heavily (e.g., variable-length articles, user reviews)
- **Decrease toward 0.25:** Use when document length variation is meaningful to relevance (e.g., longer academic papers should naturally score higher for technical queries)

### Probabilistic Foundation

BM25 roots itself in the **Probabilistic Ranking Principle**, which states: "Documents should be ranked by the probability that they are relevant to the query, given the user's query and assessments of relevance."

The model combines two competing approaches:
1. **BM11 (Binary Independence Model)** - treats terms as binary present/absent
2. **BM15** - incorporates term frequency

BM25 uses parameter b as a scaling factor to interpolate between these approaches.

### Time & Space Complexity

- **Query Time Complexity:** O(k · log(n)) where k is the number of matching documents and n is collection size
- **Space Complexity:** O(V · D) for the inverted index, where V is vocabulary size and D is average posting list length
- **Indexing Time:** O(N) where N is total number of documents

### When to Use BM25

✅ **Best For:**
- General-purpose full-text search
- E-commerce product search
- Content discovery systems
- Web search applications
- Long or variable-length documents
- Collections with natural term frequency variation
- When precision and recall are both important

❌ **Not Ideal For:**
- Exact phrase matching (use phrase queries instead)
- Structured data (use field-specific approaches)
- Semantic similarity (use embeddings)
- Very short documents with binary relevance (use TF-IDF)
- Multi-language content without language-specific tuning

### Production Considerations

**Shard Impact:** In Elasticsearch, BM25 statistics are computed per-shard. Documents in shards with fewer matching documents score higher. Use primary shard queries for consistent results.

**Text Analysis:** Text analysis setup (tokenization, stemming, synonyms, filters) has far greater impact on relevance than parameter tuning.

### BM25F: Multi-Field Extension

BM25F extends BM25 to handle documents with multiple weighted fields (title, body, metadata, etc.).

#### Mathematical Formula

```
BM25F(D, Q) = Σ IDF(qᵢ) · [B_f(qᵢ, D) · (k₁ + 1)] /
              [B_f(qᵢ, D) + k₁ · (1 - b + b · |D|/avg_len)]
```

Where B_f combines weighted term frequencies from all fields:

```
B_f(qᵢ, D) = Σ wⱼ · tf(qᵢ, fⱼ) / (1 - bⱼ + bⱼ · |fⱼ|/avg_len_j)
```

- **wⱼ** = weight for field j (e.g., title=3.0, body=1.0)
- **tf(qᵢ, fⱼ)** = term frequency in field j
- **bⱼ** = field-specific length normalization parameter

#### Field Weighting Strategy

Field weights act multiplicatively on raw term frequency before aggregation:

```
Practical Example:
Title field: weight=3.0, b=0.75
Body field: weight=1.0, b=0.75
Metadata field: weight=0.5, b=0.5

Query "Python Programming"
If "Python" appears 2x in title and 5x in body:
Contribution = 3.0 * 2 + 1.0 * 5 = 11 (title dominates)
```

#### Implementation in Elasticsearch

Elasticsearch implements BM25F through the `combined_fields` query:

```json
{
  "query": {
    "combined_fields": {
      "query": "python programming",
      "fields": [
        "title^3",
        "body^1",
        "tags^0.5"
      ],
      "operator": "or"
    }
  }
}
```

---

## TF-IDF

### Term Frequency-Inverse Document Frequency

TF-IDF is a fundamental feature extraction technique that reflects the importance of a term to a document within a collection. While simpler than BM25, it remains highly relevant for certain use cases.

### Mathematical Formulation

**Basic TF-IDF:**

```
TF-IDF(t, d) = TF(t, d) × IDF(t)
```

### Term Frequency (TF) Variants

**1. Raw Frequency (simplest):**
```
TF(t, d) = frequency(t, d)
```

**2. Logarithmically Scaled:**
```
TF(t, d) = 1 + log(frequency(t, d))
```

**3. Augmented (normalized by document length):**
```
TF(t, d) = 0.5 + 0.5 × (frequency(t, d) / max_frequency_in_doc)
```

**4. Double Normalized (dampens term frequency impact):**
```
TF(t, d) = 0.5 + 0.5 × (frequency(t, d) / max_term_freq_in_corpus)
```

### Inverse Document Frequency (IDF) Variants

**1. Standard IDF:**
```
IDF(t) = log(N / df(t))
```

**2. IDF with Smoothing (prevents zero values):**
```
IDF(t) = log(N / (1 + df(t)))
```

**3. BM25-style IDF (as discussed above):**
```
IDF(t) = log((N - df(t) + 0.5) / (df(t) + 0.5))
```

### Normalization Methods

**L1 Normalization (Manhattan):**
```
TF-IDF_normalized(t, d) = TF-IDF(t, d) / Σ|TF-IDF(t', d)|
```

**L2 Normalization (Euclidean/Cosine):**
```
TF-IDF_normalized(t, d) = TF-IDF(t, d) / √(Σ TF-IDF(t', d)²)
```

### Time & Space Complexity

- **Indexing Time:** O(N · M) where N is number of documents, M is average terms per document
- **Query Time:** O(k · log(V)) where k is number of matching documents, V is vocabulary size
- **Space Complexity:** O(V · D) for inverted index

### When to Use TF-IDF

✅ **Best For:**
- Text classification and machine learning pipelines
- Document similarity computation
- Keyword extraction
- Short text matching (where BM25 saturation isn't beneficial)
- Systems requiring explicit term importance scores
- Vector space model implementations
- Binary or near-binary relevance scenarios

❌ **Not Ideal For:**
- Long documents with high term frequency variance
- Collections with extreme document length differences
- Web-scale search (BM25 outperforms)
- Real-time search with diverse corpora
- When query term frequency matters (BM25 handles this better)

### TF-IDF vs BM25 Comparison

| Aspect | TF-IDF | BM25 |
|--------|--------|------|
| Term Frequency Saturation | Linear growth | Logarithmic saturation |
| Document Length Normalization | Not built-in | Integrated, tunable |
| Mathematical Foundation | Vector space model | Probabilistic |
| Term Frequency Handling | Direct | Sophisticated |
| Production Performance | Good for ML | Better for IR |
| Tuning Parameters | None | k₁, b |
| Interpretability | High (explicit weights) | Medium |
| Typical Usage | ML pipelines | Search engines |

---

## Inverted Index

### The Backbone Data Structure of Full-Text Search

An inverted index is a fundamental data structure that maps terms to their locations in documents. It inverts the relationship: instead of "document → terms," it stores "term → documents."

### Basic Structure

```
Dictionary (terms):
  "algorithm"  → [posting_list_1]
  "data"       → [posting_list_2]
  "search"     → [posting_list_3]

Posting Lists (locations):
  posting_list_1: [docID:1, docID:5, docID:12, ...]
  posting_list_2: [docID:2, docID:3, docID:7, ...]
  posting_list_3: [docID:1, docID:2, docID:4, ...]
```

### Components

**1. Dictionary (Lexicon):**
- Stores all unique terms in the collection
- Indexed for fast lookup (B-tree, hash table)
- Maps to the offset of posting lists on disk

**2. Posting Lists (Inverted Lists):**
- Stores document IDs where term appears
- Typically sorted by document ID for efficient intersection
- Can include additional metadata (term positions, term frequencies, field information)

**3. Enhanced Posting List Format:**
```
Term: "algorithm"
Posting List: [
  (docID: 1, tf: 3, positions: [2, 15, 42]),
  (docID: 5, tf: 1, positions: [7]),
  (docID: 12, tf: 5, positions: [1, 8, 19, 25, 33])
]
```

### Building an Inverted Index

**Single-Pass Algorithm:**

```
Algorithm BuildInvertedIndex:
1. Read all documents
2. Tokenize each document into terms
3. For each term, record (docID, tf, positions)
4. Sort posting lists by docID
5. Apply compression (optional)
6. Write to disk/memory

Complexity: O(N · M · log(M))
where N = docs, M = avg terms/doc
```

### Compression Techniques

Posting lists often represent the largest component of an inverted index. Compression is critical for production systems.

**1. Delta Encoding:**
- Store differences between consecutive docIDs rather than absolute values
- Example: [1, 5, 12, 20] → [1, 4, 7, 8] (differences)
- Reduces range of values, improving compression

**2. Variable-Byte Encoding:**
- Uses fewer bytes for small numbers, more for large
- Each byte has 1 continuation bit + 7 data bits
- Typical compression ratio: 4:1 to 10:1

**3. Golomb-Rice Encoding:**
- Optimal for power-law distributions (common in IR)
- Uses unary coding for quotient, binary for remainder
- Better compression than variable-byte for many IR workloads

**4. Frame-of-Reference (FOR):**
- Groups posting list into blocks (e.g., 256 documents)
- Uses minimum bits needed for each block
- Excellent for sequential access patterns

### Skip Pointers (Skip Lists)

Skip pointers enable jumping over irrelevant portions of posting lists during intersection operations.

**Classic Approach:**
```
Posting List with skip pointers:
[1] → [2] → [3] → [4] → [5] → [9] → [12] → [15]
               ↑                    ↑
            skip pointers every √n positions

Intersection Query "term1 AND term2":
When term1's list reaches [15]:
- term2's list can skip [9, 12] and jump directly to [15]
```

**Skip Pointer Strategy:**
- Place skip pointers every √n positions for n posting list items
- Reduces time complexity of intersection from O(n + m) to O(n + m - k·√n)
- Trade-off: slightly larger index size for faster queries

### Time & Space Complexity

- **Index Construction:** O(N · M · log(M))
- **Single Term Lookup:** O(log(V) + k) where V is vocabulary, k is list length
- **Boolean AND Query:** O(k₁ + k₂) with skip pointers, O(k₁ · k₂) without
- **Space:** O(N · avg_posting_list_size)

### Building vs Updating Indexes

**Batch Building (Initial):**
- Single pass over all documents
- Highly optimized, typically O(N · log N)
- Used for static collections

**Incremental Updates:**
- Add new documents to existing index
- Merge mini-indexes periodically
- Critical for real-time search systems

### Memory vs Disk Trade-offs

```
Production Considerations:

Scenario 1: High-Traffic Search (Google, Elasticsearch)
- Keep dictionary in RAM (10-100 MB)
- Memory-map posting lists or cache hot ones
- Use compression for disk storage

Scenario 2: Embedded Search (mobile app)
- Entire index in RAM (constraint: memory)
- Aggressive compression critical
- Limited posting list cache

Scenario 3: Batch Processing
- Index on disk, stream processing
- Sequential access patterns
- Compression less critical than access speed
```

---

## Fuzzy Matching Algorithms

### Handling Typos, Misspellings, and Approximate Matches

Fuzzy matching enables search systems to find relevant results despite spelling errors, typos, and character variations.

### Levenshtein Distance (Edit Distance)

**Definition:** Minimum number of single-character edits (insertions, deletions, substitutions) to transform one string into another.

**Mathematical Formula:**

```
For strings A and B:
- If min(|A|, |B|) = 0: distance = max(|A|, |B|)
- Otherwise: distance = min(
    levenshtein(A[1:], B) + 1,           // deletion
    levenshtein(A, B[1:]) + 1,           // insertion
    levenshtein(A[1:], B[1:]) + cost     // substitution
  )
  where cost = 0 if A[0] = B[0], else 1
```

**Dynamic Programming Implementation:**

```
Algorithm LevenshteinDistance(A, B):
  m ← length(A)
  n ← length(B)

  // Create matrix (m+1) × (n+1)
  d[0..m][0..n]

  // Initialize first row and column
  for i ← 0 to m: d[i][0] ← i
  for j ← 0 to n: d[0][j] ← j

  // Fill matrix
  for i ← 1 to m:
    for j ← 1 to n:
      cost ← 0 if A[i-1] = B[j-1] else 1
      d[i][j] ← minimum(
        d[i-1][j] + 1,      // deletion
        d[i][j-1] + 1,      // insertion
        d[i-1][j-1] + cost  // substitution
      )

  return d[m][n]
```

**Complexity Analysis:**
- **Time:** O(m · n) where m, n are string lengths
- **Space:** O(m · n) for matrix, can be optimized to O(min(m, n))

**Practical Threshold:**
```
Threshold = 1: "teh" matches "the" (common typo)
Threshold = 2: "algoritm" matches "algorithm"
Threshold = 1: Appropriate for strings < 10 characters
Threshold = 2: Recommended for strings 10-50 characters
```

### Damerau-Levenshtein Distance

**Definition:** Extends Levenshtein by including transposition of adjacent characters as a single edit operation.

**Key Insight:** Empirical studies show ~80% of spelling errors are single-character edits; Damerau-Levenshtein catches an important subset.

**Algorithm Variant 1: Optimal String Alignment (Restricted):**

```
Adds one recurrence to standard Levenshtein:
if i > 1 and j > 1 and A[i] = B[j-1] and A[i-1] = B[j]:
  d[i][j] = min(d[i][j], d[i-2][j-2] + cost)  // transposition
```

**Complexity:** O(m · n)

**Algorithm Variant 2: True Damerau-Levenshtein:**

```
Allows each substring to be edited multiple times
Uses Lowrance & Wagner approach with intermediate dictionary

Complexity: O(m · n) time, O(m · n) space
Performance: 20-30% slower than restricted version
```

### Bitap Algorithm (Approximate Matching)

Used by Fuse.js for efficient fuzzy string matching with bitmasks.

**Core Idea:** Use bitwise operations to achieve near-linear performance for fuzzy matching with small error thresholds.

**Algorithm Outline:**

```
PreProcess(pattern, alphabet_size):
1. For each character c in alphabet:
   - Create bitmask showing c positions in pattern

Matching(text, pattern, max_errors):
1. Initialize score = all 1s (worst case)
2. For each character in text:
   - Look up bitmask for this character
   - Update score using bitwise operations
   - If score ≤ max_errors AND all bits set: match found

Complexity: O(n + m + errors × alphabet_size)
```

**When Each Bit = 0: Match; When = 1: Mismatch**

**Implementation Characteristics:**
- Efficient for patterns up to machine word size (32-64 chars)
- Performs better with small error thresholds (≤ 2)
- Ideal for real-time client-side search (used by Fuse.js)

### Jaro-Winkler Similarity

**Definition:** Compares matching characters and transpositions, with preference for matching prefixes.

**Mathematical Formula:**

```
Jaro Similarity:
jaro = (m / |A|) + (m / |B|) + ((m - t) / m) / 3

Where:
  m = number of matching characters
  t = number of transpositions / 2
  |A|, |B| = lengths of strings

Jaro-Winkler (with prefix bonus):
jaro_winkler = jaro + (prefix_length × 0.1 × (1 - jaro))

  prefix_length = common prefix up to 4 characters
  0.1 = standard scaling factor (tunable)
```

**Characteristics:**
- Matches characters within max(|A|, |B|) / 2 - 1
- Particularly good for name matching
- More lenient than Levenshtein for similar strings

**Example:**

```
"DWAYNE" vs "DUANE"
- Jaro: 0.822
- Jaro-Winkler: 0.840 (prefix boost)

"DIXON" vs "DICKSON"
- Jaro: 0.767
- Jaro-Winkler: 0.813 (prefix boost)
```

**Complexity:**
- **Time:** O(m · n)
- **Space:** O(1)

### Trigram / N-gram Matching

**Definition:** Break strings into fixed-length substrings (trigrams for n=3) and compare sets.

**Index Construction:**

```
Algorithm BuildTrigramIndex:
1. For each document d:
   - Extract all trigrams (overlapping)
   - Example: "hello" → ["hel", "ell", "llo"]
   - Store (trigram → [docID, position])
2. Create inverted index of trigrams
```

**Query Matching:**

```
Algorithm TrigramSearch(query, threshold):
1. Extract trigrams from query
2. Look up each trigram in index
3. Count trigram overlaps with candidates
4. Rank by Jaccard similarity:
   similarity = |common_trigrams| / |union_trigrams|
5. Return documents exceeding threshold
```

**Similarity Metric:**

```
Jaccard Similarity = |A ∩ B| / |A ∪ B|
Cosine Similarity = |A ∩ B| / √(|A| × |B|)
```

**PostgreSQL Implementation (pg_trgm):**

```
Index Creation:
CREATE INDEX idx_trigram ON documents USING gist(name gist_trgm_ops);

Query:
SELECT * FROM documents WHERE name % 'John Smit'
LIMIT 10;

Performance: 100x faster than LIKE for similarity search
```

**Complexity:**
- **Index Build:** O(N · M × 3) where M is average string length
- **Query:** O(k) with n-gram index, k = matching documents
- **Memory:** O(V × 3) where V is unique trigrams

### Soundex (Phonetic Matching)

**Algorithm:**

```
1. Keep first letter of word
2. Remove vowels, h, w, y (except first letter)
3. Replace consonants with codes:
   B, F, P, V → 1
   C, G, J, K, Q, S, X, Z → 2
   D, T → 3
   L → 4
   M, N → 5
   R → 6
4. Remove duplicate consecutive codes
5. Pad or truncate to 4 characters

Example:
"ROBERT" → "R" + "163" = "R163"
"RUBIN" → "R" + "163" = "R163"  (both code to same)
"RUPERT" → "R" + "163" = "R163"
```

**Characteristics:**
- Invented 1918, patented 1922
- Very fast (fixed output size)
- Limited to English pronunciation
- High false positive rate

### Metaphone (Improved Phonetic)

**Improvements over Soundex:**

```
1. Considers full string context (Soundex uses first characters)
2. Alphabet-based output (not numeric)
3. Context-sensitive rules ("KNIGHT" → "NT" not "KN")
4. Double Metaphone: generates primary and secondary encodings
5. Handles more phonetic variations
```

**Performance:**

```
Soundex: 60-70% accuracy for English names
Metaphone: 85-90% accuracy
Double Metaphone: 90-95% accuracy

Typical Use Case: Phonetic search in e-commerce
"John Smyth" matches "Jon Smith" via Double Metaphone
```

---

## String Matching Algorithms

### Exact Pattern Matching in Text

### Boyer-Moore Algorithm

**Intuition:** Start matching from the END of the pattern, allowing large jumps when mismatches occur.

**Key Components:**

1. **Bad Character Rule:**
```
When mismatch occurs at position j:
- Find the rightmost occurrence of mismatched character in pattern
- Jump pattern to align with this occurrence
- If character not in pattern, skip entire pattern length

Example:
Pattern: "EXAMPLE"
Text: "HERE_IS_EXAMPLE"
      "EXAMPLE" (mismatch at 'E')
      "      EXAMPLE" (jump 6 positions)
```

2. **Good Suffix Rule:**
```
When mismatch occurs:
- Find longest suffix of pattern that matches a substring
- Use this to position pattern for next comparison

Example:
Pattern: "ABABAB"
Mismatch after matching "AB"
→ Next occurrence of "AB" in pattern before current position
→ Shift pattern appropriately
```

**Algorithm Outline:**

```
Algorithm BoyerMoore(text, pattern):
  m ← length(pattern)
  n ← length(text)

  // Preprocess: build bad character table
  bad_char[256] ← compute_bad_character_table(pattern)
  good_suffix ← compute_good_suffix_table(pattern)

  s ← 0  // shift in text
  while s <= n - m:
    j ← m - 1  // start from end of pattern

    while j >= 0 AND pattern[j] = text[s + j]:
      j ← j - 1

    if j < 0:
      return s  // match found
    else:
      // Calculate shift using both rules
      bad_shift ← j - bad_char[text[s + j]]
      good_shift ← good_suffix[j]
      s ← s + max(bad_shift, good_shift)

  return -1  // no match
```

**Complexity Analysis:**
- **Best Case:** O(n/m) - superlinear when pattern finds many mismatches early
- **Average Case:** O(n)
- **Worst Case:** O(n · m) - rare, when pattern is substring of repeating text
- **Space:** O(m + σ) where σ is alphabet size

**When Boyer-Moore Excels:**
- Long patterns in large alphabets (e.g., DNA sequences, binary data)
- Multiple character mismatches trigger large jumps
- Real-world text with diverse characters

### Knuth-Morris-Pratt (KMP) Algorithm

**Intuition:** Avoid re-comparing characters using preprocessing that identifies pattern structure.

**Key Concept: Failure Function (LPS - Longest Proper Prefix Suffix)**

```
For pattern "ABABAB":
Index:  0 1 2 3 4 5
Pattern: A B A B A B
LPS:    0 0 1 2 3 4

LPS[i] = length of longest proper prefix of pattern[0..i]
         that is also a suffix of pattern[0..i]

Example:
pattern[0..3] = "ABAB"
- Prefix "AB" = Suffix "AB" → LPS[3] = 2
```

**Building the LPS Array:**

```
Algorithm ComputeLPS(pattern):
  m ← length(pattern)
  lps[0] ← 0
  j ← 0  // length of previous LPS

  for i ← 1 to m - 1:
    while j > 0 AND pattern[j] ≠ pattern[i]:
      j ← lps[j - 1]  // fall back

    if pattern[j] = pattern[i]:
      j ← j + 1

    lps[i] ← j

  return lps
```

**Matching Algorithm:**

```
Algorithm KMPSearch(text, pattern):
  n ← length(text)
  m ← length(pattern)
  lps ← ComputeLPS(pattern)

  i ← 0  // index in text
  j ← 0  // index in pattern

  while i < n:
    if pattern[j] = text[i]:
      i ← i + 1
      j ← j + 1

    if j = m:
      return i - m  // match found
    elif i < n AND pattern[j] ≠ text[i]:
      if j ≠ 0:
        j ← lps[j - 1]
      else:
        i ← i + 1

  return -1  // no match
```

**Complexity Analysis:**
- **Time:** O(n + m)
- **Space:** O(m) for LPS array
- **Preprocessing:** O(m)

### Rabin-Karp Algorithm (Rolling Hash)

**Intuition:** Use hashing for quick approximate matching, then verify with full comparison.

**Core Insight: Rolling Hash Update**

```
Instead of recomputing hash at each position:
old_hash = value(text[0..m-1])
new_hash = (old_hash - text[0] × p^(m-1)) × p + text[m]

Where p is prime base, eliminates rehashing entire window
```

**Algorithm:**

```
Algorithm RabinKarp(text, pattern):
  n ← length(text)
  m ← length(pattern)
  q ← large_prime  // for modulo
  p ← 256          // alphabet size
  h ← p^(m-1) mod q

  pattern_hash ← 0
  text_hash ← 0

  // Compute hashes for pattern and first window
  for i ← 0 to m - 1:
    pattern_hash ← (pattern_hash × p + pattern[i]) mod q
    text_hash ← (text_hash × p + text[i]) mod q

  // Check first window and slide
  for i ← 0 to n - m:
    if pattern_hash = text_hash:
      // Verify full string (in case of hash collision)
      if text[i..i+m-1] = pattern:
        return i  // match found

    if i < n - m:
      // Rolling hash update
      text_hash ← (p × (text_hash - text[i] × h) + text[i+m]) mod q
      if text_hash < 0:
        text_hash ← text_hash + q

  return -1  // no match
```

**Complexity Analysis:**
- **Best/Average Case:** O(n + m)
- **Worst Case:** O(n · m) - when all hashes match but strings don't
- **Space:** O(1)

**Advantages:**
- Excellent for multiple pattern search (one pass for all patterns)
- Used in plagiarism detection and bioinformatics
- Simple to implement

### Aho-Corasick Algorithm (Multi-Pattern Matching)

**Problem:** Find all occurrences of multiple patterns in a single text efficiently.

**Solution:** Build a state machine (automaton) to match all patterns simultaneously.

**Core Structure:**

```
1. Dictionary: Trie of all patterns
2. Failure Links: Enable transitions after partial matches
3. Output Links: Identify pattern matches at each state
```

**Algorithm Phases:**

```
Phase 1: Build Trie
- Insert each pattern into trie
- O(Σ length_i) where Σ length_i is total pattern length

Phase 2: Compute Failure Links (via BFS)
- For each state, find longest proper suffix that's a prefix
- Enables jumping to next possible match
- O(total_pattern_length + alphabet_size)

Phase 3: Set Output Links
- Record which patterns end at each state
- O(number_of_patterns)

Phase 4: Search Text
- Single pass through text
- O(text_length + number_of_matches)
```

**Complexity Analysis:**
- **Preprocessing:** O(m) where m is total pattern length
- **Searching:** O(n + z) where n is text length, z is match count
- **Space:** O(m × σ) where σ is alphabet size
- **Overall:** Linear in input, highly efficient for many patterns

**Applications:**
- Intrusion detection systems (Snort)
- Anti-virus engines
- Spam filtering
- Content filtering
- DNA sequence matching

---

## Boolean Search Models

### AND, OR, NOT Operations on Posting Lists

Boolean search enables precise control over document retrieval using logical operators.

### Basic Operations

**AND Operation (Intersection):**

```
Query: "machine" AND "learning"
Result: Documents containing BOTH terms

Posting List Intersection:
List1 (machine): [1, 3, 5, 7, 12]
List2 (learning): [2, 3, 7, 11]
Result: [3, 7]

Algorithm (two pointers):
i ← 0, j ← 0
result ← []
while i < len(List1) AND j < len(List2):
  if List1[i] = List2[j]:
    result.append(List1[i])
    i += 1, j += 1
  elif List1[i] < List2[j]:
    i += 1
  else:
    j += 1

Time: O(n + m) where n, m are list lengths
```

**OR Operation (Union):**

```
Query: "data" OR "analysis"
Result: Documents containing EITHER term

Posting List Union:
List1 (data): [1, 3, 5, 9]
List2 (analysis): [2, 3, 6, 9]
Result: [1, 2, 3, 5, 6, 9]

Algorithm:
Merge two sorted lists, keeping unique values
Time: O(n + m)
```

**NOT Operation (Complement):**

```
Query: "data" NOT "warehouse"
Result: All documents containing "data" EXCEPT those with "warehouse"

Algorithm:
1. Get posting list for "data"
2. Remove any docIDs that appear in "warehouse" list
3. Return remaining documents

Time: O(n + m)
```

### Query Optimization

**1. Short-Circuit Evaluation:**

```
Query: "A AND B AND C"

Optimization Strategy:
1. Estimate cost of each term (posting list length)
2. Sort by increasing posting list length: B, A, C
3. Evaluate: (B AND A) first (smaller), then AND C

Result: B ∩ A ∩ C computed efficiently
Benefit: Early termination if intermediate result empty
```

**2. Parenthesization:**

```
Query: "(accounting OR sales) AND analyst"

Without optimization:
1. Union of (accounting) and (sales) lists
2. Intersect with (analyst)
3. Faster (fewer documents in second step)

Bad query: "accounting OR (sales AND analyst)"
Would need to union potentially large lists
```

**3. Conjunctive Normal Form (CNF):**

```
Goal: Minimize expensive operations (unions)

Convert to CNF where possible:
"(A OR B) AND (C OR D)" is already efficient

Avoid: "A OR (B AND C AND D)"
Better: "(A AND B AND C AND D) OR (A AND C AND D)"
```

### Extended Boolean Model (Ranking)

Standard boolean returns binary results. Extended model adds ranking.

**Fuzzy Set Interpretation:**

```
Standard: relevance(doc, term) ∈ {0, 1}
Extended: relevance(doc, term) ∈ [0, 1]

Combined with Boolean:
relevance(doc, A AND B) = 0.5 × relevance(A) + 0.5 × relevance(B)
                          (weighted conjunction)

relevance(doc, A OR B) = max(relevance(A), relevance(B))
                         (disjunction)

relevance(doc, NOT A) = 1 - relevance(A)
                        (negation)
```

**Practical Implementation:**

```
Score(doc, "machine AND learning") =
  BM25(doc, "machine") × BM25(doc, "learning")

Score(doc, "data OR science") =
  max(BM25(doc, "data"), BM25(doc, "science"))
```

---

## Probabilistic Models

### Binary Independence Model (BIM)

The foundational model underlying BM25.

**Core Principle:**

```
Rank documents by probability of relevance:
P(R | d, q) ∝ P(d | R, q) / P(d | ¬R, q)

Where:
  R = relevance
  d = document
  q = query
```

**Independence Assumption:**

```
Terms are independent:
P(d | R) = ∏ P(tᵢ | R)
P(d | ¬R) = ∏ P(tᵢ | ¬R)

Simplification: Each term contributes independently
(Known to be violated in practice but works well empirically)
```

**Document Representation:**

```
Binary vector where each element = 1 if term present, 0 otherwise
d = (x₁, x₂, ..., xₘ) where xᵢ ∈ {0, 1}

Example:
Document: "machine learning algorithms"
d = (1, 0, 1, 1, 0, ...) for terms (machine, data, learning, algorithms, ...)
```

**Relevance Score (RSV):**

```
RSV(d) = Σ log[P(tᵢ | R) × (1 - P(tᵢ | ¬R))] /
              [P(tᵢ | ¬R) × (1 - P(tᵢ | R))]

Simplified (equivalent):
RSV(d) = Σ log[(r(tᵢ) × (N - n(tᵢ) - R + r(tᵢ)))] /
              [(n(tᵢ) - r(tᵢ)) × (R - r(tᵢ))]

Where:
  r(tᵢ) = number of relevant documents with tᵢ
  n(tᵢ) = total documents with tᵢ
  R = total relevant documents
  N = total documents
```

### Language Models for IR

**Principle:** A document is relevant if it would likely generate the query.

**Process:**

```
1. Estimate language model for each document
   P(word | document)

2. Rank documents by probability of generating query
   P(query | document) = ∏ P(qᵢ | document)

3. Score = log P(query | document)
         = Σ log P(qᵢ | document)
```

**Smoothing (Critical):**

Without smoothing, zero probabilities for unseen terms. Solutions:

```
Laplace Smoothing:
P(w | d) = (count(w, d) + 1) / (total_words_d + V)
where V = vocabulary size

Jelinek-Mercer:
P(w | d) = λ × P_ML(w | d) + (1 - λ) × P_collection(w)

Dirichlet Smoothing:
P(w | d) = (count(w, d) + μ × P_collection(w)) / (total_words + μ)
μ ≈ 2000 (empirically tuned)
```

**Advantages over Binary Independence Model:**
- Naturally incorporates term frequency
- Probabilistically grounded
- Performs well empirically
- Extension to pseudo-relevance feedback straightforward

### Divergence from Randomness (DFR)

**Core Concept:**

```
"The more a term's frequency diverges from randomness,
 the more informative it is for distinguishing documents."

Term Weight = -log(Probability of observing frequency under randomness)
```

**Mathematical Framework:**

```
DFR Score = Σ -log(P_randomness(term_frequency))

Where P_randomness is derived from:
- Binomial distribution (simple case)
- Bose-Einstein statistics (more sophisticated)
- Poisson distribution (intermediate)
```

**Common DFR Models (Terrier implementations):**

```
1. Bo1 (Bose-Einstein 1):
   Uses Bose-Einstein statistics
   Excellent for ad-hoc retrieval

2. Bo2 (Bose-Einstein 2):
   Alternative parameterization
   Slight variations in performance

3. KL (Kullback-Leibler):
   Uses KL divergence from random model
   Theoretically sound
```

**Performance Characteristics:**

```
Typical Ranking: DFR > BM25 > TF-IDF (varies by collection)
Short Queries: DFR significantly better than BM25
Long Documents: BM25 and DFR similar
Robustness: DFR very robust across different collections
```

---

## Advanced Data Structures

### Suffix Trees

**Definition:** Compressed trie containing all suffixes of a string.

**Structure:**

```
For text "banana$":
Suffixes:
  banana$
  anana$
  nana$
  ana$
  na$
  a$
  $

Compressed trie (suffix tree) groups edge labels
Edge from root for "ban" → points to multiple suffixes
```

**Operations:**

```
Pattern Search: O(m) where m = pattern length
- Traverse tree following edges
- If path exists, all occurrences found

Longest Common Substring:
- Find deepest node with children from both strings
- O(n + m)

Repeated Substring Finding:
- Find nodes representing multiple suffixes
- O(n)
```

**Complexity:**

```
Space: O(n) - linear in string length (compressed)
Build: O(n) - using Ukkonen's algorithm
Substring Search: O(m + occ) - m pattern, occ = occurrences
```

**Advantages:**
- Excellent for many pattern queries on same text
- Linear time pattern matching
- Enables many string algorithms

**Disadvantages:**
- Significant space overhead (despite compression)
- Complex to implement correctly
- Not practical for many applications

### Suffix Arrays

**Definition:** Sorted array of indices of all suffixes.

**Structure:**

```
Text: "banana"
Indices: 0 1 2 3 4 5

Suffixes:
0: banana
1: anana
2: nana
3: ana
4: na
5: a

Sorted by lexicographic order:
5: a
3: ana
1: anana
0: banana
4: na
2: nana

Suffix Array: [5, 3, 1, 0, 4, 2]
```

**Binary Search for Pattern:**

```
Algorithm SuffixArraySearch(text, suffix_array, pattern):
  low ← 0, high ← len(suffix_array) - 1

  while low ≤ high:
    mid ← (low + high) / 2
    suffix ← text[suffix_array[mid]:]

    if suffix.startswith(pattern):
      return suffix_array[mid]
    elif suffix < pattern:
      low ← mid + 1
    else:
      high ← mid - 1

  return -1

Time: O(m × log n) where m = pattern length, n = text length
Better: O(m + log n) with LCP array
```

**Advantages over Suffix Trees:**
- Simpler implementation
- Better space efficiency (O(n) vs O(n) with larger constant)
- Better cache locality for modern CPUs
- Easier to parallelize

**LCP Array (Longest Common Prefix):**

```
Combined with suffix array, enables O(m + log n) matching
LCP[i] = length of common prefix between
         suffix_array[i] and suffix_array[i-1]

Reduces need for character comparisons during binary search
```

---

## Decision Trees & Comparison

### Selecting the Right Algorithm

```
START: What is your primary use case?

├─ FULL-TEXT SEARCH (documents, web pages)
│  └─ Variable document length?
│     ├─ YES → BM25 (with appropriate k1, b tuning)
│     └─ NO (consistent length) → TF-IDF or BM25
│
├─ FUZZY/TYPO MATCHING (names, misspellings)
│  ├─ User-facing search?
│  │  └─ Levenshtein (threshold ≤ 2) or Jaro-Winkler
│  ├─ Client-side search?
│  │  └─ Bitap algorithm (Fuse.js)
│  ├─ Phonetic matching?
│  │  └─ Double Metaphone or Soundex
│  └─ Large scale?
│     └─ N-gram indexing (PostgreSQL trigram)
│
├─ EXACT PATTERN MATCHING (DNA, code, text)
│  ├─ Single pattern?
│  │  ├─ Long pattern (>50 chars)? → Boyer-Moore
│  │  ├─ Medium pattern → KMP
│  │  └─ Multiple passes → Rabin-Karp
│  └─ Multiple patterns? → Aho-Corasick
│
├─ BOOLEAN QUERIES (precise logical combinations)
│  ├─ Pure boolean? → Short-circuit evaluation on posting lists
│  ├─ Boolean + ranking? → Extended Boolean with BM25 scores
│  └─ Query optimization critical? → Convert to CNF, sort by list size
│
├─ ENTITY RESOLUTION (matching similar records)
│  ├─ Names → Jaro-Winkler + phonetic
│  ├─ Addresses → N-gram or TF-IDF
│  └─ Fuzzy joins → Edit distance with indexing
│
└─ MACHINE LEARNING FEATURES
   └─ TF-IDF vectorization (sklearn, gensim)
```

### Algorithm Comparison Matrix

| Algorithm | Best Case | Avg Case | Worst Case | Space | Use Case |
|-----------|-----------|----------|-----------|-------|----------|
| BM25 | O(k log n) | O(k log n) | O(k log n) | O(n) | General web search |
| TF-IDF | O(k log V) | O(k log V) | O(n) | O(V×D) | ML features |
| Levenshtein | O(mn) | O(mn) | O(mn) | O(mn) | Fuzzy matching |
| Jaro-Winkler | O(mn) | O(mn) | O(mn) | O(1) | Name matching |
| Boyer-Moore | O(n/m) | O(n) | O(nm) | O(m+σ) | Long patterns |
| KMP | O(n+m) | O(n+m) | O(n+m) | O(m) | Pattern matching |
| Rabin-Karp | O(n+m) | O(n+m) | O(nm) | O(1) | Multi-pattern |
| Aho-Corasick | O(n+z) | O(n+z) | O(n+z) | O(m×σ) | Multi-pattern |
| Bitap | O(n+m) | O(n+m) | O(nm) | O(m) | Fuzzy real-time |
| Trigram | O(n) | O(n) | O(n) | O(V×3) | Similarity |
| Suffix Array | O(m+log n) | O(m log n) | O(m log n) | O(n) | Substring search |

---

## Production Benchmarks

### Elasticsearch/Lucene BM25 Default Configuration

**Typical Parameters:**
```
k1 = 1.2 (term frequency saturation)
b = 0.75 (document length normalization)
boost = 1.0 (field weight)
```

**Performance Metrics (from Elastic benchmarks):**
```
Query Latency:
- Simple term query: 1-10 ms
- Boolean AND query: 5-50 ms
- Complex phrase + fuzzy: 50-500 ms

Throughput:
- Single shard: 5,000-50,000 queries/sec
- Cluster (10 nodes): 50,000-500,000 queries/sec
- Factors: Document size, query complexity, hardware
```

**Index Size Estimates:**
```
Original Text:  100 GB
Inverted Index: 15-30 GB (15-30% of source)
With Compression: 5-10 GB (5-10% of source)
Factors: Tokenization, language, duplicate terms
```

### TF-IDF Performance (scikit-learn)

**Vectorization Speed:**
```
1M documents, 10K vocabulary:
- Sparse matrix creation: 2-5 seconds
- Fit transform: 3-8 seconds
- Query transformation: 1-50 ms

Memory Usage:
- Sparse matrix: 5-15 GB (much less than dense)
- Dense matrix: 80 GB (10K × 1M × 8 bytes float)
```

### Fuzzy Matching Benchmarks

**Levenshtein Distance:**
```
Two 20-character strings:
- Python: 0.5-1.0 ms
- Cython optimized: 0.01-0.05 ms
- SIMD optimized: 0.001-0.01 ms

Threshold-based pruning:
- With early termination: 5-10x faster
- With n-gram index pre-filter: 100-1000x faster
```

**Jaro-Winkler (name matching):**
```
100K records vs 100K records:
- Naive: 10 seconds
- With blocking (same first letter): 0.5 seconds
- With blocking + parallel: 0.1 seconds
```

**PostgreSQL pg_trgm:**
```
1M text records, trigram index (GIN):
- LIKE query: 5-10 seconds (no index)
- LIKE query: 100-500 ms (with trigram index)
- Similarity search: 100x faster with index
```

### String Matching Benchmarks

**Boyer-Moore (1MB text, 100-byte pattern):**
```
English text: 2-5 ms
Binary data: 0.5-1 ms (more mismatches, more jumps)
Worst case (aaaa...aab pattern): 50-200 ms
```

**KMP (same setup):**
```
English text: 5-10 ms
Binary data: 5-8 ms
Worst case: 8-10 ms (consistent)
```

**Rabin-Karp (5-pattern matching, 1MB text):**
```
Single pattern: 8-12 ms (slightly slower than Boyer-Moore)
Five patterns (parallel): 10-15 ms (much better than repeated Boyer-Moore)
Multi-pattern case: Rabin-Karp wins (cost = 1.5x × single pattern)
```

**Aho-Corasick (1000 patterns, 1MB text):**
```
Naive approach (1000 × Rabin-Karp): 15 seconds
Aho-Corasick: 10-20 ms
Speedup: 750-1500x
```

### Real-World Search System Benchmarks

**E-commerce Product Search (Elasticsearch):**
```
Dataset: 100M products, 2 GB average per product
Query: "red running shoes under $100"

Configuration: 10-node cluster
- 40 primary shards, 1 replica per shard
- k1=1.2, b=0.75

Results:
- p50 latency: 15 ms
- p95 latency: 50 ms
- p99 latency: 150 ms
- Throughput: 100K queries/sec
- Index size: 500 GB
```

**Enterprise Full-Text Search (Lucene):**
```
Dataset: 1B documents, 10KB average size
Running on: 20-node cluster

Query Distribution:
- Simple term: 40% (5 ms avg)
- Boolean: 35% (20 ms avg)
- Phrase: 20% (50 ms avg)
- Faceted: 5% (200 ms avg)

Overall p95: 75 ms
Throughput: 500K queries/sec
```

**Fuzzy Matching at Scale (Elasticsearch):**
```
Product name matching: 10M products × 1K incoming names

Approach 1: Edit distance per product
- Time: 10-20 minutes (brute force)
- Accuracy: 95%

Approach 2: N-gram index + BM25 + verify
- Time: 2-5 minutes
- Accuracy: 98%

Approach 3: Phonetic + BM25 + Jaro-Winkler
- Time: 1-2 minutes
- Accuracy: 97%
```

---

## Implementation Pseudocode Templates

### Generic Inverted Index Construction

```
Algorithm BuildIndex(documents):
  index = {}  // term → posting_list
  doc_lengths = {}

  for doc_id, document in enumerate(documents):
    tokens = Tokenize(document)
    doc_lengths[doc_id] = len(tokens)

    for token in unique(tokens):
      if token not in index:
        index[token] = []

      term_frequency = Count(token in tokens)
      positions = FindPositions(token in tokens)

      posting = {
        doc_id: doc_id,
        tf: term_frequency,
        positions: positions
      }

      index[token].append(posting)

  // Sort posting lists by doc_id
  for term in index:
    index[term].sort(key=lambda p: p.doc_id)

  // Apply compression
  for term in index:
    index[term] = Compress(index[term])

  return index, doc_lengths

Complexity: O(N × M × log(M))
```

### BM25 Scoring Function

```
Function ComputeBM25(query, doc, index, doc_lengths, params):
  k1 = params.k1  // typically 1.2
  b = params.b    // typically 0.75

  score = 0.0
  avg_len = ComputeAverageDocLength(doc_lengths)
  doc_len = doc_lengths[doc.id]

  for term in query:
    if term not in index:
      continue

    tf = GetTermFrequency(term, doc)
    df = GetDocumentFrequency(term, index)
    N = TotalDocuments()

    // Compute IDF
    idf = log((N - df + 0.5) / (df + 0.5))

    // Compute normalized TF component
    norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_len)))

    score += idf * norm_tf

  return score
```

### Boolean Query Intersection

```
Function IntersectPostingLists(lists):
  if len(lists) == 0:
    return []

  // Start with smallest list (optimization)
  lists.sort(key=lambda l: len(l))
  result = lists[0]

  for i in range(1, len(lists)):
    result = Intersect(result, lists[i])
    if len(result) == 0:
      return []  // early termination

  return result

Function Intersect(list1, list2):
  result = []
  i, j = 0, 0

  while i < len(list1) and j < len(list2):
    if list1[i].doc_id == list2[j].doc_id:
      result.append(list1[i].doc_id)
      i += 1
      j += 1
    elif list1[i].doc_id < list2[j].doc_id:
      i += 1
    else:
      j += 1

  return result

Complexity: O(n + m) where n, m are list lengths
```

---

## Tuning Parameters by Scenario

### Small E-commerce Catalog (< 1M products)

```
Recommended: BM25 with defaults
k1 = 1.2
b = 0.75

Reasoning:
- Standard parameters work well
- Collection size manageable
- Keyword-driven search (product names)
- Term frequency variance moderate
```

### Large Product Dataset (1B+ items)

```
Recommended: BM25 with tuning
k1 = 2.0    (increase TF impact)
b = 0.5     (reduce length normalization)

Reasoning:
- Product descriptions vary significantly in length
- Longer descriptions contain genuine relevance signal
- Higher k1 rewards multiple term occurrences
- Large collection requires robustness
```

### News/Content Search

```
Recommended: BM25 with moderate tuning
k1 = 1.5
b = 0.75

Reasoning:
- Articles have natural length variation
- Longer articles ≠ more relevant
- Standard length normalization appropriate
- Moderate k1 balances multiple signals
```

### Scientific/Academic Search

```
Recommended: BM25 with field-specific weighting
k1 = 1.8
b = 0.6 (body), b = 0.2 (title, abstract)

Reasoning:
- Abstract/title crucial for relevance
- Body text can be boilerplate
- Term frequency meaningful (repeated methods, results)
- Field-specific normalization critical
```

### Search-as-You-Type (Autocomplete)

```
Recommended: N-gram or prefix matching
TF-IDF lightweight scoring

Reasoning:
- Real-time constraint (< 100ms required)
- Short queries (2-5 words)
- Prefix matching more important than relevance
- BM25 overhead unnecessary
```

---

## References & Further Reading

- [Practical BM25 - Part 2: The BM25 Algorithm - Elastic Blog](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
- [Practical BM25 - Part 3: Tuning k1 and b - Elastic Blog](https://www.elastic.co/blog/practical-bm25-part-3-considerations-for-picking-b-and-k1-in-elasticsearch)
- [Okapi BM25 - Wikipedia](https://en.wikipedia.org/wiki/Okapi_BM25)
- [TF-IDF - Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Inverted Index - Wikipedia](https://en.wikipedia.org/wiki/Inverted_index)
- [Levenshtein Distance - Wikipedia](https://en.wikipedia.org/wiki/Levenshtein_distance)
- [Jaro-Winkler Distance - Wikipedia](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance)
- [Damerau-Levenshtein Distance - Wikipedia](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)
- [Bitap Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Bitap_algorithm)
- [Rabin-Karp Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm)
- [Knuth-Morris-Pratt Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
- [Boyer-Moore Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-searching_algorithm)
- [Aho-Corasick Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [Suffix Array - Wikipedia](https://en.wikipedia.org/wiki/Suffix_array)
- [Language Models for IR - Stanford NLP](https://nlp.stanford.edu/IR-book/html/htmledition/language-models-for-information-retrieval-1.html)
- [Binary Independence Model - Wikipedia](https://en.wikipedia.org/wiki/Binary_Independence_Model)
- [Divergence from Randomness - Wikipedia](https://en.wikipedia.org/wiki/Divergence-from-randomness_model)
- [Trigram Search - Wikipedia](https://en.wikipedia.org/wiki/Trigram_search)
- [PostgreSQL pg_trgm Documentation](https://www.postgresql.org/docs/current/pgtrgm.html)
- [Soundex Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Soundex)
- [Phonetic Algorithm - Wikipedia](https://en.wikipedia.org/wiki/Phonetic_algorithm)
- [Fuse.js - Fuzzy Search Library](https://www.fusejs.io/)

---

## Conclusion

Classical search algorithms form the foundation of information retrieval systems. While modern approaches incorporate machine learning and neural networks, these algorithms remain essential for:

1. **Production systems** - BM25 and inverted indexes power billions of searches daily
2. **Hybrid approaches** - Combining classical ranking with neural embeddings
3. **Edge computing** - Lightweight algorithms for client-side search
4. **Specialized domains** - Domain-specific tuning of classical algorithms

The choice of algorithm depends critically on:
- **Data characteristics** (document length, vocabulary size, language)
- **Query types** (simple keywords, boolean, phrases, fuzzy)
- **Performance constraints** (latency, throughput, memory)
- **Accuracy requirements** (precision vs recall tradeoff)

Mastering these algorithms enables building robust, efficient search systems across diverse applications.
