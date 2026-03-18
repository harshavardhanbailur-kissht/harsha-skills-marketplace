# Decision Capture and Architecture Decision Records

## Architecture Decision Record (ADR) Format

### Standard ADR Template

```markdown
# ADR-001: Use PostgreSQL as Primary Database

## Status
Accepted (2023-03-15)

## Context
System needs persistent storage for orders. Evaluated options:
- PostgreSQL (relational, ACID, mature)
- MongoDB (document, flexible schema, eventual consistency)
- DynamoDB (serverless, pay-per-use, limited query flexibility)

## Decision
We will use PostgreSQL as the primary database.

## Rationale
1. **Data consistency:** Orders require strong consistency (ACID transactions)
2. **Query flexibility:** Reporting queries need complex joins
3. **Cost:** Self-hosted PostgreSQL cheaper than DynamoDB for our scale
4. **Maturity:** Proven track record, large community

## Consequences
### Positive
- Strong data consistency guarantees
- Complex queries supported
- Excellent tooling and monitoring
- Easy to hire engineers familiar with PostgreSQL

### Negative
- Operational responsibility (backups, maintenance, upgrades)
- Scaling requires careful planning (can't autoscale like DynamoDB)
- Requires database administration expertise

### Mitigations
- Scheduled backups (automated)
- Read replicas for scaling reads
- Managed PostgreSQL service considered if operational burden grows

## Alternatives Considered
### MongoDB
- Rejected because: Flexible schema not needed, eventual consistency unacceptable for orders

### DynamoDB
- Rejected because: Higher costs at our scale, limited query flexibility for reporting

## Related Decisions
- ADR-002: Use Redis for caching
- ADR-003: Implement write-ahead logging for audit trail

## Implementation
- First implementation: 2023-04-01 (PR #123)
- Current implementation: src/persistence/database.py
- Tests: tests/persistence/test_database.py

## Review
- Last reviewed: 2025-11-01
- Still valid: Yes
- Changes considered: None (decision holding up well)

## References
- PostgreSQL documentation: https://www.postgresql.org/docs/
- Comparison with alternatives: [internal wiki]
```

---

## Inferring Decisions from Code

### When ADR Doesn't Exist (Common Case)

**Question:** Why was this design chosen?

**Method 1: Read the Git History**
```bash
# Find when this pattern was introduced
git log -S "PostgreSQL\|database.py" --all --oneline | head -10

# Find the introducing commit
git show abc1234 --stat

# Read the commit message
git show abc1234
```

**Method 2: Search for Decision Comments**
```bash
grep -r "DECISION\|RATIONALE\|WHY\|because" src/ --include="*.py"

# Example finding:
# "Use pessimistic locking (FOR UPDATE) because concurrent
#  order modifications caused race conditions. See PR #456."
```

**Method 3: Trace from Code to Design**

```python
# Code shows: synchronous payment processing (no queuing)
def create_order(customer_id, items):
    try:
        charge = stripe.charge(amount=calculate_total(items))
        # Decision visible: Charge happens immediately, not queued
    except StripeError:
        # Decision visible: Failure propagates to client

# Implications of this decision:
# Pro: User gets immediate feedback
# Con: Slow payment processing blocks order creation
# Choice suggests: User experience prioritized over throughput
```

**Method 4: Read Test Intent**

```python
def test_order_creation_fails_if_payment_fails():
    # This test exists → decision: orders fail if payment fails
    # (not: create order, retry payment later)
    with pytest.raises(PaymentError):
        create_order(customer_id=1, items=[...])

# Implication: Orders are transactional with payments
```

### Decision Inference Template

```markdown
## Inferred Decision: Use Synchronous Payment Processing

**Evidence:**
1. Code pattern: Payment happens before order persistence
2. Test: test_order_creation_fails_if_payment_fails
3. Error handling: PaymentError propagates to client
4. No queue: No background payment processing code

**Likely rationale:**
- User gets immediate feedback (good UX)
- No inconsistent states (simple logic)
- Stripe integration straightforward

**Potential issues:**
- Payment processing blocks API (slow endpoint)
- Network timeout could lose payment (not retryable)
- Slow payments create poor user experience at scale

**Confidence:** High (multiple sources align)

**Verification:** Run test to confirm behavior

**If wrong:** Would see background payment processing code, async tasks, payment status queries
```

