# Decision Tree: Compliance-Driven Architecture

## Entry Point

```
What compliance do you need?
├── Healthcare (HIPAA)
│   → HIPAA PATH
├── Enterprise B2B (SOC 2)
│   → SOC 2 PATH
├── Payments (PCI-DSS)
│   → PCI-DSS PATH
├── EU Users (GDPR)
│   → GDPR PATH
├── US Government (FedRAMP)
│   → FEDRAMP PATH
├── Multiple compliance requirements
│   → MULTI-COMPLIANCE PATH
└── Not sure what I need
    → COMPLIANCE DISCOVERY
```

---

## COMPLIANCE DISCOVERY (Help me figure out what I need)

Use this decision table to identify which compliance frameworks apply to your business:

| Scenario | Compliance Required | Reference |
|----------|-------------------|-----------|
| Selling to businesses (B2B SaaS) | SOC 2 Type II (minimum) | `references/34-compliance-soc2.md` |
| Handling health data (patient records) | HIPAA | `references/33-compliance-hipaa.md` |
| Processing payments directly | PCI-DSS | `references/35-compliance-pci-dss.md` |
| Users in European Union | GDPR | `references/36-compliance-gdpr-ccpa.md` |
| Users in California + ($25M+ rev OR 100K+ users) | CCPA/CPRA | `references/36-compliance-gdpr-ccpa.md` |
| Selling to US federal government | FedRAMP | `references/37-compliance-fedramp-gov.md` |
| Selling to US DoD contractors | CMMC 2.0 | Depends on impact level |
| Handling criminal justice data | CJIS | Varies by state |
| Defense/export controlled products | ITAR/EAR | Requires legal review |
| Selling to state/local government | StateRAMP or SOC 2 | Varies by state |
| Handling children's data (<13) | COPPA | US federal requirement |
| None of the above | Privacy best practices only | No formal compliance needed |

---

## HIPAA PATH

Healthcare data requires HIPAA. **Critical constraint:** Any vendor touching PHI (Protected Health Information) must sign a Business Associate Agreement (BAA).

This eliminates most consumer-friendly vendors: **Supabase, Vercel, Railway, Render, Fly.io, Sentry, Clerk**.

### HIPAA Stack: MVP ($200–500/mo)

| Component | Choice | Why | Cost |
|-----------|--------|-----|------|
| Cloud | AWS (standard regions) | HIPAA eligible, BAA available | $0 base |
| Database | AWS RDS (PostgreSQL) | HIPAA eligible, automated backups | $100–200 |
| Authentication | AWS Cognito | HIPAA eligible, included with AWS | $0–50 |
| Storage | AWS S3 with encryption | HIPAA eligible, BAA included | $1–10 |
| Compute | AWS Lambda or EC2 | Both HIPAA eligible | $50–150 |
| Email | AWS SES | HIPAA eligible, cheap volume | $0–5 |
| Monitoring | CloudWatch (AWS native) | Included in AWS, HIPAA compatible | $0 |
| **Total** | | | **$200–500/mo** |

### HIPAA Stack: Growth ($500–2,000/mo)

| Component | Choice | Why | Cost |
|-----------|--------|-----|------|
| Cloud | AWS or Azure | Both HIPAA eligible | $0 base |
| Database | AWS RDS + read replicas | Handle scale + data durability | $200–500 |
| Authentication | Auth0 Enterprise (with BAA) | Better UX than Cognito, signed BAA | $500–1,500 |
| Logging | Datadog (with HIPAA plan) | Comprehensive APM + HIPAA compliance | $500–1,000 |
| Storage | AWS S3 + CloudFront | Global distribution, HIPAA eligible | $50–200 |
| Email | Twilio SendGrid (with BAA) | Volume discounts, HIPAA BAA available | $100–300 |
| Monitoring | CloudWatch + custom dashboards | AWS native + compliance logging | $0 |
| **Total** | | | **$1,350–3,500/mo** |

### HIPAA Stack: Enterprise (2,000+/mo)

```
Cloud:       AWS GovCloud or Azure Government
Database:    Dedicated Postgres cluster + AWS DMS for data replication
Auth:        Okta Enterprise (full HIPAA compliance)
Logging:     Splunk or Datadog Enterprise + compliance modules
Monitoring:  Comprehensive audit logging + SIEM
DLP:         Forcepoint or Symantec for data loss prevention
Compliance:  Dedicated compliance team + regular audits
Cost:        $2,000–10,000+/month (highly variable)
```

**Key HIPAA Requirements:**
- BAA signed with EVERY vendor
- Encryption at rest (256-bit AES)
- Encryption in transit (TLS 1.2+)
- Access logs for all PHI access
- 6-year audit trail retention
- Annual security training
- Incident response plan
- Business associate audit

**Reference:** `references/33-compliance-hipaa.md`

---

## SOC 2 PATH

SOC 2 Type II is the standard for B2B SaaS. **Good news:** Most modern vendors are SOC 2 certified. Almost no tech stack restrictions.

### SOC 2 Stack (Minimal Restrictions)

```
Cloud:       AWS, GCP, Azure, Vercel, Railway — all SOC 2 certified
Database:    Supabase, Neon, PlanetScale, Turso — all SOC 2 certified
Auth:        Clerk, Auth0, Okta, Better Auth — all SOC 2 compliant
Compute:     Vercel, Railway, Hetzner, Render — all options work
Monitoring:  Sentry, Datadog, New Relic — all SOC 2 ready
Email:       Resend, SendGrid, AWS SES — all compliant
```

### SOC 2 Timeline & Cost

| Timeline | Cost | What You Get |
|----------|------|-------------|
| **Type I** (2–4 weeks) | $5K–15K | Point-in-time security assessment |
| **Type II** (6–12 months) | $15K–60K | 6+ months of operational evidence |
| **Ongoing** | $10K–30K/year | Annual audits + compliance automation |

### When to Start SOC 2?

```
IF first enterprise deal requires it        → START NOW (Type I as interim)
IF Series A+ fundraising (in next 3 months) → Start in 3 months
IF B2B product growing (10k+ revenue)       → Start in 6 months
IF no enterprise interest yet               → Wait, focus on product
```

### SOC 2 Automation Stack

