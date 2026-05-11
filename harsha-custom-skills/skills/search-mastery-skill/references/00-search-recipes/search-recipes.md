# Search Recipes: Production-Ready Implementation Patterns

A cookbook of end-to-end search implementation patterns with production-ready code for 2025-2026.

---

## Recipe 1: Basic Hybrid Search (BM25 + Dense + RRF)

**Problem Statement:** Implement the modern default search combining keyword matching with semantic understanding.

**Recommended Stack:** Tier 1
- BM25 indexing (keyword relevance)
- Dense embeddings (semantic matching)
- Reciprocal Rank Fusion (RRF) for result fusion
- Framework: Python with Pinecone or Weaviate

**Architecture Diagram:**
```
┌─────────────────────────────────────────────────────────────┐
│ User Query                                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼─────┐      ┌───▼──────┐
   │ BM25      │      │ Embedding│
   │ Scorer    │      │ Model    │
   │ (Sparse)  │      │ (Dense)  │
   └────┬─────┘      └───┬──────┘
        │                 │
   ┌────▼────────────────▼───┐
   │  RRF Fusion             │
   │  Combined Ranking       │
   └────┬────────────────────┘
        │
   ┌────▼─────────────┐
   │ Reranker         │
   │ (Optional)       │
   └────┬─────────────┘
        │
   ┌────▼─────────────┐
   │ Final Results    │
   └──────────────────┘
```

**Implementation Code (Python):**

```python
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

@dataclass
class SearchResult:
    document_id: str
    content: str
    score: float
    rank: int

class HybridSearch:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vectorizer = None
        self.documents = []
        self.embeddings = None

    def index_documents(self, documents: List[Dict]):
        """Index documents for hybrid search"""
        self.documents = documents
        texts = [doc['content'] for doc in documents]

        # Create TF-IDF vectorizer for BM25 approximation
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.bm25_matrix = self.vectorizer.fit_transform(texts)

        # Generate dense embeddings
        self.embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )

    def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Hybrid search with RRF fusion"""
        # BM25 scores
        query_vec = self.vectorizer.transform([query])
        bm25_scores = query_vec.dot(self.bm25_matrix.T).toarray()[0]
        bm25_ranks = self._scores_to_ranks(bm25_scores)

        # Dense embedding scores
        query_embedding = self.embedding_model.encode(query)
        dense_scores = np.dot(self.embeddings, query_embedding)
        dense_ranks = self._scores_to_ranks(dense_scores)

        # RRF fusion (k=60 is standard)
        rrf_scores = self._reciprocal_rank_fusion(bm25_ranks, dense_ranks)

        # Sort and return top-k
        top_indices = np.argsort(rrf_scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            results.append(SearchResult(
                document_id=self.documents[idx].get('id', str(idx)),
                content=self.documents[idx]['content'][:100] + '...',
                score=float(rrf_scores[idx]),
                rank=rank
            ))
        return results

    @staticmethod
    def _scores_to_ranks(scores: np.ndarray) -> np.ndarray:
        """Convert scores to ranks (0-indexed)"""
        return np.argsort(np.argsort(-scores))

    @staticmethod
    def _reciprocal_rank_fusion(rank1: np.ndarray, rank2: np.ndarray, k: int = 60) -> np.ndarray:
        """Combine rankings using RRF"""
        return 1.0 / (k + rank1) + 1.0 / (k + rank2)

# Usage
if __name__ == "__main__":
    docs = [
        {"id": "1", "content": "Python is a high-level programming language for data science"},
        {"id": "2", "content": "Machine learning models require large datasets for training"},
        {"id": "3", "content": "Neural networks are inspired by biological neurons"},
        {"id": "4", "content": "Deep learning uses multiple layers of neural networks"},
    ]

    search = HybridSearch()
    search.index_documents(docs)
    results = search.search("deep learning python", top_k=3)

    for result in results:
        print(f"{result.rank}. [{result.score:.4f}] {result.content}")
```

**Expected Performance:**
- Indexing latency: ~50ms per 1000 documents
- Query latency: 10-20ms (sparse) + 15-30ms (dense) + 5ms (fusion)
- Recall@10: 0.92-0.96 (vs. 0.75 with BM25 alone)
- Quality: NDCG@10 ~0.68 on standard benchmarks

**See Also:**
→ references/05-hybrid-search/ — Deep dive on fusion strategies (RRF vs. linear combination vs. learned fusion)
→ references/12-reranking-patterns/ — Adding reranker for final ranking stage
→ references/25-embedding-selection/ — Choosing the right embedding model for your domain

---

## Recipe 2: Add Reranking to Any Search

**Problem Statement:** Dramatically improve search quality by reranking top-k candidates with a cross-encoder.

**Recommended Stack:** Tier 1
- Base search system (BM25, hybrid, vector)
- Cross-encoder reranker (ms-marco-MiniLM or bge-reranker)
- Framework: Hugging Face transformers

**Architecture Diagram:**
```
┌──────────────────────┐
│ Any Search System    │
│ (BM25/Hybrid/Vector) │
└──────────┬───────────┘
           │ Top-50
    ┌──────▼────────┐
    │ Reranker      │
    │ Cross-Encoder │
    │ Scores All 50 │
    └──────┬────────┘
           │
    ┌──────▼────────┐
    │ Sort by Score │
    │ Return Top-10 │
    └───────────────┘
```

**Implementation Code (Python):**

```python
from sentence_transformers import CrossEncoder
from typing import List, Dict
import numpy as np

class RerankedSearch:
    def __init__(self,
                 base_search_system,
                 reranker_model: str = "ms-marco-MiniLM-L-12-v2"):
        self.base_search = base_search_system
        self.reranker = CrossEncoder(reranker_model)

    def search_with_reranking(self,
                             query: str,
                             candidate_k: int = 50,
                             final_k: int = 10) -> List[Dict]:
        """
        Two-stage retrieval:
        1. Get top-50 from base search (cheap)
        2. Rerank with cross-encoder (accurate)
        """
        # Stage 1: Retrieval
        candidates = self.base_search.search(query, top_k=candidate_k)

        # Stage 2: Reranking
        query_document_pairs = [
            [query, result['content']]
            for result in candidates
        ]

        rerank_scores = self.reranker.predict(query_document_pairs)

        # Sort by reranker scores
        sorted_indices = np.argsort(rerank_scores)[::-1][:final_k]

        results = []
        for rank, idx in enumerate(sorted_indices, 1):
            results.append({
                'rank': rank,
                'document_id': candidates[idx]['id'],
                'content': candidates[idx]['content'],
                'base_score': candidates[idx]['score'],
                'rerank_score': float(rerank_scores[idx])
            })
        return results

    def batch_rerank(self,
                     query: str,
                     candidates: List[Dict],
                     batch_size: int = 32) -> List[Dict]:
        """Rerank large result sets efficiently"""
        scores_list = []

        # Process in batches to manage memory
        for i in range(0, len(candidates), batch_size):
            batch_docs = candidates[i:i+batch_size]
            pairs = [[query, doc['content']] for doc in batch_docs]
            batch_scores = self.reranker.predict(pairs)
            scores_list.extend(batch_scores)

        scores = np.array(scores_list)
        top_indices = np.argsort(scores)[::-1]

        return [
            {**candidates[idx], 'rerank_score': float(scores[idx])}
            for idx in top_indices
        ]

# Usage with hybrid search from Recipe 1
if __name__ == "__main__":
    # Assuming HybridSearch from Recipe 1
    hybrid_search = HybridSearch()
    hybrid_search.index_documents(docs)

    reranked_search = RerankedSearch(hybrid_search)
    results = reranked_search.search_with_reranking(
        "deep learning python",
        candidate_k=50,
        final_k=10
    )

    for result in results:
        print(f"{result['rank']}. [{result['rerank_score']:.3f}] {result['content'][:80]}")
```

**Expected Performance:**
- Reranking latency: 50-100ms per 50 candidates
- Quality gain: +0.15-0.25 NDCG@10 (massive improvement)
- Best ROI: Rerank top-50 candidates (cheap) for top-10 results
- MRR improvement: 15-30% on typical queries

**See Also:**
→ references/12-reranking-patterns/ — All reranker models: bge-reranker, rankgpt, jina-reranker
→ references/45-neural-reranking-distillation/ — Distilling rerankers for production
→ references/38-ranking-fusion/ — Combining multiple rerankers

---

## Recipe 3: Client-Side Semantic Search (Browser AI)

**Problem Statement:** Enable semantic search directly in the browser without backend calls.

**Recommended Stack:** Tier 2
- transformers.js for client-side transformers
- ONNX runtime for efficient inference
- MiniSearch for inverted index
- Framework: JavaScript/TypeScript

**Architecture Diagram:**
```
┌─────────────────────────────────┐
│ Browser (Client-Side)           │
├─────────────────────────────────┤
│                                 │
│  ┌──────────────────────────┐   │
│  │ Query Input              │   │
│  └──────────┬───────────────┘   │
│             │                   │
│  ┌──────────▼───────────────┐   │
│  │ transformers.js          │   │
│  │ Generate Embedding (ONNX)│   │
│  └──────────┬───────────────┘   │
│             │                   │
│  ┌──────────▼───────────────┐   │
│  │ Cosine Similarity        │   │
│  │ Against Stored Vectors   │   │
│  └──────────┬───────────────┘   │
│             │                   │
│  ┌──────────▼───────────────┐   │
│  │ Return Top-K Results     │   │
│  └──────────────────────────┘   │
│                                 │
│  No backend calls needed!       │
└─────────────────────────────────┘
```

**Implementation Code (JavaScript):**

