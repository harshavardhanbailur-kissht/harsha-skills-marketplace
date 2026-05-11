# Search Architecture Reference (v4)

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

## Search Overlay UI Fixes

This section documents the exact CSS/JS patterns from the LAP KB fix that resolved critical search dropdown positioning and accessibility issues.

### CSS Root Causes & Solutions

#### Stacking Context Issue

**Problem**: Search dropdown positioned behind page content due to parent stacking contexts.

**Solution**: Apply explicit stacking context to `.search-container`:

```css
.search-container {
  position: relative;
  z-index: 200;  /* High enough to escape typical page contexts */
}
```

The z-index value of 200 is chosen to:
- Exceed typical dropdown indices (~100)
- Stay below modal indices (usually 1000+)
- Allow for nested search overlays without conflicts

#### Overlay Positioning

**Problem**: Dropdown positioned directly below search input, limited to input width.

**Solution**: Use calculated positioning with negative offsets:

```css
.search-dropdown {
  position: absolute;
  top: calc(100% + 4px);  /* 4px gap between input and dropdown */
  left: -60px;             /* Extend left for wider display */
  right: -60px;            /* Extend right for wider display */
  max-height: 600px;
  overflow-y: auto;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.05);
}
```

The left/right negative offsets create a wider dropdown that:
- Extends beyond the input box for better readability
- Maintains proper alignment on mobile (override on <640px)
- Provides sufficient space for code symbol badges

#### Background Opacity

**Problem**: Using `rgba()` with transparency caused visual artifacts in dark mode.

**Solution**: Use CSS custom properties for semantic colors:

```css
.search-dropdown {
  background-color: var(--color-bg);  /* Opaque background, not transparent */
  border: 1px solid var(--color-border);
}
```

This approach:
- Respects light/dark mode automatically
- Avoids transparency blending issues
- Maintains proper contrast ratios

#### Card-Style Result Items

**Problem**: Results blended together with no visual separation.

**Solution**: Apply card styling to each result:

```css
.search-result-item {
  background: var(--color-bg-secondary);
  border: 1px solid transparent;
  border-radius: 8px;
  margin: 4px 8px;
  padding: 12px;
  transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
```

This provides:
- Clear visual separation between results
- Rounded corners for modern appearance
- Subtle margin for breathing room

#### Hover and Active States

**Problem**: No clear visual feedback on interaction.

**Solution**: Implement state-aware styling:

```css
.search-result-item:hover,
.search-result-item.keyboard-active {
  background: var(--color-bg-tertiary);
  border-color: var(--color-border);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.search-result-item:active {
  transform: scale(0.98);  /* Subtle press feedback */
}
```

The `keyboard-active` class is set by JavaScript (not `:focus-visible`) to distinguish keyboard navigation from mouse hover.

#### Box Shadow for Professional Depth

**Problem**: Dropdown appeared flat and unimportant.

**Solution**: Multi-layer shadow system:

```css
.search-dropdown {
  box-shadow:
    0 25px 50px -12px rgba(0,0,0,0.25),  /* Outer shadow for depth */
    0 0 0 1px rgba(0,0,0,0.05);          /* Border-like edge */
}

.search-result-item:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);  /* Item hover effect */
}
```

These shadows create elevation hierarchy:
- Dropdown appears to float above the page
- Individual items show subtle depth on interaction
- Adapts to both light and dark themes

#### Scrollbar Styling

**Problem**: Default browser scrollbar didn't match design.

**Solution**: Cross-browser scrollbar styling:

```css
.search-dropdown {
  scrollbar-width: thin;
  scrollbar-color: var(--color-border) transparent;
}

.search-dropdown::-webkit-scrollbar {
  width: 8px;
}

.search-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.search-dropdown::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

.search-dropdown::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}
```

Handles both:
- Firefox (scrollbar-width/scrollbar-color)
- Webkit browsers (custom scrollbar pseudo-elements)

#### Responsive Mobile Behavior

**Problem**: Desktop overlay too wide/tall for mobile screens.

**Solution**: Mobile-specific overrides:

```css
@media (max-width: 640px) {
  .search-dropdown {
    left: -60px;
    right: -60px;
    max-height: 50vh;  /* Limit to half viewport height */
    border-radius: 0 0 12px 12px;
  }

  .search-result-item {
    margin: 2px 4px;    /* Tighter spacing */
    padding: 10px;      /* Less padding */
    font-size: 0.875rem; /* Smaller font */
  }
}
```

Adjustments for mobile:
- Wider negative offsets utilize full screen width
- Limited max-height prevents scrolling entire page
- Reduced padding fits more content in limited space
- Maintains touch target size (min 44x44px)

#### Reduced Motion Support

**Problem**: Animations cause discomfort for users with motion sensitivity.

**Solution**: Respect user preference:

```css
@media (prefers-reduced-motion: reduce) {
  .search-result-item {
    transition: none;
  }

  .search-result-item:active {
    transform: none;  /* Disable scale feedback */
  }

  .search-result-item:hover {
    /* Keep color changes, remove transforms */
    box-shadow: none;
  }
}
```

Preserves:
- Color/border feedback on hover (still usable)
- Removes all motion-based feedback (animations, transforms)

### JavaScript Keyboard Navigation

Keyboard navigation is critical for accessibility and power users. Implement this in your search React component:

#### Keyboard State Management

```javascript
function SearchComponent() {
  const [kbIndex, setKbIndex] = useState(-1);  // -1 = no selection
  const [results, setResults] = useState([]);
  const inputRef = useRef(null);
  const resultsContainerRef = useRef(null);

  // Reset keyboard selection when results change
  useEffect(() => {
    setKbIndex(-1);
  }, [results]);

  return (
    <div className="search-container">
      <input ref={inputRef} className="search-input" />
      <div ref={resultsContainerRef} className="search-dropdown">
        {results.map((result, idx) => (
          <div
            key={result.id}
            className={`search-result-item ${
              idx === kbIndex ? 'keyboard-active' : ''
            }`}
            onClick={() => navigateToResult(result)}
          >
            {result.title}
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### Arrow Key Handling

```javascript
const handleKeyDown = (e) => {
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      setKbIndex(prev => {
        if (prev < results.length - 1) return prev + 1;
        return 0;  // Wrap to beginning
      });
      break;

    case 'ArrowUp':
      e.preventDefault();
      setKbIndex(prev => {
        if (prev > 0) return prev - 1;
        return results.length - 1;  // Wrap to end
      });
      break;

    case 'Enter':
      if (kbIndex >= 0 && results[kbIndex]) {
        e.preventDefault();
        navigateToResult(results[kbIndex]);
      }
      break;

    case 'Escape':
      e.preventDefault();
      setKbIndex(-1);
      setResults([]);
      break;

    default:
      break;
  }
};
```

Add listener to input element:
```javascript
<input
  ref={inputRef}
  className="search-input"
  onKeyDown={handleKeyDown}
  {...otherProps}
/>
```

#### Ctrl+K / Cmd+K Global Shortcut

```javascript
useEffect(() => {
  const handleGlobalKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      inputRef.current?.focus();
      // Optionally select all text
      inputRef.current?.select();
    }
  };

  window.addEventListener('keydown', handleGlobalKeyDown);
  return () => window.removeEventListener('keydown', handleGlobalKeyDown);
}, []);
```

#### ScrollIntoView for Keyboard Navigation

When keyboard index changes, scroll the active item into view:

```javascript
useEffect(() => {
  if (kbIndex >= 0 && resultsContainerRef.current) {
    const items = resultsContainerRef.current.querySelectorAll('.search-result-item');
    if (items[kbIndex]) {
      items[kbIndex].scrollIntoView({
        block: 'nearest',        // Scroll minimally
        behavior: 'smooth'       // Smooth animation
      });
    }
  }
}, [kbIndex]);
```

This ensures:
- Active item is always visible
- Minimal scrolling (doesn't jump to center)
- Smooth animation (not jarring)

#### Query Change Reset

Always reset keyboard selection when the query changes:

```javascript
const handleInputChange = (e) => {
  const query = e.target.value;
  setKbIndex(-1);  // CRITICAL: Reset selection

  // Debounce search
  clearTimeout(searchTimeoutRef.current);
  searchTimeoutRef.current = setTimeout(() => {
    performSearch(query);
  }, 200);
};
```

### ARIA Accessibility

Implement ARIA attributes for screen reader support:

#### Result Container (Listbox Role)

```jsx
<div
  className="search-dropdown"
  role="listbox"
  aria-label="Search results"
  aria-expanded={results.length > 0}
  aria-activedescendant={
    kbIndex >= 0 ? `result-${results[kbIndex].id}` : undefined
  }
