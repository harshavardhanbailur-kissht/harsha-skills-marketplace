# Completeness Checklists for Codebase Handoff Documenter V6

This reference file governs the MINIMUM COMPLETENESS REQUIREMENTS for every phase of the handoff documentation pipeline. It is aligned with SKILL.md's 6-phase linear model, epistemic confidence system, and domain-aware compliance architecture.

---

## PHASE 1: CODEBASE ANALYSIS - Output Inventory Checklist

**Goal**: Extract structural patterns without bias. Output is a raw analysis inventory (no conclusions).

**MANDATORY LOADS**:
- [ ] `references/code-patterns.md` read before starting
- [ ] `references/language-patterns.md` read before starting

**Raw Analysis Inventory MUST Include**:

### Directory & Module Structure
- [ ] Complete directory tree (depth ≥ 3 levels)
- [ ] Count of source files by type (.py, .ts, .js, .go, .java, etc.)
- [ ] Count of test files by type
- [ ] Count of config files (YAML, JSON, ENV, TOML)
- [ ] Count of documentation files (README, docs/, wikis)
- [ ] Count of infrastructure files (Dockerfile, docker-compose.yml, k8s/*.yaml, Terraform)
- [ ] Identification of monorepo structure (if applicable)
- [ ] Module/package organization (flat, layered, domain-driven, feature-based)

### Entry Points & Initialization
- [ ] Main application entry point (main.py, index.ts, app.js, etc.) with file path
- [ ] All documented entry points (CLI commands, API servers, background jobs, scheduled tasks)
- [ ] Initialization order (startup sequence, dependency injection, bootstrap process)
- [ ] Global configuration loading mechanism identified
- [ ] Environment variable reading points listed

### Data Flow (Input → Processing → Output)
- [ ] Primary data inputs documented (user input, API requests, files, databases, queues)
- [ ] Processing pipelines identified (request handling, business logic, async jobs)
- [ ] Data outputs documented (API responses, database writes, file exports, webhooks)
- [ ] Error flow paths documented (exception handling, fallback mechanisms)

### External Dependencies Inventory
- [ ] Runtime dependencies (pip, npm, gem, go.mod, etc.) with version constraints
- [ ] System dependencies (database, message queue, cache, external APIs)
- [ ] Cloud/infrastructure dependencies (S3, Lambda, Kubernetes, Azure, GCP)
- [ ] API integrations (count and names: Razorpay, Stripe, AWS, Google, etc.)
- [ ] Message queue systems (RabbitMQ, Kafka, SQS, Redis, etc.)
- [ ] Data storage systems (PostgreSQL, MongoDB, DynamoDB, Elasticsearch, etc.)

### File Type Inventory (No Interpretation)
- [ ] Source code files (organized by language/module)
- [ ] Test files (unit, integration, e2e, performance)
- [ ] Configuration files (app config, infrastructure, deployment)
- [ ] Documentation files (README, API docs, architecture docs)
- [ ] Infrastructure files (Docker, Kubernetes, Terraform, CloudFormation)
- [ ] CI/CD files (GitHub Actions, Jenkins, GitLab CI)
- [ ] Asset files (templates, static files, images)

### Domain Detection Signal Count (REQUIRED)
- [ ] Fintech signals raw count (list all matching patterns with file locations, do NOT score yet)
- [ ] Healthcare signals raw count (list all matching patterns with file locations)
- [ ] Enterprise signals raw count (list all matching patterns with file locations)
- [ ] For EACH signal found: exact file path and line number where pattern appears

**OUTPUT CHECKLIST - Phase 1 Complete When**:
- [x] All sections above have non-empty entries
- [x] Inventory is descriptive but contains NO interpretations ("this is payment processing")
- [x] Every external dependency has been tagged
- [x] Every signal has been recorded with precise file locations
- [x] Total word count: ≥ 1,000 words (structural documentation only)

---

## PHASE 2: DOMAIN DETECTION & PLANNING - Output Inventory Checklist

**Goal**: Score domain, load domain-mode files, present plan to user, WAIT FOR APPROVAL.

**MANDATORY LOADS**:
- [ ] `domain-modes/detection.md` read before scoring
- [ ] For EACH activated domain: corresponding domain-mode file read

**Domain Detection Results MUST Include**:

### Scoring Results (Explicit Point Attribution)
- [ ] **Fintech Score**: [X] points total
  - [ ] Tier 1 signals: [count] × 10 = [subtotal] (list each signal with file:line)
  - [ ] Tier 2 signals: [count] × 5 = [subtotal] (list each signal)
  - [ ] Tier 3 signals: [count] × 2 = [subtotal] (list each signal)
  - [ ] Tier 4 signals: [count] × 1 = [subtotal] (list each signal)
  - [ ] **Total**: [X] points
  - [ ] **Activation Status**: ✓ ACTIVATED (≥15) or ✗ Below threshold

- [ ] **Healthcare Score**: [X] points total
  - [ ] Tier 1 signals: [count] × 10 = [subtotal]
  - [ ] Tier 2 signals: [count] × 5 = [subtotal]
  - [ ] Tier 3 signals: [count] × 2 = [subtotal]
  - [ ] Tier 4 signals: [count] × 1 = [subtotal]
  - [ ] **Total**: [X] points
  - [ ] **Activation Status**: ✓ ACTIVATED or ✗ Below threshold

- [ ] **Enterprise Score**: [X] points total
  - [ ] Tier 1 signals: [count] × 10 = [subtotal]
  - [ ] Tier 2 signals: [count] × 5 = [subtotal]
  - [ ] Tier 3 signals: [count] × 2 = [subtotal]
  - [ ] Tier 4 signals: [count] × 1 = [subtotal]
  - [ ] **Total**: [X] points
  - [ ] **Activation Status**: ✓ ACTIVATED or ✗ Below threshold

### Domain File Loading Verification
- [ ] If Fintech ≥ 15: `domain-modes/fintech.md` loaded, line count confirmed
- [ ] If Healthcare ≥ 15: `domain-modes/healthcare.md` loaded, line count confirmed
- [ ] If Enterprise ≥ 15: `domain-modes/enterprise.md` loaded, line count confirmed
- [ ] List of activated domains presented to user

### Documentation Plan Presented to User
- [ ] Architecture overview with appropriate diagrams
- [ ] For Fintech: PCI-DSS 12-requirement mapping plan, RBI DLG audit plan, payment flow diagrams
- [ ] For Healthcare: HIPAA 3-safeguard mapping plan, PHI 18-identifier inventory plan
- [ ] For Enterprise: SOC2 5-domain mapping plan, RBAC matrix plan, multi-tenant audit plan
- [ ] Technical debt audit plan
- [ ] Pre-mortem failure analysis plan
- [ ] Explicit list of which compliance sections will be generated

### Human Approval Checkpoint
- [ ] Plan presented in human-readable format (copied from SKILL.md format)
- [ ] User given explicit approval decision point: "Proceed? [Y/N]"
- [ ] **WAIT FOR USER APPROVAL BEFORE PROCEEDING TO PHASE 3**

**OUTPUT CHECKLIST - Phase 2 Complete When**:
- [x] Domain scores presented with full point attribution (no hidden math)
- [x] Every activated domain has its mode file listed as loaded
- [x] Documentation plan aligns with activated domains
- [x] User approval explicitly requested and documented
- [x] Total word count: ≥ 500 words (scoring explanation + plan)

---

## PHASE 3: EVIDENCE GATHERING - Output Inventory Checklist

**Goal**: Build evidence inventory with cross-validated provenance. Every claim tagged with confidence.

**MANDATORY LOADS**:
- [ ] `references/evidence-patterns.md` read before gathering
- [ ] `references/cross-validation.md` read before gathering
- [ ] `references/accuracy-verification.md` read before finalizing

**Evidence Map MUST Include**:

### Code Evidence Inventory
- [ ] Architecture patterns identified with file:line citations
- [ ] Data handling mechanisms identified (encryption, storage, access)
- [ ] External API integrations documented (each call site with context)
- [ ] Authentication/authorization implementation (mechanism, scope)
- [ ] Error handling patterns (exception types, recovery)
- [ ] Performance-critical sections identified
- [ ] Security-sensitive code paths identified
- [ ] For EACH finding: exact file path, line number, code snippet (5-10 lines)

### Test Evidence Inventory
- [ ] Unit test assertions analyzed for behavioral contracts
- [ ] Integration test flows analyzed
- [ ] Mock/stub configurations analyzed for expected contracts
- [ ] Test coverage for critical paths assessed
- [ ] For EACH test claim: test file name, test function name, assertion type
- [ ] Passing vs. skipped/disabled tests differentiated

### Git History Evidence
- [ ] Recent commits (last 50) categorized by type (feat, fix, refactor, docs)
- [ ] Major architectural decisions identified from commit messages
- [ ] Deprecation timelines extracted
- [ ] Bug fixes and workarounds documented
- [ ] Design rationale extracted from PR descriptions (top 10 PRs)
- [ ] For EACH claim: commit hash, author, date, message text

### Comment & Documentation Evidence
- [ ] Inline comments extracted (especially TODO, FIXME, HACK, BUG)
- [ ] Docstrings extracted
- [ ] Architecture decision records (ADRs) if present
- [ ] README sections relevant to architecture
- [ ] For EACH: file:line, context (function/class), text

### Inference Tracking (LOW credibility - use sparingly)
- [ ] Patterns deduced from naming conventions
- [ ] Patterns deduced from file structure
- [ ] Patterns deduced from dependency graphs
- [ ] **FLAGGED AS INFERENCE** - never used as sole source

### Cross-Validation Matrix (MANDATORY for Every Major Claim)

For each architectural claim, populate:

```
Claim: "[Specific, testable claim about the codebase]"

Evidence:
  Source 1: [Type]
    - Location: [file:line or test:name]
    - Content: [What it shows]
    - Credibility Weight: [0.3 - 1.0]

  Source 2: [Type]
    - Location: [file:line or test:name]
    - Content: [What it shows]
    - Credibility Weight: [0.3 - 1.0]

  [Additional sources if present]

Combined Weight: [Sum of all weights]
Confidence Level: [VERIFIED/HIGH/MEDIUM/LOW/UNKNOWN]
Cross-Validated: [YES/NO]

Competing Hypothesis:
  - Alternative explanation: [What else could explain this pattern?]
  - Why accepted/rejected: [How does evidence support/reject it?]
```

**Minimum Evidence Requirements (MANDATORY)**:
- [ ] Architecture claims: ≥ 3 sources (Code + Test + Git minimum)
- [ ] Security claims: ≥ 2 sources + explicit competing hypothesis
- [ ] Compliance claims: ≥ 2 sources + reference to specific regulation
- [ ] Integration claims: ≥ 2 sources (Code + Test or Code + Config)

### Confidence Level Distribution
- [ ] Count of VERIFIED claims: [X] (target: ≥40% of major claims)
- [ ] Count of HIGH claims: [X] (target: ≥40%)
- [ ] Count of MEDIUM claims: [X] (target: ≤15%)
- [ ] Count of LOW claims: [X] (target: <5%)
- [ ] Count of UNKNOWN claims: [X] (target: <5%)

**OUTPUT CHECKLIST - Phase 3 Complete When**:
- [x] Evidence map covers all major architecture decisions
- [x] Every VERIFIED/HIGH claim has ≥ 2 sources with combined weight ≥ 1.5
- [x] Every claim has competing hypothesis explicitly stated
- [x] All evidence tagged with source type and location
- [x] Total word count: ≥ 2,000 words (evidence documentation)
- [x] Confidence distribution is healthy (LOW/UNKNOWN < 10% combined)

---

## PHASE 4: DOCUMENTATION GENERATION - Output Completeness Checklist

**Goal**: Write multi-format docs with confidence tags, provenance, and domain-specific controls.

**MANDATORY LOADS (READ IN THIS ORDER)**:
- [ ] `references/cognitive-patterns.md`
- [ ] `references/output-formats.md`
- [ ] `templates/architecture.md`
- [ ] `templates/handoff-package.md`
- [ ] **IF Fintech Activated**: `domain-modes/fintech.md` + `templates/compliance-mapping-template.md` + `templates/pii-inventory-template.md`
- [ ] **IF Healthcare Activated**: `domain-modes/healthcare.md` + `templates/compliance-mapping-template.md`
- [ ] **IF Enterprise Activated**: `domain-modes/enterprise.md` + `templates/compliance-mapping-template.md`

### SECTION 1: Executive Summary

**Minimum Depth: 300 words**

**MUST Include**:
- [ ] System purpose (1-2 sentences: what does this code do?)
- [ ] Tech stack (languages, frameworks, databases, key libraries)
- [ ] Architecture style (monolithic, microservices, serverless, event-driven, other)
- [ ] Key dependencies listed (top 5 external systems)
- [ ] Integration points (APIs consumed, APIs exposed)
- [ ] Domain classification (Fintech/Healthcare/Enterprise/Agnostic)
- [ ] Compliance requirements if domain-specific
- [ ] Intended audience (internal team, external partners, investors)
- [ ] Knowledge cutoff date and validity period

**Word Count**: [X] / 300 minimum
**Confidence Tags Present**: [YES/NO]
**Source Citations Present**: [YES/NO]

### SECTION 2: Architecture Overview

**Minimum Depth: 500 words + diagram(s)**

**MUST Include**:
- [ ] Module/service boundaries (how is code organized?)
- [ ] Service-to-service communication (REST, gRPC, message queue, direct calls)
- [ ] Request lifecycle (entry point → processing → response)
- [ ] Database schema overview (major tables, relationships)
- [ ] Data model relationships (1:1, 1:N, M:N, inheritance)
- [ ] External integrations (APIs called, webhooks received)
- [ ] Caching layer (Redis, Memcached, application cache)
- [ ] Message queue/async job systems
- [ ] At least 1 architecture diagram (ASCII art, Mermaid, or image reference)
  - [ ] Diagram shows major components
  - [ ] Diagram shows data flow direction
  - [ ] Diagram shows external integrations
- [ ] Architectural patterns identified (MVC, MVVM, Clean Architecture, DDD, CQRS, etc.)
- [ ] Layer separation (presentation, business logic, data access)

**Word Count**: [X] / 500 minimum (excluding diagram)
**Diagram Present**: [YES/NO]
**Confidence Tags Present**: [YES/NO]

### SECTION 3: Authentication & Security

**Minimum Depth: 400 words**

**MUST Include**:
- [ ] Auth mechanism (OAuth2, JWT, session, API key, mTLS, other)
  - [ ] How credentials are issued
  - [ ] How credentials are validated
  - [ ] Credential storage mechanism (token store, session store)
  - [ ] Token/session expiration strategy
- [ ] Authorization model (RBAC, ABAC, custom)
  - [ ] Role definitions (if RBAC)
  - [ ] Permission/attribute mapping (if ABAC)
  - [ ] Scope/boundary enforcement
- [ ] Secret management (env vars, Vault, hardcoded, other)
  - [ ] Which secrets are managed how
  - [ ] Rotation strategy
  - [ ] Access controls on secrets
- [ ] Encryption (at rest, in transit, field-level)
  - [ ] At rest: algorithm, key management
  - [ ] In transit: TLS/SSL version, cipher suites
  - [ ] Field-level: which fields encrypted, algorithm
- [ ] Input validation (XSS, SQL injection, CSRF prevention)
- [ ] Security headers (if web app)
- [ ] Rate limiting/DDoS protection
- [ ] Known security gaps or TODOs

**Word Count**: [X] / 400 minimum
**Confidence Tags Present**: [YES/NO]
**Competing Hypotheses Present**: [YES/NO]

### SECTION 4: Data Flow & Processing

**Minimum Depth: 400 words per major flow**

For each of the 2-3 main data flows, document:

**MUST Include (per flow)**:
- [ ] Request entry point (API endpoint, message topic, cron trigger)
- [ ] Request format (JSON schema, XML, form data, other)
- [ ] Step-by-step processing (5-10 sequential steps)
- [ ] Data transformations (format changes, enrichment, filtering)
- [ ] External API calls (which APIs, when, with what data)
- [ ] Database operations (reads, writes, transactions)
- [ ] Response generation (format, status codes)
- [ ] Error handling (which errors caught, recovery mechanism)
- [ ] Async/background jobs triggered (if any)
- [ ] Caching strategy (cache key, TTL, invalidation)
- [ ] Performance characteristics (typical latency, throughput)
- [ ] Sequence diagram (for complex flows)

**Total Data Flow Documentation**: [X] / (400 × number_of_flows) minimum
**Diagrams Present for Complex Flows**: [YES/NO]
**Confidence Tags Present**: [YES/NO]

### SECTION 5: Domain-Specific Compliance (MANDATORY if domain activated)

**THIS IS THE LARGEST SECTION WHEN DOMAIN IS ACTIVATED**

---

#### SUBSECTION 5A: Fintech Compliance (if Fintech score ≥ 15)

**Minimum Depth: Total ≥ 1,600 words across all fintech subsections**

##### PCI-DSS Compliance Mapping
**Minimum Depth: 600 words**

**MUST Include 12-Row Table**:
| PCI-DSS Requirement | Code Evidence | Compliance Status | Notes |
|-----|--------|---------|-------|
| 1. Firewall Configuration | [file:line or N/A] | ✓ COMPLIANT / ⚠ PARTIAL / ✗ NON-COMPLIANT | [Description] |
| 2. Default Passwords Removed | [file:line or N/A] | [Status] | |
| 3. Stored Data Protection | [file:line or N/A] | [Status] | |
| 4. Data Transmission Encryption | [file:line or N/A] | [Status] | |
| 5. Malware Protection | [file:line or N/A] | [Status] | |
| 6. Secure Development | [file:line or N/A] | [Status] | |
| 7. Restricted Access | [file:line or N/A] | [Status] | |
| 8. User Identification | [file:line or N/A] | [Status] | |
| 9. Physical Access Restriction | [file:line or N/A] | [Status] | |
| 10. Access Logging & Monitoring | [file:line or N/A] | [Status] | |
| 11. Regular Testing | [file:line or N/A] | [Status] | |
| 12. Information Security Policy | [file:line or N/A] | [Status] | |

**MUST Include Narrative** (≥ 600 words):
- [ ] For each COMPLIANT requirement: specific implementation details
- [ ] For each PARTIAL: what's implemented vs. what's missing
- [ ] For each NON-COMPLIANT: remediation roadmap
- [ ] Card data handling: tokenization strategy, storage method
- [ ] PAN (Primary Account Number) masking rules
- [ ] Card validation (Luhn algorithm, expiry checks)
- [ ] Compliance status summary

##### RBI Digital Lending Guidelines Audit
**Minimum Depth: 400 words**

**MUST Include**:
- [ ] Governance structure mapped to RBI DLG
- [ ] Data protection & consent management per DLG
- [ ] Credit assessment process documented
- [ ] Pricing & transparency controls
- [ ] Grievance redressal mechanism
- [ ] Record maintenance & audit trail
- [ ] For each DLG requirement: mapped to code or policy doc
- [ ] Compliance gaps identified
- [ ] Remediation roadmap

##### PII & Sensitive Data Inventory
**Minimum Depth: 300 words**

**MUST Include Detailed Inventory Table**:
| PII Type | Found? | Storage Location | Encryption | Access Control | Retention | Deletion Policy |
|----------|--------|-----------------|------------|-----------------|-----------|-----------------|
| Aadhaar | Y/N | [storage] | [algorithm] | [who accesses] | [how long] | [how deleted] |
| PAN | Y/N | [storage] | [algorithm] | [who] | [how long] | [how deleted] |
| Phone Number | Y/N | [storage] | [algorithm] | [who] | [how long] | [how deleted] |
| Email Address | Y/N | [storage] | [algorithm] | [who] | [how long] | [how deleted] |
| Bank Account | Y/N | [storage] | [algorithm] | [who] | [how long] | [how deleted] |
| Credit Score | Y/N | [storage] | [algorithm] | [who] | [how long] | [how deleted] |
| [Other found] | Y/N | [storage] | [algorithm] | [who] | [how long] | [how deleted] |

**MUST Include Narrative** (≥ 300 words):
- [ ] For each PII type found: storage method, encryption, access controls
- [ ] Data minimization assessment (is all PII necessary?)
- [ ] Deletion/archival strategy
- [ ] Compliance with RBI data residency requirements
- [ ] Cross-border data transfer controls

##### Payment Flow Documentation
**Minimum Depth: 400 words**

**MUST Include Sequence Diagram**:
- [ ] Sequence diagram showing: Customer → App → Payment Gateway → Bank → Callback → Settlement
- [ ] Key steps labeled with timeouts, error cases
- [ ] Webhook signature verification shown

**MUST Include Narrative** (≥ 400 words):
- [ ] Payment gateway integration (Razorpay, Stripe, Cashfree, etc.)
- [ ] Order creation → Payment initiation flow
- [ ] Webhook handling and signature verification
- [ ] Settlement & reconciliation process
- [ ] Refund flow
- [ ] Idempotency handling (duplicate request protection)
- [ ] Error scenarios (timeout, decline, invalid order, etc.)
- [ ] Retry strategy

##### Indian Payment Ecosystem Integration
**Minimum Depth: 200 words**

**MUST Include**:
- [ ] UPI/NEFT/RTGS/IMPS implementation (if present)
- [ ] Currency handling (INR precision, paise/rupee conversion)
- [ ] GST/Tax calculation (if present)
- [ ] Regulatory reporting integration (if required)

**Fintech Compliance Checklist**:
- [x] All 12 PCI-DSS requirements mapped to code or status
- [x] All PCI-DSS gaps have remediation plan
- [x] All PII types found and documented with controls
- [x] Payment flow has sequence diagram
- [x] RBI DLG mapped to code
- [x] Idempotency keys present on financial operations
- [x] Webhook signature verification implemented
- [x] Settlement/reconciliation logic documented

**Total Fintech Compliance Word Count**: [X] / 1,600 minimum

---

#### SUBSECTION 5B: Healthcare Compliance (if Healthcare score ≥ 15)

**Minimum Depth: Total ≥ 1,200 words across all healthcare subsections**

##### HIPAA Safeguards Mapping
**Minimum Depth: 600 words**

**MUST Include 3-Part Table**:

**Administrative Safeguards**:
| Control | Implementation | Evidence | Status |
|---------|----------------|----------|--------|
| Security Management Process | [implementation] | [file:line] | ✓/⚠/✗ |
| Designated Security Officer | [implementation] | [doc/config] | ✓/⚠/✗ |
| Workforce Security | [implementation] | [code location] | ✓/⚠/✗ |
| Information Access Management | [implementation] | [code location] | ✓/⚠/✗ |
| Security Training | [training method] | [policy doc] | ✓/⚠/✗ |

**Physical Safeguards**:
| Control | Implementation | Evidence | Status |
|---------|----------------|----------|--------|
| Facility Access Controls | [implementation] | [doc] | ✓/⚠/✗ |
| Workstation Use Policy | [implementation] | [doc] | ✓/⚠/✗ |
| Workstation Security | [implementation] | [code] | ✓/⚠/✗ |
| Device/Media Controls | [implementation] | [doc/code] | ✓/⚠/✗ |

**Technical Safeguards**:
| Control | Implementation | Evidence | Status |
|---------|----------------|----------|--------|
| Access Controls | [RBAC/ABAC] | [file:line] | ✓/⚠/✗ |
| Encryption | [algorithm/keystore] | [file:line] | ✓/⚠/✗ |
| Audit Controls | [logging mechanism] | [file:line] | ✓/⚠/✗ |
| Data Integrity | [hash/checksums] | [file:line] | ✓/⚠/✗ |
| Transmission Security | [TLS version/ciphers] | [config] | ✓/⚠/✗ |

**MUST Include Narrative** (≥ 600 words):
- [ ] For each safeguard: specific implementation in code
- [ ] Access control matrix for PHI (who can access what, when)
- [ ] Audit log completeness (what's logged, retention)
- [ ] Encryption inventory (at rest, in transit, field-level)
- [ ] Gaps identified with remediation roadmap

##### PHI Classification & Inventory
**Minimum Depth: 300 words**

**MUST Include 18-Identifier Inventory Table**:
| HIPAA Identifier | Found in Code? | Storage Location | Encryption | Redaction Rule | Notes |
|-----------------|----------------|-----------------|------------|----------------|-------|
| Names | Y/N | [location] | [Y/N] | [Safe Harbor rule] | |
| All geographic subdivisions | Y/N | [location] | [Y/N] | [Rule] | |
| Dates (birth, admission, discharge) | Y/N | [location] | [Y/N] | [Rule] | |
| Telephone numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Fax numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Email addresses | Y/N | [location] | [Y/N] | [Rule] | |
| Social Security numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Medical record numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Health insurance IDs | Y/N | [location] | [Y/N] | [Rule] | |
| Account numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Certificate/license numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Vehicle serial numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Device serial numbers | Y/N | [location] | [Y/N] | [Rule] | |
| Web URLs | Y/N | [location] | [Y/N] | [Rule] | |
| IP addresses | Y/N | [location] | [Y/N] | [Rule] | |
| Biometric data | Y/N | [location] | [Y/N] | [Rule] | |
| Full face photos | Y/N | [location] | [Y/N] | [Rule] | |
| Any unique identifier | Y/N | [location] | [Y/N] | [Rule] | |

**MUST Include Narrative** (≥ 300 words):
- [ ] For each PHI type found: storage, encryption, access control
- [ ] De-identification process (Safe Harbor vs. Expert Determination)
- [ ] Minimum Necessary principle enforcement
- [ ] Data retention/deletion policy

##### HL7/FHIR Integration Documentation
**Minimum Depth: 300 words**

**MUST Include**:
- [ ] If HL7/FHIR present: version, message types, implementation details
- [ ] Data mapping between internal format and HL7/FHIR
- [ ] Segment-level documentation (if HL7)
- [ ] Resource profiles (if FHIR)
- [ ] Example messages (anonymized)
- [ ] EHR/EMR integration points

##### Patient Consent Workflow
**Minimum Depth: 200 words**

**MUST Include**:
- [ ] Consent types (authorization, notice, other)
- [ ] Consent capture mechanism (form, API, database)
- [ ] Consent revocation process
- [ ] Consent enforcement in code
- [ ] Example consent flow diagram

**Healthcare Compliance Checklist**:
- [x] All HIPAA safeguards mapped (administrative, physical, technical)
- [x] All 18 PHI identifiers inventoried
- [x] De-identification process documented
- [x] Consent management present
- [x] HL7/FHIR mappings if integrated
- [x] Audit trails complete and logged

**Total Healthcare Compliance Word Count**: [X] / 1,200 minimum

---

#### SUBSECTION 5C: Enterprise Compliance (if Enterprise score ≥ 15)

**Minimum Depth: Total ≥ 1,200 words across all enterprise subsections**

##### SOC2 Trust Criteria Mapping
**Minimum Depth: 600 words**

**MUST Include 5-Domain Table**:
| Trust Criterion | Specific Requirement | Implementation | Evidence | Status |
|-----------------|---------------------|---|----------|--------|
| **CC: Common Criteria** | | | | |
| CC1 | Risk assessment process | [implementation] | [file:line] | ✓/⚠/✗ |
| CC2 | Board oversight | [implementation] | [policy] | ✓/⚠/✗ |
| CC3 | Responsibility assignment | [implementation] | [code/doc] | ✓/⚠/✗ |
| CC4 | Competence | [training] | [policy] | ✓/⚠/✗ |
| CC5 | Change management | [process] | [code/config] | ✓/⚠/✗ |
| CC6 | Logical/physical access | [implementation] | [code/infra] | ✓/⚠/✗ |
| CC7 | System monitoring | [logging] | [file:line] | ✓/⚠/✗ |
| CC8 | Incident procedures | [process] | [runbook] | ✓/⚠/✗ |
| CC9 | Data protection | [encryption/classification] | [file:line] | ✓/⚠/✗ |
| **A1: Availability** | | | | |
| A1.1 | Infrastructure redundancy | [implementation] | [infra config] | ✓/⚠/✗ |
| A1.2 | System performance monitoring | [metrics/alerts] | [monitoring code] | ✓/⚠/✗ |
| **PI1: Confidentiality** | | | | |
| PI1.1 | Data classification | [classification scheme] | [code/config] | ✓/⚠/✗ |
| PI1.2 | Encryption strategy | [algorithm/keys] | [file:line] | ✓/⚠/✗ |
| **C1: Commitment to Competence** | | | | |
| C1.1 | Incident response | [plan] | [runbook] | ✓/⚠/✗ |
| C1.2 | Crisis management | [plan] | [runbook] | ✓/⚠/✗ |
| **P1-P8: Other Criteria** | [mapped individually] | [implementation] | [evidence] | ✓/⚠/✗ |

**MUST Include Narrative** (≥ 600 words):
- [ ] For each trust criterion: specific implementation
- [ ] Control gaps identified
- [ ] Audit evidence collected
- [ ] Remediation roadmap for gaps

##### RBAC/IAM Matrix
**Minimum Depth: 300 words**

**MUST Include Role & Permission Matrix**:
| Role | Users | Can Create | Can Read | Can Update | Can Delete | Special Permissions |
|------|-------|-----------|----------|-----------|-----------|-------------------|
| Admin | [count] | All | All | All | All | System config, user mgmt |
| [Role] | [count] | [resources] | [resources] | [resources] | [resources] | [special] |
| [Role] | [count] | [resources] | [resources] | [resources] | [resources] | [special] |

**MUST Include Narrative** (≥ 300 words):
- [ ] Role definitions (admin, user, viewer, etc.)
- [ ] Permission enforcement mechanism (code location)
- [ ] API-level authorization checks
- [ ] Database-level access controls
- [ ] Scope isolation per tenant (if multi-tenant)

##### Multi-Tenant Isolation Documentation
**Minimum Depth: 300 words**

**MUST Include**:
- [ ] Tenant isolation architecture (row-level, schema-level, database-level)
- [ ] Data isolation guarantees (how queries are scoped)
- [ ] Tenant context propagation (how tenant ID flows through system)
- [ ] Cross-tenant access prevention (tests/validation)
- [ ] Resource quotas per tenant
- [ ] Blast radius limitation (failure in one tenant doesn't affect others)

##### Audit Trail Completeness
**Minimum Depth: 200 words**

**MUST Include**:
- [ ] Audit events captured (user actions, permission changes, data access)
- [ ] Audit log storage (database, immutable log)
- [ ] Audit log retention (how long kept)
- [ ] Audit log access controls (who can read/modify)
- [ ] Tamper detection (how integrity verified)
- [ ] Query audit logs example (who accessed what data, when)

**Enterprise Compliance Checklist**:
- [x] All SOC2 trust criteria mapped to code
- [x] RBAC matrix populated with actual roles/permissions
- [x] Multi-tenant isolation tested and documented
- [x] Audit trail comprehensive and tamper-evident
- [x] Access control enforcement verified at API and DB layers

**Total Enterprise Compliance Word Count**: [X] / 1,200 minimum

---

### SECTION 6: Technical Debt & Known Issues

**Minimum Depth: 300 words**

**MUST Include**:
- [ ] TODO/FIXME/HACK inventory with file:line citations
  - [ ] Severity rating per item (critical/high/medium/low)
  - [ ] Count by severity
  - [ ] Estimated effort to fix
- [ ] Dependency staleness report
  - [ ] Outdated packages with version gap
  - [ ] Known security vulnerabilities
  - [ ] End-of-life dependencies
- [ ] Architecture smell detection
  - [ ] Tightly coupled modules
  - [ ] God objects (classes doing too much)
  - [ ] Circular dependencies
  - [ ] Missing abstractions
- [ ] Performance debt (inefficient queries, missing indexes, etc.)
- [ ] Test coverage gaps (critical paths without tests)
- [ ] Documentation gaps

**Word Count**: [X] / 300 minimum
**Confidence Tags Present**: [YES/NO]

### SECTION 7: Configuration & Deployment

**Minimum Depth: 300 words**

**MUST Include**:
- [ ] All environment variables documented
  - [ ] Name, type, default, required/optional
  - [ ] Purpose and impact
  - [ ] Example values
  - [ ] Marked as SECRET if sensitive
- [ ] Secret management approach (env vars, Vault, K8s secrets, other)
- [ ] Deployment assumptions
  - [ ] Container/VM requirements
  - [ ] Kubernetes manifests (if used)
  - [ ] Terraform/IaC files (if used)
  - [ ] Database setup steps
- [ ] Build process (build command, artifacts)
- [ ] Startup sequence (initialization order)
- [ ] Health checks (liveness, readiness probes)
- [ ] Logging configuration
- [ ] Monitoring/metrics setup

**Word Count**: [X] / 300 minimum
**Confidence Tags Present**: [YES/NO]

### SECTION 8: Pre-Mortem Analysis

**Minimum Depth: 200 words**

**MUST Include Exactly 3 Failure Modes**:

```
Failure Mode #1: [Most likely failure]
  Probability: [HIGH/MEDIUM/LOW]
  Impact: [Critical/Major/Minor]
  Root Cause: [Why this is likely to fail]
  Mitigation: [Specific action to prevent or recover]
  Owner: [Who monitors this]

Failure Mode #2: [Second most likely failure]
  Probability: [HIGH/MEDIUM/LOW]
  Impact: [Critical/Major/Minor]
  Root Cause: [Why this is likely to fail]
  Mitigation: [Specific action]
  Owner: [Who monitors]

Failure Mode #3: [Third most likely failure]
  Probability: [HIGH/MEDIUM/LOW]
  Impact: [Critical/Major/Minor]
  Root Cause: [Why this is likely to fail]
  Mitigation: [Specific action]
  Owner: [Who monitors]
```

**Common Failure Modes** (select from or customize):
- Missing domain context (fintech/healthcare complexity not understood)
- Silent assumptions (undocumented dependencies, implicit behavior)
- Dependency rot (external APIs deprecated, versions pinned)
- Lost rationale (design choices not explained)
- Configuration blind spots (environment variables not documented)
- Compliance drift (regulations updated, code not)
- Performance degradation (scaling assumptions wrong)
- Integration brittle (external API changes break code)

**Word Count**: [X] / 200 minimum
**3 Failure Modes Present**: [YES/NO]
**Mitigations Actionable**: [YES/NO]

### SECTION 9: Handoff Readiness Score

**Minimum Depth: 100 words**

**MUST Include**:
- [ ] Coverage Score calculation: (sections_documented / required) × 100
- [ ] Confidence Average calculation: (sum of confidence levels) / count
  - [ ] VERIFIED = 95 points
  - [ ] HIGH = 85 points
  - [ ] MEDIUM = 65 points
  - [ ] LOW = 35 points
  - [ ] UNKNOWN = 10 points
- [ ] Completeness Score: (VERIFIED + HIGH claims) / all claims × 100
- [ ] Final Score: (coverage × 0.4) + (confidence_avg × 0.4) + (completeness × 0.2)
- [ ] Interpretation: Score ≥ 75 = safe handoff, < 60 = requires rework
- [ ] Reader can answer: "What does this code do?", "Why was it built?", "What breaks easily?"

**Word Count**: [X] / 100 minimum
**Score Calculated**: [YES/NO]
**Score ≥ 75**: [YES/NO/BELOW THRESHOLD]

**YAML Frontmatter** (MANDATORY on every document):
```yaml
knowledge_as_of: "YYYY-MM-DD"
valid_until: "YYYY-MM-DD"  # 3 months from generation
review_triggers:
  - "Any modification to auth system"
  - "Addition of new external API"
  - "Schema migration"
  - "Regulatory update (RBI/HIPAA/SOC2)"
  - [domain-specific triggers]
last_reviewer: "[Name]"
next_review_date: "YYYY-MM-DD"
```

---

## PHASE 4 OUTPUT TOTALS

**Minimum Word Counts (ENFORCED)**:
- Without domain compliance: ≥ 3,000 words
- With one domain activated: ≥ 5,000 words
- With multiple domains: ≥ 6,500 words

**Phase 4 Complete When**:
- [x] All 9 sections present with content
- [x] Word counts meet minimums
- [x] Every claim has confidence tag + source
- [x] All compliance tables POPULATED (not templates)
- [x] Diagrams present for architecture & flows
- [x] Pre-mortem has exactly 3 failure modes
- [x] YAML frontmatter present
- [x] Total output meets length requirement

---

## PHASE 5: VERIFICATION & PRE-MORTEM - Verification Checklist

**Goal**: Cross-validate claims, stress-test assumptions, identify gaps.

**MANDATORY LOADS**:
- [ ] `references/accuracy-verification.md` read
- [ ] `references/completeness-checklists.md` read (this file)

**Cross-Validation Verification Checklist**:

- [ ] Every VERIFIED claim checked: ≥ 2 source types with combined weight ≥ 1.5
- [ ] Every HIGH claim checked: evidence weight reasonable
- [ ] Competing hypotheses explicitly stated for architecture decisions
- [ ] Architecture diagrams vs. actual code trace match (sample 5 traces)
- [ ] Test coverage validates claimed constraints (spot-check 5 tests)
- [ ] Git history confirms design rationale (sample 3 significant commits)
- [ ] Domain-mode compliance tables POPULATED (not empty)
- [ ] PII inventory lists EVERY field found (not "PII is handled")
- [ ] Payment/clinical/audit flows have sequence diagrams
- [ ] No contradictions between sections
- [ ] Citations point to actual files (spot-check 10 citations)

**Pre-Mortem Verification**:
- [ ] Exactly 3 failure modes documented
- [ ] Each has probability assessment (HIGH/MEDIUM/LOW)
- [ ] Each has specific mitigation (not vague)
- [ ] Each has owner assigned
- [ ] Failure modes are realistic (not imaginary)
- [ ] Mitigations are actionable (not "monitor closely")

**Completeness Verification**:
- [ ] Coverage: ≥ 80% of codebase explained (modules, entry points, data flow)
- [ ] Confidence: ≥ 60% of claims VERIFIED or HIGH
- [ ] Low/Unknown: < 10% combined
- [ ] Domain compliance (if activated): is the LARGEST section
- [ ] No critical sections skipped
- [ ] Total word count meets minimum

**Phase 5 Complete When**:
- [x] All cross-validation checks pass
- [x] No contradictions found
- [x] Pre-mortem is realistic and actionable
- [x] Completeness metrics acceptable
- [x] Document ready for delivery

---

## PHASE 6: OUTPUT ASSEMBLY & HANDOFF READINESS SCORE - Delivery Checklist

**Goal**: Multi-format delivery, scored for handoff completeness.

**MANDATORY LOADS**:
- [ ] `references/output-formats.md`
- [ ] `references/quick-reference.md`
- [ ] `templates/handoff-package.md`

**Output Formats** (select appropriate depth):
- [ ] Quick Reference (1-2 pages): Diagrams, entry points, critical deps, limitations
- [ ] Architecture Overview (5-10 pages): Domain context, design decisions, data flow, integrations
- [ ] Deep Dive (20+ pages): Code walkthrough, test analysis, config reference, compliance
- [ ] Compliance Addendum (if domain): Audit trails, encryption, consent, RBAC, SLA

**Final Output Checklist** (MANDATORY - check every item):

- [ ] YAML Frontmatter present: knowledge_as_of, valid_until, review_triggers
- [ ] Every section includes confidence tags (VERIFIED/HIGH/MEDIUM/LOW/UNKNOWN)
- [ ] Every claim has source citation [source: file:line] or [source: test:name]
- [ ] Competing hypotheses documented for architecture decisions
- [ ] Pre-mortem includes top 3 failure modes with mitigations
- [ ] Domain-specific compliance section present (if domain activated)
- [ ] Compliance tables POPULATED with actual findings (not "TBD")
- [ ] PII inventory present with field-level detail (if fintech/healthcare)
- [ ] Payment/clinical/audit flow diagrams present (if fintech/healthcare)
- [ ] Handoff readiness score calculated + interpretation provided
- [ ] All 9 sections from Phase 4 present
- [ ] Total output meets MINIMUM DEPTH requirement
- [ ] Reader can answer: "What does this code do?", "Why built this way?", "What breaks easily?"
- [ ] No broken links or references
- [ ] Examples are clear and runnable (where applicable)
- [ ] All jargon defined (first use in document)
- [ ] Document formatting consistent (headings, code blocks, tables)
- [ ] No placeholder text remaining

**Quality Gate Checks** (prevent delivery of incomplete work):

- [ ] Coverage Score: ≥ 80% of codebase sections documented
- [ ] Confidence Distribution: ≥ 60% VERIFIED + HIGH, < 10% LOW + UNKNOWN
- [ ] Cross-Validation: Every critical claim has ≥ 1.5 combined weight
- [ ] Pre-Mortem: 3 failure modes with realistic mitigations
- [ ] Compliance (if activated): All domain tables have actual findings
- [ ] Depth Verification: Each section meets word count minimum
- [ ] Readiness Score: Calculated using exact formula from Phase 6
- [ ] No critical gaps in understanding (sample by reading Phase 5 verification)

**Handoff Readiness Score Formula** (EXACT):
```
coverage_score = (sections_documented / sections_required) × 100
confidence_avg = (sum of all confidence levels mapped to 0-100) / count
  VERIFIED = 95
  HIGH = 85
  MEDIUM = 65
  LOW = 35
  UNKNOWN = 10
completeness = (verified_claims + high_claims) / (all_claims) × 100

readiness_score = (coverage_score × 0.4) + (confidence_avg × 0.4) + (completeness × 0.2)
```

**Score Interpretation**:
- 75-100: Safe handoff, recipient can maintain/extend
- 60-74: Proceed with caution, plan for ramp-up
- <60: Requires additional work before handoff

**SAFEGUARD CHECKLIST** (RUN THIS BEFORE DELIVERY - ALL ITEMS REQUIRED):

```
□ Phase 1: Loaded references/code-patterns.md AND references/language-patterns.md?
□ Phase 2: Loaded domain-modes/detection.md?
□ Phase 2: Presented explicit point-per-signal scoring to user?
□ Phase 2: For each activated domain, loaded corresponding domain-mode file?
□ Phase 3: Loaded references/evidence-patterns.md AND references/cross-validation.md?
□ Phase 3: Every VERIFIED/HIGH claim has ≥ 2 source types, combined weight ≥ 1.5?
□ Phase 3: Stated competing hypotheses for architecture decisions?
□ Phase 4: Re-loaded domain-mode files before writing compliance sections?
□ Phase 4: Loaded ALL required templates for activated domain?
□ Phase 4: Compliance section is LARGEST section (if domain activated)?
□ Phase 4: POPULATED compliance tables with actual findings (not empty templates)?
□ Phase 4: Each section meets its MINIMUM DEPTH requirement?
□ Phase 5: Loaded references/accuracy-verification.md AND references/completeness-checklists.md?
□ Phase 5: Wrote pre-mortem with top 3 failure modes?
□ Phase 6: Calculated handoff readiness score?
□ Phase 6: Total output ≥ 3,000 words (no domain), ≥ 5,000 (with domain), ≥ 6,500 (multiple)?
□ Phase 6: Included YAML frontmatter with temporal validity?
```

**IF ANY CHECKBOX IS UNCHECKED: GO BACK AND COMPLETE BEFORE DELIVERY**

**Phase 6 Delivery Complete When**:
- [x] All output checklist items checked
- [x] All quality gate checks pass
- [x] Safeguard checklist all items complete
- [x] Handoff readiness score ≥ 75 OR rationale for lower score provided
- [x] Document ready to send to recipient

---

## ANTI-PATTERNS TO AVOID (Completeness Failure Modes)

1. **Assumption Stacking**: Never build on unverified premises. Always cite code/test.
2. **Single-Source Confidence**: NEVER tag VERIFIED on code alone. Require cross-validation (≥ 1.5 weight).
3. **Lost Rationale**: Don't document WHAT without WHY. Use git history.
4. **Silent Defaults**: Call out implicit assumptions (env vars, library defaults).
5. **Incomplete Compliance**: If domain activated, missing compliance audit = CRITICAL GAP.
6. **No Pre-Mortem**: Skipping failure analysis guarantees post-handoff surprises.
7. **Competing Hypotheses Ignored**: State alternatives without addressing = lazy analysis.
8. **Empty Templates**: Never output compliance tables with placeholder text.
9. **Thin Output**: Output below minimum depth = incomplete evidence gathering.
10. **Passive File Loading**: If phase says "LOAD:", MUST read those files. "I already know" unacceptable.

---

## REFERENCE: What Counts as "Complete"

- **Complete** = All required elements present + meets minimum depth + evidence-backed + cross-validated
- **Substantial** = >80% of elements, minor gaps, generally well-evidenced
- **Partial** = 50-80% of elements, significant gaps, some sections weak
- **Incomplete** = <50% of elements, critical gaps, insufficient evidence

This checklist ensures documentation reaches **COMPLETE** status before delivery.
