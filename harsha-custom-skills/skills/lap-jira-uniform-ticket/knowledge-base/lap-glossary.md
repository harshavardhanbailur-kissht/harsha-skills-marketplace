# LAP Glossary — Single Source of Truth for Domain Terms

> Comprehensive glossary of every LAP term a PM, BA, QA, or developer would use in a Jira ticket. Built from the kissht-field-release-notes sister-skill SKILL.md and the 6 LAP exemplar tickets (LAP-1812, LAP-2039, LAP-2046, LAP-2048, LAP-2052, LAP-2242).
>
> **How to use this file:**
> - Humans: scan tables to confirm a term before writing.
> - The skill: auto-define ghost terms by looking them up here.
> - When a term is `<!-- TODO: confirm with PM -->` it means a definition is best-guess and needs human validation.
> - When a term is `<!-- PLACEHOLDER: needs definition -->` it appears in source material but no canonical definition was found.
>
> Cross-references: detailed role roster in [`lap-roles.md`](./lap-roles.md); detailed stage list in [`lap-stages.md`](./lap-stages.md); Confluence source pages in [`lap-confluence-sources.md`](./lap-confluence-sources.md).

---

## 1. Roles (one-line index — full hierarchy in [`lap-roles.md`](./lap-roles.md))

| Code | Full name | One-line definition |
|---|---|---|
| **SM** | Sales Manager | Originates leads in LSQ; uploads login docs. |
| **RM** | Relationship Manager (Sales) | Field-facing sales contact; subordinate of SM/BM. |
| **BM** | Branch Manager | Branch oversight; receives queries. |
| **NSM** | National Sales Manager | Approves rate deviations at `Rate Approval Pending`. |
| **CCPA** | Central Credit Processing Associate | Owns `Sales PD Completed`; login doc + Sales PD checks. |
| **BCM** | Branch Credit Manager | Owns `CPA Verified`, `Final Sanction Pending`, `Reject Queue`; runs Credit PD. |
| **BCPA** | Branch Credit Processing Associate | Owns `Third Party Trigger Pending`, `Post Sanction`; Legal/Technical/RCU/FI handoff. |
| **CCM** | Cluster Credit Manager | First-tier credit approver; owns `In-Principle Approval Pending`. |
| **SCM** | State Credit Manager | First-tier approver in some states (panel-equivalent to CCM). |
| **SCH** | State Credit Head | Mid-slab IPA / FA approver per LAP-2242 matrix; CCM fallback for 0–7L. |
| **NCM** | National Credit Manager | Final approver; owns `Final Sanction Approval Pending`, Relook NCM Approval. |
| **C-BCM** | Central BCM (Saral 2.0) | Replaces BCM in Saral path. |
| **BOM** | Branch Operation Manager | Owns `Branch Operations`; disbursement kit, NACH validation. |
| **COM** | Central Operation Manager | Owns `Central Operations`; final ops + disbursement initiation. |
| **C-BOM** | Central BOM (Saral 2.0) | Replaces BOM in Saral path. |
| **COPs** | Central Operations (Saral 2.0) | Replaces COM in Saral path. |
| **Auditor** | KYC / VCIP Auditor | Reviews Video KYC; issues Soft Reject / Hard Reject (LAP-2048). |
| **CPA User** | Branch Credit Processing Associate (BCPA) | Used in LAP-1812 to refer specifically to **BCPA**. Treat `CPA User` as a synonym for BCPA in any LAP ticket. The skill auto-rewrites `CPA User` → `BCPA` in drafts unless the PM explicitly objects. |

---

## 2. Stages (one-line index — full table in [`lap-stages.md`](./lap-stages.md))

