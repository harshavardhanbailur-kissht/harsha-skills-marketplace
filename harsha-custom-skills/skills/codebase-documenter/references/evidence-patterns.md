# Evidence Patterns for Code Documentation

## Updated Source Hierarchy: Credibility Weights (Research-Analyst Methodology)

All claims in codebase documentation must be grounded in this hierarchy with explicit credibility weighting:

```
Code (direct observation)           [Credibility: 1.0]
    ├─ Class/function definitions (executable logic)
    ├─ Data types, signatures, return values
    ├─ Explicit error handling (try/catch blocks)
    ├─ Dependencies, imports (what libraries are used)
    ├─ Configuration values (hardcoded, env vars)
    └─ Request/response handling (routes, handlers)

Tests (behavioral contracts)         [Credibility: 0.9]
    ├─ Unit test assertions (assert X == Y)
    ├─ Integration test setup (with pytest.fixture)
    ├─ Mock/stub definitions (what services are depended on)
    ├─ Expected error conditions (pytest.raises, expect.throw)
    ├─ Passing vs skipped tests (confidence signal)
    └─ Mock call verification (assert_called_with)

Git History (decision evidence)      [Credibility: 0.7]
    ├─ Commit messages (intent + context)
    ├─ Author accountability (git blame output)
    ├─ PR/issue descriptions (architecture narrative)
    ├─ Revert patterns (rejected approaches)
    ├─ Migration history (git log --follow for renames)
    └─ Authorship timestamps (code age/staleness)

Comments (author explanations)       [Credibility: 0.5]
    ├─ Intent comments ("why") — HIGH weight
    ├─ Description comments ("what") — LOW weight (redundant)
    ├─ TODO/HACK/BUG/FIXME markers (technical debt)
    ├─ Inline clarifications (gotchas, edge cases)
    ├─ Architecture comments (design rationale)
    └─ License headers, auto-generated docs — NOT evidence

Inference (logical deduction)        [Credibility: 0.3]
    ├─ Pattern matching (seen this before → likely same intent)
    ├─ Naming conventions (function named cache_* → likely caching)
    ├─ Structural inference (file in /migrations/ → DB migration)
    ├─ Dependency graph inference (imports reveal architecture)
    └─ DANGER: Inference alone NEVER sufficient for HIGH confidence
```

**Critical rule:** Never claim something is true based on inference alone. **Minimum combined credibility weight: 1.5** (e.g., Code 1.0 + Comment 0.5 = 1.5, or Code 1.0 + Git 0.7 = 1.7, or Test 0.9 + Git 0.7 = 1.6).

**Cross-Validation Examples:**
- Code (1.0) + Test (0.9) = 1.9 → VERIFIED ✓
- Code (1.0) + Git (0.7) = 1.7 → HIGH ✓
- Code (1.0) + Comment (0.5) = 1.5 → HIGH ✓
- Code (1.0) + Inference (0.3) = 1.3 → MEDIUM ✗ (needs more)
- Test (0.9) + Git (0.7) = 1.6 → HIGH ✓ (code-free but cross-validated)
- Comment (0.5) + Inference (0.3) = 0.8 → LOW ✗ (insufficient)

---

## Section 1: Test Assertion Reading (Credibility: 0.9)

