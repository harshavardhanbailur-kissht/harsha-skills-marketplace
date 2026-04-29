# State Management: Deep Thinker v4.0

## The .deep-think/ Directory Structure

All analysis outputs live in `.deep-think/` relative to the project root. Create this directory at analysis start.

### 8-File Manifest

| File | Phase(s) | Purpose | Save Timing |
|------|----------|---------|-------------|
| **OVERVIEW.md** | All | Single-source truth: problem, approach, decisions, status | After SCOPE; updated end of each phase |
| **SCOPE.md** | SCOPE | Problem framing, success metrics, constraints, complexity gate | End of Phase 1 |
| **GROUND.md** | GROUND | Domain model, assumptions, facts, dependencies, edge cases | End of Phase 2 |
| **DIVERGE.md** | DIVERGE | 3 paths (Obvious/Contrarian/Minimum), trade-off matrix | End of Phase 3 |
| **STRESS.md** | STRESS | Failure modes, red-team findings, mitigations, recovery narratives | End of Phase 4 |
| **EXECUTION_CHECKLIST.md** | STRESS→SYNTHESIZE | Annotated tasks, skill tags, dependency tracking, verification criteria | End of Phase 4; final review Phase 5 |
| **CONFIDENCE_TAGS.md** | SYNTHESIZE | Confidence levels per major decision, reasoning, measurement plan | End of Phase 5 |
| **PRE_MORTEM.md** | SYNTHESIZE | Structured pre-mortem narrative, what could go wrong, recovery plans | End of Phase 5 |

---

## Information Flow Between Files

```
OVERVIEW (Single Source of Truth)
├─ Anchors to SCOPE.md (problem framing)
├─ Anchors to GROUND.md (validated model)
├─ Anchors to DIVERGE.md (chosen path)
├─ Anchors to STRESS.md (mitigations)
└─ Anchors to EXECUTION_CHECKLIST.md (next steps)

EXECUTION_CHECKLIST (Synthesis Point)
└─ Synthesizes decisions from all earlier phases
   ├─ SCOPE: constraints embedded as verification criteria
   ├─ GROUND: model assumptions tagged for monitoring
   ├─ DIVERGE: trade-off justifications in comments
   ├─ STRESS: mitigations as parallel tasks
   └─ CONFIDENCE_TAGS & PRE_MORTEM: risk awareness in handoff notes
```

**Key Invariant:** OVERVIEW always reflects latest phase completion. EXECUTION_CHECKLIST is the final artifact that executor skills read.

---

## Progressive Writing Pattern

Each phase produces and saves one file before the next phase starts:

```
Phase 1 (SCOPE)
  → Write SCOPE.md
  → Update OVERVIEW.md
  → Lock (don't rewrite)

Phase 2 (GROUND)
  → Write GROUND.md
  → Update OVERVIEW.md with model summary
  → Reference SCOPE.md (don't modify)

Phase 3 (DIVERGE)
  → Write DIVERGE.md
  → Update OVERVIEW.md with chosen path
  → Reference SCOPE.md + GROUND.md

Phase 4 (STRESS)
  → Write STRESS.md
  → Write EXECUTION_CHECKLIST.md (draft)
  → Update OVERVIEW.md with mitigations

Phase 5 (SYNTHESIZE)
  → Finalize EXECUTION_CHECKLIST.md
  → Write CONFIDENCE_TAGS.md
  → Write PRE_MORTEM.md
  → Final OVERVIEW.md update: "READY FOR HANDOFF"
```

**Why locking matters:** Prevents scope creep and maintains traceability. If GROUND reveals issues, open SCOPE only to document why assumptions changed—don't rewrite it.

---

## Content Guidelines per File Type

### OVERVIEW.md (200-300 words)
- **What**: 1 sentence problem statement
- **Why**: Success metrics + constraints (3-5 bullets)
- **How**: Chosen approach + key decisions (3-5 bullets)
- **Status**: Current phase + completion criteria
- **Links**: Full file references (relative paths)
- **Update cycle**: End of every phase

