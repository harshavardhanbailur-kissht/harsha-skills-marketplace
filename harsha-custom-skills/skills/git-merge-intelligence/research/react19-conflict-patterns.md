# React 19 Merge Conflict Patterns: Comprehensive Research

## Overview

This document catalogs merge conflict patterns specific to React 19, highlighting breaking changes from React 18 that create merge conflicts, common conflict patterns in React codebases, type system gaps, testing considerations, and styling conflicts.

---

## 1. React 19 Breaking Changes That Create Merge Conflicts

### 1.1 New JSX Transform Changes

**What Changed:**
- React 19 requires the new JSX transform (introduced in React 17, now mandatory)
- Configuration changed from `"jsx": "react"` to `"jsx": "react-jsx"` in tsconfig
- Babel configuration: `@babel/preset-react` now requires `{ runtime: 'automatic' }`
- The JSX namespace moved - no longer globally available
- Optional: Remove unused `import React from 'react'` statements

**Merge Conflict Pattern:**
When both branches upgrade JSX configuration or one branch does and the other doesn't:
- **tsconfig.json conflicts**: Different "jsx" settings
- **Babel config conflicts**: Runtime configuration differences
- **Import statement conflicts**: One branch removes `import React`, the other uses it
- **Type errors**: JSX type mismatches if branches use different transforms
  ```typescript
  // React 18 style (old)
  import React from 'react'
  const MyComponent: React.FC<Props> = () => {}

  // React 19 style (new)
  const MyComponent: React.FC<Props> = () => {} // React import not needed
  ```

**Resolution Strategy:**
- Standardize on new transform across entire codebase
- Remove all unused `import React from 'react'` statements
- Update tsconfig and Babel configuration consistently
- Use codemods: `npx react-codemod@latest` to automate conversion

---

### 1.2 Server Components and Their Merge Implications

**What Changed:**
- Server Components are now stable in React 19 (were experimental)
- New `"use server"` and `"use client"` directives required
- Mixing Server and Client Components requires careful prop handling
- Data serialization rules differ between server and client boundaries
- New dependency conflicts with frameworks (Next.js, etc.)

**Merge Conflict Pattern:**
- **Directive conflicts**: Both branches add Server/Client components to same file
  ```javascript
  // Branch A
  'use client'
  export function Button({ onClick }) { ... }

  // Branch B
  'use server'
  async function handler() { ... }
  // CONFLICT: Both directives on same file (only one allowed)
  ```

- **Props and data serialization conflicts**:
  ```javascript
  // Branch A adds non-serializable prop
  <Button onClick={handleClick} data={new Date()} />

  // Branch B assumes all props are serializable for Server Components
  // CONFLICT: Date objects cannot cross server/client boundary
  ```

- **Peer dependency conflicts**:
  - React 19 introduces dependency conflicts with older libraries
  - Common: `@testing-library/react` expects `react@"^18.0.0"`
  - Solution: Use npm overrides or yarn resolutions

**Resolution Strategy:**
- Ensure only one directive per file
- Validate all props passed across server/client boundaries are serializable
- Use `npm dedupe` or package manager overrides for dependency conflicts
- Document which components are Server vs Client Components

---

### 1.3 React Compiler (React Forget) - Automatic Memoization

**What Changed:**
- React Compiler automatically inserts `useMemo`, `useCallback`, and `React.memo`
- Analyzes component source code for data flow dependencies
- Performs value dependency tracking to identify which props/state affect results
- Manual memoization becomes redundant (and can conflict with automatic optimization)

**Merge Conflict Pattern:**

- **Conflicting memoization strategies**:
  ```javascript
  // Branch A: Manual useCallback
  const handleClick = useCallback(() => {
    doSomething(value)
  }, [value])

  // Branch B: Relies on React Compiler auto-memoization
  const handleClick = () => {
    doSomething(value)
  }
  // CONFLICT: Different memoization approaches cause duplicate optimization
  ```

- **Dependency array conflicts with Compiler**:
  ```javascript
  // Branch A adds dependency
  useEffect(() => {
    effect()
  }, [a, b, c])

  // Branch B adds different dependency
  useEffect(() => {
    effect()
  }, [a, b, d])
  // CONFLICT: Compiler may optimize both differently, causing bugs
  ```

