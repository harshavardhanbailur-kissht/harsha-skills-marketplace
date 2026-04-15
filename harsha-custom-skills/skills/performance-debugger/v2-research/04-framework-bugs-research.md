# Framework Bug Patterns Research: React 19+, Next.js 15+, Three.js, GSAP, TypeScript (2025-2026)

> Comprehensive research on the most common and subtle bug patterns across modern web frameworks, with specific code examples and fixes.

---

## Table of Contents

1. [React 19+ Bugs (2025-2026)](#react-19-bugs-2025-2026)
2. [Next.js 15+ Bugs](#nextjs-15-bugs)
3. [Three.js Memory & Resource Bugs](#threejs-memory--resource-bugs)
4. [GSAP + Animation Bugs](#gsap--animation-bugs)
5. [TypeScript Bug Prevention](#typescript-bug-prevention)

---

## React 19+ Bugs (2025-2026)

### 1. React Server Components: Remote Code Execution & Deserialization Attacks

#### Context
React 19 introduced critical security vulnerabilities related to React Server Components (RSC) deserialization. The most severe issue, CVE-2025-55182 (CVSS 10.0), allows unauthenticated remote code execution.

#### Symptoms
- Server crashes or unexpected behavior when processing RSC requests
- POST requests to Server Function endpoints causing server hangs
- Undefined code execution with attacker-controlled payloads
- Application appears to hang or becomes unresponsive

#### Root Cause
React's payload decoder unsafely deserializes HTTP request bodies sent to React Server Function endpoints without proper validation. An attacker can craft malicious payloads that exploit unsafe deserialization patterns, triggering RCE or DoS conditions.

#### Detection
- Monitor for unusual POST requests to Server Function endpoints
- Check React/Next.js versions in production
- Review error logs for deserialization-related crashes
- Use vulnerability scanners to detect CVE-2025-55182, CVE-2025-55184, CVE-2025-55183, CVE-2025-67779

#### Safe Fix
Upgrade immediately to patched versions:
- React: 19.0.3, 19.1.4, 19.2.3+
- Next.js: 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7+

```bash
# Check current versions
npm list react react-dom react-server-dom-webpack

# Upgrade to safe versions
npm install react@19.2.3 react-dom@19.2.3 react-server-dom-webpack@19.2.3
```

#### Regression Test
```typescript
// src/__tests__/rsc-security.test.ts
import { test, expect } from '@playwright/test';

test('RSC payload validation rejects malicious payloads', async ({ page }) => {
  const maliciousPayload = JSON.stringify({
    // Constructor exploit attempt
    __type: 'function',
    code: 'require("child_process").exec("rm -rf /")'
  });

  const response = await page.request.post('/api/server-function', {
    data: maliciousPayload,
    headers: { 'Content-Type': 'application/json' }
  });

  // Should reject with 400/500, NOT execute
  expect([400, 500]).toContain(response.status());
  expect(response.status()).not.toBe(200);
});
```

---

### 2. useEffect Cleanup Race Conditions

#### Symptoms
- Stale data displayed after rapid state changes
- Network requests completing out of order
- State updates from cancelled operations
- "Can't perform a React state update on an unmounted component" warnings
- Data flickering between old and new values

#### Root Cause
When dependencies change rapidly, the previous effect hasn't cleaned up before the new effect runs. If async operations (fetch, timeouts) complete in reverse order, stale responses overwrite fresh data. Multiple network requests may resolve out-of-order.

#### Detection
- Console warnings about state updates on unmounted components
- Data flickering in rapid state transitions (search results, filters)
- Check for missing cleanup functions in useEffect
- ESLint rule: exhaustive-deps violations

#### Safe Fix - AbortController Pattern (Recommended for 2025)
```typescript
// PROBLEMATIC: Race conditions possible
function SearchResults({ query }: { query: string }) {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    // Problem: No way to cancel this fetch
    fetch(`/api/search?q=${query}`)
      .then(res => res.json())
      .then(data => setResults(data));
    // Missing cleanup - stale data race condition
  }, [query]);

  return <div>{results.map(r => r.title)}</div>;
}

// SAFE: AbortController prevents stale updates
function SearchResults({ query }: { query: string }) {
  const [results, setResults] = useState<any[]>([]);

  useEffect(() => {
    const controller = new AbortController();

    fetch(`/api/search?q=${query}`, {
      signal: controller.signal
    })
      .then(res => res.json())
      .then(data => {
        // This won't execute if the effect was cleaned up
        setResults(data);
      })
      .catch(err => {
        // AbortError is thrown when cleanup runs
        if (err.name !== 'AbortError') {
          console.error('Actual fetch error:', err);
        }
      });

    // Cleanup: Cancel the fetch if effect re-runs or component unmounts
    return () => controller.abort();
  }, [query]);

  return <div>{results.map(r => r.title)}</div>;
}
```

#### Safe Fix - Boolean Flag Pattern (for non-abort scenarios)
```typescript
// When AbortController isn't suitable
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let isMounted = true; // Flag to track cleanup

    async function fetchUser() {
      const data = await api.getUser(userId);

      // Only update state if component is still mounted
      if (isMounted) {
        setUser(data);
      }
    }

    fetchUser();

    // Cleanup: Mark as unmounted
    return () => {
      isMounted = false;
    };
  }, [userId]);

  return <div>{user?.name}</div>;
}
```

#### Regression Test
```typescript
// src/__tests__/useEffect-race-conditions.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';

test('useEffect cleanup prevents stale data from earlier requests', async () => {
  // Mock fetch to return in reverse order
  let resolveFirst: (value: any) => void = () => {};
  let resolveSecond: (value: any) => void = () => {};

  global.fetch = vi.fn()
    .mockImplementationOnce(() => new Promise(resolve => { resolveFirst = resolve; }))
    .mockImplementationOnce(() => new Promise(resolve => { resolveSecond = resolve; }));

  const { rerender } = render(<SearchResults query="first" />);

  // Second query starts
  rerender(<SearchResults query="second" />);

  // Second request resolves first (wrong order)
  resolveSecond({ data: [{ title: 'second result' }] });

  // First request resolves last
  resolveFirst({ data: [{ title: 'first result' }] });

  // Should show 'second result', NOT 'first result' (older stale data)
  await waitFor(() => {
    expect(screen.getByText('second result')).toBeInTheDocument();
  });
});
```

---

### 3. React Compiler (React Forget) Compatibility Gotchas

#### Symptoms
- Unexpected re-renders despite memoization being enabled
- Library functions breaking under React Compiler
- useWatch, getValues from react-hook-form returning stale values
- Props and state not updating correctly in optimized components
- Over-zealous memoization causing bugs in subtle ways

#### Root Cause
React Compiler v1.0 (stable October 2025) automatically memoizes components and values to optimize re-renders. However:
1. Library code may not be compatible with automatic memoization
2. Violations of Rules of React that aren't statically detected can cause memoization bugs
3. Memoization aggressiveness differs from manual React.memo/useMemo patterns

#### Detection
```bash
# Run the health check tool
npx react-compiler-healthcheck

# Look for:
# - "Compilation errors" in the report
# - "Memoization skipped due to rules violations"
# - Libraries in incompatibility list
```

Use React DevTools to verify actual memoization vs expected behavior.

#### Safe Fix - Gradual Adoption with Compatibility Checks
```typescript
// tsconfig.json - Enable compiler incrementally
{
  "compilerOptions": {
    // ... other options
  },
  "react-compiler": {
    "compilationMode": "strict", // or "strict-with-warnings"
    "targets": [
      "src/safe-components/**", // Start with safe areas only
      "!src/integrations/**"     // Exclude known incompatible libraries
    ],
    "runtimeModuleNamespace": "React"
  }
}

// vite.config.ts - If using Vite
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [
          ['babel-plugin-react-compiler', {
            target: '19', // React 19+
            runtimeModuleNamespace: 'React'
          }]
        ]
      }
    })
  ]
});
```

#### Safe Fix - Explicitly Opt-Out When Necessary
```typescript
// components/UserForm.tsx
// @skip-react-compiler - Don't compile this file
import { useForm } from 'react-hook-form';

export function UserForm() {
  const { useWatch, getValues } = useForm();
  // This works because the file is not compiled
  const watchedValue = useWatch({ name: 'email' });
  return <input value={watchedValue} />;
}

// Or for specific functions:
// @skip-react-compiler
function validateForm(formData: FormData) {
  // Complex validation logic that might break under memoization
  return formData.entries().every(([key, value]) => {
    return customValidators[key]?.(value);
  });
}
```

#### Regression Test
```typescript
// src/__tests__/react-compiler-compat.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('React Compiler preserves library behavior (react-hook-form)', async () => {
  function Form() {
    const { register, watch } = useForm();
    const watchedEmail = watch('email');

    return (
      <>
        <input {...register('email')} />
        <div>Email: {watchedEmail}</div>
      </>
    );
  }

  render(<Form />);

  const input = screen.getByRole('textbox');
  await userEvent.type(input, 'test@example.com');

  // Must update immediately, not lag or stale
  expect(screen.getByText(/Email: test@example.com/)).toBeInTheDocument();
});
```

---

### 4. Hydration Mismatch Patterns

#### Symptoms
- React hydration warnings/errors in console
- Flashing of different content during page load
- Browser extension attributes appear/disappear (cz-shortcut-listen="true")
- Server renders one thing, client renders another
- Build ID mismatches or chunk loading issues

#### Root Cause
Server-rendered HTML doesn't match client-rendered output. Common causes:
1. Browser-only APIs used during SSR (window, document, localStorage)
2. Random values or UUIDs generating different IDs on server vs client
3. Date/time dependent rendering
4. Responsive design breakpoints different on server
5. Extensions injecting attributes into DOM
6. Auth state mismatches between server and client

#### Detection
```typescript
// Check for hydration-prone patterns in components
// Look for these anti-patterns:
- Using Math.random() during render
- Generating UUIDs without keys
- Accessing window/document at render time
- Server and client having different auth state
- Conditional rendering based on screen size without hydration safety
```

#### Safe Fix - Move Sensitive Logic to useEffect
```typescript
// PROBLEMATIC: Hydration mismatch
function RandomComponent() {
  // This generates different values on server vs client
  const randomId = Math.random().toString(36);

  return <div id={randomId}>Content</div>;
}

// SAFE: Generate on client only
function RandomComponent() {
  const [randomId, setRandomId] = useState<string>('');

  useEffect(() => {
    // This runs only on client, after hydration
    setRandomId(Math.random().toString(36));
  }, []);

  // Avoid hydration mismatch by suppressing warning on first render
  return <div id={randomId || 'placeholder'}>Content</div>;
}

// Alternative: Use useId() hook (React 18+)
function RandomComponent() {
  const id = useId(); // Generates consistent, unique IDs
  return <div id={id}>Content</div>;
}
```

#### Safe Fix - useSyncExternalStore Pattern (For Browser API Dependencies)
```typescript
// Store that syncs with browser APIs
function useClientOnly<T>(selector: () => T, serverValue: T) {
  return useSyncExternalStore(
    () => {
      // On client: subscribe to changes
      const handleChange = () => callback?.();
      window.addEventListener('resize', handleChange);
      return () => window.removeEventListener('resize', handleChange);
    },
    () => {
      // On client: get current value from browser
      return selector();
    },
    () => {
      // During hydration: use server value
      return serverValue;
    }
  );
}

function ResponsiveComponent() {
  // Server renders with 'mobile', client updates to actual size
  const isMobile = useClientOnly(
    () => window.innerWidth < 640,
    true // server default
  );

  return <div>{isMobile ? 'Mobile' : 'Desktop'}</div>;
}
```

#### Safe Fix - Suppress Hydration Warning (Last Resort)
```typescript
// Only for known, safe mismatches
function TimeDisplay() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Suppress warning for initial render mismatch
  return (
    <time suppressHydrationWarning>
      {mounted ? new Date().toLocaleString() : 'loading...'}
    </time>
  );
}
```

#### Regression Test
```typescript
// src/__tests__/hydration-mismatch.test.tsx
import { renderToString } from 'react-dom/server';
import { render } from '@testing-library/react';
import { JSDOM } from 'jsdom';

test('component renders identically on server and client', () => {
  const serverHtml = renderToString(<MyComponent />);

  // Simulate client environment
  const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>');
  global.window = dom.window;
  global.document = dom.window.document;

  render(<MyComponent />, { hydrate: true });

  // Verify no hydration warnings (check console.error mock)
  expect(console.error).not.toHaveBeenCalledWith(
    expect.stringContaining('Hydration mismatch')
  );
});
```

---

### 5. Stale Closure Bugs with Modern Hooks Patterns

#### Symptoms
- Event handlers using outdated state/props
- Callbacks capturing old values in interval/timeout
- Event listeners from old renders staying active
- Dependencies listed in exhaustive-deps but behavior still wrong
- "useCallback Hell" - too many dependencies cause cascading re-renders

#### Root Cause
Closures capture variables at creation time. If you create a callback once on mount with `[] dependencies`, it closes over stale props/state forever. Modern hooks patterns (useCallback, useMemo) sometimes mask the real issue rather than fix it.

#### Detection
```typescript
// ESLint plugin catches most cases
// eslint-plugin-react-hooks/exhaustive-deps

// Manual detection: Use this pattern to identify stale closures
const staleClosureIndicators = [
  'Event handlers using props but created once',
  'setTimeout/setInterval closures over state',
  'Missing dependency list on useCallback/useMemo',
  'Dependencies that should update but don\'t'
];
```

#### Safe Fix - useEffectEvent (React 19.2+)
```typescript
// PROBLEMATIC: Stale closure pattern
function ChatRoom({ roomId, onMessage }) {
  const [message, setMessage] = useState('');

  // Stale closure: onMessage is captured at component creation
  // If parent updates onMessage, this handler still calls old version
  useEffect(() => {
    const handleNewMessage = (msg: string) => {
      onMessage(msg); // STALE: captures old onMessage
    };

    const connection = subscribe(roomId, handleNewMessage);
    return () => connection.unsubscribe();
  }, [roomId, onMessage]); // Adding onMessage here causes this effect to re-run every render!

  return (
    <>
      <input value={message} onChange={e => setMessage(e.target.value)} />
      <button onClick={() => onMessage(message)}>Send</button>
    </>
  );
}

// SAFE: useEffectEvent (available React 19.2+)
function ChatRoom({ roomId, onMessage }) {
  const [message, setMessage] = useState('');

  // Non-reactive effect event - always has latest onMessage
  const handleNewMessage = useEffectEvent((msg: string) => {
    onMessage(msg); // Always fresh, never stale
  });

  useEffect(() => {
    const connection = subscribe(roomId, handleNewMessage);
    return () => connection.unsubscribe();
  }, [roomId]); // handleNewMessage never changes, so roomId is only dep

  return (
    <>
      <input value={message} onChange={e => setMessage(e.target.value)} />
      <button onClick={() => handleNewMessage(message)}>Send</button>
    </>
  );
}
```

#### Safe Fix - useCallback with all dependencies (Pre-19.2)
```typescript
// Pre-useEffectEvent approach
function ChatRoom({ roomId, onMessage }) {
  const [message, setMessage] = useState('');

  // Create stable reference, but always calls latest onMessage
  const handleNewMessage = useCallback((msg: string) => {
    onMessage(msg);
  }, [onMessage]); // Include all deps - may cause re-runs but avoids stale closure

  useEffect(() => {
    const connection = subscribe(roomId, handleNewMessage);
    return () => connection.unsubscribe();
  }, [roomId, handleNewMessage]);

  return (
    <>
      <input value={message} onChange={e => setMessage(e.target.value)} />
      <button onClick={() => handleNewMessage(message)}>Send</button>
    </>
  );
}
```

#### Regression Test
```typescript
// src/__tests__/stale-closure.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('effect event always uses latest callback, not stale closure', async () => {
  const callbacks = { count: 1 };
  let capturedCallback: Function | null = null;

  function TestComponent({ onCallback }: { onCallback: (val: number) => void }) {
    const handleClick = useEffectEvent(() => {
      onCallback(callbacks.count);
    });

    capturedCallback = handleClick;
    return <button onClick={() => handleClick()}>Click</button>;
  }

  const onCallback = vi.fn();
  const { rerender } = render(<TestComponent onCallback={onCallback} />);

  // Change external state
  callbacks.count = 2;
  rerender(<TestComponent onCallback={onCallback} />);

  // Click should use new value, not stale
  await userEvent.click(screen.getByRole('button'));
  expect(onCallback).toHaveBeenCalledWith(2); // NOT 1 (stale)
});
```

---

## Next.js 15+ Bugs

### 1. App Router Cache Invalidation Failures

#### Symptoms
- Stale data persists after revalidation
- Some pages show old content while others show new
- Cache not clearing on demand with revalidateTag()
- Post updates don't reflect in lists immediately
- "404" errors after data deletion (file still cached)

#### Root Cause
Next.js 15 changed default cache behavior: pages are now **opt-out by default** (dynamic) instead of opt-in. Cache invalidation strategies that worked in v14 may not work in v15. Additionally:
1. revalidateTag() may not work if tags aren't properly set
2. Filesystem-based cache doesn't work in distributed environments
3. ISR (revalidate) timing conflicts with Server Components
4. Different cache strategies between server and client

#### Detection
```typescript
// Check for cache-related issues
const indicators = [
  'stale data after revalidation',
  'cache only works on Vercel, not self-hosted',
  'revalidatePath() doesn\'t work as expected',
  'tags in fetch don\'t match revalidateTag() calls'
];

// Check configuration
// next.config.js should have explicit cache settings
```

#### Safe Fix - Explicit Cache Configuration
```typescript
// PROBLEMATIC: Relying on defaults
// app/posts/[id]/page.tsx
export default async function PostPage({ params }) {
  const post = await fetch(`/api/posts/${params.id}`);
  // In Next.js 15, this might not be cached at all!
  return <div>{post.title}</div>;
}

// SAFE: Explicit cache configuration
// app/posts/[id]/page.tsx
export const revalidate = 3600; // ISR: revalidate every hour
// Or for dynamic rendering with revalidatePath:
// export const revalidate = 'force-dynamic';

export default async function PostPage({ params }) {
  const post = await fetch(
    `https://api.example.com/posts/${params.id}`,
    {
      next: {
        revalidate: 3600, // Cache for 1 hour
        tags: [`post-${params.id}`, 'posts'] // Tag for selective revalidation
      }
    }
  );

  return <div>{post.title}</div>;
}

// In Server Action or API route, trigger revalidation
// app/actions.ts
'use server';

export async function deletePost(id: string) {
  await db.posts.delete(id);

  // Revalidate specific post and the list
  revalidateTag(`post-${id}`);
  revalidateTag('posts'); // Revalidate all pages using 'posts' tag
}

// Or use revalidatePath for file-based routes
export async function updatePost(id: string, data: any) {
  await db.posts.update(id, data);

  revalidatePath(`/posts/${id}`); // Revalidate specific post page
  revalidatePath('/posts'); // Revalidate post list page
}
```

#### Safe Fix - Self-Hosted Cache Strategy
```typescript
// next.config.js - for self-hosted deployments
const cache = require('@vercel/cache-handler-redis');

module.exports = {
  cacheHandler: cache({
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6379'
    }
  }),
  cacheMaxMemorySize: 0, // Disable file-based cache entirely
};

// Or use custom handler
import FileSystemCache from 'next/dist/server/lib/cache-handler-fs';

module.exports = {
  cacheHandler: FileSystemCache, // Falls back to filesystem (for dev only)
  cacheMaxMemorySize: 50 * 1024 * 1024, // Limit to 50MB
};
```

#### Regression Test
```typescript
// src/__tests__/cache-invalidation.test.ts
import { revalidateTag, revalidatePath } from 'next/cache';

test('revalidateTag clears specific cached data', async () => {
  // First fetch caches data with tag
  const response1 = await fetch('http://localhost:3000/api/posts/1', {
    next: { tags: ['posts'] }
  });

  // Simulate data change
  await db.posts.update(1, { title: 'Updated' });

  // Revalidate the tag
  await revalidateTag('posts');

  // Second fetch should get fresh data
  const response2 = await fetch('http://localhost:3000/api/posts/1');
  expect(response2.title).toBe('Updated');
});
```

---

### 2. Server Action Network Error Handling

#### Symptoms
- No way to catch network errors in Server Actions
- ERR_INTERNET_DISCONNECTED shows no fallback
- Errors not properly returned to client
- useActionState doesn't capture network errors
- Silent failures with no error indication

#### Root Cause
Server Actions execute on the server, so network errors between client-server are transparent to the action itself. Additionally, errors in Server Actions aren't automatically serialized/sent to client in all cases. The useActionState hook has known bugs around error handling (December 2025).

#### Detection
```typescript
// Test by:
// 1. Disabling network in DevTools
// 2. Triggering a Server Action
// 3. Check if error is visible to user

// Check if useActionState has pending/error state
const [state, formAction, isPending] = useActionState(serverAction, null);
// If error is undefined even on network failure, bug is present
```

#### Safe Fix - Explicit Error Handling
```typescript
// PROBLEMATIC: No network error handling
// app/actions.ts
'use server';

export async function submitForm(formData: FormData) {
  const result = await api.submit(formData);
  return { success: true, data: result };
  // Network errors are unhandled
}

// SAFE: Comprehensive error handling
// app/actions.ts
'use server';

import { z } from 'zod';

export async function submitForm(formData: FormData) {
  try {
    // Validate input first
    const schema = z.object({
      email: z.string().email(),
      message: z.string().min(1)
    });

    const validated = schema.parse({
      email: formData.get('email'),
      message: formData.get('message')
    });

    // Make request with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
      const response = await fetch('https://api.example.com/submit', {
        method: 'POST',
        body: JSON.stringify(validated),
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        return {
          success: false,
          error: `Server error: ${response.status} ${response.statusText}`,
          code: 'SERVER_ERROR'
        };
      }

      return {
        success: true,
        data: await response.json()
      };
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          return {
            success: false,
            error: 'Request timeout - please check your connection',
            code: 'TIMEOUT'
          };
        }

        return {
          success: false,
          error: error.message,
          code: 'NETWORK_ERROR'
        };
      }

      throw error;
    }
  } catch (error) {
    // Validation or unexpected errors
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: error.errors[0].message,
        code: 'VALIDATION_ERROR'
      };
    }

    return {
      success: false,
      error: 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR'
    };
  }
}

