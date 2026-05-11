# Search System Migration Playbooks

A comprehensive guide to 10 common search upgrade paths with detailed implementation steps, risk assessment, and rollback strategies.

---

## 1. BM25-Only → Hybrid Search

### Starting State
- Keyword search using BM25 (Elasticsearch, Solr, or custom inverted index)
- No semantic understanding of queries
- Limited recall on paraphrased or synonym queries
- Typical NDCG@10: 0.65-0.72

### Target State
- Dual retrieval: BM25 + dense vector embeddings
- Reciprocal rank fusion combining both signals
- Supports semantic similarity and keyword precision
- Target NDCG@10: 0.78-0.85

### Expected Improvement
- **NDCG Improvement**: +12-15%
- **Recall@100**: +18-22%
- **Latency**: +35-45ms (from 50-80ms to 85-125ms)
- **Cost**: +30-40% (embedding generation + vector storage)

### Risk Assessment
- **Rank collapse**: RRF weights poorly tuned → queries return low-quality results
- **Embedding quality**: Weak model → embeddings don't capture intent
- **Latency spike**: Vector search slower than expected
- **Storage explosion**: Embedding vectors consume significant disk space

### Step-by-Step Migration Plan

**Step 1: Select embedding model**
```python
# Option A: Lightweight (fast, cost-effective)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # 384-dim, 22MB
embeddings = model.encode(documents, batch_size=32)

# Option B: High-quality (slower, more accurate)
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # 768-dim
embeddings = model.encode(documents, batch_size=16)
```

**Step 2: Generate embeddings for existing corpus**
```python
from elasticsearch import Elasticsearch
es = Elasticsearch(['localhost:9200'])

batch_size = 100
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    embeddings = model.encode(batch)

    actions = []
    for doc, embedding in zip(batch, embeddings):
        actions.append({
            '_op_type': 'update',
            '_index': 'docs_hybrid',
            '_id': doc['id'],
            'doc': {'embedding': embedding.tolist()}
        })

    from elasticsearch.helpers import bulk
    bulk(es, actions)
```

**Step 3: Create dual-mapping index**
```json
{
  "mappings": {
    "properties": {
      "text": {
        "type": "text",
        "analyzer": "standard"
      },
      "embedding": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

**Step 4: Implement RRF fusion**
```python
def hybrid_search(query, k=10):
    # BM25 retrieval
    bm25_results = es.search(
        index='docs_hybrid',
        body={'query': {'match': {'text': query}}},
        size=100  # Retrieve more for fusion
    )

    # Vector retrieval
    query_embedding = model.encode(query)
    vector_results = es.search(
        index='docs_hybrid',
        body={'query': {'knn': {'embedding': {
            'vector': query_embedding.tolist(),
            'k': 100
        }}}},
        size=100
    )

    # Reciprocal rank fusion
    rrf_scores = {}
    for rank, hit in enumerate(bm25_results['hits']['hits']):
        doc_id = hit['_id']
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(60 + rank)

    for rank, hit in enumerate(vector_results['hits']['hits']):
        doc_id = hit['_id']
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(60 + rank)

    # Sort by RRF score
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]
```

**Step 5: A/B test hybrid vs keyword-only**
```python
# Route 50% traffic to hybrid, 50% to BM25-only
import random

def search_with_variant(query):
    if random.random() < 0.5:
        results = bm25_search(query)
        variant = 'control'
    else:
        results = hybrid_search(query)
        variant = 'treatment'

    # Log for analysis
    log_event({
        'query': query,
        'variant': variant,
        'results': [r['_id'] for r in results],
        'timestamp': datetime.now()
    })

    return results
```

### Rollback Plan
1. Keep BM25-only index in parallel during hybrid testing (2-3 weeks)
2. If NDCG regresses >5%, revert to BM25-only alias
3. Disable embedding generation job
4. Delete dense_vector fields to free storage
5. Monitor query latency for 48 hours

### Testing Checklist
- [ ] Embedding model inference latency <50ms per batch
- [ ] Vector index size reasonable (<20GB for 1M docs)
- [ ] RRF tuning: NDCG improves on held-out test set
- [ ] Latency p95 < 150ms under load
- [ ] 1000+ random queries manually judged (hybrid vs BM25)
- [ ] Click-through rate stable (no CTR degradation)
- [ ] Recall improves for paraphrased queries
- [ ] Keyword precision maintained (no noise from semantics)

### See Also
→ See: references/09-metrics-observability/
→ See: references/02-reranking-models/

---

## 2. No Reranker → Cross-Encoder Reranking

### Starting State
- Single-stage retrieval (BM25 or dense vector)
- Top-K results returned directly to users
- NDCG@10: 0.70-0.75
- Latency: 40-60ms

### Target State
- Two-stage pipeline: retrieval → reranking
- Cross-encoder reranker improves ranking quality
- Candidate generation at scale, precision reranking
- NDCG@10: 0.80-0.88

### Expected Improvement
- **NDCG Improvement**: +10-18%
- **MRR**: +12-20%
- **Latency**: +80-150ms (reranking overhead)
- **Cost**: +40-60% (inference cost)

### Risk Assessment
- **Reranker bottleneck**: Reranking 1000 candidates slow
- **Poor model choice**: Cross-encoder doesn't understand domain
- **Latency budget exceeded**: Reranking adds unacceptable delay
- **Training data imbalance**: Reranker overfits to rare queries

### Step-by-Step Migration Plan

**Step 1: Choose reranker model**
```python
# Option A: API-based (easiest, highest cost)
import cohere
co = cohere.Client(api_key="YOUR_API_KEY")

def rerank_with_cohere(query, documents):
    results = co.rerank(
        model="rerank-english-v2.0",
        query=query,
        documents=documents,
        top_n=10
    )
    return results.results

# Option B: Open-source (self-hosted)
from FlagEmbedding import FlagReranker
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)

def rerank_with_bge(query, documents):
    # documents: list of {'text': '...'}
    passages = [doc['text'] for doc in documents]
    scores = reranker.compute_score([[query, p] for p in passages])

    # Sort by score
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:10]]

# Option C: Fine-tune domain-specific
from sentence_transformers import CrossEncoder
model = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')
# Fine-tune on your relevance judgments for 2-3 epochs
```

**Step 2: Build candidate retrieval stage**
```python
def retrieve_candidates(query, k_retrieval=100):
    # Retrieve more candidates for reranking
    results = bm25_search(query, size=k_retrieval)
    return results

def rerank_candidates(query, candidates, k_final=10):
    # Extract text from candidates
    documents = [{'id': c['_id'], 'text': c['_source']['text']} for c in candidates]

    # Call reranker
    reranked = rerank_with_bge(query, documents)

    return reranked[:k_final]

def two_stage_search(query):
    candidates = retrieve_candidates(query, k_retrieval=100)
    final_results = rerank_candidates(query, candidates, k_final=10)
    return final_results
```

**Step 3: Allocate latency budget**
```python
import time

def search_with_budget(query, latency_budget_ms=150):
    start = time.time()

    # Retrieval: 50ms budget
    retrieval_start = time.time()
    candidates = retrieve_candidates(query, k_retrieval=100)
    retrieval_time = (time.time() - retrieval_start) * 1000

    remaining_budget = latency_budget_ms - retrieval_time

    # Reranking: adapt k based on budget
    if remaining_budget > 100:
        k_rerank = 100  # Full reranking
    elif remaining_budget > 50:
        k_rerank = 50   # Partial reranking
    else:
        return candidates[:10]  # Skip reranking

    final_results = rerank_candidates(query, candidates[:k_rerank], k_final=10)

    total_time = (time.time() - start) * 1000

    return {
        'results': final_results,
        'latency_ms': total_time,
        'budget_used': total_time / latency_budget_ms
    }
```

**Step 4: Monitor NDCG improvement**
```python
from sklearn.metrics import dcg_score, ndcg_score

def evaluate_reranker(test_queries, judgments):
    # judgments: {query_id: {doc_id: relevance_score}}

    before_ndcg = []
    after_ndcg = []

    for query_id, query_text in test_queries:
        # Before reranking
        candidates = retrieve_candidates(query_text, k_retrieval=100)
        before_ranking = [c['_id'] for c in candidates[:10]]
        before_rel = [judgments[query_id].get(doc_id, 0) for doc_id in before_ranking]
        before_ndcg.append(ndcg_score([before_rel], [[i+1 for i, r in enumerate(before_rel) if r > 0]]))

        # After reranking
        reranked = rerank_candidates(query_text, candidates, k_final=10)
        after_ranking = [r['id'] for r in reranked]
        after_rel = [judgments[query_id].get(doc_id, 0) for doc_id in after_ranking]
        after_ndcg.append(ndcg_score([after_rel], [[i+1 for i, r in enumerate(after_rel) if r > 0]]))

    print(f"NDCG Before: {sum(before_ndcg)/len(before_ndcg):.4f}")
    print(f"NDCG After:  {sum(after_ndcg)/len(after_ndcg):.4f}")
    print(f"Improvement: {(sum(after_ndcg) - sum(before_ndcg))/len(before_ndcg)*100:+.2f}%")
