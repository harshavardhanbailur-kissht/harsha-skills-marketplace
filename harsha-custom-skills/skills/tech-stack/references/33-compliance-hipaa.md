# HIPAA Compliance Architecture Guide

## Executive Summary (5-line TL;DR)
- HIPAA applies when handling PHI (Protected Health Information)
- BAA (Business Associate Agreement) required with every vendor touching PHI
- Technical safeguards: encryption at rest (AES-256) + in transit (TLS 1.2+), access controls, audit logging
- Covered entities: healthcare providers, health plans, clearinghouses + their business associates
- Non-compliance penalties: $100-$50,000 per violation, up to $1.5M/year per category

## What Counts as PHI

### 18 HIPAA Identifiers
Any of these elements, if associated with health information, constitute PHI:
1. Names
2. All geographic subdivisions smaller than a state (except broad categories)
3. Dates (birth, admission, discharge, death, etc.)
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers and serial numbers
13. Device identifiers and serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers (fingerprints, voice patterns)
17. Full-face photographic images
18. Any unique identifying number, characteristic, or code

### De-identification Safe Harbor Method
If you remove ALL 18 identifiers AND have no knowledge of any other identifying information, the data is no longer PHI:
```
✓ Safe to store without HIPAA compliance
✓ Acceptable for analytics/research without restrictions
✓ Can share with non-covered entities
```

### De-identification Expert Determination Method
Alternative: Have a qualified expert certify that the re-identification risk is "very small" (requires statistical analysis).

### When You DON'T Need HIPAA
- **Wellness apps**: Fitness tracking, meditation, sleep coaching (no clinical data, no integration with healthcare providers)
- **Consumer health data**: User-entered health information not connected to medical records
- **Non-clinical research**: Studies on de-identified health data
- **Employee wellness programs**: Generic health incentives, not individual medical data
- **Family health trees**: Personal genealogy, unless transmitted to/from covered entity
- **Health-related APIs**: Apps that don't store or process actual patient data

**Test**: "Does a healthcare provider, health plan, or medical device collect/store this data?" If NO → likely doesn't need HIPAA.

---

## HIPAA-Compliant Cloud Providers

### Tier 1: Full HIPAA Platform (BAA available, healthcare-focused)

| Provider | BAA Available | HIPAA Features | Starting Cost | Notes |
|----------|:---:|--|--|--|
| **AWS (full suite)** | ✓ | Dedicated instances, CloudTrail, KMS, Config, AWS Config for compliance | $200-500/mo minimum viable | Industry standard for healthcare |
| **Google Cloud (Healthcare API)** | ✓ | Healthcare API, DICOM/FHIR, de-identification tools, PHI data residency | $150-400/mo | Excellent for healthcare ML |
| **Azure (Health Data Services)** | ✓ | FHIR API, DICOM, MedTech service, native HIPAA compliance features | $200-500/mo | Strong Microsoft ecosystem integration |
| **Oracle Health (Cerner)** | ✓ | Full EHR platform, integrated clinical workflows | Enterprise pricing | Use only if deploying existing Cerner |

### Tier 2: HIPAA-Capable (BAA available, general cloud)

| Provider | BAA | HIPAA Ready | Cost | Use Case |
|----------|:---:|:---:|--|--|
| **Firebase** | Yes (via Google Cloud) | ✓ Requires specific config | $50-150/mo | Real-time apps with proper architecture |
| **DigitalOcean** | ✓ | ✓ HIPAA-ready droplets available | $50-200/mo | VPS-based deployments |
| **Heroku** | Yes (Enterprise Shield only) | ✓ Enterprise tier | $250+/mo | Limited use, cost-prohibitive |
| **Supabase** | ✓ BAA on Team plan+ | ✓ Requires Team plan config | $25+/mo (Team plan) | BAA available since 2024; requires Team plan or higher, dedicated project config, encryption verification |
| **Vercel** | ✓ BAA on Pro+Enterprise | ✓ With proper architecture | Pro plan pricing | BAA available on Pro and Enterprise plans; edge functions need careful PHI routing review |
| **Railway** | ✓ BAA add-on available | ✓ With BAA add-on | Base + add-on cost | BAA offered as add-on; requires explicit opt-in and compliance configuration |
| **Render** | ✗ No BAA currently | ✗ NOT suitable | N/A | **DO NOT USE for PHI** — verify status as this may change |
| **Fly.io** | ✓ BAA available | ✓ With proper config | Standard pricing | BAA available; requires dedicated instances and proper network isolation |

