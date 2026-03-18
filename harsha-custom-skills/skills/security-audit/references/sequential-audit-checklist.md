# Sequential Audit Checklist

Condensed operational checklist for executing security audits in sequential/inline mode (when sub-agents are not available). For full domain details, see the individual auditor files in `agents/`.

---

## How to Use This Checklist

1. Run `scripts/run-audit.sh <target-dir>` first to pre-compute grep results
2. Read the output files in `audit-workdir/grep-results/`
3. For each domain below, review the grep results and read flagged files
4. Record findings in JSON format per `references/shared-formats.md`
5. Run `scripts/merge-findings.py` on collected findings

---

## Domain 1: Injection (CWE-89, CWE-78, CWE-90, CWE-943)

**OWASP:** A03:2021-Injection

### Quick Checks
- [ ] SQL queries with string concatenation/interpolation
- [ ] NoSQL queries with `$where`, `$regex`, or `JSON.parse`
- [ ] Command execution with shell=True or backticks
- [ ] Template rendering with user-controlled templates

### Key Grep Patterns
```bash
grep -rn "query.*\+" --include="*.js"           # SQL concat JS
grep -rn 'f".*SELECT' --include="*.py"          # SQL f-string Python
grep -rn "subprocess.*shell=True" --include="*.py"  # Command injection
grep -rn "child_process\.exec(" --include="*.js"    # Command injection JS
```

### Severity Guide
- **Critical**: SQL injection on sensitive data, command injection with user input
- **High**: NoSQL injection, limited command injection
- **Medium**: Template injection in sandboxed context

### Non-Invasive Fix
- Convert to parameterized queries (same output)
- Use `shlex.quote()` or subprocess with `shell=False`

---

## Domain 2: XSS-CSRF (CWE-79, CWE-352)

**OWASP:** A03:2021-Injection, A01:2021-Broken Access Control

### Quick Checks
- [ ] `innerHTML`, `dangerouslySetInnerHTML`, `v-html` usage
- [ ] Template `|safe` filter or `mark_safe()`
- [ ] CSRF protection disabled or missing
- [ ] Cookie missing `SameSite`, `HttpOnly`, `Secure`

### Key Grep Patterns
```bash
grep -rn "innerHTML" --include="*.js" --include="*.ts"
grep -rn "dangerouslySetInnerHTML" --include="*.jsx" --include="*.tsx"
grep -rn "|safe" --include="*.html" --include="*.jinja*"
grep -rn "csrf_exempt" --include="*.py"
```

### Severity Guide
- **Critical**: Stored XSS in user content
- **High**: Reflected XSS, CSRF on critical actions
- **Medium**: DOM XSS requiring interaction

### Non-Invasive Fix
- Replace `innerHTML` with `textContent`
- Remove `|safe` filter
- Enable CSRF middleware

---

## Domain 3: Auth-Session (CWE-287, CWE-384, CWE-613)

**OWASP:** A07:2021-Identification and Authentication Failures

### Quick Checks
- [ ] JWT with `algorithm: "none"` allowed
- [ ] Hardcoded secrets in JWT signing
- [ ] Session cookies missing security flags
- [ ] No token expiration
- [ ] Password comparison using `===` (timing attack)

### Key Grep Patterns
```bash
grep -rn "jwt\.verify\|jwt\.sign" --include="*.js"
grep -rn "algorithm.*none" --include="*.js"
grep -rn "httpOnly.*false\|secure.*false" --include="*.js"
grep -rn "===.*password\|password.*===" --include="*.js"
```

### Severity Guide
- **Critical**: Auth bypass, algorithm:none accepted
- **High**: Hardcoded JWT secret, no expiration
- **Medium**: Missing cookie flags

### Non-Invasive Fix
- Restrict JWT algorithms to allowlist
- Move secrets to environment variables
- Add expiration (requires token rotation plan)

---

## Domain 4: Access Control (CWE-639, CWE-285, CWE-862)

**OWASP:** A01:2021-Broken Access Control

