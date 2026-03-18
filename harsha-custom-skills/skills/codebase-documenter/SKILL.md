---
name: "Codebase Handoff Documenter V6"
description: |
  Merge V2's simplicity (linear flow, no broken deps), V5's intelligence (domain detection, explicit file loading),
  and research-analyst rigor (competing hypotheses, cross-validation, pre-mortem) into a single epistemic
  documentation pipeline for ANY single-agent Claude context (Code, Cowork, Cline, Cursor).

  Triggers: "generate a handoff doc", "document this codebase", "prepare for knowledge transfer",
  "create architecture documentation", "epistemic analysis of codebase", "pre-handoff audit",
  "compliance documentation (fintech/healthcare/enterprise)"
version: "6.1"
status: "stable"
target_contexts: ["Claude Code", "Cowork", "Cline", "Cursor"]
---

# CORE PHILOSOPHY (10 Unified Principles)

1. **Linear Simplicity**: Sequential pipeline (ANALYZE → DETECT → GATHER → GENERATE → VERIFY → OUTPUT). No multi-agent loops, no external dependencies in main flow. Fit in single context window.

2. **Epistemic Honesty**: Every claim tagged with confidence level (VERIFIED/HIGH/MEDIUM/LOW/UNKNOWN) + evidence quality (likelihood × source credibility).

3. **Evidence-First**: Source hierarchy: Code > Tests > Git History > Comments > Inference. Cross-validation required: never conclude on single source.

4. **Contrarian By Default**: For each architecture decision, explicitly state the competing hypothesis ("what if this pattern is actually wrong?").

5. **Domain-Aware Compliance**: Auto-detect fintech/healthcare/enterprise via explicit scoring matrix; generate domain-specific controls (PCI-DSS, HIPAA, SOC2, RBI).

6. **Provenance Tracking**: Every finding tagged [source: file:line] or [source: test:name]. Temporal validity (knowledge_as_of, review_triggers).

7. **Pre-Mortem Discipline**: Before finalizing, ask "If this handoff fails, what's the most likely reason?" Capture top 3 failure modes.

8. **Progressive Disclosure**: Readers choose depth (Quick Ref → Architecture → Deep Dive → Compliance). Not one wall of text.

9. **Mandatory File Loading**: Every phase explicitly specifies which reference/domain-mode files to load. No optional reads — if a phase says "LOAD:", the agent MUST read those files before proceeding.

10. **Minimum Output Depth**: Every section has a minimum word/paragraph count. Thin outputs are unacceptable. See OUTPUT DEPTH REQUIREMENTS below.

---

# CONFIDENCE LEVEL SYSTEM

| Level | Likelihood | Evidence Requirement | Example |
|-------|-----------|----------------------|---------|
| **VERIFIED** | >95% | Code + Tests + Git history + comment confirmation | "Primary key on user.id enforced by schema constraint AND test_user_creation_rejects_dup_id.py confirms" |
| **HIGH** | 80-95% | Code + Tests (at least 2 sources) | "Authentication uses bcrypt (confirmed in auth.py:42 AND test_login_success.py:15)" |
| **MEDIUM** | 50-80% | Code + 1 corroboration (comment/git/inference) | "Likely sharded by tenant_id (found in queries, not in explicit schema docs)" |
| **LOW** | 20-50% | Single source + inference gap | "Possibly cached (ttl variable in config, but no eviction test found)" |
| **UNKNOWN** | <20% | No code evidence or contradictory signals | "Replication strategy unclear (references suggest multi-region, code shows single region)" |

---

# SOURCE TAXONOMY (What Counts as a "Source")

Cross-validation requires multiple INDEPENDENT sources. Here is the exact definition of each source type:

## Source Type Definitions

| Source Type | What Qualifies | What Does NOT Qualify | Credibility Weight |
|-------------|---------------|----------------------|-------------------|
| **Code** | Executable logic at a specific file:line. Function bodies, class definitions, config values, SQL schemas, route handlers, middleware chains. | Comments above code. Import statements alone. Dead/unreachable code. | 1.0 (highest) |
| **Test** | Assertions in test files that verify behavior. `assert`, `expect`, `should`, mock configurations that reveal contract expectations. Must be a PASSING test or clearly intended to pass. | Test file existence without assertions. Skipped/disabled tests. Test helpers/fixtures (unless they reveal contracts). | 0.9 |
| **Git History** | Commit messages, PR descriptions, blame output showing authorship + date, merge commits revealing design timeline, revert commits showing rejected approaches. | Automated commits (dependabot, CI). Merge commits without meaningful messages. | 0.7 |
| **Comments** | Inline comments explaining WHY (not WHAT). TODO/FIXME/HACK/BUG markers. Docstrings describing intent. README sections about architecture. | Auto-generated JSDoc/Sphinx stubs. License headers. Commented-out code (treat as code artifact, not documentation). | 0.5 |
| **Inference** | Patterns deduced from naming conventions, file structure, dependency graph, or architectural similarity to known patterns. | Guesses without any code basis. Assumptions from external knowledge alone. | 0.3 (lowest) |

