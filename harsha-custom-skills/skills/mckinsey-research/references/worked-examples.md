# Worked Examples — Complete Walkthroughs

These examples show the full 9-phase workflow in action at each scrutiny tier,
including what the practitioner *thinks*, *does*, and *produces* at each step.

---

## Example 1: Standard Tier — "Is Bun faster than Node.js?"

### Phase 1: Triage & Scope
**Think**: Factual performance comparison. Well-benchmarked topic with official data.
Low decision stakes for most users. Standard tier.

**Do**: Rewrite neutrally:
- BAD: "Is Bun faster than Node.js?" (embeds assumption of Bun superiority)
- GOOD: "What are the performance differences between Bun and Node.js across common
  workloads, and under what conditions does each perform better?"

PICO decomposition:
- **P**roblem: Choosing a JS runtime for performance-sensitive work
- **I**ntervention: Bun
- **C**omparison: Node.js
- **O**utcome: Throughput, startup time, memory usage across workload types

Temporal check: Software frameworks have 6-18 month half-life. Need sources from
the last 12 months.

### Phase 2: Hypotheses (Light — 1 contrasting)
**H1**: Bun is faster across the board due to its Zig-based architecture.
**H2 (contrasting)**: Bun shows large gains on synthetic benchmarks but converges
with Node.js on I/O-bound real-world workloads where the runtime isn't the bottleneck.

### Phase 3: Search (2-3 searches)
1. **Official**: Bun.sh/benchmarks + Node.js performance docs
2. **Independent benchmarks**: "Bun vs Node.js benchmark 2025" (TechEmpower, etc.)
3. **Criticism**: "Bun benchmark misleading" / "Bun production problems"

Search log:
- Bun official: Found startup/install benchmarks. Note: vendor-provided.
- Independent: Found 2 TechEmpower-style comparisons and 1 blog with HTTP throughput tests.
- Criticism: Found 3 articles noting gaps in compatibility and limited production telemetry.

### Phase 4: Source Validation
- Bun's official benchmarks: **Vendor source** — treat as promotional. Note favorable
  conditions (empty servers, no middleware). Green flag: specific, reproducible methodology.
- TechEmpower: **Independent benchmark** — neutral, methodology documented. Green flag.
- Blog benchmarks: Check date (2025?), author (active developer vs. content farm?),
  methodology (real app or hello-world?).
- Criticism articles: Check whether criticisms address performance specifically or just
  ecosystem maturity.

### Phase 8: Pyramid Output

```markdown
---
title: Bun vs Node.js Performance Comparison
scrutiny_tier: Standard
knowledge_as_of: 2025-11-15
valid_until: 2026-05 (6-month framework half-life)
review_triggers: Bun 2.0 release, Node.js major version
confidence_overall: Moderate
sources_evaluated: 8 found → 6 screened → 5 included
---

## Executive Summary (SCR)
**Situation**: Bun and Node.js compete as server-side JavaScript runtimes.
Bun markets significant performance advantages over Node.js.

**Complication**: Bun's benchmarks show 3-5x speedups, but test conditions
differ from production workloads where I/O dominates.

**Resolution**: Bun is genuinely faster for startup, package installation,
and CPU-bound scripting tasks (2-5x). For production HTTP servers with
database/network I/O, the gap narrows to 10-30% because the runtime is
no longer the bottleneck. Recommend Bun for tooling and scripts; evaluate
with real workload benchmarks before production adoption.

## Key Findings
**Bun's startup speed advantage is real and significant.**
- 4-5x faster cold start than Node.js (multiple independent benchmarks)
- Likelihood: Highly Likely | Evidence Quality: High
- Caveat: Startup matters for CLI tools, less for long-running servers

**Production throughput gains are modest and workload-dependent.**
- 10-30% throughput improvement on HTTP benchmarks with I/O
- Likelihood: Likely | Evidence Quality: Moderate (limited production data)
- Caveat: Most production bottlenecks are in database/network, not runtime

## Gaps & Limitations
- Limited real-world production telemetry (most benchmarks are synthetic)
- Node.js v22+ may narrow the gap further (recent optimization work)
- Coverage: ~80% of identified performance dimensions addressed
```

### Phase 9: QA + Temporal Tag
- Spot-check: Verified Bun startup benchmark against official source ✓
- Temporal tag: `valid_until: 2026-05`, `review_trigger: Bun 2.0 or Node.js 23+`
- Failure pattern check: No package references to verify. No circular citations detected.

