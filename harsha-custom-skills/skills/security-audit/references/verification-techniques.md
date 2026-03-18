# Verification Techniques

Methods for confirming security fixes don't break functionality.

---

## Pre-Fix Baseline Capture

Before applying any fix, capture:

### 1. API Response Baseline
```bash
# Capture successful responses
curl -s https://api.example.com/endpoint | jq . > baseline_response.json

# Capture error responses
curl -s https://api.example.com/endpoint?invalid=true | jq . > baseline_error.json

# Capture headers
curl -sI https://api.example.com/endpoint > baseline_headers.txt
```

### 2. Test Suite Output
```bash
# Node.js
npm test > baseline_tests.txt 2>&1
echo $? > baseline_exit_code.txt

# Python
pytest --tb=short > baseline_tests.txt 2>&1

# Go
go test ./... > baseline_tests.txt 2>&1
```

### 3. Key User Flows
Document expected behavior for critical flows:
- Login → Dashboard
- Add to Cart → Checkout → Payment
- Form Submit → Confirmation

---

## Post-Fix Verification

### Step 1: Diff Verification

```bash
# Check only expected files changed
git diff --stat

# Verify no frontend files modified (for backend-only fixes)
git diff --name-only | grep -E '\.(jsx?|tsx?|vue|css|scss|html)$'
# Should return empty for backend fixes

# Check diff size is minimal
git diff --shortstat
```

### Step 2: Test Suite

```bash
# Run same test suite
npm test > postfix_tests.txt 2>&1
diff baseline_tests.txt postfix_tests.txt

# All tests should pass
# No new failures introduced
```

### Step 3: API Response Comparison

```bash
# Same endpoint, same response
curl -s https://api.example.com/endpoint | jq . > postfix_response.json
diff baseline_response.json postfix_response.json
# Should show no differences (or only expected new headers)

# Check new security headers present
curl -sI https://api.example.com/endpoint | grep -E 'X-Content-Type|X-Frame|Strict-Transport'
```

### Step 4: Performance Check

```bash
# Baseline timing
time curl -s https://api.example.com/endpoint > /dev/null
# real    0m0.150s

# Post-fix timing (should be within 10%)
time curl -s https://api.example.com/endpoint > /dev/null
# real    0m0.160s  # OK: within 10%
```

---

## Fix-Type Specific Verification

### SQL Injection → Parameterized Query

**Verify:**
1. Same data returned for valid queries
2. Invalid input properly rejected
3. No SQL errors exposed

```bash
# Valid query returns same data
curl "api/users/1" | jq .name
# Should return same name as before

# SQL injection attempt fails safely
curl "api/users/1;DROP TABLE users"
# Should return 400 or 404, not execute
```

### XSS → Output Encoding

**Verify:**
1. Normal text displays correctly
2. HTML entities are escaped
3. No visual change for legitimate content

```bash
# Submit test content
curl -X POST api/comments -d '{"text": "Hello <script>alert(1)</script>"}'

# Retrieve and verify encoded
curl api/comments/1
# Should show: "Hello &lt;script&gt;alert(1)&lt;/script&gt;"
# NOT: "Hello <script>alert(1)</script>"
```

### Auth/JWT Hardening

**Verify:**
1. Valid tokens still work
2. Invalid tokens rejected
3. Login flow unchanged

```bash
# Valid token accepted
curl -H "Authorization: Bearer $VALID_TOKEN" api/protected
# Should return 200

# Tampered token rejected
curl -H "Authorization: Bearer $TAMPERED_TOKEN" api/protected
# Should return 401
```

### Rate Limiting

**Verify:**
1. Normal use unaffected
2. Abuse triggers limit
3. Rate limit message matches spec

```bash
# Single request works
curl api/login -d '{"user":"test","pass":"test"}'
# Should work normally

# Rapid requests trigger limit
for i in {1..10}; do
  curl -s -w "%{http_code}\n" api/login -d '{"user":"test","pass":"wrong"}'
done
# Later requests should return 429
```

### Security Headers