```

### Rollback Plan
1. Keep retrieval-only endpoint active during rollout
2. Route 10% traffic to reranking pipeline for 1 week
3. If latency p95 >200ms or NDCG <baseline, revert
4. Disable reranker inference endpoint
5. Fall back to retrieval-only results

### Testing Checklist
- [ ] Reranker inference latency <60ms per document batch
- [ ] NDCG improvement validated on test set (>5%)
- [ ] Latency p95 under acceptable budget
- [ ] Recall maintained (top candidates never removed)
- [ ] Cold-start handling (new documents benefit from reranking)
- [ ] Robustness to out-of-domain queries
- [ ] User satisfaction metrics (click-through, dwell time) improve
- [ ] Cost per query acceptable

### See Also
→ See: references/01-hybrid-search/
→ See: references/09-metrics-observability/

---

## 3. Fuse.js → Server-Side Search

### Starting State
- Client-side search using Fuse.js
- Works for <10K documents
- No network latency
- Entire dataset must be downloaded to client
- NDCG@10: 0.60-0.68

### Target State
- Server-side search with dedicated index
- Support for 1M+ documents
- Sub-100ms search latency over network
- Advanced features: faceting, filters, autocomplete
- NDCG@10: 0.75-0.82

### Expected Improvement
- **Performance**: +5-10x faster for large datasets
- **Recall**: +25-35% (full index search vs client-side approximation)
- **UX**: instant autocomplete, faceted search
- **Cost**: $50-200/month (vs free client-side)

### Risk Assessment
- **Data sync**: Stale index if documents not synced properly
- **API rate limiting**: Unthrotted requests overwhelm server
- **Migration downtime**: Brief search unavailability
- **Feature parity**: Some Fuse.js filters not available in server backend

### Step-by-Step Migration Plan

**Step 1: Choose target platform**
```python
# Option A: Meilisearch (best UX, easiest)
from meilisearch import Client
client = Client('http://localhost:7700', 'MASTER_KEY')

# Create searchable index
index = client.create_index('products', {'primaryKey': 'id'})
index.add_documents([
    {'id': '1', 'title': 'Product A', 'price': 99.99},
    {'id': '2', 'title': 'Product B', 'price': 149.99}
])

# Option B: Typesense (speed + customization)
import typesense
client = typesense.Client({
    'nodes': [{'host': 'localhost', 'port': 8108, 'protocol': 'http'}],
    'api_key': 'xyz'
})

client.collections.create({
    'name': 'products',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'title', 'type': 'string'},
        {'name': 'price', 'type': 'float'}
    ]
})

# Option C: PostgreSQL FTS (if data already in Postgres)
import psycopg2
conn = psycopg2.connect("dbname=products user=postgres")
cur = conn.cursor()

cur.execute("""
CREATE INDEX idx_title_search ON products USING GIN (to_tsvector('english', title))
""")
```

**Step 2: Data migration**
```python
def migrate_fuse_to_server(fuse_data, target_backend):
    # Transform Fuse.js documents
    documents = []
    for doc in fuse_data:
        documents.append({
            'id': doc.get('id') or str(len(documents)),
            'title': doc.get('title', ''),
            'text': doc.get('text', ''),
            'metadata': {k: v for k, v in doc.items()
                        if k not in ['id', 'title', 'text']}
        })

    # Batch insert (important for performance)
    batch_size = 1000
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        if target_backend == 'meilisearch':
            client.index('products').add_documents(batch)
        elif target_backend == 'postgres':
            insert_to_postgres(batch)

    print(f"Migrated {len(documents)} documents")
```

**Step 3: API compatibility layer**
```python
# Old Fuse.js API: client.search(query)
# New server API: GET /api/search?q=query

from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)

    if not query:
        return jsonify({'results': []})

    # Server-side search
    results = client.index('products').search(query, {'limit': limit})

    # Return format compatible with Fuse.js client code
    return jsonify({
        'results': [
            {
                'item': result,
                'score': result.get('_rankingScore', 1.0)
            }
            for result in results['hits']
        ]
    })

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')

    suggestions = client.index('products').search(query, {
        'limit': 5,
        'attributesToRetrieve': ['title']
    })

    return jsonify({
        'suggestions': [s['title'] for s in suggestions['hits']]
    })
```

**Step 4: Zero-downtime switchover**
```javascript
// Frontend: detect which backend to use
const SEARCH_BACKEND = localStorage.getItem('search_backend') || 'fuse';

async function search(query) {
    if (SEARCH_BACKEND === 'fuse') {
        // Old client-side search
        return fuseIndex.search(query);
    } else {
        // New server-side search
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        return response.json();
    }
}

// Gradually rollout (10% → 25% → 50% → 100%)
function determineBackend(userId) {
    const hash = hashUserId(userId);
    if (hash % 100 < 10) return 'server';  // 10% server-side
    return 'fuse';                          // 90% client-side
}
```

### Rollback Plan
1. Keep Fuse.js data in memory during transition (2-4 weeks)
2. Verify server index completeness for all queries
3. If P99 latency >300ms, revert to client-side
4. Monitor data consistency: alert if server index stale
5. Maintain both backends for 1 week before full cutover

### Testing Checklist
- [ ] All documents migrated and searchable
- [ ] Search latency P95 <100ms
- [ ] Autocomplete latency <50ms
- [ ] Result ranking matches or exceeds Fuse.js
- [ ] Faceted search works on all fields
- [ ] Filters (price range, category) function correctly
- [ ] Mobile performance acceptable
- [ ] 100 random queries compared (server vs Fuse.js)
- [ ] Data sync: new documents indexed within 5 minutes

### See Also
→ See: references/01-hybrid-search/
→ See: references/09-metrics-observability/

---

## 4. Single-Stage → Multi-Stage Pipeline

### Starting State
- Single retrieval stage (BM25 or dense vector)
- Direct ranking of all candidates
- Monolithic latency budget
- NDCG@10: 0.70-0.75
- Latency: 60-100ms

### Target State
- Multi-stage: retrieval → candidate gen → reranking → personalization
- Each stage optimized independently
- Distributed latency budget
- NDCG@10: 0.82-0.90
- Latency: 120-180ms (acceptable trade-off)

### Expected Improvement
- **NDCG Improvement**: +15-22%
- **Precision@1**: +18-25%
- **Latency p99**: +50-80ms
- **Cost**: +60-80% (multi-stage overhead)

### Risk Assessment
- **Pipeline bottleneck**: One slow stage blocks entire pipeline
- **Cascading errors**: Mistakes in retrieval exclude good candidates
- **Complexity debt**: Hard to debug multi-stage interactions
- **Cost explosion**: Each stage adds compute cost

### Step-by-Step Migration Plan

**Step 1: Design pipeline architecture**
```python
from dataclasses import dataclass
from typing import List
import time

@dataclass
class SearchResult:
    doc_id: str
    score: float
    metadata: dict

class SearchPipeline:
    def __init__(self):
        self.retriever = BM25Retriever()
        self.candidate_gen = CandidateGenerator()
        self.reranker = CrossEncoderReranker()
        self.personalizer = PersonalizationEngine()

    def search(self, query, user_id, latency_budget_ms=180):
        start = time.time()

        # Stage 1: Retrieval (50-70ms budget)
        retrieval_start = time.time()
        candidates = self.retriever.search(query, k=1000)
        retrieval_time = (time.time() - retrieval_start) * 1000
        remaining = latency_budget_ms - retrieval_time

        # Stage 2: Candidate generation (30-50ms budget)
        cand_gen_start = time.time()
        filtered = self.candidate_gen.filter_and_dedupe(candidates)
        cand_gen_time = (time.time() - cand_gen_start) * 1000
        remaining -= cand_gen_time

        # Stage 3: Reranking (50-80ms budget)
        rerank_start = time.time()
        k_rerank = min(100, int(remaining / 2))  # Adaptive k
        reranked = self.reranker.rerank(query, filtered[:k_rerank])
        rerank_time = (time.time() - rerank_start) * 1000
        remaining -= rerank_time

        # Stage 4: Personalization (20-30ms budget)
        if remaining > 30:
            personalized = self.personalizer.reorder(reranked[:20], user_id)
        else:
            personalized = reranked[:10]

        total_time = (time.time() - start) * 1000

        return {
            'results': personalized,
            'latency_ms': total_time,
            'stages': {
                'retrieval': retrieval_time,
                'candidate_gen': cand_gen_time,
                'reranking': rerank_time,
                'personalization': (total_time - retrieval_time - cand_gen_time - rerank_time)
            }
        }
