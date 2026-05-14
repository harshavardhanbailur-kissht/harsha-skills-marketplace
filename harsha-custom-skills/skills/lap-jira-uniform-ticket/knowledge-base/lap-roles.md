# LAP Roles — Roster & Hierarchy

> Comprehensive role roster for the LAP Loan Origination System (LOS). Use this file when (a) confirming an abbreviation is valid in a ticket, (b) deciding which roles a feature affects, and (c) ordering role sections in PRDs and release notes.
>
> Cross-references: see [`lap-stages.md`](./lap-stages.md) for stage-by-stage owner mapping and [`lap-glossary.md`](./lap-glossary.md) for one-line role definitions in the glossary index.

---

## 1. Sales Function

| Code | Full name | Stage(s) owned | Reports to | Notes |
|---|---|---|---|---|
| **SM** | Sales Manager | Lead Generation, Sourcing | BM | Originates leads in LSQ; uploads login docs. Does not raise queries — receives them. |
| **RM** | Relationship Manager (Sales) | Lead handling | SM / BM | Field-facing sales contact. <!-- TODO: confirm with PM whether RM is a distinct system role or alias for SM in LSQ panel --> |
| **BM** | Branch Manager | Branch oversight | SM (regional) / NSM | Receives queries; does not own a stage. |
| **NSM** | National Sales Manager | `Rate Approval Pending` | (top of Sales hierarchy) | Approves rate deviations only. |

Sales rarely raises queries; they receive them. Sales sections in tickets / release notes should focus on customer-side expectation setting, new gating that blocks submission, and notifications they newly receive.

---

## 2. Credit Function

| Code | Full name | Stage(s) owned | Reports to | Notes |
|---|---|---|---|---|
| **CCPA** | Central Credit Processing Associate | `Sales PD Completed` | BCM (functionally) | Login doc check, Sales PD images, BT/Top-Up docs. Self-raise allowed. |
| **BCM** | Branch Credit Manager | `CPA Verified`, `Final Sanction Pending`, `Reject Queue`, `Disbursed Offline` | CCM | Multi-stage owner. Credit PD, sanction recommendation, post-sanction recovery. Self-raise allowed. |
| **BCPA** | Branch Credit Processing Associate | `Third Party Trigger Pending`, `Post Sanction`, `Partially Disbursed` | BCM | Owns Legal / Technical / RCU / FI handoff and post-sanction obligations. |
| **CCM** | Cluster Credit Manager | `In-Principle Approval Pending`, `Relook CCM Approval Pending` | SCH / NCM | First-tier credit approver. |
| **SCM** | State Credit Manager | (same as CCM in panel; separated by state hierarchy) | SCH / NCM | First-tier approver in some states. |
| **SCH** | State Credit Head | IPA / FA approver per slab (see LAP-2242 matrix) | NCM | Approves mid-slab loans (7L–10L) per IPA / FA approval matrix; fallback for 0–7L slab. |
| **NCM** | National Credit Manager | `Final Sanction Approval Pending`, `Relook Approval Pending`, `Relook NCM Approval Pending` | (top of Credit hierarchy) | Final approver. Can self-forward in Relook flow if CCM unavailable. Fallback for higher slabs. |
| **C-BCM** | Central BCM (Saral 2.0) | `Final Sanction Pending` (Saral), `Post Sanction` (Saral) | (Saral pool) | Replaces BCM in Saral 2.0. Round-robin by state. |

---

## 3. Operations Function

| Code | Full name | Stage(s) owned | Reports to | Notes |
|---|---|---|---|---|
| **BOM** | Branch Operation Manager | `Branch Operations` (Fresh Loan / Normal) | COM | Disbursement kit, NACH validation. |
| **COM** | Central Operation Manager | `Central Operations`, `Disbursal Initiated`, `Disbursed`, `Cheque Initiated`, `Cheque Disbursed` | (top of Ops hierarchy) | Final ops check + disbursement initiation. |
| **C-BOM** | Central BOM (Saral 2.0) | `Branch Operations` (Saral path) | COM | Replaces BOM in Saral 2.0. |
| **COPs** | Central Operations (Saral 2.0) | `Central Operations` (Saral path) | (top of Ops hierarchy) | Identical pool to Fresh Loan / Normal but distinct routing. |

---

## 4. External / Specialised Roles

| Code | Full name | Notes |
|---|---|---|
| **Financier Reviewer** | (no abbreviation in panel) | Stage owner of `Financier Review`. Lender-side. |
| **Auditor** | KYC / VCIP Auditor | Reviews Video KYC submissions. Issues Soft Reject / Hard Reject (LAP-2048). <!-- TODO: confirm with PM whether First and Second Auditor are distinct roles in panel --> |
| **Vendor (Legal / Technical / RCU / FI)** | — | External verification vendors. Receive queries from BCPA. |
| **CPA User** | (LAP-1812 verbiage) | **Maps to BCPA (Branch CPA)** verbatim — confirmed by PM. Skill auto-rewrites `CPA User` → `BCPA` in drafts. See [`lap-glossary.md`](./lap-glossary.md) §1 Roles. |

---

## 5. Hierarchy Diagram

```
                                 LAP Functional Hierarchy
                                 ------------------------

         SALES                     CREDIT                    OPERATIONS
         -----                     ------                    ----------
          NSM                       NCM                          COM
           |                         |                            |
           BM                        SCH                          BOM
           |                         |                            |
           SM                       CCM / SCM                    (BCPA hands
           |                         |                            disbursement
           RM                        BCM                          to BOM)
                                     |
                                    BCPA
                                     |
                                    CCPA  (functionally central but
                                           reports to BCM in workflow)


         SARAL 2.0 VARIANTS
         ------------------
          C-BCM   (Central, replaces BCM in Saral path)
          C-BOM   (Central, replaces BOM in Saral path)
          COPs    (Central, replaces COM in Saral path)
```

---

## 6. Role Ordering — Who Touches a Case First?

Standard Fresh Loan flow (use this order in PRD role sections):

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

---

## 7. Role Abbreviation Conventions

In any ticket, PRD, or release note:
- **First mention**: full name + abbreviation in parens. e.g. `Branch Credit Manager (BCM)`.
- **Subsequent mentions**: abbreviation only. e.g. `BCMs raise relooks.`
- **In H2 role headers**: pluralised abbreviation only. e.g. `## BCMs`.
- **In Contacts blocks**: first names only.

---

## 8. Update Protocol

1. New role discovered in a Jira ticket: verify against panel UI; add to relevant table; cite ticket.
2. Role's stage ownership changes: update both this file and [`lap-stages.md`](./lap-stages.md).
3. Saral / Top-Up / new product variant introduces new role names: add a separate variant row.

> **Roles KB version 1.0 — 2026-05-14**
> Sources: kissht-field-release-notes SKILL.md (sister skill), Confluence pageId 1088716805, LAP exemplar tickets LAP-1812, LAP-2039, LAP-2046, LAP-2048, LAP-2052, LAP-2242.