// Client-side handling
'use client';

export function SubmitForm() {
  const [state, formAction, isPending] = useActionState(submitForm, null);

  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      <textarea name="message" required />

      {state?.success === false && (
        <div className="error">
          {state.error}
          {state.code === 'TIMEOUT' && (
            <p>Consider checking your internet connection</p>
          )}
        </div>
      )}

      <button disabled={isPending}>
        {isPending ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

#### Regression Test
```typescript
// src/__tests__/server-action-errors.test.ts
import { submitForm } from '@/app/actions';

test('Server Action handles network timeout', async () => {
  // Mock fetch to timeout
  global.fetch = vi.fn(() => new Promise((_, reject) => {
    setTimeout(() => reject(new Error('AbortError')), 100);
  }));

  const formData = new FormData();
  formData.set('email', 'test@example.com');
  formData.set('message', 'test');

  const result = await submitForm(formData);

  expect(result.success).toBe(false);
  expect(result.code).toBe('TIMEOUT');
  expect(result.error).toContain('timeout');
});
```

---

### 3. Middleware Execution Order & Bypass (CVE-2025-29927)

#### Symptoms
- Security checks bypassed in middleware
- Middleware not executing for certain requests
- x-middleware-subrequest header manipulation affects behavior
- Authorization checks not running
- Route protection not working reliably

#### Root Cause
Next.js uses an internal `x-middleware-subrequest` header to prevent infinite recursion in middleware. A critical vulnerability (CVE-2025-29927) allowed attackers to bypass middleware by sending requests with this header: `x-middleware-subrequest: middleware:middleware:middleware:...`. This affects Next.js versions 11.1.4 through 15.2.2.

#### Detection
```typescript
// Check incoming requests for this header
// If it's present, it might indicate an attack attempt

// In middleware:
export function middleware(request: NextRequest) {
  const hasMiddlewareHeader = request.headers.has('x-middleware-subrequest');

  if (hasMiddlewareHeader) {
    // This request might be a bypass attempt
    // Log and handle carefully
    console.warn('Suspicious middleware header detected');
  }
}
```

#### Safe Fix - Upgrade and Add Explicit Guards
```typescript
// REQUIRED: Upgrade to Next.js 15.2.3+
// npm install next@15.2.3

// middleware.ts - Add explicit security checks
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Explicit protection for sensitive routes
  const protectedRoutes = ['/admin', '/api/secrets', '/dashboard'];
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );

  if (isProtectedRoute) {
    const token = request.cookies.get('auth-token')?.value;

    if (!token) {
      // Redirect to login, not to middleware again
      return NextResponse.redirect(new URL('/login', request.url));
    }

    // Verify token validity
    try {
      verifyToken(token); // Your verification logic
    } catch {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Sanitize headers to prevent bypass
  const response = NextResponse.next();

  // Remove potentially malicious headers (don't rely on them)
  response.headers.delete('x-middleware-subrequest');

  return response;
}

// matcher - Be explicit about when middleware runs
export const config = {
  matcher: [
    // Only run on sensitive routes
    '/admin/:path*',
    '/api/secrets/:path*',
    '/dashboard/:path*',
    // Exclude public routes
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

#### Regression Test
```typescript
// src/__tests__/middleware-security.test.ts
import { middleware } from '@/middleware';
import { NextRequest } from 'next/server';

test('middleware cannot be bypassed with crafted header', () => {
  const request = new NextRequest(
    new URL('http://localhost:3000/admin/users'),
    {
      headers: new Headers({
        'x-middleware-subrequest': 'middleware:middleware:middleware'
      })
    }
  );

  const response = middleware(request);

  // Should still require auth, not skip middleware
  expect(response.status).toBe(307); // Redirect to login
  expect(response.headers.get('Location')).toContain('/login');
});
```

---

## Three.js Memory & Resource Bugs

### 1. Geometry, Material, and Texture Disposal (Memory Leak Patterns)

#### Symptoms
- GPU memory usage increasing over time (visible in DevTools)
- WebGL context warnings: "WebGL: RESOURCE_EXHAUSTED"
- Performance degradation after adding/removing 3D objects
- Browser tab becomes sluggish after interaction
- Memory not freed even after dispose() calls

#### Root Cause
Three.js objects store references in VRAM that must be explicitly freed. Common mistakes:
1. Forgetting to call .dispose() on geometries, materials, textures
2. Disposing objects but not removing them from parent (memory still referenced)
3. Reusing materials/geometries without proper cleanup between scenes
4. Post-processing effects not disposing their render targets
5. Loaders caching models without expiration

#### Detection
```typescript
// Monitor GPU memory (Chrome DevTools)
// Memory tab > Detached DOM nodes > Check for unused Three.js objects

// Or programmatically in development:
function checkMemoryLeaks() {
  const canvas = document.querySelector('canvas');
  const gl = canvas?.getContext('webgl');
  const ext = gl?.getExtension('WEBGL_debug_renderer_info');

  if (ext) {
    const unmaskedVendor = gl!.getParameter(ext.UNMASKED_VENDOR_WEBGL);
    const unmaskedRenderer = gl!.getParameter(ext.UNMASKED_RENDERER_WEBGL);
    console.log(`GPU: ${unmaskedVendor} - ${unmaskedRenderer}`);
  }
}
```

#### Safe Fix - Complete Resource Disposal
```typescript
// PROBLEMATIC: Memory leak on mesh removal
const scene = new THREE.Scene();

function addMesh() {
  const geometry = new THREE.BoxGeometry();
  const material = new THREE.MeshStandardMaterial();
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  return mesh;
}

function removeMesh(mesh: THREE.Mesh) {
  scene.remove(mesh);
  // LEAK: geometry and material not disposed!
}

// SAFE: Proper disposal pattern
function removeMesh(mesh: THREE.Mesh) {
  // 1. Remove from scene
  scene.remove(mesh);

  // 2. Dispose geometry (can be reused if in-use elsewhere)
  if (mesh.geometry) {
    mesh.geometry.dispose();
  }

  // 3. Dispose material and its textures
  if (mesh.material) {
    const material = Array.isArray(mesh.material) ? mesh.material : [mesh.material];

    material.forEach(mat => {
      // Dispose textures
      ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap'].forEach(textureType => {
        if (mat[textureType as keyof typeof mat]) {
          mat[textureType as keyof typeof mat].dispose();
        }
      });

      // Dispose material itself
      mat.dispose();
    });
  }
}

