# Kissht Domain Knowledge

## Table of Contents
1. [Company & Products](#company-products)
2. [LAP LOS Journey Stages](#lap-los-journey)
3. [System Architecture](#system-architecture)
4. [Team Roles & Abbreviations](#team-roles)
5. [Feature Categories](#feature-categories)
6. [Terminology Glossary](#terminology)
7. [Common Ticket Patterns](#ticket-patterns)

---

## Company & Products

**Kissht** (now Ring) is a BNPL/digital lending fintech company in India. Key products:

- **LAP** (Loan Against Property) — Secured lending product with full LOS (Loan Origination System)
- **UP/Ring** — Unsecured personal lending product
- **Saral** / **LSQ** (LeadSquared) — Digital lead generation and onboarding platform
- **LOS Panel** — Internal loan origination and management system
- **Mavis** — Internal system for user whitelisting and eligibility

## LAP LOS Journey Stages

The loan lifecycle follows these stages (in order):

```
Lead Created (Saral/LSQ)
    ↓
Applicant Valid
    ↓ (KYC, Identity Verification)
Applicant Onboarded
    ↓ (Document Collection, PD Visit)
CPA Verified (Credit Policy Assessment)
    ↓ (Bureau Pull, BRE)
BRE Approved (Business Rule Engine)
    ↓ (Credit Evaluation)
Sales PD Complete (Personal Discussion)
    ↓ (Property & Home Verification)
IPA Pending (In-Principle Approval)
    ↓ (Sanction Decision)
Final Sanction Approval Pending (NCM)
    ↓
Conditional Approved / Sanctioned
    ↓ (Disbursement Processing)
Disbursed
    ↓
Closed / Written Off
```

**Key transitions where most bugs occur**:
- Saral → LOS handoff (document sync, data mapping)
- Applicant Onboarded → CPA (KYC validation, document completeness)
- BRE → Sanction (bureau logic, waiver calculations)
- Sanction → Disbursement (fee calculations, form blocking)

## System Architecture

```
EXTERNAL                    INTERNAL
┌─────────┐                ┌──────────┐
│ Saral   │ ──documents──→ │ LOS      │
│ (LSQ)   │ ←──queries───  │ Panel    │
└─────────┘                └──────────┘
     │                          │
     │                     ┌──────────┐
     └──lead data───────→  │ Document │
                           │ Manager  │
                           └──────────┘
                                │
┌─────────┐                ┌──────────┐
│ Bureau   │ ←──pull──────  │ Credit   │
│ Services │ ──score──────→ │ Engine   │
│ (CIBIL)  │               │ (BRE)    │
└─────────┘                └──────────┘
                                │
┌─────────┐                ┌──────────┐
│ Account  │ ←──redirect── │ Financial│
│ Aggregator│ ──bank data→ │ Data     │
└─────────┘                └──────────┘
                                │
┌─────────┐                ┌──────────┐
│ Mavis   │ ←──whitelist── │ Eligibility│
│ System  │ ──status─────→ │ Engine    │
└─────────┘                └──────────┘
```

**Integration hotspots** (frequent bug sources):
- Saral ↔ LOS document sync
- LSQ ↔ LAP data mapping (field formats, dropdown values)
- Bureau service ↔ BRE (score thresholds, waiver logic)
- Account Aggregator ↔ Co-applicant flows (redirect URLs)

## Team Roles & Abbreviations

| Abbreviation | Full Name | Responsibility |
|-------------|-----------|---------------|
| **Sales RM** | Sales Relationship Manager | Field sales, PD visits, document collection |
| **BCM** | Branch Credit Manager | Credit evaluation, sanction decisions |
| **CPA** | Credit Policy Assessment | Credit policy verification |
| **CCPA** | Central CPA | Centralized credit assessment |
| **NCM** | National Credit Manager | Final sanction authority |
| **Central Ops** | Central Operations | Centralized loan processing |
| **Branch Ops** | Branch Operations | Branch-level loan processing |
| **Finance** | Finance Team | Disbursement, fee management |
| **IT/Dev** | Development Team | System implementation |
| **QA** | Quality Assurance | Testing & validation |
| **Training** | Training & Development | SOP creation, user training |
| **BA** | Business Analyst | Requirements, process analysis |
| **PM** | Product Manager | Product strategy, backlog |

## Feature Categories

Standard categories for classifying LAP tickets:

| Category | Description | Key Systems |
|----------|-------------|-------------|
| **Document Management** | Upload, replace, cleanup, sync of documents | LOS Doc Manager, Saral |
| **KYC & Identity** | Aadhaar, selfie, address verification | KYC Module, Liveness |
| **Sales PD & Property** | Personal Discussion visits, property docs | Sales PD Module |
| **Credit & Bureau** | CIBIL pulls, waiver logic, CAM reports | Bureau Service, BRE |
| **Transaction & Sanction** | Loan status, sanction pipeline, fees | Sanction Engine |
| **LOS Panel & Operations** | UI, Smart View, form fixes | LOS Panel UI |
| **Multi-Applicant & Top-Up** | Co-applicant, top-up journeys | Applicant Module |
| **Data Consistency** | Field mapping, format standardization | Cross-system |
| **General Fixes** | Miscellaneous UI and workflow fixes | Various |
| **BRE & Eligibility** | Business rules, program eligibility | BRE Engine |
| **Integration** | Saral-LOS, LSQ-LAP, Mavis integration | API Layer |

## Terminology Glossary

| Term | Definition |
|------|-----------|
| **LAP** | Loan Against Property — secured lending product |
| **LOS** | Loan Origination System — internal processing platform |
| **Saral** | Digital lead generation platform (LeadSquared based) |
| **LSQ** | LeadSquared — CRM/lead management system |
| **BRE** | Business Rule Engine — automated eligibility/risk scoring |
| **CPA** | Credit Policy Assessment — verification step |
| **CAM** | Credit Assessment Memo — document summarizing credit evaluation |
| **KFS** | Key Fact Statement — regulatory document for borrowers |
| **PD** | Personal Discussion — field verification visit |
| **AA** | Account Aggregator — financial data sharing framework |
| **CIBIL** | Credit bureau score (TransUnion CIBIL in India) |
| **IPA** | In-Principle Approval — conditional loan approval |
| **NCM** | National Credit Manager — highest sanction authority |
| **OSV** | Original Seen & Verified — document verification stamp |
| **BPI** | Borrower Protection Insurance |
| **EMI** | Equated Monthly Installment |
| **TAT** | Turnaround Time |
| **SOP** | Standard Operating Procedure |
| **IC** | Income Contributor — co-applicant type |
| **Smart View** | LOS panel filtered dashboard view |
| **Query Module** | System for raising and resolving data queries |
| **Notional Fees** | Estimated fee calculation before final sanction |
| **Waiver** | Exception to standard credit rules |
| **Tranche** | Partial disbursement of sanctioned amount |
| **Financier** | Lending institution partner |
| **Top-Up** | Additional loan on existing mortgage |
| **Concurrent** | Simultaneous loan processing |
| **Whitelist** | Pre-approved list of eligible users |
| **Bureau Pull** | Fetching credit score from bureau services |
| **CAF** | Customer Application Form |

## Common Ticket Patterns

Understanding recurring ticket types helps in classification:

**Pattern 1: Saral-LOS Document Sync**
- Documents uploaded in Saral don't appear in LOS
- Document replacement from query module fails
- Fix: Data pipeline repair between systems

**Pattern 2: Field Mapping Inconsistency**
- Same field has different dropdown values in different stages
- Date formats inconsistent between lead gen and verification
- Fix: Standardize mappings across journey stages

**Pattern 3: Co-Applicant Edge Cases**
- PD tasks not generated for IC co-applicants
- AA redirect URLs wrong for co-applicant context
- Rejected co-applicants still visible in forms
- Fix: Extend logic to handle multi-applicant scenarios

**Pattern 4: Bureau/Credit Logic Errors**
- Score threshold comparisons using wrong operators
- Waiver logic not handling boundary values
- CAM reports showing stale scores after re-pull
- Fix: Correct business rule implementation

**Pattern 5: Form/UI Blocking Issues**
- Mandatory fields blocking submission incorrectly
- Dropdowns not visible in certain journey modes
- Forms not loading required data
- Fix: Form state management and conditional rendering

**Pattern 6: Financial Calculation Errors**
- Fee deductions calculating incorrectly
- Insurance rows missing from statements
- Tranche ordering wrong
- Fix: Business logic correction in calculation engines

---

## RBI Regulatory Compliance Framework

Release notes for a regulated fintech MUST account for these regulatory requirements. Flag any ticket touching these areas for Leadership + BA + Ops guides.

### RBI Digital Lending Directions (2022, updated 2024-2025)

| Requirement | Impact on Release Notes | Affected Stakeholders |
|------------|------------------------|----------------------|
| **Key Fact Statement (KFS)** | Any change to loan terms display, fee disclosure, or interest rate presentation MUST be flagged as compliance-critical | Leadership, BA, Training, Ops |
| **Audit Trail** | Changes to logging, data persistence, or transaction history must note compliance implications | Dev, Ops, BA |
| **Data Localization** | Any change to where borrower data is stored or processed (India-only requirement) | Dev, Ops, Leadership |
| **Cooling-off Period** | Changes to loan cancellation flows or timelines | Training, BA, PM |
| **Grievance Redressal** | Changes to complaint handling, escalation, or resolution workflows | Ops, Training, PM |
| **LSP Disclosure** | Changes to lending service provider identification in communications | Training, BA |
| **Digital Consent** | Changes to e-sign, OTP verification, or consent collection | QA, Dev, BA |

### Account Aggregator (AA) Framework

The AA ecosystem is a critical integration point for Kissht LAP:

```
Borrower → Consent Artifact → FIP (Bank)
                ↓
            FIU (Kissht) ← Financial Data (encrypted)
                ↓
            Financial Analysis → BRE Input
```

Key AA terminology for release notes:
- **FIP** — Financial Information Provider (banks holding customer data)
- **FIU** — Financial Information User (Kissht, consuming AA data)
- **Consent Artifact** — Digital permission record with expiry
- **AA Redirect** — URL flow for multi-party consent (frequent bug source for co-applicants)
- **Data Fetch** — Pulling bank statements via AA after consent

Common AA-related ticket patterns:
- Redirect URL mismatch for co-applicant AA flows
- Consent expiry handling (auto-revoke vs manual)
- Bank statement parsing failures (different bank formats)
- AA session timeout during multi-applicant journeys

### CIBIL/Bureau Integration Details

| Bureau Component | Description | Ticket Keywords |
|-----------------|-------------|-----------------|
| **Score Pull** | Fetching credit score from TransUnion CIBIL | "bureau pull", "CIBIL score", "credit check" |
| **Score Threshold** | Minimum score for eligibility (varies by program) | "score threshold", "minimum score", "eligibility" |
| **Waiver Logic** | Exception rules for below-threshold scores | "waiver", "bureau waiver", "score waiver" |
| **CAM Report** | Credit Assessment Memo generation from bureau data | "CAM", "credit assessment", "CAM report" |
| **Multi-Bureau** | Handling scores from multiple bureaus | "Experian", "Equifax", "multi-bureau" |
| **Soft Pull** | Pre-qualification check without hard inquiry | "soft pull", "pre-qualification" |

---

## LAP vs UP Product Differences

When classifying tickets, distinguish between LAP and UP/Ring:

| Dimension | LAP (Loan Against Property) | UP/Ring (Unsecured Personal) |
|-----------|---------------------------|------------------------------|
| **Ticket prefix** | LAP-XXXX | UP-XXXX or RING-XXXX |
| **Journey length** | 10+ stages, 15-60 days | 3-5 stages, instant to 48 hours |
| **Document volume** | 20+ document types (property, income, identity) | 3-5 documents (PAN, Aadhaar, selfie) |
| **Verification** | Physical PD visit, property valuation, legal check | Digital-only, automated verification |
| **Bureau complexity** | Multi-applicant bureau pulls, waiver matrices | Single applicant, binary pass/fail |
| **Sanction authority** | Multi-level (BCM → NCM → Committee) | Automated BRE decision |
| **Integration surface** | Saral, LOS, Bureau, AA, Mavis, Property APIs | Simpler stack, fewer integrations |
| **Ticket patterns** | Document sync, co-applicant edge cases, sanction pipeline | App flow bugs, instant decision logic, retry handling |

### Data Quality Observations (from 1839-ticket analysis)

From analysis of historical Kissht ticket data:
- **73.6% of tickets have no linked epic** — Classification must rely on ticket summary keywords, not epic grouping
- **Average cycle time**: 42.5 days (LAP), highly variable (5-120 days)
- **Top ticket categories by volume**: Document Management (22%), LOS Panel (18%), KYC (14%), Credit/Bureau (12%)
- **Most common assignee pattern**: 3-4 developers handle 60%+ of tickets — recognize key contributors in guides
- **Seasonality**: Ticket volume spikes at quarter-end (March, June, September, December)
- **Bug:Story ratio**: Approximately 2:1 — most releases are fix-heavy, not feature-heavy

---

## Kissht System Architecture (Expanded)

### Service Dependencies Map

```
                    ┌─────────────────────────────────────┐
                    │           EXTERNAL SERVICES          │
                    ├────────┬──────────┬─────────────────┤
                    │ Bureau │   AA     │  Payment GW     │
                    │ (CIBIL)│(Setu/   │  (Razorpay/     │
                    │        │ OneMoney)│   Cashfree)     │
                    └───┬────┴────┬─────┴────┬────────────┘
                        │         │          │
┌─────────┐         ┌───┴─────────┴──────────┴──┐
│  Saral   │──────→  │     LAP LOS BACKEND       │
│  (LSQ)   │←──────  │  ┌──────┬──────┬────────┐ │
│ Lead Gen │         │  │ BRE  │ Doc  │ Sanction│ │
│ Portal   │         │  │Engine│Mgmt  │ Engine  │ │
└──────────┘         │  └──────┴──────┴────────┘ │
                     └──────────┬────────────────┘
                                │
                     ┌──────────┴────────────────┐
                     │      LOS PANEL (UI)       │
                     │  ┌──────┬──────┬────────┐ │
                     │  │Smart │ Forms│ Query  │ │
                     │  │Views │      │ Module │ │
                     │  └──────┴──────┴────────┘ │
                     └──────────┬────────────────┘
                                │
                     ┌──────────┴────────────────┐
                     │       MAVIS SYSTEM         │
                     │  Whitelisting & Eligibility│
                     └───────────────────────────┘
```

### Common Integration Failure Modes

| Integration Point | Failure Mode | Typical Ticket Pattern |
|-------------------|-------------|----------------------|
| Saral → LOS | Document sync delay/loss | "documents not appearing", "sync failed" |
| LSQ → LAP | Field mapping mismatch | "dropdown values wrong", "date format" |
| LOS → Bureau | Timeout on bureau pull | "bureau timeout", "CIBIL error" |
| LOS → AA | Redirect URL mismatch | "AA redirect failed", "consent expired" |
| BRE → Sanction | Incorrect waiver calculation | "waiver logic", "eligibility error" |
| LOS → Payment GW | Fee calculation mismatch | "fee incorrect", "payment failed" |
| Mavis → LOS | Whitelist status stale | "whitelist not updated", "eligibility stale" |

---

## LAP Loan Journey Deep Dive

### Document Types Required at Each Stage

| Stage | Document Category | Count | Common Ticket Patterns |
|-------|------------------|-------|----------------------|
| **Lead Created** | Basic demographics (name, phone, PAN) | 3-5 | LSQ field mapping errors |
| **Applicant Valid** | KYC (Aadhaar, PAN, selfie) | 5-8 | eKYC failure, liveness check bugs |
| **Applicant Onboarded** | Income docs (salary slips, ITR, bank statements) | 8-12 | Document sync Saral→LOS |
| **CPA Verified** | Property docs (title deed, encumbrance cert) | 10-15 | Missing mandatory field blocking |
| **BRE Approved** | Bureau reports (CIBIL, Experian) | 2-3 | Score threshold logic errors |
| **Sales PD Complete** | PD report, property photos, home visit notes | 5-8 | PD task not generated for co-applicants |
| **IPA Pending** | Valuation report, legal opinion | 3-5 | Valuation data not syncing |
| **Sanctioned** | Sanction letter, KFS, fee breakdown | 4-6 | Fee calculation errors |
| **Disbursed** | Disbursement memo, insurance, account details | 3-5 | Tranche ordering bugs |

### CIBIL Score Requirements by Program

| Program Type | Minimum Score | Waiver Available | Waiver Authority |
|-------------|---------------|-----------------|-----------------|
| Standard LAP | 700+ | No | — |
| Premium LAP | 650+ | Yes (case-by-case) | NCM |
| Top-Up | 680+ | Yes (if existing good record) | BCM |
| Balance Transfer | 720+ | No | — |
| Self-Employed | 680+ | Yes (with collateral strength) | NCM Committee |

*Note: Exact thresholds from ticket data. Always tag as [H] unless verified from policy document.*

### Account Aggregator (AA) Ecosystem — Detailed

| AA Provider | Status | Integration Notes |
|------------|--------|-------------------|
| **Setu** | Primary | Most Kissht LAP flows use Setu for AA |
| **OneMoney** | Secondary | Backup for bank coverage gaps |
| **Finvu** | Evaluation | Under consideration for expansion |
| **CAMS** | Limited | Used for mutual fund data only |

**AA Flow Timing Requirements**:
- Consent validity: 24 hours (configurable, typically set to 24h for LAP)
- Data fetch timeout: 30 seconds per FIP
- Multi-applicant sequential flow: Each applicant consents separately
- Retry policy: 3 attempts with exponential backoff (2s, 4s, 8s)

### BRE (Business Rule Engine) Pattern Details

The BRE evaluates loan eligibility through these rule layers:

```
Layer 1: Basic Eligibility
    Age >= 21 AND Age <= 65 at maturity
    Indian citizen / resident
    PAN verified
    Not in negative list
        ↓ Pass
Layer 2: Bureau Check
    CIBIL score >= program threshold
    No active defaults > 90 DPD
    Total existing EMI/income ratio < 50%
    Bureau waiver rules (if applicable)
        ↓ Pass
Layer 3: Property Validation
    Property type in approved list
    Location in serviceable PIN codes
    Clear title (no litigation)
    Valuation within LTV limits
        ↓ Pass
Layer 4: Income Assessment
    Documented income meets FOIR requirement
    Employment stability (min 2 years for salaried)
    Business vintage (min 3 years for self-employed)
        ↓ Pass → IPA Eligible
```

**Common BRE ticket patterns**:
- Threshold comparison using wrong operator (`<` vs `<=`)
- Waiver logic not handling boundary values
- Multi-applicant income aggregation incorrect
- Program-specific rules not applied correctly
- Stale scores after bureau re-pull

### CAM (Credit Assessment Memo) Components

| Section | Content | Data Sources |
|---------|---------|-------------|
| **Applicant Profile** | Demographics, employment, income | Saral + KYC module |
| **Bureau Summary** | CIBIL score, active loans, DPD history | Bureau service |
| **Property Details** | Type, location, valuation, LTV | Property module + valuation report |
| **Income Analysis** | Gross income, deductions, FOIR | Bank statements (AA) + salary slips |
| **Risk Factors** | Negative findings, concentration risk | BRE output + manual review |
| **Recommendation** | Approve / Reject / Conditional with terms | BCM/NCM decision |

### Digital Cycle Time Benchmarks

| Metric | Target | Actual (from ticket data) | Notes |
|--------|--------|--------------------------|-------|
| Lead to Applicant Valid | < 1 day | 0.5 days | Mostly automated |
| Applicant Valid to Onboarded | 2-3 days | 3.5 days | KYC + document collection |
| Onboarded to BRE | 1-2 days | 2 days | Bureau pull + BRE run |
| BRE to Sales PD | 3-5 days | 5 days | Field visit scheduling |
| Sales PD to IPA | 2-3 days | 4 days | Property valuation |
| IPA to Sanction | 1-3 days | 3 days | NCM approval queue |
| Sanction to Disbursal | 1-2 days | 2 days | Fee processing + account setup |
| **Total Lead to Disbursal** | **7-15 days** | **~20 days** | Gap = operational improvement target |

---

## RBI Regulatory Deep Dive (2025-2026)

### Key Circulars Affecting Kissht LAP

| Circular | Reference | Impact on Release Notes |
|----------|-----------|------------------------|
| Digital Lending Guidelines | RBI/2022-23/111 (updated 2025) | KFS display, LSP disclosure, data localization |
| Account Aggregator Framework | RBI/2021-22/76 | AA consent, data fetch, FIP/FIU roles |
| Fair Practices Code | RBI/2003/FPC (updated 2024) | Loan agreement terms, foreclosure charges |
| KYC Master Direction | RBI/2016/KYC (updated 2025) | Video KYC, re-KYC timelines, CKYC |
| Outsourcing Guidelines | RBI/2024/Outsourcing | Third-party vendor management, LSP oversight |

### Compliance Ticket Classification Rules

When a ticket touches ANY of these areas, it MUST be flagged as compliance-critical:

```python
COMPLIANCE_TRIGGERS = {
    "kfs": "Key Fact Statement — RBI/2022-23/111",
    "consent": "Digital Consent — RBI Digital Lending Guidelines",
    "data localization": "Data Storage — RBI Data Localization Directive",
    "audit trail": "Transaction Logging — RBI Fair Practices Code",
    "cooling off": "Loan Cancellation — RBI/2022-23/111 (3-day window)",
    "grievance": "Complaint Handling — RBI Fair Practices Code",
    "lsp disclosure": "LSP Identity — RBI Digital Lending Guidelines",
    "e-sign": "Digital Signature — IT Act 2000 + RBI Guidelines",
    "interest rate": "Rate Disclosure — RBI Transparency Requirements",
    "penal charges": "Penal Interest — RBI/2023-24 (no penal interest, only charges)",
    "foreclosure": "Prepayment — RBI Fair Practices Code (no prepayment penalty for floating)",
    "account aggregator": "AA Framework — RBI/2021-22/76",
}
```

**Escalation matrix for compliance tickets**:
1. Flag in QA guide as P1 regression test
2. Flag in BA guide with specific RBI circular reference
3. Flag in Leadership guide under "Compliance & Regulatory Notes"
4. Flag in Training guide as "Mandatory SOP Update"
5. Flag in Ops guide for monitoring and audit trail verification
