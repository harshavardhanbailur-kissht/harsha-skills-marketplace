# Cognitive Patterns for Code Documentation

## Mental Model Building: Scaffolding Understanding

Human understanding is constructed incrementally. This section explains how to build mental models that stick, for different audiences.

### The Five-Layer Mental Model Framework

**Layer 1: What does it do? (Function)**
- "This service accepts orders and calculates total price"
- Single sentence, observable behavior
- No implementation details

**Layer 2: Why does it exist? (Purpose)**
- "Separates pricing logic from order management to allow independent changes to tax rules"
- Connect to business need or architectural constraint

**Layer 3: How does it work? (Mechanism)**
- "Queries tax rates from TaxService, applies discounts, calculates final price"
- Black-box flow, not code details

**Layer 4: What are the edge cases? (Boundaries)**
- "Assumes tax rates are never negative; doesn't handle split orders"
- Constraints and assumptions

**Layer 5: Implementation details (Code)**
- Specific classes, methods, algorithms
- Only for deep technical audience

**Progressive disclosure pattern:** Start at Layer 1 for all audiences. Expand to Layer 2+ based on audience needs.

```
For product manager:  Layers 1-2
For new engineer:     Layers 1-3
For feature owner:    Layers 1-4
For maintenance dev:  Layers 1-5
```

### The Chunking Principle

Human working memory holds ~7 chunks of information. Exceed this and comprehension fails.

**Too many chunks (WRONG):**
```
Order creation involves:
1. Customer validation
2. Address normalization
3. Inventory checking
4. Tax calculation
5. Discount application
6. Payment authorization
7. Order persistence
8. Invoice generation
9. Customer notification
10. Analytics tracking
```

**Chunked properly (RIGHT):**
```
Order creation has three phases:
1. Preparation: Validate customer and inventory, normalize address
2. Pricing: Calculate tax and discounts
3. Completion: Process payment, persist order, notify customer
```

**Chunking strategy:** Group related steps under meaningful phase names. Reduces cognitive load from 10 items to 3.

### Conceptual Integrity vs. Completeness

**Conceptual integrity:** System feels coherent, follows consistent patterns

**Completeness:** All details are documented

**The tradeoff:** Perfect completeness breaks conceptual integrity.

**Example documentation breakdown:**

```markdown
# Order Service Architecture

The Order Service manages the complete order lifecycle:

1. **Order Processing Pipeline** (coherent, ~50 lines)
   - Create: Validate input, reserve inventory
   - Fulfill: Charge payment, ship items
   - Complete: Archive order, update analytics

2. **Error Handling** (coherent, ~30 lines)
   - Inventory errors: Return to customer
   - Payment errors: Retry 3x with exponential backoff
   - Other errors: Alert operations team

3. **Configuration** (reference)
   - See CONFIG.md for all 47 settings

4. **Edge Cases** (reference)
   - See EDGE_CASES.md for 23 documented scenarios
```

**Structure principle:** Core narrative stays conceptually integral. Details move to separate reference documents.

---

## Narrative Structure for Architecture Docs

### The Hero's Journey Template (for feature narratives)

**Act 1: Inciting Incident**
- What problem triggered this feature?
- Why does it matter?

**Example:**
"Users couldn't export reports. Customers demanded this for accounting systems."

**Act 2: Quest**
- What approach was chosen?
- Why that one vs. alternatives?

**Example:**
"We added an export API (not UI) because it's more flexible. Users can build custom integrations."

**Act 3: Resolution**
- How is the problem solved?
- What new constraints does it introduce?

**Example:**
"Exports run asynchronously via Celery, returning a download URL. But exports expire in 24 hours (S3 cost constraint)."

**Epilogue: New Challenges**
- What new problems emerge?
- What's the next chapter?

**Example:**
"Users complain about expiration. We're considering persistent storage (scheduled epic)."

### The Explanation Gradient

**Density increases as you move down:**