// SAFE: Helper function for comprehensive cleanup
function disposeObject3D(object: THREE.Object3D) {
  // Traverse all children
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.geometry.dispose();

      if (Array.isArray(child.material)) {
        child.material.forEach(mat => mat.dispose());
      } else {
        child.material.dispose();
      }
    }

    // Handle line segments, points, etc.
    if (child instanceof THREE.LineSegments || child instanceof THREE.Points) {
      child.geometry.dispose();
      if (Array.isArray(child.material)) {
        child.material.forEach(mat => mat.dispose());
      } else {
        child.material.dispose();
      }
    }
  });

  // Remove from parent
  if (object.parent) {
    object.parent.remove(object);
  }
}

// Usage
const mesh = addMesh();
// ... later ...
disposeObject3D(mesh);
```

#### Safe Fix - Checklist for Complete Disposal
```typescript
// Resource Disposal Checklist for Three.js
const disposalChecklist = {
  // GEOMETRIES - Created with new THREE.Geometry()
  'Geometry objects': ['dispose()'],

  // MATERIALS - Created with new THREE.Material()
  'Material objects': [
    'Dispose material: material.dispose()',
    'Dispose textures: material.map?.dispose()',
    'Dispose all texture properties'
  ],

  // TEXTURES - Created with THREE.TextureLoader
  'Texture objects': [
    'texture.dispose()',
    'Remove from texture cache: THREE.Cache.remove(url)'
  ],

  // RENDER TARGETS - For post-processing
  'RenderTarget objects': ['target.dispose()'],

  // SHADER UNIFORMS
  'WebGL uniforms': [
    'If storing WebGL references, clean them',
    'texture uniforms must be disposed with texture'
  ],

  // SCENE
  'Scene cleanup': [
    'scene.traverse(child => disposeObject3D(child))',
    'Clear scene: scene.children.length = 0'
  ],

  // RENDERER
  'Renderer cleanup': [
    'renderer.dispose()',
    'renderer.forceContextLoss()',
    'Remove canvas from DOM'
  ]
};

