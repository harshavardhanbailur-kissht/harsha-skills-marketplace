# 04 — Anti-Repetition Mechanism

## Why this is its own phase, not a writing-time discipline

LLMs repeat. Every coding LLM eval shows it; every PM who has used Jira AI tools has seen it. The reason is structural: when a model is generating section §3 and section §AC in one pass, both sections "feel like" they should restate the rule. The model has no working memory of "I already said this in §3" because both are being generated in the same forward sweep.

The fix is to **separate drafting (Phase 5) from editing (Phase 6)**. Drafting is generative; editing is comparative. The cognitive modes are different, and cramming both into one phase produces neither well.

## The dedup pass — concrete design

### Step 1: build the assertion index

After Phase 5 produces `DRAFT.md`, the skill walks the draft and extracts every **assertion**. An assertion is a unit of factual content — a rule, a behaviour, a constraint, a UI string, a stage transition.

For each assertion, capture:
- **Text** (the assertion as written)
- **Location** (which section: Intent / Current flow / Proposed §N / Matrix row / QA bullet J_n / BA bullet K_n / AC bullet L_n)
- **Canonical form** (a normalised version: lowercased, articles dropped, numbers turned to digits — used for matching)

Write to `ASSERTIONS.md` as a numbered list.

### Step 2: pairwise match

The skill walks the assertion list and, for each pair (A_i, A_j) where i < j, checks:

- **Exact match** on canonical form → flagged as `EXACT`
- **High-overlap match** (≥70% of content words shared, both >5 words) → flagged as `NEAR`
- **Same-rule different-frame match** (same UI string + same numeric threshold + same role, even if phrased differently) → flagged as `SEMANTIC`

Each flagged pair is written to `DEDUP.md` with both assertion texts, both locations, and the match category.

### Step 3: classify each repetition

Each flagged pair gets one of these dispositions:

| Disposition | When | Action |
|---|---|---|
| **DELETE_LATER** | Same assertion appears twice; the second occurrence adds no new information | Delete the later occurrence; keep the earlier one (which is closer to the contextual frame) |
| **DELETE_EARLIER** | Same assertion appears twice; the later occurrence is in the canonical home (e.g., Proposed §3) and the earlier one was a forward-reference | Delete the earlier (forward-reference); keep the canonical home |
| **TRANSFORM** | The same rule appears in §3 (as a rule) and in §AC (as a verifiable assertion). This is allowed but the AC version must be re-phrased to focus on **verification**, not restate the rule. E.g., §3 says "If Yes, all fields are mandatory." §AC says "Save is blocked when any mandatory field is empty on the Yes path." | Re-write the AC version to verification-frame |
| **JUSTIFY** | The PM explicitly insists both occurrences are needed (e.g., the Summary table at the end of LAP-2046 restates the §3 + §4 rules — but the table format adds a different cognitive value) | Both retained; justification logged in `DEDUP.md` |
| **SPLIT** | What looked like a repetition is actually two distinct assertions that happen to share vocabulary. Mark as not-a-repeat. | No action |

### Step 4: present and apply

The skill presents `DEDUP.md` to the PM as a summary:

> Found 7 potential repetitions. Disposition recommended:
> - 3 DELETE_LATER (auto-applied, see file)
> - 2 TRANSFORM (rewritten, see file)
> - 1 JUSTIFY (kept, awaiting your justification)
> - 1 needs your call: §3 step 4 vs §AC bullet 2 — same rule, both useful?

DELETE and TRANSFORM dispositions are applied automatically. JUSTIFY and the explicit-call cases are presented to the PM with a single yes/no per pair. No more than 5 explicit-call prompts per dedup pass — if there are more, the skill batches them.

### Step 5: re-walk

After applying dispositions, the skill re-walks the modified draft and re-runs the assertion index. If any new EXACT or NEAR match appears (rare, but possible after a TRANSFORM), the dedup pass loops once. Maximum 2 dedup passes — beyond that, the residual repetitions are logged as known issues in `DEDUP.md` and the PM is told.

## When to NOT dedup (the JUSTIFY cases)

