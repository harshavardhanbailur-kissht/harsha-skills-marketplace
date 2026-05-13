# LAP Roles — Roster & Relationships

> Comprehensive role roster for the LAP Loan Origination System. Verified against Confluence 1088716805 + Harshavardhan's LAP Query Module page (1101660180).
>
> Use this file to (a) confirm a role abbreviation is valid before using it in a release note, (b) understand which roles a feature affects, and (c) order role sections in Beat 4.

---

## Sales

| Code | Full name | Owner of stage | Receives queries from |
|---|---|---|---|
| **SM** | Sales Manager | (LeadGen — leads, login docs) | CCPA, BCM, BCPA, BOM, COPs |
| **BM** | Branch Manager | (oversight) | CCPA, BCM, BCPA, BOM, COPs |
| **NSM** | National Sales Manager | `Rate Approval Pending` | (rate-approval workflow) |

Sales rarely raises queries; they receive them. In release notes, Sales sections should focus on:
- Customer-side expectation setting
- New gating that blocks their submission
- Notifications they newly receive (e.g. Move to Credit SMS)

---

## Credit (Branch / Cluster / Central / National)

| Code | Full name | Owner of stage | Notes |
|---|---|---|---|
| **CCPA** | Central Credit Processing Associate | `Sales PD Completed` | Login doc check, Sales PD images, BT/Top-Up docs. Self-raise allowed. |
| **BCM** | Branch Credit Manager | `CPA Verified`, `Final Sanction Pending`, `Reject Queue`, `Disbursed Offline` | Credit PD, sanction recommendation, post-sanction. Self-raise allowed. Multi-stage owner. |
| **BCPA** | Branch Credit Processing Associate | `Third Party Trigger Pending`, `Post Sanction`, `Partially Disbursed` | Owns Legal / Technical / RCU / FI handoff. |
| **CCM** | Cluster Credit Manager | `In-Principle Approval Pending`, `Relook CCM Approval Pending` | First-tier approver. |
| **SCM** | State Credit Manager | (same as CCM in panel; separated by state hierarchy) | First-tier approver. |
| **NCM** | National Credit Manager | `Final Sanction Approval Pending`, `Relook Approval Pending`, `Relook NCM Approval Pending` | Final approver. Can self-forward in Relook flow if CCM unavailable. |
| **C-BCM** | Central BCM (Saral 2.0) | `Final Sanction Pending` (Saral path), `Post Sanction` (Saral path) | Replaces BCM in Saral 2.0. Round-robin by state name. |

---

## Operations

| Code | Full name | Owner of stage | Notes |
|---|---|---|---|
| **BOM** | Branch Operation Manager | `Branch Operations` (Fresh Loan / Normal) | Disbursement kit, NACH. |
| **COM** | Central Operation Manager | `Central Operations`, `Disbursal Initiated`, `Disbursed`, `Cheque Initiated`, `Cheque Disbursed` | Final ops check + disbursement initiation. |
| **C-BOM** | Central BOM (Saral 2.0) | `Branch Operations` (Saral path) | Replaces BOM in Saral 2.0. Round-robin by state. |
| **COPs** | Central Operations (Saral 2.0) | `Central Operations` (Saral path) | Identical pool to Fresh Loan / Normal but distinct routing. |

---

## External / Specialised

| Code | Full name | Notes |
|---|---|---|
| **Financier Reviewer** | (no abbreviation in panel) | Stage owner of `Financier Review`. Lender-side. |
| **Vendor (Legal / Technical / RCU / FI)** | — | External verification vendors. Receive queries from BCPA. |

---

## Role Abbreviation Guide (for body text)

In release notes:
- First mention: full name + abbreviation in parens. `Branch Credit Manager (BCM)`.
- Subsequent mentions: abbreviation only. `BCMs raise relooks.`
- In Beat 4 H2s: pluralised abbreviation only. `## BCMs`.
- In rules and edge-case bypasses: abbreviation only is fine once introduced.
- In the Contacts block: first names only. `Prem, Kiran, Vinesh, Anjali, or Mahesh.`

---

## Role Ordering — Who Touches A Case First?

Standard Fresh Loan flow:
```
SM (leadgen) → CCPA (Sales PD) → BCM (CPA Verified) → CCM (IPA)
  → BCPA (Third Party Triggers) → BCM (Final Sanction)
  → [NSM (Rate)] → NCM (Final Approval)
  → BCPA (Post Sanction) → BOM (Branch Ops) → COM (Central Ops)
```

Saral 2.0 flow:
```
SM (leadgen) → CCPA (Sales PD) → C-BCM (Final Sanction)
  → [NSM (Rate)] → NCM (Final Approval)
  → C-BCM (Post Sanction) → C-BOM (Branch Ops) → COPs (Central Ops)
```

Relook flow (post-revamp):
```
BCM (raises relook) → CCM (Relook CCM Approval Pending) → NCM (Relook NCM Approval Pending)
  → [Approved] OR [Reject Queue (BCM)]
```

When ordering Beat 4 role sections, follow the order roles appear in the relevant flow.

---

## Role Section Skip Rules

A role section MUST be included if the change:
- Adds a new action that role can take.
- Removes an action that role used to take.
- Adds a new gating constraint that role must satisfy.
- Adds a new bucket / view / field they will see on their panel.
- Changes the SLA on a case they own.
- Adds a new notification they will receive.

A role section MUST be skipped if:
- The role is unaffected by the change.
- The role only sees the change as an indirect downstream effect (e.g. case routing changed somewhere else, but they're still doing the same thing).

> Bias toward exclusion. A 4-role release note that genuinely affects 4 roles is fine. A 7-role release note where 3 of the sections say "no impact" is wrong.

---

## Update Protocol

1. New role introduced (e.g. a future Compliance Officer): add to relevant table; cite source.
2. Existing role's stage ownership changes: update both `lap-stages.md` and this file.
3. Saral / Top-Up / new-product variant introduces new role names: add a separate variant section.

> **Roles KB version 1.0 — 2026-05-02**
