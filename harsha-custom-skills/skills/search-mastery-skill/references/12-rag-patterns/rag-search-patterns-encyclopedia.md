# RAG Patterns for Search: From Naive to Production-Grade Systems

**Comprehensive Encyclopedia of Retrieval-Augmented Generation Architectures and Techniques**

Last Updated: March 2026
Token Count: 3200+ words

---

## Table of Contents

1. Naive RAG & Core Limitations
2. Advanced RAG Techniques
3. Modular & Adaptive RAG
4. Chunking Strategies
5. Retrieval Methods
6. Document Processing Pipelines
7. Evaluation Frameworks
8. Production Patterns
9. RAG Frameworks Comparison
10. Agentic RAG Systems
11. Search-Specific RAG Applications

---

## 1. Naive RAG & Core Limitations

### What is Naive RAG?

Naive RAG represents the simplest implementation of retrieval-augmented generation, following a straightforward three-step pipeline:

1. **Embed** the user query and documents into vector space
2. **Retrieve** the top-k most similar documents using vector similarity
3. **Generate** a response by passing query + retrieved context to an LLM

```
User Query
    ↓
[Embedding Model]
    ↓
Vector Search (Cosine Similarity)
    ↓
Top-K Documents Retrieved
    ↓
[LLM with Context] → Response
```

### Critical Limitations of Naive RAG

Recent research reveals that naive RAG suffers from fundamental issues that limit its effectiveness in production systems.

#### Low Precision and Low Recall

The retrieval stage frequently fails to find relevant information. Systems struggle with:
- **Semantic mismatch**: The vector space may not align well between questions and answers
- **Abstract concept retrieval**: Models fail to retrieve documents based on proof techniques, methodologies, or higher-level concepts
- **Keyword-dependent failures**: Documents using synonyms or varied phrasing get missed

#### Hallucination Despite Grounding

Counter to conventional wisdom, **RAG does not prevent hallucinations**. Research shows that even with accurate and relevant retrieved content, LLMs can still generate outputs that directly contradict the provided context. This occurs through multiple mechanisms:

- **Parametric Knowledge Override**: The LLM relies on its internal knowledge rather than the retrieved context
- **Copying Head Failures**: Neural mechanisms designed to integrate external knowledge fail to properly retain or transfer that information
- **Context Distraction**: Models get distracted by irrelevant information and ignore relevant chunks

#### Outdated Information Handling

Retrieved documents may contain outdated information, especially in knowledge domains with rapid evolution. Without version tracking or recency weighting, the system propagates stale knowledge.

#### Root Cause Analysis (2025 Research)

Deep mechanistic analysis reveals that hallucinations in RAG systems stem from:
1. **Knowledge FFNs overemphasizing parametric knowledge** in the residual stream
2. **Copying Heads failing to integrate external knowledge** effectively
3. **Insufficient context weighting** relative to model priors

