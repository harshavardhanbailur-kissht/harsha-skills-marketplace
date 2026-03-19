---
name: super-pipeline
description: "Think-plan-execute pipeline that routes tasks through deep thinking, orchestration, and parallel execution. Use for complex projects needing structured planning before building."
---


# Super Skill Pipeline

A complexity-gated router that chains deep thinking, orchestration, and parallel
execution — with adapter layers that solve the handoff problem between stages.

## Quick Reference

```
USER REQUEST
     │
     ▼
┌─────────────┐
│ COMPLEXITY  │
│    GATE     │
└──────┬──────┘
       │
  ┌────┴────┬──────────┬──────────────┐
  ▼         ▼          ▼              ▼
TRIVIAL   SMALL      MEDIUM        COMPLEX
  │         │          │              │
  ▼         ▼          ▼              ▼
 Just    Think       Think          Think
 do it   only        + Build        + Orchestrate
         (.deep-     (.deep-think   + Build
         think/)     → adapter →    (.deep-think
                     .parallel/)    → .orchestrator
                                    → adapter →
                                    .parallel/)
```

## Core Philosophy

The insight behind this pipeline: **Claude's context window is a scarce resource**.
Using the same session for both deep thinking AND execution wastes context on file
writes, test runs, and debugging — context that could have been spent thinking deeper.

This pipeline separates concerns:
- **Stage 1 (Think)**: Entire context dedicated to analysis. No code written.
- **Stage 2 (Orchestrate)**: Optional. State management for multi-day projects.
- **Stage 3 (Execute)**: Multiple sub-agents work in parallel from the plan.
- **Adapters**: Translate between stages so each can use its native format.

The pipeline is NOT mandatory for every task. The complexity gate ensures trivial
tasks skip everything, and most tasks skip the orchestrator.

---

## Stage 0: Complexity Gate (ALWAYS DO THIS FIRST)

Before doing anything else, assess the task's complexity. This takes 30 seconds
and determines the entire pipeline route.

### Assessment Questions

Ask yourself these four questions:

| Question | Low Signal | High Signal |
|----------|-----------|-------------|
| How many files does this change? | 1 file | Cross-system, 10+ files |
| Are there security/data implications? | No | Yes (auth, payments, PII) |
| Is this reversible? | Easy to undo | Breaking change, migration |
| Would an executor have questions? | Obvious approach | Multiple valid approaches |

### Complexity Decision Matrix

| Complexity | Signals | Pipeline Route | Directory Created |
|-----------|---------|----------------|-------------------|
| **TRIVIAL** | Single file, obvious fix, <5 min | Direct execution, no pipeline | None |
| **SMALL** | One component, bounded scope, 5-30 min | Think only | `.deep-think/` (3 files) |
| **MEDIUM** | Multiple components, integration points, 30 min - 4 hrs | Think → Adapter → Parallel | `.deep-think/` + `.parallel/` |
| **COMPLEX** | Cross-system, foundational, >4 hrs, multi-day, or architectural | Think → Orchestrate → Adapter → Parallel | All three + `.pipeline/` |

### Recording the Decision

Create `.pipeline/status.md` using the template in `templates/pipeline-status.md`.
Record the complexity level and reasoning. This serves as the audit trail and
resume point if the pipeline is interrupted.

```bash
mkdir -p .pipeline
```

**When in doubt, go one level deeper.** The cost of overthinking is tokens;
the cost of underthinking is rework.

**User override**: If the user explicitly says "just build it" or "don't overthink",
respect that — drop to TRIVIAL or SMALL regardless of signals.

---

## Route 1: TRIVIAL — Direct Execution

No pipeline. No directories. Just do the task.

This is the escape hatch. Most quick fixes, single-file edits, and obvious
changes should take this route. Don't force pipeline overhead on simple work.

---

## Route 2: SMALL — Think Only

**Load**: `skills/deep-thinker/SKILL.md`

Follow the deep-thinker skill at the "Small" complexity level:
- Create `.deep-think/` with 3 files: OVERVIEW, IMPLEMENTATION, EDGE_CASES
- Run 1 self-reflection iteration
- The output is the deliverable — user or another session executes from these files

**No adapter needed.** The deep-thinker output is the final product for SMALL tasks.

After completion, update `.pipeline/status.md` → stage: "complete".

---

## Route 3: MEDIUM — Think Then Build in Parallel

This is the **high-value path** — proven by real-world usage (the nokia_splash
project produced 8,600+ lines across 120+ files using this pattern).

### Phase 1: Deep Thinking

**Load**: `skills/deep-thinker/SKILL.md`

Run deep-thinker at "Medium" or "Complex" complexity level (6-8 files).
The critical output for the adapter is `EXECUTION_CHECKLIST.md` — make sure
the deep-thinker produces clear, structured tasks with verification criteria.

