# LAP Stages — Single Source of Truth

> The full LAP stage list with owner role, what triggers entry, and what triggers exit. Verified against Confluence page 1088716805 ("LOAN ORIGINATION SYSTEM - LAP", canonical) and the 6 LAP exemplar tickets (LAP-1812, LAP-2039, LAP-2046, LAP-2048, LAP-2052, LAP-2242).
>
> When a Jira ticket references a stage, that stage's exact name and owner role MUST appear in a table below. If a new stage is introduced, add it here with citation.
>
> Cross-reference: [`lap-roles.md`](./lap-roles.md) for role hierarchy; [`lap-glossary.md`](./lap-glossary.md) for one-line stage definitions.

---

## 1. Open Status — The Active Pipeline

| # | Stage (verbatim from LSQ panel) | Owner role | Triggered by (entry) | Exits to (typical) |
|---|---|---|---|---|
| 1 | `Sales PD Completed` | CCPA | Submit App Check form completed by Sales | `CPA Verified` (or send-back to Sales) |
| 2 | `CPA Verified` | BCM | CCPA passes login doc / Sales PD checks | `In-Principle Approval Pending` |
| 3 | `In-Principle Approval Pending` (IPA) | CCM / SCM (or SCH per LAP-2242 matrix) | BCM completes Credit PD and recommends | `Third Party Trigger Pending` |
| 4 | `Third Party Trigger Pending` | BCPA | IPA approved by CCM/SCM | `Final Sanction Pending` |
| 5 | `Final Sanction Pending` | BCM | Legal / Technical / RCU / FI returns | `Final Sanction Approval Pending` (or `Rate Approval Pending`) |
| 6 | `Rate Approval Pending` | NSM | Rate deviation flagged by BCM in recommendation | `Final Sanction Approval Pending` |
| 7 | `Final Sanction Approval Pending` (FA) | NCM (or SCH per LAP-2242 matrix) | BCM submits final recommendation | `Financier Review` or `Post Sanction` |
| 8 | `Financier Review` | Financier Reviewer | NCM approves; lender review required | `Post Sanction` |
| 9 | `Post Sanction` | BCPA | NCM approves (or Financier passes) | `Branch Operations` |
| 10 | `Branch Operations` | BOM | BCPA closes Post Sanction obligations | `Central Operations` |
| 11 | `Central Operations` | COM | BOM submits disbursement kit | `Disbursed` (or send-back) |
| 12 | `Reject Queue` | BCM | Rejection from any stage | `Rejected` (after BCM action) or back into pipeline (relook) |
| 13 | `Relook Approval Pending` | NCM | BCM raises relook (legacy single-step path) | `In-Principle Approval Pending` (or `Reject Queue`) |
| 14 | `Relook CCM Approval Pending` | CCM / SCM | BCM raises relook (post-Revamp two-step path — LIVE in prod; Confluence pageId 1088716805 is stale on Relook, sister skill kissht-field-release-notes is canonical) | `Relook NCM Approval Pending` |
| 15 | `Relook NCM Approval Pending` | NCM | CCM forwards relook | Approved → back into pipeline / `Reject Queue` |
| 16 | `Partially Disbursed` | BCPA | Multi-tranche cases mid-disbursement | `Disbursed` |

---

## 2. Won Status — Disbursed

| Stage | Owner role | Notes |
|---|---|---|
| `Disbursed Offline` | BCM | Manual disbursement path. |
| `Disbursal Initiated` | COM | Mid-disbursement. |
| `Disbursed` | COM | Standard disbursement complete. |
| `Disbursed by Financier` | (no current owner — see note) | Co-lending / direct-financier disbursement. **Built in advance; no financier currently onboarded so this stage has no current owner. Owner role to be circled back when financier onboarding completes.** |
| `Cheque Initiated` | COM | Cheque-mode disbursement initiated. |
| `Cheque Disbursed` | COM | Cheque-mode complete. |

---

## 3. Lost Status

| Stage | Owner | Notes |
|---|---|---|
| `Rejected` | Last user to action the case | Soft rejection — closed without disbursal. Recovery: relook by BCM. |
| `Lost Rejected` (system-set) | — | Hard reject — set by system on Relook 30-day SLA breach (or equivalent). Recovery path: SM repunch only. See [`lap-glossary.md`](./lap-glossary.md) §Concepts. |

---

## 4. Saral 2.0 Variant Path

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

When writing a ticket / release note for a Saral-affecting feature, name the C-BCM / C-BOM / COPs roles explicitly.

---

## 5. Post Sanction — Substructure (verified in LAP-2154 / LAP-1812)

The Post Sanction stage has tabs and subtabs that the BCPA navigates to action different post-sanction obligations. When a ticket touches Post Sanction, name the tab + subtab + form explicitly so the BCPA can locate the trigger.