```
CONCEPTUAL (1-2 sentences)
"Orders flow through three states: pending, paid, shipped."

SIMPLIFIED (1 paragraph)
"When customers create orders, they're held in pending state.
Payment triggers transition to paid, which notifies fulfillment.
Fulfillment marks the order shipped, which generates invoice."

DETAILED (5 paragraphs with pseudocode)
"Order state machine enforces valid transitions. Pending orders
can be cancelled or paid. Payment attempt triggers... [detailed flow]"

COMPREHENSIVE (specs, error cases, performance notes)
"See design document 7-states.md for complete state table.
Error handling covered in error-recovery.md.
Performance: handles 10K orders/sec; see benchmarks/..."
```

**Structure documentation at multiple densities.** Reader chooses their level.

### The Three-Act Diagram Method

**Act 1: Simplest possible diagram**
```
[Customer] → [Order Service] → [Database]
```

**Act 2: Add key steps**
```
[Customer]
   → [Validate Input]
   → [Check Inventory]
   → [Calculate Price]
   → [Process Payment]
   → [Persist Order]
   → [Database]
```

**Act 3: Add failure paths**
```
[Customer]
   → [Validate] ⚠️ (invalid → error response)
   → [Inventory] ⚠️ (out of stock → error)
   → [Price]
   → [Payment] ⚠️ (failed → retry loop)
   → [Persist]
   → [Database]
```

**Rule:** Never exceed two diagrams per section. Use references for full detail.

---

## Explaining Complex Systems to Different Audiences

### The Product Manager Lens

**What they care about:**
- How does this affect customers?
- What's the timeline to ship?
- What are the risks?
- How much effort?

**Communication pattern:**
```
"This feature reduces checkout time from 45s to 12s by removing
address validation step. Customers in Australia complained loudest.
Implementation is 3 sprints; risk is low (feature flagged for rollback).
Effort: 8 person-weeks."
```

**Avoid:** Implementation details, architecture diagrams, technical tradeoffs.

**Include:** Business metrics, rollout plan, risk assessment.

### The New Engineer Lens

**What they care about:**
- How do I understand this system?
- Where are the entry points?
- What are common patterns?
- What tests should I read?

**Communication pattern:**
```
"Start by reading OrderService class (src/orders/service.py).
It has three main methods: create, fulfill, complete.
Tests in tests/orders/test_service.py show the happy path.
Common pattern: validate input, then call repository layer (src/persistence/).
Async jobs queued via Celery (see tasks.py)."
```

**Avoid:** Historical decisions, deprecated approaches, "technical debt we'll fix someday."

**Include:** Reading order, concrete file paths, test references, common patterns.

### The Maintenance Developer Lens

**What they care about:**
- Why is this code here?
- What breaks if I change this?
- How do I test it?
- What's the history?

**Communication pattern:**
```
"Cache invalidation on user profile change (see cache_keys.py).
This was added in 2023 (commit 3a2b1c) because profile updates
were stale. DO NOT remove unless you verify analytics exports
still work (see integration test 'test_analytics_export_staleness').
Change cache_keys.USER_PROFILE and you MUST update test_cache_keys.
Recent PR #1249 changed TTL from 1h to 30m due to PII concerns."
```

**Avoid:** "This is obviously necessary" — justify.

**Include:** Commit history, cross-system impacts, test names, recent changes.

### The Security Auditor Lens

**What they care about:**
- Where are secrets handled?
- Are inputs validated?
- Is data encrypted?
- Are there privilege escalations?

**Communication pattern:**
```
"Secrets: API keys stored in AWS Secrets Manager, rotated every 90 days.
Input validation: All order fields validated by Pydantic schemas (src/schema/).
Encryption: In-transit via HTTPS; at-rest via KMS encryption for PII fields.
Authorization: Only payment service can create charges (see rbac.py);
enforced by service principal checks, not role-based."
```

**Avoid:** Implementation details that don't affect security.

**Include:** Secret management, validation strategy, encryption, authorization mechanism.

---

## Progressive Disclosure Patterns

### The Onion Approach

**Layer 1 (Public): The Interface**
```markdown
## API Overview
POST /orders - Create order
GET /orders/{id} - Fetch order
```

