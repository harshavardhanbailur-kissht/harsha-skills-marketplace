# Accuracy Verification and Fact-Checking Framework

## Fact-Checking Methodology (Adapted from IFCN Principles)

International Fact-Checking Network developed 5 core principles. Applied to code documentation:

### Principle 1: Commitment to Nonpartisanship
**In code docs:** Document what the code actually does, not what it should do.

**Example of violation (WRONG):**
```
"This service correctly implements OAuth 2.0."
(This is a judgment, not a fact. Correct according to what standard?)
```

**Example of compliance (RIGHT):**
```
"This service implements OAuth 2.0 as per RFC 6749, validated by tests.
Known gap: Doesn't implement PKCE (RFC 7636) for mobile clients."
```

**How to verify:** Check code against official RFC. Document gaps without endorsement/condemnation.

### Principle 2: Commitment to Transparency of Sources
**In code docs:** Always cite evidence. Make verification possible.

**Example of violation (WRONG):**
```
"Payments are secured with encryption."
(What kind? Where is it? Who verified?)
```

**Example of compliance (RIGHT):**
```
"Payments are transmitted over HTTPS (TLS 1.2+) per NIST guidelines.
Evidence: See PaymentGateway.send_encrypted() in src/payment/gateway.py (line 45)
Test: test_payment_request_uses_tls_encryption verifies encryption is enabled.
Configuration: MIN_TLS_VERSION=1.2 in config.py"
```

**How to verify:** Reader can check each cited source independently.

### Principle 3: Commitment to Transparency of Funding
**In code docs:** Disclose incentives that might bias documentation.

**Example of violation (WRONG):**
```
"This microservices architecture is clearly superior to monoliths."
(Unstated assumption: More services = better; depends on context)
```

**Example of compliance (RIGHT):**
```
"This system uses microservices. Benefits: Team independence, scale.
Costs: Distributed system complexity, operational overhead.
This architecture was chosen because: [cite decision from git/PR].
You might use a monolith if: [acknowledge alternatives]"
```

**How to verify:** Documentation acknowledges tradeoffs, not zealotry.

### Principle 4: Commitment to Transparency of Methodology
**In code docs:** Explain how claims were verified.

**Example of violation (WRONG):**
```
"The system handles 1M requests per second."
(How do you know? Benchmark? Theoretical calculation? Production data?)
```

**Example of compliance (RIGHT):**
```
"The system handles ~100K requests per second under load testing.

Verification methodology:
- Load test: k6 script in tests/load/ sends sustained 100K req/s for 5 minutes
- Setup: GKE cluster with 10 pods, 4 CPU each
- Metric: p95 latency remains <100ms, error rate <0.01%

Note: This benchmark reflects controlled conditions; production has higher variance.
See tests/load/results/ for raw data."
```

**How to verify:** Methodology is reproducible. Others can run same test.

### Principle 5: Commitment to Open and Honest Corrections
**In code docs:** Maintain a corrections log.

**Example:**
```markdown
## Corrections Log

### 2024-03-01: Fixed cache TTL documentation
**What was wrong:** Documented 1-hour TTL; actual code uses 30 minutes
**Why it was wrong:** Code was updated in PR #2345 but docs weren't
**How fixed:** Updated ARCHITECTURE.md line 234 to match actual code
**Impact:** LOW (affects internal timing assumptions, not external API)
**Verification:** Tests in test_cache_ttl.py confirm 30-minute TTL

### 2024-02-15: Clarified payment retry strategy
**What was wrong:** Docs said "retries forever"; actually retries 3x then fails
**Why it was wrong:** Code was refactored in commit 3a2b1c but docs not updated
**How fixed:** Updated error-handling.md with correct retry count and backoff strategy
**Impact:** MEDIUM (affects integration with payment providers expecting specific behavior)
**Verification:** test_payment_retry_exhaustion verifies 3-retry limit
```

**Structure principle:** Corrections build trust by showing you catch and fix errors.

---

## Claim-by-Claim Verification Workflow

### Step 1: Extract Claim
```
From documentation:
"The Order Service stores orders in PostgreSQL with automatic backups every 6 hours."
```

