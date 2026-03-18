# Adapter 1: ThinkingCompiler

Converts `.deep-think/` output (human-readable markdown) into `.parallel/PLAN.md`
(structured execution plan). This is the most important adapter in the pipeline because
it bridges the gap between free-form analysis and structured parallel execution.

## When This Adapter Runs

After the deep-thinker stage completes AND the router has decided to proceed to parallel
execution (MEDIUM or COMPLEX complexity).

## Prerequisites

Before running, verify these files exist in `.deep-think/`:

**Required** (adapter fails without these):
- `EXECUTION_CHECKLIST.md` — Primary source of tasks
- `OVERVIEW.md` — Project scope and success criteria

**Strongly Recommended** (adapter produces better output with these):
- `ARCHITECTURE.md` — Dependency relationships and design decisions
- `IMPLEMENTATION.md` — File paths, component names, technical details

**Optional** (enriches sub-agent prompts):
- `CURRENT_STATE.md`, `EDGE_CASES.md`, `OPTIMIZATIONS.md`, `CREATIVE_IDEAS.md`

If required files are missing, create `.pipeline/ADAPTER_ERROR.md` and halt.

## Conversion Algorithm

### Step 1: Extract the Task Graph

Read `EXECUTION_CHECKLIST.md` and identify individual tasks.

**Pattern matching priority** (try in order):

1. **Explicit phases/sections**: Look for `## Phase N:` or `## Step N:` or `### N.` headers.
   Each phase becomes a candidate execution layer.

2. **Checkbox items**: Look for `- [ ]` items. Each becomes a candidate task.
   Nested checkboxes (indented under a parent) are sub-tasks of the parent.

3. **Numbered lists**: `1.`, `2.`, `3.` items at the top level are tasks.

4. **Bold action items**: Lines starting with `**[Action]**:` or similar emphasis.

For each extracted task, capture:
- **Title**: The first line/sentence of the task
- **Description**: Any detail text following the title
- **File paths**: Any paths mentioned (e.g., `src/components/Auth.tsx`)
- **Verification criteria**: Text after "Verify:", "Test:", "Confirm:", "Acceptance:"
- **Dependency signals**: Look for "after", "requires", "depends on", "once X is done"

### Step 2: Infer Dependencies

Dependencies come from three sources:

**Explicit signals in EXECUTION_CHECKLIST.md**:
- "After TASK-X" / "Once Phase N is complete" → hard dependency
- "Ideally after" / "Should follow" → soft dependency (treat as hard for layer computation)

**Structural signals**:
- Tasks within the same phase that reference the same file → likely sequential
- Tasks in later phases → depend on earlier phases by default
- Tasks that consume outputs mentioned in earlier tasks → hard dependency

**Architectural signals from ARCHITECTURE.md**:
- Component A depends on Component B → tasks touching A depend on tasks touching B
- "Foundation layer" / "core module" language → those tasks go in Layer 0
- "Integration" / "wiring" / "connecting" language → those tasks go in later layers

**Dependency inference rules**:
1. If unsure, assume sequential (safer than incorrect parallelization)
2. Tasks touching different files with no shared imports → likely parallelizable
3. UI tasks and API tasks → often parallelizable
4. Test tasks → always depend on the implementation they test
5. "Setup" / "config" / "init" tasks → Layer 0

### Step 3: Compute Execution Layers (Topological Sort)

Apply Kahn's algorithm to the dependency graph:

```
1. Build adjacency list from dependencies
2. Calculate in-degree for each task
3. Layer 0 = all tasks with in-degree 0
4. For each task in Layer 0:
   - For each dependent task:
     - Decrease in-degree by 1
     - If in-degree becomes 0, add to next layer
5. Repeat until all tasks assigned to layers
6. If unassigned tasks remain → circular dependency detected → flag error
```

**Layer naming convention**:
- Layer 0: "Foundation" — no dependencies, launch all simultaneously
- Layer 1: "Core Build" — depends on foundation
- Layer 2: "Integration" — wires core components together
- Layer 3+: "Refinement" — polish, optimization, testing

