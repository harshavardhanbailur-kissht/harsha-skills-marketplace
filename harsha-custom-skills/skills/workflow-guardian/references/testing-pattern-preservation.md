# Testing Pattern Preservation: A Defensive Guide

**Version:** 1.0
**Last Updated:** February 2026
**Focus:** Test Infrastructure Detection, Pattern Matching, Safe Addition, Breakage Prevention

---

## Executive Summary

When modifying or extending applications with existing test coverage, Claude's greatest risk is breaking tests without realizing it. This reference guide provides systematic detection methods, pattern matching approaches, and defensive strategies for adding features while preserving the existing test infrastructure.

### The Critical Gap

**Most breaking changes to applications occur in tested code, not untested code.** Here's why:

1. **Existing tests are a safety net** - They validate that specific component behavior works
2. **Tests encode implicit requirements** - A test for `submitForm()` reveals what the form is *supposed* to do
3. **Mock patterns reveal data contracts** - Test mocks show what shape data takes when used
4. **Test utilities are shared** - Changing how tests import utilities can break dozens of tests

The workflow-guardian skill's approach: **Never modify tested components without ensuring tests still pass. When adding features, write tests that follow the EXACT pattern of existing tests in the codebase.**

---

## Part 1: Test Infrastructure Detection

### 1.1 Identifying the Test Framework

**Why this matters:** Different frameworks have different syntax, assertion styles, and configuration patterns. Matching the framework is the first step to pattern preservation.

#### Detection Strategy

```bash
# Check for Jest configuration
grep -l "jest" package.json jest.config.js jest.config.json jest.setup.js

# Check for Vitest configuration
grep -l "vitest" package.json vitest.config.js vitest.config.ts

# Check for Playwright
grep -l "playwright" package.json playwright.config.js playwright.config.ts

# Check for Cypress
grep -l "cypress" package.json cypress.config.js cypress.config.ts

# Check for Testing Library
grep -l "@testing-library" package.json tsconfig.json

# Check for test files by extension
find . -name "*.test.js" -o -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.js" -o -name "*.spec.ts" -o -name "*.spec.tsx" | head -5
```

#### Framework Signatures in package.json

```json
// JEST SIGNATURE
{
  "devDependencies": {
    "jest": "^29.0.0",
    "ts-jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "@testing-library/react": "^14.0.0"
  }
}

// VITEST SIGNATURE
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0"
  }
}

// PLAYWRIGHT SIGNATURE
{
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "playwright": "^1.40.0"
  }
}
```

### 1.2 Test Configuration Files

**Jest Configuration Detection**

```javascript
// jest.config.js - Most common pattern
module.exports = {
  preset: 'ts-jest', // TypeScript support
  testEnvironment: 'jsdom', // Browser environment
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1', // Path aliases
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
  ],
};

// jest.config.ts - TypeScript configuration
import type { Config } from 'jest';

const config: Config = {
  // ... same as above
};

export default config;
```

**Vitest Configuration Detection**

```typescript
// vitest.config.ts - Standard Vitest pattern
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

**Playwright Configuration Detection**

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
  ],
});
```

### 1.3 Setup Files and Fixtures

**Critical Setup Files to Preserve**

```typescript
// setupTests.ts or setupTests.js - Most important file
// Located at: src/setupTests.ts, test/setup.ts, or configured in test framework

// Pattern 1: Jest/Vitest global setup
import '@testing-library/jest-dom';

// Indicates Testing Library matchers are available
// These are custom matchers like toBeInTheDocument(), toBeVisible()
// If you modify imports here, all tests break

// Pattern 2: MSW (Mock Service Worker) setup
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Indicates API mocking is centralized
// Tests expect ALL fetch calls to be intercepted

// Pattern 3: Provider setup for global contexts
import { Provider } from 'react-redux';
import store from './store';

beforeEach(() => {
  // Tests may require specific store state
});

// Pattern 4: Custom render function
import { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';

function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, {
    wrapper: ({ children }) => (
      <Provider store={store}>
        {children}
      </Provider>
    ),
    ...options,
  });
}

export { customRender as render };
```

**Detection Pattern**

```bash
# Find setup files
find . -name "setupTests.*" -o -name "setup.ts" -o -name "setup.js" | head -10

# Check for setup file references in config
grep -r "setupFilesAfterEnv\|setupFiles" . | grep -v node_modules

# Find custom render utilities (usually in test utilities folder)
find . -path "*/test/*" -name "*render*" -o -path "*/testing/*" -name "*render*"
```

### 1.4 Mock Patterns and Mock Directories

**Jest Mock Directory Pattern**

```
src/
├── api/
│   ├── fetchUser.ts
│   └── __mocks__/
│       └── fetchUser.ts        # Jest auto-mocks this
├── services/
│   ├── authService.ts
│   └── __mocks__/
│       └── authService.ts
└── tests/
    └── setupTests.ts
```

**MSW (Mock Service Worker) Pattern - Modern Standard**

```typescript
// mocks/server.ts - Server-side handler setup
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// mocks/handlers.ts - All API endpoint definitions
import { http, HttpResponse } from 'msw';

export const handlers = [
  // Pattern for GET requests
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'John' });
  }),

  // Pattern for POST requests
  http.post('/api/login', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ token: 'abc123' });
  }),

  // Pattern for error responses
  http.get('/api/error', () => {
    return HttpResponse.json({ error: 'Not found' }, { status: 404 });
  }),
];

// mocks/browser.ts - Browser worker for Storybook/dev
import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);
```

**Manual Mock Pattern**

```typescript
// __mocks__/authService.ts
export const mockAuthService = {
  login: jest.fn().mockResolvedValue({ token: 'mock-token' }),
  logout: jest.fn().mockResolvedValue(undefined),
  getUser: jest.fn().mockResolvedValue({ id: 1, name: 'Test User' }),
};

// In tests
jest.mock('../../services/authService', () => ({
  authService: mockAuthService,
}));
```

**Detection Strategy**

```bash
# Find MSW setup
find . -path "*/mocks/server.ts" -o -path "*/mocks/handlers.ts"

# Find Jest __mocks__ directories
find . -type d -name "__mocks__"

# Find manual jest.mock() calls in tests
grep -r "jest.mock\|vi.mock" --include="*.test.ts" --include="*.test.tsx" | head -5

# Find mock-related packages
grep -E "msw|jest-mock|nock" package.json
```

### 1.5 Test Utility Files and Custom Render Functions

**Where to Find Test Utilities**

```bash
# Common locations
src/testUtils.ts
src/test/setup.ts
src/test/utils.ts
src/testing/render.tsx
tests/helpers.ts
tests/utils.ts
__tests__/utils.ts
```

**Typical Test Utility File Structure**

```typescript
// src/testUtils.tsx - Complete example
import React, { ReactElement } from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import store from '../store';
import theme from '../theme';

// Custom render that wraps components with necessary providers
function render(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </Provider>
    );
  }

  return rtlRender(ui, { wrapper: Wrapper, ...options });
}

// Re-export everything from RTL
export * from '@testing-library/react';

// Export custom render
export { render };

// Common test data factories
export const mockUser = {
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
};

export const mockProject = {
  id: '1',
  name: 'Test Project',
  description: 'A test project',
};

// Assertion helpers
export function expectToBeVisible(element: HTMLElement) {
  expect(element).toBeVisible();
}

export function expectToHaveText(element: HTMLElement, text: string) {
  expect(element).toHaveTextContent(text);
}
```

