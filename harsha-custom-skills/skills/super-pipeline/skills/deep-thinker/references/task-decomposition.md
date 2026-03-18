# Thinking Decomposition Reference

Comprehensive patterns for breaking complex problems into analyzable components.

## Table of Contents
- [MECE Framework](#mece-framework)
- [Hierarchical Thinking Networks](#hierarchical-thinking-networks)
- [Dependency Mapping](#dependency-mapping)
- [Decomposition Prompts](#decomposition-prompts)

---

## MECE Framework

MECE (Mutually Exclusive, Collectively Exhaustive) ensures complete coverage without overlap.

### Principles

1. **Mutually Exclusive**: Each analysis area has unique scope
   - No two sections should cover the same ground
   - Clear ownership of each topic
   - No "shared" or "overlapping" responsibilities

2. **Collectively Exhaustive**: All areas together = complete analysis
   - Sum of analysis scopes equals problem scope
   - No gaps between areas
   - Nothing falls through the cracks

### MECE Validation Checklist

```
[ ] Can I analyze area A without touching area B's scope?
[ ] Do all areas together fully cover the problem?
[ ] Is there any aspect not covered by any area?
[ ] Are there any topics claimed by multiple areas?
```

### Common MECE Violations

| Violation | Example | Fix |
|-----------|---------|-----|
| Overlap | "UI analysis" + "Component analysis" | Merge or clarify scope |
| Gap | Missing "error handling" analysis | Add missing area |
| Ambiguity | "Handle edge cases" | Specify which edge cases |

---

## Hierarchical Thinking Networks

HTN provides recursive decomposition from abstract to detailed analysis.

### Analysis Types

**Compound Analysis**: Requires further decomposition
```yaml
- id: "ANALYSIS-001"
  name: "Authentication system analysis"
  type: compound
  sub_analyses:
    - "ANALYSIS-001-A"  # Login flow
    - "ANALYSIS-001-B"  # Registration flow
    - "ANALYSIS-001-C"  # Password reset
```

**Primitive Analysis**: Directly documentable
```yaml
- id: "ANALYSIS-001-A"
  name: "Login form analysis"
  type: primitive
  acceptance_criteria:
    - "Current implementation documented"
    - "Edge cases identified"
    - "Improvement opportunities listed"
```

### Decomposition Depth

Stop decomposing when:
- Analysis area is focused and specific
- Acceptance criteria are unambiguous
- Single topic can be fully explored
- Output is clearly verifiable

### HTN Algorithm

```python
def decompose(analysis):
    if is_primitive(analysis):
        return [analysis]

    sub_analyses = identify_sub_analyses(analysis)
    validate_mece(sub_analyses)

    result = []
    for sub in sub_analyses:
        result.extend(decompose(sub))

    return result

def is_primitive(analysis):
    return (
        len(analysis.acceptance_criteria) >= 2
        and analysis.scope_is_focused
        and analysis.output_is_verifiable
    )
```

---

## Dependency Mapping

### Dependency Types

**Hard Dependency**: Must analyze before proceeding
```yaml
dependencies:
  hard:
    - "ANALYSIS-001"  # Cannot proceed without this understanding
```

**Soft Dependency**: Helpful but not required
```yaml
dependencies:
  soft:
    - "ANALYSIS-002"  # Nice to understand first
```

**Data Dependency**: Needs output from another analysis
```yaml
dependencies:
  data:
    - from: "ANALYSIS-001.output.schema"
      to: "inputs.understanding"
```

### DAG Validation

Analyses must form a Directed Acyclic Graph (no cycles).

```python
def validate_dag(analyses):
    """Ensure no circular dependencies using Kahn's algorithm"""
    from collections import defaultdict

    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for analysis in analyses:
        analysis_id = analysis["id"]
        for dep in analysis.get("dependencies", {}).get("hard", []):
            graph[dep].append(analysis_id)
            in_degree[analysis_id] += 1

    # Start with analyses that have no dependencies
    queue = [a["id"] for a in analyses if in_degree[a["id"]] == 0]
    sorted_order = []

    while queue:
        current = queue.pop(0)
        sorted_order.append(current)

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_order) != len(analyses):
        remaining = set(a["id"] for a in analyses) - set(sorted_order)
        return False, f"Cycle detected: {remaining}"

    return True, sorted_order
```

### Analysis Order

Analyses at the same DAG level can be explored together:

```
Level 0: [ANALYSIS-A, ANALYSIS-B]        # No dependencies
Level 1: [ANALYSIS-C]                    # Depends on A
Level 2: [ANALYSIS-D, ANALYSIS-E]        # D depends on C, E depends on B
Level 3: [ANALYSIS-F]                    # Depends on D and E
```

---

## Decomposition Prompts

### Initial Decomposition Prompt

```markdown
## Thinking Decomposition Request

### Problem to Analyze
[INSERT FULL PROBLEM DESCRIPTION]

### Decomposition Requirements
1. Apply MECE: No overlaps, no gaps
2. Clear boundaries: Unambiguous scope for each area
3. Explicit dependencies: What must be understood first?

### For Each Analysis Area, Specify:
- id: Unique identifier (ANALYSIS-001 format)
- name: Clear descriptive name
- description: What needs to be analyzed
- type: "primitive" or "compound"
- dependencies:
    hard: [analysis IDs that must complete first]
    soft: [analysis IDs that are nice to have first]
- acceptance_criteria: [list of verifiable outputs]
- output_file: [which .deep-think/ file this belongs in]

### Validation
After generating:
[ ] No circular dependencies
[ ] All areas together = complete coverage
[ ] No overlapping scopes
[ ] Each area has 2+ acceptance criteria
```

### Refinement Prompt

When an analysis area is too broad:

```markdown
## Decompose Further: [ANALYSIS-ID]

This analysis area is too broad. Break it into sub-analyses.

### Current Analysis
[ANALYSIS DETAILS]

### Decomposition Constraints
- Maintain clear boundaries
- Preserve all acceptance criteria
- Update dependency graph

### Output
Replace [ANALYSIS-ID] with sub-analyses [ANALYSIS-ID-A], [ANALYSIS-ID-B], etc.
Update any analyses that depended on [ANALYSIS-ID].
```

---

## Example Decomposition

### Input: "Add mobile number login alongside email"

### Output:

```yaml
analyses:
  - id: "ANALYSIS-001"
    name: "Current email OTP implementation"
    type: primitive
    dependencies:
      hard: []
    acceptance_criteria:
      - "UI component structure documented"
      - "API contracts captured"
      - "Validation rules listed"
      - "State management pattern identified"
    output_file: "CURRENT_STATE.md"

  - id: "ANALYSIS-002"
    name: "Phone input requirements"
    type: primitive
    dependencies:
      hard: ["ANALYSIS-001"]
    acceptance_criteria:
      - "Country code handling approach"
      - "Phone format validation"
      - "International support scope"
    output_file: "ARCHITECTURE.md"

  - id: "ANALYSIS-003"
    name: "UI layout options"
    type: primitive
    dependencies:
      hard: ["ANALYSIS-001"]
    acceptance_criteria:
      - "Multiple approaches documented"
      - "Pros/cons for each"
      - "Recommendation with rationale"
    output_file: "ARCHITECTURE.md"

  - id: "ANALYSIS-004"
    name: "API changes needed"
    type: primitive
    dependencies:
      hard: ["ANALYSIS-001"]
    acceptance_criteria:
      - "Endpoint modifications listed"
      - "Backwards compatibility addressed"
      - "SMS provider integration"
    output_file: "IMPLEMENTATION.md"

  - id: "ANALYSIS-005"
    name: "Edge cases and error states"
    type: primitive
    dependencies:
      hard: ["ANALYSIS-002", "ANALYSIS-003", "ANALYSIS-004"]
    acceptance_criteria:
      - "All failure modes documented"
      - "Race conditions identified"
      - "Recovery strategies defined"
    output_file: "EDGE_CASES.md"

  - id: "ANALYSIS-006"
    name: "Implementation steps"
    type: primitive
    dependencies:
      hard: ["ANALYSIS-005"]
    acceptance_criteria:
      - "Step-by-step with file:line refs"
      - "Dependencies between steps clear"
      - "Verification for each step"
    output_file: "IMPLEMENTATION.md"
```

### Analysis Order (from DAG)
```
Level 0: ANALYSIS-001 (current state)
Level 1: ANALYSIS-002, ANALYSIS-003, ANALYSIS-004 (parallel analysis)
Level 2: ANALYSIS-005 (edge cases)
Level 3: ANALYSIS-006 (implementation details)
```
