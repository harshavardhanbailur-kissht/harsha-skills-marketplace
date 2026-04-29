# E-Commerce & Conversion Reference

## Cart Abandonment

### Baseline Statistics

**Average Cart Abandonment Rate**: 70.22%
- Source: Baymard Institute (50 studies, 2006-2025)
- **$260 billion recoverable** through better design

### Abandonment Causes (Ranked)

| Reason | % of Abandonments |
|--------|-------------------|
| Extra costs revealed late | 48% |
| Account creation required | 19-26% |
| Complex checkout process | 18-22% |
| Couldn't calculate total upfront | 17% |
| Website errors/crashes | 13% |
| Didn't trust with payment info | 12% |
| Too long delivery time | 11% |

### Recovery Strategies

**Highest Impact**:
1. Show all costs upfront (shipping, taxes, fees)
2. Guest checkout option
3. Simplify to single-page checkout
4. Cart persistence across sessions

---

## Checkout Optimization

### Form Field Count

**Optimal**: 12-14 form elements
**Average e-commerce**: 23.48 fields

**Impact Per Unnecessary Field**:
- 8-50% conversion decrease per field
- Exponential negative effect

### Specific Field Impacts

| Field | Conversion Impact |
|-------|-------------------|
| Phone number (optional) | -48-52% |
| Date of birth | -30-40% |
| Company name | -20-30% |
| Fax number | Why? Just no. |

### Progress Indicators

**Perception Study Results** (χ²(3)=31.57, p<0.001):

| Progress Pattern | Breakoff Rate |
|------------------|---------------|
| Fast-to-slow | **21.8%** (worst) |
| Consistent | 18.2% |
| Slow-to-fast | 15.4% |
| **Accelerating** | **11.3%** (best) |

**Implementation**: Weight early steps heavier visually.

### Checkout Flow Structure

**Best Practice**:
```
1. Cart Review (with edit capability)
2. Shipping Address (guest-friendly)
3. Delivery Options (with cost visible)
4. Payment
5. Review & Confirm
```

**Single Page Alternative**: All steps visible, progressive completion.

---

## Form Design

### Inline Validation

**Impact**:
- **+22%** higher completion success
- **42% faster** completion time
- Reduced error recovery time

**Implementation**:
```javascript
// Good: Validate on blur with debounce
input.addEventListener('blur', () => {
  debounce(validateField, 300)();
});

// Bad: Only on submit
form.addEventListener('submit', validateAll);
```

### Error Message Design

**Requirements**:
1. Adjacent to the field (not at top of page)
2. Explain what's wrong
3. Explain how to fix it
4. Visually distinct (color + icon)

**Example**:
```html
<!-- Good -->
<input type="email" aria-describedby="email-error">
<span id="email-error" class="error">
  ⚠ Please enter a valid email (e.g., name@example.com)
</span>

<!-- Bad -->
<span class="error">Invalid input</span>
```

### Input Formatting

**Auto-format as user types**:
- Phone: (555) 123-4567
- Credit card: 4242 4242 4242 4242
- Date: 12/25/2024

**But**: Allow flexible input (with/without dashes, spaces).

### Smart Defaults

**Address Autocomplete**:
- Google Places API
- Pre-fill city/state from ZIP
- Country detection from IP

**Payment Defaults**:
- Remember last-used payment method
- Pre-fill billing = shipping checkbox

---

## Reviews & Social Proof

### Review Quantity Impact

**Conversion vs. Number of Reviews** (Spiegel, N=15.5M page views):

| Reviews | Purchase Likelihood |
|---------|---------------------|
| 0 | Baseline |
| 5 | **+270%** |
| 10 | +280% |
| 50+ | Diminishing returns |

**Key Insight**: First 5 reviews matter most.

### Optimal Rating

**Best Rating Range**: 4.0-4.7 stars
- 5.0 rating triggers suspicion
- "Too good to be true" effect
- Some negative reviews increase credibility

### Negative Review Seeking