---

## Decision Quality Assessment

### Criteria for Good Decisions

**A good architectural decision:**
1. **Clear rationale:** "Why this vs. alternatives?"
2. **Trade-off awareness:** "What are we giving up?"
3. **Consequences documented:** "What happens next?"
4. **Alternatives considered:** "Why not X?"
5. **Time-boxed:** "When was this decided?"
6. **Reversible (ideally):** "Can we undo this?"

### Decision Quality Scoring

```
Clarity: Does rationale explain why this choice? (1-10)
Completeness: Are alternatives considered? (1-10)
Prescience: Does it hold up over time? (1-10)
Reversibility: Could we change this if needed? (1-10)
Documentation: Is it recorded? (1-10)

Average = Quality Score

> 8: Excellent decision
6-8: Good decision
4-6: Adequate decision (some uncertainty)
< 4: Poor decision (should reconsider)
```

### Examples

**High-quality decision:**
```
"Use PostgreSQL because:
- Orders require ACID transactions (absolute requirement)
- Reporting queries need complex joins (proven need)
- Team expertise in PostgreSQL (30+ person-years)
- Cost favorable vs. alternatives at 10K qps
- Can migrate to read replicas if scaling needed
Alternatives: MongoDB (no ACID), DynamoDB (too expensive)
Decided: 2023-03-15, Still valid: 2025-11-01"

Quality Score: 9/10 (clear, complete, time-tested)
```

**Poor-quality decision:**
```
Code shows: Custom JSON serialization instead of standard library

No documentation, no comments. Inferred rationale: Unknown.
Possible reasons: Performance? Functionality gap? Accidental?

Quality Score: 2/10 (undocumented, reasoning unclear, hard to assess)
```

---

## Capturing Decisions Retroactively

### Workflow for Undocumented Codebase

**Step 1: Identify Key Decisions**

```bash
# Find major architectural choices
grep -r "class.*Service\|interface.*\|abstract" src/ --include="*.py" | head -20

# Look for non-obvious patterns
grep -r "async\|Queue\|Cache\|Index" src/ --include="*.py"

# Find TODOs indicating decisions
grep -r "TODO\|DECISION\|WHY" src/ --include="*.py"
```

**Step 2: Gather Context**

```bash
# Git blame to find original author
git blame -L 45,50 src/payment.py

# Contact author if possible (email, chat)
# Ask: "Why did you implement it this way?"

# Read commit message for context
git show abc1234
```

**Step 3: Infer from Code + Tests**

```python
# Code shows: Pessimistic locking
query = select_for_update(Order).filter(Order.id == order_id)

# Test shows:
def test_concurrent_modifications_not_lost():
    # Test verifies isolation

# Inference: Decision was "Use locks for consistency"
# Rationale: Race conditions were a problem
```

**Step 4: Document Decision**

```markdown
# ADR-012: Use Pessimistic Locking for Order Updates (Inferred)

## Status
Inferred from code (original decision date unknown)

## Context
Orders can be modified by multiple processes:
- Refund processor
- Fulfillment service
- Admin tool

Without locking, concurrent modifications could be lost.

## Decision
Use SELECT FOR UPDATE (pessimistic locking) to ensure only one process
modifies an order at a time.

## Rationale (Inferred)
- Avoids race conditions (orders are critical)
- Simpler than optimistic locking (no version numbers)
- Acceptable performance for order rate

## Evidence
- Code: src/orders/service.py:45 uses select_for_update()
- Test: test_concurrent_order_updates_are_isolated verifies locking
- Pattern: Used consistently for all writes

## Alternatives (Not Chosen)
- Optimistic locking: Would require version numbers
- Message queue: Would serialize updates (slower)
- No locking: Would risk lost updates (unacceptable)

## Confidence: High
Multiple sources of evidence point to this design
```

---

## Decision Documentation Maintenance

### Keeping ADRs Fresh

**Every 6 months:**
```
Review each ADR:
- [ ] Still accurate?
- [ ] Still best choice?
- [ ] Should we change anything?
- [ ] Update "Last reviewed" date
```

