# AI/ML-Powered Search: The Comprehensive Encyclopedia
## From Embeddings to Neural Ranking - Production Guide

**Last Updated:** March 2026
**Document Version:** 1.0
**Status:** Complete Reference Guide

---

## Table of Contents

1. [Vector Embeddings for Search](#vector-embeddings-for-search)
2. [Approximate Nearest Neighbor Search](#approximate-nearest-neighbor-search)
3. [Neural Ranking Models](#neural-ranking-models)
4. [Semantic Search Architecture](#semantic-search-architecture)
5. [Large Language Models for Search](#large-language-models-for-search)
6. [ML Classification for Search Enhancement](#ml-classification-for-search-enhancement)
7. [Production Benchmarks & Trade-offs](#production-benchmarks--trade-offs)
8. [Implementation Guidance](#implementation-guidance)

---

## Vector Embeddings for Search

### What Are Vector Embeddings?

Vector embeddings are continuous, multidimensional numerical representations of text that capture semantic meaning. Instead of treating words as discrete symbols, embeddings represent them as points in high-dimensional space where semantically similar items are located near each other.

**Core Principle:** Semantic similarity is expressed as geometric proximity. Two documents about "machine learning" would have embedding vectors that are close together (low cosine distance), while a document about "cooking recipes" would be far away.

### Historical Evolution

#### Word2Vec (2013)
**How it works:** Word2Vec learns a fixed embedding for each word using two architectures:
- **Skip-gram:** Predicts context words given a target word
- **CBOW:** Predicts target word given context words

**Limitations:**
- Static, context-independent embeddings (word "bank" has same representation in "river bank" and "bank deposit")
- Word-level only (no document understanding)
- Vocabulary-dependent

**Use case:** Historical interest; superseded by contextual models

#### GloVe - Global Vectors for Word Representation (2014)
**Mathematical Foundation:** GloVe combines:
- Local context window approaches (like Word2Vec)
- Global matrix factorization of word co-occurrence statistics

**Core equation:**
```
J = Σ_i,j f(X_ij) (w_i^T w_j + b_i + b_j - log X_ij)²
```

Where `X_ij` is the co-occurrence frequency between words i and j.

**Advantages:**
- Captures global corpus statistics
- Better at semantic tasks than Word2Vec
- Slightly improved generalization

**When to use:** When you have pre-computed co-occurrence statistics and want semantic word relationships without BERT's computational overhead.

**Performance:** Still competitive for simple similarity tasks, but insufficient for modern semantic search.

### Contextual Embeddings - The Modern Era

#### BERT and Transformers
**Fundamental Shift:** BERT generates context-dependent embeddings—the same word gets different vectors based on surrounding context.

**Key difference from Word2Vec/GloVe:**
- "bank" in "river bank" → different embedding
- "bank" in "bank account" → different embedding
- Captures nuanced semantic meaning

**Architecture:** 12-layer transformer with 768 dimensions (base) or 1024 dimensions (large)

**Limitations for search:**
- Designed for classification/NLU, not semantic similarity
- No built-in pooling strategy for sentence embeddings
- Expensive to compute for large-scale retrieval

### Sentence-BERT (SBERT) - The Production Workhorse

**Innovation:** First model to efficiently generate sentence-level embeddings by adding mean pooling + loss function optimization specifically for semantic similarity.

#### all-MiniLM-L6-v2: The Standard Choice

**Specifications:**
- **Dimensions:** 384
- **Size:** 22MB (tiny!)
- **Speed:** 5x faster than all-mpnet-base-v2
- **Training:** Fine-tuned on 1B sentence pairs with batch size 1024
- **Input limit:** 256 word pieces (auto-truncated)

**Performance Profile:**
- Good semantic understanding for general tasks
- Trade-off: 5-10% accuracy loss vs all-mpnet-base-v2
- Excellent for: semantic search, clustering, similarity detection

**Production Considerations:**
```
Embedding size: 384 * 4 bytes (float32) = 1.5 KB per document
For 1M documents: ~1.5 GB storage (plus index overhead)
Query time: ~1-5ms per embedding on CPU
```

**Implementation:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(sentences)  # Returns numpy array
# embeddings.shape = (num_sentences, 384)
```

### Modern Open-Source Frontier

#### BGE-M3 (Baidu's Best General Embeddings)
**Game Changer in 2024:** Achieved commercial-quality results while remaining completely free and open-source.

**Characteristics:**
- **Dimensions:** 1024
- **Context window:** 8192 tokens (enables embedding full articles)
- **Languages:** Exceptional performance on English and Chinese
- **Cost:** Zero (self-hosted)
- **MTEB score:** 63.0 (competitive with proprietary models)

**Unique capability:** Can embed entire documents without chunking, preserving document structure and relationships.

**When to use:** When you need multilingual support or have the infrastructure to self-host, and can afford the slightly larger embedding size.

#### E5 Models - Microsoft's Weak Supervision Approach
**Training Methodology:** Contrastive learning on 270 million text pairs from weak signals

**Variants:**
- **E5-base:** General-purpose, smaller footprint
- **E5-mistral-7b-instruct:** 7B parameters, uses Mistral backbone
  - Uses LLM instructions: "Represent this text for semantic search"
  - Trade-off: Higher compute cost, superior accuracy

**Performance on RAG benchmarks:**
- E5-mistral: 56.9% (best in its category)
- OpenAI-3-large: 55.4%
- Cohere English v3: 55.0%

**Critical advantage:** Instruction-aware—can be optimized for different tasks by changing the instruction prefix.

#### Jina Embeddings v3
**Latest advancement (2025):**
- Multilingual support (100+ languages)
- Code search capabilities
- 0.6B parameters (efficient)
- Novel "last but not late interaction" mechanism

**Production edge:** Optimized for agentic RAG systems with native function-calling support.

### OpenAI's Commercial Embeddings

#### text-embedding-3-small / text-embedding-3-large
**Dimensions:**
- small: 512 (optimized for cost)
- large: 1536 (maximum quality)

**Unique feature: Matryoshka Embeddings** (discussed in depth below)

**Cost Model:**
- Input: $0.02 per 1M tokens
- 15M tokens/month free tier

**Best for:** Prototypes and low-volume applications where managed service and simplicity outweigh cost.

### Cohere embed-v3 (Now embed-v4)

**Performance leader:**
- MTEB score: 65.2 (highest in 2024-2025)
- 100+ language support
- Built-in compression (30-75% size reduction with minimal loss)

**Multilingual strength:** Significantly outperforms competitors on non-English queries.

**Deployment model:** API-only (fully managed)

### Embedding Dimension Trade-offs

**The dimension selection problem:**

| Dimensions | Size/doc | Speed | Accuracy | Use Case |
|-----------|----------|-------|----------|----------|
| 256 | 1 KB | 10x faster | 95-98% | Large-scale retrieval, re-ranking |
| 384 | 1.5 KB | 5x faster | 98-99% | General production (MiniLM) |
| 512 | 2 KB | 3x faster | 99%+ | Balanced approach |
| 768 | 3 KB | 1-2x faster | 99%+ | High accuracy needed |
| 1024 | 4 KB | baseline | 99.5%+ | Premium accuracy (BGE-M3) |
| 1536 | 6 KB | slower | max | Maximum accuracy (OpenAI-3-large) |

**Key insight:** Going from 1536 → 256 dimensions loses only 2-5% accuracy in most cases, while providing 6x speedup.

### Fine-tuning Embeddings for Domain-Specific Search

**When to fine-tune:**
- Generic embeddings perform poorly on your domain (legal, medical, scientific)
- You have labeled pairs of (query, relevant_document)
- Minimum 1000-5000 pairs recommended

**Fine-tuning approaches:**

1. **Contrastive learning:** Minimize distance between relevant pairs, maximize distance between non-relevant
2. **Triplet loss:** Optimize (anchor, positive, negative) triplets
3. **Mean-squared error:** Directly minimize distance to target embeddings

**Example: Medical literature search**
```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import ContrastiveLoss

model = SentenceTransformer('all-MiniLM-L6-v2')
train_examples = [
    InputExample(texts=['diabetes treatment', 'glucose management protocol'], label=0.9),
    InputExample(texts=['diabetes treatment', 'cooking recipes'], label=0.1)
]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
loss = ContrastiveLoss(model)
model.fit(train_objectives=[(train_dataloader, loss)], epochs=5)
```

**Expected improvements:** 10-20% accuracy gain on domain-specific queries.

### Matryoshka Embeddings - Variable Dimensions

**Revolutionary concept:** Encode more important information in early dimensions, less important in later dimensions. This allows flexible dimension reduction.

**How it works:**
- Train the model with loss function that encourages hierarchical information encoding
- At inference: Use first 256 dimensions for fast retrieval, first 1536 for precision reranking
- Each truncated vector is independently valid

**Performance impact:**
- Full (1536 dims): 100% accuracy baseline
- First 512 dims: 99.2% accuracy (67% size reduction)
- First 256 dims: 98.4% accuracy (83% size reduction)

**OpenAI's published results:**
- text-embedding-3-large truncated to 256 dimensions
- Outperforms untruncated text-embedding-ada-002 (1536 dimensions)
- 84% size reduction, superior performance

**Production use case - Funnel Search Architecture:**

```
Phase 1: Initial filtering with first 256 dims
  ├─ Speed: 10x faster
  ├─ Recall: 100% (over-inclusive by design)
  └─ Result: Top 1000 candidates

Phase 2: Re-rank with first 512 dims
  ├─ Speed: 5x faster than full
  ├─ Recall: 99%+
  └─ Result: Top 100 candidates

Phase 3: Final precision with all 1536 dims
  ├─ Speed: baseline
  ├─ Recall: 99.9%
  └─ Result: Top 10 final results
```

**Implementation with OpenAI:**
```python
from openai import OpenAI

client = OpenAI()

# Get full 1536-dimension embedding
full_embedding = client.embeddings.create(
    model="text-embedding-3-large",
    input="sample text"
).data[0].embedding

# Use only first 256 dimensions
truncated = full_embedding[:256]
```

---

## Approximate Nearest Neighbor Search

### The Core Problem

Finding exact nearest neighbors in high-dimensional space has O(n) complexity—for 1 billion vectors, you need 1 billion distance calculations per query. This is infeasible for production systems.

**Solution:** Approximate Nearest Neighbor (ANN) search trades perfect accuracy for dramatic speed improvements.

### HNSW - Hierarchical Navigable Small World

**Why it dominates:** HNSW is the leading ANN approach for high-dimensional vector search across the industry.

#### How HNSW Works

**Core concept:** Multi-layer graph structure inspired by "small world" networks found in social networks.

**Architecture visualization:**

```
Layer 3 (top):     [A]──────────[B]
                    │            │
                    │            │
Layer 2:           [A]──[C]──[B]──[D]
                    │    │    │    │
                    │    │    │    │
Layer 1:      [A]──[C]──[E]──[B]──[D]──[F]
               │    │    │    │    │    │
               │    │    │    │    │    │
Layer 0 (base):[A]──[C]──[E]──[G]──[B]──[D]──[F]──[H]
               (all nodes at bottom, fewer at top)
```

**Search strategy:**
1. Start at top layer with one node
2. Greedily navigate toward query vector (finding nearest node)
3. When no closer node found, move to layer below
4. Repeat until reaching bottom layer
5. Continue greedy search at base layer with larger local neighborhood

**Complexity:**
- Build time: O(n log n) for n vectors
- Search time: O(log n) average case
- Memory: ~1.5-2x the raw vector size

#### Key Parameters

```python
import hnswlib

index = hnswlib.Index(space='cosine', dim=384)

# During build:
index.init_index(
    max_elements=1_000_000,
    ef_construction=200,  # Quality vs build-time trade-off
    M=16                  # Number of connections per node
)

# During search:
labels, distances = index.knn_query(
    query_embedding,
    k=100,
    ef=ef_search  # Quality vs query-time trade-off
)
```

**Parameter tuning:**
- `ef_construction`: Higher = better quality, slower build (typical: 100-400)
- `M`: Higher = better quality, more memory (typical: 12-32)
- `ef_search`: Higher = better quality, slower queries (typical: 10-500)

#### Production Numbers

```
Index build:
  1M vectors (384 dims):     ~30 seconds
  100M vectors:              ~40 minutes
  Memory overhead:           ~2-3 GB for 1M vectors

Query performance:
  Latency (p50):             2-5ms
  Latency (p99):             10-20ms
  Throughput:                100K-500K QPS single machine

Recall vs ef_search:
  ef_search=10:              95% recall, 1ms latency
  ef_search=50:              99% recall, 3ms latency
  ef_search=200:             99.9% recall, 8ms latency
```

### IVF (Inverted File Index) + Product Quantization

#### IVF - Inverted File Partitioning

**Concept:** Partition vector space into clusters, search only relevant clusters.

**How it works:**
1. Train a quantizer (e.g., k-means with k=1000) on sample vectors
2. Assign each vector to nearest cluster
3. For each cluster, maintain an inverted list of vector IDs
4. Search: Find query's cluster, search only that cluster

**Speed improvement:** 10-100x depending on number of clusters

#### Product Quantization (PQ)

**Problem:** Even with IVF, storing full-precision vectors is expensive.

**Solution:** Compress each dimension group independently.

**Example with 384-dim vectors:**
```
Original: 384 floats = 1536 bytes per vector
          (4 bytes * 384)

Split into 8 subspaces:
  Subspace 1: dims 1-48 (48 values)
  Subspace 2: dims 49-96
  ...
  Subspace 8: dims 337-384

Each subspace: Quantize to 8 bits (256 clusters)
Result: 8 bytes (one byte per subspace)
        = 1.5 KB → 8 bytes = 99.5% compression!
```

**Compression ratio:** Can achieve 97% compression with only 2-5% accuracy loss

#### Combined IVF+PQ Performance

From FAISS research:
- IVF alone: 16.5x speedup
- PQ alone: 5.6x speedup
- Combined IVF+PQ: **92x speedup** with preserved accuracy

**Trade-off curve:**

```
Speedup vs Recall (on 1B vector dataset)
Speedup
   ▲
   │     ╱
   │    ╱ ← IVF+PQ
   │   ╱
   │  ╱
   │ ╱──── IVF
   │╱────────── PQ
   └────────────────────────────► Recall
   1x     10x    100x    1000x
```

### ScaNN - Google's Learned Indices Approach

**Key innovation:** Learn the index structure instead of using fixed partitioning.

**Algorithm approach:**
1. **Coarse search:** Learn a model to quickly filter 99% of vectors
2. **Fine-grained search:** Precisely evaluate remaining vectors
3. **SOAR optimization:** Spilling with Orthogonality-Amplified Residuals for improved efficiency

**Advantages over HNSW/IVF:**
- Better for MIPS (Maximum Inner Product Search)
- Anisotropic vector quantization preserves ranking
- Recent SOAR algorithm shows 2-3x improvements

**Integration:** Available in:
- Google Cloud Vertex AI Vector Search
- AlloyDB for PostgreSQL
- TensorFlow and Python APIs

### Annoy - Spotify's Tree-Based Approach

**Historical note:** Spotify used Annoy since 2013 for music recommendations. Recently deprecated in favor of HNSW-based Voyager.

**How Annoy works:**
1. Create multiple random projection trees
2. Each tree partitions space with random hyperplanes
3. Search: Traverse trees to leaf, check nearby nodes

**Key parameters:**
```python
from annoy import AnnoyIndex

index = AnnoyIndex(384, metric='angular')
for i, vector in enumerate(vectors):
    index.add_item(i, vector)

# Build time parameter
index.build(
    n_trees=10  # More trees = better recall, larger index
)

# Search parameters
results = index.get_nns_by_vector(
    query_vector,
    100,  # Number of results
    search_k=1000  # Nodes to inspect (larger = better recall)
)
```

**Performance profile:**
- Better for very high dimensions (>500)
- Slightly slower than HNSW for typical dims (256-1024)
- Good memory footprint
- Main advantage: Simple, single file format

### ANN Algorithms Comparison

```
                  Speed    Recall   Memory   Build Time   Industry Adoption
HNSW              ▓▓▓▓▓    ▓▓▓▓▓    ▓▓▓▓     ▓▓▓▓▓       ▓▓▓▓▓ (Industry standard)
IVF+PQ            ▓▓▓▓▓    ▓▓▓      ▓▓       ▓▓▓          ▓▓▓▓ (FAISS standard)
ScaNN             ▓▓▓▓▓    ▓▓▓▓▓    ▓▓▓      ▓▓           ▓▓▓ (Google infra)
Annoy             ▓▓▓▓     ▓▓▓▓     ▓▓▓▓▓    ▓▓▓▓▓        ▓▓ (Legacy)
```

### FAISS Library - Meta's Production Framework

**What is FAISS:** Massively scalable similarity search library from Meta AI Research.

**Typical usage pattern:**
```python
import faiss

# Create index
index = faiss.IndexFlatL2(384)  # Flat index (exact search)

# Add vectors
vectors = np.random.random((1_000_000, 384)).astype('float32')
index.add(vectors)

# Search
query = np.random.random((1, 384)).astype('float32')
distances, indices = index.search(query, k=10)

# For production: Use HNSW variant
hnsw_index = faiss.IndexHNSWFlat(384, 32)
hnsw_index.add(vectors)
distances, indices = hnsw_index.search(query, k=10)
```

**Index types available:**
- `IndexFlatL2`: Exact search (baseline)
- `IndexFlatIP`: Exact with inner product
- `IndexHNSWFlat`: HNSW with no quantization
- `IndexIVFFlat`: IVF without quantization
- `IndexIVFPQ`: IVF + Product Quantization (production standard)

---

## Neural Ranking Models

### The Two-Stage Retrieval Pipeline

Modern search systems use a two-stage approach:

```
┌─────────────────────────────────────────┐
│ Stage 1: RETRIEVAL (Fast, Approximate)  │
│                                         │
│  Input: Query text                      │
│  Method: Dense embeddings + ANN search  │
│  Output: Top 100-1000 candidates        │
│  Latency: 10-100ms                      │
└─────────────────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────┐
│ Stage 2: RANKING (Slow, Precise)        │
│                                         │
│  Input: Top 100-1000 candidates         │
│  Method: Neural rerankers               │
│  Output: Top 10-50 final results        │
│  Latency: 100-500ms                     │
└─────────────────────────────────────────┘
```

### Bi-Encoders vs Cross-Encoders

#### Bi-Encoders

**Architecture:** Query and document encoded independently, then compared.

```
Query: "machine learning algorithms"
  └─→ [Encoder] → Query embedding (384 dims)
        │
        └─→ Cosine similarity ← Document embedding (384 dims)
                    │
            Document: "deep learning models"
              └─→ [Encoder] → [embedding]
```

**Advantages:**
- Can pre-compute all document embeddings offline
- Fast search with ANN
- Scales to billions of documents
- Lossy comparison (no query-document interaction)

**Performance:** Not as precise as cross-encoders, but reasonable accuracy.

#### Cross-Encoders

**Architecture:** Query and document encoded together, end-to-end scoring.

```
Input: [Query + Document]
  └─→ [BERT encoder] →
        └─→ [Classification head] →
              └─→ Relevance score (0-1)
```

**Key difference:** Preserves query-document interactions throughout the network.

**Advantages:**
- More accurate than bi-encoders (typically 5-10% better MRR)
- Can model complex semantic interactions
- Better for nuanced relevance

**Disadvantages:**
- Must run inference for each candidate
- Cannot pre-compute
- Expensive at scale

**Cost analysis:**
```
Stage 1 (bi-encoder): D documents, 1 embedding per doc
  Cost = D * cost_embedding

Stage 2 (cross-encoder): K rerank candidates, Q queries
  Cost = K * Q * cost_cross_encoder

Total retrieval pipeline cost:
  (D + K*Q) * unit_cost

If Q = 100 QPS, K = 100 reranked, D = 10M docs:
  Cross-encoder: 10M + (100*100) = 10M + 10K = ~10M unit_cost
  Most of cost in preprocessing, not query-time
```

### ColBERT - Late Interaction for Efficiency

**Innovation:** Encode query and document independently (like bi-encoder), but with fine-grained interaction at retrieval time.

**How it works:**

```
Document: "Machine learning is a subset of artificial intelligence"
  └─→ BERT token encoders → [m_l, is, a, subset, ...]
           (no pooling!)

Query: "machine learning algorithms"
  └─→ BERT token encoders → [m_l, algorithms]

Interaction: MaxSim operator
  For each query token embedding:
    Find closest document token embedding
    Take maximum similarity score

  Score = mean(max similarities)
```

**Advantages:**
- ColBERTv2 on FAISS: Near-cross-encoder quality at 1000x speed
- Late interaction: Minimal overhead vs bi-encoder
- Can pre-compute document token embeddings
- Scales to large documents naturally (no length limit)

**Performance vs cross-encoders:**
- ColBERT: ~5-8% slower than best cross-encoders
- Speed: 100-1000x faster

**Practical architecture:**
```
1. Index phase (offline):
   For each document:
     - Tokenize
     - Get BERT token embeddings (128 dims each)
     - Store sparse token embeddings

2. Search phase (online):
   Get query token embeddings
   For each candidate from bi-encoder:
     - Calculate MaxSim between query and doc tokens
     - Rank by MaxSim score
```

### MonoT5 and Sequence-to-Sequence Rerankers

**Different paradigm:** Instead of classification (relevant/not relevant), generate probability distribution.

**How MonoT5 works:**

```
Input: [Query] [SEP] [Document]
  └─→ T5 encoder-decoder
        └─→ Generates: "relevant" or "not relevant"
              └─→ Probability of "relevant" = score
```

**Advantages:**
- Leverages sequence-to-sequence training (more stable)
- Can be fine-tuned on ranking datasets
- Good zero-shot performance
- Training data: MS MARCO passage dataset

**Performance:**
- MonoT5-large: 770M parameters
- Competitive with BERT cross-encoders
- Slightly better zero-shot generalization

### Cohere Rerank

**Production-ready API:**

```python
import cohere

client = cohere.ClientV2(api_key="...")

results = client.rerank(
    model="rerank-english-v3.0",
    query="best machine learning frameworks",
    documents=[
        {"index": 0, "text": "TensorFlow is..."},
        {"index": 1, "text": "PyTorch is..."},
        # ... more documents
    ],
    top_n=10
)
```

**Characteristics:**
- Cross-attention mechanisms for fine-grained ranking
- Multilingual support (100+ languages)
- Handles semi-structured data (emails, tables, JSON, code)
- Built-in compression for efficiency

**Cost:** ~$0.001 per 1000 reranked documents

### Jina Reranker v3

**Latest (2025):**
- 0.6B parameters (extremely efficient)
- Novel "last but not late interaction" architecture
- Multilingual (100+ languages)
- Function-calling support for agentic RAG
- 6x speedup over v1

**API:**
```python
from jina import Client

client = Client()
results = client.rerank(
    "query text",
    documents=[...],
    model="jina-reranker-v3-base-en",
    top_n=10
)
```

### Reranking Architecture Decision Tree

```
Is recall critical?
  ├─ YES → Use cross-encoder (most accurate)
  │        (at highest cost)
  │
  ├─ NO → Is latency critical? (<100ms required?)
  │         ├─ YES → Use Jina Reranker v3 (efficient)
  │         │
  │         └─ NO → Budget for cross-encoder cost?
  │           ├─ YES → Use Cohere Rerank (production)
  │           └─ NO → Use ColBERT (self-hosted, cheaper)
```

---

## Semantic Search Architecture

### Dense Retrieval Pipeline Overview

**Definition:** Dense Retrieval (DR) transforms both queries and documents into continuous, low-dimensional embeddings, then uses approximate nearest neighbor search.

### Full-Stack Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    QUERY PROCESSING                         │
│                                                             │
│  User Query: "machine learning frameworks"                 │
│         │                                                   │
│         ├─→ Query Preprocessing (optional)                 │
│         │    └─ Normalize, clean, expand                   │
│         │                                                   │
│         ├─→ Query Encoding                                 │
│         │    └─ all-MiniLM-L6-v2: 384-dim vector          │
│         │                                                   │
│         └─→ Vector Search (ANN)                            │
│              └─ HNSW index returns top-100 candidates      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   DOCUMENT INDEXING (OFFLINE)               │
│                                                             │
│  Raw Documents                                              │
│         │                                                   │
│         ├─→ Document Chunking                              │
│         │    └─ 512 tokens/chunk, 50-token overlap         │
│         │                                                   │
│         ├─→ Chunk Embedding                                │
│         │    └─ all-MiniLM-L6-v2: 384-dim vectors         │
│         │                                                   │
│         ├─→ ANN Indexing                                   │
│         │    └─ HNSW index built on all chunks             │
│         │                                                   │
│         └─→ Storage                                        │
│              └─ Vector DB (Pinecone/Weaviate/Qdrant)      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    RERANKING (OPTIONAL)                     │
│                                                             │
│  Top-100 candidates from dense retrieval                   │
│         │                                                   │
│         └─→ Cross-Encoder or ColBERT Reranking            │
│              └─ Output: Top-10 final results               │
└─────────────────────────────────────────────────────────────┘
```

### Query Encoding Strategies

#### Simple Encoding
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query = "machine learning frameworks"
embedding = model.encode(query)  # Shape: (384,)
```

**Limitation:** Doesn't capture complex intent. Query "TensorFlow vs PyTorch" loses the comparison aspect.

#### Query Expansion with LLM
```python
# Original query
query = "TensorFlow vs PyTorch"

# Expand with LLM
prompt = f"Generate 3 variations of this search query: {query}"
expanded = llm.generate(prompt)
# Output: [
#   "TensorFlow vs PyTorch performance",
#   "TensorFlow PyTorch comparison features",
#   "PyTorch TensorFlow which is better"
# ]

# Embed all and average
embeddings = model.encode(expanded)  # Shape: (3, 384)
query_embedding = embeddings.mean(axis=0)  # Shape: (384,)
```

**Improvement:** Better coverage of query semantics, especially for multi-faceted queries.

#### HyDE (Hypothetical Document Embeddings)
```python
query = "What is the best deep learning framework?"

# LLM generates hypothetical answer
prompt = f"Generate a document that answers: {query}"
hypothetical_doc = llm.generate(prompt)
# Output: "TensorFlow is a powerful open-source deep learning
#          framework developed by Google. It excels at..."

# Embed the hypothetical document instead
query_embedding = model.encode(hypothetical_doc)
```

**Advantage:** Query gets embedded as if it were a detailed answer, dramatically improving retrieval.

**Benchmark improvements:**
- Standard encoding: 45% recall@10
- Query expansion: 52% recall@10
- HyDE: 64% recall@10

### Document Chunking for Embeddings

#### Fixed-Size Chunking

**Strategy:** Split documents into fixed-size chunks with overlap.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,          # Tokens
    chunk_overlap=50,        # Overlap for context
    separators=["\n\n", "\n", " ", ""]  # Hierarchy
)

chunks = splitter.split_text(long_document)
```

**Typical parameters:**
```
chunk_size:    256-1024 tokens (balance: context vs specificity)
               512 is industry standard
overlap:       50-150 tokens (preserve cross-boundary relationships)
separators:    Use hierarchical separators to keep
               logical units together
```

**Chunk boundary problem:**
```
Original: "...machine learning is a field of AI. Deep learning
           uses neural networks..."

With bad split:
Chunk 1: "...machine learning is a field of AI. Deep learning"
Chunk 2: "uses neural networks..."

With good split (overlap):
Chunk 1: "...machine learning is a field of AI."
         "Deep learning uses..."
Chunk 2: "Deep learning uses neural networks..."
```

#### Semantic Chunking

**Advanced approach:** Group sentences based on semantic similarity.

```python
from semantic_chunkers import StatisticalChunker

chunker = StatisticalChunker(
    encoder=model,  # SBERT model
    threshold=0.5   # Semantic similarity threshold
)

chunks = chunker.chunk(document)
```

**Algorithm:**
1. Encode each sentence with embeddings
2. Calculate similarity between consecutive sentences
3. Split where similarity drops below threshold
4. Respects logical boundaries (paragraphs) naturally

**Advantages:**
- Respects semantic boundaries
- No arbitrary chunk sizes
- Better retrieval performance
- Slightly slower (requires encoding all sentences)

#### Benchmark: Chunking Strategy Impact

```
Standard retrieval: "What is XGBoost?"

Strategy          Chunk Size    Recall@10   Latency
────────────────────────────────────────────────────
Fixed (256)       256           78%         5ms
Fixed (512)       512           82%         6ms
Fixed (1024)      1024          80%         8ms
Semantic          dynamic       85%         12ms
Adaptive          dynamic       87%         10ms
```

**Key insight:** Semantic chunking provides 5-10% recall improvement at minor latency cost.

### Metadata Filtering Combined with Vector Search

#### Pre-filtering vs Post-filtering

```python
# PRE-FILTERING (more efficient)
# Only search documents matching metadata criteria

filtered_ids = db.query(
    filter={
        "source": "arxiv",
        "year": {"$gte": 2020},
        "topic": "machine learning"
    }
)
# Result: 50,000 documents

candidate_vectors = vectors[filtered_ids]
results = hnsw_index.search(query_embedding, k=10)

# Time cost: 50K ANN search


# POST-FILTERING (simpler to code)
# Search all, then filter results

results = hnsw_index.search(query_embedding, k=1000)
final_results = [
    (id, score) for id, score in results
    if metadata[id]["year"] >= 2020
][:10]

# Time cost: 1M ANN search (slower if filtered set is small)
```

**Decision rule:**
- If metadata filters reduce candidate set to <10% → Use pre-filtering
- Otherwise → Use post-filtering for simplicity

#### Multi-Metadata Filtering Pattern

```python
# Typical production scenario
search_results = db.search(
    query_embedding,
    filter={
        "$and": [
            {"document_type": {"$in": ["research", "blog"]}},
            {"publish_date": {"$gte": "2024-01-01"}},
            {"author": {"$ne": "unknown"}},
            {"language": "en"}
        ]
    },
    k=100,
    metadata=["source", "title", "author"]
)
```

### Multi-Vector Search

**Advanced pattern:** Store multiple embeddings per document for different purposes.

```python
# Document: "TensorFlow is a machine learning library"

# Vector 1: General semantic embedding
embedding_1 = general_model.encode(text)  # all-MiniLM

# Vector 2: Domain-specific embedding
embedding_2 = domain_model.encode(text)   # BGE-fine-tuned

# Vector 3: Dense passage retrieval
embedding_3 = dpr_model.encode(text)      # DPR model

# Storage:
db.add_document(
    id="doc-1",
    vectors={
        "semantic": embedding_1,
        "domain": embedding_2,
        "passage": embedding_3
    },
    metadata={...}
)

# Search with multiple vectors
results = db.search(
    {
        "semantic": query_embedding_1,
        "domain": query_embedding_2
    },
    weights={"semantic": 0.6, "domain": 0.4}  # Weighted fusion
)
```

**Use cases:**
- Combine general-purpose and domain-specific embeddings
- Multimodal search (text + image embeddings)
- Different retrieval objectives (exact match + semantic match)

---

## Large Language Models for Search

### LLM-Based Query Expansion

**Core idea:** Use LLMs to rewrite/expand queries before retrieval.

#### Query Rewriting

```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OpenAI(model="gpt-4", temperature=0)

prompt = PromptTemplate(
    input_variables=["query"],
    template="""
    Rewrite the following search query to be more specific and
    include relevant keywords that would help find related documents.
    Original query: {query}
    Rewritten query:
    """
)

chain = LLMChain(llm=llm, prompt=prompt)

original = "what is machine learning"
rewritten = chain.run(original)
# Output: "What is machine learning? Definition, algorithms,
#          applications, and difference from deep learning"
```

**Impact:**
- Original query retrieval: 60% recall@10
- Rewritten query retrieval: 74% recall@10

#### Query Decomposition

```python
query = "Compare machine learning frameworks: TensorFlow, PyTorch, JAX"

# Decompose into sub-queries
prompt = f"""
Break down this complex query into 3-5 simpler search queries:
{query}
"""

sub_queries = llm.generate(prompt)
# Output: [
#   "TensorFlow features and capabilities",
#   "PyTorch features and capabilities",
#   "JAX framework overview",
#   "TensorFlow vs PyTorch comparison",
#   "Best machine learning framework for production"
# ]

# Search for each sub-query independently
all_results = []
for sub_q in sub_queries:
    results = retrieve(sub_q)
    all_results.extend(results)

# Deduplicate and rerank
final_results = rerank_and_deduplicate(all_results)
```

**Benefit:** Handles complex queries better than simple embedding.

### Hypothetical Document Embeddings (HyDE)

**Mechanism:** Generate hypothetical documents that would answer the query, then embed those.

```python
from langchain.llms import OpenAI
from sentence_transformers import SentenceTransformer

llm = OpenAI(model="gpt-3.5-turbo")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def hyde_retrieve(query, k=10):
    # Step 1: Generate hypothetical document
    prompt = f"""
    Imagine a document that would perfectly answer this question.
    Write the content of that hypothetical document.

    Question: {query}
    Document:
    """

    hypothetical = llm.generate(prompt)

    # Step 2: Embed hypothetical document
    query_embedding = embedder.encode(hypothetical)

    # Step 3: Retrieve using embedding
    results = vector_db.search(query_embedding, k=k)

    return results

results = hyde_retrieve("What are the best practices for ML in production?")
```

**Benchmark improvements (on BEIR benchmark):**

```
Method                    NDCG@10    Improvements
──────────────────────────────────────────────────
BM25 (keyword)           35.2%      -
Dense retrieval          46.8%      +32.9%
Dense + Query expansion  51.2%      +45.5%
Dense + HyDE             58.4%      +65.9%
```

**When to use HyDE:**
- Query-document mismatch (query too short/vague)
- Domain-specific datasets where general models underperform
- When you can afford LLM API cost per query

### LLM as Relevance Judge

**Pattern:** Use LLM to score relevance of retrieved documents.

```python
def rerank_with_llm(query, candidates):
    """
    Rerank candidates using LLM judgment.
    """
    results = []

    for doc in candidates:
        prompt = f"""
        Query: {query}
        Document: {doc['content'][:500]}

        Is this document relevant to the query?
        Rate from 0-10 and explain briefly.
        """

        response = llm.generate(prompt)
        score = extract_score(response)  # Extract the 0-10 rating

        results.append((doc, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
```

**Advantages:**
- Can incorporate complex relevance criteria
- Reasoning preserved in explanations
- Good for specialized domains

**Disadvantages:**
- Expensive (LLM inference per candidate)
- Slower (sequential processing)
- Variable quality

**Production use:** Limited to small candidate sets (<100) due to cost.

### Generative Search (RAG)

**Beyond retrieval:** Generate answers with citations.

```python
def rag_search(query):
    # Step 1: Retrieve relevant documents
    retrieved = dense_retrieval(query, k=10)

    # Step 2: Build context from top matches
    context = "\n".join([
        f"[{i}] {doc['title']}\n{doc['content'][:300]}"
        for i, doc in enumerate(retrieved)
    ])

    # Step 3: Generate answer with citations
    prompt = f"""
    Based on these documents, answer the question.
    Include [citation] references to specific documents.

    Documents:
    {context}

    Question: {query}
    Answer:
    """

    answer = llm.generate(prompt)
    return answer

# Output might be:
# "TensorFlow is a popular ML library [0] that excels at
#  production deployment [1]. PyTorch is better for research [2]..."
```

**Quality considerations:**
- Hallucination risk: LLM may cite non-existent documents
- Context window limits: Can't include all retrieved docs
- Latency: Sequential retrieval + generation

### Tool-Augmented Search with Agents

**Pattern:** Agent decides which tools to use for search.

```python
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

tools = [
    Tool(
        name="vector_search",
        func=vector_search,
        description="Search documents by semantic similarity"
    ),
    Tool(
        name="keyword_search",
        func=bm25_search,
        description="Search documents by keywords (exact match)"
    ),
    Tool(
        name="google_search",
        func=google_search,
        description="Search the internet for current information"
    ),
    Tool(
        name="code_search",
        func=code_search,
        description="Search code repositories for examples"
    )
]

agent = initialize_agent(
    tools,
    OpenAI(model="gpt-4"),
    agent="zero-shot-react-description",
    verbose=True
)

response = agent.run(
    "Find example code for TensorFlow model deployment and "
    "recent blog posts about production ML best practices"
)
```

**Agent behavior:**
- Decides which tools fit the query intent
- Chains tool calls if needed
- Combines results from multiple sources
- Adaptive retrieval based on intermediate results

---

## ML Classification for Search Enhancement

### Intent Classification

**Problem:** Different queries need different search strategies.

```
Query: "tensorflow"
  ├─ Navigational intent: Direct to TensorFlow.org
  ├─ Informational: Return tutorials, documentation
  └─ Transactional: Installation guides, API reference

Query distribution across web:
  ├─ Informational: 80%
  ├─ Navigational: 10%
  └─ Transactional: 10%
```

#### Classification Approach

```python
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

query = "how to install tensorflow"

results = classifier(
    query,
    ["navigational", "informational", "transactional"],
    multi_class=False
)

# Output:
# {
#   "labels": ["informational", "transactional", "navigational"],
#   "scores": [0.78, 0.15, 0.07]
# }

intent = results["labels"][0]  # "informational"
```

**Action based on intent:**
```python
if intent == "navigational":
    # Direct to known entities
    results = entity_lookup(query)
elif intent == "transactional":
    # Find action-oriented results (how-to, pricing, docs)
    results = transactional_search(query)
else:  # informational
    # Comprehensive educational results
    results = semantic_search(query, k=20)
```

### Document Category Classification

**Pattern:** Auto-categorize documents for better retrieval.

```python
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

document = "TensorFlow tutorial: Building your first neural network..."

categories = classifier(
    document[:512],  # Classify on first 512 chars
    ["Tutorial", "Research Paper", "API Reference", "Blog Post"],
    multi_class=True
)

# Store categories in metadata
metadata = {
    "document_id": "doc-123",
    "categories": categories["labels"],
    "category_scores": categories["scores"]
}

# Use in search filtering
results = db.search(
    query_embedding,
    filter={"categories": {"$in": ["Tutorial", "Blog Post"]}},
    k=10
)
```

### Named Entity Recognition (NER) for Search

**Pattern:** Extract entities and enable entity-aware search.

```python
from transformers import pipeline

ner = pipeline("ner", model="dbmdz/bert-base-multilingual-cased")

text = "TensorFlow, developed by Google, excels at deep learning."

entities = ner(text)
# Output:
# [
#   {"word": "TensorFlow", "entity": "PRODUCT", "score": 0.99},
#   {"word": "Google", "entity": "ORG", "score": 0.98},
#   {"word": "deep learning", "entity": "CONCEPT", "score": 0.95}
# ]

# Index entity-enriched document
metadata = {
    "organizations": [e["word"] for e in entities if e["entity"]=="ORG"],
    "products": [e["word"] for e in entities if e["entity"]=="PRODUCT"],
    "concepts": [e["word"] for e in entities if e["entity"]=="CONCEPT"]
}

# Entity-based retrieval
results = db.search(
    query_embedding,
    filter={"organizations": "Google"},
    k=10
)
```

### Sentiment-Aware Search

**Pattern:** Consider sentiment when ranking results.

```python
from transformers import pipeline

sentiment_classifier = pipeline("sentiment-analysis")

def search_with_sentiment(query, sentiment_filter=None):
    # Standard retrieval
    candidates = dense_retrieval(query, k=100)

    # Classify sentiment of each result
    for doc in candidates:
        result = sentiment_classifier(doc["content"][:512])
        doc["sentiment"] = result[0]["label"]  # POSITIVE/NEGATIVE
        doc["sentiment_score"] = result[0]["score"]

    # Filter by sentiment if specified
    if sentiment_filter:
        candidates = [
            doc for doc in candidates
            if doc["sentiment"] == sentiment_filter
        ]

    return candidates[:10]

# Positive product reviews only
positive_reviews = search_with_sentiment(
    "tensorflow performance",
    sentiment_filter="POSITIVE"
)
```

**Use case:** Product recommendation, review search, opinion mining.

---

## Production Benchmarks & Trade-offs

### Embedding Model Benchmarks (MTEB Leaderboard 2026)

```
Model Name                Dim   Speed    Cost      MTEB Score
───────────────────────────────────────────────────────────
Cohere embed-v4          1024  medium   $2/1M     65.2
OpenAI-3-large          1536  fast     $0.02/1M  64.6
BGE-M3                  1024  medium   free      63.0
E5-Mistral-7b           768   slow     free      62.8
GTE-Qwen-7b-instruct    384   slow     free      61.9
all-mpnet-base-v2       768   fast     free      59.3
all-MiniLM-L6-v2        384   fastest  free      57.8
```

**Cost-performance trade-off:**

```
Quality (MTEB)
    │
    │   Cohere(+$) ●
    │      ●OpenAI
    │         ●BGE
    │           ●E5
    │              ●GTE
    │                 ●all-mpnet
    │                    ●all-MiniLM
    │
    └────────────────────────────────► Speed (inferences/sec/core)
       1K      10K      100K     1M
```

### ANN Algorithm Performance

**Benchmark: 1 million 768-dim vectors from SIFT1M dataset**

```
Algorithm       Build Time   Build Memory   Query Latency   Recall@10
───────────────────────────────────────────────────────────────────
HNSW            45 sec       2.1 GB         4.2ms           99.5%
IVF+PQ          120 sec      1.2 GB         12.8ms          98.2%
ScaNN           90 sec       1.8 GB         3.1ms           99.8%
Annoy           180 sec      2.8 GB         8.5ms           97.1%
Flat (exhaustive) -         3.0 GB         2100ms          100%
```

**Key insights:**
- HNSW dominates for general use (balanced)
- ScaNN best for pure speed (Google infrastructure)
- IVF+PQ best for storage constraints
- Annoy adequate but superseded by HNSW

### Search Pipeline Latency Breakdown

**Typical 2-stage retrieval system:**

```
Dense Retrieval Stage:
  Query encoding:              3-5ms    (on GPU)
  ANN search (top-100):        4-8ms    (HNSW)
  Subtotal:                    7-13ms   ✓ (sub-20ms target)

Reranking Stage (if enabled):
  Cross-encoder inference:     50-200ms per batch
                               (for 100 candidates)
  Final ranking:               2-5ms
  Subtotal:                    52-205ms ✗ (expensive!)

Total pipeline:                59-218ms

  If skip reranking:           7-13ms ✓
```

**Optimization strategies:**

```
Strategy                              Impact on Latency
──────────────────────────────────────────────────────
Use smaller embedding (256 vs 1536)   3x speedup
Use ColBERT instead of cross-encoder  10-20x speedup
Batch reranking (e.g., 10 queries)    10x speedup
GPU acceleration                      2-5x speedup (retrieval)
                                      5-20x speedup (reranking)
Use lighter model (Jina v3)           2-3x speedup (vs full)
```

### Accuracy-Cost Trade-offs

```
Scenario: E-commerce product search (1M products, 100K QPS)

Strategy 1: Dense Retrieval Only
  Setup: all-MiniLM-L6-v2 + HNSW
  Accuracy: 78% (MRR@10)
  Cost: $0 + $50/month infra
  Latency: 8ms

Strategy 2: Dense + ColBERT Reranking
  Setup: all-MiniLM + ColBERT
  Accuracy: 85% (+7%)
  Cost: $0 + $200/month infra (GPU)
  Latency: 45ms

Strategy 3: Dense + Cross-Encoder Reranking
  Setup: all-MiniLM + Cross-Encoder
  Accuracy: 87% (+2% more)
  Cost: $0 + $400/month infra
  Latency: 120ms

Strategy 4: BGE-M3 + Cohere Rerank
  Setup: BGE-M3 + Cohere API
  Accuracy: 89% (+2% more)
  Cost: $5000/month API + $200 infra
  Latency: 150ms

Cost-per-1K-queries:
  Strategy 1: ~$0.01
  Strategy 2: ~$0.10
  Strategy 3: ~$0.20
  Strategy 4: ~$2.50
```

---

## Implementation Guidance

### Getting Started: Minimal Viable Search System

**Stack recommendation for prototyping:**

```
Components:
├─ Embedding model:    all-MiniLM-L6-v2 (free, self-hosted)
├─ Vector DB:          Weaviate/Milvus (open-source)
├─ ANN algorithm:      HNSW (built into Weaviate)
└─ Reranking:         Optional (skip for MVP)

Python implementation:
"""

from sentence_transformers import SentenceTransformer
import weaviate
from weaviate.classes.query import MetadataQuery

# 1. Initialize model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Connect to Weaviate
client = weaviate.connect_to_local()

# 3. Create schema
client.collections.create(
    name="Documents",
    properties=[
        weaviate.classes.config.Property(
            name="content",
            data_type=weaviate.classes.config.DataType.TEXT,
        ),
        weaviate.classes.config.Property(
            name="source",
            data_type=weaviate.classes.config.DataType.TEXT,
        ),
    ],
    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
)

# 4. Index documents
collection = client.collections.get("Documents")
for doc in documents:
    embedding = model.encode(doc["text"])
    collection.data.insert(
        properties={
            "content": doc["text"],
            "source": doc["source"]
        },
        vector=embedding
    )

# 5. Search
query = "machine learning"
query_embedding = model.encode(query)
results = collection.query.near_vector(
    near_vector=query_embedding,
    limit=10,
    where=MetadataQuery.by_property("source").equal("arxiv")
)

print(results)
```

### Production-Grade Architecture

**Recommended stack for 10M+ documents:**

```
┌─────────────────────────────────────────────┐
│            Query Layer                      │
│  (Load balancer, rate limiting, caching)   │
└──────────┬──────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────┐
│         Encoding Service                    │
│  (GPU-accelerated, batched encoding)        │
│  - all-MiniLM for dense retrieval           │
│  - Optional: BGE for high-precision         │
└──────────┬──────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────┐
│      Vector Database (Pinecone/Weaviate)    │
│  - HNSW index for fast retrieval            │
│  - Metadata filtering                       │
│  - SLA: <10ms for top-100                   │
└──────────┬──────────────────────────────────┘
           │
      ┌────┴────┐
      │          │
┌─────▼──┐  ┌───▼────────────────────┐
│Optional│  │  Reranking Service      │
│Caching │  │  (GPU-intensive)        │
│Layer   │  │  - ColBERT or           │
│        │  │    Cross-Encoder        │
└────────┘  └────────────────────────┘

Cost estimate (1M documents, 100K QPS):
├─ Vector DB: $500-2000/month
├─ Encoding GPUs: $800-1500/month
├─ Reranking GPUs: $1500-3000/month (if enabled)
└─ Total: $2800-6500/month
```

### Evaluation Framework

**Metrics to track:**

```python
def evaluate_search(queries, gold_standard_rankings):
    """
    Gold standard: Human-annotated rankings for test queries
    """

    mrr_scores = []
    recall_at_k_scores = {10: [], 50: [], 100: []}

    for query, gold_docs in zip(queries, gold_standard_rankings):
        # Get system rankings
        results = search(query, k=100)
        retrieved_ids = [r["id"] for r in results]

        # MRR: Mean Reciprocal Rank
        gold_set = set(gold_docs)
        rank_of_first_relevant = None
        for rank, doc_id in enumerate(retrieved_ids, 1):
            if doc_id in gold_set:
                rank_of_first_relevant = rank
                break

        if rank_of_first_relevant:
            mrr_scores.append(1 / rank_of_first_relevant)
        else:
            mrr_scores.append(0)

        # Recall@K
        for k in [10, 50, 100]:
            relevant_in_top_k = len(
                set(retrieved_ids[:k]) & gold_set
            )
            recall = relevant_in_top_k / len(gold_set)
            recall_at_k_scores[k].append(recall)

    # Aggregate
    print(f"MRR: {sum(mrr_scores) / len(mrr_scores):.3f}")
    for k in [10, 50, 100]:
        avg_recall = sum(recall_at_k_scores[k]) / len(queries)
        print(f"Recall@{k}: {avg_recall:.3f}")
```

**Target metrics:**
```
E-commerce: MRR > 0.7, Recall@10 > 0.85
FAQ Search: MRR > 0.8, Recall@10 > 0.90
Academic: MRR > 0.6, Recall@20 > 0.70
Legal: MRR > 0.75, Recall@5 > 0.95
```

### Common Pitfalls & Solutions

**Problem 1: Poor retrieval on short queries**
```
Query: "tensorflow"
Causes: Single word, no context
Solutions:
  ├─ Query expansion with LLM
  ├─ HyDE (generate hypothetical docs)
  └─ Intent classification → specialized search
```

**Problem 2: Chunking boundaries cut semantic units**
```
Chunk 1: "Machine learning is a field of AI."
         "It includes..."
Chunk 2: "...deep learning..."

Solution: Use semantic chunking or increase overlap
```

**Problem 3: Embedding dimension mismatch between stages**
```
Dense retrieval: 384 dims (all-MiniLM)
Reranker input: Expects token embeddings, not pooled

Solution: Store token embeddings for ColBERT
          or use models compatible in pipeline
```

**Problem 4: Outdated document index**
```
Problem: Index built once, documents change frequently
Solution:
  ├─ Incremental updates (add new documents)
  ├─ Scheduled full rebuilds (nightly)
  └─ Cache layer for recent documents
```

---

## Advanced Topics

### Hybrid Search - Combining Sparse and Dense

**Why hybrid works:** Sparse (BM25) finds exact keywords, dense finds semantic matches.

```
Query: "python machine learning library"

Dense retrieval results:
  1. TensorFlow documentation        (semantic match)
  2. PyTorch tutorial                (semantic match)
  3. ML course overview              (semantic match)

BM25 results:
  1. "Python ML library comparison"  (keyword match)
  2. "scikit-learn python"           (keyword match)
  3. "machine learning libraries"    (keyword match)

Hybrid (weighted fusion):
  1. TensorFlow docs (0.7*dense + 0.3*bm25 score)
  2. PyTorch (0.7*dense + 0.3*bm25 score)
  3. "Python ML library comparison" (complement from BM25)
```

### Vector Quantization - Beyond Product Quantization

**Scalar quantization:** 32-bit float → 8-bit int (75% compression)
**Product quantization:** Compress dimension subgroups independently
**Binary quantization:** Full vectors → 1 bit per dimension (32x compression!)

```
vector = [0.45, -0.23, 0.78, ...]  (384 floats = 1536 bytes)
binary  = [1, 0, 1, 0, ...]        (384 bits = 48 bytes!)
recovery: 97% similarity preserved
```

### Approximate Matching at Query Time

**Scenario:** User types slowly, want real-time suggestions

```
"m"      → no results (too generic)
"ma"     → ["machine learning", "machine vision", ...]
"mac"    → ["machine learning", "Mac M1 benchmarks"]
"mach"   → ["machine learning"] ← Most likely intent
```

**Implementation with prefix search + semantic:**
```python
def autocomplete_search(partial_query):
    # Fast: Prefix matching on titles
    prefix_matches = trie.search_prefix(partial_query)

    # Slow: If few results, use semantic
    if len(prefix_matches) < 5:
        embedding = model.encode(partial_query)
        semantic_matches = vector_db.search(embedding, k=5)
        return prefix_matches + semantic_matches

    return prefix_matches[:10]
```

---

## Conclusion

Modern semantic search combines:

1. **High-quality embeddings** (BGE, E5, OpenAI)
2. **Efficient ANN indexing** (HNSW in production)
3. **Smart reranking** (ColBERT for scale, Cross-encoders for precision)
4. **LLM augmentation** (HyDE for retrieval, answer generation)
5. **Intelligent filtering** (metadata, intent classification)

**For most applications (2026 best practices):**

```
MVP/Prototype:
  └─ all-MiniLM-L6-v2 + HNSW + Weaviate

Production:
  ├─ Dense: BGE-M3 or all-MiniLM
  ├─ ANN: HNSW (production databases)
  ├─ Reranking: ColBERT (if budget allows)
  └─ Augmentation: Query expansion or HyDE

Enterprise:
  ├─ Dense: BGE-M3 + fine-tuned for domain
  ├─ ANN: HNSW with GPU acceleration
  ├─ Reranking: Cross-encoder + Cohere Rerank
  ├─ Augmentation: Full LLM pipeline with agents
  └─ Monitoring: A/B testing, user feedback loops
```

The future of search is **hybrid, augmented, and adaptive**—combining classical ranking with neural approaches, enriched by LLM intelligence.

---

## References & Further Reading

### Embedding Models
- [Vector Embeddings Guide - Meilisearch](https://www.meilisearch.com/blog/what-are-vector-embeddings)
- [Sentence Transformers Documentation](https://sbert.net/)
- [Matryoshka Embeddings - Hugging Face](https://huggingface.co/blog/matryoshka)
- [all-MiniLM-L6-v2 - Hugging Face](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Best Embedding Models 2026 Comparison](https://elephas.app/blog/best-embedding-models)

### Approximate Nearest Neighbors
- [HNSW - Pinecone Learn](https://www.pinecone.io/learn/series/faiss/hnsw/)
- [HNSW - Wikipedia](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world)
- [HNSW - Redis Blog](https://redis.io/blog/how-hnsw-algorithms-can-improve-search)
- [FAISS Documentation](https://faiss.ai/index.html)
- [Product Quantization - Pinecone](https://www.pinecone.io/learn/series/faiss/product-quantization/)
- [ScaNN - Google Research](https://zilliz.com/learn/what-is-scann-scalable-nearest-neighbors-google)
- [Annoy - Zilliz Learn](https://zilliz.com/learn/what-is-annoy)

### Neural Ranking
- [ColBERT and Late Interaction - Medium](https://medium.com/@aimichael/cross-encoders-colbert-and-llm-based-re-rankers-a-practical-guide-a23570d88548)
- [Cross-Encoder Reranking - OpenAI Cookbook](https://cookbook.openai.com/examples/search_reranking_with_cross-encoders)
- [Reranking Models 2026 Guide - ZeroEntropy](https://www.zeroentropy.dev/articles/ultimate-guide-to-choosing-the-best-reranking-model-in-2025)
- [MonoT5 Reranker - PyTerrier Docs](https://pyterrier.readthedocs.io/en/latest/neural.html)
- [Jina Reranker v3](https://jina.ai/reranker/)

### Semantic Search Architecture
- [Hybrid Search Guide - Elastic](https://www.elastic.com/what-is/hybrid-search)
- [Dense Retrieval Principles](https://iterate.ai/ai-glossary/dense-retrieval)
- [Chunking Strategies - Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Metadata Filtering in RAG - Zilliz](https://zilliz.com/blog/metadata-filtering-hybrid-search-or-agent-in-rag-applications)

### LLM for Search
- [HyDE Documentation - Haystack](https://docs.haystack.deepset.ai/docs/hypothetical-document-embeddings-hyde)
- [HyDE - Zilliz Learn](https://zilliz.com/learn/improve-rag-and-information-retrieval-with-hyde-hypothetical-document-embeddings)
- [Query Expansion with LLM - Medium](https://medium.aiplanet.com/advanced-rag-improving-retrieval-using-hypothetical-document-embeddings-hyde-1421a8ec075a)

### ML Classification
- [Search Intent Classification Guide](https://topicalmap.ai/blog/auto/search-intent-classification-methods-2026)
- [Determining Web Query Intent - ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S030645730700163X)

---

**Document created:** March 2026
**Comprehensive research completion date:** March 1, 2026
**Status:** Production-ready reference
**Target audience:** ML engineers, search architects, AI practitioners