**Layer 2: Intent**
```markdown
## Order Creation Flow
1. Validate customer and items
2. Calculate price
3. Process payment
4. Persist order
```

**Layer 3: Implementation**
```markdown
## Order Service Implementation
```
(Link to source code)
```
```

**Layer 4: Edge Cases**
```markdown
## Known Issues and Limitations
```
(Separate document)
```
```

**Structure principle:** Reader can stop at any layer. Each layer is self-contained and complete at its density.

### The Breadcrumb Navigation

```
Getting Started
  └─ Quick Start: Run local server in 5 minutes
  └─ Core Concepts: 3 main entities
      └─ Entity 1: Orders (2 paragraphs)
          └─ Order States (state diagram)
          └─ Order Properties (table)
      └─ Entity 2: Customers (2 paragraphs)
      └─ Entity 3: Payments (2 paragraphs)

Deep Dives
  └─ Order Processing Pipeline (full design doc)
  └─ Payment Gateway Integration (architecture)
  └─ Error Recovery (comprehensive guide)

Reference
  └─ API Spec (Swagger/OpenAPI)
  └─ Database Schema (ERD)
  └─ Configuration (env vars, settings)
```

**Structure principle:** Readers can follow breadcrumbs to deepen understanding without getting lost.

---

## Explanation Techniques That Work

### The Analogy Method

