# Role System Preservation Guide for Workflow Guardian

## CRITICAL PRINCIPLE: "Match, Don't Fix"

When adding features to existing applications, **PRESERVE the role and permission system exactly as it is**, even if it appears inconsistent or poorly designed. The cost of breaking existing features far outweighs the benefit of refactoring. This guide teaches you how to extend role systems defensively without breaking existing functionality.

---

## 1. ROLE SYSTEM INVENTORY PROTOCOL

Before adding any feature that touches authentication, authorization, or role-based logic, document the **entire** existing role system comprehensively.

### 1.1 Where Roles Are Defined

#### Project 1: Ring Kissht Issue Tracker

**Location:** `/src/types/index.ts` (lines 1-3)
```typescript
export type UserRole = 'sm' | 'tech_support_team' | 'product_support';
```

**Observation:** Three roles defined as string literals in a TypeScript union type.

**Location:** `/src/pages/LoginPage.tsx` (lines 8-12)
```typescript
const roles: { value: UserRole; label: string; description: string }[] = [
  { value: 'sm', label: 'Product Support', description: 'Submit and manage forms' },
  { value: 'tech_support_team', label: 'Tech Support', description: 'View and resolve submissions' },
  { value: 'product_support', label: 'SM', description: 'Submit loan issue forms' },
];
```

**CRITICAL OBSERVATION - ROLE CONFUSION PATTERN:**
- Role `'sm'` has display label `'Product Support'`
- Role `'product_support'` has display label `'SM'`
- These labels are **intentionally inverted** in the UI but the string values remain distinct
- This is **confusing but WORKING** — do NOT "fix" it
- The actual role checking uses the string values (`'sm'`, `'product_support'`), never the labels

**Why This Matters:** Someone once swapped the labels for UX reasons, but the backend still checks exact string values. If you "fix" this by renaming roles to match labels, all existing role checks will break.

#### Project 2: LOS Issue Tracker

**Location:** `/src/context/AuthContext.tsx` (lines 23-26)
```typescript
type FetchResult =
  | { status: 'found'; role: 'product_support' | 'admin'; name: string | null }
  | { status: 'not_found' }
  | { status: 'error'; message: string };
```

**Location:** `/src/types/index.ts` (lines 83-88)
```typescript
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'product_support' | 'admin';
}
```

**Observation:** Two roles defined in both the type system and the auth context. Roles are fetched from Supabase `allowed_users` table.

---

### 1.2 Where Roles Are Checked (Route Guards)

#### Project 1: Ring Kissht Issue Tracker

**Location:** `/src/App.tsx` (lines 45-51)
```typescript
if (selectedRole === 'sm') {
  navigate('/submit');
} else if (selectedRole === 'product_support') {
  navigate('/loan-issue');
} else {
  navigate('/submissions');
}
```

**Pattern:** Post-login redirect based on exact role string value.

**Location:** `/src/components/ProtectedRoute.tsx` (lines 10-22)
```typescript
export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, role } = useSimpleAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
```

**Pattern:** Route-level guard with an `allowedRoles` array. Checks if `role` is in the array.

**Route Guard Usage (App.tsx, lines 22-86):**
```typescript
<Route path="/submit" element={
  <ProtectedRoute allowedRoles={['sm']}>
    <Layout><SubmitPage /></Layout>
  </ProtectedRoute>
}/>

<Route path="/loan-issue" element={
  <ProtectedRoute allowedRoles={['product_support']}>
    <Layout><LoanIssueFormPage /></Layout>
  </ProtectedRoute>
}/>

<Route path="/submissions" element={
  <ProtectedRoute allowedRoles={['sm', 'tech_support_team']}>
    <Layout><SubmissionsListPage /></Layout>
  </ProtectedRoute>
}/>

<Route path="/submissions/:id/modify" element={
  <ProtectedRoute allowedRoles={['sm']}>
    <Layout><ModifySubmissionPage /></Layout>
  </ProtectedRoute>
}/>
```

**Inventory of Role Checks:**
| Route | Allowed Roles | Purpose |
|-------|---------------|---------|
| `/submit` | `['sm']` | Submit forms (Product Support agents only) |
| `/loan-issue` | `['product_support']` | Loan issue forms (SM only) |
| `/submissions` | `['sm', 'tech_support_team']` | View submissions (Product Support + Tech Support) |
| `/submissions/:id` | `['sm', 'tech_support_team']` | View submission details (Product Support + Tech Support) |
| `/submissions/:id/modify` | `['sm']` | Modify submissions (Product Support agents only) |
| `/product-support` | `['sm']` | Product Support dashboard (Product Support agents only) |

**Key Pattern:** Routes use `allowedRoles` arrays with exact string matches via `includes()`. Some routes accept multiple roles, others single roles.

#### Project 2: LOS Issue Tracker

