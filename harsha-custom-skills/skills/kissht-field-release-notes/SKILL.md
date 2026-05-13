---
name: kissht-field-release-notes
description: |
  Field-grade, operator-facing release notes for Kissht LAP / Loan Origination System.
  Produces ONE-document release notes in two patterns: Workflow Change (Relook) for
  tickets that introduce new stages, approval chains, or SLAs; and Branching Outcome
  (Renach) for tickets that change backend logic with multiple If-branches off one
  operator action. Two output shapes: multi-role (voice A) for the team, and single-role
  one-pager (voice B, plain English) for personal forwards. Built for the BCM / CCM /
  NCM / BCPA / Sales RM who reads the note at 9am before opening a case, not for exec
  dashboards. Every output is context-rich, stage-rich, role-aware, and grounded in
  real Jira ticket data and the canonical LAP Confluence space.
version: 1.1.1
author: Harshavardhan Bailur
replaces:
  - harsha-custom-skills:kissht-release-notes
references:
  - kissht-ba-release-notes-mastery (BA-deep impact analysis — call it for BA-only deep dives)
  - lap-intelligence-hub-v2 (Jira data backbone for ticket lookup)
  - ai-release-notes-research (academic foundation: SmartNote, DeepRelease)
triggers:
  - kissht release notes
  - LAP release note
  - field release note
  - operator release note
  - relook style release note
  - renach style release note
  - branching outcome release note
  - release note from jira ticket
  - what changed for BCM
  - what changed for CCM
  - what changed for BCPA
  - what changed for sales
  - LSQ release note
  - LOS release note
  - generate release note in Relook style
  - generate release note in Renach style
  - kissht field release note
  - release note for BCPA only
  - release note for BCM only
  - release note for CCM only
  - release note for NCM only
  - single-role release note
  - one-pager for BCPA
  - one-pager for BCM
  - WhatsApp-friendly release note
---

# Kissht Field Release Notes — Two Patterns, Two Voices

> **Canonical examples — multi-role**:
> - `examples/relook-approval-revamp.md` (Workflow Change pattern; the original artifact)
> - `examples/digilocker-journey-revamp.md` (Workflow Change pattern; LAP-2180 / 2181 / 2222 LIVE bundle)
> - `examples/lsq-renach-handling-multi-role.md` (Branching Outcome pattern; LAP-2154 LIVE)
>
> **Canonical example — single-role one-pager**:
> - `examples/lsq-renach-handling-bcpa-pager.md` (Branching Outcome pattern, BCPA-only, voice B)
>
> **Voice exemplar**: the LAP Query Module User Guide (Confluence pageId 1101660180). Read it before writing if you've never produced a Kissht operator-facing doc.

---

## 1. The Problem This Skill Solves

The existing Kissht release-note tools either:

1. Generate **N separate documents** for N stakeholders (PM, QA, Dev, Training, BA, Ops, Leadership) — too much overhead for a small change, and the field user (BCM, CCM, NCM, BCPA) reads zero of them.
2. Produce **deep BA impact analyses** (7-lens decomposition) — accurate but operationally unread, because nobody at 9am is reading a 12-page BA brief before processing a case.

Field users want one short, dense, operator-grade page that tells them: "here is what changed; here is what you do differently today."

This skill produces that page in two patterns and two output shapes.

---

## 2. The Two Patterns

The skill knows two patterns. Pick one before drafting based on the ticket type. The full detection heuristic is in `references/jira-to-release-note.md` §Pattern Detection.

### Pattern A — Workflow Change (Relook)

Use when the ticket introduces new stage(s), a new approval chain, an SLA with hard-reject, or a new mandatory action. Five beats, always in this order:

```
1. Title              "Release Note: <Feature Name>"
2. The new flow       ONE LINE arrow diagram + "Stages in the system" list
3. Key rules          Bulleted hard rules with consequences
4. What this          One H2 per role with imperative second-person bullets
   means for you
5. Contacts           Named humans + channel fallback
```