## Cross-Validation Rules (Explicit)

A "cross-validated claim" requires evidence from **2+ source types with combined credibility weight ≥ 1.5**.

**Examples:**
- Code (1.0) + Test (0.9) = 1.9 → VERIFIED ✓
- Code (1.0) + Git (0.7) = 1.7 → HIGH ✓
- Code (1.0) + Comment (0.5) = 1.5 → HIGH ✓ (barely)
- Code (1.0) + Inference (0.3) = 1.3 → MEDIUM ✗ (below threshold, needs more)
- Test (0.9) + Git (0.7) = 1.6 → HIGH ✓ (code-free but cross-validated)
- Comment (0.5) + Inference (0.3) = 0.8 → LOW ✗ (insufficient)

**The Confidence Matrix:**
```
       Code  Tests  Git  Comments  → Confidence
Claim    ✓     ✓    ✓      ✓      = VERIFIED (95%+)
         ✓     ✓    ✓      ✗      = VERIFIED (90%)
         ✓     ✓    ✗      ✗      = HIGH (85%)
         ✓     ✗    ✓      ✓      = HIGH (80%)
         ✓     ✗    ✓      ✗      = MEDIUM-HIGH (75%)
         ✓     ✗    ✗      ✓      = MEDIUM (65%)
         ✓     ✗    ✗      ✗      = MEDIUM (60%) — single source
         ✗     ✓    ✗      ✗      = LOW (40%)
         ✗     ✗    ✓      ✗      = LOW (30%)
         ✗     ✗    ✗      ✓      = LOW (25%)
         ✗     ✗    ✗      ✗      = UNKNOWN (inference only)
```

**Evidence Template (use for every major claim):**
```
Claim: "User authentication uses bcrypt with 12 rounds"
Source 1 [Code, 1.0]: auth/password.py:45 → bcrypt.hashpw(password, bcrypt.gensalt(12))
Source 2 [Test, 0.9]: test_auth.py:102 → assert password_hash generated with bcrypt
Combined weight: 1.9 → Confidence: VERIFIED
Competing hypothesis: Could be SHA-256 wrapped in bcrypt call (REJECTED: gensalt confirms bcrypt)
```

---

# DOMAIN DETECTION SCORING MATRIX

Domain detection uses an EXPLICIT point-per-signal system. No subjective judgment — count signals, sum points.

## Signal Tiers and Point Values

| Tier | Points | Description | Detection Method |
|------|--------|-------------|-----------------|
| **Tier 1: Definitive** | 10 pts each | Unambiguous domain indicators | Grep for exact patterns |
| **Tier 2: Strong** | 5 pts each | Clear domain relevance | Grep + file structure |
| **Tier 3: Supporting** | 2 pts each | Corroborating signals | Pattern matching |
| **Tier 4: Incidental** | 1 pt each | Weak but additive | Keyword presence |

## Fintech Signal Catalog

| Signal | Tier | Points | Detection Pattern |
|--------|------|--------|------------------|
| Payment gateway SDK (Razorpay, Stripe, Cashfree) | T1 | 10 | `import razorpay`, `stripe.Charge`, `cashfree` in requirements/package.json |
| Loan/EMI/lending models | T1 | 10 | Classes/tables named `Loan`, `EMI`, `Disbursement`, `Repayment` |
| PCI-DSS compliance code | T1 | 10 | Card masking, tokenization, PAN storage rules |
| RBI/NBFC regulatory references | T1 | 10 | `RBI`, `NBFC`, `DLG`, `LSP`, `digital_lending` in code/config |
| Credit score integration (CIBIL, Experian) | T2 | 5 | `cibil`, `experian`, `credit_score`, `bureau_pull` |
| KYC/Aadhaar/PAN verification | T2 | 5 | `aadhaar`, `pan_number`, `kyc_status`, `ekyc` |
| UPI/NEFT/RTGS/IMPS references | T2 | 5 | `upi_id`, `vpa`, `neft`, `rtgs`, `imps` |
| GST/Tax calculation | T2 | 5 | `gst`, `tax_rate`, `igst`, `cgst`, `sgst` |
| Idempotency keys on financial ops | T3 | 2 | `idempotency_key`, `X-Idempotency-Key` |
| Settlement/reconciliation logic | T3 | 2 | `settlement`, `reconcile`, `ledger_entry` |
| Webhook signature verification | T3 | 2 | `verify_signature`, `webhook_secret`, `hmac` |
| Interest rate calculations | T3 | 2 | `interest_rate`, `apr`, `reducing_balance` |
| Financial audit logging | T4 | 1 | `audit_log`, `transaction_log` |
| Currency formatting/handling | T4 | 1 | `INR`, `currency`, `amount_in_paise` |
| Data residency config | T4 | 1 | `data_residency`, region restrictions in config |