**Location:** `/src/App.tsx` (lines 145-149)
```typescript
return (
  <div className="min-h-screen bg-[#fafbfc]">
    <Header />
    <motion.main ... className="max-w-7xl mx-auto p-4">
      {currentUser.role === 'product_support' ? (
        <ProductSupportView />
      ) : (
        <AdminView />
      )}
    </motion.main>
  </div>
);
```

**Pattern:** Conditional rendering based on exact role string value. Two-branch (ternary) check: `product_support` vs anything else (admin).

**Key Pattern:** LOS tracker uses conditional rendering, not route guards. The entire UI changes based on role.

---

### 1.3 Where Roles Are Stored

#### Project 1: Ring Kissht Issue Tracker

**Storage:** In-memory + localStorage
- **In-memory:** `SimpleAuthContext` state: `const [role, setRole] = useState<UserRole | null>(null);`
- **localStorage:** `const STORAGE_KEY = 'issue_tracker_auth';`

**Location:** `/src/contexts/SimpleAuthContext.tsx` (lines 22-36)
```typescript
useEffect(() => {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    try {
      const { role: storedRole } = JSON.parse(stored);
      if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support') {
        setRole(storedRole);
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Failed to parse stored auth:', error);
      localStorage.removeItem(STORAGE_KEY);
    }
  }
  setLoading(false);
}, []);
```

**Validation:** The auth context validates that the stored role matches one of the known values exactly (`=== 'sm' || === 'tech_support_team' || === 'product_support'`).

**Storage Format:**
```json
{
  "role": "sm"
}
```

#### Project 2: LOS Issue Tracker

**Storage:** Supabase Auth + Supabase Database + localStorage (cache)

**Primary Source:** Supabase `allowed_users` table

**Location:** `/src/context/AuthContext.tsx` (lines 88-130)
```typescript
async function fetchAllowedUser(email: string, retries = MAX_RETRIES): Promise<FetchResult> {
  const endOuter = perfSpan('fetchAllowedUser');
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const endAttempt = perfSpan(`fetchAllowedUser:attempt-${attempt + 1}`);
      const result = await Promise.race([
        supabase
          .from('allowed_users')
          .select('role, name')
          .eq('email', email.toLowerCase())
          .single(),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('allowed_users query timed out')), QUERY_TIMEOUT_MS)
        ),
      ]);
      // ... error handling ...
      return { status: 'found', role: result.data.role, name: result.data.name };
    }
  }
}
```

**Cache:** localStorage at key `'los_cached_role'` (line 21)
```typescript
function cacheRole(email: string, role: string, name: string | null) {
  try {
    localStorage.setItem(ROLE_CACHE_KEY, JSON.stringify({ email: email.toLowerCase(), role, name, ts: Date.now() }));
  } catch { /* ignore */ }
}
```

**Cache TTL:** 8 hours (line 59)

**Storage Format:**
```json
{
  "email": "user@kissht.com",
  "role": "product_support",
  "name": "John Doe",
  "ts": 1699999999999
}
```

**Key Pattern:** The role is looked up from the database, not hardcoded or user-provided. The auth flow validates the email domain (`@kissht.com` only) before querying for role.

---

### 1.4 Exact String Values (Never Rename, Never Alias)

#### Project 1 String Values
```
'sm'
'tech_support_team'
'product_support'
```

**Hardcoded Checks in Codebase:**
1. `/src/contexts/SimpleAuthContext.tsx:27` - Validation check for all three values
2. `/src/pages/LoginPage.tsx:45` - Redirect check for `'sm'`
3. `/src/pages/LoginPage.tsx:47` - Redirect check for `'product_support'`
4. `/src/App.tsx:93` - Root path redirect check for `'sm'`
5. `/src/App.tsx:95` - Root path redirect check for `'product_support'`

**In Route Guards:**
```typescript
allowedRoles={['sm']}
allowedRoles={['product_support']}
allowedRoles={['sm', 'tech_support_team']}
```

**Why Exact Values Matter:** If you rename `'sm'` to `'smalloc'` or `'support_manager'`, the validation check at line 27 of SimpleAuthContext will reject any stored session with the new name. Existing users will be logged out permanently because the persisted role won't validate.

#### Project 2 String Values
```
'product_support'
'admin'
```

**Hardcoded Checks in Codebase:**
1. `/src/context/AuthContext.tsx:24` - Type definition in `FetchResult`
2. `/src/context/AuthContext.tsx:69` - Type definition for `getCachedRole` return
3. `/src/context/AuthContext.tsx:132` - Type definition in `buildUser` function
4. `/src/types/index.ts:87` - Type definition in `User` interface
5. `/src/App.tsx:145` - Conditional render check: `currentUser.role === 'product_support'`

**Why Exact Values Matter:** If you rename `'product_support'` to `'ps'`, the database must also have `'ps'` in the `role` column of `allowed_users`. Any existing rows with `'product_support'` will no longer match the type definition. New users assigned `'product_support'` will fail TypeScript checks.

---

## 2. SAFE ROLE EXTENSION

To add a new role **without breaking existing ones**, follow this exact pattern:

### 2.1 Pattern: Adding a New Role

