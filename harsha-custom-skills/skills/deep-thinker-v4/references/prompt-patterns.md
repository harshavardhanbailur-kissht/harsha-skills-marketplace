# Prompt Patterns: Deep Thinker v4.0

## Structured Disagreement Methodology

Replace generic multi-expert simulation with three forced alternatives:

### THE OBVIOUS (Mainstream Position)
- What the field's consensus would say
- Most commonly cited solution
- Lowest execution risk perception
- *Purpose*: Creates anchor to escape from

### THE CONTRARIAN (Genuine Alternative)
- Inverts 1–2 core assumptions of THE OBVIOUS
- Must be defensible within domain constraints
- Typically higher complexity or different trade-offs
- *Purpose*: Exposes hidden assumptions in obvious approach

### THE MINIMUM (Constraint-Respecting Alternative)
- Solves the same problem with fewest dependencies
- Often reveals unnecessary complexity
- Builds incrementally rather than redesigning
- *Purpose*: Tests whether full scope is truly required

**Why three forces genuine alternatives:** Single alternative feels oppositional. Three create a spectrum that forces reasoning about trade-offs rather than just picking "better."

---

## Anti-Anchoring Procedure (ACH Adapted)

Used in SCOPE and GROUND phases to escape initial framing:

1. **State Initial Hypothesis Explicitly**
   - "We assume the problem is: [X]"
   - "Our success metric is: [Y]"

2. **Forbid the Hypothesis**
   - "Assume [X] is wrong. What changes?"
   - "If [Y] is impossible, what becomes important?"

3. **List Inconsistencies with Forbidden Hypothesis**
   - Where does each assumption come from?
   - Which are constraints vs. preferences?

4. **Evaluate Alternatives Against Inconsistencies**
   - Does THE CONTRARIAN eliminate more inconsistencies?
   - Does THE MINIMUM expose false constraints?

---

## Phase-Transition Debiasing Checkpoints

### SCOPE → GROUND Checkpoint
- **Anchoring check**: Did we select one implementation too early?
- **Scope creep check**: Is the problem statement growing?
- **Constraint validation**: Which constraints are real vs. assumed?
- **Action**: Restate problem in 1 sentence. Compare to original framing.

### GROUND → DIVERGE Checkpoint
- **Completeness check**: Does our model predict edge cases?
- **Hidden assumption audit**: What would break our model?
- **Confirmation bias check**: Are we cherry-picking facts that fit?
- **Action**: Identify 2 facts that contradict our model. Explain how.

### DIVERGE → STRESS Checkpoint
- **Path convergence check**: Are all 3 alternatives becoming the same solution?
- **Optimization creep**: Are we solving the problem or optimizing the obvious?
- **Coverage check**: Do our 3 paths explore different dimension (speed/cost/risk)?
- **Action**: For each path, name the hidden trade-off it makes.

### STRESS → SYNTHESIZE Checkpoint
- **Brittleness audit**: Which assumptions will fail at scale?
- **Recovery narrative**: If chosen solution fails, what's the fallback?
- **Measurement alignment**: Do success metrics match what we're optimizing?
- **Action**: Write the pre-mortem narrative (see State Management).

---

## Red Teamer Role (Phase 4: STRESS)

Simulate an adversarial reviewer of your chosen solution:

**Activation Pattern:**
```
You are a senior engineer reviewing [solution] for [project] before deployment.
Your job is NOT to be helpful—it's to find the fatal flaw.
```

**Red Team Questions:**
- *On assumptions*: "Which of your 5 constraints will fail first under load?"
- *On scope*: "What did you NOT do? Is that a risk?"
- *On trade-offs*: "You gained [X]. What did you lose?"
- *On failure modes*: "This works until [scenario]. How do you recover?"

**Integration into EXECUTION_CHECKLIST:**
- Tag: `@red-team-review`
- Phase: STRESS (Phase 4)
- Produces: Mitigation strategies in FAILURE_MODES.md

---

## Chain-of-Thought in Analysis Context

For problem decomposition within each phase:

```
PROBLEM: [Concise restatement]
CONSTRAINTS: [Hard boundaries]
UNKNOWNS: [What we need to learn]
HYPOTHESIS: [Leading direction]
REASONING:
  1. [First inference]
  2. [Second inference]
  3. [Third inference]
CONFIDENCE: [High/Medium/Low] — Tag each inference
NEXT: [What question does this unlock?]
```

Adapted for analysis: use in GROUND phase to build models incrementally.

---

## Tree of Thoughts (DIVERGE Phase Structure)

Structured exploration of 3 paths from root problem:

```
ROOT: [Problem statement from GROUND]
├─ PATH A (THE OBVIOUS)
│  ├─ Design principle
│  ├─ Core trade-offs
│  └─ Risk vector
├─ PATH B (THE CONTRARIAN)
│  ├─ Inverted assumption
│  ├─ Complexity profile
│  └─ Hidden benefit
└─ PATH C (THE MINIMUM)
   ├─ Reduction principle
   ├─ Dependencies removed
   └─ Scaling risk
```

Each path is evaluated in parallel during DIVERGE, then stress-tested in STRESS.

---

## Thinking Budget & UltraThink Interaction

**Don't say:** "Think harder" or "Use more reasoning tokens."

**Instead, give structured procedures:**

- **Shallow thinking**: SCOPE + GROUND only (quick validation)
- **Medium thinking**: SCOPE + GROUND + DIVERGE (explore alternatives)
- **Deep thinking**: All 5 phases (rigorous analysis)

**UltraThink contract:**
- Allocate thinking tokens to GROUND phase (model-building)
- Allocate to STRESS phase (red-team simulation)
- Don't allocate to SCOPE (clarify requirements first)
- Reserved capacity for SYNTHESIZE if earlier phases reveal gaps

**Checkpoint pattern:** Each phase generates a file. Review before next phase. This maintains focus instead of open-ended thinking.
