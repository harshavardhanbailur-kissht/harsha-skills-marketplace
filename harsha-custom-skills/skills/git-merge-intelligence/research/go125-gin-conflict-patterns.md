# Go 1.21+ & Gin Framework Merge Conflict Patterns: Comprehensive Research

## Executive Summary

Go merge conflicts differ significantly from other languages due to Go's unique characteristics: strict type checking at compile time, interface satisfaction requirements, module dependency resolution through Minimum Version Selection (MVS), and the absence of traditional object-oriented inheritance. This research covers seven critical areas where merge conflicts occur in Go projects, with emphasis on Gin framework applications.

---

## 1. Go Struct Conflicts

### 1.1 Field Ordering and Memory Alignment

When both branches add fields to the same struct, developers must understand Go's memory alignment rules to avoid performance regressions.

#### The Alignment Problem

Go allocates struct fields in declaration order, but the compiler enforces alignment requirements based on field types:
- 1-byte types (byte, bool): align at 1-byte boundaries
- 2-byte types (int16, uint16): align at 2-byte boundaries
- 4-byte types (int32, uint32, float32): align at 4-byte boundaries
- 8-byte types (int64, uint64, float64, pointers): align at 8-byte boundaries

The compiler inserts **padding** (empty space) between fields to satisfy these requirements. Misaligned access forces the CPU to perform multiple memory reads, degrading performance.