**Detection Checklist**

- [ ] Find custom `render` function - used in all component tests
- [ ] Find test data factories/mocks - reveals expected data shapes
- [ ] Find assertion helpers - reveals common test patterns
- [ ] Check for context providers in wrapper - indicates global state setup
- [ ] Look for describe/beforeEach/afterEach patterns - reveals test structure

---

## Part 2: Test Pattern Matching

### 2.1 Test Structure Patterns (Arrange-Act-Assert)

**Standard Pattern in Jest/Vitest**

```typescript
// Pattern 1: Simple unit test structure
describe('UserForm', () => {
  // ARRANGE: Set up test data and mocks
  const mockOnSubmit = jest.fn();
  const defaultProps = {
    onSubmit: mockOnSubmit,
    initialData: { name: '', email: '' },
  };

  // Optional: Run before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should display form fields', () => {
    // ARRANGE
    const { getByLabelText } = render(<UserForm {...defaultProps} />);

    // ACT
    const nameField = getByLabelText(/name/i);

    // ASSERT
    expect(nameField).toBeInTheDocument();
  });

  it('should call onSubmit when form is submitted', async () => {
    // ARRANGE
    const { getByLabelText, getByRole } = render(
      <UserForm {...defaultProps} />
    );
    const nameField = getByLabelText(/name/i);
    const submitButton = getByRole('button', { name: /submit/i });

    // ACT
    await userEvent.type(nameField, 'John Doe');
    await userEvent.click(submitButton);

    // ASSERT
    expect(mockOnSubmit).toHaveBeenCalledWith({ name: 'John Doe', email: '' });
  });
});

// Pattern 2: Async test pattern with userEvent
it('should validate email field', async () => {
  const { getByLabelText, getByText } = render(<UserForm {...defaultProps} />);
  const emailField = getByLabelText(/email/i);

  // ACT
  await userEvent.type(emailField, 'invalid-email');
  await userEvent.tab(); // Trigger validation

  // ASSERT
  expect(getByText(/invalid email/i)).toBeInTheDocument();
});

// Pattern 3: Testing hooks (React Testing Library)
import { renderHook, act } from '@testing-library/react';

it('should increment counter', () => {
  const { result } = renderHook(() => useCounter());

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

**Detection Indicators**

```bash
# Check assertion style used
grep -r "expect(" --include="*.test.ts" --include="*.test.tsx" | head -3
# Output indicates: expect().toBe (Jest/Vitest) vs expect().equal (Chai)

# Check if using userEvent or fireEvent
grep -r "userEvent\|fireEvent" --include="*.test.ts" --include="*.test.tsx" | head -3

# Check for async patterns
grep -r "async\|await\|waitFor" --include="*.test.ts" --include="*.test.tsx" | head -3
```

### 2.2 Assertion Styles and Matchers

**Jest/Vitest Built-in Matchers (Most Common)**

```typescript
// Identity and type checks
expect(value).toBe(expected);           // Exact equality (===)
expect(value).toEqual(expected);        // Deep equality
expect(value).toStrictEqual(expected);  // Strict equality (no type coercion)

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeDefined();
expect(value).toBeUndefined();
expect(value).toBeNull();

// Numbers
expect(value).toBeGreaterThan(5);
expect(value).toBeCloseTo(0.3);

// Strings
expect(str).toContain('substring');
expect(str).toMatch(/regex/);

// Arrays and objects
expect(array).toContain(item);
expect(array).toHaveLength(3);
expect(obj).toHaveProperty('key');

// Exceptions
expect(() => { throw new Error(); }).toThrow();
expect(() => { throw new Error(); }).toThrowError('message');

// Mocks
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith(arg1, arg2);
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveReturnedWith(value);
```

**Testing Library Matchers (@testing-library/jest-dom)**

```typescript
// DOM presence and visibility
expect(element).toBeInTheDocument();
expect(element).toBeVisible();
expect(element).toHaveStyle('display: none');

// Attributes and content
expect(element).toHaveAttribute('disabled');
expect(element).toHaveTextContent('text');
expect(element).toHaveValue('value');
expect(element).toHaveClass('className');

// Forms
expect(input).toHaveFocus();
expect(input).toBeChecked();
expect(input).toBeRequired();

// Accessibility
expect(element).toHaveAccessibleName('name');
expect(element).toHaveRole('button');
```

**Pattern Detection**

```bash
# Find specific matcher style
grep -o "toBe\|toEqual\|toHaveBeenCalled\|toBeInTheDocument" *.test.ts | sort | uniq -c

# Identifies primary assertion patterns in the codebase
```

**Safe Addition Rule**

> When adding new tests, match the EXACT assertion style used in existing tests. If existing tests use `toEqual()` for objects, use `toEqual()` in new tests. Do not mix assertion styles.

### 2.3 Mock Patterns for Services and API Calls

**Pattern 1: MSW (Recommended for 2025-2026)**

```typescript
// mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  // GET with response
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'John Doe',
      email: 'john@example.com',
    });
  }),

  // POST with request body parsing
  http.post('/api/users', async ({ request }) => {
    const userData = await request.json();
    return HttpResponse.json({ id: 'new-id', ...userData }, { status: 201 });
  }),

  // DELETE with error response
  http.delete('/api/users/:id', ({ params }) => {
    if (params.id === 'protected') {
      return HttpResponse.json(
        { error: 'Cannot delete protected user' },
        { status: 403 }
      );
    }
    return HttpResponse.json({ success: true });
  }),

  // Delay pattern for testing loading states
  http.get('/api/slow-endpoint', async () => {
    await new Promise(resolve => setTimeout(resolve, 100));
    return HttpResponse.json({ data: 'delayed' });
  }),
];

// In tests, override handlers as needed
import { server } from './mocks/server';

it('should handle error response', () => {
  server.use(
    http.get('/api/users/:id', () => {
      return HttpResponse.json(
        { error: 'Not found' },
        { status: 404 }
      );
    })
  );
  // Test error handling
});
```

**Pattern 2: Jest Manual Mocks**

```typescript
// __mocks__/api.ts
const mockApi = {
  getUser: jest.fn(() => Promise.resolve({ id: 1, name: 'Test' })),
  createUser: jest.fn((data) => Promise.resolve({ id: 2, ...data })),
  deleteUser: jest.fn(() => Promise.resolve({ success: true })),
};

export default mockApi;

// In test file
jest.mock('../api');
import api from '../api';

it('should fetch user', async () => {
  api.getUser.mockResolvedValue({ id: 1, name: 'John' });

  const result = await api.getUser(1);

  expect(result.name).toBe('John');
});
```

**Pattern 3: Inline jest.mock() with Factory Function**

```typescript
// Most flexible pattern for complex mocks
jest.mock('../api', () => ({
  api: {
    getUser: jest.fn((id) => {
      if (id === 'error') {
        return Promise.reject(new Error('User not found'));
      }
      return Promise.resolve({ id, name: 'Test User' });
    }),
  },
}));
```

**Detection Strategy**

```bash
# Check for MSW setup
grep -r "setupServer\|setupWorker\|mswjs" --include="*.ts" --include="*.tsx"