Canonical artifacts: `examples/relook-approval-revamp.md`, `examples/digilocker-journey-revamp.md`. Template: `templates/release-note-template.md`.

### Pattern B — Branching Outcome (Renach)

Use when the ticket changes backend logic with ≥2 If-branches off one operator action, and there is no new stage / no new SLA / no new approval chain. Six beats:

```
1. Title              "Release Note: <Feature Name>"
2. What this is about 2-4 sentences. Mental model. NOT a flow diagram.
3. What you do        Stage / Tab / Subtab / Form / Dropdown locator + ONE click.
4. What happens next  H2 per branch (Case 1, Case 2, Case 3). Each: what you see,
   — N cases          what you do, how to verify if silent.
5. After (optional)   Downstream consequences. Push to LMS, NACH validation, etc.
6. What this means    H2 per role (multi-role version), or absent (single-role pager).
   for you (optional)
7. Contacts           Same as Pattern A.
```

Canonical artifact: `examples/lsq-renach-handling-multi-role.md`. Template: `templates/branching-outcome-template.md`.

### Pattern picker

```
count_if_branches = number of "If <X>" / "If the <Y>" / "If <Z>, then" clauses
                    found in the ticket description
has_new_stage    = any stage name in the ticket NOT in lap-stages.md
has_new_sla      = any phrase like "after N days" / "hard reject" / "auto-close" /
                   "expires" / "lost rejected"

if count_if_branches >= 2 AND not has_new_stage AND not has_new_sla:
    pattern = Branching Outcome
else:
    pattern = Workflow Change   # default
```

Mixed tickets (a workflow change with branching inside one stage) take Workflow Change as the spine and embed Case 1 / Case 2 / Case 3 sub-blocks inside the relevant role section. Do NOT split into two release notes.

### Non-negotiable properties (apply to both patterns)

- **Stage-rich (A) / Form-rich (B)**: every named stage / form / dropdown appears verbatim with owner.
- **Context-rich**: every rule carries a CONSEQUENCE.
- **System strings quoted verbatim**: `'Lost Rejected'`, `'Initiate E-Mandate Registration?'`, `'mandate_amount'` — match the panel UI exactly.
- **Imperative second-person voice in role / case sections**.
- **Real human contacts**, not departments.
- **No fabricated figures**: zero made-up percentages, fees, thresholds, or RBI references that aren't in source tickets.

If any of these is missing → the release note FAILS the verification gate (Phase 7 in §5) and must be rewritten.

---

## 3. Output Shape Selection

After picking the pattern, pick the output shape.

| User intent | Output shape | Voice |
|---|---|---|
| Default — release note for the team | **Multi-role document** (full role coverage) | A — operator-grade dense |
| "Release note for BCPA only" / "BCPA pager" / "WhatsApp-friendly" / "single-role release note" → field-role audience (BCPA, BOM, COM, BCM, CCM, NCM, Sales) | **Single-role one-pager** | **B-strict** — scenarios-first plain English; NO field references |
| "Release note for product support / tech ops / QA / SRE only" | **Single-role one-pager** | B — plain with quoted field references allowed |
| "Generate both" | Multi-role first → verify → derive single-role pager(s) | A then B / B-strict |

### Multi-role document

The default. Body is up to 600 words; voice is operator-grade dense (Voice A); role sections cover every persona affected by the change. Distributed via team channels (G-Chat, WhatsApp groups, in-panel announcements).

### Single-role one-pager

Derivative — generated FROM a verified multi-role document, not directly from the Jira ticket. This guarantees consistency.

Constraints:

- ≤ 500 body words (target ≤ 350; allow up to 500 if scenario clarity demands it)
- One role only — no "What this means for you" header (the document IS the role section)
- Voice **B-strict** for field-role audiences (BCPA / BOM / COM / BCM / CCM / NCM / Sales) — scenarios first, plain English, NO data field references, NO JSON keys, NO API/LMS jargon. Voice **B** for product-support / tech-ops / QA / SRE audiences.
- Standalone — reader does not need access to the multi-role version
- Three domain mini-patterns get surfaced explicitly:
  - **Auto-action + manual backup**: every auto-comm pairs with "send manually as backup".
  - **Silent action + plain-English acknowledgement**: when the system acts invisibly, do NOT ask the operator to verify by checking fields. Say "you don't have to check anything — the case will move forward on its own" or equivalent.
  - **Non-overridable backend rule in plain English**: "Do not try to fix it from the panel — there is nothing you can change from your end."

Closing structure (in scenario order): "The simple rule" (a 2-bullet TL;DR) + "If something looks wrong" (escalation guidance) + Contacts.

Canonical artifact: `examples/lsq-renach-handling-bcpa-pager.md` (Voice B-strict). Template: `templates/single-role-one-pager-template.md`. Voice rules: `references/voice-and-pattern.md` §Voice Levels (Voice A, B, B-strict).

---

## 4. When This Skill Activates

| User intent | What I do |
|---|---|
| "Write a release note for LAP-XXXX" | Phase 1→7 single-ticket pipeline; default to multi-role document; pattern auto-detected |
| "Write a release note for this Jira ticket" + paste | Phase 2→7 (skip Jira fetch) |
| "Write a release note in Relook style" | Force Workflow Change pattern |
| "Write a release note in Renach style" / "branching outcome release note" | Force Branching Outcome pattern |
| "Release note for BCPA only" / "BCPA pager" / "WhatsApp-friendly" | Single-role one-pager output shape, voice B |
| "Bundle these tickets into one release note" | Phase 1 + ticket-grouping logic, then 2→7 |
| "Update the release note — they changed the rule" | Edit pass, re-run verification |
| "Generate both — multi-role + BCPA pager" | Multi-role first → verify → derive pager |

**Out of scope** (explicit hand-offs):
- Multi-document multi-stakeholder release packages → use `kissht-ba-release-notes-mastery` (deeper BA lens) or write a wrapper.
- Sprint-level "everything that shipped" digests → that's a roadmap update, not a release note.
- Pure backend/integration tickets with no operator-facing change → skip; not all tickets deserve a field release note.

---

## 5. Workflow (Seven Phases)

### Phase 1 — Pick the Feature & Pull the Source

If the user names a feature or pastes a Jira ticket, skip to Phase 2. Otherwise:

1. Query Jira for recently LIVE LAP tickets:
   ```
   project = LAP AND status = "LIVE" ORDER BY resolutiondate DESC, updated DESC
   ```
2. **Filter for operator-facing changes only.** A ticket qualifies if its change is visible at the panel/UI/SOP level to a BCM, CCM, NCM, BCPA, CCPA, BOM, COM, NSM, SM, or BM. Backend refactors, integration plumbing, data hygiene, and bug fixes that don't change a screen or a rule do NOT qualify.
3. **Group related tickets** if a single feature spans multiple stories.
4. Confirm with the user before writing. Show 2-3 candidates if unclear.

Reference: `references/jira-to-release-note.md`.

### Phase 2 — Decompose the Source AND Pick the Pattern

Pull the ticket(s) via `getJiraIssue` with `responseContentFormat: "markdown"`. Extract:

- **What changed** (functional delta)
- **Why it changed** (business trigger)
- **Old flow / New flow** (Pattern A — becomes the arrow diagram)
- **New stages introduced** (named, with owners — Pattern A)
- **New rules** (each with its CONSEQUENCE)
- **Branch outcomes** (each If-branch — Pattern B becomes a Case sub-section)
- **System strings** (panel labels, status names, dropdown values, error messages — quote them verbatim)
- **Affected roles** (which personas behave differently)
- **Edge cases / bypasses** (e.g. "if CCM is unavailable, NCM can forward to themselves")
- **Auto-comm events** (SMS, email, notification — flag for manual-backup recommendation)
- **Silent system actions** (fields auto-populated, callbacks applied — list verification fields)
- **Non-overridable rules** ("the system decides" — flag for explicit "you cannot change this")
- **Contacts** (the humans who own the feature — usually reporter + assignee + named PMs)