| Stage | Owner | One-line definition |
|---|---|---|
| `Sales PD Completed` | CCPA | Sales PD complete; login docs ready for credit. (First LOS opportunity stage. Lead Initiation / Sourcing are LSQ leadgen steps that happen BEFORE the LOS opportunity exists — NOT LOS stages.) |
| `CPA Verified` | BCM | Login + Sales PD docs verified by CCPA; with BCM. |
| `In-Principle Approval Pending` (IPA) | CCM / SCM (or SCH) | First credit approval after Credit PD. |
| `Third Party Trigger Pending` | BCPA | Pre-trigger of Legal / Technical / RCU / FI to compress TAT. |
| `Final Sanction Pending` | BCM | BCM compiles final recommendation post-vendor returns. |
| `Rate Approval Pending` | NSM | Rate deviation requires NSM approval. |
| `Final Sanction Approval Pending` (FA) | NCM (or SCH) | Final credit approval. |
| `Financier Review` | Financier Reviewer | Lender-side review (co-lending / partner-financier cases). |
| `Post Sanction` | BCPA | PDD, NACH, mortgage, e-Sign, Document Cleanup obligations. |
| `Branch Operations` | BOM | Disbursement kit assembly + NACH validation. |
| `Central Operations` | COM | Final ops check before disbursement. |
| `Reject Queue` | BCM | Rejection landing; BCM owns recovery / relook. |
| `Relook Approval Pending` | NCM | Legacy single-step relook. |
| `Relook CCM Approval Pending` | CCM / SCM | First step in Relook Revamp two-step approval. |
| `Relook NCM Approval Pending` | NCM | Second step in Relook Revamp two-step approval. |
| `Partially Disbursed` | BCPA | Multi-tranche cases mid-disbursement. |
| `Disbursed Offline` | BCM | Manual disbursement path. |
| `Disbursal Initiated` | COM | Mid-disbursement (auto path). |
| `Disbursed` | COM | Standard disbursement complete. |
| `Cheque Initiated` / `Cheque Disbursed` | COM | Cheque-mode disbursement stages. |
| `Rejected` | (last user) | Soft rejection — closed without disbursal. |
| `Lost Rejected` | (system-set) | Hard reject — set on Relook 30-day SLA breach. SM-repunch only. |

---

## 3. Acronyms