# Check for jest.mock() usage
grep -r "jest.mock\|vi.mock" --include="*.test.ts" --include="*.test.tsx"

# Check for __mocks__ directories
find . -type d -name "__mocks__" | wc -l

# Identify mock pattern being used
grep -r "http.get\|http.post" --include="*.ts" | grep -v node_modules  # MSW pattern
```

### 2.4 File Naming and Organization Patterns

**Jest Conventions (Most Common)**

```
Standard structure:
src/
├── components/
│   ├── UserForm.tsx
│   ├── UserForm.test.tsx         # Co-located test
│   ├── UserForm.module.css
│   └── __tests__/
│       └── UserForm.test.tsx      # Alternative: separate __tests__ folder
├── hooks/
│   ├── useUser.ts
│   └── useUser.test.ts
├── services/
│   ├── api.ts
│   └── api.test.ts
├── __mocks__/                     # Global mock location
│   ├── api.ts
│   └── authService.ts
└── setupTests.ts
```

**Vitest Conventions**

```
Vitest supports same patterns but also:
src/
├── components/
│   ├── Button.tsx
│   ├── Button.spec.ts             # .spec preferred in Vitest
│   └── Button.test.ts             # .test also works
├── __vitest__/                    # Vitest-specific folder (optional)
│   └── setup.ts
```

**Playwright Conventions**

```
tests/
├── e2e/
│   ├── login.spec.ts
│   ├── dashboard.spec.ts
├── fixtures/
│   ├── auth.ts
│   └── database.ts
└── config.ts
```

**Detection Method**

```bash
# Find all test files and their extensions
find src -type f \( -name "*.test.tsx" -o -name "*.test.ts" -o -name "*.spec.tsx" -o -name "*.spec.ts" \) | head -10

# Check naming ratio
find src -name "*.test.*" | wc -l      # Count .test files
find src -name "*.spec.*" | wc -l      # Count .spec files

# Find __tests__ directories
find src -type d -name "__tests__"
```

**Safe Addition Rule**

> When creating a new test file, use the EXACT same naming convention as existing test files. If the codebase uses `.test.tsx`, create `NewComponent.test.tsx`. If it uses `.spec.ts`, create `newHook.spec.ts`. Never mix conventions in the same codebase.

### 2.5 Import Patterns and Test Utilities Usage

**Pattern 1: Standard Import Pattern**

```typescript
// Most common pattern - import render from custom utility
import { render, screen } from '../testUtils';
import { UserForm } from './UserForm';

// This means ALL tests in this project use the custom render
// Changing the render export breaks all tests
```

**Pattern 2: Direct React Testing Library Import**

```typescript
// Alternative pattern - import directly from library
import { render, screen } from '@testing-library/react';
import { UserForm } from './UserForm';

// This means components render WITHOUT custom providers/wrappers
// Tests expect NO global provider setup
```

**Pattern 3: Vitest-Specific Imports**

```typescript
// Vitest allows importing test utilities with defineConfig
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Vitest globals are enabled - don't need to import
// Jest would require: import { describe, it, expect } from '@jest/globals'
```

**Pattern 4: Mock Imports**

```typescript
// Pattern A: Type-safe import with jest type
import type { MockedFunction } from 'jest-mock';
import { mockApi } from '../__mocks__/api';

// Pattern B: Simple mock import
import { mockAuthService } from '../__mocks__/authService';

// Pattern C: MSW import
import { server } from '../mocks/server';
```

**Detection Method**

```bash
# Find import patterns in test files
head -20 src/**/*.test.tsx | grep -E "^import"

# Check if custom render is used
grep -r "from.*testUtils\|from.*test/utils" --include="*.test.ts" --include="*.test.tsx" | wc -l

# Check if direct RTL imports are used
grep -r "from.*@testing-library" --include="*.test.ts" --include="*.test.tsx" | wc -l

# Compare patterns
head -5 src/**/*.test.tsx
```

**Safe Addition Rule**

> Mirror the import structure exactly. If existing tests use `import { render, screen } from '../testUtils'`, use the SAME import path in new tests. If they import utilities from `@testing-library/react` directly, do the same.

---

## Part 3: Safe Feature Addition with Tests

### 3.1 Adding a New Component with Tests

**Process: Pattern Extraction → Safe Addition**

**Step 1: Analyze Existing Component Test**

```typescript
// EXISTING: analyze this pattern
// src/components/Button.test.tsx
import { render, screen } from '../testUtils';  // Import pattern
import { Button } from './Button';
import userEvent from '@testing-library/user-event';  // Event handling