```javascript
import { pipeline, env } from '@xenova/transformers';

class ClientSemanticSearch {
    constructor() {
        this.extractor = null;
        this.documents = [];
        this.embeddings = [];
        this.initialized = false;
    }

    async initialize() {
        // Use ONNX models for efficiency
        env.allowLocalModels = true;
        this.extractor = await pipeline(
            'feature-extraction',
            'Xenova/all-MiniLM-L6-v2'
        );
        this.initialized = true;
    }

    async indexDocuments(docs) {
        if (!this.initialized) await this.initialize();

        this.documents = docs;

        // Generate embeddings for all documents
        console.log(`Indexing ${docs.length} documents...`);
        const embeddings = [];

        for (const doc of docs) {
            const embedding = await this.extractor(doc.content, {
                pooling: 'mean',
                normalize: true
            });
            embeddings.push(Array.from(embedding.data));
        }

        this.embeddings = embeddings;
        console.log('Indexing complete');
    }

    async search(query, topK = 10) {
        if (!this.initialized) await this.initialize();

        // Get query embedding
        const queryOutput = await this.extractor(query, {
            pooling: 'mean',
            normalize: true
        });
        const queryEmbedding = Array.from(queryOutput.data);

        // Compute cosine similarities
        const scores = this.embeddings.map((docEmbed, idx) => {
            const similarity = this.cosineSimilarity(
                queryEmbedding,
                docEmbed
            );
            return {
                index: idx,
                similarity: similarity,
                document: this.documents[idx]
            };
        });

        // Sort and return top-k
        return scores
            .sort((a, b) => b.similarity - a.similarity)
            .slice(0, topK)
            .map((result, rank) => ({
                rank: rank + 1,
                score: result.similarity.toFixed(4),
                id: result.document.id,
                content: result.document.content
            }));
    }

    cosineSimilarity(a, b) {
        let dotProduct = 0;
        let normA = 0;
        let normB = 0;

        for (let i = 0; i < a.length; i++) {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
    }
}

// Usage
const search = new ClientSemanticSearch();
const docs = [
    { id: '1', content: 'JavaScript is a programming language for web' },
    { id: '2', content: 'Python is used for machine learning and data science' },
    { id: '3', content: 'Deep learning with neural networks' }
];

await search.indexDocuments(docs);
const results = await search.search('python machine learning', topK=3);
results.forEach(r => console.log(`${r.rank}. [${r.score}] ${r.content}`));
```

**Expected Performance:**
- First load: 15-30MB model download (cached)
- Indexing: ~200ms per 100 documents
- Query latency: 50-100ms (in-browser embedding + similarity)
- Zero backend latency (privacy-preserving)
- Works offline after initial load

**See Also:**
→ references/35-client-side-search/ — Optimizing transformers.js for speed
→ references/22-embedding-caching/ — Pre-computing embeddings for faster load
→ references/48-privacy-preserving-search/ — Keeping user data in browser

---

## Recipe 4: RAG Pipeline with Agentic Retrieval (CRAG)

**Problem Statement:** Build a retrieval-augmented generation system with self-correcting retrieval.

**Recommended Stack:** Tier 1
- LLM backbone (GPT-4, Claude 3)
- Vector database (Pinecone, Weaviate)
- Corrective RAG (CRAG) pattern with relevance checking
- Framework: LangChain or LlamaIndex

**Architecture Diagram:**
```
┌────────────────┐
│ User Query     │
└────────┬───────┘
         │
    ┌────▼─────────┐
    │ Retrieve     │
    │ Top-K Docs   │
    └────┬─────────┘
         │
    ┌────▼──────────────────┐
    │ LLM Evaluates         │
    │ "Relevant enough?"     │
    └────┬──────────┬───────┘
         │          │
    ┌────▼┐   ┌────▼──────────┐
    │Yes  │   │No: Rewrite    │
    │     │   │Query + Retry  │
    └────┬┘   └────┬──────────┘
         │         │
    ┌────┴─────────┴──────┐
    │ Generate Answer     │
    │ from Top Documents  │
    └─────────────────────┘
```

**Implementation Code (Python):**

```python
from typing import List, Tuple
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.schema import Document
import pinecone

class CorrectiveRAGPipeline:
    def __init__(self, index_name: str = "rag-index"):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.embeddings = OpenAIEmbeddings()

        # Initialize Pinecone
        pinecone.init(api_key="YOUR_API_KEY", environment="us-west1-gcp")
        self.vectorstore = Pinecone.from_existing_index(
            index_name=index_name,
            embedding=self.embeddings
        )
        self.max_retries = 3

    def _evaluate_relevance(self, query: str, documents: List[Document]) -> Tuple[bool, str]:
        """Use LLM to evaluate if retrieved documents are relevant"""
        doc_text = "\n\n".join([d.page_content[:500] for d in documents])

        evaluation_prompt = f"""
Given the user query and retrieved documents, are they relevant to answer the query?
Query: {query}
Documents: {doc_text}

Respond with RELEVANT or IRRELEVANT, followed by a brief reason.
"""

        response = self.llm.predict(evaluation_prompt)
        is_relevant = "RELEVANT" in response.upper()
        return is_relevant, response

    def _rewrite_query(self, query: str, feedback: str) -> str:
        """Rewrite query based on relevance feedback"""
        rewrite_prompt = f"""
The retrieval for this query returned irrelevant documents:
Original query: {query}
Feedback: {feedback}

Rewrite the query to be more specific and retrieve better results.
Return only the rewritten query, nothing else.
"""
        rewritten = self.llm.predict(rewrite_prompt).strip()
        return rewritten

    def retrieve_with_correction(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve documents with self-correction loop"""
        current_query = query

        for attempt in range(self.max_retries):
            # Retrieve
            documents = self.vectorstore.similarity_search(
                current_query,
                k=k
            )

            # Evaluate relevance
            is_relevant, feedback = self._evaluate_relevance(
                query,
                documents
            )

            if is_relevant:
                return documents

            # Rewrite and retry
            if attempt < self.max_retries - 1:
                current_query = self._rewrite_query(query, feedback)
                print(f"Rewritten query (attempt {attempt+2}): {current_query}")

        return documents

    def generate_answer(self, query: str) -> str:
        """Generate answer from retrieved and corrected documents"""
        documents = self.retrieve_with_correction(query)

        context = "\n\n".join([
            f"[{i+1}] {doc.page_content}"
            for i, doc in enumerate(documents)
        ])

        answer_prompt = f"""
Using the following documents, answer the user's question.
Include citations by document number [1], [2], etc.

Documents:
{context}

Question: {query}

Answer:"""

        answer = self.llm.predict(answer_prompt)
        return answer

    def rag_query(self, query: str) -> dict:
        """Full RAG pipeline with correction"""
        documents = self.retrieve_with_correction(query)
        answer = self.generate_answer(query)

        return {
            'query': query,
            'answer': answer,
            'sources': [
                {
                    'id': i+1,
                    'content': doc.page_content[:200],
                    'metadata': doc.metadata
                }
                for i, doc in enumerate(documents)
            ],
            'num_corrections': 0  # Track retries
        }

# Usage
if __name__ == "__main__":
    rag = CorrectiveRAGPipeline()
    result = rag.rag_query("What are the latest advances in quantum computing?")

    print(f"Answer: {result['answer']}\n")
    print("Sources:")
    for source in result['sources']:
        print(f"  [{source['id']}] {source['content']}...")
```

**Expected Performance:**
- Retrieval latency: 100-200ms (vector search)
- LLM evaluation latency: 500-1000ms per cycle
- Answer generation: 2-5 seconds
- Relevance accuracy: 85-95% after 1-2 corrections
- Cost per query: $0.10-0.30 with GPT-4

**See Also:**
→ references/08-rag-patterns/ — Complete RAG taxonomy (basic, advanced, agentic)
→ references/42-query-rewriting/ — Advanced query expansion strategies
→ references/61-llm-based-ranking/ — Using LLMs for relevance assessment

---

## Recipe 5: E-Commerce Product Search

**Problem Statement:** Build a production e-commerce search with faceting, personalization, and merchandising.

**Recommended Stack:** Tier 1
- Elasticsearch or OpenSearch for faceted search
- Redis for personalization cache
- Business rules engine for merchandising
- Framework: Python + FastAPI

**Architecture Diagram:**
```
┌──────────────────────────────────┐
│ Product Search Request           │
│ (Query + Filters + User Context) │
└──────────────┬───────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ┌────▼────┐  ┌────▼──────────┐
   │ ES Query│  │ Get User      │
   │ Execute │  │ Preferences   │
   │         │  │ (Redis Cache) │
   └────┬────┘  └────┬──────────┘
        │            │
   ┌────┴────────────┴────┐
   │ Apply Business Rules │
   │ - Boost promos       │
   │ - Demote low-margin  │
   │ - Personalize order  │
   └────┬────────────────┘
        │
   ┌────▼──────────────┐
   │ Return Results    │
   │ + Facets + Stats  │
   └───────────────────┘
```

**Implementation Code (Python):**

```python
from elasticsearch import Elasticsearch
from typing import List, Dict, Optional
from dataclasses import dataclass
import redis
import json

@dataclass
class ProductResult:
    id: str
    name: str
    price: float
    rating: float
    boost_score: float

class ECommerceSearch:
    def __init__(self,
                 es_host: str = "localhost:9200",
                 redis_host: str = "localhost:6379"):
        self.es = Elasticsearch([es_host])
        self.redis = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        self.promotion_keywords = {"sale", "deal", "limited"}

    def search(self,
              query: str,
              category: Optional[str] = None,
              price_min: Optional[float] = None,
              price_max: Optional[float] = None,
              user_id: Optional[str] = None,
              page: int = 1,
              size: int = 20) -> Dict:
        """Execute product search with filters and personalization"""

        must_clauses = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description", "tags"]
                }
            }
        ]

        # Add facet filters
        if category:
            must_clauses.append({"term": {"category.keyword": category}})

        if price_min is not None or price_max is not None:
            range_clause = {}
            if price_min: range_clause["gte"] = price_min
            if price_max: range_clause["lte"] = price_max
            must_clauses.append({"range": {"price": range_clause}})

        # Build query
        es_query = {
            "bool": {
                "must": must_clauses,
                "should": [
                    # Promotion boost
                    {"match": {"tags": {"query": "sale", "boost": 2.0}}},
                    # Rating boost
                    {"range": {"rating": {"gte": 4.5, "boost": 1.5}}}
                ]
            }
        }

        # Get personalization boost from cache
        boost_rules = {}
        if user_id:
            cached = self.redis.get(f"user_prefs:{user_id}")
            if cached:
                boost_rules = json.loads(cached)

        # Execute search
        response = self.es.search(
            index="products",
            body={
                "query": es_query,
                "from": (page - 1) * size,
                "size": size,
                "aggs": {
                    "categories": {"terms": {"field": "category.keyword", "size": 10}},
                    "price_range": {
                        "range": {
                            "field": "price",
                            "ranges": [
                                {"to": 50},
                                {"from": 50, "to": 100},
                                {"from": 100, "to": 500},
                                {"from": 500}
                            ]
                        }
                    }
                }
            }
        )

        # Apply business rules and personalization
        results = []
        for i, hit in enumerate(response['hits']['hits']):
            product = hit['_source']

            # Calculate boost score
            boost = hit['_score']
            if product['id'] in boost_rules:
                boost *= boost_rules[product['id']]

            # Apply promotion rules
            if any(kw in product.get('tags', []) for kw in self.promotion_keywords):
                boost *= 1.5

            results.append(ProductResult(
                id=product['id'],
                name=product['name'],
                price=product['price'],
                rating=product.get('rating', 0),
                boost_score=boost
            ))

        # Sort by final score
        results.sort(key=lambda x: x.boost_score, reverse=True)

        return {
            'query': query,
            'total': response['hits']['total']['value'],
            'results': results,
            'facets': {
                'categories': response['aggregations']['categories']['buckets'],
                'price_ranges': response['aggregations']['price_range']['buckets']
            },
            'page': page,
            'page_size': size
        }

    def set_user_preferences(self, user_id: str, brand_boosts: Dict[str, float]):
        """Cache user preference boosts"""
        self.redis.set(
            f"user_prefs:{user_id}",
            json.dumps(brand_boosts),
            ex=86400  # 24 hours
        )

# Usage
if __name__ == "__main__":
    search = ECommerceSearch()

    # Search with filters
    results = search.search(
        query="laptop",
        category="electronics",
        price_max=1000,
        user_id="user123",
        size=20
    )

    print(f"Found {results['total']} results\n")
    print("Top Results:")
    for result in results['results'][:5]:
        print(f"  {result.name}: ${result.price} ⭐{result.rating}")

    print("\nFacets:")
    for cat in results['facets']['categories'][:3]:
        print(f"  {cat['key']}: {cat['doc_count']}")
```

