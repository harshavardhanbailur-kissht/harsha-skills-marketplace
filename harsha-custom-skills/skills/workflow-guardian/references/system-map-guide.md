# System Map Guide for Workflow Guardian

**Purpose**: Before modifying any application, generate a comprehensive System Map that catalogs every component, integration point, and dependency. This prevents breakages when adding or changing features.

**When to use**: At the start of any feature development, refactoring, or architectural change.

---

## 1. Component Inventory Protocol

### Objective
Catalog every UI, utility, and service component to identify all locations that must change when adding a feature.

### Instructions

**Step 1: Search for all components**
```bash
find src -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" \)
```

**Step 2: For each component, record:**

| Field | Instructions | Example |
|-------|--------------|---------|
| **Name** | Component or function name | `TicketCard`, `useTickets`, `formatDate` |
| **Path** | Relative path in src/ | `src/components/TicketCard.tsx` |
| **Type** | Component / Hook / Utility / Context | `Component` |
| **Props** | List parameter names and types | `ticket: Ticket`, `onClaim: () => void` |
| **Imports** | Who imports this file? | `AdminView.tsx`, `ProductSupportView.tsx` |
| **Renders** | What does it render? (for UI components) | Returns JSX with ticket details |
| **Exports** | Named or default export? | `export default TicketCard` |
| **Dependencies** | External libraries and internal imports | `hooks/useTickets`, `tailwind`, `lucide-react` |

### Checklist Format

```markdown
## Component Inventory

### UI Components
- [ ] Header
  - Path: src/components/Header.tsx
  - Imports: useAuth, useCommandPalette
  - Renders: Navigation bar, search box, user menu
  - Props: none
  - Exported as: default

- [ ] TicketCard
  - Path: src/components/TicketCard.tsx
  - Imports: TicketCardType, useTimer, formatDate, tailwind classes
  - Renders: Ticket details card with status badge, TAT timer
  - Props: ticket, onClaim, onResolve
  - Exported as: default

### Custom Hooks
- [ ] useTickets
  - Path: src/hooks/useTickets.ts
  - Imports: supabase client, Ticket type, useCallback
  - Returns: { tickets, loading, error, claimTicket, resolveTicket, ... }
  - Used by: AdminView, ProductSupportView, TicketForm
  - Exported as: named

### Context Providers
- [ ] AuthContext
  - Path: src/context/AuthContext.tsx
  - Provides: { currentUser, login, logout }
  - Consumed by: App, Header, AdminView, ProtectedRoute
  - Exported as: [ AuthProvider, useAuth ]
```

### Why This Matters
When adding a new field (e.g., "priority"), the inventory shows:
- TicketCard imports the Ticket type → must update type definition
- TicketForm renders a form field → must add input
- AdminView consumes useTickets → might need new filter/sort
- ResolveModal is only imported by AdminView → safe to modify

---

## 2. Route Mapping Protocol

### Objective
Extract all application routes and how they're protected, wrapped, and what components they render.

### Instructions

**Step 1: Identify routing framework**
- React Router: Look for `<Routes>`, `<Route>`, `navigate()`
- Next.js: Look for `app/` folder structure, `[slug]` syntax
- Custom routing: Search for conditional `currentPage`, `view`, `section` state
- No routing: Document single-page UI state transitions

**Step 2: For each route, record:**

| Field | Instructions | Example |
|-------|--------------|---------|
| **Path** | URL path pattern | `/admin`, `/tickets/:id`, `/auth/login` |
| **Component** | What renders at this path | `AdminView`, `TicketDetail`, `LoginScreen` |
| **Guards** | Auth/role checks before render | `requireAuth`, `requireRole('admin')` |
| **Params** | Dynamic route parameters | `id`, `status`, `userId` |
| **Layout Wrapper** | Parent component that wraps this route | `MainLayout`, `AppContent` |
| **State dependency** | Does route depend on client-side state? | `currentUser.role`, `selectedTab` |

### Example Output

```markdown
## Route Map

### React Router Setup (App.tsx:15-45)
```tsx
<Routes>
  <Route path="/login" element={<LoginScreen />} />
  <Route path="/admin" element={<ProtectedRoute role="admin"><AdminView /></ProtectedRoute>} />
  <Route path="/support" element={<ProtectedRoute role="product_support"><SupportView /></ProtectedRoute>} />
  <Route path="/" element={<Navigate to="/admin" />} />