// Implementation:
function cleanupScene(scene: THREE.Scene, renderer: THREE.WebGLRenderer) {
  // Dispose all objects in scene
  scene.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.geometry?.dispose();

      const materials = Array.isArray(child.material)
        ? child.material
        : [child.material];

      materials.forEach(mat => {
        // Dispose all texture properties
        Object.keys(mat).forEach(key => {
          if (mat[key as keyof typeof mat]?.dispose) {
            mat[key as keyof typeof mat].dispose();
          }
        });
        mat.dispose();
      });
    }
  });

  // Dispose renderer
  renderer.dispose();
  renderer.forceContextLoss(); // Force context loss for cleanup
}
```

#### Regression Test
```typescript
// src/__tests__/three-memory-disposal.test.ts
import * as THREE from 'three';

test('disposing mesh frees GPU memory', () => {
  const scene = new THREE.Scene();
  const renderer = new THREE.WebGLRenderer();

  // Get initial GPU memory state
  const initialRenderCalls = renderer.info.render.calls;

  // Add mesh
  const geometry = new THREE.BoxGeometry();
  const material = new THREE.MeshStandardMaterial();
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  // Render once
  renderer.render(scene, new THREE.PerspectiveCamera());

  // Dispose
  scene.remove(mesh);
  geometry.dispose();
  material.dispose();

  // Verify WebGL texture memory released
  // (This is approximate - DevTools is most accurate)
  expect(renderer.info.memory.textures).toBeLessThanOrEqual(0);
});
```

---

### 2. React Three Fiber (R3F) Cleanup & Lifecycle Bugs

#### Symptoms
- Components not unmounting properly in R3F
- Memory leaks with R3F components
- dispose={null} not working as expected
- Post-processing effects leaving artifacts
- Canvas not cleaning up when parent unmounts

#### Root Cause
React Three Fiber automatically calls `.dispose()` on unmounted objects (geometry, materials). However:
1. Setting `dispose={null}` correctly prevents disposal but isn't intuitive
2. Custom post-processing passes need manual dispose implementation
3. Loaders with caching can persist across component lifecycles
4. useLoader caches globally by default, which can cause issues in dynamic scenarios

#### Detection
```typescript
// Check R3F logs for disposal messages
// Use React DevTools profiler to verify components mount/unmount