---

## Example 2: Enhanced Tier — "Should we enter the Indian BNPL market?"

### Phase 1: Triage & Scope
**Think**: Strategic business decision with regulatory, market, and competitive
dimensions. Contested regulatory landscape. Important decision → Enhanced tier.

**Do**: PICO decomposition:
- **P**roblem: Market entry decision for a fintech company
- **I**ntervention: Launch a BNPL product in India
- **C**omparison: Other fintech verticals, other geographies, staying out
- **O**utcome: Risk-adjusted ROI over 3-year horizon

Sub-questions (MECE):
1. Regulatory viability: Can BNPL operate legally under current/anticipated RBI rules?
2. Market size & growth: Is the addressable market large enough?
3. Competition: Who's there, what's their position, is there room?
4. Unit economics: Can BNPL be profitable at Indian price points?

Temporal check: Fintech regulations have ~6-month half-life. Need RBI circulars
from last 6 months minimum.

### Phase 2: Hypotheses (3 alternatives)
**H1**: India BNPL is high-growth opportunity with manageable regulatory risk.
Supporting signals: rising digital payments, young demographics, credit gap.

**H2**: RBI regulatory tightening will make the BNPL model unviable within
18 months. Supporting signals: RBI digital lending guidelines, FLDG restrictions.

**H3**: Market is viable but already saturated — late entry means unprofitable
customer acquisition costs and compressed margins.

**Bias checkpoint**: Am I anchoring on H1 because BNPL is a popular narrative?
Check: generating H2 and H3 forces consideration of failure modes.

### Phase 3: All 6 Search Types
1. **Official**: RBI circulars on digital lending (rbi.org.in), SEBI regulations
2. **Primary**: BNPL market size reports (RedSeer, Redseer, BCG), industry reports
3. **Criticism**: "BNPL India problems", "digital lending failures India"
4. **Failure**: "BNPL company shutdown India", "ZestMoney closure"
5. **Evolution**: "India credit market evolution", "credit cards to BNPL transition"
6. **Alternative**: "Embedded finance India", "micro-lending alternatives"

Search log (abbreviated):
- RBI: Found Digital Lending Guidelines (2022), FLDG circular (2023), recent commentary
- Market reports: 3 reports found; estimates vary 3x ($3B to $10B by 2026)
- Criticism: Found ZestMoney shutdown case study, NPL concerns in industry articles
- Failure: Limited post-mortems publicly available
- Evolution: Strong coverage of UPI → credit transition
- Alternative: Found embedded lending, sachet insurance gaining traction

### Phase 4: Source Validation
- RBI circulars: **Primary regulatory source** — highest authority. Green flag.
- Market reports: **Industry reports** — check funding source. RedSeer is independent;
  one report is vendor-sponsored (flag as potentially biased).
- ZestMoney coverage: **News articles** — verify from multiple outlets. Cross-referenced
  3 sources. Confirmed.
- Alternative fintech: Check recency and market-specific applicability.

### Phase 5: Synthesis + Bias Checkpoint
**Triangulation** (Denzin — Data triangulation):
- Market size: 3 sources, estimates range $3B-$10B. GRADE: Low certainty (projections
  vary 3x, different methodologies, some vendor-funded).
- Regulatory direction: 4 sources (2 RBI circulars, 2 law firm analyses). GRADE: Moderate
  certainty (regulatory intent is clear; implementation timeline uncertain).
- Competition: 5 sources. GRADE: Moderate certainty (player list is factual;
  market share estimates vary).

**Bias checkpoint**:
- Am I overweighting bullish vendor-sponsored reports? → Downweight the sponsored report.
- Am I anchoring on ZestMoney failure as representative? → It's one case; check for
  survivors and successes too.
- Recency bias: Am I overweighting recent RBI tightening vs. longer-term growth trend?
  → Include both time horizons in analysis.

### Phase 6: Stress Test + Pre-mortem
**Expert A (Fintech Specialist)**: "Regulatory risk is the dominant variable.
Everything else is secondary. If RBI restricts non-NBFC lending, the entire model
breaks regardless of market size."

**Expert B (Skeptic)**: "Unit economics don't work at Indian price points. Average
BNPL ticket is ₹5,000-15,000. Default rates are 5-8%. Margin is razor-thin. You need
massive scale to break even, which means massive CAC."

