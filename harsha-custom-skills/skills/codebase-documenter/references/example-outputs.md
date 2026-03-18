# Example Outputs

## Complete Example: Order Service Documentation

### Example 1: Small SaaS Order Service

#### YAML Frontmatter

```yaml
---
title: "Order Service"
description: "Manages the complete order lifecycle from creation through fulfillment"
lastUpdated: "2026-03-12"
authors:
  - "alice@example.com"
  - "bob@example.com"
version: "2.1.0"
audience: ["backend engineers", "new team members", "devops"]
complexity: "medium"
readTime: "20 minutes"
tags: ["orders", "payment", "e-commerce", "backend"]
status: "verified"
confidence: "high"
relatedDocs:
  - "payment-service.md"
  - "inventory-service.md"
  - "fulfillment-service.md"
---
```

#### Overview Section

```markdown
# Order Service

## Overview

The Order Service manages the complete order lifecycle: creation, payment processing, inventory management, and fulfillment coordination. It's a Python FastAPI service that handles ~1000 orders/hour in production.

**Key capabilities:**
- Accept customer orders with multiple items
- Calculate totals with tax and discounts
- Process payments via Stripe
- Coordinate with inventory and fulfillment services
- Handle failures and retries automatically

**Not in scope:**
- User authentication (handled by Auth Service)
- Inventory management (delegated to Inventory Service)
- Shipping logistics (handled by Fulfillment Service)

---

## Architecture

### High-Level Flow

```mermaid
graph TB
    Customer["Customer<br/>(via web app)"]
    API["Order API<br/>FastAPI"]
    Inv["Inventory<br/>Service"]
    Pay["Payment<br/>Service"]
    DB["PostgreSQL<br/>Orders DB"]
    Queue["Redis Queue<br/>for jobs"]
    Email["Email Service<br/>async"]

    Customer -->|REST API| API
    API -->|Check stock| Inv
    API -->|Charge card| Pay
    API -->|Save order| DB
    API -->|Queue job| Queue
    Queue -->|Send confirmation| Email
    Queue -->|Update inventory| Inv
```

### Components

**API Server (src/orders/api.py)**
- Request handling for order creation, retrieval, cancellation
- Input validation via Pydantic schemas
- Error handling with proper HTTP status codes
- Authentication middleware (checks JWT tokens)

**Service Layer (src/orders/service.py)**
- Business logic for order processing
- Orchestrates calls to Payment and Inventory services
- Implements retry logic for transient failures
- Calculates totals including tax and discounts

**Data Layer (src/orders/persistence.py)**
- Queries and mutations using SQLAlchemy ORM
- Connection pooling via pgbouncer
- Transaction management (ACID)

**Background Jobs (src/orders/tasks.py)**
- Send confirmation emails via Celery
- Update inventory reservations
- Sync with fulfillment service

---

## API Documentation

### POST /orders - Create Order

**Purpose:** Create a new order for a customer.

**Request:**
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust_123",
    "items": [
      {"product_id": "prod_456", "quantity": 2},
      {"product_id": "prod_789", "quantity": 1}
    ],
    "delivery_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94102"
    }
  }'
```

**Response (200 OK):**
```json
{
  "id": "order_abc123",
  "status": "pending",
  "customer_id": "cust_123",
  "items": [
    {"product_id": "prod_456", "quantity": 2, "price": 29.99, "subtotal": 59.98},
    {"product_id": "prod_789", "quantity": 1, "price": 49.99, "subtotal": 49.99}
  ],
  "subtotal": 109.97,
  "tax": 8.99,
  "shipping": 5.00,
  "total": 123.96,
  "created_at": "2026-03-12T15:30:45Z",
  "delivery_address": {...}
}
```

**Error Cases:**
- 400 BadRequest: Invalid input (empty items, missing address)
- 401 Unauthorized: Missing/invalid JWT token
- 402 PaymentRequired: Card declined
- 409 Conflict: Item out of stock
- 500 InternalServerError: Stripe/database error (with retry header)

**Testing:**
```bash
# Happy path
pytest tests/orders/test_api.py::test_create_order_success

# Error cases
pytest tests/orders/test_api.py::test_create_order_with_invalid_items
pytest tests/orders/test_api.py::test_create_order_payment_declined
```

### GET /orders/{order_id}

**Purpose:** Fetch order details.

**Request:**
```bash
curl -X GET http://localhost:8000/orders/order_abc123 \
  -H "Authorization: Bearer {jwt_token}"
```

**Response (200 OK):** Same structure as POST response (see above)

**Error Cases:**
- 401 Unauthorized: Invalid token
- 404 NotFound: Order doesn't exist
- 403 Forbidden: User not authorized to view this order

---

## Data Models

