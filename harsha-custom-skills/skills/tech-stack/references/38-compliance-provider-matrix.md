# Compliance Provider Matrix

## Executive Summary (5-line TL;DR)
- AWS, GCP, Azure cover ALL compliance frameworks (SOC 2, HIPAA, PCI-DSS, GDPR, FedRAMP, ISO 27001)
- Supabase, Vercel, Railway, Clerk, Sentry now offer BAAs — verify plan requirements (Team/Pro/Enterprise)
- Stripe and Paddle handle PCI-DSS compliance for you; never self-build payment card processing
- GDPR compliance available from most modern providers but requires YOUR implementation of data handling
- FedRAMP/GovCloud limits you to AWS GovCloud, Azure Government, or Google Cloud for Government only

## How to Use This File

**Quick lookup:** Find your compliance requirement in the right-hand column, see which providers/services support it.

**Compliance types priority:**
1. **SOC 2** - Audit of security, availability, processing integrity (most B2B SaaS)
2. **HIPAA/BAA** - Healthcare data (PHI) handling (US healthcare)
3. **PCI-DSS** - Credit card handling (any payments)
4. **GDPR** - EU personal data (EU customers)
5. **FedRAMP** - US government (federal contracts)
6. **ISO 27001** - Information security management (enterprise/global)

Legend: ✅ = Supported | ❌ = Not supported | ⚠️ = Partial/Requires enterprise plan

---

## Master Provider Compliance Matrix

### Cloud Infrastructure

| Provider | SOC 2 | HIPAA/BAA | PCI-DSS | GDPR | FedRAMP | ISO 27001 | Notes |
|----------|-------|-----------|---------|------|---------|-----------|-------|
| **AWS** | ✅ Full | ✅ BAA | ✅ Level 1 | ✅ DPA | ✅ GovCloud | ✅ | Industry standard, all regions, most mature |
| **Google Cloud** | ✅ Full | ✅ BAA | ✅ Level 1 | ✅ DPA | ✅ High | ✅ | Healthcare APIs, strong EU compliance |
| **Azure** | ✅ Full | ✅ BAA | ✅ Level 1 | ✅ EU Boundary | ✅ High | ✅ | Strongest EU data residency, Gov Cloud |
| **DigitalOcean** | ✅ Full | ✅ BAA | ⚠️ Partial | ✅ DPA | ❌ | ✅ | Affordable HIPAA option, limited PCI |
| **Hetzner** | ✅ Full | ❌ | ❌ | ✅ EU-only | ❌ | ✅ | EU-based, cheapest EU option, no US BAA |
| **Fly.io** | ✅ | ❌ | ❌ | ✅ DPA | ❌ | ⚠️ | Global edge platform, no compliance focus |
| **Railway** | ✅ | ❌ | ❌ | ✅ DPA | ❌ | ❌ | Developer-friendly, no compliance support |
| **Render** | ✅ | ❌ | ❌ | ✅ DPA | ❌ | ⚠️ | Simple deployments, no enterprise support |

### Hosting & Frontend Deployment

| Provider | SOC 2 | HIPAA | PCI | GDPR | EU Edge | Notes |
|----------|-------|-------|-----|------|---------|-------|
| **Vercel** | ✅ | ❌ | ❌ | ✅ EU | ✅ | No BAA, no PCI, ideal for non-regulated apps |
| **Netlify** | ✅ | ❌ | ❌ | ✅ DPA | ✅ | Similar to Vercel, good for JAMstack |
| **Cloudflare** | ✅ | ⚠️ Partial | ✅ Level 1 | ✅ Data localization | ✅ | Excellent for CDN/edge, not for PHI |
| **GitHub Pages** | ⚠️ | ❌ | ❌ | ⚠️ | ✅ | Free, but limited compliance |

### Databases & Data Storage

