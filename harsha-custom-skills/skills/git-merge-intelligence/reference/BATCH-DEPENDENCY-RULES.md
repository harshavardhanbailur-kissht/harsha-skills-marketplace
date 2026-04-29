# Batch Dependency Rules

Rules for ordering conflicted files into dependency-safe resolution batches. Load during Phases 2-3.

---

## Core Principle

**Resolve dependencies before dependents.** A file that exports types, functions, or configuration consumed by other files must be resolved first. Resolution errors in foundation files cascade to all dependents.

---

## Batch Hierarchy

```
Batch 0: Foundation (configs, lockfiles, build tools)
    ↓ depends on nothing
Batch 1: Types & Interfaces (type definitions, schemas, contracts)
    ↓ depends on Batch 0 (tsconfig, go.mod affect type resolution)
Batch 2: Shared Utilities & Middleware (utils, helpers, auth middleware)
    ↓ depends on Batch 0-1 (uses types, configured by build tools)
Batch 3: Implementations (components, handlers, services, pages)
    ↓ depends on Batch 0-2 (uses types + utilities)
Batch 4: Tests
    ↓ depends on Batch 0-3 (tests the implementations)
Batch 5: Docs & CI
    ↓ depends on nothing at runtime (but references Batch 0-3 content)
```

---

## Batch 0: Foundation — File Patterns

These files affect everything downstream. Resolve first, always.

| Pattern | Examples | Resolution Default |
|---------|----------|-------------------|
| Package manifests | `package.json`, `go.mod`, `pyproject.toml`, `Cargo.toml` | MANUAL_MERGE (deep merge versions) |
| Lock files | `package-lock.json`, `yarn.lock`, `go.sum`, `poetry.lock` | REGENERATE (never manual) |
| TypeScript config | `tsconfig.json`, `tsconfig.*.json` | MANUAL_MERGE |
| Build tool config | `vite.config.*`, `webpack.config.*`, `rollup.config.*` | MANUAL_MERGE |
| CSS tooling | `tailwind.config.*`, `postcss.config.*` | KEEP_BOTH (merge plugins/content) |
| Test config | `vitest.config.*`, `jest.config.*`, `pytest.ini` | MANUAL_MERGE |
| Container config | `Dockerfile`, `docker-compose.yml` | MANUAL_MERGE |
| CI/CD config | `.github/workflows/*`, `.gitlab-ci.yml` | MANUAL_MERGE |
| Environment | `.env.example`, `.env.template` | MANUAL_MERGE |
| Cloud config | `amplify.yml`, `serverless.yml`, `terraform/*.tf` | MANUAL_MERGE |

**Gate Rule**: Batch 1 MUST NOT start until Batch 0 is fully resolved and validated.

---

## Batch 1: Types & Interfaces — File Patterns

Type definitions consumed by implementation code.

| Pattern | Examples | Resolution Default |
|---------|----------|-------------------|
| TypeScript declarations | `*.d.ts`, `src/types/**/*.ts` | MANUAL_MERGE (merge type extensions) |
| Interfaces | `src/interfaces/**/*` | MANUAL_MERGE |
| Schemas | `src/schemas/**/*`, `*.schema.ts` | MANUAL_MERGE |
| Protobuf | `*.proto`, `*.pb.ts`, `*.pb.go` | MANUAL_MERGE |
| GraphQL | `*.graphql`, `schema.graphql` | MANUAL_MERGE |
| API contracts | `src/api/types.ts`, `contracts/*` | DEEP_THINK (cross-language risk) |
| Go types | `internal/types/*.go`, `pkg/models/*.go` | MANUAL_MERGE |
| Database models | `src/models/**/*`, `internal/models/**/*` | MANUAL_MERGE |

**Gate Rule**: Batch 2 MUST NOT start until Batch 1 passes `tsc --noEmit` / `go build`.

---

## Batch 2: Shared Utilities & Middleware

Code imported by many modules.

| Pattern | Examples | Resolution Default |
|---------|----------|-------------------|
| Utilities | `src/utils/**/*`, `src/helpers/**/*`, `pkg/utils/**/*` | MANUAL_MERGE |
| Middleware | `src/middleware/**/*`, `internal/middleware/**/*` | MANUAL_MERGE |
| Auth utilities | `src/auth/**/*` | DEEP_THINK (security) |
| Context providers | `src/context/**/*`, `src/providers/**/*` | MANUAL_MERGE |
| Hooks (shared) | `src/hooks/**/*` | MANUAL_MERGE |
| Libraries | `src/lib/**/*`, `pkg/**/*` | MANUAL_MERGE |
| Lambda layers | `layers/**/*` | MANUAL_MERGE |
| Lambda authorizers | `lambda/authorizer/**/*` | DEEP_THINK (security) |

