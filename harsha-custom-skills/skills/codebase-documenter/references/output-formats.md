# Output Formats Reference

## Markdown Output Format with YAML Frontmatter

### Standard Template

```markdown
---
title: "Order Service Architecture"
description: "Complete order processing system from creation through fulfillment"
lastUpdated: "2026-03-12"
authors:
  - "Alice Smith"
  - "Bob Jones"
version: "2.1.0"
audience: ["backend engineers", "devops", "product managers"]
complexity: "medium"
readTime: "15 minutes"
tags: ["orders", "payments", "architecture", "backend"]
status: "verified"  # verified | draft | outdated
confidence: "high"  # very-high | high | moderate | low
relatedDocs:
  - "payment-service-architecture.md"
  - "inventory-service-architecture.md"
---

# Order Service Architecture

## Overview
[1-2 paragraph description]

## Core Components
[Detailed explanation]

## Data Flow
[ASCII or Mermaid diagram]

## Error Handling
[Error codes and recovery]

## Configuration
[Required settings]
```

### Frontmatter Fields

| Field | Purpose | Example |
|-------|---------|---------|
| title | Document title | "Payment Gateway Integration" |
| description | One-line summary | "Stripe integration with retry and reconciliation" |
| lastUpdated | Last modification date | "2026-03-12" |
| authors | Who wrote/owns this | ["alice@example.com", "bob@example.com"] |
| version | Documentation version | "2.1.0" |
| audience | Who should read this | ["new engineers", "auditors", "architects"] |
| complexity | Cognitive load | "low" \| "medium" \| "high" |
| readTime | Estimated read time | "10 minutes" |
| tags | Searchable tags | ["payments", "stripe", "async"] |
| status | Documentation currency | "verified" \| "draft" \| "outdated" |
| confidence | Claim verification level | "very-high" \| "high" \| "moderate" \| "low" |
| relatedDocs | Cross-references | ["payment-reconciliation.md"] |

### Structure Rules

```markdown
# Level 1 Heading (Document Title)
Only one per document, matches frontmatter title

## Level 2 Heading (Major Sections)
Use for: Overview, Components, Data Flow, Error Handling, Configuration, Examples

### Level 3 Heading (Subsections)
Use for: Entity definitions, field descriptions, code examples

#### Level 4 Heading (Details)
Use sparingly; indicates excessive depth

**Bold** for: Field names, parameter names, key terms
*Italic* for: Emphasis, foreign terms

`code` for: File paths, function names, config keys
```monospaced code block``` for: Large code samples, JSON responses, schemas
```

---

## HTML Output with Navigation

### Generated HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codebase Documentation</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs@1.29/themes/prism-dark.css">
</head>
<body>
    <div class="sidebar">
        <!-- Auto-generated table of contents -->
        <nav class="toc">
            <h3>Contents</h3>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#components">Components</a>
                    <ul>
                        <li><a href="#component-1">Component 1</a></li>
                        <li><a href="#component-2">Component 2</a></li>
                    </ul>
                </li>
                <li><a href="#data-flow">Data Flow</a></li>
            </ul>
        </nav>

        <!-- Metadata sidebar -->
        <aside class="metadata">
            <dl>
                <dt>Last Updated</dt>
                <dd>2026-03-12</dd>

                <dt>Authors</dt>
                <dd>Alice Smith, Bob Jones</dd>

                <dt>Confidence</dt>
                <dd class="confidence-high">High</dd>

                <dt>Read Time</dt>
                <dd>15 minutes</dd>

                <dt>Status</dt>
                <dd class="status-verified">Verified</dd>
            </dl>
        </aside>
    </div>

    <main class="content">
        <!-- Breadcrumb navigation -->
        <nav class="breadcrumb">
            <a href="index.html">Home</a> /
            <a href="architecture.html">Architecture</a> /
            <span>Order Service</span>
        </nav>

        <!-- Document content -->
        <article>
            <h1>Order Service Architecture</h1>

            <!-- Auto-generated document info -->
            <div class="doc-info">
                <p><strong>Audience:</strong> Backend engineers, DevOps</p>
                <p><strong>Complexity:</strong> Medium</p>
                <p><strong>Read time:</strong> ~15 minutes</p>
            </div>

            <!-- Main content -->
            <section id="overview">
                <h2>Overview</h2>
                <p>...</p>
            </section>

            <!-- Collapsible sections for long content -->
            <section id="components">
                <h2>Components</h2>

                <details>
                    <summary>Service Layer</summary>
                    <p>Detailed explanation...</p>
                </details>

                <details>
                    <summary>Data Access Layer</summary>
                    <p>Detailed explanation...</p>
                </details>
            </section>

            <!-- Cross-references -->
            <aside class="related-docs">
                <h3>Related Documentation</h3>
                <ul>
                    <li><a href="payment-service.html">Payment Service</a></li>
                    <li><a href="inventory-service.html">Inventory Service</a></li>
                </ul>
            </aside>
        </article>

        <!-- Search functionality -->
        <div id="search-results" style="display:none;">
            <h3>Search Results</h3>
            <ul id="results-list"></ul>
        </div>
    </main>

    <footer>
        <p>Generated by Codebase Handoff Documenter V6</p>
        <p><a href="index.html">Back to home</a></p>
    </footer>

    <script src="prism.js"></script>
    <script src="navigation.js"></script>
    <script src="search.js"></script>
