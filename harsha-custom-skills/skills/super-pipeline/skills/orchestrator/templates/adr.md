# Architecture Decision Record (ADR) Template

Use this template when making decisions that affect architecture, structure, dependencies, 
interfaces, or construction techniques.

---

## Template

```markdown
# ADR-[NUMBER]: [Short Title Describing the Decision]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Date
[YYYY-MM-DD when decision was made]

## Context
[Describe the forces at play—technical, political, social, project-local. 
Write in value-neutral language. What is the issue that motivates this decision?
What constraints exist? What requirements drive this?]

## Decision
We will [decision statement in active voice].

[Expand on the decision with 2-4 sentences explaining the approach.
Be specific about what will be done and how.]

## Consequences

### Positive
- [Good outcome 1]
- [Good outcome 2]
- [Good outcome 3]

### Negative
- [Tradeoff, cost, or risk 1]
- [Tradeoff, cost, or risk 2]

### Neutral
- [Side effect that's neither good nor bad]

## Alternatives Considered

### [Alternative 1 Name]
[Brief description]
**Why rejected**: [Reason]

### [Alternative 2 Name]
[Brief description]
**Why rejected**: [Reason]

## Related
- [Link to related ADR]
- [Link to relevant documentation]
- [Link to implementation task]
```

---

## Filled Example

```markdown
# ADR-003: Use JWT for API Authentication

## Status
Accepted

## Date
2024-01-15

## Context
Our REST API needs authentication for protected endpoints. The frontend is a 
single-page application that will communicate with the API. We need a stateless
authentication mechanism that:
- Works across multiple API server instances (load balanced)
- Doesn't require server-side session storage
- Supports token refresh without full re-authentication
- Can encode user permissions for authorization checks

The team has experience with both session-based and token-based authentication.
Current infrastructure uses Redis for caching, which could support sessions if needed.

## Decision
We will use JSON Web Tokens (JWT) for API authentication.

Tokens will be signed using RS256 (asymmetric) algorithm to enable verification
without sharing the signing key. Access tokens will expire after 15 minutes,
with refresh tokens valid for 7 days. Tokens will include user ID and roles
in the payload for authorization without database lookups.

## Consequences

### Positive
- Stateless authentication enables horizontal scaling without session affinity
- Token payload enables authorization checks without database queries
- Standard format with excellent library support across languages
- Asymmetric signing allows separate signing and verification services

### Negative
- Cannot invalidate individual tokens before expiry (requires blacklist)
- Token size larger than session ID (impacts header size)
- Must implement token refresh logic in frontend
- RS256 slightly slower than HS256

### Neutral
- Will need to store refresh tokens in database for revocation
- Frontend must handle token storage (likely localStorage)

## Alternatives Considered

### Session-based Authentication with Redis
Store sessions in Redis, use session cookie.
**Why rejected**: Would require sticky sessions or shared session store, adds
operational complexity, doesn't encode authorization data.

### OAuth 2.0 with External Provider
Use Auth0 or Okta for authentication.
**Why rejected**: Adds external dependency, cost concerns at scale, team
comfortable implementing JWT ourselves.

### HS256 Signed JWTs
Use symmetric key (HS256) instead of asymmetric (RS256).
**Why rejected**: Would require sharing signing key with any service that
verifies tokens, less secure in distributed system.

## Related
- ADR-004: Refresh Token Strategy
- Task #16: Implement JWT authentication
- docs/auth/jwt-flow.md
```

---

## When to Write an ADR

**Essential** when decision affects:
- ☐ System structure or architecture
- ☐ Non-functional characteristics (performance, security, scalability)
- ☐ External dependencies or integrations
- ☐ Public interfaces or contracts
- ☐ Development or deployment approach
- ☐ First-of-a-kind technology choices
- ☐ Cross-cutting concerns

**Overkill** for:
- Limited-scope implementation details
- Temporary workarounds (document differently)
- Decisions that can change without architectural impact
- When commit messages sufficiently capture the "why"

---

## ADR Best Practices

### Writing
- Keep to 1-2 pages maximum
- Write in full sentences, active voice ("We will..." not "It was decided...")
- Use value-neutral language in Context section
- Be explicit about trade-offs in Consequences
- Always include Alternatives Considered

### Storage
- Store in `docs/decisions/` with sequential numbering
- Example: `0001-use-postgresql.md`, `0002-jwt-authentication.md`
- Numbers are never reused
- Superseded ADRs remain with updated Status—never delete

### Lifecycle
- Start as "Proposed" for team discussion
- Move to "Accepted" after agreement
- Update to "Superseded by ADR-XXX" when replaced
- Never delete—maintain decision archaeology

### Linking
- Link to related ADRs
- Link to implementation tasks
- Consequences of one ADR become Context for subsequent ADRs
