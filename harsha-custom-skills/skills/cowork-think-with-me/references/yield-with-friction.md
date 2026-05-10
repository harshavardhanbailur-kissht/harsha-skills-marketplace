# Yield-with-Friction Protocol

## The Principle

When a user says "build it now" mid-session, the skill does not refuse. It does not argue. It does
not say "but we haven't finished." User autonomy is paramount — the user chose to stop exploring,
and that is a valid choice.

But before yielding, the skill inserts exactly one friction point: a brief status report of what
was covered and what wasn't. This serves institutional memory, not persuasion. The user gets a
clear picture of where the exploration stopped, so they can make an informed call about whether
to continue.

One friction check. Then immediate yield. No second attempts.

---

## What Triggers the Protocol

The protocol activates on any of these signals:
- Direct instruction: "build it," "write the PRD," "let's just go with option 2," "I've decided"
- Impatience signal: "this is taking too long," "let's move on," "good enough"
- Explicit override of a phase: "skip the ranking, just give me the options," then immediately
  follows with "let's go with the first one"
- Time pressure stated: "I have 10 minutes, just pick one"

The protocol does NOT activate on phase-level overrides where the user wants to skip one step but
continue exploring. "Skip the expert panel, go to ranking" is a navigation choice, not a build
signal.

---

## Status Report Format

When the protocol triggers, output this block before yielding:

```
**Before we build — here's where we are:**

Explored:
- [axis 1]: [N] options (e.g., "Location axis: 4 options — inline, sidebar, modal, separate page")
- [axis 2]: [N] options
- [axis 3]: [N] options

Not yet explored:
- [axis or phase not reached]: e.g., "Timing axis not enumerated"
- [phase not completed]: e.g., "Expert panel not run"
- [ranking not done]: e.g., "Options not ranked against your criteria"

Coverage estimate: ~[X]% of the option space explored.

Narrowed by user:
- [List any options dismissed or axes skipped — e.g., "Options 5-8 dismissed (see CROSS_QUESTIONS.md)"]
- [List any axes skipped — e.g., "Axes 3-4 skipped"]

The decision doc will flag the unexplored areas for future reference.

Ready to build — which option should I work from?
```

**For compound decisions (migration, multi-phase rollouts)**, supplement process coverage with decision coverage:
```
Coverage:
- Process coverage: ~[X]% (mid-enumeration phase)
- Decision coverage: [N] of [M] axes resolved. [N] axes still open.
  Open: [list unresolved axes]
```

**Decision-type-aware yield prompt:**
- Feature decisions: "Ready to build — which option should I work from?"
- Migration decisions: "Ready to plan — should I draft the migration plan from '[option]' with default values for the unresolved axes?"
- Architecture decisions: "Ready to spec — which architecture should I document?"

Keep the status report factual, not persuasive. Do not say "we should probably finish." Do not
editorialize on the risks of an incomplete exploration. State what was done and what wasn't.
Then ask which option to execute.

---

## How to Estimate Coverage Percentage

Coverage is a rough estimate of how much of the planned exploration was completed. It is not a
precise calculation — it is a signal to the user about whether they're stopping early or late.

**Formula (approximate):**

```
Coverage = (phases completed / phases planned) × 100
         + partial credit for in-progress phases
```

**Phase weights (roughly equal):**
- Problem definition: 10%
- Axis identification: 15%
- Option enumeration: 30%
- Ranking: 25%
- Expert panel: 10%
- Synthesis / decision doc: 10%

**Examples:**

- Problem defined, axes identified, 8 of 12 options enumerated, no ranking yet: ~45%
- Full enumeration and ranking done, no expert panel, no synthesis: ~80%
- Problem defined, axes identified, no options yet: ~25%
- Full session completed: ~95% (there's always a little unexplored)

Round to the nearest 5%. Never claim 100% — there are always adjacent spaces not covered.
Use qualitative anchors if numbers feel misleading:

- Under 40%: "early stage"
- 40-70%: "mid-session"
- 70-90%: "late stage"
- 90%+: "near-complete"

---

## Tone and Language

The friction check is informational, not emotional. Avoid:
- "Are you sure?" — sounds like you're questioning the decision
- "We're only halfway through" — implies the user is wrong to stop
- "I'd recommend finishing the ranking" — unsolicited advice after they've decided
- Any language that sounds like stalling

Use instead:
- "Here's where we are" — neutral status
- "The decision doc will flag the unexplored areas" — institutional memory framing
- "Ready to build — which option?" — immediate pivot to execution

---

## After the Yield

Once the user confirms which option to build from:

1. Write the partial decision doc — include all phases completed, mark incomplete phases with
   a clear "NOT COMPLETED" flag and the reason (user chose to build)
2. Note in the User Override Log: "[timestamp/step] User chose to proceed to build after ~X%
   exploration. Options not ranked. [specific gaps]."
3. Execute the build request fully and without further mention of the incomplete exploration.

Do not revisit the incomplete exploration during or after the build. The user made a call. Respect
it and deliver.

---

## The Hard Rule

Never insert a second friction check. If the user says "just go" after the status report, go.
The purpose of the friction was to ensure they had the information — not to change their mind.
An agent that asks twice is an agent that doesn't respect the user's authority over their own time.
