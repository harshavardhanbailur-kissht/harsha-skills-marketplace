---
name: deep-thinker-v4
description: Deep Thinker v4 — pure thinking mode. ONLY THINKS, no execution. Maximum cognitive depth. Creates persistent knowledge base in .deep-think/ that survives context compaction. Targets 6 specific failure modes: satisficing, memory loss, single-path exploration, confirmation bias, missed complexity, and executor-unfriendly output. Use when planning complex features, architectural decisions, before any significant implementation, when building foundations, or when explicitly asked to "think deeply", "ultrathink", "architect this", "deep dive", "plan thoroughly", "/think", "before we code", "analyze completely", "think through", or "comprehensive analysis". Sibling of the v1 deep-thinker skill — invoke this slug explicitly to test v4 behavior side-by-side.
---

# Deep Thinker v4.0

Pure thinking engine. Every instruction targets a specific cognitive failure mode.

| Aspect | Detail |
|--------|--------|
| **Purpose** | Think better than Claude would without this skill |
| **Output** | `.deep-think/` — analysis artifacts + agent-executable briefs |
| **Core Value** | Broader (DIVERGE), deeper (STRESS), more useful to executors (SYNTHESIZE) |
| **Pipeline** | Feeds into super-pipeline via ThinkingCompiler adapter |

## Why This Exists

Without it, Claude: (1) satisfices, (2) loses plans to compaction, (3) explores one path, (4) doesn't attack its own conclusions, (5) misses complexity, (6) produces executor-unfriendly output. Extended thinking helps #1. This skill fixes #2-#6.

## Core Rules

1. **NEVER write implementation code** — analysis, plans, pseudocode only
2. **NEVER rush** — thoroughness over speed, always
3. **ALWAYS write to `.deep-think/` files** — they survive compaction
4. **ALWAYS use maximum thinking depth** — ultrathink on everything
5. **NO execution** — a separate session handles that

## Complexity Gate (30 Seconds — Do This First)

Load `references/complexity-estimation.md` for the full framework.

| Level | Signals | Files | Refs Loaded |
|-------|---------|-------|-------------|
| **Trivial** | Single file, obvious fix | 0 (inline) | 0 |
| **Small** | One component, bounded | 3 | 2: self-review, task-decomposition |
| **Medium** | Multiple components, integration | 6 | 5: + complexity-estimation, failure-recovery, context-engineering |
| **Complex** | Cross-system, architectural | 8 | All 9 |

**4 heuristic questions:** (1) One file or many? (2) Security/data implications? (3) Reversible? (4) Would executor have questions? Bump up one level for each "yes" to 2/3/4.

**When in doubt, go deeper.** Overthinking costs tokens. Underthinking costs rework.

---

## The 5 Phases

```
SCOPE → GROUND → DIVERGE → STRESS → SYNTHESIZE
  |        |         |         |          |
 (#5)     (#1)      (#3)     (#4)       (#6)
 Finds    Prevents  Forces   Attacks    Produces
 real     premature multiple own        agent-ready
 complexity solutions paths   design    outputs
```

**Progressive writing rule:** Write and save each file BEFORE starting the next phase. Never hold analysis in working memory.

### Phase 1: SCOPE → writes OVERVIEW.md

Target: failure #5 (missed complexity). Verify the problem statement before designing.

Ask: (1) What's the REAL problem? (often different from what was asked) (2) What are we NOT solving? (3) What are the HARD constraints? (security, compliance, backwards compat, perf) (4) What's the blast radius if we get this wrong?

If your scope matches the request word-for-word, you haven't thought hard enough.
**Checkpoint:** "What would invalidate this scope?"

### Phase 2: GROUND → writes CURRENT_STATE.md

Target: failure #1 (satisficing). No theorizing without reading code first.

Do: (1) READ every affected file (mandatory) (2) Map ACTUAL data flow, not assumed (3) Identify existing patterns to follow or break (4) Document SURPRISES — things that aren't what you expected.