</body>
</html>
```

### HTML Features

- **Syntax highlighting:** Prism.js for code blocks
- **Auto-generated TOC:** From heading hierarchy
- **Collapsible sections:** For dense content
- **Breadcrumb navigation:** For location awareness
- **Search:** Client-side document search
- **Responsive design:** Mobile-friendly layout
- **Dark mode toggle:** Eye-friendly reading

---

## PDF-Ready Format

### PDF Generation Requirements

```markdown
# PDF Export Configuration

## Page Setup
- Paper size: A4
- Margins: 2cm (top, bottom), 2.5cm (left, right)
- Headers: "Organization - Codebase Documentation" (right-aligned)
- Footers: "Page {page} of {total}" (centered)

## Typography
- Body text: 11pt, line-height 1.5
- Headings: 18pt (H1), 14pt (H2), 12pt (H3)
- Code: 9pt monospaced, gray background
- Links: Blue, underlined

## Structure for Print
- Cover page with metadata
- Table of contents with page numbers
- Document sections
- Appendix with code listings
- Index (if >100 pages)

## Avoiding Print Issues
- Page breaks before major sections
- Avoid fragmented tables across pages
- Code blocks with explicit line breaks
- No JavaScript-dependent content
```

### PDF Rendering Tool Integration

```bash
# Using pandoc
pandoc documentation.md \
    --pdf-engine=xelatex \
    --template=template.latex \
    --toc \
    --toc-depth=2 \
    --output=documentation.pdf

# Using WeasyPrint (Python)
from weasyprint import HTML
HTML('documentation.html').write_pdf('documentation.pdf')

# Using wkhtmltopdf (deprecated but still used)
wkhtmltopdf documentation.html documentation.pdf
```

---

## IDE-Compatible JSON Format

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Codebase Documentation",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "version": {"type": "string"},
        "lastUpdated": {"type": "string", "format": "date"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "string"}}
      }
    },
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "title": {"type": "string"},
          "content": {"type": "string"},
          "level": {"type": "integer"},
          "subsections": {"type": "array"},
          "codeReferences": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "file": {"type": "string"},
                "line": {"type": "integer"},
                "symbol": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "apiEndpoints": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
          "summary": {"type": "string"},
          "parameters": {"type": "array"},
          "responses": {"type": "object"}
        }
      }
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "fields": {"type": "array"},
          "relationships": {"type": "array"}
        }
      }
    }
  }
}
```

### IDE Integration

**IntelliJ/WebStorm autocomplete:**
```json
{
  "metadata": {
    "title": "Payment Service",
    "description": "Stripe integration with retry logic"
  },
  "codeReferences": [
    {
      "file": "src/payments/stripe_gateway.py",
      "line": 45,
      "symbol": "StripeGateway.charge",
      "type": "function"
    },
    {
      "file": "src/payments/retry.py",
      "line": 12,
      "symbol": "ExponentialBackoffRetry",
      "type": "class"
    }
  ]
}
```

