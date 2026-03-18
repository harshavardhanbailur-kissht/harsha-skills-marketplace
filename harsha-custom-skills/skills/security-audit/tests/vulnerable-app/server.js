/**
 * INTENTIONALLY VULNERABLE APPLICATION
 *
 * This file contains security vulnerabilities for testing the security audit skill.
 * DO NOT use this code in production. Each vulnerability is documented.
 */

const express = require('express');
const mysql = require('mysql');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

// =============================================================================
// VULNERABILITY: Hardcoded secrets (secrets-auditor)
// =============================================================================
const JWT_SECRET = 'super-secret-jwt-key-12345';
const API_KEY = 'sk-live-abcdef123456789';
const DB_PASSWORD = 'admin123';

// =============================================================================
// VULNERABILITY: Weak cryptography (crypto-data-auditor)
// =============================================================================
function hashPassword(password) {
  // VULN: Using MD5 for password hashing
  return crypto.createHash('md5').update(password).digest('hex');
}

function generateToken() {
  // VULN: Using Math.random for security tokens
  return Math.random().toString(36).substring(2);
}

// VULN: Using weak bcrypt rounds
const BCRYPT_ROUNDS = 4;

// =============================================================================
// VULNERABILITY: SQL Injection (injection-auditor)
// =============================================================================
const db = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: DB_PASSWORD,
  database: 'app'
});

app.get('/api/users', (req, res) => {
  const userId = req.query.id;
  // VULN: SQL injection via string concatenation
  const query = `SELECT * FROM users WHERE id = ${userId}`;
  db.query(query, (err, results) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(results);
  });
});

app.post('/api/search', (req, res) => {
  const { name } = req.body;
  // VULN: SQL injection via string interpolation
  const query = `SELECT * FROM products WHERE name LIKE '%${name}%'`;
  db.query(query, (err, results) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(results);
  });
});

// =============================================================================
// VULNERABILITY: Command Injection (injection-auditor)
// =============================================================================
app.get('/api/ping', (req, res) => {
  const host = req.query.host;
  // VULN: Command injection
  require('child_process').exec(`ping -c 1 ${host}`, (err, stdout) => {
    res.json({ output: stdout });
  });
});

// =============================================================================
// VULNERABILITY: XSS (xss-csrf-auditor)
// =============================================================================
app.get('/api/greet', (req, res) => {
  const name = req.query.name;
  // VULN: Reflected XSS - no output encoding
  res.send(`<h1>Hello, ${name}!</h1>`);
});

app.get('/api/preview', (req, res) => {
  const content = req.query.content;
  // VULN: innerHTML assignment from user input
  res.send(`
    <html>
    <body>
      <div id="preview"></div>
      <script>
        document.getElementById('preview').innerHTML = '${content}';
      </script>
    </body>
    </html>
  `);
});

// =============================================================================
// VULNERABILITY: CSRF (xss-csrf-auditor)
// =============================================================================
// VULN: No CSRF protection, state-changing GET request
app.get('/api/delete-account', (req, res) => {
  const userId = req.query.userId;
  // Deletes user account without CSRF token
  res.json({ message: `Account ${userId} deleted` });
});

// =============================================================================
// VULNERABILITY: IDOR (access-control-auditor)
// =============================================================================
app.get('/api/documents/:id', (req, res) => {
  const docId = req.params.id;
  // VULN: No ownership verification
  const query = `SELECT * FROM documents WHERE id = ?`;
  db.query(query, [docId], (err, results) => {
    res.json(results);
  });
});

app.get('/api/orders/:orderId', (req, res) => {
  // VULN: Sequential IDs without authorization check
  const orderId = req.params.orderId;
  res.json({ orderId, total: 99.99, items: [] });
});

// =============================================================================
// VULNERABILITY: Missing Auth (access-control-auditor)
// =============================================================================
// VULN: Admin route without authentication
app.get('/admin/users', (req, res) => {
  res.json({ users: ['admin', 'user1', 'user2'] });
});

app.delete('/admin/users/:id', (req, res) => {
  // VULN: No auth middleware
  res.json({ deleted: req.params.id });
});

// =============================================================================
// VULNERABILITY: JWT Issues (auth-session-auditor)
// =============================================================================
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  // VULN: JWT without expiration
  const token = jwt.sign({ username }, JWT_SECRET);
  res.json({ token });
});

app.get('/api/verify', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  try {
    // VULN: Allowing 'none' algorithm
    const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256', 'none'] });
    res.json({ user: decoded });
  } catch (e) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

// =============================================================================
// VULNERABILITY: Session Issues (auth-session-auditor)
// =============================================================================
app.use(require('express-session')({
  secret: 'keyboard cat',
  // VULN: Insecure session settings
  cookie: {
    httpOnly: false,
    secure: false,
    sameSite: 'none'
  }
}));

// =============================================================================
// VULNERABILITY: Path Traversal (input-output-auditor)
// =============================================================================
app.get('/api/files/:filename', (req, res) => {
  const filename = req.params.filename;
  // VULN: Path traversal - no validation
  const filePath = path.join('/var/app/uploads', filename);
  res.sendFile(filePath);
});

app.get('/api/read', (req, res) => {
  const file = req.query.file;
  // VULN: Direct file read from user input
  fs.readFile(file, 'utf8', (err, data) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ content: data });
  });
});