## Healthcare Signal Catalog

| Signal | Tier | Points | Detection Pattern |
|--------|------|--------|------------------|
| HIPAA compliance code | T1 | 10 | `hipaa`, PHI encryption, access controls with audit |
| Patient record models | T1 | 10 | `Patient`, `MedicalRecord`, `Diagnosis`, `Prescription` |
| HL7/FHIR integration | T1 | 10 | `hl7`, `fhir`, `Bundle`, `Observation`, `DiagnosticReport` |
| PHI/PII classification logic | T2 | 5 | PHI field markers, de-identification, Safe Harbor |
| Clinical workflow engines | T2 | 5 | Care plans, clinical pathways, order entry |
| EHR/EMR integration | T2 | 5 | `epic`, `cerner`, `allscripts`, `smart_on_fhir` |
| Consent management | T3 | 2 | `patient_consent`, `consent_form`, `opt_in` |
| Medical terminology/ICD codes | T3 | 2 | `icd10`, `snomed`, `loinc`, `cpt_code` |
| BAA (Business Associate Agreement) references | T4 | 1 | `baa`, `business_associate` |
| Minimum necessary standard logic | T4 | 1 | Field-level access restrictions on PHI |

## Enterprise Signal Catalog

| Signal | Tier | Points | Detection Pattern |
|--------|------|--------|------------------|
| SSO/SAML/OIDC integration | T1 | 10 | `saml`, `oidc`, `sso`, `okta`, `auth0` enterprise |
| Multi-tenant architecture | T1 | 10 | `tenant_id` in queries, tenant isolation, schema-per-tenant |
| SOC 2 audit controls | T1 | 10 | `soc2`, audit trail completeness, trust criteria references |
| RBAC/ABAC permission system | T2 | 5 | Role definitions, permission matrices, `has_permission` |
| LDAP/Active Directory integration | T2 | 5 | `ldap`, `active_directory`, `ad_group` |
| Data governance/retention policies | T2 | 5 | Retention schedules, deletion workflows, data classification |
| Microservice orchestration | T3 | 2 | Service mesh, API gateway routing, circuit breakers |
| Disaster recovery / RTO/RPO | T3 | 2 | Backup scripts, failover logic, DR config |
| Feature flags / environment config | T4 | 1 | `feature_flag`, `toggle`, environment-based config |
| SLA monitoring / uptime tracking | T4 | 1 | Uptime checks, SLA metrics, availability targets |

## Activation Rules

```
domain_score = sum(all matching signals for that domain)

ACTIVATION THRESHOLD: ≥ 15 points
MULTI-DOMAIN: Both domains activate if both score ≥ 15

If fintech_score ≥ 15 → Load domain-modes/fintech.md (MANDATORY)
If healthcare_score ≥ 15 → Load domain-modes/healthcare.md (MANDATORY)
If enterprise_score ≥ 15 → Load domain-modes/enterprise.md (MANDATORY)
If all scores < 15 → Use agnostic documentation mode (no domain-mode file needed)
```

**MANDATORY**: After scoring, present results to user:
```
"Domain Detection Results:
  Fintech: XX points (signals: [list top 5])
  Healthcare: XX points (signals: [list top 5])
  Enterprise: XX points (signals: [list top 5])

  Activated domains: [list]
  Loading domain-mode files: [list]

  Proceed? [Y/N]"
```

→ **Full signal catalogs with code examples**: Read `domain-modes/detection.md`

---

# 6-PHASE LINEAR PIPELINE

## PHASE 1: CODEBASE ANALYSIS (~15 min)
**Goal**: Extract structural patterns without bias.

**LOAD (MANDATORY — read these files before starting Phase 1):**
- `references/code-patterns.md` — architectural pattern identification
- `references/language-patterns.md` — language-specific parsing rules

**Steps:**
1. Scan directory structure, identify modules/services
2. List all entry points (main.py, index.ts, config.yaml, etc.)
3. Extract data flow: inputs → processing → outputs
4. Identify external dependencies (pip, npm, docker, cloud APIs)
5. Tag all file types: source code, tests, config, docs, infra
6. Count domain detection signals (see DOMAIN DETECTION SCORING MATRIX above)

**Output**: Raw analysis inventory (no conclusions yet) + domain signal counts