### Tier 3: Healthcare-Specific Platforms (PaaS)

| Platform | What It Does | Cost | Notes |
|----------|--|--|--|
| **Aptible** | HIPAA-compliant PaaS, automated compliance | $500-999/mo | Best for startups, includes compliance tooling |
| **Datica (now Sansoro)** | Healthcare integration, HL7/FHIR integration, cloud management | Enterprise | Strong for hospital integrations |
| **ClearDATA** | Healthcare cloud management, data security, compliance automation | Enterprise | Legacy system integration specialist |

---

## HIPAA-Compliant Stack Recommendations

### MVP Healthcare App ($200-500/mo)

Suitable for: Early-stage telehealth, patient portal MVP, small practice tool

```
Cloud Infrastructure:  AWS
Compute:              ECS Fargate (serverless container) OR Lambda (if appropriate)
Database:             RDS PostgreSQL (AES-256 encryption, private subnet, Multi-AZ)
Authentication:       Cognito with MFA OR Auth0 (requires BAA)
File Storage:         S3 (server-side encryption, versioning, access logging)
Email/SMS:            AWS SES (with BAA) OR Paubox (HIPAA email specialist)
Monitoring:           CloudTrail + CloudWatch + basic alarms
Audit Logging:        CloudTrail (free tier sufficient)
TLS:                  AWS Certificate Manager (automatic renewal)
Network:              VPC with private subnets, security groups, no public internet
```

**Architecture Diagram**:
```
User → CloudFront/WAF → ALB → ECS Fargate → RDS (private)
                                ↓
                            S3 (encrypted)
                                ↓
                            CloudTrail logs
```

**Cost Breakdown**:
- RDS db.t3.micro: ~$30/mo
- ECS Fargate: ~$50-100/mo
- S3: ~$5-20/mo
- NAT Gateway: ~$30/mo
- CloudFront (optional): $20-50/mo
- **Total**: $150-250/mo

---

### Growing Healthcare App ($500-2000/mo)

Suitable for: 100-5000 users, regional health system, mid-size practice

```
Cloud Infrastructure:  AWS or GCP
Compute:              ECS + Application Load Balancer with WAF
Database:             RDS PostgreSQL Multi-AZ with read replicas
Authentication:       Auth0 or Okta (enterprise BAA)
File Storage:         S3 with intelligent-tiering + CloudFront CDN
Monitoring:           CloudTrail + Datadog (BAA available) + PagerDuty
Audit Logging:        Custom audit log table (immutable) + CloudTrail
Notifications:        SNS for alerts, Datadog for SIEM
API Rate Limiting:    API Gateway throttling + WAF rate-based rules
Backup Strategy:      Automated daily backups with tested recovery (RTO: 4hr, RPO: 1hr)
Compliance Tooling:   Vanta ($6k/yr) OR Drata ($4.2k/yr) for continuous monitoring
```

**Additional Requirements at This Scale**:
- Formal BAA review with all vendors
- Documented incident response procedures
- Annual risk assessment (required by HIPAA)
- Security awareness training for team
- Encryption key management (AWS KMS with key rotation)
- DLP (Data Loss Prevention) tools

**Cost Breakdown**:
- RDS (db.r5.large Multi-AZ): $200-400/mo
- ECS + ALB: $150-250/mo
- CloudFront + S3: $50-150/mo
- Datadog: $200-500/mo
- Compliance platform: $350-500/mo
- **Total**: $950-1,800/mo

---

### Enterprise Healthcare ($2000+/mo)

Suitable for: 10,000+ users, health system operations, government contractors

```
Cloud Infrastructure:  AWS GovCloud, Azure Government, or private cloud
Compute:              EKS (Kubernetes) with dedicated node pools, auto-scaling
Database:             Aurora PostgreSQL (Multi-region read replicas) OR Cosmos DB
Authentication:       Okta or Azure AD B2C with SAML/OpenID Connect
File Storage:         S3 with Object Lock (immutable retention) + CloudFront
FHIR Integration:     AWS HealthLake OR Azure Health Data Services
Monitoring:           Datadog + Splunk + native cloud SIEM
Audit Logging:        Splunk with 7-year retention, real-time alerting
Network:              VPC peering, DX for on-premises connectivity, WAF everywhere
Encryption:           KMS with HSM-backed keys, key rotation monthly
Backup Strategy:      Multi-region backup with 7-year archive, annual DR test
Compliance:           Vanta/Drata + external SOC 2 Type II audit + HITRUST certification
```

