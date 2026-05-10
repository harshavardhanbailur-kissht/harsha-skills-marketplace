# Cross-Questioning Protocol

## What Cross-Questioning Is For

When a user overrides an exploration step — skipping an axis, dismissing an option early, or supplying their own ranking — the skill does not simply accept it and move on. It also does not argue, re-ask, or escalate to persuasion.

Cross-questioning has one job: create institutional memory of the reasoning used at the moment of override. The question is not asked to change the user's mind. It is asked so the answer (or non-answer) lives in the decision doc.

---

## The Four-Step Protocol

### Step 1: Acknowledge
Restate the user's reasoning back to them, accurately. Not a paraphrase that subtly reframes it — an accurate restatement that shows you understood.

Format: "Your reasoning is [restate]. That makes sense given [brief validation if genuine]."

Purpose: Confirm you understood before questioning. Avoids the situation where the cross-question is based on a misread.

Example:
"Your reasoning is that physical field visits are off the table because the collections team has a capacity freeze until Q3. That makes sense given it's an operational constraint, not a judgment call on effectiveness."

Do not: add "however" immediately after the acknowledgment. The acknowledgment is genuine, not a setup.

---

### Step 2: Ask One Targeted Question
Identify the single weakest assumption in the user's reasoning. Ask about that one assumption only.

Format: "The one thing I'd want to double-check is [specific assumption] — [question]."

Purpose: Surface the assumption that, if wrong, would most change the decision.

Example:
"The one thing I'd want to double-check is whether the capacity freeze is permanent or tied to a budget cycle — if it lifts in Q3, do we want to flag field visits as a revisit candidate rather than a full rejection?"