### Quick Checks
- [ ] Resources accessed by user-provided ID without ownership check
- [ ] Routes missing auth middleware
- [ ] Privilege escalation via role manipulation
- [ ] Mass assignment allowing role changes

### Key Grep Patterns
```bash
grep -rn "findById(req\.params" --include="*.js"
grep -rn "router\.\(get\|post\|put\|delete\)(" --include="*.js"
grep -rn "\.update.*role" --include="*.js"
grep -rn "req\.body\.role" --include="*.js"
```

### Severity Guide
- **Critical**: IDOR exposing all user data
- **High**: IDOR on sensitive data, privilege escalation
- **Medium**: Missing auth on non-sensitive routes

### Non-Invasive Fix
- Add ownership check before data access
- Add auth middleware to routes
- Use allowlist for updatable fields

---

## Domain 5: Crypto-Data (CWE-327, CWE-328, CWE-916)

**OWASP:** A02:2021-Cryptographic Failures

### Quick Checks
- [ ] MD5/SHA1 for password hashing
- [ ] `Math.random()` for security purposes
- [ ] Weak encryption (DES, 3DES, RC4, ECB mode)
- [ ] Hardcoded encryption keys/IVs

### Key Grep Patterns
```bash
grep -rn "createHash.*md5\|createHash.*sha1" --include="*.js"
grep -rn "Math\.random()" --include="*.js"
grep -rn "DES\|RC4\|ECB" --include="*.js" --include="*.py"
grep -rn "key.*=.*['\"].\{16,\}['\"]" --include="*.js"
```

### Severity Guide
- **Critical**: Passwords hashed with MD5/SHA1
- **High**: Hardcoded encryption keys
- **Medium**: Weak ciphers, insecure random

### Non-Invasive Fix
- Replace MD5/SHA1 with bcrypt/argon2
- Use `crypto.randomBytes()` or `secrets` module
- Move keys to environment

---

## Domain 6: Secrets (CWE-798, CWE-321)

**OWASP:** A02:2021-Cryptographic Failures

### Quick Checks
- [ ] API keys hardcoded in source
- [ ] Database credentials in config files
- [ ] Private keys in repository
- [ ] AWS/GCP/Azure credentials exposed

### Key Grep Patterns
```bash
grep -rn "AKIA[0-9A-Z]\{16\}"                    # AWS Access Key
grep -rn "ghp_[a-zA-Z0-9]\{36\}"                 # GitHub Token
grep -rn "sk_live_\|sk_test_"                    # Stripe Keys
grep -rn "-----BEGIN.*PRIVATE KEY-----"          # Private Keys
```

### Severity Guide
- **Critical**: Production API keys, private keys
- **High**: Database credentials, cloud provider keys
- **Medium**: Test/sandbox credentials

### Non-Invasive Fix
- Move to environment variables
- Add to `.gitignore`
- Rotate exposed credentials

---

## Domain 7: Dependencies (CWE-1035)

**OWASP:** A06:2021-Vulnerable and Outdated Components

### Quick Checks
- [ ] Known vulnerable package versions
- [ ] Outdated major versions
- [ ] Unpatched security advisories

### Analysis Method
1. Run `scripts/scan-dependencies.py <target-dir>`
2. Review output for known vulnerabilities
3. Check `npm audit` / `pip-audit` if available

### Severity Guide
- **Critical**: RCE vulnerabilities in deps
- **High**: Data exposure, auth bypass vulnerabilities
- **Medium**: DoS, limited impact vulnerabilities
- **Low**: Best practice updates

### Non-Invasive Fix
- Bump to patched minor/patch version
- Review changelog for breaking changes

---

## Domain 8: Config-Headers (CWE-16, CWE-693)

**OWASP:** A05:2021-Security Misconfiguration

### Quick Checks
- [ ] Missing security headers (CSP, X-Frame-Options, etc.)
- [ ] CORS allowing all origins (`*`)
- [ ] Debug mode enabled
- [ ] Default credentials

### Key Grep Patterns
```bash
grep -rn "helmet\|lusca" --include="*.js"       # Security middleware
grep -rn "origin.*\*" --include="*.js"          # Open CORS
grep -rn "DEBUG.*=.*True" --include="*.py"      # Debug mode
```