### Order

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Order:
    id: str                    # UUID, Primary key
    customer_id: str           # Foreign key to customers table
    status: str                # pending, paid, fulfilled, delivered, cancelled
    items: List[OrderItem]     # Line items
    subtotal: Decimal          # Sum of item prices
    tax: Decimal               # Calculated from address
    shipping: Decimal          # Fixed or calculated
    discount: Decimal          # Applied promos
    total: Decimal             # subtotal + tax + shipping - discount
    delivery_address: Address  # Where to ship
    created_at: datetime       # Order creation time
    paid_at: Optional[datetime]  # When payment completed
    shipped_at: Optional[datetime]  # When fulfillment started
    delivered_at: Optional[datetime]  # When customer received
    cancelled_at: Optional[datetime]  # If order cancelled
    stripe_charge_id: Optional[str]   # Reference to Stripe charge
```

**State Transitions:**
```
pending → paid → fulfilled → delivered
    ↓ (payment fails)
  error → pending (retry)

Any state → cancelled (customer or admin)
```

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/orders
DATABASE_POOL_SIZE=20
DATABASE_ECHO=false  # Set to true for SQL logging

# Payment (Stripe)
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Queue
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Email
SENDGRID_API_KEY=...
EMAIL_FROM=orders@example.com

# Timeouts
PAYMENT_TIMEOUT_SECONDS=30
INVENTORY_CHECK_TIMEOUT_SECONDS=10

# Features
ENABLE_ASYNC_CONFIRMATION=true
MAX_ITEMS_PER_ORDER=100
```

---

## Error Handling

### Error Types and Recovery

| Code | Name | Cause | Recovery |
|------|------|-------|----------|
| 400 | ValidationError | Invalid request | Fix input, retry |
| 402 | PaymentRequired | Card declined | Use different card |
| 409 | ConflictError | Item out of stock | Remove item, retry |
| 429 | RateLimitError | Too many requests | Wait, retry after delay |
| 500 | InternalServerError | Stripe/DB error | Retry (idempotent) |
| 503 | ServiceUnavailable | Inventory service down | Retry after 30 seconds |

**Example error response:**
```json
{
  "error": "ConflictError",
  "message": "Item prod_456 out of stock",
  "details": {
    "product_id": "prod_456",
    "requested": 5,
    "available": 2
  },
  "retry_after": null
}
```

---

## Technical Decisions

**ADR-1: Use PostgreSQL for order persistence**
- Why: ACID transactions needed for data consistency
- Alternative: MongoDB (flexibility, but eventual consistency risky)
- Trade-off: Operational responsibility for database

**ADR-2: Synchronous payment processing**
- Why: Immediate customer feedback on success/failure
- Risk: Slow payment API blocks order creation
- Mitigated by: Payment timeout (30s) + retry logic

**ADR-3: Pessimistic locking for order updates**
- Why: Prevent concurrent modification race conditions
- Code: SELECT FOR UPDATE in database queries
- Trade-off: Slightly lower throughput, but guarantee correctness

---

## Known Issues and Limitations

### Current Limitations
1. **No support for partial refunds** - Can only refund entire order
2. **No multi-currency support** - Only USD supported
3. **Tax calculated by address, not item type** - Doesn't account for digital vs. physical
4. **No scheduled order cancellation** - Manual cancellation only

### Performance Characteristics
- Order creation: ~150ms (p95)
- Includes: inventory check, payment processing, database write
- Bottleneck: Stripe API (30ms average, 100ms p95)
- Scaling: Horizontal (stateless), limited by database connections

### Production Monitoring
- Alert if order creation latency > 500ms
- Alert if payment failures > 5% of orders
- Monitor: database connection pool utilization
- Dashboard: orders/minute, payment success rate, error rate

---

## Deployment

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 6.0+
- Stripe API keys

### Local Development
```bash
git clone repo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/
python src/main.py  # Runs on port 8000
```

### Production
```bash
# Docker image
docker build -t order-service:latest .
docker run -e DATABASE_URL=... order-service:latest

# Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl logs deployment/order-service
```

---

## Testing Strategy

### Test Coverage
```
Unit tests: 85% (business logic)
Integration tests: 60% (service-to-service)
E2E tests: 40% (full flows)
Load tests: Payment spike scenarios
```

### Key Test Cases
```python
def test_order_creation_happy_path():
    """Full order creation with payment"""
    # Setup customer, inventory
    # Create order
    # Assert order created, payment charged, email queued

def test_order_creation_payment_fails():
    """Order creation when payment fails"""
    # Mock stripe to fail
    # Create order
    # Assert order NOT created, customer NOT charged

def test_concurrent_orders_same_customer():
    """Two orders created simultaneously"""
    # Create two orders in parallel
    # Assert both succeed, no race conditions
```

---

## Contact and Support

**On-call:** See PagerDuty escalation policy
**Slack channel:** #order-service-oncall
**Code reviewers:** alice@, bob@, carol@
**Last updated by:** Alice Smith (alice@example.com)

---
```

---

## Example 2: Fintech Mode Output Structure

### Fintech-Specific Documentation

```markdown
# Payment Processing Service

## Regulatory Compliance

