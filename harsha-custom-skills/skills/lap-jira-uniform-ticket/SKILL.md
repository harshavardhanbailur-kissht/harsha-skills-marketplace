---
name: lap-jira-uniform-ticket
description: |
  Socratic Jira ticket-writing skill for the Kissht LAP product team. Forces the PM
  through a structured interrogation that produces a uniform-pattern ticket every time,
  so (a) every PM on the team writes to the same standard regardless of seniority,
  (b) the resulting ticket can be lifted directly into the kissht-field-release-notes
  skill to produce a Relook-style or Renach-style operator release note in one pass,
  and (c) downstream consumers (BA, QA, Dev, Ops) can read any LAP ticket cold and
  understand it without re-asking the PM. If the Atlassian MCP is connected, auto-searches
  the LAP Jira project and the LAP Confluence space for related tickets BEFORE asking
  the PM; otherwise falls back to asking the PM directly. Classifies the ticket into one
  of 5 types (Workflow Change, Branching Outcome, Simple Change, Reference Data, Mixed),
  then asks 9-17 type-trimmed MUST questions before drafting. Never assumes. Blocks on
  undefined glossary terms. **v1.0.1 beta — markdown output only**; push-to-Jira via
  createJiraIssue planned for v1.1 once the Atlassian MCP integration is bundled.
version: 1.0.2
author: Harshavardhan Bailur
references:
  - kissht-field-release-notes (downstream consumer — every ticket from this skill
    must be cleanly extractable by it)
  - harsha-custom-skills:cowork-think-with-me (parent in spirit — same Socratic stance)
triggers:
  - write a LAP ticket
  - write a LAP story
  - write a LAP task
  - write a LAP epic
  - draft a LAP ticket
  - new LAP ticket
  - create a LAP Jira ticket
  - LAP ticket for
  - file a LAP ticket
  - help me write a LAP story
  - LAP-XXXX from scratch
  - new ticket on LAP project
  - write a Jira ticket for LAP
  - turn this idea into a LAP ticket
  - turn this slack into a LAP ticket
  - turn this meeting into a LAP ticket
  - LAP ticket from PRD
  - convert this to a LAP ticket
  - structure this as a LAP ticket
  - LAP uniform ticket
  - LAP gold standard ticket
  - lap-jira-uniform-ticket
---

# LAP Jira Uniform Ticket — One Skill, Five Types, One Spine

> **Canonical exemplars (read at least 2 before drafting if you are new to this skill)**:
> - `examples/LAP-2039.md` — Simple Change. The user-authored gold standard with QA Scope + BA Open Considerations.
> - `examples/LAP-2242.md` — Reference Data. Approval matrix table + 10 numbered logic items, zero repetition.
> - `examples/LAP-2052.md` — Reference Data. Sectioned by surface area (Leadgen / LOS / etc.), super clean. Canonical for RD-type Open-Considerations + Out-of-scope conditional omission.
> - `examples/LAP-2154.md` — Branching Outcome. ONE operator action (`'Initiate E-Mandate Registration?'`) with 3 backend-state branches + buffer-policy edge case. The release-notes skill cites this as its canonical Pattern B (Renach) source.
> - `examples/LAP-1812.md` — Workflow Change. Multi-area Acceptance Criteria pattern (organised by Document Generation / Consent / Versioning / Audit sub-areas).
> - `examples/LAP-2046.md` — Workflow Change with matrix.
> - `examples/LAP-2048.md` — Mixed (workflow change with branching outcomes embedded).
>
> **The principles that govern this skill**: `reference/PRINCIPLES.md`.
> **The output spine every ticket carries**: `reference/PATTERN.md`.
> **The voice that prevents LLM-ticket smell**: `reference/voice-and-style.md`.

---

## 1. The Problem This Skill Solves

Three problems the Kissht LAP team has today, all linked:

1. **Inconsistent ticket quality across PMs.** The same feature written by two different PMs lands in Jira looking like two different products. New PMs have no canon to copy from. Senior PMs drift over time. The team's strongest tickets (LAP-2039, LAP-2242, LAP-2052) sit unrecognised as exemplars while weaker tickets pass code review.
2. **Release notes can't be auto-generated cleanly.** The downstream `kissht-field-release-notes` skill needs a predictable shape — named stages with owners, rules with consequences, verbatim system strings, branch outcomes, named contacts. When tickets vary, the release-notes writer has to re-interview the PM. The skill exists; the input is broken.
3. **PMs leak context downstream and re-pay the cost on every ticket.** BA asks "what should happen if X?" QA asks "is the Saral journey in scope?" Dev asks "what's the consequence if the auto-action fails?" Each question is a context switch the PM already paid for once. A uniform pattern with QA Scope and BA Open Considerations sections fronts those questions into the ticket, paid once.

This skill fixes all three by enforcing the same Socratic flow on every PM, every ticket type, every time.

---

## 2. The Five Ticket Types

Every LAP ticket is classified into exactly one of five types. The type determines which sections of the uniform spine are MUST, OPTIONAL, or SKIPPED, and which MUST questions get asked.

| Code | Name | Detection heuristic | Maps to release-notes pattern | Canonical exemplar |
|---|---|---|---|---|
| **WC** | Workflow Change | Names a NEW stage / approval level / SLA / mandatory action | Pattern A (Relook) | LAP-1812, LAP-2046 |
| **BO** | Branching Outcome | One operator action triggers ≥2 if-branches with no new stage | Pattern B (Renach) | LAP-2154 |
| **SC** | Simple Change | Single form / field / toggle change killing a workaround | Pattern A (lite) | LAP-2039 |
| **RD** | Reference Data | Dropdown / matrix / config / slab change; no flow change | Pattern A (matrix-only) | LAP-2052, LAP-2242 |
| **MX** | Mixed | WC signals AND BO signals fire simultaneously | Pattern A with embedded Cases | LAP-2048 |

