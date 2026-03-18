# Workflow Guardian: Real-World Scenario Playbooks

## Overview

This document contains 10 practical, step-by-step playbooks for the most common feature addition scenarios. Each playbook walks through the complete lifecycle from request analysis through verification, with concrete commands, files to check, patterns to match, and verification checklists.

**Master Workflow:**
1. **Recon Phase** - Understand the existing system
2. **Impact Phase** - Map what changes will affect
3. **Implement Phase** - Make changes carefully
4. **Verify Phase** - Confirm nothing broke

---

## SCENARIO 1: Add a New Page/Route

### When You Receive This Request
"Add a new [Dashboard/Settings/Admin] page accessible at /[path]"

### Phase 1: Recon - Understand Existing Route System

#### Step 1.1: Run Initial Codebase Analysis
```bash
# Find all route/page definitions
grep -r "Route\|path=" src/ --include="*.tsx" --include="*.ts" --include="*.jsx" --include="*.js" | head -20

# Find routing configuration file
find src -name "*route*" -o -name "*router*" | head -10
```

#### Step 1.2: Identify the Router/Route Configuration File
Look for these common patterns:
- `src/router.ts` or `src/router/index.ts`
- `src/App.tsx` (if using inline routing)
- `src/routes/index.ts` or `src/config/routes.ts`
- Next.js: `app/` or `pages/` directory structure
- Remix: `routes/` directory

**Check the file:**
```bash
cat src/router.ts
# or
cat src/App.tsx | grep -A 5 "Route"
```

#### Step 1.3: Read System Map to Understand Current Pages
```bash
# List all existing pages
find src/pages -type f -name "*.tsx" | sort
# or for component-based routing
find src -path "*pages*" -name "*.tsx" | sort

# Count existing routes
grep -r "path=" src/router.ts | wc -l
```

#### Step 1.4: Examine Existing Page Pattern (Copy Nearest Similar)
If adding a Dashboard page:
```bash
# Find existing dashboard-like pages
find src/pages -name "*Dashboard*" -o -name "*Home*" -o -name "*Overview*"

# Read the structure of the most similar page
cat src/pages/Dashboard.tsx
```

**Look for:**
- Layout wrapper used (e.g., `<MainLayout>`, `<AuthLayout>`)
- How data is fetched (useEffect, custom hook, server component)
- What components are composed
- TypeScript interfaces used
- Styling approach (CSS modules, Tailwind, styled-components)

### Phase 2: Impact - Map Change Propagation

#### Step 2.1: Identify Affected Files
1. **Route configuration file** - needs new route entry
2. **Navigation/sidebar component** - needs menu item
3. **Type definitions** - if needed
4. **Role/permission system** - if page is role-restricted
5. **Layout files** - if special layout needed

```bash
# Find navigation/sidebar components
grep -r "nav\|sidebar\|menu" src/ --include="*.tsx" -l | grep -i "component\|layout" | head -5

# Find role definitions
grep -r "role\|permission" src/ --include="*.ts" -l | head -3
```

#### Step 2.2: Check Existing Route Order
```bash
# Critical: Look for catch-all routes
grep -E "\*|catch.*all|:id|\[\.\.\." src/router.ts | head -5

# List routes in order
grep "path=" src/router.ts | head -20
```

**Key insight:** New specific routes MUST come BEFORE catch-all routes (`*`, `/:id/*`)

#### Step 2.3: Check Role Guards on Existing Pages
```bash
# Find role/permission patterns
grep -A 3 -B 1 "isAdmin\|useRole\|useAuth\|canAccess" src/pages/*.tsx | head -20
```

### Phase 3: Implement - Add New Page Safely

#### Step 3.1: Create New Page File
Copy the structure of the most similar existing page:
```bash
# If Dashboard exists, copy its structure
cp src/pages/Dashboard.tsx src/pages/NewFeature.tsx
```

Edit the new file:
- Replace component name: `Dashboard` → `NewFeature`
- Update any hardcoded titles/labels
- Clear out dashboard-specific data fetching
- Keep the layout, styling, and structural patterns identical

**Pattern to follow:**
```tsx
import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/MainLayout';

export default function NewFeaturePage() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    // Fetch data if needed
  }, []);

  return (
    <MainLayout>
      <div className="page-container">
        <h1>New Feature Title</h1>
        {/* Content here */}
      </div>
    </MainLayout>
  );
}
```

#### Step 3.2: Add Route in Correct Configuration File
**Find the router file:**
```bash
cat src/router.ts
```

**Exact placement rule:**
```
✓ CORRECT:
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/new-feature" element={<NewFeature />} />  // ADD HERE
  <Route path="/settings" element={<Settings />} />
  <Route path="*" element={<NotFound />} />  // Catch-all LAST
</Routes>

✗ WRONG - After catch-all:
<Routes>
  ...
  <Route path="*" element={<NotFound />} />
  <Route path="/new-feature" element={<NewFeature />} />  // UNREACHABLE
</Routes>
```

**Implementation:**
```bash
# Check exact line number of catch-all route
grep -n "\*\|catch" src/router.ts

# Add import at top
# Add route before catch-all
```

#### Step 3.3: Update Navigation Menu
Find navigation/sidebar:
```bash
grep -r "Dashboard\|Settings" src/components --include="*.tsx" -l | head -3
```

Read the navigation component:
```bash
cat src/components/Sidebar.tsx
# or
cat src/components/Navigation.tsx
```

**Pattern to match:**
```tsx
const menuItems = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'New Feature', path: '/new-feature' },  // ADD HERE
  { label: 'Settings', path: '/settings' },
];
```

#### Step 3.4: Add Role Guard (If Needed)
Check if similar pages have role guards:
```bash
grep -A 2 "NewFeaturePage" src/router.ts
grep -B 5 -A 5 "isAdmin\|useRole" src/pages/AdminPage.tsx 2>/dev/null | head -15
```

**If role guard needed, wrap in router:**
```tsx
<Route
  path="/admin-feature"
  element={
    <ProtectedRoute roles={['admin']}>
      <NewFeature />
    </ProtectedRoute>
  }
/>
```

Or in the page component itself:
```tsx
export default function NewFeaturePage() {
  const { role } = useAuth();

  if (role !== 'admin') {
    return <UnauthorizedPage />;
  }

  return (/* page content */);
}
```

### Phase 4: Verify - Confirm Nothing Broke

#### Verification Checklist
- [ ] All existing routes still accessible (test 5+ existing pages)
- [ ] New page accessible at correct URL
- [ ] Navigation menu displays new item in correct order
- [ ] New page has correct layout and styling
- [ ] If role-protected: non-authorized users cannot access
- [ ] If role-protected: authorized users can access
- [ ] No console errors on any page
- [ ] No TypeScript errors: `npm run type-check` passes
- [ ] Mobile responsive (if applicable)

#### Step 4.1: Manual Testing
```bash
# Start dev server
npm run dev

# Test in browser
# 1. Visit existing page: http://localhost:3000/dashboard
# 2. Verify sidebar/nav loads correctly
# 3. Click on new feature in nav
# 4. Verify new page loads at /new-feature
# 5. Go back to existing pages, verify they still work
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Run tests if they exist
npm run test -- --testPathPattern="router\|navigation" 2>/dev/null || echo "No tests found"

# Check no import errors
grep -r "from.*NewFeature" src/ --include="*.tsx" | wc -l
# Should be: 1 (only in router.ts)
```

#### Step 4.3: Common Issues and Fixes

**Problem: New page returns 404**
```
Cause: Route added AFTER catch-all route
Fix: Move route definition before catch-all//:id/* routes
Verify: grep -n "path.*\*" src/router.ts shows catch-all at END
```

**Problem: Menu item doesn't appear**
```
Cause: Navigation component not updated or wrong path
Fix: Verify path in menu item matches route path exactly
Verify: grep "new-feature" src/components/Navigation.tsx
```

**Problem: Role guard not working**
```
Cause: Wrong role value or missing role provider
Fix: Check useAuth() hook returns role correctly
Verify: console.log in page shows correct role value
```

**Problem: Page has wrong layout/styling**
```
Cause: Used wrong layout component or different CSS
Fix: Copy layout wrapper from similar existing page
Verify: Compare Layout wrapper with Dashboard component
```

---

## SCENARIO 2: Add a New Field to an Existing Form

### When You Receive This Request
"Add a [name/email/date] field to the [User/Product/Order] form"

### Phase 1: Recon - Understand Form Structure

#### Step 1.1: Find the Form Component
```bash
# Find all forms in the app
find src -name "*Form*" -o -name "*form*" | grep -E "\.tsx?$"

# Search for the specific form
grep -r "UserForm\|ProfileForm\|RegistrationForm" src/ --include="*.tsx" -l
```

#### Step 1.2: Read the Entire Form File
```bash
# Read complete form structure
cat src/components/UserForm.tsx | head -100
# or if large:
wc -l src/components/UserForm.tsx
```

**Understand:**
- Framework used (React Hook Form, Formik, custom)
- TypeScript type definition for form data
- How fields are structured (naming, validation)
- How errors are displayed
- CSS classes used for styling

#### Step 1.3: Check TypeScript Type Definition
```bash
# Find type definition
grep -B 5 -A 10 "interface.*User\|type.*User" src/types/index.ts

# Or in same file
grep -B 2 -A 8 "interface.*Form" src/components/UserForm.tsx
```

**Look for:**
```typescript
interface UserFormData {
  name: string;
  email: string;
  // New field goes here
}
```

#### Step 1.4: Identify Field Patterns
```bash
# Check how existing fields are implemented
grep -A 5 "email\|name" src/components/UserForm.tsx | head -30

# Check validation patterns
grep -B 2 -A 2 "required\|pattern\|validate" src/components/UserForm.tsx | head -20
```

**Common patterns to find:**
- Input type (text, email, date, number)
- Validation (required, pattern, min/max)
- Error display (className="error", error?.message)
- Label styling (className for labels)

#### Step 1.5: Check Display/Summary Components
```bash
# Find where form data is displayed
grep -r "user\.name\|user\.email" src/ --include="*.tsx" -l

# Check detail view component
cat src/components/UserDetail.tsx 2>/dev/null || cat src/pages/UserDetail.tsx
```

### Phase 2: Impact - Map Change Propagation

#### Step 2.1: Identify All Affected Files
```bash
# 1. Form component itself
echo "Form component: src/components/UserForm.tsx"

# 2. Type definitions
grep -r "interface UserFormData\|type.*UserForm" src/ --include="*.ts" -l

# 3. API/Database layer
grep -r "updateUser\|postUser" src/ --include="*.ts" -l

# 4. Display components
grep -r "user\." src/pages --include="*.tsx" -l | head -5

# 5. Tests
find src -path "*test*" -o -path "*spec*" | grep -i user | head -5
```

#### Step 2.2: Check Form Submission Handler
```bash
# Find what happens when form submits
grep -A 10 "onSubmit\|handleSubmit" src/components/UserForm.tsx
```

**Check if it:**
- Makes API call
- Updates database directly
- Dispatches Redux action
- Updates local state
- Returns data to parent