**Expert C (Practitioner)**: "The operational complexity of collections in India is
chronically underestimated by new entrants. Physical presence matters for recovery.
This isn't a pure-digital business."

**Pre-mortem**: "If this market entry fails, the most likely reasons are:"
1. RBI bans lending by non-NBFC entities (probability: 25-35%; would require
   complete strategic pivot)
2. Customer acquisition costs exceed LTV at Indian ticket sizes (probability: 40%;
   would require finding higher-value segments)
3. Default rates spike during economic downturn (probability: 20%; cyclical risk
   with limited historical data for BNPL in India)

### Phase 7: Gap Check
Coverage assessment:
- Regulatory viability: 85% covered (strong RBI sources)
- Market size: 60% covered (conflicting estimates, limited primary data)
- Competition: 75% covered (public data only; private company metrics unavailable)
- Unit economics: 50% covered (limited public data on Indian BNPL margins)

Overall coverage: ~68%. Below Enhanced tier requirement (85%).
Gap: Unit economics data is thin. Attempt targeted search for "BNPL profitability
India" and "digital lending NPA rates India."

After targeted search: Coverage rises to ~78%. Document remaining gaps.

### Phase 8: Pyramid Output

```markdown
---
title: Indian BNPL Market Entry Assessment
scrutiny_tier: Enhanced
knowledge_as_of: 2025-12-01
valid_until: 2026-06 (regulatory half-life ~6 months)
review_triggers: New RBI FLDG circular, major BNPL player exit/entry
confidence_overall: Moderate (high regulatory uncertainty)
sources_evaluated: 18 found → 14 screened → 11 included
---

## Executive Summary (SCR)
**Situation**: India's BNPL market is estimated at $3-10B (wide range reflects
methodological differences), driven by digital payment adoption and a large
credit-underserved population.

**Complication**: RBI has progressively tightened digital lending regulations.
The ZestMoney shutdown signals unit economics challenges. Default rates are
elevated at 5-8% for the segment.

**Resolution**: Market entry is viable but high-risk. Recommend: (1) Secure
NBFC license as prerequisite — non-NBFC routes are regulatory time bombs.
(2) Target ticket sizes >₹20,000 to improve unit economics. (3) Build a
6-month regulatory monitoring capability before launch. Alternative: Consider
embedded lending partnerships with existing NBFCs as lower-risk entry.
Confidence: Possible | Evidence Quality: Low-Moderate.

## Competing Positions
**Position A** (Bullish): India's credit gap + digital infrastructure = massive
opportunity. Evidence: UPI transaction growth, rising e-commerce, government
financial inclusion push.

**Position B** (Bearish): Regulatory tightening + thin margins + high defaults
= value trap. Evidence: RBI guidelines, ZestMoney closure, 5-8% NPL rates.

**Current Assessment**: Evidence slightly favors caution (B). The regulatory
trajectory is clear: RBI is tightening. The unit economics question is unresolved.

**What Would Change This**: (a) RBI explicitly endorsing BNPL model, or
(b) A player publicly demonstrating profitability at scale in India.

## Pre-Mortem
1. RBI restricts non-NBFC lending (25-35%) → Mitigate: secure NBFC license first
2. CAC exceeds LTV at Indian ticket sizes (40%) → Mitigate: target higher segments
3. Default rates spike in downturn (20%) → Mitigate: conservative underwriting

## Gaps & Limitations
- Unit economics data is limited (no public margin data for Indian BNPL)
- Private company performance data unavailable
- Coverage: 78% of identified topics addressed
```

### Phase 9: QA + Temporal Tag
- Spot-checked: RBI circular references verified against rbi.org.in ✓
- ZestMoney shutdown: Confirmed across 3 independent news sources ✓
- Circular source check: Market size estimates trace to 2 independent methodologies ✓
  (RedSeer and BCG use different approaches — genuinely independent)
- Temporal: `valid_until: 2026-06`, `review_trigger: next RBI policy review`

---

## Example 3: Maximum Tier — "Evaluate LLM orchestration frameworks for production"

### Phase 1: Triage & Scope
**Think**: High-stakes technology decision with significant lock-in risk.
Fast-evolving landscape (6-month half-life). Maximum tier.

**Do**: MECE decomposition across 5 dimensions:
1. **Reliability**: Error handling, retry logic, graceful degradation
2. **Cost**: Token efficiency, API call optimization, total cost of ownership
3. **Flexibility**: Model-agnostic, customization, escape hatches
4. **Ecosystem**: Community, docs, integrations, maintenance health
5. **Operational complexity**: Debugging, monitoring, deployment, team onboarding