For multi-ticket bundles, reconcile across tickets — pick the most authoritative description per dimension; flag contradictions.

**Pick the pattern** using the heuristic in §2 (Pattern picker). When in doubt, default to Workflow Change.

### Phase 3 — Establish Stage / Form / Role Vocabulary

Cross-check every stage name, tab/subtab/form name (Pattern B), and role name against `references/lap-glossary.md` and `knowledge-base/lap-stages.md`. If a name in the ticket is NOT in the glossary, either:

- Find it in the canonical LAP LOS Confluence page (1088716805) and add it to the glossary, OR
- Flag the gap to the user — don't silently invent or paraphrase.

This is the most common source of error in machine-written release notes. Spend the time.

### Phase 4 — Pick the Output Shape

Default to the multi-role document. Switch to single-role one-pager only on explicit user intent. See §3 for the picker.

### Phase 5 — Draft Using the Template

Use the right template for the (pattern, shape) combination:

| Pattern × Shape | Template |
|---|---|
| Workflow Change × Multi-role | `templates/release-note-template.md` |
| Branching Outcome × Multi-role | `templates/branching-outcome-template.md` |
| Workflow Change × Single-role | Derive from multi-role using Voice A → B conversion (`references/voice-and-pattern.md` §Voice Levels) |
| Branching Outcome × Single-role | `templates/single-role-one-pager-template.md` |

### Phase 6 — Compress

Word-count discipline:

| Pattern × Shape | Target |
|---|---|
| Workflow Change × Multi-role | 250–400 words (Relook is 287; gold standard) |
| Branching Outcome × Multi-role | 400–600 words |
| Single-role one-pager (any pattern) | ≤ 350 body words |
| Bundled multi-ticket (any pattern) | 600–900 words |

Cut:
- Every sentence that doesn't change behaviour.
- Every adjective that isn't load-bearing.
- Every "we believe" / "this should help" — those don't belong in a field release note.
- Every passive construction in the role / case sections — make them imperative.

### Phase 7 — Verification Gate

**Universal checks** (apply to every release note):

- [ ] **Title** is `Release Note: <Feature Name>` (multi-role) or `Release Note for <Role>s: <Feature Name>` (single-role pager) exactly.
- [ ] **Every rule** has a CONSEQUENCE attached (the word "if X, then Y" or equivalent).
- [ ] **System strings** appear in `'single quotes'` and match panel UI verbatim.
- [ ] **Imperative second person** in role / case sections.
- [ ] **Edge case bypasses** explicitly named.
- [ ] **Contacts block** has named humans, not departments.
- [ ] **No fabricated** percentages, fees, thresholds, RBI/RBI-Digital-Lending citations not in source ticket.
- [ ] **Stage / form / role names** match `knowledge-base/lap-stages.md` and `references/lap-glossary.md` verbatim.
- [ ] **Ticket traceability** — every claim maps to a Jira ticket key (kept in a hidden footer).

**Pattern-specific checks**:

For **Workflow Change**:
- [ ] **Flow line** is one arrow diagram, no commentary.
- [ ] **Every stage** in "Stages in the system" has owner in parens.

For **Branching Outcome**:
- [ ] **No flow arrow diagram** (it would be wrong here).
- [ ] **No "Stages in the system" list** (the stage is unchanged).
- [ ] **Each case** has: what you see + what you do + (if silent) how to verify.
- [ ] **Auto-actions paired with manual-backup** instructions.
- [ ] **Non-overridable rules** explicitly named ("you cannot change this from the panel").

**Shape-specific checks**:

For **Multi-role document** (any pattern):
- [ ] Word count ≤ 600 for single-feature note (or ≤ 900 for bundled multi-ticket).
- [ ] One H2 per role under "What this means for you".

