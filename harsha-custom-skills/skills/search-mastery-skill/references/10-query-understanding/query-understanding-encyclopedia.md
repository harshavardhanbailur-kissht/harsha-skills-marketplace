# Query Understanding Encyclopedia: The Complete NLP Pipeline for Search

## Overview: Why Query Understanding Matters

Query understanding is the foundation of modern search systems. Before ranking documents or retrieving results, a search engine must first understand what the user is actually asking for. This process transforms raw, noisy user input into a structured, semantically rich representation that can be used for effective retrieval and ranking.

According to modern search research, **query understanding improvements often have greater impact on overall search quality than ranking improvements alone**. This is because:

1. A perfectly ranked wrong set of results is useless
2. Proper query understanding enables semantic matching rather than keyword matching
3. It unlocks support for complex, ambiguous, and conversational queries
4. It allows for intelligent query reformulation and clarification

The complete query understanding pipeline typically involves:
1. **Preprocessing** - Cleaning and normalizing raw input
2. **Expansion** - Enriching queries with semantically related terms
3. **Rewriting** - Transforming queries into canonical forms
4. **Intent Classification** - Understanding user goals (navigational, informational, transactional)
5. **Named Entity Recognition** - Extracting semantic entities
6. **Query Segmentation** - Breaking queries into meaningful chunks
7. **Classification & Routing** - Directing queries to appropriate backends
8. **Context Management** - Handling multi-turn and conversational scenarios

---

## 1. Query Understanding Pipeline Architecture

### The Complete Flow

```
Raw Query Input
    ↓
[Preprocessing Layer]
    ├─ Tokenization
    ├─ Lowercasing
    ├─ Spell Correction
    ├─ Normalization
    └─ Stop Word Handling
    ↓
[Enrichment Layer]
    ├─ Query Expansion
    ├─ Synonym Extraction
    ├─ Entity Recognition
    └─ Named Entity Linking
    ↓
[Analysis Layer]
    ├─ Intent Classification
    ├─ Query Segmentation
    ├─ Language Detection
    └─ Content Type Classification
    ↓
[Rewriting Layer]
    ├─ Abbreviation Expansion
    ├─ Concatenation Splitting
    ├─ LLM-based Reformulation
    └─ Query Relaxation
    ↓
[Routing Layer]
    ├─ Backend Selection
    ├─ Safety Filtering
    ├─ Feature Engineering
    └─ Context Injection
    ↓
Structured Query Representation
    ↓
[Retrieval/Ranking]
```

### Key Principles

**1. The Google Approach**
Google's massive query understanding system leverages:
- Trillions of historical query logs
- Click-through data and user behavior signals
- Deep learning models trained on query-result pairs
- Real-time feedback loops for continuous improvement

For smaller systems without Google's scale:
- Focus on high-value transformations first
- Use pretrained models (BERT, spaCy, fastText)
- Build from publicly available datasets
- Implement feedback loops to improve over time

**2. Query Log Complexity**
Most real-world queries face challenges:
- **Typos and misspellings**: "iphone 14 promax" vs "iphone 14 pro max"
- **Abbreviations**: "NYC pizza" vs "New York City pizza"
- **Ambiguity**: Does "apple" mean the fruit or the company?
- **Short fragments**: Users often type 2-3 words, not full sentences
- **Implicit context**: "best nearby" requires location context

**3. The Long Tail Problem**
- 20% of queries are "head" queries (frequently repeated)
- 30% are "torso" queries (moderately common)
- 50% are "long-tail" queries (unique or rare)

Long-tail queries require smarter understanding because they can't rely on historical click data alone.

---

## 2. Query Preprocessing: Cleaning the Raw Input

Preprocessing is the foundation. Clean input means better signals throughout the pipeline.

### 2.1 Tokenization

Tokenization breaks text into meaningful units. The strategy depends on your model:

```python
# Basic word tokenization
text = "What's the best pizza in NYC?"
tokens = text.split()  # ["What's", "the", "best", "pizza", "in", "NYC?"]

# Whitespace + punctuation aware
import re
tokens = re.split(r'\W+', text.lower())  # ["what", "s", "the", "best", "pizza", "in", "nyc"]

# Subword tokenization for transformers (BERT)
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
tokens = tokenizer.tokenize(text)  # ["what", "'", "s", "the", "best", "pizza", "in", "nyc", "?"]
```

**Key Decision**: Traditional models need careful tokenization, but BERT and other transformers handle it internally. For search, you typically want:
- Whitespace splitting as primary delimiter
- Punctuation attachment aware of context (URLs, prices, etc.)
- Compound word handling ("co-founder" stays together)

### 2.2 Lowercasing and Normalization

Normalize variations to a canonical form:

```python
# Basic lowercasing
query = "BEST iPhone 14 Pro Max DEALS"
normalized = query.lower()  # "best iphone 14 pro max deals"

# Unicode normalization (handling accents, special chars)
import unicodedata
text = "café"
normalized = unicodedata.normalize('NFKD', text)
# 'café' -> 'cafe' (decomposed form)

# Domain-specific normalization
# Phone numbers: "1-800-FLOWERS" -> "1800flowers"
# Prices: "$19.99" -> "19.99"
# Product codes: handle both "iPhone-14" and "iPhone 14"
```

### 2.3 Spell Correction: From Typos to Intent

Spell correction is more nuanced than it appears. Sometimes a "misspelling" is actually a valid variant or user preference.

#### Peter Norvig's Algorithm (Baseline)