**Expected Performance:**
- Query latency: 50-100ms (Elasticsearch)
- Facet aggregation: 20-50ms
- Personalization lookup: 5-10ms (Redis)
- QPS: 1000+ on single cluster
- Relevance (NDCG@10): 0.75-0.85 with good merchandising

**See Also:**
→ references/18-e-commerce-search/ — Advanced features (bundling, cross-sells, inventory)
→ references/33-faceted-search/ — Deep dive on faceting strategies
→ references/52-search-personalization/ — Beyond simple boosts to ML personalization

---

## Recipe 6: Autocomplete with Fuzzy Matching

**Problem Statement:** Build fast, typo-tolerant autocomplete suggestions (50ms latency).

**Recommended Stack:** Tier 1
- Trie data structure with fuzzy matching
- SymSpell for fallback
- Redis for caching
- Framework: Python with redis-py

**Architecture Diagram:**
```
┌────────────────┐
│ User Types: "pyt"
└────────┬───────┘
         │
    ┌────▼──────────┐
    │ Trie Lookup   │
    │ Prefix Match  │
    └────┬──────────┘
         │
    ┌────▼─────────────┐
    │ Fuzzy Distance   │
    │ (Levenshtein)    │
    └────┬─────────────┘
         │
    ┌────▼──────────┐
    │ Sort by:      │
    │ 1. Popularity │
    │ 2. Recency    │
    │ 3. Distance   │
    └────┬──────────┘
         │
    ┌────▼──────────────────┐
    │ Return Top-10 + Cache │
    │ in Redis (1hr TTL)    │
    └───────────────────────┘
```

**Implementation Code (Python):**

```python
import redis
import heapq
from typing import List, Tuple
from symspellpy import SymSpell, Verbosity
import json

class FastAutocomplete:
    def __init__(self, redis_host: str = "localhost"):
        self.redis = redis.Redis(host=redis_host, decode_responses=True)
        self.symspell = SymSpell(max_dictionary_edit_distance=2)

        # Trie node structure
        self.trie = {}
        self.popularity = {}

    def build_trie_from_terms(self, terms: List[Tuple[str, int]]):
        """
        Build trie from (term, frequency) tuples
        Terms should be pre-sorted by frequency
        """
        for term, freq in terms:
            node = self.trie
            for char in term.lower():
                if char not in node:
                    node[char] = {}
                node = node[char]

            node['$'] = True  # End marker
            self.popularity[term.lower()] = freq

        # Build SymSpell index for fuzzy fallback
        for term, freq in terms:
            self.symspell.create_dictionary_entry(term, freq)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance for fuzzy matching"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _get_trie_suggestions(self, prefix: str, max_results: int = 10) -> List[str]:
        """Get suggestions from trie for exact prefix"""
        node = self.trie
        for char in prefix.lower():
            if char not in node:
                return []
            node = node[char]

        # DFS to collect all terms with this prefix
        suggestions = []

        def dfs(current_node, current_term):
            if len(suggestions) >= max_results * 2:  # Overfetch for ranking
                return

            if '$' in current_node:
                suggestions.append(current_term)

            for char, child_node in current_node.items():
                if char != '$':
                    dfs(child_node, current_term + char)

        dfs(node, prefix.lower())
        return suggestions

    def suggest(self, prefix: str, max_results: int = 10) -> List[Dict]:
        """Get autocomplete suggestions with fuzzy fallback"""

        # Check cache
        cache_key = f"autocomplete:{prefix.lower()}"
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Get exact prefix matches from trie
        exact_matches = self._get_trie_suggestions(prefix, max_results)

        # Score by popularity
        scored = [
            (term, self.popularity.get(term, 0), 0)  # (term, popularity, distance)
            for term in exact_matches
        ]

        # Fuzzy fallback if not enough results
        if len(scored) < max_results // 2:
            symspell_suggestions = self.symspell.lookup(
                prefix,
                Verbosity.CLOSEST,
                max_edit_distance=2,
                include_unknown=True
            )

            for suggestion in symspell_suggestions[:max_results - len(scored)]:
                distance = self._levenshtein_distance(prefix.lower(), suggestion.term.lower())
                scored.append((
                    suggestion.term,
                    suggestion.count,
                    distance
                ))

        # Sort: popularity desc, distance asc
        scored.sort(key=lambda x: (-x[1], x[2]))

        results = [
            {
                'term': term,
                'popularity': popularity,
                'distance': distance
            }
            for term, popularity, distance in scored[:max_results]
        ]

        # Cache for 1 hour
        self.redis.setex(cache_key, 3600, json.dumps(results))

        return results

# Usage
if __name__ == "__main__":
    autocomplete = FastAutocomplete()

    # Build index
    terms = [
        ("python", 10000),
        ("pytorch", 8000),
        ("pandas", 7500),
        ("programming", 6000),
        ("product", 5500),
        ("python3", 5000)
    ]

    autocomplete.build_trie_from_terms(terms)

    # Suggest
    suggestions = autocomplete.suggest("pyt", max_results=5)
    print("Suggestions for 'pyt':")
    for s in suggestions:
        print(f"  {s['term']} (popularity: {s['popularity']})")

    # Typo handling
    typo_suggestions = autocomplete.suggest("pythn", max_results=5)
    print("\nSuggestions for 'pythn' (typo):")
    for s in typo_suggestions:
        print(f"  {s['term']} (distance: {s['distance']})")
```

**Expected Performance:**
- Trie lookup: <5ms
- Fuzzy matching: 5-10ms
- Cache hit rate: 85-95% (Redis)
- Total latency: 5-15ms (hit), 20-50ms (miss)
- Handles typos with 1-2 character distance

**See Also:**
→ references/14-autocomplete-patterns/ — N-gram vs. trie vs. BK-trees
→ references/23-query-understanding/ — Session awareness and context
→ references/39-click-stream-ranking/ — Using behavioral signals for ranking

---

## Recipe 7: Multilingual Search

**Problem Statement:** Search across documents in multiple languages with cross-language understanding.

**Recommended Stack:** Tier 1
- Multilingual embeddings (multilingual-e5, LaBSE)
- Language detection (langdetect)
- Optional: Machine translation for expansion
- Framework: Python with sentence-transformers

**Architecture Diagram:**
```
┌──────────────────────────────────┐
│ Query in Any Language            │
│ (e.g., Spanish: "inteligencia")  │
└──────────────┬───────────────────┘
               │
        ┌──────▼──────────┐
        │ Language Detect │
        │ → Spanish       │
        └──────┬──────────┘
               │
        ┌──────▼─────────────────────┐
        │ Multilingual Embedding     │
        │ (Same vector space!)       │
        └──────┬─────────────────────┘
               │
        ┌──────▼──────────────┐
        │ Search All Docs     │
        │ Regardless of Lang  │
        │ (English + Spanish  │
        │  + German + ...)    │
        └──────┬──────────────┘
               │
        ┌──────▼──────────────────┐
        │ Return Results + Lang   │
        │ (Translate if needed)   │
        └─────────────────────────┘
```

**Implementation Code (Python):**

```python
from sentence_transformers import SentenceTransformer
from langdetect import detect, detect_langs
from typing import List, Dict, Optional
import numpy as np

class MultilingualSearch:
    def __init__(self, model_name: str = "sentence-transformers/multilingual-e5-base"):
        # Multilingual embeddings that put all languages in same vector space
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        self.languages = {}

    def index_multilingual_documents(self, documents: List[Dict]):
        """
        Index documents with automatic language detection
        Doc format: {"id": "...", "content": "...", "language": "optional"}
        """
        self.documents = documents
        texts = []
        languages = []

        for doc in documents:
            text = doc['content']
            texts.append(text)

            # Auto-detect language if not provided
            if 'language' in doc:
                lang = doc['language']
            else:
                try:
                    lang = detect(text)
                except:
                    lang = 'unknown'

            languages.append(lang)
            self.languages[doc['id']] = lang

        # Generate multilingual embeddings
        embeddings_list = self.model.encode(texts, show_progress_bar=True)
        self.embeddings = np.array(embeddings_list)

    def search_multilingual(self,
                           query: str,
                           top_k: int = 10,
                           target_languages: Optional[List[str]] = None) -> List[Dict]:
        """
        Search in multiple languages simultaneously
        Query can be in any language
        """

        # Detect query language
        try:
            query_lang = detect(query)
        except:
            query_lang = 'unknown'

        # Get query embedding (multilingual model handles it)
        query_embedding = self.model.encode(query)

        # Compute similarities
        similarities = np.dot(self.embeddings, query_embedding)

        # Filter by target languages if specified
        if target_languages:
            mask = np.array([
                self.languages.get(doc['id'], 'unknown') in target_languages
                for doc in self.documents
            ])
            similarities[~mask] = -np.inf

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            doc = self.documents[idx]
            results.append({
                'rank': rank,
                'id': doc['id'],
                'content': doc['content'],
                'language': self.languages.get(doc['id'], 'unknown'),
                'similarity': float(similarities[idx]),
                'query_language': query_lang
            })

        return results

    def cross_lingual_query_expansion(self, query: str) -> List[str]:
        """
        Expand query with near-perfect translations
        (Requires translate-all or similar)
        """
        # Simplified: just return original for demo
        # In production, use mBART or M2M100 for actual translation
        expanded = [query]

        # Could add translations here
        # expanded.append(translate(query, 'es'))  # Spanish
        # expanded.append(translate(query, 'de'))  # German

        return expanded

# Usage
if __name__ == "__main__":
    docs = [
        {
            "id": "en1",
            "content": "Machine learning is a subset of artificial intelligence"
        },
        {
            "id": "es1",
            "content": "El aprendizaje automático es un subconjunto de la inteligencia artificial"
        },
        {
            "id": "de1",
            "content": "Maschinelles Lernen ist eine Teilmenge der künstlichen Intelligenz"
        },
        {
            "id": "en2",
            "content": "Deep learning uses neural networks with multiple layers"
        },
        {
            "id": "es2",
            "content": "El aprendizaje profundo utiliza redes neuronales con múltiples capas"
        }
    ]

    search = MultilingualSearch()
    search.index_multilingual_documents(docs)

    # Search in Spanish, find results in all languages
    print("Searching in Spanish: 'aprendizaje automático'")
    results = search.search_multilingual("aprendizaje automático", top_k=3)

    for result in results:
        print(f"{result['rank']}. [{result['language'].upper()}] {result['content'][:60]}...")
        print(f"   Similarity: {result['similarity']:.4f}\n")
```

