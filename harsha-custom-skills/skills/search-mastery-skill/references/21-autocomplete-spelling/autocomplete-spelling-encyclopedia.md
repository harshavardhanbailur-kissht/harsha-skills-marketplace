# Comprehensive Reference: Autocomplete, Typeahead, and Spelling Correction Algorithms

**Last Updated:** March 2026
**Scope:** Production-grade systems, data structures, algorithms, and implementation patterns

---

## Table of Contents

1. [Trie Data Structure Fundamentals](#1-trie-data-structure-fundamentals)
2. [Advanced Trie Variants](#2-advanced-trie-variants)
3. [Autocomplete Ranking Algorithms](#3-autocomplete-ranking-algorithms)
4. [Spelling Correction Approaches](#4-spelling-correction-approaches)
5. [Production Autocomplete Systems](#5-production-autocomplete-systems)
6. [Query Suggestion and "Did You Mean"](#6-query-suggestion-and-did-you-mean)
7. [Search-as-You-Type Implementation](#7-search-as-you-type-implementation)
8. [Performance Optimization](#8-performance-optimization)
9. [Implementation Patterns](#9-implementation-patterns)
10. [Decision Tree: Choosing the Right Approach](#10-decision-tree-choosing-the-right-approach)

---

## 1. Trie Data Structure Fundamentals

### Overview

A trie, also known as a prefix tree or digital tree, is a specialized tree data structure used to store and retrieve strings from a dictionary or set. It's uniquely suited for autocomplete and spell-checking because it natively supports prefix-based searches.

**Key Characteristics:**
- Each node represents a character
- Paths from root to leaf spell out complete strings
- Inherently supports prefix searches without hash collisions
- O(p + k) time complexity for prefix search, where p = prefix length, k = matching results

### Why Tries for Autocomplete

Unlike hash tables that cannot answer prefix queries efficiently (requiring O(n) time to examine every key), tries enable:

- **Fast Prefix Matching:** Find all words starting with "auto" in O(4 + n) time
- **No Hash Collisions:** Predictable performance regardless of input data
- **Natural Lexicographic Order:** Results naturally sorted alphabetically
- **Memory Locality:** Related strings share common prefixes

### Basic Trie Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.weight = 0  # for ranking

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, weight=1):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.weight = weight

    def search_prefix(self, prefix):
        """Return all words starting with prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []
        self._dfs(node, prefix, results)
        return sorted(results, key=lambda x: -x[1])  # Sort by weight

    def _dfs(self, node, current, results):
        if node.is_word:
            results.append((current, node.weight))

        for char, child in node.children.items():
            self._dfs(child, current + char, results)
```

### Space Complexity Issues

Standard tries create one node per character, leading to high memory overhead:

- English alphabet: ~26 children per node
- Many nodes have single children (forming long chains)
- Typical overhead: 1 byte per character stored + pointers

For a 1M word English dictionary:
- Words: ~5.5MB
- Trie structure: 50-100MB

---

## 2. Advanced Trie Variants

### 2.1 Radix Trees (Patricia Tries)

**What is it:** A compressed trie that merges nodes with single children into their parents.

**How it works:**
- Instead of storing single characters, edges store entire strings/substrings
- Eliminates chains of single-child nodes
- Preserves O(p) search complexity but reduces memory significantly

**Example:**
```
Standard Trie:
root -> h -> e -> l -> l -> o [is_word]

Radix Tree:
root -> "hel" -> "lo" [is_word]
```

**Space Efficiency:**
- Reduces nodes from O(total characters) to O(number of strings)
- Particularly efficient for strings sharing long common prefixes
- Better for small datasets with long strings

**Implementation Concept:**
```python
class RadixNode:
    def __init__(self):
        self.edge_label = ""  # Substring instead of char
        self.children = {}
        self.is_word = False
        self.weight = 0
```

**When to Use:**
- Small datasets (thousands, not millions)
- Long strings with common prefixes
- Memory-constrained environments
- Reference implementations: [GitHub - PruningRadixTrie](https://github.com/wolfgarbe/PruningRadixTrie)

### 2.2 Ternary Search Trees (TSTs)

**What is it:** A hybrid between binary search trees and tries, using a tree-within-tree structure.

**How it works:**
- Each node has up to 3 children: left (smaller char), middle (matching char), right (larger char)
- Represents a trie node as a balanced tree instead of an array
- Effectively trades time for space

**Space Optimization:**
- Reduces per-node overhead from ~26 pointers to 3 pointers
- Can store entire English dictionary at ~3 words per node
- Trade-off: O(log n) binary search per character during traversal

**Memory Comparison:**
```
Standard Trie:    100MB for 1M words
Radix Tree:       20-30MB for 1M words
TST:              15-25MB for 1M words (more space-efficient)
```

**Autocomplete with TSTs:**
```python
class TST:
    def autocomplete(self, prefix, limit=10):
        """Returns top 'limit' suggestions for prefix"""
        node = self._find_prefix_node(prefix)
        if not node:
            return []

        suggestions = []
        self._collect_sorted(node, prefix, suggestions, limit)
        return suggestions

    def _collect_sorted(self, node, path, results, limit):
        if len(results) >= limit:
            return
        # BST traversal + prefix collection
        self._traverse_left(node.left, path, results, limit)
        if node.is_word:
            results.append((path, node.weight))
        if len(results) < limit:
            self._traverse_middle(node.middle, path + node.char, results, limit)
        if len(results) < limit:
            self._traverse_right(node.right, path, results, limit)
```

**Use Cases:**
- Near-neighbor searches (spelling correction)
- Spell checking with distance constraints
- Auto-complete with space constraints
- Resource-limited environments (mobile, embedded systems)

Reference: [Efficient Auto-complete with TSTs](https://igoro.com/archive/efficient-auto-complete-with-a-ternary-search-tree/)

### 2.3 BK-Trees for Fuzzy Matching

**What is it:** A metric tree in discrete metric spaces, optimized for similarity searches.

**How it works:**
- Organizes strings as a tree based on distance metric (Levenshtein)
- Edge labels store exact distance between parent and child
- Uses triangle inequality to prune search space

**Triangle Inequality Pruning:**
```
For any three points A, B, C:
distance(A, C) ≤ distance(A, B) + distance(B, C)

If distance(A, B) = 5 and we search with radius 2:
- If child C has distance 8 from B
- distance(A, C) could be at least |5 - 8| = 3
- Since 3 > 2, entire subtree under C can be pruned
```

**SymSpell vs BK-Tree Comparison:**
```
BK-Tree:
- Slower: ~100-1000x for simple edits
- Better for large edit distances
- Flexible with different metrics

SymSpell (next section):
- 100-1000x faster for edit distance ≤ 3
- Optimized specifically for spelling
- Pre-computes all deletes
```

**Use Cases:**
- Approximate string matching in dictionaries
- Spell correction with fuzzy prefixes
- Finding similar product names/categories
- Entity matching and deduplication

Reference: [BK-Tree Wikipedia](https://en.wikipedia.org/wiki/BK-tree)

---

## 3. Autocomplete Ranking Algorithms

### 3.1 Basic Popularity Ranking

**The Simplest Approach:**

Store a frequency count with each word:

```python
class PopularityTrie:
    def search_with_ranking(self, prefix, limit=10):
        """Return top 'limit' suggestions by popularity"""
        candidates = self.get_all_prefix_matches(prefix)

        # Sort by frequency (weight)
        ranked = sorted(candidates, key=lambda x: -x['frequency'])
        return ranked[:limit]

# Usage
trie = PopularityTrie()
trie.insert('apple', frequency=1000000)
trie.insert('application', frequency=500000)
trie.insert('apply', frequency=250000)

suggestions = trie.search_with_ranking('app', limit=3)
# Returns: [('apple', 1000000), ('application', 500000), ('apply', 250000)]
```

**Data Collection:**
- Track query frequency across all users
- Periodic updates from logs (batch processing)
- More stable but less responsive to trends

### 3.2 Multi-Signal Ranking

**What it is:** Weighted combination of multiple relevance signals.

**Common Signals:**

1. **Popularity (Global):** Total searches for a query
   - Weight: 0.4 (40%)
   - Source: Aggregated logs across all users
   - Update frequency: Daily/Weekly

2. **Recency (Freshness):** How recently a query was searched
   - Weight: 0.3 (30%)
   - Formula: Exponential decay or moving average
   - Update frequency: Real-time

3. **Personalization:** User's historical searches
   - Weight: 0.2 (20%)
   - Based on user's search history
   - Update frequency: Real-time

4. **Location:** Geographic relevance
   - Weight: 0.05 (5%)
   - For queries like "restaurants", "weather"
   - Update frequency: Real-time

5. **Language/Locale:** Language matching
   - Weight: 0.05 (5%)
   - Language-specific dictionaries

**Ranking Formula:**

```
score = (0.4 * popularity_score +
         0.3 * recency_score +
         0.2 * personalization_score +
         0.05 * location_score +
         0.05 * language_score)

where each component is normalized to [0, 1]
```

**Implementation Example:**

```python
class MultiSignalRanker:
    def calculate_score(self, query, user_context):
        # Popularity: 0-1000 searches, normalize to 0-1
        popularity = min(query.frequency / 1000, 1.0)

        # Recency: exponential decay over days
        days_old = (datetime.now() - query.last_search_date).days
        recency = math.exp(-0.1 * days_old)  # Half-life of 7 days

        # Personalization: user has searched this before?
        in_user_history = 1.0 if query.id in user_context['search_history'] else 0.0

        # Location: is user location relevant to query?
        location_match = 1.0 if self._is_location_relevant(query, user_context) else 0.0

        # Language match
        language_match = 1.0 if query.language == user_context['language'] else 0.5

        # Weighted sum
        score = (0.4 * popularity +
                 0.3 * recency +
                 0.2 * in_user_history +
                 0.05 * location_match +
                 0.05 * language_match)

        return score
```

**Real-World Complexity:**

Google reportedly uses 10+ signals:
- Click-through rates
- Dwell time (how long user stays on result)
- Click depth (result position that was clicked)
- Session patterns
- Query reformulation patterns
- Entity signals (person, place, thing)
- Semantic understanding
- Device type and context
- Search intent signals

### 3.3 Top-K Selection Efficiently

**The Problem:** With millions of suggestions, can't rank all candidates.

**Two-Phase Ranking:**

```python
class EfficientTopK:
    def get_top_k_suggestions(self, prefix, k=10):
        # Phase 1: Fast filtering with simple signals
        # Get candidates that START with prefix (trie traversal O(p + n))
        candidates = self.trie.get_prefix_matches(prefix)  # n results

        # Filter to top N by single signal (e.g., frequency only)
        # Sort complexity: O(n log k) instead of O(n log n)
        top_n = heapq.nlargest(k * 10, candidates,
                               key=lambda x: x['frequency'])

        # Phase 2: Complex ranking on smaller set
        # Apply multi-signal ranking to top_n only
        final_ranked = self.apply_complex_ranking(top_n)

        return final_ranked[:k]
```

**Time Complexity:**
- Phase 1: O(p + n) for trie traversal + O(n log k) for heap selection
- Phase 2: O(k * log k) for final ranking
- Total: O(p + n log k) instead of O(n log n)

**At Google Scale:**
- 100,000 queries per second
- Millions of unique prefixes
- Phase 1 filters to top 1000 candidates
- Phase 2 applies complex ML models to top 1000
- Returns top 10

---

## 4. Spelling Correction Approaches

### 4.1 Peter Norvig's Algorithm

**Historical Significance:** Foundational approach, published as influential blog post. Still used as baseline for learning.

**How It Works:**

```python
import re
from collections import Counter

class NorvigSpeller:
    def __init__(self, vocabulary_text):
        # Build vocabulary with word frequencies
        self.words = Counter(self.extract_words(vocabulary_text))

    def extract_words(self, text):
        return re.findall(r'\w+', text.lower())

    def spell_correct(self, word):
        """Return most probable spelling correction for word"""
        return max(self.candidates(word), key=self.word_probability)

    def candidates(self, word):
        """Generate spelling candidates within edit distance 2"""
        return (self.known([word]) or
                self.known(self.edits1(word)) or
                self.known(self.edits2(word)) or
                [word])

    def known(self, words):
        """Filter words that appear in vocabulary"""
        return set(w for w in words if w in self.words)

    def edits1(self, word):
        """All edits that are one edit away from word"""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        """All edits that are two edits away from word"""
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def word_probability(self, word):
        """Probability of word in vocabulary"""
        return self.words.get(word, 0) / sum(self.words.values())
```

**Computational Complexity:**

For a word of length n with alphabet size a:
- Edit distance 1: O(2n + an + a) = O(an) operations
- Edit distance 2: O((an)²) operations
- Example: 5-letter word = 2,187 edit distance 1 candidates, 4.7M edit distance 2 candidates

**Limitations:**

1. **Exponential Growth:** Average 5-letter word has ~3 million variants at distance 3
2. **Slow:** Dictionary lookup required for each variant
3. **Limited Distance:** Practical only for distance ≤ 2
4. **No Context:** Treats each word independently

**When to Use:**
- Educational purposes
- Small datasets (< 100K words)
- Real-time constraint not critical
- Simple spelling errors

Reference: [Peter Norvig's "How to Write a Spelling Corrector"](http://norvig.com/spell-correct.html)

### 4.2 Symmetric Delete (SymSpell) Algorithm

**Why SymSpell is Superior:**

Problem with Norvig's approach: Generate all variants of INPUT word, check against dictionary (millions of candidates).

SymSpell insight: Instead, generate all variants of DICTIONARY words at indexing time.

**The Symmetric Delete Principle:**

```
For a typo "speling" (missing 'l'):
- Norvig: Generate 3M edits of "speling", check each

SymSpell:
- Pre-index: For word "spelling", generate all edits
- Query: Generate only edits of "speling" (much fewer)
- Match: Find where edits intersect

Insight: If typo is within distance d from correct word,
then correct word is within distance d from typo.
But one of the deletes of either will be in common!
```

**Algorithm:**

```python
class SymSpell:
    def __init__(self):
        self.dictionary = {}  # word -> frequency
        self.deletes = {}     # delete -> [words with this delete]

    def build_dictionary(self, corpus_words):
        """Pre-processing phase: index all words and their deletes"""
        for word, frequency in corpus_words.items():
            self.add_to_dictionary(word, frequency)

    def add_to_dictionary(self, word, frequency, max_edit_distance=2):
        """Add word and all its deletes to index"""
        self.dictionary[word] = frequency

        # Generate all deletes up to max_edit_distance
        deletes = self.generate_deletes(word, max_edit_distance)
        for delete in deletes:
            if delete not in self.deletes:
                self.deletes[delete] = set()
            self.deletes[delete].add(word)

    def generate_deletes(self, word, max_dist):
        """Generate all strings with max_dist deletions"""
        deletes = set()
        candidates = [word]

        for i in range(max_dist):
            new_candidates = set()
            for candidate in candidates:
                for j in range(len(candidate)):
                    # Delete character at position j
                    delete = candidate[:j] + candidate[j+1:]
                    new_candidates.add(delete)
            deletes.update(new_candidates)
            candidates = new_candidates

        return deletes

    def spell_correct(self, typo, max_edit_distance=2):
        """Find spelling corrections for typo"""
        if typo in self.dictionary:
            return [(typo, self.dictionary[typo])]

        suggestions = set()

        # Generate deletes of typo
        typo_deletes = self.generate_deletes(typo, max_edit_distance)

        # For each delete, find dictionary words that produce same delete
        for delete in typo_deletes:
            if delete in self.deletes:
                for word in self.deletes[delete]:
                    if self.levenshtein_distance(typo, word) <= max_edit_distance:
                        suggestions.add((word, self.dictionary[word]))

        # Sort by frequency
        return sorted(suggestions, key=lambda x: -x[1])

    def levenshtein_distance(self, s1, s2):
        """Calculate actual edit distance"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
```

**Efficiency Comparison:**

```
For a 5-letter word:
Norvig:   ~3,000,000 candidates to check
SymSpell: ~25 deletes to check (120x faster)

For dictionary of 1M words:
Norvig:   Per-query: O(an²) where a=26, n=5 → 6,500 ops
SymSpell: Per-query: O(Σ deletes) → 50 ops
          Pre-index: O(sum of word lengths × max_dist) → computed once
```

**Real-World Numbers:**

- SymSpell: 1 million times faster than naive approach
- Spell checking: Sub-millisecond latency
- Handles edit distance 3-5 efficiently
- Supports compound words with special handling

**Key Optimizations:**

1. **Pre-computed Deletes:** All dictionary edits pre-computed at index time
2. **Early Termination:** Sort candidates by frequency, stop after finding good match
3. **Distance-aware Filtering:** Only check candidates within distance threshold
4. **Compound-aware:** Special handling for hyphenated/compound words

**Languages Supported:** Language-independent (works with any character set)

Reference: [SymSpell GitHub](https://github.com/wolfgarbe/SymSpell)

### 4.3 Noisy Channel Model & Probabilistic Approaches

**What is it:** Bayesian framework that models spelling errors as noise in communication channel.

**Conceptual Model:**

```
Correct Word (w) ─[Noisy Channel]─> Misspelled Word (t)

Goal: Find correct word w that maximizes P(w|t)

Using Bayes' theorem:
P(w|t) = P(t|w) × P(w) / P(t)
        ∝ P(t|w) × P(w)

Where:
- P(w)   = Language model (how common is word w?)
- P(t|w) = Error model (how likely is typo t given correct word w?)
```

**Components:**

1. **Language Model P(w):**
   - Probability of word based on corpus frequency
   - Unigram language model: word frequency
   - N-gram language model: word context dependency

   ```python
   class LanguageModel:
       def __init__(self, corpus_text):
           self.word_freq = Counter(corpus_text.lower().split())
           self.total = sum(self.word_freq.values())

       def probability(self, word):
           return self.word_freq.get(word, 0) / self.total
   ```

2. **Error Model P(t|w):**
   - Probability of error transformation (deletion, insertion, substitution, transposition)
   - Can be learned from a corpus of known errors

   ```python
   class ErrorModel:
       def __init__(self):
           self.error_freq = Counter()

       def learn_from_errors(self, correct_word, typo_word):
           """Learn error patterns from (correct, misspelled) pairs"""
           edits = self.get_edit_operations(correct_word, typo_word)
           self.error_freq.update(edits)

       def probability(self, correct_word, typo_word):
           """P(typo | correct_word)"""
           if self.levenshtein_distance(correct_word, typo_word) > 3:
               return 0.0  # Impossible error

           # Can model as inverse of edit distance
           # Or use learned probabilities from error corpus
           distance = self.levenshtein_distance(correct_word, typo_word)
           return math.exp(-distance)  # Exponential decay
   ```

3. **Spelling Correction Decision:**

   ```python
   class NoisyChannelCorrector:
       def correct(self, typo, num_suggestions=5):
           candidates = self.generate_candidates(typo)  # nearby words

           scores = {}
           for candidate in candidates:
               # P(candidate | typo) ∝ P(typo | candidate) × P(candidate)
               p_word = self.language_model.probability(candidate)
               p_error = self.error_model.probability(candidate, typo)
               score = p_error * p_word
               scores[candidate] = score

           # Return top-k by score
           return sorted(scores.items(), key=lambda x: -x[1])[:num_suggestions]
   ```

**Advanced: Hidden Markov Models**

Using HMMs for context-aware spelling correction:

```
Observed sequence (typos): [t1, t2, t3]
Hidden sequence (correct):  [w1, w2, w3]

HMM captures:
- P(ti | wi) = observation probability (local error model)
- P(wi | wi-1) = transition probability (language model)

Viterbi algorithm finds most likely sequence of correct words
```

**When to Use:**

- Context-dependent correction ("there" vs "their")
- Phrase-level corrections
- Statistical confidence in corrections
- Learning error patterns from user data

**Advantages:**

- Handles context
- Can learn from real error data
- Probabilistic confidence scores
- Sound theoretical foundation

**Disadvantages:**

- Requires error corpus to train
- More complex than edit distance
- Slower than SymSpell for single-word correction
- Needs language model training

Reference: [Stanford Speech and Language Processing - Noisy Channel Model](https://web.stanford.edu/~jurafsky/slp3/old_dec21/B.pdf)

---

## 5. Production Autocomplete Systems

### 5.1 Google's Autocomplete Architecture

**Scale and Performance:**

- 3 billion searches per day
- ~104,167 queries per second (100,000 QPS)
- Each autocomplete request must return results in < 100ms
- Supports multiple languages and regions

**Core Architecture:**

```
Client (Web/Mobile)
    ↓ HTTP Request + partial query
[API Gateway] ← Authentication, Rate Limiting, Routing
    ↓
[Load Balancer]
    ↓
[Autocomplete Service Fleet]
    ├─ [Trie Index] (Compressed, optimized for prefix search)
    ├─ [Cache Layer] (Popular queries, frequent prefixes)
    └─ [Ranking Service] (Multi-signal scoring)
    ↓
[Results Cache] ← Store results for popular queries
    ↓ HTTP Response
Client
```

**Multi-Signal Ranking at Google:**

The company reportedly uses 10+ signals beyond basic popularity:

1. **Query Frequency:** Global search volume for query
2. **Freshness/Recency:** Recent trend spike indicators
3. **User History:** User's personal search history
4. **Query Completeness:** Likelihood user will search full query
5. **Spelling Quality:** Is query misspelled?
6. **Entity Signals:** Is query a person/place/thing?
7. **Semantic Understanding:** Topic and intent
8. **Click-Through Rate:** How often users click results
9. **Dwell Time:** How long users stay on clicked results
10. **Device Type:** Desktop vs Mobile context
11. **Geographic Location:** Localization signals
12. **Search Context:** Same session context

**Ranking Algorithm (Conceptual):**

```
score = Σ weight_i × signal_i

Optimization via machine learning:
- Train model on historical search logs
- Signals: user context, query properties, result properties
- Label: user satisfaction (CTR, dwell time)
- Model: LambdaMART, neural networks
```

**Caching Strategy:**

```
3-tier cache hierarchy:

Tier 1: Result Cache
- Query prefix → ranked suggestions
- Most popular queries cached
- TTL: 1-24 hours depending on freshness signal
- Hit rate: ~80% of queries

Tier 2: Trie Node Cache
- Partial trie traversals cached
- When traversing "autom", cache result node
- Reduces repeated trie traversals
- Hit rate: ~90%

Tier 3: Reverse Index Cache
- For reverse trie (suffix matching)
- Enables mid-word search
- Smaller dataset, selective caching
```

**Infrastructure at Scale:**

```
Data:
- 1M+ frequent search queries indexed
- Query history: Last 30-90 days
- User profiles: Personalization signals
- Entity index: People, places, products

Serving Infrastructure:
- Hundreds of thousands of servers
- Multiple datacenters for geographic distribution
- Edge caching at CDN level
- Replication: 3x redundancy per region
```

**Optimization Techniques:**

1. **Delta Encoding:** Store differences between similar queries
2. **Bit Packing:** Compress frequency scores into fewer bits
3. **Bloom Filters:** Quick non-existence checks
4. **Prefix Pruning:** Trim unpromising branches in trie
5. **Lazy Loading:** Load full metadata on demand

Reference: [Google's Search Autocomplete High-Level Design](https://www.geeksforgeeks.org/system-design/googles-search-autocomplete-high-level-designhld/)

### 5.2 Elasticsearch Completion Suggester

**What is it:** Purpose-built autocomplete feature in Elasticsearch using Finite State Transducer (FST).

**Data Structure:**

```
FST (Finite State Transducer):
- Similar to trie but optimized for fast lookups
- Stored in-memory on Elasticsearch nodes
- Compresses paths more aggressively than tries
- Returns weighted results efficiently
```

**Index Mapping:**

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "suggest": {
        "type": "completion",
        "analyzer": "simple"
      }
    }
  }
}
```

**Indexing Example:**

```python
# Indexing documents with suggestions
documents = [
    {
        "title": "Apple Inc.",
        "suggest": {
            "input": ["apple", "apple inc", "apple computer"],
            "weight": 10  # Popularity weight
        }
    },
    {
        "title": "Application Software",
        "suggest": {
            "input": ["application", "app", "software"],
            "weight": 5
        }
    }
]

# Index documents
for doc in documents:
    es.index(index="products", id=doc['title'], body=doc)
```

**Query API:**

```python
# Get suggestions
query = {
    "suggest": {
        "my-suggestions": {
            "prefix": "app",
            "completion": {
                "field": "suggest",
                "size": 10,
                "skip_duplicates": True,
                "fuzzy": {
                    "fuzziness": "AUTO"  # For spelling correction
                }
            }
        }
    }
}

results = es.search(index="products", body=query)
# Returns: ["apple", "application", "app", ...]
```

**Advantages:**

- Very fast: in-memory FST lookup
- No duplicates: built-in deduplication
- Weighted results: supports popularity ranking
- Fuzzy support: optional fuzzy matching

**Limitations:**

- Not suitable for infix matching (mid-word search)
- Advanced filtering limited
- Complex range queries not supported
- Best for simple prefix matching

Reference: [Elasticsearch Completion Suggester](https://blog.mimacom.com/autocomplete-elasticsearch-part3/)

### 5.3 Redis Sorted Sets for Autocomplete

**Why Redis for Autocomplete:**

- Ultra-fast in-memory operations
- Atomic operations (no race conditions)
- Pub/Sub for real-time updates
- Persistence options for durability
- Cluster support for horizontal scaling

**Core Approach:**

```python
import redis

class RedisAutocomplete:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.prefix_key = "ac:"  # prefix for autocomplete keys

    def add_suggestion(self, suggestion, score, category="general"):
        """Add a suggestion with a score (popularity/frequency)"""
        key = f"{self.prefix_key}{category}"
        # ZADD: Z = sorted set, ADD = add member with score
        self.redis.zadd(key, {suggestion: score})

    def get_suggestions(self, prefix, category="general", limit=10):
        """Get suggestions starting with prefix, ordered by score"""
        key = f"{self.prefix_key}{category}"

        # Use lexicographic range with ZRANGEBYLEX
        # ZRANGEBYLEX: range by lexicographic order
        # Syntax: ZRANGEBYLEX key min max
        # Use [prefix to get strings starting with prefix
        min_lex = f"[{prefix}"
        max_lex = f"[{prefix}\xff"  # \xff = highest byte value

        # Get results by lexicographic order, limit to 'limit' results
        results = self.redis.zrangebylex(key, min_lex, max_lex, start=0, num=limit)

        # Get scores for each result (for ranking)
        scored_results = []
        for result in results:
            score = self.redis.zscore(key, result)
            scored_results.append((result, score))

        # Sort by score (descending)
        return sorted(scored_results, key=lambda x: -x[1])

    def increment_popularity(self, suggestion, category="general", increment=1):
        """Increment popularity score when user selects suggestion"""
        key = f"{self.prefix_key}{category}"
        self.redis.zincrby(key, increment, suggestion)
```

**Advanced: Prefix Caching**

```python
class RedisAutocompleteWithCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_prefix = "ac_cache:"
        self.ttl = 3600  # 1 hour cache

    def get_suggestions_cached(self, prefix, category="general", limit=10):
        """Get suggestions with caching"""

        # Check if cached
        cache_key = f"{self.cache_prefix}{category}:{prefix}:{limit}"
        cached = self.redis.get(cache_key)

        if cached:
            # Return from cache
            import json
            return json.loads(cached)

        # Compute suggestions (expensive operation)
        suggestions = self.get_suggestions(prefix, category, limit)

        # Cache results
        import json
        self.redis.setex(cache_key, self.ttl, json.dumps(suggestions))

        return suggestions
```

**Popularity Ranking Example:**

```python
class PopularityAutocomplete:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.search_log_key = "search_logs"

    def log_search(self, query):
        """Log a search query"""
        # Add to sorted set with score = current timestamp
        # (or use ZADD with INCR to just increment count)
        self.redis.zincrby(self.search_log_key, 1, query)

    def get_trending_queries(self, limit=10):
        """Get trending queries by search count"""
        # ZREVRANGE: reverse range (highest scores first)
        return self.redis.zrevrange(self.search_log_key, 0, limit-1, withscores=True)

    def record_click(self, query):
        """Record when user clicks suggestion"""
        click_key = f"clicks:{query}"
        self.redis.incr(click_key)

        # Also update sorted set for trending
        self.redis.zincrby("trending_queries", 1, query)
```

**Scalability Considerations:**

```
Memory efficiency:
- Store only top N queries per prefix
- Prune infrequent queries periodically
- 100k suggestions × 20 char average = ~2MB dictionary
- Sorted set overhead: ~20-30% additional memory

Replication for redundancy:
- Redis Sentinel: automatic failover
- Redis Cluster: sharding across multiple nodes
- Each shard contains range of prefixes

Update strategy:
- Real-time updates via ZINCRBY (atomic)
- Batch updates from logs (periodic)
- Hybrid: real-time for recent, batch for historical
```

Reference: [Building Smart Autocomplete with Redis Sorted Sets](https://upstash.com/blog/redis-autocomplete-popularity-ranking/)

---

## 6. Query Suggestion and "Did You Mean"

### 6.1 Understanding Query Suggestion Types

**Category 1: Query Correction ("Did You Mean?")**

When user's query has typo or is unusual:

```
User enters: "speling mistakes"
System suggests: "spelling mistakes" (typo correction)

User enters: "how do you spell encyclopedia?"
System suggests: "how to spell encyclopedia" (semantic normalization)
```

**Category 2: Query Completion/Refinement**

When user's query is too broad or vague:

```
User enters: "restaurants"
System suggests:
  - "restaurants near me"
  - "restaurants open now"
  - "restaurants with delivery"
  - "restaurants in [city]"
```

**Category 3: Related/Scoped Suggestions**

When system suggests alternative search directions:

```
User enters: "python"
System suggests:
  - "python programming"
  - "python snake"
  - "python vs java"
  - "python download"
  - "python tutorial"
```

### 6.2 "Did You Mean" Implementation

**Algorithm:**

```python
class DidYouMean:
    def __init__(self, spell_corrector, index):
        self.spell_corrector = spell_corrector  # SymSpell, etc.
        self.index = index  # Elasticsearch, etc.

    def suggest_correction(self, query):
        """
        Return corrected query if original returns too few results
        """
        # Step 1: Get results for original query
        original_results = self.index.search(query)

        if len(original_results) > 10:
            # Enough results, no correction needed
            return None

        # Step 2: Try to correct each word
        corrected_terms = []

        for word in query.split():
            # Is word spelled correctly?
            if self.spell_corrector.is_correct(word):
                corrected_terms.append(word)
            else:
                # Get best correction
                best_correction = self.spell_corrector.correct(word)
                corrected_terms.append(best_correction)

        corrected_query = " ".join(corrected_terms)

        # Step 3: Try search with corrected query
        corrected_results = self.index.search(corrected_query)

        if len(corrected_results) > len(original_results):
            # Corrected query is better, suggest it
            return {
                "original": query,
                "corrected": corrected_query,
                "confidence": self._calculate_confidence(query, corrected_query)
            }

        return None

    def _calculate_confidence(self, original, corrected):
        """Calculate confidence in correction"""
        # Based on Levenshtein distance and correction likelihood
        distance = self._edit_distance(original, corrected)

        if distance == 0:
            return 1.0  # Same query
        elif distance == 1:
            return 0.9  # Single character difference
        elif distance == 2:
            return 0.7  # Two character differences
        else:
            return 0.5  # More than two differences
```

**Contextual Implementation:**

```python
class ContextualDidYouMean:
    def suggest_with_context(self, query, user_context):
        """
        Use user context to improve suggestions

        context = {
            'location': 'San Francisco',
            'language': 'en',
            'previous_queries': ['pizza', 'restaurants'],
            'session_queries': [...]
        }
        """

        # Location-aware correction
        if 'near me' in query or 'local' in query:
            return self._location_aware_suggestion(query, user_context['location'])

        # Time-aware correction
        current_hour = datetime.now().hour
        if current_hour in [7, 8, 9]:  # Morning
            return self._morning_aware_suggestion(query)
        elif current_hour in [12, 13]:  # Lunch
            return self._lunch_aware_suggestion(query)
        elif current_hour in [18, 19, 20]:  # Dinner
            return self._dinner_aware_suggestion(query)

        # Session-context aware
        if len(user_context['session_queries']) > 0:
            return self._session_aware_suggestion(query, user_context['session_queries'])

        return self.suggest_correction(query)  # Default
```

### 6.3 Query Suggestion from Logs

**Log-Based Suggestions:**

```python
class LogBasedQuerySuggester:
    def __init__(self, query_logs_db):
        """
        query_logs_db contains:
        {
            'query': 'restaurants near me',
            'count': 10000,
            'click_rate': 0.45,
            'avg_dwell_time': 45,  # seconds
            'related_queries': [...]
        }
        """
        self.logs = query_logs_db

    def get_suggestions(self, prefix, num=10):
        """
        Suggest queries based on frequency and engagement
        """
        # Find queries starting with prefix
        matching = self.logs.find_prefix_matches(prefix)

        # Score based on multiple signals
        scored = []
        for query_record in matching:
            score = (
                0.5 * self._normalize_frequency(query_record['count']) +
                0.3 * query_record['click_rate'] +
                0.2 * self._normalize_dwell_time(query_record['avg_dwell_time'])
            )
            scored.append((query_record['query'], score))

        # Return top-k
        return sorted(scored, key=lambda x: -x[1])[:num]

    def _normalize_frequency(self, count):
        """Normalize count to 0-1 range"""
        max_count = self.logs.max_query_count()
        return min(count / max_count, 1.0)

    def _normalize_dwell_time(self, dwell_time):
        """Normalize dwell time to 0-1 range"""
        # More dwell time = higher engagement = better query
        return min(dwell_time / 300, 1.0)  # 5 minutes as max
```

**Related Queries:**

```python
class RelatedQuerySuggester:
    def __init__(self, query_graph):
        """
        query_graph: network of related queries
        edges weighted by co-occurrence frequency
        """
        self.graph = query_graph

    def find_related(self, query, depth=1, num=10):
        """
        Find related queries using graph traversal
        """
        related = set()
        visited = {query}
        queue = [(query, 0)]

        while queue:
            current, distance = queue.pop(0)

            if distance > depth:
                continue

            # Get neighbors (related queries)
            neighbors = self.graph.get_neighbors(current)

            for neighbor, weight in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.add((neighbor, weight))
                    queue.append((neighbor, distance + 1))

        # Sort by weight (co-occurrence frequency)
        return sorted(related, key=lambda x: -x[1])[:num]
```

Reference: [Elastic Blog - Scoped Search Suggestions](https://www.elastic.co/blog/how-to-build-scoped-search-suggestions-and-search-query-corrections)

---

## 7. Search-as-You-Type Implementation

### 7.1 Edge N-Grams and Tokenization

**What is it:** Breaking text into overlapping substrings starting at word beginning.

**How It Works:**

```
Word: "Elasticsearch"

Edge N-Grams (min=2, max=15):
- Length 2:  "El"
- Length 3:  "Ela"
- Length 4:  "Elas"
- Length 5:  "Elast"
- Length 6:  "Elastic"
- Length 7:  "Elastics"
- ...
- Length 13: "Elasticsearch"

Query "ela" matches "Ela", "Elas", "Elast", "Elastic", etc.
Query "las" does NOT match (infix, not edge)
```

**Elasticsearch Configuration:**

```json
{
  "settings": {
    "analysis": {
      "tokenizer": {
        "edge_ngram_tokenizer": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 20,
          "token_chars": ["letter", "digit"]
        }
      },
      "analyzer": {
        "edge_ngram_analyzer": {
          "type": "custom",
          "tokenizer": "edge_ngram_tokenizer",
          "filter": ["lowercase"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "product_name": {
        "type": "text",
        "analyzer": "edge_ngram_analyzer",
        "search_analyzer": "standard"  # Don't apply at query time
      }
    }
  }
}
```

**Why separate search_analyzer:**

During indexing, apply edge n-grams to generate all prefixes.
During query time, search as plain text (don't generate n-grams).

```
Index time:  "apple" → generates ["ap", "app", "appl", "apple"]
Query time:  search for "app" as literal string
Result:      matches "app", "appl", "apple"
```

### 7.2 Shingle Tokens for Phrase Matching

**What is it:** Grouping consecutive tokens into phrases.

**How It Works:**

```
Sentence: "Elasticsearch is awesome"
Tokens: ["elasticsearch", "is", "awesome"]

Shingles (size=2):
- "elasticsearch is"
- "is awesome"

Shingles (size=3):
- "elasticsearch is awesome"

Useful for:
- Phrase matching: "elastic search" (two words)
- Context-aware suggestions: "machine learning framework"
```

**Configuration:**

```json
{
  "settings": {
    "analysis": {
      "filter": {
        "two_shingles": {
          "type": "shingle",
          "min_shingle_size": 2,
          "max_shingle_size": 2,
          "output_unigrams": true
        }
      },
      "analyzer": {
        "shingle_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "two_shingles"]
        }
      }
    }
  }
}
```

**Example Output:**

```
Input:  "machine learning framework"
Tokens: ["machine", "learning", "framework"]
Output: ["machine", "learning", "framework", "machine learning", "learning framework"]
```

### 7.3 Search-as-You-Type Field Type

**Elasticsearch Optimization:**

Elasticsearch's `search_as_you_type` field type automatically creates subfields with appropriate analyzers:

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "search_as_you_type"
      }
    }
  }
}
```

**Automatically Creates:**

```
title              → Full text, standard analyzer
title._2gram       → Text with 2-shingles
title._3gram       → Text with 3-shingles
title._index_prefix → Edge n-grams + 3-shingles
```

**Multi-Field Query:**

```json
{
  "query": {
    "multi_match": {
      "query": "ela",
      "type": "bool_prefix",
      "fields": [
        "title",           // Exact prefix match
        "title._2gram",    // Bigram match
        "title._3gram",    // Trigram match
        "title._index_prefix^2"  // Boosted prefix match
      ]
    }
  }
}
```

**Performance:**

```
Latency with search_as_you_type:
- 1 character: ~10ms
- 2 characters: ~15ms
- 3 characters: ~20ms
- 10+ characters: ~30ms

Memory overhead: ~30-50% vs standard text field
(Extra subfields and n-gram tokens)
```

Reference: [Elasticsearch Autocomplete: Search as You Type](https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search)

---

## 8. Performance Optimization

### 8.1 Debounce and Throttle

**Why It Matters:**

Users typing "elasticsearch" generate 13 characters = 13 requests.
Without debouncing, autocomplete systems would be overloaded.

**Debounce (Client-Side):**

```javascript
class DebouncedAutocomplete {
    constructor(fetchSuggestions, delayMs = 300) {
        this.fetch = fetchSuggestions;
        this.delay = delayMs;
        this.timeout = null;
    }

    onChange(inputValue) {
        // Clear previous timeout
        if (this.timeout) {
            clearTimeout(this.timeout);
        }

        // Set new timeout - only fetch if user pauses typing
        this.timeout = setTimeout(() => {
            console.log(`Fetching suggestions for: ${inputValue}`);
            this.fetch(inputValue);
        }, this.delay);
    }
}

// Usage
const ac = new DebouncedAutocomplete(async (query) => {
    const response = await fetch(`/api/suggestions?q=${query}`);
    const suggestions = await response.json();
    updateUI(suggestions);
}, 300);

// In HTML
inputElement.addEventListener('input', (e) => {
    ac.onChange(e.target.value);
});
```

**Throttle (Client-Side):**

```javascript
class ThrottledAutocomplete {
    constructor(fetchSuggestions, intervalMs = 200) {
        this.fetch = fetchSuggestions;
        this.interval = intervalMs;
        this.lastFetch = 0;
        this.pending = null;
    }

    onChange(inputValue) {
        const now = Date.now();

        if (now - this.lastFetch >= this.interval) {
            // Enough time has passed, fetch immediately
            this.lastFetch = now;
            this.fetch(inputValue);
        } else {
            // Recent fetch, schedule for later
            this.pending = inputValue;
            setTimeout(() => {
                if (this.pending !== inputValue) return;
                this.lastFetch = Date.now();
                this.fetch(this.pending);
            }, this.interval - (now - this.lastFetch));
        }
    }
}
```

**Debounce vs Throttle:**

```
Debounce (300ms):
User types: e-l-a-s-t-i-c...
Events:     ↓ ↓ ↓ ↓ ↓ ↓ ↓
Fetch:                      ↓ (only when pause)

Throttle (200ms):
User types: e-l-a-s-t-i-c...
Events:     ↓ ↓ ↓ ↓ ↓ ↓ ↓
Fetch:      ↓      ↓      ↓ (regularly spaced)

Debounce: Better for autocomplete (wait until user pauses)
Throttle: Better for scroll events (regular updates)
```

### 8.2 Caching Strategies

**3-Level Cache Hierarchy:**

```python
class CachedAutocomplete:
    def __init__(self, trie, cache_ttl=3600):
        self.trie = trie
        self.cache = {}  # In-memory cache (L1)
        self.cache_ttl = cache_ttl
        self.hit_stats = {'hits': 0, 'misses': 0}

    def get_suggestions(self, prefix, limit=10):
        """
        L1: In-memory dictionary cache
        L2: Trie node cache (store traversal results)
        L3: Full results cache (store final ranking)
        """

        cache_key = f"{prefix}:{limit}"

        # L1 Check: Full results cache
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if not self._is_expired(cached_item):
                self.hit_stats['hits'] += 1
                return cached_item['data']

        self.hit_stats['misses'] += 1

        # L2/L3: Compute results
        results = self.trie.search_prefix(prefix)[:limit]

        # Cache results
        self.cache[cache_key] = {
            'data': results,
            'timestamp': time.time(),
            'ttl': self.cache_ttl
        }

        # Cleanup old entries
        self._cleanup_expired()

        return results

    def _is_expired(self, item):
        age = time.time() - item['timestamp']
        return age > item['ttl']

    def _cleanup_expired(self):
        expired_keys = [
            k for k, v in self.cache.items()
            if self._is_expired(v)
        ]
        for key in expired_keys:
            del self.cache[key]

    def get_cache_stats(self):
        total = self.hit_stats['hits'] + self.hit_stats['misses']
        hit_rate = self.hit_stats['hits'] / total if total > 0 else 0
        return {
            'hits': self.hit_stats['hits'],
            'misses': self.hit_stats['misses'],
            'hit_rate': f"{hit_rate*100:.1f}%",
            'cache_size': len(self.cache)
        }
```

**Intelligent Caching by Prefix Length:**

```python
class SmartCache:
    def __init__(self):
        self.prefix_length_cache = {
            1: None,  # Don't cache single character (too many results)
            2: 3600,  # Cache 2-char prefixes for 1 hour (higher traffic)
            3: 7200,  # Cache 3-char prefixes for 2 hours
            4: 86400, # Cache 4+ char prefixes for 24 hours
            5: 86400
        }

    def should_cache(self, prefix):
        return len(prefix) >= 2

    def get_ttl(self, prefix):
        length = len(prefix)
        if length in self.prefix_length_cache:
            return self.prefix_length_cache[length]
        return self.prefix_length_cache[5]  # Default for long prefixes
```

**Distributed Caching (Redis):**

```python
class DistributedAutocompleteCache:
    def __init__(self, redis_client, ttl=3600):
        self.redis = redis_client
        self.ttl = ttl

    def get_suggestions(self, prefix, limit=10):
        cache_key = f"ac:{prefix}:{limit}"

        # Check distributed cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Compute (would call actual suggestion service)
        results = self._compute_suggestions(prefix, limit)

        # Store in distributed cache
        self.redis.setex(cache_key, self.ttl, json.dumps(results))

        return results

    def invalidate_cache(self, prefix):
        """Invalidate cache when index updates"""
        # Invalidate prefix and all sub-prefixes
        pattern = f"ac:{prefix}*"
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, match=pattern)
            if keys:
                self.redis.delete(*keys)
            if cursor == 0:
                break
```

### 8.3 Pre-computation vs Real-Time

**Pre-computation Approach:**

Compute popular queries offline, serve from cache.

```python
class PrecomputedAutocomplete:
    def precompute_popular_suggestions(self):
        """Run nightly or periodically"""

        # Get top 1M queries from logs
        popular_queries = self.logs.get_top_queries(1000000)

        # For each popular query, compute suggestions
        suggestions = {}

        for query in popular_queries:
            for prefix_len in range(1, len(query) + 1):
                prefix = query[:prefix_len]

                if prefix not in suggestions:
                    suggestions[prefix] = set()

                suggestions[prefix].add(query)

        # Store in fast key-value store
        for prefix, sug_set in suggestions.items():
            self.cache.set(prefix, list(sug_set)[:100])

    def get_suggestions(self, prefix):
        """Fast lookup from precomputed cache"""
        return self.cache.get(prefix, [])
```

**Real-Time Approach:**

Compute suggestions on-demand with trie traversal.

```python
class RealTimeAutocomplete:
    def get_suggestions(self, prefix):
        """Compute suggestions real-time from trie"""

        # Traverse trie to prefix node
        node = self._traverse_to_prefix(prefix)

        if not node:
            return []

        # DFS from prefix node to collect all matches
        candidates = []
        self._dfs_collect(node, prefix, candidates)

        # Quick ranking (1-2 signals)
        return sorted(candidates, key=lambda x: -x['frequency'])[:10]
```

**Hybrid Approach:**

Best of both worlds - precompute popular, compute real-time for long-tail.

```python
class HybridAutocomplete:
    def get_suggestions(self, prefix, limit=10):
        """
        Try precomputed first (fast), fall back to real-time (thorough)
        """

        # Check precomputed cache
        cached = self.precomputed_cache.get(prefix)
        if cached:
            return cached[:limit]

        # Not precomputed, compute real-time
        results = self.compute_real_time(prefix)

        # Cache for next time if it becomes popular
        if self._is_becoming_popular(prefix):
            self.precomputed_cache.set(prefix, results)

        return results[:limit]

    def _is_becoming_popular(self, prefix):
        """Check if this prefix is becoming popular"""
        recent_count = self.logs.count_recent(prefix, days=7)
        return recent_count > 100
```

### 8.4 CDN-Based Autocomplete

**Global Content Distribution:**

```
User in Tokyo
  ↓
[CDN Edge in Tokyo] ← Cached popular suggestions
  ├─ Top 10K queries cached at edge
  ├─ Latency: < 10ms
  ├─ Hit rate: ~95% for popular queries
  └─ If miss, fallback to origin server

Origin Server (Central)
  ├─ Full index
  ├─ Recomputed every hour
  ├─ Handles long-tail queries
  └─ Pushes popular queries to CDN
```

**Implementation:**

```
Cache-Control headers:
- Popular prefixes (< 3 chars): Cache for 1 hour
- Medium prefixes (3-6 chars): Cache for 6 hours
- Long prefixes (> 6 chars): Cache for 24 hours

CDN Purge strategy:
- On index update, purge all 1-2 char prefixes
- Keep longer prefixes cached (more stable)
- Pre-warming: Push top 1000 prefixes to CDN
```

---

## 9. Implementation Patterns

### 9.1 Building Production Autocomplete Service

**Complete Python Implementation:**

```python
from typing import List, Tuple, Optional
import json
import time
from collections import Counter, defaultdict
import heapq

class ProductionAutocomplete:
    """
    Production-grade autocomplete service combining:
    - Trie data structure
    - Multi-signal ranking
    - LRU caching
    - Configurable parameters
    """

    def __init__(self, max_cache_size=10000, cache_ttl=3600):
        self.root = TrieNode()
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.cache_access_times = {}
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    def index_queries(self, queries: List[Tuple[str, int]]):
        """
        Index queries with frequencies.
        queries: List of (query_string, frequency) tuples
        """
        for query, frequency in queries:
            self._insert_with_frequency(query, frequency)

    def _insert_with_frequency(self, word: str, frequency: int):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_word = True
        node.word = word
        node.frequency = frequency
        node.last_updated = time.time()

    def get_suggestions(self, prefix: str, limit: int = 10,
                       personalization_factor: dict = None) -> List[str]:
        """
        Get autocomplete suggestions for prefix.

        personalization_factor: Dict with keys:
            - 'user_history': Set of queries user previously searched
            - 'location': User's location
            - 'language': User's language preference
        """

        # Check cache first
        cache_key = f"{prefix}:{limit}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                return cached['suggestions']

        self.stats['cache_misses'] += 1

        # Traverse trie to find candidates
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all candidates with DFS
        candidates = []
        self._collect_candidates(node, candidates)

        # Multi-signal ranking
        ranked = self._rank_suggestions(candidates, personalization_factor)

        # Take top-k
        suggestions = [item[0] for item in ranked[:limit]]

        # Cache results
        self._cache_result(cache_key, suggestions)

        self.stats['total_queries'] += 1
        return suggestions

    def _collect_candidates(self, node, candidates, path=''):
        """DFS to collect all words under node"""
        if node.is_word:
            candidates.append({
                'word': node.word,
                'frequency': node.frequency,
                'last_updated': node.last_updated
            })

        for char, child in node.children.items():
            self._collect_candidates(child, candidates, path + char)

    def _rank_suggestions(self, candidates, personalization):
        """Rank candidates using multiple signals"""
        if not candidates:
            return []

        personalization = personalization or {}
        user_history = personalization.get('user_history', set())

        scored = []
        for candidate in candidates:
            # Primary signal: frequency
            frequency_score = min(candidate['frequency'] / 1000, 1.0)

            # Secondary signal: recency
            age_days = (time.time() - candidate['last_updated']) / 86400
            recency_score = math.exp(-0.1 * age_days)

            # Tertiary signal: personalization
            personalization_score = (1.0 if candidate['word'] in user_history else 0.0)

            # Combined score
            score = (0.6 * frequency_score +
                     0.3 * recency_score +
                     0.1 * personalization_score)

            scored.append((candidate['word'], score))

        # Sort by score descending
        return sorted(scored, key=lambda x: -x[1])

    def _cache_result(self, key, suggestions):
        """Cache result with LRU eviction"""
        self.cache[key] = {
            'suggestions': suggestions,
            'timestamp': time.time()
        }
        self.cache_access_times[key] = time.time()

        # LRU eviction if cache too large
        if len(self.cache) > self.max_cache_size:
            lru_key = min(self.cache_access_times,
                         key=self.cache_access_times.get)
            del self.cache[lru_key]
            del self.cache_access_times[lru_key]

    def get_stats(self):
        """Return performance statistics"""
        total = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total * 100) if total > 0 else 0

        return {
            'total_queries': self.stats['total_queries'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{hit_rate:.1f}%",
            'cache_size': len(self.cache)
        }


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.word = None
        self.frequency = 0
        self.last_updated = time.time()
```

**REST API Wrapper:**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
autocomplete = ProductionAutocomplete()

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """
    GET /api/suggestions?prefix=ela&limit=10&user_history=a,b,c
    """
    prefix = request.args.get('prefix', '')
    limit = int(request.args.get('limit', 10))

    # Parse personalization data
    user_history_str = request.args.get('user_history', '')
    user_history = set(user_history_str.split(',')) if user_history_str else set()

    personalization = {'user_history': user_history}

    suggestions = autocomplete.get_suggestions(prefix, limit, personalization)

    return jsonify({
        'prefix': prefix,
        'suggestions': suggestions,
        'count': len(suggestions)
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(autocomplete.get_stats())


# Initialize with sample data
sample_queries = [
    ('apple', 100000),
    ('application', 50000),
    ('apply', 25000),
    ('approximately', 10000),
    ('approximate', 8000),
]

autocomplete.index_queries(sample_queries)

if __name__ == '__main__':
    app.run(debug=False, port=5000)
```

### 9.2 Spelling Correction Service

```python
from typing import List, Tuple

class SpellingCorrectionService:
    """
    Production spelling correction combining:
    - SymSpell algorithm
    - Language model
    - Error context
    """

    def __init__(self, dictionary_file):
        self.sym_spell = SymSpell()
        self.language_model = LanguageModel()
        self.load_dictionary(dictionary_file)

    def load_dictionary(self, dictionary_file):
        """Load dictionary with word frequencies"""
        with open(dictionary_file, 'r') as f:
            for line in f:
                word, frequency = line.strip().split('\t')
                self.sym_spell.add_to_dictionary(word, int(frequency))
                self.language_model.add_word(word, int(frequency))

    def correct(self, text: str, max_distance: int = 2) -> str:
        """Correct text - handles single or multiple words"""
        words = text.split()
        corrected_words = []

        for word in words:
            if self.language_model.is_known(word):
                # Word is correct
                corrected_words.append(word)
            else:
                # Find correction
                corrections = self.sym_spell.spell_correct(word, max_distance)

                if corrections:
                    best_correction = corrections[0][0]
                    corrected_words.append(best_correction)
                else:
                    # No correction found, keep original
                    corrected_words.append(word)

        return ' '.join(corrected_words)

    def correct_with_confidence(self, word: str,
                                max_distance: int = 2) -> List[Tuple[str, float]]:
        """Return corrections with confidence scores"""
        corrections = self.sym_spell.spell_correct(word, max_distance)

        results = []
        for correction, frequency in corrections:
            distance = self.levenshtein_distance(word, correction)

            # Confidence: inverse of distance, weighted by frequency
            confidence = (1.0 / (1.0 + distance)) * min(frequency / 1000, 1.0)
            results.append((correction, confidence))

        return results
```

---

## 10. Decision Tree: Choosing the Right Approach

### Quick Decision Framework

```
Q1: How many queries/words to index?

├─ < 100K
│  └─ Use: Standard Trie + Simple Ranking
│     Pros: Simple, fast to implement, low memory
│     Cons: Limited optimization
│
├─ 100K - 10M
│  ├─ Q2: Real-time updates needed?
│  │
│  ├─ YES (frequent index updates)
│  │  └─ Use: Trie + Redis Cache
│  │     Pros: Fast updates, distributed cache
│  │     Cons: More complex, network overhead
│  │
│  └─ NO (batch updates only)
│     ├─ Q3: Memory constrained?
│     │
│     ├─ YES (< 1GB)
│     │  └─ Use: Ternary Search Tree or Radix Tree
│     │     Pros: Very memory efficient
│     │     Cons: Slower than Trie, insertion order sensitive
│     │
│     └─ NO (plenty of memory)
│        └─ Use: Trie + Multi-Signal Ranking + Caching
│           Pros: Fast, flexible ranking, good scalability
│           Cons: Memory overhead
│
└─ > 10M
   ├─ Q4: Need fuzzy/spelling correction?
   │
   ├─ YES
   │  └─ Use: Elasticsearch with Completion Suggester
   │     + SymSpell for spelling
   │     Pros: Distributed, scales to billions
   │     Cons: Operational complexity
   │
   └─ NO
      ├─ Q5: Phrase/infix search needed?
      │
      ├─ YES (mid-word matching)
      │  └─ Use: Elasticsearch search_as_you_type
      │     + Edge N-grams
      │     Pros: Flexible search, distributed
      │     Cons: Higher memory/CPU
      │
      └─ NO (prefix-only)
         └─ Use: Elasticsearch Completion Suggester
            or Google Cloud Search
            Pros: Most efficient, lowest latency
            Cons: Less flexible
```

### By Use Case

**E-Commerce Product Search:**
```
Size: 10M+ products
Updates: Hourly
Requirements: Spelling correction, synonyms, attributes

Recommended Stack:
├─ Elasticsearch search_as_you_type (base)
├─ SymSpell for spelling correction
├─ Query log analysis for trending products
├─ Redis cache for top 10K prefixes
└─ Multi-signal ranking (sales, reviews, freshness)
```

**Search Engine Autocomplete:**
```
Size: Billions of queries
Updates: Real-time
Requirements: Personalization, geographic signals

Recommended Stack:
├─ Distributed Trie (or similar)
├─ Multi-tier caching (CDN, regional, local)
├─ Real-time ranking (click signals)
├─ A/B testing framework
└─ ML model for complex ranking signals
```

**Mobile App Autocomplete:**
```
Size: 100K-1M queries
Updates: Daily
Requirements: Small footprint, offline support

Recommended Stack:
├─ Compressed Trie (Radix or TST)
├─ SQLite on device
├─ Sync with server daily
└─ Simple frequency-based ranking
```

**Internal Tool Search:**
```
Size: 1K-100K items
Updates: Daily
Requirements: Simple, reliable, searchable metadata

Recommended Stack:
├─ Trie + Filesystem
├─ Local caching
├─ Simple ranking (alpha + frequency)
└─ Single-machine solution (no distribution needed)
```

---

## References and Further Reading

### Core Algorithms
- [Trie Data Structure - Wikipedia](https://en.wikipedia.org/wiki/Trie)
- [Radix Tree - Wikipedia](https://en.wikipedia.org/wiki/Radix_tree)
- [BK-Tree - Wikipedia](https://en.wikipedia.org/wiki/BK-tree)
- [Efficient Auto-complete with TSTs](https://igoro.com/archive/efficient-auto-complete-with-a-ternary-search-tree/)

### Spelling Correction
- [Peter Norvig's Spell Corrector](http://norvig.com/spell-correct.html)
- [SymSpell GitHub](https://github.com/wolfgarbe/SymSpell)
- [Stanford SLP - Noisy Channel Model](https://web.stanford.edu/~jurafsky/slp3/old_dec21/B.pdf)

### Production Systems
- [Google's Autocomplete HLD](https://www.geeksforgeeks.org/system-design/googles-search-autocomplete-high-level-designhld/)
- [Elasticsearch Autocomplete](https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search)
- [Elasticsearch Completion Suggester](https://blog.mimacom.com/autocomplete-elasticsearch-part3/)
- [Building Smart Autocomplete with Redis](https://upstash.com/blog/redis-autocomplete-popularity-ranking/)

### Search-as-You-Type
- [Edge N-grams in Elasticsearch](https://opster.com/guides/elasticsearch/how-tos/how-to-implement-the-typeahead-in-elasticsearch/)
- [Search-as-You-Type Implementation](https://www.learningstuffwithankit.dev/implementing-auto-complete-functionality-in-elasticsearch-part-ii-n-grams/)

### Query Suggestions
- [Query Suggestion Strategies](https://www.numberanalytics.com/blog/query-suggestion-strategies/)
- [Scoped Search Suggestions - Elastic](https://www.elastic.co/blog/how-to-build-scoped-search-suggestions-and-search-query-corrections)

### System Design
- [System Design Interview: Autocomplete System](https://algomaster.io/learn/system-design-interviews/design-search-autocomplete-system)
- [Design Typeahead System](https://www.enjoyalgorithms.com/blog/design-typeahead-system/)

---

**Document Status:** Complete Reference
**Last Verified:** March 2026
**Total Words:** 3000+
**Sections:** 10 major sections with code examples, algorithms, and production patterns
