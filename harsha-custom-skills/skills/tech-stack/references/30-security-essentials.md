# Security Essentials: Complete Tech-Stack Reference (2025-2026)

## Executive Summary (5-line TL;DR)
- OWASP Top 10 2025: Broken Access Control #1, Supply Chain Failures now in top 10 (new entry)
- Security headers (CSP, CORS, HSTS) are non-negotiable; use Helmet.js for Express/Fastify auto-configuration
- Rate limiting is mandatory for all public APIs: use token bucket algorithm, 100 req/min default for auth endpoints
- Passkeys replacing passwords with 70% adoption by end 2025; implement via SimpleWebAuthn library
- Always use parameterized queries (never string concat SQL), bcrypt/argon2 for password hashing, HttpOnly+Secure cookies

## Table of Contents

1. [OWASP Top 10 2025](#owasp-top-10-2025)
2. [Security Headers & Configuration](#security-headers--configuration)
3. [Rate Limiting](#rate-limiting)
4. [Web Application Firewall (WAF)](#web-application-firewall-waf)
5. [Authentication & Password Security](#authentication--password-security)
6. [Session Security](#session-security)
7. [CSRF Prevention](#csrf-prevention)
8. [Free Security Tools & Services](#free-security-tools--services)

---

## OWASP Top 10 2025

The OWASP Top 10:2025 reflects the evolving landscape of web security based on analysis of 175,000+ CVE records and feedback from security practitioners globally. This edition represents a fundamental shift toward identifying root causes rather than symptoms.

### A01: Broken Access Control (100% of applications tested affected)

**What It Is:**
Broken access control fails to enforce policies that users cannot act outside of their intended permissions. This includes IDOR (Insecure Direct Object References), directory traversal, and SSRF (Server-Side Request Forgery) vulnerabilities.

**Common CVEs:**
- CWE-200: Exposure of Sensitive Information to Unauthorized Actor
- CWE-201: Exposure of Sensitive Information Through Sent Data
- CWE-918: Server-Side Request Forgery (SSRF)
- CWE-352: Cross-Site Request Forgery (CSRF)

**Prevention Strategies:**
- Implement server-side authentication and authorization checks
- Enforce role-based access control (RBAC) with principle of least privilege
- Test for IDOR, directory traversal, and URL-based access flaws using DAST scanners
- Implement Access Control Lists (ACLs) with explicitly defined permissions
- Proper session management with secure tokens, timeouts, and termination handling

**Framework Support:**
- **Django**: Built-in permission and access control decorators
- **Spring Security**: Comprehensive authorization filters and role-based security
- **Ruby on Rails**: Pundit gem for declarative authorization
- **Next.js/Express**: Middleware-based auth systems (NextAuth.js, Passport.js)
- **ASP.NET Core**: Claims-based authorization and policy-based access control

---

### A02: Cryptographic Failures (Dropped from #2 to #4 in 2025)

**What It Is:**
Failures related to missing or weak cryptography, insufficient encryption strength, exposed cryptographic keys, and improper cryptographic function usage.

**Prevention Strategies:**

**Data Classification:**
- Classify and label data processed, stored, or transmitted
- Identify sensitive data per privacy laws and regulatory requirements
- Don't store sensitive data unnecessarily; use PII tokenization

**Encryption Implementation:**
- Always use authenticated encryption (AEAD), not just encryption
- Encrypt all data in transit at transport layer (TLS 1.2+)
- Use TLS 1.3 for new deployments

**Key Management:**
- Generate keys cryptographically randomly
- Store sensitive keys in memory as byte arrays or HSM (Hardware Security Module)
- Rotate keys regularly (every 30-90 days)
- Use key versioning for zero-downtime rotation

**Cryptographic Algorithms:**
- **Avoid:** MD5, SHA1, CBC mode, PKCS#1 v1.5
- **Use:** SHA-256+, ChaCha20-Poly1305, AES-GCM
- **Password Hashing:** Argon2id (gold standard), bcrypt, or scrypt

**Framework Support:**
- **Node.js:** crypto module (built-in), libsodium (TweetNaCl.js)
- **Python:** cryptography library, PyCryptodome
- **Java:** Bouncy Castle, Java Security API
- **Go:** crypto package, crypto/aes, crypto/rand
- **Rust:** RustCrypto libraries, sodiumoxide

---

### A03: Injection (Dropped from #3 to #5 in 2025)

**Types:**
- SQL Injection
- NoSQL Injection
- OS Command Injection
- LDAP/XPath Injection
- Expression Language Injection

**Prevention:**
- Use parameterized queries and prepared statements
- Use ORM frameworks (SQLAlchemy, TypeORM, Sequelize)
- Input validation with strict whitelisting
- Output encoding based on context
- Least privilege database accounts

**Framework Support:**
- Most modern ORMs provide built-in parameterized query protection
- Express.js with libraries like `sqlstring`, `mysql2/promise`
- Django ORM with parameterized queries by default

---

### A04: Insecure Design (New in 2025)

**What It Is:**
Missing or ineffective control design, including threat modeling failures, missing security requirements, and unsafe design patterns.

**Prevention:**
- Implement threat modeling during design phase
- Establish security requirements in planning
- Design patterns with security in mind
- Security architecture reviews
- Secure defaults

---

### A05: Security Misconfiguration (Jumped from #5 to #2 in 2025)

**Affects 3% of tested applications**

**Common Issues:**
- Default credentials on systems
- Unnecessary features enabled
- Outdated or unpatched systems
- Missing security headers
- Verbose error messages revealing system info
- Insecure default configurations

**Prevention:**
- Automated compliance scanning
- Hardened base images/configurations
- Minimal installation principle
- Infrastructure-as-Code (IaC) security
- Regular vulnerability scanning
- Security header enforcement (see Security Headers section)

---

### A06-A10: Other Critical Vulnerabilities

**A06: Vulnerable and Outdated Components**
- Regular dependency audits
- Software composition analysis (SCA) tools
- Automated patching
- Component inventory management

**A07: Authentication & Session Management Failures**
- MFA/2FA enforcement
- Secure session token management
- Password reset flow security
- Session timeout implementation

**A08: Cryptographic Failures (Data)**
- Sensitive data classification
- Encryption at rest and in transit
- Key management

**A09: Logging & Monitoring Failures**
- Comprehensive audit logging
- Security event detection
- Alerting on suspicious activities
- Log retention and protection

**A10: Mishandling of Exceptional Conditions**
- Proper error handling
- Fail-secure approaches
- Avoiding open security-relevant information disclosure

---

## Security Headers & Configuration

### Helmet.js Best Practices

Helmet is a middleware collection for securing Express and Node.js applications by setting various HTTP headers.

**Basic Setup:**
```javascript
const helmet = require('helmet');
const app = require('express')();

app.use(helmet()); // Default configuration
```

**Default Headers Set by Helmet:**
```
Content-Security-Policy: default-src 'self'; base-uri 'self'; font-src 'self' https: data:; form-action 'self'; frame-ancestors 'self'; img-src 'self' data:; object-src 'none'; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-Powered-By: (removed)
X-XSS-Protection: (removed - deprecated)
Strict-Transport-Security: max-age=15552000; includeSubDomains
```

### Content Security Policy (CSP) Configuration

**CSP is NOT enabled by default in Helmet** because it can break things like CDN file inclusion. You must explicitly enable it.

**Report-Only Mode (Recommended for Initial Implementation):**
```javascript
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"], // Evaluate and remove unsafe-inline
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'"],
  },
  reportOnly: true, // Use draft-8 report header
}));
```

**Nonce-Based Approach (Recommended for Production):**
```javascript
app.use((req, res, next) => {
  res.locals.cspNonce = crypto.randomBytes(16).toString('hex');
  next();
});

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: [(req, res) => `'nonce-${res.locals.cspNonce}'`],
    styleSrc: [(req, res) => `'nonce-${res.locals.cspNonce}'`],
  },
}));
```

**CSP Best Practices:**
- Use `report-only` mode first to identify blocked resources
- Whitelist only trusted domains (avoid blanket exclusions)
- Use nonces or hashes for inline scripts instead of `unsafe-inline`
- Monitor CSP violation reports
- Use CSP Evaluator (Google) to validate policies

### Essential Security Headers

| Header | Purpose | Recommended Value |
|--------|---------|-------------------|
| `Strict-Transport-Security` | Force HTTPS | `max-age=31536000; includeSubDomains; preload` |
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |
| `X-Frame-Options` | Prevent clickjacking | `DENY` (or `SAMEORIGIN`) |
| `Content-Security-Policy` | XSS prevention | Nonce-based or hash-based |
| `Referrer-Policy` | Control referrer info | `strict-no-referrer` or `no-referrer-when-downgrade` |
| `Permissions-Policy` | Feature restrictions | Restrict geolocation, camera, microphone, etc. |
| `X-Permitted-Cross-Domain-Policies` | Flash/PDF restrictions | `none` |

### CORS: Common Mistakes & Prevention

**Mistake #1: Wildcard with Credentials (DANGEROUS)**
```javascript
// WRONG - Browser will reject
res.header('Access-Control-Allow-Origin', '*');
res.header('Access-Control-Allow-Credentials', 'true');
```

**Mistake #2: Reflecting Origin Without Validation**
```javascript
// WRONG - Any domain can access
const origin = req.headers.origin;
res.header('Access-Control-Allow-Origin', origin);
```

**Correct Implementation:**
```javascript
const allowedOrigins = ['https://example.com', 'https://app.example.com'];
const origin = req.headers.origin;

if (allowedOrigins.includes(origin)) {
  res.header('Access-Control-Allow-Origin', origin);
  res.header('Access-Control-Allow-Credentials', 'true');
}
```

**Using Express CORS Middleware:**
```javascript
const cors = require('cors');

const corsOptions = {
  origin: ['https://example.com', 'https://app.example.com'],
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));
```

**Mistake #3: Forgetting Preflight Handling**
- All configured CORS endpoints must also handle OPTIONS requests
- Express CORS middleware handles this automatically

**Key CORS Principles:**
- Never use wildcard (`*`) with credentials
- Whitelist specific origins
- Explicitly define allowed methods and headers
- Validate origin headers server-side
- Use CORS for public APIs; prefer same-origin for internal resources

---

## Rate Limiting

Rate limiting protects APIs from abuse, brute-force attacks, and DoS attacks by controlling request frequency.

### Rate Limiting Algorithms

**1. Fixed Window Counter:**
- Simple but allows burst attacks at window boundaries
- Example: 100 requests per minute

**2. Sliding Window Log:**
- Most accurate but memory-intensive
- Stores all request timestamps
- Prevents boundary-based attacks

**3. Sliding Window Counter:**
- Hybrid approach, memory-efficient
- Uses counter + decay with calculation
- Good balance of accuracy and performance

**4. Token Bucket:**
- Allows controlled bursts
- Tokens replenish at fixed rate
- Tokens consumed per request
- Ideal for variable rate scenarios

**5. Leaky Bucket:**
- Requests queued and processed at fixed rate
- Simple and fair
- Better for consistent throughput

### express-rate-limit (Node.js/Express)

**Basic Configuration:**
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true, // Return rate limit info in RateLimit-* headers
  legacyHeaders: false, // Disable X-RateLimit-* headers
  handler: (req, res) => {
    res.status(429).json({ error: 'Too many requests' });
  },
  skip: (req) => req.user?.isPremium // Skip rate limiting for premium users
});

app.use(limiter);
```

**Storage Options:**
- **Default (Memory):** For development only, doesn't work in clustered setups
- **Redis:** Best for production with multiple instances
- **Memcached:** Alternative distributed cache
- **MongoDB:** Persistent storage option

**Redis Implementation:**
```javascript
const RedisStore = require('rate-limit-redis');
const redis = require('redis');
const client = redis.createClient();

const limiter = rateLimit({
  store: new RedisStore({
    client: client,
    prefix: 'rl:' // Rate limit prefix
  }),
  windowMs: 15 * 60 * 1000,
  max: 100
});
```

**User-Based Rate Limiting:**
```javascript
const limiter = rateLimit({
  keyGenerator: (req, res) => {
    // Rate limit by user ID instead of IP
    return req.user?.id || req.ip;
  },
  windowMs: 15 * 60 * 1000,
  max: 1000 // Higher limit for authenticated users
});
```

### Upstash Rate Limiting

Serverless-first rate limiting service with Redis backend.

**Features:**
- Designed for serverless environments (Vercel, Cloudflare Workers, Netlify)
- Multiple rate limiting algorithms
- Regional distribution for low latency
- Rate limit analytics dashboard
- Free tier: 10,000 requests/day

**Implementation:**
```javascript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(100, '1 h'), // 100 requests per hour
  analytics: true, // Optional analytics
  prefix: '@upstash/ratelimit',
});

export default async function handler(req, res) {
  const identifier = req.ip; // or req.user?.id
  const result = await ratelimit.limit(identifier);

  if (!result.success) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      reset: new Date(result.resetInMs),
    });
  }

  // Process request
  res.json({ success: true });
}
```

**Algorithms:**
- `slidingWindow(max, window)` - Smooth rate limiting
- `tokenBucket(refillRate, capacity)` - Burst tolerance
- `fixedWindow(max, window)` - Simple counter

### @hono/rate-limiter (Hono Framework)

Rate limiting middleware for Hono web framework.

```javascript
import { Hono } from 'hono';
import { rateLimiter } from '@hono/rate-limiter';

const app = new Hono();

app.use('*', rateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  limit: 100, // Max requests per window
  keyGenerator: (c) => c.req.header('cf-connecting-ip') || 'anonymous',
  handler: (c) => c.json({ error: 'Rate limit exceeded' }, 429),
  skip: (c) => c.req.path === '/health', // Skip health checks
}));

