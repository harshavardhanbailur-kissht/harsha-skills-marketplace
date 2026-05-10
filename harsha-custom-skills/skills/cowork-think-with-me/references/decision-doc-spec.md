# Decision Document Specification

## What the Decision Doc Is

The decision doc is the terminal artifact of a think-with-me session. Its primary reader is a future Claude session (or a human returning to this decision weeks later) who needs to understand not just what was decided, but how — so they can build on it, challenge it, or extend it without redoing the work.

A decision doc is NOT:
- A PRD (it may inform one, but it does not replace one)
- A meeting summary
- A bullet-point summary of the conversation
- A recommendation memo

A decision doc IS:
- A structured record of the full option space, the reasoning used to narrow it, and the institutional memory of what was tried and rejected

---

## The 11 Mandatory Fields

### Field 1: Problem Statement
**What it contains:** A single crisp statement of what decision is being made, for whom, and by when (if known).

**Good example:**
"Decide how to structure the loan repayment reminder flow for LAP borrowers who have missed one EMI, balancing recovery rate against relationship damage."

**Bad example:**
"We need to figure out the repayment reminder thing."

The bad version has no audience, no constraint, and no measurability.

---

### Field 2: Axes of Enumeration
**What it contains:** The dimensions used to generate the option space. These are the axes along which options were varied.

**Good example:**
```
- Channel: SMS / WhatsApp / In-app / IVR / Physical visit
- Timing: Same day / +1 day / +3 days / +7 days
- Tone: Informational / Urgent / Empathetic / Legal-warning
- Actor: Automated / Agent-initiated / Manager-escalation
- Content: Payment link only / Explanation of consequence / Restructuring offer
```

**Bad example:**
"We looked at different types of reminders."

Why axes matter: if you skipped an axis (e.g., never considered "who initiates"), that gap is visible. A future session can pick up a missed axis without re-doing the whole enumeration.

---

### Field 3: Full Option Space
**What it contains:** Every option generated, organized by axis. This is intentionally exhaustive — options are not filtered here.

Format:
```
Channel axis:
- SMS (standard)
- WhatsApp (if consent collected)
- In-app push notification
- IVR call
- Field visit (for high-value accounts)

Timing axis:
- Same day as missed EMI
- Next business day
- 3 days post-miss
- 7 days post-miss (final notice window)
```

Include options that were immediately dismissed — their dismissal reason goes in Field 7 (Rejected Options), not here.

---

### Field 4: Ranking Criteria
**What it contains:** The rubric used to evaluate options, with explicit weights if applicable.

**Good example:**
```
1. Recovery rate impact (weight: 40%) — does this drive actual payment?
2. Relationship preservation (weight: 30%) — does this damage the borrower relationship?
3. Implementation effort (weight: 20%) — how long to build and test?
4. Compliance risk (weight: 10%) — any regulatory exposure?
```

**Bad example:**
"We ranked based on what's best for users and feasibility."

Without explicit criteria, a future session cannot reproduce or challenge the ranking. They also cannot reweight the criteria if company priorities shift.

---

### Field 5: Ranked Options
**What it contains:** All options ordered 1 through N, with the mandatory ranked-option template for each.

Template per option:
```
### Rank [N]: [Option Name]
Best case: [specific positive outcome]
Worst case: [specific negative outcome]
Why this rank: [comparative statement vs. adjacent ranks]
Who would hate this: [stakeholder or user segment most disadvantaged]
```

Rules:
- All options must be ranked (no ties without explicit justification)
- At least one option must be explicitly labeled as worst
- Downsides must be specific, not hedged

---

### Field 6: Selected Options
**What it contains:** The top N options chosen, with full rationale.

The rationale must answer: "Given the criteria in Field 4, here is why these options score highest." It should be possible to re-derive the selection from Fields 4 and 5 alone — Field 6 is the synthesis, not a surprise.

---

### Field 7: Rejected Options
**What it contains:** Every option not selected, with specific reasons.

**Good example:**
"IVR call rejected: our IVR completion rate for collections is 12% (internal data, Q3 FY25). At that rate, the volume required to generate meaningful recovery would create a noise-complaint pattern that compliance flagged in a previous review."

**Bad example:**
"IVR call rejected: less suitable for this use case."

The "less suitable" rejection is worthless. It tells a future session nothing about whether to reconsider IVR if the completion rate improves.

---

### Field 8: Unexplored Adjacent Spaces
**What it contains:** Enumeration axes or option clusters that were identified but not explored in this session.

**Example:**
"Did not explore: restructuring offer as a trigger for reminder content (separate decision), or personalization of tone based on borrower credit history. These warrant a separate think-with-me session."

This field converts "we didn't have time" into a navigable backlog.

---

### Field 9: User Override Log
**What it contains:** Every instance where the user supplied their own reasoning to skip or override an exploration step, plus the cross-question asked.

Format:
```
Override #1:
User reasoning: "We're not considering WhatsApp — legal hasn't approved the consent flow."
Cross-question asked: "Is the legal block temporary (pending review) or permanent (policy decision)? 
  If temporary, WhatsApp may be worth revisiting in 60 days."
User response: "Permanent for now — moving on."
Status: Closed. WhatsApp noted in Field 8 (Unexplored Adjacent Spaces) for re-evaluation if policy changes.
```

---

### Field 10: Residual Uncertainty
**What it contains:** Questions that were raised but not answered, data that was missing, and assumptions that could not be validated in this session.

**Example:**
```
- Recovery rate impact of each channel is estimated, not measured. We don't have 
  controlled A/B data on reminder channel vs. repayment.
- WhatsApp consent rate among LAP borrowers is unknown. If high, WhatsApp may 
  outrank SMS on Field 4 criteria.
- Engineering estimated 2-sprint effort for IVR. This estimate was not validated 
  with the tech team.
```

Residual uncertainties are inputs to the next decision cycle, not failures of this one.

---

### Field 11: Expert Panel Synthesis
**What it contains:** Where experts agreed, where they disagreed, and the minority views that should not be ignored.

Format: see expert-panels.md for the full documentation standard. The key rule: disagreements are named by expert, not averaged away.

---

## Optional Fields

These are written only when explicitly relevant:
- **Competitive / Market Context** — if a competitor decision or market condition materially affected ranking
- **Data Gaps** — a specific list of data that would change the ranking if available (distinct from Residual Uncertainty, which is broader)
- **Implementation Sketch** — only if the user explicitly requests it; this doc is a decision record, not a spec

---

## What Makes a Decision Doc Useful vs. Useless

**Useful:** A future Claude session reading it can reconstruct what options existed, why the top option was chosen, and what would have to change for a different option to win.

**Useless:** A future Claude session reads it and has to ask "but why did you rule out X?" — meaning X was never written down, or was dismissed with a vague phrase.

The test: hand the doc to someone who wasn't in the session. If they say "I understand why you chose this and what you'd need to reconsider it," the doc passed. If they say "but why didn't you consider...?" it failed.

---

## How a Future Claude Session Should Interpret This Doc

1. Read Field 1 (Problem Statement) to ground the context
2. Read Field 4 (Ranking Criteria) to understand what mattered
3. Read Field 6 (Selected Options) and Field 7 (Rejected Options) together — this is the decision
4. Read Field 9 (User Override Log) to understand what constraints were set by the user, not by analysis
5. Read Field 10 (Residual Uncertainty) to identify what has changed since the session that might warrant reopening the decision
6. Do NOT re-derive the ranking from scratch unless criteria have changed — use this doc as the starting point and amend it, don't replace it