- **Unnecessary useMemo/useCallback after merge**:
  - React Compiler may already handle the optimization
  - Manual wrapping becomes redundant and obscures intent

**Resolution Strategy:**
- Choose either manual memoization OR React Compiler, not both
- Remove manual `useCallback`/`useMemo` wrapping for functions passed as props
- Let React Compiler handle optimization; remove explicit wrapping
- Use ESLint rule updates to enforce consistency
- Run `eslint --fix` with React Compiler rules enabled

---

### 1.4 The `use()` Hook - New Patterns and Conflicts

**What Changed:**
- New `use()` API for reading Promises and Context
- Can be called conditionally (inside if/for loops) - breaks Rules of Hooks for this pattern
- Integrates with Suspense and Error Boundaries
- Replaces some patterns of `useEffect` + `useState`

**Merge Conflict Pattern:**

- **Hook ordering conflicts**:
  ```javascript
  // Branch A: Old pattern with conditional hook
  if (condition) {
    const data = useData() // Rules of Hooks violation if truly conditional
  }

  // Branch B: New pattern using use()
  const data = use(promise) // Can be conditional!
  if (data) { ... }
  // CONFLICT: Different patterns for same logic, different Rules of Hooks implications
  ```

- **Promise handling conflicts**:
  ```javascript
  // Branch A: Promise created in component
  const promise = fetchData()

  // Branch B: Promise from Server Component (stable)
  // use(promiseFromServer)
  // CONFLICT: Different Promise stability guarantees
  ```

- **useContext vs use() conflicts**:
  ```javascript
  // Branch A: useContext at top level
  const theme = useContext(ThemeContext)

  // Branch B: use() called conditionally
  const theme = condition ? use(ThemeContext) : defaultTheme
  // CONFLICT: Different execution contexts and semantics
  ```

**Resolution Strategy:**
- Prefer `use()` for conditional Promise/Context access
- Keep `useContext` at top level for non-conditional access
- Create Promises in Server Components, not Client Components
- Run linter to detect mixed patterns
- Add comments explaining why `use()` was chosen over `useContext`

---

### 1.5 Actions and Form Handling Changes

**What Changed:**
- Forms now accept functions in `action` prop
- New hooks: `useActionState`, `useFormStatus`, `useOptimistic`
- Server Actions integrated with form submission
- Automatic form reset on successful action completion
- Form data automatically serialized

**Merge Conflict Pattern:**

- **Form action handler conflicts**:
  ```javascript
  // Branch A: Old pattern with onSubmit
  <form onSubmit={e => {
    e.preventDefault()
    handleSubmit(formData)
  }}>

  // Branch B: New Action pattern
  <form action={serverAction}>
  // CONFLICT: Different form submission patterns
  ```

- **Form state management conflicts**:
  ```javascript
  // Branch A: Traditional useState for form
  const [formData, setFormData] = useState({})
  const [isLoading, setIsLoading] = useState(false)

  // Branch B: useActionState
  const [state, formAction] = useActionState(serverAction, null)
  // CONFLICT: Different state management approaches
  ```

- **useFormStatus hook conflicts**:
  ```javascript
  // Branch A: Manual loading state
  {isLoading && <Spinner />}

  // Branch B: useFormStatus hook
  const { pending } = useFormStatus()
  {pending && <Spinner />}
  // CONFLICT: Different ways to track form status
  ```

**Resolution Strategy:**
- Migrate all forms to Action pattern with `action` prop
- Replace manual `useState` form state with `useActionState`
- Use `useFormStatus` instead of manual loading state tracking
- Prefer Server Actions for form submission
- Ensure form IDs match between branches when using `useFormStatus`

---

### 1.6 Ref Handling Changes and forwardRef Deprecation

**What Changed:**
- `forwardRef` is deprecated; refs now pass as regular props
- Ref cleanup functions now supported in ref callbacks
- Ref callbacks can return cleanup function: `ref={(el) => { cleanup(); return () => cleanup() }}`
- Simplified ref API for function components

**Merge Conflict Pattern:**

- **forwardRef vs new ref as prop**:
  ```javascript
  // Branch A: Old forwardRef pattern
  const Button = forwardRef(({ label }, ref) => (
    <button ref={ref}>{label}</button>
  ))

  // Branch B: New ref as prop pattern
  const Button = ({ ref, label }) => (
    <button ref={ref}>{label}</button>
  )
  // CONFLICT: Different component signatures
  ```

