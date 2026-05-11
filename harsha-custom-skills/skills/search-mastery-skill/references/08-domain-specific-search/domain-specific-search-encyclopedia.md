# Domain-Specific Search Encyclopedia: Specialized Search for Every Use Case

## Overview

Search is not one-size-fits-all. Different domains have radically different requirements, constraints, and opportunities. This comprehensive guide explores how search implementations vary dramatically across nine critical domains, providing practical implementation patterns, architectural insights, and real-world considerations for each.

The fundamental challenge across all domains is the mismatch between user intent and how data is structured. A product name in e-commerce, a bug ticket in project management, a code snippet on GitHub, and a medical record in healthcare all require different indexing, ranking, and retrieval strategies.

---

## 1. Project Management / Jira Ticket Search

### Challenge Profile

Jira ticket search operates in a unique space where brevity meets complexity. Tickets typically contain:
- **Short fields**: Key (6-8 chars), Summary (50-200 chars)
- **Long unstructured fields**: Description (variable length), Comments (threaded)
- **Status-based filtering**: Open/In Progress/Done/etc.
- **Multi-valued fields**: Assignee, Reporter, Components, Labels
- **Custom fields**: Project-specific metadata that varies wildly

The core challenge is that ticket descriptions are often poorly formatted, inconsistently written, and difficult to index effectively. Additionally, JQL (Jira Query Language) is powerful but requires users to understand field names and syntax.

### Jira Query Language (JQL) Architecture

JQL is Jira's advanced search mechanism, operating as a structured query language rather than full-text search.

**Core Structure**:
```
field operator value [AND/OR field operator value]
```

Common operators include:
- `=` (exact match)
- `~` (contains/text search)
- `>=`, `<=`, `>`, `<` (numeric/date comparisons)
- `IN` (list membership)
- `IS` (null checks)

**Advanced Functions**:
- `linkedIssues(issueKey)` - Returns issues linked to a specific issue
- `linkedIssues(issueKey, linkType)` - Returns issues with specific link types
- `currentUser()` - Resolves to the logged-in user
- `startOfDay()`, `endOfDay()` - Time-aware date functions

**Example Queries**:
```jql
project = "LAP" AND status = "Open" AND priority = High
assignee = currentUser() AND resolution = Unresolved
created >= -30d AND text ~ "bug"
summary ~ "crash" OR description ~ "memory leak"
```

### Field Weighting and Relevance

When implementing improved search beyond Jira's built-in, use **BM25F** (an extension of BM25 for fielded documents):

**Recommended Field Weights for Tickets**:
```
Key:         3.0  (highest weight - exact identifiers matter most)
Summary:     2.5  (title is crucial)
Description: 1.5  (detailed info, but noisier)
Comments:    1.0  (context but variable quality)
Labels:      1.8  (metadata often carefully chosen)
```

BM25F calculates per-field scoring and applies weights to balance field contributions. The challenge is that descriptions in ticket systems often contain:
- HTML artifacts from paste-and-paste
- Code snippets with syntax highlighting markup
- Inconsistent formatting (sometimes markdown, sometimes plain text)
- Embedded links and images
- Quoted text from conversations

### Pre-processing for Indexability

Before indexing ticket descriptions:

1. **HTML Cleaning**: Strip markup, preserve text content
2. **Code Block Extraction**: Extract code blocks as separate indexed units
3. **Normalization**: Convert to consistent casing, remove special characters
4. **Tokenization**: Split on word boundaries AND camelCase boundaries (e.g., "DatabaseConnection" → "Database", "Connection")
5. **Category Detection**: Use keyword extraction to automatically tag ticket themes

**Example Pre-processing Pipeline**:
```
Raw: "<p>Database connection failing: java.sql.SQLException
      when connecting to prod</p><code>String url = ...</code>"

After cleaning: "Database connection failing java.sql.SQLException
                when connecting to prod String url = ..."

After tokenization: ["database", "connection", "failing",
                     "java", "sql", "exception", "when", ...]

Extracted category: "database-connectivity" (via keyword patterns)
```

### Real-World Example: LAP Project

Consider a real project with 1,839+ tickets where descriptions are largely unindexable due to:
- Free-form text with no schema
- Mixed formatting (some HTML, some plain text)
- Technical jargon without standardization
- Embedded error traces that clutter search

**Solution Strategy**:
1. Extract error stack traces into separate indexed field
2. Identify technology keywords (Python, Docker, Kubernetes)
3. Create concept-level tags from description patterns
4. Weight recent tickets higher (temporal decay)
5. Use query expansion to handle abbreviations (e.g., "DB" → "database")

### Limitations of Built-in Jira Search

- JQL requires knowing field names (not intuitive for new users)
- Text search (~) doesn't support advanced ranking
- No understanding of semantic similarity ("crash" ≠ "failure")
- No behavioral signals (which tickets get solved fastest?)
- Limited phrase handling and proximity search

---

