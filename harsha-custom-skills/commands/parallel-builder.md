---
description: Decompose features into parallel subtasks and launch simultaneous Claude subagents
argument-hint: "<feature, epic, or PRD to parallelize>"
---

# /parallel-builder — Parallel Skill Builder

Decompose complex features into independent subtasks, engineer complete prompts for each, and launch them simultaneously via the Task tool.

## Invocation

```
/parallel-builder Build a full dashboard with auth, analytics, and settings
/parallel-builder [upload a PRD or feature epic]
/parallel-builder Parallelize this: user registration + product catalog + checkout
```

## Workflow

Load the `parallel-builder` skill to decompose, generate interface contracts, and fan out to subagents.