>
  {/* Results */}
</div>
```

Properties explained:
- `role="listbox"`: Tells screen readers this is a list of options
- `aria-expanded`: Announces whether results are showing
- `aria-activedescendant`: Points to the keyboard-selected item

#### Result Items (Option Role)

```jsx
<div
  key={result.id}
  id={`result-${result.id}`}
  className="search-result-item"
  role="option"
  aria-selected={idx === kbIndex}
  onClick={() => navigateToResult(result)}
>
  <h3>{result.title}</h3>
  <p>{result.description}</p>
</div>
```

Properties explained:
- `role="option"`: Identifies as selectable option
- `aria-selected`: Announces whether this item is keyboard-selected
- `id`: Allows parent to reference via `aria-activedescendant`

#### Search Input (Combobox Role)

```jsx
<input
  role="combobox"
  aria-label="Search documentation"
  aria-autocomplete="list"
  aria-controls="search-results-listbox"
  aria-expanded={results.length > 0}
  placeholder="Search docs... (Ctrl+K)"
  ref={inputRef}
  onChange={handleInputChange}
  onKeyDown={handleKeyDown}
/>
```

Properties explained:
- `role="combobox"`: Input that shows suggestions
- `aria-autocomplete="list"`: Shows list of suggestions
- `aria-controls`: Links to the results container ID
- `aria-expanded`: Announces whether results are visible

#### Result Count Announcement

```jsx
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {results.length > 0
    ? `${results.length} results found`
    : 'No results found'}
</div>
```

This announces result count changes to screen readers:
- `aria-live="polite"`: Announces changes without interrupting speech
- `aria-atomic="true"`: Announces entire message, not just changes
- Hidden with `.sr-only` class (screen reader only)

### React Hooks Injection Constraint (CRITICAL)

When injecting search into existing vanilla React 18 SPAs, hook placement is CRITICAL. Violating this causes "React Error #321".

#### The Rule

All new useState/useEffect/useRef/useCallback/useMemo calls MUST be placed between the last existing useState and the first existing useEffect:

```javascript
// ❌ WRONG - Hook after useEffect
function SearchComponent() {
  useEffect(() => {
    // existing effect
  }, []);

  const [kbIndex, setKbIndex] = useState(-1);  // ERROR!
  // ...
}

