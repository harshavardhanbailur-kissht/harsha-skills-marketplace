# Learning to Rank (LTR) - Comprehensive Encyclopedia

> A Complete Reference for ML-Powered Search Relevance: From Theory to Production

## Table of Contents

1. [Foundational Concepts](#foundational-concepts)
2. [Three Core Approaches](#three-core-approaches)
3. [Classical Methods: RankNet → LambdaRank → LambdaMART](#classical-methods)
4. [Modern Neural Ranking](#modern-neural-ranking)
5. [Feature Engineering](#feature-engineering)
6. [Training Data Collection & Bias](#training-data-collection)
7. [Evaluation Metrics](#evaluation-metrics)
8. [Production Deployment](#production-deployment)
9. [Practical Decision Framework](#practical-decision-framework)
10. [Implementation Patterns](#implementation-patterns)

---

## Foundational Concepts

### What is Learning to Rank?

Learning to Rank (LTR), also known as machine-learned ranking (MLR), is the application of supervised machine learning to construct ranking models for information retrieval and recommendation systems. Rather than using hand-crafted ranking functions (BM25, TF-IDF), LTR uses data-driven approaches to learn an optimal ranking function.

**Key Characteristics:**

- **Problem Definition:** Given a query Q and candidate documents {D₁, D₂, ..., Dₙ}, predict the optimal ordering that maximizes user satisfaction
- **Training Data:** Collections of query-document pairs with relevance labels (0-4 scale or binary)
- **Optimization Target:** Ranking metrics (NDCG, MAP, MRR) rather than pointwise classification accuracy
- **Typical Architecture:** Two-stage pipeline with retrieval (first pass) + reranking (LTR second pass)

### Historical Evolution

| Year | Development | Impact |
|------|---|---|
| **2005** | RankNet introduced | First neural network approach to ranking |
| **2007** | LambdaRank published | Gradient-based optimization with NDCG awareness |
| **2010** | LambdaMART released | Gradient boosted trees + Lambda gradients; dominates production |
| **2019** | BERT for ranking | "BERT revolution" (MonoBERT, DuoBERT) |
| **2020+** | Cross-encoder scaling | Knowledge distillation for low-latency inference |

### Traditional vs. Learning to Rank

**Traditional Ranking (BM25, TF-IDF):**
- Fixed, hand-crafted formulas
- Query-document term matching
- Fast and interpretable
- Cannot adapt to domain-specific relevance signals

**Learning to Rank:**
- Data-driven function learned from judgments
- Combines hundreds of heterogeneous features
- Optimizes directly for ranking metrics
- Requires quality training data and careful feature engineering
- Higher computational cost at inference time (mitigated by reranking)

---

## Three Core Approaches

### 1. Pointwise Approaches

**Definition:** Each query-document pair is treated independently. The model predicts a relevance score for each document.

**Loss Function:**
```
L_pointwise = Σ loss(predicted_score_i, true_label_i)
```

**Approaches:**

a) **Regression-based:** Predict continuous relevance scores
```python
# Scikit-learn example
from sklearn.ensemble import GradientBoostingRegressor

model = GradientBoostingRegressor()
model.fit(X_train, y_train)  # y_train ∈ [0, 4]
```

b) **Classification-based:** Binary (relevant/not) or multi-class (0-4 grades)
```python
# Multi-class classification
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(n_classes=5)
model.fit(X_train, y_train)  # y_train ∈ {0, 1, 2, 3, 4}
```

**Advantages:**
- Simple to implement and understand
- Fast training
- Works with standard ML libraries
- Scales well to large datasets

**Disadvantages:**
- Ignores document-to-document relationships
- Doesn't directly optimize ranking metrics
- High-relevance and low-relevance errors treated equally
- Poor ranking context awareness

**When to Use:**
- Baseline systems
- When labeled data is straightforward (clean absolute scores)
- Large datasets with limited computational budget
- When individual document quality matters more than ranking order

---

### 2. Pairwise Approaches

**Definition:** The model learns to order pairs of documents correctly. Loss is computed on whether document A should rank higher than document B.

**Loss Function:**
```
L_pairwise = Σ loss(score_i - score_j, 1)  for all discordant pairs
```

**Key Algorithms:**

#### a) **RankNet (Burges et al., 2005)**

First neural network approach using pairwise loss. Treats ranking as a classification problem on pairs.

**Architecture:**
- Two-layer neural network
- Pairwise cross-entropy loss
- Gradient via backpropagation

```python
# Conceptual implementation
class RankNet:
    def __init__(self, hidden_dim=128):
        self.net = NeuralNetwork(input_dim=n_features,
                                 hidden_dim=hidden_dim,
                                 output_dim=1)

    def pairwise_loss(self, scores_i, scores_j, label):
        # label = 1 if i should rank higher than j
        prob_ij = sigmoid(scores_i - scores_j)
        return -label * log(prob_ij) - (1 - label) * log(1 - prob_ij)
```

#### b) **LambdaRank (Burges et al., 2007)**

Improves RankNet by scaling gradients by the change in NDCG when swapping a pair.

**Key Innovation:** Lambda gradient
```
λ_ij = |NDCG_change_ij| × learning_rate
```

This makes the model NDCG-aware without computing NDCG loss directly.

#### c) **LambdaMART (Burges, 2010)**

Combines LambdaRank with MART (Multiple Additive Regression Trees) = gradient boosted trees.

**Why It Dominates Production:**
- Uses gradient boosting (fast, scalable, handles non-linearity)
- Lambda-based gradients optimize NDCG
- Lower inference latency than neural networks
- Excellent empirical performance
- Widely supported (XGBoost, LightGBM, RankLib)

**LambdaMART with LightGBM:**
```python
import lightgbm as lgb

# Data format: query groups, features, and labels
train_data = lgb.Dataset(X_train, label=y_train,
                         group=[10, 20, 30, 40])  # 4 queries with doc counts

params = {
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'num_leaves': 31,
    'learning_rate': 0.05,
}

model = lgb.train(params, train_data, num_boost_round=1000)
predictions = model.predict(X_test)
```

**Advantages:**
- Directly optimizes for ranking metrics (NDCG)
- Pairwise comparisons reflect real ranking decisions
- Efficient gradient computation
- Less sensitive to noise than pointwise
- Standard production choice (used by Bing, Yahoo, Yandex)

**Disadvantages:**
- Doesn't model entire ranking context
- Quadratic complexity in label space (many pairs)
- Complexity vs. implementation difficulty trade-off

**When to Use:**
- Production search systems
- When noisy training data (clicks, implicit feedback)
- When NDCG optimization is critical
- Budget allows training complexity

---

### 3. Listwise Approaches

**Definition:** The entire ranked list is treated as a unit. Loss is computed on the entire ranking.

**Loss Function:**
```
L_listwise = loss(predicted_ranking, ground_truth_ranking)
```

**Key Algorithms:**

#### a) **ListNet (Cao et al., 2007)**

Uses Plackett-Luce model to define probability distribution over permutations.

```python
# Conceptual: minimize cross-entropy between distributions
def listnet_loss(predicted_scores, true_labels):
    # Convert scores to probability distributions
    pred_dist = softmax(predicted_scores)
    true_dist = softmax(true_labels)

    # Cross-entropy between distributions
    loss = -Σ true_dist[i] * log(pred_dist[i])
    return loss
```

#### b) **SoftRank**

Treats each score as a Gaussian distribution. Smooths NDCG by marginalizing over rank distributions.

**Key Idea:** Approximate indicator functions with smooth distributions

```
P(rank_i = k) = ∫∫∫ P(score_i = s_i) ∏ P(score_j ≠ s_i) ds_i
```

#### c) **ApproxNDCG**

Directly approximates NDCG loss by smoothing the indicator function used in DCG computation.

```
NDCG_approx = DCG(scores) / IDCG
  where DCG = Σ_i (2^rel_i - 1) / log₂(i+1) × smooth_indicator(rank_i)
```

**Advantages:**
- Directly optimizes ranking metrics (NDCG)
- Considers entire list context
- Better theoretical alignment with evaluation metrics
- Often achieves highest quality rankings

**Disadvantages:**
- High computational complexity (O(n² log n) or higher)
- More difficult to implement correctly
- Unstable gradients in some cases
- Training time significantly longer

**When to Use:**
- When quality is paramount (cost of bad rankings is high)
- When you have sufficient computational resources
- Offline ranking systems (not real-time constraint)
- Medium-sized candidate sets (100-1000 documents)

**Comparison Table:**

| Property | Pointwise | Pairwise | Listwise |
|----------|-----------|----------|----------|
| Computational Cost | Low | Medium | High |
| Metric Awareness | Poor | Good (Lambda) | Excellent (Direct) |
| Implementation | Easy | Medium | Hard |
| Production Adoption | Low | **High** | Growing |
| Training Stability | Good | Good | Moderate |

---

## Classical Methods

### RankNet Deep Dive

**Architecture:**

```
Query Features ─┐
               ├─ Shared Hidden Layer (128 units) ─┐
Doc Features  ─┘                                   ├─ Output: Score
                                                   │
                            ┌──────────────────────┘
                            │
                     Pairwise Cross-Entropy
```

**Training:**
1. Sample query Q with document pairs (D_i, D_j)
2. Pass both through network independently
3. Compute cross-entropy loss on pair ordering
4. Backprop gradients
5. Repeat for all pairs

**Why It Failed for Production:**
- Neural networks were computationally expensive (2005)
- Difficult to deploy in real-time systems
- Superseded by LambdaRank's elegant gradient innovation

---

### LambdaRank to LambdaMART Progression

**LambdaRank Insight:**

Instead of computing full gradient and then scaling by NDCG improvement:

```
Traditional: grad = compute_gradient(network)
             weighted_grad = grad × NDCG_improvement

LambdaRank: grad = NDCG_improvement × compute_gradient_direction(pair)
```

The key is computing "Lambda" = gradient × NDCG improvement directly.

**Mathematics:**

For a discordant pair (i, j) where document i has lower true relevance than j but scores higher:

```
λ_ij = |Z| / (1 + exp(s_i - s_j))

where Z = |NDCG@k(ideal) - NDCG@k(swapped pair)|
```

**LambdaMART Implementation with XGBoost:**

```python
import xgboost as xgb

# Training data preparation
# X_train: feature matrix
# y_train: relevance labels
# group_train: number of documents per query

dtrain = xgb.DMatrix(X_train, label=y_train)
dtrain.set_group(group_train)

params = {
    'objective': 'rank:ndcg',  # Metric to optimize
    'ndcg_eval_at': [5, 10],
    'max_depth': 6,
    'eta': 0.1,
    'subsample': 0.8,
}

# Train with unbiased LambdaMART (handles position bias)
bst = xgb.train(
    params,
    dtrain,
    num_boost_round=100,
    evals=[(dtrain, 'train')],
)

# Predict
predictions = bst.predict(xgb.DMatrix(X_test))
```

**Why Gradient Boosted Trees + Lambda:**
- GBDTs efficiently handle non-linear feature interactions
- Lambda gradients encode NDCG optimization
- Combination is robust to noise
- Fast inference (simple tree traversal)
- Easy feature importance analysis

---

## Modern Neural Ranking

### The BERT Revolution

**MonoBERT (2019):** Cross-encoder that jointly encodes query and document

```
Query: "best machine learning textbooks"
Document: "A comprehensive guide to learning..."

Input: [CLS] best machine learning... [SEP] A comprehensive... [SEP]
        └─────── Query ────────────┘         └── Document ──┘

BERT Encoder (12 layers, 12 attention heads)
         ↓
Output: [CLS] embedding (sequence of 768-dim vectors)
         ↓
Classification Head (2 classes: relevant/not relevant)
         ↓
Score ∈ [0, 1]
```

**Advantages:**
- Full token-level interactions
- Leverages pre-trained knowledge
- Can capture semantic nuances
- Fine-tunes in hours with GPUs

**Disadvantages:**
- Latency: ~5-50ms per document
- Cannot batch different queries
- Expensive for large candidate sets
- Requires GPU for practical deployment

### DuoBERT: Pairwise Neural Ranking

**Innovation:** Instead of predicting relevance scores, predict which document in a pair is more relevant.

```
Input: [CLS] query [SEP] doc_A [SEP] doc_B [SEP]

BERT Encoder
    ↓
Classification Head: "Which is more relevant?"
    ↓
Logit ∈ ℝ (positive = A > B, negative = B > A)
```

**Advantages:**
- More directly aligned with ranking objective
- Faster convergence during fine-tuning
- Can be applied in multi-stage pipeline

**Typical Pipeline:**
```
BM25 Retrieval (fast 1st pass)
    ↓ (top 100)
MonoBERT Reranking (fast single-pass ranking)
    ↓ (top 20)
DuoBERT Fine Reranking (pairwise comparisons)
    ↓ (top 10 final results)
```

---

## Feature Engineering

### Feature Categories

#### 1. Query-Dependent Features

Computed fresh for each query; reflect how query relates to document.

**Statistical Features:**
```
BM25(query, doc)           # Okapi BM25 score
TF-IDF(query, doc)         # TF-IDF overlap
Query-Coverage             # Fraction of query terms in doc
Term-Match-Count           # Number of query terms found
Exact-Phrase-Match         # Does document contain exact query phrase
```

**Implementation:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi

# BM25 scoring
corpus = [doc.split() for doc in documents]
bm25 = BM25Okapi(corpus)
bm25_scores = bm25.get_scores(query.split())

# TF-IDF scoring
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)
query_vec = vectorizer.transform([query])
tfidf_scores = X.dot(query_vec.T).toarray().flatten()
```

#### 2. Query-Independent (Static) Features

Computed once per document; don't change with query.

**Popularity & Authority:**
```
PageRank                    # Graph-based importance
InLink-Count               # Number of incoming links
OutLink-Count              # Number of outgoing links
Domain-Authority           # Domain trust score
```

**Content Quality:**
```
Document-Length            # Word count
Title-Length               # Titular prominence
H-Index (headings)         # Structural quality
Readability-Score          # FLESCH-KINCAID or similar
```

**Freshness:**
```
Creation-Date              # When document published
Update-Frequency           # How often updated
Staleness-Days             # Days since last update
```

#### 3. Query-Document Interaction Features

Capture specific relationships.

**Field-Level Matching:**
```python
def compute_field_features(query, doc):
    features = {}

    # Title match
    title_bm25 = bm25_score(query, doc.title)
    features['title_bm25'] = title_bm25

    # Body match
    body_bm25 = bm25_score(query, doc.body)
    features['body_bm25'] = body_bm25

    # Title vs body ratio
    features['title_body_ratio'] = title_bm25 / (body_bm25 + 1e-6)

    return features
```

**Position-Based Features:**
```python
def compute_position_features(query_terms, doc):
    features = {}

    # Where do first query terms appear?
    first_match_pos = find_first_match(query_terms, doc)
    features['first_match_position'] = first_match_pos

    # Distance between query terms
    term_positions = [find_all_positions(term, doc)
                      for term in query_terms]
    features['term_clustering'] = compute_variance(term_positions)

    return features
```

#### 4. Behavioral Features

From user interactions (clicks, dwells, impressions).

```
Click-Count                # Number of clicks
Click-Through-Rate (CTR)   # Clicks / Impressions
Dwell-Time (avg)           # Average time on page
Skip-Rate                  # Skips / Impressions (position-biased)
Conversion-Rate            # Desired action rate
```

**Critical Note on Bias:** Click-based features suffer from position bias (higher-ranked items get more clicks regardless of relevance). See [Training Data Collection](#training-data-collection) for mitigation.

### Feature Normalization & Scaling

**Why Normalize:**
- Features have different ranges (BM25: 0-100+, CTR: 0-1)
- Tree-based models are scale-invariant
- Neural models require normalized input
- Gradient-based optimization converges faster

**Methods:**

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Standard scaling (Z-score normalization)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# Min-max scaling to [0, 1]
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_train)

# Log scaling for heavy-tailed distributions
X_log = np.log1p(X)  # log(1 + x)

# Custom: percentile-based scaling
def percentile_scale(x, p_lower=5, p_upper=95):
    lower = np.percentile(x, p_lower)
    upper = np.percentile(x, p_upper)
    return np.clip((x - lower) / (upper - lower), 0, 1)
```

### Feature Importance Analysis

**With LightGBM:**
```python
import lightgbm as lgb
import matplotlib.pyplot as plt

# Feature importance scores
importance = lgb_model.feature_importance(importance_type='gain')
feature_names = ['BM25', 'TF-IDF', 'PageRank', ...]

# Visualize
plt.barh(feature_names, importance)
plt.xlabel('Gain')
plt.show()

# Top features
top_features = sorted(zip(feature_names, importance),
                      key=lambda x: x[1], reverse=True)[:10]
for name, score in top_features:
    print(f"{name}: {score:.2f}")
```

**With SHAP Values:**
```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

shap.summary_plot(shap_values, X_test, feature_names=feature_names)
```

---

## Training Data Collection

### Types of Training Data

#### 1. Explicit Judgments

Human raters assign relevance grades to query-document pairs.

**Relevance Scale (4-point):**
```
0: Not relevant
1: Somewhat relevant
2: Relevant
3: Highly relevant
```

**Advantages:**
- Clean, unbiased labels
- High quality for metric optimization
- Easy to reason about

**Disadvantages:**
- Expensive (human labor)
- Slow (weeks to collect)
- Limited scale (thousands of pairs vs. millions possible)
- Rater disagreement/inconsistency

**Cost Estimate:**
```
100 queries × 20 judgments each
= 2,000 judgments
At $0.10/judgment = $200
Timeline: 1-2 weeks
```

#### 2. Implicit Feedback

Inferred from user interactions.

**Click Data:**
```
Query: "machine learning book"
Result 1: "The ML Textbook" ← Clicked
Result 2: "AI Overview" ← Not clicked
Result 3: "Deep Learning Guide" ← Clicked
```

**Implicit Signals:**
```
- Click vs. non-click
- Dwell time (seconds on page)
- Scroll depth (% of page viewed)
- Return-to-SERP (abandoned result)
- Conversions (purchases, sign-ups)
```

**Advantages:**
- Massive scale (millions of interactions daily)
- Real user behavior
- Continuous data collection
- No human labeling cost

**Disadvantages:**
- **Position Bias:** Users preferentially click higher-ranked results
- **Presentation Bias:** Document appearance affects clicks
- **Trust Bias:** Users click known brands
- Noisy and indirect signal
- Aggregation challenges

### The Position Bias Problem

**Issue:** A highly relevant document ranked 10th gets fewer clicks than a mediocre document ranked 1st.

```
Ideal Rankings:
Doc A (Relevant) ranked 1st → 80% click rate
Doc B (Mediocre) ranked 1st → 20% click rate

With Position Bias:
Doc A ranked 5th → 20% click rate (due to position, not relevance)
Doc B ranked 1st → 80% click rate (position advantage)

If we train on observed clicks, model learns wrong ordering!
```

### Debiasing Approaches

#### 1. **Position-Based Click Model (PBM)**

Assume click probability = relevance × position_bias

```
P(click | relevance, position) = P(exam | position) × P(click | exam, relevance)

where exam = "user examined the result"
```

**Inference:**
```
If we observe click pattern across positions, we can estimate
position_bias separately from relevance using EM algorithm
```

**Implementation:**
```python
def position_bias_debiasing(clicks, positions, queries):
    """
    EM algorithm to estimate relevance from position-biased clicks
    """
    # E-step: estimate click probability without position bias
    exam_probs = estimate_examination_probs(clicks, positions)

    # M-step: estimate relevance given examination
    relevance = clicks / (exam_probs + 1e-6)

    return relevance
```

#### 2. **Randomized Ranking (A/A Testing)**

Occasionally show random rankings to measure unbiased relevance.

```python
def randomized_ranking_experiment():
    """
    1% of searches get random ranking
    Use this data to build unbiased training set
    """
    if random() < 0.01:
        ranking = shuffle(ranking)  # Randomize
    return ranking

# Collect clicks on randomized rankings
# Position is now independent of typical relevance signals
# Much more reliable for training
```

**Trade-off:** Degraded user experience (1% of searches) for better models.

#### 3. **Interleaving Experiments**

Compare two rankings by interleaving results.

```
Query: "best restaurants NYC"

Ranking A: [Restaurant 1, Restaurant 3, Restaurant 5, ...]
Ranking B: [Restaurant 2, Restaurant 4, Restaurant 6, ...]

Interleaved: [Restaurant 1, Restaurant 2, Restaurant 3, Restaurant 4, ...]
              (from A)     (from B)     (from A)     (from B)

Which restaurants get clicked?
→ Direct comparison of rankings without position bias
```

---

## Evaluation Metrics

### NDCG (Normalized Discounted Cumulative Gain)

**Intuition:** Rewards relevant documents at the top, with exponential decay for lower positions.

**Formula:**

```
DCG@k = Σ_{i=1}^{k} (2^{rel_i} - 1) / log₂(i+1)

NDCG@k = DCG@k / IDCG@k

where:
  rel_i = relevance of document at position i ∈ {0, 1, 2, 3, 4}
  IDCG = DCG of ideal ranking (best possible)
```

**Concrete Example:**

```
Query: "machine learning books"
Judgment: Doc A=4, Doc B=3, Doc C=2, Doc D=0, ...

Ranking 1: [A, B, C, D]
  DCG = (2^4-1)/log₂2 + (2^3-1)/log₂3 + (2^2-1)/log₂4 + 0
      = 15/1 + 7/1.585 + 3/2 + 0
      = 15 + 4.42 + 1.5 = 20.92

Ranking 2: [B, A, D, C]
  DCG = 7/1 + 15/1.585 + 0 + 3/3.32
      = 7 + 9.46 + 0 + 0.90 = 17.36

IDCG = [A, B, C, ...] = 20.92
NDCG@4 (Ranking 1) = 20.92 / 20.92 = 1.0
NDCG@4 (Ranking 2) = 17.36 / 20.92 = 0.829
```

**Properties:**
- Range: [0, 1] (normalized)
- Position-aware (exponential decay)
- Graded relevance support
- Most widely used in industry

**Python:**
```python
from sklearn.metrics import ndcg_score

y_true = [3, 2, 3, 0, 1, 2]  # Relevance grades
y_score = [0.9, 0.5, 0.8, 0.1, 0.3, 0.7]  # Predicted scores

ndcg = ndcg_score(y_true, y_score)  # NDCG@all
ndcg_5 = ndcg_score(y_true, y_score, k=5)  # NDCG@5
```

### MAP (Mean Average Precision)

**Formula:**

```
AP@k = (1/min(m, k)) × Σ_{i=1}^{k} P(i) × rel(i)

where:
  P(i) = precision at position i (relevant items so far / i)
  rel(i) = binary relevance {0, 1} at position i
  m = total relevant documents

MAP = average of AP across all queries
```

**Properties:**
- Binary relevance only (treats 2-relevant same as 4-relevant)
- Position-aware but less aggressively than NDCG
- Less suitable for graded judgments
- Historically important, less used now

**When to Use:** Metrics competitions (TREC), legacy systems

---

### MRR (Mean Reciprocal Rank)

**Formula:**

```
RR = 1 / (rank of first relevant item)
MRR = average RR across queries
```

**Example:**
```
Query 1: [Irrelevant, Relevant, Relevant, ...] → RR = 1/2 = 0.5
Query 2: [Relevant, ...] → RR = 1
Query 3: [Irrelevant, Irrelevant, Irrelevant, ...] → RR = 0

MRR = (0.5 + 1 + 0) / 3 = 0.5
```

**Properties:**
- Only cares about first relevant item
- Binary relevance
- Good for "finding the answer" tasks (factoid QA)
- Poor for ranking tasks

**When to Use:** Question-answering systems, "find X" queries

---

### ERR (Expected Reciprocal Rank)

**Formula:**

```
ERR@k = Σ_{i=1}^{k} (1/i) × P(user stops at position i)

P(user stops at i) = Σ_{j=1}^{i} [∏_{l=1}^{j-1} (1 - rel_l)] × rel_j

where rel_i ∈ [0, 1] (normalized relevance)
```

**Intuition:** Models user as examining results sequentially, stopping when satisfied.

**Advantages over NDCG:**
- User-model based (cascade/satisficing model)
- Probabilistically rigorous
- Can use graded relevance
- Better for understanding user satisfaction

**Disadvantages:**
- Less commonly used in practice
- Harder to interpret
- Requires normalized graded relevance

**Python Implementation:**
```python
def compute_err(relevances, k=10):
    """
    Compute Expected Reciprocal Rank
    relevances: array of relevance grades
    """
    err = 0.0
    cumulative_prob = 1.0

    for i in range(min(k, len(relevances))):
        rel = relevances[i] / 4.0  # Normalize to [0, 1]
        prob_stop = cumulative_prob * rel / (i + 1)
        err += prob_stop
        cumulative_prob *= (1 - rel)

    return err
```

---

### Precision@K and Recall@K

**Formulas:**

```
Precision@K = (Relevant documents in top K) / K
Recall@K = (Relevant documents in top K) / Total relevant documents
```

**Properties:**
- Binary relevance only
- Position-unaware (top-1 and top-K treated equally)
- Interpretable percentages
- Good for monitoring coverage

**Not recommended for** primary ranking evaluation (use NDCG instead).

### Offline vs. Online Metrics

**Offline Metrics:** Computed on held-out test set with human judgments
```
Advantages: Reproducible, controlled, fast
Disadvantages: May not correlate with real user satisfaction
```

**Online Metrics:** Measured from live user traffic
```
NDCG-like:  Click-based approximations
MRR-like:   Position of first click
CTR:        Click-through rate
Conversion: Purchase, signup, etc.
Dwell time: Time on page
```

**Key Finding:** Offline and online metrics often have weak correlation. Always validate with online A/B testing.

---

## Production Deployment

### Typical Ranking Pipeline

```
Query
  ↓
[Stage 1] Retrieval (BM25, ES, Vector DB)
  ├─ Input: 1 query
  ├─ Output: top 1000 candidates
  └─ Latency: 10-50ms
  ↓
[Stage 2] Reranking (LambdaMART)
  ├─ Input: 1000 candidates + features
  ├─ Output: top 100 reranked
  └─ Latency: 20-100ms (vectorized)
  ↓
[Stage 3] Final Ranking (Optional: BERT, Business Rules)
  ├─ Input: 100 candidates
  ├─ Output: top 10 final results
  └─ Latency: 5-50ms (depending on model)
  ↓
Response to User
```

### Elasticsearch Integration

**Native LTR (Elasticsearch 8.13+):**

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['localhost:9200'])

# Define features
features = [
    {
        "definition": {
            "agg_name": "agg_match",
            "agg": {
                "filter": {
                    "match": {"title": "_query"}
                }
            }
        }
    },
    {
        "definition": {
            "agg_name": "agg_pagerank",
            "agg": {
                "sum": {
                    "field": "pagerank"
                }
            }
        }
    }
]

# Create feature set
es.indices.create(index="my_index")
es.indices.put_alias(index="my_index", name="features")

# Log training features
query = {
    "query": {
        "match": {"title": "machine learning"}
    },
    "aggs": {
        # Feature aggregations
    }
}
```

**Model Deployment:**

```python
# Train model outside ES (XGBoost, LightGBM)
# Export as JSON

model_json = {
    "definition": {
        "ensemble": {
            "models": [
                {
                    "name": "my_lambdamart",
                    "model": "linear_regression",
                    "weights": [0.1, 0.3, 0.5, 0.1]
                }
            ],
            "weights": [1.0]
        }
    }
}

# Upload to ES
es.indices.put_settings(index="my_index", body={
    "ltr": {
        "model": model_json
    }
})

# Use in query
search_query = {
    "rescore": {
        "window_size": 50,
        "query": {
            "rescore_query": {
                "sltr": {
                    "model": "my_lambdamart",
                    "params": {
                        "keywords": "machine learning"
                    }
                }
            },
            "weight": 2.0
        }
    }
}

results = es.search(index="my_index", body=search_query)
```

### XGBoost + LambdaMART Production Pattern

**Training:**

```python
import xgboost as xgb
import json
import joblib

# Load training data
train_data = pd.read_csv('training_data.csv')
X_train = train_data[feature_cols]
y_train = train_data['label']
groups_train = train_data.groupby('query_id').size().values

# Create DMatrix with group information
dtrain = xgb.DMatrix(X_train, label=y_train)
dtrain.set_group(groups_train)

# Train LambdaMART
params = {
    'objective': 'rank:ndcg',
    'metric': 'ndcg@10',
    'max_depth': 6,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'tree_method': 'hist',
    'device': 'cuda',
}

model = xgb.train(
    params,
    dtrain,
    num_boost_round=500,
    evals=[(dtrain, 'train')],
    early_stopping_rounds=50,
)

# Save model
model.save_model('ltr_model.xgb')
joblib.dump(feature_scaler, 'scaler.pkl')
```

**Inference:**

```python
class LTRRanker:
    def __init__(self, model_path, scaler_path):
        self.model = xgb.Booster(model_file=model_path)
        self.scaler = joblib.load(scaler_path)

    def rank(self, query, candidates):
        """
        Rank candidates for a query

        Args:
            query: Query string
            candidates: List of {'id': ..., 'features': {...}} dicts

        Returns:
            List of candidate IDs in ranked order
        """
        # Extract features
        feature_matrix = np.array([
            [cand['features'][f] for f in self.feature_names]
            for cand in candidates
        ])

        # Normalize features
        feature_matrix = self.scaler.transform(feature_matrix)

        # Score with XGBoost
        dmatrix = xgb.DMatrix(feature_matrix)
        scores = self.model.predict(dmatrix)

        # Sort by score descending
        ranked_indices = np.argsort(-scores)
        return [candidates[i]['id'] for i in ranked_indices]

# Inference server
from flask import Flask, request, jsonify

app = Flask(__name__)
ranker = LTRRanker('ltr_model.xgb', 'scaler.pkl')

@app.route('/rank', methods=['POST'])
def rank_endpoint():
    data = request.json
    query = data['query']
    candidates = data['candidates']

    ranked = ranker.rank(query, candidates)

    return jsonify({'ranked_ids': ranked})
```

### BERT Reranker: Latency Optimization

**Problem:** BERT inference is slow (5-50ms per document).

**Solutions:**

1. **Truncation:** Limit token count
```python
def rank_with_bert(query, candidates, max_tokens=512):
    scores = []
    for doc in candidates[:100]:  # Only top-100
        # Truncate to max_tokens
        text = f"{query} [SEP] {doc['text'][:500]}"
        tokens = tokenizer(text,
                          truncation=True,
                          max_length=max_tokens,
                          return_tensors='pt')
        with torch.no_grad():
            logits = model(**tokens).logits[:, 0]
        scores.append(logits[0])

    return scores
```

2. **Batching:** Process multiple documents simultaneously
```python
# Batch size 32 instead of 1
batches = [candidates[i:i+32] for i in range(0, len(candidates), 32)]
all_scores = []

for batch in batches:
    inputs = tokenizer(
        [f"{query} [SEP] {doc['text']}" for doc in batch],
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors='pt'
    )

    with torch.no_grad():
        logits = model(**inputs).logits[:, 0]

    all_scores.extend(logits.cpu().numpy())
```

3. **Model Distillation:** Train smaller model to mimic BERT
```python
# Teacher: Large BERT (monoBERT)
teacher_model = AutoModelForSequenceClassification.from_pretrained(
    'cross-encoder/ms-marco-MiniLM-L-6-v2'
)

# Student: Tiny model (TinyBERT with 2 layers)
student_model = AutoModelForSequenceClassification.from_pretrained(
    'sentence-transformers/all-MiniLM-L6-v2'
)

# Knowledge distillation training
for epoch in range(num_epochs):
    for batch in train_dataloader:
        student_outputs = student_model(**batch)
        teacher_outputs = teacher_model(**batch)

        # KL divergence loss between teacher and student
        loss = F.kl_div(
            F.log_softmax(student_outputs.logits, dim=-1),
            F.softmax(teacher_outputs.logits, dim=-1),
            reduction='batchmean'
        )

        loss.backward()
        optimizer.step()
```

**Latency Comparison:**
```
Full BERT (12 layers):  45ms per doc × 100 docs = 4.5s
+ Distillation:        15ms per doc × 100 docs = 1.5s (70% reduction)
+ Truncation:          8ms per doc × 100 docs = 0.8s (82% reduction)
+ GPU optimizations:   3ms per doc × 100 docs = 0.3s (93% reduction)
```

---

## Practical Decision Framework

### When to Implement LTR

**Strong Indicators (Go for LTR):**
```
✓ > 10K queries monthly
✓ > 100K documents in corpus
✓ Existing relevance metrics show room for improvement
✓ Team has ML expertise
✓ Search relevance is critical business metric
✓ Can invest 2-4 weeks for initial implementation
```

**Skip LTR If:**
```
✗ < 1K queries monthly (too few for training)
✗ Simple domain (FAQ, small catalog)
✗ Perfect BM25 performance already
✗ No ML infrastructure
✗ Needs immediate results
```

### Minimum Data Requirements

**For Baseline LTR Model:**
```
- Minimum: 500 queries × 20 judgments = 10K labeled pairs
- Better: 2,000 queries × 50 judgments = 100K labeled pairs
- Gold: 10,000 queries × 100 judgments = 1M labeled pairs

Rule of thumb: 50-100 queries per each model parameter
```

**For Neural Models (BERT):**
```
- Minimum: 5,000 labeled query-document pairs
- Better: 50,000+ labeled pairs
- Can leverage pre-trained models with less data
```

### Phased Implementation Strategy

**Phase 1: Baseline (Week 1-2)**
```
1. Collect 500-1000 explicit judgments (human raters)
2. Train pointwise logistic regression model
3. Deploy as simple reranker on top of BM25
4. Measure offline NDCG improvement
5. Decision: Proceed to pairwise if >5% gain
```

**Phase 2: Pairwise (Week 3-4)**
```
1. Expand training set to 3,000+ queries
2. Train LambdaMART with LightGBM
3. Implement feature engineering pipeline
4. A/B test against baseline (4-week online evaluation)
5. Decision: Scale if statistically significant lift (p < 0.05)
```

**Phase 3: Production (Week 5-8)**
```
1. Instrument feature logging
2. Build feature store for consistent feature computation
3. Setup automated model retraining pipeline (monthly)
4. Deploy to production with monitoring
5. Monitor NDCG, CTR, conversion metrics
```

**Phase 4: Advanced (Month 3+)**
```
1. Add neural reranking (BERT cross-encoder)
2. Implement online learning from click feedback
3. Multi-stage ranking pipeline
4. Personalization by user cohort
```

### Build vs. Buy Analysis

**Build LTR Internally:**

Pros:
- Full control over model behavior
- Competitive advantage (custom features)
- Cost savings (long-term)
- Integration with existing systems

Cons:
- Engineering effort (3-4 months)
- Ongoing maintenance
- Need ML expertise
- High initial cost

**Buy Commercial Solution (Algolia, Elasticsearch LTR, Vespa, etc.):**

Pros:
- Quick deployment (days)
- Vendor support
- Less maintenance
- Integrated with search platform

Cons:
- Vendor lock-in
- Limited customization
- Monthly costs ($5K-$50K+)
- Feature constraints

**Recommendation:**
- Small teams, startup: **Buy** (Elasticsearch, Algolia)
- Large teams, scale needed: **Build** (LightGBM + custom features)
- Hybrid: Buy platform, build custom model on top

---

## Implementation Patterns

### Feature Store Pattern

Consistent feature computation across training and inference.

```python
class FeatureStore:
    def __init__(self):
        self.features = {}
        self.cache = {}

    def register_feature(self, name, compute_fn):
        """Register a feature computation function"""
        self.features[name] = compute_fn

    def compute(self, query, doc):
        """Compute all features for query-doc pair"""
        key = (query, doc)

        if key in self.cache:
            return self.cache[key]

        feature_dict = {}
        for name, compute_fn in self.features.items():
            try:
                feature_dict[name] = compute_fn(query, doc)
            except Exception as e:
                logger.warning(f"Failed to compute {name}: {e}")
                feature_dict[name] = 0.0

        self.cache[key] = feature_dict
        return feature_dict

# Usage
store = FeatureStore()
store.register_feature('bm25', lambda q, d: bm25_score(q, d.text))
store.register_feature('pagerank', lambda q, d: d.pagerank)
store.register_feature('freshness_days', lambda q, d: (now() - d.updated_at).days)

features = store.compute("machine learning", doc)
# {'bm25': 15.2, 'pagerank': 0.85, 'freshness_days': 7}
```

### Online Learning Pattern

Continuously improve model from user feedback.

```python
class OnlineLTRLearner:
    def __init__(self, base_model, online_lr=0.01):
        self.base_model = base_model
        self.online_lr = online_lr

    def rank(self, query, candidates):
        """Return ranking and store for feedback"""
        features = [self.extract_features(query, c) for c in candidates]
        scores = self.base_model.predict(features)
        ranking = np.argsort(-scores)

        # Store for potential feedback
        self.last_ranking = {
            'query': query,
            'candidates': candidates,
            'ranking': ranking,
            'timestamp': time.time()
        }

        return ranking

    def feedback(self, click_position):
        """Update from user click"""
        # Higher-ranked documents that got clicked = good
        # Higher-ranked documents that got skipped = bad

        ranking = self.last_ranking['ranking']

        for i, doc_idx in enumerate(ranking):
            if i < click_position:
                # Documents above click: positive signal
                self.learn_pair(ranking[i], ranking[i+1], positive=True)
            elif i > click_position:
                # Documents below click: negative signal
                self.learn_pair(ranking[i], ranking[i-1], positive=False)

    def learn_pair(self, doc_a_idx, doc_b_idx, positive):
        """Online pairwise learning"""
        # In production: stream to retraining pipeline
        self.training_buffer.append({
            'pair': (doc_a_idx, doc_b_idx),
            'label': positive
        })
```

### Monitoring & Validation

```python
class LTRMonitor:
    def __init__(self, model):
        self.model = model
        self.metrics = {
            'ndcg_10': [],
            'mrr': [],
            'latency_ms': [],
            'feature_distribution': {}
        }

    def evaluate_batch(self, queries, judgments):
        """Daily evaluation on held-out set"""
        ndcg_scores = []

        for query, docs, true_labels in zip(queries, docs_list, judgments):
            predictions = self.model.predict(docs)
            ndcg = compute_ndcg(predictions, true_labels, k=10)
            ndcg_scores.append(ndcg)

        avg_ndcg = np.mean(ndcg_scores)
        self.metrics['ndcg_10'].append(avg_ndcg)

        # Alert if drop > 5%
        if len(self.metrics['ndcg_10']) > 1:
            prev_ndcg = self.metrics['ndcg_10'][-2]
            if (prev_ndcg - avg_ndcg) / prev_ndcg > 0.05:
                alert("NDCG drop detected")

    def check_feature_drift(self, features):
        """Monitor feature distribution changes"""
        for feature_name, values in features.items():
            new_dist = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }

            if feature_name in self.metrics['feature_distribution']:
                old_dist = self.metrics['feature_distribution'][feature_name]
                if abs(new_dist['mean'] - old_dist['mean']) > old_dist['std']:
                    alert(f"Feature drift in {feature_name}")

            self.metrics['feature_distribution'][feature_name] = new_dist
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Position Bias in Training Data

**Problem:** Train model on clicked results → model learns position bias, not relevance

**Solution:**
```python
# Use randomized experiment data
if random() < 0.01:  # 1% of searches randomized
    ranking = shuffle(ranking)

# OR implement PBM debiasing
clicks_debiased = apply_pbm_debiasing(observed_clicks, positions)
```

### Pitfall 2: Feature Leakage

**Problem:** Using features that aren't available at inference time (e.g., future clicks)

**Solution:**
```python
# Training: Use only historical information
train_features = [
    'bm25',           # ✓ Available at inference
    'pagerank',       # ✓ Pre-computed static
    'query_type',     # ✓ From query analysis
    # 'future_clicks',  # ✗ Not available at inference!
]
```

### Pitfall 3: Offline-Online Metric Misalignment

**Problem:** Model optimizes NDCG offline but doesn't improve user satisfaction online

**Solution:**
```
1. Validate metrics correlation
2. Add online metrics to evaluation
3. Run longer A/B tests (>2 weeks for stability)
4. Monitor multiple metrics simultaneously
```

### Pitfall 4: Model Degradation Over Time

**Problem:** Model trained on old data becomes stale

**Solution:**
```python
# Monthly retraining pipeline
@scheduled_job('cron', id='monthly_retrain', hour=2, day_of_month=1)
def retrain_ltr_model():
    # Collect new judgments since last training
    new_judgments = fetch_judgments(since=last_training_date)

    # Combine with historical
    all_judgments = combine_old_new(historical_judgments, new_judgments)

    # Retrain
    new_model = train_lambdamart(all_judgments)

    # Validate on hold-out test set
    val_ndcg = evaluate(new_model, val_set)

    # If improvement, deploy
    if val_ndcg > current_model_ndcg:
        deploy_model(new_model)
```

---

## Summary & Comparison

### Quick Decision Tree

```
Your Situation:
├─ Have explicit labels (human judgments)
│  ├─ < 5K labeled pairs → Start with Pointwise
│  └─ > 10K labeled pairs → Jump to LambdaMART (Pairwise)
│
├─ Only have click data (implicit)
│  ├─ Implement position bias debiasing
│  └─ Train LambdaMART on debiased clicks
│
└─ Want best possible quality (cost not constraint)
   ├─ Multiple-stage: BM25 → LambdaMART → BERT
   └─ Optimize NDCG with listwise approach if scale allows
```

### Algorithm Comparison

| Aspect | Pointwise | Pairwise | Listwise | BERT |
|--------|-----------|----------|----------|------|
| **NDCG Optimization** | Poor | Good | Excellent | Good |
| **Training Speed** | Fast | Medium | Slow | Slow |
| **Inference Speed** | Very Fast | Fast | Medium | Slow |
| **Implementation** | Easy | Medium | Hard | Hard |
| **Production Adoption** | Low | **High** | Growing | Growing |
| **Data Needs** | Low | Medium | High | High |
| **Interpretability** | Good | Good | Fair | Poor |

---

## References & Further Reading

### Foundational Papers

- [From RankNet to LambdaRank to LambdaMART: An Overview](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/MSR-TR-2010-82.pdf) - Burges, 2010
- [Learning to Rank: From Pairwise Approach to Listwise Approach](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2007-40.pdf) - Cao et al., 2007
- [Multi-Stage Document Ranking with BERT](https://arxiv.org/abs/1910.14424) - Nogueira & Cho, 2019

### Practical Resources

- [Elasticsearch Learning to Rank Documentation](https://elasticsearch-learning-to-rank.readthedocs.io/)
- [LightGBM LambdaRank Tutorial](https://lightgbm.readthedocs.io/en/latest/Objectives.html#rank)
- [XGBoost Learning to Rank Guide](https://xgboost.readthedocs.io/en/latest/tutorials/learning_to_rank.html)

### Open Source Implementations

- **RankLib** - Yahoo's Java library for LTR
- **allRank** - PyTorch-based listwise LTR framework
- **Elasticsearch LTR Plugin** - Production-ready ES integration
- **TensorFlow Ranking** - Google's neural ranking framework

### Key Conferences

- SIGIR (Information Retrieval)
- WSDM (Web Search and Data Mining)
- KDD (Knowledge Discovery and Data Mining)
- NeurIPS (Neural Information Processing Systems)

---

**Document Version:** 1.0
**Last Updated:** March 2026
**Author:** AI-Powered Search Knowledge Base

---

## Appendix: Code Templates

### Complete LambdaMART Training Pipeline

```python
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import ndcg_score

class LTRTrainingPipeline:
    def __init__(self, feature_names):
        self.feature_names = feature_names
        self.scaler = StandardScaler()
        self.model = None

    def prepare_data(self, df):
        """Convert raw data to LightGBM format"""
        # Sort by query for grouping
        df = df.sort_values('query_id')

        # Extract features
        X = df[self.feature_names].values
        y = df['relevance_label'].values
        groups = df.groupby('query_id').size().values

        # Scale features
        X = self.scaler.fit_transform(X)

        return X, y, groups

    def train(self, X_train, y_train, groups_train):
        """Train LambdaMART model"""
        train_data = lgb.Dataset(X_train, label=y_train)
        train_data.set_group(groups_train)

        params = {
            'objective': 'lambdarank',
            'metric': 'ndcg',
            'metric_freq': 10,
            'ndcg_eval_at': [5, 10],
            'num_leaves': 31,
            'max_depth': 6,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 1,
        }

        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=500,
            valid_sets=[train_data],
            valid_names=['train'],
            callbacks=[
                lgb.early_stopping(stopping_rounds=50),
                lgb.log_evaluation(period=10),
            ],
        )

        return self.model

    def evaluate(self, X_test, y_test, groups_test):
        """Evaluate on test set"""
        predictions = self.model.predict(X_test)

        # Compute NDCG@10 per query
        ndcgs = []
        start_idx = 0

        for group_size in groups_test:
            end_idx = start_idx + group_size
            query_preds = predictions[start_idx:end_idx]
            query_labels = y_test[start_idx:end_idx]

            ndcg = ndcg_score([query_labels], [query_preds], k=10)
            ndcgs.append(ndcg)

            start_idx = end_idx

        avg_ndcg = np.mean(ndcgs)
        return avg_ndcg

    def rank(self, X_query):
        """Rank candidates for a query"""
        X_query = self.scaler.transform(X_query)
        scores = self.model.predict(X_query)
        ranking = np.argsort(-scores)
        return ranking

# Usage
if __name__ == "__main__":
    # Load data
    df = pd.read_csv('training_data.csv')

    # Split train/test
    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']

    # Feature names
    feature_cols = ['bm25', 'tfidf', 'pagerank', 'length', 'freshness']

    # Create pipeline
    pipeline = LTRTrainingPipeline(feature_cols)

    # Prepare data
    X_train, y_train, groups_train = pipeline.prepare_data(train_df)
    X_test, y_test, groups_test = pipeline.prepare_data(test_df)

    # Train
    model = pipeline.train(X_train, y_train, groups_train)

    # Evaluate
    ndcg = pipeline.evaluate(X_test, y_test, groups_test)
    print(f"Test NDCG@10: {ndcg:.4f}")
```

---

**End of Encyclopedia**
