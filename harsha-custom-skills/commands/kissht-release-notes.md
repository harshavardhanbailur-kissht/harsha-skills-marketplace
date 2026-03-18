---
description: Generate stakeholder-specific release notes from Jira tickets for Kissht/Ring fintech products
argument-hint: "<Jira sprint or ticket IDs>"
---

# /kissht-release-notes — Kissht Release Notes Generator

Generate role-based release documentation from Jira ticket data for LAP LOS, UP/Ring, Saral LSQ products. Creates tailored notes for PMs, QA, Developers, Training, BAs, Operations, and Leadership.

## Invocation

```
/kissht-release-notes Sprint 45 LAP LOS
/kissht-release-notes KISSHT-1234, KISSHT-1235, KISSHT-1240
/kissht-release-notes [paste Jira ticket data or upload CSV]
```

## Workflow

Load the `kissht-release-notes` skill and follow its orchestration pipeline to generate stakeholder-specific documentation.
