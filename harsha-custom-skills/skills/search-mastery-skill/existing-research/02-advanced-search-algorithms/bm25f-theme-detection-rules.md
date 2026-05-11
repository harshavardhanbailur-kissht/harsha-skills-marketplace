# Theme Detection Rules for LAP Intelligence Hub v2

## Overview

Themes group related tickets for exploratory analysis. Detection uses BM25F scoring with priority-based conflict resolution.

## Scoring System

**BM25F Algorithm** with field-specific weights:
- Summary field weight: 2.0 (title carries more importance)
- Description field weight: 1.0 (body text less specific)
- **Score Threshold**: >= 2.0 to classify ticket

**Calculation**:
```
score = (matches_in_summary * 2.0) + (matches_in_description * 1.0)
```

Match = regex pattern found (case-insensitive)

## Theme Definitions

### Priority 1 Themes (Domain-Core)

These are fundamental business areas. Assign with highest weight and authority.

#### 1. KYC (Know Your Customer)
**Patterns**:
```
kyc|"know your customer"|customer verification|identity check|verification status|
compliance check|regulatory|aml
```

**Examples**:
- "Add KYC verification step"
- "Implement identity checks for new users"
- "AML compliance dashboard"

**Score Threshold**: >= 2.0

#### 2. TopUp
**Patterns**:
```
topup|top.?up|top.?up transaction|fund wallet|add balance|deposit|recharge|
balance reload|wallet funding
```

**Examples**:
- "Implement topup feature"
- "Fix topup transaction flow"
- "Add topup methods"

**Score Threshold**: >= 2.0

#### 3. Payment
**Patterns**:
```
payment|checkout|transaction|payment gateway|payout|settlement|payment method|
refund|charge|invoice|billing|payment processing
```

**Examples**:
- "Implement Stripe integration"
- "Fix payment retry logic"
- "Add payment reconciliation"
- **Tricky**: Don't conflate "topup" (specific feature) with generic "payment"

**Score Threshold**: >= 2.0

#### 4. Security
**Patterns**:
```
security|encrypt|ssl|tls|vulnerability|breach|penetration test|auth|password|
token|jwt|oauth|two.?factor|2fa|security audit|secure|ssl certificate
```

**Examples**:
- "Implement JWT authentication"
- "Fix SQL injection vulnerability"
- "Enable 2FA"
- "Security audit for payment module"

**Score Threshold**: >= 2.0

### Priority 2 Themes (Feature-Implementation)

These are feature areas or technical categories. Assign when domain themes don't match.

#### 5. Bug Fix
**Patterns**:
```
bug|fix|issue|broken|crash|error|exception|defect|problem|incorrect|
malfunction|regression|patch|hotfix
```

**Examples**:
- "Fix login redirect issue"
- "Patch API timeout bug"
- "Resolve payment calculation error"
- **Tricky**: "Implement fix for X" is still a bug fix if X is broken

**Score Threshold**: >= 2.0

#### 6. Database
**Patterns**:
```
database|db|sql|query|index|migration|schema|table|column|postgres|mysql|
mongodb|redis|cache|orm|performance tuning|data consistency
```

**Examples**:
- "Add database migration for users table"
- "Optimize query performance"
- "Implement Redis caching"

**Score Threshold**: >= 2.0

#### 7. API
**Patterns**:
```
api|endpoint|rest|graphql|webhook|request|response|http|get|post|put|delete|
rate limit|api documentation|openapi|swagger
```

**Examples**:
- "Create user API endpoint"
- "Add webhook support"
- "Document API endpoints"

**Score Threshold**: >= 2.0

#### 8. UI/UX
**Patterns**:
```
ui|ux|interface|frontend|react|vue|angular|component|button|form|dialog|modal|
css|styling|layout|responsive|accessibility|a11y|design|usability
```

**Examples**:
- "Create login form component"
- "Fix responsive design issues"
- "Implement dark mode"

**Score Threshold**: >= 2.0

#### 9. Notification
**Patterns**:
```
notification|email|sms|alert|message|notification|push|inbox|digest|alert|
notification service|notification channel
```

**Examples**:
- "Send email verification"
- "Implement SMS alerts"
- "Create notification service"

**Score Threshold**: >= 2.0

#### 10. Login
**Patterns**:
```
login|signin|authentication|sign.?in|logout|session|credentials|password reset|
forgot password|sign up|registration|account creation
```

**Examples**:
- "Implement password reset flow"
- "Fix login session timeout"
- "Add multi-user login support"

**Score Threshold**: >= 2.0

#### 11. Reporting
**Patterns**:
```
report|analytics|dashboard|metric|statistics|chart|graph|visualization|
export|download|csv|excel|pdf report|audit log
```

