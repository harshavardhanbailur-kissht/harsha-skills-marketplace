# Language-Specific Parsing Heuristics

## Python

### Import Analysis Patterns

**Standard imports indicating core dependencies:**
```python
import os, sys, json, logging  # stdlib essentials
from typing import List, Dict, Optional  # typing indicators
from dataclasses import dataclass  # modern Python (3.7+)
from pathlib import Path  # modern stdlib (3.4+)
```

**Detection strategy:**
1. Scan `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile`
2. Extract top-level packages: `numpy`, `django`, `flask`, `sqlalchemy`, `pydantic`
3. Analyze import distribution:
   - 30%+ stdlib = mature, minimal dependencies
   - 50%+ data science libs = ML/analytics focus
   - 40%+ web framework = web application

**Dependency classification:**
- **Core framework**: Django, Flask, FastAPI, Celery, SQLAlchemy
- **Data handling**: Pandas, NumPy, SciPy, Polars, Dask
- **Testing**: pytest, unittest, mock, hypothesis
- **Async**: asyncio, aiohttp, aiokafka
- **Message queues**: pika, kafka-python, celery-redis

### Test Framework Detection

**pytest indicators:**
```python
def test_xxx():  # Function-based tests
@pytest.fixture  # Fixture decorators
assert result == expected  # Assertion style
```
- `conftest.py` files indicate fixture sharing
- `-m pytest` in CI/CD
- `pytest.ini` or `[tool.pytest]` in `pyproject.toml`

**unittest indicators:**
```python
class TestXxx(unittest.TestCase):
    def setUp(self): ...
    def tearDown(self): ...
    self.assertEqual(...)
```
- Older codebases prefer unittest
- Class-based structure
- More verbose setup/teardown

**Testing coverage signals:**
- `coverage` or `pytest-cov` in dependencies
- `.coveragerc` config file
- CI checks for coverage thresholds

### Build System Recognition

**Setup.py indicator:**
```python
from setuptools import setup
setup(name='package', version='1.0.0', packages=find_packages())
```
- Legacy build system (Python < 3.10)
- Custom build logic often embedded

**Pyproject.toml (modern standard):**
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "package"
version = "1.0.0"
```
- PEP 517/518 compliant
- Single source of truth for metadata

**Poetry indicator:**
```toml
[tool.poetry]
name = "package"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.8"
```
- Dependency locking via `poetry.lock`
- Virtual env management

**PDM indicator:**
```toml
[project]
dependencies = [...]

[tool.pdm]
```
- Lightweight, PEP 582 backend
- Lock file: `pdm.lock`

**Dependency extraction:**
```bash
# Extract from requirements.txt
cat requirements.txt | grep -v "^#" | cut -d'[' -f1

# Extract from setup.py
grep "install_requires=\|requires=" setup.py

# Extract from pyproject.toml
toml parse dependencies
```

### Async/Await Patterns

**Asyncio usage indicators:**
```python
import asyncio
async def fetch_data(): ...
await some_coroutine()
asyncio.run(main())
```

**Async web frameworks:**
- FastAPI: `async def route_handler()`
- AIOHTTP: `async with session.get()`
- Starlette: ASGI-based async

**Detection approach:**
- Count `async def` functions
- Identify `await` calls
- Check for event loop initialization
- Look for `concurrent.futures.ThreadPoolExecutor` (hybrid approach)

**Async signal strength:**
- 30%+ async functions = async-first design
- 10-30% async = selective async (I/O operations)
- <10% async = primarily synchronous with async wrappers

### Type Hint Maturity

**Type hint presence levels:**
```python
# Level 1: No hints
def fetch_data(user_id):
    return db.query(user_id)

# Level 2: Partial hints
def fetch_data(user_id: int) -> dict:
    return db.query(user_id)

# Level 3: Full hints with generics
def fetch_data(user_id: int) -> Dict[str, Any]:
    return db.query(user_id)

# Level 4: Advanced (Protocol, TypeVar, overload)
from typing import Protocol, TypeVar
T = TypeVar('T')
def fetch_data(user_id: int) -> T: ...
```

**Mypy integration indicators:**
- `[tool.mypy]` in `pyproject.toml`
- `.mypy.ini` file
- CI integration: `mypy check` step

**Type maturity scoring:**
- No hints: 0 points
- Partial hints: 20-40 points
- Full hints: 60-80 points
- Strict mode + Protocol usage: 90-100 points

### Dataclass vs NamedTuple vs Pydantic

**Dataclass (Python 3.7+):**
```python
from dataclasses import dataclass
@dataclass
class User:
    id: int
    name: str
