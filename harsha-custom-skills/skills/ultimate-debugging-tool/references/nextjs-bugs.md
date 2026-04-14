# Next.js 15+ / 16+ Bug Patterns

**Versions Covered:** Next.js 15.0+ through 16.2 (released March 18, 2026; validated April 2, 2026)

### N-001: Stale Cache Data

**Symptom:** Updated data doesn't appear; old content served even after database changes

**Root Cause:** App Router caches aggressively by default. Route is cached indefinitely unless explicitly revalidated

**Detection:**
```typescript
// BUGGY - no revalidation strategy
export default async function PostPage({ params }) {
  const post = await fetch(`/api/posts/${params.id}`);
  return <div>{post.title}</div>; // Cached forever
}

// BUGGY - time-based caching with stale data
export default async function Page() {
  const data = await fetch('/api/data', { next: { revalidate: 60 } });
  return <div>{data}</div>; // Stale for up to 60 seconds
}
```

**Safe Fix**

**For Next.js 16+** (opt-in caching with "use cache" directive):
```typescript
// Option 1: Use "use cache" directive for explicit caching (Next.js 16+)
// Requires cacheComponents: true in next.config.js
'use cache';

export default async function PostPage({ params }) {
  // Must await async params in Next.js 16
  const { id } = await params;

  const post = await fetch(`/api/posts/${id}`, {
    next: { tags: [`post-${id}`] }
  });

  async function revalidatePost() {
    'use server';
    revalidateTag(`post-${id}`);
  }

  return (
    <div>
      <h1>{post.title}</h1>
      <button onClick={revalidatePost}>Refresh</button>
    </div>
  );
}

// Option 2: "use cache" at function level (data function)
async function getPost(id: string) {
  'use cache';
  return fetch(`/api/posts/${id}`);
}

// Option 3: No cache for dynamic data
export default async function Dashboard() {
  const data = await fetch('/api/dashboard', {
    cache: 'no-store' // Fresh data every request
  });

  return <div>{data}</div>;
}
```

**For Next.js 15 and earlier** (legacy revalidation):
```typescript
// Option 1: Revalidate on demand via Server Action
export default async function PostPage({ params }) {
  const post = await fetch(`/api/posts/${params.id}`, {
    next: { tags: ['post', `post-${params.id}`] }
  });

  async function revalidatePost() {
    'use server';
    revalidateTag(`post-${params.id}`);
  }

  return (
    <div>
      <h1>{post.title}</h1>
      <button onClick={revalidatePost}>Refresh</button>
    </div>
  );
}

// Option 2: Route-level revalidation
export const revalidate = 60; // Revalidate every 60 seconds

export default async function Page() {
  const data = await fetch('/api/data');
  return <div>{data}</div>;
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Rely on client-side refetch to invalidate cache
export default function PostPage({ params }) {
  const [post, setPost] = useState(null);

  useEffect(() => {
    fetch(`/api/posts/${params.id}`)
      .then(res => res.json())
      .then(setPost);
  }, []); // Cache still active on server
}
```

**Regression Test:**
```typescript
describe('N-001: Stale Cache', () => {
  it('should revalidate tagged data', async () => {
    const cache = new Map();

    // Initial fetch
    const post1 = await fetch('/api/posts/1');
    expect(post1.title).toBe('Original');

    // Update on backend
    await updatePost(1, { title: 'Updated' });
    revalidateTag('post-1');

    const post2 = await fetch('/api/posts/1');
    expect(post2.title).toBe('Updated');
  });
});
```

---

### N-002: Server Action Error Not Caught

**Symptom:** Server Action throws error but client doesn't show error state; application appears broken

**Root Cause:** Server Action throws but client code doesn't handle the error or returns error state

**Detection:**
```typescript
// BUGGY - no error handling
'use server';
export async function createUser(formData) {
  const email = formData.get('email');

  if (!email) {
    throw new Error('Email required'); // Not caught on client
  }

  const user = await db.users.create({ email });
  return user;
}

// Client side - no error handling
export function SignupForm() {
  async function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const user = await createUser(formData); // Error thrown, not caught
    console.log(user);
  }

  return <form onSubmit={handleSubmit}>...</form>;
}
```

**Safe Fix:**
```typescript
// Option 1: Return error state object
'use server';
export async function createUser(formData) {
  const email = formData.get('email');

  if (!email) {
    return { error: 'Email required', success: false };
  }

  try {
    const user = await db.users.create({ email });
    return { user, success: true };
  } catch (error) {
    return { error: error.message, success: false };
  }
}

// Client side - handle response
'use client';
export function SignupForm() {
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const result = await createUser(formData);

    if (!result.success) {
      setError(result.error);
      return;
    }

    console.log('User created:', result.user);
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <input type="email" name="email" />
      <button type="submit">Sign Up</button>
    </form>
  );
}

// Option 2: Use try-catch if you prefer exceptions
'use client';
export function SignupForm() {
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const formData = new FormData(e.target);
      const user = await createUser(formData);
      console.log('User created:', user);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <input type="email" name="email" />
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Assume Server Action always succeeds
export function SignupForm() {
  async function handleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const user = await createUser(formData); // Crashes if error thrown
    navigate('/dashboard');
  }

  return <form onSubmit={handleSubmit}>...</form>;
}
```