```

**Step 2: Implement retrieval stage**
```python
class BM25Retriever:
    def search(self, query, k=1000):
        # Retrieve many candidates for downstream stages
        results = self.es.search(
            query={'match': {'text': query}},
            size=k,
            min_score=0.1  # Filter obvious low-quality results
        )

        return [SearchResult(
            doc_id=hit['_id'],
            score=hit['_score'],
            metadata=hit['_source']
        ) for hit in results['hits']['hits']]
```

**Step 3: Implement candidate generation stage**
```python
class CandidateGenerator:
    def filter_and_dedupe(self, candidates):
        # Remove duplicates (same content, different IDs)
        seen_content = {}
        deduplicated = []

        for candidate in candidates:
            content_hash = hash(candidate.metadata['text'][:500])
            if content_hash not in seen_content:
                seen_content[content_hash] = candidate
                deduplicated.append(candidate)

        # Filter by quality threshold
        filtered = [c for c in deduplicated if c.metadata.get('quality_score', 0) > 0.3]

        # Ensure diversity (not all same domain/author)
        return self.enforce_diversity(filtered, max_same_author=3)

    def enforce_diversity(self, candidates, max_same_author):
        result = []
        author_counts = {}

        for candidate in candidates:
            author = candidate.metadata.get('author', 'unknown')
            count = author_counts.get(author, 0)

            if count < max_same_author:
                result.append(candidate)
                author_counts[author] = count + 1

        return result
```

**Step 4: Implement reranking stage**
```python
class CrossEncoderReranker:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')

    def rerank(self, query, candidates):
        # Prepare inputs
        passages = [c.metadata['text'] for c in candidates]
        pairs = [[query, p] for p in passages]

        # Compute scores
        scores = self.model.predict(pairs)

        # Re-rank
        scored = list(zip(candidates, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        return [SearchResult(
            doc_id=c.doc_id,
            score=float(s),
            metadata=c.metadata
        ) for c, s in scored]
```

**Step 5: Implement personalization stage**
```python
class PersonalizationEngine:
    def reorder(self, results, user_id):
        # Boost documents matching user interests
        user_profile = self.get_user_profile(user_id)

        scored = []
        for result in results:
            boost = 1.0

            # Boost if matches user category preferences
            if result.metadata.get('category') in user_profile['preferred_categories']:
                boost *= 1.5

            # Penalize if matches excluded categories
            if result.metadata.get('category') in user_profile['excluded_categories']:
                boost *= 0.5

            # Boost if author is followed by user
            if result.metadata.get('author') in user_profile['followed_authors']:
                boost *= 1.3

            scored.append((result, result.score * boost))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [r for r, _ in scored]
```

### Rollback Plan
1. Maintain single-stage endpoint during rollout
2. Compare results between pipelines offline
3. If p99 latency exceeds budget by >20%, revert to single-stage
4. If NDCG drops >2%, investigate personalization stage
5. Keep detailed logs of each stage latency for debugging

### Testing Checklist
- [ ] Each stage latency measured independently
- [ ] Total latency under budget (p95 <180ms)
- [ ] NDCG improves at each stage addition
- [ ] No "lucky ranking" (reranking doesn't remove good candidates)
- [ ] Personalization doesn't hurt cold-start users
- [ ] 500+ queries evaluated across stages
- [ ] Latency distribution normal (no outliers)
- [ ] Graceful degradation if a stage fails

### See Also
→ See: references/02-reranking-models/
→ See: references/09-metrics-observability/

---

## 5. Elasticsearch → Hybrid Elasticsearch

### Starting State
- Pure BM25 search in Elasticsearch
- No semantic search capabilities
- Vocabulary mismatch problems (exact term matching)
- NDCG@10: 0.68-0.73

### Target State
- Elasticsearch with dense_vector + kNN
- Combined BM25 + dense vector queries
- Optional: ELSER (learned sparse embeddings)
- NDCG@10: 0.80-0.87

### Expected Improvement
- **NDCG Improvement**: +12-18%
- **Recall**: +20-25%
- **Latency**: +40-60ms
- **Storage**: +30-50% (embedding vectors)
- **Cost**: +35-45%

### Risk Assessment
- **Cluster overhead**: Dense vectors consume memory
- **Indexing slowdown**: Embedding generation bottleneck
- **Version incompatibility**: Old ES versions don't support kNN
- **Query complexity**: Hybrid queries are harder to debug

### Step-by-Step Migration Plan

**Step 1: Enable dense_vector field type**
```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['localhost:9200'])

# Create index with dense_vector
mapping = {
    'mappings': {
        'properties': {
            'title': {'type': 'text', 'analyzer': 'standard'},
            'body': {'type': 'text', 'analyzer': 'standard'},
            'embedding': {
                'type': 'dense_vector',
                'dims': 384,
                'index': True,
                'similarity': 'cosine'
            }
        }
    },
    'settings': {
        'number_of_shards': 3,
        'number_of_replicas': 1,
        'index.codec': 'best_compression'  # Compress vector storage
    }
}

es.indices.create(index='articles_hybrid', body=mapping)
```

**Step 2: Generate embeddings for existing documents**
```python
from sentence_transformers import SentenceTransformer
from elasticsearch.helpers import bulk

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def generate_embeddings_for_es(index_name, batch_size=100):
    # Scan all documents in index
    documents = []
    for doc in es.helpers.scan(es, index=index_name, query={'query': {'match_all': {}}}):
        documents.append(doc)

    # Generate embeddings in batches
    actions = []
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        # Combine title + body for embedding
        texts = [f"{d['_source']['title']} {d['_source']['body']}" for d in batch]
        embeddings = model.encode(texts, batch_size=batch_size)

        for doc, embedding in zip(batch, embeddings):
            actions.append({
                '_op_type': 'update',
                '_index': index_name,
                '_id': doc['_id'],
                'doc': {'embedding': embedding.tolist()}
            })

        if len(actions) >= 1000:
            bulk(es, actions, chunk_size=1000)
            actions = []

    if actions:
        bulk(es, actions)

generate_embeddings_for_es('articles_hybrid')
```

**Step 3: Implement hybrid BM25 + kNN query**
```python
def hybrid_es_search(query, k=10):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    query_embedding = model.encode(query)

    # Hybrid query combining BM25 and kNN
    search_body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': query,
                            'fields': ['title^2', 'body'],
                            'type': 'best_fields',
                            'operator': 'or'
                        }
                    }
                ]
            }
        },
        'knn': {
            'field': 'embedding',
            'query_vector': query_embedding.tolist(),
            'k': 100,
            'num_candidates': 500
        },
        'rank': {
            'rrf': {}  # Reciprocal rank fusion
        },
        'size': k
    }

    results = es.search(index='articles_hybrid', body=search_body)
    return results['hits']['hits']

# Alternative: separate queries with manual RRF fusion
def hybrid_es_search_manual_rrf(query, k=10, bm25_weight=0.6, vector_weight=0.4):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    query_embedding = model.encode(query)

    # BM25 search
    bm25_results = es.search(
        index='articles_hybrid',
        body={
            'query': {'multi_match': {
                'query': query,
                'fields': ['title^2', 'body']
            }},
            'size': 100
        }
    )

    # Vector search
    vector_results = es.search(
        index='articles_hybrid',
        body={
            'query': {'knn': {
                'field': 'embedding',
                'query_vector': query_embedding.tolist(),
                'k': 100,
                'num_candidates': 500
            }},
            'size': 100
        }
    )

    # Manual RRF fusion
    rrf_scores = {}
    for rank, hit in enumerate(bm25_results['hits']['hits']):
        doc_id = hit['_id']
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + bm25_weight / (60 + rank)

    for rank, hit in enumerate(vector_results['hits']['hits']):
        doc_id = hit['_id']
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + vector_weight / (60 + rank)

    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]
```

**Step 4: Add ELSER (Elasticsearch Learned Sparse)**
```python
# Create ELSER index mapping
elser_mapping = {
    'mappings': {
        'properties': {
            'title': {'type': 'text'},
            'body': {'type': 'text'},
            'embedding': {'type': 'dense_vector', 'dims': 384, 'index': True, 'similarity': 'cosine'},
            'sparse_embedding': {
                'type': 'sparse_vector'  # Requires Elasticsearch 8.13+
            }
        }
    }
}

es.indices.create(index='articles_elser', body=elser_mapping)

# Generate ELSER vectors with ingest pipeline
ingest_pipeline = {
    'processors': [
        {
            'inference': {
                'model_id': '.elser_model_2_linux-x86_64',
                'input_output': [
                    {'input_field': 'body', 'output_field': 'sparse_embedding'}
                ]
            }
        }
    ]
}

es.ingest.put_pipeline(id='elser-pipeline', body=ingest_pipeline)