**VS Code hover documentation:**
```json
{
  "hover": {
    "file": "src/orders/service.py",
    "line": 34,
    "symbol": "OrderService.create",
    "documentation": "Creates an order from customer input...",
    "relatedDoc": "order-service.md#create-order"
  }
}
```

---

## Quick Reference Card Format

### Single-Page Cheat Sheet

```markdown
# Order Service - Quick Reference (1 page)

## Core Concepts
| Term | Definition | Example |
|------|-----------|---------|
| Order | Customer purchase | `{"id": 1, "total": 99.99}` |
| Status | Order state | pending, paid, shipped, delivered |
| Item | Line item in order | `{"product_id": 1, "qty": 2}` |

## Common Tasks

### Create Order
```bash
curl -X POST /orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "items": [...]}'
```

### Get Order
```bash
curl -X GET /orders/123
```

### Cancel Order
```bash
curl -X DELETE /orders/123
```

## Error Codes
| Code | Meaning | Action |
|------|---------|--------|
| 400 | Invalid input | Check fields |
| 404 | Order not found | Verify ID |
| 409 | Can't cancel | Order already shipped |

## Configuration
```bash
ORDER_TIMEOUT=30s
ORDER_MAX_ITEMS=1000
ORDER_ARCHIVE_AFTER=90d
```

## Architecture
```
[Customer] → [API] → [Service] → [Database]
             ↓
          [Cache]
```

## Troubleshooting
| Problem | Solution |
|---------|----------|
| Slow creation | Check database connection |
| Errors 500 | See error logs |
| Stuck orders | Manual cancel in DB |

## Related Docs
- Payment Service
- Inventory Service
- Fulfillment Service
```

---

## Living Documentation Format with Temporal Validity Headers

### Temporal Metadata

```markdown
---
validity:
  startDate: "2026-03-12"
  expiryDate: "2026-09-12"  # 6-month TTL
  reviewSchedule: "quarterly"
  lastReviewDate: "2026-03-12"
  reviewDueDate: "2026-06-12"
  reviewer: "alice@example.com"

changeLog:
  - version: "2.1.0"
    date: "2026-03-12"
    changes: "Added webhook documentation, updated error codes"
    reviewer: "alice@example.com"

  - version: "2.0.0"
    date: "2026-01-15"
    changes: "Major refactor: split into microservices"
    reviewer: "bob@example.com"
---

# Document with Expiration
```

### Temporal Validity Implementation

```python
def check_documentation_freshness(doc_metadata):
    """Warn if documentation is stale."""
    from datetime import datetime, timedelta

    expires = datetime.fromisoformat(doc_metadata['validity']['expiryDate'])
    today = datetime.today()

    if today > expires:
        return {
            'status': 'EXPIRED',
            'message': f'Documentation expired on {expires.date()}',
            'action': 'Needs review'
        }

    days_until_review = (
        datetime.fromisoformat(doc_metadata['validity']['reviewDueDate']) - today
    ).days

    if days_until_review < 7:
        return {
            'status': 'REVIEW DUE SOON',
            'message': f'Review due in {days_until_review} days',
            'action': 'Schedule review'
        }

    return {'status': 'CURRENT', 'message': 'Documentation is current'}
```

### Living Documentation Features

- **Auto-expiration warnings:** Review reminders
- **Version tracking:** Change history
- **Reviewer attribution:** Who verified this?
- **TTL-based reminders:** Review every 6 months
- **Breaking change alerts:** Highlighted in TOC if recent

---

## Handoff Readiness Score Calculation

### Scoring Framework