| Tool | Cost | Purpose |
|------|------|---------|
| **Vanta** | $6K/year | Continuous compliance + audit prep (easiest) |
| **Drata** | $4.2K/year | Full SOC 2 automation + workflow |
| **Sprinto** | $3.6K/year | Budget option, India-based |
| **Secureframe** | $5.5K/year | Powerful but complex setup |

**Recommendation:** Use Vanta for first-time SOC 2 audits (integrates with everything).

**Reference:** `references/34-compliance-soc2.md`

---

## PCI-DSS PATH

**The key insight:** Use Stripe/PayPal checkout and you avoid 95% of PCI requirements.

### PCI Decision Matrix

| Your Setup | Requirement | Scope | Cost |
|-----------|-------------|-------|------|
| **Stripe Checkout (redirect)** | SAQ A | 22 questions | $0–1K/year |
| **Stripe Elements (custom UI)** | SAQ A-EP | 139 questions | $1K–5K/year |
| **Handle raw card numbers** | SAQ D | 300+ questions | $50K–150K/year |
| **Marketplace (Stripe Connect)** | SAQ A | 22 questions | $0–1K/year |

### PCI Stack by Requirement Level

#### SAQ A (Stripe Redirect) — No Stack Restrictions

```
Frontend:    Any framework (React, Vue, Next.js)
Backend:     Any backend (Node.js, Python, Go, Rust)
Database:    Any database (Postgres, MongoDB, MySQL)
Hosting:     Any hosting (Vercel, Railway, Hetzner, AWS)
Total Cost:  $0 additional for PCI compliance
```

#### SAQ A-EP (Stripe Elements) — Minimal Restrictions

```
Security Headers:  Add Content Security Policy (CSP)
Script Integrity:  Enable SRI (Subresource Integrity) for Stripe.js
TLS:               Minimum TLS 1.2 (all hosts support this)
Frontend:          React, Vue, Next.js (any framework)
Backend:           Any backend, just don't log card numbers
Database:          Any database
Hosting:           Vercel, Railway, AWS, Hetzner
Additional Cost:   $1K–5K for security audit
```

#### SAQ D (Raw Card Handling) — Major Constraints

```
Cloud:             AWS, GCP, Azure only (not Vercel, Railway)
Network:           Segmented network (separate card-handling VPC)
Encryption:        FIPS 140-2 validated encryption modules
Monitoring:        Intrusion detection + SIEM (Wazuh or Splunk)
Personnel:         Background checks, NDA on all devs
Audit:             Annual QSA audit ($50K–150K)
Cost:              $100K–300K+ (Year 1), $50K–150K ongoing
```

**Strong recommendation:** Never handle raw card numbers. Use SAQ A with Stripe Checkout.

**Reference:** `references/35-compliance-pci-dss.md`

---

## GDPR PATH

GDPR primarily affects analytics and data residency, not your core stack.

### GDPR Stack Changes

| Component | Standard | GDPR-Compliant | Impact |
|-----------|----------|----------------|--------|
| **Analytics** | Google Analytics | Plausible ($9/mo) or Umami (self-hosted) | Replace entirely |
| **Database** | Any region | EU region (Supabase EU, Neon EU, AWS eu-west-1) | Select region only |
| **Auth** | Any with DPA | Most have DPA available | Minimal change |
| **Email** | SendGrid, Resend | Both have DPA signed | Minimal change |
| **CDN** | Cloudflare | Cloudflare (GDPR compliant) | Minimal change |

### Cookie-Free Architecture (Recommended)

The simplest GDPR approach: **Eliminate all tracking cookies**.

```
✗ Remove: Google Analytics
✗ Remove: Facebook Pixel
✗ Remove: HubSpot tracking
✗ Remove: Mixpanel
✗ Remove: Segment

✓ Replace with: Plausible ($9/mo) or self-hosted Umami
✓ Result: No consent banner needed, full GDPR compliance
```

### GDPR Stack Stack at Scale

| Scale | Analytics | Database | Cost |
|-------|-----------|----------|------|
| **MVP** | Umami self-hosted | Supabase EU | $0–25/mo |
| **Growth** | Plausible ($9/mo) | Neon EU | $50–100/mo |
| **Scale** | Plausible ($20/mo) | PostgreSQL EU region | $200+/mo |

**Key GDPR Requirements:**
- Data Processing Agreement (DPA) with vendors
- EU data residency (if users primarily in EU)
- Right to erasure (delete user data on request)
- 30-day breach notification
- Privacy Policy published
- Cookie consent only if using tracking cookies
- DPIA for high-risk processing

**Reference:** `references/36-compliance-gdpr-ccpa.md`

---

## FEDRAMP PATH

FedRAMP fundamentally changes your entire architecture. This is not a stack tweak—it's a complete re-build.

### FedRAMP Stack Requirements

| Requirement | Non-FedRAMP | FedRAMP | Impact |
|-------------|------------|---------|--------|
| **Cloud** | Any (Vercel, Railway, AWS) | AWS GovCloud or Azure Government only | Forced migration |
| **Regions** | Global | US only (GovCloud) | Data residency locked |
| **Encryption** | Standard TLS | FIPS 140-2 modules required | Mandatory |
| **Team** | Normal dev team | US persons only (for High/DoD impact) | Hiring restricted |
| **Audit** | SOC 2 ($20K–60K) | FedRAMP ($500K–2M) | Massive cost increase |
| **Timeline** | 6–12 months | 12–24 months minimum | Long authorization |

### FedRAMP Authorization Levels

| Level | Compliance Cost | Timeline | Use Case |
|-------|-----------------|----------|----------|
| **Low** | $150K–300K | 6–9 months (FedRAMP 20x) | Most startups |
| **Moderate** | $500K–800K | 12–18 months | Typical agencies |
| **High** | $1M–2M | 18–24 months | Sensitive data |
| **DoD** | $2M+ | 24+ months | Defense contractor |

### Realistic Startup Path to Government Sales

```
Year 1:
  - Get SOC 2 Type II ($20K–60K one-time)
  - Land state/local contracts (no FedRAMP required)
  - Build features for government (audit logs, SAML SSO)
  - Establish US presence

Year 2:
  - Apply for FedRAMP 20x (Low impact, faster path)
  - Target small federal contracts
  - Cost: $150K–300K
  - Timeline: 6–9 months

Year 3:
  - Target Moderate level government contracts
  - Full FedRAMP Moderate authorization
  - Cost: $500K–800K additional
```

### FedRAMP Alternative: StateRAMP