// =============================================================================
// VULNERABILITY: Unsafe Deserialization (input-output-auditor)
// =============================================================================
app.post('/api/config', (req, res) => {
  const yaml = require('js-yaml');
  // VULN: Unsafe YAML parsing (should use safeLoad)
  const config = yaml.load(req.body.config);
  res.json({ config });
});

// =============================================================================
// VULNERABILITY: Missing Rate Limiting (api-endpoint-auditor)
// =============================================================================
// VULN: No rate limiting on authentication endpoint
app.post('/api/auth/login', (req, res) => {
  // Brute force vulnerable
  res.json({ success: true });
});

// VULN: No body size limit
app.post('/api/upload', (req, res) => {
  res.json({ uploaded: true });
});

// =============================================================================
// VULNERABILITY: Mass Assignment (api-endpoint-auditor)
// =============================================================================
app.put('/api/users/:id', async (req, res) => {
  // VULN: Mass assignment - accepts all fields including 'role'
  const userData = req.body;
  // User could set { role: 'admin' }
  res.json({ updated: userData });
});

// =============================================================================
// VULNERABILITY: SSRF (api-endpoint-auditor)
// =============================================================================
const axios = require('axios');

app.post('/api/fetch-url', async (req, res) => {
  const { url } = req.body;
  // VULN: SSRF - fetching arbitrary URLs
  const response = await axios.get(url);
  res.json(response.data);
});

// =============================================================================
// VULNERABILITY: Error Disclosure (error-handling-auditor)
// =============================================================================
app.get('/api/error', (req, res) => {
  try {
    throw new Error('Something went wrong');
  } catch (err) {
    // VULN: Exposing stack trace to user
    res.status(500).json({
      error: err.message,
      stack: err.stack
    });
  }
});

// VULN: User enumeration via different error messages
app.post('/api/check-user', (req, res) => {
  const { username, password } = req.body;
  // Would leak user existence
  if (!findUser(username)) {
    return res.status(404).json({ error: 'User not found' });
  }
  if (!checkPassword(password)) {
    return res.status(401).json({ error: 'Wrong password' });
  }
  res.json({ success: true });
});

// =============================================================================
// VULNERABILITY: Race Condition (concurrency-auditor)
// =============================================================================
app.post('/api/withdraw', async (req, res) => {
  const { userId, amount } = req.body;
  // VULN: TOCTOU race condition
  const user = await getUser(userId);
  if (user.balance >= amount) {
    // Race window: another request could withdraw simultaneously
    user.balance -= amount;
    await saveUser(user);
    res.json({ newBalance: user.balance });
  } else {
    res.status(400).json({ error: 'Insufficient funds' });
  }
});

// =============================================================================
// VULNERABILITY: Sensitive Data in Logs (logging-monitoring-auditor)
// =============================================================================
app.post('/api/payment', (req, res) => {
  const { cardNumber, cvv, amount } = req.body;
  // VULN: Logging sensitive data
  console.log('Payment request:', { cardNumber, cvv, amount });
  console.log('Processing payment with card:', cardNumber);
  res.json({ success: true });
});

app.post('/api/signup', (req, res) => {
  const { email, password } = req.body;
  // VULN: Logging password
  console.log('New user signup:', { email, password });
  res.json({ created: true });
});

// =============================================================================
// VULNERABILITY: Business Logic Flaws (business-logic-auditor)
// =============================================================================
app.post('/api/checkout', (req, res) => {
  // VULN: Price from client - should look up from database
  const { items, total } = req.body;
  // Client could send total: 0.01 for expensive items
  processPayment(total);
  res.json({ success: true });
});

app.post('/api/apply-coupon', (req, res) => {
  const { couponCode, cartTotal } = req.body;
  // VULN: No validation of coupon usage limits or expiry
  const discount = getCouponDiscount(couponCode);
  res.json({ newTotal: cartTotal - discount });
});

// =============================================================================
// VULNERABILITY: Missing Security Headers (config-headers-auditor)
// =============================================================================
// VULN: No helmet, no security headers set
// No Content-Security-Policy
// No X-Frame-Options
// No X-Content-Type-Options

// =============================================================================
// VULNERABILITY: CORS Misconfiguration (config-headers-auditor)
// =============================================================================
const cors = require('cors');
app.use(cors({
  // VULN: Allow all origins with credentials
  origin: '*',
  credentials: true
}));

// =============================================================================
// Stub functions (not actual implementations)
// =============================================================================
function findUser(username) { return { username }; }
function checkPassword(password) { return true; }
function getUser(userId) { return Promise.resolve({ id: userId, balance: 1000 }); }
function saveUser(user) { return Promise.resolve(user); }
function processPayment(amount) { return true; }
function getCouponDiscount(code) { return 10; }

// =============================================================================
// Start server
// =============================================================================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Vulnerable app running on port ${PORT}`);
});

module.exports = app;
