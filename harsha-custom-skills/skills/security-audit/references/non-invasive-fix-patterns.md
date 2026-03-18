# Non-Invasive Fix Patterns

This document provides comprehensive patterns for fixing security vulnerabilities without breaking existing functionality. Every pattern maintains the 10-point non-invasive checklist.

## The 10-Point Non-Invasive Checklist

Before applying ANY fix, verify:

| # | Check | Verification |
|---|-------|--------------|
| 1 | Zero UI/UX changes | No visual modifications |
| 2 | Identical outputs | Same input → same output |
| 3 | User flows unchanged | No new/removed steps |
| 4 | API contracts unchanged | Same schemas, status codes |
| 5 | No performance regression | Response times within 10% |
| 6 | Error messages unchanged | Same user-facing errors |
| 7 | Config additive-only | New with safe defaults |
| 8 | No new runtime deps | Stdlib or existing libs |
| 9 | Minimal diff | Smallest change possible |
| 10 | Trivially reversible | Single git revert |

---

## Pattern 1: Parameterized Queries (SQL Injection)

**Why Non-Invasive:** Query returns identical results; only execution method changes.

### JavaScript (mysql2/pg)
```javascript
// BEFORE (vulnerable)
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
connection.query(query);

// AFTER (safe)
const query = 'SELECT * FROM users WHERE id = ?';
connection.query(query, [req.params.id]);
```

### Python (psycopg2/SQLAlchemy)
```python
# BEFORE (vulnerable)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# AFTER (safe)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Java (JDBC)
```java
// BEFORE (vulnerable)
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);

// AFTER (safe)
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
stmt.setInt(1, userId);
ResultSet rs = stmt.executeQuery();
```

### Go (database/sql)
```go
// BEFORE (vulnerable)
db.Query(fmt.Sprintf("SELECT * FROM users WHERE id = %s", userId))

// AFTER (safe)
db.Query("SELECT * FROM users WHERE id = $1", userId)
```

**Checklist Verification:**
- ✅ Same data returned
- ✅ Same response format
- ✅ No UI changes
- ✅ No new dependencies (uses same driver)

---

## Pattern 2: Output Encoding Wrappers (XSS)

**Why Non-Invasive:** Same text displays to user; HTML entities are rendered identically by browsers.

### JavaScript (DOM)
```javascript
// BEFORE (vulnerable)
element.innerHTML = userInput;

// AFTER (safe) - textContent
element.textContent = userInput;

// AFTER (safe) - with HTML structure needed
const text = document.createTextNode(userInput);
element.appendChild(text);
```

### Template Engines
```html
<!-- EJS: BEFORE (vulnerable) -->
<%- userInput %>

<!-- EJS: AFTER (safe) -->
<%= userInput %>
```

```html
<!-- Jinja2: BEFORE (vulnerable) -->
{{ user_content|safe }}

<!-- Jinja2: AFTER (safe) -->
{{ user_content }}
```

### React (when HTML needed)
```jsx
// BEFORE (vulnerable)
<div dangerouslySetInnerHTML={{__html: userContent}} />

// AFTER (safe) - using existing DOMPurify
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userContent)}} />
```

**Checklist Verification:**
- ✅ Encoded text displays identically to user
- ✅ No visual difference
- ✅ No new dependencies (use existing sanitizer or native encoding)

---

## Pattern 3: Security Headers Addition (Config)

**Why Non-Invasive:** Headers don't affect response body or UI rendering.

### Express.js (Manual)
```javascript
// Add to middleware chain
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});
```

### Express.js (Helmet - if already in deps)
```javascript
const helmet = require('helmet');
app.use(helmet());
```

### Django
```python
# settings.py - add these lines
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
```

### Nginx
```nginx
# Add to server block
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

**Checklist Verification:**
- ✅ Response body unchanged
- ✅ No UI changes
- ✅ Additive config only
- ✅ No performance impact

---

## Pattern 4: CSRF Middleware Addition

**Why Non-Invasive:** Backend-only change; forms work same way.

### Express.js (csurf - if in deps)
```javascript
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

// Apply to routes that need it
app.post('/api/sensitive', csrfProtection, handler);

// Provide token to forms (add to existing render)
app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});
```

### Django (ensure not disabled)
```python
# Remove csrf_exempt if present
# @csrf_exempt  <- DELETE THIS LINE
def my_view(request):
    ...
```

**Checklist Verification:**
- ✅ Forms submit same way (with existing token field)
- ✅ No new UI elements required
- ✅ Existing AJAX requests need X-CSRF-Token header (usually already there)

---

## Pattern 5: JWT Configuration Hardening

**Why Non-Invasive:** Token validation becomes stricter but valid tokens still work.

### Algorithm Restriction
```javascript
// BEFORE (allows algorithm:none attack)
jwt.verify(token, secret, { algorithms: ['HS256', 'none'] });

// AFTER (only allow expected algorithm)
jwt.verify(token, secret, { algorithms: ['HS256'] });
```

### Add Expiry (Requires Review)
```javascript
// BEFORE (no expiry)
jwt.sign(payload, secret);

// AFTER (with expiry)
jwt.sign(payload, secret, { expiresIn: '1h' });
```
⚠️ **Requires Review:** Existing tokens without `exp` will be rejected. Plan token rotation.

