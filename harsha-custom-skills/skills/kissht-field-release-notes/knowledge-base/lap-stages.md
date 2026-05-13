# LAP Stages — Single Source of Truth

> Verified against Confluence page 1088716805 ("LOAN ORIGINATION SYSTEM - LAP", canonical, last modified 2026-04-02). Cross-referenced with Harshavardhan's LAP Query Module page (1101660180).
>
> When a release note references a stage, that stage's exact name and owner role MUST appear in the table below. If a new stage is introduced by a feature, add it here with citation.

---

## Open Status — The Active Pipeline

| # | Stage (verbatim from LSQ panel) | Owner role | Notes |
|---|---|---|---|
| 1 | `Sales PD Completed` | Central CPA (CCPA) | Entry to LOS. Tabs: Applicant, Mortgage, Documents, CAM, Tasks, Query, CPA Check. Exit via Submit App Check form. |
| 2 | `CPA Verified` | Branch Credit Manager (BCM) | Auto-assigned to BCM mapped to branch; orphan-branch fallback applies. |
| 3 | `In-Principle Approval Pending` | Cluster CM / State CM (CCM / SCM) | First credit approval. |
| 4 | `Third Party Trigger Pending` | Branch CPA (BCPA) | Pre-trigger of Legal / Technical / RCU / FI to compress TAT. |
| 5 | `Final Sanction Pending` | Branch Credit Manager (BCM) | BCM recommends sanction. |
| 6 | `Rate Approval Pending` | National Sales Manager (NSM) | Optional — only when rate deviation exists. |
| 7 | `Final Sanction Approval Pending` | National Credit Manager (NCM) | Final credit approval. |
| 8 | `Financier Review` | Financier Reviewer | Lender-side review. |
| 9 | `Post Sanction` | Branch CPA (BCPA) | Post-sanction obligations: PDD, NACH, mortgage. |
| 10 | `Branch Operations` | Branch Operation Manager (BOM) | Disbursement kit, NACH validation. |
| 11 | `Central Operations` | Central Operation Manager (COM) | Final ops check before disbursement. |
| 12 | `Reject Queue` | Branch Credit Manager (BCM) | Rejection landing — BCM owns recovery. |
| 13 | `Relook Approval Pending` | National Credit Manager (NCM) | Legacy single-step relook stage. |
| 14 | `Relook CCM Approval Pending` | Cluster CM / State CM (CCM / SCM) | First step in the Relook Revamp two-step approval flow. |
| 15 | `Relook NCM Approval Pending` | National Credit Manager (NCM) | Second step in the Relook Revamp two-step approval flow. |
| 16 | `Partially Disbursed` | Branch CPA (BCPA) | Multi-tranche cases mid-disbursement. |

---

## Won Status — Disbursed

| Stage | Owner role | Notes |
|---|---|---|
| `Disbursed Offline` | Branch Credit Manager (BCM) | Manual disbursement path. |
| `Disbursal Initiated` | Central Operation Manager (COM) | Mid-disbursement. |
| `Disbursed` | Central Operation Manager (COM) | Standard disbursement complete. |
| `Disbursed by Financier` | TBD per case | Co-lending / direct-financier disbursement. |
| `Cheque Initiated` | Central Operation Manager (COM) | Cheque-mode disbursement initiated. |
| `Cheque Disbursed` | Central Operation Manager (COM) | Cheque mode complete. |

---

## Lost Status

| Stage | Owner | Notes |
|---|---|---|
| `Rejected` | Last user to action the case | Soft rejection — closed without disbursal. |
| `Lost Rejected` (system-set) | — | Hard reject — set by system on Relook 30-day SLA breach (or equivalent). Recovery path: SM repunch only. |

---

## Saral 2.0 Variant Path

Saral 2.0 is a waiver-eligible Fresh Loan programme. It skips the BCM CPA-Verified step and replaces several owners with their Central counterparts:

```
Sales PD Completed (CCPA)
  → Final Sanction Pending (C-BCM)         ← skip CPA Verified
  → [Rate Approval Pending (NSM)? optional]
  → Final Sanction Approval Pending (NCM)
  → Post Sanction (C-BCM)                   ← C-BCM, not BCPA
  → Branch Operation (C-BOM)                ← C-BOM, not BOM
  → Central Operation (COPs)                ← COPs, not COM
  → Push to LMS
```

When writing a release note for a Saral-affecting feature, name the C-BCM / C-BOM / COPs roles explicitly. Don't assume BCM / BOM / COM — they don't apply.

