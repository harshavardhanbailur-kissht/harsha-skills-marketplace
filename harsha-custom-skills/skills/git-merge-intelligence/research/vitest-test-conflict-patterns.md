# Vitest and Testing Library Conflict Patterns: Comprehensive Research Guide

**Date:** April 7, 2026
**Focus:** Post-merge test conflict resolution for Vitest + Testing Library projects

---

## Table of Contents

1. [Vitest Configuration Conflicts](#vitest-configuration-conflicts)
2. [Test File Conflict Patterns](#test-file-conflict-patterns)
3. [Testing Library Conflicts](#testing-library-conflicts)
4. [Distinguishing Test Failures: Wrong Resolution vs. Test Updates](#distinguishing-test-failures)
5. [Mock and Fixture Conflicts](#mock-and-fixture-conflicts)
6. [CI Integration and Test Execution](#ci-integration-and-test-execution)
7. [Decision Frameworks](#decision-frameworks)

---

## 1. Vitest Configuration Conflicts

### 1.1 vitest.config.ts vs vite.config.ts Test Configuration

**Problem:** When both `vitest.config.ts` and `vite.config.ts` exist, they can conflict over test configuration precedence.

**Key Behaviors:**
- `vitest.config.ts` has **higher priority** and will override settings in `vite.config.ts`
- If `vitest.config.ts` exists, it completely takes precedence—settings in `vite.config.ts` are not merged automatically
- This creates merge conflicts when different branches have different test configuration strategies

**Conflict Patterns:**
- Branch A configures tests in `vite.config.ts` (with `test` property)
- Branch B creates separate `vitest.config.ts` file
- After merge: Vitest uses `vitest.config.ts` and ignores `vite.config.ts` changes from Branch A

**Best Practice Resolution:**
```typescript
// Recommended: Use mergeConfig for clarity and avoiding duplication
// vitest.config.ts
import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      // Vitest-specific options only
      environment: 'jsdom',
      globals: true,
    }
  })
)
```

**Alternative Pattern (Environment-Based):**
```typescript
// vite.config.ts - single file approach
import { defineConfig } from 'vite'

export default defineConfig(({ command, mode }) => {
  // Apply test config only when Vitest runs
  const testConfig = mode === 'test' ? {
    test: {
      environment: 'jsdom',
      globals: true,
    }
  } : {}

  return {
    ...testConfig,
    // Regular Vite config
  }
})
```

**Resolution Strategy After Merge:**
1. Choose **one** location for test config (prefer separate `vitest.config.ts`)
2. If using `mergeConfig`, ensure Vite config exports from `vite.config.ts`
3. Delete redundant test config from the other file
4. Run `vitest run` to verify configuration is applied

---

### 1.2 Test Environment Conflicts (jsdom, happy-dom, node)

**Problem:** Different branches specify different test environments, causing DOM/global availability conflicts.

**Environment Options:**

| Environment | Use Case | Global Availability | Performance |
|------------|----------|-------------------|-------------|
| **node** | Non-DOM testing, API testing, utilities | No browser globals | Fast |
| **jsdom** | React/Vue components, full DOM compliance | Complete browser API | Slower, comprehensive |
| **happy-dom** | React/Vue components, speed-critical | Complete browser API (+ Fetch) | Very fast |
| **edge-runtime** | Edge deployment testing | Minimal browser globals | Fast |

**Common Merge Conflicts:**

**Scenario A: Environment Type Change**
```typescript
// Branch A
export default defineConfig({
  test: {
    environment: 'jsdom'  // Full DOM compliance needed
  }
})

// Branch B
export default defineConfig({
  test: {
    environment: 'happy-dom'  // Faster, lightweight
  }
})
```

**Resolution Decision:**
- If tests use **accessibility queries** (`getByRole`): Use `jsdom` (more standards-compliant)
- If tests are **performance-critical**: Use `happy-dom`
- If **no DOM needed**: Use `node`
- Check test requirements before merging

**Scenario B: Per-File Environment Override**
```typescript
// Branch A: Global default
// vitest.config.ts
export default defineConfig({
  test: { environment: 'jsdom' }
})

// Branch B: Per-test override
// tests/component.test.ts
// @vitest-environment happy-dom
describe('Fast DOM tests', () => { ... })
```

**After Merge:** Both are valid—per-file overrides take precedence. Verify test behavior hasn't changed.

**Setting Environment-Specific Options:**
```typescript
export default defineConfig({
  test: {
    environment: 'jsdom',
    environmentOptions: {
      jsdom: {
        resources: 'usable',  // Allow script execution
        pretendToBeVisual: true,
      }
    }
  }
})
```

---

### 1.3 Setup File Conflicts (vitest.setup.ts)

**Problem:** Multiple branches add/modify global mocks, fixtures, or custom matchers in setup files.

**Typical Conflict Scenarios:**

**Scenario 1: Global Mock Setup**
```typescript
// Branch A's vitest.setup.ts
global.fetch = vi.fn(() => Promise.resolve(...))

// Branch B's vitest.setup.ts
global.fetch = vi.fn().mockResolvedValue(...)

// After merge: Both try to assign global.fetch
```

**Scenario 2: Custom Matchers**
```typescript
// Branch A
expect.extend({ toBeWithinRange() { ... } })

// Branch B
expect.extend({ toBeValidEmail() { ... } })

// After merge: Both matchers should exist, but file structure creates conflict
```

**Scenario 3: Environment Variables**
```typescript
// Branch A
process.env.API_URL = 'http://test-a.local'
process.env.FEATURE_FLAG = 'true'

// Branch B
process.env.API_URL = 'http://test-b.local'
process.env.DEBUG = 'true'
```

**Resolution Patterns:**

**Pattern 1: Merge Global Mocks**
```typescript
// vitest.setup.ts - AFTER MERGE
import { beforeAll, afterEach, vi } from 'vitest'

// Collect all global mocks in one place
const globalMocks = {
  fetch: vi.fn(),
  localStorage: createMockLocalStorage(),
  // ... both branches' mocks
}

// Apply all mocks
beforeAll(() => {
  global.fetch = globalMocks.fetch
  global.localStorage = globalMocks.localStorage
})

// Reset mocks between tests
afterEach(() => {
  vi.clearAllMocks()
})
```

**Pattern 2: Centralized Custom Matchers**
```typescript
// vitest.setup.ts
import { expect } from 'vitest'

// Collect from both branches
expect.extend({
  toBeWithinRange(actual: number, floor: number, ceiling: number) {
    // Branch A's matcher
  },
  toBeValidEmail(value: string) {
    // Branch B's matcher
  }
})
```

**Pattern 3: Environment Variable Merging**
```typescript
// vitest.setup.ts
const envConfig = {
  // Base config from both branches
  API_URL: process.env.API_URL || 'http://localhost:3000',
  DEBUG: process.env.DEBUG === 'true',
  FEATURE_FLAG: process.env.FEATURE_FLAG === 'true',
}

Object.assign(process.env, envConfig)
```

**Configuration in vitest.config.ts:**
```typescript
export default defineConfig({
  test: {
    setupFiles: ['./vitest.setup.ts'],  // Only one setup file entry point
    globals: true,  // Enable global access to test/expect/describe
  }
})
```

**Conflict Detection After Merge:**
- Look for **duplicate global assignments** in setup file
- Check for **conflicting environment variables**
- Verify **custom matchers don't have naming collisions**

---

### 1.4 Coverage Configuration Conflicts

**Problem:** Both branches modify coverage thresholds or reporter settings, creating repeated merge conflicts.

**High-Conflict Area: Threshold Auto-Update**

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',  // or 'istanbul'
      reporter: ['text', 'html', 'json'],
      thresholdAutoUpdate: true,  // PROBLEM AREA
      lines: 85.234567,    // Decimal precision changes with every run
      functions: 82.567890,
      branches: 78.123456,
      statements: 85.345678,
    }
  }
})
```

**Why This Causes Merge Conflicts:**
- Coverage values change by tiny decimal increments as code changes
- Two branches modify thresholds independently → merge conflicts on almost every sync
- No way to configure decimal precision (decimal places are fixed)

**Solution 1: Disable Auto-Update (Recommended for Teams)**
```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      thresholdAutoUpdate: false,  // Manual threshold updates only
      lines: 80,      // Round numbers
      functions: 80,
      branches: 75,
      statements: 80,
    }
  }
})
```

**Solution 2: Custom Function to Round Thresholds**
```typescript
export default defineConfig({
  test: {
    coverage: {
      thresholdAutoUpdate: true,
      // Custom function to round to whole numbers
      thresholds: (coverage) => {
        const lines = Math.round(coverage.lines)
        const functions = Math.round(coverage.functions)
        const branches = Math.round(coverage.branches)
        const statements = Math.round(coverage.statements)

        return { lines, functions, branches, statements }
      }
    }
  }
})
```

**Solution 3: Per-File/Glob Pattern Thresholds**
```typescript
export default defineConfig({
  test: {
    coverage: {
      lines: 80,        // Global threshold
      // Override for specific files
      thresholds: {
        lines: { './src/utils/**/*.ts': 90 },
        functions: { './src/core/**/*.ts': 95 },
      }
    }
  }
})
```

**Global vs Per-File Inconsistency:**
- Global threshold enforcement: Shows error messages clearly
- Per-glob threshold enforcement: Silent failures—verify with `vitest run --coverage`

**After Merge Conflict Resolution:**
1. Choose **round numbers** for thresholds (80, 85, 90)
2. Disable `thresholdAutoUpdate` for team projects
3. Run `vitest run --coverage` to verify new thresholds
4. Commit the resolved thresholds as baseline

---

## 2. Test File Conflict Patterns

### 2.1 Mock Factory Changes

**Problem:** Both branches mock the same module differently, creating test isolation and behavior conflicts.

**Scenario 1: Direct vi.mock Overwrites**
```typescript
// Branch A's test file
vi.mock('./api', () => ({
  fetchUser: vi.fn(() => Promise.resolve({ id: 1 }))
}))