**Scenario:** Project 1 needs a new `'supervisor'` role.

#### Step 1: Add to Type Definition ONLY

**File:** `/src/types/index.ts`

```typescript
// BEFORE
export type UserRole = 'sm' | 'tech_support_team' | 'product_support';

// AFTER
export type UserRole = 'sm' | 'tech_support_team' | 'product_support' | 'supervisor';
```

**Rule:** Add the new role at the END of the union. Do NOT reorder or remove existing values.

#### Step 2: Add to Login Role Selector (Copy Existing Pattern Exactly)

**File:** `/src/pages/LoginPage.tsx`

```typescript
// BEFORE
const roles: { value: UserRole; label: string; description: string }[] = [
  { value: 'sm', label: 'Product Support', description: 'Submit and manage forms' },
  { value: 'tech_support_team', label: 'Tech Support', description: 'View and resolve submissions' },
  { value: 'product_support', label: 'SM', description: 'Submit loan issue forms' },
];

// AFTER
const roles: { value: UserRole; label: string; description: string }[] = [
  { value: 'sm', label: 'Product Support', description: 'Submit and manage forms' },
  { value: 'tech_support_team', label: 'Tech Support', description: 'View and resolve submissions' },
  { value: 'product_support', label: 'SM', description: 'Submit loan issue forms' },
  { value: 'supervisor', label: 'Supervisor', description: 'Oversee and manage team' },
];
```

**Rule:** Add the new role as a new array element. Do NOT modify existing elements.

#### Step 3: Add Route Redirection (If Needed)

**File:** `/src/App.tsx`, default redirect section

```typescript
// BEFORE
<Route path="/" element={
  isAuthenticated ? (
    role === 'sm' ? (
      <Navigate to="/submit" replace />
    ) : role === 'product_support' ? (
      <Navigate to="/loan-issue" replace />
    ) : (
      <Navigate to="/submissions" replace />
    )
  ) : (
    <Navigate to="/login" replace />
  )
}/>

// AFTER
<Route path="/" element={
  isAuthenticated ? (
    role === 'sm' ? (
      <Navigate to="/submit" replace />
    ) : role === 'product_support' ? (
      <Navigate to="/loan-issue" replace />
    ) : role === 'supervisor' ? (
      <Navigate to="/supervisor-dashboard" replace />
    ) : (
      <Navigate to="/submissions" replace />
    )
  ) : (
    <Navigate to="/login" replace />
  )
}/>
```

**Rule:** Add the new role check BEFORE the catch-all `else` at the end. This preserves the fallback behavior.

#### Step 4: Create New Routes for Supervisor Features

**File:** `/src/App.tsx`, add new routes AFTER existing ones

```typescript
<Route
  path="/supervisor-dashboard"
  element={
    <ProtectedRoute allowedRoles={['supervisor']}>
      <Layout>
        <SupervisorDashboard />
      </Layout>
    </ProtectedRoute>
  }
/>
```

**Rule:**
- Create isolated routes for the new role's features
- Do NOT add the new role to existing `allowedRoles` arrays (unless intentional and tested)
- Do NOT modify existing routes

#### Step 5: Update Auth Validation (If Using SimpleAuthContext)

**File:** `/src/contexts/SimpleAuthContext.tsx`

```typescript
// BEFORE
if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support') {
  setRole(storedRole);
  setIsAuthenticated(true);
}

// AFTER
if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support' || storedRole === 'supervisor') {
  setRole(storedRole);
  setIsAuthenticated(true);
}
```

**Rule:** Add the new role to the OR chain. This validates that stored sessions can load the new role.

#### Step 6: Test ALL Existing Roles First

**Before deploying the new role, verify:**
- ✓ Login as `'sm'` → redirects to `/submit`
- ✓ Login as `'tech_support_team'` → redirects to `/submissions`
- ✓ Login as `'product_support'` → redirects to `/loan-issue`
- ✓ Each role can access its protected routes
- ✓ Each role cannot access other roles' protected routes
- ✓ Refresh the page → role persists from localStorage

**Only then** login as the new `'supervisor'` role.

---

### 2.2 Pattern: Adding a New Role to Project 2 (LOS Tracker)

**Scenario:** Project 2 needs a `'manager'` role in addition to `'product_support'` and `'admin'`.

#### Step 1: Update Type Definitions

**File:** `/src/context/AuthContext.tsx` (lines 23-26)

```typescript
// BEFORE
type FetchResult =
  | { status: 'found'; role: 'product_support' | 'admin'; name: string | null }
  | { status: 'not_found' }
  | { status: 'error'; message: string };

// AFTER
type FetchResult =
  | { status: 'found'; role: 'product_support' | 'admin' | 'manager'; name: string | null }
  | { status: 'not_found' }
  | { status: 'error'; message: string };
```

**File:** `/src/context/AuthContext.tsx` (line 69)

```typescript
// BEFORE
function getCachedRole(email: string): { role: 'product_support' | 'admin'; name: string | null } | null {

// AFTER
function getCachedRole(email: string): { role: 'product_support' | 'admin' | 'manager'; name: string | null } | null {
```

