# Problem Statement Template

Use this template when creating `PROBLEM.md` in Phase 1.

```markdown
## Problem Statement
[One-sentence decision statement from the user, reframed if necessary]

## Decision Type
[Feature / Pricing / Migration / Architecture / Partnership / Operational]

## Current State
[How things work today. What exists. What the baseline is.]

## Known Constraints
[List all known constraints: budget, timeline, regulatory, technical, team capacity, policy]

## Stakeholders Affected

| Stakeholder | How Affected | Priority |
|-------------|-------------|----------|
| [e.g., Active borrower with outstanding loan] | [e.g., Must switch mid-EMI cycle] | [High/Medium/Low] |
| [e.g., Internal CS/ops teams] | [e.g., New support playbooks needed] | [High/Medium/Low] |
| [e.g., Payment gateway integrations] | [e.g., API endpoint changes] | [High/Medium/Low] |

## Regulatory Context (if applicable)
[Relevant regulations, compliance requirements, audit implications]

## Success Criteria
[How will we know the decision was good? What does success look like in 30/90/180 days?]

## What Is NOT Being Decided
[Explicitly name what is out of scope to prevent scope creep during exploration]
```

## Guidance

- For **execution decisions** (migration, sunset, consolidation): the "why" is settled. Focus the problem statement on the "how" — list the sub-decisions that need to be made.
- For **binary framings** ("should we do A or B?"): reframe to the full decision space before writing PROBLEM.md. The problem is never "A or B" — it's the underlying need that A and B both attempt to address.
- The "What Is NOT Being Decided" field prevents the session from expanding into adjacent decisions. Fill it early.
