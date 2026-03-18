# Shared Formats Reference

This document is the **single source of truth** for formats, checklists, and classification criteria used throughout the security audit skill. All auditors and coordination files reference this document instead of duplicating content.

---

## The 10-Point Non-Invasive Fix Checklist

**EVERY proposed fix MUST pass ALL 10 checks. No exceptions.**

| # | Check | Pass Criteria | Verification Method |
|---|-------|---------------|---------------------|
| 1 | Zero UI/UX changes | No visual, layout, interaction, or rendering modifications | Diff shows no frontend file modifications |
| 2 | Identical outputs | Same input produces exactly same output | Manual test or automated comparison |
| 3 | User flows unchanged | No new steps, removed steps, or reordering | User journey documentation unchanged |
| 4 | API contracts unchanged | Same request/response schemas, status codes, headers | Schema comparison, endpoint testing |
| 5 | No performance regression | No observable slowdown (response time within 10%) | Timing comparison before/after |
| 6 | Error messages unchanged | User-facing errors identical (internal logging can change) | Compare user-visible error strings |
| 7 | Config additive-only | New config with safe defaults, no removed options | Config diff shows only additions |
| 8 | No new runtime deps | Prefer stdlib, existing deps, or dev-only tools | package.json/requirements unchanged or dev-only |
| 9 | Minimal diff | Smallest change that addresses the vulnerability | Lines changed is minimal for the fix |
| 10 | Trivially reversible | Single git revert undoes the fix | Single commit, clean revert possible |

### Checklist Status Values

- `all_pass`: All 10 points verified, fix is ready to apply automatically
- `requires_review`: One or more points need manual verification before applying
- `pending`: Checklist not yet evaluated

**If ANY check fails**: Mark finding as `requires_review` instead of `all_pass`.

---

## Finding Output Format

All auditors and the coordinator use this JSON structure for findings:

```json
{
  "id": "FINDING-001",
  "title": "SQL Injection in user search",
  "severity": "critical",
  "cvss": 9.8,
  "cwe": "CWE-89",
  "owasp": "A03:2021-Injection",
  "domain": "injection",
  "location": "src/api/users.js:47",
  "evidence": "const query = `SELECT * FROM users WHERE id = ${req.params.id}`;",
  "impact": "Full database access, data exfiltration, potential RCE via stacked queries",
  "fix": "- const query = `SELECT * FROM users WHERE id = ${req.params.id}`;\n+ const query = 'SELECT * FROM users WHERE id = ?';\n+ connection.query(query, [req.params.id]);",
  "verification": "1. Run existing tests\n2. Verify query returns same data\n3. Test SQL injection payload returns 400/404",
  "checklist_status": "all_pass",
  "checklist_notes": ""
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier (FINDING-NNN format) |
| title | string | Yes | Brief description of the vulnerability |
| severity | enum | Yes | One of: critical, high, medium, low, info |
| cvss | float | Yes | CVSS 3.1 score (0.0-10.0) |
| cwe | string | Yes | CWE identifier (CWE-NNN format) |
| owasp | string | Yes | OWASP Top 10 2021 category |
| domain | string | Yes | Security domain (injection, xss-csrf, auth-session, etc.) |
| location | string | Yes | File path and line number (path:line format) |
| evidence | string | Yes | Code snippet showing the vulnerability |
| impact | string | Yes | Description of potential damage if exploited |
| fix | string | Yes | Diff-formatted fix (- for removed, + for added lines) |
| verification | string | Yes | Steps to verify fix works without breakage |
| checklist_status | enum | Yes | One of: all_pass, requires_review, pending |
| checklist_notes | string | No | Explanation if checklist_status is requires_review |

### Markdown Finding Format

For human-readable reports, use this format:

```markdown
### FINDING-001: SQL Injection in user search

- **Severity**: Critical
- **CVSS**: 9.8
- **CWE**: CWE-89 (SQL Injection)
- **OWASP**: A03:2021-Injection
- **Domain**: injection
- **Location**: `src/api/users.js:47`

**Evidence:**
```javascript
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
```

**Impact:** Full database access, data exfiltration, potential RCE via stacked queries

**Recommended Fix:**
```diff
- const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
+ const query = 'SELECT * FROM users WHERE id = ?';
+ connection.query(query, [req.params.id]);
```

**Verification:**
1. Run existing tests
2. Verify query returns same data
3. Test SQL injection payload returns 400/404