Peter Norvig's famous spell corrector uses edit distance and frequency:

```python
def edits1(word):
    """All edits that are one edit away from word"""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def known(words):
    """Filter words that exist in dictionary"""
    return set(w for w in words if w in NWORDS)

def correct(word):
    """Find most likely correction"""
    candidates = (known([word]) or
                  known(edits1(word)) or
                  known(edits2(word)) or
                  [word])
    return max(candidates, key=lambda w: NWORDS[w])
```

**Problem**: This is slow for large dictionaries and doesn't scale. Edit distance grows exponentially.

#### SymSpell: 1 Million Times Faster

SymSpell uses the Symmetric Delete algorithm, which is dramatically faster:

```python
# Key insight: Instead of generating all edits of the query word,
# generate all edits of dictionary words and store them
# Then only do deletes (not inserts/replaces) on the query

# Pre-processing: Build dictionary with all delete variants
dictionary = {}  # max_edit_distance: [words]

for word in word_list:
    for d in range(1, max_distance + 1):
        # Generate all d-length deletions of word
        variants = all_deletes(word, d)
        for variant in variants:
            if variant not in dictionary:
                dictionary[variant] = []
            dictionary[variant].append(word)

# Query time: Only delete from query
def correct_word(query_word, max_distance=2):
    candidates = set()
    for d in range(1, max_distance + 1):
        for variant in all_deletes(query_word, d):
            if variant in dictionary:
                candidates.update(dictionary[variant])
    # Score by edit distance + frequency
    return sorted(candidates, key=frequency, reverse=True)[0]
```

**Performance**: SymSpell is 1 million times faster than Norvig's algorithm while achieving better accuracy.

#### BK-Trees: Another Approach

BK-trees (Burkhard-Keller trees) organize words in metric space:

```python
class BKNode:
    def __init__(self, word):
        self.word = word
        self.children = {}  # {distance: child_node}

# Building: Insert words into tree by edit distance
def insert(node, word):
    if node is None:
        return BKNode(word)

    d = levenshtein_distance(word, node.word)
    if d == 0:
        return node  # Word already exists

    if d not in node.children:
        node.children[d] = BKNode(word)
    else:
        node.children[d] = insert(node.children[d], word)
    return node

# Searching: Use triangle inequality to prune search space
def search(node, query, max_distance):
    if node is None:
        return []

    d = levenshtein_distance(query, node.word)
    results = []

    if d <= max_distance:
        results.append(node.word)

    # Triangle inequality: only explore children within range
    for distance, child in node.children.items():
        if abs(distance - d) <= max_distance:
            results.extend(search(child, query, max_distance))

    return results
```

**Comparison Summary**:
- **Norvig**: Simple, understandable, too slow
- **SymSpell**: Very fast (1M+ times faster), 100x faster than BK-tree
- **BK-Tree**: Good balance, 100x slower than SymSpell but scalable

### 2.4 Whitespace and Special Character Handling

```python
# Normalize multiple spaces
query = "best    pizza    near me"
normalized = ' '.join(query.split())  # "best pizza near me"

# Handle special characters based on context
# URLs: "www.example.com" -> keep intact or recognize as entity
# Prices: "$19.99" -> remove $ or normalize to "19.99"
# Hashtags: "#python" -> keep or convert to "python"
# Email: "john@example.com" -> recognize as entity

# Regex-based cleaning
import re
def clean_query(query):
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query)
    # Normalize quotes
    query = re.sub(r'[""'']', '"', query)
    # Remove control characters
    query = re.sub(r'[\x00-\x1f\x7f]', '', query)
    return query.strip()
```

---

## 3. Query Expansion: Making Connections

Query expansion enriches the user's query with related and synonymous terms. This helps retrieve relevant documents that use different vocabulary.

### 3.1 Synonym-Based Expansion

#### Manual Thesaurus Approach
Create hand-curated synonym lists for your domain:

```python
synonyms = {
    'cheap': ['inexpensive', 'affordable', 'budget', 'low-cost'],
    'buy': ['purchase', 'acquire', 'get', 'shop'],
    'restaurant': ['dining', 'eatery', 'bistro', 'cafe'],
    'car': ['automobile', 'vehicle', 'motor', 'auto'],
}

def expand_query_manual(query):
    tokens = query.split()
    expanded = set(tokens)

    for token in tokens:
        if token in synonyms:
            expanded.update(synonyms[token])

    return list(expanded)

# Example: "cheap restaurant" expands to include
# "inexpensive dining", "affordable eatery", etc.
```

**Pros**: Domain-specific, controllable, reliable
**Cons**: Manual maintenance, limited coverage, doesn't scale

#### WordNet-Based Expansion

WordNet is a large lexical database of English:

```python
from nltk.corpus import wordnet

def expand_with_wordnet(query):
    tokens = query.split()
    expanded = set(tokens)

    for token in tokens:
        synsets = wordnet.synsets(token)
        for synset in synsets:
            # Get lemmas (word forms) for this meaning
            for lemma in synset.lemmas():
                expanded.add(lemma.name().replace('_', ' '))

    return list(expanded)

# Example: "bank" expands to:
# {bank, depository, bank, river_bank, slope, financial_institution, ...}
```

**Pros**: Large coverage, automatic
**Cons**: Limited to common words, doesn't capture domain-specific meanings, can introduce noise

### 3.2 Embedding-Based Expansion