### Sources
- [Why RAG won't solve generative AI's hallucination problem](https://techcrunch.com/2024/05/04/why-rag-wont-solve-generative-ais-hallucination-problem/)
- [Hallucination Mitigation for Retrieval-Augmented LLMs: A Review](https://www.mdpi.com/2227-7390/13/5/856)
- [Retrieval-Augmented Generation: A Comprehensive Survey](https://arxiv.org/html/2506.00054v1)
- [ReDeEP: Detecting Hallucination via Mechanistic Interpretability](https://openreview.net/forum?id=ztzZDzgfrh)

---

## 2. Advanced RAG Techniques

Advanced RAG addresses naive RAG's limitations through three stages: pre-retrieval optimization, retrieval enhancement, and post-retrieval refinement.

### Architecture Diagram: Advanced RAG Pipeline

```
Query Input
    ↓
┌─────────────────────────────────────┐
│  PRE-RETRIEVAL OPTIMIZATION         │
├─────────────────────────────────────┤
│ • Query Rewriting                   │
│ • Hypothetical Document Embeddings  │
│ • Query Expansion                   │
│ • Multi-perspective Queries         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  RETRIEVAL ENHANCEMENT              │
├─────────────────────────────────────┤
│ • Hybrid Search (Dense + Sparse)    │
│ • Reranking Models                  │
│ • Multi-Vector Retrieval            │
│ • Contextual Retrieval              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  POST-RETRIEVAL REFINEMENT          │
├─────────────────────────────────────┤
│ • Context Compression               │
│ • Chunk Reordering                  │
│ • Prompt Optimization               │
│ • Relevance Filtering               │
└─────────────────────────────────────┘
    ↓
LLM Generation + Response
```

### Pre-Retrieval Techniques

#### Query Rewriting

Query rewriting uses an LLM to transform the original query before searching, addressing phrasing mismatches between questions and answer documents.

```python
# Query Rewriting Example
def rewrite_query(query: str, llm) -> str:
    prompt = f"""
    Rewrite this query to improve semantic alignment
    with documents that contain the answer:

    Original Query: {query}
    """
    return llm.generate(prompt)
```

#### Hypothetical Document Embeddings (HyDE)

HyDE addresses the semantic gap between questions and answers by having the LLM generate a hypothetical perfect answer, then embedding and searching for documents similar to that hallucination.

**Why it works**: The vector similarity between a question and answer is often lower than the similarity between an answer and a hypothetical answer.

```python
# HyDE Implementation
def hyde_retrieval(query: str, llm, retriever):
    # Step 1: Generate hypothetical document
    prompt = f"Generate a perfect answer to: {query}"
    hypothetical_doc = llm.generate(prompt)

    # Step 2: Embed and retrieve documents similar to the answer
    embedding = embed(hypothetical_doc)
    results = retriever.search(embedding)

    return results
```

#### Multi-Query Expansion

Generate multiple diverse reformulations of the same query and retrieve documents for all variants, then aggregate results.

```python
def multi_query_retrieval(query: str, llm, retriever, k=3):
    # Generate alternative queries
    prompt = f"""Generate {k} alternative formulations of this query:
    {query}
    Return as a numbered list."""

    alternative_queries = llm.generate(prompt)

    # Retrieve for all queries
    all_results = []
    for alt_query in alternative_queries:
        results = retriever.search(alt_query)
        all_results.extend(results)

    # Deduplicate and aggregate
    return deduplicate(all_results)
```

### Retrieval Enhancement

#### Hybrid Search: Dense + Sparse

Hybrid search combines:
- **Dense Retrieval** (semantic embeddings): Captures conceptual similarity
- **Sparse Retrieval** (BM25/keyword search): Captures exact term matches

Combining both methods improves recall significantly because if the dense retriever misses a document due to unusual phrasing, the sparse retriever may catch it via keyword matching, and vice versa.

```python
# Hybrid Search Implementation
from elasticsearch import Elasticsearch
import numpy as np

def hybrid_search(query: str, dense_embedder, es_client):
    # Dense retrieval
    query_embedding = dense_embedder.embed(query)
    dense_results = semantic_search(query_embedding)

    # Sparse retrieval (BM25)
    sparse_results = es_client.search(
        index="documents",
        body={"query": {"multi_match": {"query": query}}}
    )

    # Normalize scores and combine
    dense_scores = {doc['id']: score for doc, score in dense_results}
    sparse_scores = {doc['id']: score for doc, score in sparse_results}

    # Hybrid scoring (equal weight)
    combined_scores = {}
    for doc_id in set(dense_scores) | set(sparse_scores):
        combined_scores[doc_id] = (
            0.5 * normalize(dense_scores.get(doc_id, 0)) +
            0.5 * normalize(sparse_scores.get(doc_id, 0))
        )

    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
```

#### Reranking Models

After initial retrieval, reranker models reassess document relevance more accurately than the embedding model.

```python
# Reranking Example using Cross-Encoders
from sentence_transformers import CrossEncoder

def rerank_results(query: str, documents: list, reranker_model):
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    # Compute relevance scores
    scores = reranker.predict([
        [query, doc['text']] for doc in documents
    ])

    # Reorder by score
    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [doc for doc, score in ranked]
```

Empirical improvements: Hybrid pipelines achieve **18.5% improvement in Mean Reciprocal Rank**, significantly increasing the likelihood that the correct answer appears in the top position.

### Post-Retrieval Refinement

#### Context Compression

Instead of passing all retrieved text to the LLM, compress to essential information only, reducing token consumption and improving focus.

```python
def compress_context(documents: list, query: str, llm):
    compressed = []
    for doc in documents:
        prompt = f"""Extract only the information relevant to answering:

        Question: {query}
        Document: {doc['text']}

        Keep only essential facts, remove fluff."""

        compressed_text = llm.generate(prompt)
        compressed.append({**doc, 'text': compressed_text})

    return compressed
```

### Sources
- [Advanced RAG 06: Exploring Query Rewriting](https://medium.com/@florian_algo/advanced-rag-06-exploring-query-rewriting-23997297f2d1)
- [HyDE: Hypothetical Document Embeddings](https://medium.com/data-science/how-to-use-hyde-for-better-llm-rag-retrieval-a0aa5d0e23e8)
- [Hybrid Search for RAG](https://www.meilisearch.com/blog/hybrid-search-rag)
- [DMQR-RAG: Diverse Multi-Query Rewriting](https://arxiv.org/html/2411.13154v1)

---

## 3. Modular & Adaptive RAG

### Modular RAG Architecture

Modular RAG decomposes the RAG pipeline into composable, interchangeable components rather than a rigid linear flow.

```
┌─────────────────────────────────┐
│  Query Routing Module           │
│  - Analyze query complexity     │
│  - Route to appropriate path    │
└──────────┬──────────────────────┘
           │
    ┌──────┴─────────┬──────────────────┐
    ↓                ↓                  ↓
[Simple      [Multi-hop         [External
 Retrieval]  Reasoning]         Search]
    │                │                  │
    └──────┬─────────┴──────────────────┘
           ↓
┌─────────────────────────────────┐
│  Retrieval Module Options       │
│  (Pluggable):                   │
│  - Dense Retrieval              │
│  - Hybrid Search                │
│  - Graph Traversal              │
│  - Web Search Integration       │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Reranking Module (Optional)    │
│  - Cross-encoder reranking      │
│  - Relevance filtering          │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Generation Module              │
│  (Pluggable LLMs)               │
└─────────────────────────────────┘
```

### Key Modular Components

1. **Routing Module**: Directs queries to different retrieval strategies based on complexity analysis
2. **Pluggable Retrievers**: Multiple retrieval backends can be swapped
3. **Optional Rerankers**: Relevance refinement without mandatory dependency
4. **Flexible Generation**: Different LLMs for different scenarios

### Adaptive RAG: Dynamic Strategy Selection

Adaptive RAG enhances modularity by dynamically choosing retrieval strategies based on query characteristics.

```python
class AdaptiveRAG:
    def __init__(self, llm, retriever, classifier):
        self.llm = llm
        self.retriever = retriever
        self.classifier = classifier  # Classifies query complexity

    def process_query(self, query: str):
        # Classify query complexity
        complexity = self.classifier.predict(query)

        if complexity == "simple":
            # Use single-step retrieval
            docs = self.retriever.simple_retrieve(query)
        elif complexity == "multi_hop":
            # Use multi-step reasoning
            docs = self.multi_hop_retrieve(query)
        elif complexity == "reasoning_intensive":
            # Use external knowledge and reasoning
            docs = self.advanced_retrieve(query)
        else:
            # Skip retrieval for factual queries
            docs = []

        return self.llm.generate(query, docs)
```

### Sources
- [Modular RAG: Transforming RAG Systems into LEGO-like Frameworks](https://arxiv.org/html/2407.21059v1)
- [Adaptive Modular RAG](https://www.emergentmind.com/topics/adaptive-and-modular-retrieval-augmented-generation-rag)
- [Implementing Modular RAG with Haystack](https://towardsdatascience.com/implementing-modular-rag-with-haystack-and-hypster-d2f0ecc88b8f)

---

## 4. Chunking Strategies

Effective chunking is foundational to RAG success. Poor chunking leads to information loss, context fragmentation, and retrieval failures.

### Chunking Strategy Comparison

| Strategy | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| **Fixed-Size** | Split every N tokens | Simple, fast | Ignores semantic boundaries |
| **Recursive** | Hierarchical split by sections/paragraphs/sentences | Preserves structure | May leave some large semantic units |
| **Semantic** | Split at semantic boundaries using embeddings | Maximizes coherence | Computationally expensive |
| **Parent-Child** | Hierarchical with both small and full chunks | Balances detail and context | Added complexity |
| **Sentence-Window** | Sliding window of N sentences | Provides immediate context | May miss distant relationships |

### Semantic Chunking: Detailed Implementation

Semantic chunking splits text at natural conceptual boundaries by analyzing embedding similarities between consecutive sentences.

```python
from sentence_transformers import SentenceTransformer

def semantic_chunking(text: str, model_name: str = "all-MiniLM-L6-v2",
                     threshold: float = 0.5):
    """
    Split text at semantic boundaries using embeddings.
    """
    model = SentenceTransformer(model_name)

    # Tokenize into sentences
    sentences = sent_tokenize(text)

    # Generate embeddings for each sentence
    embeddings = model.encode(sentences)

    # Calculate similarity between consecutive sentences
    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = cosine_similarity(
            embeddings[i-1].reshape(1, -1),
            embeddings[i].reshape(1, -1)
        )[0][0]

        # If similarity drops below threshold, start new chunk
        if similarity < threshold:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])

    # Add final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
```

### Recursive Chunking: Hierarchical Approach

Recursive chunking applies splitting rules hierarchically to preserve document structure.

```python
def recursive_chunking(text: str, separators: list, chunk_size: int = 1000):
    """
    Recursively split text using multiple separators while preserving structure.

    Args:
        text: Input text
        separators: Hierarchy of separators ["\n\n", "\n", ". ", " "]
        chunk_size: Target chunk size in characters
    """
    chunks = []
    good_splits = []

    for separator in separators:
        if separator in text:
            splits = text.split(separator)
            good_splits = [s for s in splits if len(s) < chunk_size]

            if good_splits:
                # Recursively process good splits
                for split in good_splits:
                    if len(split) > chunk_size:
                        chunks.extend(recursive_chunking(
                            split, separators[separators.index(separator)+1:], chunk_size
                        ))
                    else:
                        chunks.append(split)
                break

    if not good_splits:
        chunks.append(text)

    return chunks
```

### Parent-Child Chunking: Hierarchical Retrieval

Parent-child chunking stores small chunks for retrieval but returns larger parent chunks for context.

```python
class ParentChildChunking:
    def __init__(self, child_chunk_size: int = 256, parent_chunk_size: int = 1024):
        self.child_size = child_chunk_size
        self.parent_size = parent_chunk_size

    def create_chunks(self, text: str):
        # Create parent chunks
        parent_chunks = [
            text[i:i+self.parent_size]
            for i in range(0, len(text), self.parent_size-100)  # 100 char overlap
        ]

        chunks_with_parents = []
        for parent_idx, parent in enumerate(parent_chunks):
            # Create child chunks within parent
            children = [
                parent[j:j+self.child_size]
                for j in range(0, len(parent), self.child_size-50)  # 50 char overlap
            ]

            for child in children:
                chunks_with_parents.append({
                    'text': child,
                    'parent_id': parent_idx,
                    'parent_text': parent
                })

        return chunks_with_parents

    def retrieve(self, query_embedding, index, k: int = 3):
        # Retrieve top-k child chunks
        child_results = index.search(query_embedding, k=k)

        # Return parent chunks instead
        parent_chunks = {}
        for result in child_results:
            parent_id = result['parent_id']
            if parent_id not in parent_chunks:
                parent_chunks[parent_id] = result['parent_text']

        return list(parent_chunks.values())
```

### Sources
- [Chunking Strategies to Improve RAG Performance](https://www.nb-data.com/p/9-chunking-strategis-to-improve-rag)
- [Semantic Chunking for RAG](https://medium.com/the-ai-forum/semantic-chunking-for-rag-f4733025d5f5)
- [The Ultimate Guide to Chunking Strategies](https://community.databricks.com/t5/technical-blog/the-ultimate-guide-to-chunking-strategies-for-rag-applications/ba-p/113089)
- [Weaviate: Chunking Strategies for RAG](https://weaviate.io/blog/chunking-strategies-for-rag)

---

## 5. Advanced Retrieval Methods

### Hybrid Retrieval: Dense + Sparse + Reranking

```python
class HybridRetriever:
    def __init__(self, dense_model, sparse_index, reranker, weights=None):
        self.dense = dense_model
        self.sparse = sparse_index
        self.reranker = reranker
        self.weights = weights or {'dense': 0.5, 'sparse': 0.5}

    def retrieve(self, query: str, k: int = 10):
        # Dense retrieval
        query_emb = self.dense.embed(query)
        dense_results = self.dense.search(query_emb, k=k*2)  # Overretrieval

        # Sparse retrieval
        sparse_results = self.sparse.search(query, k=k*2)

        # Normalize and combine scores
        combined = self.combine_results(dense_results, sparse_results)

        # Rerank top candidates
        top_candidates = combined[:k*2]
        reranked = self.reranker.rank(query, top_candidates)

        return reranked[:k]

    def combine_results(self, dense, sparse):
        # Normalize and combine scores
        scores = {}

        for i, (doc, score) in enumerate(dense):
            scores[doc['id']] = self.weights['dense'] * (1 - i/len(dense))

        for i, (doc, score) in enumerate(sparse):
            doc_id = doc['id']
            scores[doc_id] = scores.get(doc_id, 0) + self.weights['sparse'] * (1 - i/len(sparse))

        return sorted(
            [(doc, score) for doc, score in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
```

### Multi-Hop Retrieval for Complex Reasoning

Multi-hop retrieval iteratively refines queries based on intermediate results.

```python
class MultiHopRetriever:
    def __init__(self, retriever, llm, max_hops: int = 3):
        self.retriever = retriever
        self.llm = llm
        self.max_hops = max_hops

    def retrieve(self, query: str):
        results = []
        current_query = query

        for hop in range(self.max_hops):
            # Retrieve documents
            docs = self.retriever.search(current_query)
            results.extend(docs)

            # Check if we have sufficient information
            accumulated_context = "\n".join([doc['text'] for doc in results])
            is_complete = self.llm.evaluate_completeness(query, accumulated_context)

            if is_complete:
                break

            # Refine query based on retrieved context
            current_query = self.llm.refine_query(
                query, accumulated_context
            )

        return results
```

### Graph-Based Retrieval

Graph-based methods traverse knowledge graphs to find answers through entity relationships.

```python
class GraphRetriever:
    def __init__(self, graph_db):
        self.graph = graph_db

    def retrieve(self, query: str, max_depth: int = 2):
        # Extract entities from query
        entities = self.extract_entities(query)

        # Traverse graph from source entities
        retrieved_docs = set()
        to_visit = [(entity, 0) for entity in entities]
        visited = set()

        while to_visit:
            current_entity, depth = to_visit.pop(0)
            if current_entity in visited or depth > max_depth:
                continue

            visited.add(current_entity)

            # Get all documents connected to this entity
            connected_docs = self.graph.get_connected_documents(current_entity)
            retrieved_docs.update(connected_docs)

            # Get related entities for next hop
            related_entities = self.graph.get_related_entities(current_entity)
            for entity in related_entities:
                if entity not in visited:
                    to_visit.append((entity, depth + 1))

        return list(retrieved_docs)

    def extract_entities(self, query: str):
        # Use NER or LLM to extract entities
        pass
```

### Sources
- [Hybrid Search for RAG](https://apxml.com/courses/optimizing-rag-for-production/chapter-2-advanced-retrieval-optimization/hybrid-search-rag)
- [Graph-enhanced Agent for Retrieval](https://aclanthology.org/2025.findings-acl.624.pdf)
- [Dense–Sparse Hybrid Retrieval](https://www.emergentmind.com/topics/dense-sparse-hybrid-retrieval)

---

## 6. Document Processing Pipeline

A robust document processing pipeline converts raw documents (PDFs, DOCX, tables, images) into clean, structured chunks ready for embedding and retrieval.

```
Raw Documents (PDF, DOCX, Images)
    ↓
┌─────────────────────────┐
│ File Parsing            │
│ - PDF extraction        │
│ - DOCX parsing          │
│ - Layout analysis       │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│ Layout & Structure      │
│ - Identify sections     │
│ - Extract headers       │
│ - Detect tables         │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│ Table Extraction        │
│ - Detect table bounds   │
│ - Extract cells         │
│ - Preserve structure    │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│ OCR (for images)        │
│ - Extract text from img │
│ - Handle scanned PDFs   │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│ Text Cleaning           │
│ - Remove noise          │
│ - Normalize formatting  │
│ - Handle special chars  │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│ Metadata Enrichment     │
│ - Add source file       │
│ - Add page numbers      │
│ - Timestamp creation    │
└────────┬────────────────┘
         ↓
┌─────────────────────────┐
│ Chunking                │
│ - Apply chunking strat. │
│ - Create chunks         │
└────────┬────────────────┘
         ↓
Clean, Structured Chunks Ready for Embedding
```

### Implementation Example with Docling

Docling is a modern document processing library designed for AI-readiness.

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConvertedDocument

def process_documents(file_paths: list):
    """
    Process multiple document types using Docling.
    """
    converter = DocumentConverter()
    processed_docs = []

    for file_path in file_paths:
        # Convert document to structured format
        converted: ConvertedDocument = converter.convert(file_path)

        # Extract structured content
        for block in converted.document.body_blocks:
            if block.type == "table":
                table_data = extract_table_structure(block)
                processed_docs.append({
                    'type': 'table',
                    'source': file_path,
                    'content': table_data,
                    'page': block.page
                })
            elif block.type == "text":
                processed_docs.append({
                    'type': 'text',
                    'source': file_path,
                    'content': block.text,
                    'page': block.page
                })
            elif block.type == "image":
                # Apply OCR to image
                text = ocr_image(block.image)
                processed_docs.append({
                    'type': 'image',
                    'source': file_path,
                    'content': text,
                    'page': block.page
                })

    return processed_docs

def extract_table_structure(table_block):
    """
    Extract table as structured data (rows, columns).
    """
    rows = []
    for row in table_block.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.text)
        rows.append(row_data)

    return {
        'rows': rows,
        'columns': len(rows[0]) if rows else 0
    }
```

### Metadata Enrichment Strategy

```python
class DocumentEnricher:
    def __init__(self):
        self.metadata_fields = [
            'source_file',
            'page_number',
            'section',
            'creation_date',
            'chunk_index',
            'chunk_type'  # table, text, list, etc.
        ]

    def enrich_chunks(self, chunks: list, source_file: str, metadata: dict):
        """
        Add metadata to chunks for better tracking and retrieval.
        """
        enriched = []
        for idx, chunk in enumerate(chunks):
            enriched_chunk = {
                'text': chunk,
                'metadata': {
                    'source_file': source_file,
                    'chunk_index': idx,
                    'chunk_total': len(chunks),
                    'page_number': metadata.get('page_number'),
                    'section': metadata.get('section'),
                    'creation_date': metadata.get('creation_date'),
                    'chunk_type': self.detect_chunk_type(chunk)
                }
            }
            enriched.append(enriched_chunk)

        return enriched

    def detect_chunk_type(self, text: str):
        """Detect chunk type (table, code, list, paragraph)."""
        if self.is_table(text):
            return 'table'
        elif self.is_code(text):
            return 'code'
        elif self.is_list(text):
            return 'list'
        else:
            return 'paragraph'

    def is_table(self, text):
        return '|' in text and text.count('\n') > 2

    def is_code(self, text):
        return '```' in text or (text.count('\n') > 3 and '  ' in text)

    def is_list(self, text):
        return text.strip().startswith(('-', '*', '•')) or any(
            line.strip()[0].isdigit() for line in text.split('\n')
        )
```

### Sources
- [Docling: Get Your Documents Ready for GenAI](https://github.com/docling-project/docling)
- [Building a Production-Ready Document Ingestion Pipeline](https://medium.com/@shaafabdullah/building-a-production-ready-azure-document-ingestion-pipeline-8272a71fe142)
- [From PDFs to AI-ready Structured Data](https://explosion.ai/blog/pdfs-nlp-structured-data)

---

## 7. RAG Evaluation Framework: RAGAS

RAGAS (Retrieval-Augmented Generation Assessment) provides automated evaluation metrics without requiring gold-standard reference answers.

### Core Metrics

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)

def evaluate_rag_system(questions, generated_answers, retrieved_contexts, ground_truths=None):
    """
    Evaluate RAG system using RAGAS metrics.
    """

    # Dataset format
    dataset = {
        'question': questions,
        'answer': generated_answers,
        'contexts': [contexts for contexts in retrieved_contexts],
        'ground_truth': ground_truths  # Optional
    }

    # Available metrics
    metrics = [
        faithfulness,          # Factual consistency with context
        answer_relevancy,      # Answer relevance to question
        context_recall,        # Context contains info for ideal answer
        context_precision,     # Context ranked by relevance
    ]

    # Evaluate
    results = evaluate(dataset, metrics=metrics)

    return results.scores
```

### Metric Definitions

1. **Faithfulness (0-1)**: Measures factual consistency of the generated answer with retrieved context. Higher = better alignment.

2. **Answer Relevancy (0-1)**: Evaluates if the generated answer directly addresses the question.

3. **Context Recall (0-1)**: Assesses whether retrieved context contains all information needed for the ideal answer.

4. **Context Precision (0-1)**: Measures whether context documents are ranked correctly (higher relevance first).

### Implementation of Custom Metrics

```python
from ragas.metrics.base import Metric
from ragas.llm import LLMInterface

class CustomFaithfulnessMetric(Metric):
    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def score(self, row):
        """
        Score faithfulness by asking LLM if answer contradicts context.
        """
        prompt = f"""
        Given the context below, is the answer faithful (consistent) with the context?

        Context: {row['contexts']}
        Answer: {row['answer']}

        Reply with: YES or NO
        """

        response = self.llm.generate(prompt)
        return 1.0 if "YES" in response.upper() else 0.0
```

### Debugging RAG Performance with RAGAS

```python
class RAGDebugger:
    def __init__(self, evaluator):
        self.evaluator = evaluator

    def identify_failures(self, results):
        """
        Identify why RAG is failing.
        """

        failures = {
            'retrieval_failures': [],
            'generation_failures': [],
            'hallucinations': []
        }

        for result in results:
            # Low context_recall = retrieval failure
            if result['context_recall'] < 0.5:
                failures['retrieval_failures'].append(result)

            # Low answer_relevancy = generation failure
            elif result['answer_relevancy'] < 0.5:
                failures['generation_failures'].append(result)

            # Low faithfulness = hallucination
            elif result['faithfulness'] < 0.5:
                failures['hallucinations'].append(result)

        return failures
```

### Sources
- [RAGAS: Automated Evaluation of RAG](https://arxiv.org/html/2309.15217v1)
- [Evaluating RAG Applications with RAGAS](https://medium.com/data-science/evaluating-rag-applications-with-ragas-81d67b0ee31a)
- [Best Practices in RAG Evaluation](https://qdrant.tech/blog/rag-evaluation-guide/)

---

## 8. Production Patterns & Optimization

### Latency Optimization Architecture

Production RAG systems must achieve sub-second latencies. Typical breakdown:

- **Embedding Generation**: 10-20ms
- **Vector Search**: 30-50ms
- **Reranking**: 20-50ms
- **LLM Generation (to first token)**: 100-300ms
- **Total**: ~200-400ms

```python
import asyncio
from typing import List
import time

class OptimizedRAGPipeline:
    def __init__(self, embedding_model, retriever, reranker, llm):
        self.embedding = embedding_model
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
        self.embedding_cache = {}
        self.retrieval_cache = {}

    async def process_query(self, query: str):
        """
        Optimized query processing with parallelization and caching.
        """
        start_time = time.time()

        # Step 1: Check embedding cache
        if query in self.embedding_cache:
            query_embedding = self.embedding_cache[query]
        else:
            query_embedding = await self.embedding.embed_async(query)
            self.embedding_cache[query] = query_embedding

        # Step 2: Check retrieval cache
        cache_key = str(query_embedding)
        if cache_key in self.retrieval_cache:
            top_documents = self.retrieval_cache[cache_key]
        else:
            # Parallel retrieval: dense + sparse
            dense_task = asyncio.create_task(
                self.retriever.dense_search_async(query_embedding)
            )
            sparse_task = asyncio.create_task(
                self.retriever.sparse_search_async(query)
            )

            dense_results, sparse_results = await asyncio.gather(
                dense_task, sparse_task
            )

            # Combine results
            combined = self.combine_results(dense_results, sparse_results)
            top_documents = combined[:10]
            self.retrieval_cache[cache_key] = top_documents

        # Step 3: Rerank (can be parallelized if multiple rerankers)
        reranked = await self.reranker.rank_async(query, top_documents)

        # Step 4: Stream LLM response
        context = "\n".join([doc['text'] for doc in reranked[:5]])

        response_stream = await self.llm.generate_stream(query, context)

        end_time = time.time()
        return {
            'response': response_stream,
            'latency_ms': (end_time - start_time) * 1000,
            'documents': reranked[:5]
        }

    def combine_results(self, dense, sparse):
        # Normalize and combine
        pass
```

### Caching Strategies

Three-layer caching reduces latency and cost:

```python
class MultiLayerCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}  # In-memory cache
        self.embedding_cache = {}  # Embedding cache
        self.retrieval_cache = {}  # Retrieval results cache

    def get_or_compute_embedding(self, text: str, embedder):
        """
        Embedding caching: expensive, rarely changes.
        """
        cache_key = f"embedding:{hash(text)}"

        # Try in-memory
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Try Redis
        cached = self.redis.get(cache_key)
        if cached:
            embedding = json.loads(cached)
            self.embedding_cache[cache_key] = embedding
            return embedding

        # Compute
        embedding = embedder.embed(text)
        self.redis.setex(cache_key, 86400*30, json.dumps(embedding))  # 30 days
        self.embedding_cache[cache_key] = embedding

        return embedding

    def get_or_retrieve(self, query: str, retriever):
        """
        Retrieval result caching: common queries repeated.
        """
        cache_key = f"retrieval:{hash(query)}"

        # Try cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Retrieve
        results = retriever.search(query)
        self.redis.setex(cache_key, 3600, json.dumps(results))  # 1 hour

        return results

    def get_or_generate(self, prompt: str, llm):
        """
        LLM response caching: identical or very similar prompts.
        """
        cache_key = f"generation:{hash(prompt)}"

        cached = self.redis.get(cache_key)
        if cached:
            return cached.decode()

        response = llm.generate(prompt)
        self.redis.setex(cache_key, 7200, response)  # 2 hours

        return response
```

### Cost Analysis

Typical RAG cost breakdown (per query):

```
Embedding generation:    $0.00001 (1K tokens @ $0.02/1M)
Vector storage:          $0.0001 (storage + retrieval)
LLM inference:           $0.002 (500 tokens @ $0.004/1K)
Infrastructure:          $0.0001 (compute, storage)
─────────────────────────────
Total per query:         ~$0.0032

With caching (80% hit rate):
$0.0032 * 0.2 = ~$0.0006 per query
86% cost reduction
```

### Sources
- [Designing Production-Ready RAG Pipelines](https://hackernoon.com/designing-production-ready-rag-pipelines-tackling-latency-hallucinations-and-cost-at-scale)
- [RAGCache: Efficient Knowledge Caching](https://dl.acm.org/doi/10.1145/3768628)
- [Achieving Sub-Second Latency RAG Pipelines](https://www.rtinsights.com/real-time-rag-pipelines-achieving-sub-second-latency-in-enterprise-ai/)

---

## 9. RAG Frameworks Comparison

### LangChain vs LlamaIndex vs Haystack

| Aspect | LangChain | LlamaIndex | Haystack |
|--------|-----------|-----------|----------|
| **Primary Focus** | LLM chaining & orchestration | Data indexing & RAG | Search pipelines |
| **Architecture** | General-purpose workflows | Data-centric | Pipeline-based |
| **Learning Curve** | Steep (flexible, complex) | Gentle (high-level API) | Medium (opinionated) |
| **Latency** | ~10ms overhead | ~6ms overhead | ~5.9ms overhead |
| **Production Readiness** | Good | Good | Excellent |
| **Search-Specific Features** | Basic | Strong | Very strong |
| **Monitoring** | Manual | Manual | Built-in |

### Framework Code Examples

**LangChain RAG Example:**
```python
from langchain.chains import RetrievalQA
from langchain.retrievers import BM25Retriever
from langchain.llms import OpenAI

retriever = BM25Retriever.from_documents(documents)
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=retriever
)

answer = qa.run("What is RAG?")
```

**LlamaIndex RAG Example:**
```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

response = query_engine.query("What is RAG?")
```

**Haystack RAG Example:**
```python
from haystack import Pipeline, Document
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator

pipeline = Pipeline()
pipeline.add_component("retriever", InMemoryBM25Retriever(documents))
pipeline.add_component("generator", OpenAIGenerator())
pipeline.connect("retriever.documents", "generator.documents")

result = pipeline.run({"retriever": {"query": "What is RAG?"}})
```

### Sources
- [LlamaIndex vs LangChain vs Haystack: Which Should You Use?](https://kanerika.com/blogs/llamaindex-vs-langchain-vs-haystack/)
- [RAG Frameworks: LangChain vs LangGraph vs LlamaIndex](https://research.aimultiple.com/rag-frameworks/)
- [Best RAG Frameworks 2025: Benchmarks](https://langcopilot.com/posts/2025-09-18-top-rag-frameworks-2024-complete-guide)

---

## 10. Agentic RAG Systems

Agentic RAG embeds autonomous AI agents into the retrieval pipeline, enabling iterative refinement, multi-tool coordination, and self-correction.

### Agentic RAG Architecture

```
Query
  ↓
┌─────────────────────────────────┐
│  Agent Decision Loop            │
├─────────────────────────────────┤
│  1. Reflect on current state    │
│  2. Plan next action            │
│  3. Execute tool (retrieve)     │
│  4. Evaluate results            │
│  5. Continue or conclude        │
└─────────────────────────────────┘
  ↓
Multiple Retrieval Rounds
  ├─ Retrieve relevant documents
  ├─ Evaluate relevance
  ├─ Refine query if needed
  └─ Accumulate evidence
  ↓
Synthesize Final Answer
```

### Self-Reflective RAG (SELF-RAG)

SELF-RAG uses the LLM to self-evaluate whether retrieval is needed and whether generated text is supported by context.

```python
class SelfReflectiveRAG:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def generate_with_reflection(self, query: str):
        """
        Generate response with self-reflection about retrieval necessity
        and answer quality.
        """

        # Step 1: Decide if retrieval is needed
        decide_prompt = f"""
        Do you need to retrieve documents to answer this question well?

        Question: {query}

        Answer YES or NO.
        """

        need_retrieval = "YES" in self.llm.generate(decide_prompt).upper()

        documents = []
        if need_retrieval:
            documents = self.retriever.search(query)

        # Step 2: Generate answer
        if documents:
            context = "\n".join([doc['text'] for doc in documents[:3]])
            gen_prompt = f"""
            Answer based on the context provided:

            Context: {context}
            Question: {query}
            """
        else:
            gen_prompt = f"Answer the following question: {query}"

        answer = self.llm.generate(gen_prompt)

        # Step 3: Self-evaluate answer quality
        eval_prompt = f"""
        Is this answer well-supported by the documents and accurate?

        Question: {query}
        Answer: {answer}
        Context: {context if documents else "No context retrieved"}

        Rate on scale 1-5.
        """

        quality_score = self.llm.generate(eval_prompt)

        return {
            'answer': answer,
            'quality_score': quality_score,
            'documents_used': len(documents),
            'needed_retrieval': need_retrieval
        }
```

### Corrective RAG

Corrective RAG employs specialized agents to evaluate and fix retrieval failures.

```python
class CorrectiveRAG:
    def __init__(self, llm, retriever, web_search):
        self.llm = llm
        self.retriever = retriever
        self.web_search = web_search

    def correct_retrieval(self, query: str):
        """
        Five-agent system for corrective RAG.
        """

        # Agent 1: Initial retrieval
        documents = self.retriever.search(query)

        # Agent 2: Evaluate relevance
        relevant_docs = self.evaluate_relevance(query, documents)

        if len(relevant_docs) < 3:  # Insufficient relevant documents
            # Agent 3: Rewrite query
            refined_query = self.refine_query(query)
            documents = self.retriever.search(refined_query)

            # Re-evaluate
            relevant_docs = self.evaluate_relevance(refined_query, documents)

        if len(relevant_docs) < 2:  # Still insufficient
            # Agent 4: Web search fallback
            web_results = self.web_search(query)
            documents.extend(web_results)
            relevant_docs = self.evaluate_relevance(query, documents)

        # Agent 5: Synthesize validated information
        answer = self.synthesize_answer(query, relevant_docs)

        return answer

    def evaluate_relevance(self, query: str, documents: list):
        """
        Evaluate which documents are relevant.
        """
        relevant = []
        for doc in documents:
            prompt = f"""
            Is this document relevant to answering the question?

            Question: {query}
            Document: {doc['text'][:500]}

            Answer: YES or NO
            """

            if "YES" in self.llm.generate(prompt).upper():
                relevant.append(doc)

        return relevant

    def refine_query(self, query: str):
        """Rewrite query for better retrieval."""
        prompt = f"""
        Rewrite this query to be more specific and retrievable:
        Original: {query}
        """
        return self.llm.generate(prompt)

    def synthesize_answer(self, query: str, documents: list):
        """Synthesize final answer from validated documents."""
        context = "\n".join([doc['text'] for doc in documents])
        prompt = f"""
        Based on the documents, answer the question:

        Documents: {context}
        Question: {query}
        """
        return self.llm.generate(prompt)
```

### Sources
- [Agentic Retrieval-Augmented Generation: A Survey](https://arxiv.org/html/2501.09136v3)
- [Agentic RAG: A Self-Corrective Method](https://medium.com/@bhuvaneswari.subramani/agentic-rag-a-self-corrective-method-for-implementing-retrieval-augmented-generation-d6bbd583446f)
- [Self-Reflective RAG with LangGraph](https://blog.langchain.com/agentic-rag-with-langgraph/)

---

## 11. Search-Specific RAG Applications

RAG transforms traditional search systems by adding semantic understanding and answer generation capabilities.

### Answer Box Generation using RAG

```python
class SearchAnswerGenerator:
    def __init__(self, retriever, llm, reranker):
        self.retriever = retriever
        self.llm = llm
        self.reranker = reranker

    def generate_answer_box(self, query: str):
        """
        Generate a featured answer box for search results.
        """

        # Retrieve relevant documents
        documents = self.retriever.search(query, k=20)

        # Rerank for highest quality
        top_docs = self.reranker.rank(query, documents)[:5]

        # Extract factual answer
        extract_prompt = f"""
        Extract a concise, factual answer to this question from the documents.
        If no clear answer exists, respond with "No clear answer found."

        Question: {query}

        Documents:
        {chr(10).join([doc['text'][:300] for doc in top_docs])}

        Answer (1-2 sentences):
        """

        answer = self.llm.generate(extract_prompt)

        # Extract knowledge panel facts
        facts = self.extract_facts(query, top_docs)

        # Create answer box structure
        return {
            'answer': answer,
            'source': top_docs[0]['source'],
            'facts': facts,
            'confidence': self.assess_confidence(query, top_docs)
        }

    def extract_facts(self, query: str, documents: list):
        """Extract key facts from documents."""
        facts_prompt = f"""
        Extract 3-5 key facts about {query}:

        {chr(10).join([doc['text'][:200] for doc in documents])}

        Return as a bullet list.
        """
        return self.llm.generate(facts_prompt)

    def assess_confidence(self, query: str, documents: list):
        """Assess confidence in the answer."""
        confidence_prompt = f"""
        How confident are you that the retrieved documents
        can answer this question well?

        Question: {query}
        Document relevance: {documents[0]['score']}

        Rate 1-5.
        """
        return self.llm.generate(confidence_prompt)
```

### Featured Snippets Optimization

```python
class SnippetOptimizer:
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever

    def generate_optimized_snippet(self, query: str, document: str, context_length: int = 200):
        """
        Generate optimized snippet that directly answers the question.
        """

        # Identify answer location in document
        answer_prompt = f"""
        Find the sentence or paragraph that best answers this question:

        Question: {query}
        Document: {document}

        Return only the answer text.
        """

        answer_text = self.llm.generate(answer_prompt)

        # Expand context around answer
        answer_start = document.find(answer_text)
        context_start = max(0, answer_start - context_length // 2)
        context_end = min(len(document), answer_start + len(answer_text) + context_length // 2)

        snippet = document[context_start:context_end]

        # Clean up
        snippet = snippet.strip()
        if not snippet.startswith(answer_text):
            snippet = "... " + snippet
        if context_end < len(document):
            snippet = snippet + " ..."

        return snippet
```

### Contextual Search Results Enhancement

```python
class ContextualSearch:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def enhance_search_results(self, query: str, results: list):
        """
        Enhance traditional search results with semantic understanding.
        """

        enhanced_results = []
        for result in results:
            # Get full document for context extraction
            full_doc = self.retriever.get_document(result['doc_id'])

            # Generate contextual summary
            summary_prompt = f"""
            Write a 2-sentence summary of how this document answers the question.

            Question: {query}
            Document Title: {result['title']}
            Document: {full_doc[:500]}
            """

            context_summary = self.llm.generate(summary_prompt)

            # Extract related queries
            related_prompt = f"""
            What are 2-3 related questions someone might ask after reading this?

            Question: {query}
            Document: {full_doc[:300]}

            Return as a list.
            """

            related_queries = self.llm.generate(related_prompt)

            enhanced_results.append({
                **result,
                'context_summary': context_summary,
                'related_queries': related_queries,
                'relevance_explanation': self.explain_relevance(query, full_doc)
            })

        return enhanced_results

    def explain_relevance(self, query: str, document: str):
        """Explain why a document is relevant."""
        prompt = f"""
        In one sentence, explain why this document is relevant to the question.

        Question: {query}
        Document: {document[:200]}
        """
        return self.llm.generate(prompt)
```

### Sources
- [Advanced RAG Techniques: Querying & Testing](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2)
- [Contextual Retrieval in RAG](https://blog.box.com/contextual-retrieval-in-retrieval-augmented-generation-rag)
- [Improving RAG Accuracy: 10 Techniques](https://redis.io/blog/10-techniques-to-improve-rag-accuracy/)

---

## Conclusion

RAG has evolved from a simple three-step process (naive RAG) to sophisticated multi-stage systems incorporating:

- **Pre-retrieval optimization** (query rewriting, HyDE)
- **Advanced retrieval** (hybrid search, reranking)
- **Post-retrieval refinement** (compression, reordering)
- **Agentic capabilities** (self-reflection, correction)
- **Production patterns** (caching, streaming, monitoring)

The most effective RAG systems in production combine:
1. Semantic chunking for coherent document units
2. Hybrid retrieval (dense + sparse) for comprehensive coverage
3. Reranking for precision
4. Caching for latency/cost reduction
5. Evaluation frameworks (RAGAS) for continuous improvement
6. Agentic loops for error correction
7. Modular architecture for flexibility

Success requires treating RAG not as a black box but as an orchestrated system where each component contributes to overall quality, latency, and cost objectives.

---

## References & Further Reading

- [Retrieval-Augmented Generation: A Comprehensive Survey](https://arxiv.org/html/2506.00054v1)
- [Agentic Retrieval-Augmented Generation: A Survey](https://arxiv.org/html/2501.09136v3)
- [RAG Evaluation Metrics: Comprehensive Guide](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more)
- [Prompt Engineering Guide: RAG](https://www.promptingguide.ai/research/rag)
- [Neo4j: Advanced RAG Techniques](https://neo4j.com/blog/genai/advanced-rag-techniques/)

---

**End of Encyclopedia**
Generated: March 2026
Word Count: 3,200+

---

## See Also (Cross-References)

→ **references/00-search-recipes/** — Recipe #4: RAG Pipeline with Agentic Retrieval provides end-to-end implementation
→ **references/00-benchmark-matrix/** — RAG accuracy comparison table (naive vs CRAG vs agentic)
→ **references/00-migration-playbooks/** — Playbook #7: Naive RAG → Agentic RAG shows progression path
→ **references/40-agentic-rag-self-reflective/** — Agentic RAG/CRAG for self-correction and verification
→ **references/45-neural-reranking-distillation/** — Rerank before sending to LLM for improved accuracy
→ **references/38-multi-hop-reasoning/** — Multi-hop retrieval for complex, multi-step queries
→ **references/35-embeddings-deep-dive/** — Embedding model selection critical for RAG quality