For **Single-role one-pager** (any pattern):
- [ ] No "What this means for you" header — the document IS the role section.
- [ ] Voice B applied throughout (see `references/voice-and-pattern.md` §Voice Levels conversion checklist).
- [ ] Closing "Quick reminder" with 4–6 numbered imperative steps.
- [ ] Body word count ≤ 350.
- [ ] Standalone — does not reference the multi-role document.

If any item fails → loop back to the relevant phase. Do not deliver a partial release note.

---

## 6. The Bundled Files (and what they contain)

```
kissht-field-release-notes/
├── SKILL.md                                ← This file (workflow + verification gates)
├── references/
│   ├── voice-and-pattern.md                ← Voice rules + Voice Levels A and B + anti-patterns
│   ├── lap-glossary.md                     ← Domain terms, system strings, Renach vocab, buffer policy
│   ├── role-segmentation.md                ← "What this means for you" patterns per persona
│   ├── jira-to-release-note.md             ← Mapping Jira fields → release-note beats + pattern detection
│   └── source-of-truth.md                  ← Canonical Confluence + Jira sources to consult
├── templates/
│   ├── release-note-template.md            ← Workflow Change × multi-role spine
│   ├── branching-outcome-template.md       ← Branching Outcome × multi-role spine
│   └── single-role-one-pager-template.md   ← Single-role one-pager (voice B) spine
├── examples/
│   ├── relook-approval-revamp.md           ← Workflow Change × multi-role (canonical)
│   ├── digilocker-journey-revamp.md        ← Workflow Change × multi-role (LAP-2180/2181/2222)
│   ├── lsq-renach-handling-multi-role.md   ← Branching Outcome × multi-role (LAP-2154)
│   └── lsq-renach-handling-bcpa-pager.md   ← Branching Outcome × single-role pager, voice B (LAP-2154)
├── knowledge-base/
│   ├── lap-stages.md                       ← All LAP stages with owners + Post Sanction substructure + Push-to-LMS contract
│   ├── lap-roles.md                        ← Role roster: BCM, CCM, NCM, BCPA, CCPA, BOM, COM, NSM, SM, BM
│   └── lap-confluence-sources.md           ← Canonical Confluence pages + IDs to consult
└── scripts/
    └── generate.py                         ← Optional helper — feeds Jira ticket data through the pipeline
```

---

## 7. Anti-Patterns (Things This Skill Refuses To Produce)

1. **Multi-document deliverables** — one release note per feature, not one per persona. (Use `kissht-ba-release-notes-mastery` if you need that. Single-role one-pager is a derivative artifact, not an alternative.)
2. **Marketing voice** — no "we are excited to announce", no "improved user experience", no superlatives.
3. **Backend-only release notes** — if the change is invisible to the operator, there should be no operator-facing release note.
4. **Confidence-tagged or hedged claims in the body** — operators need rules, not probabilities. If a claim is uncertain, leave it out and flag it to the author.
5. **Stage / role / form names that don't match the panel** — "approval queue" if the panel says "Approval Pending" is a bug.
6. **Department-level contacts** ("contact product team") — name humans.
7. **Long preambles** — the operator skips them. Open with the new flow (Pattern A) or the mental-model summary (Pattern B).
8. **Forcing Pattern A onto a Pattern B ticket** (or vice versa) — pick the right pattern using the heuristic in §2.
9. **Mixing voice levels within one document** — pick A or B per document; don't switch mid-way.
10. **Omitting manual-backup recommendations** when an auto-comm fires — at minimum flag it for the author to confirm.

---

## 8. Quick Start

