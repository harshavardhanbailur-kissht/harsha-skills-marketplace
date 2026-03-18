# Anti-Anchoring & Competing Hypotheses — Mandatory Phase 2

## Why This Phase Cannot Be Skipped

Anchoring bias is the MOST resistant bias to mitigation. Research consistently shows:
- "Instructing models to forget earlier anchors does not mitigate anchoring effects"
- First impressions dominate subsequent evaluation regardless of instructions
- The ONLY effective countermeasure is collecting information from comprehensive
  angles BEFORE forming any conclusion

## The Competing Hypotheses Method

### Step 1: Generate 2-4 Genuinely Different Hypotheses

Before any search, generate hypotheses about what the answer MIGHT be:

**Rules:**
- Hypotheses must be genuinely different, not slight variations
- At least one must contradict the "obvious" answer
- At least one must be uncomfortable or counterintuitive
- They should cover different causal mechanisms, not just different conclusions

**Example — "What's the best frontend framework for a fintech app?":**
- H1: React — mature ecosystem, wide hiring pool, time-tested
- H2: Svelte — smaller bundle, simpler mental model, growing adoption
- H3: Server-rendered (Next.js) — SEO + performance, most "state" is server data
- H4: No framework — vanilla JS with Web Components, zero lock-in

**Example — "Should we enter the Indian PropTech market?":**
- H1: Yes — massive underserved market, regulatory modernization (RERA)
- H2: No — regulatory complexity, land record fragmentation, trust deficit
- H3: Conditionally — only specific verticals (fractional ownership) are viable
- H4: Too early — wait for SM-REIT framework to mature, then enter

### Step 2: Design Search Strategy Per Hypothesis

For EACH hypothesis, design specific searches that would:
1. **Support** this hypothesis (what evidence would make it true?)
2. **Disprove** this hypothesis (what evidence would make it false?)

This ensures search is NOT anchored to a single expected answer.

### Step 3: Evaluate Using Analysis of Competing Hypotheses (ACH)

The ACH insight: **The most likely hypothesis is the one with the LEAST
evidence AGAINST it, not the most evidence FOR it.**

Create a matrix:
```
| Evidence Item | H1 | H2 | H3 | H4 |
|---|---|---|---|---|
| Evidence A | C | I | C | I |
| Evidence B | I | C | C | I |
| Evidence C | C | C | I | C |
```
C = Consistent, I = Inconsistent, N = Neutral

The hypothesis with the fewest "I" (Inconsistent) marks is the most likely.

### Step 4: Diagnostic vs. Non-Diagnostic Evidence

**Diagnostic evidence**: Differentiates BETWEEN hypotheses
- "This evidence supports H1 but contradicts H2" = DIAGNOSTIC

**Non-diagnostic evidence**: Consistent with multiple hypotheses
- "This evidence is consistent with all hypotheses" = NON-DIAGNOSTIC

Focus analysis on DIAGNOSTIC evidence. Non-diagnostic evidence feels
confirming but doesn't help you choose between hypotheses.

## Common Anchoring Traps

1. **First-result anchoring**: The first search result anchors all subsequent evaluation
   → Mitigate: Vary search order across hypotheses

2. **User-provided anchoring**: When user says "I think X is best, research it"
   → Mitigate: Always generate competing hypotheses regardless of user framing

3. **Popularity anchoring**: Most-discussed option becomes default winner
   → Mitigate: Viability over popularity — smaller but better-maintained > larger but abandoned

4. **Recency anchoring**: Newest option assumed best
   → Mitigate: "Boring technology" test — proven often > novel

5. **Confirmation anchoring**: After finding supporting evidence, stop searching
   → Mitigate: Mandatory 6-type search REGARDLESS of early findings

## Empirical Evidence on Anchoring in LLMs

### Quantified Anchoring Effects (2024-2025 Research)
- LLMs show anchoring bias on 22-61% of questions depending on domain and model
  (Lou et al., 2025, Journal of Computational Social Science)
- Anchoring index of 0.37 — models retain ~37% of difference between low/high anchors
  (He et al., 2025). Compare: human anchoring index = 0.49 (Jacowitz & Kahneman)
- Mechanism: "shallow-layer acting" — bias operates at shallow computation levels
- **Critical finding**: Simple mitigation (CoT, Reasoning, Reflection) does NOT reduce
  anchoring in "expert anchoring" scenarios

### What This Means for This Skill
- Generating competing hypotheses BEFORE search is not optional — it's the ONLY
  effective countermeasure with empirical support
- Search order variation (don't search "expected winner" first) matters because
  first results anchor at shallow processing levels
- Instructing the model to "ignore" anchors does NOT work — only procedural
  alternatives (structured hypothesis evaluation) produce improvement

### Sycophancy as Anchoring to User Beliefs
- RLHF training actively AMPLIFIES sycophancy (Sharma et al., ICLR 2024)
- When user says "I think X is best", the model anchors to X
- Mitigation: Always generate competing hypotheses regardless of user framing
- Larger, reasoning-capable models show better resistance (EMNLP 2025)

### Multi-Agent Debate Reduces Anchoring
- Multiple agents debating improves accuracy from 50% to 98% on arithmetic tasks
  and from 76% to 88% on reasoning tasks (2023)
- Two debate rounds capture most gains; third round gives slight additional boost
- Specialized (heterogeneous) agents outperform identical agents by ~3.5%
- **Implication**: Sub-agent dispatch with genuine diversity of perspective is a
  proven debiasing mechanism

## Integration With Workflow

Phase 2 feeds directly into Phase 3 (Systematic Search):
- Each hypothesis generates specific search queries
- Search order varies per hypothesis (empirically validated as anchoring prevention)
- Evidence is tagged with which hypotheses it supports/contradicts
- Final synthesis uses ACH to determine most likely conclusion
- For Maximum tier: dispatch sub-agents as debate participants for debiasing
