# Anti-Padding Heuristics

## The Core Problem

Padding happens when the skill generates options to hit a number rather than to serve the user.
The result: a long list that feels thorough but wastes the user's time, because the marginal
options don't represent real choices anyone would face.

The antidote is not fewer options — it's honest options. Ten genuine options beats twelve padded
ones. Three genuine options beats ten padded ones.

---

## The Gut-Check

"If you stopped at 3, you didn't try."

This phrase exists to push past the first obvious cluster of ideas. Most problems have 3 options
that come to mind immediately. Stopping there means you generated options from the surface of your
knowledge, not from a structured enumeration. You likely missed options in different axes entirely.

But the inverse is equally true: don't pad to hit a number. The gut-check is about effort, not
arithmetic. If you genuinely have 5 distinct options and are about to write a 6th that's a rewording
of option 2, stop.

---

## Quality Signals for a Genuine Option

An option is genuine if it passes all three:

**1. Addresses a real user need**
Could a real stakeholder advocate for this option with a straight face? Not "technically this is
an option," but "a product manager in a real company would propose this as the right approach."
If the option has no natural constituency — no user segment, no business goal, no stakeholder who
would fight for it — it is not a real option.

**2. Is implementable**
Not necessarily easy, but implementable within the constraints of the problem. An option that
requires technology that doesn't exist, regulatory approval that isn't possible, or a team 10x
larger than what exists is not a real option for this decision. It might belong in "unexplored
adjacent spaces" but not in the ranked option set.

**3. Differs meaningfully from adjacent options**
"Meaningfully" means: a decision-maker choosing between option A and this option would have a
genuinely different outcome — different users served, different cost structure, different risk
profile, different implementation path. If swapping options A and B would produce nearly identical
outcomes, one of them is padding.

---

## When an Axis Is Fully Enumerated

An axis is fully enumerated when:
- You have covered all structurally distinct positions on that axis
- Adding another position would require inventing a distinction that doesn't exist in practice
- The options you have already span from one logical extreme to the other

Example: on a "notification timing" axis, you might have: immediate, batched (hourly), batched
(daily), on-demand only. Adding "batched (every 47 minutes)" is not a new axis position — it's
arithmetic padding within a position you already named.

An axis is NOT fully enumerated when:
- You have covered only the obvious positions and haven't considered edge cases
- You've anchored on one end of the spectrum and not considered the other
- You haven't included the "don't do this at all" position (zero is always a valid axis value)

---

## Red Flags for Padding

**Options that are rephrased versions of each other**
If you can combine two options into one by adding the word "or" in the middle — "show inline or
show in a panel" — those were never two options. They were one option with a sub-choice.

**Options no stakeholder would actually advocate for**
"Do nothing" is legitimate. "Do a half-measure that satisfies nobody" is padding. If you can't
write a sentence starting with "The case for this option is..." without reaching, cut it.

**Options that exist only to be rejected**
If you're generating an option specifically so you can say "we considered and rejected this," and
it wasn't a real candidate, that's not intellectual honesty — it's theater. The decision doc's
"rejected options" section should contain options that were genuine contenders, not straw men.

**Adjective-only differentiation**
"Simple version" vs "full version" vs "lightweight version" — if the only difference is a modifier
that implies quality or scope, you haven't identified three options, you've identified one option
at three budget levels. That might be a real axis (effort/scope), but enumerate it as one axis with
three positions, not three separate options.

**Options that require the same decision to resolve**
If you'd need a separate decision meeting to choose between two "options," they aren't final
options — they're directions that each contain their own option space. Either go one level deeper
or keep them as directions and enumerate within each.

---

## The Completeness Test

When you think you're done enumerating, run this check:

1. Can I name a stakeholder who would fight for each option? (If not, cut it.)
2. Are there axes I haven't used at all? (If yes, at least one option from each unused axis.)
3. Have I included the "don't do this" option? (It's almost always valid.)
4. Would a domain expert in this area recognize all of these as real choices? (If they'd laugh at
   one, it's padding.)
5. Are any two options distinguishable only by degree, not by kind? (If yes, they may belong to
   one axis, not two options.)