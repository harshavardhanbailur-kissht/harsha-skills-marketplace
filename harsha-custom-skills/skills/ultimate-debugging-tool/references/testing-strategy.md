# Testing Strategies for Bug Prevention

Testing strategies that prevent bugs during and after fixing:

## 1. Regression Test Protocol

The regression test protocol ensures that bugs are properly verified as fixed and don't resurface.

**Before Fixing**: Write a test that FAILS (proves bug exists)
```javascript
describe('BUG-123: dropdown closes unexpectedly on blur', () => {
  it('should keep dropdown open when clicking inside dropdown content', async () => {
    render(<Dropdown />);
    const trigger = screen.getByRole('button', { name: /open menu/i });

    await userEvent.click(trigger);
    expect(screen.getByRole('menu')).toBeInTheDocument();

    const menuItem = screen.getByRole('menuitem', { name: /option a/i });
    await userEvent.click(menuItem);

    // This test FAILS before fix
    expect(screen.getByRole('menu')).toBeInTheDocument();
  });
});
```

**After Fixing**: Run the test (proves fix works)
- Test naming: `describe('BUG-XXX: description', () => { ... })`
- Include edge cases discovered during debugging
- Add performance assertions where relevant

```javascript
describe('BUG-123: dropdown closes unexpectedly on blur', () => {
  it('should keep dropdown open when clicking inside dropdown content', async () => {
    render(<Dropdown />);
    const trigger = screen.getByRole('button', { name: /open menu/i });

    await userEvent.click(trigger);
    expect(screen.getByRole('menu')).toBeInTheDocument();

    const menuItem = screen.getByRole('menuitem', { name: /option a/i });
    await userEvent.click(menuItem);

    expect(screen.getByRole('menu')).toBeInTheDocument();
  });

  it('should close dropdown when clicking outside', async () => {
    render(
      <div>
        <Dropdown />
        <button>Outside Button</button>
      </div>
    );

    await userEvent.click(screen.getByRole('button', { name: /open menu/i }));
    await userEvent.click(screen.getByText('Outside Button'));

    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('should open and close within 300ms', async () => {
    const { rerender } = render(<Dropdown />);
    const start = performance.now();

    await userEvent.click(screen.getByRole('button', { name: /open menu/i }));
    await userEvent.click(screen.getByRole('menuitem'));

    const duration = performance.now() - start;
    expect(duration).toBeLessThan(300);
  });
});
```

## 2. Testing Pyramid for Web Apps

A structured approach to testing at different levels of abstraction.

### Unit Tests (Vitest/Jest)
Test individual functions, hooks, utilities in isolation.

```javascript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 80,
      functions: 80,
      branches: 75,
      statements: 80,
    },
  },
});

// utils/calculations.test.ts
import { describe, it, expect } from 'vitest';
import { calculateDiscount, formatPrice } from './calculations';

describe('calculateDiscount', () => {
  it('applies percentage discount correctly', () => {
    expect(calculateDiscount(100, 10)).toBe(90);
  });

  it('handles zero discount', () => {
    expect(calculateDiscount(100, 0)).toBe(100);
  });

  it('handles 100% discount', () => {
    expect(calculateDiscount(100, 100)).toBe(0);
  });

  it('throws on negative discount', () => {
    expect(() => calculateDiscount(100, -10)).toThrow();
  });
});
```

### Component Tests (React Testing Library)
Test component behavior, not implementation details.

```javascript
// components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button Component', () => {
  it('calls onClick handler when clicked', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Click Me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('shows loading state', () => {
    render(<Button loading>Loading...</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
  });
});
```

### Integration Tests (Testing Library + MSW)
Test components with mocked API calls.

```javascript
// api/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'John Doe',
      email: 'john@example.com',
    });
  }),
];

// setupTests.ts
import { setupServer } from 'msw/node';
import { handlers } from './api/mocks/handlers';

export const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// components/UserProfile.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile Integration', () => {
  it('fetches and displays user data', async () => {
    render(<UserProfile userId="123" />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    server.use(
      http.get('/api/users/:id', () => {
        return HttpResponse.json(
          { error: 'Not found' },
          { status: 404 }
        );
      })
    );

    render(<UserProfile userId="999" />);

    await waitFor(() => {
      expect(screen.getByText(/user not found/i)).toBeInTheDocument();
    });
  });
});
```

### E2E Tests (Playwright)
Test full user flows across the application.