app.get('/api/data', (c) => c.json({ data: 'example' }));
```

### Cloudflare Rate Limiting

Built-in rate limiting available on all Cloudflare plans.

**Free Tier:**
- Access to rate limiting rules
- Configurable based on request properties
- Integration with Cloudflare WAF
- Recommended rules: 50-100 requests per minute for APIs

---

## Web Application Firewall (WAF)

### Cloudflare WAF

**Free Tier Capabilities (2025-2026):**
- **Managed Ruleset:** Cloudflare Free Managed Ruleset (subset of full ruleset)
- **Protections:** High-profile vulnerabilities (Shellshock, Log4J, etc.)
- **Custom Rules:** Ability to create firewall rules with sophisticated filtering
- **Dashboard Access:** Security Events dashboard
- **Request Body Analysis:** 1 MB limit for free tier

**Limitations:**
- No access to full Cloudflare Managed Ruleset
- No OWASP Core Ruleset
- No Leaked Credential Check
- Requires upgrade to PRO for advanced features

**Features Available on Free Plan:**
- Web Application Firewall (WAF) interface
- Rule creation and customization
- Traffic filtering based on:
  - IP address
  - User agent
  - Country
  - Request URI
  - HTTP method
  - Query string

**Activation (Free):**
```
1. Add domain to Cloudflare
2. Login to dashboard
3. Go to Security > WAF
4. Enable Free Managed Ruleset (default)
5. Create custom rules as needed
```

**Example Custom Rule:**
- Block requests from specific countries
- Allow/Block by IP range
- Rate limiting integration
- DDoS mitigation

### AWS WAF

**Pricing Structure (2025-2026):**
- **Web ACL:** $5.00/month (prorated hourly)
- **Rules:** $1.00/month per rule (prorated hourly)
- **Requests:** $0.60 per million inspected requests
- **Rule Groups:** $1.00/month (prorated hourly)

**Key Features:**
- Standard rule actions (Allow, Block, Count)
- Bot Control: 10M free requests/month (Common), 1M free/month (Targeted)
- Account Takeover Prevention
- Account Creation Fraud Prevention
- Layer 7 DDoS protection
- IP reputation lists
- Managed rules

**Recent Changes (October 2024):**
- CloudFront no longer charges for WAF-blocked requests
- AWS WAF still charges for evaluating blocked requests

**New Flat-Rate Pricing (2025):**
- **Free:** $0/month (includes CloudFront, WAF, DDoS, Route 53, 50GB S3)
- **Pro:** $15/month
- **Business:** $200/month
- **Premium:** $1,000/month

### WAF Best Practices

**Configuration:**
1. Start in monitoring mode (Log only, don't block)
2. Analyze logs for false positives
3. Gradually enable rules based on threat model
4. Implement rate limiting rules
5. Use IP reputation lists
6. Enable bot detection

**Testing:**
- Use tools like OWASP ZAP or Burp Suite
- Test for false positive/negatives
- Monitor legitimate traffic for impacts
- Regular rule updates

---

## Authentication & Password Security

### Password Hashing: Argon2 vs Bcrypt

**Argon2 (Gold Standard in 2025)**

Winner of Password Hashing Competition (2015), specifically designed to resist GPU/ASIC/side-channel attacks.

**OWASP 2025 Recommendations:**
```
Argon2id Configuration:
- Memory: 19 MiB (19,456 KB) minimum
- Iterations: 2
- Parallelism: 1
- OR
- Memory: 46 MiB (47,104 KB)
- Iterations: 1
- Parallelism: 1

