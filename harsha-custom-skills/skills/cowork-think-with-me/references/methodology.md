# Methodology: Socratic Questioning for Product and Strategy Decisions

## What This Is Not

This is not a debate technique. The goal is not to win an argument or to prove the user wrong. The goal is to surface assumptions the user hasn't articulated yet, so those assumptions can be evaluated and written into the decision doc before they become invisible load-bearing walls.

---

## The Four Question Types

### 1. Probing Assumptions
Use when: the user states something as fact that is actually a belief.

Pattern: "That assumes [X] — what's the basis for that?"

Examples:
- "You've said users drop off because they don't understand the flow. What evidence do we have that it's comprehension vs. friction?"
- "This assumes approval will take 2 days. Is that based on current SLAs or historical actuals?"
- "You're treating the two user segments as equivalent here — are they actually similar in this context?"

Do not ask: "Is that really true?" — too vague, produces defensiveness not information.

### 2. Probing Evidence
Use when: a ranking or preference is stated without a source.

Pattern: "What's driving that ranking? Is it data, intuition, or stakeholder input?"

Examples:
- "You've ranked cost as the top criterion — is that a company directive or your own read of the situation?"
- "You said retention is more important than activation. Is that based on current metrics or a hypothesis?"
- "Where did the 10% number come from? Is that a target, a benchmark, or a back-of-envelope estimate?"

The purpose is not to discredit the evidence — it's to document what kind of evidence it is. A hunch is valid input; it just needs to be labeled as one.

### 3. Questioning Viewpoints
Use when: only one perspective has been represented in the framing.

Pattern: "Who would disagree with that framing, and what would their argument be?"

Examples:
- "This is framed from the lender's perspective. How does the borrower experience the same decision?"
- "Engineering would probably push back on this timeline — what's their strongest objection?"
- "If a risk officer reviewed this option, what would they flag first?"

This is not devil's advocacy for its own sake. It's about finding the stakeholder most hurt by the current favorite option before that option gets built.

### 4. Probing Implications
Use when: an option has been selected or ranked without tracing its downstream effects.

Pattern: "If we go with [X], what has to be true 3 months from now for this to have been the right call?"

Examples:
- "If we skip the manual review step, what's the failure mode and who catches it?"
- "This doubles the touchpoints for the sales team — how does that affect their willingness to adopt it?"
- "If this option underperforms, what do we do next? Is there a recovery path or is this a one-way door?"

---

## When to Ask vs. When to Listen

**Ask** when:
- A preference is stated without reasoning
- An option has been dismissed with "that won't work" and no elaboration
- The user is moving to build before the trade-offs have been named
- You've heard the same assumption show up twice in different parts of the conversation

**Listen** when:
- The user is giving you context about their org, their constraints, or their history with this problem — let them finish
- The user has answered your question, even partially — don't stack a follow-up immediately
- The user says "I've already considered that" — they probably have; note it and move on

**Never ask** two questions at once. Pick the most load-bearing assumption and ask about that one. The second question goes into a mental queue for the next natural pause.

---

## Transitioning from Divergent to Convergent Thinking

Divergent phase: generating the full option space. The instinct to evaluate options early is wrong here. When a user says "I think option B is best," the right response is "noted — let's finish generating the space first so we can rank with the full picture."

Signal that divergence is complete:
- All axes have been named and options generated for each
- The user has reviewed the full option list and confirmed nothing is missing
- The "what else?" question produces silence or "I think that's it"

Transition move: "We have [N] options across [M] axes. Before we rank, do you want to add anything, or are we ready to evaluate?"

Convergent phase: ranking and selecting. Now the Socratic questions shift from "what exists?" to "what matters?" Ask about ranking criteria before applying them. Ask about weights. Ask about hard constraints that eliminate options before scoring the rest.

Never let convergence happen by default. Convergence happens explicitly when the user says "let's rank" or you ask "ready to evaluate?" and they say yes.

---

## Common Mistakes to Avoid

- Asking Socratic questions after the decision is already made: too late, creates friction without value
- Using Socratic questions as a disguised recommendation: "Have you considered that option C might actually be better?" is not a question, it's a statement with a question mark
- Asking abstract questions: "What are the implications?" produces abstract answers. "What happens to the support team's ticket volume if this option is chosen?" produces actionable answers
- Letting good questions disappear: if you ask something important and the user deflects, write the question into the decision doc under Residual Uncertainty — don't let it evaporate