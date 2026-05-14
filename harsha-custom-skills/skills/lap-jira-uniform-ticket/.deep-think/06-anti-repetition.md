# 06 — Anti-Repetition Mechanism

## The anti-repetition principle (locked)

Every section in the uniform spine has a unique job. The Intent paragraph says what + why. Current Flow says how it works today. Proposed Solution says how it will work. AC says the done gates. Each appears exactly once. The skill's job is to detect when the PM has restated the same rule in two sections and collapse the restatement.

This file specifies (a) when restatement happens (PM behaviour), (b) how the skill detects it during Phase 4, (c) how the dedup pass works in Phase 6, and (d) what the disposition rules are for each flagged repetition.

---

## How PMs restate (the patterns we're catching)

From the round-1 archive review and the 6 exemplars (which mostly do NOT repeat — that's why they're exemplars), the common restatement patterns are:

1. **Intent → Proposed Solution restate.** PM writes "this ticket adds a new approval stage for cases over 7L" in the Intent paragraph and then writes step 1 of the Proposed Solution as "Add a new approval stage that triggers for cases over 7L." Both correct, both saying the same thing.

2. **Proposed Solution → AC restate.** PM writes "the form must validate income > 0" in step 3 of the proposed solution and then re-lists "AC: form validates income > 0" as bullet 4 of AC. The exemplars catch this — LAP-2039's AC stays focused on the QA-observable outcomes, not a re-list of the proposed flow.

3. **Current Flow → Proposed Solution restate.** PM writes "today the BCM clicks Mark as Complete" in current flow step 3 and writes "after the change, the BCM still clicks Mark as Complete" in proposed solution step 1. The Mark-as-Complete click is unchanged; mentioning it twice adds zero information.

4. **System string echo.** PM quotes `'Approval Pending'` in the Proposed Solution and re-quotes it in QA Scope and re-quotes it in AC. One quotation is necessary (Phase 2 release-notes extraction needs the verbatim string); three quotations is bloat.

5. **Consequence echo across cases.** In a BO ticket, PM writes "case status flips to Renach" in Case 1 outcome, in Case 2 outcome (a different branch), and in the Summary table row for Case 1. Repetition across cases is harder to catch because some cases legitimately share consequences — the disposition rules below handle this.

6. **Out-of-scope echo.** PM writes the Out-of-scope statement in BA Scope and then re-writes a hedge in the Intent paragraph ("note: this does NOT change X"). The Out-of-scope statement is the canonical place for negation; the Intent paragraph stays positive.

---

## Phase 4 inline detection

The skill watches each new answer as it's written to ANSWERS.md. After every answer, it runs a lightweight pairwise check:

- **Canonicalise the new answer.** Strip filler words (the, a, this, that), normalise glossary terms via file 05, lowercase, drop punctuation.
- **Compare against canonical forms of all prior answers.** A "canonical form" is the noun-verb-object skeleton — e.g., "system route case to NCM" is the canonical of "the system should route the case to NCM."
- **Flag near-matches** (cosine similarity > 0.75 on the canonical sentence vectors, OR edit distance < 30% on canonical sentence pairs).

When a flag fires INSIDE Phase 4 (i.e., the PM is repeating across two questions), the skill:

> "What you just said about `<rule>` overlaps with what you already said in answer to question E1.2: `<prior text>`. Are these the same rule, a deliberate emphasis, or two different rules that just sound similar? If same, I'll keep one and reference the other; if different, give me the distinguishing detail."

This catches repetition AT INPUT TIME, before it gets into the draft. Cheaper than catching it post-draft.

---

## Phase 6 dedup pass (the post-draft sweep)

After Phase 5 produces `DRAFT.md`, the skill runs a more thorough pass:

### Step 1 — Build the assertion index

Walk the draft top-to-bottom. For each sentence:

1. Extract the canonical form (noun-verb-object skeleton, with glossary normalisation).
2. Tag with the section it appears in (Intent / Current Flow / Proposed Solution / Matrix / QA / BA / AC / Sources).
3. Tag with the entity it's about (which step, which case, which row, which role).
4. Add to the assertion index.

End state: a flat list of `(canonical, section, entity)` triples covering every claim in the draft.

### Step 2 — Pairwise matching

For every pair of triples with similar canonicals (same threshold as Phase 4), evaluate:

- **Same section + same entity?** → almost certainly a typo or a copy-paste — flag for DELETE.
- **Different sections + same entity + identical canonical?** → flag for disposition (rules below).
- **Different sections + same canonical + different entities?** → not a repetition; structurally similar claims about different things. Skip.
- **Same section + different entities + identical canonical?** → check whether this is a legitimate parallel (Case 1 and Case 2 both flip status to Renach because they're meant to be parallel) or a collapse opportunity. Disposition rule below.

### Step 3 — Disposition rules

For each flagged pair, the skill picks one of four dispositions and announces it (auto-applies DELETE / TRANSFORM, asks PM on JUSTIFY):

| Pair pattern | Disposition | Action | PM consulted? |
|---|---|---|---|
| Intent ↔ Proposed Solution step 1 | **DELETE Intent restatement** | Keep Proposed Solution step 1; tighten Intent to its why-only role | No (auto) |
| Proposed Solution ↔ AC | **DELETE AC bullet** | Keep Proposed Solution; AC must be observable outcome, not the rule itself | No (auto) |
| Current Flow ↔ Proposed Solution where the action is unchanged | **DELETE Proposed Solution mention** | Current flow step describes today; Proposed Solution describes what changes — unchanged actions don't appear in Proposed | No (auto) |
| System string echo (≥3 occurrences) | **TRANSFORM to first-quoted-then-referenced** | First mention quotes verbatim; subsequent mentions use the quoted name without re-quoting | No (auto) |
| Consequence echo across BO cases | **JUSTIFY** | Ask PM whether the parallel is intentional (parallel cases by design) or accidental | Yes |
| Out-of-scope echo in Intent | **DELETE Intent hedge** | Keep Out-of-scope in BA Scope; strip Intent | No (auto) |
| Sentence appears verbatim in 2+ sections, canonical and entity match exactly | **DELETE one** | Skill picks the section where it has the strongest job-fit (e.g., consequence stays in Proposed Solution, not in QA) | No (auto) |
| Genuine ambiguity (skill can't decide) | **JUSTIFY** | Ask PM | Yes |
| Sentence is the only place a critical detail appears, but appears stretched across two sentences | **TRANSFORM to merge** | Combine into one sentence | No (auto) |
| Skill flagged it but PM disagrees on JUSTIFY | **SPLIT** (treat as legitimately distinct) | Keep both, log for review | Yes (already consulted) |

### Step 4 — Auto-apply and ask

The skill auto-applies all DELETE and TRANSFORM dispositions. For JUSTIFY (and only JUSTIFY) it batches the questions and asks the PM up to 5 prompts:

> "Found <N> potential repetitions in the draft. <M> I auto-cleaned. <K> need your call. Here they are: ..."

Cap at 5 PM prompts per dedup iteration to prevent prompt fatigue. If more than 5 JUSTIFY items, the skill asks the top 5 by similarity score and ships the rest with a footer note "Deferred dedup: <list> — PM to review post-delivery."

### Step 5 — Re-walk

After dispositions, re-walk the draft once. New repetitions that emerged from the dispositions (rare but possible — e.g., a TRANSFORM merge that brought together two paragraphs and revealed a tertiary echo) are caught and dispositioned the same way.

**Hard cap: 2 dedup iterations.** On iteration 3, residual flagged pairs are JUSTIFY'd and shipped with a footer note. This bounds the worst-case session and prevents the dedup pass from being a tar pit.

---

## Why LAP-2242's 10-rule list never repeats — and how the skill enforces that

LAP-2242 has 10 numbered rules in its Logic section. None repeat. The reason:

- Each rule is a different conditional: rule 1 is "identify slab," rule 2 is "route by slab," rule 3 is "fallback when designated unavailable," rule 4 is "specific fallback for 0–5L," rule 5 is "specific fallback for 10L+," rule 6 is "log routing decision," rule 7 is "configurable," rule 8 is "escalation if both unavailable," rule 9 is "state-wise SCH variant," rule 10 is "production mapping reference."
- The canonicalised forms are: `identify_slab`, `route_by_slab`, `fallback_unavailable`, `fallback_5L`, `fallback_10L`, `log_decision`, `configurable`, `escalate_both_unavailable`, `state_variant`, `prod_mapping`. All distinct.

The skill enforces this by running the assertion index ON the Logic section itself: every rule's canonical form must be unique within the Logic section. If two rules canonicalise to the same skeleton, one is a restatement and gets DELETE'd or the rules need to be merged into a single fuller rule.

---

## What the skill does NOT try to dedup

- **Pure structural repetition** (every Case section has a "What the operator sees" header) — that's spine, not content. Headers stay.
- **Glossary footer entries** — by design, the same term may appear in multiple ticket sections; the footer entry is the single canonical definition.
- **Quotations in Sources** — attachments / parent epic / bug fan-out lists may legitimately reference the same key in two roles (e.g., a ticket is both a parent and a sibling of another). These are tagged role-specific, not duplicates.
- **Bidirectional toggle behaviour** in SC tickets — "Yes → No" and "No → Yes" sections will look symmetric; that's required, not a repetition.

---

## Disposition log

Every dedup decision is logged to `DEDUP.md`:

```
## DEDUP iteration 1

| # | Section A | Section B | Canonical | Disposition | Auto? |
|---|---|---|---|---|---|
| 1 | Intent | Proposed Solution step 1 | introduce_approval_stage_above_7L | DELETE Intent restatement | yes |
| 2 | Proposed Solution step 3 | AC bullet 4 | form_validate_income_gt_0 | DELETE AC bullet | yes |
| 3 | Case 1 outcome | Case 3 outcome | flip_status_to_renach | JUSTIFY (asked PM) | no, PM said parallel by design |
```

This log is part of the deliverable — it's not just internal accounting. The PM and (eventually) the team can audit how the skill enforced uniformity, which is itself a training mechanism.