#### Step 2.3: Check Database Schema
```bash
# If using database schema file
find src -name "*.sql" -o -name "*schema*" | head -5
cat src/db/schema.sql 2>/dev/null | grep -A 5 "CREATE TABLE users"

# If using ORM (Prisma, etc)
cat prisma/schema.prisma 2>/dev/null | grep -A 10 "model User"

# If using Firebase
grep -r "users.*collection\|user.*schema" src/config --include="*.ts"
```

### Phase 3: Implement - Add Field Following Patterns

#### Step 3.1: Extend TypeScript Type
**Find the type:**
```bash
grep -n "interface UserFormData" src/components/UserForm.tsx
```

**Pattern to follow:**
```typescript
// BEFORE
interface UserFormData {
  name: string;
  email: string;
}

// AFTER - add optional if field is optional
interface UserFormData {
  name: string;
  email: string;
  phone?: string;  // NEW - optional because not critical
}
```

**Key rule:** If field is not required by business logic, make it optional (`?`)

#### Step 3.2: Add Field to Form JSX
Copy the exact pattern of an existing field:

**Find existing similar field:**
```bash
# For text fields
grep -A 8 'name="email"' src/components/UserForm.tsx

# For date fields
grep -A 8 'type="date"' src/components/UserForm.tsx

# For select fields
grep -A 12 '<select' src/components/UserForm.tsx
```

**Example - adding phone field:**
```tsx
// COPY THIS PATTERN from existing email field

// BEFORE (existing email field)
<label htmlFor="email">Email</label>
<input
  type="email"
  id="email"
  name="email"
  className="form-input"
  {...register('email', {
    required: 'Email is required',
    pattern: { value: /\S+@\S+/, message: 'Invalid email' }
  })}
/>
{errors.email && <span className="error-message">{errors.email.message}</span>}

// AFTER (add new phone field with same pattern)
<label htmlFor="email">Email</label>
<input
  type="email"
  id="email"
  name="email"
  className="form-input"
  {...register('email', {
    required: 'Email is required',
    pattern: { value: /\S+@\S+/, message: 'Invalid email' }
  })}
/>
{errors.email && <span className="error-message">{errors.email.message}</span>}

{/* NEW FIELD - SAME PATTERN */}
<label htmlFor="phone">Phone</label>
<input
  type="tel"
  id="phone"
  name="phone"
  className="form-input"
  {...register('phone', {
    pattern: { value: /^\d{10}$/, message: 'Phone must be 10 digits' }
  })}
/>
{errors.phone && <span className="error-message">{errors.phone.message}</span>}
```

**Critical matching rules:**
- Same className: `form-input`
- Same label structure with htmlFor
- Same error display pattern
- Same spacing/layout around field

#### Step 3.3: Update Form Submission Handler
```bash
# Find current handler
grep -A 15 "const handleSubmit\|const onSubmit" src/components/UserForm.tsx
```

**Pattern:**
```typescript
// BEFORE
const handleSubmit = async (data: UserFormData) => {
  await updateUser({
    name: data.name,
    email: data.email
  });
};

// AFTER - just add the new field
const handleSubmit = async (data: UserFormData) => {
  await updateUser({
    name: data.name,
    email: data.email,
    phone: data.phone  // NEW
  });
};
```

#### Step 3.4: Update Display/Detail Components
Find where user data is shown:
```bash
cat src/components/UserDetail.tsx
# or
cat src/pages/UserProfile.tsx
```

**Add display of new field:**
```tsx
// BEFORE
<div className="user-info">
  <p><strong>Name:</strong> {user.name}</p>
  <p><strong>Email:</strong> {user.email}</p>
</div>

// AFTER
<div className="user-info">
  <p><strong>Name:</strong> {user.name}</p>
  <p><strong>Email:</strong> {user.email}</p>
  {user.phone && <p><strong>Phone:</strong> {user.phone}</p>}  // NEW
</div>
```

#### Step 3.5: Update Database Schema (If Needed)
**If using Prisma:**
```prisma
model User {
  id String @id
  name String
  email String
  phone String?  // NEW - optional
  createdAt DateTime @default(now())
}
```

**Run migration:**
```bash
npx prisma migrate dev --name add_phone_to_user
```

**If using SQL:**
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

**If using Firebase:**
Usually handled automatically by Firestore document schema.

#### Step 3.6: Update API Endpoint (If Needed)
```bash
# Find API handler
grep -r "POST.*user\|PUT.*user" src/api --include="*.ts" -l

# Read handler
cat src/api/users.ts | grep -A 20 "export.*PUT\|export.*POST"
```

**Pattern:**
```typescript
// BEFORE
export const updateUser = async (userId: string, data: UserFormData) => {
  const response = await fetch(`/api/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify({
      name: data.name,
      email: data.email
    })
  });
};

// AFTER
export const updateUser = async (userId: string, data: UserFormData) => {
  const response = await fetch(`/api/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify({
      name: data.name,
      email: data.email,
      phone: data.phone  // NEW
    })
  });
};
```

### Phase 4: Verify - Test All Existing Fields Still Work

#### Verification Checklist
- [ ] Form displays all existing fields correctly
- [ ] Form displays new field with correct input type
- [ ] Existing field validation still works (test required, pattern)
- [ ] Existing field error messages display correctly
- [ ] New field validation works (if applicable)
- [ ] New field is optional/required as intended
- [ ] Form submits successfully with new field populated
- [ ] Form submits successfully with new field empty (if optional)
- [ ] Form submits successfully with only existing fields
- [ ] Existing fields show correct values when editing
- [ ] New field shows correct value when editing
- [ ] Display components show existing fields
- [ ] Display components show new field when present
- [ ] Display components don't break if new field is missing

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Load the form page
# 2. Verify all existing fields render
# 3. Verify new field renders with correct input type
# 4. Submit form with only required fields
#    - Confirm existing fields saved
#    - Confirm new field not required (if optional)
# 5. Submit form with new field filled
#    - Confirm all fields saved
# 6. Edit an existing user
#    - Verify all existing fields pre-populate
#    - Verify new field pre-populates (if applicable)
# 7. Test validation on new field
#    - Enter invalid data
#    - Confirm error message shows
#    - Confirm error matches pattern
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check - verify type is used correctly
npm run type-check

# Find all uses of the form
grep -r "UserFormData\|UserForm" src/ --include="*.tsx" --include="*.ts"

# Verify form exports
grep "export.*UserForm\|export.*UserFormData" src/components/UserForm.tsx
```

#### Step 4.3: Common Issues and Fixes

**Problem: Form validation error on submit**
```
Cause: New field type doesn't match API expectation
Fix: Check API schema matches field type (string, number, date)
Verify: Check API error message in browser console
```

**Problem: Existing field validation breaks**
```
Cause: Accidentally modified existing field pattern
Fix: Compare field with backup copy from git
Verify: git diff src/components/UserForm.tsx | grep -A3 -B3 "existing_field"
```

**Problem: Field doesn't save to database**
```
Cause: Database schema not updated or API not handling new field
Fix: Check database has column for new field
Verify: SELECT * FROM users LIMIT 1; shows new column
```

**Problem: Display component doesn't show new field**
```
Cause: Didn't update detail/summary component
Fix: Add new field to display component like existing fields
Verify: grep "phone" src/components/UserDetail.tsx shows new field
```

---

## SCENARIO 3: Add a New Role/Permission

### When You Receive This Request
"Add a new [moderator/viewer/contributor] role with [specific permissions]"

### Phase 1: Recon - Inventory Existing Role System

#### Step 1.1: Find Role Definitions
```bash
# Find where roles are defined
grep -r "role.*=\|Role\|ROLES\|roles" src/ --include="*.ts" --include="*.tsx" | grep -i "const\|enum\|type" | head -20

# Find role files
find src -name "*role*" -o -name "*auth*" | grep -E "\.ts$" | head -10
```

#### Step 1.2: Identify Current Roles
```bash
# Read role definitions file
cat src/types/roles.ts 2>/dev/null || \
cat src/constants/roles.ts 2>/dev/null || \
cat src/enums/roles.ts 2>/dev/null || \
grep -A 10 "enum Role\|type Role\|const ROLES" src/auth/index.ts | head -15
```

**Pattern to find:**
```typescript
enum Role {
  ADMIN = 'admin',
  USER = 'user',
  // NEW ROLE GOES HERE
}

// OR

const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  // NEW ROLE GOES HERE
} as const;

// OR

type Role = 'admin' | 'user';  // NEW ROLE GOES HERE
```

#### Step 1.3: Find Where Roles Are Checked
```bash
# Find all role checks
grep -r "role.*==\|role.*===\|hasRole\|isAdmin" src/ --include="*.tsx" --include="*.ts" | head -20

# Find permission guards
grep -r "ProtectedRoute\|requireRole\|canAccess\|authorize" src/ --include="*.tsx" --include="*.ts" | head -10
```

#### Step 1.4: Find Login/Registration with Role Selection
```bash
# Find login component
find src -name "*Login*" -o -name "*SignIn*" | grep -E "\.tsx?$"

# Read login component
cat src/pages/Login.tsx | grep -A 30 "role\|Role"

# Find registration
find src -name "*Register*" -o -name "*SignUp*" | grep -E "\.tsx?$"
```

#### Step 1.5: Find Role-Based Conditional Renders
```bash
# Find where components render differently by role
grep -B 3 -A 3 "role.*admin\|role.*user\|role ===" src/components/*.tsx | head -30

# Find all useAuth or useRole hooks
grep -r "useRole\|useAuth" src/ --include="*.tsx" | head -10
```

### Phase 2: Impact - Map Where Roles Are Used

#### Step 2.1: Create Role Usage Map
```bash
# Find route guards
grep -r "path.*role\|protected.*route\|requireRole" src/router.ts --include="*.ts" | head -10

# Find component-level guards
grep -B 2 "role ===\|role ==\|isAdmin\|isModerator" src/components/*.tsx | head -20

# Find conditional renders
grep -r "role ===.*admin\|role ==.*user" src/ --include="*.tsx" | head -15
```

#### Step 2.2: Find All Display Changes by Role
```bash
# Find navigation that changes by role
grep -B 5 -A 5 "role.*nav\|role.*menu" src/components/*.tsx

# Find buttons/actions that show/hide by role
grep -B 2 "role.*button\|role.*delete\|role.*edit" src/components/*.tsx | head -20
```

#### Step 2.3: Check Database for Role Column
```bash
# Find user schema
grep -A 10 "CREATE TABLE.*user\|model User" src/db/schema.sql 2>/dev/null || \
grep -A 10 "model User" prisma/schema.prisma 2>/dev/null

# Find user type
grep -A 5 "interface User\|type User" src/types/index.ts
```

### Phase 3: Implement - Add New Role Following Patterns

#### Step 3.1: Add New Role Constant
Find role definitions file:
```bash
cat src/types/roles.ts
```

**Pattern to follow:**
```typescript
// BEFORE
enum Role {
  ADMIN = 'admin',
  USER = 'user',
}

// AFTER
enum Role {
  ADMIN = 'admin',
  MODERATOR = 'moderator',  // NEW ROLE
  USER = 'user',
}
```

**Alternative patterns:**
```typescript
// If using const ROLES object:
// BEFORE
const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
} as const;

// AFTER
const ROLES = {
  ADMIN: 'admin',
  MODERATOR: 'moderator',  // NEW ROLE
  USER: 'user',
} as const;

// If using type union:
// BEFORE
type Role = 'admin' | 'user';

// AFTER
type Role = 'admin' | 'moderator' | 'user';
```

#### Step 3.2: Add Role to Login Selector
Find login/auth component:
```bash
grep -n "role.*select\|select.*role" src/pages/Login.tsx -A 10 -B 2
```

**Pattern to follow:**
```tsx
// BEFORE
<select name="role" value={role} onChange={(e) => setRole(e.target.value)}>
  <option value="admin">Admin</option>
  <option value="user">User</option>
</select>

// AFTER
<select name="role" value={role} onChange={(e) => setRole(e.target.value)}>
  <option value="admin">Admin</option>
  <option value="moderator">Moderator</option>  {/* NEW ROLE */}
  <option value="user">User</option>
