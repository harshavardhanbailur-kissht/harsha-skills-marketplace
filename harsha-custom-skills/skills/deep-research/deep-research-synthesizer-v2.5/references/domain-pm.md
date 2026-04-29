# Product Management Domain Lens

**Version:** 1.0
**Last Updated:** 2026-03-25
**Scope:** PM-specific research framing, dimensions, query enrichment, and webapp views
**Activation:** User explicitly requests PM lens — never auto-detected

---

## Section 1: Activation & Philosophy

### When This Lens Activates

The PM lens activates ONLY when the user explicitly requests it:
- "use PM lens", "PM mode", "through a PM perspective"
- "I want to study this as a PM", "product management angle"
- "help me understand this for my PM work"

It does NOT auto-detect. This is intentional — the same topic (e.g., "AI in healthcare") yields very different research through a general lens vs. PM lens, and only the user knows which they want.

### What the PM Lens Does

The PM lens is an **overlay**, not a replacement. The standard 6+2 phase pipeline runs exactly as before. The PM lens modifies what happens WITHIN each phase:

| Phase | Standard Behavior | PM Lens Addition |
|-------|------------------|------------------|
| Phase 1 (Planning) | Decompose into sub-questions | Add 10 PM dimension queries |
| Phase 2 (Breadth) | Tag themes | Tag entries with PM dimensions |
| Phase 3 (Depth) | Extract knowledge entries | Add PM metadata fields per entry |
| Phase 3.5 (Graph) | Build relationships | Add PM relationship types |
| Phase 4 (Verify) | Trace evidence chains | Prioritize market data verification |
| Phase 4.5 (QA) | Score 0-50 | Add "PM Actionability" score |
| Phase 5 (Assemble) | Deduplicate, normalize | Generate PM Executive Summary |
| Phase 6 (Webapp) | Knowledge graph + search | Add PM Dashboard view |

### What the PM Lens Does NOT Do

- Does not replace the generic pipeline
- Does not lower quality standards
- Does not auto-trigger on keywords
- Does not use a separate template (uses the generic template with PM view injection)
- Does not require different sub-agent architecture

---

## Section 2: The 10 PM Research Dimensions

Every knowledge entry gets tagged with which PM dimension(s) it serves. These are the dimensions a PM cares about when studying ANY topic:

### Dimension 1: Opportunity Landscape
**Question**: Where are the customer pain points and unmet needs?
**What to research**: Customer struggles, satisfaction gaps, workflow friction, Jobs-to-be-Done
**PM Framework**: Opportunity-Solution Tree (Teresa Torres), Opportunity Scoring = Importance x (1 - Satisfaction)
**Query enrichment**: Add "[topic] customer pain points", "[topic] user frustrations", "[topic] unmet needs"

### Dimension 2: Competitive Positioning
**Question**: Who else is solving this? What's the white space?
**What to research**: Direct competitors (5+), competitor strengths/weaknesses, feature gaps, switching costs, moats
**PM Framework**: Competitive Landscape Map, Feature Parity Matrix
**Query enrichment**: Add "[topic] competitors", "[topic] market leaders", "[topic] startup landscape"

### Dimension 3: Market Size & Addressability
**Question**: How big is this opportunity? What can we realistically capture?
**What to research**: TAM/SAM/SOM, growth drivers, market growth rate, analyst reports
**PM Framework**: Top-Down + Bottom-Up Market Estimation
**Query enrichment**: Add "[topic] market size", "[topic] TAM", "[topic] market growth forecast"

### Dimension 4: Customer Segments & Value
**Question**: WHO specifically has this problem, and what's the value to each segment?
**What to research**: Target segments by problem (not demographics), segment-specific needs, value propositions per segment
**PM Framework**: Segment-Problem-Solution mapping, Value Proposition Canvas
**Query enrichment**: Add "[topic] customer segments", "[topic] buyer personas", "[topic] use cases by industry"

### Dimension 5: Metrics & Measurement
**Question**: If we build this, how do we know it's working?
**What to research**: North Star Metric candidates, industry KPIs, benchmark data, leading vs lagging indicators
**PM Framework**: North Star Framework (Amplitude), HEART metrics (Google), Pirate Metrics (AARRR)
**Query enrichment**: Add "[topic] success metrics", "[topic] KPIs", "[topic] industry benchmarks"

### Dimension 6: Go-to-Market Strategy
**Question**: How do customers discover and adopt solutions in this space?
**What to research**: Distribution channels, sales motions, adoption patterns, pricing models, buyer journey
**PM Framework**: GTM Motion Selection (PLG, Sales-led, Community-led)
**Query enrichment**: Add "[topic] go to market", "[topic] adoption pattern", "[topic] distribution channels"

