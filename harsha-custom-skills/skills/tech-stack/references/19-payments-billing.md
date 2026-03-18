# Payment & Billing Platforms: Comprehensive Tech-Stack Reference

## Executive Summary (2025-2026)

This guide evaluates six major payment platforms across 13 critical dimensions. The payment ecosystem has fragmented into two clear models: **Merchant of Record (MoR) solutions** that assume legal responsibility for tax/compliance and **Payment Service Providers (PSPs)** that handle transactions only.

**As of February 2026:**
- Stripe remains dominant for technical control and API depth
- Paddle dominates MoR for SaaS (5% + $0.50)
- LemonSqueezy leads indie hacker segment (5% + $0.50, simpler UX)
- RevenueCat owns in-app purchases exclusively
- Polar and Creem are emerging open-source/startup alternatives

---

## PART 1: PLATFORM COMPARISON MATRIX

### 1. Transaction Fees

| Provider | Base Fee | International | Subscription | PayPal | Monthly Fee | Payout Fee |
|----------|----------|----------------|--------------|--------|-------------|-----------|
| **Stripe** | 2.9% + $0.30 | +1.5% | Same | N/A | $0 | $0 |
| **Paddle** | 5% + $0.50 | Included | Included | N/A | $0 | $0 |
| **LemonSqueezy** | 5% + $0.50 | +1.5% | +0.5% | +1.5% | $0 | $0 (lowered 2025) |
| **Creem** | 3.9% + $0.40 | Included | Included | N/A | $0 | Free instant payouts |
| **Polar** | 4% + $0.40 | +1.5% | +0.5% | N/A | $0 | $0 |
| **RevenueCat** | $8-$12/1k MTR | App store only | App store only | N/A | $0 | $0 |

**Key Insight:** Stripe cheapest for high volume (2.9%+), but MoR providers hide multi-jurisdiction tax costs in their percentage. At <$85k MRR with multi-jurisdiction needs, Paddle/LemonSqueezy often cheaper total cost of ownership.

---

### 2. Monthly Fees & Minimums

| Provider | Setup Fee | Monthly Minimum | Platform Fee | Features Gated by Revenue |
|----------|-----------|-----------------|--------------|--------------------------|
| **Stripe** | $0 | $0 | $0 | No |
| **Paddle** | $0 | $0 | $0 (5% transaction) | No |
| **LemonSqueezy** | $0 | $0 | $0 (5% transaction) | Email: Free <500 subscribers |
| **Creem** | $0 | $0 | $0 (3.9% transaction) | No |
| **Polar** | $0 | $0 | $0 (4% transaction) | No |
| **RevenueCat** | $0 | $0 | MTR-based usage | Free <$2,500 MTR |

**Decision Rule:** All platforms have $0 entry cost. RevenueCat free tier most generous for early-stage apps (<$2,500/month).

---

### 3. Merchant of Record (MoR) Status

#### What is MoR?

**Definition:** A Merchant of Record is the legal entity selling to end customers. MoR assumes liability for:
- Tax collection, filing, and remittance (VAT/GST/sales tax)
- Fraud and chargeback management
- PCI compliance and data liability
- Customer dispute resolution
- Regulatory compliance across 50+ jurisdictions

The MoR's name appears on customer credit card statements. They hold liability; your company gains simplicity.

#### MoR Status by Provider

| Provider | MoR Status | Tax Coverage | Jurisdictions | Liability Model |
|----------|-----------|--------------|---------------|-----------------|
| **Stripe** | PSP (partial via Managed Payments beta) | Stripe Tax + manual | <50 (API-driven) | You liable |
| **Paddle** | ✅ Full MoR | Automatic | 100+ | Paddle liable |
| **LemonSqueezy** | ✅ Full MoR | Automatic | 50+ | LemonSqueezy liable |
| **Creem** | ✅ Full MoR | Automatic | 50+ | Creem liable |
| **Polar** | ✅ Full MoR (hosted) | Automatic | 50+ | Polar liable |
| **RevenueCat** | ✗ None (reseller) | App store handles | Apple/Google only | App store liable |

**Strategic Implication:**
- **Choose MoR if:** Selling internationally, don't want compliance risk, <$85k MRR with multi-jurisdiction needs
- **Choose PSP if:** Selling primarily US-based, want complete control, >$85k MRR where unbundled Stripe becomes cheaper

#### Cost Comparison: MoR vs. PSP (typical $50k MRR, 3 jurisdictions)

**Paddle:**
- 5% + $0.50 transaction fee = ~$2,500/month
- Total cost: **$2,500**

**LemonSqueezy:**
- 5% + $0.50 transaction fee = ~$2,500/month
- Total cost: **$2,500**

**Stripe + Tax Compliance:**
- 2.9% + $0.30 + Stripe Tax (0.5%) = 3.4% = ~$1,700
- TaxJar subscription: ~$199/month
- CPA filing services: ~$400/month
- Currency conversion: 1% = ~$500
- Total cost: **~$2,800+**

**Verdict:** MoR wins below $85k MRR. At $100k MRR, Stripe unbundled approaches cost parity while offering control.

---

### 4. Subscription Billing Features

| Provider | Recurring Billing | Dunning/Recovery | Usage-Based | Trials | Seat-Based | Prorations |
|----------|------------------|------------------|-------------|--------|-----------|-----------|
| **Stripe** | ✅ Advanced | ✅ Smart Retries | ✅ Meters API | ✅ | ✅ | ✅ |
| **Paddle** | ✅ Advanced | ✅ Built-in | ✅ | ✅ | ✅ | ✅ |
| **LemonSqueezy** | ✅ Solid | ✅ Basic | ✅ | ✅ | ⚠ Limited | ⚠ Basic |
| **Creem** | ✅ Solid | ⚠ Basic | ✅ | ✅ | ⚠ Limited | ✅ |
| **Polar** | ✅ Solid | ⚠ Basic | ✅ | ✅ | ⚠ Limited | ✅ |
| **RevenueCat** | ✅ (App store) | ✅ (App store) | ⚠ Limited | ✅ | ⚠ Limited | ✅ |

**Stripe Leadership:** Stripe Billing named Leader in Forrester Wave (Q1 2025) and Gartner Magic Quadrant (2025). Advanced dunning via Smart Disputes reduces involuntary churn.

---

### 5. One-Time Payments