// Branch B's test file (same file or imported)
vi.mock('./api', () => ({
  fetchUser: vi.fn(() => Promise.reject(new Error('Offline')))
}))

// After merge: Last mock wins, first is ignored
```

**Why This Happens:**
- `vi.mock()` calls are hoisted to top of file
- Second call to `vi.mock('./api')` overwrites the first factory
- No error thrown—test silently uses wrong mock

**Solution 1: Using vi.hoisted() for Shared Mocks (BEST)**
```typescript
// test.ts - After merge
const { fetchUser } = vi.hoisted(() => ({
  fetchUser: vi.fn()
}))

vi.mock('./api', () => ({ fetchUser }))

describe('API tests', () => {
  beforeEach(() => {
    // Branch A's test case
    fetchUser.mockResolvedValue({ id: 1 })
  })

  it('fetches user on success', async () => {
    expect(await fetchUser()).toEqual({ id: 1 })
  })

  it('handles offline error', () => {
    // Branch B's test case
    fetchUser.mockRejectedValue(new Error('Offline'))
  })
})
```

**How vi.hoisted() Prevents Conflicts:**
- Executes **before imports**, creating shared mock objects
- Both branches can call `.mockResolvedValue()` and `.mockRejectedValue()` on **same object**
- No duplicate `vi.mock()` calls—single source of truth

**Solution 2: Using vi.doMock() for Dynamic Mocks**
```typescript
// When you need local scope variables
beforeEach(() => {
  vi.doMock('./api', async () => ({
    fetchUser: vi.fn().mockResolvedValue({ id: 1 })
  }))
})

afterEach(() => {
  vi.doUnmock('./api')
})
```

**Difference from vi.mock():**
- `vi.mock()`: Hoisted, can't access local variables
- `vi.doMock()`: Not hoisted, runs in test context, can use local scope

**Scenario 2: Partial Mock Conflicts**
```typescript
// Branch A: Mocks only one export
vi.mock('./api', () => ({
  fetchUser: vi.fn()
  // Missing: fetchPosts, fetchComments
}))

// Branch B: Mocks different exports
vi.mock('./api', () => ({
  fetchPosts: vi.fn(),
  fetchComments: vi.fn()
  // Missing: fetchUser
}))

// After merge: Only one branch's exports available
```

**Resolution:**
```typescript
// Merged version
const mocks = vi.hoisted(() => ({
  fetchUser: vi.fn(),
  fetchPosts: vi.fn(),
  fetchComments: vi.fn(),
}))

vi.mock('./api', () => mocks)
```

**Detection After Merge:**
- Test runs but fails with "is not a function" error
- Check for multiple `vi.mock('./same-module')` calls in same file
- Look for import errors from mocked modules

---

### 2.2 Test Setup File Conflicts

**Problem:** Global mocks and custom matchers defined in setup files conflict between branches.

*See Section 1.3 for detailed setup file patterns*

**Test-Specific Additional Patterns:**

**Scenario 1: Test Fixture Mocking**
```typescript
// Branch A's test
const mockUser = { id: 1, name: 'Alice', role: 'admin' }

// Branch B's test
const mockUser = { id: 1, name: 'Alice', email: 'alice@test.com' }

// After merge: Which fixture object is used?
```

**Resolution: Centralized Test Fixtures**
```typescript
// vitest.setup.ts or fixtures/users.ts
export const testFixtures = {
  mockUser: {
    id: 1,
    name: 'Alice',
    email: 'alice@test.com',
    role: 'admin'
    // Merged from both branches
  },
  mockAdmin: { ... },
  mockGuest: { ... }
}

