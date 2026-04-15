# Anti-Patterns & Common Mistakes

## Architecture Anti-Patterns

### Premature Optimization
```
❌ "We might need microservices later"
❌ "Let's add caching from day one"
❌ "We should use Kubernetes for scalability"

✅ Build the simplest thing that works
✅ Measure before optimizing
✅ Scale when you have traffic problems
```

### Resume-Driven Development
```
❌ Using GraphQL because it's cool (when REST is fine)
❌ Implementing event sourcing for a CRUD app
❌ Using Redis for a feature that works fine in-memory

✅ Choose boring technology
✅ Match complexity to actual needs
✅ Add complexity only when required
```

### Second System Syndrome
```
❌ "V2 will fix everything"
❌ Rewriting from scratch instead of iterating
❌ Adding every feature users might want

✅ Iterate on what exists
✅ Refactor incrementally
✅ Ship small, get feedback
```

## React Anti-Patterns

### Prop Drilling (Excessive)
```tsx
// ❌ Passing props through many levels
<App theme={theme}>
  <Layout theme={theme}>
    <Sidebar theme={theme}>
      <Navigation theme={theme}>
        <ThemeToggle theme={theme} />
      </Navigation>
    </Sidebar>
  </Layout>
</App>

// ✅ Use Context for widely-needed data
const ThemeContext = createContext()
const theme = useContext(ThemeContext)
```

### Huge Components
```tsx
// ❌ 500+ line component doing everything
function Dashboard() {
  // Auth logic
  // Data fetching
  // Form handling
  // Chart rendering
  // Table rendering
  // Modal management
  // ... 500 more lines
}

// ✅ Compose from smaller, focused components
function Dashboard() {
  return (
    <>
      <DashboardHeader />
      <MetricsOverview />
      <DataTable />
      <ChartSection />
    </>
  )
}
```

### State in Wrong Place
```tsx
// ❌ Global state for local concerns
const useStore = create((set) => ({
  isModalOpen: false,  // Should be local!
  selectedItem: null,  // Should be local!
}))

// ✅ Keep state as local as possible
function Component() {
  const [isModalOpen, setIsModalOpen] = useState(false)
}
```

### useEffect Abuse
```tsx
// ❌ Deriving state in useEffect
const [items, setItems] = useState([])
const [filteredItems, setFilteredItems] = useState([])

useEffect(() => {
  setFilteredItems(items.filter(i => i.active))
}, [items])

// ✅ Derive during render
const [items, setItems] = useState([])
const filteredItems = items.filter(i => i.active)

// Or with useMemo if expensive
const filteredItems = useMemo(
  () => items.filter(i => i.active),
  [items]
)
```

### Unnecessary Re-renders
```tsx
// ❌ Creating new objects/functions every render
function Parent() {
  return (
    <Child 
      style={{ color: 'red' }}  // New object every render
      onClick={() => doSomething()}  // New function every render
    />
  )
}

// ✅ Stable references
const style = useMemo(() => ({ color: 'red' }), [])
const onClick = useCallback(() => doSomething(), [])
```

## Database Anti-Patterns

### N+1 Queries
```typescript
// ❌ One query per item
const posts = await db.post.findMany()
for (const post of posts) {
  const author = await db.user.findUnique({ where: { id: post.authorId } })
}

// ✅ Single query with join
const posts = await db.post.findMany({
  include: { author: true }
})
```

### No Indexes
```sql
-- ❌ Slow queries without indexes
SELECT * FROM users WHERE email = 'user@example.com';

-- ✅ Add index on frequently queried columns
CREATE INDEX idx_users_email ON users(email);
```

### SELECT *
```typescript
// ❌ Fetching all columns
const users = await db.user.findMany()

// ✅ Select only needed fields
const users = await db.user.findMany({
  select: { id: true, name: true, email: true }
})
```

### Storing Files in Database
```
❌ Storing images as BLOBs in database
❌ Large text files in database columns

✅ Use object storage (S3, Supabase Storage, Cloudinary)
✅ Store only the URL/path in database
```

## API Anti-Patterns

### Exposing Internal IDs
```typescript
// ❌ Sequential IDs reveal business info
GET /api/users/1234  // Competitor knows you have ~1234 users

// ✅ Use UUIDs or obfuscated IDs
GET /api/users/550e8400-e29b-41d4-a716-446655440000
```