### Dimension 7: Solution Patterns
**Question**: What's been built already? What approaches work?
**What to research**: Existing solutions, UX patterns, technology approaches, build-vs-buy, MVP patterns
**PM Framework**: Solution Space mapping, Build-Buy-Partner matrix
**Query enrichment**: Add "[topic] solutions", "[topic] product features", "[topic] UX patterns"

### Dimension 8: Validation & Experimentation
**Question**: What are the riskiest assumptions? How do we test them cheaply?
**What to research**: Common failure modes, assumption patterns, experiment designs, case studies of failures
**PM Framework**: Assumption Mapping (Value/Usability/Viability/Feasibility), Pretotype Design
**Query enrichment**: Add "[topic] failed startups", "[topic] lessons learned", "[topic] critical assumptions"

### Dimension 9: Business Model & Unit Economics
**Question**: Can you make money at this? What does the business model look like?
**What to research**: Pricing models, revenue streams, CAC/LTV data, margins, competitor pricing
**PM Framework**: Business Model Canvas, Unit Economics, LTV:CAC ratio
**Query enrichment**: Add "[topic] pricing", "[topic] business model", "[topic] unit economics", "[topic] revenue model"

### Dimension 10: Strategic Context & Constraints
**Question**: What regulatory, technical, or organizational factors constrain this space?
**What to research**: Regulatory landscape, compliance requirements, technical debt, partnership dependencies, adjacencies
**PM Framework**: PESTLE Analysis, Dependency Mapping
**Query enrichment**: Add "[topic] regulations", "[topic] compliance", "[topic] risks", "[topic] dependencies"

---

## Section 3: Phase-by-Phase PM Lens Behavior

### Phase 1 PM Enhancement: Query Planning

For each of the 10 PM dimensions, generate 1-2 additional queries beyond the standard decomposition. This means a PM lens research typically has 15-25 queries vs the standard 5-10.

**Example**: Topic = "AI in Healthcare"
Standard queries (5-10): diagnostic AI, drug discovery AI, hospital efficiency, regulatory challenges...
PM-added queries (10-15):
- Opportunity: "healthcare AI unmet needs clinicians", "doctor frustrations with current diagnostic tools"
- Competitive: "healthcare AI startups funding 2025", "healthcare AI market leaders"
- Market: "healthcare AI market size TAM 2025-2030", "clinical AI addressable market"
- Segments: "healthcare AI buyer personas hospital vs clinic vs pharma"
- Metrics: "healthcare AI success metrics adoption rate", "clinical AI KPIs"
- GTM: "healthcare AI sales motion enterprise vs PLG", "medical device go to market"
- Solutions: "healthcare AI product features comparison", "clinical decision support UX"
- Validation: "healthcare AI failed startups lessons", "clinical AI adoption barriers"
- Business: "healthcare AI pricing SaaS per bed per clinician", "medical AI revenue models"
- Strategic: "FDA AI medical device regulations 2025", "healthcare AI partnership landscape"

### Phase 2 PM Enhancement: Breadth Tagging

During breadth scan, tag each discovered source/theme with PM dimensions:
```
Theme: "Diagnostic AI Performance" → PM Dimensions: [Opportunity, Solution Patterns, Metrics]
Theme: "FDA Approval Process" → PM Dimensions: [Strategic Context, Validation]
Theme: "AI Startup Landscape" → PM Dimensions: [Competitive Positioning, Market Size]
```

After Phase 2, generate a **PM Dimension Coverage Matrix**:
```
PM DIMENSION COVERAGE (after breadth scan):
- Opportunity Landscape:    ████████░░ (8 sources)  ✓ Good
- Competitive Positioning:  ██████░░░░ (6 sources)  ✓ Good
- Market Size:              ████░░░░░░ (4 sources)  ⚠ Needs depth
- Customer Segments:        ███░░░░░░░ (3 sources)  ⚠ Needs depth
- Metrics:                  ██░░░░░░░░ (2 sources)  ✗ Gap — add queries
- GTM Strategy:             █░░░░░░░░░ (1 source)   ✗ Gap — add queries
- Solution Patterns:        ██████░░░░ (6 sources)  ✓ Good
- Validation:               ██░░░░░░░░ (2 sources)  ✗ Gap — add queries
- Business Model:           ███░░░░░░░ (3 sources)  ⚠ Needs depth
- Strategic Context:        █████░░░░░ (5 sources)  ✓ Good
```

