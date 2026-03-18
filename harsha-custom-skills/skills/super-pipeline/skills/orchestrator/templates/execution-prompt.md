# Execution Prompt Template

Use this template for creating self-contained prompts that execute reliably in fresh context windows.

---

## Template

```markdown
# [Task Title - Verb + Object + Purpose]

## Intent
[One sentence: WHY this task matters and what success enables]
If we accomplish nothing else: [the ONE non-negotiable requirement]

## Context
**Tech Stack**: [Language/version, frameworks/versions, key dependencies]
**Environment**: [Dev/prod, OS, runtime constraints]
**Current State**: [What exists now relevant to this task]

## Existing Code Reference
```[language]
// [filepath]
[Relevant code snippet showing patterns to follow]
```

## Task
[Single, clear objective statement]

### Requirements
- [Specific requirement 1]
- [Specific requirement 2]

### Constraints
- **MUST**: [Required approaches/patterns]
- **MUST NOT**: [Explicitly forbidden approaches]
- **SHOULD**: [Preferred but flexible]

## Interface Contract
**Input**: [What the code receives, with types]
**Output**: [What the code returns, with types]
**Errors**: [How errors should be handled/surfaced]

## Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Verification step - e.g., "All tests pass"]

## Out of Scope
- [Explicit exclusion 1]
- [Explicit exclusion 2]
```

---

## Filled Example

```markdown
# Implement JWT Authentication Middleware

## Intent
Enable protected API routes by validating JWT tokens on incoming requests.
If we accomplish nothing else: Invalid tokens must return 401 before reaching route handlers.

## Context
**Tech Stack**: Node 20, Express 4.18, TypeScript 5.3, jsonwebtoken 9.0
**Environment**: Development, Docker container, PostgreSQL 15
**Current State**: Unprotected API with User model (id, email, passwordHash)

## Existing Code Reference
```typescript
// src/services/user.service.ts (pattern to follow)
export async function getUserById(id: string): Promise<ServiceResult<User>> {
  const user = await prisma.user.findUnique({ where: { id } });
  if (!user) return { success: false, error: 'User not found' };
  return { success: true, data: user };
}
```

## Task
Create JWT authentication middleware that validates tokens and attaches user to request.

### Requirements
- Validate JWT from Authorization header (Bearer token format)
- Decode token and fetch user from database
- Attach user object to req.user for downstream handlers
- Handle expired tokens with appropriate error

### Constraints
- **MUST**: Use jsonwebtoken library for validation
- **MUST**: Store JWT_SECRET in environment variable
- **MUST NOT**: Modify existing User model
- **SHOULD**: Follow existing service return pattern

## Interface Contract
**Input**: Express Request with Authorization header
**Output**: Calls next() with req.user populated, or returns 401 response
**Errors**: 
- Missing token → 401 with { error: "No token provided" }
- Invalid token → 401 with { error: "Invalid token" }
- Expired token → 401 with { error: "Token expired" }

## Success Criteria
- [ ] Middleware compiles without TypeScript errors
- [ ] Valid token → req.user contains user object
- [ ] Invalid token → 401 response, route handler never called
- [ ] Unit tests cover: valid token, missing token, expired token, invalid token
- [ ] Integration test verifies protected route behavior

## Out of Scope
- Token refresh mechanism
- OAuth/social login
- Session management
- Password reset flow
```

---

## Checklist Before Using

- [ ] **Mission clarity**: Single objective in first paragraph?
- [ ] **Context complete**: Tech stack with versions? Relevant code included?
- [ ] **Assumptions eliminated**: No pronouns without antecedents? No "as we discussed"?
- [ ] **Structure verified**: Critical info in first 20%? Under 2000 tokens?
- [ ] **Fresh context test**: Would someone unfamiliar understand completely?
