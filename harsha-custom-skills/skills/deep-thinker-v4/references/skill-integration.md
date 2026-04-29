# Skill Integration: Deep Thinker v4.0

## The Boundary: Thinker vs. Executor

**Deep Thinker owns:**
- Problem framing (SCOPE phase)
- Model building (GROUND phase)
- Exploring alternatives (DIVERGE phase)
- Risk identification (STRESS phase)
- Decision synthesis (SYNTHESIZE phase)
- Annotation of what-to-do-and-why (EXECUTION_CHECKLIST.md)

**Executor skills own:**
- Writing code, modifying files, running commands
- Implementing decisions from EXECUTION_CHECKLIST.md
- Handling real-time feedback and iteration
- Validating assumptions in practice
- Reporting back learnings

**Handoff mechanism:** EXECUTION_CHECKLIST.md with skill annotations tells executors what to do and in what order.

---

## Core Domain Skills Reference

Use these in EXECUTION_CHECKLIST annotations:

| Skill | Domain | When to Tag | Output Type |
|-------|--------|------------|------------|
| **ui-ux-mastery** | UX/UI design, design systems, accessibility | Design decisions, component layout, interaction flow | Figma/mockups or code |
| **shadcn-ui-mastery** | React + shadcn/ui implementation | Building with shadcn components, theming, responsive | React components |
| **gas-debugger** | Production debugging, performance, analytics | Investigating failures, profiling, traces | Diagnosis + fix code |
| **frontend-blitz** | Rapid frontend prototyping, rapid iteration | Speed-critical UI development, POCs | Working frontend |
| **security-audit** | Security review, threat modeling, compliance | Auditing code for vulnerabilities, architecture review | Audit report + fixes |
| **workflow-guardian** | Preventing breaking changes, regression testing | Validating changes against existing workflows | Test suite + validation |
| **mobile-mastery** | Mobile app development, cross-platform | iOS/Android specific decisions, mobile UX | Mobile app/library |
| **web-brainstorm** | Architecture exploration, tech decisions | Early-stage design, system topology | Architecture docs |
| **parallel-builder** | Feature decomposition, parallel implementation | Breaking work into parallel streams | Task breakdown + ownership |
| **orchestrator** | Coordinating multi-skill workflows | Sequencing executor skills, managing dependencies | Delegation + coordination |

---

## Annotation Pattern in EXECUTION_CHECKLIST.md

Format: `- [ ] Task name @skill-tag #dependency`

### Example Task with Full Annotation

```markdown
## Phase 3: DIVERGE

- [ ] Design payment flow for Obvious path @ui-ux-mastery @shadcn-ui-mastery
  - **Why**: Establish visual hierarchy and interaction model
  - **Success**: Mockups show 3 screens, 2 error states, mobile responsive
  - **Depends-on**: GROUND phase model validation (from GROUND.md)
  - **Rationale**: From DIVERGE.md PATH A (Obvious), assumes simple sequential flow

- [ ] Threat model for Contrarian path @security-audit
  - **Why**: Contrarian uses OAuth flow; audit for token handling
  - **Success**: Audit report identifies 0 high-severity gaps
  - **Depends-on**: Security requirements from SCOPE.md
  - **Risk**: If audit finds critical gaps, shifts us back to Obvious

## Phase 4: STRESS

- [ ] Code review against red-team findings @workflow-guardian
  - **Why**: Validate chosen path doesn't break existing user flows
  - **Success**: Regression test suite passes 100%
  - **Blocks**: Phase 5 SYNTHESIZE cannot start until this passes
  - **Mitigates**: From STRESS.md, "Integration risk: breaking user logout flow"
```

### Annotation Grammar

**Skill tags** (can have multiple):
- `@skill-name` maps to the executor skill that owns this task
- For architecture tasks: `@web-brainstorm`
- For implementation: `@shadcn-ui-mastery`, `@gas-debugger`, etc.

**Dependency language:**
- `depends-on`: This task waits for [other task/file] to complete
- `blocks`: This task prevents [other tasks] from starting
- `parallel-with`: This can run simultaneously with [other task]

**Rationale callouts:**
- Link to DIVERGE.md/STRESS.md findings explaining WHY this task exists
- Quote the trade-off or risk being mitigated

---

## Skill-Domain Mapping Table

Use this when deciding which skills to activate:

| Problem Domain | Primary Skill | Supports | Notes |
|---|---|---|---|
| Visual/interaction design | ui-ux-mastery | shadcn-ui-mastery, frontend-blitz | Design-first; code follows |
| React + shadcn components | shadcn-ui-mastery | ui-ux-mastery, frontend-blitz | Implementation details |
| Performance/stability issues | gas-debugger | workflow-guardian, security-audit | Deep investigation |
| Mobile/cross-platform | mobile-mastery | ui-ux-mastery, parallel-builder | Platform-specific |
| Tech selection, architecture | web-brainstorm | parallel-builder, security-audit | High-level strategy |
| Preventing regressions | workflow-guardian | security-audit, mobile-mastery | Validation at scale |
| Threat modeling, compliance | security-audit | workflow-guardian, mobile-mastery | Risk mitigation |
| Parallel execution planning | parallel-builder | [any domain skill] | Orchestration layer |
| Multi-skill orchestration | orchestrator | [all domain skills] | Coordination only |