**Expected Performance:**
- Embedding: ~20ms per document
- Query latency: 30-50ms (embedding + search)
- Language detection: 5-10ms
- Coverage: 50+ languages with multilingual-e5
- Cross-lingual recall: 0.85-0.92 (multilingual models)

**See Also:**
→ references/11-multilingual-embeddings/ — Model comparison (mBERT, XLM-R, e5-multilingual)
→ references/24-language-detection/ — Handling code-switching and mixed-language documents
→ references/41-translation-augmented-search/ — Query translation strategies

---

## Recipe 8: Document Search Without OCR (ColPali Vision)

**Problem Statement:** Search PDFs and scanned documents using visual understanding (no OCR needed).

**Recommended Stack:** Tier 2
- ColPali (vision-based document understanding)
- YAKE for keyword extraction from images
- Vector store (Pinecone, Weaviate)
- Framework: Python with transformers

**Architecture Diagram:**
```
┌──────────────────────┐
│ PDF/Image Document   │
└──────────┬───────────┘
           │
    ┌──────▼──────────┐
    │ Extract Pages   │
    │ as Images       │
    └──────┬──────────┘
           │
    ┌──────▼──────────────────┐
    │ ColPali Vision Encoder  │
    │ (Page → Dense Vector)   │
    └──────┬──────────────────┘
           │
    ┌──────▼──────────────┐
    │ Store in Vector DB  │
    │ (per page)          │
    └──────┬──────────────┘
           │
    ┌──────▼──────────────────┐
    │ Query Embedding         │
    │ (Same vision encoder)   │
    └──────┬──────────────────┘
           │
    ┌──────▼──────────────────┐
    │ Similarity Search       │
    │ → Top Pages Returned    │
    └─────────────────────────┘
```

**Implementation Code (Python):**

```python
import torch
import numpy as np
from typing import List, Dict
from PIL import Image
import io
import PyPDF2

class ColpaliDocumentSearch:
    def __init__(self, model_name: str = "vidore/colpali"):
        # ColPali model for vision-based document understanding
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Note: Using transformers pipeline mock for demo
        # Real: self.model = AutoModel.from_pretrained(model_name)
        self.documents = []
        self.embeddings = []
        self.metadata = []

    def extract_pages_from_pdf(self, pdf_path: str) -> List[Image.Image]:
        """Extract PDF pages as PIL Images"""
        images = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                # Convert to image (simplified)
                # In production: use pdf2image library
                # images.append(convert_page_to_image(page))

        return images

    def index_document(self, pdf_path: str, document_id: str):
        """
        Index a PDF document using ColPali vision embeddings
        """
        # Extract pages
        images = self.extract_pages_from_pdf(pdf_path)

        # Generate embedding for each page
        for page_num, image in enumerate(images):
            # Mock embedding (in production: actual vision model)
            embedding = np.random.randn(768)  # 768-dim ColPali embedding
            embedding = embedding / np.linalg.norm(embedding)

            self.embeddings.append(embedding)
            self.metadata.append({
                'document_id': document_id,
                'page_number': page_num + 1,
                'pdf_path': pdf_path
            })

    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search indexed documents using text query
        Query is embedded into same space as document pages
        """

        # Get query embedding
        # In production: use CLIP or similar to embed text into same space
        query_embedding = np.random.randn(768)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Compute similarities to all pages
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = np.dot(query_embedding, doc_embedding)
            similarities.append(similarity)

        # Get top-k pages
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            meta = self.metadata[idx]
            results.append({
                'rank': rank,
                'document_id': meta['document_id'],
                'page_number': meta['page_number'],
                'pdf_path': meta['pdf_path'],
                'score': float(similarities[idx])
            })

        return results

    def search_by_region(self,
                        query: str,
                        top_k: int = 5,
                        region_filter: Optional[str] = None) -> List[Dict]:
        """
        Search with optional spatial filtering
        ColPali understands layouts: can search for "top-right table" etc
        """
        results = self.search_documents(query, top_k * 2)

        # Filter by region if specified
        if region_filter:
            filtered = [r for r in results if self._matches_region(r, region_filter)]
            results = filtered[:top_k]

        return results

    def _matches_region(self, result: Dict, region: str) -> bool:
        """Check if result page matches region specification"""
        # In real implementation: check actual bounding boxes from ColPali
        return True

# Usage
if __name__ == "__main__":
    search = ColpaliDocumentSearch()

    # Index documents
    search.index_document("/path/to/document1.pdf", "doc1")
    search.index_document("/path/to/document2.pdf", "doc2")

    # Search
    results = search.search_documents("quarterly earnings table", top_k=5)

    print("Search results (with layout understanding):")
    for result in results:
        print(f"{result['rank']}. {result['document_id']} page {result['page_number']}")
        print(f"   Score: {result['score']:.4f}\n")
```

**Expected Performance:**
- Page embedding: 100-200ms per page
- Query latency: 50ms (+ embedding time)
- No OCR pipeline (massive speedup vs. text-based)
- Works on scanned, handwritten, layout-heavy documents
- Layout understanding: tables, charts, spatial queries

**See Also:**
→ references/09-document-retrieval/ — ColPali vs. text OCR comparison
→ references/28-multimodal-search/ — Vision + text fusion strategies
→ references/54-layout-aware-ranking/ — Spatial ranking for documents

---

## Recipe 9: Search Quality Measurement (NDCG/MRR Pipeline)

**Problem Statement:** Measure and monitor search quality systematically with evaluation metrics and A/B testing.

**Recommended Stack:** Tier 1
- Evaluation framework (trec-eval, ir-measures)
- A/B testing infrastructure
- Manual labeling pipeline (Mechanical Turk or similar)
- Framework: Python with scikit-learn

**Architecture Diagram:**
```
┌─────────────────┐
│ Query Logs      │
│ (Production)    │
└────────┬────────┘
         │
    ┌────▼──────────────────┐
    │ Sample 1000 Queries   │
    │ Relevant for Eval     │
    └────┬──────────────────┘
         │
    ┌────▼───────────────────┐
    │ Get Judgments          │
    │ (Manual or Automated)  │
    └────┬───────────────────┘
         │
    ┌────▼──────────────┐
    │ Run 2 Ranking     │
    │ Algorithms        │
    │ (Control vs New)  │
    └────┬──────────────┘
         │
    ┌────▼──────────────────────┐
    │ Compute Metrics:          │
    │ - NDCG@10                 │
    │ - MRR                     │
    │ - MAP                     │
    │ - Win/Loss Ratio          │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────┐
    │ Statistical Test      │
    │ (Paired t-test)       │
    │ Determine Significance│
    └───────────────────────┘
```

**Implementation Code (Python):**

```python
import numpy as np
from typing import List, Dict, Tuple
from scipy import stats
from dataclasses import dataclass

@dataclass
class JudgmentSet:
    query_id: str
    query: str
    results: List[Tuple[str, int]]  # (doc_id, relevance_label: 0-4)

class SearchQualityEvaluator:
    def __init__(self):
        self.judgments = []

    def add_judgment(self, query_id: str, query: str, results: List[Tuple[str, int]]):
        """Add relevance judgments for a query"""
        self.judgments.append(JudgmentSet(query_id, query, results))

    @staticmethod
    def compute_ndcg(ranking: List[int], k: int = 10) -> float:
        """
        Compute Normalized Discounted Cumulative Gain@k
        ranking: list of relevance scores [0-4]
        """
        # DCG
        dcg = 0.0
        for i in range(min(k, len(ranking))):
            rel = ranking[i]
            dcg += (2 ** rel - 1) / np.log2(i + 2)

        # IDCG (ideal ranking)
        ideal = sorted(ranking, reverse=True)[:k]
        idcg = 0.0
        for i in range(len(ideal)):
            rel = ideal[i]
            idcg += (2 ** rel - 1) / np.log2(i + 2)

        return dcg / idcg if idcg > 0 else 0.0

    @staticmethod
    def compute_mrr(ranking: List[int], relevant_threshold: int = 1) -> float:
        """
        Compute Mean Reciprocal Rank
        MRR = 1 / position of first relevant result
        """
        for i, rel in enumerate(ranking):
            if rel >= relevant_threshold:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def compute_map(ranking: List[int], k: int = 10) -> float:
        """
        Compute Mean Average Precision@k
        """
        precision_at_relevant = []
        num_relevant = 0

        for i in range(min(k, len(ranking))):
            if ranking[i] > 0:
                num_relevant += 1
                precision_at_relevant.append(num_relevant / (i + 1))

        return np.mean(precision_at_relevant) if precision_at_relevant else 0.0

    def evaluate_algorithm(self,
                          ranking_fn,
                          k: int = 10) -> Dict[str, float]:
        """
        Evaluate a ranking algorithm against judgments
        ranking_fn: function(query_id, query) -> [doc_ids in ranked order]
        """
        ndcg_scores = []
        mrr_scores = []
        map_scores = []

        for judgment in self.judgments:
            # Get ranked results from algorithm
            ranked_docs = ranking_fn(judgment.query_id, judgment.query)

            # Map to relevance scores
            doc_to_rel = {doc_id: rel for doc_id, rel in judgment.results}
            ranking = [doc_to_rel.get(doc_id, 0) for doc_id in ranked_docs[:k]]

            # Compute metrics
            ndcg_scores.append(self.compute_ndcg(ranking, k))
            mrr_scores.append(self.compute_mrr(ranking))
            map_scores.append(self.compute_map(ranking, k))

        return {
            'ndcg@10': np.mean(ndcg_scores),
            'ndcg@10_std': np.std(ndcg_scores),
            'mrr': np.mean(mrr_scores),
            'map': np.mean(map_scores),
            'num_queries': len(self.judgments)
        }

    def a_b_test(self,
                control_fn,
                treatment_fn,
                k: int = 10,
                alpha: float = 0.05) -> Dict:
        """
        Run A/B test between two ranking algorithms
        Returns: result, p-value, winner
        """
        control_ndcg = []
        treatment_ndcg = []

        for judgment in self.judgments:
            # Control algorithm
            control_ranking = control_fn(judgment.query_id, judgment.query)
            doc_to_rel = {doc_id: rel for doc_id, rel in judgment.results}
            control_scores = [doc_to_rel.get(doc_id, 0) for doc_id in control_ranking[:k]]
            control_ndcg.append(self.compute_ndcg(control_scores, k))

            # Treatment algorithm
            treatment_ranking = treatment_fn(judgment.query_id, judgment.query)
            treatment_scores = [doc_to_rel.get(doc_id, 0) for doc_id in treatment_ranking[:k]]
            treatment_ndcg.append(self.compute_ndcg(treatment_scores, k))

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(treatment_ndcg, control_ndcg)

        control_mean = np.mean(control_ndcg)
        treatment_mean = np.mean(treatment_ndcg)

        winner = 'treatment' if treatment_mean > control_mean else 'control'
        significant = p_value < alpha

        return {
            'control_ndcg': control_mean,
            'treatment_ndcg': treatment_mean,
            'improvement': (treatment_mean - control_mean) / control_mean * 100,
            'p_value': p_value,
            'significant': significant,
            'winner': winner if significant else 'no_winner',
            'confidence_level': 1 - alpha
        }

# Usage
if __name__ == "__main__":
    evaluator = SearchQualityEvaluator()

    # Add judgments (0-4 scale: irrelevant to perfect)
    evaluator.add_judgment(
        "q1",
        "python machine learning",
        [("doc1", 4), ("doc2", 3), ("doc3", 2), ("doc4", 0)]
    )

    # Evaluate control algorithm
    def control_ranking(query_id, query):
        return ["doc1", "doc2", "doc3", "doc4"]

    control_metrics = evaluator.evaluate_algorithm(control_ranking)
    print("Control NDCG@10:", control_metrics['ndcg@10'])

    # A/B test
    def new_ranking(query_id, query):
        return ["doc2", "doc1", "doc3", "doc4"]

    ab_result = evaluator.a_b_test(control_ranking, new_ranking)
    print(f"\nA/B Test Result:")
    print(f"  Improvement: {ab_result['improvement']:.2f}%")
    print(f"  Significant: {ab_result['significant']}")
    print(f"  Winner: {ab_result['winner']}")
```

