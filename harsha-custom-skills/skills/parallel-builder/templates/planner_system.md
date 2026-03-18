# Decomposition Planning Guide

Use this guide when performing Phase 1 (Decompose) of the parallel-skill-builder workflow.
This is NOT a system prompt for an API call — it's instructions for Claude to follow
when decomposing a feature into parallel subtasks.

---

## Decomposition Strategy

### Step 1: Identify Independent Concerns
Break the feature into distinct areas of responsibility:
- Data layer (models, schemas, database)
- Business logic (services, algorithms, validation)
- API layer (endpoints, routes, middleware)
- UI components (if applicable)
- Tests (unit, integration)
- Documentation (API docs, README)

### Step 2: Map Dependencies
For each concern, ask: "Does this NEED output from another concern to start?"
- If NO → Layer 0 (can run immediately, in parallel with other Layer 0 tasks)
- If YES → Later layer (must wait for dependency to complete)

Only create dependencies where data ACTUALLY flows between tasks.
Two components that share the same database don't necessarily depend on each other —
they just both need the schema, which is its own task.

### Step 3: Optimize Granularity
Target "junior engineer" level per task:
- ONE clear objective per task
- Completable in a single subagent session
- Specific enough to be actionable
- Broad enough that coordination doesn't dominate

Bad: "Build the backend" (too broad)
Bad: "Add import for datetime" (too narrow)
Good: "Build the JWT auth module with login endpoint, token generation, and get_current_user dependency"

### Step 4: Define Interface Contracts
For each task, write to `.parallel/contracts/TASK-{id}.md`:
- What it outputs (exact files, schemas, function signatures)
- What it needs from dependencies (specific data/interfaces)
- What it must NOT implement (boundaries — prevents overlap)
- Explicit assumptions (what other tasks handle)

### Step 5: Assign to Execution Layers
- Layer 0: All tasks with no dependencies (run in parallel)
- Layer 1: Tasks depending only on Layer 0 outputs (run in parallel after Layer 0)
- Layer 2+: Continue until all tasks assigned
- Final layer: Assembly/integration task (depends on everything)

## Layer Limits (Research-Backed)

| Layers | Error Propagation | Recommendation |
|--------|-------------------|----------------|
| 1 | ~85% success | Ideal for simple features |
| 2 | ~72% success | Good for most features |
| 3 | ~61% success | Max for typical features |
| 4+ | ~52% success | Only when absolutely necessary |

## Task Count Guidelines

| Tasks | Assessment |
|-------|-----------|
| 1-2 | Too few — no parallelism benefit, don't use this skill |
| 3-5 | Sweet spot for most features |
| 6-7 | Good for complex features or epics |
| 8-10 | Maximum recommended — coordination overhead increases |
| 10+ | Over-parallelized — decompose into sub-features first |

## Output: PLAN.md Structure

Write the plan to `.parallel/PLAN.md` with this structure:

```markdown
# Parallel Execution Plan

## Feature: {description}
## Created: {timestamp}
## Tasks: {count} across {layer_count} layers

## Dependency Graph

Layer 0 (parallel — no dependencies):
- [ ] TASK-001: {name} → produces {output files}
- [ ] TASK-002: {name} → produces {output files}

Layer 1 (parallel — depends on Layer 0):
- [ ] TASK-003: {name} → depends on [TASK-001] → produces {output files}
- [ ] TASK-004: {name} → depends on [TASK-002] → produces {output files}

Layer 2 (assembly):
- [ ] TASK-005: Final assembly → depends on all

## Contracts
See .parallel/contracts/TASK-{id}.md for each task's interface contract.

## Execution Mode
- [ ] Auto-launch via Task tool
- [ ] Export prompts for manual chat windows
```

## Common Decomposition Patterns

### Web Application
```
Layer 0: [database_models, auth_module, config/schemas]
Layer 1: [api_endpoints, middleware] ← depends on L0
Layer 2: [tests, documentation] ← depends on L1
```

### Claude Skill
```
Layer 0: [SKILL.md_core, reference_docs (parallel per topic)]
Layer 1: [templates, examples] ← depends on L0 for structure
Layer 2: [validation, integration_test] ← depends on L1
```

### Research/Document
```
Layer 0: [section_1, section_2, section_3, ...(parallel per section)]
Layer 1: [synthesis, cross_references] ← depends on all L0
Layer 2: [editing, formatting] ← depends on L1
```
