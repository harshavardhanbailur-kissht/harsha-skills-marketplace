# 03 — Ticket-Type Detection

## Why detection is upfront and explicit

The 6 exemplars cluster cleanly into 5 archetypes. Each archetype has a different optimal spine and a different question subset. If we run the wrong question set, the PM either gets asked irrelevant questions (wasting their patience) or has critical questions skipped (producing an unfeedable ticket).

So Phase 3 detection is non-skippable. The skill names the type, justifies it from heuristic signals, and the PM gets one chance to override.

## The five types

| Code | Type | Exemplar | Spine shape | Mandatory blocks |
|---|---|---|---|---|
| **WC** | Workflow Change | LAP-1812, LAP-2048 | Intent → Actors → Preconditions → Numbered functional flow with sub-steps → AC by area → Sources | Actors, Preconditions, Functional Flow, AC by area |
| **BO** | Branching Outcome | LAP-2046 | Intent → Problem → Proposed solution with Step 1 / Step 2 / Case 1 / Case 2 → Applicability → Exception → Summary table | Numbered logic, Cases, Summary table |
| **MX** | Mixed (workflow + branching inside) | (no pure exemplar; combination of LAP-1812 + LAP-2046 patterns) | WC spine with Cases embedded inside one stage | Everything from WC + Case sub-blocks |
| **RD** | Reference-data / config / matrix | LAP-2052, LAP-2242 | Intent → Per-system or per-matrix-row breakdown → Matrix table → QA Scenarios → Role Definitions | Matrix or per-system breakdown, QA Scenarios |
| **SF** | Single-form behaviour change | LAP-2039 | Problem → Current flow → Proposed solution → QA Scope → Open Considerations for BA | Current flow, Proposed solution, QA Scope, BA Open Considerations |

## Detection heuristic (run after Phase 2 verify, before Phase 4 questions)

The detector reads the **scoped intent statement** from `INTENT.md` plus the **related-tickets summary** from `RELATED.md`. It evaluates 8 signals and scores each type. Highest score wins; ties resolved by the priority WC > MX > BO > SF > RD (because under-classifying a workflow change as a branching outcome loses the stage/owner detail; over-classifying a branching outcome as a workflow change just adds an empty Actors block).

### Signals