**Bad analogy (WRONG):**
"A cache is like a short-term memory."
(Vague, doesn't clarify mechanism)

**Good analogy (RIGHT):**
"A cache is like a convenience store. Customers want milk.
The store keeps milk in stock (cache). If a customer wants
a rare item, they special order from the distributor (fetch from DB).
Items expire and are restocked (TTL invalidation)."

**Analogy quality metrics:**
- Maps to mechanism, not just metaphor
- Has edge cases analogous to real system
- Helps predict behavior
- Fails gracefully (when limits of analogy are clear)

### The Worked Example Method

**Theory without example (WEAK):**
"Eventual consistency means replicas converge over time."

**With worked example (STRONG):**
```
User1 @ Datacenter A writes order #123
  T=0ms: A's database has order
  T=50ms: B's replica gets order (replication lag)
  T=100ms: C's replica gets order

If User2 @ Datacenter B reads at T=75ms: Doesn't see order yet.
If User2 @ Datacenter B reads at T=150ms: Sees order (converged).

The "eventual" part: there's a window where different datacenters
disagree about whether the order exists.
```

**Use worked examples for:**
- Asynchronous behavior
- State transitions
- Error conditions
- Edge cases

### The Negative Example Method

**What it does:**
"This shows what NOT to do and why it breaks."

**When to use:**
- Anti-patterns
- Common mistakes
- Performance traps
- Security vulnerabilities

**Example:**
```
# WRONG: Directly modifying user list during iteration
users = [...]
for user in users:
    if user.is_inactive:
        users.remove(user)  # BREAKS: Skips elements

# RIGHT: Filter into new list
active_users = [u for u in users if u.is_active]
```

**Effectiveness:** Readers remember what NOT to do, which prevents bugs.

### The Runnable Example Method

**For complex setup:** Include a script readers can run.

```python
# examples/order_creation.py
from orders import OrderService
from persistence import InMemoryOrderRepository

# Setup
repo = InMemoryOrderRepository()
service = OrderService(repo)

# Create order
order = service.create(
    customer_id=1,
    items=[{"product_id": 1, "quantity": 2}]
)

# Verify
assert order.status == "pending"
assert order.total == 50.00
print(f"Order {order.id} created successfully")
```

**Structure:** Readers can copy, run, modify, experiment.

---

## Epistemic Humility in Documentation

Expressing uncertainty without losing reader confidence.

### The Confidence Ladder

**Level 1: Definitive**
"Passwords are hashed with bcrypt."
(Code confirms this: bcrypt.hashpw() call)

**Level 2: High confidence**
"Passwords are hashed before storage."
(Tests confirm hashing; specific algorithm inferred from dependencies)

**Level 3: Moderate confidence**
"Passwords are likely hashed, using bcrypt or similar."
(No tests verify hashing; inferred from code structure)

**Level 4: Speculation**
"Passwords are probably hashed, though current hashing implementation isn't obvious."
(Couldn't find evidence; avoid this level)

**Level 5: Admission of ignorance**
"Password storage mechanism isn't documented; requires code review."
(Honest but unhelpful)

### Calibrated Confidence Language

```markdown
## Order Pricing

**Very High Confidence (verified by code + tests):**
Orders include tax calculated by the TaxService.

**High Confidence (confirmed by code, not explicitly tested):**
Tax is calculated for the delivery address, not customer home address.

**Moderate Confidence (inferred from code structure):**
Discounts are applied before tax (structure suggests this, test confirms result).

**Uncertain (found references but flow unclear):**
Whether sales tax or VAT is applied may depend on customer jurisdiction;
verify with TaxService documentation.

**Action item (unknown):**
Payment failure retry strategy is not documented; see PR #1249.
```

### Hedge Phrases That Work

**Avoid vague hedges:**
- "probably" (false precision)
- "maybe" (no useful info)
- "could be" (too speculative)

**Use specific hedges:**
- "Code suggests X; tests don't verify" (evidence-based)
- "Assumed to work this way; no test found" (honest)
- "X is documented as Y in [reference]; code may differ" (cites conflicts)
- "Behavior verified for scenarios A and B; edge case C untested" (specific boundaries)

### The Epistemic Honesty Checklist

- [ ] Do I have code evidence, or just inference?
- [ ] Are my assumptions explicit?
- [ ] Would a new engineer find this helpful or misleading?
- [ ] Have I marked edges of my knowledge?
- [ ] Could I be wrong? How would we know?

---

## Narrative Coherence Patterns

### The Three-Act Structure for System Explanations

**Act 1: The Setup (Why this system exists)**
```
When users export large datasets (10M+ rows), the request times out.
Database queries take 2+ minutes. Immediate response is impossible.
We built ExportQueue to solve this.
```

**Act 2: The Mechanism (How it works)**
```
Exports are queued asynchronously via Celery.
User gets a download URL immediately.
Celery workers process in background, uploading to S3.
User receives email when export is ready.
```

**Act 3: The Constraints (What it costs)**
```
Exports expire in 24 hours (S3 cost optimization).
Can't stream huge exports (UI timeout risk).
Users with 100K+ rows wait 5-10 minutes.
```

**Coherence check:** Does Act 3 explain why Act 2 was designed this way?

### The Cause-and-Effect Chain

Instead of listing features, show how they emerged:

**WRONG (list):**
```
System has:
- Caching
- Rate limiting
- Async jobs
- Database sharding
- Load balancing
```

**RIGHT (narrative):**
```
1. System served 100K req/s initially
2. Database became bottleneck (added caching to reduce load)
3. Users called API directly, causing cache thrashing (added rate limiting)
4. Long-running exports blocked API responses (moved to async jobs)
5. Single database couldn't handle volume (added sharding)
6. Requests unbalanced across shards (added load balancing)
```

**Effect:** Reader understands not just what, but why each piece exists.

---

## Summary: Cognitive Patterns Checklist

- [ ] Documentation is structured in layers (1-5)
- [ ] No section exceeds 7 chunks of information
- [ ] Narrative has coherent purpose, not just features
- [ ] Audience is identified (product manager vs. new engineer vs. auditor)
- [ ] Progressive disclosure present (can read at multiple depths)
- [ ] Analogies are mechanism-based, not metaphorical
- [ ] Worked examples show realistic scenarios
- [ ] Negative examples warn against anti-patterns
- [ ] Confidence levels are calibrated and honest
- [ ] Epistemic humility is explicit without being apologetic
- [ ] System evolution is explained (cause-and-effect)
- [ ] Edge cases are acknowledged, not hidden
- [ ] Reader can follow breadcrumbs deeper if desired