Modern approach using word embeddings to find semantically similar terms:

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Pretrained word vectors (e.g., from Word2Vec, GloVe, FastText)
word_vectors = {...}  # word -> embedding vector

def expand_with_embeddings(query, top_k=5):
    tokens = query.split()
    expanded = set(tokens)

    for token in tokens:
        if token in word_vectors:
            query_vec = word_vectors[token].reshape(1, -1)

            # Find most similar words in vocabulary
            similarities = {}
            for word, vec in word_vectors.items():
                vec = vec.reshape(1, -1)
                sim = cosine_similarity(query_vec, vec)[0][0]
                similarities[word] = sim

            # Get top_k most similar
            top_similar = sorted(
                similarities.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_k]

            expanded.update([word for word, _ in top_similar])

    return list(expanded)

# Example: "pizza" expands to include
# "spaghetti", "pasta", "lasagna" based on semantic similarity
```

**Pros**: Automatic, captures semantic relationships, scalable
**Cons**: Requires large corpus for training, generic (not domain-specific without fine-tuning)

### 3.3 Query Relaxation for Zero Results

When a query returns zero results, intelligently relax it:

```python
def relax_query(query, current_results_count):
    if current_results_count > 0:
        return query  # Results exist, no need to relax

    tokens = query.split()

    # Strategy 1: Remove least frequent terms
    term_frequencies = {...}  # word -> frequency in corpus
    removable = sorted(tokens, key=lambda t: term_frequencies.get(t, 0))

    for token in removable:
        relaxed = ' '.join([t for t in tokens if t != token])
        relaxed_results = search(relaxed)
        if len(relaxed_results) > 0:
            return relaxed

    # Strategy 2: Replace with synonyms/broader terms
    for i, token in enumerate(tokens):
        for synonym in get_broader_synonyms(token):
            relaxed = tokens[:i] + [synonym] + tokens[i+1:]
            relaxed_results = search(' '.join(relaxed))
            if len(relaxed_results) > 0:
                return ' '.join(relaxed)

    return query  # Give up, return original
