# Project Orchestrator Workflow Guide

Complete end-to-end workflow for using the Project Orchestrator skill.

---

## Overview

The Project Orchestrator transforms vague project ideas into execution-ready task lists
with embedded context that survives AI context compaction. This guide walks through
the complete workflow from intake to verification.

---

## Phase 1: Project Intake & Shaping

### Input
- Vague project idea, feature request, or problem statement

### Process

1. **Define the Appetite**
   - How much time is this worth? (not "how long will it take")
   - Fixed time, variable scope
   - Options: Small Batch (1-2 days), Medium Batch (1-2 weeks), Big Batch (6 weeks)

2. **Establish Boundaries**
   - What's explicitly OUT of scope?
   - What's the "nice to have" vs "must have"?
   - What are we NOT building?

3. **Identify the Solution Shape**
   - What's the high-level approach?
   - What are the major components?
   - What are the riskiest parts?

4. **Define Success**
   - What does "done" look like?
   - How will we know it works?
   - What's the minimum viable outcome?

### Output
```markdown
## Shaped Concept: [Project Name]

**Appetite**: [Time budget]

**Problem**: [What we're solving]

**Solution Approach**: [High-level how]

**Boundaries**:
- IN: [What's included]
- OUT: [What's excluded]

**Success Criteria**:
- [Measurable outcome 1]
- [Measurable outcome 2]

**Risks**:
- [Known risk 1]
- [Known risk 2]
```

---

## Phase 2: Task Decomposition

### Input
- Shaped concept from Phase 1

### Process

1. **Identify Phases**
   - What are the major milestones?
   - What must complete before what?
   - Where are the natural checkpoints?

2. **Break into Tasks**
   - Target 2-4 hour tasks
   - Use action verbs: Implement, Create, Configure, Write, Test
   - One objective per task
   - Include acceptance criteria

3. **Map Dependencies**
   - What blocks what?
   - What can run in parallel?
   - Minimize dependencies through vertical slicing

4. **Size and Estimate**
   - S: <2 hours
   - M: 2-4 hours
   - L: 4-8 hours
   - If >8 hours, break down further

5. **Identify Research Needs**
   - What don't we know?
   - Create timeboxed spikes
   - Output required even if timebox expires

### Use Template
`templates/task-definition.md` for each task
`templates/spike-task.md` for research tasks
`templates/project-plan.md` for overall structure

### Output
```markdown
# Project: [Name]
## Appetite: [Time] | [N] tasks | ~[X] hours

### PHASE 1: [Name]
- [ ] #1 [Task] (S/M/L)
- [ ] #2 [Task] (S/M/L) — BLOCKED BY: #1

### PHASE 2: [Name]
- [ ] #3 [Task] (S/M/L)
...

### NEXT ACTIONS:
1. #[N] [First task to execute]

### DISCOVERY:
- [ ] SPIKE: [Question] ([timebox])
```

---

## Phase 3: Knowledge Capture Setup

### Input
- Decomposed task list
- Any existing decisions or constraints

### Process

1. **Initialize Decision Log**
   - Create ADR folder structure
   - Document any decisions already made
   - Use `templates/adr.md`

2. **Create Failure Log**
   - Prepare for documenting what doesn't work
   - Use `templates/failure-log.md`

3. **Establish Research Repository**
   - Where findings will be stored
   - Use `templates/research-finding.md`

4. **Set Up Context Snippets**
   - For handoffs between sessions
   - Use `templates/context-snippet.md`

### Triggers to Remember
| Event | Action | Template |
|-------|--------|----------|
| Architectural decision | Create ADR | adr.md |
| Failed approach | Document | failure-log.md |
| Research insight | Capture | research-finding.md |
| Session end | Context snapshot | context-snippet.md |
| Constraint discovered | Add to docs | Inline |

---

## Phase 4: Skill Mapping & Prompt Generation

### Input
- Task definitions with acceptance criteria

### Process

1. **Identify Required Skills**
   For each task, determine what capabilities are needed:
   - Code execution?
   - Web search?
   - File creation?
   - Specific domain knowledge?

2. **Generate Execution Prompts**
   - Use `templates/execution-prompt.md`
   - Include all context (assume fresh AI)
   - Embed relevant code snippets
   - Specify constraints and success criteria

3. **Verify Prompt Completeness**
   - Fresh Context Test: Would this make sense with no prior conversation?
   - All code references included inline?
   - Success criteria measurable?

### Execution Prompt Checklist
- [ ] Intent stated (why this matters)
- [ ] Tech stack with versions
- [ ] Existing code snippets included
- [ ] Interface contracts defined
- [ ] MUST/MUST NOT constraints
- [ ] Success criteria (binary verifiable)
- [ ] Out of scope explicit

---

## Phase 5: Execution

### Input
- Execution-ready prompts
- Task list with dependencies resolved

### Process

1. **Execute Next Action**
   - Pick from NEXT ACTIONS list
   - Use the generated execution prompt
   - Stay within scope boundaries

