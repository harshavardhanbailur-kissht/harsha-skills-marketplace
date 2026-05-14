# Release Note: LSQ Renach Handling

## What this is about

When a BCPA initiates E-Mandate registration at Post Sanction, the system now checks whether the customer already has an approved mandate from a previous loan. Depending on what it finds, one of three things happens automatically — no new stage is introduced, and the BCPA's only action is one click.

- If an existing approved mandate fits this loan → the system reuses it; no new link is generated.
- If no prior approved mandate exists, or the existing one does not fit this loan → a fresh E-Mandate link is shown on the repayment activity.

The BCPA cannot override the outcome. The backend decides.

## What you do

Go to the case and open:

- Stage: **Post Sanction** (with BCPA)
- Subtab: **Repayment Details**
- Form: **Repayment & Disbursal Details Capture - v5**
- Dropdown: `'Initiate E-Mandate Registration?'`

Select **Yes** on the dropdown. That is the only action that triggers the new logic. The system does the rest.

## What happens next — 3 cases

Wait for the system to respond.

### Case 1 — First-time customer (no prior approved mandate)

- A new E-Mandate link appears on the repayment activity.
- The system sends an SMS with the link to the customer automatically. Also send the link to the customer manually — just to confirm they received it.

### Case 2 — Repeat customer; existing mandate fits this loan

Both conditions are met: Sanction Loan amount ≤ `'mandate_amount'`, AND Last EMI date + 5 years ≤ `'mandate_expiry_date'`.

- No link is shown. The success callback is auto-applied to the opportunity and the repayment activity. Every field maps in EXCEPT `'enach_session_id'` and `'juspay_pg_reference'`.
- Confirm reuse by checking that `'enach_reference_number'`, `'mandate_amount'`, `'mandate_approved_date'`, `'mandate_expiry_date'`, and `'status'` = `'APPROVED'` are populated on the opportunity and the repayment activity.
- You cannot override this outcome from the panel.

### Case 3 — Repeat customer; existing mandate does not fit this loan

Either condition failed: sanction loan amount > `'mandate_amount'`, or Last EMI date + 5 years > `'mandate_expiry_date'`.

- A fresh E-Mandate link appears on the repayment activity.
- The system sends an SMS with the link to the customer automatically. Also send the link manually as a backup.
- You cannot override from the panel. The fresh link generates a new mandate.

## After the E-Mandate step

The latest NACH reference number is included in the Push-to-LMS API request body and validated against the loan in LMS. If LMS rejects the push, the case will not move forward until the mandate is reconciled — escalate to product support.

Buffer policy on mandate expiry: the initial mandate uses a 5-year expiry buffer. For revised-mandate requests, the payment team checks if Last EMI date + 4 years ≤ existing `'mandate_expiry_date'`; if yes, the existing mandate is reused; if no, a fresh link is sent. When a fresh mandate is created, its buffer is 5 years again.

## What this means for you

### BCPAs

- Open the Repayment Details subtab on the Repayment & Disbursal Details Capture - v5 form. Selecting Yes on `'Initiate E-Mandate Registration?'` is the only action that triggers the new logic.
- For first-time customers (Case 1), proceed as before — a link appears; send it to the customer, and send manually as a backup even though the SMS fires automatically.
- For repeat customers where the system reuses the existing mandate (Case 2), no link appears. Confirm reuse by checking that `'enach_reference_number'`, `'mandate_amount'`, `'mandate_approved_date'`, `'mandate_expiry_date'`, and `'status'` = `'APPROVED'` are populated on the opportunity and the repayment activity.
- If you expected reuse but a link appeared (Case 3), the existing mandate failed one of the conditions. You cannot override from the panel — send the link and a fresh mandate will be generated.
- If LMS rejects the Push-to-LMS after the mandate step, the case will not move forward until the mandate is reconciled — escalate to product support.

## For any issues or clarifications

Please contact product support: Prem, Kiran, Vinesh, Anjali, or Mahesh. You can also drop a message in your relevant G Chat group for further assistance.

<!--
  Skill output — produced by kissht-field-release-notes v1.1 from a real LIVE Jira ticket.
  Source ticket: LAP-2154 (LSQ Renach Handling) — status LIVE, priority High, label qa_done.
  Reporter: Vishaw Kashyap. Assignee: Kunal Varade.
  Pattern: Branching Outcome (canonical example for this pattern).
  Output shape: Multi-role document.
  Voice level: A (operator-grade dense).
  Confluence sources: 1088716805 (LAP LOS canonical, Post Sanction stage owner = BCPA).
  Verified against glossary: yes — Post Sanction stage / BCPA owner / NACH-and-mandate vocabulary.
  Word count: ~400 (body, excluding hidden footer).
  Drafted: 2026-05-04.
  Structure corrected: 2026-05-14 — removed Pattern-A headings (## The new flow, arrow diagram,
  Stages in the system, ## Key rules); replaced with correct Pattern-B structure
  (## What this is about / ## What you do / ## What happens next — 3 cases /
  ## After the E-Mandate step). All factual content preserved; SMS auto-send + manual
  backup added to Cases 1 & 3 (consistent with lsq-renach-handling-bcpa-pager.md).
-->
