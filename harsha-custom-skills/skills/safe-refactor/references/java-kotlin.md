# Java / Kotlin Refactoring Patterns

Patterns specific to JVM languages including Spring, Android, and general JVM.

## Table of Contents

1. [Java Modernization](#java-modernization)
2. [Kotlin Idioms](#kotlin-idioms)
3. [Both: Structural](#structural)
4. [Tools](#tools)

---

## Java Modernization

### 1. POJO → Records (Java 16+)
**Risk: Low**
```java
// Before
public class Point {
    private final int x, y;
    public Point(int x, int y) { this.x = x; this.y = y; }
    public int x() { return x; }
    public int y() { return y; }
    // equals, hashCode, toString...
}

// After
public record Point(int x, int y) {}
```
- When: Immutable data carriers; no inheritance needed
- Safety: Records are final; check no subclasses exist
- Watch: Serialization behavior may differ; verify if using Jackson/Gson

### 2. if-else Chains → Switch Expressions (Java 14+)
**Risk: Low**
```java
// Before
String result;
if (status == ACTIVE) result = "Active";
else if (status == INACTIVE) result = "Inactive";
else result = "Unknown";

// After
String result = switch (status) {
    case ACTIVE -> "Active";
    case INACTIVE -> "Inactive";
    default -> "Unknown";
};
```
- Safety: Compiler warns on non-exhaustive switches with enums

### 3. Anonymous Classes → Lambdas (Java 8+)
**Risk: Low**
```java
// Before
button.addListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) { handle(e); }
});

// After
button.addListener(e -> handle(e));
```
- When: Single Abstract Method (SAM) interfaces
- Safety: Variable capture must be effectively final

### 4. Imperative Loops → Streams API
**Risk: Medium**
```java
// Before
List<String> names = new ArrayList<>();
for (User u : users) {
    if (u.isActive()) names.add(u.getName());
}

// After
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .toList();
```
- Safety: Streams are lazy; verify terminal operations present
- Watch: Performance in hot loops; streams have overhead
- Anti-pattern: Don't use parallel streams without benchmarking

### 5. Optional Usage
**Risk: Low**
```java
// Before: if (user != null) return user.getName(); else return "Unknown";
// After:  return Optional.ofNullable(user).map(User::getName).orElse("Unknown");
```
- When: Method return types; NOT for fields or parameters
- Safety: Don't use Optional.get() without isPresent()

---

## Kotlin Idioms

### 6. Java-style → Kotlin Idiomatic
**Risk: Low**
```kotlin
// Before (Java-style in Kotlin)
fun getUser(id: Int): User? {
    val user = repository.findById(id)
    if (user != null) {
        return user
    } else {
        return null
    }
}

// After (Kotlin idiomatic)
fun getUser(id: Int): User? = repository.findById(id)
```

### 7. Callbacks → Coroutines
**Risk: Medium**
```kotlin
// Before
api.fetchUser(id, object : Callback<User> {
    override fun onSuccess(user: User) { updateUI(user) }
    override fun onError(e: Exception) { showError(e) }
})

// After
try {
    val user = api.fetchUser(id)  // suspend function
    updateUI(user)
} catch (e: Exception) {
    showError(e)
}
```
- Safety: Ensure proper CoroutineScope; handle cancellation
- Watch: Don't use GlobalScope; prefer viewModelScope/lifecycleScope

### 8. Nullable Handling
**Risk: Low**
```kotlin
// AVOID: !! (non-null assertion) — crashes at runtime
val name = user!!.name  // Bad

// PREFER: safe call + elvis
val name = user?.name ?: "Unknown"

// PREFER: let for scoped null checks
user?.let { processUser(it) }
```
- Audit: Find all `!!` usages; replace with safe alternatives

### 9. Data Classes & Sealed Classes
**Risk: Low**
```kotlin
// Value objects
data class Point(val x: Int, val y: Int)

// Algebraic data types
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}
```
- When: Replace Java-style POJOs with data classes
- Safety: `copy()` method behavior; verify destructuring usage

---

## Structural

### 10. Dependency Injection Cleanup
**Risk: Medium**
- Prefer constructor injection over field injection
- Replace `@Autowired` field injection with constructor params
```java
// Before
@Service
public class UserService {
    @Autowired private UserRepository repo;
}

// After
@Service
public class UserService {
    private final UserRepository repo;
    public UserService(UserRepository repo) { this.repo = repo; }
}
```
- Safety: Spring auto-detects single-constructor injection

### 11. God Class Decomposition
**Risk: High**
- When: Service class has >500 lines, >10 methods
- Extract domain-specific services
- Safety: Map all callers; update dependency injection

---

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| IntelliJ IDEA | Semantic refactoring | Built-in refactoring menu |
| Spotless | Formatting | `./gradlew spotlessApply` |
| PMD | Code analysis | `pmd check -d src` |
| SpotBugs | Bug detection | `./gradlew spotbugsMain` |
| detekt (Kotlin) | Static analysis | `./gradlew detekt` |
| ktlint (Kotlin) | Formatting | `ktlint --format` |
| Error Prone | Compile-time checks | Gradle/Maven plugin |