### Step 2: Break Into Atomic Claims
1. "Order Service uses PostgreSQL"
2. "Orders are stored in PostgreSQL"
3. "Automatic backups exist"
4. "Backups run every 6 hours"

### Step 3: Find Evidence for Each Claim

**Claim 1: "Order Service uses PostgreSQL"**

```bash
# Search for PostgreSQL driver
grep -r "psycopg2\|PostgreSQL\|pg" requirements.txt package.json pom.xml

# Search for connection strings
grep -r "postgresql://\|postgres://" src/ config/

# Search in comments
grep -r "postgres\|postgresql" src/ --include="*.py" --include="*.md"
```

Evidence found:
- Code: `import psycopg2` in src/orders/persistence.py
- Config: `DATABASE_URL=postgresql://...` in .env.example
- Tests: conftest.py uses PostgreSQL test container

**Confidence: Very High** ✓

---

**Claim 2: "Orders are stored in PostgreSQL"**

```bash
# Check schema
find . -name "*.sql" -o -name "*schema*" -o -name "*migration*"

# Check ORM definitions
grep -r "class Order\|model Order" src/ --include="*.py"

# Check repository layer
grep -r "SELECT.*order\|INSERT.*order" src/ --include="*.py"
```

Evidence found:
- SQL migration: migrations/001_create_orders_table.sql
- ORM model: src/orders/models.py defines `class Order(db.Model)`
- Tests: test_orders.py includes `test_order_persistence_to_postgres`

**Confidence: Very High** ✓

---

**Claim 3: "Automatic backups exist"**

```bash
# Search for backup configuration
grep -r "backup\|BACKUP" config/ .env* *.yaml *.yml

# Search for backup job definitions
grep -r "backup\|Backup" src/ --include="*.py" | grep -i "job\|task\|cron"

# Search in infrastructure code
grep -r "backup" infrastructure/ terraform/ k8s/ --include="*.tf" --include="*.yaml"
```

Evidence found:
- Config: BACKUP_ENABLED=true in .env
- Task: src/tasks.py has `backup_database()` function
- Git: Commit 2a1b9c "add daily database backups"

But: Where is it scheduled?

```bash
# Search for cron or scheduler
grep -r "cron\|schedule\|APScheduler" src/ config/
```

Not found in code! Need to check:
- Infrastructure: Kubernetes CronJob? AWS Lambda scheduler?
- Database: PostgreSQL pg_dump scheduled job?

**After searching infrastructure/k8s/:**
- Found: backup-cronjob.yaml with schedule: "0 */6 * * *" (every 6 hours)

**Confidence: High** ✓

---

**Claim 4: "Backups run every 6 hours"**

Evidence:
- Cron expression: `0 */6 * * *` = every 6 hours
- Confirmed in backup-cronjob.yaml

**Confidence: Very High** ✓

---

### Step 4: Assess Collective Confidence

| Claim | Evidence | Confidence |
|-------|----------|------------|
| PostgreSQL used | Code + config + tests | Very High |
| Orders stored there | SQL + ORM + tests | Very High |
| Backups exist | Config + code + infra | High |
| Every 6 hours | Cron expression | Very High |

**Overall: Very High** → Document as "Verified"

---

## Cross-Referencing Code Claims Against Tests

### Pattern: Documented behavior must have test coverage

**Documented:**
"Orders are calculated with tax based on delivery address."

**Verification workflow:**

```bash
# Find calculation code
grep -r "calculate.*tax\|apply_tax" src/ --include="*.py"
# Result: src/orders/pricing.py:47

# Find tests for this functionality
grep -r "test.*tax\|calculate.*tax" tests/
# Result: tests/orders/test_pricing.py:112-145

# Check if test uses delivery address
cat tests/orders/test_pricing.py | grep -A 20 "def test_tax_calculation"
```

Test content:
```python
def test_tax_calculation_uses_delivery_address():
    order = Order(
        items=[Item(price=100)],
        delivery_address=Address(state="CA")
    )
    total = calculate_order_total(order)
    assert total == 107.25  # CA tax rate is 7.25%
```

**Result:** Claim verified by test. Can document with high confidence.

---

### Pattern: Error handling claims must match test assertions

**Documented:**
"Creating an order with no items returns ValidationError"

**Verification:**

