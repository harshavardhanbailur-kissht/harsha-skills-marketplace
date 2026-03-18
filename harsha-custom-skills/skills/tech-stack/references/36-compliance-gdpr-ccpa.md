# GDPR & CCPA/CPRA Compliance Architecture Guide

## Executive Summary

Privacy compliance is not optional—it's a foundational architecture decision. This guide covers the two most impactful privacy regulations:

- **GDPR** (General Data Protection Regulation): Applies if you have **any users in the EU/EEA**, regardless of where your company is located. Fines up to €20M or 4% of global revenue.
- **CCPA/CPRA** (California Consumer Privacy Act / California Privacy Rights Act): Applies if you're a for-profit business with users in California AND meet at least one threshold: >$25M revenue, >100K California consumers, or >50% revenue from selling consumer data. Fines up to $7,500 per intentional violation.

### Key Principle: Privacy by Design (GDPR Article 25)
Privacy must be architected into your system from day one—not bolted on later. This includes:
- Data minimization (collect only what you need)
- Purpose limitation (use data only for stated purposes)
- Storage limitation (delete after purpose is fulfilled)
- Security by design (encryption, access controls, audit logs)

### Compliance Timeline
- **Immediate** (Week 1): Determine which laws apply, conduct data audit
- **Short-term** (Month 1): Implement consent management, update privacy policy
- **Medium-term** (Month 2-3): Build data subject rights infrastructure (access, deletion, portability)
- **Ongoing**: Monitor vendor compliance, handle breach notifications, audit access logs

---

## When These Laws Apply: Decision Matrix

Use this decision tree to determine your compliance obligations:

```
START: Do you have users in the EU/EEA?
├─ YES → GDPR APPLIES (regardless of your location)
└─ NO → Continue to CCPA check

Does your company have California users AND meet at least one threshold?
├─ Annual revenue > $25M? → CCPA/CPRA APPLIES
├─ Personal information of 100K+ California consumers? → CCPA/CPRA APPLIES
├─ Derive 50%+ revenue from selling consumer data? → CCPA/CPRA APPLIES
└─ NO to all → Continue to other regulations check

Are you handling children's data (under 13 in US, under 16 in EU)?
├─ YES → COPPA (US) and GDPR Article 8 (EU) apply additionally
└─ NO → Continue

Other jurisdictions:
├─ Canada: PIPEDA applies if handling Canadian data
├─ Brazil: LGPD applies if handling Brazilian data
├─ UK: UK GDPR applies (similar to EU GDPR)
├─ Australia: Privacy Act applies if handling Australian data
└─ When in doubt, implement GDPR (strictest standard, covers most others)
```

### Practical Trigger Examples

| Scenario | GDPR? | CCPA? | Action |
|----------|-------|-------|--------|
| B2B SaaS, EU customers only | Yes | No | Implement GDPR fully |
| US-only SaaS, <$25M revenue | No | No | Basic privacy best practices |
| VC-funded startup, 50K users in California | No | Yes | Implement CCPA/CPRA |
| Global e-commerce, EU + CA users | Yes | Yes | Implement GDPR (covers both) |
| Email service, UK/EU only | Yes | No | Implement UK GDPR + EU GDPR |

---

## Data Residency Requirements

### GDPR Data Residency Rules

The EU restricts where personal data can be stored and processed:

#### Rule 1: EU/EEA Border
- **Personal data of EU residents must be processed and stored in EU/EEA** (or countries with "adequacy decisions")
- EU/EEA includes: All EU member states + Iceland, Liechtenstein, Norway, Switzerland
- Adequacy countries: UK, Israel, South Korea, Japan, Canada (conditional)

#### Rule 2: International Transfers (US/Other Regions)
If you must transfer data to the US or other non-adequate countries:

**Pre-transfer requirements:**
1. Execute Standard Contractual Clauses (SCCs) with your processor
2. Conduct a **Transfer Impact Assessment (TIA)** evaluating:
   - Local government surveillance laws
   - Ability of local government to compel disclosure
   - Effectiveness of security measures
   - Alternative safeguards available
3. Address identified risks (e.g., encrypt data, minimize transfer, restrict US access)

**Post-Schrems II (European Court ruling):**
- SCCs alone are NOT sufficient for US transfers
- Must supplement with additional safeguards
- If inadequate safeguards identified, transfer may be prohibited
- Document your risk assessment (Article 30 records)

#### Rule 3: Cloud Provider Selection for GDPR
When selecting cloud providers, ensure:

| Provider | EU Regions Available | Data Residency Controls | GDPR DPA | Notes |
|----------|----------------------|------------------------|----------|-------|
| **AWS** | 6 EU regions (Frankfurt, Ireland, Paris, Stockholm, Milan, Spain) | Customer controls region selection | Yes | Most mature GDPR support; EU Data Protection Impact Assessment available |
| **Google Cloud** | 3 EU regions (Frankfurt, Belgium, Netherlands) | Customer controls region selection | Yes | Some services (Analytics, Ads) problematic for GDPR |
| **Microsoft Azure** | 6 EU regions | Customer controls; EU Data Boundary option | Yes | EU Data Boundary: data/processing stays in EU even for Microsoft staff |
| **Vercel** | EU edge locations (Dublin, Frankfurt, etc.) | Set project region to EU | Yes | Good for Next.js apps; ensures edge cache in EU |
| **Supabase** | EU regions available | Select region at project creation | Yes | Postgres in EU region only; all backups stay in region |
| **Neon** | EU regions available | Region selection at branch creation | Yes | Auto-scaling Postgres; EU region has data residency guarantees |
| **Cloudflare** | Global (with EU specifics) | Data localization suite; GDPR-specific features | Yes | Can store personal data in EU only via Data Localization Suite |
| **Stripe** | EU processing available | Default EU processing for EU users; no US transfer | Yes | Automatically routes to EU data centers for EU users |
| **Postmark** | EU regions available | Select EU region for account | Yes | Email service; EU region = all data stays in EU |
| **Resend** | EU regions available | Region selection available | Yes | Email service; EU-friendly; smaller but growing |