describe('Button', () => {                       // describe() structure
  it('should render button with text', () => {  // it() naming pattern
    // ARRANGE
    render(<Button label="Click me" />);

    // ACT
    const button = screen.getByRole('button');   // Query method

    // ASSERT
    expect(button).toHaveTextContent('Click me');  // Assertion matcher
  });

  it('should call onClick when clicked', async () => {
    const mockOnClick = jest.fn();                 // Mock creation pattern
    render(<Button label="Click" onClick={mockOnClick} />);

    const button = screen.getByRole('button');
    await userEvent.click(button);                // userEvent pattern

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button label="Click" disabled />);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
```

**Step 2: Extract Pattern Elements**

```
Pattern Elements Extracted:
✓ Import source: '../testUtils' (custom render)
✓ Test structure: describe() → it() → ARRANGE/ACT/ASSERT
✓ Query method: screen.getByRole()
✓ Mock pattern: jest.fn()
✓ Event handling: userEvent.click()
✓ Assertion style: expect().toHaveTextContent()
✓ Async pattern: async/await
✓ Prop naming: camelCase (onClick, disabled)
```

**Step 3: Apply Pattern to New Component**

```typescript
// NEW: UserCard.test.tsx - Following EXACT pattern
import { render, screen } from '../testUtils';  // SAME import
import { UserCard } from './UserCard';
import userEvent from '@testing-library/user-event';  // SAME package

describe('UserCard', () => {                    // SAME structure
  it('should render user information', () => {  // SAME naming style
    // ARRANGE
    const userData = {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
    };
    render(<UserCard user={userData} />);

    // ACT
    const userName = screen.getByText('John Doe');  // SAME query method

    // ASSERT
    expect(userName).toBeInTheDocument();  // SAME matcher
  });

  it('should call onEdit when edit button is clicked', async () => {
    const mockOnEdit = jest.fn();  // SAME mock pattern
    const userData = { id: '1', name: 'John' };
    render(<UserCard user={userData} onEdit={mockOnEdit} />);

    const editButton = screen.getByRole('button', { name: /edit/i });
    await userEvent.click(editButton);  // SAME event handling

    expect(mockOnEdit).toHaveBeenCalledWith('1');  // SAME assertion
  });

  it('should show delete confirmation when delete is clicked', async () => {
    const mockOnDelete = jest.fn();
    const userData = { id: '1', name: 'John' };
    render(<UserCard user={userData} onDelete={mockOnDelete} />);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await userEvent.click(deleteButton);

    // New assertion - but matching existing style
    expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
  });
});
```

**Pattern Preservation Checklist**

- [ ] Import `render` and `screen` from the same source as existing tests
- [ ] Use `describe()` and `it()` naming structure
- [ ] Follow ARRANGE-ACT-ASSERT comment pattern
- [ ] Use `screen.getByRole()` or `screen.getByText()` if existing tests do
- [ ] Use `jest.fn()` for mocks (or `vi.fn()` if Vitest)
- [ ] Use `userEvent` for interactions (not `fireEvent`)
- [ ] Use same assertion matchers (`toBeInTheDocument`, `toHaveTextContent`, etc.)
- [ ] Name test descriptions in same style (e.g., "should..." vs "renders...")

### 3.2 Adding API Calls with Mock Tests

**Scenario: Adding a new API endpoint**

**Step 1: Analyze Existing API Mock Pattern**

```typescript
// EXISTING: mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: 1, name: 'Alice', role: 'admin' },
      { id: 2, name: 'Bob', role: 'user' },
    ]);
  }),

  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'John',
      role: 'user',
    });
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: 'new-id', ...body },
      { status: 201 }
    );
  }),
];
```

**Step 2: Extract Pattern Elements**

```
Pattern Elements:
✓ Framework: MSW (http.get, http.post)
✓ Handler structure: http.METHOD('/path', ({ params, request }) => {})
✓ Response style: HttpResponse.json()
✓ Error handling: { status: 404 }
✓ Async pattern: async ({ request }) => { await request.json() }
✓ Params access: ({ params })
```

**Step 3: Add New Endpoint Following Pattern**

```typescript
// EXTENDED: mocks/handlers.ts - add new endpoint
export const handlers = [
  // ... existing handlers ...

  // NEW: Following exact pattern
  http.get('/api/projects', () => {
    return HttpResponse.json([
      { id: 1, name: 'Project A', status: 'active' },
      { id: 2, name: 'Project B', status: 'archived' },
    ]);
  }),

  http.post('/api/projects', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: 'proj-new', ...body },
      { status: 201 }
    );
  }),

  http.delete('/api/projects/:id', ({ params }) => {
    return HttpResponse.json({ success: true });
  }),
];
```

**Step 4: Add Tests Following Existing Test Pattern**

```typescript
// EXISTING test pattern
it('should fetch users', async () => {
  const { result } = renderHook(() => useUsers());

  await act(async () => {
    await result.current.fetchUsers();
  });

  expect(result.current.users).toHaveLength(2);
  expect(result.current.users[0].name).toBe('Alice');
});

// NEW test - following EXACT pattern
it('should fetch projects', async () => {
  const { result } = renderHook(() => useProjects());

  await act(async () => {
    await result.current.fetchProjects();
  });

  expect(result.current.projects).toHaveLength(2);
  expect(result.current.projects[0].name).toBe('Project A');
});

// Existing error test pattern
it('should handle fetch error', async () => {
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    })
  );

  const { result } = renderHook(() => useUsers());

  await act(async () => {
    await result.current.fetchUsers();
  });

  expect(result.current.error).toBe('Unauthorized');
});

// NEW error test - same pattern
it('should handle project fetch error', async () => {
  server.use(
    http.get('/api/projects', () => {
      return HttpResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      );
    })
  );

  const { result } = renderHook(() => useProjects());

  await act(async () => {
    await result.current.fetchProjects();
  });

  expect(result.current.error).toBe('Forbidden');
});
```

**Safe API Addition Checklist**

- [ ] Add handler to `mocks/handlers.ts` using exact MSW syntax pattern
- [ ] Match HTTP method patterns (http.get, http.post, etc.)
- [ ] Match response format (HttpResponse.json with same structure)
- [ ] Match error handling pattern (status codes consistent with existing)
- [ ] Add tests using same test pattern as existing API tests
- [ ] Test success case first, then error case
- [ ] Use same assertion pattern (expect result values to match)
- [ ] Test with `renderHook` if it's a custom hook
- [ ] Override handlers in tests same way existing tests do

### 3.3 Adding Routes with Navigation Tests

**Step 1: Analyze Existing Route Pattern**

```typescript
// EXISTING: routes.tsx or router configuration
import { Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { UserList } from './pages/UserList';
import { UserDetail } from './pages/UserDetail';
import { ProtectedRoute } from './components/ProtectedRoute';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/users" element={<UserList />} />
      <Route
        path="/users/:id"
        element={<ProtectedRoute roles={['admin']} element={<UserDetail />} />}
      />
    </Routes>
  );
}

// EXISTING test pattern
import { BrowserRouter as Router } from 'react-router-dom';
import { render, screen } from '../testUtils';

it('should render dashboard on root path', () => {
  render(
    <Router>
      <AppRoutes />
    </Router>
  );

  expect(screen.getByText(/welcome/i)).toBeInTheDocument();
});

it('should render protected route only for authorized users', () => {
  // Mock auth context
  const mockAuth = { user: { role: 'user' }, isAuthenticated: true };

  render(
    <Router>
      <AuthProvider value={mockAuth}>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );

  // Protected route should not render
  expect(screen.queryByText(/admin only/i)).not.toBeInTheDocument();
});
```

**Step 2: Extract Route Pattern Elements**

```
Pattern Elements:
✓ Router: React Router (Routes, Route components)
✓ Structure: Route path → element mapping
✓ Guards: ProtectedRoute wrapper
✓ Role-based: roles prop array
✓ Test setup: Wrap in Router in test
✓ Test pattern: Render route + check if element appears
✓ Auth testing: Mock auth context
✓ Assertion: screen.getByText() for rendered content
```

**Step 3: Add New Route Following Pattern**

```typescript
// EXTENDED: routes.tsx
export function AppRoutes() {
  return (
    <Routes>
      // ... existing routes ...

      // NEW: Following exact pattern
      <Route path="/projects" element={<ProjectList />} />
      <Route
        path="/projects/:id"
        element={<ProtectedRoute roles={['admin']} element={<ProjectDetail />} />}
      />
    </Routes>
  );
}
```

**Step 4: Add Route Tests Following Pattern**

```typescript
// NEW: projectRoutes.test.tsx - following exact pattern

it('should render project list on /projects', () => {
  render(
    <Router>
      <AppRoutes />
    </Router>
  );

  // Navigate and test
  window.history.pushState({}, '', '/projects');

  expect(screen.getByText(/projects/i)).toBeInTheDocument();
});

it('should render protected project detail for authorized users', () => {
  const mockAuth = { user: { role: 'admin' }, isAuthenticated: true };

  render(
    <Router>
      <AuthProvider value={mockAuth}>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );

  window.history.pushState({}, '', '/projects/123');

  expect(screen.getByText(/project details/i)).toBeInTheDocument();
});

