---
title: Deep Research Synthesizer
description: |
  STOP! Before you run random queries, read this. This skill transforms fragmented web searches into a cohesive knowledge base. It orchestrates multi-pass research, cross-references sources, detects hallucinations, and builds relationship maps between concepts. Your research will be thorough, trustworthy, and actually useful.
mcp_tools_used:
  - WebSearch
  - WebFetch
  - Glob
  - Grep
  - Read
  - Write
  - Notion tools (fetch, search, create-pages, update-page)
tags: [research, knowledge-base, synthesis, quality-assurance, knowledge-graphs, proptech, real-estate]
---

# Deep Research Synthesizer

**Status**: Production-ready
**Version**: 2.5
**Last Updated**: 2026-02-09

## Executive Summary

The Deep Research Synthesizer is a skill for transforming raw research queries into structured, verified knowledge bases. It orchestrates 6 phases of research, quality assurance, and synthesis, complete with relationship mapping and hallucination detection.

**Key improvements in v2.5**:
- Phase 3.5: Knowledge Graph Building (relationship mapping between entries)
- Phase 4.5: Research Quality Assurance (fact-checking and verification)
- Failure recovery paths for each phase
- Concrete worked example with topic flowing through all phases
- Performance budgets and metrics
- Enhanced sub-agent scaling guidance
- Anti-patterns and testing guidance
- **NEW: PropTech Domain Mode** — auto-detects PropTech queries and switches to specialized research pipeline, PropTech-specific UI, deeper multi-pass research, and India/US/UK market-aware prompts
- **NEW: BM25F Search Algorithm** — replaces basic TF-IDF with field-weighted BM25F scoring, trigram fuzzy matching, faceted filtering
- **NEW: Advanced Search Algorithms Reference** — complete client-side search engine with autocomplete, facets, and performance benchmarks
- **NEW: PropTech Web App Template** — map views (Leaflet), property cards, market segment filters, region-based visualization, D3 knowledge graph with PropTech-specific UI/UX

## The 6+2 Phase Research Pipeline

### Phase 1: Research Planning & Query Synthesis (15-30 min)

**Goal**: Transform a research request into 5-10 targeted queries that cover the topic comprehensively.

**Process**:
1. **Decompose the topic** into core sub-questions
   - Example: "How is AI transforming healthcare?" → [diagnosis automation, drug discovery, administrative efficiency, patient outcomes, regulatory challenges]
2. **Generate diverse query angles**
   - Industry perspective: "AI healthcare applications 2025"
   - Academic perspective: "machine learning clinical decision support"
   - Risk perspective: "AI healthcare regulatory concerns"
   - Practical perspective: "AI healthcare implementation case studies"
3. **Add specificity markers** (geography, time, sector)
4. **Create fallback queries** for low-signal searches