Target Hash Time: 200-500ms for interactive authentication
```

**Implementation (Node.js):**
```javascript
const argon2 = require('argon2');

// Hash password
const hashedPassword = await argon2.hash(password, {
  type: argon2.argon2id,
  memoryCost: 19456, // 19 MiB
  timeCost: 2,
  parallelism: 1
});

// Verify password
const isPasswordValid = await argon2.verify(hashedPassword, password);
```

**Bcrypt (Still Safe in 2025)**

Widely used, proven secure with cost factor 12+. Document migration timeline to Argon2.

**Configuration:**
```javascript
const bcrypt = require('bcrypt');

// Hash with cost factor 12 (minimum)
const hashedPassword = await bcrypt.hash(password, 12);

// Verify
const isPasswordValid = await bcrypt.compare(password, hashedPassword);
```

**Cost Factor Recommendations:**
- **Cost 10:** < 10ms hash time (legacy)
- **Cost 12:** ~200ms hash time (recommended minimum)
- **Cost 14:** ~1 second hash time (for background jobs)

### Password Migration Strategy

When transitioning from bcrypt to Argon2:
```javascript
async function verifyPassword(plaintext, storedHash) {
  // Try Argon2 first (new standard)
  try {
    if (storedHash.startsWith('$argon2')) {
      return await argon2.verify(storedHash, plaintext);
    }
  } catch (err) {
    // Fall back to bcrypt
  }

  // Check with bcrypt (legacy)
  const isValid = await bcrypt.compare(plaintext, storedHash);

  // Re-hash with Argon2 on successful login
  if (isValid) {
    const newHash = await argon2.hash(plaintext);
    // Update database with new hash
  }

  return isValid;
}
```

### Timing Considerations

- **Too Fast:** Vulnerable to brute force attacks
- **Too Slow:** Creates DoS vulnerability and poor UX
- **Target:** 200-500ms for interactive authentication

### Password Storage Best Practices

- **Never store plaintext passwords**
- **Use cryptographically random salts** (not secret, can be stored with hash)
- **Use strong salt length:** 32+ bits recommended
- **Never reuse salts** across password hashes
- **Hash during registration AND on password change**

---

### JWT Security Best Practices

**Key Vulnerabilities to Avoid:**

1. **Algorithm Bypass:**
   - Never allow algorithm negotiation from claims
   - Whitelist algorithms in application configuration
   - Avoid HS256 (HMAC) with weak secrets

2. **Key Management:**
   - Minimum 256 bits of entropy (32 bytes)
   - Rotate keys regularly (30-90 days)
   - Implement zero-downtime key rotation with overlapping validity

3. **Token Validation:**
   - Always validate signature using server-side keys
   - Validate claims: `iss` (issuer), `aud` (audience), `exp` (expiration), `nbf` (not-before)
   - Check token freshness with `jti` (JWT ID) for revocation

4. **Token Lifetime:**
   - Keep access tokens short-lived (5-15 minutes)
   - Use refresh tokens for long-lived sessions
   - Implement token revocation for logout

**Recommended Algorithms (2025):**
- **EdDSA (Newest):** Quantum-resistant, smallest signature size
- **ES256 (ECDSA P-256):** Strong and efficient
- **RS256 / PS256:** For RSA scenarios (larger keys needed)
- **Avoid:** HS256 with short secrets, symmetric HMAC for multi-service

**Token Storage (Web Applications):**
```javascript
// BEST PRACTICE: Secure & HttpOnly cookie
res.cookie('accessToken', token, {
  httpOnly: true,
  secure: true, // HTTPS only
  sameSite: 'strict',
  maxAge: 15 * 60 * 1000 // 15 minutes
});

