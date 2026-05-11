# Search Evaluation Encyclopedia: Measuring and Improving Search Quality

**Last Updated:** March 2026
**Word Count:** 4,200+
**Scope:** Comprehensive guide covering offline metrics, online signals, A/B testing, benchmark datasets, and practical evaluation frameworks.

---

## Table of Contents

1. [Offline Metrics & Formulas](#offline-metrics--formulas)
2. [Online Metrics & User Signals](#online-metrics--user-signals)
3. [Relevance Judgment & Annotation](#relevance-judgment--annotation)
4. [A/B Testing & Interleaving](#ab-testing--interleaving)
5. [Benchmark Datasets](#benchmark-datasets)
6. [Evaluation Frameworks & Tools](#evaluation-frameworks--tools)
7. [Search Quality Dashboards](#search-quality-dashboards)
8. [Common Pitfalls & Biases](#common-pitfalls--biases)
9. [Practical Examples & Code](#practical-examples--code)

---

## 1. Offline Metrics & Formulas

Offline metrics evaluate search quality using pre-judged relevance assessments. These are the foundation of reproducible, comparable evaluation.

### 1.1 Normalized Discounted Cumulative Gain (NDCG)

**What it measures:** Ranking quality with graded relevance, penalizing errors early in the list while accounting for multiple relevant documents.

**Formula:**

```
DCG@k = Σ(i=1 to k) [rel_i / log₂(i+1)]

NDCG@k = DCG@k / IDCG@k
```

Where:
- `rel_i` = relevance score of the document at position i
- `IDCG@k` = Ideal DCG (maximum possible DCG with perfect ranking)

**Example:**
Consider a search query with 5 results having relevance scores [3, 2, 3, 0, 1] (on a 0-3 scale):

```
Position 1: 3 / log₂(2) = 3 / 1.0 = 3.00
Position 2: 2 / log₂(3) = 2 / 1.58 = 1.26
Position 3: 3 / log₂(4) = 3 / 2.0 = 1.50
Position 4: 0 / log₂(5) = 0 / 2.32 = 0.00
Position 5: 1 / log₂(6) = 1 / 2.58 = 0.39

DCG@5 = 3.00 + 1.26 + 1.50 + 0.00 + 0.39 = 6.15
```

The ideal ranking would be [3, 3, 2, 1, 0]:
```
IDCG@5 = 3.00 + 1.89 + 1.26 + 0.43 + 0.0 = 6.58

NDCG@5 = 6.15 / 6.58 = 0.93
```

**Variations:**
- **NDCG@10, NDCG@100:** Evaluation at different cutoff positions
- **Binary NDCG:** Using rel_i ∈ {0, 1} instead of graded scores
- **Position-aware NDCG:** Different discount functions (e.g., 1/log(i+1) vs 1/i)

**When to use:**
- Graded relevance judgments available
- Multiple relevant documents per query
- Position sensitivity matters
- Compare ranking systems fairly across queries

---

### 1.2 Mean Average Precision (MAP)

**What it measures:** How well relevant documents are ranked, with emphasis on precision at each relevant position.

**Formula:**

```
AP = Σ(k=1 to n) [P(k) × rel(k)] / min(m, k)

MAP = (1/Q) × Σ(q=1 to Q) AP(q)
```

Where:
- `P(k)` = Precision at position k
- `rel(k)` = Relevance indicator (1 if relevant, 0 otherwise)
- `m` = Total number of relevant documents
- `Q` = Number of queries

**Example:**
Query with 3 relevant documents, system returns [relevant, not, not, relevant, relevant]:

```
Position 1 (relevant):    P(1) = 1/1 = 1.00
Position 2 (not):        P(2) = 1/2 = 0.50
Position 3 (not):        P(3) = 1/3 = 0.33
Position 4 (relevant):    P(4) = 2/4 = 0.50
Position 5 (relevant):    P(5) = 3/5 = 0.60

AP = (1.00 + 0.50 + 0.60) / 3 = 0.70
```

**Key characteristics:**
- Heavily penalizes early misses
- Binary relevance only (can be adapted for graded)
- Highly sensitive to ranking order
- Range: 0 to 1 (higher is better)

---

### 1.3 Mean Reciprocal Rank (MRR)

**What it measures:** Position of the first relevant document.

**Formula:**

```
RR = 1 / rank_of_first_relevant_doc
MRR = (1/Q) × Σ(q=1 to Q) RR(q)
```

**Example:**
- First relevant at position 1: RR = 1/1 = 1.0
- First relevant at position 2: RR = 1/2 = 0.5
- First relevant at position 5: RR = 1/5 = 0.2
- No relevant documents: RR = 0

**Limitations:**
- Only considers the first relevant result
- Ignores other relevant documents in the ranking
- Best for navigational queries (where users want one specific answer)

**When to use:**
- Question answering systems
- Named entity retrieval
- Navigational queries

---

### 1.4 Expected Reciprocal Rank (ERR)

**What it measures:** Expected position where a user finds the first relevant result, accounting for graded relevance and user cascade behavior.

**Formula:**

```
ERR = Σ(i=1 to n) [(1 - C(i)) × (1/i) × Π(j=1 to i-1) C(j)]

Where C(i) = cumulative relevance at position i
```

This models a cascade user who examines results sequentially and stops at the first sufficiently relevant document.

**Key advantages over MRR:**
- Incorporates graded relevance (partially relevant documents contribute)
- Multiple relevant items can contribute to the metric
- Reflects realistic user behavior (browsing stops at satisfactory result)

---

### 1.5 Precision@K and Recall@K

**Precision@K:** What proportion of top-K results are relevant?

```
Precision@K = (# relevant docs in top K) / K
```

**Recall@K:** What proportion of all relevant documents appear in top K?

```
Recall@K = (# relevant docs in top K) / (total relevant docs)
```

**Example:**
For a query with 10 total relevant documents, if top-10 results contain 7 relevant documents:
- Precision@10 = 7/10 = 0.70
- Recall@10 = 7/10 = 0.70

**Decision tree for metric selection:**

```
Q: Do you have graded relevance?
├─ YES: NDCG or ERR preferred
└─ NO: MAP or Precision@K

Q: Is ranking order critical?
├─ YES: MRR, MAP, NDCG
└─ NO: Recall, Precision (unranked)

Q: Single relevant document?
├─ YES: MRR is appropriate
└─ NO: NDCG or MAP better

Q: What position matters most?
├─ Top 1: MRR
├─ Top 5-10: Precision@5, NDCG@10
└─ Overall: MAP, NDCG@k where k ≥ user session length
```

---

## 2. Online Metrics & User Signals

Online metrics measure real user behavior in production systems. They're often noisier but represent actual satisfaction.

### 2.1 Click-Through Rate (CTR)

**Definition:** Fraction of search results that users click on.

```
CTR = (# clicks on results) / (# impressions)
```

**Position Bias Correction:**

Raw CTR is heavily influenced by ranking position. A result in position 1 gets ~40% CTR while position 2 gets ~18% (Google data). Solutions:

```
Position-Normalized CTR = Observed_CTR / Expected_CTR_at_position

PAL Framework (Position-bias Aware Learning):
Models P(click|position, relevance) separately
Allows offline training, online inference without position information
```

**When useful:**
- High-volume production signals
- Relative ranking quality
- A/B test results

**Pitfalls:**
- Position bias masks true relevance
- Selection bias: good results already at top
- Novelty effects: new results get clicks due to curiosity
- "Bad clicks": accidental or exploratory

---

### 2.2 Dwell Time & Long Clicks

**Dwell Time:** Duration between clicking a result and returning to search results.

```
Dwell_time = time_user_leaves_result - time_user_clicks
```

**Satisfaction Thresholds:**
- < 10 seconds: Likely dissatisfied ("bad click")
- 10-30 seconds: Ambiguous
- > 30 seconds: Likely satisfied ("long click")

**Research findings:**
- Strong correlation between dwell time > 30s and document relevance
- Combining with CTR: "good click" = click + dwell > 30s
- Diminishing returns: dwell 60s vs 120s shows minimal difference

**Implementation considerations:**
- Minimum dwell of 30s ≈ 90% accuracy for satisfaction
- Requires accurate page load tracking (don't include network latency)
- Mobile dwell times are typically shorter

---

### 2.3 Query Reformulation

**Definition:** User resubmits a modified query within 5 minutes.

```
Reformulation_rate = (# sessions with reformulation) / (# sessions)
```

**Satisfaction signals:**
- High reformulation rate → dissatisfaction (more likely)
- Low reformulation rate → satisfaction (more likely)

**Combining signals (example heuristic):**
```
Satisfaction =
  1.0 if dwell > 30s AND no reformulation
  0.5 if dwell > 10s AND reformulation within 10min
  0.0 if dwell < 5s OR reformulation within 2min
  undefined if insufficient signal
```

**Limitations:**
- Users reformulate for other reasons (clarification, exploration)
- Not all reformulations indicate failure

---

### 2.4 Zero-Result Rate (ZRR)

**Definition:** Proportion of searches yielding zero results.

```
ZRR = (# searches with 0 results) / (# total searches)
```

**Benchmarks:**
- Excellent: < 2%
- Good: 2-5%
- Acceptable: 5-10%
- Poor: > 10%

**Component signals in dashboards:**
```
Overall_Score = (4 × CTR) + (0.2 × Session_Rate) - ZRR - Abandon_Rate + Filter_Rate
(Formula from Site Search 360)
```

---

### 2.5 Time to First Click (TTFC)

**Definition:** How long does user take to click first result?

**Signals:**
- < 1s: Likely satisfied immediately
- 1-5s: Typical acceptable time
- > 10s: User struggling or reading carefully
- No click: Complete dissatisfaction

---

### 2.6 Session Success Rate

**Definition:** Sessions where user finds what they need (signals: long click, no reformulation, page stay > threshold).

```
Session_Success = Sessions_with_satisfaction_signals / Total_Sessions
```

**Multi-signal approach:**
```
Is_Successful_Session = (
  (first_click_dwell > 30s) OR
  (any_click_dwell > 60s) OR
  (user_stayed_on_page_and_exited_normally)
)
```

---

## 3. Relevance Judgment & Annotation

### 3.1 Binary vs Graded Relevance

**Binary (relevant/irrelevant):**
- Simpler: rel ∈ {0, 1}
- Standard for older IR work (TREC)
- Lower inter-annotator agreement
- Less nuanced

**Graded (multi-level):**

Common scales:
```
4-point scale (TREC):
  0 = Not relevant
  1 = Marginally relevant
  2 = Fairly relevant
  3 = Highly relevant

5-point scale (Natural Questions):
  0 = Not relevant
  1 = Slightly relevant
  2 = Moderately relevant
  3 = Highly relevant
  4 = Perfectly relevant

Binary conversion:
  rel >= threshold → relevant
  Otherwise → not relevant
```

**Advantages of graded:**
- Better reflects partial relevance
- Higher inter-annotator agreement (when proper guidelines provided)
- Enables NDCG, ERR metrics
- Accommodates documents of varying utility

---

### 3.2 Inter-Annotator Agreement Metrics

**Cohen's Kappa (two annotators):**

```
κ = (P_o - P_e) / (1 - P_e)

Where:
  P_o = observed agreement
  P_e = expected agreement by chance

Interpretation:
  κ > 0.8  = Very good agreement
  κ > 0.67 = Tentative conclusions acceptable
  κ > 0.5  = Moderate agreement
  κ < 0.5  = Poor agreement
```

**Krippendorff's Alpha:**

```
α = 1 - (D_o / D_e)

Advantages:
  - Works with 2+ annotators
  - Handles missing data
  - Supports nominal, ordinal, interval, ratio data
  - More conservative than Cohen's kappa

Interpretation:
  α >= 0.8   = Very good
  α >= 0.667 = Acceptable
  α >= 0.5   = Moderate
  α < 0.5    = Poor
```

**Data quality impact:**

For NDCG calculation with disagreement:
- Use median grade (all annotators present)
- Use majority vote (more disagreement → lower confidence)
- Weight annotations by annotator track record (expert weighting)

---

### 3.3 Crowdsourcing Platforms

**Popular options:**

1. **Amazon Mechanical Turk (MTurk)**
   - Largest crowd, lowest cost
   - Quality control challenging
   - Qualification tests essential
   - Typical cost: $0.05-0.15 per annotation

2. **Prolific**
   - More vetted workers
   - Better retention
   - Higher cost: $0.20-0.50 per annotation
   - Built-in attention checks

3. **Scale AI**
   - Expert annotation services
   - Training provided
   - Premium cost: $1-5+ per annotation
   - Best for high-stakes evaluation

**Quality control practices:**

```
1. Use control items (known answers) scattered throughout
2. Set qualification tests before main annotation
3. Require rater agreement on test items (80%+ threshold)
4. Monitor metrics in real-time
5. Implement attention checks
6. Pay small bonuses for high agreement
7. Block low-quality workers
```

---

### 3.4 LLM-as-Judge for Relevance

**Approach:** Use GPT-4, Claude, or other frontier LLMs to automatically judge relevance.

**Research findings:**
- GPT-4 reaches ~85% agreement with human judgment
- Claude 3.5 Sonnet, GPT-4o show even better alignment
- Exceeds inter-human agreement (~81%)

**Prompt engineering (example):**

```
You are evaluating search result relevance.

Query: "best laptop for programming"
Document: "MacBook Pro M3 Max: A powerful machine for developers..."

Rating criteria:
- 3 (Highly relevant): Directly addresses laptop for programming
- 2 (Moderately relevant): About laptops or programming but not both
- 1 (Slightly relevant): Mentions laptop or programming tangentially
- 0 (Not relevant): No connection to query

Provide rating (0-3) and brief justification.
```

**Known biases to watch:**
- LLMs prefer longer outputs
- Favor outputs from themselves over other models (10-25% win rate bias)
- Preference for lists/structured output
- Choice order bias (vary answer position in pairwise comparison)
- May conflate helpfulness with relevance

**Best practices:**
```
1. Use multiple LLM judges, aggregate ratings
2. Compare human vs LLM labels on subset before full rollout
3. Use randomized prompt variations (order, wording)
4. Include diverse relevance levels in evaluation set
5. Monitor for systematic biases by reviewing disagreements
6. Use strongest available models (GPT-4o, Claude 3.5+)
```

---

## 4. A/B Testing & Interleaving

### 4.1 Traditional A/B Testing

**Setup:**
```
50% users see control (current ranking)
50% users see treatment (new ranking)

Measure success metrics for each group
Calculate statistical significance
```

**Challenges:**
- High variance due to different users, sessions, times
- Requires large sample size (days/weeks to reach significance)
- Position novelty effect: new results get temporary click boost

---

### 4.2 Team Draft Interleaving

**Algorithm (simplified):**

```
Input: Ranking_A (control), Ranking_B (treatment)
Output: Interleaved ranking

For each position:
  1. Pick highest-ranked remaining result from A or B
  2. Randomly break ties (50-50)
  3. Add to interleaved list
  4. Mark which system contributed
  5. Remove from source ranking, continue

Result: Both systems' results on same page, position-fair
```

**Key advantages:**
- 10-100× less traffic needed
- 10-100× faster experiments (days vs weeks)
- Removes user-to-user variance
- Fair position presentation (alternating which system gets priority)

**Real-world examples:**
- Airbnb: 100+ interleaving experiments validated
- Walmart Search: Accelerated ranking improvement
- Etsy: Faster ML experimentation cycles
- Netflix: Personalization algorithm testing

**Position fairness mechanism:**

```
For each request, randomly choose:
  Team A takes priority tier (positions 1, 3, 5, 7...)
  Team B takes priority tier (positions 2, 4, 6, 8...)

Switch priority assignment per request (50-50)

Result: Over many requests, both teams get fair exposure
```

---

### 4.3 Statistical Significance

**Sample size calculation:**

```
n = (Z_α + Z_β)² × (p₁(1-p₁) + p₂(1-p₂)) / (p₁ - p₂)²

Where:
  α = significance level (0.05 = 95% confidence)
  β = power (0.2 = 80% power to detect effect)
  p₁ = baseline conversion rate
  p₂ = expected conversion rate with treatment
  (p₁ - p₂) = minimum detectable effect size

Common Z values:
  α=0.05: Z_α = 1.96
  β=0.2:  Z_β = 0.84
```

**Example:**
```
Baseline: 5% of searches result in click-through
Want to detect: 5.5% improvement
Target: 80% power, 95% confidence

n = (1.96 + 0.84)² × (0.05×0.95 + 0.055×0.945) / (0.005)²
n ≈ 6,200 searches per variant
Total: ~12,400 searches needed
```

**Online calculators:**
- Optimizely sample size calculator
- Statsig A/B test calculator
- Amplitude statistical significance tool

---

## 5. Benchmark Datasets

### 5.1 MS MARCO

**Size:** 1M questions, 8.8M passages, 384M relevance judgments
**Source:** Real Bing search queries
**Tasks:**
- Passage ranking
- Document ranking
- Full document ranking

**Characteristics:**
- Web-scale real-world distribution
- Annotated by crowd workers
- Multiple passages per question
- Zero-shot generalization testing

---

### 5.2 BEIR (Heterogeneous IR Benchmark)

**Size:** 15+ diverse datasets, millions of documents
**Zero-shot protocol:** No in-domain fine-tuning allowed
**Composition:**
- Open-domain QA: SQuAD, Natural Questions
- Fact-checking: Fever, Climate-Fever
- Biomedical: TREC-COVID, BioASQ
- E-commerce: DBPedia
- Domain-specific: SciEval, Trec-News

**Evaluation metric:** nDCG@10 (primary), others secondary

**Use case:** Test domain generalization of retrieval models

---

### 5.3 TREC Collections

**TREC-DL (Deep Learning Track):**
- Passage ranking: ~60K queries, 8.8M passages
- Document ranking: Complex information needs
- Full ranking task with graded judgments

**NIST Evaluation:**
- Professional assessors
- Stringent quality control
- Multiple assessments per query
- High inter-annotator agreement

---

### 5.4 Natural Questions Dataset

**Size:** 307K training, 7.8K dev, 7.8K test (5-way annotated)
**Source:** Real Google search queries
**Task:** Retrieve relevant passages + identify answer spans
**Complexity:**
- Wikipedia articles (whole pages, not passages)
- Multi-hop reasoning required
- Yes/No answers possible
- Null (no answer) cases included

**Evaluation:**
- Exact match (strict answer span match)
- Precision/Recall: 90/85% (long answers), 79/72% (short)

---

### 5.5 MTEB (Massive Text Embedding Benchmark)

**Size:** 56+ datasets, 8 diverse task categories
**Tasks:**
1. Semantic textual similarity
2. Clustering
3. Reranking
4. Retrieval
5. Classification
6. Pair classification
7. Instruction following
8. Structured retrieval

**Standard comparison:** NDCG@10 for retrieval tasks

---

## 6. Evaluation Frameworks & Tools

### 6.1 RAGAS (Retrieval Augmented Generation Assessment)

**Purpose:** Evaluate RAG (Retrieval-Augmented Generation) pipelines without ground truth.

**Core metrics:**

```
1. Context_Relevancy (0-1)
   - Does retrieved context match the query?
   - LLM scores context relevance to query

2. Context_Recall (0-1)
   - Does context contain information needed to answer?
   - LLM checks if all required facts present

3. Faithfulness (0-1)
   - Are generated answers grounded in retrieved context?
   - Detects hallucinations outside context

4. Answer_Relevancy (0-1)
   - Does generated answer address the query?
   - Direct relevance judgment

RAGAS_Score = mean(context_relevancy, context_recall,
                     faithfulness, answer_relevancy)
```

**Advantages:**
- No human annotations needed
- Reference-free evaluation
- Component-level diagnosis
- Automated at scale

---

### 6.2 ranx: Ranking Evaluation Library

**Features:**
- Blazing-fast metrics (Numba JIT compiled)
- 20+ metrics: NDCG, MAP, MRR, Precision, Recall, ERR, etc.
- Statistical testing (t-tests, bootstrap)
- Report generation (LaTeX tables)
- Verified against trec_eval

**Installation:**
```bash
pip install ranx
```

**Example:**

```python
from ranx import Ranx, evaluate, compare

# Load qrels and run files
qrels = Ranx.from_file("qrels.trec")
results = Ranx.from_file("results.trec")

# Calculate metrics
metrics = evaluate(qrels, results, ["ndcg@10", "map", "mrr"])
print(metrics)
# Output: {'ndcg@10': 0.58, 'map': 0.42, 'mrr': 0.71}

# Compare systems
comparison = compare(qrels, results_a, results_b,
                    metrics=["ndcg@10"])
```

---

### 6.3 Elasticsearch Rank Evaluation API

**Built-in evaluation:** Test ranking quality directly in Elasticsearch

**Required:**
1. Collection of documents
2. Typical search queries
3. Manually rated documents per query (0-3 ratings)

**Example request:**

```json
{
  "requests": [
    {
      "id": "search_query_1",
      "request": {
        "query": {
          "match": {"title": "python programming"}
        }
      },
      "ratings": [
        {"_id": "doc1", "rating": 3},
        {"_id": "doc2", "rating": 2},
        {"_id": "doc3", "rating": 0}
      ]
    }
  ],
  "metric": {
    "ndcg": {
      "k": 10
    }
  }
}
```

**Response:** Metric scores, helping verify query tuning

---

### 6.4 Python Code: Computing Metrics from Scratch

```python
import numpy as np
from typing import List, Dict

def compute_dcg(relevances: List[int], k: int) -> float:
    """Compute Discounted Cumulative Gain"""
    dcg = 0.0
    for i, rel in enumerate(relevances[:k]):
        dcg += rel / np.log2(i + 2)  # i+2 because positions are 1-indexed
    return dcg

def compute_ndcg(relevances: List[int], k: int) -> float:
    """Compute Normalized DCG"""
    dcg = compute_dcg(relevances, k)

    # Ideal DCG: sort relevances in descending order
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = compute_dcg(ideal_relevances, k)

    if idcg == 0:
        return 0.0
    return dcg / idcg

def compute_precision_at_k(relevant_positions: List[int], k: int) -> float:
    """Compute Precision@K"""
    relevant_in_k = sum(1 for pos in relevant_positions if pos <= k)
    return relevant_in_k / k

def compute_recall_at_k(relevant_positions: List[int], k: int,
                       total_relevant: int) -> float:
    """Compute Recall@K"""
    relevant_in_k = sum(1 for pos in relevant_positions if pos <= k)
    return relevant_in_k / total_relevant if total_relevant > 0 else 0.0

def compute_mrr(first_relevant_pos: int) -> float:
    """Compute Mean Reciprocal Rank"""
    if first_relevant_pos is None:
        return 0.0
    return 1.0 / first_relevant_pos

def compute_map(relevant_positions: List[int], k: int) -> float:
    """Compute Mean Average Precision"""
    if not relevant_positions:
        return 0.0

    ap = 0.0
    for i, pos in enumerate(relevant_positions, 1):
        if pos <= k:
            precision_at_pos = i / pos
            ap += precision_at_pos

    return ap / len(relevant_positions)

# Example usage
if __name__ == "__main__":
    # Relevance scores: [highly, moderate, high, none, slight]
    relevances = [3, 2, 3, 0, 1]

    print(f"NDCG@5: {compute_ndcg(relevances, 5):.3f}")

    # For binary metrics
    relevant_at = [1, 3, 5]  # Relevant results at positions 1, 3, 5
    print(f"Precision@5: {compute_precision_at_k(relevant_at, 5):.3f}")
    print(f"Recall@5: {compute_recall_at_k(relevant_at, 5, 5):.3f}")
    print(f"MRR: {compute_mrr(relevant_at[0]):.3f}")
    print(f"MAP@5: {compute_map(relevant_at, 5):.3f}")
```

---

## 7. Search Quality Dashboards

### 7.1 Essential KPIs

**Relevance metrics:**
- NDCG@10: Primary ranking quality metric
- MAP: Secondary measure for comparison
- Click CTR (position-normalized): User-perceived relevance

**User satisfaction signals:**
- Long click rate (> 30s dwell): Gold-standard signal
- Session success rate: Multi-signal combination
- Return visit rate: Long-term satisfaction
- Zero-result rate: System failure detection

**System health:**
- Query reformulation rate: Dissatisfaction signal
- Abandonment rate: Users give up
- Time-to-first-click: User friction
- No-click rate: Broken SERPs

---

### 7.2 Dashboard Design Patterns

**Real-time monitoring:**
```
┌─ Search Quality Dashboard ────────────────────────────┐
│                                                        │
│ Overall Score: 4.2/5.0  ↑ +0.1 (vs last week)        │
│                                                        │
│ ┌─ Ranking Quality ──────┬─ User Signals ────┐        │
│ │ NDCG@10:   0.62        │ CTR:     4.2%      │        │
│ │ MAP:       0.58        │ Long clicks: 35%   │        │
│ │ MRR:       0.71        │ Reformulation: 8%  │        │
│ │ Click CTR: 0.048       │ ZRR:     2.1%      │        │
│ │                        │ Session success: 62%│       │
│ └────────────────────────┴────────────────────┘        │
│                                                        │
│ Trend (Last 30 days):                                 │
│ NDCG@10: ▁▂▃▄▄▄▅▅▅▅ (steady improvement)             │
│ CTR:     ▄▄▃▃▂▂▂▃▄▅ (volatile)                        │
│                                                        │
│ Query Segments:                                       │
│ ├─ Navigational:    NDCG 0.89, Success 92%           │
│ ├─ Informational:   NDCG 0.58, Success 68%           │
│ └─ Transactional:   NDCG 0.42, Success 45%           │
│                                                        │
│ Alerts:                                               │
│ ⚠ ZRR increased to 2.1% (was 1.8%)                    │
│ ✓ CTR stable despite ranking changes                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 7.3 Segment Analysis

**Dimensions to track:**

```python
dashboard_segments = {
    "Device": ["mobile", "desktop", "tablet"],
    "User_Type": ["new", "returning", "power_user"],
    "Query_Type": ["navigational", "informational", "transactional"],
    "Geography": ["US", "EU", "Asia", "APAC"],
    "Search_Domain": ["products", "articles", "people", "other"],
    "Time_Period": ["morning", "afternoon", "evening", "night"],
}

# For each segment, track:
metrics_per_segment = {
    "segment_id": {
        "ndcg@10": float,
        "ctr": float,
        "long_click_rate": float,
        "success_rate": float,
        "session_count": int,
        "trend": str  # "↑", "↓", "→"
    }
}
```

---

## 8. Common Pitfalls & Biases

### 8.1 Position Bias

**Problem:** Better ranking positions naturally get more clicks regardless of relevance.

```
Position     Avg CTR (Google data)
1            39.6%
2            18.4%
3            10.1%
4            6.0%
5            4.0%
```

**Solutions:**
1. Normalize CTR by position before using as signal
2. Use randomized ranking AB tests (each user sees different order)
3. Apply position bias correction models (propensity weighting)

---

### 8.2 Selection Bias

**Problem:** System feedback can be biased toward what the system already shows well.

**Example:**
```
Truth: Doc A is more relevant than Doc B
System shows: A (top 3) >> B (top 50)
Observable clicks: A >> B
Conclusion: A >> B ✓ (correct but selection-biased)

System shows: B (top 1) >> A (bottom 10)
Observable clicks: B >> A
Conclusion: B >> A ✗ (false, contradicts position bias lessons)
```

**Solutions:**
- Use human judgments (not click data) for evaluation
- Interleaving experiments for fair comparison
- Counterfactual evaluation techniques

---

### 8.3 Simpson's Paradox

**Problem:** Trends can reverse when data is segmented.

**Example:**
```
Overall: New ranking BETTER (NDCG 0.61 vs 0.58)

Segmented by device:
├─ Mobile: New ranking WORSE (0.55 vs 0.58)
└─ Desktop: New ranking WORSE (0.62 vs 0.64)

Paradox: New ranking better overall but worse in ALL segments!
Root cause: Traffic shifted toward mobile (where old was better)
```

**Lesson:** Always check segment-level metrics, not just aggregates.

---

### 8.4 Novelty Effect

**Problem:** New results get temporary boost due to curiosity.

```
Week 1: New ranking CTR = 5.2% (↑ 0.5%)
Week 2: New ranking CTR = 4.8% (↑ 0.1%)
Week 3: New ranking CTR = 4.7% (→ -0.1%)

Week 1 clicks are partially "novelty" not "quality"
Need 2+ weeks to see true effect
```

**Mitigation:** Use long-dwell-time metric (> 30s) which is less susceptible to novelty.

---

### 8.5 Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure"

**In search context:**

```
Target: Maximize NDCG@10
Action: Override ranking to create "perfect" test cases
Result: System overfits to evaluation set, hurts real users

Target: Maximize CTR
Action: Show clickbait, surprising results
Result: Clicks up, satisfaction down

Solution:
1. Monitor multiple metrics (not just one)
2. Establish guardrail metrics
3. Human spot-checks of changed results
4. Use holdout human evaluators
```

**Guardrail metrics approach:**

```python
can_deploy = (
    primary_metric_improved(new_vs_old)
    and guardrail_1(new_ranking) > threshold_1
    and guardrail_2(new_ranking) > threshold_2
    and human_review_passed(new_ranking)
)

guardrails = {
    "ctr_not_degraded": new_ctr >= old_ctr * 0.95,
    "zero_result_rate": new_zzr < 3.5%,
    "user_satisfaction": long_click_rate >= old_lcr * 0.95,
    "no_ranking_collapse": bottom_10_results_quality_ok,
}
```

---

## 9. Practical Examples & Code

### Example: Full Evaluation Pipeline

```python
import pandas as pd
from ranx import Ranx, evaluate, compare
from sklearn.metrics import ndcg_score

class SearchEvaluator:
    def __init__(self, qrels_file: str, results_dir: str):
        self.qrels = Ranx.from_file(qrels_file)
        self.results_dir = results_dir
        self.metrics_config = ["ndcg@10", "map", "mrr", "precision@5"]

    def evaluate_system(self, system_name: str, results_file: str):
        """Evaluate a single ranking system"""
        results = Ranx.from_file(f"{self.results_dir}/{results_file}")
        metrics = evaluate(self.qrels, results, self.metrics_config)

        return {
            "system": system_name,
            "timestamp": pd.Timestamp.now(),
            **metrics
        }

    def compare_systems(self, baseline_file: str,
                       treatment_file: str):
        """A/B compare two ranking systems"""
        baseline = Ranx.from_file(baseline_file)
        treatment = Ranx.from_file(treatment_file)

        comparison = compare(
            self.qrels,
            baseline,
            treatment,
            metrics=self.metrics_config,
            stat_test="paired_t_test"
        )

        return comparison

    def get_per_query_analysis(self, results_file: str):
        """Get metrics broken down by query"""
        results = Ranx.from_file(results_file)
        per_query = {}

        for query_id in self.qrels.queries:
            query_qrels = {query_id: self.qrels[query_id]}
            query_results = {query_id: results[query_id]}

            metrics = evaluate(
                Ranx(query_qrels),
                Ranx(query_results),
                self.metrics_config
            )
            per_query[query_id] = metrics

        return pd.DataFrame(per_query).T

# Usage
evaluator = SearchEvaluator("qrels.trec", "results/")

# Single system evaluation
baseline_metrics = evaluator.evaluate_system(
    "current", "baseline_results.trec"
)
print(baseline_metrics)

# A/B comparison
comparison = evaluator.compare_systems(
    "results/baseline_results.trec",
    "results/treatment_results.trec"
)
print(f"NDCG@10: {comparison['ndcg@10']['p-value']:.4f} (significant={comparison['ndcg@10']['p-value'] < 0.05})")

# Per-query analysis
per_query = evaluator.get_per_query_analysis("results/baseline_results.trec")
print(per_query.describe())
```

---

## Summary & Decision Framework

**Choosing evaluation approach:**

```
If evaluating offline (test set available):
├─ Use NDCG@10 (graded relevance)
├─ Support with MAP or Precision@K
└─ Run human evaluation for >200 queries minimum

If evaluating online (production):
├─ Track position-normalized CTR
├─ Monitor long-click rate > 30s
├─ Watch zero-result rate
├─ Check reformulation rate
└─ Combine into session success metric

If comparing two systems:
├─ Sample size < 500K searches? → Interleaving
├─ Large scale (millions)? → A/B test
├─ Rapid iteration needed? → Interleaving
└─ Statistical rigor critical? → A/B with guardrails

If need graded relevance annotations:
├─ High quality + budget? → Scale AI or expert annotators
├─ Moderate quality + cost? → Prolific
├─ Cost-sensitive? → MTurk with quality control
└─ No budget for human? → LLM-as-Judge (with validation)

If designing search quality dashboard:
├─ Primary metric: NDCG@10 or Long-Click Rate
├─ Support metrics: CTR, Success Rate, ZRR
├─ Segment by: Device, User Type, Query Class
├─ Alert on: ZRR > 3%, Reformulation rate > 12%
└─ Weekly reporting with trend analysis
```

---

## References & Further Reading

- [Discounted Cumulative Gain - Wikipedia](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)
- [Marqo: NDCG Explanation](https://www.marqo.ai/blog/what-is-normalized-discounted-cumulative-gain-ndcg)
- [Evidentlyai: NDCG Metric](https://www.evidentlyai.com/ranking-metrics/ndcg-metric)
- [Mean Average Precision Guide](https://www.evidentlyai.com/ranking-metrics/mean-average-precision-map)
- [Expected Reciprocal Rank](https://www.envisioning.com/vocab/err-expected-reciprocal-rank)
- [Position-Normalized CTR in Search Advertising](https://dl.acm.org/doi/10.1145/2339530.2339654)
- [Modeling Dwell Time for Satisfaction](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/KimWSDM2014.pdf)
- [Team Draft Interleaving - OpenSource Connections](https://opensourceconnections.com/blog/2025/08/06/a-b-testing-with-team-draft-interleaving/)
- [Airbnb Beyond A/B Testing](https://airbnb.tech/data/beyond-a-b-test-speeding-up-airbnb-search-ranking-experimentation-through-interleaving/)
- [Krippendorff's Alpha Guide](https://encord.com/blog/interrater-reliability-krippendorffs-alpha/)
- [BEIR Benchmark Paper](https://arxiv.org/pdf/2104.08663)
- [RAGAS Framework](https://arxiv.org/abs/2309.15217)
- [ranx: Python Ranking Evaluation](https://github.com/AmenRa/ranx)
- [Elasticsearch Rank Evaluation API](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval)
- [LLM-as-Judge Evaluation](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge)
- [Natural Questions Dataset](https://aclanthology.org/Q19-1026.pdf)
- [Simpson's Paradox](https://en.wikipedia.org/wiki/Simpson's_paradox)
- [Goodhart's Law](https://en.wikipedia.org/wiki/Goodhart's_law)

---

**Document Version:** 1.0
**Last Updated:** March 1, 2026
**Word Count:** 4,200+
**Suitable for:** ML Engineers, Search Teams, Data Scientists, Product Managers
