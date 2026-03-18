# PCI-DSS 4.0 Compliance Architecture Guide

## Executive Summary

PCI-DSS (Payment Card Industry Data Security Standard) is a mandatory compliance framework for any organization handling credit card data. Understanding scope reduction is the key to minimizing compliance burden.

### When Does PCI-DSS Apply?

You **MUST** comply with PCI-DSS if you:
- Accept, process, store, or transmit credit card data (CHD)
- Operate a Cardholder Data Environment (CDE)
- Process payments via credit/debit cards

You **DO NOT** need to comply if you:
- Only accept payments via PayPal, Apple Pay, Google Pay (without storing card data)
- Use fully-hosted payment forms where you never touch card data
- Use payment providers that tokenize all sensitive data

### Version Status

| Version | Status | Compliance Deadline |
|---------|--------|-------------------|
| 3.2.1   | Sunset | March 31, 2025    |
| 4.0     | Current | Mandatory since April 1, 2025 |

**Action Required:** If still on 3.2.1, migrate to 4.0 immediately. Most organizations can self-assess (no QSA needed) if using payment providers correctly.

### The Golden Rule: Reduce Your Scope

The single most important PCI-DSS principle is **REDUCE SCOPE**. Your compliance burden drops dramatically based on how you handle card data:

```
Never touch card data directly    → SAQ A     → ~22 requirements  → 30 minutes
Use payment provider iframe       → SAQ A-EP  → ~139 requirements → 2-3 days
Handle card data yourself         → SAQ D     → ~300+ requirements → 3-6 months + QSA
```

**Recommended approach for 99% of applications:** Use a payment provider like Stripe with `SAQ A` scope.

---

## Scope Reduction Strategy (Most Important Section)

This section explains how to minimize PCI-DSS compliance burden by choosing the right payment architecture.

### Scope Decision Matrix

| Payment Method | SAQ Level | Requirements | Setup Time | Annual Cost | Recommended |
|---|---|---|---|---|---|
| **Stripe Checkout** (redirect) | A | ~22 | 1 hour | $0 | ✅ YES |
| **Stripe Elements** (iframe) | A-EP | ~139 | 4 hours | $0 | ✅ YES |
| **PayPal Hosted** (redirect) | A | ~22 | 1 hour | $0 | ✅ YES |
| **Square Web Payments** | A-EP | ~139 | 4 hours | $0 | ✅ YES |
| **Braintree Drop-in** | A-EP | ~139 | 2 hours | $0 | ✅ YES |
| **Custom Card Form** | D | 300+ | 3-6 months | $50K+ | ❌ AVOID |
| **In-house Card Storage** | D | 300+ | 6-12 months | $100K+ | ❌ AVOID |

### Scope Reduction Strategy Breakdown

#### Strategy 1: Use Stripe Checkout (Simplest - SAQ A)

**How it works:**
1. Customer clicks "Pay" button on your site
2. Redirects to Stripe's hosted checkout page (never see card data)
3. Stripe handles payment processing
4. Returns to your site with payment confirmation

**Your responsibilities:**
- Verify webhook signatures from Stripe
- Secure webhook endpoint with HTTPS + API key validation
- Keep Stripe API keys secret in environment variables
- Apply standard web security (CSP, CORS, HTTPS everywhere)

**Your non-responsibilities:**
- Card data security (Stripe handles it)
- PCI compliance details (covered by Stripe)
- Payment gateway security (Stripe certified)

**PCI Impact:** SAQ A - ~22 requirements, self-assessment only, 30 minutes

**Code example:**
```typescript
// Next.js example - redirect to Stripe Checkout
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

export async function POST(req: Request) {
  const { items } = await req.json();

  // Create checkout session
  const session = await stripe.checkout.sessions.create({
    line_items: items.map(item => ({
      price_data: {
        currency: 'usd',
        product_data: { name: item.name },
        unit_amount: item.price,
      },
      quantity: 1,
    })),
    mode: 'payment',
    success_url: `${process.env.DOMAIN}/success`,
    cancel_url: `${process.env.DOMAIN}/cancel`,
  });

  return Response.json({ url: session.url });
}
```

#### Strategy 2: Use Stripe Elements (Better UX - SAQ A-EP)

**How it works:**
1. Stripe loads an iframe on your checkout page (your domain, but Stripe content)
2. Customer enters card in the iframe
3. Card data stays in Stripe's frame, never touches your servers
4. You receive a token to charge

**Your responsibilities:**
- Keep Stripe.js library up-to-date
- Validate all user input on your form
- Secure API endpoints handling tokens
- Verify webhook signatures

**PCI Impact:** SAQ A-EP - ~139 requirements, self-assessment, 2-3 days

**Code example:**
```typescript
// React + Stripe Elements example
import { loadStripe } from '@stripe/js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY);

function CheckoutForm() {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const { token } = await stripe.createToken(elements.getElement(CardElement));

    // Send token (not card!) to your backend
    const response = await fetch('/api/charge', {
      method: 'POST',
      body: JSON.stringify({ token: token.id, amount: 5000 }),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button type="submit">Pay</button>
    </form>
  );
}

export default function CheckoutPage() {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm />
    </Elements>
  );
}
```

#### Strategy 3: Use PayPal / Apple Pay / Google Pay (SAQ A)

**How it works:**
- PayPal: Customer logs into PayPal, you never see card data
- Apple Pay: Encrypted token sent directly to payment processor
- Google Pay: Tokenized payment method, no raw card data

**PCI Impact:** SAQ A - minimal requirements

**Why it works:** These providers tokenize data at the source, so you never handle card information directly.

---

## PCI-DSS 4.0 Key Changes from 3.2.1

### 1. Customized Approach vs Defined Approach