// In tests
import { testFixtures } from './vitest.setup'
const { mockUser } = testFixtures
```

**Scenario 2: Async Setup Conflicts**
```typescript
// Branch A
beforeAll(async () => {
  await server.listen()
  await db.connect()
})

// Branch B
beforeAll(async () => {
  await mockServer.init()
  await cache.warm()
})

// After merge: Both beforeAll hooks run (correct!)
// But order and dependencies may conflict
```

**Resolution: Ordered Setup**
```typescript
beforeAll(async () => {
  // Phase 1: Core setup (both branches)
  await server.listen()
  await db.connect()

  // Phase 2: Optional setup (branch-specific)
  if (process.env.ENABLE_CACHE) {
    await cache.warm()
  }

  // Phase 3: Verification
  expect(server.isListening).toBe(true)
})
```

---

### 2.3 Snapshot Conflicts

**Problem:** Both branches modify snapshots or add new tests with snapshot expectations, creating `.snap` file conflicts.

**Snapshot File Merge Conflict Example:**
```
<<<<<<< HEAD
exports[`Button component renders 1`] = `
<button
  class="button"
>
  Click me
</button>
`
=======
exports[`Button component renders 1`] = `
<button
  class="button button--primary"
>
  Click me
</button>
`
>>>>>>> feature/button-styling
```

**Decision Framework:**

| Situation | Action | Command |
|-----------|--------|---------|
| Both snapshots valid, different features | Manually merge snapshots | Edit `.snap` file directly |
| Snapshot outdated, needs new version | Regenerate all snapshots | `vitest -u` |
| One branch's snapshot is correct | Use that branch's snapshot | Manual edit of `.snap` |
| Uncertain which is correct | Review both, then regenerate | `vitest -u` after confirmation |

**When to Regenerate vs. Manually Resolve:**

**Regenerate (`vitest -u`) When:**
- Snapshots represent legitimate new features from both branches
- UI has intentionally changed in both branches
- Visual output is expected to differ
- You've reviewed the new output and it's correct

```bash
# Regenerate all snapshots
vitest -u

# Regenerate specific file
vitest -u src/Button.test.ts
```

**Manually Resolve When:**
- One branch's snapshot is correct, other is not
- The change represents a bug, not a feature
- Snapshot was accidentally updated
- You need to preserve parts of both snapshots

```
// Manual resolution: Keep both branches' meaningful changes
exports[`Button component renders 1`] = `
<button
  class="button button--primary"
  data-testid="primary-button"
>
  Click me
</button>
`
```

**After Merge Snapshot Workflow:**
1. **Run tests:** `vitest run` to see which snapshots fail
2. **Review visually:** Open `.snap` file and compare both versions
3. **Decide:** Regenerate or manually edit
4. **Verify:** Run `vitest run` again to confirm no new failures
5. **Commit:** `.snap` files are code—review in PR

**Concurrent Test Snapshot Note:**
When using snapshots with async concurrent tests, use local test context:
```typescript
it('concurrent snapshot test', async (ctx) => {
  expect(result).toMatchSnapshot() // Uses ctx for isolation
})
```

---

### 2.4 Test ID / Test Name Conflicts

**Problem:** Both branches add tests with the same `describe` or `it` name, causing duplicate test detection.

**Scenario 1: Duplicate Test Names**
```typescript
// Branch A
it('should handle errors', () => { ... })

// Branch B (in same file)
it('should handle errors', () => { ... }) // Different implementation

// After merge: Both exist, Vitest may error or run both
```

**Vitest Behavior with Duplicate Names:**
- Vitest allows duplicate test names (unlike Jest)
- Both tests run
- Results show as duplicate in output
- Confusing to debug which test failed

**Resolution:**
```typescript
// Merged version: Differentiate test scenarios
describe('error handling', () => {
  it('should handle network errors', () => {
    // Branch A's test
  })

  it('should handle validation errors', () => {
    // Branch B's test
  })

  it('should handle offline errors', () => {
    // Combined test for shared scenario
  })
})
```

**Scenario 2: test-id vs Semantic Queries**
```typescript
// Branch A: Uses test IDs
getByTestId('user-button')

// Branch B: Uses semantic queries
getByRole('button', { name: /user/i })

// After merge: Different query strategies in same file
```

**Resolution Philosophy:**
Prefer semantic queries over test IDs (accessibility-first):
```typescript
// AFTER MERGE: Priority order
1. getByRole('button', { name: /user/i })  // Accessible
2. getByLabelText('User')                   // Form labels
3. getByPlaceholderText('Search')          // Inputs
4. getByText('Create Account')             // Visible text
5. getByTestId('user-button')              // Last resort
```

---

## 3. Testing Library Conflicts

### 3.1 Query Strategy Changes

**Problem:** Branches use different query methods, leading to different test behaviors post-merge.

**Query Hierarchy (Recommended):**
```
BEST  → getByRole()          // Accessible, semantic
      → getByLabelText()      // Form labels
      → getByPlaceholderText()
      → getByText()           // Visible text
      → getByTestId()         // Decouple from DOM
WORST
```

**Conflict Scenario:**
```typescript
// Branch A: Accessibility-focused
getByRole('button', { name: /submit/i })

// Branch B: Test ID focused (quick migration)
getByTestId('submit-button')

// After merge: Inconsistent query strategy
```

**Why This Matters:**
- `getByRole()` verifies element is **semantically accessible**
- `getByTestId()` doesn't verify accessibility
- Mixed strategies = mixed test coverage quality

**Resolution: Standardize Query Strategy**
```typescript
// AFTER MERGE: Unified approach
describe('Form submission', () => {
  it('submits on valid input', () => {
    // Primary: Semantic query (accessible)
    const button = getByRole('button', { name: /submit/i })

    userEvent.click(button)
    expect(onSubmit).toHaveBeenCalled()
  })

  it('disables button while loading', async () => {
    const button = getByRole('button', { name: /submit/i })
    expect(button).toBeDisabled()
  })

  // Use test ID only when semantic query is impossible
  it('identifies loader overlay', () => {
    expect(getByTestId('loading-overlay')).toBeInTheDocument()
  })
})
```

**Detection After Merge:**
- Grep for mixed `getByRole`, `getByTestId`, `getByText` in same file
- Not necessarily a problem, but indicates style inconsistency

---

### 3.2 User Event Simulation Changes

**Problem:** Branches use different event simulation methods (`fireEvent` vs `userEvent`), causing behavior differences.

**fireEvent vs userEvent Comparison:**

| Aspect | fireEvent | userEvent |
|--------|-----------|-----------|
| **What it does** | Dispatches DOM events | Simulates real user interactions |
| **Events fired** | Single event per call | Multiple events (focus, input, change) |
| **Realism** | Not realistic | Very realistic |
| **Performance** | Fast (click: 724ms for 3 buttons) | Slow (click: 3603ms for 3 buttons) |
| **Browser behavior** | Skips browser defaults | Simulates browser defaults |
| **Recommendation** | Avoid (last resort) | Always prefer |

**Conflict Scenario:**
```typescript
// Branch A: Quick/legacy tests
fireEvent.click(button)
fireEvent.change(input, { target: { value: 'text' } })

