# 02 — Ticket Type Taxonomy

## Why type detection is upfront and explicit

The 6 LAP exemplars cluster cleanly into 4 archetypes (plus a small mixed bridge). Each archetype has a different optimal spine, a different mandatory question subset, and different failure modes. If the skill runs the wrong question set, the PM either answers irrelevant questions (wasting patience) or skips critical ones (producing an unfeedable ticket). So Phase 3 is non-skippable.

This file aligns the LAP types with the downstream `kissht-field-release-notes` patterns:

- **Pattern A** in the release-notes skill = Workflow Change / Relook → upstream produces a **WC** ticket.
- **Pattern B** in the release-notes skill = Branching Outcome / Renach → upstream produces a **BO** ticket.
- A third "Simple Change" type (**SC**) handles single-form behaviour changes (LAP-2039 shape) — these flow into **either** release-note pattern depending on what the change touches, so the upstream type is held distinct.
- A fourth "Reference Data" type (**RD**) handles dropdown / matrix / config (LAP-2052, LAP-2242 shape).
- A bridge type (**MX**) handles mixed WC-with-branching-inside (no pure exemplar; both LAP-1812 and LAP-2046 patterns).

The four primary types — WC, BO, SC, RD — plus the MX bridge cover all 6 exemplars and every Story / Epic / Task we expect to see.

---

## The four types (plus bridge)

### WC — Workflow Change

**Maps to downstream:** Pattern A (Relook).
**Exemplars:** LAP-1812 (E-Sign Phase 2), LAP-2048 (Video KYC epic).
**One-line definition:** Introduces a new stage, a new approval chain, a new SLA, or a new mandatory action — i.e., the operator's flow changes shape.

**Detection cue (one line):** The intent statement names a NEW stage / approval level / SLA / hard-reject window, or the change adds an actor who wasn't in the flow before.

**Mandatory blocks in the spine:**
- Release-note line (top)
- Intent paragraph
- Primary Actor + Secondary Actors
- Preconditions
- Numbered Functional Flow with sub-steps (1.1, 1.2 …)
- AC organised by area (not flat)
- Sources / contacts

**Conditional blocks:** Matrix table (only if the WC includes routing); Cases (only if MX, otherwise none).