```
"Write a release note for LAP-2180 in Relook style"
  → Pattern: Workflow Change (forced) | Shape: Multi-role
  → Phases 1→7 → deliver

"Write a release note for LAP-2154"
  → Pattern: Branching Outcome (auto-detected) | Shape: Multi-role
  → Phases 1→7 → deliver
  → Canonical artifact: examples/lsq-renach-handling-multi-role.md

"Write a release note for LAP-2154 just for BCPA"
  → Pattern: Branching Outcome (auto-detected) | Shape: Single-role one-pager
  → Phases 1→7 → multi-role first, then derive pager
  → Canonical artifact: examples/lsq-renach-handling-bcpa-pager.md

"Write a field release note for the DigiLocker journey revamp"
  → Pattern: Workflow Change | Shape: Multi-role
  → Phase 1 (group LAP-2180 + 2181 + 2222) → 2→7 → deliver

"Write me a release note in Relook style — pick the most recent shippable LAP feature"
  → Full Phase 1 (Jira query + filter + group + confirm) → 2→7 → deliver
```

---

## 9. References to Sister Skills

This skill is intentionally narrow. For adjacent jobs, hand off:

| Need | Use |
|---|---|
| Multi-stakeholder release package (PM/QA/Dev/Training/BA/Ops/Leadership) | `kissht-ba-release-notes-mastery` (BA-deep) — or build a wrapper |
| Real-time LAP Jira ticket search / theme detection / sync | `lap-intelligence-hub-v2` |
| Academic context on AI-powered release-note generation | `ai-release-notes-research` |
| Word document output | `docx` skill |
| Web app for browsing release notes | `web-artifacts-builder` or `frontend-blitz` |

---

## 10. Why This Skill Replaces `kissht-release-notes`

The previous `kissht-release-notes` skill produced a multi-document deliverable per feature. In practice:

- The PM read the PM guide.
- Nobody else read theirs.
- The BCMs / CCMs / NCMs got the change communicated via WhatsApp screenshots of an internal product update doc — which always looked like the Relook Approval Revamp release note.

This skill formalises what was already happening: ONE field-grade release note per feature for the team, plus optional derivative single-role one-pagers for personal forwards. Distributed via the existing operator channels (G-Chat, WhatsApp groups, in-panel announcements). Per-persona docs that nobody read are gone.

---

## 11. Change Log

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-05-02 | Initial release. Replaces `kissht-release-notes`. Built around the Relook Approval Revamp pattern. Canonical example written from LAP-2180/2181/2222. |
| 1.1.0 | 2026-05-04 | Adds **Branching Outcome** pattern (Renach), **Single-Role One-Pager** output shape, **Voice Levels A and B**, and three domain mini-patterns (auto-action + manual backup, silent action + verification checklist, non-overridable backend rule). New canonical examples: `lsq-renach-handling-multi-role.md`, `lsq-renach-handling-bcpa-pager.md` (both from LAP-2154). New templates: `branching-outcome-template.md`, `single-role-one-pager-template.md`. Glossary additions: Post Sanction substructure, E-Mandate / Renach vocabulary, mandate buffer policy. Knowledge-base additions: Push-to-LMS request body contract. Verification gate updated with pattern-specific and shape-specific checks. Backwards-compatible: every v1.0 call site still produces the Relook-pattern multi-role document by default. |
| 1.1.1 | 2026-05-04 | Adds **Voice B-strict** for field-role single-role pagers (BCPA / BOM / COM / BCM / CCM / NCM / Sales). B-strict drops all data field references, JSON keys, single-quoted system strings (except UI labels the operator clicks), backend formulas, API/LMS jargon, and verification-by-fields language. Replaces with scenarios in plain English and trust-the-system framing. Rewrites `examples/lsq-renach-handling-bcpa-pager.md` as the B-strict canonical from reviewer feedback ("scenarios in plain English without mention of any fields etc"). Updates `references/voice-and-pattern.md` with the B-strict spec, drop-list, keep-list, anti-patterns, and audience-routing table. Updates §3 Output Shape Selection to default field-role pagers to B-strict and tech-ops pagers to B. Backwards-compatible: existing multi-role documents and Voice-A/B pagers unchanged. |