- **Ref callback return value conflicts**:
  ```javascript
  // Branch A: Implicit return of cleanup function
  ref={(el) => () => cleanup()}

  // Branch B: No return (old pattern)
  ref={(el) => { cleanup() }}
  // CONFLICT: TypeScript may reject implicit returns in React 19
  ```

- **TypeScript type signature conflicts**:
  ```javascript
  // Branch A: forwardRef with generics
  const Component = forwardRef<HTMLDivElement, Props>(...)

  // Branch B: ref as prop
  function Component({ ref }: { ref: React.RefObject<HTMLDivElement> } & Props) {}
  // CONFLICT: Type signatures don't match
  ```

**Resolution Strategy:**
- Use codemod: `npx react-codemod@latest react-19/remove-forward-ref`
- Convert all `forwardRef` to ref-as-prop pattern
- Remove implicit returns from ref callbacks
- Update TypeScript types to use ref as property
- Update call sites to pass ref as prop instead of using forwardRef

---

## 2. Conflict Patterns Specific to React Codebases

### 2.1 Component Prop Interface Changes

**Conflict Pattern:**
Both branches add different props to the same component, creating prop signature mismatches.

```javascript
// main branch
interface ButtonProps {
  label: string
  onClick: () => void
  className?: string // added here
}

// feature branch
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary' // added here instead
}

// After merge: conflicting prop additions
interface ButtonProps {
  label: string
  onClick: () => void
  className?: string
  variant?: 'primary' | 'secondary'
}
```

**Detection:**
- TypeScript will catch type mismatches at call sites
- But won't catch redundant or conflicting props
- Props that do the same thing (className vs variant) may both be added

**Resolution Strategy:**
- Identify props that serve the same purpose
- Choose one approach (e.g., prefer variant enums over className for styling)
- Update all usages to be consistent
- Consider creating prop merging utility for complex cases
- Document prop naming conventions

---

### 2.2 Hook Dependency Array Conflicts

**Conflict Pattern:**
Both branches modify useEffect/useMemo/useCallback dependency arrays differently.

```javascript
// Base version
useEffect(() => {
  loadData(id)
}, [id])

// Branch A adds data dependency
useEffect(() => {
  if (data) loadData(id)
}, [id, data]) // adds data

// Branch B adds enabled flag
useEffect(() => {
  if (enabled) loadData(id)
}, [id, enabled]) // adds enabled

// Merged result - both dependencies added
useEffect(() => {
  if (data && enabled) loadData(id)
}, [id, data, enabled]) // may cause infinite loops
```

**Problems:**
- Creates unnecessary re-runs if dependencies are objects/arrays
- May introduce stale closures
- Can cause infinite loops if dependency is created fresh each render
- ESLint exhaustive-deps rule may show warnings

**Detection:**
- Runtime: Excessive effect re-runs, infinite loops
- Linting: eslint-plugin-react-hooks warnings
- Testing: Tests that expect X renders but get Y

**Resolution Strategy:**
- Understand what each dependency represents semantically
- Use `useMemo` to stabilize object/array dependencies
- Verify that all added dependencies are necessary
- Check if effect should split into multiple useEffects
- Add comments explaining dependency logic
- Use ESLint to guide resolution: `"exhaustive-deps": "error"`

```javascript
// Better resolution
const stableId = useMemo(() => id, [id])
const stableData = useMemo(() => data, [data])

useEffect(() => {
  if (stableData?.enabled) {
    loadData(stableId)
  }
}, [stableId, stableData])
```

---

### 2.3 State Management Conflicts

**Conflict Pattern:**
Both branches modify useState or useReducer differently.

```javascript
// Initial state conflicts
// Branch A
const [formData, setFormData] = useState({
  name: '',
  email: '',
  phone: '' // added here
})

// Branch B
const [formData, setFormData] = useState({
  name: '',
  email: '',
  address: '' // added here instead
})

// Merged: inconsistent state shape
```

**Conflict Pattern 2: Action object conflicts**
```javascript
// Branch A: Reducer dispatch structure
dispatch({ type: 'SET_NAME', payload: name })

// Branch B: Different action structure
dispatch({ type: 'UPDATE_FIELD', field: 'name', value: name })

// Merged: handlers don't match dispatch calls
```