**Before (3.2.1):** All requirements applied equally to everyone.

**Now (4.0):** Organizations must choose:
- **Defined Approach:** Follow prescriptive requirements (safer, more work)
- **Customized Approach:** Document custom controls with risk analysis (more flexibility, requires justification)

**Recommendation:** Use Defined Approach unless you have specific regulatory guidance otherwise.

### 2. Multi-Factor Authentication Expanded (Requirement 8)

**New in 4.0:**
- MFA required for ALL administrative access (not just remote)
- MFA required for access to CDE systems
- MFA required for access to applications with cardholder data
- Out-of-band MFA preferred (separate channel from primary auth)

**Implementation:**
- Use authenticator apps (Google Authenticator, Authy)
- Hardware security keys (YubiKey) for admin accounts
- SMS/email as fallback only (not primary)

### 3. Targeted Risk Analysis Required (Requirement 12.6)

**New in 4.0:**
- Annual risk assessment of all new technologies/processes
- Document rationale for any exceptions
- Include third-party risk assessment

**What to assess:**
- New payment methods
- Cloud migrations
- Third-party integrations
- Infrastructure changes

### 4. Anti-Phishing Mechanisms Mandatory (Requirement 7.3)

**New in 4.0:**
- Implement DMARC, SPF, DKIM for email authentication
- Configure security headers (CSP, HSTS, X-Frame-Options)
- User awareness training for phishing
- Incident response plan for compromised accounts

**Implementation checklist:**
- [ ] DMARC record published (at least p=quarantine)
- [ ] SPF record configured
- [ ] DKIM signing enabled
- [ ] CSP headers on all pages
- [ ] HSTS enabled (Strict-Transport-Security)
- [ ] X-Frame-Options: DENY (prevent clickjacking)

### 5. Client-Side Script Management (Requirement 6.4.3) - CRITICAL FOR WEB APPS

**This is the most impactful new requirement for web developers.**

**What it requires:**
- Maintain inventory of ALL JavaScript/third-party scripts on pages accessing cardholder data
- Justify the business need for each script
- Implement subresource integrity (SRI) for script validation
- Monitor for unauthorized script injection
- Use Content Security Policy (CSP) to restrict script sources

**Why it matters:**
- Malicious actors can inject code through compromised libraries
- Third-party widgets (analytics, chat, ads) can steal card data
- Supply chain attacks are increasing

**Implementation:**

```html
<!-- BAD: No integrity check, external source not validated -->
<script src="https://external.com/analytics.js"></script>

<!-- GOOD: Subresource Integrity hash, explicitly allowed source -->
<script
  src="https://external.com/analytics.js"
  integrity="sha384-ABC123..."
  crossorigin="anonymous"
></script>
```

**Content Security Policy header:**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://stripe.com https://js.stripe.com
    https://cdn.jsdelivr.net integrity='require-sri-for' 'strict-dynamic';
  style-src 'self' 'unsafe-inline';
  img-src 'self' https:;
  font-src 'self' https:;
  connect-src 'self' https://api.stripe.com;
  frame-src 'self' https://stripe.com;
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  upgrade-insecure-requests;
```

**Script inventory template:**

| Script Name | URL | Purpose | Business Justification | SRI Hash | Frequency |
|---|---|---|---|---|---|
| Stripe.js | https://js.stripe.com/v3 | Payment processing | Core functionality | sha384-ABC... | Always |
| Analytics | https://cdn.example.com/analytics | Traffic tracking | Marketing | sha384-DEF... | Always |
| Chat widget | https://chat.example.com/chat.js | Customer support | User support | sha384-GHI... | Business hours |
| A/B testing | https://experiments.example.com/ab.js | Conversion optimization | Product | sha384-JKL... | **REMOVE FROM CHECKOUT** |

**Action for checkout pages:**
- [ ] No analytics scripts on payment pages
- [ ] No chat widgets during checkout
- [ ] No A/B testing on checkout flow
- [ ] Only Stripe.js and minimal required scripts

---

## Payment Stack Recommendations

### Scenario 1: E-commerce / SaaS (Most Common)

**Goal:** Process payments without handling card data

**Stack:**

```
┌─────────────────────────────────────────────────────────┐
│ Your Frontend (React, Vue, Svelte, etc.)                │
│ - Display products                                      │
│ - Collect customer info (name, email, address)         │
│ - Redirect to Stripe Checkout OR embed Stripe Elements │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Stripe Payment Gateway │
        │  (Handles all card data)│
        └────────────┬────────────┘
                     │
        ┌────────────▼──────────────┐
        │ Your Backend (Node, Python)│
        │ - Verify webhook signature │
        │ - Update order status      │
        │ - Send receipt email       │
        │ - Update inventory         │
        └────────────────────────────┘
                     │
┌────────────────────▼───────────────────┐
│ Your Database (PostgreSQL, MongoDB)    │
│ - Store: order_id, customer_id,       │
│   stripe_payment_id, amount, status    │
│ - NEVER store: card numbers, CVV,     │
│   expiration dates                    │
└───────────────────────────────────────┘
```

**Implementation Details:**

```typescript
// Backend: Handle webhook from Stripe
import Stripe from 'stripe';
import { createHmac } from 'crypto';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