**Examples**:
- "Create transaction report"
- "Build analytics dashboard"
- "Export data to CSV"

**Score Threshold**: >= 2.0

#### 12. Admin Panel
**Patterns**:
```
admin|administration|management|control panel|dashboard|manage|configure|
settings|permissions|roles|user management|tenant management
```

**Examples**:
- "Build admin dashboard"
- "Add role-based access control"
- "Create settings management panel"

**Score Threshold**: >= 2.0

#### 13. Performance
**Patterns**:
```
performance|optimization|optimize|slow|latency|lag|bottleneck|profiling|
benchmark|load test|stress test|caching|cdn|compression|memory
```

**Examples**:
- "Optimize query performance"
- "Reduce page load time"
- "Implement caching layer"

**Score Threshold**: >= 2.0

#### 14. Onboarding
**Patterns**:
```
onboarding|onboard|setup|welcome|first.?time|getting started|user setup|
initialization|welcome flow|new user experience|tutorial
```

**Examples**:
- "Create user onboarding flow"
- "Add welcome tour"
- "Implement getting started guide"

**Score Threshold**: >= 2.0

## Conflict Resolution Rules

When a ticket matches multiple themes (score >= 2.0 for each):

1. **Priority 1 > Priority 2**: Domain themes (KYC, TopUp, Payment, Security) override feature themes
2. **Highest Score Wins**: Among themes at same priority level, choose highest BM25F score
3. **Compound Keywords**: If multiple Priority 1 match (e.g., "Payment" + "KYC"), assign both
4. **No Fallback**: If no themes match (all scores < 2.0), ticket is unthemed

**Example Scenarios**:

| Ticket | Matches | Score | Assign |
|--------|---------|-------|--------|
| "Fix payment security vulnerability" | Payment (3.0), Security (2.5) | Multiple Priority 1 | Both Payment + Security |
| "Implement KYC with JWT tokens" | KYC (2.5), Security (2.1) | Multiple Priority 1 | Both KYC + Security |
| "Create payment report" | Payment (2.0), Reporting (2.1) | Priority 1 + 2 | Payment (higher priority) |
| "API rate limiting" | API (2.1), Performance (1.8) | API wins | API |
| "Fix typo in welcome message" | Onboarding (1.2) | Below threshold | None (unthemed) |

## Implementation Pseudocode

```python
def detect_themes(ticket):
    themes = {}

    for theme in THEME_LIST:
        pattern = THEME_PATTERNS[theme]

        summary_matches = count_matches(pattern, ticket['summary'])
        description_matches = count_matches(pattern, ticket['description'] or "")

        score = (summary_matches * 2.0) + (description_matches * 1.0)

        if score >= 2.0:
            themes[theme] = score

    # Conflict resolution
    if not themes:
        return []

    # Check for Priority 1 themes
    priority_1 = {t: s for t, s in themes.items() if t in PRIORITY_1}
    priority_2 = {t: s for t, s in themes.items() if t in PRIORITY_2}

    if priority_1:
        return list(priority_1.keys())  # All Priority 1 matches
    else:
        return [max(priority_2, key=priority_2.get)]  # Highest Priority 2
```

## Test Cases

### Test 1: Single Theme
**Input**: "Implement KYC verification for new users"
- KYC: summary match (1) × 2.0 = 2.0 ✓
- **Output**: ["KYC"]

### Test 2: Multiple Priority 1
**Input**: "Add JWT security to payment processing"
- Payment: summary match × 2.0 = 2.0 ✓
- Security: summary match × 2.0 = 2.0 ✓
- **Output**: ["Payment", "Security"]

### Test 3: Priority 1 vs Priority 2
**Input**: "Database optimization for payment transactions"
- Payment: summary match × 2.0 = 2.0 ✓
- Database: summary match × 2.0 = 2.0 ✓
- **Output**: ["Payment"] (Priority 1 wins)

### Test 4: Below Threshold
**Input**: "Update README with coding guidelines"
- No theme matches above 2.0
- **Output**: [] (no theme)

### Test 5: Description-Heavy Match
**Input**: "LAP-999: System improvements"
- Summary: no clear matches
- Description: "Improve API response times using Redis caching and optimize database queries"
  - API: description match × 1.0 = 1.0 ✗
  - Database: description match × 1.0 = 1.0 ✗
  - Performance: description matches (2) × 1.0 = 2.0 ✓
- **Output**: ["Performance"]

## Notes for Implementation

- Use case-insensitive regex matching
- Pattern order doesn't matter (BM25F is order-agnostic)
- Tickets can have 0, 1, or multiple themes
- Store theme results in theme_index.json as flat assignments (not scored)
- Re-run theme detection after each Jira sync
- Consider caching theme results per ticket to avoid recomputation
