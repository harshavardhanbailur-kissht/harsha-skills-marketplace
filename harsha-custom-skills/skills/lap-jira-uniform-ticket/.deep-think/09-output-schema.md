# 09 — Output Schema

The exact markdown skeleton the skill produces. This is the contract with the downstream `kissht-field-release-notes` skill — its Phase 2 extraction logic depends on these section headers and their order.

---

## Universal header

Every ticket starts with this header block (regardless of type):

```
# LAP-<key> — <Title>

**Type:** <Story | Epic | Task> · **Status:** <status> · **Reporter:** <name>
**Assignee:** <name> · **Sponsor:** <name or N/A> · **Updated:** YYYY-MM-DD
**Direct link:** https://kissht.atlassian.net/browse/LAP-<key>

> **Release-note line:** <one-sentence operator-readable summary, GitLab borrow>
```

The `Release-note line` blockquote is the GitLab borrow — it's the first thing the downstream skill reads, and it lifts verbatim into the release note.

---

## Body sections, in order, by type

The body sections appear in this fixed order whenever they apply. Optional sections are marked **(opt)**. Sections marked **(forbidden)** for a type must NOT appear.

| # | Section header | WC | BO | SC | RD | MX |
|---|---|:-:|:-:|:-:|:-:|:-:|
| 1 | `## Intent` | required | required | required | required | required |
| 2 | `## Primary actor + Secondary actors` | required | forbidden | forbidden | opt | required |
| 3 | `## Preconditions` | required | forbidden | forbidden | opt | required |
| 4 | `## Problem` | opt | required | required | opt | opt |
| 5 | `## Current flow that we want to fix` | opt | required | required | forbidden | required |
| 6 | `## Proposed solution` (numbered, with consequences) | required | required | required | required | required |
| 7 | `### Step 1 / Step 2 / ... / Case 1 / Case 2 ...` (under §6 for BO, MX-branch slices) | forbidden | required | forbidden | forbidden | required (one stage only) |
| 8 | `## Approval matrix` (or per-row table) | opt | opt | forbidden | required | opt |
| 9 | `## Per-system breakdown` (Leadgen / LOS / LMS) | opt | forbidden | forbidden | required | opt |
| 10 | `## Logic` (numbered rules with consequences — RD pattern) | forbidden | forbidden | forbidden | required | forbidden |
| 11 | `## Applicability` | opt | required | opt | required | opt |
| 12 | `## Exception` | opt | opt | forbidden | opt | opt |
| 13 | `## Summary table` (BO ≥3 cases) | forbidden | opt | forbidden | forbidden | opt |
| 14 | `## QA Scope` (or `## QA Scenarios` / `## QA Testing Notes`) | required | required | required | required | required |
| 15 | `## Open Considerations for BA` | required | required | required | required | required |
| 16 | `### Out of scope` (Shape Up borrow, inside §15) | required | required | required | required | required |
| 17 | `### Alternatives considered` (Google borrow, inside §15) | opt | opt | opt | opt | opt |
| 18 | `## Acceptance Criteria` (3–5 bullets, organised by area) | required | required | required | required | required |
| 19 | `## Role Definitions` (when role acronyms used) | opt | opt | opt | required | opt |

The header text is fixed verbatim — `## Intent`, not `## What it is`; `## Open Considerations for BA`, not `## BA Open Items`. Cross-PM uniformity demands fixed headers.

---

## Universal footer (mandatory in every ticket)

```
---

**System strings referenced in this ticket** (verbatim, for downstream use):

Panel labels & dropdown values:
- '<string>'
- ...

Status names:
- '<string>'
- ...

Tab labels:
- '<string>'
- ...

Button / action labels:
- '<string>'
- ...

SMS / email / notification templates:
- '<verbatim with {{variables}}>'
- ...

Old → New rename pairs:
| Old | New |
|---|---|
| '<old>' | '<new>' |

---

**Glossary used in this ticket** (auto-generated):
- <term> — <definition> (canonical | local)
- ...

**New terms added by this session** (for promotion to canonical glossary):
- <term> — <definition>
- ...

Full glossary: kissht-field-release-notes/references/lap-glossary.md

---

**Sources & attachments:**
- Parent epic: LAP-<key> (when applicable)
- Sibling tickets: LAP-<key>, LAP-<key> (PM-tagged in Phase 2)
- Superseded by / supersedes: LAP-<key> (when applicable)
- Confluence: <pageId> — <title>
- Attachments: <count> (<list of filenames>)
- Loom / screenshots: <urls>

---

**Bug fan-out** (if any): LAP-<key>, LAP-<key>, ...

---

**Contacts:**
- Reporter: <Name> (<email>)
- Assignee: <Name> (<email>)
- Sponsor / Owning PM: <Name>
- SME for QA / BA questions: <Name>
```

