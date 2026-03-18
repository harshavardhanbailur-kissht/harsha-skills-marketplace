# Content Generation Patterns

## Table of Contents
1. [Core Principle: Same Tickets, Different Stories](#core-principle)
2. [PM Guide Generation](#pm-guide-generation)
3. [QA Guide Generation](#qa-guide-generation)
4. [Dev Guide Generation](#dev-guide-generation)
5. [Training Guide Generation](#training-guide-generation)
6. [BA Guide Generation](#ba-guide-generation)
7. [Ops Guide Generation](#ops-guide-generation)
8. [Leadership Summary](#leadership-summary)
9. [Grouping Strategy](#grouping-strategy)
10. [Tone & Voice Guidelines](#tone-voice)

---

## Core Principle

The same set of Jira tickets tells a different story depending on who's reading. A bureau waiver logic fix (LAP-1994) is:

- **For PM**: "We fixed a business rule that was incorrectly rejecting eligible borrowers with score 712, improving approval rates"
- **For QA**: "Bureau waiver threshold boundary: verify score 712 returns YES, score 711 returns NO, test all waiver combinations"
- **For Dev**: "Corrected conditional logic in bureau waiver evaluation — threshold comparison was using `<` instead of `<=`"
- **For Training**: "The system now correctly approves borrowers with CIBIL score 712. Update SOP section 4.3 to reflect this"
- **For BA**: "Bureau waiver rule engine updated: applicants with score >= 712 now receive automatic waiver, aligning with Policy v3.2"
- **For Ops**: "Bureau waiver calculation fix deployed. Monitor bureau-waiver-service for any spike in waiver grants"

Every guide must pass the **"Would this reader act on this?"** test. If not, the content is wrong for this audience.

---

## PM Guide Generation

### Structure Template

```markdown
# Release Notes: [Project] [Version/Sprint] — Product Manager View
**Release Date**: [date]
**Sprint**: [sprint name]
**Tickets Shipped**: [count] ([bugs] fixes, [stories] features)

## Executive Summary
[3-5 sentence narrative: what shipped, biggest wins, any concerns]

## Release Highlights

### [Release Announcement Title 1]
**Status**: [Critical Fix / Live Now / Enhancement]
**Impact**: [audience roles affected]

**What Changed**: [1-2 sentence business narrative]

**Why This Matters**: [Business impact — revenue, efficiency, compliance, UX]

**Key Improvements**:
- [Bullet 1: user-facing improvement]
- [Bullet 2: user-facing improvement]

**Success Metrics**: [How we'll know this worked — adoption, error reduction, etc.]

---

### [Release Announcement Title 2]
[Same structure...]

## Delivery Metrics
| Metric | This Sprint | Trend |
|--------|------------|-------|
| Tickets Shipped | [N] | [up/down/stable] |
| Bug:Feature Ratio | [N:M] | |
| Avg Cycle Time | [N days] | |
| Critical Fixes | [N] | |

## Communication Draft
[Pre-written stakeholder email/Slack message they can send]

## What's Coming Next
[Known upcoming features/fixes from backlog]
```

### Content Rules for PM
- Lead with business impact, not technical change
- Group by Release Announcement Title (thematic grouping)
- Include "Why This Matters" for every group — this is the most important section
- Quantify impact where possible (# of affected users, % improvement)
- Draft a ready-to-send communication message
- Include delivery velocity metrics for sprint retrospective

---

## QA Guide Generation

### Structure Template

```markdown
# Release Notes: [Project] [Version/Sprint] — QA Impact Assessment
**Release Date**: [date]
**Risk Level**: [High/Medium/Low based on content]

## Test Impact Summary
| Module | Changes | Risk | Priority |
|--------|---------|------|----------|
| [Category] | [N tickets] | [H/M/L] | [P1/P2/P3] |

## Critical Test Areas (Priority 1)

### [Feature Category]: [Specific Change]
**Tickets**: [LAP-XXXX, LAP-YYYY]
**What Changed**: [Technical description of change]
**Regression Risk**: [What existing functionality could break]

**Test Scenarios**:
1. [Scenario]: [Expected result]
2. [Scenario]: [Expected result]
3. [Edge case]: [Expected result]

**Test Data Requirements**: [Specific data needed]

---

## Regression Scope

### Must Test (Changed directly)
- [ ] [Area 1] — [reason]
- [ ] [Area 2] — [reason]

### Should Test (Potentially affected)
- [ ] [Area 3] — [reason]

### Smoke Test (Sanity check)
- [ ] [Area 4] — basic functionality

## Journey-Based Test Matrix
| Journey Stage | Changes | Test Priority |
|--------------|---------|--------------|
| [stage] | [description] | [P1/P2/P3] |

## Known Limitations
- [Limitation 1]
- [Limitation 2]
```

### Content Rules for QA
- Lead with risk, not features
- Provide specific test scenarios with expected results
- Map changes to journey stages for systematic testing
- Flag boundary conditions and edge cases explicitly
- Include test data requirements
- Prioritize regression areas by change proximity
- Note any known limitations or deferred fixes

---

## Dev Guide Generation

### Structure Template

```markdown
# Release Notes: [Project] [Version/Sprint] — Developer Changelog
**Release Date**: [date]
**Deployed By**: [name]

## Technical Summary
[1-2 sentences: what services/modules were touched]

## Changes by Module

### [Feature Category / Service Name]

#### [LAP-XXXX]: [Summary]
- **Type**: Bug Fix / Feature / Enhancement
- **Assignee**: [name]
- **Code Area**: [service/module/file area]
- **Change**: [Technical description of what was changed]
- **Related**: [linked tickets if any]

---

## API Changes
| Endpoint | Change Type | Description |
|----------|-----------|-------------|
| [endpoint] | Modified/New/Deprecated | [what changed] |

## Data Model Changes
- [Schema change 1]
- [Schema change 2]

## Configuration Changes
- [Config change 1]

## Technical Debt Notes
- [Workaround in LAP-XXXX that needs future cleanup]
- [Known technical limitation]

## Contributors
| Developer | Tickets | Areas |
|-----------|---------|-------|
| [name] | [count] | [modules] |
```

### Content Rules for Dev
- Lead with module/service organization
- Include ticket key and direct link for every change
- Mention assignee and contributors for knowledge routing
- Flag any technical debt or workarounds
- Note API and data model changes explicitly
- Keep business context minimal — focus on implementation

---

## Training Guide Generation

### Structure Template

```markdown
# Release Update: [Project] [Version/Sprint] — Training & SOP Guide
**Effective Date**: [date]
**Training Priority**: [Mandatory / Recommended / Informational]

## What's Changed for Users

### [User-Friendly Title]
**Who's Affected**: [Sales RM, BCM, CPA, etc.]
**Training Type**: [Mandatory / Recommended / Informational]

**Before**: [How it used to work]
**After**: [How it works now]

**What Users Need to Do Differently**:
1. [Step-by-step instruction]
2. [Step-by-step instruction]

**Screenshot Updates Needed**: [Yes/No — list specific screens]

---

## SOP Update Checklist
| SOP Document | Section | Change Type | Priority |
|-------------|---------|-------------|----------|
| [SOP name] | [section] | Update / New / Remove | [P1/P2/P3] |

## Frequently Asked Questions
**Q**: [Likely question from users]
**A**: [Clear answer]

## Training Schedule Recommendation
| Topic | Audience | Duration | Deadline |
|-------|----------|----------|----------|
| [topic] | [role] | [minutes] | [date] |
```

### Content Rules for Training
- NEVER use technical jargon — write for end users
- Always include Before/After for every change
- List specific SOP documents that need updating
- Identify screenshot requirements explicitly
- Create FAQ based on likely user confusion
- Classify training urgency (Mandatory for critical fixes)
- Group by audience role, not by technical module

---

## BA Guide Generation

### Structure Template

```markdown
# Release Analysis: [Project] [Version/Sprint] — Business Analyst View
**Release Date**: [date]

## Process Impact Assessment

### [Journey Stage]: [Change Summary]
**Affected Process**: [Business process name]
**Change Type**: [New / Modified / Fixed / Removed]

**Impact Analysis**:
- **Data Flow**: [How data movement changed]
- **Business Rules**: [Which rules were modified]
- **Integration**: [System integration changes]
- **User Experience**: [Process step changes]

**Tickets**: [LAP-XXXX, LAP-YYYY]

---

## Journey Stage Impact Matrix
| Journey Stage | Changes | Impact Level | Tickets |
|--------------|---------|-------------|---------|
| [stage] | [summary] | [H/M/L] | [keys] |

## Integration Changes
| Source System | Target System | Change | Impact |
|-------------|--------------|--------|--------|
| [Saral/LSQ] | [LOS/LAP] | [what changed] | [effect] |

## Data Model Changes
| Entity | Field | Change | Business Rule |
|--------|-------|--------|--------------|
| [entity] | [field] | [change] | [rule affected] |

## Requirements Traceability
| BRD/PRD Item | Ticket(s) | Status | Notes |
|-------------|-----------|--------|-------|
| [requirement] | [keys] | [Complete/Partial] | [gap notes] |
```

### Content Rules for BA
- Map every change to a business process
- Track journey stage impacts systematically
- Document integration changes between systems
- Note data model and business rule modifications
- Provide requirements traceability where possible
- Flag any gaps between requirements and delivery

---

## Ops Guide Generation

### Structure Template

```markdown
# Release Notes: [Project] [Version/Sprint] — Operations Runbook
**Release Date**: [date]
**Deployment Window**: [time]
**Risk Level**: [Critical / Standard / Low]

## Deployment Summary
| Item | Detail |
|------|--------|
| Version | [version] |
| Tickets | [count] |
| Critical Fixes | [count] |
| Services Affected | [list] |

## Pre-Deployment Checklist
- [ ] [Check 1]
- [ ] [Check 2]

## Post-Deployment Verification
- [ ] [Verify 1]
- [ ] [Verify 2]

## Monitoring Changes
| Service | Alert | Threshold | Action |
|---------|-------|-----------|--------|
| [service] | [alert] | [threshold] | [what to do] |

## Rollback Procedure
1. [Step 1]
2. [Step 2]

## Known Issues
| Issue | Impact | Workaround | Fix ETA |
|-------|--------|-----------|---------|
| [issue] | [impact] | [workaround] | [eta] |

## Escalation Contacts
| Area | Primary | Secondary |
|------|---------|-----------|
| [area] | [name] | [name] |
```

---

## Leadership Summary

### Structure Template

```markdown
# Release Summary: [Project] [Version/Sprint]
**Date**: [date]

## In One Paragraph
[Executive summary: what shipped, business impact, team performance]

## Key Numbers
| Metric | Value |
|--------|-------|
| Features Shipped | [N] |
| Bugs Fixed | [N] |
| Critical Fixes | [N] |
| Avg Cycle Time | [N days] |

## Top 3 Wins
1. [Win + business impact]
2. [Win + business impact]
3. [Win + business impact]

## Top 3 Risks
1. [Risk + mitigation]
2. [Risk + mitigation]
3. [Risk + mitigation]

## Team Recognition
[Developer/team shoutouts for significant contributions]
```

---

## Grouping Strategy

Tickets should be grouped into **Release Announcements** — thematic clusters that tell a coherent story:

**Grouping Criteria** (in priority order):
1. **Feature Category** — Same module/system area
2. **Journey Stage** — Same part of the loan lifecycle
3. **User Impact** — Same user roles affected
4. **Fix Type** — Critical fixes grouped for urgency

**Naming Convention**: `[Status]: [Feature Area] | [Business Domain]`

Examples:
- "Live Now: Document Management Overhaul | LOS & Saral Integration"
- "Critical Fix: Transaction Status & Sanction Pipeline | Loan Disbursement"
- "Enhancement: KYC, Selfie & Address Verification | Identity Verification"

Each group should have:
- 3-15 related tickets
- A "What's New" summary
- A "Why This Matters" narrative
- Key highlights (3-5 bullet points)
- Access & controls note (who can use it, permissions needed)

---

## Tone & Voice

### General Rules
- Write in active voice
- Be specific — no "various improvements" or "several fixes"
- Use Kissht domain terminology correctly (see kissht-domain.md)
- Every sentence should pass the "so what?" test

### Tone by Stakeholder
| Stakeholder | Tone | Avoid |
|------------|------|-------|
| PM | Strategic, outcome-focused | Technical jargon, code references |
| QA | Precise, risk-aware | Business metrics, strategy talk |
| Dev | Technical, concise | Marketing language, vague descriptions |
| Training | Friendly, instructional | Technical details, acronyms without expansion |
| BA | Analytical, process-oriented | Code-level details, ops concerns |
| Ops | Operational, action-oriented | Feature narratives, business strategy |
| Leadership | Executive, metrics-driven | All technical details |

---

## AI Content Generation Framework (COSTAR Method)

For each stakeholder guide, apply the COSTAR framework:

**C — Context**: Release metadata (sprint, date, project, ticket count)
**O — Objective**: Stakeholder-specific goal (PM wants narrative, QA wants test scope, etc.)
**S — Style**: Tone from the tone matrix above
**T — Tone**: Professional, precise, domain-aware
**A — Audience**: The specific stakeholder receiving this guide
**R — Response Format**: Structure template from the relevant templates/*.md file

### Content Transformation Pipeline

```
Raw Ticket Data
    │
    ├─→ [Classification Engine] → category, journey, status, audience
    │
    ├─→ [Domain Enrichment] → business context, system mappings, terminology
    │
    ├─→ [Stakeholder Lens] → filter + transform per COSTAR
    │
    ├─→ [Grouping Engine] → cluster into release announcements
    │
    ├─→ [Template Rendering] → apply structure template
    │
    ├─→ [Confidence Tagging] → mark each claim with confidence level
    │
    └─→ [Verification Loop] → cross-check against source data
```

### NLP Classification Patterns

When classifying tickets automatically, use these keyword → category mappings with weighted scoring:

**High-confidence keywords** (weight: 3):
- "document upload", "doc sync", "saral" → Document Management
- "KYC", "aadhaar", "selfie", "liveness" → KYC & Identity
- "bureau", "CIBIL", "waiver", "BRE", "CAM" → Credit & Bureau
- "sanction", "disbursal", "tranche", "fee" → Transaction & Sanction
- "PD visit", "property", "home visit" → Sales PD & Property

**Medium-confidence keywords** (weight: 2):
- "LOS panel", "smart view", "form" → LOS Panel & Operations
- "co-applicant", "IC", "top-up" → Multi-Applicant & Top-Up
- "field mapping", "dropdown", "format" → Data Consistency

**Low-confidence keywords** (weight: 1):
- "fix", "issue", "bug" → General Fixes (catch-all, needs manual review)

Score threshold: ≥ 3 = confident classification, < 3 = flag for manual review.

### Python NLP Classification Engine (spaCy + scikit-learn)

For production-grade automated classification, use this pipeline:

```python
# ticket_classifier.py — NLP-powered ticket classification
import re
from collections import Counter

class KishtTicketClassifier:
    """
    Lightweight NLP classifier for Kissht Jira tickets.
    Uses TF-IDF-like weighted keyword matching + domain rules.
    No external ML dependencies required (works standalone).
    For advanced usage, integrate spaCy or scikit-learn.
    """

    # Domain-specific keyword weights
    CATEGORY_RULES = {
        "Document Management": {
            "high": ["document upload", "doc sync", "saral", "document replace",
                     "document cleanup", "file upload", "pdf", "image upload"],
            "medium": ["attachment", "file", "upload"],
            "journey": ["Applicant Onboarded → CPA Verified"]
        },
        "KYC & Identity": {
            "high": ["kyc", "aadhaar", "selfie", "liveness", "pan card",
                     "identity verification", "address verification", "ekyc"],
            "medium": ["verification", "identity", "photo"],
            "journey": ["Applicant Valid → Applicant Onboarded"]
        },
        "Credit & Bureau": {
            "high": ["bureau", "cibil", "waiver", "bre", "cam report",
                     "credit score", "experian", "equifax", "bureau pull"],
            "medium": ["score", "credit", "eligibility", "threshold"],
            "journey": ["BRE Approved → CPA Verified"]
        },
        "Transaction & Sanction": {
            "high": ["sanction", "disbursal", "disbursement", "tranche", "fee",
                     "transaction status", "conditional approved", "ncm"],
            "medium": ["loan", "amount", "payment", "emi"],
            "journey": ["IPA Pending → Disbursed"]
        },
        "Sales PD & Property": {
            "high": ["pd visit", "property", "home visit", "valuation",
                     "personal discussion", "sales pd", "site visit"],
            "medium": ["field", "visit", "property"],
            "journey": ["Sales PD Complete"]
        },
        "LOS Panel & Operations": {
            "high": ["los panel", "smart view", "form", "dropdown",
                     "ui fix", "panel", "dashboard"],
            "medium": ["display", "button", "screen", "view"],
            "journey": ["Cross-journey"]
        },
        "Multi-Applicant & Top-Up": {
            "high": ["co-applicant", "income contributor", "top-up",
                     "ic applicant", "multi-applicant", "concurrent"],
            "medium": ["applicant", "co-app"],
            "journey": ["Cross-journey"]
        },
        "Data Consistency": {
            "high": ["field mapping", "dropdown values", "format",
                     "data mismatch", "sync", "standardize"],
            "medium": ["mapping", "format", "value"],
            "journey": ["Cross-journey"]
        },
        "BRE & Eligibility": {
            "high": ["bre rule", "eligibility", "program", "business rule",
                     "rule engine", "whitelist", "mavis"],
            "medium": ["rule", "eligible", "qualify"],
            "journey": ["BRE Approved → CPA Verified"]
        },
        "Integration": {
            "high": ["saral los", "lsq lap", "api", "integration",
                     "webhook", "account aggregator", "aa redirect"],
            "medium": ["connect", "interface", "endpoint"],
            "journey": ["Cross-journey"]
        }
    }

    # Hinglish / Indian English patterns common in Kissht tickets
    HINGLISH_MAPPINGS = {
        "updation": "update",
        "updations": "updates",
        "rectification": "fix",
        "rectify": "fix",
        "bifurcation": "split",
        "prepone": "advance",
        "revert": "reply",  # Indian English usage
        "do the needful": "complete the required action",
        "intimation": "notification",
        "disbursment": "disbursement",  # Common typo
        "sanction letter": "sanction document",
    }

    def classify(self, summary: str, labels: list = None,
                 components: list = None) -> dict:
        """Classify a ticket into category + journey stage."""
        # Normalize
        text = summary.lower()
        for hinglish, english in self.HINGLISH_MAPPINGS.items():
            text = text.replace(hinglish, english)

        scores = {}
        for category, rules in self.CATEGORY_RULES.items():
            score = 0
            for keyword in rules["high"]:
                if keyword in text:
                    score += 3
            for keyword in rules["medium"]:
                if keyword in text:
                    score += 2
            # Boost from Jira labels/components
            if labels:
                for label in labels:
                    if label.lower() in text or any(
                        k in label.lower() for k in rules["high"]
                    ):
                        score += 2
            if components:
                for comp in components:
                    if any(k in comp.lower() for k in rules["high"]):
                        score += 3
            scores[category] = score

        # Get best match
        best = max(scores, key=scores.get)
        confidence = scores[best]

        if confidence >= 6:
            conf_level = "VERIFIED"
        elif confidence >= 3:
            conf_level = "HIGH"
        elif confidence >= 2:
            conf_level = "MEDIUM"
        else:
            conf_level = "LOW"
            best = "General Fixes"  # Fallback

        return {
            "category": best,
            "journey": self.CATEGORY_RULES.get(best, {}).get("journey", ["Unknown"])[0],
            "confidence": conf_level,
            "score": confidence,
            "all_scores": scores
        }

    def classify_status(self, priority: str, issue_type: str,
                        summary: str) -> str:
        """Determine Critical Fix / Live Now / Enhancement status."""
        text = summary.lower()
        if priority in ["Highest", "High"] and issue_type == "Bug":
            return "Critical Fix"
        if any(w in text for w in ["blocker", "crash", "production",
                                    "urgent", "hotfix", "data loss"]):
            return "Critical Fix"
        if issue_type == "Story":
            return "Live Now"
        return "Enhancement"

    def detect_compliance_flag(self, summary: str) -> bool:
        """Flag tickets touching RBI-regulated areas."""
        compliance_keywords = [
            "kfs", "key fact statement", "consent", "data localization",
            "audit trail", "cooling off", "grievance", "lsp disclosure",
            "rbi", "regulatory", "compliance", "account aggregator",
            "digital consent", "e-sign", "otp verification"
        ]
        text = summary.lower()
        return any(kw in text for kw in compliance_keywords)
```

### Advanced NLP: BM25 Ranking for Similar Ticket Detection

```python
# Use BM25 to find similar historical tickets for better classification
import math

class BM25Ranker:
    """BM25 ranking for finding similar tickets in historical data."""

    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus = [doc.lower().split() for doc in corpus]
        self.avgdl = sum(len(d) for d in self.corpus) / len(self.corpus)
        self.df = self._calc_df()
        self.n = len(self.corpus)

    def _calc_df(self):
        df = {}
        for doc in self.corpus:
            for term in set(doc):
                df[term] = df.get(term, 0) + 1
        return df

    def score(self, query: str, doc_idx: int) -> float:
        query_terms = query.lower().split()
        doc = self.corpus[doc_idx]
        dl = len(doc)
        score = 0
        for term in query_terms:
            tf = doc.count(term)
            df = self.df.get(term, 0)
            idf = math.log((self.n - df + 0.5) / (df + 0.5) + 1)
            tf_norm = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            )
            score += idf * tf_norm
        return score

    def rank(self, query: str, top_n: int = 5) -> list:
        scores = [(i, self.score(query, i)) for i in range(self.n)]
        scores.sort(key=lambda x: -x[1])
        return scores[:top_n]
```

### Jinja2 Template Rendering for Stakeholder Guides

```python
# Use Jinja2 for consistent template rendering
from jinja2 import Template

PM_TEMPLATE = Template("""
# Release Notes: {{ project }} {{ version }} — Product Manager View
**Release Date**: {{ release_date }}
**Sprint**: {{ sprint }}
**Tickets Shipped**: {{ total }} ({{ bugs }} fixes, {{ stories }} features)

## Executive Summary
{{ executive_summary }}

## Release Highlights
{% for group in announcements %}
### {{ group.title }}
**Status**: {{ group.status }}
**Impact**: {{ group.audience | join(', ') }}

**What Changed**: {{ group.whats_new }}

**Why This Matters**: {{ group.why_matters }}

**Key Improvements**:
{% for highlight in group.highlights %}
- {{ highlight }}
{% endfor %}

---
{% endfor %}

## Delivery Metrics
| Metric | This Sprint | Trend |
|--------|------------|-------|
| Tickets Shipped | {{ total }} | {{ trend }} |
| Bug:Feature Ratio | {{ bugs }}:{{ stories }} | |
| Avg Cycle Time | {{ avg_cycle_time }} days | |
| Critical Fixes | {{ critical_count }} | |
""")
```

### Hallucination Prevention for Fintech

Critical rules when generating release note content for a regulated fintech:

1. **NEVER fabricate financial figures**: Interest rates, fee percentages, loan limits, score thresholds must come from ticket data or be explicitly marked [?]
2. **NEVER invent regulatory references**: Don't claim "as per RBI circular" unless the ticket explicitly references a regulation
3. **NEVER assume system behavior**: If a ticket says "fixed bureau logic", describe the fix, don't speculate about the exact conditional logic unless described
4. **ALWAYS attribute claims to sources**: "Based on LAP-1994..." or "Per the ticket summary..."
5. **ALWAYS flag uncertainty**: Use the confidence tagging system from stakeholder-profiles.md
6. **NEVER generate test data examples with real-looking PII**: No real-seeming Aadhaar numbers, PAN numbers, phone numbers in QA guides

### Verification Checklist (Pre-Publication)

Before any stakeholder guide is finalized:

- [ ] Every ticket key mentioned exists in the source data
- [ ] No financial figures were fabricated (all traced to source)
- [ ] Confidence tags applied to all inferred content
- [ ] Domain terminology used correctly (cross-reference kissht-domain.md)
- [ ] Stakeholder-inappropriate content filtered (check information density matrix)
- [ ] Ticket counts match source data (total, bugs, stories)
- [ ] All Jira links are valid and point to correct tickets
- [ ] No PII or sensitive credentials appear in any guide
- [ ] Status badges (Critical Fix / Live Now / Enhancement) match classification rules

---

## Multi-Format Output Patterns

### Keep-a-Changelog Standard (for Dev guides)
Follow keepachangelog.com format for developer changelogs:
- **Added** — New features (Story tickets)
- **Changed** — Changes in existing functionality (Enhancement)
- **Fixed** — Bug fixes (Bug tickets)
- **Deprecated** — Soon-to-be removed features
- **Removed** — Removed features
- **Security** — Vulnerability fixes

### Stripe-Style Release Notes (for PM guides)
Inspired by Stripe's release notes format:
- Date header with version
- One-paragraph human-readable summary
- Feature highlights with before/after comparison
- "Breaking Changes" section clearly separated
- Code/API examples where relevant (Dev tab only)

### SRE Runbook Format (for Ops guides)
Following Google SRE handbook patterns:
- Deployment steps as numbered checklist
- Monitoring dashboard links
- Alert threshold changes table
- Rollback procedure with estimated time
- Escalation matrix with on-call rotation

---

## Release Note Quality Assessment Framework

### Anti-Slop Rules for AI-Generated Content

AI-generated release notes must avoid these common failure modes:

| Failure Mode | Example | Fix |
|-------------|---------|-----|
| **Vague language** | "Various improvements made" | Name specific changes: "Fixed bureau waiver threshold for scores 712+" |
| **Feature-stuffing** | Listing 45 tickets without grouping | Group into 6-8 release announcements |
| **Missing "so what"** | "Changed dropdown values" | "Standardized dropdown values so BCM can select correct property type" |
| **Wrong audience tone** | Technical jargon in Training guide | Filter through information density matrix |
| **Fabricated metrics** | "Improved performance by 40%" | Only use metrics from ticket data, tag [?] if inferred |
| **Orphan tickets** | Ticket mentioned but not in source data | Pre-publication verification catches this |
| **Stale context** | Referencing old journey stages | Cross-check against latest kissht-domain.md |

### Sentiment-Aware Content Framing

Use VADER-style sentiment analysis on ticket summaries to frame content appropriately:

```python
# Simplified sentiment for ticket framing
def frame_ticket(summary: str, issue_type: str) -> str:
    """Determine framing tone based on ticket content."""
    negative_signals = ["fix", "bug", "error", "fail", "crash", "missing",
                        "incorrect", "wrong", "broken", "block", "issue"]
    positive_signals = ["add", "new", "enhance", "improve", "feature",
                        "enable", "support", "implement", "introduce"]

    text = summary.lower()
    neg_count = sum(1 for w in negative_signals if w in text)
    pos_count = sum(1 for w in positive_signals if w in text)

    if issue_type == "Bug" or neg_count > pos_count:
        return "fix"      # Frame as reliability improvement
    elif pos_count > neg_count:
        return "feature"  # Frame as capability expansion
    else:
        return "enhancement"  # Frame as quality improvement
```

### Release Note Tools Ecosystem (Reference)

Industry tools that inform our patterns (this skill generates equivalent output without these tools):

| Tool | What It Does | Pattern We Adopt |
|------|-------------|-----------------|
| **Release Drafter** (GitHub) | Auto-drafts changelogs from PRs | Keep-a-Changelog format for Dev guide |
| **LaunchNotes** | Stakeholder-filtered release comms | Role-based tab system in web app |
| **Beamer** | In-app changelogs | Status badges (Critical Fix / Live Now) |
| **Semantic Release** | Auto-versioning from commits | SemVer logic for release classification |
| **Updated.dev** | AI-powered release notes | COSTAR method for multi-audience content |

### Three-Level Output Quality

Every stakeholder guide should support three levels of detail (progressive disclosure):

1. **TL;DR** (1 line): "This sprint: 45 tickets, 4 critical fixes, bureau + document sync improvements"
2. **Summary** (1 paragraph): Executive summary covering top wins, risks, and velocity metrics
3. **Full Guide** (complete document): Stakeholder-specific deep dive with all sections populated

The web app should surface Level 1 as a header, Level 2 as an expandable summary, and Level 3 as the full tab content.