export async function POST(req: Request) {
  const body = await req.text();
  const sig = req.headers.get('stripe-signature');

  // Verify webhook signature (CRITICAL for security)
  let event;
  try {
    event = stripe.webhooks.constructEvent(body, sig, webhookSecret);
  } catch (err) {
    return new Response('Webhook signature verification failed', { status: 400 });
  }

  // Handle payment completion
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;

    // Update order in your database
    await db.orders.update(
      { stripe_payment_id: session.payment_intent },
      { status: 'paid', paid_at: new Date() }
    );

    // Send receipt email (Stripe can do this automatically)
    await sendReceiptEmail(session.customer_email);

    // Fulfill order
    await fulfillOrder(session.metadata.order_id);
  }

  return Response.json({ received: true });
}
```

**Database Schema (Safe - No Card Data):**

```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY,
  customer_id UUID NOT NULL,
  stripe_payment_id TEXT NOT NULL,           -- stripe-assigned ID
  amount_cents INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',
  status ENUM('pending', 'paid', 'failed', 'refunded'),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- NEVER add columns for:
-- - card_number
-- - cvv / cvc
-- - expiration_date
-- - cardholder_name (store separately in customer table if needed)
```

**PCI-DSS Impact:**
- SAQ Level: **A** (30 minutes self-assessment)
- Stripe handles: Payment security, PCI compliance, fraud protection
- You handle: Business logic, order fulfillment, customer service

**Cost:**
- Stripe: 2.9% + $0.30 per transaction
- Annual PCI compliance: $0 (self-assessment only)
- Infrastructure: Whatever you'd use anyway

---

### Scenario 2: SaaS Subscriptions with Recurring Billing

**Goal:** Process recurring payments + manage subscriptions

**Stripe Features to Use:**
- Stripe Billing (subscriptions, invoicing, proration)
- Customer Portal (customers manage billing themselves)
- Webhook events (subscription events trigger your logic)

**Implementation:**

```typescript
// Create subscription for customer
const subscription = await stripe.subscriptions.create({
  customer: stripe_customer_id,
  items: [
    {
      price: 'price_monthly_plan', // Create price in Stripe dashboard
      quantity: 1,
    },
  ],
  payment_behavior: 'default_incomplete',
  payment_settings: { save_default_payment_method: 'on_subscription' },
  expand: ['latest_invoice.payment_intent'],
});

// Webhook: Handle subscription events
if (event.type === 'invoice.paid') {
  // Payment succeeded - give customer access
  await grantUserAccess(event.data.object.customer);
}

if (event.type === 'invoice.payment_failed') {
  // Payment failed - revoke access
  await revokeUserAccess(event.data.object.customer);
}

if (event.type === 'customer.subscription.deleted') {
  // Subscription cancelled - clean up
  await cleanupUserData(event.data.object.customer);
}
```

**Customer Portal (Self-Service):**

```typescript
// Generate link to Stripe Customer Portal
const portalSession = await stripe.billingPortal.sessions.create({
  customer: stripe_customer_id,
  return_url: 'https://yourapp.com/account',
});

// Redirect customer to: portalSession.url
// They can now:
// - Change payment method
// - Update billing address
// - View invoices
// - Cancel subscription
// - All without you handling any card data
```

**PCI-DSS Impact:** SAQ A (similar to e-commerce)

**Benefits:**
- Reduced support tickets (customers self-serve)
- Automatic billing retries (Stripe handles dunning)
- Reduced churn (easy to reactivate subscriptions)
- Stripe handles all PCI compliance

---

### Scenario 3: Marketplace / Platform (Multiple Sellers)

**Goal:** Process payments from buyers → collect fees → send funds to sellers

**Use Stripe Connect:**

```
Customer pays Seller
        ↓
    Your Platform
        ↓
    Stripe charges customer
    Stripe pays seller (minus your fee)
        ↓
    You never touch money directly
    You never have seller funds in your account
```

**Implementation:**

```typescript
// Setup seller account (Stripe Connected Account)
const account = await stripe.accounts.create({
  type: 'express',
  country: 'US',
  email: seller.email,
});

// Create account link for onboarding
const accountLink = await stripe.accountLinks.create({
  account: account.id,
  type: 'account_onboarding',
  return_url: 'https://yourapp.com/seller/dashboard',
  refresh_url: 'https://yourapp.com/seller/onboarding',
});

// When buyer purchases:
const paymentIntent = await stripe.paymentIntents.create({
  amount: total_amount,
  currency: 'usd',
  application_fee_amount: fee_amount,
  stripe_account: seller_stripe_account_id,
});

// Seller receives: total_amount - fee_amount
// You receive: fee_amount (automatically)
// PCI compliance: Stripe handles everything
```

**PCI-DSS Impact:**
- Your platform: SAQ A
- Sellers: Stripe handles (they're Stripe's customers)
- You never touch seller funds or payment details

**Why it's better than transferring money manually:**
- No bank transfer delays
- No 1099 tax reporting burden
- No PCI compliance for sellers
- Instant payouts available to sellers

---

### Scenario 4: Enterprise / Custom Requirements (Rare)

**When you MUST handle card data:**
- Regulatory requirement (e.g., issuing bank)
- Unique business model (e.g., payment processor)
- Contractual obligation (e.g., enterprise customer)

**If you absolutely must handle card data:**

#### Use a Tokenization Vault (Don't Store Cards Directly)

**What it is:** A third-party service that encrypts and stores card data, you use tokens

| Provider | Cost | Best For | Key Feature |
|---|---|---|---|
| **VGS (Very Good Security)** | $500+/mo | Any industry, any use case | Proxy vault, tokenizes all data |
| **Basis Theory** | $50+/mo | Growing companies, custom flows | Developer-friendly, flexible |
| **TokenEx** | Enterprise pricing | Large enterprises | Mature platform |
| **Stripe Restricted Accounts** | Custom | If already using Stripe | Limited custom flows |

**How it works:**

```
Customer enters card info
          ↓
Tokenization Vault (VGS/Basis Theory) handles encryption
          ↓
Your app receives: token_abc123
          ↓
Your database stores: token_abc123 (not the card)
          ↓
To charge: Send token_abc123 to Stripe (or other processor)
          ↓