| Provider | SOC 2 | HIPAA/BAA | PCI | GDPR | EU Region | Type | Notes |
|----------|-------|-----------|-----|------|-----------|------|-------|
| **AWS RDS** | ✅ | ✅ BAA | ✅ | ✅ | ✅ | Managed SQL | Gold standard for compliance, all SQL engines |
| **MongoDB Atlas** | ✅ | ✅ BAA | ✅ | ✅ | ✅ | NoSQL | Full compliance, enterprise-ready |
| **CockroachDB** | ✅ | ✅ BAA (dedicated) | ⚠️ | ✅ | ✅ | Distributed SQL | Multi-region, geo-redundancy |
| **PlanetScale** | ✅ | ✅ BAA (enterprise) | ⚠️ | ✅ | ✅ | MySQL | MySQL serverless, enterprise BAA available |
| **Supabase** | ✅ | ❌ No BAA | ❌ | ✅ DPA | ✅ | Postgres | NOT for PHI/card data, open source option |
| **Neon** | ✅ | ❌ | ❌ | ✅ DPA | ✅ | Postgres | Serverless Postgres, early compliance stage |
| **Turso** | ❌ | ❌ | ❌ | ✅ | ✅ | SQLite | Edge SQLite, early stage, avoid regulated data |
| **Firebase/Firestore** | ✅ | ✅ (via GCP BAA) | ⚠️ | ✅ | ✅ | NoSQL | Inherits GCP compliance with BAA |
| **AWS DynamoDB** | ✅ | ✅ BAA | ✅ | ✅ | ✅ | NoSQL | Serverless, fully managed, BAA included |

### Authentication & Identity Management

| Provider | SOC 2 | HIPAA/BAA | PCI | GDPR | Enterprise BAA | Notes |
|----------|-------|-----------|-----|------|----------------|-------|
| **AWS Cognito** | ✅ | ✅ BAA | ⚠️ | ✅ | Included | Part of AWS compliance ecosystem |
| **Auth0** | ✅ | ✅ BAA | ❌ | ✅ EU hosting | Enterprise plan required | Industry standard, mature |
| **Okta** | ✅ | ✅ BAA | ⚠️ | ✅ | Included | Enterprise-focused, HIPAA-ready |
| **Firebase Auth** | ✅ | ✅ (via GCP BAA) | ⚠️ | ✅ | Inherited from GCP | Simple setup, GCP compliance required |
| **Clerk** | ✅ | ❌ | ❌ | ✅ DPA | ❌ | Modern developer experience, no PHI support |
| **Supabase Auth** | ✅ | ❌ | ❌ | ✅ | ❌ | Follows Supabase limitations |

### Monitoring & Observability

| Provider | SOC 2 | HIPAA/BAA | GDPR | PII-Safe | Notes |
|----------|-------|-----------|------|----------|-------|
| **Datadog** | ✅ | ✅ BAA (enterprise) | ✅ EU | ⚠️ | Be careful logging sensitive data; enterprise tier for BAA |
| **New Relic** | ✅ | ✅ BAA | ✅ EU | ⚠️ | Similar to Datadog, enterprise features |
| **Sentry** | ✅ | ❌ | ✅ EU | ❌ | Risk: PHI in error logs; use carefully |
| **Grafana Cloud** | ✅ | ❌ | ✅ EU | ⚠️ | Open source option, no BAA |
| **BetterStack** | ✅ | ❌ | ✅ | ⚠️ | Lightweight, no HIPAA focus |
| **AWS CloudWatch** | ✅ | ✅ BAA | ✅ | ⚠️ | Part of AWS compliance, BAA included |

### Email & Communication

| Provider | SOC 2 | HIPAA/BAA | GDPR | Use Case | Notes |
|----------|-------|-----------|------|----------|-------|
| **AWS SES** | ✅ | ✅ BAA | ✅ | Bulk email | Cheapest compliant option, BAA included |
| **Paubox** | ✅ | ✅ BAA | ✅ | Healthcare email | HIPAA-first design, encrypted by default |
| **Postmark** | ✅ | ❌ | ✅ | Transactional | Good for marketing/password resets, no BAA |
| **Resend** | ✅ | ❌ | ✅ | Developer email | Modern API, React templates, no BAA |
| **SendGrid** | ✅ | ❌ | ✅ | High volume | Enterprise features, no BAA for standard tier |
| **Gmail API** | ⚠️ | ❌ | ⚠️ | Personal use | Subject to standard Google policies, risky for business |

### Payment Processing & PCI Compliance

