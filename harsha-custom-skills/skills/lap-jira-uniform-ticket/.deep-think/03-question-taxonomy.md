# 03 — Question Taxonomy

The skill is Socratic. It is allowed to ask 50–100 questions if needed. Quality over speed is locked. This file enumerates every question category, classifies each as MUST / CONDITIONAL / DEFER / NEVER, and gives exact phrasing for the MUST set.

The 14 categories (A–N) map 1:1 to slots in the spine templates and to extraction dimensions in the downstream `kissht-field-release-notes` Phase 2. There is no orphan question and no orphan slot.

---

## The 14 categories

| Code | Category | Owns which spine block | Maps to release-note extraction dimension |
|---|---|---|---|
| **A** | Intent + Why | Intent paragraph, Release-note line | What changed + Why it changed |
| **B** | Current state | Current flow that we want to fix | Old flow |
| **C** | Surface area | Stage list, touchpoints, per-system breakdown | Affected stages / surfaces |
| **D** | Vocabulary | Glossary footer, role/stage labels | Stage names, role names |
| **E** | Proposed change | Numbered Functional Flow, Step/Case, Per-row breakdown | New flow / branch outcomes |
| **F** | Matrix / config | Matrix table, Source-of-truth link | Routing rules, slabs |
| **G** | System strings | Inline `'quoted'` strings throughout | System strings (panel labels, status names) |
| **H** | Auto-comm + silent | Auto-comm flags, silent-action notes | Auto-comm events, silent system actions |
| **I** | Edge cases + bypasses | Exception block, Edge case list | Edge cases / bypasses |
| **J** | QA Scope | QA Scope block | (consumed at QA, not by release-notes) |
| **K** | BA Open Considerations | BA Open Considerations + Out of scope + Alternatives considered | (consumed at BA review) |
| **L** | Acceptance Criteria | AC organised by area | (consumed at sprint planning) |
| **M** | Sources / attachments | Sources footer | (provenance) |
| **N** | Contacts | Contacts block, reporter/assignee | Contacts (named humans) |

---

## MUST-ask categories per type

| Category | WC | BO | SC | RD | MX |
|---|:-:|:-:|:-:|:-:|:-:|
| A Intent | M | M | M | M | M |
| B Current state | M | M | M | — | M |
| C Surface area | M | M | M | M | M |
| D Vocabulary | M | M | M | M | M |
| E Proposed change | M | M | M | M | M |
| F Matrix | C | C | — | M | C |
| G System strings | M | M | M | M | M |
| H Auto-comm + silent | C | M | C | C | M |
| I Edge cases | M | M | C | M | M |
| J QA Scope | M | M | M | M | M |
| K BA Open Considerations | M | M | M | M | M |
| L AC | M | M | M | M | M |
| M Sources | M | M | M | M | M |
| N Contacts | M | M | M | M | M |

(M = MUST-ask, C = CONDITIONAL, — = NEVER for that type.)

