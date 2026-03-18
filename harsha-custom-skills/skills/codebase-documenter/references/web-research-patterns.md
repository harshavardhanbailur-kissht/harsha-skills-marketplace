# Web Research Patterns for Code Analysis

## When and How to Use Web Research

### When Web Research is Necessary

**Use web research when:**
1. Codebase uses external library, need to understand API
2. Code references standards (RFC, OWASP, PCI-DSS)
3. Code implements known pattern or algorithm
4. Codebase extends third-party framework
5. Understanding version compatibility

**Don't use web research when:**
1. Codebase itself explains the pattern
2. Tests demonstrate the behavior
3. Comments document the decision
4. Code is simple enough to understand directly

### The Research Hierarchy

```
Level 1 (Best): Official documentation + code matches
  Example: "See RFC 7231 for HTTP semantics" → Code follows RFC

Level 2 (Good): GitHub repo + active maintenance
  Example: "Uses Flask 2.0 patterns" → Check Flask docs

Level 3 (Okay): Stack Overflow if multiple sources agree
  Example: Common pattern explained in multiple answers

Level 4 (Risky): Blog posts and tutorials
  Example: Single article explaining pattern (may be outdated)

Level 5 (Dangerous): Assumed knowledge (no verification)
  Example: "This is standard, everyone knows it" (untrue)
```

### Research Validation Workflow

```
1. Question: "How does codebase handle X?"
2. Initial search: Find 3-5 sources
3. Compare: Do they agree?
   - If yes, high confidence
   - If no, flag as ambiguous
4. Verify against code: Does code match sources?
5. Age check: Are sources recent (< 2 years)?
   - If no, note version specificity
6. Document: Cite sources in documentation
```

---

## GitHub Issues Mining for Context

### What GitHub Issues Reveal

**Issue descriptions:**
- Why was this built?
- What problem does it solve?
- Context that code alone doesn't show

**Example:**
```
Issue #234: "Order totals incorrect for multi-currency orders"

From issue description:
- Problem: Orders with items in different currencies calculated wrong
- Current behavior: Uses customer's default currency for all items
- Expected: Use item's native currency, convert to customer default
- Root cause: Money exchange rates not considered

This reveals INTENT: Multi-currency support was added (not obvious from code alone)
```

### How to Mine Issues

**Find related issues:**
```bash
# Find issues mentioning this file
gh issue list --repo user/repo --label "payments" --limit 100

# Find issues in specific timeframe
gh issue list --repo user/repo --search "created:2025-01-01..2025-03-01"

# Find closed issues (gives context on past decisions)
gh issue list --repo user/repo --state closed --search "payments"
```

**Extract useful context:**
1. Issue title: Problem statement
2. Description: Why it matters
3. Comments: Alternative approaches considered
4. Linked PRs: Implementation details
5. Closed reason: Why it was resolved

### Evidence Quality from Issues

**High-quality evidence:**
- Issue created near when code was written
- Comments from code authors
- Explicit design decisions
- Reference to RFCs or standards

**Low-quality evidence:**
- Issue created long after code
- Comments from non-authors
- Vague descriptions
- "Fix it" without reasoning

---

## Stack Overflow Cross-Referencing

### The Stack Overflow Caveat

**Stack Overflow obsolescence rate: 58.4%**

Meaning: ~58% of answers are outdated or incomplete within 5 years.

