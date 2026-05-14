# Release Note for <Role>s: <Feature Name>

<!--
  TEMPLATE — Single-Role One-Pager.
  USE WHEN: user asks for "release note for <Role> only" / "<Role>-only release note" /
  "WhatsApp-friendly release note" / a personal one-pager.
  VOICE: B-strict for field roles (BCPA / BOM / COM / BCM / CCM / NCM / Sales);
         B for tech-ops / QA / SRE. See references/voice-and-pattern.md §Voice B-strict.
  Canonical example: examples/lsq-renach-handling-bcpa-pager.md (Voice B-strict)
  Word count target: ≤350 body words.
  Replace every <…> placeholder. Delete this comment block.
-->

## What this is about

<2-4 sentences in plain English. Grade-7 reading level. Short sentences.>

- If yes → <plain consequence>.
- If no → <plain consequence>.

## What you do

Go to the case and open:

- Stage: **<Stage Name>**
- Tab: **<Tab Name>**
- Subtab: **<Subtab Name>**
- Form: **<Form Name>**
- Dropdown / Field: **<Trigger Name>**

Click **<Yes / Submit / etc.>** on the dropdown. That is your only step. The system does the rest.

## What happens next — N cases

Wait for the system to respond.

### Case 1 — <Short label in plain English>

- <What you see>.
- <If an SMS / email / notification goes out:> The system sends <X> to the customer **automatically**.
- <If an auto-comm went out:> **Backup: send <X> to the customer manually too.** Just to make sure they got it.
- <Verification step if action was silent>.

### Case 2 — <Short label>

- <Plain explanation of what happens>.
- <Verification fields list — bulleted, in 'single quotes' for system strings>.

### Case 3 — <Short label>

- <Branch reasons: bulleted, plain English>.
- <What you do>.
- <Auto + manual backup pattern if comm fired>.

## After <event>

<Plain English downstream consequence. "If LMS does not accept it, escalate to product support.">

## The simple rule

- <Core decision bullet 1 — the key If / Then in plain English. E.g. "Link appears → send it to the customer manually too.">
- <Core decision bullet 2. E.g. "No link appears → the system used the old mandate. You're done.">

## If something looks wrong

<Escalation guidance in 2–3 sentences. Lead with what the operator will see ("If the case gets stuck and does not move forward…"). Then: "Do not try to fix it from the panel — there is nothing you can change from your end. Escalate to product support.">

## For any issues or clarifications

Please contact product support: <Named Human 1>, <Named Human 2>, <Named Human 3>, or <Named Human 4>. You can also drop a message in your relevant <channel name> for further assistance.

<!--
  HIDDEN FOOTER — KEEP FOR TRACEABILITY, STRIP BEFORE DISTRIBUTION

  Source ticket(s): <LAP-XXXX>
  Pattern: <Workflow Change | Branching Outcome>
  Output shape: Single-role one-pager
  Voice level: B-strict (field roles: BCPA / BOM / COM / BCM / CCM / NCM / Sales) or B (tech-ops / QA / SRE)
  Body word count: <N> (target ≤ 350)
  Drafted: <YYYY-MM-DD>
-->