```

### 3.4 Pseudo-Relevance Feedback (PRF)

Refine the original query based on top-k initial results:

```python
def apply_prf(original_query, top_k_docs, iterations=1):
    """
    Pseudo-Relevance Feedback:
    Assume top_k results are relevant and use them to expand query
    """
    expanded_query = original_query

    for iteration in range(iterations):
        # Retrieve documents with current query
        results = search(expanded_query, top_k=top_k_docs)

        # Extract important terms from top results
        all_terms = []
        for doc in results:
            doc_tokens = tokenize(doc.content)
            all_terms.extend(doc_tokens)

        # Score terms by TF-IDF or other metric
        term_scores = score_terms(all_terms)

        # Add top scoring terms to query
        top_terms = sorted(
            term_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Add top 5 terms

        expanded_query = original_query + ' ' + ' '.join([
            term for term, _ in top_terms
        ])

    return expanded_query
```

---

## 4. Query Rewriting: Transformation Techniques

Query rewriting transforms the query into equivalent or improved forms.

### 4.1 Abbreviation and Acronym Expansion

```python
# Curated abbreviation dictionary
abbreviations = {
    'NYC': 'New York City',
    'SF': 'San Francisco',
    'CA': 'California',
    'US': 'United States',
    'API': 'Application Programming Interface',
    'ML': 'Machine Learning',
    'AI': 'Artificial Intelligence',
}

def expand_abbreviations(query):
    tokens = query.split()
    expanded = []

    for token in tokens:
        token_clean = token.rstrip('.,!?;:')
        punctuation = token[len(token_clean):]

        if token_clean in abbreviations:
            expanded.append(abbreviations[token_clean] + punctuation)
        else:
            expanded.append(token)

    return ' '.join(expanded)

# "Find restaurants in SF" -> "Find restaurants in San Francisco"
# "ML engineer jobs in NYC" -> "Machine Learning engineer jobs in New York City"
```

### 4.2 Concatenation Splitting

Handle cases where users don't use spaces properly:

```python
def should_split(token, context):
    """
    Heuristic: Split if token is:
    - Very long (>15 chars) and contains natural word boundaries
    - Matches known compound patterns
    """
    if len(token) > 15:
        # Try common dictionary-based splits
        for i in range(1, len(token)):
            left = token[:i]
            right = token[i:]
            if is_valid_word(left) and is_valid_word(right):
                # Heuristic: both parts should be reasonably long
                if len(left) >= 3 and len(right) >= 3:
                    return (left, right)

    return None

def split_concatenations(query):
    tokens = query.split()
    result = []

    for token in tokens:
        split = should_split(token)
        if split:
            result.extend(split)
        else:
            result.append(token)

    return ' '.join(result)

# "newyorkpizza" -> "new york pizza"
# "iphonecase" -> "iphone case"
```

### 4.3 Entity-Based Rewriting

Enrich query with structured information about entities:

```python
def rewrite_with_entity_context(query, entity_kb):
    """
    If query contains known entity, add context
    Example: "Apple" -> "Apple, a technology company known for iPhones, iPads, and software"
    """
    entities = extract_entities(query)
    enriched_query = query

    for entity in entities:
        if entity in entity_kb:
            context = entity_kb[entity]
            enriched_query += f" ({context})"

    return enriched_query

# entity_kb example:
entity_kb = {
    'Apple': 'technology company known for iPhones, Macs, and software services',
    'Tesla': 'electric vehicle manufacturer founded by Elon Musk',
    'Amazon': 'e-commerce and cloud computing company',
}

# "Apple products" -> "Apple products (technology company known for iPhones, Macs, and software services)"
```

### 4.4 LLM-Powered Query Rewriting

Use large language models for flexible query rewriting:

```python
from transformers import pipeline

def rewrite_with_llm(query, instruction="clarify"):
    """
    Use LLM for query transformation
    """
    prompt = f"User query: {query}\nTask: {instruction}\nRewritten query:"

    # Use appropriate instruction based on task
    if instruction == "clarify":
        prompt = f"User query: {query}\nMake this query more specific and clear:\n"
    elif instruction == "expand":
        prompt = f"User query: {query}\nExpand this query with related concepts:\n"
    elif instruction == "simplify":
        prompt = f"User query: {query}\nSimplify this complex query:\n"

    generator = pipeline("text-generation", model="gpt2")
    result = generator(prompt, max_length=100)

    return result[0]['generated_text']
```

**Important**: Structured prompts work better than free-form. Instead of allowing the LLM to rewrite freely, provide a strict template:

```python
def structured_query_rewrite(query, template="{original} focused on {focus}"):
    """
    Template-based rewriting for reliability
    """
    prompt = f"""Given the user query: "{query}"

Fill in the template:
{template}

Where {original} is the original query and {focus} is what aspect to emphasize.
Output ONLY the completed template, no explanation."""

    return llm_call(prompt)
```

---

## 5. Intent Classification: Understanding User Goals

Andrei Broder's taxonomy (2002) remains the foundation of search intent classification:

### 5.1 The Three Intent Categories

#### Navigational Intent (~10% of queries)
User wants to reach a specific website or page they have in mind.

```
Examples:
- "facebook"
- "gmail login"
- "amazon.com"
- "wikipedia python"
- "github tensorflow"

Signals:
- Single brand/site name
- "login", "sign up", "download"
- Home page or specific path
- Usually 1-2 words
```

#### Informational Intent (~80% of queries)
User wants to learn about a topic or find information.

```
Examples:
- "how to make pizza dough"
- "best practices machine learning"
- "python list methods"
- "what is photosynthesis"
- "history of the internet"

Signals:
- Question words (how, what, why, when, where, who)
- "tips", "guide", "tutorial", "explanation"
- Multiple related keywords
- Usually longer queries
```

#### Transactional Intent (~10% of queries)
User wants to perform an action (buy, download, sign up, etc.).

```
Examples:
- "buy iphone 14 pro"
- "download chrome"
- "book flight to paris"
- "reserve table restaurant"
- "purchase domain name"

Signals:
- Action verbs (buy, purchase, download, book, reserve)
- Product/service names
- Price indicators
- "Best deals", "cheapest", "near me"
```

### 5.2 Classification Approaches

#### Rule-Based Classification

```python
def classify_intent_rules(query):
    """
    Simple rule-based intent classification
    """
    query_lower = query.lower()

    # Navigational signals
    nav_signals = ['login', 'sign up', 'download', 'facebook', 'gmail', 'amazon']
    if any(signal in query_lower for signal in nav_signals):
        return 'navigational'

    # Transactional signals
    trans_signals = ['buy', 'purchase', 'book', 'reserve', 'rent', 'order']
    if any(signal in query_lower for signal in trans_signals):
        return 'transactional'

    # Informational signals
    info_signals = ['how', 'what', 'why', 'when', 'where', 'tutorial', 'guide']
    if any(signal in query_lower for signal in info_signals):
        return 'informational'

    # Default: informational (most common)
    return 'informational'
```

#### ML-Based Classification with BERT

```python
from transformers import BertForSequenceClassification, BertTokenizer
import torch

# Training data
training_data = [
    ("facebook", "navigational"),
    ("how to bake bread", "informational"),
    ("buy laptop", "transactional"),
    # ... more examples
]

# Load pretrained BERT
model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=3  # navigational, informational, transactional
)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Training loop (simplified)
optimizer = torch.optim.Adam(model.parameters(), lr=2e-5)

for query, intent in training_data:
    # Tokenize
    inputs = tokenizer(
        query,
        padding=True,
        truncation=True,
        return_tensors='pt'
    )

    # Forward pass
    outputs = model(**inputs)
    logits = outputs.logits

    # Calculate loss and backprop
    loss = compute_loss(logits, intent_label)
    loss.backward()
    optimizer.step()

# Inference
def predict_intent(query):
    inputs = tokenizer(query, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    intent_id = torch.argmax(logits, dim=1).item()
    return id_to_intent_label[intent_id]
```

#### fastText for Fast Classification

```python
import fasttext

# Train on labeled data in format: __label__navigational facebook
fasttext_model = fasttext.train_supervised(
    input='queries_labeled.txt',
    epoch=25,
    lr=1.0,
    wordNgrams=2,
    dim=100,
    loss='softmax'
)

# Prediction
pred = fasttext_model.predict('buy iphone')
# Output: ('__label__transactional',), (0.95,)

intent = pred[0][0].replace('__label__', '')
confidence = pred[1][0]
```

### 5.3 Multi-Intent Queries

Some queries have multiple intents:

```python
def classify_multi_intent(query):
    """
    A query like "best restaurants near me to book" is:
    - Informational (best restaurants)
    - Locational (near me)
    - Transactional (to book)
    """
    intents = []
    confidences = []

    # Use multi-label classification instead of single-label
    model = BertForMultiLabelClassification(...)

    outputs = model(tokenized_query)
    logits = outputs.logits

    # Apply sigmoid + threshold
    probs = torch.sigmoid(logits)[0]

    for i, prob in enumerate(probs):
        if prob > 0.5:  # Threshold
            intents.append(intent_labels[i])
            confidences.append(float(prob))

    return intents, confidences
```

---

## 6. Named Entity Recognition (NER) for Search

Extracting and linking entities dramatically improves search understanding.

### 6.1 spaCy for NER

```python
import spacy

# Load pretrained model
nlp = spacy.load("en_core_web_sm")

def extract_entities(query):
    doc = nlp(query)
    entities = []

    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'label': ent.label_,  # PERSON, ORG, GPE, PRODUCT, etc.
            'start': ent.start_char,
            'end': ent.end_char
        })

    return entities