#### Recommended EU-Safe Architecture
```
├─ Database: Supabase (eu-central-1 Frankfurt) or Neon (EU region)
├─ Hosting: Vercel EU Edge or Cloudflare Pages EU
├─ Auth: Clerk (EU region) or Auth0 (EU tenant)
├─ Email: Postmark EU or Resend
├─ Analytics: Plausible Analytics (EU-based, no tracking cookies)
├─ Storage: AWS S3 Frankfurt or Cloudflare R2 EU
└─ CDN: Cloudflare (with Data Localization) or AWS CloudFront EU
```

#### Practical Data Residency Checklist
- [ ] All personal data encrypted in transit (TLS 1.2+) and at rest
- [ ] Cloud provider is ISO 27001 and SOC 2 Type II certified
- [ ] Backups stored in same region as primary data (or EU region minimum)
- [ ] No automatic replication to US or non-adequate countries
- [ ] Data processing agreements (DPA) signed with all processors
- [ ] Transfer Impact Assessment completed and documented
- [ ] Right to audit data location confirmed in contract
- [ ] Incident response plan includes data residency verification

---

## Privacy-Compliant Tech Stack

### Minimum Viable Privacy Stack (MVP)

This is the bare minimum to be legally compliant with GDPR/CCPA without unnecessary complexity:

```
┌─ Frontend Analytics (NO tracking cookies)
│  └─ Plausible Analytics ($9/month) or Umami (self-hosted, $0)
│
├─ Consent/Cookies (Cookie-First Approach)
│  └─ No banner needed if you use only essential cookies
│  └─ If needed: Cookie-compliance in code, not third-party tool
│
├─ Email Service (GDPR Compliant)
│  ├─ Resend ($0-150/month, EU hosting)
│  └─ Postmark ($10+/month, EU server available)
│
├─ Authentication (GDPR Built-In)
│  ├─ Clerk (free tier, EU hosting)
│  └─ Auth0 (free tier, EU tenant available)
│
├─ Database (EU Data Residency)
│  ├─ Supabase (free tier, eu-central-1 Frankfurt)
│  ├─ Neon (free tier, EU regions)
│  └─ PlanetScale (Scaler plan $39/mo, EU regions — free tier removed 2024)
│
├─ Hosting (EU Edge)
│  ├─ Vercel (free tier, EU edge)
│  └─ Netlify (free tier, EU available)
│
└─ Privacy Dashboard (Built-in)
   └─ Data access/deletion/portability endpoints (code it yourself, ~200 lines)
```

**Total Monthly Cost for Compliance:** $0-20 (can be fully free with self-hosting and open-source)

### Analytics: Google Analytics Alternatives

**Problem:** Google Analytics is problematic for GDPR:
- Sets third-party cookies without explicit consent
- Transfers data to US servers without adequate safeguards
- EDPB opinion 05/2022: GA likely GDPR non-compliant
- Austrian DPA, French CNIL ruled GA transfers illegal
- Legal risk even with consent (due to Schrems II)

**GDPR-Compliant Alternatives:**

| Tool | Type | Cookies | GDPR Status | Cost | Self-Host | Setup Difficulty |
|------|------|---------|------------|------|-----------|-----------------|
| **Plausible** | Privacy-first | Zero cookies | Compliant, EU-based | $9/mo | No | Very Easy |
| **Umami** | Privacy-first | Optional | Fully compliant | $0 (self) | Yes | Easy |
| **Fathom** | Privacy-first | Zero cookies | Compliant | $14/mo | No | Very Easy |
| **PostHog** | Product analytics | Configurable | EU hosting available | Free-$450/mo | Yes | Medium |
| **Simple Analytics** | Privacy-first | Zero cookies | Compliant, EU-based | $9/mo | No | Very Easy |
| **Pirsch** | Privacy-first | Zero cookies | Compliant, EU-based | $5/mo | No | Very Easy |

**Recommendation for Most Startups:** Plausible ($9/mo) - no cookies, EU-based, instant GDPR compliance, beautiful UI.

**Recommendation for Cost-Conscious:** Umami (self-hosted free) - full control, own your data, no vendor lock-in.

### Email Service Compliance

| Service | GDPR Status | EU Region | DPA Available | Cost | Notes |
|---------|------------|-----------|---------------|------|-------|
| **Resend** | Compliant | Ireland | Yes | $0-150/mo | Modern API, great DX, growing features |
| **Postmark** | Compliant | EU available | Yes | $10/mo | Reliability-focused, US-based but EU servers |
| **SendGrid** | Conditional | EU available | Yes | $0-300/mo | Must configure for GDPR; DPA available |
| **Mailgun** | Conditional | EU available | Yes | $0-300/mo | Good API, ensure EU endpoint used |
| **Mailchimp** | Conditional | EU available | Yes | Free | Larger feature set, requires DPA |
| **AWS SES** | Conditional | Multiple EU | Yes | $0.10 per email | Most cost-effective for volume; requires DPA |

**Avoid:** Mailchimp for EU users without proper DPA and consent; SendGrid without configuring for GDPR.

### Authentication Compliance

| Service | GDPR Ready | EU Hosting | DPA | Free Tier | Notes |
|---------|-----------|-----------|-----|-----------|-------|
| **Clerk** | Yes | Yes | Yes | 10K MAU free | Modern, great DX, GDPR by design |
| **Auth0** | Yes | Yes (EU tenant) | Yes | 7K free users/mo | Flexible, comprehensive, steeper learning curve |
| **Supabase Auth** | Yes | Yes (EU region) | Yes | 50K free users | Integrated with Postgres, simpler than Auth0 |
| **Firebase Auth** | Problematic | US-based | Conditional | 50K users free | Google data practices raise GDPR concerns |

**Recommendation:** Clerk (great DX) or Supabase Auth (integrated with DB) for best GDPR compliance without complexity.

---

## Consent Management Architecture

### When You Need Cookie Consent (And When You Don't)

