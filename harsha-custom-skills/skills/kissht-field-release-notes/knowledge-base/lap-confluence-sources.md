# LAP Confluence Sources — Cited Reference Set

> The Confluence pages worth consulting when writing a LAP field release note. Curated from a sweep across the kissht.atlassian.net Confluence on 2026-05-02. Each entry has a one-line "When to consult" guide.
>
> Cloud ID: `76a6058f-c3ec-4764-8c15-e7d4a3e8aae2`
> Tenant URL: `https://kissht.atlassian.net/wiki`

---

## Tier 1 — Always Consult

| Page ID | Title | Author | When to consult |
|---|---|---|---|
| **1088716805** | LOAN ORIGINATION SYSTEM - LAP | Vishaw Kashyap | EVERY release note. Master stage list, programme matrix, role roster. |
| **1089142840** | Fresh Loan \| NORMAL PROGRAM \| Is Waiver Eligible? is NO | Vishaw Kashyap | Whenever a feature affects the Normal-non-Waiver path (most common). |
| **900431885** | LOS for LAP (PRD) | Vatsala S | For Send-Back, Query, CAM, Sanction Conditions, Deviations, PDD definitions. |

---

## Tier 2 — Stage-Specific Deep Dives

| Page ID | Title | Author | When to consult |
|---|---|---|---|
| **1089568836** | Sales PD Completed \| CCPA | Vishaw Kashyap | Changes to Sales PD Completed: tabs (Applicant, Mortgage, Documents, CAM, Tasks, Query, CPA Check), Submit App Check form, Bureau Pull, CPA Checklist. |
| **1089568947** | CPA Verified \| BCM | Vishaw Kashyap | Changes to CPA Verified: BCM auto-assignment, orphan-branch fallback. |
| **1089569179** | Third Party Triggers Pending | Harshavardhan Bailur | Changes to Third Party Trigger Pending: BCPA pre-trigger of Legal/Technical/RCU/FI. |
| **1093927112** | In-principle Approval Pending \| CCM or SCM (DRAFT) | Vishaw Kashyap | DRAFT — IPA stage spec for CCM / SCM. Use cautiously; not yet canonical. |

---

## Tier 3 — Cross-Cutting Modules

| Page ID | Title | Author | When to consult |
|---|---|---|---|
| **1101660180** | LAP Query Module — User Guide & User Journey (PRIVATE DRAFT) | Harshavardhan Bailur | Query / Send-Back / notification changes. Also the closest existing voice exemplar — read it before writing your first release note. |
| **1020199073** | Initial PRD: Concurrent / Internal Top-Up LAP Loan Product | Shweta I | Top-Up / BT+Topup specific changes. |
| **978288872** | LOS Lead-gen Final PRD | Shweta I | Leadgen-stage changes (S1-S4 of the journey). |
| **896401462** | LAP Inhouse CRM: Leadgen | Roshni Singh | SM CRM context for leadgen. |

---

## Tier 4 — Adjacent / Domain-Wide

| Page ID | Title | Author | When to consult |
|---|---|---|---|
| **906362889** | LAP via APP | Gaurav Kumar | Mobile app surface changes. |
| **878281062** | LAP – Loan Against Property (product overview) | Keerthika R | Product context for non-LAP audiences (rare). |
| **1096024234** | Format Release Notes (template) | (Kissht-wide) | Cross-check that your output is structurally compatible with Kissht's de-facto release-note shape. |
| **1101922394** | User Test Scenarios for PAN Re-verification in PL and LAP | Shweta I | When a feature touches PAN re-verification or PL→LAP migration. |
| **1106641211** | 01 – Collections Core & Sync | Sandeep Kadam | Collections module context (post-disbursement). |
| **1104773723** | LOS Functional Specification — Overview | Sandeep Kadam | Cross-product LOS context (PL/BL/LAP/CC). |
| **1105559712** | Glossary (LOS space) | Sandeep Kadam | Domain term definitions across LOS. |

---

## Tier 5 — Personal Workspaces

Personal Confluence spaces hold private working drafts. Cite cautiously.

| Author | Space key | Notable contents |
|---|---|---|
| Vishaw Kashyap | `~712020bc942d513dd54fe789341fe9cf7dbe61` | The CANONICAL LAP-LOS workspace. Holds the master page (1088716805) + 4 stage children. |
| Harshavardhan | `~712020d14f4537151b4d03a774c0f2ab2a3e75` | LAP Query Module guide (1101660180), Third Party Triggers stage spec (1089569179). |
| Shweta Iyengar | `~712020b616e54a5a85414487cf407d5e251dbc` | Internal Top-Up PRD (1020199073), Lead-gen Final PRD (978288872). |
| Paras Arora | (account ID required for queries — display name search 400s) | LAP Inhouse CRM Leadgen (co-named on 896401462). |

---

## Confluence-Side Author Caveats

- **`creator.fullname` CQL field returns 400** on the kissht.atlassian.net tenant for both single-name and full-name queries. Solution: use `lookupJiraAccountId` to get the accountId, then `creator = "<accountId>"`.
- **Personal spaces are restricted by default.** When citing a personal space page, double-check the space-permission settings before relying on it as a public source-of-truth.
- **Drafts** (status = "draft") are common in personal spaces. Don't treat them as canonical.

---

## Related Jira Spaces

While not Confluence, these Jira projects often hold complementary context:

| Project key | What's there |
|---|---|
| **LAP** | All LAP stories, bugs, epics — primary source for release-note generation. |
| **LMS** | Loan Management System (post-disbursement). |
| **LOS** | Cross-product LOS (PL/BL/LAP/CC integrations). |
| **Conexo** | Lender / partner integrations (CS, ABCL, etc.). |
| **PAY** | Payments / settlements. |
| **COL** | Collections. |
| **UI** | UW Integrations (bureau, location intelligence, third-party). |

When a LAP release note touches a non-LAP project (e.g. a bureau integration that affects LAP only at the panel-display level), the integration spec usually lives in `UI` or `LMS`.

---

## Version

> **Confluence sources KB version 1.0 — 2026-05-02**
> Sweep methodology: CQL searches + descendants of pageId 1088716805 + author-scoped digests.
