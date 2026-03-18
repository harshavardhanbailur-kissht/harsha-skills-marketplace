# Quick Decision Matrices

## Frontend Framework

| Factor | Next.js | Vue/Nuxt | Svelte | Astro |
|--------|---------|----------|--------|-------|
| Job market | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Learning curve | Medium | Easy | Easy | Easy |
| Bundle size | Medium | Medium | Small | Tiny |
| Dev satisfaction | High | High | Highest | High |
| Ecosystem | Huge | Large | Growing | Growing |
| Best for | Full-stack apps | Gradual adoption | Max performance | Content sites |

**Default choice**: Next.js (unless specific reason otherwise)

## Database

| Factor | Supabase | Firebase | PlanetScale | SQLite |
|--------|----------|----------|-------------|--------|
| Data model | Relational | Document | Relational | Relational |
| Query power | Full SQL | Limited | Full SQL | Full SQL |
| Free tier | 50K MAU | Spark (generous) | 5GB | Free |
| Real-time | Good | Excellent | No | No |
| Vendor lock-in | Low (OSS) | High | Medium | None |
| Auth included | Yes | Yes | No | No |
| Best for | Most apps | Real-time apps | Scale focus | Single server |

**Default choice**: Supabase (PostgreSQL + Auth + Storage combo)

## Hosting

| Factor | Vercel | Railway | Render | Cloudflare |
|--------|--------|---------|--------|------------|
| Next.js support | Best | Good | Good | Limited |
| Free tier | Generous | $5/mo credit | 750 hrs | Generous |
| Docker support | No | Yes | Yes | No |
| Database | Via integrations | Built-in | Built-in | D1 (beta) |
| Edge functions | Yes | No | No | Yes |
| Best for | Next.js apps | Full-stack | General | Static/Edge |

**Default choice**: Vercel for Next.js, Railway for full-stack with DB

## State Management

| Factor | TanStack Query | Zustand | Redux Toolkit | Context |
|--------|----------------|---------|---------------|---------|
| Server state | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Client state | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Bundle size | ~12KB | ~1KB | ~11KB | 0 |
| Boilerplate | Low | Minimal | Medium | Low |
| DevTools | Excellent | Good | Excellent | Basic |
| Learning curve | Easy | Very easy | Medium | Easy |

**Default choice**: TanStack Query for server state, Zustand for client state

## CSS Approach

| Factor | Tailwind | CSS Modules | styled-components | Plain CSS |
|--------|----------|-------------|-------------------|-----------|
| Setup | Easy | Built-in | Medium | None |
| Bundle size | Tiny (purged) | Small | Larger | Small |
| Learning curve | Medium | Easy | Medium | Varies |
| AI friendliness | Excellent | Good | Good | Good |
| Component libs | shadcn/ui | Manual | Many | Manual |

**Default choice**: Tailwind + shadcn/ui

## Auth Solution

| Factor | Supabase Auth | Clerk | NextAuth | Auth0 |
|--------|---------------|-------|----------|-------|
| Free tier | 50K MAU | 10K MAU | Free | 7K MAU |
| Setup | Easy | Easiest | Medium | Medium |
| Customization | High | Medium | High | High |
| Social providers | Many | Many | Many | Many |
| UI components | Basic | Polished | None | Polished |

**Default choice**: Supabase Auth if using Supabase DB, Clerk for best DX

## ORM

| Factor | Prisma | Drizzle | Kysely |
|--------|--------|---------|--------|
| Type safety | Excellent | Excellent | Excellent |
| Bundle size | Larger | Smaller | Small |
| Learning curve | Easy | Medium | Medium |
| Raw SQL | Possible | Native | Native |
| Migrations | Built-in | Built-in | External |
| Edge compatible | Limited | Yes | Yes |

**Default choice**: Prisma for most, Drizzle for edge/smaller bundles

## Form Library

| Factor | React Hook Form | Formik | Native |
|--------|-----------------|--------|--------|
| Bundle size | ~9KB | ~15KB | 0 |
| Performance | Excellent | Good | Varies |
| Validation | Via Zod/Yup | Built-in | Manual |
| Learning curve | Medium | Medium | Easy |

**Default choice**: React Hook Form + Zod

## Testing

| Factor | Vitest | Jest | Playwright | Cypress |
|--------|--------|------|------------|---------|
| Type | Unit/Integration | Unit/Integration | E2E | E2E |
| Speed | Fast | Medium | Fast | Medium |
| Setup | Easy | Easy | Easy | Easy |
| Browser testing | Via happy-dom | Via jsdom | Real browsers | Real browsers |

**Default choice**: Vitest for unit tests, Playwright for E2E

## Animation

| Factor | Framer Motion | CSS | GSAP | React Spring |
|--------|---------------|-----|------|--------------|
| Bundle size | ~30KB | 0 | ~60KB | ~25KB |
| Ease of use | Easy | Medium | Medium | Medium |
| Power | High | Medium | Highest | High |
| Best for | UI animations | Simple | Complex | Physics |

**Default choice**: CSS for simple, Framer Motion for complex

## Quick Stack Recipes

### SaaS MVP
```
Next.js + Supabase + Tailwind + shadcn/ui + Stripe
```

### Content/Blog
```
Astro + MDX + Tailwind + Vercel
```

### E-commerce
```
Next.js + Supabase + Stripe + Tailwind
```

### Real-time App
```
Next.js + Firebase/Supabase Realtime + Tailwind
```

### Dashboard
```
Next.js + TanStack Query + Recharts + Tailwind + shadcn/ui
```

### Mobile-first
```
React Native/Expo + Supabase + NativeWind
```