*Tools*: Glob, Read, Grep (pattern searches, no interpretation)

---

## PHASE 2: DOMAIN DETECTION & PLANNING (Human-in-Loop)
**Goal**: Score domain, load domain-mode files, present plan to user.

**LOAD (MANDATORY):**
- `domain-modes/detection.md` — full signal catalogs with code examples and edge cases

**Steps:**
1. Apply the DOMAIN DETECTION SCORING MATRIX (above) to Phase 1 inventory
2. For EACH domain, list every matching signal with its tier, points, and code location
3. Sum points per domain. Apply activation rules.
4. **For each activated domain**: Read the corresponding domain-mode file:
   - Fintech activated → `Read domain-modes/fintech.md` (MANDATORY, do NOT skip)
   - Healthcare activated → `Read domain-modes/healthcare.md` (MANDATORY, do NOT skip)
   - Enterprise activated → `Read domain-modes/enterprise.md` (MANDATORY, do NOT skip)
5. Present detection results + documentation plan to user
6. **WAIT FOR USER APPROVAL** before proceeding

**HUMAN PAUSE FORMAT:**
```
"=== DOMAIN DETECTION RESULTS ===

Fintech Score: 42 points
  T1 (10pts each): Razorpay SDK [src/payment.py:3], Loan models [src/models.py:45], PCI masking [src/utils.py:88]
  T2 (5pts each): CIBIL integration [src/credit.py:12], Aadhaar KYC [src/kyc.py:5]
  T3 (2pts each): Idempotency keys [src/payment.py:67]

Healthcare Score: 0 points
Enterprise Score: 8 points (below threshold)

→ Activated: FINTECH
→ Loaded: domain-modes/fintech.md (882 lines of PCI-DSS, RBI DLG, Indian payment ecosystem rules)

Documentation Plan:
  - Architecture overview with payment flow diagrams
  - PCI-DSS compliance mapping (12 requirements)
  - RBI Digital Lending Guidelines audit
  - PII inventory (Aadhaar, PAN, CIBIL)
  - Payment webhook flow documentation
  - Technical debt + compliance gaps
  - Pre-mortem failure analysis

Proceed? [Y/N]"
```

---

## PHASE 3: EVIDENCE GATHERING (Source Validation Hierarchy)
**Goal**: Build evidence inventory for every major claim, with cross-validated provenance.

**LOAD (MANDATORY):**
- `references/evidence-patterns.md` — how to read test assertions for behavioral contracts
- `references/cross-validation.md` — Denzin's triangulation adapted for code analysis
- `references/accuracy-verification.md` — fact-checking checklist

**Steps:**
1. **Code scan** (Credibility: 1.0): All architecture decisions, data handling, external integrations. Record file:line for every finding.
2. **Test analysis** (Credibility: 0.9): Constraints, edge cases, error handling, concurrency behavior. Record test name + assertion.
3. **Git history** (Credibility: 0.7): Design rationale (commits), deprecation timelines, migration patterns. Record commit hash + message.
4. **Comment analysis** (Credibility: 0.5): Intended behavior, known limitations, TODO/FIXME markers. Record file:line.
5. **Inference** (Credibility: 0.3): Patterns, likely intent, unverified assumptions. Record basis for inference.

**Cross-Validation Protocol (MANDATORY for every claim):**
For each claim, apply the Confidence Matrix:
- Sum credibility weights of all supporting source types
- If combined weight ≥ 1.5 → Claim is cross-validated
- If combined weight < 1.5 → Flag as needs-more-evidence or tag LOW/UNKNOWN
- For each HIGH+ claim, state the competing hypothesis (what if this is wrong?)

