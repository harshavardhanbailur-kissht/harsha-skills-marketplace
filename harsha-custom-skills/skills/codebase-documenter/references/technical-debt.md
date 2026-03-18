# Technical Debt Classification and Management

## Technical Debt Classification

### Deliberate Debt (Intentional Trade-off)

**Definition:** Known limitation accepted for strategic gain (speed, business value, learning).

**Example:**
```python
def process_payment(amount):
    # DEBT: Direct Stripe API call for speed
    # TODO: Extract PaymentProvider abstraction when moving to multiple providers
    return stripe.Charge.create(amount=amount)
```

**Characteristics:**
- Documented or commented
- Business justification clear
- Repayment plan exists (or is acceptable)
- Awareness is high

**Management:**
- Add DEBT marker with context
- Reference ticket/epic for repayment
- Accept as legitimate strategic choice
- Monitor if repayment date passes

### Accidental Debt (Unintended Accumulation)

**Definition:** Unintended code quality degradation due to time pressure, knowledge gaps, or scope creep.

**Example:**
```python
def calculate_order_total(order):
    # Complex logic mixing tax, discount, shipping, promotion
    # No clear separation of concerns
    # Multiple if/elif chains for special cases
    # Hard to test, harder to modify
```

**Characteristics:**
- Not documented
- Evolution visible in git history (started simple, grew complex)
- Tests are fragile
- New features slow

**Management:**
- Requires refactoring/cleanup
- Higher priority (more insidious)
- Often discovered during feature work

---

## Debt Severity Scoring

### Severity Levels

**LEVEL 1: Low Severity (Quick Fix)**
- Impact: Cosmetic, naming, documentation
- Effort to fix: <1 hour
- Risk if unfixed: Low
- Examples: Typos in variables, outdated comments

**LEVEL 2: Medium Severity (Plan to Address)**
- Impact: Code complexity, maintainability
- Effort to fix: 1-8 hours
- Risk if unfixed: Moderate (future work slows)
- Examples: Missing abstraction, duplicated code

**LEVEL 3: High Severity (Address Soon)**
- Impact: Performance, reliability, or significant complexity
- Effort to fix: 1-3 days
- Risk if unfixed: High (blocks features, causes bugs)
- Examples: N+1 queries, circular dependencies, inadequate error handling

**LEVEL 4: Critical Severity (Address Now)**
- Impact: Security, data loss, or system failures
- Effort to fix: 3+ days
- Risk if unfixed: Critical (incidents, compliance)
- Examples: SQL injection vulnerability, missing encryption, race conditions

### Severity Calculation

```
Severity = (Impact × Frequency × Spread) / Effort

Impact:     1-10 (how bad if it fails)
Frequency:  1-10 (how often does it matter?)
Spread:     1-10 (how much code affected?)
Effort:     1-10 (how hard to fix)

Example: Bug in payment retry
  Impact: 10 (payment failures)
  Frequency: 5 (happens sometimes)
  Spread: 3 (isolated code)
  Effort: 3 (moderate to fix)
  Severity = (10 × 5 × 3) / 3 = 50 (HIGH)

Example: Unclear variable naming
  Impact: 2 (readability)
  Frequency: 10 (everyone reads code)
  Spread: 1 (local)
  Effort: 1 (rename)
  Severity = (2 × 10 × 1) / 1 = 20 (LOW)
```

---

## Remediation Priority Matrix

### 4-Box Matrix

```
URGENCY
    ^
    |
  10|  [ Critical ]      [ Important ]
    |  Do Now            Schedule Soon
    |
    |  [ Cosmetic ]      [ Should Fix ]
    |  Defer              Plan for iteration
    |
    +--> IMPACT
    0        5        10
```

### Plotting Debt Items

```
Database N+1 Query (users list):
  Urgency: 8 (hits often in production)
  Impact: 7 (loads page slowly)
  Position: Important → Schedule Soon

Error Message Typo:
  Urgency: 3 (low user impact)
  Impact: 2 (cosmetic)
  Position: Cosmetic → Defer

SQL Injection in Admin Panel:
  Urgency: 10 (security)
  Impact: 10 (data breach)
  Position: Critical → Do Now

Missing Unit Tests:
  Urgency: 6 (affects quality)
  Impact: 6 (hard to modify safely)
  Position: Should Fix → Plan for iteration
```