**82%** of consumers specifically seek negative reviews
- To understand worst case
- To evaluate reviewer credibility
- To confirm authenticity

**Implication**: Don't hide negative reviews; make them findable.

### Review Enhancements

| Enhancement | Conversion Lift |
|-------------|-----------------|
| Photo reviews | **+106.3%** |
| Verified purchase badge | +15% |
| Video reviews | +60-80% |
| Review helpfulness voting | +20-30% |

### Review Display Best Practices

1. Show star distribution histogram
2. Enable filtering (rating, recency, verified)
3. Highlight "most helpful" reviews
4. Show reviewer profile credibility signals
5. Display review response from brand

---

## Product Images

### Quantity Impact

**eBay Study** (Di et al. 2014):
| Images | Conversion Lift |
|--------|-----------------|
| 1 | 2× baseline |
| 2 | 2× again (4× total) |
| 3+ | Diminishing returns |

**Implication**: Minimum 2 images; after that, focus on quality.

### Image Types

**Required**:
- Hero shot (clean, white background)
- In-context/lifestyle shot
- Scale reference

**High Impact**:
- 360° view: +16% to +47% conversion
- Zoom capability: +20-30%
- User-generated photos: +60%

### Load Time Impact

**Every 0.1s improvement**:
- **+8.4% conversions**
- **+9.2% average order value**

**Optimization**:
- WebP format (30% smaller)
- Lazy loading
- Progressive JPEGs
- CDN distribution

---

## Search & Discovery

### Searcher Behavior

| Metric | Searchers | Non-Searchers |
|--------|-----------|---------------|
| % of visitors | 24% | 76% |
| % of revenue | **61%** | 39% |
| Conversion rate | **15%** | 7% |

### Search Behavior Patterns

- **69%** go straight to search bar
- **80%** leave if search doesn't meet expectations
- Average searches per session: 1.2

### Search UX Requirements

**Essential**:
- Prominent search bar
- Autocomplete suggestions
- Typo tolerance
- Synonym handling

**Advanced**:
- Visual search (image input)
- Voice search
- Personalized results
- Faceted filtering

### Zero Results Handling

**Never Show Empty State**:
- Suggest alternatives
- Show popular products
- Offer category browsing
- "Did you mean..." suggestions

---

## Trust Signals

### Security Indicators

| Signal | Trust Impact |
|--------|--------------|
| SSL/HTTPS | Expected baseline |
| Payment icons (Visa, MC) | +5-10% |
| Security badges | +10-15% |
| BBB/TrustPilot | +8-12% |

### Trust Placement

**Critical Locations**:
1. Near "Add to Cart" button
2. On payment form
3. In footer (persistent)
4. Near price display

### Authenticity Signals

- Physical address visible
- Real phone number
- Real human photos (not stock)
- Customer service chat available
- Return policy prominent

---

## Pricing Psychology

### Charm Pricing

**Prices Ending in 9**: +24% sales (Gendall et al. 1997)

**Left-Digit Effect**:
- $3.00 → $2.99 feels significantly cheaper
- Despite only 1¢ difference
- Effect diminishes for larger purchases

### Price Display

**Best Practices**:
```html
<!-- Good: Clear pricing -->
<span class="price">
  <span class="currency">$</span>
  <span class="dollars">29</span>
  <span class="cents">.99</span>
</span>

<!-- Bad: Hidden costs -->
<span class="price">$29.99</span>
<small class="hidden-fee">+ $4.99 shipping</small>
```

### Drip Pricing (DARK PATTERN)

**Definition**: Revealing additional fees throughout checkout

**Effect**:
- Consumers select lower base, higher total prices
- Creates self-justification bias (committed to purchase)
- Adds 30-40% to costs across industries

**Regulatory Status**:
- UK DMCC Act 2024: BANNED
- FTC enforcement increasing
- GDPR implications for EU

### Promo Code Field Paradox

**27%** abandon checkout to search for voucher codes

**Problem**: Empty promo field creates FOMO