Candidates to evaluate: LangChain, LlamaIndex, Semantic Kernel, raw API + custom
orchestration, Haystack.

Inclusion criteria: Production-ready (not alpha/beta), active maintenance (commit
within 90 days), documented by multiple independent sources.

### Phase 2: Full ACH (4 hypotheses)
**H1**: LangChain is production-ready and best-supported — the safe default.
**H2**: LangChain is over-abstracted; lighter frameworks or direct API integration
outperform in production.
**H3**: No framework — direct API with custom orchestration wins on flexibility
and debuggability.
**H4**: The landscape is too volatile for commitment; any framework choice has
high switching cost and short useful life.

**ACH matrix setup**: Each hypothesis will be evaluated against all 5 MECE dimensions.
Focus on diagnostic evidence (what differentiates between hypotheses), not confirming
evidence (what all hypotheses share).

### Phase 3: 6 Searches + Sub-Agent Dispatch

**Sub-agent dispatch** (6 agents — one per MECE dimension + 1 contrarian):

Agent 1 (Explorer — Reliability): "Research error handling, retry logic, and
production failure modes across LangChain, LlamaIndex, Semantic Kernel, and
direct API approaches. Search for production incident reports and post-mortems."

Agent 2 (Explorer — Cost): "Research token efficiency, API call optimization,
and total cost of ownership for LLM orchestration frameworks. Find concrete
cost comparisons from production deployments."

Agent 3 (Explorer — Flexibility): "Research customization capabilities,
model-switching ease, and lock-in risk for LLM orchestration frameworks.
Search for migration stories between frameworks."

Agent 4 (Explorer — Ecosystem): "Research community size, documentation quality,
maintenance health, and integration availability for LLM orchestration frameworks.
Check GitHub metrics, release cadence, bus factor."

Agent 5 (Explorer — Operations): "Research debugging, monitoring, deployment
complexity, and team onboarding experience for LLM orchestration frameworks.
Search for developer experience reports."

Agent 6 (Contrarian): "Search specifically for: 'LangChain problems',
'why I stopped using LangChain', 'LlamaIndex criticism', 'LLM framework
overengineered', 'direct API vs framework LLM'. Return the strongest
arguments AGAINST each framework."

All 6 agents launched in single message for parallel execution.

### Phase 4: Source Validation (applied within each agent)
Each agent validates per domain-strategies.md (Software Engineering section):
- GitHub: stars are vanity, dependents are sanity. Check npm dependents count.
- Production reports: Author is actual practitioner? Company disclosed?
- Vendor comparisons: Check for sponsorship. LangChain-funded comparison ≠ independent.
- Documentation: Official docs > blog tutorials > Stack Overflow answers.

### Phase 5: Synthesis + Bias Checkpoint
**Collation** (6-step algorithm from sub-agent-orchestration.md):
1. Parse: Extract structured findings from each agent
2. Merge: Combine into unified matrix (framework × dimension)
3. Detect conflicts: Agent 4 (Ecosystem) says LangChain has best ecosystem;
   Agent 6 (Contrarian) says LangChain's complexity negates ecosystem advantages.
   **Preserve as competing position.**
4. Resolve where possible: Multiple agents confirm debugging is harder with
   LangChain than direct API (3 independent sources) → high confidence.
5. De-duplicate: Remove overlapping findings across agents.
6. Cross-reference: Link cost findings to flexibility findings (lock-in affects TCO).

**Bias checkpoint**:
- Popularity bias: LangChain dominates search results. Are we underweighting
  less-popular alternatives? → Contrarian agent compensates.
- Recency bias: Recent criticism may overweight short-term issues. → Check if
  issues are being fixed (release notes, roadmap).
- Authority bias: High-profile developer opinions ≠ production evidence. →
  Require production data over personal preference.

### Phase 6: Stress Test + Pre-mortem
**Expert A (ML Engineer)**: "LangChain adds unnecessary abstraction for most
use cases. Direct API with thin wrappers gives you better control and debugging."

**Expert B (Skeptic)**: "All of these frameworks will look different in 12 months.
The real question isn't which framework — it's how cheaply can you switch."

**Expert C (Practitioner)**: "We migrated from LangChain to direct API. The
migration took 3 weeks for a team of 2. The hard part wasn't code — it was
finding where LangChain's abstractions were hiding actual behavior."

