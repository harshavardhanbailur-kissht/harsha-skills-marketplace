# Web App Patterns for Stakeholder Guide Access

## Table of Contents
1. [Self-Contained HTML Approach](#self-contained)
2. [Architecture Decision](#architecture)
3. [Feature Requirements](#features)
4. [Role-Based Tab System](#tabs)
5. [Search & Filtering](#search)
6. [Data Structure](#data-structure)
7. [Mobile Responsiveness](#mobile)
8. [Offline Capability](#offline)
9. [Hosting Options](#hosting)

---

## Self-Contained HTML Approach

The recommended approach is a **single self-contained HTML file** that includes all data, styles, and logic inline. This allows for:

- Zero dependencies (no server, no build step, no npm)
- Works offline (can be emailed, shared via Slack, saved locally)
- Can be hosted on any static file server
- Version control friendly (single file per release)

The file structure inside the HTML:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Release Notes: [Project] [Version] — Stakeholder Guides</title>
  <style>/* All CSS inline */</style>
</head>
<body>
  <div id="app"></div>
  <script>
    // All release data embedded as JSON
    const RELEASE_DATA = { /* ... */ };

    // All stakeholder guides embedded
    const GUIDES = { /* ... */ };

    // App logic (tab switching, search, filtering)
  </script>
</body>
</html>
```

## Architecture Decision

**Why NOT a React/Next.js app**: The guides are documentation artifacts, not interactive applications. A static HTML file is:
- Instantly deployable (drag and drop to any host)
- Archivable (each release becomes a permanent record)
- Shareable (attach to email, upload to Confluence)
- Fast (no hydration, no client-side routing, no API calls)

**When to use React**: Only if the user explicitly wants a persistent dashboard that aggregates multiple releases over time, or if they need real-time Jira integration in the browser. In that case, use the `frontend-blitz` skill.

## Feature Requirements

The web app must support:

1. **Role-based tabs** — One tab per stakeholder (PM, QA, Dev, Training, BA, Ops, Leadership)
2. **Search** — Full-text search across all guides, highlighting matches
3. **Filter by**:
   - Date range
   - Feature category
   - Priority level
   - Status (Critical Fix / Live Now / Enhancement)
   - Journey stage
4. **Ticket deep-links** — Every ticket reference links to Jira
5. **Print-friendly** — Each tab can be printed as a standalone document
6. **Dark mode** — Toggle for developer preference
7. **Export** — Download individual guide as Markdown or PDF

## Role-Based Tab System

The tab interface should feel like a documentation site, not a dashboard:

```
┌──────────────────────────────────────────────────────────────┐
│ Kissht LAP Release Notes — March 2026                         │
│                                                                │
│ [PM] [QA] [Dev] [Training] [BA] [Ops] [Leadership] [Raw Data]│
├──────────────────────────────────────────────────────────────┤
│                                                                │
│ Filter: [Category ▼] [Priority ▼] [Status ▼] [Search...]     │
│                                                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Executive Summary                                         │ │
│ │ This sprint shipped 45 tickets across 8 release themes... │ │
│ │                                                           │ │
│ │ ■ Release Highlight 1                                     │ │
│ │   Status: CRITICAL FIX                                    │ │
│ │   Impact: BCM, Central Ops, Finance                       │ │
│ │   ...                                                     │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

Each tab loads its complete guide content. Tab switching is instant (no network requests).

### Tab Content Mapping

| Tab | Content Source | Template |
|-----|---------------|----------|
| PM | `templates/pm-guide.md` structure | Strategic narrative |
| QA | `templates/qa-guide.md` structure | Test impact matrix |
| Dev | `templates/dev-guide.md` structure | Technical changelog |
| Training | `templates/training-guide.md` structure | SOP updates |
| BA | `templates/ba-guide.md` structure | Process analysis |
| Ops | `templates/ops-guide.md` structure | Runbook updates |
| Leadership | Leadership summary template | Executive brief |
| Raw Data | Ticket-level data table | Sortable, filterable |

## Search & Filtering

### Search Implementation
- Full-text search across all guide content
- Highlights matching text in yellow
- Shows which tabs contain matches (badge count)
- Searches ticket keys, summaries, and guide content

### Filter Chips
```
Category:  [All] [Documents] [KYC] [Credit] [Sales PD] [Transaction] ...
Priority:  [All] [Highest] [High] [Medium] [Low]
Status:    [All] [Critical Fix] [Live Now] [Enhancement]
Journey:   [All] [Onboarding] [Verification] [Sanction] [Disbursement]
```

Filters apply across all tabs simultaneously. The content dynamically shows/hides based on active filters.

## Data Structure

The embedded JSON data structure for the web app:

```javascript
const RELEASE_DATA = {
  metadata: {
    project: "LAP",
    version: "Sprint 23",
    releaseDate: "2026-03-07",
    totalTickets: 45,
    bugCount: 30,
    storyCount: 12,
    subtaskCount: 3,
    criticalFixes: 4,
    avgCycleTime: 42.5
  },

  tickets: [
    {
      key: "LAP-2013",
      link: "https://kissht.atlassian.net/browse/LAP-2013",
      summary: "Introduced Conditional Approved transaction status",
      category: "Transaction & Sanction",
      journey: "IPA Pending → Disbursed",
      releaseTitle: "Transaction Status & Sanction Pipeline",
      status: "Live Now",
      audience: ["BCM", "Central Ops", "Finance"],
      context: "New Conditional Approved status for flexible sanction decisions",
      issueType: "Story",
      priority: "Medium",
      assignee: "Developer Name",
      cycleTime: 5.2,
      completedDate: "2026-03-01"
    }
    // ... more tickets
  ],

  announcements: [
    {
      title: "Transaction Status & Sanction Pipeline | Loan Disbursement",
      status: "Critical Fix",
      whatsNew: "...",
      whyMatters: "...",
      highlights: ["...", "..."],
      access: "...",
      tickets: ["LAP-2013", "LAP-641", "LAP-1340", "LAP-1413"]
    }
    // ... more announcements
  ],

  guides: {
    pm: "# Product Manager Release Notes\n...",
    qa: "# QA Impact Assessment\n...",
    dev: "# Developer Changelog\n...",
    training: "# Training & SOP Guide\n...",
    ba: "# Business Analyst View\n...",
    ops: "# Operations Runbook\n...",
    leadership: "# Executive Summary\n..."
  }
};
```

## Mobile Responsiveness

The web app must work on mobile (team members checking release notes on the go):

- Tabs become a dropdown selector on mobile
- Filter chips scroll horizontally
- Tables become card-based layouts
- Search stays prominent at top
- Print action available per section

## Offline Capability

Since the HTML is self-contained:
- No network requests needed after initial load
- All data embedded in the file
- Works when opened from email attachment
- Can be saved as local file for offline access
- No CDN dependencies (all CSS/JS inline)

## Hosting Options

In order of simplicity:

1. **Local file** — Save HTML to shared drive, email as attachment
2. **Confluence/Notion** — Upload HTML as attachment, embed or link
3. **GitHub Pages** — Push to repo, auto-deploy
4. **Google Cloud Storage** — Upload to bucket, share URL
5. **Internal web server** — Deploy to company intranet
6. **Slack file share** — Upload HTML directly to Slack channel

### Auto-Deploy Pattern

```bash
# After generating release notes HTML:
# Option 1: Copy to shared drive
cp release-notes-2026-03.html /shared/releases/

# Option 2: Push to GitHub Pages
git add docs/release-notes-2026-03.html
git commit -m "Release notes: Sprint 23, March 2026"
git push origin main

# Option 3: Upload to GCS
gsutil cp release-notes-2026-03.html gs://kissht-releases/
```

## Styling Guidelines

The web app should look professional and branded:

- Clean, readable typography (system fonts stack)
- Kissht brand colors where appropriate
- Status badges: Critical Fix (red), Live Now (green), Enhancement (amber)
- Sufficient whitespace
- Code blocks for technical content (Dev tab)
- Tables with zebra striping
- Collapsible sections for long content
- Smooth tab transitions
- Print stylesheet that removes navigation chrome

---

## Enhanced Search Implementation (MiniSearch)

For web apps with 50+ tickets, implement client-side fuzzy search using MiniSearch (3KB, zero dependencies):

```javascript
// Embed MiniSearch directly in the HTML (minified, ~3KB)
// Or use a simplified fuzzy search implementation:

class SimpleSearch {
  constructor(tickets) {
    this.tickets = tickets;
    this.index = this._buildIndex();
  }

  _buildIndex() {
    const index = {};
    this.tickets.forEach((ticket, i) => {
      const text = [
        ticket.key,
        ticket.summary,
        ticket.category,
        ticket.journey,
        ticket.assignee,
        ticket.context || ''
      ].join(' ').toLowerCase();

      // Bigram tokenization for fuzzy matching
      const tokens = text.split(/\s+/);
      tokens.forEach(token => {
        if (!index[token]) index[token] = new Set();
        index[token].add(i);
        // Also index bigrams for partial matches
        for (let j = 0; j < token.length - 1; j++) {
          const bigram = token.substr(j, 2);
          if (!index[bigram]) index[bigram] = new Set();
          index[bigram].add(i);
        }
      });
    });
    return index;
  }

  search(query) {
    const terms = query.toLowerCase().split(/\s+/);
    let results = null;

    terms.forEach(term => {
      const matches = new Set();
      // Exact token match
      if (this.index[term]) {
        this.index[term].forEach(i => matches.add(i));
      }
      // Prefix match
      Object.keys(this.index).forEach(key => {
        if (key.startsWith(term)) {
          this.index[key].forEach(i => matches.add(i));
        }
      });

      if (results === null) {
        results = matches;
      } else {
        // Intersection for multi-term queries
        results = new Set([...results].filter(i => matches.has(i)));
      }
    });

    return [...(results || [])].map(i => this.tickets[i]);
  }
}
```

### Search UX Enhancements

```javascript
// Tab match badges — show which tabs contain search matches
function updateTabBadges(query) {
  const tabs = ['pm', 'qa', 'dev', 'training', 'ba', 'ops', 'leadership'];
  tabs.forEach(tab => {
    const content = RELEASE_DATA.guides[tab] || '';
    const count = (content.toLowerCase().match(new RegExp(query.toLowerCase(), 'g')) || []).length;
    const badge = document.querySelector(`[data-tab="${tab}"] .badge`);
    if (badge) {
      badge.textContent = count > 0 ? count : '';
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
  });
}
```

---

## Progressive Web App (PWA) Capability

For teams that want the release notes available offline on mobile:

```javascript
// Add to the HTML <head>:
// <link rel="manifest" href="data:application/json,...">

// Inline service worker registration (no external file needed):
const SW_CODE = `
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => self.clients.claim());
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
`;

if ('serviceWorker' in navigator) {
  const blob = new Blob([SW_CODE], { type: 'application/javascript' });
  navigator.serviceWorker.register(URL.createObjectURL(blob))
    .catch(() => {}); // Graceful fallback
}
```

### Inline Manifest for PWA

```javascript
// Generate manifest data URL inline:
const manifest = {
  name: `Release Notes: ${RELEASE_DATA.metadata.project}`,
  short_name: 'Release Notes',
  start_url: '.',
  display: 'standalone',
  background_color: '#f5f5f5',
  theme_color: '#1a1a2e'
};
const link = document.createElement('link');
link.rel = 'manifest';
link.href = 'data:application/json,' + encodeURIComponent(JSON.stringify(manifest));
document.head.appendChild(link);
```

---

## Dark Mode Support

```css
/* Dark mode toggle — add to inline styles */
@media (prefers-color-scheme: dark) {
  body.auto-dark { background: #1a1a2e; color: #e0e0e0; }
  body.auto-dark .tab-content { background: #16213e; }
  body.auto-dark .controls { background: #1a1a2e; border-color: #333; }
  body.auto-dark .search { background: #16213e; color: #e0e0e0; border-color: #333; }
  body.auto-dark th { background: #1a1a2e; }
  body.auto-dark td { border-color: #333; }
  body.auto-dark .tab-btn { color: #aaa; }
  body.auto-dark .tab-btn.active { color: #fff; }
}

/* Manual toggle */
body.dark-mode { background: #1a1a2e; color: #e0e0e0; }
body.dark-mode .tab-content { background: #16213e; }
body.dark-mode .controls { background: #1a1a2e; border-color: #333; }
body.dark-mode .search { background: #16213e; color: #e0e0e0; border-color: #333; }
body.dark-mode th { background: #1a1a2e; }
body.dark-mode td { border-color: #333; }
body.dark-mode .tab-btn { color: #aaa; }
body.dark-mode .tab-btn.active { color: #fff; }
```

```javascript
// Dark mode toggle button
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}
// Restore preference
if (localStorage.getItem('darkMode') === 'true') {
  document.body.classList.add('dark-mode');
}
```

---

## Export & Download Capabilities

```javascript
// Export individual guide as Markdown
function exportMarkdown(tabKey) {
  const content = RELEASE_DATA.guides[tabKey];
  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `release-notes-${tabKey}-${RELEASE_DATA.metadata.releaseDate}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// Export all guides as ZIP (using inline JSZip or simple concatenation)
function exportAll() {
  const allContent = Object.entries(RELEASE_DATA.guides)
    .map(([key, content]) => `\n\n${'='.repeat(80)}\n${key.toUpperCase()} GUIDE\n${'='.repeat(80)}\n\n${content}`)
    .join('');
  const blob = new Blob([allContent], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `release-notes-all-${RELEASE_DATA.metadata.releaseDate}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

// Print single tab
function printTab(tabKey) {
  const content = document.getElementById(`tab-${tabKey}`);
  const win = window.open('', '_blank');
  win.document.write(`
    <html><head><title>Release Notes: ${tabKey}</title>
    <style>body{font-family:-apple-system,sans-serif;max-width:800px;margin:0 auto;padding:20px;}
    table{width:100%;border-collapse:collapse;}th,td{border:1px solid #ddd;padding:8px;text-align:left;}
    th{background:#f8f9fa;}</style></head>
    <body>${content.innerHTML}</body></html>
  `);
  win.print();
}
```

---

## Accessibility (WCAG 2.1 AA Compliance)

The web app should meet accessibility standards:

```html
<!-- ARIA roles for tab interface -->
<div role="tablist" aria-label="Stakeholder guides" class="tabs">
  <button role="tab" aria-selected="true" aria-controls="tab-pm" id="btn-pm" class="tab-btn active" data-tab="pm">
    Product Manager
  </button>
  <!-- ... more tabs -->
</div>

<div role="tabpanel" id="tab-pm" aria-labelledby="btn-pm" class="tab-content active">
  <!-- PM guide content -->
</div>
```

```javascript
// Keyboard navigation with ARIA
document.querySelectorAll('[role="tab"]').forEach(tab => {
  tab.addEventListener('keydown', (e) => {
    const tabs = [...document.querySelectorAll('[role="tab"]')];
    const idx = tabs.indexOf(e.target);
    let newIdx;

    switch(e.key) {
      case 'ArrowRight': newIdx = (idx + 1) % tabs.length; break;
      case 'ArrowLeft': newIdx = (idx - 1 + tabs.length) % tabs.length; break;
      case 'Home': newIdx = 0; break;
      case 'End': newIdx = tabs.length - 1; break;
      default: return;
    }

    e.preventDefault();
    tabs[newIdx].focus();
    tabs[newIdx].click();
  });
});
```

### Color Contrast Requirements
- Badge text: WCAG AA compliant (4.5:1 contrast ratio minimum)
- Critical Fix badge: white text on #EA4335 (passes AA)
- Live Now badge: white text on #34A853 (passes AA)
- Enhancement badge: #333 text on #FBBC04 (passes AA)
- All body text: #333 on #fff background (passes AAA)

---

## Cognitive Load Optimization (from Behavioral Interface Psychology)

### Information Architecture Principles

Based on cognitive research, the web app should respect these thresholds:

| Principle | Threshold | Application |
|-----------|-----------|-------------|
| Working memory | 4±1 chunks | Max 7 tabs (PM, QA, Dev, Training, BA, Ops, Leadership) |
| Menu depth | 2-3 levels max | Tab → Section → Detail (never deeper) |
| Scan time | 47 seconds average | Front-load critical info in each tab |
| Value prop window | 2.6 seconds | Executive summary visible without scrolling |
| Line length | 50-75 characters | Set `max-width: 700px` on content container |
| Body font minimum | 16px | Never smaller for body text |

### Progressive Disclosure in Web App

Apply 3-level progressive disclosure (from Deep Research Synthesizer pattern):

```
Level 1: TL;DR Banner (always visible)
    "Sprint 24: 45 tickets | 4 critical fixes | Bureau + Document improvements"

Level 2: Tab Summary (expandable)
    "PM View: 8 release announcements, top win = bureau waiver fix, 2 risks flagged"

Level 3: Full Guide Content (tab body)
    Complete stakeholder-specific guide with all sections
```

### Alert Fatigue Prevention

From behavioral psychology research — avoid "Three Mile Island Pattern" where critical signals are lost in noise:

- **Distinguish signal from noise**: Use status badges (Critical Fix = red, prominent) vs (Enhancement = subtle amber)
- **Limit visible items**: Show top 5 highlights per tab, collapse rest under "Show all N items"
- **Aggregate low-priority**: Group minor fixes into collapsible "Other Changes" section
- **First impression matters**: 50ms aesthetic judgment — the web app must look professional immediately

### Audience-Optimized Reading Patterns

| Audience | Reading Pattern | Design Implication |
|----------|----------------|-------------------|
| PM | F-pattern scan, headline-focused | Bold key metrics, front-load business impact |
| QA | Systematic, checklist-oriented | Use checkboxes for test scenarios, tables for matrices |
| Dev | Code-first, skim-for-relevance | Monospace ticket keys, code blocks, minimal prose |
| Training | Step-by-step, sequential | Numbered lists, Before/After comparisons |
| BA | Analytical, relationship-seeking | Tables, flow diagrams, cross-reference links |
| Ops | Action-oriented, urgency-driven | Checklists, color-coded severity, escalation contacts |
| Leadership | Metric-driven, 30-second scan | Dashboard-style numbers, trend arrows, 1-paragraph summary |

---

## BM25F Field-Weighted Search (Advanced)

For large releases with 100+ tickets, upgrade from simple search to BM25F:

```javascript
class BM25FSearch {
  /**
   * BM25F field-weighted search — adapted from Deep Research Synthesizer v2.5
   * Field weights: title (3.0), summary (2.0), content (1.0), tags (2.5), category (1.5)
   */
  constructor(documents, fieldWeights = null) {
    this.docs = documents;
    this.weights = fieldWeights || {
      key: 4.0,        // Ticket key (exact match priority)
      summary: 3.0,    // Ticket summary
      category: 2.5,   // Feature category
      context: 2.0,    // Business context
      assignee: 1.5,   // Developer name
      journey: 1.5,    // Journey stage
      audience: 1.0    // Affected roles
    };
    this.k1 = 1.2;
    this.b = 0.75;
    this.avgDl = {};
    this.df = {};
    this.N = documents.length;
    this._buildIndex();
  }

  _buildIndex() {
    // Calculate average document length per field
    for (const field of Object.keys(this.weights)) {
      let totalLen = 0;
      this.docs.forEach(doc => {
        const val = String(doc[field] || '');
        totalLen += val.split(/\s+/).filter(Boolean).length;
      });
      this.avgDl[field] = totalLen / this.N || 1;
    }

    // Calculate document frequency per term
    this.docs.forEach(doc => {
      const seen = new Set();
      for (const field of Object.keys(this.weights)) {
        const tokens = String(doc[field] || '').toLowerCase().split(/\s+/);
        tokens.forEach(t => {
          const key = `${field}:${t}`;
          if (!seen.has(key)) {
            seen.add(key);
            this.df[key] = (this.df[key] || 0) + 1;
          }
        });
      }
    });
  }

  search(query, topN = 20) {
    const qTerms = query.toLowerCase().split(/\s+/).filter(Boolean);
    const scores = this.docs.map((doc, idx) => {
      let score = 0;
      for (const field of Object.keys(this.weights)) {
        const tokens = String(doc[field] || '').toLowerCase().split(/\s+/);
        const dl = tokens.length;
        const avgDl = this.avgDl[field];
        const w = this.weights[field];

        for (const q of qTerms) {
          const tf = tokens.filter(t => t.includes(q)).length;
          const dfKey = `${field}:${q}`;
          const docFreq = this.df[dfKey] || 0;
          const idf = Math.log((this.N - docFreq + 0.5) / (docFreq + 0.5) + 1);
          const tfNorm = (tf * (this.k1 + 1)) /
            (tf + this.k1 * (1 - this.b + this.b * dl / avgDl));
          score += w * idf * tfNorm;
        }
      }
      return { idx, score };
    });

    return scores
      .filter(s => s.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, topN)
      .map(s => ({ ...this.docs[s.idx], _score: s.score }));
  }
}
```

---

## Lightweight CSS Framework Options

For professional styling without custom CSS, consider these zero-dependency options:

| Framework | Size | Best For | CDN |
|-----------|------|----------|-----|
| **Pico.css** | 10KB | Semantic HTML styling, clean forms | `unpkg.com/@picocss/pico` |
| **Water.css** | 2KB | Minimal, classless styling | `cdn.jsdelivr.net/npm/water.css` |
| **Simple.css** | 4KB | Documentation-style pages | `cdn.simplecss.org/simple.min.css` |
| **MVP.css** | 7KB | Minimal viable product look | `unpkg.com/mvp.css` |

**Recommendation**: For self-contained HTML (no CDN), embed Pico.css minified inline. For CDN-allowed deployments, use Pico.css via CDN link.

**Self-contained inline approach** (preferred for release notes):
```html
<style>
  /* Embed minified CSS framework inline — zero external dependencies */
  /* Use system font stack for cross-platform consistency */
  :root {
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   "Helvetica Neue", Arial, sans-serif;
    --font-mono: "SF Mono", "Fira Code", "Consolas", monospace;
    --color-primary: #1a73e8;
    --color-critical: #EA4335;
    --color-success: #34A853;
    --color-warning: #FBBC04;
    --color-bg: #ffffff;
    --color-text: #333333;
    --color-border: #e0e0e0;
    --radius: 6px;
    --shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
</style>
```

---

## Print Stylesheet

```css
@media print {
  /* Hide navigation and interactive elements */
  .tabs, .controls, .search, .dark-toggle,
  .export-btn, .print-btn, .filter-chips { display: none !important; }

  /* Show only active tab content */
  .tab-content { display: none !important; }
  .tab-content.active { display: block !important; }

  /* Reset colors for print */
  body { background: white !important; color: black !important; }
  * { box-shadow: none !important; }

  /* Ensure tables don't break across pages */
  table { page-break-inside: avoid; }
  tr { page-break-inside: avoid; }

  /* Add page headers */
  @page { margin: 2cm; }
  @page :first { margin-top: 3cm; }

  /* Show URLs for links */
  a[href^="http"]::after {
    content: " (" attr(href) ")";
    font-size: 0.8em;
    color: #666;
  }

  /* Expand collapsible sections */
  details { open: true; }
  details > summary { font-weight: bold; }
}
```

---

## Responsive Table Pattern

For mobile devices, convert tables to card layouts:

```css
@media (max-width: 768px) {
  /* Convert table to card layout on mobile */
  table.responsive thead { display: none; }
  table.responsive tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 0.75rem;
  }
  table.responsive td {
    display: flex;
    justify-content: space-between;
    padding: 0.25rem 0;
    border: none;
  }
  table.responsive td::before {
    content: attr(data-label);
    font-weight: 600;
    margin-right: 1rem;
    flex-shrink: 0;
  }
}
```

---

## Diátaxis-Inspired Content Organization

Adapt the Diátaxis documentation framework (from Codebase Handoff Documenter) for each tab:

| Tab | Diátaxis Type | Content Approach |
|-----|--------------|-----------------|
| PM | **Explanation** | Why changes matter, business narrative |
| QA | **How-To Guide** | Step-by-step test scenarios, checklists |
| Dev | **Reference** | Technical changelog, API changes, code areas |
| Training | **Tutorial** | Before/After walkthroughs, SOP updates |
| BA | **Explanation** | Process impact analysis, data flow changes |
| Ops | **How-To Guide** | Deployment runbook, monitoring checklists |
| Leadership | **Explanation** | Executive brief, balanced scorecard |
| Raw Data | **Reference** | Sortable ticket table, all fields visible |
