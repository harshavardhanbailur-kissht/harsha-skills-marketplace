# LAP Domain Glossary

> Single source of truth for stage names, role names, system strings, and acronyms used in field release notes. Verified against the canonical LAP LOS Confluence page (1088716805) and Harshavardhan's LAP Query Module guide (1101660180).
>
> **Rule**: every term that appears in a release note's "Stages in the system" or "Key rules" section MUST be in this glossary. If it is not, either add it (with a Confluence citation) or do not use it.

---

## Stage Names (LSQ Panel — Verbatim)

These are the strings that appear in the LeadSquared (LSQ) panel UI. Treat them as proper nouns. Quote them in `'single quotes'` when referenced inside rules.

### Open status

| Stage | Owner role |
|---|---|
| `Sales PD Completed` | Central CPA (CCPA) |
| `CPA Verified` | Branch Credit Manager (BCM) |
| `In-Principle Approval Pending` | Cluster CM / State CM (CCM / SCM) |
| `Third Party Trigger Pending` | Branch CPA (BCPA) |
| `Final Sanction Pending` | Branch Credit Manager (BCM) |
| `Rate Approval Pending` | National Sales Manager (NSM) |
| `Final Sanction Approval Pending` | National Credit Manager (NCM) |
| `Financier Review` | Financier Reviewer |
| `Post Sanction` | Branch CPA (BCPA) |
| `Branch Operations` | Branch Operation Manager (BOM) |
| `Central Operations` | Central Operation Manager (COM) |
| `Reject Queue` | Branch Credit Manager (BCM) |
| `Relook Approval Pending` | National Credit Manager (NCM) |
| `Relook CCM Approval Pending` | Cluster CM / State CM (CCM / SCM) |
| `Relook NCM Approval Pending` | National Credit Manager (NCM) |
| `Partially Disbursed` | Branch CPA (BCPA) |

### Won status

| Stage | Owner role |
|---|---|
| `Disbursed Offline` | Branch Credit Manager (BCM) |
| `Disbursal Initiated` | Central Operation Manager (COM) |
| `Disbursed` | Central Operation Manager (COM) |
| `Disbursed by Financier` | (TBD per case) |
| `Cheque Initiated` | Central Operation Manager (COM) |
| `Cheque Disbursed` | Central Operation Manager (COM) |

### Lost status

| Stage | Owner role |
|---|---|
| `Rejected` | Last user to action the case |

### System-set status values (as the case will display them)

- `'Lost Rejected'` — system-set status when the case is hard-rejected (e.g. Relook 30-day SLA breach).
- `'Live'` — Jira ticket status, signals the change is in production.
- `'Done'` / `'Released'` — Jira ticket states where the change is shippable.

---

## Roles (with abbreviations)

Use the abbreviation in body text once the full name is established once. In role section H2s, use the abbreviation only (`BCMs`, `CCMs`, `NCMs`).

### Sales

| Code | Full name | What they do |
|---|---|---|
| **SM** | Sales Manager | Generates lead, uploads login docs |
| **BM** | Branch Manager | Oversees branch sales, can receive queries |
| **NSM** | National Sales Manager | Approves rates |

### Credit

| Code | Full name | What they do |
|---|---|---|
| **CCPA** | Central Credit Processing Associate | Login doc check, Sales PD images, BT/Top-Up docs (owns Sales PD Completed stage) |
| **BCM** | Branch Credit Manager | Credit PD, Sanction Recommendation, Post-Sanction (owns CPA Verified, Final Sanction Pending, Reject Queue) |
| **BCPA** | Branch Credit Processing Associate | Third-party verifications: Legal, Technical, RCU, FI |
| **CCM / SCM** | Cluster CM / State CM | First approver — In-Principle Approval Pending, Relook CCM Approval Pending |
| **NCM** | National Credit Manager | Final approver — Final Sanction Approval Pending, Relook NCM Approval Pending |
| **C-BCM** | Central BCM | Saral 2.0 equivalent of BCM |

### Operations

| Code | Full name | What they do |
|---|---|---|
| **BOM** | Branch Operation Manager | Branch Ops handoff (Fresh Loan / Normal) |
| **COM** | Central Operation Manager | Central Ops, disbursement initiation |
| **C-BOM** | Central BOM | Saral 2.0 equivalent of BOM |
| **COPs** | Central Operations | Final ops check before Push to LMS |
| **Financier Reviewer** | (no abbreviation in panel) | Reviews case at Financier Review stage |

---

## System Strings (quoted in release notes)

Quote any of these verbatim with `'single quotes'` when they appear in body text:

- `'Lost Rejected'` — system-set hard-reject status
- `'Sales PD Completed'`, `'CPA Verified'`, `'Final Sanction Pending'`, …  (all stage names above)
- `'Approval'` — the tab on the Reject Queue panel where rejection comments are read
- `'Submit App Check'` — the form that exits Sales PD Completed
- `'Relook Date'` — CAM field, separate from original case date
- `'Relook Status'` — CAM field, Yes / No
- `'Underwriter Status'` — DigiLocker journey field; values include `'Not Seen'` and `'Rework'`
- `'is_discarded'` — flag set true when underwriter status moves Not Seen → Rework
- `'check_status'` — KYC flag, values `'PASSED'` / `'FAILED'`
- `'is_aadhaar_unique'`, `'face_verification'`, `'dob_matched'`, `'aadhaar_last_4_digits_matched'`, `'document_verification'`, `'pan_name_matched'`, `'aadhaar_name_matched'`, `'pmla_match'`, `'pep_match'` — KYC sub-flags returned by DigiLocker

When a release note references one of these strings, quote it exactly. Do not paraphrase ("the underwriter status field" → bad; `'Underwriter Status'` field → good).

---

## Programme & Loan Type Vocabulary

| Term | Meaning |
|---|---|
| **Programme** | Combination of `Eligible program` (NORMAL / SARAL) × `Is Waiver Eligible?` (Yes / No). Set by Finbox at leadgen, immutable after. |
| **Loan Type** | Fresh Loan / BT + Topup / Internal Topup |
| **Saral** / **Saral 2.0** | Fast-track waiver-eligible Fresh Loan programme. Skips BCM CPA-Verified stage; routes Sales PD Completed → Final Sanction Pending (C-BCM). |
| **NORMAL** | Standard programme; full BCM/CCM/NCM chain. |
| **BT + Topup** | Balance Transfer plus Top-Up. |
| **Internal Topup** | Whitelist-based top-up product for existing LAP customers (LAP-551, LAP-1020199073 PRD). |

---

## Activity & Document Vocabulary

| Term | Meaning |
|---|---|
| **CAM** | Credit Appraisal Memorandum — collated credit summary auto-built from earlier-stage inputs; consumed at sanction. |
| **CPA Check** | Tab on Sales PD Completed; contains Bureau Pull, CPA Checklist, Address Update. |
| **Submit App Check** | Form that exits Sales PD Completed. For SARAL → jumps to Final Sanction (Central BCM). For all others → CPA Verified (BCM). |
| **PD** | Personal Discussion. |
| **Send Back** | Reverses stage ownership to a prior owner. Different from Query (which keeps stage/owner and asks for info). |
| **Query** | Structured ask for missing/wrong/unclear info; keeps stage; routed to specific role via Raise-To matrix. See LAP Query Module page (1101660180). |
| **Sanction Condition** | Pre-disbursement obligation. Status: Open / Closed / Waived / Discarded / Converted to PDD. Blocks loan creation if any remain Open. |
| **Deviation** | Exception to credit policy (e.g. LTV/score). Requires approver email + supporting doc. Blocks Ops handoff if Open. |
| **PDD** | Post-Disbursement Document. Doc promised after sanction with target date and submission status. |
| **FOIR** | Fixed-Obligation-to-Income Ratio; computed before & after offer. |
| **OVD** / **Deemed OVD** | Officially Valid Documents for address proof (Voter ID, DL, Passport; utility bills as Deemed). |
| **OSV** | Original Seen and Verified. |
| **Bureau Repull** / **Bureau After 30 Days** | Bureau report valid 31 days; repull triggers an "After 30 Days" data block. |
| **CERSAI** | Central registry where the property charge is filed; LOS calls API and stores CERSAI ID. |
| **e-NACH** / **NACH Profile ID** | E-mandate registration for EMI auto-debit. |
| **DigiLocker** | Govt-backed KYC tool; hosts Aadhaar / PAN / DL data with consent. |
| **Selfie** / **Underwriter Status** | DigiLocker selfie processing state; values `'Not Seen'`, `'Rework'`, `'Seen'`. |
| **AA** / **Account Aggregator** | RBI-licensed data aggregator for consented bank-statement fetch. |
| **IMD** | Initial Margin Deposit — fee collected before processing. |
| **PMLA** | Prevention of Money Laundering Act check. |
| **PEP** | Politically Exposed Person check. |

---

## Channels & Tools

| Tool | What it is in LAP context |
|---|---|
| **LSQ** / **LeadSquared** | The CRM/panel where credit users work cases. |
| **LOS** | Loan Origination System — backend that owns stage transitions and rules. |
| **LMS** | Loan Management System — receives the case post Push-to-LMS. |
| **LSQ Push** / **Push to LMS** | Final stage transition; sends the loan to LMS for booking. |
| **Finbox** | Eligibility / offer engine; sets Programme + Waiver flags at leadgen. |
| **G-Chat** | Internal chat. Default channel fallback in Contacts blocks. |
| **WhatsApp groups** | Out-of-band ops channel; commonly cited fallback. |

