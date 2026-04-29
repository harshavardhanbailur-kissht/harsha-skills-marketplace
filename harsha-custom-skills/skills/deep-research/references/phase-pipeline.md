# Phase Pipeline Reference

Detailed specifications for each phase of the Deep Research Synthesizer pipeline. The orchestrating SKILL.md stays lean and points here for the per-phase mechanics, examples, metrics, and failure-recovery paths.

**When to read this file**: While operating any phase. Each phase below is self-contained — you can jump directly to the section you need.

**Pipeline at a glance** (standard entry):

```
Phase 1 → 2 → 3 → 3.5 → 4 → 4.5 → 5 → 6
plan   breadth depth graph deep  QA  ingest  visualize
```

Visualization-only entry skips Phases 1–4 and starts at Phase 3.5 with pre-researched data.

---

## Phase 1: Research Planning & Query Synthesis (15-30 min)

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

## Phase 2: Breadth Search (30-60 min)

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

## Phase 3: Depth Research (60-180 min)

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

## Phase 3.5: Knowledge Graph Building (30-60 min)

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
- Avg connections per entry: 3-7 (primary metric — use this to assess graph quality)
- Graph density: Varies by KB size. For 30-50 entries target 0.08-0.20; for 100+ entries target 0.03-0.10. (Density = edges / (n*(n-1)/2). Density drops naturally as KB grows because not everything connects.)
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

## Phase 3.5 Enhancement: Learning Mode

When the user's intent signals **learning** (not just research), activate learning mode to reorder and reframe the output for progressive understanding.

**Learning mode activation** (detect ANY of these in user query):
- Keywords: "understand", "learn", "study", "help me grasp", "explain", "how does X work", "teach me", "guide me through", "walk me through", "I want to know about", "deep dive into", "master"
- Phrasing: Questions starting with "What is...", "How do...", "Why does..."

**Research mode (default, no reordering)** — detect these instead:
- Keywords: "research", "analyze", "compare", "investigate", "find out about", "what's the state of", "landscape", "competitive analysis"

**When learning mode is active, Phase 3.5 adds these steps**:

1. **Topological sort** on dependency edges to determine prerequisite ordering
2. **Assign learning tiers** (Foundation / Intermediate / Advanced) based on dependency in-degree
3. **Detect PM topic** — if PM keywords found in query or entries, apply PM context framing
4. **Reorder assembly output** to follow dependency chain (foundations first, advanced last)
5. **Apply progressive difficulty framing** — accessible language for foundations, technical precision for advanced

→ **Full algorithm details**: See `references/knowledge-graph-builder.md` → "Learning Mode: Dependency-Ordered Output"

**PM-topic detection keywords**: product management, sprint, OKR, roadmap, discovery, prioritization, stakeholder, user story, A/B test, funnel, retention, JTBD, backlog, MVP, PLG, north star metric, agile, scrum, kanban, user research, persona, PMF, churn, PRD

**When PM topic detected, each entry gets additional framing**:
- "How This Applies in PM Work" section
- "When to Use This" / "When NOT to Use This" guidance
- "Real-World PM Scenario" example
- Cross-references to related PM frameworks

**Impact on Phase 6 (Assembly)**:
- Webapp sidebar follows dependency order (not alphabetical)
- Learning tier badges (Foundation / Intermediate / Advanced) on each entry
- "Learning Path" view toggle alongside "Explore Mode" (knowledge graph)
- Learning Path shows linear progression with connecting arrows between prerequisites

**Important**: Learning mode is ADDITIVE. Standard research mode works exactly as before. Learning mode only activates when learning intent is detected, and only adds reordering + framing on top of the existing pipeline.

---

## Phase 4: Source Deep-Dive (60-120 min)

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

## Phase 4.5: Research Quality Assurance (30-60 min)

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

## Phase 5: Knowledge Base Assembly & Ingestion (30-60 min)

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

## Phase 6: Knowledge Graph Visualization & Discovery (20-60 min)

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

## Cross-Phase Tips

- **Don't run phases strictly serially when possible.** Phases 2 and 3 can interleave with sub-agents (see `references/sub-agent-orchestration.md`).
- **Don't skip Phase 3.5.** Even at condensed 10-min form, the graph catches gaps and contradictions you'd otherwise miss.
- **Don't publish before Phase 4.5.** QA gates publication; bad entries surface and undermine credibility.
- **Phase 4 and Phase 4.5 are different.** Phase 4 traces individual claims; Phase 4.5 scores whole entries and the corpus.

For a fully worked example flowing through every phase, see `worked-example-ai-healthcare.md`.