**Gate Rule**: Run `tsc --noEmit` after Batch 2 to catch type errors before implementations.

---

## Batch 3: Implementations

Feature code that consumes types, utilities, and middleware.

| Pattern | Examples | Resolution Default |
|---------|----------|-------------------|
| React components | `src/components/**/*.tsx` | MANUAL_MERGE |
| Pages/routes | `src/pages/**/*`, `src/routes/**/*` | MANUAL_MERGE |
| API handlers | `src/api/**/*`, `internal/handlers/**/*` | MANUAL_MERGE |
| Services | `src/services/**/*`, `internal/services/**/*` | MANUAL_MERGE |
| Go commands | `cmd/**/*.go` | MANUAL_MERGE |
| Lambda functions | `lambda/*/index.ts`, `lambda/*/handler.go` | MANUAL_MERGE |
| State management | `src/store/**/*`, `src/redux/**/*` | MANUAL_MERGE |

**This is typically the largest batch.** For HEAVY mode (41+ files), consider sub-batching:
- Batch 3a: Core services (imported by other services)
- Batch 3b: Feature implementations (leaf nodes)
- Batch 3c: UI components (leaf nodes)

---

## Batch 4: Tests

Test files are resolved last because they validate implementations.

| Pattern | Examples | Resolution Default |
|---------|----------|-------------------|
| Unit tests | `*.test.ts`, `*.test.tsx`, `*_test.go` | MANUAL_MERGE |
| Spec files | `*.spec.ts`, `*.spec.tsx` | MANUAL_MERGE |
| Test directories | `__tests__/**/*`, `tests/**/*`, `test/**/*` | MANUAL_MERGE |
| Fixtures | `__fixtures__/**/*`, `testdata/**/*` | KEEP_BOTH |
| Mocks | `__mocks__/**/*`, `src/mocks/**/*` | MANUAL_MERGE |
| E2E tests | `e2e/**/*`, `cypress/**/*`, `playwright/**/*` | MANUAL_MERGE |

**Key Rule**: Resolve test fixtures (Batch 4) AFTER implementation (Batch 3), because tests depend on implementation behavior.

---

## Batch 5: Docs & CI

Non-runtime files resolved last.

| Pattern | Examples | Resolution Default |
|---------|----------|-------------------|
| Documentation | `docs/**/*.md`, `*.md` | KEEP_BOTH |
| READMEs | `README.md`, `CONTRIBUTING.md` | MANUAL_MERGE |
| Changelogs | `CHANGELOG.md` | KEEP_BOTH (chronological) |
| Static assets | `public/**/*`, `static/**/*` | KEEP_BOTH |
| CI workflows | `.github/workflows/*` (if not in Batch 0) | MANUAL_MERGE |
| Astro/Starlight docs | `src/content/docs/**/*` | KEEP_BOTH |

---

## Dependency Detection Commands

### TypeScript
```bash
# Extract imports from a file
grep -E "^import|^export.*from|^require" "$FILE" | \
  sed -E "s|.*from ['\"]([^'\"]+)['\"].*|\1|"
```

### Go
```bash
# Extract imports from a Go file
grep -E "^\t\"" "$FILE" | sed 's/\t"//;s/"//'
```

### Python
```bash
# Extract imports
grep -E "^import|^from .* import" "$FILE" | \
  sed -E 's/^from ([^ ]+) import.*/\1/;s/^import ([^ ]+).*/\1/'
```

---

## Circular Dependency Handling

When Kahn's algorithm detects cycles:

1. **Identify cycle members**: Files that never reach zero in-degree.
2. **Force into single batch**: Resolve together, manually coordinated.
3. **Document in MERGE-CONTEXT.md**: Note the circular dependency for the developer.
4. **Common cycles**:
   - TypeScript barrel files importing from files that import from the barrel
   - Go packages with mutual imports (requires restructuring)
   - React components with circular context dependencies

---

## SPRINT Mode (≤15 files)

When in SPRINT mode:
- Skip formal batch assignment
- Process all files in a single logical batch
- Order by: lockfiles → configs → types → everything else → tests
- No dependency graph analysis (too expensive for small merges)

---

## References
- polyglot-dependency-analysis.md (Sections 4-8: Kahn's Algorithm, Heuristics)
- parallel-conflict-resolution-theory.md (Sections 2-5: Isolation Boundaries)
- large-scale-merge-patterns.md (Sections 3-4: Batch Sizing)
