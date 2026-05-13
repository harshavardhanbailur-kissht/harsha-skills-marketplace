# Release Note: <Feature Name>

<!--
  TEMPLATE — Branching Outcome pattern (multi-role).
  USE WHEN: ticket changes backend logic with ≥2 If-branches off one operator action,
  no new stage, no new SLA, no new approval chain.
  Canonical example: examples/lsq-renach-handling-multi-role.md
  Replace every <…> placeholder. Delete this comment block and any unused role sections.
  Run the §5 Phase 7 verification gate from SKILL.md before delivering.
-->

## What this is about

<2-4 sentences. The operator's mental model of what changed. NOT a flow diagram.>

- If <branch trigger A> → <result A summary>.
- If <branch trigger B> → <result B summary>.
- (If three or more branches: list each.)

## What you do

Go to the case and open:

- Stage: `<Stage Name>`
- Tab: `<Tab Name>`
- Subtab: `<Subtab Name>`
- Form: `<Form Name>`
- Dropdown / Field: `<Trigger Name>`

Click `<Yes / Submit / etc.>` on the dropdown. That is the only action that triggers the new logic. The system does the rest.

## What happens next — N cases

Wait for the system to respond.

### Case 1 — <Short label>

- <What you see — UI or panel state>.
- <Auto-action by the system, if any>.
- <Manual backup recommendation, if an auto-comm fired>.
- <How to verify the silent action, if applicable>.

### Case 2 — <Short label>

- <What you see>.
- <How to verify if the action was silent (e.g. fields populated)>.

### Case 3 — <Short label>

- <Branch reason: bulleted condition that triggered this branch>.
- <What you do>.
- <Manual backup recommendation if applicable>.

## After the customer / system completes <action>

<Downstream consequences. Push to LMS, sanction state changes, NACH validation, etc.>

## What this means for you

### <RoleAbbreviation 1>s

- <Imperative second-person bullet>.
- <How to verify (silent action) or what to do (visible action)>.
- <Edge-case bypass — if applicable>.

### <RoleAbbreviation 2>s (only if affected)

- <Imperative second-person bullet>.

## For any issues or clarifications

Please contact product support: <Named Human 1>, <Named Human 2>, <Named Human 3>, or <Named Human 4>. You can also drop a message in your relevant <channel name> for further assistance.

<!--
  HIDDEN FOOTER — KEEP FOR TRACEABILITY, STRIP BEFORE DISTRIBUTION

  Source tickets: <LAP-XXXX>, <LAP-XXXX>
  Pattern: Branching Outcome
  Output shape: Multi-role
  Voice level: A (operator-grade dense)
  Confluence sources: <pageId 1>, <pageId 2>
  Verified against glossary: yes / no
  Word count: <N>
  Drafted: <YYYY-MM-DD>
-->