// Manual check:
console.log('R3F Dispose Messages:', window.__r3f?.store?.internal?.disposedObjects);
```

#### Safe Fix - Proper Asset Management in R3F
```typescript
// PROBLEMATIC: Memory leak with cached assets
function Scene() {
  // useLoader caches globally - if component unmounts, cache remains
  const model = useGLTF('/model.glb');

  return <primitive object={model.scene} />;
}

// SAFE: Manage assets with disposal control
function Scene() {
  const group = useRef<THREE.Group>(null);

  const model = useGLTF('/model.glb', (gltf) => {
    // Post-process if needed
    return gltf;
  });

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (model.scene) {
        model.scene.traverse((child) => {
          if (child instanceof THREE.Mesh) {
            child.geometry?.dispose();
            if (Array.isArray(child.material)) {
              child.material.forEach(m => m.dispose());
            } else {
              child.material?.dispose();
            }
          }
        });
      }
    };
  }, [model]);

  return (
    <group ref={group}>
      <primitive object={model.scene} dispose={null} />
    </group>
  );
}

// SAFE: Post-processing with proper disposal
function Effects() {
  const composer = useRef<EffectComposer>(null);

  useEffect(() => {
    return () => {
      // Dispose composer and all passes
      composer.current?.dispose();

      // Dispose render targets
      composer.current?.passes.forEach(pass => {
        if ('dispose' in pass) {
          (pass as any).dispose();
        }
      });
    };
  }, []);

  return (
    <EffectComposer ref={composer}>
      <Bloom />
      <Noise />
    </EffectComposer>
  );
}

// SAFE: Using @react-three/postprocessing (handles disposal)
// This library properly disposes effects
import { EffectComposer, Bloom, Noise } from '@react-three/postprocessing';

function Scene() {
  return (
    <EffectComposer>
      <Bloom />
      <Noise />
      {/* Disposal handled automatically */}
    </EffectComposer>
  );
}

// SAFE: Preventing loader cache pollution
function useGLTFCached(url: string) {
  const model = useGLTF(url);

  useEffect(() => {
    return () => {
      // Remove from global cache on unmount
      // (Be careful: only if you don't reuse this asset)
      if (DELETE_CACHE_ON_UNMOUNT) {
        THREE.Cache.remove(url);
      }
    };
  }, [url]);

  return model;
}
```

---

## GSAP + Animation Bugs

### 1. gsap.context() Cleanup Pattern & Bugs

#### Symptoms
- GSAP animations not stopping on component unmount
- Multiple animations stacking and interfering
- ScrollTrigger not cleaning up
- Memory usage increasing with multiple animations
- Draggables not deactivating on unmount

#### Root Cause
GSAP animations/ScrollTriggers need explicit cleanup. The old pattern (manually tracking instances) was error-prone. The new gsap.context() pattern is safer but requires correct usage:
1. Not wrapping code in gsap.context()
2. Not calling revert() in cleanup
3. Setting revertOnUpdate incorrectly
4. Context scope not matching component scope

#### Detection
```bash
# GSAP provides a dev tool to check for "orphaned" animations
# In DevTools console:
gsap.globalTimeline.getChildren();
// If this has many animations, cleanup might be broken

# Check for unapplied tweens:
gsap.globalTimeline.getTweensOf('.element');
```

#### Safe Fix - useGSAP Hook Pattern
```typescript
// PROBLEMATIC: Manual cleanup without gsap.context()
function AnimatedBox() {
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tween = gsap.to(boxRef.current, {
      duration: 1,
      x: 100,
      repeat: -1
    });

    // Cleanup forgotten - animation continues
    return () => {
      // This doesn't exist - tween never stops
      // tween.kill();
    };
  }, []);

  return <div ref={boxRef}>Box</div>;
}

// SAFE: Using useGSAP hook with gsap.context()
import { useGSAP } from '@gsap/react';

function AnimatedBox() {
  const boxRef = useRef<HTMLDivElement>(null);

  // useGSAP automatically handles cleanup via gsap.context()
  useGSAP(() => {
    gsap.to(boxRef.current, {
      duration: 1,
      x: 100,
      repeat: -1
    });
    // All GSAP objects created here are tracked automatically
  }, { scope: boxRef }); // scope ensures all selectors are relative to boxRef

  return <div ref={boxRef}>Box</div>;
}

// SAFE: Using gsap.context() directly
function AnimatedBox() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Create context to group animations
    const ctx = gsap.context(() => {
      // All GSAP code here is tracked
      gsap.to('.box', {
        duration: 1,
        x: 100,
        stagger: 0.1
      });

      gsap.from('.title', {
        duration: 0.5,
        opacity: 0,
        y: -20
      });
    }, containerRef); // scope to container

    // Cleanup: revert ALL animations created in context
    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef}>
      <div className="title">Title</div>
      <div className="box">Box 1</div>
      <div className="box">Box 2</div>
    </div>
  );
}

// SAFE: With revertOnUpdate for re-renders
function AnimatedBox({ count }: { count: number }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      // Re-creates animations when 'count' changes
      gsap.to('.item', {
        duration: 0.5,
        opacity: 1,
        y: 0,
        stagger: 0.1
      });
    },
    {
      scope: containerRef,
      revertOnUpdate: true, // Kill old animations before creating new ones
      dependencies: [count] // Only re-run when count changes
    }
  );

  return (
    <div ref={containerRef}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="item">Item {i}</div>
      ))}
    </div>
  );
}
```

#### Regression Test
```typescript
// src/__tests__/gsap-cleanup.test.tsx
import { render, unmountComponentAtNode } from 'react-dom';
import { gsap } from 'gsap';

test('gsap.context cleanup reverts all animations on unmount', () => {
  const container = document.createElement('div');

  function AnimatedComponent() {
    const ref = useRef<HTMLDivElement>(null);

    useGSAP(() => {
      gsap.to(ref.current, { x: 100, duration: 1 });
      gsap.to(ref.current, { rotation: 360, duration: 1 });
    }, { scope: ref });

    return <div ref={ref} />;
  }

  // Render component
  render(<AnimatedComponent />, container);

  // Check animations exist
  const initialChildren = gsap.globalTimeline.getChildren().length;
  expect(initialChildren).toBeGreaterThan(0);

  // Unmount
  unmountComponentAtNode(container);

  // Check animations cleaned up
  const finalChildren = gsap.globalTimeline.getChildren().length;
  expect(finalChildren).toBe(initialChildren - 2); // 2 animations removed
});
```

---

### 2. ScrollTrigger Refresh Timing & Race Conditions

#### Symptoms
- ScrollTrigger animations starting before page content loads
- Pinned elements overlapping content after resize
- ScrollTrigger positions incorrect on page load
- Animations triggering at wrong scroll positions
- Performance lag on window resize (refresh hammer)

#### Root Cause
ScrollTrigger calculates trigger positions based on current DOM. If called before layout is complete:
1. Dimensions are wrong, calculations off
2. New content added → ScrollTrigger positions stale
3. Window resize → Must recalculate all triggers (expensive)
4. Race condition with GSAP animations initializing

#### Detection
```typescript
// Check if scroll positions are calculated correctly
gsap.utils.toArray('[data-trigger]').forEach((trigger: any) => {
  const scrollTrigger = gsap.getProperty(trigger, 'scrollTrigger');
  console.log(`Trigger ${trigger.id}:`, {
    start: scrollTrigger?.start,
    end: scrollTrigger?.end,
    trigger: scrollTrigger?.trigger
  });
});

