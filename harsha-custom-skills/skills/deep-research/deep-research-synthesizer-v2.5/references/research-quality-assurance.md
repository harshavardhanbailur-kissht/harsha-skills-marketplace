# Research Quality Assurance

**Purpose**: Ensure research outputs are trustworthy, fact-checked, and ready for publication.
**Usage**: Implement in Phase 4.5 of the Deep Research Synthesizer pipeline.
**Last Updated**: 2026-02-09

---

## Table of Contents

1. Source Evaluation Framework
2. Multi-Pass Research Pipeline
3. Hallucination Detection
4. Citation Tracking
5. Quality Scoring
6. Fact-Checking Checklist
7. Confidence Level Definitions
8. Common Pitfalls & Fixes

---

## Source Evaluation Framework

### Authority Scoring

Not all sources are created equal. Build trust through authority tiers.

#### Tier 1: PRIMARY SOURCES (Highest Authority)
These are the original sources of knowledge:
- **Academic peer-reviewed journals**: Nature, Science, JAMA, The Lancet, etc.
  - Score: 10/10 (gold standard)
  - Trust indicator: Peer-reviewed, methodology disclosed, data available
- **Government official data**: .gov websites, census data, regulatory filings (SEC, FDA)
  - Score: 10/10 if official (.gov/.edu domains)
  - Trust indicator: Official seal, data download options, version control
- **Primary research reports**: Original studies, pilot programs, surveys conducted by researchers
  - Score: 10/10 if methodology sound
  - Trust indicator: Full methodology, sample size, statistical significance disclosed
- **Official organization reports**: Reports from UN, WHO, World Bank, major NGOs
  - Score: 9/10 (highly credible but sometimes advocacy-driven)
  - Trust indicator: Data sources disclosed, multiple countries/years

**How to identify Tier 1**:
- Domain ends in `.edu` or `.gov`
- Peer-review symbol visible
- Full citation information provided
- Authors have institutional affiliations
- Methodology section present
- Data/findings openly available

#### Tier 2: REPUTABLE SECONDARY SOURCES (High Authority)
Credible organizations that synthesize and report on primary sources:
- **Established news organizations**: BBC, Reuters, AP, NPR, The Guardian, Financial Times
  - Score: 8-9/10
  - Trust indicator: Bylined reporting, multiple sources quoted, editorial standards visible
- **Domain-specific publications**: Medical journals (Nature Medicine), tech publications (MIT Tech Review, ACM Queue)
  - Score: 8-9/10
  - Trust indicator: Editorial board visible, author credentials clear
- **Non-profit research organizations**: McKinsey, Brookings Institution, Stanford Internet Observatory
  - Score: 8/10
  - Trust indicator: Research methodology disclosed, no obvious political bias
- **Industry-leading tech companies**: Research from Microsoft, Google, OpenAI published reports
  - Score: 7-8/10 (may have business incentive bias)
  - Trust indicator: Peer review encouraged, code/data released, limitations disclosed
- **Trade publications**: Harvard Business Review, Healthcare Dive, Energy Industry Insight
  - Score: 7-8/10
  - Trust indicator: Subject matter experts as authors, editorial review

**How to identify Tier 2**:
- Organization has established reputation (>5 years active)
- Editorial board or peer review process exists
- Authors have credentials/titles
- Retractions/corrections policy visible
- Citation of primary sources throughout

#### Tier 3: COMMUNITY & EXPERT COMMENTARY (Medium Authority)
Individual experts and specialized communities:
- **Academic blogs/Medium posts by credentialed experts**: Professor blog, PhD researcher's writeup
  - Score: 6-7/10
  - Trust indicator: Author credentials listed, sources cited, disclosure of potential bias
- **Forum discussions**: Reddit threads with expert participation, Stack Overflow answers with high votes
  - Score: 5-6/10
  - Trust indicator: Credentialed responders visible, citations/links to sources
- **Conference talks/presentations**: Slides from reputable conferences, webinar recordings
  - Score: 6-7/10
  - Trust indicator: Known speaker, reputable event, recording available
- **Technical documentation**: Open-source projects, company technical blogs
  - Score: 7/10 for technical accuracy, lower for business claims
  - Trust indicator: Code included, examples reproducible