**Problems:**
- Undefined properties after merge
- Reducer handlers don't match action structures
- State initialization mismatches
- Type errors in TypeScript

**Resolution Strategy:**
- Merge state shapes carefully, ensuring all properties exist
- Verify reducer handles both old and new action types
- Consider creating state factory function
- Use Immer for immutable state updates
- Add type safety with TypeScript discriminated unions

```javascript
// Type-safe reducer
type FormAction =
  | { type: 'SET_NAME'; payload: string }
  | { type: 'SET_EMAIL'; payload: string }
  | { type: 'SET_PHONE'; payload: string }
  | { type: 'SET_ADDRESS'; payload: string }

function formReducer(state: FormData, action: FormAction) {
  switch (action.type) {
    case 'SET_NAME': return { ...state, name: action.payload }
    case 'SET_EMAIL': return { ...state, email: action.payload }
    case 'SET_PHONE': return { ...state, phone: action.payload }
    case 'SET_ADDRESS': return { ...state, address: action.payload }
    default: return state
  }
}
```

---

### 2.4 Context Provider Hierarchy Changes

**Conflict Pattern:**
Both branches change how context providers are nested or structured.

```javascript
// Base: Simple provider
<AppProvider>
  <App />
</AppProvider>

// Branch A: Added new provider
<AppProvider>
  <ThemeProvider>
    <App />
  </ThemeProvider>
</AppProvider>

// Branch B: Reorganized provider order
<ThemeProvider>
  <AppProvider>
    <App />
  </AppProvider>
</ThemeProvider>

// Merged: Conflicting provider hierarchy
```

**Problems:**
- Providers depend on execution order
- Some providers may need context from other providers
- App component receives different context values
- Type mismatches in Provider.Provider type

**Detection:**
- Runtime: Missing or undefined context values
- Components in wrong provider scope can't access context
- useContext calls return undefined

**Resolution Strategy:**
- Document provider dependencies (which providers need which)
- Test all context access paths after merge
- Establish consistent provider ordering convention
- Consider using custom hooks to encapsulate provider setup
- Create provider composition tests

```javascript
// Provider composition pattern
export function RootProviders({ children }) {
  return (
    <AppProvider>
      <ThemeProvider>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </ThemeProvider>
    </AppProvider>
  )
}
```

---

### 2.5 Event Handler Conflicts

**Conflict Pattern:**
Both branches modify the same event handler or add different handlers for same event.

```javascript
// Base button
<button onClick={handleClick}>Click me</button>

// Branch A: Enhanced click handler
const handleClick = async () => {
  await logEvent('button_clicked')
  navigate('/next')
}

// Branch B: Different click handler
const handleClick = () => {
  setCount(count + 1)
  onClickProp?.()
}

// Merged: Second branch's implementation wins, losing analytics
```

**Conflict Pattern 2: Event delegation**
```javascript
// Branch A: Multiple handlers on container
<div onClick={handleContainerClick} onKeyDown={handleKeyDown}>
  <Button />
</div>

// Branch B: Handlers on child instead
<div>
  <Button onClick={handleButtonClick} onKeyDown={handleKeyDown} />
</div>

// Merged: Both sets of handlers, unclear which fires
```

**Problems:**
- Lost functionality (analytics, side effects)
- Duplicate handler execution
- Event bubbling issues
- Type mismatches in handler signatures

**Resolution Strategy:**
- Understand what each branch's handler does
- Combine functionalities if both are necessary
- Use event composition patterns
- Extract handler logic into hooks
- Document event flow

```javascript
// Combined handler
const handleClick = async () => {
  // From Branch A: Analytics
  await logEvent('button_clicked')

  // From Branch B: State update
  setCount(count + 1)

  // From both: Prop callback
  onClickProp?.()

  // From Branch A: Navigation
  navigate('/next')
}
```

---

## 3. What TypeScript Won't Catch in React Conflicts

### 3.1 Rules of Hooks Violations Introduced by Merge

**The Problem:**
TypeScript doesn't validate hook calling rules - only ESLint can catch these.

```javascript
// Merge introduces hook violation
function Component({ showExtra }) {
  if (showExtra) {
    const [data] = useState(null) // VIOLATION: Conditional hook
  }
  const [value] = useState(0) // This hook changes position based on condition
  return null
}
```

