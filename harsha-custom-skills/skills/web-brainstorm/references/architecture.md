# Architecture & Project Structure

## Next.js App Router Structure (Recommended)

```
src/
├── app/                    # App Router
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Homepage (/)
│   ├── loading.tsx         # Global loading
│   ├── error.tsx           # Global error boundary
│   ├── not-found.tsx       # 404 page
│   ├── (auth)/             # Route group (no URL impact)
│   │   ├── login/page.tsx  # /login
│   │   └── signup/page.tsx # /signup
│   ├── (dashboard)/        # Another route group
│   │   ├── layout.tsx      # Shared dashboard layout
│   │   ├── page.tsx        # /dashboard
│   │   └── settings/page.tsx
│   ├── api/                # API routes
│   │   └── users/route.ts  # /api/users
│   └── [slug]/page.tsx     # Dynamic route
│
├── components/             # Shared components
│   ├── ui/                 # Primitive UI (buttons, inputs)
│   └── features/           # Feature-specific
│
├── lib/                    # Utilities & helpers
│   ├── db.ts               # Database client
│   ├── auth.ts             # Auth utilities
│   └── utils.ts            # General utilities
│
├── hooks/                  # Custom React hooks
├── types/                  # TypeScript types
└── styles/                 # Global styles
```

## File Naming Conventions

```
components/
├── Button.tsx              # PascalCase for components
├── UserCard.tsx
├── ui/
│   ├── button.tsx          # lowercase for shadcn/ui style
│   └── card.tsx

lib/
├── utils.ts                # camelCase for utilities
├── formatDate.ts

hooks/
├── useAuth.ts              # use prefix for hooks
├── useLocalStorage.ts

types/
├── user.ts                 # lowercase for type files
├── api.ts
```

## Component Organization

### Feature-First (Recommended for Growing Apps)
```
features/
├── auth/
│   ├── components/
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── lib/
│   │   └── auth-utils.ts
│   └── types.ts
│
├── dashboard/
│   ├── components/
│   ├── hooks/
│   └── types.ts
```

### Flat (Good for Smaller Apps)
```
components/
├── LoginForm.tsx
├── SignupForm.tsx
├── Dashboard.tsx
├── UserCard.tsx
```

## Design Patterns

### Repository Pattern (Data Access)
```typescript
// lib/repositories/user.ts
export const userRepository = {
  findById: async (id: string) => {
    return db.user.findUnique({ where: { id } })
  },
  
  findByEmail: async (email: string) => {
    return db.user.findUnique({ where: { email } })
  },
  
  create: async (data: CreateUserInput) => {
    return db.user.create({ data })
  }
}

// Usage in API route or Server Action
const user = await userRepository.findById(id)
```

### Service Layer
```typescript
// lib/services/auth.ts
export const authService = {
  login: async (email: string, password: string) => {
    const user = await userRepository.findByEmail(email)
    if (!user) throw new Error('User not found')
    
    const valid = await verifyPassword(password, user.passwordHash)
    if (!valid) throw new Error('Invalid password')
    
    return createSession(user)
  }
}
```

### Facade Pattern (Simplify Complex APIs)
```typescript
// lib/facades/analytics.ts
export const analytics = {
  track: (event: string, data?: object) => {
    // Abstract away analytics provider details
    mixpanel.track(event, data)
    posthog.capture(event, data)
  }
}
```

## Colocation Principle

**Keep related code close together:**
```
// ❌ Don't scatter related files
components/UserCard.tsx
styles/UserCard.css
tests/UserCard.test.tsx
types/UserCard.ts

// ✅ Colocate related files
components/UserCard/
├── UserCard.tsx
├── UserCard.test.tsx
├── UserCard.module.css
└── types.ts
```

## Rule of Three

**Don't abstract until you have 3 instances:**
```typescript
// First time: just write the code inline
// Second time: note the duplication
// Third time: NOW extract to shared utility

// ❌ Premature abstraction
const formatUserName = (user) => `${user.first} ${user.last}`
// Used once, adds indirection

// ✅ Wait for patterns to emerge
// After seeing similar code 3 times, extract
```

## Import Organization

```typescript
// 1. React/framework imports
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

// 2. Third-party libraries
import { format } from 'date-fns'
import { toast } from 'sonner'

// 3. Internal absolute imports
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'

// 4. Relative imports
import { UserAvatar } from './UserAvatar'
import type { User } from './types'

// 5. Styles/assets
import styles from './Component.module.css'
```

## Barrel Files (Use Sparingly)

```typescript
// components/ui/index.ts
export { Button } from './button'
export { Card } from './card'
export { Input } from './input'

// Usage
import { Button, Card, Input } from '@/components/ui'

// ⚠️ Warning: Can hurt tree-shaking and bundle size
// Only use for small, cohesive modules
```

## Monorepo vs Polyrepo

### Monorepo When
- Shared code between projects
- Consistent tooling/standards
- Atomic changes across packages
- Small team

### Polyrepo When
- Independent deployment cycles
- Different teams own different repos
- Security/access boundaries needed
- Very large codebases

### Monorepo Tools
- **Turborepo** (Vercel) - Simple, fast
- **Nx** - Feature-rich, steep learning curve
- **pnpm workspaces** - Lightweight

## Database Schema Design

### Naming Conventions
```sql
-- Tables: plural, snake_case
users, blog_posts, order_items

-- Columns: snake_case
created_at, updated_at, user_id

-- Foreign keys: singular_table_id
user_id, post_id

-- Junction tables: alphabetical
post_tags (not tags_posts)
```

### Common Patterns
```sql
-- Soft delete
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

-- Audit timestamps
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW()

-- UUID primary keys
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```
