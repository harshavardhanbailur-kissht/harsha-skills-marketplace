# Security-Specific Documentation Patterns

## Documenting Authentication and Authorization

### Authentication Flow Documentation

**What to document:**

```markdown
## Authentication Mechanism

**Type:** OAuth 2.0 with JWT tokens

**Flow:**
1. User login via OAuth provider (Google, GitHub)
2. Provider returns authorization code
3. Backend exchanges code for access token + refresh token
4. Access token is JWT, signed with private key
5. Token stored in HttpOnly cookie (not accessible to JavaScript)
6. Token included in Authorization header for API requests
7. Backend validates token signature on each request

**Implementation:**
- File: src/auth/oauth.py
- Provider integration: src/auth/providers/
- Token validation: middleware/auth.py:45
- Token refresh: src/auth/token_refresh.py

**Configuration:**
- OAUTH_CLIENT_ID: [secure, from environment]
- OAUTH_CLIENT_SECRET: [secure, from environment]
- JWT_SIGNING_KEY: [secure, from key management]
- TOKEN_TTL: 3600 seconds (1 hour)
- REFRESH_TOKEN_TTL: 2592000 seconds (30 days)

**Edge Cases:**
- What if provider is unreachable? → Return 503 Service Unavailable
- What if token expires mid-request? → Return 401 Unauthorized
- What if user revokes access at provider? → Refresh fails, user logs out

**Security Assumptions:**
- HTTPS enforced (no cleartext tokens)
- HttpOnly cookies prevent XSS token theft
- CSRF protection via SameSite cookies
- Tokens are short-lived (1 hour max)
```