### Remediation Schedule

**This Sprint (Critical Urgent):**
- Security vulnerabilities
- Production outages
- Data loss risks

**Next Sprint (Important/Should Fix):**
- High-impact performance issues
- Common bugs
- Major code quality issues

**Planned Epic (Backlog):**
- Refactoring projects
- Architectural improvements
- Technical migration

**Acceptable Debt (Defer):**
- Cosmetic improvements
- Non-blocking issues
- Low-impact technical debt

---

## Domain-Specific Debt Patterns

### FinTech Systems

**Critical debt types:**
- Incomplete transaction logging (audit trail)
- Missing reconciliation checks
- Timing-dependent bugs (race conditions in transfers)
- Precision loss in calculations (float vs decimal)

**Red flags:**
```python
# BAD: Using float for money
balance = balance + 0.1  # Rounding errors!

# GOOD: Using Decimal or integer cents
balance = balance + Decimal('0.10')
# or
balance_cents = balance_cents + 10
```

**Scoring:** Financial errors get +10 severity boost.

### Healthcare Systems

**Critical debt types:**
- Incomplete audit trails (regulatory requirement)
- Missing data validation (patient safety)
- Inadequate security (PII exposure)
- Race conditions in prescriptions

**Red flags:**
```python
# BAD: Silent data loss
if validate(data):
    save(data)
else:
    pass  # Data ignored, no log!

# GOOD: Explicit logging
if validate(data):
    save(data)
else:
    logger.error(f"Invalid patient data: {data}")
    alert_team()
```

**Scoring:** Healthcare errors get +15 severity boost due to life safety.

### E-Commerce Systems

**Critical debt types:**
- Inventory race conditions (overselling)
- Payment state inconsistencies (double-charging)
- Cart manipulation vulnerabilities
- Missing order reconciliation

**Red flags:**
```python
# BAD: Check-then-act race condition
if inventory['qty'] >= ordered_qty:
    inventory['qty'] -= ordered_qty  # Lost update!
    charge_customer()

# GOOD: Database transaction + locking
with transaction:
    inventory = select_for_update(product_id)
    if inventory.qty >= ordered_qty:
        inventory.qty -= ordered_qty
        charge_customer()
```

**Scoring:** E-commerce debt affecting payments get +8 severity boost.

### Enterprise Systems

**Common debt:**
- Legacy integration points (ETL failures)
- Complex permission systems (security creep)
- Undocumented workflows (tribal knowledge)
- Performance degradation over time

**Scoring:** Enterprise debt affecting >1000 users gets +5 severity boost.

---

## Debt Documentation Format

### Debt Register Template

```markdown
# Technical Debt Register

## Item: [Debt-001] Order Calculation Complexity

**Classification:** Accidental debt
**Severity Level:** 3 (High)
**Priority:** Should Fix

**Location:**
- File: `src/orders/pricing.py`
- Function: `calculate_order_total()`
- Lines: 45-120

**Description:**
The order total calculation mixes multiple concerns:
- Tax calculation
- Discount application
- Shipping cost
- Promotional codes
- Special case handling

This makes the function hard to test and modify.

**Business Impact:**
- Each new promotion requires code change
- Testing is fragile (>50 line test functions)
- Bugs in calculation affect revenue

**Technical Impact:**
- Cognitive load: Function is too complex (McCabe > 20)
- Testing: 15+ test cases to cover scenarios
- Modification: New requirements slow down

**Remediation Plan:**
1. Extract tax calculation → TaxService
2. Extract discounts → DiscountCalculator
3. Extract promotions → PromotionEngine
4. Keep main function as orchestrator

**Effort Estimate:** 3 days
**Blocked?:** No
**Suggested Sprint:** Q2 2026
**Owner:** Alice Smith

**Evidence:**
- Commit history: 12+ changes to this function in 6 months
- Bug tracker: #234, #456, #890 traced to this function
- Test fragility: 10% failure rate on test runs
```

### Debt Metrics

```
Total Debt Items: 47
- Critical: 2
- High: 8
- Medium: 15
- Low: 22

Technical Debt Ratio:
  Estimated remediation time: 120 person-days
  Estimated project timeline: 240 person-days
  Ratio: 50% (high, indicates quality issues)

Debt Trend:
  6 months ago: 32 items (28 person-days)
  Now: 47 items (120 person-days)
  Trend: Increasing (ALERT)
```