2. **Capture Knowledge as You Go**
   - Document decisions immediately
   - Log failed approaches
   - Note constraints discovered

3. **Update Task Status**
   - Mark complete when criteria met
   - Move next tasks to NEXT ACTIONS
   - Update blockers as resolved

4. **Create Context Snapshots**
   - Before ending a session
   - When significant progress made
   - When handing off to another executor

### Execution Cadence
```
For each task:
1. Review acceptance criteria
2. Execute with prompt
3. Verify criteria met
4. Update task status
5. Capture knowledge
6. Update context snapshot
```

---

## Phase 6: Verification

### Input
- Completed task
- Original acceptance criteria
- Execution artifacts

### Process

1. **Run Automated Checks**
   - Build passes?
   - Tests pass?
   - Linting clean?
   - Coverage maintained?

2. **Criterion-by-Criterion Verification**
   - For EACH acceptance criterion:
     - State the criterion
     - Find the evidence
     - Evaluate: PASS/FAIL/CANNOT_VERIFY
     - Document gaps

3. **Scope Analysis**
   - Missing: specified but not implemented
   - Extraneous: implemented but not specified
   - Deviated: different from specification

4. **Generate Verification Report**
   - Use `templates/verification-report.md`
   - Include all findings
   - Provide recommendations

### Use Template
`templates/debugging-agent.md` for the full debugging prompt
`templates/verification-report.md` for output format

---

## Phase 7: Remediation (If Needed)

### Input
- Verification report with failures

### Process

1. **Triage Errors**
   - Critical: Blocking, fix immediately
   - High: Major feature broken, this sprint
   - Medium: Impaired, workaround exists, next sprint
   - Low: Minor, backlog

2. **Decide: Patch or Replan**
   - Patch if: Isolated, clear cause, low risk
   - Replan if: Systemic, design-level, recurring

3. **Create Fix Tasks**
   - Use `templates/task-definition.md`
   - Reference original error
   - Include regression test requirement
   - Scope constraints: limit to affected area

4. **Add to Task List**
   - Same backlog, different labels
   - Priority based on triage
   - Track "fix churn" as quality metric

---

## Phase 8: Completion & Archive

### Input
- All tasks complete and verified
- Project deliverables ready

### Process

1. **Final Verification**
   - All phase checkpoints pass
   - Integration verified
   - Definition of Done met

2. **Knowledge Consolidation**
   - ADRs complete and linked
   - Failure log comprehensive
   - Research findings captured

3. **Archive**
   - Move project docs to archive
   - Update hub notes
   - Create final context snapshot

4. **Retrospective Capture**
   - What worked well?
   - What didn't?
   - Process improvements for next time

---

## Quick Reference: Templates

| Situation | Template |
|-----------|----------|
| Define a new task | task-definition.md |
| Generate AI execution prompt | execution-prompt.md |
| Document architectural decision | adr.md |
| Capture research insight | research-finding.md |
| Hand off between sessions | context-snippet.md |
| Document failed approach | failure-log.md |
| Structure entire project | project-plan.md |
| Define research spike | spike-task.md |
| Verify task completion | verification-report.md |
| Full debugging agent prompt | debugging-agent.md |

---

## Quick Reference: Sizing

| Size | Time | When to Use |
|------|------|-------------|
| S | <2hr | Simple, well-understood tasks |
| M | 2-4hr | Standard implementation tasks |
| L | 4-8hr | Complex but still single-objective |
| SPIKE | Timeboxed | Research with unknown duration |

**If >8 hours**: Break it down further

---

## Quick Reference: Verification Tiers

| Tier | Confidence | What's Checked |
|------|------------|----------------|
| Automated | High | Build, tests, linting, security |
| AI-Assisted | Medium | Requirements trace, patterns, docs |
| Human Review | Low | Architecture, UX, business logic |

---

## Anti-Pattern Warnings

### During Decomposition
- ❌ Tasks with vague verbs (Handle, Ensure, Address)
- ❌ Tasks estimated >8 hours
- ❌ Missing "NOT INCLUDED" section
- ❌ Compound criteria (multiple things partially pass)

### During Execution
- ❌ Scope creep without documentation
- ❌ Skipping knowledge capture
- ❌ Not updating context snapshots
- ❌ Ignoring failed approaches

### During Verification
- ❌ "It looks right" instead of binary checks
- ❌ Skipping verification due to time pressure
- ❌ Not documenting deviations (even beneficial ones)
- ❌ Mixing verification and remediation

---

## Success Indicators

You're using this skill well when:

- [ ] Every task can be picked up cold without context rebuilding
- [ ] Decisions are documented with rationale
- [ ] Failed approaches are captured (negative knowledge)
- [ ] Verification happens before marking complete
- [ ] Context snapshots enable seamless handoffs
- [ ] Task sizing is consistently accurate (2-4 hours)
- [ ] No silent failures—issues are caught and documented
