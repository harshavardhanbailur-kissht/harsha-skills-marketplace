# Frontend Framework Guide

## Quick Decision Matrix

| Situation | Recommendation |
|-----------|----------------|
| Just learning React | **Next.js** (industry standard) |
| Fastest learning curve | **Vue/Nuxt** (gentlest intro) |
| Best DX, smallest bundles | **Svelte/SvelteKit** |
| Need a job ASAP | **React/Next.js** (70% of jobs) |
| Building quickly, solo | **Next.js + Supabase** |
| Content site, minimal JS | **Astro** |

## Next.js 15+ (Recommended)

### Why Choose
- Largest ecosystem, most resources
- 70% of frontend job postings
- Server Components for performance
- Vercel's first-class support

### App Router Structure
```
app/
├── layout.tsx          # Root layout (required)
├── page.tsx            # Homepage
├── loading.tsx         # Loading UI
├── error.tsx           # Error boundary
├── (auth)/             # Route group (no URL segment)
│   ├── login/page.tsx
│   └── signup/page.tsx
├── dashboard/
│   ├── page.tsx
│   └── [id]/page.tsx   # Dynamic route
└── api/
    └── route.ts        # API endpoint
```

### Server vs Client Components
```typescript
// Server Component (default) - no directive needed
async function ServerComponent() {
  const data = await db.query() // Direct DB access OK
  return <div>{data}</div>
}

// Client Component - add directive
'use client'
import { useState } from 'react'
function ClientComponent() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

**Use Server for**: Data fetching, sensitive logic, large dependencies
**Use Client for**: Interactivity, browser APIs, state, event handlers

## CSS Strategy

### Tailwind CSS (Recommended)
```jsx
// Everything inline, readable, AI-friendly
<div className="rounded-lg shadow-md p-6 bg-white dark:bg-gray-900">
  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Title</h2>
</div>

// Responsive (mobile-first)
<div className="w-full md:w-1/2 lg:w-1/3">

// Conditional classes with cn/clsx
<div className={cn("base", isActive && "active", variant === "primary" && "primary")}>
```

### Component Libraries
| Library | Best For |
|---------|----------|
| **shadcn/ui** | Copy-paste, full control, Tailwind |
| **Radix UI** | Headless primitives |
| **Headless UI** | Simple, Tailwind team |

**Recommendation**: shadcn/ui - you own the code, customize everything

## State Management

### Decision Tree
```
Is data from API?
├─ Yes → TanStack Query
└─ No → Shared across components?
         ├─ No → useState
         └─ Yes → Changes frequently?
                  ├─ No → React Context
                  └─ Yes → Zustand
```

### TanStack Query (Server State)
```typescript
// Query
const { data, isPending, error } = useQuery({
  queryKey: ['todos'],
  queryFn: () => fetch('/api/todos').then(r => r.json())
})

// Mutation
const mutation = useMutation({
  mutationFn: (newTodo) => fetch('/api/todos', {
    method: 'POST',
    body: JSON.stringify(newTodo)
  }),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['todos'] })
})
```

### Zustand (Client State)
```typescript
import { create } from 'zustand'

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))

// Selective subscription (minimal re-renders)
const count = useStore((state) => state.count)
```

## TypeScript Essentials

### When to Use
- Project maintained 6+ months
- Working with APIs or complex data
- Team > 1 person
- Anything non-trivial

### Key Patterns
```typescript
// Props
interface ButtonProps {
  variant: 'primary' | 'secondary'
  onClick: () => void
  children: React.ReactNode
  disabled?: boolean
}

// API Response
interface User {
  id: string
  email: string
  createdAt: Date
}

// Type guard
function isUser(data: unknown): data is User {
  return typeof data === 'object' && data !== null && 'id' in data
}
```

## React Patterns (Kent C. Dodds)

### Compound Components
```tsx
<Select>
  <Select.Trigger>Choose</Select.Trigger>
  <Select.Options>
    <Select.Option value="a">A</Select.Option>
  </Select.Options>
</Select>
```

### Prop Getters
```typescript
function useToggle() {
  const [on, setOn] = useState(false)
  const getTogglerProps = (props = {}) => ({
    'aria-pressed': on,
    onClick: () => setOn(v => !v),
    ...props
  })
  return { on, getTogglerProps }
}
```

### State Reducer
```typescript
// Let users customize state logic
function useToggle({ reducer = toggleReducer } = {}) {
  const [state, dispatch] = useReducer(reducer, { on: false })
  // Users can pass custom reducer to override behavior
}
```
