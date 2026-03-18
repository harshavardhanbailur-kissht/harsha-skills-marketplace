---
description: Prevent breaking existing apps when adding features — 4-phase defensive development workflow
argument-hint: "<feature to add to existing app>"
---

# /workflow-guardian — Defensive Feature Development

Enforces RECONNAISSANCE → IMPACT ANALYSIS → IMPLEMENTATION → VERIFICATION when modifying working applications. Prevents breaking existing functionality.

## Invocation

```
/workflow-guardian Add dark mode to the dashboard
/workflow-guardian Build notification system on top of existing app
/workflow-guardian [describe the feature + point to existing codebase]
```

## Workflow

Load the `workflow-guardian` skill and follow the mandatory 4-phase pipeline. Core principle: "Match, Don't Fix."