Source: LAP-1665 (Saral 2.0 Positive & Send-Back flow, LIVE), LAP-1700 (Saral 2.0 query dropdown restrictions, TO DO).

---

## Stage Sub-States (Query Routing)

When a case is mid-stage but waiting on a sub-resolution, the Query Stage dropdown adds a sub-state suffix (post LAP-1903 rename):

| Stage value | Meaning |
|---|---|
| `Credit PD pending_sales` | Credit needs Sales to provide info before PD proceeds |
| `Credit PD pending_credit` | Credit owes itself something (intra-credit) |
| `Post PD pendencies` | After Credit PD, before sanction — extra asks |
| `Legal/Technical/RCU/FI pending_vendor` | Awaiting external verification vendor |
| `Legal/Technical/RCU/FI pending_sales` | Vendor blocked on Sales artefact |
| `Legal/Technical/RCU/FI pending_credit` | Internal credit clarification pending |
| `Final sanction pending_sales` | Pre-sanction ask on Sales |
| `Final sanction pending_credit` | Pre-sanction ask on Credit |
| `Disbursement Kit Released` | Kit out; query on post-disbursement items |
| `Disbursement Kit pending_sales` | Kit blocked on Sales artefact |
| `Disbursement Kit pending_credit` | Kit blocked on Credit artefact |

---

## Stage Adjacency (For Send-Back And Relook Routing)

When writing about a Send-Back, the destination stage matters. Common send-back routes:

| From | Send-back category | To | Side-effects |
|---|---|---|---|
| Third Party Trigger Pending | Rejection Post IPA | Final Sanction Pending (BCM) | No submit-to-source; mandatory remarks; recommendation flag preserved. |
| Final Sanction Pending | Legal/Technical Pending | Third Party Trigger Pending (BCPA) | Resets Act Recommendation Posted flag; recommendation deleted. |
| Final Sanction Pending | Change in Income | Sales | Blanks recommendation flag; recommendation deleted. |
| Final Sanction Approval Pending | Return Request | Final Sanction Pending (BCM) | Recommendation deleted; flags preserved. |
| Rate Approval Pending | Return Request | Final Sanction Pending (BCM) | Recommendation + loan parameter field deleted. |
| Post Sanction | Legal/Technical related | Third Party Trigger Pending (BCPA) | Recommendation activity preserved; params locked; new submit-to-source generated. |
| Post Sanction | Change in Offer / Rate | C-BCM (Saral) / BCM | Discards Fees & Charges (Legal/Tech + PF, NOT IMD); blanks recom flags. |

Source: LAP-1445 (Send-Back Enhancement), LAP Query Module page §12.

---

## Post Sanction — substructure (verified in LAP-2154)

The Post Sanction stage has tabs and subtabs that the BCPA navigates to action different post-sanction obligations. When a release note touches Post Sanction, name the tab + subtab + form explicitly so the BCPA can locate the trigger.

| Tab | Subtab | Notable forms |
|---|---|---|
| Post Sanction | Repayment Details | `Repayment & Disbursal Details Capture - v5` (contains `'Initiate E-Mandate Registration?'` dropdown — primary trigger for Renach logic) |
| Post Sanction | Disbursement Details | (TBD — extend on next ticket touching this) |

Source: LAP-2154 (LSQ Renach Handling, LIVE 2026-05).

---

## Push to LMS — request body contract additions

When a release note describes a change that flows through to LMS via the Push-to-LMS API request body, name the affected fields in the body. Currently known additions:

- `enach_reference_number` (added in LAP-2154) — LMS validates against the loan; rejection halts the case until reconciled.

When a release note touches Push-to-LMS validation, the BCPA / COM section MUST include the consequence of LMS rejection: "the case will not Push to LMS until the mandate (or other affected entity) is reconciled — escalate to product support."

---

## Update Protocol

1. New stage discovered in a Jira ticket: verify against panel UI; add to the right table; cite ticket.
2. Owner change: cite source; update; flag both old and new owners for backwards compatibility in legacy cases.
3. New send-back / query routing: add to the adjacency / sub-state table.

> **Stages KB version 1.1 — 2026-05-04**
> v1.1 adds Post Sanction substructure (tabs/subtabs/forms) and Push-to-LMS request body contract from LAP-2154.
> Sources: Confluence 1088716805 (master), 1101660180 (Query module), LAP-1445 / LAP-1665 / LAP-1903 / LAP-2180 / LAP-2181 / LAP-2222 / LAP-2154.