// Refresh token (also HttpOnly)
res.cookie('refreshToken', refreshToken, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
});
```

**JWT Verification:**
```javascript
import jwt from 'jsonwebtoken';

const publicKey = fs.readFileSync('public.key', 'utf-8');

function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, publicKey, {
      algorithms: ['ES256', 'RS256'], // Whitelist algorithms
      issuer: 'https://auth.example.com',
      audience: 'my-app',
      clockTolerance: 5 // 5 second clock skew tolerance
    });

    return decoded;
  } catch (err) {
    throw new Error('Invalid token');
  }
}
```

**2025 CVE Concerns:**
- Kid parameter injection in JWKS endpoints
- JKU/X5U URI manipulation (attackers hosting malicious keys)
- Insufficient key expiration validation

---

### OAuth 2.0 Security Considerations

**Critical Vulnerabilities:**

1. **Redirect URI Manipulation:**
   - Always validate redirect_uri against whitelist
   - Never accept client-provided URIs without validation

2. **PKCE (Proof Key for Code Exchange) - REQUIRED:**
   - Mandatory for public clients (SPAs, mobile apps)
   - Prevents authorization code interception attacks
   - Code_verifier must be unpredictable

3. **Implicit Grant (DEPRECATED):**
   - No longer recommended in OAuth 2.1
   - Vulnerable to access token leakage
   - Use Authorization Code with PKCE instead

**2025 Best Practices (RFC 9700):**

```javascript
// OAuth 2.0 with PKCE flow (Correct)
const codeVerifier = generateRandomString(128); // 128 characters
const codeChallenge = base64url(sha256(codeVerifier));