Tests are the most reliable documentation of what code **actually does** (as opposed to what it's supposed to do). Test assertions form behavioral contracts.

### Pattern Recognition in Test Assertions

#### Pattern 1: Equality Assertions (`assert X == Y`)

**Code Example (pytest):**
```python
def test_calculate_discount():
    order = Order(subtotal=100.00, customer_type="premium")
    result = calculate_discount(order)
    assert result == 15.00  # 15% discount for premium
```

**Contract extracted:**
- Function signature: `calculate_discount(Order) → float`
- Precondition: `Order` has `subtotal` and `customer_type` attributes
- Postcondition: Returns 15.00 for premium customer with $100 subtotal
- Behavioral guarantee: Function is deterministic (same input → same output)

**Code Example (unittest/Java):**
```java
@Test
public void testGetUserById() {
    User user = userRepository.getById(1);
    assertEquals("Alice", user.getName());
    assertEquals("alice@example.com", user.getEmail());
}
```

**Contract extracted:**
- Users are persisted with id, name, email attributes
- Repository lookup by ID returns correct user
- Absence of assertion → no constraint on password/phone/address visibility

---

#### Pattern 2: Exception Assertions (`pytest.raises()`, `assertThrows()`, `expect().toThrow()`)

**Code Example (pytest):**
```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_email_format():
    with pytest.raises(ValidationError) as exc_info:
        create_user(email="not_an_email")
    assert "Invalid email" in str(exc_info.value)
```

**Contract extracted:**
- `divide()` raises `ZeroDivisionError` when denominator is 0 (not None, not inf, not default value)
- `create_user()` raises `ValidationError` (not generic `Exception`) with message containing "Invalid email"
- Function fails fast on invalid input (doesn't continue)

**Code Example (Jest/JavaScript):**
```javascript
test('should throw NotFoundError when user does not exist', () => {
  expect(() => getUser(9999)).toThrow(NotFoundError);
});
```

**Contract extracted:**
- User lookup raises typed exception (not null, not undefined)
- Exception type itself is meaningful (can be caught separately from other errors)

**Code Example (Go):**
```go
func TestNoRowsError(t *testing.T) {
    db := setupTestDB()
    _, err := db.GetUser(context.Background(), 999)
    if !errors.Is(err, sql.ErrNoRows) {
        t.Fatalf("expected sql.ErrNoRows, got %v", err)
    }
}
```

**Contract extracted:**
- Database query returns `sql.ErrNoRows` (not `nil`, not generic error)
- Function respects Go error wrapping patterns (`errors.Is`)
- Test uses sentinel error comparison (standard Go pattern)

---

#### Pattern 3: Mock Setup and Expectations (`with.patch()`, `@Mock`, `.mockReturnValue()`)

**Code Example (pytest with mock):**
```python
from unittest.mock import patch, MagicMock

def test_send_welcome_email():
    with patch('email_service.send_email') as mock_send:
        user = User(email="new@example.com", name="Bob")
        create_user(user)

        mock_send.assert_called_once_with(
            to="new@example.com",
            subject="Welcome!",
            template="welcome"
        )
```

**Contract extracted:**
- `create_user()` calls external email service (not built-in)
- Email is sent synchronously during user creation (not queued)
- Email recipient matches user email, subject is exactly "Welcome!"
- Function sends email only once (not retries, not multiple sends)

**Code Example (unittest with MagicMock):**
```java
@Test
public void testPaymentChargesCard() {
    PaymentGateway mockGateway = mock(PaymentGateway.class);
    when(mockGateway.charge(any())).thenReturn(TransactionResult.SUCCESS);

    PaymentService service = new PaymentService(mockGateway);
    Order order = new Order(customerId=1, amount=50.00);
    service.processPayment(order);

    verify(mockGateway).charge(argThat(transaction ->
        transaction.getAmount() == 50.00 &&
        transaction.getCurrency().equals("USD")
    ));
}
```

**Contract extracted:**
- `PaymentService` accepts injected gateway dependency (dependency injection pattern)
- `processPayment()` calls gateway `charge()` method exactly once
- Charge amount and currency are passed correctly
- Service depends on external payment gateway (not internal implementation)

---

#### Pattern 4: State Transition Assertions (object state changes)

**Code Example (pytest):**
```python
def test_order_status_transitions():
    order = Order(status="pending")
    assert order.status == "pending"

    order.confirm()
    assert order.status == "confirmed"
    assert order.confirmed_at is not None

    order.ship()
    assert order.status == "shipped"
    assert order.tracking_number is not None
```

**Contract extracted:**
- Order lifecycle: pending → confirmed → shipped (state machine)
- State transitions update metadata (confirmed_at, tracking_number)
- Each state has associated attributes
- Transitions are explicit methods (not implicit)

---

#### Pattern 5: Setup/Fixture Contracts (what preconditions are required)

**Code Example (pytest fixtures):**
```python
@pytest.fixture
def authenticated_user(db):
    user = User.create(email="user@example.com")
    user.password_hash = hash_password("password")
    db.session.add(user)
    db.session.commit()
    return user

def test_fetch_user_profile(authenticated_user):
    result = get_user_profile(authenticated_user.id)
    assert result.email == authenticated_user.email
    assert result.is_active
```

**Contract extracted:**
- User persistence requires database session management
- Password stored as hash (security implication)
- User fetching by ID requires existing user
- Profile data includes at least email and is_active flag
- Test setup shows password hashing is synchronous

---

### Multi-Framework Assertion Patterns

| Framework | Assert Syntax | Exception Pattern | Mock Pattern |
|-----------|---------------|-------------------|--------------|
| **pytest** | `assert x == y` | `with pytest.raises(Error):` | `@patch()` decorator / `with patch()` context |
| **unittest** | `self.assertEqual(x, y)` | `self.assertRaises(Error)` | `@patch()` / `unittest.mock.patch()` |
| **Jest (JS)** | `expect(x).toBe(y)` | `expect().toThrow(Error)` | `jest.mock()` / `jest.fn()` |
| **Mocha (JS)** | `assert.equal(x, y)` | `assert.throws()` | `sinon.stub()` / `sinon.mock()` |
| **JUnit (Java)** | `assertEquals(x, y)` | `assertThrows(Error.class)` | `@Mock` / `Mockito.mock()` |
| **Go testing** | `if x != y { t.Fatal() }` | `errors.Is(err, target)` / `t.Fatalf()` | `interface{}` for mocking (no native mock lib) |
| **RSpec (Ruby)** | `expect(x).to eq(y)` | `expect { }.to raise_error(Error)` | `allow().to receive()` / `double()` |

---

### Test Absence as Evidence

**Critical insight:** If a test does NOT exist for a behavior, that behavior may not be implemented.

**Example:**
```python
# Tests exist for these:
def test_create_order():  # ✓ Exists
def test_order_persistence_to_db():  # ✓ Exists
def test_order_status_confirmed():  # ✓ Exists

# But no test for:
# def test_order_cancellation_after_shipped():  # NOT FOUND
# def test_order_refund_on_cancellation():  # NOT FOUND
# def test_concurrent_order_updates():  # NOT FOUND
```

**Documentation impact:**
- Claim: "Orders can be cancelled after shipping" → Search for test
- No test found → Feature may not exist or untested
- Document as: "Order cancellation may not support post-shipment cancellations (no test found)"

---

### Reading Test Assertions (Original Section, Enhanced)

**Example: Authentication test with contracts extracted**

```python
def test_login_with_invalid_password():
    user = User.create(email="user@example.com", password="correct")

    with pytest.raises(PasswordError):
        user.verify_password("wrong_password")

    assert not user.is_authenticated
```

**Behavioral contracts extracted:**
1. Contract: `User.create(email, password)` succeeds with email/password
2. Contract: `verify_password(wrong_pass)` raises `PasswordError` (typed exception, not generic)
3. Contract: `user.is_authenticated` defaults to `False` or becomes `False` on failed verification
4. Non-contracts (NOT guaranteed, since no test for them):
   - Account lockout after N failed attempts (not tested)
   - Password reset flow (not tested)
   - Email confirmation requirement (not tested)

**Strength of evidence:** HIGH (Code 1.0 + Test 0.9 = 1.9 weight)


---

## Section 2: Git History Mining (Credibility: 0.7)

Git history reveals **why** decisions were made, not just **what** code does. It's the second most reliable source of architectural intent after code and tests.

### Subsection 2.1: Commit Message Pattern Analysis

**Conventional Commits format (standardized intent signaling):**
```
feat: add user authentication system
feat(payment): add Razorpay integration
fix: resolve race condition in cache invalidation
fix(auth): correct password hash comparison timing attack
refactor: extract payment processing into service class
refactor(db): normalize user_accounts schema
docs: update API documentation
test: add integration tests for payment flow
chore: bump dependency versions
```

**Extracting design intent from commit messages:**

| Message Type | Information Density | Example | Evidence Value |
|--------------|-------------------|---------|-----------------|
| Generic | VERY LOW | "fix issue", "WIP", "cleanup" | No design intent revealed |
| Issue reference only | LOW | "fix: #456" | Requires external issue lookup |
| Specific behavior | HIGH | "fix: prevent double-charge on network timeout" | Clear architectural constraint |
| Rationale included | VERY HIGH | "fix: retry on 503 instead of failing instantly (Razorpay SLA requirement)" | Decision logic visible |
| Negative intent | HIGH | "revert: remove in-memory cache (memory leak on concurrent writes)" | Documents what NOT to do |

**Practical extraction example:**

```bash
$ git log --oneline -n 30 -- src/payment/stripe.py | head -20
a1b2c3d (HEAD) fix(payment): handle Stripe webhook signature verification failures
9f8e7d6 feat(payment): add Stripe charge retry with exponential backoff
8a7b6c5 fix(payment): correct currency conversion for INR transactions
7d6c5b4 refactor(payment): extract payment validation logic
6c5b4a3 feat(payment): add Stripe integration (replaces Razorpay)
5b4a392 revert: remove Razorpay integration (deprecated API)
4a3928f fix(payment): race condition in Razorpay settlement processing
```

**Design narrative derived:**
1. Original: Razorpay integration (commit 5b4a392)
2. Problem: Race condition in settlement (commit 4a3928f)
3. Decision: Migrate to Stripe (commit 6c5b4a3, explicit feat message)
4. New problem: Currency handling for INR (commit 8a7b6c5)
5. Reliability addition: Exponential backoff on charge retry (commit 9f8e7d6)
6. Latest issue: Webhook signature verification (commit a1b2c3d)

**What this history tells us:**
- Payment integration is a critical, evolving component (many commits)
- Maintainers respond to discovered issues (race condition → fix, currency issue → fix)
- Technology choices are documented (Razorpay → Stripe migration is explicit)
- Reliability patterns are intentional (exponential backoff added after retry feature)

---

### Subsection 2.2: Git Blame for Authorship + Temporal Context

**Basic git blame output:**
```bash
$ git blame src/auth/password.py | head -5
abc1234 (Alice Smith    2023-06-15) def hash_password(password):
abc1234 (Alice Smith    2023-06-15)     """Hash password using bcrypt."""
def2456 (Bob Johnson    2024-01-20)     return bcrypt.hashpw(
def2456 (Bob Johnson    2024-01-20)         password.encode('utf-8'),
def2456 (Bob Johnson    2024-01-20)         bcrypt.gensalt(12)
```

**What blame reveals:**

| Signal | Interpretation | Confidence |
|--------|-----------------|-----------|
| Author: Alice Smith, Date: 2023-06-15 | Alice decided on bcrypt in June 2023 | Authorship + timestamp = can contextualize library versions |
| Author: Bob Johnson, Date: 2024-01-20 | Updated hashing logic 8 months later | Code may have evolved; original intent may differ from current state |
| Many authors on same function | Multiple people have touched this code | Risk: implicit agreements or design understanding lost |
| Author: <commit hash> | Original file creation author | Can trace feature from conception |

**Contextualizing temporal information:**

```bash
$ git blame --date=short src/config/database.py | grep "max_connections"
5f6g7h8 (Carol White    2021-03-10) max_connections=50,
```

**Implication:** Max connections setting from March 2021. Check if:
- PostgreSQL default changed since then?
- Load patterns different now (original code written for 10 users, now 1000)?
- Should this be revisited with current architectural needs?

**Detecting stale code:**
```bash
$ git log -1 --format="%h %ad" --date=short src/legacy/old_auth.py
3b4c5d6 2019-05-20
```

**Assessment:** Code hasn't been touched since May 2019 (5 years old). Consider:
- Why hasn't this been refactored or removed?
- Is it dead code that can be deleted?
- Is it stable but genuinely unused?
- Is it a workaround for a system that no longer exists?

---

### Subsection 2.3: Git Log for Design Timeline (`git log --follow`)

**Following file renames and migrations:**
```bash
$ git log --follow --oneline src/payment/processor.py
a1b2c3d refactor: rename payment_service.py to processor.py
9f8e7d6 feat: merge legacy_payment_handler.py into payment_service.py
8a7b6c5 refactor: extract payment_service.py from orders.py
7d6c5b4 feat(initial): orders.py with inline payment handling
```

**Migration story revealed:**
1. v1: Payment logic inline in orders.py (tightly coupled)
2. v2: Extracted to separate payment_service.py (separation of concerns)
3. v3: Merged legacy handler into payment_service (consolidation)
4. v4: Renamed to processor.py (semantic shift)

**Documentation implication:** Design evolved from monolithic to modular. Explain this evolution; next developer won't wonder why code is organized this way.

**Finding orphaned code:**
```bash
$ git log -p --all -- src/deprecated/old_cache.py | head -100
# (shows history but file no longer in HEAD)
```

**Questions to answer:**
- When was this code deleted? (find commit with -D flag)
- Why was it deleted? (read commit message)
- Can we find a safer, newer approach by examining what replaced it?

---

### Subsection 2.4: PR/Issue Descriptions as Architecture Narrative

**GitHub Issue template (decision context):**
```
Title: "Add rate limiting to API endpoints"

Description:
"Problem: Users on free tier hitting 1000 req/min, impacting infrastructure.

Requirement: Limit free tier to 10 req/min, premium tier to 1000 req/min.

Implementation approach: Use Redis for distributed state (supports multi-instance).
Sliding window algorithm for precision. TTL = 60 seconds.

Why not in-memory? We run 3 API instances; need shared state.
Why not database? TTL-based eviction is cheaper in Redis than DB roundtrips.

Affected endpoints: /api/v1/users, /api/v1/orders, /api/v1/search
Excluded endpoints: /health, /status (monitoring endpoints)

Risks: Redis dependency adds failure mode. Graceful degradation: if Redis down,
allow requests through (overage preferred to outage).

Timeline: Needed by end of Q3 (September 15) due to free tier abuse.
```

**Architectural insights extracted:**

| Information | Significance | Evidence Type |
|-------------|-------------|----------------|
| Rate limiting is later addition | Not original design; reactive feature | Git + PR context |
| Free tier + premium tier distinction | Business model detail (SaaS) | PR description |
| 10 vs 1000 req/min | Service SLA commitment | Business requirement |
| Redis chosen, not database | Architecture decision trade-off | PR discussion/rationale |
| Multi-instance requirement | Infrastructure constraint (scale) | Why Redis? (shared state) |
| Sliding window algorithm | Implementation detail (precision) | Technical approach |
| Specific endpoints excluded | Security/monitoring policy | Operational concern |
| Graceful degradation preference | Reliability philosophy (availability > accuracy) | Risk mitigation strategy |
| Time-critical deadline | Reputational issue (free tier abuse) | Business context |

**Documentation strategy:** Include PR/issue context in handoff. New developer understands "this wasn't in original spec" and "here's why Redis, not in-memory".

---

### Subsection 2.5: Revert Commits as Negative Evidence (What Didn't Work)

**Finding reverts:**
```bash
$ git log --grep="Revert" --oneline | head -20
5d4c3b2 Revert "feat: add in-memory cache for user lookups"
4c3b2a1 Revert "refactor: migrate to async database queries"
3b2a190 Revert "fix: attempt to fix intermittent auth timeouts"
```

**Investigating a revert:**
```bash
$ git show 5d4c3b2
commit 5d4c3b2
Author: Alice Smith <alice@company.com>
Date:   2024-02-10

    Revert "feat: add in-memory cache for user lookups"

    This reverts commit abc1234.

    Reason: Memory leak on concurrent updates. Cache invalidation
    failed when multiple instances running. Under load (100 concurrent
    requests), memory usage grew from 500MB → 5GB in 10 minutes.

$ git show abc1234
commit abc1234
Author: Bob Johnson <bob@company.com>
Date:   2024-01-15

    feat: add in-memory cache for user lookups

    Single-instance optimization. Reduces DB queries by 80%.
    Expected to cut page load time from 500ms → 100ms.
```

**Evidence analysis:**
1. Original intent: Optimize page load (legitimate goal)
2. Original scope: Single-instance optimization (key assumption)
3. Actual deployment: Multi-instance environment
4. Failure mode: Memory leak on concurrent writes (cache invalidation bug)
5. Impact: Catastrophic (5GB memory growth)
6. Resolution: Reverted (abandon feature entirely)

**Documentation impact:**
- Never implement in-memory caching without cross-instance invalidation
- If caching is needed, use Redis/distributed cache
- Document: "In-memory caching was attempted in Jan 2024 but reverted due to memory leak in multi-instance environment"

**Pattern: Multiple reverts on same feature:**
```bash
$ git log --oneline | grep -i "payment"
xyz9999 Revert "Revert 'fix: payment timeout handling'"
abc8888 Revert "fix: payment timeout handling"
def7777 fix: payment timeout handling
```

**Implication:** Genuine disagreement or oscillation between approaches. Investigate:
- Why was fix needed? (What was the original problem?)
- Why was it reverted? (What new problem did it cause?)
- Why was the revert reverted? (What changed?)

Document this as: "Payment timeout handling is difficult. Solutions have been attempted 3+ times. See commits [hashes] for details. Current approach [X] preferred because [reason]."

---

### Subsection 2.6: Commit Message Patterns Specific to Architectural Decisions

**Identifying refactoring momentum:**
```bash
$ git log --oneline --grep="refactor" -n 10 -- src/core/
a1b2c3d refactor: simplify payment validation logic
9f8e7d6 refactor: extract user service methods
8a7b6c5 refactor: remove unused database utilities
7d6c5b4 refactor: consolidate error handling across services
```

**Signal:** Active refactoring agenda. Codebase is evolving toward modular design. Likely:
- Code quality is improving
- Maintainers have identified patterns worth extracting
- Original design was monolithic but is being systematized

**Identifying bug-fix intensity:**
```bash
$ git log --oneline --grep="^fix" -n 15 -- src/auth/
5d4c3b2 fix(auth): prevent brute force on login endpoint
4c3b2a1 fix(auth): JWT token validation wasn't checking expiry
3b2a190 fix(auth): session cookie not secure on HTTP
2a1908f fix(auth): password reset token reuse vulnerability
1908def fix(auth): CORS allowed all origins in auth endpoints
```

**Signal:** Auth module has recurring issues. Questions to answer:
- Are fixes reactive (bugs discovered in production) or proactive (security review)?
- Is test coverage insufficient? (Why weren't these caught earlier?)
- Is this module underfunded/deprioritized?

Document: "Authentication module has 5+ security fixes in recent history. Consider: (a) enhanced code review, (b) security-focused testing, (c) audit by external specialist."

---

## Section 3: Code Pattern Evidence (Credibility: 1.0)

Code is the primary evidence source: executable, specific, verifiable. Patterns in code reveal architectural decisions.

### Subsection 3.1: Import Statements as Dependency Evidence

**What imports reveal:**
```python
# src/payment_service.py
from stripe import Charge, Customer, Webhook
import razorpay
from redis import Redis
from sqlalchemy import create_engine
from logging import getLogger
import numpy as np
```

**Evidence extracted:**

| Import | What It Reveals | Architectural Implication |
|--------|-----------------|---------------------------|
| `from stripe import Charge` | Direct Stripe SDK usage | Stripe is primary payment processor |
| `import razorpay` | Alternative payment processor available | Legacy integration or fallback? |
| `from redis import Redis` | Caching/session layer used | Performance optimization, data tiering |
| `from sqlalchemy import create_engine` | ORM in use, not raw SQL | Database abstraction preference |
| `from logging import getLogger` | Structured logging configured | Debugging/monitoring capability |
| `import numpy as np` | Heavy numerical computation | Data science or ML integration |

**Inference confidence:** HIGH (Code 1.0 + architecture pattern = verifiable)

**Red flag patterns:**
```python
# src/legacy/payment.py
import sys, os, pickle
import urllib2  # Python 2 code!
from __future__ import print_function
```

**Signals:** Code is old, potentially abandoned. Questions:
- Is this Python 2 code still running? (EoL since 2020)
- Is this being actively maintained or left for legacy compatibility?
- Should this be prioritized for migration?

**Conditional imports (feature flags):**
```python
try:
    from newlib import feature_x
    HAS_NEW_FEATURE = True
except ImportError:
    from legacylib import feature_x
    HAS_NEW_FEATURE = False
```

**Evidence:** Feature rollout in progress. Either:
- Testing new library (A/B testing)
- Gradual migration from legacy to new
- Fallback for older environments

---

### Subsection 3.2: Error Handling Patterns as Reliability Evidence

**Pattern 1: Silent swallowing (DANGER):**
```python
def fetch_user(user_id):
    try:
        return db.query(User).filter_by(id=user_id).first()
    except Exception:
        return None  # ← Silent failure, no logging
```

**Evidence:**
- Errors are ignored (reliability risk)
- Caller can't distinguish "not found" from "error"
- Debugging will be difficult (no logs)
- Confidence: MEDIUM (code pattern only)

**Pattern 2: Typed exception handling (GOOD):**
```python
def fetch_user(user_id):
    try:
        return db.query(User).filter_by(id=user_id).first()
    except DatabaseError as e:
        logger.error(f"Database query failed: {e}", exc_info=True)
        raise UserFetchError(f"Could not retrieve user {user_id}") from e
    except TypeError as e:
        logger.error(f"Invalid user_id type: {user_id}", exc_info=True)
        raise InvalidUserIdError(f"user_id must be int, got {type(user_id)}") from e
```

**Evidence:**
- Errors are caught and re-raised as domain exceptions (good separation)
- Logging is structured (debugging enabled)
- Exception chaining preserves original stack (Python 3 best practice)
- Type validation is explicit (robustness)
- Confidence: HIGH (code pattern + defensive programming intent clear)

**Pattern 3: Circuit breaker pattern (resilience):**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_external_api(endpoint):
    return requests.get(endpoint, timeout=5)
```

**Evidence:**
- External API calls are protected (reliability engineering)
- Automatic recovery after 60 seconds (graceful degradation)
- Threshold of 5 failures before tripping (tunable sensitivity)
- Confidence: HIGH (explicit resilience architecture)

**Pattern 4: Retry with backoff (reliability):**
```python
def charge_payment_with_retry(amount, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            return stripe.Charge.create(amount=amount)
        except stripe.error.RateLimitError:
            if attempt < max_retries:
                wait_time = 2 ** attempt  # exponential backoff
                logger.info(f"Rate limited, retrying in {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
```

**Evidence:**
- Transient failures (rate limits) are handled with retry logic
- Exponential backoff prevents thundering herd (2^1, 2^2, 2^3 = 2, 4, 8 seconds)
- Max retries prevent infinite loops
- Confidence: HIGH (specific retry strategy visible)

---

### Subsection 3.3: Configuration Loading as Deployment Assumption Evidence

**Pattern 1: Environment variable configuration (12-factor app):**
```python
# config.py
import os

DATABASE_URL = os.environ['DATABASE_URL']  # Required, no default
API_KEY = os.environ.get('API_KEY', 'default_key')  # Optional with default
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'  # Boolean parsing
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
```

**Evidence:**
- Configuration is environment-driven (standard 12-factor pattern)
- Some configs are required (DATABASE_URL) — no default means must be set
- Some configs are optional (API_KEY, REDIS_URL) — have sensible defaults
- Boolean conversion is explicit (error-prone, but intentional)
- Confidence: HIGH (deployment assumptions visible)

**Assumptions revealed:**
- Database URL must be provided at runtime (database is not bundled)
- Redis is optional but defaults to localhost (caching is optional feature)
- DEBUG flag controls behavior dynamically (no rebuild for dev/prod)

**Pattern 2: Configuration file loading (less portable):**
```python
import yaml

with open('/etc/app/config.yaml') as f:
    config = yaml.safe_load(f)

database_host = config['database']['host']
database_port = config['database']['port']
```

**Evidence:**
- Configuration is file-based (requires file presence on filesystem)
- YAML format (human-readable, but less portable than env vars)
- Assumptions: File exists at `/etc/app/config.yaml` (hard-coded path)
- Confidence: MEDIUM (file path assumption, not environment-agnostic)

**Risk:** Deployment must set up this file. Env vars are more container-friendly.

**Pattern 3: Hardcoded configuration (DANGER):**
```python
# src/config.py
DATABASE_HOST = "prod-db.example.com"
API_KEY = "sk_live_abc123xyz789"
DEBUG = False
```

**Evidence:**
- Configuration is baked into code (no environment separation)
- Secrets are exposed in source (CRITICAL SECURITY ISSUE)
- Cannot run same code in multiple environments without rebuild
- Confidence: HIGH (but evidence of poor practice)

---

### Subsection 3.4: Middleware Chains and Security Architecture

**Example: Express.js middleware (security headers):**
```javascript
// src/server.js
app.use(helmet());  // ← Security headers (HSTS, X-Frame-Options, CSP)
app.use(express.json({ limit: '10mb' }));  // ← Request size limit
app.use(cors({ origin: 'https://trusted.example.com' }));  // ← CORS policy
app.use(rateLimit({ windowMs: 60000, max: 100 }));  // ← Rate limiting
app.use(authMiddleware);  // ← Authentication before routes
app.use(authorize);  // ← Authorization before routes
```

**Security evidence extracted:**

| Middleware | Security Control | Evidence |
|-----------|-----------------|----------|
| `helmet()` | HTTP security headers | Defense against XSS, clickjacking, MIME sniffing |
| `limit: '10mb'` | Request payload validation | DoS protection (unbounded uploads rejected) |
| `cors()` | Origin restriction | CSRF/cross-origin attack mitigation |
| `rateLimit()` | Rate limiting | DDoS/brute-force protection (100 req/min) |
| `authMiddleware` | Authentication check | Access control (who are you?) |
| `authorize` | Authorization check | Access control (what are you allowed to do?) |

**Middleware order matters:**
- Auth before routes → Unauthenticated requests rejected early
- Rate limiting before auth → Brute-force attacks are rate-limited
- Security headers applied globally → No accidental insecure routes

**Confidence:** HIGH (middleware chain reveals security architecture)

**Missing middleware (red flag):**
```javascript
// No helmet()
// No rate limiting
// No CORS restriction
// No input validation
```

**Evidence:** Likely default configuration (not hardened). Document as: "Security middleware not explicitly configured; relies on framework defaults."

---

### Subsection 3.5: Decorator/Annotation Patterns as Framework Evidence

**Python decorators (Flask):**
```python
@app.route('/api/users/<user_id>', methods=['GET'])
@require_auth('admin')  # ← Custom authorization
@cache(ttl=300)  # ← Caching directive
@validate_json(UserSchema)  # ← Input validation
def get_user(user_id):
    """Retrieve user by ID."""
    return User.query.get(user_id).to_dict()
```

**Framework evidence:**

| Decorator | Framework Pattern | Implication |
|-----------|-------------------|-------------|
| `@app.route()` | Flask web framework | HTTP routing framework in use |
| `@require_auth('admin')` | Custom decorator | Role-based access control (RBAC) implemented |
| `@cache(ttl=300)` | Caching framework | Performance optimization; responses cached 5 minutes |
| `@validate_json()` | Input validation framework | Schema validation before handler execution |

**Java annotations (Spring):**
```java
@RestController
@RequestMapping("/api/payments")
public class PaymentController {

    @PostMapping("/charge")
    @PreAuthorize("hasRole('PREMIUM')")  // ← Authorization annotation
    @Transactional  // ← Database transaction management
    public ResponseEntity<ChargeResponse> chargeCard(
        @RequestBody @Valid ChargeRequest request,  // ← Input validation
        @RequestHeader("X-Idempotency-Key") String idempotencyKey  // ← Header injection
    ) {
        // ...
    }
}
```

**Framework evidence:**

| Annotation | Spring Feature | Implication |
|------------|----------------|-------------|
| `@RestController` | Spring REST routing | REST API framework |
| `@PreAuthorize` | Spring Security | Role-based authorization |
| `@Transactional` | Spring ORM | ACID transaction support |
| `@Valid` | Bean Validation JSR-380 | Input validation framework |
| `@RequestHeader` | Spring parameter injection | HTTP header binding |

**Confidence:** VERY HIGH (framework annotations are unambiguous)

---

## Section 4: Comment Classification (Credibility: 0.5)

**Critical principle:** Not all comments are equal. Comments reveal intent, but can become stale. Classify before trusting.

### Subsection 4.1: Intent Comments (HIGH credibility within comments)

**What they explain:** WHY the code does something, not WHAT it does.

**Example 1: Business logic justification**
```python
def calculate_tax(amount, state, item_type):
    # Tax rates vary by state and item type. California uses 7.25% for most items
    # but some categories (groceries, medicine) are tax-exempt.
    # We use a lookup table from CA Department of Tax and Fee Administration
    # (last updated 2023-04-15). Exempt items return 0.0.
    # See: https://www.cdtfa.ca.gov/taxes-and-fees/taxes/sales-tax-rate

    if item_type == 'grocery':
        return 0.0
    elif item_type == 'medicine':
        return 0.0
    elif state == 'CA':
        return amount * 0.0725
    else:
        return amount * 0.0600  # Default fallback for other states
```

**Evidence:** HIGH
- Explains why tax rates exist (regulatory requirement)
- Documents data source (CA DTFA)
- Notes item exemptions with business logic
- Links to authoritative source
- Confidence: HIGH (combines comment + code)

**Example 2: Performance trade-off**
```python
def process_batch_payment(payments):
    # We use sequential processing (not parallel) to respect Stripe's rate limits.
    # Stripe enforces 100 requests/second per API key.
    # A naive parallel implementation (concurrent.futures.ThreadPoolExecutor)
    # hit rate limits and caused failures. This sequential approach is 5x slower
    # (10 requests/sec vs 100) but 100% reliable.
    # Trade-off: Latency (batch takes 10s instead of 2s) vs Reliability (0 failures)
    # For payment operations, reliability > latency.

    for payment in payments:
        charge_result = stripe.Charge.create(
            amount=payment['amount'],
            customer=payment['customer_id']
        )
        payment['stripe_charge_id'] = charge_result.id
```

**Evidence:** VERY HIGH
- Explains design decision (rate limits)
- Documents failed approach (parallel → rate limit errors)
- Quantifies trade-off (10s vs 2s latency)
- Provides rationale (reliability priority)
- Confidence: HIGH (contains learning from past issue)

**Example 3: Security decision**
```python
# We hash passwords with bcrypt using 12 rounds (not SHA-256).
# bcrypt is slow-by-design, making rainbow table attacks expensive.
# 12 rounds ≈ 250ms per hash (acceptable for login, expensive for attackers).
# SHA-256 is fast (<1ms), making offline cracking trivial.
#
# See OWASP: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
```

**Evidence:** VERY HIGH
- Explains security rationale (defense against specific attack)
- Compares alternatives (bcrypt vs SHA-256)
- Quantifies cost (250ms)
- References security authority (OWASP)
- Confidence: HIGH (security decision documented)

---

### Subsection 4.2: Description Comments (LOW credibility; often redundant)

**What they do:** Repeat what the code already says.

**Bad example:**
```python
# Initialize the counter
counter = 0

# Loop through items
for item in items:
    # Increment counter
    counter += 1
```

**Why low credibility:** Code already shows initialization, loop, increment. Comment adds no new information. Risk: if code changes but comment isn't updated, they diverge.

**Better example (refactored code instead):**
```python
item_count = len(items)
```

**Why better:** Code is clearer (single expression, not loop). Comment not needed.

**Acceptable description comment:**
```python
# Expected format: {"user_id": 123, "action": "login", "timestamp": "2024-01-15T10:30Z"}
event = json.loads(raw_event)
```

**Why acceptable:** Clarifies data format (not obvious from code alone). Helps new developers understand expected structure.

---

### Subsection 4.3: TODO/FIXME/HACK/BUG Markers (HIGH credibility as technical debt)

**Systematic extraction:**
```bash
$ grep -r "TODO\|FIXME\|HACK\|BUG\|XXX" src/ --include="*.py" | sort
```

**Marker semantics and evidence weight:**

| Marker | Meaning | Evidence of | Confidence | Action |
|--------|---------|------------|-----------|--------|
| **TODO** | Planned but incomplete | Feature backlog | MEDIUM | Schedule for next sprint |
| **FIXME** | Broken, needs repair | Bug waiting for fix | MEDIUM-HIGH | Prioritize for bug fix |
| **HACK** | Workaround, temporary | Acknowledged tech debt | HIGH | Plan refactoring |
| **BUG** | Known defect | Acknowledged issue | VERY HIGH | Critical; document risk |
| **XXX** | Pay attention here | Author caution flag | MEDIUM | Code review required |

**Example 1: HACK marker**
```python
def get_user_email_domain():
    # HACK: Email domain is hardcoded until we implement multi-tenancy.
    # Currently all users are under @company.com, but this breaks in multi-tenant mode.
    # TODO: Make email domain configurable per tenant
    return "company.com"
```

**Evidence:**
- Acknowledges temporary workaround (reliability is uncertain)
- Documents future migration path (multi-tenancy)
- Includes TODO for next phase
- Confidence: HIGH (hack is intentional, not invisible)

**Document as:** "Email domain is currently hardcoded. Will break in multi-tenant deployment. Plan refactoring when multi-tenancy is implemented."

**Example 2: BUG marker**
```python
def calculate_discount(amount, percentage):
    # BUG: Percentage calculation is incorrect. Should be amount * (percentage / 100),
    # but currently does amount * percentage (off by factor of 100).
    # Example: $100 with 10% should be $10, but this returns $1000.
    # This was never fixed because it affects all discounts equally (consistent bug).
    # Fixing it requires database migration to correct past orders.
    # See issue #4521 for tracking.
    return amount * percentage
```

**Evidence:**
- Acknowledges bug with reproducible example ($100, 10% → wrong result)
- Explains why not fixed (data migration complexity)
- References tracking issue (not floating in code alone)
- Confidence: VERY HIGH (bug impact is documented)

**Document as:** "CRITICAL: Discount calculation is off by factor of 100. Known issue #4521. Affects all orders. Pending data migration for fix."

**Example 3: XXX marker**
```python
def validate_user_input(user_data):
    # XXX: User can submit HTML in bio field. Currently not sanitized.
    # This could allow XSS attacks if bio is rendered without escaping.
    # Sanitization library added but not integrated yet.

    return {
        'name': user_data.get('name'),
        'bio': user_data.get('bio'),  # ← Not sanitized
        'email': user_data.get('email')
    }
```

**Evidence:**
- Flags security risk (XSS vulnerability)
- Explains exposure (HTML rendering without escaping)
- Notes partial solution (library added but not used)
- Confidence: HIGH (security issue documented)

**Document as:** "SECURITY WARNING: User bio input is not sanitized. XSS vulnerability if bio is rendered. Pending: integrate HTML sanitization library."

---

### Subsection 4.4: Architecture Comments (Highest credibility of all comments)

**What they explain:** System-level design rationale, not just function behavior.

**Example 1: Multi-layer architecture**
```python
"""
Payment Processing Architecture:

Layer 1 - API Handler (routes.py)
├─ Accepts HTTP request, validates JSON schema
├─ Calls PaymentService (business logic)
└─ Returns HTTP response

Layer 2 - PaymentService (payment_service.py)
├─ Orchestrates payment flow (validation → gateway → webhook)
├─ Handles retries and error recovery
├─ Logs all payment events to audit trail
└─ Calls PaymentGateway (Stripe/Razorpay)

Layer 3 - PaymentGateway (stripe_adapter.py)
├─ Wraps Stripe SDK, returns typed responses
├─ Handles Stripe-specific error codes
├─ Caches API responses where safe
└─ Circuit breaker for outages

Webhook Handler (webhooks.py)
└─ Receives async Stripe events (charge.succeeded, charge.failed)
└─ Updates payment status in database
└─ Idempotency check (process webhook only once)

This separation ensures:
✓ Dependency injection (easy to test, swap gateways)
✓ Error handling at right level (API errors vs gateway errors)
✓ Audit trail (all payments logged)
✓ Resilience (circuit breaker, retries)
✓ Extensibility (add new gateways without rewriting PaymentService)
"""
```

**Evidence:** VERY HIGH
- Explains system structure clearly
- Documents dependencies and flow
- Lists benefits of architecture
- Confidence: VERY HIGH (architectural insight preserved for next developer)

**Example 2: Why a pattern was chosen**
```python
"""
Authentication Strategy:

We use JWT (JSON Web Tokens), not session cookies, because:

1. Stateless: Tokens are self-contained (user ID, roles, expiry in token).
   No server-side session database needed.
   Enables horizontal scaling (any server can validate token).

2. Mobile-friendly: Native apps can't use HTTP cookies reliably.
   APIs receive token in Authorization header.

3. Multi-domain: Single token works across api.example.com and app.example.com
   (Cookies are domain-bound; JWTs are portable).

Trade-off: Token revocation is harder (can't invalidate instantly).
Mitigation: Short expiry (15 min) + refresh tokens for revocation.

Alternative we rejected: Session cookies
- Would require shared session store (Redis) across servers
- Adding Redis dependency for auth
- Not mobile-friendly without custom handling
- Decided: JWT complexity < session infrastructure complexity
"""
```

**Evidence:** VERY HIGH
- Explains choice rationale (statelessness, scalability, mobile support)
- Documents trade-offs (revocation difficulty)
- Shows mitigation (short expiry)
- Compares rejected alternative (session cookies)
- Confidence: VERY HIGH (decision recorded for future reference)

---

### Subsection 4.5: Comment Age Detection (Staleness Risk)

**Red flag patterns:**

```python
# Written in 2020 but code changed in 2023
def legacy_feature():
    # This uses jQuery because we didn't have React back then
    # TODO: Convert to React component
    jquery_call()
```

**Stale comment detection strategy:**
1. Check git blame for comment line
2. If comment is > 2 years old AND code around it has changed → suspect stale
3. Cross-reference comment against actual code behavior
4. Test claim (does it match reality?)

**Example: Comment vs code mismatch**
```python
def calculate_commission(sales_amount):
    # Commission is 5% for all sales

    if sales_amount > 10000:
        return sales_amount * 0.08  # Actually 8% for large sales
    else:
        return sales_amount * 0.05
```

**Evidence:** Comment claims 5% flat, but code has 8% for > $10k. Document as: "Commission calculation: comment states 5% flat, but code shows tiered (5% standard, 8% for >$10k). Code is authoritative; comment is stale."

**Mitigation:** Trust code over stale comments. Use comment as hypothesis, verify against code.

---

### Subsection 4.6: Non-Evidence Comments (Do NOT count as documentation)

**License headers (not evidence):**
```python
# Copyright (c) 2023 Example Corp. All rights reserved.
# Licensed under the MIT License. See LICENSE file.
```

**Auto-generated documentation (not evidence):**
```python
def get_user(user_id):
    """
    Gets a user.

    Args:
        user_id: The user ID.

    Returns:
        A user object.
    """
```

**Reason:** These are metadata, not explanations of design or intent.

**Commented-out code (TREAT AS ARTIFACT, not documentation):**
```python
# Old implementation (no longer used):
# payment_result = stripe.Charge.create(amount=amount)
# payment_gateway.log(payment_result)

# New implementation:
payment_result = stripe.Charge.create(amount=amount)
asyncio.create_task(log_payment_async(payment_result))
```

**Evidence:** Commented-out code shows evolution (sync → async). But it's evidence of code change, not documentation. Document as: "Payment logging migrated from sync to async (see commit xyz)."

---

## Section 5: Inference Rules (Credibility: 0.3)

**Critical principle:** Inference alone is NEVER sufficient for HIGH confidence. Always pair with code, tests, or git evidence.

### Subsection 5.1: Pattern Matching Inference

**Pattern:** "I've seen this architecture before → likely same intent"

**Example: Repository pattern detection**
```python
# Code structure:
class UserRepository:
    def find_by_id(self, id):
        return db.query(User).filter(User.id == id).first()

    def find_all(self):
        return db.query(User).all()

    def save(self, user):
        db.session.add(user)
        db.session.commit()

    def delete(self, user_id):
        db.session.query(User).filter(User.id == user_id).delete()
```

**Inference:** Class is named `*Repository` with CRUD methods → implements Repository pattern.

**Confidence:** MEDIUM (pattern visible, but needs corroboration)
- Hypothesis A: Repository pattern is intentional (separation of data access)
- Hypothesis B: Just happened to have these methods (coincidence)
- Verification: Check if Repository is injected into services (Hypothesis A) or instantiated directly (Hypothesis B)

**Confidence upgrade to HIGH if:**
- Tests show Repository injected via dependency injection (Code + Test evidence)
- Git commit mentions "extract repository pattern" (Git evidence)
- Comments explain separation of concerns (Comment evidence)

---

### Subsection 5.2: Naming Convention Inference

**Pattern:** Function name reveals likely behavior

| Naming Pattern | Inferred Behavior | Confidence | Verification |
|---|---|---|---|
| `cache_*` | Caching logic | MEDIUM | Look for TTL, eviction policy |
| `validate_*` | Input validation | MEDIUM-HIGH | Look for exception raising |
| `serialize_*` | Convert object to string/JSON | MEDIUM | Look for JSON.dumps, .to_dict() |
| `parse_*` | Convert string to object | MEDIUM | Look for JSON.loads, string parsing |
| `is_*`, `has_*`, `can_*` | Returns boolean | HIGH | Return type visible in code |
| `get_*` | Retrieve data (read-only) | MEDIUM | Check if method modifies state |
| `set_*`, `update_*` | Modify data (write) | MEDIUM-HIGH | Look for assignment, db.commit() |
| `init_*`, `setup_*` | Initialize/bootstrap | MEDIUM | Check if called at startup |

**Example: Cache inference**
```python
def cache_user_profile(user_id, profile_data, ttl=3600):
    """Cache user profile in Redis."""
    redis_key = f"user_profile:{user_id}"
    cache.set(redis_key, profile_data, ttl)
```

**Inference:** Name suggests caching (cache_*). Likely implements caching + TTL.

**Confidence:** HIGH (name + code both indicate caching)
- But still verify: What's the TTL default? (3600 seconds = 1 hour, reasonable)
- Is cache invalidated on user update? (Search for cache.delete or cache.expire calls)

---

### Subsection 5.3: Structural Inference (File location reveals purpose)

| File Path Pattern | Inferred Purpose | Confidence | Example |
|---|---|---|---|
| `/migrations/` | Database schema changes | HIGH | `001_create_users_table.sql` |
| `/models/` | Data models/schemas | HIGH | `user.py`, `order.py` |
| `/services/` | Business logic orchestration | MEDIUM | `payment_service.py` |
| `/handlers/`, `/routes/` | API endpoint handlers | HIGH | `users.py`, `orders.py` |
| `/utils/`, `/helpers/` | Utility functions (shared) | MEDIUM | `string_utils.py` |
| `/tests/` | Test files | HIGH | `test_auth.py` |
| `/config/` | Configuration | HIGH | `database_config.py` |
| `/adapters/`, `/integrations/` | External integrations | MEDIUM | `stripe_adapter.py` |

**Example: Migration file inference**
```
src/
  database/
    migrations/
      001_create_users_table.py
      002_add_email_column.py
      003_create_orders_table.py
```

**Inference:** Files in migrations/ are database schema changes. Sequential numbering (001, 002, 003) suggests ordered execution.

**Confidence:** HIGH (file location is unambiguous)
- Verify: Run `ls -la` to confirm files exist
- Check actual content: Do they contain SQL/ORM schema changes?

---

### Subsection 5.4: Dependency Graph Inference

**Pattern:** Import chains reveal module relationships

```python
# routes.py imports:
from services.payment_service import PaymentService
from models.order import Order
from adapters.stripe_adapter import StripeAdapter

# Inferred dependency direction:
# routes (API) → services (business logic) → adapters (external integrations) → models (data)
```

**Inference:** Layered architecture (API layer → Service layer → Adapter layer → Data models)

**Confidence:** MEDIUM-HIGH (import structure visible)
- Verify: Check if reverse imports exist (circular dependency detection)
- Check if all imports follow layering (no shortcuts like routes → models directly)

---

### Subsection 5.5: DANGER ZONE — Insufficient Inference (NEVER USE ALONE)

**These inferences are NOT sufficient without corroboration:**

```python
# ❌ WRONG: Single inference only
Claim: "This codebase uses caching"
Evidence: "There's a cache_users() function"
Problem: Function exists, but is it called? Is it actually used? Is it tested?

# ✓ CORRECT: Inference + Code
Claim: "This codebase uses caching"
Evidence:
  1. Function cache_users() exists in cache_layer.py (Inference)
  2. Tests verify cache hit rate (Code + Test)
  3. Git history shows caching performance optimization commit (Git)
Confidence: HIGH
```

---

### Subsection 5.6: Competing Hypotheses in Inference

**When inferring architecture, always state alternatives:**

```
Code shows: Function named validate_email() exists

Hypothesis A (likely): Function validates email format
Hypothesis B (less likely): Function is named misleadingly; actually sends email

Test to disambiguate:
- Look at return type: boolean → Hypothesis A (return True/False for valid/invalid)
- Look at side effects: any email sending? → Hypothesis B
- Check tests: validate_email("invalid@") raises ValidationError? → Hypothesis A
```

**If you can't disambiguate:** Tag as MEDIUM confidence, state both hypotheses in documentation.

---

## Cross-Validation Protocol (Multi-Source Requirements)

**Cardinal rule:** Every major claim requires **combined credibility weight ≥ 1.5** from independent sources.

### Evidence Combination Examples

**Claim: "API is paginated with 50 items per page"**

```
Evidence sources:
  1. Code (1.0): src/api/routes.py:45 → PageSize = 50 constant
  2. Tests (0.9): tests/test_api.py:102 → assert len(response['items']) == 50
  3. API docs: "Returns up to 50 items" (not code, ignore)

Combined weight: 1.0 + 0.9 = 1.9 → Confidence: VERIFIED

Why this is strong:
- Code defines the constant (1.0 weight)
- Test verifies the behavior (0.9 weight)
- Two independent sources confirm same claim
```

**Claim: "Users authenticate via OAuth 2.0"**

```
Evidence sources:
  1. Code (1.0): src/auth/oauth.py:12 → oauth2.Provider() initialization
  2. Dependencies (code, 1.0): requirements.txt → oauth2-python==3.0.0
  3. Git (0.7): Commit abc123 (2023-05-10) → "feat: add OAuth 2.0 integration"
  4. Tests (0.9): tests/test_oauth_flow.py → test_oauth_login_succeeds()

Combined weight: 1.0 + 1.0 + 0.7 = 2.7 → Confidence: VERIFIED
(Using highest 3 sources to avoid overcounting)

Alternative combination: 1.0 (code) + 0.9 (test) = 1.9 → Still VERIFIED
```

**Claim: "Passwords are hashed with bcrypt using 12 rounds"**

```
Evidence sources:
  1. Code (1.0): src/auth/password.py:45 → bcrypt.hashpw(pwd, bcrypt.gensalt(12))
  2. Tests (0.9): tests/test_password.py:23 → assert bcrypt.checkpw(password, hash)
  3. Dependencies (1.0): requirements.txt → bcrypt==4.1.0
  4. Comments (0.5): "bcrypt with 12 rounds for security"

Combined weight: 1.0 + 0.9 = 1.9 → Confidence: VERIFIED
(Code + Test is sufficient; comment is bonus)

Why 12 rounds:
  - Code shows gensalt(12) explicitly (1.0)
  - Git comment "12 rounds ≈ 250ms" (0.5) explains tradeoff
  - Combined: 1.0 + 0.5 = 1.5 → HIGH confidence on cost
```

---

### Conflicting Evidence Resolution

**Scenario 1: Code and comment disagree**

```python
def calculate_discount(amount):
    # Discount is 20% for all orders
    return amount * 0.15  # Actually 15%
```

**Resolution (MANDATORY):**
1. Note the contradiction in documentation
2. Trust code (actual runtime behavior) over comment
3. Confidence: Code is VERIFIED (1.0), comment is misleading
4. Flag for bug: Either comment is wrong OR code is wrong
5. Include in handoff: "Discount calculation needs verification. Code shows 15%, comment claims 20%. Need to resolve which is correct before next release."

**Example documented conflict:**
```markdown
**DISCREPANCY FOUND:**
- Code claim: 15% discount (return amount * 0.15)
- Comment claim: 20% discount
- Confidence: Code is authoritative (actual behavior)
- Recommendation: Verify business requirement. If 20% is correct, code has bug.
```

**Scenario 2: Code and tests disagree**

```python
# Implementation
def is_valid_email(email):
    return "@" in email

# Test
def test_invalid_email_with_multiple_ats():
    assert not is_valid_email("user@@example.com")
    # Test expects double @@ to be invalid
```

**Resolution:**
- Run the test: Does it pass or fail?
- If test FAILS: Code has bug (doesn't reject double @@), needs fix
- If test PASSES: Test is wrong (but this is unlikely if test is well-named)
- Always trust running test results over inspection

**Document as:**
```markdown
**Test-Code Mismatch:**
- Code: return "@" in email (checks for single @, accepts double @@)
- Test: test_invalid_email_with_multiple_ats asserts double @@ is invalid
- Test status: FAILING
- Implication: Email validation is incomplete (security issue)
- Recommendation: Fix code to properly reject malformed emails
```

**Scenario 3: Git history vs current code**

```
Commit (2023-01-15): "refactor: migrate from synchronous to async email"
Current code (2024-01-10): email_service.send_email(to, subject)  # Looks synchronous
```

**Resolution:**
1. Check git blame: When was this line last modified?
2. If commit message disagrees with current code: One is stale
3. Document: "Git history claims async email, but code appears synchronous. Verify which is correct."
4. Confidence: MEDIUM (contradiction needs clarification)

**Example documented conflict:**
```markdown
**Git-Code Mismatch:**
- Git (Jan 2023): "async email migration complete"
- Code (Jan 2024): send_email() appears synchronous (no await keyword)
- Git blame: This line modified July 2023 (after async migration claim)
- Hypothesis 1: Async was implemented then reverted (find revert commit)
- Hypothesis 2: Code is still sync despite migration claim
- Next step: Review commit history for reversions or rollbacks
```

---

### Multi-Source Evidence Matrix (Quick Reference)

| Sources | Combined Weight | Confidence | Acceptable? |
|---------|-----------------|-----------|-------------|
| Code (1.0) | 1.0 | MEDIUM | ✓ (for implementation facts) |
| Code (1.0) + Test (0.9) | 1.9 | VERIFIED | ✓ |
| Code (1.0) + Git (0.7) | 1.7 | HIGH | ✓ |
| Code (1.0) + Comment (0.5) | 1.5 | HIGH | ✓ (barely) |
| Test (0.9) + Git (0.7) | 1.6 | HIGH | ✓ (without code!) |
| Test (0.9) + Comment (0.5) | 1.4 | MEDIUM | ✗ (below threshold) |
| Code (1.0) + Inference (0.3) | 1.3 | MEDIUM | ✗ (needs more) |
| Git (0.7) + Comment (0.5) | 1.2 | LOW | ✗ |
| Comment (0.5) + Inference (0.3) | 0.8 | LOW | ✗ |
| Inference (0.3) alone | 0.3 | UNKNOWN | ✗ (forbidden) |

---

## Evidence Quality Checklist (Every Major Claim)

For each claim in your documentation, verify:

```
Claim: "[state your claim clearly]"

Source 1 [Type]: [file:line or test:name] → [what it shows]
Source 2 [Type]: [file:line or test:name] → [what it shows]

Combined weight: X.X
Confidence level: [VERIFIED/HIGH/MEDIUM/LOW/UNKNOWN]

Competing hypothesis: [what if this pattern means something else?]
  → Evidence supporting primary hypothesis: [list]
  → Evidence supporting alternative: [none found, or brief note]
```

**Example completion:**

```
Claim: "Payment service uses circuit breaker pattern"

Source 1 [Code, 1.0]: src/payment/service.py:67 → @circuit(failure_threshold=5) decorator
Source 2 [Test, 0.9]: tests/test_payment.py:134 → test_circuit_opens_after_5_failures verifies behavior

Combined weight: 1.9
Confidence: VERIFIED

Competing hypothesis: "Decorator is there but not actually protecting calls"
  → Evidence for primary: Test explicitly verifies circuit breaker trips
  → Evidence for alternative: None found (code is straightforward)
  → Conclusion: Circuit breaker is definitely active
```

---

## Circular Evidence Detection (AVOID THIS)

**What it is:** Using evidence to justify a claim that was derived from that same evidence. The evidence and claim are circular — they prove each other, not the underlying fact.

**Example of circular evidence (WRONG):**

```
Claim: "This codebase uses dependency injection"
Evidence: "There's a DI framework in imports (from fastapi import Depends)"

Problem: We've proven FastAPI is imported, NOT that DI pattern is used.
Import ≠ Usage.

Correct evidence (requires USAGE proof):
1. Code (1.0): @app.get("/users") def get_user(repo: UserRepo = Depends(get_repo))
   → Function parameter has Depends() → DI is USED
2. Tests (0.9): test_get_user(mock_repo) shows repo is injected
3. No evidence: endpoints instantiate UserRepo directly (would contradict DI claim)

Combined: 1.0 + 0.9 = 1.9 → VERIFIED
```

**Why the original was circular:**
- Claim: "Uses DI" (design pattern)
- Evidence: "Imports DI framework" (library presence)
- Fallacy: Importing library ≠ using pattern (could import and never use)

**Example of circular evidence (WRONG):**

```
Claim: "The system supports distributed transactions"
Evidence: "There's a database.transaction() call in the code"

Problem: Single-database transactions() are NOT distributed.
We proved code has transactions, not distributed transactions.

Correct evidence:
1. Code (1.0): src/transactions.py:45 → coordinator.enroll(db1, db2)
   → Enrolling TWO databases in transaction (distributed pattern)
2. Tests (0.9): test_two_phase_commit verifies vote + commit across DB1 and DB2
3. Config (0.5): Multiple database connections configured

Combined: 1.0 + 0.9 = 1.9 → VERIFIED (distributed transactions)
```

**Why the original was circular:**
- Claim: "Supports distributed transactions"
- Evidence: "Has transaction() method"
- Fallacy: Most databases have transaction() method; that doesn't make them distributed

---

### Circular Evidence Detector Checklist

When reviewing your own documentation, ask:

- [ ] Is the evidence just restating the claim in different words?
- [ ] Does the evidence actually PROVE the claim, or just mention a related term?
- [ ] Example: Claim "Uses X pattern" → Evidence "Imports X library" (NOT SUFFICIENT)
- [ ] Example: Claim "Caches data" → Evidence "cache_users() function exists but never called" (WRONG)
- [ ] Is there independent confirmation from tests, git history, or comments?
- [ ] Could I explain this claim to someone who hasn't seen this code?
- [ ] If the evidence disappeared, would the claim still be true?

---

## Advanced Verification: SIFT Method (Research-Analyst)

Adapted from Stanford History Education Group fact-checking methodology:

### S: Stop and Investigate the Source

Before using evidence, ask:

1. **Author credibility:** Who wrote this code?
   - Original author (high credibility for intent)
   - Later maintainer (may not know original intent)
   - Unknown contributor (verify code independently)

2. **Evidence freshness:** When was this code written?
   - Created 2024 (current, likely accurate)
   - Created 2020 (5 years old, verify against current code)
   - Never modified (stale, needs checking)

3. **Source type:** Is this primary or secondary evidence?
   - Code itself = primary (executable truth)
   - Comment about code = secondary (interpretation)
   - Git history = primary + secondary (author documented intent)

### I: Investigate Independent Confirmation

Find corroborating evidence OUTSIDE the original claim:

```
Original claim: "User authentication uses bcrypt"
Independent checks:
  1. Is bcrypt in requirements? (yes)
  2. Do tests verify bcrypt? (yes)
  3. Does git history mention bcrypt choice? (yes, commit abc123)
  4. Are there other auth methods in code? (no)

Result: VERIFIED (multiple independent sources agree)
```

### F: Find Better Coverage (Multiple Perspectives)

Seek evidence from different angles:

```
Claim: "API rate limiting is per-user"

Angle 1 - Code: Where is rate limit key created?
  → src/ratelimit.py:23: redis_key = f"user_limits:{user_id}"
  → Evidence: Uses user_id as key (per-user)

Angle 2 - Tests: How are rate limits tested?
  → tests/test_ratelimit.py:45: test_user1_limited_separately_from_user2()
  → Evidence: Test verifies per-user isolation

Angle 3 - Config: Is per-user limit configurable?
  → config.yaml: RATE_LIMIT_STRATEGY: "per_user"
  → Evidence: Config confirms per-user strategy

Result: VERIFIED from 3 angles (code, tests, config)
```

### T: Trace Claims to Original Context

Follow claim back to its source:

```
Claim: "Payment service uses Stripe"

Trace 1 - Current code:
  → from stripe import Charge
  → Evidence: Direct import (recent)

Trace 2 - When was Stripe adopted?
  → git log --grep="stripe" --oneline
  → Commit 3a2b1c (2023-06-15): "integrate Stripe payment processor"
  → Evidence: Decision made June 2023

Trace 3 - Why was Stripe chosen?
  → git show 3a2b1c (read full commit message)
  → Message: "Migrate from Razorpay. Razorpay deprecated API, Stripe has better support"
  → Evidence: Upgrade from failing Razorpay

Result: VERIFIED with full decision context
```

---

## Minimum Required Evidence by Claim Type

| Claim Type | Minimum Sources | Example |
|-----------|-----------------|---------|
| **Implementation fact** | Code (1.0) | "Function returns int" |
| **Behavioral guarantee** | Code (1.0) + Test (0.9) | "Function throws TypeError for invalid input" |
| **Architectural decision** | Code (1.0) + Git (0.7) | "Uses repository pattern" |
| **Security control** | Code (1.0) + Test (0.9) + Comment (0.5) | "Passwords hashed with bcrypt" |
| **Performance characteristic** | Code (1.0) + Comment (0.5) | "O(n) algorithm, acceptable for <1M items" |
| **Compliance requirement** | Code (1.0) + Comment (0.5) + Git (0.7) | "PCI-DSS compliant card handling" |
| **Design pattern** | Code (1.0) + Test (0.9) | "Uses factory pattern for service creation" |

---

## Documentation Template: Evidence-Based Claim

Use this template for every significant claim in your handoff documentation:

```markdown
### [Component/Feature Name]

**What it does:**
[One sentence describing the component]

**Evidence:**
- Source 1 [Code, 1.0]: `file:line` → [what it shows]
- Source 2 [Test, 0.9]: `test_name()` → [what it verifies]
- Source 3 [Git, 0.7]: Commit `hash` → [decision context]

**Combined weight:** X.X → **Confidence: [VERIFIED/HIGH/MEDIUM/LOW]**

**Behavioral contract:**
[What the component guarantees; what it does NOT guarantee]

**Competing hypothesis:**
Alternative explanation: [what if it's actually doing something else?]
→ Evidence against alternative: [why we rejected it]

**Known limitations:**
[What this component does NOT do, or edge cases]

**Related components:**
[What depends on this, what it depends on]
```

---



---

## Behavioral Contract Extraction

### Test-Driven Contract Reading

**Given this test:**

```python
def test_create_order_with_items():
    order = create_order(customer_id=1, items=[
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 1}
    ])

    assert order.status == "pending"
    assert order.total == 45.00
    assert len(order.line_items) == 2
    assert order.created_at is not None
```

**Behavioral contract extracted:**

```
create_order(customer_id, items) → Order

Preconditions:
  - customer_id must be valid (assumed, not tested here)
  - items is a list of {product_id, quantity}

Postconditions:
  - Returns Order object with status = "pending"
  - Order.total is calculated (45.00 for these items)
  - Line items are created (one per item in input)
  - created_at timestamp is set

Side effects: (not apparent from this test alone)
  - Database persistence? (maybe, depends on test isolation)
  - Inventory adjustment? (not tested, probably not here)
  - Invoice generation? (not tested, probably not here)
```

### Exception Contract Extraction

**Given this test:**

```python
def test_create_order_with_invalid_customer():
    with pytest.raises(CustomerNotFoundError):
        create_order(customer_id=999999, items=[...])

def test_create_order_with_empty_items():
    with pytest.raises(ValidationError):
        create_order(customer_id=1, items=[])
```

**Exception contract:**

```
create_order() may raise:
  - CustomerNotFoundError if customer doesn't exist
  - ValidationError if items list is empty

Not tested (may or may not be raised):
  - OutOfStockError if items unavailable
  - PaymentFailureError if payment fails
```

---

## Pre-mortem Methodology for Documentation

**Question: "If this documentation is wrong, how would we find out?"**

### Example: Documenting a Payment Flow

**Documented behavior:**
"Orders are charged immediately when created."

**Pre-mortem questions:**

1. **Test evidence:** Is there a test `test_order_creation_charges_immediately()`?
   - If no: Document as "assumed, not tested"

2. **Code evidence:** Can I trace the payment call in order creation code?
   - If calls `charge_card()`: Confident
   - If calls `queue_payment()`: Async, need to note

3. **Git evidence:** When was immediate charging decided?
   - Commit message "charge immediately on order creation"?
   - PR discussion about async vs sync?

4. **Could be wrong if:**
   - Async payment queue exists but isn't in happy path tests
   - Webhook updates order status after async charge
   - Payment attempt could be deferred (fraud check, etc.)

**Documentation with pre-mortem:**

```markdown
## Payment Flow

Orders are charged immediately upon creation using Stripe API.

**Evidence:**
- Code: order.create() calls stripe.Charge.create() synchronously
- Test: test_order_creation_charges_card verifies charge is created
- Git: Commit 3a2b1c "charge immediately on order creation"

**Assumptions we're making:**
- Stripe charge API returns synchronously (not queued)
- No fraud checks delay charging
- Network failures are rare enough not to retry

**Could be wrong if:**
- Async payment queue is being used (search for queue_payment)
- Fraud detection service is in the call chain
- Payment retry logic exists but isn't documented

**Verify by:**
1. grep for "queue_payment" or "async.*payment"
2. Check Stripe webhook handlers
3. Review error handling for payment failures
```

---

## Fact-Checking Methodology (IFCN-inspired)

**International Fact-Checking Network principles adapted for code:**

### Principle 1: Identify Author Responsibly
- Who wrote this code?
- Who reviewed it?
- What's their expertise level (commit history)?

### Principle 2: Distinguish News from Commentary
- **Fact claim:** "Passwords are hashed with bcrypt"
- **Commentary:** "This implementation is secure" (subjective)

### Principle 3: Identify Original Sources
- **Primary source:** Code itself
- **Secondary source:** Comments, git history
- **Tertiary source:** PR discussions, external docs

### Principle 4: Assess Source Credibility
- Code created by original architects: High
- Code from junior contributor: Lower (may need review)
- Code without tests: Lower credibility

### Principle 5: Check for Contradictions
- Does test pass for the claimed behavior?
- Does comment match code?
- Does implementation match its own error messages?

### Principle 6: Verify Independently
- Can you run the test yourself?
- Can you trace the code path?
- Can you find corroborating evidence?

### Principle 7: Disclose Sources
- Show evidence in documentation
- Link to specific code lines
- Reference test assertions

### Principle 8: Maintain Correction Log
- If documentation is wrong, note what was wrong
- Include corrected version
- Explain why error occurred

---

## Practical Validation Workflow

### Step 1: Extract Candidate Claim
```
"System uses event sourcing for audit trail"
```

### Step 2: Identify Required Evidence Sources
- [ ] Code evidence: Event storage mechanism
- [ ] Test evidence: Event persistence test
- [ ] Git evidence: Decision context
- [ ] Comment evidence: Architecture documentation

### Step 3: Search for Each Source
```bash
# Code search
grep -r "EventStore\|EventLog\|append_event" src/

# Test search
grep -r "test.*event.*stor\|test.*sourcing" tests/

# Git search
git log --grep="event sourc" --oneline

# Comment search
grep -r "event sourc\|audit trail" src/ --include="*.py" --include="*.md"
```

### Step 4: Cross-Reference Findings
- If all sources agree: Very high confidence (document as "confirmed")
- If 2+ sources agree: High confidence (document as "verified")
- If only code: Medium confidence (document as "code-based, untested")
- If only comments: Low confidence (document as "assumes, unverified")
- If sources conflict: Flag as ambiguous, include all perspectives

### Step 5: Include Evidence Trail in Documentation
```markdown
**Event Sourcing Implementation**

The system uses event sourcing to maintain an immutable audit trail.

Evidence:
- Code: EventStore class in src/persistence/event_store.py (line 34)
- Test: test_event_persistence_is_append_only (tests/persistence_test.py)
- Git: Commit 5a4b3c "implement event sourcing for audit" (2023-04-15)
- Comments: Architecture notes in src/persistence/README.md

Confidence: Very high
```

### Step 6: Note Assumptions and Gaps
```markdown
**Assumptions:**
- All events are genuinely appended (no delete capability)
- Event schema changes are backward compatible

**Not tested / not verified:**
- Performance at scale (>1M events)
- Snapshot mechanism for recovery
- Event ordering under concurrent writes

**Recommendation:**
Review concurrency handling in event store before handling high-throughput scenarios.
```

---

## Summary Checklist for Evidence-Based Documentation

- [ ] Every claim has 2+ evidence sources
- [ ] Sources are listed (code location, test name, commit hash)
- [ ] Confidence level is stated (very high/high/medium/low)
- [ ] Contradictions are noted, not hidden
- [ ] Circular evidence is eliminated
- [ ] Assumptions are explicit
- [ ] Pre-mortem considerations are documented
- [ ] Evidence hierarchy is followed (Code > Tests > Git > Comments > Inference)
- [ ] Reader can verify claims independently
- [ ] Gaps and uncertainties are acknowledged