| Provider | Checkout UX | Payment Methods | Express Checkout | Custom Branding | Mobile-First |
|----------|------------|-----------------|------------------|-----------------|--------------|
| **Stripe** | Excellent | 40+ methods | ✅ (Apple/Google) | ✅ Customizable | ✅ |
| **Paddle** | Excellent | 20+ methods | ✅ | ✅ Localized | ✅ Premium |
| **LemonSqueezy** | Good | 15+ methods | Lemon.js (basic) | ✅ | ✅ |
| **Creem** | Good | 15+ methods | ✅ | ✅ | ✅ |
| **Polar** | Solid | 15+ methods | ✅ | ✅ | ✅ |
| **RevenueCat** | App store only | App store only | N/A | N/A | ✅ (native) |

**Decision Rule:** Paddle/Stripe best for international commerce (localized checkout in 17+ languages). LemonSqueezy simplest for digital products.

---

### 6. Payment Methods Accepted

| Provider | Credit/Debit | ACH | Bank Transfer | Digital Wallets | Regional Methods | PayPal |
|----------|-----------|-----|----------------|-----------------|-----------------|--------|
| **Stripe** | ✅ All | ✅ | ✅ | ✅ Full | ✅ 40+ | ✅ |
| **Paddle** | ✅ All | ✅ | ✅ | ✅ Full | ✅ 20+ | ✅ |
| **LemonSqueezy** | ✅ All | ⚠ | ⚠ | ✅ | ⚠ Limited | ✅ |
| **Creem** | ✅ All | ⚠ | ✅ | ✅ | ⚠ Limited | ⚠ |
| **Polar** | ✅ All | ⚠ | ✅ | ✅ | ⚠ Limited | ⚠ |
| **RevenueCat** | App store | N/A | N/A | N/A | N/A | N/A |

**Strategic Note:** Stripe/Paddle support 40+ payment methods. RevenueCat limited to App Store payment methods (Apple/Google ecosystem only).

---

### 7. Webhook Reliability & Stability

| Provider | Retry Logic | Delivery Guarantee | Out-of-Order Events | Duplicate Prevention | Max Endpoints |
|----------|------------|-------------------|-------------------|-------------------|---------------|
| **Stripe** | 3 days exponential backoff | Best effort | Possible (timestamp order) | Event ID idempotency | 16 per account |
| **Paddle** | 3-5 days exponential backoff | High (MoR model) | Possible | Event ID tracking | Unlimited |
| **LemonSqueezy** | 24-48 hours | Good | Possible | Event ID tracking | Standard |
| **Creem** | 24-48 hours | Good | Possible | Event ID tracking | Standard |
| **Polar** | 24-48 hours | Good | Possible | Event ID tracking | Standard |
| **RevenueCat** | Custom (app store) | High | Possible | Idempotent by default | Unlimited |

**Implementation Rule:** All providers retry with exponential backoff. Always handle out-of-order events and duplicates via event ID tracking. Stripe webhooks are industry standard for reliability.

**Stripe Webhook Specifics (2025 Update):**
- Up to 3-day retry window with exponential backoff
- Support for 16 endpoints per account
- Full versioning support for API changes
- Official documentation: https://docs.stripe.com/webhooks

---

### 8. API & SDK Quality

| Provider | REST API | Webhook Versioning | Official SDKs | Documentation | Rate Limits | GraphQL |
|----------|----------|-------------------|---------------|---------------|-----------|---------|
| **Stripe** | ✅ Mature | ✅ | ✅ 25+ langs | ✅ Extensive | Published | ⚠ Beta |
| **Paddle** | ✅ V2 modern | ✅ | ✅ 6 langs | ✅ Good | Published | ✅ |
| **LemonSqueezy** | ✅ V1 solid | ✅ | ✅ 3 langs | ✅ Good | Published | ⚠ |
| **Creem** | ✅ Modern | ✅ | ✅ 2 langs | ⚠ Growing | Published | ✅ |
| **Polar** | ✅ Modern | ✅ | ✅ 3 langs | ✅ Open source | Published | ✅ |
| **RevenueCat** | ✅ Mature | ✅ | ✅ 8 langs | ✅ Extensive | Published | ⚠ |

**Ranking for Developers:**
1. Stripe: Most mature, 25+ SDKs, extensive documentation
2. Paddle: Modern V2 API, good documentation
3. Polar: Open source, clean API design
4. LemonSqueezy: Solid but smaller community
5. Creem: Growing, good for startups
6. RevenueCat: Excellent for mobile only

---

### 9. Payout Schedule

| Provider | Settlement Time | Payout Frequency | Minimum Payout | Hold Period | Chargeback Reserve |
|----------|-----------------|------------------|---------------|--------------|--------------------|
| **Stripe** | T+1 to T+2 | Daily/Weekly | $0 | 7 days | 0-4 weeks |
| **Paddle** | T+2 to T+3 | Weekly | $0 | 7 days | 0-4 weeks |
| **LemonSqueezy** | T+2 to T+3 | Weekly/Monthly | $0 | 5-7 days | 0-2 weeks |
| **Creem** | Instant | Instant | $0 | Real-time | 0-1 week |
| **Polar** | T+1 to T+2 | Daily/Weekly | $0 | 5 days | 0-2 weeks |
| **RevenueCat** | App store schedule | Weekly | $0 | App store | App store |

**Creem Advantage:** Instant payouts (unique feature), no daily cutoff delays. Useful for high-volume or tight cash flow scenarios.

**Standard Timeline:** Most PSPs: T+1 (1 business day). Most MoRs: T+2 (2 business days). Settlement delays can occur due to:
- Cutoff times (often 2-4 PM local)
- Weekends/bank holidays
- Chargeback holds (0-4 weeks depending on history)

---

### 10. International Support

| Provider | Countries | Multi-Currency | VAT/GST Auto | Bank Transfers | Local Methods | Compliance Docs |
|----------|-----------|----------------|--------------|---------------|--------------|-|
| **Stripe** | 195+ | 135+ | Stripe Tax | ✅ | ✅ 40+ | ✅ Self-serve |
| **Paddle** | 100+ | 29 | ✅ Full | ✅ | ✅ 20+ | ✅ Automatic |
| **LemonSqueezy** | 50+ | 15+ | ✅ Partial | ⚠ | ⚠ 10+ | ✅ Auto via MoR |
| **Creem** | 50+ | 30+ | ✅ Full | ✅ | ⚠ 10+ | ✅ Auto |
| **Polar** | 50+ | 30+ | ✅ Full | ✅ | ⚠ 10+ | ✅ Auto |
| **RevenueCat** | 160+* | *App store | N/A | N/A | N/A | *Limited |

