# Smoke test: RD type from a LAP-2242-style PM input

**Purpose:** Prove the skill can take a Reference Data (matrix / slab) PM intent and produce a uniform-pattern ticket whose body, when fed to `kissht-field-release-notes`, produces an extractable Pattern A (matrix-only variant) operator release note.

**What this test covers:** RD type detection. Matrix-table mandatory section. Conditional omission of §15a Out of scope when ticket is purely additive AND every assumption is closed. Role Definitions footer. Source-of-truth sheet link. Downstream extractability.

**What this test does NOT cover:** State-wise variant deep-dive (covered in v1.1 multi-state RD test, TBD).

---

## Input — what the PM types into the skill

> "Need a LAP ticket for the IPA and FA approval routing matrix. The system should route IPA decisions to CCM for 0-7L, SCH for 7-10L+, and FA decisions to CCM (0-7L) / SCH (7-10L) / NCM (10L+). When the designated approver role is unavailable, fall back to the default approver per slab. Need state-wise SCH variant mapping (SCH 1 / SCH 2). Configurable through a config screen without code deploy. Audit trail logs primary vs fallback routing per case."

## Expected skill behaviour — Phase by Phase

### Phase 0 — Activate & Set Destination
- PM answers "config / matrix change."
- Skill seeds toward RD.

### Phase 1 — Auto-Search (if Atlassian MCP connected)
- JQL on "IPA FA approval matrix" surfaces LAP-2242 (canonical exemplar) and bugs LAP-2287, LAP-2298, LAP-2305, LAP-2330.

### Phase 2 — Verify Context
- PM tags LAP-2242 as DUPLICATE (test scenario is re-filing the canonical example).
- For test purposes, PM continues so we can verify the full pipeline.

### Phase 3 — Classify Ticket Type
- T1 (new stage?): NO.
- T2 (one action, multiple branches?): NO ("the matrix routes per slab — that's policy, not branching at one operator action").
- T3 (single form change?): NO ("matrix is multi-row").
- Skill asks the RD-disambiguating sub-question: "Is this a dropdown / matrix / config / slab change with NO flow change?" PM: YES.
- **Expected classification: RD.**

### Phase 4 — Socratic Decompose (RD asks ~9 MUST questions — leanest type)
PM answers:
- A1 one-line: "IPA and FA decisions route by loan-amount slab with role-based fallback."
- A2 business reason: today routing is hard-coded; ops can't update slabs without dev cycle.
- C1 stages: `In-Principle Approval Pending` and `Final Sanction Approval Pending` (both are LOS Open-status stages per Confluence pageId 1088716805).
- C2 forms: routing is system-side; no specific form (the operator just submits Credit PD or final recommendation).
- C3 other systems: NO (all in LSQ + LOS).
- D1 roles: CCM, SCH, NCM (all already in `lap-roles.md`).
- E1-RD: 3-row matrix with columns = Slab × IPA Approver × FA Approver × Default (Fallback).
- E2 + F1 (configurability): business / ops can edit slab thresholds, approver roles, and fallbacks via config screen without code deploy.
- G1 system strings: panel UI labels for stage names (verbatim from `lap-stages.md`).
- J1 QA scope: simulate approver unavailability by inactivating the user; verify fallback routing; verify state-wise SCH 1 / SCH 2 variants.
- K1 out of scope: routing for cases above 10L stays at NCM (no new tier introduced).
- K2 BA assumptions: skill detects PM has not flagged any open assumption — RD CONDITIONAL kicks in.
- L1 lean AC: 4 bullets (Matrix accuracy / Per-system parity / Fallback behaviour / Configurability).
- M1 attachments: source-of-truth sheet link (LSQ mapping spreadsheet).
- N1 reporter / assignee.

### Phase 5 — Draft Into Uniform Spine
- Skill renders into `templates/rd-reference-data.md`.
- Approval matrix section MANDATORY — populated with 3-row table.
- Per-system breakdown section: documents touchpoints across LSQ + LOS + LMS.
- Logic section: 8 numbered rules including fallback logic, configurability, audit trail, state-wise variants.
- §15 Open Considerations + §15a Out of scope: **omitted via RD conditional rule** because every assumption is closed AND change is purely additive (per LAP-2052 conditional precedent in PATTERN.md §15 / §15a).
- Skill MUST insert the conditional-omission justification line in §1 Intent: "no open assumptions — the attached sheet / matrix is canonical."
- Role Definitions section MANDATORY: CCM / SCH / NCM expansions.
- Source-of-truth footer MANDATORY: sheet link.

### Phase 6 — Anti-Repetition + Glossary Sweep
- Glossary auto-populates: CCM, SCH, NCM, IPA, FA, In-Principle Approval Pending, Final Sanction Approval Pending, fallback logic, state-wise SCH variant.
- No ghost terms.

### Phase 7 — Validate Against Output Gates
- U1-U4, U8, U9, U10: PASS.
- U5 (lean AC): PASS — 4 area-organised bullets.
- U6 (Out of scope): RD CONDITIONAL EXCEPTION applied — PASS with §1 justification line.
- U7 (BA Open Considerations): RD CONDITIONAL EXCEPTION applied — PASS with §1 justification line.
- RD1 (matrix table present): PASS.
- RD2 (source-of-truth sheet linked): PASS.
- RD3 (configurability statement present): PASS.

### Phase 8 — Deliver (markdown only)
- Title: `LAP <> LSQ : IPA and FA approval matrix`
- Body: full markdown with matrix + logic + per-system + role definitions.

---

## Verification — feed into `kissht-field-release-notes`

**Expected pattern:** **Pattern A (matrix-only variant)** — operator-facing reference-data change.

**Expected extractability checklist:**
- [ ] Release-note line → lifted verbatim
- [ ] Approval matrix table → reproduced or quoted in release note
- [ ] Logic numbered rules → bullet list of rules in operator section
- [ ] System strings (stage names) → quoted verbatim
- [ ] Affected roles (CCM / SCH / NCM) → one role section each in "What this means for"
- [ ] Audit trail rule → operator-facing verification note ("you can see whether your case took the primary or fallback route in the audit log")
- [ ] State-wise SCH variant → state-specific notice in role section
- [ ] Configurability rule → ops-facing note ("ops can update the matrix from the config screen without a release")
- [ ] No fabricated percentages / fees / RBI references
- [ ] Reporter / Assignee → Contacts block

**Pass criteria:** All 10 boxes ticked AND the release note reads cleanly to a CCM at 9am.

---

## Test status

- [ ] Run manually after first marketplace install.
- [ ] Re-run after any RD-type question change in `SKILL.md` §5.
- [ ] Re-run after any `kissht-field-release-notes` upgrade that changes Pattern A matrix-variant extraction.
