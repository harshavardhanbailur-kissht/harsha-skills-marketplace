# Pipeline Status
**Started**: [TIMESTAMP]
**Complexity**: [TRIVIAL | SMALL | MEDIUM | COMPLEX]
**Pipeline Depth**: [0 | 1 | 2 | 3]
**Route**: [direct | think-only | think-parallel | think-orchestrate-parallel]
**Current Stage**: [assessing | thinking | adapting | orchestrating | parallelizing | verifying | complete | error]

## Complexity Assessment

**Signals detected**:
- Files affected: [1 | few | many | cross-system]
- Security/data implications: [yes | no]
- Reversible: [yes | no]
- Executor questions anticipated: [few | some | many]

**Decision**: [COMPLEXITY] because [reasoning]

## Pipeline Route

```
[visual of the active route, e.g.:]
USER REQUEST → deep-thinker → ThinkingCompiler → parallel-builder → DONE
                    ✅              ✅                 🔄
```

## Stage Log

| # | Stage | Status | Started | Completed | Output |
|---|-------|--------|---------|-----------|--------|
| 1 | Complexity Gate | ✅ | [time] | [time] | [COMPLEXITY] |
| 2 | deep-thinker | [status] | [time] | [time] | .deep-think/ ([N] files) |
| 3 | ThinkingCompiler | [status] | [time] | [time] | .parallel/PLAN.md |
| 4 | parallel-builder | [status] | [time] | [time] | [N] sub-agents launched |
| 5 | Verification | [status] | [time] | [time] | .parallel/reports/ |

## Key Decisions

- [Decision 1: why this route was chosen]
- [Decision 2: why orchestrator was skipped/included]
- [Decision 3: any complexity override by user]

## Errors / Warnings

- [Any adapter errors, missing files, or degraded output]

## Resume Instructions

If this pipeline was interrupted:
1. Read this file first
2. Check which stage is marked as current
3. Resume from that stage (prior stages' output is preserved in their directories)
