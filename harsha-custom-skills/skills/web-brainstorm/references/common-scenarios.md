# Common Application Scenarios

## SaaS Application

### Recommended Stack
```
Frontend: Next.js 15+ (App Router)
Database: Supabase (PostgreSQL)
Auth: Supabase Auth
Payments: Stripe
Email: Resend
Hosting: Vercel
```

### Core Features & Implementation

#### Multi-tenancy
```typescript
// Organization-based multi-tenancy
// schema.prisma
model Organization {
  id        String   @id @default(cuid())
  name      String
  members   Member[]
  projects  Project[]
}

model Member {
  userId String
  orgId  String
  role   Role     @default(MEMBER)
  user   User     @relation(fields: [userId], references: [id])
  org    Organization @relation(fields: [orgId], references: [id])
  @@id([userId, orgId])
}

// Row Level Security (Supabase)
CREATE POLICY "Users can only see their org's data"
ON projects FOR SELECT
USING (org_id IN (
  SELECT org_id FROM members WHERE user_id = auth.uid()
));
```

#### Subscription Billing (Stripe)
```typescript
// Webhook handler
export async function POST(req: Request) {
  const event = stripe.webhooks.constructEvent(
    await req.text(),
    req.headers.get('stripe-signature')!,
    process.env.STRIPE_WEBHOOK_SECRET!
  )
  
  switch (event.type) {
    case 'checkout.session.completed':
      await activateSubscription(event.data.object)
      break
    case 'customer.subscription.deleted':
      await deactivateSubscription(event.data.object)
      break
  }
  
  return Response.json({ received: true })
}
```

### Key Patterns
- Feature flags for gradual rollout
- Usage tracking for billing
- Admin dashboard for support
- Audit logging for compliance

## E-commerce

### Recommended Stack
```
Frontend: Next.js 15+ (App Router)
Database: Supabase or PlanetScale
Payments: Stripe
Search: Algolia or Typesense
Images: Cloudinary or Vercel Image
Hosting: Vercel
```

### Core Features

#### Product Catalog
```typescript
// Product with variants
model Product {
  id          String    @id @default(cuid())
  name        String
  description String
  images      String[]
  variants    Variant[]
  categories  Category[]
}

model Variant {
  id        String  @id @default(cuid())
  productId String
  name      String  // "Red / Large"
  sku       String  @unique
  price     Int     // Store in cents
  stock     Int
  product   Product @relation(fields: [productId], references: [id])
}
```

#### Cart (Client + Server)
```typescript
// Zustand store for cart
const useCart = create(
  persist(
    (set, get) => ({
      items: [],
      addItem: (variant, quantity = 1) => set(state => ({
        items: [...state.items, { variantId: variant.id, quantity }]
      })),
      removeItem: (variantId) => set(state => ({
        items: state.items.filter(item => item.variantId !== variantId)
      })),
      total: () => get().items.reduce((sum, item) => sum + item.price * item.quantity, 0)
    }),
    { name: 'cart-storage' }
  )
)
```

#### Checkout Flow
```typescript
// Create Stripe Checkout Session
export async function POST(req: Request) {
  const { items } = await req.json()
  
  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: items.map(item => ({
      price_data: {
        currency: 'usd',
        product_data: { name: item.name },
        unit_amount: item.price
      },
      quantity: item.quantity
    })),
    success_url: `${origin}/order/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}/cart`
  })
  
  return Response.json({ url: session.url })
}
```

## Blog / Content Site

### Recommended Stack
```
Framework: Astro (or Next.js)
Content: MDX or Contentlayer
Styling: Tailwind
Comments: Giscus (GitHub Discussions)
Analytics: Plausible or Umami
Hosting: Vercel or Cloudflare Pages
```

### MDX Setup (Next.js)
```typescript
// app/blog/[slug]/page.tsx
import { allPosts } from 'contentlayer/generated'

export async function generateStaticParams() {
  return allPosts.map(post => ({ slug: post.slug }))
}

export default function Post({ params }) {
  const post = allPosts.find(p => p.slug === params.slug)
  return (
    <article className="prose dark:prose-invert">
      <h1>{post.title}</h1>
      <MDXContent code={post.body.code} />
    </article>
  )
}
```

### SEO Optimization
```typescript
// Generate metadata
export function generateMetadata({ params }) {
  const post = allPosts.find(p => p.slug === params.slug)
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
      images: [post.image]
    }
  }
}
```

## Real-time Dashboard

### Recommended Stack
```
Frontend: Next.js + TanStack Query
Backend: Supabase (PostgreSQL + Realtime)
Charts: Recharts or Tremor
Styling: Tailwind + shadcn/ui
Hosting: Vercel
```

### Real-time Updates
```typescript
// Supabase Realtime subscription
useEffect(() => {
  const channel = supabase
    .channel('metrics')
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table: 'metrics' },
      (payload) => {
        queryClient.invalidateQueries({ queryKey: ['metrics'] })
      }
    )
    .subscribe()
  
  return () => { supabase.removeChannel(channel) }
}, [])
```

### Dashboard Layout
```tsx
export default function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen">
      <Sidebar className="w-64 border-r" />
      <main className="flex-1 overflow-auto p-6">
        {children}
      </main>
    </div>
  )
}
```

## Authentication Flow

### Email/Password + OAuth
```typescript
// Supabase Auth in Next.js
'use client'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'

export function AuthForm() {
  const supabase = createClientComponentClient()
  
  const signInWithEmail = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) toast.error(error.message)
  }
  
  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${origin}/auth/callback` }
    })
  }
  
  // Form UI...
}
```

### Protected Routes (Middleware)
```typescript
// middleware.ts
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })
  const { data: { session } } = await supabase.auth.getSession()
  
  const isProtected = req.nextUrl.pathname.startsWith('/dashboard')
  
  if (isProtected && !session) {
    return NextResponse.redirect(new URL('/login', req.url))
  }
  
  return res
}

export const config = {
  matcher: ['/dashboard/:path*']
}
```

## API-First Architecture

### REST API with Next.js
```typescript
// app/api/v1/[...path]/route.ts
import { Hono } from 'hono'
import { handle } from 'hono/vercel'

const app = new Hono().basePath('/api/v1')

app.get('/users', async (c) => {
  const users = await db.user.findMany()
  return c.json(users)
})

app.post('/users', async (c) => {
  const body = await c.req.json()
  const user = await db.user.create({ data: body })
  return c.json(user, 201)
})

export const GET = handle(app)
export const POST = handle(app)
```

### tRPC for Type-Safe APIs
```typescript
// server/routers/user.ts
export const userRouter = router({
  getById: publicProcedure
    .input(z.string())
    .query(async ({ input }) => {
      return db.user.findUnique({ where: { id: input } })
    }),
  
  create: protectedProcedure
    .input(createUserSchema)
    .mutation(async ({ input, ctx }) => {
      return db.user.create({ data: { ...input, createdBy: ctx.user.id } })
    })
})

// Client usage (fully typed!)
const user = await trpc.user.getById.query('user-123')
```