Three patterns where intentional restatement adds value and the skill must NOT collapse them:

1. **Matrix → narrative** (LAP-2046, LAP-2242). The Summary table at the end and the narrative §3 cover the same rules but in different cognitive modes. The table is for scanning; the narrative is for reading. Both retained.
2. **Rule → verification** (universal). §3 says the rule from a system-design perspective. §AC says the same rule from a test-perspective. Both retained — but the AC version is rewritten to verification-frame in the TRANSFORM step, so it doesn't feel like a copy.
3. **Universal preconditions** (LAP-1812 pattern). Preconditions block ("Loan case stage is Post Sanction; Loan is sanctioned successfully") may overlap with Functional Flow step 1. Both retained because the Preconditions block exists as a quick-check for the reader before they invest in reading the Flow.

## Inline checks during drafting (Phase 5) — not a substitute for the dedup pass

The drafter has one inline check: as it writes each new sentence, it scans the draft-so-far for the **exact same UI string in single-quotes**. If the same `'string'` appears more than twice, the drafter flags it ("`'Mark as Complete'` appears 4 times — is that intentional?") to the PM in real time.

This catches the most egregious repetition (the same panel label dropped 8 times in a 600-word ticket) before the dedup pass even runs. It's a cheap pre-filter.

## What the user-facing prompt looks like

The skill is explicit about the dedup phase. Sample interaction:

> **Skill**: Phase 6 — anti-repetition pass. I found 4 potential repetitions in your draft. I'm going to apply 2 of them automatically and ask you about the other 2.
>
> **PM**: ok
>
> **Skill**: Auto-applied:
> - "Income Considered defaults to Yes" appeared in §1 (Problem) and §3.1 (Proposed). Kept §1, deleted §3.1 — §3 starts with the move action so the default state belongs in the Problem framing.
> - "Yes-path validation runs exactly like a fresh Mark as Complete with Yes" appeared in §3.4 (Edit form) and §AC bullet 2. Rewrote AC bullet 2 to: "After No → Yes on Edit form, all income fields are mandatory and Save is blocked until filled."
>
> Asking you about:
> - §3.4 step "switching Yes to No disables every income field" and §AC bullet 4 "Disabled fields save as blank." Same rule from two angles. Keep both, or merge?
>
> **PM**: keep both
>
> **Skill**: Logged. Justification: "AC adds the save-as-blank consequence which §3 implies but doesn't state." Moving to Phase 7.

The PM sees the skill working. They don't see a dedup-and-merge that quietly destroys their content.

## Failure mode: the skill mis-classifies a repetition

If the skill marks something as DELETE_LATER and the PM disagrees, the PM can revert in the same turn ("no, keep that bullet") and the skill restores it + logs the disagreement to `DEDUP.md` so the next session learns. After 3 disagreements in one session, the skill switches to **conservative mode** — every dispoition is asked, none auto-applied, for the rest of this draft.

## Why not use a fancy embedding-similarity model

Tempting, but no:

1. **Determinism**: the canonical-form string match is deterministic; an embedding model is not. Determinism matters for cross-PM uniformity (same ticket → same dedup → same result).
2. **Explicability**: when the PM asks "why did you flag these as duplicates?", the skill can show the canonical forms side by side. With an embedding score, the skill can only say "they were 0.87 similar."
3. **Cost**: an embedding call per pair scales O(N²). For a 30-assertion draft, that's 435 pairs. The string-match approach handles them in milliseconds.

The string match catches EXACT and NEAR. SEMANTIC requires a small heuristic check (UI string + numeric threshold + role triple) — not embeddings. This covers the failure modes that matter without introducing non-determinism.

## What the dedup phase explicitly does NOT do

- It does NOT shorten the ticket. Length is governed by Phase 7 word-count checks per type, not by dedup.
- It does NOT re-organise sections. Re-organisation is a re-draft, not a dedup.
- It does NOT touch the AC bullet count cap. That's a Phase 7 check.
- It does NOT delete vocabulary repetition. The same UI string appearing in §3 and §AC is fine if it's referring to different actions on that string.