## 2. E-Commerce Product Search

### Problem Space

E-commerce search differs fundamentally from document search. Users search for products with:
- **Exact attributes**: Color: red, Size: M, Price: $50-100
- **Fuzzy intent**: "tennis shoes" could match sneakers, trainers, athletic footwear
- **Behavioral signals**: Products people add-to-cart or purchase rank higher
- **Personalization**: Same query returns different results for different users
- **Typo tolerance**: "nike shoess" should match "nike shoes"

### Faceted Search Architecture

Faceted search allows users to refine results using multiple attributes simultaneously.

**Components**:
1. **Index**: All products with attribute fields indexed separately
2. **Facets**: Dynamic computation of available filter options based on current result set
3. **Constraints**: User-selected filters applied to narrow results
4. **Ranking**: Relevance scoring combining textual match + user behavior

**Implementation Pattern**:
```
1. User searches: "red winter coat"
2. Full-text match finds 2,500 products
3. Facets computed:
   - Size: [XS (450), S (620), M (580), L (250), ...]
   - Brand: [Columbia (340), North Face (290), ...]
   - Price Range: [$50-$100 (450), $100-$200 (1200), ...]
4. User selects: Size=M, Price=$100-200
5. Results filtered to 380 products
6. Facets recomputed based on new result set
```

### Ranking Algorithms

Modern e-commerce uses **Learn-to-Rank (LTR)** approaches that combine:

**Textual Signals**:
- BM25 score (query term frequency + document term rarity)
- Title match (higher weight than description)
- Synonym matching (red/crimson/scarlet)

**Behavioral Signals** (typically 60-70% of ranking weight):
- Click-through rate (CTR): % of users who clicked this product when it appeared in search
- Add-to-cart rate: % of clickthroughs that converted to cart addition
- Purchase rate: % of clicks that converted to purchase
- Return rate: % of purchases that were returned (negative signal)
- Dwell time: How long users spent viewing the product

**Contextual Signals**:
- User's browsing history
- User's previous purchases
- Geographic location
- Device type
- Time of day/season

**Personalization**:
```
Base Score = TextRelevance × 0.3 + BehavioralSignals × 0.5 +
             PersonalSignals × 0.2

PersonalSignals = UserHistory × 0.6 + CategoryAffinity × 0.4
```

### Attribute Search Challenges

**Challenge 1: Attribute Synonyms**
- Users search for "shoes", "sneakers", "trainers", "athletic footwear"
- Solution: Maintain synonym mappings, embed synonyms in product index

**Challenge 2: Incomplete Attributes**
- Not all products have complete metadata
- Solution: Use facet cardinality (avoid empty facets in UI)

**Challenge 3: Price Range Ambiguity**
- User searches "$50-100" but products list prices without ranges
- Solution: Allow price filtering as true range queries, not discrete buckets

**Challenge 4: Visual Search Integration**
- Users want to search by image (user uploads photo of shoe)
- Solution: Generate image embeddings, use embedding similarity for retrieval

### Typo Tolerance

Implement using:
1. **Fuzzy Matching**: Levenshtein distance (e.g., "shoess" is 1 edit away from "shoes")
2. **N-gram Indexing**: Index character-level n-grams, match on partial overlaps
3. **Phonetic Matching**: Soundex/Metaphone for pronunciation-based typos
4. **Context-Aware Correction**: "nikes" is usually "nike", not "kites"

---

## 3. Code Search

### GitHub's Blackbird Engine

GitHub replaced Elasticsearch for code search with **Blackbird**, a custom Rust-based engine designed specifically for code at massive scale.

**Why Custom?**
- Elasticsearch couldn't keep up with 200M+ repositories
- Code has unique properties (syntax, structure, naming conventions)
- Query patterns differ from document search (regex, symbol search, language awareness)

### Architecture Overview

**Indexing Strategy**:
1. **Trigram Index**: GitHub indexes code at the trigram level (3-character sequences)
   - "search" → [sea, ear, arc, rch]
   - Enables very fast substring matching
   - Trades off index size for query speed

2. **Blob Deduplication**: Sharded by Git blob object ID
   - Same code appearing in multiple repositories stored once
   - Load distributed uniformly across shards
   - Massive storage savings

3. **Query Parsing**: Blackbird parses queries into abstract syntax trees
   - Normalizes language specifications
   - Applies permissions and access controls
   - Rewrites queries for optimization

**Performance**:
- Handles 640 queries/second
- Indexes 120,000 documents/second
- Twice as fast as previous Elasticsearch-based system
- Supports regex queries directly

### Query Capabilities

**Substring Search**:
```
query: "database.connect"
matches: any line containing that exact substring
```

**Regular Expressions**:
```
query: "database\.(connect|open|query)"
matches: lines with database.connect, database.open, or database.query
```

**Symbol Search**:
```
query: symbol:DatabasePool
matches: definitions or references to DatabasePool class/function
```

