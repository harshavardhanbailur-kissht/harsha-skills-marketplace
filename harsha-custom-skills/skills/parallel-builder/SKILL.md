---
name: parallel-skill-builder
description: |
  Parallel execution orchestrator for Claude Code/Cowork. Decomposes features, epics, or PRDs
  into parallel subtasks, engineers complete prompts for each, and launches them simultaneously
  using the Task tool. Creates a `.parallel/` knowledge base with fully-documented plans, prompts,
  and interface contracts — usable by Task tool subagents OR as manual chat window prompts.
  Triggers: "build in parallel", "parallel agents", "fan-out", "multi-agent build", "decompose
  and execute", "launch subagents", "build simultaneously", "parallelize this", or any non-trivial
  build request with 3+ independent components. Also use when user provides a feature description,
  epic, or PRD and wants efficient multi-agent execution.
---

# Parallel Skill Builder

Orchestrate multiple Claude subagents simultaneously within Claude Code/Cowork to build
complex deliverables faster and with better compartmentalization than a single agent.

## Quick Reference

| Aspect | This Skill |
|--------|------------|
| **Purpose** | Decompose → engineer prompts → launch parallel subagents |
| **Output** | `.parallel/` folder with plans, prompts, contracts + actual deliverables |
| **Execution** | Claude Code Task tool (native subagents, no API keys needed) |
| **When to Use** | 3+ independent components that can be built simultaneously |
| **Dual Mode** | Auto-launch via Task tool OR export prompts for manual chat windows |

## Core Philosophy

```
THINK FIRST:     Decompose thoroughly before launching anything
ENGINEER PROMPTS: Each subagent gets a complete, self-contained prompt (zero questions needed)
DOCUMENT EVERYTHING: All plans/prompts written to .parallel/ (persistent, inspectable, reusable)
PARALLEL EXECUTE: Use Task tool to launch independent subtasks simultaneously
VERIFY & MERGE:  Check outputs for conflicts, then assemble the final deliverable
```

## When to Use

Use when the task has ANY of these:
- Multiple independent components (frontend + backend + database + tests)
- Can be decomposed into 3+ subtasks
- Different concerns that don't depend on each other upfront
- User explicitly asks for parallel/multi-agent execution
- Feature is complex enough that a single agent would lose context

