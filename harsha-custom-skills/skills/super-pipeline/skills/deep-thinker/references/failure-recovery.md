# Failure Analysis Reference

Patterns for identifying and documenting potential failures in analysis.

## Table of Contents
- [Failure Taxonomy](#failure-taxonomy)
- [Analysis Patterns](#analysis-patterns)
- [Documentation Templates](#documentation-templates)

---

## Failure Taxonomy

### Common Failure Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Input Failures** | Invalid or unexpected input | Empty string, wrong format |
| **State Failures** | System in unexpected state | Already logged in, expired session |
| **Timing Failures** | Race conditions, timeouts | Double-click, slow network |
| **External Failures** | Third-party service issues | API down, rate limited |
| **Resource Failures** | System resources exhausted | Memory, storage, connections |
| **Logic Failures** | Business rule violations | Invalid state transition |

### Failure Severity Levels

| Severity | Impact | Example |
|----------|--------|---------|
| **Critical** | Data loss, security breach | Unauthorized access |
| **High** | Feature completely broken | Cannot complete action |
| **Medium** | Degraded experience | Slow, confusing error |
| **Low** | Minor inconvenience | Visual glitch |

---

## Analysis Patterns

### Failure Mode Analysis (FMEA)

For every feature, document:

```markdown
## Failure Mode Analysis: [Feature]

| What Could Fail | How It Fails | Impact | Likelihood | Prevention | Recovery |
|-----------------|--------------|--------|------------|------------|----------|
| [Failure 1] | [Mechanism] | [Severity] | [Low/Med/High] | [Strategy] | [Action] |
| [Failure 2] | ... | ... | ... | ... | ... |
```

### Pre-Mortem Analysis

Imagine the feature has failed catastrophically:

```markdown
## Pre-Mortem: [Feature]

### The Disaster Scenario
[Describe what went wrong]

### What Caused It
1. [Root cause 1]
2. [Root cause 2]

### Warning Signs We Missed
1. [Sign 1]
2. [Sign 2]

### How We Could Have Prevented It
1. [Prevention 1]
2. [Prevention 2]
```

### Edge Case Exploration

```markdown
## Edge Cases: [Feature]

### Input Variations
- Empty: [What happens?]
- Too long: [What happens?]
- Special characters: [What happens?]
- Unicode: [What happens?]

### Timing Variations
- Very fast (double-click): [What happens?]
- Very slow (timeout): [What happens?]
- Interrupted (page close): [What happens?]

### State Variations
- Already done: [What happens?]
- Partially done: [What happens?]
- Done elsewhere: [What happens?]

### Concurrent Variations
- Same user, two tabs: [What happens?]
- Two users, same resource: [What happens?]
```

---

## Documentation Templates

### EDGE_CASES.md Structure

```markdown
# Edge Cases & Scenarios

## Happy Paths
| Scenario | Input | Expected Output | Notes |
|----------|-------|-----------------|-------|
| Normal case 1 | Valid input | Success | Standard flow |

## Error States
| Error | Cause | User Experience | Recovery |
|-------|-------|-----------------|----------|
| Network failure | No connection | Error message | Retry button |

## Race Conditions
| Condition | Scenario | Risk | Prevention |
|-----------|----------|------|------------|
| Double submit | User clicks twice | Duplicate action | Disable button |

## Boundary Conditions
| Boundary | At Value | Below | Above |
|----------|----------|-------|-------|
| Max length | Exactly 255 | 254 works | 256 rejected |

## Security Considerations
| Risk | Attack Vector | Prevention |
|------|--------------|------------|
| XSS | User input in HTML | Sanitize/escape |

## Accessibility Scenarios
| Scenario | User Need | Support |
|----------|-----------|---------|
| Screen reader | Visual impairment | ARIA labels |
```

### Thinking Questions

For each potential failure, ask:

1. **What triggers this failure?**
2. **How does the user experience it?**
3. **What data is at risk?**
4. **How do we prevent it?**
5. **How do we recover from it?**
6. **How do we detect it happened?**

---

## Quality Checklist

Before considering EDGE_CASES.md complete:

```
[ ] All happy paths documented
[ ] All error states documented
[ ] Race conditions considered
[ ] Boundary conditions tested
[ ] Security risks identified
[ ] Accessibility scenarios covered
[ ] Prevention strategies defined
[ ] Recovery actions specified
```