Many startups skip FedRAMP and sell to state/local governments instead:

```
StateRAMP:      State-specific compliance (varies by state)
Cost:           $50K–200K (much cheaper than FedRAMP)
Timeline:       3–6 months
Market Size:    Smaller than federal, but easier path
```

**Reference:** `references/37-compliance-fedramp-gov.md`

---

## MULTI-COMPLIANCE PATH

When you need multiple frameworks simultaneously.

### Common Compliance Combinations

| Combination | Tech Stack Impact | Annual Cost | Difficulty |
|-------------|-------------------|-------------|------------|
| **SOC 2 + GDPR** | Minimal (add EU region) | $10K–25K | Easy |
| **SOC 2 + PCI-DSS (SAQ A)** | Minimal (use Stripe) | $10K–20K | Easy |
| **SOC 2 + HIPAA** | Major (BAA vendors only) | $50K–150K | Hard |
| **SOC 2 + GDPR + PCI (SAQ A)** | Minimal | $20K–40K | Easy |
| **HIPAA + PCI-DSS** | Severe (very limited vendors) | $100K–300K | Very hard |
| **SOC 2 + FedRAMP** | Total rewrite (GovCloud only) | $500K–1M+ | Extremely hard |
| **SOC 2 + HIPAA + GDPR** | Major rework required | $100K–250K | Hard |

### Optimal Layering Strategy

**Start with:** SOC 2 (broadest enterprise appeal, helps with most others)
```
Time: 6–12 months
Cost: $30K–60K
Payoff: Opens enterprise B2B market
```

**Add GDPR:** EU region selection + Plausible/Umami
```
Time: 2–4 weeks (minimal)
Cost: Additional $200–500/mo for EU hosting
Payoff: EU market access + privacy advantage
```

**Add PCI-DSS:** Use Stripe → SAQ A (zero tech impact)
```
Time: 1–2 weeks (setup only)
Cost: $1K–5K (one-time assessment)
Payoff: Payment processing immediately compliant
```

**Add HIPAA:** Separate infrastructure, BAA-only vendors
```
Time: 3–6 months
Cost: $30K–100K (Year 1), $20K–60K annually
Payoff: Healthcare market (highest margins)
```

**Do NOT try to add FedRAMP** unless you have government contracts and budget for $500K+.

---

## Compliance Cost Quick Reference

| Framework | Year 1 Cost | Annual Ongoing | Tech Restrictions | Time to Audit |
|-----------|-------------|----------------|-------------------|--------------|
| **SOC 2 Type II** | $20K–60K | $10K–30K | None | 6–12 months |
| **HIPAA** | $30K–100K | $20K–60K | Significant | Ongoing |
| **PCI-DSS SAQ A** | $0–5K | $0–2K | None | 1–3 months |
| **PCI-DSS SAQ D** | $100K–300K | $50K–150K | Severe | 12+ months |
| **GDPR** | $5K–20K | $3K–10K | Minor | Ongoing |
| **CCPA/CPRA** | $10K–30K | $5K–15K | Minor | Ongoing |
| **FedRAMP Low** | $150K–300K | $100K–200K | Major | 6–9 months |
| **FedRAMP Moderate** | $500K–800K | $200K–400K | Extreme | 12–18 months |

---

## Compliance Automation & Tooling

Once you've chosen your compliance path, automate it:

### Continuous Compliance Tools

| Tool | Cost | Best For | Features |
|------|------|----------|----------|
| **Vanta** | $6K/year | First-time SOC 2 | Auto-logging, gap reports, audit prep |
| **Drata** | $4.2K/year | SOC 2 + ongoing | Workflow automation, policy templates |
| **Sprinto** | $3.6K/year | Budget option | Full compliance suite, audit-ready |
| **Secureframe** | $5.5K/year | Complex orgs | Risk management + compliance |
| **Laika** | $3K/year | Small teams | SOC 2 essentials + templates |

### Vendor Compliance Verification

Before selecting a vendor, verify compliance:

| Check | How | Tools |
|-------|-----|-------|
| **BAA availability** | Ask vendor support | Direct email to sales |
| **SOC 2 certification** | Review on SOC Register | socregister.org |
| **DPA signed** | Vendor contract section | Cloud provider agreements |
| **Security certifications** | Check vendor website | ISO 27001, FedRAMP, etc. |

**Reference:** `references/38-compliance-provider-matrix.md` for full matrix of which providers support which compliance.

---

## Compliance Decision Checklist

Before building, answer these questions:

```
1. Who are your target customers?
   [ ] Consumers → No formal compliance (privacy best practices)
   [ ] Small businesses → SOC 2 Type I (optional)
   [ ] Enterprises → SOC 2 Type II (required)
   [ ] Government → FedRAMP (mandatory)
   [ ] Healthcare → HIPAA (mandatory)

2. Do you handle sensitive data?
   [ ] No → No data compliance
   [ ] Payment cards → PCI-DSS SAQ A (use Stripe)
   [ ] Patient data → HIPAA
   [ ] EU user data → GDPR
   [ ] US government data → FedRAMP

3. What's your budget for compliance?
   [ ] $0 → Privacy best practices only
   [ ] <$10K/year → SOC 2 Type I or GDPR
   [ ] $20K–50K/year → SOC 2 Type II or HIPAA MVP
   [ ] $100K+/year → HIPAA growth or multi-compliance
   [ ] $500K+/year → FedRAMP

4. What's your timeline?
   [ ] <3 months → Can't do serious compliance (focus on SOC 2 Type I)
   [ ] 3–6 months → SOC 2 Type I or GDPR
   [ ] 6–12 months → SOC 2 Type II or HIPAA MVP
   [ ] 12+ months → Multiple compliance or FedRAMP
```

---

## COMPLIANCE FRAMEWORK COMPARISON: DETAILED DECISION GUIDE

Choosing the wrong compliance framework wastes tens of thousands of dollars. Use this guide to choose correctly.

### Framework Overview Table