// Branch B: Modern/realistic tests
await userEvent.click(button)
await userEvent.type(input, 'text')

// After merge: Mixed simulation strategies
```

**Why userEvent Is Better:**
```typescript
// fireEvent.change() does this:
// - Sets value
// - Fires change event
// (Missing: focus, input event, selection changes)

// userEvent.type() does this:
// 1. Focuses element
// 2. Fires keydown for each character
// 3. Fires keypress
// 4. Updates value
// 5. Fires input event
// 6. Fires change event
// 7. Fires keyup
// (Realistic: matches real typing)
```

**Migration After Merge:**
```typescript
// BEFORE (fireEvent)
fireEvent.click(submitButton)
fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

// AFTER (userEvent)
await userEvent.click(submitButton)
await userEvent.type(emailInput, 'test@example.com')

// IMPORTANT: userEvent is async!
```

**When fireEvent is Still Valid:**
- Testing unsupported interactions in userEvent
- Specific DOM event verification needed
- Performance-critical tests (use sparingly)

```typescript
// OK: Verify specific event fired (userEvent doesn't allow this)
fireEvent.mouseEnter(element)
expect(tooltipOpen).toBe(true)

// Better: Test the user's observable result
await userEvent.hover(element)
expect(getByRole('tooltip')).toBeInTheDocument()
```

**Performance Consideration:**
If tests become too slow after migration to userEvent:
1. First: Optimize component, not tests
2. Then: Use `userEvent.setup()` for better performance
3. Last resort: Use `fireEvent` for specific interactions

```typescript
// Performance optimization
const user = userEvent.setup()
await user.click(button)
await user.type(input, 'text')
```

---

### 3.3 Render Wrapper Conflicts

**Problem:** Both branches modify the test provider hierarchy, creating wrapper configuration conflicts.

**Scenario 1: Multiple Provider Additions**
```typescript
// Branch A's custom render
function renderWithTheme(component) {
  return render(component, {
    wrapper: ThemeProvider
  })
}

// Branch B's custom render (same file!)
function renderWithTheme(component) {
  return render(component, {
    wrapper: ({ children }) => (
      <ThemeProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </ThemeProvider>
    )
  })
}

// After merge: One definition wins, both providers needed?
```

**Conflict Indicators:**
- Duplicate `render()` function exports
- Different wrapper component hierarchies
- Tests fail with "useTheme is not available" or "useAuth is not available"

**Solution: Merged Provider Wrapper**
```typescript
// test/setup.tsx - Single render function
import { ThemeProvider } from '@theme/ThemeProvider'
import { AuthProvider } from '@auth/AuthProvider'
import { QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function AllTheProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

export function renderWithProviders(
  component: React.ReactElement,
  options = {}
) {
  return render(component, {
    wrapper: AllTheProviders,
    ...options
  })
}

// In tests: Use single custom render function
import { renderWithProviders as render } from '@test/setup'

it('shows user with theme', () => {
  render(<UserProfile />)
  // Both theme and auth context available
})
```

**Scenario 2: Wrapper Prop Passing Issues**
```typescript
// Branch A: Simple wrapper
const wrapper = ({ children }) => <Provider>{children}</Provider>

// Branch B: Wrapper that needs props
const wrapper = ({ children, value }) => (
  <Provider value={value}>{children}</Provider>
)

// After merge: How to pass `value` to wrapper?
```

**Solution: Higher-Order Wrapper**
```typescript
// Fixed wrapper with prop support
function createWrapper(initialValue = 'default') {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider value={initialValue}>
        {children}
      </Provider>
    )
  }
}

// Usage in tests
it('renders with custom value', () => {
  const wrapper = createWrapper('custom-value')
  render(<Component />, { wrapper })
})
```

**Scenario 3: Rerender with Wrapper Issue**
```typescript
// Problem: Rerendering doesn't apply new wrapper props
const { rerender } = render(<Component prop="A" />, {
  wrapper: ThemeProvider
})

// Rerender with new prop—but wrapper props don't update
rerender(<Component prop="B" />)
```

**Solution: Custom render with rerender support**
```typescript
export function renderWithProviders(component, options = {}) {
  const Wrapper = ({ children }) => (
    <Provider value={options.providerValue}>
      {children}
    </Provider>
  )

  const renderResult = render(component, { wrapper: Wrapper })

  return {
    ...renderResult,
    rerenderWithProvider: (newComponent, newOptions) => {
      const newWrapper = ({ children }) => (
        <Provider value={newOptions?.providerValue}>
          {children}
        </Provider>
      )
      return renderResult.rerender(newComponent, { wrapper: newWrapper })
    }
  }
}
```

---

### 3.4 Act() Warning Introduction

**Problem:** Merged code introduces or surfaces `act()` warnings that weren't present in individual branches.

**Warning Message:**
```
Warning: An update to [Component] inside a test was not wrapped in act(...)
```

**Root Causes After Merge:**

**Cause 1: Async State Updates Not Awaited**
```typescript
// Branch A
const { rerender } = render(<Component />)
fireEvent.click(button)
rerender(<Component />)  // State update not awaited

// Branch B
render(<Component />)
await someAsyncAction()
// Implicit state update from promise resolution

// After merge: Combined code triggers act warning
```

**Cause 2: Version Incompatibility**
```typescript
// Branch A uses @testing-library/react 13.4.0
// Branch B updated to @testing-library/react 14.0.0+
// Merged package.json has 14.0.0

// Result: Version change surfaced act warnings
```

**Cause 3: Setup/Teardown Async Issues**
```typescript
// Branch A
afterEach(() => {
  cleanup()
})

// Branch B
afterEach(async () => {
  await waitFor(() => expect(api.calls).toBe(0))
})

// After merge: Both afterEach hooks run
// State updates in async afterEach not wrapped
```

**Solutions:**

**Solution 1: Wrap in act() Explicitly**
```typescript
import { act } from 'react-dom/test-utils'  // or 'vitest'

await act(async () => {
  fireEvent.click(button)
  await waitFor(() => expect(result).toBeVisible())
})
```

**Solution 2: Use Testing Library Async Utilities (BEST)**
```typescript
// These are already wrapped in act()
import { waitFor, findBy* } from '@testing-library/react'

