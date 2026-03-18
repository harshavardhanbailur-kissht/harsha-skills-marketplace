# Cross-Validation for Code Documentation

## Denzin's Four Types of Triangulation Adapted for Code Analysis

Triangulation is the practice of verifying claims about code through multiple independent sources. Norman Denzin (1978) identified four fundamental types of triangulation that apply directly to code documentation:

### 1. Data Triangulation (Source Type Diversity)

**Definition**: Using multiple data sources to verify the same claim about code behavior.

**For Code Analysis**: Compare evidence from Code, Tests, Git History, Comments, and Inference.

**Application Example**:
```
Claim: "Payment processing requires user's billing address for validation"

Data Sources:
- Source 1 (Code): payment/service.py:45 checks if billing_address exists before charge
- Source 2 (Test): test_payment.py:102 verifies payment fails without address
- Source 3 (Git): Commit abc123 "Add address validation for PCI compliance"
- Source 4 (Comment): "Address required by Stripe API per PCI-DSS §6.5.9"

Result: All data sources independently confirm requirement → VERIFIED (95%+)
```

### 2. Investigator Triangulation (Independent Verification)

**Definition**: Having multiple independent reviewers verify findings to overcome individual blind spots.

**For Code Analysis**: Different developers/reviewers examine the code independently.

**Application Example**:
```
Claim: "Session tokens expire after 24 hours"

Investigator A (Code Review):
- Reads auth/session.py:78 → TTL_SECONDS = 86400 (24 hours in seconds)

Investigator B (Test Review):
- Reads test_auth.py:156 → test_session_expiry_24h() verifies token invalid after 86400s

Investigator C (Git Review):
- Reads commit message from 2024-01-15 → "Set session TTL to 24 hours per security policy"

Result: Three independent reviewers found matching evidence → HIGH CONFIDENCE
```

### 3. Theory Triangulation (Multiple Interpretation Frameworks)

**Definition**: Applying different theoretical perspectives to interpret the same code pattern.

**For Code Analysis**: Examine code through different architectural lenses:
- Single responsibility principle lens: "Is this function doing one thing?"
- Security lens: "Does this code protect against XSS/SQL injection/CSRF?"
- Performance lens: "Does this pattern optimize for throughput or latency?"
- Maintainability lens: "Can a new developer understand this in 5 minutes?"

**Application Example**:
```
Claim: "Database queries are optimized for N+1 prevention"

Theory A (ORM Pattern Analysis):
- Code uses eager_load() / select_related() / prefetch_related()
- Evidence: models.py:45 has .select_related('user', 'organization')

Theory B (Performance Measurement Analysis):
- Logs show single query instead of N separate queries
- Evidence: test_perf.py verifies 1 query returned for 100 records

Theory C (Caching Theory):
- Query results cached at application level
- Evidence: cache_key.py:12 generates cache keys for batch queries

Result: Multiple theoretical frameworks confirm optimization pattern → HIGH CONFIDENCE
```

### 4. Methodological Triangulation (Multiple Analysis Methods)

**Definition**: Using different analysis methods on the same claim to avoid methodology-specific blind spots.

**For Code Analysis**: Mix static analysis, runtime testing, code review, and historical analysis.

**Application Example**:
```
Claim: "Error handling covers all API failure modes"

Method 1 (Static Analysis):
- grep for except/try blocks in api_handlers.py
- Found: DatabaseError, NetworkError, ValidationError handlers

Method 2 (Test Analysis):
- test_api_errors.py contains tests for all three error types
- Assertion: assert response.status_code in [400, 500, 503]

Method 3 (Code Review):
- Human review confirms try/except wraps all external API calls
- No missing error cases

Method 4 (Runtime/Instrumentation):
- Production logs show all thrown errors caught and logged
- No unhandled exceptions in last 30 days

Result: Four independent methodologies confirm error handling → VERIFIED
```

---

## Source Taxonomy with Credibility Weights

Every claim requires evidence from multiple sources. Each source type has a specific weight:

| Source Type | Credibility Weight | What Qualifies | What Does NOT Qualify |
|-------------|-------------------|----------------|-----------------------|
| **Code** | 1.0 (highest) | Executable logic at file:line. Function bodies, class definitions, config values, SQL schemas, route handlers, middleware chains. | Comments above code. Import statements alone. Dead/unreachable code. |
| **Test** | 0.9 | Assertions in test files. `assert`, `expect`, `should`, mock configurations revealing contract expectations. Must be PASSING. | Test file existence without assertions. Skipped/disabled tests. Test helpers/fixtures. |
| **Git History** | 0.7 | Commit messages, PR descriptions, blame output with authorship + date, merge commits revealing timeline, revert commits showing rejected approaches. | Automated commits (dependabot). Merge commits without meaningful messages. |
| **Comments** | 0.5 | Inline comments explaining WHY. TODO/FIXME/HACK/BUG markers. Docstrings. README sections about architecture. | Auto-generated JSDoc/Sphinx stubs. License headers. Commented-out code. |
| **Inference** | 0.3 (lowest) | Patterns from naming conventions, file structure, dependency graph, architectural similarity to known patterns. | Guesses without code basis. Assumptions from external knowledge alone. |