```
- Mutable by default
- Auto-generates `__init__`, `__repr__`, `__eq__`
- Indicates Python 3.7+ modern style

**NamedTuple:**
```python
from typing import NamedTuple
class User(NamedTuple):
    id: int
    name: str
```
- Immutable (tuple-based)
- Serializable
- Lightweight

**Pydantic:**
```python
from pydantic import BaseModel
class User(BaseModel):
    id: int
    name: str
```
- Validation on instantiation
- JSON serialization
- Extra field handling
- Indicates validation-heavy domain (fintech, healthcare)

**Classification:**
- All dataclasses = Python-native, simple value objects
- Mix of dataclass + Pydantic = Pydantic for external API boundaries
- Pure Pydantic = validation-critical domain

---

## JavaScript / TypeScript

### Module System Detection

**CommonJS (Node.js traditional):**
```javascript
const express = require('express');
module.exports = myFunction;
```
- Older codebases, backend-only
- `require()` calls

**ES6 Modules (modern standard):**
```javascript
import express from 'express';
export default myFunction;
```
- Modern codebases
- Bundler-friendly
- Tree-shaking capable

**Hybrid (CommonJS with ES6 import):**
- Indicates transpilation step
- `babel` or TypeScript compiler

**Detection:**
```bash
# CommonJS prevalence
grep -r "require(" src/ | wc -l
grep -r "import " src/ | wc -l
```

### TypeScript vs JavaScript

**TypeScript indicators:**
- `*.ts` or `*.tsx` file extensions
- `tsconfig.json` present
- `tsc` in build scripts
- Type annotations: `const x: string = ""`

**TypeScript strictness levels:**
```json
{
  "compilerOptions": {
    "strict": true,           // All strict checks
    "noImplicitAny": true,    // Catch untyped vars
    "strictNullChecks": true  // Null safety
  }
}
```

**Strictness scoring:**
- Strict mode enabled + 90%+ typed: 90+ score (high confidence)
- Mixed typed/untyped with strict: 60-80 score
- No strict mode: <60 score

**Type coverage tools:**
- `type-coverage`: Reports percentage of typed code
- `typescript-eslint`: Linting typed code

### Testing Framework Detection

**Jest (most common):**
```javascript
describe('MyComponent', () => {
  it('should render', () => {
    expect(component).toBeDefined();
  });
});
```
- `jest.config.js` present
- Snapshot testing capability

**Mocha + Chai:**
```javascript
describe('MyComponent', () => {
  it('should render', () => {
    expect(component).to.be.defined;
  });
});
```
- More verbose assertion style
- `.mocharc.js` config

**Vitest (modern alternative):**
- TypeScript-first
- Faster than Jest
- `vitest.config.ts` file
- Gaining adoption in 2024+

**React Testing Library vs Enzyme:**
- React Testing Library: Query by role/label (behavioral testing)
- Enzyme: Query by component structure (implementation testing)
- Library choice indicates testing philosophy

### React Component Patterns

**Class components (legacy):**
```javascript
class MyComponent extends React.Component {
  render() { return <div>...</div>; }
}
```
- Older codebases
- Lifecycle methods: `componentDidMount`, `componentWillUnmount`

**Functional components + Hooks (modern):**
```javascript
function MyComponent({ prop }) {
  const [state, setState] = useState(null);
  useEffect(() => { ... }, []);
  return <div>...</div>;
}
```
- React 16.8+
- Hooks indicate modern React (2019+)

**Custom hooks:**
```javascript
function useUser(id) {
  const [user, setUser] = useState(null);
  useEffect(() => { ... }, [id]);
  return user;
}
```
- Code reuse pattern
- Higher sophistication indicator

**Hook prevalence scoring:**
- 0% hooks, all class components: Legacy, likely React 15
- 30-70% mixed: Migration in progress
- >90% hooks: Modern, React 16.8+

### Dependency Injection in JavaScript

**Constructor injection:**
```javascript
class Service {
  constructor(dependency) {
    this.dependency = dependency;
  }
}
```

**Module-level singleton:**
```javascript
const db = new Database();
export default db;
```

**Dependency injection frameworks:**
- NestJS: Decorator-based (TypeScript)
- TypeDI: Reflection-based (TypeScript)
- Awilix: Manual container (JavaScript)

**Signal of maturity:**
- Manual DI (constructor params): 40 points
- DI container: 70 points
- Testable mocks without DI container: 80 points

### Build and Bundler Detection

**Webpack:**
- `webpack.config.js` present
- Complex configuration, enterprise standard
- Loader ecosystem for CSS, images, etc.

**Vite:**
- `vite.config.ts` or `vite.config.js`
- Modern, ES modules-based, fast
- Gaining adoption 2022+

**Turbopack:**
- `turbopack.config.ts`
- Next.js 13+ bundler

**Esbuild:**
- Minimal config, fast
- Used in tools, libraries

**Package manager detection:**
```bash
# npm
ls package-lock.json && echo "npm"
# yarn
ls yarn.lock && echo "yarn"
# pnpm
ls pnpm-lock.yaml && echo "pnpm"
```

**Monorepo indicators:**
- `lerna.json` (Lerna)
- `pnpm-workspace.yaml` (pnpm workspaces)
- `package.json` with `workspaces` field

---

## Go

### Import Analysis

**Standard library heavy:**
```go
import (
    "fmt"
    "net/http"
    "encoding/json"
)
```
- Mature, minimal external dependencies
- Stdlib sufficiency

**Third-party framework usage:**
```go
import "github.com/gin-gonic/gin"  // Gin web framework
import "gorm.io/gorm"              // GORM ORM
import "github.com/spf13/cobra"    // CLI framework
```

**Dependency indicator:**
- `go.mod` version pinning
- `go.sum` integrity checking
- Import count > 50 external = significant complexity

### Testing Patterns

**Standard testing package (idiomatic):**
```go
package mypackage_test