**What NOT to document:**
- Actual secret values
- Private key contents
- How to forge tokens (security through obscurity fails, but don't enable attacks)
- Weaknesses that haven't been patched

### Authorization Documentation

```markdown
## Access Control

**Model:** Role-Based Access Control (RBAC)

**Roles:**
| Role | Permissions | Who | Escalation |
|------|------------|-----|-----------|
| User | Read own orders | Customers | None |
| Support | Read all orders, answer questions | Support team | Manager |
| Admin | All actions | Administrators | CEO |

**Permission Checking:**
```python
# Middleware enforces role checks
@app.get("/orders")
@require_role("user")  # or "support" or "admin"
def list_orders():
    ...
```

**File:** src/auth/rbac.py:123

**Gotchas:**
- User can read own orders (scope check)
- Support can view but not modify (read-only)
- Admin bypass not used (audit trail every action)

**Testing:**
- test_user_cannot_read_others_orders
- test_support_can_read_all_orders
- test_admin_can_escalate_permissions
```

---

## Vulnerability Documentation Without Exploitation

### Pattern: Known Issues with Mitigation

**WRONG (enables exploitation):**
```
"There's an SQL injection vulnerability in the search endpoint.
The user input isn't sanitized in the query string."
```

**RIGHT (documents risk without enabling attack):**
```markdown
## Input Validation

**Search Endpoint** (`GET /products/search`)

**Implementation:**
- Uses parameterized queries (prepared statements)
- Input validated via Pydantic schema
- Length limit: 100 characters
- Allowed characters: alphanumeric, hyphen, underscore

**Tested:**
- test_search_with_valid_input
- test_search_rejects_invalid_characters
- test_search_respects_length_limit

**Security approach:**
- Whitelist allowed characters (not blacklist bad ones)
- Parameterized queries prevent SQL injection
- Input validation in business logic, not view layer
```

### Pattern: Security Assumptions

```markdown
## Payment Processing

**Security Assumptions:**

1. **TLS 1.2+ is enforced**
   - All payment traffic encrypted in transit
   - No fallback to HTTP
   - Test: test_payment_api_requires_tls

2. **Private keys are not stored in code**
   - Stripe API keys in environment variables
   - Never in git (checked by git hooks)
   - Test: verify_no_secrets_in_git

3. **Payment data is not logged**
   - Sensitive fields excluded from logs
   - PII not in error messages
   - Test: test_payment_logs_exclude_card_data

**If assumption breaks:**
- Assumption 1 breaks: Man-in-the-middle attacks possible
- Assumption 2 breaks: Private key compromise
- Assumption 3 breaks: PII leakage in logs
```

---

## Data Flow with PII Marking

### Diagram Pattern

```
[User Input]
    ↓
[Validation - no PII logged]
    ↓
[Processing]
    ↓
[Database - PII ENCRYPTED]
    ↓
[Replication - PII ENCRYPTED in transit]
    ↓
[Backup - PII ENCRYPTED at rest]
```

### Data Classification

```markdown
## User Data Handling

| Field | Type | Storage | Encryption | Logged | Exported |
|-------|------|---------|-----------|--------|----------|
| user_id | String | DB | No | Yes | Yes |
| email | PII | DB | At-rest | No | No |
| password_hash | Secret | DB | N/A | No | No |
| full_name | PII | DB | At-rest | No | If authorized |
| phone | PII | DB | At-rest | No | If authorized |
| ip_address | PII | Logs | N/A | Hashed | No |
| browser_ua | Non-PII | Logs | No | Yes | Yes |

**At-rest encryption:** Field-level encryption using AWS KMS
**In-transit encryption:** TLS 1.2+ for all connections
**Key rotation:** Automatic monthly via KMS

**Handling:**
- Email: Used for login, not logged, never exported to third parties
- Password: Hashed with bcrypt, never stored plaintext
- Phone: Encrypted at rest, used for 2FA only
- IP: Hashed in logs to prevent user tracking
```

### Handling Sensitive Data in Code

```markdown
## Secrets Management

**Rule 1: Secrets Not in Code**
```python
# WRONG
api_key = "sk_live_<REDACTED_EXAMPLE>"  # NEVER

# RIGHT
api_key = os.environ.get("STRIPE_API_KEY")
```

**Rule 2: Secrets Not in Logs**
```python
# WRONG
logger.info(f"User logged in with token: {token}")

# RIGHT
logger.info("User logged in")  # Log event, not token
logger.debug(f"Token hash: {hash(token)}")  # If debugging needed
```

**Rule 3: Secrets Not in Error Messages**
```python
# WRONG
except Exception as e:
    return {"error": str(e)}  # Error might contain API key!

# RIGHT
logger.exception("Payment processing failed")  # Log full error
return {"error": "Payment processing failed"}  # Generic to client
```

**Testing:**
- test_no_secrets_in_logs
- test_no_secrets_in_error_responses
- test_sensitive_fields_encrypted
```

---

## Encryption Documentation

### Encryption-at-Rest

```markdown
## Data Encryption

**Sensitive Fields (encrypted at-rest):**
- user.email
- user.phone
- user.ssn
- payment.card_token
- user.address

**Encryption Method:**
- Algorithm: AES-256-GCM
- Key Management: AWS KMS
- Key rotation: Monthly automatic
- Master key: AWS-managed (never exposed)

**Implementation:**
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_sensitive_field(plaintext, key):
    nonce = os.urandom(12)
    cipher = AESGCM(key)
    ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext  # Nonce prepended for decryption
```

**Testing:**
- test_sensitive_fields_encrypted_in_database
- test_decryption_produces_original_value
- test_encrypted_data_unreadable_without_key

**Verification:**
```bash
# Verify fields in database are ciphertexts
SELECT user_id, email FROM users LIMIT 1;
# Should show: random binary data, not readable email
```

**In case of key compromise:**
1. Generate new master key in KMS
2. Re-encrypt all data with new key (backup first)
3. Invalidate sessions (relogin required)
4. Monitor for unauthorized access
```

### Encryption-in-Transit

```markdown
## TLS Configuration

**Enforced:**
- TLS 1.2 minimum (no TLS 1.0, 1.1)
- Strong ciphers (no RC4, weak algorithms)
- Certificate pinning for payment APIs

**Configuration:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

**Verification:**
```bash
# Check TLS version
openssl s_client -connect api.example.com:443 -tls1_2

# Check cipher strength
nmap --script ssl-enum-ciphers api.example.com
```

**Testing:**
- test_https_redirect_on_all_endpoints
- test_tls_1_0_connections_rejected
- test_weak_ciphers_not_available
```

---

## Authentication Token Documentation

```markdown
## JWT Token Structure

**Token composition:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  # Header
.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjo...    # Payload
.4gLnNVRb_16jBjJGvxR3wNfSbzn...        # Signature
```

**Payload contents:**
```json
{
  "sub": "user123",           // Subject (who)
  "iss": "api.example.com",   // Issuer
  "aud": "web-app",           // Audience
  "exp": 1647281600,          // Expiration (1 hour from issue)
  "iat": 1647278000,          // Issued at
  "roles": ["user", "admin"]  // User roles
}
```

**Security properties:**
- Token is SIGNED with private key (tampering detected)
- Token is NOT encrypted (don't put secrets in payload!)
- Token is STATELESS (validated by signature, no DB lookup)

**Validation:**
- Signature verification: Ensures token not tampered
- Expiration check: Ensures token not stale
- Audience check: Ensures token for correct service

**Risks:**
- Token exposed via XSS: Mitigation = HttpOnly cookie
- Token exposed via man-in-the-middle: Mitigation = TLS enforcement
- Token leaked in logs: Mitigation = no logging of tokens
```

---

## Audit and Logging for Security

```markdown
## Security Audit Trail

**What is logged:**
- Login attempts (success and failure)
- Permission changes (who changed whose access)
- Sensitive data access (who accessed PII)
- Failed authentication (potential brute force)
- Admin actions (deletion, escalation)

**Example log entry:**
```
timestamp=2026-03-12T15:30:45Z
event=login_success
user_id=user123
ip_hash=h4x7k2m  # Hashed IP for privacy
user_agent_hash=4j2nq5m  # Hashed UA
location=NY  # Inferred from IP (if enabled)
```

**What is NOT logged:**
- Passwords (at any stage)
- API keys
- Tokens
- Credit card numbers
- Email addresses (to prevent tracking)

**Retention:**
- Security logs: 2 years
- Audit trail: 7 years (for compliance)
- Debug logs: 30 days

**Access:**
- Only security team can view audit logs
- Access is logged (who accessed logs)
- Automated alerts on suspicious patterns
```

---

## Security Testing Documentation

```markdown
## Security Testing

**Test coverage:**

| Threat | Test Name | How |
|--------|-----------|-----|
| SQL Injection | test_sql_injection_prevented | Attempt `' OR '1'='1` in search |
| XSS | test_xss_input_sanitized | Attempt `<script>` injection |
| CSRF | test_csrf_token_required | POST without token fails |
| Brute force | test_login_rate_limiting | 10 failed logins → 429 |
| Session fixation | test_session_token_rotated | New token after login |

**Automated scanning:**
- OWASP ZAP (penetration testing)
- Dependabot (dependency vulnerabilities)
- Snyk (code vulnerabilities)
- SonarQube (code quality)

**Manual testing:**
- Annual penetration test
- Vulnerability assessment by third party
- Red team exercise (quarterly)
```

---

## Incident Response

```markdown
## Security Incident Response

**If credentials are compromised:**
1. Rotate credentials immediately
2. Invalidate all active sessions
3. Force password reset for affected users
4. Monitor for unauthorized access
5. File incident report
6. Post-mortem within 24 hours

**If data is breached:**
1. Isolate affected systems
2. Assess scope of exposure
3. Notify affected users within 72 hours
4. File regulatory reports (GDPR, etc.)
5. Work with security firm for root cause
6. Update security measures

**If service is compromised:**
1. Failover to backup systems
2. Engage incident response team
3. Begin forensics
4. Communicate status externally
5. Recovery and validation
6. Root cause analysis and fixes
```

---

## Security Documentation Checklist

Before publishing documentation:

- [ ] No secrets (API keys, passwords, tokens)
- [ ] No exploitation guides (describe security, not attack vectors)
- [ ] PII clearly marked and handling documented
- [ ] Encryption explained (types, algorithms, key management)
- [ ] Authentication and authorization flows clear
- [ ] Known vulnerabilities documented with mitigations
- [ ] Security assumptions explicit
- [ ] Testing approach documented
- [ ] Audit logging covered
- [ ] Incident response plan referenced
- [ ] Reviewed by security team
- [ ] No false sense of security (acknowledge risks)
