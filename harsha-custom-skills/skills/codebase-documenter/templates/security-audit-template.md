# Security Audit Template

**Project**: {{PROJECT_NAME}} | **Audit Date**: {{DATE}} | **Auditor**: {{NAME}}

**Scope**: {{Full system | Specific modules | Third-party integrations | Incident post-mortem}}

---

## Executive Summary

{{2-3 paragraph assessment of security posture}}

**Overall Security Score**: {{SCORE}}/10 ({{LEVEL}}: STRONG | MODERATE | WEAK)

**Critical Findings**: {{COUNT}} | **High**: {{COUNT}} | **Medium**: {{COUNT}} | **Low**: {{COUNT}}

**Recommendation**: {{APPROVE_FOR_PRODUCTION | CONDITIONAL_APPROVAL | DO_NOT_DEPLOY}}

---

## Scope & Methodology

### What Was Audited

- [ ] Authentication mechanisms (SSO, API keys, MFA)
- [ ] Authorization & access control (RBAC, ABAC)
- [ ] Data protection (encryption at rest, in transit)
- [ ] API security (input validation, rate limiting)
- [ ] Infrastructure security (firewalls, network segmentation)
- [ ] Third-party integrations (vendor security, contracts)
- [ ] Incident response procedures
- [ ] Dependency vulnerabilities
- [ ] Secrets management
- [ ] Audit logging & monitoring

### Methodology

**Code Review**: {{Manual review of code | Automated scanning | Both}}

**Tools Used**: {{Tool 1}}, {{Tool 2}}, {{Tool 3}}

**Testing Performed**:
- Static analysis (SAST): {{Tool}}, found {{COUNT}} issues
- Dynamic analysis (DAST): {{Tool}}, found {{COUNT}} issues
- Dependency scanning: {{Tool}}, found {{COUNT}} vulnerabilities
- Penetration testing: {{Type}}, conducted {{Date}}

---

## Authentication & Authorization

### Current Implementation

**Authentication Method**: {{OAuth2 | SAML | API Key | mTLS | Multiple}}

**Identity Provider**: {{Provider name}}

**Details**:
- SSO integrated: ✓ Yes | ✗ No
- MFA enforcement: {{Required | Optional | Not implemented}}
- MFA methods: {{TOTP | SMS | Push | Biometric | Hardware key}}
- Backup codes: ✓ Yes | ✗ No
- Session timeout: {{Duration}}
- Token lifetime: {{Duration}}
- Token refresh: {{Mechanism}}

### RBAC/ABAC Policies

**Role Hierarchy**:
```
Admin (root)
  ├── Editor
  │   └── Viewer
  └── Operator
      └── Guest
```

**Permission Matrix**: {{Documented in}} `docs/permissions.md`

**Policy Enforcement**:
- ✓ Middleware-enforced
- ✓ Database-enforced
- ✗ Missing enforcement
- ⚠️ Partial enforcement

### Findings

**Finding 1**: {{VULNERABILITY/CONCERN}}

| Aspect | Details |
|--------|---------|
| **Severity** | 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW |
| **Type** | {{Type of vulnerability}} |
| **Description** | {{Detailed description}} |
| **Affected Code** | `src/{{path}}/{{file}}.{{ext}}`, Line {{START}} |
| **Proof of Concept** | {{How to demonstrate vulnerability}} |

**Remediation**:
```javascript
// Before (vulnerable)
{{VULNERABLE_CODE}}

// After (fixed)
{{SECURE_CODE}}
```

**Timeline**: {{Fix date}}, Owner: {{Person}}

---

**Finding 2**: {{VULNERABILITY}}

{{Same structure as Finding 1}}

---

## Data Protection

### Encryption at Rest

| Data Type | Algorithm | Key Management | Key Rotation | Compliance |
|-----------|-----------|---|---|---|
| User credentials | {{Algorithm}} | {{Location}} | {{Frequency}} | ✓ / ⚠️ / ✗ |
| PII (email, phone) | {{Algorithm}} | {{Location}} | {{Frequency}} | ✓ / ⚠️ / ✗ |
| Sensitive (API keys) | {{Algorithm}} | {{Location}} | {{Frequency}} | ✓ / ⚠️ / ✗ |
| Database | {{Algorithm}} | {{Location}} | {{Frequency}} | ✓ / ⚠️ / ✗ |
| Backups | {{Algorithm}} | {{Location}} | {{Frequency}} | ✓ / ⚠️ / ✗ |