# Query with ELSER
def hybrid_with_elser(query):
    results = es.search(
        index='articles_elser',
        body={
            'query': {
                'bool': {
                    'should': [
                        {'match': {'body': query}},
                        {'sparse_vector_match': {'sparse_embedding': query}}
                    ]
                }
            },
            'size': 10
        }
    )
    return results['hits']['hits']
```

### Rollback Plan
1. Keep old BM25-only index active during hybrid testing
2. Alias points to hybrid index; easy to switch back
3. If NDCG regresses, revert alias to BM25 index
4. Monitor search latency; if p99 >250ms, investigate
5. Delete dense_vector fields to reclaim storage if rolling back

### Testing Checklist
- [ ] Embedding generation completes for all documents
- [ ] kNN queries return results in <60ms
- [ ] RRF tuning optimized (try 0.5/0.5, 0.6/0.4 splits)
- [ ] NDCG improves on test set
- [ ] Vector index size acceptable
- [ ] Cluster memory usage under control
- [ ] 1000+ queries manually judged (hybrid vs BM25-only)
- [ ] ELSER adds marginal gains if used

### See Also
→ See: references/01-hybrid-search/
→ See: references/10-postgres-pgvector/

---

## 6. Pure Keyword → SPLADE

### Starting State
- Pure BM25 keyword search
- Vocabulary mismatch issues (synonyms, paraphrasing)
- Limited precision
- NDCG@10: 0.65-0.70

### Target State
- SPLADE (Sparse Lexical and Semantic Embeddings)
- Learned sparse representations
- Combined lexical and semantic signals
- NDCG@10: 0.78-0.85

### Expected Improvement
- **NDCG Improvement**: +15-22%
- **Recall**: +20-28%
- **Latency**: +30-50ms (SPLADE generation)
- **Storage**: Index size similar to BM25
- **Cost**: +25-35%

### Risk Assessment
- **SPLADE generation bottleneck**: Model inference slow
- **Index not compatible**: Need Qdrant/Vespa support for sparse vectors
- **Vocabulary mismatch**: SPLADE weights unfamiliar tokens
- **Domain-specific weakness**: SPLADE trained on general corpus

### Step-by-Step Migration Plan

**Step 1: Set up SPLADE model**
```python
import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM

# Load SPLADE model (trained sparse retriever)
model_name = "naver/splade-cocondenser-ensembledistil"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForMaskedLM.from_pretrained(model_name)

def get_splade_vector(text, topk=100):
    """Generate SPLADE sparse vector for text"""
    tokens = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        output = model(**tokens)
        logits = output.logits

    # Get vocabulary expansion weights
    vocab_size = len(tokenizer)
    weights = torch.log(1 + torch.nn.functional.relu(logits[0]))  # Log activation

    # Get top-k tokens
    topk_weights, topk_indices = torch.topk(weights, min(topk, vocab_size))

    # Create sparse representation
    sparse_vector = {}
    for idx, weight in zip(topk_indices.cpu(), topk_weights.cpu()):
        token_id = idx.item()
        token_str = tokenizer.decode([token_id])
        weight_val = weight.item()
        if weight_val > 0:
            sparse_vector[token_str] = weight_val

    return sparse_vector

# Test
text = "information retrieval deep learning"
splade_vec = get_splade_vector(text)
print(splade_vec)  # {'information': 0.45, 'retrieval': 0.42, 'deep': 0.38, ...}
```

**Step 2: Index documents with SPLADE**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, SparseVector

client = QdrantClient(":memory:")

# Create collection with sparse vectors
client.create_collection(
    collection_name="documents_splade",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    sparse_vectors_config={
        "splade": SparseVector(index=True)
    }
)

# Index documents
def index_with_splade(documents):
    points = []

    for i, doc in enumerate(documents):
        # Generate SPLADE vector
        splade_vec = get_splade_vector(doc['text'])

        # Create point
        point = PointStruct(
            id=i,
            vector={
                'splade': splade_vec  # Sparse vector
            },
            payload={
                'doc_id': doc['id'],
                'text': doc['text'][:500]  # Store snippet
            }
        )
        points.append(point)

    client.upsert(
        collection_name="documents_splade",
        points=points
    )

    print(f"Indexed {len(documents)} documents with SPLADE")

# Index your corpus
index_with_splade(documents)
```

**Step 3: Query with SPLADE**
```python
def search_splade(query, k=10):
    """Search using SPLADE representations"""

    # Get SPLADE vector for query
    query_splade = get_splade_vector(query, topk=50)

    # Search in Qdrant
    results = client.search(
        collection_name="documents_splade",
        query_vector=({"splade": query_splade}),
        limit=k
    )

    return [
        {
            'doc_id': r.payload['doc_id'],
            'text': r.payload['text'],
            'score': r.score
        }
        for r in results
    ]

# Test
results = search_splade("how does machine learning work")
for r in results:
    print(f"{r['doc_id']}: {r['score']:.3f}")
```

**Step 4: Compare SPLADE vs BM25**
```python
from sklearn.metrics import ndcg_score

def benchmark_splade_vs_bm25(test_queries, judgments):
    """Compare SPLADE and BM25 on test set"""

    bm25_ndcg = []
    splade_ndcg = []

    for query_id, query_text in test_queries:
        # BM25 search
        bm25_results = bm25_search(query_text, k=10)
        bm25_ranking = [r['doc_id'] for r in bm25_results]
        bm25_relevance = [judgments[query_id].get(doc_id, 0) for doc_id in bm25_ranking]
        bm25_ndcg.append(ndcg_score([bm25_relevance], [[i+1 for i, r in enumerate(bm25_relevance) if r > 0]]))

        # SPLADE search
        splade_results = search_splade(query_text, k=10)
        splade_ranking = [r['doc_id'] for r in splade_results]
        splade_relevance = [judgments[query_id].get(doc_id, 0) for doc_id in splade_ranking]
        splade_ndcg.append(ndcg_score([splade_relevance], [[i+1 for i, r in enumerate(splade_relevance) if r > 0]]))

    print(f"BM25 NDCG@10:   {sum(bm25_ndcg)/len(bm25_ndcg):.4f}")
    print(f"SPLADE NDCG@10: {sum(splade_ndcg)/len(splade_ndcg):.4f}")
    print(f"Improvement:    {(sum(splade_ndcg)-sum(bm25_ndcg))/len(bm25_ndcg)*100:+.2f}%")

    return {
        'bm25_ndcg': sum(bm25_ndcg)/len(bm25_ndcg),
        'splade_ndcg': sum(splade_ndcg)/len(splade_ndcg)
    }

benchmark_splade_vs_bm25(test_queries, judgments)
```

**Step 5: Hybrid SPLADE + Dense vectors**
```python
def hybrid_splade_dense_search(query, k=10):
    """Combine SPLADE with dense vectors"""

    # SPLADE search
    splade_results = search_splade(query, k=100)
    splade_docs = {r['doc_id']: r['score'] for r in splade_results}

    # Dense vector search (for semantic similarity)
    query_embedding = model_dense.encode(query)
    dense_results = client.search(
        collection_name="documents_dense",
        query_vector=query_embedding,
        limit=100
    )
    dense_docs = {r.payload['doc_id']: r.score for r in dense_results}

    # RRF fusion
    rrf_scores = {}
    for rank, (doc_id, score) in enumerate(sorted(splade_docs.items(), key=lambda x: x[1], reverse=True)):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(60 + rank)

    for rank, (doc_id, score) in enumerate(sorted(dense_docs.items(), key=lambda x: x[1], reverse=True)):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(60 + rank)

    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]
```

### Rollback Plan
1. Keep BM25 index active during SPLADE rollout
2. Route 10% traffic to SPLADE for 1 week
3. If NDCG <baseline or latency >150ms, revert to BM25
4. Monitor relevance feedback; if users click less, revert

### Testing Checklist
- [ ] SPLADE model inference latency <50ms per batch
- [ ] NDCG improves on test set (>5%)
- [ ] SPLADE handles out-of-vocabulary well
- [ ] Sparse index size reasonable
- [ ] 500+ random queries manually judged
- [ ] Domain-specific evaluation if applicable
- [ ] Recall improves for synonym queries
- [ ] Latency p95 under acceptable threshold

### See Also
→ See: references/01-hybrid-search/
→ See: references/06-rag-systems/

---

## 7. Naive RAG → Agentic RAG

### Starting State
- Simple retrieve-then-generate RAG
- No self-correction or validation
- Hallucinations possible
- Accuracy: 65-75%
- Latency: 2-3 seconds

### Target State
- Agentic RAG with self-critique
- Query rewriting, document validation
- Self-RAG with critique tokens
- Accuracy: 82-92%
- Latency: 4-8 seconds (acceptable trade-off)