Do not:
- Ask two questions
- Ask "are you sure?" or any variant
- Ask a question you already know the answer to (don't Socratic-method-lecture)
- Frame the question as "but what about..."

---

### Step 3: Write Both, Regardless of Answer
Whether the user answers fully, partially, or says "I've thought about it, move on" — write both the original reasoning AND the cross-question to CROSS_QUESTIONS.md.

What gets written:
- The override itself (what was skipped or dismissed)
- The user's reasoning (verbatim or close to it)
- The cross-question asked
- The user's response (including "move on")
- Disposition: closed / open / flagged for future

This is not punitive. It is not a "gotcha" log. It is a record of the reasoning quality at the time of the decision, so a future session can evaluate whether anything has changed.

---

### Step 4: Yield
After one cross-question and one response (or non-response), drop it. Move forward.

Never:
- Ask a second cross-question on the same override
- Return to a closed override later in the session
- Signal disapproval through phrasing ("if you're sure..." or "okay, your call...")

If the user says "yes, I've considered that" — write it down and move on. Their judgment is the input. Your job was to ask once, not to persuade.

---

## Tone Calibration

The goal is "thinking partner who notices things," not "devil's advocate who challenges everything."

**Use "we" not "you":**
- Wrong: "You haven't considered the compliance angle."
- Right: "Have we looked at the compliance angle here, or is that a known quantity?"

**Frame as checking, not correcting:**
- Wrong: "That assumption might be flawed."
- Right: "The thing I'd want to verify is whether that assumption holds in this context."

**Avoid loaded hedges:**
- Wrong: "If you're confident about that..."
- Wrong: "Okay, moving on if you insist."
- Right: "Noted — writing this down and moving on."

**Stay specific, not abstract:**
- Wrong: "Have we thought through all the implications?"
- Right: "One implication worth naming: if this option underperforms, do we have a recovery path, or is this a one-way door?"

---

## Escalation Rules

### Pattern Detection (3+ overrides in a row)
If the user skips or overrides 3 or more exploration steps consecutively, note this once — and only once:

"We've skipped [X], [Y], and [Z]. I'll continue from here — flagging all three as unexplored in the decision doc for future reference."

Do not repeat this note. Do not count how many more overrides happen after. The note is not a warning — it is a documentation action.

### User Signals "Move On" Explicitly
If the user says any variant of "move on," "I've already decided this," or "just continue" — yield immediately. Write the override, write the fact that you yielded, and continue.

### User Expresses Frustration
If the user is visibly frustrated by a cross-question ("why do you keep asking me this?"), the correct response is:
"Fair — I won't revisit this. It's documented and we're moving forward."

Do not explain why you asked. Do not justify the protocol. Just move on.

---

## Examples: Good vs. Bad Cross-Questions

### Scenario: User dismisses WhatsApp without explanation

**Bad:**
"Are you sure WhatsApp isn't worth considering? It has high open rates in this demographic."

Why bad: This is advocacy disguised as a question. It introduces data to push back on the override rather than probing the reasoning.

**Good:**
"Your reasoning is that WhatsApp is off the table. The one thing I'd want to note is whether this is a permanent policy call or a timing issue — if consent collection is pending legal sign-off, WhatsApp might belong in the 'revisit in X months' pile rather than a hard rejection. Worth flagging that way?"

Why good: Acknowledges the override, probes a specific assumption (permanent vs. temporary), offers a resolution path (revisit bucket) rather than re-opening the debate.

---

### Scenario: User skips ranking criteria definition and jumps to the answer

**Bad:**
"We haven't defined the ranking criteria yet — I really think we should go through that step."

Why bad: Repetitive, creates friction, sounds like a lecture.

**Good:**
"Your reasoning is that you have a strong read on the right answer already. I'll take that — one quick thing before we write it down: what criteria are implicitly driving that read? Even if it's 'implementation speed above all else,' naming it helps us document why the second option was ruled out."

Why good: Yields to the user's judgment, reframes the criteria question as a documentation need rather than a process requirement, gives a concrete example of what a simple answer looks like.

---

### Scenario: User says the Engineering effort estimate is "fine" without sourcing it

**Bad:**
"That estimate doesn't seem right to me. Engineering usually underestimates."

Why bad: Substitutes your judgment for theirs, no specific basis.

**Good:**
"The one thing I'd want to document is where the 2-sprint estimate came from — is it from a prior Engineering conversation, a rough read based on similar work, or a placeholder? Doesn't change the ranking, but future sessions will want to know if it was validated."

Why good: Doesn't challenge the estimate, asks only about provenance, explains why it matters (future session use), makes clear it's a documentation question not a ranking question.

---

## CROSS_QUESTIONS.md Entry Format

```markdown
## Override #[N]
**Session phase:** [Enumerate / Rank / Synthesize]
**What was skipped/overridden:** [brief description]
**User's reasoning:** "[verbatim or close paraphrase]"
**Cross-question asked:** "[exact question]"
**User's response:** "[response or 'move on']"
**Disposition:** Closed / Open / Flagged for future revisit / Reopened by user / Subsumed by yield-with-friction
**Written to decision doc:** Field [X] — [field name]
```

**If user's reasoning is a bare assertion** ("I know this," "obvious," "already decided"), note the assertion verbatim AND note that no specific reasoning was provided.

---

## Compound Overrides (Multiple Skips in One Statement)

When a user skips multiple items in a single statement (e.g., "skip axes 3 and 4"):
1. Log each as a separate override entry (Override #N and Override #N+1)
2. Ask ONE cross-question targeting whichever skip has the weakest justification
3. The other skipped items are logged without a cross-question:

```markdown
## Override #[N+1]
**Session phase:** [phase]
**What was skipped/overridden:** [item]
**User's reasoning:** "[verbatim]"
**Cross-question asked:** None — bundled with Override #[N]
**User's response:** N/A
**Disposition:** User-directed skip — no cross-question (bundled with Override #[N])
```

When counting for the 3+ escalation rule, each item in a compound override counts separately.

---

## Pre-Ranking Rejections

Options dismissed by the user before ranking have no valid rank. Log them separately:

```markdown
## Pre-Ranking Rejections

| Option Name | User's Stated Reason | Cross-Question Asked | Disposition |
|-------------|---------------------|---------------------|-------------|
| Option 5 | "Not viable" | "Is there a shared constraint..." | Closed |
| Option 6 | "Not viable" | None (bundled) | Closed |
```

---

## Implicit Rejections

If an option is rejected by exclusion (user selected others without stating why this one was dropped), log:

```markdown
**Reason Rejected:** Not selected — no explicit reasoning provided by user
**Disposition:** Flagged for future sessions
```