```
DO YOU HAVE TRACKING COOKIES?
├─ NO (only httpOnly, sameSite essential) → NO BANNER NEEDED
│  └─ You can track usage with cookieless analytics (Plausible, Umami)
│  └─ No GDPR/ePrivacy violation
│
└─ YES (Google Analytics, Facebook Pixel, LinkedIn Ads, etc.) → CONSENT REQUIRED
   ├─ Consent banner before setting cookies
   ├─ Pre-checked boxes invalid (GDPR requirement: active opt-in)
   ├─ Consent preference stored in cookies (httpOnly, 12-month expiry)
   └─ Consent withdrawal must be as easy as consent (right to withdraw)
```

### Consent Management Platforms (CMPs)

| CMP | Cost | GDPR Ready | Implementation | Notes |
|-----|------|-----------|-----------------|-------|
| **Cookiebot** | $19+/mo | Yes | Script tag | CMP leader; trusted by many enterprises |
| **OneTrust** | Custom | Yes | Script tag | Enterprise-grade; very expensive |
| **Osano** | Custom | Yes | Script tag | Legal-focused; helps with legal docs |
| **iubenda** | Free-$80/mo | Yes | Script tag | Good for SMBs; privacy policy generator |
| **Termly** | Free-$300/mo | Yes | Script tag | All-in-one (policy + consent + DSR) |
| **Custom Implementation** | $0 | Yes | React component | Build your own (200 lines); full control |

### Consent Architecture Pattern

```
User Visits Site
    ↓
Check localStorage.getItem('gdpr_consent')
    ├─ FOUND: Apply stored preferences (analytics enabled/disabled)
    ├─ NOT FOUND: Show consent banner
    │   ↓
    │   User selects preferences
    │   ↓
    │   Store consent object in httpOnly cookie + localStorage:
    │   {
    │     "analytics": true,
    │     "marketing": false,
    │     "timestamp": "2026-03-02T10:00:00Z",
    │     "version": "1"
    │   }
    │   ↓
    │   Load analytics script (if analytics: true)
    │
    └─ Load site with preferred tracking
```

### Consent Storage & Withdrawal

**Storage (Secure):**
```javascript
// Set consent in httpOnly cookie (server-side)
// JavaScript cannot access; immune to XSS stealing
res.cookie('gdpr_consent', JSON.stringify(consentObj), {
  httpOnly: true,      // JavaScript cannot access
  sameSite: 'Strict',  // CSRF protection
  secure: true,        // HTTPS only
  maxAge: 12 * 30 * 24 * 60 * 60 * 1000  // 12 months
});

// Also store in localStorage for quick client checks
localStorage.setItem('gdpr_consent_status', 'given');
```

**Withdrawal (Easy):**
- Prominent "Manage Cookies" link in footer
- User clicks → shows current preferences
- Can change/withdraw at any time
- Withdrawal effective immediately
- No re-consent required until 12 months expires

### Consent Compliance Checklist
- [ ] Consent banner appears BEFORE cookies are set
- [ ] Consent is specific (separate toggles: analytics, marketing, functional)
- [ ] "Accept All" and "Reject All" buttons equally prominent
- [ ] No pre-checked boxes (affirmative action required)
- [ ] Consent withdrawal available in footer ("Manage Cookies")
- [ ] Consent version tracked (to re-request on policy changes)
- [ ] Consent withdrawal affects only future tracking (not retroactive)
- [ ] Consent records kept for audit (what user consented to, when)

---

## Cookie-Free Architecture: Zero Consent Banner Approach

The easiest GDPR path: **Don't use tracking cookies at all.**

### The Cookie-Free Stack

| Component | Traditional | Cookie-Free |
|-----------|------------|------------|
| **Analytics** | Google Analytics (tracking cookies) | Plausible/Umami (no cookies) |
| **Session** | Session cookie | httpOnly cookie (essential) |
| **Conversion Tracking** | Facebook Pixel (cookies) | Server-side API call |
| **Ads Attribution** | Third-party cookies | First-party data (email, CRM) |
| **User Preferences** | Cookie | localStorage |
| **Consent** | Cookie consent banner | Not needed! |

### Implementation

```javascript
// ✅ ALLOWED: No banner needed
// Session management (essential cookie)
res.cookie('session', sessionToken, {
  httpOnly: true,
  sameSite: 'Strict',
  secure: true
});

// ✅ ALLOWED: No banner needed
// Analytics without cookies
import PlausibleProvider from 'next-plausible';
<PlausibleProvider domain="example.com">
  {children}
</PlausibleProvider>

// ❌ NOT ALLOWED: Requires consent banner
// (Don't use these)
<script async src="https://www.googletagmanager.com/gtag/js?id=..."></script>
<img src="https://facebook.com/tr?id=..." /> {/* Facebook Pixel */}
<script src="https://connect.facebook.net/..."></script> {/* FB SDK */}
```

### Benefits of Cookie-Free Architecture
- **No consent banner** (better UX, less friction)
- **Better privacy** (users not tracked across sites)
- **Higher conversion** (less consent banner opt-outs)
- **Simpler compliance** (fewer GDPR headaches)
- **Faster page load** (fewer third-party scripts)
- **Better analytics** (Plausible shows what matters)

### Conversion Tracking Without Third-Party Cookies

```
Traditional Flow:
Click Ad → Landing Page → User Action → Facebook Pixel reads third-party cookies
                                        → Matches to original ad click

Cookie-Free Flow:
Click Ad → Add ?utm_source=fb param → Landing Page → User Action →
→ Server logs conversion with utm_source param →
→ API call to Facebook Conversions API (no cookies) → Facebook tracks conversion
```

**Tools for Server-Side Conversion Tracking:**
- Facebook Conversions API
- Google Measurement Protocol
- LinkedIn Conversion Tracking API
- TikTok Pixel (server-side)

---

## Data Subject Rights Implementation

GDPR and CCPA both require you to provide users mechanisms to exercise their rights. This is both a legal requirement and should be user-friendly.

### Rights Required

| Right | GDPR | CCPA | Implementation | Deadline |
|-------|------|------|-----------------|----------|
| **Access** | Yes (Art. 15) | Yes (1798.100) | Export all user data | 30 days |
| **Deletion** | Yes (Art. 17) | Yes (1798.105) | Delete user records | 30 days |
| **Portability** | Yes (Art. 20) | No, but similar | Export structured data | 30 days |
| **Rectification** | Yes (Art. 16) | No | Edit user info | 30 days |
| **Restrict Processing** | Yes (Art. 18) | No | Disable some processing | 30 days |
| **Opt-Out (Data Sales)** | N/A | Yes (1798.120) | Disable data sales | 30 days |