---

## Common Authors / Contacts (for the Contacts block)

These are humans who reliably own LAP product / process changes. Use their first names in the Contacts block when relevant.

| Person | Role context |
|---|---|
| **Harshavardhan** | PM — LAP Query Module, Third Party Triggers spec |
| **Shweta** (Iyengar) | PM — Internal Top-Up PRD, Lead-gen PRD, DigiLocker auto-update spec (LAP-2222 reporter) |
| **Paras** (Arora) | PM — DigiLocker journey changes (LAP-2180/2181 reporter) |
| **Vatsala** (S) | PM — original LOS for LAP PRD |
| **Roshni** (Singh) | PM — Leadgen / SM CRM |
| **Vishaw** (Kashyap) | Author — canonical LAP LOS Confluence space |
| **Prem, Kiran, Vinesh, Anjali, Mahesh** | Product support roster (per Relook release note) |

If a release note's feature has a clear PM owner, name them. If it's a multi-PM bundle, use the product support roster.

---

## Stage Sub-States (for query/send-back routing)

When a stage carries a "pending_sales", "pending_credit", or "pending_vendor" sub-state, write it as `<Stage> | pending_<group>`:

- `Credit PD pending_sales`
- `Credit PD pending_credit`
- `Legal/Technical/RCU/FI pending_vendor`
- `Final sanction pending_sales`
- `Final sanction pending_credit`
- `Disbursement Kit pending_sales`
- `Disbursement Kit pending_credit`

These are the values in the Query Stage dropdown post LAP-1903.

---

## Post Sanction substructure (verified in LAP-2154)

| Component | Verbatim panel string |
|---|---|
| Stage | `Post Sanction` |
| Tab | `Post Sanction` |
| Subtabs | `Repayment Details`, `Disbursement Details` (extend on next ticket touching this) |
| Form (on Repayment Details subtab) | `Repayment & Disbursal Details Capture - v5` |
| Dropdown trigger (e-mandate) | `'Initiate E-Mandate Registration?'` |
| Dropdown values | `Yes`, `No` |

Source: LAP-2154 (LSQ Renach Handling, LIVE 2026-05).

---

## E-Mandate / Renach vocabulary

| Term | Meaning |
|---|---|
| **Renach** | Re-NACH. Re-using a customer's existing approved e-mandate for a new loan instead of generating a fresh link. |
| **'mandate_amount'** | The authorised amount on the existing approved mandate. |
| **'mandate_expiry_date'** | The expiry date on the existing approved mandate. |
| **'mandate_approved_date'** | The date the existing mandate was approved. |
| **'mandate_frequency'** | Mandate-level frequency (`monthly`, etc.). |
| **'enach_reference_number'** | The unique mandate reference. The latest such reference is sent in the Push-to-LMS request body. |
| **'enach_session_id'** | Internal session ID — NOT mapped to opportunity / repayment activity. |
| **'enach_status'** | Callback status (`Success`). |
| **'auth_mode'** | Mandate auth mode (`debit`). |
| **'juspay_pg_reference'** | Payment-gateway internal reference — NOT mapped. |
| **'user_bank_reference_number'** | Customer-bank-side mandate reference. |
| **'status'** | Callback status field (`APPROVED` is the success-eligible value). |

When a release note quotes any of these, use the verbatim form in `'single quotes'`.

Source: LAP-2154.

---

## Mandate buffer policy (LAP-2154)

| Scenario | Buffer |
|---|---|
| Initial mandate (first time for a customer) | 5 years past the last EMI date |
| Revised mandate request | 4 years past the last EMI date — checks if the existing mandate covers it; if yes, re-use; if no, send link |
| New mandate generated after fresh link | Reverts to the 5-year buffer (initial-mandate policy) |

Conditions for re-use (BOTH must be true):

- Sanction Loan amount ≤ `'mandate_amount'`
- Last EMI date + 5 years ≤ `'mandate_expiry_date'`

If either fails, a fresh E-Mandate link is generated.

Source: LAP-2154.

---

## Update Protocol

When you encounter a new stage, role, or system string in a Jira ticket or Confluence page:

1. Verify it against the LSQ panel (or the source Confluence page).
2. Add it to the relevant section above.
3. Cite the source (Confluence pageId + section, or Jira ticket key).
4. Increment the version footer.

> **Glossary version 1.1 — 2026-05-04** — v1.1 adds Post Sanction substructure, E-Mandate/Renach vocabulary, and mandate buffer policy from LAP-2154. Earlier: stages from Confluence 1088716805, roles from LAP Query Module page 1101660180, system strings from LAP-2180 / 2181 / 2222.
