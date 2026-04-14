# Rust Refactoring Patterns

Patterns specific to Rust projects.

## Table of Contents

1. [Error Handling](#error-handling)
2. [Ownership & Borrowing](#ownership)
3. [API Design](#api-design)
4. [Modernization](#modernization)
5. [Async Patterns](#async)

---

## Error Handling

### 1. unwrap() → ? Operator
**Risk: Medium**
```rust
// Before
let data = fs::read_to_string("config.toml").unwrap();
let config: Config = toml::from_str(&data).unwrap();

// After
let data = fs::read_to_string("config.toml")?;
let config: Config = toml::from_str(&data)?;
```
- Must: Function return type must be `Result<T, E>`
- Safety: Audit ALL unwrap() calls; each is a potential panic

### 2. Custom Error Types (thiserror)
**Risk: Low** (for libraries)
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    Parse(#[from] toml::de::Error),
    #[error("Not found: {0}")]
    NotFound(String),
}
```
- Libraries: Use `thiserror` for typed, matchable errors
- Applications: Use `anyhow` for ergonomic context-rich errors
- Safety: Ensure From implementations cover all error sources

### 3. String Error Messages → Typed Errors
**Risk: Low**
```rust
// Before: Err("invalid input".to_string())
// After:  Err(AppError::InvalidInput { field: "email" })
```

---

## Ownership & Borrowing

### 4. String → &str in Parameters
**Risk: Low**
```rust
// Before: fn greet(name: String) → takes ownership
// After:  fn greet(name: &str)   → borrows
```
- When: Function doesn't need to own the string
- Safety: Compiler enforces; if it compiles, it's correct

### 5. Clone Elimination
**Risk: Low**
```rust
// Before: let copy = data.clone(); process(copy);
// After:  process(&data);  // borrow instead
```
- Safety: If the borrow checker accepts it, it's safe
- When clone is needed: shared ownership → use `Arc<T>` or `Rc<T>`

### 6. Lifetime Simplification
**Risk: Medium**
- Rust's lifetime elision rules handle most cases
- Remove explicit lifetimes when the compiler can infer them
```rust
// Before: fn first<'a>(s: &'a str) -> &'a str
// After:  fn first(s: &str) -> &str  // elision handles this
```
- Safety: If it compiles without lifetimes, the elision rules match your intent

---

## API Design

### 7. Trait Extraction
**Risk: Low**
```rust
// Before: fn process(db: &PostgresDB)
// After:
trait DataStore {
    fn query(&self, q: &str) -> Result<Vec<Row>>;
}
fn process(db: &impl DataStore)
```
- Enables mocking in tests
- Keep traits small and focused

### 8. From/Into Implementations
**Risk: Low**
```rust
impl From<&str> for MyType {
    fn from(s: &str) -> Self { /* ... */ }
}
// Now: let x: MyType = "hello".into();
```
- Conversions should be lossless and obvious

### 9. Builder Pattern
**Risk: Low**
```rust
let config = ConfigBuilder::new()
    .port(8080)
    .host("localhost")
    .build()?;
```
- When: Struct has >4 fields, some optional
- Safety: Builder validates at .build() time

---

## Modernization

### 10. Iterator Chains
**Risk: Low**
```rust
// Before
let mut results = Vec::new();
for item in &items {
    if item.active {
        results.push(item.value * 2);
    }
}

// After
let results: Vec<_> = items.iter()
    .filter(|i| i.active)
    .map(|i| i.value * 2)
    .collect();
```
- Often faster due to iterator fusion; always more idiomatic

### 11. Enum Refinement
**Risk: Medium**
- Replace stringly-typed states with enums
- Use enum variants with data for state machines
- Safety: Compiler enforces exhaustive matching

---

## Async

### 12. Blocking → Async
**Risk: Medium**
```rust
// Before: std::fs::read_to_string(path)
// After:  tokio::fs::read_to_string(path).await
```
- Never use blocking calls inside async functions
- Use `tokio::task::spawn_blocking` for CPU-intensive work
- Safety: Verify no blocking operations in async context

---

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| rustfmt | Formatting | `cargo fmt` |
| clippy | Comprehensive linting | `cargo clippy -- -D warnings` |
| cargo-audit | Security vulnerabilities | `cargo audit` |
| cargo-outdated | Dependency freshness | `cargo outdated` |
| cargo-geiger | Unsafe code detection | `cargo geiger` |