**Coaching the deep-thinker for adapter compatibility**:

When writing EXECUTION_CHECKLIST.md, the deep-thinker should structure tasks
in a way the adapter can parse. This doesn't mean rigid formatting — it means
including these elements naturally:

- Clear phase/section boundaries (numbered phases or headers)
- Explicit deliverables (file paths for each task)
- Dependency language ("after X", "requires Y", "once Z is done")
- Verification criteria ("verify by", "test with", "confirm that")

The deep-thinker doesn't need to know about the adapter — it just needs to
write a thorough checklist. The adapter handles the translation.

### Phase 2: ThinkingCompiler Adapter

**Load**: `references/adapter-thinking-compiler.md`

This is where the magic happens. The adapter reads the deep-thinker's output
and produces a structured parallel execution plan.

**Step-by-step**:

1. Read `.deep-think/EXECUTION_CHECKLIST.md` — extract individual tasks
2. Read `.deep-think/ARCHITECTURE.md` — infer dependency relationships
3. Read `.deep-think/IMPLEMENTATION.md` — gather technical details for prompts
4. Read `.deep-think/OVERVIEW.md` — get project scope for sub-agent context
5. Optionally read EDGE_CASES.md, OPTIMIZATIONS.md — enrich prompts
6. Build the dependency graph from explicit + inferred signals
7. Compute execution layers via topological sort (Kahn's algorithm):
   - Layer 0: all tasks with no dependencies (launch simultaneously)
   - Layer 1: tasks depending only on Layer 0 tasks
   - Layer N: tasks depending on Layer N-1
8. Generate self-contained sub-agent prompts for each task
9. Create interface contracts for cross-task integration points
10. Write `.parallel/PLAN.md` using `templates/plan-from-thinking.md`
11. Write individual prompts to `.parallel/prompts/`
12. Create `.parallel/contracts/` if cross-task interfaces exist

**Create the directory structure**:
```bash
mkdir -p .parallel/{contracts,prompts,outputs,reports}
```

**Quality gate before proceeding**:
- Every task from EXECUTION_CHECKLIST is in PLAN.md
- No circular dependencies
- Layer 0 has 2+ tasks (otherwise parallel adds no value)
- Sub-agent prompts are self-contained

### Phase 3: Parallel Execution

**Load**: `skills/parallel-builder/ARCHITECTURE.md` for execution patterns

Now execute the plan. For each layer, launch all tasks simultaneously using
the Agent tool (subagent_type: "general-purpose").

**Execution protocol**:

```
For Layer 0:
  Launch ALL tasks in a SINGLE message (multiple Agent tool calls)
  Each agent gets its prompt from .parallel/prompts/TASK-XXX-prompt.md
  Each agent saves output to .parallel/outputs/TASK-XXX-summary.md
  Wait for ALL to complete

For Layer 1:
  Inject Layer 0 outputs into Layer 1 prompts (dependency context)
  Launch ALL Layer 1 tasks simultaneously
  Wait for ALL to complete

Repeat for each layer...
```

**Sub-agent launch template**:
```
Execute this task autonomously:

[Contents of .parallel/prompts/TASK-XXX-prompt.md]

Save your output summary to: .parallel/outputs/TASK-XXX-summary.md
Save any code files to the paths specified in the deliverables section.
```

### Phase 4: Verification

After all layers complete:

1. Check that all expected deliverables exist
2. Read `.parallel/outputs/` summaries — verify each task's acceptance criteria
3. Check interface contracts — do the pieces fit together?
4. If issues found: create targeted fix tasks and run them
5. Update `.pipeline/status.md` → stage: "complete"

---

## Route 4: COMPLEX — Full Pipeline (Think → Orchestrate → Build)

Use this route for multi-day projects, projects requiring session continuity,
or when the orchestrator's state management genuinely adds value.

**V3.1 orchestrator has native pipeline support.** Unlike V2, the orchestrator v3.1
reads `.deep-think/` directly (Section 2: Deep-Thinker Intake Protocol) and writes
to `.parallel/` directly (Section 5: Writing to .parallel/). No manual adapter needed
for this route — the orchestrator IS the adapter.

### Phase 1: Deep Thinking

Same as Route 3 Phase 1, but at "Complex" level (all 8 files).
Extra emphasis on ARCHITECTURE.md — the orchestrator will use it for ADRs.
Extra emphasis on EDGE_CASES.md — the orchestrator uses it for acceptance criteria.

### Phase 2: Orchestrator Intake (Native — No Adapter Needed)

**Load**: `skills/orchestrator/SKILL.md` — specifically Section 2

The V3.1 orchestrator reads `.deep-think/` files in this order:
1. `OVERVIEW.md` → project goal, scope, success criteria
2. `ARCHITECTURE.md` → constraints, patterns, ADR candidates
3. `IMPLEMENTATION.md` → task boundaries, file dependencies, sequencing
4. `EDGE_CASES.md` → acceptance criteria, verification scenarios
5. `CURRENT_STATE.md` → existing code analysis
6. `OPTIMIZATIONS.md` → quality criteria, performance targets
7. `CREATIVE_IDEAS.md` → stretch goals (tagged as optional)
8. `EXECUTION_CHECKLIST.md` → step-by-step hints (validated against MECE)

**Intake actions** (the orchestrator does these automatically):
1. Populates `state.yaml` project section from OVERVIEW + ARCHITECTURE
2. Creates ADRs in `.orchestrator/knowledge/adr/` from ARCHITECTURE.md decisions
3. Logs failed approaches in `.orchestrator/knowledge/failures/` from EDGE_CASES.md
4. Begins MECE decomposition using IMPLEMENTATION.md as primary input

Initialize with:
```bash
python skills/orchestrator/scripts/init_project.py "Project Name" --goal "Goal"
```

### Phase 3: Orchestrator Planning + Prompt Generation

**Continue with**: `skills/orchestrator/SKILL.md` — Sections 3-5

The orchestrator:
1. **Decomposes** into MECE tasks (Section 3) with layer assignments for parallelization
2. **Captures knowledge** — ADRs, failure logs, research findings (Section 6)
3. **Writes to .parallel/** (Section 5) — this is the critical output:
   - `.parallel/PLAN.md` — dependency graph in parallel-skill-builder's format
   - `.parallel/contracts/TASK-{id}.md` — interface contracts per task
   - `.parallel/prompts/TASK-{id}.md` — self-contained execution prompts

**Key V3.1 feature**: Execution prompts are **compaction-proof**. Each prompt embeds
ALL context so a fresh Claude window executes with zero questions. Nothing lives
only in memory. This solves the handoff problem at the source.

**Quality gate** (from V3.1's "Pickup Test"):
For each prompt, ask: "Can someone with zero context pick this up and know
exactly what to build, how to verify it, and what NOT to build?"
If no → add more context to the prompt.

### Phase 4: Parallel Execution

**Load**: `skills/parallel-builder/ARCHITECTURE.md` for execution patterns

The orchestrator has already written everything to `.parallel/`. Now dispatch:

```
For each layer in .parallel/PLAN.md:
  Launch ALL tasks simultaneously (Agent tool, multiple calls in one message)
  Each agent reads its prompt from .parallel/prompts/TASK-{id}.md
  Each agent writes output to .parallel/outputs/TASK-{id}/
  Wait for ALL to complete before next layer
```

### Phase 5: Results Ingestion (V3.1 Section 7)

**Load**: `skills/orchestrator/SKILL.md` — Section 7

After parallel execution completes, the orchestrator reads results back:
1. Read `.parallel/reports/EXECUTION_REPORT.md` for completion status
2. For each task in `.parallel/outputs/TASK-{id}/`:
   - Verify against acceptance criteria
   - If PASS → mark "verified" in state.yaml
   - If FAIL → mark "blocked", create failure log, plan remediation
3. Update `.orchestrator/CONTEXT.md` with what was accomplished
4. Update `.orchestrator/todo.md` (attention anchor) with next phase
5. If more phases remain → generate prompts for next phase (back to Phase 3)
6. If all complete → run completion checklist

### Phase 6: Multi-Session Continuity

For multi-day projects, the orchestrator's state persists across sessions:
- **Resume**: Read CONTEXT.md → todo.md → state.yaml (always this order)
- **Checkpoint**: `python skills/orchestrator/scripts/checkpoint.py create`
- **Status**: `python skills/orchestrator/scripts/report.py`
- **Loop detection**: If stuck, `python skills/orchestrator/scripts/detect_loops.py`

---

## Feedback Loops (Handling Failures)

Real projects don't flow linearly. Here's how to handle backtracking:

### Parallel Builder Finds a Design Flaw

If a sub-agent discovers the architecture won't work:
1. Document the issue in `.parallel/reports/ISSUE-XXX.md`
2. Pause remaining tasks in the affected dependency chain
3. Options:
   a. **Minor fix**: Create a targeted fix task, run it, continue
   b. **Major flaw**: Go back to deep-thinker for re-analysis of the specific area
      (don't redo the entire analysis — surgical update to the relevant files)
   c. **Architectural change**: Flag for user review in `.pipeline/status.md`

### Adapter Can't Parse Deep-Thinker Output

If EXECUTION_CHECKLIST.md is too unstructured for the adapter:
1. Create `.pipeline/ADAPTER_ERROR.md` (see contract in `references/pipeline-contracts.md`)
2. Options:
   a. Ask the user for clarification
   b. Re-run the deep-thinker with a prompt: "Rewrite EXECUTION_CHECKLIST.md with
      explicit phases, numbered tasks, and dependency signals"
   c. Skip the adapter and run the parallel-builder with inline planning
      (the nokia_splash approach — proven to work)

### Context Window Running Low

If context usage exceeds 70% during any stage:
1. Complete the current stage's output files
2. Create a resume point in `.pipeline/status.md`
3. Tell the user: "I've completed [stage]. To continue, start a new session and
   say 'resume pipeline' — all progress is saved in the directories."

---

## Resuming an Interrupted Pipeline

When the user says "resume" or "continue":

1. Check for `.pipeline/status.md` — read current stage
2. Based on the stage, load the appropriate files:
   - "thinking" → Read `.deep-think/` files, continue analysis
   - "adapting" → Read `.deep-think/`, run the adapter
   - "orchestrating" → Read `.orchestrator/CONTEXT.md` + `state.yaml`
   - "parallelizing" → Read `.parallel/PLAN.md`, check which tasks are done
   - "verifying" → Read `.parallel/outputs/`, run verification
3. Continue from where it left off

If `.pipeline/status.md` doesn't exist but `.deep-think/` does:
- Infer the pipeline was interrupted during or after thinking
- Read the deep-think files, assess completeness, and continue

---

## Reference Files

Load these as needed — don't load everything upfront:

| File | When to Load | Purpose |
|------|-------------|---------|
| `references/pipeline-contracts.md` | When building adapters | Schema definitions for handoffs |
| `references/adapter-thinking-compiler.md` | Route 3 Phase 2 | Converting .deep-think → .parallel (when orchestrator is SKIPPED) |
| `references/adapter-state-extractor.md` | Rarely — fallback only | Converting .orchestrator → .parallel (V3.1 does this natively) |
| `skills/deep-thinker/SKILL.md` | Routes 2-4, Phase 1 | Deep thinking methodology |
| `skills/orchestrator/SKILL.md` | Route 4, Phases 2-5 | V3.1: native pipeline — reads .deep-think/, writes .parallel/ |
| `skills/parallel-builder/ARCHITECTURE.md` | Routes 3-4, execution | Parallel execution patterns |
| `skills/parallel-builder/SKILL.md` | Routes 3-4, execution | Parallel dispatch and verification |

## Sub-Skill References

The three bundled sub-skills have their own reference files. Load them through
the sub-skill's SKILL.md — it will tell you which references to load and when.

Key V3.1 orchestrator references (loaded via its SKILL.md):
- `prompt-architecture.md` — How to write compaction-proof execution prompts
- `knowledge-capture.md` — ADRs, failure logs, PARA organization
- `verification-patterns.md` — SMART-T criteria, debugging agents

## Adapter Usage Guide

**Route 3 (MEDIUM)**: Uses `adapter-thinking-compiler.md` — the orchestrator is skipped,
so we need the adapter to translate .deep-think/ → .parallel/ directly.

**Route 4 (COMPLEX)**: The V3.1 orchestrator handles the translation natively
(Section 2: intake, Section 5: output to .parallel/). The adapter-state-extractor
is only needed as a fallback if using a pre-V3.1 orchestrator.

## Anti-Patterns

- **Don't force all 3 stages on every task.** The complexity gate exists for a reason.
  Most tasks are TRIVIAL or SMALL. Let them be.
- **Don't load all sub-skills upfront.** Load the deep-thinker SKILL.md only when
  entering the thinking stage. Load the orchestrator only for Route 4.
- **Don't skip the adapter on Route 3.** Going directly from .deep-think/ to .parallel/
  without the ThinkingCompiler adapter is why delegator-frontend's parallel directory was empty.
- **Don't use the adapter on Route 4.** The V3.1 orchestrator reads .deep-think/ and
  writes .parallel/ natively. Using the adapter on top would create duplicate/conflicting output.
- **Don't over-orchestrate.** The orchestrator adds value for multi-day, multi-session
  projects. For single-session work, skip it (Route 3 > Route 4 in most cases).
- **Don't ignore the complexity gate output.** If the gate says SMALL, trust it.
- **Don't summarize upstream outputs in prompts.** V3.1 rule: pass verbatim, never summarize.
  Summaries lose the details that make execution prompts self-contained.

---

*Super Skill Pipeline v1.1 — Think deep. Plan smart. Build in parallel.*
*Orchestrator upgraded to V3.1 (native pipeline support). Deep-thinker confirmed v3 (latest).*
*Based on analysis of 6+ real-world deployments across Elemental Clash, delegator-frontend,
nokia_splash, services-website, Journal, and PropHit-Revamp.*