| Framework | What It Certifies | Who Needs It | Mandatory Or Optional | Audit Type |
|-----------|-----------------|------------|----------------------|-----------|
| **SOC 2** | Security, reliability, confidentiality | B2B SaaS | Effectively mandatory for enterprise sales | Third-party auditor |
| **HIPAA** | Healthcare data protection | Healthcare companies, patient data handlers | Legally mandatory | HHS + third-party |
| **PCI-DSS** | Payment card security | Any company processing credit cards | Legally mandatory | PCI councils + QSA |
| **GDPR** | EU resident data protection | Companies with EU users | Legally mandatory | Self-certified + DPA |
| **FedRAMP** | US federal cloud security | Vendors selling to US federal government | Mandatory for fed contracts | Third-party assessor |
| **ISO 27001** | Information security management | Enterprise vendors, finance, healthcare | Optional but increasingly expected | Third-party auditor |
| **CCPA/CPRA** | California resident data rights | Companies with California users earning >$25M | Legally mandatory | Self-certified |

### COMPLIANCE FRAMEWORK SELECTION MATRIX

Not all frameworks are created equal. This deep matrix shows exactly what each framework requires.

### Detailed Framework Comparison

| Framework | Primary Goal | Auditor Type | Evidence Required | Cost (Year 1) | Cost (Annual) | Timeline |
|-----------|-------------|--------------|-------------------|--------------|--------------|----------|
| **SOC 2 Type II** | Security + reliability for B2B | Third-party auditor (Big 4) | 6+ months operational evidence | $15K–60K | $10K–30K | 6–12 mo |
| **HIPAA** | Healthcare data protection | HHS + auditor | 6-year audit trail, BAA docs | $30K–100K | $20K–60K | Ongoing |
| **PCI-DSS SAQ A** | Payment card security (minimal) | Self-assessment | 22 questions, security test | $0–5K | $0–2K | 1–3 mo |
| **PCI-DSS SAQ D** | Payment card security (full) | QSA auditor | 300+ controls, full audit | $100K–300K | $50K–150K | 12+ mo |
| **GDPR** | EU data protection | DPA + self-assessment | Privacy impact assessments, DPA | $5K–20K | $3K–10K | Ongoing |
| **FedRAMP Low** | US federal use (low risk) | Third-party assessor | 325 controls, full assessment | $150K–300K | $100K–200K | 6–9 mo |
| **FedRAMP Moderate** | US federal use (medium risk) | Third-party assessor | 325 controls + continuous monitoring | $500K–800K | $200K–400K | 12–18 mo |
| **ISO 27001** | Information security management | External auditor | 114 controls, management review | $50K–150K | $30K–80K | 12+ mo |

### Compliance Burden by Framework (estimated hours/year)

| Framework | Year 1 Setup | Ongoing Work | Team Size Needed |
|-----------|-------------|-------------|-----------------|
| **SOC 2 Type II** | 500 hours | 100 hours/year | 1 person (part-time) |
| **HIPAA** | 800+ hours | 200+ hours/year | 1 person (full-time) + legal |
| **PCI-DSS SAQ A** | 40 hours | 20 hours/year | 0.25 person (contractor) |
| **PCI-DSS SAQ D** | 2000+ hours | 500+ hours/year | 2–3 people (dedicated team) |
| **GDPR** | 200 hours | 100 hours/year | 0.5 person |
| **FedRAMP Low** | 3000+ hours | 1000+ hours/year | 3–5 people |
| **ISO 27001** | 1000+ hours | 300+ hours/year | 1–2 people |

---

## PROVIDER SELECTION MATRIX FOR EACH FRAMEWORK

Before choosing your infrastructure, ensure providers support your compliance needs.

### Compliance Certification by Cloud Provider

| Provider | SOC 2 | HIPAA | FedRAMP | PCI-DSS | ISO 27001 | GDPR | Notes |
|----------|-------|-------|---------|---------|-----------|------|-------|
| **AWS** | ✓ Type II | ✓ + BAA | ✓ GovCloud | ✓ | ✓ | ✓ EU regions | Most comprehensive |
| **Google Cloud** | ✓ Type II | Limited | ✓ | ✓ | ✓ | ✓ EU regions | Good for ML/data |
| **Azure** | ✓ Type II | ✓ + BAA | ✓ GovCloud | ✓ | ✓ | ✓ EU regions | Microsoft ecosystem |
| **Vercel** | ✓ Type II | ✗ | ✗ | ✓ | ✓ | ✓ | Great for startups, limited compliance |
| **Railway** | ✓ Type II | ✗ | ✗ | ✓ | ✗ | ✓ | Good for EU (Germany servers) |
| **Fly.io** | ✓ Type II | ✗ | ✗ | ✓ | ✓ | ✓ | Multi-region, good latency |
| **Heroku** | ✓ Type II | ✗ | ✗ | ✓ | ✓ | ✓ | Deprecated, not recommended |
| **Hetzner** | ✓ Type II | ✗ | ✗ | ✓ (self) | ✓ | ✓ EU | Cheapest, German data centers |
| **AWS GovCloud** | ✓ Type II | ✓ + BAA | ✓ Authorized | ✓ | ✓ | Limited | ONLY for US government |

### Database Provider Compliance

| Provider | SOC 2 | HIPAA | BAA | PCI-DSS | GDPR | Cost |
|----------|-------|-------|-----|---------|------|------|
| **Supabase** | ✓ | ✗ (Supabase Enterprise) | ✗ | ✓ | ✓ (EU) | $25–1000/mo |
| **Neon** | ✓ | ✗ | ✗ | ✓ | ✓ (EU branch) | $0–500/mo |
| **AWS RDS** | ✓ | ✓ | ✓ | ✓ | ✓ (EU region) | $50–500/mo |
| **Azure Database** | ✓ | ✓ | ✓ | ✓ | ✓ (EU) | $50–500/mo |
| **PlanetScale** | ✓ | ✗ | ✗ | ✓ | ✓ | $10–200/mo |
| **CockroachDB** | ✓ | ✗ | ✗ | ✓ | ✓ (regional) | $100–1000/mo |

### Auth Provider Compliance

| Provider | HIPAA BAA | Enterprise SSO | Cost |
|----------|-----------|---------------|------|
| **Supabase Auth** | ✗ (Enterprise) | ✓ | $0–1000 |
| **Clerk** | ✗ | ✓ (Pro+) | $0–200/mo |
| **Auth0** | ✓ Enterprise | ✓ | $0–1500/mo |
| **Okta** | ✓ | ✓ (built-in) | $500–2000/mo |
| **AWS Cognito** | ✓ | ✓ | $0–100/mo |
| **Azure AD** | ✓ | ✓ (Microsoft) | $0–600/mo |
| **Better Auth** | $0 (self-hosted) | $0 | $0 |
| **Keycloak** | $0 (self-hosted) | ✓ (built-in) | $0 |