// Authorization request
const authUrl = `https://auth.example.com/authorize?
  client_id=YOUR_CLIENT_ID
  response_type=code
  redirect_uri=https://yourapp.com/callback
  code_challenge=${codeChallenge}
  code_challenge_method=S256`;

// Token request (with code_verifier)
const tokenResponse = await fetch('https://auth.example.com/token', {
  method: 'POST',
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authCode,
    code_verifier: codeVerifier,
    client_id: 'YOUR_CLIENT_ID',
    client_secret: 'YOUR_CLIENT_SECRET' // For confidential clients only
  })
});
```

**Implementation Guidelines:**
- Use well-reviewed libraries (Passport.js, node-oauth2-server)
- Avoid custom OAuth implementations
- Train developers on OAuth vulnerabilities
- Implement PKCE downgrade attack mitigation
- Rotate client secrets regularly
- Monitor for suspicious token usage patterns

---

## Session Security

### HttpOnly & Secure Cookies

**Must-Have Attributes:**

```javascript
// CORRECT: Secure session cookie configuration
res.cookie('sessionId', token, {
  httpOnly: true,      // Prevents JavaScript access (blocks XSS token theft)
  secure: true,        // HTTPS only (prevents MITM)
  sameSite: 'strict',  // CSRF protection
  domain: '.example.com', // Set explicitly
  path: '/',           // Restrict to needed paths
  maxAge: 30 * 60 * 1000 // 30 minutes
});
```

**Attribute Purposes:**

| Attribute | Purpose | Value |
|-----------|---------|-------|
| `httpOnly` | Block JavaScript access | `true` |
| `secure` | HTTPS only | `true` |
| `sameSite` | CSRF protection | `strict` or `lax` |
| `maxAge` | Session lifetime | 15-30 minutes ideal |
| `path` | URL scope | `/` or specific path |
| `domain` | Domain scope | Explicit domain only |

**Cookie Prefix (Additional Security):**
```javascript
res.cookie('__Secure-sessionId', token, {
  // Browser ensures this cookie:
  // - Is only sent over HTTPS
  // - Cannot be overwritten by non-HTTPS sources
  secure: true,
  httpOnly: true,
  sameSite: 'strict'
});
```

### SameSite Values

**Strict (Recommended):**
- Cookie sent only in same-site requests
- Maximum CSRF protection
- Impacts some legitimate workflows

**Lax (Default in modern browsers):**
- Cookie sent in same-site and top-level navigation
- Balance between security and usability
- Protects against most CSRF attacks

**None (Legacy):**
- Cookie sent in all contexts
- Requires `Secure` attribute
- Only use if third-party context is necessary

### Session Timeout & Rotation

**Idle Timeout:**
```javascript
const SESSION_IDLE_TIMEOUT = 30 * 60 * 1000; // 30 minutes

