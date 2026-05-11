# Search Architecture Reference

This reference provides the complete specification for building working, Amazon-level search into generated documentation sites. The search system uses a 3-layer architecture: keyword search (instant), fuzzy + ranked search (fast), and optional semantic search (smart).

## Why Search Was Broken in v1/v2

The previous skill had 3 critical failures:

1. **Pagefind only indexes at BUILD TIME** — Running `astro dev` shows no search. The skill never instructed Claude to run `astro build` followed by `npx pagefind --site dist/`.
2. **Missing `data-pagefind-body`** — Once ANY page has `data-pagefind-body`, pages WITHOUT it become INVISIBLE to search. Starlight adds it automatically, but custom layouts may not.
3. **No autocomplete, no fuzzy matching, no code-aware tokenization** — Pagefind's default search is keyword-only. It can't find `getUserProfile` when you search for "get user".

## The 3-Layer Search Architecture

```
USER TYPES QUERY
       |
       v
[Layer 1: Pagefind] ---------> Results in <10ms (keyword match)
       |                        Show immediately to user
       v
[Layer 2: BM25F + Fuzzy] ----> Refined results in <50ms
       |                        Code-aware tokenization
       |                        Fuzzy typo correction
       |                        Field-weighted ranking
       |                        Confidence boosting
       v
[Layer 3: Semantic] ----------> Smart results in <300ms (optional)
                                Pre-computed embeddings
                                Intent understanding
                                "how does auth work?" finds auth module
```

## Layer 1: Pagefind (Keyword Search)

### Making Pagefind Actually Work

CRITICAL: Follow this exact sequence when generating an interactive documentation site:

```bash
# Step 1: Build the static site
npm run build  # or: npx astro build

# Step 2: Run Pagefind indexing on the built output
npx pagefind --site dist/

# Step 3: Verify the index exists
ls dist/pagefind/
# Should contain: pagefind.js, pagefind-ui.js, pagefind-ui.css, fragment files
```

### Pagefind Configuration

Create `pagefind.json` in the project root:

```json
{
  "site": "dist",
  "output_subdir": "pagefind",
  "glob": "**/*.html",
  "include_characters": "<>()[]{}",
  "root_selector": "[data-pagefind-body]",
  "exclude_selectors": ["nav", "footer", "[data-pagefind-ignore]"]
}
```

### Ensuring All Pages Are Indexed

In Starlight config (astro.config.mjs):
```javascript
export default defineConfig({
  integrations: [
    starlight({
      title: 'Project Docs',
      pagefind: true,  // Enable built-in Pagefind
    }),
  ],
});
```

For custom layouts, ALWAYS include `data-pagefind-body`:
```html
<main data-pagefind-body>
  <article>
    <h1>{title}</h1>
    <slot />
  </article>
</main>
```

### Pagefind Custom Records (for Code Symbols)

Use the Pagefind Node API to index code symbols alongside prose:

```javascript
import * as pagefind from "pagefind";

const { index } = await pagefind.createIndex();

// Index all HTML files from the build
await index.addDirectory({ path: "dist" });

// Add custom records for code symbols
await index.addCustomRecord({
  url: "/api/auth-service/",
  content: "AuthService class handles OAuth2 authentication flows including token refresh and session management",
  language: "en",
  meta: {
    title: "AuthService",
    type: "class",
    module: "auth",
    confidence: "VERIFIED"
  },
  filters: {
    doc_type: ["reference"],
    module: ["auth"],
    confidence: ["VERIFIED"]
  },
  sort: {
    weight: "100"
  }
});

await index.writeFiles({ outputPath: "dist/pagefind" });
```

### Pagefind Ranking Tuning

```javascript
const pagefind = await import("/pagefind/pagefind.js");
await pagefind.options({
  ranking: {
    termFrequency: 0.8,
    termSaturation: 1.5,
    termSimilarity: 1.5,
    pageLength: 1.0
  }
});
await pagefind.init();
```

### Pagefind Weighting in HTML

Add weight attributes to HTML elements to control ranking:

```html
<!-- Title gets highest weight -->
<h1 data-pagefind-weight="10.0">Authentication Module</h1>

<!-- Headings get medium weight -->
<h2 data-pagefind-weight="5.0">validateToken()</h2>

<!-- Code blocks get elevated weight -->
<pre data-pagefind-weight="3.0"><code>
function validateToken(token) { ... }
</code></pre>

<!-- Body text gets default weight (1.0) -->
<p>This function validates JWT tokens against the issuer.</p>
```

### Pagefind Metadata for Rich Results

```html
<div data-pagefind-meta="title">Authentication Module</div>
<div data-pagefind-meta="module">auth</div>
<div data-pagefind-meta="doc_type">reference</div>
<div data-pagefind-meta="confidence">VERIFIED</div>
```

### Pagefind Filters for Faceted Search

```html
<div data-pagefind-filter="module">auth</div>
<div data-pagefind-filter="doc_type">reference</div>
<div data-pagefind-filter="confidence">VERIFIED</div>
```

## Layer 2: BM25F + Fuzzy Search (Custom Engine)

### Search-Optimized Frontmatter

EVERY generated documentation page MUST include this frontmatter schema:

```yaml
---
title: "Authentication Module"
description: "OAuth2 flow with JWT tokens and session management"
module: "auth"
doc_type: "reference"           # tutorial | howto | reference | explanation
confidence: "VERIFIED"          # VERIFIED | HIGH | MEDIUM | LOW | UNKNOWN
audience: ["maintainer", "new-dev"]
keywords: ["oauth", "jwt", "authentication", "middleware", "token"]
code_symbols: ["AuthService", "validateToken", "refreshToken", "TokenPayload"]
last_verified: "2026-02-08"
search_weight: 1.5              # boost multiplier for critical docs
---
```

### Code-Aware Tokenization

The code tokenizer handles ALL naming conventions developers use:

| Pattern | Input | Tokens |
|---------|-------|--------|
| camelCase | `getUserProfile` | get, user, profile, getuserprofile |
| snake_case | `get_user_profile` | get, user, profile |
| PascalCase | `AuthService` | auth, service, authservice |
| kebab-case | `my-component` | my, component |
| dot.notation | `user.auth.getToken` | user, auth, get, token |
| SCREAMING_SNAKE | `MAX_RETRY_COUNT` | max, retry, count |
| Acronyms | `OAuth2Client` | oauth, 2, client |
| Import paths | `@/components/ui` | components, ui |
| File paths | `src/auth/middleware.ts` | src, auth, middleware |

This means searching "get user" finds `getUserProfile`, `get_user_profile`, and `getUser`.

### BM25F Field Weighting

The search engine uses BM25F (field-weighted BM25) with these weights:

| Field | Weight | Rationale |
|-------|--------|-----------|
| title | 10 | Exact title matches are highest priority |
| code_symbols | 8 | Function/class name matches are very important |
| headings | 5 | Section headings indicate topic relevance |
| keywords | 4 | Curated keywords are strong signals |
| description | 3 | Brief summaries carry moderate weight |
| module | 2 | Module-level matching is useful for filtering |
| body | 1 | Full-text body is baseline |

### Confidence Boosting

Results are boosted based on the documentation's confidence level:

| Confidence | Boost Factor | Effect |
|-----------|-------------|--------|
| VERIFIED | 1.0 | Full relevance score |
| HIGH | 0.8 | Slightly reduced |
| MEDIUM | 0.5 | Half weight |
| LOW | 0.2 | Significantly reduced |
| UNKNOWN | 0.1 | Near-bottom of results |

### Ranking Formula

```
finalScore =
  0.50 * BM25F(query, doc, FIELD_WEIGHTS) +
  0.20 * confidenceBoost(doc.confidence) +
  0.15 * fuzzyBonus(query, doc.title) +
  0.10 * freshnessScore(doc.last_verified) +
  0.05 * searchWeightBoost(doc.search_weight)
```

### Fuzzy Matching for Typo Tolerance