**Solutions**:
1. Hide behind expandable link ("Have a promo code?")
2. Pre-apply available discounts automatically
3. Remove field entirely, use automatic detection

### Subscription Pricing

**Subscription Fatigue**:
- 62% feel overwhelmed by subscriptions
- Average household: 4-5 subscriptions

**Anti-Dark Pattern**:
- Clear cancellation process
- Renewal reminders
- Usage summaries
- Easy pause options

---

## Urgency & Scarcity

### Legitimate vs. Manipulative

| Legitimate | Manipulative |
|------------|--------------|
| Actual inventory count | Fake "only 2 left!" |
| Real sale end date | Perpetual "ending soon" |
| Genuine limited editions | Artificial scarcity |
| Actual viewer count | Inflated numbers |

### Impact of Fake Urgency

**Brand Trust Damage**: Up to 45% reduction
- Customers remember being manipulated
- Word-of-mouth negative impact
- Regulatory risk increasing

### Effective Legitimate Urgency

```html
<!-- Good: Real inventory -->
<span class="inventory" data-count="3">
  Only 3 left in stock
</span>

<!-- Good: Real deadline -->
<span class="sale-end" data-end="2024-12-31T23:59:59">
  Sale ends in <time>2 days, 4 hours</time>
</span>

<!-- Bad: Fake urgency -->
<span class="fake-urgency">🔥 Selling fast!</span>
```

---

## Mobile E-Commerce

### Mobile Conversion Gap

**Mobile conversion typically 50% of desktop**:
- Smaller screens
- Typing difficulty
- Checkout friction

### Mobile Optimization

**Essential**:
- Thumb-zone friendly CTAs
- Mobile payment (Apple Pay, Google Pay)
- Sticky cart/CTA
- Simplified forms
- Large touch targets (44px+)

**Payment Impact**:
- Apple Pay: +30-40% mobile conversion
- Stored payment methods: +20-30%

---

## Quick Detection Signals

### Checkout Optimized
- ≤14 form fields
- Guest checkout available
- Progress indicator (accelerating)
- All costs visible upfront
- Inline validation

### Trust Established
- Security badges near payment
- Real contact information
- Clear return policy
- Payment icons visible

### Reviews Effective
- First 5+ reviews present
- Photo reviews available
- Verified badges shown
- Negative reviews accessible
- Star distribution visible

### Pricing Honest
- No drip pricing
- Total visible throughout
- Promo field handled well
- No fake urgency
- Clear subscription terms

---

## Code Patterns to Detect

### Good Patterns
```javascript
// Inline validation
<input 
  type="email" 
  onBlur={validateEmail}
  aria-describedby="email-error"
/>

// Progress indication
<CheckoutProgress 
  currentStep={2} 
  totalSteps={4}
  pattern="accelerating"
/>

// Guest checkout
<Button onClick={proceedAsGuest}>
  Continue as Guest
</Button>

// All costs visible
<OrderSummary
  subtotal={subtotal}
  shipping={shipping}
  tax={tax}
  total={total}
  showAllFees={true}
/>
```

### Warning Patterns
```javascript
// Too many fields
const formFields = Array(25).fill(<input />);

// Forced account creation
if (!user.isLoggedIn) {
  redirect('/create-account');
}

// Hidden fees
<span className="fine-print">
  + processing fee calculated at checkout
</span>

// Fake urgency
<span className="urgency">
  {randomNumber(1, 5)} people viewing this!
</span>

// No guest checkout
const checkout = requiresAuth(CheckoutFlow);

// Drip pricing
const revealShippingCost = (step) => {
  if (step === 3) return shippingCost;
  return null;
};
```

### Trust Check
```javascript
// Verify trust signals present
const hasTrustSignals = 
  document.querySelector('.security-badge') &&
  document.querySelector('.payment-icons') &&
  document.querySelector('.return-policy');

// Check for dark patterns
const hasDarkPatterns =
  document.querySelector('[class*="countdown"]') && 
  !document.querySelector('[data-real-deadline]');
```
