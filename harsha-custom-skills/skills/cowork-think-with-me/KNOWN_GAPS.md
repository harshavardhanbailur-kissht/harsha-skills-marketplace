# Known Gaps

## 1. Auto-Trigger Not Implemented

The skill currently activates only on explicit triggers. Auto-triggering on build-shaped requests (e.g., "write a PRD") was deferred as opt-in. To implement: add a classifier that detects build requests and offers to activate think-with-me before proceeding. This would need a CLAUDE.md flag like `think-with-me-auto-trigger: true`.

**Impact**: Users must remember to invoke the skill. They might default to "write a PRD" and miss the exploration step.

## 2. No Eval Suite

The skill lacks a formal eval suite (evals.json per skill-creator format). Ideally, 8-10 eval cases would test: proper reframing (including binary framing detection), axis identification count, option generation count, ranking quality (no ties without justification), cross-questioning when overridden (including compound overrides), yield-with-friction compliance, compaction recovery, reversal handling, and migration/pricing decision coverage.

**Impact**: Can't benchmark improvements or verify regressions when modifying the skill.

## 3. Multi-Session Handoff Not Tested

The compaction-resilience design (SESSION_STATE.md + file-based recovery) is specified but hasn't been tested across actual compaction events. Edge cases like "compaction happens mid-option-enumeration" or "user resumes after 2 days" need real-world validation.

**Impact**: Recovery might require manual intervention in edge cases.

## 4. Cross-Questioning Tone

The cross-questioning protocol specifies tone calibration, but actual tone depends heavily on Claude's current behavior. The "one targeted question" might feel too mild or too pointed depending on context. This needs user feedback tuning.

**Impact**: First few sessions may need user feedback to calibrate the right tone.

## 5. Coverage Estimation

The yield-with-friction protocol estimates "coverage percentage" but this is inherently subjective. The formula in yield-with-friction.md provides a framework, but real coverage is unknowable — you can't measure what you haven't explored. For compound decisions, decision-coverage (N of M axes resolved) is more honest than process-coverage.

**Impact**: Coverage percentages should be treated as rough signals, not precise measurements.

## 6. Integration with Other Skills

The skill doesn't yet have explicit handoff protocols to other skills. For example: after think-with-me produces a decision doc, the user might want to invoke `create-prd` or `write-spec` using the decision doc as input. This handoff is manual.

**Impact**: Users need to manually copy decision doc content into subsequent skill invocations.

## 7. Compound Decision Trees Not Fully Implemented

The skill now detects compound decisions (migration, multi-phase rollouts) and has axis templates for them. However, full DECISION_TREE.md generation (mapping which sub-decisions gate others, with conditional branching and trigger conditions) is described in stress tests but not yet implemented as a template or reference file.

**Impact**: For complex migrations, the PM must mentally track decision dependencies. A future DECISION_TREE.md template would automate this.

## 8. Stakeholder Impact Matrix

For compound decisions affecting the same stakeholder across multiple axes simultaneously, a full stakeholder-impact matrix (stakeholder × axis × combined risk) would surface compounding effects. Currently described in stress tests but not yet a template.

**Impact**: Compounding effects on individual stakeholders may be missed when analyzing axes independently.

---

## Resolved Gaps (from stress testing, 2026-05-02)

These gaps were identified during stress testing and fixed in v1.1:

- ~~Reference files not indexed in SKILL.md~~ → Added full reference/template index with "Load When" conditions
- ~~No pricing/migration axis templates~~ → Added to `references/axis-enumeration.md`
- ~~Multi-axis skip ambiguity in cross-questioning~~ → Added compound override handling
- ~~Missing templates for SESSION_STATE, PROBLEM, EXPERT_PANEL~~ → Created all 3
- ~~Binary framing doesn't trigger reframe~~ → Added binary framing trigger to Phase 1
- ~~Execution decisions not handled in Phase 1~~ → Added execution decision reframe
- ~~No partial-completion format in SESSION_STATE~~ → Added `[~]` marker
- ~~No reversal protocol~~ → Added full reversal protocol
- ~~Expert panel missing pricing/migration/finance roles~~ → Added 3 new experts (#13-15)
- ~~Protocol collision (yield + cross-question)~~ → Added priority rule
- ~~Ranking template missing ops fields~~ → Added timeline/transition cost/reversibility/blast radius
- ~~No pre-ranking rejection format~~ → Added to cross-questioning protocol
- ~~Phase 6 not decision-type-aware~~ → Phase 6 now produces EXECUTION_PLAN.md for migrations
- ~~Steel-man the loser ambiguous~~ → Clarified: steel-man rank 2-3, not worst
- ~~Swing weight vs. veto criteria unclear~~ → Added binary criteria = veto gates guidance