### Expected Improvement
- **Accuracy**: +15-25%
- **Faithfulness**: +20-30%
- **Hallucination rate**: -40-60%
- **Latency**: +2-4x (mitigated by sampling)
- **Cost**: +80-120%

### Risk Assessment
- **Loop runaway**: Self-correction loops endlessly
- **Latency explosion**: Multiple retrieval rounds slow query
- **Model disagreement**: LLM critic contradicts generator
- **Cost explosion**: Multiple LLM calls per query

### Step-by-Step Migration Plan

**Step 1: Implement CRAG evaluation**
```python
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import json

class CRAGEvaluator:
    """Corrective RAG: evaluate retrieval quality"""

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def evaluate_documents(self, query, documents):
        """Rate documents as relevant/irrelevant/ambiguous"""

        prompt = f"""
        Query: {query}

        Documents:
        {chr(10).join([f"[{i}] {doc[:200]}" for i, doc in enumerate(documents)])}

        For each document, output: RELEVANT, IRRELEVANT, or AMBIGUOUS
        Format: [0] RELEVANT, [1] IRRELEVANT, ...
        """

        evaluation = self.llm(prompt)

        # Parse evaluation
        lines = evaluation.split('\n')[0]
        judgments = {}
        for item in lines.split(','):
            match = item.strip()  # '[0] RELEVANT'
            if '] ' in match:
                doc_id = int(match.split(']')[0].strip('['))
                judgment = match.split('] ')[1].upper()
                judgments[doc_id] = judgment

        return judgments

    def retrieve_if_needed(self, query, documents, judgments):
        """Re-retrieve if documents are irrelevant/ambiguous"""

        relevant_count = sum(1 for j in judgments.values() if j == 'RELEVANT')
        total_count = len(judgments)

        if relevant_count / total_count < 0.5:  # <50% relevant
            return 'REWRITE'  # Rewrite query
        elif 'AMBIGUOUS' in judgments.values():
            return 'RETRIEVE'  # Retrieve more
        else:
            return 'GENERATE'  # Proceed to generation

    def run(self, query):
        # Retrieve initial documents
        documents = self.retriever.retrieve(query, k=10)

        # Evaluate
        judgments = self.evaluate_documents(query, documents)
        action = self.retrieve_if_needed(query, documents, judgments)

        return {
            'action': action,
            'documents': documents,
            'judgments': judgments
        }

# Usage
evaluator = CRAGEvaluator(llm=OpenAI(), retriever=my_retriever)
result = evaluator.run("What is machine learning?")
print(f"Action: {result['action']}")  # GENERATE, REWRITE, or RETRIEVE
```

**Step 2: Implement query rewriting**
```python
class QueryRewriter:
    """Rewrite query for better retrieval"""

    def __init__(self, llm):
        self.llm = llm

    def rewrite(self, query, feedback=None):
        """Generate alternative queries"""

        prompt = f"""
        Original query: {query}
        {f"Feedback (low relevance): {feedback}" if feedback else ""}

        Generate 3 alternative queries that might retrieve better documents:
        1. [rewrite 1]
        2. [rewrite 2]
        3. [rewrite 3]
        """

        response = self.llm(prompt)

        # Parse rewrites
        rewrites = []
        for line in response.split('\n'):
            if line.startswith(('1.', '2.', '3.')):
                rewrite = line.split('. ', 1)[1].strip('[]')
                rewrites.append(rewrite)

        return rewrites

    def rewrite_and_retrieve(self, query, retriever, evaluator):
        """Rewrite and retrieve until good documents found"""

        max_attempts = 3
        for attempt in range(max_attempts):
            documents = retriever.retrieve(query, k=10)
            judgments = evaluator.evaluate_documents(query, documents)
            relevant_count = sum(1 for j in judgments.values() if j == 'RELEVANT')

            if relevant_count >= 5:  # Good enough
                return documents

            # Rewrite and try again
            feedback = f"Only {relevant_count}/10 documents relevant"
            rewrites = self.rewrite(query, feedback)
            query = rewrites[0]  # Try first rewrite

        # Fallback: return best attempt
        return documents
```

**Step 3: Implement Self-RAG with critique tokens**
```python
class SelfRAG:
    """Self-Reflective RAG with critique tokens"""

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def generate_with_critique(self, query, documents):
        """Generate answer and self-critique"""

        # Generate initial answer
        prompt_gen = f"""
        Query: {query}

        Context:
        {chr(10).join(documents[:3])}

        Generate a concise answer.
        """

        answer = self.llm(prompt_gen)

        # Critique answer
        prompt_critique = f"""
        Query: {query}
        Answer: {answer}
        Context: {documents[0][:200]}

        Is this answer:
        [CORRECT] - Fully accurate and supported by context
        [PARTIALLY_CORRECT] - Some accurate parts but incomplete
        [INCORRECT] - Inaccurate or contradicts context
        [NOT_SUPPORTED] - Not supported by provided context

        Output one tag only.
        """

        critique = self.llm(prompt_critique).strip().upper()

        return {
            'answer': answer,
            'critique': critique,
            'confident': critique in ['[CORRECT]', '[PARTIALLY_CORRECT]']
        }

    def generate_with_self_correction(self, query, documents):
        """Multi-turn generation with self-correction"""

        result = self.generate_with_critique(query, documents)

        if not result['confident'] and len(documents) > 3:
            # Try again with different documents
            result_2 = self.generate_with_critique(query, documents[3:6])

            # Choose better answer
            if result_2['confident']:
                result = result_2

        return result

# Usage
self_rag = SelfRAG(llm=OpenAI(), retriever=my_retriever)
documents = my_retriever.retrieve("What is quantum computing?", k=5)
result = self_rag.generate_with_self_correction("What is quantum computing?", documents)
print(f"Answer: {result['answer']}")
print(f"Critique: {result['critique']}")
```

**Step 4: Build agentic loop**
```python
class AgenticRAG:
    """Full agentic RAG pipeline"""

    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
        self.evaluator = CRAGEvaluator(llm, retriever)
        self.rewriter = QueryRewriter(llm)
        self.self_rag = SelfRAG(llm, retriever)

    def answer(self, query, max_iterations=3):
        """Answer query with self-correction loop"""

        current_query = query

        for iteration in range(max_iterations):
            # Retrieve
            documents = self.retriever.retrieve(current_query, k=10)

            # Evaluate
            judgments = self.evaluator.evaluate_documents(current_query, documents)
            relevant_count = sum(1 for j in judgments.values() if j == 'RELEVANT')

            if relevant_count < 3:
                # Not enough relevant docs; rewrite query
                rewrites = self.rewriter.rewrite(current_query)
                current_query = rewrites[0]
                continue

            # Generate and critique
            result = self.self_rag.generate_with_critique(current_query, documents)

            if result['confident']:
                return {
                    'answer': result['answer'],
                    'iterations': iteration + 1,
                    'documents': documents[:3],
                    'critique': result['critique']
                }

        # Fallback: return best attempt
        return result

# Usage
agentic_rag = AgenticRAG(llm=OpenAI(), retriever=my_retriever)
result = agentic_rag.answer("How does photosynthesis work?")
print(f"Answer: {result['answer']}")
print(f"Iterations: {result['iterations']}")
```

### Rollback Plan
1. Keep naive RAG endpoint active during agentic rollout
2. Compare accuracy on 500+ test queries
3. If accuracy improves <5%, revert to naive RAG
4. Monitor latency; if >10 seconds, reduce max_iterations
5. Implement timeout: abort after 8 seconds and return best answer

### Testing Checklist
- [ ] CRAG evaluation accuracy >85%
- [ ] Query rewriting improves relevance
- [ ] Self-critique detects hallucinations >80% of the time
- [ ] Latency p95 <10 seconds
- [ ] Answer accuracy improves by >10%
- [ ] Hallucination rate drops significantly
- [ ] 100+ user studies on answer quality
- [ ] Cost per query acceptable (<$0.10)

### See Also
→ See: references/04-multi-stage-pipeline/
→ See: references/09-metrics-observability/

---

## 8. Manual Synonyms → Query Understanding

### Starting State
- Hardcoded synonym lists (car → automobile → vehicle)
- Simple query expansion
- No semantic understanding
- Limited recall
- NDCG@10: 0.68-0.72

### Target State
- ML-based query understanding
- Intent classification, NER, spell correction
- Learned synonyms from embeddings
- Robust to misspellings
- NDCG@10: 0.80-0.87

### Expected Improvement
- **NDCG Improvement**: +12-20%
- **Recall**: +18-25%
- **Typo handling**: 95%+ correction rate
- **Intent understanding**: 90%+ accuracy
- **Cost**: +35-50%

### Risk Assessment
- **Over-expansion**: Too many synonyms hurt precision
- **Intent confusion**: Ambiguous queries misclassified
- **Out-of-vocabulary**: Rare terms not handled
- **Language-specific**: Models trained on English may not generalize