// If values seem wrong, timing issue likely
```

#### Safe Fix - Proper ScrollTrigger Initialization
```typescript
// PROBLEMATIC: Race condition on page load
function ScrollSection() {
  useGSAP(() => {
    gsap.registerPlugin(ScrollTrigger);

    // PROBLEM: Called immediately, DOM might not be ready
    ScrollTrigger.create({
      trigger: '.section',
      start: 'top center',
      onEnter: () => console.log('Entered')
    });

    // PROBLEM: Images might still be loading
  }, { scope: containerRef });

  return <div className="section">Content</div>;
}

// SAFE: Wait for DOM and images to load
function ScrollSection() {
  useGSAP(() => {
    gsap.registerPlugin(ScrollTrigger);

    // Delay refresh until images are loaded
    const refreshAfterLoad = () => {
      ScrollTrigger.refresh();
    };

    // Option 1: Wait for images
    Promise.all(
      Array.from(document.images)
        .filter(img => !img.complete)
        .map(img => new Promise(resolve => {
          img.addEventListener('load', resolve);
          img.addEventListener('error', resolve);
        }))
    ).then(() => {
      ScrollTrigger.refresh();
    });

    // Option 2: Use requestAnimationFrame for next paint
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        ScrollTrigger.refresh();
      });
    });

    // Create ScrollTrigger after refresh
    ScrollTrigger.create({
      trigger: '.section',
      start: 'top center',
      markers: process.env.NODE_ENV === 'development', // Debug markers in dev
      onEnter: () => console.log('Entered')
    });
  }, { scope: containerRef });

  return <div className="section">Content</div>;
}

// SAFE: Optimize refresh performance
function ScrollSection() {
  const lastRefreshTime = useRef(0);

  useGSAP(() => {
    gsap.registerPlugin(ScrollTrigger);

    // Debounce refresh on resize (prevent "refresh hammer")
    const handleResize = () => {
      const now = Date.now();
      if (now - lastRefreshTime.current > 250) { // Max 1 refresh per 250ms
        ScrollTrigger.refresh();
        lastRefreshTime.current = now;
      }
    };

    window.addEventListener('resize', handleResize);

    // Initial refresh
    ScrollTrigger.refresh();

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, { scope: containerRef });

  return <div className="section">Content</div>;
}

// SAFE: Setting refreshPriority for complex layouts
function ScrollSection() {
  useGSAP(() => {
    gsap.registerPlugin(ScrollTrigger);

    // Pinned element (refreshes first to avoid conflicts)
    ScrollTrigger.create({
      trigger: '.pinned',
      pin: true,
      pinSpacing: true,
      start: 'top top',
      refreshPriority: 1, // Refresh first (lower number = higher priority)
    });

    // Regular scroll trigger (refreshes after pinned)
    ScrollTrigger.create({
      trigger: '.section',
      start: 'top center',
      refreshPriority: 2,
    });

    ScrollTrigger.refresh();
  }, { scope: containerRef });

  return (
    <div ref={containerRef}>
      <div className="pinned">Pinned</div>
      <div className="section">Content</div>
    </div>
  );
}
```

#### Regression Test
```typescript
// src/__tests__/scrolltrigger-timing.test.tsx
import { render, waitFor } from '@testing-library/react';

test('ScrollTrigger calculates positions after images load', async () => {
  let imageLoadCount = 0;

  function ScrollComponent() {
    useGSAP(() => {
      gsap.registerPlugin(ScrollTrigger);

      // Wait for images
      Promise.all(
        Array.from(document.images).map(img =>
          new Promise(resolve => {
            if (img.complete) resolve(null);
            else img.addEventListener('load', resolve);
          })
        )
      ).then(() => {
        ScrollTrigger.refresh();
      });

      ScrollTrigger.create({
        trigger: '.section',
        start: 'top center',
      });
    }, { scope: containerRef });

    return (
      <div ref={containerRef}>
        <img src="/image.jpg" onLoad={() => imageLoadCount++} />
        <div className="section">Content</div>
      </div>
    );
  }

  render(<ScrollComponent />);

  await waitFor(() => {
    expect(imageLoadCount).toBe(1);
  });

  // ScrollTrigger should have correct positions
  const triggers = ScrollTrigger.getAll();
  expect(triggers.length).toBeGreaterThan(0);
  triggers.forEach(trigger => {
    expect(trigger.start).toBeGreaterThan(-1);
    expect(trigger.end).toBeGreaterThan(trigger.start);
  });
});
```

---

### 3. Lenis + ScrollTrigger Synchronization

#### Symptoms
- Scroll position jumps between Lenis and ScrollTrigger
- Pinning breaks when Lenis is enabled
- Animation timing off with smooth scroll
- Mobile performance degradation
- Multiple scrolling animations fighting each other

#### Root Cause
Lenis (smooth scrolling library) and GSAP's ScrollTrigger calculate scroll independently. When both run:
1. They disagree on current scroll position
2. ScrollTrigger pins interfere with Lenis scroll
3. Browser's native scroll events and Lenis custom events conflict
4. Mobile browsers handle scroll differently, Lenis can't keep up

#### Detection
```typescript
// Test if sync is working:
// 1. Scroll page smoothly
// 2. Pin should stay in place without jumping
// 3. No lag between scroll and pin movement

// Check Lenis and ScrollTrigger state
console.log('Lenis isScrolling:', window.lenis?.isScrolling);
console.log('ScrollTrigger proxy:', ScrollTrigger.getScrollerProxyObject());
```

#### Safe Fix - Proper Lenis + ScrollTrigger Integration
```typescript
// PROBLEMATIC: Lenis without ScrollTrigger sync
function SmoothScroll() {
  useEffect(() => {
    const lenis = new Lenis(); // Missing ScrollTrigger integration

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => lenis.destroy();
  }, []);

  return <div>Content</div>;
}

// SAFE: Proper Lenis + ScrollTrigger sync (from Lenis docs)
function SmoothScroll() {
  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const lenis = new Lenis();

    // Sync Lenis scroll with ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);

    // Use ScrollTrigger's scroller proxy for Lenis
    ScrollTrigger.scrollerProxy(window, {
      scrollTop(value) {
        if (arguments.length) {
          lenis.scrollTo(value, { immediate: true, force: true });
        } else {
          return lenis.scroll;
        }
      },
      scrollLeft(value) {
        // Horizontal scroll if needed
        if (arguments.length) {
          lenis.scrollTo(value, { immediate: true, force: true });
        } else {
          return lenis.scroll;
        }
      },
      getBoundingClientRect() {
        return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
      },
      pinType: 'transform' // Use transform for pinning (better performance)
    });

    // Refresh ScrollTrigger on resize
    ScrollTrigger.addEventListener('refresh', () => lenis.resize());
    ScrollTrigger.refresh();

    // Animation loop
    const clock = new THREE.Clock();
    function raf() {
      const deltaTime = clock.getDelta();
      lenis.raf(deltaTime * 1000); // Convert to milliseconds
      ScrollTrigger.update();
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, []);

  return <div>Content</div>;
}

// SAFE: Alternative using Next.js + Lenis hook
function SmoothScrollContainer() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // easeOutExpo
      direction: 'vertical',
      gestureDirection: 'vertical',
      smoothWheel: true,
      smoothTouch: false,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    });

    // Fix for RAF
    let lastTime = Date.now();
    function raf(currentTime: number) {
      const deltaTime = currentTime - lastTime;
      lastTime = currentTime;

      lenis.raf(deltaTime);
      requestAnimationFrame(raf);
    }

    const animationFrameId = requestAnimationFrame(raf);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId);
      lenis.destroy();
    };
  }, []);

  return <div>Content</div>;
}

