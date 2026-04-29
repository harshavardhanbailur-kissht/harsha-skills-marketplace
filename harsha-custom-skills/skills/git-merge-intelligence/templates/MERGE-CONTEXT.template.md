# Merge Resolution Context

> This file is the persistent shared memory for the git-merge-intelligence skill.
> Every phase reads this file first to recover state. Every phase writes its results here.
> This file survives context compaction — it IS the memory.

## Meta
- **Created**: {ISO-8601 timestamp}
- **Last Updated**: {ISO-8601 timestamp}
- **Mode**: {SPRINT | STANDARD | HEAVY}
- **Conflict Count**: {number}
- **Repository**: {repo name or path}

## Phase Status
- [ ] Phase 0: Safety Bootstrap
- [ ] Phase 1: Context Building
- [ ] Phase 2: Triage & Classification
- [ ] Phase 3: Resolution Planning
- [ ] Phase 4: Execution
- [ ] Phase 5: Validation

## PR Metadata
- **Title**: {PR title or "N/A — no Bitbucket credentials"}
- **Description**: {PR description summary}
- **Source Branch**: {branch name}
- **Destination Branch**: {branch name}
- **PR URL**: {URL or "N/A"}
- **Bitbucket Status**: {available | unavailable — git-log-only mode}

## Branch Intent Analysis
### Our Branch ({branch name})
- **Intent Category**: {FEATURE | REFACTOR | BUGFIX | HOTFIX | DEPENDENCY_UPDATE | MIGRATION | CHORE}
- **Summary**: {1-2 sentence description of what this branch was trying to do}
- **Key Commits**:
  - {commit hash}: {message}
  - ...

### Their Branch ({branch name})
- **Intent Category**: {same categories}
- **Summary**: {1-2 sentence description}
- **Key Commits**:
  - {commit hash}: {message}
  - ...

## Merge Base
- **Commit**: {commit hash}
- **Date**: {ISO-8601 timestamp}
- **Divergence Point**: {brief description of what base represents}

## PR Signals
- **Bitbucket Status**: {available | unavailable — git-log-only mode}
- **Reviewer Flags**: {list of flags or "none"}
- **Intent-Enriching Signals**: {BREAKING_CHANGE | EXPERIMENTAL | REVIEWER_RESTRUCTURE_REQUEST | SECURITY_CONCERN_RAISED | REVIEWER_APPROVED | etc.}

## Conflict Inventory
- **Total Files**: {number}
- **By Type**: ADDITIVE: {n}, MODIFY_SAME: {n}, DELETE_MODIFY: {n}, RENAME_MODIFY: {n}, SEMANTIC: {n}, CONFIG: {n}, LOCKFILE: {n}, AUTH_SECURITY: {n}
- **By Complexity**: TRIVIAL: {n}, MODERATE: {n}, COMPLEX: {n}, CRITICAL: {n}
- **By Language**: TypeScript: {n}, Go: {n}, Python: {n}, Config: {n}, CSS: {n}, Markdown: {n}, Other: {n}

## Batch Execution Plan
### Batch 0: Foundation (configs)
| File | Strategy | Status | Confidence |
|------|----------|--------|------------|
| {path} | {KEEP_OURS/KEEP_THEIRS/KEEP_BOTH/MANUAL_MERGE/REGENERATE/DEEP_THINK} | {pending/resolved/needs-human/blocked} | {🟢/🟡/🔴} |

### Batch 1: Types & Interfaces
| File | Strategy | Status | Confidence |
|------|----------|--------|------------|
...

### Batch 2: Shared / Middleware / Auth
...

### Batch 3: Implementations
...

### Batch 4: Tests
...

### Batch 5: Docs / CI
...

## Batch Checkpoints
### Batch 0 Checkpoint [pending]
- Resolved: 0 / 0 files
- Status: pending

### Batch 1 Checkpoint [pending]
- Resolved: 0 / 0 files
- Status: pending

### Batch 2 Checkpoint [pending]
- Resolved: 0 / 0 files
- Status: pending

### Batch 3 Checkpoint [pending]
- Resolved: 0 / 0 files
- Status: pending

### Batch 4 Checkpoint [pending]
- Resolved: 0 / 0 files
- Status: pending

### Batch 5 Checkpoint [pending]
- Resolved: 0 / 0 files
- Status: pending

## Validation Results
| Layer | Status | Details |
|-------|--------|---------|
| L1: Syntax | {⬜ pending / ✅ PASS / ❌ FAIL} | {details} |
| L2: Types | {status} | {details} |
| L3: Lint | {status} | {details} |
| L4: Tests | {status} | {details} |
| L5: Markers | {status} | {details} |
| L6: Semantic | {status} | {details} |

## Decision Summary
- **Total Resolved**: {n} / {total}
- **Auto-Resolved (GREEN)**: {n}
- **Flagged for Review (YELLOW)**: {n}
- **Needs Human (RED)**: {n}
- **Key Decisions**:
  - {decision 1 summary}
  - {decision 2 summary}
  - ...

## Files Needing Human Review
| File | Reason | Question for Developer |
|------|--------|----------------------|
| {path} | {reason} | {specific question} |