**Regression Test:**
```typescript
describe('N-002: Server Action Errors', () => {
  it('should return error state on validation failure', async () => {
    const result = await createUser(new FormData());

    expect(result.success).toBe(false);
    expect(result.error).toBe('Email required');
  });

  it('should display error in form', async () => {
    render(<SignupForm />);
    fireEvent.click(screen.getByText('Sign Up'));

    await waitFor(() => {
      expect(screen.getByText('Email required')).toBeInTheDocument();
    });
  });
});
```

---

### N-003: Environment Variable Exposed to Client

**Symptom:** Secret API key appears in browser DevTools; credentials leaked to client

**Root Cause:** Using `NEXT_PUBLIC_` prefix on sensitive values, or importing server-only modules in client code

**Detection:**
```typescript
// BUGGY - secret exposed
// .env.local
NEXT_PUBLIC_DATABASE_PASSWORD=super_secret_123
NEXT_PUBLIC_API_KEY=sk_secret_abc123

// page.tsx
const apiKey = process.env.NEXT_PUBLIC_API_KEY; // Bundled into client
const password = process.env.NEXT_PUBLIC_DATABASE_PASSWORD;

fetch('https://api.example.com', {
  headers: { Authorization: `Bearer ${apiKey}` }
});
```

**Safe Fix:**
```typescript
// .env.local
# Public values only
NEXT_PUBLIC_API_URL=https://api.example.com

# Secret values (no NEXT_PUBLIC_ prefix)
DATABASE_PASSWORD=super_secret_123
API_SECRET_KEY=sk_secret_abc123

// lib/api.ts (Server-only)
export async function fetchWithAuth(endpoint: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    headers: {
      Authorization: `Bearer ${process.env.API_SECRET_KEY}` // Server only
    }
  });
  return response.json();
}

// page.tsx (Client uses Server Action)
'use client';

export function MyComponent() {
  async function loadData() {
    const data = await fetchWithAuth('/data'); // Calls server-only function
    return data;
  }

  return <button onClick={loadData}>Load</button>;
}

// route.ts (API Route with secrets)
export async function GET(request: Request) {
  const data = await fetch('https://internal-api.example.com', {
    headers: {
      'X-API-Key': process.env.API_SECRET_KEY // Safe in route handler
    }
  });

  return Response.json(data);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Pass secrets to client
'use client';

export function MyComponent() {
  // Secrets visible in browser
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;

  async function loadData() {
    fetch('https://api.example.com', {
      headers: { Authorization: `Bearer ${apiKey}` }
    });
  }
}
```

**Regression Test:**
```typescript
describe('N-003: Env Var Exposure', () => {
  it('should not bundle API_SECRET_KEY', () => {
    const bundle = getBundleContent();
    expect(bundle).not.toContain('sk_secret_abc123');
    expect(bundle).not.toContain('DATABASE_PASSWORD');
  });

  it('should allow NEXT_PUBLIC_ vars in bundle', () => {
    const bundle = getBundleContent();
    expect(bundle).toContain('https://api.example.com');
  });
});
```

---

### N-004: Middleware Security Bypass (CVE-2025-29927)

**Status:** RESOLVED in Next.js 15.2.3+, 14.2.25+, 13.5.9+, 12.3.5+ (all Next.js 16.x versions are safe)

**Symptom:** Middleware authentication could be bypassed; unauthorized requests reach protected routes

**Root Cause:** `x-middleware-subrequest` header could be forged to bypass middleware checks (in older Next.js versions)

**Detection:**
```typescript
// BUGGY PATTERN (now patched) - doesn't validate middleware header
export function middleware(request: NextRequest) {
  if (request.headers.get('x-middleware-subrequest')) {
    return NextResponse.next(); // Previously skipped auth check
  }

  const token = request.cookies.get('auth');
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}
```

**Safe Fix:**

**For Next.js 15.2.3+ and all 16.x versions:**
```typescript
// Vulnerability is patched; standard middleware patterns are safe
export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth');

  if (!token && !isPublicRoute(request.nextUrl.pathname)) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

function isPublicRoute(pathname: string): boolean {
  return ['/login', '/signup', '/'].includes(pathname);
}
```

**For older Next.js versions (12.3.4 and earlier):**
```typescript
// If stuck on older version, explicitly validate auth before checking internal headers
export function middleware(request: NextRequest) {
  // Check auth first, regardless of headers
  const token = request.cookies.get('auth');

  if (!token && !isPublicRoute(request.nextUrl.pathname)) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Validate subrequest header only after auth check
  if (request.headers.get('x-middleware-subrequest') === 'true') {
    const referer = request.headers.get('referer');
    if (!referer || !referer.startsWith(request.nextUrl.origin)) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
  }

  return NextResponse.next();
}

function isPublicRoute(pathname: string): boolean {
  return ['/login', '/signup', '/'].includes(pathname);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Trust any internal-looking headers
export function middleware(request: NextRequest) {
  // Attacker can forge this header
  if (request.headers.get('x-internal-request')) {
    return NextResponse.next();
  }

  // Auth check bypassed
  const user = getUser(request);
  if (!user) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}
```

**Regression Test:**
```typescript
describe('N-004: Middleware Security', () => {
  it('should not bypass auth with forged header', async () => {
    const response = await fetch('/protected', {
      headers: {
        'x-middleware-subrequest': 'true'
      }
    });

    expect(response.status).toBe(401);
  });

  it('should allow authenticated requests', async () => {
    const response = await fetch('/protected', {
      headers: {
        'cookie': 'auth=valid_token_123'
      }
    });

    expect(response.status).toBe(200);
  });
});
```

---