**How to identify Tier 3**:
- Author has relevant expertise (visible in bio/credentials)
- First-person or direct experience claimed
- Other sources cited but not comprehensive
- No formal editorial process, but author integrity clear
- Community engagement (comments, discussion)

#### Tier 4: UNVERIFIED SOURCES (Low Authority)
Use cautiously, verify before trusting:
- **Random blogs**: Unsourced blog posts, medium posts by unknowns
  - Score: 2-3/10
  - Trust indicator: Only use if no better source exists, treat as opinion not fact
- **Social media posts**: Twitter threads, LinkedIn posts, YouTube videos
  - Score: 1-3/10
  - Trust indicator: Verify claims independently, treat as signal not confirmation
- **Paid sponsorships/advertorials**: Content marked as "sponsored" or "in partnership"
  - Score: 1/10 (biased by definition)
  - Trust indicator: Assume bias, verify facts independently
- **Uncited claims**: Statements without source attribution
  - Score: 0-1/10
  - Trust indicator: Do not use unless claim is verified elsewhere

**How to identify Tier 4**:
- No author name or bio
- No citations or sources
- Sensational language, clickbait title
- Contradicts multiple Tier 1-2 sources
- Domain registration anonymous or very new

---

### Recency Scoring

Information becomes stale at different rates depending on domain:

**Fresh (≤6 months old)**: PREFERRED
- Technology: Essential (moves fast)
- Medicine: Highly valuable (new treatments emerging)
- Economics: Very valuable (markets change)
- Culture: Valuable (trends shift)
- Score boost: +1 to quality score

**Current (6-24 months old)**: ACCEPTABLE
- Technology: Acceptable only if still relevant
- Medicine: Acceptable for background context
- Economics: Acceptable if structural findings (not market prices)
- Evergreen topics: Fully acceptable (history, foundational concepts)
- Score boost: +0.5

**Aging (2-5 years old)**: LIMITED USE
- Only cite if no newer source available
- Use for historical context or foundational knowledge
- Note the age clearly in entry
- Score penalty: -0.5

**Outdated (>5 years old)**: RARELY USE
- Technology: Almost never use (obsolete)
- Medicine: Avoid unless discussing historical evolution
- Evergreen topics: OK if foundational (e.g., "history of the internet")
- Social trends: Outdated, risky to cite
- Score penalty: -1.0

**How to check recency**:
1. Publication date on article (obvious check)
2. Check "last updated" on institutional sites
3. For reports: Check if new version released
4. For studies: Check if replicated or contradicted since publication
5. For statistics: Check if collection date older than publication

**Example Assessment**:
- "COVID-19 vaccine efficacy: 94% (Nature Medicine, Feb 2025)" → FRESH ✓
- "Economic recovery: GDP +2.3% (2023 report, published 2024)" → CURRENT ✓
- "AI adoption in healthcare: 40% of hospitals (2021 McKinsey study)" → AGING (update if possible)
- "Mobile phone usage: 47% of population (2018 ITU report)" → OUTDATED (must update)

---

### Cross-Verification Requirement

**Core Rule**: Any claim that appears only once should be treated as UNVERIFIED.

**Minimum verification standard**:
- **Tier 1-2 sources**: 1 citation acceptable (if methodology clear)
- **Tier 3 sources**: MUST verify with 2+ sources (can be Tier 2)
- **Tier 4 sources**: MUST verify with 3+ Tier 1-2 sources
- **Statistical claims**: MUST appear in 2+ independent sources AND match within ±10%
- **Controversial claims**: MUST appear in 3+ sources with detailed reasoning

**How to verify**:
1. Search for the exact statistic/quote (in quotes, Google search)
2. Find original source (trace backwards through citations)
3. Find 2nd independent source making similar claim
4. Note both sources in entry
5. If sources differ: Document both, note discrepancy

