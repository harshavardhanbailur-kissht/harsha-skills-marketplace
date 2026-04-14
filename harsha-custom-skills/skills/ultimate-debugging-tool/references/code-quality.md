# Code Quality During Debugging

Improve code quality while debugging—leave the codebase better than you found it without introducing new bugs. Apply these patterns to code you've already touched during debugging work.

## The Boy Scout Rule for Debugging

**"Leave the code better than you found it"** through small, incremental improvements applied alongside (not mixed with) bug fixes.

**Core principles:**
- Commit bug fixes and quality improvements in **separate commits**
- Only improve code you already touched during debugging (avoid scope creep)
- If improvement risk exceeds low, defer to a separate pull request
- Keep improvements focused and reviewable in isolation

Example workflow:
```
Commit 1: Fix: Resolve null reference error in validateUser()
Commit 2: Refactor: Extract validation logic from validateUser()
```

This separation makes it easy to revert improvements independently if needed while keeping the bug fix intact.

## Code Smell Detection

Identify opportunities for improvement while debugging by recognizing these patterns:

### Complexity Smells

**Function length:** Functions >50 lines are difficult to reason about
```javascript
// BEFORE: 60-line function mixing concerns
function processOrder(order) {
  // 20 lines of validation
  // 20 lines of calculation
  // 20 lines of logging
  // ...
}

// AFTER: Extract helper functions
function processOrder(order) {
  validateOrder(order);
  const total = calculateOrderTotal(order);
  logOrderProcessing(order, total);
}
```

**Deep nesting:** Nesting >3 levels reduces readability—use guard clauses
```javascript
// BEFORE: Difficult to follow intent
function process(data) {
  if (data) {
    if (data.items) {
      if (data.items.length > 0) {
        // actual business logic
      }
    }
  }
}

// AFTER: Exit early, logic is clear
function process(data) {
  if (!data?.items?.length) return;
  // actual business logic
}
```

**Cyclomatic complexity:** >10 branches indicates function should be split
- Each branch path = one unit of complexity
- Use strategy pattern or polymorphism to reduce branching

**Parameter count:** >4 parameters suggests grouping related data
```javascript
// BEFORE: Many parameters
function createUser(firstName, lastName, email, phone, address) {}

// AFTER: Use object for related data
function createUser(userInfo) {
  // userInfo = { firstName, lastName, email, phone, address }
}
```

**Boolean parameters:** Split into two functions to clarify behavior
```javascript
// BEFORE: Unclear what true/false means
function formatData(data, compress)

// AFTER: Intention is obvious
function formatDataCompressed(data)
function formatDataUncompressed(data)
```

### Naming Smells

**Single-letter variables:** Acceptable only for loop counters (i, j, k)
```javascript
// BAD
const d = new Date();
const a = calculateAmount(price, tax);

// GOOD
const currentDate = new Date();
const totalAmount = calculateAmount(price, tax);
```

**Generic names:** Avoid data, info, handler, manager, utils—be specific
```javascript
// BAD
const userHandler = (user) => { ... }
const validateData = (input) => { ... }

// GOOD
const authenticateUser = (user) => { ... }
const validateEmailAddress = (input) => { ... }
```

**Misleading names:** Names must accurately describe what code does
```javascript
// BAD: Name doesn't match behavior
function isReady() {
  return userHasPermission && dataIsLoaded && !isError;
}

// GOOD: Name matches what's actually checked
function canRenderUserDashboard() {
  return userHasPermission && dataIsLoaded && !isError;
}
```

**Inconsistent naming:** Pick a style and apply it uniformly
```javascript
// BAD: Mixed conventions
const user_name = "Alice";
const userEmail = "alice@example.com";

// GOOD: Consistent camelCase
const userName = "Alice";
const userEmail = "alice@example.com";
```

### Duplication Smells

**Copy-pasted blocks:** Extract to shared function
```javascript
// BEFORE: Validation logic duplicated in 3 places
function createUser(data) {
  if (!data.email) throw new Error("Email required");
  // ...
}

function updateUser(data) {
  if (!data.email) throw new Error("Email required");
  // ...
}

// AFTER: Shared validation
function validateUserEmail(data) {
  if (!data.email) throw new Error("Email required");
}
```

**Similar switch/if chains:** Use lookup table or strategy pattern
```javascript
// BEFORE: Repeated branching logic
const status1 = role === 'admin' ? 'FULL_ACCESS' : 'LIMITED';
const status2 = role === 'admin' ? 'FULL_ACCESS' : 'LIMITED';

// AFTER: Lookup table
const rolePermissions = { admin: 'FULL_ACCESS', user: 'LIMITED' };
const status = rolePermissions[role];
```

