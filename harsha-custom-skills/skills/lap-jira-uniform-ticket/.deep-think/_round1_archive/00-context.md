# 00 — Context, Constraints, Exemplar Summary

## What I am optimising for

The lap-jira-uniform-ticket skill must produce Jira ticket bodies that are **structurally uniform across the entire Kissht LAP team** so that one downstream skill (`kissht-field-release-notes`) can mechanically convert any LAP ticket into either a Pattern A (Workflow Change / Relook) or Pattern B (Branching Outcome / Renach) release note without re-asking the PM what was meant. Uniformity is the goal; literary quality is a side effect.

The skill is Socratic in the cowork-think-with-me lineage: it resists ticket production until the PM has answered enough questions to fill every slot in the structure. It is NOT a fast-path — every PM, every ticket, same flow.

The three success conditions I am designing for:

1. **Downstream feedability** — every ticket the skill produces can be ingested by `kissht-field-release-notes` Phase 2 ("Decompose the source") without ambiguity. Specifically: stages are named, owners are named, branches are enumerated, system strings are quoted, consequences are attached to rules.
2. **Cross-PM uniformity** — a Paras ticket, a Vishaw ticket, a Mohini ticket, a Harsha ticket all look like they came from the same hand. No per-PM calibration, no "style preference." The skill enforces, the PM does not.
3. **Operator-grade content** — the field BCM/CCM/NCM/BCPA/Sales RM at 9am opens the resulting release note and can act on it. That requires the source ticket to already contain the operator-actionable detail; the skill's job is to extract that detail from the PM's head.

## Locked constraints (do not redesign)

1. **8 content principles**: intent paragraph / current-vs-proposed / numbered logic with consequences / tables for matrices / named QA Scope / named BA Scope / lean AC / sources at bottom.
2. **Anti-principles**: no repetition, no pseudocode, no bloated AC, no assumed context.
3. **Socratic method** modelled on cowork-think-with-me — one question at a time, no hedging, write to files as we go.
4. **Step 1 is auto-search** of Jira + Confluence for related tickets; **Step 2 is verify-with-PM** that the related-ticket set is right.
5. **No fast-path** — same flow for the 5-line dropdown change as for the multi-stakeholder workflow rebuild.
6. **Both output destinations** — markdown file OR push directly to Jira via `editJiraIssue`. PM picks per session.
7. **Glossary reuse** — the skill loads `references/lap-glossary.md` from kissht-field-release-notes and may extend it; it does NOT re-build the vocabulary.
8. **No per-PM calibration** — the skill behaves identically for every team member.

## The 6 LAP exemplars — what each one teaches the skill

| Ticket | Type | Core lesson the skill must enforce |
|---|---|---|
| **LAP-1812** (E-Sign Phase 2, Story, READY FOR RELEASE) | Workflow / process change with multiple actors | Primary actor + secondary actors named upfront; preconditions block; numbered functional flow with sub-steps (1.1, 1.2 …); explicit Acceptance Criteria block organised by area; SMS/copy verbatim. Long but never repeats. |
| **LAP-2039** (Income Considered move, Story, In QA — user's own gold standard) | Single-form behaviour change with bidirectional toggle | Three-block spine: **Problem** → **Current flow we want to fix** (numbered, painful) → **Proposed solution** (numbered, with consequences). **QA Scope** named explicitly. **Open Considerations for BA** named explicitly with each item carrying a Proposal + Impact. |
| **LAP-2046** (PAN re-verification ETB, Story, READY FOR RELEASE) | Branching backend rule | Section 1 Problem → Section 2 Proposed Solution with **Step 1 / Step 2 / Case 1 / Case 2** → Section 3 Applicability matrix → Section 4 Exception → Section 5 Summary table. Every if-branch is a named Case. Every applicability dimension is enumerated. |
| **LAP-2048** (Video KYC, Epic, To Do) | Multi-act epic with time-windowed bypasses + soft/hard reject | Three numbered acts (Pre-initiation → Digital Journey → VCIP & Auditor Review). Each act has bold sub-steps. Time windows quoted (72h, 9y6mo). Soft-reject vs hard-reject behaviour spelled out as separate branches. |
| **LAP-2052** (Property dropdown sync, Story, LIVE) | Cross-system reference-data change with QA scope | Plain prose grouped by **system** (Leadgen / LOS) and within LOS by **journey** (Fresh Normal / SARAL / BT+Topup). Touchpoints enumerated by stage. **QA Scenarios** block. Source-of-truth sheet linked. |
| **LAP-2242** (Approval matrix, Story, In QA) | Routing rules with fallback chain + role glossary | Intent paragraph → **matrix table** (slab × IPA × FA × fallback) → **numbered Logic** with each rule carrying a consequence → **QA Testing Notes** → **Role Definitions for reference**. State-wise variants enumerated. Configurability called out. |

### Cross-cutting structural pattern across all 6

Every exemplar — across Story, Epic, single-form change, multi-actor workflow, dropdown sync, routing matrix — has the same backbone:

```
Intent (1 paragraph; what + why)
└─ Current state (numbered or prose, only when there's a flow to replace)
└─ Proposed change (numbered; every rule carries a consequence)
└─ Matrix table (when 2+ dimensions interact)
└─ QA Scope / QA Scenarios (named, bulleted)
└─ BA Open Considerations (named, with Proposal + Impact)
└─ Acceptance Criteria (lean, organised by area, never line-by-line repeating §3)
└─ Sources / attachments / parent / bug fan-out (footer)
```

Not every ticket uses every block. The skill must know which blocks are mandatory vs conditional vs forbidden for a given ticket type.

## What the downstream skill needs from us (the contract)

`kissht-field-release-notes` Phase 2 extracts these dimensions:

- What changed (functional delta) → from Proposed change
- Why it changed (business trigger) → from Intent paragraph
- Old flow / New flow → from Current state + Proposed change
- New stages introduced (named, with owners) → must be present verbatim
- New rules + consequences → from numbered logic
- Branch outcomes (each If-branch = a Case) → from Step/Case enumeration
- System strings (panel labels, status names, dropdowns, error messages) → quoted verbatim
- Affected roles (which personas behave differently) → named (CPA / BCM / CCM / NCM / BCPA / Sales RM / Auditor / Applicant)
- Edge cases / bypasses → enumerated
- Auto-comm events (SMS / email / notification) → quoted in body
- Silent system actions → flagged
- Non-overridable rules → flagged
- Contacts (humans, not departments) → reporter + assignee + named PMs

If our skill produces a ticket that's missing any of these, the release note skill has to ask the PM mid-flow — which defeats the whole pipeline. So the contract is: **we ask all of these upfront so the release-note skill never has to.**

## Failure modes I'm specifically designing against (the deep-thinker 6)

1. **Satisficing** — accepting the first viable phase architecture without testing alternatives.
2. **Memory loss** — the skill loses state between phases or between sessions.
3. **Single-path exploration** — only considering the obvious "ask question → fill template" loop.
4. **Confirmation bias** — assuming the 6 exemplars are representative when they may all be from the operator-facing change subset.
5. **Missed complexity** — under-handling multi-system, regulatory, hotfix, or cross-stakeholder tickets.
6. **Executor-unfriendly output** — producing architecture documents that the next session (the synthesis pass) can't act on.

Each downstream file (01–08) explicitly addresses these where they apply.