// Instead of fireEvent + manual act:
await waitFor(() => {
  expect(element).toBeVisible()
})

// Or use findBy* queries (waitFor internally)
const button = await findByRole('button', { name: /save/i })
```

**Solution 3: Avoid Manual State Updates**
```typescript
// BAD: Can trigger act warnings
fireEvent.click(button)
// Test assumes state update completes immediately

// GOOD: Wait for state update
await userEvent.click(button)
await waitFor(() => expect(onSubmit).toHaveBeenCalled())
```

**Solution 4: Fix Async Setup/Teardown**
```typescript
// BEFORE
afterEach(() => {
  cleanup()  // Synchronous
})

// AFTER
afterEach(async () => {
  await cleanup()  // Wait for cleanup
  // or use synchronous cleanup if possible
})

// Or defer async cleanup
afterEach(() => {
  cleanup()
  // Don't have async operations in afterEach
})
```

**Version Check After Merge:**
```bash
# Check installed versions
npm list @testing-library/react

# If 14.0.0+ and seeing new warnings:
# 1. Update to latest 14.x
# 2. Review migration guide for breaking changes
```

**When Warning is Harmless:**
- Test passes despite warning
- Warning occurs in cleanup phase
- No actual test failure

**When to Address:**
- Test intermittently fails
- Warning in assertion phase (not cleanup)
- Specific to merged code changes

---

## 4. Distinguishing Test Failures: Wrong Resolution vs. Test Updates

### 4.1 Test Failure Types After Merge

**Type 1: Failure Because Resolution Was Wrong** (FIX RESOLUTION)
**Type 2: Failure Because Test Itself Is Outdated** (UPDATE TEST)
**Type 3: False Positive / Environmental** (FIX ENVIRONMENT)

### 4.2 Decision Framework

```
┌─ Test fails after merge resolution
│
├─ Did test pass on BOTH branches before merge?
│  │
│  ├─ YES → Resolution is wrong
│  │       Action: Review merged code, fix resolution
│  │
│  └─ NO → Test itself changed or needs update
│          Action: Update test or revert to passing version
│
└─ Does test pass on main/develop without your merge?
   │
   ├─ YES → Merge resolution introduced the failure
   │       Action: Fix the resolution
   │
   └─ NO → Test was already failing or has environmental issue
           Action: Isolate environmental factors
```

### 4.3 Diagnostic Test Cases

**Case 1: Test Passing on Both Branches, Failing After Merge**

```
Branch A commit: Test passes ✓
Branch B commit: Test passes ✓
After merge: Test fails ✗
```

**This ALWAYS indicates wrong resolution.**

```typescript
// DIAGNOSTIC STEPS

// 1. Verify test passes on both branches
git checkout branch-a
npm test -- Component.test.ts  // ✓ Passes?

git checkout branch-b
npm test -- Component.test.ts  // ✓ Passes?

// 2. Check current merged state
git checkout main  // Your merge branch
npm test -- Component.test.ts  // ✗ Fails?

// 3. If both pass individually but fails merged:
// The resolution is WRONG.
// Review conflicts in Component.ts or Component.test.ts
```

**How to Fix:**
1. Identify the conflict in the actual code (not the test)
2. Review what each branch changed
3. Ensure both changes are represented correctly
4. Run test again

**Example:**
```typescript
// Component.ts after merge (wrong resolution)
export function Button({ onClick, label }) {
  return <button onClick={onClick}>{label}</button>
  // Missing: disabled prop from Branch B
}

// Branch A added: onClick handling
// Branch B added: disabled state
// Resolution lost Branch B's disabled prop

// Fix: Add back the disabled prop
export function Button({ onClick, label, disabled }) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  )
}
```

---

**Case 2: Test Was Already Failing or Outdated**

```
Branch A commit: Test fails or doesn't exist ✗
Branch B commit: Test passes ✓
After merge: Test fails ✗
```

**This indicates test needs updating, NOT resolution issue.**

```typescript
// DIAGNOSTIC STEPS

// 1. Check test history
git log --all -- Component.test.ts | head -20

// 2. Check if test existed in branch-a
git show branch-a:src/Component.test.ts > /dev/null 2>&1
echo $?  // 0 = existed, 1 = didn't exist

// 3. If test is new or was failing in branch-a:
// UPDATE the test to match new merged behavior
```

**Example:**
```
Branch A: Component API was v1
Branch B: Component API updated to v2, new tests added
After merge: Tests written for v2 API fail on v1 code

Fix: Update component code OR test to one consistent version
```

---

**Case 3: Snapshot Failure After Merge**

```
Snapshot mismatch after merge
```

**Diagnostic:**
```typescript
// 1. Run test with update flag
vitest -u Component.test.ts

// 2. Review snapshot diff
git diff Component.test.ts.snap

// 3. Verify new snapshot is correct
// If YES: Commit updated snapshot
// If NO: Revert and manually resolve snapshot conflict

// 4. What caused the change?
// - Branch A modified component rendering?
// - Branch B modified component rendering?
// - Both made changes that combined unexpectedly?
```

**Decision:**
- If snapshot change is intentional from merged features: Accept
- If snapshot change is unintended: Fix code, not snapshot

---

### 4.4 Environmental/Setup Issues (False Positives)

**Type 3 Test Failures: Not resolution issues, but environment:**

```
Symptom: Same test fails on CI but passes locally
Symptom: Test fails intermittently
Symptom: Test fails only when run with other tests
```

**Common Causes:**

**Cause: Test Isolation Issues**
```typescript
// Global mock not cleaned up
beforeAll(() => {
  vi.mock('./api')
})
// Missing: afterEach cleanup

// Fix:
afterEach(() => {
  vi.clearAllMocks()  // Or vi.doUnmock()
})
```

**Cause: Async Cleanup**
```typescript
beforeEach(async () => {
  await server.listen()
})

// Missing: afterEach cleanup
// Fix:
afterEach(() => {
  server.close()
})
```

**Cause: Environment Variable Conflicts**
```
Test expects: process.env.API_URL = 'http://test.local'
After merge: API_URL might be different from other branch
Test fails only when run with other tests that change env vars
```

**Cause: Provider Initialization Order**
After merge, multiple providers might initialize in wrong order:
```typescript
// Setup file has providers A, B, C
// Merged code expects order A → B → C
// But somehow running as C → B → A