**Repeated null checks:** Use null object pattern or optional chaining
```javascript
// BEFORE: Multiple null checks scattered
if (user && user.profile && user.profile.avatar) { ... }
if (user && user.profile && user.profile.bio) { ... }

// AFTER: Optional chaining
user?.profile?.avatar
user?.profile?.bio
```

### Dead Code Smells

**Unused imports:** Remove them immediately—they increase cognitive load
```javascript
// Remove: import { unusedFunction } from './utils';
import { usedFunction } from './utils';
```

**Commented-out code:** Delete it—git preserves history, comments don't
```javascript
// Remove these lines entirely:
// const legacyValue = calculateOldWay();
// console.log(debugInfo);
```

**Unreachable branches:** Remove—they confuse future readers
```javascript
// BEFORE: Dead code after return
function getValue() {
  return result;
  console.log("unreachable"); // DELETE THIS
}

// AFTER: Clean
function getValue() {
  return result;
}
```

**Unused parameters:** Remove or prefix with underscore if required by interface
```javascript
// BEFORE: Parameter never used
function handleClick(event, unused) {
  console.log(event.target);
}

// AFTER: Mark intentionally unused
function handleClick(event, _unused) {
  console.log(event.target);
}
```

### Type Safety Smells (TypeScript)

**`any` type:** Replace with proper type or `unknown`
```typescript
// BAD: any disables type checking
function process(data: any) { }

// GOOD: Explicit type or unknown for validation
function process(data: ProcessInput) { }
function parseUnknown(data: unknown): ProcessInput { ... }
```

**Type assertion (`as`):** Replace with type guard
```typescript
// BAD: Assertion bypasses safety
const user = data as User;

// GOOD: Guard ensures safety
function isUser(data: unknown): data is User {
  return data && typeof data === 'object' && 'id' in data;
}
```

**`@ts-ignore`:** Fix the type error instead of ignoring it
```typescript
// BAD: Hiding type problems
// @ts-ignore
const result = problematicFunction();

// GOOD: Properly typed
const result: ExpectedType = fixFunction();
```

**Missing return types:** Add explicit return types to exported functions
```typescript
// BAD: Type inferred (may change unexpectedly)
export function getUserAge(user) {
  return user.birthDate ? calculateAge(user.birthDate) : null;
}

// GOOD: Explicit return type
export function getUserAge(user: User): number | null {
  return user.birthDate ? calculateAge(user.birthDate) : null;
}
```

## Code Quality Metrics

Track these metrics to measure improvement:

| Metric | Target | Action |
|--------|--------|--------|
| Cognitive complexity | <15 per function | Extract helper functions if exceeded |
| Function length | <50 lines | Split into smaller functions |
| File length | <300 lines | Reorganize into multiple files |
| Import count | <15 imports | File may be doing too much |
| `any` type count | 0 (or decreasing) | Replace with proper types |
| Test coverage | >80% critical paths | Add tests for debugged code |
| TODO comments | Bounded, tracked | Don't let accumulate indefinitely |

## Documentation Improvements During Debugging

**Add JSDoc when you've spent time understanding code:**
```javascript
/**
 * Validates email format and checks against known disposable domains.
 * @param {string} email - Email address to validate
 * @returns {boolean} True if email is valid and not from disposable domain
 * @throws {TypeError} If email is not a string
 */
function validateEmail(email) { }
```

**Add inline comments explaining WHY, not WHAT:**
```javascript
// BAD: Comment restates what code does
const price = quantity * unitPrice; // Multiply quantity by unit price

// GOOD: Comment explains intent
// Use gross price before tax to match API contract with legacy billing system
const price = quantity * unitPrice;
```

**Update misleading names during debugging:**
- If you discovered a function name doesn't match behavior, fix it
- If you clarified a variable's purpose, rename it appropriately
- If you added logic that changed a function's behavior, update its documentation

**Document error paths:**
```javascript
/**
 * @throws {ValidationError} If input fails schema validation
 * @throws {NetworkError} If API call fails
 */
function processData(input) { }
```

## When NOT to Improve

Respect these constraints before applying improvements:

**File scheduled for major refactoring:** Don't apply small improvements—wait for the refactoring
**Change affects >5 files:** Create a separate pull request for cross-file changes
**Requires new dependency:** Separate PR for dependency changes
**You're not confident:** Don't refactor if unsure of correctness—defer to code review or ask
**Under deadline pressure:** Fix the bug first, note improvements for later

## Summary Checklist

When debugging, before committing quality improvements:

- [ ] Bug fix is complete and tested separately
- [ ] Improvement is in a separate commit
- [ ] Improvement only touches code I debugged
- [ ] Risk assessment: improvement is low-risk
- [ ] Refactoring doesn't introduce new behavior
- [ ] Code is more readable/maintainable than before
- [ ] Tests still pass
- [ ] No new complexity introduced to solve the problem