### Encryption in Transit

| Channel | Protocol | TLS Version | Cipher Suites | Certificate Pinning |
|---------|----------|---|---|---|
| API | HTTPS | {{Version}} | {{Ciphers}} | ✓ Yes | ✗ No |
| Database | TLS | {{Version}} | {{Ciphers}} | ✓ Yes | ✗ No |
| Third-party APIs | HTTPS | {{Version}} | {{Ciphers}} | ✓ Yes | ✗ No |

**Findings**:

🔴 **CRITICAL**: TLS 1.2 not enforced in `src/server.js`
- Impact: Vulnerable to POODLE attacks
- Fix: Enable TLS 1.2 minimum in {{Config file}}
- Timeline: Immediate

🟡 **MEDIUM**: Weak cipher suites negotiated in production
- Impact: Reduced encryption strength
- Fix: Update cipher suite configuration
- Timeline: {{Date}}

---

## API Security

### Input Validation

| Endpoint | Input Type | Validation | Sanitization | Rate Limit |
|----------|-----------|-----------|---|---|
| `POST /api/users` | JSON | ✓ Yes | ✓ Yes | 100/min |
| `GET /api/users/:id` | Path | ✓ Yes | ✓ Yes | 1000/min |
| `PUT /api/users/:id` | JSON | ⚠️ Partial | ✓ Yes | 100/min |
| `DELETE /api/users/:id` | Path | ✗ No | ✓ Yes | 10/min |

**Finding**: `PUT /api/users/:id` endpoint missing input validation
- Code: `src/api/users.js`, line 245
- Risk: Injection attacks, XSS, malformed data
- Fix: Add schema validation using {{Library}}
- Timeline: {{Date}}

### SQL Injection Prevention

**Status**: ✓ PROTECTED | ⚠️ PARTIALLY | ✗ VULNERABLE

**Implementation**:
- ✓ Parameterized queries used
- ✓ ORM ({{ORM_NAME}}) prevents injection
- ⚠️ Some raw queries detected (10 locations)

**Locations with Raw Queries**:
1. `src/db/queries.js:50` — {{Query description}}
2. `src/db/queries.js:75` — {{Query description}}

**Fix**: Migrate to parameterized queries using {{ORM}}

### CSRF Protection

**Status**: ✓ IMPLEMENTED | ⚠️ INCOMPLETE | ✗ MISSING

**Implementation**:
- [ ] CSRF tokens generated for forms
- [ ] Token validation enforced
- [ ] SameSite cookie attribute set
- [ ] CORS properly configured

**Finding**: SameSite cookie attribute not set in `config/cookies.js`
- Impact: CSRF vulnerability
- Fix: Add `SameSite=Strict` to all cookies
- Timeline: Immediate

---

## Secrets Management

### Current Implementation

**Secrets Manager**: {{AWS Secrets Manager | HashiCorp Vault | Environment variables | Hardcoded ✗}}

**Secrets Storage**:
- [ ] Never in source code ✓
- [ ] Never in config files ✓
- [ ] Never in logs ⚠️
- [ ] Protected in transit ✓
- [ ] Protected at rest ✓

**Secrets Rotation**:
- API Keys: {{Frequency}}
- Database credentials: {{Frequency}}
- Encryption keys: {{Frequency}}

**Findings**:

🔴 **CRITICAL**: API key stored in `config/third-party.js`
```javascript
// Found in: config/third-party.js:15
const apiKey = 'sk_live_abc123xyz789...';  // LEAKED
```
- Action: Rotate API key immediately
- Prevention: Use environment variable
- Timeline: Immediately

🟡 **MEDIUM**: Passwords appear in debug logs
- Location: `.log` files contain credentials in error messages
- Fix: Implement credential masking in logger
- Timeline: {{Date}}

---

## Infrastructure Security

### Network Segmentation

**Current Architecture**:
```
[Internet] → [CDN/WAF] → [API Gateway] → [Services] → [Database]
                    ↓
                 [VPC]
                    ↓
            [Security Groups]
            [Network ACLs]
```