# Example:
query = "Show me Italian restaurants in San Francisco run by famous chefs"
entities = extract_entities(query)
# [
#   {'text': 'Italian', 'label': 'NORP', 'start': 8, 'end': 15},
#   {'text': 'San Francisco', 'label': 'GPE', 'start': 35, 'end': 48}
# ]
```

Common spaCy entity types for search:
- **PERSON**: People (celebrities, chefs, authors)
- **ORG**: Organizations (companies, brands)
- **GPE**: Geopolitical entities (countries, cities)
- **PRODUCT**: Products (phones, cars, software)
- **DATE**: Dates and times
- **QUANTITY**: Measurements, weights, distances

### 6.2 Entity Linking to Knowledge Base

```python
def link_entities_to_kb(entities, kb):
    """
    Link textual mentions to canonical entities in knowledge base
    """
    linked = []

    for entity in entities:
        # Find best match in KB
        candidates = kb.search(entity['text'], entity['label'])

        if candidates:
            best_match = candidates[0]  # Already ranked by relevance
            linked.append({
                'mention': entity['text'],
                'kb_id': best_match['id'],
                'canonical_name': best_match['name'],
                'description': best_match['description'],
                'confidence': best_match['score']
            })

    return linked

# Example KB structure:
kb = {
    'gpe': {
        'new york': {'id': 'gpe_us_ny', 'name': 'New York', ...},
        'new york city': {'id': 'gpe_us_nyc', 'name': 'New York City', ...},
        'california': {'id': 'gpe_us_ca', 'name': 'California', ...},
    },
    'org': {
        'apple': {'id': 'org_apple', 'name': 'Apple Inc.', ...},
        'google': {'id': 'org_google', 'name': 'Google LLC', ...},
    },
}
```

### 6.3 Custom NER for Domain-Specific Entities

```python
from spacy.training import Example
import spacy
from spacy.util import minibatch, compounding

def train_custom_ner(training_data, n_iterations=30):
    """
    Train custom NER for domain-specific entities
    training_data format:
    [
        (text, {"entities": [(start, end, label), ...]}),
        ...
    ]
    """
    nlp = spacy.blank("en")
    ner = nlp.add_pipe("ner")

    for _, annotations in training_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Training
    optimizer = nlp.create_optimizer()

    for itn in range(n_iterations):
        random.shuffle(training_data)
        losses = {}

        for batch in minibatch(training_data, size=8):
            examples = []
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                examples.append(example)

            nlp.update(
                examples,
                drop=0.35,
                sgd=optimizer,
                losses=losses,
            )

    return nlp
```

---

## 7. Query Segmentation: Breaking into Phrases

Query segmentation identifies meaningful phrase boundaries within a query.

Example: "new york pizza delivery" → ["new york", "pizza", "delivery"]

### 7.1 Statistical Approaches

#### PMI-Based Segmentation

Pointwise Mutual Information measures how much two words co-occur:

```python
from math import log

def calculate_pmi(word1, word2, corpus):
    """
    PMI(word1, word2) = log(P(word1, word2) / (P(word1) * P(word2)))
    High PMI = words appear together more than chance
    """
    p_word1_word2 = corpus.count(word1 + ' ' + word2) / corpus.total_bigrams
    p_word1 = corpus.count(word1) / corpus.total_words
    p_word2 = corpus.count(word2) / corpus.total_words

    pmi = log(p_word1_word2 / (p_word1 * p_word2))
    return pmi

def segment_query_pmi(query, corpus, threshold=2.0):
    """
    Segment by grouping words with high PMI
    """
    tokens = query.split()

    if len(tokens) < 2:
        return tokens

    segments = []
    current = [tokens[0]]

    for i in range(1, len(tokens)):
        pmi = calculate_pmi(tokens[i-1], tokens[i], corpus)

        if pmi > threshold:
            # Keep together
            current.append(tokens[i])
        else:
            # Start new segment
            segments.append(' '.join(current))
            current = [tokens[i]]

    segments.append(' '.join(current))
    return segments

# "new york pizza delivery"
# PMI(new, york) = 4.2 (high, keep together)
# PMI(york, pizza) = 0.8 (low, segment)
# PMI(pizza, delivery) = 2.5 (high, keep together)
# Result: ["new york", "pizza delivery"]
```

### 7.2 Neural Approaches

Use sequence models to predict boundaries:

```python
import tensorflow as tf
from tensorflow import keras

def create_segmentation_model(vocab_size=10000, embedding_dim=128):
    """
    Neural segmentation: Predict if each word is start of new segment
    """
    model = keras.Sequential([
        keras.layers.Embedding(vocab_size, embedding_dim),
        keras.layers.Bidirectional(
            keras.layers.LSTM(64, return_sequences=True)
        ),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(2, activation='softmax')  # [no_segment_start, segment_start]
    ])

    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    return model