### Secret from Environment
```javascript
// BEFORE (hardcoded)
const JWT_SECRET = 'hardcoded-secret';

// AFTER (environment)
const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) throw new Error('JWT_SECRET required');
```

---

## Pattern 6: Input Validation Wrappers

**Why Non-Invasive:** Valid inputs work same; invalid inputs already failed in some way.

### Wrapper Function Pattern
```javascript
// Create reusable validator
const validateInt = (value, { min = -Infinity, max = Infinity } = {}) => {
  const num = parseInt(value, 10);
  if (isNaN(num) || num < min || num > max) {
    return null;
  }
  return num;
};

// Use in handlers
app.get('/api/items/:id', (req, res) => {
  const id = validateInt(req.params.id, { min: 1 });
  if (id === null) {
    return res.status(400).json({ error: 'Invalid ID' });
  }
  // ... proceed with validated id
});
```

### Schema Validation (Joi - if in deps)
```javascript
const schema = Joi.object({
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(0).max(150)
});

const validateBody = (schema) => (req, res, next) => {
  const { error, value } = schema.validate(req.body);
  if (error) return res.status(400).json({ error: error.message });
  req.body = value;
  next();
};

app.post('/users', validateBody(schema), createUser);
```

---

## Pattern 7: Error Handler Hardening

**Why Non-Invasive:** Same generic error shown to user; only internal logging changes.

```javascript
// Global error handler
app.use((err, req, res, next) => {
  // Log full error internally
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    path: req.path,
    user: req.user?.id
  });

  // Return generic message to user
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    error: statusCode >= 500 ? 'Internal server error' : err.message
  });
});
```

**Checklist Verification:**
- ✅ User sees same generic error (or more generic)
- ✅ Internal logging preserved for debugging
- ✅ No UI changes

---

## Pattern 8: Rate Limiting Addition

**Why Non-Invasive:** Normal users unaffected; only abusers see 429.

```javascript
// express-rate-limit (if in deps)
const rateLimit = require('express-rate-limit');

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: { error: 'Too many attempts, try again later' }
});

// Apply to auth routes
app.post('/login', authLimiter, loginHandler);
app.post('/forgot-password', authLimiter, forgotHandler);
```

**Checklist Verification:**
- ✅ Normal users never hit limit
- ✅ Same response for successful requests
- ✅ New 429 response only for abuse

---

## Pattern 9: Atomic Database Operations

**Why Non-Invasive:** Same data outcome; race conditions prevented.

### MongoDB Atomic Update
```javascript
// BEFORE (TOCTOU vulnerable)
const user = await User.findById(id);
if (user.balance < amount) throw new Error('Insufficient');
user.balance -= amount;
await user.save();

// AFTER (atomic)
const result = await User.findOneAndUpdate(
  { _id: id, balance: { $gte: amount } },
  { $inc: { balance: -amount } },
  { new: true }
);
if (!result) throw new Error('Insufficient');
```

### PostgreSQL Transaction
```javascript
const client = await pool.connect();
try {
  await client.query('BEGIN');
  const { rows } = await client.query(
    'SELECT balance FROM accounts WHERE id = $1 FOR UPDATE',
    [id]
  );
  if (rows[0].balance < amount) {
    await client.query('ROLLBACK');
    throw new Error('Insufficient');
  }
  await client.query(
    'UPDATE accounts SET balance = balance - $1 WHERE id = $2',
    [amount, id]
  );
  await client.query('COMMIT');
} catch (e) {
  await client.query('ROLLBACK');
  throw e;
} finally {
  client.release();
}
```

---

## Pattern 10: Secret Extraction to Environment

**Why Non-Invasive:** Same secret value used; only source changes.

```javascript
// BEFORE
const API_KEY = 'sk-live-abc123xyz';

// AFTER
const API_KEY = process.env.API_KEY;
```

```python
# BEFORE
API_KEY = "sk-live-abc123xyz"

# AFTER
import os
API_KEY = os.environ.get("API_KEY")
```

**Also add to .gitignore:**
```
.env
.env.local
.env.*.local
```

**Create .env.example:**
```
API_KEY=your-api-key-here
```

---

## Fix Priority Order

Apply fixes in this order (safest to more complex):

1. **Config-only** - Headers, CSP, CORS (zero code change)
2. **Dependency bumps** - Semver-compatible only
3. **Validation wrappers** - Guard existing code
4. **Secret removal** - Move to environment
5. **Sanitization** - Parameterized queries, encoding
6. **Privilege separation** - Middleware guards
7. **Logging additions** - Non-observable audit trails
8. **Error hardening** - Same user message, better internal
9. **Atomic operations** - Transactions for race conditions
10. **Business logic** - Server-side validation

---

## Common Mistakes That Make Fixes Invasive

| Mistake | Why It's Invasive | Better Approach |
|---------|------------------|-----------------|
| Adding required fields | Changes API contract | Validate existing fields |
| Changing error message text | Breaks client error handling | Keep exact message |
| Adding frontend validation | Changes UI | Backend-only |
| Requiring new headers | Breaks existing clients | Make optional with fallback |
| Changing response structure | Breaks parsers | Add fields, don't remove |
| Increasing bcrypt cost 8→14 | 4x slower login | Incremental 8→10→12 |
| Major version dep upgrade | May break | Patch/minor only |
| Adding CAPTCHA | Changes UI flow | Rate limiting first |