**Metrics**:
- Query count: 5-10 (more = deeper but slower)
- Diversity score: Queries should cover ≥3 different angles
- Time budget: 15-30 minutes to plan (don't over-plan)

**Failure Recovery**:
- If decomposition stalls: Use WebSearch to find "overview" or "introduction" articles first, then re-decompose
- If queries too broad: Add specificity (year, geography, industry)
- If no good angles emerge: Proceed with 3-5 broad queries and adapt in Phase 2

**Concrete Example**: Topic = "Sustainable Fashion Supply Chains"
- Query 1: "sustainable fashion supply chain 2025"
- Query 2: "textile production environmental impact"
- Query 3: "circular economy clothing brands"
- Query 4: "ethical sourcing supply chain verification"
- Query 5: "fast fashion environmental cost"

---

### Phase 2: Breadth Search (30-60 min)

**Goal**: Map the topic landscape quickly. Identify key themes, controversies, stakeholders.

**Process**:
1. **Execute all Phase 1 queries** via WebSearch
2. **Capture initial results** (first 5-10 results per query)
3. **Quick scan** of each result (5-10 seconds) for relevance
4. **Tag emerging themes** as you scan
   - Theme = a recurring topic/concept that appears 2+ times
5. **Flag contradictions** (opposing viewpoints)
6. **Identify authoritative sources** (gov, .edu, major publications)

**Output Structure**:
```
Topic Map:
- Theme 1: [description] (3 sources)
  - Sub-theme 1a (2 sources)
  - Sub-theme 1b (1 source)
- Theme 2: [description] (5 sources)
- Controversy: [issue] (pro: sources, con: sources)
- Gaps: [things mentioned but not well-covered]
```

**Metrics**:
- Sources scanned: 25-50 minimum
- Themes identified: 5-10
- Contradictions found: 0-3 (normal)
- Time per source: 5-10 seconds (quick scan only)

**Failure Recovery**:
- If low-quality results: Refine queries, add specificity
- If no clear themes: You're in a new/niche area — proceed with Phase 3, expect UNKNOWN ratings
- If too many contradictions: Mark as high-controversy topic, proceed with Phase 3.5 (relationship building) early

**Example Output for Sustainable Fashion**:
```
Topic Map:
- Environmental Impact (8 sources)
  - Water usage and pollution
  - Carbon emissions in production
  - Textile waste and landfill
- Supply Chain Transparency (5 sources)
  - Certification standards
  - Blockchain tracking
  - Third-party audits
- Economic Models (6 sources)
  - Circular fashion business models
  - Consumer willingness to pay premium
- Controversy: Greenwashing vs. genuine sustainability (conflicting claims)
- Gaps: Developing world worker perspectives, emerging materials science
```

---

### Phase 3: Depth Research (60-180 min)

**Goal**: Deep-dive into each theme with specific queries, extract key insights, find primary sources.

**Process**:
1. **For each theme identified in Phase 2**, execute 2-3 specific queries
   - Example: If "Water usage" is a theme, query: "textile production water consumption gallons", "cotton farming water pollution", "dyeing wastewater treatment"
2. **Fetch full content** of 5-10 most relevant results per theme
   - Use WebFetch tool
   - Extract main content (ignore nav, ads, footers)
3. **Extract knowledge entries** (see knowledge-ingestion.md for detailed pipeline)
   - Title, summary, key claims, statistics, date, source URL
4. **Document sources** with authority tier (see research-quality-assurance.md)
5. **Capture evidence chains**
   - Quote: "87% of textile production uses virgin materials" — who said this first?
   - Verify: Can you find this stat in a primary source?

**Metrics**:
- Depth per theme: 3-5 sources minimum
- Entry extraction rate: 1-2 entries per source (don't over-parse)
- Time per source: 10-20 minutes (real reading)
- Authority distribution: ≥50% Tier 1-2 sources

**Failure Recovery**:
- If sources insufficient for a theme: Proceed with UNKNOWN entries, flag for manual review
- If content paywalled: Try WebFetch, note as UNKNOWN if not readable
- If contradictions within sources: Document both viewpoints separately, flag as low confidence
- If theme collapses (not a real topic): Merge with adjacent theme or remove

**Example for Water Usage Theme**:
```
Entry 1: Cotton Water Consumption
- Title: "Water Crisis in Cotton Production"
- Source: [University of Michigan water institute]
- Claim: "Cotton production uses 2,700 liters per shirt"
- Authority: Tier 1 (academic research center)
- Confidence: HIGH (verified in 2+ sources)

Entry 2: Dyeing Industry Impact
- Title: "Textile Dyeing: The World's Largest Water Polluter"
- Source: [UN Environment Programme report]
- Claim: "10-20% of industrial water pollution comes from dyeing"
- Authority: Tier 1 (UN official)
- Confidence: HIGH
```

---

### Phase 3.5: Knowledge Graph Building (30-60 min)

**Goal**: Map relationships between entries. Build the knowledge graph structure that powers search and discovery.

**Process**:
1. **Identify relationship types** (see knowledge-graph-builder.md)
   - Semantic: "Water usage" and "Dyeing wastewater" discuss same concept
   - Hierarchical: "Textile Production" → "Cotton Farming" → "Water Management"
   - Causal: "Rising water prices" causes "shift to synthetic materials"
   - Temporal: "2020 pandemic" preceded "supply chain restructuring"
   - Comparative: "Organic cotton" vs. "Conventional cotton"
   - Dependency: Understanding "circular economy" requires "material science basics"

2. **Detect relationships algorithmically**
   - Explicit: Entries that cite each other
   - Tag overlap: Entries sharing 2+ tags
   - Content similarity: TF-IDF cosine similarity > 0.3
   - Category siblings: Entries in same subcategory

3. **Build graph data structure** (JSON format, see knowledge-graph-builder.md)
   - Nodes: Each entry
   - Edges: Relationships with type and strength (0-1.0)
   - Clusters: Topic communities detected via modularity

4. **Calculate graph metrics**
   - Centrality: Which entries are hubs? (high connectivity)
   - Orphans: Entries with 0 connections (possible gaps)
   - Bridges: Entries connecting otherwise isolated clusters
   - Density: Overall connectedness (0-1.0)

5. **Visualize** (optional but recommended)
   - D3.js force-directed graph
   - Node size = connectivity
   - Node color = category
   - Edge color = relationship type

**Metrics**:
- Graph density target: 0.15-0.35 (too high = everything related to everything; too low = fragmented)
- Avg connections per entry: 3-7
- Orphan count: <10% of total entries (flag for review)
- Clustering coefficient: Shows local clustering

**Failure Recovery**:
- If fragmented graph (low density): May indicate incomplete research — return to Phase 2
- If too many orphans: Add Phase 3 queries to fill gaps
- If dense subclusters but weak bridges: Add comparative entries to connect themes
- If false relationships: Adjust similarity threshold or remove false edges

**Example Graph for Sustainable Fashion**:
```json
{
  "nodes": [
    {"id": "entry-water", "title": "Cotton Water Usage", "category": "environmental", "connections": 5},
    {"id": "entry-dyeing", "title": "Dyeing Wastewater", "category": "environmental", "connections": 6},
    {"id": "entry-circular", "title": "Circular Economy Models", "category": "economic", "connections": 7},
    {"id": "entry-cert", "title": "Certification Standards", "category": "governance", "connections": 4}
  ],
  "edges": [
    {"source": "entry-water", "target": "entry-dyeing", "type": "semantic", "strength": 0.9},
    {"source": "entry-water", "target": "entry-cert", "type": "dependency", "strength": 0.7},
    {"source": "entry-circular", "target": "entry-dyeing", "type": "causal", "strength": 0.6}
  ],
  "clusters": [
    {"name": "Environmental Impact", "nodes": ["entry-water", "entry-dyeing"], "density": 0.95},
    {"name": "Governance & Economics", "nodes": ["entry-circular", "entry-cert"], "density": 0.6}
  ]
}
```

---

### Phase 4: Source Deep-Dive (60-120 min)

**Goal**: Extract evidence chains. Verify statistics. Trace claims back to primary sources.

**Process**:
1. **For each key claim** that appears in multiple entries:
   - "87% of textile production uses virgin materials"
   - "Dyeing produces 10-20% of industrial water pollution"

2. **Trace the claim backwards**
   - Search the exact quote
   - Find the original paper/report (primary source)
   - Check methodology: Is it rigorous?
   - Check year: Is it current?
   - Check scope: Does it apply to your context?

3. **Verify statistics**
   - If stat is cited with source: Fetch that source, verify claim
   - If no citation: Mark as UNVERIFIED, search for original
   - If conflicting stats exist: Document all, note which have strongest evidence

4. **Build evidence chains**
   ```
   Claim: "Circular economy can reduce textile waste"
   ├─ Primary source: MIT research "Circular Materials Study 2024"
   ├─ Secondary source: UN sustainability report citing MIT
   └─ Derivative: News article reporting on UN report (weakest)
   Confidence: HIGH (primary + secondary agreement)
   ```

5. **Document authority tiers** (see research-quality-assurance.md)
   - Tier 1: Primary sources (academic papers, official reports, government data)
   - Tier 2: Reputable secondary (established publications, non-profit orgs)
   - Tier 3: Community (blogs, forums, user-generated)
   - Tier 4: Unverified (random sources, single citations)

**Metrics**:
- Claims traced: 100% of key claims
- Evidence chain depth: Average ≥2 sources per chain
- Authority mix: ≥60% Tier 1-2 sources
- Time per claim: 10-20 minutes

**Failure Recovery**:
- If claim unverifiable: Mark as UNKNOWN, remove from knowledge base OR keep with LOW confidence
- If only weak sources: Document as such, flag for expert review
- If conflicting evidence equally strong: Keep both, note controversy
- If evidence from geo/time outliers: Note limitations (e.g., "data from India 2015")

---

### Phase 4.5: Research Quality Assurance (30-60 min)

**Goal**: Verify the entire research output before it enters the knowledge base. Catch hallucinations, contradictions, bias.

**Process**:
1. **Multi-pass verification pipeline** (see research-quality-assurance.md)
   - **Pass 1 (Accuracy)**: Do claims have citations? Do URLs resolve?
   - **Pass 2 (Completeness)**: Does entry cover all important angles?
   - **Pass 3 (Consistency)**: Does it conflict with other entries?
   - **Pass 4 (Recency)**: How current is the information?

2. **Hallucination detection** (key red flags)
   - Overly specific statistics without citation (e.g., "exactly 47.3%")
   - Claims that sound too clean (too simple, no nuance)
   - URLs that don't resolve or look fake
   - Organization names that don't exist
   - Date references that don't make sense (future dates, etc.)
   - Quotes without source attribution

3. **Cross-entry contradiction check**
   - Search for opposing claims
   - Document conflicts with sources on each side
   - Note if one source is more authoritative
   - Flag for manual review if unresolved

4. **Quality scoring** (0-50 scale, minimum 30 to include)
   - Accuracy (0-10): Are claims verifiable?
   - Completeness (0-10): Are all aspects covered?
   - Depth (0-10): Surface-level vs. expert-level?
   - Recency (0-10): How current?
   - Consistency (0-10): Conflicts with other entries?

   Example: Entry scores 9 (accuracy) + 8 (completeness) + 7 (depth) + 8 (recency) + 9 (consistency) = 41/50 ✓ PASS

5. **Fact-checking checklist**
   - [ ] All statistics have citations (searchable)
   - [ ] All URLs resolve to real pages
   - [ ] Key claims appear in 2+ independent sources
   - [ ] No fabricated organizations, publications, or people
   - [ ] Date references are accurate and make sense
   - [ ] Technical claims are internally consistent
   - [ ] Author/source attribution is clear

**Metrics**:
- Entry pass rate: Target ≥80% (entries scoring 30+/50)
- False positive rate: <5% (entries that fail QA but are actually correct)
- Time per entry: 5-10 minutes
- Contradiction resolution rate: 100% (all conflicts documented)

**Failure Recovery**:
- If entry fails QA but seems important: Review manually, or ask expert
- If high failure rate (>50%): Return to Phase 3, re-source entries
- If contradictions unresolvable: Document both sides as equal-authority viewpoints
- If sources unreliable: Extend Phase 2 to find better sources

**Example QA Scoring**:
```
Entry: "Cotton Production Water Usage"
- Accuracy: 9/10 (citations verifiable, stats cross-checked)
- Completeness: 8/10 (covers production, dyeing, finishing; misses recycling angle)
- Depth: 7/10 (good overview; lacks mechanical details)
- Recency: 9/10 (sources from 2023-2025)
- Consistency: 9/10 (matches other water entries)
TOTAL: 42/50 ✓ PASS

Entry: "Greenwashing: Industry Scale"
- Accuracy: 6/10 (one statistic unverifiable)
- Completeness: 5/10 (mostly focuses on fast fashion, ignores luxury)
- Depth: 4/10 (surface-level analysis)
- Recency: 6/10 (sources from 2022-2023, outdated)
- Consistency: 5/10 (conflicts with Brand A's sustainability claims)
TOTAL: 26/50 ✗ FAIL — FLAG FOR EXPERT REVIEW
```

---

### Phase 5: Knowledge Base Assembly & Ingestion (30-60 min)

**Goal**: Combine all verified entries into a structured knowledge base. Deduplicate. Enrich metadata.

**Process**:
1. **Deduplicate entries**
   - Identical titles? Merge (keep higher confidence)
   - Similar content (90%+ match)? Merge or flag as duplicate angle
   - Same claim, different sources? Keep separate entries, link them

2. **Normalize metadata**
   - Title: Concise (50-100 characters)
   - Summary: 150-300 words
   - Content: 300-1000 words per entry
   - Tags: 3-7 per entry (must match existing taxonomy)
   - Source URL + access date
   - Authority tier (Tier 1-4)
   - Confidence level (HIGH, MEDIUM, LOW, UNKNOWN)
   - Creation date (when added to KB)

3. **Add knowledge base metadata**
   - Entry ID: UUID or slug
   - Category: Main category (e.g., "Environmental Impact")
   - Subcategory: Specific area (e.g., "Water")
   - Related entries: Links to Phase 3.5 knowledge graph
   - Conflicts: Flag entries with contradicting claims
   - Last verified: Date of QA check

4. **Ingest into chosen backend**
   - Notion database (using Notion MCP)
   - JSON knowledge graph file
   - Vector database (Pinecone, Weaviate) if search needed
   - Static site generator (if publishing)

5. **Generate ingestion report**
   - Total entries: X
   - Pass rate: Y%
   - Confidence breakdown: Z% HIGH, W% MEDIUM, etc.
   - Gaps identified: [list of areas needing more research]
   - Sources by tier: Tier 1 (X%), Tier 2 (Y%), etc.

**Metrics**:
- Deduplication rate: 5-15% (typical for large research)
- Ingestion time: <30 minutes
- Metadata completeness: 100% of fields filled
- Entry count final: Sum of all themes

**Failure Recovery**:
- If duplicate detection missed true duplicates: Manual pass before publish
- If metadata incomplete: Use defaults or flag for manual entry
- If ingestion fails: Validate JSON/CSV format, check MCP tools

**Example Ingestion Report**:
```
KNOWLEDGE BASE INGESTION REPORT
Topic: Sustainable Fashion Supply Chains
Date: 2026-02-09

Summary:
- Total entries ingested: 47
- Pass rate: 89% (42 entries ≥30/50 QA score)
- Failed QA: 5 entries (flagged for expert review)

Confidence Distribution:
- HIGH: 34 entries (72%)
- MEDIUM: 7 entries (15%)
- LOW: 5 entries (11%)
- UNKNOWN: 1 entry (2%)

Source Authority Distribution:
- Tier 1 (primary/academic): 23 entries (49%)
- Tier 2 (reputable secondary): 18 entries (38%)
- Tier 3 (community): 6 entries (13%)
- Tier 4 (unverified): 0 entries (0%)

Category Breakdown:
- Environmental Impact: 18 entries
- Supply Chain Transparency: 12 entries
- Economic Models: 10 entries
- Regulatory & Governance: 7 entries

Identified Gaps:
- Worker welfare perspectives from developing countries (LOW coverage)
- Emerging materials science beyond cotton (MINIMAL coverage)
- Consumer behavior and attitude shifts (MODERATE coverage)
- Technology solutions (blockchain, IoT) (MODERATE coverage)

Recommendations:
- Conduct targeted Phase 2-3 research on worker welfare
- Extend Phase 3 to include material innovation sources
- Consider expert review for 5 failed QA entries
```

---

### Phase 6: Knowledge Graph Visualization & Discovery (20-60 min)

**Goal**: Make the knowledge base discoverable and navigable. Visualize relationships.

**Process**:
1. **Build D3.js force-directed graph** (see knowledge-graph-builder.md)
   - Load JSON from Phase 3.5
   - Render nodes (entries) with size = connectivity
   - Render edges (relationships) with color = type
   - Add interactivity: hover to highlight, click to expand

2. **Create cluster visualization**
   - Show topic clusters as regions
   - Label clusters
   - Show bridges between clusters
   - Allow toggling cluster visibility

3. **Build search interface**
   - Full-text search across entry titles, summaries, content
   - Faceted search (by category, authority, confidence)
   - Related entries based on graph proximity
   - Similar entries based on content similarity

4. **Generate static exports**
   - SVG visualization for documentation/reports
   - DOT format for Graphviz rendering
   - Bibliography (CSV or JSON)
   - Topic outline (hierarchical)

5. **Publish knowledge base** (if web-facing)
   - Choose platform: Static HTML site, Notion public workspace, GitHub Pages, etc.
   - Optimize for SEO (if desired)
   - Add metadata (description, authors, last updated)

**Metrics**:
- Graph rendering time: <2 seconds
- Search response time: <500ms
- Visualization accessibility: Works on desktop + mobile
- Click-through distance to any entry: <3 clicks from home

**Failure Recovery**:
- If graph too dense to visualize: Reduce edge threshold (only show strength >0.5)
- If search slow: Add indexing or pre-compute popular queries
- If mobile display broken: Use responsive D3 or simplify visualization
- If export corrupted: Regenerate from source JSON

---

## Sub-Agent Scaling Guidance

When research scope is large (100+ entries expected), distribute work across multiple agents:

**Agent Pool Formula**:
- Entries per agent: 15-25 per Phase 3
- Number of agents needed: ceil(total_entries / 20)
- Example: 100 entries → 5 agents in parallel

**Phase Parallelization**:

| Phase | Parallelizable? | Pool Size | Notes |
|-------|-----------------|-----------|-------|
| Phase 1 | YES | 1-2 | Merge results |
| Phase 2 | YES | 1-2 | Merge theme maps |
| Phase 3 | YES | N agents | Each researches subset of themes |
| Phase 3.5 | NO | 1 | Must see all entries |
| Phase 4 | YES | N/2 agents | Verify different claims |
| Phase 4.5 | NO | 1-2 | Centralized QA |
| Phase 5 | YES | 1-2 | One lead, one backup |
| Phase 6 | YES | 1 | Sequential (depends on Phase 5 output) |

**Coordination Pattern**:
```
Phase 1 (Agent A): Plan queries
  ↓ (queries distributed)
Phase 2 (Agent B, C): Breadth search in parallel
  ↓ (merged theme map)
Phase 3 (Agent B, C, D, E): Each agent researches N/4 themes
  ↓ (entries combined)
Phase 3.5 (Agent A): Build graph from all entries
  ↓
Phase 4 (Agent B, C): Verify evidence chains in parallel
  ↓
Phase 4.5 (Agent A): Centralized QA scoring
  ↓
Phase 5 (Agent A, D): Deduplicate, ingest
  ↓
Phase 6 (Agent A): Publish, visualize
```

**Communication Protocol**:
- Shared JSON file for passing data between phases
- Explicit handoff checklist (what must be complete before next phase)
- Conflict resolution: If agents disagree on theme categorization, vote or escalate to Phase Lead

---

## Performance Budgets

**Small research** (5-10 entries): 4-6 hours
- Phase 1: 20 min
- Phase 2: 30 min
- Phase 3: 90 min
- Phase 3.5: 15 min
- Phase 4: 30 min
- Phase 4.5: 20 min
- Phase 5: 15 min
- Phase 6: 10 min

**Medium research** (20-50 entries): 8-12 hours
- Phases 1-2: 1 hour
- Phase 3: 3 hours
- Phase 3.5: 30 min
- Phase 4: 1 hour
- Phase 4.5: 45 min
- Phase 5: 45 min
- Phase 6: 30 min

**Large research** (100+ entries): 20-40 hours
- Use sub-agent scaling
- Expect 4-6 weeks with careful coordination
- Budget extra time for conflict resolution

---

## Reference Files

| File | Read When | Purpose |
|------|----------|---------|
| `references/sonnet-45-prompting-bible.md` | Before launching ANY sub-agent, or when user asks for prompt optimization | The definitive Sonnet 4.5 prompting guide — 10 golden rules, XML patterns, extended thinking, output schemas, domain-specific templates, prompt chaining, anti-patterns |
| `references/sub-agent-orchestration.md` | When spawning research agents (Phase 3-4) | Multi-pass research architecture, parallel dispatch patterns, optimal agent count formula, result collation, error handling, quality scoring |
| `references/knowledge-ingestion.md` | When processing user inputs (Phase 5) | File type detection, PDF/DOCX/XLSX/CSV/URL/Notion/code parsing, data normalization, metadata extraction, batch processing, error recovery |
| `references/gap-analysis-engine.md` | After ingestion, before research | Gap types (coverage, depth, cross-reference, recency, conflict, completeness), detection algorithm, priority matrix, topic completeness templates for 10 domains |
| `references/research-quality-assurance.md` | During Phase 4.5 QA | Source authority tiers (1-4), multi-pass verification pipeline, hallucination detection, citation tracking, quality scoring (0-50 scale), fact-checking checklist |
| `references/knowledge-graph-builder.md` | During Phase 3.5 graph building | 6 relationship types, detection algorithm, D3.js force-directed specs, cluster detection, graph metrics (centrality, orphans, bridges), export formats |
| `references/prompt-templates.md` | When crafting sub-agent prompts | 8 complete XML-structured prompts: file reader, web researcher, gap analyzer, synthesizer, categorizer, verifier, topic deep-diver, graph builder |
| `references/search-engine-reference.md` | When customizing or debugging the web app search | TF-IDF algorithm, field-weighted scoring, trigram fuzzy matching, inverted index structure, full search pipeline, performance characteristics |
| `references/domain-proptech.md` | When PropTech mode is triggered | PropTech market taxonomy, data sources (ATTOM, CoreLogic, Knight Frank), 4-pass research architecture, India deep-dive, PropTech confidence tiers, anti-patterns |
| `references/advanced-search-algorithms.md` | When implementing or tuning BM25F search | BM25F scoring with field weights, trigram fuzzy matching, faceted search, ranking pipeline, autocomplete trie, performance benchmarks |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/web-app-shell.html` | Production-grade interactive web app with TF-IDF search, D3 knowledge graph, analytics dashboard, faceted filtering, dark/light mode, responsive design (2,565 lines) |
| `templates/knowledge-entry.md` | JSON schema for knowledge entries with confidence decision tree, source attribution guide, tag taxonomy, 3 complete examples |
| `templates/research-synthesis.md` | Multi-agent research collation report template with quality metrics, conflict resolution log, before/after comparison |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/build_knowledge_app.py` | Assembles knowledge JSON into final HTML — validates entries, enriches metadata, generates graph data, calculates statistics, replaces template placeholders (593 lines) |

---

## Anti-Patterns & What NOT to Do

### 1. **Skipping Phase 3.5 (Knowledge Graph Building)**
- **Wrong**: "We'll build relationships after publishing"
- **Right**: Build graph before final QA (Phase 3.5 before Phase 4.5)
- **Why**: Relationships help detect gaps and contradictions

### 2. **Insufficient Phase 2**
- **Wrong**: 5-10 total sources for Phase 2
- **Right**: 25-50 sources (quick scan), extract 5-10 key themes
- **Why**: Premature depth misses important angles

### 3. **Trusting All Sources Equally**
- **Wrong**: Citing a random blog as authoritatively as academic paper
- **Right**: Tier sources, weight authority in final summary
- **Why**: Quality varies wildly; authority matters

### 4. **Not Verifying Statistics**
- **Wrong**: "The internet says 87%, so we'll use it"
- **Right**: Trace the stat to original source, verify methodology
- **Why**: Stats get distorted through re-citation chains

### 5. **Over-Parsing During Phase 3**
- **Wrong**: Creating 5 entries from one comprehensive source
- **Right**: 1-2 entries per source max
- **Why**: Dilutes signal, creates near-duplicates

### 6. **Ignoring Contradictions**
- **Wrong**: Keep only entry that agrees with your hypothesis
- **Right**: Document both sides with evidence chains
- **Why**: Bias ruins credibility; balanced coverage is better

### 7. **Phase 4.5 as Optional**
- **Wrong**: "QA can happen after publishing"
- **Right**: QA must gate entry into knowledge base
- **Why**: Low-quality entries undermine entire base

### 8. **Not Documenting Gaps**
- **Wrong**: Assume silence means topic is unimportant
- **Right**: Explicitly list what you didn't find
- **Why**: Gaps inform future research priorities

---

## Testing & Validation Guidance

**Before publishing your knowledge base**:

### Smoke Test (10 min)
- [ ] All entries have titles
- [ ] All entries have sources with URLs
- [ ] All URLs resolve (test 10 random)
- [ ] No duplicate entries
- [ ] Knowledge graph has <10% orphans
- [ ] QA pass rate ≥80%

### Content Test (30 min)
- [ ] Pick a random entry
- [ ] Read it fully
- [ ] Cross-check 3 claims in cited sources
- [ ] Verify the claim appears in cited source
- [ ] Repeat for 5 random entries
- [ ] If >1 claim fails: Return to Phase 4

### Relationship Test (15 min)
- [ ] Pick a random entry
- [ ] Follow "related entries" to 3 neighbors
- [ ] Do the relationships make sense?
- [ ] Can you navigate from topic A to topic B through related entries?
- [ ] Are isolated clusters obvious? (expected)
- [ ] Repeat for 3 different entries

### User Test (optional, 30 min)
- [ ] Ask a non-researcher to find 3 facts about the topic
- [ ] Can they find them easily?
- [ ] Do search results make sense?
- [ ] Do they encounter confusing contradictions?
- [ ] Do they get lost or find entry navigation intuitive?

### Confidence Calibration (15 min)
- [ ] Count HIGH, MEDIUM, LOW, UNKNOWN entries
- [ ] Are HIGH entries truly well-sourced?
- [ ] Are LOW entries marked clearly as uncertain?
- [ ] Does confidence level match quality?
- [ ] Adjust if miscalibrated

---

## Worked Example: "AI in Healthcare 2025"

**Topic**: How is AI transforming healthcare in 2025?

### Phase 1 Output: Query Plan
```
1. "AI healthcare 2025 applications"
2. "machine learning clinical diagnosis"
3. "AI drug discovery pipeline"
4. "healthcare AI regulatory challenges"
5. "AI hospital workflow efficiency"
6. "AI healthcare bias discrimination"
7. "medical imaging AI diagnostics"
8. "AI patient outcomes evidence"
```

### Phase 2 Output: Theme Map
```
Themes Identified:
1. Diagnostic AI (6 sources)
   - Medical imaging analysis
   - Lab result interpretation
2. Drug Discovery Acceleration (5 sources)
   - Molecule screening
   - Clinical trial design
3. Administrative Efficiency (7 sources)
   - Scheduling
   - Billing automation
   - Note generation
4. Regulatory & Safety (4 sources)
   - FDA approval process
   - AI safety standards
5. Bias & Equity (6 sources)
   - Racial bias in models
   - Access disparities
6. Controversy: Claims of superhuman performance vs. actual limitations
```

### Phase 3 Sample Entries
```
Entry 1: Medical Imaging AI Performance
Title: "Deep Learning in Radiology: Current Performance & Limitations"
Source: Nature Medicine, 2025
Key Claim: "AI matches radiologist performance on chest X-rays but fails on rare pathologies"
Authority: Tier 1 (peer-reviewed journal)
Confidence: HIGH (verified in 3+ studies)
Related to: Entry 5 (AI bias in radiology)

Entry 2: Pharma AI Cost Savings
Title: "AI Accelerates Drug Discovery: Cost Analysis 2025"
Source: McKinsey Healthcare Report
Key Claim: "AI can reduce early-stage discovery costs by 30-50%"
Authority: Tier 2 (reputable consulting)
Confidence: MEDIUM (estimates vary 20-60%)
Related to: Entry 8 (approval timeline)

Entry 3: AI Bias in Healthcare
Title: "Racial Disparities in Clinical Decision AI"
Source: JAMA Medicine, 2024
Key Claim: "Models trained on majority-white datasets show 20% higher error rates on Black patients"
Authority: Tier 1 (peer-reviewed)
Confidence: HIGH (replicated in multiple systems)
Related to: Entry 1 (limitations)
Conflict: Contradicts vendor claims of universal accuracy
```

### Phase 3.5 Graph Output
```json
{
  "nodes": [
    {"id": "entry-imaging", "title": "Medical Imaging AI", "category": "diagnostics", "connections": 5},
    {"id": "entry-bias", "title": "AI Bias in Diagnostics", "category": "equity", "connections": 4},
    {"id": "entry-drug", "title": "AI Drug Discovery", "category": "research", "connections": 3},
    {"id": "entry-admin", "title": "Administrative Efficiency", "category": "operations", "connections": 2},
    {"id": "entry-regulatory", "title": "FDA Approval Process", "category": "governance", "connections": 3}
  ],
  "edges": [
    {"source": "entry-imaging", "target": "entry-bias", "type": "dependency", "strength": 0.9},
    {"source": "entry-imaging", "target": "entry-regulatory", "type": "causal", "strength": 0.7},
    {"source": "entry-drug", "target": "entry-regulatory", "type": "hierarchical", "strength": 0.8}
  ]
}
```

### Phase 4 Evidence Chains
```
Claim: "AI matches radiologist performance on chest X-rays"
├─ Primary: Stanford study (2024) "AI in Radiology Benchmarking"
│  └─ Methodology: 1000 chest X-rays, blinded comparison
│  └─ Finding: AI 94% accuracy, radiologists 92%
├─ Secondary: Nature Medicine editorial citing Stanford
└─ Derivative: News article on AI "beating" doctors (oversimplified)

Confidence: HIGH (primary source strong, methodology sound)
But Note: Study used selected X-rays, not all presentations
```

### Phase 4.5 QA Scores
```
Entry: Medical Imaging AI
- Accuracy: 9/10 ✓
- Completeness: 7/10 (misses ophthalmology imaging)
- Depth: 8/10 ✓
- Recency: 9/10 ✓
- Consistency: 8/10 ✓
TOTAL: 41/50 ✓ PASS

Entry: "AI Replaces Doctors Soon" (hypothetical)
- Accuracy: 3/10 ✗ (contradicts evidence)
- Completeness: 4/10
- Depth: 2/10
- Recency: 5/10
- Consistency: 1/10 ✗ (conflicts heavily with entries)
TOTAL: 15/50 ✗ FAIL — DO NOT INCLUDE
```

### Phase 5 Ingestion Report
```
HEALTHCARE AI KNOWLEDGE BASE
Total Entries: 34
Pass Rate: 88%
Source Tiers: Tier 1 (62%), Tier 2 (28%), Tier 3 (10%)

Categories:
- Diagnostics (12 entries)
- Research (8 entries)
- Operations (7 entries)
- Governance (5 entries)
- Equity (6 entries)

Confidence: HIGH (22), MEDIUM (8), LOW (4)
```

### Phase 6 Visualization
- D3 graph showing 34 nodes
- Clusters: Diagnostics (hub, 8 connections), Equity (6 connections), Research (isolated, 3 connections)
- Search: Full-text on titles + summaries
- Export: SVG graph, bibliography (CSV)

---

## Domain Detection: PropTech Mode

When the skill detects PropTech-related queries, it automatically switches to a specialized research pipeline with deeper research, better prompts, and a PropTech-specific UI.

**→ Read `references/domain-proptech.md` for the complete PropTech domain profile**
**→ Read `references/advanced-search-algorithms.md` for BM25F search implementation**
**→ Use `templates/proptech-web-app-shell.html` instead of the generic web app template**

### Trigger Detection

The skill enters PropTech mode when the query contains ANY of these signals:

**Keywords:** proptech, property tech, real estate tech, realty, mortgage, lending, property management, smart building, construction tech, contech, property valuation, AVM, appraisal, listing platform, MLS, brokerage, RERA, real estate regulatory, tenant management, facility management, co-living, co-working, fractional ownership, REIT

**Company Names:** Zillow, Opendoor, Compass, Redfin, NoBroker, Housing.com, Square Yards, 99acres, Rightmove, Zoopla, Matterport, CoStar, Reonomy, Side, Divvy Homes, Bilt Rewards, ServiceTitan

**Phrases:** "property data", "real estate market", "housing market", "rental market", "commercial real estate", "CRE", "residential real estate", "smart home", "digital twin building", "real estate investment"

### What Changes in PropTech Mode

| Aspect | Generic Mode | PropTech Mode |
|--------|-------------|---------------|
| **Research depth** | 3-pass (breadth → depth → verify) | 4-pass (landscape → segment deep-dive → verify → competitive intel) |
| **Sub-agent count** | 3-15 based on scope | 8-25+ (more agents for market segmentation) |
| **Data sources** | General web search | PropTech-specific: ATTOM, CoreLogic, Knight Frank, CREDAI, PropTech List |
| **Confidence tiers** | Generic 4-tier | PropTech 5-tier with industry-specific authority rules |
| **Web app template** | `web-app-shell.html` | `proptech-web-app-shell.html` — map views, property cards, market filters |
| **Search algorithm** | TF-IDF | BM25F with PropTech field weights (property_type=3.0, market_segment=2.5) |
| **UI/UX** | Generic knowledge cards | PropTech cards with property type icons, region flags, stage badges |
| **Facets** | Category, confidence, tags | + Property type, market segment, region, authority tier, company stage |
| **Visualization** | D3 graph only | D3 graph + Leaflet map with regional markers |

### PropTech Sub-Agent Dispatch (Enhanced)

PropTech research uses a 4-pass architecture instead of the standard 3-pass:

```
PASS 1: LANDSCAPE (8 agents)
├── Agent 1: Market size + growth data (2025-2030 projections)
├── Agent 2: Key players by segment (FinTech, Marketplace, Management, etc.)
├── Agent 3: Recent funding rounds + M&A (last 12 months)
├── Agent 4: Technology trends (AI, digital twins, IoT)
├── Agent 5: Regulatory updates (RERA, RBI, HUD, TCPA)
├── Agent 6: India market specifics (NoBroker, Housing.com, RERA landscape)
├── Agent 7: US/UK market comparison
└── Agent 8: Customer/user insights + adoption patterns

PASS 2: SEGMENT DEEP-DIVE (10-15 agents)
├── One agent per market segment (FinTech, Marketplace, Management, SmartBuilding, ConTech, Data, ESG, InsurTech)
├── Each uses segment-specific data sources and query templates
└── Follows evidence chains to primary sources (Tier 1-2 only)

PASS 3: VERIFICATION + COMPETITIVE INTELLIGENCE (5 agents)
├── Agent V1: Verify market size claims (cross-reference 3+ sources)
├── Agent V2: Validate company funding/valuation claims
├── Agent V3: Fact-check regulatory claims (RERA, RBI)
├── Agent V4: Cross-reference India-specific data
└── Agent V5: Competitive positioning accuracy

PASS 4: SYNTHESIS + GAP FILL (3 agents)
├── Agent S1: Merge all passes into unified knowledge base
├── Agent S2: Generate comparative analysis (India vs US vs UK)
└── Agent S3: Identify remaining gaps, generate follow-up research plan
```

### PropTech Research Quality Bar

PropTech research has a HIGHER quality bar than generic research:
- **Minimum source authority:** Tier 2+ for market sizing claims
- **Cross-reference requirement:** Key claims must appear in 3+ independent sources (not 2)
- **Recency requirement:** Market data must be from 2024+ (PropTech moves fast)
- **Geographic specificity:** Must distinguish US vs India vs UK market data
- **Regulatory accuracy:** RERA/RBI claims must cite specific regulations or official sources

---

## FAQ & Troubleshooting

**Q: How many sources should Phase 2 scan?**
A: 25-50 minimum. Each source gets 5-10 seconds of attention. Goal is theme identification, not depth.

**Q: What if a topic has conflicting expert opinions?**
A: Document both. Include entries from both sides with evidence chains. Note in QA which has stronger authority.

**Q: Can I skip Phase 3.5 (Knowledge Graph)?**
A: Technically yes, but DON'T. Graph building catches gaps and contradictions you'll miss otherwise. Do Phase 3.5 at minimum at condensed form (10 min).

**Q: How do I know when Phase 3 research is "done"?**
A: When you're seeing repeated findings across new sources (diminishing returns) AND knowledge graph is >80% connected (low orphan rate).

**Q: What's the difference between MEDIUM and LOW confidence?**
A: MEDIUM = multiple sources agree but some weakness (old data, limited scope, moderate authority). LOW = conflicting sources or single weak source.

**Q: Can I publish before Phase 4.5 QA?**
A: No. QA gates publication. Publishing without QA will undermine credibility as bad entries surface.

**Q: How do I handle paywalled sources?**
A: Try WebFetch tool (sometimes works even for paywalled content). If not accessible, mark as UNKNOWN. Never guess content.

---

## Version History

**v2.5** (Feb 2026)
- **PropTech Domain Mode**: Auto-detects PropTech/real-estate queries and switches to specialized pipeline
- **BM25F Search Algorithm**: Replaces basic TF-IDF with field-weighted scoring, trigram fuzzy matching
- **PropTech Web App Template**: Leaflet.js map views, property cards, market segment filters
- **5 PropTech Sub-Agent Templates**: Market Researcher, Regulatory Analyst, Tech Stack Analyst, India Specialist, Competitive Intelligence
- **Advanced Search Algorithms Reference**: Complete client-side search engine with autocomplete, facets, performance benchmarks
- **PropTech Domain Profile**: Market taxonomy, data sources, 4-pass research architecture, India deep-dive

**v2.0** (Feb 2026)
- Added Phase 3.5: Knowledge Graph Building
- Added Phase 4.5: Research Quality Assurance
- Enhanced failure recovery for all phases
- Worked example: "AI in Healthcare"
- Sub-agent scaling formulas
- Reference file reorganization

**v1.0** (2025)
- Initial 6-phase framework
- Basic quality checks
- Simple entry structure

---

## Contributing & Feedback

Found an issue? Have a better pattern? Questions about phases?
- Open an issue with phase + problem
- Propose pattern improvements with before/after examples
- Share metrics from your own research runs

---

**Last Updated**: 2026-02-09
**Maintainer**: Research Quality Team
**Status**: Production - Use with confidence