# Training labels: [0, 0, 1, 0, 1, 0, ...]
# 0 = word continues previous segment
# 1 = word starts new segment

# Usage:
model = create_segmentation_model()
# Train on query segmentation data...
predictions = model.predict(tokenized_query)
# Apply threshold to get segments
```

---

## 8. Conversational Search & Context

Modern search is increasingly conversational, requiring context from previous turns.

### 8.1 Coreference Resolution

Resolving pronouns and references to previous entities:

```python
def resolve_coreference(current_query, conversation_history):
    """
    Turn: "Show me Italian restaurants"
    Turn: "Can I find one near the waterfront?" (one = restaurant)
    Turn: "Which of these are open late?" (these = the restaurants from turn 1)
    """
    nlp = spacy.load("en_core_web_trf")  # Transformer-based for better coref

    # Combine conversation
    full_context = ' [TURN] '.join([
        turn['query'] for turn in conversation_history
    ] + [current_query])

    doc = nlp(full_context)

    resolved = {}
    for token in doc:
        if token._.coref_clusters:
            cluster = token._.coref_clusters[0]
            resolved[token.text] = cluster.main.text

    return resolved
```

### 8.2 Query Reformulation in Context

Expand implicit references using context:

```python
def expand_implicit_query(current_query, context):
    """
    Make implicit context explicit
    Turn 1: "Italian restaurants in NYC"
    Turn 2: "Which are open late?" → "Which Italian restaurants in NYC are open late?"
    """
    # Identify what context should be carried forward
    carried_context = {}

    # Entity types that carry across turns
    for entity_type in ['GPE', 'CUISINE', 'RESTAURANT_TYPE']:
        for entity in context['entities']:
            if entity['label'] == entity_type:
                carried_context[entity_type] = entity['text']

    # Expand current query with relevant context
    expanded = current_query

    for entity_type, value in carried_context.items():
        if value not in expanded:
            expanded += f" {value}"

    return expanded
```

### 8.3 Session Context Carrying

Maintain state across the conversation:

```python
class ConversationSession:
    def __init__(self):
        self.history = []
        self.current_context = {
            'location': None,
            'cuisine': None,
            'price_range': None,
            'entities': [],
        }

    def process_turn(self, user_query):
        # Extract entities and intent from current query
        entities = extract_entities(user_query)
        intent = classify_intent(user_query)

        # Update context based on new information
        for entity in entities:
            if entity['label'] == 'GPE':
                self.current_context['location'] = entity['text']
            elif entity['label'] == 'CUISINE':
                self.current_context['cuisine'] = entity['text']

        # Store turn
        self.history.append({
            'query': user_query,
            'entities': entities,
            'intent': intent,
            'timestamp': datetime.now()
        })

        # Expand query with context
        expanded_query = self.expand_with_context(user_query)

        return expanded_query

    def expand_with_context(self, query):
        # Inject context into query
        if self.current_context['location'] and self.current_context['location'] not in query:
            query += f" in {self.current_context['location']}"

        return query
```

---

## 9. Query Classification & Routing

Beyond intent, classify queries for routing to appropriate backends.

### 9.1 Content Type Classification

```python
def classify_content_type(query):
    """
    Route to appropriate search backend
    """
    content_signals = {
        'image': ['picture', 'photo', 'image', 'wallpaper', 'icon'],
        'video': ['video', 'youtube', 'tutorial video', 'how to video'],
        'product': ['buy', 'price', 'product', 'amazon', 'ebay', 'shop'],
        'news': ['news', 'today', 'breaking', 'report', 'headline'],
        'academic': ['research', 'paper', 'study', 'scholar', 'pdf'],
        'code': ['github', 'code', 'programming', 'algorithm', 'implementation'],
    }

    query_lower = query.lower()
    scores = {}

    for content_type, signals in content_signals.items():
        score = sum(1 for signal in signals if signal in query_lower)
        if score > 0:
            scores[content_type] = score

    if scores:
        return max(scores, key=scores.get)

    return 'general'
```

### 9.2 Language Detection

```python
from langdetect import detect_langs

def detect_query_language(query):
    """
    Detect language and route to appropriate index
    """
    try:
        languages = detect_langs(query)
        # Returns list of (Language, probability) tuples
        primary_lang = languages[0]
        return primary_lang.lang, primary_lang.prob
    except:
        return 'en', 0.5  # Default to English
```

### 9.3 Safety & Sensitivity Classification

```python
def classify_safety(query):
    """
    Identify sensitive queries requiring special handling
    """
    safety_indicators = {
        'health_sensitive': ['disease', 'symptom', 'treatment', 'medical'],
        'financial_sensitive': ['password', 'credit card', 'ssn', 'bank account'],
        'legal_sensitive': ['copyright', 'piracy', 'illegal', 'dmca'],
        'nsfw': ['explicit', 'adult', 'pornography'],  # Plus trained models
    }

    query_lower = query.lower()
    flags = []

    for category, indicators in safety_indicators.items():
        if any(indicator in query_lower for indicator in indicators):
            flags.append(category)

    return flags
```

---

## 10. Query Analytics & Mining

Understanding patterns in query logs drives product improvements.

### 10.1 Query Log Analysis

```python
import pandas as pd
from collections import Counter
import numpy as np