**Example Verification Process**:
```
Claim found: "87% of textile production uses virgin materials"
├─ Source 1: Fashion Industry Sustainability Report (2024)
│  └─ Statistic: "87% virgin materials use"
│  └─ Authority: Tier 2
├─ Verify: Search for "87% textile virgin materials" → Find original
├─ Original: Academic paper "Circular Economy in Fashion" (2023)
│  └─ Actual finding: "87% ± 3% across surveyed brands"
│  └─ Authority: Tier 1
└─ Source 2: UN Fashion Report (2024) citing academic paper
   └─ Statistic: "87% virgin materials"
   └─ Authority: Tier 1

Result: ✓ VERIFIED (appears in 2 independent Tier 1 sources)
```

---

## Multi-Pass Research Pipeline

### Pass 1: Breadth (Quick Landscape Scan)

**Timeline**: 30-60 minutes
**Goal**: Map the topic landscape without deep analysis
**Output**: Theme list with 3-5 key sources per theme

**Process**:
1. Execute 5-10 diverse queries on the topic
2. Scan first 10 results from each query (50-100 URLs total)
3. For each result:
   - Read headline + first 2 sentences (10 seconds)
   - Determine: relevant or not?
   - Note: authority tier, theme covered
4. Identify recurring themes (appearing 2+ times)
5. Flag contradictions (opposing viewpoints)
6. Create theme summary with example sources

**Quality gates**:
- [ ] ≥5 different query angles executed
- [ ] ≥25 sources scanned
- [ ] ≥5 themes identified
- [ ] Contradictions noted

**Example Output**:
```
BREADTH SCAN: Sustainable Fashion
Themes:
1. Environmental Impact (8 sources)
   - Cotton water usage
   - Dyeing pollution
   - Textile waste
   Key source: UN Fashion & Environment 2024

2. Supply Chain Transparency (6 sources)
   - Certification standards
   - Blockchain tracking
   - Audit processes
   Key source: Fashion Industry Transparency Report

3. Greenwashing Concerns (4 sources)
   - Brand false claims
   - Lack of standards
   - Verification challenges
   Key source: Academic paper "Greenwashing in Luxury Fashion"

Contradictions found:
- Claim A: "Organic cotton always sustainable"
- Claim B: "Organic cotton has water & land issues"
- Resolution needed: Proceed to Pass 2
```

---

### Pass 2: Depth (Targeted Deep Research)

**Timeline**: 60-180 minutes
**Goal**: Deep-dive each theme, extract key insights with evidence
**Output**: 15-50 research entries with citations

**Process**:
1. For each theme from Pass 1, execute 2-3 specific queries
2. Fetch full content of top 3-5 results per theme
3. Read carefully (10-20 min per source):
   - Identify key claims
   - Extract statistics with citations
   - Note methodology/limitations
   - Check author credentials
4. Create entry for each major insight
5. Assign authority tier based on source
6. Track evidence chains (where did this claim originate?)

**Quality gates**:
- [ ] ≥3 deep sources per theme
- [ ] ≥80% of entries have ≥2 citations
- [ ] ≥60% Tier 1-2 sources
- [ ] No unattributed statistics

**Example: Depth Research on Water Usage Theme**:
```
Query 1: "cotton production water consumption gallons"
→ Fetch: WWF textile production report (Tier 1)
→ Entry: "Cotton Water Footprint: 2,700 liters per shirt"
  - Claim: 2,700 L/shirt average
  - Citation: WWF Water Footprint Network (Tier 1)
  - Evidence: Based on 50+ cotton farms in India, US, others

Query 2: "dyeing textile wastewater environmental impact"
→ Fetch: UN Environmental Programme report (Tier 1)
→ Entry: "Dyeing Industry Water Pollution"
  - Claim: 10-20% of industrial water pollution from dyeing
  - Citation: UNEP 2023 Textiles & Environment
  - Evidence: Analysis of industrial discharge data, 15 countries

Query 3: "water recycling textile factories"
→ Fetch: Case study from Nature Sustainability (Tier 1)
→ Entry: "Water Recycling in Textile Manufacturing"
  - Claim: Advanced water recycling can reduce consumption by 80%
  - Citation: Case study of Swiss manufacturer
  - Limitation: Only applicable in water-rich regions
```

---

### Pass 3: Verification (Fact-Checking Key Claims)