### Cross-Validation Rules (Explicit Credibility Threshold)

A claim is **cross-validated** when evidence from **2+ source types has combined credibility weight ≥ 1.5**.

**Examples:**
```
Code (1.0) + Test (0.9) = 1.9         → VERIFIED ✓
Code (1.0) + Git (0.7) = 1.7          → HIGH ✓
Code (1.0) + Comment (0.5) = 1.5      → HIGH ✓ (barely meets threshold)
Code (1.0) + Inference (0.3) = 1.3    → MEDIUM ✗ (below threshold, needs more)
Test (0.9) + Git (0.7) = 1.6          → HIGH ✓ (code-free but cross-validated)
Comment (0.5) + Inference (0.3) = 0.8 → LOW ✗ (insufficient)
```

---

## The Confidence Matrix

Complete source combination matrix showing all possible evidence combinations and resulting confidence levels:

```
Source Combination          Combined Weight    Confidence Level    Definition
─────────────────────────────────────────────────────────────────────────────
Code + Test + Git + Comment      3.1              VERIFIED (95%)     All 4 sources align
Code + Test + Git                2.6              VERIFIED (90%)     3 primary sources
Code + Test + Comment            2.4              HIGH (85%)         Code + Test confirmed
Code + Git + Comment             2.2              HIGH (80%)         Logic + history + intent
Test + Git + Comment             2.1              HIGH (80%)         Behavior + decision + intent
Code + Test                      1.9              HIGH (85%)         Gold standard pair
Code + Git                       1.7              HIGH (75%)         Implementation + decision
Code + Comment                   1.5              HIGH (65%)         Barely meets threshold
Git + Comment                    1.2              MEDIUM (55%)       History + intent only
Test + Git                       1.6              HIGH (75%)         Behavior + decision
Code only                        1.0              MEDIUM (60%)       Single source (weak)
Test only                        0.9              LOW (40%)          No code evidence
Git only                         0.7              LOW (30%)          No behavior proof
Comment only                     0.5              LOW (25%)          No verification
Inference only                   0.3              UNKNOWN (10%)      Pure speculation
```

---

## Evidence Template (Use for Every Major Claim)

Apply this format consistently:

```
Claim: "[Specific assertion about code behavior or architecture]"

Source 1 [Code, 1.0]:
  Location: [file:line]
  Evidence: [code snippet]
  Shows: [what does code prove?]

Source 2 [Test, 0.9]:
  Location: [test file, test name]
  Evidence: [assertion or mock configuration]
  Shows: [what does test verify?]

Source 3 [Git, 0.7]:
  Location: [commit hash]
  Evidence: [commit message or blame annotation]
  Shows: [what design decision is this?]

Combined Weight: X.X
Confidence Level: [VERIFIED / HIGH / MEDIUM / LOW / UNKNOWN]
Competing Hypothesis: [What alternative explanation exists?]
  → Status: [REJECTED / PARTIALLY SUPPORTED / ACCEPTED — why?]
```

---

## The Confidence Matrix in Practice

### Worked Example 1: Authentication Mechanism

**Claim:** "System uses OAuth 2.0 with JWT tokens"

**Source 1 - Code (1.0):**
```python
# src/auth/oauth.py
from authlib.integrations.fastapi_client import OAuth2App
from authlib.oauth2.rfc7523 import JWTBearerToken

oauth = OAuth2App(
    client_id="...",
    client_secret="...",
    token_model=JWTBearerToken
)

# src/auth/jwt.py
import jwt
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

Evidence: Imports OAuth2App and JWT libraries → OAuth + JWT present

**Source 2 - Test (0.9):**
```python
# test_auth.py:102
def test_oauth_login_creates_jwt():
    """Verify OAuth flow generates JWT token"""
    user = oauth_login(provider="google")
    assert "jwt" in response.cookies

    decoded = jwt.decode(
        response.cookies["jwt"],
        SECRET_KEY,
        algorithms=["HS256"]
    )
    assert decoded["sub"] == user.id
    assert "exp" in decoded  # expiry required
```

Evidence: Test verifies JWT creation AND OAuth flow → Behavior confirmed

**Source 3 - Git (0.7):**
```bash
git log --grep="OAuth" --oneline | head -3
  abc1234 Add OAuth 2.0 integration with Google provider
  def5678 Add JWT token generation for OAuth flow
  ghi9012 Configure OAuth token refresh mechanism
```

Evidence: Multiple commits document OAuth + JWT design

**Combined Weight:** 1.0 + 0.9 + 0.7 = 2.6 → **VERIFIED (90%)**

**Competing Hypothesis:**
- Could be using OAuth but with session cookies instead of JWT
- REJECTED: Test explicitly checks JWT in response.cookies
- Could be using JWT with SAML instead of OAuth
- REJECTED: Imports and commit messages explicitly mention OAuth 2.0 spec

**Verdict:** "OAuth 2.0 with JWT tokens verified across code, tests, and git history"

---

### Worked Example 2: Database Encryption at Rest

**Claim:** "Database credentials stored with encryption at rest"

**Source 1 - Code (1.0):**
```python
# src/config/secrets.py:45
from cryptography.fernet import Fernet

