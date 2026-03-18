# Task Definition Template

Use this template for creating unambiguous, independently-executable task entries.

---

## Template

```markdown
## Task #[NUMBER]: [Action Verb] + [Specific Object] + [Scope Boundary]

**Type**: Implementation | Bug Fix | Research | Documentation | Refactoring
**Size**: S (<2hr) | M (2-4hr) | L (4-8hr)
**Phase**: [Project phase this belongs to]

### Context
[Why this task exists. What preceded it. Any relevant decisions already made.
Link to related ADRs if applicable.]

### Done When
- [ ] [Binary criterion 1 - must be yes/no verifiable]
- [ ] [Binary criterion 2]
- [ ] [Binary criterion 3]
- [ ] [Verification step - e.g., "All tests pass"]

### Not Included
- [Explicit exclusion 1]
- [Explicit exclusion 2]

### Blocked By
- [Task #X: Description] (if any)

### References
- [Link to relevant code/files]
- [Link to relevant ADR]
- [Link to relevant documentation]

### Notes
[Any additional context, warnings, or tips for the executor]
```

---

## Filled Example

```markdown
## Task #16: Implement User Registration Endpoint with Email Validation

**Type**: Implementation
**Size**: M (2-4hr)
**Phase**: Phase 2 - Authentication

### Context
Part of the authentication module. This is the first user-facing auth endpoint.
Frontend team expects POST /api/auth/register returning { user, token }.
Uses existing User model from Task #14.
See ADR-003 for JWT token decision.

### Done When
- [ ] POST /api/auth/register accepts { email, password, name }
- [ ] Email format validated (returns 400 for invalid)
- [ ] Password hashed with bcrypt before storage
- [ ] Duplicate email returns 409 Conflict
- [ ] Success returns 201 with { user: { id, email, name }, token: JWT }
- [ ] Unit tests cover: success, invalid email, duplicate, weak password
- [ ] Endpoint documented in OpenAPI spec

### Not Included
- Email verification/confirmation flow
- Password strength requirements beyond minimum length
- Rate limiting (handled in Task #22)
- Social login options

### Blocked By
- Task #14: Create User model and migrations
- Task #15: Set up database connection

### References
- User model: `src/models/user.ts`
- Service pattern: `src/services/user.service.ts`
- ADR-003: JWT Authentication Decision

### Notes
- Follow existing service return pattern { success, data, error }
- JWT_SECRET must be in .env (see .env.example)
- Frontend expects exact response shape - coordinate if changes needed
```

---

## Task Definition Checklist

**Pickup Test**: Can someone unfamiliar with the project understand what to do and verify completion?

### Clarity
- [ ] Starts with action verb (Write, Create, Implement, Fix, etc.)
- [ ] Single, unambiguous objective
- [ ] Scope boundaries explicit

### Completeness  
- [ ] Context explains why task exists
- [ ] All dependencies listed
- [ ] References to relevant code/docs included

### Verifiability
- [ ] Every "Done When" criterion is binary (yes/no)
- [ ] No subjective terms ("good", "fast", "proper")
- [ ] Includes verification step (tests pass, review approved, etc.)

### Boundaries
- [ ] "Not Included" section present
- [ ] Explicit about what adjacent work is excluded
- [ ] Scope appropriate for size estimate

---

## Size Estimation Guide

| Size | Time | Characteristics |
|------|------|-----------------|
| **S** | <2 hours | Single-file change, clear approach, no research needed |
| **M** | 2-4 hours | Multiple files, some decisions, tests required |
| **L** | 4-8 hours | Significant feature, multiple components, integration |

**If estimated >8 hours**: Break into smaller tasks. Target 2-4 hours per task.

---

## Common Mistakes to Avoid

| Mistake | Example | Fix |
|---------|---------|-----|
| No verb | "Authentication" | "Implement authentication endpoint" |
| Vague completion | "Works correctly" | "Returns 200 for valid input" |
| Hidden dependencies | Missing blockers | Map all data/state dependencies |
| Scope creep | No "Not Included" | Explicit exclusions |
| Subjective criteria | "Good performance" | "Response time <200ms" |
