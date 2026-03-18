---
name: mckinsey-grade-research-engine
description: >
  Consultant-grade research engine producing rigorous, decision-ready analysis by
  combining McKinsey's Pyramid Principle and MECE decomposition with epistemic
  research methodology, procedural debiasing, and AI-native sub-agent orchestration.

  Integrates: McKinsey communication frameworks (Pyramid, SCR/SCQA, bold-bullet) +
  CIA structured analytic techniques (ACH, Devil's Advocacy, Red Team) + PRISMA
  audit methodology + GRADE evidence grading + Denzin triangulation + procedural
  debiasing (empirically validated — declarative awareness alone has limited effect).

  USE THIS SKILL WHEN:
  - User wants rigorous research on ANY topic — market, technology, strategy, claims
  - User says "deep research", "consulting-grade", "strategic analysis", "evaluate X"
  - User needs to compare options, verify claims, or assess a technology/library
  - Research for business strategy, product decisions, market entry, competitive positioning
  - User asks to "analyze", "investigate", "evaluate", "compare deeply"
  - User needs structured output with executive summary, evidence chains, confidence tags
  - User wants fact-checking, claim verification, or information freshness assessment
  - User mentions "thought leadership", "insight report", "competitive analysis"
  - Research as input for skill creation, knowledge bases, or decision documents
---

# McKinsey-Grade Research Engine v3.0

A research production system fusing McKinsey's communication rigor with epistemic
methodology, procedural debiasing, and AI-native sub-agent orchestration.

**Provenance**: ~30% McKinsey frameworks (Pyramid, MECE, SCR, kill gates, micro-to-macro),
~30% intelligence analysis (CIA SATs, ACH, NATO Admiralty Code), ~25% academic methodology
(PRISMA, GRADE, Denzin, Cochrane), ~15% LLM-specific research (anchoring mitigation,
sycophancy prevention, failure patterns). The name reflects the *output quality standard*,
not exclusive McKinsey derivation.

## Non-Negotiable Rules

1. **Procedure over awareness**: Debiasing is mandatory workflow steps, not advisory text.
   Research shows procedural interventions are effective ~80% of the time; telling models
   about bias has limited measurable effect (Meade et al. ACL 2022).

2. **Hypotheses before evidence**: Generate competing explanations BEFORE searching.
   Anchoring bias retains ~37% of anchor difference and is resistant to simple mitigation
   (He et al. 2025). The only effective counter is structured hypothesis diversity.

3. **Disconfirmation over confirmation**: Actively seek evidence that DISPROVES hypotheses.
   One strong contradicting source outweighs ten confirming ones.

4. **Preserve contradictions**: Never silently resolve disagreements. Document both
   positions, evidence for each, and what would change the assessment.

5. **Tag confidence AND evidence quality separately**: A claim can be "likely" with "low"
   evidence quality. These are independent dimensions.

## The 9-Phase Workflow

```
REQUEST → [1] TRIAGE & SCOPE → [2] HYPOTHESES → [3] SYSTEMATIC SEARCH
        → [4] SOURCE VALIDATION → [5] SYNTHESIS + BIAS CHECK
        → [6] STRESS TEST + PRE-MORTEM → [7] GAP CHECK
        → [8] PYRAMID OUTPUT → [9] QA + TEMPORAL TAG
        → [POST-DELIVERY] FEEDBACK LOOP
```

| Phase | What Happens | Depth Scales With Tier | Reference File |
|-------|-------------|----------------------|----------------|
| **1. Triage** | Assess worthiness, set tier, MECE decompose, strip assumptions | All tiers | `kill-gates.md` |
| **2. Hypotheses** | Generate competing explanations before any search | Standard: 1 contrasting; Enhanced: 2-3; Maximum: full ACH | `anti-anchoring.md`, `bias-debiasing.md` |
| **3. Search** | Execute 6 search types: primary, alternative, criticism, failure, evolution, official | Standard: 2-3 searches; Enhanced: all 6; Maximum: all 6 + sub-agents | `domain-strategies.md`, `prompt-optimization.md` |
| **4. Validate** | Type-specific source quality checks (technical, academic, business, web) | All tiers | `source-validation.md`, `fact-checking.md` |
| **5. Synthesize** | Triangulate evidence, grade certainty, run bias checkpoint | All tiers | `evidence-synthesis.md`, `bias-debiasing.md` |
| **6. Stress test** | Multi-expert simulation + pre-mortem ("if wrong, why?") | Enhanced+Maximum | `expert-simulation.md` |
| **7. Gap check** | Identify coverage/depth/conflict/assumption gaps, check saturation | Enhanced+Maximum | `gap-analysis.md` |
| **8. Output** | Pyramid structure: answer first, then arguments, then evidence (SCR format) | All tiers | `pyramid-output.md`, `executive-summary.md` |
| **9. QA** | Spot-check claims, check for hallucinations/circular sources, temporal tag | All tiers | `failure-prevention.md`, `temporal-validity.md` |

### Scrutiny Tiers — Match Effort to Stakes

| Tier | When | Phases | Typical Effort |
|------|------|--------|---------------|
| **Standard** | Factual lookups, established topics | 1→2(light)→3(2-3 searches)→4→8→9 | Quick |
| **Enhanced** | Important decisions, contested topics | All 9 phases | Moderate |
| **Maximum** | High-stakes, novel, contradictory evidence | All 9 phases + sub-agent dispatch | Deep |

Phase 2 **scales with tier**: Standard gets one contrasting hypothesis (enough to avoid
anchoring on the obvious answer). Enhanced gets 2-3 genuine alternatives. Maximum gets
full Analysis of Competing Hypotheses with evidence matrix.

### The 6 Search Types (Phase 3)

Every research question beyond Standard tier gets ALL six. Vary the order across
hypotheses — don't always search the "expected winner" first.

1. **Primary**: Direct answer to the research question
2. **Alternative**: "Alternatives to [X]", "competitors to [X]"
3. **Criticism**: "Problems with [X]", "[X] limitations"
4. **Failure**: "[X] post-mortem", "migration away from [X]"
5. **Evolution**: "History of [X]", "what replaced [X]"
6. **Official**: Go directly to official documentation, not blog summaries

Log every search. This creates the PRISMA-style audit trail.

### Sub-Agent Dispatch (Phase 3, Maximum Tier)

**→ Read `references/sub-agent-orchestration.md` for full patterns**

Use sub-agents when independent research vectors exist and main context is >60% utilized.

| Research Scope | Practical Agent Count | Notes |
|---------------|----------------------|-------|
| Small (3-5 gaps) | 3-5 agents | One agent per gap |
| Medium (5-15 gaps) | 5-8 agents | Prioritize by severity |
| Large (15+ gaps) | 8-12 in waves | Wave 1: top priorities → reassess → Wave 2 |

Each sub-agent gets: ONE specific target, neutrally-framed prompt, explicit instruction
to search for contradicting evidence, and structured output schema. Budget 30-40% of
total context for synthesis after agents return.

**Practical constraint**: Beyond ~10 concurrent agents, per-agent token budgets shrink
enough to degrade individual research quality. Prefer fewer, better-resourced agents
over many shallow ones.

### Temporal Validity (Phase 9)

Every finding gets temporal metadata. Different domains decay at different rates:

| Domain | Half-Life | Review Trigger |
|--------|-----------|---------------|
| Security/vulnerabilities | Days-weeks | CVE disclosure |
| Software frameworks | 6-18 months | Major version release |
| Fintech regulations | ~6 months | New regulatory circular |
| Academic research | 5-10 years | Replication study |
| Mathematics/proofs | Indefinite | Never |

**→ Read `references/temporal-validity.md` for full domain table and tagging procedure**

### Post-Delivery Feedback Loop

After delivering research, prompt for outcome tracking:

1. **Was the research acted on?** If not, understand why (wrong question? wrong depth?)
2. **Did conclusions hold up?** Track which findings aged well vs. which were wrong
3. **What was missing?** Capture gaps discovered only in application
4. **Update the temporal tags**: If findings expired faster/slower than predicted, adjust
   domain decay estimates for future research

This closes the loop that makes research methodology improve over time, rather than
remaining a static one-shot pipeline.

## Worked Examples

### Example 1: Standard Tier — "Is Bun faster than Node.js?"

**Phase 1 (Triage)**: Factual performance comparison, well-benchmarked. Standard tier.
Neutral rewrite: "What are the performance differences between Bun and Node.js across
common workloads, and under what conditions does each perform better?"

**Phase 2 (Hypotheses — light)**: H1: Bun is faster across the board. Contrasting H2:
Bun is faster on micro-benchmarks but similar in real-world applications with I/O waits.

**Phase 3 (Search — 2-3 queries)**: Official Bun benchmarks, independent benchmarks
(TechEmpower, etc.), criticism/limitations of Bun performance claims.

**Phase 4 (Validate)**: Check benchmark dates, methodology, who ran them (vendor vs independent).

**Phase 8 (Output)**: SCR format. Situation: Both runtimes target server-side JS.
Complication: Bun's benchmarks show 3-5x speedups but conditions differ from production.
Resolution: Bun is faster for startup and scripting; production throughput gap narrows
with I/O-bound workloads. Recommend Bun for tooling/scripts, evaluate for production.
Confidence: Likely | Evidence: Moderate (benchmarks exist but production data is limited).

**Phase 9 (QA)**: Tag `knowledge_as_of: [date]`, `valid_until: +12 months` (framework
half-life), `review_trigger: Bun 2.0 or Node.js major release`.

### Example 2: Enhanced Tier — "Should we enter the Indian BNPL market?"

**Phase 1**: Strategic business decision, contested regulatory landscape. Enhanced tier.
PICO: Problem: market entry decision. Intervention: launching BNPL product in India.
Comparison: other fintech verticals or geographic markets. Outcome: risk-adjusted ROI.

**Phase 2 (3 hypotheses)**: H1: India BNPL is high-growth with manageable regulation.
H2: RBI tightening will make BNPL unviable within 18 months. H3: Market is viable but
already saturated — late entry means unprofitable unit economics.

**Phase 3 (All 6 search types)**: RBI circulars on digital lending (official), BNPL
market size reports (primary), competitor failures/exits (failure), criticism of BNPL
model in India (criticism), evolution from credit cards to BNPL (evolution), alternative
fintech products gaining traction (alternative).

**Phase 5 (Synthesis + bias check)**: Triangulate RBI regulatory direction across 3+
sources. GRADE the market size estimates (Low certainty — projections vary 3x). Bias
checkpoint: are we overweighting bullish reports from BNPL vendors?

**Phase 6 (Stress test)**: Expert A (fintech specialist): regulatory risk is real.
Expert B (skeptic): unit economics don't work at Indian price points. Expert C
(practitioner): operational complexity of collections in India is underestimated.
Pre-mortem: "If this fails, most likely because RBI bans lending by non-NBFCs."

**Phase 8 (Output)**: Full Pyramid with competing positions section, evolution narrative,
pre-mortem, and source registry. Temporal tag: `valid_until: next RBI policy review`.

### Example 3: Maximum Tier — "Evaluate LLM orchestration frameworks for production"

**Phase 1**: High-stakes technology decision. Maximum tier. MECE decomposition:
reliability, cost, flexibility, ecosystem, operational complexity.

**Phase 2 (Full ACH)**: H1: LangChain is production-ready and best-supported.
H2: LangChain is over-abstracted; lighter frameworks outperform. H3: No framework —
direct API integration with custom orchestration wins. H4: The landscape is too
volatile; any choice has high switching cost.

**Phase 3 (6 searches + sub-agents)**: Dispatch 6 sub-agents — one per MECE dimension.
Each searches all 6 types within their dimension. Contrarian agent specifically searches
for "LangChain problems" and "why I stopped using [framework]."

**Phase 7 (Gap check)**: After synthesis, coverage is 78%. Gaps: limited production
telemetry data, no cost comparison at scale. Dispatch 2 more agents for targeted deep-dives.

**Phase 9 (QA)**: Verify all referenced APIs exist. Check version currency (frameworks
with 6-month half-life). Flag any single-source claims. Temporal tag:
`valid_until: +6 months`, `review_trigger: any framework major release`.

## Specialized Modes

| Mode | When | Start By Reading | Key Addition |
|------|------|-----------------|--------------|
| **Competitive Analysis** | Comparing products/options | `competitive-analysis.md` | Weighted scoring, red-team each option, include "do nothing" |
| **Technology Evaluation** | "Should I use X?" | `domain-strategies.md` (Software section) | Viability matrix, bus factor, lock-in, TRL classification |
| **Claim Verification** | "Is this true?" | `fact-checking.md` | Primary source hunt, lateral verification, circular source detection |
| **Fintech/Regulatory** | Regulations, compliance | `domain-strategies.md` (Fintech section) | Regulator-first hierarchy, temporal sensitivity |
| **Strategic Research** | C-suite analysis | All references (Maximum tier) | Full Pyramid, evolution narrative, micro-to-macro |
| **Skill Creation Research** | Research → skill | `failure-prevention.md` | TRL gate, actionability filter, expiration tagging |

## Anti-Patterns

- **Single-query research** — one search = one perspective = biased
- **Hypotheses after evidence** — anchoring is unfixable retroactively
- **Silently resolving contradictions** — preserve them; document both sides
- **Equating popularity with quality** — GitHub stars are participation trophies
- **Blog summaries over official docs** — always go to the source
- **Skipping pre-mortem** — "what if we're wrong?" is the most valuable question
- **Confusing likelihood with evidence quality** — tag both, separately
- **Stack Overflow as authority** — 58.4% obsolescence rate in answers
- **Skipping temporal tags** — every finding decays; tag when it expires
- **Launching biased sub-agents** — neutrally frame all prompts
- **Sequential sub-agents when parallel is possible** — launch in one message
- **Skipping QA** — hallucinations and circular sources are common failure modes

## Known Failure Patterns

Check these before delivery (→ `references/failure-prevention.md` for procedures):

| Pattern | Frequency | Prevention |
|---------|-----------|------------|
| Hallucinated packages (slopsquatting) | 5.2% closed-source, 21.7% open-source models | Verify every package/API reference exists |
| Deprecated-but-popular APIs | 68% of training data contains deprecated patterns | Check official docs for current version |
| Circular citations | Common in web content | Trace every claim to primary source |
| AI code security vulnerabilities | ~45% of AI-generated code | Security review for any code output |
| Multi-agent coordination failures | 41-86.7% in production settings | Structured collation, conflict resolution |

## Reference Files — When to Read

**Progressive loading**: Read SKILL.md first (you're here). Load references as each
phase demands. Standard tier may only need `pyramid-output.md` + `source-validation.md`.

### Core References

| Reference | Read At Phase | What It Provides |
|-----------|--------------|-----------------|
| `kill-gates.md` | Phase 1 | Topic worthiness assessment, scope refinement |
| `anti-anchoring.md` | Phase 2 | Competing hypotheses procedure, ACH matrix |
| `bias-debiasing.md` | Phase 2, 5 | 9 LLM biases with procedural checkpoints |
| `domain-strategies.md` | Phase 3 | 6 domain protocols with source hierarchies |
| `prompt-optimization.md` | Phase 3 | Sub-agent prompt templates, model selection |
| `source-validation.md` | Phase 4 | Type-specific quality checks, SIFT method |
| `fact-checking.md` | Phase 4 | IFCN principles, verification levels, triage |
| `evidence-synthesis.md` | Phase 5 | Triangulation, GRADE grading, confidence tagging |
| `expert-simulation.md` | Phase 6 | Multi-expert prompts, CIA SATs, Tree of Thoughts |
| `gap-analysis.md` | Phase 7 | Gap types, severity scoring, saturation detection |
| `pyramid-output.md` | Phase 8 | Pyramid Principle, MECE, SCR/SCQA templates |
| `executive-summary.md` | Phase 8 | Bold-bullet format, scanning test |
| `failure-prevention.md` | Phase 9 | 6-stage QA pipeline, known failure patterns |
| `temporal-validity.md` | Phase 9 | Domain decay rates, tagging procedure |
| `micro-to-macro.md` | Multi-level analysis | Granular → aggregate pattern |
| `competitive-analysis.md` | Comparing options | Weighted scoring, red-teaming, TCO |
| `worked-examples.md` | First time using skill | 3 complete walkthroughs with full output |

**By research type**:
- Technology evaluation → `competitive-analysis.md` + `source-validation.md` + `temporal-validity.md`
- Market research → `competitive-analysis.md` + `domain-strategies.md` + `micro-to-macro.md`
- Claim verification → `fact-checking.md` + `evidence-synthesis.md` + `source-validation.md`
- Strategic analysis → all references (Maximum tier)

## Quality Checklist

Before delivering ANY output:

- [ ] Tier assigned and phases completed accordingly
- [ ] Competing hypotheses generated BEFORE first search (depth matched to tier)
- [ ] Search types executed per tier (Standard: 2-3; Enhanced/Maximum: all 6)
- [ ] Sources validated with type-specific checks
- [ ] Every major claim has 2+ independent sources (or tagged as single-source)
- [ ] Confidence AND evidence quality tagged separately for each finding
- [ ] Contradictions preserved, not silently resolved
- [ ] Pre-mortem completed (Enhanced + Maximum tiers)
- [ ] Output follows Pyramid structure (SCR format, answer first)
- [ ] Temporal tags applied (knowledge_as_of, valid_until, review_triggers)
- [ ] QA spot-check passed (20% of claims verified against sources)
- [ ] Gaps and limitations explicitly documented

---

*McKinsey-Grade Research Engine v3.0*
*Built on: McKinsey frameworks + CIA SATs + PRISMA/GRADE/Denzin + LLM bias research*
*Source skills: Research Analyst + Deep Research Synthesizer + Deep Thinker*