### SCOPE.md (300-400 words)
- Problem statement (expanded from OVERVIEW)
- Success metrics + measurement approach
- Hard constraints (time, resources, dependencies)
- Out-of-scope items (what we're NOT doing)
- Complexity assessment (complexity gate decision)
- Assumptions being accepted (for later validation)
- Open questions entering GROUND phase

### GROUND.md (400-500 words)
- Domain model: core concepts, relationships, behaviors
- Facts established (sources cited)
- Assumptions validated or rejected
- Dependencies mapped (internal and external)
- Edge cases identified
- Unknowns remaining (for DIVERGE exploration)
- Model validation: how do we know this is right?

### DIVERGE.md (500-600 words)
- PATH A (THE OBVIOUS): implementation, risks, benefits, costs
- PATH B (THE CONTRARIAN): inverted assumption, design, viability, complexity
- PATH C (THE MINIMUM): reduction principle, scaling story, trade-offs
- Trade-off matrix: (Obvious vs Contrarian vs Minimum) on (Speed, Cost, Risk, Complexity)
- Chosen path + rationale (WHY, not just WHAT)
- Rejected path learnings: what did we gain by exploring them?

### STRESS.md (400-500 words)
- Red-team review: top 3 vulnerabilities in chosen path
- Failure modes: scenarios where solution breaks
- Mitigations: concrete actions to reduce each risk
- Recovery narratives: if it fails, how do we recover?
- Scaling concerns: assumptions that break under load
- Integration risks: where does it touch other systems?

### EXECUTION_CHECKLIST.md (600-800 words)
- Phase markers: `## Phase 1: SCOPE` through `## Phase 5: SYNTHESIZE`
- Checkbox format: `- [ ] Task name @skill-tag #dependency`
- Skill annotations: `@ui-ux-mastery`, `@gas-debugger`, etc.
- Dependency language: `blocks`, `depends-on`, `parallel-with`
- Verification criteria: each task includes success definition
- Risk mitigation callouts: linked to STRESS.md findings
- Comments with rationale from DIVERGE phase

### CONFIDENCE_TAGS.md (300-400 words)
- Major decisions + confidence levels (High/Medium/Low)
- For each decision: confidence reasoning + measurement plan
- Calibration: what would move confidence up or down?
- Monitoring criteria: what metrics signal this decision is working?
- Escalation triggers: when do we revisit this decision?

### PRE_MORTEM.md (400-500 words)
- Narrative: "It's 3 months from now. The project failed."
- What went wrong: 3-5 failure stories
- Root causes: trace back from failure to root assumption
- Prevention strategies: what should we do differently?
- Early warning signs: what metrics signal trouble?
- Recovery protocols: if we detect warning signs, what's the playbook?

---

## Quality Criteria per File

| File | Completeness | Clarity | Actionability |
|------|--------------|---------|---------------|
| OVERVIEW.md | Links to all other files | No jargon; CEO-readable | Clear next phase entry point |
| SCOPE.md | All constraints named | Problem restatable in 1 sentence | Metrics measurable today |
| GROUND.md | Model predicts edge cases | Diagrams > walls of text | Facts traceable to source |
| DIVERGE.md | 3 paths clearly separated | Trade-offs quantified where possible | Path choice justified |
| STRESS.md | Failure modes named | Mitigations have owners | Recovery playbook is runnable |
| EXECUTION_CHECKLIST.md | All tasks have skill tags | Each task has success criterion | Can hand to executor today |
| CONFIDENCE_TAGS.md | All major decisions tagged | Measurement plan is specific | Escalation triggers clear |
| PRE_MORTEM.md | 3-5 distinct failure stories | Narratives, not bullet lists | Early warning signs measurable |

---

## File Persistence & Context Compaction

**.deep-think/ survives context resets because:**

1. **Directory is project-local**, not in any single file that gets overwritten
2. **Each file is immutable** once saved (unless explicitly reopened for updates)
3. **OVERVIEW.md acts as index**: new Claude sessions can read it and find all related files
4. **Progressive writing**: If context compacts mid-analysis, completed files are safe; reopen OVERVIEW to resume

**Context recovery pattern:**
```
If context compacts before Phase 5 completion:
1. Read OVERVIEW.md to understand current status
2. Read latest completed file (e.g., DIVERGE.md if in Phase 4)
3. Resume from last saved checkpoint
4. Update OVERVIEW.md with "resumed from [phase]"
```

**Recommended file sizes:** Keep each file 300-600 words. Exceeding this signals scope creep or lack of editing.
