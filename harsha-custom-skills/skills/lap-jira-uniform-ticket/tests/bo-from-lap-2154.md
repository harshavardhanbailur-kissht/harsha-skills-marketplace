# Smoke test: BO type from a LAP-2154-style PM input

**Purpose:** Prove the skill can take a Branching Outcome (one operator action, multiple backend-state branches) PM intent and produce a uniform-pattern ticket whose body, when fed to `kissht-field-release-notes`, produces an extractable Pattern B (Renach) operator release note.

**What this test covers:** BO type detection. ONE-trigger-N-branches discipline. See/Do/Verify-if-silent triplet per Case. Auto-comm flagging. Non-overridable backend rule call-out. Edge-case section for the buffer policy. Downstream extractability into Pattern B (Renach).

**What this test does NOT cover:** Multi-Case BO with ≥4 branches (covered in v1.1 multi-Case BO test, TBD).

---

## Input — what the PM types into the skill

> "Need a LAP ticket for LSQ Renach handling. On the Post Sanction stage, Repayment Details subtab, when the user clicks Yes on the 'Initiate E-Mandate Registration?' dropdown of the Repayment & Disbursal Details Capture v5 form, three things can happen depending on whether a mandate is already approved: (1) if no mandate exists or first-time, show a fresh link; (2) if mandate exists AND sanction loan amount ≤ mandate amount AND last EMI date + 5 years ≤ mandate expiry, send a success callback without link AND push the latest NACH reference to LMS; (3) if mandate exists but conditions fail, show a fresh link. Conditions are backend-only, not editable in LSQ. Buffer policy: initial mandate is tenure + 5y; revised mandate uses tenure + 4y; new mandate generated via link goes back to 5y."

## Expected skill behaviour — Phase by Phase

### Phase 0 — Activate & Set Destination
- PM answers "tweak to an existing flow with branching outcomes."
- Skill seeds toward BO.

### Phase 1 — Auto-Search (if Atlassian MCP connected)
- JQL on "LSQ Renach" surfaces LAP-2154 (canonical) + child bugs LAP-2068, LAP-2165, LAP-2175, LAP-2176, LAP-2211.

### Phase 2 — Verify Context
- PM tags LAP-2154 as DUPLICATE (test scenario).

### Phase 3 — Classify Ticket Type
- T1 (new stage / approval / SLA?): NO.
- T2 (one operator action triggers ≥2 if-branches?): YES — three branches off the dropdown click.
- **Expected classification: BO.**
- Skill confirms: "Classified as BO — branching outcome with three backend-state branches and a buffer-policy edge case."

### Phase 4 — Socratic Decompose (BO asks ~15 MUST questions)
PM answers:
- A1 one-line: "When 'Initiate E-Mandate Registration?' is set to Yes on Repayment Details, the system either shows a fresh link or skips to success based on existing mandate validity."
- A2 business reason: today, the system always sends a fresh link even when a valid mandate exists — wastes operator time and customer friction.
- C1 stage: `Post Sanction`.
- C2 forms: Repayment Details subtab → `'Repayment & Disbursal Details Capture - v5'` form (note: bumped to v6 per LAP-2176 — confirm latest).
- C3 other systems: LMS (push-to-LMS contract for `enach_reference_number`).
- D1 roles: BCPA (operator on Post Sanction).
- E1-BO: ONE trigger action = clicking Yes on `'Initiate E-Mandate Registration?'`. THREE branches:
   - Case 1: mandate not approved or first-time → link shown
   - Case 2: mandate approved AND conditions met → success callback (no link) + NACH ref pushed to LMS
   - Case 3: mandate approved AND conditions not met → link shown