### Severity Guide
- **High**: Debug mode in production, open CORS
- **Medium**: Missing critical headers
- **Low**: Missing optional headers

### Non-Invasive Fix
- Add security header middleware
- Restrict CORS to specific origins
- Disable debug mode

---

## Domain 9: Logging-Monitoring (CWE-778, CWE-532)

**OWASP:** A09:2021-Security Logging and Monitoring Failures

### Quick Checks
- [ ] Passwords/tokens logged
- [ ] Full request bodies logged
- [ ] Log injection possible
- [ ] Missing audit logs for security events

### Key Grep Patterns
```bash
grep -rn "console\.log.*password\|console\.log.*token" --include="*.js"
grep -rn "console\.log.*req\.body" --include="*.js"
grep -rn "logger.*password" --include="*.py"
```

### Severity Guide
- **High**: Passwords logged in plaintext
- **Medium**: Tokens/sessions logged
- **Low**: Excessive logging without sensitive data

### Non-Invasive Fix
- Redact sensitive fields before logging
- Use structured logging with field filtering

---

## Domain 10: Error Handling (CWE-209, CWE-200)

**OWASP:** A05:2021-Security Misconfiguration

### Quick Checks
- [ ] Stack traces returned to users
- [ ] Database errors exposed
- [ ] Internal paths revealed
- [ ] Auth error oracles ("user not found" vs "wrong password")

### Key Grep Patterns
```bash
grep -rn "res\..*err\.stack" --include="*.js"
grep -rn "res\..*e\.message" --include="*.js"
grep -rn "user not found\|invalid user" --include="*.js"
```

### Severity Guide
- **Medium**: Stack traces exposed
- **Low**: Verbose errors, path disclosure

### Non-Invasive Fix
- Return generic error to user
- Log full details internally
- Use consistent auth error messages

---

## Domain 11: Concurrency (CWE-367, CWE-362)

**OWASP:** A04:2021-Insecure Design

### Quick Checks
- [ ] Check-then-act patterns on balances/inventory
- [ ] Non-atomic counter increments
- [ ] Double-submit possible on payments

### Key Grep Patterns
```bash
grep -rn "balance.*-=\|balance.*+=" --include="*.js"
grep -rn "inventory.*-=" --include="*.js"
grep -rn "counter++\|count++" --include="*.js"
```

### Severity Guide
- **Critical**: Race condition on financial transactions
- **High**: Inventory/stock manipulation
- **Medium**: Non-financial state races

### Non-Invasive Fix
- Use atomic database operations
- Add transactions with locking
- Implement idempotency keys

---

## Domain 12: API Endpoints (CWE-918, CWE-400, CWE-799)

**OWASP:** A10:2021-SSRF, A05:2021-Security Misconfiguration

### Quick Checks
- [ ] No rate limiting on login/auth endpoints
- [ ] SSRF via user-provided URLs
- [ ] Mass assignment on models
- [ ] No pagination on list endpoints

### Key Grep Patterns
```bash
grep -rn "rateLimit\|rate-limit" --include="*.js"
grep -rn "fetch(.*req\.\|axios(.*req\." --include="*.js"
grep -rn "\.create(req\.body)\|\.update(req\.body)" --include="*.js"
```

### Severity Guide
- **High**: SSRF to internal services
- **Medium**: Missing rate limiting, mass assignment
- **Low**: Missing pagination

### Non-Invasive Fix
- Add rate limiting middleware
- Validate/allowlist URLs for SSRF
- Use explicit field allowlist for updates

---

## Domain 13: Input-Output (CWE-22, CWE-434, CWE-502)

**OWASP:** A03:2021-Injection, A08:2021-Software and Data Integrity Failures

### Quick Checks
- [ ] Path traversal via user input in file paths
- [ ] Unrestricted file upload (type, size)
- [ ] Unsafe deserialization (pickle, yaml.load)
- [ ] Type coercion issues (`==` vs `===`)