---

## Pipeline Compatibility: Feeding EXECUTION_CHECKLIST to ThinkingCompiler

**ThinkingCompiler adapter** reads EXECUTION_CHECKLIST.md and extracts:

### Phase Extraction
```
Regex: /^## Phase \d: [A-Z]+/
Extracts: Phase number, phase name
Maps to thinking mode: SCOPE→shallow, GROUND→medium, DIVERGE+→deep
```

### Checkbox Extraction
```
Pattern: - [ ] Task name @skill-tag #dependency
Extracts:
  ├─ Task description
  ├─ Skill tags (list)
  ├─ Dependency references
  └─ Completion status (checked/unchecked)
```

### Metadata Extraction
```
Pattern: [[ **Key**: Value ]]
Extracts: All inline metadata (Why, Success, Depends-on, Blocks, Risk, Mitigates)
```

### Verification Criteria Extraction
```
Looks for: "Success: ..." line for each task
Provides to skill: measurable acceptance criteria
```

**Adapter output format (for orchestrator):**
```yaml
phases:
  - number: 3
    name: DIVERGE
    tasks:
      - id: task-001
        description: "Design payment flow for Obvious path"
        skills: ["ui-ux-mastery", "shadcn-ui-mastery"]
        dependencies: ["ground-phase-complete"]
        verification: "Mockups show 3 screens, 2 error states, mobile responsive"
        phase_dependencies: "GROUND.md model validation"
        rationale: "DIVERGE.md PATH A"
```

---

## Adapter Extraction Patterns

### How Adapters Find Skill Boundaries

Adapters scan EXECUTION_CHECKLIST for:

1. **Skill activation**: Any task with `@skill-name` triggers that skill's entrance
2. **Skill exit**: Next `@different-skill` or new phase ends prior skill
3. **Handoff boundaries**: When skill changes, artifact path and verification criteria are passed

**Example extraction:**
```
[EXTRACT FROM EXECUTION_CHECKLIST]
- [ ] Design payment flow @ui-ux-mastery
  - **Success**: Mockups in ./designs/payment-flow.md

[ADAPTER OUTPUT TO ORCHESTRATOR]
Skill: ui-ux-mastery
Input: { phase: DIVERGE, task_id: task-001 }
Input_artifact_path: ./designs/payment-flow.md
Verification: Mockups show 3 screens, 2 error states, mobile responsive
Exit_condition: Artifact exists AND verification passes
Output_to_next: ./designs/payment-flow.md → task-002 @shadcn-ui-mastery
```

---

## Cross-Skill Coordination: Thinker → Orchestrator → Executor

### 1. Deep-Thinker → Orchestrator Handoff
```
Input: EXECUTION_CHECKLIST.md + all .deep-think/ files
Orchestrator reads:
  ├─ All phase markers and task order
  ├─ All @skill-tags and their sequence
  ├─ All #dependencies and parallelization points
  └─ All rationales linking back to thinking phases
```

### 2. Orchestrator → Executor Skills Handoff
```
For each task:
  1. Read skill annotation (@skill-name)
  2. Extract verification criteria ("Success: ...")
  3. Pass context: rationale, dependencies, artifact paths
  4. Execute skill with EXECUTION_CHECKLIST as guide
  5. Receive artifact + completion signal
  6. Move to next task or parallel task
```

### 3. Feedback Loop Back to Thinking
```
If executor discovers:
  ├─ Task is impossible → Return to DIVERGE phase
  ├─ Verification fails → Return to STRESS phase
  ├─ Assumption breaks → Return to GROUND phase
  └─ Success → Proceed to next task
```

---

## Executor Skill Integration Checklist

When adding a new executor skill to the ecosystem, ensure:

- [ ] Skill knows how to read EXECUTION_CHECKLIST.md format
- [ ] Skill extracts @its-tag and runs only that task
- [ ] Skill respects #dependency ordering
- [ ] Skill produces artifacts at paths specified in EXECUTION_CHECKLIST
- [ ] Skill validates against "Success: ..." criteria before completion
- [ ] Skill can report back: "artifact created at [path], verification passed"
- [ ] Skill documents: what input format, what output format, what verification means
- [ ] Skill can handle: "This task blocked by [dependency]. Skip for now."
- [ ] Skill links output back to DIVERGE.md rationale (in comments if code, in metadata if doc)

**Integration pattern:** All skills follow same entry/exit contract. Deep-Thinker doesn't need to know skill internals—just format of EXECUTION_CHECKLIST.
