# React 19+ Bug Patterns

**Versions Covered:** React 19.0+ through 19.2.4 (validated April 2, 2026)

### R-001: Stale Closure in useEffect

**Symptom:** Event handler uses old state value; clicking button shows stale data from first render

**Root Cause:** Closure captures variable at creation time. Dependency array missing the variable, so handler never updates.

**Detection:**
```typescript
// BUGGY - handler always uses initial count
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const handler = () => console.log(count); // count is "0" always
    button.addEventListener('click', handler);
  }, []); // Missing count dependency
}
```

**Safe Fix:**
```typescript
// Option 1: Add to dependency array
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const handler = () => console.log(count);
    button.addEventListener('click', handler);
    return () => button.removeEventListener('click', handler);
  }, [count]); // Include in deps
}

// Option 2: Use useRef for latest value
function Counter() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);

  useEffect(() => {
    countRef.current = count;
  }, [count]);

  useEffect(() => {
    const handler = () => console.log(countRef.current); // Always latest
    button.addEventListener('click', handler);
    return () => button.removeEventListener('click', handler);
  }, []); // No re-attach needed
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Silencing the linter hides real bugs
useEffect(() => {
  const handler = () => console.log(count);
  button.addEventListener('click', handler);
}, []); // eslint-disable-next-line react-hooks/exhaustive-deps
```

**Regression Test:**
```typescript
describe('R-001: Stale Closure', () => {
  it('should log current count, not initial', async () => {
    const logs: number[] = [];
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(v => logs.push(v));

    const { rerender } = render(<Counter />);
    fireEvent.click(screen.getByRole('button', { name: 'Increment' }));
    fireEvent.click(screen.getByRole('button', { name: 'Log Count' }));

    expect(logs[logs.length - 1]).toBe(1); // Not 0
    consoleSpy.mockRestore();
  });
});
```

---

### R-002: Missing useEffect Cleanup

**Symptom:** Memory leak warning "setState called on unmounted component"; memory grows over time; stale subscriptions

**Root Cause:** Async operation (fetch, subscription, timer) completes after component unmounts. Component tries to update state that no longer exists.

**Detection:**
```typescript
// BUGGY - no cleanup
function Profile({ userId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/user/${userId}`)
      .then(res => res.json())
      .then(data => setData(data)); // Can fire after unmount
  }, [userId]);
}
```

**Safe Fix (AbortController Pattern):**
```typescript
function Profile({ userId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch(`/api/user/${userId}`, { signal: controller.signal })
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err);
        }
      });

    // Cleanup: abort fetch on unmount or userId change
    return () => controller.abort();
  }, [userId]);

  return data ? <div>{data.name}</div> : error ? <div>Error</div> : <div>Loading...</div>;
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Boolean flag without actually aborting
function Profile({ userId }) {
  const [data, setData] = useState(null);
  let isMounted = true;

  useEffect(() => {
    fetch(`/api/user/${userId}`)
      .then(res => res.json())
      .then(data => {
        if (isMounted) setData(data); // Doesn't prevent fetch
      });

    return () => { isMounted = false; }; // Fetch still completes
  }, [userId]);
}
```

**Regression Test:**
```typescript
describe('R-002: Missing Cleanup', () => {
  it('should abort fetch on unmount', async () => {
    const { unmount } = render(<Profile userId="123" />);
    unmount();

    // Verify fetch was aborted (no setState warning)
    await new Promise(resolve => setTimeout(resolve, 100));
    expect(console.error).not.toHaveBeenCalledWith(expect.stringContaining('setState on unmounted'));
  });
});
```

---

### R-003: Infinite Re-render Loop

**Symptom:** App freezes or crashes; console shows "Maximum update depth exceeded"

**Root Cause:** setState inside useEffect without proper dependency array, or object/array literal in deps creates new reference every render

**Detection:**
```typescript
// BUGGY - setState in effect with no deps
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(count + 1); // Triggers render -> effect -> setState loop
  }); // No deps array at all
}

// BUGGY - object literal in deps
function SearchPage({ query }) {
  const [results, setResults] = useState(null);

  const filters = { type: 'user' }; // New object every render

  useEffect(() => {
    fetchResults(query, filters);
  }, [query, filters]); // filters causes re-run every time
}
```

**Safe Fix:**
```typescript
// Option 1: Correct deps array
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setCount(count + 1), 1000);
    return () => clearTimeout(timer);
  }, [count]); // Proper dependency
}