| Signal | Detection cue (in `INTENT.md` or PM's opening message) | Type weight |
|---|---|---|
| **S1** mentions a NEW stage / new approval level / new SLA / new mandatory action | words: "new stage," "approval queue," "after N days," "auto-close," "expires," "hard reject," "lost rejected," "introduce" + stage name | WC + 3 |
| **S2** mentions ≥2 if-branches off ONE action with NO new stage | words: "if X then ... if Y then," "Case 1 / Case 2," "branches" + no stage word | BO + 3 |
| **S3** mentions a single form / toggle / field move / validation change | words: "move field," "toggle," "switch," "validation," "Mark as Complete form," "edit form," "field defaults to" | SF + 3 |
| **S4** mentions a dropdown sync / matrix / config / cross-system reference data | words: "dropdown," "matrix," "list of values," "approver matrix," "slab," "config screen," "values across" | RD + 3 |
| **S5** mentions ≥2 systems with cross-system contracts | "LSQ <> LOS," "LAP <> LMS," "Digio integration," "LSQ to LMS push" | WC + 1, RD + 1 |
| **S6** mentions multi-act flow with bypasses or time windows | "bypass," "valid for N years," "within N hours," "soft reject vs hard reject" | WC + 2 |
| **S7** mentions a current operator workaround being replaced | "today the BCM has to," "currently they fill junk," "manual workaround," "long way around" | SF + 2 |
| **S8** mentions branching INSIDE a workflow change | "new stage AND if X then Y" — both S1 and S2 fire | MX + 5 (overrides) |

If MX fires, it overrides; otherwise highest scorer wins.

### Worked detection (against the 6 exemplars)

| Exemplar | Cues that fired | Score | Detected type | Matches actual? |
|---|---|---|---|---|
| LAP-1812 | S1 (Post Sanction stage anchor, drop-off resume, expiry handling), S5 (LSQ + Kissht + Digio), S6 (10-day expiry, drop-off resume) | WC=6 | WC | Yes |
| LAP-2039 | S3 (Mark as Complete form, toggle, field move), S7 (BCM fills junk values today) | SF=5 | SF | Yes |
| LAP-2046 | S2 (Case 1: VCIP Yes, Case 2: VCIP No), S4 (applicability matrix), S5 (LSQ for LAP) | BO=4, RD=4, tie → BO wins by priority — but actual is also presented as a clean BO with a summary table. Acceptable. | BO | Yes (with summary-table support) |
| LAP-2048 | S1 (mandatory VCIP, disable Physical KYC, "Onboarded" status), S5 (LSQ + Kissht + Digio), S6 (72h Digilocker, 9y6mo VCIP, soft/hard reject) | WC=6 | WC | Yes (Epic-shaped WC) |
| LAP-2052 | S4 (dropdown sync, list of values, sheet link), S5 (LSQ + LOS) | RD=4 | RD | Yes |
| LAP-2242 | S4 (approver matrix, slab, configurable), S2 (slab branches) | RD=4, BO=3 | RD | Yes |

Detection works on all 6 exemplars. The interesting case is LAP-2046 where BO and RD tied — we take BO and the resulting spine includes the summary table at the end (which the BO spine allows but doesn't require). So both spines would actually produce an acceptable ticket here; the BO spine is preferred because it forces the per-Case See/Do/Verify discipline.

## Override protocol

If the PM disagrees with the detected type:

1. Skill announces: "I detected this as **WC** because ___. You can override to MX / BO / SF / RD — which?"
2. PM picks. Selection is logged to `TYPE.md` with a `## User override` section recording the original detection, the override, and the PM's stated reason.
3. The skill loads the new type's question set and proceeds. No second cross-question (per cowork-think-with-me's "one cross-question and yield" rule).

## What if no signals fire?

Then `INTENT.md` is too thin. The skill loops back to Phase 2 and asks the PM to expand the intent statement with one more sentence covering "what changes structurally — a stage, a branch, a form, a list?" — and re-runs detection.

If the second pass also produces no signal, default to **SF** (Single-form change) and warn the PM: "I'm defaulting to SF because no structural signal fired. If this is actually a workflow change or matrix change, override now."

## Adaptation per type — concrete deltas

### WC (Workflow Change) adaptation

- **Question set additions**: Category B (current flow) is mandatory. Category D demands stage names + owners verbatim. Category E asks "what's the entry condition for the new stage? what's the exit condition? what's the SLA? what happens at SLA breach?"
- **Spine differences**: opens with **Primary Actor + Secondary Actors** block (LAP-1812 pattern). Includes **Preconditions**. Numbered Functional Flow has sub-steps (1.1 / 1.2 / 1.3). AC is **organised by area**, not flat.
- **Validation differences**: every named stage MUST have an owner role. Drop-off and resume logic MUST be explicit. Expiry handling MUST be explicit.

### BO (Branching Outcome) adaptation

- **Question set additions**: Category E is the spine; the See/Do/Verify triplet per Case is mandatory. Category G (auto-comm) and Category H (silent action) trigger more often because branches frequently involve silent system actions.
- **Spine differences**: NO actor block (the actor is implicit — one operator). NO preconditions block (the operator is already in flow). Each Case is an H2 sub-section. Summary table optional but recommended when ≥3 Cases.
- **Validation differences**: at least 2 Cases. Each Case has all three slots filled. Manual-backup flag set if any Case involves auto-comm.

### MX (Mixed) adaptation

- **Question set**: union of WC and BO question sets, but the skill is explicit about which questions belong to which slice. PM is told upfront: "This is a workflow change with branches inside Stage X. We'll do the WC questions first, then drill into the branches."
- **Spine differences**: WC spine, but the relevant stage in the Functional Flow is replaced with embedded Case 1 / Case 2 sub-blocks (per kissht-field-release-notes Mixed-ticket guidance).
- **Risk**: this is the type most likely to bloat. The skill enforces "no more than one stage may have embedded branches — if two stages branch, you have two tickets."

### RD (Reference-data) adaptation

- **Question set additions**: Category F (matrix) is mandatory. Category D demands every dropdown value enumerated. Category C asks "every touchpoint where this list appears" — and the spine enumerates them per system.
- **Spine differences**: NO Current flow block (the flow doesn't change; only the values do). NO Cases. The spine is **per-system** or **per-matrix-row**. Includes a **Source-of-truth link** (sheet, config doc) and a **Role Definitions** appendix (LAP-2242 pattern) when role acronyms appear.
- **Validation differences**: every dropdown value matches the source-of-truth sheet. Every touchpoint stage is named verbatim. Source link is live and accessible.

### SF (Single-form) adaptation

- **Question set additions**: Category B is mandatory and must produce a numbered list of pain steps (LAP-2039 had 6 numbered current-state steps). Category E asks bidirectional behaviour ("Yes → No AND No → Yes").
- **Spine differences**: opens with **Problem** statement, then **Current flow that we want to fix** (numbered), then **Proposed solution** (numbered, with consequences). NO actors block (it's implicit — one operator on one form).
- **Validation differences**: Yes-path and No-path behaviour both specified. State-refresh check explicitly asked. Primary-applicant vs. co-applicant distinction explicitly addressed (the LAP-2039 lesson).

## What gets the same regardless of type

Every ticket, regardless of type, gets:

- **Intent paragraph** (Category A) — always.
- **QA Scope** (Category J) — always.
- **BA Scope / Open Considerations** (Category K) — always.
- **Acceptance Criteria** (Category L, lean) — always.
- **Sources** (Category M) — always.
- **Contacts** (Category N) — always.

These are the universal constants — the 8 content principles that survive across types.

## What if a ticket genuinely doesn't fit any of the 5 types?

This should be rare given the 6-exemplar coverage spans every common LAP shape. But if it happens:

1. The skill recognises it (no signal scores ≥3 after both passes).
2. It announces: "This doesn't match any of the 5 standard types. I'll route to the **fallback spine**: Intent → Description → Logic → QA → BA → AC → Sources. This is uniform but less type-specific."
3. The fallback spine is the universal structure with no type-specific blocks. It still produces a feedable ticket; it just doesn't optimise for any one shape.

The fallback exists so the skill never refuses to produce a ticket. Refusal would push the PM back to free-form Jira — which is what we're trying to fix.
