# Project Orchestrator Quick Reference

One-page cheat sheet for rapid reference during project work.

---

## Task Definition Formula

```
TASK: [Action Verb] + [Specific Object] + [Scope Boundary]
CONTEXT: [Why this exists]
DONE WHEN: [Binary criteria]
NOT INCLUDED: [Exclusions]
ESTIMATED: S (<2hr) | M (2-4hr) | L (4-8hr)
```

---

## Task Sizing

| Too Big (break down) | Just Right | Too Small (combine) |
|---------------------|------------|---------------------|
| >8 hours | 2-4 hours | <15 minutes |
| Multiple ANDs | One objective | Same context as adjacent |
| Can't estimate | Clear scope | Tracking > execution |
| >12 criteria | 3-5 criteria | Micro-task |

---

## Acceptance Criteria Pattern

```gherkin
Given [precondition]
When [action]
Then [outcome]
  And [additional outcome]
```

**Good**: Specific, measurable, binary (PASS/FAIL)
**Bad**: "Works correctly," "Good performance," "User-friendly"

---

## Execution Prompt Structure

```
# Task Title
## Intent: [WHY in one sentence]
## Context: Tech stack + versions, environment, current state
## Code Reference: [Actual snippets]
## Task: [Single objective]
## Constraints: MUST / MUST NOT / SHOULD
## Success Criteria: [Binary checks]
## Out of Scope: [Exclusions]
```

---

## ADR Format

```
# ADR-N: Title
## Status: Proposed | Accepted | Deprecated | Superseded
## Context: [Forces at play]
## Decision: We will [active voice]...
## Consequences: [Positive, negative, neutral]
```

---

## Context Snippet (Handoff)

```
# Context: [Task]
## Goal: [One sentence]
## Current State: Complete / In Progress
## Key Decisions: [With rationale]
## Next Steps: [Immediate actions]
## Blockers: [If any]
## References: [Links]
```

---

## Verification Tiers

| Tier | Confidence | Checks |
|------|------------|--------|
| Automated | High | Build, tests, lint, security |
| AI-Assisted | Medium | Requirements, patterns, docs |
| Human Review | Low | Architecture, UX, business logic |

---

## Error Types

| Type | Description | Detection |
|------|-------------|-----------|
| Missing | Not implemented | Forward trace |
| Incomplete | Partial | Thorough testing |
| Wrong | Incorrect | Tests |
| Deviated | Different from spec | Plan comparison |
| Extraneous | Unrequested | Backward trace |
| Context Loss | Right per instructions, wrong for goal | Original context |

---

## Severity Levels

| Level | Definition | Response |
|-------|------------|----------|
| S1 Critical | System unusable | Same day |
| S2 High | Major feature broken | This sprint |
| S3 Medium | Impaired, workaround exists | Next sprint |
| S4 Low | Minor/cosmetic | Backlog |

---

## Templates Quick Reference

| Situation | Template |
|-----------|----------|
| New task | `task-definition.md` |
| AI prompt | `execution-prompt.md` |
| Decision | `adr.md` |
| Research insight | `research-finding.md` |
| Session handoff | `context-snippet.md` |
| Failed approach | `failure-log.md` |
| Research question | `spike-task.md` |
| Task verification | `verification-report.md` |

---

## Knowledge Capture Triggers

| When | Do |
|------|-----|
| Architectural decision | ADR same day |
| Failed approach | Failure log immediately |
| Research complete | Research finding |
| Constraint discovered | Add to docs |
| Session ending | Context snippet |

---

## Workflow Summary

```
1. INTAKE    → Shape concept (appetite, boundaries, success)
2. DECOMPOSE → 2-4hr tasks with acceptance criteria
3. SETUP     → Initialize knowledge capture
4. MAP       → Generate execution prompts
5. EXECUTE   → One task at a time, capture knowledge
6. VERIFY    → Binary check against criteria
7. REMEDIATE → Fix or replan as needed
8. COMPLETE  → Archive and retrospect
```

---

## Red Flags

- ❌ Task with no "NOT INCLUDED" section
- ❌ Criteria that aren't binary
- ❌ Prompt assuming prior context
- ❌ Decision without documented rationale
- ❌ Failed approach not documented
- ❌ Verification skipped for speed
- ❌ Deviation not flagged (even if beneficial)

---

## Success Checklist

- [ ] Tasks can be picked up cold
- [ ] Decisions documented with why
- [ ] Failed approaches captured
- [ ] Verification before completion
- [ ] Context snapshots current
- [ ] No silent failures