**Enterprise-Grade Safeguards**:
- Dedicated security operations team (SOC)
- Red team/penetration testing (annual)
- HITRUST CSF certification ($50-150K, 6-month process)
- Business associate management platform
- Advanced threat detection (EDR on all systems)
- Incident response team with playbooks
- Legal review of all BAAs

**Cost Breakdown**:
- EKS cluster: $400-800/mo
- Aurora: $500-1,200/mo
- Datadog + Splunk: $1,000-3,000/mo
- Compliance/audit: $2,000-5,000/mo
- Security team: $100K-300K/year (5-10 people)
- **Total**: $2,000-10,000+/mo (infrastructure only)

---

## Technical Safeguards Checklist

### Encryption
- [ ] **At Rest**: AES-256 for all PHI storage (database, S3, backups, etc.)
- [ ] **In Transit**: TLS 1.2+ minimum (TLS 1.3 preferred)
- [ ] **Key Management**: Use cloud KMS, rotate keys every 90 days
- [ ] **Mobile**: Device encryption mandatory (iOS/Android native)
- [ ] **Offline**: Encrypted cache only, clear on logout

### Access Controls
- [ ] **RBAC**: Role-based access control with least privilege
- [ ] **MFA**: Multi-factor authentication for all users
- [ ] **Session Timeout**: Maximum 15 minutes of inactivity
- [ ] **Password Policy**: 12+ characters, complexity requirements
- [ ] **Admin Access**: Separate admin accounts, never used for normal work
- [ ] **API Keys**: Short-lived tokens (< 24 hours), service accounts, no hardcoding

### Audit & Logging
- [ ] **PHI Access**: Every access logged (who, what data, when, outcome)
- [ ] **CloudTrail**: All AWS API calls logged for 90+ days
- [ ] **Application Logs**: Structured logging without PHI, indexed for searchability
- [ ] **Log Integrity**: Tamper-evident (write-once storage or immutable logs)
- [ ] **Log Retention**: 6-7 years minimum
- [ ] **Monitoring**: Real-time alerts for suspicious access patterns

### Data Protection
- [ ] **Backup Strategy**: Daily automated backups, tested recovery (RTO: 4 hours)
- [ ] **Version Control**: Keep 30 days of point-in-time recovery
- [ ] **Disaster Recovery**: Off-region backup, annually tested
- [ ] **Data Integrity**: Checksums for critical records, database constraints
- [ ] **De-identification**: Anonymization tools for non-production data

### Network Security
- [ ] **Network Segmentation**: PHI in private subnets, no public internet
- [ ] **WAF**: Web Application Firewall for DDoS/injection attacks
- [ ] **VPN/Bastion**: Jump host for admin access
- [ ] **Intrusion Detection**: IDS/IPS tools monitoring traffic
- [ ] **DLP**: Data loss prevention for email, uploads, etc.

### Application Security
- [ ] **Code Review**: All code reviewed before production
- [ ] **Dependency Scanning**: Regular vulnerability scanning (Dependabot, Snyk)
- [ ] **SAST**: Static code analysis in CI/CD pipeline
- [ ] **Input Validation**: All user inputs validated, parameterized queries
- [ ] **Error Handling**: Generic error messages, detailed logging only
- [ ] **Security Headers**: CSP, X-Frame-Options, HSTS, etc.

### Breach Response
- [ ] **Breach Procedure**: Documented response steps
- [ ] **Notification Timeline**: 72-hour rule for breach notification
- [ ] **Legal Counsel**: Pre-arranged breach counsel (e.g., Breach Coach)
- [ ] **Credit Monitoring**: Offer 1-2 years for affected individuals
- [ ] **Documentation**: Breach assessment report, remediation plan

---

## BAA Decision Matrix

Use this flowchart to determine when a BAA is required:

```
Does the vendor touch, store, process, or access PHI?
├─ YES → BAA REQUIRED (non-negotiable)
│  ├─ Sign BAA before any data is transmitted
│  ├─ Verify vendor indemnification language
│  └─ Document vendor audit rights (annual minimum)
│
└─ NO → Do they handle infrastructure only (no PHI access)?
   ├─ YES → BAA still RECOMMENDED for:
   │  ├─ Cloud computing platforms (AWS, GCP, Azure)
   │  ├─ CDNs and DDoS protection (Cloudflare, Akamai)
   │  ├─ Monitoring tools (if they have API access)
   │  └─ Load balancers and firewalls
   │
   └─ NO → Is this a subcontractor of your BA?
      └─ YES → Subcontractor BAA required (passes liability chain)
```

### Common Vendor BAA Status