---

## COST OF COMPLIANCE AT EACH LEVEL

Compliance is not a binary cost—it scales with your business.

### Total Cost of Compliance by Framework and Size

**100 customers (SMB tier):**

| Framework | Setup Cost | Annual Cost | Total Year 1 |
|-----------|-----------|-----------|-----------|
| SOC 2 Type I | $5K | $2K | $7K |
| GDPR only | $3K | $1K | $4K |
| PCI-DSS (SAQ A) | $1K | $0.5K | $1.5K |

**1,000 customers (Growth tier):**

| Framework | Setup Cost | Annual Cost | Total Year 1 |
|-----------|-----------|-----------|-----------|
| SOC 2 Type II | $30K | $10K | $40K |
| SOC 2 + GDPR | $35K | $15K | $50K |
| SOC 2 + HIPAA | $80K | $50K | $130K |

**10,000 customers (Scale tier):**

| Framework | Setup Cost | Annual Cost | Total Year 1 |
|-----------|-----------|-----------|-----------|
| SOC 2 Type II + GDPR | $50K | $20K | $70K |
| SOC 2 + HIPAA + GDPR | $150K | $100K | $250K |
| FedRAMP Low (if needed) | $200K | $150K | $350K |

### Cost Breakdown: SOC 2 Type II (Most Common)

```
Audit Fees:              $15K–30K (Big 4 auditor)
Automation Tool (Vanta): $6K/year
Evidence Collection:     5K-10K hours (internal time)
  = $20K for salary (average $10/hour burden rate)
Training:               $2K–5K
Policy/Documentation:   $3K–5K (external writer)

Total Year 1:           $40K–60K
Annual Ongoing:         $8K–15K (auto tool + audit review)
```

### Cost Breakdown: HIPAA (Healthcare)

```
Initial Compliance Setup:
  Risk Assessment:       $5K–10K
  Policies/Documentation: $5K–15K
  BAA Negotiations:      $3K–5K (legal)
  Technology Hardening: $10K–20K (encryption, audit logs)
  Training:             $2K–5K

Year 1 Total:           $30K–60K

Annual Ongoing:
  Audit (third-party):  $10K–30K
  Breach Response (est.): $5K–20K
  Infrastructure:       $20K–60K (AWS RDS + monitoring)
  Training:             $2K–5K

Annual:                 $35K–115K+
```

---

## AUDIT PREPARATION CHECKLIST

Use this before your actual audit to avoid delays.

### Pre-Audit (4 weeks before)

**Documentation:**
- [ ] Security policy document (10+ pages minimum)
- [ ] Incident response plan (documented procedures)
- [ ] Data handling procedures
- [ ] Access control matrix (who can access what)
- [ ] Change management log (last 6 months)
- [ ] Vendor security assessments (SOC 2, ISO 27001, BAA)

**Technical Evidence:**
- [ ] Firewall rules and network diagram
- [ ] Encryption certificate list (TLS, at-rest)
- [ ] Backup logs (last 6 months)
- [ ] Patch management logs
- [ ] Access logs (5 samples)
- [ ] Failed login attempts log
- [ ] Antivirus/endpoint protection proof

**Process Evidence:**
- [ ] 6+ months of change tickets (each with approval)
- [ ] User onboarding/offboarding records
- [ ] Security training completion records
- [ ] Vulnerability scan reports
- [ ] Penetration testing results

### Week Before Audit

- [ ] All logs are readable and searchable
- [ ] System access is documented in matrix format
- [ ] All vendor agreements are printed/ready
- [ ] Audit team has network access (VPN, SSH)
- [ ] Evidence is organized by control (easy navigation)

### During Audit

- [ ] Assign one person as audit liaison
- [ ] Provide rapid access to requested evidence
- [ ] Document all questions and answers
- [ ] Flag any timeline issues immediately
- [ ] Take notes on auditor comments

### Post-Audit (1–2 weeks after)

- [ ] Review draft report
- [ ] Identify gaps, prepare remediation plan
- [ ] Set timeline for fixes
- [ ] Track all remediation items in project management

---

## BAA VERIFICATION WORKFLOW

A Business Associate Agreement (BAA) is required for any HIPAA vendor.

### BAA Checklist

Before signing ANY vendor contract (especially for healthcare):

**Questions to ask vendor support:**

```
1. Do you offer a BAA?
   [ ] Yes, standard  [ ] Yes, custom  [ ] No (disqualified)

2. What does your BAA cover?
   [ ] Data encryption at rest
   [ ] Data encryption in transit
   [ ] Access logs (1 year minimum)
   [ ] Audit rights
   [ ] Breach notification (within 24 hours)
   [ ] Subprocessor management
   [ ] Data deletion on contract end

3. Subprocessors (vendors your vendor uses):
   [ ] Are they all listed?
   [ ] Do they each have BAAs?
   [ ] Can you audit them?

4. In case of breach:
   [ ] How quickly do they notify you?
   [ ] Who covers the cost of breach notification?
   [ ] Do they have cyber liability insurance?

5. What happens to data if they go out of business?
   [ ] Do they commit to data return/deletion?
   [ ] Is it in the BAA?
```

### Common BAA Issues

| Issue | Why It Matters | Resolution |
|-------|----------------|-----------|
| No BAA available | Vendor can't handle HIPAA data | Use different vendor |
| BAA requires custom negotiation | Delays contract signing | Budget 2–4 weeks |
| Subprocessors aren't listed | Hidden data sharing | Require full list before signing |
| No breach notification timeline | May violate HIPAA 60-day rule | Insert "within 48 hours" |
| Can't audit vendor | Can't prove compliance | Require right to audit |
| Vendor goes out of business | Data handling unclear | Require data destruction clause |

---

## ENCRYPTION REQUIREMENTS MATRIX

Different frameworks have different encryption requirements.

| Framework | At-Rest | In-Transit | Min Cipher | Key Management |
|-----------|---------|-----------|-----------|-----------------|
| **SOC 2** | AES-256 recommended | TLS 1.2+ | TLS_ECDHE_RSA_AES_256_GCM | Customer managed or provider |
| **HIPAA** | AES-256 required | TLS 1.2+ | Same as SOC 2 | Audit log required |
| **PCI-DSS** | AES-256 required | TLS 1.2+ | Minimum TLS 1.2 | Key rotation required |
| **FedRAMP Low** | AES-128 minimum | TLS 1.2+ | FIPS-approved cipher | Government-approved KMS |
| **GDPR** | Encryption if needed by DPA | TLS 1.2+ | Depends on processor | Processor responsible |