**File:** `/src/context/AuthContext.tsx` (line 132)

```typescript
// BEFORE
function buildUser(supabaseUser: SupabaseUser, role: 'product_support' | 'admin', displayName: string | null): User {

// AFTER
function buildUser(supabaseUser: SupabaseUser, role: 'product_support' | 'admin' | 'manager', displayName: string | null): User {
```

**File:** `/src/types/index.ts` (lines 83-88)

```typescript
// BEFORE
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'product_support' | 'admin';
}

// AFTER
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'product_support' | 'admin' | 'manager';
}
```

**Rule:** Update ALL type definitions consistently. The role type must be identical everywhere it appears.

#### Step 2: Create New View Component

**File:** `/src/pages/ManagerView.tsx` (new file)

```typescript
export function ManagerView() {
  return (
    <div>
      {/* Manager-specific dashboard */}
    </div>
  );
}
```

**Rule:** Create isolated view components for new roles, don't modify existing views.

#### Step 3: Update App Routing

**File:** `/src/App.tsx`

```typescript
// BEFORE
return (
  <div className="min-h-screen bg-[#fafbfc]">
    <Header />
    <motion.main ... className="max-w-7xl mx-auto p-4">
      {currentUser.role === 'product_support' ? (
        <ProductSupportView />
      ) : (
        <AdminView />
      )}
    </motion.main>
  </div>
);

// AFTER
return (
  <div className="min-h-screen bg-[#fafbfc]">
    <Header />
    <motion.main ... className="max-w-7xl mx-auto p-4">
      {currentUser.role === 'product_support' ? (
        <ProductSupportView />
      ) : currentUser.role === 'manager' ? (
        <ManagerView />
      ) : (
        <AdminView />
      )}
    </motion.main>
  </div>
);
```

**Rule:** Add the new role check BEFORE the catch-all `else`. Preserve the fallback.

#### Step 4: Update RoleBadge Display (If Used)

**File:** `/src/components/ui/Badge.tsx` (or wherever roles are displayed)

Find the role display logic and ensure it handles the new role:

```typescript
// BEFORE
const roleLabels = {
  product_support: 'Product Support',
  admin: 'Admin',
};

// AFTER
const roleLabels = {
  product_support: 'Product Support',
  admin: 'Admin',
  manager: 'Manager',
};
```

**Rule:** Add display labels for any UI that shows roles.

#### Step 5: Database Update (SEPARATE from Code)

**Action:** Add users to the Supabase `allowed_users` table with role `'manager'`.

**Important:** This is a database operation, not a code change. The code is already prepared to handle the new role because of the type updates.

#### Step 6: Test ALL Existing Roles First

**Before deploying:**
- ✓ Login as `'product_support'` → see `ProductSupportView`
- ✓ Login as `'admin'` → see `AdminView`
- ✓ Refresh page → role persists from cache
- ✓ Verify role badge displays correctly

**Only then** test the new `'manager'` role.

---

## 3. SAFE PERMISSION EXTENSION

When adding new permissions, **match the existing pattern** in your application, even if it's ugly or seems inefficient.

### 3.1 Identify the Permission Pattern

#### Project 1: Pattern Analysis

**Pattern:** No explicit permission system. Roles ARE permissions. If you have role `'sm'`, you're allowed to do whatever `'sm'` users do.

**Evidence:**
- `/src/components/ProtectedRoute.tsx` checks only `allowedRoles`, never `allowedPermissions`
- No separate permission definitions in the codebase
- No `hasPermission()` function

**Consequence:** If you need a new permission (e.g., "approve submissions"), you must either:
1. Create a new role: `'approval_manager'` (matches the pattern)
2. Change an existing role's behavior via conditional rendering (matches the pattern)

#### Project 2: Pattern Analysis

**Pattern:** No explicit permission system. Roles map to views. Role `'admin'` sees everything; role `'product_support'` sees limited view.

**Evidence:**
- `/src/App.tsx` uses conditional `===` checks on role
- No `hasPermission()`, no permission enum
- All permission logic is "if role === 'admin' then X else Y"

**Consequence:** If you need new permissions, create new role checks in the conditional rendering.

### 3.2 Safe Permission Pattern: Adding Approval Capability to Project 1

**Requirement:** Product Support managers (`'sm'` users) should now approve submissions, not just submit them.

**Wrong Approach (Creates New System):**
```typescript
// DON'T DO THIS - creates parallel permission system
const PERMISSIONS = {
  'sm': ['submit', 'approve'],
  'tech_support_team': ['view', 'resolve'],
  'product_support': ['submit']
};

function hasPermission(role: UserRole, permission: string): boolean {
  return PERMISSIONS[role]?.includes(permission) ?? false;
}
```

**Reason:** This introduces a new permission checking pattern. All existing code uses `allowedRoles` array checks. Now you have two competing systems.

