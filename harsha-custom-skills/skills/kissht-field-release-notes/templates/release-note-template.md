# Release Note: <Feature Name>

<!--
  TEMPLATE — DO NOT DISTRIBUTE.
  Replace every <…> placeholder. Delete this comment block and any unused role sections.
  Run the §5 Phase 7 verification gate from SKILL.md before delivering.
-->

## The new flow

<Role-or-event A>  →  <Role-or-event B>  →  <Role-or-event C>  →  <Outcome 1> or <Outcome 2>

Stages in the system:

- `<Stage Name 1>`  (with `<Owner Role>`)
- `<Stage Name 2>`  (with `<Owner Role>`)
- `<Stage Name 3>`  (rejected by `<Role 1>` or `<Role 2>`, owner: `<Owner Role>`)

## Key rules

- <Rule 1>. <Consequence: what happens if violated, what the operator must do>.
- <Rule 2>. <Consequence>.
- <Rule 3 — typically the SLA / hard-reject timer>. After `<N>` days the case will be hard rejected by the system (case status will be `'<system string>'`) if it is still in `<list of stages>`. Once hard rejected, the only option is to `<recovery action>`.
- <Rule 4 — typically the mandatory-comment / mandatory-field rule>. <Consequence>.
- <Rule 5 — new CAM / database fields>. Two new CAM fields: `<Field 1>` (`<description>`) and `<Field 2>` (`<allowed values>`).
- <Rule 6>. <Consequence>.

## What this means for you

### <RoleAbbreviation 1>s

- <Imperative verb> <object> <constraint>.
- <Imperative verb> <object> <constraint>.
- <Imperative verb> <object> <constraint>.

### <RoleAbbreviation 2>s

- <Imperative verb> <object> <constraint>.
- <Imperative verb> <object> <constraint>.
- <Edge-case bypass — only if applicable>: If the `<other role>` is unavailable, you can `<bypass action>`. This `<effect>`. `<When-to-use guidance>`.

### <RoleAbbreviation 3>s

- <Imperative verb> <object> <constraint>.
- <Imperative verb> <object> <constraint>.

## For any issues or clarifications

Please contact product support: <Named Human 1>, <Named Human 2>, <Named Human 3>, or <Named Human 4>. You can also drop a message in your relevant <channel name> for further assistance.

<!--
  HIDDEN FOOTER — KEEP FOR TRACEABILITY, STRIP BEFORE DISTRIBUTION

  Source tickets: <LAP-XXXX>, <LAP-XXXX>, <LAP-XXXX>
  Confluence sources: <pageId 1>, <pageId 2>
  Verified against glossary: yes / no
  Word count: <N>
  Drafted: <YYYY-MM-DD>
-->