### Encryption Implementation Checklist

**At-Rest (Database, Storage):**
- [ ] All customer data encrypted by default
- [ ] Encryption key stored separately (not in code)
- [ ] Key rotation policy (90 days recommended)
- [ ] Hardware security module (HSM) for keys (enterprise only)
- [ ] Backups encrypted with same key

**In-Transit (Network):**
- [ ] TLS 1.2+ minimum (prefer 1.3)
- [ ] Valid certificate for domain
- [ ] HSTS enabled (HTTP Strict Transport Security)
- [ ] All internal communication encrypted (microservices)
- [ ] VPN for admin access

**Key Management:**
- [ ] Keys never logged or exposed in errors
- [ ] Key rotation documented
- [ ] Old keys retained for decryption (old data)
- [ ] Secure key exchange between services
- [ ] Access to keys logged and audited

---

## LOGGING & MONITORING FOR COMPLIANCE

Compliance frameworks require comprehensive logging.

### What Must Be Logged (Framework Requirements)

| Action | SOC 2 | HIPAA | PCI-DSS | FedRAMP |
|--------|-------|-------|---------|---------|
| **Login attempts** | ✓ | ✓ | ✓ | ✓ |
| **Failed logins** | ✓ | ✓ | ✓ | ✓ |
| **Data access** | ✓ | ✓✓ (detailed) | ✓ | ✓ |
| **Changes to access** | ✓ | ✓ | ✓ | ✓ |
| **Admin actions** | ✓ | ✓ | ✓✓ (detailed) | ✓✓ (detailed) |
| **Configuration changes** | ✓ | ✓ | ✓ | ✓ |
| **System events** | ✓ | ✓ | ✓ | ✓ |
| **Security events** | ✓ | ✓ | ✓ | ✓ |

### Log Retention Requirements

| Framework | Duration | Searchability |
|-----------|----------|---------------|
| **SOC 2** | 1 year minimum | 30 days hot, 11 months warm |
| **HIPAA** | 6 years | 90 days searchable, older archived |
| **PCI-DSS** | 1 year minimum | All 1 year searchable |
| **GDPR** | Per DPA (usually 1–3 years) | All retention period searchable |
| **FedRAMP** | 3 years minimum | All period searchable |

### Logging Architecture (Production Grade)

```
Application
  ↓
Central Log Collector (Fluentd, Filebeat)
  ↓
Log Storage (CloudWatch, Splunk, Datadog)
  ↓
Retention Policy (Archive old logs to S3)
  ↓
Compliance Reporting (Query, alert, export)
```

**Tools by framework:**

| Framework | Recommended Tool | Cost | Features |
|-----------|-----------------|------|----------|
| **SOC 2** | Datadog Logs | $15–30/host | Audit trail, dashboards, retention |
| **HIPAA** | Splunk Enterprise Security | $5K+/year | PHI handling, retention, alerts |
| **PCI-DSS** | CloudWatch + S3 Archive | $10–50/mo | Queryable, retained, immutable |
| **GDPR** | Axiom or ELK Stack | $10–100/mo | GDPR-compliant, searchable |
| **FedRAMP** | AWS CloudTrail + CloudWatch | $50–100/mo | Immutable, tamper-proof |

---

## COMPLIANCE TIMELINE EXPECTATIONS

Knowing the realistic timeline prevents missed deadlines.

### Timeline Estimates (In Months)

| Framework | Planning | Implementation | Audit | Total |
|-----------|----------|-----------------|--------|--------|
| **SOC 2 Type I** | 1 | 2–3 | 1 | **4–5 months** |
| **SOC 2 Type II** | 1 | 2–3 | 6–12 | **12–18 months** |
| **HIPAA MVP** | 1 | 3–4 | 1 | **5–6 months** |
| **HIPAA Full** | 1 | 3–4 | Ongoing | **6+ months (continuous)** |
| **PCI-DSS SAQ A** | 0.5 | 0.5 | 0.25 | **1–2 months** |
| **PCI-DSS SAQ D** | 1 | 6–9 | 3–6 | **12+ months** |
| **GDPR Prep** | 1 | 1–2 | Ongoing | **3+ months (continuous)** |
| **FedRAMP Low** | 2 | 6–9 | 6–12 | **18–24 months** |

### Critical Path (What You Can't Parallelize)

```
Month 1:  Compliance planning, vendor selection
Month 2:  Infrastructure setup, policy documentation
Month 3:  Implementation begins (logging, encryption)
Month 4:  Internal testing, evidence collection
Month 5:  External audit, remediation
Month 6:  Final approval, ongoing monitoring
```

**Can be parallelized:** Documentation writing, policy creation, training
**Can't be parallelized:** Evidence collection (6 months real data), external audit

---

## COMMON COMPLIANCE MISTAKES & HOW TO AVOID THEM

| Mistake | Cost | Prevention |
|---------|------|-----------|
| **Starting compliance too late** | 3–6 months delay to first deal | Plan compliance 6 months before enterprise sales |
| **Wrong framework chosen** | $50K+ wasted | Use compliance discovery table |
| **Vendors without required agreements** | Audit failure | Maintain vendor compliance matrix, verify before signing |
| **Insufficient logging** | Audit findings requiring re-do | Plan logging architecture before implementation |
| **Encryption not enabled by default** | Critical finding | Enable AES-256 day 1 |
| **No access control matrix** | Failed audit | Document who can access what (before audit) |
| **Audit logs not retained** | Finding | Archive all logs automatically |
| **Vendor changes mid-audit** | Restarted audit | Lock vendor stack 3 months before audit |
| **No incident response plan** | Critical finding | Document before going live |
| **Skipping employee training** | Finding | Mandatory training for all staff |

---

## COMPLIANCE DECISION FLOWCHART

Use this to make decisions without overthinking:

```
Do you handle user data outside of their country?
  YES → GDPR or local privacy law applies
  NO  → Continue

Do you handle health/medical information?
  YES → HIPAA applies
  NO  → Continue

Do you process credit cards directly?
  YES → PCI-DSS SAQ D (don't do this, use Stripe instead!)
  NO  → Continue (use Stripe → PCI-DSS SAQ A, minimal compliance)

Are you selling to enterprises?
  YES → SOC 2 Type II required
  NO  → Continue

Are you selling to US government?
  YES → FedRAMP required
  NO  → Privacy best practices only

Done! Your compliance path is clear.
```

---

## REAL-WORLD COMPLIANCE SCENARIOS & DECISIONS

### Scenario 1: B2B SaaS Startup (100 customers, $100k MRR)

**Your situation:**
- Enterprise customers starting to ask about compliance
- First $500k deal requires SOC 2
- No healthcare/government data
- EU users: <5%

**Decision matrix:**
```
Primary need: SOC 2 Type II
Timeline: 6–12 months (start now)
Cost: $40–60k Year 1, $10–15k annually
Vendors: Supabase ✓, Stripe ✓, SendGrid ✓ (all SOC 2 certified)
```

**Action plan:**
```
Month 1:   Hire compliance person or engage consultant ($50–100k)
Month 2:   Choose automation tool (Vanta, $6k/year)
Month 3:   Document security policies + incident response
Month 4–8: Vanta integration + control implementation
Month 9:   Start audit (6-month observation period begins)
Month 12:  Complete audit, get SOC 2 Type II certification
```

**Compliance roadmap:**
- Phase 1: Get SOC 2 Type II (win enterprise deals)
- Phase 2: If EU growth >20%, add GDPR (easy, just EU region selection)
- Phase 3: If healthcare ever needed, switch to HIPAA-ready vendors

---

### Scenario 2: Healthcare SaaS (Telemedicine Platform, 50k users)

**Your situation:**
- Handling patient medical records (PHI)
- HIPAA is legally mandatory
- Want to scale to 500k users
- Expanding to Europe next year

**Decision matrix:**
```
Primary need: HIPAA (mandatory)
Secondary need: GDPR (Year 2)
Timeline: HIPAA = 6+ months (ongoing), GDPR = 3 months (after HIPAA)
Cost: HIPAA Year 1 = $50–100k, Annual = $30–80k
     GDPR Year 1 = $10–20k, Annual = $5–10k
Vendors: AWS RDS ✓ BAA, Auth0 ✓ BAA, Datadog ✓ HIPAA Plan (all required BAAs)
```

**Critical decisions:**
```
Database: AWS RDS (only real option for HIPAA)
  Cost: $200–500/mo
  Alternative: Supabase Enterprise (BAA available, $2k+/mo)

Auth: Auth0 Enterprise + BAA
  Cost: $500–1500/mo
  Negotiable: Okta also good option

Logging: Datadog HIPAA Plan
  Cost: $500–1000/mo
  Critical: 6-year audit trail required
```

**Action plan:**
```
Month 1:   Engage HIPAA compliance consultant ($100k/year)
Month 1–2: Migrate infrastructure to AWS (RDS, Cognito, CloudWatch)
Month 3–4: Sign BAAs with all vendors
Month 5–6: Implement encryption at-rest + in-transit
Month 6–9: Set up logging + audit trails
Month 9–12: Internal audit + documentation
Month 12:  Ready for audit (ongoing process)
```

**Cost estimate: Year 1**
```
Infrastructure upgrade: $10k
Compliance consulting: $50–100k
BAA negotiations: $5k (legal review)
Tools (Vanta, Datadog): $15k
Training/documentation: $5k
Total: $85k–130k
```

---

### Scenario 3: Fintech/Payment Startup (10k+ transactions/day)

**Your situation:**
- Processing credit cards via Stripe
- Want to avoid PCI-DSS SAQ D hell
- Enterprise B2B customers
- Global operations

**Decision matrix:**
```
Primary need: PCI-DSS SAQ A (via Stripe)
Secondary: SOC 2 Type II (enterprise requirement)
Tertiary: International regulations (varies by country)
Timeline: SAQ A = 2–4 weeks, SOC 2 = 6–12 months
Cost: PCI SAQ A = minimal (<$5k), SOC 2 = $40–60k Year 1
Vendors: Stripe (SAQ A via Checkout), AWS (SOC 2), Datadog (SOC 2)
```

**Critical decision: Use Stripe Checkout (SAQ A) not SAQ D**
```
❌ WRONG (SAQ D - don't do this):
  Customer enters card info on your website
  Your server handles raw card data
  Your company is liable for $100k–300k audit
  Massive compliance burden

✓ RIGHT (SAQ A - use Stripe):
  Customer redirected to Stripe
  Stripe handles card data
  Your company only processes token
  Minimal compliance (22 questions)
  Stripe liable, not you
```

**Action plan:**
```
Week 1:   Audit: Are you handling raw card data?
          If YES → Migrate to Stripe Checkout immediately!
          If NO → Continue

Week 2–4: Implement Stripe Webhook handlers (checkout.completed, etc)
Week 4:   Run through SAQ A self-assessment (22 questions)
Month 2:  Start SOC 2 Type II process (separate from PCI)
Month 3:  Get SOC 2 Type I (interim, for enterprise deals)
Month 6+: Complete SOC 2 Type II (6-month observation)
```

**Cost estimate:**
```
PCI-DSS (SAQ A): $0–5k (compliance verification)
SOC 2 Type II: $40–60k
Total Year 1: $45–65k
```

---

### Scenario 4: EU-First SaaS (100% European users)

**Your situation:**
- 50k users, all in EU
- GDPR is legally mandatory
- No healthcare, government, or payment data
- Want to expand to US later

**Decision matrix:**
```
Primary need: GDPR
Timeline: 3–6 months (fairly quick)
Cost: $10–20k Year 1, $5–10k annually
Vendors: All major vendors GDPR-compliant (just need DPA signed)
Database: Supabase EU or Neon EU (geographically required)
```

**Action plan:**
```
Month 1: Audit data flows
  [ ] Where do you store user data?
  [ ] What third parties access it?
  [ ] Do you have DPAs signed?

Month 2: Replace non-compliant vendors
  [ ] Analytics: Replace Google → Plausible
  [ ] Auth: Supabase/Clerk both GDPR-OK
  [ ] Email: SendGrid/Resend both have DPA

Month 3: Document
  [ ] Privacy Policy (required)
  [ ] Data Processing Agreement (with vendors)
  [ ] Data Subject Rights procedures
  [ ] Breach notification procedures (30-day window)

Month 4: DPA Sign-Offs
  [ ] Get DPA from each vendor
  [ ] Store in shared folder
  [ ] Make accessible for audits

Ongoing: Monitor
  [ ] Any new vendors? Get DPA before using.
  [ ] New data processing? Document in register.
```