### Architecture Pattern for Data Subject Rights (DSR)

```
┌─────────────────────────────────────────────────────────────┐
│                    USER DASHBOARD                            │
│  "My Data" tab shows all data we have about them            │
│  "Data Rights" section with buttons:                        │
│  - [Download My Data] (Right to Access/Portability)        │
│  - [Change My Info] (Right to Rectification)               │
│  - [Delete My Account] (Right to Erasure)                  │
│  - [Stop Selling Data] (CCPA-specific)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
                   DSR REQUEST API
                 POST /api/dsr/request
        { type: 'access' | 'delete' | 'portability',
          userId: '...',
          email: '...@example.com' }
                            ↓
                      REQUEST QUEUE
               Store in database: id, type, status
                            ↓
                   ASYNC PROCESSING
          (Process request in background worker)
                            ↓
        ┌────────────────────────────────────┐
        │    RIGHT TO ACCESS/PORTABILITY    │
        │  Export user data to JSON/CSV     │
        │  Include: profile, posts, files,  │
        │  preferences, activity log        │
        └────────────────────────────────────┘
                            ↓
        ┌────────────────────────────────────┐
        │       RIGHT TO ERASURE             │
        │  1. Cascade delete user records    │
        │  2. Anonymous old backups          │
        │  3. Notify third parties           │
        │  4. Check audit logs               │
        └────────────────────────────────────┘
                            ↓
                    VERIFICATION
            Confirm deletion completed;
          Verify no residual data remains
                            ↓
                    NOTIFICATION
            Email user: "Request completed"
         Attach ZIP of exported data (if access)
```

### Implementation Example: Right to Access

```javascript
// POST /api/dsr/access
async function handleAccessRequest(req, res) {
  const { userId, email } = req.body;

  // Verify user identity (re-authenticate)
  const user = await verifyUser(userId, email);

  // Collect all user data
  const userData = {
    profile: await db.users.findOne({ id: userId }),
    posts: await db.posts.find({ userId }),
    comments: await db.comments.find({ userId }),
    files: await db.files.find({ userId }),
    activityLog: await db.activityLog.find({ userId }),
    preferences: await db.preferences.findOne({ userId }),
    loginHistory: await db.loginHistory.find({ userId }),
    payments: await db.payments.find({ userId })
  };

  // Generate JSON/CSV export
  const zip = new JSZip();
  zip.file('profile.json', JSON.stringify(userData.profile, null, 2));
  zip.file('posts.json', JSON.stringify(userData.posts, null, 2));
  // ... add other files

  // Store for retrieval
  const downloadId = crypto.randomUUID();
  await db.dsr_exports.insert({
    id: downloadId,
    userId,
    type: 'access',
    expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    createdAt: new Date()
  });

  // Email user download link
  await emailService.send({
    to: email,
    subject: 'Your Data Export is Ready',
    template: 'dsr-access',
    downloadLink: `${baseUrl}/dsr/download/${downloadId}`
  });

  res.json({ status: 'processing', dsr_id: downloadId });
}
```

### Implementation Example: Right to Erasure

```javascript
// POST /api/dsr/delete
async function handleDeletionRequest(req, res) {
  const { userId, email, confirmation } = req.body;

  // Verify user identity and confirmation
  if (confirmation !== 'DELETE MY ACCOUNT') {
    return res.status(400).json({ error: 'Invalid confirmation' });
  }

  // Start deletion process
  const dsrId = crypto.randomUUID();

  // Queue for async processing
  await jobQueue.add('user-deletion', {
    userId,
    email,
    dsrId,
    timestamp: new Date()
  });

  res.json({ status: 'deletion_queued', dsr_id: dsrId });
}

// Background worker
async function processUserDeletion(job) {
  const { userId, email, dsrId } = job.data;

  try {
    // 1. Delete primary records
    await db.users.deleteOne({ id: userId });
    await db.posts.deleteMany({ userId });
    await db.comments.deleteMany({ userId });
    await db.files.deleteMany({ userId });
    await db.preferences.deleteOne({ userId });

    // 2. Handle backups (anonymize old backup snapshots)
    await db.backups.updateMany(
      { contains_user: userId },
      { $set: { anonymized: true } }
    );

    // 3. Notify third-party processors
    if (stripeCustomerId) {
      await stripe.customers.del(stripeCustomerId);
    }

    // 4. Audit trail (do NOT delete audit logs - needed for compliance)
    await db.auditLog.insert({
      event: 'user_deleted',
      userId: 'ANONYMIZED',
      timestamp: new Date(),
      dsr_id: dsrId,
      reason: 'user_requested_deletion'
    });

    // 5. Verify deletion
    const remaining = await db.users.findOne({ id: userId });
    if (remaining) {
      throw new Error('Deletion verification failed');
    }

    // 6. Notify user
    await emailService.send({
      to: email,
      subject: 'Your Account Has Been Deleted',
      template: 'dsr-deletion-confirmed'
    });

  } catch (error) {
    // Log failure and retry
    await db.dsr_requests.updateOne(
      { id: dsrId },
      { status: 'failed', error: error.message }
    );
  }
}
```

### DSR Compliance Checklist
- [ ] User dashboard provides access to all their personal data
- [ ] Download/export feature generates JSON or CSV
- [ ] Data deletion is truly permanent (not soft-deleted)
- [ ] Deletion includes cascade (posts, files, comments, etc.)
- [ ] Backups are handled (old snapshots anonymized)
- [ ] Third-party data notified of deletion (Stripe, payment providers)
- [ ] Audit trail preserved (for compliance, not connected to user)
- [ ] All requests logged with timestamps
- [ ] Deadline tracked (30 days for GDPR, 45 days for CCPA)
- [ ] User notified when request completed

---

## CCPA/CPRA Specific Requirements

