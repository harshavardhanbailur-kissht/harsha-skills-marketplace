---
name: project-orchestrator
description: |
  The planning brain of the THINK→PLAN→DISPATCH→EXECUTE pipeline. Reads deep-thinker analysis
  from .deep-think/, decomposes work into MECE tasks, generates self-contained execution prompts
  with embedded context that survives compaction, and writes output to .parallel/ in the exact
  format parallel-skill-builder consumes. Use when: planning projects, breaking down epics,
  generating execution-ready prompts, capturing architectural decisions, tracking state across
  sessions, resuming interrupted planning, or when work must survive context loss. Does NOT
  execute tasks — that is parallel-skill-builder's job. Keywords: project planning, task
  breakdown, execution prompts, context engineering, knowledge capture, ADR, checkpoint, resume,
  compaction-proof, MECE decomposition, sprint planning, epic decomposition.
---

# Project Orchestrator v3.1

The planning brain. Reads analysis, decomposes into tasks, generates compaction-proof
execution prompts, writes them to `.parallel/` for dispatch. Does not execute.

## Core Problem

Context compaction silently loses decisions, constraints, failed approaches, implicit knowledge.
This skill writes **self-contained execution prompts to files**. Each prompt embeds ALL context
so a fresh Claude window executes with zero questions. Nothing lives only in memory.

## Pipeline Position & Responsibilities

```
.deep-think/  ──▶  .orchestrator/  ──▶  .parallel/  ──▶  execution
 (input)           (own state)          (output)         (not our job)
 DEEP-THINKER      ORCHESTRATOR         PARALLEL-SKILL-BUILDER
 Thinks deeply     Plans + prompts      Dispatches + verifies
```

**Orchestrator OWNS**: Task decomposition, state persistence, knowledge capture, prompt generation.
**Orchestrator DOES NOT OWN**: Launching subagents, executing tasks, verifying outputs, assembling results.
Those belong to parallel-skill-builder.

**Directory ownership**:
- `.orchestrator/` — Our persistent state (survives sessions)
- `.parallel/` — Our output for parallel-skill-builder (their input)
- `.deep-think/` — Our input from deep-thinker (their output)

---

## 1. Project Initialization

### New Project

```bash
python scripts/init_project.py "Project Name" --goal "High-level goal"
```

Creates:
```
.orchestrator/
├── state.yaml          ← Project state (templates/project-state.yaml)
├── CONTEXT.md          ← Cold-start resume (templates/context-snippet.md)
├── todo.md             ← Attention anchor (templates/todo.md)
├── checkpoints/        ← State snapshots
├── knowledge/          ← ADRs, failure logs, research
│   ├── adr/
│   ├── failures/
│   └── research/
└── session.jsonl       ← Append-only action log

.parallel/
├── PLAN.md             ← Dependency graph for parallel-skill-builder
├── contracts/          ← Interface contracts per task
├── prompts/            ← Self-contained execution prompts per task
├── outputs/            ← Where parallel-skill-builder writes results
└── reports/            ← Execution reports from parallel-skill-builder
```

### Resume Project

When user says "resume", "continue", "pick up where we left off":

1. Read `.orchestrator/CONTEXT.md` (cold-start mental model)
2. Read `.orchestrator/todo.md` (attention anchor — what RIGHT NOW)
3. Read `.orchestrator/state.yaml` (current state data)
4. Check for `.orchestrator/HUMAN_INPUT.md` (pending decisions?)
5. Continue from last known good state

**Always this order**: CONTEXT.md → todo.md → state.yaml.

---

## 2. Deep-Thinker Intake Protocol

If `.deep-think/` exists, the deep-thinker ran first. Read its output in this order:

| Order | File | Extract |
|-------|------|---------|
| 1 | `OVERVIEW.md` | Project goal, scope boundaries, success criteria |
| 2 | `ARCHITECTURE.md` | Constraints, tech stack, patterns to follow/avoid, ADR candidates |
| 3 | `IMPLEMENTATION.md` | Natural task boundaries, file dependencies, sequencing hints |
| 4 | `EDGE_CASES.md` | Acceptance criteria, verification scenarios, failure modes |
| 5 | `CURRENT_STATE.md` | Existing code analysis (if modifying existing project) |
| 6 | `OPTIMIZATIONS.md` | Quality criteria, performance targets |
| 7 | `CREATIVE_IDEAS.md` | Stretch goals (tag as optional in task definitions) |
| 8 | `EXECUTION_CHECKLIST.md` | Step-by-step hints (validate against MECE decomposition) |