**Right Approach (Match Existing Pattern):**

Use the existing `allowedRoles` pattern everywhere. Add new routes for new capabilities:

**File:** `/src/App.tsx`

```typescript
// NEW ROUTE - matches existing pattern
<Route
  path="/submissions/approve"
  element={
    <ProtectedRoute allowedRoles={['sm']}>
      <Layout>
        <ApprovalQueuePage />
      </Layout>
    </ProtectedRoute>
  }
/>
```

**File:** `/src/pages/SubmitPage.tsx` (or similar)

```typescript
// NEW CONDITIONAL - matches existing pattern
if (role === 'sm' && userCanApprove) {
  // Show approve button
}
```

**Why This Works:** You're using the same role checking mechanism everywhere. Someone reading the code sees `allowedRoles={['sm']}` and immediately understands the permission model.

### 3.3 Safe Permission Pattern: Adding Team Lead Role to Project 2

**Requirement:** Project 2 needs a `'team_lead'` role with some admin powers but not full admin.

**Wrong Approach (Creates New Permission System):**
```typescript
// DON'T DO THIS
const getPermissionLevel = (role: Role): number => ({
  'product_support': 1,
  'team_lead': 2,
  'admin': 3
}[role]);

if (getPermissionLevel(role) >= 2) {
  // Can access team lead features
}
```

**Right Approach (Match Existing Pattern):**

```typescript
// File: /src/App.tsx
return (
  <div>
    <Header />
    <motion.main>
      {currentUser.role === 'product_support' ? (
        <ProductSupportView />
      ) : currentUser.role === 'team_lead' ? (
        <TeamLeadView />
      ) : (
        <AdminView />
      )}
    </motion.main>
  </div>
);
```

**Why This Works:** Uses the same conditional rendering pattern as existing roles.

---

## 4. DANGEROUS PATTERNS TO AVOID

These refactorings break existing applications. **Never do these:**

### 4.1 "Let Me Consolidate the Role Names"

**The Problem:**
```typescript
// BEFORE - Project 1's intentionally confusing setup
const roles = [
  { value: 'sm', label: 'Product Support' },
  { value: 'product_support', label: 'SM' }
];

// AFTER - "Fixed" by renaming
export type UserRole = 'product_support_agent' | 'support_manager';
const roles = [
  { value: 'product_support_agent', label: 'Product Support' },
  { value: 'support_manager', label: 'SM' }
];
```

**What Breaks:**
1. All hardcoded `allowedRoles={['sm']}` checks become incorrect
2. All localStorage keys with `"role": "sm"` fail validation
3. All route redirects checking `role === 'sm'` become dead code
4. Existing users are logged out (stored role no longer validates)
5. Database records referencing the old role become invalid

**The Cost:** Days of debugging. Users unable to login. Production data inconsistencies.

**The Principle:** The confusing names are intentional, hardwired, and relied upon. Even if you don't understand why `'sm'` and `'product_support'` are labeled backwards, **leave them exactly as is**.

---

### 4.2 "Let Me Create a Proper RBAC System"

**The Problem:**
```typescript
// BEFORE - Simple role-based access
<ProtectedRoute allowedRoles={['sm', 'tech_support_team']}>

// AFTER - "Proper" RBAC
enum Permission {
  VIEW_SUBMISSIONS = 'view_submissions',
  APPROVE_SUBMISSIONS = 'approve_submissions',
  SUBMIT_FORMS = 'submit_forms'
}

const rolePermissions = {
  'sm': [Permission.SUBMIT_FORMS, Permission.VIEW_SUBMISSIONS],
  'tech_support_team': [Permission.VIEW_SUBMISSIONS],
  'product_support': [Permission.SUBMIT_FORMS]
};

<ProtectedRoute requiredPermissions={[Permission.VIEW_SUBMISSIONS]}>
```

**What Breaks:**
1. All existing `<ProtectedRoute allowedRoles={...}>` components become invalid
2. You must rewrite every route guard in the application
3. The permission-to-role mapping is now duplicated in data structure
4. If the permission system has a bug, you've introduced it into the application
5. You now maintain two authorization systems in parallel

**The Cost:** Complete rewrite of auth logic. Testing all routes again. New bugs in permission mapping.

**The Principle:** Project 1 uses simple role-based checks. Adding a permission layer on top doesn't improve the code; it complicates it. Work within the existing model.

---

### 4.3 "Let Me Add Role Hierarchy"

**The Problem:**
```typescript
// BEFORE - Flat roles
if (role === 'sm') { /* do sm stuff */ }
if (role === 'admin') { /* do admin stuff */ }

// AFTER - "Hierarchical" roles
const hierarchy = {
  'product_support': 0,
  'team_lead': 1,
  'manager': 2,
  'admin': 3
};

if (userHierarchy >= 2) { /* do manager-and-above stuff */ }
```

