# Search Engine Configuration for LAP Intelligence Hub v2

## Library: Fuse.js v7.1.0

**CDN**: https://cdn.jsdelivr.net/npm/fuse.js@7.0.0

Fuse.js provides lightweight, client-side full-text search without requiring a server-side search service.

## Configuration

```javascript
const options = {
  keys: [
    { name: 'key', weight: 3.0 },
    { name: 'summary', weight: 2.0 },
    { name: 'description', weight: 1.0 },
    { name: 'assignee', weight: 0.5 }
  ],
  threshold: 0.3,
  distance: 100,
  useExtendedSearch: true,
  minMatchCharLength: 2
};

const fuse = new Fuse(searchIndex, options);
```

## Configuration Breakdown

### Keys (Weighted Fields)

The search index includes 4 searchable fields with field-specific weights:

| Field | Weight | Purpose | Example Match |
|-------|--------|---------|---|
| key | 3.0 | Exact ticket ID | "LAP-123" → finds LAP-123 |
| summary | 2.0 | Title text (highest relevance) | "payment fix" → matches summaries |
| description | 1.0 | Body text (lower relevance) | "integration" → finds in descriptions |
| assignee | 0.5 | Person name (lowest relevance) | "John" → finds tickets assigned to John |

**Weight Rationale**:
- Key matches are most relevant (exact ticket reference)
- Summary matches are more specific than description
- Description is broad but useful as secondary signal
- Assignee is useful for filtering but lower priority

### Threshold: 0.3

Fuzzy matching score (0.0 to 1.0). Lower = more permissive.

- 0.0 = match everything
- 0.3 = default; permits 30% character difference
- 0.6 = stricter; only very close matches
- 1.0 = exact match only

**Impact**:
- 0.3 catches typos: "paument" matches "payment"
- Reduces false negatives (missing relevant results)
- May increase false positives (irrelevant results)

### Distance: 100

Fuzzy matching distance tolerance (Levenshtein distance in characters). Used with threshold.

- 100 = allow up to 100 character difference
- 50 = stricter matching
- Lower values for shorter, more precise searches

**Impact**:
- 100 is permissive; good for varied ticket descriptions
- Helps match partial words and variations

### useExtendedSearch: true

Enables advanced query syntax for users.

### minMatchCharLength: 2

Minimum characters to trigger a search (prevents single-char searches like "a").

## Extended Search Syntax

When `useExtendedSearch: true`, users can use advanced operators:

### 1. Prefix Search: `^`
```
^payment     → matches "payment", "payments", "payment-method" (starts with)
^api         → matches "api", "api-docs" (starts with)
```

### 2. Exact Match: `=`
```
=payment     → matches only "payment" (exact string, not "payments")
="LAP-123"   → matches exact ticket key
```

### 3. Include: `'`
```
'bug 'fix    → both "bug" AND "fix" must be present
'payment 'gateway → matches only if both terms exist
```

### 4. Exclude: `!`
```
!bug         → excludes tickets containing "bug"
payment !resolved → includes "payment" but not "resolved"
```

### 5. Combined
```
^pay !refund       → starts with "pay" but exclude "refund"
'api '=rest        → includes "api" and exact match for "rest"
=KYC 'verification → exact "KYC" and includes "verification"
```

## Usage Examples

### Basic Search
```javascript
const results = fuse.search('payment');
```
Finds tickets with "payment" in key, summary, description, or assignee.

### With Extended Syntax
```javascript
const results = fuse.search('^LAP payment');
// Finds tickets with key starting with "LAP" AND containing "payment"

const results = fuse.search('=payment !bug');
// Finds exact "payment" string but excludes "bug"

const results = fuse.search("'api '=rest");
// Finds tickets with both "api" and exact "rest"
```

### Programmatic (No Extended Syntax)
```javascript
const results = fuse.search({
  $and: [
    { key: 'LAP' },
    { summary: 'payment' }
  ]
});
```

## Result Format

```javascript
[
  {
    item: {
      key: "LAP-45",
      summary: "Fix payment transaction timeout",
      description: "Payment requests are timing out after 30s...",
      type: "Bug",
      status: "In Progress",
      assignee: "Jane Smith",
      priority: "High"
    },
    refIndex: 44,
    score: 0.892
  },
  {
    item: {
      key: "LAP-67",
      summary: "Implement payment reconciliation",
      ...
    },
    refIndex: 66,
    score: 0.745
  }
]
```

**Fields**:
- `item`: Full ticket object from search_index
- `refIndex`: Index in original search_index array
- `score`: Relevance score (0.0 = perfect match, 1.0 = no match)

Typically sort by score ascending (lower score = better match).

## Performance Considerations

### For 2000+ Tickets

**Index Size**:
- 2000 tickets × ~500 bytes each = ~1MB
- Fits comfortably in browser memory

**Search Performance**:
- Single query: 10-50ms (depends on result count)
- Acceptable for real-time search-as-you-type

**Optimization Strategies**:

1. **Lazy Load Index**: Load search_index.json only when user opens search panel
2. **Web Worker**: Offload search to background thread (prevent UI blocking)
   ```javascript
   // main.js
   const worker = new Worker('search-worker.js');
   worker.postMessage({ query: 'payment' });
   worker.onmessage = (e) => displayResults(e.data);

   // search-worker.js
   let fuse;
   fetch('/search_index.json').then(r => r.json()).then(data => {
     fuse = new Fuse(data, options);
   });
   self.onmessage = (e) => {
     self.postMessage(fuse.search(e.data.query));
   };
   ```

3. **Debounce Input**: Wait 300ms after user stops typing before searching
   ```javascript
   let timeout;
   input.addEventListener('input', (e) => {
     clearTimeout(timeout);
     timeout = setTimeout(() => {
       const results = fuse.search(e.target.value);
       displayResults(results);
     }, 300);
   });
   ```

4. **Limit Results**: Display only top 20 results
   ```javascript
   const results = fuse.search(query).slice(0, 20);
   ```

5. **Cache Common Searches**: Store results for frequently searched terms
   ```javascript
   const cache = {};
   if (cache[query]) return cache[query];
   const results = fuse.search(query);
   cache[query] = results;
   ```

## Troubleshooting

### No Results Found
- Check `threshold` is not too high (increase to 0.6+)
- Verify query contains at least 2 characters (minMatchCharLength)
- Try extended syntax without special operators

### Too Many Results
- Decrease `threshold` (0.0 to 0.2)
- Use extended syntax to narrow: `'payment '!bug`
- Limit result count: `results.slice(0, 10)`

### Slow Search
- Check if search_index.json is loaded (test in console)
- Use Web Worker for background search (see above)
- Reduce result limit

### Unexpected Match
- Review `keys` weights; may prioritize wrong field
- Check `distance` parameter (may be too permissive)
- Use exact match syntax: `=exact_term`

## Future Enhancements

1. **Server-Side Search**: For projects > 5000 tickets, consider Elasticsearch or Meilisearch
2. **Autocomplete**: Combine Fuse.js with autocomplete library (e.g., Typeahead.js)
3. **Faceted Search**: Add filters by type, status, assignee alongside text search
4. **Search Analytics**: Track popular searches to guide theme improvements