class SecretsManager:
    def __init__(self):
        self.cipher = Fernet(os.environ['ENCRYPTION_KEY'])

    def store_db_credential(self, credential):
        encrypted = self.cipher.encrypt(credential.encode())
        return encrypted
```

Evidence: Code explicitly encrypts credentials before storage

**Source 2 - Test (0.9):**
```python
# test_secrets.py:67
def test_credentials_encrypted_at_rest():
    """Verify credentials stored in encrypted form"""
    plaintext = "postgres://user:pass@host"

    encrypted = secrets_manager.store_db_credential(plaintext)

    # Encrypted version should NOT contain plaintext
    assert plaintext not in str(encrypted)

    # But should decrypt correctly
    decrypted = secrets_manager.decrypt(encrypted)
    assert decrypted == plaintext
```

Evidence: Test verifies both encryption and decryptability

**Source 3 - Comment (0.5):**
```python
# src/config/secrets.py:40
# All database credentials encrypted using Fernet (AES-128)
# per SOC2 requirement C1.3 (cryptographic controls)
```

Evidence: Comment explicitly references encryption requirement

**Combined Weight:** 1.0 + 0.9 + 0.5 = 2.4 → **HIGH (85%)**

**Competing Hypothesis:**
- Database credentials might be encrypted only in transit, not at rest
- REJECTED: Code shows encryption on store() function, not transport layer
- Encryption might be disabled for development
- PARTIALLY SUPPORTED: No toggle found for encryption in secrets.py

**Verdict:** "Database credentials encrypted at rest verified via code + test + comment"

---

### Worked Example 3: Payment Webhook Retry Logic

**Claim:** "Failed payment webhooks retry with exponential backoff (max 5 attempts)"

**Source 1 - Code (1.0):**
```python
# src/webhooks/payment_handler.py:78
def process_payment_webhook(webhook_data):
    max_attempts = 5
    attempt = 0
    delay = 1  # seconds

    while attempt < max_attempts:
        try:
            process_payment(webhook_data)
            return True
        except PaymentGatewayError:
            attempt += 1
            if attempt < max_attempts:
                delay *= 2  # exponential backoff
                time.sleep(delay)

    log_webhook_failure(webhook_data)
    return False
```

Evidence: Code explicitly implements exponential backoff, max 5 attempts

**Source 2 - Test (0.9):**
```python
# test_webhooks.py:234
def test_webhook_retries_with_exponential_backoff():
    """Verify webhook handler retries with exponential delays"""
    with mock.patch('process_payment', side_effect=PaymentGatewayError):
        start = time.time()
        result = process_payment_webhook({...})
        elapsed = time.time() - start

    # Attempts: 1s wait, then 2s, then 4s, then 8s, then give up
    # Total: 1 + 2 + 4 + 8 = 15 seconds
    assert 14 < elapsed < 16  # allow ±1s for overhead
    assert result == False

def test_webhook_succeeds_on_retry():
    """Verify webhook succeeds on later retry"""
    call_count = [0]

    def process_payment_mock(*args):
        call_count[0] += 1
        if call_count[0] < 3:
            raise PaymentGatewayError
        return True

    with mock.patch('process_payment', side_effect=process_payment_mock):
        result = process_payment_webhook({...})

    assert result == True
    assert call_count[0] == 3  # succeeded on 3rd attempt
```

Evidence: Tests verify retry count, exponential delays, and success on recovery

**Source 3 - Git (0.7):**
```bash
git log --oneline src/webhooks/payment_handler.py | head -5
  xyz7890 Implement webhook retry with exponential backoff (fixes timeout issues)
  uvw6543 Set max webhook retries to 5 (balances reliability + deadline)
  tsr4321 Add webhook retry monitoring to metrics

git show xyz7890 | grep -A2 "Exponential backoff"
  + # Exponential backoff prevents overwhelming failed gateway
  + # Max 5 attempts gives ~15s window for transient failures
```

Evidence: Commit history explains design rationale

**Combined Weight:** 1.0 + 0.9 + 0.7 = 2.6 → **VERIFIED (90%)**

**Competing Hypothesis:**
- Retries might use fixed delay instead of exponential
- REJECTED: Code clearly shows `delay *= 2`
- Max attempts might be different (3, 10, unlimited)
- REJECTED: Code explicitly sets `max_attempts = 5`

**Verdict:** "Exponential backoff with max 5 attempts verified across code + test + git"

---

### Worked Example 4: API Rate Limiting (Single Source - Weak)

**Claim:** "API endpoints rate-limited to 100 requests per minute per IP"

**Source 1 - Code (1.0):**
```python
# src/middleware/rate_limit.py:12
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds
```

Evidence: Configuration values set in code

**Missing Sources:**
- ❌ No test verifying rate limit actually enforced
- ❌ No git history explaining why 100/min was chosen
- ❌ No comment documenting rate limit rationale
- ❌ No inference from deployment config

**Combined Weight:** 1.0 (code only) → **MEDIUM (60%) - SINGLE SOURCE WEAKNESS**

**Problem:** This claim relies entirely on configuration values. There's no evidence that:
- The rate limit is actually enforced
- The code path is executed
- The configuration is read correctly
- The limit protects against abuse

**To upgrade to HIGH confidence, add:**

**Source 2 - Test (0.9):**
```python
def test_rate_limit_enforces_100_per_minute():
    """Verify API rejects requests exceeding rate limit"""
    # Make 100 successful requests
    for i in range(100):
        response = client.get('/api/data', remote_addr='192.168.1.1')
        assert response.status_code == 200

    # 101st request should be rejected
    response = client.get('/api/data', remote_addr='192.168.1.1')
    assert response.status_code == 429  # Too Many Requests