// Option 2: Memoize objects in deps
function SearchPage({ query }) {
  const [results, setResults] = useState(null);

  const filters = useMemo(() => ({ type: 'user' }), []);

  useEffect(() => {
    fetchResults(query, filters);
  }, [query, filters]); // filters now stable
}

// Option 3: Use functional setState
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setCount(prevCount => prevCount + 1); // Doesn't depend on current count
  }, []); // No dependency needed
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Empty array masks the real problem
function SearchPage({ query }) {
  const [results, setResults] = useState(null);
  const filters = { type: 'user' }; // Still creates new object

  useEffect(() => {
    fetchResults(query, filters);
  }, []); // Hides bug; filters never updates
}
```

**Regression Test:**
```typescript
describe('R-003: Infinite Loop', () => {
  it('should not exceed update depth', () => {
    let renderCount = 0;
    const originalError = console.error;

    jest.spyOn(console, 'error').mockImplementation((msg) => {
      if (msg.includes('Maximum update depth')) renderCount++;
    });

    render(<Counter />);
    expect(renderCount).toBe(0);

    console.error = originalError;
  });
});
```

---

### R-004: Hydration Mismatch

**Symptom:** Content flickers on page load; console warning "Hydration failed because the initial UI does not match what was rendered on the server"

**Root Cause:** Server renders different content than client. Common causes: Date/timestamp, Math.random(), browser APIs (window, localStorage), timezone-dependent content

**Detection:**
```typescript
// BUGGY - renders different on server vs client
function Greeting() {
  const [time] = useState(new Date().toLocaleString()); // Different every render

  return <div>{time}</div>;
}

// BUGGY - Math.random() different
function RandomID() {
  return <div id={`id-${Math.random()}`}>Content</div>;
}
```

**Safe Fix:**
```typescript
// Option 1: useEffect for client-only content
function Greeting() {
  const [time, setTime] = useState('');

  useEffect(() => {
    setTime(new Date().toLocaleString()); // Only runs on client
  }, []);

  return <div>{time || 'Loading...'}</div>;
}

// Option 2: suppressHydrationWarning for intentional differences
function CurrentTime() {
  return (
    <div suppressHydrationWarning>
      {new Date().toLocaleString()}
    </div>
  );
}

// Option 3: Server render a placeholder
function RandomID() {
  const [id, setId] = useState('');

  useEffect(() => {
    setId(`id-${Math.random()}`);
  }, []);

  return <div id={id || 'temp-id'}>Content</div>;
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Suppress warning without understanding why
function RandomID() {
  return <div suppressHydrationWarning id={`id-${Math.random()}`}>Content</div>;
}
```

**Regression Test:**
```typescript
describe('R-004: Hydration Mismatch', () => {
  it('should not show hydration warning', () => {
    const errors: string[] = [];
    jest.spyOn(console, 'error').mockImplementation(msg => {
      if (msg.includes('Hydration')) errors.push(msg);
    });

    render(<Greeting />);
    expect(errors).toHaveLength(0);
  });
});
```

---

### R-005: Context Value Instability

**Symptom:** All consumers re-render on every parent render even though context value didn't change

**Root Cause:** Inline object created as context value. Creates new reference every render, causing all consumers to see "change"

**Detection:**
```typescript
// BUGGY - context value is new object every render
const ThemeContext = createContext(null);

function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(false);

  return (
    <ThemeContext.Provider value={{ isDark, setIsDark }}>
      {children}
    </ThemeContext.Provider>
  ); // New object every render -> all consumers update
}
```

**Safe Fix:**
```typescript
const ThemeContext = createContext(null);

function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(false);

  // Memoize context value
  const value = useMemo(() => ({ isDark, setIsDark }), [isDark]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  ); // Same object reference unless isDark changes
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Split context to "optimize" without memoizing
const ThemeDarkContext = createContext(false);
const ThemeSetterContext = createContext(null);