**Cost estimate:**
```
Vendor changes: $0 (most upgrades are free or minimal)
Legal review: $3–5k (check privacy policy)
Privacy training: $1–2k
Total: $5–10k
```

---

### Scenario 5: Government Contractor (Need FedRAMP)

**Your situation:**
- Landing first federal government contract (6-figure deal)
- Customer requires FedRAMP Low
- SaaS product (web-based)
- Budget is healthy (VC funded)

**Decision matrix:**
```
Primary need: FedRAMP Low
Timeline: 9–18 months (very long)
Cost: $200–400k first year, $100–200k annually
Vendors: AWS GovCloud ONLY (this is the constraint)
```

**Critical constraints:**
```
Cloud: AWS GovCloud ONLY (no alternatives)
      Cost: 30% more than commercial AWS
      Regions: US only (no Europe)

Team: Must be US persons only
      Hiring: More expensive than regular market
      Contractors: Must be cleared

Technology: FIPS 140-2 encryption required
           Custom development needed
           Off-the-shelf libraries may not qualify
```

**Realistic roadmap:**
```
Year 1: Get SOC 2 Type II first (2–3 months)
        This demonstrates security foundation
        Cost: $40–60k

Year 1–2: FedRAMP 20x program (Low impact level)
          Faster path than traditional FedRAMP
          Cost: $150–300k
          Timeline: 6–9 months
          Result: FedRAMP Low authorized

Year 2–3: Scale to Moderate (if needed for bigger deals)
          Full FedRAMP Moderate
          Cost: $500k–1M additional
          Timeline: 12–18 months
          Result: Can bid on larger federal contracts
```

**Cost estimate: Year 1**
```
Consultant/firm: $100–150k
Tool subscriptions: $20k
AWS GovCloud: $30–50k
Internal staff time: $50k+
Legal/compliance: $20k
Total: $220–290k
```

**Real talk:**
- Don't pursue FedRAMP unless you have $500k+ funding
- Have signed contract BEFORE starting FedRAMP (sunk cost otherwise)
- Plan for 18+ month first deal cycle
- Only worth it if deal size >$1M/year

---

## COMPLIANCE AUTOMATION DECISION TREE

Use this to pick the right compliance tool for your situation.

```
Do you have <$50k budget for compliance tooling?
  YES → Drata or Sprinto ($3.6k–4.2k/year)
  NO  → LaunchDarkly or Vanta ($6k/year)

Is this your first SOC 2 audit?
  YES → Vanta (easiest, best guides)
  NO  → Drata (more features, automation)

Do you need multiple compliance frameworks?
  YES → Secureframe or Vanta (multi-framework support)
  NO  → Sprinto (single framework, cheapest)

Is compliance a core business function?
  YES → Splunk or Datadog (deep customization)
  NO  → Vanta or Drata (pre-built templates)
```

---

## COMPLIANCE FAILURE SCENARIOS & COSTS

What happens if you fail the audit or have a breach?

### Audit Failure Costs

| Failure Type | Cost | Recovery Time | Example |
|-------------|------|---------------|---------|
| **Minor findings** | $5–20k (remediation) | 1–2 months | Weak password policy, incomplete logging |
| **Major findings** | $20–50k (engineering + audit retry) | 3–6 months | Unencrypted sensitive data, failed access controls |
| **Critical findings** | $50k–200k+ (infrastructure changes + re-audit) | 6–12 months | Hardcoded credentials, no encryption key management |

### Breach Notification Costs

| Scenario | Regulatory Cost | Notification Cost | Legal Cost | Total |
|----------|-----------------|-------------------|-----------|-------|
| **Small (100 records)** | $0–10k | $5k | $10k | $15–25k |
| **Medium (10k records)** | $20–50k | $20k | $50k | $90–120k |
| **Large (100k+ records)** | $100k+ | $100k+ | $200k+ | $400k+ |

**HIPAA Breach Example:**
```
Exposed 50k patient records
Notification: $50k (mail + credit monitoring)
HHS fine: $100k–$1.5M (per violation)
Lawsuits: $500k–5M+
Total damage: $650k–6.5M+
```

**Lesson:** Compliance is insurance. $100k compliance investment prevents $1M+ breach costs.

---

## COMPLIANCE VENDOR EVALUATION RUBRIC

When choosing a vendor, use this scorecard:

| Criteria | Weight | Score (1–5) | Notes |
|----------|--------|-------------|-------|
| **Has required compliance (BAA/SOC 2)** | 40% | ? | Non-negotiable |
| **Security track record** | 20% | ? | Any major breaches? |
| **Pricing** | 15% | ? | Cost per month × months needed |
| **Ease of implementation** | 15% | ? | Can you integrate in 2 days? |
| **Support quality** | 10% | ? | How fast do they respond? |

Example scoring:
```
Supabase for HIPAA-ready app:
  BAA available: 5/5 (Enterprise tier has it)
  Security: 4/5 (Postgres-based, good)
  Pricing: 3/5 (Enterprise plan expensive)
  Implementation: 5/5 (Postgres is standard)
  Support: 4/5 (Good docs, decent support)

  Weighted score: (5×0.4) + (4×0.2) + (3×0.15) + (5×0.15) + (4×0.1)
               = 2.0 + 0.8 + 0.45 + 0.75 + 0.4
               = 4.4/5 (Good choice)
```

---

## Next Steps

1. **Identify your compliance** using the COMPLIANCE DISCOVERY table (at top of document)
2. **Choose your primary framework** using the detailed comparison matrix
3. **Evaluate your vendors** against provider compliance matrix
4. **Budget for your path** using real-world scenario costs
5. **Plan your timeline** using realistic timeline estimates (6–12 months)
6. **Verify BAAs** before signing any vendor contracts
7. **Implement logging/encryption** per framework requirements
8. **Choose your automation tool** (Vanta for SOC 2, Drata for multi-framework)
9. **Schedule pre-audit** checklist 4 weeks before audit date
10. **Set up ongoing monitoring** to maintain compliance after certification