```python
# Implementation
def create_order(items):
    if not items:
        raise ValidationError("Order must have at least one item")
    return Order(items)

# Test
def test_order_creation_fails_with_no_items():
    with pytest.raises(ValidationError) as exc_info:
        create_order([])
    assert "at least one item" in str(exc_info.value)
```

**Result:** Implementation + test align. Document with high confidence.

### Pattern: Performance claims require benchmarks

**Documented:**
"Order creation completes in <100ms"

**Verification workflow:**

```bash
# Search for performance tests
grep -r "test.*performance\|benchmark\|@pytest.mark.benchmark" tests/

# Look for benchmark results
find . -name "*benchmark*" -o -name "*perf*" -o -name "*load*"
```

**If benchmarks exist:**
```python
@pytest.mark.benchmark
def test_order_creation_performance():
    # Setup
    order_data = {...}

    # Benchmark
    result = benchmark(create_order, order_data)

    # Assertion
    assert result < 0.100  # 100ms
```

**If benchmarks don't exist:** Document as "target performance unknown; see comment on PR #1249 for proposed optimization"

---

## Detecting Contradictions Between Docs and Code

### Automated Contradiction Finder

```bash
#!/bin/bash
# Find all claims in documentation
grep -rh "The.*is\|returns\|throws\|takes\|accepts\|is stored" docs/ > claims.txt

# For each claim, verify against code
while IFS= read -r claim; do
    # Extract key terms
    terms=$(echo "$claim" | grep -oE '\b[A-Z][a-zA-Z]+\b' | head -3)

    # Search code for contradicting pattern
    if grep -r "NOT \|no\|never\|disabled" src/ | grep -q "$terms"; then
        echo "CONTRADICTION FOUND: $claim"
        echo "  Counter-evidence: "
        grep -r "NOT \|no\|never\|disabled" src/ | grep "$terms"
    fi
done < claims.txt
```

### Example Contradiction Detection

**Documented:**
```
"The API requires authentication for all endpoints."
```

**Code search for contradictions:**
```bash
grep -r "@public\|require_auth.*=.*False\|authentication.*optional" src/

# Found: src/endpoints/health.py
@app.get("/health")
@public  # <-- This allows unauthenticated access
def health_check():
    return {"status": "ok"}
```

**Action:** Update documentation to say "All endpoints except /health and /status require authentication."

---

### Example: Documented vs. Actual Response Format

**Documented:**
```markdown
## GET /orders/{id}
Returns: `{ "order": { "id": 1, "total": 99.99 } }`
```

**Code check:**
```python
@app.get("/orders/{id}")
def get_order(id: int):
    order = db.query(Order).filter(Order.id == id).first()
    return {
        "order": {
            "id": order.id,
            "total": order.total,
            "status": order.status  # <-- Not documented!
        }
    }
```

**Action:** Update documentation to include `status` field.

**Or:** Remove status from actual code if it shouldn't be exposed.

---

## Pre-mortem Methodology: "How Could This Doc Be Wrong?"

### For Each Major Claim, Ask:

**1. Code contradiction**
"Is there code that contradicts this claim?"
```bash
grep -r "NOT \|no\|false\|disable" src/ | grep -i <claim_keyword>
```

**2. Test gap**
"Is there a test that would fail if this claim is wrong?"
```bash
grep -r "test.*<claim>" tests/
```

**3. Git evidence**
"When was this decided? Has it changed?"
```bash
git log -S "<claim>" --all -- .
git blame -L<line>,<line> <file>
```

**4. Assumption exposure**
"What assumptions does this claim make?"
- "Assumes X never changes"
- "Assumes users do Y"
- "Assumes performance is acceptable"

**5. Edge case exposure**
"What scenarios aren't covered by tests?"
```bash
# Tests cover happy path, but what about:
# - Large payloads?
# - Concurrent requests?
# - Network failures?
# - Invalid data?
```

### Pre-mortem Document Template