### Step-by-Step Migration Plan

**Step 1: Implement intent classification**
```python
from transformers import pipeline

class QueryIntentClassifier:
    """Classify query intent"""

    def __init__(self):
        # Use zero-shot classification
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        self.intent_labels = [
            "navigational",  # Looking for specific site/page
            "informational",  # Want to learn about topic
            "transactional",  # Want to buy/do something
            "local",          # Local business search
            "news"            # Looking for recent news
        ]

    def classify(self, query):
        """Classify query intent"""

        result = self.classifier(
            query,
            self.intent_labels,
            multi_class=False
        )

        return {
            'intent': result['labels'][0],
            'confidence': result['scores'][0]
        }

    def example_usage(self):
        print(self.classify("Where can I buy running shoes?"))      # transactional
        print(self.classify("Best running shoes for marathons"))    # informational
        print(self.classify("Nike official website"))               # navigational
```

**Step 2: Implement Named Entity Recognition (NER)**
```python
from transformers import pipeline

class QueryEntityExtractor:
    """Extract entities from query"""

    def __init__(self):
        self.ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

    def extract_entities(self, query):
        """Extract entities: person, location, organization, etc."""

        entities = self.ner(query)

        # Group by entity type
        entity_groups = {}
        for entity in entities:
            entity_type = entity['entity_group']
            entity_text = entity['word']

            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity_text)

        return entity_groups

    def example_usage(self):
        print(self.extract_entities("Tesla stock price in New York"))
        # {'ORG': ['Tesla'], 'LOC': ['New York']}

        print(self.extract_entities("When did Steve Jobs found Apple?"))
        # {'PER': ['Steve Jobs'], 'ORG': ['Apple']}
```

**Step 3: Implement spell correction**
```python
from symspellpy import SymSpell, Verbosity

class QuerySpellCorrector:
    """Correct spelling errors"""

    def __init__(self, max_dictionary_edit_distance=2):
        self.spell = SymSpell(max_dictionary_edit_distance=max_dictionary_edit_distance)

        # Load dictionary
        self.spell.load_dictionary("frequency_dictionary_en_82_765.txt", term_index=0, count_index=1)

    def correct(self, query):
        """Correct spelling errors"""

        suggestions = self.spell.lookup_compound(
            query,
            max_edit_distance=2,
            transfer_casing=True
        )

        if suggestions:
            return suggestions[0].term  # Best suggestion
        return query

    def example_usage(self):
        print(self.correct("machne lerning"))      # machine learning
        print(self.correct("artifical inteligence")) # artificial intelligence
        print(self.correct("quantm computing"))    # quantum computing
```

**Step 4: Implement semantic synonym expansion**
```python
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticSynonymExpander:
    """Expand query with semantic synonyms"""

    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.vocabulary = self._load_vocabulary()
        self.vocab_embeddings = self.model.encode(self.vocabulary)

    def _load_vocabulary(self):
        """Load domain vocabulary (e.g., product names, topics)"""
        return [
            "machine learning", "deep learning", "neural networks",
            "artificial intelligence", "AI", "ML",
            "transformer", "BERT", "GPT",
            # ... more terms
        ]

    def expand(self, query, k=5, threshold=0.7):
        """Find semantic synonyms for query"""

        query_embedding = self.model.encode(query)

        # Compute similarity
        similarities = np.dot(self.vocab_embeddings, query_embedding)
        similarities = similarities / (np.linalg.norm(self.vocab_embeddings, axis=1) * np.linalg.norm(query_embedding))

        # Find top-k similar terms above threshold
        top_indices = np.argsort(similarities)[::-1][:k]
        synonyms = [
            self.vocabulary[i] for i in top_indices
            if similarities[i] >= threshold
        ]

        return synonyms

    def example_usage(self):
        print(self.expand("ML models"))  # ['machine learning', 'deep learning', 'neural networks', ...]
        print(self.expand("automotive vehicles"))  # ['cars', 'vehicles', 'automobiles', ...]
```

**Step 5: Unified query understanding pipeline**
```python
class QueryUnderstandingPipeline:
    """Combine all understanding components"""

    def __init__(self):
        self.intent_classifier = QueryIntentClassifier()
        self.entity_extractor = QueryEntityExtractor()
        self.spell_corrector = QuerySpellCorrector()
        self.synonym_expander = SemanticSynonymExpander()

    def understand(self, query):
        """Full query understanding"""

        # Step 1: Spell correction
        corrected_query = self.spell_corrector.correct(query)

        # Step 2: Intent classification
        intent = self.intent_classifier.classify(corrected_query)

        # Step 3: Entity extraction
        entities = self.entity_extractor.extract_entities(corrected_query)

        # Step 4: Synonym expansion
        synonyms = self.synonym_expander.expand(corrected_query)

        return {
            'original_query': query,
            'corrected_query': corrected_query,
            'intent': intent['intent'],
            'intent_confidence': intent['confidence'],
            'entities': entities,
            'synonyms': synonyms
        }

    def search_with_understanding(self, query, retriever):
        """Search using query understanding"""

        understanding = self.understand(query)

        # Build expanded query
        expanded_query = understanding['corrected_query']
        if understanding['synonyms']:
            expanded_query += ' ' + ' OR '.join(understanding['synonyms'][:2])

        # Route to appropriate retriever based on intent
        if understanding['intent'] == 'local':
            # Use location-aware ranking
            results = retriever.search_local(expanded_query, entities=understanding['entities'])
        elif understanding['intent'] == 'navigational':
            # Boost exact domain matches
            results = retriever.search_with_boost(expanded_query, boost_type='domain')
        else:
            # Standard search
            results = retriever.search(expanded_query)

        return {
            'results': results,
            'understanding': understanding
        }

# Usage
pipeline = QueryUnderstandingPipeline()
result = pipeline.search_with_understanding("where can I by iphone 15s nearby?", my_retriever)
print(f"Corrected: {result['understanding']['corrected_query']}")
print(f"Intent: {result['understanding']['intent']}")
print(f"Results: {result['results']}")
```

### Rollback Plan
1. Keep manual synonyms in parallel during rollout
2. A/B test query understanding vs manual synonyms
3. If NDCG <baseline or latency >200ms, revert
4. Monitor false positives (incorrect corrections)
5. Gradual rollout: 10% → 25% → 50% → 100%

### Testing Checklist
- [ ] Spell correction accuracy >95%
- [ ] Intent classification accuracy >90%
- [ ] NER extraction accuracy >85%
- [ ] Synonym expansion doesn't hurt precision
- [ ] NDCG improves on test set
- [ ] Latency p95 <150ms
- [ ] Handles domain-specific terminology
- [ ] 500+ queries manually evaluated

### See Also
→ See: references/01-hybrid-search/
→ See: references/09-metrics-observability/

---

## 9. No Metrics → Full Observability

### Starting State
- No search quality metrics
- No A/B testing framework
- Blind to ranking performance
- User satisfaction unknown

### Target State
- NDCG/MRR offline evaluation
- Click tracking and analysis
- Search analytics dashboard
- A/B testing framework
- Full observability

### Expected Improvement
- **Decision making**: Data-driven improvements
- **Confidence**: Measure impact of changes
- **Debugging**: Identify problem queries
- **Quality**: Catch regressions before production

### Risk Assessment
- **Privacy concerns**: Tracking user behavior
- **Data overhead**: Logging adds latency
- **Noisy signals**: Clicks don't always mean relevance
- **Complexity**: Building infrastructure takes time

### Step-by-Step Migration Plan

**Step 1: Implement click tracking**
```python
import json
import logging
from datetime import datetime
from typing import List

class ClickTracker:
    """Track user clicks on search results"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def log_click(self, query_id: str, query: str, doc_id: str, rank: int,
                   user_id: str, session_id: str, timestamp: datetime = None):
        """Log a user click"""

        event = {
            'event_type': 'click',
            'query_id': query_id,
            'query': query,
            'doc_id': doc_id,
            'rank': rank,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': timestamp or datetime.now().isoformat(),
            'dwell_time': None  # Will be filled on session end
        }

        # Log to file/database
        self.logger.info(json.dumps(event))

    def log_impression(self, query_id: str, query: str, results: List[dict],
                       user_id: str, session_id: str):
        """Log search results shown to user"""

        event = {
            'event_type': 'impression',
            'query_id': query_id,
            'query': query,
            'results': [r['doc_id'] for r in results[:10]],
            'num_results': len(results),
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(json.dumps(event))

# Frontend integration
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    user_id = request.cookies.get('user_id')
    session_id = request.cookies.get('session_id')

    results = search_engine.search(query, k=10)

    # Track impression
    click_tracker.log_impression(
        query_id=hashlib.md5(query.encode()).hexdigest(),
        query=query,
        results=results,
        user_id=user_id,
        session_id=session_id
    )

    return jsonify({'results': results})

# Frontend: track clicks
<script>
function trackClick(docId, rank, queryId) {
    fetch('/api/click', {
        method: 'POST',
        body: JSON.stringify({
            query_id: queryId,
            doc_id: docId,
            rank: rank
        })
    });
}
</script>
```

