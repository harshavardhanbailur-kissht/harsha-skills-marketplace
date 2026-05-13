# Source of Truth — Where To Look

> Canonical Confluence pages, Jira projects, and code sources to consult when writing or verifying a release note.

---

## Atlassian Cloud

| Item | Value |
|---|---|
| Cloud ID | `76a6058f-c3ec-4764-8c15-e7d4a3e8aae2` |
| Domain | `kissht.atlassian.net` |
| Jira project (LAP LOS) | key = `LAP` |
| Jira project (Conexo) | key = `Conexo` (LMS-side, mostly out of LAP scope) |
| Jira project (LMS) | key = `LMS` (loan management — post-LOS) |
| Jira project (LOS) | key = `LOS` (LMS / cross-product LOS) |

For LAP release notes, query `project = LAP`.

---

## Canonical Confluence Pages

### Tier 1 — Always consult

| Page ID | Title | Why |
|---|---|---|
| **1088716805** | LOAN ORIGINATION SYSTEM - LAP | Master stage list with owners, programme matrix, role roster |
| **1089142840** | Fresh Loan \| NORMAL PROGRAM \| Is Waiver Eligible? is NO | The live "normal, no-waiver" path written stage-by-stage |
| **900431885** | LOS for LAP (PRD) | Original PRD: maker/checker/authoriser, Send-Back, Queries, CAM, Sanction Conditions, Deviations, PDD |

### Tier 2 — Consult when relevant

| Page ID | Title | When |
|---|---|---|
| **1089568836** | Sales PD Completed \| CCPA | Changes within Sales PD Completed stage |
| **1089568947** | CPA Verified \| BCM | Changes within CPA Verified stage |
| **1089569179** | Third Party Triggers Pending | Changes within Third Party Trigger stage |
| **1101660180** | LAP Query Module — User Guide & User Journey | Query / Send-Back changes; voice exemplar |
| **1020199073** | Initial PRD: Concurrent / Internal Top-Up LAP | Top-Up specific |
| **978288872** | LOS Lead-gen Final PRD | Leadgen-stage changes |
| **896401462** | LAP Inhouse CRM: Leadgen | Leadgen / SM CRM context |
| **906362889** | LAP via APP | Mobile app surface |
| **878281062** | LAP – Loan Against Property (product overview) | Product context for non-LAP audiences |

### Tier 3 — Cross-domain

| Page | When |
|---|---|
| `Format Release Notes` template (1096024234) | Compatibility check — Kissht's de-facto release-note shape |
| LOS Functional Spec set (LOS space) | Cross-product LOS context (PL/BL/LAP/CC) |
| LMS Functional Spec set (LMS space) | Post-disbursement / loan lifecycle context |

---

## Confluence Spaces By Author

When a ticket references a feature whose PM owner has a personal Confluence space, that space often has the most up-to-date / detailed spec. Personal spaces:

| Author | Space key |
|---|---|
| Vishaw Kashyap | `~712020bc942d513dd54fe789341fe9cf7dbe61` (canonical LAP-LOS workspace) |
| Harshavardhan | `~712020d14f4537151b4d03a774c0f2ab2a3e75` |
| Shweta Iyengar | `~712020b616e54a5a85414487cf407d5e251dbc` |

Personal spaces hold private working drafts. Cite cautiously — content may not be official.

---

## Jira Query Patterns

### Find the most recent shippable LAP feature

```
project = LAP AND status = "LIVE"
ORDER BY resolutiondate DESC, updated DESC
```

Caveat: many LAP tickets transition to `LIVE` without setting `resolutiondate` (resolution field is often blank). Order by `updated` as the secondary sort.

### Find tickets under a specific epic

```
project = LAP AND parent = LAP-XXXX
ORDER BY created ASC
```

### Find tickets touching a specific stage

```
project = LAP AND (text ~ "<stage name>" OR summary ~ "<stage name>")
```

### Find tickets by reporter (PM)

```
project = LAP AND reporter = "<accountId>"
ORDER BY updated DESC
```

`accountId` is required — display names like `"Shweta I"` or `"Paras Arora"` return 400 on this tenant. Use `lookupJiraAccountId` first.

### Find QA-passed tickets ready for release

```
project = LAP AND labels = "qa_done" AND status != "LIVE"
ORDER BY updated DESC
```

---

## Confluence CQL Patterns

### Find LAP-related pages updated recently

```
text ~ "LAP" AND text ~ "BCM" AND type = page AND lastModified > "2026-01-01"
ORDER BY lastModified DESC
```

### Find pages by a specific author

```
creator = "<accountId>" AND type = page
```

(Display-name CQL fails on this tenant — need accountId.)

### Find pages under the canonical LAP LOS space

```
space = "~712020bc942d513dd54fe789341fe9cf7dbe61" AND type = page
```

### Find release-note-shaped templates

```
title ~ "release note" AND type = page
ORDER BY lastModified DESC
```

---

## Existing Sister Skills To Cross-Reference

| Skill | Location | Used for |
|---|---|---|
| `kissht-ba-release-notes-mastery` | `~/Downloads/claude skills/kissht-ba-release-notes-mastery/` | BA-deep impact analysis (7-lens decomposition). Hand off if the user wants BA-only depth. |
| `lap-intelligence-hub-v2` | `~/Downloads/claude skills/lap-intelligence-hub-v2/` | Real-time LAP Jira knowledge base (1839+ tickets, 13 themes). Pull from here for theme detection. |
| `ai-release-notes-research` | `~/Downloads/claude skills/ai-release-notes-research/` | Academic foundation (SmartNote, DeepRelease patterns). |
| `lap-documenter` | `~/Downloads/claude skills/lap-documenter/` | Used to synthesise the LAP Query Module page from 140 tickets — useful as a precedent. |
| `lap-jira-uniform-ticket` | `~/Downloads/claude skills/lap-jira-uniform-ticket/` | Standardising Jira ticket descriptions. Useful when a ticket is too sparse for a release note. |
| `lap-policies-research` | `~/Downloads/claude skills/lap-policies-research/` | Credit policy / RBI compliance lookups. |

---

## Out-Of-Band Sources

When Confluence and Jira don't cover the change:

| Source | When |
|---|---|
| **G-Chat / WhatsApp screenshots** of internal updates | Often the feature was communicated informally before being documented. Ask the reporter for the original update. |
| **Loom recordings** | Some LAP features are demo'd via Loom before docs catch up. Ask if a recording exists. |
| **Reporter / assignee comment** | If the ticket is sparse, comment on the ticket asking the reporter for a 1-paragraph operator-facing summary. |
| **Sprint demo deck / standup notes** | Sometimes the only authoritative source for what a feature does at handoff. |

Never invent. If a source isn't authoritative, leave the rule out of the release note and flag the gap to the user.

---

## Update Protocol

When you find a new canonical page or a new query pattern that's useful:

1. Add it to the relevant section above with a one-line "When" justification.
2. Cite the page ID or query.
3. Increment the footer.

> **Source-of-truth version 1.0 — 2026-05-02**
