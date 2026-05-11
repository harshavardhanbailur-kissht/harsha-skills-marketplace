# Search Indexing Pipelines and Data Ingestion: A Comprehensive Reference

## Table of Contents

1. [ETL/ELT Patterns for Search](#etlelt-patterns-for-search)
2. [Web Crawlers and Crawling Strategies](#web-crawlers-and-crawling-strategies)
3. [Document Processing and Text Extraction](#document-processing-and-text-extraction)
4. [Text Processing Pipeline](#text-processing-pipeline)
5. [Embedding Generation and Chunking](#embedding-generation-and-chunking)
6. [Real-Time vs Batch Indexing](#real-time-vs-batch-indexing)
7. [Schema Design and Index Mapping](#schema-design-and-index-mapping)
8. [Data Quality in Search Systems](#data-quality-in-search-systems)
9. [Index Management and Optimization](#index-management-and-optimization)
10. [Monitoring and Error Handling](#monitoring-and-error-handling)

---

## ETL/ELT Patterns for Search

### Overview

The foundation of any search indexing pipeline depends on how you extract, transform, and load data. Two primary patterns dominate modern data infrastructure: ETL (Extract-Transform-Load) and ELT (Extract-Load-Transform).

### ETL: Extract-Transform-Load

**Definition and Flow:**
ETL is the traditional approach where data transformation occurs on a separate processing server before loading into the destination system. The process follows a sequential pattern: Extract → Transform → Load.

**Key Characteristics:**
- Data transformation occurs in staging environments before ingestion
- Optimal for compute-intensive transformations
- Effective for small to medium datasets requiring complex processing
- Well-suited for legacy systems with limited computational resources
- Supports data quality checks and validation before loading

**Search Indexing Use Cases:**
- Document preprocessing and content extraction from complex formats
- Sensitive data masking and PII redaction before indexing
- Complex schema normalization and field mapping
- Language detection and encoding conversion before indexing
- Metadata enrichment in staging environments

**Advantages:**
- Full control over transformation logic
- Data quality assurance before indexing
- Audit trails and compliance-friendly approach
- Minimal compute requirements on target system

**Disadvantages:**
- Processing bottlenecks during heavy transformation stages
- Delayed availability of data for search
- Separate infrastructure required for staging
- Higher operational overhead

### ELT: Extract-Load-Transform

**Definition and Flow:**
ELT reverses the ETL sequence, loading raw data directly into the destination system (Elasticsearch, vector databases, etc.) and performing transformations in-place using the target system's computational power.

**Key Characteristics:**
- Raw data loads directly into the search index or data warehouse
- Transformation logic executes within the destination system
- Leverages modern distributed systems for processing
- Enables rapid data availability
- Flexible schema management through post-load transformation

**Search Indexing Use Cases:**
- Large-scale dataset ingestion with lazy transformation
- Real-time indexing where immediate availability is critical
- Cloud-native deployments leveraging distributed systems
- Dynamic schema scenarios with evolving field requirements

**Advantages:**
- Faster data availability in search systems
- Scalable processing using target system resources
- Simplified pipeline architecture
- Better for rapidly evolving schemas

**Disadvantages:**
- Requires robust destination system capacity
- More difficult quality control pre-indexing
- Potential for index bloat with raw data
- Complex transformation logic in the search system

### Hybrid Approaches (2025 Best Practices)

Modern production systems increasingly adopt hybrid patterns combining ETL benefits with ELT flexibility:

**Stream-Based ETL:**
Apache Kafka and cloud messaging services enable continuous ETL where transformations occur in streaming pipelines. Data flows through transformation layers as it arrives, balancing real-time delivery with data quality.

**Micro-Transformation Layers:**
Breaking complex transformations into smaller, composable units allows systems to perform lightweight transformations in ELT while offloading expensive operations to dedicated ETL stages.

**Adaptive Pipeline Selection:**
High-value documents or complex schemas use ETL staging, while standard documents flow through ELT for speed. Real-time feeds use streaming ETL with Kafka, while historical data uses batch ETL.

### Document Processing Pipeline

The document processing pipeline is the first critical stage in indexing workflows:

```
Raw Document Input
    ↓
Format Detection (PDF, HTML, Office, etc.)
    ↓
Content Extraction (text, tables, metadata)
    ↓
Encoding Detection & Normalization
    ↓
Language Detection
    ↓
Metadata Extraction
    ↓
Structured Output (JSON, markdown)
```

**Key Steps:**

1. **Format Detection**: Identify document type (PDF, DOCX, HTML, XML, plain text)
2. **Content Extraction**: Extract text, tables, figures, and embedded data
3. **Encoding Detection**: Handle various character encodings (UTF-8, Latin-1, etc.)
4. **Metadata Extraction**: Extract title, author, creation date, and custom properties
5. **Structural Parsing**: Preserve document hierarchy and formatting context
6. **Quality Validation**: Check for extraction completeness and accuracy

---

## Web Crawlers and Crawling Strategies

### Crawler Architecture Overview

Web crawlers form the entry point for content acquisition in search systems. Modern crawlers must balance thoroughness with politeness, efficiency with accuracy.

### Major Crawler Frameworks

#### Scrapy (Python)

**Architecture:**
Scrapy is a pure-Python, asynchronous framework built atop Twisted, providing declarative spider definitions and built-in middleware for handling cookies, retries, and throttling.

**Key Features:**
- Asynchronous request handling for high throughput
- Declarative spider definitions using XPath and CSS selectors
- Built-in middleware for cookies, authentication, and retries
- Easy integration with data pipelines (MongoDB, Elasticsearch, databases)
- Request scheduling and deduplication
- Robust error handling and recovery

**Performance:**
- Handles thousands of requests per second per instance
- Distributed crawling support via Scrapy Cloud
- Memory-efficient for long-running crawls

**Best For:**
- Complex, multi-page crawling scenarios
- Custom data extraction logic
- Large-scale crawling operations
- Teams familiar with Python ecosystem

#### Colly (Go)

**Architecture:**
Colly is a lightweight Go-based crawler emphasizing speed and simplicity.

**Key Features:**
- Processes over 1,000 requests per second on a single core
- Lightweight middleware for proxy rotation and cookie management
- Fast HTTP performance from Go's concurrency model
- Minimal memory footprint
- Easy integration into Go applications

**Performance:**
- Extreme speed for straightforward crawling
- Excellent for high-volume, simple extraction tasks

**Best For:**
- High-performance crawling requirements
- Go ecosystem integration
- Minimal resource consumption scenarios
- Simple extraction patterns

#### Apache Nutch

**Architecture:**
Apache Nutch is a distributed web crawler built for enterprise-scale crawling and indexing operations.

**Key Features:**
- Distributed crawling over Hadoop clusters
- Plugin architecture for custom URL filtering and link analysis
- Real-time deduplication using bloom filters
- Adaptive crawling with politeness policies
- Integration with Solr and Elasticsearch for indexing
- Sophisticated robots.txt and sitemap handling

**Performance:**
- Scales to billions of pages
- Efficient resource utilization in distributed environments

**Best For:**
- Enterprise search engine deployments
- Large-scale web indexing
- Complex filtering and analysis requirements
- Organizations with Hadoop infrastructure

### Incremental Crawling

**Purpose:**
Incremental crawling revisits previously crawled pages to detect and capture updates without recrawling the entire web.

**Strategy:**
1. Maintain last-crawl timestamps for each URL
2. Use HTTP conditional requests (If-Modified-Since, ETag)
3. Prioritize frequently-changing content
4. Implement adaptive scheduling based on change frequency

**Implementation:**
- Track content fingerprints or hashes
- Monitor HTTP 304 Not Modified responses
- Adjust revisit schedules based on observed update patterns
- Use sitemap change frequency hints

### Crawl Scheduling

**Frequency Optimization:**
- High-value content: Daily or multiple times per day
- Standard content: Weekly to monthly
- Archive content: Quarterly or yearly
- Monitor change detection to avoid unnecessary crawls

**Politeness Policies:**

1. **Robots.txt Compliance**: Respect disallow rules and crawl-delay directives
2. **Crawl-Delay Headers**: Implement configurable delays between requests (2-10 seconds typical)
3. **User-Agent Declaration**: Identify crawler with descriptive user agent
4. **Request Distribution**: Spread requests across time to avoid server overload
5. **Sitemap Prioritization**: Use XML sitemaps to discover important URLs efficiently

**Sitemap-Based Crawling:**
- Parse XML sitemaps for URL discovery
- Respect priority and change frequency hints
- Use sitemap indexes for large sites
- Combine with robots.txt for complete crawl planning

---

## Document Processing and Text Extraction

### Multi-Format Content Extraction

Modern document processing must handle diverse formats, each with unique challenges.

#### PDF Processing

**Text Extraction Methods:**

1. **Native PDFs**: Extract text streams directly from PDF structure
   - Fast and accurate for born-digital PDFs
   - Preserves text order and formatting metadata
   - Challenges: Embedded fonts, special encodings

2. **Scanned PDFs**: Use OCR (Optical Character Recognition)
   - Required for scanned documents and images
   - Modern OCR supports 30+ languages
   - Vision Language Models (VLMs) like GPT-4 integrate text and image understanding
   - Accuracy: 85-98% depending on image quality and language

**Advanced Approaches:**
Vision-Language Models collapse traditional multi-tool pipelines into single models. Models like DeepSeek OCR and OpenAI's latest VLMs integrate text extraction with context-aware understanding, enabling more nuanced extraction.

#### HTML/Web Content

**Extraction Techniques:**
- DOM-based extraction: Parse HTML structure
- CSS selector targeting: Extract specific elements
- Text-only extraction: Strip markup and preserve structure
- Link extraction: Identify internal and external references
- Metadata extraction: Title, meta tags, structured data

**Tools:**
- Beautiful Soup (Python): DOM parsing and extraction
- jsdom/Cheerio (JavaScript): Server-side HTML processing
- Selenium/Playwright: JavaScript-rendered content

#### Office Documents (DOCX, PPTX, ODF)

**Structure:**
Office documents use ZIP-based XML formats enabling direct content extraction.

**Extraction Process:**
1. Unzip the document
2. Parse XML content files
3. Handle embedded media and cross-references
4. Preserve document hierarchy and formatting
5. Extract metadata from document properties

#### Specialized Formats

**Tools & Platforms (2025):**
- **MinerU**: Transforms complex PDFs into LLM-ready markdown/JSON
- **Docling**: Comprehensive document parsing for gen AI applications
- **Unstructured**: Enterprise data extraction with OCR and NLP
- **PDF-Extract-Kit**: High-quality PDF content extraction toolkit

### Encoding Detection and Normalization

**Character Encoding Challenges:**
Different documents use various character encodings (UTF-8, Latin-1, CP1252, etc.). Misdetection causes corruption and search failures.

**Detection Strategies:**
1. **Byte-Order Mark (BOM) Detection**: Check for UTF BOM sequences
2. **Declared Encoding**: Honor charset declarations in content
3. **Statistical Analysis**: Analyze byte distributions to infer encoding
4. **Language-Based Heuristics**: Use language detection to guess encoding

**Tools:**
- chardet (Python): Probabilistic encoding detection
- iconv: Character set conversion library
- ICU (International Components for Unicode): Comprehensive Unicode support

**Normalization Process:**
1. Detect original encoding
2. Convert to UTF-8 (internal standard)
3. Normalize Unicode forms (NFC, NFKC)
4. Handle combining characters
5. Remove invalid sequences

### Language Detection

**Importance:**
- Enables language-specific tokenization
- Drives stemming/lemmatization selection
- Supports multi-language search
- Optimizes OCR accuracy

**Detection Methods:**
1. **Declared Language**: HTML lang attribute, metadata
2. **Statistical Models**: N-gram analysis and language models
3. **Multiple Language Support**: Handle code-switching and mixed content

**Tools:**
- langdetect (Python): Fast language detection
- TextCat: Multi-language detection
- Azure Cognitive Services: Handles 100+ languages

### Deduplication: SimHash and MinHash

**Purpose:**
Prevent duplicate or near-duplicate documents from cluttering search indices, improving relevance and reducing storage.

#### SimHash Algorithm

**Concept:**
SimHash creates fingerprints preserving similarity relationships. Documents with similar hashes are likely duplicates or near-duplicates.

**Process:**
1. Tokenize document
2. Hash each token
3. Use hash bits to vote on fingerprint bits
4. Compute Hamming distance between fingerprints

**Advantages:**
- Fast computation
- Small fingerprint size (64-128 bits)
- Preserves similarity

**Limitations:**
- Limited to orthographic similarity
- Doesn't capture semantic similarity
- Less effective for structural duplicates

#### MinHash Algorithm

**Concept:**
MinHash estimates Jaccard similarity by creating signatures that preserve set similarity.

**Process:**
1. Tokenize document into set of shingles
2. Hash shingles with multiple hash functions
3. Keep minimum hash value for each function
4. Compare signatures for similarity estimation

**MinHash with LSH (Locality Sensitive Hashing):**
- Divide signatures into bands
- Hash bands to find probable matches
- Reduces comparison space from O(n²) to manageable size
- Tunable recall/precision/performance tradeoff

**Advantages:**
- Probabilistic similarity preservation
- Scales to trillion-scale datasets
- Tunable parameters for accuracy/speed

**2025 Tools:**
- **text-dedup**: PyPI package supporting MinHash, SimHash, SuffixArray
- **SemHash**: Fast multimodal semantic deduplication using embeddings
- **Milvus 2.6**: Built-in MinHash LSH for deduplication

---

## Text Processing Pipeline

### Pipeline Overview

The text processing pipeline transforms raw extracted text into searchable, meaningful index terms. The sequence of operations critically impacts search quality.

```
Raw Text Input
    ↓
Lowercasing/Case Normalization
    ↓
Tokenization
    ↓
Stop Word Removal
    ↓
Stemming/Lemmatization
    ↓
Synonym Expansion
    ↓
Indexed Terms
```

### Lowercasing and Case Normalization

**Purpose:**
Ensure "Word", "word", and "WORD" map to the same search term.

**Considerations:**
- Language-specific rules (some languages have complex lowercasing)
- Acronyms and proper nouns (decide whether to preserve)
- Acronym expansion ("FBI" → "federal bureau of investigation")

**Implementation:**
```python
# Basic lowercasing
text.lower()

# Unicode-aware lowercasing
import unicodedata
unicodedata.normalize('NFKD', text).lower()
```

### Tokenization

**Definition:**
Breaking text into individual tokens (words, punctuation, numbers).

**Methods:**

1. **Whitespace Tokenization**: Split on spaces
   - Simplest approach
   - Fails with punctuation and complex text
   - Useful for initial preprocessing

2. **Rule-Based Tokenization**: Use punctuation and whitespace rules
   - Handles common punctuation
   - Language-specific rules for abbreviations
   - Example: "don't" → ["don", "'t"] or ["don't"]

3. **Linguistic Tokenization**: Parse grammar and language structure
   - Handles complex cases (hyphenated words, contractions)
   - Language-specific and slower
   - Best for high-quality indexing

**Tools:**
- NLTK (Python): Comprehensive tokenization options
- spaCy: Linguistic tokenization with POS tagging
- Elasticsearch Tokenizer: Built-in flexible tokenization

### Stop Word Removal

**Purpose:**
Remove common, low-value words (the, a, an, is, etc.) to reduce index size and improve relevance.

**Standard Stop Words (English):**
a, about, after, again, all, am, an, and, any, are, as, at, be, because, been, being, but, by, can, could, did, do, does, doing, down, during, each, few, for, from, further, had, has, have, having, he, her, here, hers, herself, him, himself, his, how, i, if, in, into, is, it, its, itself, just, me, might, more, most, myself, no, nor, not, of, off, on, only, or, other, our, ours, ourselves, out, over, own, same, she, should, so, some, such, than, that, the, their, theirs, them, themselves, then, there, these, they, this, those, through, to, too, under, until, up, very, was, we, were, what, when, where, which, while, who, whom, why, with, you, your, yours, yourself, yourselves

**Considerations:**
- Language-specific stopwords
- Domain-specific adjustments (medical search may keep medical terms)
- Balance: Too many removes noise, too few bloats index

### Stemming vs. Lemmatization

#### Stemming

**Definition:**
Stemming reduces words to root forms through rule-based suffix removal.

**Process:**
- "running" → "runn"
- "jumped" → "jump"
- "happiness" → "happi"

**Characteristics:**
- Fast computation
- Produces valid or invalid word forms
- Rule-based, independent of dictionary
- Language-specific algorithms (Porter Stemmer for English)

**Advantages:**
- High performance
- Reduces vocabulary size
- Good for general search

**Disadvantages:**
- May produce non-existent words
- Over-stemming and under-stemming
- Less accurate than lemmatization

#### Lemmatization

**Definition:**
Lemmatization maps words to canonical forms (lemmas) using dictionary knowledge and morphological analysis.

**Process:**
- "running", "runs", "ran" → "run"
- "am", "is", "are" → "be"
- "better" → "good"

**Characteristics:**
- Dictionary-based morphological analysis
- Returns valid dictionary forms
- Language-specific rules (more complex than stemming)
- Slower but more accurate

**Advantages:**
- Accurate, valid word forms
- Better for specialized domains
- Handles irregular forms well

**Disadvantages:**
- Computational overhead
- Requires language-specific resources
- Slower than stemming

**Tools:**
- NLTK Snowball: Multiple language stemmers
- spaCy: Lemmatization with POS tagging
- WordNet: English lemmatization database
- Elasticsearch Analyzers: Built-in stemming/lemmatization

### Synonym Expansion

**Purpose:**
Connect related terms to improve recall (finding more relevant documents).

**Methods:**

1. **Dictionary-Based Synonyms:**
   - Predefined synonym lists
   - WordNet, thesaurus sources
   - Curated domain-specific synonyms
   - Examples: "car" ↔ "automobile", "begin" ↔ "start"

2. **Embedding-Based Synonyms:**
   - Use word embeddings (Word2Vec, GloVe, FastText)
   - Find nearest neighbors in embedding space
   - Dynamic, corpus-driven synonymy
   - Better captures context-specific relationships

3. **Query-Time vs. Index-Time:**
   - **Index-time expansion**: Add synonyms to index (increases size)
   - **Query-time expansion**: Expand at search time (slower queries)
   - Hybrid: Keep frequent synonyms at index time

**Implementation Considerations:**
- Ambiguous terms may have multiple meanings
- Bidirectional expansion (both directions?)
- Domain-specific synonymy
- Avoid over-expansion (performance impact)

---

## Embedding Generation and Chunking

### Embedding Fundamentals

Embeddings convert text into dense numerical vectors capturing semantic meaning, enabling:
- Semantic similarity search
- Clustering and classification
- Multi-modal search (text + images)
- Neural ranking and relevance

### Document Chunking Strategies

Before embedding documents, breaking them into manageable chunks is critical. Chunking strategy dramatically impacts search quality and retrieval cost.

#### Fixed-Size Chunking

**Approach:**
Split documents into fixed-length chunks (tokens, characters, or sentences).

**Methods:**
- Token-based: 256, 512, 1024 token chunks
- Character-based: 1000, 2000 character chunks
- Sentence-based: Fixed number of sentences

**Advantages:**
- Simple to implement
- Predictable overhead
- Easy to batch for inference
- Works across languages/domains

**Disadvantages:**
- May cut in middle of sentences/paragraphs
- Loses semantic structure
- Often suboptimal for retrieval

**Implementation:**
```python
# Token-based fixed chunking
def chunk_by_tokens(text, chunk_size=512, overlap=50):
    tokens = tokenize(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(' '.join(chunk))
    return chunks
```

#### Semantic Chunking

**Concept:**
Break documents at semantic boundaries (topic changes), preserving context and meaning.

**Process:**
1. Sentence segmentation
2. Embedding each sentence or sentence group
3. Compute similarity between consecutive groups
4. Identify boundaries where similarity drops (topic shift)
5. Create chunks respecting semantic boundaries

**Max-Min Semantic Chunking (2025 Innovation):**
- Maximize within-chunk semantic similarity
- Minimize between-chunk overlap
- Leads to 9% improved recall over fixed-size
- Production systems report 85-90% recall rates

**Advantages:**
- Respects semantic structure
- Better retrieval relevance
- Context preservation
- Language-independent

**Disadvantages:**
- Computational overhead (embeddings required)
- Variable chunk sizes
- Slower than fixed-size chunking

#### Recursive Chunking

**Concept:**
Hierarchically split text using multiple separators (paragraphs, lines, sentences, words), recursively subdividing oversized chunks.

**Separators (in order):**
1. Paragraph breaks "\n\n"
2. Line breaks "\n"
3. Sentence endings ". "
4. Words (spaces)

**Process:**
```
Split by paragraphs
    ↓
If chunk > max_size, split by lines
    ↓
If chunk > max_size, split by sentences
    ↓
If chunk > max_size, split by words
    ↓
Result: Semantically meaningful chunks respecting hierarchy
```

**Advantages:**
- Preserves document structure
- Semantic awareness without embedding cost
- 30-50% higher retrieval precision vs. fixed-size
- 2025 benchmark winner

**Performance (2025 Benchmarks):**
- Recursive token-based (R100-0): Highest precision/recall
- Produces chunks respecting paragraph structure
- 10-20% overlap recommended
- 400-512 token sweet spot for most domains

### Overlap Strategy

**Purpose:**
Overlap ensures context continuity between chunks, preventing information loss at boundaries.

**Recommended Settings:**
- 10-20% overlap typical for production
- 50-token overlap for 256-token chunks
- 100-token overlap for 512-token chunks
- Balance: More overlap = better context but larger index

### Embedding Model Selection

**Dense Embedding Models (2025):**
- OpenAI text-embedding-3 series: High performance, proprietary
- Open-source alternatives: Sentence-transformers (MiniLM, MPNet)
- Domain-specific: SciBERT (scientific), BioBERT (biomedical)
- Multi-lingual: mBERT, XLM-RoBERTa
- Latest: Vision-language models for multi-modal embedding

**Dimension Tradeoffs:**
- Higher dimensions (1536): Better accuracy, more storage/compute
- Smaller dimensions (384): Faster, less storage, acceptable quality
- Quantization: Reduce precision (int8) for 75% storage savings with minimal quality loss

### Batching and Inference Optimization

**Batching Strategy:**
- Group chunks for parallel embedding
- Batch size: 32-256 depending on model and GPU memory
- Trade-off: Larger batches are faster but require more memory

**GPU Utilization:**
- Enable mixed precision (FP16) for 2x speedup
- Distribute batches across GPUs
- Use TensorRT or ONNX for inference optimization
- Monitor: 80-90% GPU utilization target

**Inference Performance (Benchmarks):**
- 1000 chunks/minute on single GPU (512-dim embeddings)
- 10,000 chunks/minute with batch optimization
- Cost: ~$0.02 per 1M embeddings with cloud APIs

---

## Real-Time vs Batch Indexing

### Batch Indexing

**Characteristics:**
- Scheduled, large-scale indexing operations
- Process accumulated documents in bulk
- Simpler error recovery
- Lower cost per document
- Higher indexing latency (minutes to hours)

**Use Cases:**
- Initial index population
- Periodic content refreshes
- Full reindexing with schema changes
- Nightly content synchronization

**Architecture:**
```
Data Source
    ↓
Extract (hourly/daily)
    ↓
Transform
    ↓
Batch Load to Index
    ↓
Search Index Updated
```

**Best Practices:**
1. Schedule during low-traffic periods
2. Use temporary indices to avoid blocking reads
3. Merge indices afterward to consolidate
4. Monitor: Track total batch time and errors
5. Implement checkpointing for failure recovery

### Near-Real-Time Indexing

**Elasticsearch Refresh Mechanism:**
Documents become searchable after index refresh (default: 1 second). Increasing refresh interval improves indexing performance but delays document visibility.

**Refresh Configuration:**
```json
{
  "settings": {
    "refresh_interval": "1s"    // Default: 1 second
  }
}
```

**Tradeoffs:**
- `refresh_interval: 1s`: Near-real-time (default production)
- `refresh_interval: 5s`: Balanced (better throughput)
- `refresh_interval: 30s`: High throughput mode
- `refresh_interval: -1`: Disable (manual refresh only)

### Event-Driven Indexing with Kafka

**Architecture:**
```
Data Source
    ↓
Change Data Capture (CDC)
    ↓
Kafka Topic (event stream)
    ↓
Stream Processor (transform)
    ↓
Elasticsearch Connector
    ↓
Real-Time Index Updates
```

**Components:**

1. **Change Data Capture (Debezium):**
   - Capture database changes (inserts, updates, deletes)
   - Provide event streams to Kafka
   - Support: PostgreSQL, MySQL, MongoDB, Oracle

2. **Kafka Broker:**
   - Store event stream with configurable retention
   - Enable replayability for reindexing
   - Partition by document ID for ordering

3. **Stream Processor (optional):**
   - Apache Flink, Kafka Streams, Spark
   - Enrich events with additional data
   - Aggregate related updates
   - Complex transformations

4. **Elasticsearch Connector:**
   - Consume Kafka topics
   - Buffer documents for batching
   - Handle retries and failures
   - Update search index

**Performance Targets (2025):**
- End-to-end latency: 95th percentile < 5 seconds
- Throughput: 10,000-100,000 documents/second
- Consistency: Exactly-once delivery semantics

**Implementation Example:**
```json
{
  "name": "elasticsearch-connector",
  "config": {
    "connector.class": "com.elasticsearch.kafka.connect.sink.ElasticsearchSinkConnector",
    "topics": "documents",
    "connection.url": "http://elasticsearch:9200",
    "tasks.max": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "batch.size": "1000",
    "linger.ms": "5000"
  }
}
```

### Hybrid Batch + Real-Time

**Strategy:**
Combine batch and real-time for optimal performance:
- Batch: Bulk historical data, nightly refreshes
- Real-time: Fresh documents, user-generated content
- Separate indices merged in search

**Benefits:**
- Initial population via fast batch
- User-facing data stays current
- Efficient resource usage
- Flexibility in timing

---

## Schema Design and Index Mapping

### Elasticsearch Mapping Fundamentals

Mapping defines how documents and their fields are stored and indexed. It's the schema layer for Elasticsearch.

### Field Types

**Core Field Types:**

1. **String Types:**
   - `text`: Full-text searchable field (analyzed)
   - `keyword`: Exact match field (not analyzed)

2. **Numeric Types:**
   - `integer`, `long`: Whole numbers
   - `float`, `double`: Decimal numbers
   - Range queries supported

3. **Date Type:**
   - `date`: Date/timestamp values
   - Millisecond precision
   - Multiple format support

4. **Boolean Type:**
   - `boolean`: true/false values
   - Efficient storage and filtering

5. **Binary Type:**
   - `binary`: Base64-encoded binary data
   - Not searchable, useful for storage

6. **Complex Types:**
   - `object`: Nested JSON objects
   - `nested`: Arrays of objects with field preservation
   - `flattened`: Deeply nested structures

7. **Geo Types:**
   - `geo_point`: Latitude/longitude
   - `geo_shape`: Polygon and complex geometries

8. **Specialized Types:**
   - `completion`: Autocomplete suggestions
   - `token_count`: Count of analyzed tokens
   - `ip`: IP address values
   - `version`: Version numbers

### Dynamic Mapping

**Concept:**
Elasticsearch automatically detects field types and creates mappings for documents with new fields.

**Dynamic Field Detection:**
```
JSON value type → Elasticsearch field type
{} (object)       → object
[] (array)        → field type of first element
"string"          → text + keyword
123               → long
123.45            → double
true              → boolean
"2025-03-01"      → date (if format matches)
```

**Dynamic Setting Values:**
- `true` (default): Auto-detect and create fields
- `false`: Ignore unmapped fields
- `strict`: Reject documents with new fields
- `runtime`: Create runtime fields on unmapped fields

### Multi-Field Mappings

**Purpose:**
Index the same data in multiple ways for different query types.

**Common Pattern:**
```json
{
  "properties": {
    "title": {
      "type": "text",
      "analyzer": "standard",
      "fields": {
        "keyword": {
          "type": "keyword"
        },
        "raw": {
          "type": "keyword"
        }
      }
    }
  }
}
```

**Use Cases:**
- Full-text search via `title`
- Exact matching via `title.keyword`
- Sorting via `title.raw`
- Faceting via `title.keyword`

### Dynamic Templates

**Purpose:**
Control how new fields map based on matching conditions.

**Match Conditions:**
- `match_mapping_type`: Match detected data type
- `match` / `unmatch`: Pattern matching on field name
- `path_match` / `path_unmatch`: Pattern on full dotted path

**Example: Automatic Keyword Fields:**
```json
{
  "dynamic_templates": [
    {
      "strings_as_keywords": {
        "match_mapping_type": "string",
        "mapping": {
          "type": "keyword"
        }
      }
    }
  ]
}
```

**Example: Numeric Field Detection:**
```json
{
  "dynamic_templates": [
    {
      "numbers": {
        "match_mapping_type": "long",
        "mapping": {
          "type": "scaled_float",
          "scaling_factor": 100
        }
      }
    }
  ]
}
```

**Processing Order:**
- Templates processed sequentially
- First matching template wins
- Order dynamic_templates array for precedence

### Index Templates

**Purpose:**
Define default settings and mappings for indices matching a pattern.

**Use Cases:**
- Time-based indices (logs-2025-03-*)
- Multi-tenant systems (tenant-*-data)
- Environment-specific configurations (prod-*, test-*)

**Template Configuration:**
```json
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1,
    "refresh_interval": "5s"
  },
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" }
    }
  }
}
```

### Analyzer Configuration

**Text Analysis Pipeline:**
```
Input Text
    ↓
Character Filter (HTML stripping, etc.)
    ↓
Tokenizer (split into tokens)
    ↓
Token Filter (stemming, synonyms, etc.)
    ↓
Tokens (indexed terms)
```

**Built-in Analyzers:**
- `standard`: Default (tokenizer + lowercase + stop words)
- `simple`: Split on non-letters
- `whitespace`: Split on whitespace
- `language`: Language-specific (English, French, etc.)
- `keyword`: No analysis (exact match)

**Custom Analyzer Example:**
```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "custom_text": {
          "type": "custom",
          "char_filter": ["html_strip"],
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "custom_text"
      }
    }
  }
}
```

---

## Data Quality in Search Systems

### Handling Missing Fields

**Strategy:**
Missing fields are inevitable in real-world data. Decide how to handle them.

**Approaches:**

1. **Accept Missing Values:**
   - Leave field empty in index
   - Exclude from search/filtering queries
   - Track separately for analysis

2. **Default Values:**
   - Provide sensible defaults during indexing
   - Example: missing `price` → 0
   - Document default choices for consistency

3. **Field Imputation:**
   - Statistical imputation (mean, median for numbers)
   - Forward-fill for time-series data
   - Machine learning prediction for important fields

4. **Required Field Validation:**
   - Reject documents missing critical fields
   - Define minimum required fields per document type
   - Route invalid documents to manual review

### Data Normalization

**Text Normalization:**
- Lowercasing and case folding
- Unicode normalization (NFC, NFKC)
- Whitespace normalization (collapse multiple spaces)
- Punctuation handling (strip or preserve)

**Format Normalization:**

1. **Phone Numbers:**
   - Normalize: (555) 123-4567 → 5551234567
   - Strip formatting during indexing
   - Support international formats

2. **Addresses:**
   - Standardize: "St." vs "Street", "Dr." vs "Drive"
   - Parse components: street, city, state, zip
   - Geocoding for location search

3. **Dates:**
   - Parse multiple input formats
   - Convert to ISO 8601 (2025-03-01T10:30:00Z)
   - Handle timezones consistently

4. **Currency:**
   - Strip symbols and formatting
   - Convert to base unit (e.g., cents for USD)
   - Support multiple currencies with conversion

**Numeric Normalization:**
- Range normalization (0-1 scale)
- Log normalization for skewed distributions
- Scaling for machine learning features

### Entity Extraction During Indexing

**Purpose:**
Extract structured entities from unstructured text, enabling targeted search and filtering.

**Common Entities:**
- **Named Entities**: People, organizations, locations
- **Temporal Entities**: Dates, times, duration
- **Numeric Entities**: Money, percentages, measurements
- **Domain-Specific**: Product codes, medical terms, company stock symbols

**Extraction Methods:**

1. **Rule-Based:**
   - Regular expressions for patterns
   - Dictionary matching
   - Simple and fast

2. **NLP-Based:**
   - Named Entity Recognition (NER) models
   - spaCy, Stanford CoreNLP
   - More accurate for complex text

3. **ML Models:**
   - Fine-tuned BERT/RoBERTa for entity tasks
   - Domain-specific models for specialized entities
   - High accuracy but computational cost

**Implementation:**
```python
# Entity extraction example
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    entities = {}

    for ent in doc.ents:
        label = ent.label_  # PERSON, ORG, GPE, etc.
        if label not in entities:
            entities[label] = []
        entities[label].append(ent.text)

    return entities

# Index with extracted entities
doc = {
    "text": "John Smith works at OpenAI in San Francisco",
    "entities": extract_entities("John Smith works at OpenAI in San Francisco")
}
# Result: {"PERSON": ["John Smith"], "ORG": ["OpenAI"], "GPE": ["San Francisco"]}
```

### Data Enrichment Pipelines

**Enrichment Types:**

1. **External Data Lookups:**
   - Reverse geocoding (coordinates → address)
   - Company lookups (domain → company info)
   - Wikipedia enrichment (person → biography)

2. **Derived Metrics:**
   - Sentiment analysis
   - Text classification
   - Keyword extraction

3. **Relationship Building:**
   - Entity linking (coreference resolution)
   - Knowledge graph lookups
   - Related document suggestions

**Implementation Pattern:**
```
Index Document
    ↓
Extract Entities
    ↓
Lookup External Data
    ↓
Add Enriched Fields
    ↓
Re-Index
```

**Tools:**
- Azure Cognitive Search: Built-in enrichment skillsets
- Google Document AI: Enterprise document understanding
- Custom Python pipelines with external APIs

---

## Index Management and Optimization

### Index Lifecycle Management (ILM)

**Purpose:**
Automate index management through lifecycle phases based on age, size, or performance.

**Phases:**

1. **Hot Phase:**
   - Active indexing and searching
   - High refresh rates
   - Aggressive rollover policies
   - Typical duration: Hours to days

2. **Warm Phase:**
   - No new indexing
   - Read operations only
   - Lower refresh intervals
   - Optimized for cost
   - Typical duration: Days to weeks

3. **Cold Phase:**
   - Archive storage
   - Searchable but slow
   - Minimal CPU/memory
   - Searchable snapshots option
   - Typical duration: Weeks to months

4. **Frozen Phase:**
   - Fully archived, minimal resources
   - Searchable but very slow
   - Snapshot storage
   - Long-term retention
   - Typical duration: Months to years

5. **Delete Phase:**
   - Remove indices beyond retention
   - Compliance and cost management

**ILM Policy Example:**
```json
{
  "policy": "logs-lifecycle",
  "phases": {
    "hot": {
      "min_age": "0d",
      "actions": {
        "rollover": {
          "max_primary_shard_size": "50GB",
          "max_age": "1d"
        },
        "set_priority": {
          "priority": 100
        }
      }
    },
    "warm": {
      "min_age": "3d",
      "actions": {
        "set_priority": {
          "priority": 50
        },
        "shrink": {
          "number_of_shards": 1
        }
      }
    },
    "cold": {
      "min_age": "30d",
      "actions": {
        "searchable_snapshot": {
          "snapshot_repository": "s3-backup"
        }
      }
    },
    "delete": {
      "min_age": "365d",
      "actions": {
        "delete": {}
      }
    }
  }
}
```

### Reindexing Strategies

**When Reindexing is Needed:**
- Mapping changes
- Analyzer configuration updates
- Tokenizer modifications
- Field type changes
- Schema consolidation

**Blue-Green Reindexing (Zero-Downtime):**

```
Blue Index (Current/Production)
    ↓
Create Green Index (new schema)
    ↓
Reindex: Blue → Green
    ↓
Test Green Index
    ↓
Switch Alias: Blue → Green
    ↓
Green Index (New Production)
    ↓
Delete Blue Index
```

**Implementation:**
1. Create new index with updated mapping
2. Use reindex API to copy documents
3. Verify document count and spot-check results
4. Update alias to point to new index
5. Delete old index after verification

**Reindex API:**
```json
POST _reindex
{
  "source": {
    "index": "old-index"
  },
  "dest": {
    "index": "new-index"
  },
  "script": {
    "source": "ctx._source.new_field = ctx._source.old_field"
  }
}
```

**Handling Large Indices:**
- Use slices for parallel reindexing
- Monitor disk space during reindex
- Implement throttling to avoid resource exhaustion
- Plan for bandwidth requirements

### Index Aliases

**Purpose:**
Provide logical names for physical indices, enabling seamless index switching.

**Advantages:**
- Zero-downtime index updates
- A/B testing capability
- Gradual migration between indices
- Index version management

**Example:**
```json
POST _aliases
{
  "actions": [
    { "add": { "index": "new-index", "alias": "products" } },
    { "remove": { "index": "old-index", "alias": "products" } }
  ]
}
```

### Force Merge and Compaction

**Purpose:**
Merge segments to improve search performance and reduce storage for read-only indices.

**When to Force Merge:**
- After large reindex operations
- Moving indices to cold/frozen phases
- Preparing for backup/archive
- Regular maintenance on stable indices

**Configuration:**
```json
POST old-index/_forcemerge?max_num_segments=1
```

**Tradeoffs:**
- Improves search speed (fewer segments to search)
- Increases merge CPU/memory during operation
- Slows indexing temporarily
- Good for time-based indices after daily cutoff

**Best Practices:**
- Schedule during low-traffic periods
- Monitor CPU and memory usage
- Don't force merge to 1 segment on active indices (harms ongoing indexing)
- Archive indices: force merge to 1 segment

### Index Optimization

**Shard Sizing:**
- Too many shards: Overhead, slow queries
- Too few shards: Bottleneck, slow indexing
- Target: 30-50GB per shard for optimal performance

**Replica Strategy:**
- Production: 1-2 replicas (High Availability)
- Development: 0 replicas (Cost savings)
- Balance: Availability vs. resource usage

**Segment Management:**
```json
{
  "settings": {
    "index.merge.policy.segments_per_tier": 10,
    "index.merge.policy.max_merge_at_once": 5,
    "index.refresh_interval": "30s"
  }
}
```

---

## Monitoring and Error Handling

### Key Indexing Metrics

**Throughput Metrics:**
- Documents per second (target: 1,000-10,000 depending on setup)
- Bytes per second indexed
- Batches per second (if batch processing)

**Latency Metrics:**
- End-to-end latency (source to searchable)
- P50, P95, P99 latencies
- Queue depth and processing time

**Quality Metrics:**
- Document count vs. source count (verification)
- Error rate and types
- Reprocess rate (retry effectiveness)

**Resource Metrics:**
- CPU utilization (target: 50-80%)
- Memory usage and GC pauses
- Disk I/O and space usage
- Network throughput

### Indexing Lag Measurement

**Definition:**
Time between data source update and searchability in index.

**Measurement Points:**
1. Source timestamp (data creation)
2. Index timestamp (document indexed)
3. Refresh completion (document searchable)

**Formula:**
```
Lag = Searchable Timestamp - Source Timestamp
```

**Targets (by system):**
- Real-time systems: < 5 seconds (P95)
- Near-real-time: < 30 seconds
- Batch systems: Minutes to hours

**Monitoring Implementation:**
```json
{
  "monitor_lag": {
    "filter": {
      "range": {
        "source_timestamp": {
          "gte": "now-1h"
        }
      }
    },
    "aggs": {
      "lag_distribution": {
        "stats": {
          "script": "doc['index_timestamp'].value - doc['source_timestamp'].value"
        }
      }
    }
  }
}
```

### Error Handling Strategies

**Error Categories:**

1. **Transient Errors:**
   - Network timeouts
   - Temporary service unavailability
   - Rate limiting (429 responses)
   - Retry Strategy: Exponential backoff (3-5 attempts)

2. **Validation Errors:**
   - Schema mismatch
   - Type conversion failure
   - Required field missing
   - Action: Route to Dead Letter Queue

3. **Application Errors:**
   - Deserialization failure
   - Processing logic errors
   - Out of memory exceptions
   - Action: Alert, investigate, reprocess

### Dead Letter Queues (DLQ)

**Purpose:**
Capture messages that cannot be processed, preventing pipeline stalling.

**Implementation (Kafka):**
```json
{
  "connector.class": "org.apache.kafka.connect.sink.SinkConnector",
  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "documents-dlq",
  "errors.deadletterqueue.topic.replication.factor": 3,
  "errors.deadletterqueue.context.headers.enable": true
}
```

**DLQ Processing Workflow:**
```
Failed Message
    ↓
Send to DLQ Topic
    ↓
Alert/Log Error
    ↓
Manual Review/Investigation
    ↓
Fix Issue
    ↓
Reprocess from DLQ
    ↓
Success or Re-DLQ
```

**Monitoring DLQ:**
- Depth: Number of messages in DLQ
- Age: Oldest message timestamp
- Rate: Messages per hour
- Alert when depth > threshold or age > retention

### Retry Strategies

**Classification:**

1. **Transient Failure Retries:**
   - Network errors: Retry 3-5 times
   - Timeout errors: Retry with longer timeout
   - Rate limits: Exponential backoff with jitter

2. **Permanent Failure (No Retry):**
   - Schema validation failures
   - Type conversion errors
   - Required field missing

**Exponential Backoff with Jitter:**
```
Attempt 1: Wait 100ms + random(0-50ms)
Attempt 2: Wait 200ms + random(0-50ms)
Attempt 3: Wait 400ms + random(0-50ms)
Attempt 4: Wait 800ms + random(0-50ms)
Attempt 5: Wait 1600ms + random(0-50ms)
After 5: Route to DLQ
```

**Implementation (Python):**
```python
import random
import time

def retry_with_backoff(func, max_attempts=5, base_delay=0.1):
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError as e:
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                jitter = random.uniform(0, delay * 0.5)
                time.sleep(delay + jitter)
            else:
                raise
```

### Alerting and Notifications

**Critical Alerts:**
1. Indexing failure rate > 1%
2. Lag > SLA threshold (e.g., > 5 min)
3. DLQ depth growing
4. Disk space < 10%
5. Index replica count below minimum

**Alert Configuration (Prometheus):**
```yaml
alert_rules:
  - alert: HighIndexingErrorRate
    expr: |
      (rate(indexing_errors_total[5m]) /
       rate(indexing_total[5m])) > 0.01
    for: 5m
    annotations:
      summary: "High indexing error rate"

  - alert: IndexingLagHigh
    expr: indexing_lag_seconds > 300
    for: 2m
    annotations:
      summary: "Indexing lag above SLA"
```

### Performance Optimization Checklist

**Indexing Optimization:**
- [ ] Batch size tuned (32-256 documents)
- [ ] Refresh interval appropriate (1-30 seconds)
- [ ] Shard count matches throughput needs
- [ ] Replica count balanced with availability needs
- [ ] Translog settings optimized
- [ ] Index buffer sized adequately

**Data Quality:**
- [ ] Deduplication implemented (SimHash/MinHash)
- [ ] Missing field handling defined
- [ ] Data normalization consistent
- [ ] Entity extraction working
- [ ] Enrichment pipeline functioning

**Infrastructure:**
- [ ] CPU utilization 50-80%
- [ ] Memory GC pauses < 100ms
- [ ] Disk I/O not bottleneck
- [ ] Network bandwidth sufficient
- [ ] Backup strategy in place

**Monitoring:**
- [ ] Lag tracking active
- [ ] Error rates monitored
- [ ] DLQ depth tracked
- [ ] Performance metrics dashboards
- [ ] Alert thresholds set

---

## References and Further Reading

### ETL/ELT Patterns
- [Pure Storage: ETL vs. ELT](https://blog.purestorage.com/purely-technical/etl-vs-elt/)
- [Databricks: ETL vs ELT](https://www.databricks.com/discover/etl/vs-elt)
- [AWS: ETL Fundamentals](https://aws.amazon.com/what-is/etl/)

### Web Crawlers
- [Octoparse: Open Source Web Crawlers](https://www.octoparse.com/blog/top-open-source-web-crawlers)
- [Scrapy Official Documentation](https://scrapy.org/)
- [Apache Nutch Documentation](https://nutch.apache.org/)

### Document Processing
- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [Docling Project](https://github.com/docling-project/docling)
- [Unstructured.io Documentation](https://unstructured.io/)

### Text Processing & NLP
- [Medium: NLP Text Preprocessing](https://keremkargin.medium.com/nlp-tokenization-stemming-lemmatization-and-part-of-speech-tagging-9088ac068768)
- [Dev Community: NLP Pipeline Guide](https://dev.to/themustaphatijani/the-complete-guide-to-nlp-text-preprocessing-tokenization-normalization-stemming-lemmatization-50ap)

### Embeddings and Chunking
- [Pinecone: Chunking Strategies](https://www.pinecone.io/learn/chunking-strategies/)
- [Milvus: Semantic Chunking](https://milvus.io/blog/embedding-first-chunking-second-smarter-rag-retrieval-with-max-min-semantic-chunking.md)
- [Weaviate: RAG Chunking](https://weaviate.io/blog/chunking-strategies-for-rag)

### Real-Time Indexing
- [Confluent: Kafka and Elasticsearch](https://www.confluent.io/blog/kafka-elasticsearch-connector-tutorial/)
- [DoorDash: Real-Time Indexing with Kafka](https://careersatdoordash.com/blog/open-source-search-indexing/)
- [Elastic: Kafka Integration](https://www.elastic.co/search-labs/blog/elasticsearch-apache-kafka-ingest-data)

### Elasticsearch Schema Design
- [Elastic Docs: Mapping](https://www.elastic.co/docs/manage-data/data-store/mapping/)
- [Elastic Docs: Dynamic Templates](https://www.elastic.co/docs/manage-data/data-store/mapping/dynamic-templates)
- [Logz.io: Elasticsearch Mapping Guide](https://logz.io/blog/elasticsearch-mapping/)

### Index Management
- [Elastic Docs: Index Lifecycle Management](https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management/index-lifecycle)
- [Widhian Bramantya: Blue-Green Deployment](https://widhianbramantya.com/elasticsearch/blue-green-deployment-in-elasticsearch-safe-reindexing-and-zero-downtime-upgrades/)

### Data Quality
- [Azure AI Search: Enrichment](https://learn.microsoft.com/en-us/azure/search/cognitive-search-concept-intro)
- [Google Cloud: Entity Extraction](https://cloud.google.com/discover/what-is-entity-extraction)

### Deduplication
- [Milvus: MinHash LSH](https://milvus.io/es/blog/minhash-lsh-in-milvus-the-secret-weapon-for-fighting-duplicates-in-llm-training-data.md)
- [Made of Bugs: Fuzzy Deduplication](https://blog.nelhage.com/post/fuzzy-dedup/)
- [text-dedup PyPI](https://pypi.org/project/text-dedup/)

### Error Handling and Monitoring
- [Confluent: Kafka Dead Letter Queues](https://www.confluent.io/learn/kafka-dead-letter-queue/)
- [Confluent: Error Handling Deep Dive](https://www.confluent.io/blog/kafka-connect-deep-dive-error-handling-dead-letter-queues/)
- [AWS: SQS Dead Letter Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)

---

## Conclusion

Search indexing pipelines are the backbone of modern search systems, enabling organizations to make unstructured data searchable, discoverable, and actionable. This reference covers the full spectrum from data ingestion through to production monitoring.

Key takeaways:

1. **Pipeline Design**: Choose ETL vs. ELT vs. hybrid based on latency, complexity, and resource requirements
2. **Data Quality**: Invest in deduplication, normalization, and enrichment upstream
3. **Real-Time vs. Batch**: Modern systems blend both for optimal performance
4. **Schema Design**: Explicit, well-planned mappings prevent costly reindexing
5. **Monitoring**: Lag, throughput, and error metrics reveal pipeline health
6. **Resilience**: Dead letter queues and retry strategies handle failures gracefully

As systems grow and data volumes increase, these patterns and practices become essential for maintaining search quality, performance, and reliability at scale.

Last Updated: March 2025