**Why TypeScript Misses It:**
- Valid TypeScript syntax
- Compiles without errors
- Runtime error: "Rendered more hooks than during the previous render"

**Detection:**
- ESLint rule: `eslint-plugin-react-hooks`
- Runtime: Warning in development, broken behavior in production
- Not caught by type checking

**Resolution Strategy:**
- Always run ESLint with react-hooks plugin
- Configure: `"rules": { "react-hooks/rules-of-hooks": "error" }`
- Extract conditional logic outside of hooks
- Use `use()` API for truly conditional needs in React 19

---

### 3.2 Missing Key Props in Lists After Merge

**The Problem:**
```javascript
// Branch A: Added new items to map
{items.map(item => <Item item={item} />)} // No key!

// Branch B: Added children to same list
{items.map((item, index) => (
  <Item key={index} item={item}> {/* index as key is bad but valid */}
    {children}
  </Item>
))}

// Merged: No keys or wrong keys on list items
```

**Why TypeScript Misses It:**
- Key is valid optional prop
- No type error for missing keys
- No type error for using array index as key

**Problems:**
- Component state doesn't persist correctly when list reorders
- Performance issues with large lists
- Incorrect animations or transitions

**Detection:**
- ESLint rule: `react/jsx-key`
- React DevTools: Yellow warning about missing keys
- Manual testing: Reorder list, state gets confused

**Resolution Strategy:**
- Always use unique, stable IDs as keys
- Never use array index as key
- Run linter: `"react/jsx-key": "error"`
- Test list reordering behavior

```javascript
// Correct pattern
{items.map(item => (
  <Item key={item.id} item={item}>
    {children}
  </Item>
))}
```

---

### 3.3 Incorrect Prop Drilling After Component Restructuring

**The Problem:**
```javascript
// Branch A: Moved component to different level
function Parent() {
  const theme = useContext(ThemeContext)
  return <Child theme={theme} /> // passes theme prop
}

// Branch B: Added intermediate component
function Parent() {
  const theme = useContext(ThemeContext)
  return <Wrapper /> // doesn't pass theme prop
}

function Wrapper() {
  return <Child /> // expects theme prop but doesn't get it!
}

// After merge: Child doesn't receive expected props
```

**Why TypeScript Might Miss It:**
- Component signatures may have optional props
- No type error if Child's theme prop is optional
- Only fails at runtime

**Detection:**
- Runtime: Component renders with undefined values
- TypeScript: Only if props are strictly typed as required
- Manual testing: Props appear undefined

**Resolution Strategy:**
- Verify all props propagate through component tree
- Use required props in TypeScript when possible
- Create provider for deeply nested props instead
- Test component at all nesting levels
- Use prop-types or TypeScript generics for type safety

```javascript
// Better: Use context instead of prop drilling
function Parent() {
  const theme = useContext(ThemeContext)
  return <ThemeProvider value={theme}><Wrapper /></ThemeProvider>
}
```

---

### 3.4 Stale Closure Issues from Merged Dependency Arrays

**The Problem:**
```javascript
// Branch A: Added effect with captured value
useEffect(() => {
  const timer = setInterval(() => {
    console.log(count) // captures current count
  }, 1000)
  return () => clearInterval(timer)
}, []) // No dependency on count!

// Branch B: Expected count to update
// ... but it won't because effect has stale closure

// Merged result: count value always stale in callback
```

**Why TypeScript Misses It:**
- Valid TypeScript syntax
- No type error for missing dependency
- ESLint can catch this IF configured

**Problems:**
- Callback uses old value of variables
- State updates don't reflect in captured values
- Timers/intervals use stale data
- Hard to debug at runtime

**Detection:**
- ESLint exhaustive-deps rule (if enabled)
- Runtime: Wrong values in callbacks
- Manual testing: Values don't update when expected

**Resolution Strategy:**
- Always enable ESLint exhaustive-deps
- Review merged dependency arrays carefully
- Understand what each dependency represents
- Use ref for values that shouldn't trigger effect
- Test behavior by manually changing dependencies

```javascript
// Correct: Include count in dependencies
useEffect(() => {
  const timer = setInterval(() => {
    console.log(count) // always current value
  }, 1000)
  return () => clearInterval(timer)
}, [count]) // Include dependency
```

---

### 3.5 Concurrent Mode Gotchas in State Updates

**The Problem:**
React 19 makes concurrent rendering default. Code that worked in React 18 may break:

```javascript
// Code that worked in React 18
function Component() {
  const [count, setCount] = useState(0)

  const handleClick = () => {
    setCount(count + 1)
    setCount(count + 1) // In React 18: both execute, count becomes 1
    // In React 19: batched, still becomes 1 (same state snapshot)
  }
}

// Merge adds state update that assumes React 18 behavior
function suspendingComponent() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData().then(setData).catch(setError)
    // In React 19: might suspend before all updates apply
  }, [])
}
```

**Why TypeScript Misses It:**
- Syntax is valid
- No type errors in code
- Behavior difference only at runtime

**Problems:**
- Multiple state updates batch differently
- Suspense behavior changes
- Race conditions in error handling
- UI partially updates when user expects full update

**Detection:**
- React DevTools: Warning about batching
- Manual testing: State updates don't accumulate
- Suspense components show wrong fallback timing
- Race conditions in error boundaries

**Resolution Strategy:**
- Review state update patterns for React 19 batching
- Use `useTransition` for non-urgent updates
- Understand Suspense integration points
- Test with Suspense-using components
- Verify error boundaries catch correct errors

```javascript
// React 19 aware pattern
function Component() {
  const [count, setCount] = useState(0)
  const [, startTransition] = useTransition()

  const handleClick = () => {
    startTransition(() => {
      setCount(c => c + 1) // Use updater function
      setCount(c => c + 1) // Both will apply sequentially
    })
  }
}
```

---

## 4. Testing Considerations for React 19 Conflicts

### 4.1 React Testing Library Pattern Changes

**Breaking Changes:**

1. **Suspense handling in tests**
   ```javascript
   // React 18: Suspended components render children after await
   // React 19: Suspended components keep showing fallback
   // Tests must await differently

   // React 18 style (may not work in 19)
   await render(<Component />)
   expect(screen.getByText('Data')).toBeInTheDocument()

   // React 19 style
   await waitFor(() => {
     expect(screen.getByText('Data')).toBeInTheDocument()
   })
   ```

2. **act() import moved**
   ```javascript
   // Old (React 18)
   import { act } from 'react-dom/test-utils'

   // New (React 19)
   import { act } from 'react'
   ```

3. **render options type updates**
   - `onCaughtError` type inference changed
   - `onUncaughtError` handling changed
   - Error boundary testing patterns changed

**Merge Conflict Pattern:**
```javascript
// Branch A: Old RTL imports
import { render } from '@testing-library/react'
import { act } from 'react-dom/test-utils'

// Branch B: New RTL patterns
import { render } from '@testing-library/react'
import { act } from 'react'
import { waitFor } from '@testing-library/react'

// Merged: Duplicate imports, mixed patterns
```

**Resolution Strategy:**
- Update all `act` imports from `react-dom/test-utils` to `react`
- Use `waitFor` wrapper for async assertions in Suspense tests
- Verify `@testing-library/react` is compatible with React 19
- Test Suspense behavior explicitly
- Update render options for new error handling

---

### 4.2 Snapshot Test Conflicts and Regeneration

**The Problem:**
```javascript
// Merge changes component output format
// Branch A: formatDate function added
// Branch B: component structure changed

// Both branches update the same snapshot
// After merge: Which snapshot is correct?
```

**When to Regenerate vs Resolve:**
- **Regenerate snapshots** if:
  - Breaking changes are intentional (component redesign)
  - Format changes are expected (date display update)
  - Both branches made valid changes to snapshot
  - Visual diff looks correct

- **Resolve conflict** if:
  - One branch shouldn't have changed snapshot
  - Changes are incompatible
  - Need to keep specific branch's snapshot

**Testing Strategy:**
```javascript
// Add accompanying unit test that validates snapshot
describe('Component snapshot', () => {
  it('renders correctly with new date format', () => {
    const { container } = render(<Component date={new Date('2025-01-01')} />)
    expect(container).toMatchSnapshot()

    // Also verify specific output
    expect(screen.getByText('2025-01-01')).toBeInTheDocument()
  })
})
```

**Resolution Strategy:**
- Review snapshot diff in merge conflict
- Decide if change is intentional
- If both branches changed: manually create correct snapshot
- Always include assertions beyond snapshots
- Run tests to verify snapshot matches behavior

---

### 4.3 Component Tests vs Integration Tests

