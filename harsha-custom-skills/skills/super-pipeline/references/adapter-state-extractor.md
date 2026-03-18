# Adapter 2: StateExtractor

Converts `.orchestrator/` state (YAML + markdown) into `.parallel/PLAN.md`
(structured execution plan). This adapter is simpler than ThinkingCompiler because
the orchestrator already produces structured, machine-parseable output.

## When This Adapter Runs

After the orchestrator stage completes AND the router decides to fan out to
parallel execution. This happens only at COMPLEX pipeline depth (the full 3-stage path).

## Prerequisites

Before running, verify these files exist in `.orchestrator/`:

**Required**:
- `state.yaml` — Task definitions with statuses and dependencies
- `CONTEXT.md` — Project context for sub-agent prompt enrichment

**Optional**:
- `checkpoints/` — Historical state for recovery
- `knowledge/` — Accumulated project knowledge
- `HUMAN_INPUT.md` — If present, read it first — the user may have made decisions

## Conversion Algorithm

### Step 1: Parse state.yaml

Read the YAML file and extract:

```python
# Pseudocode for what the adapter does mentally
project_name = state.project.name
project_goal = state.project.goal
current_phase = state.phase

# Filter to actionable tasks only
actionable_tasks = [
    task for task in state.tasks
    if task.status in ("pending", "in_progress")
]

# Skip completed/verified tasks — they're done
# Skip blocked tasks — they need human input first
```

**If no actionable tasks found**:
- Check if all tasks are completed → project is done, no parallel work needed
- Check if tasks are blocked → create ADAPTER_ERROR.md noting the block
- Check if phase is "complete" → confirm with user before proceeding

### Step 2: Build Dependency Graph

The orchestrator already provides explicit dependencies:

```yaml
tasks:
  - id: "TASK-001"
    dependencies:
      hard: ["TASK-000"]  # Must complete first
      soft: ["TASK-002"]  # Should complete first, but not blocking
```

**Conversion rules**:
- `hard` dependencies → edges in the DAG (strict ordering)
- `soft` dependencies → edges in the DAG (treat as hard for layer computation,
  but note in the prompt that the dependency output is "nice to have, not required")
- Dependencies on completed tasks → already satisfied, ignore

**Handle cross-references to completed tasks**:
If TASK-005 depends on TASK-002 (completed), the adapter should:
1. Find TASK-002's output in state.yaml (`task.outputs[].path`)
2. Include that output path in TASK-005's prompt context
3. Remove the dependency edge (it's already satisfied)

### Step 3: Compute Execution Layers

Same Kahn's algorithm as ThinkingCompiler:

```
1. Build adjacency list from hard dependencies (excluding satisfied ones)
2. Calculate in-degree for each actionable task
3. Layer 0 = all tasks with in-degree 0
4. Process layers iteratively
```

The orchestrator may have already suggested an execution order. If `state.yaml`
contains a `suggested_order` field, use it as a hint but still verify with
topological sort (the suggestion may be outdated if tasks were completed).

### Step 4: Generate Sub-Agent Prompts

For each task, generate a prompt enriched with orchestrator context.

**Prompt structure**:

```markdown
# Task: [TASK-ID] — [Task Name]

## Project Context
[From CONTEXT.md: the full project mental model]

## Your Mission
[Task name and description from state.yaml]

## Acceptance Criteria
[From state.yaml task.acceptance_criteria — these are already structured]

## Assigned Skill
[If state.yaml has task.assigned_skill, include:]
"This task is best suited for the [skill-name] domain skill.
Approach it with that expertise."

## Completed Dependencies
[For each completed dependency, include the output path and summary]

## Deliverables
[From state.yaml task.outputs — expected paths and descriptions]

## Notes from Orchestrator
[Any session.notes or task-specific notes from state.yaml]
```

**Differences from ThinkingCompiler prompts**:
- Orchestrator prompts are more structured (data comes from YAML, not markdown)
- Acceptance criteria are explicit (not inferred)
- Skill assignments are explicit (not guessed)
- Less "exploration" context, more "execution" context

### Step 5: Respect Orchestrator Skill Routing

The orchestrator assigns domain skills to tasks (`assigned_skill` field).
The parallel-builder should honor these:

| assigned_skill | Sub-Agent Instruction |
|---------------|----------------------|
| `3d-web-graphics-mastery` | "Read the 3d-web-graphics-mastery skill before starting" |
| `gas-debugger` | "Use the gas-debugger skill's methodology" |
| `ui-ux-mastery-modular` | "Apply ui-ux-mastery-modular principles" |
| `null` / empty | No special instruction needed |

Include the skill reference in the sub-agent prompt, not as a dependency.

### Step 6: Write Output Files

Same structure as ThinkingCompiler:

1. **`.parallel/PLAN.md`** — Execution plan from orchestrator state
2. **`.parallel/contracts/`** — Interface contracts (infer from task outputs)
3. **`.parallel/prompts/TASK-XXX-prompt.md`** — Individual prompts

### Step 7: Update Orchestrator State

After generating the parallel plan, update `.orchestrator/state.yaml`:
- Set `phase: "parallel_execution"`
- Add note to `session.notes`: "Parallel plan generated at [timestamp]"
- Create checkpoint in `.orchestrator/checkpoints/`

This ensures the orchestrator can resume correctly if the parallel execution
is interrupted.

## Quality Checks

1. [ ] All actionable tasks from state.yaml are in PLAN.md
2. [ ] Completed task outputs are referenced in dependent task prompts
3. [ ] No circular dependencies (orchestrator should prevent this, but verify)
4. [ ] Skill assignments are preserved in sub-agent prompts
5. [ ] Orchestrator state updated with parallel execution phase

## Handling Edge Cases

**state.yaml is malformed or incomplete**:
- Try to parse what's available
- Flag missing fields in ADAPTER_ERROR.md
- If task list is present but metadata is missing, proceed with warnings

**HUMAN_INPUT.md exists (pending human decision)**:
- Do NOT proceed to parallel execution
- Instead, surface the human input request in `.pipeline/status.md`
- Halt and tell the user: "The orchestrator is waiting for your input on [topic]"

**All tasks have skill assignments**:
- This is fine — the parallel-builder just passes the skill context through
- Each sub-agent prompt includes the skill reference

**Mixed completed and pending tasks (mid-project resume)**:
- Only include pending/in_progress tasks in the parallel plan
- Reference completed task outputs as available context
- This is the adapter's most common real-world scenario
