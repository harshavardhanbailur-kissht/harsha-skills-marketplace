# Go Refactoring Patterns

Patterns specific to Go projects.

## Table of Contents

1. [Error Handling](#error-handling)
2. [Interface & Structure](#interface-structure)
3. [Concurrency](#concurrency)
4. [Modernization](#modernization)
5. [Testing](#testing)

---

## Error Handling

### 1. Sentinel Errors → Wrapped Errors
**Risk: Low** (Go 1.13+)
```go
// Before
if err == ErrNotFound {

// After
if errors.Is(err, ErrNotFound) {
```
- Wrap with context: `fmt.Errorf("loading user %d: %w", id, err)`
- Safety: `errors.Is` works through wrapped chains; direct == does not

### 2. Error String Matching → errors.As
**Risk: Low**
```go
// Before
if strings.Contains(err.Error(), "timeout") {

// After
var netErr *net.OpError
if errors.As(err, &netErr) {
```
- Safety: Type-safe, won't break when error messages change

### 3. Panic Removal
**Risk: Medium**
- Replace `panic()` in library code with returned errors
- `panic` is only acceptable for truly unrecoverable programmer errors
- Safety: Must update all callers to handle the new error return

---

## Interface & Structure

### 4. Interface Extraction
**Risk: Medium**
```go
// Before: function accepts concrete type
func ProcessData(db *sql.DB) error {

// After: function accepts interface (testable)
type DataStore interface {
    Query(ctx context.Context, q string) (*sql.Rows, error)
}
func ProcessData(db DataStore) error {
```
- Keep interfaces small (1-3 methods); Go proverb: "the bigger the interface, the weaker the abstraction"
- Define interfaces at the consumer, not the provider
- Safety: Verify all concrete types satisfy the interface

### 5. Struct Embedding for Composition
**Risk: Medium**
```go
// Before: manual delegation
type Server struct { logger *Logger }
func (s *Server) Log(msg string) { s.logger.Log(msg) }

// After: embedding
type Server struct { *Logger }
// Server.Log() is automatically available
```
- Safety: Watch for shadowed fields/methods; check exported method sets

### 6. Context Propagation
**Risk: Low** (additive change)
```go
// Before: func DoWork(id int) error
// After:  func DoWork(ctx context.Context, id int) error
```
- Context goes as the first parameter, always
- Safety: Cascade through all callers; check for cancellation with `ctx.Done()`

---

## Concurrency

### 7. Goroutine Safety
**Risk: High**
- Replace unsynchronized shared state with channels or sync.Mutex
- Always run `go test -race ./...` before and after
- Use `sync.WaitGroup` for goroutine lifecycle management
- Safety: Race detector is your primary verification tool

### 8. Channel Direction Annotations
**Risk: Low**
```go
// Before: func producer(ch chan int)
// After:  func producer(ch chan<- int)  // send-only
```
- Compile-time safety; prevents accidental reads from a write channel

---

## Modernization

### 9. ioutil → io/os (Go 1.16+)
**Risk: None** (drop-in replacements)
```go
// Before                    → After
ioutil.ReadAll(r)           → io.ReadAll(r)
ioutil.ReadFile(name)       → os.ReadFile(name)
ioutil.WriteFile(name,d,p)  → os.WriteFile(name,d,p)
ioutil.TempDir(dir,prefix)  → os.MkdirTemp(dir,prefix)
ioutil.TempFile(dir,prefix) → os.CreateTemp(dir,prefix)
ioutil.ReadDir(name)        → os.ReadDir(name)
```

### 10. String Concatenation → strings.Builder
**Risk: None**
```go
// Before (in loop): result += chunk
// After:
var b strings.Builder
for _, chunk := range chunks {
    b.WriteString(chunk)
}
result := b.String()
```
- Performance: O(n) vs O(n^2) for large strings

### 11. init() Cleanup
**Risk: Medium**
- Replace `init()` side effects with explicit initialization functions
- Makes testing easier; removes hidden startup dependencies
- Safety: Document initialization order; verify in integration tests

---

## Testing

### 12. Table-Driven Tests
**Risk: None** (test-only change)
```go
tests := []struct {
    name string
    input int
    want  int
}{
    {"positive", 5, 25},
    {"zero", 0, 0},
    {"negative", -3, 9},
}
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        got := Square(tt.input)
        if got != tt.want {
            t.Errorf("Square(%d) = %d, want %d", tt.input, got, tt.want)
        }
    })
}
```

### 13. Package Organization
**Risk: Medium**
- When a package exceeds ~500 lines, split by responsibility
- Use internal/ for implementation details
- Safety: `go test ./...` must pass; verify no circular imports

---

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| gofmt | Formatting | `gofmt -w .` |
| goimports | Import management | `goimports -w .` |
| go vet | Static analysis | `go vet ./...` |
| golangci-lint | Comprehensive linting | `golangci-lint run` |
| gocyclo | Cyclomatic complexity | `gocyclo -over 10 .` |
| gocognit | Cognitive complexity | `gocognit -over 15 .` |
| deadcode | Dead code detection | `deadcode ./...` |