| Provider | PCI Level | SOC 2 | GDPR | EMV | Tokenization | Notes |
|----------|-----------|-------|------|-----|--------------|-------|
| **Stripe** | Level 1 | ✅ | ✅ | ✅ | Built-in | Industry standard, handles PCI for you (SAQ A) |
| **PayPal/Braintree** | Level 1 | ✅ | ✅ | ✅ | Built-in | Major alternative, also reduces PCI burden |
| **Adyen** | Level 1 | ✅ | ✅ | ✅ | Built-in | Enterprise-grade, supports 250+ payment methods |
| **Square** | Level 1 | ✅ | ✅ | ✅ | Built-in | Good for physical + digital payments |
| **Wise/TransferWise** | Level 1 | ✅ | ✅ | N/A | Built-in | International transfers, low fees |

### Compliance Automation Platforms

| Tool | Annual Cost | SOC 2 | HIPAA | PCI | ISO 27001 | GDPR | FedRAMP | Best For |
|------|------------|-------|-------|-----|-----------|------|---------|----------|
| **Vanta** | ~$6K-15K | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Comprehensive, seamless integrations |
| **Drata** | ~$4.2K-12K | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Accounting-friendly, API-first |
| **Secureframe** | ~$4K-10K | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | Mid-market, strong UX |
| **Thoropass** | ~$6K-16K | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | Detailed, thorough assessments |
| **Sprinto** | ~$3.6K-8K | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | Budget-friendly, ISO-focused |
| **OneTrust** | Enterprise | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | Enterprise risk/compliance suite |

---

## Compliance Stack Recipes

### Recipe 1: "I need SOC 2" (Most B2B SaaS)

**Difficulty:** Easy ✅
**Tech Stack Freedom:** Maximum

```
Cloud:      Any (AWS/GCP/Azure/Vercel/Railway all have SOC 2)
Database:   Any (Supabase/Neon/PlanetScale all have SOC 2)
Auth:       Any (Clerk/Auth0/Okta/AWS Cognito all have SOC 2)
Email:      Any (Postmark/Resend/SendGrid all have SOC 2)
Payments:   Stripe/PayPal/Adyen
Monitoring: Datadog/Sentry/New Relic/Grafana
Automation: Vanta or Drata (~$6K/year)
Timeline:   3-6 months with automation
```

**Key insight:** SOC 2 is the LEAST restrictive on tech stack choice. Focus on operational security, not integrations.

**Gotchas:**
- You still need actual security controls (firewalls, backups, access logs)
- Not sufficient for healthcare, payments with card data, or government
- Sentry can expose PII in error logs—sanitize before sending

---

### Recipe 2: "I need HIPAA" (Healthcare)

**Difficulty:** Hard 🔴
**Tech Stack Freedom:** Highly restricted

```
Cloud:      AWS, GCP (Healthcare APIs), or Azure (BAA REQUIRED)
            ❌ NOT: Vercel, Railway, Fly.io, Hetzner

Database:   AWS RDS, MongoDB Atlas, or PlanetScale Enterprise (BAA)
            ❌ NOT: Supabase, Neon, Turso (no BAA)

Auth:       Auth0 Enterprise, Okta, or AWS Cognito (BAA)
            ❌ NOT: Clerk, Firebase free tier

Email:      AWS SES or Paubox (BAA)
            ❌ NOT: SendGrid, Postmark (no BAA)

Monitoring: Datadog Enterprise or AWS CloudWatch (BAA)
            ❌ NOT: Sentry, Grafana (no BAA, PHI risk)

Compliance: Vanta or Drata (BAA coverage, HIPAA module)
Timeline:   6-12 months, significant changes needed
```

**Critical requirements:**
- Every service must have a signed Business Associate Agreement (BAA)
- Encryption at rest and in transit (TLS 1.2+)
- Audit logging everything
- Access controls & role-based permissions
- Annual risk assessment (HIPAA Security Rule)

**Gotchas:**
- HIPAA applies once you handle ONE patient record
- "Healthcare company" ≠ automatic HIPAA coverage; depends on data
- Subprocessors (Datadog, Paubox, etc.) also need BAAs
- AWS/GCP/Azure BAAs are expensive at scale

---

### Recipe 3: "I need PCI-DSS" (Payment Processing)

**Difficulty:** Medium 🟡
**Tech Stack Freedom:** High (if using Stripe)

