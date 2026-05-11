# Production Search Architectures Encyclopedia

A comprehensive guide to how leading tech companies design, build, and scale search systems at massive production scale (100M-1B+ daily queries).

---

## Table of Contents

1. [Shared Architectural Patterns Across Companies](#shared-architectural-patterns)
2. [Perplexity: AI-First Search Engine](#perplexity-deep-dive)
3. [Pinterest: Visual Search + LLM Relevance](#pinterest-deep-dive)
4. [Airbnb: Marketplace Search Challenges](#airbnb-deep-dive)
5. [Spotify & YouTube: Audio/Video Search](#spotify-youtube)
6. [Two-Tower Retrieval Model Pattern](#two-tower-pattern)
7. [Multi-Stage Ranking Pipelines](#multi-stage-ranking)
8. [Feature Stores and Real-Time Feature Serving](#feature-stores)
9. [Lessons Learned at Scale](#lessons-learned)
10. [Applying Patterns to Smaller Systems](#scaling-down)

---

## 1. Shared Architectural Patterns Across Companies {#shared-architectural-patterns}

After analyzing search systems from Perplexity, Pinterest, Airbnb, Spotify, LinkedIn, Netflix, YouTube, Google, Amazon, and Uber, several core architectural patterns emerge that are universally adopted at scale.

### The Common DNA: Multi-Stage Retrieval and Ranking

Every major search platform uses a **two-to-four stage pipeline**:

1. **Candidate Generation**: Fast, coarse retrieval from massive catalogs (millions/billions of items)
2. **Initial Ranking**: Medium-complexity model applies richer features to narrow candidates
3. **Final Ranking**: Complex model with expensive computation on final 100-200 items
4. **Re-ranking/Personalization**: Apply context-specific logic or LLM-based refinement

This architecture exists because of a fundamental compute tradeoff: **Cheap models scale to billions, complex models don't—so layer them.**

### Hybrid Retrieval: Combining Signals

Leading platforms no longer rely on single retrieval methods:

- **Lexical search** (keyword matching, BM25) — fast, interpretable, covers exact matches
- **Semantic search** (embedding similarity, ANN) — captures intent, handles synonyms
- **Metadata filters** (category, location, ratings) — eliminates irrelevant candidates
- **Structured queries** (dates, prices, geographic bounds) — applies hard constraints
- **Business rules** (sponsored listings, diversity) — enforces platform priorities

Perplexity fuses all signals in Vespa. Amazon's A10 combines on-site and off-site signals. Pinterest uses hybrid lexical + semantic with LLM distillation. This is universal.

### Embedding-Centric Architecture

Modern search is built on embeddings:

- **User embeddings**: Representation of user preferences from history
- **Query embeddings**: Encoding the search intent semantically
- **Item/content embeddings**: Dense vectors for products, videos, profiles
- **Embedding indices**: ANN (Approximate Nearest Neighbor) indexes for fast lookup
- **Embedding tables**: Cached in memory for sub-millisecond retrieval

Examples: Pinterest SearchSage (query embeddings), Spotify Voyager (track embeddings), Netflix viewer embeddings, YouTube user/video embeddings.

### Feature Stores as Critical Infrastructure

Every major platform has centralized feature serving:

- **Offline store**: Historical data for training ML models
- **Online store**: Pre-computed features served at <100ms latency for inference
- **Feature computation layer**: ETL pipelines that generate features from raw data
- **Real-time updates**: Features refreshed on user action or time decay

Pinterest, Airbnb, LinkedIn, Uber, and Spotify all run production feature stores (often custom-built, sometimes using Feast or similar).

### Two-Tower Retrieval as the Standard Pattern

The two-tower (dual-encoder, Siamese network) model is the dominant retrieval architecture:

```
Query Tower                    Item Tower
   |                              |
Input Query                  Input Item
   |                              |
Neural Network              Neural Network
   |                              |
Query Embedding             Item Embedding
   |                              |
   +-----------> Dot Product <----+
                    |
              Similarity Score
```

This pattern dominates because:
- Query encoding (expensive) happens once per search
- Item encoding (expensive) happens offline, amortized across millions of queries
- At serving time, only a dot product is needed
- Scales to billions of items with ANN indexes

Used by: Uber (two-tower recommendations), Snap (embedding-based retrieval), Google (TensorFlow two-towers), and most modern recommenders.

### Real-Time Personalization

Every platform personalizes search results:

- **User context**: History, location, device, time
- **Session context**: Current session behavior, recent actions
- **Real-time signals**: Ongoing user engagement patterns
- **Cold-start handling**: Category/demographic-based defaults for new users

Netflix applies lightweight re-ranking after initial recommendations based on real-time session interactions. Airbnb personalizes search results based on browsing history and guest characteristics. This is standard.

---

## 2. Perplexity: AI-First Search Engine {#perplexity-deep-dive}

Perplexity represents a new category of search: **AI-first retrieval-augmented generation (RAG)** at scale, handling 200M+ daily queries with a hybrid lexical+semantic architecture.

### Perplexity + Vespa Partnership (2025)

In May 2025, Perplexity partnered with Vespa.ai to bring its search function in-house, replacing third-party retrieval systems. The partnership is significant because it demonstrates the shift toward **unified retrieval-ranking-inference stacks**.

Key metrics:
- **22 million active users** (as of 2025)
- **780 million monthly queries** (reported in partnership announcement)
- **Sub-second response latency** across all tiers
- **Chunk-level retrieval** (sections within documents, not just full documents)

### Architecture: Hybrid Lexical + Semantic

Perplexity's system achieves high-quality RAG by combining three retrieval signals:

```
Web Corpus (Billions of documents)
        |
        +--- Lexical Scorer (BM25)
        |
        +--- Embedding Scorer (Vector similarity)
        |
        +--- Metadata Scorer (Freshness, authority)
        |
        v
Early Stage: Filter to 1000 candidates
        |
        v
Middle Stage: Apply learning-to-rank models
        |
        v
Late Stage: Cross-encoder re-ranking
        |
        v
Final Output: Top-K chunks for LLM context
```

The key insight: **Completeness, freshness, and speed require fusion of lexical and semantic signals**. Neither alone is sufficient.

### Chunk-Level Retrieval

Unlike traditional search which returns full documents, Perplexity retrieves **chunks** (sections within documents):

- **Advantages**: More precise context for LLMs, reduced token count, improved factual accuracy
- **Implementation**: Vespa's support for field-level retrieval enables this efficiently
- **Challenge**: Chunk boundaries must be semantically meaningful, not arbitrary

This is important for RAG because LLMs work better with focused context than long documents.

### Vespa as Infrastructure

Vespa is the critical infrastructure enabling Perplexity's architecture. Key capabilities:

- **Distributed retrieval**: Query billions of documents in parallel, sub-second latency
- **Hybrid queries**: Single query combines lexical, vector, and metadata signals
- **Ranking models**: Deploy ML models directly in the serving layer
- **Stateless architecture**: Scales horizontally without bottlenecks
- **Memory-resident indexes**: Fast access to frequently-queried data

Vespa also powers Yahoo's search and handles Spotify's recommendation queries, demonstrating it's a general-purpose platform, not Perplexity-specific.

### The RAG Pipeline

```
User Query
    |
    v
Query Embedding + Lexical Processing
    |
    v
Vespa Retrieval (Hybrid)
    |
    v
Candidate Ranking (Learning-to-rank)
    |
    v
Top Chunks Selection
    |
    v
LLM Context Assembly
    |
    v
Prompt Engineering (Query + Context)
    |
    v
LLM Generation (Gemini, Claude, etc.)
    |
    v
Citation + Formatting
    |
    v
User Response
```

Key insight: Perplexity's value isn't the LLM (commodity), but the **retrieval quality**. Better retrieval = better context = better LLM responses = higher user satisfaction.

---

## 3. Pinterest: Visual Search + LLM Relevance {#pinterest-deep-dive}

Pinterest is unique among major search platforms for emphasizing **visual understanding**. With 600M+ monthly searches and billions of pins, Pinterest demonstrates how visual features integrate with semantic search and LLM-powered ranking.

### SearchSage: Query Embedding Learning

Pinterest developed **SearchSage**, a system for learning effective query embeddings:

- **Multi-modal input**: Text query + visual context (user's recent saves, board themes)
- **Task-specific encoding**: Different embeddings for different search intents
- **Learnable embeddings**: Not just pre-trained models, but task-optimized
- **Online inference**: Sub-100ms query encoding at serving time

SearchSage is critical because query understanding is the bottleneck in visual search. Users describe visual concepts imprecisely ("boho chic", "cozy living room vibes"), requiring the embedding model to infer intent.

### LLM-Powered Relevance Ranking (Dec 2025)

In December 2025, Pinterest announced using fine-tuned LLMs to improve search relevance:

**The Pipeline:**
1. Fine-tune open-source LLMs (Llama-3-8B) on Pinterest's human-labeled relevance judgments
2. Use LLM as a teacher model to evaluate pin relevance to queries
3. Distill LLM knowledge into lightweight student models via knowledge distillation
4. Deploy student model at scale for real-time ranking

**Performance Results:**
- Llama-3-8B outperformed BERT-base by **12.5%** in accuracy
- Student model (distilled) achieved **19.7% improvement** over baseline
- Real-time latency maintained (<100ms) despite 10x smaller model

This demonstrates the industry trend: **LLMs as labeling/ranking tools, not just user-facing interfaces**.

### Multi-Entity Embeddings (OmniSearchSage)

Pinterest's SearchSage system handles **multiple entity types**:

- **Pins**: Visual items with descriptions, category, creator
- **Boards**: Collections of pins with themes
- **Users**: Searchers with interests and history
- **Searches**: Query history and intent patterns

Each entity type gets its own embedding space, but they're aligned in a shared representation. This enables:
- Cross-entity search ("show me boards like this pin")
- Recommendation diversity
- Cold-start handling for new pins/boards

### Architecture: Online vs Offline

```
Offline (Training):
    User Feedback + Labeled Data
        |
        v
    LLM Teacher Training
        |
        v
    Knowledge Distillation
        |
        v
    Student Model (Lightweight)

Online (Serving):
    Query -> SearchSage Embedding -> ANN Lookup -> Candidate Set
                                        |
                                        v
                                    Student Ranker
                                        |
                                        v
                                    Diversity Filter
                                        |
                                        v
                                    Sponsored Results
                                        |
                                        v
                                    Final Ranking
```

**Key insight**: Distillation from LLMs to lightweight models is the pattern for achieving state-of-the-art ranking at scale. Pinterest shows this works well in visual search, likely because LLMs capture semantic nuances that smaller models struggle with.

### Real-Time Features

Pinterest's ranking uses real-time features:

- **User engagement history**: Clicks, saves, shares on recent searches
- **Pin popularity**: Within-session engagement
- **Creator credibility**: Account age, follower count
- **Temporal signals**: Trending pins within category
- **Diversity penalty**: Avoid redundant results

These features are served from Pinterest's feature store with <50ms latency.

---

## 4. Airbnb: Marketplace Search Challenges {#airbnb-deep-dive}

Airbnb's search is fundamentally different from Google, YouTube, or e-commerce because:
- **High cardinality**: Listings change constantly (occupancy, pricing)
- **Geographic constraints**: Relevance is location-dependent
- **Personalization variance**: Same query from different users => different results
- **Conversion optimization**: Goal is booking, not click-through

Airbnb's 2025 research contributions highlight emerging challenges in marketplace search.

### CIKM 2025 Publications

Airbnb's Relevance & Personalization team published five papers at CIKM 2025:

1. **Augmenting Guest Search Results with Recommendations**: Dynamic suggestions for alternative dates, amenities, or price ranges when initial search returns few results
2. **Beyond Pairwise Learning-to-Rank**: Advanced ranking techniques beyond traditional pair-wise loss
3. **BiListing: Modality Alignment for Listings**: Alignment between text and visual representations
4. **Learning to Comparison-Shop**: Helping guests understand listing alternatives
5. **Maps Ranking Optimization**: Geographic ranking improvements

### Challenge: Narrow Search Criteria

Airbnb reports that **guests often search too narrowly**, resulting in few matches. A guest searching for 2-bedroom apartments in San Francisco for exact dates may find only 20 results despite 1000+ 2-bedroom listings.

**Solution: Dynamic Alternative Suggestions**

The system learns to:
- Suggest relaxing constraints (nearby neighborhoods, ±2 days)
- Recommend complementary amenities (pool if they searched "gym")
- Adjust price range based on guest budget patterns
- Diversify property types (house vs apartment)

This is **recommendation-within-search**, a pattern emerging across platforms:
- YouTube: Suggesting related videos when search results don't satisfy
- Uber Eats: Suggesting similar restaurants when query matches few
- Amazon: Suggesting alternatives when exact matches are out of stock

### Personalization: Embedding-Based Retrieval

Airbnb published "Embedding-Based Retrieval for Airbnb Search" (March 2025), describing:

- **User embedding**: Derived from booking history, search patterns, preferences
- **Listing embedding**: Derived from attributes (location, price, amenities), user reviews, images
- **Query embedding**: Derived from search text, filters applied

Two-stage ranking:
1. Retrieve 500 listings via semantic similarity
2. Rank final 50 using complex model with 1000+ features

### Real-World Constraints

Airbnb's system must handle:
- **Real-time occupancy**: Listings become available/unavailable dynamically
- **Pricing changes**: Daily prices update based on demand
- **Review velocity**: New reviews arrive constantly
- **Seasonal trends**: Relevance changes with season, holidays, events
- **Host reliability**: Cancellation rates and response times factor in

This is why Airbnb's papers emphasize **counterfactual evaluation**: Understanding how ranking changes would impact user behavior without running constant A/B tests (expensive and slow).

### Maps Ranking

Airbnb's 2025 work includes "Maps Ranking Optimization", likely addressing:
- Geographic diversity in results (don't show 10 apartments all in Mission District)
- Neighborhood-level personalization (some guests prefer certain areas)
- Commute patterns (distance to landmarks guests care about)
- Visual clustering (don't show clustered results redundantly)

This is critical because geographic diversity directly impacts user satisfaction—guests want options across the city, not repetition in one neighborhood.

---

## 5. Spotify & YouTube: Audio/Video Search {#spotify-youtube}

Spotify and YouTube demonstrate that **search for different content types requires specialized embeddings and retrieval methods**.

### Spotify: Music Information Retrieval (MIR)

Spotify uses recommendation features that require understanding music similarity in high-dimensional embedding space.

#### Voyager: Open-Source ANN Library

Spotify open-sourced **Voyager**, a next-generation approximate nearest neighbor (ANN) library based on HNSW (Hierarchical Navigable Small Worlds):

**Performance vs Predecessors:**
- **10x faster** than Spotify's previous Annoy library (at same recall)
- **50% more accuracy** at same speed
- **4x less memory** than Annoy
- **16x less memory** than raw HNSW

This performance improvement is significant for production deployment. At Spotify's scale, 10x speedup means serving recommendations 10x faster or using 10x less hardware.

#### Music Embeddings Pipeline

```
Audio Content
    |
    v
Audio Feature Extraction (Spectrograms, MFCC, Chroma)
    |
    v
Neural Encoder (CNN/Transformer)
    |
    v
Track Embedding (e.g., 128-dimensional vector)
    |
    v
User Embedding (Derived from listening history)
    |
    v
ANN Index (Voyager/HNSW)
    |
    v
Candidate Recommendation (Top-K nearest neighbors)
    |
    v
Re-ranking with:
        - Collaborative signals (user-user, item-item)
        - Metadata (artist, genre, era)
        - Diversity (avoid repetition)
```

#### Spotify's Insight: Co-Occurrence Matters

Spotify's key insight: **The closer two tracks appear together in playlists, the closer they should be in embedding space**. This is captured in training objectives:
- Contrastive learning: Pulls co-occurring tracks close, pushes others apart
- Playlist prediction: Predict next track in a playlist
- Co-listening patterns: Users who listen to A also listen to B

#### Discover Weekly: The Canonical Example

Spotify's Discover Weekly playlist:
1. Build user embedding from 3+ months of listening history
2. Find 100+ candidate tracks via Voyager ANN in track embedding space
3. Rank candidates by:
   - Freshness (new releases weighted higher)
   - Artist diversity (avoid 10 songs from same artist)
   - Genre diversity
   - Playlist context (does this song fit the vibe?)
4. Generate playlist with 30 songs

This is **pure collaborative filtering + embedding search**, scaled to 500M+ users.

### YouTube: Video Retrieval

YouTube's search handles 8B+ daily searches with specialized retrieval for video content.

#### Two-Stage Architecture (Documented)

```
Stage 1: Candidate Generation
    User Query -> Query Embedding
    Candidate Gen Model -> Retrieves 100s from millions
    Methods:
        - Co-watch similarity (users who watched A watched B)
        - Embedding similarity
        - Keyword matching
        - Browse history

Stage 2: Ranking
    Input: 100-200 candidate videos
    Features:
        - User context (history, preferences, location)
        - Query context (search text, intent)
        - Video features (view count, rating, upload date)
        - Cross features (query-video similarity)

    Prediction Tasks (via MMoE):
        - Click-through rate (CTR)
        - Watch time
        - Engagement (likes, comments, shares)
```

The multi-task learning (MMoE = Multi-task Mixture of Experts) combines multiple objectives:
- **Objective balance**: YouTube optimizes for watch time (long-term) vs clicks (short-term)
- **Re-weighting**: Different objectives get different weights during serving
- **Context-dependent**: Weights change based on user context (logged-in vs not, on desktop vs mobile)

#### Embedding Models for Video

YouTube's embeddings capture:
- **Content similarity**: Videos about similar topics
- **User interest alignment**: What this user typically watches
- **Temporal dynamics**: Trending content vs evergreen
- **Cross-modal**: Text (titles, descriptions) + visual (thumbnails, frames) + audio

#### Special Challenges

- **Sheer volume**: 500+ hours uploaded per minute, billions of existing videos
- **Long tail**: Most videos get <100 views; embeddings for new videos must be seeded from metadata
- **Cold-start**: New users have no watch history; solve via demographic embeddings
- **Real-time signals**: Trending videos change within hours; freshness is critical

---

## 6. Two-Tower Retrieval Model Pattern {#two-tower-pattern}

The two-tower model is the dominant retrieval pattern in production search systems. Understanding its architecture, training, and deployment is essential for modern search.

### Architecture

A two-tower system (also called dual-encoder or Siamese network) has two separate neural networks:

```
Input: Query                     Input: Item
   |                               |
   v                               v
Query Tower                     Item Tower
(Transformer/CNN)              (Transformer/CNN)
   |                               |
   v                               v
Query Embedding (d dims)       Item Embedding (d dims)
   |                               |
   +-----------Dot Product----------+
                  |
                  v
            Similarity Score
              (Float value)
```

### Why This Pattern Dominates

**1. Training Efficiency**
- Query encoding (expensive NN forward pass) happens once per query
- Item encoding happens offline, amortized across billions of queries
- At training time: compute loss between query and positive/negative items

**2. Serving Efficiency**
- Offline: Pre-compute and store all item embeddings (~vectors for all items)
- Online: Encode query (single NN forward pass), search via ANN
- Sub-millisecond latency on billion-scale corpora

**3. Update Flexibility**
- New items: Compute embedding offline, add to index (no retraining)
- Retiring items: Remove from index (no model changes)
- Model improvements: Re-encode all items, replace index

### Training Objectives

Two-tower models are trained with contrastive losses:

```python
# Contrastive learning formulation
for query, positive_item, negative_items in training_data:
    query_emb = query_tower(query)              # (d,)
    pos_emb = item_tower(positive_item)         # (d,)
    neg_embs = item_tower(negative_items)       # (N, d)

    # Similarity scores
    pos_score = dot(query_emb, pos_emb)         # scalar
    neg_scores = matmul(query_emb, neg_embs.T)  # (N,)

    # Loss: pull positive close, push negatives far
    loss = softmax_cross_entropy([pos_score] + neg_scores)
```

Key insights:
- **Hard negative mining**: Choose negatives that are "hard" (high similarity but not relevant)
- **Negative sampling**: Can't use all non-relevant items; sample intelligently
- **Temperature scaling**: Adjust softmax temperature to control loss geometry
- **In-batch negatives**: Use other positives in batch as negatives (very efficient)

### Production Considerations

**1. Serving Infrastructure**
```
Client
  |
  v
Query Encoder (small, fast NN)
  |
  v
Query Embedding (vector)
  |
  v
ANN Index (HNSW/ScaNN/etc)
  |
  v
Candidate Items (100-1000)
  |
  v
Re-ranker (more complex model)
  |
  v
Final Results
```

**2. Index Management**
- **HNSW**: Hierarchical Navigable Small Worlds (Spotify's Voyager, Elasticsearch)
- **ScaNN**: Google's Scalable Nearest Neighbors (Google Cloud, some internal systems)
- **DiskANN**: Microsoft's disk-friendly ANN (suitable for very large indexes)
- **IVF+PQ**: Inverted File with Product Quantization (Faiss baseline)

**3. Memory vs Accuracy Trade-offs**
- **Quantization**: 32-bit -> 8-bit embeddings (4x memory reduction, slight accuracy loss)
- **Product Quantization**: Further reduce with table lookups
- **Pruning**: Remove less important items from index
- **Sharding**: Split large indexes across machines

### Common Pitfalls

**1. Training-Serving Skew**
- Train on in-batch negatives (all queries from batch as potential negatives)
- Serve with ANN (only nearby items as negatives)
- Solution: Use hard negatives from production logs in training

**2. Dead Zone Problem**
- Random embeddings can have high dot product with queries simply by chance
- Solution: Initialize carefully, use cosine similarity instead of dot product

**3. Index Staleness**
- Items added/updated daily but index rebuilt weekly
- Solution: Use hybrid systems (ANN + inverted index for recent items)

### Extending Two-Tower

Modern systems extend the basic pattern:

**1. Hybrid Loss**
```
total_loss = contrastive_loss + pointwise_loss + ranking_loss
```
Mix contrastive (discrimination) with pointwise (calibration) objectives.

**2. Hard Negative Mining**
Use production queries that retrieved irrelevant items, make them training examples.

**3. Cross-Encoder Fusion**
```
Two-tower scores -> Top 100 candidates
Cross-encoder -> Re-rank top 100 (slower, more accurate)
```

**4. Multi-Tower for Context**
```
Query Tower + User Context Tower + Item Context Tower -> Fusion
```
Encode multiple entity types, fuse embeddings.

---

## 7. Multi-Stage Ranking Pipelines {#multi-stage-ranking}

Production search systems universally use **multi-stage ranking** (also called funneling or cascading) because the compute-accuracy tradeoff demands it.

### The Funnel Pattern

```
Corpus: 1 billion items
    |
    v
Stage 1: Candidate Generation (Fast, Cheap)
    Retrieve: 10,000 candidates via BM25 + categorical filters
    Latency: <10ms
    Compute: O(log N) with inverted index

    |
    v
Stage 2: Initial Ranking (Medium, Medium)
    Retrieve: 500 candidates via two-tower embedding similarity
    Latency: 10-50ms (ANN lookup + initial scoring)
    Compute: O(log N) with ANN index

    |
    v
Stage 3: Main Ranking (Slow, Expensive)
    Retrieve: 100-200 candidates via full neural ranking model
    Latency: 50-200ms (requires 1000+ features)
    Compute: O(N) but N is small; deep model inference

    |
    v
Stage 4: Final Ranking/Personalization (Optional)
    Retrieve: 10-20 final items with business logic, LLM re-ranking, etc.
    Latency: 100-500ms
    Compute: Context-dependent (LLM calls, database lookups)

    |
    v
User Results
```

### Why This Pattern

The fundamental reason: **Model complexity vs compute budget**.

```
Accuracy Gain    Compute Cost
      ^                ^
      |      /|        |      /|
      |     / |        |     / |
      |    /  |        |    /  |
      |   /   |        |   /   |
      |  /    |        |  /    |
      | /     |        | /     |
      |/______|        |/______|
      Stage    Stage   Stage    Stage
```

A simple model (BM25) gets 70% accuracy with O(log N) compute.
A complex model (BERT + MLPs + attention) gets 90% accuracy with O(N) compute.

**Solution**: Use simple models on all items, complex models on refined set.

### Stage 1: Candidate Generation

Purpose: Reduce from billions to thousands.

**Methods:**

1. **Inverted Index (BM25)**
   - Fast: O(log N) per query via index structure
   - Effective: Well-tuned BM25 gets 70-80% of relevant results
   - Used by: Google, Elasticsearch, every search engine
   - Example: Query "best coffee shops brooklyn" -> match with 20,000 documents mentioning these terms

2. **Multi-Channel Retrieval**
   - Run multiple independent retrievers in parallel
   - Channel 1: Keywords + metadata filters
   - Channel 2: Query embedding + collaborative signals
   - Channel 3: Browse history + trending items
   - Channel 4: Diversity-seeking (sparse candidates)
   - Union or blend results from all channels

3. **Pre-computed Nearness**
   - Pre-compute for each item: what are similar items?
   - At query time: retrieve seed item, get its neighbors
   - Saves expensive embedding computation at serving time

### Stage 2: Initial Ranking

Purpose: Apply richer signals to refine candidates.

**Methods:**

1. **Two-Tower Embedding Model**
   - Compute query embedding (single NN forward)
   - ANN lookup in pre-computed item embeddings
   - Re-rank by similarity
   - Latency: 10-50ms for billions of items

2. **Learning-to-Rank (LTR) Models**
   - Gradient boosted trees (XGBoost, LightGBM)
   - 50-500 features per item (query-item relevance, popularity, freshness, etc.)
   - Much cheaper than deep neural networks
   - Latency: 20-100ms for 500 candidates

3. **Listwise Ranking Models**
   - Take a list of candidates, re-rank them
   - Account for interdependencies (position bias, diversity)
   - More expensive than pointwise but better quality

### Stage 3: Main Ranking

Purpose: Final precision via complex models.

**Methods:**

1. **Deep Learning Ranking Models**
   - Input: Query features + item features + context features
   - Architecture: Deep feed-forward networks, transformers, or attention-based
   - Features: 1000+ (query text, item text, user history, images, metadata, embeddings)
   - Output: Relevance score
   - Latency: 100-300ms for 100-200 items

2. **Cross-Encoders**
   - Input: Concatenate [query, item]
   - Process jointly (not independently like two-tower)
   - Captures fine-grained interactions
   - More accurate than two-tower but O(N) compute
   - Trade-off: Use two-tower for retrieval (fast), cross-encoder for re-ranking (slow)

3. **Multi-Task Learning**
   - Predict multiple objectives simultaneously: CTR, conversion, watch time, engagement, etc.
   - Use MMoE (Multi-task Mixture of Experts) architecture
   - Blend objectives via weighted sum
   - Used by: YouTube, LinkedIn, Uber, Pinterest

### Stage 4: Final Ranking / Post-Processing

Purpose: Apply business logic, personalization, diversity constraints.

**Methods:**

1. **Business Logic**
   - Boost sponsored results (ads)
   - Enforce freshness (recently updated items first)
   - Apply inventory constraints (out of stock items lower)
   - Enforce category limits (don't show 10 items from same brand)

2. **Diversity Constraints**
   - Use MMR (Maximal Marginal Relevance) to select diverse results
   - Formulation: Select items that maximize relevance - diversity_penalty * redundancy_with_previous
   - Ensures result variety

3. **LLM-Based Re-ranking (Emerging)**
   - Pass top candidates + query to LLM
   - LLM provides nuanced relevance judgment
   - Used by: Pinterest (LLM teacher for student model)
   - Tradeoff: Expensive but high quality; use sparingly

### Key Insights

**1. Latency Budgeting**
```
Total budget: 200ms
Stage 1: <10ms (inverted index)
Stage 2: <50ms (ANN + initial scoring)
Stage 3: <100ms (deep model)
Stage 4: <40ms (post-processing)
```

Budget is finite. Stages must fit within it. If a stage takes too long, remove it or simplify.

**2. Recall at Each Stage**
```
Stage 1: 100% recall (return all relevant items from index)
Stage 2: 95% recall (ANN may miss some similar items)
Stage 3: 90% recall (final ranking may reorder but doesn't remove good items)
Stage 4: 85% recall (business logic might filter out some items)
```

Early stages must have high recall. Later stages optimize precision.

**3. Cascading Failures**
If stage 1 misses a relevant item, no later stage can recover it. Invest heavily in stage 1 quality.

### Multi-Stage vs End-to-End

**Cascading (Multi-Stage)**: Different model at each stage
- Pros: Controllable, tunable per stage, easy to diagnose
- Cons: Training-serving skew, optimization mismatch

**End-to-End Learning**: Single model optimized for final ranking
- Pros: Unified objective, consistent training-serving
- Cons: Hard to debug, expensive to train, less interpretable

Production systems use cascading with careful monitoring for skew.

---

## 8. Feature Stores and Real-Time Feature Serving {#feature-stores}

Modern search systems generate thousands of features per item (relevance, user interaction, contextual, temporal). **Feature stores** are the infrastructure that manages this complexity.

### What is a Feature Store?

A feature store is a centralized repository that:
1. **Computes features** from raw data via ETL pipelines
2. **Stores features** in both offline (historical) and online (low-latency) stores
3. **Serves features** to training (offline) and inference (online) with consistency
4. **Manages versions** so that training and serving use the same feature definitions

### Dual-Layer Architecture

```
Feature Computation
        |
        +-> Offline Store (Data Warehouse)
        |   Storage: Columnar (Snowflake, BigQuery)
        |   Use: Training ML models
        |   Latency: Seconds to minutes
        |   Access: Batch queries
        |
        +-> Online Store (In-Memory Cache)
            Storage: KV database (Redis, DynamoDB, Cassandra)
            Use: Real-time inference
            Latency: <50ms
            Access: Entity-keyed lookups
```

### Feature Types

**1. Query Features**
- Query text, length, language
- Parsed intent (category, brand, price range)
- Query embedding

**2. Item Features**
- Title, description, category
- Price, availability, inventory
- Rating, review count
- Trending score (views in last hour)
- Item embedding

**3. User Features**
- User ID, location, device type
- Historical CTR, conversion rate
- Viewing history (last 10 items viewed)
- User embedding
- Purchase history summary (avg price, category distribution)

**4. Context Features**
- Time of day, day of week
- Season, holiday
- Device, app version
- User geographic location
- Session length so far

**5. Cross Features** (Query-Item-User)
- BM25 score (query vs item title)
- Embedding similarity (query embedding dot item embedding)
- User has seen similar item before (binary)
- Historical CTR for user on this item category

### Challenges and Solutions

**Challenge 1: Freshness vs Latency**

Some features are rapidly changing:
- Trending score (updates every minute)
- Inventory level (updates frequently)
- User session state (updates constantly)

**Solution:**
- Frequent recomputation in online store (update every minute for trending)
- In-memory caching with TTL (Time-To-Live)
- Hybrid approach: Compute-on-demand for very fresh features, cache others

**Challenge 2: Training-Serving Skew**

Training used yesterday's data, but serving uses today's data. Features might be computed differently:
- Training uses historical events (off-session)
- Serving uses real-time data (on-session)
- Aggregation windows differ

**Solution:**
- Enforce consistent feature computation code (single definition)
- Log features at training time, verify serving uses same values
- Monitor for statistical shifts in feature distributions

**Challenge 3: Scale**

At Perplexity (200M+ queries/day) or Pinterest (600M+ monthly searches):
- Computing 1000 features for each candidate in real-time is infeasible
- Need pre-computed features, updated incrementally

**Solution:**
```
Batch Computation (Offline, Hourly):
    Raw data + feature definitions -> Spark/Flink
    Compute all features for all items
    Store in online store

Real-Time Updates (Online, Per-Event):
    User action (click, purchase) -> event stream (Kafka)
    Update derived features (user history, popularity)
    Invalidate cached features (TTL triggers)
```

### Popular Feature Store Solutions

1. **Feast** (Open-source)
   - Python-native, integrates with popular tools (Spark, Snowflake, DynamoDB)
   - Feature definitions as code
   - Offline/online consistency checking
   - Used by some startups, less common at big tech

2. **Tecton** (Commercial)
   - Built on same ideas as Feast but proprietary
   - Real-time feature engineering
   - Lineage and governance
   - Used at some enterprises

3. **Custom-Built** (Most common at big tech)
   - Perplexity, Pinterest, Airbnb, Spotify all build custom feature stores
   - Tailored to specific data infrastructure (Kafka, Spark, Presto, etc.)
   - Reasons: Scale requirements, legacy systems, unique use cases

### Example: Query Rewrite Features

A practical example of feature engineering in search:

```python
# Query-level features computed at search time
query = "best coffee shops in brooklyn"
features = {
    # Raw features
    "query_text": query,
    "query_length": 5,
    "query_language": "en",

    # Embedding feature
    "query_embedding": embedding_model(query),  # 768-dim vector

    # NLP parse features
    "parsed_intent": {
        "entity_type": "location",
        "location": "brooklyn",
        "category": "coffee_shops",
        "qualifier": "best"
    },

    # User personalization
    "user_location": user.location,
    "user_search_history": user.recent_queries,

    # Context
    "hour_of_day": 14,
    "day_of_week": "friday",
    "device": "mobile"
}

# Pair with item features at ranking time
for item in candidate_items:
    combined_features = {
        **query_features,
        **item.features,
        "relevance_score": bm25(query, item),
        "distance_miles": distance(user.location, item.location),
        "user_viewed_similar": user_viewed_category(item.category),
    }

    # Pass to ranking model
    score = ranking_model.predict(combined_features)
```

---

## 9. Lessons Learned at Scale {#lessons-learned}

Examining production systems at companies handling 100M-1B+ queries daily reveals hard-won lessons.

### 1. Retrieval Quality is Paramount

**Lesson**: Spending effort on retrieval (candidate generation, early ranking) is often higher ROI than improving final ranking.

**Why**: A great ranker can't rescue poor candidates. If the top 100 candidates are all irrelevant, even a perfect final ranker gives bad results.

**Data**: Perplexity's shift to Vespa for better hybrid retrieval, Pinterest's focus on SearchSage embeddings, YouTube's multi-channel candidate generation—all prioritize retrieval quality.

**Implementation:**
- Invest in query understanding (parsing, intent detection)
- Combine signals (lexical + semantic + metadata)
- Monitor retrieval recall at each stage
- A/B test retrieval changes even though they're less visible than ranking changes

### 2. Embeddings Are a Fundamental Building Block

**Lesson**: Nearly all modern search systems are embedding-centric. Query embeddings, item embeddings, user embeddings are foundational.

**Why**: Embeddings capture semantic similarity, enable ANN search at scale, are trainable end-to-end.

**Data**:
- Spotify built Voyager for embedding search
- Pinterest uses SearchSage embeddings
- YouTube uses learned embeddings for users and videos
- Google TensorFlow's two-towers architecture is embedding-based

**Implementation:**
- Learn task-specific embeddings (not just fine-tune pre-trained)
- Use contrastive learning with hard negatives
- Quantize embeddings for memory efficiency
- Regularly update embeddings from production logs

### 3. LLMs Enhance Ranking, Not Just User Interaction

**Lesson**: LLMs are tools for improving ranking (via distillation, annotation) not just for generating responses to users.

**Data**: Pinterest fine-tunes LLMs (Llama-3-8B) to label relevance, then distills into lightweight models for serving.

**Why This Matters**:
- LLMs are expensive at serving time
- But LLMs can label training data automatically
- Distillation transfers that quality to fast, cheap models
- This pattern is likely to proliferate

**Implementation:**
- Use open-source LLMs (Llama, Mistral) for labeling
- Fine-tune on domain-specific labeled data
- Distill into smaller models (4B -> 1B parameters)
- Evaluate distilled model thoroughly before deploying

### 4. Context-Aware Ranking is Standard

**Lesson**: Relevance is not static—it changes based on user, session, time, location, device.

**Data**:
- Netflix applies session-based personalization
- Airbnb personalizes by guest profile and booking history
- Uber uses geospatial context for driver matching
- LinkedIn personalizes job recommendations

**Implementation:**
- Build user embeddings from history
- Include session context (recent actions, current session length)
- Include environment context (time, location, device)
- Use real-time features with short TTLs

### 5. Multi-Stage Ranking is Universal

**Lesson**: No company runs a single ranking model on the entire corpus.

**Why**: Compute constraints. A 1B-item corpus processed with a 200ms model = 200B ms of compute per second = infeasible.

**Data**: Every system discussed (Perplexity, Pinterest, YouTube, Netflix, Spotify, Airbnb, LinkedIn, Uber, Google, Amazon) uses 2-4 stages.

**Implementation:**
- Stage 1: <10ms (BM25, metadata filters, categorical rules)
- Stage 2: <50ms (embedding similarity, learning-to-rank trees)
- Stage 3: <100ms (deep learning models, 1000+ features)
- Stage 4: <40ms (business logic, diversity, post-processing)

### 6. Diversity Matters More Than Optimizing for Single Metric

**Lesson**: Optimizing purely for relevance often harms user satisfaction. Need to optimize for diversity, serendipity, coverage.

**Data**:
- Spotify diversifies Discover Weekly by genre, artist, era
- YouTube diversifies recommendations across content types
- Pinterest adds diversity filters to avoid pin redundancy
- Airbnb diversifies results across neighborhoods

**Why**:
- Pure relevance is boring (all recommendations are similar)
- Users want choice, exploration, surprise
- Diversity improves long-term engagement

**Implementation:**
- Use MMR (Maximal Marginal Relevance) for diverse ranking
- Add constraints (limit items from same source/brand/category)
- Vary temperature/randomness based on user (some want diversity, some want precision)

### 7. Freshness Requires Hybrid Indexing

**Lesson**: Real-time content (new items, updated metadata) requires special handling in retrieval.

**Data**:
- Perplexity needs fresh web content for current events
- YouTube has 500+ hours uploaded per minute
- Airbnb has nightly availability/pricing updates
- Pinterest has millions of pins added daily

**Problem**: ANN indexes are expensive to rebuild. Keeping them fresh with new items is slow.

**Solution**: Hybrid indexing
```
Retrieval Strategy:
    1. ANN index (rebuilt daily/weekly) for historical items
    2. Inverted index (updated in real-time) for recent items
    3. Union results, re-rank with fresh items boosted
```

### 8. Monitor and Debug at Scale

**Lesson**: Production issues are subtle and require sophisticated monitoring.

**Common Issues**:
- **Position bias**: ML models learn that items at top of list are good (they get more clicks), creating feedback loop
- **Popularity bias**: Models overweight popular items, hurting tail
- **Temporal shift**: Model trained on data from Monday doesn't work well on Friday
- **User confusion**: Model's ranking is confusing (e.g., results seem random)

**Solutions**:
- A/B test ranking changes (the gold standard)
- Use inverse propensity weighting (IPW) to debias clicks
- Interleave experimental and control rankings
- Monitor distribution of features, predictions, user engagement metrics

### 9. Small Models > Large Models at Scale

**Lesson**: Distillation from large (slow, expensive) to small (fast, cheap) models is the practical pattern.

**Data**: Pinterest distills LLMs to lightweight student models. YouTube uses this pattern extensively.

**Tradeoff**:
- Large model: 90% accuracy, 500ms latency per item
- Small model: 87% accuracy, 50ms latency per item
- Small model is more useful in production (can process 10x items in time budget)

**Implementation**:
- Train large model (teacher) thoroughly
- Fine-tune on domain data
- Distill into smaller model (student)
- Use teacher predictions as soft labels for student
- A/B test student vs teacher; student is often better in production due to diversity

### 10. Investment in Infrastructure Compounds

**Lesson**: Building good infrastructure (Vespa for Perplexity, Voyager for Spotify, custom feature stores) pays massive dividends over time.

**Why**:
- Reduces iteration time (faster experiments = more learning)
- Enables scale (handles 10x growth without major rewrite)
- Improves debuggability (clear signal flow)
- Attracts talent (engineers like good infrastructure)

**Data**: Perplexity partnered with Vespa specifically because unified retrieval-ranking-inference reduced engineering burden.

---

## 10. Applying These Patterns to Smaller-Scale Systems {#scaling-down}

Not every system needs to handle Perplexity's scale (200M daily queries). Here's how to apply these patterns to smaller, more typical systems.

### Scaling Pyramid

```
Scale Level        QPS        Approach            Stack
------------------------------------------------------------
Tiny              <100       Simple search       Single model (BM25 + heuristics)
Small            100-1K      Two-stage           Embedding retrieval + simple ranker
Medium           1K-100K     Three-stage         Retrieval + LTR + deep model
Large           100K-1M      Full pipeline       Candidate gen + ranking + post-proc
Massive          1M+         Distributed         Sharded corpus + feature store
```

### Tier 1: Tiny Systems (<100 QPS)

**Constraint**: Can't afford complex infrastructure.

**Approach**:
```
1. Use existing tools (Elasticsearch, Postgres full-text)
2. Simple BM25 ranking + hand-crafted boosts
3. User personalization: rule-based (categories they viewed)
4. No embeddings needed yet
```

**Example Stack**:
- Elasticsearch for indexing
- FastAPI for query API
- In-memory cache for hot queries
- PostgreSQL for user history
- Batch daily recompute of scores

### Tier 2: Small Systems (100-1K QPS)

**Constraint**: Can invest in simple ML.

**Approach**:
```
Stage 1: Elasticsearch (BM25)
    |
    +-> Retrieve top 1000

Stage 2: Simple embeddings
    |
    +-> Use pre-trained model (Sentence-BERT)
    +-> Compute query embedding
    +-> ANN lookup in item embeddings
    +-> Retrieve top 100

Final: Return results, cache popular queries
```

**Example Stack**:
- Elasticsearch + Kibana for search
- Sentence-BERT (pre-trained) for embeddings
- Faiss for ANN indexing (rebuilds nightly)
- FastAPI for inference server
- Redis for result caching
- Simple database for user history

**Tools**:
- BM25: Elasticsearch, Lucene
- Embeddings: Sentence-BERT, all-MiniLM-L6-v2
- ANN: Faiss, Annoy
- Hosting: Docker + simple Kubernetes

### Tier 3: Medium Systems (1K-100K QPS)

**Constraint**: Can afford feature engineering, simple ML ranking.

**Approach**:
```
Stage 1: Lexical + categorical
    BM25 + category filters -> 5000 candidates
    Latency: <10ms

Stage 2: Embedding + collaborative
    Query embedding + item embedding similarity
    User collaborative signals
    -> 500 candidates
    Latency: <50ms

Stage 3: LTR ranking
    XGBoost trained on relevance labels
    500+ features
    -> 100 top candidates
    Latency: <50ms

Final: Post-processing + caching
```

**Example Stack**:
- Elasticsearch for inverted index
- Vector database (Pinecone, Weaviate) for embeddings
- Feast (open-source) or custom for feature store
- XGBoost for ranking
- Python FastAPI service orchestrating stages
- Kafka for event logging
- Snowflake for feature computation
- Redis for online feature cache

**Development**:
1. Instrument system to collect labels (user clicks, conversions)
2. Compute features for clicked vs non-clicked items
3. Train XGBoost ranker
4. A/B test against baseline
5. Deploy and monitor

### Tier 4: Large Systems (100K-1M QPS)

**Constraint**: Can invest in feature store, distributed serving, complex models.

**Approach**: Multi-stage as described in Section 7, with:
- Advanced candidate generation (multi-channel)
- Deep learning rankers with 1000+ features
- Feature store for consistent train/serve
- A/B testing framework
- Online learning from production signals

**Example Stack**:
- Vespa, Elasticsearch, or proprietary for retrieval
- Custom feature store (or Tecton/Feast)
- TensorFlow or PyTorch for deep ranking models
- Distributed inference (Ray, TensorFlow Serving)
- Kafka for event streaming
- Feature warehouse (Snowflake, BigQuery, Redshift)
- Experiment platform for A/B testing

### Tier 5: Massive Systems (1M+ QPS)

**Approach**: Full production architecture as described in this document.

**Requirements**:
- Distributed retrieval (Vespa, custom)
- Feature store at scale (custom)
- Real-time feature serving (<50ms)
- Multiple ranking models in pipeline
- Sophisticated experimentation
- Custom infrastructure for monitoring, debugging

**Example Companies**: Perplexity, Pinterest, YouTube, Spotify, Amazon, Google

---

## Practical Implementation Guide

### For a New Project at Tier 2 (100-1K QPS)

**Week 1-2: Foundation**
```
1. Set up Elasticsearch
   - Ingest item corpus (products, documents, posts)
   - Define BM25 parameters
   - Expose query API

2. Set up Sentence-BERT
   - Download pre-trained model
   - Batch embed all items (~10x cheaper per item)
   - Save embeddings

3. Set up Faiss
   - Load embeddings into Faiss index
   - Test ANN queries
   - Benchmark latency
```

**Week 3-4: Two-Stage Ranking**
```
1. Create query service
   - Accept query
   - Stage 1: BM25 retrieval (top 1000)
   - Stage 2: Embedding retrieval (top 100)
   - Return results

2. Add user personalization
   - Track clicks/conversions
   - Compute user embeddings from history
   - Boost items similar to user preferences

3. Add simple post-processing
   - Diversity: avoid duplicate categories
   - Freshness: boost recent items
   - Business logic: boost sponsored
```

**Week 5-6: Learning-to-Rank**
```
1. Collect training data
   - Log queries + results + user actions
   - Compute features for each query-result pair
   - Label as relevant (clicked/converted) or not

2. Train ranking model
   - XGBoost on 50-100 features
   - Cross-validate performance
   - Feature importance analysis

3. A/B test
   - Deploy to 10% of traffic
   - Monitor click-through rate, conversion rate
   - Expand if positive
```

**Ongoing: Monitoring**
```
- Query latency per stage
- Cache hit rate
- Feature distributions (detect shift)
- User feedback (thumbs up/down on results)
- A/B test results
```

### Cost Estimation

**For 1K QPS system**:
```
Compute:
  - Elasticsearch node: $100/month
  - Query inference (GPU for embeddings): $200/month
  - Feature serving (Redis): $50/month
  Total: ~$350/month

Development:
  - 3-4 engineers, 2 months
  - ~$150K in salary
  - ~$10K in tools/compute for development
```

**ROI**: If system drives even 1% improvement in user satisfaction or conversion, it's worth it.

---

## Conclusion

Production search architectures across major tech companies share fundamental patterns:

1. **Multi-stage ranking**: Cheap + fast on all items, complex + slow on refined set
2. **Embedding-centric retrieval**: Dense vectors, ANN indexes, learned similarity
3. **Hybrid signals**: Lexical + semantic + metadata + collaborative + engagement
4. **Real-time personalization**: User, session, and contextual features served at <100ms
5. **Feature infrastructure**: Consistent feature computation for train/serve alignment
6. **Diversity and business logic**: Balance relevance with variety and platform goals
7. **Sophisticated monitoring**: A/B testing, offline evaluation, production telemetry

These aren't theoretical best practices—they're empirically validated at billions of queries per day. Start simple (Tier 1-2) and evolve toward complexity only when you hit scale.

The systems described in this encyclopedia (Perplexity, Pinterest, Airbnb, Spotify, YouTube, LinkedIn, Netflix, Google, Amazon, Uber) represent the frontier of search technology. Each has achieved mastery in their domain through years of engineering and iteration.

The good news: The fundamental patterns are now well-documented, tools are available (Vespa, Feast, Faiss, etc.), and teams of engineers have published detailed technical work. You can apply these patterns to your system regardless of scale.

---

## References and Further Reading

### Perplexity & Vespa
- [How Perplexity uses Vespa.ai](https://vespa.ai/perplexity/)
- [Vespa Blog: Perplexity Case Study](https://blog.vespa.ai/perplexity-show-what-great-rag-takes/)
- [Architecting and Evaluating an AI-First Search API](https://research.perplexity.ai/articles/architecting-and-evaluating-an-ai-first-search-api)

### Pinterest Search
- [LLM-Powered Relevance Assessment for Pinterest Search](https://medium.com/pinterest-engineering/llm-powered-relevance-assessment-for-pinterest-search-b846489e358d)
- [OmniSearchSage: Multi-Task Multi-Entity Embeddings](https://arxiv.org/html/2404.16260v1)
- [Improving Pinterest Search with LLMs](https://arxiv.org/html/2410.17152v1)

### Airbnb Search
- [Academic Publications 2025](https://medium.com/airbnb-engineering/academic-publications-airbnb-tech-2025-year-in-review-7d79f57d3b52)
- [Embedding-Based Retrieval for Airbnb Search](https://sites.google.com/view/airbnb-relevance-publications/home)
- [Search Ranking and Personalization at Airbnb](https://dl.acm.org/doi/10.1145/3109859.3109920)

### Spotify
- [Introducing Voyager: Spotify's ANN Library](https://engineering.atspotify.com/2023/10/introducing-voyager-spotifys-new-nearest-neighbor-search-library)
- [Voyager GitHub Repository](https://github.com/spotify/voyager)

### YouTube & Video Search
- [YouTube Recommendation Architecture](https://github.com/GokuMohandas/casual-digressions/blob/master/notes/youtube_recommendations.md)
- [Two-Stage Recommendation Patterns](https://fanluo.me/article/design-a-modern-recommendation-system)

### LinkedIn
- [LinkedIn Economic Graph](https://economicgraph.linkedin.com/)
- [LiRank: Industrial Large Scale Ranking Models](https://arxiv.org/html/2402.06859v1)

### Netflix
- [Netflix Personalization and Recommendations](https://research.netflix.com/research-area/recommendations)
- [Netflix PRS Workshop 2025](https://prs2025.splashthat.com/)

### Google Search
- [Google AI Overviews and Gemini Integration](https://blog.google/products-and-platforms/products/search/)
- [AI Mode in Google Search](https://blog.google/products-and-platforms/products/search/ai-mode-ai-overviews-updates/)

### Amazon
- [Amazon A9 and A10 Algorithms](https://www.salsify.com/blog/amazon-a9-vs-amazon-a10)
- [Amazon Product Search and Ranking](https://scaleinsights.com/learn/a9-algorithm-on-amazon)

### Uber
- [Uber's Recommendation Applications](https://www.uber.com/blog/innovative-recommendation-applications-using-two-tower-embeddings/)
- [Uber Eats Search Optimization](https://www.infoq.com/presentations/optimization-search-uber/)
- [Orders Near You: Real-Time Geospatial](https://www.uber.com/blog/orders-near-you/)

### Architectural Patterns
- [Two-Tower Model Overview](https://blog.reachsumit.com/posts/2023/03/two-tower-model/)
- [TensorFlow Two-Towers Architecture](https://cloud.google.com/blog/products/ai-machine-learning/scaling-deep-retrieval-tensorflow-two-towers-architecture)
- [Multi-Stage Ranking Pipelines](https://medium.com/@zaiinn440/one-stop-guide-for-production-recommendation-systems-9491f68d92e3)
- [Re-Ranking Mechanisms in RAG](https://medium.com/@adnanmasood/re-ranking-mechanisms-in-retrieval-augmented-generation-pipelines-an-overview-8e24303ee789)

### Feature Stores
- [Feast Feature Store](https://feast.dev/)
- [Feature Store 101](https://aerospike.com/blog/feature-store/)
- [Tecton Feature Platform](https://www.tecton.ai/blog/what-is-a-feature-store/)

### ANN/Vector Search
- [Approximate Nearest Neighbor Search Guide](https://www.pinecone.io/learn/a-developers-guide-to-ann-algorithms/)
- [Elasticsearch ANN Search](https://www.elastic.org/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0)
- [Google Cloud Spanner ANN](https://cloud.google.com/blog/products/databases/spanner-now-supports-approximate-nearest-neighbor-search/)

### Vespa
- [Vespa AI Platform](https://vespa.ai/)
- [Vespa Architecture](https://vespa.ai/architecture/)
- [Building Billion-Scale Vector Search](https://medium.com/vespa/building-billion-scale-vector-search-part-two-94f0101d15dd)

---

**Document Version**: 1.0
**Last Updated**: March 2026
**Scope**: Production search systems at scale (100M-1B+ daily queries)
**Audience**: Search engineers, ML engineers, system designers building or improving search products

---

## See Also (Cross-References)

→ **references/00-stack-blueprints/** — Blueprint #10: High-Scale Platform with multi-stage ranking
→ **references/00-search-recipes/** — Recipe #13: Multi-Stage Ranking Pipeline for production systems
→ **references/00-benchmark-matrix/** — Search engine performance comparison at scale
→ **references/33-search-at-scale/** — Search at scale technical deep dives and optimization
→ **references/07-architecture-patterns/** — Architecture patterns for distributed search systems
→ **references/45-neural-reranking-distillation/** — Reranking in production pipelines and latency budgets
→ **references/30-recommendations-vs-search/** — Recommendations vs search tradeoffs in production

