# Graph and Knowledge Graph Search: Comprehensive Reference

**Last Updated:** March 2026
**Scope:** Entity-based search, knowledge graph architecture, graph traversal algorithms, semantic search
**Target Audience:** Search engineers, data architects, machine learning engineers, information retrieval specialists

---

## Table of Contents

1. [Knowledge Graphs for Search](#knowledge-graphs-for-search)
2. [Graph Databases for Search](#graph-databases-for-search)
3. [Entity Search Fundamentals](#entity-search-fundamentals)
4. [Graph-Enhanced Information Retrieval](#graph-enhanced-information-retrieval)
5. [Graph Traversal Algorithms](#graph-traversal-algorithms)
6. [GraphRAG Architecture](#graphrag-architecture)
7. [Ontology-Based Search](#ontology-based-search)
8. [Production Systems](#production-systems)
9. [Implementation Guide](#implementation-guide)
10. [Decision Framework](#decision-framework)

---

## Knowledge Graphs for Search

### What Are Knowledge Graphs?

A knowledge graph is a structured, machine-readable representation of interconnected data entities and their relationships. Knowledge graphs transform unstructured and semi-structured information into queryable networks that enable advanced search, analytics, reasoning, and discovery.

The fundamental building block of knowledge graphs is the **semantic triple** (or RDF triple), which represents facts in a subject-predicate-object format:
- **Subject:** The entity being described (e.g., "Mount Everest")
- **Predicate:** The relationship or property (e.g., "hasHeight")
- **Object:** The value or related entity (e.g., "8,849 meters")

### Triple-Based Data Architecture

The entity-attribute-value (EAV) model maps directly to semantic triples. In classical object-oriented terminology, statements like "The sky has the color blue" are decomposed into:
- **Entity:** Sky
- **Attribute:** Color
- **Value:** Blue

This decomposition provides several advantages:
- **Flexibility:** New properties can be added without schema modifications
- **Expressiveness:** Complex relationships can be represented naturally
- **Interoperability:** Triples form the basis for linked data standards
- **Reasoning:** Deductive systems can infer new facts from existing triples

### Schema.org and Structured Data

[Schema.org](https://schema.org), created in 2011 by Google, Bing, Yahoo, and Yandex, provides a standardized vocabulary for marking up web content with structured data. Schema.org enables the creation of knowledge graphs by:

1. **Standardizing Terminology:** Defining common entity types (Person, Organization, Place, Event, etc.) and properties
2. **Enabling Machine-Readability:** Allowing search engines to parse and understand web content at semantic level
3. **Improving Discovery:** Helping search engines identify and rank relevant entities
4. **Supporting Knowledge Panels:** Providing data for rich search result features

Key Schema.org markup formats include:
- **JSON-LD:** JavaScript Object Notation for Linked Data (recommended by Google)
- **Microdata:** HTML5 attribute-based markup
- **RDFa:** Resource Description Framework in Attributes

### Knowledge Graph Scale and Scope

Modern knowledge graphs operate at massive scales. For example:
- **Google Knowledge Graph:** Contains over 500 million objects and 3.5 billion facts about relationships between entities
- **Wikidata:** Hosts 1.65 billion semantic triples across multiple languages
- **DBpedia:** Extracts structured information from Wikipedia covering millions of entities

These graphs serve as the foundation for search engines to understand user intent beyond keyword matching, enabling:
- Disambiguation (distinguishing "Apple the company" from "apple the fruit")
- Related entity discovery
- Relationship-based search
- Structured answer generation

---

## Graph Databases for Search

### Overview of Graph Database Systems

Graph databases are specialized data systems designed to store, index, and query highly connected data efficiently. Unlike relational databases that struggle with complex joins, and NoSQL systems optimized for unstructured data, graph databases excel at traversing relationships.

Key characteristics:
- **Native Graph Storage:** Data stored as nodes (entities) and edges (relationships), not tables
- **Relationship Traversal:** Fast path queries across multiple hops
- **Property Storage:** Both nodes and edges can carry properties (attributes)
- **ACID Compliance:** Many modern graph databases provide transactional guarantees

### Neo4j: The Leading Graph Database

[Neo4j](https://neo4j.com) is the most widely adopted graph database platform with dedicated search and full-text capabilities.

#### Full-Text Search in Neo4j

Neo4j provides full-text search capabilities through Lucene-powered fulltext schema indexes:

**Implementation:**
```cypher
CREATE FULLTEXT INDEX product_search
  FOR (n:Product)
  ON EACH [n.name, n.description, n.tags]
```

**Query Execution:**
```cypher
CALL db.index.fulltext.queryNodes("product_search", "electronics laptop")
  YIELD node, score
  RETURN node.name, score
  ORDER BY score DESC
  LIMIT 10
```

**Key Features:**
- Supports only STRING and LIST<STRING> property values
- Returns relevance scores for ranking results
- Automatically populated with existing data
- Transactional consistency across clusters
- Lucene-based tokenization and stemming

#### Hybrid Retrieval: Full-Text + Graph Traversal

The most powerful Neo4j search pattern combines full-text search with graph traversal:

```cypher
CALL db.index.fulltext.queryNodes("product_search", "laptop")
  YIELD node as product, score
WITH product
MATCH (product)-[:BELONGS_TO]->(category)
MATCH (product)<-[:PURCHASED_BY]-(customer)
WHERE customer.loyalty_status = 'Premium'
RETURN product.name, category.name,
       collect(customer.name) as premium_customers
```

This approach:
1. Identifies initial result set through full-text indexing (fast, limited semantic understanding)
2. Enhances results with graph context (relationships, aggregations, recommendations)
3. Applies business logic filtering based on relationship properties
4. Generates enriched results impossible through either mechanism alone

**HybridCypherRetriever Pattern:**
```
Vector/Full-text Search → Initial Nodes → Graph Traversal → Enhanced Results
```

### Amazon Neptune

[Amazon Neptune](https://aws.amazon.com/neptune/) is a managed graph database service for AWS environments.

**Characteristics:**
- **Fully Managed:** AWS handles provisioning, patching, backups, scaling
- **Multi-Model:** Supports both property graph (Apache TinkerPop) and RDF models
- **Query Languages:** Gremlin, SPARQL, openCypher
- **AWS Integration:** Native connectivity to Lambda, SageMaker, Glue, and other AWS services
- **ACID Compliance:** Multi-AZ replication with strong consistency
- **Search Capabilities:** Supports Elasticsearch integration for full-text search

**Suitable For:**
- Organizations already invested in AWS ecosystem
- Applications requiring fully managed infrastructure
- Teams wanting to avoid operational complexity
- Semantic web and RDF applications

### ArangoDB

[ArangoDB](https://www.arangodb.com/) is a multi-model database combining document, graph, and search capabilities.

**Architecture:**
- **Multi-Model:** Single system for graphs, documents, key-value, and search
- **Native Query Language:** ArangoDB Query Language (AQL) - similar to SQL
- **Flexible Deployment:** On-premises, cloud, or managed ArangoGraph platform
- **Efficient Storage:** Document-oriented with columnar optimization for analytics

**Advantages for Search:**
- Integrated full-text search without separate systems
- Flexible schema supporting rapid prototyping
- Document + graph combination for hierarchical data
- Efficient disk usage and faster data loading than competitors

**Performance Characteristics:**
- Strong in data loading speed
- Disk space efficiency
- Suitable for complex query scenarios

### TigerGraph

[TigerGraph](https://www.tigergraph.com/) is optimized for high-performance, compute-intensive graph operations.

**Performance Leadership:**
- 2x to 8000x faster than competing systems on graph traversal
- 40x to 337x faster on 2-hop queries
- Single-server performance comparable to cluster solutions from competitors

**Query Language:**
- **GSQL:** Native graph-specific SQL
- **openCypher:** Industry-standard graph query language

**Deployment Options:**
- Self-hosted on-premises
- Self-managed cloud (AWS, GCP, Azure)
- TigerGraph Cloud (managed service)

**Ideal Use Cases:**
- Deep multi-hop graph queries
- Compute-intensive graph analytics
- Custom graph algorithms
- Real-time pattern detection
- Large-scale social network analysis

**Comparison Summary:**

| Criteria | Neo4j | Neptune | ArangoDB | TigerGraph |
|----------|-------|---------|----------|-----------|
| Query Language | Cypher | Gremlin/SPARQL | AQL | GSQL/openCypher |
| Full-Text Search | Native | Via Elasticsearch | Native | Via Integration |
| Deployment | All options | AWS only | All options | All options |
| Performance Focus | Balanced | AWS-optimized | Multi-model | Graph speed |
| ACID Support | Yes | Yes | Yes | Yes |
| Scalability | Cluster | Horizontal | Horizontal | Horizontal |

---

## Entity Search Fundamentals

### Named Entity Recognition (NER)

Named Entity Recognition is the foundational NLP task that automatically identifies and categorizes named entities in text. Entities include:
- **Person:** Individual human beings
- **Organization:** Companies, governments, institutions
- **Location:** Geographic places, cities, countries
- **Product:** Commercial goods and services
- **Date/Time:** Temporal expressions
- **Money:** Financial amounts and currencies
- **Facility:** Buildings, landmarks, infrastructure

**Methods:**
1. **Rule-Based:** Pattern matching with hand-crafted rules (low coverage, high precision)
2. **Statistical ML:** Sequence labeling with CRF, HMM (balanced approach)
3. **Deep Learning:** Bi-LSTM, Transformer-based models (high coverage, requires training data)
4. **LLM-Based:** Fine-tuned or prompted large language models (increasingly dominant)

**Challenges:**
- Nested entities ("New York City" vs. "York")
- Class ambiguity ("Apple" as company vs. fruit)
- Low-resource languages
- Domain-specific terminology
- Abbreviations and acronyms

### Entity Linking and Disambiguation

Entity linking (also called Named Entity Disambiguation or NED) resolves entity mentions in text to canonical identifiers in a knowledge base. This is critical for unifying references across documents.

**Disambiguation Problem:**
The same mention can refer to multiple real-world entities:
- "Washington" → U.S. State, D.C., or President
- "Michael Jordan" → Basketball player, mathematician, or multiple other people
- "Tesla" → Company, Scientist, or car brand

**Entity Linking Process:**

```
Input Text: "Michael Jordan won MVP in 1988 at Chicago."
          ↓
NER: Identify "Michael Jordan", "MVP", "1988", "Chicago"
          ↓
Candidate Generation: Find possible entities in knowledge base
          ↓
Disambiguation: Score candidates using:
  - Textual similarity to mention
  - Knowledge base entity popularity
  - Context coherence (related entities?)
  - Prior disambiguation decisions
          ↓
Output: michael_jordan/basketball, chicago/city
```

**Disambiguation Approaches:**
1. **String Similarity:** Levenshtein distance, cosine similarity on embeddings
2. **Popularity:** Entity frequency in knowledge base (common bias)
3. **Coherence:** Relatedness of linked entities (if linking "Chicago" and "Michael Jordan", verify connection)
4. **Learning-Based:** Neural models trained on gold standard entity link datasets

**Knowledge Bases for Linking:**
- **Wikidata:** 100+ million entities with QID identifiers
- **DBpedia:** Structured data extracted from Wikipedia
- **YAGO:** Combines Wikipedia, WordNet, Wikidata
- **Freebase:** (Deprecated, integrated into Wikidata)
- **Domain-Specific:** Industry knowledge bases, medical ontologies, product catalogs

### Entity-Centric Search Architecture

Entity-centric search inverts traditional IR: instead of documents containing entities, the system treats entities as primary retrieval units.

**Architecture Components:**

```
Document Collection
        ↓
[NER + Entity Linking]
        ↓
Entity Index (Lucene, Elasticsearch)
    - Entity profiles
    - Mention frequency
    - Document associations
        ↓
Query
        ↓
[Query Analysis + NER]
        ↓
Entity Retrieval
    - Full-text match
    - Related entities
    - Disambiguated entities
        ↓
Result Ranking (by:
    - Entity popularity
    - Mention frequency
    - Query match quality
    - User context)
        ↓
Result Presentation
```

**Advantages:**
- Users often search for entities, not documents
- Better ranking of entity-centric information
- Support for entity-to-entity discovery
- Cleaner handling of entity ambiguity
- Integration with knowledge panels

---

## Graph-Enhanced Information Retrieval

### Traditional IR Limitations

Traditional information retrieval, based on vector space models and inverted indexes, has limitations:

1. **Query Mismatch:** "President of USA" won't match documents using "Joe Biden"
2. **Relationship Ignorance:** No understanding that "Tesla is founded by Elon Musk"
3. **Context Disconnection:** Ranking ignores relationships between retrieved documents
4. **Semantic Gaps:** Keywords miss synonymous or related concepts

### Entity-Aware Ranking

Graph-based ranking integrates entity relationships into relevance scoring.

**Components:**
1. **Entity Extraction:** Identify entities in both query and documents
2. **Entity Linking:** Normalize entities to canonical identifiers
3. **Relationship Computation:** Build relationship graph between entities
4. **Ranking Enhancement:** Adjust document scores based on entity relationships

**Example:**
```
Query: "Apple CEO products"
        ↓
Entities: Apple (company), CEO (role), products

Retrieved documents about "Jobs" article:
Without graph: Ranked low (keyword mismatch)
With graph: Boosted because:
  - Jobs is linked to Apple (relationship match)
  - Jobs held CEO role (entity type match)
  - Jobs associated with products (transitive match)
```

### Knowledge Graph Query Expansion

Query expansion automatically enriches user queries with related entities and concepts.

**Expansion Methods:**

**1. Entity Expansion:**
```
Query: "machine learning"
Expansion: machine learning, deep learning, neural networks,
           artificial intelligence, supervised learning, ...
```

**2. Synonym Expansion:**
```
Query: "CEO"
Expansion: Chief Executive Officer, executive director,
           company leader, president, ...
```

**3. Related Entity Expansion:**
```
Query: "Elon Musk"
Expansion: Tesla, SpaceX, Neuralink, Twitter,
           electric vehicles, space exploration, ...
```

**Implementation Techniques:**
- **Ontology-Based:** Follow rdfs:subClassOf and similar relationships
- **Embedding-Based:** Find nearest neighbors in entity embedding space
- **Graph-Walk:** Random walks from query entities
- **Learning-Based:** Train model on query expansion feedback

### Google Knowledge Panels

Knowledge panels are rich information displays that appear beside search results, powered by the Google Knowledge Graph.

**How Google Constructs Knowledge Panels:**

```
Information Sources:
  1. Your Website + Schema.org markup
  2. Structured databases (Wikipedia, Wikidata)
  3. Media coverage and news
  4. Public profiles (LinkedIn, etc.)
        ↓
Knowledge Graph Aggregation:
  - Extract facts and relationships
  - Resolve entity references
  - Verify information quality
  - Rank by reliability
        ↓
Panel Generation:
  - Select most relevant facts
  - Format visually
  - Add images, links, related entities
        ↓
Display: Beside search results
```

**Benefits for Search:**
- Satisfies user intent directly (no click required)
- Showcases structured information
- Drives traffic to authoritative sources
- Improves CTR for featured entities

**Technical Triggers:**
- Sufficient structured data quality
- Entity notability/prominence
- Entity coverage across sources
- User search intent
- Schema.org markup completeness

---

## Graph Traversal Algorithms

### Core Traversal Methods

Graph traversal algorithms navigate graph structures to find paths, connections, and patterns.

#### Breadth-First Search (BFS)

**Use Case:** Finding shortest paths, proximity searches, level-based exploration

```
Algorithm:
1. Start at source node
2. Visit all immediate neighbors (1-hop)
3. Then all neighbors of neighbors (2-hop)
4. Continue level-by-level until target or exhaustion
```

**Search Application:** "People you know" in social networks
```
BFS from User →
  1st level: Direct connections (friends)
  2nd level: Friends of friends
  3rd level: Friends of friends of friends
```

#### Depth-First Search (DFS)

**Use Case:** Exploring all reachable nodes, finding cycles, topological sorting

```
Algorithm:
1. Start at source node
2. Go deep on one path to leaf
3. Backtrack and explore other paths
4. Continue until all reachable nodes visited
```

**Search Application:** Graph curiosity "what's connected to this entity"

### Ranking and Relevance Algorithms

#### PageRank

PageRank models the behavior of a "random web surfer" to rank graph nodes by importance.

**How It Works:**

1. **Random Surfer Model:**
   - Start at random node
   - Follow outgoing edges with equal probability
   - Occasionally jump to random node (damping)
   - Repeat to convergence

2. **Importance Definition:**
   - Nodes visited frequently are important
   - Importance from high-importance nodes counts more
   - The probability of visiting a node IS its PageRank

**Formula (Simplified):**
```
PR(A) = (1-d)/N + d * Σ(PR(B)/L(B))
Where:
  - N = total nodes
  - d = damping factor (usually 0.85)
  - B = pages linking to A
  - L(B) = number of outgoing links from B
```

**Search Application:**
```
Document Graph:
  Doc1 ← (links from Doc2, Doc3, Doc4)

PageRank determines:
  - How many docs link to Doc1
  - Quality of linking documents
  - Relative importance for ranking
```

**Limitations:**
- Doesn't account for query relevance
- Sink nodes (no outgoing links) distort calculations
- Doesn't capture temporal dynamics

#### HITS Algorithm (Hypertext Induced Topic Search)

HITS treats search as a two-part process identifying:
1. **Hubs:** Pages linking to many authorities
2. **Authorities:** Pages linked to by many hubs

**Algorithm:**
```
Iterate:
1. Authority Score: Sum of incoming hub scores
2. Hub Score: Sum of outgoing authority scores
3. Normalize scores
4. Repeat until convergence
```

**Distinction from PageRank:**
- PageRank: Single importance score per node
- HITS: Separate hub and authority scores
- HITS: Query-dependent (finds topic-specific authorities)
- PageRank: Query-independent

**Search Relevance:**
```
Query: "machine learning frameworks"
High Authority: Papers, tutorials on frameworks
High Hub: Survey papers, curated collections linking to authorities
Result Ranking: Combine authority and hub scores
```

### Personalized PageRank (PPR)

Personalized PageRank modifies standard PageRank to emphasize importance relative to a specific user or seed set.

**Key Difference:**
- Standard PageRank: Random walk can teleport to ANY node
- PPR: Random walk teleports only to seed nodes

**Modification:**
```
PPR(A, seed_set) = (1-d)/|S| + d * Σ(PPR(B)/L(B))
Where:
  - Teleportation only to nodes in seed_set S
  - Damping factor d = 0.85 (typical)
```

**Applications:**

**1. Personalized Search Results:**
```
User Profile:
  - Recent interests: Machine Learning, Python, Data Science
  - Following: Specific researchers, companies
  - Saved articles: Particular domains

PPR Seed Set: {ML, Python, Data Science entities}

Ranking: Emphasizes results related to user's domain
```

**2. Social Network Recommendations:**
```
Twitter's "Users You May Know":
Seed Set: User's current followers
PPR: Find nodes "close" to follower network
Result: Account recommendations aligned with user's community
```

**3. Product Recommendations:**
```
E-commerce Graph:
  Products ← → Categories ← → Brands ← → Users

For User A:
Seed Set: Categories A previously purchased
PPR: Find products related to A's category preferences
Result: Personalized product ranking vs. global popularity
```

### Graph-Based Ranking for Search

Combined approach using multiple algorithms:

```
Entity Query Graph:
  Entity E1 --relation1--> E2
           --relation2--> E3

Ranking Signals:
1. PageRank(E): Popularity
2. PPR(E, query_intent): Relevance to user
3. BFS proximity: Distance from seed entities
4. HITS authority: Citation/mention frequency
5. Entity recency: Freshness of mentions
6. Semantic similarity: Embedding distance

Combined Score:
  score = w1*PR + w2*PPR + w3*proximity + w4*authority + w5*recency + w6*semantic

Learned weights from engagement data
```

---

## GraphRAG Architecture

### What is GraphRAG?

GraphRAG (Graph-augmented Retrieval Augmented Generation) is Microsoft's approach to improving retrieval quality for complex, long-form text by leveraging knowledge graphs and community detection.

**Problem It Solves:**
Traditional RAG systems struggle with:
- Questions requiring holistic dataset understanding
- Summarization of complex, interconnected information
- Maintaining context across large document collections
- Answering questions about patterns and themes vs. specific facts

### Architecture Components

#### 1. Knowledge Graph Extraction

**Input:** Raw documents, transcripts, PDFs, articles

**Process:**
```
Raw Text
  ↓
LLM Entity & Relation Extraction
  ↓
Entity Resolution (deduplication)
  ↓
Knowledge Graph
  - Nodes: Entities (persons, organizations, concepts)
  - Edges: Relationships (works_for, located_in, discussed_in)
  - Properties: Attributes on nodes and edges
```

**Example:**
```
Input: "Elon Musk founded Tesla in 2003. Tesla manufactures
        electric vehicles. The company is headquartered in California."

Extracted:
Nodes:
  - Elon Musk (person)
  - Tesla (organization)
  - 2003 (date)
  - California (location)

Edges:
  - Elon Musk --founded--> Tesla
  - Tesla --founded_in--> 2003
  - Tesla --headquartered_in--> California
  - Tesla --manufactures--> Electric Vehicles
```

#### 2. Community Detection and Clustering

**Algorithm:** Hierarchical Leiden Algorithm

The system recursively partitions the graph to identify communities of densely-connected nodes.

**Process:**
```
Initial Graph (all nodes)
  ↓
Community Detection Pass 1:
  Partition into communities based on connection density
  ├─ Community 1 (e.g., Tesla ecosystem: Tesla, Elon, SpaceX, Grimes)
  ├─ Community 2 (e.g., Tesla competitors: Tesla, Ford, GM, EV market)
  └─ Community 3 (e.g., California tech: Tesla, California, Bay Area, tech)
  ↓
For each community, recurse (Community Detection Pass 2):
  ├─ Community 1.1 (Tesla company specifics)
  ├─ Community 1.2 (Elon Musk personal activities)
  └─ Community 1.3 (Tesla & SpaceX connection)
  ↓
Continue until communities fall below size threshold
  ↓
Result: Hierarchical community structure
```

**Outcome:**
```
Level 0 (Global):
  - Dataset contains discussions of: Tesla, space exploration, EV, technology

Level 1 (Sub-topics):
  - Manufacturing and engineering
  - Business and leadership
  - Technology and innovation
  - Controversy and criticism

Level 2 (Specific topics):
  - Battery technology specifics
  - Supply chain
  - Competition analysis
  - Leadership personalities
```

#### 3. Community Summarization

**For each community node:** Generate text summaries

```
Community: "Battery Technology"
Nodes: Lithium-ion, cell manufacturing, energy density,
       recycling, performance, costs

Generated Summary:
"This section discusses battery technology, particularly
lithium-ion cells used in electric vehicles. Key topics include
manufacturing processes, energy density improvements, recycling
initiatives, and cost reduction strategies. The discussion covers
performance specifications and technical challenges in scaling
battery production."
```

**Advantages:**
- Pre-computed summaries reduce LLM calls during retrieval
- Hierarchical summaries at different levels of abstraction
- Community context improves answer quality
- Scales better than document-level retrieval

#### 4. Dynamic Community Selection During Retrieval

**Query-Time Process:**

```
User Query: "How does Tesla approach battery innovation?"

1. Start at highest level (global context):
   Evaluate relevance of each top-level summary

2. Rate relevance (by LLM):
   ├─ "Tesla ecosystem" → Highly relevant (keep)
   ├─ "Competitors analysis" → Moderately relevant (maybe)
   └─ "Political topics" → Not relevant (prune)

3. For relevant communities, traverse down:
   ├─ From "Tesla ecosystem" → "Battery innovation subtopic"
   │  └─ Rate sub-summaries
   │     ├─ "Manufacturing specifics" → Relevant
   │     ├─ "Supply chain" → Moderately relevant
   │     └─ "Sales strategy" → Not relevant
   │
   └─ Continue recursion to leaf communities

4. Collect relevant community reports at all levels

5. Use as context in LLM:
   "Based on these community reports about battery
    innovation, answer: How does Tesla approach battery
    innovation?"
```

**Key Innovation:** Dynamic community selection avoids:
- Processing irrelevant information
- Context window overload
- Dilution of relevant details
- Computational waste

### GraphRAG vs. Standard RAG

| Aspect | Standard RAG | GraphRAG |
|--------|-------------|----------|
| Index | Document chunks | Knowledge graph + communities |
| Retrieval | Similarity search | Dynamic community selection |
| Context | Top-K similar chunks | Hierarchical community summaries |
| Question Type | Specific factual queries | Complex, holistic questions |
| Performance | High recall, moderate precision | High precision, excellent on complex Q |
| Computational Cost | Lower | Higher (worth it for complex Q) |

### Use Cases

**Excellent for:**
- Long documents (dissertations, technical specs, legal contracts)
- Complex research questions requiring dataset overview
- Discovering patterns and relationships
- Cross-document coherence (understanding connections)

**Overkill for:**
- Factual lookup queries ("What is X?")
- Single-document searches
- Real-time, low-latency requirements
- Resource-constrained environments

---

## Ontology-Based Search

### Semantic Web Fundamentals

The semantic web vision: "The Semantic Web is the Web of data. There are advantages to having both human-readable information and machine-readable information served up together."

**Key Principles:**
1. Data should be machine-readable and interpretable
2. Relationships and context matter as much as content
3. Distributed knowledge sources should be linkable
4. Systems should enable reasoning and inference

### RDF: Resource Description Framework

RDF is the foundational data model for semantic web, consisting of:
- **Resources:** Anything described (URIs or blank nodes)
- **Properties:** Attributes or relationships (URI predicates)
- **Values:** Objects referenced (resources or literals)

**RDF Triple Example:**
```
<http://example.org/Tesla>
  <http://example.org/foundedBy>
  <http://example.org/ElonMusk> .

In Turtle syntax (human-readable):
Tesla foundedBy ElonMusk .
```

**Key Advantage:** Global namespace via URIs enables global data linking

```
Multiple data sources:
- Wikipedia: http://en.wikipedia.org/wiki/Tesla_Inc
- DBpedia: http://dbpedia.org/resource/Tesla,_Inc.
- Wikidata: http://www.wikidata.org/entity/Q478214

All refer to the SAME entity via linked URIs
Enables semantic integration without centralized authority
```

### SPARQL: Semantic Query Language

SPARQL (SPARQL Protocol and RDF Query Language) is the W3C standard for querying RDF data.

**Syntax:**
```sparql
PREFIX tesla: <http://example.org/>

SELECT ?person ?role
WHERE {
  ?person tesla:worksFor tesla:Tesla .
  ?person tesla:hasRole ?role .
  FILTER (?role IN ("CEO", "CTO", "Founder"))
}
ORDER BY ?person
```

**Key Constructs:**
- **SELECT:** Specify returned variables
- **WHERE:** Graph patterns to match
- **FILTER:** Constraints on results
- **UNION:** Alternative patterns
- **OPTIONAL:** Conditional matching
- **GROUP BY / AGGREGATE:** Summarization

**Comparison to SQL:**
```sql
SELECT person, role
FROM employees
WHERE company = 'Tesla' AND role IN ('CEO', 'CTO', 'Founder')

SPARQL: Same logic, operates on RDF graph instead of relational tables
```

**Advantage:** SPARQL operates directly on relationship patterns

```
SQL Query Pattern:
SELECT * FROM employees
  JOIN companies ON employees.company_id = companies.id
  WHERE companies.name = 'Tesla'

SPARQL Equivalent (more natural for relationships):
SELECT ?person WHERE {
  ?person workFor ?company .
  ?company name "Tesla" .
}
```

### OWL: Web Ontology Language

OWL extends RDF with expressive semantics for defining:
- Classes and inheritance
- Property characteristics (transitive, symmetric, functional)
- Cardinality constraints
- Equivalence and disjointness
- Reasoning rules

**OWL Concepts:**

**1. Class Hierarchies:**
```
:Vehicle rdfs:subClassOf :TransportationDevice .
:ElectricVehicle rdfs:subClassOf :Vehicle .
:Car rdfs:subClassOf :Vehicle .
:Tesla rdfs:subClassOf :ElectricVehicle .

Inference: Tesla is-a ElectricVehicle is-a Vehicle
```

**2. Property Characteristics:**
```
:worksFor a owl:ObjectProperty ;
  rdfs:domain :Person ;
  rdfs:range :Organization .

:locatedIn a owl:TransitiveProperty ;
  # If A locatedIn B, B locatedIn C → A locatedIn C

:married a owl:SymmetricProperty ;
  # If A married B → B married A
```

**3. Cardinality Constraints:**
```
:hasSpouse a owl:FunctionalProperty ;
  # Each person has at most one spouse

:hasMember a owl:InverseFunctionalProperty ;
  # Each member belongs to one organization
```

### Ontology-Based Query Expansion

Semantic web ontologies enable automatic query expansion through reasoning:

**Example: Software Engineering Ontology**

```
Query: "Find papers about Java programming"

Ontology Knowledge:
  :Java rdfs:subClassOf :ProgrammingLanguage
  :ProgrammingLanguage owl:intersectionOf (:Language, :Software)

Expansion 1 (class hierarchy):
  Papers about :JavaProgramming
  Papers about :ProgrammingLanguage (broader)

Expansion 2 (property-based):
  :Java usedIn :WebDevelopment
  :Java usedIn :MobileApps

Expanded Query becomes:
  (Java) OR (ProgrammingLanguage) OR
  (WebDevelopment with Java) OR (MobileApps with Java)
```

**Reasoning for Expansion:**

1. **Hierarchical Expansion:**
   - Query: "CEO" → Also search: "ExecutiveOfficer", "Leadership"
   - Uses rdfs:subClassOf relationships

2. **Related Concept Expansion:**
   - Query: "Machine Learning" → Also search: "DeepLearning", "NeuralNetworks", "AI"
   - Uses semantic relationships defined in ontology

3. **Domain-Based Expansion:**
   - Query: "Python" + domain=DataScience → prioritize data science applications
   - Uses domain-specific ontologies

### RDFS Entailment and OWL Reasoning

SPARQL with OWL entailment enables queries that return implicit knowledge:

**Example:**
```
Explicit triple in RDF graph:
  :Tesla :locatedIn :California

Ontology rule:
  :California :locatedIn :UnitedStates

Query with RDFS entailment:
  SPARQL CONSTRUCT {
    ?company :locatedIn :UnitedStates
  } WHERE {
    ?company :type :Company
  }

Result includes: Tesla :locatedIn :UnitedStates
(derived, not explicitly stored)
```

**Inference Engines:**
- **Jena Reasoner:** Open-source, supports RDFS/OWL reasoning
- **GraphDB:** Commercial engine with optimized inference
- **Virtuoso:** Enterprise RDF/SPARQL store with reasoning

---

## Production Systems

### Google Knowledge Graph

**Scale and Coverage:**
- 500+ million objects (entities)
- 3.5+ billion facts (relationships)
- Covers diverse domains: people, places, organizations, creative works, events

**Architecture Components:**

```
Data Collection:
  1. Web crawl + structured data (Schema.org)
  2. Wikipedia & Wikidata integration
  3. Public databases and APIs
  4. News and media monitoring
  5. User contributions and corrections
        ↓
Knowledge Graph Construction:
  - Entity extraction and disambiguation
  - Relationship extraction
  - Fact verification and conflict resolution
  - Entity resolution across sources
  - Quality scoring
        ↓
Knowledge Graph Maintenance:
  - Continuous crawl updates
  - Fact freshness monitoring
  - Contradiction detection
  - User feedback integration
        ↓
Search Integration:
  - Query understanding (NER + disambiguation)
  - Entity-aware ranking
  - Knowledge Panel generation
  - Result enrichment
        ↓
User-Facing Features:
  - Knowledge Panels
  - Related entities (carousel)
  - Structured answers
  - Entity cards in results
```

**Knowledge Panels:**
Google automatically generates information panels beside search results when:
- Entity has sufficient coverage across web
- Structured data quality is high
- User search intent matches entity
- Information can be reliably verified

**What Influences Panels:**
1. **Your Website + Schema.org:** Entity information with structured markup
2. **Wikipedia:** Most reliable source for notable entities
3. **Media Coverage:** Recent news and credible sources
4. **Public Data:** Government records, databases
5. **Aggregated Web Content:** Cross-site information synthesis

**Improvement Tactics:**
- Implement comprehensive Schema.org markup
- Create Wikipedia article (if notable)
- Ensure consistent information across web
- Link to authoritative sources
- Monitor Knowledge Panel accuracy
- Submit corrections through Google My Business

### Bing Satori

**Overview:**
Microsoft Satori is Bing's knowledge graph engine, built on:
- **Trinity:** Microsoft's distributed graph computing platform
- **RDF Model:** Uses semantic triples and SPARQL
- **Integration:** Particularly strong in LinkedIn data for people search

**Key Differentiators:**

1. **LinkedIn Integration:**
   - Professional information seamlessly integrated
   - People search enhanced with job history, education, skills
   - Unique competitive advantage for professional searches

2. **SPARQL Support:**
   - More open to structured queries
   - Some API access for developers
   - Semantic web standards-based

3. **Graph Database Foundation:**
   - Built on proper graph DB (Trinity), not inverted index overlay
   - More efficient relationship traversal
   - Better supports deep graph queries

**Use Cases:**
- Professional people search ("Find CEOs of automotive companies")
- Organizations and company information
- Educational institutions
- Locations and places
- News and media entities

### Amazon Product Graph

**Domain:** E-commerce product relationships and metadata

**Structure:**
```
Products
  ├─ Attributes: Price, Brand, Category, Reviews, Availability
  └─ Relationships:
      - belongsToCategory
      - manufacturedBy
      - similarTo
      - frequentlyBoughtWith
      - hasAlternative
      - isVariantOf

Categories
  ├─ Hierarchical classification
  └─ Cross-category relationships

Brands
  ├─ Manufacturer/seller info
  └─ Product associations

Users (implicit)
  └─ Purchase patterns (not directly exposed)
```

**Applications:**
- Personalized product recommendations
- "Customers also bought" suggestions
- Category suggestions and browsing
- Cross-selling and upselling
- Product similarity rankings
- Inventory optimization

**Technical Implementation:**
- Products as nodes with rich property sets
- Relationships captured as edges with weights/confidence
- Trained models for relationship generation
- Real-time graph update pipelines
- User-level personalization via collaborative filtering

### LinkedIn Knowledge Graph

**Purpose:** Professional profile and networking connections

**Entity Types:**
- **People:** User profiles with skills, education, experience
- **Companies:** Organization profiles, industries, locations
- **Schools:** Educational institutions
- **Skills:** Professional competencies
- **Jobs/Titles:** Positions and role information
- **Locations:** Geographic information

**Key Features:**

**1. People Search:**
- Filter by skills, company, education, location
- Advanced Boolean operators for recruiters
- Entity-based filtering vs. keyword search
- Relationship paths ("how you're connected")

**2. Graph-Based Recommendations:**
- "People you may know" (PPR-based)
- "Jobs you may be interested in" (skill + experience match)
- "Companies hiring people like you"
- Alumni networks and connections

**3. Engagement Ranking:**
- Who you should connect with (based on mutual connections)
- Relevant content (from people in your network/industry)
- Recruit recommendations (skill graph matching)

**Technical Architecture:**
```
User Profiles + Connections Graph
        ↓
Entity Recognition (extract skills, companies, etc.)
        ↓
Knowledge Graph:
  People --connected--> People
  People --worksAt--> Company
  People --studiedAt--> School
  People --hasSkill--> Skill
        ↓
Application Layers:
  - Search (entity + relationship queries)
  - Recommendation (personalized ranking)
  - Discovery (graph traversal for suggestions)
  - Analytics (aggregation over entity subgraphs)
```

### Wikidata: Open Knowledge Graph

**Unique Characteristics:**
- Community-edited, completely open
- 1.65 billion semantic triples
- Multilingual (100+ languages)
- Public API and SPARQL endpoint
- Embeddable in external projects

**Entity Identification:**
- QID: Persistent entity identifier (e.g., Q30 = USA)
- PID: Property identifier (e.g., P625 = coordinates)
- Versions tracked with edit history

**Data Model:**
```
Item (Q):
  {
    "id": "Q80",
    "label": "Tim Berners-Lee",
    "description": "inventor of the World Wide Web",
    "claims": {
      "P31": [  # instance of
        { "value": "Q5", "rank": "normal" }  # human
      ],
      "P625": [  # coordinates
        { "value": "51.2088, -0.1753", "rank": "normal" }
      ],
      "P937": [  # work location
        { "value": "Q34683", "rank": "normal" }  # MIT
      ]
    }
  }
```

**Semantic Search Enhancements:**

Wikidata Embedding Project adds vector-based search:
```
Traditional Wikidata Search:
  Query: "inventor of web" → String matching
  Result: May miss non-English labels, requires exact phrasing

Vector-Based Semantic Search:
  Query: "inventor of web"
  Embedding: Convert to vector
  Retrieve: Find entities with similar embeddings
  Result: Finds Tim Berners-Lee even with rephrased query
```

**Applications:**
- Fact-checking and knowledge verification
- Data integration across systems
- Research and academic knowledge exploration
- Wikipedia content enhancement
- External application knowledge augmentation

---

## Implementation Guide

### Building an Entity Search System

**Phase 1: Entity Extraction Pipeline**

**Step 1.1: Document Ingestion**
```python
from document_loader import PDFLoader, HTMLLoader, TextLoader

documents = []
for file_path in document_files:
    if file_path.endswith('.pdf'):
        loader = PDFLoader(file_path)
    elif file_path.endswith('.html'):
        loader = HTMLLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents.extend(loader.load())
```

**Step 1.2: Named Entity Recognition (NER)**
```python
from transformers import pipeline
from spacy.language import Language

# Option 1: Transformer-based (higher quality, slower)
ner_model = pipeline(
    "ner",
    model="dslim/bert-base-NER"
)

# Option 2: spaCy (balanced performance)
import spacy
nlp = spacy.load("en_core_web_lg")

for doc in documents:
    if using_transformers:
        entities = ner_model(doc.text)
    else:
        processed = nlp(doc.text)
        entities = [
            (ent.text, ent.label_)
            for ent in processed.ents
        ]

    doc.entities = entities
```

**Step 1.3: Entity Linking to Knowledge Base**

```python
from entity_linker import EntityLinker
from knowledge_base import WikidataKB, DBpediaKB

linker = EntityLinker(
    knowledge_base=WikidataKB(),
    threshold=0.85  # confidence threshold
)

for doc in documents:
    for entity_text, entity_type in doc.entities:
        # Find candidates and disambiguate
        links = linker.link(
            entity_text,
            entity_type,
            context=doc.text  # use document context
        )

        doc.entity_links[entity_text] = {
            'candidates': links['candidates'],  # ranked options
            'best_match': links['best'],  # top choice
            'confidence': links['score']
        }
```

**Step 1.4: Entity Resolution (Deduplication)**

```python
from entity_resolver import EntityResolver

resolver = EntityResolver()

# Collect all unique entity mentions
entity_mentions = {}
for doc in documents:
    for entity_text, linked_entity in doc.entity_links.items():
        qid = linked_entity['best_match']['qid']
        if qid not in entity_mentions:
            entity_mentions[qid] = []
        entity_mentions[qid].append({
            'mention': entity_text,
            'doc_id': doc.id,
            'context': doc.text,
            'confidence': linked_entity['confidence']
        })

# Deduplicate and merge
resolved_entities = {}
for qid, mentions in entity_mentions.items():
    # Take canonical form (most confident mention)
    canonical = sorted(
        mentions,
        key=lambda x: x['confidence'],
        reverse=True
    )[0]

    resolved_entities[qid] = {
        'canonical_name': canonical['mention'],
        'mention_count': len(mentions),
        'document_count': len(set(m['doc_id'] for m in mentions)),
        'all_mentions': [m['mention'] for m in mentions],
        'confidence': canonical['confidence']
    }
```

**Phase 2: Knowledge Graph Population**

**Step 2.1: Relation Extraction**

```python
from relation_extractor import RelationExtractor

extractor = RelationExtractor(model="re-trained-bert")

relationships = []
for doc in documents:
    # Find entity pairs in proximity
    entity_pairs = find_nearby_entities(doc.entities, window=50)

    for entity1, entity2 in entity_pairs:
        # Extract relationship
        relation = extractor.extract(
            entity1,
            entity2,
            context_text=doc.text
        )

        if relation['confidence'] > 0.7:
            relationships.append({
                'source': entity1['linked_qid'],
                'target': entity2['linked_qid'],
                'relation_type': relation['type'],
                'confidence': relation['confidence'],
                'source_doc': doc.id,
                'evidence': doc.text[relation['start']:relation['end']]
            })
```

**Step 2.2: Building the Graph**

```python
import neo4j
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

def create_graph(driver, entities, relationships):
    with driver.session() as session:
        # Create entity nodes
        for qid, entity_info in entities.items():
            session.run("""
                CREATE (n:Entity {
                    qid: $qid,
                    name: $name,
                    type: $type,
                    mention_count: $count,
                    confidence: $confidence
                })
            """, {
                'qid': qid,
                'name': entity_info['canonical_name'],
                'type': entity_info.get('type', 'UNKNOWN'),
                'count': entity_info['mention_count'],
                'confidence': entity_info['confidence']
            })

        # Create relationships
        for rel in relationships:
            session.run("""
                MATCH (a:Entity {qid: $source})
                MATCH (b:Entity {qid: $target})
                CREATE (a)-[r:RELATED {
                    type: $rel_type,
                    confidence: $confidence,
                    source_doc: $doc,
                    evidence: $evidence
                }]->(b)
            """, rel)

        # Create full-text index
        session.run("""
            CREATE FULLTEXT INDEX entity_search
            FOR (n:Entity)
            ON EACH [n.name]
        """)

create_graph(driver, resolved_entities, relationships)
```

**Phase 3: Search Implementation**

**Step 3.1: Full-Text + Graph Retrieval**

```python
def entity_search(driver, query, top_k=10):
    with driver.session() as session:
        # Step 1: Full-text search for initial entity set
        initial_results = session.run("""
            CALL db.index.fulltext.queryNodes("entity_search", $query)
            YIELD node, score
            RETURN node.qid as qid, node.name as name, score
            ORDER BY score DESC
            LIMIT $limit
        """, {
            'query': query,
            'limit': top_k * 2  # Get more for filtering
        })

        entity_qids = [r['qid'] for r in initial_results]

        # Step 2: Enhance with graph context
        enhanced_results = session.run("""
            MATCH (entity:Entity)
            WHERE entity.qid IN $qids
            OPTIONAL MATCH (entity)-[r:RELATED]-(related:Entity)
            RETURN
                entity.qid as qid,
                entity.name as name,
                entity.mention_count as popularity,
                collect({
                    name: related.name,
                    relation: type(r),
                    confidence: r.confidence
                }) as related_entities
            LIMIT $limit
        """, {
            'qids': entity_qids,
            'limit': top_k
        })

        return enhanced_results

# Query example
results = entity_search(driver, "machine learning frameworks")
for result in results:
    print(f"Entity: {result['name']} (QID: {result['qid']})")
    print(f"  Mentions: {result['popularity']}")
    print(f"  Related: {[r['name'] for r in result['related_entities']]}")
```

**Step 3.2: Personalized Ranking**

```python
def personalized_entity_search(driver, query, user_profile, top_k=10):
    """
    Use PPR to personalize ranking based on user interests
    """
    with driver.session() as session:
        # Find seed entities from user profile
        seed_query = """
            MATCH (entity:Entity)
            WHERE entity.qid IN $user_interests
            RETURN entity.qid as qid
        """
        seed_results = session.run(
            seed_query,
            {'user_interests': user_profile['interests']}
        )
        seed_entities = [r['qid'] for r in seed_results]

        # Full-text search for query
        initial_results = session.run("""
            CALL db.index.fulltext.queryNodes("entity_search", $query)
            YIELD node, score
            RETURN node.qid as qid, score
            LIMIT $limit
        """, {
            'query': query,
            'limit': top_k * 3
        })

        query_entities = [r['qid'] for r in initial_results]

        # Compute personalized PageRank
        ppr_scores = compute_personalized_pagerank(
            driver,
            seed_entities,
            query_entities,
            damping_factor=0.85
        )

        # Return top-k by combined score
        combined_scores = {}
        for qid in query_entities:
            text_score = next(
                (r['score'] for r in initial_results
                 if r['qid'] == qid), 0.5
            )
            graph_score = ppr_scores.get(qid, 0.1)
            combined_scores[qid] = 0.7 * text_score + 0.3 * graph_score

        top_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return top_results
```

### Populating Knowledge Graphs from Documents

**Best Practices:**

1. **Progressive Extraction:**
   - Start with high-confidence extractions only
   - Add lower-confidence relationships with quality flags
   - Continuously verify and update as more data arrives

2. **Quality Control:**
   - Manual verification of sample extractions
   - Cross-reference with existing knowledge bases
   - Track confidence scores through pipeline
   - Flag controversial or conflicting information

3. **Incremental Updates:**
   - Don't rebuild entire graph from scratch
   - Process new documents through extraction pipeline
   - Apply entity resolution to connect to existing entities
   - Update relationship weights as evidence accumulates

4. **Schema Evolution:**
   - Start with simple schema (entity + relation type)
   - Add properties as needed
   - Version schema changes
   - Maintain backward compatibility

### Entity Resolution at Scale

**Challenge:** Multiple mentions of same entity across documents

```
Mentions of Tesla Inc:
  - "Tesla" (ambiguous)
  - "Tesla Inc" (specific)
  - "Tesla Motors" (old name)
  - "TSLA" (ticker)
  - "The electric car company founded by Elon Musk"

Goal: All resolve to single canonical entity
```

**Approaches:**

**1. String Similarity-Based:**
```python
from difflib import SequenceMatcher

def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

mentions = ["Tesla", "Tesla Inc", "Tesla Motors", "TSLA"]
canonical = "Tesla Inc"

for mention in mentions:
    sim = string_similarity(mention.lower(), canonical.lower())
    if sim > 0.8:
        print(f"{mention} → {canonical} (similarity: {sim})")
```

**2. Embedding-Based:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

mention_embeddings = {
    mention: model.encode(mention)
    for mention in mentions
}

canonical_embedding = model.encode("Tesla Inc")

# Find closest mentions
from sklearn.metrics.pairwise import cosine_similarity

for mention, emb in mention_embeddings.items():
    similarity = cosine_similarity([emb], [canonical_embedding])[0][0]
    if similarity > 0.9:
        print(f"{mention} ← similar to → Tesla Inc")
```

**3. Context-Based (LLM):**
```python
from openai import OpenAI

client = OpenAI()

def resolve_entity_llm(mention, context, kb_candidate):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"""
            Context: {context}
            Mention: "{mention}"

            Does this mention refer to {kb_candidate}?
            Answer with confidence 0-100.
            """
        }]
    )
    return float(response.choices[0].message.content)

# Use for ambiguous cases
confidence = resolve_entity_llm(
    mention="Tesla",
    context="Tesla revolutionized the electric vehicle industry",
    kb_candidate="Tesla Inc (electric vehicle company)"
)
```

**4. Semantic Matching (Ontology-Based):**
```python
from owlready2 import *

# Load ontology with entity relationships
onto = get_ontology("entities.owl")

class Company(Thing):
    pass

class TeslaInc(Company):
    aliases = ["Tesla", "Tesla Inc", "Tesla Motors", "TSLA"]

def resolve_mention(mention):
    for entity in Company.subclasses():
        if mention in entity.aliases:
            return entity
        # Check parent class for inheritance
        if mention in entity.ancestors():
            return entity
    return None
```

---

## Decision Framework

### When to Use Graph Search vs. Traditional IR

**Use Traditional Full-Text Search (Elasticsearch, Lucene) When:**

✓ Queries are primarily keyword-based ("machine learning tutorial")
✓ Document relevance dominates over relationships
✓ Latency is critical (sub-100ms requirement)
✓ Index size must be minimal
✓ Schema is fixed and simple
✓ Real-time indexing isn't required
✓ Team lacks graph database expertise

**Example:**
```
Blog search: User types keywords, wants relevant articles
Traditional IR sufficient: Lucene full-text + BM25 ranking
```

**Use Entity-Centric Search When:**

✓ Users search for entities primarily (people, companies, products)
✓ Relationships between entities matter to relevance
✓ Entity disambiguation is common
✓ Users benefit from "related entities" suggestions
✓ Ambiguity resolution is important
✓ Rich entity metadata is available

**Example:**
```
People search on LinkedIn: "Find Python developers in SF working at startups"
Need entity search: Developer (person entity) with skills (relation),
location (relation), company type (relation)
```

**Use Knowledge Graphs (GraphRAG) When:**

✓ Questions require holistic understanding of dataset
✓ Complex reasoning over multiple documents needed
✓ Context summarization is important
✓ Answers span multiple information sources
✓ Pattern discovery and analysis required
✓ Sufficient latency budget (seconds acceptable)
✓ Relationships are as important as content

**Example:**
```
"How does the company's technology strategy across all divisions
align with recent market trends?" (complex Q)
Need GraphRAG: Extract entities, build graph, detect patterns across
documents, hierarchical summarization, LLM reasoning
```

**Use Semantic Web (SPARQL, OWL) When:**

✓ Reasoning and inference is core requirement
✓ Schema and ontology define domain precisely
✓ Data interoperability with external systems needed
✓ Query expressiveness is more important than performance
✓ Publishing data on semantic web is goal
✓ Domain experts define ontology

**Example:**
```
Bioinformatics: "Find all proteins that interact with disease X
through a chain of at most 3 intermediary interactions"
Need SPARQL: Complex traversal queries, inference over protein
interactions, cross-database linking
```

### Technology Selection Matrix

| Requirement | Full-Text | Entity Search | Knowledge Graph | GraphRAG | Semantic Web |
|-------------|-----------|---------------|-----------------|----------|--------------|
| Latency | **Excellent** | Good | Good | Fair | Poor |
| Relationship Queries | Poor | **Excellent** | **Excellent** | **Excellent** | **Excellent** |
| Reasoning/Inference | None | Limited | Good | Good | **Excellent** |
| Implementation Complexity | Low | Medium | Medium-High | High | Very High |
| Query Expressiveness | Low | Medium | High | High | **Very High** |
| Scalability | Excellent | Excellent | Good | Fair | Varies |
| Learning Curve | Low | Medium | Medium-High | High | Very High |
| Operational Overhead | Low | Medium | Medium | High | High |

### Complexity vs. Value Analysis

**Start Simple:**
1. Full-text search (low-hanging fruit)
2. Add entity extraction and linking
3. Build entity-centric search
4. Add relationship context

**Only add complexity if:**
- Current system doesn't meet requirements
- Value of improvement justifies engineering cost
- Team has necessary expertise
- Use case genuinely requires capability

**Common Mistakes:**
- Over-engineering simple searches (using GraphRAG for keyword queries)
- Under-engineering complex requirements (using keyword search for entity discovery)
- Choosing technology by hype rather than fit
- Building without clear performance requirements

### Migration Path

**Phase 1: Augment Existing Search**
```
Existing: Elasticsearch for document search
Add: Entity extraction + linking layer
Benefit: Better disambiguation, related entities
Cost: Moderate (add post-processing pipeline)
```

**Phase 2: Build Entity Index**
```
Existing: Document + entity extraction
Add: Dedicated entity search index
Benefit: Entity-first results, entity relationships
Cost: Moderate (new index, new retrieval logic)
```

**Phase 3: Add Graph Layer**
```
Existing: Entity search index
Add: Graph database with entity relationships
Benefit: Relationship-aware ranking, multi-hop queries
Cost: High (new infrastructure, complex queries)
```

**Phase 4: Advanced Reasoning (if needed)**
```
Existing: Graph database
Add: GraphRAG or semantic web layer
Benefit: Complex reasoning, cross-document synthesis
Cost: Very High (significant engineering effort)
```

---

## Summary: Key Takeaways

### Fundamental Concepts

1. **Knowledge graphs** represent entities and relationships as semantic triples (subject-predicate-object)
2. **Entity linking** connects text mentions to canonical knowledge base identifiers
3. **Graph traversal** algorithms (PageRank, PPR) measure importance within networks
4. **Semantic web** standards (RDF, SPARQL, OWL) enable machine-readable, reasoning-capable knowledge representation
5. **Community detection** (used in GraphRAG) identifies densely-connected clusters in graphs for better summarization

### Technology Landscape

- **Graph Databases:** Neo4j, Amazon Neptune, ArangoDB, TigerGraph enable native relationship queries
- **Semantic Web:** RDF, SPARQL, OWL provide reasoning and inference capabilities
- **Production Systems:** Google Knowledge Graph, Bing Satori, LinkedIn Knowledge Graph, Amazon Product Graph demonstrate production viability
- **Emerging:** GraphRAG combines graph structure with LLM reasoning for complex document understanding

### Implementation Approach

1. Extract entities from documents using NER
2. Link entities to knowledge base
3. Resolve duplicates (entity resolution)
4. Extract and store relationships
5. Implement search combining full-text + graph traversal
6. Layer on ranking (popularity, relevance, personalization)
7. Add reasoning/summarization as needed

### Decision Framework

- Use **traditional IR** for fast, keyword-based search
- Use **entity search** for entity-centric queries with relationship context
- Use **knowledge graphs** for complex multi-hop relationships
- Use **GraphRAG** for dataset-level understanding and synthesis
- Use **semantic web** for formal reasoning and interoperability

The optimal approach often combines multiple techniques: full-text search for initial relevance, entity linking for disambiguation, graph traversal for relationship context, and potentially GraphRAG for complex synthesis.

---

## References and Further Reading

### Core Concepts
- [The Anatomy of a Content Knowledge Graph | Schema App Solutions](https://www.schemaapp.com/schema-markup/the-anatomy-of-a-content-knowledge-graph/)
- [Knowledge Graphs: What They Are and Why They Matter | Splunk](https://www.splunk.com/en_us/blog/learn/knowledge-graphs.html)
- [Enterprise Knowledge Graph Overview | Google Cloud Documentation](https://docs.cloud.google.com/enterprise-knowledge-graph/docs/overview)

### Knowledge Graph Search
- [How Google's Knowledge Graph Works - Knowledge Panel Help](https://support.google.com/knowledgepanel/answer/9787176?hl=en)
- [Google Knowledge Graph Search API | Google for Developers](https://developers.google.com/knowledge-graph)
- [Understanding Google Knowledge Graphs](https://global-lingo.com/understanding-google-knowledge-graphs/)

### Graph Databases
- [Fulltext Search in Neo4j - Knowledge Base](https://neo4j.com/developer/kb/fulltext-search-in-neo4j/)
- [Enhancing Hybrid Retrieval With Graph Traversal Using the GraphRAG Python Package](https://neo4j.com/blog/developer/enhancing-hybrid-retrieval-graphrag-python-package/)
- [Amazon Neptune vs. TigerGraph Comparison | DB-Engines](https://db-engines.com/en/system/Amazon+Neptune%3BTigerGraph)

### Entity Recognition and Linking
- [Named Entity Recognition | GraphRAG](https://graphrag.com/reference/preparation/ner/)
- [Entity Linking | NLP-Progress](http://nlpprogress.com/english/entity_linking.html)
- [What Is Named Entity Recognition? | IBM](https://www.ibm.com/think/topics/named-entity-recognition)

### Graph Algorithms
- [PageRank Algorithm for Graph Databases](https://memgraph.com/blog/pagerank-algorithm-for-graph-databases)
- [Efficient Algorithms for Personalized PageRank Computation: A Survey](https://arxiv.org/html/2403.05198v1)
- [PageRank Centrality Algorithm - Neptune Analytics](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/page-rank.html)

### GraphRAG
- [GraphRAG: Improving Global Search via Dynamic Community Selection - Microsoft Research](https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/)
- [Welcome - GraphRAG](https://microsoft.github.io/graphrag/)
- [How Would Microsoft GraphRAG Work Alongside a Graph Database? | Memgraph](https://memgraph.com/blog/how-microsoft-graphrag-works-with-graph-databases)

### Semantic Web
- [RDF and SPARQL: Using Semantic Web Technology to Integrate the World's Data](https://www.w3.org/2007/03/VLDB/)
- [Introduction to the Semantic Web — GraphDB Documentation](https://graphdb.ontotext.com/documentation/11.2/introduction-to-semantic-web.html)
- [OWL - Semantic Web Standards](https://www.w3.org/OWL/)

### Production Systems
- [Knowledge Graphs in Google and Bing: Importance, Differences, and SEO Integration](https://coraseosoftware.net/knowledge-graphs-in-google-and-bing/)
- [Bing Now Knows Much More About People And Places Thanks To Satori | TechCrunch](https://techcrunch.com/2013/03/21/bing-just-got-a-lot-smarter-now-knows-more-about-people-and-places/)
- [Wikidata: A Free and Open Knowledge Base](https://www.wikidata.org/)

### Entity Resolution
- [Entity Resolved Knowledge Graphs: A Tutorial | Neo4j](https://neo4j.com/blog/developer/entity-resolved-knowledge-graphs/)
- [Combining Entity Resolution and Knowledge Graphs | Linkurious](https://linkurious.com/blog/entity-resolution-knowledge-graph/)
- [Entity Resolution at Scale: Deduplication Strategies | Medium](https://medium.com/@shereshevsky/entity-resolution-at-scale-deduplication-strategies-for-knowledge-graph-construction-7499a60a97c3)

### Advanced Topics
- [Query-Centric Graph Retrieval Augmented Generation](https://arxiv.org/pdf/2509.21237)
- [Graph-Based Entity-Oriented Search: A Unified Framework | PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7148020/)
- [Wikidata Embedding Project - Wikidata](https://www.wikidata.org/wiki/Wikidata:Embedding_Project)

---

**Document Version:** 1.0
**Last Updated:** March 2026
**Author:** Search Mastery Reference Series
**Status:** Complete Reference Material