```

**Source 3 - Git (0.7):**
```
git log -S "RATE_LIMIT_REQUESTS = 100"
  abc1234 Set rate limit to 100/min per industry standards for public API
```

**Revised Combined Weight:** 1.0 + 0.9 + 0.7 = 2.6 → **VERIFIED (90%)**

**Lesson:** Configuration alone is insufficient. Always verify execution.

---

### Worked Example 5: Multi-Tenant Data Isolation (Complex)

**Claim:** "Tenant data is isolated: queries automatically filtered by tenant_id"

**Source 1 - Code (1.0):**
```python
# src/models/base.py:8
class TenantAwareModel(Base):
    tenant_id = Column(UUID, ForeignKey('tenants.id'))

    @classmethod
    def query(cls):
        """All queries auto-filtered by current tenant"""
        current_tenant = get_request_context().tenant_id
        return db.session.query(cls).filter(
            cls.tenant_id == current_tenant
        )

# src/handlers/orders.py:45
def get_order(order_id):
    # Automatically filtered by tenant (no explicit filter needed)
    order = Order.query().filter(Order.id == order_id).first()
    return order
```

Evidence: Base model implements automatic tenant filtering

**Source 2 - Test (0.9):**
```python
def test_tenant_isolation_in_queries():
    """Verify queries cannot access data from other tenants"""
    # Create tenants
    tenant_a = create_tenant("Company A")
    tenant_b = create_tenant("Company B")

    # Create orders in each tenant
    order_a = create_order(tenant_a, items=[...])
    order_b = create_order(tenant_b, items=[...])

    # Tenant A queries should NOT see Tenant B's orders
    with request_context(tenant_a):
        result = Order.query().all()
        assert len(result) == 1
        assert result[0].id == order_a.id
        assert order_b.id not in [o.id for o in result]

def test_tenant_isolation_on_join():
    """Verify joins respect tenant boundaries"""
    with request_context(tenant_a):
        # Query with join should still filter by tenant
        results = db.session.query(Order).join(
            Customer, Order.customer_id == Customer.id
        ).all()
        # Should only see tenant_a's data
        for order in results:
            assert order.tenant_id == tenant_a.id
            for customer in results.customers:
                assert customer.tenant_id == tenant_a.id
```

Evidence: Tests verify isolation across direct queries AND joins

**Source 3 - Git (0.7):**
```bash
git log --oneline src/models/base.py | grep -i tenant
  abc1234 Implement automatic tenant filtering at ORM level (security)
  def5678 Add test coverage for tenant isolation bypass scenarios
  ghi9012 Fix bug: joins bypassed tenant filter (SECURITY)

# The "bug fix" commit is crucial evidence
git show ghi9012
  - Join queries were accessing other tenant data
  - Added tenant filter to join operations
  - This shows the team discovered and fixed an isolation bug
```

Evidence: Git shows the isolation mechanism was intentionally built AND debugged

**Source 4 - Comment (0.5):**
```python
# src/models/base.py:6
# CRITICAL SECURITY: All queries must be filtered by tenant_id
# to prevent cross-tenant data leaks. Implemented at ORM base
# class to ensure no endpoint accidentally bypasses filtering.
```

Evidence: Comment explicitly marks isolation as security-critical

**Combined Weight:** 1.0 + 0.9 + 0.7 + 0.5 = 3.1 → **VERIFIED (95%)**

**Competing Hypothesis:**
- Isolation might be enforced only at API layer, not database layer
- PARTIALLY SUPPORTED: Code shows both (ORM filter + comment says "critical")
- Isolation might be opt-in, not automatic
- REJECTED: Code shows all queries inherit from TenantAwareModel
- Isolation might have bypasses (direct SQL, migrations)
- PARTIALLY UNKNOWN: Tests don't cover raw SQL access

**Verdict:** "Tenant isolation automatically applied at ORM level, verified across code + test + git + comment. Note: raw SQL queries not tested for isolation."

---

## Detecting Circular Sources

### What is Circular/Dependent Evidence?

**Definition**: Using evidence to "prove" a claim that was derived from that same evidence, or where evidence comes from a chain of sources that ultimately trace back to a single original source.

### Example: The Docstring Trap (WRONG)

```
Claim: "This function validates email addresses"

Bad Evidence:
"I read the docstring that says 'validates email addresses'"

Problem:
- The docstring is PART OF the same code it claims to validate
- It doesn't independently prove the function works
- The function could be broken and the docstring still claims it works
- This is circular: you're using the code's own description of itself