app.use((req, res, next) => {
  const lastActivity = req.session?.lastActivity;
  const now = Date.now();

  if (lastActivity && (now - lastActivity) > SESSION_IDLE_TIMEOUT) {
    req.session.destroy((err) => {
      if (err) return next(err);
      res.status(401).json({ error: 'Session expired' });
    });
  } else {
    req.session.lastActivity = now;
    next();
  }
});
```

**Absolute Session Lifetime:**
```javascript
const SESSION_MAX_LIFETIME = 24 * 60 * 60 * 1000; // 24 hours

if (req.session?.createdAt &&
    (Date.now() - req.session.createdAt) > SESSION_MAX_LIFETIME) {
  req.session.destroy();
  return res.status(401).json({ error: 'Session expired' });
}
```

**Session Regeneration (After Login):**
```javascript
// Prevent session fixation attacks
app.post('/login', (req, res) => {
  // Verify credentials...

  req.session.regenerate((err) => {
    if (err) return res.status(500).json({ error: 'Session error' });

    req.session.userId = user.id;
    req.session.save((err) => {
      if (err) return res.status(500).json({ error: 'Session error' });
      res.json({ success: true });
    });
  });
});
```

---

## CSRF Prevention

### CSRF Token Pattern

CSRF (Cross-Site Request Forgery) protection requires cryptographically secure tokens.

**Token Requirements:**
- **Minimum length:** 128 bits (16 bytes)
- **Randomness:** Cryptographically secure
- **Uniqueness:** Per session or per request
- **Binding:** Tied to user session

**Generation:**
```javascript
const crypto = require('crypto');

function generateCSRFToken() {
  return crypto.randomBytes(32).toString('hex'); // 256-bit token
}
```

**Implementation Pattern:**

```javascript
// 1. Middleware: Attach CSRF token to session
app.use((req, res, next) => {
  if (!req.session.csrfToken) {
    req.session.csrfToken = generateCSRFToken();
  }
  res.locals.csrfToken = req.session.csrfToken;
  next();
});

// 2. HTML Form: Include token
// <form method="POST">
//   <input type="hidden" name="_csrf" value="<%= csrfToken %>">
// </form>

// 3. Middleware: Validate CSRF token on state-changing requests
app.use((req, res, next) => {
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
    const tokenFromRequest = req.body._csrf || req.headers['x-csrf-token'];
    const tokenFromSession = req.session.csrfToken;

    if (!tokenFromRequest || tokenFromRequest !== tokenFromSession) {
      return res.status(403).json({ error: 'CSRF token invalid' });
    }
  }
  next();
});
```

**HMAC-Based Token (Stateless):**
```javascript
const crypto = require('crypto');

