# Security Guide

## Solo Developer Security Checklist

### Non-Negotiable (Do These First)
- [ ] HTTPS everywhere (automatic on Vercel/Netlify)
- [ ] Use auth service (Supabase Auth, Clerk, NextAuth) - NEVER build your own
- [ ] Hash passwords with bcrypt/Argon2 (if storing locally)
- [ ] Validate ALL input server-side (never trust client)
- [ ] Use parameterized queries/ORM (prevent SQL injection)
- [ ] Environment variables for secrets (never commit to git)
- [ ] Keep dependencies updated (`npm audit`, Dependabot)

### Important (Add These Soon)
- [ ] Rate limit API endpoints
- [ ] Generic error messages (don't expose internals)
- [ ] Enable logging/monitoring
- [ ] CORS configuration
- [ ] Content Security Policy headers
- [ ] Input sanitization for HTML output

## OWASP Top 10 (2021)

### A01: Broken Access Control
**What**: Users access/modify data they shouldn't
**Prevention**:
```typescript
// Always verify ownership server-side
async function getPost(postId: string, userId: string) {
  const post = await db.post.findUnique({ where: { id: postId } })
  if (post.authorId !== userId) {
    throw new Error('Forbidden')
  }
  return post
}
```

### A02: Cryptographic Failures
**What**: Weak encryption, exposed data
**Prevention**:
- Use TLS 1.2+ (HTTPS)
- Hash passwords with bcrypt/Argon2
- Never store plaintext passwords
- Encrypt sensitive data at rest

### A03: Injection (SQL, XSS, etc.)
**What**: Untrusted input executed as code
**Prevention**:
```typescript
// ❌ SQL Injection vulnerable
const query = `SELECT * FROM users WHERE id = '${userId}'`

// ✅ Parameterized query
const user = await prisma.user.findUnique({ where: { id: userId } })

// ✅ XSS - React auto-escapes by default
<div>{userInput}</div>  // Safe

// ❌ XSS - dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // Danger!
```

### A04: Insecure Design
**What**: Missing security in architecture
**Prevention**:
- Threat modeling from the start
- Security requirements in specs
- Don't rely on client-side validation

### A05: Security Misconfiguration
**What**: Default credentials, verbose errors
**Prevention**:
- Change default passwords
- Disable debug mode in production
- Remove unused features
- Generic error messages

### A06: Vulnerable Components
**What**: Using libraries with known CVEs
**Prevention**:
```bash
npm audit
npm audit fix

# Dependabot or Renovate for auto-updates
```

### A07: Authentication Failures
**What**: Weak passwords, broken sessions
**Prevention**:
- Use established auth service (Clerk, Supabase Auth, NextAuth)
- Implement 2FA/MFA
- Rate limit login attempts
- Secure session management

### A08: Software Integrity Failures
**What**: Untrusted code in CI/CD, unsigned updates
**Prevention**:
- Verify dependencies (lockfiles)
- Secure CI/CD pipelines
- Sign releases

### A09: Logging Failures
**What**: Can't detect breaches (average: 200 days to discover)
**Prevention**:
- Log security events
- Monitor for anomalies
- Alerting on suspicious activity

### A10: SSRF
**What**: Server makes requests to attacker-controlled URLs
**Prevention**:
- Validate/whitelist URLs
- Don't expose internal services
- Network segmentation

## Authentication Implementation

### Use Auth Services (Recommended)
```typescript
// Supabase Auth
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(url, key)

// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'secure-password'
})

// Get current user
const { data: { user } } = await supabase.auth.getUser()
```

### NextAuth.js
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'

export const { handlers, auth } = NextAuth({
  providers: [GitHub],
})

// Usage in Server Component
import { auth } from '@/auth'

export default async function Page() {
  const session = await auth()
  if (!session) redirect('/login')
  return <div>Welcome {session.user.name}</div>
}
```

## Row Level Security (Supabase)

```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own posts
CREATE POLICY "Users can view own posts"
ON posts FOR SELECT
USING (auth.uid() = user_id);

-- Users can only insert their own posts
CREATE POLICY "Users can insert own posts"
ON posts FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Users can only update their own posts
CREATE POLICY "Users can update own posts"
ON posts FOR UPDATE
USING (auth.uid() = user_id);
```

## Input Validation

### Zod (Recommended)
```typescript
import { z } from 'zod'

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  age: z.number().min(18).optional()
})

// Validate
const result = userSchema.safeParse(input)
if (!result.success) {
  return { error: result.error.flatten() }
}
const validData = result.data
```

### Server-Side Validation Pattern
```typescript
// app/api/users/route.ts
export async function POST(request: Request) {
  const body = await request.json()
  
  // Validate
  const result = userSchema.safeParse(body)
  if (!result.success) {
    return Response.json(
      { error: 'Validation failed', details: result.error.flatten() },
      { status: 400 }
    )
  }
  
  // Safe to use
  const user = await db.user.create({ data: result.data })
  return Response.json(user, { status: 201 })
}
```

## Rate Limiting

```typescript
// Using Upstash for serverless
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from '@upstash/redis'

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'), // 10 requests per 10 seconds
})

export async function POST(request: Request) {
  const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1'
  const { success } = await ratelimit.limit(ip)
  
  if (!success) {
    return Response.json({ error: 'Too many requests' }, { status: 429 })
  }
  
  // Continue with request
}
```

## Security Headers

```typescript
// next.config.js
const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
]

module.exports = {
  async headers() {
    return [{ source: '/(.*)', headers: securityHeaders }]
  }
}
```

## Secrets Management

```bash
# .env.local (NEVER commit)
DATABASE_URL="postgresql://..."
API_SECRET="super-secret-key"

# .env.example (commit this, with dummy values)
DATABASE_URL="postgresql://user:pass@localhost:5432/mydb"
API_SECRET="your-secret-here"

# .gitignore
.env
.env.local
.env*.local
```

### Vercel/Railway Environment Variables
- Set in dashboard, not in code
- Different values for Preview vs Production
- Mark sensitive as "Secret" (encrypted, not shown in logs)
