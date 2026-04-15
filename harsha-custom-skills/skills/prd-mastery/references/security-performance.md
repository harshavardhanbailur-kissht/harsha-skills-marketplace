# Security & Performance Requirements

Complete reference for specifying security and performance requirements in PRDs.

---

## Security Requirements Framework

### OWASP Integration

**OWASP Application Security Verification Standard (ASVS)**
- Identifier format: `v<version>-<chapter>.<section>.<requirement>`
- Enables traceable security requirements

**OWASP Top 10 (2021) Mapping**
| Risk | PRD Requirement Category |
|------|--------------------------|
| A01 Broken Access Control | Authorization requirements |
| A02 Cryptographic Failures | Encryption requirements |
| A03 Injection | Input validation requirements |
| A04 Insecure Design | Security architecture requirements |
| A05 Security Misconfiguration | Deployment/config requirements |
| A06 Vulnerable Components | Dependency requirements |
| A07 Auth Failures | Authentication requirements |
| A08 Integrity Failures | Data integrity requirements |
| A09 Logging Failures | Audit logging requirements |
| A10 SSRF | Network security requirements |

---

## Threat Modeling (STRIDE)

| Threat | Requirement Category | Example Requirement |
|--------|---------------------|---------------------|
| **S**poofing | Authenticity | MFA required for admin access |
| **T**ampering | Integrity | Digital signatures for data at rest |
| **R**epudiation | Non-repudiability | Immutable audit logs |
| **I**nformation Disclosure | Confidentiality | Encryption in transit and at rest |
| **D**enial of Service | Availability | Rate limiting, DDoS protection |
| **E**levation of Privilege | Authorization | Least privilege access |

---

## Authentication Requirements

### Specification Template
```markdown
## Authentication Requirements

### Authentication Methods
- [ ] Username/password
- [ ] OAuth 2.0 with PKCE (for public clients)
- [ ] SAML 2.0 (enterprise SSO)
- [ ] Passwordless (magic link, WebAuthn)
- [ ] Social login (Google, Apple, etc.)

### Password Policy
- Minimum length: 12 characters
- Complexity: Mix of character types recommended, not required
- Check against breached password databases (HaveIBeenPwned)
- No periodic forced rotation (per NIST 800-63B)

### Multi-Factor Authentication
- Required for: [admin accounts, high-value transactions, etc.]
- Supported factors:
  - [ ] TOTP (authenticator apps)
  - [ ] SMS (not recommended for high-security)
  - [ ] Hardware keys (FIDO2/WebAuthn)
  - [ ] Push notifications

### Token Management
| Token Type | Expiration | Storage |
|------------|------------|---------|
| Access token | 10-60 minutes | Memory only |
| Refresh token | 7-30 days | Secure HTTP-only cookie |
| Session token | [duration] | [storage method] |

### Session Management
- Idle timeout: [duration]
- Absolute timeout: [duration]
- Concurrent session limit: [number or unlimited]
- Session invalidation on password change: Required

### Step-Up Authentication
- Triggers: [high-value actions requiring re-authentication]
- ACR claims for authentication level verification
```

---

## Authorization Requirements

### Specification Template
```markdown
## Authorization Requirements

### Access Control Model
- [ ] RBAC (Role-Based Access Control) - NIST INCITS 359-2012
- [ ] ABAC (Attribute-Based Access Control) - NIST SP 800-162
- [ ] ReBAC (Relationship-Based Access Control)

### Role Definitions
| Role | Description | Permissions |
|------|-------------|-------------|
| Admin | Full system access | All |
| Manager | Team management | [list] |
| User | Standard access | [list] |
| Viewer | Read-only | [list] |

### Permission Model
- Resource-based permissions
- Hierarchical role inheritance
- Separation of duties requirements

### Multi-Tenancy
- Tenant isolation mechanism: [row-level, schema-level, database-level]
- Cross-tenant access: Explicitly prohibited unless [exceptions]
- Tenant context validation on every request

### API Authorization
- Authorization header: Bearer token
- Scope-based permissions for OAuth
- API key management for service accounts
```

---

## Data Protection Requirements

### Encryption Specifications
```markdown
## Encryption Requirements

### Data at Rest
- Algorithm: AES-256-GCM
- Key management: [AWS KMS, Azure Key Vault, HashiCorp Vault]
- Key rotation: Annual minimum, immediate on compromise

### Data in Transit
- TLS 1.2 minimum, TLS 1.3 preferred
- HSTS header required
- Certificate pinning for mobile apps (optional)

### Field-Level Encryption
| Data Type | Encryption Required | Algorithm |
|-----------|---------------------|-----------|
| SSN | Yes | AES-256-GCM |
| Credit Card | Yes (PCI-DSS) | AES-256-GCM |
| Password | Hash only | Argon2id |
| PII | [Per classification] | [Per policy] |

### Key Management
- HSM-backed key storage for production
- Separate keys per environment
- Key access audit logging
```

### Data Classification
```markdown
## Data Classification

| Level | Description | Handling Requirements |
|-------|-------------|----------------------|
| Public | No restrictions | Standard controls |
| Internal | Company confidential | Access controls |
| Confidential | Customer data, PII | Encryption, logging |
| Restricted | Financial, health | Full controls, audit |
```

---

## Audit Logging Requirements

```markdown
## Audit Logging Requirements

### Events to Log
- Authentication events (login, logout, failed attempts)
- Authorization failures
- Data access (read, create, update, delete)
- Administrative actions
- Configuration changes
- Security events

### Log Format
```json
{
  "timestamp": "ISO 8601 format",
  "event_type": "string",
  "actor": {
    "user_id": "string",
    "ip_address": "string",
    "user_agent": "string"
  },
  "resource": {
    "type": "string",
    "id": "string"
  },
  "action": "string",
  "outcome": "success|failure",
  "metadata": {}
}
```

### Log Requirements
- Immutable storage (append-only)
- Retention period: [requirement, typically 1-7 years]
- Tamper-evident logging
- Centralized log aggregation
- Real-time alerting on security events
- Log access restricted and audited
```