Do NOT use when:
- Task is simple (< 3 subtasks)
- Everything is purely sequential (step 2 needs step 1's full output)
- User wants a quick, single-file output
- The overhead of decomposition exceeds the parallelism benefit

## Core Workflow

```
USER REQUEST
      ↓
[1. DECOMPOSE] ← Ultrathink: break into DAG of subtasks
      ↓
[2. ENGINEER]  ← Write complete prompts + interface contracts to .parallel/
      ↓
[3. LAUNCH]    ← Fan-out via Task tool (parallel within each layer)
      ↓
[4. VERIFY]    ← Check outputs against contracts, fix conflicts
      ↓
[5. ASSEMBLE]  ← Merge into cohesive deliverable
      ↓
FINAL OUTPUT
```

---

## Phase 1: Decompose (THINK — No Execution Yet)

### Step 1: Create the knowledge base

```bash
mkdir -p .parallel/prompts .parallel/contracts .parallel/outputs .parallel/reports
```

### Step 2: Analyze the request with ultrathink depth

For every feature, mentally simulate:
- What are the independent concerns? (things that DON'T need each other to start)
- What are the dependencies? (what DOES need something else first)
- What's the right granularity? (each task = one focused, completable unit)

### Step 3: Write the Decomposition Plan

Create `.parallel/PLAN.md`:

```markdown
# Parallel Execution Plan

## Feature: {description}
## Created: {timestamp}

## Dependency Graph

Layer 0 (parallel — no dependencies):
- [ ] TASK-001: {name} → {output file(s)}
- [ ] TASK-002: {name} → {output file(s)}
- [ ] TASK-003: {name} → {output file(s)}

Layer 1 (parallel — depends on Layer 0):
- [ ] TASK-004: {name} → depends on [TASK-001, TASK-002]
- [ ] TASK-005: {name} → depends on [TASK-003]

Layer 2 (final assembly — depends on all):
- [ ] TASK-006: {name} → depends on [TASK-004, TASK-005]

## Interface Contracts
See .parallel/contracts/ for each task's contract.

## Execution Mode
- [ ] Auto-launch via Task tool
- [ ] Export prompts for manual chat windows
```

### Decomposition Rules (Research-Backed)

1. **Max 3 layers** for most features (4 absolute max). Each layer adds ~10-15% error propagation
2. **3-7 tasks** is the sweet spot. Under 3 = no parallelism benefit. Over 7 = coordination overhead
3. **Junior engineer granularity**: Each task should have ONE clear objective, completable in one shot
4. **MECE principle**: Mutually Exclusive (no overlapping scope), Collectively Exhaustive (all tasks = complete feature)
5. **Interface contracts FIRST**: Define what each task produces and consumes before writing prompts

---

## Phase 2: Engineer Prompts (The Core Value)

For EACH subtask, create two files:

### A. Interface Contract: `.parallel/contracts/TASK-{id}.md`

```markdown
# Interface Contract: TASK-{id} — {name}

## Objective
{Exactly what this task must produce — specific, unambiguous}

## Inputs
- Dependencies: {list of TASK-IDs this depends on, or "none"}
- Context files: {specific files/outputs this task will receive}

## Expected Output
- Files: {exact file paths this task must create}
- Format: {code language, document type, data format}
- Schema: {if applicable — function signatures, API shapes, data models}

## Boundary Conditions (What NOT To Do)
- Do NOT implement: {specific things outside this task's scope}
- Do NOT modify: {files owned by other tasks}
- Assumptions: {explicit assumptions this task can make about other tasks}

## Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}
- [ ] {criterion 3}

## Verification
- Syntax: {how to verify — e.g., "must pass ast.parse"}
- Functional: {how to test — e.g., "import succeeds, function callable"}
```

### B. Subagent Prompt: `.parallel/prompts/TASK-{id}.md`

This is the COMPLETE prompt that will be sent to the Task tool subagent. It must be
self-contained — the subagent has NO access to the conversation history.

```markdown
# Subagent Prompt: TASK-{id} — {name}

## Your Role
You are a specialist agent working on ONE specific subtask of a larger feature.
You have ONE job. Do it completely and correctly.

## Your Task
{detailed task description — be specific, not vague}

## Context
{project context — tech stack, patterns, conventions, existing code structure}

## Dependencies (Output from Prior Tasks)
{If Layer 0: "None — you have no dependencies, work independently."}
{If Layer 1+: Verbatim outputs from dependency tasks — NEVER summarized}

## Interface Contract
- **You MUST produce**: {exact output files/format}
- **You must NOT**: {boundary conditions}
- **You can assume**: {explicit assumptions about other tasks}

## Technical Requirements
- Language/Framework: {specific}
- Patterns to follow: {specific patterns, conventions}
- Libraries to use: {specific}
- File structure: {where to write output}

## Quality Standards
- Production-ready code (not pseudocode, not placeholders)
- All functions must have docstrings and type hints
- Handle edge cases explicitly
- Include error handling

## Output
Write your complete output to: {output_path}
Do NOT explain your reasoning. Just produce the deliverable.
```

**CRITICAL**: The prompt quality determines everything. Most subagent failures are
invocation failures (bad prompts), not execution failures. Each prompt must pass this test:
"Could a competent developer execute this with ZERO clarifying questions?"

---

## Phase 3: Launch (Parallel Execution)

### Option A: Auto-Launch via Task Tool (Recommended)

Use the Task tool to spawn parallel subagents. Launch ALL tasks within a layer simultaneously
in a single message with multiple Task tool calls:

```
For Layer 0 (all independent — launch simultaneously):
  Task tool → TASK-001 prompt (from .parallel/prompts/TASK-001.md)
  Task tool → TASK-002 prompt (from .parallel/prompts/TASK-002.md)
  Task tool → TASK-003 prompt (from .parallel/prompts/TASK-003.md)

Wait for all Layer 0 to complete.

Inject Layer 0 outputs into Layer 1 prompts, then launch Layer 1:
  Task tool → TASK-004 prompt (with TASK-001 + TASK-002 outputs injected)
  Task tool → TASK-005 prompt (with TASK-003 output injected)

Continue until all layers complete.
```

**Task tool settings per subagent:**
- `subagent_type`: Use "general-purpose" for code/docs, "Bash" for scripts/commands
- `model`: Use "sonnet" for workers, "opus" for complex analysis tasks
- `prompt`: The full content of the `.parallel/prompts/TASK-{id}.md` file
- `description`: Short 3-5 word summary

**Parallelism rules:**
- Max 10 concurrent Task calls (Claude Code limit)
- Recommend 3-5 for most features (more = more overhead)
- Each subagent gets its own context window (no cross-contamination)

### Option B: Export for Manual Chat Windows

If the user prefers manual control, the `.parallel/prompts/` folder contains
ready-to-paste prompts. User can:
1. Open multiple Claude Code / Cowork chat windows
2. Paste each prompt into a separate window
3. Run them simultaneously
4. Manually collect outputs

Update `.parallel/PLAN.md` checkboxes as tasks complete.

---

## Phase 4: Verify

After each layer completes, verify outputs:

### Verification Checklist

For each completed task:
1. **Exists**: Output file(s) created at expected path
2. **Non-empty**: Output has substantive content
3. **Syntax** (for code): Run `python3 -c "import ast; ast.parse(open('file').read())"`
4. **Contract check**: Output matches Interface Contract (expected format, files, schema)
5. **Conflict check**: No duplicate/conflicting definitions across parallel outputs

### Cross-Output Conflict Detection

When multiple agents produce code for the same project:
- Check for duplicate function/class names
- Check for conflicting import patterns
- Check for incompatible assumptions
- If conflicts found: resolve before proceeding to next layer

### Fix Protocol

If a task's output fails verification:
1. First attempt: Launch a fix subagent with the original prompt + error feedback
2. Second attempt: Adjust the prompt (more specific, different approach)
3. Third attempt: Escalate to user with clear description of what's failing

---

## Phase 5: Assemble

Merge all verified outputs into the final deliverable:

1. **Collect** all outputs from `.parallel/outputs/`
2. **Resolve** any remaining conflicts (import deduplication, naming)
3. **Assemble** into the target file structure
4. **Generate** `.parallel/reports/EXECUTION_REPORT.md` with:
   - Tasks completed/failed
   - Verification results
   - Conflict resolutions
   - Files produced
5. **Deliver** final output to the user's project directory

---

## State Management

### Progress Tracking

Use TodoWrite throughout execution to track each task's status.
Also maintain `.parallel/PLAN.md` with checkbox states for persistence across sessions.

### Resuming Interrupted Work

If a session runs out of context or is interrupted:
1. Read `.parallel/PLAN.md` to see what's completed
2. Check `.parallel/outputs/` for existing task outputs
3. Skip completed tasks (idempotent — don't re-run what's done)
4. Continue from the first incomplete layer

---

## Reference Documentation

The research/ and references/ folders contain deep knowledge backing every design decision.
Load these when you need deeper guidance on specific topics:

| Reference | When to Load |
|-----------|-------------|
| `references/DECOMPOSITION.md` | Complex dependency graphs, DAG algorithms |
| `references/VERIFICATION.md` | LLM-as-judge patterns, rubric design |
| `references/PROMPT_ENGINEERING.md` | Advanced prompt patterns for subagents |
| `references/ORCHESTRATION.md` | Concurrency patterns, rate limiting |
| `research/02-multi-agent-failures-research.md` | MAST failure modes to prevent |
| `research/03-task-decomposition-research.md` | ADaPT adaptive decomposition |
| `research/07-agent-teams-orchestration-research.md` | Agent Teams vs Task tool |
| `research/09-prompt-injection-defense-research.md` | Inter-agent security |
| `research/10-evaluation-benchmarking-research.md` | Quality measurement |
| `research/12-contradiction-analysis.md` | Reconciled design decisions |

---

## Key Design Principles (Research-Backed)

### 1. Think Before You Launch
Never launch subagents without a complete PLAN.md and all prompts written to files.
The planning phase IS the value — rushing to execution produces garbage.

### 2. Interface Contracts First
Before writing any prompt, define what each task produces and consumes.
This prevents the #1 multi-agent failure mode (MAST FM-2.6: reasoning-action mismatch at 13.2%).

### 3. Prompt Quality Over Quantity
Each subagent prompt must be self-contained and unambiguous.
"Most sub-agent failures aren't execution failures — they're invocation failures."
Include: objective, context, dependencies (verbatim), boundaries, output format.

### 4. File-Based Communication
Subtask outputs go to files, not through the coordinator.
Pass full dependency outputs verbatim into downstream prompts — never summarize.
This prevents MAST FM-2.2 (information loss in telephone game).

### 5. Verify Before Proceeding
Check each layer's outputs against contracts before launching the next layer.
Don't trust outputs blindly. Syntax check, contract check, conflict check.

### 6. Design for Resume
Everything persists in `.parallel/`. If the session dies, another session can
read PLAN.md and continue exactly where we left off. No state in LLM memory.

### 7. Dual Mode Always Available
Every plan produces `.parallel/prompts/` files that work both ways:
- Auto-launched via Task tool (fast, automated)
- Copy-pasted into manual chat windows (full control, inspectable)
The user always has the option to do either.

---

## Example Walkthrough

**User says**: "Build a FastAPI service with JWT auth, SQLAlchemy models, CRUD endpoints, and pytest tests"

### Phase 1 output (`.parallel/PLAN.md`):

```
Layer 0 (parallel — no dependencies):
- [x] TASK-001: Database models (SQLAlchemy) → models.py
- [x] TASK-002: Auth module (JWT) → auth.py, auth_config.py
- [x] TASK-003: Pydantic schemas → schemas.py

Layer 1 (parallel — depends on Layer 0):
- [ ] TASK-004: CRUD endpoints → routers/users.py, routers/posts.py
         depends on [TASK-001, TASK-003]
- [ ] TASK-005: Middleware (auth, CORS, error handling) → middleware.py
         depends on [TASK-002]

Layer 2 (parallel — depends on Layer 1):
- [ ] TASK-006: Integration tests → tests/
         depends on [TASK-004, TASK-005]
- [ ] TASK-007: API documentation → docs/
         depends on [TASK-004]
```

### Phase 2 output (example prompt file):

`.parallel/prompts/TASK-001.md` would contain a complete, self-contained prompt
for building the SQLAlchemy models — including tech stack context, naming conventions,
exact output path, and the explicit boundary: "Do NOT implement API endpoints or auth."

### Phase 3: Launch TASK-001, 002, 003 simultaneously via 3 Task tool calls.

### Phase 4: Verify all Layer 0 outputs, inject into Layer 1 prompts, launch.

### Phase 5: Assemble all files into project structure, deliver.

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong | Instead Do |
|--------------|----------------|------------|
| Launching without planning | Subagents produce conflicting garbage | Write PLAN.md + all prompts first |
| Vague prompts | Subagent asks questions it can't ask | Engineer self-contained prompts |
| Summarizing dependency outputs | Information loss (MAST FM-2.2) | Pass verbatim outputs |
| Over-parallelizing (10+ tasks) | Coordination overhead exceeds benefit | 3-7 tasks, max 3 layers |
| Skipping verification | Conflicts compound in later layers | Check contracts after each layer |
| State in LLM memory only | Lost on context reset | Write everything to .parallel/ |
| Using API scripts in Cowork | Wrong execution model | Use Task tool (native subagents) |

---

*Parallel Skill Builder v3.0 — Native Claude Code/Cowork parallel execution*

**Research base**: 12 research files, 4 reference documents (~10,000 lines of validated knowledge)
**Key sources**: MAST Taxonomy (NeurIPS 2025), ADaPT Framework, SagaLLM (VLDB 2025),
Anthropic Engineering (multi-agent research system), OWASP LLM Top 10 2025
