# Learned Index Structures: Comprehensive Encyclopedia

## Table of Contents
1. [Introduction & Core Concept](#introduction--core-concept)
2. [Why ML Can Replace Traditional Index Structures](#why-ml-can-replace-traditional-index-structures)
3. [Foundational Work: The Case for Learned Index Structures (Kraska et al., 2018)](#foundational-work-the-case-for-learned-index-structures)
4. [Types of Learned Indexes](#types-of-learned-indexes)
5. [Key Architectures](#key-architectures)
6. [Learned Bloom Filters](#learned-bloom-filters)
7. [Performance Benchmarks](#performance-benchmarks)
8. [Application to Search Systems](#application-to-search-systems)
9. [Update Handling & Dynamic Workloads](#update-handling--dynamic-workloads)
10. [PostgreSQL Integration & Practical Adoption](#postgresql-integration--practical-adoption)
11. [LITune: Automated Tuning with Reinforcement Learning](#litune-automated-tuning-with-reinforcement-learning)
12. [When to Use / When NOT to Use](#when-to-use--when-not-to-use)
13. [Challenges & Limitations](#challenges--limitations)
14. [Future Directions](#future-directions)

---

## Introduction & Core Concept

Learned index structures represent a paradigm shift in database systems: the insight that traditional data structures—B-Trees, hash indexes, Bloom filters, and others—are essentially functions mapping keys to positions or existence predicates. If they are functions, they can potentially be replaced with machine learning models that learn the mapping from data.

Unlike traditional indexes that use carefully engineered algorithms and data structures to organize data, learned indexes leverage machine learning techniques—from simple linear regression to sophisticated neural networks—to predict where a key might be located in a sorted array or whether it exists in a dataset. The key insight is that ML models can be more compact and faster than traditional structures when they learn the underlying data distribution.

This encyclopedia covers the breadth of research, applications, and practical considerations in learned indexing for search, database systems, and data management.

---

## Why ML Can Replace Traditional Index Structures

### The Core Insight: Indexes Are Functions

The foundational insight of learned index structures is deceptively simple: all existing index structures can be viewed as functions:

- **B-Tree Index**: Maps a key → approximate position in a sorted array
- **Hash Index**: Maps a key → position in an unsorted array
- **Bitmap Index**: Maps a key → boolean (existence predicate)

If an index is fundamentally a function, and machine learning is fundamentally about learning functions from data, then ML models can potentially approximate these functions more efficiently than hand-engineered structures.

### Why ML Models Can Win

**1. Exploiting Data Distribution**
Traditional indexes like B-Trees make no assumptions about the underlying data distribution. They use the same algorithm and data layout regardless of whether keys follow a uniform distribution, skewed distribution, correlated multi-dimensional patterns, or clustered distributions. ML models, by contrast, learn the specific distribution present in the data and can exploit regularities that traditional indexes ignore.

**2. Compression Through Learning**
A neural network or learned model can compress the information needed to predict key positions into a compact mathematical function. A B-Tree requires storing pointers, node structures, and metadata; an ML model stores only learned parameters. For example, a simple linear regression model might need only two parameters (slope and intercept) to approximate the CDF of keys.

**3. Cache Efficiency**
Traditional B-Trees must perform pointer chasing and navigate tree structures, which causes cache misses on modern CPUs. ML models, particularly those based on learned linear models or lightweight neural networks, can make predictions in a single forward pass with better cache locality.

**4. Speed vs. Traditional Binary Search**
While binary search takes O(log n) comparisons, a learned model can make a prediction in near-constant time (a single forward pass). Even accounting for a small error bound requiring local search, the overall lookup time is often faster.

### The Trade-off: Accuracy vs. Simplicity

The ML model doesn't need to be perfect. It just needs to be "good enough" to narrow the search space significantly. For example:
- A model might predict position 50,000 when the true position is 50,350 (error of 350)
- A traditional binary search would require ~16 comparisons on 100M records
- The learned model's small error can be resolved with just a few linear scans or binary searches

This bounded-error prediction approach is central to why learned indexes work.

---

## Foundational Work: The Case for Learned Index Structures

### Publication Details

**Title**: The Case for Learned Index Structures
**Authors**: Tim Kraska (MIT), Alex Beutel, Ed H. Chi, Jeffrey Dean, Neoklis Polyzotis
**Published**: SIGMOD 2018 (June 10-15, 2018, Houston, TX)
**Impact**: Seminal paper that spawned an entire research area

### Key Findings

The original paper demonstrated that:

1. **Speed Improvements**: Learned indexes outperformed cache-optimized B-Trees by up to 70% on lookup speed using neural networks
2. **Memory Savings**: Achieved an order-of-magnitude reduction in memory (100x smaller) compared to B-Trees on real-world datasets
3. **Versatility**: The approach generalizes to range queries, point queries, and can replace multiple traditional index types

### Main Contribution: The Recursive Model Index (RMI)

The paper introduced the **Recursive Model Index (RMI)**, a hierarchical model structure that works as follows:

1. **Stage 1**: A simple linear model makes a coarse-grained prediction of the CDF (cumulative distribution function) of the data
2. **Stage 2**: Based on the Stage 1 output, the RMI selects one of multiple second-stage models (e.g., cubic or neural network models) to refine the prediction
3. **Final Output**: The final prediction points to a position in the sorted array, with a bounded error

The RMI structure allows for balancing accuracy and model complexity: simpler models early on, more sophisticated models for refinement.

### Why RMI Works

RMI succeeds because it exploits the observation that different regions of the data often follow different patterns. By using an ensemble of models, it can adapt to local patterns while maintaining a small overall size.

### Theoretical Contribution

The paper theoretically analyzed under which conditions learned indexes outperform B-Trees:
- When the data has strong regularities or non-uniform distribution
- When memory bandwidth is a bottleneck (learned models are smaller)
- When the target platform has good cache behavior for sequential access

---

## Types of Learned Indexes

### 1D Learned Indexes (Point and Range Queries)

**Use Case**: Sorted key-value pairs, ordered data, point lookups and range queries

**Representative Systems**:
- **Recursive Model Index (RMI)**: Hierarchical models for sorted data
- **RadixSpline**: Hybrid structure combining radix tables with linear splines
- **PGM-Index**: Piecewise geometric models with compression
- **ALEX**: Updatable learned index with support for inserts/deletes
- **LIPP**: Learned index with precise position prediction

**Characteristics**:
- Excellent for point lookups on sorted data
- Range queries supported with bounded error
- Can be updatable (ALEX, LIPP) or read-only (RadixSpline, original RMI)

### Multi-Dimensional Learned Indexes

**Use Case**: Range queries on multiple dimensions, spatial data, vector search

**Representative Systems**:
- **Flood**: CDF-based partitioning for orthogonal range queries
- **FlexFlood**: Updatable variant of Flood
- **Tsunami**: Handles correlated data and skewed workloads
- **LISA**: Specialized for spatial data (2D/3D coordinates)

**Characteristics**:
- Projects multi-dimensional data into lower-dimensional space or grid structures
- Uses learned models to optimize data storage layout
- Typically read-optimized (though FlexFlood supports updates)
- Exploits data correlations and query skew

### Probabilistic Data Structures with Learned Models

**Use Case**: Membership queries, existence checks, cardinality estimation

**Representative Systems**:
- **Learned Bloom Filters**: Replace traditional probabilistic filters with ML classifiers
- **Stable Learned Bloom Filters**: For dynamic insertion workloads
- **Partitioned Learned Bloom Filters**: For distributed systems

**Characteristics**:
- Use lightweight ML classifiers instead of hash functions
- Maintain small backup Bloom filters for false negatives
- Dramatically reduce memory consumption (10-100x improvements)
- Preserve correctness guarantees of traditional Bloom filters

### Spatial & Geographic Data Indexes

**Use Case**: Geographic information systems, nearest-neighbor queries, region searches

**Representative Systems**:
- **LISA**: Learned index for spatial data with support for range and KNN queries
- **LiLIS**: Distributed learned spatial index

**Characteristics**:
- Learn mapping functions for spatial partitioning
- Support KNN and range queries efficiently
- Adapt to data distribution within geographic regions

---

## Key Architectures

### 1. Recursive Model Index (RMI) Architecture

**Structure**: Two-stage hierarchical model

```
Input Key
    ↓
[Stage 1: Linear Model]  (coarse prediction of CDF)
    ↓
    ├→ [Stage 2 Model A: Polynomial]
    ├→ [Stage 2 Model B: Neural Network]
    ├→ [Stage 2 Model C: Linear Regression]
    └→ [Stage 2 Model D: Cubic]
    ↓
[Output: Position in Array]
```

**Advantages**:
- Compact: stores only model parameters
- Fast: single forward pass through two stages
- Adaptable: can choose different model types for different regions

**Disadvantages**:
- Training can be expensive (needs to coordinate all models)
- No built-in support for updates (requires retraining)
- Limited to read-only workloads in basic form

### 2. PGM-Index (Piecewise Geometric Model) Architecture

**Structure**: Recursive linear model approximation with error bounds

```
Keys: [1, 5, 8, 12, 15, 20, 25, 30, ...]
                ↓
        [Learn Linear Model]
        m = 1.5x + 2 (max error ε)
                ↓
        If error exceeds ε, recursively partition
        and build models for subregions
                ↓
        [Compressed Tree of Linear Models]
```

**Key Innovation**: Uses the theoretical lower bound on predecessor search to guide model construction. Each linear segment has a guaranteed maximum error tolerance.

**Advantages**:
- Theoretically optimal space-time tradeoff
- Fully-learned (unlike RMI which mixes traditional and learned)
- Supports fully-dynamic operations (insertions, deletions)
- Orders of magnitude compression (1140x less space than B-Trees in dynamic setting)

**Disadvantages**:
- Complex implementation
- Slower than some specialized structures on pure read-only workloads
- Compression overhead in some scenarios

### 3. ALEX (Adaptive Learned IndeX) Architecture

**Structure**: Learned index with gapped array layout for efficient updates

```
Learned Model Layer
        ↓
    [Linear Model predicts region]
        ↓
    [Gapped Array with Strategic Gaps]
        ├─ data[0] | gap | data[1] | gap | ...
        └─ Gaps allow efficient insertion without shifting
        ↓
    [Adaptive Gaps based on insert distribution]
```

**Key Innovation**: **Gapped Array Layout**
- Unlike traditional arrays that require shifting on insertion, gapped arrays have empty slots strategically placed
- Gaps are positioned based on observed insertion patterns
- When gaps fill up, the array is split into two leaf nodes

**Advantages**:
- Supports full CRUD operations (create, read, update, delete)
- Adapts online to changing data distributions
- Up to 4.1x faster than B+Trees on mixed read-write workloads
- 2000x smaller index size

**Disadvantages**:
- More complex data structure than simple arrays
- Overhead from gap management during insertions

### 4. RadixSpline: Hybrid Learned Index

**Structure**: Combines radix tables with linear splines

```
Search Key
    ↓
[Radix Table: Extract prefix bits]
    ↓
[Lookup in radix table to find spline segment]
    ↓
[Linear Spline Interpolation: Fine-grained position]
    ↓
[Binary Search in predicted range]
```

**Key Innovation**: Hybrid approach that doesn't require training; can be built in a single pass over sorted data.

**Advantages**:
- Single-pass construction (no need for iterative training)
- Competitive with RMI in size and lookup performance
- Simple and practical to implement
- Predictable build time

**Disadvantages**:
- Limited to numeric data types (uint32_t, uint64_t)
- Read-only (no update support in original form)
- Slightly larger than fully-optimized learned models

### 5. LIPP (Learned Index with Precise Positions)

**Structure**: Learned index with precise key-to-position mapping

```
Learned Model → Position Prediction
                    ↓
            [Precise Position]

If multiple keys map to same position:
    → [Child node created for disambiguation]
    → [Eliminates "last-mile" search]
```

**Key Innovation**: Focuses on **precise position prediction** rather than approximate ranges. If the model predicts position 50,000, the key is exactly at position 50,000 (or a child node handles conflicts).

**Advantages**:
- Eliminates the "last-mile" search in leaf nodes
- Lookup cost bounded to tree height
- Supports full range of operations: lookup, range, insert, update, delete, bulkload
- Reduces lookup latency compared to ALEX

**Disadvantages**:
- More memory overhead than ALEX (4.5-5.4x higher)
- Complex child node management

---

## Learned Bloom Filters

### What Are Learned Bloom Filters?

Traditional Bloom filters answer the question: "Does element x exist in this set?" with a probability of false positives but zero false negatives. They use multiple hash functions to set bits in a large bit array.

**Learned Bloom Filters** replace the hash-based approach with:
1. A lightweight ML classifier (decision tree, neural network, or similar)
2. A small backup traditional Bloom filter for false negatives

### How They Work

```
Input: Query element x

Step 1: ML Classifier
    ├─ If prediction score > threshold τ → return "Present"
    └─ If prediction score ≤ τ → query backup Bloom filter

Step 2: Backup Bloom Filter (for false negatives only)
    └─ Returns accurate answer for elements classified as absent by ML
```

### Advantages

**1. Dramatic Space Savings**
- Traditional Bloom filter: 10 bits per element minimum
- Learned Bloom filter: 1-2 bits per element + small model
- Reduction: 10-100x smaller than traditional Bloom filters

**2. Faster Lookups**
- Single ML prediction is faster than multiple hash computations
- No need to probe multiple memory locations (better cache locality)

**3. Adaptive to Data Distribution**
- ML models learn which elements are more likely to be queried
- Can exploit patterns in the data

### Disadvantages

**1. Training Overhead**
- Requires labeled examples (present vs. absent elements)
- Training time adds to index construction

**2. Distribution Sensitivity**
- Performance degrades if query distribution differs from training distribution

**3. Complexity**
- More complex than traditional Bloom filters
- Difficult to update dynamically

### Applications in LSM-Trees

**Context**: LSM-Trees (Log-Structured Merge-trees) use Bloom filters to determine whether a key might exist before performing expensive disk lookups.

**Learned Bloom Filter Benefits**:
- Reduce memory footprint of Bloom filters (critical in LSM-trees with many levels)
- Improve lookup latency on negative queries
- Enable more aggressive caching of other structures

---

## Performance Benchmarks

### 1D Learned Indexes vs. B-Trees

| Metric | Learned Index | B-Tree | Winner |
|--------|---------------|--------|--------|
| Lookup Speed (ns) | 50-100 ns | 150-300 ns | Learned (1.5-3x faster) |
| Memory Usage | 10-100 MB | 100 MB - 1 GB | Learned (100x smaller) |
| Range Query | Similar to B-Tree | Optimized | B-Tree (slightly better) |
| Insert Performance | Depends on structure | O(log n) | B-Tree (if not learned+updatable) |
| Cache Behavior | Excellent | Good | Learned |

**Key Insight**: Learned indexes excel at point lookups on read-mostly workloads with ample memory; B-Trees are still superior for mixed workloads or when memory is tightly constrained.

### ALEX vs. B+Trees (from SIGMOD 2020)

On read-only workloads:
- **ALEX**: Up to 2.2x faster than original learned index
- **ALEX**: Up to 15x smaller index size

On mixed read-write workloads:
- **ALEX**: Up to 4.1x faster than B+Trees
- **ALEX**: 2000x smaller index size (median 3.2x)
- **Trade-off**: Slightly more complex implementation than B+Trees

### PGM-Index Results (VLDB 2019-2020)

**Static workloads (read-only)**:
- Query performance: within 2 orders of magnitude of cache-optimized B+-trees (ratio: ~83x)
- Space consumption: **1140x less space** than B+-tree

**Fully-dynamic workloads (with inserts/deletes)**:
- **Query time**: Up to 71% faster than B+-trees
- **Update time**: Up to 40% faster than B+-trees
- **Space consumption**: **1140x less space**

### RadixSpline in RocksDB

When integrated into RocksDB key-value store:
- Average read time: **20% decrease**
- Total execution time: 521s (RadixSpline) vs. 712s (B-Tree)
- Memory usage: **45% less** than B-Tree variant

### Google Bigtable Integration (Real-World)

Google integrated learned indexes into Bigtable (their web-scale distributed storage system):
- **Mean read latency**: Reduced significantly
- **Tail latency**: Substantial improvements (important for user experience)
- **Throughput**: Measurable improvements
- **Index size**: Orders of magnitude reduction

### Learned Bloom Filters

Comparison of space usage:
- **Traditional Bloom Filter**: 10 bits/element for 1% false positive rate
- **Learned Bloom Filter**: 1-2 bits/element for same false positive rate
- **Reduction**: 5-10x smaller

Comparison of lookup performance:
- Traditional: Multiple hash computations and memory accesses
- Learned: Single ML prediction (single forward pass)
- **Improvement**: 20-50% faster on average

### Flood (Multi-Dimensional)

On real-world datasets and workloads:
- **Performance**: Up to 3 orders of magnitude (1000x) faster for range scans with predicates
- **Speed-up**: Compared to state-of-the-art traditional multi-dimensional indexes (R-trees) and column-oriented sort orders
- **Trade-off**: Optimized for reads; writes are slow or unsupported

### Tsunami (with Skewed Workloads)

Compared to other learned multi-dimensional indexes:
- **Performance**: Up to 6x faster than Flood
- **Size**: Up to 8x smaller than Flood

Compared to traditional indexes:
- **Query time**: Up to 11x faster than R-trees
- **Size**: 170x smaller than optimally-tuned traditional indexes

---

## Application to Search Systems

### Context: How Search Engines Use Indexes

Modern search engines (Google, Bing, Elasticsearch, etc.) use **inverted indexes**:

```
Term Dictionary          Posting Lists
─────────────           ────────────
"machine" → [Pos: X] → [DocID: 1, freq: 3, positions: [5, 12, 45]]
                      → [DocID: 5, freq: 1, positions: [23]]
                      → [DocID: 7, freq: 2, positions: [10, 88]]

"learning" → [Pos: Y] → [DocID: 1, freq: 2, positions: [50, 120]]
                      → [DocID: 3, freq: 5, positions: [...]]
```

### Application 1: Fast Dictionary Lookup

**Problem**: For each query term, quickly locate its posting list

**Traditional Approach**: B-Tree or hash table over term dictionary

**Learned Approach**: Train a learned index (RMI or ALEX) on term keys
- Terms are typically sorted lexicographically
- Distribution of popular vs. rare terms can be learned
- ML model can predict approximate location of term in dictionary

**Benefits**:
- Faster term lookup (50-100ns instead of 150-300ns)
- Smaller in-memory footprint for dictionary
- Better cache behavior

### Application 2: Posting List Compression & Traversal

**Problem**: Once you've found a term's posting list, traverse it efficiently

**Traditional Approach**: Linear scan, binary search, or compressed format traversal

**Learned Approach**: Learn the distribution of document IDs within a posting list
- If DocIDs are: [1, 5, 8, 12, 15, 20, 25, 30, ...]
- A learned model can predict approximate position of DocID 18
- Binary search or exponential search can refine from prediction

**Benefits**:
- Faster DocID location in posting list
- Enables efficient intersection of multiple posting lists

### Application 3: Document ID Mapping

**Problem**: Map external document IDs to internal storage locations

**Traditional Approach**: Hash table (O(1) average) or B-Tree (O(log n))

**Learned Approach**: Train a learned index on internal DocID → storage location mapping
- DocIDs often have patterns (sequential, batched, hierarchical)
- Learned model can exploit these patterns

**Benefits**:
- Smaller memory footprint
- Faster lookup for range-based or sequential DocID queries

### Application 4: Field Indexing in Structured Search

**Problem**: Index and search structured fields (URLs, timestamps, ratings, etc.)

**Traditional Approach**: Multiple B-Trees or hash indexes for different fields

**Learned Approach**: Use specialized learned indexes
- **1D indexes**: Timestamps, ratings, numeric fields
- **Multi-dimensional indexes**: Combinations of fields
- **Learned Bloom filters**: For field existence/value membership

**Benefits**:
- Compact multi-field indexes
- Faster field-based filtering

### Real-World Search Engine Use Cases

**1. Google's Web Search (Bigtable Integration)**
- Applied learned indexes to Bigtable row key indexing
- Reduced index memory by orders of magnitude
- Improved query latency (both mean and tail)
- Benefits applied to billions of documents

**2. Elasticsearch / OpenSearch**
- Could use learned indexes for term dictionary (not yet widely adopted)
- Multi-dimensional learned indexes for range queries on numeric fields
- Potential for learned Bloom filters in filter cache

**3. Information Retrieval Systems**
- Learned indexes for BM25 term frequency index
- Learned spatial indexes for geographic search
- Learned indexes for vector-based semantic search

### Why Learned Indexes May Not Yet Be Widespread

Despite theoretical advantages, adoption in search engines is limited due to:

1. **Distribution Shift**: Query patterns may change over time
2. **Update Overhead**: Search indexes receive continuous insertions/deletions
3. **Robustness**: Traditional indexes are proven, tested, and well-understood
4. **Engineering Burden**: Integrating new index types into mature systems is expensive
5. **Workaround Viability**: Traditional indexes work "well enough" for most use cases

---

## Update Handling & Dynamic Workloads

### The Original Challenge

The original learned index structures (RMI, 2018) were **read-only**. This severely limited practical applicability because:

- Real databases receive continuous insertions, updates, and deletions
- Search indexes must add new documents constantly
- LSM-trees require frequent writes to support database operations

### Solution 1: ALEX (Adaptive Learned Index)

**Approach**: Learned index + Gapped Array layout

**Mechanism**:
```
Before insertion of 50:  data[0..10] | gap | gap | data[11..20] | ...
                        (keys: 1, 5, 10, 15, 20, ...)

Insert 50:               data[0..10] | gap | 50 | gap | data[11..20] | ...
                        Fits in gap without shifting!

Gap fills up:           Split node into two leaves with new gaps
```

**Performance Characteristics**:
- **Insert**: O(f) where f is number of elements to shift (usually small due to gaps)
- **Deletion**: O(f) with potential gap reorganization
- **Lookup**: Still O(1) prediction + O(log n) local search

**Trade-offs**:
- Complexity: More complex than simple arrays
- Gap management: Overhead in tracking and maintaining gaps
- Adaptivity: Gaps must be repositioned as insertion patterns change

### Solution 2: PGM-Index (Recursive Linear Models)

**Approach**: Fully-dynamic learned index from first principles

**Mechanism**:
- Build linear models with error bounds recursively
- When data changes, rebalance models and segments
- Maintain pointer-based structure (unlike ALEX array)

**Performance Characteristics**:
- **Query**: Fast (similar to static case)
- **Insert**: O(log n) amortized (like B-Trees)
- **Delete**: O(log n) amortized
- **Update**: O(log n)

**Advantages**:
- Theoretically optimal space-time tradeoff
- No specialized gap management needed
- Natural support for all operations

**Disadvantages**:
- Implementation complexity
- Training cost for model construction

### Solution 3: LIPP (Learned Index with Precise Positions)

**Approach**: Precise position prediction with child node disambiguation

**Mechanism**:
```
If model predicts position 50 for multiple keys:
    → Create child node to handle collisions
    → Each key has precise position or child node

Lookup: Follow precise position → may recurse to child
```

**Performance Characteristics**:
- **Lookup**: Bounded to tree height (typically 2-3 levels)
- **Insert**: Create child nodes as needed
- **Delete**: Mark as deleted or reorganize

**Advantages**:
- Precise predictions eliminate "last-mile" search variability
- Naturally handles collisions

**Disadvantages**:
- Higher memory overhead than ALEX (4.5-5.4x in some cases)
- Child node management complexity

### Solution 4: FlexFlood (Updatable Multi-Dimensional)

**Approach**: Extension of Flood (read-only) with dynamic updates

**Mechanism**:
- Core Flood structure for spatial partitioning
- Adaptive reorganization when inserts/deletes change distribution
- Flexible grid resizing and rebalancing

**Performance Characteristics**:
- **Read-heavy**: Nearly as fast as static Flood
- **Inserts**: Trigger reorganization (cost varies)
- **Deletes**: Efficient marker-based deletion

**Trade-offs**:
- Less aggressive optimization than fully static Flood
- Rebalancing cost when distribution shifts significantly

### General Patterns for Dynamic Learned Indexes

**Pattern 1: Adaptive Rebalancing**
- Monitor insert patterns
- Periodically rebuild or reorganize based on new distribution
- Cost amortized over many operations

**Pattern 2: Hybrid Structures**
- Use learned components for primary organization
- Fallback to traditional structures (B-Trees) for local operations
- Example: RMI predicts region, local B-Tree handles exact position

**Pattern 3: Online Learning**
- Start with initial model from training data
- Continuously update model as new data arrives
- Example: ALEX's adaptive gap placement

### Current State of Dynamic Learned Indexes

**Mature Solutions**:
- ALEX: Production-ready, comprehensive benchmarks
- PGM-Index: Fully-dynamic, theoretically optimal
- LIPP: Good for diverse workloads

**Research Challenges**:
- Finding optimal balance between update cost and query speed
- Predicting when reorganization is necessary
- Handling adversarial insertion patterns

---

## PostgreSQL Integration & Practical Adoption

### Current Status (As of PGConf.dev 2025)

**Assessment**: Learned indexes remain in **research and development phase** within PostgreSQL ecosystem. No official PostgreSQL core support yet, but active exploration.

### Discussion at PGConf.dev 2025

Presenters Gary Evans and Nishchay Kothari presented on "Exploring Learned Indexes in PostgreSQL," raising key questions:

1. **Architectural Feasibility**: How to integrate learned models into PostgreSQL's extensible indexing framework?
2. **Robustness Concerns**: Traditional B-Trees provide consistent, predictable performance. Learned indexes may have unpredictable failure modes.
3. **Fragility Assumptions**: The assumption that you have robust foreknowledge of the dataset seems incredibly fragile in production systems.

### Potential PostgreSQL Integration Approaches

### Approach 1: Custom Access Method (AM)

PostgreSQL's `CREATE INDEX` syntax allows custom access methods:

```sql
CREATE INDEX idx_my_table ON my_table USING learned_am (column_name);
```

**Requirements**:
- Implement PostgreSQL AM interface (scan, insert, delete, vacuum, etc.)
- Handle PostgreSQL transaction semantics
- Manage cache pages and WAL (write-ahead log) for durability

**Challenge**: PostgreSQL's AM interface is complex; learned indexes must handle:
- Concurrent access and locking
- Transaction isolation levels
- Crash recovery
- Index size estimation

### Approach 2: Hybrid Strategy (ALEX-like with B-Tree Fallback)

**Idea**: Use learned index as primary, fall back to B-Tree segments on error

```
Query Key X
    ↓
[Learned Model: Predict position]
    ↓
[Is error within bounds?]
    ├─ YES: Search in predicted range → success
    └─ NO: Fallback to B-Tree segment for this region
```

**Advantages**:
- Safety: Always correct results even if prediction fails
- Robustness: Graceful degradation on distribution shift
- Production-ready: Can guarantee SLA compliance

**Disadvantages**:
- Complexity: Must maintain both structures
- Space: May not achieve theoretical space savings

### Approach 3: PostgreSQL Extension (Non-Core)

**Existing Examples**:
- PGM-Index extension: Some researchers have published PGM-Index PostgreSQL extensions

**Development Path**:
1. Create PostgreSQL extension with custom AM
2. Implement core learned index operations
3. Handle PostgreSQL-specific concerns (durability, concurrency)
4. Community testing and feedback
5. Consider for PostgreSQL core if proven reliable

### Approach 4: Learned Index for Bloom Filters Only

**Shorter-term path**: Replace Bloom filters in indexes with learned variants

**Use Case**: Index filter pages in B+Trees

PostgreSQL uses Bloom filters in hash joins and some index structures. Learned Bloom filters could:
- Reduce memory for filter pages
- Improve cache performance
- Maintain correctness guarantees

**Advantage**: Smaller change surface, easier integration

### Practical Challenges in PostgreSQL

**1. Durability and Crash Recovery**
- PostgreSQL uses WAL (write-ahead log) for durability
- Learned indexes must participate in WAL protocol
- On recovery, must rebuild or reload learned models
- Challenge: ML models aren't traditionally part of database recovery

**2. Concurrent Access**
- PostgreSQL supports concurrent readers and writers
- Learned indexes must handle concurrent access safely
- Row-level locks, page locks, and transaction isolation
- Challenge: Learned model updates must be coordinated with locks

**3. Adaptive Reorganization**
- Learned indexes like ALEX reorganize based on insert patterns
- Must coordinate reorganization with ongoing queries
- Cannot block all access during reorganization
- Challenge: Online reorganization is complex

**4. Vacuum and Maintenance**
- PostgreSQL VACUUM removes dead tuples and reclaims space
- Learned indexes must handle vacuum events
- Statistics must be updated post-vacuum
- Challenge: Model updates after vacuum are not trivial

**5. Query Planner Integration**
- PostgreSQL's query planner chooses between indexes
- Must provide cost estimates for learned indexes
- Different learned indexes have different characteristics
- Challenge: Cost model must be accurate and adaptive

### Production Deployment Lessons from Bigtable

Google's integration of learned indexes into Bigtable (real distributed system) revealed:

**Success Factors**:
1. **Read-Heavy Workloads**: Most beneficial where lookups >> updates
2. **Distribution Stability**: Works best with stable, learnable distributions
3. **Bounded Error**: Use bounded-error models with fallbacks
4. **Graceful Degradation**: Always have traditional fallback mechanism

**Caution Points**:
1. **Distribution Shift**: Monitor and retrain when distribution changes
2. **Adversarial Data**: Potential for adversarial insertions to cause poor performance
3. **Complexity Trade-off**: Code complexity increases; must be worth it
4. **Testing Burden**: Extensive testing needed for edge cases

### Path to PostgreSQL Adoption

**Short-term (2025-2026)**:
- Research integrations and community extensions
- Benchmark learned indexes on realistic PostgreSQL workloads
- Develop best practices for learned Bloom filters in existing indexes

**Medium-term (2026-2028)**:
- Develop and test custom AM implementations
- Community feedback and performance evaluation
- Consider PostgreSQL extension marketplace distribution

**Long-term (2028+)**:
- Potential PostgreSQL core integration if proven stable and beneficial
- Integration with query planner
- Automatic selection of learned vs. traditional indexes

---

## LITune: Automated Tuning with Reinforcement Learning

### What is LITune?

**Full Name**: LITune: Tuning Learned Indexes using Deep Reinforcement Learning
**Status**: Accepted to SIGMOD 2025 (published early 2025)
**Authors**: Taiyi Wang and collaborators from University of Cambridge

### The Problem

Learned index structures have many hyperparameters:
- Model type (linear, polynomial, neural network, decision tree)
- Model depth/complexity
- Cache line optimization
- Gapped array gap sizes
- Bloom filter backup size
- Rebuild frequency
- Training data sampling rate

Tuning these parameters is a complex optimization problem:
- Too many combinations to enumerate
- No clear guidelines on optimal settings
- Different workloads require different tunings
- Manual tuning is time-consuming and error-prone

### LITune's Approach

**Framework**: End-to-end automatic tuning using Deep Reinforcement Learning (DRL)

**Key Components**:

**1. Adaptive Training Pipeline**
- Generates candidate parameter configurations
- Trains learned indexes with different hyperparameters
- Measures performance on representative workload
- Feeds results back to DRL agent

**2. Tailor-made Deep Reinforcement Learning**
- Uses DRL (not genetic algorithms or random search)
- Learns which parameter combinations work well
- Explores parameter space intelligently (not exhaustively)
- Balances exploration (try new combinations) vs. exploitation (refine good ones)

**3. O2 System: Online Learning and Tuning**
- Continuously monitors production performance
- Detects performance degradation from workload shift
- Automatically triggers retuning
- "O2" = Online Learning and Tuning system

**4. Safety Mechanisms**
- Prevents unsafe parameter configurations
- Rollback capability if new tuning degrades performance
- Ensures stable performance during tuning

### Performance Results

**Compared to Default Parameters**:
- **Runtime**: Up to 98% reduction
- **Throughput**: Up to 17x improvement
- **Latency**: Consistent improvements across different workloads

**Mechanism of Improvement**:
- Default parameters often poorly chosen for specific workload
- LITune learns workload characteristics
- Optimizes parameters specifically for observed patterns
- Reduces cache misses, memory usage, and computation

### Technical Details

**State Space** (observed by DRL agent):
- Current workload characteristics (read/write ratio, key distribution)
- Current performance metrics (latency, throughput, memory)
- Recent configuration changes and their effects

**Action Space** (decisions made by DRL agent):
- Parameter selection for next experiment
- Training data size
- Model complexity
- Cache optimization level

**Reward Function**:
- Optimizes for low latency and high throughput
- Penalizes memory overhead
- Encourages stable configurations

### Advantages of Automatic Tuning

**1. Workload Adaptation**
- No manual intervention needed
- Automatically adapts to shifting workloads
- Handles diverse data distributions

**2. Performance Optimization**
- Explores parameter space systematically
- Finds configurations humans might miss
- Continuous improvement over time

**3. Ease of Use**
- No need for DBA expertise in learned index tuning
- Set-and-forget operation
- Enables broader adoption of learned indexes

### Limitations and Considerations

**1. Training Cost**
- DRL model training itself requires computation
- Must amortize training cost over performance gains
- Cold-start problem: needs time to learn before seeing benefits

**2. Stability**
- DRL can be unstable in some scenarios
- Requires careful reward function design
- May need human oversight in early deployments

**3. Safety**
- LITune includes safety mechanisms but must be monitored
- Automatic retuning could cause temporary performance dips
- Rollback capabilities are important

### Integration with Learned Index Ecosystem

**Potential Targets for LITune**:
- ALEX indexes: Optimize gap placement, node split strategies
- RMI indexes: Tune model types and depths for each stage
- PGM-Indexes: Adjust error tolerance and split points
- Learned Bloom filters: Optimize classifier architecture and backup filter size

### Future Directions for LITune

1. **Hardware-Aware Tuning**: Optimize for specific CPU architectures
2. **Distributed Tuning**: DRL for tuning in distributed settings (Bigtable-like)
3. **Cross-Workload Learning**: Transfer learning from similar workloads
4. **Interactive Tuning**: Human feedback to improve DRL agent

---

## When to Use / When NOT to Use

### Use Learned Indexes When:

**✓ 1. Read-Mostly Workloads**
- Point lookups dominate (>80% of operations)
- Few insertions/deletions
- Perfect for: Caching layers, read-optimized analytics, historical data

**✓ 2. Large, Stable Datasets**
- Data distribution is learnable and stable
- Distribution doesn't change dramatically over time
- Perfect for: Google's Bigtable, machine learning datasets, reference data

**✓ 3. Memory is Constrained**
- Memory bandwidth is a bottleneck
- Disk access is expensive (SSD or spinning disk)
- Perfect for: Embedded systems, IoT devices, cost-sensitive cloud

**✓ 4. Predictable Access Patterns**
- Workload patterns are relatively consistent
- Can be learned by ML models
- Perfect for: Time-series data, geographic queries, repeated analytical queries

**✓ 5. Point and Prefix Queries Only**
- Don't need efficient range queries
- 1D learned indexes for point lookups
- Perfect for: Key-value stores, dictionary lookups, term indexes in search

**✓ 6. Highly Skewed Data Distribution**
- Data follows non-uniform distribution (Zipfian, power-law, etc.)
- ML models excel at exploiting skew
- Perfect for: User activity logs, natural language term frequencies

**✓ 7. Single Machine, In-Memory**
- System architecture is simple
- No distributed coordination needed
- Perfect for: Analytical databases, specialized search systems

**✓ 8. Can Accept Distribution Shift Monitoring**
- Willing to monitor and retrain periodically
- Have processes for detecting and handling model degradation
- Perfect for: Large organizations with ML expertise

### Don't Use Learned Indexes When:

**✗ 1. Write-Heavy Workloads**
- Many insertions/updates/deletions
- Updates make learned model stale
- Problem: ALEX and dynamic structures have overhead; might not be faster than B-Trees
- Better: Use B-Trees, LSM-Trees, or hash tables

**✗ 2. Complex Range Queries**
- Need efficient range queries on large ranges
- Learned models have bounded error but still need sequential scan
- Problem: B-Trees navigate efficiently; learned models degrade
- Better: B-Trees with range query optimization

**✗ 3. Completely Unknown Data Distribution**
- No prior knowledge of data distribution
- Training data might not be representative
- Problem: ML model may be no better than traditional index
- Better: Use general-purpose B-Trees that work for all distributions

**✗ 4. Adversarial or Hostile Inputs**
- Data could be deliberately crafted to break the index
- Adversarial insertions can cause worst-case behavior
- Problem: Attackers could cause O(n) lookups or memory explosion
- Better: Use traditional structures with guaranteed worst-case bounds

**✗ 5. Rapidly Changing Distributions**
- Data distribution changes frequently
- Learned model becomes stale between retraining
- Problem: Distribution shift causes performance degradation; retraining is expensive
- Better: Traditional structures that adapt gradually or use sketch-based structures

**✗ 6. OLTP (Online Transaction Processing) Workloads**
- Mix of reads and writes
- Low latency is critical
- Transactions span multiple indexes
- Problem: Complexity and overhead make OLTP performance unpredictable
- Better: B-Trees, which are well-understood and have predictable behavior

**✗ 7. Complex Queries Spanning Multiple Indexes**
- Learned indexes optimized individually, not for complex query plans
- Interactions between multiple learned indexes unclear
- Problem: Query planner complexity increases significantly
- Better: Traditional indexes work well with existing query optimizers

**✗ 8. Limited Monitoring and Operations Infrastructure**
- No ML expertise in team
- Cannot monitor model performance
- Cannot handle retraining and updates
- Problem: Learned indexes require more operational oversight
- Better: Stick with proven traditional structures

**✗ 9. Must Guarantee Strict SLA**
- SLA violation is costly or critical (medical, financial systems)
- Need guaranteed worst-case performance
- Problem: Learned model could have unpredictable failures
- Better: Traditional indexes with proven performance bounds

**✗ 10. String Keys (Some Learned Indexes)**
- Some learned indexes (RadixSpline) only support numeric types
- String comparison is more complex to learn
- Problem: Implementation complexity for string support is significant
- Better: B-Trees handle strings naturally

### Decision Matrix

```
                    Learned Index  |  B-Tree  |  Hash Index  |  LSM-Tree
                    ─────────────────────────────────────────────────────
Read-heavy             ★★★★★      |  ★★★★   |    ★★★★★    |   ★★★
Write-heavy            ★★          |  ★★★★   |    ★★★★     |   ★★★★★
Range queries          ★★★         |  ★★★★★  |    ★         |   ★★★★
Point lookups          ★★★★★       |  ★★★★   |    ★★★★★    |   ★★★
Memory usage           ★★★★★       |  ★★★    |    ★★★      |   ★★★
Adaptability           ★★★★        |  ★       |    ★        |   ★★★
Complexity            ★★           |  ★★★★★  |    ★★★★★   |   ★★★★

Legend: ★ = poor, ★★★ = average, ★★★★★ = excellent
```

---

## Challenges & Limitations

### 1. Distribution Shift Problem

**Challenge**: ML models train on a snapshot of data. When the actual data distribution changes, model predictions become less accurate.

**Manifestations**:
- New keys arrive with different patterns
- Popular keys change over time
- Seasonal patterns in real-world data

**Current Solutions**:
- Monitor prediction accuracy continuously
- Retrain models periodically (e.g., daily, weekly)
- Detect distribution shift automatically

**Unsolved Issues**:
- When to trigger retraining (too often = overhead, too late = performance loss)
- How to retrain without service interruption
- How to handle gradual vs. sudden shifts

### 2. Adversarial Inputs and Security

**Challenge**: Machine learning models can be fooled. Adversarial insertions could cause the learned index to degrade.

**Research Finding** (Algorithmic Complexity Attacks on Dynamic Learned Indexes):
- Attackers can craft specific insertion sequences
- Cause memory usage to explode (1000x increase)
- Cause lookup time to degrade dramatically (1641x slowdown)

**Attack Vectors**:
1. **Memory Explosion**: Insert keys that all hash to same position; force many reorganizations
2. **Model Degradation**: Insert keys that don't match model predictions; cause recalibration
3. **Cache Misses**: Insert keys to maximize cache misses

**Current Mitigations**:
- Use fallback B-Trees for safety (hybrid approach)
- Monitor for anomalous insertion patterns
- Limit maximum reorganization depth

**Unsolved Issues**:
- How to detect adversarial data in practice
- Trade-off between robustness and performance
- Scalability of detection mechanisms

### 3. Accuracy vs. Latency Trade-off

**Challenge**: More complex ML models are more accurate but slower to evaluate.

**Example**:
- Linear model: 10 ns to evaluate, but high prediction error
- Neural network: 100 ns to evaluate, but lower error

If the additional error requires more local search, the latency improvement is lost.

**Current Solutions**:
- Use simple, fast models (linear, polynomial)
- Multi-stage models (coarse then fine)
- Model compression techniques

**Unsolved Issues**:
- Automated selection of model complexity vs. latency trade-off
- Theoretical analysis of optimal trade-off

### 4. Update Overhead

**Challenge**: Updates to learned indexes can be expensive, potentially slower than B-Trees.

**Mechanisms**:
- Inserting into gapped arrays may require shifting (ALEX)
- Rebalancing multi-dimensional indexes is expensive (Flood)
- Maintaining precise positions requires node creation (LIPP)

**Current Solutions**:
- Adaptive gapped arrays (ALEX)
- Amortized analysis (PGM-Index)
- Hybrid structures with B-Tree local operations

**Unsolved Issues**:
- Updates to multi-dimensional indexes still very expensive
- Balancing adaptivity with update cost
- Predicting when reorganization is necessary

### 5. Multi-Dimensional Complexity

**Challenge**: Extending 1D learned indexes to multiple dimensions is non-trivial.

**Issues**:
- Multi-dimensional space has curse of dimensionality
- Data correlations must be exploited (hard to learn)
- Range query semantics change
- Skewed workloads have complex patterns

**Current Solutions**:
- Specialized architectures (Tsunami, Flood, LISA)
- Empirical CDF transformations
- Grid-based partitioning

**Limitations**:
- No universally best multi-dimensional index
- Trade-offs vary significantly
- Complex to integrate with query optimizers

### 6. String and Categorical Data

**Challenge**: Most learned indexes optimize for numeric keys.

**Why Strings Are Hard**:
- String comparison is complex (lexicographic order)
- Prediction on strings is non-trivial
- Encoding strings as numeric features is lossy

**Current Solutions**:
- Encode strings to numeric keys (hash or lexicographic rank)
- Use prefix-based indexes (radix trees combined with learning)
- Tree structures that handle string splitting

**Limitations**:
- Encoding adds overhead
- Loss of string semantics
- Complex to handle variable-length strings

### 7. Theoretical Foundations

**Challenge**: Limited theoretical analysis of when/why learned indexes work.

**Questions**:
- When does a learned model beat a traditional index?
- What are fundamental limits on compression?
- Can we prove worst-case bounds?

**Current Work**:
- PGM-Index provides theoretical lower bounds
- Information-theoretic analysis of learned indexes
- Trade-off analysis (space vs. time)

**Unsolved**:
- Unified theory across all learned index types
- Predictability of performance in novel scenarios
- Optimality of existing structures

### 8. Integration with Database Systems

**Challenge**: Learned indexes don't fit traditional database architecture.

**Issues**:
- Query optimizers designed for traditional indexes
- Cost estimation is difficult and index-specific
- Concurrent access and locking is complex
- Durability and crash recovery must be rethought
- Statistics and cardinality estimation assumptions break

**Current Solutions**:
- Custom access methods in PostgreSQL
- Research prototypes in specialized systems
- Hybrid approaches (learned + traditional)

**Adoption Barriers**:
- Implementation complexity
- Testing and validation burden
- Operational overhead

### 9. Comparison and Benchmarking

**Challenge**: Difficult to fairly compare learned indexes across systems.

**Issues**:
- Different implementations have different trade-offs
- Benchmarks may favor certain access patterns
- Real-world workloads are complex
- No standardized benchmark suite

**Current Effort**:
- Academic surveys attempting comprehensive evaluation
- Mixed results: no universally best index

**Limitations**:
- Most research uses specialized or synthetic workloads
- Limited production deployment data
- Reproducibility challenges

### 10. Operational Complexity

**Challenge**: Running learned indexes in production is more complex than traditional indexes.

**Considerations**:
- Model retraining and versioning
- Performance monitoring and alerting
- Fallback mechanisms when models fail
- Debugging unexpected behavior (model black box)
- Version control and experimentation

**Current Solutions**:
- LITune for automatic tuning
- Monitoring frameworks for model performance
- Safety mechanisms and gradual rollout

**Unsolved**:
- Standard operations playbook
- Automated detection of when to retrain
- Integration with existing DBA tools

---

## Future Directions

### 1. Hardware-Aware Learned Indexes

**Direction**: Design learned indexes specifically for modern hardware characteristics.

**Opportunities**:
- SIMD vectorization of model inference
- GPU acceleration of bulk operations
- NVMe/SSD-aware structures
- Cache-aware model design

**Research Challenge**: Models that exploit hardware without sacrificing generality

### 2. Learned Indexes for Approximate Query Processing

**Direction**: Use learned indexes to support approximate answers quickly.

**Idea**: Trade exact answers for faster responses in analytics

**Applications**:
- Approximate count/sum queries
- Approximate distinct count (HyperLogLog-like)
- Sketch-based aggregations

### 3. Federated and Distributed Learned Indexes

**Direction**: Extend learned indexes to distributed systems.

**Challenges**:
- Coordination of models across nodes
- Handling data replication
- Cross-node query optimization
- Network latency implications

**Opportunities**: Google's Bigtable integration could extend to BigQuery and other services

### 4. Transfer Learning and Few-Shot Learning

**Direction**: Reuse models from similar datasets/workloads.

**Idea**: Train on one dataset, quickly adapt to similar datasets

**Applications**:
- New databases that resemble existing ones
- Rapid index construction
- Cross-domain transfer

### 5. Learned Indexes for Time-Series and Temporal Data

**Direction**: Specialized indexes for time-series analysis.

**Opportunities**:
- Learned indexes for financial data
- IoT sensor data indexing
- Event stream indexing

**Challenge**: Temporal patterns and seasonality

### 6. Self-Tuning Databases with Learned Indexes

**Direction**: Integrate learned indexes with autonomous database concepts.

**Idea**: Databases that automatically select, build, and tune learned indexes

**Components**:
- Workload characterization
- Automatic index recommendation
- Performance prediction
- Continuous optimization (LITune-like)

### 7. Vector Search and Neural Embeddings

**Direction**: Learned indexes specialized for vector similarity search.

**Motivation**: Explosion of vector databases (Pinecone, Weaviate, etc.)

**Approach**:
- Learn structure of high-dimensional embedding spaces
- Exploit geometric properties of semantic embeddings
- Combine with traditional ANN techniques (product quantization, locality-sensitive hashing)

### 8. Learned Sketches and Streaming

**Direction**: Combine learned models with stream algorithms.

**Applications**:
- Learned Bloom filters for dynamic streams
- Learned count-min sketches
- Learned frequency estimation

**Challenge**: Online learning under concept drift

### 9. Robustness and Certifiability

**Direction**: Develop learned indexes with provable performance guarantees.

**Goals**:
- Worst-case bounds on query time
- Quantified resilience to adversarial inputs
- Certified memory usage

**Approach**:
- Bounded-error models (like PGM-Index)
- Hybrid structures with safety fallbacks
- Adversarial robustness techniques from ML

### 10. Learned Indexes in Specialized Domains

**Direction**: Develop domain-specific learned indexes.

**Domains**:
- **Graph Databases**: Learned indexes for graph traversal
- **Full-Text Search**: Learned term dictionary and posting lists
- **Spatial-Temporal**: Learned indexes for GPS/location data
- **Genomic Data**: Specialized for DNA sequence matching
- **Legal/NLP**: Semantic learned indexes for document search

---

## Conclusion

Learned index structures represent a fundamental paradigm shift in how we think about data organization. Rather than designing indexes algorithmically, we can learn them from data.

### Key Takeaways

1. **Why It Works**: ML models can exploit data distribution and be more compact and faster than hand-engineered structures on many real-world workloads.

2. **Mature Solutions Exist**: ALEX, PGM-Index, and LIPP demonstrate that fully-dynamic learned indexes are practical and can beat B-Trees significantly.

3. **Multi-Dimensional Extensions**: Flood, Tsunami, and LISA extend learned indexes to spatial data, though this remains more challenging.

4. **Probabilistic Structures**: Learned Bloom filters show how ML can replace traditional probabilistic data structures with massive space savings.

5. **Automation**: LITune demonstrates that automatic tuning can further optimize learned indexes for specific workloads, increasing their practical applicability.

6. **Search Applications**: Learned indexes are directly applicable to search engines (dictionary, posting lists, document ID mapping) but adoption is limited by practical concerns.

7. **PostgreSQL Path**: Integration with PostgreSQL is being explored but remains in research phase; hybrid strategies (learned + traditional) are most practical.

8. **Trade-offs Matter**: Learned indexes excel for read-heavy, stable, in-memory workloads but struggle with write-heavy and adversarial scenarios.

9. **Operations Complexity**: Production deployment requires robust monitoring, retraining, fallback mechanisms, and ML expertise.

10. **Future is Promising**: Hardware-aware variants, distributed systems, vector search, and autonomous databases represent exciting future directions.

### The Verdict

**Are learned indexes ready for mainstream adoption?**

**Answer**: Partially. For specific use cases (read-only caches, embedded systems, specialized analytics), yes. For general-purpose OLTP databases, traditional B-Trees remain safer. The sweet spot is hybrid approaches (learned + traditional) that gain benefits while maintaining safety.

The field is rapidly maturing. As tools like LITune reduce tuning complexity and integration with major systems like PostgreSQL matures, broader adoption is likely within the next 2-3 years.

---

## References & Further Reading

### Foundational Papers

1. [The Case for Learned Index Structures (Kraska et al., 2018)](https://arxiv.org/abs/1712.01208) - The seminal paper that started the field
2. [CDFShop: Exploring and Optimizing Learned Index Structures (Marcus et al., 2020)](https://dl.acm.org/doi/abs/10.1145/3318464.3384706) - Tool for exploring RMI configurations
3. [A Critical Analysis of Recursive Model Indexes (Maltry et al., 2021)](https://arxiv.org/pdf/2106.16166) - Critical examination of RMI limitations

### Key Learned Index Systems

1. [ALEX: An Updatable Adaptive Learned Index (Ding et al., 2020)](https://arxiv.org/abs/1905.08898) - Fully dynamic learned index with gapped arrays
2. [The PGM-index: a fully-dynamic compressed learned index (Ferragina & Vinciguerra, 2020)](https://arxiv.org/abs/1910.06169) - Theoretically optimal recursive linear models
3. [RadixSpline: A Single-Pass Learned Index (Kipf et al., 2020)](https://arxiv.org/abs/2004.14541) - Hybrid radix-spline structure
4. [Updatable Learned Index with Precise Positions (Wu et al., 2021)](https://arxiv.org/abs/2104.05520) - Precise position prediction for learned indexes
5. [LITune: A Reinforcement Learning Enhanced Approach to Tuning Learned Indexes (Wang et al., 2025)](https://arxiv.org/abs/2502.05001) - Automatic tuning via DRL

### Multi-Dimensional Learned Indexes

1. [Flood: Learning Multi-dimensional Indexes (Nathan et al., 2019)](https://arxiv.org/abs/1912.01668) - CDF-based multi-dimensional indexes
2. [Tsunami: A Learned Multi-dimensional Index for Correlated Data (Ding et al., 2020)](https://arxiv.org/abs/2006.13282) - Handles correlations and skewed workloads
3. [LISA: A Learned Index Structure for Spatial Data (Li et al., 2020)](https://dl.acm.org/doi/abs/10.1145/3318464.3389703) - Spatial data specialization
4. [FlexFlood: Efficiently Updatable Learned Multi-dimensional Index (Hu et al., 2024)](https://arxiv.org/abs/2411.09205) - Dynamic variant of Flood
5. [A Survey of Learned Indexes for the Multi-dimensional Space (Aref et al., 2024)](https://arxiv.org/abs/2403.06456) - Comprehensive survey of multi-dimensional approaches

### Learned Bloom Filters & Probabilistic Structures

1. [A Model for Learned Bloom Filters and Related Structures (Mitzenmacher, 2019)](https://arxiv.org/abs/1802.08017) - Theoretical foundations
2. [Learned LSM-trees: Two Approaches Using Learned Bloom Filters (Alves et al., 2024)](https://arxiv.org/abs/2508.00882) - Integration with LSM-trees
3. [Partitioned Learned Bloom Filters (Vaidya et al., 2020)](https://arxiv.org/abs/2006.03176) - For distributed systems

### Learned Indexes in Practice

1. [Evaluating Learned Indexes in LSM-tree Systems: Benchmarks, Insights and Design Choices (2026)](https://arxiv.org/abs/2506.08671) - Real-world integration challenges
2. [Are Updatable Learned Indexes Ready? (Wongkham et al., 2023)](https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf) - Critical evaluation of production readiness
3. [Algorithmic Complexity Attacks on Dynamic Learned Indexes (Matula et al., 2024)](https://arxiv.org/abs/2403.12433) - Security and adversarial concerns
4. [LearnedKV: Integrating LSM and Learned Index for Superior Performance (Wang et al., 2024)](https://arxiv.org/abs/2406.18892) - Integration with key-value stores

### PostgreSQL & Database Integration

1. [Exploring Learned Indexes in PostgreSQL (Evans & Kothari, PGConf.dev 2025)](https://www.postgresql.fastware.com/blog/exploring-learned-indexes-in-postgresql) - Current state and challenges

### Surveys and Overview

1. [Learned Index Structures Overview (Emergent Mind)](https://www.emergentmind.com/papers/1712.01208) - Accessible overview of the field
2. [How good are multi-dimensional learned indexes? An experimental survey (The VLDB Journal, 2024)](https://link.springer.com/article/10.1007/s00778-024-00893-6) - Experimental evaluation and comparison

---

**Last Updated**: March 1, 2026
**Encyclopedia Version**: 1.0
**Field Status**: Active research with increasing practical adoption