**What Breaks:**
1. Existing code checking `role === 'specific_role'` becomes incorrect
2. The `allowedRoles={['sm']}` pattern breaks (what hierarchy level is 'sm'?)
3. You must decide: does `sm` fit into the hierarchy? If yes, you've renamed it. If no, you have two systems.
4. New team members must understand the hierarchy. Old code is incomprehensible.
5. Adding a role between hierarchy levels breaks all numeric comparisons

**The Cost:** Refactoring every authorization check. Confusion about what each hierarchy level means. Breaking role-specific logic.

**The Principle:** Project 1 has flat roles for a reason: it's simple. Each role does specific things. There's no "less admin" or "more admin" — you either are admin or you're not.

---

### 4.4 "Let Me Move Roles to the Database"

**The Problem:**
```typescript
// BEFORE - Roles in code
export type UserRole = 'sm' | 'tech_support_team' | 'product_support';

// AFTER - Roles in database
// Remove UserRole type
// Query database for role definitions
// Dynamically load allowed roles from a `roles` table
// Check permissions based on database configuration
```

**What Breaks:**
1. Offline-first checks become impossible (roles are now a network call)
2. TypeScript type safety is gone (role is now a string from database)
3. The auth context must make a database call every time you check a role
4. Circular dependency: you need the role to query the database, but the database tells you what the role is
5. Caching logic becomes complex (cache invalidation is hard)
6. All hardcoded `role === 'sm'` checks become risky (the database might have changed)

**The Cost:** Performance degradation. Auth latency increases. Type safety lost. Debugging difficulties.

**The Principle:** Project 2 already does this (roles come from Supabase). It works for Project 2 because the architecture supports it. Project 1 uses hardcoded roles because it doesn't need database queries. **Don't force one architecture onto both projects.**

---

### 4.5 "Let Me Unify the Auth Systems"

**The Problem:**

Project 1 uses `SimpleAuthContext` with hardcoded roles. Project 2 uses `AuthContext` with Supabase. Someone says, "Let me make them both use the same pattern!"

```typescript
// BEFORE - Two different systems
// Project 1: SimpleAuthContext with localStorage
// Project 2: AuthContext with Supabase + cache

// AFTER - "Unified" system
// Both projects use Supabase
// Both projects use the same AuthContext
// Both projects have identical role logic
```