</select>
```

#### Step 3.3: Add Role to Registration
Find registration component:
```bash
find src -name "*Register*" -o -name "*Signup*" | head -1 | xargs cat | grep -A 20 "role"
```

**Same pattern as login:**
```tsx
// BEFORE
const roles = ['admin', 'user'];

// AFTER
const roles = ['admin', 'moderator', 'user'];  // NEW ROLE
```

#### Step 3.4: Add Route Guards for New Role
Find router file:
```bash
grep -n "ProtectedRoute\|requireRole" src/router.ts | head -10
```

**Pattern to follow:**
```tsx
// BEFORE
<Route
  path="/admin"
  element={
    <ProtectedRoute roles={['admin']}>
      <AdminPage />
    </ProtectedRoute>
  }
/>

// AFTER - add moderator access where appropriate
<Route
  path="/admin"
  element={
    <ProtectedRoute roles={['admin']}>
      <AdminPage />
    </ProtectedRoute>
  }
/>

<Route
  path="/moderation"
  element={
    <ProtectedRoute roles={['admin', 'moderator']}>  {/* NEW ROLE */}
      <ModerationPage />
    </ProtectedRoute>
  }
/>
```

#### Step 3.5: Add Conditional Renders by Role
Find component-level permission checks:
```bash
grep -n "role.*admin\|useAuth" src/components/UserActions.tsx | head -10
```

**Pattern to follow:**
```tsx
// BEFORE
export function UserActions({ userId }) {
  const { role } = useAuth();

  return (
    <div>
      {role === 'admin' && <DeleteButton userId={userId} />}
      <EditButton userId={userId} />
    </div>
  );
}

// AFTER
export function UserActions({ userId }) {
  const { role } = useAuth();

  return (
    <div>
      {role === 'admin' && <DeleteButton userId={userId} />}
      {(role === 'admin' || role === 'moderator') && (  {/* NEW ROLE */}
        <SuspendButton userId={userId} />
      )}
      <EditButton userId={userId} />
    </div>
  );
}
```

#### Step 3.6: Add Role to Navigation/Sidebar
Find navigation component:
```bash
cat src/components/Navigation.tsx | grep -A 30 "nav\|menu"
```

**Pattern to follow:**
```tsx
// BEFORE
const navItems = [
  { label: 'Users', path: '/users', roles: ['admin'] },
  { label: 'Dashboard', path: '/dashboard', roles: ['admin', 'user'] },
];

// AFTER
const navItems = [
  { label: 'Users', path: '/users', roles: ['admin'] },
  { label: 'Moderation', path: '/moderation', roles: ['admin', 'moderator'] },  {/* NEW */}
  { label: 'Dashboard', path: '/dashboard', roles: ['admin', 'moderator', 'user'] },
];

return (
  <nav>
    {navItems.map(item =>
      item.roles.includes(userRole) && (
        <Link key={item.path} to={item.path}>{item.label}</Link>
      )
    )}
  </nav>
);
```

#### Step 3.7: Update Database/Auth Schema
**If using Prisma:**
```prisma
model User {
  id String @id
  email String @unique
  role String  // Update to enum or add validation
  createdAt DateTime @default(now())
}
```

**If using database:**
```sql
-- Update role enum if exists
ALTER TABLE users MODIFY COLUMN role ENUM('admin', 'moderator', 'user');

-- Or ensure role column exists
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';
```

### Phase 4: Verify - Confirm All Existing Roles Still Work

#### Verification Checklist
- [ ] Admin role still works (all permissions intact)
- [ ] User role still works (no new permissions)
- [ ] New moderator role accessible in login selector
- [ ] New role can be assigned during registration
- [ ] Routes protected for admin-only still require admin
- [ ] Routes protected for new role accessible with new role
- [ ] Navigation shows correct items for admin
- [ ] Navigation shows correct items for user
- [ ] Navigation shows correct items for new role
- [ ] Conditional renders show/hide correctly for all roles
- [ ] No TypeScript errors: `npm run type-check` passes
- [ ] Login with each role works correctly

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Go to login, verify new role in dropdown
# 2. Try to register with new role
# 3. Login as ADMIN
#    - Verify can access admin pages
#    - Verify see all navigation items
# 4. Login as MODERATOR (new)
#    - Verify can access moderator pages
#    - Verify moderation buttons appear
#    - Verify cannot access admin-only pages
# 5. Login as USER
#    - Verify still works like before
#    - Verify new role not accessible
#    - Verify cannot see new role actions
```

#### Step 4.2: Automated Verification
```bash
# Check all role references
grep -r "role.*admin\|role.*moderator\|role.*user" src/ --include="*.tsx" --include="*.ts" | wc -l

# TypeScript check
npm run type-check

# Check enum was updated everywhere
grep -r "Role\." src/ --include="*.tsx" --include="*.ts" | head -10
```

#### Step 4.3: Common Issues and Fixes

**Problem: New role doesn't appear in login selector**
```
Cause: Selector not updated or hardcoded array used
Fix: Add new role to registration options array
Verify: grep "moderator" src/pages/Login.tsx shows in dropdown
```

**Problem: User can access pages they shouldn't**
```
Cause: Route guard not updated or condition wrong
Fix: Check ProtectedRoute roles array includes all permitted roles
Verify: <ProtectedRoute roles={['admin', 'moderator']}> has correct roles
```

**Problem: Navigation doesn't update**
```
Cause: Navigation component hardcodes role or uses old roles array
Fix: Update roles array in navigation component
Verify: Logged in as new role, see new nav items
```

**Problem: TypeScript errors after adding role**
```
Cause: Role string doesn't match enum
Fix: Use enum value: Role.MODERATOR instead of 'moderator'
Verify: npm run type-check passes without errors
```

---

## SCENARIO 4: Add a New Dashboard Widget/Card

### When You Receive This Request
"Add a [stats/chart/recent items] widget to the dashboard"

### Phase 1: Recon - Understand Dashboard Layout

#### Step 1.1: Find Dashboard Component
```bash
# Find dashboard
find src/pages -name "*Dashboard*" -o -name "*Home*" | head -1

# Read it
cat src/pages/Dashboard.tsx | head -50
```

#### Step 1.2: Analyze Existing Widget Patterns
```bash
# Find all card/widget components
find src/components -name "*Card*" -o -name "*Widget*" | head -5

# Look at existing widgets
cat src/components/DashboardCard.tsx 2>/dev/null || \
cat src/components/StatCard.tsx 2>/dev/null || \
ls -la src/components/ | grep -i widget
```

**Check for:**
- Card wrapper component (className, styling)
- Data fetching pattern (useEffect, custom hook)
- Loading state indicator
- Error handling
- Data display format

#### Step 1.3: Read Dashboard JSX Structure
```bash
# Get full dashboard structure
cat src/pages/Dashboard.tsx | grep -A 100 "return"
```

**Look for:**
- Container/grid layout (Grid, CSS Grid, Flexbox)
- How cards are arranged (col span, responsive)
- How spacing is applied (padding, gap)
- How data is passed to cards

#### Step 1.4: Check Responsive Breakpoints
```bash
# Find CSS or Tailwind classes used
grep -o "grid-cols-\|col-span-\|md:\|lg:" src/pages/Dashboard.tsx | sort | uniq -c

# Find existing responsive patterns
grep "responsive\|mobile\|tablet" src/pages/Dashboard.tsx
```

#### Step 1.5: Identify Data Fetching Pattern
```bash
# Find how cards get data
grep -B 5 -A 10 "useEffect\|useQuery\|useFetch" src/pages/Dashboard.tsx | head -30
```

### Phase 2: Impact - Map Changes

#### Step 2.1: Analyze Layout Impact
```bash
# Count current columns
grep -c "col-span" src/pages/Dashboard.tsx

# Check if layout has fixed column count
grep -o "grid-cols-[0-9]" src/pages/Dashboard.tsx
```