*RevenueCat supports all countries where App Store/Play Store operates, but lacks manual compliance controls.

**International Best Practice:** Paddle (100+ jurisdictions, auto tax) for global SaaS. Creem/Polar emerging as good Stripe alternatives with better compliance automation.

---

### 11. Tax Compliance Deep Dive

#### Stripe Approach (PSP Model)
You own compliance responsibility. Stripe provides tools:
- **Stripe Tax API:** Calculate VAT/GST/sales tax (0.5% added to transaction)
- **Tax Settings Dashboard:** Jurisdiction registration, filing requirements
- **Export Reports:** For quarterly/annual tax filings
- **Manual Filing:** You or your accountant must file returns in each jurisdiction

**Cost:** Stripe Tax (0.5%) + TaxJar ($199/mo) + accountant/filing (~$400-500/mo) = **0.5% + $600+/month**

**Liability:** You remain liable for compliance errors. Audit risk on you.

#### Paddle Approach (MoR Model)
Paddle owns compliance responsibility:
- Registered in 100+ jurisdictions as legal seller
- Automatic VAT/GST/sales tax calculation by jurisdiction
- Automatic filing and remittance to tax authorities
- Generates tax forms (1099-NEC, tax invoices)
- Customer information collection via checkout

**Cost:** 5% + $0.50 per transaction (includes tax handling)

**Liability:** Paddle assumes audit risk. You receive tax documentation.

#### LemonSqueezy Approach (MoR Model, Simplified)
- Registered in 50+ jurisdictions
- Automatic tax calculation and remittance
- Generates tax forms for US merchants
- Simpler than Paddle for indie creators

**Cost:** 5% + $0.50 per transaction

#### Creem & Polar Approach (MoR Model, Emerging)
- Automatic VAT/GST/sales tax in 50+ countries
- Tax form generation
- Built-in compliance for 2025+ regulations

**Cost:** Creem (3.9% + $0.40), Polar (4% + $0.40)

#### Tax Compliance Comparison: $50k MRR, 3 Jurisdictions (US, EU, UK)

**Stripe (Self-managed):**
- Transactions: 2.9% + $0.30 = $1,450
- Stripe Tax API: 0.5% = $250
- TaxJar: $199
- Accountant filing/setup: $400
- **Total: $2,299/month + compliance risk**

**Paddle (Full MoR):**
- Transactions: 5% + $0.50 = $2,500
- Tax handling: Included
- **Total: $2,500/month, zero compliance risk**

**Creem (MoR, Lower Fee):**
- Transactions: 3.9% + $0.40 = $1,950
- Tax handling: Included
- **Total: $1,950/month, zero compliance risk**

**Verdict at $50k MRR:**
1. **Creem** if available in your regions (3.9% + tax included)
2. **Paddle** if Creem unavailable (5% all-in, proven)
3. **Stripe** only if >$85k MRR and want control

---

### 12. SaaS Billing Features

| Provider | Usage Metering | Seat Licensing | Proration Logic | Revenue Recognition | Dunning | Upgrade/Downgrade |
|----------|----------------|----------------|-----------------|--------------------|---------|-|
| **Stripe** | ✅ Meters API | ✅ | ✅ Prorata | ✅ Revenue Rec | ✅ Smart Retries | ✅ Full |
| **Paddle** | ✅ | ✅ | ✅ | ✅ | ✅ Dunning | ✅ Full |
| **LemonSqueezy** | ✅ | ⚠ Limited | ⚠ Basic | ⚠ Basic | ✅ | ⚠ Limited |
| **Creem** | ✅ | ⚠ Limited | ✅ | ⚠ | ✅ | ✅ |
| **Polar** | ✅ | ⚠ Limited | ✅ | ✅ | ✅ | ✅ |
| **RevenueCat** | ✅ (App store) | ✅ (In-app) | ✅ | ✅ | ✅ (App store) | ✅ (In-app) |

**Stripe's SaaS Moat:** Meters API (real-time usage tracking), Smart Retries (reduce involuntary churn), Revenue Recognition (GAAP compliance). No competitor matches this depth yet.

---

### 13. React/Next.js Integration Libraries & DX

#### Stripe
```javascript
// next/payment integration
import { Elements, CardElement, useStripe } from '@stripe/react-stripe-js';

// 1-line setup
const stripe = useStripe();
```
- **Official libraries:** @stripe/react-stripe-js, @stripe/next-js
- **DX Score:** 10/10 (industry standard)
- **Starter templates:** Multiple (Vercel, Clerk, Auth0)

#### LemonSqueezy
```javascript
// next/script integration
import Script from 'next/script';

// Load Lemon.js
<Script src="https://app.lemonsqueezy.com/checkout.js" afterInteractive />
```
- **Official support:** Lemon.js + Next.js Script component (recommended)
- **Environment variables:** LEMONSQUEEZY_API_KEY, LEMONSQUEEZY_STORE_ID, LEMONSQUEEZY_WEBHOOK_SECRET
- **DX Score:** 8/10 (simple for indie projects, less SDK depth)
- **GitHub example:** lmsqueezy/nextjs-billing (official)

#### Paddle
```javascript
// Lazy-loaded checkout component
import dynamic from 'next/dynamic';

const PaddleCheckout = dynamic(() => import('@paddle/checkout'));
```
- **Official React SDK:** @paddle/checkout (v0 to v1 migration ongoing)
- **Integration:** Lazy-loaded for performance
- **DX Score:** 8/10 (good, but SDK undergoes changes)
- **Starter kits:** MakerKit (Next.js + Paddle integration)

#### Polar
```javascript
// React/Next.js SDK
import { PolarCheckout } from '@polar-sh/checkout';

<PolarCheckout productId="..." />
```
- **Official library:** @polar-sh/checkout (React wrapper)
- **DX Score:** 7/10 (growing, open source, API-first design)
- **Documentation:** Open source on GitHub (polarsource/polar)

#### Creem
```javascript
// Embed checkout
import { CreemCheckout } from '@creem-io/react';
```
- **Official library:** @creem-io/react (new)
- **DX Score:** 7/10 (emerging, still building developer experience)

#### RevenueCat
```javascript
// Swift/Kotlin only (mobile-first)
import RevenueCat

let offerings = try await Purchases.shared.offerings()
```
- **Official libraries:** Swift (iOS), Kotlin (Android), Flutter, React Native
- **DX Score:** 9/10 for mobile, N/A for web
- **No web integration:** (app-only platform)