// ✅ CORRECT - Hook before any useEffect
function SearchComponent() {
  // Existing hooks
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  // NEW hooks inserted here (between useState and useEffect)
  const [kbIndex, setKbIndex] = useState(-1);
  const inputRef = useRef(null);
  const resultsContainerRef = useRef(null);

  // Existing effects
  useEffect(() => {
    // existing effect
  }, []);

  // More effects...
}
```

#### Hook Ordering Rules

```javascript
// CORRECT hook order in React:
function SearchComponent() {
  // 1. All useState hooks
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [kbIndex, setKbIndex] = useState(-1);

  // 2. All useRef hooks
  const inputRef = useRef(null);
  const resultsContainerRef = useRef(null);

  // 3. All useCallback hooks
  const handleKeyDown = useCallback((e) => {
    // ...
  }, [kbIndex, results]);

  // 4. All useMemo hooks
  const filteredResults = useMemo(() => {
    return results.filter(r => r.relevant);
  }, [results]);

  // 5. All useEffect hooks (in dependency order)
  useEffect(() => {
    setKbIndex(-1);  // Reset on results change
  }, [results]);

  useEffect(() => {
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  return (
    // JSX
  );
}
```

#### Destructured Hooks Pattern

If the component uses destructured hooks:

```javascript
// ❌ WRONG - Mixing patterns
function SearchComponent() {
  const [query, setQuery] = React.useState('');  // old style
  const kbIndex = useState(-1);  // new style - INCONSISTENT!
}

// ✅ CORRECT - Keep pattern consistent
function SearchComponent() {
  const [query, setQuery] = React.useState('');
  const [results, setResults] = React.useState([]);
  const [kbIndex, setKbIndex] = React.useState(-1);  // Same pattern
  const inputRef = React.useRef(null);
}
```

#### Inside useEffect Callbacks (FORBIDDEN)

NEVER define useState inside useEffect:

```javascript
// ❌ ABSOLUTELY WRONG - Error #321
useEffect(() => {
  const [kbIndex, setKbIndex] = useState(-1);  // INVALID!
}, []);

// ✅ CORRECT - State defined outside
const [kbIndex, setKbIndex] = useState(-1);
useEffect(() => {
  // Use state here
  console.log(kbIndex);
}, [kbIndex]);
```

### Query Highlighting

Highlight the matched query text in search results:

#### HTML Structure

```jsx
<div className="search-result-item">
  <h3>
    {highlightMatch(result.title, query)}
  </h3>
  <p>{result.description}</p>
</div>
```

#### Highlighting Function

```javascript
function highlightMatch(text, query) {
  if (!query || !text) return text;

  try {
    // Escape regex special characters
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');

    const parts = text.split(regex);

    return parts.map((part, idx) => {
      if (idx % 2 === 0) {
        return part;  // Non-matched text
      } else {
        return (
          <mark key={idx} className="search-highlight">
            {part}
          </mark>
        );
      }
    });
  } catch (e) {
    // Fallback if regex fails
    return text;
  }
}
```

#### CSS for Highlight Mark

```css
.search-highlight {
  background: var(--color-highlight, #fef08a);  /* Light yellow in light mode */
  border-radius: 2px;
  padding: 0 1px;
  font-weight: 500;
}

@media (prefers-color-scheme: dark) {
  .search-highlight {
    background: rgba(59, 130, 246, 0.3);  /* Blue overlay in dark mode */
  }
}
```

#### Escaping Regex Special Characters

The regex escape is essential to handle queries like:

```javascript
highlightMatch("Use () for functions", "()")
// Without escape: Would be regex syntax error
// With escape: Correctly highlights "()"

highlightMatch("Match [brackets]", "[")
// Without escape: Would be regex syntax error
// With escape: Correctly highlights "["
```

## Production Deployment Verification Checklist

Before deploying documentation with search to production, verify every item on this checklist. Missing any single item can result in search appearing broken to users.

### Search Functionality

```
CRITICAL - Search Must Work
[ ] Run `npm run build` — static site generated in dist/
[ ] Run `npx pagefind --site dist/` — Pagefind index created
[ ] Verify dist/pagefind/ directory exists
[ ] Verify dist/pagefind/ contains: pagefind.js, pagefind-ui.js, pagefind-ui.css
[ ] Verify dist/pagefind/ contains fragment files (fragment-*.pf_fragment or .pf_json)
[ ] Open deployed site in browser
[ ] Search box visible on page
[ ] Typing in search box shows autocomplete suggestions within 200ms
[ ] Pressing Enter shows full results within 300ms
[ ] Autocomplete dropdown positioned correctly (not cut off by page layout)
[ ] Dropdown background visible (not transparent or blended)
[ ] Results are selectable with mouse and keyboard
```

### Search Quality

```
FUNCTIONAL QUALITY
[ ] Exact title search returns the correct page as #1 result
[ ] Code symbol search works (e.g., "validateToken" finds function)
[ ] camelCase search works (e.g., "get user" finds "getUserProfile")
[ ] snake_case search works (e.g., "get user" finds "get_user_profile")
[ ] Fuzzy search works (e.g., "authetication" suggests "authentication")
[ ] "Did you mean?" suggestion appears for misspelled queries
[ ] All documentation pages appear in search results
[ ] Pages marked VERIFIED rank higher than LOW confidence docs
[ ] Title matches rank above body-text-only matches
[ ] No spurious results for partial matches (searching "auth" returns relevant results)
```

### Keyboard Navigation

```
KEYBOARD MUST WORK
[ ] Arrow Down key navigates to next result
[ ] Arrow Up key navigates to previous result
[ ] Enter key opens the selected result
[ ] Escape key closes the search dropdown
[ ] Escape key clears keyboard selection
[ ] Ctrl+K (or Cmd+K on Mac) focuses the search input
[ ] Keyboard-selected item scrolls into view smoothly
[ ] Keyboard selection resets when query changes
[ ] Tab through results doesn't work (only arrow keys)
```

### Accessibility (WCAG 2.1 AA)

```
SCREEN READER
[ ] Search input has aria-label or label element
[ ] Results dropdown has role="listbox"
[ ] Result items have role="option"
[ ] aria-selected updates as keyboard selection changes
[ ] aria-expanded updates when results show/hide
[ ] Result count announcement works (aria-live)
[ ] No keyboard traps (user can always Escape)
[ ] Proper heading hierarchy in results (h3, not h1)

VISUAL INDICATORS
[ ] Keyboard-selected items have visible focus indicator (not just underline)
[ ] Hover and active states have sufficient contrast (WCAG AA minimum 4.5:1)
[ ] Focus indicator meets WCAG (2px outline or equivalent)
[ ] Error states use color + icon (not color alone)
```

### Responsive Design

```
MOBILE (< 640px)
[ ] Search input is at least 44x44px (tap target size)
[ ] Dropdown is scrollable and doesn't cover entire viewport
[ ] Dropdown max-height is 50vh or less
[ ] Results show complete on narrow screens
[ ] No horizontal scrolling in dropdown
[ ] Touch interactions (tap to open, tap to select) work

TABLET (640px - 1024px)
[ ] Dropdown width appropriate for screen size
[ ] Results legible without horizontal scroll
[ ] Confidence badges and symbols visible

DESKTOP (> 1024px)
[ ] Dropdown positioned correctly below input
[ ] Dropdown wider than input (for readability)
[ ] Scrollbar visible when results overflow
[ ] Results cards have proper spacing
```

### Performance

```
LOAD TIME
[ ] First search result appears in < 100ms
[ ] Search index loads lazily (not on page load)
[ ] Total search index size < 500KB (gzipped)
[ ] Pagefind JS bundle < 100KB (gzipped)

INTERACTION
[ ] Search doesn't block page scrolling during query
[ ] Search doesn't block clicking other page elements
[ ] Typing feels responsive (no lag)
[ ] Results update smoothly (no flicker)
[ ] Keyboard navigation doesn't stutter

OPTIMIZATION
[ ] Search runs on Web Worker (off main thread) if possible
[ ] Index is gzip-compressed in distribution
[ ] Unused CSS removed from search component
```

### Browser Compatibility

```
MODERN BROWSERS
[ ] Works in Chrome 90+
[ ] Works in Firefox 88+
[ ] Works in Safari 14+
[ ] Works in Edge 90+

MOBILE BROWSERS
[ ] Works in iOS Safari 14+
[ ] Works in Chrome Android
[ ] Works in Samsung Internet

FALLBACK BEHAVIOR
[ ] If search breaks, site still usable
[ ] No JavaScript errors in console
[ ] Graceful fallback if Pagefind fails to load
```

### Dark Mode Support

```
THEME DETECTION
[ ] Auto-detects system dark mode preference
[ ] Dark mode colors defined in CSS variables
[ ] Light mode colors defined in CSS variables
[ ] Switching dark mode doesn't break search

DARK MODE COLORS
[ ] Background high contrast with text (WCAG AA+)
[ ] Dropdown shadow visible in dark mode
[ ] Hover states distinguishable in dark mode
[ ] Code syntax colors readable in dark mode
[ ] Confidence badges visible in dark mode
```

### Build Pipeline

```
BUILD SCRIPT
[ ] npm run build creates dist/
[ ] Pagefind step runs after build
[ ] Pagefind configuration correct in pagefind.json
[ ] No errors in npm run build output
[ ] No errors in npx pagefind output

DEPLOYMENT
[ ] dist/ directory deployed to web server
[ ] All files in dist/pagefind/ uploaded
[ ] Proper MIME types set:
    [ ] .js files: application/javascript
    [ ] .json files: application/json
    [ ] .pf_fragment files: application/octet-stream
[ ] No CORS issues (if serving from CDN)
[ ] Files are gzip-compressed (if supported by server)
```

### SEO & Analytics

```
INDEXING
[ ] Search pages not blocked by robots.txt
[ ] Search functionality tracked in analytics
[ ] User searches logged for improvement insights
[ ] No search telemetry sent to third parties

METRICS
[ ] Search usage tracked (% of users)
[ ] Top search queries identified
[ ] Zero-result queries identified
[ ] Conversion (search to result click) tracked
```

### Edge Cases & Error Handling

```
ERROR HANDLING
[ ] Empty search (empty string) handled gracefully
[ ] Very long query (>500 chars) handled
[ ] Special characters in query (!, @, #, etc.) handled
[ ] Rapid typing doesn't cause multiple requests
[ ] Network error shows helpful message
[ ] Malformed search index shows error

EMPTY STATES
[ ] "No results found" message clear and helpful
[ ] Fallback suggestions shown for zero results
[ ] Search doesn't freeze on empty state

PERFORMANCE EDGE CASES
[ ] Very large documentation (10k+ pages) loads in < 1s
[ ] Search works on slow networks (3G)
[ ] Search works on low-end devices
```

### Verification Script

Run this script to test search functionality programmatically:

```bash
#!/bin/bash
# test-search.sh - Verify search deployment

set -e

echo "Checking search files..."
test -f dist/pagefind/pagefind.js || { echo "ERROR: pagefind.js not found"; exit 1; }
test -f dist/pagefind/pagefind-ui.js || { echo "ERROR: pagefind-ui.js not found"; exit 1; }
test -f dist/pagefind/pagefind-ui.css || { echo "ERROR: pagefind-ui.css not found"; exit 1; }

echo "Checking index files..."
ls dist/pagefind/*.pf_* > /dev/null || { echo "ERROR: No fragment files found"; exit 1; }

echo "Checking search CSS..."
grep -q "search-container" dist/search-styles.css || { echo "WARNING: search-styles.css not included"; }

echo "Checking search JS..."
grep -q "kbIndex" dist/search-component.js || { echo "WARNING: keyboard navigation not found"; }

echo "All checks passed!"
```

Run before deployment:
```bash
bash test-search.sh
```

### Post-Deployment Testing

After deploying to production:

1. **Manual smoke test** (2 minutes):
   - Visit site in Chrome, Firefox, Safari
   - Type in search box
   - Verify results appear
   - Click a result
   - Navigate back

2. **Automated test** (CI/CD):
   ```bash
   npm run build
   npx pagefind --site dist/
   npm run test:search  # custom test script
   ```

3. **User testing** (24 hours after deploy):
   - Monitor analytics for search usage
   - Check error logs for JavaScript errors
   - Verify top search queries are relevant
   - Identify any zero-result searches

4. **Rollback plan**:
   - If search completely broken: revert to previous build
   - If search partially broken: deploy hotfix
   - If search slow: enable lazy loading, optimize index

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
| Dropdown hidden behind content | No stacking context on container | Add `position: relative; z-index: 200;` to `.search-container` |
| Dropdown cuts off on mobile | No negative offsets on overlay | Use `left: -60px; right: -60px;` |
| Keyboard navigation doesn't work | Arrow handlers not attached | Verify `onKeyDown` listener on input |
| Screen reader doesn't announce results | Missing ARIA attributes | Add `role="listbox"` to dropdown, `role="option"` to items |
| Dark mode text unreadable | Using absolute colors instead of variables | Use `var(--color-bg)` not `#ffffff` |
| Focus indicator invisible | Default focus outline removed | Add `outline: 2px solid var(--color-primary);` |

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
| Styles | CSS custom properties | ~5KB | Theme support + accessibility |
| Accessibility | ARIA implementation | <1KB | Screen reader support |
| Worker | Web Worker | ~2KB | Non-blocking search |
| Build | build_search_index.js | N/A (build-time only) | Index generation |