**Key questions:**
- How many columns now? (2, 3, 4, 12?)
- Is grid responsive? (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
- Will new widget fit without reflow?

#### Step 2.2: Check Data Dependencies
```bash
# Find if widget data depends on other widgets
grep -r "const.*data.*=" src/pages/Dashboard.tsx | head -10

# Check if shared data fetching
grep "useContext\|useSelector" src/pages/Dashboard.tsx
```

#### Step 2.3: Check Loading States
```bash
# Find how loading is handled
grep "loading\|isLoading\|isFetching" src/pages/Dashboard.tsx
```

### Phase 3: Implement - Add Widget Following Patterns

#### Step 3.1: Create Widget Component
Find a similar widget:
```bash
cat src/components/RecentActivityCard.tsx 2>/dev/null || \
cat src/components/StatCard.tsx 2>/dev/null
```

**Pattern to follow:**
```tsx
import React, { useState, useEffect } from 'react';

interface StatsWidgetProps {
  title: string;
}

export function StatsWidget({ title }: StatsWidgetProps) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/stats');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="card loading-skeleton">Loading...</div>;
  if (error) return <div className="card error">{error}</div>;

  return (
    <div className="card">
      <h3 className="card-title">{title}</h3>
      <div className="card-content">
        {/* Display data */}
      </div>
    </div>
  );
}
```

**Match these exactly:**
- Loading state skeleton
- Error message styling
- Card className structure
- useEffect pattern
- Data fetching try/catch pattern

#### Step 3.2: Add Widget to Dashboard
Find dashboard file:
```bash
grep -n "import.*Card\|from.*components" src/pages/Dashboard.tsx | head -5
```

Add import:
```tsx
import { StatsWidget } from '@/components/StatsWidget';
```

Find where cards are rendered:
```bash
grep -n "return\|<div.*grid\|<.*Card" src/pages/Dashboard.tsx
```

Add widget to grid:
```tsx
// BEFORE
<div className="dashboard-grid">
  <RecentActivityCard />
  <UserStatsCard />
</div>

// AFTER - maintain same grid structure
<div className="dashboard-grid">
  <RecentActivityCard />
  <UserStatsCard />
  <StatsWidget title="New Stats" />  {/* NEW WIDGET */}
</div>
```

#### Step 3.3: Ensure Responsive Layout
Check existing responsive classes:
```bash
grep -o "md:\|lg:\|grid-cols" src/pages/Dashboard.tsx | head -5
```

**Pattern to preserve:**
```tsx
// BEFORE - 3 column on desktop, 1 on mobile
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card1 />
  <Card2 />
  <Card3 />
</div>

// AFTER - add new card, layout automatically reflows
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card1 />
  <Card2 />
  <Card3 />
  <Card4 />  {/* NEW - layout handles responsiveness */}
</div>
```

#### Step 3.4: Add API Endpoint (If Needed)
```bash
# Find existing endpoint pattern
find src/api -name "*.ts" | head -1 | xargs cat | head -30
```

**Pattern to follow:**
```typescript
// BEFORE
export const getStats = async () => {
  const response = await fetch('/api/stats');
  return response.json();
};

// AFTER - add new endpoint
export const getStats = async () => {
  const response = await fetch('/api/stats');
  return response.json();
};

export const getDetailedStats = async () => {  // NEW
  const response = await fetch('/api/stats/detailed');
  return response.json();
};
```

### Phase 4: Verify - Test Dashboard Integrity

#### Verification Checklist
- [ ] Dashboard loads without errors
- [ ] All existing widgets still display
- [ ] New widget displays in correct position
- [ ] New widget loads data correctly
- [ ] New widget shows loading state
- [ ] New widget handles errors gracefully
- [ ] Dashboard responsive on mobile (1 column)
- [ ] Dashboard responsive on tablet (2 columns)
- [ ] Dashboard responsive on desktop (3+ columns)
- [ ] No layout shift or overflow
- [ ] All existing widgets layout unchanged
- [ ] Spacing/gaps consistent with other widgets

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Navigate to dashboard
# 2. Verify all existing widgets render
# 3. Verify new widget renders in correct position
# 4. Verify new widget has correct title/content
# 5. Check network tab - verify API call for new widget
# 6. Resize browser to mobile (375px width)
#    - Verify single column layout
#    - Verify new widget flows correctly
# 7. Resize to tablet (768px)
#    - Verify 2 column layout
# 8. Resize to desktop (1200px)
#    - Verify 3+ column layout
# 9. Slow down network (DevTools)
#    - Verify loading skeleton appears
#    - Verify data loads correctly
# 10. Block API call (DevTools)
#     - Verify error message appears
#     - Verify other widgets still work
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Check imports are correct
grep -r "StatsWidget" src/ --include="*.tsx" | wc -l
# Should be: 2 (import in Dashboard, export in component)

# Check className consistency
grep "className=\"card" src/components/StatsWidget.tsx
```

#### Step 4.3: Common Issues and Fixes

**Problem: Widget displays but no data appears**
```
Cause: API endpoint not returning data or fetch fails
Fix: Check browser console for network errors
Verify: curl http://localhost:3000/api/stats shows data
```

**Problem: Dashboard layout breaks (overflow or extra rows)**
```
Cause: New widget doesn't fit in grid or has wrong className
Fix: Verify className="card" matches existing cards
Verify: Check grid-cols-* matches existing cards
```

**Problem: Widget doesn't respond to responsive changes**
```
Cause: Uses fixed width or hardcoded size
Fix: Remove hardcoded width, use grid layout classes
Verify: Resize browser, widget shrinks proportionally
```

**Problem: Loading state not showing**
```
Cause: Data fetches too fast or loading state not used
Fix: Add artificial delay in dev for testing: await new Promise(r => setTimeout(r, 1000))
Verify: Slow network in DevTools shows skeleton
```

**Problem: Old widgets affected by new widget**
```
Cause: Accidentally modified shared CSS or grid structure
Fix: git diff to see what changed in Dashboard.tsx
Verify: Revert to original grid structure
```

---

## SCENARIO 5: Add File Upload to an Existing Form

### When You Receive This Request
"Add file upload to the [profile/document/image] form"

### Phase 1: Recon - Check Existing Upload Patterns

#### Step 1.1: Search for Existing File Uploads
```bash
# Find all file uploads in app
grep -r "type=\"file\"\|FileUpload\|uploadFile" src/ --include="*.tsx" --include="*.ts" | head -10

# Find upload components
find src/components -name "*Upload*" -o -name "*File*" | head -5
```

#### Step 1.2: Check Storage Service
```bash
# Find storage configuration
find src -name "*storage*" -o -name "*firebase*" -o -name "*supabase*" | grep -E "\.ts$" | head -5

# Read storage config
cat src/config/storage.ts 2>/dev/null || \
cat src/lib/storage.ts 2>/dev/null || \
grep -r "Storage\|uploadFile\|upload" src/config --include="*.ts" | head -10
```

#### Step 1.3: Read Existing Form to Understand Structure
```bash
cat src/components/ProfileForm.tsx | head -80
```

**Look for:**
- Form framework (React Hook Form, Formik, etc)
- TypeScript types
- How existing fields work
- Error handling
- Form submission

#### Step 1.4: Check If Upload Exists Elsewhere
```bash
# Find working upload example
grep -l "FileUpload\|handleFileUpload" src/components/*.tsx | head -1 | xargs cat
```

**If exists, copy this pattern exactly.**

### Phase 2: Impact - Map File Upload Changes

#### Step 2.1: Identify Form Type Definition
```bash
# Find type for form
grep -B 5 -A 10 "interface.*FormData\|type.*Form" src/components/ProfileForm.tsx | head -20
```

**Check if file field already in type:**
```typescript
interface ProfileFormData {
  name: string;
  email: string;
  // Check if profileImage or similar exists
}
```

#### Step 2.2: Check Database Schema
```bash
# Check if column for file exists
grep -A 5 "CREATE TABLE.*profile\|model Profile" src/db/schema.sql 2>/dev/null || \
grep -A 5 "model Profile" prisma/schema.prisma 2>/dev/null

# Check current user/profile schema
grep -i "image\|file\|upload" src/db/schema.sql 2>/dev/null
```

#### Step 2.3: Check API Handling
```bash
# Find form submission handler
grep -A 20 "handleSubmit\|onSubmit" src/components/ProfileForm.tsx | grep -A 20 "updateProfile\|submitForm"

# Find API endpoint
find src/api -name "*.ts" | xargs grep -l "profile\|update" | head -1 | xargs cat
```

### Phase 3: Implement - Add File Upload Following Patterns

#### Step 3.1: Find or Create Upload Component
**If upload exists elsewhere:**
```bash
# Copy exact upload pattern
cp src/components/FileUpload.tsx .
cat src/components/FileUpload.tsx
```

**If no upload exists, create minimal pattern:**
```tsx
import React, { useState } from 'react';

interface FileUploadProps {
  onFileSelected: (file: File) => void;
  accept?: string;
  maxSize?: number;
}

export function FileUpload({ onFileSelected, accept = 'image/*', maxSize = 5 * 1024 * 1024 }: FileUploadProps) {
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > maxSize) {
      setError(`File must be less than ${maxSize / 1024 / 1024}MB`);
      return;
    }

    setError(null);
    onFileSelected(file);
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        accept={accept}
        onChange={handleChange}
        className="file-input"
      />
      {error && <span className="error-message">{error}</span>}
    </div>
  );
}
```

#### Step 3.2: Extend Form Type with File Field
```bash
# Find type definition
grep -n "interface.*FormData" src/components/ProfileForm.tsx
```

**Update type:**
```typescript
// BEFORE
interface ProfileFormData {
  name: string;
  email: string;
}

// AFTER
interface ProfileFormData {
  name: string;
  email: string;
  profileImage?: File;  // NEW - optional file
}
```

#### Step 3.3: Add File Upload Field to Form
```bash
# Read current form JSX
grep -A 50 "return" src/components/ProfileForm.tsx | head -50
```

**Add field following existing pattern:**
```tsx
// BEFORE (existing fields)
<label htmlFor="email">Email</label>
<input
  type="email"
  id="email"
  name="email"
  className="form-input"
  {...register('email')}
/>

// AFTER (add file upload)
<label htmlFor="email">Email</label>
<input
  type="email"
  id="email"
  name="email"
  className="form-input"
  {...register('email')}
/>

{/* NEW - File Upload Field */}
<label htmlFor="profileImage">Profile Photo</label>
<FileUpload
  onFileSelected={(file) => {
    // Update form with file
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    const fileInput = document.getElementById('profileImage') as HTMLInputElement;
    fileInput.files = dataTransfer.files;
  }}
  accept="image/*"
  maxSize={5 * 1024 * 1024}
/>
{errors.profileImage && <span className="error-message">{errors.profileImage.message}</span>}
```

#### Step 3.4: Handle File Upload on Form Submit
```bash
# Find submit handler
grep -n "handleSubmit\|const onSubmit" src/components/ProfileForm.tsx
```

**Update submission to handle file:**
```typescript
// BEFORE
const handleSubmit = async (data: ProfileFormData) => {
  await updateProfile({
    name: data.name,
    email: data.email
  });
};

// AFTER
const handleSubmit = async (data: ProfileFormData) => {
  let profileImageUrl = null;

  // Upload file if provided
  if (data.profileImage) {
    profileImageUrl = await uploadFile(data.profileImage);
  }

  await updateProfile({
    name: data.name,
    email: data.email,
    profileImage: profileImageUrl  // NEW
  });
};
```

#### Step 3.5: Create/Update Upload Handler
```bash
# Check for upload service
find src/lib -name "*upload*" -o -name "*storage*" | head -1
```

**Create upload function if doesn't exist:**
```typescript
// src/lib/upload.ts

export const uploadFile = async (file: File): Promise<string> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  const { url } = await response.json();
  return url;
};
```

#### Step 3.6: Update Display Component
Find where profile is displayed:
```bash
find src/pages -name "*Profile*" | head -1 | xargs cat | grep -A 20 "profileImage\|image" || echo "No image field found"
```

**Add image display:**
```tsx
// BEFORE
<div className="profile-info">
  <p><strong>Name:</strong> {user.name}</p>
  <p><strong>Email:</strong> {user.email}</p>
</div>

// AFTER
<div className="profile-info">
  {user.profileImage && (  {/* NEW */}
    <img
      src={user.profileImage}
      alt={user.name}
      className="profile-avatar"
    />
  )}
  <p><strong>Name:</strong> {user.name}</p>
  <p><strong>Email:</strong> {user.email}</p>
