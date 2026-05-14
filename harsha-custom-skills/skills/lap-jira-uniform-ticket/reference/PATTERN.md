# PATTERN — the canonical 8-section spine

The exact shape every LAP ticket carries. Section names are fixed verbatim. Order is fixed. Per-type variations are listed at the bottom.

For voice, see `voice-and-style.md`. For the principles behind each section, see `PRINCIPLES.md`.

---

## The spine

Every ticket has a header block, a body of numbered sections, and a universal footer.

### Header (always present)

```
# LAP-<key> — <Title>

**Type:** <Story | Epic | Task> · **Status:** <status> · **Reporter:** <name>
**Assignee:** <name> · **Sponsor:** <name or N/A> · **Updated:** YYYY-MM-DD
**Direct link:** https://kissht.atlassian.net/browse/LAP-<key>

> **Release-note line:** <one-sentence operator-readable summary>
```

### Body sections (in fixed order, presence varies by type)

| # | Section header | Job |
|---|---|---|
| 1 | `## Intent` | What and why, one paragraph |
| 2 | `## Primary actor + Secondary actors` | Named roles touching this change |
| 3 | `## Preconditions` | What must already be true before this kicks in |
| 4 | `## Problem` | What hurts today, in prose |
| 5 | `## Current flow that we want to fix` | Numbered steps of today's workaround |
| 6 | `## Proposed solution` | Numbered steps of tomorrow's flow, each with a system consequence |
| 7 | `### Step N` / `### Case N` | Sub-structure under §6 for BO / MX |
| 8 | `## Approval matrix` | Table of slabs / rows / approvers |
| 9 | `## Per-system breakdown` | Leadgen / LOS / LMS / SARAL touchpoint slices |
| 10 | `## Logic` | Numbered rules, each with consequence (RD pattern) |
| 11 | `## Applicability` | Who / when / where the change applies |
| 12 | `## Exception` | Named single exception case |
| 13 | `## Summary table` | BO with three or more cases |
| 14 | `## QA Scope` | Numbered scenarios QA will run |
| 15 | `## Open Considerations for BA` | Named assumptions + proposal + impact |
| 15a | `### Out of scope` | What is explicitly NOT changing (always present) |
| 15b | `### Alternatives considered` | 2 to 3 sentences on rejected approaches (optional) |
| 16 | `## Acceptance Criteria` | 3 to 5 bullets organised by area |
| 17 | `## Role Definitions` | Acronym expansions when role acronyms used |

### Universal footer (always present)

```
---

**System strings referenced in this ticket** (verbatim, for downstream use):
- '<string>'
...

**Glossary used in this ticket** (auto-generated):
- <term> — <definition> (canonical | local)

**New terms added by this session** (for promotion to canonical glossary):
- <term> — <definition>

---

**Sources & attachments:**
- Parent epic: LAP-<key>
- Sibling tickets: LAP-<key>
- Confluence: <pageId> — <title>
- Attachments: <count>

**Bug fan-out** (if any): LAP-<key>, LAP-<key>

**Contacts:**
- Reporter: <Name> (<email>)
- Assignee: <Name> (<email>)
- Sponsor / Owning PM: <Name>
- SME for QA / BA questions: <Name>
```

The footer order is fixed. The release-notes skill reads System Strings and Contacts first, then Sources, then synthesises the body.

---

## Per-section rules

### §1 Intent

- **Must contain:** What this ticket does. Why. One paragraph. Plain English. Past or present tense.
- **Must not contain:** Bullets. Pseudocode. Hedges ("note: this does NOT change X" — that goes in `Out of scope`). Restatement of Proposed Solution step 1.
- **Length budget:** 2 to 5 sentences. One paragraph.
- **Smell test:** A new PM joining tomorrow can read this paragraph cold and tell you what is changing.

LAP-2052 §1: *"The idea is to make the list of the Property Document (type of ownership document) and Property Type (property occupancy status) to be same across LSQ."*

### §2 Primary actor + Secondary actors

- **Must contain:** One Primary actor (the role taking the action). Zero or more Secondary actors (roles affected or notified). Roles drawn from the glossary.
- **Must not contain:** Department names ("Sales team"). Pronouns. Job titles that are not LAP roles.
- **Length budget:** 1 line per actor. Bullets allowed.
- **Smell test:** Every name here also appears in the Proposed Solution OR the System Strings as the audience for an SMS / panel.

LAP-1812 §2: *"Primary: CPA User (Internal / Assisted Journey). Secondary: Applicants & Co-Applicants (Non-Rejected Only), Digio (E-sign partner)."*

### §3 Preconditions