**Timeline**: 45-90 minutes
**Goal**: Verify top claims against primary sources, catch hallucinations
**Output**: Verified claims with confidence levels

**Process**:
1. Identify 10-15 key claims that appear multiple times
2. For each claim:
   - Search for exact quote/statistic
   - Find original source (primary)
   - Check methodology: Is it sound?
   - Check scope: Does it apply broadly?
   - Check date: Is it current?
   - Find 2nd independent source making same claim
3. Compare versions across sources
4. Document discrepancies
5. Assign confidence level (HIGH/MEDIUM/LOW/UNKNOWN)

**Quality gates**:
- [ ] ≥90% of claims traced to source
- [ ] No unattributed statistics remain
- [ ] Discrepancies between sources noted
- [ ] Confidence levels assigned consistently

**Example Verification**:
```
CLAIM: "87% of textile production uses virgin materials"

Trace 1:
├─ Found in: McKinsey Fashion Report 2024
├─ McKinsey cites: Academic paper "Circular Economy in Textiles" 2023
├─ Paper methodology: Survey of 500 brands, voluntary disclosure
└─ Original stat: "87% ± 3% of surveyed brands"

Trace 2:
├─ Found in: UN Textiles Report 2024
├─ UN cites: Same academic paper + 3 industry sources
├─ Independent verification: EU regulatory filing data shows 85-90%
└─ Consistency: Within margin of error ✓

Result: VERIFIED
Confidence: HIGH
Notes: Applies to global brands, excludes niche circular companies
```

---

### Pass 4: Synthesis (Merge & Finalize)

**Timeline**: 30-60 minutes
**Goal**: Combine all findings, resolve conflicts, assign final confidence levels
**Output**: Final knowledge base entries ready for QA

**Process**:
1. Consolidate entries by theme
2. Identify duplicate concepts (merge them)
3. Identify contradictions (document both sides with evidence)
4. Assign final confidence levels:
   - HIGH: 2+ Tier 1-2 sources agree, no contradictions, recent
   - MEDIUM: 1-2 Tier 2 sources OR 3+ Tier 3, some age/limitations
   - LOW: Single source OR conflicting evidence OR weak authority
   - UNKNOWN: Insufficient information, no reliable sources
5. Add metadata:
   - Created date
   - Last verified date
   - Conflict notes
   - Gap notes
6. Generate final entry with all citations

**Quality gates**:
- [ ] All conflicts documented
- [ ] All gaps identified
- [ ] Confidence levels calibrated (MEDIUM not overused)
- [ ] Ready for Phase 4.5 QA

---

## Hallucination Detection

### Red Flags (Patterns to Watch)

**Red Flag 1: Overly Specific Statistics Without Citation**
- Example: "Exactly 47.3% of consumers prefer sustainable brands"
- Why suspicious: Humans don't measure to 0.1%, and if real, it would be cited
- Check: Search for the exact statistic, find original source, verify methodology
- If unfindable: Mark as UNVERIFIED, remove or reword as "roughly half"

**Red Flag 2: Claims That Sound Too Clean**
- Example: "AI reduced diagnosis time by exactly 50% with zero errors"
- Why suspicious: Real systems always have trade-offs and error rates
- Check: Find the original study, read methodology section, note actual findings
- If too good: Likely oversimplification or misinterpretation
- Fix: Rewrite with actual nuance ("reduced by 40-60% with 2-5% error rate")

**Red Flag 3: Fabricated URLs or Citations**
- Example: "According to a study at harvard.ai/research/2024"
- Why suspicious: That's not a real domain/path structure
- Check: Try to visit the URL, search for the exact title
- If unreachable: Flag as unverifiable, find legitimate source
- Pattern: Fake cites often have misspellings or awkward phrasing

**Red Flag 4: Organization Names That Don't Exist**
- Example: "The National Institute for Future Studies found..."
- Why suspicious: Unknown/oddly-named organizations are often fabricated
- Check: Search for the organization + location + "official"
- If not found: Mark UNVERIFIED, do not cite
- Pattern: Real orgs have established websites and media presence

**Red Flag 5: Date References That Don't Make Sense**
- Example: "A 2025 study showed future trends..."
- Why suspicious: Can't have data from future
- Check: Verify publication date on the source
- Pattern: Confusing publication date with data collection date