**Non-Invasive Checklist:** All 10 points pass - Ready to apply
```

---

## Severity Classification Matrix

Use this matrix to determine finding severity consistently across all domains.

### Critical (CVSS 9.0-10.0)

Immediate exploitation risk with major business impact:

| Pattern | Example | CWE |
|---------|---------|-----|
| Remote Code Execution | Command injection, unsafe deserialization | CWE-78, CWE-502 |
| SQL Injection with data access | Unparameterized queries on sensitive data | CWE-89 |
| Authentication bypass | Broken auth allowing access to any account | CWE-287 |
| Hardcoded admin credentials | Admin password in source code | CWE-798 |
| Exposed private keys | RSA/SSH keys in repository | CWE-321 |
| Mass data exposure | API returning all user records | CWE-200 |

### High (CVSS 7.0-8.9)

Significant vulnerability requiring urgent attention:

| Pattern | Example | CWE |
|---------|---------|-----|
| Stored XSS | Script injection in user comments | CWE-79 |
| IDOR on sensitive data | Access to other users' data via ID manipulation | CWE-639 |
| JWT algorithm:none | Token verification accepting unsigned tokens | CWE-347 |
| Privilege escalation | User able to access admin functions | CWE-269 |
| SSRF to internal services | Server-side request to internal APIs | CWE-918 |
| Hardcoded API keys | Production API keys in code | CWE-798 |

### Medium (CVSS 4.0-6.9)

Moderate risk requiring scheduled remediation:

| Pattern | Example | CWE |
|---------|---------|-----|
| Reflected XSS | URL parameter reflected in response | CWE-79 |
| CSRF on state-changing actions | Missing token on profile update | CWE-352 |
| Missing rate limiting | Brute force possible on login | CWE-307 |
| Information disclosure | Stack traces, internal paths exposed | CWE-200 |
| Weak cryptographic algorithm | Using MD5 for password hashing | CWE-327 |
| Race condition (limited impact) | Double-submit on non-financial action | CWE-367 |

### Low (CVSS 0.1-3.9)

Minor issues for normal maintenance:

| Pattern | Example | CWE |
|---------|---------|-----|
| Missing security headers | No X-Frame-Options, CSP | CWE-693 |
| Verbose error messages | Detailed errors to unauthenticated users | CWE-209 |
| Debug mode in non-production | DEBUG=True in staging | CWE-489 |
| Outdated dependencies (no exploit) | Old but not vulnerable version | CWE-1035 |
| Minor information leakage | Software versions in headers | CWE-200 |

### Info (CVSS 0)

Best practice recommendations (not vulnerabilities):

| Pattern | Example |
|---------|---------|
| Defense-in-depth suggestions | Add CSP even without XSS found |
| Code quality observations | Could use more specific error handling |
| Future-proofing recommendations | Consider implementing SRI for CDN resources |
| Documentation gaps | Security-relevant behavior not documented |

---

## Security Domain Mapping

| Domain | Primary CWEs | OWASP Category | Key Files to Audit |
|--------|--------------|----------------|-------------------|
| injection | 89, 78, 90, 943 | A03 | Database queries, CLI handlers, templates |
| xss-csrf | 79, 352, 346 | A03, A01 | Templates, frontend JS, form handlers |
| auth-session | 287, 384, 613, 798 | A07 | Auth modules, JWT handlers, session config |
| access-control | 639, 285, 862 | A01 | Middleware, route guards, permission checks |
| crypto-data | 327, 328, 916 | A02 | Encryption modules, hash functions |
| secrets | 798, 321, 312 | A02 | Config files, env handling, credentials |
| dependency | 1035 | A06 | Package manifests, lock files |
| config-headers | 16, 693 | A05 | Server config, HTTP setup, CORS |
| logging-monitoring | 778, 532 | A09 | Logger setup, audit trails |
| error-handling | 209, 200 | A05 | Catch blocks, error middleware |
| concurrency | 367, 362 | A04 | Transaction code, shared state |
| api-endpoint | 918, 400, 799 | A10 | Route definitions, controllers |
| input-output | 22, 434, 502 | A03, A08 | Validators, file handlers, serializers |
| business-logic | 841, 837, 863 | A04 | Payment, workflow, discount logic |
| database-security | 798, 862, 89, 16 | A01, A02, A03, A05 | Supabase RLS, service keys, connection security, migrations |

---

## Risk Score Calculation

```
Risk Score = min(100, sum of:
  - Critical findings × 25
  - High findings × 10
  - Medium findings × 3
  - Low findings × 1
)
```

### Risk Level Interpretation

| Score | Level | Recommended Action |
|-------|-------|-------------------|
| 0-20 | Low Risk | Routine maintenance, schedule fixes |
| 21-50 | Moderate Risk | Prioritize high/critical items within 2 weeks |
| 51-80 | High Risk | Immediate attention needed, fix within days |
| 81-100 | Critical Risk | **Stop deployment**, fix critical issues before release |

---

## Fix Priority Order

Apply fixes in this order (safest first):

1. **Config-only**: Headers, CSP, CORS, rate limits, TLS settings
2. **Dependency bumps**: Semver-compatible (patch/minor), lockfile-only preferred
3. **Server-side validation wrappers**: Wrap existing function, guard input, same output
4. **Secret removal**: Move to env vars, update .gitignore
5. **Backend sanitization**: Parameterized queries, output encoding
6. **Privilege separation**: Extract to scoped functions
7. **Logging additions**: Audit events (non-observable to users)
8. **Error handler hardening**: Generic user message, detailed internal log
9. **Atomic operations**: Database transactions for race conditions
10. **Business logic guards**: Server-side checks, same user-visible flow
