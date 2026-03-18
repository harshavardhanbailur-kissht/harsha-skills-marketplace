---
description: Exhaustive multi-domain security audit across OWASP Top 10, CWE Top 25, and 15 security domains — non-invasive fixes only
argument-hint: "<path to codebase or repo>"
---

# /security-audit — Codebase Security Audit

Performs comprehensive, non-invasive security analysis across 15 domains including injection, XSS, authentication, cryptography, secrets, dependencies, Supabase RLS, and more.

## Invocation

```
/security-audit ./src
/security-audit [point to a repo or folder]
```

## Workflow

Load the `security-audit` skill and execute the multi-domain audit pipeline. All fixes preserve existing UI/UX and API contracts.
