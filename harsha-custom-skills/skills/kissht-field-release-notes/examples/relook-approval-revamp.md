# Release Note: Relook Approval Revamp

<!--
  REFERENCE ARTIFACT — the original artifact this skill was reverse-engineered from.
  Source: user-uploaded Word doc (Relook_Approval_Revamp_Release_Note.docx, May 2026).
  Verbatim transcription. Used as the gold-standard test case for verification.
  Word count: 287.
-->

## The new flow

BCM raises relook  →  CCM reviews  →  NCM reviews  →  Approved or Reject Queue

Stages in the system:

- Relook CCM Approval Pending  (with CCM)
- Relook NCM Approval Pending  (with NCM)
- Reject Queue  (rejected by CCM or NCM, owner: BCM)

## Key rules

- Rejection sends the case to the Reject Queue. No returns. The BCM has to raise the approval again.
- After 30 days the case will be hard rejected by the system (case status will be 'Lost Rejected') if it is still in any of these three stages: Relook CCM Approval Pending, Relook NCM Approval Pending, or Reject Queue. Once hard rejected, the only option is to ask the SM to repunch the case. Get the case approved within 30 days or take action swiftly and accurately.
- Rejection comment is mandatory for both CCM and NCM.
- Two new CAM fields: Relook Date (separate from the original case date) and Relook Status (Yes or No).
- Owner and stage are visible throughout the flow.

## What this means for you

### BCMs

- Raise relooks directly in the system. They route to CCM automatically.
- Open the Approval tab in the Reject Queue to read CCM and NCM rejection comments.
- If a case lands in the Reject Queue, act quickly. Get the case approved within 30 days.
- In case of hard reject (case status will be 'Lost Rejected'), the only option is to ask the SM to repunch the case.

### CCMs

- You are now the first approver on every relook.
- Act within 30 days. Inaction will hard reject the case.
- Rejection note is mandatory. Approving sends the case to NCM. Rejecting sends it to the Reject Queue.

### NCMs

- You are now the second approver. Cases reach you only after CCM approval.
- The same 30 day deadline applies. Rejection note is mandatory.
- If the CCM is unavailable, you can view the case and forward the request directly to yourself. This bypasses the CCM bucket and the case lands in your bucket directly. Please use accordingly.

## For any issues or clarifications

Please contact product support: Prem, Kiran, Vinesh, Anjali, or Mahesh. You can also drop a message in your relevant G Chat group for further assistance.