| Acronym | Expansion | One-line meaning |
|---|---|---|
| **LAP** | Loan Against Property | Secured lending product. The product this skill is built for. |
| **LOS** | Loan Origination System | The Kissht system that processes loans from leadgen to disbursement. |
| **LMS** | Loan Management System | Post-disbursement system; manages active loans. |
| **LSQ** | LeadSquared | Third-party CRM platform Kissht uses as the operational panel UI. |
| **PL** | Personal Loan | Adjacent product; ETB users may have prior PL records. |
| **BL** | Business Loan | Adjacent product. |
| **CC** | Credit Card | Adjacent product. |
| **IPA** | In-Principle Approval | First credit approval (CCM / SCM / SCH). See `In-Principle Approval Pending` stage. |
| **FA** | Final Approval | Final credit approval (NCM / SCH per slab). See `Final Sanction Approval Pending` stage. |
| **PD** | Personal Discussion | Sales PD (Sales-side) and Credit PD (Credit-side) — two distinct activities in LSQ. |
| **CAM** | Credit Appraisal Memo | Credit assessment artefact stored in `Sales PD Completed` tabs. |
| **CAF** | Customer Application Form | One of the documents in the e-Sign combined PDF kit (LAP-1812). |
| **KFS** | Key Fact Statement | RBI-mandated disclosure; combined with Sanction Letter into one document for e-Sign (LAP-1812). |
| **SL** | Sanction Letter | Bundled with KFS as one document for e-Sign (LAP-1812). |
| **LA** | Loan Agreement | Final document in the e-Sign combined PDF kit (LAP-1812). |
| **PDD** | Post-Disbursement Documents | Documents pending after disbursal; tracked in Post Sanction. |
| **NIC** | Non Income Considered | Tab on `Final Sanction Pending` and `Post Sanction` showing co-applicants flagged Income Considered = No (LAP-2039). |
| **FOIR** | Fixed Obligation to Income Ratio | Eligibility / debt-to-income calculation; reflects only co-applicants currently marked Income Considered = Yes (LAP-2039). |
| **OSV** | Originally Seen and Verified | Document verification stamp; confirms a copy was checked against the original by an authorised person (BCPA / CCPA / Auditor). |
| **AA** | Account Aggregator | RBI-regulated framework for consented financial data sharing (Sahamati / OneMoney / Finvu / NADL). Used to pull bank statements / GST data for income assessment. |
| **OD** | Overdraft | Loan product variant where the customer can draw up to a sanctioned limit on demand; interest charged only on utilised amount. |
| **BT** | Balance Transfer | Loan being moved from another lender; used in BT + Top-Up. |
| **BTLOAN** / **BT Loan** | Balance Transfer Loan | The loan being transferred in. |
| **BT + Top-Up** | Balance Transfer plus Top-Up | Combined product where customer transfers existing loan and tops up. |
| **Internal Top-Up** | Top-up loan on existing Kissht loan | Distinct from BT + Top-Up; PAN re-verification not required (LAP-2046). |
| **KYC** | Know Your Customer | RBI-mandated identity verification. |
| **OKYC** | Offline KYC | Aadhaar XML / paperless offline KYC. Customer downloads an encrypted Aadhaar XML from UIDAI and shares; no UIDAI API call needed. Used when biometric / OTP eKYC is unavailable. |
| **CKYC** | Central KYC | CERSAI's centralised KYC Records Registry. Each customer gets a 14-digit CKYC number; lenders can fetch existing KYC data instead of re-collecting. |
| **eKYC** | Electronic KYC | Aadhaar-based electronic KYC via UIDAI API; OTP-based or biometric. Returns demographic + photo. |
| **VCIP** | Video Customer Identification Process | Video KYC; valid for 9 years 6 months (LAP-2048). |
| **CIBIL** | Credit Information Bureau (India) Ltd. | Consumer credit bureau; pulled at Bureau Pull step. |
| **NACH** | National Automated Clearing House | E-mandate / auto-debit mandate framework; validated at `Branch Operations`. |
| **E-Mandate** / **eNACH** | Electronic NACH | Digital mandate registration; triggered via `'Initiate E-Mandate Registration?'` dropdown. |
| **Renach** | E-Mandate re-registration / re-NACH | E-mandate renewal flow with branching outcomes (LAP-2154). |
| **ETB** | Existing-to-Business | User who has applied with SiCreva before (PL or LAP). PAN re-verification logic differs (LAP-2046). |
| **NTB** | New-to-Business | First-time SiCreva applicant; formal counterpart of ETB in LSQ. PAN re-verification logic differs (LAP-2046 — NTB requires full bureau pull; ETB may bypass under conditions). |
| **TAT** | Turn-Around Time | SLA for completing a stage. |
| **SLA** | Service-Level Agreement | Time bound for a stage / action. |
| **PF** | Processing Fee | Loan-origination fee. |
| **IMD** | Initial Margin Deposit | Customer-side deposit; preserved across send-backs (Post Sanction → BCM, per kissht-field-release-notes SKILL.md). |
| **PAN** | Permanent Account Number | Indian tax ID; PAN re-verification logic in LAP-2046. |
| **DOB** | Date of Birth | One of the fields validated against PAN bureau response. |

---

## 4. Concepts & Domain Vocabulary

