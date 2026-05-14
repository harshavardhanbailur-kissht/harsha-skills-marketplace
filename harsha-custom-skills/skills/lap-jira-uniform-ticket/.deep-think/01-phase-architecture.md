# 01 — Phase Architecture

## The 8 phases (in order)

```
Phase 0  Activate & Set Destination
Phase 1  Auto-Search (Jira + Confluence)
Phase 2  Verify Context with PM
Phase 3  Classify Ticket Type
Phase 4  Socratic Decompose
Phase 5  Draft Into Uniform Spine
Phase 6  Anti-Repetition + Glossary Sweep
Phase 7  Validate Against Output Gates
Phase 8  Deliver (Markdown OR Push to Jira)
```

State persists in `.lap-ticket-session/<key-or-slug>/` so the PM can resume after a compaction, two PMs working overlapping scope can detect collision, and the downstream `kissht-field-release-notes` skill can backreference what was decided.

The Socratic discipline borrows from `cowork-think-with-me`: write to files as we go, one question at a time, never let the PM fill silence.

---

## Phase 0 — Activate & Set Destination

**Trigger.** PM types something like "write a Jira ticket for X" / "/lap-ticket" / drops a Loom or screenshot with the ask.

**The skill does (in order, single turn):**
1. Asks: **destination** — markdown to copy, OR push directly to Jira via `createJiraIssue` / `editJiraIssue`.
2. Asks: **issue type** — Story, Epic, Task. (Bug routes elsewhere — handed off to a bug template; see file 08 F-Bug.)
3. If push-to-Jira: reserves a Jira key by calling `createJiraIssue` with a stub body (`[DRAFTING — lap-jira-uniform-ticket session in progress]`). The key is locked; the body will be `editJiraIssue`-ed at Phase 8.
4. Creates `.lap-ticket-session/<key-or-slug>/` and writes `SESSION_STATE.md` (current phase, next action, override count).

**Exit criterion.** `SESSION_STATE.md` exists; destination + type recorded; for Jira push, key is reserved.

**Artifacts produced.** `SESSION_STATE.md`.

**Why this is its own phase.** Forces the PM to make the destination choice once, at the top, so we never produce a markdown blob and re-format for ADF. Also catches the "I'm enriching an existing ticket" case (PM gives an existing key) — that path skips reservation and pre-loads the existing body.

---

## Phase 1 — Auto-Search

**Trigger.** SESSION_STATE.md exists. PM has typed the one-line ask.

**The skill does:**
1. Extracts intent keywords from the PM's opening message (stage names, role acronyms, surface area words like "form / dropdown / matrix / approval").
2. Runs JQL on the LAP project, recent 6 months: keyword stems against summary + description.
3. Runs CQL on the LAP Confluence space: same keywords + always-include the canonical pages (LOS canonical 1088716805, LAP Query Module Guide 1101660180).
4. Loads the three inherited glossary files: `lap-glossary.md`, `lap-stages.md`, `lap-roles.md` (from `kissht-field-release-notes/references/` and `knowledge-base/`).
5. Writes candidate sets to `RELATED.md` (each ticket: key + title + status + 1-line summary; each Confluence page: page-id + title + last-modified).

**Exit criterion.** `RELATED.md` exists with bounded candidate sets (capped at 10 tickets + 5 pages — if more, the skill ranks by recency × keyword density and trims, flagging the trim count).

**Artifacts produced.** `RELATED.md`, glossary loaded into session memory.

**Why mandatory and upfront.** If we ask the PM Socratic questions before knowing what already exists, we waste their time on context the related ticket already supplies, miss inherited stage/role names, and produce a ticket that overlaps with one a colleague filed two weeks ago. This is the deep-thinker "ground in reality before theorising" step.

---

## Phase 2 — Verify Context with PM

**Trigger.** `RELATED.md` exists.

**The skill does:**
1. Presents each candidate ticket, asks PM to tag: **parent / sibling / superseded / unrelated**. Default unrelated.
2. Presents canonical Confluence pages, asks PM to confirm authoritative sources. (Default-keep the two canonicals; PM can add others.)
3. Drafts a one-paragraph **scoped intent statement** from the PM's opening + the confirmed related context. Asks PM to sign off word-for-word.

**Exit criterion.** PM has confirmed (a) related-ticket tags, (b) Confluence sources, (c) intent paragraph signed off.