Stripe charges and returns: success/failure
```

**Network Architecture for SAQ D:**

```
┌─────────────────────────────────────────────────────────┐
│ Your Cardholder Data Environment (CDE)                  │
│ - Tokenization vault                                    │
│ - Payment processing servers                            │
│ - Database (tokens only, no card numbers)               │
│                                                         │
│ Security:                                               │
│ - Dedicated firewall (hardware or software)             │
│ - Network segmentation from corporate network          │
│ - VPN/IPSEC for all CDE communication                  │
│ - File Integrity Monitoring (Samhain, AIDE)            │
│ - IDS/IPS (Snort, Suricata)                           │
│ - Log aggregation (ELK, Splunk)                        │
│ - Vulnerability scanning weekly                        │
│ - Penetration testing annually (QSA)                   │
└─────────────────────────────────────────────────────────┘
           ↓
        Firewall (Only allow required ports/IPs)
           ↓
┌─────────────────────────────────────────────────────────┐
│ Non-CDE (Corporate Network)                             │
│ - Web servers (no payment data)                         │
│ - Admin workstations                                    │
│ - Logging systems                                       │
└─────────────────────────────────────────────────────────┘
```

**QSA Audit (Annual):**
- Cost: $50,000 - $200,000
- Timeline: 3-6 months
- Assessment Type: SAQ D
- Requirements: ~300+ detailed requirements
- Ongoing: Quarterly external vulnerability scans

**Cost Analysis (SAQ D vs SAQ A):**

| Factor | SAQ A | SAQ D |
|---|---|---|
| Annual PCI cost | $0 (self) | $100K-200K (QSA + infrastructure) |
| Staff time | 30 min | 3-6 months |
| Infrastructure complexity | Simple | Complex (CDE, firewall, monitoring) |
| Security incidents | Low risk | Higher attack surface |
| Scalability | Pay per transaction | Fixed infrastructure cost |

**Recommendation:** Only choose SAQ D if you have specific business reasons (payment processor, bank requirements, unique workflow that can't be tokenized).

---

## Requirement 6.4.3: Client-Side Script Management (New in 4.0)

This requirement fundamentally changes how you build payment pages. It's critical for modern web applications.

### What Changed

**Before 4.0:** No specific requirement for script inventory

**Now 4.0:** Must maintain and justify ALL scripts on CDE-connected pages

### Script Categories

**1. Essential (Always allowed):**
- Stripe.js (or Square.js, etc.)
- PayPal SDK
- Your own custom payment code
- SSL/TLS libraries

**2. Conditional (Needs justification):**
- Form validation libraries
- CSS frameworks
- Session management

**3. Problematic (Should avoid on checkout):**
- Analytics (Google Analytics, Mixpanel)
- Chat widgets (Intercom, Drift, Zendesk)
- A/B testing (Optimizely, VWO)
- Ad networks (Facebook Pixel, Google Ads)
- User session recording (Fullstory, Hotjar)
- Error tracking (Sentry, Rollbar) — if not configured properly

### Implementation: Content Security Policy

**Step 1: Define CSP Header**

```
Content-Security-Policy:
  default-src 'none';
  script-src 'self'
    https://js.stripe.com
    https://cdn.jsdelivr.net
    https://your-verified-analytics.com
    'strict-dynamic'
    'nonce-{RANDOM}';
  style-src 'self' 'unsafe-inline';
  img-src 'self' https: data:;
  font-src 'self' https:;
  connect-src 'self'
    https://api.stripe.com
    https://your-backend.com;
  frame-src 'self' https://js.stripe.com;
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
```

**Step 2: Implement Subresource Integrity (SRI)**

```html
<!-- Generate hash: cat script.js | openssl dgst -sha384 -binary | openssl enc -base64 -A -->
<script
  src="https://js.stripe.com/v3"
  integrity="sha384-..."
  crossorigin="anonymous"
  nonce="random-value-123"
></script>
```

**Step 3: Maintain Script Inventory**

Create a document in your compliance folder:

```markdown
# Script Inventory - Checkout Page

| Script | Source | Hash | Purpose | Justification | Approved | Review Date |
|---|---|---|---|---|---|---|
| Stripe.js | https://js.stripe.com/v3 | sha384-abc | Payment processing | Core functionality | ✓ | 2026-03-02 |
| Form validation | https://yourcdn.com/validate.js | sha384-def | User input validation | Prevents bad data | ✓ | 2026-03-02 |
| Analytics | https://google-analytics.com/ga.js | sha384-ghi | **NOT ON CHECKOUT** | **PROHIBITED** | ✗ | 2026-03-02 |
```

### What Auditors Look For

During a PCI audit or self-assessment, they'll verify:

1. **Script Inventory Exists:** Can you list every script on checkout pages?
2. **Hashes Documented:** Do you have SRI hashes for each script?
3. **Justification:** Is there business justification for each script?
4. **Monitoring:** Do you check monthly for unauthorized script injection?
5. **Incident Response:** What's your response plan if a script is compromised?

### Common Violations & Fixes

**Violation 1: Analytics on checkout page**

```html
<!-- BAD: Analytics captures card input -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
</script>

<!-- GOOD: Analytics redirects to thank-you page AFTER payment -->
<script>
  // Only load analytics AFTER successful payment
  if (window.location.pathname === '/thank-you') {
    // Load analytics script here
  }
</script>
```

**Violation 2: No SRI on third-party script**

```html
<!-- BAD: No integrity check -->
<script src="https://external-cdn.com/library.js"></script>

<!-- GOOD: SRI prevents tampering -->
<script
  src="https://external-cdn.com/library.js"
  integrity="sha384-xyzabc..."
  crossorigin="anonymous"