</div>
```

#### Step 3.7: Update Database Schema
**If using Prisma:**
```prisma
model Profile {
  id String @id
  name String
  email String
  profileImage String?  // NEW - optional image URL
  createdAt DateTime @default(now())
}
```

**If using SQL:**
```sql
ALTER TABLE profiles ADD COLUMN profile_image VARCHAR(500);
```

### Phase 4: Verify - Test Form with and Without File

#### Verification Checklist
- [ ] Form displays all existing fields
- [ ] Form displays file upload input
- [ ] File validation shows error for oversized files
- [ ] File validation shows error for wrong file type
- [ ] Form submits successfully with file
- [ ] Form submits successfully without file (if optional)
- [ ] Uploaded file appears in database/storage
- [ ] Profile displays uploaded image correctly
- [ ] Existing fields submit correctly with file upload
- [ ] Image URL stored and retrievable
- [ ] No console errors on form load
- [ ] No console errors on file upload

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Load profile form
# 2. Verify all existing fields render
# 3. Verify file upload input renders
# 4. Try to upload file larger than limit
#    - Verify error message appears
# 5. Try to upload wrong file type
#    - Verify error message appears (if validation exists)
# 6. Upload valid image file (< 5MB, .jpg/.png)
#    - Verify no error
#    - Verify can clear selection
# 7. Submit form with file
#    - Check network tab for upload request
#    - Verify success message
# 8. Navigate to profile view
#    - Verify image displays
# 9. Edit profile again
#    - Verify existing image shown
#    - Verify can upload new image
# 10. Submit form without changing image
#     - Verify form submits without re-upload
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Verify upload handler exists and is used
grep -r "uploadFile" src/ --include="*.tsx" --include="*.ts" | wc -l

# Verify form handles file field
grep "profileImage\|FileUpload" src/components/ProfileForm.tsx
```

#### Step 4.3: Common Issues and Fixes

**Problem: File doesn't upload / "Upload failed" error**
```
Cause: API endpoint not created or returns wrong format
Fix: Create /api/upload endpoint that returns { url: string }
Verify: curl -F "file=@test.jpg" http://localhost:3000/api/upload
```

**Problem: Form validation fails on submit**
```
Cause: File field validation too strict
Fix: Make file field optional: profileImage?: File
Verify: Submit form without file should succeed
```

**Problem: Old form fields don't save when uploading file**
```
Cause: Form submission replaced with just file upload
Fix: Upload file first, then submit form with URL
Verify: Check both form fields and image in database
```

**Problem: Image doesn't appear after upload**
```
Cause: Image URL not stored or not in correct format
Fix: Verify upload returns full URL, not just path
Verify: console.log(uploadedUrl) shows valid URL
```

---

## SCENARIO 6: Add Search/Filter to a List

### When You Receive This Request
"Add search/filter functionality to the [users/products/items] list"

### Phase 1: Recon - Understand List Structure

#### Step 1.1: Find the List Component
```bash
# Find list components
find src/pages -name "*List*" -o -name "*Items*" -o -name "*Table*" | head -5

# Find the specific list
grep -r "UserList\|ProductList" src/pages --include="*.tsx" | head -1
```

#### Step 1.2: Read List Component Structure
```bash
# Read full list
cat src/pages/UserList.tsx | head -100
```

**Look for:**
- How data is fetched
- How list is rendered (table, grid, cards)
- How pagination works (if exists)
- Current state management
- TypeScript types

#### Step 1.3: Check Data Source
```bash
# Find where data comes from
grep -A 5 "useState\|useEffect\|useQuery" src/pages/UserList.tsx | head -20
```

**Is data:**
- Fetched from API?
- From local state?
- From Redux/Context?

#### Step 1.4: Check for Existing Search/Filter
```bash
# Check if search exists elsewhere
grep -r "search\|filter\|query" src/components --include="*.tsx" -l | head -3

# Check the pattern used
cat src/components/SearchBar.tsx 2>/dev/null || \
grep -B 3 -A 10 "search" src/pages/UserList.tsx | head -20
```

#### Step 1.5: Understand List Rendering
```bash
# Find how items are rendered
grep -A 20 "\.map\|\.filter" src/pages/UserList.tsx | head -30
```

### Phase 2: Impact - Map Search Implementation

#### Step 2.1: Check Data Fetching Method
```bash
# Is data fetched with query params already?
grep "fetch.*\?.*=" src/pages/UserList.tsx

# Or is it filtered in memory?
grep "\.filter\(.*=>.*\.includes" src/pages/UserList.tsx
```

**Decision:**
- **Server-side search:** Pass search to API, fetch filtered results
- **Client-side search:** Fetch all, filter in memory

#### Step 2.2: Check List Constraints
```bash
# Check if pagination exists
grep -i "page\|limit\|take" src/pages/UserList.tsx

# Check if virtualization used
grep "virtual\|windowing" src/pages/UserList.tsx

# Check item count
grep "\.length\|count" src/pages/UserList.tsx
```

**If thousands of items:** Use server-side search
**If tens of items:** Client-side search is fine

#### Step 2.3: Check State Management
```bash
# Is there Redux/Zustand/Context?
grep "useSelector\|useDispatch\|useContext" src/pages/UserList.tsx

# Check for global search state
grep -r "searchQuery\|filterState" src/store --include="*.ts" 2>/dev/null || echo "No store found"
```

### Phase 3: Implement - Add Search Following Patterns

#### Step 3.1: Create Search Input Component (If Needed)
Check for existing:
```bash
cat src/components/SearchInput.tsx 2>/dev/null || echo "Create new"
```

**Pattern to follow:**
```tsx
import React from 'react';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchInput({ value, onChange, placeholder = 'Search...' }: SearchInputProps) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="search-input"
    />
  );
}
```

#### Step 3.2: Add Search State to List Component
```bash
# Read list component to find state management
grep -n "useState\|const.*=" src/pages/UserList.tsx | head -20
```

**Add search state:**
```typescript
// BEFORE
export default function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  // AFTER
  export default function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');  // NEW

  useEffect(() => {
    fetchUsers(searchQuery);  // NEW - pass search query
  }, [searchQuery]);  // NEW - refetch on search change
```

#### Step 3.3: Update Data Fetching for Search
**Client-side approach (for small lists):**
```typescript
// BEFORE
const filteredUsers = users;

// AFTER
const filteredUsers = users.filter(user =>
  user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
  user.email.toLowerCase().includes(searchQuery.toLowerCase())
);
```

**Server-side approach (for large lists):**
```typescript
// BEFORE
const fetchUsers = async () => {
  const response = await fetch('/api/users');
  setUsers(await response.json());
};

// AFTER
const fetchUsers = async (search: string) => {
  const params = new URLSearchParams();
  if (search) {
    params.append('search', search);
  }
  const response = await fetch(`/api/users?${params}`);
  setUsers(await response.json());
};
```

#### Step 3.4: Add Search Input to UI
Find where list renders:
```bash
grep -n "return\|<div\|<table" src/pages/UserList.tsx | head -10
```

**Add search input before list:**
```tsx
// BEFORE
<div className="page-container">
  <h1>Users</h1>
  <table>
    {/* User rows */}
  </table>
</div>

// AFTER
<div className="page-container">
  <h1>Users</h1>
  <SearchInput  {/* NEW */}
    value={searchQuery}
    onChange={setSearchQuery}
    placeholder="Search by name or email"
  />
  <table>
    {/* User rows - now filtered */}
  </table>
</div>
```

#### Step 3.5: Update List Rendering with Filtered Data
```bash
# Find current render logic
grep -n "users\.map\|users\." src/pages/UserList.tsx | head -5
```

**Update to use filtered data:**
```tsx
// BEFORE
{users.map(user => (
  <tr key={user.id}>
    <td>{user.name}</td>
    <td>{user.email}</td>
  </tr>
))}

// AFTER
{filteredUsers.map(user => (  // Use filtered, not original
  <tr key={user.id}>
    <td>{user.name}</td>
    <td>{user.email}</td>
  </tr>
))}

{/* Show empty state if search returned nothing */}
{filteredUsers.length === 0 && (
  <tr><td colSpan={2} className="text-center">No results found</td></tr>
)}
```

#### Step 3.6: Add Loading State for Search
```typescript
// BEFORE - no debounce
const [searchQuery, setSearchQuery] = useState('');

useEffect(() => {
  fetchUsers(searchQuery);
}, [searchQuery]);

// AFTER - with debounce to prevent excessive API calls
const [searchQuery, setSearchQuery] = useState('');
const [isSearching, setIsSearching] = useState(false);

useEffect(() => {
  const timer = setTimeout(() => {
    setIsSearching(true);
    fetchUsers(searchQuery).finally(() => setIsSearching(false));
  }, 300); // Wait 300ms after user stops typing

  return () => clearTimeout(timer);
}, [searchQuery]);
```

#### Step 3.7: Preserve Pagination with Search (If Applicable)
```bash
# Check if pagination exists
grep -i "page\|pagination" src/pages/UserList.tsx | head -5
```

**If pagination exists, reset page on search:**
```typescript
// BEFORE
const [searchQuery, setSearchQuery] = useState('');

// AFTER
const [searchQuery, setSearchQuery] = useState('');
const [currentPage, setCurrentPage] = useState(1);

const handleSearch = (query: string) => {
  setSearchQuery(query);
  setCurrentPage(1);  // Reset to page 1 on search
};
```

### Phase 4: Verify - Test Search with Various Queries

#### Verification Checklist
- [ ] Search input appears above list
- [ ] List displays all items when search is empty
- [ ] List filters correctly when search matches name
- [ ] List filters correctly when search matches email
- [ ] Search is case-insensitive
- [ ] List shows "No results" when no matches
- [ ] Original list items still all accessible
- [ ] Search doesn't break pagination (if exists)
- [ ] Search doesn't break sorting (if exists)
- [ ] Rapid typing doesn't cause excessive API calls (if server-side)
- [ ] No console errors
- [ ] No TypeScript errors

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Navigate to user list
# 2. Verify all items display without search
# 3. Type in search box - "John"
#    - Verify list filters to matching names
# 4. Type in search box - "john@example.com"
#    - Verify email search works
# 5. Type in search box - "JOHN" (uppercase)
#    - Verify case-insensitive search
# 6. Clear search box
#    - Verify all items show again
# 7. Type search that matches nothing - "xyz123"
#    - Verify "No results" message shows
# 8. Search for space " "
#    - Verify doesn't break
# 9. Test rapid typing "j", "jo", "joh", "john"
#    - Verify list updates smoothly
#    - Check Network tab - verify debounce works (not 4 requests)
# 10. If pagination exists - search that returns > 1 page
#     - Verify pagination still works
#     - Verify page resets on new search
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Verify search component is used
grep -r "SearchInput\|searchQuery" src/ --include="*.tsx" | wc -l

# Check filtering logic
grep -r "\.filter.*includes\|toLowerCase" src/pages/UserList.tsx
```

#### Step 4.3: Common Issues and Fixes

**Problem: Search returns no results even when items match**
```
Cause: Case sensitivity or field name mismatch
Fix: Add .toLowerCase() to both query and field values
Verify: grep "\.toLowerCase()" src/pages/UserList.tsx
```

**Problem: Excessive API calls during typing**
```
Cause: No debounce on search input
Fix: Add setTimeout debounce wrapper
Verify: Check Network tab, max 1 request per search
```

**Problem: Pagination breaks with search**
```
Cause: Page number not reset when search changes
Fix: Reset currentPage to 1 when searchQuery changes
Verify: Search for something, navigate to page 2, search again - should go to page 1
```

**Problem: Original list items no longer visible**
```
Cause: Rendering filtered list instead of original
Fix: Keep both users (original) and filteredUsers (filtered)
Verify: grep "filteredUsers\|users\.map" shows using correct variable
```

---

## SCENARIO 7: Add Status Tracking to Existing Items

### When You Receive This Request
"Add status tracking to [items/orders/tasks] - show [draft/published/archived] states"

### Phase 1: Recon - Understand Status Patterns in App

#### Step 1.1: Find Existing Status Patterns
```bash
# Search for existing status implementations
grep -r "status\|state\|STATE" src/ --include="*.ts" --include="*.tsx" | grep -i "const\|enum\|type" | head -20