PM-readable summary: `reference/PATTERN.md` §"Per-Type Variations". (Skill author's architectural notes are quarantined out of the active skill folder at `../lap-jira-uniform-ticket-design/deep-think/`; not loaded at runtime.)

### Why no sixth "Trivial" type

The team explicitly rejected an express path. Calibration value of forcing every PM through the same Socratic flow once outweighs the per-ticket time saving, and a fast-path added now is impossible to remove later without breaking downstream `kissht-field-release-notes` extraction. Type-specific trimming (RD asks ~9 MUST questions; WC asks ~16) is the only pace control. Re-evaluate after 4 weeks of usage data.

---

## 3. When This Skill Activates

| User intent | What I do |
|---|---|
| "Write a LAP ticket for <feature>" | Phase 0→8 single-feature pipeline |
| "Write a LAP story for <feature>" | Same — "story" is a ticket type label, not a skill switch |
| "Write a LAP epic for <theme>" | Same flow, but Phase 3 classifies likely as MX or WC and Phase 4 mandates child-ticket enumeration |
| "Turn this Slack thread into a LAP ticket" + paste | Phase 1 skipped (PM has provided context); Phase 2→8 |
| "Turn this meeting transcript into a LAP ticket" + paste | Phase 1 partial (auto-search runs in parallel for related tickets); Phase 2→8 |
| "Convert this PRD into a LAP ticket" + paste | Phase 1 + Phase 2 in parallel; Phase 3→8 |
| "I want to write a LAP-2242-style ticket" | Force RD type at Phase 3; otherwise full flow |
| "Just give me the template for <type>" | Hand off `templates/<type>.md` directly; do NOT run the full skill (the templates exist for direct use, but they are skeletons, not finished tickets) |

**Out of scope (explicit hand-offs)**:
- Writing the operator release note from a finished LAP ticket → use `kissht-field-release-notes`.
- Multi-ticket bundle release packages → write each LAP ticket here, then run `kissht-field-release-notes` with the bundle.
- Bug tickets → not in scope. (LAP bugs follow a different pattern with repro steps, expected vs actual, severity. Continue using your existing bug-filing process. A dedicated bug-pattern skill may be added to the marketplace later if the team requests it.)
- Sub-tasks → not in scope. PMs file the parent Story / Task / Epic with this skill; sub-tasks are created by the assignee at sprint planning.

---

## 4. Workflow — Eight Phases

Every session runs Phase 0 through Phase 8 in order. No phase is skippable except as noted.

### Phase 0 — Activate & Set Destination

Skill loads. One opening question before anything else:

- **D1.** "Quick orientation — is this a new feature, a tweak to an existing feature, a config / dropdown change, or something else?" (Used to seed type detection.)

**v1.0.1 beta:** output destination is markdown-only. PM gets a clean ticket body in chat at Phase 8 to paste into Jira manually. Push-to-Jira via `createJiraIssue` is planned for v1.1 once the Atlassian MCP integration is bundled into the plugin (see §11 References).

### Phase 1 — Auto-Search (Jira + Confluence) — CONDITIONAL on Atlassian MCP

**If the Atlassian MCP is connected** (skill detects via tool availability check), skill runs two queries in parallel BEFORE asking the PM about related tickets:

- JQL on `project = LAP` filtered by keywords extracted from PM's Phase 0 answer + any title/topic the PM has mentioned. ORDER BY updated DESC. Top 10 candidates pulled.
- CQL on the LAP Confluence space (`https://kissht.atlassian.net/wiki/spaces/LAP`) with the same keywords. Top 5 pages pulled.

Both searches fail-graceful: if Confluence is slow or unauthorised, skill proceeds with Jira-only and notes it.

**If the Atlassian MCP is NOT connected** (no Jira/Confluence tools available), skill skips the auto-search entirely and tells the PM at Phase 2: *"I can't auto-search Jira or Confluence in this session. Drop any related ticket keys or Confluence page IDs you want me to know about, or say 'none' to proceed."* The PM provides context manually.

Phase 1 produces a candidate list saved internally — no PM interaction yet (other than the fallback prompt above when the MCP is unavailable).

### Phase 2 — Verify Context with PM

Skill shows the top 5 Jira candidates + top 3 Confluence pages and asks:

- **V1.** "Before we draft, here's what the LAP project already has on this topic. For each, mark RELATED, NOT-RELATED, or DUPLICATE." (DUPLICATE means the PM might be re-filing an existing ticket — skill flags this hard at Phase 8.)
- **V2.** *(only if PM tags 7+ of 8 candidates as NOT-RELATED, indicating bad search recall)* "My search wasn't useful. Give me a tighter 2-3 word search phrase and I'll try once more."
- **V3.** *(only if all candidates dismissed AND no re-search succeeds)* "I couldn't find related context. Are there any LAP tickets, Confluence pages, or external docs you want me to know about? Drop links."

Exit criterion: PM has either picked relevant context OR explicitly told the skill there is none.

### Phase 3 — Classify Ticket Type

Skill asks 1-3 classification questions to nail down WC / BO / SC / RD / MX:

- **T1.** "Does this introduce a new STAGE in the LAP flow, a new APPROVAL chain, a new SLA, or a new MANDATORY action a role must perform?" (YES → likely WC or MX.)
- **T2.** "Does this change a single OPERATOR ACTION such that the system now does ≥2 different things depending on a condition? List the conditions if yes." (YES → likely BO or MX.)
- **T3.** *(if both T1 and T2 are YES)* → MX. *(if neither)* "Is this a single FORM / FIELD / TOGGLE change, or a DROPDOWN / MATRIX / CONFIG / SLAB change?" → SC or RD.

Exit criterion: type is locked. Skill announces: "Classified as <type> — <one-line reason>. The questions ahead are tailored for <type>; we'll skip the ones that don't apply."

### Phase 4 — Socratic Decompose

The longest phase. Skill asks the type-trimmed MUST questions from §5 below, in the order specified.

Two strict rules during Phase 4:

1. **Ghost terms BLOCK.** If PM uses a term not in `knowledge-base/lap-glossary.md`, skill stops and asks: "You mentioned `<term>`. I don't have it in the LAP glossary. In one sentence: what is it? Is it a stage / role / system string / abbreviation / concept?" Definition added to glossary so the next PM doesn't have to define it.
2. **No assumption substitution.** If PM gives a 3-word answer to a multi-part question, skill asks the missing parts as separate follow-ups. It does not silently fill in "probably the BCM" or "I'll assume Final Sanction Pending stage".

Exit criterion: every MUST question for the locked type is answered AND every glossary term has a definition AND no contradictions remain in answers.

### Phase 5 — Draft Into Uniform Spine

Skill renders the answers into the appropriate template (`templates/<type>.md`) producing a complete first draft. The draft honors the 10-section uniform spine from `reference/PATTERN.md`.

PM gets the draft inline + asked: "First-pass draft above. Read it through. Anything wrong, missing, or restated?"

### Phase 6 — Anti-Repetition + Glossary Sweep

Skill runs two automated passes on the draft:

1. **Anti-repetition.** Detects sentences that restate a rule already covered in another section. If found, asks PM "Section [5] says '<X>'; section [6] also says '<Y>'. Same rule? If yes, I'll keep it in [5] only." Cap: 5 such prompts per draft.
2. **Glossary sweep.** Auto-populates the footer Glossary section with definitions for every term used in the body (pulled from `knowledge-base/lap-glossary.md`). Any ghost term that escaped Phase 4 gets caught here and triggers a follow-up question.

Exit criterion: no repetition prompts left to resolve AND every term in the body has a glossary entry.

### Phase 7 — Validate Against Output Gates

Skill checks the draft against 8 universal gates + 2-4 type-specific gates. See §6.

If any gate fails → loop back to the relevant Phase 4 question or Phase 5 redraft.

### Phase 8 — Deliver (v1.0.1 beta: markdown only)

- Skill outputs the final ticket as fenced markdown in chat.
- PM copies, opens Jira, pastes into description, sets Reporter / Assignee / Sprint / Fix Version per skill's footer hints.
- Skill provides a copy-paste hint for the title field separately (since Jira's title is not part of the description body).

**v1.1 roadmap (not in this version):** push-to-Jira via `createJiraIssue`. When the Atlassian MCP is bundled into the plugin, this phase will offer a second option ("push directly to Jira and return the LAP-XXXX key"). Until then, markdown-only is the only delivery path.

---

## 5. The MUST-Question Taxonomy

The categories below show what gets asked per type. (Full taxonomy with exact question phrasings is preserved in the skill author's design notes at `../lap-jira-uniform-ticket-design/deep-think/03-question-taxonomy.md` — not loaded at runtime.)

### Universal MUST (asked for ALL types, in order)

- **A1** — One-sentence what-this-changes. Form: "X now does Y instead of Z" or "<Role> can now do <Action>".
- **A2** — One-paragraph why-this-changes. The business reason: what problem is the field user / underwriter / customer facing today?
- **C1** — Which LAP stage(s) does this touch? (Pulled from `knowledge-base/lap-stages.md`.)
- **C2** — Which screen(s) / form(s) / tab(s) / subtab(s) inside that stage?
- **C3** — Does this touch any system other than LOS? LSQ? LMS? Digio? CIBIL? An external partner?
- **D1** — Which roles are affected? (Pulled from `knowledge-base/lap-roles.md`.)
- **G1** — Quote the EXACT text of every panel label, dropdown value, status name, button label, and error message that's part of this change. Use single quotes.
- **J1** — List the top 5-10 things QA must verify. Be specific.
- **K1** — What's NOT changing that should be explicitly called out? (Becomes the Out of scope line.)
- **K2** — List any assumption you're making that BA should validate. For each: state the assumption, your proposed default, and the impact if the assumption is wrong.
- **L1** — Give me 3-5 lean AC bullets — observable in UAT, organised by area. AC is NOT a re-listing of the proposed flow; it's the "done" gates.
- **M1** — Drop any attachments — screenshots, mocks, source-of-truth sheets, Confluence page links, Loom recordings.
- **N1** — Reporter? Assignee? Sponsoring PM (if different)? SME if QA / BA has questions?

### Conditional MUST (asked only when type matches)

- **B1** *(WC, SC, MX — skip for BO and RD)* — Walk me through what happens today, step by step. Use numbered steps. Name the role doing each step.
- **E1-WC** *(WC only)* — What new stage(s) does this introduce? For each: name, owner role, entry trigger, exit trigger, SLA if any.
- **E1-BO** *(BO and MX)* — What is the ONE operator action that triggers the branches? For each branch (Case 1, Case 2, …): what does the operator see, what do they do, and if the system acts silently — how does the operator verify it acted?
- **E1-SC** *(SC only)* — What's the one form / field / toggle change? Show me the before-state and the after-state.
- **E1-RD** *(RD only)* — Show me the matrix as a table. Rows = ___, columns = ___, cells = the rule that applies. Drop or link the source-of-truth sheet.
- **E2** *(all types)* — For each step / case / row above: what's the SYSTEM CONSEQUENCE? Don't tell me what the operator does without telling me what the system does in response.
- **F1** *(RD MUST, others if matrix appears)* — Confirm the matrix is canonical and configurable: who can edit it without a code deploy?
- **H1** *(BO and MX MUST)* — Does the system fire any auto-comm (SMS / email / notification) as part of this change? If yes — to whom, when, with what content?
- **H2** *(BO and MX MUST)* — Does the system perform any silent action — auto-populate a field, auto-create a callback, auto-route a case — without any operator click?
- **I1** *(any type with time windows)* — What happens at the boundary of any time window? (E.g. cooling-off period, SLA expiry, NACH activation date.)

Total per type: **RD ≈ 9 questions**, **SC ≈ 13**, **BO ≈ 15**, **WC ≈ 16**, **MX ≈ 17**.

---

## 6. Output Verification Gates

Every draft is checked against these gates at Phase 7. A failed gate loops the skill back to Phase 4 or Phase 5.

### Universal gates (apply to every ticket, all types)

- [ ] **U1 Release-note line** is present at the very top, ≤ 20 words, operator-readable, no marketing voice.
- [ ] **U2 Intent paragraph** is 1 paragraph, plain English, no "we believe" / "should help" / passive voice.
- [ ] **U3 Every Logic rule has a CONSEQUENCE.** ("If X, then Y" or equivalent. Operator-action without system-consequence is rejected.)
- [ ] **U4 System strings** appear in `'single quotes'` and match panel UI verbatim where named.
- [ ] **U5 Acceptance Criteria honors the area-aware budget** — 3-5 bullets total for single-area tickets; 3-5 per area for multi-area tickets (max 4 areas, organised under `### Area Name` sub-headers). Each bullet is a "done" gate, not a re-listing of the flow. See `reference/PATTERN.md` §16.
- [ ] **U6 Out of scope** section is present (1-3 lines). EXCEPTION: RD-type tickets may omit IF the change is purely additive AND ticket includes a "purely additive" statement in §6 or §10 (LAP-2052 conditional pattern). See `reference/PATTERN.md` §15a.
- [ ] **U7 BA Open Considerations** lists at least one assumption with proposed default + impact if wrong. EXCEPTION: RD-type tickets may omit IF every assumption is closed AND ticket includes a "no open assumptions — sheet/matrix is canonical" statement in §1 or §10 (LAP-2052 conditional pattern). See `reference/PATTERN.md` §15.
- [ ] **U8 No ghost terms** — every term used has a glossary entry in the footer.
- [ ] **U9 Reporter + Assignee** named. Department-level contacts ("the BA team") rejected.
- [ ] **U10 No fabricated** percentages, fees, thresholds, RBI references not provided by the PM.

### Type-specific gates

For **WC**:
- [ ] WC1 Current Flow + Proposed Solution both numbered.
- [ ] WC2 Stages-in-the-system list at footer with owner per stage.
- [ ] WC3 Every named stage matches `knowledge-base/lap-stages.md` verbatim.

For **BO**:
- [ ] BO1 ONE trigger action explicitly named.
- [ ] BO2 Each Case has See / Do / Verify-if-silent triplet.
- [ ] BO3 Auto-comms flagged with manual-backup recommendation.
- [ ] BO4 Non-overridable rules explicitly named.

For **SC**:
- [ ] SC1 Current Flow shows the workaround being killed.
- [ ] SC2 Proposed Solution covers BOTH directions of any toggle (Yes→No AND No→Yes).
- [ ] SC3 Regression-guard AC bullet present (the unchanged path stays unchanged).

For **RD**:
- [ ] RD1 Matrix table present.
- [ ] RD2 Source-of-truth sheet linked or attached.
- [ ] RD3 Configurability statement present (can business edit without code deploy?).

For **MX**:
- [ ] MX1 Stages list AND Cases sub-sections both present.
- [ ] MX2 Cases live INSIDE one named stage (not floating).

If any gate fails after 2 redraft loops → skill ships a partial draft with `[BLOCKED — needs PM input: <gate>]` markers and asks PM whether to push partial / hold / discard.

Full gate enumeration with severities is in the skill author's design notes at `../lap-jira-uniform-ticket-design/deep-think/09-output-schema.md` (not loaded at runtime).

---

## 7. Output Destination — Markdown Only (v1.0.1 beta)

This version of the skill ships with markdown output only. Push-to-Jira is on the v1.1 roadmap.

**v1.0.1 beta — markdown delivery:**
- Skill outputs the full ticket body as fenced markdown in chat at Phase 8.
- Skill ALSO outputs the H1 title separately (Jira's "Summary" field is not part of the description, so it needs its own copy step).
- PM opens Jira → New Issue → LAP project → Story (or Epic per PM's classification) → pastes title into "Summary" → pastes body into "Description" → sets Reporter / Assignee / Sprint / Fix Version manually per the skill's footer hints.
- PM closes the loop: posts the resulting LAP-XXXX key back to the skill so it can be logged for downstream tools (e.g. the kissht-field-release-notes skill).

**v1.1 roadmap (not in this version):** Push-to-Jira via `createJiraIssue`. Implementation requires:
- The Atlassian MCP bundled into the plugin (currently the skill assumes the user has it connected separately).
- A scripted `createJiraIssue` wrapper that maps the skill's question answers (Phase 4 N1 = Reporter / Assignee, Phase 8 confirmation = Sprint / Fix Version) into the API call.
- A `tests/push-to-jira-roundtrip.md` smoke test to prove the round-trip stays consistent with the markdown path.
- Issue type inference from skill type (WC/MX → Story; SC/BO/RD → Story; Epic only when PM says "epic" at Phase 0).

Until v1.1 ships, every ticket is created manually by the PM after the skill produces the markdown body.

---

## 8. The Bundled Files (and what they contain)

```
lap-jira-uniform-ticket/
├── SKILL.md                                ← This file (workflow + question taxonomy + verification gates)
├── reference/
│   ├── PRINCIPLES.md                       ← The 8 content + 4 anti + 5 skill + 5 team principles
│   ├── PATTERN.md                          ← The 10-section uniform spine + per-type variations + dedup rule
│   ├── voice-and-style.md                  ← Plain English, no pseudocode, anti-pattern gallery
│   ├── external-patterns-research.md       ← The 7-phase research-analyst survey
│   └── external-patterns-synthesis.md      ← One-page punchline (adopt-3 reject-3)
├── templates/
│   ├── wc-workflow-change.md               ← Workflow Change skeleton
│   ├── bo-branching-outcome.md             ← Branching Outcome skeleton (See/Do/Verify per Case)
│   ├── sc-simple-change.md                 ← Simple Change skeleton (LAP-2039 shape)
│   ├── rd-reference-data.md                ← Reference Data skeleton (matrix-first)
│   └── mx-mixed.md                         ← Mixed skeleton (WC spine + embedded Cases)
├── knowledge-base/
│   ├── lap-glossary.md                     ← 18 roles + 36 acronyms + 28 system strings + concepts
│   ├── lap-stages.md                       ← 25 stages with owner, entry/exit triggers
│   ├── lap-roles.md                        ← Role roster with hierarchy diagram
│   └── lap-confluence-sources.md           ← Canonical Confluence pages with pageIds
├── examples/
│   ├── LAP-1812.md                         ← WC exemplar (E-Sign workflow)
│   ├── LAP-2039.md                         ← SC exemplar (user-authored gold standard)
│   ├── LAP-2046.md                         ← WC exemplar (PAN re-verification)
│   ├── LAP-2048.md                         ← MX exemplar (LSQ Video KYC + branches)
│   ├── LAP-2052.md                         ← RD exemplar (dropdown changes)
│   ├── LAP-2154.md                         ← BO exemplar (LSQ Renach handling)
│   └── LAP-2242.md                         ← RD exemplar (approval matrix)
├── tests/
│   ├── sc-from-lap-2039.md                 ← Smoke test: SC type from a LAP-2039-style PM input
│   ├── rd-from-lap-2242.md                 ← Smoke test: RD type from a LAP-2242-style PM input
│   └── bo-from-lap-2154.md                 ← Smoke test: BO type from a LAP-2154-style PM input
└── (skill author's design notes at sibling
   ../lap-jira-uniform-ticket-design/         ← deep-think/ + round1_archive/
                                                Quarantined OUT of the active skill folder.
                                                Not loaded at runtime; preserved for skill maintainer.)
```

---

## 9. Anti-Patterns (Things This Skill Refuses To Produce)

1. **Pseudocode, JSON schemas, SQL in the body.** PMs write specs, not code. (Forbidden: `def foo(...)`, ` => `, fenced code blocks > 5 lines. Allowed: short inline `'system_string'` quoting and matrix tables.)
2. **Restated rules across sections.** Logic says it once. AC doesn't re-list Logic. QA doesn't re-list AC.
3. **Bloated AC.** If AC has more than 5 bullets, the body is doing AC's job poorly. Loop back.
4. **"As a CCM, I want..." as MANDATORY.** Allowed when it adds clarity (LAP-1812 uses it well). Never required.
5. **Given-When-Then AC.** Bloats AC into a regression script. Use plain "done" bullets instead.
6. **PR-FAQ press-release format.** Wrong audience and register for an internal feature ticket.
7. **Marketing voice.** "We are excited to introduce...", "improved user experience", "delights the customer". Killed at Phase 7 gate U2.
8. **Department-level contacts.** "Contact the BA team" rejected at Phase 7 gate U9. Name humans.
9. **Ghost terms shipped without definition.** Killed at Phase 6 sweep + Phase 7 gate U8.
10. **Premature drafting.** Skill does not draft until every MUST question for the locked type is answered. There is no "fast path".
11. **Silent assumption substitution.** A 3-word PM answer triggers a follow-up, not a fill-in.
12. **Single-stage Case-based content for non-BO types.** A WC ticket cannot have free-floating Cases; if branches matter, classify as MX.

---

## 10. Quick Start

```
"Write a LAP ticket — Income Considered toggle on Credit PD form"
  → Phase 0: clarify destination (markdown / push) and seed type
  → Phase 1: auto-search Jira for "Income Considered Credit PD" + Confluence
  → Phase 2: PM picks LAP-2039 as RELATED (the predecessor ticket)
  → Phase 3: classified as SC (single field behavior change)
  → Phase 4: ~13 MUST questions covering current flow, proposed solution,
             QA scope, BA open considerations, AC, attachments
  → Phase 5: draft from templates/sc-simple-change.md
  → Phase 6: dedup + glossary sweep
  → Phase 7: 8 universal gates + 3 SC-specific gates
  → Phase 8: deliver as markdown OR push to LAP

"Turn this Slack message into a LAP ticket: [paste]"
  → Phase 0: same orientation questions
  → Phase 1: auto-search runs in parallel (PM's text gives keywords)
  → Phase 2: PM verifies context
  → Phase 3→8: standard flow

"Just give me the WC template — I'll fill it myself"
  → Skill hands over templates/wc-workflow-change.md as-is
  → Skill does NOT run the Socratic flow
  → Skill warns: "The template is a skeleton. The Socratic flow exists because
                  filling a skeleton without it usually misses BA Open Considerations
                  and ghost terms. If you skip the flow, run reference/PATTERN.md
                  through the gates manually before pushing to Jira."

"Write a LAP epic for the LSQ Renach migration"
  → Phase 3 likely classifies as MX or WC
  → Phase 4 mandates child-ticket enumeration (epics break down into stories)
  → Phase 8 push-to-Jira creates the Epic + offers to scaffold child stories
```

---

## 11. References to Sister Skills

This skill is intentionally narrow. For adjacent jobs, hand off:

| Need | Use |
|---|---|
| Operator-facing release note from a finished LAP ticket | `kissht-field-release-notes` (downstream consumer of every ticket from this skill) |
| Multi-ticket release bundle | `kissht-field-release-notes` Phase 1 grouping logic |
| Word document export of a ticket | `docx` skill |
| PRD-to-tickets decomposition | `harsha-custom-skills:decompose-prd` |
| Bug ticket (different pattern) | Continue with existing process; bug-pattern skill not currently planned |
| Sprint planning / roadmap | `pm-execution:sprint-plan` |

---

## 12. Why This Skill Exists at All (one paragraph for skeptics)

The team already writes good LAP tickets sometimes. LAP-2039, LAP-2242, LAP-2052 prove it. The problem is that "sometimes" is not a strategy. New PMs onboard without canon. Senior PMs drift over time. The release-notes skill downstream needs uniform input and currently doesn't get it. This skill is the team's contract with itself: every LAP ticket, every PM, runs the same Socratic flow once, and the output meets the standard the team's strongest tickets already meet. The cost is 8-30 minutes of PM time per ticket. The savings are: zero re-interviews from BA / QA / Dev, zero release-note rewrites, zero new-PM onboarding cliff. After 4 weeks, measure abandonment rate. If PMs are skipping this skill for trivial tickets, revisit the no-fast-path decision. Until then: hold the line.

---

## 13. Change Log

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-05-14 | Initial release. 5 ticket types (WC/BO/SC/RD/MX). 8-phase Socratic flow. Auto-search Jira+Confluence on every run. Ghost terms block until defined. Output destination PM-picks per session. 6 LAP exemplars canonical. 3 external borrowings (GitLab release-note line, Shape Up Out-of-scope, Google design doc Alternatives considered). 3 patterns rejected (Given-When-Then AC, mandatory Connextra, PR-FAQ). Glossary built from kissht-field-release-notes references + LAP exemplars. Built using deep-thinker + research-analyst + parallel-builder methodology. |
| 1.0.1 | 2026-05-14 | **v1.0.1 markdown-only beta — five reviewer risks addressed before first marketplace push.** (1) **Overpromise removed.** Frontmatter description updated to make Atlassian-MCP integration explicitly conditional ("if Atlassian MCP connected, otherwise asks PM directly"). Phase 0 D2 question (markdown vs push-to-Jira) removed. Phase 1 (auto-search) made conditional on MCP availability. Phase 8 (deliver) is markdown-only in this version; push-to-Jira deferred to v1.1 with implementation requirements documented in §7. (2) **Inconsistencies fixed.** LAP-2046 was tagged BO in PRINCIPLES.md and WC in SKILL.md — reconciled to WC (with matrix) across all files. LAP-2048 was tagged WC in PRINCIPLES.md — reconciled to MX. LAP-2154 added to PRINCIPLES.md exemplar table (was already in SKILL.md). All template frontmatter bumped from v1.0.0 to v1.0.1. BO template TIPs updated to reference LAP-2154 (canonical BO) primarily and LAP-2046 (WC with internal Cases) as structural cross-reference. SF (Simple Feature) round-1 terminology no longer in active skill (archives moved out — see #3 below). (3) **Quarantined heavy context.** `.deep-think/` (10 design notes) and `round1_archive/` moved OUT of the skill folder to a sibling `../lap-jira-uniform-ticket-design/` location. Active skill folder dropped from 5,312 lines / 32 files to 3,757 lines / 26 files. SKILL.md cross-references to `.deep-think/` paths updated to point to the sibling location with a "not loaded at runtime" note. (4) **TODO markers quarantined.** Created `knowledge-base/pending-validation.md` for the 4 outstanding uncertainties (RM vs SM distinctness, Auditor First/Second, Paras Arora's accountId, Veriphy LAP-flow status). Inline TODO comments removed from canonical KB files; replaced with "see pending-validation.md §VN" pointers. lap-glossary.md "How to use" preamble updated: every entry in canonical KB is now asserted as canonical; uncertainties live separately in pending-validation.md. (5) **Template footer headers aligned to PATTERN.md contract verbatim.** All 5 templates: `**System strings referenced** (verbatim):` → `**System strings referenced in this ticket** (verbatim, for downstream use):`; `**Glossary used:**` → `**Glossary used in this ticket** (auto-generated):`. Header text is the contract per PATTERN.md mapping section — release-notes parser depends on these exact strings. (6) **Three smoke tests added** under `tests/`: `sc-from-lap-2039.md`, `rd-from-lap-2242.md`, `bo-from-lap-2154.md`. Each test specifies PM input, Phase 0-8 expected behaviour, validation gates that must pass, and a release-notes-extractability checklist for downstream consumption. To be run after first marketplace install and after any change to SKILL.md §5 (question taxonomy) or `kissht-field-release-notes` Pattern A/B extraction. |