// Check vitest.setup.ts for provider order
```

---

### 4.5 Decision Flowchart with Actions

```
TEST FAILS AFTER MERGE RESOLUTION
│
├─→ Check: Did test pass on BOTH branches individually?
│   │
│   ├─ YES (Both passed) → RESOLUTION IS WRONG
│   │   Action:
│   │   1. git show branch-a:file.ts vs branch-b:file.ts
│   │   2. Identify what each branch changed
│   │   3. Ensure BOTH changes present in merged file
│   │   4. Re-run test
│   │
│   └─ NO (Passed on one, failed on other) → TEST ITSELF NEEDS UPDATE
│       Action:
│       1. Determine which branch is "correct"
│       2. Update test to match that branch's expectations
│       3. Or update code to match test expectations
│       4. Re-run test
│
├─→ Check: Does test pass on main without your merge?
│   │
│   ├─ YES → MERGE INTRODUCED ISSUE
│   │   Go to above: check both branches
│   │
│   └─ NO → ENVIRONMENTAL/BASELINE ISSUE
│       Action:
│       1. Check vitest.setup.ts for setup conflicts
│       2. Check test isolation: afterEach cleanup
│       3. Check mock cleanup: vi.clearAllMocks()
│       4. Check async handling: await server.listen()
│       5. Run with --reporter=verbose for details
│
└─→ If still failing: Run diagnostic
    Command: vitest run --reporter=verbose --reporter=tap
    Check: Error message, stack trace, setup logs
```

---

## 5. Mock and Fixture Conflicts

### 5.1 Shared Test Fixtures Modified by Both Branches

**Problem:** Both branches add or modify shared test fixtures, creating conflicts.

**Scenario: Fixture File Additions**
```typescript
// fixtures/users.ts before merge conflict
export const mockUsers = {
  admin: { id: 1, role: 'admin' }
}

// Branch A adds:
const superAdmin = { id: 0, role: 'super_admin' }

// Branch B adds:
const guest = { id: 999, role: 'guest', permissions: [] }

// After merge: Both additions needed
```

**Resolution:**
```typescript
// fixtures/users.ts - AFTER MERGE
export const mockUsers = {
  superAdmin: { id: 0, role: 'super_admin' },
  admin: { id: 1, role: 'admin' },
  guest: { id: 999, role: 'guest', permissions: [] },
}

export const createMockUser = (overrides = {}) => ({
  id: Math.random(),
  name: 'Test User',
  role: 'user',
  ...overrides
})
```

**Scenario: Fixture Function Conflicts**
```typescript
// Branch A
export function createMockPost(title = 'Default Title') {
  return { id: 1, title, published: true }
}

// Branch B
export function createMockPost(overrides = {}) {
  return {
    id: 1,
    title: 'Test Post',
    published: false,
    ...overrides
  }
}

// After merge: Different signatures
```

**Solution: Consolidated Fixture Factory**
```typescript
// MERGED VERSION
interface MockPostOptions {
  id?: number
  title?: string
  published?: boolean
  [key: string]: any
}

export function createMockPost(options: MockPostOptions = {}) {
  return {
    id: options.id ?? 1,
    title: options.title ?? 'Default Title',
    published: options.published ?? true,
    ...options
  }
}

// Usage matches both branches
createMockPost({ title: 'Custom' })  // Branch A style
createMockPost({ title: 'Custom', published: false })  // Branch B style
```

---

### 5.2 Mock Server Configuration Conflicts (MSW Handlers)

**Problem:** Both branches add handlers to MSW (Mock Service Worker), creating route conflicts.

**Scenario: Handler Duplication**
```typescript
// Branch A: handlers.ts
export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Alice' })
  })
]

// Branch B: handlers.ts
export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Bob', role: 'admin' })
  })
]

// After merge: Last handler wins (Branch B)
```

**Resolution: Merged Handlers**
```typescript
// handlers.ts - AFTER MERGE
import { http, HttpResponse } from 'msw'

export const handlers = [
  // Base user handler (from Branch B - more complete)
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Alice',
      role: 'admin'  // From Branch B
    })
  }),

  // New handler from Branch A (if it was different endpoint)
  http.post('/api/users', async ({ request }) => {
    const data = await request.json()
    return HttpResponse.json({ id: 2, ...data }, { status: 201 })
  })
]
```

**Key MSW Principle:**
> When multiple handlers match the same request, the **last one in the array** is used. No error thrown.

**Conflict Pattern: Handler Override Issue**
```typescript
// Problem: Both branches add handler for same endpoint
export const handlers = [
  // Branch A's handler (for feature-x)
  http.post('/api/users/:id/profile', ({ request }) => {
    return HttpResponse.json({ updated: true })
  }),

  // Branch B's handler (for feature-y, same endpoint!)
  http.post('/api/users/:id/profile', ({ request }) => {
    return HttpResponse.json({ saved: true })
  }),
  // Branch B's handler overrides Branch A's
]

// After merge: Tests for Branch A fail (wrong response)
```

**Solution: Single Handler Serving Both Needs**
```typescript
// MERGED HANDLER
http.post('/api/users/:id/profile', async ({ request }) => {
  const body = await request.json()

  // Serve different responses based on request body
  if (body.updateProfile) {
    return HttpResponse.json({ updated: true })  // Branch A
  } else {
    return HttpResponse.json({ saved: true })    // Branch B
  }
})

// Or use different endpoints entirely
http.post('/api/users/:id/profile', () =>
  HttpResponse.json({ updated: true })  // Branch A
)
http.patch('/api/users/:id/profile', () =>
  HttpResponse.json({ saved: true })    // Branch B
)
```

**Scenario: Per-Test Handler Overrides**
```typescript
// Branch A: Base handler in setup
// Branch B: Overrides handler in specific tests

// After merge: Both patterns exist
setupServer(
  http.get('/api/data', () =>
    HttpResponse.json({ data: [] })
  )
)

// In test (Branch B's pattern)
beforeEach(() => {
  server.use(
    http.get('/api/data', () =>
      HttpResponse.json({ data: [1, 2, 3] })  // Override
    )
  )
})

// Resolution: Ensure afterEach cleanup
afterEach(() => {
  server.resetHandlers()  // IMPORTANT: Reset after each test
})
```

**After Merge MSW Verification:**
```bash
# 1. Check for duplicate route patterns
grep -r "http\." handlers.ts

# 2. Run tests and verify API responses
vitest run --reporter=verbose

# 3. If tests fail with wrong response:
# - Review handler array order
# - Check for .use() overrides in tests
# - Verify server.resetHandlers() in afterEach
```

---

### 5.3 Environment Variable Mocks

**Problem:** Both branches mock different environment variables or set them differently.

**Scenario: Conflicting Environment Setup**
```typescript
// Branch A: vitest.setup.ts
process.env.API_URL = 'http://test-a.local:3000'
process.env.LOG_LEVEL = 'error'

// Branch B: vitest.setup.ts
process.env.API_URL = 'http://test-b.local:3000'
process.env.API_TIMEOUT = '5000'
process.env.FEATURE_FLAG = 'true'

