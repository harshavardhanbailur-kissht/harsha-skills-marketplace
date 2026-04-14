# Security Bug Patterns & Fix Templates

> **Scope:** 10 CWE patterns detected by `scan_bugs.py -c security`. Each entry includes the detection pattern, why it matters, a safe fix template, and a regression test template.

---

## S-001: SQL Injection (CWE-89)

**Detection:** String concatenation or template literals in SQL queries with user input (`req.body`, `req.query`, `req.params`).

**Why it matters:** Allows attackers to execute arbitrary SQL, exfiltrate data, or drop tables.

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
const result = await db.query(`SELECT * FROM users WHERE id = '${req.params.id}'`);

// AFTER (parameterized query)
const result = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
```

**ORM equivalent (Prisma/Sequelize):**
```javascript
// Prisma — always use where clause, never raw SQL with user input
const user = await prisma.user.findUnique({ where: { id: parseInt(req.params.id) } });
```

**Regression test:**
```javascript
it('rejects SQL injection in user ID', async () => {
  const res = await request(app).get("/users/1' OR '1'='1");
  expect(res.status).toBe(400); // or 404, not 200 with all users
});
```

---

## S-002: Cross-Site Scripting / XSS (CWE-79)

**Detection:** `innerHTML`, `document.write()`, `dangerouslySetInnerHTML` with unsanitized user input.

**Why it matters:** Allows attackers to inject malicious scripts that run in other users' browsers, stealing sessions or data.

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
element.innerHTML = userInput;

// AFTER — use textContent for plain text
element.textContent = userInput;

// AFTER — use DOMPurify if HTML is required
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

**React-specific:**
```jsx
// BEFORE (vulnerable)
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// AFTER — sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
```

**Regression test:**
```javascript
it('sanitizes XSS payloads in user content', () => {
  const malicious = '<img src=x onerror=alert(1)>';
  const { container } = render(<Comment content={malicious} />);
  expect(container.querySelector('img[onerror]')).toBeNull();
});
```

---

## S-003: Hardcoded Credentials (CWE-798)

**Detection:** Strings matching API key, password, secret, or token patterns assigned in source code.

**Why it matters:** Credentials in source code get committed to version control and exposed to anyone with repo access.

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
const API_KEY = 'sk-abc123def456';
const dbPassword = 'supersecret';

// AFTER — use environment variables
const API_KEY = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;

// Validate at startup
if (!process.env.API_KEY) {
  throw new Error('API_KEY environment variable is required');
}
```

**Prevention:**
- Add `.env` to `.gitignore`
- Use a secrets manager (AWS Secrets Manager, Vault, Doppler)
- Run `git-secrets` or `trufflehog` in CI to catch leaks

**Regression test:**
```javascript
it('does not contain hardcoded secrets in source', () => {
  const source = fs.readFileSync('src/config.js', 'utf8');
  expect(source).not.toMatch(/['"]sk-[a-zA-Z0-9]{20,}['"]/);
  expect(source).not.toMatch(/password\s*=\s*['"][^'"]{4,}['"]/i);
});
```

---

## S-004: Path Traversal (CWE-22)

**Detection:** `req.params` or `req.query` values used directly in `fs.readFile()`, `path.join()`, or `path.resolve()` without sanitization.

**Why it matters:** Attackers can read arbitrary files on the server (`../../etc/passwd`).

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
const filePath = path.join(uploadDir, req.params.filename);
const data = fs.readFileSync(filePath);

// AFTER — resolve and validate prefix
const filePath = path.resolve(uploadDir, req.params.filename);
if (!filePath.startsWith(path.resolve(uploadDir))) {
  return res.status(403).send('Access denied');
}
const data = fs.readFileSync(filePath);
```

**Regression test:**
```javascript
it('blocks path traversal attempts', async () => {
  const res = await request(app).get('/files/../../etc/passwd');
  expect(res.status).toBe(403);
});
```

---

## S-005: Command Injection (CWE-78)

**Detection:** `child_process.exec()`, `execSync()`, or shell commands with user input concatenated.

**Why it matters:** Allows arbitrary command execution on the server.

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
const { exec } = require('child_process');
exec(`convert ${req.body.filename} output.png`);

// AFTER — use execFile with argument array (no shell interpolation)
const { execFile } = require('child_process');
execFile('convert', [req.body.filename, 'output.png'], (err, stdout) => {
  // handle result
});
```

**Additional defense:** Validate/whitelist input before passing to any process.