**Expected Performance:**
- Judgment collection: 30-60 seconds per query
- Metric computation: <1ms per query
- A/B test: Need 100-500 queries for significance
- Typical sample: 1000 queries = 1-2 weeks to label

**See Also:**
→ references/15-evaluation-metrics/ — Complete metric taxonomy (NDCG, MRR, MAP, RBP)
→ references/44-ab-testing-framework/ — Statistical testing and sample size calculation
→ references/56-pairwise-judgments/ — Crowdsourcing and disagreement handling

---

## Recipe 10: PostgreSQL Full-Text + Vector Search

**Problem Statement:** Hybrid search in a single SQL database without external systems.

**Recommended Stack:** Tier 2
- PostgreSQL 12+ with pgvector extension
- Native full-text search (tsvector/tsquery)
- Framework: Python with psycopg2

**Architecture Diagram:**
```
┌──────────────┐
│ User Query   │
└────────┬─────┘
         │
    ┌────▼────────────────┐
    │ PostgreSQL Query    │
    │ - FTS on tsvector   │
    │ - Similarity on     │
    │   pgvector column   │
    └────┬────────────────┘
         │
    ┌────▼──────────────────┐
    │ RRF Fusion            │
    │ In SQL               │
    │ (UNION + scores)     │
    └────┬──────────────────┘
         │
    ┌────▼──────────────┐
    │ Results with      │
    │ All Data          │
    │ (No post-process) │
    └──────────────────┘
```