// After merge: Which env vars are actually set?
```

**Resolution: Consolidated Environment Setup**
```typescript
// vitest.setup.ts - AFTER MERGE
const testEnvConfig = {
  // Common base config
  API_URL: process.env.API_URL || 'http://localhost:3000',

  // Branch A's variables
  LOG_LEVEL: process.env.LOG_LEVEL || 'error',

  // Branch B's variables
  API_TIMEOUT: process.env.API_TIMEOUT || '5000',
  FEATURE_FLAG: process.env.FEATURE_FLAG === 'true',

  // Merged variables with defaults
  NODE_ENV: 'test',
  DEBUG: process.env.DEBUG === 'true',
}

// Apply config
Object.assign(process.env, testEnvConfig)

export const getTestEnv = () => testEnvConfig
```

**Scenario: Per-Test Environment Override**
```typescript
// Branch A: Global env var
process.env.FEATURE_X_ENABLED = 'true'

// Branch B: Per-test env override
beforeEach(() => {
  process.env.FEATURE_Y_ENABLED = 'true'
})
afterEach(() => {
  delete process.env.FEATURE_Y_ENABLED
})

// After merge: Both patterns exist—need consolidation
```

**Solution: Environment Manager**
```typescript
// vitest.setup.ts
export class TestEnvManager {
  private originalEnv: Record<string, string | undefined> = {}

  setEnv(key: string, value: string | undefined) {
    if (!this.originalEnv[key]) {
      this.originalEnv[key] = process.env[key]
    }
    if (value === undefined) {
      delete process.env[key]
    } else {
      process.env[key] = value
    }
  }

  resetEnv() {
    Object.entries(this.originalEnv).forEach(([key, value]) => {
      if (value === undefined) {
        delete process.env[key]
      } else {
        process.env[key] = value
      }
    })
    this.originalEnv = {}
  }
}

export const envManager = new TestEnvManager()

// In tests
beforeEach(() => {
  envManager.setEnv('FEATURE_X_ENABLED', 'true')
})

afterEach(() => {
  envManager.resetEnv()
})
```

**Verification After Merge:**
```typescript
// Check setup file for env var conflicts
vitest.setup.ts:
- process.env.VAR1 = 'value1'
- process.env.VAR2 = 'value2'
// Both should be present

// Verify in test
console.log(process.env.API_URL)  // From merged setup
```

---

## 6. CI Integration and Test Execution

### 6.1 Running Tests After Merge Resolution

**Basic Command:**
```bash
# Run all tests
vitest run

# Run specific file
vitest run src/Component.test.ts

# Run with verbose output
vitest run --reporter=verbose

# Run with multiple reporters
vitest run --reporter=verbose --reporter=json

# Watch mode (for development)
vitest
```

**Post-Merge Test Workflow:**
```bash
# 1. Run all tests
npm test  # or: vitest run

# 2. If failures, run with verbose reporter
vitest run --reporter=verbose > test-results.txt

# 3. Review failures and identify type:
# - Resolution failure (fix code)
# - Test failure (update test)
# - Environment issue (fix setup)

# 4. Regenerate snapshots if needed
vitest -u

# 5. Final verification
npm test
```

---

### 6.2 Coverage Integration After Merge

**Basic Coverage Command:**
```bash
# Run tests with coverage
vitest run --coverage

# Specify coverage reporters
vitest run --coverage --coverage.reporter=text --coverage.reporter=html

# View HTML coverage report
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
start coverage/index.html  # Windows
```

**Coverage Report Interpretation:**
```
File                    | % Stmts | % Branch | % Funcs | % Lines |
-----------------------|---------|----------|---------|---------|
All files               |    85.2 |     78.9 |    82.1 |    85.1 |
 src/                   |    85.2 |     78.9 |    82.1 |    85.1 |
  Component.tsx         |    91.2 |     87.5 |    95.0 |    91.2 |
  utils.ts              |    78.5 |     70.2 |    75.0 |    78.5 |
```

**After Merge: Coverage Conflicts**

**Scenario: Coverage Regression**
```
Before merge:
- Component.tsx: 95% coverage
- utils.ts: 90% coverage

After merge:
- Component.tsx: 82% coverage (regression!)
- utils.ts: 85% coverage (regression!)
```

**Diagnosis:**
```bash
# 1. Identify which branch's code was merged incorrectly
git show branch-a:src/Component.tsx > /tmp/a.tsx
git show branch-b:src/Component.tsx > /tmp/b.tsx
git show HEAD:src/Component.tsx > /tmp/merged.tsx

# 2. Compare visually
diff /tmp/a.tsx /tmp/merged.tsx

# 3. Check if merge removed test cases or added untested code
```

**Fix:**
- Add missing test cases from both branches
- Or remove untested code if it's not critical

---

### 6.3 Coverage Threshold Conflicts (Post-Merge)

**Scenario: Threshold Auto-Update Conflict Continues**

```yaml
# git merge conflict in vitest.config.ts
< <<<<<<< HEAD (Branch A)
  lines: 85.234567,
  functions: 82.567890,
| =======
  lines: 82.123456,  (Branch B)
  functions: 79.987654,
> >>>>>>> branch/feature
```

**Resolution:**
```typescript
// vitest.config.ts - AFTER MERGE
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      thresholdAutoUpdate: false,  // Disable auto-update
      lines: 80,      // Use round numbers
      functions: 80,
      branches: 75,
      statements: 80,
    }
  }
})
```

**Verification:**
```bash
# 1. Run coverage
vitest run --coverage

# 2. Check if thresholds passed
# Output will indicate PASS or FAIL for each threshold

# 3. If passing but too low, increase thresholds gradually
# (Don't jump from 75% to 95% in one commit)
```

---

### 6.4 CI Pipeline Configuration

**GitHub Actions Example (Post-Merge):**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - run: npm ci

      # Run tests with verbose reporter
      - run: npm test -- --reporter=verbose

      # Fail if coverage thresholds not met
      - run: npm test -- --coverage
        env:
          CI: true

      # Upload coverage reports
      - uses: codecov/codecov-action@v3
        if: always()
```

**CI Test Failure Diagnosis:**
```bash
# If CI fails but local tests pass:
# 1. Check Node version mismatch
node --version

# 2. Check environment variables
echo $API_URL

# 3. Run with CI env var
CI=true vitest run --reporter=verbose

# 4. Check system memory/limits
free -h
```

---

## 7. Decision Frameworks

### 7.1 Snapshot Conflict Resolution Decision Tree