```
OPTION A: Use Stripe/PayPal (Recommended)
  → You get SAQ A (simplest PCI assessment)
  → Stripe handles PCI for you
  → Any cloud/database stack works
  → Cost: 2.7% + $0.30 per transaction

OPTION B: Handle cards yourself
  → You need Level 1 PCI-DSS certification
  → Use tokenization: Stripe, VGS, Basis Theory
  → Network segmentation required
  → Annual audit cost: $10K-50K
  → NOT recommended unless high volume (<250K transactions)
```

**Stack if using Stripe:**

```
Cloud:      Any (AWS/GCP/Azure/Vercel all OK)
Database:   Any (no card data stored)
Auth:       Any
Payments:   Stripe (handles PCI)
Compliance: Minimal burden if using Stripe SAQ A
Timeline:   1-3 months
```

**Stack if handling cards (rare):**

```
Cloud:      AWS PCI-compliant regions, network segmentation
Database:   Encrypted, tokenized storage only
Firewall:   PCI-DSS firewall requirements
Monitoring: Intrusion detection system (IDS)
Compliance: Annual audit, significant engineering
Timeline:   6-12 months
```

**Gotchas:**
- Don't build your own payment form—use Stripe Elements or PayPal
- Never log card data (pan, CVV, expiry)
- PCI applies to "any entity that stores, transmits, or processes" card data
- Stripe/PayPal stores card tokens, not card data

---

### Recipe 4: "I need GDPR" (EU Customers)

**Difficulty:** Medium 🟡
**Tech Stack Freedom:** High

```
Cloud:      Any with EU region (most have this)
            AWS EU (Frankfurt, Ireland), GCP EU (Belgium), Azure EU (Netherlands, Ireland)

Database:   Any with EU region selection
            Choose EU region during setup

Analytics:  ❌ Google Analytics (needs explicit consent)
            ✅ Plausible, Umami, Fathom (GDPR-native)
            ✅ Matomo (self-hosted or GDPR provider)

Auth:       Any with DPA (Data Processing Agreement)
            Most vendors offer this by request

Email:      Any with DPA
            AWS SES, Postmark, Resend all have DPAs

Compliance: Vanta/Drata (GDPR module)
Timeline:   2-4 months (lighter than SOC 2)
```