```markdown
## Claim: "Orders are charged immediately upon creation"

Evidence:
✓ Code: order.create() calls stripe.Charge() synchronously
✓ Test: test_order_creation_triggers_charge
✓ Git: Commit 3a2b1c "charge immediately"

How could this be wrong?
1. Async queue might exist but not in happy path
   - Mitigation: grep for "queue_payment" or "async_charge"

2. Fraud detection might delay charging
   - Mitigation: Check fraud_detection.py for interaction

3. Webhook might update status after async charge
   - Mitigation: Search for webhook handlers

4. Tests might not cover failure case
   - Risk: Real failures might use different path
   - Mitigation: See test_charge_failure

5. Payment retry might be async
   - Risk: Retried charges might succeed hours later
   - Mitigation: Check retry_payment() in tasks.py

Scenarios not covered by tests:
- [ ] Charge succeeds but webhook fails
- [ ] Network timeout during charge
- [ ] Stripe API down
- [ ] Customer hitting account limit

Confidence: High (code + test align)
Confidence degradation if: Async payment queue is discovered
```

---

## Fact-Checking Framework for Documentation Updates

### When Documentation Changes, Verify:

1. **Change impact scope**
   - Does this change affect only one module?
   - Or multiple dependent systems?

2. **Test coverage for change**
   - Are there tests for the new claim?
   - Do all tests still pass?

3. **Backward compatibility**
   - Does this contradict old documentation?
   - Are old API consumers affected?

4. **Evidence freshness**
   - Is the code recent?
   - Have there been recent changes contradicting this?

### Verification Checklist for Doc Updates

- [ ] Claim is supported by code (within last month)
- [ ] At least one test covers this behavior
- [ ] Git history doesn't show contradicting changes
- [ ] No comments indicate this is deprecated
- [ ] No GitHub issues dispute this behavior
- [ ] If claim is new, rationale is documented

---

## Handling Uncertainty in Documentation

### Confidence Level Definitions

**LEVEL 1: Verified**
- Code: Clear implementation
- Test: Passes, covers scenario
- Git: Recent (within 3 months), no contradicting commits
- Comments: Align with code
- Example: "Passwords are hashed with bcrypt"

**LEVEL 2: High Confidence**
- Code: Clear implementation
- Test: Covers scenario (though might be minimal)
- Git: No contradicting recent changes
- Missing: Specific edge case tests
- Example: "Orders calculate tax by delivery address"

**LEVEL 3: Moderate Confidence**
- Code: Likely implementation (inferred from structure)
- Test: Covers happy path, edge cases untested
- Git: Design is clear, implementation might have drifted
- Example: "Cache invalidation happens on user profile change"

**LEVEL 4: Low Confidence**
- Code: Unclear or contradicted by other code
- Test: No specific test found
- Git: Old (>6 months) or no clear decision
- Example: "User accounts are auto-archived after 2 years"

**LEVEL 5: Unknown**
- Code: Not found
- Test: Not found
- Requires: Deep code archaeology or author interview
- Example: "Maximum supported users is 1M" (not in code)

### Documenting Uncertainty

```markdown
## Authentication Mechanism

**Verified:** Users authenticate via OAuth 2.0

**Implementation:** See src/auth/oauth.py for OAuth provider setup

**High Confidence:** Access tokens are JWT-based, validated on each request

**Moderate Confidence:** Token TTL is 1 hour
- Code: `TOKEN_TTL = 3600` in config.py
- Test: test_token_expiration confirms expiration
- Edge case: What happens if user's OAuth provider revokes token mid-request? Unknown

**Low Confidence:** Refresh tokens are stored in secure HttpOnly cookies
- Code: Cookies set in auth response, but "secure" attribute not visible
- Test: No specific test for HttpOnly flag
- Assumption: Based on security best practices, but not verified

**Unknown:** Token rotation strategy for compromised tokens
- No code found implementing token rotation
- No test or documentation
- Recommend: Interview security team
```

---

## Summary: Verification Checklist

Before publishing documentation, verify each claim:

- [ ] **Code evidence exists** (specific file, line number)
- [ ] **Test evidence found** (test name, assertion)
- [ ] **Git evidence available** (commit hash, date)
- [ ] **No contradicting code** (search for negatives)
- [ ] **No contradicting tests** (search for "not equal")
- [ ] **Assumptions explicit** (stated in doc)
- [ ] **Edge cases noted** (untested scenarios marked)
- [ ] **Confidence level assigned** (1-5)
- [ ] **False positives ruled out** (claim is actually true)
- [ ] **Stale evidence excluded** (no commits >6 months old without recent verification)