### Intake Actions

After reading, immediately:
1. Populate `state.yaml` project section (goal, constraints from ARCHITECTURE.md)
2. Create ADRs in `.orchestrator/knowledge/adr/` for decisions found in ARCHITECTURE.md
3. Note failed approaches from EDGE_CASES.md in `.orchestrator/knowledge/failures/`
4. Begin decomposition (Section 3) using IMPLEMENTATION.md as the primary input

### If No Deep-Thinker Output

Start from user input directly. Ask for: goal, scope boundaries, constraints, tech stack.
Populate state.yaml manually.

---

## 3. Task Decomposition

### MECE Rules

1. **Mutually Exclusive**: No overlapping scope
2. **Collectively Exhaustive**: All tasks = complete goal
3. **Right-Sized**: 2-4 hours human time (sweet spot for AI: ~30 min human equivalent)
4. **Clear Boundaries**: Unambiguous start/end conditions
5. **Dependency-Aware**: Explicit hard/soft dependencies
6. **Vertically Sliced**: End-to-end slices over horizontal layers
7. **Layer-Aware**: Max 3 dependency layers (for parallel-skill-builder)

### Task Sizing

| Human Time | AI Success | Action |
|------------|-----------|--------|
| <15 min | ~95% | Execute directly |
| 15-60 min | ~75% | Execute with checkpoint |
| 1-4 hours | ~40% | Decompose further |
| >4 hours | <15% | Must decompose |

**Break when**: >8 hours, multiple "AND"s, >12 criteria, >5 files (drops to <15% success).

### Essential Task Definition (templates/task-definition.md)

```markdown
TASK: [Action verb] + [Specific object] + [Scope boundary]
CONTEXT: Why this exists, what preceded it, relevant decisions
DONE WHEN:
- [ ] Binary criterion 1
- [ ] Binary criterion 2
NOT INCLUDED: Explicit exclusions
BLOCKED BY: Prerequisites (if any)
ESTIMATED: S (<2hr) | M (2-4hr) | L (4-8hr)
ASSIGNED SKILL: [skill name or "general"]
```

**The Pickup Test**: Can someone with zero context pick this up and know exactly what to build,
how to verify it, and what NOT to build? If no, add more context.

For detailed patterns (HTN, DAG validation, 6-factor scoring): `references/task-decomposition.md`
and `references/complexity-estimation.md`.

---

## 4. State Management

**Location**: `.orchestrator/state.yaml`

```yaml
project:
  id: "proj_001"
  name: "Project Name"
  goal: "High-level goal"
  created: "2025-01-03T10:00:00Z"
  constraints: ["Must use existing auth library", "Budget: 2 weeks"]

phase: "planning"  # planning | prompts | dispatched | review | complete
phase_progress: 0.45

tasks:
  - id: "TASK-001"
    name: "Implement JWT middleware"
    status: "completed"  # pending | in_progress | completed | verified | blocked
    layer: 0             # Parallel execution layer (for .parallel/PLAN.md)
    assigned_skill: "general"
    complexity: "S"
    dependencies: { hard: [], soft: [] }
    acceptance_criteria: ["Returns 401 for expired tokens", "Passes pytest suite"]
    prompt_file: ".parallel/prompts/TASK-001.md"
    contract_file: ".parallel/contracts/TASK-001.md"
    output_path: ".parallel/outputs/TASK-001/"

checkpoints:
  - id: "cp_001"
    created: "2025-01-03T11:00:00Z"
    trigger: "phase_complete"
    state_hash: "sha256:abc123..."

session:
  last_updated: "2025-01-03T12:00:00Z"
  context_usage: 0.45
```

### Key State Rules