CCPA (California Consumer Privacy Act, 2020) and CPRA (California Privacy Rights Act, 2023) add California-specific requirements on top of general privacy.

### When CCPA/CPRA Applies

You must comply if you're a for-profit business serving California residents AND meet at least ONE:
- Annual revenue exceeding $25 million
- Collect personal information from 100,000 or more California consumers or households
- Derive 50% or more of annual revenue from selling consumers' personal information

### CCPA/CPRA Legal Obligations

| Requirement | Implementation | GDPR Equivalent? | Deadline |
|-------------|-------------------|-----------------|----------|
| **Privacy Policy** | Disclose what data collected, purpose, user rights | Art. 13-14 | At collection |
| **"Do Not Sell"** | Link/button "Do Not Sell My Personal Information" | No | Visible on homepage |
| **Opt-Out Mechanism** | Allow users to opt-out of data sales | No | Must function within 45 days |
| **Data Requests** | Process access/deletion/portability | Art. 15, 17, 20 | Within 45 days |
| **Sensitive Data** | Additional protections for: SSN, precise geolocation, etc. | Similar to Art. 9 | By default |
| **Annual Audit** | Audit who accesses personal data | Art. 30 (Records) | Annual |

### CCPA Categories of Personal Information

CCPA defines broad categories you must track:

```
A. Identifiers
   ├─ Name, postal address, email, phone, SSN, passport
   ├─ IP address, cookies, pixel tags, device identifiers
   └─ Commercial information (purchase history)

B. Biometric Information
   ├─ Fingerprints, face recognition, voice prints
   └─ Used for identification/verification

C. Commercial Activity
   ├─ Products/services purchased, purchase history
   ├─ Purchase amounts, transaction dates
   └─ Tendencies to purchase products/services

D. Biometric Information (Inferences)
   ├─ Inferences from data to predict preferences
   ├─ Inferences about interests, behaviors, attitudes
   └─ Inferences about income, education level

E. Geolocation Data
   ├─ Precise location (GPS, triangulation)
   └─ Approximate location (IP-based)

F. Sensory Information
   ├─ Audio/video recordings
   ├─ Photography (not faces in publicly available records)
   └─ Thermal imagery

G. Professional Information
   ├─ Current/past job history, performance
   ├─ Skills, qualifications, salary information
   └─ Professional experience

H. Education Information
   ├─ Enrollment status, grades, diplomas
   ├─ Transcripts, disciplinary records
   └─ Special education records

I. Protected Classification
   ├─ Race, ethnicity, national origin
   ├─ Religion, sex, gender identity, age
   └─ Disability, military status, union membership
```

### "Do Not Sell My Personal Information" Implementation

```html
<!-- Homepage Footer -->
<footer>
  <a href="/privacy">Privacy Policy</a>
  <a href="/data-request">Download My Data</a>
  <a href="/delete-account">Delete My Account</a>
  <a href="/opt-out-sales">Do Not Sell My Personal Information</a>
</footer>

<!-- /opt-out-sales endpoint -->
// POST /api/ccpa/opt-out-sales
async function optOutDataSales(req, res) {
  const { userId } = req.body;

  // Verify identity
  const user = await getAndVerifyUser(userId);

  // Set opt-out flag
  await db.users.updateOne(
    { id: userId },
    {
      ccpa_opt_out_sales: true,
      ccpa_opt_out_timestamp: new Date()
    }
  );

  // Stop all data sales/sharing for this user
  // - Don't share with brokers
  // - Don't sell to third parties
  // - Clear from audience segments used for ads

  res.json({ status: 'opted_out', effective_date: new Date() });
}
```

### CPRA Enhancements (vs CCPA)

CPRA (2023) added:
- **Right to Correct:** Ability to correct inaccurate data (similar to GDPR Art. 16)
- **Right to Delete:** Enhanced (similar to GDPR Art. 17)
- **Right to Opt-Out:** For sales, sharing, and profiling (better than CCPA)
- **Sensitive Personal Information:** Higher protection tier (biometrics, SSN, precise geolocation, health, sex life, citizenship status)
- **CPRA Enforcement:** California Privacy Protection Agency (new regulator)
- **Increased Fines:** Up to $10,000 per intentional violation (vs $7,500 in CCPA)

### CCPA/CPRA Privacy Policy Additions

Your privacy policy must explicitly disclose:

```markdown
## California Consumer Privacy Notice

### Personal Information Collected
We collect the following categories of personal information:
- Identifiers (name, email, IP address)
- Commercial information (purchase history, transaction history)
- Internet activity (browsing history, interactions with our site)

### Purposes for Collection
We collect personal information for:
- Providing services you request
- Improving our products
- Marketing communications
- Fraud prevention
- Legal compliance

### Sources of Information
We collect information from:
- You directly (account signup, forms)
- Automatically (cookies, server logs)
- Third parties (payment providers, analytics)

### Do Not Sell My Personal Information
We do not sell personal information as defined by CCPA.
(OR: If you do: "Users can opt-out [here]")

### Data Retention
We retain personal information for:
- As long as account is active, plus 2 years
- Or as required by law

### Consumer Rights
California consumers have rights to:
- Access: Download your personal information
- Delete: Request deletion of personal information
- Correct: Correct inaccurate information (CPRA)
- Opt-Out: Opt-out of data sales (if applicable)

To exercise rights:
- Email: privacy@company.com
- Submit form: /data-request
```

### CCPA/CPRA Compliance Checklist
- [ ] Privacy policy updated with CCPA sections
- [ ] "Do Not Sell" link on homepage (if you sell data)
- [ ] Data request mechanism handles: access, delete, correct
- [ ] Opt-out mechanism for data sales (if applicable)
- [ ] Personal information categories documented
- [ ] Data retention periods defined
- [ ] Annual audit of data sharing completed
- [ ] Requests processed within 45 days
- [ ] User verification (prevent unauthorized deletion)
- [ ] Tracking of requests and response times

---

## Data Processing Agreements (DPA)

A Data Processing Agreement is a contract required by GDPR between Data Controller (you) and Data Processor (vendors like Stripe, SendGrid, etc.). CCPA doesn't require this but it's best practice.

### When You Need a DPA