- E2 per-case system consequence: each Case names what operator sees, what system silently does (push to LMS for Case 2), how operator verifies (Case 2: check NACH ref in LMS push body).
- G1 system strings (verbatim): `'Initiate E-Mandate Registration?'`, `'Repayment & Disbursal Details Capture - v5'`, `'Post sanction'`, `'Repayment Details'`, `enach_status: Success`, `mandate_amount`, `mandate_expiry_date`, `enach_reference_number`.
- H1 auto-comm: NONE flagged in source ticket — skill records "None" for each Case.
- H2 silent action: YES — Case 2 silently pushes NACH reference to LMS without operator click. Skill MUST flag this for the BCPA-facing release-note section ("you don't have to verify by checking fields — the system pushes silently and the case moves forward on its own").
- I1 time-window edge case: mandate buffer policy — initial mandate is tenure + 5y, revised mandate uses 4y buffer, new mandate via link uses 5y buffer.
- Non-overridable rule (mandatory for BO): "Conditions are developed in the backend, not in the LSQ" → skill MUST surface as "you cannot change this from the panel" in the BCPA-facing release-note section.
- J1 QA scope: 5 numbered scenarios — verify trigger fires correctly, verify each Case end-to-end, verify NACH ref in LMS push body, verify buffer-policy edge case at revised-mandate boundary.
- K1 out of scope: any change to the dropdown UI itself (the dropdown stays as-is — only the post-click behaviour changes).
- K2 BA assumptions: (a) what to do if push-to-LMS fails after success callback in Case 2 — propose: hold case in queue, alert ops; (b) what counts as "first-time user" in Case 1 — propose: any opportunity that has zero prior mandate records.
- L1 lean AC: 4 bullets (Trigger detection / Case 1 link generation / Case 2 silent push to LMS / Buffer-policy edge case).
- M1 attachments: ENACH callback payload sample (the JSON schema from the source ticket — preserved as a code block per the LAP-2154 voice exception).
- N1 reporter / assignee: Vishaw Kashyap / Kunal Tan.

### Phase 5 — Draft Into Uniform Spine
- Skill renders into `templates/bo-branching-outcome.md`.
- Step 2 sub-section names the ONE operator action verbatim.
- Three Case sub-sections, each with See / Do / Verify / Auto-comm / Consequence triplet (Case 2 also names the non-overridable backend rule).
- Edge case section (buffer policy) with 4-year vs 5-year explanation.
- Summary table mandatory (3 cases ≥3): one row per Case.

### Phase 6 — Anti-Repetition + Glossary Sweep
- Glossary auto-populates: BCPA, Renach, E-Mandate / eNACH, NACH, push-to-LMS, mandate buffer, `enach_reference_number`, mandate_amount, mandate_expiry_date.
- Mandate buffer is in `lap-glossary.md` §Concepts (definition matches LAP-2154 verbatim).

### Phase 7 — Validate Against Output Gates
- All 10 universal gates (U1-U10): PASS.
- BO1 (ONE trigger action explicitly named): PASS.
- BO2 (each Case has See / Do / Verify-if-silent triplet): PASS.
- BO3 (auto-comms flagged with manual-backup recommendation): N/A (no auto-comms in this ticket; skill records "None" per Case).
- BO4 (non-overridable rules explicitly named): PASS — "Conditions are developed in the backend" surfaced.

### Phase 8 — Deliver (markdown only)
- Title: `LSQ Renach Handling`
- Body: full markdown with Case-by-Case See/Do/Verify + buffer edge case + Summary table + footer.

---

## Verification — feed into `kissht-field-release-notes`

**Expected pattern:** **Pattern B (Renach)** — branching outcome with cases.

**Expected extractability checklist:**
- [ ] Release-note line → lifted verbatim
- [ ] Mental-model summary (NOT a flow diagram) → 2-4 sentences in release note opening
- [ ] Stage / Tab / Subtab / Form locator + ONE click → release note "What you do" section
- [ ] Each Case → release note "Case 1 / Case 2 / Case 3" sub-section with See / Do / Verify-if-silent
- [ ] System strings in single quotes → quoted verbatim
- [ ] Non-overridable rule → "you cannot change this from the panel" plain-English call-out
- [ ] Silent system action (push-to-LMS) → "you don't have to verify — the case moves forward on its own" plain-English call-out
- [ ] Buffer policy edge case → release note appendix or footer note
- [ ] Reporter / Assignee → Contacts block
- [ ] BCPA-facing voice when single-role pager is requested (Voice B-strict per `kissht-field-release-notes` §3)

**Pass criteria:** All 10 boxes ticked AND the release note reads cleanly to a BCPA at 9am — including the trust-the-system framing for the silent push-to-LMS.

---

## Test status

- [ ] Run manually after first marketplace install.
- [ ] Re-run after any BO-type question change in `SKILL.md` §5.
- [ ] Re-run after any `kissht-field-release-notes` upgrade that changes Pattern B (Renach) extraction or Voice B-strict spec.