```javascript
// tests/checkout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test('should complete purchase successfully', async ({ page }) => {
    await page.goto('http://localhost:3000/products');

    await page.click('button:has-text("Add to Cart")');
    await page.click('a:has-text("Cart")');

    expect(page.url()).toContain('/cart');
    expect(await page.locator('[data-testid="item-count"]')).toContainText('1');

    await page.click('button:has-text("Proceed to Checkout")');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="card"]', '4111111111111111');

    await page.click('button:has-text("Complete Purchase")');

    await expect(page.locator('text=Order Confirmed')).toBeVisible();
  });

  test('should persist cart on page reload', async ({ page }) => {
    await page.goto('http://localhost:3000/products');
    await page.click('button:has-text("Add to Cart")');

    await page.reload();

    const cartCount = await page.locator('[data-testid="item-count"]').textContent();
    expect(cartCount).toBe('1');
  });
});
```

### Visual Regression Tests (Chromatic/Percy)
Catch unintended visual changes automatically.

```javascript
// tests/visual.spec.ts
import { test, expect } from '@playwright/test';

test('Button component should match snapshot', async ({ page }) => {
  await page.goto('http://localhost:3000/components/button');

  const button = page.locator('button').first();
  await expect(button).toHaveScreenshot('button.png');
});

test('Modal should match snapshot when open', async ({ page }) => {
  await page.goto('http://localhost:3000/modals');
  await page.click('button:has-text("Open Modal")');

  const modal = page.locator('[role="dialog"]');
  await expect(modal).toHaveScreenshot('modal-open.png');
});
```

### Performance Tests (Lighthouse CI)
Catch performance regressions in CI.

```yaml
# lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000"],
      "numberOfRuns": 3,
      "settings": {
        "configPath": "./lighthouse-config.js"
      }
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

## 3. React-Specific Testing Patterns

### Testing Custom Hooks
```javascript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('increments counter', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('decrements counter', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(-1);
  });
});
```

### Testing Suspense Boundaries
```javascript
describe('Suspense Integration', () => {
  it('shows fallback while loading', async () => {
    render(
      <Suspense fallback={<div>Loading...</div>}>
        <AsyncComponent />
      </Suspense>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
  });
});
```

### Testing Error Boundaries
```javascript
describe('Error Boundary', () => {
  it('catches errors and displays fallback', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });
});
```

### Testing Context Consumers
```javascript
const TestProvider = ({ children }) => (
  <ThemeContext.Provider value={{ theme: 'dark' }}>
    {children}
  </ThemeContext.Provider>
);

describe('Theme Context', () => {
  it('provides theme to consumers', () => {
    render(
      <TestProvider>
        <ThemedComponent />
      </TestProvider>
    );

    expect(screen.getByTestId('theme-display')).toHaveTextContent('dark');
  });
});
```

### Mocking Modules
```javascript
// api/client.ts
export const fetchUser = async (id: string) => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};

// component.test.ts
import { vi } from 'vitest';
import * as apiClient from '../api/client';

vi.mock('../api/client', () => ({
  fetchUser: vi.fn(),
}));