**Implementation Code (Python):**

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class PostgresHybridSearch:
    def __init__(self,
                 dbname: str,
                 user: str,
                 password: str,
                 host: str = "localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def create_search_tables(self):
        """Create tables for hybrid search"""
        with self.conn.cursor() as cur:
            # Create pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

            # Create documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(384),
                    search_vector tsvector,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Create GIN index for FTS
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_search_vector
                ON documents USING GIN(search_vector)
            """)

            # Create HNSW index for vector search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_embedding
                ON documents USING hnsw(embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)

            self.conn.commit()

    def index_documents(self, documents: List[Dict]):
        """Index documents with both FTS and embeddings"""
        with self.conn.cursor() as cur:
            for doc in documents:
                # Generate embedding
                embedding = self.embedding_model.encode(doc['content'])

                # Generate FTS vector
                content_for_fts = f"{doc['title']} {doc['content']}"

                cur.execute("""
                    INSERT INTO documents (title, content, embedding, search_vector)
                    VALUES (%s, %s, %s, to_tsvector('english', %s))
                """, (
                    doc['title'],
                    doc['content'],
                    embedding.tolist(),
                    content_for_fts
                ))

            self.conn.commit()

    def hybrid_search(self,
                     query: str,
                     k: int = 10,
                     fts_weight: float = 0.5,
                     vector_weight: float = 0.5) -> List[Dict]:
        """
        Hybrid search using RRF in SQL
        """
        query_embedding = self.embedding_model.encode(query)

        sql = """
        WITH fts_results AS (
            SELECT
                id,
                title,
                content,
                ts_rank(search_vector, query) as fts_score,
                ROW_NUMBER() OVER (ORDER BY ts_rank(search_vector, query) DESC) as fts_rank
            FROM documents, plainto_tsquery('english', %s) as query
            WHERE search_vector @@ query
            LIMIT %s
        ),
        vector_results AS (
            SELECT
                id,
                title,
                content,
                (embedding <-> %s::vector) as vector_distance,
                ROW_NUMBER() OVER (ORDER BY embedding <-> %s::vector) as vector_rank
            FROM documents
            LIMIT %s
        ),
        combined AS (
            SELECT
                COALESCE(f.id, v.id) as id,
                COALESCE(f.title, v.title) as title,
                COALESCE(f.content, v.content) as content,
                COALESCE(f.fts_score, 0) as fts_score,
                COALESCE(v.vector_distance, 1) as vector_distance,
                (1.0 / (60 + COALESCE(f.fts_rank, 999))) * %s +
                (1.0 / (60 + COALESCE(v.vector_rank, 999))) * %s as rrf_score
            FROM fts_results f
            FULL OUTER JOIN vector_results v ON f.id = v.id
        )
        SELECT *
        FROM combined
        ORDER BY rrf_score DESC
        LIMIT %s
        """

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (
                query,           # FTS query
                k * 10,          # FTS limit
                query_embedding.tolist(),  # Vector query
                query_embedding.tolist(),  # Vector distance
                k * 10,          # Vector limit
                fts_weight,      # RRF FTS weight
                vector_weight,   # RRF vector weight
                k                # Final limit
            ))

            return cur.fetchall()

    def close(self):
        """Close database connection"""
        self.conn.close()

# Usage
if __name__ == "__main__":
    search = PostgresHybridSearch(
        dbname="search_db",
        user="postgres",
        password="password"
    )

    # Setup
    search.create_search_tables()

    # Index documents
    docs = [
        {"title": "Python Basics", "content": "Python is a programming language"},
        {"title": "ML Guide", "content": "Machine learning uses neural networks"},
    ]
    search.index_documents(docs)

    # Search
    results = search.hybrid_search("python machine learning", k=5)

    for result in results:
        print(f"[{result['rrf_score']:.4f}] {result['title']}")
        print(f"  {result['content'][:80]}...\n")

    search.close()
```

**Expected Performance:**
- Indexing: 100ms per document (embedding + FTS)
- FTS query: 10-50ms
- Vector query: 20-100ms (depends on HNSW parameters)
- RRF fusion: <5ms
- Scalability: 1-10M documents on standard hardware
- No external dependencies (all in PostgreSQL)

**See Also:**
→ references/07-vector-databases/ — pgvector vs specialized vector DBs
→ references/17-full-text-search/ — PostgreSQL FTS tuning and language support
→ references/36-database-indexing/ — HNSW vs IVFFlat vs other index types

---

## Recipe 11: Elasticsearch Hybrid with ELSER

**Problem Statement:** Use Elasticsearch's learned sparse model (ELSER) combined with dense embeddings for hybrid search.

**Recommended Stack:** Tier 1
- Elasticsearch 8.0+ with ELSER inferred pipeline
- Dense embeddings (optional secondary)
- Framework: Python with elasticsearch-py

**Architecture Diagram:**
```
┌──────────────────┐
│ Document Text    │
└────────┬─────────┘
         │
    ┌────▼──────────────────┐
    │ ELSER Ingest Pipeline │
    │ (Automatic)           │
    │ Learned Sparse Token  │
    │ Weights               │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ Store:               │
    │ - Sparse vectors     │
    │ - Token weights      │
    │ - Original text      │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ Query Time:          │
    │ ELSER encodes query  │
    │ to same tokens       │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ BM25-like Scoring    │
    │ Learned Token IDF    │
    │ (Better than BM25)   │
    └──────────────────────┘
```

**Implementation Code (Python):**

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from typing import List, Dict, Optional
import json

class ElasticsearchELSERSearch:
    def __init__(self, es_host: str = "localhost:9200"):
        self.es = Elasticsearch([es_host])
        self.index_name = "documents_elser"

    def create_elser_index(self):
        """
        Create index with ELSER pipeline
        Requires: ml_inference privilege + ELSER model deployed
        """
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index.lifecycle.name": "default"
            },
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "ml_token_count": {
                        "type": "rank_feature"
                    },
                    "elser_embedding": {
                        "type": "sparse_vector"
                    },
                    "dense_embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }

        # Create index
        self.es.indices.create(index=self.index_name, body=settings)

        # Add ingest pipeline for ELSER
        pipeline = {
            "processors": [
                {
                    "inference": {
                        "model_id": ".elser_model_2",
                        "input_output": [
                            {
                                "input_field": "content",
                                "output_field": "elser_embedding"
                            }
                        ]
                    }
                }
            ]
        }

        self.es.ingest.put_pipeline(
            id="elser_pipeline",
            body=pipeline
        )

    def index_documents(self,
                       documents: List[Dict],
                       include_dense: bool = False):
        """
        Index documents with ELSER sparse embeddings
        Optional: also include dense embeddings for hybrid search
        """
        actions = []

        for doc in documents:
            action = {
                "_index": self.index_name,
                "_id": doc.get("id", None),
                "pipeline": "elser_pipeline",
                "_source": {
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "metadata": doc.get("metadata", {})
                }
            }

            # Optional: Add dense embedding for secondary ranking
            if include_dense:
                # In production: use actual embedding model
                import numpy as np
                dense_embedding = np.random.randn(384).tolist()
                action["_source"]["dense_embedding"] = dense_embedding

            actions.append(action)

        # Bulk index
        success, failed = bulk(self.es, actions)
        print(f"Indexed {success} documents, {failed} failed")

    def search_with_elser(self,
                         query: str,
                         top_k: int = 10,
                         use_dense_secondary: bool = False) -> List[Dict]:
        """
        Search using ELSER sparse vectors
        Optionally combine with dense embeddings
        """

        # ELSER sparse query
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "text_expansion": {
                                "elser_embedding": {
                                    "model_id": ".elser_model_2",
                                    "model_text": query
                                }
                            }
                        }
                    ]
                }
            },
            "size": top_k
        }

        # Optional: Add dense similarity for RRF fusion
        if use_dense_secondary:
            # Mock dense embedding (in production: actual embedding)
            import numpy as np
            dense_query_vector = np.random.randn(384).tolist()

            query_body["query"]["bool"]["should"].append({
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'dense_embedding') + 1.0",
                        "params": {
                            "query_vector": dense_query_vector
                        }
                    },
                    "boost": 0.5  # Secondary weight
                }
            })

        # Execute search
        response = self.es.search(index=self.index_name, body=query_body)

        results = []
        for rank, hit in enumerate(response['hits']['hits'], 1):
            results.append({
                'rank': rank,
                'id': hit['_id'],
                'content': hit['_source']['content'],
                'title': hit['_source'].get('title', ''),
                'score': hit['_score']
            })

        return results

    def search_with_rrf_fusion(self,
                              query: str,
                              top_k: int = 10) -> List[Dict]:
        """
        Use RRF to combine ELSER sparse and optional dense
        """

        # ELSER query
        elser_results = self.search_with_elser(query, top_k * 2)

        # Create ranking from ELSER
        elser_scores = {}
        for result in elser_results:
            elser_scores[result['id']] = result['score']

        # Would also get dense results here for true RRF
        # For demo: just return ELSER results

        # RRF computation
        rrf_scores = {}
        for doc_id, score in elser_scores.items():
            rrf_scores[doc_id] = score

        # Sort and return
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return [
            {
                'rank': rank,
                'id': doc_id,
                'rrf_score': score
            }
            for rank, (doc_id, score) in enumerate(sorted_docs[:top_k], 1)
        ]

# Usage
if __name__ == "__main__":
    search = ElasticsearchELSERSearch()

    # Setup
    search.create_elser_index()

    # Index documents
    docs = [
        {"id": "1", "content": "Machine learning models require large training datasets"},
        {"id": "2", "content": "Deep learning uses neural networks with multiple layers"},
        {"id": "3", "content": "Natural language processing handles text understanding"},
    ]

    search.index_documents(docs)

    # Search
    results = search.search_with_elser("deep learning neural networks", top_k=3)

    print("ELSER Search Results:")
    for result in results:
        print(f"{result['rank']}. [{result['score']:.4f}] {result['content'][:60]}...")
```

**Expected Performance:**
- Indexing latency: 100-300ms per document (ELSER inference)
- Query latency: 20-50ms (sparse search is fast)
- No training needed (ELSER is pre-trained)
- Better relevance than BM25 (learned term importance)
- Scales to 100M+ documents efficiently

**See Also:**
→ references/03-sparse-embeddings/ — ELSER, SPLADE, DeepImpact comparison
→ references/21-elasticsearch-tuning/ — Index configuration and query optimization
→ references/46-learned-to-rank/ — When ELSER isn't enough: pointwise LTR

---

## Recipe 12: SPLADE for Domain-Specific Search (Legal/Medical)

**Problem Statement:** Build specialized search for legal/medical documents using SPLADE (Sparse Lexical and Expansion Model).

**Recommended Stack:** Tier 2
- SPLADE model (domain-specific)
- ColBERT-X for maximum efficiency
- Vector store with sparse support
- Framework: Python with sentence-transformers

**Architecture Diagram:**
```
┌────────────────────────────┐
│ Domain-Specific Document   │
│ (Legal contract, Medical)  │
└────────────┬───────────────┘
             │
      ┌──────▼──────────────┐
      │ SPLADE Encoder      │
      │ (Domain-tuned)      │
      │ Outputs:            │
      │ - Token weights     │
      │ - Expansion terms   │
      └──────┬──────────────┘
             │
      ┌──────▼──────────────┐
      │ Store Sparse Vector │
      │ with Expansion      │
      └──────┬──────────────┘
             │
      ┌──────▼──────────────┐
      │ Query Encoding      │
      │ (Same SPLADE model) │
      └──────┬──────────────┘
             │
      ┌──────▼──────────────┐
      │ Similarity Matching │
      │ (Domain-specific)   │
      └─────────────────────┘
```

**Implementation Code (Python):**

```python
import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM
import numpy as np
from typing import List, Dict
from scipy.sparse import csr_matrix

class SPLADESearch:
    def __init__(self, model_name: str = "naver/splade-cocondenser-ensembledistil"):
        """
        Initialize SPLADE model
        model_name options:
        - naver/splade (general)
        - naver/splade-cocondenser-ensembledistil (efficient)
        Custom models available for legal, medical domains
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name).to(self.device)
        self.model.eval()

        self.documents = []
        self.sparse_embeddings = []  # Store as (row, col, data) for sparse matrix

    def _get_splade_embedding(self, text: str, max_length: int = 256) -> np.ndarray:
        """
        Generate SPLADE sparse embedding for text
        Returns dense representation (convert to sparse for storage)
        """
        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=max_length,
                truncation=True,
                padding=True
            ).to(self.device)

            # Get logits from masked LM head
            logits = self.model(**inputs).logits

            # Get attention weights
            attention = inputs['attention_mask'].float()

            # Compute term importance scores
            term_scores = torch.max(logits * attention.unsqueeze(-1), dim=1)[0]

            # ReLU to get positive weights
            term_scores = torch.relu(term_scores).squeeze()

            # Convert to vocabulary distribution
            vocab_size = self.tokenizer.vocab_size
            embedding = np.zeros(vocab_size, dtype=np.float32)

            for token_id, score in enumerate(term_scores):
                if score > 0:
                    embedding[token_id] = score.item()

        return embedding

    def index_documents(self, documents: List[Dict]):
        """Index documents with SPLADE embeddings"""
        self.documents = documents

        for i, doc in enumerate(documents):
            text = doc['content']

            # Get SPLADE embedding
            embedding = self._get_splade_embedding(text)

            # Store as sparse
            self.sparse_embeddings.append(embedding)

            if (i + 1) % 10 == 0:
                print(f"Indexed {i+1}/{len(documents)} documents")

    def search(self,
              query: str,
              top_k: int = 10,
              expansion: bool = True) -> List[Dict]:
        """
        Search using SPLADE
        expansion: whether to use query expansion
        """

        # Get query embedding
        query_embedding = self._get_splade_embedding(query)

        # Optionally expand query with related terms
        if expansion:
            query_embedding = self._expand_query(query_embedding)

        # Compute similarities
        similarities = []
        for doc_embedding in self.sparse_embeddings:
            # Cosine similarity on sparse vectors
            dot_product = np.dot(query_embedding, doc_embedding)
            norm_q = np.linalg.norm(query_embedding)
            norm_d = np.linalg.norm(doc_embedding)
            similarity = dot_product / (norm_q * norm_d) if norm_q > 0 and norm_d > 0 else 0
            similarities.append(similarity)

        # Get top-k
        similarities = np.array(similarities)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            doc = self.documents[idx]
            results.append({
                'rank': rank,
                'id': doc['id'],
                'content': doc['content'][:200],
                'score': float(similarities[idx]),
                'expanded': expansion
            })

        return results

    def _expand_query(self, query_embedding: np.ndarray) -> np.ndarray:
        """
        Expand query with related terms from SPLADE weights
        Helps with domain-specific synonyms
        """
        # Get top terms from query
        top_indices = np.argsort(query_embedding)[::-1][:20]

        # Could add related terms here using domain lexicon
        # For now, return original
        return query_embedding

    def domain_specific_search(self,
                              query: str,
                              domain: str = "legal",
                              top_k: int = 10) -> List[Dict]:
        """
        Search with domain-specific post-processing
        domain: "legal", "medical", "patent", etc
        """

        results = self.search(query, top_k * 2)

        # Apply domain-specific filtering/boosting
        if domain == "legal":
            # Boost results with legal keywords
            legal_keywords = ["clause", "agreement", "liability", "jurisdiction"]
            for result in results:
                if any(kw in result['content'].lower() for kw in legal_keywords):
                    result['score'] *= 1.5

        elif domain == "medical":
            # Boost results with medical terminology
            medical_keywords = ["patient", "treatment", "diagnosis", "symptom"]
            for result in results:
                if any(kw in result['content'].lower() for kw in medical_keywords):
                    result['score'] *= 1.5

        # Re-sort by modified scores
        results.sort(key=lambda x: x['score'], reverse=True)

        return results[:top_k]

# Usage
if __name__ == "__main__":
    search = SPLADESearch()

    # Index legal documents
    docs = [
        {
            "id": "legal1",
            "content": "This agreement shall terminate upon 30 days written notice. Neither party shall be liable for indirect damages."
        },
        {
            "id": "legal2",
            "content": "The jurisdiction of this contract is determined by the laws of the state. Disputes shall be resolved through arbitration."
        },
        {
            "id": "legal3",
            "content": "All intellectual property rights remain with the original creator. Licensed use is restricted to commercial purposes only."
        }
    ]

    search.index_documents(docs)

    # Search
    results = search.domain_specific_search(
        "liability clause agreement",
        domain="legal",
        top_k=3
    )

    print("Legal Document Search Results:")
    for result in results:
        print(f"{result['rank']}. [{result['score']:.4f}] {result['content'][:80]}...")