function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(false);

  return (
    <ThemeDarkContext.Provider value={isDark}>
      <ThemeSetterContext.Provider value={setIsDark}>
        {children}
      </ThemeSetterContext.Provider>
    </ThemeDarkContext.Provider>
  ); // Still re-renders when isDark changes (expected) but design fragile
}
```

**Regression Test:**
```typescript
describe('R-005: Context Value Instability', () => {
  it('should not re-render consumer when context value same', () => {
    let consumerRenders = 0;

    function Consumer() {
      useContext(ThemeContext);
      consumerRenders++;
      return null;
    }

    const { rerender } = render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>
    );

    expect(consumerRenders).toBe(1);
    rerender(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>
    );
    expect(consumerRenders).toBe(2); // Only 1 extra, not multiple
  });
});
```

---

### R-006: Server/Client Component Boundary Error

**Symptom:** Error "useState can only be used within the rendering of a client component" in Next.js App Router

**Root Cause:** Using hooks, browser APIs, or client-only code in Server Components

**Detection:**
```typescript
// BUGGY - Server Component with useState
export default function Page() {
  const [count, setCount] = useState(0);

  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**Safe Fix:**
```typescript
// Option 1: Mark as Client Component
'use client';

import { useState } from 'react';

export default function Page() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}

// Option 2: Keep Server Component, extract Client Component
// page.tsx (Server Component)
import Counter from '@/components/Counter';

export default function Page() {
  return (
    <div>
      <h1>My Page</h1>
      <Counter />
    </div>
  );
}

// components/Counter.tsx (Client Component)
'use client';

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Force everything to be client component
'use client';

export default function Page() {
  // This wastes benefits of Server Components
  const [count, setCount] = useState(0);
}
```

**Regression Test:**
```typescript
describe('R-006: Server/Client Boundary', () => {
  it('should render Client Component with useState', () => {
    render(<Counter />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});
```

---

### R-007: React Compiler Compatibility Issues

**Symptom:** Memoization not working as expected; unexpected re-renders with React Compiler enabled

**Root Cause:** Code patterns incompatible with automatic optimization. Mutations in render, reassignments, or complex closures

**Detection:**
```typescript
// BUGGY - mutation in render
function Component({ users }) {
  const filtered = users;
  filtered.sort((a, b) => a.name.localeCompare(b.name)); // Mutates input

  return filtered.map(user => <div key={user.id}>{user.name}</div>);
}

// BUGGY - reassignment in render
function Counter() {
  let count = 0;
  count++; // Reassignment in render

  return <div>{count}</div>;
}
```

**Safe Fix:**
```typescript
// Option 1: Don't mutate, create new array
function Component({ users }) {
  const filtered = [...users].sort((a, b) =>
    a.name.localeCompare(b.name)
  );

  return filtered.map(user => <div key={user.id}>{user.name}</div>);
}

// Option 2: Use useState for mutable state
function Counter() {
  const [count, setCount] = useState(0);

  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}

// Option 3: Use useMemo for expensive calculations
function Component({ users }) {
  const filtered = useMemo(
    () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
    [users]
  );

  return filtered.map(user => <div key={user.id}>{user.name}</div>);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Try to fool the compiler with comments
function Component({ users }) {
  // @react-compiler-ignore-next-line
  users.sort((a, b) => a.name.localeCompare(b.name));

  return users.map(user => <div key={user.id}>{user.name}</div>);
}
```

**Regression Test:**
```typescript
describe('R-007: React Compiler', () => {
  it('should handle sorting without mutation', () => {
    const users = [
      { id: 1, name: 'Charlie' },
      { id: 2, name: 'Alice' },
      { id: 3, name: 'Bob' }
    ];

    const { container } = render(<Component users={users} />);
    const names = Array.from(container.querySelectorAll('div')).map(el => el.textContent);

    expect(names).toEqual(['Alice', 'Bob', 'Charlie']);
    expect(users[0].name).toBe('Charlie'); // Original unchanged
  });
});
```

---

### R-008: Suspense Boundary Error Handling

**Symptom:** Error thrown in suspended component crashes entire page; no error fallback shown

**Root Cause:** Suspense without ErrorBoundary. Error thrown in suspended component has nowhere to be caught

**Detection:**
```typescript
// BUGGY - Suspense without ErrorBoundary
function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AsyncComponent />
    </Suspense>
  );
}
```

**Safe Fix:**
```typescript
function Page() {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <Suspense fallback={<div>Loading...</div>}>
        <AsyncComponent />
      </Suspense>
    </ErrorBoundary>
  );
}

// ErrorBoundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('Error caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Use try-catch for async errors (doesn't work)
function Page() {
  try {
    return (
      <Suspense fallback={<div>Loading...</div>}>
        <AsyncComponent />
      </Suspense>
    );
  } catch (e) {
    // Won't catch errors from suspended components
    return <div>Error</div>;
  }
}
```

**Regression Test:**
```typescript
describe('R-008: Suspense Error Handling', () => {
  it('should show error fallback on error', async () => {
    const ErrorComponent = () => {
      throw new Error('Component failed');
    };

    render(
      <ErrorBoundary fallback={<div>Error caught</div>}>
        <Suspense fallback={<div>Loading</div>}>
          <ErrorComponent />
        </Suspense>
      </ErrorBoundary>
    );

    expect(screen.getByText('Error caught')).toBeInTheDocument();
  });
});
```

---