| Tab | Subtab | Notable forms / contents |
|---|---|---|
| Post Sanction | Repayment Details | `Repayment & Disbursal Details Capture - v5` form (note: bumped to v6 per LAP-2176 — confirm latest version with PM). Contains `'Initiate E-Mandate Registration?'` dropdown — primary trigger for Renach logic (LAP-2154). ENACH task surfaces here. |
| Post Sanction | `Disbursal Details` | Auto-fetched disbursal details on case entry. Contains: Disbursal Bank Details + DRF (Disbursal Request Form) Document. Auto-fetched data is deleted on send-back to Saral User and re-fetched on click (LAP-1868). Task hidden once case is sent back from Post Sanction (LAP-1505). **Inferred from LAP-1879 / LAP-1868 / LAP-1505 / LAP-1663 — please validate field-by-field with PM.** |
| Post Sanction | `Document Upload and Cleanup` | Document replacement for `'Type of ownership document / Property Document'` (LAP-2052). |
| Post Sanction | NIC tab | Shows co-applicants flagged Income Considered = No (LAP-2039). |
| Post Sanction (BT-only smart view) | `Disbursal` (separate from Disbursal Details) | Surfaced under BT Partially Disbursed Smart View for BCPA (LAP-1879) — when one tranche is disbursed and disbursal flow type is "Tranche-level disbursals with different disbursement dates". |

**Note on terminology:** Internal usage interchanges "Disbursement Details" and "Disbursal Details" — Indian-English convention favors `Disbursal`. Tickets and panel UI use both. Skill auto-normalizes to `Disbursal Details` (panel-canonical) when drafting.

---

## 6. BT + Top-Up Variant Stages

For BT + Top-Up loans (LAP-2052):

| Stage | Owner | Form / Touchpoint |
|---|---|---|
| `CPA Verified` | BCM | BT Category form (edit + first-time initiation) |
| `In-Principle Approval Pending` | CCM | BT Category form (edit + first-time initiation) |

After BT Category is defined at Credit PD, Property Technical, and Recommendation, downstream touchpoints are frozen.

---

## 7. Key Forms by Stage

These forms are referenced in LAP exemplars and should be used verbatim when writing tickets:

| Stage | Form | Reference |
|---|---|---|
| `Sales PD Completed` | Submit App Check form | Sister skill SKILL.md §3 |
| `CPA Verified` | CPA Checklist; BT Category (BT+Top-Up) | LAP-2052 |
| Credit PD activity (multi-stage) | `Credit PD Mark as Complete form` (contains `Income Considered` field — moved to top per LAP-2039) | LAP-2039 |
| `Third Party Trigger Pending` | Property Technical form; Recommendation form | LAP-2052 |
| `Final Sanction Pending` | Property Technical form; Recommendation form; Submit App Check | LAP-2052 |
| `Final Sanction Approval Pending` | Property Technical form; Recommendation form | LAP-2052 |
| `Post Sanction` | `Repayment & Disbursal Details Capture - v5`; Document Upload and Cleanup tab | LAP-2052, LAP-2154, LAP-1812 |
| Saral path Final Sanction | Review Property Technical form | LAP-2052 |

---

## 8. Push to LMS — Request Body Contract Additions

When a ticket describes a change that flows through to LMS via the Push-to-LMS API, name the affected fields. Currently known additions:

- `enach_reference_number` (LAP-2154) — LMS validates against the loan; rejection halts the case until reconciled.

When a ticket touches Push-to-LMS validation, the BCPA / COM section MUST include the consequence of LMS rejection.

---

## 9. Stage Adjacency (Send-Back And Relook Routing)

Common send-back routes (source: kissht-field-release-notes SKILL.md, LAP-1445):

| From | Send-back category | To | Side-effects |
|---|---|---|---|
| Third Party Trigger Pending | Rejection Post IPA | Final Sanction Pending (BCM) | No submit-to-source; mandatory remarks. |
| Final Sanction Pending | Legal/Technical Pending | Third Party Trigger Pending (BCPA) | Resets Act Recommendation Posted flag. |
| Final Sanction Pending | Change in Income | Sales | Blanks recommendation flag. |
| Final Sanction Approval Pending | Return Request | Final Sanction Pending (BCM) | Recommendation deleted; flags preserved. |
| Rate Approval Pending | Return Request | Final Sanction Pending (BCM) | Recommendation + loan parameter field deleted. |
| Post Sanction | Legal/Technical related | Third Party Trigger Pending (BCPA) | Recommendation activity preserved; new submit-to-source generated. |
| Post Sanction | Change in Offer / Rate | C-BCM (Saral) / BCM | Discards Fees & Charges (Legal/Tech + PF, NOT IMD). |

---

## 10. Update Protocol

1. New stage discovered in a Jira ticket: verify against panel UI; add to the right table; cite ticket.
2. Owner change: cite source; update; flag both old and new owners for backwards compatibility in legacy cases.
3. New send-back / query routing: add to §9.

> **Stages KB version 1.0 — 2026-05-14**
> Sources: kissht-field-release-notes SKILL.md (sister skill), Confluence 1088716805 (master), 1101660180 (Query module), and LAP exemplar tickets.