---

## Preventing New Debt

### Code Review Checklist

```
During code review, check for debt introduction:

□ Does this add complexity without clarity?
□ Are there TODOs/HACKs without context?
□ Is this duplicating existing code?
□ Are edge cases unhandled?
□ Is this testable?
□ Does it create tight coupling?
□ Is error handling adequate?
□ Is performance acceptable?
□ Are there security concerns?

If YES to any: Request changes or formal debt entry
```

### Debt Prevention Rules

**1. Establish Debt Threshold**
```
Code review blocks merges if:
- Cyclomatic complexity > 15
- Method length > 100 lines
- Comment-to-code ratio < 0.1
- Test coverage drops >5%
```

**2. Require Debt Tickets**
```
If accepting debt:
- Create ticket with severity/priority
- Link in PR/commit message
- Set expected remediation date
- Assign owner
```

**3. Monitor Debt Trends**
```
Quarterly:
- Total debt items: target is flat or declining
- Critical/high severity items: target is <5
- Average time to remediation: target <30 days
- New debt rate: target <3 items/month
```

---

## Debt Paydown Strategy

### Refactoring Approach

**Don't:** Do big rewrites hoping for perfection.
**Do:** Make small, testable improvements incrementally.

**Pattern: Extract and Test**
```python
# BEFORE: Complex function
def process_order(order):
    # 100 lines of complex logic

# STEP 1: Extract piece into separate function
def extract_tax(order):
    return TaxService.calculate(order.address, order.items)

# STEP 2: Update original to use extracted function
def process_order(order):
    tax = extract_tax(order)  # Now testable separately
    # ... rest of logic

# STEP 3: Repeat for other concerns
```

### Risk Management

**Safe refactoring:**
- Each change is small
- Tests pass before, during, after
- Can deploy intermediate state
- Can roll back specific changes

**Unsafe refactoring:**
- One big rewrite (high risk of introducing bugs)
- Refactoring without tests
- Mixing refactoring with feature work

---

## Communicating Debt to Stakeholders

### For Engineering Team

```
We have 47 debt items (120 person-days to fix).
This slows feature work by ~15% (time spent on bugs vs. features).

Current work is sustainable at this level.
Trend is concerning: debt increasing 50% per 6 months.

Recommendation: Dedicate 20% sprint capacity to paydown.
Impact: Improve feature velocity by 10% within 6 months.
```

### For Product Managers

```
Technical debt is like financial debt: costs interest.

Our codebase has $120K in "debt" (time to fix).
We pay 10% interest (15% of engineer time).

Refinancing plan:
- Pay $20K now (dedicate 3 weeks)
- Reduce interest by 3% (save 2% engineer time)
- ROI: Break even in 2 months

Cost of ignoring: Debt grows, interest increases.
```

### For Executives

```
Code quality metric: 47 known issues, 2 critical.

Risk: System incidents increase if not addressed.
Cost: Each incident = 5+ hours engineering time.
Prevention: Invest 3 weeks now, save 10+ hours/quarter.

Recommendation: Schedule debt paydown sprint next quarter.
```

---

## Debt Paydown Metrics

### Measure Success

```
Before paydown:
- Critical items: 2
- Average remediation time: 45 days
- Feature velocity: 8 points/sprint

After paydown (target):
- Critical items: 0
- Average remediation time: 20 days
- Feature velocity: 9 points/sprint

Success = velocity increase + debt decrease
```

### Leading Indicators (Monitor During Paydown)

```
- Test coverage: Should increase
- Code complexity metrics: Should decrease
- Bug report frequency: Should decrease
- Code review time: Should decrease (easier to understand)
- New feature velocity: Should increase (less bug fixes)
```

---

## Summary: Debt Management Framework

1. **Classify:** Deliberate vs. Accidental
2. **Score:** Severity using impact × frequency × spread
3. **Prioritize:** Use urgency-impact matrix
4. **Document:** Track in debt register
5. **Prevent:** Code review gates, threshold enforcement
6. **Pay down:** Small incremental improvements
7. **Monitor:** Trends and metrics
8. **Communicate:** To engineers, product, executives