```
SNAPSHOT CONFLICT DETECTED
│
├─ Both snapshots look visually reasonable?
│  │
│  ├─ NO (One is obviously broken)
│  │   └─ Keep: [the correct one]
│  │      Manual edit: Delete wrong snapshot
│  │
│  └─ YES (Both look valid, different features)
│     │
│     ├─ Can both changes coexist?
│     │  │
│     │  ├─ YES → Merge snapshots manually
│     │  │         Edit: Combine both versions
│     │  │
│     │  └─ NO → Pick one to keep
│     │         Question: Which feature is more important?
│     │
│     └─ Regenerate snapshots
│         vitest -u
│         Review result: Is output correct?
```

### 7.2 Mock Conflict Decision Tree

```
MOCK CONFLICT DETECTED (vi.mock duplicate)
│
├─ Same module, same test file?
│  │
│  ├─ YES → Use vi.hoisted() pattern
│  │         Consolidate: Single mock definition
│  │         Both tests use: Same mock object with different impl
│  │
│  └─ NO (Different files)
│     └─ Independent mocks: Usually OK
│        (Verify: Run tests, no conflicts)
│
├─ Different module mocks, same factory structure?
│  │
│  └─ Check: Are both needed for merged functionality?
│     ├─ YES → Keep both
│     └─ NO → Consolidate into single mock
│
└─ If tests still fail:
   └─ Debug: Which mock is being called?
      vi.mock(...).toHaveBeenCalled()
```

### 7.3 Test Failure Attribution Decision Tree

```
TEST FAILS AFTER MERGE
│
├─ STEP 1: Checkout both branches individually
│  ├─ Branch A test result: ?
│  ├─ Branch B test result: ?
│  └─ Merged test result: FAIL
│
├─ STEP 2: Both branches passed?
│  │
│  ├─ YES (BOTH: ✓, MERGED: ✗)
│  │   → RESOLUTION IS WRONG
│  │   Action:
│  │   1. Review merged code in conflicted file
│  │   2. Ensure both feature changes are present
│  │   3. Re-test
│  │
│  └─ NO (One/Both failed on their branch)
│     → TEST ITSELF NEEDS UPDATE
│     Action:
│     1. Determine which test is "correct"
│     2. Update test or implementation
│     3. Re-test
│
├─ STEP 3: Still failing?
│  │
│  └─ ENVIRONMENTAL/SETUP ISSUE
│     Check:
│     1. vi.clearAllMocks() in afterEach?
│     2. server.resetHandlers() in afterEach?
│     3. Environment variables correct?
│     4. Setup file conflicts resolved?
│
└─ STEP 4: Run diagnostic
   vitest run --reporter=verbose --reporter=tap
   Review error message and stack trace
```

### 7.4 Configuration Conflict Priority Matrix

```
CONFLICT TYPE          | PRIORITY | HOW TO MERGE
-----------------------|----------|------------------------------------------
Config file (vitest vs vite) | HIGH    | Use mergeConfig + keep test config separate
Test environment       | HIGH    | Choose based on test requirements
Setup file globals     | HIGH    | Consolidate, avoid duplicates
Mock factories         | HIGH    | Use vi.hoisted() for shared mocks
Snapshots              | MEDIUM  | Review visually, regenerate or merge
Coverage thresholds    | LOW     | Round numbers, disable auto-update
Test names             | MEDIUM  | Rename for clarity
Environment variables  | MEDIUM  | Merge all needed variables with defaults
```

---

## Sources and References

### Vitest Documentation
- [Vitest Configuration](https://vitest.dev/config/)
- [Vitest Test Environment Guide](https://vitest.dev/guide/environment)
- [Vitest Mocking Guide](https://vitest.dev/guide/mocking.html)
- [Vitest vi.hoisted Documentation](https://vitest.dev/api/vi.html)
- [Vitest Coverage Configuration](https://vitest.dev/config/coverage)
- [Vitest CLI Guide](https://vitest.dev/guide/cli)
- [Vitest Snapshot Testing](https://vitest.dev/guide/snapshot)

### Testing Library Documentation
- [React Testing Library API](https://testing-library.com/docs/react-testing-library/api/)
- [Testing Library: Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Testing Library Query Methods](https://testing-library.com/docs/react-testing-library/cheatsheet/)
- [Fix the "not wrapped in act(...)" warning](https://kentcdodds.com/blog/fix-the-not-wrapped-in-act-warning)
- [userEvent vs fireEvent Comparison](https://blog.mimacom.com/react-testing-library-fireevent-vs-userevent/)

### Mock Service Worker (MSW)
- [Mock Service Worker Documentation](https://mswjs.io/)
- [MSW Network Behavior Overrides](https://mswjs.io/docs/best-practices/network-behavior-overrides/)
- [MSW Testing Patterns](https://www.callstack.com/blog/guide-to-mock-service-worker-msw)

### Community Resources
- [Vitest vs Jest Migration Guide](https://vitest.dev/guide/migration.html)
- [Advanced Vitest Mocking Guide](https://blog.logrocket.com/advanced-guide-vitest-testing-mocking/)
- [React Testing Best Practices](https://medium.com/@ignatovich.dm/best-practices-for-using-react-testing-library-0f71181bb1f4)

---

## Appendix: Quick Reference Checklists

### Post-Merge Test Verification Checklist

```
□ Configuration Conflicts
  □ vitest.config.ts vs vite.config.ts reconciled
  □ Test environment consistent (jsdom/happy-dom/node)
  □ Setup file globals merged (not duplicated)
  □ Coverage thresholds reviewed and set reasonably

□ Test Files
  □ No duplicate vi.mock() calls for same module
  □ Mock factories use vi.hoisted() for shared mocks
  □ Snapshot conflicts resolved (manually or regenerated)
  □ Test names unique and descriptive

□ Testing Library
  □ Query strategy consistent (prefer getByRole)
  □ Event simulation consistent (prefer userEvent)
  □ Render wrappers consolidated
  □ No act() warnings in critical paths

□ Execution & CI
  □ npm test passes locally
  □ vitest run --coverage passes thresholds
  □ CI pipeline green
  □ No environment variable conflicts
  □ Mock cleanup in afterEach hooks

□ Final Verification
  □ Checkout both branches individually: tests pass
  □ Merged state: tests pass
  □ Coverage report reviewed
  □ No flaky tests
```

### Configuration Merge Template

```typescript
// vitest.config.ts - POST-MERGE TEMPLATE
import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      // Environment
      environment: 'jsdom',  // Chosen from both branches

      // Setup
      setupFiles: ['./vitest.setup.ts'],  // Single setup file
      globals: true,

      // Coverage (non-conflicting)
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html', 'json'],
        thresholdAutoUpdate: false,
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      }
    }
  })
)
```

---

**Document Version:** 1.0
**Last Updated:** April 7, 2026
**Scope:** Vitest + Testing Library merge conflict patterns and resolution strategies