If nothing surprises you, you're not looking hard enough.

**Kill gate:** After reading code, reassess complexity. If simpler than scoped → DOWNGRADE (fewer files, skip deeper analysis).
**Checkpoint:** "State your current favorite approach. Now it's forbidden."

### Phase 3: DIVERGE → writes ARCHITECTURE.md

Target: failure #3 (single-path exploration). Forces genuinely different approaches, not cosmetic variations.

**Structured Disagreement** — three approaches by construction:

```
1. THE OBVIOUS: First solution that comes to mind (what Claude would produce WITHOUT the skill)
2. THE CONTRARIAN: If the obvious were forbidden, what would you do? (genuine innovation)
3. THE MINIMUM: Absolute smallest change that solves the problem (prevents over-engineering)
```

**For each approach, document ALL FOUR:**
- Strongest argument FOR (one sentence)
- Strongest argument AGAINST (one sentence)
- Confidence: VERIFIED (code evidence) / HIGH (pattern match) / MEDIUM (reasoning only) / LOW (assumption)
- Would fail if: [specific scenario making this the WRONG choice]

**Select one.** Rationale MUST address the AGAINST arguments. Document what was rejected and WHY — so executor doesn't revisit dead ends.

**Transition checkpoint:** "What evidence would change your selection?"

### Phase 4: STRESS → writes EDGE_CASES.md

Target: failure #4 (confirmation bias). Attack your own design.

**4a. Pre-Mortem (MANDATORY):** "It's 2 weeks post-deployment. This caused an incident. What happened?" Write 3 failure stories — narrative, not bullets. Each connects multiple linked failures into a causal chain revealing cascading failures tables miss.

**4b. Constraint Verification:** For EACH hard constraint from Phase 1: "Does the approach satisfy this? HOW specifically?" Forces checking, not assumption.

**4c. Systematic Edge Sweep:**

| Dimension | Normal | Boundary | Adversarial |
|-----------|--------|----------|-------------|
| **Input** | Valid data | Empty/max | Injection/malformed |
| **State** | Expected | Partially done | Corrupted |
| **Timing** | Normal | Concurrent | Timeout/race |
| **External** | All up | Degraded | Down/changed |

**4d. Single Biggest Risk** — one paragraph forcing prioritization.

**Transition checkpoint:** "What did the pre-mortem reveal that you'd prefer to ignore?"

### Phase 5: SYNTHESIZE → writes IMPLEMENTATION.md → EXECUTION_CHECKLIST.md (last)

Target: failure #6 (executor-unfriendly output). The executor is another Claude session.

**IMPLEMENTATION.md:** Micro-steps with file:line references, dependencies marked, patterns to follow.

**EXECUTION_CHECKLIST.md** — self-contained executor brief (adapter-compatible format):
```
CONFIDENCE:        Analysis [H/M/L] × Execution [H/M/L] — reason
CONTEXT:           Self-contained — executor needs nothing else
APPROACH:          Selected design + WHY (enables executor judgment calls)
STEPS:             Phased, with file:line refs + dependency markers
RISKS:             Pre-mortem findings — specific failure modes to watch
SKILLS:            Which skills to activate per phase
KNOWN GAPS:        Classified: No-Regrets | Options | Blockers
```

**Complex only:** Also write OPTIMIZATIONS.md and CREATIVE_IDEAS.md before EXECUTION_CHECKLIST.

---

## File Output

| File | Phase | Content |
|------|-------|---------|
| `OVERVIEW.md` | 1-SCOPE | Scope, constraints, blast radius |
| `CURRENT_STATE.md` | 2-GROUND | What exists, surprises, patterns |
| `ARCHITECTURE.md` | 3-DIVERGE | 3 approaches, selection, rationale |
| `EDGE_CASES.md` | 4-STRESS | Pre-mortem, constraints, attack surface |
| `IMPLEMENTATION.md` | 5-SYNTHESIZE | Micro-steps with file:line |
| `OPTIMIZATIONS.md` | Complex only | Performance/quality refinements |
| `CREATIVE_IDEAS.md` | Complex only | Beyond requirements |
| `EXECUTION_CHECKLIST.md` | 5-SYNTHESIZE | Self-contained executor brief |

