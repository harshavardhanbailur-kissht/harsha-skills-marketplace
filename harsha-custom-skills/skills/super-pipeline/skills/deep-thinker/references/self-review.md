# Analysis Quality Review Reference

Patterns for self-critique that ensures analysis quality before completion.

## Table of Contents
- [Review Philosophy](#review-philosophy)
- [Quality Dimensions](#quality-dimensions)
- [Review Prompts](#review-prompts)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Review Philosophy

### Core Principles

1. **Genuine Criticism Required**: Force identification of at least 2 potential improvements, even for good work. Prevents rubber-stamping.

2. **Completeness Over Speed**: Every analysis area must be fully explored before moving on.

3. **External Perspective**: Review as if another Claude session will execute this with zero additional context.

4. **Evidence-Based Quality**: Every "complete" declaration must cite specific verification performed.

### The Self-Review Mindset

When reviewing your own analysis:
- Would a senior engineer find gaps?
- Would the executor have questions?
- Are there scenarios not considered?
- Is the rationale for decisions clear?

---

## Quality Dimensions

### 1. Completeness (40%)
- Are ALL aspects of the problem addressed?
- Is anything missing that should be there?
- Check each acceptance criterion individually.

### 2. Depth (30%)
- Is this surface-level or truly thorough?
- Are edge cases explored?
- Are alternatives considered?

### 3. Clarity (20%)
- Could someone else understand this without asking questions?
- Are decisions justified with rationale?
- Are file:line references specific?

### 4. Actionability (10%)
- Could an executor implement from this directly?
- Are steps specific enough?
- Are dependencies clear?

---

## Review Prompts

### Analysis Completeness Check

```markdown
## Completeness Review

### Analysis to Review
[INSERT ANALYSIS SECTION]

### Check Against Acceptance Criteria
For each criterion:
- [ ] Criterion 1: [ADDRESSED? HOW?]
- [ ] Criterion 2: [ADDRESSED? HOW?]
- [ ] Criterion 3: [ADDRESSED? HOW?]

### Gaps Identified
1. [GAP 1]: Why it matters, how to address
2. [GAP 2]: Why it matters, how to address

### Verdict
[ ] COMPLETE - All criteria met, no significant gaps
[ ] NEEDS MORE - Gaps identified above must be addressed
```

### Depth Check

```markdown
## Depth Review

### Questions a Senior Engineer Would Ask
1. [QUESTION 1]: [ANSWER IN ANALYSIS?]
2. [QUESTION 2]: [ANSWER IN ANALYSIS?]
3. [QUESTION 3]: [ANSWER IN ANALYSIS?]

### Edge Cases Considered?
- [ ] Happy path documented
- [ ] Error states documented
- [ ] Race conditions documented
- [ ] Boundary conditions documented

### Alternatives Explored?
- [ ] Multiple approaches documented
- [ ] Pros/cons for each
- [ ] Clear recommendation with rationale
```

### Executor Readiness Check

```markdown
## Executor Readiness Review

### Can Someone Execute From This?
For each implementation step:
- [ ] File location specified
- [ ] What to change is clear
- [ ] Why it's needed is explained
- [ ] Dependencies identified

### Questions an Executor Might Have
1. [QUESTION]: [ANSWERED IN ANALYSIS?]
2. [QUESTION]: [ANSWERED IN ANALYSIS?]

### Final Verdict
[ ] READY - Executor needs zero clarification
[ ] NOT READY - These questions need answers first: [LIST]
```

---

## Anti-Patterns to Avoid

### In Analysis

| Anti-Pattern | Example | Instead Do |
|--------------|---------|------------|
| Surface-level | "Handle errors appropriately" | Specify exact error types and recovery |
| Vague steps | "Update the component" | "In `src/auth/Login.tsx:45`, add..." |
| Missing rationale | "Use Option A" | "Use Option A because X, Y, Z" |
| Assumed context | "Use the existing pattern" | "Follow pattern in `src/utils/validators.ts:23`" |
| Skipped edge cases | Only happy path | Document all failure modes |

### In Self-Review

| Anti-Pattern | Why It's Wrong | Instead Do |
|--------------|----------------|------------|
| Rubber-stamping | Misses real issues | Force 2+ improvements minimum |
| Overconfidence | "This is complete" without checking | Verify against criteria explicitly |
| Premature completion | Rushing to finish | Quality over speed |
| Defensive review | Justifying rather than critiquing | Be genuinely critical |

---

## Quality Checklist

Before declaring any `.deep-think/` file complete:

```
[ ] Every acceptance criterion addressed explicitly
[ ] At least 2 potential improvements identified
[ ] All edge cases documented
[ ] All decisions have rationale
[ ] File:line references are specific
[ ] Executor could implement without questions
[ ] Senior engineer wouldn't find obvious gaps
```