import "testing"

func TestFunction(t *testing.T) {
    result := Function()
    if result != expected {
        t.Errorf("expected %v, got %v", expected, result)
    }
}
```
- `*_test.go` file naming convention
- `testing.T` interface for assertions
- Table-driven tests common

**Table-driven test pattern:**
```go
tests := []struct {
    name     string
    input    string
    expected string
}{
    {"test1", "a", "A"},
    {"test2", "b", "B"},
}
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        // test
    })
}
```
- Indicates mature Go code
- Minimal test duplication

**Testing framework usage:**
- `github.com/stretchr/testify`: `assert`, `require` helpers
- `github.com/onsi/ginkgo`: BDD-style
- Pure stdlib: Most idiomatic

### Concurrency Patterns

**Goroutine prevalence:**
```go
go func() { ... }()        // Fire-and-forget
go someFunction()
```
- Count `go ` keyword occurrences
- Indicates concurrent design

**Channel patterns:**
```go
done := make(chan bool)
results := make(chan Result, 10)  // Buffered channel
for range results { ... }          // Range over channel
```

**Concurrency sophistication scoring:**
- No goroutines: Synchronous, simple
- 5-20 goroutines: Selective async (HTTP handlers, workers)
- 50+ goroutines: Concurrent-first design
- Complex channel orchestration: Advanced

### Package Organization

**By feature (recommended):**
```
users/
  user.go       // Domain model
  repository.go // Data access
  service.go    // Business logic
  handler.go    // HTTP handler
