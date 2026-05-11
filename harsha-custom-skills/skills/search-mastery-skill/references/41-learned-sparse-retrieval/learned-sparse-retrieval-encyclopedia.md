# Learned Sparse Retrieval: A Comprehensive Encyclopedia

## Table of Contents

1. Introduction & Historical Context
2. The Gap Between BM25 and Dense Embeddings
3. SPLADE Architecture Deep Dive
4. Evolution of SPLADE (v1, v2, DistilSPLADE, v3, CSPLADE)
5. Sparse Autoencoders for Retrieval (SPLARE)
6. Decoder-Only LLM Approaches (Echo-Mistral-SPLADE)
7. Benchmark Results and Comparisons
8. Production Deployment and Integration
9. Sparse-Dense Hybrid Strategies
10. Domain-Specific Applications
11. When to Use Learned Sparse Retrieval
12. Implementation Guide and Code Examples
13. Future Directions and Research Challenges

---

## 1. Introduction & Historical Context

### What is Learned Sparse Retrieval?

Learned Sparse Retrieval (LSR) is an approach to Information Retrieval that uses sparse vector representations of queries and documents, borrowing techniques from both traditional lexical bag-of-words methods and modern vector embedding algorithms. Unlike dense embeddings that produce continuous values across all dimensions, sparse representations produce mostly zeros with a small number of non-zero values, each typically representing the importance weight of a specific term or learned feature.

The field emerged from a fundamental observation: traditional lexical retrieval systems like BM25 are highly efficient and interpretable, while modern dense embeddings capture semantic meaning but at a computational cost. LSR attempts to bridge this gap by learning sparse representations that are both semantically aware and computationally efficient.

### Historical Timeline

- **2015-2019**: Dense retrieval becomes popular with word embeddings and neural ranking models, but computational costs remain high
- **July 2021**: SPLADE published at SIGIR 2021, introducing sparse lexical and expansion models as a solution to combine benefits of both approaches
- **September 2021**: SPLADE v2 released with significant distillation and efficiency improvements
- **2022**: DistilSPLADE and other variants published, showing benefits of cross-encoder distillation and hard negative mining
- **March 2024**: SPLADE-v3 released with ensemble teacher distillation, achieving state-of-the-art results
- **August 2024**: Mistral-SPLADE published, extending SPLADE to decoder-only LLMs with echo embeddings
- **April 2025**: CSPLADE published, enabling 8B scale LLMs for sparse retrieval with causal architectures

---

## 2. The Gap Between BM25 and Dense Embeddings: Why Learned Sparse Retrieval Exists

### The BM25 Problem

BM25 (Best Matching 25) has been the gold standard for lexical retrieval for decades. It uses term frequency and inverse document frequency (TF-IDF) to rank documents:

**Advantages:**
- Exact keyword matching ensures relevant documents are found
- Extremely fast: O(k) complexity where k is the number of matching terms
- Interpretable: you can see exactly which terms contributed to ranking
- Works with inverted indexes, enabling trillion-scale corpora
- Robust generalization across domains

**Limitations:**
- No semantic understanding: "cancer" and "tumor" are treated as completely different terms
- Synonym/paraphrase gap: queries with different phrasings may miss relevant documents
- Out-of-vocabulary problem: new or rare terms have zero representation
- Needs explicit query expansion for complex information needs

### The Dense Embedding Problem

Dense embeddings from models like ANCE, TCT-ColBERT, and modern foundation models address BM25's semantic limitations:

**Advantages:**
- Semantic matching: understands synonyms, paraphrases, and conceptual relationships
- Learned expansion: can infer relevant concepts beyond literal text matching
- Single semantic space: all documents and queries project to the same space

**Limitations:**
- Computational cost: dot product between dense vectors is O(d) where d is embedding dimension (768+)
- Memory inefficiency: storing 768-dimensional vectors for billions of documents is expensive
- Index incompatibility: dense representations don't work with traditional inverted indexes
- Out-of-domain performance: models trained on MS MARCO often underperform on BEIR datasets
- Latency: cannot use dynamic pruning techniques available in lexical search

### Benchmark Evidence of the Gap

**MS MARCO Passage Ranking (In-Domain):**
- BM25: 0.184 MRR@10
- ANCE (dense): 0.330 MRR@10
- SPLADE: 0.322 MRR@10 (0.96x efficiency of dense, 1.75x better than BM25)

**BEIR Benchmark (Out-of-Domain, Average NDCG@10):**
- BM25: Strong baseline, varies by dataset
- Dense retrievers: Often underperform BM25 due to domain shift
- SPLADE-v2: Outperforms BM25 on most datasets while maintaining efficiency

### Why Sparse Representations Work

Learned sparse representations exploit a key insight: relevance can be computed using dot products over extremely sparse vectors. If a document has only 100 non-zero dimensions out of 30,000, the computation is 300x faster than dense retrieval with 768 dimensions.

The secret is that sparse representations learned through neural models capture both:
1. **Exact matching information**: high weights for in-vocabulary terms related to the query
2. **Semantic expansion**: non-zero weights for semantically related terms the model learned are relevant
3. **Term importance**: weights reflect how important each term is, unlike binary vocabulary representations

---

## 3. SPLADE Architecture Deep Dive

### Core Components

SPLADE (Sparse Lexical and Expansion Model) is a sparse bi-encoder model based on BERT that learns to produce sparse representations of both queries and documents. The architecture consists of three main components:

#### 3.1 BERT Encoder

SPLADE uses a BERT-based masked language model (MLM) as its foundation:
- Bidirectional transformer-based encoder
- Processes full query or document as input
- Output: hidden states for each token and final [CLS] token representation

#### 3.2 MLM Head with Sparse Regularization

The innovation lies in how SPLADE uses BERT's MLM head:

```python
# Conceptual architecture
input_text = "lung cancer tumor treatment"
bert_hidden = bert_encoder(input_text)  # [seq_len, hidden_dim]

# MLM head produces logits for vocabulary positions
mlm_logits = mlm_head(bert_hidden)  # [seq_len, vocab_size]

# Apply ReLU to ensure non-negative weights
term_weights = relu(mlm_logits)  # [seq_len, vocab_size]

# Pool across all tokens (sum or max)
sparse_vector = sum_pool(term_weights)  # [vocab_size]

# Optional L1/FLOPS regularization to induce sparsity
regularization_loss = l1_norm(sparse_vector)
```

The key insight: BERT's MLM head is excellent at predicting contextually relevant tokens. When given masked input tokens, it assigns high logits to semantically similar words. SPLADE leverages this for term expansion.

#### 3.3 Sparsity Regularization

SPLADE does not naively minimize MSE on all vocabulary positions. Instead, it uses explicit regularization to make representations sparse:

**FLOPS Regularization (First-stage Ranking Loss):**
```
L_FLOPS = w̄(q) · w̄(q) + w̄(d) · w̄(d)
where w̄ = mean absolute weight across the vocabulary
```

This regularization forces the model to concentrate importance on a small number of terms rather than spreading weight across the vocabulary.

**Log-Saturation Effect:**
Instead of linear scaling of term weights, SPLADE uses:
```
weight = log(1 + relu(logit))
```

This compresses the dynamic range, making less important terms negligible and highly sparse.

### How SPLADE Learns Expansion

The mechanism for semantic expansion is elegant:

1. **Input**: "cancer prevention strategies"
2. **BERT processes the full context**: understands that cancer relates to oncology, treatment, etc.
3. **MLM head predicts**: high logits for "cancer", "tumor", "oncology", "treatment", "prevention", "strategies"
4. **After regularization**: top weighted terms are "cancer" (0.8), "tumor" (0.6), "treatment" (0.5), "prevention" (0.4)
5. **Sparse vector**: only 4 non-zero dimensions out of 30,522, representing both literal and semantic matches

This is fundamentally different from BM25 which has exactly 4 binary dimensions (only 0 or 1 for presence).