></script>
```

**Violation 3: Chat widget on checkout**

```html
<!-- BAD: Chat can capture card info or inject malicious code -->
<script src="https://chat.example.com/chat.js"></script>

<!-- GOOD: Chat only on non-checkout pages -->
<!-- Load chat.js ONLY on homepage and product pages, NOT checkout -->
```

---

## Tokenization Providers (Alternative to Handling Cards)

If you need flexibility beyond Stripe but don't want SAQ D complexity, use a tokenization vault:

### VGS (Very Good Security)

**What it does:** Proxy-based tokenization. Customer card → VGS vault → your app receives token

**Cost:** $500-5,000+/month depending on volume

**Best for:** Enterprise, custom payment flows, financial services

**Integration:**

```typescript
// 1. Customer enters card in VGS-hosted iframe
<iframe src="https://vault.example.com/form"></iframe>

// 2. On form submit, you receive tokenized payment method
const response = await fetch('/api/process', {
  method: 'POST',
  body: JSON.stringify({
    // NOT card data, just the token
    vgs_token: 'tok_sandbox_abc123',
    amount: 5000,
  }),
});

// 3. Your backend sends token to Stripe (or any processor)
const charge = await stripe.charges.create({
  amount: 5000,
  currency: 'usd',
  source: vgs_token, // Stripe accepts VGS tokens
});
```

**Scope:** SAQ A-EP (similar to Stripe Elements)

### Basis Theory

**What it does:** API-first tokenization platform

**Cost:** $50-1,000+/month

**Best for:** Developers, startups scaling up, custom integrations

**Key features:**
- Tokenization for any data (cards, SSNs, IBANs)
- Proxy API (tokenizes in transit)
- Reactor (serverless data processing)

**Integration:**

```typescript
// Client-side: Submit card to Basis Theory
const response = await fetch('https://api.basistheory.com/tokenize', {
  method: 'POST',
  headers: { 'BT-API-KEY': 'public_key' },
  body: JSON.stringify({
    data: {
      number: cardNumber,
      expiration_month: expMonth,
      expiration_year: expYear,
      cvc: cvc,
    },
  }),
});

const token = response.token;

// Server-side: Use token with Stripe
const charge = await stripe.charges.create({
  amount: 5000,
  currency: 'usd',
  source: token,
});
```

**Scope:** SAQ A-EP (you never handle card data)

### TokenEx

**What it does:** Enterprise tokenization vault

**Cost:** Custom enterprise pricing

**Best for:** Large enterprises, high transaction volume, mature PCI programs

**Scope:** Can be SAQ A-EP or SAQ D depending on integration method

---

## Network Architecture for PCI (SAQ D)

If you must handle card data, here's the secure architecture:

### Network Diagram

```
┌─────────────────────────────────────────────────────┐
│  INTERNET                                           │
│  └─ HTTPS/TLS 1.2+ only                            │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  Firewall (Primary) │
        │  - Stateful         │
        │  - Logging enabled  │
        │  - DDoS protection  │
        └──────────┬──────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│  CDE (Cardholder Data Environment) - ISOLATED      │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Payment Application Servers                 │   │
│  │ - Stripe integration                        │   │
│  │ - Payment processing API                    │   │
│  │ - Only handles tokens, not card data        │   │
│  │ - TLS 1.2+ for all communication            │   │
│  │ - API authentication (X-API-Key header)     │   │
│  └─────────────────────────────────────────────┘   │
│                  │                                   │
│  ┌──────────────▼──────────────────────────────┐   │
│  │ Tokenization Vault (VGS/Basis Theory)       │   │
│  │ - Encrypts and stores card data             │   │
│  │ - Returns tokens only                       │   │
│  │ - HSM-backed encryption                     │   │
│  │ - Separate DB access controls               │   │
│  └──────────────┬──────────────────────────────┘   │
│                 │                                    │
│  ┌──────────────▼──────────────────────────────┐   │
│  │ CDE Database                                │   │
│  │ - Encrypted storage (AES-256)               │   │
│  │ - Tokenized card references ONLY            │   │
│  │ - NEVER stores: card numbers, CVV, PIN      │   │
│  │ - Row-level access controls                 │   │
│  │ - Separate encryption keys per record       │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  Monitoring & Logging:                              │
│  - File Integrity Monitoring (Samhain/AIDE)        │
│  - IDS/IPS (Snort/Suricata)                       │
│  - Network monitoring (tcpdump, zeek)              │
│  - Log aggregation (ELK, Splunk, Papertrail)       │
│  - Real-time alerting on anomalies                 │
└─────────────────┬──────────────────────────────────┘
                  │
        ┌─────────▼─────────┐
        │  Firewall (DMZ)   │
        │  - Restrictive    │
        └─────────┬─────────┘
                  │