**Red Flag 6: Unattributed Quotes or Claims**
- Example: "Experts agree that blockchain will revolutionize everything"
- Why suspicious: "Experts" is vague, no citation
- Check: Find which experts, get exact quotes, cite their names
- Fix: "According to MIT's [Name], "quote here" (2024)"

**Red Flag 7: Cascading Citations (Citation Laundering)**
- Example: Article A cites Blog B which cites 2015 report C with wrong statistic
- Why suspicious: The error is now in 3 places, looks verified
- Check: Find original source C, compare to derivative versions
- Pattern: Stats drift through re-citation chains
- Fix: Always trace to original source, note when derivative versions diverge

**Red Flag 8: Logical Inconsistencies**
- Example: "AI will eliminate all jobs but also create new opportunities"
- Why suspicious: Unresolved contradiction
- Check: Do these claims come from same source? Different sources?
- If same source: Request clarification or mark as conflicted
- If different: Document both viewpoints separately

---

### Verification Patterns

**Pattern 1: Verify Statistics**
```
Suspicious stat: "92% of companies use AI"
├─ Search: Exact quote ("92% of companies use AI")
├─ Find original: Gartner survey 2024
├─ Verify methodology:
│  ├─ Sample size: 2,000 companies (adequate)
│  ├─ Geography: Global (good)
│  ├─ Definition: "Any AI or machine learning" (broad, favorable)
│  └─ Methodology notes: Self-reported (may be inflated)
├─ Compare with other sources:
│  ├─ McKinsey 2024: "78% of enterprises"
│  └─ IDC 2024: "85% in developed markets"
├─ Reconciliation: Stat validity depends on AI definition
└─ Final: Report as "78-92% depending on definition" with sources

Result: VERIFIED but QUALIFIED (range, caveats noted)
```

**Pattern 2: Verify URLs Are Real**
```
Suspicious link: "https://example.com/research/2024/findings"
├─ Try visiting the URL → 404 error or not real site
├─ Search for the exact title → No results from that domain
├─ Search for the domain → Site doesn't exist
└─ Check archive.org (Wayback Machine) → Never archived

Result: FABRICATED - Remove from knowledge base
```

**Pattern 3: Verify Organizations Exist**
```
Suspicious claim: "The Global Innovation Council found..."
├─ Google search: "Global Innovation Council" + official
├─ Find: Multiple real organizations, can't identify the specific one
├─ Search with additional context: "Global Innovation Council healthcare"
├─ Result: Found real "Global Innovation Institute" (different name, scope)
├─ Further search: No entity called exactly "Global Innovation Council"
└─ Check: If claimed in article, does article cite them?

Result: UNVERIFIED ORGANIZATION - Reword to specific org or remove
```

**Pattern 4: Verify Dates Are Accurate**
```
Suspicious claim: "A 2023 study showed COVID vaccines prevent all infection"
├─ Find the 2023 study
├─ Check: Does it actually claim "prevent all infection"?
├─ Reality: Study shows "reduce severe illness risk" (different claim)
├─ Check date: Is 2023 the publication or data collection year?
└─ Actual: Published 2023, data from 2021-2022

Result: MISQUOTED & MISSTATED - Fix wording to match actual study
```

---

### When to Mark UNKNOWN vs. LOW

**UNKNOWN**: No information available despite thorough search
- Example: "Impact of quantum computing on fashion supply chains in 2026"
- Symptom: 0 relevant sources after 3+ search attempts with different angles
- Action: Mark topic as UNKNOWN, note as research gap
- Useful: Helps identify future research priorities

**LOW**: Conflicting information OR weak sources OR significant limitations
- Example: Single blog post making strong claim, contradicted elsewhere
- Symptom: Tier 3-4 sources, or Tier 1-2 sources that contradict each other
- Action: Include entry but flag confidence as LOW
- Useful: Captures developing/controversial areas

**Difference**: UNKNOWN = literally no data. LOW = data exists but unreliable.

---

## Citation Tracking

### Citation Format Standard

Every claim needs traceability. Use this format:

**Basic citation**:
```
[Source Title](URL) — accessed YYYY-MM-DD
```

**Example**:
```
[Water Footprint Network: Cotton Consumption](https://waterfootprint.org/en/about-us/frequently-asked-questions/#cotton) — accessed 2026-02-09
```

**Academic citation** (include author + year):
```
[Author Last Name](URL) — Year: Publication Name — accessed YYYY-MM-DD
```

**Example**:
```
[Steinfeld et al.](https://doi.org/10.1038/nature12313) — 2023: Nature Climate Change — accessed 2026-02-09
```

**Organization report**:
```
[Organization Name: Report Title](URL) — Year — accessed YYYY-MM-DD
```

**Example**:
```
[UN Environment Programme: Textiles and the Environment Technical Report](https://www.unep.org/resources/report/textiles-and-environment-2019) — 2019 — accessed 2026-02-09
```

### Bibliography Generation

Create a bibliography file (CSV or JSON) for each knowledge base:

**CSV Format**:
```csv
source_url,source_title,source_author,publication_year,authority_tier,accessed_date
https://example.com/study,Cotton Water Usage,Smithson J,2024,Tier 1,2026-02-09
https://example.com/report,Fashion Sustainability Report,UN UNEP,2023,Tier 1,2026-02-09
```

**JSON Format**:
```json
{
  "bibliography": [
    {
      "id": "source_1",
      "title": "Cotton Water Usage",
      "author": "Smithson, J.",
      "year": 2024,
      "url": "https://example.com/study",
      "authority_tier": "Tier 1",
      "accessed_date": "2026-02-09",
      "citations_count": 3
    }
  ]
}
```

**Include**:
- Source URL (clickable for verification)
- Title
- Author(s)
- Publication year
- Authority tier
- Access date
- Number of times cited in KB (for relevance ranking)

---

## Quality Scoring System

### The 5-Dimension Model

Score each research entry on these 5 dimensions (0-10 each):

#### 1. Accuracy (Are claims verifiable?)
- **10**: All claims traced to Tier 1 sources, methodology sound, no contradictions
- **8-9**: Most claims verified, minor unsourced details, no contradictions
- **6-7**: Claims mostly verifiable, some Tier 3 sources, minor contradictions
- **4-5**: Some unverifiable claims, mixed source tiers, notable contradictions
- **2-3**: Mostly unverifiable, weak sources, significant contradictions
- **0-1**: Fabricated or false claims

**Scoring guide**: Read each claim, search for source, verify methodology. Penalize unsourced stats.

#### 2. Completeness (Are all aspects covered?)
- **10**: Covers all major angles, sub-themes, context, limitations
- **8-9**: Covers main aspects, most sub-themes, mentions limitations
- **6-7**: Covers central topic, misses 1-2 important angles
- **4-5**: Surface-level, misses multiple important aspects
- **2-3**: Narrow focus, many gaps
- **0-1**: Incomplete or misleading omissions

**Scoring guide**: Compare entry to your full Phase 2 theme map. Does it cover all key sub-themes?

#### 3. Depth (Surface-level vs. expert-level?)
- **10**: Expert-level analysis, nuance, mechanism explanation, limitations discussed
- **8-9**: Deep analysis, context provided, some limitations noted
- **6-7**: Moderate depth, explains key concepts, light on context
- **4-5**: Surface-level, basic explanation, lacks context
- **2-3**: Very shallow, oversimplified, potentially misleading
- **0-1**: Trivial or obviously incomplete

**Scoring guide**: Would an expert in the field find this useful or dismiss it as shallow?

#### 4. Recency (How current is the information?)
- **10**: ≤6 months old, most recent available
- **9**: 6-12 months old, recent
- **7-8**: 1-2 years old, acceptable
- **5-6**: 2-3 years old, aging
- **3-4**: 3-5 years old, outdated for fast-moving fields
- **1-2**: >5 years old, only use for historical context
- **0**: Explicitly contradicted by recent research

**Scoring guide**: Domain-dependent. Tech & medicine need recency. History/philosophy less so.