it('should not render protected project detail for non-admin', () => {
  const mockAuth = { user: { role: 'user' }, isAuthenticated: true };

  render(
    <Router>
      <AuthProvider value={mockAuth}>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );

  window.history.pushState({}, '', '/projects/123');

  expect(screen.queryByText(/unauthorized/i)).toBeInTheDocument();
});
```

**Route Addition Checklist**

- [ ] Add route with exact same pattern as existing routes
- [ ] Apply protection wrapper same way (ProtectedRoute, roles array)
- [ ] Write test wrapping Routes in Router
- [ ] Test both allowed and denied access scenarios
- [ ] Test that correct component renders for path
- [ ] Use screen.getByText() to verify rendered content
- [ ] Mock auth context same way existing tests do
- [ ] Use pushState pattern if testing navigation

---

## Part 4: Test Breakage Prevention

### 4.1 Common Breaking Changes

**Break Type 1: Modifying Component Props**

```typescript
// EXISTING component and test
// Button.tsx
interface ButtonProps {
  label: string;
  onClick?: () => void;
}

// Button.test.tsx
it('should render button with label', () => {
  render(<Button label="Click me" />);
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});

// DANGEROUS CHANGE: Rename prop
interface ButtonProps {
  text: string;  // BREAK: Was 'label'
  onClick?: () => void;
}

// This breaks the test:
// ❌ <Button label="Click me" /> no longer works
// ❌ Button.test.tsx still passes 'label' prop
// ❌ Component doesn't receive the label

// SAFE CHANGE: Add prop, keep old one (backward compatible)
interface ButtonProps {
  label?: string;        // Keep for backward compatibility
  text?: string;         // New prop
  onClick?: () => void;
}

export function Button({ label, text, onClick }: ButtonProps) {
  const displayText = text || label;
  return <button onClick={onClick}>{displayText}</button>;
}
```

**Break Type 2: Changing Component Structure**

```typescript
// EXISTING component
export function UserCard({ user }: { user: User }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <p data-testid="user-email">{user.email}</p>
    </div>
  );
}

// EXISTING test relying on structure
it('should display user email', () => {
  render(<UserCard user={mockUser} />);
  expect(screen.getByTestId('user-email')).toBeInTheDocument();
});

// DANGEROUS CHANGE: Wrap in container
export function UserCard({ user }: { user: User }) {
  return (
    <article>  // NEW: Added article wrapper
      <header>
        <h2>{user.name}</h2>
      </header>
      <section>  // NEW: Email moved into section
        <p data-testid="user-email">{user.email}</p>
      </section>
    </article>
  );
}

// Test still works ✓ (testid preserved)
// BUT if tests used selectors like:
// screen.getByRole('heading') - still works
// screen.getByText(user.name) - still works
// BUT: screen.queryAllByRole('paragraph') behavior might change

// SAFER CHANGE: Extend structure, preserve existing elements
export function UserCard({ user }: { user: User }) {
  return (
    <article>
      <h2>{user.name}</h2>  // Keep structure
      <p data-testid="user-email">{user.email}</p>  // Keep exact element
      <footer>New content</footer>  // Add new elements
    </article>
  );
}
```

**Break Type 3: Modifying Shared Utilities**

```typescript
// EXISTING: testUtils.tsx
export function render(ui: ReactElement, options?: RenderOptions) {
  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </Provider>
    ),
    ...options,
  });
}

// This custom render is used in 47 test files
// Any change breaks all 47 tests

// DANGEROUS CHANGE: Remove provider
export function render(ui: ReactElement, options?: RenderOptions) {
  return rtlRender(ui, { ...options });  // No wrapper!
}

// BREAK: All tests expecting Redux state now fail
// BREAK: All tests expecting theme now fail
// BREAK: 47 test files need updating

// SAFE CHANGE: Add optional provider, keep default
export function render(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & { withoutProviders?: boolean }
) {
  if (options?.withoutProviders) {
    return rtlRender(ui, { ...options });
  }

  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </Provider>
    ),
    ...options,
  });
}

// Existing tests work as-is ✓
// New tests can opt-out if needed ✓
```

**Break Type 4: Changing Mock Data Shapes**

```typescript
// EXISTING: mocks/handlers.ts
http.get('/api/users/:id', ({ params }) => {
  return HttpResponse.json({
    id: params.id,
    name: 'John Doe',
    email: 'john@example.com',
    createdAt: '2024-01-01',  // This shape matters
  });
}),

// EXISTING: tests rely on this shape
it('should display user creation date', () => {
  const { result } = renderHook(() => useUser('1'));

  act(() => {
    result.current.load();
  });

  expect(result.current.user.createdAt).toBe('2024-01-01');
});

// DANGEROUS CHANGE: Remove or rename field
http.get('/api/users/:id', ({ params }) => {
  return HttpResponse.json({
    id: params.id,
    name: 'John Doe',
    email: 'john@example.com',
    // createdAt removed!
  });
}),

// BREAK: Test expects createdAt, mock doesn't provide it
// Test fails: expect(undefined).toBe('2024-01-01')

// SAFE CHANGE: Add field, keep existing fields
http.get('/api/users/:id', ({ params }) => {
  return HttpResponse.json({
    id: params.id,
    name: 'John Doe',
    email: 'john@example.com',
    createdAt: '2024-01-01',  // Keep existing
    updatedAt: '2024-02-26',  // Add new
  });
}),

// Existing tests work ✓
// New tests can use updatedAt ✓
```

**Break Type 5: Missing Test Wrapper Provider**

```typescript
// EXISTING: Component that uses context
function Dashboard() {
  const { user } = useAuth();  // Expects AuthContext
  const { theme } = useTheme();  // Expects ThemeContext
  return <div>{user.name}</div>;
}

// EXISTING: testUtils provides both contexts
export function render(ui: ReactElement) {
  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <AuthProvider>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </AuthProvider>
    ),
  });
}

// DANGEROUS NEW COMPONENT: Adds another context
function Dashboard() {
  const { user } = useAuth();
  const { theme } = useTheme();
  const { notifications } = useNotifications();  // NEW
  return <div>{user.name}</div>;
}

// BREAK: Test renders Dashboard but NotificationContext not provided
// useNotifications() throws error
// Test fails: "useNotifications must be used within NotificationProvider"

// SAFE FIX: Update render function
export function render(ui: ReactElement) {
  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <AuthProvider>
        <ThemeProvider>
          <NotificationProvider>  // Add new provider
            {children}
          </NotificationProvider>
        </ThemeProvider>
      </AuthProvider>
    ),
  });
}