**Key GDPR requirements:**
- Data Processing Agreement (DPA) with every vendor
- EU data residency (don't cross borders unnecessarily)
- Explicit consent for analytics/cookies (Cookie banner required)
- Right to erasure: ability to delete user data
- Data breach notification within 72 hours

**Gotchas:**
- GDPR is about consent, not just encryption
- Google Analytics = consent popup required
- "EU region" ≠ EU data residency unless explicitly configured
- Subprocessors also need DPAs (AWS, GCP, Datadog, etc.)
- Fines: up to 4% of global revenue or 20M EUR

---

### Recipe 5: "I need FedRAMP" (US Government)

**Difficulty:** Extreme 🔴🔴🔴
**Tech Stack Freedom:** None (government only)

```
Cloud:      ❌ ONLY AWS GovCloud or Azure Government
            ❌ NOT: Regular AWS, GCP, Azure
            ❌ NOT: Any startup cloud

Database:   Whatever FedRAMP cloud provides
            AWS RDS on GovCloud, Azure SQL on Gov

Auth:       AWS Cognito on GovCloud only

Compliance: FedRAMP JAB (typically 1-2 years, $100K+)
Timeline:   12-24 months
Cost:       $500K-2M to achieve
```

**Everything changes:**
- Separate infrastructure (GovCloud or Gov Cloud)
- FIPS 140-2 encryption (different crypto than commercial)
- US-citizen-only access required
- Enhanced audit trails
- Annual Authority to Operate (ATO) required

**Gotchas:**
- Most startups don't need FedRAMP (only government contracts)
- FedRAMP is NOT a product, it's an ATO (authorization to operate)
- Your entire vendor chain must be FedRAMP-authorized
- Cannot use any commercial SaaS unless it's FedRAMP-authorized
- Cost is prohibitive; only pursue if required by contract

---

## Quick Decision: "Can I Use [X] for [Y] Compliance?"

### Common Combinations

#### Supabase (Postgres + Auth + Realtime)
| Requirement | Can Use? | Notes |
|-------------|----------|-------|
| SOC 2 | ✅ Yes | Full support |
| HIPAA | ❌ No | No BAA offered |
| PCI | ❌ No | Not certified |
| GDPR | ✅ Yes | DPA available, EU regions |
| FedRAMP | ❌ No | Not in GovCloud |

**Verdict:** Good for non-regulated B2B SaaS. Avoid healthcare and payments.

---

#### Vercel (Next.js Hosting)
| Requirement | Can Use? | Notes |
|-------------|----------|-------|
| SOC 2 | ✅ Yes | Built-in |
| HIPAA | ❌ No | No BAA |
| PCI | ❌ No | Frontend only, use Stripe for payments |
| GDPR | ✅ Yes | EU regions, DPA available |
| FedRAMP | ❌ No | Not in GovCloud |

**Verdict:** Excellent for frontend. Pair with AWS/Stripe for regulated data.

---

#### Firebase / GCP
| Requirement | Can Use? | Notes |
|-------------|----------|-------|
| SOC 2 | ✅ Yes | GCP has SOC 2 |
| HIPAA | ✅ Yes (GCP BAA) | GCP offers healthcare APIs |
| PCI | ✅ Yes | With tokenization |
| GDPR | ✅ Yes | EU regions, Data Residency Controls |
| FedRAMP | ⚠️ Limited | GCP FedRAMP available, not all services |

**Verdict:** Solid enterprise choice. More mature HIPAA than AWS for healthcare verticals.

---

#### MongoDB Atlas
| Requirement | Can Use? | Notes |
|-------------|----------|-------|
| SOC 2 | ✅ Yes | Full support |
| HIPAA | ✅ Yes | BAA available on Enterprise |
| PCI | ✅ Yes | Paid plans only |
| GDPR | ✅ Yes | DPA, EU regions |
| FedRAMP | ❌ No | Not in GovCloud |

**Verdict:** Great for NoSQL needs. BAA requires Enterprise ($3K+/month).

---

#### Auth0
| Requirement | Can Use? | Notes |
|-------------|----------|-------|
| SOC 2 | ✅ Yes | Full support |
| HIPAA | ✅ Yes | Enterprise plan only (BAA) |
| PCI | ❌ No | Not certified for payment data |
| GDPR | ✅ Yes | EU data center option |
| FedRAMP | ❌ No | Not in GovCloud |

**Verdict:** Industry standard. HIPAA requires Enterprise ($1K+/month min).

---

## Compliance by Use Case

### B2B SaaS (Most Common)
**Essential:** SOC 2
**Optional:** ISO 27001 (for enterprise customers)

**Recommended Stack:**
- Cloud: Vercel + AWS backend (or just AWS)
- Database: Supabase or AWS RDS
- Auth: Clerk or Auth0
- Payments: Stripe
- Automation: Vanta (~$6K/year)
- **Timeline: 3-6 months**

---

### Healthcare SaaS (EHR/Medical)
**Essential:** HIPAA/BAA
**Optional:** SOC 2, ISO 27001

**Recommended Stack:**
- Cloud: AWS (most mature HIPAA)
- Database: AWS RDS with BAA
- Auth: AWS Cognito or Okta
- Email: AWS SES or Paubox
- Monitoring: Datadog Enterprise
- Automation: Vanta (HIPAA module)
- **Timeline: 6-12 months**

---

### Payment Platform
**Essential:** PCI-DSS
**Optional:** SOC 2, ISO 27001

**Recommended Stack (if using Stripe):**
- Frontend: Vercel
- Backend: Any (AWS/Railway/Render)
- Database: Any
- Payments: Stripe (handles PCI)
- Compliance: Minimal (SAQ A)
- **Timeline: 1-3 months**

---

### EU/GDPR-Focused
**Essential:** GDPR + DPAs
**Optional:** SOC 2

**Recommended Stack:**
- Cloud: AWS EU regions (Frankfurt/Ireland)
- Database: EU region specified
- Analytics: Plausible or Fathom (GDPR-native)
- Compliance: Vanta (GDPR module)
- **Timeline: 2-4 months**

---

### Enterprise/Government
**Essential:** FedRAMP (if US government) or ISO 27001
**Optional:** SOC 2, HIPAA

**Recommended Stack:**
- FedRAMP: AWS GovCloud only
- ISO 27001: Any major cloud + Vanta
- **Timeline: 6-24 months depending on requirement**

---

## Pricing Reference & Stability

### Cloud Infrastructure (Monthly, Baseline)
| Provider | Estimated Monthly | HIPAA Premium | Notes |
|----------|------------------|---------------|-------|
| AWS | $100-500 | +20-30% for logging/compliance | Biggest variable by region |
| Azure | $100-500 | Native included | Simplest HIPAA pricing |
| GCP | $100-500 | Similar to AWS | Good healthcare discounts |
| DigitalOcean | $5-100 | +BAA tier ~$500/month | Cheapest HIPAA option |

### Compliance Automation (Annual)
| Tool | Base Price | Features | ROI |
|------|-----------|----------|-----|
| Vanta | $6K-15K | Automated audits, integrations | Reduces manual audit cost by 50% |
| Drata | $4.2K-12K | Accounting-friendly | Great for startups |
| Secureframe | $4K-10K | Strong UX, mid-market | Good SMB option |

**Pricing Stability Note:**
<!-- PRICING_STABILITY: moderate | last_verified: 2026-03 | check_interval: 6_months -->
- Cloud pricing: Stable with annual discounts available
- Compliance tools: Growing market, expect 10-15% annual increases
- BAA pricing: Varies by vendor; negotiate at enterprise scale
- Recommendation: Budget compliance spend at 5-8% of cloud/engineering costs

---

## Compliance Burden by Requirement

| Requirement | Burden | Timeline | Annual Cost | Automation Help |
|------------|--------|----------|-------------|-----------------|
| SOC 2 | Light | 3-6 mo | $6-10K | ✅ High |
| HIPAA | Heavy | 6-12 mo | $30-50K | ⚠️ Medium |
| PCI (Stripe) | Minimal | 1-3 mo | $1-2K | ✅ High |
| PCI (Custom) | Severe | 6-12 mo | $50-100K+ | ❌ Low |
| GDPR | Medium | 2-4 mo | $5-15K | ✅ High |
| FedRAMP | Extreme | 12-24 mo | $500K-2M | ❌ None |
| ISO 27001 | Medium | 4-8 mo | $20-40K | ⚠️ Medium |

---

## Key Principles for Compliance Decisions

1. **Start with your actual requirement**, not marketing pressure
   - "We want SOC 2" ≠ your customers actually require it
   - Ask: Who's asking? What framework? Why?

2. **Use compliance platforms early** (Vanta/Drata)
   - They catch gaps before auditors do
   - Reduce manual work by 70-80%
   - Cost pays for itself in audit speed

3. **BAA is the expensive gate**
   - Most vendors will give BAA if you ask + pay
   - Budget $1-5K/month per vendor requiring BAA
   - Negotiate volume discounts at scale

4. **GDPR is about consent, not encryption**
   - You don't need special infrastructure
   - You need cookie banners and DPAs
   - Most vendors offer GDPR by default now

5. **PCI is borderline unnecessary**
   - Stripe/PayPal handle it for you (SAQ A)
   - Only pursue custom card handling if 10M+/year volume
   - Otherwise, it's engineering waste

6. **FedRAMP is a hard gate**
   - Only pursue if required by contract
   - Plan for 12-24 months
   - Costs $500K-2M minimum
   - Not worth it otherwise

---

## Related References
- [HIPAA Compliance Architecture Guide](./33-compliance-hipaa.md) — BAA requirements for healthcare applications
- [SOC 2 Compliance Architecture Guide](./34-compliance-soc2.md) — Vendor compliance certifications and audit requirements
- [PCI-DSS 4.0 Compliance Architecture Guide](./35-compliance-pci-dss.md) — Payment processor compliance matrix
- [GDPR & CCPA/CPRA Compliance Architecture Guide](./36-compliance-gdpr-ccpa.md) — Privacy compliance by provider
- [FedRAMP & Government Compliance Architecture Guide](./37-compliance-fedramp-gov.md) — Government authorization status

---

## Last Updated

- **Date:** March 2026
- **Next Review:** September 2026
- **Changes from last update:** Added CockroachDB BAA option, updated Datadog enterprise BAA, clarified Stripe SAQ A requirements