The footer order is fixed: System Strings → Glossary → Sources → Bug fan-out → Contacts. The release-notes skill's Phase 2 reads the System Strings and Contacts blocks first, then the Sources, then synthesises the body. Order matters for the downstream skill's parser efficiency.

---

## Worked spine examples per type

### Spine WC (LAP-1812 / LAP-2048 shape)

```
# LAP-XXXX — <Title>
[universal header]

> Release-note line: <one sentence>

## Intent
<one paragraph: what + why>

## Primary actor + Secondary actors
- Primary: <role>
- Secondary: <role>, <role>

## Preconditions
- <condition>
- <condition>

## Proposed solution
1. <step> — <consequence>
   1.1 <sub-step> — <consequence>
   1.2 <sub-step> — <consequence>
2. <step> — <consequence>
3. <step> — <consequence>

## Applicability (opt)
<who / when / where the change applies>

## QA Scope
1. <scenario>
2. <scenario>
...

## Open Considerations for BA
<assumptions narrative>

### Out of scope
- <thing not changing>

### Alternatives considered (opt)
<2-3 sentences>

## Acceptance Criteria
- <Area A>: <bullet>
- <Area B>: <bullet>
- <Area C>: <bullet>

[universal footer]
```

### Spine BO (LAP-2046 shape)

```
# LAP-XXXX — <Title>
[universal header]

> Release-note line: <one sentence>

## Intent
<paragraph>

## Problem
<paragraph>

## Current flow that we want to fix
1. <step>
2. <step>

## Proposed solution

### Step 1: <action>
<paragraph>

### Step 2: <action that branches>
<paragraph leading into cases>

#### Case 1: <branch condition>
- What the operator sees: '<system string>'
- What the operator does: <action>
- How the operator verifies (if silent): <method>
- Consequence: <system action>

#### Case 2: <branch condition>
- What the operator sees: '<system string>'
- What the operator does: <action>
- How the operator verifies (if silent): <method>
- Consequence: <system action>

## Applicability
<matrix or list>

## Exception (opt)
<single exception case>

## Summary table (when ≥3 cases)
| Branch | Sees | Does | Consequence |
|---|---|---|---|

## QA Scope
...

## Open Considerations for BA
...

### Out of scope
...

## Acceptance Criteria
- <bullets>

[universal footer]
```

### Spine SC (LAP-2039 shape — gold standard)

```
# LAP-XXXX — <Title>
[universal header]

> Release-note line: <one sentence>

## Problem
<paragraph>

## Current flow that we want to fix
1. <step>
2. <step>
... (numbered, painful)

## Proposed solution
1. <change>
2. Behaviour on the <form name> form:
   * If <condition>, <consequence>.
   * If <other condition>, <consequence>.
3. <consequence summary>
4. Behaviour on the <other form> form (when bidirectional toggle applies):
   * Switching A → B: <consequence>.
   * Switching B → A: <consequence>.

## QA Scope
1. <scenario>
2. <scenario including state-refresh>
3. <back-to-back toggle scenario>
...

## Open Considerations for BA
<narrative>

Items where BA needs to confirm an assumption:
1. **<assumption name>.** <one paragraph: assumption + proposal + impact>
2. **<assumption name>.** <one paragraph>

### Out of scope
- <thing not changing>

## Acceptance Criteria
- <Area A>: <bullet>
- <Area B>: <bullet>
- <Area C>: <bullet>

[universal footer]
```

### Spine RD (LAP-2052 / LAP-2242 shape)