**Step 2: Set up NDCG offline evaluation**
```python
import numpy as np
from typing import Dict, List

class OfflineEvaluator:
    """Evaluate search quality offline"""

    def __init__(self, judgments: Dict[str, Dict[str, int]]):
        """
        judgments format:
        {
            'query_1': {'doc_a': 2, 'doc_b': 1, 'doc_c': 0},
            'query_2': {'doc_x': 2, 'doc_y': 1}
        }
        """
        self.judgments = judgments

    def dcg_at_k(self, ranking: List[str], k: int, judgments: Dict) -> float:
        """Compute DCG@k"""
        dcg = 0.0
        for i, doc_id in enumerate(ranking[:k]):
            relevance = judgments.get(doc_id, 0)
            dcg += (2**relevance - 1) / np.log2(i + 2)
        return dcg

    def idcg_at_k(self, judgments: Dict, k: int) -> float:
        """Compute ideal DCG@k"""
        relevances = sorted(judgments.values(), reverse=True)[:k]
        idcg = sum((2**rel - 1) / np.log2(i + 2) for i, rel in enumerate(relevances))
        return idcg

    def ndcg_at_k(self, ranking: List[str], k: int, judgments: Dict) -> float:
        """Compute NDCG@k"""
        dcg = self.dcg_at_k(ranking, k, judgments)
        idcg = self.idcg_at_k(judgments, k)
        return dcg / idcg if idcg > 0 else 0.0

    def evaluate(self, rankings: Dict[str, List[str]], k: int = 10) -> Dict:
        """Evaluate all queries"""

        scores = {}
        for query_id, ranking in rankings.items():
            if query_id in self.judgments:
                score = self.ndcg_at_k(ranking, k, self.judgments[query_id])
                scores[query_id] = score

        # Compute averages
        mean_ndcg = np.mean(list(scores.values()))
        median_ndcg = np.median(list(scores.values()))

        return {
            'per_query': scores,
            'mean': mean_ndcg,
            'median': median_ndcg,
            'p95': np.percentile(list(scores.values()), 95)
        }

# Usage
judgments = {
    'machine learning': {'doc1': 2, 'doc2': 1, 'doc3': 0},
    'deep learning': {'doc4': 2, 'doc5': 1}
}

evaluator = OfflineEvaluator(judgments)
rankings = {
    'machine learning': ['doc1', 'doc3', 'doc2'],
    'deep learning': ['doc4', 'doc5']
}

results = evaluator.evaluate(rankings, k=3)
print(f"Mean NDCG@3: {results['mean']:.4f}")
```

**Step 3: Build search analytics dashboard**
```python
import pandas as pd
from datetime import datetime, timedelta

class SearchAnalyticsDashboard:
    """Analytics dashboard for search metrics"""

    def __init__(self, click_log_path: str):
        self.click_log_path = click_log_path
        self.df = self._load_clicks()

    def _load_clicks(self) -> pd.DataFrame:
        """Load click data from log"""
        clicks = []
        with open(self.click_log_path) as f:
            for line in f:
                clicks.append(json.loads(line))

        return pd.DataFrame(clicks)

    def ctr_by_position(self):
        """Click-through rate by rank position"""
        ctr = self.df.groupby('rank').apply(lambda x: x[x['event_type'] == 'click'].shape[0] / len(x))
        return ctr

    def most_clicked_queries(self, limit=10):
        """Top queries by clicks"""
        clicks = self.df[self.df['event_type'] == 'click']
        return clicks.groupby('query').size().sort_values(ascending=False).head(limit)

    def zero_click_queries(self):
        """Queries with no clicks"""
        impressions = self.df[self.df['event_type'] == 'impression']
        queries_with_impressions = impressions['query_id'].unique()

        clicks = self.df[self.df['event_type'] == 'click']
        queries_with_clicks = clicks['query_id'].unique()

        zero_click_ids = set(queries_with_impressions) - set(queries_with_clicks)
        return impressions[impressions['query_id'].isin(zero_click_ids)]['query'].unique()

    def mrr_from_clicks(self):
        """Reciprocal Rank (RR) from clicks"""
        clicks = self.df[self.df['event_type'] == 'click']
        rr_by_query = clicks.groupby('query_id')['rank'].apply(lambda x: 1.0 / x.iloc[0] if len(x) > 0 else 0)
        return rr_by_query.mean()

# Flask dashboard
@app.route('/dashboard')
def dashboard():
    analytics = SearchAnalyticsDashboard('/var/log/search_clicks.log')

    return render_template('dashboard.html', {
        'ctr_by_position': analytics.ctr_by_position().to_dict(),
        'top_queries': analytics.most_clicked_queries().to_dict(),
        'zero_click_queries': list(analytics.zero_click_queries()),
        'mrr': analytics.mrr_from_clicks()
    })
```

**Step 4: Implement A/B testing framework**
```python
import hashlib
from typing import Callable

class ABTestFramework:
    """A/B testing for search changes"""

    def __init__(self, salt: str = 'search_ab_test'):
        self.salt = salt

    def get_variant(self, user_id: str, test_id: str, variant_a: str, variant_b: str) -> str:
        """Deterministically assign user to variant"""

        hash_input = f"{user_id}:{test_id}:{self.salt}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)

        if hash_value % 2 == 0:
            return variant_a
        else:
            return variant_b

    def run_test(self, query: str, user_id: str, test_id: str,
                 variant_a_fn: Callable, variant_b_fn: Callable):
        """Run A/B test"""

        variant = self.get_variant(user_id, test_id, 'control', 'treatment')

        if variant == 'control':
            results = variant_a_fn(query)
            variant_name = 'control'
        else:
            results = variant_b_fn(query)
            variant_name = 'treatment'

        # Log test assignment
        self.log_test_assignment(user_id, test_id, variant_name, query)

        return results, variant_name

    def log_test_assignment(self, user_id, test_id, variant, query):
        """Log test assignment for analysis"""

        event = {
            'event_type': 'test_assignment',
            'test_id': test_id,
            'user_id': user_id,
            'variant': variant,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }

        logging.info(json.dumps(event))

    def analyze_test(self, test_id: str, metric_fn: Callable) -> Dict:
        """Analyze test results"""

        # Read all logs for this test
        control_metrics = []
        treatment_metrics = []

        with open('/var/log/search_events.log') as f:
            for line in f:
                event = json.loads(line)
                if event.get('test_id') == test_id and event.get('event_type') == 'test_assignment':
                    metric = metric_fn(event)
                    if event['variant'] == 'control':
                        control_metrics.append(metric)
                    else:
                        treatment_metrics.append(metric)

        # Compute statistics
        control_mean = np.mean(control_metrics)
        treatment_mean = np.mean(treatment_metrics)

        # T-test
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(control_metrics, treatment_metrics)

        return {
            'control_mean': control_mean,
            'treatment_mean': treatment_mean,
            'improvement': (treatment_mean - control_mean) / control_mean * 100,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

# Usage
ab_test = ABTestFramework()

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    user_id = request.cookies.get('user_id')

    # Run A/B test: new reranker vs old BM25
    results, variant = ab_test.run_test(
        query, user_id, 'test_reranker_v2',
        variant_a_fn=lambda q: bm25_search(q),
        variant_b_fn=lambda q: bm25_with_reranker(q)
    )

    return jsonify({'results': results, 'variant': variant})
```

### Rollback Plan
1. Logging doesn't affect search; safe to enable immediately
2. Start with click tracking only (non-blocking)
3. Gradually add NDCG evaluation on hold-out test set
4. A/B tests are always reversible (just change traffic split)

### Testing Checklist
- [ ] Click logging adds <10ms latency
- [ ] Logs collected reliably (no data loss)
- [ ] NDCG correlates with user satisfaction (validation)
- [ ] A/B test framework detects 5% improvements
- [ ] Dashboard loads in <2 seconds
- [ ] Privacy: no PII in logs
- [ ] Data retention policy established
- [ ] Alerts set up for ranking regressions

### See Also
→ See: references/01-hybrid-search/
→ See: references/02-reranking-models/

---

## 10. PostgreSQL FTS → pgvector Hybrid

### Starting State
- PostgreSQL full-text search (tsvector)
- BM25-like ranking via PostgreSQL
- No semantic search
- NDCG@10: 0.70-0.75
- Latency: 100-150ms

### Target State
- pgvector extension for embeddings
- Hybrid query: tsvector + vector similarity
- RRF fusion combining both signals
- NDCG@10: 0.82-0.89
- Latency: 150-200ms