### PCI-DSS Compliance
- Card data never stored (Stripe tokenization)
- Encryption: AES-256 for sensitive fields
- Audit trail: Complete transaction history
- Compliance: Annual third-party audit

### Anti-Money Laundering (AML)
- Customer verification: KYC process
- Transaction monitoring: Pattern analysis
- Suspicious activity: Reported within 24 hours

## Security-First Documentation

### Authentication & Authorization
- OAuth 2.0 with JWT (1-hour TTL)
- Role-based access: User, Support, Admin, Auditor
- Every API call logged with user ID

### Data Protection
- At-rest encryption: KMS key rotation
- In-transit: TLS 1.3 required
- Sensitive fields marked: [SENSITIVE]

### Incident Response
- Payment failures: Automatic retry with backoff
- Data breaches: Notify affected users within 72 hours
- Audit: Complete post-mortem within 48 hours

---
```

---

## Example 3: Handoff Readiness Score Calculation

```
Documentation Completeness Assessment:

Architecture Documentation: 38/40 points
  ✓ Overview present and clear
  ✓ Major components explained
  ✓ Data flows documented with diagrams
  ✓ Design decisions justified
  × Performance characteristics under-documented

API Documentation: 18/20 points
  ✓ All endpoints documented
  ✓ Request/response examples provided
  ✓ Error codes explained
  × Webhook documentation missing

Data Models: 15/15 points
  ✓ All entities defined
  ✓ Relationships shown
  ✓ State machines documented

Configuration: 9/10 points
  ✓ Environment variables listed
  ✓ Defaults documented
  × Cluster configuration options not mentioned

Testing: 8/10 points
  ✓ Test strategy explained
  ✓ Critical paths tested
  × Load test results missing

Operations: 4/5 points
  ✓ Deployment documented
  × Rollback procedure unclear

===========================================
OVERALL HANDOFF READINESS SCORE: 82/100

Status: MOSTLY READY ✓

Minor gaps to address before handoff:
1. Add performance benchmarks (p50, p95, p99 latencies)
2. Document webhook signatures and retry logic
3. Add troubleshooting guide
4. Clarify rollback procedure

Estimated time to handoff-ready: 4 hours
Recommended next steps: Fill gaps above, get team review
```

---

## Example 4: Output Format Comparison

### Same Documentation in Different Formats

#### Markdown (Source)
```markdown
# Order Service

## Overview
The service handles order processing.

### Data Flow
Orders are created → Payments processed → Shipped
```

#### HTML (Rendered)
```html
<h1>Order Service</h1>
<section id="overview">
  <h2>Overview</h2>
  <p>The service handles order processing.</p>
</section>
<section id="data-flow">
  <h3>Data Flow</h3>
  <p>Orders are created → Payments processed → Shipped</p>
</section>
```

#### PDF (Print)
```
ORDER SERVICE

1. Overview
   The service handles order processing.

   1.1 Data Flow
   Orders are created → Payments processed → Shipped

   [Page 1 of 8]
```

#### JSON (For IDE)
```json
{
  "title": "Order Service",
  "sections": [
    {
      "title": "Overview",
      "content": "The service handles order processing.",
      "subsections": [
        {
          "title": "Data Flow",
          "content": "Orders are created → Payments processed → Shipped"
        }
      ]
    }
  ]
}
```

---

## Common Mistakes to Avoid

### ✗ Bad Example

```markdown
# Order Service

This is the order service. It does order stuff. It was built in 2020. We use Python.

The database is PostgreSQL and we use Redis for caching. There's also Stripe for payments.

Some code is in src/ and tests are in tests/. There are 50000 lines of code.

Configuration happens via env vars. Just read the code to figure out what to set.

We don't really have documentation for this.
```

**Problems:**
- No overview or purpose
- No architecture or design explanation
- No examples or how-to guides
- Technical debt not documented
- No evidence or confidence levels

### ✓ Good Example

```markdown
---
title: "Order Service"
description: "Manages order creation, payment, and fulfillment coordination"
lastUpdated: "2026-03-12"
authors: ["alice@example.com"]
confidence: "high"
---

# Order Service

## Purpose
Processes customer orders from creation through fulfillment. Handles inventory reservations, payment processing via Stripe, and coordination with fulfillment service.

## Architecture
[Diagram showing flow]

## Configuration
See CONFIG.md for complete environment variable reference.

## API
All endpoints documented in API.md with examples.

## Getting Started
1. Clone repo
2. `pip install -r requirements.txt`
3. `pytest tests/`
4. `python src/main.py`

## Known Limitations
- No multi-currency support (documented in technical-debt.md)
- Refunds are full-order only (see issue #234)

## Confidence Level: High
Verified against code, tests, and git history (see evidence-patterns.md)
```

**Improvements:**
- Clear purpose and scope
- Diagrams show architecture
- Configuration documented
- Getting started guide
- Known limitations acknowledged
- Confidence level assigned