The search engine uses the Bitap algorithm (same as Fuse.js) with:
- Threshold: 0.3 (catches 1-2 character typos without false positives)
- "froq" matches "frog", "authetication" matches "authentication"
- Results show "Did you mean: authentication?" when fuzzy match differs from query

## Layer 3: Semantic Search (Optional)

### Pre-computed Embeddings

At build time, generate embeddings for all documentation pages:

```javascript
// Build-time: Generate embeddings (requires API call or local model)
const embeddings = {};
for (const doc of documents) {
  const text = `${doc.title} ${doc.description} ${doc.body.slice(0, 500)}`;
  embeddings[doc.id] = await embedModel.encode(text);
  // Quantize to INT8 for storage: 384 bytes per document
}
fs.writeFileSync('dist/embeddings.bin', serializeEmbeddings(embeddings));
```

Storage requirements (INT8, 384 dimensions):
- 1,000 documents: ~384 KB
- 5,000 documents: ~1.9 MB
- 10,000 documents: ~3.8 MB

### Hybrid Search with RRF

Combine keyword and semantic results using Reciprocal Rank Fusion:

```javascript
function hybridSearch(query, bm25Results, semanticResults) {
  const k = 60;  // Standard RRF constant
  const scores = new Map();

  bm25Results.forEach((doc, rank) => {
    scores.set(doc.id, (scores.get(doc.id) || 0) + 1/(k + rank));
  });
  semanticResults.forEach((doc, rank) => {
    scores.set(doc.id, (scores.get(doc.id) || 0) + 1/(k + rank));
  });

  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([id, score]) => ({ id, score }));
}
```

### Query Expansion (Simpler Alternative to Embeddings)

If semantic search is too heavy, use pre-built concept maps:

```javascript
const conceptMap = {
  "auth": ["authentication", "authn", "login", "signin", "oauth", "jwt", "session"],
  "error": ["exception", "err", "bug", "failure", "crash", "throw", "catch"],
  "api": ["endpoint", "route", "handler", "request", "response", "REST", "GraphQL"],
  "db": ["database", "query", "schema", "migration", "model", "ORM", "SQL"],
  "test": ["testing", "spec", "assertion", "mock", "stub", "fixture", "jest", "vitest"],
  "config": ["configuration", "settings", "env", "environment", "dotenv", "options"]
};
```

## Search UI Requirements

### Autocomplete Dropdown (As-You-Type)

When the user types in the search box, show a dropdown with:

1. **Grouped by category**: "In Functions:", "In Modules:", "In Guides:"
2. **Each suggestion shows**:
   - Icon (based on type: function, class, module, guide)
   - Title text with matched characters highlighted
   - Module breadcrumb (e.g., auth > service > validateToken)
   - Confidence badge (color-coded)
3. **Keyboard navigation**: Up/Down arrows, Enter to select, Escape to close
4. **Debounced**: 200ms delay before searching (prevents excessive computation)

### Full Search Results (On Enter)

When the user presses Enter:

1. **Ranked results** with relevance score visualization
2. **Code-highlighted excerpts** showing where the match occurred
3. **Faceted filtering sidebar**: filter by module, confidence level, doc type
4. **Sort options**: Relevance (default), Newest first, Highest confidence
5. **Pagination**: 10 results per page

### Keyboard Shortcut

The search box should be focusable via Cmd/Ctrl+K (standard documentation shortcut).

## Build-Time Search Index Generation

### The Build Script

Run `node scripts/build_search_index.js` AFTER generating documentation Markdown:

```bash
# Generate documentation (Claude's output)
# ... Markdown files in docs/

# Build search indices
node scripts/build_search_index.js \
  --docs-dir ./docs \
  --output-dir ./dist/search \
  --format all

# Build the static site
npx astro build

# Run Pagefind on the built site
npx pagefind --site dist/
```

### Output Files

```
dist/search/
  search-index.json        # Documents for runtime search (~50-300KB)
  autocomplete-trie.json   # Prefix data for autosuggest (~10-50KB)
  facets.json             # Available filter options (~1-5KB)
  code-symbols.json       # Code symbol index (~10-100KB)
dist/pagefind/
  pagefind.js             # Pagefind search library
  pagefind-ui.js          # Default UI (optional)
  pagefind-ui.css         # Default styles (optional)
  fragment-*.pf_fragment  # Index chunk files
```