The pattern: A/C/D/E/G/J/K/L/M/N are MUST for every type — they are the locked uniform spine. B is MUST for every type except RD (RD doesn't have a "current flow"). F is MUST only for RD. H is MUST for BO and MX (where silent actions are common). I is MUST for everything except SC (where edge cases are usually the bidirectional toggle behaviour, captured in E).

---

## MUST-ask question phrasing (exact)

These are the canonical phrasings. The skill MAY paraphrase if the PM has already partially answered, but MUST cover every dimension below before exiting Phase 4.

### A Intent + Why

- **A1.** "In one sentence: what is this ticket changing? Use the form 'X now does Y instead of Z' or '<Role> can now do <Action>'." *(This becomes the release-note line.)*
- **A2.** "In one paragraph: what's the business reason? What problem is the field user / underwriter / customer facing today that this change solves?"

### B Current state *(skip for RD)*

- **B1.** "Walk me through what happens today, step by step. Use numbered steps. Name the role doing each step."
- **B2.** "Where in this flow is the friction? Point to the specific step number."
- **B3.** *(SC only)* "What workaround are operators doing today to get around this? Be specific — what do they fill in junk fields with, what do they click twice, where do they re-enter?"

### C Surface area

- **C1.** "Which LAP stage(s) does this touch? Name them — Lead Initiation, Sourcing, Credit PD, IPA, FA, Final Sanction, Post Sanction substages, etc."
- **C2.** "Which screen(s) / form(s) / tab(s) / subtab(s) inside that stage?"
- **C3.** "Does this touch any system other than LOS? LSQ? LMS? Digio? CIBIL? An external partner?"

### D Vocabulary

- **D1.** "Which roles are affected? Pick from the glossary: BCM, CCM, NCM, SCH, BCPA, CCPA, BOM, COM, NSM, SM, BM, Sales RM, Auditor, Applicant, Co-applicant. Add any role that's not in this list and define it now."
- **D2.** "Are you using any acronym or label I haven't seen before in the LAP glossary? List them and define them now — they will be added to the glossary footer."

### E Proposed change

- **E1 (WC / MX).** "Walk me through the new flow, step by step. For each step: who does it, what they see, what they click. Use numbered sub-steps (1.1, 1.2, …) where one step has internal phases."
- **E1 (BO / MX-branch).** "What is the ONE operator action that triggers the branches? What are the branch outcomes? For each branch (Case 1, Case 2, …): what does the operator see on screen, what do they do next, and if the system acts silently — how does the operator verify it acted?"
- **E1 (SC).** "After the change, what happens on the form? Specify behaviour for both directions of any toggle (e.g., Yes → No AND No → Yes). What's the behaviour on the Mark-as-Complete form vs the Edit form?"
- **E1 (RD).** "List every value in the new dropdown / matrix / slab. For each value: what's the treatment? Where does the source of truth live (sheet, config doc, page link)?"
- **E2 (all types).** "For each step / case / row in your answer above: what's the SYSTEM CONSEQUENCE? Don't tell me what the operator does without telling me what the system does in response."

### F Matrix / config *(MUST for RD)*

- **F1.** "Show me the matrix as a table. Rows = ___, columns = ___, cells = the rule that applies."
- **F2.** "If a designated value is unavailable, what's the fallback? Walk me through the fallback chain."
- **F3.** "Is this configurable by ops without a code deploy? If yes, where (config screen URL or page)? If no, what's the change-process?"
- **F4.** "Are there geographic or state-wise variants? List them."

### G System strings

- **G1.** "Quote the EXACT text of every panel label, dropdown value, status name, button label, and error message that's part of this change. Use single quotes. If you have a screenshot, drop it and I'll extract."
- **G2.** "If this change adds, removes, or renames any of the above, list both the OLD string and the NEW string side by side."
- **G3.** "Quote any SMS / email / WhatsApp / in-app notification text verbatim — including dynamic variables in their template form (e.g., `{{applicant_name}}`)."

### H Auto-comm + silent *(MUST for BO/MX)*

- **H1.** "Does the system fire any auto-comm (SMS / email / notification) as part of this change? If yes — to whom, when, with what content?"
- **H2.** "Does the system perform any silent action — auto-populate a field, auto-create a callback, auto-route a case — without any operator click? If yes, what is it and how does the operator know it happened?"
- **H3.** "Are there any non-overridable backend rules in this change — places where the system decides and the operator cannot change it from the panel? List them."

### I Edge cases + bypasses *(MUST for WC/BO/RD/MX, CONDITIONAL for SC)*

- **I1.** "What happens at the boundary of any time window? (e.g., '72 hours' — what about hour 73? '9 years 6 months' — what about exactly 9y6mo?)"
- **I2.** "Is there a bypass / override path? Who can use it, under what condition?"
- **I3.** "What happens if the operator never completes this action? Does the case auto-expire? auto-route? sit forever?"
- **I4.** "What happens if data is missing / stale / invalid?"

### J QA Scope

- **J1.** "List the top 5–10 things QA must verify. Be specific — not 'verify the flow works' but 'verify Yes-to-No on Edit form saves with all income fields blank'."
- **J2.** "Are there any state-refresh scenarios QA must verify? (Real-time updates between stages, between tabs, after toggle.)"
- **J3.** "Any back-to-back toggle / replay scenarios? (Yes→No→Yes→No — does state match final value?)"
- **J4.** "Any cross-system QA — does QA need to verify LSQ, LMS, or any external system independently?"

### K BA Open Considerations

- **K1.** "What's NOT changing that should be explicitly called out? (Out-of-scope statement — Shape Up borrow.)"
- **K2.** "List any assumption you're making that BA should validate. For each: state the assumption, your proposed default, and the impact if the assumption is wrong."
- **K3.** *(when applicable)* "Did you consider any alternative approaches before settling on this one? In 2–3 sentences: what alternatives, and why did you pick this one? (Google design-doc borrow — optional.)"

### L Acceptance Criteria

- **L1.** "Give me 3–5 lean AC bullets — observable in UAT, organised by area. AC is NOT a re-listing of the proposed flow; it's the 'done' gates."

### M Sources / attachments

- **M1.** "Drop any attachments — screenshots, mocks, source-of-truth sheets, Confluence page links, Loom recordings. I'll list them in the Sources footer."

### N Contacts

- **N1.** "Reporter? Assignee? Sponsoring PM (if different)? Subject matter expert if QA / BA has questions?"

---

## CONDITIONAL questions (asked only if a previous answer flagged them)

| Trigger | CONDITIONAL question |
|---|---|
| C1 named ≥2 stages | "Does the change behave differently per stage? If so, walk me through each stage's variant." |
| C3 named LSQ/LMS/Digio | "What's the LSQ ↔ LOS contract? What field is sent / received? Quote the field names." |
| D1 named a role not in the glossary | "Define <new role> in one sentence — who they are, where they sit in the hierarchy, what they decide." |
| E2 revealed a step with no consequence stated | "What does the system do at this step? Or is this purely an operator action with no system response?" |
| F1 matrix has 3+ dimensions | "Is the matrix sliced state-wise / city-wise / branch-wise / hierarchy-wise? Show the sliced version." |
| H1 has auto-comm | "Should operators send a manual backup if the auto-comm fails? What's the backup channel?" |
| H2 has silent action | "How does the operator verify the silent action happened? Visual cue on panel? Status flip? Or 'trust the system, no need to verify'?" |
| I3 has SLA / expiry | "At expiry, who gets notified? What's the case status after expiry?" |
| K2 listed an assumption with no proposed default | "What default do you propose if the assumption fails? What's the impact?" |
| Issue type = Epic | "List the child stories / tasks you envision under this Epic. (One line each — not full descriptions.)" |
| Issue type = Story + S6 fired (multi-act) | "Should this be split into smaller stories? If yes, how would you slice it?" |

---

## DEFER questions (asked AFTER first draft, never before)

The skill batches these into one PM check after Phase 5 draft, before Phase 6 dedup.

- **DEFER-1.** "Reading the draft cold — does the Intent paragraph stand alone? Could a new PM joining tomorrow grasp it without context?"
- **DEFER-2.** "Are AC bullets really lean (3–5)? Or do they look like a re-list of the proposed flow?"
- **DEFER-3.** "Any system string in the draft that should be in single-quotes but isn't?"
- **DEFER-4.** "Anything missing that QA / BA / dev would have to ask you in standup?"
- **DEFER-5.** "Should we attach this draft to a parent Epic / Initiative? If yes, key?"

These are deferred because asking them upfront is wasted breath — the PM can't evaluate the draft until it exists.

---

## NEVER-ask categories

The skill **never** asks these — assumes from glossary, auto-fills, or skips entirely:

- **NEVER-1.** "What does BCM / CCM / NCM / etc. stand for?" → Glossary auto-defines in footer.
- **NEVER-2.** "What's the canonical Confluence page for LAP LOS?" → 1088716805, hardcoded in the Sources footer.
- **NEVER-3.** "What's the project key?" → LAP, hardcoded.
- **NEVER-4.** "What's the date?" → System date.
- **NEVER-5.** "What's your Jira account ID?" → `lookupJiraAccountId` on PM email.
- **NEVER-6.** "Story points?" → out of scope; sprint planning, not ticket authoring.
- **NEVER-7.** "Priority?" → defaults to Medium; PM can override post-delivery in Jira.
- **NEVER-8.** "Sprint / Fix Version?" → out of scope; release planning, not ticket authoring.
- **NEVER-9.** "Should I summarise what you said?" → no, the skill writes it as said and dedups in Phase 6.
- **NEVER-10.** "Are you sure?" → cowork-think-with-me discipline: never seek false reassurance.

---

## Question-flow discipline

- **One question per turn.** No multi-part stacks. If two dimensions are both unknown, the skill picks one, asks, writes, then asks the next.
- **No Q-then-summary turn.** The skill writes the answer to ANSWERS.md and asks the next question in the same response. PM doesn't see "thanks for that, here's what I understand" — that's filler.
- **Skip what's already answered.** If the PM's opening message gave A1 + A2, the skill skips to B1.
- **Inline glossary check.** If the PM mentions a term not in glossary, the skill pauses the main flow, asks D2 inline, then resumes.
- **Inline contradiction check.** If a new answer contradicts a prior one, the skill names the contradiction and asks PM to resolve before proceeding.
- **Cap on follow-ups within a category.** Max 5 follow-ups per category before the skill writes "best-effort answer captured; will validate at Phase 7" and moves on. Prevents rabbit holes.
- **Cap on total Phase 4 turns: 100.** If hit, the skill banner-warns and either ships a partial draft (with `MISSING:` markers) or asks the PM to schedule a follow-up. Prevents PM rage-quit (file 08 F1).