#### Multi-Gateway Starter Kits
Several Next.js SaaS boilerplates support 2-3 providers:
- **SaaSBold:** Stripe, Paddle, LemonSqueezy all integrated
- **staarter.dev:** Multiple payment gateway support
- **supastarter:** Comparative integrations for easy switching

**Best DX for Next.js:** Stripe (mature, @stripe/react-stripe-js) or LemonSqueezy (simplest, Lemon.js + Script).

---

## PART 2: MERCHANT OF RECORD DEEP DIVE

### What is a Merchant of Record?

A Merchant of Record (MoR) is the legal entity that appears on a customer's credit card statement. The MoR assumes:

1. **Tax Liability**
   - Collects applicable VAT, GST, sales tax
   - Files and remits taxes to authorities in each jurisdiction
   - Maintains compliance across 50-100+ jurisdictions
   - Generates tax documentation (1099-NEC, tax invoices)

2. **Fraud & Chargeback Liability**
   - Absorbs fraud losses
   - Manages chargeback disputes
   - Implements PCI compliance
   - Maintains fraud detection systems

3. **Regulatory Liability**
   - Audit risk for tax compliance
   - Data protection (GDPR, CCPA compliance)
   - Payment Card Industry compliance
   - Jurisdiction-specific regulations

### Why Use a MoR?

**For Sellers:**
- Eliminate tax compliance burden (major headache for international sales)
- Reduce legal/audit risk
- Simplify accounting
- Enable global sales without legal entity in each jurisdiction

**For Platforms:**
- De-risk seller compliance (especially important for marketplaces)
- Enable 1099 contractor payment networks
- Simplify vendor payouts

### MoR vs. PSP (Payment Service Provider)

| Dimension | MoR (Paddle, LemonSqueezy) | PSP (Stripe) |
|-----------|---------------------------|------------|
| **Appears on Statement** | Paddle/LemonSqueezy | Your Business Name |
| **Tax Liability** | MoR liable | You liable |
| **Compliance Risk** | MoR assumes | You assume |
| **Cost Structure** | 5-8% all-in | 2.9% + unbundled costs |
| **Best For** | <$85k MRR, multi-jurisdictions | >$85k MRR, single region or control-focused |
| **Customer Experience** | Generic checkout (e.g., "Paddle Inc") | Branded checkout |
| **Invoice** | MoR issues invoice | You issue invoice |

### Stripe's MoR Attempt: Managed Payments (2025 Beta)

**Status:** Private preview, launching summer 2025

**What it does:**
- Simplified tax compliance (handles VAT/sales tax)
- Fraud prevention
- Customer support

**Limitations:**
- Not a full MoR (Stripe still not legally liable)
- You retain compliance responsibility for complex scenarios
- Still in beta—production readiness unknown

**Verdict:** Stripe Managed Payments is Stripe's incremental step toward MoR features, but doesn't match Paddle's maturity or full liability assumption.

### Provider MoR Comparison

#### Paddle: Enterprise MoR
- **Jurisdictions:** 100+
- **Liability:** Full (Paddle is legal seller)
- **Tax Filing:** Automatic to all jurisdictions
- **Customer Portal:** Advanced (refund management, subscription changes)
- **Checkout Languages:** 17+ (localized for each region)
- **Chargeback Management:** Integrated, expert support
- **Use Case:** Ideal for SaaS, multi-region sellers, complex subscriptions
- **Cost:** 5% + $0.50 per transaction
- **When to use:** Scale-up SaaS ($10k-$85k MRR), international products, subscription management required

#### LemonSqueezy: Indie Creator MoR
- **Jurisdictions:** 50+
- **Liability:** Full (LemonSqueezy is legal seller)
- **Tax Filing:** Automatic (US-focused, good for other regions)
- **Customer Portal:** Basic (simpler than Paddle)
- **Checkout:** Simple, content-creator focused
- **Chargeback Management:** Basic
- **Use Case:** Ideal for digital products, indie projects, courses
- **Cost:** 5% + $0.50 per transaction (+ 1.5% intl, +0.5% subscription, +1.5% PayPal)
- **When to use:** Solo entrepreneurs, digital product sales, minimal complexity

#### Creem: Startup MoR (Emerging)
- **Jurisdictions:** 50+
- **Liability:** Full
- **Tax Filing:** Automatic (50+ countries VAT/GST/tax)
- **Payouts:** **Instant** (unique advantage)
- **Features:** Payment splits (for teams/affiliates), advanced fraud detection, AI insights
- **Use Case:** Startups, remote teams, multi-founder revenue splits
- **Cost:** 3.9% + $0.40 per transaction (lowest fee of all MoRs)
- **When to use:** Startups with tight cash flow (instant payouts), need revenue splitting, want lowest fees
- **Funding Status:** €1.8M pre-seed (2025), 10 months to €930k ARR (strong adoption)

#### Polar: Open-Source MoR (Emerging)
- **Jurisdictions:** 50+
- **Liability:** Full (when using hosted service)
- **Unique:** Apache 2.0 open source (can self-host, lose MoR benefits)
- **Hosting:** Recommended to use hosted for full MoR
- **Tax Filing:** Automatic
- **Use Case:** Developer-first, open-source projects, indie SaaS
- **Cost:** 4% + $0.40 per transaction (20% cheaper than Paddle per their claim)
- **Community:** 36+ contributors, active GitHub
- **When to use:** Teams wanting transparency/open source, cost-conscious devs, custom integrations

---

## PART 3: MOBILE IN-APP PURCHASES & REVENUECAT

### App Store Commission Structure (2025-2026)

#### Apple App Store (iOS, iPadOS, macOS)

**Standard Rate:** 30% commission on all in-app purchases (auto-renewing subscriptions)

**Small Business Program:** 15% commission if annual revenue <$1M from IAP
- Applies per-app, per-region
- Must opt in
- Resets January 1 each year

**Subscription Tiers:**
- **Year 1:** 30% commission
- **Year 2+:** 15% commission (if customer subscribed for 12+ months)

**Anti-Steering Changes (2025):**
- As of April 30, 2025, US developers can send customers to external web payment links to complete purchases
- Avoids 30% commission for link-based purchases
- Applies to US-based users only (other regions still restricted)

#### Google Play (Android)

**Standard Rate:** 30% commission on all in-app purchases

**User Acquisition Campaign:** 15% commission if acquired via user acquisition campaigns (limited scope)

**Subscription Tiers:**
- **Year 1:** 30% commission
- **Year 2+:** 15% commission (automatic)

**2025 Changes:**
- Similar external link allowances being explored
- More flexible billing options

### RevenueCat: In-App Purchase Aggregator