# Find status badges/displays
grep -r "badge\|status.*color\|status.*class" src/components --include="*.tsx" -l | head -5
```

#### Step 1.2: Check Item Type Definition
```bash
# Find item type
grep -B 3 -A 10 "interface Item\|type.*Item" src/types/index.ts | head -20

# Check if status already exists
grep "status" src/types/index.ts
```

#### Step 1.3: Find Status Display Pattern
```bash
# Look for status badge component
cat src/components/StatusBadge.tsx 2>/dev/null || \
cat src/components/Badge.tsx 2>/dev/null || \
grep -r "className.*badge\|className.*status" src/components/*.tsx | head -3
```

#### Step 1.4: Check Existing Workflow Patterns
```bash
# Find where item state changes
grep -r "update.*status\|change.*state\|publish\|archive" src/ --include="*.tsx" | head -10

# Find how transitions are handled
grep -B 5 -A 5 "canPublish\|canArchive\|canDraft" src/ --include="*.tsx" | head -20
```

### Phase 2: Impact - Map Status Changes

#### Step 2.1: Identify Status Values
```bash
# Check what statuses exist in app
grep -r "draft\|published\|archived\|pending\|active" src/ --include="*.ts" | head -10
```

**Common patterns:**
```typescript
enum ItemStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

// or

type ItemStatus = 'draft' | 'published' | 'archived';
```

#### Step 2.2: Find All Item Display Locations
```bash
# Find list component
grep -r "items\.map\|<ItemRow\|<ItemCard" src/pages --include="*.tsx" | head -5

# Find detail component
find src/pages -name "*ItemDetail*" -o -name "*ItemView*"

# Find item component
find src/components -name "*Item*" | head -5
```

#### Step 2.3: Check Update Permissions
```bash
# Find where items are updated
grep -r "updateItem\|updateStatus\|patchItem" src/api --include="*.ts" | head -5

# Check if role checks exist
grep -B 5 "updateItem" src/pages/*.tsx | grep -i "role\|admin"
```

### Phase 3: Implement - Add Status Field

#### Step 3.1: Extend Item Type with Status
```bash
# Find item type
grep -n "interface Item\|type Item" src/types/index.ts
```

**Update type:**
```typescript
// BEFORE
interface Item {
  id: string;
  title: string;
  content: string;
  createdAt: Date;
}

// AFTER
interface Item {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'published' | 'archived';  // NEW
  createdAt: Date;
}

// OR use enum
enum ItemStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

interface Item {
  id: string;
  title: string;
  content: string;
  status: ItemStatus;  // NEW
  createdAt: Date;
}
```

#### Step 3.2: Create Status Badge Component
```bash
# Check if StatusBadge exists
cat src/components/StatusBadge.tsx 2>/dev/null || echo "Create new"
```

**Pattern to follow:**
```tsx
import React from 'react';

interface StatusBadgeProps {
  status: 'draft' | 'published' | 'archived';
}

const statusColors = {
  draft: 'bg-gray-100 text-gray-800',
  published: 'bg-green-100 text-green-800',
  archived: 'bg-gray-200 text-gray-600',
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`badge ${statusColors[status]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
```

#### Step 3.3: Add Status to List View
Find item list:
```bash
grep -n "items\.map\|<ItemRow" src/pages/ItemList.tsx | head -3
```

**Add status badge:**
```tsx
// BEFORE (table row)
<tr key={item.id}>
  <td>{item.title}</td>
  <td>{item.createdAt}</td>
</tr>

// AFTER
<tr key={item.id}>
  <td>{item.title}</td>
  <td><StatusBadge status={item.status} /></td>  {/* NEW */}
  <td>{item.createdAt}</td>
</tr>
```

#### Step 3.4: Add Status Filter to List
```bash
# Check if filters exist
grep -r "filter\|Filter" src/pages/ItemList.tsx | head -5
```

**Add status filter following existing pattern:**
```tsx
// BEFORE (if filters exist)
const [filterRole, setFilterRole] = useState('all');

// AFTER
const [filterRole, setFilterRole] = useState('all');
const [filterStatus, setFilterStatus] = useState('all');  // NEW

// Filter logic
const filtered = items.filter(item => {
  if (filterStatus !== 'all' && item.status !== filterStatus) return false;
  return true;
});

// Filter UI
<select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
  <option value="all">All Statuses</option>
  <option value="draft">Draft</option>
  <option value="published">Published</option>
  <option value="archived">Archived</option>
</select>
```

#### Step 3.5: Add Status Change Actions
Find item actions/buttons:
```bash
grep -B 3 -A 3 "delete\|edit\|action" src/components/ItemActions.tsx 2>/dev/null || \
grep -B 5 "className.*button" src/pages/ItemDetail.tsx | head -10
```

**Add status transition buttons:**
```tsx
// BEFORE
<button onClick={() => deleteItem(item.id)}>Delete</button>
<button onClick={() => editItem(item.id)}>Edit</button>

// AFTER
<button onClick={() => deleteItem(item.id)}>Delete</button>
<button onClick={() => editItem(item.id)}>Edit</button>

{/* NEW - Status transition buttons */}
{item.status === 'draft' && (
  <button onClick={() => updateStatus(item.id, 'published')}>
    Publish
  </button>
)}

{item.status === 'published' && (
  <>
    <button onClick={() => updateStatus(item.id, 'draft')}>
      Unpublish
    </button>
    <button onClick={() => updateStatus(item.id, 'archived')}>
      Archive
    </button>
  </>
)}

{item.status === 'archived' && (
  <button onClick={() => updateStatus(item.id, 'draft')}>
    Restore
  </button>
)}
```

#### Step 3.6: Add Status Update Handler
```typescript
// BEFORE - no status update
const deleteItem = async (id: string) => {
  await fetch(`/api/items/${id}`, { method: 'DELETE' });
};