**Conflict Pattern:**
Merge affects different levels of test hierarchy differently.

```javascript
// Component test (isolated)
describe('Button', () => {
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick} />)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalled()
  })
})

// Integration test (full app)
describe('Form submission', () => {
  it('submits form and shows success', async () => {
    render(<App />)
    fillForm(...)
    clickSubmit()
    await expect(screen.findByText('Success')).resolves.toBeInTheDocument()
  })
})

// Merge: Component test passes but integration test fails
// because form action changed between branches
```

**Resolution Strategy:**
- Test component in isolation with mocked props
- Test integration with real providers and dependencies
- Both must pass after merge
- Update mocks to match new prop interfaces
- Verify Server Actions work in integration tests

---

## 5. CSS-in-JS and Tailwind Class Conflicts in React Components

### 5.1 Tailwind CSS Class Conflicts

**The Problem:**
```javascript
// Branch A: Added dark mode class
<div className="text-black dark:text-white">

// Branch B: Added size variant class
<div className="text-sm md:text-base">

// Merged: Multiple conflicting Tailwind classes
<div className="text-black dark:text-white text-sm md:text-base">

// Issue: Classes for same property (text color, size) conflict
// CSS cascade determines which wins - may not be what's intended
```

**Why This Happens:**
- Tailwind class order doesn't matter in CSS
- Last class in CSS file wins, not last in className string
- Multiple utility classes can target same property
- Hard to debug: no TypeScript errors

**Solution: tailwind-merge**

The `tailwind-merge` library intelligently resolves conflicting Tailwind classes:

```javascript
import { twMerge } from 'tailwind-merge'
import clsx from 'clsx'

function cn(...inputs) {
  return twMerge(clsx(inputs))
}

// Usage
const merged = cn(
  'text-black dark:text-white', // Base
  'text-sm md:text-base',        // Size override
  data.variant === 'large' && 'md:text-lg' // Conditional
)
// Result: tailwind-merge ensures proper class precedence
```

**Merge Conflict Resolution:**
```javascript
// Branch A
className={cn(
  'px-4 py-2',
  'bg-blue-500 hover:bg-blue-600' // added
)}

// Branch B
className={cn(
  'px-4 py-2',
  'bg-gray-100 hover:bg-gray-200' // added differently
)}

// Merged: Use cn() utility with both, let tailwind-merge resolve
className={cn(
  'px-4 py-2',
  variant === 'primary' && 'bg-blue-500 hover:bg-blue-600',
  variant === 'secondary' && 'bg-gray-100 hover:bg-gray-200'
)}
```

**Detection:**
- Visual testing: Colors/sizing don't match design
- Browser DevTools: Check which classes actually apply
- Linter: Create custom rule to validate class merging

**Resolution Strategy:**
- Install `tailwind-merge` and `clsx`: `npm install tailwind-merge clsx`
- Create `cn()` utility function
- Replace all className assignments with `cn(...)`
- Test responsive breakpoints
- Verify hover/focus/dark mode states
- Document variant system

---

### 5.2 CSS-in-JS Library Conflicts

**Common Patterns:**
```javascript
// Branch A: Uses styled-components
import styled from 'styled-components'

const Button = styled.button`
  background: blue;
  padding: 8px 16px;
`

// Branch B: Uses Emotion
import { css } from '@emotion/react'

const buttonStyles = css`
  background: blue;
  padding: 8px 16px;
`

// Merged: Two different CSS-in-JS libraries for same component
```

**Problems:**
- Inconsistent styling approach
- Larger bundle size
- Runtime CSS conflicts
- Maintenance burden

**Resolution Strategy:**
- Choose single CSS-in-JS solution for codebase
- Migrate all components to same library
- Use codemods if available for conversion
- Keep styled-components OR Emotion, not both
- Document styling conventions

---

### 5.3 Style Prop and Tailwind Conflicts

**The Problem:**
```javascript
// Branch A: Inline styles
<div style={{ color: 'black', fontSize: '16px' }}>

// Branch B: Tailwind classes
<div className="text-black text-base">

// Merged: Both style and className
<div
  style={{ color: 'black', fontSize: '16px' }}
  className="text-black text-base"
>
// Inline styles win over Tailwind (specificity), causing confusion
```