### Integrating Search UI into the Site

For Starlight/Astro sites, override the search component:

```astro
---
// src/components/Search.astro
import SearchComponent from '../search-ui/search-component.jsx';
---

<SearchComponent client:load />

<script>
  // Load search index lazily on first focus
  document.querySelector('[data-search-input]')?.addEventListener('focus', async () => {
    const [indexData, trieData] = await Promise.all([
      fetch('/search/search-index.json').then(r => r.json()),
      fetch('/search/autocomplete-trie.json').then(r => r.json())
    ]);
    // Initialize search engine with loaded data
    window.searchEngine = new CodeDocSearchEngine();
    window.searchEngine.loadIndex(indexData);
  }, { once: true });
</script>
```

## Verification Checklist

Before delivering documentation with search:

```
SEARCH FUNCTIONALITY
[ ] Run `astro build` — static site generated in dist/
[ ] Run `npx pagefind --site dist/` — Pagefind index created
[ ] dist/pagefind/ directory exists with pagefind.js and fragment files
[ ] Search box appears on the site
[ ] Typing in search box shows autocomplete suggestions
[ ] Pressing Enter shows full results
[ ] Exact title search returns the correct page as #1 result
[ ] Code symbol search works (e.g., "validateToken" finds the function)
[ ] Fuzzy search works (e.g., "authetication" suggests "authentication")
[ ] Faceted filtering works (filter by module, confidence, doc type)
[ ] Keyboard shortcut (Cmd/Ctrl+K) focuses search box
[ ] Mobile responsive — search works on small screens

SEARCH QUALITY
[ ] All documentation pages appear in search results
[ ] VERIFIED docs rank higher than LOW confidence docs
[ ] Title matches rank above body-text-only matches
[ ] Code symbols are searchable by partial name
[ ] No empty results for known content
[ ] "Did you mean?" appears for misspelled queries

PERFORMANCE
[ ] First search result appears in <100ms
[ ] Search doesn't block page scrolling or interaction
[ ] Search index loads lazily (not on page load)
[ ] Total search index size < 500KB (gzipped)
```

## Common Failure Modes and Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Search returns nothing | Pagefind not run after build | Run `npx pagefind --site dist/` |
| Search works locally but not deployed | `/pagefind/` not in deploy output | Check build command includes pagefind step |
| Some pages missing from search | Inconsistent `data-pagefind-body` | Ensure ALL pages have it, or NONE do |
| Code symbols not searchable | No custom records added | Use Pagefind Node API to add custom records |
| Typos return no results | Default Pagefind has no fuzzy matching | Add Layer 2 (BM25F + fuzzy) search engine |
| "How does X work?" returns nothing | Keyword-only search can't handle intent | Add Layer 3 (semantic) or query expansion |
| Search is slow (>500ms) | Index loaded on page load | Lazy load on first search focus |
| Search blocks typing | Search runs on main thread | Move to Web Worker |

## Technology Stack Summary

| Component | Technology | Bundle Size (gzipped) | Purpose |
|-----------|-----------|----------------------|---------|
| Layer 1 | Pagefind | ~50-70KB (loaded on demand) | Instant keyword search |
| Layer 2 | Custom BM25F engine | ~15KB | Code-aware ranked search |
| Layer 2 | Code tokenizer | ~3KB | camelCase/snake_case splitting |
| Layer 2 | Fuzzy matcher (Bitap) | ~5KB | Typo tolerance |
| Layer 3 | Pre-computed embeddings | ~100-400KB | Semantic understanding |
| Layer 3 | Transformers.js (optional) | ~14MB (lazy loaded) | Neural reranking |
| UI | React search component | ~8KB | Autocomplete + results |
| Worker | Web Worker | ~2KB | Non-blocking search |
| Build | build_search_index.js | N/A (build-time only) | Index generation |