const SECRET = process.env.CSRF_SECRET;

function generateCSRFToken(sessionId) {
  return crypto
    .createHmac('sha256', SECRET)
    .update(sessionId + Date.now())
    .digest('hex');
}

function verifyCSRFToken(token, sessionId) {
  const expectedToken = crypto
    .createHmac('sha256', SECRET)
    .update(sessionId + /* original timestamp would need to be stored */)
    .digest('hex');

  return crypto.timingSafeEqual(Buffer.from(token), Buffer.from(expectedToken));
}
```

### Using Express CSRF Libraries

**Using `csurf` middleware:**
```javascript
const csrf = require('csurf');
const cookieParser = require('cookie-parser');
const session = require('express-session');

app.use(cookieParser());
app.use(session({
  secret: 'your-secret-key',
  cookie: { secure: true, httpOnly: true, sameSite: 'strict' }
}));

const csrfProtection = csrf({
  cookie: false, // Store token in session, not cookie
});

// Display form with CSRF token
app.get('/form', csrfProtection, (req, res) => {
  res.send(`<form action="/process" method="POST">
    <input type="hidden" name="_csrf" value="${req.csrfToken()}">
    <button type="submit">Submit</button>
  </form>`);
});

// Validate CSRF token on POST
app.post('/process', csrfProtection, (req, res) => {
  res.json({ success: true });
});

// Error handler for CSRF failures
app.use((err, req, res, next) => {
  if (err.code === 'EBADCSRFTOKEN') {
    res.status(403).json({ error: 'CSRF token validation failed' });
  } else {
    next(err);
  }
});
```

### CSRF + SameSite Cookies (Defense in Depth)

```javascript
// Double protection: CSRF token + SameSite cookie
app.use(helmet.csrfProtection());

app.use((req, res, next) => {
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
    // Validate CSRF token
    const token = req.body._csrf || req.headers['x-csrf-token'];
    if (!req.session.csrfToken || token !== req.session.csrfToken) {
      return res.status(403).json({ error: 'CSRF validation failed' });
    }
  }
  next();
});

// Session cookie with SameSite
app.use(session({
  cookie: {
    sameSite: 'strict', // Blocks cross-site cookie transmission
    httpOnly: true,
    secure: true
  }
}));
```

### CSRF Limitations

**Important:** XSS defeats all CSRF protections because attackers can read tokens via JavaScript. Mitigate XSS first:
- Input validation
- Output encoding
- Content Security Policy (CSP)
- Trusted Types API
- Use framework auto-escaping

---

## Free Security Tools & Services

### Cloudflare (DNS + DDoS + WAF)

**What's Included (Free Tier):**
- **DNS Management:** Nameserver change (no cost)
- **DDoS Protection:** Automatic Layer 3/4 DDoS mitigation
- **WAF:** Free Managed Ruleset with high-profile vulnerability protection
- **SSL/TLS:** Automatic HTTPS with auto-renewing certificates
- **Page Rules:** Basic security rules
- **Bot Management:** Basic bot detection

**Getting Started:**
1. Register at cloudflare.com
2. Add your domain
3. Change nameservers to Cloudflare
4. Enable WAF and DDoS protection (automatic on free plan)

**Cost:** $0 (Free), $20/month (Pro), $200/month (Business)

### Let's Encrypt

**What's Included:**
- **Free SSL/TLS certificates** valid for 90 days
- **Automated renewal** via ACME protocol
- **Unlimited certificates** per domain
- **IP address certificates** (new in 2025)
- **Short-lived certificates** option

**Installation (Using Certbot):**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate (auto-renewal setup)
sudo certbot certonly --nginx -d example.com -d www.example.com

# Auto-renewal via cron
sudo certbot renew --dry-run

# Configure web server with certificate
# /etc/letsencrypt/live/example.com/
```

**In Docker:**
```dockerfile
FROM nginx:latest

RUN apt-get update && apt-get install -y certbot python3-certbot-nginx

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
```

**Cost:** $0 (Completely free)

### Snyk

**Free Tier Features (2025):**
- **Snyk Code:** Up to 100 vulnerability scans/month
- **Snyk Open Source:** Dependency vulnerability scanning
- **Snyk Container:** Container image scanning
- **Supported Languages:** JavaScript, Python, Java, Ruby, .NET, Go, Rust, and more
- **GitHub Integration:** Automatic PR scanning

**Limitations:**
- Valid only for 1-2 codebases
- No historical vulnerability tracking
- Limited to free tier features

**Getting Started:**
1. Sign up at snyk.io
2. Connect GitHub/GitLab repository
3. Enable automated scanning
4. Review vulnerability reports
5. Apply suggested fixes

**Cost:** $0 (Free), $25/month+ (Paid plans)