**Mitigation:**
1. Check answer date (prefer recent)
2. Check score and comments (good answers are upvoted, problems noted)
3. Verify against official docs
4. Test in codebase (don't assume answer applies)

### Effective Stack Overflow Searches

**Search pattern:**
```
[language] [framework] [specific problem]

Good: "Python FastAPI async request body validation"
Bad: "How to validate stuff"
```

**Evaluating answers:**
1. Score: Higher score = more people found it useful
2. Comments: Corrections and caveats
3. Date: When was it written?
4. Acceptance: Did author accept answer? (OP validation)
5. Code examples: Does code work?

**Red flags:**
- Answer from 2015 for Python 3.10 question (language evolved)
- Comments saying "this doesn't work"
- Score of 1-2 (only found by searchers, not community validated)
- Accepted answer but newer high-scoring answers contradict it

### Using Stack Overflow Responsibly

**Good use:**
```
"How do I handle async errors in FastAPI?"
→ Find multiple high-scoring answers
→ Cross-reference with official FastAPI docs
→ Test pattern in code
→ Document with source and verification note
```

**Bad use:**
```
"Stack Overflow says X, so implementation is correct"
(Without checking date, verifying against code, or testing)
```

---

## Official Documentation Navigation

### Hierarchy of Official Docs

**Tier 1: Specification documents**
- RFCs (IETF standards)
- Standards (W3C, OWASP, PCI-DSS)
- JSR (Java Specification Request)

**Tier 2: Framework/library official docs**
- Django docs
- React docs
- Spring documentation

**Tier 3: Implementation guides**
- Official tutorials
- Quickstart guides
- API reference

### How to Cite Official Docs

**Good citation:**
```
"Passwords are hashed using PBKDF2 per OWASP guidelines.
See: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
Code: src/auth/hashing.py:45 uses hmac.pbkdf2_hmac()"
```

**Bad citation:**
```
"Passwords are secure"
(No source, no verification, no detail)
```

### Finding Official Docs

**For frameworks:**
```bash
# Check package for link
pip show django | grep Home

# Go to GitHub (official repo is usually in "About" section)
# Look for docs/ directory or link to docs site
```

**For standards:**
```bash
# RFC lookup
# Visit https://tools.ietf.org/html/rfc7231

# W3C standards
# Visit https://www.w3.org/

# OWASP
# Visit https://owasp.org/
```

---

## Source Validation Framework

### Validation Checklist

**For blog posts:**
- [ ] Author has credentials in the domain
- [ ] Published recently (within 2 years)
- [ ] Matches official documentation
- [ ] Code examples are tested
- [ ] Comments point out issues/updates

**For Stack Overflow answers:**
- [ ] Score > 10 (community validated)
- [ ] Published within 3 years
- [ ] No negative comments
- [ ] Matches official docs
- [ ] Tested in your code

**For GitHub repositories:**
- [ ] Maintained (recent commits)
- [ ] Respectable number of stars (1000+)
- [ ] Official or from known author
- [ ] Tests included
- [ ] No security vulnerabilities (check dependabot)

**For official docs:**
- [ ] Matches codebase version
- [ ] Tested examples work
- [ ] Covers your use case
- [ ] Not marked as deprecated

### Red Flags in Online Sources

**Content red flags:**
- "Quick and dirty solution" (might not be production-ready)
- "This is how everyone does it" (without verification)
- "I think this works" (untested)
- No code examples (theoretical without validation)

**Metadata red flags:**
- Published 5+ years ago (technology evolved)
- Low views/engagement (not validated by community)
- Blog not about this topic (off-topic author)
- No author name or profile (accountability)

**Example comment patterns indicating issues:**
- "This doesn't work in version X" (outdated)
- "There's a security issue with this" (critical flaw)
- "Use X instead" (superseded)

---

## Temporal Validity Checking

### Version Drift Problem

**Scenario:**
```
Article published 2019: "Use X for async in Python"
Codebase uses Python 3.10 (2021+)
Python 3.7+ has async/await (standard since 2018)
Article recommends library (now superseded by language feature)
```

**Solution:**
```
For each external reference:
1. Note the version mentioned (Python 3.6? Python 3.8?)
2. Check codebase version (Python 3.10)
3. Verify reference still applies
4. Document version assumptions
```

### How to Check Freshness

**For frameworks:**
```bash
# Check framework version in codebase
grep -r "Django\|Flask\|Rails" requirements.txt Gemfile package.json

# Cross-reference with documentation
# Example: Django 3.2 vs Django 4.0 have different patterns
```

**For standards:**
```bash
# RFC may have obsoleted prior RFCs
# Example: RFC 7231 obsoletes RFC 2616 (HTTP/1.1)

# Check RFC status page
https://tools.ietf.org/html/rfc7231#section-1.1
```

**For library practices:**
```bash
# What was best practice 5 years ago may be anti-pattern now

2018 JavaScript: jQuery is standard → 2024: Native DOM is better
2015 Python: Classes with __init__ → 2024: Dataclasses are cleaner
2010 Java: XML configuration → 2024: Annotations preferred
```

### Marking Temporal Assumptions

```markdown
## Caching Strategy

**Based on:** Redis patterns as of 2024

**Versions assumed:**
- Redis: 6.0+ (supports streams)
- Python: 3.10+ (has structural pattern matching)

**Would differ if:**
- Redis < 5.0: Streams not available, use lists/sorted sets
- Python < 3.7: Use traditional try/except instead of match

**Verification:** Code imports redis.streams (requires 6.0+)

**Last verified:** 2026-03-12 (6+ months = check again)
```

---

## Research Documentation Standards

### Including Research in Documentation

**Template:**

```markdown
## Payment Processing

**How it works:**
[Description from code analysis]

**Based on:**
- Official source: Stripe API documentation (v1.50)
- Reference: https://stripe.com/docs/api/charges
- Accessed: 2026-03-12
- Verified: Code matches documentation

**Code implementation:**
[Code snippets showing integration]

**Testing:**
[Test cases validating behavior]

**Known gaps:**
- Stripe webhook delivery not retried (code could lose events)
- 3D Secure not implemented (limits card types)

**Related discussion:**
- GitHub issue #234: "Add Stripe retry logic"
- Stack Overflow answer: https://stackoverflow.com/a/12345678
  (Score: 42, from 2023, matches our implementation)
```

### When to Exclude Web Research

```markdown
## Order Total Calculation

**Note:** This behavior is unique to our business logic
and not based on external standards.

Equivalent systems:
- Shopify: Calculates tax after discount
- WooCommerce: Calculates tax before discount
- Our choice: Tax on discounted subtotal (business decision)

**Source:** CEO decision (email 2023-06-15), implemented Q3 2023
```

---

## Updating Research as Code Evolves

### Maintenance Workflow

**Quarterly (every 3 months):**
1. List all external references in documentation
2. Check if still current
3. Update if sources changed
4. Note new sources since last update

**Example update:**
```markdown
## Before (outdated)
"Use X for async, per article from 2019"

## After (updated)
"X was standard in 2019; language now has native async/await (since 3.7).
We use native async/await per Python official docs (2021+).
See: https://docs.python.org/3/library/asyncio.html"
```

### Deprecation Tracking

```bash
# Mark documentation sections that reference external sources

# In YAML frontmatter:
research_sources:
  - source: "Stack Overflow #12345"
    verified: "2026-03-12"
    confidence: "high"
    needs_review: false  # Set true if something changed

  - source: "Blog post on async patterns"
    verified: "2024-06-01"
    confidence: "medium"
    needs_review: true  # Over 2 years old
```

---

## Summary: Research Best Practices

1. **Verify against code:** Don't trust research alone
2. **Check dates:** Prefer recent sources (< 2 years)
3. **Cross-reference:** 2+ sources agreeing = higher confidence
4. **Test locally:** Run examples to validate
5. **Document sources:** Show where information came from
6. **Note versions:** What version was this for?
7. **Watch for obsolescence:** Update when patterns change
8. **Flag uncertainties:** Be honest about what you don't know
9. **Use official sources:** Prefer documentation to blog posts
10. **Maintain freshness:** Review quarterly for updates
