# Release Note: BCM Co-applicant Income-Considered Flip

<!--
  Test output — produced by kissht-field-release-notes skill on 2026-05-02.
  Source ticket: LAP-979 (status LIVE, label qa_done).
  Reporter: Vishaw Kashyap. Assignee: Neeraj Shah.
  Confluence sources: 1088716805 (LAP LOS canonical) for stage names; 1089568947 (CPA Verified | BCM)
  for stage owner context; lap-glossary.md for Finbox flag terminology.
  Verified against §6 verification gate.
  Word count: 583.
-->

## The new flow

BCM opens case at `CPA Verified`  →  Applicant Details tab  →  Edit co-applicant form  →  flips `'Is Income Considered?'` from No to Yes  →  Finbox + age + bureau checks  →  save  →  Credit PD task auto-created for co-applicant  →  income documents collected  →  Submit In-Principle proceeds

Stages where this is visible:

- `CPA Verified`  (with BCM — only stage where the Edit co-applicant form is accessible)
- `Post Sanction`, `Branch Operations`, `Central Operations`  (with BCPA / BOM / COM — form is LOCKED at these stages, no IC flip allowed)

Field & status values:

- `'Is Income Considered?'`: Yes / No. Editable only when `can_become_income_considered` (Finbox) is Yes.
- Finbox flags: `can_become_income_considered`, `can_become_applicant`, `can_become_co-applicant`, `is_waiver_eligible`.
- Programme restriction: Saral 2.0 and Normal-with-waiver cases (where `is_waiver_eligible` = Yes) — form is restricted entirely.

## Key rules

- The Edit co-applicant form is accessible at `CPA Verified` only. After Final Sanction Approval the form is locked across `Post Sanction`, `Branch Operations`, and `Central Operations`. IC marking becomes final at that point.
- The form is restricted on Saral 2.0 and Normal-with-waiver programmes (driven by the `is_waiver_eligible` Finbox flag). On these, BCMs cannot flip IC on the co-applicant — the case has to go through the standard waiver workflow.
- To flip `'Is Income Considered?'` from No to Yes, all of the following must hold: (1) Finbox `can_become_income_considered` = Yes — if No, the field is uneditable and shows _"This Co-applicant cannot be marked as income considered as derogs are failed."_ ; (2) Age between 21 and 63 — otherwise: _"Co-applicant's Age is X while Age should be between 21 to 63."_ ; (3) PAN on file (already enforced); (4) Bureau pull not expired.
- If both Finbox flags `can_become_applicant` and `can_become_co-applicant` are Yes, swapping is enabled between the primary applicant and the IC co-applicant. Use it when the wrong applicant is on the primary slot.
- Marking a co-applicant Income Considered creates a Credit PD task automatically. The task appears under the Credit PD tab at `CPA Verified` and must be cleared like any other Credit PD task.
- Income documents are **mandatory** before Submit In-Principle if (a) `'Is Income Considered?'` = Yes AND (b) In-Principle Result = Recommended. Without docs, Submit In-Principle is blocked. Documents are optional if Is Income Considered = No, or if the user is rejecting at Submit In-Principle.
- The income detail section is hidden across all scenarios. The income programme for a co-applicant is changed only via the Credit PD tasks (not via the income details form). Credit PD tasks can be (re)triggered from the blue button on the right — admin role only.

## What this means for you

### BCMs

- You can now flip a co-applicant's `'Is Income Considered?'` from No to Yes from the Edit co-applicant form on the Applicant Details tab. Available on web AND mobile app.
- Use it only at `CPA Verified`. After Final Sanction Approval the form is locked — plan your IC decision before sanction.
- If the field is greyed out with the derogs error, the Finbox flag has refused. There is no override. Skip the IC flip on this case.
- After you flip, a Credit PD task for the co-applicant will appear in the Credit PD tab. Clear it before you Submit In-Principle.
- Upload the co-applicant's income documents in the income details form before you Submit In-Principle with In-Principle Result = Recommended. The system will block the submit if documents aren't collected.
- If you're on Saral 2.0 or a Normal-with-waiver case, the form is not available. Don't try to flip IC — escalate via the standard waiver workflow.
- If both `can_become_applicant` and `can_become_co-applicant` flags are Yes from Finbox, you have a swap option — use it if the cleaner credit profile sits on the co-applicant.

### CCPAs

- The `'Is Income Considered?'` field is now visible on the co-applicant's first-time Credit PD task completion (editable + mandatory). Set it correctly the first time — it carries forward.
- The income detail section is hidden. Don't look for it; it's been removed from the form.

### BCPAs / Branch & Central Ops

- The Edit co-applicant form is not accessible to you. Once a case is at `Post Sanction` or beyond, IC marking is final and cannot be changed.

## For any issues or clarifications

Please contact product support: Vishaw, Neeraj, Prem, Kiran, Vinesh, Anjali, or Mahesh. You can also drop a message in your relevant LAP G-Chat group for further assistance.