**Always Require BAA**:
- Cloud providers (AWS, GCP, Azure, DigitalOcean)
- Email/communication tools (SendGrid, Twilio, etc.)
- Analytics (Mixpanel, Amplitude — only if not tracking PHI)
- CRM systems (Salesforce, HubSpot)
- Ticketing/helpdesk (Zendesk, Jira Service)

**Verify BAA Availability**:
- Auth0 (yes, available)
- Okta (yes, available)
- Datadog (yes, available)
- PagerDuty (yes, available)
- Sentry (available but requires careful setup — avoid logging PHI)
- Google Analytics (only via specific HIPAA setup)

**BAA NOT Available** (don't use for PHI):
- Supabase
- Vercel
- Netlify
- Railway
- Render
- Fly.io
- Basic Firebase
- Heroku (except Enterprise Shield)

---

## Common HIPAA Mistakes in Tech Stacks

### 🔴 Critical Mistakes (Will Fail Audit)

1. **Using Supabase/Firebase without BAA for PHI storage**
   - ❌ `const db = supabase.from('patients').select()`
   - ✓ Use AWS RDS or GCP Cloud SQL instead

2. **Logging PHI in application logs**
   - ❌ `console.log('Patient ' + patient.name + ' diagnosed with ' + condition)`
   - ✓ `console.log('Event: diagnosis_recorded, patient_id: ' + hashId(patient.id))`
   - Watch out for: Sentry, LogRocket, DataDog (configure to exclude PHI)

3. **Storing PHI in client-side storage**
   - ❌ `localStorage.setItem('patient_data', JSON.stringify(patientData))`
   - ✓ Keep only session token, fetch fresh data on load

4. **Sending PHI via unencrypted email**
   - ❌ `nodemailer.send({ to: email, subject: 'Your test results', text: results })`
   - ✓ Use Paubox, AWS SES with encryption, or send only secure link

5. **Not encrypting local/mobile device storage**
   - ❌ `fs.writeFileSync('patient.txt', patientData)`
   - ✓ iOS: use Keychain, Android: use EncryptedSharedPreferences

### ⚠️ Compliance Mistakes (Will Be Flagged)

6. **Not having breach notification procedures**
   - ❌ Discovering breach but no documented response
   - ✓ Written procedure, legal counsel contact, notification templates, 72-hour timer

7. **PHI in URLs or query parameters**
   - ❌ `/patient-portal?patient_id=12345&mrn=MRN-XXXXX`
   - ✓ `/patient-portal/secure-id-token` (token maps server-side)
   - URLs appear in: browser history, server logs, proxy logs, referrer headers

8. **Not using MLAs (Minimum Necessary)**
   - ❌ Loading all patient fields even if form only needs name + DOB
   - ✓ Query only required fields: `SELECT name, dob FROM patients`

9. **No encryption key management**
   - ❌ All data encrypted with same static key
   - ✓ Unique key per patient/record, key rotation every 90 days

10. **Analytics tools capturing PHI**
    - ❌ Google Analytics tracking form submissions with patient names
    - ✓ Strip PHI before sending to analytics, or use custom events only

---

## HIPAA + HITRUST Decision Tree

```
What's your organization size/stage?

├─ Startup/MVP (< 1000 users)
│  └─ Approach: HIPAA self-attestation
│     ├─ Annual risk assessment (internal)
│     ├─ SOC 2 Type II (external audit, ~$20K)
│     ├─ Documented security policies
│     └─ Cost: $0 (self) + $20K audit = $20K total
│
├─ Growth (1000-50K users)
│  └─ Approach: HIPAA + SOC 2 Type II
│     ├─ Continuous compliance (Vanta/Drata)
│     ├─ External auditor engagement
│     ├─ HIPAA Security Rule assessment
│     └─ Cost: $6-10K/year compliance tool + $20K audit = $26-30K
│
└─ Enterprise or Selling to Large Health Systems
   └─ Approach: HIPAA + HITRUST CSF Certification
      ├─ HITRUST CSF ($50-150K, 6-month process)
      ├─ Required for: major health systems, insurers, government
      ├─ Third-party assessment organization (e.g., Coalfire)
      ├─ Annual surveillance audit
      └─ Cost: $150K initial + $30K/year maintenance

Special Cases:

IF selling to Federal health programs (VA, IHS, DoD)
└─ Add: FedRAMP compliance ($100K+, 12+ months)

IF handling sensitive health data (mental health, substance abuse, HIV)
└─ Add: 42 CFR Part 2 compliance (even stricter than HIPAA)

IF international expansion
└─ Add: GDPR (EU), PIPEDA (Canada), equivalent frameworks
```

---

## HIPAA Compliance Monitoring Tools

### Automated Continuous Compliance

| Tool | Price | What It Does | Best For |
|------|-------|--|--|
| **Vanta** | $6K-15K/year | Continuous HIPAA monitoring, audit automation | Startups, growth |
| **Drata** | $4.2K-12K/year | Continuous compliance, audit trails | Finance/healthcare |
| **Sprinto** | $5K-20K/year | Compliance as code, policy templates | Enterprise |
| **Hyperproof** | Custom | Manual evidence collection automation | Large orgs |

### Compliance Auditors

| Type | Cost | Timeline | Purpose |
|------|-------|--|--|
| **SOC 2 Type II** | $15K-30K | 6 months | Standard for SaaS health companies |
| **HITRUST CSF** | $50K-150K | 6 months | Required for large health systems |
| **HIPAA Security Assessment** | $10K-20K | 8 weeks | Self-attestation validation |

---

## Related References
- [Compliance Provider Matrix](./38-compliance-provider-matrix.md) — Cross-reference for BAA availability across vendors
- [SOC 2 Compliance Architecture Guide](./34-compliance-soc2.md) — Complementary compliance standard for healthcare SaaS
- [GDPR & CCPA/CPRA Compliance Architecture Guide](./36-compliance-gdpr-ccpa.md) — Handles international patient data requirements
- [Modern Web Security & Zero Trust Architecture](./44-modern-web-security-zero-trust.md) — Technical safeguards architecture details
- [Multi-Tenancy Architecture Patterns for SaaS Applications](./56-multi-tenancy-architecture-saas.md) — Isolation patterns for healthcare multi-tenant systems

---

## Pricing Stability Note

<!-- PRICING_STABILITY: low | last_verified: 2026-03 | check_interval: 6_months -->

Cloud provider pricing for HIPAA-eligible services changes frequently. Verify current pricing at provider websites. The architecture patterns and BAA requirements are stable; specific dollar amounts should be validated. Check:

- **AWS Pricing**: https://aws.amazon.com/pricing/ (HIPAA services listed separately)
- **GCP Pricing**: https://cloud.google.com/pricing (Healthcare API pricing)
- **Azure Pricing**: https://azure.microsoft.com/pricing/ (Health Data Services)
- **Compliance Tools**: Contact for current quotes (annual volume discounts available)

---

## Quick Reference: Stack Decision Flowchart

```
Starting a healthcare app?

1. Does your app handle PHI?
   ├─ NO → Use any modern stack (Vercel, Supabase, etc.)
   └─ YES → Continue...

2. Will you be handling PHI?
   ├─ NO (consultative only, no storage) → Reduced HIPAA requirements
   └─ YES → Use Tier 1 or Tier 2 provider

3. Budget and scale?
   ├─ MVP ($200-500/mo) → AWS minimal + RDS + S3
   ├─ Growth ($500-2K/mo) → AWS full stack + Datadog + Vanta
   └─ Enterprise ($2K+/mo) → AWS/GCP/Azure dedicated + HITRUST path

4. Who are your customers?
   ├─ Individual patients → HIPAA self-attestation sufficient
   ├─ Small practices → SOC 2 Type II recommended
   ├─ Health systems → HITRUST CSF required
   └─ Government (VA/IHS) → FedRAMP + HIPAA required

5. Timeline to compliance?
   ├─ Immediate (< 1 month) → Pre-built stacks (Aptible, ClearDATA)
   ├─ Standard (1-3 months) → AWS/GCP + Vanta automation
   └─ Thorough (3-6 months) → Full SOC 2 Type II audit
```

---

## Key Takeaways

1. **BAA is non-negotiable** — If a vendor touches PHI, you need a BAA in writing before any data is shared.

2. **Infrastructure is just the beginning** — The majority of HIPAA work is process, documentation, and access controls, not technology.

3. **Encryption is necessary but not sufficient** — HIPAA requires encryption, but also audit logs, access controls, and incident response.

4. **Cost scales with compliance** — MVP is $200-500/mo, but compliance tooling adds $4-15K/year. Budget accordingly.

5. **Self-hosting doesn't avoid HIPAA** — Even open-source self-hosted solutions require the same technical controls (encryption, logging, access controls).

6. **Breach notification is mandatory** — 72-hour notification rule, affected individual notification, and HHS reporting are non-negotiable.

7. **Compliance is continuous** — Annual risk assessments, policy updates, and security training are ongoing requirements.