┌─────────────────▼──────────────────────────────────┐
│  Non-CDE (Corporate Network)                        │
│  - Web servers (no card processing)                │
│  - Admin workstations                              │
│  - DNS servers                                     │
│  - Email servers                                   │
│  - Separate from CDE by firewall                   │
│  - No user workstations access CDE                │
│  - Restricted VPN for admin access                │
└──────────────────────────────────────────────────────┘
```

### Firewall Rules (SAQ D)

**CDE Inbound Rules:**

| Source | Destination | Protocol | Port | Purpose | Justification |
|---|---|---|---|---|---|
| Customers (0.0.0.0/0) | Payment servers | HTTPS | 443 | Payment processing | Needed |
| Payment processor (Stripe IP) | CDE servers | HTTPS | 443 | Webhook callbacks | Needed |
| CDE servers | External APIs | HTTPS | 443 | Tokenization, processing | Needed |
| Admins (VPN) | CDE servers | SSH | 22 | Maintenance | Restricted |
| CDE servers | Logging (ELK) | TCP | 5000 | Log forwarding | Monitoring |
| CDE servers | Internal DB | TCP | 5432 | Database access | Needed |

**CDE Outbound Rules:**

| Source | Destination | Protocol | Port | Purpose | Justification |
|---|---|---|---|---|---|
| Payment servers | Stripe | HTTPS | 443 | Payment processor | Needed |
| Tokenization vault | CDE DB | TCP | 5432 | Token storage | Needed |
| Any CDE | Internet | All | Any | **BLOCKED** | Security |
| CDE | NTP server | UDP | 123 | Time sync (for logs) | Needed |

### Encryption Requirements

**Data in Transit (TLS 1.2+ Mandatory):**
- All CDE communication encrypted
- TLS 1.0/1.1 obsolete (PCI 4.0 requirement)
- Certificate pinning for external integrations

**Data at Rest (AES-256 Minimum):**
- Database encryption: AES-256
- Backup encryption: AES-256
- Key management: Hardware Security Module (HSM)
- Key rotation: Quarterly minimum

**Key Management:**
```
- Never store encryption keys in code or config files
- Use HSM (Hardware Security Module) for key storage
- Separate key storage from encrypted data location
- Access logging for all key operations
- Key rotation policy (quarterly minimum)
- Tested disaster recovery for key backup
```

### Logging & Monitoring

**What to Log:**
- All access to CDE systems
- All database queries involving tokens
- All admin logins and activities
- All security events (failed logins, firewall blocks)
- All file integrity monitoring alerts

**What NOT to Log:**
- Full card numbers (PAN)
- CVV/CVC codes
- Security codes
- PIN blocks
- Encryption keys
- Passwords

**Log Retention:**
- Minimum 1 year
- Minimum 3 months immediately accessible
- Searchable and backed up
- Protected from tampering (immutable storage)

**Log Example (GOOD):**
```
2026-03-02T14:23:45Z user=admin action=process_payment
  event=token_received token_id=tok_abc123
  amount=5000 status=success ip=192.168.1.10
```

**Log Example (BAD - Don't do this):**
```
2026-03-02T14:23:45Z user=admin action=process_payment
  card_number=4242424242424242 cvv=123 exp=12/26
  amount=5000 status=success
```

---

## Common PCI-DSS Mistakes

### Mistake 1: Building Custom Card Forms

**What people do:**
```html
<!-- BAD: Your server now has SAQ D -->
<input type="text" name="card_number" maxlength="16" />
<input type="text" name="cvv" maxlength="3" />
<input type="text" name="expiration" />
```

**Why it fails:**
- Card data touches your servers
- Every input field is a PCI requirement
- One vulnerability compromises cards
- Auditor required annually (expensive)
- Compliance burden: 300+ requirements

**Solution: Use Stripe Elements**
```html
<!-- GOOD: Card data never touches your servers -->
<div id="card-element"></div>

<script>
const stripe = Stripe('pk_live_...');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');
</script>
```

**Result:** SAQ A-EP instead of SAQ D

### Mistake 2: Logging Card Data

**What people do:**
```typescript
// BAD: Card data in logs = PCI violation
console.log('Processing payment:', {
  card_number: '4242424242424242',
  cvv: '123',
  amount: 5000,
});
```

**Impact:**
- Violation of Requirement 3.4 (protecting card data)
- Logs now contain sensitive data
- Backup tapes require secure disposal
- Audit failure

**Solution:**
```typescript
// GOOD: Only log non-sensitive data
console.log('Processing payment:', {
  token: 'tok_abc123',
  last_four: '4242',
  amount: 5000,
});
```

### Mistake 3: Storing CVV (Never Allowed)

**What people do:**
```typescript
// EXTREMELY BAD: CVV storage is NEVER permitted
await db.cards.insert({
  customer_id: 123,
  card_number: '4242...4242',
  cvv: '123', // PCI explicitly forbids this
  expiration: '12/26',
});
```

**Why:**
- PCI explicitly prohibits CVV storage (even encrypted)
- CVV is used to verify card ownership
- Storing it defeats its purpose
- Guaranteed audit failure

**Solution:**
```typescript
// GOOD: Never store CVV
const token = await stripe.createToken({
  number: cardNumber,
  exp_month: expMonth,
  exp_year: expYear,
  cvc: cvv, // Stripe handles CVV, not your servers
});

await db.cards.insert({
  customer_id: 123,
  stripe_token: token.id, // Store token, not card
});
```

### Mistake 4: Not Verifying Webhook Signatures

**What people do:**
```typescript
// BAD: Trusts any webhook without verification
app.post('/webhook', (req, res) => {
  if (req.body.type === 'payment.success') {
    // Attacker can send fake webhooks!
    grantUserAccess(req.body.customer_id);
  }
});
```

**Why it's dangerous:**
- Attackers can forge webhook requests
- Grant access to accounts that didn't pay
- Revenue loss and fraud

**Solution:**
```typescript
// GOOD: Verify webhook signature
app.post('/webhook', (req, res) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET // Secret only you know
    );

    if (event.type === 'charge.succeeded') {
      grantUserAccess(event.data.object.customer);
    }
  } catch (err) {
    return res.status(400).send('Webhook signature verification failed');
  }
});
```

### Mistake 5: Not Removing Scripts from Checkout (6.4.3)

**What people do:**
```html
<!-- BAD: Analytics on checkout page (6.4.3 violation) -->
<head>
  <script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
  <script src="https://chat.example.com/chat.js"></script> <!-- Customer support? -->
</head>

<!-- Payment form here -->
<form id="payment-form">
  <!-- Card input or Stripe Elements -->
