# Performance Optimization Guide

## Core Web Vitals Targets

| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| LCP (Largest Contentful Paint) | <2.5s | 2.5-4s | >4s |
| INP (Interaction to Next Paint) | <200ms | 200-500ms | >500ms |
| CLS (Cumulative Layout Shift) | <0.1 | 0.1-0.25 | >0.25 |

## Quick Wins (Do These First)

### 1. Image Optimization
```tsx
// ✅ Use Next.js Image (automatic optimization)
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero"
  width={800}
  height={600}
  priority  // For above-fold images
  placeholder="blur"
  blurDataURL={blurDataUrl}
/>

// Generates WebP/AVIF, responsive sizes, lazy loading
```

### 2. Font Optimization
```tsx
// ✅ Use next/font (zero layout shift)
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function Layout({ children }) {
  return <body className={inter.className}>{children}</body>
}
```

### 3. Code Splitting
```tsx
// ✅ Dynamic imports for heavy components
import dynamic from 'next/dynamic'

const Chart = dynamic(() => import('./Chart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false  // Client-only component
})
```

## Next.js Specific Optimizations

### Server Components (Default in App Router)
```tsx
// ✅ Server Component - no JS shipped to client
async function UserList() {
  const users = await db.user.findMany() // Server-side fetch
  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  )
}

// Only add 'use client' when you NEED browser APIs
```

### Streaming with Suspense
```tsx
// Show content as it loads
export default function Page() {
  return (
    <>
      <Header /> {/* Renders immediately */}
      
      <Suspense fallback={<Loading />}>
        <SlowComponent /> {/* Streams when ready */}
      </Suspense>
      
      <Suspense fallback={<Loading />}>
        <AnotherSlowComponent />
      </Suspense>
    </>
  )
}
```

### Parallel Data Fetching
```tsx
// ❌ Sequential (slow)
const user = await getUser(id)
const posts = await getPosts(id)
const comments = await getComments(id)

// ✅ Parallel (fast)
const [user, posts, comments] = await Promise.all([
  getUser(id),
  getPosts(id),
  getComments(id)
])
```

## React Performance

### Prevent Unnecessary Re-renders
```tsx
// ✅ React.memo for pure components
const UserCard = memo(function UserCard({ user }) {
  return <div>{user.name}</div>
})

// ✅ useMemo for expensive calculations
const expensiveValue = useMemo(
  () => computeExpensiveValue(data),
  [data]
)

// ✅ useCallback for stable function references
const handleClick = useCallback(() => {
  doSomething(id)
}, [id])
```

### Virtualization for Long Lists
```tsx
// Use react-window or @tanstack/react-virtual
import { FixedSizeList } from 'react-window'

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={400}
      itemCount={items.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  )
}
```

### Avoid Prop Drilling Re-renders
```tsx
// ✅ Zustand with selective subscriptions
const name = useStore(state => state.user.name) // Only re-renders on name change

// ❌ Context causes all consumers to re-render
const { user } = useContext(UserContext) // Re-renders on ANY context change
```

## Database Query Optimization

### Use Indexes
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_created ON posts(created_at DESC);
```

### Select Only Needed Fields
```typescript
// ❌ Fetching everything
const users = await db.user.findMany()

// ✅ Select only what you need
const users = await db.user.findMany({
  select: { id: true, name: true, email: true }
})
```

### Pagination
```typescript
// Cursor-based (better for large datasets)
const posts = await db.post.findMany({
  take: 20,
  cursor: lastPostId ? { id: lastPostId } : undefined,
  orderBy: { createdAt: 'desc' }
})

// Offset-based (simpler, worse for large datasets)
const posts = await db.post.findMany({
  skip: (page - 1) * 20,
  take: 20
})
```

### Avoid N+1 Queries
```typescript
// ❌ N+1 Problem
const posts = await db.post.findMany()
for (const post of posts) {
  const author = await db.user.findUnique({ where: { id: post.authorId } })
}

// ✅ Include related data
const posts = await db.post.findMany({
  include: { author: true }
})
```

## Caching Strategies

### TanStack Query (Client-Side)
```typescript
const { data } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
  staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
  gcTime: 30 * 60 * 1000,   // Keep in cache for 30 minutes
})
```

### Next.js Data Cache
```typescript
// Cache for 1 hour
fetch(url, { next: { revalidate: 3600 } })

// No cache (always fresh)
fetch(url, { cache: 'no-store' })

// Revalidate on demand
import { revalidatePath, revalidateTag } from 'next/cache'
revalidatePath('/posts')
revalidateTag('posts')
```

### HTTP Caching Headers
```typescript
// API route with caching
export async function GET() {
  const data = await fetchData()
  
  return Response.json(data, {
    headers: {
      'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400'
    }
  })
}
```

## Bundle Size Optimization

### Analyze Bundle
```bash
# Next.js bundle analyzer
npm install @next/bundle-analyzer
ANALYZE=true npm run build
```

### Tree Shaking Tips
```typescript
// ❌ Imports entire library
import _ from 'lodash'

// ✅ Import specific functions
import debounce from 'lodash/debounce'

// ❌ Barrel imports can hurt tree shaking
import { Button, Card, Modal } from '@/components'

// ✅ Direct imports when needed
import { Button } from '@/components/ui/button'
```

### Lazy Load Heavy Dependencies
```tsx
// Load heavy libraries only when needed
const Chart = dynamic(() => import('recharts').then(mod => mod.LineChart))
```

## Measuring Performance

### Lighthouse
```bash
# CLI
npx lighthouse https://yoursite.com --view

# Chrome DevTools > Lighthouse tab
```

### React DevTools Profiler
- Record interactions
- Identify slow components
- Find unnecessary re-renders

### Web Vitals in Production
```typescript
// Track real user metrics
import { onCLS, onINP, onLCP } from 'web-vitals'

onCLS(metric => sendToAnalytics(metric))
onINP(metric => sendToAnalytics(metric))
onLCP(metric => sendToAnalytics(metric))
```

## Performance Budget

Set limits and enforce them:
```json
// package.json
{
  "bundlesize": [
    { "path": ".next/static/chunks/*.js", "maxSize": "150 kB" },
    { "path": ".next/static/css/*.css", "maxSize": "50 kB" }
  ]
}
```