### Key Grep Patterns
```bash
grep -rn "path\.join.*req\." --include="*.js"
grep -rn "readFile.*req\." --include="*.js"
grep -rn "pickle\.loads\|yaml\.load" --include="*.py"
grep -rn "==\s*false\|==\s*null" --include="*.js"
```

### Severity Guide
- **Critical**: Path traversal to sensitive files
- **High**: Unsafe deserialization, unrestricted upload
- **Medium**: Limited path traversal

### Non-Invasive Fix
- Validate paths don't contain `..`
- Restrict uploads by type/size
- Use safe deserialization (`yaml.safe_load`)

---

## Domain 14: Business Logic (CWE-841, CWE-837, CWE-863)

**OWASP:** A04:2021-Insecure Design

### Quick Checks
- [ ] Price/total accepted from client
- [ ] Coupon codes reusable or stackable
- [ ] Workflow steps skippable
- [ ] Trial/subscription dates modifiable

### Key Grep Patterns
```bash
grep -rn "req\.body\.price\|req\.body\.amount" --include="*.js"
grep -rn "coupon\|discount\|promo" --include="*.js"
grep -rn "order.*status\|payment.*status" --include="*.js"
```

### Severity Guide
- **Critical**: Arbitrary price setting
- **High**: Unlimited discount application
- **Medium**: Workflow bypass

### Non-Invasive Fix
- Calculate totals server-side
- Server-side coupon validation
- State machine for workflows

---

## Domain 15: Database Security — Supabase/Postgres (CWE-798, CWE-862, CWE-89)

**OWASP:** A01:2021-Broken Access Control, A02:2021-Cryptographic Failures, A03:2021-Injection

**⛔ ALL fixes in this domain are `requires_review` unless purely config/code-level.**

### Quick Checks
- [ ] Service role key exposed in client-side code
- [ ] Tables without RLS enabled
- [ ] Overly permissive RLS policies (`USING (true)`)
- [ ] `FOR ALL` policies instead of per-operation policies
- [ ] SQL injection via `.rpc()` with string interpolation
- [ ] Connection strings hardcoded in source
- [ ] Connections without SSL/TLS
- [ ] Public storage buckets without policies
- [ ] Edge functions without auth verification
- [ ] Missing auth check before Supabase queries in components

### Key Grep Patterns
```bash
grep -rn "SUPABASE_SERVICE_ROLE\|service_role" --include="*.tsx" --include="*.jsx"
grep -rn "NEXT_PUBLIC.*SERVICE_ROLE" --include="*.env*"
grep -rn "CREATE TABLE" --include="*.sql" supabase/migrations/
grep -rn "ENABLE ROW LEVEL SECURITY" --include="*.sql" supabase/migrations/
grep -rn "USING\s*(true)" --include="*.sql"
grep -rn "\.rpc(.*\`" --include="*.ts" --include="*.tsx"
grep -rn "postgresql://\|postgres://" --include="*.ts" --include="*.env*"
```

### Severity Guide
- **Critical**: Service role key in client code, SQL injection via RPC
- **High**: Missing RLS on user data tables, hardcoded connection strings
- **Medium**: Overly permissive policies, missing auth checks, public buckets
- **Low**: Missing SSL config, `FOR ALL` policies on non-sensitive tables
- **Info**: Migration best practices, documentation gaps

### Non-Invasive Fix (ALL `requires_review`)
- Move service key to server-only env var
- Report missing RLS (do NOT auto-add policies)
- Report overly permissive policies (do NOT auto-modify)
- Parameterize RPC calls (code-level only, `all_pass` if contract unchanged)
- Move connection strings to env vars (`all_pass`)

**See `references/supabase-database-patterns.md` for comprehensive patterns.**

---

## Output Collection

After reviewing all domains, collect findings into a single JSON array:

```json
{
  "project": "target-project",
  "audit_date": "2024-01-15",
  "findings": [
    // All findings from all domains
  ]
}
```

Then run:
```bash
python3 scripts/merge-findings.py findings.json > merged-findings.json
python3 scripts/generate-report.py merged-findings.json > report.md
```