#### 5. Consistency (Does it conflict with other entries?)
- **10**: No conflicts with other entries, fits coherently into KB
- **8-9**: No conflicts, one or two awkward fits
- **6-7**: Minor tensions with other entries, resolvable
- **4-5**: Significant conflict with 1-2 other entries
- **2-3**: Major conflicts with multiple entries
- **0-1**: Directly contradicts well-sourced entries

**Scoring guide**: Compare entry to related entries in graph. Flag contradictions.

### Quality Score Calculation

```
Total = Accuracy + Completeness + Depth + Recency + Consistency
Range: 0-50
Minimum to include: 30
```

**Interpretation**:
- **41-50**: Excellent. Publish as-is.
- **35-40**: Good. Minor revisions may help.
- **30-34**: Acceptable. Flag for review or minor editing.
- **Below 30**: Reject. Needs significant work or removal.

**Real examples**:
```
Entry: "Cotton Water Consumption"
- Accuracy: 9 (verified in 3 sources, methodology clear)
- Completeness: 8 (covers production, dyeing; misses finishing)
- Depth: 8 (explains mechanisms, discusses regional variation)
- Recency: 9 (2025 sources)
- Consistency: 9 (aligns with other water entries)
TOTAL: 43/50 ✓ PUBLISH

Entry: "AI Will Replace All Humans"
- Accuracy: 2 (unverified claims, no sources)
- Completeness: 3 (covers employment, ignores technical constraints)
- Depth: 2 (oversimplified, ignores nuance)
- Recency: 5 (2023 sources, prediction not verification)
- Consistency: 1 (contradicts expert consensus)
TOTAL: 13/50 ✗ REJECT
```

---

## Fact-Checking Checklist

Before accepting ANY research entry into knowledge base, verify:

### Pre-Publication Checklist

**Content Verification**:
- [ ] All statistics have citations (searchable, verifiable)
- [ ] All URLs resolve to real, active pages
- [ ] All quotes are exact and attributed
- [ ] Key claims appear in 2+ independent sources
- [ ] No fabricated organizations, publications, or people
- [ ] Date references are accurate (no future dates, correct years)
- [ ] Technical claims are internally consistent (no logical contradictions)
- [ ] Author/source attribution is clear (no "some say" without names)

**Source Verification**:
- [ ] Primary sources are Tier 1 or higher
- [ ] At least 60% of claims sourced to Tier 1-2
- [ ] No more than 20% of claims from Tier 4 sources
- [ ] Source authority tiers are correctly assigned
- [ ] Evidence chains are traceable (can find original source)

**Confidence Calibration**:
- [ ] Confidence level (HIGH/MEDIUM/LOW/UNKNOWN) is justified
- [ ] HIGH confidence requires 2+ Tier 1-2 sources AND recent
- [ ] LOW confidence clearly marked, not overstated
- [ ] UNKNOWN confidence used only when no reliable sources found
- [ ] Confidence explanation included (why this level?)

**Quality Metrics**:
- [ ] Quality score 30+ (see scoring section above)
- [ ] Accuracy dimension ≥6/10
- [ ] No unresolved contradictions
- [ ] Gaps or limitations noted
- [ ] Entry fits coherently with related entries

**Format & Usability**:
- [ ] Title is concise and clear (50-100 characters)
- [ ] Summary available (150-300 words)
- [ ] Full content organized with headings
- [ ] Key claims callout available (3-5 bullet points)
- [ ] Tags appropriate (3-7, consistent with taxonomy)
- [ ] Related entries linked (via knowledge graph)
- [ ] Metadata complete (author, date, source URL)

### Decision Tree

```
Does entry meet ALL checklist items?
├─ YES → ✓ PUBLISH
└─ NO → Continue...

Are failures minor (e.g., formatting)?
├─ YES → Fix and re-check
└─ NO → Continue...

Can failures be resolved with revision?
├─ YES → Revise, re-check
└─ NO → Continue...

Are failures in accuracy/confidence?
├─ YES → REJECT and request rewrite
└─ NO → Continue...

Are failures in completeness only?
├─ YES → Publish with "Incomplete" flag for expert follow-up
└─ NO → REJECT
```

---

## Confidence Level Definitions