// SAFE: ScrollTrigger with pinType: 'transform' (doesn't conflict with Lenis)
function PinnedSection() {
  useGSAP(() => {
    gsap.registerPlugin(ScrollTrigger);

    ScrollTrigger.create({
      trigger: '.pinned-section',
      pin: true,
      start: 'top top',
      end: 'bottom center',
      pinSpacing: true,
      pinType: 'transform', // Use CSS transform, not position changes
      markers: true,
    });
  });

  return (
    <section className="pinned-section">
      <h2>This stays pinned</h2>
    </section>
  );
}
```

#### Regression Test
```typescript
// src/__tests__/lenis-scrolltrigger-sync.test.ts
import { Lenis } from '@studio-freight/lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

test('Lenis and ScrollTrigger stay in sync during scroll', (done) => {
  gsap.registerPlugin(ScrollTrigger);
  const lenis = new Lenis();

  // Setup sync (as per safe fix pattern)
  lenis.on('scroll', ScrollTrigger.update);

  ScrollTrigger.scrollerProxy(window, {
    scrollTop(value) {
      if (arguments.length) {
        lenis.scrollTo(value, { immediate: true });
      } else {
        return lenis.scroll;
      }
    },
    getBoundingClientRect() {
      return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
    },
    pinType: 'transform'
  });

  // Create a trigger
  const trigger = ScrollTrigger.create({
    trigger: '.test-element',
    start: 'top center',
    end: 'bottom center'
  });

  // Simulate scroll
  lenis.scrollTo(500, { immediate: true });

  // Check sync
  setTimeout(() => {
    expect(Math.abs(window.scrollY - lenis.scroll)).toBeLessThan(1); // Allow 1px tolerance
    expect(trigger.isActive).toBe(true);

    lenis.destroy();
    done();
  }, 100);
});
```

---

## TypeScript Bug Prevention

### 1. Strict Mode: Catching Null Reference and Type Errors

#### What Strict Mode Prevents
When `"strict": true` is enabled in tsconfig.json, TypeScript enforces five critical checks that prevent 2 a.m. production bugs:

```typescript
// tsconfig.json - Complete strict configuration
{
  "compilerOptions": {
    "strict": true,
    // This enables all of:
    "noImplicitAny": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "strictBindCallApply": true,
    "strictFunctionTypes": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true
  }
}
```

#### 1a. noImplicitAny: Prevents "undefined is not a function"

```typescript
// PROBLEMATIC: Without noImplicitAny
function processData(data) { // 'data' is implicitly 'any'
  return data.toUpperCase(); // No error! But crashes if data is null
}

processData(null); // Runtime error: Cannot read property 'toUpperCase' of null

// SAFE: With noImplicitAny enabled
function processData(data: string) {
  return data.toUpperCase(); // TypeScript knows this is safe
}

// OR accept null explicitly:
function processData(data: string | null) {
  if (data === null) return 'N/A';
  return data.toUpperCase();
}
```

#### 1b. strictNullChecks: Prevents "Cannot read property of null"

```typescript
// PROBLEMATIC: Without strictNullChecks
function getUserName(user: { name: string }) {
  return user.name.length; // Assumes name exists, but what if user is null?
}

// Function called with null
getUserName(null); // Runtime error!

// SAFE: With strictNullChecks enabled
function getUserName(user: { name: string } | null) {
  if (user === null) return 0;
  return user.name.length; // TypeScript forces you to handle null
}

// OR use optional chaining:
function getUserName(user: { name: string } | null) {
  return user?.name?.length ?? 0;
}
```

#### 1c. strictPropertyInitialization: Prevents "property used before initialization"

```typescript
// PROBLEMATIC: Without strictPropertyInitialization
class UserService {
  userId: string; // Not initialized
  userName: string;

  constructor(id: string) {
    this.userId = id;
    // userName is never initialized but will be used
  }

  getName() {
    return this.userName.toUpperCase(); // Runtime error: undefined
  }
}

// SAFE: With strictPropertyInitialization enabled
class UserService {
  userId: string;
  userName: string = ''; // Initialize, or...

  constructor(id: string) {
    this.userId = id;
    this.userName = this.loadUserName(id); // Initialize in constructor
  }

  getName() {
    return this.userName.toUpperCase(); // Safe: guaranteed to be string
  }

  private loadUserName(id: string): string {
    return 'User'; // Or load from API
  }
}
```

#### Regression Test - Strict Mode Benefits
```typescript
// src/__tests__/strict-mode-benefits.test.ts
import { describe, test, expect } from 'vitest';

describe('Strict Mode Prevention', () => {
  test('prevents null reference errors at compile time', () => {
    // With strictNullChecks, this compiles error:
    // Type 'null' is not assignable to type 'string'

    // Without it, this would fail at runtime:
    const result = (null as any).toUpperCase();
  });

  test('prevents implicit any type errors', () => {
    // With noImplicitAny, this compiles error:
    // Parameter 'x' implicitly has an 'any' type

    // Without it, TypeScript silently accepts it:
    function broken(x: any) {
      return x.nonExistentMethod();
    }
  });

  test('prevents uninitialized property usage', () => {
    class Example {
      prop: string; // With strictPropertyInitialization, ERROR
      // Without it, this compiles and crashes at runtime

      constructor() {
        // prop is never set
      }

      use() {
        console.log(this.prop.length); // undefined.length → error
      }
    }
  });
});
```

---

### 2. Discriminated Unions for Exhaustive Type Checking

#### Problem: Forgetting Cases in Type Unions

```typescript
// PROBLEMATIC: Easy to forget cases
type APIResponse =
  | { status: 'success'; data: any }
  | { status: 'error'; error: string }
  | { status: 'loading' };

function handleResponse(response: APIResponse) {
  if (response.status === 'success') {
    console.log(response.data);
  }
  // Oops! Forgot 'error' and 'loading' cases
  // Compiles fine, but at runtime crashes if response is error or loading
}

// SAFE: Discriminated Union with Exhaustive Checking
type APIResponse =
  | { status: 'success'; data: any }
  | { status: 'error'; error: string }
  | { status: 'loading' };

function handleResponse(response: APIResponse): void {
  switch (response.status) {
    case 'success':
      console.log(response.data);
      break;
    case 'error':
      console.error(response.error);
      break;
    case 'loading':
      console.log('Loading...');
      break;
    default:
      // Exhaustiveness check: if you add a new status, this will error
      const _: never = response;
      throw new Error(`Unhandled status: ${_}`);
  }
}

// Add new status? TypeScript NOW forces you to handle it:
type APIResponse =
  | { status: 'success'; data: any }
  | { status: 'error'; error: string }
  | { status: 'loading' }
  | { status: 'cached' }; // NEW

// This now has an error on default case:
// Type 'APIResponse' is not assignable to type 'never'
// Forces you to add 'cached' case
```

#### Safe Pattern - Discriminated Union Handler Map

```typescript
// Type-safe handler pattern
type UserEvent =
  | { type: 'login'; email: string }
  | { type: 'logout' }
  | { type: 'updateProfile'; name: string; avatar: string };

// Create handler map that MUST handle all types
const userEventHandlers: Record<UserEvent['type'], (event: UserEvent) => void> = {
  'login': (e) => {
    if (e.type !== 'login') return; // Exhaustion check
    console.log('Logged in:', e.email);
  },
  'logout': (e) => {
    if (e.type !== 'logout') return;
    console.log('Logged out');
  },
  'updateProfile': (e) => {
    if (e.type !== 'updateProfile') return;
    console.log('Profile updated:', e.name, e.avatar);
  }
  // MUST have all types here or TypeScript errors
};