**Reference**: [Struct Field Alignment - Go Optimization Guide](https://goperf.dev/01-common-patterns/fields-alignment/)

#### Merge Conflict Scenario

```go
// Branch A: adds UserID field
type User struct {
    Name string      // 16 bytes (pointer + len + cap)
    UserID int64     // 8 bytes - no padding needed if after Name
}

// Branch B: adds Active field
type User struct {
    Name string      // 16 bytes
    Active bool      // 1 byte - creates 7 bytes of padding before next 8-byte field
}

// Merge result: correct field ordering depends on the actual fields
type User struct {
    Name string      // 16 bytes
    UserID int64     // 8 bytes (proper 8-byte alignment)
    Active bool      // 1 byte + 7 bytes padding = 8 bytes total
    // Total: 32 bytes (vs optimal 25 bytes if reordered)
}
```

#### Resolution Strategy

After merge conflict resolution, **reorder fields by size, largest to smallest**:

```go
// Optimal ordering after merge
type User struct {
    Name string      // 16 bytes (largest)
    UserID int64     // 8 bytes
    Active bool      // 1 byte + 7 bytes padding (smallest)
    // Still 32 bytes but clearer intent
}

// Better yet: group by size
type User struct {
    // 8-byte aligned fields
    UserID int64
    Created time.Time  // 16 bytes on 64-bit systems
    // String field (16 bytes)
    Name string
    // Boolean field (1 byte + padding)
    Active bool
}
```

**Validation**: Use `fieldalignment` linter via golangci-lint to detect suboptimal ordering after merge.

### 1.2 Struct Tag Conflicts

Struct tags are metadata used by libraries to marshal/unmarshal data. Conflicts occur when branches add or modify tags.

#### Common Tag Types

```go
type Product struct {
    // JSON marshaling tag
    Name string `json:"name"`

    // BSON (MongoDB) tag
    ID string `bson:"_id"`

    // Database tag (sqlx, gorm, etc.)
    Price float64 `db:"product_price"`

    // Multiple tags on one field
    SKU string `json:"sku" db:"sku_code" bson:"sku"`
}
```

#### Merge Conflict Scenario

```go
// Branch A adds JSON tag
Price float64 `json:"price"`

// Branch B adds database tag
Price float64 `db:"unit_price"`

// Merge conflict - which tag wins?
// Git shows both, must manually resolve
```

#### Resolution Strategy

When both branches add different tags to the same field, **combine all tags**:

```go
// Correct resolution
Price float64 `json:"price" db:"unit_price"`

// NOT this (only one tag applies)
// Price float64 `json:"price"`

// Special case: ignoring a field in specific marshaler
// Wrong - second tag may be ignored
Field string `json:"-" bson:"-"`

// Better: be explicit about which marshalers see it
Field string `json:"-" bson:"field" db:"field"`
```

**Key Risk**: If the same field has conflicting tag values (e.g., `json:"old_name"` vs `json:"new_name"`), this causes silent data mapping failures in production.

### 1.3 Embedded Struct Conflicts

Embedded structs (composition via anonymous fields) create implicit method promotion that can conflict after merges.

#### Embedded Struct Basics

```go
type Timestamp struct {
    CreatedAt time.Time
    UpdatedAt time.Time
}

type User struct {
    Timestamp  // Anonymous field - methods promoted to User
    Name string
}

// User automatically has CreatedAt, UpdatedAt methods
user := User{}
user.CreatedAt = time.Now()  // Works - promoted from Timestamp
```

#### Merge Conflict Scenario

```go
// Branch A embeds Logger
type Handler struct {
    Logger *log.Logger
    // ... fields
}

// Branch B embeds Config
type Handler struct {
    Config *AppConfig
    // ... fields
}

// Merge conflict: which embedding wins?
// If both are embedded, may cause:
// 1. Unintended method promotion
// 2. Ambiguous method resolution
// 3. Initialization complexity

type Handler struct {
    Logger *log.Logger     // From branch A
    Config *AppConfig      // From branch B
    mux *http.ServeMux
}

// Now Handler has methods from both Logger and Config
// If both have a String() method, ambiguity error at compile time
```

#### Resolution Strategy

**Avoid embedded conflicts by using named fields** instead of anonymous composition when multiple branches might add similar types:

```go
// Better: explicit names avoid promotion ambiguity
type Handler struct {
    logger *log.Logger
    config *AppConfig
    mux *http.ServeMux
}

// Or keep embedding but use interface types
type Handler struct {
    logger Logger       // interface type, prevents method collision
    config Config      // interface type
    mux *http.ServeMux
}
```

**Validation**: Compile-time errors will reveal ambiguous method promotion immediately.

---

## 2. Go Interface Conflicts

### 2.1 Breaking vs Non-Breaking Interface Changes

Adding methods to interfaces is a **breaking change** in Go because implementations must define all interface methods.

#### The Interface Satisfaction Problem

Go uses **implicit interface satisfaction**: a type satisfies an interface if it implements all methods, regardless of intent.

```go
// Original interface in stdlib
type io.Writer interface {
    Write(p []byte) (n int, err error)
}

// Many implementations exist in user code
type MyWriter struct { ... }
func (mw *MyWriter) Write(p []byte) (n int, err error) { ... }

// If stdlib adds a new method to io.Writer
type io.Writer interface {
    Write(p []byte) (n int, err error)
    Flush() error  // NEW METHOD - BREAKS myWriter!
}

// MyWriter no longer satisfies io.Writer in code expecting Flush()
// This breaks anyone passing MyWriter to a function expecting io.Writer with Flush
```

#### Merge Conflict Scenario

```go
// Branch A adds method to public interface
type PaymentProcessor interface {
    ProcessPayment(amount float64) error
}

// Branch B adds different method to same interface
type PaymentProcessor interface {
    ProcessPayment(amount float64) error
    Validate() error  // NEW in branch B
}

// After merge: existing implementations must implement both
// Any type that implemented old interface in external packages breaks!
```

#### Resolution Strategy: Preserve Compatibility

**Option 1: Create new interface extending the old one**

```go
// Keep original interface untouched
type PaymentProcessor interface {
    ProcessPayment(amount float64) error
}

// Create new interface for extended functionality
type ValidatingPaymentProcessor interface {
    PaymentProcessor  // Embed original
    Validate() error  // Add new method
}

// Existing code using PaymentProcessor still works
// New code can opt-in to ValidatingPaymentProcessor
```

**Option 2: Use unexported methods (internal use only)**

```go
// If interface is only used internally, add unexported method
type paymentProcessor interface {
    ProcessPayment(amount float64) error
    validate() error  // Unexported - won't break external implementations
}
```

**Option 3: Return concrete types instead of interfaces**

```go
// Instead of returning interface
// func GetProcessor() PaymentProcessor { ... }

// Return concrete type
func GetProcessor() *StripeProcessor { ... }

// Allows adding methods to StripeProcessor without breaking interface contracts
// Only matters if return value is cast to interface
```

**Key Principle**: Never add methods to exported interfaces used in other packages.

**Reference**: [Keeping Your Modules Compatible - The Go Programming Language](https://go.dev/blog/module-compatibility)

### 2.2 Interface Satisfaction After Merge

Subtle situations where a struct loses interface satisfaction during merge:

#### Loss of Method When Field Removed

```go
// Original type
type Handler struct {
    logger *Logger
}
func (h *Handler) Log(msg string) error {
    return h.logger.Log(msg)
}
// Handler satisfies Logger interface: Log(msg string) error

// Branch A: removes logger field, adds direct implementation
type Handler struct {
    logFunc func(string) error
}
func (h *Handler) Log(msg string) error {
    return h.logFunc(msg)  // Still implements Log
}

// Branch B: modifies the Log signature
type Handler struct {
    logger *Logger
}
func (h *Handler) Log(msg string) {  // Removed error return!
    h.logger.Log(msg)
}

// After merge: if we take Branch B's signature, Handler breaks interface contract
type Logger interface {
    Log(msg string) error
}
// Handler no longer satisfies Logger interface!
```

#### Embedded Interface Satisfaction Loss

```go
// Original
type UserService struct {
    repo UserRepository  // Embedded interface
}
// UserService satisfies UserRepository (by embedding)

// Branch A: adds explicit implementation
type UserService struct {
    repo UserRepository
    db *sql.DB
}
// Still satisfies via embedding

// Branch B: removes embedding, forgets implementation
type UserService struct {
    db *sql.DB
    cache *redis.Client
}

// After merge: may accidentally use Branch B's structure
// UserService no longer satisfies UserRepository interface!
```

#### Resolution Strategy

After merge:

1. **Run `go build ./...`** - catches obvious interface satisfaction failures
2. **Check method signatures** - ensure return types and parameters match interface
3. **Verify embedding** - if interface is satisfied via embedded field, ensure field is still there
4. **Use compile-time checks**:

```go
// Add compile-time assertion
var _ Logger = (*Handler)(nil)  // Fails at compile if Handler doesn't satisfy Logger
var _ json.Marshaler = (*User)(nil)
var _ io.Reader = (*CustomReader)(nil)
```

### 2.3 The empty interface (any) to Concrete Type Evolution

The empty interface `interface{}` (or `any` in Go 1.18+) creates type erasure that leads to merge conflicts when concrete types are introduced.

#### Problem Scenario

```go
// Original: flexible with interface{}
func ProcessData(data interface{}) error {
    switch v := data.(type) {
    case string:
        return processString(v)
    case int:
        return processInt(v)
    default:
        return fmt.Errorf("unsupported type")
    }
}

// Branch A: adds User struct as new supported type
type User struct {
    ID int
    Name string
}

func ProcessData(data interface{}) error {
    // ... existing cases ...
    case *User:
        return processUser(v)
    default:
        return fmt.Errorf("unsupported type")
    }
}

// Branch B: refactors to use concrete type, removes interface{}
type DataProcessor interface {
    Process() error
}

func HandleData(processor DataProcessor) error {
    return processor.Process()
}

type User struct {
    ID int
    Name string
}
func (u *User) Process() error { ... }

// Merge conflict: Branch B's concrete approach is incompatible with Branch A's interface{}
// After merge: which approach do we use?
```

#### Resolution Strategy: Generics as Modern Alternative

Go 1.18+ provides **generics** as a safer alternative to `interface{}`:

```go
// Modern approach: use generics instead of interface{}
type Processor[T any] interface {
    Process(data T) error
}

type StringProcessor struct{}
func (sp *StringProcessor) Process(data string) error { ... }

type UserProcessor struct{}
func (up *UserProcessor) Process(data *User) error { ... }

// Type-safe, no runtime type switches
// Easier to merge because types are explicit
```

If merging branches with `interface{}` vs concrete types:

1. **Prefer concrete types** if possible - more maintainable
2. **Use generics** instead of `interface{}` for new code
3. **Keep both approaches only if necessary** (legacy support) - clearly document in comments

---

## 3. Go Module Conflicts

### 3.1 go.mod Require Block Conflicts

The `require` directive specifies module versions. Conflicts occur when branches update different dependencies or the same dependency to different versions.

#### Merge Conflict Anatomy

```go
// Original go.mod
require (
    github.com/lib/pq v1.10.0
    github.com/gin-gonic/gin v1.8.0
)

// Branch A updates gin
require (
    github.com/lib/pq v1.10.0
    github.com/gin-gonic/gin v1.9.0  // Updated
)

// Branch B updates postgres driver
require (
    github.com/lib/pq v1.11.0  // Updated
    github.com/gin-gonic/gin v1.8.0
)

// After merge: Git shows conflict
<<<<<<< HEAD
require (
    github.com/lib/pq v1.10.0
    github.com/gin-gonic/gin v1.9.0
)
=======
require (
    github.com/lib/pq v1.11.0
    github.com/gin-gonic/gin v1.8.0
)
>>>>>>> feature-branch
```

#### Resolution Strategy

When resolving require conflicts:

1. **Take the union of versions** - resolve to highest version for each distinct module:

```go
// Correct resolution: highest version of each
require (
    github.com/lib/pq v1.11.0
    github.com/gin-gonic/gin v1.9.0
)
```

2. **Verify compatibility** - higher versions may have breaking changes:

```bash
# After manual merge resolution
go mod tidy
# This regenerates based on actual imports and runs go get
```

3. **Understand Minimum Version Selection (MVS)**:

Instead of solving complex dependency constraints like npm or pip, Go uses **Minimum Version Selection**: for each module, select the **minimum version that satisfies all requirements**.

**Reference**: [research!rsc: Minimal Version Selection](https://research.swtch.com/vgo-mvs)

Example:
```
- Your code requires github.com/lib/pq v1.11.0
- github.com/lib/pq v1.11.0 requires postgres v0.5.0
- Your code independently requires postgres v0.6.0

Result: MVS selects postgres v0.6.0 (minimum that satisfies both constraints)
Not v0.7.0 or v1.0.0 even if available!
```

### 3.2 go.mod Replace Directive Conflicts

The `replace` directive temporarily substitutes one module with another, typically for local development.

#### Replace Directive Mechanics

```go
// Redirect a module to a local filesystem path (for local development)
replace github.com/mycompany/library => ../library

// Or replace with a different module/version
replace github.com/old/package => github.com/new/package v1.0.0
```

#### Merge Conflict Scenario

```go
// Original go.mod (no replace)
require github.com/mycompany/lib v1.5.0

// Branch A: replaces lib with local path for development
replace github.com/mycompany/lib => ../mycompany-lib

// Branch B: upgrades lib version
require github.com/mycompany/lib v1.6.0

// Merge conflict in replace block (or absence of it)
```

#### Resolution Strategy

**Key Rule**: Replace directives only apply in the **main module's** go.mod file. They are ignored in dependency modules.

After merge conflict:

1. **Decide the intent**: Is this for local development or permanent upgrade?

2. **If local development**: keep replace, comment on why
```go
// For development, use local copy
replace github.com/mycompany/lib => ../mycompany-lib
require github.com/mycompany/lib v1.6.0  // Version must still exist
```

3. **If permanent upgrade**: remove replace, update require
```go
require github.com/mycompany/lib v1.6.0
// No replace - use actual module
```

4. **For conflicting replace directives** across workspace modules (if using go.work):

```go
// go.work file can override replace directives
go 1.21
use (
    ./main
    ./lib1
    ./lib2
)

// Can specify replace at workspace level that overrides modules
replace github.com/external/lib => ../local/lib
```

**Critical**: After resolving replace conflicts, always run:
```bash
go mod tidy
go build ./...
```

### 3.3 go.sum Conflicts - Never Manually Merge

The `go.sum` file contains cryptographic hashes of module contents. It must NEVER be manually merged.

#### What go.sum Is

```
# go.sum tracks module versions and their content hashes
github.com/lib/pq v1.10.0 h1:Yk...
github.com/lib/pq v1.10.0/go.mod h1:W7...
github.com/gin-gonic/gin v1.8.0 h1:n...
github.com/gin-gonic/gin v1.8.0/go.mod h1:...
```

#### Merge Conflict in go.sum

```
# Branch A updated a dependency
github.com/lib/pq v1.11.0 h1:XXX...
github.com/lib/pq v1.11.0/go.mod h1:YYY...

# Branch B kept older version
github.com/lib/pq v1.10.0 h1:ZZZ...
github.com/lib/pq v1.10.0/go.mod h1:WWW...

# Conflict appears in go.sum
<<<<<<< HEAD
github.com/lib/pq v1.11.0 h1:XXX...
=======
github.com/lib/pq v1.10.0 h1:ZZZ...
>>>>>>> feature
```

#### Resolution: Always Regenerate

**NEVER manually edit go.sum to "pick" one hash over another.**

1. **Resolve go.mod first** (see section 3.1)
2. **Delete go.sum** entirely
3. **Run `go mod tidy`**:

```bash
rm go.sum
go mod tidy
# This re-downloads verified modules and regenerates go.sum with correct hashes
```

Or:
```bash
git checkout --ours go.mod  # Take version from HEAD
git rm go.sum              # Mark as resolved (will regenerate)
go mod tidy               # Regenerates go.sum
git add go.mod go.sum
git commit
```

**Reference**: [Go Modules Reference - The Go Programming Language](https://go.dev/ref/mod)

### 3.4 When to Run `go mod tidy` After Merge

`go mod tidy` serves two purposes:
1. **Removes unused dependencies** from require block
2. **Adds missing dependencies** based on imports in code
3. **Validates hashes** in go.sum

#### Merge Workflow

```bash
# Step 1: Manually resolve go.mod conflicts
# - Keep union of requires from both branches
# - Resolve to highest version of each module

git add go.mod

# Step 2: Delete conflicted go.sum
git rm go.sum

# Step 3: Run tidy - this regenerates both
go mod tidy

# Step 4: Verify
go build ./...
go test ./...

# Step 5: Commit
git add go.mod go.sum
git commit -m "Merge branch X: resolved module conflicts"
```

#### Common Mistake

```bash
# WRONG: Running tidy with conflicted go.mod
<<<<<<< HEAD
require github.com/lib/pq v1.11.0
=======
require github.com/lib/pq v1.10.0
>>>>>>> feature

go mod tidy  # Undefined behavior! Tidy may not work correctly
```

---

## 4. Gin Framework Specific Conflicts

### 4.1 Router Registration Conflicts

Both branches add routes - either to the same group or with conflicting patterns.

#### Basic Router Setup

```go
import "github.com/gin-gonic/gin"

func main() {
    router := gin.Default()

    // Public routes
    router.GET("/health", healthHandler)

    // API group
    api := router.Group("/api")
    api.GET("/users", listUsers)
    api.POST("/users", createUser)

    router.Run(":8080")
}
```

#### Merge Conflict Scenario: Duplicate Routes

```go
// Branch A adds user routes
func setupUserRoutes(api *gin.RouterGroup) {
    api.GET("/users", listUsers)
    api.GET("/users/:id", getUser)
    api.POST("/users", createUser)
}

// Branch B adds authentication routes
func setupAuthRoutes(api *gin.RouterGroup) {
    api.POST("/login", login)
    api.POST("/users", registerUser)  // CONFLICTS with createUser!
}

// After merge: which handler runs for POST /api/users?
// The one registered last!
router := gin.Default()
api := router.Group("/api")
setupUserRoutes(api)
setupAuthRoutes(api)

// POST /api/users calls registerUser, not createUser
// Or vice versa depending on merge outcome
```

#### Merge Conflict Scenario: Same Route Different Methods

```go
// Branch A
api.GET("/users", listUsers)

// Branch B
api.POST("/users", createUser)

// After merge: no Git conflict (different methods), but both should exist
api.GET("/users", listUsers)
api.POST("/users", createUser)
// Both are correct! Conflict resolved properly.
```

#### Merge Conflict Scenario: Handler Extraction

```go
// Original
router.POST("/products", func(c *gin.Context) {
    // handler implementation
})

// Branch A extracts to function
func productCreateHandler(c *gin.Context) {
    // implementation
}
router.POST("/products", productCreateHandler)

// Branch B extracts to different function name
func createProductHandler(c *gin.Context) {
    // similar implementation
}
router.POST("/products", createProductHandler)

// After merge: which extraction won?
// Conflict in line with route registration
```

#### Resolution Strategy

1. **Ensure no duplicate routes** (same method and path):
```bash
# After merge, verify routes
go build ./...
# The code compiles, but doesn't detect duplicate routes

# Create test to validate routes
func TestNoRouteConflicts(t *testing.T) {
    router := gin.Default()
    setupRoutes(router)

    // Gin doesn't expose routes easily, so test by making requests
    w := httptest.NewRecorder()
    req, _ := http.NewRequest("POST", "/api/users", nil)
    router.ServeHTTP(w, req)

    // Verify correct handler was called
    // (requires injecting test doubles)
}
```

2. **Organize handlers in separate functions**:
```go
func setupRoutes(router *gin.Engine) {
    api := router.Group("/api")

    // Separate setup functions prevent conflicts
    setupUserRoutes(api)
    setupProductRoutes(api)
    setupAuthRoutes(api)
}

func setupUserRoutes(api *gin.RouterGroup) {
    users := api.Group("/users")
    users.GET("", listUsers)
    users.GET("/:id", getUser)
    users.POST("", createUser)
}
```

3. **Document route intent**:
```go
// Clear naming prevents registration confusion
const (
    // User Management
    routeUserList   = "GET /api/users"
    routeUserGet    = "GET /api/users/:id"
    routeUserCreate = "POST /api/users"

    // Not /api/users with different semantics
    routeRegister   = "POST /api/auth/register"
    routeLogin      = "POST /api/auth/login"
)
```

### 4.2 Middleware Ordering - Critical Security Implications

Gin executes middleware in the order registered (onion model). Wrong order = security bypass.

#### Middleware Execution Model

```go
router := gin.Default()
// Default() adds Logger and Recovery middleware

router.Use(globalMiddleware1)  // Executes first
router.Use(globalMiddleware2)  // Executes second

api := router.Group("/api")
api.Use(authMiddleware)         // For /api/* only
api.GET("/users", listUsers)    // authMiddleware runs before handler

// Execution order for GET /api/users:
// 1. globalMiddleware1
// 2. globalMiddleware2
// 3. authMiddleware
// 4. listUsers handler
```

#### Security Merge Conflict Scenario

```go
// Original
func setupRoutes(router *gin.Engine) {
    router.Use(loggingMiddleware)
    router.Use(corsMiddleware)

    api := router.Group("/api")
    api.Use(authMiddleware)
    api.GET("/users", listUsers)
}

// Branch A: adds rate limiting before auth
func setupRoutes(router *gin.Engine) {
    router.Use(loggingMiddleware)
    router.Use(corsMiddleware)

    api := router.Group("/api")
    api.Use(rateLimitMiddleware)  // NEW
    api.Use(authMiddleware)
    api.GET("/users", listUsers)
}

// Branch B: adds CSRF protection
func setupRoutes(router *gin.Engine) {
    router.Use(loggingMiddleware)
    router.Use(corsMiddleware)
    router.Use(csrfProtectionMiddleware)  // NEW - at router level

    api := router.Group("/api")
    api.Use(authMiddleware)
    api.GET("/users", listUsers)
}

// After merge conflict resolution:
func setupRoutes(router *gin.Engine) {
    router.Use(loggingMiddleware)
    router.Use(corsMiddleware)
    router.Use(csrfProtectionMiddleware)  // Branch B

    api := router.Group("/api")
    api.Use(rateLimitMiddleware)           // Branch A
    api.Use(authMiddleware)
    api.GET("/users", listUsers)
}

// SECURITY ISSUE: CSRF protection runs before CORS?
// CORS may bypass CSRF on cross-origin requests!
// Correct order: auth -> CSRF -> rate limit
```

#### Security Principles for Middleware Order

```go
// Canonical order for web security
router.Use(recoveryMiddleware)        // Catch panics (first for safety)
router.Use(loggingMiddleware)         // Log requests
router.Use(corsMiddleware)            // CORS headers (before auth for browser)
router.Use(csrfProtectionMiddleware)  // CSRF validation
router.Use(authMiddleware)            // Authentication/authorization (last before handler)

// Special case: rate limiting
// Should be early to prevent DoS, but after auth if protecting authenticated endpoints
api := router.Group("/api")
api.Use(authMiddleware)               // Auth first
api.Use(rateLimitMiddleware)          // Then rate limit by authenticated user
```

#### Resolution Strategy After Merge

1. **Document middleware intent in comments**:
```go
// Security-critical: do not reorder without security review
router.Use(recoveryMiddleware)         // 1. Graceful error handling
router.Use(loggingMiddleware)          // 2. Audit trail
router.Use(corsMiddleware)             // 3. CORS (before auth for browsers)
router.Use(csrfProtectionMiddleware)   // 4. CSRF validation
router.Use(authMiddleware)             // 5. Authentication

// Rate limiting: after auth to rate-limit by identity
api := router.Group("/api")
api.Use(authMiddleware)
api.Use(rateLimitMiddleware)
```

2. **Test middleware order**:
```go
func TestMiddlewareOrder(t *testing.T) {
    router := gin.New()

    order := []string{}
    router.Use(func(c *gin.Context) {
        order = append(order, "1")
        c.Next()
    })
    router.Use(func(c *gin.Context) {
        order = append(order, "2")
        c.Next()
    })
    router.GET("/test", func(c *gin.Context) {
        order = append(order, "handler")
    })

    w := httptest.NewRecorder()
    req, _ := http.NewRequest("GET", "/test", nil)
    router.ServeHTTP(w, req)

    if !reflect.DeepEqual(order, []string{"1", "2", "handler"}) {
        t.Fatalf("Wrong middleware order: %v", order)
    }
}
```

3. **Use gin.RouterGroup for logical separation**:
```go
// Branch A: public routes
public := router.Group("")  // No middleware
public.GET("/health", healthCheck)
public.POST("/login", login)

// Branch B: authenticated API
api := router.Group("/api")
api.Use(authMiddleware)
api.Use(rateLimitMiddleware)
api.GET("/users", listUsers)

// After merge: clear which middleware applies where
// No conflicts because they apply to different groups
```

**Reference**: [Middleware - Gin Web Framework](https://gin-gonic.com/en/docs/middleware/)

### 4.3 Handler Function Conflicts

Multiple branches may refactor handlers or change their signatures.

#### Handler Signature Stability

```go
// Standard Gin handler signature
type HandlerFunc func(*Context)

// Must match this signature to be registered
func userListHandler(c *gin.Context) {
    users, err := db.GetUsers()
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, users)
}
```

#### Merge Conflict Scenario

```go
// Original handler
func getProductHandler(c *gin.Context) {
    id := c.Param("id")
    // ...
}

// Branch A: refactors for dependency injection
func getProductHandler(c *gin.Context, db *Database) {  // WRONG SIGNATURE!
    id := c.Param("id")
    // ...
}

// Branch B: uses c.MustGet for service access
func getProductHandler(c *gin.Context) {
    db := c.MustGet("database").(*Database)
    id := c.Param("id")
    // ...
}

// After merge: which approach?
// Branch A won't compile - doesn't match HandlerFunc signature!
// Must use Branch B approach or custom middleware
```

#### Resolution Strategy

1. **Keep handlers conforming to HandlerFunc signature**:
```go
func getProductHandler(c *gin.Context) {
    // Dependencies injected via middleware/context
    db := c.MustGet("database").(*Database)
    userID := c.GetString("userID")

    product, err := db.GetProduct(c.Param("id"), userID)
    if err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    c.JSON(200, product)
}
```

2. **Use middleware for dependency injection**:
```go
// Middleware injects dependencies
router.Use(func(c *gin.Context) {
    c.Set("database", db)
    c.Set("cache", cache)
    c.Set("logger", logger)
    c.Next()
})

// Handler retrieves them
func getProductHandler(c *gin.Context) {
    db := c.MustGet("database").(*Database)
    cache := c.MustGet("cache").(*Cache)
    // ...
}
```

3. **Create handler factory functions** if merging refactors:
```go
// After merge: handler factory provides consistent signatures
func NewProductHandler(db *Database, cache *Cache) gin.HandlerFunc {
    return func(c *gin.Context) {
        // Implementation
    }
}

router.GET("/products/:id", NewProductHandler(db, cache))
```

### 4.4 Gin Context Usage Patterns

Both branches may add context bindings, causing key name conflicts or type mismatches.

#### Context Key Conflicts

```go
// Branch A stores user ID as string
c.Set("userID", "123")  // Type: string

// Branch B stores user ID as int
c.Set("userID", 123)    // Type: int

// Handler expects string but gets int -> runtime panic!
userID := c.GetString("userID")  // Returns empty string if int stored
// or
userID := c.MustGet("userID").(string)  // Panic: cannot convert int to string
```

#### Merge Conflict Scenario

```go
// Middleware in Branch A
func authMiddleware(c *gin.Context) {
    userID := extractUserIDFromToken(c)
    c.Set("userID", userID)           // string
    c.Set("user", user)               // *User struct
    c.Next()
}

// Middleware in Branch B
func authMiddleware(c *gin.Context) {
    userID, _ := extractUserIDFromToken(c)
    c.Set("userID", userID)           // int
    c.Set("claims", claims)           // *Claims struct
    c.Next()
}

// After merge: both set "userID" with different types!
// Whichever runs last determines the type
// Handler expecting string fails if int runs last
```

#### Resolution Strategy

1. **Define constants for context keys**:
```go
const (
    ContextKeyUserID   = "userID"
    ContextKeyUser     = "user"
    ContextKeyToken    = "token"
    ContextKeyLogger   = "logger"
)

// In middleware
c.Set(ContextKeyUserID, userID)
c.Set(ContextKeyUser, user)

// In handlers
userID := c.GetString(ContextKeyUserID)
user := c.MustGet(ContextKeyUser).(*User)
```

2. **Create type-safe wrapper** for context access:
```go
type RequestContext struct {
    *gin.Context
}

func (rc *RequestContext) UserID() (string, error) {
    val, exists := rc.Get("userID")
    if !exists {
        return "", fmt.Errorf("userID not found in context")
    }
    userID, ok := val.(string)
    if !ok {
        return "", fmt.Errorf("userID is not string: %T", val)
    }
    return userID, nil
}

func (rc *RequestContext) User() (*User, error) {
    val, exists := rc.Get("user")
    if !exists {
        return nil, fmt.Errorf("user not found in context")
    }
    user, ok := val.(*User)
    if !ok {
        return nil, fmt.Errorf("user is not *User: %T", val)
    }
    return user, nil
}

// Usage in handler
func getProfileHandler(c *gin.Context) {
    rc := &RequestContext{c}
    userID, err := rc.UserID()
    if err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    user, err := rc.User()
    if err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    // ...
}
```

3. **Document expected context values**:
```go
// Context values populated by authMiddleware:
// - "userID" (string): JWT claim sub
// - "user" (*User): loaded from database
// - "token" (string): raw JWT token
//
// Handlers must depend on authMiddleware
```

---

## 5. Error Handling Evolution

### 5.1 Both Branches Change Error Handling Patterns

Go's error handling evolved significantly, and merge conflicts occur when branches use different patterns.

#### Error Handling Evolution in Go

```go
// Pre-Go 1.13: basic errors
err := SomeOperation()
if err != nil {
    return err  // No context about what operation failed
}

// Go 1.13+: error wrapping with fmt.Errorf and %w
err := SomeOperation()
if err != nil {
    return fmt.Errorf("processing user data: %w", err)
}

// Go 1.20+: multiple error wrapping
err := fmt.Errorf("operation failed: %w and %w", err1, err2)
```

#### Merge Conflict Scenario

```go
// Original
func processPayment(amount float64) error {
    result := apiCall()
    if result.err != nil {
        return result.err
    }
    return nil
}

// Branch A: adds error context
func processPayment(amount float64) error {
    result := apiCall()
    if result.err != nil {
        return fmt.Errorf("payment API failed: %w", result.err)
    }
    return nil
}

// Branch B: adds custom error type
type PaymentError struct {
    Amount float64
    Reason string
}
func (e PaymentError) Error() string {
    return fmt.Sprintf("payment of %.2f failed: %s", e.Amount, e.Reason)
}

func processPayment(amount float64) error {
    result := apiCall()
    if result.err != nil {
        return PaymentError{Amount: amount, Reason: result.err.Error()}
    }
    return nil
}

// After merge: which pattern?
// If both apply:
func processPayment(amount float64) error {
    result := apiCall()
    if result.err != nil {
        err := PaymentError{Amount: amount, Reason: result.err.Error()}
        return fmt.Errorf("payment API failed: %w", err)
    }
    return nil
}

// Results in nested wrapping: fmt.Errorf wraps PaymentError wraps original error
// Caller using errors.As() may not unwrap correctly
```

### 5.2 Error Wrapping Conflicts

The `%w` verb in fmt.Errorf allows error chains. Multiple patterns create merge conflicts.

#### Wrapping Pattern Merge Conflict

```go
// Branch A: wraps with %w
err := SomeOperation()
if err != nil {
    return fmt.Errorf("step A failed: %w", err)
}

// Branch B: wraps differently or uses errors.New + additional wrapping
err := SomeOperation()
if err != nil {
    log.Printf("error: %v", err)
    return fmt.Errorf("operation failed")  // NO %w - breaks chain!
}

// After merge: inconsistent wrapping patterns
if err != nil {
    return fmt.Errorf("step A failed: %w", err)  // Chain preserved
}
// vs
if err != nil {
    return fmt.Errorf("operation failed")  // Chain broken!
}

// Caller can't use errors.Unwrap() on Branch B's errors
var paymentErr PaymentError
if errors.As(err, &paymentErr) {
    // Works for Branch A chain
    // Fails for Branch B because wrapping is broken
}
```

#### Resolution Strategy

1. **Standardize wrapping pattern across codebase**:
```go
// Always use %w for wrapping
err := SomeOperation()
if err != nil {
    return fmt.Errorf("operation description: %w", err)
}

// Never break the chain
// WRONG: return fmt.Errorf("operation failed")  // Lost error context
// RIGHT: return fmt.Errorf("operation failed: %w", err)
```

2. **Merge wrapping styles carefully**:
```go
// If merging custom error type with %w wrapping
type PaymentError struct {
    Amount float64
    Cause error
}

func (e *PaymentError) Error() string {
    return fmt.Sprintf("payment of %.2f failed: %v", e.Amount, e.Cause)
}

func (e *PaymentError) Unwrap() error {
    return e.Cause  // Satisfy errors.Unwrap interface
}

// Now callers can chain:
err := PaymentError{Amount: 100, Cause: apiErr}
wrapped := fmt.Errorf("transaction failed: %w", err)

// Chain: wrapped -> PaymentError -> apiErr
```

3. **Use errors.Is() and errors.As() consistently**:
```go
result, err := processPayment()
if err != nil {
    // Check for specific error type in chain
    var paymentErr PaymentError
    if errors.As(err, &paymentErr) {
        log.Printf("Payment failed for %.2f: %v", paymentErr.Amount, paymentErr.Cause)
    }

    // Check for specific error value
    if errors.Is(err, ErrInsufficientFunds) {
        // refund and notify
    }

    return err
}
```

**Reference**: [Working with Errors in Go 1.13 - The Go Programming Language](https://go.dev/blog/go1.13-errors)

### 5.3 Custom Error Type Conflicts

Both branches may define similar or identical custom error types.

#### Custom Error Type Merge Conflict

```go
// Branch A
type ValidationError struct {
    Field   string
    Message string
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// Branch B
type ValidationError struct {
    Field   string
    Message string
    Value   interface{}  // Different - extra field
}

func (e ValidationError) Error() string {
    return fmt.Sprintf("invalid %s='%v': %s", e.Field, e.Value, e.Message)
}

// After merge: which ValidationError struct?
// If they have the same name, Git creates conflict
// After resolution, code using one pattern breaks

type ValidationError struct {
    Field   string
    Message string
    Value   interface{}  // Both versions merged
}
```

#### Resolution Strategy

1. **Combine error types if both are needed**:
```go
// After merge: unified ValidationError
type ValidationError struct {
    Field   string
    Message string
    Value   interface{}  // From Branch B
    // No conflict - have all needed fields
}

func (e ValidationError) Error() string {
    if e.Value != nil {
        return fmt.Sprintf("invalid %s='%v': %s", e.Field, e.Value, e.Message)
    }
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}
```

2. **Create error constructors** to avoid conflicts:
```go
// Exported functions provide consistent error creation
func NewValidationError(field, message string) ValidationError {
    return ValidationError{Field: field, Message: message}
}

func NewValidationErrorWithValue(field, message string, value interface{}) ValidationError {
    return ValidationError{Field: field, Message: message, Value: value}
}

// Both branches use these functions
// Adding fields to struct doesn't break existing callers
```

3. **Avoid duplicating errors across packages**:
If both branches define similar errors in different packages:
```go
// bad-merge: duplicate error types
// package/a
type ValidationError struct { ... }

// package/b
type ValidationError struct { ... }

// good-merge: centralized error types
// package/errors
type ValidationError struct { ... }
type PaymentError struct { ... }
type DatabaseError struct { ... }

// package/a and package/b import from package/errors
```

---

## 6. Validation Tools: What Each Catches

After resolving merge conflicts, validation tools detect problems at different levels.

### 6.1 go build ./...

**What it does**: Compiles all packages in the module.

**What it catches**:
- Syntax errors
- Undefined variables/functions/types
- Type mismatches in function calls
- Missing imports
- Circular import dependencies
- Interface satisfaction failures (if caught at compile time)

**What it MISSES**:
- Logic errors
- Uninitialized variables (if types allow zero value)
- Potential nil pointer dereferences
- Race conditions
- Unused variables/imports (only via flags)

**After merge, run first**:
```bash
go build ./...
# If this fails, merge is fundamentally broken
```

### 6.2 go vet ./...

**What it does**: Reports suspicious code patterns that are technically valid but likely bugs.

**What it catches**:
- Printf format string mismatches
- Unreachable code
- Assignments that don't affect output
- Suspicious comparisons
- Struct field alignment issues (via fieldalignment linter)
- Invalid method receivers
- Suspicious map operations
- Nil pointer dereferences (via nilness analysis)

**What it MISSES**:
- Most logic errors
- Performance problems
- Security issues (not specialized for security)
- Race conditions (requires -race flag at build time, not vet)

**After merge, run second**:
```bash
go vet ./...
go build -race ./...  # Detect data races
```

### 6.3 staticcheck

**What it does**: ~150 different static analysis checks, more sophisticated than go vet.

**What it catches**:
- Dead code elimination
- Inefficient code patterns
- Incorrect use of standard library
- Nil pointer dereferences (more thorough than vet)
- Redundant nil checks
- Unreachable code
- Unused variables/functions/types
- Incorrect error handling
- Resource leaks
- Synchronization issues

**What it MISSES**:
- Most business logic errors
- Security vulnerabilities (though catches some)
- Complex race conditions
- Performance regressions

**Installation and usage**:
```bash
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...
```

**After merge**:
```bash
go vet ./...
staticcheck ./...
go test -race ./...
```

### 6.4 golangci-lint

**What it does**: Orchestrates 50+ linters (includes go vet, staticcheck, revive, etc.) with intelligent caching.

**What it catches** (comprehensive):
- All issues from go vet
- All issues from staticcheck
- Additional style checks (revive)
- Security issues (gosec)
- Complexity metrics (gocyclo)
- Duplicate code (dupl)
- Error handling patterns
- Interface satisfaction
- Unused code
- Inefficient code

**Configuration**:
```yaml
# .golangci.yml
run:
  deadline: 5m
linters:
  enable:
    - staticcheck
    - golint
    - errcheck
    - unused
    - gosec
issues:
  exclude-rules:
    - path: _test\.go
      linters:
        - staticcheck
```

**After merge**:
```bash
go build ./...
go vet ./...
golangci-lint run ./...
go test -race ./...
```

### 6.5 Validation Workflow After Merge

**Comprehensive post-merge validation**:
```bash
#!/bin/bash
# Run after resolving merge conflicts

set -e

echo "=== Step 1: Basic Compilation ==="
go build ./...

echo "=== Step 2: Go Vet Checks ==="
go vet ./...

echo "=== Step 3: Staticcheck Analysis ==="
staticcheck ./...

echo "=== Step 4: Comprehensive Linting ==="
golangci-lint run ./...

echo "=== Step 5: Race Condition Detection ==="
go test -race ./...

echo "=== Step 6: Full Test Suite ==="
go test ./... -v

echo "All validation passed!"
```

**Key insight**: Each tool layer catches different issues:
- `go build`: Structural correctness
- `go vet`: Obvious bugs
- `staticcheck`: Subtle correctness issues
- `golangci-lint`: Style, complexity, security
- `go test -race`: Concurrency issues
- `go test ./...`: Business logic

---

## 7. Go 1.21+ Features Affecting Merging

### 7.1 Generic Type Parameter Conflicts

Go 1.18+ introduced generics. Merging generic code creates new conflict patterns.

#### Generic Type Declaration Merge Conflict

```go
// Original function
func FindItem(items []interface{}, target interface{}) interface{} {
    for _, item := range items {
        if item == target {
            return item
        }
    }
    return nil
}

// Branch A: refactors to generics
func FindItem[T comparable](items []T, target T) *T {
    for i, item := range items {
        if item == target {
            return &items[i]
        }
    }
    return nil
}

// Branch B: adds logging without generics
func FindItem(items []interface{}, target interface{}) interface{} {
    log.Printf("Searching for %v", target)
    for _, item := range items {
        if item == target {
            return item
        }
    }
    return nil
}

// After merge: generic or non-generic?
// Callers expecting generic signature fail if non-generic wins
items := []int{1, 2, 3}
result := FindItem(items, 2)  // Type error if non-generic signature chosen!
```

#### Generic Constraint Merge Conflict

```go
// Branch A: requires Ordered constraint
func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}

// Branch B: requires custom Reader constraint
func Min[T interface{ Read() }](a, b T) T {
    // Different constraint!
    // Can't compare with <, but has Read method
}

// After merge: which constraint?
// Type checking depends on correct constraint
result := Min(5, 3)  // Works with Ordered, fails with Reader
```

#### Resolution Strategy

1. **Prefer generics for type-safe merges**:
```go
// After merge: use generics if both branches add related types
func ProcessItems[T any](items []T, process func(T) error) error {
    for _, item := range items {
        if err := process(item); err != nil {
            return fmt.Errorf("processing failed: %w", err)
        }
    }
    return nil
}

// Supports both Branch A and B patterns type-safely
```

2. **Use `any` constraint when flexibility needed**:
```go
// When constraint doesn't matter
func Wrap[T any](value T) *T {
    return &value
}
```

3. **Define constraints in separate package**:
```go
// package constraints
type Numeric interface {
    int | int64 | float64
}

type Reader interface {
    Read() error
}

// package handlers - no conflict over constraint definition
func Sum[T Numeric](values []T) T {
    var total T
    for _, v := range values {
        total += v
    }
    return total
}
```

### 7.2 slog Structured Logging Conflicts

Go 1.21 introduced `log/slog` for structured logging. Merging old and new logging patterns creates conflicts.

#### Logging Pattern Merge Conflict

```go
// Original: unstructured logging
log.Printf("User %s created account", username)

// Branch A: migrates to slog
import "log/slog"
slog.Info("User account created", "username", username, "email", email)

// Branch B: stays with unstructured
log.Printf("User account created: username=%s, email=%s", username, email)

// After merge: mixed logging styles
slog.Info("User account created", "username", username)  // Branch A
log.Printf("User logged in: %s", username)               // Branch B

// Different parsers needed, inconsistent log structure
```

#### Logging Handler Conflict

```go
// Branch A: uses slog with JSON handler
import "log/slog"
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
logger := slog.New(handler)

// Branch B: uses slog with text handler
import "log/slog"
handler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelDebug,
})
logger := slog.New(handler)

// After merge: which handler?
// Logs appear in different format depending on merge outcome
```

#### Resolution Strategy

1. **Migrate completely to slog if Go 1.21+**:
```go
// Single logging pattern throughout
import "log/slog"

// Initialize at main()
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
logger := slog.New(handler)
slog.SetDefault(logger)

// Use throughout application
slog.Info("processing request", "user", userID, "action", action)
slog.Error("database error", "query", query, "error", err)
```

2. **If mixing old and new**, use adapter:
```go
// package logging
import (
    "log"
    "log/slog"
)

// Adapter for gradual migration
func InfoCompat(msg string, args ...interface{}) {
    slog.Info(msg, convertArgs(args)...)
}

// Where convertArgs transforms varargs to key-value pairs
```

3. **Define logger at package initialization**:
```go
// package handlers
import "log/slog"

var logger = slog.Default()

func setupHandler(c *gin.Context) {
    logger.Info("handling request", "path", c.Request.URL.Path)
    // Consistent logger usage across package
}
```

**Reference**: [Structured Logging with slog - The Go Programming Language](https://go.dev/blog/slog)

### 7.3 maps and slices Package Usage

Go 1.21 added generic `maps` and `slices` packages. Merging custom implementations with stdlib creates conflicts.

#### Custom vs Standard Implementation Merge Conflict

```go
// Branch A: implements custom Reverse for slices
func Reverse[T any](s []T) {
    for i, j := 0, len(s)-1; i < j; i, j = i+1, j-1 {
        s[i], s[j] = s[j], s[i]
    }
}

// Branch B: uses slices.Reverse from stdlib
import "slices"
slices.Reverse(items)

// After merge: duplicate implementations
func Reverse[T any](s []T) { ... }  // Custom, unused if slices used elsewhere
items := slices.Reverse(items)      // Stdlib, conflicts with custom

// Confusing: which Reverse used? Results may differ!
```

#### Resolution Strategy

1. **Prefer stdlib packages (maps, slices) if Go 1.21+**:
```go
import "slices"
import "maps"

// Standard implementations
slices.Contains(items, target)
slices.Sort(items)
slices.Reverse(items)

maps.Keys(myMap)
maps.Values(myMap)
maps.Equal(map1, map2)

// Don't define custom versions
```

2. **If custom required, use clear naming**:
```go
// package myutils
func ReverseInPlace[T any](s []T) { ... }

// vs stdlib
// import "slices"
// items = slices.Reverse(items)

// Different names prevent merge confusion
```

3. **Update dependencies when migrating**:
After merge, ensure all code uses stdlib versions:
```bash
# Find custom slice/map utilities
grep -r "func.*Reverse\|func.*Keys\|func.*Values" *.go

# Replace with stdlib equivalents
go mod tidy
```

---

## Summary: Merge Conflict Resolution Checklist

After resolving a Go merge conflict:

1. **Structural Issues**
   - [ ] `go build ./...` passes (basic compilation)
   - [ ] `go vet ./...` passes (obvious bugs)
   - [ ] Interface satisfaction maintained (use `var _ Interface = (*Type)(nil)`)

2. **Module Dependencies**
   - [ ] Resolve `go.mod` to highest version of each distinct module
   - [ ] Delete and regenerate `go.sum`
   - [ ] Run `go mod tidy`
   - [ ] No conflicting `replace` directives

3. **Struct and Type Safety**
   - [ ] Field ordering optimized (use fieldalignment linter)
   - [ ] All struct tags present (json, bson, db if needed)
   - [ ] Embedded struct conflicts resolved

4. **Interfaces and Abstractions**
   - [ ] No methods added to exported interfaces (create new interface if needed)
   - [ ] All implementations satisfy interfaces
   - [ ] No loss of interface satisfaction after merge

5. **Gin Framework (if applicable)**
   - [ ] No duplicate routes (same method + path)
   - [ ] Middleware order reviewed for security
   - [ ] Handler signatures match `gin.HandlerFunc`
   - [ ] Context key conflicts resolved (use constants)

6. **Error Handling**
   - [ ] Error wrapping consistent (always use `%w` for chains)
   - [ ] Custom error types unified if duplicated
   - [ ] Error interface{} to concrete type migrations handled

7. **Modern Go Features (1.21+)**
   - [ ] Generic type constraints compatible
   - [ ] Logging unified (prefer slog for Go 1.21+)
   - [ ] No duplicate stdlib and custom slice/map utilities

8. **Comprehensive Validation**
   - [ ] `staticcheck ./...` passes
   - [ ] `golangci-lint run ./...` passes
   - [ ] `go test -race ./...` passes
   - [ ] `go test ./... -v` passes
   - [ ] Code review for business logic

---

## References

- [Struct Field Alignment - Go Optimization Guide](https://goperf.dev/01-common-patterns/fields-alignment/)
- [Keeping Your Modules Compatible - The Go Programming Language](https://go.dev/blog/module-compatibility)
- [Ensuring Go interface satisfaction at compile-time](https://medium.com/stupid-gopher-tricks/ensuring-go-interface-satisfaction-at-compile-time-1ed158e8fa17)
- [Go Modules Reference - The Go Programming Language](https://go.dev/ref/mod)
- [research!rsc: Minimal Version Selection](https://research.swtch.com/vgo-mvs)
- [Middleware - Gin Web Framework](https://gin-gonic.com/en/docs/middleware/)
- [Working with Errors in Go 1.13 - The Go Programming Language](https://go.dev/blog/go1.13-errors)
- [An Introduction To Generics - The Go Programming Language](https://go.dev/blog/intro-generics)
- [Structured Logging with slog - The Go Programming Language](https://go.dev/blog/slog)
- [Go Wiki: CodeTools](https://go.dev/wiki/CodeTools)
- [How to use go vet, gofmt, and golint](https://sparkbox.com/foundry/go_vet_gofmt_golint_to_code_check_in_Go)
- [Quick Start – Golangci-lint](https://golangci-lint.run/docs/welcome/quick-start/)
