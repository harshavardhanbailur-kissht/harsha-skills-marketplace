# Smoke test: SC type from a LAP-2039-style PM input

**Purpose:** Prove the skill can take a Simple Change PM intent expressed in plain English and produce a uniform-pattern ticket whose body, when fed to `kissht-field-release-notes`, produces an extractable Pattern A (Relook) operator release note.

**What this test covers:** Phase 0 → 8 single-feature pipeline. Type detection (SC). MUST-question coverage. Output gate U1-U10 + SC1-SC3. Downstream extractability into Pattern A release note.

**What this test does NOT cover:** Multi-ticket bundles. Push-to-Jira (deferred to v1.1). Atlassian MCP integration (assumed connected; fallback path is covered separately in `tests/no-atlassian-mcp-fallback.md` — TBD).

---

## Input — what the PM types into the skill

> "I need to file a LAP ticket. The Income Considered field for the co-applicant currently sits inside the Edit form of an already completed Credit PD activity, defaults to Yes, and to set it to No the BCM has to fill every income field with junk values, click Mark as Complete, then re-open the activity in Edit mode and flip the toggle. Six steps for one toggle. Move the field to the top of the Mark as Complete form so the BCM can set No in one step."

## Expected skill behaviour — Phase by Phase

### Phase 0 — Activate & Set Destination
- Skill greets, confirms scope ("Quick orientation — is this a new feature, a tweak to an existing feature, a config / dropdown change, or something else?")
- Expected PM answer: "Tweak to an existing form."
- Skill seeds type detection toward SC.

### Phase 1 — Auto-Search (if Atlassian MCP connected)
- Skill runs JQL on LAP project for "Income Considered Credit PD" or similar.
- Expected: surfaces LAP-2039 itself (since it's the canonical exemplar for this exact change) and possibly child bugs LAP-2322, LAP-2327, LAP-2328, LAP-2332.
- If Atlassian MCP NOT connected: skill skips Phase 1, asks PM at Phase 2 for any related ticket keys.

### Phase 2 — Verify Context
- Skill shows top candidates. PM marks LAP-2039 as DUPLICATE (since the test scenario is filing what already exists).
- **Skill must hard-flag the duplicate** at Phase 8: "I think you're re-filing LAP-2039. Continue anyway, or stop?"
- For this test, PM continues so we can verify the full draft pipeline.

### Phase 3 — Classify Ticket Type
- Skill asks T1 (NEW stage / approval / SLA / mandatory action?). PM answers NO.
- Skill asks T2 (one operator action with ≥2 if-branches?). PM answers NO ("just moving a field").
- Skill asks T3 (single form / field / toggle change?). PM answers YES ("one toggle move").
- **Expected classification: SC.**
- Skill announces: "Classified as SC — single field move killing a workaround. The questions ahead are tailored for SC; we'll skip the ones that don't apply."

### Phase 4 — Socratic Decompose (SC asks ~13 MUST questions)
PM answers must include:
- A1 one-line: "Income Considered moves to the Mark as Complete form so BCM can set No in one step instead of seven."
- A2 business reason: BCM wastes time filling junk values.
- B1 current flow: 6 numbered steps (the workaround).
- C1 stage: Credit PD (multi-stage activity).
- C2 form: Credit PD `'Mark as Complete'` form; also Edit form post-completion.
- C3 other systems: NO (LOS only).
- D1 roles: BCM (primary), CCPA + BCM downstream observers via NIC tab.
- E1-SC: before-state (toggle inside Edit form, defaulted Yes) → after-state (toggle at top of Mark as Complete form).
- E2 system consequence: each step shows what the system does (form blocks save, fields disable, NIC tab updates).
- G1 system strings (verbatim): `'Income Considered'`, `'Mark as Complete'`, `'Yes'`, `'No'`, `'NIC'` (Non Income Considered), `'Applicant Details'`.
- J1 QA scope: 9 numbered scenarios (verify both directions, NIC tab refresh, primary-vs-co-applicant scope).
- K1 out of scope: any change to the Yes-path behaviour is OUT.
- K2 BA assumptions: (a) Primary applicant scope — lock to Yes; (b) Previously-filled income data on Yes→No — keep for audit, disabled on screen.
- L1 lean AC: 4 bullets organised by area (Form behaviour / Toggle bidirectionality / Downstream visibility / Regression guard).
- M1 attachments: NONE.
- N1 reporter / assignee: harshavardhan.bailur / Mohini Nikale.

### Phase 5 — Draft Into Uniform Spine
- Skill renders into `templates/sc-simple-change.md` shape.
- Expected sections present: Intent, Problem, Current flow, Proposed solution (with bidirectional toggle behaviour for Yes↔No), QA Scope, Open Considerations for BA, Out of scope (sub-section), Acceptance Criteria, footer with System strings + Glossary + Reporter/Assignee/etc.

### Phase 6 — Anti-Repetition + Glossary Sweep
- Skill auto-populates glossary footer with: BCM, CCPA, Credit PD, NIC, Mark as Complete form, Income Considered, Applicant Details, Edit form, Yes/No.
- No ghost terms expected (all terms are in `lap-glossary.md`).
- No repetition expected (clean SC structure).

### Phase 7 — Validate Against Output Gates
- All 10 universal gates (U1-U10) PASS.
- SC1 (Current Flow shows workaround): PASS.
- SC2 (bidirectional toggle behaviour both ways): PASS.
- SC3 (regression-guard AC bullet present): PASS.

### Phase 8 — Deliver (markdown only in v1.0.1)
- Skill outputs the H1 title `Move Income Considered from Yes / No selection to the Credit PD Mark as Complete form` separately for the Jira "Summary" field.
- Skill outputs the full body as fenced markdown for the Jira "Description" field.
- PM closes the loop by posting the resulting LAP-XXXX key back.

---

## Verification — feed the output into `kissht-field-release-notes`

After the skill produces the markdown, invoke `kissht-field-release-notes` with that ticket as input.

**Expected release-notes pattern:** **Pattern A (Relook)** — operator-facing workflow change.

**Expected extractability checklist:**
- [ ] Release-note line at top of ticket → lifted verbatim into release-note headline
- [ ] Named primary actor (BCM) → role section "What this means for BCM"
- [ ] Numbered Current flow → Old flow arrow diagram
- [ ] Numbered Proposed solution → New flow arrow diagram
- [ ] System strings in single quotes → quoted verbatim in release note
- [ ] BCPA / NIC tab references → role section "What this means for BCPA / CCPA reading downstream"
- [ ] Reporter (harshavardhan.bailur) + Assignee (Mohini Nikale) → Contacts block
- [ ] Open Considerations (primary applicant scope locked to Yes) → Note for BA in operator section
- [ ] Out of scope (Yes-path unchanged) → Disclaimer in role section ("the existing Yes flow is unchanged")

**Pass criteria:** All 9 boxes ticked AND the resulting release note reads cleanly to a BCM at 9am without re-interviewing the PM.

---

## Test status

- [ ] Run manually by skill author after first marketplace install.
- [ ] Re-run after any Phase-4 question taxonomy change in `SKILL.md` §5.
- [ ] Re-run after any `kissht-field-release-notes` upgrade that changes Pattern A extraction.
- [ ] Pass / fail logged in `tests/_results.md` (TBD).