function dispatch(event: UserEvent) {
  userEventHandlers[event.type](event);
}

// Add new event type?
type UserEvent =
  | { type: 'login'; email: string }
  | { type: 'logout' }
  | { type: 'updateProfile'; name: string; avatar: string }
  | { type: 'changePassword' }; // NEW

// TypeScript ERROR: Missing 'changePassword' in handlers map
// Forces you to add handler
```

#### Regression Test - Exhaustiveness
```typescript
// src/__tests__/discriminated-unions.test.ts
import { describe, test, expect } from 'vitest';

describe('Discriminated Unions', () => {
  test('exhaustiveness prevents missing cases', () => {
    type Shape =
      | { kind: 'circle'; radius: number }
      | { kind: 'square'; side: number }
      | { kind: 'triangle'; base: number; height: number };

    // This compiles error if any case is missing:
    function getArea(shape: Shape): number {
      switch (shape.kind) {
        case 'circle':
          return Math.PI * shape.radius ** 2;
        case 'square':
          return shape.side ** 2;
        case 'triangle':
          return (shape.base * shape.height) / 2;
        default:
          const _: never = shape;
          return _;
      }
    }

    expect(getArea({ kind: 'circle', radius: 5 })).toBeCloseTo(78.5);
    expect(getArea({ kind: 'square', side: 4 })).toBe(16);
    expect(getArea({ kind: 'triangle', base: 3, height: 4 })).toBe(6);
  });
});
```

---

### 3. Template Literal Types for Type-Safe APIs

#### Problem: String APIs Without Type Safety

```typescript
// PROBLEMATIC: Type-unsafe API
function fetchResource(resource: string, action: string) {
  return fetch(`/api/${resource}/${action}`);
}

// Compiles fine but could be wrong at runtime:
fetchResource('users', 'list'); // OK
fetchResource('users', 'updateSetting'); // Typo, no error!
fetchResource('product', 'list'); // Wrong resource name, no error!

// SAFE: Template Literal Types
type Resource = 'users' | 'posts' | 'comments';
type Action = 'list' | 'get' | 'create' | 'update' | 'delete';

// Define valid endpoints explicitly
type ValidEndpoint = `${Resource}/${Action}`;

function fetchResource(endpoint: ValidEndpoint) {
  return fetch(`/api/${endpoint}`);
}

fetchResource('users/list'); // OK
fetchResource('users/create'); // OK
fetchResource('users/updateSetting'); // ERROR: not a valid endpoint
fetchResource('product/list'); // ERROR: 'product' not a valid resource
```

#### Advanced: Event Names Stay in Sync

```typescript
// Type-safe event system
type Events = {
  'user:login': { email: string };
  'user:logout': void;
  'post:created': { postId: string };
  'post:deleted': { postId: string };
};

// Define event emitter that only accepts valid events
class EventBus {
  on<E extends keyof Events>(
    event: E,
    callback: (data: Events[E]) => void
  ): void {
    // Implementation
  }

  emit<E extends keyof Events>(
    event: E,
    data: Events[E]
  ): void {
    // Implementation
  }
}

const bus = new EventBus();

bus.on('user:login', (data) => {
  console.log(data.email); // Type-safe: data has 'email'
});

bus.emit('user:login', { email: 'user@example.com' }); // OK

// This errors:
bus.on('user:login', (data) => {
  console.log(data.nonExistent); // ERROR: no such property
});

bus.emit('user:login', { wrongField: 'value' }); // ERROR: missing 'email'

bus.on('user:login123', () => {}); // ERROR: invalid event name
```

#### Path Validation with Template Literals

```typescript
// Type-safe route definitions
type Page = 'home' | 'about' | 'contact';
type User = 'profile' | 'settings' | 'privacy';

// Only these paths are valid
type ValidRoute = `/` | `/about` | `/contact` | `/users/${string}`;

// Or more precisely:
type ValidRoute =
  | `/`
  | `/${Page}`;

// Router function
function navigateTo(path: ValidRoute) {
  window.location.href = path;
}

navigateTo('/'); // OK
navigateTo('/about'); // OK
navigateTo('/invalid'); // ERROR: not a ValidRoute

// Even more powerful: Parameter extraction
type RoutePath<T extends string> = T extends `/users/${infer UserID}`
  ? UserID
  : never;

type UserRoute = `/users/john`;
type UserId = RoutePath<UserRoute>; // Type: 'john'
```

#### Regression Test - Type-Safe APIs
```typescript
// src/__tests__/template-literal-types.test.ts
import { describe, test, expect } from 'vitest';

describe('Template Literal Types', () => {
  test('prevents invalid API endpoint calls at compile time', () => {
    type ValidEndpoint = `api/${
      | 'users'
      | 'posts'
    }/${
      | 'list'
      | 'detail'
      | 'create'
      | 'update'
    }`;

    // These compile:
    const endpoint1: ValidEndpoint = 'api/users/list';
    const endpoint2: ValidEndpoint = 'api/posts/create';

    // These don't compile:
    // const endpoint3: ValidEndpoint = 'api/comments/list'; // Invalid resource
    // const endpoint4: ValidEndpoint = 'api/users/delete'; // Invalid action

    expect(endpoint1).toBe('api/users/list');
    expect(endpoint2).toBe('api/posts/create');
  });

  test('event names stay in sync with handlers', () => {
    type Events = {
      'click:button': { buttonId: string };
      'scroll:end': { position: number };
    };

    // Type-safe handler registration
    function registerHandler<E extends keyof Events>(
      event: E,
      handler: (data: Events[E]) => void
    ) {
      return { event, handler };
    }

    const registration = registerHandler('click:button', (data) => {
      // data is typed as { buttonId: string }
      expect(data.buttonId).toBeDefined();
    });

    // This would not compile:
    // registerHandler('invalid:event', () => {});
    // registerHandler('click:button', (data) => data.nonExistent);
  });
});
```

---

## Summary & Action Items

### Critical Updates Required (2025)
1. **React & Next.js**: Update immediately to patch CVE-2025-55182 and related RSC vulnerabilities
2. **Middleware Security**: Upgrade Next.js to 15.2.3+ to patch CVE-2025-29927
3. **Three.js Memory**: Audit disposal patterns - use checklist provided
4. **GSAP Cleanup**: Migrate to useGSAP hook or implement gsap.context() properly

### Testing Priority
1. Implement regression tests for each bug pattern
2. Use TypeScript strict mode as your first line of defense
3. Run exhaustive-deps ESLint checks in CI/CD
4. Test hydration mismatches with SSR/SSG combinations

### Configuration Checklist
- [ ] `tsconfig.json`: `"strict": true` enabled
- [ ] ESLint: `plugin:react-hooks/recommended` and `exhaustive-deps`
- [ ] React: Updated to 19.2.3+ (RSC security)
- [ ] Next.js: Updated to latest patched version
- [ ] GSAP: Using @gsap/react with useGSAP hook
- [ ] Three.js: Disposal audit complete
- [ ] ScrollTrigger: Proper refresh timing implemented

---

## References & Sources

- [React 19.2 Release](https://react.dev/blog/2025/10/01/react-19-2)
- [React Server Components Security](https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components)
- [React Compiler Documentation](https://react.dev/learn/react-compiler)
- [Next.js 15 Security Update](https://nextjs.org/blog/security-update-2025-12-11)
- [GSAP + React Guide](https://gsap.com/resources/React/)
- [React Three Fiber Disposal](https://gracious-keller-98ef35.netlify.app/docs/api/automatic-disposal/)
- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)
- [Discriminated Unions](https://www.typescriptlang.org/docs/handbook/unions-and-intersections.html)
- [Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)

---

**Last Updated**: February 2025
**Research Cutoff**: December 2025
**Framework Versions Covered**:
- React 19.0-19.2+
- Next.js 15.0-15.5+
- Three.js (latest)
- GSAP 3.12+
- React Three Fiber (latest)
- TypeScript 5.x