| Term | Definition |
|---|---|
| **Saral journey** | Saral 2.0 — a waiver-eligible Fresh Loan programme that skips `CPA Verified` and uses Central role variants (C-BCM, C-BOM, COPs). See [`lap-stages.md`](./lap-stages.md) §4. |
| **Fresh Loan** | A new LAP loan (not BT, not Top-Up). Default product flow. |
| **Normal program** | Fresh Loan without Saral path. Subdivided into "Is Waiver Eligible? = YES" and "= NO" (Confluence 1089142840). |
| **Relook** | A second-look on a rejected case; raised by BCM. Post-Revamp uses two-step CCM → NCM approval. See "Relook Revamp" / Workflow Change pattern in sister skill. |
| **Renach** | E-mandate re-registration flow. Triggered via `'Initiate E-Mandate Registration?'` dropdown on Post Sanction. Has branching outcomes (LAP-2154). |
| **Mandate buffer** | Time buffer added to the mandate expiry beyond the loan tenure, to accommodate EMI bouncing / re-presentation / tenure extension without needing a fresh mandate. Per LAP-2154 §"Edge case — buffer policy": **initial mandate = tenure + 5 years buffer**; **revised mandate = tenure + 4 years buffer**. New mandate generated via link = **5 years buffer** again. Conditions enforced backend-side, not in LSQ. |
| **Hard reject** | System-set terminal rejection. Recovery requires SM repunch (e.g. `Lost Rejected` after Relook SLA breach; LAP-2048 Hard Reject sets reapply days = 0). |
| **Soft reject** | User-recoverable rejection. e.g. LAP-2048 Soft Reject — user can redo VCIP using same link for 72 hours. |
| **Push-to-LMS** | API call from LOS to LMS at end of `Central Operations`. Includes contractual fields like `enach_reference_number` (LAP-2154). LMS rejection halts the case. |
| **Eligibility calculation** | Amount the applicant qualifies for; depends on Income Considered flags, FOIR, bureau score. Locked to primary applicant Yes per LAP-2039 Open Considerations. |
| **Debt-to-Income** | Same as FOIR conceptually. |
| **Send-Back** | Routing a case back to a previous stage with category + remarks. See [`lap-stages.md`](./lap-stages.md) §9 for adjacency table. |
| **Bypass Protocol** | LAP-2048 — if VCIP is valid (within 9y6mo), system marks KYC `Completed` and case status `Onboarded`. |
| **72-hour Digilocker bypass** | LAP-2048 — if Digilocker was completed within 72 hours, skip and go directly to VCIP. |
| **Approval matrix** | LAP-2242 — slab-based mapping of loan amount → IPA approver / FA approver / fallback approver. |
| **Fallback logic** | LAP-2242 — when designated approver role has no active user, route to default approver for the slab. |
| **State-wise SCH variant** | LAP-2242 — SCH 1 / SCH 2 mapping by state (MH, AP, TG → SCH 2; TN, UP, GJ → SCH 1). |
| **Income Considered** | Per-applicant flag (Yes/No) on the Credit PD form indicating whether their income contributes to eligibility. Moved to top of `Mark as Complete` form per LAP-2039. |
| **Bug fan-out** | The set of bugs raised during QA against a story; treated as a quality signal for exemplar selection. |
| **Saral 2.0 Positive & Send-Back flow** | LAP-1665 — Saral path send-back routing. |
| **Loan Amount Slab** | Per LAP-2242: 0–7L, 7L–10L, 10L+. Determines IPA / FA approver. |

---

## 5. External Systems

| System | Role |
|---|---|
| **LSQ (LeadSquared)** | The CRM panel UI Kissht operators use. The "panel" referenced throughout. |
| **LMS (Loan Management System)** | Post-disbursement loan servicing; Push-to-LMS is the API contract. |
| **LOS (Loan Origination System)** | Kissht's pre-disbursement system; this is where the LAP flow lives. |
| **Digio** | E-sign partner; receives one flow per applicant with single OTP (LAP-1812). |
| **Digilocker** | Government e-document wallet; Aadhaar-based; 72-hour bypass window (LAP-2048). |
| **Veriphy** | KYC verification vendor. <!-- TODO: confirm with PM whether Veriphy is in current LAP flow --> |
| **Finbox** | Bureau / underwriting input source; dropdown values must match the Finbox input parameter (LAP-2052 QA scenarios). |
| **Polaris** | Internal product / experiment tracking system; LAP-1812 references "Polaris items" in linked issues. |
| **Kissht** | The hosting platform; stores `user_consents` table, generates SMS links (LAP-1812). |
| **SiCreva** | Kissht's regulated NBFC entity; SMS sender ID (LAP-1812 SMS). |
| **Jira (kissht.atlassian.net)** | Issue tracker; LAP project key. |
| **Confluence (kissht.atlassian.net/wiki)** | Documentation; LOS-LAP master page is 1088716805. |

---

## 6. System Strings (verbatim panel labels)

These appear in panel UI / forms and MUST be quoted verbatim with single quotes when referenced in tickets, PRDs, or release notes.

