# Rejected Options Log

<!-- HOW TO USE:
     - Log every option that was considered but not selected.
     - "Reason Rejected" must be specific — "less suitable" is not acceptable.
     - "Reconsidered If" must name a real condition, not a platitude.
     - User overrides and cross-question exchanges get their own sections below.
     - Cross-question log entries carry forward across sessions if the decision doc is resumed.
-->

## Problem: [Problem statement in one sentence]

---

## Rejected Options

| Rank | Option Name | Reason Rejected | Reconsidered If |
|------|-------------|-----------------|-----------------|
| [2] | [Option name] | [Specific reason — e.g., "requires 3 API changes estimated at 2-sprint effort, ruled out by Q2 deadline"] | [Condition — e.g., "deadline extends past Q3 or engineering capacity increases by 1 team"] |
| [3] | [Option name] | [Specific reason] | [Condition] |
| [4] | [Option name] | [Specific reason] | [Condition] |
| [N] | [Option name — WORST] | [Why this is the definitively weakest option, not just "least preferred"] | [Condition, if any, that would revive it] |

<!-- Every option not selected must appear here. If an option has no realistic revival condition, write "None — [reason why]." -->

---

## User Override Log

<!-- When the user supplied their own logic to skip or override an exploration step,
     log the exchange here verbatim. Claude asks one cross-question and then yields. -->

### Override 1
**Step overridden:** [Which exploration step was skipped — e.g., "Axis 3 enumeration"]
**User's reasoning:** "[User's exact reasoning, quoted or closely paraphrased]"
**Cross-question asked:** "[The one targeted question Claude posed — probing the weakest assumption]"
**User's response:** "[User's answer, or 'User said to move on — yielded.']"
**Logged to decision doc:** [Yes / No]

### Override 2
**Step overridden:** [Step]
**User's reasoning:** "[Reasoning]"
**Cross-question asked:** "[Question]"
**User's response:** "[Response]"
**Logged to decision doc:** [Yes / No]

<!-- If user overrides 3+ steps in a row, note the pattern once here:
     "Pattern noted: [X], [Y], [Z] were all skipped. Flagged in decision doc under Unexplored Adjacent Spaces." -->

---

## Cross-Question Log (Cross-Session)

<!-- If this decision doc spans multiple sessions, log cross-questions that were raised
     but not resolved, so a resuming session can pick them up. -->

| Session | Question Raised | Status |
|---------|----------------|--------|
| [Session date / context] | [Cross-question that was asked] | [Resolved / Open / User yielded] |
| [Session date / context] | [Cross-question that was asked] | [Resolved / Open / User yielded] |