**Forbidden blocks:** Per-Case See/Do/Verify (those belong to BO). Single-system reference-data table (that's RD).

---

### BO — Branching Outcome

**Maps to downstream:** Pattern B (Renach).
**Exemplar:** LAP-2046 (PAN re-verification ETB).
**One-line definition:** One operator action triggers ≥2 if-branches with no new stage and no new SLA.

**Detection cue (one line):** The intent statement contains "if X then ... if Y then ..." structure, OR the PM's mental model is "operator clicks one thing, system goes one of N ways."

**Mandatory blocks:**
- Release-note line
- Intent paragraph
- Problem
- Proposed solution with **Step / Case** structure (Step 1, Step 2 → Case 1, Case 2, …)
- Per-Case **See / Do / Verify** triplet
- Applicability matrix
- Summary table (recommended when ≥3 Cases)

**Conditional blocks:** Exception block (when one Case is a real exception, not a branch); Auto-comm flag (when any Case fires an SMS/email).

**Forbidden blocks:** Primary/Secondary Actors block (the actor is implicit — one operator). Preconditions block (the operator is already in flow). Stage-list block.

---

### SC — Simple Change

**Maps to downstream:** Pattern A or B depending on what the change touches (single-form behaviour can be either; the release-notes skill picks at its Phase 2).
**Exemplar:** LAP-2039 (Income Considered move — user's gold standard).
**One-line definition:** A bounded, single-surface change — one form, one toggle, one field move, one validation tweak. No new stage, no new branch chain, no cross-system dependency.

**Detection cue (one line):** The intent statement names a single form/field/validation by name AND there is a current operator workaround being killed (`"today the BCM has to..."`).

**Mandatory blocks:**
- Release-note line
- Problem (1 paragraph)
- Current flow that we want to fix (numbered, painful — the workaround being killed)
- Proposed solution (numbered, with consequences per step)
- QA Scope (named, with state-refresh scenarios)
- Open Considerations for BA (assumption + proposal + impact per item)

**Conditional blocks:** Bidirectional behaviour block (when a toggle is bidirectional — Yes→No AND No→Yes both must be specified); Primary-vs-co-applicant scope block (the LAP-2039 lesson: always check whether the change applies to both or just co-applicants).

**Forbidden blocks:** Actor block, Preconditions block, Matrix table, multi-stage AC.

**Why SC is its own type (not just a subset of WC).** A WC ticket has a flow shape that changes; an SC ticket has a flow shape that stays the same with a behaviour swap inside one screen. The question sets and validation gates differ enough that conflating them produces bloat (SC tickets don't need actor/precondition lists) and gaps (SC tickets must specify bidirectional toggle behaviour, which WC doesn't).

---

### RD — Reference Data / Matrix / Config

**Maps to downstream:** Mostly Pattern A (cross-system change) but can be a thin Pattern B if a matrix selects between branches.
**Exemplars:** LAP-2052 (Property dropdown sync), LAP-2242 (Approval matrix).
**One-line definition:** Dropdown sync, value list change, approval matrix update, slab thresholds, or any config that changes data without changing flow.

**Detection cue (one line):** The intent statement names "matrix / dropdown / slab / list of values / config screen" AND the structural change is to which value gets which treatment, not to the steps of the flow.

**Mandatory blocks:**
- Release-note line
- Intent paragraph
- Per-system OR per-matrix-row breakdown
- Matrix table
- QA Scenarios (per row + boundary cases)
- Source-of-truth link (the canonical sheet / config doc)
- Role Definitions appendix (when role acronyms appear — the LAP-2242 pattern)

**Conditional blocks:** Configurability statement ("can ops update this without code deploy?"); State-wise variant block (when the matrix has geographic variants — LAP-2242 SCH 1 / SCH 2 lesson).

**Forbidden blocks:** Current Flow block (the flow doesn't change — only values do); per-Case See/Do/Verify; Actor block.

---

### MX — Mixed (bridge)

**Maps to downstream:** Pattern A with embedded Case sub-blocks per the release-notes skill's Mixed-ticket guidance.
**No pure exemplar** — surfaces when both WC and BO signals fire strongly.
**One-line definition:** A workflow change that introduces branching inside one new stage.

**Detection cue (one line):** Both Signal-1 (new stage) AND Signal-2 (≥2 if-branches off one action) fire on the same intent statement.

**Spine:** WC spine, with the relevant stage's Functional Flow step replaced by embedded Case 1 / Case 2 sub-blocks. **Hard rule:** at most ONE stage may have embedded branches. If two stages branch, the skill insists on splitting into two tickets.

**Why MX exists as a bridge, not a fifth primary type.** It re-uses the WC spine plus the BO Case mechanism — there's no new template needed; the question set is the union; the validation is the union. It's a routing decision more than a category.

---

## The 8-signal detector

The detector reads `INTENT.md` + `RELATED.md` after Phase 2 and scores each type. Highest score wins; ties resolved by priority WC > MX > BO > SC > RD (under-classifying a workflow change as a branching outcome loses stage/owner detail; over-classifying a branching outcome as a workflow change just adds an empty Actors block — the asymmetry justifies the priority).

| # | Signal | Cue (in INTENT.md or PM opening) | Type weight |
|---|---|---|---|
| S1 | NEW stage / approval level / SLA / mandatory action | "new stage," "approval queue," "after N days," "auto-close," "expires," "hard reject," "lost rejected," "introduce" + stage name | WC + 3 |
| S2 | ≥2 if-branches off ONE action with NO new stage | "if X then ... if Y then," "Case 1 / Case 2," "branches" — without stage word | BO + 3 |
| S3 | Single form / toggle / field move / validation change | "move field," "toggle," "switch," "validation," "Mark as Complete form," "edit form," "field defaults to" | SC + 3 |
| S4 | Dropdown / matrix / config / cross-system reference data | "dropdown," "matrix," "list of values," "approver matrix," "slab," "config screen," "values across" | RD + 3 |
| S5 | ≥2 systems with cross-system contracts | "LSQ <> LOS," "LAP <> LMS," "Digio integration," "LSQ to LMS push" | WC + 1, RD + 1 |
| S6 | Multi-act flow with bypasses or time windows | "bypass," "valid for N years," "within N hours," "soft reject vs hard reject" | WC + 2 |
| S7 | Current operator workaround being replaced | "today the BCM has to," "currently they fill junk," "manual workaround," "long way around" | SC + 2 |
| S8 | Branching INSIDE a workflow change | both S1 and S2 fire | MX + 5 (overrides) |

If MX fires (S1 + S2 both ≥1), it overrides; otherwise highest scorer wins. If no signal scores ≥3 after a Phase-2 expansion loop, the skill defaults to **SC** with a warning.

### Worked detection across the 6 exemplars

| Exemplar | Cues fired | Score | Detected | Matches actual? |
|---|---|---|---|---|
| LAP-1812 | S1, S5, S6 | WC=6 | WC | Yes |
| LAP-2039 | S3, S7 | SC=5 | SC | Yes (gold standard) |
| LAP-2046 | S2, S4, S5 | BO=4, RD=4 → tie → BO wins by priority | BO | Yes |
| LAP-2048 | S1, S5, S6 | WC=6 | WC | Yes (Epic-shaped WC) |
| LAP-2052 | S4, S5 | RD=4 | RD | Yes |
| LAP-2242 | S4, S2 | RD=4, BO=3 | RD | Yes |

Detection works on all 6.

---

## Spine differentials at a glance

| Block | WC | BO | SC | RD | MX |
|---|:-:|:-:|:-:|:-:|:-:|
| Release-note line (GitLab borrow) | required | required | required | required | required |
| Intent paragraph | required | required | required | required | required |
| Primary + Secondary Actors | required | forbidden | forbidden | optional | required |
| Preconditions | required | forbidden | forbidden | optional | required |
| Current flow that we want to fix | optional | required | required | forbidden | required |
| Numbered Functional Flow | required | forbidden | forbidden | forbidden | required |
| Step / Case (See/Do/Verify) | forbidden | required | forbidden | forbidden | required (for one stage only) |
| Matrix table | optional | optional | forbidden | required | optional |
| Per-system or per-row breakdown | forbidden | forbidden | forbidden | required | forbidden |
| Source-of-truth link | optional | optional | optional | required | optional |
| QA Scope / QA Scenarios | required | required | required | required | required |
| BA Open Considerations | required | required | required | required | required |
| Out of scope (Shape Up borrow) | required | required | required | required | required |
| Alternatives considered (Google borrow) | optional | optional | optional | optional | optional |
| AC organised by area | required | required | required | required | required |
| Role Definitions appendix | optional | optional | optional | required (when acronyms used) | optional |
| Sources / Contacts / Bug fan-out | required | required | required | required | required |

---

## Override + fallback

**Override:** If the PM disagrees with the detected type, they pick from the menu of 5. Override logged in `TYPE.md`. No second cross-question (cowork-think-with-me discipline).

**Fallback:** If no signal fires after the Phase-2 expansion loop, the skill defaults to **SC** with a banner: "I'm defaulting to Simple Change because no structural signal fired. If this is actually WC / BO / RD / MX, override now." This guarantees the skill never refuses to produce a ticket.

**Bug routing:** The skill explicitly does NOT handle Bug issue type — Bugs route to a hand-off template that says "use the LAP bug template; this skill is for Story / Epic / Task." (See file 08 F-Bug.)