**What it does:** Wrapper around Apple/Google IAP APIs, providing:
- Unified subscription management across iOS/Android
- Remote config (pricing, offerings changes without app update)
- Cross-platform subscription eligibility
- Subscriber analytics
- Revenue reporting

**RevenueCat Pricing:**

| MTR (Monthly Tracked Revenue) | Free Tier | Starter | Pro |
|------|-----------|---------|-----|
| <$2,500 | ✅ Free | - | - |
| $2,500-$10,000 | - | $8 per $1,000 MTR | - |
| >$10,000 | - | - | $12 per $1,000 MTR |

**Example Calculation:**
- App earning $5,000/month in gross revenue (before app store commission)
- Starter plan: $8 × 5 = $40/month (RevenueCat fee)
- Your net: $5,000 - (30% to Apple/Google) - $40 (RevenueCat) = ~$3,460

**Key Insight:** RevenueCat fee calculated on gross revenue (before app store cuts), not net payout. Important for cash flow planning.

### RevenueCat Competitive Advantage vs. Direct IAP

**Direct App Store APIs:**
- ✅ Zero platform fees (only pay app store commission)
- ❌ Manual subscription management per platform
- ❌ No cross-platform subscription eligibility
- ❌ Limited analytics/reporting
- ❌ Remote config requires app updates

**RevenueCat:**
- ✅ Remote config (change pricing/offerings without update)
- ✅ Unified subscriber view (iOS + Android + Web)
- ✅ Advanced analytics (cohort analysis, LTV metrics)
- ✅ Cross-platform eligibility (one subscription = all platforms)
- ❌ $40-120/month fee (but worth it for cross-platform apps)

**When to use RevenueCat:**
- Multi-platform apps (iOS + Android + Web)
- Complex subscription offerings
- Frequent pricing/offering changes
- Need advanced subscriber analytics

**When to use Direct IAP:**
- iOS-only or Android-only apps
- Simple single-tier subscriptions
- Cost-conscious (very low monthly revenue)

---

## PART 4: EMERGING PLATFORMS — POLAR & CREEM

### Polar.sh: Open-Source Monetization (2025 Status)

**What is it?** Developer-centric billing platform, fully open source under Apache 2.0 license.

**Positioning:** "Turn your software into a business" for indie hackers and small SaaS.

**Key Differentiators:**
1. **Open Source:** Can audit code, self-host (loses MoR benefits though), 36+ GitHub contributors
2. **API-First Design:** Everything via REST/GraphQL (no-code dashboard secondary)
3. **Developer Target:** Built by developers, for developers
4. **Bundled Offering:** Like other MoRs, includes tax compliance, product management, access control
5. **Pricing:** 4% + $0.40 (claims 20% cheaper than Paddle)

**Functionality:**
- Subscriptions, one-time payments, usage-based billing
- Automatic tax handling (50+ countries)
- Webhook support
- Customer portal
- Revenue recovery
- Analytics

**Adoption Status (2025):**
- Active development on GitHub (polarsource/polar)
- Growing community of indie developers
- Not yet at Paddle's scale, but gaining traction
- Funded and actively developed

