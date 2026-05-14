# LAP Confluence Sources — Cited Reference Set

> The Confluence pages worth consulting when writing a LAP Jira ticket, PRD, or release note. Curated from a sweep across kissht.atlassian.net Confluence and the kissht-field-release-notes sister-skill knowledge base.
>
> Cloud ID: `76a6058f-c3ec-4764-8c15-e7d4a3e8aae2`
> Tenant URL: `https://kissht.atlassian.net/wiki`
> URL pattern: `https://kissht.atlassian.net/wiki/spaces/<spaceKey>/pages/<pageId>`
>
> Cross-references: term definitions in [`lap-glossary.md`](./lap-glossary.md); stage list in [`lap-stages.md`](./lap-stages.md); role roster in [`lap-roles.md`](./lap-roles.md).

---

## Tier 1 — Always Consult

| Page ID | Title | Author | One-line content summary | Last-known-canonical-for |
|---|---|---|---|---|
| **1088716805** | LOAN ORIGINATION SYSTEM - LAP | Vishaw Kashyap | Master LAP LOS page; full stage list, programme matrix, role roster. | Stages, role roster, programme matrix |
| **1089142840** | Fresh Loan \| NORMAL PROGRAM \| Is Waiver Eligible? is NO | Vishaw Kashyap | Normal-non-Waiver path spec — the most common Fresh Loan path. | Normal-non-Waiver flow |
| **900431885** | LOS for LAP (PRD) | Vatsala S | Foundational PRD covering Send-Back, Query, CAM, Sanction Conditions, Deviations, PDD definitions. | Send-Back, Query, CAM, Deviations, PDD |

---

## Tier 2 — Stage-Specific Deep Dives

| Page ID | Title | Author | One-line content summary | Last-known-canonical-for |
|---|---|---|---|---|
| **1089568836** | Sales PD Completed \| CCPA | Vishaw Kashyap | Sales PD Completed stage spec — tabs (Applicant, Mortgage, Documents, CAM, Tasks, Query, CPA Check), Submit App Check form, Bureau Pull, CPA Checklist. | `Sales PD Completed` stage |
| **1089568947** | CPA Verified \| BCM | Vishaw Kashyap | CPA Verified stage spec — BCM auto-assignment, orphan-branch fallback. | `CPA Verified` stage |
| **1089569179** | Third Party Triggers Pending | Harshavardhan Bailur | Third Party Trigger Pending stage spec — BCPA pre-trigger of Legal/Technical/RCU/FI. | `Third Party Trigger Pending` stage |
| **1093927112** | In-principle Approval Pending \| CCM or SCM (DRAFT) | Vishaw Kashyap | DRAFT — IPA stage spec for CCM / SCM. Treat cautiously; not yet canonical. | `In-Principle Approval Pending` stage (draft) |

---

## Tier 3 — Cross-Cutting Modules

| Page ID | Title | Author | One-line content summary | Last-known-canonical-for |
|---|---|---|---|---|
| **1101660180** | LAP Query Module — User Guide & User Journey (PRIVATE DRAFT) | Harshavardhan Bailur | Query / Send-Back / notification module spec; closest existing voice exemplar — read it before writing your first LAP doc. | Query module, Send-Back routing, voice exemplar |
| **1020199073** | Initial PRD: Concurrent / Internal Top-Up LAP Loan Product | Shweta I | Top-Up / BT+Top-Up specific changes. | Top-Up product, BT+Top-Up |
| **978288872** | LOS Lead-gen Final PRD | Shweta I | Leadgen-stage changes (S1-S4 of the journey). | Lead Initiation, Sourcing |
| **896401462** | LAP Inhouse CRM: Leadgen | Roshni Singh | SM CRM context for leadgen. | SM CRM, leadgen |

---

## Tier 4 — Adjacent / Domain-Wide

| Page ID | Title | Author | One-line content summary | Last-known-canonical-for |
|---|---|---|---|---|
| **906362889** | LAP via APP | Gaurav Kumar | Mobile app surface changes. | Mobile app |
| **878281062** | LAP – Loan Against Property (product overview) | Keerthika R | Product context for non-LAP audiences. | LAP product overview |
| **1096024234** | Format Release Notes (template) | (Kissht-wide) | Cross-product release-note template. | Release-note structure |
| **1101922394** | User Test Scenarios for PAN Re-verification in PL and LAP | Shweta I | Test scenarios for PAN re-verification (relevant to LAP-2046). | PAN re-verification testing |
| **1106641211** | 01 – Collections Core & Sync | Sandeep Kadam | Collections module context (post-disbursement). | Collections |
| **1104773723** | LOS Functional Specification — Overview | Sandeep Kadam | Cross-product LOS context (PL/BL/LAP/CC). | Cross-product LOS |
| **1105559712** | Glossary (LOS space) | Sandeep Kadam | Domain term definitions across LOS. | Cross-product term definitions |

---

## Tier 5 — Personal Workspaces

Personal Confluence spaces hold private working drafts. Cite cautiously; double-check space-permission settings before relying on them as public source-of-truth.

| Author | Space key | Notable contents |
|---|---|---|
| Vishaw Kashyap | `~712020bc942d513dd54fe789341fe9cf7dbe61` | Canonical LAP-LOS workspace. Holds master page (1088716805) + 4 stage children. |
| Harshavardhan Bailur | `~712020d14f4537151b4d03a774c0f2ab2a3e75` | LAP Query Module guide (1101660180), Third Party Triggers stage spec (1089569179). |
| Shweta Iyengar | `~712020b616e54a5a85414487cf407d5e251dbc` | Internal Top-Up PRD (1020199073), Lead-gen Final PRD (978288872). |
| Paras Arora | <!-- TODO: confirm with PM — account ID required for queries --> | Co-named on LAP Inhouse CRM Leadgen (896401462). |

---

## Confluence-Side Author Caveats

- **`creator.fullname` CQL field returns 400** on the kissht.atlassian.net tenant. Solution: use `lookupJiraAccountId` to get the accountId, then `creator = "<accountId>"`.
- **Personal spaces are restricted by default.** Verify space-permission settings before treating personal pages as canonical.
- **Drafts** (status = "draft") are common in personal spaces. Don't treat them as canonical.

---

## Related Jira Spaces

While not Confluence, these Jira projects often hold complementary context:

| Project key | What's there |
|---|---|
| **LAP** | Primary source — all LAP stories, bugs, epics. |
| **LMS** | Loan Management System (post-disbursement). |
| **LOS** | Cross-product LOS (PL/BL/LAP/CC integrations). |
| **Conexo** | Lender / partner integrations (CS, ABCL, etc.). |
| **PAY** | Payments / settlements. |
| **COL** | Collections. |
| **UI** | UW Integrations (bureau, location intelligence, third-party). |

---

## Version

> **Confluence sources KB version 1.0 — 2026-05-14**
> Sources: kissht-field-release-notes SKILL.md (sister skill v1.1.1), original `lap-confluence-sources.md` from sister-skill knowledge base.