| String | Where it appears | Source |
|---|---|---|
| `'Initiate E-Mandate Registration?'` | `Repayment & Disbursal Details Capture - v5` form on Post Sanction | sister skill SKILL.md, LAP-2154 |
| `'Lost Rejected'` | Lost-status stage label | sister skill SKILL.md |
| `'Income Considered'` | Field on Credit PD `Mark as Complete` form | LAP-2039 |
| `'Mark as Complete'` | Button / form name on Credit PD activity | LAP-2039 |
| `'Yes'` / `'No'` | Income Considered toggle values | LAP-2039 |
| `'Type of ownership document / Property Document'` | Dropdown at Property Documents Task, Credit PD, Property Technical, Recommendation forms | LAP-2052 |
| `'Property occupancy status / Property type'` | Dropdown at Loan and Property; mortgage detail tab | LAP-2052 |
| `'Primary Property Document/Type of ownership document'` | Dropdown at Leadgen Property Documents Task | LAP-2052 |
| `'Onboarded'` | Case/applicant status set after VCIP bypass | LAP-2048 |
| `'Completed'` | KYC activity status after Bypass Protocol | LAP-2048 |
| `'Soft Reject'` / `'Hard Reject'` | Auditor verdicts on VCIP | LAP-2048 |
| `'Approved'` / `'Rejected'` | Second Auditor Review verdicts | LAP-2048 |
| `'NIC'` (Non Income Considered) | Tab name on Final Sanction Pending and Post Sanction stages | LAP-2039 |
| `'Applicant Details'` | Tab/section showing all applicants regardless of NIC status | LAP-2039 |
| `'Submit App Check'` | Form/action exiting Sales PD Completed | sister skill SKILL.md |
| `'CPA Check'` | Tab on Sales PD Completed | sister skill SKILL.md |
| `'Mortgage Details'` → `'System Generated Documents'` | Path where consent records are stored in LSQ | LAP-1812 |
| `'Opportunity Data'` | Final storage location for signed combined PDF | LAP-1812 |
| `'BT Category'` | Form at CPA Verified and In-principle Approval Pending for BT+Top-Up | LAP-2052 |
| `'Document Upload and Cleanup'` | Tab at Post Sanction stage for document replacement | LAP-2052 |
| `'Recommendation form'` | Form at Final Sanction Pending and Final Sanction Approval Pending | LAP-2052 |
| `'Property Technical form'` | Form at Third Party Trigger Pending, Final Sanction Pending, Final Sanction Approval Pending | LAP-2052 |
| `'Review Property Technical'` | Form at Final Sanction Pending and Final Sanction Approval Pending (Saral path) | LAP-2052 |
| `'Repayment & Disbursal Details Capture - v5'` | Form on Post Sanction → Repayment Details subtab | sister skill SKILL.md / LAP-2154 |
| `'Approval Pending'` | Generic substring in stage names — never use without prefix | sister skill SKILL.md |
| `'reapply days'` | Field set to 0 on Hard Reject in VCIP flow | LAP-2048 |
| `'mandate_amount'` | Backend field on E-Mandate registration | sister skill SKILL.md |
| `'enach_reference_number'` | Push-to-LMS request body field; LMS validates and may reject | sister skill SKILL.md, LAP-2154 |

---

## 7. Document Composition Rules (LAP-1812 specific)

For e-Sign combined PDF kit at Post Sanction:

| Order | Document | Notes |
|---|---|---|
| 1 | KFS + SL | Treated as ONE document; page references picked dynamically by tenure config |
| 2 | CAF | Mandatory |
| 3 | LA (Loan Agreement) | Mandatory |

All three are mandatory. Combined PDF; one upload only for Physical Sign; cannot be replaced unless regenerated.

---

## 8. Update Protocol

1. New term encountered in a Jira ticket: add to the relevant section above with citation.
2. Term marked `<!-- TODO: confirm with PM -->` is verified by user: remove the comment, update.
3. Term marked `<!-- PLACEHOLDER: needs definition -->` is defined by user: replace placeholder with the definition + citation.
4. New system string discovered: add to §6 verbatim with single quotes.

> **Glossary KB version 1.0 — 2026-05-14**
> Sources: kissht-field-release-notes SKILL.md (sister skill), Confluence pageId 1088716805 (master), 1101660180 (Query module), and LAP exemplar tickets LAP-1812, LAP-2039, LAP-2046, LAP-2048, LAP-2052, LAP-2242.