def analyze_query_logs(log_file):
    """
    Load and analyze query patterns
    """
    df = pd.read_csv(log_file)
    # Columns: timestamp, query, results_count, ctr, dwell_time, user_id, session_id

    # Basic statistics
    stats = {
        'total_queries': len(df),
        'unique_queries': df['query'].nunique(),
        'avg_query_length': df['query'].str.split().apply(len).mean(),
        'zero_result_queries': (df['results_count'] == 0).sum(),
        'avg_ctr': df['ctr'].mean(),
        'avg_dwell_time': df['dwell_time'].mean(),
    }

    # Query distribution (head vs torso vs tail)
    query_freq = df['query'].value_counts()
    total = len(df)

    head = query_freq[query_freq >= total * 0.0001].sum()  # Top 0.01%
    tail = query_freq[query_freq == 1].sum()  # Never repeated
    torso = total - head - tail

    stats['distribution'] = {
        'head': f"{head / total * 100:.1f}%",
        'torso': f"{torso / total * 100:.1f}%",
        'tail': f"{tail / total * 100:.1f}%",
    }

    return stats

# Typical distribution:
# Head (frequently repeated): ~20%
# Torso (moderately common): ~30%
# Tail (unique or rare): ~50%
```

### 10.2 Zero-Result Query Mining

Queries returning zero results are valuable signals for improvement:

```python
def find_zero_result_queries(log_file):
    """
    Find queries with no results - signals for expansion/improvement
    """
    df = pd.read_csv(log_file)
    zero_result = df[df['results_count'] == 0].copy()

    # Group similar queries
    zero_result['query_stem'] = zero_result['query'].apply(
        lambda q: ' '.join(stem(word) for word in q.split())
    )

    # Count by stem
    stem_counts = zero_result['query_stem'].value_counts()

    # Find high-frequency zero-result patterns
    high_freq_zero = stem_counts[stem_counts > 5]

    # These are good candidates for:
    # - Query expansion rules
    # - New content/products
    # - Spelling correction
    # - Intent misclassification fixes

    return high_freq_zero