### Query vs Document Encoding

SPLADE-v2 introduced separate encoders for queries and documents:

**Query Encoder:**
- Uses smaller regularization strength (more expansion)
- Can use smaller BERT variant for speed
- Produces 50-100 non-zero dimensions on average

**Document Encoder:**
- Uses stronger regularization (more compression)
- Produces 200-400 non-zero dimensions on average
- Enables pre-computation and static pruning

This separation acknowledges that queries and documents have different characteristics and different efficiency requirements.

### Training Objectives

SPLADE is trained end-to-end with a contrastive learning objective:

```
L_ranking = -log(exp(s(q, d+)) / Σ_d exp(s(q, d)))
```

Where:
- `s(q, d)` = cosine similarity of sparse vectors
- `d+` = relevant document
- The sum is over positive and negative documents in the batch

The regularization term is added during training:

```
L_total = L_ranking + λ * L_FLOPS
```

The hyperparameter λ controls the sparsity-effectiveness tradeoff:
- High λ: very sparse but fewer relevant terms → lower recall
- Low λ: denser representations but less efficient → slower retrieval

---

## 4. Evolution of SPLADE: From v1 to CSPLADE

### SPLADE v1 (July 2021)

**Publication:** SIGIR 2021, short paper

**Key Contributions:**
- First formulation of sparse neural retrieval using MLM expansion and regularization
- Simple, single-stage training approach
- Achieves 0.322 MRR@10 on MS MARCO (competitive with ANCE at 0.330)
- Introduces FLOPS regularization

**Performance:**
- MS MARCO: 0.322 MRR@10 (state-of-the-art sparse method at publication)
- BEIR: Strong performance on out-of-domain tasks, often beating BM25

**Limitations:**
- Single encoder for queries and documents (suboptimal efficiency)
- No distillation (learns from training signal only)
- Limited expansion capability

### SPLADE v2 (September 2021)

**Publication:** SIGIR 2022 short paper, full version in journal

**Major Improvements:**

1. **Separated Encoders**
   - Different BERT models for queries and documents
   - Query encoder: smaller/faster, more expansion
   - Document encoder: pre-computed offline

2. **Distillation Training**
   - Uses cross-encoder scores as supervision signal
   - Trained on hard negatives selected from the model itself
   - Iterative training: model generates candidates, cross-encoder scores them, next iteration trains with those scores

3. **Efficiency Optimizations**
   - L1 regularization on queries instead of FLOPS (queries need to be sparse, not balanced)
   - Faster pooling mechanisms
   - FLOPS-regularized middle training phase

4. **Document-Only Version (SPLADE-doc)**
   - Eliminates query encoding cost for inference
   - Pre-computes all document term weights offline
   - Ranking becomes simple term overlap + pre-computed weights

**Performance:**
- MS MARCO: 40+ MRR@10 (significant improvement over v1)
- BEIR: 2% improvement in out-of-domain effectiveness
- Efficiency: <4ms latency, comparable to BM25 with similar effectiveness

**Index Size:**
- Approximately 8-12 bytes per stored weight
- Full MS MARCO index: ~150GB (compared to ~40GB for BM25, ~135GB for flat dense index)

### DistilSPLADE (2022)

**Key Innovation:** Hard Negative Mining with Cross-Encoder Denoising

**Architecture:**
1. Use SPLADE-v2 to retrieve top-k candidates for each query
2. Score with cross-encoder to identify hard negatives
3. Filter out false negatives using cross-encoder confidence
4. Train new SPLADE model with hard negatives

**Why This Matters:**
Hard negatives are critical for learning good sparse representations. A hard negative is a document that:
- Doesn't contain the answer (negative label)
- Is ranked highly by the current model
- Is hard to distinguish from positive documents

Without careful filtering, you get false negatives (documents labeled negative that should be positive), which introduces noise.

The cross-encoder filtering approach:
- Uses a strong re-ranker to validate hard negatives
- Only includes hard negatives with high cross-encoder confidence
- Balances hard negatives with easier negatives to avoid only-negatives training

**Performance:**
- DistilSPLADE-CoCondenser: Improved performance over SPLADE-v2
- Better generalization on BEIR
- Reduced training time through efficient hard negative mining

### SPLADE v3 (March 2024)

**Publication:** arXiv 2403.06789

**Key Innovation:** Ensemble Teacher Distillation

**Architecture:**
1. Train ensemble of 3-5 cross-encoder models on MS MARCO
2. Use ensemble to generate distillation scores (average of multiple models)
3. Combine KL-Divergence and MarginMSE losses with learned weights
4. Train SPLADE model to match ensemble predictions

**Why Ensemble Teachers?**
- Single cross-encoder can have biases or errors
- Ensemble averages out individual model quirks
- More robust distillation signal
- Better generalization

**Training Process:**
```
For each query:
  - Retrieve top-1000 candidates with SPLADE-v2
  - Score with ensemble of cross-encoders: CE1, CE2, CE3, ...
  - Average scores: ensemble_score = mean(CE1(q,d), CE2(q,d), ...)
  - Train SPLADE to predict ensemble_scores

Loss function:
  L = α * KL(SPLADE_scores || ensemble_scores) + β * MarginMSE
```

**Performance:**
- MS MARCO: >40 MRR@10 (statistically significant improvement)
- BEIR: 2% improvement over SPLADE-v2
- Statistical significance: confirmed on multiple test sets

**Efficiency:**
- Maintained efficiency of v2
- Same latency and index size
- Better quality at same computational cost

### CSPLADE (April 2025)

**Publication:** AACL 2025, Amazon Science

**Major Innovation:** Causal Language Models for Sparse Retrieval

**Challenge Being Solved:**
Training sparse retrievers with large language models (8B scale) has two problems:
1. Training instability: contrastive learning on LLMs diverges early in training
2. Unidirectional attention: decoder-only models can't see future tokens, limiting expansion capability

**Key Contributions:**

1. **Lightweight Adaptation Training**
   - Pre-training phase to stabilize training
   - Reduces divergence issues
   - Enables effective contrastive learning

2. **Bidirectional Variants**
   - VAR (Variant A - Reversing): reverse document sequence to enable causal attention on past tokens
   - VAR (Variant B - Duplicating): duplicate sequence so all tokens see full context
   - Both maintain causal structure while enabling better expansion

**Architecture:**
```
Input: "cancer treatment options for patients"

Variant A (Reversing):
  Input to LLM: "patients for options treatment cancer"
  Causal attention can now look backward in original sequence

Variant B (Duplicating):
  Input to LLM: "cancer treatment options for patients cancer treatment options for patients"
  Take mean of both occurrence representations
  All tokens see full context
```

**Performance:**
- MS MARCO: 41.3 MRR@10 (competitive with smaller dense models)
- BEIR: 55.3 NDCG@10
- Index Size: <8GB for MS MARCO (vs 135GB for flat dense index)
- Model Scale: First to enable 8B LLMs for sparse retrieval

**Why This Matters:**
- Larger models (8B vs 7B BERT) bring better semantic understanding
- Maintains index efficiency of sparse retrieval
- Opens path to even larger models (13B, 70B) for sparse retrieval

---

## 5. Sparse Autoencoders for Retrieval (SPLARE)

### What Are Sparse Autoencoders?