**Status**:
- ✓ VPC in place
- ✓ Subnets segmented (public/private)
- ✓ Security groups configured
- ⚠️ VPC Flow Logs not enabled
- ✗ Network ACLs overly permissive

**Finding**: Security group allows 0.0.0.0/0 to database port 5432
- Impact: Unauthorized database access possible
- Fix: Restrict to application tier only
- Timeline: Immediate

### WAF & DDoS Protection

**Status**: ✓ Enabled | ⚠️ Partial | ✗ Not enabled

- [ ] CloudFlare/AWS WAF enabled
- [ ] SQL injection rules active
- [ ] XSS protection active
- [ ] DDoS protection enabled
- [ ] Rate limiting configured
- [ ] Bot detection enabled

### Firewalls

| Firewall | Status | Config Location | Last Updated |
|----------|--------|---|---|
| {{Firewall}} | ✓ Active | `infra/firewall.yaml` | {{Date}} |
| {{Firewall}} | ⚠️ Misconfigured | `infra/firewall.yaml` | {{Date}} |

---

## Third-Party Integrations

### Dependency Vulnerabilities

**Scan Date**: {{Date}} | **Tool**: {{Tool}}

**Summary**: {{COUNT}} total dependencies, {{VULNERABLE_COUNT}} with known vulnerabilities

**Critical Vulnerabilities**:

| Package | Version | Vulnerability | CVSS | Fix Available |
|---------|---------|---|---|---|
| `{{package}}` | {{Version}} | {{CVE}} | 9.8 | Yes → {{Fix_Version}} |
| `{{package}}` | {{Version}} | {{CVE}} | 8.5 | Yes → {{Fix_Version}} |

**Action Items**:
1. Update `{{package}}` to version {{VERSION}} immediately
2. Update `{{package}}` to version {{VERSION}} before next release
3. Monitor `{{package}}` for security updates (no fix available yet)

**Scan Report**: {{Link to full dependency report}}

### Vendor Security Assessment

| Vendor | Service | Compliance | BAA | Reviewed |
|--------|---------|-----------|-----|----------|
| {{Vendor}} | {{Service}} | SOC2 | ✓ | {{Date}} |
| {{Vendor}} | {{Service}} | ISO27001 | ⚠️ Outdated | {{Date}} |
| {{Vendor}} | {{Service}} | Custom | — | {{Date}} |

**Finding**: {{Vendor}} compliance certificate expired on {{Date}}
- Impact: Can no longer rely on their security posture
- Action: Request updated certificate or migrate to alternative
- Timeline: {{Date}}

---

## Incident Response

### Incident Response Plan

**Status**: ✓ Documented | ⚠️ Incomplete | ✗ Not documented

**Incident Response Team**:
- **Incident Commander**: {{Name}} ({{Slack}})
- **Security Lead**: {{Name}} ({{Slack}})
- **Communications**: {{Name}} ({{Slack}})

**Key Procedures**:
1. **Detection**: {{How are incidents detected}}
2. **Triage**: {{Who decides severity}}
3. **Containment**: {{Initial steps to limit damage}}
4. **Eradication**: {{How to fix the root cause}}
5. **Recovery**: {{How to restore normal operation}}
6. **Lessons Learned**: {{Post-mortem within}} {{TIME_FRAME}}

### Past Incidents

| Date | Type | Severity | Root Cause | Resolution Time |
|------|------|----------|-----------|---|
| {{Date}} | {{Type}} | {{Severity}} | {{Cause}} | {{Duration}} |
| {{Date}} | {{Type}} | {{Severity}} | {{Cause}} | {{Duration}} |

**Finding**: No documented postmortem for {{Date}} incident
- Action: Schedule postmortem and document learnings
- Timeline: {{Date}}

---

## Pre-Mortem: Potential Security Failures

**What could go wrong in the next 6 months?**

1. **Database Breach**
   - Likelihood: MEDIUM
   - Impact: CRITICAL (all customer data exposed)
   - Mitigation: Implement encryption, restrict access, audit logs
   - Owner: {{Person}}, Timeline: {{Date}}

2. **Supply Chain Attack (Dependency)**
   - Likelihood: MEDIUM
   - Impact: CRITICAL (code execution in production)
   - Mitigation: Dependency scanning, pinned versions, SBOM
   - Owner: {{Person}}, Timeline: {{Date}}

