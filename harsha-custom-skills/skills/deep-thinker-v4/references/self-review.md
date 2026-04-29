# Self-Review: Quality Gates & Confidence Tagging

## Review Philosophy

**Genuine Criticism Over Polish**: Catch logical gaps, missing scenarios, and faulty assumptions before review. Don't waste time on grammar.

**Completeness Before Speed**: A thorough review of one version beats a shallow review of many. Better to spend 15 min finding a critical gap than 60 min reviewing everything and missing it.

**Confidence Over Certainty**: Mark what you know vs what you're inferring. Let executor decide confidence tolerance.

## Quality Dimensions (Weighted)

| Dimension | Weight | Definition |
|-----------|--------|-----------|
| Completeness | 40% | All files affected identified, all scenarios covered, no gaps that block execution |
| Depth | 30% | Each decision is reasoned, trade-offs are explained, edge cases are addressed |
| Clarity | 20% | Steps are unambiguous, rationale is explicit, executor doesn't need to guess |
| Actionability | 10% | Executor can take next action immediately without rework or clarification |

**Target**: Score 80+ on all dimensions before SYNTHESIZE. If any dimension <70, identify and fix gap.

## Confidence Tagging System

Apply to architecture decisions, API choices, and path validation:

**VERIFIED**: Code evidence, tests passing, production validated.
- Example: "Session storage uses distributed cache (VERIFIED: Redis connection pooling tested)"

**HIGH**: Pattern matches known working solution, multiple sources confirm approach.
- Example: "Mobile auth via OAuth (HIGH: industry standard, used by Stripe, Facebook)"

**MEDIUM**: Reasoning is sound but untested, or inference from domain knowledge.
- Example: "Migration tool can handle 100K records (MEDIUM: linear complexity, not tested at scale)"

**LOW**: Assumption, educated guess, or best-effort estimation.
- Example: "API will support webhook retries (LOW: assumption, need to verify with vendor)"

## Two-Dimensional Confidence for Executor Brief

Format each major decision as:
```
[Decision Name]
Analysis Confidence: [VERIFIED/HIGH/MEDIUM/LOW]
Execution Confidence: [VERIFIED/HIGH/MEDIUM/LOW]
Rationale: [why each dimension rates as it does]
```

**Analysis Confidence**: How sure are you the decision is sound?
**Execution Confidence**: How sure are you the executor can implement it without blockers?

Example: "Feature flag migration: Analysis Confidence HIGH (standard pattern), Execution Confidence MEDIUM (requires coordination with DevOps, timeline uncertain)"

## "So What?" Test

For every file change in SYNTHESIZE brief:
1. Does this file change an executor decision? (YES or NO)
2. If NO, remove it. It's extra.
3. If YES, can executor understand why in <30 seconds? (YES or NO)
4. If NO, clarify the "so what?"

**Anti-pattern**: "Update login.ts because auth now uses OAuth" (missing the SO WHAT).
**Fixed version**: "Update login.ts: replace email input with OAuth button to reduce form friction (per user research showing 40% abandonment on email+password)."

## Five Adversarial Review Questions

Before finalizing SYNTHESIZE, ask:
1. **Could this break existing functionality?** What backwards compatibility is at risk? Rollback plan clear?
2. **Are there hidden dependencies?** What other systems/teams are affected? Notification plan?
3. **Can this actually be done as written?** Are all tools/permissions/access available? Any blockers?
4. **What am I missing?** What scenario would make me regret this decision? Any unstated assumptions?
5. **Is the simplest path chosen?** Could this be smaller? Faster? Lower risk? Why not?

If you can't answer all five clearly, go back to DIVERGE and stress-test alternatives.

## Anti-Patterns to Flag

- **Vague Steps**: "Update auth flow" → NO. "Replace email login form with OAuth button in login.tsx line 45-52" → YES.
- **Missing Rationale**: "Add feature flag" → NO. "Add feature flag for gradual rollout; we need to catch 10% user errors before full deploy" → YES.
- **Surface-Level Analysis**: "This should work" → NO. "Tested with 10K concurrent logins, response time <500ms at p99" → YES.
- **Template Filling**: Checking boxes without thought. Resist. Genuine criticism only.
- **Assumption Hiding**: "We'll use Redis" without mentioning "assuming Redis cluster is available" → Fix it.

## Debiasing Checkpoints at Phase Transitions

**After SCOPE** (before GROUND):
- Did I actually understand the problem? Can I restate it in one sentence to someone else?
- Am I solving the right problem or the stated problem?

**After GROUND** (before DIVERGE):
- Did I test my understanding with real code? Am I reading actual behavior or imagining it?
- What assumption could be most wrong?

**After DIVERGE** (before STRESS):
- Am I anchored to my first idea? Did I genuinely evaluate alternatives or defend my favorite?
- Which alternative would I choose if I didn't know my first idea?

**After STRESS** (before SYNTHESIZE):
- Did I find any scenario that would make me regret this decision? Did I fully understand it?
- Is my confidence tag honest? Am I downplaying uncertainty?

**Before Executor Brief** (SYNTHESIZE):
- Can executor make the right decision without my explanation? If NO, explanation is too terse.
- Did I mark uncertainty clearly? Would executor be surprised by a blocker?

## Quality Score Rubric

**40-Completeness**: Count major code changes needed. Do you have a file for each? ≤2 files missing → PASS.
**30-Depth**: For each file, do you have 2+ alternative approaches considered? Trade-offs documented? YES → PASS.
**20-Clarity**: Could a competent engineer execute this in 1 sprint without asking questions? YES → PASS.
**10-Actionability**: Does executor have next action <5 words? YES → PASS.

Minimum to SYNTHESIZE: 80/100 score, all CRITICAL review questions answered, zero LOW confidence on architecture decisions.