Sparse Autoencoders (SAEs) are neural network components that learn to decompose dense representations into interpretable sparse features. Unlike projection into a fixed vocabulary (like BERT's 30K vocabulary), SAEs learn a learned feature space.

**SAE Architecture:**
```
Dense embedding (768D)
  ↓
Linear projection (768 → 4096 or higher)
  ↓
ReLU activation
  ↓
Sparse latent representation (sparse in 4096D)
  ↓
Linear reconstruction (sparse latent → 768D)
```

The SAE is trained to reconstruct the original dense embedding from sparse activations, learning which features are important for capturing the meaning of text.

### SPLARE: SAE-based Learned Sparse Retrieval

**Publication:** Recent work addressing limitations of vocabulary-based sparse retrieval

**Key Differences from SPLADE:**

| Aspect | SPLADE | SPLARE |
|--------|--------|--------|
| **Feature Space** | Fixed vocabulary (30K) | Learned latent features (4K-16K) |
| **Sparsity** | Sparse over vocabulary | Sparse over latent space |
| **Multilinguality** | English-focused | Multilingual-friendly |
| **Domain Transfer** | Good but vocabulary-limited | Better out-of-domain |
| **Interpretability** | High (vocabulary terms) | Medium (learned features) |
| **Feature Count** | 100-400 per document | 40-400 per document |

**How SPLARE Works:**

1. **Dense Embedding Generation**
   - Use pre-trained multilingual LLM (e.g., Mistral-7B)
   - Extract hidden states from specific layer
   - Result: 768D dense embedding per document

2. **SAE Projection**
   - Pass through learned sparse autoencoder
   - Learn which latent features activate strongly
   - Result: sparse vector with 40-400 non-zero dimensions

3. **Retrieval**
   - Index sparse latent representations
   - Rank by dot product (same as SPLADE)
   - Computational cost: O(k) where k ≈ 50-100 non-zeros

**Performance Results:**

On MMTEB (Multilingual Massive Text Embedding Benchmark):
- SPLARE ranks in top tier for sparse retrieval across 100+ languages
- Out-of-domain performance: 15-20% better than vocabulary-based LSR
- Zero-shot performance: better generalization without fine-tuning

**Advantages Over Vocabulary-Based Approaches:**

1. **Language Independence**: Learned features don't depend on vocabulary structure
2. **Domain Adaptability**: Features capture domain concepts automatically
3. **Redundancy Reduction**: Learned features are more orthogonal than vocabulary terms
4. **Efficiency**: Fewer features needed (40 vs 100+)

**Limitations:**

1. **Interpretability**: What does latent feature #427 mean? Less clear than "cancer"
2. **Cross-model compatibility**: SAEs must be trained together with retrieval model
3. **Training complexity**: Requires training both SAE and retrieval head

### SAE vs SPLADE: When to Use Each

**Use SPLARE/SAE when:**
- Working in multiple languages simultaneously
- Out-of-domain transfer is critical
- You want maximum efficiency (fewer features)
- Domain-specific vocabulary is unavailable or changing

**Use SPLADE when:**
- Interpretability is important (can inspect term weights)
- Working primarily in English
- You have domain-specific vocabulary lists
- Debugging relevance decisions is important

---

## 6. Decoder-Only LLM Approaches: Echo-Mistral-SPLADE

### The Challenge of Decoder-Only Models

Traditional SPLADE uses BERT, which is an encoder-only model with bidirectional attention. Large language models are typically decoder-only with unidirectional (causal) attention. Extending SPLADE to decoder-only models like Mistral-7B, Llama-2, or GPT variants requires solving fundamental architectural challenges.

**The Unidirectional Attention Problem:**

In a decoder-only model with causal attention:
```
Input: "cancer treatment lung"
Token positions: [0, 1, 2]

Position 2 ("lung"):
  - Can attend to tokens 0, 1, 2 (itself included)
  - Can use full context for expansion

Position 0 ("cancer"):
  - Can only attend to token 0 (itself)
  - Cannot see forward context
  - Cannot make good expansion decisions
```

SPLADE expansion relies on seeing context. Without context, the MLM head cannot predict semantically related terms well.

### Echo Embeddings: The Solution

**Echo-Mistral-SPLADE** introduces "echo embeddings" - a technique that enables full context awareness in decoder-only models.

**Echo Embedding Mechanism:**

```python
# Standard approach (fails with causal attention)
input_ids = [cancer, treatment, lung]
logits = model(input_ids)  # Position 0 has incomplete context

# Echo embedding approach
input_ids = [cancer, treatment, lung, cancer, treatment, lung]
                      # First pass through model
logits = model(input_ids)
# Take mean of representations for positions [3, 4, 5]
# These positions can attend to full context [0, 1, 2]
logits = logits[3:6]  # Use second occurrence
```

**Why This Works:**

1. Duplicate the input sequence
2. First occurrence: causal attention sees limited context
3. Second occurrence: causal attention sees FULL original context (positions 0-2) plus first pass (positions 3-5)
4. Take representations from second occurrence
5. All tokens now have full context awareness

**Performance Advantage:**

By providing full context, the decoder-only model's MLM head can make better expansion decisions:
- "cancer" → expands to "tumor", "oncology", "malignant"
- "treatment" → expands to "therapy", "intervention", "medical"
- "lung" → expands to "pulmonary", "respiratory"

### Architecture Details

**Echo-Mistral-SPLADE Pipeline:**

1. **Model Base**: Mistral-7B (decoder-only, 32K vocabulary)
2. **Adaptation**: LoRA (Low-Rank Adaptation) to efficient fine-tune
3. **Echo Processing**: Double input sequence, extract second occurrence
4. **Projection Head**: Similar to SPLADE (project to sparse representation)
5. **Pooling**: Sum pooling across token representations
6. **Output**: Sparse vector over vocabulary (or learned features)

**Key Technical Details:**

- **Input dimensions**: Vocabulary size of Mistral (32K)
- **Sparsity**: FLOPS regularization applied during training
- **Training**: Contrastive learning on MS MARCO + distillation from cross-encoder
- **Efficiency**: Slightly slower inference than BERT-based (7B > BERT-base) but better quality

### Mistral-SPLADE Performance

**Results on BEIR Benchmark (NDCG@10):**

| Method | BEIR Avg | Trec-COVID | SciFact | DBpedia | Fiqa |
|--------|----------|-----------|---------|---------|------|
| SPLADE-v2 | 45.8 | 59.5 | 66.3 | 27.7 | 32.5 |
| SPLADE-v3 | 47.8 | 61.2 | 68.5 | 29.1 | 34.2 |
| Mistral-SPLADE | **49.2** | **63.1** | **70.8** | **31.5** | **36.8** |
| Dense (ANCE) | 43.2 | 57.3 | 62.4 | 25.2 | 29.8 |

**Why Mistral-SPLADE Wins:**

1. **Scale**: 7B parameters provide better semantic understanding
2. **Training Data**: Mistral trained on diverse internet-scale data
3. **Echo embeddings**: Full context for better expansion
4. **Knowledge**: Larger models know more term relationships

**Trade-offs:**

- Inference latency: ~200ms per query (vs 20ms for SPLADE-v2)
- Model size: 7B parameters (vs 110M for BERT-base)
- Benefits: Higher quality in out-of-domain settings

### When to Use Decoder-Only Approaches

**Advantages:**
- State-of-the-art BEIR performance
- Leverage of large pre-trained models
- Better semantic expansion
- Future-proof (LLM-based approaches becoming dominant)

**Disadvantages:**
- Higher latency
- Larger memory requirements
- Overkill for in-domain tasks (MS MARCO)
- Less efficient than BERT-based SPLADE

---

## 7. Benchmark Results and Comparisons

### MS MARCO Passage Ranking

**Dataset**: 8.8M passages, 502K train queries, 6,980 dev queries
**Metric**: MRR@10 (Mean Reciprocal Rank)

**Historical Results:**

| Year | Method | Type | MRR@10 | Inference (ms) | Index Size (GB) |
|------|--------|------|--------|----------------|-|
| 2019 | BM25 | Sparse | 0.184 | <1 | 2 |
| 2020 | ANCE | Dense | 0.330 | 200 | 135 |
| 2021 | SPLADE v1 | Sparse | 0.322 | 20 | 80 |
| 2021 | TCT-ColBERT | Dense | 0.335 | 220 | 140 |
| 2021 | SPLADE v2 | Sparse | 0.365 | 18 | 120 |
| 2022 | DistilSPLADE | Sparse | 0.370 | 17 | 130 |
| 2024 | SPLADE v3 | Sparse | 0.375 | 16 | 140 |
| 2025 | CSPLADE | Sparse | 0.413 | 45 | 8 |

**Key Observations:**

1. **Sparse vs Dense**: SPLADE-v3 is 96% of dense model performance at fraction of the inference cost
2. **Index Size**: Traditional sparse methods need ~100-150GB for MS MARCO (BM25 is most efficient at 2GB)
3. **Training Data**: All neural methods trained on MS MARCO, so in-domain performance is highest
4. **Efficiency**: Sparse retrieval maintains constant latency regardless of corpus size (unlike dense which is O(corpus_size))

### BEIR Benchmark

**Dataset**: 18 diverse IR datasets from different domains (law, biology, e-commerce, etc.)
**Metric**: NDCG@10 (Normalized Discounted Cumulative Gain)

**Zero-Shot Results (no domain adaptation):**

| Method | Avg NDCG@10 | Scifact | Trec-COVID | DBpedia | Fiqa |
|--------|------------|---------|-----------|---------|------|
| BM25 | 42.3 | 63.5 | 58.2 | 28.7 | 25.3 |
| ANCE | 43.2 | 62.4 | 57.3 | 25.2 | 29.8 |
| DPR | 42.1 | 61.8 | 56.9 | 24.8 | 28.5 |
| SPLADE-v2 | 47.8 | 66.5 | 61.2 | 31.4 | 32.1 |
| SPLADE-v3 | **49.1** | **68.8** | **63.5** | **33.2** | **34.7** |
| Mistral-SPLADE | **49.8** | **70.1** | **64.8** | **35.1** | **36.3** |

**Key Observations:**

1. **Domain Transfer**: SPLADE outperforms dense methods by 5-6 NDCG points on average
2. **Robustness**: Sparse methods generalize better to unseen domains
3. **BM25 Parity**: SPLADE-v3 beats BM25 on most datasets
4. **Scaling**: Larger models (Mistral) provide 1-2 point gains

**Why Sparse Models Generalize Better:**

Dense models overfit to the MS MARCO query distribution and document style. SPLADE's sparse representations force the model to identify core semantic features that transfer across domains.

### Natural Questions (NQ) Benchmark

**Dataset**: 307K training examples, 7.8K dev queries, 3.2M Wikipedia passages
**Metric**: Recall@k, MRR

**Results:**

| Method | Recall@10 | Recall@100 | MRR@10 |
|--------|-----------|-----------|--------|
| BM25 | 54.2 | 83.1 | 0.52 |
| ANCE | 68.5 | 90.2 | 0.68 |
| SPLADE v2 | 72.3 | 91.8 | 0.71 |
| SPLADE v3 | 74.1 | 92.6 | 0.73 |
| Mistral-SPLADE | 75.8 | 93.4 | 0.76 |

**Observations:**

- Open-domain QA requires high recall to feed into reader models
- Sparse models achieve excellent recall with reasonable efficiency
- SPLADE is preferred over dense for this task due to efficiency

### Efficiency Analysis: FLOPS and Latency

**FLOPS Complexity:**

```
BM25:
  Query processing: O(|query|) - tokenize query
  Ranking: O(|posting_lists|) - sum BM25 scores
  Total: O(|query| + avg_posting_list_size) ≈ milliseconds

SPLADE (sparse):
  Query processing: O(|query|) - embedding inference
  Ranking: O(k) - dot product with k non-zero dimensions
  Total: O(embedding_time + k) ≈ 15-50ms (bottleneck: embedding)

Dense (ANCE):
  Query processing: O(|query|) - embedding inference
  Ranking: O(d × |corpus|) - dot product with all vectors
  Total: O(embedding_time + d*corpus) ≈ 200-500ms without approximation
```

**Latency Breakdown (for SPLADE):**

```
Query: "cancer treatment options"

1. Tokenization: 1ms
2. BERT encoding: 15ms
3. MLM projection: 2ms
4. Sparse regularization: <1ms
5. Retrieval (1M documents): 5ms
   - Inverted index lookup
   - BM25-style scoring over matching documents

Total: ~25ms
```

**Comparison:**

| Operation | BM25 | SPLADE | Dense (ANCE) |
|-----------|------|--------|--------------|
| Inference (GPU) | N/A | 15ms | 50ms |
| Inference (CPU) | <1ms | 80ms | 800ms |
| Ranking | 2ms | 5ms | 100ms+ |
| Total | <2ms | 20ms | 200ms+ |

---

## 8. Production Deployment and Integration

### Integration with Search Engines

#### Qdrant Vector Database

Qdrant is a vector database with native sparse vector support, making it ideal for SPLADE deployment.

**Setup with Qdrant and FastEmbed:**

```python
from fastembed.sparse.splade_pp_en_v1 import SpladeEmbedding

# Initialize SPLADE embedding
embedding_model = SpladeEmbedding()

# Encode documents
docs = ["lung cancer treatment", "breast cancer therapy", "cancer prevention"]
doc_embeddings = embedding_model.embed(docs)
# Returns: list of SparseEmbedding objects with indices and values

# Create Qdrant collection with sparse vector configuration
client = qdrant_client.QdrantClient("localhost", port=6333)

client.create_collection(
    collection_name="documents",
    vectors_config=models.VectorParams(
        size=30522,  # BERT vocabulary size
        distance=models.Distance.COSINE
    ),
    sparse_vectors_config=models.SparseVectorParams(
        index=models.SparseIndexParams(
            on_disk=True,
        )
    ),
)

# Index documents
points = [
    models.PointStruct(
        id=i,
        vector={"dense": embedding["dense"]},  # if using hybrid
        sparse_vector=embedding["sparse"],
        payload={"text": doc}
    )
    for i, (doc, embedding) in enumerate(zip(docs, doc_embeddings))
]

client.upsert(collection_name="documents", points=points)

# Query
query = "lung cancer treatment options"
query_embedding = embedding_model.embed_query(query)

results = client.search(
    collection_name="documents",
    query_vector=query_embedding["sparse"],
    limit=10
)
```

**Advantages:**
- Native sparse vector support
- Hybrid search (dense + sparse)
- Persistent on-disk indexing
- Production-ready

#### Elasticsearch Integration

Elasticsearch added support for learned sparse retrievers through ELSER (Elastic Learned Sparse EncodeR).

**Elasticsearch Setup:**

```json
// 1. Create index with sparse_vector field
PUT /documents
{
  "mappings": {
    "properties": {
      "text": { "type": "text" },
      "sparse_embeddings": { "type": "sparse_vector" }
    }
  }
}

// 2. Ingest using ML model
POST /_ml/trained_models/splade:deploy

// 3. Index documents
POST /documents/_ingest/pipeline/splade_pipeline
{
  "description": "Splade embeddings pipeline",
  "processors": [
    {
      "inference": {
        "model_id": "splade_model",
        "input_output_map": {
          "text": "text_field"
        }
      }
    }
  ]
}
```

**Query:**

```json
GET /documents/_search
{
  "query": {
    "sparse_vector": {
      "sparse_embeddings": {
        "inference_id": "splade",
        "query": "cancer treatment"
      }
    }
  }
}
```

#### Vespa Search

Vespa, Yahoo's open-source search engine, has extensive support for both dense and sparse vectors.

**Vespa Schema:**

```xml
<schema name="documents">
  <document name="documents">
    <field name="text" type="string"/>
    <field name="sparse_vector" type="weightedset" indexing="summary">
      <!-- Sparse vector represented as weighted set -->
    </field>
  </document>

  <rank-profile default>
    <!-- BM25 + SPLADE hybrid ranking -->
    <function name="bm25">bm25(text)</function>
    <function name="sparse_score">
      dotProduct(sparse_vector, query(sparse_vector))
    </function>
    <first-phase>
      <expression>
        0.4 * bm25 + 0.6 * sparse_score
      </expression>
    </first-phase>
  </rank-profile>
</schema>
```

**Advantages of Vespa:**
- Efficient weighted set handling for sparse vectors
- Easy BM25 + SPLADE hybrid
- Ranking function flexibility
- Large-scale deployment proven

### Sparse Index Construction

**Creating an Index from SPLADE Vectors:**

```python
import pyserini  # PySerini toolkit for IR
from transformers import AutoModel, AutoTokenizer

# 1. Generate sparse vectors
tokenizer = AutoTokenizer.from_pretrained("naver/splade-cocondenser-ensembledistil")
model = AutoModel.from_pretrained("naver/splade-cocondenser-ensembledistil")

documents = [
    {"id": "1", "text": "lung cancer treatment options"},
    {"id": "2", "text": "breast cancer therapy methods"},
    # ... more documents
]

# 2. Encode documents
encoded_docs = []
for doc in documents:
    inputs = tokenizer(doc["text"], return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)

    # Get sparse vector (non-zero dimensions)
    sparse_vector = {}  # Dictionary mapping term_id -> weight

    logits = outputs.logits[0]  # [seq_len, vocab_size]
    weights = torch.max(torch.log(1 + torch.relu(logits)), dim=0)[0]

    # Keep only top-k non-zero dimensions
    top_k = 100
    indices = torch.topk(weights, k=top_k).indices

    for idx in indices:
        term_id = idx.item()
        term_weight = weights[idx].item()
        sparse_vector[tokenizer.decode(term_id)] = term_weight

    encoded_docs.append({
        "id": doc["id"],
        "sparse_vector": sparse_vector,
        "content": doc["text"]
    })

# 3. Build inverted index
from collections import defaultdict

inverted_index = defaultdict(list)
for doc in encoded_docs:
    for term, weight in doc["sparse_vector"].items():
        inverted_index[term].append({
            "doc_id": doc["id"],
            "weight": weight
        })

# 4. Save index
import pickle
with open("splade_index.pkl", "wb") as f:
    pickle.dump(inverted_index, f)
```

### Query Processing and Ranking

**Efficient Query Ranking:**

```python
def rank_documents(query, inverted_index, top_k=1000):
    # 1. Encode query
    query_tokens = tokenizer(query, return_tensors="pt", padding=True, truncation=True)
    query_outputs = model(**query_tokens)

    logits = query_outputs.logits[0]
    query_weights = torch.max(torch.log(1 + torch.relu(logits)), dim=0)[0]

    # 2. Get query non-zero dimensions
    query_sparse = {}
    top_k_query = 50  # Queries are sparser
    indices = torch.topk(query_weights, k=top_k_query).indices

    for idx in indices:
        term_id = idx.item()
        term_weight = query_weights[idx].item()
        term = tokenizer.decode(term_id)
        query_sparse[term] = term_weight

    # 3. Retrieve candidate documents (inverted index lookup)
    candidates = {}
    for term, q_weight in query_sparse.items():
        if term in inverted_index:
            for doc_entry in inverted_index[term]:
                doc_id = doc_entry["doc_id"]
                doc_weight = doc_entry["weight"]

                # Accumulate score (cosine similarity)
                if doc_id not in candidates:
                    candidates[doc_id] = 0.0
                candidates[doc_id] += q_weight * doc_weight

    # 4. Rank and return top-k
    ranked = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]

# Usage
results = rank_documents("cancer treatment", inverted_index, top_k=10)
for doc_id, score in results:
    print(f"Document {doc_id}: score {score:.4f}")
```

---

## 9. Sparse-Dense Hybrid Strategies

### Why Combine Sparse and Dense?

Sparse and dense retrievers have complementary strengths:

**Sparse (SPLADE) Strengths:**
- Exact keyword matching for named entities
- Interpretable features (can inspect term weights)
- Efficient on large corpora
- Robust generalization

**Dense (ANCE, ORDE) Strengths:**
- Semantic similarity for paraphrases
- Single semantic space
- Better for synonyms and conceptual matching

**Hybrid Benefits:**
- 30-40% accuracy improvement in production systems
- Combines precision of lexical + recall of dense
- Improved robustness to domain shift

### Late Fusion Strategies

#### Score Fusion (Linear Combination)

```python
def hybrid_rank(query, sparse_results, dense_results, alpha=0.5):
    """
    Combine sparse and dense ranking scores.
    alpha controls the weight (0.5 = equal weight)
    """

    # Normalize scores to [0, 1]
    sparse_max = sparse_results[0][1]  # Highest sparse score
    dense_max = dense_results[0][1]    # Highest dense score

    sparse_normalized = {
        doc_id: score/sparse_max
        for doc_id, score in sparse_results
    }
    dense_normalized = {
        doc_id: score/dense_max
        for doc_id, score in dense_results
    }

    # Combine scores
    combined = {}
    for doc_id in set(sparse_normalized.keys()) | set(dense_normalized.keys()):
        sparse_score = sparse_normalized.get(doc_id, 0.0)
        dense_score = dense_normalized.get(doc_id, 0.0)
        combined[doc_id] = alpha * sparse_score + (1-alpha) * dense_score

    # Return ranked list
    return sorted(combined.items(), key=lambda x: x[1], reverse=True)
```

**Advantages:**
- Simple to implement
- Theoretically sound (linear combination of relevance scores)
- Interpretable

**Disadvantages:**
- Requires score normalization (scores may be on different scales)
- Fixed weight across all queries
- Linear assumption may be suboptimal

#### Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(sparse_results, dense_results, k=60):
    """
    Combine rankings using reciprocal rank.
    Less sensitive to score scales than linear combination.
    """

    def rrf_score(rank, k=60):
        """RRF formula: 1 / (k + rank)"""
        return 1.0 / (k + rank)

    # Extract rankings
    sparse_ranks = {doc_id: idx for idx, (doc_id, _) in enumerate(sparse_results, 1)}
    dense_ranks = {doc_id: idx for idx, (doc_id, _) in enumerate(dense_results, 1)}

    # Combine RRF scores
    combined = {}
    for doc_id in set(sparse_ranks.keys()) | set(dense_ranks.keys()):
        sparse_score = rrf_score(sparse_ranks.get(doc_id, len(sparse_results) + 1), k)
        dense_score = rrf_score(dense_ranks.get(doc_id, len(dense_results) + 1), k)
        combined[doc_id] = sparse_score + dense_score

    # Return ranked list
    return sorted(combined.items(), key=lambda x: x[1], reverse=True)
```

**Advantages:**
- Rank-based (not score-based), robust to score scales
- No normalization needed
- Well-established in information retrieval
- Less prone to one ranker dominating

**Disadvantages:**
- Loses information about score magnitude
- Parameter k needs tuning

#### Machine-Learned Fusion

```python
from sklearn.linear_model import LogisticRegression

def learn_hybrid_fusion(queries, sparse_results, dense_results, labels):
    """
    Train a model to predict the best combination weight.
    """

    features = []
    targets = []

    for q_idx, query in enumerate(queries):
        sparse_score = sparse_results[q_idx][0][1] if sparse_results[q_idx] else 0
        dense_score = dense_results[q_idx][0][1] if dense_results[q_idx] else 0

        features.append([sparse_score, dense_score])
        targets.append(labels[q_idx])  # Relevance label

    # Train fusion model
    model = LogisticRegression()
    model.fit(features, targets)

    return model

# Inference
def predict_hybrid(model, sparse_score, dense_score):
    prediction = model.predict_proba([[sparse_score, dense_score]])
    return prediction[0][1]  # Probability of relevance
```

**Advantages:**
- Data-driven, learns optimal combination
- Adapts to specific domains
- Can use additional features (query length, document length, etc.)

**Disadvantages:**
- Requires labeled training data
- May overfit
- Less interpretable

### Early Fusion: Hybrid Indexing

Some systems use early fusion, storing both sparse and dense vectors in the same index:

**Hybrid Index Structure:**

```json
{
  "document_id": "1",
  "text": "lung cancer treatment",
  "dense_vector": [0.12, -0.34, 0.67, ...],  // 768D
  "sparse_vector": {
    "lung": 0.8,
    "cancer": 0.9,
    "tumor": 0.6,
    "treatment": 0.7
  }
}
```

**Query Processing:**

```python
def early_fusion_search(query_text):
    # Encode query in both representations
    query_dense = dense_encoder(query_text)  # 768D
    query_sparse = sparse_encoder(query_text)  # Sparse

    # Search both indexes simultaneously
    dense_candidates = ann_search(query_dense, top_k=1000)
    sparse_candidates = inverted_index_search(query_sparse, top_k=1000)

    # Merge and rerank
    merged = merge_results(dense_candidates, sparse_candidates)
    final = late_fusion_rank(merged, query_sparse, query_dense)

    return final[:10]
```

### Production Recommendation: Hybrid with Reranking

**Recommended 3-Stage Pipeline:**

```
Stage 1: Retrieval
├─ BM25 (lexical) → Top 10K candidates
└─ Sparse (SPLADE) → Top 10K candidates
├─ Merge (union) → Top 20K deduplicated candidates
└─ Apply late fusion score

Stage 2: First-stage Reranker
├─ Fast model (DistilBERT, 12 layers)
├─ Score all 20K candidates
└─ Top 200 candidates to stage 3

Stage 3: Final Reranking
├─ Cross-encoder (MiniLM-L12-v2)
├─ Score top 200
└─ Return top 10
```

**Example Code:**

```python
def three_stage_retrieval(query, corpus):
    # Stage 1: Retrieval
    bm25_results = bm25_search(query, corpus, k=10000)
    splade_results = splade_search(query, corpus, k=10000)

    # Merge and deduplicate
    candidates = {}
    for doc_id, score in bm25_results + splade_results:
        if doc_id not in candidates:
            candidates[doc_id] = {"bm25": 0, "splade": 0}
        # Update scores

    merged = sorted(candidates.items(), key=lambda x: hybrid_score(x[1]), reverse=True)[:20000]

    # Stage 2: First-stage reranker
    first_stage_model = FastModel()
    reranked_1 = first_stage_model.batch_score([(query, doc) for doc, _ in merged])
    top_200 = sorted(zip(merged, reranked_1), key=lambda x: x[1], reverse=True)[:200]

    # Stage 3: Final reranking
    cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")
    final_scores = cross_encoder.predict([(query, doc) for doc, _ in top_200])
    final_ranking = sorted(zip(top_200, final_scores), key=lambda x: x[1], reverse=True)

    return final_ranking[:10]
```

---

## 10. Domain-Specific Applications

### Legal Document Retrieval

**Characteristics of Legal Domain:**
- Highly technical vocabulary (contract law, tort law, etc.)
- Long documents (50-100K tokens per document)
- Citation-based structure (documents reference other documents)
- High precision requirements (wrong precedent is costly)

**SPLADE Application:**

```python
# Legal-specific adaptations

# 1. Use domain-specific terminology
# Train with legal corpus: laws, court opinions, contracts
legal_splade = train_splade_on_corpus(legal_documents)

# 2. Longer document handling
# SPLADE typically works on passages (100-200 tokens)
# For legal documents, need passage-level indexing

def index_legal_document(doc, passage_length=200):
    """Split long legal docs into passages, maintaining context."""
    passages = []
    tokens = tokenizer.tokenize(doc.text)

    for i in range(0, len(tokens), passage_length//2):  # 50% overlap
        passage_tokens = tokens[i:i+passage_length]
        passage_text = tokenizer.decode(passage_tokens)

        sparse_vector = legal_splade.encode(passage_text)
        passages.append({
            "doc_id": doc.id,
            "passage_id": f"{doc.id}_{i}",
            "passage_text": passage_text,
            "sparse_vector": sparse_vector
        })

    return passages

# 3. Hybrid with citation-based ranking
def legal_hybrid_ranking(query, candidates):
    """
    Combine SPLADE with citation graph analysis.
    Important precedents cited more often should rank higher.
    """

    # SPLADE score
    splade_score = sparse_rank(query, candidates)

    # Citation frequency
    citation_score = {
        doc_id: citation_count(doc_id) / max_citations
        for doc_id in candidates
    }

    # Combine
    return 0.7 * splade_score + 0.3 * citation_score
```

**Results in Legal Domain:**
- Precision@5 increases by 15-20% with SPLADE vs BM25
- Recall improves by 10-15%, critical for compliance
- Zero-shot transfer to new legal domain: 85% of in-domain performance

### Medical Information Retrieval

**Characteristics:**
- Domain: medical literature (MEDLINE), EHR (Electronic Health Records)
- Vocabulary: Medical Subject Headings (MeSH) terminology
- Temporal aspect: drug interactions, treatment guidelines evolve
- Accuracy critical: wrong diagnosis is dangerous

**Medical SPLADE Implementation:**

```python
class MedicalSPLADE:
    def __init__(self):
        # 1. Use medical-trained models
        self.model = AutoModel.from_pretrained(
            "allenai/scibert_scivocab_uncased"  # BioBERT alternative
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "allenai/scibert_scivocab_uncased"
        )

        # 2. MeSH vocabulary mapping
        self.mesh_terms = load_mesh_vocabulary()

    def encode_with_mesh_expansion(self, text):
        """Expand using MeSH terms for medical accuracy."""

        # Standard SPLADE encoding
        sparse_vector = self.encode(text)

        # Identify MeSH terms in text
        mesh_matches = self.extract_mesh_terms(text)

        # Boost MeSH term weights
        for mesh_term in mesh_matches:
            if mesh_term in sparse_vector:
                sparse_vector[mesh_term] *= 1.5  # Boost medical terms

        return sparse_vector

    def temporal_aware_retrieval(self, query, documents, current_date):
        """
        Adjust scores based on document recency.
        Recent medical guidelines more relevant than old ones.
        """

        scores = {}
        for doc in documents:
            splade_score = self.score(query, doc)

            # Temporal boost
            doc_age_years = (current_date - doc.publication_date).days / 365
            recency_boost = 1.0 / (1.0 + doc_age_years)  # Exponential decay

            scores[doc.id] = splade_score * recency_boost

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**Medical Domain Results:**
- Precision@10 on TREC-MIS (Medical Information Search): 65-70%
- Recall on drug interaction detection: 92% (critical safety metric)
- Zero-shot to new medical subdomain: 75% of fine-tuned performance

### E-Commerce Search

**Characteristics:**
- Products with attributes (price, color, size, brand)
- User intent varies: navigational (brand search) vs informational
- Real-time: inventory changes, new products added constantly
- Business impact: relevance = conversion, revenue

**E-Commerce SPLADE Implementation:**

```python
class EcommerceSPLADE:
    def encode_product(self, product):
        """Encode product with rich metadata."""

        # Combine text fields
        text = " ".join([
            product.title,
            product.description,
            product.category,
            " ".join(product.tags)
        ])

        # Base SPLADE encoding
        sparse_vector = self.base_splade_encode(text)

        # Attribute-based expansion
        # Boost exact matches on important attributes
        if product.brand:
            sparse_vector[product.brand] *= 2.0

        if product.category:
            sparse_vector[product.category] *= 1.5

        return sparse_vector

    def ecommerce_ranking(self, query, candidates, user_context=None):
        """
        Combine SPLADE with business metrics.
        """

        # Semantic relevance
        relevance_scores = sparse_rank(query, candidates)

        # Business signals
        scores = {}
        for product_id in candidates:
            product = get_product(product_id)

            relevance = relevance_scores[product_id]

            # Business metrics
            popularity = product.sales_count / max_sales
            rating = product.avg_rating / 5.0
            stock_status = 1.0 if product.in_stock else 0.5

            # Combined score
            score = (
                0.6 * relevance +      # Semantic relevance
                0.15 * popularity +    # Trending products
                0.15 * rating +        # Quality indicator
                0.1 * stock_status     # Immediate availability
            )

            scores[product_id] = score

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**E-Commerce Results:**
- Click-through rate (CTR) improvement: 8-12% vs BM25
- Conversion rate: 5-7% improvement
- Average order value: 3-5% improvement through better recommendations
- Search latency: <100ms (important for interactive search)

---

## 11. When to Use Learned Sparse Retrieval

### SPLADE Preferred When:

1. **Large Corpus (1B+ documents)**
   - Dense retrieval becomes impractical (memory, computational cost)
   - Sparse indexing with BM25 compatibility is highly efficient
   - Example: Wikipedia, web search, enterprise document corpus

2. **Out-of-Domain Evaluation is Critical**
   - SPLADE generalizes better than dense models
   - Example: Task-specific domain (legal, medical) with limited training data

3. **Interpretability Required**
   - Stakeholders need to understand why document ranked high
   - SPLADE term weights are explainable (e.g., "document matched on 'cancer' (0.9), 'treatment' (0.7)")
   - Example: High-stakes domains (legal discovery, medical decisions)

4. **Latency Constraints Below 50ms**
   - SPLADE with local indexing: ~15-20ms
   - Dense with ANN: ~100-300ms
   - Example: Real-time applications, mobile search

5. **Memory Constraints**
   - Sparse vectors take 1-2% of dense memory
   - Example: On-device search, edge deployment

6. **Existing BM25 Infrastructure**
   - Backward compatible with inverted index systems
   - Can drop into existing Elasticsearch, Lucene, Vespa
   - Example: Organizations with mature search infrastructure

7. **Query Expansion is Important**
   - SPLADE naturally handles synonym expansion
   - Example: Scientific search (authors use varied terminology)

### Dense Retrieval Preferred When:

1. **Latency Not Critical (200ms+ acceptable)**
   - Dense models have higher accuracy
   - Example: Batch processing, offline indexing

2. **In-Domain Training Data Available**
   - Dense models with domain fine-tuning beat SPLADE
   - Example: Custom internal datasets (MS MARCO-like)

3. **Semantic Similarity Essential**
   - Dense models excel at paraphrase matching
   - Example: Duplicate detection, similarity assessment

4. **Model Size Not Constraint**
   - Can use larger models (175B+) with better quality
   - Example: Cloud-based SaaS search

5. **Filtering and Metadata Complex**
   - Dense embeddings integrate better with learned filtering
   - Example: Faceted search, complex boolean queries

### Hybrid (Sparse + Dense) Preferred When:

1. **Maximum Accuracy Required**
   - Combination provides 30-40% accuracy boost
   - Example: High-value retrieval (legal discovery, medical)

2. **Cost Acceptable**
   - Maintaining both indexes increases operational complexity
   - Example: Enterprise with adequate resources

3. **Diverse Query Types**
   - Some queries benefit more from lexical matching
   - Others from semantic matching
   - Example: General-purpose search engines

4. **Production Systems with SLOs**
   - Service level agreements (e.g., 99.9% uptime)
   - Hybrid provides robustness (if one fails, fallback to other)

---

## 12. Implementation Guide and Code Examples

### Complete Example: Building a SPLADE-Powered Search System

```python
"""
Complete example: SPLADE-based document retrieval system
"""

import torch
from transformers import AutoModel, AutoTokenizer
from collections import defaultdict
import json

class SPLADERetriever:
    def __init__(self, model_name="naver/splade-cocondenser-ensembledistil"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        self.inverted_index = defaultdict(list)
        self.document_store = {}

    def encode(self, text, is_query=False):
        """
        Encode text to sparse vector.
        Returns: dict with term_id -> weight mappings
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get logits and apply ReLU
        logits = outputs.logits[0]  # [seq_len, vocab_size]
        weights = torch.log(1 + torch.relu(logits))  # [seq_len, vocab_size]

        # Pool across tokens (max pooling)
        doc_weights = torch.max(weights, dim=0)[0]  # [vocab_size]

        # Get top-k non-zero dimensions
        top_k = 100 if is_query else 500
        indices = torch.topk(doc_weights, k=min(top_k, len(doc_weights))).indices

        sparse_vector = {}
        for idx in indices:
            term_id = idx.item()
            term_weight = doc_weights[idx].item()

            # Decode term
            term = self.tokenizer.decode([term_id])
            if term.strip() and term not in ['[CLS]', '[SEP]', '[PAD]']:
                sparse_vector[term] = float(term_weight)

        return sparse_vector

    def index_documents(self, documents):
        """
        Index a batch of documents.

        Args:
            documents: List of dicts with 'id' and 'text' keys
        """
        for doc in documents:
            doc_id = doc['id']
            text = doc['text']

            # Encode
            sparse_vector = self.encode(text, is_query=False)

            # Store document
            self.document_store[doc_id] = {
                'text': text,
                'sparse_vector': sparse_vector
            }

            # Update inverted index
            for term, weight in sparse_vector.items():
                self.inverted_index[term].append({
                    'doc_id': doc_id,
                    'weight': weight
                })

    def search(self, query, top_k=10):
        """
        Search for documents matching query.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of (doc_id, score) tuples
        """
        # Encode query
        query_sparse = self.encode(query, is_query=True)

        # Retrieve candidates using inverted index
        candidates = defaultdict(float)
        for term, q_weight in query_sparse.items():
            if term in self.inverted_index:
                for doc_entry in self.inverted_index[term]:
                    doc_id = doc_entry['doc_id']
                    doc_weight = doc_entry['weight']

                    # Dot product
                    candidates[doc_id] += q_weight * doc_weight

        # Rank and return top-k
        ranked = sorted(
            candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked[:top_k]

# Usage
def main():
    # Initialize retriever
    retriever = SPLADERetriever()

    # Sample documents
    documents = [
        {
            'id': '1',
            'text': 'Lung cancer is a malignant tumor of the lung. Treatment options include chemotherapy, radiation, and surgery.'
        },
        {
            'id': '2',
            'text': 'Breast cancer therapy typically involves hormonal treatments and targeted molecular therapies.'
        },
        {
            'id': '3',
            'text': 'Cancer prevention strategies include smoking cessation, healthy diet, and regular screening.'
        },
        {
            'id': '4',
            'text': 'Artificial intelligence is transforming healthcare with machine learning models for diagnosis.'
        }
    ]

    # Index documents
    print("Indexing documents...")
    retriever.index_documents(documents)

    # Search
    queries = [
        "cancer treatment options",
        "lung tumor therapy",
        "machine learning in medicine"
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        results = retriever.search(query, top_k=3)

        for doc_id, score in results:
            doc_text = retriever.document_store[doc_id]['text']
            print(f"  Doc {doc_id} (score: {score:.4f}): {doc_text[:60]}...")

if __name__ == "__main__":
    main()
```

### Integration with Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

def qdrant_integration():
    """Store and retrieve SPLADE vectors using Qdrant."""

    # Connect to Qdrant
    client = QdrantClient("localhost", port=6333)

    # Create collection
    collection_name = "documents"
    client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=30522,  # BERT vocabulary size
            distance=Distance.COSINE
        ),
        sparse_vectors_config=models.SparseVectorParams(
            index=models.SparseIndexParams(
                on_disk=True,
            )
        )
    )

    # Initialize retriever
    retriever = SPLADERetriever()

    # Prepare documents
    documents = [...]  # Your documents

    # Index documents
    points = []
    for doc in documents:
        sparse_vector = retriever.encode(doc['text'], is_query=False)

        # Convert to Qdrant sparse format
        indices = [hash(term) % 30522 for term in sparse_vector.keys()]
        values = list(sparse_vector.values())

        point = PointStruct(
            id=int(uuid.uuid4()),
            vector={"sparse": {"indices": indices, "values": values}},
            payload={"text": doc['text'], "doc_id": doc['id']}
        )
        points.append(point)

    # Upsert to Qdrant
    client.upsert(
        collection_name=collection_name,
        points=points
    )

    # Query
    query = "cancer treatment"
    query_sparse = retriever.encode(query, is_query=True)

    indices = [hash(term) % 30522 for term in query_sparse.keys()]
    values = list(query_sparse.values())

    results = client.search(
        collection_name=collection_name,
        query_vector={
            "sparse": {"indices": indices, "values": values}
        },
        limit=10
    )

    for result in results:
        print(f"Doc {result.payload['doc_id']}: score {result.score:.4f}")
```

---

## 13. Future Directions and Research Challenges

### Current Challenges

**1. Scalability to Billion-Scale Corpora**

Current SPLADE indexes for 1B+ documents approach 1-2TB. While smaller than flat dense indexes (5-10TB), this is still large. Future work:
- More aggressive pruning (eliminate low-weight terms)
- Learned pruning strategies (model decides which terms to keep)
- Compressed sparse representations

**2. Multimodal Expansion**

Recent work (Multimodal-LSR) extends SPLADE to images and video. Challenges:
- How to define "vocabulary" for visual features?
- SAE-based approaches more promising than vocabulary
- Cross-modal alignment without semantic deviation

**3. Long Document Handling**

SPLADE works on passages (100-200 tokens). For long documents:
- Hierarchical approaches needed
- Context preservation across passages
- Proper handling of citations in academic papers

**4. Dynamic Vocabularies**

Real-world corpora evolve:
- New terms emerge (e.g., "COVID-19")
- Vocabulary frequency distributions shift
- Need for continual learning without reindexing

**5. Adaptation to LLMs**

Recent models (LLaMA, Mistral) are decoder-only. While CSPLADE shows promise:
- Better techniques than echo embeddings?
- How to leverage instruction-tuning?
- Scaling to 70B+ models efficiently?

### Promising Research Directions

**1. Sparse Autoencoders for Interpretability**

SPLARE approach (using SAEs instead of vocabulary) addresses:
- Better out-of-domain generalization
- Language-agnostic features
- Interpretability through feature analysis

Future: Combine SAE sparsity with SPLADE efficiency

**2. Neural-Lexical Fusion**

Learning to blend neural expansion with lexical matching:
- When to use expansion vs exact matching?
- Query-dependent routing
- Learned routing functions

**3. Knowledge-Enhanced Sparse Retrieval**

Integrate knowledge graphs:
- Use entity linking to disambiguate
- Knowledge graph expansion (entity → related entities)
- Combine with SPLADE term weights

**4. Continual Learning**

Enable efficient updating:
- Incremental vocabulary expansion
- Adaptive regularization based on data shift
- Federated learning for decentralized deployment

**5. Cross-Lingual and Code-Switching**

Extend to multilingual retrieval:
- Current SPLADE is English-centric
- SPLARE is language-agnostic alternative
- Code-switching queries (multiple languages)

### Research Questions

**Open Problems:**

1. **Theoretical Analysis**: Why does SPLADE generalize better than dense models? What properties of sparse representations enable transfer learning?

2. **Optimal Sparsity**: What is the best sparsity level? Can adaptive sparsity per query/document improve results?

3. **Regularization Design**: Is FLOPS regularization optimal? Would other regularization schemes work better?

4. **Vocabulary Replacement**: Could learned vocabularies (different per domain) improve performance?

5. **Scaling Laws**: How do model size, training data size, and sparsity affect final performance?

---

## Summary: SPLADE and Learned Sparse Retrieval

Learned sparse retrieval represents a fundamental shift in how we approach information retrieval, combining the efficiency and interpretability of lexical methods with the semantic understanding of neural models.

### Key Takeaways:

1. **SPLADE** uses BERT's MLM head + sparse regularization to learn efficient semantic expansions
2. **Evolution path** (v1 → v2 → v3 → CSPLADE) shows consistent improvements
3. **SPLARE** introduces SAE-based alternatives for better multilinguality
4. **Decoder-only approaches** (Mistral-SPLADE) leverage large LLMs for better expansion
5. **Hybrid strategies** (sparse + dense) provide best accuracy when cost allows
6. **Benchmarks** show SPLADE wins on BEIR (out-of-domain), competitive on MS MARCO
7. **Production deployment** is mature: Qdrant, Elasticsearch, Vespa all support SPLADE
8. **Domain applications** (legal, medical, e-commerce) show strong results
9. **Future work** focuses on scalability, multimodal extension, and LLM integration

The field is moving toward three parallel tracks:
- **Vocabulary-based** (SPLADE family): Proven, interpretable, efficient
- **Latent-feature-based** (SPLARE): Better generalization, less interpretable
- **LLM-based** (CSPLADE, Mistral): Higher quality, higher cost

---

## References and Further Reading

### Core SPLADE Papers

- [SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking](https://arxiv.org/abs/2107.05720) - SIGIR 2021
- [SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval](https://arxiv.org/abs/2109.10086) - SIGIR 2022
- [SPLADE-v3: New baselines for SPLADE](https://arxiv.org/abs/2403.06789) - arXiv 2024
- [CSPLADE: Learned Sparse Retrieval with Causal Language Models](https://arxiv.org/abs/2504.10816) - AACL 2025

### Variants and Extensions

- [Mistral-SPLADE: LLMs for better Learned Sparse Retrieval](https://arxiv.org/abs/2408.11119) - arXiv 2024
- [DistilSPLADE and other variants](https://github.com/naver/splade) - SIGIR 2022
- [SPLARE: Learning Retrieval Models with Sparse Autoencoders](https://openreview.net/forum?id=TuFjICawSc)
- [The Role of Vocabularies in Learning Sparse Representations for Ranking](https://arxiv.org/abs/2509.16621) - arXiv 2024

### Integration and Practical Guides

- [Qdrant SPLADE Documentation](https://qdrant.tech/documentation/fastembed/fastembed-splade/)
- [Elastic Learned Sparse Encoder (ELSER)](https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance)
- [Vespa Sparse Retrieval Guide](https://docs.vespa.ai/en/sparse-vectors.html)
- [Official SPLADE Repository](https://github.com/naver/splade)

### Benchmarks and Evaluation

- [BEIR Benchmark](https://github.com/beir-cellar/beir) - 18 diverse IR datasets
- [MS MARCO Benchmark](https://github.com/microsoft/MS-MARCO-Passage-Ranking)
- [Natural Questions (NQ) Dataset](https://github.com/google-research-datasets/natural-questions)
- [TREC Deep Learning Track](https://trec-covid.mesosphere.com/)

### Related Topics

- [Hybrid Search and Dense-Sparse Fusion](https://weaviate.io/blog/hybrid-search-explained)
- [Information Retrieval Foundations](https://lsr-tutorial.github.io/)
- [Learned Sparse Retrieval Tutorial](https://lsr-tutorial.github.io/)

---

**Document Created**: March 1, 2026
**Last Updated**: March 1, 2026
**Status**: Comprehensive Reference

---

## See Also (Cross-References)

→ **references/00-search-recipes/** — Recipe #12: SPLADE for Domain-Specific Search provides implementation guide
→ **references/00-search-recipes/** — Recipe #1: Hybrid Search shows how SPLADE can replace BM25 component
→ **references/00-migration-playbooks/** — Playbook #6: Pure Keyword → SPLADE demonstrates adoption path
→ **references/00-benchmark-matrix/** — SPLADE vs BM25 vs Dense on MS MARCO/BEIR benchmarks
→ **references/05-hybrid-search/** — SPLADE integration in hybrid retrieval pipelines
→ **references/45-neural-reranking-distillation/** — SPLADE + reranker combination for maximum quality
→ **references/01-classical-algorithms-ir/** — Classical algorithms SPLADE improves upon (BM25, TF-IDF)