### Step 4: Generate Sub-Agent Prompts

For each task, generate a prompt that gives the sub-agent everything it needs.

**Prompt structure**:

```markdown
# Task: [TASK-ID] — [Title]

## Context
[From OVERVIEW.md: project goal, scope]
[From CURRENT_STATE.md: what already exists relevant to this task]

## Your Mission
[Task description from EXECUTION_CHECKLIST.md]

## Technical Details
[From IMPLEMENTATION.md: specific file paths, patterns, APIs]
[From ARCHITECTURE.md: design decisions relevant to this task]

## Constraints
[From EDGE_CASES.md: error scenarios to handle]
[From OPTIMIZATIONS.md: performance targets if relevant]

## Deliverables
[Expected output files with descriptions]

## Acceptance Criteria
[From EXECUTION_CHECKLIST.md verification criteria]

## Interface Contracts
[If this task shares interfaces with other tasks, include the contract]

## Dependencies
[If Layer 1+: "Read the outputs from TASK-X before starting"]
```

**Prompt enrichment rules**:
- Layer 0 prompts get full project context (sub-agents have no prior knowledge)
- Layer 1+ prompts reference specific outputs from prior layers
- All prompts include relevant edge cases from EDGE_CASES.md
- Prompts should be self-contained — sub-agent should need zero questions

### Step 5: Generate Interface Contracts

If two tasks produce code that must integrate (e.g., one builds an API, another builds
the client), create a contract file in `.parallel/contracts/`:

**When to create contracts**:
- Two tasks reference the same type/interface/class
- One task produces an output another task consumes
- Tasks touch both sides of an API boundary
- Tasks build components that will be composed together

**Contract detection from deep-think files**:
- ARCHITECTURE.md mentions "shared types" or "interface" → contract needed
- IMPLEMENTATION.md shows the same type defined in multiple components → contract needed
- Tasks in different layers where the later task reads the earlier task's output → contract needed

### Step 6: Write Output Files

Create the following in `.parallel/`:

1. **`PLAN.md`** — Full execution plan (see template in `templates/plan-from-thinking.md`)
2. **`contracts/`** — Interface contracts (if any)
3. **`prompts/TASK-XXX-prompt.md`** — Individual prompt files (one per task)

Also create directory scaffolding:
```bash
mkdir -p .parallel/{contracts,prompts,outputs,reports}
```

## Quality Checks

Before declaring the adapter complete, verify:

1. [ ] Every task from EXECUTION_CHECKLIST.md is accounted for in PLAN.md
2. [ ] No circular dependencies in the layer graph
3. [ ] Layer 0 has at least 2 tasks (otherwise parallelization adds no value)
4. [ ] Every task has acceptance criteria (even if inferred)
5. [ ] Sub-agent prompts are self-contained (no "see above" references)
6. [ ] Interface contracts exist for all cross-task integration points

## Handling Edge Cases

**Deep-thinker produced minimal output** (only OVERVIEW + EXECUTION_CHECKLIST):
- Still proceed, but flag that prompts will be less enriched
- Add note to each prompt: "This task may require additional research/exploration"

**EXECUTION_CHECKLIST has no clear phases**:
- Treat each top-level item as independent → all go in Layer 0
- Flag for user review: "Could not infer dependencies, defaulting to full parallel"

**Circular dependency detected**:
- Break the cycle at the weakest link (the dependency with most "soft" signals)
- Document the break in PLAN.md with rationale
- Flag for user review

**Too many tasks for parallel execution** (>15):
- Group related tasks into "meta-tasks"
- Each meta-task becomes one sub-agent that handles multiple related items
- Keeps sub-agent count manageable (5-10 is optimal)

**Too few tasks** (<3):
- Consider whether parallel execution adds value
- If not, recommend the user run deep-thinker output directly without parallel-builder
- Document reasoning in `.pipeline/status.md`