**Verify:**
1. Headers present in response
2. No functional change
3. Page still loads correctly

```bash
# Check headers present
curl -sI https://example.com | grep -E "X-Frame-Options|X-Content-Type|Strict-Transport"
# Should show all expected headers

# Verify page still functions (visual check or automated)
# No JavaScript errors in console
# No blocked resources
```

### Error Handler Hardening

**Verify:**
1. User sees generic error
2. Internal logs contain details
3. Status codes unchanged

```bash
# Trigger an error
curl api/users/invalid-id

# User response (should be generic)
# {"error": "Internal server error"}

# Server logs (should have details)
# grep "invalid-id" /var/log/app.log
# Should show full stack trace
```

---

## Automated Verification Script

```bash
#!/bin/bash
# verify-fix.sh - Run after applying security fix

set -e

echo "=== Pre-flight checks ==="
git diff --stat

echo ""
echo "=== Running test suite ==="
npm test || { echo "FAIL: Tests failed"; exit 1; }

echo ""
echo "=== Checking API responses ==="
RESPONSE=$(curl -s http://localhost:3000/api/health)
if [[ "$RESPONSE" != *"ok"* ]]; then
  echo "FAIL: Health check failed"
  exit 1
fi

echo ""
echo "=== Checking security headers ==="
HEADERS=$(curl -sI http://localhost:3000)
for header in "X-Content-Type-Options" "X-Frame-Options"; do
  if [[ "$HEADERS" != *"$header"* ]]; then
    echo "WARN: Missing header $header"
  fi
done

echo ""
echo "=== Performance check ==="
START=$(date +%s%N)
curl -s http://localhost:3000/api/users > /dev/null
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))
echo "Response time: ${DURATION}ms"
if [ $DURATION -gt 500 ]; then
  echo "WARN: Response time > 500ms"
fi

echo ""
echo "=== All checks passed ==="
```

---

## Regression Test Patterns

### For Each Fix Type, Add Test:

#### Parameterized Query Test
```javascript
describe('SQL Injection Prevention', () => {
  it('should reject SQL injection in user lookup', async () => {
    const malicious = "1; DROP TABLE users;--";
    const res = await request(app).get(`/api/users/${malicious}`);
    expect(res.status).toBe(400);
    // Verify table still exists
    const users = await User.count();
    expect(users).toBeGreaterThan(0);
  });
});
```

#### XSS Prevention Test
```javascript
describe('XSS Prevention', () => {
  it('should escape HTML in user content', async () => {
    await Comment.create({ text: '<script>alert(1)</script>' });
    const res = await request(app).get('/api/comments');
    expect(res.text).not.toContain('<script>');
    expect(res.text).toContain('&lt;script&gt;');
  });
});
```

#### Rate Limit Test
```javascript
describe('Rate Limiting', () => {
  it('should limit login attempts', async () => {
    const attempts = 10;
    let rateLimited = false;
    for (let i = 0; i < attempts; i++) {
      const res = await request(app)
        .post('/api/login')
        .send({ email: 'test@test.com', password: 'wrong' });
      if (res.status === 429) {
        rateLimited = true;
        break;
      }
    }
    expect(rateLimited).toBe(true);
  });
});
```

---

## Rollback Verification

If fix causes issues, verify clean rollback:

```bash
# Revert the fix
git revert HEAD --no-edit

# Re-run tests
npm test

# Verify original behavior restored
curl api/endpoint | diff - baseline_response.json

# Should show zero differences
```

---

## Checklist Template

Use this checklist for each fix:

```markdown
## Fix Verification: [Finding ID]

### Pre-Fix
- [ ] Captured baseline API responses
- [ ] Captured baseline test output
- [ ] Documented expected behavior

### Post-Fix
- [ ] All existing tests pass
- [ ] API responses unchanged (except expected)
- [ ] No frontend files modified (if backend fix)
- [ ] Performance within 10% of baseline
- [ ] Security issue confirmed resolved
- [ ] Regression test added

### Sign-off
- [ ] Developer verified
- [ ] Ready for code review
```