**REFERENCE TO CANONICAL DEFINITION**: The authoritative confidence level framework is defined in `templates/knowledge-entry.md` under "Confidence Level Decision Tree." This section provides quick-reference criteria for QA purposes.

See that section for:
- VERIFIED: 3+ independent Tier 1 sources agree, cross-checked against primary data
- HIGH: 2+ independent sources (at least 1 Tier 1-2), recent, no contradictions
- MEDIUM: 1-2 Tier 2 OR 3+ Tier 3 sources, or single Tier 1 with limitations, 2-3 years old
- LOW: Single Tier 2 OR conflicting Tier 1-2, OR Tier 3-4 only, >3 years old
- UNKNOWN: No source found, or source quality cannot be assessed

### Quick Reference for QA

**HIGH Confidence Checklist**:
- [ ] 2+ Tier 1-2 sources agreeing
- [ ] Methodology disclosed, ≤24 months old
- [ ] Zero contradictions in literature

**MEDIUM Confidence Checklist**:
- [ ] 1-2 Tier 2 sources OR 3+ Tier 3 sources agreeing
- [ ] OR single Tier 1 with acknowledged limitations
- [ ] 2-3 years old, methodology sound

**LOW Confidence Checklist**:
- [ ] Single Tier 2 source OR conflicting Tier 1-2 sources
- [ ] OR only Tier 3-4 available
- [ ] >3 years old OR significant methodology limitations
- [ ] Clearly flag limitations and conflicts

**UNKNOWN Checklist**:
- [ ] No sources found despite thorough search
- [ ] All sources are Tier 4 (unverified)
- [ ] Claim is speculative with zero supporting evidence

---

## Common Pitfalls & Fixes

| Pitfall | What Goes Wrong | Fix |
|---------|-----------------|-----|
| **Over-trusting search results** | First 3 Google results aren't always the best | Use multiple search angles, check for Tier classification |
| **Accepting any "study says"** | Claims without methodology are unverifiable | Fetch original paper, read methods section |
| **Using old data** | "A 2015 study showed..." still cited in 2026 | Check publication date vs. data date; prefer ≤2 years old |
| **Ignoring contradictions** | Keep source that confirms bias | Document both sides, note which is better-sourced |
| **Cascade citations** | Article A cites Blog B cites Paper C (error at each step) | Always trace to original paper C |
| **Fabricated stats** | "47.3% (no citation)" gets copied everywhere | Search exact stat; if not found, remove or reword |
| **Greenwashing claims** | Company says "sustainable" with zero evidence | Check third-party certifications, not company claims |
| **Oversimplification** | "AI solves healthcare" ignores real challenges | Include limitations, tradeoffs, remaining gaps |
| **Missing confidence labels** | Reader doesn't know if claim is solid or speculative | Always tag HIGH/MEDIUM/LOW/UNKNOWN |
| **Incomplete citations** | "A study showed..." with no link | Provide URL + title + author + year |

---

## Quality Assurance Workflow

### Step-by-Step for Each Entry

1. **Read the entry** (5 min)
   - Scan for red flags
   - Note any unattributed claims

2. **Verify statistics** (10 min)
   - Search for exact stat
   - Find original source
   - Check if matches ± 10%
   - Document both in entry

3. **Check sources** (10 min)
   - Visit 3-5 cited URLs
   - Verify they say what entry claims
   - Confirm URLs are real/not broken

4. **Assess authority** (5 min)
   - Classify each source Tier 1-4
   - Ensure ≥60% Tier 1-2
   - Flag if too much Tier 4

5. **Score dimensions** (5 min)
   - Accuracy: 0-10
   - Completeness: 0-10
   - Depth: 0-10
   - Recency: 0-10
   - Consistency: 0-10
   - Total: Should be ≥30

6. **Assign confidence** (2 min)
   - HIGH/MEDIUM/LOW/UNKNOWN
   - Justify in notes

7. **Make decision** (2 min)
   - ≥30 points? → PASS
   - <30 points? → FAIL, requires revision or rejection

**Total time per entry: 39-40 minutes**
**Target QA pass rate: ≥85% of entries**

---

**Version**: 2.0
**Last Updated**: 2026-02-09
**Status**: Production