</form>
```

**Why it fails (PCI 4.0):**
- Requirement 6.4.3 (new in 4.0) prohibits unauthorized scripts
- Analytics can be compromised to steal data
- Chat widget can inject malicious code
- Audit failure

**Solution:**
```html
<!-- GOOD: Minimal scripts on checkout -->
<head>
  <!-- Only Stripe, no analytics, no chat -->
  <script src="https://js.stripe.com/v3"
    integrity="sha384-..."
    crossorigin="anonymous"></script>
</head>

<!-- Payment form here -->
<form id="payment-form">
  <!-- Card input or Stripe Elements -->
</form>

<!-- Load analytics ONLY on thank-you page -->
<script>
  if (window.location.pathname === '/thank-you') {
    // Load analytics here, after payment completed
  }
</script>
```

### Mistake 6: Not Doing SAQ Even When Using Stripe

**What people do:**
- Use Stripe Checkout (SAQ A)
- Never submit SAQ self-assessment
- Assume "Stripe handles it all"

**Why it's incomplete:**
- YOU are still responsible for SAQ compliance
- Stripe handles payment security, not your business logic
- Your web server security is your responsibility
- Your API endpoints are your responsibility
- Your database security is your responsibility

**Solution:**
```
Annual Checklist (SAQ A - 30 minutes):
☐ All my systems run HTTPS (no HTTP)
☐ I've documented Stripe as payment processor
☐ I have firewall rules logged
☐ I've verified no card data in my database
☐ I have vulnerability scanning enabled
☐ I have incident response plan
☐ Staff completed security training
☐ I've documented security policies
```

---

## Decision Tree: Choosing Your Approach

```
START
  │
  ├─ Do you process credit cards online?
  │  ├─ NO → Not in scope, no PCI needed ✓
  │  └─ YES → Continue
  │
  ├─ Can you avoid handling card data entirely?
  │  ├─ YES → Use payment provider → SAQ A → Done ✓
  │  │        (Stripe Checkout, PayPal, etc.)
  │  └─ NO → Continue
  │
  ├─ Can you use a payment iframe (Stripe Elements)?
  │  ├─ YES → SAQ A-EP → Manageable (2-3 days) ✓
  │  └─ NO → Continue
  │
  ├─ Do you have a specific business reason to handle cards?
  │  ├─ Payment processor? Issuing bank? Enterprise requirement?
  │  │  ├─ YES → Use tokenization vault → SAQ A-EP or D
  │  │  │        (Still better than storing cards directly)
  │  │  │        Budget: $50K-200K/year
  │  │  └─ NO → You probably shouldn't handle cards
  │  │           Talk to your compliance officer
  │  └─ NO → STOP, reevaluate architecture
  │
  └─ If SAQ D unavoidable:
     ├─ Hire QSA (Qualified Security Assessor)
     ├─ Budget: $50K-200K annually
     ├─ Timeline: 6-12 months for first assessment
     ├─ Infrastructure: CDE, firewall, monitoring, HSM
     ├─ Staffing: Dedicated compliance/security team
     └─ Accept higher ongoing costs
```

---

## SAQ Self-Assessment Template (SAQ A)

If using Stripe Checkout or similar, complete this annually:

```markdown
# PCI-DSS 4.0 Self-Assessment (SAQ A)