---

## Performance Requirements

### Latency Specifications

**Use Percentiles, Not Averages**
> A 50ms average can hide 2500ms spikes.

```markdown
## Latency Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| P50 (median) | ≤50ms | Typical user experience |
| P95 | ≤200ms | Performance under load |
| P99 | ≤500ms | Tail latency threshold |
| P99.9 | ≤1000ms | Extreme outliers |

### By Operation Type
| Operation | P50 | P99 |
|-----------|-----|-----|
| API read | 50ms | 200ms |
| API write | 100ms | 500ms |
| Page load (LCP) | 1.5s | 2.5s |
| Search | 100ms | 300ms |
| File upload | [size-dependent] | [spec] |

### Load Conditions
- Normal load: [X requests/second]
- Peak load: [Y requests/second]
- Requirements apply under [load condition]
```

### Throughput Specifications
```markdown
## Throughput Requirements

| Metric | Target |
|--------|--------|
| Requests per second | [number] |
| Transactions per second | [number] |
| Concurrent users | [number] |
| Peak concurrent connections | [number] |

### Growth Projections
| Timeframe | Expected Load | Headroom |
|-----------|---------------|----------|
| Launch | [baseline] | 2x |
| 6 months | [projection] | 2x |
| 12 months | [projection] | 2x |
```

---

## Scalability Requirements

```markdown
## Scalability Requirements

### Horizontal Scaling
- Stateless application tier
- Session externalization (Redis, etc.)
- Load balancer requirements

### Vertical Limits
- Maximum instance size before horizontal scaling required
- Memory limits per instance
- CPU limits per instance

### Auto-Scaling Policies
| Metric | Scale Up | Scale Down |
|--------|----------|------------|
| CPU | >70% for 5 min | <30% for 10 min |
| Memory | >80% for 5 min | <40% for 10 min |
| Request queue | >100 pending | <10 pending |

### Data Scalability
- Database sharding strategy (if needed)
- Read replica requirements
- Caching layer specifications
```

---

## Availability Requirements

### SLA Specifications
```markdown
## Availability Requirements

### SLA Target
| Level | Uptime | Downtime/Year | Downtime/Month |
|-------|--------|---------------|----------------|
| 99.0% | | 3.65 days | 7.31 hours |
| 99.9% | | 8.76 hours | 43.83 minutes |
| 99.95% | | 4.38 hours | 21.92 minutes |
| 99.99% | | 52.60 minutes | 4.38 minutes |

**Target SLA:** [X]%

### Measurement
- Measurement period: Rolling 30 days
- Measurement method: Synthetic monitoring from [regions]
- Exclusions: Scheduled maintenance with [X hours] notice

### SLA Credits (if applicable)
| Uptime | Credit |
|--------|--------|
| 99.0-99.9% | 10% |
| 95.0-99.0% | 25% |
| <95.0% | 50% |
```

### Disaster Recovery
```markdown
## Disaster Recovery Requirements

| Metric | Target | Definition |
|--------|--------|------------|
| RTO | [hours] | Recovery Time Objective |
| RPO | [hours] | Recovery Point Objective |
| MTTR | [hours] | Mean Time To Recovery |

### Backup Requirements
- Backup frequency: [hourly/daily/weekly]
- Backup retention: [duration]
- Backup testing: [frequency]
- Geographic redundancy: [requirements]

### Failover
- Automatic failover: [yes/no]
- Failover time: [target]
- Failover testing: [frequency]
```

---

## Caching & CDN Requirements

```markdown
## Caching Requirements

### CDN
- Provider: [Cloudflare, CloudFront, Fastly, etc.]
- Edge locations: [geographic coverage]
- Cache hit ratio target: [%]

### Application Cache
| Cache Type | TTL | Invalidation |
|------------|-----|--------------|
| Static assets | 1 year | Version hash |
| API responses | [duration] | [strategy] |
| Session data | [duration] | [strategy] |
| Database queries | [duration] | [strategy] |

### Cache Headers
- Cache-Control directives
- ETag support
- Vary header usage
```

---

## Rate Limiting Requirements

```markdown
## Rate Limiting

### API Limits
| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Public API | 100 | 1 minute |
| Authenticated API | 1000 | 1 minute |
| Webhook delivery | 10 | 1 second |
| Bulk operations | 10 | 1 hour |

### Response Behavior
- HTTP 429 with Retry-After header
- X-RateLimit-* headers for quota visibility

### Bypass
- Internal services: [authentication method]
- Premium tier: [elevated limits]
```

---

## Security PRD Section Template

```markdown
## Security Requirements

### Classification
- Data sensitivity: [Public | Internal | Confidential | Restricted]
- Compliance requirements: [GDPR, HIPAA, PCI-DSS, SOC 2, etc.]

### Authentication
[Specify per templates above]

### Authorization
[Specify per templates above]

### Data Protection
[Specify per templates above]

### Audit & Logging
[Specify per templates above]

### Penetration Testing
- Pre-launch pentest: Required
- Frequency: [Annual, after major changes]
- Scope: [Full application, API only, etc.]

### Security Review Checklist
- [ ] Threat model completed
- [ ] Security architecture reviewed
- [ ] Authentication mechanism approved
- [ ] Data classification documented
- [ ] Encryption requirements met
- [ ] Audit logging implemented
- [ ] Penetration test scheduled
```