### Socket.dev

**Detection Capabilities:**
- **70+ supply chain risk signals** beyond traditional CVEs
- **Malware detection** in dependencies
- **Install scripts analysis** (post-install hooks)
- **Hidden code detection** (obfuscation)
- **Typosquatting prevention**
- **Zero-day supply chain attack detection**

**Speed:** Detects and blocks malicious packages within minutes of publication

**Supported Ecosystems:**
- JavaScript/npm (robust)
- Python (robust)
- Java, Ruby, .NET, Go, Rust, Scala, Kotlin
- PHP, Swift, Objective-C (planned)

**Pricing:**
- **Free forever:** For open source repositories
- **Paid:** Required for private repositories beyond first one

**Usage:**
```bash
# Install Socket CLI
npm install -g @socket-cli

# Scan your project
socket-cli check .
```

**Cost:** $0 (Free for open source)

### Mozilla Observatory

**Free Security Header Tester:** developer.mozilla.org/en-US/observatory

**Tests Performed:**
- Content-Security-Policy (CSP)
- HTTP Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy
- Cookie security attributes
- TLS/SSL configuration

**Recent Updates (October 2024):**
- Improved UI/UX
- Removed outdated X-XSS-Protection test
- 60-second rescan minimum (prevents abuse)
- Actionable recommendations

**Usage:**
1. Navigate to developer.mozilla.org/en-US/observatory
2. Enter your domain
3. Review security recommendations
4. Implement suggested headers
5. Rescan to verify

**Cost:** $0 (Completely free)

---

## Summary: Security Checklist for Deployments

### Pre-Launch Security Audit

- [ ] All OWASP Top 10 2025 vulnerabilities assessed
- [ ] Security headers configured (Helmet.js or equivalent)
- [ ] HTTPS/TLS 1.3 enforced
- [ ] CORS properly configured with whitelist
- [ ] CSRF protection implemented
- [ ] Rate limiting configured
- [ ] Password hashing using Argon2 or bcrypt (12+)
- [ ] Session cookies: HttpOnly, Secure, SameSite=Strict
- [ ] JWT validation: signature, claims, expiration
- [ ] Input validation and output encoding implemented
- [ ] Dependency scanning (Snyk, Socket.dev) integrated
- [ ] WAF rules enabled (Cloudflare or AWS WAF)
- [ ] Security header test passed (Mozilla Observatory)
- [ ] CSP policy validated and enabled
- [ ] Logging and monitoring configured
- [ ] Incident response plan documented

### Ongoing Maintenance

- [ ] Weekly: Review security logs and alerts
- [ ] Weekly: Check for dependency vulnerabilities
- [ ] Monthly: Update all dependencies and patches
- [ ] Quarterly: Penetration testing
- [ ] Quarterly: Security training for developers
- [ ] Annually: Full security audit

---

## References & Resources

**OWASP:**
- [OWASP Top 10:2025](https://owasp.org/Top10/2025/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

**Security Best Practices:**
- [Helmet.js Documentation](https://helmetjs.github.io/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [RFC 9700 - OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/rfc9700/)

**Tools & Services:**
- [Cloudflare](https://www.cloudflare.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Snyk](https://snyk.io/)
- [Socket.dev](https://socket.dev/)
- [Mozilla Observatory](https://developer.mozilla.org/en-US/observatory)
- [express-rate-limit](https://www.npmjs.com/package/express-rate-limit)
- [Upstash Rate Limiting](https://upstash.com/docs/redis/sdks/ratelimit-ts/overview)

**Password Hashing:**
- [Password Storage - OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Argon2 - Password Hashing Competition](https://password-hashing.info/)

**Latest Research:**
- [OWASP Top 10 2025 - What's Changed](https://about.gitlab.com/blog/2025-owasp-top-10-whats-changed-and-why-it-matters/)
- [OAuth 2.0 Common Vulnerabilities](https://blog.doyensec.com/2025/01/30/oauth-common-vulnerabilities.html)
- [JWT Vulnerabilities 2025-2026](https://redsentry.com/resources/blog/jwt-vulnerabilities-list-2026-security-risks-mitigation-guide)

---

**Document Version:** 1.0
**Last Updated:** February 2026
**Security References:** 75+ authoritative sources
**Applicable To:** All web application architectures

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->

---
## Related References
- [Security & Zero Trust](./44-security-zero-trust.md) — Deep dive: CORS, CSP, passkeys, supply chain
- [HIPAA Compliance](./33-compliance-hipaa.md) — Healthcare security requirements
- [SOC 2 Compliance](./34-compliance-soc2.md) — Security audit requirements
- [Feature Flags](./57-feature-flags-experimentation.md) — Kill switches for incident response