## Company Information
- Organization: [Your company]
- Assessment date: [Today's date]
- Assessor: [Your name, title]
- Systems assessed: [List systems processing cards]

## Compliance Questions

### 1. Cardholder Data Handling
- [ ] We do NOT directly handle credit card data
- [ ] We use Stripe for all payment processing
- [ ] We never store: card numbers, CVV, PIN

### 2. Security Infrastructure
- [ ] All systems use HTTPS (TLS 1.2+)
- [ ] Firewall is configured and logged
- [ ] Intrusion detection is enabled
- [ ] Antivirus is installed and updated

### 3. Network Segmentation
- [ ] Payment systems are segmented from corporate network
- [ ] Non-public internet-connected devices have firewall rules
- [ ] No untrusted systems access payment data

### 4. Data Protection
- [ ] Stripe handles encryption for card data
- [ ] Our database contains NO card data
- [ ] All sensitive data in transit is encrypted

### 5. Vulnerability Management
- [ ] Vulnerability scans enabled (quarterly minimum)
- [ ] Security patches applied (within 30 days)
- [ ] Up-to-date antivirus definitions

### 6. Access Control
- [ ] Admin passwords are unique and strong
- [ ] MFA enabled for admin access
- [ ] Access logs reviewed monthly
- [ ] User accounts removed when no longer needed

### 7. Monitoring & Logging
- [ ] Security events are logged
- [ ] Logs retained for minimum 1 year
- [ ] Logs are protected from tampering
- [ ] Log integrity verified monthly

### 8. Security Policies
- [ ] Security policy documented and reviewed annually
- [ ] Incident response plan documented
- [ ] Employee security training completed
- [ ] Third-party data handling agreements in place

### 9. Testing & Remediation
- [ ] Vulnerability scans show no critical/high severity issues
- [ ] Identified issues remediated within agreed timeframe
- [ ] Firewall rules tested quarterly
- [ ] Incident response plan tested at least once annually

### 10. Evidence & Documentation
- [ ] Stripe integration documentation
- [ ] Network diagram showing payment flow
- [ ] Firewall rules and configuration
- [ ] Vulnerability scan reports
- [ ] Security policy
- [ ] Incident response plan
- [ ] Training certificates
- [ ] Risk assessment

## Attestation

I attest that this organization is compliant with PCI-DSS 4.0 requirements for SAQ A as of [date].

Assessor: _________________ Date: _________
```

---

## Pricing & Cost Analysis

### Cost Comparison by Approach

| Approach | Setup | Per-transaction | Annual Compliance | Total Annual |
|---|---|---|---|---|
| **Stripe Checkout (SAQ A)** | 1 hour | 2.9% + $0.30 | $0 (self) | Transaction fees only |
| **Stripe Elements (SAQ A-EP)** | 4 hours | 2.9% + $0.30 | $0 (self) | Transaction fees only |
| **VGS Tokenization (SAQ A-EP)** | 20 hours | 2.9% + $0.30 + $500+/mo | $0-2K (self) | ~$6K-8K + transaction fees |
| **SAQ D (Custom handling)** | 3-6 months | 2.9% + $0.30 | $100K-200K (QSA) | $100K-250K + fees |

### Fee Breakdown (Example: $100,000 Monthly Volume)

**Stripe Checkout:**
- Processing: $100,000 × 2.9% = $2,900
- Per-transaction: 100,000 × $0.30 = $30,000 (wait, this seems wrong for monthly)
  - Actually: If 1,000 transactions/month: 1,000 × $0.30 = $300
- Annual compliance: $0
- **Total: ~$36,600/year in fees (assuming typical transaction counts)**

**SAQ D with QSA:**
- Processing: ~$36,600 (same as above)
- QSA audit: $100,000-200,000
- Infrastructure (firewall, monitoring, staff): ~$50,000-100,000
- **Total: $186K-336K/year**

**Verdict:** For 99% of organizations, Stripe is dramatically cheaper and less risky.

---

## Current Compliance Deadline

- **PCI-DSS 3.2.1**: Sunset March 31, 2025 (PAST - must upgrade)
- **PCI-DSS 4.0**: Mandatory April 1, 2025 (CURRENT)
- **Compliance assessment**: Self-assessment (SAQ) due by end of calendar year

**Action items:**
1. If still on 3.2.1, upgrade immediately
2. Update SAQ form to 4.0 version
3. Review Requirement 6.4.3 (client-side scripts)
4. Document all third-party scripts on payment pages
5. Remove non-essential scripts from checkout

---

## Pricing Stability Note

<!-- PRICING_STABILITY: moderate | last_verified: 2026-03 | check_interval: 12_months -->

**Payment Processing Fees:** Stripe charges 2.9% + $0.30 per transaction. These rates have been stable for 5+ years and are unlikely to change significantly.

**SAQ Requirements:** PCI-DSS 4.0 is current through 2025+. Major version changes occur roughly every 3-4 years, so expect 4.0 requirements to remain stable through 2027-2028.

**Recommendation:** Lock in Stripe rates for multi-year contracts if you have high volume.

---

## Quick Reference Checklist

### For E-commerce / SaaS (Using Stripe)

```
☐ Stripe Checkout or Elements integrated
☐ Webhook secret stored in environment variable
☐ Webhook signature verification implemented
☐ No card data in database (only stripe_payment_id or customer_id)
☐ HTTPS enabled on all pages
☐ CSP header with Stripe.js whitelisted
☐ No analytics/chat scripts on checkout page (6.4.3)
☐ API endpoints authenticated (API key or JWT)
☐ Logging configured (no card data in logs)
☐ SAQ A self-assessment completed and filed
☐ Incident response plan documented
☐ Security policies reviewed with team
☐ Vulnerability scanning enabled (quarterly)
☐ Backups tested and encrypted
☐ MFA enabled for admin accounts
```

### For Enterprise (SAQ D)

```
☐ QSA selected and contracted
☐ CDE designed and documented
☐ Firewall rules implemented and tested
☐ Tokenization vault operational
☐ File integrity monitoring enabled
☐ IDS/IPS deployed
☐ Key management HSM operational
☐ Log aggregation system operational
☐ Encryption enabled (TLS 1.2+, AES-256)
☐ Access controls configured
☐ Security policies documented
☐ Training completed for all staff
☐ Penetration testing scheduled
☐ Quarterly vulnerability assessments scheduled
☐ Incident response drills conducted
☐ SAQ D self-assessment in progress
```

---

## Related References
- [Compliance Provider Matrix](./38-compliance-provider-matrix.md) — PCI-DSS compliance status by payment provider
- [Payment & Billing Platforms](./19-payment-billing-platforms.md) — Payment processor PCI compliance requirements
- [SOC 2 Compliance Architecture Guide](./34-compliance-soc2.md) — Broader security framework complementing PCI-DSS
- [Security Essentials: Complete Tech-Stack Reference](./30-security-essentials.md) — Foundational security controls for PCI
- [Modern Web Security & Zero Trust Architecture](./44-modern-web-security-zero-trust.md) — Network security for payment systems

---

## References & Resources

- [PCI Security Standards Council](https://www.pcisecuritystandards.org/)
- [PCI-DSS 4.0 Full Standard](https://www.pcisecuritystandards.org/documents/PCI-DSS-v4.0.pdf)
- [Stripe PCI Compliance](https://stripe.com/en-gb/guides/pci-compliance)
- [OWASP Payment Card Industry Data Security Standard](https://owasp.org/www-project-pci-dss/)
- [VGS Tokenization Platform](https://www.verygoodsecurity.com/)
- [Basis Theory](https://www.basistheory.com/)

---

## Document Maintenance

**Last Updated:** March 2, 2026
**Next Review:** March 2, 2027
**Maintained By:** Compliance & Security Team

**Change Log:**
- 2026-03-02: Initial document creation, PCI-DSS 4.0 current
- Content covers: Stripe integration, tokenization alternatives, SAQ levels, 6.4.3 requirements

---

**Disclaimer:** This guide provides general architectural guidance for PCI-DSS 4.0 compliance. It is not legal or professional security advice. Consult with a Qualified Security Assessor (QSA) or compliance professional for your specific situation, especially for SAQ D requirements.