```

**By layer (less idiomatic):**
```
models/
services/
handlers/
repositories/
```

**Detection approach:**
- Count files per package
- Measure package interdependencies
- Assess if packages are independently deployable

### Error Handling Style

**Explicit error checking (idiomatic):**
```go
err := doSomething()
if err != nil {
    return fmt.Errorf("failed: %w", err)
}
```

**Error wrapping maturity (Go 1.13+):**
- `fmt.Errorf("... %w", err)`: Modern
- `errors.Wrap(err, "msg")`: Legacy (pkg/errors)

**Panic recovery (escape hatches):**
```go
defer func() {
    if r := recover(); r != nil {
        // Handle panic
    }
}()
```
- Rare in production Go
- Indicates exceptional cases or legacy code

---

## Rust

### Ownership & Borrowing Patterns

**Ownership transfer:**
```rust
fn take_ownership(s: String) { ... }  // Moves s
let s = String::from("hello");
take_ownership(s);  // s is moved, no longer available
```

**Borrowing (references):**
```rust
fn borrow(s: &String) { ... }  // Immutable borrow
fn borrow_mut(s: &mut String) { ... }  // Mutable borrow
```

**Borrowing sophistication:**
- Heavy move semantics: Compile-learning curve, safety-focused
- Heavy borrowing: More functional style
- Unsafe blocks: Production efficiency concerns

### Result & Option Patterns

**Result type for fallible operations:**
```rust
fn risky() -> Result<String, Error> {
    Ok(value)?  // Early return on error
}
```

**Option type for nullable values:**
```rust
let maybe: Option<String> = None;
match maybe {
    Some(val) => { ... }
    None => { ... }
}
```

**Pattern matching usage:**
- Heavy pattern matching: Functional, exhaustive
- If-let shortcuts: Pragmatic balance

### Async/Await (Rust 1.39+)

**Async function definition:**
```rust
async fn fetch() -> Result<String> {
    let response = reqwest::get(url).await?;
    Ok(response.text().await?)
}
```

**Async runtime selection:**
- `tokio`: Industry standard
- `async-std`: Alternative
- Multiple runtimes: Flexibility concern

### Unsafe Blocks

**Unsafe code prevalence:**
```rust
unsafe {
    ptr::write(raw_ptr, value);
}
```

**Unsafe audit:**
- Count `unsafe` blocks
- Verify justification comments
- Check peer review evidence

**Unsafe ratio scoring:**
- 0% unsafe: Pure safe Rust
- <5% unsafe: Well-justified performance
- >10% unsafe: Performance critical or legacy C FFI

### Macro Usage

**Declarative macros:**
```rust
macro_rules! vec! {
    ( $( $x:expr ),* ) => { ... }
}
```

**Procedural macros (derive, attribute):**
```rust
#[derive(Debug, Clone)]
struct MyStruct { ... }
```

**Macro complexity:**
- Derive macro usage: Common, standard library patterns
- Custom declarative macros: Advanced metaprogramming

---

## Java

### Dependency Management

**Maven indicators:**
- `pom.xml` present
- Transitive dependency management
- Central repository integration

**Gradle indicators:**
- `build.gradle` or `build.gradle.kts` (Kotlin DSL)
- More concise syntax
- Task-based build system

**Dependency declaration extraction:**
```xml
<!-- Maven -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

```gradle
// Gradle
dependencies {
  implementation 'org.springframework.boot:spring-boot-starter-web'
}
```

### Test Framework Detection

**JUnit 4 (legacy):**
```java
@RunWith(SpringRunner.class)
public class MyTest {
    @Test
    public void testSomething() { ... }
}
```

**JUnit 5 (modern):**
```java
@ExtendWith(SpringExtension.class)
class MyTest {
    @Test
    void testSomething() { ... }
}
```

**Testing libraries:**
- Mockito: Mocking framework
- AssertJ: Fluent assertions
- Hamcrest: Matcher library

### Dependency Injection

**Spring Framework patterns:**
```java
@Autowired
private MyService service;

// Or constructor injection (preferred)
public MyController(MyService service) {
    this.service = service;
}
```

**Spring Boot indicators:**
- `@SpringBootApplication`
- Application auto-configuration

### Build Tools and Java Version

**Java version detection:**
- `pom.xml`: `<source>`, `<target>` tags
- `gradle.build`: `sourceCompatibility`, `targetCompatibility`
- `MANIFEST.MF`: `Specification-Version`

**Java version maturity:**
- Java 8: Introduced lambdas, streams
- Java 11: LTS, modules
- Java 17: LTS, sealed classes, records
- Java 21: LTS, virtual threads

### Stream API Usage

**Functional stream style:**
```java
List<String> result = users.stream()
    .filter(u -> u.isActive())
    .map(User::getName)
    .collect(Collectors.toList());
```

**Stream prevalence:**
- 30%+ stream usage: Functional orientation
- 10-30%: Selective functional patterns
- <10%: Imperative style

---

## C#

### Async/Await Patterns

**Modern async style:**
```csharp
public async Task<string> FetchDataAsync() {
    return await client.GetStringAsync(url);
}
```

**Async method naming convention:**
- `*Async` suffix indicates async methods
- Prevalence indicates modern codebase

### Dependency Injection

**Built-in (ASP.NET Core):**
```csharp
services.AddScoped<IRepository, SqlRepository>();

public class Service {
    public Service(IRepository repo) { ... }
}
```

### LINQ Patterns

**Query syntax:**
```csharp
var query = from u in users
            where u.IsActive
            select u.Name;
```

**Method syntax:**
```csharp
var query = users.Where(u => u.IsActive).Select(u => u.Name);
```