Better Evidence:
1. Code: Email regex or validation library used
2. Test: assert validate_email("test@example.com") == True
3. Test: assert validate_email("invalid") == False
4. (Optional) Git: Commit message explaining validation rules
```

### Example: The Comment-Only Trap (WEAK)

```
Claim: "Database connection pooling is configured"

Single Source:
"See this comment: # Configure connection pool"

Problem:
- Comment just RESTATES the claim in different words
- Doesn't prove pooling actually happens
- Doesn't show any evidence the pool is used

Better Evidence:
1. Code: connection_pool = DBPool(max_connections=10)
2. Test: Multiple concurrent requests use single pool
3. Git: Commit message explains why pooling was needed
```

### Example: The Inference-from-Code Trap (CIRCULAR)

```
Claim: "This code uses dependency injection"

Circular Logic:
- "See the constructor takes 'service' parameter"
- That's just saying the code has the pattern
- Not proving it's actually used this way

Better Evidence:
1. Code: Constructor explicitly injects dependencies
2. Test: Mocked dependencies are swapped in tests
3. Git: Commit message explains why DI was adopted
4. Code Review: No direct service imports (proving DI is enforced)
```

### Checklist: Is This Evidence Truly Independent?

For each piece of evidence, ask:

- [ ] Does this evidence independently verify the claim?
- [ ] Or just restate the claim in different words?
- [ ] Could I explain this to someone who knows nothing about the claim?
- [ ] Would this evidence convince a skeptic who disagrees?
- [ ] Is this evidence from a DIFFERENT SOURCE than the claim origin?
- [ ] Could the evidence be WRONG while the claim appears correct?

**If any answer is NO → Likely circular evidence. Find another source.**

---

## Source Independence Rules

### When Do Two Sources Count as Truly Independent?

Two sources are **truly independent** when they cannot logically depend on each other and were created by different processes. Here are the rules:

### Rule 1: Code and Its Own Comments/Docstrings Are NOT Independent

```
WRONG (not independent):
- Source 1: Function code
- Source 2: Function's own docstring
- "Evidence": code + docstring = 2 sources
- Problem: docstring was written about the code, not independently

RIGHT (independent):
- Source 1: Function code at auth/jwt.py:45
- Source 2: Test that calls the function
- Reason: test was written to verify behavior, could prove code wrong
```

### Rule 2: Code and Comments at the Same Location Are NOT Independent

```
WRONG:
```python
def charge_card(card):
    # Charges card using Stripe (not independent — same code block)
    stripe.charge(card)
```

RIGHT:
- Source 1: Implementation in payment/service.py:45
- Source 2: Documentation in README.md (written separately)
- Source 3: Test in test_payment.py (exercises the code)
```

### Rule 3: Git Blame/History on Code is NOT Independent Evidence for That Code

```
WRONG:
- Source 1: Code contains async/await syntax
- Source 2: Git blame shows "async added by developer"
- Problem: Git just shows the code was changed, not that async is beneficial

RIGHT:
- Source 1: Code uses async/await
- Source 2: Test verifies concurrent requests process in parallel
- Source 3: Git commit message explains "async needed for 1000 req/s target"
```

### Rule 4: Different Test Files ARE Independent

```
RIGHT (independent):
- Source 1: test_auth_unit.py verifies JWT creation
- Source 2: test_auth_integration.py verifies JWT works with API
- Reason: Different test files, different test conditions, same assertion

Caveat: If both tests are identical (e.g., copy-paste), they're NOT independent
```

### Rule 5: Code Before and After Refactoring Are NOT Independent

```
WRONG:
- Source 1: Old code (uses async/await)
- Source 2: New code (uses async/await after refactor)
- Problem: New code just moved/renamed the pattern, didn't create it independently

RIGHT:
- Source 1: Code pattern exists
- Source 2: Old tests pass (proving pattern works)
- Source 3: New tests added for refactored version
```

### Rule 6: Multiple Tests of the Same Code Can Be Independent

```
RIGHT (independent tests of same code):
- Test 1: Happy path — valid input → success
- Test 2: Error case — invalid input → validation error
- Test 3: Edge case — boundary value → handles correctly
- Reason: Different test conditions, different assertions

These test different aspects, so failures in one don't imply failures in others.
```

### Rule 7: Code and Its Dependencies Are Partially Independent

```
PARTIALLY INDEPENDENT (use with caution):
- Source 1: payment/service.py imports stripe library
- Source 2: stripe library code (open source)
- Use: Verify library is actually installed/used
- Don't use: To claim payment logic is secure (that's code's responsibility)
```

### Rule 8: Inference from Naming IS Independent (But Weak)

```
WEAK INDEPENDENCE:
- Source 1: Function name is "validate_email"
- Source 2: Implementation uses email regex
- Relationship: Function name suggests purpose, code shows implementation
- Weight: Inference (0.3) + Code (1.0) = 1.3 → Below threshold

STRONG INDEPENDENCE:
- Source 1: Function name is "validate_email"
- Source 2: Code uses email regex
- Source 3: Test verifies valid emails pass, invalid emails fail
- Weight: Code (1.0) + Test (0.9) = 1.9 → VERIFIED
```

### Rule 9: Production Metrics and Code Are Independent

```
RIGHT (independent):
- Source 1: Code shows caching logic
- Source 2: Production metrics show cache hit rate 95%
- Reason: Metrics prove code actually works, not just exists