**What Breaks:**
1. Project 1 is a **demo app**. It doesn't need Supabase. Adding it adds complexity.
2. Project 1's SimpleAuthContext is intentionally simple (hardcoded password for demo). Forcing OAuth adds dependencies.
3. Existing Project 1 users with localStorage sessions become invalid (new auth system won't read them).
4. Project 1's routes are designed around its auth system. Changing auth breaks assumptions.
5. The two projects have different **requirements**. Forcing sameness breaks both.

**The Cost:** Breaking Project 1's demo functionality. Complexity creep. Maintenance burden of keeping both systems in sync.

**The Principle:** Different applications can have different auth systems. It's OK if they're different. The goal isn't consistency; the goal is that **each system works correctly for its own application**.

---

## 5. REAL EXAMPLES FROM PROJECT 1: THE ROLE CONFUSION

This section documents the **exact role confusion** currently in Project 1 to teach you what "Match, Don't Fix" means.

### 5.1 The Confusion: String Values vs. Display Labels

**Location:** `/src/pages/LoginPage.tsx` (lines 8-12)

```typescript
const roles: { value: UserRole; label: string; description: string }[] = [
  { value: 'sm', label: 'Product Support', description: 'Submit and manage forms' },
  { value: 'tech_support_team', label: 'Tech Support', description: 'View and resolve submissions' },
  { value: 'product_support', label: 'SM', description: 'Submit loan issue forms' },
];
```

**The Confusion:**

| String Value | Label in UI | Description |
|---|---|---|
| `'sm'` | `'Product Support'` | Submit and manage forms |
| `'product_support'` | `'SM'` | Submit loan issue forms |

**Why This Is Backwards:**

- `'sm'` stands for "Support Manager" internally, but displays as "Product Support"
- `'product_support'` describes what a role does, but displays as "SM" (Support Manager abbreviation)
- A developer reading the code would expect `'sm'` to display as "SM"
- A developer would expect `'product_support'` to display as "Product Support"
- **Reality:** It's the opposite.

### 5.2 Hardcoded Checks Using the String Values

**Location:** `/src/App.tsx` (lines 45-50)

```typescript
if (selectedRole === 'sm') {
  navigate('/submit');
} else if (selectedRole === 'product_support') {
  navigate('/loan-issue');
} else {
  navigate('/submissions');
}
```

**Key Observation:** The code checks exact string values (`'sm'` and `'product_support'`), not the labels. This is **correct and working**, even though the labels are confusing.

**Location:** `/src/components/ProtectedRoute.tsx`

```typescript
<ProtectedRoute allowedRoles={['sm', 'tech_support_team']}>
```

**Again:** Using the exact string values, not labels.

### 5.3 Validation in Auth Context

**Location:** `/src/contexts/SimpleAuthContext.tsx` (line 27)

```typescript
if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support') {
  setRole(storedRole);
  setIsAuthenticated(true);
}
```

**Key Observation:** The validation explicitly checks all three string values. If localStorage has `{ "role": "sm" }`, it passes validation because `'sm'` matches.

### 5.4 Why You MUST NOT "Fix" This

**Scenario:** A developer decides to "fix" the confusion:

```typescript
// "Fix" the confusion by renaming roles to match labels
export type UserRole = 'support_manager' | 'tech_support_team' | 'product_support_agent';

const roles = [
  { value: 'support_manager', label: 'Product Support' },
  { value: 'tech_support_team', label: 'Tech Support' },
  { value: 'product_support_agent', label: 'SM' },
];
```

**What Breaks:**

1. **All existing route guards break:**
   ```typescript
   // Old code checks 'sm', but role is now 'support_manager'
   allowedRoles={['sm']}  // BROKEN - will never match
   ```

2. **All localStorage sessions become invalid:**
   ```typescript
   // Stored in localStorage: { "role": "sm" }
   // New validation: if (storedRole === 'support_manager' || ...)
   // BROKEN - 'sm' doesn't match any validation
   // User is logged out, cannot recover
   ```

3. **The database (if any) has hard-coded values:**
   ```typescript
   // Submissions table: submittedBy = 'sm'
   // New code expects: submittedBy = 'support_manager'
   // BROKEN - historical data is inconsistent
   ```

4. **Navigation logic breaks:**
   ```typescript
   // Old: if (selectedRole === 'sm') navigate('/submit')
   // New code gets 'support_manager'
   // BROKEN - conditional never matches
   ```

**Why It's Confusing But WORKING:**
- The labels in the UI are backwards, yes
- But the **string values** are used consistently everywhere
- The backend logic matches the string values, not the labels
- Users log in, select a role (which shows the label), and the login handler uses the string value
- Everything works, even though it's confusing to read

**The Principle:** Don't optimize for code readability at the cost of breaking functionality. The confusion is in the **documentation** (the labels), not the **logic** (the string values). Better to leave it alone and document the confusion (which is what this guide does) than to "fix" it and break everything.

---

## 6. AUTH FLOW PRESERVATION

When adding features that interact with authentication, match the existing auth check pattern exactly.

### 6.1 Project 1: SimpleAuthContext Pattern

**Pattern:** In-memory state + localStorage persistence, hardcoded password validation.

**When Adding a Feature That Needs Auth:**

✓ **DO THIS - Use the existing auth hook:**
```typescript
import { useSimpleAuth } from '@/contexts/SimpleAuthContext';

function MyNewFeature() {
  const { role, isAuthenticated } = useSimpleAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <YourComponent />;
}
```

✓ **DO THIS - Wrap routes with ProtectedRoute:**
```typescript
<Route
  path="/my-feature"
  element={
    <ProtectedRoute allowedRoles={['sm']}>
      <MyNewFeature />
    </ProtectedRoute>
  }
/>
```

✗ **DON'T DO THIS - Add another auth method:**
```typescript
// WRONG - Creates parallel auth system
const [localAuth, setLocalAuth] = useState(null);
useEffect(() => {
  const localSession = localStorage.getItem('my_feature_session');
  // ...
});
```

✗ **DON'T DO THIS - Check localStorage directly:**
```typescript
// WRONG - Bypasses the auth context
const role = JSON.parse(localStorage.getItem('issue_tracker_auth')).role;
```

**Why:** SimpleAuthContext is the single source of truth for auth. Checking localStorage directly or creating parallel systems leads to inconsistency and bugs.

### 6.2 Project 2: Supabase + Cache Pattern

**Pattern:** Supabase OAuth + role lookup from `allowed_users` table + 8-hour localStorage cache with background revalidation.

**When Adding a Feature That Needs Auth:**

✓ **DO THIS - Use the existing auth hook:**
```typescript
import { useAuth } from '../context/AuthContext';

function MyNewFeature() {
  const { currentUser, loading } = useAuth();

  if (loading) return <LoadingSpinner />;
  if (!currentUser) return <Navigate to="/login" />;

  if (currentUser.role === 'admin') {
    return <AdminFeature />;
  } else if (currentUser.role === 'product_support') {
    return <ProductSupportFeature />;
  }
}
```

✗ **DON'T DO THIS - Query Supabase directly in component:**
```typescript
// WRONG - Bypasses auth context
useEffect(() => {
  supabase.from('allowed_users').select('role').eq('email', email).then(...);
});
```

✗ **DON'T DO THIS - Check cache directly:**
```typescript
// WRONG - Bypasses auth context and revalidation
const cached = JSON.parse(localStorage.getItem('los_cached_role'));
if (cached && Date.now() - cached.ts < TTL) {
  // Use cached role
}
```

**Why:** AuthContext manages the complex flow: cache hit → background revalidation → error handling. If you query directly, you bypass this logic.

### 6.3 When to Add New Auth Tokens/Claims

**Rule:** Don't. Use the existing auth system as-is.

**Exception:** If you absolutely must:

1. **Don't change the token format.** If Project 2 uses `{ id, email, role, name }`, don't add fields.
2. **Check all consumers.** Any code that creates, reads, or validates the token must be updated.
3. **Verify type definitions.** Update the `User` interface in all places it's imported.
4. **Test backward compatibility.** Can old tokens still work, or do you require a re-login?

**Example: Adding a `permissions` field to Project 2's User**

**Wrong:**
```typescript
// File: /src/context/AuthContext.tsx
function buildUser(supabaseUser: SupabaseUser, role: 'product_support' | 'admin', displayName: string | null): User {
  return {
    id: supabaseUser.id,
    email: supabaseUser.email || '',
    name: displayName || supabaseUser.email?.split('@')[0] || 'User',
    role,
    permissions: calculatePermissions(role), // NEW FIELD - BREAKS EXISTING CACHE
  };
}
```

**Problem:** Cached User objects in localStorage won't have `permissions`. When you load from cache, the new field is missing, causing undefined errors.

**Right:**
```typescript
// File: /src/types/index.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'product_support' | 'admin';
  // If you need permissions, compute them at runtime, not in the User object
}

// File: /src/hooks/usePermissions.ts (NEW)
export function usePermissions() {
  const { currentUser } = useAuth();

  return {
    canViewAdmin: currentUser?.role === 'admin',
    canViewReports: currentUser?.role === 'admin',
    // etc.
  };
}

// Usage:
function MyComponent() {
  const { canViewAdmin } = usePermissions();
  if (canViewAdmin) { /* render */ }
}
```

**Why This Works:** You're not changing the User object structure, so cached data still works. Permissions are computed at runtime based on role, which is the source of truth.

---

## 7. FEATURE ADDITION CHECKLIST

When adding a new feature that touches roles/auth:

### Before You Start
- [ ] Understand the existing role system (use Section 1 of this guide)
- [ ] Identify all hardcoded role checks in the codebase
- [ ] Find the auth context / auth hook
- [ ] Locate the ProtectedRoute or route guard component

### Adding a New Role
- [ ] Add role to type definition (Section 2.1-2.2)
- [ ] Add role to login selector (copy existing pattern)
- [ ] Add role to auth validation logic
- [ ] Create routes/views for the new role (isolated, don't modify existing)
- [ ] Add role to post-login redirect logic
- [ ] Test all existing roles still work (refresh, logout/login, localStorage persistence)
- [ ] Only then test the new role

### Adding New Permissions/Features for Existing Role
- [ ] Don't create a new permission system
- [ ] Use existing auth checks (allowedRoles, conditional role checks)
- [ ] Create new routes with existing ProtectedRoute
- [ ] Test all affected routes work correctly

### Database Schema Changes
- [ ] If adding a new role: ensure database has the new role value
- [ ] If removing a role: ensure no existing data uses it (backfill or migrate)
- [ ] If changing role strings: update all queries that check role values
- [ ] Document the change and migration process

### After Deployment
- [ ] Verify existing users can still log in
- [ ] Verify existing roles redirect to expected pages
- [ ] Verify localStorage sessions still work (refresh the page)
- [ ] Check error logs for any hardcoded role checks that broke
- [ ] Monitor for "404 on /login" or auth context errors

---

## 8. SUMMARY: THE WORKFLOW GUARDIAN PRINCIPLE

**Workflow Guardian exists to prevent Claude from breaking existing applications when adding features.**

**The Core Principle: "Match, Don't Fix"**

1. **Document the status quo** — Understand how roles and permissions work exactly as they are, including any confusing patterns (Section 1)
2. **Extend, don't refactor** — Add new roles/features using the existing patterns, even if they seem ugly (Section 2-3)
3. **Avoid dangerous refactorings** — Never consolidate names, create RBAC systems, add hierarchies, or move auth to the database (Section 4)
4. **Preserve auth flows** — Use existing auth hooks and patterns, don't create parallel systems (Section 6)
5. **Test thoroughly** — Verify existing functionality still works before deploying new features (Section 7)

**Why This Matters:**

Existing applications have hardcoded role checks scattered throughout the codebase. These checks are in route guards, conditionals, localStorage validation, database queries, and UI displays. A single rename or refactoring breaks all of them simultaneously.

Example: If you rename `'sm'` to `'support_manager'` in the type definition, you've broken:
- Every `allowedRoles={['sm']}` check (18 locations)
- Every `role === 'sm'` conditional (5 locations)
- Every localStorage validation (1 location)
- Every database record with `role = 'sm'` (unknown quantity)
- Every cached role in users' browsers

**That's 25+ places to update, each with risk of missing one and creating a broken state.**

By "Matching, Don't Fixing," you:
- Add new roles alongside existing ones (1 location update per feature)
- Avoid touching existing role logic
- Enable safe, incremental feature development
- Preserve the existing application's correctness

**Workflow Guardian's job is to remind you of this principle whenever you're tempted to "improve" the role system.**