**Hosted vs. Self-Hosted:**
- **Hosted (Recommended):** Get full MoR benefits, automatic tax compliance
- **Self-Hosted:** Can run your own instance, but lose MoR liability assumption (you'd need own tax compliance setup)

**When to choose Polar:**
- ✅ Want open-source transparency
- ✅ Want 20% fee savings vs. Paddle
- ✅ Prefer API-first architecture
- ✅ Don't need Paddle's SaaS-specific features
- ❌ Avoid if: Need mature support, complex dunning

---

### Creem.io: AI-Native Financial OS (2025 Status)

**What is it?** Emerging financial OS/payment platform targeting AI-native startups and fast-growing companies.

**Positioning:** "Stripe for AI startups" with built-in revenue splitting, compliance, and fraud detection.

**Key Differentiators:**
1. **Revenue Splits:** Automated multi-party revenue sharing (founders, investors, contractors)
2. **Lowest Fees:** 3.9% + $0.40 (lowest of all MoRs)
3. **Instant Payouts:** Unique feature (not T+2, but real-time)
4. **AI-Powered:** Fraud detection, insights dashboard
5. **Startup-First:** Designed for remote teams, co-founder payments, contractor payments

**Functionality:**
- Subscriptions, one-time payments, usage-based billing
- Automatic tax compliance (50+ countries VAT/GST)
- Payment splits (auto-distribute revenue)
- Fraud detection + chargeback protection
- Instant payouts (no daily cutoff delays)

**Adoption Status (2025):**
- Launched ~2024, already €930k ARR (10 months post-launch)
- €1.8M pre-seed funding (Practica Capital led, Antler supported)
- No sales team—growth via word-of-mouth
- **Roadmap:** Virtual IBANs, virtual accounts (2026)

**Competitive Advantage:**
- **Instant payouts:** Game-changer for high-volume or tight cash flow
- **Revenue splits:** Unique (designed for co-founder/affiliate payments)
- **Lowest fees:** 3.9% + $0.40
- **Strong momentum:** €930k ARR, €1.8M funding in 10 months

**When to choose Creem:**
- ✅ Need instant payouts (no daily delays)
- ✅ Have multiple revenue recipients (founders, affiliates, contractors)
- ✅ Want lowest fee tier (3.9%)
- ✅ Targeting AI/tech audience
- ❌ Avoid if: Need mature support (newer platform), in conservative industries

**Creem vs. Polar (both emerging):**

| Dimension | Creem | Polar |
|-----------|-------|-------|
| Fees | 3.9% + $0.40 | 4% + $0.40 |
| Payouts | **Instant** | T+1 to T+2 |
| Revenue Splits | ✅ Yes (unique) | No |
| Open Source | ❌ No | ✅ Yes (Apache 2.0) |
| Target Market | AI startups, remote teams | Indie developers, SaaS |
| Funding Status | €1.8M pre-seed | Self-funded/bootstrapped |
| Maturity | Very new (10 months) | Young but growing |

---

## PART 5: DECISION LOGIC & RECOMMENDATION TREES

### Decision Tree 1: Choose Your Payment Model (MoR vs. PSP)

```
START
│
├─ Do you sell internationally (2+ regions with tax requirements)?
│  ├─ YES → Go to Decision Tree 2 (MoR evaluation)
│  └─ NO → Go to Decision Tree 3 (PSP: Stripe/others)
│
├─ If YES: What's your monthly revenue?
│  ├─ <$20k MRR → MoR (Creem/Polar/LemonSqueezy) [lowest cost]
│  ├─ $20k-$85k MRR → MoR (Paddle/Creem) [simplicity > cost]
│  ├─ >$85k MRR → Calculate both models; likely PSP wins on cost
│  └─ >$250k MRR → PSP (Stripe) definitely wins, get custom pricing
│
└─ If NO: Use Stripe (PSP); no compliance complexity
```

### Decision Tree 2: Which MoR? (Paddle vs. LemonSqueezy vs. Creem vs. Polar)

```
START: Choosing a Merchant of Record
│
├─ What's your use case?
│
├─ SaaS subscriptions (B2B) → Paddle
│  │  (Advanced dunning, seat licensing, revenue recognition)
│  │  Cost: 5% + $0.50
│  │  Example: Project management tool, analytics SaaS
│  │
│  └─ If SaaS + need instant payouts → Creem
│     (Instant payouts + splits unique to Creem)
│     Cost: 3.9% + $0.40 (cheaper!)
│     Example: Startup SaaS with co-founder revenue split
│
├─ Digital products/indie creator → LemonSqueezy
│  │  (Simplest UX, storefronts, no-code)
│  │  Cost: 5% + $0.50 + extras
│  │  Example: Online course, e-book, template store
│  │
│  └─ If indie + want open-source → Polar
│     (API-first, transparent, developer-centric)
│     Cost: 4% + $0.40
│     Example: Developer tool, indie SaaS, open-source monetization
│
├─ Fast-growing startup (AI/tech) → Creem
│  │  (Revenue splits, instant payouts, fraud detection)
│  │  Cost: 3.9% + $0.40 (lowest!)
│  │  Example: AI API, developer tools, remote-first startup
│  │
│  └─ If startup + control/transparency → Polar
│     (Open source, API-first, cost savings)
│     Cost: 4% + $0.40
│
└─ Complex compliance needs → Paddle (100+ jurisdictions)
   (Most mature MoR, handles EU complexities best)
   Cost: 5% + $0.50
```

### Decision Tree 3: Which PSP? (Stripe only, practically)

```
START: Choosing a Payment Service Provider
│
├─ Is Stripe available in your region?
│  ├─ YES → Use Stripe (industry standard)
│  └─ NO → Use Paddle (MoR fallback, works everywhere)
│
├─ Do you need advanced SaaS features?
│  ├─ Usage-based billing, seats, prorations → Stripe (Meters API unmatched)
│  ├─ Simple subscriptions → LemonSqueezy/Creem/Polar
│  └─ Moderate complexity → Paddle (good SaaS features without Stripe depth)
│
├─ Regional focus?
│  ├─ US-only → Stripe (cheapest)
│  ├─ Europe/UK + US → Stripe + Stripe Tax (or MoR)
│  └─ 5+ regions → MoR (Paddle/Creem) is cheaper
│
└─ Technical depth?
   ├─ High (customize everything) → Stripe
   ├─ Moderate → Paddle (good APIs, great docs)
   └─ Low (wants simplicity) → LemonSqueezy
```

### Decision Tree 4: Mobile In-App Purchases

```
START: Monetizing mobile app subscriptions
│
├─ Is your app mobile-only?
│  ├─ YES (iOS/Android only) → RevenueCat
│  │  (Cross-platform subscription management)
│  │  Cost: $8-12 per $1,000 MTR (worth it for multi-platform)
│  │
│  └─ NO (Web + Mobile) → Evaluate web first, then layer mobile
│     ├─ Web via Stripe/Paddle/Creem → Use their IAP integrations
│     └─ Mobile via RevenueCat (recommended for cross-platform)
│
├─ Revenue tier?
│  ├─ <$2,500/month → RevenueCat free tier
│  ├─ $2,500-10,000/month → RevenueCat Starter ($8/1k)
│  └─ >$10,000/month → RevenueCat Pro ($12/1k)
│
└─ Can you accept external payment links (US users)?
   ├─ YES (April 2025+) → Consider Stripe external links for US
   │  (Avoid 30% Apple commission for US users)
   │  (RevenueCat still best for simplicity)
   │
   └─ NO (other regions) → RevenueCat only way to cross-platform
```

### Decision Tree 5: React/Next.js Integration Complexity

```
START: Building payments into Next.js app
│
├─ How much customization needed?
│
├─ Maximum control + features → Stripe
│  │  Library: @stripe/react-stripe-js
│  │  Time: 1-2 days (mature docs)
│  │  Use: Vercel starter kits, official examples
│  │
│  └─ If SaaS billing required → Add Stripe Billing layer
│     (Meters API for usage, Smart Retries for dunning)
│
├─ Quick launch, simpler setup → LemonSqueezy
│  │  Method: Lemon.js + next/script (recommended)
│  │  Time: 2-4 hours
│  │  Use: next/script afterInteractive strategy
│  │
│  └─ Good for: Indie projects, quick MVP
│
├─ Professional SaaS look → Paddle
│  │  Library: @paddle/checkout (React SDK)
│  │  Time: 1-2 days
│  │  Use: MakerKit starter template
│  │  Pro: Localized checkout in 17 languages
│
├─ Open-source priority → Polar
│  │  Library: @polar-sh/checkout
│  │  Time: 1 day (API-first, cleaner)
│  │  Use: GitHub integration examples
│
└─ Multi-provider support → Use boilerplate
   Recommended: SaaSBold (Stripe + Paddle + LemonSqueezy)
   Time: 0 (starter kit includes all 3)
```

---

## PART 6: COST COMPARISON SCENARIOS

### Scenario 1: Indie Digital Product ($10k MRR, Global)

**Monthly Revenue:** $10,000
**Regions:** 5 (US, UK, Canada, Australia, Germany)
**Model:** One-time product sales + email marketing

#### Option A: Stripe + Tax Compliance
- Transactions (2.9% + $0.30): $290
- Stripe Tax (0.5%): $50
- TaxJar ($199 flat): $199
- Accountant filing: $100
- **Total: $639/month**
- Liability: On you

#### Option B: LemonSqueezy (MoR)
- Transactions (5% + $0.50): $500
- Email marketing: Free (<500 subscribers)
- **Total: $500/month**
- Liability: On LemonSqueezy

#### Option C: Creem (MoR)
- Transactions (3.9% + $0.40): $390
- Email marketing: N/A (not offered)
- **Total: $390/month**
- Liability: On Creem

**Winner:** Creem ($390) < LemonSqueezy ($500) < Stripe ($639)

**Verdict:** Use Creem for lowest cost. If need email, use LemonSqueezy.

---

### Scenario 2: SaaS Subscription ($50k MRR, 2 Regions US + EU)

**Monthly Revenue:** $50,000
**Model:** Monthly subscription (annual billing 20%, monthly 80%)
**Customers:** 500 (averaging $100/month)

#### Option A: Stripe + Billing + Tax
- Transactions (2.9% + $0.30): $1,450
- Stripe Billing (no direct fee): $0
- Stripe Tax (0.5%): $250
- TaxJar: $199
- Accountant (quarterly): $300
- Smart Disputes (if chargebacks): 30% of recovery
- **Total: ~$2,200/month**
- Liability: On you
- Features: Meters API ✅, Smart Retries ✅, Revenue Recognition ✅

#### Option B: Paddle (MoR)
- Transactions (5% + $0.50): $2,500
- Tax handling: Included
- Dunning: Included
- **Total: $2,500/month**
- Liability: On Paddle
- Features: Dunning ✅, 100+ jurisdictions ✅, SaaS-optimized ✅

#### Option C: Creem (MoR)
- Transactions (3.9% + $0.40): $1,950
- Tax handling: Included
- Dunning: Basic
- **Total: $1,950/month**
- Liability: On Creem
- Features: Revenue splits ✅, instant payouts ✅

**Winner at $50k:** Creem ($1,950) < Stripe ($2,200) < Paddle ($2,500)

**But consider:**
- If need advanced dunning/revenue recognition → Stripe ($2,200 justified)
- If want SaaS maturity + Paddle's features → Paddle ($300 more for peace of mind)
- If want lowest cost + emerging platform → Creem ($1,950, but newer)

**Verdict:** Stripe if need Meters API + Smart Retries. Paddle if need maturity + EU complexity. Creem if cost/instant payouts priority.

---

### Scenario 3: Mobile App (iOS + Android, $30k MRR)

**Monthly Revenue:** $30,000 (gross, before app store cut)
**Platform:** iOS + Android (50/50 split)
**Model:** Auto-renewing subscription

#### Option A: Direct App Store APIs (No wrapper)
- Apple commission (30% year 1, 15% year 2+): ~$3,750 + $1,875
- Platform fee: $0
- Revenue management: Manual across iOS/Android
- Analytics: Limited
- Remote config: Requires app update
- **Total: $0 platform, but $3,750-5,625/month to app stores**
- Your net: ~$24,375/month (year 1) or $25,875/month (year 2+)

#### Option B: RevenueCat (Recommended)
- Apple commission: ~$4,500 (same as direct)
- Google commission: ~$4,500 (same as direct)
- RevenueCat fee: $30k × $12/1000 = $360/month (Pro tier)
- Remote config: ✅ (change offerings without update)
- Cross-platform eligibility: ✅ (one sub = both platforms)
- Analytics: ✅ Advanced
- **Total: $360 platform fee + app store commissions**
- Your net: ~$21,000/month (after RevenueCat + commissions)

**Comparison:**
- Direct APIs: More revenue ($24-25k), but manual management, limited insights
- RevenueCat: $360 fee + better ops (remote config, analytics, cross-platform)

**Verdict:** RevenueCat if cross-platform. Direct APIs if iOS-only and minimal pricing changes.

---

### Scenario 4: Scaling SaaS ($200k MRR, Global, Complex Billing)

**Monthly Revenue:** $200,000
**Regions:** 10+
**Model:** Tiered subscriptions + usage-based overage
**Features Needed:** Seat licensing, prorations, revenue recognition

#### Option A: Stripe (Full Stack)
- Transactions (2.9% + $0.30): $5,800
- Stripe Tax (0.5%): $1,000
- Stripe Billing (no direct fee): $0
- Usage tracking (Meters): Included
- Smart Retries/dunning: Included
- Revenue Recognition module: Included
- Accountant (quarterly): $300
- Custom rate negotiation (at this MRR, possible): -5% to -15% discount
- **Estimated total with negotiated rate: $3,000-5,000/month**
- Liability: On you
- Features: Everything ✅

#### Option B: Paddle (MoR)
- Transactions (5% + $0.50): $10,000
- Tax handling: Included
- Dunning: Included
- SaaS features: ✅
- Custom pricing (at this scale, likely): Possible negotiation
- **Estimated with negotiation: $7,000-8,000/month**
- Liability: On Paddle

#### Option C: Creem (MoR)
- Transactions (3.9% + $0.40): $7,800
- Tax handling: Included
- Revenue splits: Included
- Instant payouts: ✅
- Custom negotiation: Unknown (too early stage)
- **Total: ~$7,800/month**
- Liability: On Creem

**Winner at $200k:** Stripe with negotiated rate ($3,000-5,000) << Creem ($7,800) < Paddle ($7,000-8,000)

**Verdict:** At $200k MRR, Stripe wins even accounting for tax complexity. Negotiate custom rate (most companies get 2.2% + $0.30 or better at this scale).

---

## PART 7: IMPLEMENTATION CHECKLIST & DECISION MATRIX

### Quick Decision Matrix

```
╔════════════════════════════════════════════════════════════════════════════════╗
║ Use Case                          │ Best Provider    │ Cost (Typical)          ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ Digital Products, Indie (<$10k)   │ Creem            │ 3.9% + $0.40            ║
║ Digital Products, Indie (<$20k)   │ LemonSqueezy     │ 5% + $0.50              ║
║ SaaS, <$50k MRR, 2+ regions       │ Creem/Paddle     │ 1.9-2.5% effective      ║
║ SaaS, $50-100k MRR                │ Stripe or Paddle │ 2.2-5% effective        ║
║ SaaS, >$200k MRR                  │ Stripe (custom)  │ 2.0-2.2% negotiated     ║
║ Complex billing (usage-based)      │ Stripe           │ 2.9% + Meters API       ║
║ Mobile subscriptions (iOS/Android) │ RevenueCat       │ $8-12 per $1k MTR       ║
║ Open-source monetization           │ Polar            │ 4% + $0.40              ║
║ Startup with revenue splits        │ Creem            │ 3.9% + $0.40            ║
║ Enterprise, custom needs           │ Stripe           │ Negotiated (<2%)        ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

### Implementation Checklist

#### Phase 1: Research & Decision (Week 1)
- [ ] Determine use case (SaaS vs. digital products vs. mobile)
- [ ] Calculate current/projected monthly revenue
- [ ] Identify all regions you sell to or plan to sell to
- [ ] List required features (subscriptions, usage-based, dunning, etc.)
- [ ] Run through Decision Trees above
- [ ] Create cost comparison spreadsheet (use scenarios above)

#### Phase 2: Provider Evaluation (Week 1-2)
- [ ] Sign up for free tier or trial on top 2 providers
- [ ] Review API documentation quality
- [ ] Check webhook reliability (sandbox testing)
- [ ] Evaluate dashboard UX
- [ ] Contact sales (if applicable) for guidance
- [ ] Read customer reviews on Capterra/G2

#### Phase 3: Technical Integration (Week 2-3)
- [ ] Review official SDK/library quality
- [ ] Test webhook signature verification
- [ ] Build sample integration (hello world)
- [ ] Test payment flow (use test card numbers)
- [ ] Verify tax calculation (for MoR: check jurisdiction coverage)
- [ ] Test refund/chargeback handling

#### Phase 4: Launch (Week 3-4)
- [ ] Set up production account
- [ ] Configure webhooks for all events
- [ ] Set payout schedule
- [ ] Enable tax compliance (if MoR, verify jurisdiction setup)
- [ ] Test with real transaction (small amount)
- [ ] Monitor first week closely
- [ ] Set up admin alerts for failures

---

## PART 8: 2025-2026 TRENDS & OUTLOOK

### Stripe's Evolution
- **Managed Payments beta** (summer 2025): Incremental MoR features, not full replacement for Paddle/LemonSqueezy
- **Meters API maturity:** Usage-based billing becoming table-stakes
- **Custom pricing:** Negotiate below 2.2% at $200k+ MRR
- **Trend:** Remaining dominant but facing stronger competition from MoR solutions

### MoR Market Consolidation
- **Winners:** Paddle (proven SaaS leader), Creem (fastest growth), Polar (open-source momentum)
- **Pressure:** LemonSqueezy facing competition from lower-cost options (Creem 3.9% vs 5%)
- **Opportunity:** Stripe Managed Payments still in beta; if it matures, could consolidate market

### Emerging Platform Adoption
- **Creem:** €1.8M funding, €930k ARR in 10 months = strong product-market fit for startups
- **Polar:** Growing community, 36+ contributors, gaining indie developer traction
- **Trend:** Both challenging Paddle/LemonSqueezy via lower fees + modern developer experience

### In-App Purchase Landscape (Post-Epic v. Apple)
- **US External Links:** April 2025 ruling allows Stripe/web payments for US users
- **Other Regions:** Apple/Google still require 30% commission
- **RevenueCat Impact:** Remote config + cross-platform eligibility remain valuable despite reduced commission option
- **Trend:** Hybrid models emerging (web links for US, in-app for international)

### Tax Compliance Automation
- **Creem/Polar/Paddle:** All investing in automated compliance
- **EU DMA Updates:** June 2025 Apple EU ruling creating three-fee system (entitlements + commissions)
- **Trend:** MoR providers gaining advantage as compliance gets more complex

---

## Sources & References

### Official Documentation
- [Stripe Pricing](https://stripe.com/pricing)
- [Stripe Webhooks](https://docs.stripe.com/webhooks)
- [Paddle Pricing](https://www.paddle.com/pricing)
- [LemonSqueezy Docs](https://docs.lemonsqueezy.com/)
- [RevenueCat Pricing](https://www.revenuecat.com/pricing/)
- [Polar Documentation](https://docs.polar.sh/)
- [Creem Pricing](https://www.creem.io/pricing)

### Comparison Resources
- [LemonSqueezy vs Stripe Analysis](https://saasfeecalc.com/)
- [Paddle vs Stripe Detailed Comparison](https://unibee.dev/blog/paddle-vs-stripe-the-ultimate-2025-comparison/)
- [SaaS Payment Solutions Overview](https://www.ratiotech.com/blog/saas-subscription-billing-solutions)
- [Payment Gateway Comparison](https://fungies.io/top-payment-gateways-saas/)

### Technical Integration
- [LemonSqueezy Next.js Integration](https://github.com/lmsqueezy/nextjs-billing)
- [Stripe React Integration](https://stripe.com/)
- [Paddle Documentation](https://www.paddle.com/)
- [Polar Open Source](https://github.com/polarsource/polar)

### Current News & Updates
- [Creem €1.8M Funding](https://techfundingnews.com/creem-grabs-1-8m-stripe-for-ai-financial-os/)
- [LemonSqueezy 2026 Updates](https://www.lemonsqueezy.com/blog/2026-update)
- [Apple June 2025 EU Update](https://www.revenuecat.com/blog/growth/apple-eu-dma-update-june-2025/)

---

## Final Recommendation Summary

### For Most Founders
**Use Stripe** if:
- Building SaaS with complex billing (usage-based, seat licensing)
- US-focused, minimal international complexity
- Want maximum control and API depth
- Revenue >$200k MRR

**Use Paddle** if:
- SaaS with subscription focus
- Selling to 2-50 jurisdictions
- Want proven MoR maturity
- Revenue $20k-$200k MRR

**Use LemonSqueezy** if:
- Selling digital products (courses, templates, e-books)
- Solo entrepreneur or small team
- Want simplicity over control
- Revenue <$50k MRR

**Use Creem** if:
- Fast-growing startup with co-founders/team
- Need instant payouts or revenue splitting
- Want lowest fees (3.9%)
- Revenue $10k-$100k MRR

**Use Polar** if:
- Want open-source transparency
- Building indie SaaS
- Prefer API-first architecture
- Revenue <$100k MRR

**Use RevenueCat** if:
- Mobile-only app (iOS + Android)
- Need cross-platform subscription management
- Require remote config for pricing changes
- Revenue $2.5k-$100k+ MRR

---

**Document Version:** February 2026
**Last Updated:** 2026-02-19
**Data Sources:** Official provider documentation, independent comparisons, 2025-2026 pricing

## Related References
- [PCI-DSS Compliance](./35-compliance-pci-dss.md) — Payment card data security requirements
- [Security Essentials](./30-security-essentials.md) — PCI tokenization and encryption
- [Real-World Cost Traps](./40-cost-traps-real-world.md) — Hidden payment processing fees
- [Email Services](./18-email-services.md) — Receipt and invoice delivery
- [Compliance Provider Matrix](./38-compliance-provider-matrix.md) — Payment provider compliance certifications

<!-- PRICING_STABILITY: HIGH_VOLATILITY | Updated: 2026-03-03 | Cloud/SaaS pricing changes quarterly. Verify current pricing at provider websites before recommending. -->