**Regression test:**
```javascript
it('prevents command injection via filename', async () => {
  const res = await request(app).post('/convert').send({
    filename: 'test.jpg; rm -rf /'
  });
  // Should reject or safely handle — not execute rm
  expect(res.status).toBe(400);
});
```

---

## S-006: Open Redirect (CWE-601)

**Detection:** `res.redirect()` with user-controlled URL from `req.query` or `req.body` without validation.

**Why it matters:** Attackers craft links that appear to come from your domain but redirect to phishing sites.

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
app.get('/redirect', (req, res) => {
  res.redirect(req.query.url);
});

// AFTER — whitelist allowed hosts
const ALLOWED_HOSTS = ['example.com', 'app.example.com'];

app.get('/redirect', (req, res) => {
  try {
    const url = new URL(req.query.url, `https://${req.hostname}`);
    if (!ALLOWED_HOSTS.includes(url.hostname)) {
      return res.status(400).send('Invalid redirect target');
    }
    res.redirect(url.toString());
  } catch {
    res.status(400).send('Invalid URL');
  }
});
```

**Regression test:**
```javascript
it('blocks open redirect to external domain', async () => {
  const res = await request(app).get('/redirect?url=https://evil.com');
  expect(res.status).toBe(400);
});

it('allows redirect to whitelisted domain', async () => {
  const res = await request(app).get('/redirect?url=https://app.example.com/dashboard');
  expect(res.status).toBe(302);
});
```

---

## S-007: Permissive CORS (CWE-942)

**Detection:** `Access-Control-Allow-Origin: *` in headers, `cors()` with no config (defaults to `origin: *`), or `cors({ origin: '*' })`.

**Why it matters:** Allows any website to make authenticated requests to your API, enabling data theft via cross-origin attacks.

**Safe Fix:**
```javascript
// BEFORE (vulnerable) — any of these patterns
res.setHeader('Access-Control-Allow-Origin', '*');
app.use(cors());  // defaults to origin: *
app.use(cors({ origin: '*' }));

// AFTER — explicit origin whitelist
const ALLOWED_ORIGINS = [
  'https://app.example.com',
  'https://staging.example.com',
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
}));
```

**Warning:** If `credentials: true`, the browser rejects `origin: '*'` anyway — but the server still exposes non-credentialed endpoints.

**Regression test:**
```javascript
it('rejects requests from unauthorized origins', async () => {
  const res = await request(app)
    .get('/api/data')
    .set('Origin', 'https://evil.com');
  expect(res.headers['access-control-allow-origin']).not.toBe('*');
  expect(res.headers['access-control-allow-origin']).not.toBe('https://evil.com');
});
```

---

## S-008: Prototype Pollution (CWE-1321)

**Detection:** Bracket notation assignment (`obj[key] = value`) with user input keys, or `Object.assign({}, userInput)` / `_.merge()` with unsanitized input.

**Why it matters:** Attackers inject `__proto__` or `constructor.prototype` properties to modify all objects in the application, potentially achieving RCE.

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
function setProperty(obj, key, value) {
  obj[key] = value;  // key from user input
}

// AFTER — block prototype keys
const FORBIDDEN_KEYS = ['__proto__', 'constructor', 'prototype'];

function setProperty(obj, key, value) {
  if (FORBIDDEN_KEYS.includes(key)) {
    throw new Error(`Forbidden property key: ${key}`);
  }
  obj[key] = value;
}

// AFTER — use Map instead of plain objects for user-keyed data
const userPrefs = new Map();
userPrefs.set(req.body.key, req.body.value);
```

**For deep merge:** Use a safe merge library or `structuredClone()`:
```javascript
// BEFORE (vulnerable)
const merged = _.merge({}, defaults, req.body);

// AFTER — use structuredClone to strip prototype chains
const sanitized = JSON.parse(JSON.stringify(req.body));
const merged = _.merge({}, defaults, sanitized);
```

**Regression test:**
```javascript
it('blocks __proto__ pollution', () => {
  const before = ({}).polluted;
  setProperty({}, '__proto__', { polluted: true });
  expect(({}).polluted).toBeUndefined();
});
```

---

## S-009: NoSQL Injection (CWE-943)

**Detection:** MongoDB query operators (`$gt`, `$ne`, `$regex`, `$where`) in user input passed to `find()`, `findOne()`, or `aggregate()`.

**Why it matters:** Attackers bypass authentication or extract data by injecting query operators (e.g., `{ password: { $ne: "" } }` matches all users).