```

### 10.3 Trending Query Detection

```python
def detect_trending_queries(log_file, window_days=7):
    """
    Identify emerging trends in queries
    """
    df = pd.read_csv(log_file)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date

    # Get previous period
    today = df['date'].max()
    prev_week_start = today - timedelta(days=window_days)
    current_week_start = today - timedelta(days=window_days // 2)

    prev_queries = df[df['date'] < current_week_start]['query'].value_counts()
    curr_queries = df[df['date'] >= current_week_start]['query'].value_counts()

    # Calculate growth rate
    trending = []

    for query in curr_queries.index:
        prev_count = prev_queries.get(query, 1)  # Avoid division by zero
        curr_count = curr_queries[query]
        growth = (curr_count - prev_count) / prev_count

        if growth > 2.0:  # >200% growth
            trending.append({
                'query': query,
                'prev_count': prev_count,
                'curr_count': curr_count,
                'growth': growth,
            })

    return sorted(trending, key=lambda x: x['growth'], reverse=True)
```

### 10.4 Query Clustering for Pattern Discovery

```python
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

def cluster_queries(queries, n_clusters=50):
    """
    Cluster similar queries to find patterns
    """
    # Convert to TF-IDF vectors
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    X = vectorizer.fit_transform(queries)

    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    # Analyze clusters
    clusters = {}
    for query, label in zip(queries, labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(query)

    # Find cluster representatives
    for cluster_id, queries_in_cluster in clusters.items():
        if len(queries_in_cluster) > 3:  # Only show clusters with 3+ queries
            print(f"Cluster {cluster_id} ({len(queries_in_cluster)} queries):")
            # Print first 5 examples
            for query in queries_in_cluster[:5]:
                print(f"  - {query}")

    return clusters
```

---

## 11. Implementation Decision Framework

### 11.1 Choosing Your Approach

**For Small/Startup Systems:**
1. Start with rule-based preprocessing + simple spell correction
2. Add manual synonym dictionary for top 1000 queries
3. Use fastText for basic intent classification
4. Add spaCy NER for entity extraction
5. Evolve gradually based on query logs

**For Medium Systems:**
1. Full preprocessing pipeline (tokenization, normalization, spell correction)
2. Query expansion with word embeddings
3. BERT-based intent classification
4. Entity linking to knowledge base
5. Query segmentation with PMI
6. Session management for context

**For Large/Enterprise Systems:**
1. All of the above +
2. Custom fine-tuned models on domain data
3. Deep learning for all components
4. Real-time query understanding
5. A/B testing framework for improvements
6. Query reformulation with LLMs
7. Advanced conversational features

### 11.2 Performance Considerations

**Latency Budget:**
- Query understanding should complete in <50ms to avoid user-perceived delays
- Spell correction: <5ms (SymSpell)
- Tokenization & preprocessing: <10ms
- Intent classification: <20ms (fastText) to <50ms (BERT)
- Entity extraction: <15ms (spaCy)
- Context processing: <20ms

**Memory Usage:**
- BERT model: ~400MB
- spaCy models: ~50MB
- Word embeddings (1M words): ~400-800MB
- Knowledge base: varies

**Trade-offs:**
- fastText vs BERT: 10x faster, slightly less accurate
- Rule-based vs ML: Rules are faster, ML is more flexible
- Real-time vs batch: Batch processing can be 100x more efficient

### 11.3 Measuring Quality

```python
def evaluate_query_understanding(system, test_queries):
    """
    Evaluate quality of query understanding
    """
    metrics = {
        'spell_correction_accuracy': 0,
        'intent_classification_accuracy': 0,
        'entity_extraction_f1': 0,
        'segmentation_accuracy': 0,
    }

    for test_query, expected in test_queries:
        # Process
        result = system.process_query(test_query)

        # Compare to expected
        if result['corrected'] == expected['corrected']:
            metrics['spell_correction_accuracy'] += 1

        if result['intent'] == expected['intent']:
            metrics['intent_classification_accuracy'] += 1

        # F1 for entity extraction
        extracted = set(result['entities'])
        expected_set = set(expected['entities'])
        precision = len(extracted & expected_set) / len(extracted) if extracted else 1.0
        recall = len(extracted & expected_set) / len(expected_set) if expected_set else 1.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        metrics['entity_extraction_f1'] += f1

    # Normalize
    n = len(test_queries)
    for key in metrics:
        metrics[key] /= n

    return metrics
```

---

## 12. Key Takeaways & Best Practices

1. **Query understanding is foundational** - It's more impactful than ranking improvements alone

2. **Use a pipeline, not a single model** - Each component (preprocessing, expansion, intent, etc.) plays a role

3. **Start with rules, evolve to ML** - Rules are interpretable and fast for MVP; ML improves quality at scale

4. **Leverage existing tools** - spaCy, BERT, fastText, SymSpell have years of optimization

5. **Learn from query logs** - Mine zero-result queries, trending terms, and patterns

6. **Context matters** - Especially in conversational search, carrying context across turns improves quality

7. **Safety is critical** - Implement query safety filtering early

8. **Measure everything** - A/B test improvements and track quality metrics

9. **Domain matters** - Generic models need fine-tuning for domain-specific queries

10. **Performance + quality tradeoff** - Choose models based on your latency budget

---

## References

- [Intent Classification in NLP (Label Your Data)](https://labelyourdata.com/articles/machine-learning/intent-classification)
- [How To Implement Intent Classification In NLP (Spot Intelligence)](https://spotintelligence.com/2023/11/03/intent-classification-nlp/)
- [Intent Recognition Pipeline (Springer)](https://link.springer.com/article/10.1007/s41870-023-01642-8)
- [Building Intent Classification Pipeline (Langfuse)](https://langfuse.com/guides/cookbook/example_intent_classification_pipeline)
- [Text Preprocessing in NLP (GeeksforGeeks)](https://www.geeksforgeeks.org/nlp/text-preprocessing-for-nlp-tasks/)
- [Complete Guide to NLP Text Preprocessing (DEV Community)](https://dev.to/themustaphatijani/the-complete-guide-to-nlp-text-preprocessing-tokenization-normalization-stemming-lemmatization-50ap)
- [Query Expansion via WordNet](https://risame.github.io/sun/query.pdf)
- [WordNet-based Query Expansion for Geographical IR (ResearchGate)](https://www.researchgate.net/publication/228574617_A_wordnet-based_query_expansion_method_for_geographical_information_retrieval)
- [Query Expansion Using Word Embeddings](https://www.researchgate.net/publication/366647747_Query_Expansion_for_Information_Retrieval_using_Word_Embeddings_A_Comparative_Study)
- [Query Rewriting with LLMs (Elasticsearch Labs)](https://www.elastic.co/search-labs/blog/query-rewriting-llm-search-improve)
- [Query Rewriting in RAG (Shekhar Gulati)](https://shekhargulati.com/2024/07/17/query-rewriting-in-rag-applications/)
- [Determining Informational/Navigational/Transactional Intent (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S030645730700163X)
- [Broders Classification of Keywords (Medium)](https://medium.com/@seokai/broders-classification-of-keywords-16ddb1015a3)
- [spaCy EntityLinker API](https://spacy.io/api/entitylinker)
- [NER and Entity Linking with spaCy (Medium)](https://kristinelpetrosyan.medium.com/ner-and-ned-with-spacy-dd847800b7d9)
- [Pointwise Mutual Information (PMI) in NLP (Listen Data)](https://www.listendata.com/2022/06/pointwise-mutual-information-pmi.html)
- [Conversational Search with Coreference (ArXiv)](https://arxiv.org/html/2508.12630)
- [Coreference Resolution in NLP (Spot Intelligence)](https://spotintelligence.com/2024/01/17/coreference-resolution-nlp/)
- [SymSpell vs BK-Tree (Medium)](https://medium.com/data-science/symspell-vs-bk-tree-100x-faster-fuzzy-string-search-spell-checking-c4f10d80a078)
- [SymSpell GitHub](https://github.com/wolfgarbe/SymSpell)
- [Pseudo Relevance Feedback (ArXiv)](https://arxiv.org/html/2503.14887v1)
- [BERT Intent Classification (KDnuggets)](https://www.kdnuggets.com/2020/02/intent-recognition-bert-keras-tensorflow.html)
- [fastText Text Classification (Medium)](https://medium.com/analytics-vidhya/text-classification-from-bag-of-words-to-bert-part-3-fasttext-8313e7a14fce)
- [Stemming vs Lemmatization (Analytics Vidhya)](https://www.analyticsvidhya.com/blog/2022/06/stemming-vs-lemmatization-in-nlp-must-know-differences/)
- [Mining Query Logs (Microsoft Research)](https://www.microsoft.com/en-us/research/wp-content/uploads/2012/01/fp266-hu.pdf)
- [Query Log Analysis Literature Review](https://arxiv.org/html/2508.13949v1)
