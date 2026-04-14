# JavaScript / TypeScript Refactoring Patterns

Patterns specific to JS/TS ecosystems including React, Node.js, Deno, and Bun.

## Table of Contents

1. [Modernization Patterns](#modernization-patterns)
2. [React-Specific Patterns](#react-specific)
3. [Node.js / Backend Patterns](#nodejs-patterns)
4. [TypeScript Strictness Patterns](#typescript-patterns)
5. [Codemods & Automation](#codemods)

---

## Modernization Patterns

### 1. var → const/let
**Risk: Low** | Always safe when done correctly
- Replace `var` with `const` (default) or `let` (if reassigned)
- Watch: `var` hoisting in loops with closures changes behavior with `let`
- Safety: Run tests; the closure behavior change in loops is the only risk

### 2. Callbacks → async/await
**Risk: Low**
```javascript
// Before
function fetchData(id, callback) {
  fetch(`/api/${id}`).then(r => r.json()).then(d => callback(null, d)).catch(callback);
}
// After
async function fetchData(id) {
  const res = await fetch(`/api/${id}`);
  return res.json();
}
```
- Safety: Ensure all error paths have try/catch; verify concurrent calls use Promise.all
- Anti-pattern: Don't await inside loops when calls are independent (use Promise.all)

### 3. .then() Chains → async/await
**Risk: Low**
- Flatten nested .then chains into sequential await statements
- Safety: Verify error handling is equivalent (catch at end → try/catch wrapping)

### 4. Object.assign → Spread
**Risk: Low**
```javascript
// Before: Object.assign({}, defaults, options)
// After: { ...defaults, ...options }
```
- Safety: Both are shallow copies; behavior is identical

### 5. for Loops → Array Methods
**Risk: Low**
```javascript
// Before: for loop building array → After: .map()
// Before: for loop filtering → After: .filter()
// Before: for loop accumulating → After: .reduce()
```
- Safety: Verify no `break`/`continue` (use .find/.some/.every instead)
- Anti-pattern: Don't chain 5+ array methods; readability suffers

### 6. require() → import
**Risk: Medium** (CJS→ESM migration)
- Replace `const x = require('x')` with `import x from 'x'`
- Replace `module.exports` with `export default` / `export`
- Must: Add `"type": "module"` to package.json
- Must: Replace `__dirname` with `import.meta.dirname` (Node 21+) or `fileURLToPath(import.meta.url)`
- Must: Replace `require.resolve()` with `import.meta.resolve()`
- Safety: Test EVERY import; some packages may not support ESM

### 7. String Concatenation → Template Literals
**Risk: Low**
```javascript
// Before: 'Hello ' + name + ', you are ' + age
// After: `Hello ${name}, you are ${age}`
```

---

## React-Specific

### 8. Class Components → Functional Components + Hooks
**Risk: Medium**
```jsx
// Lifecycle mapping:
// componentDidMount → useEffect(() => {}, [])
// componentDidUpdate → useEffect(() => {}, [deps])
// componentWillUnmount → useEffect(() => { return () => cleanup }, [])
// this.state → useState()
// this.refs → useRef()
```
- Safety: Test all lifecycle behaviors; verify cleanup functions
- Watch: `this` binding patterns disappear; ensure event handlers work
- Anti-pattern: Don't refactor class components that use getDerivedStateFromProps
  or getSnapshotBeforeUpdate without careful thought

### 9. Prop Drilling → Context / State Management
**Risk: Medium**
- When props pass through 3+ intermediate components that don't use them
- Options: React.createContext, Zustand, Jotai, Redux Toolkit
- Safety: Context changes re-render ALL consumers; may need React.memo
- Anti-pattern: Don't put frequently-changing values in Context (use Zustand instead)

### 10. Inline Styles → CSS Modules / Tailwind
**Risk: Low**
- Move inline style objects to CSS modules or Tailwind classes
- Safety: Verify responsive behavior; check dynamic styles still work

### 11. React.forwardRef → ref prop (React 19+)
**Risk: Low** (React 19+ only)
- In React 19, `ref` is a regular prop; forwardRef is no longer needed
- Safety: Only if project uses React 19+

---

## Node.js Patterns

### 12. Callback APIs → Promise APIs
**Risk: Low**
```javascript
// Before: fs.readFile(path, callback)
// After: const data = await fs.promises.readFile(path)
```
- Safety: All Node.js fs/crypto/etc have .promises variants

### 13. Express Middleware Cleanup
**Risk: Medium**
- Extract inline handlers to named functions
- Group related middleware into routers
- Safety: Verify middleware order is preserved (critical for auth, CORS)

### 14. Error Handling Standardization
**Risk: Low**
- Replace mix of try/catch styles with consistent error middleware
- Ensure async route handlers have error catching (express-async-errors or wrapper)

---

## TypeScript Patterns

### 15. `any` → Proper Types
**Risk: Medium**
```typescript
// Before: function process(data: any): any
// After: function process(data: UserInput): ProcessedResult
```
- Safety: Enable `noImplicitAny` in tsconfig after migration
- Strategy: Start with function boundaries (params + return types), then internals

### 16. Type Assertions → Type Guards
**Risk: Low**
```typescript
// Before: (user as Admin).permissions
// After: if (isAdmin(user)) { user.permissions }
function isAdmin(user: User): user is Admin { return user.role === 'admin'; }
```

### 17. Enums → Union Types (when appropriate)
**Risk: Low**
```typescript
// Before: enum Status { Active, Inactive }
// After: type Status = 'active' | 'inactive'
```
- When: String-based enums; no computed members
- Safety: Update all switch/case exhaustiveness

### 18. Interface Segregation
**Risk: Low**
- Split large interfaces into smaller, focused ones
- Use intersection types: `type FullUser = BaseUser & WithAddress & WithPayment`

---

## Codemods

For large-scale automated refactoring:

| Tool | Use Case |
|------|----------|
| jscodeshift | AST-based JS/TS transforms |
| ts-morph | TypeScript-specific refactoring |
| eslint --fix | Auto-fixable lint rules |
| @next/codemod | Next.js version migrations |
| react-codemod | React version migrations |

Run codemods on a clean git branch, review the diff, test everything.