3. **Secrets Leaked via Logs**
   - Likelihood: HIGH
   - Impact: HIGH (API keys, database credentials exposed)
   - Mitigation: Credential masking in logs, secret scanning on commits
   - Owner: {{Person}}, Timeline: {{Date}}

4. **Unauthorized API Access**
   - Likelihood: MEDIUM
   - Impact: HIGH (customer data accessed without authorization)
   - Mitigation: API authentication/authorization, rate limiting
   - Owner: {{Person}}, Timeline: {{Date}}

5. **Configuration Drift**
   - Likelihood: HIGH
   - Impact: MEDIUM (security groups, IAM policies become misconfigured)
   - Mitigation: IaC enforcement, regular audits, GitOps workflow
   - Owner: {{Person}}, Timeline: {{Date}}

---

## Audit Logging & Monitoring

### Audit Logs

**What's Logged**:
- ✓ User login/logout
- ✓ API calls (method, path, user, timestamp)
- ✓ Data access (who accessed what, when)
- ✓ Configuration changes (what changed, who changed it)
- ⚠️ Failed access attempts (incomplete)
- ✗ Secrets access (not logged)

**Retention**: {{Duration}} ({{Legal basis}})

**Immutability**: ✓ Guaranteed | ⚠️ Partial | ✗ Not enforced

**Finding**: Audit logs stored in mutable database without tamper detection
- Impact: Attacker could cover tracks by modifying logs
- Fix: Move logs to immutable append-only store (S3 with Object Lock)
- Timeline: {{Date}}

### Monitoring & Alerting

| Alert | Threshold | Action |
|---|---|---|
| {{Alert}} | {{Threshold}} | {{Response}} |
| {{Alert}} | {{Threshold}} | {{Response}} |

**Finding**: No alert for suspicious API access patterns
- Implement: Anomaly detection on API call frequency/patterns
- Timeline: {{Date}}

---

## Compliance Status

| Standard | Status | Last Audit |
|----------|--------|-----------|
| {{Standard}} | ✓ Compliant | {{Date}} |
| {{Standard}} | ⚠️ Partial | {{Date}} |
| {{Standard}} | ✗ Non-compliant | {{Date}} |

---

## Remediation Plan

### Critical (Fix Immediately)

- [ ] {{Finding 1}} — Owner: {{Person}}, Deadline: {{ASAP}}
- [ ] {{Finding 2}} — Owner: {{Person}}, Deadline: {{ASAP}}

### High (Fix Before Production)

- [ ] {{Finding}} — Owner: {{Person}}, Deadline: {{Date}}
- [ ] {{Finding}} — Owner: {{Person}}, Deadline: {{Date}}

### Medium (Fix Within 30 Days)

- [ ] {{Finding}} — Owner: {{Person}}, Deadline: {{Date}}
- [ ] {{Finding}} — Owner: {{Person}}, Deadline: {{Date}}

### Low (Fix Within 90 Days)

- [ ] {{Finding}} — Owner: {{Person}}, Deadline: {{Date}}

---

## Approval & Sign-Off

### Security Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| **Security Lead** | {{Name}} | Approved / Conditional / Rejected | {{Date}} |
| **Compliance Officer** | {{Name}} | Approved / Conditional / Rejected | {{Date}} |
| **Engineering Lead** | {{Name}} | Approved / Conditional / Rejected | {{Date}} |

**Comments**: {{Any conditions or concerns}}

### Recommendation

{{APPROVE | CONDITIONAL_APPROVAL | DO_NOT_DEPLOY}}

**Rationale**: {{Explanation of recommendation}}

---

## Appendix: Tools & Techniques

**SAST Tools Used**:
- {{Tool}}: {{Config/findings}}
- {{Tool}}: {{Config/findings}}

**DAST Tools Used**:
- {{Tool}}: {{Config/findings}}
- {{Tool}}: {{Config/findings}}

**Dependency Scanners**:
- {{Tool}}: {{Version}}, {{Scan results}}

**Manual Testing**:
- Code review: {{Hours spent}}, {{Reviewer names}}
- Penetration testing: {{Scope}}, {{Findings}}

---

**Audit Report Version**: {{VERSION}} | **Date**: {{DATE}} | **Auditor**: {{NAME}} | **Status**: {{DRAFT | FINAL | APPROVED}}

**Next Audit**: {{DATE}}