- **Must contain:** What must be true before this flow can fire. Stage. Status. Configuration.
- **Must not contain:** The trigger event itself (that goes in §6 step 1).
- **Length budget:** 1 to 4 bullets.
- **Smell test:** If the precondition is false, the rest of the ticket is irrelevant.

LAP-1812 §3: *"Loan case stage is Post Sanction. Loan is sanctioned successfully."*

### §4 Problem

- **Must contain:** The operational pain that triggered this ticket. Named in prose. Names the role that hurts.
- **Must not contain:** The solution. "We should add..." belongs in §6.
- **Length budget:** 1 paragraph, 2 to 5 sentences.
- **Smell test:** A reader can tell you who is suffering and how, without reading further.

LAP-2039 §4: *"The Income Considered field for a co-applicant currently sits inside the Edit form of an already completed Credit PD activity... To actually set it to No, the BCM has to go through a long workaround."*

### §5 Current flow that we want to fix

- **Must contain:** Numbered steps of how the workaround works today. Each step is one operator action.
- **Must not contain:** Steps that are not changing. Steps unrelated to the workaround being killed.
- **Length budget:** Numbered list, typically 3 to 8 steps.
- **Smell test:** Removing this list and the BCM still understands what hurts? Then this section is the wrong shape.

LAP-2039 §5 (excerpt): *"1. BCM opens the Credit PD activity for the co-applicant. 2. BCM fills every income field on the form with random or placeholder values just to clear mandatory validation. 3. BCM clicks Mark as Complete and saves the activity..."*

### §6 Proposed solution

- **Must contain:** Numbered steps of how the flow works after this change. Every step names what the system does in response. Sub-bullets allowed for branch behaviour.
- **Must not contain:** Pseudocode. JSON. Steps that are unchanged from current flow (they don't appear in §6 because they don't change). Restatement of the Intent paragraph.
- **Length budget:** Numbered list, typically 3 to 7 top-level steps. Sub-bullets per step allowed.
- **Smell test:** Every step has a verb the operator does AND a consequence the system produces.

LAP-2039 §6 (excerpt): *"2. Behaviour on the Mark as Complete form: If Income Considered stays Yes, the form works exactly like it does today... If the BCM switches Income Considered to No, all other fields on the form stay visible but become disabled..."*

### §7 Step N / Case N (BO sub-structure)

- **Must contain (per Case):** What the operator sees ('verbatim string'). What the operator does. How the operator verifies (if silent). Consequence.
- **Must not contain:** Cases that are not branches of a single operator action (those are separate stages, not cases).
- **Length budget:** 4 bullets per Case.
- **Smell test:** Every Case has a See / Do / Verify / Consequence line.

### §8 Approval matrix

- **Must contain:** A table with slab / row / approver columns. One row per slab.
- **Must not contain:** Narrative restatement of the table.
- **Length budget:** Table.
- **Smell test:** The table is the truth; surrounding prose only explains what the columns mean.

LAP-2242 §8: *"| Loan Amount Slab | IPA Approver | FA Approver | Default Approver (Fallback) |"*

### §9 Per-system breakdown

- **Must contain:** One sub-section per system (Leadgen / LOS / LMS / SARAL / BT+Topup). Per system, named touchpoints with the change.
- **Must not contain:** Cross-system rules (those go in §10 Logic).
- **Length budget:** Bullets, one per touchpoint per system.
- **Smell test:** A QA can run the ticket per system without re-reading other sections.

LAP-2052 §9 (excerpt): *"At Property Documents Task: Update the 'Primary Property Document/Type of ownership document' dropdowns as per the list attached..."*

### §10 Logic