**When code changes:**
```
If code changes architecture:
- [ ] Update related ADR
- [ ] Add "Superseded by ADR-XXX" if replacing
- [ ] Keep old ADR (history matters)
```

**Example: Decision Evolution**

```markdown
# ADR-001: Use PostgreSQL (ACCEPTED, 2023)
# ADR-015: Add Redis for Caching (ACCEPTED, 2024)
# ADR-028: Migrate Reads to ReadReplica (ACCEPTED, 2025)

Progression: PostgreSQL → PostgreSQL + Redis → PostgreSQL + replica + Redis
Each decision builds on previous, not replacing
```

### Decision Reversibility

**Good decision:** "Can we change this if we're wrong?"

```
PostgreSQL choice:
- Could migrate to MongoDB if needed (data migration project)
- Could add DynamoDB for specific use case
- Effort: High but doable

Cache choice:
- Could change from Redis to Memcached (API compatible)
- Could add second cache layer
- Effort: Low to medium
```

**Bad decision:** "We're locked in"

```
Custom query language:
- Would require rewriting all queries if we change
- No clear exit strategy
- Risk: Technology debt that can't be fixed
```

---

## Decision Anti-Patterns

### Anti-Pattern 1: Cargo Cult Decision

```markdown
## BAD EXAMPLE

"We're using microservices"

Why? "That's what everyone does now"
Alternatives considered? No
Trade-offs understood? No
Team capacity? Unknown
Complexity cost? Not assessed

Result: Distributed monolith, same problems as monolith, more operational pain
```

### Anti-Pattern 2: Undocumented Decision

```
Code shows: Custom ORM instead of SQLAlchemy

No documentation, no comments.
Potential reasons: Performance? Security? Requirement?

Years later: New engineer tries to use SQLAlchemy
Breaks subtle assumptions in custom ORM
Nobody remembers why custom ORM existed

Result: Technical debt, confusion, repeated mistakes
```

### Anti-Pattern 3: Reversing a Decision Without Updating ADR

```markdown
OLD ADR:
"ADR-005: Use MySQL for primary database (ACCEPTED, 2020)"

Current code: Uses PostgreSQL

Problems:
1. Old ADR makes it look like MySQL is standard
2. New engineers think it's a bug
3. Confusion about why migration happened

Solution: Mark ADR as "Superseded by ADR-009"
```

---

## Decision Capture Template for Code Review

**When reviewing pull request, check:**

```
Does this change make an architectural decision?
- [ ] Yes
- [ ] No

If YES, is it documented?
- [ ] ADR exists
- [ ] Decision in commit message
- [ ] Decision in code comment
- [ ] No documentation (add it!)

For undocumented decisions, request:
- [ ] Comment explaining "why this way?"
- [ ] Alternative approaches considered
- [ ] Trade-offs acknowledged
- [ ] Related decisions noted
```

### Example Code Review Comment

```
Great work on the payment retry logic!

One issue: The logic for exponential backoff isn't explained.
This is an important design decision because:
- Affects payment processing reliability
- Performance impact on payment queue
- Should match error handling strategy

Please add:
1. Comment explaining why exponential backoff
2. Reference alternatives (linear, fixed delay)
3. Note the limits (max retries, max delay)

Example:
// DECISION: Exponential backoff with 1s/10s/100s delays
// Why: Avoids overwhelming payment API during glitches
// Alternative: Linear (would hammer API harder)
// Limits: 3 retries max, 100s max delay
```

---

## Summary: Decision Capture Best Practices

1. **Write ADRs for major decisions** (yes/no choice affects architecture)
2. **Include rationale and trade-offs** (not just what, but why)
3. **Document alternatives considered** (shows thinking)
4. **Mark decisions with status** (accepted, rejected, superseded)
5. **Infer decisions from code** (if ADR doesn't exist)
6. **Update ADRs regularly** (decisions evolve)
7. **Keep old ADRs** (history is important)
8. **Mark reversible vs. locked-in** (manage risk)
9. **Review decisions periodically** (challenge assumptions)
10. **Communicate decisions** (handoff readiness depends on this)
