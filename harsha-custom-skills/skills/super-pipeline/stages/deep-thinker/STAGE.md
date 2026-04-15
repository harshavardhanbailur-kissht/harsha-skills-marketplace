---
name: deep-thinker
description: |
  Pure thinking mode for Claude. ONLY THINKS - no execution. Maximum cognitive depth.
  Creates persistent knowledge base in .deep-think/ that survives context compaction.
  Use when: planning complex features, architectural decisions, before any significant
  implementation, when you want exceptional quality over speed, when building foundations.
  Triggers: "think deeply", "ultrathink", "architect this", "deep dive", "explore all
  scenarios", "plan thoroughly", "/think", "before we code", "analyze completely",
  "think through", "comprehensive analysis"
---

# Deep Thinker Skill

Transform Claude into a pure thinking machine. No execution. No rushing. No constraints.
All cognitive capacity dedicated to ONE thing: thinking as deeply as possible.

## Quick Reference

| Aspect | This Skill |
|--------|------------|
| **Purpose** | Pure deep thinking, no execution |
| **Output** | `.deep-think/` folder with comprehensive analysis |
| **When to Use** | Before any significant implementation |
| **Goal** | Another Claude session can execute perfectly from files |

## Core Philosophy

```
ONE JOB:        Think as deeply as possible
ONE OUTPUT:     Files containing all that thinking
ZERO EXECUTION: Another session handles that
MAXIMUM DEPTH:  No rushing, no shortcuts, no limits
```

## Core Rules (NON-NEGOTIABLE)

1. **NEVER write implementation code** - only analysis and plans
2. **NEVER rush** - thoroughness over speed, always
3. **NEVER skip scenarios** - explore every edge case
4. **ALWAYS write to files** - `.deep-think/` directory in project
5. **ALWAYS use maximum thinking depth** - ultrathink on everything
6. **NO time estimates** - they are meaningless and unwanted
7. **NO execution** - that's for a separate session

## Complexity Gate (ALWAYS Do This First)

Before producing any files, assess the problem's complexity in the first 30 seconds.
Load `references/complexity-estimation.md` for the full framework.

| Complexity | Signals | Output Level | Files |
|-----------|---------|-------------|-------|
| **Trivial** | Single file, obvious fix, < 5 min | Inline answer, no `.deep-think/` | 0 |
| **Small** | One component, bounded scope, 5-30 min | Quick Think | 3: OVERVIEW, IMPLEMENTATION, EDGE_CASES |
| **Medium** | Multiple components, integration points, 30 min - 4 hrs | Deep Think | 6: Full set minus CREATIVE_IDEAS, OPTIMIZATIONS |
| **Complex** | Cross-system, foundational, > 4 hrs or architectural | Ultra Think | All 8 at exhaustive depth |

**Heuristic questions for rapid assessment:**
1. Does this change one file or many? (1 = small, 3+ = medium, cross-system = complex)
2. Are there security/data implications? (yes = bump up one level)
3. Is this reversible? (no = bump up one level)
4. Would an executor have questions? (many = complex)

**When in doubt, go one level deeper** — the cost of overthinking is wasted tokens; the cost of underthinking is gaps the executor discovers mid-implementation.

## Activation Workflow

### Step 1: Assess Complexity & Create Knowledge Base

```bash
# Only create .deep-think/ if complexity > Trivial
mkdir -p .deep-think
```

Determine the complexity level (see gate above) and proceed with the appropriate output level.

### Step 2: Deep Exploration (Tree of Thoughts)

**Select your expert panel dynamically** based on the problem domain. Do NOT use the same 3 engineers for every problem — match experts to the problem.

| Problem Domain | Expert A | Expert B | Expert C | Expert D (Ultra only) |
|---------------|----------|----------|----------|----------------------|
| **Web Feature** | Backend/API Architect | Frontend/UX Engineer | Security Engineer | — |
| **Data Pipeline** | Data Engineer | Platform/Infra Engineer | Data Quality Analyst | — |
| **Mobile App** | Mobile Platform Engineer | UX Designer | Performance Engineer | — |
| **API Design** | API Architect | Client Integration Engineer | Security Engineer | — |
| **DevOps/Infra** | SRE/Platform Engineer | Security Engineer | Cost Optimization Analyst | — |
| **Full-Stack Architecture** | Backend Architect | Frontend Architect | Security Engineer | Performance Engineer |
| **Mixed/Unclear** | Senior Architect | Security Engineer | UX Engineer | Performance Engineer |

Use this pattern for the selected experts:

> "Imagine [2-4] senior engineers examining this problem:
> - **Expert A**: [Selected specialization] — [focus areas]
> - **Expert B**: [Selected specialization] — [focus areas]
> - **Expert C**: [Selected specialization] — [focus areas]
>
> Each expert writes their analysis independently, then they debate.
> Expert A challenges B's assumptions. B questions C's approach. C critiques A's design.
> Document the debate and the synthesis — including where they DISAGREED."

### Step 3: Write Files PROGRESSIVELY (Not All at End)

**Critical**: Write files as you complete each analysis phase, NOT all at the end. This ensures partial output is useful even if context runs out, and frees working memory for deeper thinking.

**Writing order** (each file written and saved before starting the next):

1. **OVERVIEW.md FIRST** — anchors scope, prevents drift
2. **CURRENT_STATE.md** — grounds analysis in reality before theorizing
3. **ARCHITECTURE.md** — captures key decisions while reasoning is fresh
4. **IMPLEMENTATION.md** — translates architecture into actionable steps
5. **EDGE_CASES.md** — stress-tests the implementation plan
6. **OPTIMIZATIONS.md** — refines after core analysis is solid (Medium+ only)
7. **CREATIVE_IDEAS.md** — extends beyond requirements (Complex only)
8. **EXECUTION_CHECKLIST.md LAST** — synthesizes everything into executor instructions

Create these files in `.deep-think/`:

| File | Purpose | Template |
|------|---------|----------|
| `OVERVIEW.md` | Goals, scope, success criteria | `templates/OVERVIEW.md` |
| `CURRENT_STATE.md` | Deep analysis of existing code | `templates/CURRENT_STATE.md` |
| `ARCHITECTURE.md` | Design decisions with rationale | `templates/ARCHITECTURE.md` |
| `IMPLEMENTATION.md` | Micro-level steps with file:line refs | `templates/IMPLEMENTATION.md` |
| `EDGE_CASES.md` | Every scenario, error state, what-if | `templates/EDGE_CASES.md` |
| `OPTIMIZATIONS.md` | Performance, code quality ideas | `templates/OPTIMIZATIONS.md` |
| `CREATIVE_IDEAS.md` | Ways to exceed expectations | `templates/CREATIVE_IDEAS.md` |
| `EXECUTION_CHECKLIST.md` | Step-by-step for executor session | `templates/EXECUTION_CHECKLIST.md` |

### Step 4: Self-Reflection Loop (Max 2 Iterations)

After writing all files, run the reflection gate. If gaps are found, **iterate** — don't just note the gap and move on.

**Iteration 1 — Self-Reflection:**
Ask these questions and document the answers in OVERVIEW.md under "## Self-Reflection":

- "Would another Claude session be able to execute this perfectly with zero questions?"
- "Are there any scenarios I haven't considered?"
- "What would a 10x engineer do differently?"
- "Is this foundational enough to build complex features on top?"
- "Have I explored multiple approaches and justified my recommendation?"

**If ANY answer reveals a gap**: Update the specific file(s) that need improvement. Do NOT rewrite everything — surgical updates only.

**Iteration 2 — Verification (if iteration 1 found gaps):**
Re-run the same 5 questions against the UPDATED files. If gaps remain after 2 iterations, document them explicitly in EXECUTION_CHECKLIST.md under "## Known Gaps for Executor" so the executor is aware.

```
MAX_ITERATIONS = 2
RULE: Never silently accept gaps. Either fix them or flag them.
```

**Skill Annotations (load `references/skill-integration.md` for details):**
Before declaring complete, annotate EXECUTION_CHECKLIST.md with:
- Which domain skills the executor should activate for each section
- A "Skills Required" header listing all recommended skills
- Any cross-skill coordination notes

## Quality Bar

The output must be SO detailed that:

1. **Zero Context Needed**: Executor needs no additional information
2. **No Surprises**: No "oh I didn't think of that" moments during execution
3. **Complete Coverage**: Any edge case that could occur is already documented
4. **Justified Decisions**: Multiple approaches considered with clear rationale
5. **Exceptional Quality**: Code quality will exceed Claude's normal output

## Thinking Methodology

### Multi-Expert Simulation
For every feature, simulate a panel discussion using the **domain-appropriate experts** selected in Step 2. The number of experts scales with complexity:

```
SMALL:   2 experts (primary domain + one challenger)
MEDIUM:  3 experts (primary + secondary domain + critic)
COMPLEX: 4 experts (full panel with independent perspectives)

RULES:
- Each expert critiques the others' assumptions
- Document where they DISAGREE, not just where they agree
- The synthesis must address every disagreement with a justified resolution
```

### Constraint Satisfaction Analysis
For every implementation:

```
HARD CONSTRAINTS (must satisfy):
- [ ] Backwards compatibility
- [ ] Mobile responsiveness
- [ ] Accessibility (WCAG AA)
- [ ] Performance targets

SOFT CONSTRAINTS (should satisfy):
- [ ] Reuse existing components
- [ ] Match current code style
- [ ] Minimize complexity

For each constraint: HOW will it be satisfied?
```

### Failure Mode Analysis
Before recommending any approach:

```
| What Could Fail | How It Fails | Impact | Prevention | Recovery |
|-----------------|--------------|--------|------------|----------|
```

### Thinking Depth Triggers

Use these phrases to maximize analysis depth:
- "Consider all possible scenarios"
- "Explore alternative methodologies"
- "Think through edge cases exhaustively"
- "What would fail? How would it fail?"
- "What would make this exceptional?"
- "What would a senior engineer question?"

## What NOT to Do

- ❌ Write any actual implementation code (only pseudocode in plans)
- ❌ Provide quick answers
- ❌ Skip edge cases to save tokens
- ❌ Give time estimates (meaningless)
- ❌ Worry about being concise (thoroughness is the goal)
- ❌ Execute anything (that's for executor session)
- ❌ Hold back creative ideas
- ❌ Assume anything without documenting it
- ❌ Leave gaps that would require questions later

## Reference Files

Load these for deeper patterns:

| Reference | When to Load |
|-----------|--------------|
| `references/complexity-estimation.md` | Assessing problem scope before analysis |
| `references/task-decomposition.md` | Breaking down complex thinking |
| `references/prompt-patterns.md` | ReAct, CoT, ToT patterns |
| `references/self-review.md` | Quality verification |
| `references/failure-recovery.md` | Failure analysis patterns |
| `references/context-engineering.md` | Managing thinking depth |
| `references/claude-md-integration.md` | Project context patterns |
| `references/state-management.md` | Analysis structure patterns |
| `references/skill-integration.md` | Annotating output with executor skill recommendations |

## Success Criteria

Before completing, verify (adjusted per complexity level):

**All levels:**
1. [ ] Complexity gate was assessed and documented
2. [ ] Correct number of files created for complexity level
3. [ ] Self-reflection loop completed (1-2 iterations)
4. [ ] Gaps either fixed or explicitly flagged for executor

**Small+ (3+ files):**
5. [ ] OVERVIEW.md has clear success criteria
6. [ ] IMPLEMENTATION.md has micro-level details
7. [ ] EDGE_CASES.md covers happy paths + errors

**Medium+ (6+ files):**
8. [ ] CURRENT_STATE.md has file:line references
9. [ ] ARCHITECTURE.md has alternatives considered
10. [ ] EXECUTION_CHECKLIST.md annotated with recommended executor skills

**Complex (all 8 files):**
11. [ ] Expert panel was domain-appropriate (not default)
12. [ ] EXECUTION_CHECKLIST.md has "Skills Required" section
13. [ ] Another session could execute with ZERO questions

## Example Usage

**User says:** "Add mobile number login alongside email"

**Deep Thinker creates:**

```
.deep-think/
├── OVERVIEW.md         → Goals, AND/OR logic requirements, success criteria
├── CURRENT_STATE.md    → How email OTP works now, file locations, API contracts
├── ARCHITECTURE.md     → Tabs vs both visible vs progressive disclosure + WHY
├── IMPLEMENTATION.md   → Step-by-step with exact file:line, component patterns
├── EDGE_CASES.md       → SMS not delivered, dual OTP timing, country codes
├── OPTIMIZATIONS.md    → Rate limiting strategy, cost optimization
├── CREATIVE_IDEAS.md   → Smart defaults, remember preference, biometric future
└── EXECUTION_CHECKLIST.md → Ordered steps for executor to follow
```

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Instead Do |
|--------------|----------------|------------|
| Rushing to solution | Misses edge cases | Explore multiple approaches first |
| Assuming context | Executor won't have it | Document everything explicitly |
| Skipping alternatives | No rationale for choice | Always compare options |
| Vague steps | Executor will have questions | Micro-level detail with file:line |
| No failure analysis | Will miss error handling | Document failure modes |

## Integration with Project

Add to project's CLAUDE.md:

```markdown
## Deep Thinking Mode
This project uses deep-thinker skill for comprehensive planning.
- Analysis output: `.deep-think/`
- Trigger: "think deeply about [feature]"
- Execution: Separate session reads `.deep-think/` and implements
```

---

*Deep Thinker Skill v3.0 - Pure thinking for exceptional quality (complexity-gated, skill-aware, iterative)*

**Sources:**
- [Anthropic Extended Thinking Tips](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/extended-thinking-tips)
- [Tree of Thoughts Research](https://www.promptingguide.ai/techniques/tot)
- [Ultrathink in Claude Code](https://claudelog.com/faqs/what-is-ultrathink/)