**LINQ sophistication:**
- Heavy query syntax: Older style (C# 3.0)
- Method syntax: Modern (C# 6+)

---

## Ruby

### Testing Frameworks

**RSpec (BDD-style):**
```ruby
describe User do
  it "should be valid" do
    expect(user).to be_valid
  end
end
```

**Minitest (unit-style):**
```ruby
class UserTest < Minitest::Test
  def test_valid
    assert user.valid?
  end
end
```

### Rails Conventions

**Standard Rails structure:**
```
app/
  models/
  controllers/
  views/
  services/     # Non-standard, indicates service layer
config/
spec/ or test/
Gemfile        # Dependency specification
```

### Dependency Management

**Gemfile patterns:**
```ruby
gem 'rails', '~> 7.0'
gem 'pg', '>= 1.0'
group :test do
  gem 'rspec-rails'
end
```

**Lock file: Gemfile.lock** ensures reproducible builds

---

## PHP

### Framework Detection

**Laravel indicators:**
- `app/`, `routes/`, `config/` directories
- `composer.json` with Laravel dependency
- Artisan command structure

**Symfony indicators:**
- `src/`, `config/` structure
- Service container usage
- Bundle organization

### Test Framework Detection

**PHPUnit (standard):**
```php
class UserTest extends TestCase {
    public function test_user_creation() { ... }
}
```

**Pest (modern alternative):**
```php
test('user can be created', function() { ... });
```

### Type Hints (PHP 7.0+)

**Type hint maturity:**
```php
// PHP < 7.0 (no type hints)
function fetch($id) { ... }

// PHP 7.0+ (parameter type hints)
function fetch(int $id): User { ... }

// PHP 7.4+ (property type hints)
private string $name;
```

**Return type indicators:**
- Return type declarations: Modern PHP (7.0+)
- Strict types: `declare(strict_types=1);` indicates discipline

---

## Kotlin

### Coroutine Patterns

**Coroutine integration (Kotlin specific):**
```kotlin
GlobalScope.launch {
    val data = fetchData()  // Suspension point
}
```

**Structured concurrency (modern):**
```kotlin
runBlocking {
    val data = async { fetchData() }.await()
}
```

### Extension Functions

**Indicates Kotlin-idiomatic code:**
```kotlin
fun String.isValidEmail(): Boolean {
    return this.contains("@")
}

"user@example.com".isValidEmail()
```

### Data Classes

**Modern value object pattern:**
```kotlin
data class User(val id: Int, val name: String)
```
- Auto-generates equals, hashCode, toString, copy

---

## Swift

### Protocol-Oriented Programming

**Protocol definition:**
```swift
protocol Repository {
    func fetch(_ id: Int) -> Item?
}
```

**Composition over inheritance:**
- Heavy protocol usage: Modern Swift
- Class inheritance: Objective-C heritage

### Async/Await (Swift 5.5+)

**Modern concurrency:**
```swift
async func fetchData() -> String {
    return try await networkCall()
}
```

### Property Wrappers

**@Property pattern:**
```swift
@Published var count: Int = 0
@State var isLoading = false
```
- Modern Swift (5.1+)
- Declarative state management

---

## Cross-Language Patterns

### Dependency Extraction Workflow

```
1. Identify package/dependency format
   └─> requirements.txt, go.mod, Cargo.toml, pom.xml, package.json
2. Parse for external dependencies
   └─> Filter stdlib/standard library
3. Categorize by type
   └─> Web frameworks, databases, testing, utilities
4. Analyze import prevalence
   └─> Which deps are actually used?
5. Assess dependency health
   └─> Last update date, security vulnerabilities, activity
```

### Build System Maturity Indicators

- **No explicit build tool**: Scripts or makefile = low maturity
- **Basic tool (Maven, npm, pip)**: Standard maturity
- **Tool plugins, custom tasks**: High maturity
- **Reproducible, hermetic builds**: Production-grade

### Testing Maturity Scoring

| Metric | Score |
|--------|-------|
| No tests | 10 |
| Unit tests only | 40 |
| Unit + integration tests | 70 |
| Full pyramid (unit/integration/E2E) | 90 |
| Test coverage >80% | +20 |
| Mutation testing configured | +10 |

---

## Quick Detection Checklist

- [ ] Identify primary language
- [ ] Locate dependency manifest (package.json, requirements.txt, etc.)
- [ ] Extract top-level dependencies
- [ ] Identify test framework and coverage
- [ ] Detect build system and version pinning
- [ ] Assess async/concurrency patterns
- [ ] Measure type safety indicators
- [ ] Identify framework-specific patterns
- [ ] Check for polyglot elements (multiple languages)
- [ ] Note deviations from language idioms