**Language-Specific Search**:
```
query: language:python database
matches: only .py files containing "database"
```

### Code Search Limitations

**Blackbird/GitHub Code Search Limitations**:
- No semantic understanding (doesn't know "database.connect()" is a function call)
- Substring/regex only (no AST-aware search)
- No cross-file definition following
- Query complexity limited compared to semantic engines

### Sourcegraph: AST-Aware Code Search

Sourcegraph provides **semantic code search** capabilities that GitHub's Blackbird lacks.

**Capabilities**:
- **Structural Search**: Language-aware parsing of code structure
  - Finds function definitions matching patterns
  - Understands comment vs code vs strings
  - Can search for specific syntax patterns (e.g., "all try-catch blocks")

- **SCIP-Based Precise Navigation**:
  - Analyzes Abstract Syntax Tree (AST)
  - Maps symbols to definitions across files
  - "Go to definition" works accurately across repositories
  - Language-specific intelligence (Python imports, Java package structure)

- **Embedding-Based Semantic Search** (via Cody):
  - Encodes entire codebase into vectors
  - Finds semantically similar code snippets
  - "Find code that does X" where X is natural language

**Tradeoffs**:
- Requires language-specific indexers (slower than trigram-based)
- More complex infrastructure
- But vastly better precision for refactoring and code review tasks

### grep/ripgrep: Local Code Search

For single-machine or small-codebase code search, ripgrep dominates.

**ripgrep Performance Optimizations**:

1. **SIMD Searching**: Uses Intel Hyperscan (Teddy algorithm)
   - Vectorized comparison of regex against lines
   - 10x+ faster than GNU grep

2. **Smart File Handling**:
   - Respects .gitignore (skips ignored files automatically)
   - Skips hidden files by default
   - Skips binary files
   - Multi-threaded directory traversal

3. **Literal Prefix Extraction**:
   - Identifies searchable literal strings before regex
   - Scans file for literal first, then applies full regex engine
   - Stays out of regex engine for the majority of file

4. **Unicode Support**: Full Unicode support built-in (traditional grep is ASCII-focused)

**Limitations**:
- Local-only (no distributed search)
- No ranking or relevance
- No understanding of code structure
- Simple boolean/regex matching

---

## 4. Document / Knowledge Base Search

### Full-Text Extraction Challenges

**Multi-Format Documents**:
Documents arrive in PDF, DOCX, HTML, Markdown, plain text. Each requires different extraction:

- **PDF**: Text extraction (OCR for scanned), table detection, layout preservation
- **DOCX**: Metadata (author, created date), comments, tracked changes
- **HTML**: Tag-aware extraction, distinguishing content from navigation
- **Markdown**: Parse heading hierarchy, code blocks, links

**Practical Challenge**: A 50-page PDF report has 10,000 words, but users search for specific facts. Indexing the entire document as a single unit fails because:
- Document is too long (BM25 penalizes long documents)
- Query "database configuration" might appear only in chapter 3, but full document is returned

### Chunk-Based Indexing

The solution is **semantic chunking**:

**Approach**:
1. Split document into meaningful units (~800 characters, sentence boundaries)
2. Preserve context (include surrounding sentences)
3. Index each chunk separately
4. Return top-K chunks, not full documents

**Implementation**:
```
Document: "Chapter 3: Database Configuration..."

Chunks:
- Chunk 1: "Database Configuration. To configure the
           database connection, edit config.yaml.
           The host parameter specifies..."

- Chunk 2: "The port parameter defaults to 5432 for
           PostgreSQL. For custom ports, ensure
           firewall rules allow traffic..."

- Chunk 3: "After configuration, test the connection
           using: psql -h hostname -U user..."

When user searches "database port configuration":
- All three chunks match
- Return top 2-3 ranked by relevance
- User sees specific sections, not entire 50-page document
```

**Tradeoffs**:
- Better precision (users find exact information)
- Need to store more index entries (50-page doc → 50+ chunks)
- Must handle chunk overlap (preserve context across boundaries)
- Challenge: What if answer spans multiple chunks?

### Confluence and Notion Search Patterns

**Confluence**:
- Full-text index updates in batches (every 5 seconds)
- Maintains content index (pages, posts, comments)
- Maintains change index (who modified what, when)
- CQL (Confluence Query Language) for advanced search
- Permission-aware (users only see documents they have access to)

**Hybrid Retrieval Strategy for Confluence**:
1. Over-fetch results (get top 100, not top 10)
2. Apply score boosting heuristics:
   - Recent documents (+2x weight)
   - Documents the user created (+1.5x weight)
   - Pages in favorite spaces (+1.2x weight)
3. Aggregate results from multiple indexes:
   - Full-text content
   - Page titles
   - Comments
4. Rank by combined score, return top-K

### Section-Level vs Document-Level Retrieval

**Document-Level**:
- Return entire document
- Pros: User sees full context, good for overview searches
- Cons: Overwhelming for fact-finding, poor BM25 scoring

**Section-Level** (Chapter/Heading):
- Return individual sections
- Pros: Targeted results, better relevance
- Cons: Lost document context, require section extraction

**Paragraph-Level** (Chunk):
- Return individual paragraphs
- Pros: Extremely precise, users find exact answer
- Cons: Fragment context significantly

**Recommendation**: Implement multi-level retrieval:
```
User Query: "How do I configure the database?"

Return:
1. Top 2 sections (with heading context)
2. Top 3 paragraphs (most specific)
3. Overall document score (for browsing)

User can drill down from section → paragraph level
```

---

## 5. Log / Observability Search

### Challenge Profile

Log search operates at a scale most domains never reach:
- **Velocity**: Millions of log events per second
- **Volume**: Exabytes of data across years
- **Cardinality**: Hundreds of unique fields per application
- **Real-time**: Users want to search logs within seconds of events occurring

Traditional full-text indexing (Elasticsearch) becomes prohibitively expensive at scale. Modern solutions use **columnar storage** and **time-series aware indexing**.

### Structured vs Unstructured Logs

**Unstructured Log Entry**:
```
2024-03-01T14:23:45.123Z [ERROR] Database connection timeout
after 30s, user_id=12345, retry_count=3, host=db-prod-01
```

**Structured Log Entry** (JSON):
```json
{
  "timestamp": "2024-03-01T14:23:45.123Z",
  "level": "ERROR",
  "message": "Database connection timeout after 30s",
  "user_id": 12345,
  "retry_count": 3,
  "host": "db-prod-01",
  "service": "payment-api",
  "trace_id": "abc123xyz"
}
```

**Advantage of Structured Logs**:
- Field-specific queries (host=db-prod-01, level=ERROR)
- Numeric comparisons (retry_count > 2)
- Much more efficient indexing
- Better aggregation capabilities

### Elasticsearch Architecture

Elasticsearch uses **inverted indexes** for full-text search:
```
word → [doc_id_1, doc_id_2, doc_id_3, ...]
```

For logs specifically:
1. **Index per time period** (daily, hourly)
   - Older indexes can be moved to slower storage
   - Deleted automatically after retention period
   - Distributes load

2. **Elastic Common Schema (ECS)**:
   - Standardizes field names across sources
   - Enables correlation of logs from different services
   - Example fields: `@timestamp`, `log.level`, `service.name`, `host.name`

3. **Structured vs Unstructured Indexing**:
   - Structured fields indexed as keywords (fast exact match)
   - Unstructured message field full-text indexed (slower but flexible)

### Grafana Loki: The Lightweight Alternative

Loki is designed for log aggregation at scale while minimizing storage costs.

**Key Insight**: Don't index all content, only index labels (metadata).

**Architecture**:
```
Ingestion: Stream Selector [application="api", environment="prod"]
Query: {application="api"} |= "error" |> "500"
  1. Find all streams matching selector (fast - indexed)
  2. Stream log lines through regex filter (slower - but on smaller set)
  3. Parse lines, filter on values (slowest - minimal impact)
```

**LogQL (Loki Query Language) Examples**:

```logql
# Basic log stream selection
{job="api-server", env="production"}

# Text filtering (case-sensitive regex)
{job="api"} |= "error"

# Negative filtering
{job="api"} != "debug"

# Regex filtering
{job="api"} |= `error_code=\d+`

# Label extraction (extract from log line)
{job="api"} | json | label_extract | level="error"

# Metric aggregation (convert logs to metrics)
rate({job="api"}[5m])
count_over_time({job="api"} |= "error"[5m])
```

**Performance**: Loki typically uses 10-100x less storage than Elasticsearch for the same logs.

### Time-Series Aware Querying

Critical insight for observability: **time matters**.

**Time-Bucketing Pattern**:
```
Query: "Find errors in last hour"

Instead of: Full-text search entire history
Do this:
  1. Identify which log shards contain last hour (fast)
  2. Search only those shards (parallelized)
  3. Aggregate results with time-series functions
```

**Example: KQL (Kibana Query Language)**:
```
timestamp >= "now - 1h" AND level:ERROR AND service:payment-api
```

The `timestamp` constraint is applied first to drastically reduce search scope.

---

## 6. Healthcare / Medical Search

### Medical Terminology Challenge

Healthcare has the opposite problem of e-commerce: **too much standardization and too many synonyms**.

**Single Concept, Multiple Names**:
- "Myocardial Infarction" (formal)
- "Heart Attack" (colloquial)
- "MI" (abbreviation)
- "Acute Myocardial Infarction" (specific diagnosis code)
- ICD-10: I21 (specific code)
- SNOMED CT: 22298006 (unique concept ID)

### SNOMED CT and ICD-10 Integration

**SNOMED CT** (Systematized Nomenclature of Medicine):
- Most comprehensive clinical terminology
- ~350,000 concepts
- Hierarchical relationships (is-a, part-of, caused-by)
- Used in EHR systems for clinical documentation

**ICD-10** (International Classification of Diseases):
- Used for billing and statistics
- ~70,000 codes
- Less granular than SNOMED CT
- Required for medical coding

**Mapping**: SNOMED CT ↔ ICD-10
```
SNOMED CT Concept: "Myocardial infarction of anterolateral wall"
  ↓ (mapped to)
ICD-10 Code: I21.02 (ST elevation myocardial infarction of left
              anterior descending coronary artery)
```

### Biomedical NLP Approaches

**Challenge**: Extracting diagnoses from unstructured clinical notes.

**Input**:
```
Clinical Note: "Patient presents with chest pain and shortness of
breath. EKG shows ST elevation in leads II, III, and aVF.
Cardiac troponin elevated. Diagnoses: Acute myocardial infarction
of inferior wall, Hypertension, Type 2 diabetes."
```

**NLP Pipeline**:
1. **Named Entity Recognition (NER)**:
   - Identify medical terms: "chest pain", "ST elevation", "Acute myocardial infarction"
   - Map to standard terminology

2. **Concept Normalization**:
   - "chest pain" → SNOMED CT concept 29857009
   - "ST elevation" → SNOMED CT concept 251101009

3. **Relationship Extraction**:
   - Extract which diagnoses are primary vs secondary
   - Extract temporal relationships (current vs history)

4. **ICD-10 Coding**:
   - Convert identified SNOMED CT concepts to ICD-10 codes
   - Apply business rules for code specificity

### Clinical Decision Support Search

Medical search systems must answer questions like:
- "Medications contraindicated with patient's current drugs?"
- "Relevant clinical guidelines for diagnosed condition?"
- "Similar patient cases and outcomes?"

**Implementation**:
1. Index clinical protocols and guidelines by:
   - Diagnosis codes (SNOMED + ICD-10)
   - Medication interactions
   - Patient demographics (age, comorbidities)

2. At query time:
   - Match patient's diagnoses to relevant protocols
   - Check drug interactions
   - Filter by patient characteristics

3. Rank by:
   - Evidence level (clinical trial data > case reports)
   - Recency of guideline
   - Local hospital protocols (personalized)

### HIPAA Compliance in Search

Critical requirement: User should only see data they're authorized to access.

**Implementation**:
```
Search Query: "Find all myocardial infarction patients from 2024"

Authorization Check:
  - Can user access cardiology records? (role-based)
  - Can user access data from specific wards? (location-based)
  - Can user de-identify data? (for research)

Results:
  - If authorized for identified data: Show patient names
  - If authorized for de-identified only: Show patient ID only
  - If not authorized: Return 0 results
```

---

## 7. Legal / Compliance Search

### Boolean Search Dominance

Unlike most domains that moved to neural search, legal search still heavily uses **Boolean search**:
```
(contract OR agreement) AND (liability AND limitation)
NOT (indemnification)
```

**Why Boolean Prevails**:
- Lawyers need precise, predictable results
- Legal documents have specific structures and language
- Regulatory compliance requires traceable, explainable searches
- False negatives (missing a critical clause) are far worse than false positives

### Contract Clause Extraction

**Challenge**: Locate specific clauses within complex contracts.

**Manual Approach** (traditional):
- Lawyer reads entire 50-page contract
- Identifies clause locations
- Time-consuming and error-prone

**NLP Approach**:

**Step 1: Clause Boundary Detection**
```
Input: Contract text
Output: Boundaries of each clause

Example:
  [Clause: "Limitation of Liability"] → [Section 5.1-5.4]
  [Clause: "Indemnification"] → [Section 6.1-6.3]
  [Clause: "Term and Termination"] → [Section 7.1-7.5]
```

**Step 2: Clause Type Classification**
```
{Clause: "Neither party shall be liable for any indirect,
          incidental, or consequential damages..."}

→ Type: "Limitation of Liability"
→ Polarity: "FAVORABLE" (limits exposure)
→ Counterparty: "Vendor" (unfavorable to vendor)
```

**Step 3: Information Extraction from Clause**
```
{Limitation of Liability Clause}

Extracted Entities:
  - Damages Excluded: [indirect, incidental, consequential]
  - Monetary Cap: $1,000,000
  - Exceptions: [gross negligence, willful misconduct]
```

### Named Entity Recognition for Legal Documents

Critical entities to extract:
- **Parties**: Company names, individuals
- **Dates**: Effective date, expiration, renewal dates
- **Monetary Terms**: Payment amounts, penalties, caps
- **Obligations**: What each party must do
- **Conditions**: When obligations are triggered

**Example**:
```
Input: "Effective January 1, 2024, Acme Corp shall pay XYZ
       $50,000 per quarter, with a 10% penalty if payment
       is more than 30 days late."

Extracted:
  - Party 1: "Acme Corp" (payer)
  - Party 2: "XYZ" (recipient)
  - Effective Date: 2024-01-01
  - Amount: $50,000
  - Frequency: Quarterly
  - Penalty: 10%
  - Trigger: Payment > 30 days late
```

### Legal NLP Pipeline

Best results combine multiple techniques:

**Hybrid Approach**:
1. **Rule-Based Patterns** (60-70% accuracy):
   - Regular expressions for dates: `\d{1,2}/\d{1,2}/\d{4}`
   - Company patterns: Known vendor names
   - Monetary patterns: `\$[\d,]+`

2. **ML-Based Classification** (80-90% accuracy):
   - Clause type classification (trained on labeled contracts)
   - Entity recognition (conditional random fields or transformers)

3. **Post-Processing Rules** (improve to 95%+ accuracy):
   - Validate extracted dates against context
   - Link entities (Party A mentioned in clause → use consistent name)
   - Validate monetary amounts against total contract value

---

## 8. Real Estate / PropTech Search

### Geospatial Search Fundamentals

Real estate search requires location-aware queries impossible in traditional text search.

**Query Types**:
- "Properties within 5 miles of downtown"
- "Properties near schools and parks"
- "Properties in neighborhoods with low crime"

**Geospatial Index Structure**:
```
Property Index:
  - Latitude/Longitude (point location)
  - Price (numeric)
  - Bedrooms (numeric)
  - Neighborhood (categorical)
  - School District (categorical)

User Query: "3-bedroom homes within 2 miles of Main St"

1. Geocode "Main St" → (lat: 40.71, lon: -74.01)
2. Find all properties within 2-mile radius (use spatial index)
3. Filter by: bedrooms=3
4. Return sorted by distance
```

### Spatial Index Algorithms

**Geohash Approach** (simple, works well):
```
Location: (40.7128, -74.0060)  [New York City]

Geohash: "dr5reg"  (6-character precision ≈ 1.2km)
         "dr5regu" (7-character, ≈ 152m)

Index structure:
  - Store all properties by geohash
  - Query: Return all properties in this cell + neighboring cells
  - Efficient range queries
```

**Quadtree Approach** (hierarchical):
```
        [World]
         /    \
      [N]      [S]
     /  \      /  \
   [NW][NE]  [SW][SE]

Query "5-mile radius from point":
  1. Find quadrant containing point
  2. Check neighboring quadrants
  3. Return properties from relevant cells
```

### Price Range Filtering

**Challenge**: Users specify price ranges, but properties are discrete values.

**Wrong Approach**:
```
User: "Show me homes $300k-500k"

Naive Implementation:
  Only return properties priced between $300,000 and $500,000
  Result: Very few exact matches in narrow range
```

**Better Approach**:
```
User: "Show me homes $300k-500k"

Smart Implementation:
  1. Show homes in exact range ($300k-500k): 450 results
  2. Show nearby homes ($280k-$520k) as "Expand Search": 800 results
  3. Use slider UI: Allow user to dynamically adjust bounds
  4. Suggest similar properties just outside range with reasons why
```

### Attribute Combinations

Real estate search combines multiple attribute dimensions:

```
User Query:
  - Location: "San Francisco"
  - Price: $800k-$1.2M
  - Bedrooms: 2-3
  - Bathrooms: 1.5+
  - Walkability: "Very Walkable"
  - Built After: 2000
  - Pet-Friendly: Yes
  - Has Parking: Yes

Filtering Logic:
  1. Geospatial filter (San Francisco + nearby)
  2. Apply numeric filters (price, beds, baths, year)
  3. Apply categorical filters (walkability, pet-friendly, parking)
  4. Rank by:
     - Relevance to query
     - Days on market (newer listings weighted slightly higher)
     - Similar properties sold nearby (price validation)
     - User browsing history
```

### Similar Property Recommendations

**Embedding-Based Approach**:
```
For Property A (3-bed, $1M, SF, 2020):

Generate embedding from:
  - Price: normalized to [0,1]
  - Beds/Baths: normalized
  - Location: geospatial embedding
  - Age: normalized
  - Amenities: one-hot encoded

Find K properties with closest embeddings
  → Returns "Similar Properties"

Usually 5-10 suggestions shown alongside search results
```

---

## 9. Communication / Chat Search

### Message Search Architecture

Slack, Teams, and Discord all face similar challenges: **Real-time indexing of massive message volume**.

**Scale Context**:
- Slack: Billions of messages across workspace
- Teams: Millions of concurrent users, millions of messages/day
- Discord: Real-time message indexing across thousands of servers

### Slack's Approach

**Indexing Strategy**:
- Uses Solr with Lucene scoring
- Messages indexed in real-time (stored for persistence before broadcast)
- Each team's corpus is relatively small, allowing aggressive scoring

**Real-Time Flow**:
```
1. User types message in #channel
2. Message logged to durable storage (Kafka)
3. Message broadcast to channel subscribers (Redis)
4. Message indexed into Solr (parallel operation)
5. Search system queries Solr index
```

**Access Control Integration**:
```
User performs search: "project deadline"

For each result:
  - Check if user has access to channel
  - Check if user has access to thread
  - Check visibility settings (private vs public thread)
  - Return only accessible results

No external index of private messages created
Messages remain indexed with access controls applied at query time
```

### Privacy-Aware Search Implementation

**Critical Requirement**: Users should never see messages they don't have access to.

**Approach 1: Access Control at Query Time** (Slack's method)
```
Full text index includes private messages
At query time: Filter results by user's channel membership
Pro: Simple, one index for all content
Con: Each query must check permissions (slightly slower)
```

**Approach 2: Separate Indexes Per User**
```
Maintain individual indexes per user based on channel access
User searches only their own index
Pro: Faster queries, stronger privacy guarantee
Con: Massive storage overhead (N users = N copies of messages)
```

### Conversation Threading and Context

**Challenge**: Messages exist in threads, but search needs to return context.

**Implementation**:
```
User searches: "deployment failed"

Result 1:
  Message: "Deployment to prod failed this morning"
  Context:
    - Previous 2 messages (thread context)
    - Following 2 messages (resolution)
  Metadata:
    - Thread ID (user can jump to full thread)
    - Timestamp
    - Author
```

**Indexing Strategy**:
- Index individual messages
- Store thread_id and parent_message_id
- At display time: Reconstruct thread context

### Multi-Media Search in Messages

**Challenge**: Messages contain files, images, and reactions, not just text.

**Implementation**:
1. **Image Content**: Extract OCR text, store with message
   - User searches for text in screenshot: Requires OCR index

2. **File Content**: Extract text from PDFs, documents
   - User searches for "budget.pdf mentions Q3" → requires indexing file content

3. **Reactions and Metadata**:
   - Index reactions (emoji reactions searchable)
   - Index file names, mentions, links

**Tradeoff**: Indexing file content is expensive; many systems only index file metadata (name, date, size).

---

## Cross-Domain Lessons: Universal Search Patterns

### Pattern 1: Hybrid Retrieval

Nearly every domain benefits from combining multiple retrieval methods:

```
For Query "database connection failing":

1. Full-Text Match: BM25 scoring (lexical match)
2. Semantic Match: Embedding similarity (understanding)
3. Behavioral Signals: What solved similar problems before?
4. Recency/Popularity: Recent results often better

Final Ranking = 0.4 × BM25 + 0.3 × Semantic +
                0.2 × Behavioral + 0.1 × Recency
```

### Pattern 2: Field-Aware Indexing

Every domain has "important" vs "unimportant" content:

```
Document Search:
  - Title field: 3x weight
  - Headings: 2x weight
  - Body: 1x weight

Ticket Search:
  - Key: 3x weight
  - Summary: 2.5x weight
  - Description: 1.5x weight

Product Search:
  - Product name: 3x weight
  - Category: 2x weight
  - Description: 1x weight
```

### Pattern 3: Progressive Refinement

Users rarely get the perfect query on first attempt:

```
User Iteration:
1. Initial query: "database" (too broad)
2. System shows facets: [error type, database type, severity]
3. User refines: "database connection" + filter [error type: timeout]
4. Further refinement: Add [severity: critical]
5. Final results: Highly targeted
```

### Pattern 4: Real-Time Feedback

Modern search systems show feedback instantly:

```
1. User types: "datab" → Show suggestions as typing
2. User clicks result → Track click-through for ranking
3. User dwell time: How long did they look at result?
4. User action: Bought product? Fixed ticket? Downloaded doc?
   → Use feedback to improve ranking
```

### Pattern 5: Query Expansion and Synonyms

Raw user queries rarely match indexed content perfectly:

```
User Query: "bugs"
Expanded Query: "bugs" OR "defects" OR "issues" OR "problems"

Product Query: "red shoes"
Expanded: "red shoes" OR "red sneakers" OR "red athletic shoes"

Medical Query: "MI"
Expanded: "myocardial infarction" OR "heart attack" OR ICD-10:I21
```

---

## Implementation Checklist for Domain-Specific Search

When building search for a new domain:

1. **Understand Field Importance**
   - [ ] Identify which fields matter most
   - [ ] Determine field-specific ranking weights
   - [ ] Plan for custom field handling

2. **Choose Index Architecture**
   - [ ] Text-only or structured fields?
   - [ ] Document-level or chunk-level indexing?
   - [ ] Full-text or metadata-only indexing?

3. **Plan Ranking Strategy**
   - [ ] Text relevance (BM25 or vector embeddings)
   - [ ] Domain-specific signals (behavioral, recency, etc.)
   - [ ] Personalization factors

4. **Handle Domain-Specific Queries**
   - [ ] Query language needed? (JQL, LogQL, etc.)
   - [ ] Synonyms and abbreviations
   - [ ] Special operators (numeric ranges, dates, geography)

5. **Access Control**
   - [ ] Can search leak sensitive information?
   - [ ] Query-time filtering or separate indexes?
   - [ ] Audit trail of searches?

6. **Observability**
   - [ ] Track slow queries
   - [ ] Monitor query patterns
   - [ ] Measure search quality (click-through rate, dwell time)
   - [ ] Alert on anomalies (suddenly no results for common query)

---

## Conclusion

Domain-specific search is not about applying the same algorithm everywhere. The most successful search systems understand their domain deeply:

- **Jira**: Knows that ticket keys are paramount, descriptions are messy
- **E-commerce**: Knows that behavior (purchase) matters more than keywords
- **GitHub**: Knows that code has structure, substring search matters
- **Logs**: Knows that time dimension is critical, real-time matters
- **Healthcare**: Knows that terminology is standardized, safety is paramount
- **Legal**: Knows that precision matters more than recall, explainability is critical
- **Real Estate**: Knows that location is everything, similar items matter
- **Chat**: Knows that real-time matters, privacy is critical
- **Docs**: Knows that long content needs chunking, context matters

The future of search is **adaptive specialization**: systems that understand their specific domain and implement tailored solutions rather than generic full-text search.

---

## References and Further Reading

### Jira and Project Management Search
- [Atlassian JQL Guide](https://www.atlassian.com/software/jira/guides/jql/overview)
- [JQL Operators Documentation](https://support.atlassian.com/jira-software-cloud/docs/jql-operators/)
- [Master Jira Query Language](https://www.salto.io/blog-posts/jira-jql-guide)
- [BM25 Field Weighting Research](https://ceur-ws.org/Vol-2741/paper-11.pdf)
- [Okapi BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)

### E-Commerce Product Search
- [Faceted Search Guide](https://www.prefixbox.com/blog/faceted-filtering/)
- [Learn-to-Rank for E-Commerce](https://snowplow.io/blog/ecommerce-search-best-practices)
- [Faceted Navigation Survey](https://www.mdpi.com/2078-2489/14/7/387)
- [BigCommerce Faceted Search Best Practices](https://www.bigcommerce.com/articles/ecommerce/faceted-search/)

### Code Search
- [GitHub's Blackbird Engine](https://github.blog/engineering/architecture-optimization/the-technology-behind-githubs-new-code-search/)
- [A Brief History of Code Search at GitHub](https://github.blog/engineering/architecture-optimization/a-brief-history-of-code-search-at-github/)
- [Sourcegraph Structural Code Search](https://sourcegraph.com/blog/going-beyond-regular-expressions-with-structural-code-search)
- [ripgrep Performance and Architecture](https://burntsushi.net/ripgrep/)

### Document Search and Knowledge Bases
- [Confluence Search Architecture](https://confluence.atlassian.com/doc/confluence-search-syntax-158720.html)
- [Building Confluence Chatbot with Smart Search](https://medium.com/@EBingolIT/building-a-confluence-db-chatbot-lessons-from-naive-indexing-and-smart-search-c20617fdc2a8)
- [Chunk-Based Retrieval for Long Documents](https://www.johnsnowlabs.com/)

### Log and Observability Search
- [Grafana Loki Query Guide](https://grafana.com/docs/loki/latest/query/)
- [LogQL Reference](https://grafana.com/docs/loki/latest/query/query_reference/)
- [Elasticsearch Log Analysis](https://oneuptime.com/blog/post/2026-01-27-elasticsearch-log-analysis/view)
- [Elastic Common Schema (ECS)](https://www.elastic.co/observability)

### Healthcare and Medical Search
- [SNOMED CT Overview](https://www.snomed.org/)
- [NLP for ICD-10 Classification](https://pmc.ncbi.nlm.nih.gov/articles/PMC12099355/)
- [Clinical Terminology Integration](https://pmc.ncbi.nlm.nih.gov/articles/PMC6115234/)

### Legal Document Search
- [Clause Extraction with NLP](https://blog.lexcheck.com/how-does-clause-extraction-nlp-work-in-legal-tech-lc)
- [Legal NLP by John Snow Labs](https://www.johnsnowlabs.com/legal-nlp/)
- [Legal Information Extraction](https://naturaltech.medium.com/legaltech-information-extraction-in-legal-documents-e1843a60bc8d)

### Real Estate and Geospatial Search
- [Geospatial Search Algorithms](https://www.searchstax.com/blog/geospatial-search-with-managed-search/)
- [CARTO Real Estate Analysis](https://carto.com/industries/real-estate/)
- [AI-Powered Property Recommendations](https://aglowiditsolutions.com/blog/ai-property-recommendations-in-real-estate/)

### Communication and Chat Search
- [Slack Search Architecture](https://engineering.slack.com/search-at-slack/)
- [Slack Enterprise Search](https://slack.engineering/how-we-built-enterprise-search-to-be-secure-and-private/)
- [Slack System Design](https://www.systemdesignhandbook.com/guides/slack-system-design-interview/)