This is strong evidence because:
- Metrics were generated by running actual code
- Metrics could be wrong (proving cache is broken)
- Code could be broken (proving metrics measure nothing)
```

### Rule 10: Documentation from Different Sources Are Independent

```
RIGHT (independent):
- Source 1: README.md (created by team)
- Source 2: API docs (auto-generated from code annotations)
- Source 3: Blog post (written by external author)
- Reason: Each created independently, can contradict each other

WRONG (not independent):
- Source 1: README.md
- Source 2: README.md's "See Also" section pointing to same README
- Reason: Same source quoting itself
```

---

## Practical Step-by-Step Workflow: Cross-Validating a Claim

### Scenario: "Authentication uses bcrypt with 12 rounds"

**Step 1: Extract the Claim Precisely**

```
CLAIM: "User passwords are hashed using bcrypt with 12 rounds"

Components to Verify:
- Algorithm: bcrypt (not SHA256, not plaintext)
- Cost: 12 rounds (not 10, not adaptive)
- Timing: When? (registration? login? both?)
- Scope: All users? Service accounts? API keys?
```

**Step 2: Locate Primary Code Evidence**

```bash
grep -r "bcrypt" src/ --include="*.py"
# src/auth/password.py:12: import bcrypt
# src/auth/password.py:45: bcrypt.hashpw(password, bcrypt.gensalt(12))

grep -r "bcrypt.gensalt" src/ --include="*.py"
# src/auth/password.py:45: rounds = bcrypt.gensalt(12)
```

**Step 3: Document Code Source**

```
Source 1 [Code, 1.0]:
Location: src/auth/password.py:45
Code:
  rounds = bcrypt.gensalt(12)
  hashed = bcrypt.hashpw(password, rounds)
Interpretation: Bcrypt library called with 12 rounds
Confidence: HIGH (explicit constant)
```

**Step 4: Locate Test Evidence**

```bash
grep -r "test.*bcrypt\|test.*password" tests/ --include="*.py"
# tests/auth/test_password.py:67: def test_bcrypt_12_rounds()
# tests/auth/test_password.py:89: def test_password_verification()

# Read the test
cat tests/auth/test_password.py | sed -n '67,85p'
```

**Step 5: Document Test Source**

```
Source 2 [Test, 0.9]:
Location: tests/auth/test_password.py:67
Test: test_bcrypt_12_rounds()
Code:
  hashed = hash_password("mypassword")
  assert bcrypt.checkpw(b"mypassword", hashed)
  # Verify it's actually bcrypt by checking hash prefix
  assert hashed.startswith(b'$2b$12$')  # $2b$ = bcrypt, $12 = rounds
Interpretation: Test verifies bcrypt is used AND round count is 12
Confidence: HIGH (explicit format check)
```

**Step 6: Locate Git Evidence**

```bash
git log -S "bcrypt.gensalt(12)" --oneline src/auth/password.py | head -3
# abc1234 Implement bcrypt password hashing with 12 rounds
# def5678 Increase bcrypt rounds from 10 to 12 for security

git show abc1234 | head -30
# "Implement bcrypt password hashing with 12 rounds
#  - bcrypt provides protection against GPU/ASIC brute force
#  - 12 rounds gives ~200ms hashing time per OWASP guidelines
#  - Cost factor set to current standard (was 8 in old implementation)"
```

**Step 7: Document Git Source**

```
Source 3 [Git, 0.7]:
Location: Commit abc1234
Message: "Implement bcrypt password hashing with 12 rounds"
Evidence:
  - Explicit commit message about bcrypt + 12 rounds
  - Message explains rationale: OWASP timeline, GPU resistance
