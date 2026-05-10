# Decision Document

<!-- This is the terminal artifact. A future Claude session reading this should fully understand
     what was decided, why, and what was left unexplored. Fill every mandatory field.
     Optional fields: include only if relevant. -->

---

## 1. Problem Statement
<!-- What decision is being made? One crisp paragraph. No background padding. -->
[State the decision to be made and why it matters now.]

---

## 2. Axes of Enumeration
<!-- What dimensions were used to generate options? List each axis and its values. -->
- **[Axis 1 name]:** [value A] | [value B] | [value C]
- **[Axis 2 name]:** [value A] | [value B]
- **[Axis 3 name]:** [value A] | [value B] | [value C]

---

## 3. Full Option Space
<!-- Every option generated, grouped by axis. Do not pre-filter here. -->
### From [Axis 1]:
- [Option 1]
- [Option 2]

### From [Axis 2]:
- [Option 3]
- [Option 4]

### Cross-axis combinations:
- [Option 5 — combination of Axis 1 value A + Axis 2 value B]

---

## 4. Ranking Criteria
<!-- The rubric used to evaluate. Weights must sum to 100%. -->
| Criterion | Weight | Definition |
|-----------|--------|------------|
| [Criterion 1] | [X%] | [What a high score on this means] |
| [Criterion 2] | [X%] | [What a high score on this means] |
| [Criterion 3] | [X%] | [What a high score on this means] |

---

## 5. Ranked Options
<!-- Best to worst. Every option gets a downside. No ties without explicit justification. -->

### Rank 1: [Option Name]
**Best case:** [Specific positive outcome]
**Worst case:** [Specific failure mode]
**Why this rank:** [Comparative statement vs. Rank 2]
**Who would hate this:** [Stakeholder or user segment]

### Rank 2: [Option Name]
**Best case:** [Specific positive outcome]
**Worst case:** [Specific failure mode]
**Why this rank:** [Comparative statement vs. Ranks 1 and 3]
**Who would hate this:** [Stakeholder or user segment]

### Rank N (Worst): [Option Name]
**Best case:** [Specific positive outcome]
**Worst case:** [Specific failure mode]
**Why this rank:** [Why this is definitively the weakest option]
**Who would hate this:** [Stakeholder or user segment]

---

## 6. Selected Options
<!-- Top N chosen for implementation. Full rationale required. -->
**Selected:** [Option Name(s)]

**Rationale:** [Why this option wins given the criteria weights and constraints]

**Conditions under which this selection changes:** [What would have to be true for Rank 2 to win instead]

---

## 7. Rejected Options
<!-- Specific rejection reasons. "Less suitable" is not a reason. -->
| Option | Reason Rejected | Reconsidered If |
|--------|----------------|-----------------|
| [Option A] | [Specific reason — e.g., "requires 3 API changes, 2-sprint effort, ruled out by timeline constraint"] | [Condition that would revive it] |
| [Option B] | [Specific reason] | [Condition] |

---

## 8. Unexplored Adjacent Spaces
<!-- What we didn't explore. Flagged for future sessions. -->
- [Adjacent space 1 — why not explored this session]
- [Adjacent space 2 — why not explored this session]

---

## 9. User Override Log
<!-- When the user supplied their own logic to skip/override a step. Written verbatim. -->
| Override # | Step Overridden | User's Reasoning | Cross-Question Asked | User's Response |
|------------|-----------------|------------------|----------------------|-----------------|
| 1 | [Which exploration step was skipped] | [User's exact reasoning] | [The one targeted question Claude asked] | [User's answer or "yielded"] |

---

## 10. Residual Uncertainty
<!-- What we still don't know. Be specific about what data would resolve each uncertainty. -->
- **[Uncertainty 1]:** [What we don't know] — resolved by [specific data or action]
- **[Uncertainty 2]:** [What we don't know] — resolved by [specific data or action]

---

## 11. Expert Panel Synthesis
<!-- Which experts were on the panel, where they agreed, where they disagreed. -->
**Panel:** [Expert 1], [Expert 2], [Expert 3], [Expert 4]

**Agreement:** [What all experts converged on]

**Disagreement:** [Where experts split — and whose view prevailed, and why]

---

## Optional: Competitive / Market Context
<!-- Include only if directly relevant to the decision. -->
[Market or competitive context that shaped the option space or ranking]

## Optional: Data Gaps
<!-- What data, if available, would have changed the ranking. -->
[Data gaps here]