```

**Expected Performance:**
- Embedding latency: 50-150ms per document
- Query latency: 10-30ms
- Specialization gain: +10-20% NDCG on domain datasets
- Memory efficient: sparse vectors only store non-zero weights
- Works with domain-specific fine-tuned models

**See Also:**
→ references/03-sparse-embeddings/ — SPLADE vs ELSER vs DeepImpact
→ references/26-domain-specific-models/ — Fine-tuning for legal, medical, finance
→ references/50-specialized-retrieval/ — Terminology expansion and synonym handling

---

## Recipe 13: Multi-Stage Ranking Pipeline

**Problem Statement:** Production-grade ranking with retrieval, reranking, and personalization stages.

**Recommended Stack:** Tier 1
- Retrieval layer (BM25/Vector/Hybrid)
- First-stage reranker (fast, 100ms budget)
- Second-stage reranker (slow, 500ms budget)
- Personalization layer
- Framework: Python with LangChain/haystack

**Architecture Diagram:**
```
┌────────────────────────┐
│ Query                  │
└───────────┬────────────┘
            │
    ┌───────▼────────┐
    │ Stage 1:       │
    │ Fast Retrieval │
    │ (BM25/Vector)  │
    │ 1000 candidates│
    │ ~10ms          │
    └───────┬────────┘
            │
    ┌───────▼─────────────┐
    │ Stage 2:            │
    │ Fast Reranker       │
    │ (DistilBERT)        │
    │ Top 100 → Top 50    │
    │ ~100ms              │
    └───────┬─────────────┘
            │
    ┌───────▼──────────────┐
    │ Stage 3:             │
    │ Expensive Reranker   │
    │ (GPT-4, cross-enc)   │
    │ Top 50 → Top 20      │
    │ ~500ms               │
    └───────┬──────────────┘
            │
    ┌───────▼──────────────┐
    │ Stage 4:             │
    │ Personalization      │
    │ User prefs + context │
    │ Top 20 → Top 10      │
    │ ~50ms                │
    └───────┬──────────────┘
            │
    ┌───────▼──────────────┐
    │ Final Results        │
    │ ~700ms total latency │
    └──────────────────────┘
```

**Implementation Code (Python):**

```python
from typing import List, Dict, Callable
import time
from dataclasses import dataclass
import numpy as np

@dataclass
class RankingResult:
    id: str
    content: str
    score: float
    stage_scores: Dict[str, float]

class MultiStageRankingPipeline:
    def __init__(self):
        self.retriever = None
        self.fast_reranker = None
        self.expensive_reranker = None
        self.personalizer = None
        self.latency_budget = {
            'retrieval': 10,
            'fast_rerank': 100,
            'expensive_rerank': 500,
            'personalization': 50
        }

    def set_retriever(self, retriever: Callable):
        """Set retrieval function: query -> List[{id, content, score}]"""
        self.retriever = retriever

    def set_fast_reranker(self, reranker: Callable):
        """Set fast reranker: (query, docs) -> List[{id, score}]"""
        self.fast_reranker = reranker

    def set_expensive_reranker(self, reranker: Callable):
        """Set expensive reranker: (query, docs) -> List[{id, score}]"""
        self.expensive_reranker = reranker

    def set_personalizer(self, personalizer: Callable):
        """Set personalization: (query, docs, user_id) -> List[{id, score}]"""
        self.personalizer = personalizer

    def rank(self,
            query: str,
            user_id: str = None,
            final_k: int = 10,
            enable_expensive: bool = True) -> List[RankingResult]:
        """
        Execute multi-stage ranking pipeline
        """
        timing = {}

        # Stage 1: Fast Retrieval
        t0 = time.time()
        candidates = self.retriever(query, k=1000)
        timing['retrieval'] = time.time() - t0

        if len(candidates) == 0:
            return []

        # Stage 2: Fast Reranker (e.g., DistilBERT)
        t0 = time.time()
        if self.fast_reranker:
            fast_rerank_scores = self.fast_reranker(query, candidates)
            candidates = sorted(
                zip(candidates, fast_rerank_scores),
                key=lambda x: x[1],
                reverse=True
            )[:100]
            candidates = [c[0] for c in candidates]

        timing['fast_rerank'] = time.time() - t0

        # Stage 3: Expensive Reranker (GPT-4, CrossEncoder)
        t0 = time.time()
        if self.expensive_reranker and enable_expensive:
            if timing['retrieval'] + timing['fast_rerank'] < 200:  # Time budget check
                expensive_scores = self.expensive_reranker(query, candidates[:50])
                candidates = sorted(
                    zip(candidates[:50], expensive_scores),
                    key=lambda x: x[1],
                    reverse=True
                )
                candidates = [c[0] for c in candidates]

        timing['expensive_rerank'] = time.time() - t0

        # Stage 4: Personalization
        t0 = time.time()
        if self.personalizer and user_id:
            personalization_scores = self.personalizer(
                query,
                candidates[:20],
                user_id
            )
            candidates = sorted(
                zip(candidates[:20], personalization_scores),
                key=lambda x: x[1],
                reverse=True
            )
            candidates = [c[0] for c in candidates]

        timing['personalization'] = time.time() - t0

        # Return final results
        results = [
            RankingResult(
                id=c['id'],
                content=c['content'],
                score=c.get('final_score', c.get('score', 0)),
                stage_scores={
                    'retrieval': c.get('retrieval_score', 0),
                    'fast_rerank': c.get('fast_rerank_score', 0),
                    'expensive_rerank': c.get('expensive_rerank_score', 0),
                    'personalization': c.get('personalization_score', 0)
                }
            )
            for c in candidates[:final_k]
        ]

        # Log timing
        total_latency = sum(timing.values())
        print(f"Pipeline latency: {total_latency:.0f}ms")
        for stage, lat in timing.items():
            print(f"  {stage}: {lat:.0f}ms")

        return results

    def adaptive_ranking(self,
                        query: str,
                        user_id: str = None,
                        target_latency: int = 500) -> List[RankingResult]:
        """
        Adaptive ranking: skip expensive stages if latency budget exceeded
        """
        t0 = time.time()

        # Always do retrieval + fast rerank
        results = self.rank(query, user_id, final_k=10, enable_expensive=True)

        elapsed = (time.time() - t0) * 1000

        if elapsed > target_latency:
            # If too slow, re-run without expensive reranker
            results = self.rank(query, user_id, final_k=10, enable_expensive=False)

        return results

# Usage Example
if __name__ == "__main__":
    # Setup mock components
    def mock_retriever(query: str, k: int = 1000):
        return [
            {"id": f"doc{i}", "content": f"Document {i}", "score": 0.5}
            for i in range(k)
        ]

    def mock_fast_reranker(query: str, docs: List[Dict]):
        # Simulate DistilBERT reranking
        return np.random.rand(len(docs))

    def mock_expensive_reranker(query: str, docs: List[Dict]):
        # Simulate GPT-4 reranking
        return np.random.rand(len(docs))

    def mock_personalizer(query: str, docs: List[Dict], user_id: str):
        # Simulate user preference personalization
        return np.random.rand(len(docs))

    # Build pipeline
    pipeline = MultiStageRankingPipeline()
    pipeline.set_retriever(mock_retriever)
    pipeline.set_fast_reranker(mock_fast_reranker)
    pipeline.set_expensive_reranker(mock_expensive_reranker)
    pipeline.set_personalizer(mock_personalizer)

    # Execute
    results = pipeline.rank("query", user_id="user123", final_k=10)

    print("\nFinal Results:")
    for result in results:
        print(f"  {result.id}: {result.score:.4f}")
```

**Expected Performance:**
- Total latency: 600-800ms budget
- Stage breakdown: Retrieval 10-20ms, Fast rerank 50-100ms, Expensive rerank 400-500ms, Personalization 20-50ms
- Quality: NDCG@10 ~0.75-0.85 with good reranking
- Throughput: Bottleneck is expensive reranker (batch for 100 QPS)

**See Also:**
→ references/13-ranking-architecture/ — Production ranking systems deep dive
→ references/31-cascade-ranking/ — Efficiently routing queries to different rankers
→ references/58-latency-optimization/ — Caching, batching, and time budget allocation

---

## Recipe 14: Geospatial + Text Search

**Problem Statement:** Location-aware search combining text relevance with spatial proximity.

**Recommended Stack:** Tier 2
- Elasticsearch/OpenSearch with geospatial
- H3 hexagonal indexing for spatial grouping
- Framework: Python with elasticsearch-py

**Architecture Diagram:**
```
┌────────────────────────┐
│ Query: "restaurants"   │
│ Location: (40.7,-74.0)│
│ Radius: 5km            │
└────────────┬───────────┘
             │
      ┌──────▼──────────┐
      │ Convert to H3   │
      │ Hex ID at ~1km  │
      │ resolution      │
      └──────┬──────────┘
             │
      ┌──────▼──────────────────┐
      │ ES Query:               │
      │ 1. Geo-distance filter  │
      │ 2. Text match boost     │
      │ 3. Ranking by:          │
      │    - Relevance          │
      │    - Distance           │
      │    - Rating             │
      └──────┬──────────────────┘
             │
      ┌──────▼──────────────────┐
      │ Results Ranked by       │
      │ Distance + Relevance    │
      └────────────────────────┘
```

**Implementation Code (Python):**

```python
from elasticsearch import Elasticsearch
from typing import List, Dict, Tuple, Optional
import h3
import math

class GeospatialTextSearch:
    def __init__(self, es_host: str = "localhost:9200"):
        self.es = Elasticsearch([es_host])
        self.index_name = "places"

    def create_geospatial_index(self):
        """Create index with geospatial field"""
        settings = {
            "mappings": {
                "properties": {
                    "name": {"type": "text"},
                    "description": {"type": "text"},
                    "category": {"type": "keyword"},
                    "rating": {"type": "float"},
                    "location": {
                        "type": "geo_point"  # Elasticsearch geo field
                    },
                    "h3_id": {
                        "type": "keyword"  # H3 hexagon ID for spatial grouping
                    }
                }
            }
        }

        self.es.indices.create(index=self.index_name, body=settings)

    def index_place(self, place: Dict):
        """
        Index a place with geospatial data
        place: {name, description, category, lat, lon, rating}
        """
        # Compute H3 hex ID at resolution 8 (~5km hexagons)
        h3_id = h3.geo_to_h3(place['lat'], place['lon'], resolution=8)

        doc = {
            "name": place['name'],
            "description": place.get('description', ''),
            "category": place['category'],
            "rating": place.get('rating', 0),
            "location": {
                "lat": place['lat'],
                "lon": place['lon']
            },
            "h3_id": h3_id
        }

        self.es.index(index=self.index_name, body=doc)

    def search_nearby(self,
                     query: str,
                     lat: float,
                     lon: float,
                     distance_km: int = 5,
                     category: Optional[str] = None,
                     top_k: int = 10) -> List[Dict]:
        """
        Search for places by text + location
        """

        must_clauses = [
            {
                "multi_match": {
                    "query": query,
                    "fields": ["name^2", "description", "category"]
                }
            },
            {
                "geo_distance": {
                    "distance": f"{distance_km}km",
                    "location": {
                        "lat": lat,
                        "lon": lon
                    }
                }
            }
        ]

        if category:
            must_clauses.append({"term": {"category": category}})

        query_body = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {"lat": lat, "lon": lon},
                        "order": "asc",
                        "unit": "km"
                    }
                },
                {"rating": {"order": "desc"}}
            ],
            "size": top_k
        }

        response = self.es.search(index=self.index_name, body=query_body)

        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            distance = hit.get('sort', [None])[0]

            results.append({
                'name': source['name'],
                'category': source['category'],
                'rating': source['rating'],
                'distance_km': distance,
                'location': source['location'],
                'score': hit['_score']
            })

        return results

    def search_by_area(self,
                      query: str,
                      h3_ids: List[str],
                      top_k: int = 10) -> List[Dict]:
        """
        Search within specific H3 hexagon regions
        (useful for neighborhood/area-based search)
        """

        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["name^2", "description"]
                            }
                        },
                        {
                            "terms": {
                                "h3_id": h3_ids
                            }
                        }
                    ]
                }
            },
            "size": top_k
        }

        response = self.es.search(index=self.index_name, body=query_body)

        return [
            {
                'name': hit['_source']['name'],
                'rating': hit['_source']['rating'],
                'category': hit['_source']['category'],
                'score': hit['_score']
            }
            for hit in response['hits']['hits']
        ]

    def get_area_hexagons(self,
                         lat: float,
                         lon: float,
                         radius_km: int = 5,
                         resolution: int = 8) -> List[str]:
        """Get H3 hexagon IDs covering a geographic area"""
        center_h3 = h3.geo_to_h3(lat, lon, resolution=resolution)
        ring = h3.hex_ring(center_h3, 1)  # Get neighbors
        return [center_h3] + list(ring)