// Now all tests work again ✓
```

### 4.2 Breaking Change Detection Checklist

**Before Modifying Any Tested Component:**

- [ ] **Search for all test files** that import the component
  ```bash
  grep -r "import.*Component" --include="*.test.ts" --include="*.test.tsx"
  ```

- [ ] **Check all existing tests** for the component
  ```bash
  find . -name "Component.test.tsx" -o -name "Component.spec.ts"
  ```

- [ ] **Review prop usage** in existing tests
  ```bash
  grep -r "<Component" *.test.tsx | grep -o "prop=[^}]*" | sort -u
  ```

- [ ] **Check query selectors** used in tests
  ```bash
  grep -r "getByTestId\|getByRole\|getByText" Component.test.tsx
  ```

- [ ] **Verify mock data structure** in tests
  ```bash
  grep -A5 "mockData\|mockUser\|mockProject" Component.test.tsx
  ```

- [ ] **Look for snapshot tests** that will break
  ```bash
  grep -r "toMatchSnapshot\|toMatchInlineSnapshot" Component.test.tsx
  ```

**Before Modifying Test Setup or Utilities:**

- [ ] **Count files using the utility**
  ```bash
  grep -r "from.*testUtils" --include="*.test.tsx" | wc -l
  ```

- [ ] **List all files** that import it
  ```bash
  grep -r "from.*testUtils" --include="*.test.tsx"
  ```

- [ ] **Check for snapshot tests** using the render
  ```bash
  grep -r "toMatchSnapshot" --include="*.test.tsx" | grep -c "render"
  ```

**Before Changing Mock Handlers:**

- [ ] **Find all handler usages**
  ```bash
  grep -r "http.get\|http.post" mocks/handlers.ts
  ```

- [ ] **Search for tests** mocking those handlers
  ```bash
  grep -r "server.use\|server.override" --include="*.test.ts"
  ```

- [ ] **Check data shape** expectations
  ```bash
  grep -r "expect.*\[0\]\|expect.*\.id\|expect.*\.name" --include="*.test.tsx"
  ```

### 4.3 Snapshot Testing Breakage

**Understanding Snapshot Tests**

```typescript
// snapshot test - captures rendered output
it('should match snapshot', () => {
  render(<UserCard user={mockUser} />);
  expect(document.body.innerHTML).toMatchSnapshot();
});

// When you run tests, snapshot is saved to:
// UserCard.test.tsx.snap
// This file is version controlled

// Snapshot content:
exports[`should match snapshot 1`] = `
<div>
  <h2>John Doe</h2>
  <p>john@example.com</p>
</div>
`;
```

**Breaking Snapshots Intentionally**

```typescript
// DANGEROUS: Component change breaks snapshot
export function UserCard({ user }: { user: User }) {
  return (
    <article>
      <header>
        <h2>{user.name}</h2>
      </header>
      <section>
        <p>{user.email}</p>
      </section>
    </article>
  );
}

// Test fails: snapshot mismatch
// Current: <article><header>...
// Expected: <div><h2>...

// MUST: Review snapshot change, then update
// Command: npm test -- --updateSnapshot

// Then verify change was intentional by reviewing .snap file diff
```

**Safe Snapshot Handling**

```bash
# Before modifying component:
# 1. Run tests to establish baseline
npm test

# 2. Review which tests have snapshots
grep -r "toMatchSnapshot" --include="*.test.tsx"

# 3. After modifying component, check diff
npm test 2>&1 | grep -A10 "Snapshot"

# 4. Review diff carefully - is it intentional?
# 5. Update snapshot only if change was intentional
npm test -- --updateSnapshot

# 6. Commit snapshot change
git diff *.snap  # Review before commit
```

**Prevention Rules**

- [ ] Never update snapshots without reviewing the diff
- [ ] Never modify component just to "pass snapshot tests"
- [ ] Always ask: "Is this visual change intentional?"
- [ ] Keep snapshots in version control
- [ ] Review snapshot diffs in pull requests

---

## Part 5: Running Tests as Verification

### 5.1 Identifying the Test Command

**Detection Method**

```bash
# Check package.json scripts
cat package.json | grep -A 20 '"scripts"'

# Look for common test commands
grep -E '"test"|"jest"|"vitest"' package.json

# Common patterns:
# "test": "jest"
# "test": "vitest"
# "test": "vitest run"
# "test:watch": "jest --watch"
# "test:coverage": "jest --coverage"
```

**Running Tests in Different Frameworks**

```bash
# Jest
npm test                          # Run all tests
npm test -- --watch              # Watch mode
npm test -- Component.test.tsx    # Run specific test
npm test -- --coverage            # With coverage report
npm test -- --updateSnapshot      # Update snapshots

# Vitest
npm test                          # Run all tests
npm run test:watch               # Watch mode (if configured)
vitest run                        # Run once (exit after)
vitest --coverage                # Coverage report
vitest --ui                       # UI dashboard

# Playwright
npm run test:e2e                 # Run E2E tests
npx playwright test              # Run playwright tests
npx playwright test --headed     # Show browser
npx playwright test --debug      # Debug mode
```

### 5.2 Running Tests After Changes

**Safe Verification Pattern**

```bash
# Step 1: Run tests related to your change
npm test -- Component.test.tsx      # Specific test file
npm test -- --testPathPattern="components"  # All component tests

# Step 2: Check for test failures
# Output shows:
# ✓ passed tests (green)
# ✗ failed tests (red)
# ⊙ skipped tests (gray)

# Step 3: If tests fail - DO NOT proceed
# Example output:
# FAIL src/components/Button.test.tsx
# ✓ should render button (12ms)
# ✗ should call onClick (45ms)
#   Expected: 1 call
#   Received: 0 calls

# Step 4: Run full test suite before committing
npm test

# Step 5: Check coverage report
npm test -- --coverage
```

**Expected Test Output**

```
Test Suites: 15 passed, 15 total
Tests:       87 passed, 87 total
Snapshots:   3 passed, 3 total
Time:        23.456 s

All tests passed!
```

**Failure Output**

```
Test Suites: 1 failed, 14 passed, 15 total
Tests:       2 failed, 85 passed, 87 total

FAIL src/components/UserForm.test.tsx
  UserForm
    ✗ should submit form with data (125ms)
      Expected: mockOnSubmit was called with [{"name": "John", "email": "john@example.com"}]
      Received: mockOnSubmit was not called

    ✗ should validate email field (89ms)
      Error: element with text "Invalid email" not found
```

### 5.3 Understanding Test Coverage Reports

**Coverage Report Interpretation**

```
File                  | % Stmts | % Branch | % Funcs | % Lines |
------|---------|----------|---------|---------|
All   |  78.5%  |  65.3%   |  82.1%  |  78.9%  |
```

**Understanding Coverage Metrics**

```
Statements (% Stmts): Lines of code executed by tests
- 90% = Most code is tested
- 60% = Some code is untested
- 40% = Many untested code paths

Branches (% Branch): Conditional paths (if/else, ternary)
- 80% = Most conditions tested
- 50% = Many edge cases not tested

Functions (% Funcs): Functions that are called in tests
- 85% = Most functions have tests
- 70% = Some functions untested

Lines (% Lines): Physical lines of code covered
- Similar to statements, more granular
```

**Coverage Report in Terminal**

```bash
npm test -- --coverage

# Output:
# ├── src/components/Button.tsx           91.5% covered
# ├── src/hooks/useUser.ts                78.2% covered
# ├── src/services/api.ts                 65.4% covered ← Gaps visible
# └── src/utils/format.ts                 100% covered

# Detailed report in HTML
open coverage/lcov-report/index.html  # macOS
xdg-open coverage/lcov-report/index.html  # Linux
```

**Coverage Gap Investigation**

```bash
# Find untested code
npm test -- --coverage --verbose