**Evidence Template (use for every section's key claims):**
```
Claim: "[specific claim about the codebase]"
Source 1 [Type, Weight]: [file:line or test:name] → [what it shows]
Source 2 [Type, Weight]: [file:line or test:name] → [what it shows]
Combined weight: X.X → Confidence: [LEVEL]
Competing hypothesis: [alternative explanation] → [why accepted/rejected]
```

**Minimum Evidence Requirements:**
- Architecture claims: ≥ 3 sources (code + test + git minimum)
- Security claims: ≥ 2 sources + explicit competing hypothesis
- Compliance claims: ≥ 2 sources + reference to specific regulation requirement
- Integration claims: ≥ 2 sources (code + test or code + config)

---

## PHASE 4: DOCUMENTATION GENERATION (Domain-Aware)
**Goal**: Write multi-format docs, confidence-tagged, with provenance. This is the LARGEST phase.

**LOAD (MANDATORY — read ALL of these before writing ANY documentation):**
- `references/cognitive-patterns.md` — how to explain complex flows to non-experts
- `references/output-formats.md` — multi-format output patterns
- `templates/architecture.md` — architecture section template
- `templates/handoff-package.md` — overall handoff package structure
- **IF fintech activated**: `domain-modes/fintech.md` (MUST re-read even if read in Phase 2 — this file contains the PCI-DSS mapping table, RBI DLG checklist, PII inventory template, and payment flow documentation patterns that MUST appear in output)
- **IF healthcare activated**: `domain-modes/healthcare.md` (MUST re-read — contains HIPAA mapping table, PHI classification, HL7/FHIR patterns)
- **IF enterprise activated**: `domain-modes/enterprise.md` (MUST re-read — contains SOC2 mapping, RBAC matrix, multi-tenancy documentation)
- **IF fintech activated**: `templates/compliance-mapping-template.md`, `templates/pii-inventory-template.md`, `templates/security-audit-template.md`
- **IF healthcare activated**: `templates/compliance-mapping-template.md`, `templates/security-audit-template.md`
- **IF enterprise activated**: `templates/compliance-mapping-template.md`, `templates/security-audit-template.md`

**CRITICAL INSTRUCTION**: The domain-mode files contain SPECIFIC tables, checklists, and templates that MUST appear in the output. Do NOT summarize them — USE them. For example:
- fintech.md contains a 12-row PCI-DSS requirements table → populate it with findings from Phase 3
- fintech.md contains RBI DLG 2022 checklist → fill in compliance status per requirement
- healthcare.md contains HIPAA safeguards tables → populate with discovered controls
- enterprise.md contains SOC2 trust criteria matrix → populate with code evidence

**For each section:**
1. State claim with confidence level + source tags
2. Include brief evidence summary (1-2 sentences)
3. Link to source file:line if code/test, or git commit if history
4. Add competing hypothesis if confidence < HIGH ("but consider: X might be the real pattern")

**REQUIRED SECTIONS (all outputs must include these):**

### Section 1: Executive Summary
- System purpose, tech stack, architecture style
- Key dependencies and integration points
- Domain classification + compliance requirements
- **Minimum depth: 300 words**

### Section 2: Architecture Overview
- Module/service boundaries with data flow
- Entry points and request lifecycle
- Database schema and data model relationships
- External integrations (APIs, message queues, caches)
- **Minimum depth: 500 words + at least 1 diagram (ASCII or Mermaid)**

### Section 3: Authentication & Security
- Auth mechanism (OAuth, JWT, session, API key)
- Authorization model (RBAC, ABAC, custom)
- Secret management (env vars, vault, hardcoded)
- Encryption (at rest, in transit, field-level)
- **Minimum depth: 400 words**

### Section 4: Data Flow & Processing
- Request→Processing→Response trace for main flows
- Error handling and retry patterns
- Async/background job patterns
- Caching strategy
- **Minimum depth: 400 words per major flow**

### Section 5: Domain-Specific Compliance (if domain activated)
**This section is MANDATORY if any domain scored ≥ 15 and must be the LARGEST section.**

**Fintech minimum requirements (if activated):**
- PCI-DSS compliance table (12 requirements, each with code evidence or gap flag) — minimum 600 words
- RBI Digital Lending Guidelines audit (each DLG requirement mapped to code) — minimum 400 words
- PII inventory (every PII field found: Aadhaar, PAN, phone, email, bank account — with storage method, encryption, access control) — minimum 300 words
- Payment flow documentation (entry→gateway→callback→settlement with sequence diagram) — minimum 400 words
- Indian payment ecosystem specifics (Razorpay/Cashfree/UPI integration details) — minimum 200 words

**Healthcare minimum requirements (if activated):**
- HIPAA safeguards mapping (Administrative, Physical, Technical) — minimum 600 words
- PHI classification inventory (18 HIPAA identifiers, which are present) — minimum 300 words
- HL7/FHIR integration documentation — minimum 300 words
- Patient consent workflow — minimum 200 words

**Enterprise minimum requirements (if activated):**
- SOC2 Trust Criteria mapping (CC, A1, PI1, C1, P1-P8) — minimum 600 words
- RBAC/IAM matrix — minimum 300 words
- Multi-tenant isolation documentation — minimum 300 words
- Audit trail completeness — minimum 200 words

### Section 6: Technical Debt & Known Issues
- TODO/FIXME/HACK inventory with severity ratings
- Dependency staleness report
- Architecture smell detection
- **Minimum depth: 300 words**

### Section 7: Configuration & Deployment
- Environment variables with descriptions
- Secret management approach
- Deployment assumptions (Docker, K8s, cloud)
- **Minimum depth: 300 words**

### Section 8: Pre-Mortem Analysis
- Top 3 failure modes (see PHASE 5)
- Mitigation for each
- **Minimum depth: 200 words**

### Section 9: Handoff Readiness Score
- Coverage, confidence, completeness metrics
- Score calculation (see PHASE 6)
- **Minimum depth: 100 words**

**TOTAL MINIMUM OUTPUT**:
- Without domain compliance: ~3,000 words minimum
- With one domain activated: ~5,000 words minimum
- With multiple domains: ~6,500 words minimum

---

## PHASE 5: VERIFICATION & PRE-MORTEM
**Goal**: Cross-validate claims, stress-test assumptions, identify failure modes.

**LOAD (MANDATORY):**
- `references/accuracy-verification.md` — fact-checking checklist
- `references/completeness-checklists.md` — ensures no critical sections are skipped

**Cross-Validation Checklist:**
- [ ] Every VERIFIED/HIGH claim checked against Confidence Matrix (≥ 1.5 combined weight)
- [ ] Competing hypotheses explicitly stated (not ignored)
- [ ] Architecture diagrams vs. actual code trace match (no gaps)
- [ ] Test coverage validates claimed constraints (spot-check 5 tests)
- [ ] Git history confirms design rationale (sample 3 significant commits)
- [ ] Domain-mode compliance tables are POPULATED (not empty templates)
- [ ] PII inventory lists EVERY field found (not just "PII is handled")
- [ ] Payment/clinical/audit flows have sequence diagrams (not just prose)

**Pre-Mortem** (Assumed failure date: 6 months post-handoff):
Ask: "If the recipient can't maintain/extend this codebase in 6 months, what's the most likely reason?"

Common failure modes:
1. Missing domain context (fintech/healthcare/enterprise complexity not documented)
2. Silent assumptions (code relies on implicit behavior; tests don't cover edge case)
3. Dependency rot (external APIs deprecated, library versions pinned without docs)
4. Lost rationale (why was this design chosen? What alternatives were rejected?)
5. Configuration blind spots (environment variables, secrets, deployment assumptions)
6. Compliance drift (regulations updated, code not — who monitors?)

**Document top 3 failure modes** with specific mitigation for each.

---

## PHASE 6: OUTPUT ASSEMBLY & HANDOFF READINESS SCORE
**Goal**: Multi-format delivery, scored for handoff completeness.

**LOAD (MANDATORY):**
- `references/output-formats.md` — format specifications
- `references/quick-reference.md` — quick reference card format
- `templates/handoff-package.md` — package structure

**Output Formats** (pick reader depth):
1. **Quick Reference** (1-2 pages): Diagrams, key entry points, critical dependencies, known limitations
2. **Architecture Overview** (5-10 pages): Domain context, design decisions (with competing hypotheses), data flow, external integrations
3. **Deep Dive** (20+ pages): Code walkthrough, test coverage analysis, configuration reference, compliance controls
4. **Compliance Addendum** (if fintech/healthcare/enterprise): Audit trails, encryption, consent, RBAC, SLA commitments

**Handoff Readiness Score Formula:**
```
coverage_score = (sections_documented / sections_required) × 100
confidence_avg = (sum of all confidence levels mapped to 0-100) / count
  where: VERIFIED=95, HIGH=85, MEDIUM=65, LOW=35, UNKNOWN=10
completeness = (verified_claims + high_claims) / (all claims) × 100

readiness_score = (coverage_score × 0.4) + (confidence_avg × 0.4) + (completeness × 0.2)
```
Range: 0-100. Target: ≥75 for safe handoff. <60 = requires rework.

**YAML Frontmatter (on each doc):**
```yaml
knowledge_as_of: "YYYY-MM-DD"
valid_until: "YYYY-MM-DD"  # 3-month TTL
review_triggers:
  - "Any modification to auth system"
  - "Addition of new external API"
  - "Schema migration"
  - "Regulatory update (RBI/HIPAA/SOC2)"
last_reviewer: "[Your name]"
next_review_date: "YYYY-MM-DD"
```

**Output Checklist (EVERY item must be checked before delivery):**
- [ ] Knowledge_as_of date, valid_until, review_triggers in YAML
- [ ] Every section includes confidence tags + source citations
- [ ] Competing hypotheses documented (not assumptions)
- [ ] Pre-mortem top 3 failure modes included
- [ ] Domain-specific compliance section present + tables POPULATED (if domain activated)
- [ ] PII inventory present with field-level detail (if fintech/healthcare)
- [ ] Payment/clinical flow diagrams present (if fintech/healthcare)
- [ ] Handoff readiness score calculated + interpretation
- [ ] Total output meets MINIMUM DEPTH requirements
- [ ] Reader can answer: "What does this code do?", "Why was it built this way?", "What breaks easily?"

---

# SAFEGUARD CHECKLIST (Run Before Delivery)

This checklist prevents the agent from missing critical steps. Run through EVERY item:

```
□ Phase 1: Did I load references/code-patterns.md AND references/language-patterns.md?
□ Phase 2: Did I load domain-modes/detection.md?
□ Phase 2: Did I present explicit point-per-signal scoring to the user?
□ Phase 2: For each activated domain, did I load the corresponding domain-mode file?
□ Phase 3: Did I load references/evidence-patterns.md AND references/cross-validation.md?
□ Phase 3: Does every VERIFIED/HIGH claim have ≥ 2 source types with combined weight ≥ 1.5?
□ Phase 3: Did I state competing hypotheses for architecture decisions?
□ Phase 4: Did I re-load domain-mode files before writing compliance sections?
□ Phase 4: Did I load ALL required templates for the activated domain?
□ Phase 4: Is my compliance section the LARGEST section (if domain activated)?
□ Phase 4: Did I POPULATE compliance tables with actual findings (not empty templates)?
□ Phase 4: Does each section meet its MINIMUM DEPTH requirement?
□ Phase 5: Did I load references/accuracy-verification.md AND references/completeness-checklists.md?
□ Phase 5: Did I write a pre-mortem with top 3 failure modes?
□ Phase 6: Did I calculate handoff readiness score?
□ Phase 6: Is the total output ≥ 3,000 words (no domain) or ≥ 5,000 words (with domain)?
□ Phase 6: Did I include YAML frontmatter with temporal validity?
```

If ANY checkbox is unchecked, GO BACK and complete it before delivering.

---

# REFERENCE FILE ROUTING TABLE

When you need...                          | Read this first... | Phase
------------------------------------------|------------------------------------|---------
Architecture pattern identification      | `references/code-patterns.md` | Phase 1
Language-specific parsing rules          | `references/language-patterns.md` | Phase 1
Domain classification heuristics         | `domain-modes/detection.md` | Phase 2
Fintech compliance (PCI-DSS, RBI, PII)  | `domain-modes/fintech.md` | Phase 2, 4
Healthcare compliance (HIPAA, PHI)       | `domain-modes/healthcare.md` | Phase 2, 4
Enterprise compliance (SOC2, IAM)        | `domain-modes/enterprise.md` | Phase 2, 4
How to read test assertions              | `references/evidence-patterns.md` | Phase 3
Cross-validation methodology             | `references/cross-validation.md` | Phase 3
Explaining complex flows                 | `references/cognitive-patterns.md` | Phase 4
Documentation templates                  | `templates/[type].md` | Phase 4
Fact-checking claims                     | `references/accuracy-verification.md` | Phase 3, 5
Completeness verification                | `references/completeness-checklists.md` | Phase 5
Output format specifications             | `references/output-formats.md` | Phase 6
Quick reference card format              | `references/quick-reference.md` | Phase 6
Security documentation patterns          | `references/security-documentation.md` | Phase 3, 4
Technical debt classification            | `references/technical-debt.md` | Phase 4
Architecture decision records            | `templates/adr-template.md` | Phase 4
PII inventory template                   | `templates/pii-inventory-template.md` | Phase 4
Compliance mapping template              | `templates/compliance-mapping-template.md` | Phase 4

---

# ANTI-PATTERNS TO AVOID

1. **Assumption Stacking**: Never build conclusions on unverified premises. Always cite code or test.
2. **Single-Source Confidence**: NEVER tag a claim VERIFIED on code alone. Require cross-validation (weight ≥ 1.5).
3. **Lost Rationale**: Don't document *what* without *why*. Use git history to capture intent.
4. **Silent Defaults**: Call out implicit assumptions (env vars, library defaults, timing dependencies).
5. **Incomplete Compliance**: If domain activated, missing compliance audit = CRITICAL GAP. The compliance section must be the LARGEST section.
6. **No Pre-Mortem**: Skipping failure mode analysis guarantees surprise failures post-handoff.
7. **Competing Hypotheses Ignored**: Stating alternative explanations and not addressing them = lazy analysis.
8. **Empty Templates**: Never output compliance tables with placeholder text. Every cell must contain actual findings or "NOT FOUND — [reason]".
9. **Thin Output**: Output below minimum depth requirements means the agent skipped evidence. Go back and gather more.
10. **Passive File Loading**: If a phase says "LOAD:", the agent MUST read those files. "I already know this" is not acceptable — the files contain specific tables/checklists that must be used.

---

# SKILL STACKING (Experimental)

When used alongside other skills, this skill benefits from:

**Research-Analyst Skill** (if available):
- Use its competing hypotheses framework for Phase 3 evidence gathering
- Use its SIFT source validation for Phase 5 verification
- Use its pre-mortem methodology for Phase 5 failure analysis
- Use its provenance tracking for source citations

**When to stack**: If the user says "deep research", "thorough analysis", or "use research-analyst", load the research-analyst skill's methodology alongside this skill's domain-specific pipeline.

---

# EPISTEMIC METHODOLOGY (Research-Analyst Rigor)

**Debiasing Procedures** (embedded from research-analyst methodology):
1. **Confirmation bias prevention**: For each hypothesis, explicitly search for disconfirming evidence
2. **Scope creep awareness**: Set evidence gathering cutoff (e.g., "first 100 tests", "last 10 commits")
3. **Inference flagging**: Never use inference alone; tag competing hypotheses in output
4. **Temporal awareness**: Note when code was last modified (stale code ≠ current design)

**Competing Hypotheses Protocol** (MANDATORY for architecture decisions):
For each major design choice discovered:
1. State what the code does (the pattern)
2. State why it was likely done this way (hypothesis A — from git/comments)
3. State an alternative explanation (hypothesis B — competing)
4. Evaluate both against evidence
5. Document which hypothesis is supported and why

**Example:**
```
Pattern: Payment retries use exponential backoff with max 3 attempts
Hypothesis A: Standard reliability pattern for payment gateway timeouts (supported by: retry logic in payment_service.py:89, test_retry_exponential.py:45)
Hypothesis B: Workaround for specific Razorpay timeout bug (supported by: git commit abc123 "fix razorpay timeout issue")
Evaluation: Both partially correct. Code implements standard pattern, but git shows it was triggered by a specific Razorpay issue. Document BOTH.
Confidence: HIGH [Code + Test + Git = weight 2.6]
```

---

# QUALITY CRITERIA CHECKLIST

Before marking readiness_score ≥ 75:

- [ ] Coverage: ≥80% of codebase explained (modules, entry points, data flow)
- [ ] Confidence: ≥60% of claims tagged VERIFIED or HIGH; <10% UNKNOWN
- [ ] Cross-Validation: Every critical claim has ≥ 2 sources with combined weight ≥ 1.5
- [ ] Competing Hypotheses: For each architecture decision, stated and addressed
- [ ] Provenance: Every claim tagged [source: file:line] or [source: test:name]
- [ ] Temporal Validity: YAML frontmatter includes knowledge_as_of and review_triggers
- [ ] Pre-Mortem: Top 3 failure modes documented with mitigations
- [ ] Domain Compliance: If domain activated, compliance section is LARGEST section with POPULATED tables
- [ ] Minimum Depth: Total output meets word count requirements (3,000 / 5,000 / 6,500)
- [ ] Reader Tests: Can new dev answer: "What's the main entry point?", "How does auth work?", "What's the critical path?"

---

# QUICK-START DECISION TREE

```
START: "Document this codebase"
  |
  ├─ Is this a single-module script? YES → Run Phase 1-4 only (~20 min), output Quick Ref
  │
  ├─ Is this a multi-service system? YES → Run full Phase 1-6 (~2 hours), progressive disclosure
  │
  ├─ Is this fintech/healthcare/enterprise? YES → Phase 2 LOADS domain-mode file (MANDATORY),
  │                                                Phase 4 re-LOADS it and POPULATES compliance tables,
  │                                                Phase 6 adds compliance addendum + PII inventory
  │
  ├─ Do I have ≥3 hours for deep analysis? YES → Phase 3 includes git history deep-dive,
  │                                              Phase 5 full pre-mortem, target readiness ≥80
  │
  └─ Quick turnaround (<1 hour)? YES → Phase 1 only, output "Analysis Snapshot" (coverage, deps, gaps)
```

---

# EXECUTION (Single Agent, Linear, No External Scripts)

```
1. Ask user: Codebase path, domain context (if known), time available, output depth
2. RUN PHASE 1: Scan + extract (15 min) — LOAD code-patterns.md, language-patterns.md
3. RUN PHASE 2: Domain detection, present plan, WAIT FOR USER APPROVAL — LOAD detection.md + domain files
4. RUN PHASE 3: Evidence gathering (evidence map) — LOAD evidence-patterns.md, cross-validation.md
5. RUN PHASE 4: Doc generation (confidence-tagged, domain-mode tables populated) — LOAD cognitive-patterns.md, templates, domain files (AGAIN)
6. RUN PHASE 5: Cross-validate, pre-mortem (identify gaps) — LOAD accuracy-verification.md, completeness-checklists.md
7. RUN PHASE 6: Assemble outputs, calculate readiness_score, deliver — LOAD output-formats.md, quick-reference.md
8. RUN SAFEGUARD CHECKLIST: Every checkbox must be checked before delivery
```

No loops. No external scripts. All work in single Claude context. Reader picks depth.