**Artifacts produced.** `INTENT.md` (signed-off paragraph), `RELATED.md` (now tagged).

**Why a separate phase.** Auto-search is a noisy filter; the PM does the relevance pass. Without this human step, the skill confidently inherits wrong context — the confirmation-bias failure applied to source selection.

---

## Phase 3 — Classify Ticket Type

**Trigger.** `INTENT.md` is signed off.

**The skill does:**
1. Runs the 8-signal heuristic from file 02 against `INTENT.md` + `RELATED.md`.
2. Names the type, with a one-line justification citing which signals fired.
3. PM gets one chance to override (logged, no second cross-question — `cowork-think-with-me`'s "one cross-question and yield" rule).

**Exit criterion.** `TYPE.md` written, with `Detected: <code>` + `Override: <code or none>` + `Reason: <one line>`.

**Artifacts produced.** `TYPE.md`.

**Why it gates Phase 4.** The question set, the spine, and the validation checks are all type-driven. Misdetection cascades — wrong questions wasted, wrong spine drafted, wrong gates run. The override exists because heuristic detection is fallible; logging the override is the deep-thinker memory-loss defence.

---

## Phase 4 — Socratic Decompose

**Trigger.** `TYPE.md` written.

**The skill does:** asks the type-driven question set from file 03, one question at a time, writing each answer to `ANSWERS.md` immediately. Categories are A–N (file 03 enumerates). Each answer is checked inline against:

- The glossary (file 05 strategy — auto-define if known, ask PM if unknown, surface for consent).
- The contradiction detector (file 06 mechanism — if the new answer contradicts a prior one, the skill flags it and re-asks).

The skill stays in Phase 4 until the gating logic in file 04 says "ready to draft."

**Exit criterion.** Every MUST-ask category answered; every CONDITIONAL-triggered category answered; no unresolved contradictions; glossary has matched all named stages / roles / system strings.

**Artifacts produced.** `ANSWERS.md` (organised by category), `CONTRADICTIONS.md` (resolutions logged), `LOCAL_GLOSSARY.md` (any new terms PM defined this session).

**Why this is the longest phase.** This is the work. Everything else is plumbing. The skill is allowed to ask 50–100 questions if needed (locked principle: quality over speed).

---

## Phase 5 — Draft Into Uniform Spine

**Trigger.** Phase 4 gate satisfied.

**The skill does:**
1. Loads the spine template for the detected type (`templates/spine-WC.md`, `spine-BO.md`, `spine-MX.md`, `spine-RD.md`, `spine-SC.md`, or `spine-fallback.md`).
2. Substitutes content from `ANSWERS.md` + `INTENT.md` + `RELATED.md` into the spine slots. **Substitution only — no generation freedom.** Slot keys map 1:1 to ANSWERS.md keys.
3. Drafts the GitLab-borrowed **release-note line** at the top (one-sentence operator-readable summary) by re-using A1 from ANSWERS.md.
4. Drafts the Shape Up-borrowed **Out of scope** line inside BA Scope.
5. If applicable (only when answers reveal multiple plausible approaches), drafts the Google-borrowed **Alternatives considered** paragraph inside BA Scope.

**Exit criterion.** `DRAFT.md` exists; every spine slot is either filled or marked `N/A: <reason>`.

**Artifacts produced.** `DRAFT.md`.

**Why generation freedom is restricted.** Cross-PM uniformity (locked principle) requires that the same answer set produce the same draft regardless of which PM ran the session. Spines are literal text + slot substitution; the skill is a clerk here, not an author.

---

## Phase 6 — Anti-Repetition + Glossary Sweep

**Trigger.** `DRAFT.md` exists.

**The skill does (file 06 mechanism):**
1. Builds an assertion index across the draft (every claim canonicalised).
2. Pairwise matching → flags repetitions.
3. For each flagged pair: auto-applies DELETE or TRANSFORM where the disposition is unambiguous; asks PM only on the JUSTIFY cases (max 5 prompts).
4. Glossary sweep: every named stage / role / system string is rendered consistently (not "BCM" in one place and "Branch Credit Manager" in another); first mention links to the glossary footer.
5. Re-walk the draft once after dispositions; max 2 dedup iterations total.

**Exit criterion.** `DEDUP.md` records every flagged pair and its disposition; no auto-applied changes pending PM review.

**Artifacts produced.** `DEDUP.md`, updated `DRAFT.md`.

**Why this is its own phase, not folded into Phase 5.** The drafter's job is correctness of structure; the sweeper's job is ruthless compression. Mixing them gives you a drafter that hesitates and a sweeper that hedges. Separate them so each can be aggressive in its lane.

---

## Phase 7 — Validate Against Output Gates

**Trigger.** `DEDUP.md` complete.

**The skill does (file 09 schema gates):**
1. Runs the **universal checks** (U1–U16): intent present, AC lean, system strings quoted, contacts named, etc.
2. Runs the **type-specific checks** (WC1–8 / BO1–7 / MX1–4 / RD1–6 / SC1–6).
3. Runs the **destination-specific checks** (MD1–3 for markdown, JR1–6 for Jira-push).
4. On any check failure → loops back to the specific phase that owns the failed check (e.g., a missing system string loops to Phase 4 G; a contact gap loops to Phase 4 N). Max 3 validation iterations.
5. Three hard-stop failures: empty intent, empty proposal, no detected type. Hard-stop = skill refuses to deliver and re-engages PM.

**Exit criterion.** `VALIDATION.md` says PASS.

**Artifacts produced.** `VALIDATION.md`.

**Why a gate phase is needed.** Without it, the skill optimistically delivers tickets that the downstream release-notes skill then rejects mid-flow. The whole point of the uniform-ticket skill is to spare the release-notes skill that round-trip.

---

## Phase 8 — Deliver

**Trigger.** `VALIDATION.md` = PASS.

**The skill does:**
- **If markdown destination:** writes `DRAFT.md` final to the user-specified path (default `./LAP-<key>.md`); confirms overwrite if file exists.
- **If Jira-push destination:** converts the markdown to Atlassian Document Format (ADF), calls `editJiraIssue` against the reserved key, fetches the issue back, and diffs the round-trip to confirm faithful translation. If the diff fails (e.g., a table got mangled), the skill flags the diff and asks the PM to confirm before declaring delivery.
- Writes `DELIVERY.md` recording destination + key + timestamp.
- Archives the session folder for collision detection (file 08 F8).

**Exit criterion.** `DELIVERY.md` exists; ticket lives in destination.

**Artifacts produced.** `DELIVERY.md`; the ticket itself in markdown or Jira.

**Why diff the round-trip.** ADF conversion is lossy for non-trivial tables and code-style monospace; without the diff the PM discovers the loss when they open Jira. The diff catches it before the skill says "done."

---

## Phase summary table

| # | Phase | Trigger | Exit criterion | Artifacts |
|---|---|---|---|---|
| 0 | Activate & Set Destination | PM invokes skill | SESSION_STATE.md exists, destination + type chosen | SESSION_STATE.md |
| 1 | Auto-Search | SESSION_STATE.md exists | Bounded candidate sets in RELATED.md, glossary loaded | RELATED.md |
| 2 | Verify Context | RELATED.md exists | INTENT.md signed off + RELATED.md tagged | INTENT.md |
| 3 | Classify Type | INTENT.md signed | TYPE.md written with override slot | TYPE.md |
| 4 | Socratic Decompose | TYPE.md written | All MUST + triggered CONDITIONAL answered, no contradictions | ANSWERS.md, CONTRADICTIONS.md, LOCAL_GLOSSARY.md |
| 5 | Draft | Phase 4 gate satisfied | DRAFT.md with every slot filled or N/A | DRAFT.md |
| 6 | Anti-Repetition + Glossary Sweep | DRAFT.md exists | DEDUP.md complete, draft compressed | DEDUP.md, updated DRAFT.md |
| 7 | Validate | DEDUP.md complete | VALIDATION.md = PASS | VALIDATION.md |
| 8 | Deliver | VALIDATION.md = PASS | Ticket in destination, DELIVERY.md written | DELIVERY.md |

## Backwards-loop discipline

Phase N can only loop back to a specific earlier phase via the gate failure protocol — the skill never re-runs an earlier phase wholesale. The gates below force surgical re-entry:

- Phase 7 failure → re-enters the phase that owned the failed check (4 / 5 / 6).
- Phase 4 contradiction → re-asks the contradictory question, never re-runs Phase 4 from scratch.
- Phase 6 dedup → at most 2 iterations; on iteration 3 the residual repetitions are JUSTIFY-flagged and shipped with a footer note.

This bounds the worst-case session length; without it, a stubborn ticket can ping-pong indefinitely.
