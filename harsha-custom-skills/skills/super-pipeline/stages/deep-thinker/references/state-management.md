# Analysis Structure Reference

Patterns for organizing comprehensive analysis output in `.deep-think/` files.

## Table of Contents
- [Output Structure](#output-structure)
- [File Relationships](#file-relationships)
- [Content Guidelines](#content-guidelines)
- [Cross-Reference Patterns](#cross-reference-patterns)

---

## Output Structure

### The `.deep-think/` Directory

All analysis output goes to a single directory:

```
.deep-think/
├── OVERVIEW.md              # Start here - goals, scope, success criteria
├── CURRENT_STATE.md         # Existing code analysis
├── ARCHITECTURE.md          # Design decisions with rationale
├── IMPLEMENTATION.md        # Step-by-step micro-details
├── EDGE_CASES.md            # All scenarios documented
├── OPTIMIZATIONS.md         # Quality improvements
├── CREATIVE_IDEAS.md        # Exceeding expectations
└── EXECUTION_CHECKLIST.md   # For executor session
```

### File Purposes

| File | Primary Purpose | Key Contents |
|------|-----------------|--------------|
| OVERVIEW.md | What and why | Goals, scope, success criteria, risks |
| CURRENT_STATE.md | What exists | Code locations, patterns, contracts |
| ARCHITECTURE.md | How to approach | Options, decisions, rationale |
| IMPLEMENTATION.md | Exact steps | File:line refs, micro-details |
| EDGE_CASES.md | What could go wrong | Scenarios, failures, recovery |
| OPTIMIZATIONS.md | How to improve | Performance, quality ideas |
| CREATIVE_IDEAS.md | How to exceed | Delight factors, future-proofing |
| EXECUTION_CHECKLIST.md | What to do | Ordered steps for executor |

---

## File Relationships

### Information Flow

```
OVERVIEW.md (goals)
     │
     ├──▶ CURRENT_STATE.md (what exists)
     │         │
     │         ▼
     ├──▶ ARCHITECTURE.md (how to approach)
     │         │
     │         ├──▶ IMPLEMENTATION.md (exact steps)
     │         │
     │         └──▶ EDGE_CASES.md (what could fail)
     │
     ├──▶ OPTIMIZATIONS.md (improvements)
     │
     └──▶ CREATIVE_IDEAS.md (exceeding expectations)
              │
              ▼
     EXECUTION_CHECKLIST.md (synthesis of all)
```

### Cross-References

When one file references another:

```markdown
## Implementation Approach

See [ARCHITECTURE.md](ARCHITECTURE.md#selected-approach) for why this
approach was selected over alternatives.

For edge cases related to this step, see
[EDGE_CASES.md](EDGE_CASES.md#step-3-api-changes).
```

---

## Content Guidelines

### OVERVIEW.md

```markdown
# Overview: [Feature Name]

## Goal
[What are we building and why?]

## Success Criteria
- [ ] Criterion 1 (verifiable)
- [ ] Criterion 2 (verifiable)

## Scope
### In Scope
- Item 1
### Out of Scope
- Item 1

## Risks
| Risk | Likelihood | Impact | Mitigation |
```

### CURRENT_STATE.md

```markdown
# Current State Analysis

## Code Locations
- Primary: `path/to/file.ts:line` - Description
- Related: `path/to/other.ts` - Description

## How It Works
[Detailed walkthrough]

## Patterns to Follow
[What existing patterns should new code match?]

## Technical Debt
[Issues discovered]
```

### ARCHITECTURE.md

```markdown
# Architecture Decisions

## Selected Approach
[High-level description]

### Why This Approach
- Reason 1
- Reason 2

## Alternatives Considered

### Option A: [Name]
**Pros:** ...
**Cons:** ...
**Why not:** ...

### Option B: [Name]
...
```

### IMPLEMENTATION.md

```markdown
# Implementation Details

## Step 1: [Action]
**Location:** `path/to/file.ts:line`

**What to do:**
[Detailed explanation]

**Micro-details:**
- Detail 1
- Detail 2

**Watch out for:**
- Gotcha 1

---

## Step 2: [Action]
...
```

### EDGE_CASES.md

```markdown
# Edge Cases & Scenarios

## Happy Paths
| Scenario | Input | Output |

## Error States
| Error | Cause | Handling |

## Race Conditions
| Condition | Risk | Prevention |

## Boundary Conditions
- At 0:
- At max:
- At exactly limit:
```

---

## Quality Criteria

Before considering any file complete:

```
[ ] All sections filled out
[ ] No placeholder text remaining
[ ] File:line references are accurate
[ ] Cross-references work
[ ] Executor could work from this alone
```
