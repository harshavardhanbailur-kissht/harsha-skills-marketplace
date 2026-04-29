# Go Merge Conflicts: Quick Reference Guide

## 1. STRUCT CONFLICTS

### Field Ordering (Performance)
- Order fields by size: largest to smallest
- Reduces padding waste
- Use `fieldalignment` linter to verify

### Struct Tags
- Combine tags from both branches: `json:"name" db:"user_name" bson:"user"`
- Never pick one tag over another
- Check tag consistency across branches

### Embedded Structs
- Avoid embedded conflicts by using named fields instead
- If both branches embed different types, may cause method promotion collisions
- Use interface types instead of concrete types to prevent ambiguity

## 2. INTERFACE CONFLICTS

### Method Addition (BREAKING)
- Adding methods to interfaces breaks existing implementations
- Solution: Create new interface extending old one
- Or add unexported methods for internal-only usage

### Interface Satisfaction Loss
- Check with: `var _ Interface = (*Type)(nil)` at compile time
- May lose satisfaction after merge if method removed or signature changed
- `go build ./...` will catch these

### interface{} to Concrete Evolution
- Use Go 1.18+ generics instead of interface{}
- Prefer explicit types over type erasure
- Document migration path clearly

## 3. MODULE CONFLICTS

### go.mod Conflicts
- Take UNION of versions: use highest version of each module
- After manual resolution, always run: `go mod tidy`
- Never manually merge go.sum - regenerate it

### go.sum
- DELETE and regenerate: `rm go.sum && go mod tidy`
- Never manually pick one hash over another
- Always regenerate after go.mod changes

### Replace Directives
- Only apply in main module, ignored in dependencies
- For local development: `replace github.com/lib => ../lib`
- Remove after merging if permanent change

### MVS (Minimum Version Selection)
- Go picks MINIMUM version satisfying all constraints
- Higher versions only if explicitly required
- Provides predictable builds

## 4. GIN FRAMEWORK CONFLICTS

### Router Registration
- No duplicate routes (same method + path)
- Organize handlers in separate setup functions
- Document route intent with constants

### Middleware Ordering (SECURITY CRITICAL)
```
Canonical order:
1. Recovery (panic handling)
2. Logging (audit trail)
3. CORS (browser headers)
4. CSRF Protection (validation)
5. Authentication (auth/authz)
6. Rate Limiting (after auth for identity-based limits)
```
- Document why order matters
- Test middleware execution order
- Wrong order can bypass security checks

### Handler Signatures
- Must match `gin.HandlerFunc`: `func(*gin.Context)`
- Inject dependencies via middleware or context
- Use `c.Set()` and `c.Get()` for dependency injection

### Context Keys
- Define constants for context keys
- Ensure type consistency (string vs int)
- Create type-safe wrapper for context access

## 5. ERROR HANDLING

### Error Wrapping
- ALWAYS use `%w` to preserve error chains
- Enable `errors.As()` and `errors.Unwrap()`
- Never break chains with `fmt.Errorf("msg")` (no %w)

### Custom Error Types
- Combine if both branches define similar types
- Implement `Unwrap()` to satisfy error interface
- Use error constructors for consistency

### Multi-Error (Go 1.20+)
- Use `fmt.Errorf("%w + %w", err1, err2)` for multiple errors
- Callers use `errors.As()` to extract specific errors

## 6. VALIDATION TOOLS

### go build ./...
- Syntax, type, import errors
- Interface satisfaction failures
- Run FIRST - merge is broken if this fails

### go vet ./...
- Suspicious code patterns
- Printf mismatches, nil deferences
- Run SECOND after compilation

### staticcheck
- ~150 checks vs vet's ~10
- Dead code, nil deferences, leaks
- `go install honnef.co/go/tools/cmd/staticcheck@latest`

### golangci-lint
- 50+ linters orchestrated
- Includes vet, staticcheck, gosec, gocyclo
- Run: `golangci-lint run ./...`

### go test -race
- Data race detection
- Catches concurrent access issues
- Run: `go test -race ./...`

### POST-MERGE WORKFLOW
```bash
go build ./...
go vet ./...
staticcheck ./...
golangci-lint run ./...
go test -race ./...
go test ./... -v
```

## 7. GO 1.21+ FEATURES

### Generics
- Prefer generics over interface{} for type safety
- Define constraints in separate package
- Compatible type constraints: `[T comparable]`, `[T constraints.Ordered]`

### slog (Structured Logging)
- Migrate completely to slog if Go 1.21+
- Consistent JSON or text output
- Use `slog.Default()` for package access
- Avoid mixing old log and new slog

### maps & slices Packages
- Use stdlib: `slices.Reverse()`, `maps.Keys()`
- Remove custom implementations
- Better performance and consistency

## POST-MERGE CHECKLIST

- [ ] `go build ./...` ✓
- [ ] `go vet ./...` ✓
- [ ] Interface satisfaction verified
- [ ] go.mod: highest versions, go.sum regenerated
- [ ] No replace directive conflicts
- [ ] Struct field ordering optimized
- [ ] Gin routes: no duplicates
- [ ] Middleware order security-reviewed
- [ ] Error wrapping consistent
- [ ] `staticcheck ./...` ✓
- [ ] `golangci-lint run ./...` ✓
- [ ] `go test -race ./...` ✓
- [ ] `go test ./... -v` ✓
