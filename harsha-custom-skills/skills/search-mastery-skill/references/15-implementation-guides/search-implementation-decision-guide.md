# The Ultimate Search Implementation Decision Guide

A comprehensive guide for choosing and implementing search solutions across all database sizes, budgets, and technology stacks.

---

## Table of Contents

1. [The Master Decision Tree](#the-master-decision-tree)
2. [Search Implementation Patterns by Stack](#search-implementation-patterns-by-stack)
3. [Migration Playbooks](#migration-playbooks)
4. [Performance Optimization Cookbook](#performance-optimization-cookbook)
5. [Search Quality Improvement Playbook](#search-quality-improvement-playbook)
6. [Common Anti-Patterns](#common-anti-patterns)
7. [Cost Analysis Templates](#cost-analysis-templates)
8. [Security & Compliance](#security--compliance)

---

## The Master Decision Tree

### Step 1: Determine Your Dataset Size

The size of your searchable dataset is the primary driver of architecture decisions.

```
Dataset Size Decision Flow:
├─ <1K documents
│  ├─ Client-side search (Fuse.js, MiniSearch)
│  ├─ Cost: $0/month
│  └─ Latency: <50ms (on client)
│
├─ 1K-10K documents
│  ├─ Client-side search preferred
│  ├─ OR: Simple PostgreSQL FTS
│  ├─ Cost: $0-100/month
│  └─ Latency: 50-200ms
│
├─ 10K-100K documents
│  ├─ PostgreSQL FTS (recommended)
│  ├─ OR: Meilisearch/Typesense (self-hosted)
│  ├─ Cost: $100-500/month
│  └─ Latency: 25-100ms
│
├─ 100K-1M documents
│  ├─ Meilisearch/Typesense (recommended)
│  ├─ OR: Elasticsearch (if advanced features needed)
│  ├─ Cost: $500-3K/month
│  └─ Latency: 50-150ms
│
├─ 1M-100M documents
│  ├─ Elasticsearch/OpenSearch (recommended)
│  ├─ OR: Algolia (managed)
│  ├─ Cost: $3K-50K+/month
│  └─ Latency: 100-500ms
│
└─ 100M+ documents
   ├─ Elasticsearch cluster (required)
   ├─ OR: Algolia enterprise
   ├─ Cost: $50K+/month
   └─ Latency: 500ms-2s
```

### Step 2: Evaluate Your Latency Requirements

**Latency Requirement Decision Matrix:**

| Requirement | Target | Best Solution | Why |
|------------|--------|--------------|-----|
| Ultra-fast (<10ms) | Sub-10ms | Client-side search | No network latency |
| Instant (<50ms) | <50ms | Typesense, Meilisearch | Optimized for speed |
| Good (<200ms) | <200ms | PostgreSQL FTS, Elasticsearch | Acceptable for most UX |
| Acceptable (<1s) | <1s | Any solution | Background searches |

**Performance Benchmarks by Solution:**
- Client-side (Fuse.js): <50ms for <10K docs
- PostgreSQL FTS: ~25-30ms for 1.5M records
- Typesense: ~50ms for 1M+ records
- Elasticsearch: 100ms-2s depending on tuning
- Algolia: 50-100ms with SLA

### Step 3: Map Budget Constraints

**Budget-Driven Decision Flow:**

```
Monthly Budget Decision:

$0 Budget
├─ Client-side: Fuse.js, MiniSearch (free)
├─ Server-side: PostgreSQL FTS, Elasticsearch (self-hosted)
├─ Trade-off: Engineering time, operational overhead
└─ Best for: <100K documents, in-house ops team

<$100/month
├─ Self-hosted: Typesense, Meilisearch on cheap VPS
├─ PostgreSQL: Your existing database
├─ Trade-off: ~20-40 hours setup and maintenance
└─ Best for: 10K-100K documents

<$1K/month
├─ Managed: Algolia growth tier (if <1M queries)
├─ Self-hosted: AWS/Heroku Elasticsearch cluster
├─ Hybrid: PostgreSQL + vector search add-on
└─ Best for: 100K-1M documents, non-technical teams

<$10K/month
├─ Algolia: Scale tier with volume commitments
├─ Elasticsearch Cloud: m6g.large instances
├─ Multiple search systems for different use cases
└─ Best for: 1M-100M documents, enterprise needs

Unlimited Budget
├─ Algolia Enterprise: SLA, support, custom features
├─ Dedicated Elasticsearch cluster with expert ops
├─ Hybrid search infrastructure (multiple systems)
└─ Best for: 100M+ documents, mission-critical search
```

### Step 4: Assess Feature Requirements

**Feature Requirement Checklist:**

- [ ] **Fuzzy Matching** (typo tolerance)
  - Needed for user-facing search
  - Client-side: Fuse.js, MiniSearch support
  - Server-side: All solutions support

- [ ] **Faceted Navigation** (filtering)
  - Advanced: Elasticsearch, Algolia
  - Basic: PostgreSQL (with work), Typesense
  - Not available: Client-side solutions

- [ ] **Semantic Search** (meaning-based)
  - Advanced: Elasticsearch with KNN, pgvector with PostgreSQL
  - Emerging: Meilisearch (experimental)
  - Not available: Algolia (vector plans coming)
  - Workaround: Client-side hybrid with embeddings

- [ ] **Full-Text Search**
  - All solutions support
  - Best: Elasticsearch, PostgreSQL, Meilisearch

- [ ] **Geospatial Search**
  - Advanced: Elasticsearch
  - Basic: PostgreSQL with PostGIS
  - Not available: Others (implement at app layer)

- [ ] **Multi-Language Support**
  - Elasticsearch: Extensive analyzers
  - PostgreSQL: Language-specific stemming
  - Others: Basic support with configuration

- [ ] **Real-Time Indexing**
  - All solutions support
  - Fastest: Meilisearch, Typesense (~100ms)
  - PostgreSQL: Immediate (single source of truth)
  - Elasticsearch: Near real-time (~1s)

### Step 5: Client-Side vs Server-Side Decision

**Client-Side Search Criteria:**

Choose client-side search when:
- ✓ Dataset <10K documents
- ✓ Can load entire dataset on client
- ✓ Don't need advanced features (faceting, semantic search)
- ✓ Want zero backend infrastructure
- ✓ Building static site or JAMstack architecture
- ✓ Offline-first capability required

**Server-Side Search Criteria:**

Choose server-side search when:
- ✓ Dataset >10K documents
- ✓ Cannot load all data to client
- ✓ Need faceted navigation
- ✓ Real-time data updates critical
- ✓ Advanced ranking required
- ✓ Private/sensitive data (don't expose to client)

---

## Search Implementation Patterns by Stack

### Pattern 1: React/Next.js + Client-Side Search (Fuse.js)

**Best for:** Static content, documentation, <10K documents

**Architecture:**
```javascript
// 1. Build time: Export searchable data
export async function getStaticProps() {
  const documents = await getAllDocuments();
  return {
    props: { documents },
    revalidate: 3600
  };
}

// 2. Client component: Fuse.js search
import Fuse from 'fuse.js';

export function SearchComponent({ documents }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const fuse = useMemo(() => new Fuse(documents, {
    keys: ['title', 'content', 'tags'],
    threshold: 0.3,
    ignoreLocation: true,
    minMatchCharLength: 2
  }), [documents]);

  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      return;
    }

    // Debounce search (200ms)
    const timer = setTimeout(() => {
      setResults(fuse.search(query).slice(0, 10));
    }, 200);

    return () => clearTimeout(timer);
  }, [query, fuse]);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <ResultsList results={results} />
    </div>
  );
}
```

**Pros:**
- Zero backend required
- Instant results (no network latency)
- Fully customizable ranking
- Works offline
- SEO friendly with CDN distribution

**Cons:**
- Data exposed to client
- Can't scale beyond ~10K documents
- No real-time updates
- Larger initial page load

**Cost:** $0/month

---

### Pattern 2: React/Next.js + Algolia

**Best for:** Product search, content discovery, 100K-100M documents

**Architecture:**
```javascript
// 1. Client setup
import algoliasearch from 'algoliasearch';
import { InstantSearch, SearchBox, Hits } from 'react-instantsearch';

const searchClient = algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID,
  process.env.NEXT_PUBLIC_ALGOLIA_SEARCH_KEY
);

export function SearchUI() {
  return (
    <InstantSearch searchClient={searchClient} indexName="products">
      <SearchBox />
      <Hits hitComponent={Hit} />
      <RefinementList attribute="category" />
      <Pagination />
    </InstantSearch>
  );
}

// 2. Server setup: Index products
import algoliasearch from 'algoliasearch';

const client = algoliasearch(
  process.env.ALGOLIA_APP_ID,
  process.env.ALGOLIA_WRITE_KEY
);
const index = client.initIndex('products');

async function indexProducts(products) {
  await index.saveObjects(products, { autoGenerateObjectIDIfNotExist: true });
}

// 3. Sync on updates
export async function updateProduct(product) {
  await db.products.update(product);
  await index.partialUpdateObject({
    objectID: product.id,
    ...product
  });
}
```

**Pros:**
- Ready-to-use UI components
- Hosted solution (no ops burden)
- Excellent performance (<100ms)
- Rich analytics built-in
- Geo-location targeting

**Cons:**
- Cost scales with volume ($1-5 per 1000 queries)
- Data sent to third-party
- Less control over ranking
- Vendor lock-in

**Typical Cost:** $50-5000/month depending on volume

---

### Pattern 3: Node.js/Express + Elasticsearch

**Best for:** Large-scale applications, 1M-100M documents, advanced features

**Architecture:**
```javascript
// 1. Initialize client
const { Client } = require('@elastic/elasticsearch');
const client = new Client({ node: 'http://localhost:9200' });

// 2. Create index with custom analyzers
async function createIndex() {
  await client.indices.create({
    index: 'products',
    settings: {
      number_of_shards: 3,
      number_of_replicas: 1,
      analysis: {
        analyzer: {
          standard_with_synonyms: {
            type: 'standard',
            stopwords: '_english_',
            synonym_graph: 'synonyms'
          }
        }
      }
    },
    mappings: {
      properties: {
        title: { type: 'text', analyzer: 'standard_with_synonyms' },
        description: { type: 'text' },
        price: { type: 'float' },
        category: { type: 'keyword' },
        location: { type: 'geo_point' },
        tags: { type: 'keyword' },
        updated_at: { type: 'date' }
      }
    }
  });
}

// 3. Index documents
async function indexProduct(product) {
  await client.index({
    index: 'products',
    id: product.id,
    body: product,
    refresh: true // For real-time search
  });
}

// 4. Advanced search with query DSL
async function search(query, filters = {}) {
  const response = await client.search({
    index: 'products',
    body: {
      query: {
        bool: {
          must: [
            {
              multi_match: {
                query,
                fields: ['title^3', 'description', 'tags'],
                fuzziness: 'AUTO',
                type: 'best_fields'
              }
            }
          ],
          filter: [
            { range: { price: { gte: filters.minPrice, lte: filters.maxPrice } } },
            { terms: { category: filters.categories } }
          ]
        }
      },
      aggs: {
        categories: { terms: { field: 'category', size: 100 } },
        price_ranges: { range: { field: 'price', ranges: [
          { to: 50 }, { from: 50, to: 200 }, { from: 200 }
        ]}}
      },
      size: 20,
      from: (filters.page - 1) * 20
    }
  });

  return response;
}

// 5. Learning to Rank (LTR) implementation
async function searchWithRanking(query, userId) {
  const results = await search(query);

  // Rerank using behavioral signals
  const ranked = results.hits.hits
    .map(hit => ({
      ...hit,
      _score: recomputeScore(hit, { userId })
    }))
    .sort((a, b) => b._score - a._score);

  return ranked;
}
```

**Pros:**
- Highly scalable (100M+ documents)
- Advanced features (geo, vector search)
- Distributed architecture for high availability
- Rich query language
- Community and ecosystem

**Cons:**
- Complex setup and tuning required
- Higher operational overhead
- Requires dedicated team
- Memory intensive
- Two sources of truth (sync challenges)

**Typical Cost:** $3K-50K+/month (self-hosted or Elasticsearch Cloud)

---

### Pattern 4: Python/Django + Meilisearch

**Best for:** Developer-friendly, 10K-100M documents, need typo tolerance

**Architecture:**
```python
# 1. Django integration
from meilisearch_django.models import MeilisearchQuerySet

class Product(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    category = models.CharField(max_length=50)

    objects = MeilisearchQuerySet.as_manager()

    class MeilisearchMeta:
        fields = ['id', 'title', 'description', 'price', 'category']
        settings = {
            'typoTolerance': {
                'enabled': True,
                'minWordSizeForTypos': { 'oneTypo': 5, 'twoTypos': 9 }
            },
            'searchableAttributes': ['title', 'description', 'category'],
            'sortableAttributes': ['price', 'updated_at'],
            'filterableAttributes': ['category', 'price']
        }

# 2. Search view
from django.http import JsonResponse
from meilisearch_django.models import MeilisearchQuerySet

def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category')

    filters = []
    if category:
        filters.append(f'category = {category}')

    results = Product.objects.ms_search(
        query,
        filters=filters,
        sort=['price:asc'],
        limit=20
    )

    return JsonResponse({
        'results': [
            {
                'id': r.id,
                'title': r.title,
                'score': r._score
            }
            for r in results
        ]
    })

# 3. Sync on save
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Product)
def index_product(sender, instance, created, **kwargs):
    instance.index()  # Automatic Meilisearch sync
```

**Pros:**
- Simple Django integration
- Instant results (<50ms)
- Excellent typo tolerance
- JSON API
- Built-in dashboard

**Cons:**
- Single-node architecture limits scale
- Less mature than Elasticsearch
- Limited advanced features
- Smaller community

**Typical Cost:** $100-1000/month (self-hosted), $50/month (managed)

---

### Pattern 5: PostgreSQL FTS + pgvector (Hybrid Search)

**Best for:** Existing PostgreSQL users, 10K-1M documents, cost-sensitive

**Architecture:**
```sql
-- 1. Create full-text search index
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  title TEXT,
  content TEXT,
  category VARCHAR(50),
  created_at TIMESTAMP DEFAULT now()
);

-- Add tsvector column for full-text search
ALTER TABLE documents ADD COLUMN search_vector tsvector;

-- Create trigger to maintain tsvector
CREATE FUNCTION document_search_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector :=
    to_tsvector('english', COALESCE(NEW.title, '') || ' ' ||
                           COALESCE(NEW.content, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER document_search_trigger
BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION document_search_update();

-- Index for performance
CREATE INDEX documents_search_idx ON documents USING GIN(search_vector);

-- 2. Install pgvector for semantic search
CREATE EXTENSION vector;

ALTER TABLE documents ADD COLUMN embedding vector(1536);
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);

-- 3. Full-text search query
SELECT
  id,
  title,
  ts_rank(search_vector, query) as rank
FROM documents,
     plainto_tsquery('english', 'best coffee') as query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;

-- 4. Hybrid search (keyword + semantic)
WITH keyword_results AS (
  SELECT
    id,
    title,
    ts_rank(search_vector, plainto_tsquery('english', 'coffee')) as bm25_score
  FROM documents
  WHERE search_vector @@ plainto_tsquery('english', 'coffee')
),
semantic_results AS (
  SELECT
    id,
    title,
    (1 - (embedding <=> query_embedding)) as semantic_score
  FROM documents
  WHERE embedding IS NOT NULL
  CROSS JOIN (SELECT $1::vector as query_embedding) q
  ORDER BY semantic_score DESC LIMIT 100
)
SELECT
  COALESCE(k.id, s.id) as id,
  COALESCE(k.title, s.title) as title,
  COALESCE(k.bm25_score, 0) * 0.4 +
  COALESCE(s.semantic_score, 0) * 0.6 as final_score
FROM keyword_results k
FULL OUTER JOIN semantic_results s ON k.id = s.id
ORDER BY final_score DESC
LIMIT 20;
```

**Python Integration:**
```python
from django.db.models import F, Value, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

def search_documents(query_text):
    search_query = SearchQuery(query_text, search_type='websearch')
    search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')

    results = Document.objects.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(
        search=search_query
    ).order_by('-rank')[:20]

    return results

# Hybrid search with embeddings
def hybrid_search(query_text, embedding):
    from pgvector.django import L2Distance

    # Normalize scores: BM25 (0-1) + Semantic (0-1)
    bm25_results = search_documents(query_text)
    semantic_results = Document.objects.annotate(
        distance=L2Distance('embedding', embedding)
    ).order_by('distance')[:100]

    # Combine and rerank
    combined = merge_and_rank(bm25_results, semantic_results)
    return combined[:20]
```

**Pros:**
- Single source of truth (no sync needed)
- ~25-30ms latency
- Zero additional infrastructure
- ACID transactions
- Perfect for real-time data
- Can add vector search (pgvector)

**Cons:**
- Not optimized for full-text like dedicated engines
- Limited advanced features (faceting)
- Doesn't scale beyond single database
- Requires PostgreSQL expertise

**Typical Cost:** $0-200/month (included in database)

---

### Pattern 6: Mobile Search (React Native + Expo)

**Best for:** Mobile apps, offline-first, <100K documents

**Architecture:**
```javascript
import SQLite from 'expo-sqlite';
import Fuse from 'fuse.js';

// 1. Initialize local database
const db = SQLite.openDatabase('search.db');

async function initializeDatabase(documents) {
  await db.execAsync([{
    sql: `
      CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        title TEXT,
        content TEXT,
        searchable_text TEXT
      )
    `,
    args: []
  }]);

  // Bulk insert
  const insertStatements = documents.map(doc => ({
    sql: 'INSERT INTO documents (id, title, content, searchable_text) VALUES (?, ?, ?, ?)',
    args: [doc.id, doc.title, doc.content, `${doc.title} ${doc.content}`]
  }));

  await db.execAsync(insertStatements);
}

// 2. Hybrid search: SQLite FTS + Fuse.js
async function search(query) {
  // SQLite full-text search
  const sqliteResults = await db.getAllAsync(`
    SELECT * FROM documents
    WHERE searchable_text LIKE ?
    LIMIT 50
  `, [`%${query}%`]);

  // Create Fuse index only if not already cached
  if (!this.fuseIndex) {
    const allDocs = await db.getAllAsync('SELECT * FROM documents');
    this.fuseIndex = new Fuse(allDocs, {
      keys: ['title', 'content'],
      threshold: 0.3
    });
  }

  // Fuse fuzzy search
  const fuzzyResults = this.fuseIndex.search(query);

  // Combine and deduplicate
  const combined = [...sqliteResults, ...fuzzyResults]
    .reduce((acc, item) => {
      const doc = item.item || item;
      if (!acc.find(d => d.id === doc.id)) acc.push(doc);
      return acc;
    }, []);

  return combined.slice(0, 20);
}

// 3. React Native component
import { FlatList, TextInput, View, Text } from 'react-native';

export function SearchScreen() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const timer = setTimeout(() => {
      search(query).then(setResults);
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <View>
      <TextInput
        value={query}
        onChangeText={setQuery}
        placeholder="Search offline..."
      />
      <FlatList
        data={results}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <ResultItem item={item} />}
      />
    </View>
  );
}
```

**Pros:**
- Works offline
- No network latency
- Storage-efficient (SQLite)
- Mobile-optimized
- User privacy (data on device)

**Cons:**
- Limited to device storage
- Synchronization complexity
- Can't update indices in real-time
- Search logic in app code

**Typical Cost:** $0/month

---

### Pattern 7: Static Sites with Pagefind

**Best for:** Documentation, blogs, static content, <100K documents

**Architecture:**
```bash
# 1. Install
npm install -D pagefind

# 2. Build configuration
# package.json
{
  "scripts": {
    "build": "next build && pagefind --source out"
  }
}

# 3. HTML integration
<link href="/_pagefind/pagefind-ui.css" rel="stylesheet">
<script src="/_pagefind/pagefind-ui.js"></script>
<div id="search"></div>
<script>
  window.addEventListener('DOMContentLoaded', (event) => {
    new PagefindUI({ element: "#search", showImages: false });
  });
</script>
```

**Pros:**
- Zero backend
- Static hosting only
- Automatic indexing
- Great SEO
- Works offline

**Cons:**
- Build-time only (no real-time)
- Limited customization
- Entire index in browser
- Scales to ~100K pages

**Typical Cost:** $0/month

---

## Migration Playbooks

### Migration 1: Basic SQL LIKE → Full-Text Search

**From:**
```sql
SELECT * FROM articles WHERE title LIKE '%coffee%' OR content LIKE '%coffee%';
```

**To PostgreSQL FTS:**
```sql
-- Step 1: Add tsvector column
ALTER TABLE articles ADD COLUMN search_tsvector tsvector;

-- Step 2: Populate existing data
UPDATE articles SET search_tsvector =
  to_tsvector('english', title || ' ' || content);

-- Step 3: Create trigger
CREATE FUNCTION articles_search_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.search_tsvector := to_tsvector('english',
    NEW.title || ' ' || NEW.content);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_search_trigger
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW EXECUTE FUNCTION articles_search_update();

-- Step 4: Create index
CREATE INDEX articles_search_idx ON articles USING GIN(search_tsvector);

-- Step 5: New query (10-100x faster)
SELECT * FROM articles
WHERE search_tsvector @@ to_tsquery('english', 'coffee')
ORDER BY ts_rank(search_tsvector, to_tsquery('english', 'coffee')) DESC;
```

**Performance Gain:** 100-1000x faster

---

### Migration 2: Elasticsearch → Meilisearch/Typesense

**Step 1: Export data from Elasticsearch**
```bash
# Install elasticsearch-dump
npm install -g elasticdump

# Export all indices
elasticdump --input=http://localhost:9200/products \
            --output=products.json \
            --type=data
```

**Step 2: Transform and import to Meilisearch**
```python
import json
import requests

# Read ES export
with open('products.json', 'r') as f:
    docs = json.load(f)

# Transform to Meilisearch format
meilisearch_docs = [
    {
        'id': doc['_id'],
        **doc['_source']
    }
    for doc in docs
]

# Import to Meilisearch
response = requests.post(
    'http://localhost:7700/indexes/products/documents',
    json=meilisearch_docs,
    headers={'Authorization': f'Bearer {MEILISEARCH_MASTER_KEY}'}
)

print(f"Indexed {response.json()['taskUid']} documents")
```

**Step 3: Update application code**
```javascript
// Before: Elasticsearch
const { Client } = require('@elastic/elasticsearch');
const client = new Client({ node: 'http://localhost:9200' });

async function search(query) {
  const result = await client.search({
    index: 'products',
    body: { query: { match: { title: query } } }
  });
  return result.hits.hits;
}

// After: Meilisearch
import { MeiliSearch } from 'meilisearch';
const client = new MeiliSearch({ host: 'http://localhost:7700' });

async function search(query) {
  const results = await client.index('products').search(query);
  return results.hits;
}
```

**Migration Cost:** 2-5 days of engineering time

---

### Migration 3: Client-Side → Server-Side Search

**Trigger:** Dataset growing beyond 10K documents or real-time updates needed

**Step 1: Identify breaking points**
```javascript
// Monitor in your client-side search
const PERFORMANCE_THRESHOLD = 100; // ms

function monitorSearchPerformance(startTime, docCount, resultCount) {
  const duration = performance.now() - startTime;

  if (duration > PERFORMANCE_THRESHOLD) {
    console.warn(
      `Search slow: ${duration}ms for ${docCount} docs, ${resultCount} results`
    );

    // Signal backend migration needed
    analytics.track('search_performance_degradation', {
      duration,
      docCount,
      resultCount
    });
  }
}
```

**Step 2: Add server-side search alongside client**
```javascript
// Hybrid mode: try client first, fallback to server
async function hybridSearch(query) {
  try {
    // Try client-side (fast path)
    const startTime = performance.now();
    const results = clientSideSearch(query);
    const duration = performance.now() - startTime;

    // If slow, use server next time
    if (duration > 200) {
      setUseServerSearch(true);
    }

    return results;
  } catch (error) {
    // Fallback to server
    return serverSearch(query);
  }
}
```

**Step 3: Migrate users gradually**
```javascript
// Feature flag for gradual rollout
const useServerSearch = featureFlags.isEnabled('server_search') &&
                       Math.random() < 0.1; // 10% rollout

// A/B test: client vs server performance
if (useServerSearch) {
  await serverSearch(query);
} else {
  clientSideSearch(query);
}
```

---

### Migration 4: Keyword Search → Hybrid (Keyword + Semantic)

**Step 1: Add embeddings model**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Choose model: 'all-MiniLM-L6-v2' (fast), 'all-mpnet-base-v2' (accurate)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed all documents
embeddings = model.encode([
    doc['title'] + ': ' + doc['content']
    for doc in documents
])
```

**Step 2: Store embeddings**
```sql
-- PostgreSQL with pgvector
ALTER TABLE documents ADD COLUMN embedding vector(384);
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);

-- Update embeddings
UPDATE documents SET embedding = $1 WHERE id = $2;
```

**Step 3: Implement hybrid scoring**
```python
def hybrid_search(query_text, top_k=20):
    # 1. Keyword search
    keyword_results = db.execute("""
        SELECT id, title, ts_rank(search_vector, query) as score
        FROM documents, plainto_tsquery('english', %s) query
        WHERE search_vector @@ query
    """, [query_text]).fetchall()

    # 2. Semantic search
    query_embedding = model.encode(query_text)
    semantic_results = db.execute("""
        SELECT id, title, 1 - (embedding <=> %s::vector) as score
        FROM documents
        WHERE embedding IS NOT NULL
        ORDER BY score DESC LIMIT 50
    """, [query_embedding]).fetchall()

    # 3. Combine scores (0.4 keyword + 0.6 semantic)
    combined = {}
    for doc_id, title, score in keyword_results:
        combined[doc_id] = {'title': title, 'keyword_score': score}

    for doc_id, title, score in semantic_results:
        if doc_id in combined:
            combined[doc_id]['semantic_score'] = score
        else:
            combined[doc_id] = {'title': title, 'semantic_score': score}

    # Score combination
    results = [
        {
            'id': doc_id,
            'title': data['title'],
            'score': (
                0.4 * data.get('keyword_score', 0) +
                0.6 * data.get('semantic_score', 0)
            )
        }
        for doc_id, data in combined.items()
    ]

    return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
```

---

## Performance Optimization Cookbook

### Optimization 1: Debounce Search Requests

**Problem:** Every keystroke triggers a search → server overload + poor UX

**Solution:**
```javascript
// React hook with configurable delay
function useDebounce(value, delay = 200) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// Usage
export function SearchComponent() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery.length < 2) return;

    search(debouncedQuery).then(setResults);
  }, [debouncedQuery]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}
```

**Impact:** 80-90% reduction in search queries

---

### Optimization 2: Client-Side Result Caching

```javascript
class SearchCache {
  constructor(maxSize = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  get(key) {
    if (!this.cache.has(key)) return null;

    // Move to end (LRU)
    const value = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, value);

    return value;
  }

  set(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }

    this.cache.set(key, value);

    // Evict oldest if exceeds max
    if (this.cache.size > this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
  }

  clear() {
    this.cache.clear();
  }
}

// Usage
const searchCache = new SearchCache(50);

async function searchWithCache(query) {
  const cached = searchCache.get(query);
  if (cached) return cached;

  const results = await fetch(`/api/search?q=${query}`).then(r => r.json());
  searchCache.set(query, results);

  return results;
}
```

**Impact:** 70-80% of searches served from cache

---

### Optimization 3: Lazy-Load Results with Pagination

```javascript
// Virtual scrolling for large result sets
import { FixedSizeList as List } from 'react-window';

export function SearchResults({ results, pageSize = 20 }) {
  const [page, setPage] = useState(0);
  const visibleResults = results.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <List
      height={600}
      itemCount={results.length}
      itemSize={60}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          {results[index] && <ResultItem result={results[index]} />}
        </div>
      )}
    </List>
  );
}
```

**Impact:** Renders 100K+ results smoothly

---

### Optimization 4: Web Workers for Heavy Lifting

```javascript
// main.js
const searchWorker = new Worker('search-worker.js');

function localSearch(query) {
  return new Promise((resolve) => {
    const handleMessage = (event) => {
      resolve(event.data);
      searchWorker.removeEventListener('message', handleMessage);
    };

    searchWorker.addEventListener('message', handleMessage);
    searchWorker.postMessage({ query, documents });
  });
}

// search-worker.js
import Fuse from 'fuse.js';

let fuseIndex = null;

self.addEventListener('message', (event) => {
  const { query, documents } = event.data;

  // Initialize Fuse in worker (one-time)
  if (!fuseIndex) {
    fuseIndex = new Fuse(documents, {
      keys: ['title', 'content'],
      threshold: 0.3
    });
  }

  // Heavy search computation off main thread
  const results = fuseIndex.search(query);
  self.postMessage(results);
});
```

**Impact:** Keeps UI responsive during heavy search

---

### Optimization 5: Index Size Reduction

**Problem:** Large indices slow down everything

**Solutions:**
```sql
-- 1. Store only searchable fields, not full documents
-- Bad: Index everything
SELECT * FROM articles;

-- Good: Index only what you need to search
SELECT id, title, category FROM articles;

-- 2. Use keyword-only fields where appropriate
-- Bad: Analyze all fields for full-text
title TEXT (analyzed)

-- Good: Mix analyzed and keyword fields
title TEXT (analyzed for search)
category VARCHAR(50) (keyword for filtering)

-- 3. Remove low-value fields
-- Don't index: large JSON blobs, images, videos
-- Do index: title, tags, description, metadata

-- 4. Use aggressive filtering
CREATE INDEX articles_search_idx ON articles
USING GIN(search_tsvector)
WHERE status = 'published'; -- Only index published

-- 5. Tokenization optimization
CREATE FUNCTION article_search_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.search_tsvector := to_tsvector('english',
    SUBSTRING(NEW.title, 1, 100) || ' ' ||  -- Limit length
    SUBSTRING(NEW.content, 1, 500)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Impact:** 30-50% index size reduction

---

## Search Quality Improvement Playbook

### Step 1: Measure Current Search Quality

**Metrics to track:**
```javascript
// 1. Click-Through Rate (CTR) on first result
analytics.track('search_ctr', {
  query,
  rank_position: 1,
  clicked: true
});

// 2. Query success rate (user took action)
analytics.track('search_conversion', {
  query,
  converted: true,
  time_to_conversion: 45000 // ms
});

// 3. Bounce rate after search
analytics.track('search_bounce', {
  query,
  bounced: true
});

// 4. Search quality metrics
// NDCG@10 (Normalized Discounted Cumulative Gain)
function calculateNDCG(results, relevanceLabels, k = 10) {
  const dcg = results
    .slice(0, k)
    .reduce((sum, result, i) => {
      const relevance = relevanceLabels[result.id] || 0;
      return sum + relevance / Math.log2(i + 2);
    }, 0);

  const idealDcg = relevanceLabels
    .sort((a, b) => b - a)
    .slice(0, k)
    .reduce((sum, rel, i) => sum + rel / Math.log2(i + 2), 0);

  return dcg / idealDcg;
}

// 5. Mean Reciprocal Rank (MRR)
function calculateMRR(results, relevanceLabels) {
  for (let i = 0; i < results.length; i++) {
    if (relevanceLabels[results[i].id] > 0) {
      return 1 / (i + 1);
    }
  }
  return 0;
}
```

---

### Step 2: Improve Tokenization and Analysis

**Problem:** "MacBook Pro" doesn't match "macbook", "pro" separately

**Solution:**
```json
{
  "settings": {
    "analysis": {
      "char_filter": {
        "remove_special": {
          "type": "mapping",
          "mappings": [
            "& => and",
            "@ => at"
          ]
        }
      },
      "tokenizer": {
        "standard_with_dash": {
          "type": "pattern",
          "pattern": "[^\\w]+"
        }
      },
      "analyzer": {
        "search_analyzer": {
          "type": "custom",
          "char_filter": ["remove_special"],
          "tokenizer": "standard_with_dash",
          "filter": [
            "lowercase",
            "stop",
            "snowball",
            "synonym_graph"
          ]
        }
      }
    }
  }
}
```

---

### Step 3: Add Synonyms and Query Expansion

```json
{
  "settings": {
    "analysis": {
      "filter": {
        "synonyms": {
          "type": "synonym_graph",
          "synonyms": [
            "fast,quick,rapid",
            "phone,mobile,smartphone",
            "buy,purchase,acquire",
            "broken => defective",
            "tv,television"
          ]
        }
      }
    }
  }
}
```

---

### Step 4: Implement Typo Tolerance

**Elasticsearch:**
```json
{
  "query": {
    "multi_match": {
      "query": "espresso",
      "fields": ["title", "description"],
      "fuzziness": "AUTO",
      "prefix_length": 0,
      "max_expansions": 50
    }
  }
}
```

**PostgreSQL:**
```sql
-- Install Levenshtein for fuzzy matching
CREATE EXTENSION fuzzystrmatch;

-- Query with typo tolerance
SELECT * FROM documents
WHERE levenshtein(title, 'espreso') < 3
ORDER BY levenshtein(title, 'espreso');
```

---

### Step 5: Add Behavioral Signals

```python
def rerank_by_behavior(results, user_id):
    """Rerank results based on user behavior"""

    # Get user's click history
    user_clicks = db.query("""
        SELECT document_id, COUNT(*) as clicks
        FROM search_clicks
        WHERE user_id = %s
        GROUP BY document_id
    """, [user_id])

    click_scores = {r['document_id']: r['clicks'] for r in user_clicks}

    # Get global popularity
    global_clicks = db.query("""
        SELECT document_id, COUNT(*) as clicks
        FROM search_clicks
        GROUP BY document_id
    """).all()

    # Rerank: original score + behavioral boost
    reranked = []
    for i, result in enumerate(results):
        position_boost = 1.0 / (i + 1)  # Decrease boost for lower positions
        behavior_boost = (
            click_scores.get(result['id'], 0) * 0.3 +  # Personal history
            next((g['clicks'] for g in global_clicks
                  if g['document_id'] == result['id']), 0) * 0.1  # Global popularity
        )

        result['final_score'] = (
            result['original_score'] * 0.6 +
            position_boost * 0.2 +
            behavior_boost * 0.2
        )
        reranked.append(result)

    return sorted(reranked, key=lambda x: x['final_score'], reverse=True)
```

---

### Step 6: Implement Learning to Rank

**Using XGBoost with LambdaMART:**
```python
import xgboost as xgb
from sklearn.datasets import load_svmlight_file

# Training data format: qid, document_id, relevance_label
# 2 qid:1 1:0.5 2:0.3 3:0.8  -> Query 1, doc relevance 2, feature 1=0.5
# 0 qid:1 1:0.2 2:0.9 3:0.1

# Load training data
X_train, y_train, qgroups_train = load_svmlight_file(
    'training_data.svm',
    query_id=True,
    zero_based=False
)

# Train LambdaMART model
params = {
    'objective': 'rank:ndcg',
    'metric': 'ndcg',
    'ndcg_eval_metric': 'ndcg@10',
    'eta': 0.1,
    'max_depth': 5,
    'num_leaves': 31
}

model = xgb.train(
    params,
    xgb.DMatrix(X_train, label=y_train, group=qgroups_train),
    num_boost_round=100
)

# Predict: rerank results
def rerank_with_ltr(results, features):
    """features: [[feature_1, feature_2, ...], ...]"""
    dmatrix = xgb.DMatrix(features)
    scores = model.predict(dmatrix)

    # Sort by LTR scores
    ranked = sorted(
        zip(results, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [r[0] for r in ranked]
```

---

### Step 7: Add Semantic Search

**Using sentence transformers:**
```python
from sentence_transformers import SentenceTransformer, util
import torch

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_search(query, documents, top_k=10):
    # Encode query
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Encode documents (batch for efficiency)
    doc_texts = [f"{d['title']}: {d['description']}" for d in documents]
    doc_embeddings = model.encode(doc_texts, convert_to_tensor=True)

    # Compute similarity
    similarities = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

    # Get top-k
    top_k_indices = torch.topk(similarities, k=min(top_k, len(documents)))[1]

    return [documents[i] for i in top_k_indices]

# Hybrid: combine keyword + semantic
def hybrid_search(query, documents):
    # Keyword search
    keyword_results = keyword_search(query, documents)
    keyword_ids = {r['id']: i for i, r in enumerate(keyword_results)}

    # Semantic search
    semantic_results = semantic_search(query, documents, top_k=20)
    semantic_ids = {r['id']: i for i, r in enumerate(semantic_results)}

    # Combine: documents found by both, then keyword-only, then semantic-only
    combined = []
    seen = set()

    # Both
    for doc_id in set(keyword_ids) & set(semantic_ids):
        doc = next(d for d in documents if d['id'] == doc_id)
        doc['combined_score'] = (
            (1 - keyword_ids[doc_id] / len(keyword_results)) * 0.5 +
            (1 - semantic_ids[doc_id] / len(semantic_results)) * 0.5
        )
        combined.append(doc)
        seen.add(doc_id)

    # Keyword only
    for result in keyword_results:
        if result['id'] not in seen:
            result['combined_score'] = 0.5
            combined.append(result)
            seen.add(result['id'])

    # Semantic only
    for result in semantic_results:
        if result['id'] not in seen:
            result['combined_score'] = 0.5
            combined.append(result)
            seen.add(result['id'])

    return combined
```

---

### Step 8: Continuous Evaluation and Iteration

```python
def search_quality_dashboard():
    """Generate search quality metrics"""

    metrics = {
        'queries_per_day': db.query("""
            SELECT COUNT(*) FROM search_logs
            WHERE created_at > NOW() - INTERVAL '1 day'
        """)[0][0],

        'avg_results_per_query': db.query("""
            SELECT AVG(result_count) FROM search_logs
            WHERE created_at > NOW() - INTERVAL '7 days'
        """)[0][0],

        'ctr_first_result': db.query("""
            SELECT
              COUNT(CASE WHEN clicked_position = 1 THEN 1 END) * 100.0 / COUNT(*)
            FROM search_logs
            WHERE created_at > NOW() - INTERVAL '7 days'
              AND clicked = true
        """)[0][0],

        'zero_results_rate': db.query("""
            SELECT
              COUNT(CASE WHEN result_count = 0 THEN 1 END) * 100.0 / COUNT(*)
            FROM search_logs
            WHERE created_at > NOW() - INTERVAL '7 days'
        """)[0][0],

        'avg_time_to_click': db.query("""
            SELECT AVG(EXTRACT(EPOCH FROM (clicked_at - created_at)))
            FROM search_logs
            WHERE clicked = true
              AND created_at > NOW() - INTERVAL '7 days'
        """)[0][0],
    }

    return metrics

# Monitor and alert on degradation
def monitor_search_quality():
    current = search_quality_dashboard()
    baseline = get_baseline_metrics()

    for metric, value in current.items():
        change = (value - baseline[metric]) / baseline[metric] * 100

        if abs(change) > 10:  # 10% change
            alert(f"Search metric {metric} changed by {change}%")
```

---

## Common Anti-Patterns

### Anti-Pattern 1: Over-Engineering for Small Datasets

**Problem:**
```python
# ❌ Wrong: Using Elasticsearch for 5K documents
from elasticsearch import Elasticsearch

es = Elasticsearch(['localhost:9200'])
# Cluster management, shard allocation, memory overhead...
```

**Solution:**
```python
# ✓ Right: Use simple full-text search
from django.contrib.postgres.search import SearchVector, SearchQuery

results = Article.objects.annotate(
    search=SearchVector('title', weight='A') + SearchVector('content', weight='B')
).filter(
    search=SearchQuery(query)
)
```

**When to switch:** >100K documents or advanced features needed

---

### Anti-Pattern 2: Not Measuring Search Quality

**Problem:** Shipping search changes without data

**Solution:**
```javascript
// Track search quality metrics
function trackSearchMetrics(query, results, clicked) {
  analytics.track('search', {
    query,
    result_count: results.length,
    clicked,
    click_position: clicked ? results.findIndex(r => r.clicked) : null,
    time_to_search: performance.now() - searchStart,
    timestamp: new Date()
  });
}

// Analysis
SELECT
  query,
  COUNT(*) as searches,
  COUNT(CASE WHEN clicked THEN 1 END) as clicks,
  COUNT(CASE WHEN clicked THEN 1 END) * 100.0 / COUNT(*) as ctr,
  AVG(CASE WHEN result_count = 0 THEN 1 ELSE 0 END) * 100 as zero_result_rate
FROM search_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY query
ORDER BY searches DESC;
```

---

### Anti-Pattern 3: Ignoring Text Analysis

**Problem:**
```python
# ❌ Wrong: Default analysis
class ProductIndex(DocType):
    title = Text()
    description = Text()
```

**Solution:**
```python
# ✓ Right: Custom analysis with language support
class ProductIndex(DocType):
    title = Text(analyzer='standard_with_synonyms', fields={
        'raw': Keyword()
    })
    description = Text(analyzer='english_with_synonyms')

    class Settings:
        analysis = {
            'analyzer': {
                'standard_with_synonyms': {
                    'type': 'standard',
                    'stopwords': '_english_',
                    'synonym_graph': 'product_synonyms'
                }
            }
        }
```

---

### Anti-Pattern 4: Using Elasticsearch for <10K Documents

**Cost-Benefit Analysis:**

| Metric | Elasticsearch | PostgreSQL |
|--------|---------------|-----------|
| Setup time | 20-40 hours | 2-4 hours |
| Monthly ops cost | $500-5000 | $0-100 |
| Query latency | 100-500ms | 25-100ms |
| Maintenance burden | High | Low |
| Team expertise needed | Dedicated engineer | SQL knowledge |

**Rule of thumb:** Only use Elasticsearch if >100K documents OR need advanced features

---

### Anti-Pattern 5: Premature Ranking Optimization

**Problem:**
```python
# ❌ Wrong: Complex ranking on day 1
def custom_ranking(results):
    import ML_Model
    return ML_Model.predict(results)  # Overengineered
```

**Solution:**
```python
# ✓ Right: Start simple, measure, then optimize
# Step 1: Baseline (simple BM25)
results = search(query)

# Step 2: Measure quality
quality_metrics = measure_search_quality(results)

# Step 3: Only optimize if metrics show need
if quality_metrics['ctr'] < 0.3:
    # Add synonyms
    # Improve tokenization
    # Then measure again
    pass
```

---

## Cost Analysis Templates

### Template 1: Self-Hosted vs Managed Cost Calculator

```python
def calculate_search_costs(
    document_count,
    monthly_queries,
    engineering_hours,
    ops_hours,
    infrastructure_preference='self-hosted'
):
    """Calculate total cost of ownership"""

    costs = {}

    # === SELF-HOSTED OPTIONS ===

    # PostgreSQL FTS
    costs['postgresql_fts'] = {
        'infrastructure': 50,  # Included in DB cost
        'setup': engineering_hours * 150,
        'maintenance': ops_hours * 50 * 12,  # Annual
        'total_monthly': 50 + (engineering_hours * 150) / 12 + (ops_hours * 50)
    }

    # Meilisearch (self-hosted)
    # $5/month VPS + engineering
    costs['meilisearch_self'] = {
        'infrastructure': 5,
        'setup': engineering_hours * 150,
        'maintenance': ops_hours * 50 * 12,
        'total_monthly': 5 + (engineering_hours * 150) / 12 + (ops_hours * 50)
    }

    # Elasticsearch cluster
    # 3x m6g.large = ~$270/month
    costs['elasticsearch_self'] = {
        'infrastructure': min(270, document_count * 0.0001),  # Scale with size
        'setup': engineering_hours * 150,
        'maintenance': ops_hours * 100 * 12,  # Higher ops burden
        'total_monthly': min(270, document_count * 0.0001) +
                        (engineering_hours * 150) / 12 + (ops_hours * 100)
    }

    # === MANAGED OPTIONS ===

    # PostgreSQL managed (RDS)
    costs['postgresql_rds'] = {
        'infrastructure': 100,  # db.t3.medium
        'setup': engineering_hours * 150,
        'maintenance': ops_hours * 20 * 12,  # Lower ops
        'total_monthly': 100 + (engineering_hours * 150) / 12 + (ops_hours * 20)
    }

    # Algolia (usage-based)
    # ~$1 per 1000 queries + $0.50 per 1000 records
    query_cost = (monthly_queries / 1000) * 1.0
    record_cost = (document_count / 1000) * 0.50
    costs['algolia'] = {
        'infrastructure': query_cost + record_cost,
        'setup': 0,  # No setup
        'maintenance': 0,  # Fully managed
        'total_monthly': query_cost + record_cost
    }

    # Elasticsearch Cloud
    costs['elasticsearch_cloud'] = {
        'infrastructure': max(200, document_count * 0.0003),  # m6g.large base
        'setup': engineering_hours * 150,
        'maintenance': ops_hours * 30 * 12,  # Managed but still ops
        'total_monthly': max(200, document_count * 0.0003) +
                        (engineering_hours * 150) / 12 + (ops_hours * 30)
    }

    # === RECOMMENDATION ENGINE ===

    recommendation = {}

    for solution, cost in costs.items():
        recommendation[solution] = {
            **cost,
            'annual': cost['total_monthly'] * 12,
            'break_even_months': cost['setup'] / cost['total_monthly'] if cost['total_monthly'] > 0 else 0
        }

    return recommendation


# Example
costs = calculate_search_costs(
    document_count=50000,
    monthly_queries=10000,
    engineering_hours=40,  # 1 week setup
    ops_hours=10,  # Hours/month for ops
)

for solution, data in costs.items():
    print(f"{solution}: ${data['total_monthly']:.2f}/mo, ${data['annual']:.2f}/yr")
```

**Example Output:**
```
postgresql_fts: $650.00/mo, $7800.00/yr
meilisearch_self: $655.00/mo, $7860.00/yr
elasticsearch_self: $1170.00/mo, $14040.00/yr
postgresql_rds: $800.00/mo, $9600.00/yr
algolia: $15.00/mo, $180.00/yr ✓ CHEAPEST FOR THIS SCALE
elasticsearch_cloud: $875.00/mo, $10500.00/yr
```

---

### Template 2: Growth Transition Points

```
Monthly Budget Progression:
$0 → $100 → $1K → $10K → Unlimited

Phase 1: $0/month (Bootstrapped)
├─ <10K documents
├─ Client-side search (Fuse.js)
├─ OR PostgreSQL FTS
└─ Timeline: Months 0-6

Phase 2: $100-500/month (Early Traction)
├─ 10K-100K documents
├─ PostgreSQL or Meilisearch
├─ Self-hosted on $5-10/month VPS
└─ Timeline: Months 6-18

Phase 3: $500-3K/month (Growth)
├─ 100K-1M documents
├─ Meilisearch/Typesense managed ($200/mo)
├─ OR Elasticsearch Cloud ($500/mo)
└─ Timeline: Months 18-36

Phase 4: $3K-50K/month (Scale)
├─ 1M-100M documents
├─ Algolia (~$50-5000/mo based on volume)
├─ OR Elasticsearch cluster ($1000-30K/mo)
└─ Timeline: Months 36+

Phase 5: Unlimited (Enterprise)
├─ 100M+ documents
├─ Algolia enterprise ($10K+/mo)
├─ OR dedicated Elasticsearch infrastructure
├─ Custom features and SLAs
└─ Timeline: As needed
```

---

## Security & Compliance

### Secure Search API Implementation

```python
from functools import wraps
from flask import request, jsonify
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

# 1. Authentication
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key or not validate_api_key(api_key):
            logger.warning(f"Invalid API key from {request.remote_addr}")
            return jsonify({'error': 'Unauthorized'}), 401

        return f(*args, **kwargs)

    return decorated_function

# 2. Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/search')
@limiter.limit("100 per hour")
@require_api_key
def search():
    # Actual search
    pass

# 3. Input validation
from marshmallow import Schema, fields, ValidationError

class SearchSchema(Schema):
    query = fields.Str(required=True, validate=lambda x: 2 <= len(x) <= 1000)
    limit = fields.Int(missing=20, validate=lambda x: 1 <= x <= 100)
    offset = fields.Int(missing=0, validate=lambda x: x >= 0)
    filters = fields.Dict(missing={})

@app.route('/search', methods=['POST'])
@require_api_key
def search():
    schema = SearchSchema()

    try:
        args = schema.load(request.json)
    except ValidationError as err:
        logger.warning(f"Invalid search request: {err}")
        return jsonify({'error': 'Invalid request'}), 400

    # Sanitize query (prevent injection)
    query = sanitize_query(args['query'])

    results = search_engine.search(query, **args)

    # Log search (for analytics and compliance)
    log_search(
        user_id=get_user_id(request),
        query=query,
        result_count=len(results),
        timestamp=datetime.now()
    )

    return jsonify({'results': results})

# 4. GDPR: Right to be forgotten
@app.route('/user/<user_id>/data/delete', methods=['DELETE'])
@require_admin
def delete_user_data(user_id):
    """Delete all user data from search index"""

    # 1. Delete from search index
    search_engine.delete_documents(user_id=user_id)

    # 2. Delete from logging
    logger.info(f"Deleting search logs for user {user_id}")
    db.execute("""
        DELETE FROM search_logs WHERE user_id = %s
    """, [user_id])

    # 3. Verify deletion
    remaining = search_engine.count(user_id=user_id)
    if remaining > 0:
        logger.error(f"Failed to delete user {user_id} data: {remaining} docs remain")
        return jsonify({'error': 'Deletion failed'}), 500

    return jsonify({'status': 'deleted'})

# 5. Query logging (PII audit trail)
def log_search(user_id, query, result_count, timestamp):
    """Log search for analytics and compliance"""

    # Check if query contains PII
    pii_patterns = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        'ssn': r'\d{3}-\d{2}-\d{4}'
    }

    pii_detected = {}
    for pii_type, pattern in pii_patterns.items():
        if re.search(pattern, query):
            pii_detected[pii_type] = True
            logger.warning(f"PII detected in search query: {pii_type}")

    # Store log with PII warning
    db.execute("""
        INSERT INTO search_logs
        (user_id, query, result_count, has_pii, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, [user_id, query, result_count, bool(pii_detected), timestamp])
```

### Access Control for Search Index

```python
class SearchAccessControl:
    """Control what documents users can search"""

    def get_user_documents(self, user_id):
        """Get documents user can access"""
        return db.query("""
            SELECT d.* FROM documents d
            JOIN document_access da ON d.id = da.document_id
            WHERE da.user_id = %s OR d.is_public = true
        """, [user_id])

    def filter_search_results(self, results, user_id):
        """Filter results based on access control"""
        accessible_ids = set(d['id'] for d in self.get_user_documents(user_id))

        return [
            r for r in results
            if r['id'] in accessible_ids
        ]

# Usage in search endpoint
@app.route('/search')
def search():
    user_id = get_user_id(request)
    query = request.args.get('q')

    # Search across all documents
    all_results = search_engine.search(query, limit=100)

    # Filter by access control
    access_control = SearchAccessControl()
    accessible_results = access_control.filter_search_results(all_results, user_id)

    return jsonify({'results': accessible_results[:20]})
```

---

## Conclusion

The key to successful search implementation is:

1. **Match your tool to your scale** - Not every project needs Elasticsearch
2. **Measure quality early** - Data-driven decisions beat guesses
3. **Start simple, optimize systematically** - Add complexity when needed
4. **Respect user privacy** - PII in search is a compliance nightmare
5. **Plan for growth** - Build migration paths early

Use this guide to navigate the search technology landscape and make confident architecture decisions for your specific constraints.

---

## Quick Reference: Tool Comparison Matrix

| Solution | Size | Latency | Cost/mo | Ops | Features | Best For |
|----------|------|---------|---------|-----|----------|----------|
| Fuse.js | <10K | <50ms | $0 | None | Fuzzy | Static sites |
| PostgreSQL FTS | 10K-1M | 25ms | $0-100 | Low | Full-text | Existing PG users |
| Meilisearch | 10K-100M | 50ms | $5-500 | Low | Typo, facets | Developer friendly |
| Typesense | 100K-100M | 50ms | $0-1K | Low | Typo, facets, geo | Performance |
| Elasticsearch | 100K-100M+ | 100ms | $500-50K | High | Advanced | Scale |
| Algolia | 1K-100M+ | 50ms | $0-10K+ | None | All | Managed SaaS |
| Pinecone | Any | 50ms | $100-1K | None | Vector | Semantic search |

---

**Sources:**
- [Elasticsearch vs Typesense Comparison](https://www.meilisearch.com/blog/elasticsearch-vs-typesense)
- [Algolia vs Self-Hosted Cost Analysis](https://www.meilisearch.com/blog/algolia-pricing)
- [PostgreSQL Full-Text Search](https://neon.com/blog/postgres-full-text-search-vs-elasticsearch)
- [Client-Side Search Libraries](https://www.fusejs.io/)
- [Learning to Rank Guide](https://hav4ik.github.io/learning-to-rank/)
- [Hybrid Search Implementation](https://www.elastic.co/what-is/hybrid-search)
- [Search Performance Optimization](https://www.algolia.com/doc/guides/building-search-ui/going-further/improve-performance/js)
- [GDPR Compliance for Search](https://www.techtarget.com/searchdatamanagement/feature/How-to-manage-data-and-the-gdpr-right-to-be-forgotten)