If any dimension has <3 sources, add targeted queries before proceeding to Phase 3.

### Phase 3 PM Enhancement: Entry Metadata

Each knowledge entry gets additional PM metadata fields:

```json
{
  "id": "entry-fda-approval",
  "title": "FDA AI Medical Device Approval Process",
  "category": "governance",
  "content": "...",
  "confidence": "HIGH",
  "source": "FDA.gov",

  "pm_dimensions": ["strategic_context", "validation"],
  "pm_actionability": "HIGH",
  "pm_decision_relevance": "Build vs. regulatory risk — affects timeline by 12-18 months",
  "pm_so_what": "If building clinical AI, budget 18 months and $500K+ for FDA clearance. Consider 510(k) pathway for faster approval.",
  "pm_who_cares": ["VP Engineering", "Head of Regulatory", "CEO"],
  "pm_timeframe": "18-24 months (regulatory timeline)"
}
```

**PM-specific fields explained**:
- `pm_dimensions`: Which of the 10 dimensions this entry serves (array, 1-3 values)
- `pm_actionability`: HIGH (directly changes a decision), MEDIUM (informs strategy), LOW (background context)
- `pm_decision_relevance`: One sentence explaining what PM decision this informs
- `pm_so_what`: The "so what?" synthesis — what should a PM DO with this information
- `pm_who_cares`: Which stakeholders need this information
- `pm_timeframe`: When is this relevant? (immediate, 3-6 months, 12+ months)

### Phase 3.5 PM Enhancement: PM Relationship Types

In addition to the standard 6 relationship types (Semantic, Hierarchical, Causal, Temporal, Comparative, Dependency), the PM lens adds:

- **Competes-with**: Two solutions/companies competing for same customer segment
- **Enables**: One entry enables another (e.g., "regulatory approval" enables "market entry")
- **Monetizes**: Business model connects to customer segment/solution
- **Validates**: One entry provides evidence for/against an assumption in another entry
- **Blocks**: One entry represents a blocker for another (e.g., "FDA regulation" blocks "clinical deployment")

### Phase 4.5 PM Enhancement: Actionability Scoring

In addition to the standard 5-dimension QA score (0-50), PM lens adds a 6th dimension:

**PM Actionability (0-10)**:
- 10: Directly changes a build/ship/kill decision with specific numbers
- 8-9: Strongly informs strategy with concrete data points
- 6-7: Useful context that shapes thinking
- 4-5: Background information, nice to know
- 2-3: Tangentially relevant
- 0-1: Not actionable for PM work

Entries with PM Actionability <4 are deprioritized (not removed) in the PM Dashboard view.

### Phase 5 PM Enhancement: Executive Summary

After assembly, automatically generate a PM Executive Summary:

```
PM EXECUTIVE SUMMARY: [Topic]
Generated: [Date]

THE OPPORTUNITY
[2-3 sentences from Dimension 1 entries, highest confidence]

THE MARKET
[TAM/SAM/SOM from Dimension 3, with confidence level]

THE COMPETITION
[Top 3-5 competitors from Dimension 2, one line each]

THE CUSTOMER
[Primary segments from Dimension 4]

WHAT SUCCESS LOOKS LIKE
[North Star metric candidate from Dimension 5]

HOW TO GET THERE
[GTM motion from Dimension 6, pricing from Dimension 9]

BIGGEST RISKS
[Top 3 from Dimensions 8 + 10]

RECOMMENDED NEXT STEPS
[3-5 actionable items derived from highest-actionability entries]
```

### Phase 6 PM Enhancement: PM Dashboard View

The webapp gets an additional view mode (alongside Explore Mode and Learning Path):

**PM Dashboard View** — organized by the 10 dimensions:
- Each dimension is a card/section
- Entries within each dimension sorted by PM Actionability (highest first)
- Color coding: GREEN (well-researched, 5+ entries), YELLOW (moderate, 2-4), RED (gap, 0-1)
- PM Executive Summary at the top
- "Decision Board" showing entries with HIGH pm_actionability
- Stakeholder filter: filter by pm_who_cares to see what matters to specific roles

---

## Section 4: PM-Specific Sub-Agent Query Templates

When PM lens is active, sub-agents get PM-enriched prompts. Each sub-agent receives one additional instruction block:

```
PM LENS ACTIVE — In addition to standard research:
1. For every key finding, assess: "So what? What would a PM DO with this?"
2. Tag each finding with PM dimensions: [opportunity, competitive, market_size, segments, metrics, gtm, solutions, validation, business_model, strategic_context]
3. Note stakeholders who would care about this finding
4. Rate actionability: HIGH (changes a decision), MEDIUM (informs strategy), LOW (background)
5. If you find market size data, pricing data, or competitor data — these are HIGH priority, extract precisely
```

This is a lightweight addition (~100 tokens) that doesn't change the sub-agent's research behavior, just enriches its output tagging.

---

## Section 5: PM Lens Quality Bar

PM lens research has specific quality expectations beyond generic:

- **Market sizing claims**: Must have 2+ independent sources, must specify methodology (top-down or bottom-up), must include year and geographic scope
- **Competitor claims**: Must be from 2024+ sources (competitive landscape changes fast)
- **Pricing/revenue claims**: Must specify currency, geography, and whether it's public data or estimates
- **Regulatory claims**: Must cite specific regulation, agency, or official guidance
- **Customer segment claims**: Must be based on research data, not assumptions

---

## Section 6: PM Dimension Coverage Targets

A well-researched PM knowledge base should have:

| Dimension | Minimum Entries | Target Entries | Critical? |
|-----------|----------------|----------------|-----------|
| Opportunity Landscape | 3 | 5-8 | YES — without this, no problem-solution fit |
| Competitive Positioning | 3 | 5-10 | YES — without this, can't differentiate |
| Market Size | 2 | 3-5 | YES — without this, can't prioritize |
| Customer Segments | 2 | 4-6 | YES — without this, building for nobody |
| Metrics & Measurement | 1 | 3-5 | No — can be derived later |
| GTM Strategy | 1 | 3-5 | No — can be derived later |
| Solution Patterns | 2 | 4-8 | No — but helps avoid reinventing |
| Validation & Experimentation | 1 | 2-4 | No — but prevents costly mistakes |
| Business Model | 2 | 3-5 | YES — without this, no viability |
| Strategic Context | 2 | 3-5 | Depends on domain (high for regulated) |

If any "Critical" dimension has <minimum entries after Phase 3, trigger additional queries before proceeding.

---

## Section 7: Worked Example — "AI in Healthcare" Through PM Lens

### Standard Research Output (no PM lens):
```
Entries: 34
Categories: Diagnostics (12), Research (8), Operations (7), Governance (5), Equity (6)
Focus: What AI can do, how it works, where it's applied, what the risks are
```

### PM Lens Research Output (same topic):
```
Entries: 48 (+14 PM-specific entries from enriched queries)
Categories: Same as above PLUS PM overlay
PM Dimensions:
  - Opportunity: 6 entries (clinician pain points, workflow gaps, patient experience)
  - Competitive: 8 entries (23andMe, Tempus, PathAI, Viz.ai, Aidoc positions)
  - Market Size: 4 entries (clinical AI TAM $45B by 2030, diagnostic AI SAM $12B)
  - Segments: 5 entries (radiologists, pathologists, hospital systems, pharma, patients)
  - Metrics: 3 entries (diagnostic accuracy, time-to-diagnosis, adoption rate)
  - GTM: 3 entries (enterprise sales, FDA pathway, academic partnership)
  - Solutions: 6 entries (existing products, UX patterns, integration approaches)
  - Validation: 3 entries (failed clinical AI startups, adoption barriers)
  - Business: 4 entries (per-read pricing, SaaS models, payer reimbursement)
  - Strategic: 6 entries (FDA SaMD, HIPAA, EU MDR, partnership requirements)

PM Executive Summary:
  THE OPPORTUNITY: Radiologists face 20-30% workload increase annually with no proportional
  staffing increase. AI-assisted triage can reduce time-to-diagnosis by 40-60%.

  THE MARKET: TAM $45B (global clinical AI), SAM $12B (diagnostic imaging AI),
  SOM $800M-1.2B (English-speaking hospitals, radiology focus). HIGH confidence.

  THE COMPETITION: Viz.ai (stroke, $100M raised), Aidoc (triage, $250M raised),
  PathAI (pathology, $325M raised). White space: primary care AI triage.

  BIGGEST RISKS: FDA 510(k) timeline (18 months), HIPAA compliance cost ($200K+),
  physician trust barrier (only 34% of doctors trust AI recommendations).

  NEXT STEPS:
  1. Interview 10 radiologists about triage pain points (Dimension 1 validation)
  2. Map competitive feature matrix for top 5 players (Dimension 2 depth)
  3. Identify fastest FDA pathway for MVP scope (Dimension 10 de-risking)
```

---

**Last Updated**: 2026-03-25
**Status**: Production
