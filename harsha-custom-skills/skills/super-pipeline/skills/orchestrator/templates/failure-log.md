# Failure Log Template

Use this template to document failed approaches—valuable negative knowledge
that prevents future executors from repeating the same investigation.

---

# Failed Approach: [Brief Description]

**ID**: FAIL-[number]
**Date**: [YYYY-MM-DD]
**Project**: [Project name]
**Related Task**: [Task reference]

---

## What We Tried

### Approach Description
[Detailed description of the approach attempted]

### Implementation
[How it was implemented—code snippets, configuration, steps taken]

```
[Code or configuration if relevant]
```

---

## Why We Tried It

### Expected Benefit
[What we hoped to achieve]

### Hypothesis
[The assumption or theory behind this approach]

### Alternatives Considered
[Other options we could have tried instead]

---

## What Happened

### Observed Behavior
[Factual description of what occurred]

### Error Messages
```
[Actual error output if any]
```

### Symptoms
[How the failure manifested]

---

## Why It Didn't Work

### Immediate Cause
[What directly caused the failure]

### Root Cause
[The fundamental reason this approach cannot work]

### Contributing Factors
[Conditions that enabled or amplified the failure]

---

## What We Learned

### Key Insight
[The actionable takeaway from this failure]

### Conditions for Failure
[When would this approach fail? Specific constraints it violates]

### Conditions Where It Might Work
[Are there scenarios where this approach could work? If so, what's different?]

---

## Alternative Chosen

### What We Did Instead
[The approach that was used instead]

### Why This Works
[Why the alternative succeeds where the failed approach didn't]

### Reference
[Link to implementation or ADR documenting the successful approach]

---

## Prevention

### Warning Signs
[How to recognize if someone is about to try this approach]

### Recommendation
[What to tell someone considering this approach]

---

## Time Investment

**Time Spent on Failed Approach**: [hours]
**Value of Documenting**: [Saves X hours for future executor]

---

## Related

- [Link to related failures]
- [Link to successful approach]
- [Link to relevant ADR]

---

## Tags

[failure] [topic] [technology] [antipattern]