**Expert D (Security)**: "Framework dependencies are attack surface. LangChain's
dependency tree is massive. Each dependency is a supply chain risk."

**Pre-mortem**: "If this framework choice fails:"
1. Framework introduces breaking changes in next major version (probability: 50%
   within 12 months; all frameworks are pre-1.0 or recently 1.0)
2. Performance bottleneck traced to framework overhead (probability: 30%;
   measurable at scale)
3. Security vulnerability in framework dependency chain (probability: 25%;
   proportional to dependency count)

### Phase 7: Gap Check
Coverage assessment:
- Reliability: 85% (good production data for LangChain, limited for others)
- Cost: 65% (few public TCO comparisons)
- Flexibility: 80% (migration stories available)
- Ecosystem: 90% (GitHub metrics are public)
- Operations: 70% (debugging reports available; monitoring data scarce)

Overall coverage: ~78%. Below Maximum tier requirement (95%).

**Dispatch 2 additional agents**:
- Deep-Diver: "Find specific TCO comparisons for LLM orchestration in production.
  Search for blog posts with actual cost numbers."
- Deep-Diver: "Find production monitoring and observability setup guides for
  each framework. Search for OpenTelemetry integration status."

After Wave 2: Coverage rises to ~88%. Document remaining gaps.

### Phase 8: Pyramid Output (abbreviated structure)

```markdown
---
title: LLM Orchestration Framework Evaluation
scrutiny_tier: Maximum
knowledge_as_of: 2025-12-15
valid_until: 2026-06 (6-month framework half-life)
review_triggers: LangChain 1.0 stable, new framework launch, model provider API changes
confidence_overall: Moderate
sources_evaluated: 34 found → 26 screened → 19 included
---

## Executive Summary (SCR)
**Situation**: Production LLM applications need orchestration for prompt management,
tool use, retrieval, and multi-step workflows. Four main approaches exist.

**Complication**: The framework landscape is volatile (6-month half-life). LangChain
dominates mindshare but faces growing criticism for over-abstraction. Lock-in risk
is high for any choice.

**Resolution**: For most production use cases, start with direct API integration
plus thin custom wrappers (H3). This maximizes debuggability and minimizes lock-in.
Use LangChain/LlamaIndex only if you need specific pre-built integrations (RAG
pipelines, agent frameworks) AND accept the debugging/migration cost. Key decision
factor is switching cost, not current features.

## Weighted Scoring Matrix
[Framework × Dimension matrix with scores and weights]
Winner: Direct API (weighted 4.2/5) > LlamaIndex (3.6) > LangChain (3.4)

## Competing Positions
**Position A**: LangChain's ecosystem advantage outweighs complexity costs.
**Position B**: Over-abstraction makes LangChain a net negative for production.
**Current Assessment**: B has more diagnostic evidence (migration stories,
debugging complaints, production incident reports).

## Pre-Mortem: What If We're Wrong
[3 failure modes with probabilities and mitigations]

## Evolution & Context
Trajectory: Frameworks are converging toward thinner abstractions. LangChain
Expression Language (LCEL) was a response to over-abstraction criticism.
Model providers (OpenAI, Anthropic) are building more orchestration into their
APIs, potentially making frameworks less necessary.

## Gaps & Limitations
- TCO data remains limited (few companies share actual costs)
- Long-term maintenance burden data doesn't exist yet (frameworks too young)
- Coverage: 88% of identified topics addressed
```

### Phase 9: QA + Temporal Tag
- API verification: All referenced framework APIs verified against current docs ✓
- Deprecated check: Verified LangChain APIs against 0.3.x release notes ✓
- Circular source check: Migration stories trace to 4 independent authors ✓
- Slopsquatting check: No package references in this research (not applicable)
- Temporal: `valid_until: 2026-06`, `review_trigger: any framework major release`

---

## Key Patterns Across Examples

| Pattern | Standard | Enhanced | Maximum |
|---------|----------|----------|---------|
| Hypotheses | 1 contrasting | 3 alternatives | 4+ with ACH matrix |
| Search types | 2-3 targeted | All 6 | All 6 + sub-agents |
| Sub-agents | None | Optional | 6-12 in waves |
| Pre-mortem | None | Required | Required + expert panel |
| Gap threshold | 70% | 85% | 95% (achieved 88%) |
| Sources | 5-8 | 11-18 | 19-34 |
| Temporal tag | Basic | Full | Full + dependency mapping |