```
Use Vendor ↓
├─ Vendor accesses personal data? (Yes/No)
│  ├─ YES → Need a DPA
│  └─ NO → No DPA needed
│
└─ DPA includes what language?
   ├─ Article 28 (GDPR processor obligations)
   ├─ SCCs (Standard Contractual Clauses, for international transfers)
   ├─ Data Protection Impact Assessment (DPIA) commitment
   └─ Sub-processor notification and approval
```

### List of Vendors That Provide DPAs

| Vendor Category | With DPA | Notes |
|-----------------|----------|-------|
| **Email** | Resend, Postmark, SendGrid, Mailgun, AWS SES | All major providers have DPAs |
| **Database** | Supabase, Neon, PlanetScale, AWS RDS | All provide DPAs |
| **Auth** | Clerk, Auth0, Supabase Auth | All provide DPAs |
| **Analytics** | Plausible, Fathom, Umami (self-hosted) | Plausible has DPA; Fathom has DPA |
| **Payment** | Stripe, Paddle, Lemonsqueezy | All provide DPAs |
| **Cloud Storage** | AWS S3, Cloudflare R2, Google Cloud Storage | All provide DPAs |
| **Hosting** | Vercel, Netlify, AWS, Google Cloud | All provide DPAs |
| **❌ No DPA** | Google Analytics, Facebook Pixel, LinkedIn Ads | These are problematic for GDPR |

### How to Request a DPA

**For cloud providers (easy):**
1. Log into vendor dashboard
2. Find "Security" or "Compliance" section
3. Look for "Data Processing Agreement" or "DPA"
4. Download/accept DPA (usually auto-accepted)
5. Confirm in writing with support if needed