### Expected Improvement
- **NDCG Improvement**: +12-18%
- **Recall**: +20-28%
- **Latency**: +50-100ms
- **Storage**: +25-35% (embedding vectors)
- **Cost**: +30-40% (increased queries)

### Risk Assessment
- **Pgvector extension stability**: Still developing
- **Index memory**: Vector indices consume RAM
- **Query complexity**: Hybrid queries harder to optimize
- **Tuning difficulty**: RRF weights require experimentation

### Step-by-Step Migration Plan

**Step 1: Install pgvector extension**
```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname FROM pg_extension WHERE extname = 'vector';

-- Create embedding column
ALTER TABLE documents ADD COLUMN embedding vector(384);

-- Create index for faster similarity search
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: IVF with inner product
CREATE INDEX ON documents USING ivfflat (embedding vector_ip_ops)
WITH (lists = 100);

-- Or HNSW index (better quality, slower build)
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Step 2: Generate embeddings for existing data**
```python
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

def generate_embeddings_postgres(db_config, batch_size=100):
    """Generate embeddings for all documents in PostgreSQL"""

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Get total count
    cur.execute("SELECT COUNT(*) FROM documents WHERE embedding IS NULL")
    total = cur.fetchone()[0]

    # Process in batches
    cur.execute("SELECT id, title, body FROM documents WHERE embedding IS NULL LIMIT %s", (batch_size,))

    while True:
        rows = cur.fetchall()
        if not rows:
            break

        # Generate embeddings
        texts = [f"{row[1]} {row[2]}" for row in rows]
        embeddings = model.encode(texts, batch_size=batch_size)

        # Update database
        for (doc_id, title, body), embedding in zip(rows, embeddings):
            embedding_list = embedding.tolist()
            cur.execute(
                "UPDATE documents SET embedding = %s WHERE id = %s",
                (embedding_list, doc_id)
            )

        conn.commit()

        # Fetch next batch
        cur.execute("SELECT id, title, body FROM documents WHERE embedding IS NULL LIMIT %s", (batch_size,))

    conn.close()

# Run embedding generation
db_config = {
    'host': 'localhost',
    'database': 'search_db',
    'user': 'postgres',
    'password': 'password'
}

generate_embeddings_postgres(db_config)
```

**Step 3: Implement vector similarity search**
```python
import psycopg2

def vector_search(query, k=10, db_config=None):
    """Search using vector similarity"""

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Generate query embedding
    query_embedding = model.encode(query)
    embedding_list = query_embedding.tolist()

    # Vector similarity search (cosine distance)
    query_sql = """
    SELECT id, title, body, 1 - (embedding <=> %s::vector) AS similarity
    FROM documents
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> %s
    LIMIT %s
    """

    cur.execute(query_sql, (embedding_list, embedding_list, k))
    results = cur.fetchall()

    conn.close()

    return [
        {'id': r[0], 'title': r[1], 'body': r[2], 'score': r[3]}
        for r in results
    ]
```

**Step 4: Implement full-text search**
```python
def fulltext_search(query, k=10, db_config=None):
    """Search using PostgreSQL full-text search"""

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Create search vector
    query_sql = """
    SELECT id, title, body,
           ts_rank(search_vector, query, 1) AS rank
    FROM documents,
         to_tsquery('english', %s) AS query
    WHERE search_vector @@ query
    ORDER BY rank DESC
    LIMIT %s
    """

    cur.execute(query_sql, (query.replace(' ', '&'), k))
    results = cur.fetchall()

    conn.close()

    return [
        {'id': r[0], 'title': r[1], 'body': r[2], 'score': r[3]}
        for r in results
    ]
```

**Step 5: Implement hybrid RRF fusion**
```python
def hybrid_search(query, k=10, db_config=None, bm25_weight=0.5, vector_weight=0.5):
    """Hybrid search combining FTS and vector similarity"""

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    # Generate query embedding
    query_embedding = model.encode(query)
    embedding_list = query_embedding.tolist()

    # Combined query with RRF
    query_sql = """
    WITH fts_results AS (
        SELECT id, title, body,
               ROW_NUMBER() OVER (ORDER BY ts_rank(search_vector, query) DESC) AS fts_rank,
               ts_rank(search_vector, query) AS fts_score
        FROM documents,
             to_tsquery('english', %s) AS query
        WHERE search_vector @@ query
        LIMIT 100
    ),
    vector_results AS (
        SELECT id, title, body,
               ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) AS vector_rank,
               1 - (embedding <=> %s::vector) AS vector_score
        FROM documents
        WHERE embedding IS NOT NULL
        LIMIT 100
    ),
    combined AS (
        SELECT COALESCE(f.id, v.id) AS id,
               COALESCE(f.title, v.title) AS title,
               COALESCE(f.body, v.body) AS body,
               COALESCE(1.0 / (60 + f.fts_rank), 0) * %s +
               COALESCE(1.0 / (60 + v.vector_rank), 0) * %s AS rrf_score
        FROM fts_results f
        FULL OUTER JOIN vector_results v ON f.id = v.id
    )
    SELECT id, title, body, rrf_score
    FROM combined
    ORDER BY rrf_score DESC
    LIMIT %s
    """

    cur.execute(query_sql, (
        query.replace(' ', '&'),
        embedding_list,
        embedding_list,
        bm25_weight,
        vector_weight,
        k
    ))

    results = cur.fetchall()
    conn.close()

    return [
        {'id': r[0], 'title': r[1], 'body': r[2], 'score': r[3]}
        for r in results
    ]

# Usage
results = hybrid_search("machine learning algorithms")
for r in results:
    print(f"{r['id']}: {r['title']} ({r['score']:.3f})")
```

**Step 6: Optimize with stored procedures**
```sql
-- Create stored procedure for hybrid search
CREATE OR REPLACE FUNCTION hybrid_search(
    p_query TEXT,
    p_k INT DEFAULT 10,
    p_bm25_weight FLOAT DEFAULT 0.5,
    p_vector_weight FLOAT DEFAULT 0.5
)
RETURNS TABLE(id INT, title TEXT, body TEXT, score FLOAT) AS $$
DECLARE
    v_query_vector vector(384);
BEGIN
    -- Generate query embedding (in Python wrapper)
    -- For now, assume p_query_vector passed as parameter

    RETURN QUERY
    WITH fts_results AS (
        SELECT documents.id,
               documents.title,
               documents.body,
               ROW_NUMBER() OVER (ORDER BY ts_rank(documents.search_vector, to_tsquery('english', p_query)) DESC) AS fts_rank
        FROM documents
        WHERE documents.search_vector @@ to_tsquery('english', p_query)
        LIMIT 100
    ),
    vector_results AS (
        SELECT documents.id,
               documents.title,
               documents.body,
               ROW_NUMBER() OVER (ORDER BY documents.embedding <=> v_query_vector) AS vector_rank
        FROM documents
        WHERE documents.embedding IS NOT NULL
        LIMIT 100
    )
    SELECT COALESCE(f.id, v.id),
           COALESCE(f.title, v.title),
           COALESCE(f.body, v.body),
           (COALESCE(1.0 / (60 + f.fts_rank), 0) * p_bm25_weight +
            COALESCE(1.0 / (60 + v.vector_rank), 0) * p_vector_weight) AS combined_score
    FROM fts_results f
    FULL OUTER JOIN vector_results v ON f.id = v.id
    ORDER BY combined_score DESC
    LIMIT p_k;
END;
$$ LANGUAGE plpgsql;
```

### Rollback Plan
1. Keep FTS-only queries active during pgvector transition
2. Verify hybrid results match or exceed FTS-only on test queries
3. If latency p99 >300ms, reduce vector index from hnsw to ivfflat
4. If NDCG doesn't improve, revert to FTS-only queries
5. Monitor pgvector extension stability

### Testing Checklist
- [ ] Embeddings generated for all documents
- [ ] Vector index builds successfully (hnsw or ivfflat)
- [ ] Vector search latency <80ms for k=100
- [ ] Hybrid query latency p95 <200ms
- [ ] RRF weights tuned (try 0.5/0.5, 0.6/0.4, 0.4/0.6)
- [ ] NDCG improves on test set
- [ ] No NULL embedding issues
- [ ] Storage space acceptable
- [ ] 500+ queries manually evaluated
- [ ] Recall improves for semantic queries

### See Also
→ See: references/01-hybrid-search/
→ See: references/05-elasticsearch-hybrid/

---

## Cross-References

All playbooks reference:
- Full observability setup: Implement metrics tracking before and after migration
- Rollback procedures: Always maintain the ability to revert changes
- Testing protocols: Validate each stage with both quantitative and manual evaluation

For questions on specific components (models, tools, infrastructure), refer to related playbooks noted in each "See Also" section.