**Resolution Strategy:**
- Choose either inline styles OR Tailwind, not both
- Prefer Tailwind for consistency
- Use Tailwind `invert-colors` and other utilities instead of inline styles
- If inline styles needed, document why
- Create custom component wrapper that handles styling consistently

---

## 6. Merge Conflict Resolution Checklist for React 19

After resolving merge conflicts, verify:

### TypeScript & Compilation
- [ ] `tsc --noEmit` passes without errors
- [ ] All imports resolve (removed unused React imports)
- [ ] forwardRef usage updated or removed
- [ ] JSX type errors resolved
- [ ] ref types match new pattern

### Linting
- [ ] `eslint --fix` passes
- [ ] No React Hooks violations
- [ ] No missing keys in lists
- [ ] Dependency arrays reviewed
- [ ] No "exhaustive-deps" warnings

### Functionality
- [ ] All forms updated to Action pattern or verified
- [ ] Server/Client component directives correct
- [ ] Props pass correctly through component tree
- [ ] Event handlers have all necessary functionality
- [ ] State shapes match across branches

### Testing
- [ ] Component tests pass with new props
- [ ] Integration tests verify behavior
- [ ] Snapshot tests reviewed and updated
- [ ] Suspense behavior tested
- [ ] Error boundaries catch errors

### Styling
- [ ] Tailwind classes merged with `cn()` utility
- [ ] No inline style + Tailwind class conflicts
- [ ] Responsive breakpoints work
- [ ] Dark mode/theme variants work
- [ ] CSS-in-JS pattern consistent

### Performance
- [ ] No unnecessary re-renders
- [ ] Memoization strategy consistent
- [ ] Dependency arrays optimized
- [ ] Large lists have proper keys
- [ ] Server Actions don't block UI unnecessarily

---

## 7. Tools and Resources

### Codemods
- `react-codemod`: Official React migration tool
  - `npx react-codemod@latest react-19/...`
  - Available: `remove-forward-ref`, `replace-use-legacy-api`, etc.

### Configuration
- **tsconfig.json**: Update "jsx" to "react-jsx"
- **eslint config**: Enable `eslint-plugin-react-hooks`
- **babel config**: Update @babel/preset-react runtime

### Utilities
- **tailwind-merge**: Merge Tailwind classes intelligently
- **clsx**: Conditional class name utilities
- **React Testing Library**: Updated for React 19

### Documentation
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 19 Blog Post](https://react.dev/blog/2024/12/05/react-19)
- [Server Components](https://react.dev/reference/rsc/server-components)
- [React Compiler](https://react.dev/learn/react-compiler)

---

## 8. Prevention Strategies

### Code Organization
- Keep Server and Client components separate
- Document component communication boundaries
- Use consistent naming conventions
- Establish prop interface standards

### Tooling Setup
- Enable all linting rules before merge
- Configure TypeScript strict mode
- Set up pre-commit hooks
- Run tests before pull requests

### Team Practices
- Review merge impact on tests
- Document breaking changes
- Use feature branches with clear scope
- Communicate major refactors early
- Consider merge strategy for long-lived branches

### Testing Strategy
- Write integration tests spanning components
- Test context provider hierarchy
- Verify form Actions work end-to-end
- Test Suspense boundaries
- Snapshot tests with semantic assertions

---

## Conclusion

React 19 introduces significant changes that create new merge conflict patterns compared to React 18. The most critical areas are:

1. **JSX Transform** - Configuration and imports must be consistent
2. **Server Components** - Careful prop serialization and directive usage
3. **Ref API** - Complete migration from forwardRef to ref-as-prop
4. **Form Actions** - New patterns replace traditional form handling
5. **Hooks** - Dependency arrays and hook ordering require careful review
6. **TypeScript** - Many issues aren't caught by types alone; linting is essential
7. **Testing** - RTL patterns and Suspense handling changed

The key to avoiding conflicts is:
- Establish team conventions early
- Use linting and type safety aggressively
- Test both component and integration levels
- Review both semantic and syntactic changes
- Document breaking changes clearly

References:
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [React 19 Release](https://react.dev/blog/2024/12/05/react-19)
- [React Compiler Documentation](https://react.dev/learn/react-compiler)
- [Server Components](https://react.dev/reference/rsc/server-components)
- [use() Hook](https://react.dev/reference/react/use)
- [forwardRef Deprecation](https://react.dev/reference/react/forwardRef)