</Routes>
```

### Route Inventory

| Path | Component | Guards | Params | Layout | Notes |
|------|-----------|--------|--------|--------|-------|
| `/login` | LoginScreen | none | none | LayoutDefault | Always accessible |
| `/admin` | AdminView | requireRole('admin') | none | AppContent | Pull-model ticket management |
| `/support` | SupportView | requireRole('product_support') | none | AppContent | Create & track own tickets |
| `/settings` | SettingsPage | requireAuth() | none | AppContent | User preferences |
| `*` | NotFound | none | none | LayoutDefault | 404 fallback |

### Protected Route Implementation (ProtectedRoute.tsx:1-20)
- Checks: `currentUser.role === requiredRole`
- Failure: Redirects to `/login`
- Location: src/components/ProtectedRoute.tsx

### If changing routes, update:
1. App.tsx (route definitions)
2. Header.tsx (navigation links)
3. CommandPalette.tsx (keyboard commands)
4. Analytics/logging if path tracking exists
```

### Why This Matters
When adding a new page (e.g., "Analytics Report"):
- Need a new `<Route>` in App.tsx
- Need a new nav link in Header.tsx
- If admin-only, must wrap with `<ProtectedRoute role="admin">`
- If old routes still reference old component, might cause dead links

---

## 3. Design Language Extraction

### Objective
Document the design system so new components look and feel consistent.

### Instructions

**Step 1: Color Palette**

Find colors in these locations (in order of priority):
1. `tailwind.config.js` or `tailwind.config.ts` → custom theme colors
2. CSS files (`.css`, `.scss`) → CSS variables `--color-*`
3. Component files → inline color values (hex, rgb, Tailwind classes)

**Step 2: Record each color:**