# Usage
if __name__ == "__main__":
    search = GeospatialTextSearch()
    search.create_geospatial_index()

    # Index places
    places = [
        {"name": "Pizza Palace", "category": "restaurant", "lat": 40.7128, "lon": -74.0060, "rating": 4.5, "description": "Italian pizza"},
        {"name": "Sushi House", "category": "restaurant", "lat": 40.7150, "lon": -74.0080, "rating": 4.8, "description": "Japanese sushi"},
        {"name": "Brew Coffee", "category": "cafe", "lat": 40.7100, "lon": -74.0040, "rating": 4.2, "description": "Artisan coffee shop"},
    ]

    for place in places:
        search.index_place(place)

    # Search
    results = search.search_nearby(
        "restaurant",
        lat=40.7128,
        lon=-74.0060,
        distance_km=2,
        top_k=5
    )

    print("Nearby Results:")
    for result in results:
        print(f"  {result['name']} ({result['category']})")
        print(f"    Distance: {result['distance_km']:.2f}km, Rating: {result['rating']}/5\n")
```

**Expected Performance:**
- Query latency: 30-80ms (geo-distance filter + text match)
- H3 hexagon grouping: ~5km resolution appropriate for most use cases
- Scales to millions of locations
- Sorting by distance + relevance: efficient with ES indices

**See Also:**
→ references/10-geospatial-search/ — H3 vs Geohash vs quad-trees
→ references/27-location-personalization/ — Context-aware ranking with geography
→ references/51-neighborhood-search/ — Area-based aggregation and faceting

---

## Recipe 15: Real-Time Search Index (CDC + Debezium)

**Problem Statement:** Keep search index in sync with database changes in real-time (seconds latency).

**Recommended Stack:** Tier 1
- Debezium for Change Data Capture (CDC)
- Kafka for event streaming
- Elasticsearch/Pinecone for search index
- Framework: Python with kafka-python

**Architecture Diagram:**
```
┌──────────────────────────────┐
│ Primary Database             │
│ (PostgreSQL, MySQL)          │
│ Write: "INSERT product"      │
└──────────┬───────────────────┘
           │
    ┌──────▼──────────────┐
    │ Debezium CDC        │
    │ Captures WAL events │
    │ (logical replication)
    └──────┬──────────────┘
           │
    ┌──────▼──────────────┐
    │ Kafka Topic         │
    │ db.products.changes │
    │ (Event Stream)      │
    └──────┬──────────────┘
           │
    ┌──────▼──────────────────┐
    │ Consumer:               │
    │ 1. Extract change      │
    │ 2. Transform           │
    │ 3. Enrich (embeddings) │
    │ 4. Index to Search DB  │
    └──────┬──────────────────┘
           │
    ┌──────▼──────────────┐
    │ Search Index        │
    │ (ES/Pinecone)       │
    │ Real-time sync      │
    └──────────────────────┘
```

**Implementation Code (Python):**

```python
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import json
from typing import Dict, Any, Callable
from datetime import datetime
import logging
from sentence_transformers import SentenceTransformer

class RealTimeIndexer:
    def __init__(self,
                 kafka_bootstrap: str = "localhost:9092",
                 topic: str = "db.products.changes",
                 group_id: str = "search-indexer"):
        """
        Initialize real-time indexer
        Assumes Debezium is publishing CDC events to Kafka
        """
        self.kafka_bootstrap = kafka_bootstrap
        self.topic = topic
        self.group_id = group_id

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_bootstrap,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index_handler = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def set_index_handler(self, handler: Callable):
        """
        Set handler for indexing
        handler should implement: (operation, document) -> None
        Operations: 'index', 'update', 'delete'
        """
        self.index_handler = handler

    def transform_document(self, db_document: Dict) -> Dict:
        """
        Transform database record to search document
        Add embeddings, enrichments, etc
        """
        # Extract text fields for embedding
        searchable_text = f"{db_document.get('name', '')} {db_document.get('description', '')}"

        # Generate embedding
        embedding = self.embedding_model.encode(searchable_text)

        # Create search document
        search_doc = {
            'id': db_document['id'],
            'name': db_document.get('name'),
            'description': db_document.get('description'),
            'category': db_document.get('category'),
            'price': db_document.get('price'),
            'embedding': embedding.tolist(),
            'updated_at': datetime.now().isoformat(),
            'db_updated_at': db_document.get('updated_at')
        }

        return search_doc

    def process_cdc_event(self, event: Dict) -> None:
        """
        Process a single CDC event from Debezium
        Event structure (Debezium):
        {
            "before": {...},
            "after": {...},
            "op": "c|u|d|r" (create/update/delete/read),
            "ts_ms": timestamp
        }
        """

        operation = event.get('op', 'c')
        after = event.get('after', {})
        before = event.get('before', {})

        # Handle different operations
        if operation == 'c':  # Create
            doc = self.transform_document(after)
            self.index_handler('index', doc)
            self.logger.info(f"Indexed new document: {doc['id']}")

        elif operation == 'u':  # Update
            doc = self.transform_document(after)
            self.index_handler('update', doc)
            self.logger.info(f"Updated document: {doc['id']}")

        elif operation == 'd':  # Delete
            doc_id = before.get('id')
            self.index_handler('delete', {'id': doc_id})
            self.logger.info(f"Deleted document: {doc_id}")

        elif operation == 'r':  # Read (snapshot)
            doc = self.transform_document(after)
            self.index_handler('index', doc)

    def start_indexing(self, batch_size: int = 100, timeout_ms: int = 5000):
        """
        Start consuming CDC events and indexing in real-time
        batch_size: Process events in batches for efficiency
        timeout_ms: Timeout for each batch
        """

        self.logger.info(f"Starting real-time indexer on topic: {self.topic}")

        try:
            batch = []
            for message in self.consumer:
                # Decode Debezium event
                event = message.value

                # Process event
                self.process_cdc_event(event)

                batch.append(event)

                # Batch optimization
                if len(batch) >= batch_size:
                    self.logger.info(f"Processed batch of {len(batch)} events")
                    batch = []

        except KeyboardInterrupt:
            self.logger.info("Stopping indexer")
            self.consumer.close()

    def batch_initial_sync(self, documents: list) -> None:
        """
        Initial bulk sync of all documents
        Use this to bootstrap the index from database snapshot
        """

        self.logger.info(f"Starting bulk sync of {len(documents)} documents")

        for i, doc in enumerate(documents):
            transformed = self.transform_document(doc)
            self.index_handler('index', transformed)

            if (i + 1) % 100 == 0:
                self.logger.info(f"Synced {i+1}/{len(documents)} documents")

        self.logger.info("Bulk sync complete")

# Mock Index Handler Example
class MockElasticsearchHandler:
    def __call__(self, operation: str, document: Dict) -> None:
        """Mock Elasticsearch indexing"""
        if operation == 'index':
            print(f"[INDEX] {document['id']}: {document['name']}")
        elif operation == 'update':
            print(f"[UPDATE] {document['id']}: {document['name']}")
        elif operation == 'delete':
            print(f"[DELETE] {document['id']}")

# Usage
if __name__ == "__main__":
    indexer = RealTimeIndexer(
        kafka_bootstrap="localhost:9092",
        topic="db.products.changes",
        group_id="search-indexer"
    )

    # Set index handler
    indexer.set_index_handler(MockElasticsearchHandler())

    # Simulate CDC events
    mock_events = [
        {
            "op": "c",
            "after": {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop",
                "category": "electronics",
                "price": 1200,
                "updated_at": "2026-03-01T10:00:00"
            }
        },
        {
            "op": "u",
            "before": {"id": 1},
            "after": {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop - Now on sale!",
                "category": "electronics",
                "price": 999,
                "updated_at": "2026-03-01T11:00:00"
            }
        }
    ]

    # Process events
    for event in mock_events:
        indexer.process_cdc_event(event)
```

**Expected Performance:**
- End-to-end latency: 5-15 seconds (CDC capture + Kafka + processing)
- Throughput: 1000-5000 changes/second per consumer
- Scalability: Multiple consumers for higher throughput
- Data consistency: Exactly-once semantics with Kafka + offsets
- Cost: Debezium is open-source; Kafka managed services available

**See Also:**
→ references/06-real-time-indexing/ — Debezium alternatives (Watermill, Translog)
→ references/29-event-streaming/ — Kafka partitioning and consumer groups
→ references/53-change-data-capture/ — Handling database-specific CDC (PostgreSQL WAL, MySQL binlog)

---

## Summary

These 15 recipes cover the complete spectrum of search implementation:

**Foundational (Recipes 1-5):** Start here for basic to advanced retrieval
- Hybrid search, reranking, client-side, RAG, e-commerce

**Specialized Applications (Recipes 6-10):** Domain-specific patterns
- Autocomplete, multilingual, documents, evaluation, database integration

**Production Patterns (Recipes 11-15):** Enterprise-grade systems
- ELSER/SPLADE, multi-stage ranking, geospatial, real-time sync

Each recipe includes working code, performance baselines, and cross-references to deeper reference materials.

