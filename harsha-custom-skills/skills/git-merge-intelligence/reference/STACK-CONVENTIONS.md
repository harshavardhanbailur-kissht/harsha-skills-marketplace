# Stack Conventions: Language-Specific Resolution Patterns

Reference for resolving merge conflicts with language-aware semantics. Load during Phases 2-4.

---

## TypeScript / JavaScript

### Import Resolution
- **Duplicate imports**: Deduplicate. Keep the one with more named imports.
- **Conflicting import paths**: Prefer alias imports (`@/`) over relative (`../../../`).
- **Default vs named**: If one branch uses default import and other uses named, check the export. Barrel files (`index.ts`) often re-export with different styles.
- **Side-effect imports**: Always keep (`import './polyfill'`). Order: polyfills → framework → libraries → local.

### Type Merging
- **Union types**: When both branches widen a type, merge unions: `string | number` + `string | boolean` → `string | number | boolean`.
- **Interface extension**: When both branches add fields, keep all fields. Check for name collisions with different types.
- **Generic constraints**: Prefer the wider constraint unless narrowing is intentional.
- **Enum members**: Keep all members. Watch for duplicate numeric values — explicit values prevent accidental overlap.

### React Patterns (v18+/v19)
- **Hook order**: NEVER reorder hooks. Both branches' hooks must appear in the original + new positions.
- **Props interfaces**: Merge all props. If both branches make a prop optional/required differently, prefer required (safer).
- **Context providers**: Nesting order matters. Inner provider values override outer. Preserve nesting from the branch that established the architecture.
- **Server Components (React 19)**: `'use client'` directive placement is critical. If conflict involves this directive, preserve whichever branch needs client-side rendering.

### Package.json
- **dependencies/devDependencies**: Deep merge. Higher semver wins for the same package.
- **scripts**: Keep all scripts from both branches. If same script name, keep the more comprehensive command.
- **engines**: Keep the stricter constraint (higher minimum).
- **Never merge lockfiles manually**: Always regenerate with `npm install` / `yarn install`.

---

## Go

### Module Resolution
- **go.mod**: Keep higher module version for each dependency. Use `go mod tidy` after.
- **go.sum**: ALWAYS delete and regenerate with `go mod tidy`. Never merge manually.
- **Replace directives**: Keep all `replace` directives from both branches.

### Struct Merging
- **Field ordering**: Exported fields first (capitalized), then unexported. Alphabetical within each group.
- **Embedded structs**: If both branches embed different structs, keep both. Check for method name collisions.
- **Tags**: Merge struct tags. Both `json` and `db` tags should be preserved.
- **Pointer vs value receivers**: Prefer the one from the branch with more changes to that type.

### Interface Patterns
- **Interface expansion**: When both branches add methods, keep all methods.
- **Interface satisfaction**: After merging, verify all types that implemented the interface still satisfy it.
- **Empty interface → `any`**: Go 1.18+ uses `any` instead of `interface{}`. Prefer `any`.

### Error Handling
- **Error types**: If both branches define new error types, keep both. Check for `errors.Is`/`errors.As` chains.
- **Error wrapping**: Prefer `fmt.Errorf("%w", err)` (Go 1.13+) over `errors.New`.

### Gin/HTTP Handlers
- **Route registration order**: Preserves priority (first match wins). Merge carefully.
- **Middleware chain**: Order matters. Auth before rate-limit before handler.
- **Context values**: Both branches may store different values in `gin.Context`. Key collision = bug.

---

## Python

### Import Resolution
- **Absolute vs relative**: Prefer absolute imports (`from mypackage.module import X`).
- **Wildcard imports**: Avoid. If both branches add `from X import *`, replace with explicit imports.
- **Import order**: isort convention: stdlib → third-party → local. Separated by blank lines.

### Function Signatures
- **Parameter order**: Positional → keyword → `*args` → keyword-only → `**kwargs`.
- **Type hints**: Prefer the more specific type. `Optional[str]` > `str | None` (style varies by project).
- **Default values**: If both branches change defaults, prefer the one from the branch with the test that validates it.

### Lambda/Serverless
- **Handler signatures**: AWS Lambda expects `def handler(event, context)`. Never change this.
- **Authorizer patterns**: Auth middleware conflicts are ALWAYS AUTH_SECURITY. Use Deep Thinker.
- **Environment variables**: Never hardcode. If conflict involves env vars, prefer `os.environ.get()` with defaults.

---

## Configuration Files

### JSON (tsconfig.json, package.json)
- **Deep merge**: Nested objects are merged recursively.
- **Arrays**: Deduplicate entries. Order typically doesn't matter.
- **compilerOptions (tsconfig)**: Stricter settings win (`strict: true` > `strict: false`).

### YAML (docker-compose.yml, CI configs)
- **Service definitions**: Merge services from both branches.
- **Environment variables**: Keep all env vars from both branches. Watch for conflicting values.
- **Volume mounts**: Keep all unique mounts. Flag duplicates with different host paths.

### Dockerfile
- **Layer ordering matters**: Base image → install deps → copy source → build → runtime.
- **Multi-stage builds**: If both branches modify different stages, keep both.
- **COPY/ADD instructions**: Order determines layer cache validity. Don't reorder.

### .env Files
- **NEVER merge .env files with real values**.
- **env.example**: Merge variable names, use placeholder values.
- **If real secrets detected**: Flag immediately. Do not write to any file.

---

## CSS / SCSS / Tailwind

### CSS Specificity
- Later rules win for same specificity. If both branches add rules for same selector, keep both (later branch's last).
- **Media queries**: Keep all. Merge breakpoint rules.

### Tailwind Config
- **Theme extensions**: Deep merge `theme.extend`. Both branches' additions are kept.
- **Plugin array**: Concatenate and deduplicate.
- **Content paths**: Union of all glob patterns.
- **Tailwind v4**: Uses `@import` instead of `@tailwind`. If upgrading, prefer the v4 syntax.

---

## Markdown / Documentation

### Content Merging
- **Heading conflicts**: Keep both sections. Reorder by logical flow.
- **Table of contents**: Regenerate after merge (manual ToC will be wrong).
- **Link references**: Keep all. Check for broken links after merge.
- **Frontmatter (YAML)**: Deep merge.

---

## Cross-Language Contracts

When TypeScript types and Go structs define the same API contract:

1. **Field names must match**: TypeScript `camelCase` maps to Go `json:"camelCase"` tags.
2. **Types must be compatible**: TS `string` → Go `string`, TS `number` → Go `float64` or `int`.
3. **Optional fields**: TS `field?: type` → Go `Field *type` (pointer) or `omitempty` tag.
4. **If one branch changes the contract**: The OTHER language's types must be updated to match.
5. **Always validate both ends** after resolution.

---

## References
- typescript-conflict-resolution-guide.md
- go125-gin-conflict-patterns.md
- react19-conflict-patterns.md
- python-lambda-authorizer-conflicts.md
- vite7-tailwind4-config-conflicts.md
- esm-typescript-module-conflicts.md
- dockerfile-conflict-patterns.md