// AFTER - add status update
const updateStatus = async (id: string, newStatus: ItemStatus) => {
  const response = await fetch(`/api/items/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  });

  // Refresh item
  const updated = await response.json();
  setItem(updated);
};
```

#### Step 3.7: Update API Endpoint
```bash
# Check existing endpoint
grep -A 10 "PATCH.*items\|PUT.*items" src/api/items.ts
```

**Update to handle status:**
```typescript
// Backend handler pseudocode
export async function patchItem(req, res) {
  const { id } = req.params;
  const { status } = req.body;

  // Validate status transition
  if (status && !['draft', 'published', 'archived'].includes(status)) {
    return res.status(400).json({ error: 'Invalid status' });
  }

  // Update in database
  const item = await db.items.update(id, { status });
  res.json(item);
}
```

#### Step 3.8: Update Database Schema
**If using Prisma:**
```prisma
model Item {
  id String @id
  title String
  content String
  status String @default("draft")  // or use enum
  createdAt DateTime @default(now())
}

// Or with enum:
enum ItemStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

model Item {
  id String @id
  title String
  content String
  status ItemStatus @default(DRAFT)
  createdAt DateTime @default(now())
}
```

**Run migration:**
```bash
npx prisma migrate dev --name add_status_to_items
```

### Phase 4: Verify - Test Status Transitions

#### Verification Checklist
- [ ] Status field added to all items
- [ ] Status badge displays for all items
- [ ] Status badge colors correct for each status
- [ ] Status filter works correctly
- [ ] Existing items show default status (draft or published)
- [ ] Status can be changed from draft to published
- [ ] Status can be changed from published to archived
- [ ] Status can be changed back to draft
- [ ] Invalid status transitions prevented (if applicable)
- [ ] Status persists after page reload
- [ ] List view filters work with status
- [ ] Detail view shows status and change options
- [ ] Status change reflects immediately in UI
- [ ] No console errors

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Navigate to items list
# 2. Verify all items show status badge
# 3. Verify status colors match expected (draft=gray, published=green, etc)
# 4. Click status filter dropdown
#    - Select "Draft" only
#    - Verify only draft items show
# 5. Select "Published" filter
#    - Verify only published items show
# 6. Click item details
# 7. Verify status shown
# 8. Click "Publish" button (if draft)
#    - Verify status changes to published
#    - Verify badge color updates immediately
# 9. Click "Archive" button (if published)
#    - Verify status changes to archived
# 10. Go back to list
#     - Verify status persisted
# 11. Use filter to find archived items
#     - Verify archive status works
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Verify status is used everywhere
grep -r "item\.status\|ItemStatus" src/ --include="*.tsx" --include="*.ts" | wc -l

# Verify status badge component
grep -r "StatusBadge" src/ --include="*.tsx" | head -5
```

#### Step 4.3: Common Issues and Fixes

**Problem: Status doesn't persist after reload**
```
Cause: Not saved to database or API returns old data
Fix: Verify PATCH request succeeds, check database
Verify: SELECT status FROM items LIMIT 1; shows new value
```

**Problem: Status badge doesn't update immediately**
```
Cause: UI not refreshed after status change
Fix: Update local item state after API call
Verify: setItem(updated) or similar called after status change
```

**Problem: Filter shows wrong items**
```
Cause: Filter logic includes/excludes wrong status values
Fix: Check filter condition: item.status === filterStatus
Verify: Manually count items in each status category
```

**Problem: Some items have no status**
```
Cause: Old items in database don't have status column
Fix: Run database migration or set default value
Verify: UPDATE items SET status = 'draft' WHERE status IS NULL;
```

---

## SCENARIO 8: Add Email/Notification Feature

### When You Receive This Request
"Send [email/notification] when [event happens]"

### Phase 1: Recon - Check Existing Notification System

#### Step 1.1: Find Notification Service
```bash
# Find existing notification patterns
grep -r "toast\|notification\|alert\|message" src/ --include="*.tsx" | grep -i "context\|provider\|service" | head -10

# Find notification components
find src/components -name "*Toast*" -o -name "*Alert*" -o -name "*Notification*" | head -5
```

#### Step 1.2: Find Notification Context/Provider
```bash
# Check for global notification context
grep -r "NotificationContext\|ToastContext\|useToast\|useNotification" src/ --include="*.tsx" --include="*.ts" | head -5

# Read notification provider
cat src/contexts/NotificationContext.tsx 2>/dev/null || \
cat src/providers/ToastProvider.tsx 2>/dev/null
```

#### Step 1.3: Check Email Service Configuration
```bash
# Find email service
find src -name "*email*" -o -name "*mail*" | grep -E "\.ts$" | head -5

# Check for sendgrid, nodemailer, etc
grep -r "sendgrid\|nodemailer\|email" src/config --include="*.ts" | head -5

# Check environment variables
grep -i "email\|smtp\|sendgrid" .env.example 2>/dev/null || echo "No .env.example found"
```

#### Step 1.4: Find Existing Notifications
```bash
# Find where notifications are triggered
grep -r "notify\|toast\|alert" src/pages --include="*.tsx" | head -10

# Check message patterns
grep -r "useNotification\|notificationService" src/pages --include="*.tsx" | head -5
```

### Phase 2: Impact - Map Notification Implementation

#### Step 2.1: Identify the Event Trigger
```bash
# Find where the triggering event happens
# Example: User registration, item published, etc.

grep -B 5 -A 5 "createUser\|publishItem\|onSubmit" src/pages/*.tsx | grep -A 10 "await\|fetch" | head -30
```

#### Step 2.2: Check Notification UI Style
```bash
# Find toast/notification UI pattern
cat src/components/Toast.tsx 2>/dev/null || \
grep -A 15 "className.*toast\|className.*notification" src/components/*.tsx | head -30
```

#### Step 2.3: Identify User Email Field
```bash
# Check if user has email
grep -A 5 "interface User\|type User" src/types/index.ts | grep email
```

### Phase 3: Implement - Add Notification

#### Step 3.1: Use Existing Notification Service
Find notification hook:
```bash
grep -r "useNotification\|useToast" src/ --include="*.tsx" | head -1
```

**Pattern to follow:**
```tsx
import { useNotification } from '@/contexts/NotificationContext';

export function MyComponent() {
  const { notify } = useNotification();

  const handleAction = async () => {
    try {
      await doSomething();
      notify({
        type: 'success',
        message: 'Action completed successfully!'
      });
    } catch (error) {
      notify({
        type: 'error',
        message: 'Something went wrong'
      });
    }
  };
}
```

#### Step 3.2: Create Notification Service (If Doesn't Exist)
```typescript
// src/services/notificationService.ts

export interface Notification {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number; // ms
}

export const notificationService = {
  show(notification: Notification) {
    // Dispatch to toast/notification system
    window.dispatchEvent(
      new CustomEvent('notification', { detail: notification })
    );
  },

  success(message: string) {
    this.show({ type: 'success', message });
  },

  error(message: string) {
    this.show({ type: 'error', message });
  }
};
```

#### Step 3.3: Add Notification on Event
Find the event handler:
```bash
grep -n "const handleSubmit\|const onCreate\|const onPublish" src/pages/MyPage.tsx
```

**Add notification:**
```typescript
// BEFORE
const handlePublish = async (itemId: string) => {
  await publishItem(itemId);
};

// AFTER
const handlePublish = async (itemId: string) => {
  try {
    await publishItem(itemId);
    notify({  // NEW
      type: 'success',
      message: 'Item published successfully!'
    });
  } catch (error) {
    notify({  // NEW
      type: 'error',
      message: 'Failed to publish item'
    });
  }
};
```

#### Step 3.4: Create Email Service (If Needed)
```typescript
// src/services/emailService.ts

export const emailService = {
  async sendWelcomeEmail(userEmail: string, userName: string) {
    const response = await fetch('/api/emails/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        to: userEmail,
        template: 'welcome',
        data: { name: userName }
      })
    });

    if (!response.ok) throw new Error('Email send failed');
    return response.json();
  },

  async sendNotificationEmail(userEmail: string, title: string) {
    return fetch('/api/emails/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        to: userEmail,
        template: 'notification',
        data: { title }
      })
    });
  }
};
```

#### Step 3.5: Create API Endpoint for Email
```typescript
// src/api/emails.ts or backend equivalent

export async function sendEmail(req, res) {
  const { to, template, data } = req.body;

  try {
    // Use email service (SendGrid, Nodemailer, etc)
    const emailService = initializeEmailService();

    const emailTemplates = {
      welcome: `Welcome ${data.name}!`,
      notification: `New ${data.title} for you`
    };

    await emailService.send({
      to,
      subject: emailTemplates[template],
      html: renderEmailTemplate(template, data)
    });

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

#### Step 3.6: Add Email Trigger to Event Handler
```typescript
// BEFORE - just API call
const createUser = async (userData) => {
  await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify(userData)
  });
};

// AFTER - add email
const createUser = async (userData) => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify(userData)
  });

  const user = await response.json();

  // Send email
  try {
    await emailService.sendWelcomeEmail(user.email, user.name);
  } catch (error) {
    console.error('Failed to send welcome email:', error);
    // Don't fail user creation if email fails
  }
};
```

### Phase 4: Verify - Test Notifications and Emails

#### Verification Checklist
- [ ] In-app notification shows on success
- [ ] In-app notification shows on error
- [ ] Notification displays correct message
- [ ] Notification disappears after timeout
- [ ] Multiple notifications stack or queue correctly
- [ ] Email sent for welcome event
- [ ] Email contains correct content
- [ ] Email goes to correct recipient
- [ ] Error notification doesn't prevent main action
- [ ] No console errors
- [ ] Existing functionality not affected

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Perform action that triggers success notification
#    - Verify toast appears
#    - Verify message is correct
#    - Verify disappears after 3-5 seconds
# 2. Perform action that causes error
#    - Verify error notification appears
#    - Verify message is clear
# 3. Check email inbox
#    - Verify email received
#    - Verify subject correct
#    - Verify content correct
# 4. Test rapid actions
#    - Verify multiple toasts don't overlap
# 5. Refresh page with notification
#    - Verify notification persists (for persistent notifications)
#    - Or disappears (for toast notifications)
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Find all notification calls
grep -r "notify\|notificationService" src/ --include="*.tsx" | wc -l

# Find all email triggers
grep -r "emailService\|sendEmail" src/ --include="*.tsx" --include="*.ts" | head -10
```

#### Step 4.3: Common Issues and Fixes

**Problem: Notification doesn't appear**
```
Cause: Notification provider not in component tree
Fix: Verify <NotificationProvider> wraps entire app in _app.tsx or main
Verify: grep -r "NotificationProvider" src/ shows in main layout
```

**Problem: Email not sent**
```
Cause: Email service not configured or endpoint missing
Fix: Check /api/emails endpoint exists
Verify: curl -X POST http://localhost:3000/api/emails -H "Content-Type: application/json" -d '{"to":"test@test.com"}'
```

**Problem: Notification blocks user action**
```
Cause: Notification shows async error before completion
Fix: Separate notification from action, don't await it
Verify: User can continue after notification appears
```

**Problem: Email goes to spam**
```
Cause: Email not configured with proper headers
Fix: Set proper From address, add DKIM/SPF
Verify: Check email headers, verify domain setup
```

---

## SCENARIO 9: Add Data Export (CSV/PDF)

### When You Receive This Request
"Add export to [CSV/PDF/Excel] for the [users/items/reports] list"

### Phase 1: Recon - Check Existing Export Patterns

#### Step 1.1: Search for Existing Exports
```bash
# Find export functionality
grep -r "export\|download\|csv\|pdf" src/ --include="*.tsx" --include="*.ts" | grep -i "export\|download" | head -10

# Find export components
find src/components -name "*Export*" -o -name "*Download*" | head -5
```

#### Step 1.2: Check Data Format
```bash
# Find list data structure
cat src/pages/ItemList.tsx | grep -A 30 "useState.*items\|const \[data"
```

**Understand:**
- What fields are displayed
- What order
- How much data (10s vs 1000s items)

#### Step 1.3: Find Export Button Pattern
```bash
# Check if buttons exist
grep -B 3 -A 3 "delete\|edit\|action" src/components/ItemActions.tsx 2>/dev/null | head -15
```

### Phase 2: Impact - Map Export Implementation

#### Step 2.1: Check Data Size
```bash
# How many items typically?
grep -i "limit\|take.*=" src/pages/ItemList.tsx | head -3
```

**If < 1000 items:** Can export all
**If > 1000 items:** Need server-side export

#### Step 2.2: Identify Fields to Export
```bash
# Find what's displayed in list
grep -A 20 "\.map\|<tr\|<td" src/pages/ItemList.tsx | head -30
```

### Phase 3: Implement - Add Export Following Patterns

#### Step 3.1: Create CSV Export Function
```typescript
// src/lib/exporters/csv.ts

export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: (keyof T)[]
) {
  // Determine columns to export
  const keys = columns || Object.keys(data[0] || {}) as (keyof T)[];

  // Create header
  const header = keys.join(',');

  // Create rows
  const rows = data.map(item =>
    keys.map(key => {
      const value = item[key];
      // Handle special values (quotes, dates, etc)
      if (typeof value === 'string' && value.includes(',')) {
        return `"${value.replace(/"/g, '""')}"`;
      }
      return value;
    }).join(',')
  );

  // Combine and download
  const csv = [header, ...rows].join('\n');
  downloadFile(csv, filename, 'text/csv');
}

function downloadFile(content: string, filename: string, mimeType: string) {
  const element = document.createElement('a');
  element.setAttribute('href', `data:${mimeType};charset=utf-8,${encodeURIComponent(content)}`);
  element.setAttribute('download', filename);
  element.style.display = 'none';
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}
```

#### Step 3.2: Create PDF Export Function (If Needed)
```typescript
// src/lib/exporters/pdf.ts
// Install: npm install jspdf

import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

export function exportToPDF<T extends Record<string, any>>(
  data: T[],
  filename: string,
  title: string,
  columns?: (keyof T)[]
) {
  const doc = new jsPDF();

  // Add title
  doc.setFontSize(16);
  doc.text(title, 14, 22);

  // Prepare table data
  const keys = columns || Object.keys(data[0] || {}) as (keyof T)[];
  const headers = [keys];
  const rows = data.map(item => keys.map(key => String(item[key])));

  // Add table
  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 30
  });

  // Save
  doc.save(filename);
}
```

#### Step 3.3: Add Export Button to List
Find list component:
```bash
grep -n "return\|<button" src/pages/ItemList.tsx | head -10
```

**Add button:**
```tsx
// BEFORE
<div className="page-container">
  <h1>Items</h1>
  <button onClick={handleDelete}>Delete</button>
</div>

// AFTER
<div className="page-container">
  <h1>Items</h1>
  <button onClick={handleDelete}>Delete</button>
  <button onClick={handleExport}>Export CSV</button>  {/* NEW */}
</div>
```

#### Step 3.4: Implement Export Handler
```typescript
// In ItemList.tsx

import { exportToCSV } from '@/lib/exporters/csv';

export default function ItemList() {
  const [items, setItems] = useState([]);

  const handleExport = () => {
    // Export visible fields only
    const exportData = items.map(item => ({
      title: item.title,
      status: item.status,
      createdAt: new Date(item.createdAt).toLocaleDateString(),
      email: item.creator?.email
    }));

    exportToCSV(exportData, 'items.csv');
  };

  return (
    <div>
      <button onClick={handleExport}>Export CSV</button>
      {/* Rest of list */}
    </div>
  );
}
```

#### Step 3.5: Add Export Options (If Needed)
```tsx
// BEFORE - simple export
<button onClick={handleExport}>Export</button>

// AFTER - multiple formats
<select onChange={(e) => {
  if (e.target.value === 'csv') handleExportCSV();
  if (e.target.value === 'pdf') handleExportPDF();
}}>
  <option value="">Export as...</option>
  <option value="csv">CSV</option>
  <option value="pdf">PDF</option>
</select>
```

### Phase 4: Verify - Test Export Functionality

#### Verification Checklist
- [ ] Export button appears on list
- [ ] Export button is clickable
- [ ] CSV file downloads with correct filename
- [ ] CSV contains all expected columns
- [ ] CSV contains all visible items
- [ ] CSV headers match column names
- [ ] CSV values are correctly formatted
- [ ] Numbers export as numbers, not text
- [ ] Dates export in readable format
- [ ] Commas in data handled correctly (quoted)
- [ ] List still displays after export
- [ ] Can export multiple times
- [ ] No console errors

#### Step 4.1: Manual Testing Script
```bash
# Start app
npm run dev

# Test in browser:
# 1. Navigate to items list
# 2. Click "Export CSV" button
# 3. Verify download starts
# 4. Open downloaded CSV file
# 5. Verify header row present
# 6. Verify all items included
# 7. Verify all columns included
# 8. Verify dates formatted correctly
# 9. Open in Excel/Sheets
#    - Verify displays correctly
#    - Verify no formatting issues
# 10. Add filter, export again
#     - Verify only filtered items exported
# 11. Check browser console
#     - No errors or warnings
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check
npm run type-check

# Verify export function exists
grep -r "exportToCSV\|exportToPDF" src/ --include="*.tsx" --include="*.ts" | head -5

# Check if library installed (if using jsPDF)
grep "jspdf" package.json
```

#### Step 4.3: Common Issues and Fixes

**Problem: CSV opens with garbled text**
```
Cause: Encoding not UTF-8 or Excel locale issue
Fix: Prepend BOM to CSV: "\uFEFF" + csv content
Verify: File opens correctly in Excel
```

**Problem: Column order wrong in export**
```
Cause: Didn't specify column order
Fix: Pass columns array to exportToCSV()
Verify: Column order matches display order
```

**Problem: Empty cells show "undefined"**
```
Cause: Missing values not handled
Fix: Use || '' to default empty values
Verify: csv = csv.map(item => ({ ...item, field: item.field || '' }))
```

**Problem: Export doesn't include filtered items**
```
Cause: Exporting all data instead of filtered
Fix: Call exportToCSV(filteredItems) not items
Verify: Apply filter, export shows only filtered items
```

---

## SCENARIO 10: Modify an Existing Component's Behavior

### When You Receive This Request
"Change [component] to [new behavior]" without breaking other uses

### Phase 1: Recon - Understand Current Component Usage

#### Step 1.1: Find the Component
```bash
# Find component file
find src/components -name "MyComponent.*" | head -1

# Read it
cat src/components/MyComponent.tsx | head -50
```

#### Step 1.2: Inventory All Props
```bash
# Find interface definition
grep -B 2 -A 10 "interface.*Props\|type.*Props" src/components/MyComponent.tsx
```

#### Step 1.3: Find All Consumers of Component
```bash
# Find everywhere component is imported
grep -r "from.*MyComponent\|import.*MyComponent" src/ --include="*.tsx" --include="*.ts" | head -20

# Find all uses
grep -r "<MyComponent\|MyComponent\(" src/ --include="*.tsx" | head -30
```

**Note all:**
- Different prop combinations used
- Different parent contexts
- Different dependencies

#### Step 1.4: Read Component Implementation Fully
```bash
# Get complete component
cat src/components/MyComponent.tsx
```

**Understand:**
- All props and their defaults
- All state and side effects
- All event handlers
- All return JSX

### Phase 2: Impact - Map Breaking Changes

#### Step 2.1: Analyze Each Consumer
```bash
# For each consumer found, read their usage
grep -B 3 -A 5 "<MyComponent" src/pages/Page1.tsx
grep -B 3 -A 5 "<MyComponent" src/components/Container.tsx
# ... for each consumer
```

**Identify:**
- Required props vs optional
- Default behavior expectations
- State dependencies

#### Step 2.2: Categorize Required Changes
```
Will this change break existing usage?
- YES: Need backward compatibility
- NO: Safe to change directly
```

#### Step 2.3: Check Variants
```bash
# Different ways component is used
grep "<MyComponent" src/ --include="*.tsx" -B 1 -A 3 | grep -v "^--$" | sort | uniq -c
```

### Phase 3: Implement - Make Backward-Compatible Changes

#### Strategy 1: Add New Optional Props (Safest)
```typescript
// BEFORE
interface MyComponentProps {
  title: string;
  onClose: () => void;
}

// AFTER - add new optional prop for new behavior
interface MyComponentProps {
  title: string;
  onClose: () => void;
  newBehavior?: boolean;  // NEW - optional, defaults to false
  newOption?: 'option1' | 'option2';  // NEW
}

export function MyComponent({
  title,
  onClose,
  newBehavior = false,  // Default preserves old behavior
  newOption = 'option1'
}: MyComponentProps) {
  return (
    <div>
      <h1>{title}</h1>
      {newBehavior && <NewFeature />}  {/* Only if opted in */}
      {/* Original content */}
    </div>
  );
}
```

#### Strategy 2: Add Feature Flag
```typescript
interface MyComponentProps {
  title: string;
  onClose: () => void;
  features?: {
    enableNewBehavior?: boolean;
    showNewUI?: boolean;
  };
}

export function MyComponent({
  title,
  onClose,
  features = {}
}: MyComponentProps) {
  const { enableNewBehavior = false, showNewUI = false } = features;

  return (
    <div>
      {showNewUI ? <NewUILayout /> : <OldUILayout />}
      {enableNewBehavior && <NewBehavior />}
    </div>
  );
}
```

#### Strategy 3: Support Both Old and New Behavior
```typescript
interface MyComponentProps {
  title: string;
  onClose: () => void;
  mode?: 'legacy' | 'modern';  // NEW - allows opt-in
}

export function MyComponent({
  title,
  onClose,
  mode = 'legacy'  // Default keeps old behavior
}: MyComponentProps) {
  if (mode === 'modern') {
    return <ModernImplementation title={title} onClose={onClose} />;
  }

  return <LegacyImplementation title={title} onClose={onClose} />;
}
```

#### Step 3.4: Test Each Consumer Path
```bash
# Verify old usage still works
grep "<MyComponent" src/pages/Page1.tsx

# Check if any props are missing defaults
# If prop is not always provided, it MUST have default value
```

**Example of safe vs unsafe change:**
```typescript
// UNSAFE - no default for title
interface Props {
  title?: string;  // Was required, now optional
}

// SAFE - default provided
interface Props {
  title?: string;  // NEW optional prop
  onClose?: () => void;  // Now optional with default
  children?: React.ReactNode;
}
```

### Phase 4: Verify - Test All Consumer Paths

#### Verification Checklist
- [ ] Original usage (no new props) still works
- [ ] New behavior only activates with opt-in prop
- [ ] All existing consumers still render correctly
- [ ] All existing consumers still respond to events
- [ ] New behavior works when enabled
- [ ] No console errors in any consumer
- [ ] No TypeScript errors: `npm run type-check`
- [ ] Each consumer still works independently

#### Step 4.1: Test Each Consumer Manually
```bash
# Start app
npm run dev

# For EACH consumer found:

# 1. Page where MyComponent is used
#    - Verify page loads
#    - Verify component renders
#    - Verify original behavior works
#    - Verify new feature OFF by default

# 2. If enabled with flag:
#    - Pass newBehavior={true}
#    - Verify new behavior activates
#    - Verify old behavior disabled

# 3. Check all event handlers still work
#    - Clicks, inputs, etc.

# 4. Mobile responsiveness (if applicable)
```

#### Step 4.2: Automated Verification
```bash
# TypeScript check - catches breaking changes
npm run type-check

# Count prop usages
grep "<MyComponent" src/ --include="*.tsx" | wc -l

# Verify all consumers still valid
npm run test -- --testPathPattern="MyComponent" 2>/dev/null || echo "No tests"
```

#### Step 4.3: Common Issues and Fixes

**Problem: Consumer breaks with new code**
```
Cause: Made prop required or changed behavior
Fix: Ensure all props have defaults or optional
Verify: Add ? to prop: oldProp?: string = 'default'
```

**Problem: New behavior activates unintentionally**
```
Cause: Default flag value is true
Fix: Default feature flags to false for backward compatibility
Verify: newBehavior = false (not true)
```

**Problem: TypeScript errors in consumers**
```
Cause: Component props interface changed type
Fix: Maintain prop types, extend instead of changing
Verify: npm run type-check passes for all consumers
```

**Problem: One consumer works, another doesn't**
```
Cause: Different props or parent context
Fix: Ensure default values cover all cases
Verify: Test component in isolation with minimal props
```

---

## Quick Reference: Pattern Matching Guide

Use this when implementing ANY change:

### Route Addition Pattern
```
Router file: Check for catch-all route position
New route: Add BEFORE catch-all, maintain order
Navigation: Update menu item list with new path
Guard: Match existing guard pattern (roles, auth)
Verify: List existing routes, ensure new route reachable
```

### Field Addition Pattern
```
Type: Extend interface with optional field (?)
Form JSX: Copy exact pattern from nearest similar field
Validation: Match existing validation style
Error display: Use existing error message className
Submission: Add field to submit payload
Database: Add column, handle missing values
Display: Show field only if present
```

### Permission/Role Pattern
```
Definition: Add to enum/const of all roles
Selector: Add to login/registration dropdown
Router guard: Update all role-checks to include new role
Conditional renders: Update role comparisons (OR logic)
Navigation: Update menu based on roles array
Database: Update role column/enum
Verify: Test each role has correct access
```

### Widget/Card Pattern
```
Create: Copy nearest existing widget file
Data fetch: Match existing fetch pattern (useEffect, hooks)
Loading: Use existing skeleton/loading pattern
Errors: Match existing error display
Add to layout: Insert in grid maintaining responsive classes
Responsive: Keep grid structure, don't change columns
Verify: Dashboard layout, all widgets visible, responsive
```

### Search/Filter Pattern
```
Input: Match existing input styling and layout
State: Add useState for query, track separately
Fetch: Either API call or in-memory filter
Filter logic: Case-insensitive, multiple fields
Display: Use filtered list, show no-results message
Debounce: Add if API calls (avoid excessive requests)
Pagination: Reset page 1 on new search
```

---

## Final Verification Template

For ANY change, run this verification checklist:

```
PHASE 1: Change Isolation
□ Only files needed for feature modified
□ No unrelated files changed
□ Clear git diff showing changes

PHASE 2: Type Safety
□ TypeScript check passes: npm run type-check
□ No @ts-ignore comments added
□ Props have proper types

PHASE 3: Backward Compatibility
□ All existing users of changed code still work
□ New props optional with sensible defaults
□ Old behavior preserved when new feature disabled

PHASE 4: Manual Testing
□ Feature works as intended
□ Original functionality not affected
□ No console errors or warnings
□ Mobile responsive (if applicable)

PHASE 5: Cleanup
□ No debug console.log left
□ No commented-out code
□ Documentation updated if needed
```

---

**Document Created:** 2026-02-26
**Version:** 1.0
**Use Case:** workflow-guardian skill - preventing breaking changes in feature additions

This playbook document provides step-by-step guidance for the 10 most common feature addition scenarios, with exact commands, patterns to follow, common mistakes to avoid, and comprehensive verification checklists.
