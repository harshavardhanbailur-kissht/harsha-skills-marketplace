# Session State Template

Use this template when creating or updating `SESSION_STATE.md`. This is the single most important file for compaction recovery — a recovering Claude session reads this first.

```markdown
## Session: [brief problem description, 1 line]
## Started: [date or session identifier]
## Decision Type: [Feature / Pricing / Migration / Architecture / Partnership / Operational]
## Complexity: [Trivial / Simple / Medium / Complex]
## Current Phase: [Define | Axes | Enumerate | Rank | Expert Panel | Synthesize | Build | Complete]

## Progress:
- [x] Problem definition
- [x] Axis identification ([N] axes identified)
- [~] Option enumeration ([N] options, [N] dismissed by user — see CROSS_QUESTIONS.md)
- [ ] Ranking
- [ ] Expert panel
- [ ] Synthesis / decision doc

## Next Action:
[One sentence describing exactly what should happen next. Be specific enough that a new session
can start executing immediately.]

## User Overrides: [N] (see CROSS_QUESTIONS.md)
## User-Narrowed Axes: [list any axes where user locked in a value, or "None"]

## Axes Identified:
[List axis names, one per line]

## Options Count by Axis:
[Axis name]: [N] options
[Axis name]: [N] options

## Composite Strategies (for compound decisions):
- Constructed: [N] from morphological cross-product
- Survived pruning: [N]

## Phase History:
1. Phase 1 (Define) — completed
2. Phase 2 (Axes) — completed

## Reversals: [None, or list]

## Notes for Recovery:
[Any context a recovering session needs. E.g., "User indicated mobile-first only."
"User is time-constrained — 45 minutes max." "Decision type is migration — use
EXECUTION_PLAN.md template in Phase 6."]
```

## Completion Markers

| Marker | Meaning |
|--------|---------|
| `[x]` | Phase fully completed |
| `[~]` | Phase completed with user-directed skips (details in parentheses) |
| `[ ]` | Phase not yet started |

## Update Rules

- Update SESSION_STATE.md at the end of EVERY phase, before starting the next
- When a reversal occurs, add to Phase History and update Current Phase
- When user narrows an axis (locks in a value), add to User-Narrowed Axes
- The "Next Action" field must always be specific enough for a cold-start recovery