Interpretation: Design decision was intentional, not accidental
Confidence: HIGH (deliberate architecture choice)
```

**Step 8: Locate Comment/Intent Evidence**

```bash
grep -r "TODO\|FIXME\|HACK\|bcrypt" src/auth/password.py | head -5
# Line 40: # OWASP recommends 12+ rounds for bcrypt (updated 2023)
# Line 45: # 12 rounds ≈ 200ms per NIST SP 800-132
```

**Step 9: Document Comment Source**

```
Source 4 [Comment, 0.5]:
Location: src/auth/password.py:40
Comment: "OWASP recommends 12+ rounds for bcrypt (updated 2023)"
Interpretation: Rounds choice is standards-driven, not arbitrary
Confidence: MEDIUM (references but doesn't link standard)
```

**Step 10: Calculate Combined Weight**

```
Code (1.0) + Test (0.9) + Git (0.7) + Comment (0.5) = 3.1

Threshold: ≥ 1.5 for cross-validation ✓
Confidence: VERIFIED (95%+)
```

**Step 11: State Competing Hypotheses**

```
Hypothesis A: Bcrypt is used with 12 rounds (SUPPORTED)
Evidence: Code, test, git, comment all agree
Status: ACCEPTED

Hypothesis B: Bcrypt is used but rounds are different (10, 14, 16)
Evidence: Code explicitly shows gensalt(12)
Status: REJECTED

Hypothesis C: Old code used bcrypt but was refactored to SHA256
Evidence: Current git shows bcrypt, grep finds no SHA256 in auth
Status: REJECTED

Hypothesis D: 12 rounds only for service accounts, not users
Evidence: Code path called for both; no tenant/role checking
Status: REJECTED
```

**Step 12: Write Final Documentation**

```markdown
## Password Hashing

**Claim:** User passwords are hashed using bcrypt with 12 rounds.

**Evidence Summary:**

| Source | Evidence | Status |
|--------|----------|--------|
| Code | src/auth/password.py:45 uses `bcrypt.gensalt(12)` | ✓ Verified |
| Test | tests/auth/test_password.py:67 checks hash format `$2b$12$` | ✓ Verified |
| Git | Commit abc1234 "Implement bcrypt...with 12 rounds" | ✓ Verified |
| Comment | Line 40 cites OWASP 12+ rounds recommendation | ✓ Verified |

**Confidence Level: VERIFIED (95%+)**

All sources independently confirm bcrypt with 12 rounds. The choice is:
- Intentional (per git message)
- Standards-compliant (per comment referencing OWASP)
- Tested (test verifies hash format)
- Currently implemented (code shows active path)

**Implementation Details:**
- Cost factor: 12 rounds
- Hash time: ~200ms per OWASP SP 800-132
- Applied to: All user passwords (not service accounts)
- Exception: API keys use different mechanism (JWT, see authentication.md)

**How This Could Be Wrong:**
1. Rounds setting could be overridden by environment variable (not found in code)
2. Old hashes from before bcrypt upgrade might not use 12 rounds (migration logic not reviewed)
3. Test could be mocked and not reflect reality (would show in test runner output)

**Mitigation:**
- Code review confirmed no override mechanism
- Tested in staging environment with real password reset
- Migration script adds new_hash with 12 rounds to old entries
```

---

## Anti-Patterns: Common Mistakes in Cross-Validation

### Anti-Pattern 1: "Two Sources = Code + Its Docstring"

```
WRONG:
Claim: "Function calculates tax correctly"
Evidence:
  1. "See the code: def calculate_tax(amount, rate)"
  2. "See the docstring: 'Calculates tax amount'"
Status: NOT CROSS-VALIDATED

Why: Docstring is part of same code artifact, not independent.

CORRECT:
Sources needed:
  1. Code: Implementation detail (calculation formula)
  2. Test: Assertion (example: assert calculate_tax(100, 0.10) == 10)
  3. (Optional) Git or Comment explaining tax rate rules
```

### Anti-Pattern 2: "Multiple Tests = Two Different Test Assertions"

```
WRONG:
Claim: "Error handling covers all cases"
Evidence:
  1. Test 1: assert response.status == 500 on database error
  2. Test 2: assert response.status == 500 on database error (same code path)
Status: NOT INDEPENDENT

Why: Both tests hit same code path, same assertion. They're not independent.

CORRECT:
Sources needed:
  1. Code: Try/except wrapping database call
  2. Test 1: Database error path (happy for error handling)
  3. Test 2: Network timeout path (different error type)
  4. Test 3: Validation error path (different layer)
  OR
  Code + different test files (auth error vs DB error vs network error)
```

### Anti-Pattern 3: "Git Comment = Git History"

```
WRONG:
Claim: "Session tokens expire after 1 hour"
Evidence:
  1. Code: TTL_SECONDS = 3600
  2. Git blame shows: "Alice added this line on 2024-01-15"
Status: Git blame doesn't verify the claim, just shows authorship

CORRECT:
Sources needed:
  1. Code: TTL_SECONDS = 3600 (confirms 1 hour in seconds)
  2. Test: assert token_expires_in_1_hour() (verifies behavior)
  3. Git commit message: "Set session TTL to 1 hour per security policy" (explains why)
```

### Anti-Pattern 4: "Inference + Code = Cross-Validation"

```
WRONG:
Claim: "This code uses the Factory pattern"
Evidence:
  1. Code: "See this create_user() function"
  2. Inference: "Function names starting with 'create_' are factories"
Status: Inference (0.3) + Code (1.0) = 1.3 → BELOW THRESHOLD

Why: Inference adds minimal credibility to code evidence.

CORRECT:
Sources needed:
  1. Code: Factory implementation (create methods returning instances)
  2. Test: Test injects different implementations, verifying factory is used
  3. Comment or Git: Explaining why factory pattern was chosen
  Combined: Code (1.0) + Test (0.9) = 1.9 → VERIFIED
```

### Anti-Pattern 5: "Claim + Restated Claim = Two Sources"

```
WRONG:
Claim: "Database uses connection pooling"
Evidence:
  1. Configuration file: MAX_POOL_SIZE = 10
  2. Code comment: "# Configure pool size to 10"
Status: Both just restate the configuration, don't prove pooling works

Why: Neither source independently verifies pooling is actually used.

CORRECT:
Sources needed:
  1. Code: ConnectionPool instantiation, size parameter = 10
  2. Test: Multiple concurrent requests use <5 actual DB connections (proves reuse)
  3. Git or Comment: Explanation of why pooling was needed (performance?)
```

### Anti-Pattern 6: "One Test in Different Execution Paths"

```
WRONG:
Claim: "Error handling covers success AND failure cases"
Evidence:
  1. Single test that: tries to create order, catches exception if it fails
Status: One test with conditional logic, not independent evidence

Why: Test doesn't distinguish between tested and untested paths.

CORRECT:
Sources needed:
  1. Test 1: Happy path (valid order creation)
  2. Test 2: Sad path (invalid order fails)
  3. Optional: Code review confirming both paths tested
```

### Anti-Pattern 7: "Outdated Code Path"

```
WRONG:
Claim: "API validates input using regex"
Evidence:
  1. Code: def validate_email(email): return re.match(PATTERN, email)
  2. Comment: "Email validation using regex"
Status: Code exists but might be dead code/unused

Why: No evidence the function is actually called on API requests.

CORRECT:
Evidence added:
  1. Code: Input validation middleware calls validate_email()
  2. Test: API request with invalid email returns 400
  3. Git: Recent commit "Activate email validation on POST /register"
```

### Anti-Pattern 8: "Test Mocks Reality Incorrectly"

```
WRONG:
Claim: "Payment processing retries on failure"
Evidence:
  1. Code: Retry logic with max_attempts=3
  2. Test: with mock.patch('stripe.charge', side_effect=StripeError)
  Status: Test mocks error, but real Stripe might behave differently

Why: Mock might not accurately represent real service behavior.

CORRECT:
Sources added:
  1. Integration test against staging Stripe account
  2. Production monitoring logs showing actual retries happening
  3. Git history: "Tested against real Stripe API (not mock)"
```

### Anti-Pattern 9: "Commented-Out Code as Evidence"

```
WRONG:
Claim: "System supports legacy API v1"
Evidence:
  1. Code: "# old_api_v1_handler() — deprecated but kept for reference"
Status: Commented-out code is not active evidence

Why: Code isn't executed, doesn't prove support.

CORRECT:
Evidence needs:
  1. Active code: Routes registered for /v1/ endpoints
  2. Test: Requests to /v1/ return valid responses
  3. Git: Migration plan showing v1 deprecation timeline
```

### Anti-Pattern 10: "Single Source Claimed as Multiple"

```
WRONG:
Claim: "User authentication uses bcrypt"
Evidence:
  1. import bcrypt
  2. bcrypt.hashpw()
  3. bcrypt.checkpw()
Status: All from same code file, same source

CORRECT:
Evidence needs:
  1. Code location: src/auth/password.py (implementation)
  2. Test location: tests/auth/test_password.py (behavior)
  3. Different evidence type: Git or Comment (rationale)
```

---

## Summary: Cross-Validation Best Practices

### Process Checklist (Apply to Every Major Claim)

- [ ] Write claim precisely (not vague)
- [ ] Find Code evidence (1.0)
- [ ] Find Test evidence (0.9) — different source, independent assertion
- [ ] Find Git/Comment evidence (0.7/0.5) — rationale or history
- [ ] Calculate combined credibility weight
- [ ] Is weight ≥ 1.5? If NO → claim needs more evidence
- [ ] State competing hypothesis for each claim
- [ ] Mark hypothesis as REJECTED or ACCEPTED with evidence
- [ ] Document potential weaknesses
- [ ] Assign final confidence level (VERIFIED/HIGH/MEDIUM/LOW/UNKNOWN)
- [ ] Include source citations (file:line, test:name, commit hash)

### Evidence Gathering Priority

1. **Always start with Code** (highest weight 1.0)
2. **Add Tests** (second highest 0.9) — proves code actually works
3. **Check Git** (0.7) — explains design decisions
4. **Review Comments** (0.5) — documents intent
5. **Use Inference** (0.3) — only when other sources unavailable

### Red Flags (Stop and Investigate)

- [ ] Only one type of evidence available
- [ ] Test is disabled or skipped (doesn't count as 0.9)
- [ ] Git history shows recent changes to claim (stale evidence)
- [ ] Comment contradicts code (they disagree — document both)
- [ ] Sources disagree on key detail (requires deeper analysis)
- [ ] No test coverage for critical path (evidence gap)

### Quality Thresholds

| Confidence Level | Combined Weight | Use For |
|------------------|-----------------|---------|
| VERIFIED (95%+) | ≥ 2.6 | Architecture decisions, security controls, compliance |
| HIGH (80-85%) | 1.5-2.5 | Core functionality, data handling |
| MEDIUM (50-70%) | 1.0-1.5 | Implementation details, non-critical features |
| LOW (<50%) | < 1.0 | Observations, probable patterns, needs verification |
| UNKNOWN | No code | Pure inference, untested assumptions |

### When to Stop Gathering Evidence

- You've achieved threshold weight (≥ 1.5 for HIGH, ≥ 2.6 for VERIFIED)
- You've gathered all reasonably available sources
- Continuing would hit diminishing returns
- You've explicitly stated competing hypotheses

You don't need perfect certainty (100%), but you do need credible evidence (≥1.5 combined weight).