- **Atomic writes**: Write to `.tmp`, rename to `.yaml`. Never corrupt on failure.
- **Checkpoint triggers**: Phase completion, context >60%, before risky operations, user request.
- **prompt_file points to .parallel/**: Not .orchestrator/. This is where parallel-skill-builder reads.
- **Validate with**: `python scripts/validate_state.py`

For full state patterns: `references/state-management.md`.

---

## 5. Writing to .parallel/ (Output Protocol)

**This is the orchestrator's most critical output.** Everything written here must be in the
exact format parallel-skill-builder expects.

### Step 1: Write PLAN.md

Create `.parallel/PLAN.md` in parallel-skill-builder's format:

```markdown
# Parallel Execution Plan

## Feature: {from state.yaml project.goal}
## Created: {timestamp}

## Dependency Graph

Layer 0 (parallel — no dependencies):
- [ ] TASK-001: {name} → {output file(s)}
- [ ] TASK-002: {name} → {output file(s)}

Layer 1 (parallel — depends on Layer 0):
- [ ] TASK-003: {name} → depends on [TASK-001, TASK-002]

Layer 2 (final assembly — depends on all):
- [ ] TASK-004: {name} → depends on [TASK-003]

## Interface Contracts
See .parallel/contracts/ for each task's contract.

## Execution Mode
- [ ] Auto-launch via Task tool
- [ ] Export prompts for manual chat windows
```

### Step 2: Write Interface Contracts

For EACH task, create `.parallel/contracts/TASK-{id}.md`:

```markdown
# Interface Contract: TASK-{id} — {name}

## Objective
{Exactly what this task must produce}

## Inputs
- Dependencies: {TASK-IDs or "none"}
- Context files: {specific files this task receives}

## Expected Output
- Files: {exact output paths}
- Format: {language, data format}
- Schema: {function signatures, API shapes if applicable}

## Boundary Conditions
- Do NOT implement: {out of scope}
- Do NOT modify: {files owned by other tasks}
- Assumptions: {what this task can assume about others}

## Acceptance Criteria
- [ ] {binary criterion 1}
- [ ] {binary criterion 2}

## Verification
- Syntax: {e.g., "must pass ast.parse"}
- Functional: {e.g., "import succeeds, function callable"}
```

### Step 3: Write Execution Prompts

For EACH task, create `.parallel/prompts/TASK-{id}.md`:

```markdown
# Subagent Prompt: TASK-{id} — {name}

## Your Role
You are a specialist agent. You have ONE job. Do it completely and correctly.

## Your Task
{detailed description — specific, not vague}

## Context
{project context, tech stack, patterns, conventions, existing code structure}
{Include ACTUAL code snippets — not descriptions}

## Dependencies (Output from Prior Tasks)
{Layer 0: "None — work independently."}
{Layer 1+: Verbatim outputs from dependencies — NEVER summarized}

## Interface Contract
- **You MUST produce**: {exact output files/format}
- **You must NOT**: {boundary conditions}
- **You can assume**: {explicit assumptions}

## Technical Requirements
- Language/Framework: {specific versions}
- Patterns to follow: {specific, with examples}
- File structure: {where to write output}

## Quality Standards
- Production-ready code (no placeholders)
- Handle edge cases explicitly
- Include error handling

## Success Criteria
- [ ] {binary criterion 1}
- [ ] {binary criterion 2}

## Out of Scope
- {explicit exclusion 1}
- {explicit exclusion 2}

## Required Skills
- **{skill-name}**: {why needed}

## Output
Write your complete output to: .parallel/outputs/TASK-{id}/
```

### Implicit Knowledge Checklist

Before generating EACH prompt, verify you've embedded:
- [ ] Framework idioms and patterns from this codebase
- [ ] Naming conventions (variables, files, functions)
- [ ] Error handling patterns already established
- [ ] State management approach
- [ ] Testing patterns and where tests live
- [ ] What was tried and failed (from deep-thinker or knowledge/)
- [ ] Why the current approach was chosen over alternatives

For prompt architecture deep dive: `references/prompt-architecture.md`.

---

## 6. Knowledge Capture

### Triggers

| Event | Action | Template | Location |
|-------|--------|----------|----------|
| Architecture decision | Create ADR | `templates/adr.md` | `.orchestrator/knowledge/adr/` |
| Failed approach | Log immediately | `templates/failure-log.md` | `.orchestrator/knowledge/failures/` |
| Research complete | Atomic finding | `templates/research-finding.md` | `.orchestrator/knowledge/research/` |
| Constraint found | Add to state.yaml | Inline | `state.yaml → constraints` |

**Negative knowledge is as valuable as success.** Prevents future sessions from repeating mistakes.

For PARA organization and maintenance: `references/knowledge-capture.md`.

---

## 7. Results Ingestion (Post-Execution)

After parallel-skill-builder finishes, read results back:

1. Read `.parallel/reports/EXECUTION_REPORT.md` for task completion status
2. For each completed task in `.parallel/outputs/TASK-{id}/`:
   - Update `state.yaml` task status to "completed"
   - Verify against acceptance criteria (quick review)
   - If PASS → mark "verified"
   - If FAIL → mark "blocked", create failure log, plan remediation
3. Update `.orchestrator/CONTEXT.md` with what was accomplished
4. Update `.orchestrator/todo.md` with next phase
5. If more phases remain: generate prompts for next phase (back to Section 5)
6. If all phases complete: run completion checklist

### Review Protocol for Ingested Results

For each completed task, apply quick self-review:

```
Acceptance criteria met?  → YES: mark verified
                          → PARTIALLY: create remediation task, add to next phase
                          → NO: mark blocked, create HUMAN_INPUT.md if 3+ failures
```

**Rule**: Find at least 2 improvements per review. Prevents rubber-stamping.

For full self-review patterns: `references/self-review.md`.
For verification tiers (Automated/AI-Assisted/Human): `references/verification-patterns.md`.

---

## 8. Human Escalation

Escalate when: confidence <70%, irreversible action, conflicting requirements,
3+ failures, security-sensitive, ambiguous criteria.

Create `.orchestrator/HUMAN_INPUT.md` using `templates/human-input.md` with:
situation, what was tried, options with pros/cons/risk, recommendation with confidence %,
and "How to Resume: say 'Continue with Option [X]'".

---

## 9. Session Lifecycle

### New Session
```
[ ] Run init_project.py (creates .orchestrator/ + .parallel/)
[ ] Check for .deep-think/ → run intake protocol (Section 2)
[ ] Decompose into MECE tasks (Section 3)
[ ] Write PLAN.md + contracts + prompts to .parallel/ (Section 5)
[ ] Self-review prompts (Pickup Test on each)
[ ] Hand off: "Execute .parallel/PLAN.md with parallel-skill-builder"
```

### Resume Session
```
[ ] Read CONTEXT.md → todo.md → state.yaml
[ ] Check for HUMAN_INPUT.md
[ ] Check .parallel/outputs/ for new results → ingest (Section 7)
[ ] Continue from current phase
```

### Complete Session
```
[ ] All tasks verified
[ ] Generate report: python scripts/report.py
[ ] Archive state to .orchestrator/archive/
[ ] Update CONTEXT.md with final summary
```

---

## 10. Failure Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| Context exhaustion | Usage >80% | Checkpoint → update CONTEXT.md → new session |
| Infinite loop | Jaccard similarity >0.8 × 3 | Break → alternative decomposition |
| Task stuck | 3 failed attempts | Mark blocked → HUMAN_INPUT.md |
| State corruption | validate_state.py fails | Auto-repair or restore checkpoint |
| Goal drift | Key term overlap <50% | Re-read todo.md → re-align |

**Circuit breaker**: CLOSED → [failure] → OPEN → [timeout] → HALF_OPEN → [success] → CLOSED.

For detailed patterns ($47K disaster case study, failure taxonomy, defensive design):
`references/failure-recovery.md`.

---

## 11. Context Management

At **70% context usage**: checkpoint → update CONTEXT.md + todo.md → recommend new session.

**Memory tiers**: Working (context window) → Short-term (session.jsonl, decisions) →
Long-term (knowledge/, CONTEXT.md, state.yaml).

**Attention anchor**: Read + update `.orchestrator/todo.md` before every action.
Structure: RIGHT NOW → NEXT UP → BLOCKED → DONE THIS SESSION.

For token budgets, compaction algorithms, progressive loading: `references/context-engineering.md`.

---

## 12. Skill Routing

When assigning tasks to skills, embed the skill name in the execution prompt's
"Required Skills" section. Parallel-skill-builder handles the actual routing.

Discovery: check available skills at runtime rather than hardcoding. If unsure which
skill fits, describe the task requirements in the prompt and let the executor decide.

For composition patterns (Saga, circuit breaker): `references/skill-mapping.md`.

---

## Anti-Patterns

**Planning**: Storing state in memory (use files), tasks >4 hours (decompose), skipping
self-review, putting state in CLAUDE.md, ignoring dependency order.

**Prompts**: Subjective terms ("faster" → "<500ms"), context dumps (only modified files),
overloaded prompts (one task per prompt), missing criteria, implicit dependencies,
summarizing upstream outputs (pass verbatim).

**Pipeline**: Writing to wrong directory (use .parallel/ not .orchestrator/prompts/),
executing tasks yourself (that's parallel-skill-builder), launching subagents directly.

---

## Reference Files

| File | Contents |
|------|----------|
| `references/task-decomposition.md` | MECE, HTN, DAG validation, sizing |
| `references/state-management.md` | State schema, checkpoints, atomic updates |
| `references/self-review.md` | Critique prompts, stopping conditions |
| `references/skill-mapping.md` | Skill routing, Saga pattern, circuit breakers |
| `references/failure-recovery.md` | Recovery, loop detection, defensive patterns |
| `references/context-engineering.md` | Compaction, memory tiers, attention anchors |
| `references/complexity-estimation.md` | 6-factor scoring, SWE-bench data |
| `references/prompt-architecture.md` | Self-contained prompts, implicit knowledge |
| `references/knowledge-capture.md` | ADRs, failure logs, PARA organization |
| `references/verification-patterns.md` | SMART-T, debugging agents, error taxonomy |
| `references/git-worktree.md` | Safe isolation for execution (used by parallel-skill-builder) |
| `references/claude-md-integration.md` | CLAUDE.md patterns |
| `references/prompt-patterns.md` | ReAct, CoT, ToT |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/project-state.yaml` | Initial state file |
| `templates/context-snippet.md` | Cold-start resume context |
| `templates/todo.md` | Attention anchor |
| `templates/task-definition.md` | Task entry format |
| `templates/execution-prompt.md` | Self-contained prompt (reference) |
| `templates/human-input.md` | Human escalation |
| `templates/adr.md` | Architecture Decision Record |
| `templates/research-finding.md` | Atomic research insight |
| `templates/failure-log.md` | Negative knowledge capture |
| `templates/verification-report.md` | Debugging output |
| `templates/spike-task.md` | Timeboxed research task |
| `templates/project-plan.md` | Full project decomposition |
| `templates/debugging-agent.md` | Verification agent prompt |

## Scripts

| Script | Usage |
|--------|-------|
| `scripts/init_project.py` | `python scripts/init_project.py "Name" --goal "..."` |
| `scripts/validate_state.py` | `python scripts/validate_state.py` |
| `scripts/detect_loops.py` | `python scripts/detect_loops.py <output1> <output2>` |
| `scripts/checkpoint.py` | `python scripts/checkpoint.py create\|restore` |
| `scripts/report.py` | `python scripts/report.py` |

## Quick Commands

| User Says | Action |
|-----------|--------|
| "Start project X" | Init → intake .deep-think/ → decompose → write .parallel/ |
| "Resume project" | CONTEXT.md → todo.md → state.yaml → continue |
| "Status?" | `scripts/report.py` |
| "Checkpoint" | Checkpoint → update CONTEXT.md |
| "Generate prompts" | Write .parallel/PLAN.md + contracts + prompts |
| "Results are ready" | Ingest .parallel/outputs/ → update state → next phase |
| "I'm stuck" | Create HUMAN_INPUT.md |

## Success Metrics

| Metric | Target |
|--------|--------|
| Session continuity | 90%+ tasks resume correctly |
| Prompt completeness | Zero questions from executor |
| Self-review catch rate | 70%+ issues found |
| Context efficiency | <80% usage per session |
| Human escalations | <10% of tasks |

---

*Project Orchestrator v3.1 — The planning brain. Reads .deep-think/, writes .parallel/, owns .orchestrator/*
