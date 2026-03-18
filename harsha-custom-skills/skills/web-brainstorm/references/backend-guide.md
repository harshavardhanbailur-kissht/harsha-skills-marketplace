# Backend & Database Guide

## Database Decision Matrix

| Situation | Recommendation |
|-----------|----------------|
| Solo dev, quick start | **Supabase** (PostgreSQL + Auth + Storage) |
| Mobile/embedded, simple | **SQLite** |
| High traffic production | **PostgreSQL** (self-managed or hosted) |
| Real-time sync critical | **Firebase** (if NoSQL is OK) |
| Need complex queries | **PostgreSQL** or **Supabase** |
| Graph relationships | **Neo4j** |
| Document-oriented | **MongoDB** |

## Supabase vs Firebase

### Choose Supabase When
- You want SQL and relational data
- Complex queries and joins needed
- Data ownership matters (open-source, can self-host)
- Predictable pricing preferred
- You know SQL or want to learn it
- Building SaaS, dashboards, CRUD apps

### Choose Firebase When
- Real-time sync is critical (chat, collaboration)
- Building mobile-first app
- Need push notifications built-in
- NoSQL document model fits your data
- Want zero database thinking
- Google Cloud integration needed

### Comparison
| Feature | Supabase | Firebase |
|---------|----------|----------|
| Database | PostgreSQL (relational) | Firestore (NoSQL) |
| Query | Full SQL, complex joins | Limited, no joins |
| Auth | Built-in, RLS integration | Mature, plug-and-play |
| Realtime | Via LISTEN/NOTIFY | Native, seamless |
| Pricing | Predictable, resource-based | Per read/write (can spike) |
| Lock-in | Open-source, portable | Proprietary |
| Storage | S3-compatible | Google Cloud |

## SQLite vs PostgreSQL

### SQLite: When to Use
- Mobile/desktop apps
- Single-server web apps <100 concurrent users
- Development/testing
- Read-heavy workloads
- Prototypes and MVPs
- Low-moderate traffic sites

### PostgreSQL: When to Use
- Multi-user concurrent writes
- Large datasets (GB to TB)
- Complex queries and analytics
- High-traffic production
- Advanced data types (JSONB, arrays, geo)
- Enterprise requirements

### Critical Warning
```
⚠️ DO NOT use SQLite for dev and PostgreSQL for production
Different type systems cause bugs that only appear in production!
Boolean: SQLite = 0/1, PostgreSQL = true/false/null
```

## Hosting Decision Matrix

| Type | Recommendation | Why |
|------|----------------|-----|
| Static site | **Vercel** or **Netlify** | Free, fast, simple |
| Next.js app | **Vercel** | First-class support |
| Full-stack | **Railway** or **Render** | Easy, good free tier |
| Need Docker | **Railway** or **Fly.io** | Container support |
| Budget critical | **Cloudflare Pages** | Generous free tier |
| Enterprise | **AWS/GCP** | Full control |

### Vercel
- Best for Next.js (they made it)
- Generous free tier
- Automatic deployments from Git
- Edge functions built-in
- Preview deployments for PRs

### Railway
- Best DX for full-stack
- PostgreSQL included
- Easy environment variables
- Good free tier ($5/month credit)
- Supports any Dockerfile

### Supabase (for BaaS needs)
- 50K MAU free tier
- PostgreSQL + Auth + Storage + Edge Functions
- Row Level Security
- Real-time subscriptions
- Auto-generated REST/GraphQL APIs

## API Design

### REST Best Practices
```
GET    /api/users          # List users
GET    /api/users/:id      # Get one user
POST   /api/users          # Create user
PUT    /api/users/:id      # Replace user
PATCH  /api/users/:id      # Update fields
DELETE /api/users/:id      # Delete user

# Filtering, sorting, pagination
GET /api/users?status=active&sort=-created_at&page=2&limit=20
```

### Next.js API Routes
```typescript
// app/api/users/route.ts
export async function GET() {
  const users = await db.user.findMany()
  return Response.json(users)
}

export async function POST(request: Request) {
  const body = await request.json()
  const user = await db.user.create({ data: body })
  return Response.json(user, { status: 201 })
}
```

### Server Actions (Next.js 14+)
```typescript
// In a Server Component or separate file
async function createUser(formData: FormData) {
  'use server'
  const name = formData.get('name')
  await db.user.create({ data: { name } })
  revalidatePath('/users')
}

// In form
<form action={createUser}>
  <input name="name" />
  <button type="submit">Create</button>
</form>
```

## ORM Choices

### Prisma (Recommended)
```typescript
// schema.prisma
model User {
  id    String @id @default(cuid())
  email String @unique
  posts Post[]
}

// Usage
const users = await prisma.user.findMany({
  where: { email: { contains: '@gmail.com' } },
  include: { posts: true }
})
```

### Drizzle (Lighter, SQL-like)
```typescript
const users = await db.select()
  .from(usersTable)
  .where(like(usersTable.email, '%@gmail.com%'))
```

| Aspect | Prisma | Drizzle |
|--------|--------|---------|
| Learning curve | Easier | Steeper |
| Bundle size | Larger | Smaller |
| Type safety | Excellent | Excellent |
| Raw SQL | Possible | Native |
| Migrations | Built-in | Built-in |

## Environment Variables

```bash
# .env.local (never commit!)
DATABASE_URL="postgresql://..."
SUPABASE_URL="https://..."
SUPABASE_ANON_KEY="eyJ..."

# Access in code
process.env.DATABASE_URL

# Next.js client exposure (prefix with NEXT_PUBLIC_)
NEXT_PUBLIC_APP_URL="https://myapp.com"
```

### Security Rules
1. Never commit `.env` files
2. Use `.env.example` with dummy values
3. Rotate leaked keys immediately
4. Use different values for dev/staging/prod
5. Server-only secrets should NEVER have `NEXT_PUBLIC_` prefix