- **Must contain:** Numbered rules. Each rule names the trigger AND the system consequence. State-wise variants get their own numbered entry.
- **Must not contain:** Restatement (each rule's canonical form must be unique). Pseudocode.
- **Length budget:** Numbered list, 5 to 12 rules typical.
- **Smell test:** Every rule could be lifted into a release-note bullet without rewriting.

LAP-2242 §10 rule 3: *"Fallback logic: If no active user is mapped to the designated approver role for the applicable case... the case should automatically route to the Default Approver for that slab."*

### §11 Applicability

- **Must contain:** Who, when, where the change applies. Journey (Fresh / SARAL / BT+Topup). Stage. State, if state-specific.
- **Must not contain:** Logic rules (those are §10).
- **Length budget:** 1 paragraph or short list.
- **Smell test:** If a BCM in Tamil Nadu reads this, she knows whether it applies to her cases today.

### §12 Exception

- **Must contain:** Named single exception case where the rule does not apply.
- **Must not contain:** Multiple exceptions (each named exception gets its own line).
- **Length budget:** 1 paragraph.
- **Smell test:** The exception is genuinely an exception and not a parallel rule.

### §13 Summary table

- **Must contain (BO with three or more cases):** A table with Branch / Sees / Does / Consequence columns. One row per Case.
- **Must not contain:** Restatement of the per-Case prose; the table is a digest.
- **Length budget:** Table, one row per Case.
- **Smell test:** Operator can read the table alone and know what to do.

### §14 QA Scope

- **Must contain:** Numbered scenarios QA will run. Includes back-to-back toggles, refresh cases, cross-stage propagation. Names the simulation method when behaviour is hard to trigger.
- **Must not contain:** Implementation details. Test code. Test data dumps.
- **Length budget:** Numbered list, 4 to 10 scenarios.
- **Smell test:** A QA who has not read the rest of the ticket can run these scenarios.

LAP-2242 §14: *"Approver unavailability is simulated in UAT by inactivating the user at the relevant role / hierarchy level and submitting IPA or FA."*

### §15 Open Considerations for BA

- **Must contain:** Named assumptions where the BA needs to confirm. Each assumption gets a name (bold), a proposal (the default we are picking), and an impact-of-being-wrong.
- **Must not contain:** Resolved questions. Hedges that belong in `Out of scope`.
- **Length budget:** 1 to 4 assumptions, 1 paragraph each.
- **Smell test:** Each item names a real decision the BA can sign off on or push back on.
- **Conditional rule for RD type:** This section is OPTIONAL for RD tickets when EVERY assumption is closed (e.g. the source-of-truth sheet IS the truth, no override possible, no exceptions to flag). When omitted, the ticket MUST include a one-line statement in §1 Intent or §10 Logic stating "no open assumptions — the attached sheet / matrix is canonical." LAP-2052 is the exemplar for this conditional case.

LAP-2039 §15: *"1. Primary applicant scope. The Credit PD activity is also generated for the primary applicant with default Yes. Allowing the BCM to set No on the primary applicant would break eligibility... Proposal: keep the Income Considered field visible on the primary applicant's form but lock it to Yes... Impact: protects eligibility calculation and prevents accidental sanction breakage."*

#### §15a Out of scope

- **Must contain:** What this ticket is explicitly NOT changing.
- **Length budget:** 1 to 3 lines.
- **Smell test:** A regression in the called-out path during UAT is now provably the BCM's bug to file, not this ticket's silent break.
- **Conditional rule for RD type:** This sub-section is OPTIONAL for RD tickets when the change is purely additive (e.g. dropdown values added to match a source-of-truth sheet, no removal, no behavior change in any other surface). When omitted, the ticket MUST include a one-line statement in §6 Proposed solution OR §10 Logic stating "purely additive — no other surface changes." LAP-2052 is the exemplar for this conditional case.

#### §15b Alternatives considered (optional)

- **Must contain:** 2 to 3 sentences naming the alternative approaches considered and why they were rejected.
- **Length budget:** 2 to 3 sentences. No more.
- **Smell test:** Pre-empts the "why didn't you just..." review.

### §16 Acceptance Criteria

- **Must contain:** 3 to 5 bullets per area. Each bullet is observable in UAT.
- **Must not contain:** Re-listing of Proposed Solution rules. Implementation language. Given-When-Then.
- **Length budget:**
    - **Single-area ticket** (most SC, BO, RD): 3 to 5 bullets total. If you need more, the body is doing AC's job.
    - **Multi-area ticket** (most WC, MX): 3 to 5 bullets per area, organised by `### Area Name` sub-headers. Maximum 4 areas (so 12-20 bullets total). If you need more areas, split the ticket.
- **Smell test:** A QA can tick each bullet off without reading any other section.

LAP-1812 §16 follows the multi-area shape: bullets organised under `### Document Generation`, `### Consent`, `### Versioning`, `### Audit` — each with 2-3 bullets. This is the multi-area pattern, not a violation of the lean rule.

Single-area exemplar — LAP-2039 §16 stays at 3-5 bullets total because the change is one form / one toggle.

### §17 Role Definitions

- **Must contain (when role acronyms used):** One bullet per acronym, with expansion.
- **Length budget:** Bullets, one per acronym.
- **Smell test:** Every acronym in the ticket appears here OR in the canonical glossary.

LAP-2242 §17: *"CCM – Cluster Credit Manager. SCH – State Credit Head. NCM – National Credit Manager."*

---

## Per-type variations

The five types each take a slice of the spine. `R` = required, `O` = optional, `—` = forbidden.

| Section | WC Workflow Change | BO Branching Outcome | SC Simple Change | RD Reference Data | MX Mixed |
|---|:-:|:-:|:-:|:-:|:-:|
| §1 Intent | R | R | R | R | R |
| §2 Primary + Secondary actors | R | — | — | O | R |
| §3 Preconditions | R | — | — | O | R |
| §4 Problem | O | R | R | O | O |
| §5 Current flow | O | R | R | — | R |
| §6 Proposed solution | R | R | R | R | R |
| §7 Step / Case sub-structure | — | R | — | — | R (one stage only) |
| §8 Approval matrix | O | O | — | R | O |
| §9 Per-system breakdown | O | — | — | R | O |
| §10 Logic | — | — | — | R | — |
| §11 Applicability | O | R | O | R | O |
| §12 Exception | O | O | — | O | O |
| §13 Summary table (≥3 Cases) | — | O | — | — | O |
| §14 QA Scope | R | R | R | R | R |
| §15 Open Considerations | R | R | R | C¹ | R |
| §15a Out of scope | R | R | R | C² | R |
| §15b Alternatives considered | O | O | O | O | O |
| §16 Acceptance Criteria | R | R | R | R | R |
| §17 Role Definitions | O | O | O | R | O |

**C¹ — §15 conditional for RD:** Optional ONLY when every assumption is closed (sheet IS canonical, no override). Add a one-line "no open assumptions" statement in §1 or §10 if omitting.

**C² — §15a conditional for RD:** Optional ONLY when the change is purely additive (no removal, no behavior change in any other surface). Add a one-line "purely additive" statement in §6 or §10 if omitting.

LAP-2052 is the canonical exemplar for both conditional cases. Any new RD ticket that wants to invoke the conditional must mirror LAP-2052's tightness.

MX is bridge type: a WC spine where one stage in §6 has embedded BO Cases. Hard rule — only one stage may have embedded branches. If two stages branch, the skill insists on splitting into two tickets.

When no signal fires, the skill falls back to a universal spine: header, §1 Intent, free-form Description, §10 Logic, §14 QA Scope, §15 Open Considerations + §15a Out of scope, §16 AC, footer.

---

## The dedup rule

No rule appears in two sections. Each section has a unique job.

- §1 Intent says **what** + **why**.
- §4 / §5 say **how it works today**.
- §6 / §10 say **how it will work**.
- §14 says **how QA verifies**.
- §16 says **the done gates**.

If the Intent paragraph and Proposed Solution step 1 say the same thing, delete the Intent restatement.
If the Proposed Solution step 3 and AC bullet 4 say the same thing, delete the AC bullet (AC is observable outcome, not the rule).
If the Current Flow step 3 and Proposed Solution step 1 describe the same unchanged action, delete the Proposed Solution mention (unchanged actions don't appear in §6).
If a system string appears verbatim three or more times across sections, transform — first mention quotes, subsequent mentions reference by name.

The dedup pass auto-applies DELETE and TRANSFORM. JUSTIFY items get raised to the PM.

---

## Mapping to `kissht-field-release-notes`

The release-notes skill extracts five things from this ticket. Each maps to specific sections.

| Release-notes field | Pulled from |
|---|---|
| Operator-readable headline | Header `Release-note line` (verbatim) |
| Stages and owners | §2 Primary actor + Secondary actors, §6 Proposed solution stage names |
| Rules with consequences | §6 Proposed solution numbered steps, §10 Logic numbered rules |
| Verbatim system strings | Footer System Strings block |
| Branch outcomes | §7 Case blocks (See / Do / Verify / Consequence) |
| Named human contacts | Footer Contacts block (named humans, never "team" / "ops" / "QA") |
| Sources for traceability | Footer Sources block (parent epic, siblings, Confluence, attachments) |

Sections the release-notes skill mostly ignores: §15 Open Considerations for BA (internal), §15b Alternatives considered (internal), §17 Role Definitions (looked up from glossary).

If you change a section header in this file, check that the release-notes skill's parser still finds it. The header text is the contract.

---

## When a ticket fails Phase 7 validation

The skill runs 16 universal gates (U1 to U16) plus type-specific gates (WC1-8, BO1-7, SC1-6, RD1-6, MX1-4) plus destination-specific gates. Three failures are hard-stop:

- Empty Intent paragraph.
- Empty Proposed Solution / Logic.
- No detected type AND no fallback applied.

These three force re-engagement — the skill announces the hard-stop reason and re-enters the relevant phase. Other failures route back to the relevant Phase 4 question category.

Full gate enumeration is preserved in the skill author's design notes at `../lap-jira-uniform-ticket-design/deep-think/09-output-schema.md` (not loaded at runtime).