```
# LAP-XXXX — <Title>
[universal header]

> Release-note line: <one sentence>

## Intent
<paragraph>

## Approval matrix (or per-row table)
| Slab | IPA | FA | Default fallback |
|---|---|---|---|

## Per-system breakdown (when cross-system)
### Leadgen
- <touchpoint>: <change>
### LOS — Fresh Normal journey
- <touchpoint>: <change>
### LOS — SARAL journey
- <touchpoint>: <change>

## Logic
1. <rule + consequence>
2. <rule + consequence>
... (numbered, no repetition)
N. **State-wise variants:** <variants>

## QA Testing Notes
- <scenario>
- <scenario>

## Open Considerations for BA
<narrative>

### Out of scope
- <thing not changing>

## Acceptance Criteria
- <Area A>: <bullet>
- <Area B>: <bullet>

## Role Definitions (for reference)
* **<acronym>** – <expansion>
* **<acronym>** – <expansion>

[universal footer]
```

### Spine MX (Mixed)

WC spine, with one stage in `## Proposed solution` replaced by an inline `### Case 1 / ### Case 2` block following the BO See/Do/Verify pattern. Hard rule: only one stage may have embedded branches; if the PM has two branching stages, the skill insists on splitting into two tickets.

### Spine fallback (universal)

```
# LAP-XXXX — <Title>
[universal header]

> Release-note line: <one sentence>

## Intent
<paragraph>

## Description
<paragraph or numbered list — whatever fits>

## Logic
1. <rule + consequence>
2. <rule + consequence>

## QA Scope
- <scenario>

## Open Considerations for BA
<narrative>

### Out of scope
- <thing not changing>

## Acceptance Criteria
- <bullets>

[universal footer]
```

---

## Phase 7 validation checks (the gates)

Universal checks (apply to every ticket type):

| # | Check | Routes back to phase |
|---|---|---|
| U1 | Header has key, title, type, status, reporter, assignee, link | Phase 0 / Phase 4 N |
| U2 | Release-note line present and ≤ 1 sentence | Phase 4 A1 |
| U3 | Intent paragraph present, plain English, no bullets, no pseudocode | Phase 4 A |
| U4 | Every numbered rule in Proposed Solution / Logic carries a consequence | Phase 4 E2 |
| U5 | Every system string is in single quotes | Phase 5 R1 |
| U6 | System Strings footer present and complete (every body string listed) | Phase 5 R5 |
| U7 | Glossary footer present, every named role/stage/string accounted for | Phase 6 sweep |
| U8 | No section appears that's `forbidden` for the detected type | Phase 5 spine selection |
| U9 | Every section that's `required` for the detected type is present | Phase 5 spine selection |
| U10 | AC has 3-5 bullets organised by area | Phase 4 L1 |
| U11 | AC bullets are observable in UAT (no implementation language) | Phase 4 L1 |
| U12 | Out of scope statement present in BA Open Considerations | Phase 4 K1 |
| U13 | Contacts block has named humans (regex: not "team", "ops", "QA") | Phase 4 N |
| U14 | Sources footer present with parent / siblings / Confluence / attachments | Phase 4 M |
| U15 | No section content is repeated across sections (Phase 6 sweep clean) | Phase 6 |
| U16 | No `[BLOCKED]` / `[CONTRADICTION]` markers, OR they are explicitly flagged in title | Phase 4 / F1 / F10 |

Type-specific checks: WC1-8, BO1-7, MX1-4, RD1-6, SC1-6 (full enumeration in `references/output-gating-checklist.md` derived from this file).

Destination-specific checks:

| # | Markdown destination | # | Jira destination |
|---|---|---|---|
| MD1 | File written at user-specified path | JR1 | Reserved key has been edited (not still stub) |
| MD2 | File extension is `.md` | JR2 | ADF round-trip diff is clean |
| MD3 | If file existed, overwrite confirmed | JR3 | Reporter / assignee Jira account IDs resolved |
| | | JR4 | Linked tickets (parent / siblings) created via createIssueLink |
| | | JR5 | Attachments uploaded |
| | | JR6 | Status set to To Do (default) or PM-specified |

Hard-stops (skill refuses to deliver):

- Empty Intent paragraph.
- Empty Proposed Solution / Logic.
- No detected type AND no fallback applied.

These three force re-engagement — the skill announces the hard-stop reason and re-enters the relevant phase.
