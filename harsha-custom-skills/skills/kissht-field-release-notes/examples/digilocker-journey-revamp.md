# Release Note: DigiLocker Journey Revamp

<!--
  Skill output — produced by kissht-field-release-notes from real LIVE Jira tickets.
  Source tickets: LAP-2180 (client side), LAP-2181 (server side), LAP-2222 (auto-update Underwriter Status).
  All three tickets are in status LIVE under epic LAP-2169 ("LAP <> LSQ - April adhoc changes").
  Reporters: Paras Arora (LAP-2180/2181), Shweta Iyengar (LAP-2222).
  Confluence sources: 1088716805 (LAP LOS canonical), 1101660180 (LAP Query Module — voice exemplar).
  Verified against glossary: yes.
  Word count: 461.
  Drafted: 2026-05-02.
-->

## The new flow

LSQ requests DigiLocker URL  →  server checks Underwriter Status  →  link generated or rejected  →  customer completes DigiLocker  →  9 KYC flags returned  →  LSQ rejects on FAILED  →  Kissht rejects in step

Stages in the system where this is visible:

- `Sales PD Completed`  (with CCPA — owns the KYC display + new rejection messaging)
- `CPA Verified`  (with BCM — sees the KYC-flag-driven rejection reasons on the panel)

Field & status values (new or changed):

- `'Underwriter Status'`: `'Not Seen'` (incoming, must be cleared), `'Rework'` (auto-set on link generation), `'Seen'` (post-completion).
- `'check_status'`: `'PASSED'` or `'FAILED'` (driven by 5 critical KYC sub-flags).

## Key rules

- DigiLocker is mandatory for all applicants and co-applicants. The case will not proceed until DigiLocker is completed for every party. There is no skip on either web or mobile.
- Before generating a DigiLocker link, the system checks if a selfie exists for the user with `'Underwriter Status'` = 'Not Seen'. If yes, the system auto-flips it to 'Rework' (sets `'is_discarded'` = true) and proceeds with link generation. The user does not have to wait.
- If the prior selfie is in 'Not Seen' for an unrelated reason and link generation is rejected, LSQ shows: _"Previous document is not processed correctly, get that closed and then process again."_ The applicant cannot proceed until the prior document is closed.
- A case is rejected only when LSQ confirms `'check_status'` = 'FAILED'. Kissht no longer rejects pre-emptively at its end. The trigger flags are: `'is_aadhaar_unique'`, `'face_verification'`, `'dob_matched'`, `'aadhaar_last_4_digits_matched'`, `'document_verification'`. Any one failing → `'check_status'` = 'FAILED'.
- The rejection reason shown on LSQ is picked from the failed flag, e.g. `'is_aadhaar_unique'` failure displays as "Aadhaar Uniqueness Check Failed".
- The More Details section of the Application Details tab now displays all 9 KYC flags as Success or Failure: Aadhaar Uniqueness, DOB Match, PAN Name Match, Aadhaar Declared Name Match, Aadhaar Face Verification, Aadhaar Document Verification, Aadhaar Last 4 Digits Match, PMLA Check, PEP Check.
- PAN is now collected for all users — every PAN-dependent check applies universally.

## What this means for you

### Sales (SM, BM)

- Set the customer's expectation early: every applicant AND co-applicant must complete DigiLocker. There is no skip, on web or mobile.
- If the customer says "the link is not coming" — confirm whether the prior selfie is in 'Not Seen'. If yes, the system clears it automatically; if not, that prior document must be closed first.

### CCPAs

- Open the More Details section of the Application Details tab to see the full 9-flag KYC display per applicant. Each flag reads Success or Failure.
- When the case is rejected, the rejection reason on the panel is now driven by which flag failed. Read the displayed reason; do not assume.
- For Saral and Normal cases alike — there is no programme-level difference in this flow.

### BCMs

- KYC-driven rejections now land with a specific rejection reason (one of the 7 failure flags). Read the reason on the panel before acting.
- Cases pending DigiLocker for any co-applicant will not move forward until that co-applicant completes it. Plan your TAT accordingly.

## For any issues or clarifications

Please contact product support: Paras, Shweta, Neeraj, Amar, or Sujit. You can also drop a message in your relevant LAP G-Chat group for further assistance.
