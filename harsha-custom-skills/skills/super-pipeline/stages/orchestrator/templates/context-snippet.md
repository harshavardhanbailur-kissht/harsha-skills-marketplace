# Context Snippet Template

Use this template when handing off work between sessions or executors.
Keep under 500 tokens—this is the minimum context needed to continue work.

---

# Context: [Task/Project Name]

**Updated**: [YYYY-MM-DD HH:MM]
**Author**: [Who wrote this snapshot]
**For**: [Intended recipient—next session, specific person, any executor]

---

## Goal

[One sentence: what we're trying to achieve. This is the north star.]

---

## Current State

### Completed
- [x] [Completed item 1]
- [x] [Completed item 2]

### In Progress
- [ ] [Current work item] ← **START HERE**

### Not Started
- [ ] [Remaining item 1]
- [ ] [Remaining item 2]

---

## Key Decisions Made

| Decision | Rationale | Reference |
|----------|-----------|-----------|
| [Decision 1] | [Why] | [ADR link if any] |
| [Decision 2] | [Why] | |

---

## What Didn't Work (Critical Context)

- **[Attempted approach]**: [Why it failed, so next executor doesn't repeat]

---

## Next Steps

**Immediate** (do first):
1. [Specific next action]

**Then**:
2. [Following action]
3. [Following action]

---

## Blockers

| Blocker | Waiting On | Expected Resolution |
|---------|------------|---------------------|
| [Blocker] | [What/who] | [When/how] |

*None* if no blockers.

---

## Critical References

- **Code**: [filepath or repo link]
- **Docs**: [relevant documentation]
- **Ticket**: [issue tracker link]
- **ADR**: [decision record if relevant]

---

## Environment/Setup

[Any non-obvious setup required. Skip if standard.]

```bash
# Quick start commands if helpful
```

---

## Questions for Next Executor

[Any open questions that should be addressed or decisions that need input]

---

## Warnings

[Anything that could trip someone up. Gotchas, known issues, time-sensitive items.]