# Look for files with low coverage
npm test -- --coverage | grep -E "[0-9]{1,2}\.[0-9]" | awk '$2 < 70 {print}'

# Example output:
# src/services/api.ts 65.4%
# src/utils/validation.ts 58.2%
```

### 5.4 Detecting When Code Lacks Tests

**Danger Signs**

```bash
# 1. New files with no test file
find src -name "*.tsx" ! -name "*.test.tsx" ! -name "*.spec.tsx" | grep -v __tests__

# 2. Files with 0% coverage
npm test -- --coverage | grep "0\.0%"

# 3. Test files excluded from coverage
grep -E "collectCoverageFrom|coveragePathIgnorePatterns" jest.config.js

# 4. Untested directories
npm test -- --coverage | grep "^src/" | awk '$3 == 0 {print}'
```

**Coverage Threshold Enforcement**

```javascript
// jest.config.js - defines minimum required coverage
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/main.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 70,      // Must test 70% of conditions
      functions: 75,     // Must test 75% of functions
      lines: 75,         // Must test 75% of lines
      statements: 75,    // Must test 75% of statements
    },
    './src/critical/': {
      branches: 90,      // Critical code requires 90%
      functions: 90,
      lines: 90,
      statements: 90,
    },
  },
};

// Test result if threshold not met:
// npm test
// Coverage thresholds not met:
// ├─ Lines 74.5% < 75%
// ├─ Statements 73.8% < 75%
// └─ Functions 76.2% > 75% ✓
// Test suite fails - must add tests before commit
```

**Verification Workflow**

```bash
# 1. After making changes, run tests
npm test

# 2. Check coverage
npm test -- --coverage

# 3. Identify gaps
npm test -- --coverage | grep -E "^src.*[0-9]{1,2}\.[0-9]"

# 4. If gaps in modified files
#    → Add tests for new/modified code
#    → Re-run tests
#    → Verify coverage threshold passed

# 5. If all tests pass
#    → Safe to commit
#    → Safe to push
```

---

## Part 6: Test-Related Breakage Patterns (Real Examples)

### 6.1 Breaking a Component Without Updating Tests

**Scenario: Adding Optional Field to Form**

```typescript
// EXISTING: UserForm.tsx with tests
interface UserFormProps {
  name: string;
  email: string;
  onSubmit: (data: UserData) => void;
}

export function UserForm({ name, email, onSubmit }: UserFormProps) {
  const [formData, setFormData] = useState({ name, email });

  return (
    <form onSubmit={() => onSubmit(formData)}>
      <input value={formData.name} onChange={...} />
      <input value={formData.email} onChange={...} />
      <button type="submit">Submit</button>
    </form>
  );
}

// EXISTING: Test
it('should submit form data', async () => {
  const mockOnSubmit = jest.fn();
  render(
    <UserForm
      name="John"
      email="john@example.com"
      onSubmit={mockOnSubmit}
    />
  );

  const submitBtn = screen.getByRole('button');
  await userEvent.click(submitBtn);

  expect(mockOnSubmit).toHaveBeenCalledWith({
    name: 'John',
    email: 'john@example.com',
  });
});

// DANGEROUS: Add field without updating type
interface UserFormProps {
  name: string;
  email: string;
  phone?: string;  // NEW
  onSubmit: (data: UserData) => void;
}

export function UserForm({ name, email, phone, onSubmit }: UserFormProps) {
  const [formData, setFormData] = useState({ name, email, phone });  // CHANGED

  return (
    <form onSubmit={() => onSubmit(formData)}>
      {/* ... existing fields ... */}
      {phone && <input value={formData.phone} onChange={...} />}  // NEW
      <button type="submit">Submit</button>
    </form>
  );
}

// TEST BREAKS:
// ✗ expect(mockOnSubmit).toHaveBeenCalledWith(...)
// Expected: { name: 'John', email: 'john@example.com' }
// Received: { name: 'John', email: 'john@example.com', phone: undefined }

// SAFE: Update test to match new form structure
it('should submit form data', async () => {
  const mockOnSubmit = jest.fn();
  render(
    <UserForm
      name="John"
      email="john@example.com"
      phone="+1234567890"  // NEW
      onSubmit={mockOnSubmit}
    />
  );

  const submitBtn = screen.getByRole('button');
  await userEvent.click(submitBtn);

  expect(mockOnSubmit).toHaveBeenCalledWith({
    name: 'John',
    email: 'john@example.com',
    phone: '+1234567890',  // NEW
  });
});
```

### 6.2 Breaking Mock Data That Multiple Tests Depend On

**Scenario: API Response Shape Change**

```typescript
// EXISTING: Multiple tests rely on this shape
const mockUser = {
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
};

// mocks/handlers.ts
http.get('/api/users/:id', ({ params }) => {
  return HttpResponse.json(mockUser);
});

// Test 1: Checks name
it('should display user name', async () => {
  render(<UserProfile userId="1" />);
  expect(screen.getByText('John Doe')).toBeInTheDocument();
});

// Test 2: Checks email
it('should display user email', async () => {
  render(<UserProfile userId="1" />);
  expect(screen.getByText('john@example.com')).toBeInTheDocument();
});

// Test 3: Checks ID
it('should pass user ID to analytics', async () => {
  render(<UserProfile userId="1" />);
  expect(analytics.track).toHaveBeenCalledWith('user_viewed', { id: '1' });
});

// DANGEROUS: Remove email field from mock
const mockUser = {
  id: '1',
  name: 'John Doe',
  // email removed!
};

// BREAKS:
// ✗ Test 2 fails: text "john@example.com" not found
// ✗ Any code using user.email breaks
// ✗ Component might crash if it expects email

// SAFE: Add field, keep old fields
const mockUser = {
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',  // Keep
  phone: '+1234567890',        // Add new
  lastLogin: '2024-02-26',      // Add new
};

// All existing tests work ✓
// New code can use phone and lastLogin ✓
```

### 6.3 Changing Import Paths That Tests Reference

**Scenario: Moving Test Utilities**

```typescript
// EXISTING: 47 test files import from here
// src/testUtils.tsx
export function render(...) { ... }
export { screen } from '@testing-library/react';

// Test files:
import { render, screen } from '../testUtils';  // 47 files

// DANGEROUS: Move or rename testUtils
// src/test/utils.tsx  ← NEW LOCATION

// BREAKS:
// ✗ All 47 test files break
// Error: Cannot find module '../testUtils'
// Error: Cannot find module '../../testUtils'

// Must update all 47 imports:
// From: import { render, screen } from '../testUtils'
// To: import { render, screen } from '../test/utils'

// SAFER: Keep original file, re-export from new location
// src/testUtils.tsx (keep existing)
export { render, screen } from './test/utils';

// New code can use:
import { render, screen } from '../test/utils';

// Old code still works:
import { render, screen } from '../testUtils';

// Gradual migration possible ✓
```

### 6.4 Breaking Custom Test Utilities

**Scenario: Modifying Custom Render Function**

```typescript
// EXISTING: testUtils.tsx - used in 30+ tests
export function render(ui: ReactElement) {
  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <Provider store={store}>
        {children}
      </Provider>
    ),
  });
}

