# Release Note for BCPAs: LSQ Renach Handling

## What's new

Some customers already have an e-mandate from a past loan with us. The system can now check if that old e-mandate still works for this new loan.

- If it works → the system uses the old e-mandate again. **You don't have to send a new link.**
- If it doesn't work → the system shows you a new link. **You send the link to the customer.**

The system decides this on its own. You don't have to check anything.

## How it works

In the case at the **Post Sanction** stage:

1. Open the **Repayment Details** subtab.
2. Click **Yes** on **"Initiate E-Mandate Registration?"**.
3. Wait for the system to respond.

You will see one of three scenarios.

## Scenario 1: Brand new customer

The customer has never given us an e-mandate before.

- A new e-mandate link will appear.
- The system sends an SMS with the link to the customer **automatically**.
- **Also send the link to the customer manually.** Just to make sure they got it. Better safe than sorry.
- The customer clicks the link and signs up the e-mandate.

## Scenario 2: Old e-mandate is good for this loan

The customer has given us an e-mandate before, and the system says it still works for this new loan.

- No link will appear. No SMS goes out.
- The system uses the old e-mandate on its own.
- You don't have to do anything more. Move on to the next step.

## Scenario 3: Old e-mandate doesn't work for this loan

The customer has an old e-mandate, but the system says it does not fit this new loan. This usually happens when the new loan is bigger than the old e-mandate covers, or when the old e-mandate is going to expire too soon to last through all the EMIs.

- A new e-mandate link will appear.
- The system sends an SMS with the link to the customer **automatically**.
- **Also send the link to the customer manually.** Just to make sure.
- The customer clicks the link and signs up a fresh e-mandate.

## The simple rule

- **A link appears → send it to the customer manually too.** The SMS goes out on its own, but a manual nudge is always safer.
- **No link appears → the system used the old e-mandate. You're done.**

## If something looks wrong

Sometimes the case can get stuck and not move forward. If that happens, **escalate to product support**. Do not try to fix it from the panel — the checks all happen behind the scenes, and there is nothing you can change from your end.

## For any issues or clarifications

Please contact product support: Prem, Kiran, Vinesh, Anjali, or Mahesh. You can also drop a message in your relevant G Chat group.

<!--
  Skill output — produced by kissht-field-release-notes v1.1.1 from a real LIVE Jira ticket.
  Source ticket: LAP-2154 (LSQ Renach Handling) — status LIVE.
  Pattern: Branching Outcome.
  Output shape: Single-role one-pager (BCPA only).
  Voice level: B-strict (BCPA-grade plain English — scenarios first, NO data field references, NO JSON keys, NO API/LMS jargon, NO single-quoted system strings except UI labels the BCPA literally clicks).
  Reviewer feedback (2026-05-04): "scenarios in plain English without mention of any fields etc" — incorporated.
  Domain mini-patterns surfaced: SMS auto-send + manual-backup (Scenarios 1 & 3); silent-action acknowledgement via "no link appears = system used the old e-mandate" (Scenario 2); non-overridable rule via "Do not try to fix it from the panel" (If something looks wrong).
  Body word count: ~480.
  Drafted: 2026-05-04.
-->
