# Resolution Decision Audit Trail

> Every merge resolution decision is logged here for forensic review, reversal, and learning.
> Read this file to understand why each conflict was resolved the way it was.

**Started**: {ISO-8601 timestamp}
**Mode**: {SPRINT | STANDARD | HEAVY}
**Total Files**: {number}

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Resolved | 0 |
| 🟢 GREEN (auto-resolved) | 0 |
| 🟡 YELLOW (needs review) | 0 |
| 🔴 RED (needs human) | 0 |
| Regenerated (lockfiles) | 0 |
| Deep Thinker invocations | 0 |

---

## Decision Log

### Batch 0: Foundation

_(Decisions logged here as files are resolved)_

<!--
TEMPLATE for each decision:

### Decision: {file_path}

- **Timestamp**: {ISO-8601}
- **Batch**: {batch_id} ({batch_name})
- **Conflict Type**: {type}
- **Complexity**: {complexity}
- **Strategy Applied**: {KEEP_OURS | KEEP_THEIRS | KEEP_BOTH | MANUAL_MERGE | REGENERATE | DEEP_THINK}
- **Resolution Summary**: {1-2 sentence description of what was done}
- **Confidence**: {🟢 GREEN (score) | 🟡 YELLOW (score) | 🔴 RED (score)}
- **Reasoning**: {Why this resolution was chosen}
- **Intent Applied**: Ours={intent}, Theirs={intent}
- **Reversal Command**: `git show :2:{file_path} > {file_path}`
- **Reviewed By**: {AI (auto-resolved) | AI (flagged for review) | Human}
- **Uncertainty Notes**: {Any caveats or risks}

---
-->

### Batch 1: Types & Interfaces

_(Decisions logged here)_

### Batch 2: Shared / Middleware

_(Decisions logged here)_

### Batch 3: Implementations

_(Decisions logged here)_

### Batch 4: Tests

_(Decisions logged here)_

### Batch 5: Docs / CI

_(Decisions logged here)_

---

## Files Flagged for Human Review

| File | Confidence | Reason | Question |
|------|-----------|--------|----------|
| _(none yet)_ | | | |

---

## Reversal Index

Quick reference for undoing specific resolutions:

| File | Reversal Command |
|------|-----------------|
| _(populated during execution)_ | |

---

## Post-Merge Regeneration Commands

Run these after committing the merge:

```bash
# JavaScript/TypeScript lockfiles
npm install          # or: yarn install / pnpm install

# Go dependencies
go mod tidy

# Python dependencies
poetry lock          # or: pip freeze > requirements.txt

# Generated code
npm run generate     # if applicable (GraphQL codegen, Prisma, etc.)
```

---

## Lessons Learned

_(Populated after merge completion — patterns to improve future resolutions)_
