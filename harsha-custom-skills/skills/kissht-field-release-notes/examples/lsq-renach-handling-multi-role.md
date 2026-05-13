# Release Note: LSQ Renach Handling

## The new flow

BCPA selects Yes on 'Initiate E-Mandate Registration?'  →  system checks for an existing approved mandate  →  conditions met or not  →  Success callback auto-applied (no link) or Link shown on the repayment activity

Stages in the system:

- Post Sanction  (with BCPA — Repayment Details subtab on the Repayment & Disbursal Details Capture - v5 form)

Outcomes when the dropdown is set to Yes:

- Success callback auto-applied to the opportunity and the repayment activity, no link shown — only when an existing approved mandate satisfies both conditions below.
- Link shown on the repayment activity — when no prior approved mandate exists, or either condition fails.

## Key rules

- The system re-uses an existing approved mandate only when BOTH conditions are met: Sanction Loan amount ≤ 'mandate_amount', AND Last EMI date + 5 years ≤ 'mandate_expiry_date'. If either fails, a fresh E-Mandate link is generated on the repayment activity.
- When the mandate is re-used, the success callback is mapped into the opportunity AND the repayment activity. Every field maps in EXCEPT 'enach_session_id' and 'juspay_pg_reference'.
- The latest NACH reference number is sent in the Push-to-LMS API request body and validated against the loan in LMS. If LMS rejects, the case will not Push to LMS until the mandate is reconciled.
- All conditions are evaluated in the backend. The BCPA cannot override the decision from the panel; selecting Yes on the dropdown is the only trigger.
- Buffer policy on mandate expiry: the initial mandate uses a 5-year buffer (tenure 5 years + 5 years = expiry at 10 years). For revised-mandate requests, the payment team checks if Last EMI date + 4 years ≤ existing 'mandate_expiry_date' — if yes, the existing mandate is re-used; if no, a fresh link is sent. When a fresh link generates a new mandate, that new mandate's buffer is 5 years again.

## What this means for you

### BCPAs

- Open the Repayment Details subtab on the Repayment & Disbursal Details Capture - v5 form. Selecting Yes on 'Initiate E-Mandate Registration?' is the only action that triggers the new logic.
- For first-time users (no prior approved mandate), proceed as before. The system will show an E-Mandate link on the repayment activity. Send it to the customer.
- For repeat customers with an approved mandate, the system may auto-apply the existing mandate and no link will be shown. Confirm re-use by checking that 'enach_reference_number', 'mandate_amount', 'mandate_approved_date', 'mandate_expiry_date', and 'status' = 'APPROVED' are populated on the opportunity and the repayment activity.
- If you expected re-use but a link still appeared, the case failed one of the conditions (sanction loan amount > mandate amount, or last EMI date + 5 years > mandate expiry). You cannot override from the panel. Send the link; a fresh mandate will be generated.
- Push to LMS now carries the latest NACH reference number for validation. If LMS rejects the push, the case will not move forward until the mandate is reconciled — escalate to product support.

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
  Word count: ~545 (body, excluding hidden footer).
  Drafted: 2026-05-04.
-->