**For smaller vendors (harder):**
1. Email vendor: "Can you provide a GDPR Data Processing Agreement?"
2. Provide template (use EDPB template or vendor's template)
3. Negotiate terms (usually takes 1-2 weeks)
4. Sign and keep on file

**Template DPA sections to require:**
```
1. Controller and Processor identification
2. Nature and purpose of processing
3. Types of personal data processed
4. Categories of data subjects
5. Duration and scope of processing
6. Processor obligations:
   - Process only on instructions
   - Ensure confidentiality of staff
   - Implement security measures
   - Assist with data subject rights
   - Notify of data breaches
7. Sub-processor policy (require approval)
8. EU Standard Contractual Clauses (if transferring to US/non-EU)
9. Data deletion/return after termination
10. Audit rights and cooperation
```

### Building Your DPA Record (Article 30 Register)

GDPR Article 30 requires you document all processing:

```markdown
# Article 30 Register of Processing Activities

## 1. User Account Database
- **Processor:** Supabase (based in Ireland)
- **Personal Data:** Names, emails, hashed passwords, profile data
- **Categories:** Account holders
- **Duration:** Until account deletion
- **Purpose:** Provide service, authentication
- **Security:** Encryption at rest, TLS in transit
- **DPA:** Yes, signed 2024-01-15
- **Sub-processors:** AWS (database host), Vercel (backup)

## 2. Email Campaigns
- **Processor:** Postmark (based in US, EU servers)
- **Personal Data:** Email addresses, open/click events
- **Categories:** Users who opted in to emails
- **Duration:** 2 years after opt-out
- **Purpose:** Marketing communications
- **Security:** Encrypted, DKIM/SPF configured
- **DPA:** Yes, signed 2024-01-15
- **Sub-processors:** AWS (email delivery), Mailgun (API)

## 3. Analytics
- **Processor:** Plausible Analytics (based in EU)
- **Personal Data:** Page views, session events (anonymized)
- **Categories:** All visitors
- **Duration:** Aggregated, 90-day retention
- **Purpose:** Understand usage patterns
- **Security:** No cookies, local storage only
- **DPA:** Yes, EU-based provider
- **Sub-processors:** None (self-hosted infrastructure)

## 4. Payment Processing
- **Processor:** Stripe (based in US)
- **Personal Data:** Email, billing address, payment method (last 4 digits)
- **Categories:** Paying customers
- **Duration:** For transaction + 7 years (accounting)
- **Purpose:** Payment processing, fraud prevention
- **Security:** PCI DSS compliant, tokenized payments
- **DPA:** Yes, signed 2024-01-15
- **Transfer basis:** SCCs + TIA completed
```

---

## Common Privacy Mistakes (And How to Avoid Them)

### Mistake #1: Using Google Analytics in EU Without Proper Safeguards
**Risk:** GDPR violation, €20M fine or 4% revenue

**Why it's problematic:**
- Sets third-party tracking cookies without valid consent
- Transfers data to US servers (Schrems II implications)
- EDPB, French CNIL, Austrian DPA all ruled GA non-compliant
- "Legitimate interest" is not sufficient for tracking cookies

**Fix:**
- Replace with Plausible, Fathom, or Umami
- Cost: $9/month vs. free GA
- Compliance: Automatic, no consent banner needed
- Better UX: Same insights, no cookie banner friction

### Mistake #2: No Right to Deletion
**Risk:** GDPR Article 17 violation, €10M+ fines

**Why it's problematic:**
- Users request "right to be forgotten"
- You have no deletion mechanism
- Data stays in database forever
- User has legal recourse (complaint to DPA)

**Fix:**
- Implement right to deletion in dashboard (30-line feature)
- Delete cascading records (posts, comments, files)
- Handle backups (anonymize old snapshots)
- Document deletion in audit log

### Mistake #3: Storing Unnecessary Personal Data
**Risk:** GDPR Article 5 (Data Minimization) violation

**Why it's problematic:**
- Store phone numbers but never use them
- Keep address after customer moves away
- Retain payment methods after cancellation
- Audit discovers "we don't need this data"

**Fix:**
- Conduct data audit: "What data do we actually use?"
- Delete what you don't need (no risk to delete)
- Document retention period for each field
- Auto-delete when retention expires (cleanup jobs)

### Mistake #4: Pre-Checked Consent Boxes
**Risk:** GDPR Article 7 (Consent) violation, €5M+ fines

**Why it's problematic:**
- Consent must be explicit (affirmative action)
- Pre-checked "I agree to marketing emails" is invalid
- User must actively check the box themselves
- Courts have ruled pre-checked invalid in many cases

**Fix:**
```javascript
// ❌ WRONG: Pre-checked consent
<label>
  <input type="checkbox" name="marketing" defaultChecked />
  Email me about new features
</label>

// ✅ CORRECT: Empty checkbox (user must check)
<label>
  <input type="checkbox" name="marketing" defaultChecked={false} />
  Email me about new features (optional)
</label>
```

### Mistake #5: No Data Processing Agreement
**Risk:** GDPR Article 28 violation, €10M+ fines

**Why it's problematic:**
- Vendor processes personal data without DPA
- You have no legal basis to share data
- Regulator fines you (and vendor)
- In breach even if vendor is trustworthy

**Fix:**
- Check vendor website for "DPA" or "Security" section
- Download DPA (usually auto-accepted)
- Sign and keep on file
- Audit annually (include in DPA tracking sheet)

### Mistake #6: Ignoring Data Breach Notification (72-Hour Rule)
**Risk:** GDPR Article 33 violation, €10M+ fines

**Why it's problematic:**
- Database compromised on Day 1
- You discover on Day 5
- You have 72 hours from discovery (Day 5 → Day 8)
- But you wait 2 weeks to notify
- Regulator fines you for late notification

**Fix:**
- Have incident response plan (who calls who)
- Monitor for breaches (uptime monitoring, log alerts)
- Prepare breach notification template
- Notify regulator AND users within 72 hours
- Document breach response (for compliance)

### Mistake #7: Not Appointing a Data Protection Officer (DPO)
**Risk:** GDPR Article 37 violation (if required)

**Why it's problematic:**
- You're required to appoint DPO but haven't
- DPO is required if you: process large amounts of personal data, are a public authority, or have data processing as core activity
- Regulator fines you if DPO is missing

**Fix:**
- Assess if DPO is required (usually only for large companies, nonprofits, public sector)
- If required: appoint someone as DPO (internal or external service)
- If not required: no action needed, but document assessment

### Mistake #8: Transferring EU Data to US Without Safeguards
**Risk:** GDPR Chapter 5 violation, criminal penalties possible

**Why it's problematic:**
- Schrems II ruling: Transfers must have TIA (Transfer Impact Assessment)
- SCCs alone insufficient (must supplement with safeguards)
- If US law allows surveillance, you can't transfer

**Fix:**
- Keep EU data in EU (simplest)
- If must transfer: EU Cloud Providers first (Scaleway, OVHcloud)
- If using US provider: EU regions only (AWS Frankfurt)
- Document Transfer Impact Assessment

### Mistake #9: Cookie Consent Banner That Can't Be Declined
**Risk:** GDPR Article 21 violation

**Why it's problematic:**
```
❌ DARK PATTERN:
[Accept All]  [Settings]
↑
Only "Accept All" is prominent
"Reject All" requires 3 clicks
```

**Fix:**
```javascript
// ✅ CORRECT: Equal prominence
<button>Accept All</button>
<button>Reject All</button>
<button>Customize</button>
// All same color, same size, same location
```

### Mistake #10: No Privacy Policy or Outdated Policy
**Risk:** GDPR Article 13 violation, CCPA non-compliance

**Why it's problematic:**
- Users have right to know what you collect
- Privacy policy must be clear, accessible, up-to-date
- Outdated policy (mentions Google Analytics, data broker sharing) is misleading

**Fix:**
- Write privacy policy using template (Termly, iubenda)
- Update when: new processors, new data types, new purposes
- Review annually
- Make easily accessible (footer link, account settings)

---

## Decision Logic: Full Compliance Tree

Use this flowchart to determine exact compliance requirements:

```
┌─ START: Assess Data & Users
│
├─ Question 1: Do you have EU/EEA users?
│  ├─ YES → GDPR APPLIES
│  │  ├─ Data residency: EU/EEA only (or with SCCs)
│  │  ├─ Consent required for non-essential cookies
│  │  ├─ DPA required for vendors
│  │  ├─ Right to access/delete/portability mandatory
│  │  ├─ 30-day response deadline for DSR
│  │  ├─ 72-hour breach notification required
│  │  └─ Consider appointing DPO if large processor
│  │
│  └─ NO → Continue
│
├─ Question 2: Do you have California users?
│  └─ AND meet at least one threshold:
│     ├─ >$25M annual revenue
│     ├─ >100K California consumers
│     ├─ >50% revenue from selling consumer data
│     │
│     └─ YES to any → CCPA/CPRA APPLIES
│        ├─ "Do Not Sell" link on homepage
│        ├─ Opt-out mechanism for data sales
│        ├─ Privacy policy disclosure required
│        ├─ Right to access/delete/correct mandatory
│        ├─ 45-day response deadline for DSR
│        └─ Annual data sharing audit
│
│     └─ NO → Continue
│
├─ Question 3: Are you collecting children's data (under 13)?
│  ├─ YES → COPPA (US) applies
│  │  ├─ Parental consent required
│  │  ├─ No third-party tracking
│  │  ├─ Delete data upon request
│  │  └─ No behavioral profiling
│  │
│  └─ NO → Continue
│
├─ Question 4: Do you have users in other jurisdictions?
│  ├─ Canada → PIPEDA applies
│  ├─ Brazil → LGPD applies
│  ├─ UK → UK GDPR applies
│  ├─ Australia → Privacy Act applies
│  └─ When in doubt: Implement GDPR (strictest = covers most)
│
└─ Question 5: What's your compliance baseline?
   ├─ EU users → Implement GDPR fully
   ├─ Both EU + California → Implement GDPR (covers both)
   ├─ California only → Implement CCPA/CPRA
   └─ Neither → Implement privacy best practices anyway (laws expanding globally)

─────────────────────────────────────────

IMPLEMENTATION PRIORITY:
1. Privacy Policy (write/update)
2. Consent Mechanism (if using tracking cookies)
3. Data Subject Rights (access, delete, portability)
4. Vendor DPAs (collect from all processors)
5. Data Processing Register (Article 30)
6. Incident Response Plan (breach notification)
7. Privacy Audit (annual review)
```

---

## Enforcement & Fines: What Actually Happens

### GDPR Enforcement

**Who enforces:** Each EU country has a Data Protection Authority (DPA)
- Examples: CNIL (France), BfDI (Germany), ICO (UK), EDPB (coordination)

**How fines are calculated:**
```
Tier 1 (Lower violations):
- $0 - €10M
- Examples: Missing privacy policy, no consent mechanism
- Reality: Usually €50K-€500K for small/medium companies

Tier 2 (Serious violations):
- €10M - €20M OR 2% - 4% global revenue (whichever is higher)
- Examples: Illegal data transfers, no DPA, breach disclosure delay
- Reality: €1M - €15M+ for data transfers and systemic failures

FAMOUS FINES:
- Meta (Facebook): €1.2B (illegal data transfer to US) + €405M (tracking)
- Amazon: €746M (consent, data use)
- Google: €90M (lack of consent for tracking)
- TikTok: €345M (children data protection)
```

### CCPA/CPRA Enforcement

**Who enforces:** California Privacy Protection Agency (started 2023)

**How fines work:**
```
Per-Violation Fines:
- Unintentional violation: $100 - $2,500 per consumer
- Intentional violation: $2,500 - $7,500 per consumer (CCPA)
- CPRA: Up to $10,000 per intentional violation

Statutory damages:
- Data breach involving personal info: $100-$750 per consumer per incident
- Can sue directly (private right of action)

REALITY:
- Most enforcement is warnings first
- Fines escalate if violations continue after warning
- Not enforced as aggressively as GDPR (yet)
```

### How to Respond If Contacted by Regulator

1. **Email from regulator saying "complaint received":**
   - Do NOT ignore
   - Consult lawyer immediately
   - You have 30-60 days to respond with explanation
   - This is an investigation, not a fine yet

2. **Audit/Investigation:**
   - Regulator may request: technical logs, DPA contracts, consent records
   - Provide within deadline (typically 2 weeks-1 month)
   - Document your compliance efforts
   - Be honest; lying makes fines worse

3. **Settlement or Fine:**
   - Best case: Warning (you fix issue, no fine)
   - Likely case: Small fine ($1K-$50K) if you respond quickly
   - Worst case: Large fine if systemic violations found

**Key lesson:** Proactive compliance is 100x easier than reactive enforcement.

---

## Compliance Checklist (Monthly/Quarterly)

### Monthly
- [ ] Review new cookies/tracking added to site
- [ ] Monitor vendor DPA status (new processors?)
- [ ] Check data retention policies (are we deleting old data?)
- [ ] Review access logs (who accessed user data?)

### Quarterly
- [ ] Run privacy audit (what data are we storing?)
- [ ] Update vendor DPA list
- [ ] Review and respond to data subject rights requests
- [ ] Check for data breaches (logs, security alerts)

### Annually
- [ ] Update privacy policy (new processors, new purposes?)
- [ ] Conduct Transfer Impact Assessment (for US data transfers)
- [ ] Review children's data handling (if applicable)
- [ ] Certify CCPA compliance (annual audit)
- [ ] Renew DPAs with all vendors
- [ ] Update Article 30 Register

---

## Tools & Resources

### Privacy-as-a-Service Tools
- **Termly:** Privacy policy + cookie consent + DSR handling ($0-300/mo)
- **Osano:** Legal compliance platform ($custom)
- **OneTrust:** Enterprise compliance platform ($custom, expensive)
- **iubenda:** Cookie banner + privacy policy (€9-80/mo)

### Open Source Compliance
- **Plausible Analytics:** Cookie-free analytics (open source available)
- **Umami:** Self-hosted analytics ($0, full control)
- **OpenConsentManager:** DIY consent management

### Legal Resources
- **GDPR Text:** https://gdpr-info.eu/
- **EDPB Guidelines:** https://edpb.ec.europa.eu/our-work/our-work-tools/guidelines_en
- **CCPA Text:** https://oag.ca.gov/privacy/ccpa
- **CPRA Text:** https://cpra-info.ca.gov/

---

## Pricing Stability Note

<!-- PRICING_STABILITY: moderate | last_verified: 2026-03 | check_interval: 6_months -->

All vendor pricing and GDPR/CCPA law references in this guide were verified as of March 2026. Privacy regulations continue to evolve globally—expect new requirements every 12-18 months. Check regulatory updates quarterly.

---

## Related References
- [Compliance Provider Matrix](./38-compliance-provider-matrix.md) — GDPR/CCPA compliance across cloud providers
- [HIPAA Compliance Architecture Guide](./33-compliance-hipaa.md) — Healthcare compliance with international expansion
- [Internationalization (i18n) & Localization (l10n) Architecture](./54-internationalization-localization.md) — Regional data handling patterns
- [AI/ML Integration Tech Stack Research](./43-ai-ml-integration-tech-stack.md) — GDPR considerations for ML/AI systems
- [Multi-Tenancy Architecture Patterns for SaaS Applications](./56-multi-tenancy-architecture-saas.md) — Data isolation for international multi-tenant systems

---

## Summary: The Practical Playbook

**If you have EU users:**
1. Stop using Google Analytics → use Plausible ($9/mo)
2. Keep EU data in EU region (Supabase EU, AWS Frankfurt)
3. Implement data subject rights (30-line feature)
4. Collect DPAs from all vendors
5. Write privacy policy disclosing all processing
6. Done! You're GDPR-compliant

**If you have California users + >$25M revenue:**
1. Add "Do Not Sell" link to homepage
2. Implement opt-out mechanism (5-line feature)
3. Update privacy policy with CCPA disclosures
4. Process data requests within 45 days
5. Annual audit of data sharing
6. Done! You're CCPA-compliant

**If you have both EU + California users:**
- Implement GDPR (stricter standard)
- GDPR compliance covers ~90% of CCPA requirements
- Add CCPA-specific bits (Do Not Sell, opt-out)
- Done!

**Most important principle:** Privacy by Design. Build privacy in from day one, not as afterthought. It's cheaper, faster, and makes your product better (users trust you more).