**Safe Fix:**
```javascript
// BEFORE (vulnerable)
const user = await User.findOne({
  username: req.body.username,
  password: req.body.password  // attacker sends { "$ne": "" }
});

// AFTER — sanitize by enforcing string type
const { username, password } = req.body;
if (typeof username !== 'string' || typeof password !== 'string') {
  return res.status(400).send('Invalid input');
}
const user = await User.findOne({ username, password: await bcrypt.hash(password, salt) });

// AFTER (alternative) — use mongo-sanitize
const sanitize = require('mongo-sanitize');
const user = await User.findOne({
  username: sanitize(req.body.username),
  password: sanitize(req.body.password),
});
```

**Regression test:**
```javascript
it('blocks NoSQL operator injection in login', async () => {
  const res = await request(app).post('/login').send({
    username: 'admin',
    password: { '$ne': '' }
  });
  expect(res.status).toBe(400); // not 200 with admin session
});
```

---

## S-010: JWT Algorithm None Attack (CWE-347)

**Detection:** `jwt.verify()` without explicit `algorithms` parameter, or `algorithms: ['none']`.

**Why it matters:** Without pinning the algorithm, attackers can forge tokens with `"alg": "none"` (no signature) or switch from RS256 to HS256 (using the public key as HMAC secret).

**Safe Fix:**
```javascript
// BEFORE (vulnerable) — no algorithms parameter
const decoded = jwt.verify(token, secret);

// ALSO VULNERABLE — algorithm confusion (RS256 → HS256)
const decoded = jwt.verify(token, publicKey);

// AFTER — always pin the algorithm
const decoded = jwt.verify(token, secret, {
  algorithms: ['HS256'],  // pin to exactly one algorithm
});

// For RSA signatures
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256'],  // never allow HS256 with RSA keys
});
```

**Defense in depth:**
```javascript
// Reject tokens with 'none' algorithm before verification
const header = JSON.parse(Buffer.from(token.split('.')[0], 'base64url').toString());
if (header.alg === 'none' || header.alg === 'None') {
  throw new Error('Algorithm none is not permitted');
}
```

**Regression test:**
```javascript
it('rejects tokens with algorithm none', () => {
  // Craft a token with alg: none
  const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
  const payload = Buffer.from(JSON.stringify({ sub: 'admin' })).toString('base64url');
  const forgedToken = `${header}.${payload}.`;

  expect(() => {
    jwt.verify(forgedToken, secret, { algorithms: ['HS256'] });
  }).toThrow();
});

it('rejects RS256 tokens verified with HS256', () => {
  // This test ensures algorithm confusion is blocked
  const token = jwt.sign({ sub: 'admin' }, publicKey, { algorithm: 'HS256' });
  expect(() => {
    jwt.verify(token, publicKey, { algorithms: ['RS256'] });
  }).toThrow();
});
```

---

## Version Applicability

| Pattern | CWE | Frameworks | Min Version |
|---------|-----|-----------|-------------|
| S-001 SQL Injection | CWE-89 | Node.js (mysql, pg, sequelize) | All |
| S-002 XSS | CWE-79 | React, vanilla JS | All |
| S-003 Hardcoded Credentials | CWE-798 | All | All |
| S-004 Path Traversal | CWE-22 | Node.js (fs, path) | All |
| S-005 Command Injection | CWE-78 | Node.js (child_process) | All |
| S-006 Open Redirect | CWE-601 | Express, Next.js | All |
| S-007 Permissive CORS | CWE-942 | Express (cors middleware) | All |
| S-008 Prototype Pollution | CWE-1321 | Node.js, lodash < 4.17.12 | All |
| S-009 NoSQL Injection | CWE-943 | MongoDB (mongoose, native driver) | All |
| S-010 JWT Algorithm None | CWE-347 | jsonwebtoken | All |

---

## Quick Reference: Detection → Fix

| scan_bugs.py ID | This file section | Severity |
|----------------|-------------------|----------|
| `sqli` | S-001 | Critical |
| `xss` | S-002 | Critical |
| `hardcoded-secret` | S-003 | High |
| `path-traversal` | S-004 | Critical |
| `command-injection` | S-005 | Critical |
| `open-redirect` | S-006 | Medium |
| `permissive-cors` | S-007 | Medium |
| `prototype-pollution` | S-008 | High |
| `nosql-injection` | S-009 | Critical |
| `jwt-alg-none` | S-010 | Critical |
