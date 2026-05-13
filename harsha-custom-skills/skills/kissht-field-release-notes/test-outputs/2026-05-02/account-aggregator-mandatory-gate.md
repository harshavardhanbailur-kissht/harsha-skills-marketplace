# Release Note: Account Aggregator Mandatory Before IMD Submission

<!--
  Test output — produced by kissht-field-release-notes skill on 2026-05-02.
  Source ticket: LAP-2171 (status LIVE) under epic LAP-2169 ("LAP <> LSQ - April adhoc changes").
  Reporter & assignee: Paras Arora.
  Confluence sources: 1088716805 (LAP LOS canonical) for stage names; lap-glossary.md for IMD / AA terminology.
  Verified against §6 verification gate.
  Word count: 419.
-->

## The new flow

SM punches case  →  system checks AA gate (spoke location OR primary applicant CIBIL < 700)  →  AA must be `'Success'` for primary applicant  →  IMD task can be submitted  →  case proceeds to `Sales PD Completed`

Stages where this is visible:

- IMD Collection Task  (with SM — case sits here pre-LOS until AA resolves)
- `Sales PD Completed`  (with CCPA — only reached AFTER IMD is submitted; gate happens upstream)

Field & status values:

- `'AA Status'` (Account Aggregator) values: `'Success'` (gate clears), `'null'` / `'Pending'` / `'Failed'` (gate holds).

## Key rules

- Account Aggregator is now mandatory for two specific cohorts before the IMD task can be submitted: (1) every case punched by an SM at a spoke location, regardless of CIBIL score; (2) every case where the main applicant's CIBIL score is below 700, regardless of branch. For all other cases, AA behaviour is unchanged.
- For these cohorts, IMD task submission is blocked unless the AA status of the **primary applicant** is `'Success'`. If AA is `'null'`, `'Pending'`, or `'Failed'`, the task cannot be submitted — the system will not let the SM proceed.
- The gate fires on the **primary applicant only**. Co-applicants' AA status does not unblock the IMD task.
- The gate is hard. There is no manual override. The case sits at the IMD task indefinitely until AA resolves to `'Success'`.

## What this means for you

### SMs at spoke locations

- Set the customer's expectation upfront: AA completion is mandatory before you can submit the IMD task, on every case you punch — not just sub-700 CIBIL ones.
- If AA is showing `'null'`, `'Pending'`, or `'Failed'`, you cannot proceed with IMD submission. Get the customer to complete AA first; the IMD task will unblock automatically once AA flips to `'Success'`.
- This is hub-and-spoke specific. Cases punched by a hub SM follow the universal rule below.

### SMs (all locations)

- For every case you punch where the main applicant's CIBIL score is below 700, the same gate applies: AA must be `'Success'` on the primary applicant before IMD submission.
- The system blocks IMD submit if AA is incomplete. There is no override.

### BCMs / CCPAs

- Cases caught by this gate will not reach your `Sales PD Completed` bucket until IMD is submitted, which means until AA is `'Success'`. If you're tracking a case that hasn't reached you yet, the most likely block is upstream AA.
- The gate is enforced before LOS — once a case lands with you at `Sales PD Completed`, AA is already `'Success'`. No new check on your end.

## For any issues or clarifications

Please contact product support: Paras, Prem, Kiran, Vinesh, Anjali, or Mahesh. You can also drop a message in your relevant LAP G-Chat group for further assistance.