```python
class HandoffReadinessScore:
    def __init__(self, documentation):
        self.doc = documentation

    def calculate(self):
        """Calculate handoff readiness 0-100."""
        scores = {
            'architecture': self._score_architecture(40),
            'api': self._score_api_documentation(20),
            'errors': self._score_error_handling(15),
            'configuration': self._score_configuration(10),
            'testing': self._score_test_documentation(10),
            'operations': self._score_operational_readiness(5)
        }

        total = sum(scores.values())
        return {
            'overallScore': total,
            'breakdown': scores,
            'readiness': self._readiness_level(total),
            'gaps': self._identify_gaps(scores)
        }

    def _score_architecture(self, max_points):
        """Score 0-max based on architecture documentation."""
        checks = [
            ('overview_present', self.doc.has_overview),
            ('data_flow_documented', self.doc.has_data_flow_diagram),
            ('components_explained', self.doc.component_coverage > 0.8),
            ('relationships_documented', self.doc.has_relationships),
            ('patterns_identified', self.doc.has_pattern_analysis),
        ]
        return int((sum(checks) / len(checks)) * max_points)

    def _score_api_documentation(self, max_points):
        """Score 0-max based on API completeness."""
        endpoints_total = self.doc.total_endpoints
        endpoints_documented = self.doc.documented_endpoints
        coverage = endpoints_documented / endpoints_total if endpoints_total > 0 else 0

        coverage_score = coverage * 50
        response_docs = (
            sum(1 for e in self.doc.endpoints if e.response_documented) / max(endpoints_total, 1)
        ) * 30
        error_docs = (
            sum(1 for e in self.doc.endpoints if e.errors_documented) / max(endpoints_total, 1)
        ) * 20

        return int((coverage_score + response_docs + error_docs) / 100 * max_points)

    def _score_error_handling(self, max_points):
        """Score 0-max based on error documentation."""
        errors_total = self.doc.total_error_codes
        errors_documented = self.doc.documented_error_codes
        coverage = errors_documented / errors_total if errors_total > 0 else 0

        recovery_documented = sum(
            1 for e in self.doc.errors if e.recovery_strategy
        ) / max(errors_total, 1)

        return int((coverage * 60 + recovery_documented * 40) / 100 * max_points)

    def _readiness_level(self, score):
        """Convert score to readiness level."""
        if score >= 90:
            return "READY_NOW"
        elif score >= 75:
            return "MOSTLY_READY"
        elif score >= 60:
            return "PARTIALLY_READY"
        elif score >= 40:
            return "NEEDS_WORK"
        else:
            return "NOT_READY"

    def _identify_gaps(self, scores):
        """List documentation gaps."""
        gaps = []
        if scores['architecture'] < 30:
            gaps.append("Architecture documentation incomplete")
        if scores['api'] < 15:
            gaps.append("API documentation missing")
        if scores['errors'] < 10:
            gaps.append("Error handling underdocumented")
        if scores['configuration'] < 7:
            gaps.append("Configuration not documented")
        if scores['testing'] < 7:
            gaps.append("Testing approach unclear")
        if scores['operations'] < 3:
            gaps.append("Operations guide missing")
        return gaps
```

### Sample Output

```json
{
  "overallScore": 82,
  "readiness": "MOSTLY_READY",
  "breakdown": {
    "architecture": 36,
    "api": 18,
    "errors": 13,
    "configuration": 9,
    "testing": 4,
    "operations": 2
  },
  "gaps": [
    "Testing approach unclear - add test strategy guide",
    "Operations guide missing - document deployment, monitoring, rollback"
  ],
  "recommendation": "Handoff ready with minor gaps. Add 2-3 hours of operations documentation before critical production handoff.",
  "readinessTimeline": {
    "NOW": ["api", "architecture", "errors"],
    "SOON": ["configuration", "testing"],
    "PLAN_FOR": ["operations"]
  }
}
```

---

## Format Selection Guide

| Format | Best For | Advantages | Limitations |
|--------|----------|-----------|------------|
| Markdown | Source control, GitHub, Git | Version control friendly, diffs work | No interactive search |
| HTML | Web browsing, sharing | Full-featured search, navigation | Static snapshot |
| PDF | Printing, archiving, distribution | Guaranteed layout, offline | Not easily searchable |
| JSON | IDE integration, tooling | Machine-readable, autocomplete | Verbose, less human-readable |
| Quick Ref | Pocket guides, cheat sheets | Quick lookup, concise | Limited depth |

**Production recommendation:** Generate all formats from single markdown source. Use Pandoc or custom scripts for conversion.