```markdown
## Color Palette

**Primary Navy**: #0f1c7a
  - Source: tailwind.config.js (theme.colors.navy)
  - Tailwind class: `text-[#0f1c7a]` (custom value)
  - Usage: Primary buttons, active states, logo
  - Components: Header.tsx, Button.tsx (variant="primary")

**Accent Yellow**: #fbbf24 (Tailwind amber-400)
  - Source: default Tailwind palette
  - Tailwind class: `bg-yellow-400`, `text-yellow-400`
  - Usage: Open ticket badges, warnings
  - Components: StatusBadge.tsx, AlertBox.tsx

**Success Green**: #10b981 (Tailwind emerald-500)
  - Tailwind class: `text-green-500`
  - Usage: Resolved tickets, confirmation messages
  - Components: TicketCard.tsx (resolved state), ToastMessage.tsx

**Semantic Colors**:
  - Error/Danger: #ef4444 (red-500)
  - Warning: #f59e0b (amber-500)
  - Info: #3b82f6 (blue-500)
```

**Step 3: Typography Scale**

```markdown
## Typography System

**Font Family**: Inter (from @fontsource/inter)
  - @import in src/index.css
  - Applied globally via `font-family: 'Inter', sans-serif`

**Font Sizes & Usage**:
  - Heading 1: `text-2xl` (32px) - Page titles
  - Heading 2: `text-lg` (18px) - Section headers
  - Body: `text-base` (16px) - Main content, labels
  - Small: `text-sm` (14px) - Secondary text, hints
  - Tiny: `text-xs` (12px) - Captions, metadata

**Font Weights**:
  - Bold: `font-bold` (700) - Headings, emphasis
  - Semibold: `font-semibold` (600) - Subheadings, labels
  - Normal: `font-normal` (400) - Body text
  - Light: `font-light` (300) - Disabled text

**Line Heights**:
  - Tight: `leading-tight` (1.25) - Headings
  - Normal: `leading-normal` (1.5) - Body
  - Relaxed: `leading-relaxed` (1.625) - Descriptions
```

**Step 4: Spacing System**

```markdown
## Spacing System

**Base Unit**: 4px (Tailwind default)

**Common Gaps**:
  - gap-2 (8px) - Tight horizontal spacing
  - gap-3 (12px) - Component groups
  - gap-4 (16px) - Section spacing
  - gap-6 (24px) - Page sections

**Padding** (horizontal x vertical):
  - px-3 py-2 (12px x 8px) - Small buttons, inputs
  - px-4 py-3 (16px x 12px) - Standard buttons, cards
  - px-6 py-4 (24px x 16px) - Large sections, modals

**Margins**:
  - mb-2, mb-3, mb-4 - Between elements
  - mt-6 - Section breaks
```

**Step 5: Component Patterns**

```markdown
## UI Component Patterns

### Button Variants
- **Primary**: Navy background, white text (action-oriented)
  ```tsx
  <button className="bg-[#0f1c7a] text-white px-4 py-3 rounded">Action</button>
  ```
  Uses: ClaimButton, ResolveButton, SubmitForm

- **Secondary**: Border, dark text (less prominent)
  ```tsx
  <button className="border border-gray-300 text-gray-700 px-4 py-3 rounded">Cancel</button>
  ```
  Uses: CancelButton, SecondaryAction

- **Danger**: Red background (destructive actions)
  Uses: DeleteButton, RejectButton

### Badge Types
- **Status Badge**: Colored background + text
  - open: yellow-400 background
  - claimed: blue-500 background
  - resolved: green-500 background

- **Issue Type Badge**: Icon + label
  - bug: red icon + "Bug"
  - feature: green icon + "Feature"
  - support: blue icon + "Support"

### Card Layout
- Border: 1px solid gray-200
- Padding: px-4 py-3
- Border radius: rounded (default 4px)
- Shadow: shadow-sm (subtle)
```

### Why This Matters
When adding new UI:
- Button should use primary navy color, not random blue
- New badges should follow the status-color mapping
- Card padding should match existing cards
- Without this reference, new components break visual consistency

---

## 4. Data Model Mapping

### Objective
Document all TypeScript types, database schemas, and how data flows from input → API → storage → display.

### Instructions

**Step 1: Find type definitions**

```bash
find src -name "*.ts" -o -name "*.tsx" | xargs grep -l "interface\|type.*="
```

**Step 2: For each core type, record:**

```markdown
## Data Models

### Ticket Type (src/types/index.ts:5-30)

**TypeScript Definition**:
```typescript
interface Ticket {
  id: string;                    // UUID primary key
  ticket_number: number;         // Auto-increment display number
  title: string;                 // User input, max 200 chars
  description: string;           // User input, multiline
  status: 'open' | 'claimed' | 'resolved';
  issue_type: 'bug' | 'feature' | 'support';
  submitted_by: string;          // product_support user name
  submitted_at: Date;            // ISO timestamp
  claimed_by?: string;           // admin user name (nullable)
  claimed_at?: Date;             // ISO timestamp when claimed (nullable)
  resolved_at?: Date;            // ISO timestamp when resolved
  image_urls?: string[];         // Array of Supabase Storage URLs
  priority?: 'low' | 'medium' | 'high';
}
```

**Database Schema** (migrations/001_create_tickets.sql):
```sql
CREATE TABLE tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_number SERIAL UNIQUE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'open' NOT NULL,
  issue_type VARCHAR(20) NOT NULL,
  submitted_by VARCHAR(255) NOT NULL,
  submitted_at TIMESTAMP DEFAULT NOW(),
  claimed_by VARCHAR(255),
  claimed_at TIMESTAMP,
  resolved_at TIMESTAMP,
  image_urls TEXT[],
  priority VARCHAR(20)
);
```

**Validation Rules**:
- title: required, 5-200 characters
- description: required, 10-2000 characters
- issue_type: must be one of ['bug', 'feature', 'support']
- image_urls: at least 1 image required on creation

**If adding a field**:
1. Update interface in src/types/index.ts
2. Create SQL migration (migrations/NNN_add_field.sql)
3. Update insert/update queries in src/hooks/useTickets.ts
4. Update forms/displays that show this field
```

**Step 3: Data Flow Diagram**

```markdown
## Data Flow: Create Ticket

1. **User Input** (TicketForm.tsx)
   - Form fields: title, description, issue_type, images
   - Validation: title length, image count
   - State: formData, isSubmitting, error

2. **Image Upload** (imageUpload.ts)
   - Compression: JPEG, max 500KB, max 1920px
   - Destination: Supabase Storage bucket 'ticket-images'
   - Returns: Public URL array

3. **Insert Ticket** (useTickets.ts:45-60)
   ```typescript
   const { data, error } = await supabase
     .from('tickets')
     .insert([{
       title, description, issue_type,
       image_urls,
       submitted_by: currentUser.name,
       submitted_at: new Date(),
       status: 'open'
     }])
     .select();
   ```

4. **Realtime Subscription** (AdminView.tsx:120-140)
   - Listens to: INSERT on tickets table
   - Triggers: Full ticket refetch
   - Updates: Display in AdminView open pool

5. **Display** (TicketCard.tsx)
   - Shows: title, status badge, images, TAT timer
   - Props: Ticket object, callbacks for claim/resolve
```

**Step 4: API Contract**

```markdown
## Supabase API Contract

### Select Tickets
```typescript
const { data: tickets } = await supabase
  .from('tickets')
  .select('*')
  .eq('status', 'open')
  .order('submitted_at', { ascending: false });
```
Returns: Ticket[]

### Claim Ticket (Race condition protected)
```typescript
const { data } = await supabase
  .from('tickets')
  .update({ claimed_by, claimed_at: new Date(), status: 'claimed' })
  .eq('id', ticketId)
  .eq('status', 'open')  // Only claim if still open!
  .select();
```
Risk: If .eq('status', 'open') is removed, multiple admins can claim same ticket

### Resolve Ticket
```typescript
const { data } = await supabase
  .from('tickets')
  .update({ status: 'resolved', resolved_at: new Date() })
  .eq('id', ticketId)
  .eq('claimed_by', currentUser.name)  // Only own claims
  .select();
```
Risk: If guard is removed, admins can resolve others' tickets
```

### Why This Matters
When changing the data model:
- Adding a field requires migration + type + form + display
- Missing migration causes silent failures in production
- Race condition guards must be preserved when refactoring
- API contracts define what breaks if backend changes

---

## 5. Service Layer Analysis

### Objective
Identify all external services and document boundaries so new features know what dependencies exist.

### Instructions

**Step 1: Search for external service calls**

```bash
grep -r "supabase\|firebase\|fetch\|axios\|api\." src --include="*.ts" --include="*.tsx"
```

**Step 2: For each service, document:**

```markdown
## External Services

### Supabase (src/lib/supabase.ts)

**Initialization**:
```typescript
const supabase = createClient(
  process.env.VITE_SUPABASE_URL,
  process.env.VITE_SUPABASE_ANON_KEY
);
```

**Environment Variables Required**:
- VITE_SUPABASE_URL: https://xyz.supabase.co
- VITE_SUPABASE_ANON_KEY: public.xyz
- Missing var: Client created with empty values, no error
- Impact: All database queries silently fail

**Authentication Contract**:
- Method: Email + password via supabase.auth.signInWithPassword()
- Session: Stored in browser localStorage by Supabase
- RLS Policies: Enable/disable based on authenticated user
- Risk: No password hashing server-side in old fork; fixed in LOS

**Database Contract**:
- Table: tickets
- CRUD Operations: insert(), select(), update(), delete()
- Filters: .eq(), .neq(), .gt(), .in(), compound with chaining
- Realtime: Enabled for postgres_changes event
- Risk: If RLS policies are "Allow all", any user can read/write all tickets

**Storage Contract**:
- Bucket: ticket-images (public)
- Upload: storage.from('ticket-images').upload(path, file)
- Download: Via public HTTPS URL (no auth token needed)
- Risk: Public bucket means anyone with URL can download

### Realtime Subscription (useTickets.ts:180-210)

**Listener Setup**:
```typescript
supabase
  .channel('tickets')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'tickets' }, handler)
  .subscribe();
```

**Triggered Events**: INSERT, UPDATE, DELETE on tickets table

**Handler Behavior**: Refetch all tickets (full refresh, no partial update)

**Risk**:
- If realtime is disabled, ProductSupportView doesn't get live notifications
- If subscription fails silently, stale UI persists
- No error boundary; if Supabase goes down, app shows cached data

### Image Compression Service (utils/imageUpload.ts)

**Library**: browser-image-compression

**Compression Rules**:
- Format: JPEG
- Max size: 500KB
- Max dimensions: 1920px (width/height)
- Quality: Automatic based on file size

**Failure Mode**: If compression fails, original file uploaded uncompressed

**Risk**: If library updated, compression algorithm changes; old compressed images might decompress differently
```

**Step 3: Service Boundaries**

```markdown
## Service Boundaries

### What depends on Supabase?
- useTickets hook (all CRUD)
- AuthContext (login/logout)
- useRealtimeSubscription (live updates)
- Image upload handler

### What breaks if Supabase URL changes?
- Need to update VITE_SUPABASE_URL env var
- App won't error; just silently fails all queries

### What breaks if RLS policies change?
- If policies become "Allow all", security boundary broken
- If policies become "Deny all", even admin queries blocked

### What breaks if Realtime is disabled?
- ProductSupportView notifications stop
- AdminView doesn't auto-refresh when new tickets arrive
- User sees stale data until manual refresh
```

### Why This Matters
When adding a new feature:
- If it queries the database, check RLS policies allow it
- If it uploads files, check Storage bucket is accessible
- If it needs live updates, ensure realtime subscription is active
- If it uses environment variables, ensure they're documented and set

---

## 6. State Management Mapping

### Objective
Catalog all state (Context, hooks, local, component state) so new features know how data flows between components.

### Instructions

**Step 1: Find all Context Providers**

```bash
grep -r "createContext\|Provider" src --include="*.tsx" --include="*.ts"
```

**Step 2: For each state source, record:**

```markdown
## State Management

### Global Context: AuthContext (src/context/AuthContext.tsx:1-50)

**Provider**:
```typescript
export const AuthProvider: React.FC = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  return (
    <AuthContext.Provider value={{ currentUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Shape**:
```typescript
interface AuthContextType {
  currentUser: {
    name: string;
    role: 'admin' | 'product_support';
  } | null;
  login: (password: string) => void;
  logout: () => void;
}
```

**Consumers**: Header, AppContent, AdminView, ProductSupportView

**Risk**: If changing currentUser shape (add/remove/rename field), all consumers break

**Safe to change**: Add new role types (backward compatible if existing code checks enum)

### Custom Hook: useTickets (src/hooks/useTickets.ts)

**Returns**:
```typescript
interface UseTicketsReturn {
  tickets: Ticket[];
  loading: boolean;
  error: Error | null;
  claimTicket: (id: string) => Promise<void>;
  resolveTicket: (id: string) => Promise<void>;
  refetch: () => Promise<void>;
}
```

**Consumers**: AdminView (main), ProductSupportView (notifications), TicketForm (on submit)

**Race Conditions**:
- claimTicket: Protected by compound filter (.eq('status', 'open'))
- resolveTicket: Protected by .eq('claimed_by', currentUser.name)

**Risk**: If removing guards, concurrent claim/resolve breaks logic

**Safe to change**: Add new filter/sort functions (new methods are additive)

### Component-Level State Examples

**AdminView activeTab** (src/components/AdminView.tsx:35-40)
```typescript
const [activeTab, setActiveTab] = useState<'open' | 'claimed' | 'resolved'>('open');
```
- Local to component
- Controls which TicketCard list renders
- Risk: Low (UI state only)

**ResolveModal selectedTicket** (AdminView.tsx:84-94)
```typescript
const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
```
- Lifted to AdminView parent
- Passed to ResolveModal as prop
- Risk: If moving modal to different parent, selectedTicket state becomes unreachable

**State Flow**:
1. AdminView has selectedTicket state
2. AdminView renders TicketCard (child), passes `onSelect={setSelectedTicket}`
3. AdminView renders ResolveModal (child), passes selectedTicket as prop
4. ResolveModal calls resolveTicket() from useTickets hook

### Dependency Graph

```
AuthContext (global)
├── Consumed by: Header, AdminView, ProductSupportView
├── Risk: Changing shape breaks all
└── Safe: Adding optional fields (backward compatible)

useTickets hook (dependency injection per component)
├── Consumed by: AdminView, ProductSupportView, TicketForm
├── Returns: tickets, CRUD functions, loading, error
├── Risk: Changing return shape breaks all consumers
└── Safe: Adding new methods (additive)

Realtime subscription (inside useTickets)
├── Triggered by: Supabase INSERT/UPDATE/DELETE
├── Affects: ticket list refetch
├── Risk: If disabled, live updates stop
└── Safe: Changing refetch strategy (if coordinating all consumers)

Component-level state (AdminView activeTab)
├── Self-contained UI state
├── Risk: Low (only affects this component)
└── Safe: Adding new tab types
```

### Why This Matters
When adding state:
- If global (Context), all consumers must handle new fields
- If hook-based, all callers must know return type changed
- If local (component state), only affects that component
- Use Context for truly global state (auth, theme)
- Use hooks for data fetch logic (tickets, users)
- Use component state for UI toggles (modals, tabs)

---

## 7. Sub-Agent Coordination Protocol

### Objective
For large codebases (1000+ files), split analysis across multiple Claude agents, then merge results.

### Instructions

**Step 1: Identify analysis zones**

Divide codebase by responsibility:
- **Agent A**: Components (all .tsx files in src/components/)
- **Agent B**: Hooks (all .ts files in src/hooks/)
- **Agent C**: Data layer (src/lib/, migrations/, types/)
- **Agent D**: Pages/views (src/pages/, src/views/)

**Step 2: Each agent documents their zone**

Agent A documents:
```
- Every .tsx file name, what it renders, what props it takes
- Import/export relationships (who imports this component?)
- External library dependencies (tailwind, lucide-react, etc.)
```

Agent B documents:
```
- Every hook: what it does, what it returns
- Dependencies: what other hooks/contexts/services it uses
- Consumer count: which components call this hook?
```

Agent C documents:
```
- Type definitions (all interfaces/types)
- Database schema (all tables and fields)
- API contracts (what Supabase calls exist?)
- Migrations (schema changes over time)
```

Agent D documents:
```
- Top-level pages/views (Admin, Support, etc.)
- Page structure (what components does each page render?)
- Page-specific state (tabs, modals, filters)
- Route configuration (paths, guards, redirects)
```

**Step 3: Merge results into single System Map**

Create a `SYSTEM_MAP.md` with sections:

```markdown
# System Map

## Zone A: Components (Agent A)
[All components inventory]

## Zone B: Hooks (Agent B)
[All hooks inventory]

## Zone C: Data (Agent C)
[Types, schema, API contracts]

## Zone D: Pages (Agent D)
[Top-level pages and routes]

## Integration Points (Merge of all zones)
[Shows how zones connect]
```

**Step 4: Identify cross-zone dependencies**

Create an integration matrix:

```markdown
## Cross-Zone Dependencies

Components → Hooks:
- TicketCard uses useTimer
- AdminView uses useTickets
- TicketForm uses useImageUpload

Hooks → Data:
- useTickets queries Ticket type, calls Supabase API
- useAuth depends on AuthContext (global state)

Components → Data:
- Header uses AuthContext directly
- TicketCard renders Ticket type

Pages → Components:
- AdminView renders TicketCard, ResolveModal
- SupportView renders TicketForm
```

**Step 5: Validate consistency**

Check:
- Are all imported components actually defined?
- Are all Ticket fields in type used in at least one component?
- Are all Supabase tables queried by at least one hook?
- Are all routes in App.tsx linked in Header.tsx?

### Coordination Template

**Prompt for Agent A (Components)**:
```
Analyze all components in src/components/.
For each .tsx file:
1. Component name
2. File path
3. Props interface
4. What components/hooks it imports
5. What it renders (JSX description)
6. External dependencies (libraries)
7. Who imports this component? (search codebase)

Format as inventory table.
```

**Prompt for Agent B (Hooks)**:
```
Analyze all hooks in src/hooks/.
For each .ts file:
1. Hook name (must start with "use")
2. File path
3. Return type (interface)
4. Dependencies (what it imports)
5. Consumer count (how many components use it?)
6. Risks (race conditions, data consistency issues)

Format as inventory table.
```

**Prompt for Agent C (Data)**:
```
Analyze src/types, migrations, src/lib.
For each:
1. TypeScript interface/type name
2. Database table name (if exists)
3. Fields and types
4. Validation rules
5. Supabase API calls (queries, inserts, updates)
6. Breaking change history (migrations)

Format as structured reference.
```

**Merge Checklist**:
- [ ] All components listed in Zone A
- [ ] All hooks listed in Zone B
- [ ] All types listed in Zone C
- [ ] All pages listed in Zone D
- [ ] Import graph matches (if A imports B, is B documented?)
- [ ] No circular dependencies
- [ ] All external services documented
- [ ] All routes have guards/permissions listed
- [ ] All types have database schema mapping
- [ ] All hooks have consumer list

### Why This Matters
For large codebases:
- Single agent can miss files or relationships
- Sub-agents can work in parallel (faster)
- Divided responsibility ensures thorough analysis
- Integration matrix catches cross-zone breakages
- Merge process validates completeness

---

## Quick Reference Checklist

Before making changes, verify you have documented:

- [ ] **Components**: All .tsx files cataloged with props, imports, exports
- [ ] **Routes**: All paths, guards, layout wrappers mapped
- [ ] **Colors**: Primary, accent, semantic colors with Tailwind equivalents
- [ ] **Types**: Core data structures with validation rules
- [ ] **Database**: Schema, migrations, API contracts
- [ ] **Services**: Supabase (auth, database, storage) contracts and failure modes
- [ ] **State**: Context and hook shapes, consumer lists
- [ ] **Integration points**: Feature → component → hook → service flow documented

---

**Generated for**: Workflow Guardian skill
**Version**: 1.0
**Last Updated**: 2026-02-26