## Self-Reflection (Max 2 Iterations)

After all files, run adversarial self-review: (1) "Could the executor build with ZERO questions?" (2) "Unmitigated critical risks from pre-mortem?" (3) "Does ARCHITECTURE selection survive its AGAINST arguments?" (4) "Does every file change an executor decision?" (So What? test) (5) "Would I bet my reputation on this?"

Gap found → **surgical update** to specific file only. After 2 iterations, remaining gaps → EXECUTION_CHECKLIST.md KNOWN GAPS. `Fix or flag — never silently accept gaps.`

## Expert Selection

Match to domain — not generic panels. Select 2-4 experts with natural tension. Always include a **Red Teamer** (finds how the design breaks). Experts enrich Phases 2-4 but do NOT replace Structured Disagreement — those are three approaches, not three opinions. Load `references/skill-integration.md` for skill annotations.

## Success Criteria (Tiered)

**All levels:**
- [ ] Complexity assessed, correct file count produced
- [ ] Self-reflection completed (1-2 iterations)
- [ ] Gaps fixed or flagged — none silently accepted

**Small+:**
- [ ] OVERVIEW has scope boundaries and hard constraints
- [ ] ARCHITECTURE has 3 genuinely different approaches with confidence tags
- [ ] EDGE_CASES has at least one pre-mortem failure story

**Medium+:**
- [ ] CURRENT_STATE has file:line references and documented surprises
- [ ] Constraint verification table complete
- [ ] EXECUTION_CHECKLIST has two-dimensional confidence + skill annotations

**Complex:**
- [ ] 3 narrative pre-mortem stories with cascading causes
- [ ] KNOWN GAPS classified (No-Regrets / Options / Blockers)
- [ ] Executor can build with ZERO questions AND no unmitigated critical risks

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Agreement Theater | 3 "approaches" = same idea | Obvious/Contrarian/Minimum can't converge by construction |
| Risk Lists | Misses cascading failures | Pre-mortem narratives: "what DID go wrong" |
| Template Filling | 8 shallow files | Success = thinking quality, not file count |
| Anchoring | First idea dominates | GROUND→DIVERGE checkpoint: "favorite approach is now forbidden" |
| Optimism Bias | "This should work" | STRESS→SYNTHESIZE checkpoint: "what would you prefer to ignore?" |

## Example

**User:** "Add mobile number login alongside email"

**SCOPE:** Real problem = multi-identifier auth. Hard constraints: existing sessions can't break, OTP rate limits, country codes. Blast radius: auth is foundational.

**DIVERGE:**
- OBVIOUS: Parallel OTP (email+SMS), shared session → Confidence: HIGH → Fails if: SMS unreliable in target markets
- CONTRARIAN: Universal identifier with smart routing → Confidence: MEDIUM → Fails if: ambiguous identifiers (numeric emails?)
- MINIMUM: Phone as alias, reuse email OTP infra + SMS adapter → Confidence: VERIFIED (pattern exists in codebase) → Fails if: users want phone-only accounts

**STRESS Pre-Mortem:** "Week 2. Rural India. SMS OTP delivery: 73%. Retry logic assumes 30s delivery but carriers delay 2+ min. Users hammer resend → rate limiting triggers → 400% support spike."

**Executor brief:** Analysis HIGH × Execution MEDIUM. Known gap (Options): SMS delivery reliability unverified for target markets.

---

*Deep Thinker v4.0 — Cognitive failure mode compensation engine*
*SCOPE → GROUND → DIVERGE → STRESS → SYNTHESIZE*

**Foundations:** Klein's Pre-Mortem, Heuer's Analysis of Competing Hypotheses, McKinsey Pyramid Principle, Kahneman's Outside View, Research-Analyst Procedural Debiasing