// Tests rely on Redux store being available:
it('should show user name from Redux', () => {
  render(<Dashboard />);  // Store is available
  expect(screen.getByText('John')).toBeInTheDocument();
});

// DANGEROUS: Remove store from wrapper
export function render(ui: ReactElement) {
  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <div>{children}</div>  // No Provider!
    ),
  });
}

// BREAKS:
// ✗ All 30+ tests fail with:
// Error: useSelector must be used within <Provider>
// ✗ Components expecting Redux state crash

// SAFE: Add option to disable provider if needed
export function render(
  ui: ReactElement,
  { withoutStore = false }: { withoutStore?: boolean } = {}
) {
  if (withoutStore) {
    return rtlRender(ui, { wrapper: ({ children }) => children });
  }

  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <Provider store={store}>
        {children}
      </Provider>
    ),
  });
}

// Existing tests work:
render(<Dashboard />);  // Has store ✓

// New tests can opt-out:
render(<Dashboard />, { withoutStore: true });  // No store ✓
```

---

## Part 7: Practical Detection and Analysis Tools

### 7.1 Test Framework Detection Script

```bash
#!/bin/bash
# detect-test-framework.sh

# Check package.json for test framework
echo "=== Checking Test Framework ==="
grep -E '"jest"|"vitest"|"playwright"|"cypress"' package.json

# Find test config files
echo -e "\n=== Test Config Files ==="
find . -maxdepth 1 -name "*jest.config*" -o -name "*vitest.config*" -o -name "*playwright.config*"

# Find setupTests files
echo -e "\n=== Setup Files ==="
find . -name "setupTests.*" -o -name "setup.ts" -o -name "setup.js"

# Count test files
echo -e "\n=== Test File Count ==="
echo "*.test.tsx: $(find . -name "*.test.tsx" | wc -l)"
echo "*.test.ts: $(find . -name "*.test.ts" | wc -l)"
echo "*.spec.tsx: $(find . -name "*.spec.tsx" | wc -l)"
echo "*.spec.ts: $(find . -name "*.spec.ts" | wc -l)"

# Find mock directories
echo -e "\n=== Mock Directories ==="
find . -type d -name "__mocks__" -o -type d -name "mocks"

# Show test command
echo -e "\n=== Test Commands ==="
grep '"test"' package.json
```

### 7.2 Test Pattern Analysis

```bash
#!/bin/bash
# analyze-test-patterns.sh

TEST_FILE=$1

echo "=== Test Structure ==="
grep -c "describe(" $TEST_FILE
grep -c "it(" $TEST_FILE

echo -e "\n=== Assertion Matchers Used ==="
grep -o "expect.*toBe\|expect.*toHave\|expect.*toContain" $TEST_FILE | sort -u

echo -e "\n=== Mock Patterns ==="
grep -c "jest.fn()" $TEST_FILE
grep -c "mockResolvedValue\|mockRejectedValue" $TEST_FILE

echo -e "\n=== Async Patterns ==="
grep -c "async\|await\|waitFor" $TEST_FILE

echo -e "\n=== Import Sources ==="
grep "^import.*from" $TEST_FILE | grep -o "from '[^']*'" | sort -u
```

### 7.3 Test Coverage Gap Detection

```bash
#!/bin/bash
# detect-coverage-gaps.sh

npm test -- --coverage 2>&1 | {
  echo "=== Files Below 70% Coverage ==="
  awk '$2 < 70 && $1 != "All" {print $1, $2"%"}'

  echo -e "\n=== Files with 0% Coverage ==="
  awk '$2 == 0 {print $1}'
}
```

---

## Part 8: Quick Reference Checklist

### Before Any Test Modification

**Pre-Modification Checklist**

- [ ] Run `npm test` - establish baseline
- [ ] Run `npm test -- --coverage` - document coverage
- [ ] Grep for all test files using the component
  ```bash
  grep -r "Component" --include="*.test.tsx"
  ```
- [ ] List all existing tests for the component
  ```bash
  grep "it(" Component.test.tsx
  ```
- [ ] Check for snapshots
  ```bash
  grep "toMatchSnapshot\|toMatchInlineSnapshot" Component.test.tsx
  ```

### When Adding New Tests

**New Test Checklist**

- [ ] Match file naming convention (`.test.tsx` vs `.spec.ts`)
- [ ] Place in same directory structure as existing tests
- [ ] Import from same test utilities source
- [ ] Use same assertion style (`expect().toBe` vs other)
- [ ] Follow ARRANGE-ACT-ASSERT comment structure
- [ ] Use same mock pattern (MSW, jest.fn(), etc.)
- [ ] Test both success and error cases
- [ ] Run full test suite after adding
- [ ] Verify test output shows new tests passing

### When Modifying Tested Components

**Modification Checklist**

- [ ] Identify all tests for the component
- [ ] Run existing tests before modification
- [ ] Make changes incrementally
- [ ] Run tests after each change
- [ ] Update tests to match new behavior
- [ ] Update snapshots if visual changes intentional
- [ ] Verify all tests pass
- [ ] Run full suite before committing

### When Modifying Test Infrastructure

**Infrastructure Modification Checklist**

- [ ] Count files affected (grep usage count)
- [ ] Run all tests to establish baseline
- [ ] Make minimal changes
- [ ] Consider backward compatibility
- [ ] Update all affected files
- [ ] Run full suite
- [ ] Document changes
- [ ] Commit atomically with affected tests

---

## Sources and References

This reference guide synthesizes best practices from:

- [How to Test TypeScript Code: Jest, Vitest & Best Practices Guide](https://reintech.io/blog/how-to-test-typescript-code-jest-vitest-best-practices)
- [Vitest in 2026: The New Standard for Modern JavaScript Testing](https://jeffbruchado.com.br/en/blog/vitest-2026-standard-modern-javascript-testing)
- [Mock Service Worker](https://mswjs.io/)
- [How to Mock API Calls in React Tests with MSW](https://oneuptime.com/blog/post/2026-01-15-mock-api-calls-react-msw/view)
- [Testing Library Patterns and Best Practices](https://testing-library.com/docs/react-testing-library/example-intro/)
- [React Testing Library Documentation](https://testing-library.com/)
- [Jest Testing Framework](https://jestjs.io/)
- [Vitest Documentation](https://vitest.dev/)
- [A systematic literature review of test breakage prevention and repair techniques](https://www.sciencedirect.com/science/article/abs/pii/S0950584919300990)
- [Snapshot Testing – Capturing Your Code's Best Side](https://infinum.com/blog/snapshot-testing/)
- [Jest vs Vitest: Which Test Runner Should You Use in 2025](https://medium.com/@ruverd/jest-vs-vitest-which-test-runner-should-you-use-in-2025-5c85e4f2bda9)
- [10 Jest/Vitest Patterns That Reduce Flaky Tests](https://medium.com/@Modexa/10-jest-vitest-patterns-that-reduce-flaky-tests-4105009ead56)

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial comprehensive reference for testing pattern preservation |

---

**Last Updated:** February 26, 2026
**For:** workflow-guardian skill - Test Infrastructure Preservation
**Audience:** Claude Code developers adding features to tested applications