### Inconsistent Responses
```typescript
// ❌ Different shapes for same resource
{ user: { name: "John" } }
{ data: { user_name: "John" } }

// ✅ Consistent response format
{ data: { id: "...", name: "John", ... }, meta: { ... } }
```

### No Rate Limiting
```
❌ API open to abuse
❌ No protection against brute force

✅ Rate limit by IP and user
✅ Return 429 Too Many Requests
```

### Over-fetching / Under-fetching
```typescript
// ❌ Returning entire user for profile card
// ❌ Requiring 5 requests for one page

// ✅ Purpose-built endpoints or GraphQL
// ✅ Include related data when commonly needed together
```

## Security Anti-Patterns

### Client-Side Validation Only
```typescript
// ❌ Only validating on client
if (formData.email.includes('@')) { submit() }

// ✅ ALWAYS validate server-side
export async function POST(req: Request) {
  const body = await req.json()
  const result = schema.safeParse(body)
  if (!result.success) return Response.json({ error: 'Invalid' }, { status: 400 })
}
```

### Secrets in Frontend
```typescript
// ❌ API keys in client code
const stripe = new Stripe('sk_live_<REDACTED>')  // NEVER DO THIS

// ✅ Secrets only on server
// Use STRIPE_SECRET_KEY env var, accessed only in API routes
```

### Trusting User Input
```typescript
// ❌ Using user input directly
const query = `SELECT * FROM users WHERE id = '${userId}'`

// ✅ Parameterized queries
const user = await db.user.findUnique({ where: { id: userId } })
```

### Rolling Your Own Auth
```
❌ Building custom auth system
❌ Storing passwords in plain text
❌ Custom session management

✅ Use established auth services
✅ Supabase Auth, Clerk, NextAuth, Auth0
```

## Performance Anti-Patterns

### Loading Everything Upfront
```tsx
// ❌ Importing everything
import { Chart, Table, Modal, DatePicker, ColorPicker } from 'heavy-lib'

// ✅ Dynamic imports
const Chart = dynamic(() => import('heavy-lib').then(m => m.Chart))
```

### Images Without Optimization
```tsx
// ❌ Unoptimized images
<img src="/huge-image.jpg" />

// ✅ Optimized with Next.js Image
<Image src="/image.jpg" width={800} height={600} />
```

### No Caching
```
❌ Fetching same data repeatedly
❌ No HTTP cache headers
❌ Full page reload for data refresh

✅ TanStack Query for client caching
✅ Proper cache headers
✅ Incremental updates
```

## Code Quality Anti-Patterns

### Magic Numbers/Strings
```typescript
// ❌ Magic values
if (status === 1) { ... }
const timeout = 86400000

// ✅ Named constants
const STATUS = { ACTIVE: 1, INACTIVE: 0 }
const ONE_DAY_MS = 24 * 60 * 60 * 1000
```

### Commented-Out Code
```typescript
// ❌ Dead code in version control
// function oldImplementation() { ... }
// if (feature.enabled) { ... }

// ✅ Delete it - git has history
```

### Inconsistent Naming
```typescript
// ❌ Mixed conventions
const user_name = '...'
const userEmail = '...'
const USER_AGE = '...'

// ✅ Consistent conventions
const userName = '...'
const userEmail = '...'
const userAge = '...'
```

### God Files
```
❌ utils.ts with 2000 lines
❌ helpers.ts with everything
❌ index.ts re-exporting the world

✅ Small, focused modules
✅ Clear responsibilities
✅ Easy to find and modify
```

## Process Anti-Patterns

### No Version Control
```
❌ Coding directly on server
❌ Manual file uploads
❌ No git history

✅ Git for everything
✅ Pull requests for review
✅ Automated deployments
```

### No Error Tracking
```
❌ console.log in production
❌ No alerts for failures
❌ Finding out from users

✅ Error tracking (Sentry, etc.)
✅ Alerting on failures
✅ Proactive monitoring
```

### Big Bang Releases
```
❌ Months of work deployed at once
❌ "We'll test after launch"
❌ No rollback plan

✅ Deploy frequently
✅ Feature flags
✅ Incremental rollouts
```