describe('Component with API', () => {
  it('displays user data from API', async () => {
    vi.mocked(apiClient.fetchUser).mockResolvedValueOnce({
      id: '1',
      name: 'John Doe',
    });

    render(<UserComponent userId="1" />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });
});
```

## 4. Three.js Testing

### Unit Test Utilities
```javascript
import { describe, it, expect } from 'vitest';
import { generateGeometry, calculateBoundingBox } from './geometry-utils';
import * as THREE from 'three';

describe('Geometry Utilities', () => {
  it('generates correct box geometry', () => {
    const geo = generateGeometry('box', { width: 1, height: 1, depth: 1 });

    expect(geo).toBeInstanceOf(THREE.BoxGeometry);
    expect(geo.parameters.width).toBe(1);
  });

  it('calculates bounding box correctly', () => {
    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const box = calculateBoundingBox(geometry);

    expect(box.getSize(new THREE.Vector3()).length()).toBeCloseTo(Math.sqrt(12), 1);
  });
});
```

### Snapshot Testing Scene Setup
```javascript
describe('Scene Setup', () => {
  it('creates scene with correct components', () => {
    const scene = createScene();

    expect(scene.children.length).toBe(3); // camera, lights, geometry
    expect(scene.children[1]).toBeInstanceOf(THREE.Light);
  });
});
```

### Memory Leak Testing
```javascript
describe('Memory Management', () => {
  it('does not leak memory on component unmount', () => {
    const initialHeap = performance.memory.usedJSHeapSize;

    const { unmount } = render(<ThreeScene />);
    unmount();

    // Force garbage collection (requires --expose-gc flag)
    if (global.gc) global.gc();

    const finalHeap = performance.memory.usedJSHeapSize;
    const leakage = finalHeap - initialHeap;

    expect(leakage).toBeLessThan(5000000); // Less than 5MB leak
  });
});
```

## 5. Animation Testing

### GSAP Testing
Test final state, not animation progress.

```javascript
describe('GSAP Animation', () => {
  it('animates element to final position', async () => {
    const element = document.createElement('div');
    element.style.left = '0px';
    document.body.appendChild(element);

    gsap.to(element, { duration: 0.5, left: '100px' });

    await new Promise(resolve => setTimeout(resolve, 600));

    expect(element.style.left).toBe('100px');

    document.body.removeChild(element);
  });
});
```

### Framer Motion Testing
Test presence/absence after animation completes.

```javascript
describe('Framer Motion', () => {
  it('animates in and out correctly', async () => {
    const { rerender } = render(
      <motion.div animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
        Content
      </motion.div>
    );

    await waitFor(() => {
      const element = screen.getByText('Content');
      expect(element).toHaveStyle('opacity: 1');
    });

    rerender(<></>);

    await waitFor(() => {
      expect(screen.queryByText('Content')).not.toBeInTheDocument();
    }, { timeout: 1000 });
  });
});
```

### CSS Animation Testing
Test computed styles after transition completes.

```javascript
describe('CSS Animations', () => {
  it('applies transition styles', async () => {
    const { container } = render(
      <div className="box" style={{ transition: 'all 0.3s' }} />
    );

    const box = container.querySelector('.box') as HTMLElement;
    box.style.backgroundColor = 'red';

    await new Promise(resolve => setTimeout(resolve, 350));

    expect(getComputedStyle(box).backgroundColor).toBe('rgb(255, 0, 0)');
  });
});
```

## 6. Property-Based Testing

Use the fast-check library for generating random inputs.

```javascript
import fc from 'fast-check';
import { validateEmail, parseJSON, normalizeURL } from './validators';

describe('Email Validator (Property-Based)', () => {
  it('should accept any valid email', () => {
    fc.assert(
      fc.property(fc.emailAddress(), (email) => {
        expect(validateEmail(email)).toBe(true);
      })
    );
  });

  it('should reject emails without @', () => {
    fc.assert(
      fc.property(fc.string().filter(s => !s.includes('@')), (notEmail) => {
        expect(validateEmail(notEmail)).toBe(false);
      })
    );
  });
});

describe('JSON Parser (Property-Based)', () => {
  it('should parse valid JSON objects', () => {
    fc.assert(
      fc.property(fc.object(), (obj) => {
        const json = JSON.stringify(obj);
        expect(parseJSON(json)).toEqual(obj);
      })
    );
  });

  it('should reject invalid JSON gracefully', () => {
    fc.assert(
      fc.property(fc.string(), (str) => {
        if (!isValidJSON(str)) {
          expect(() => parseJSON(str)).not.toThrow();
        }
      })
    );
  });
});

describe('URL Normalizer (Property-Based)', () => {
  it('should normalize URLs consistently', () => {
    fc.assert(
      fc.property(fc.webUrl(), (url) => {
        const normalized1 = normalizeURL(url);
        const normalized2 = normalizeURL(url);
        expect(normalized1).toBe(normalized2);
      })
    );
  });

  it('should handle various URL formats', () => {
    fc.assert(
      fc.property(
        fc.tuple(
          fc.constantFrom('http', 'https'),
          fc.domain(),
          fc.integer(0, 65535)
        ),
        ([protocol, domain, port]) => {
          const url = `${protocol}://${domain}:${port}`;
          expect(() => normalizeURL(url)).not.toThrow();
        }
      )
    );
  });
});
```

## Testing Best Practices Summary

- Write failing tests before fixing bugs
- Organize tests using the pyramid: unit → component → integration → E2E
- Test behavior, not implementation
- Use meaningful test names that describe expected outcomes
- Keep tests isolated and independent
- Mock external dependencies (APIs, timers, DOM)
- Maintain test coverage above 80%
- Run tests in CI/CD pipeline on every commit
- Use property-based testing for complex validation logic
- Profile tests regularly to prevent slowdowns
