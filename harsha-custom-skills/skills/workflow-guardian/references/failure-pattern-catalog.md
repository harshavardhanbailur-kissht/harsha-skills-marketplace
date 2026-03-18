# AI-Induced Failure Pattern Catalog

## Overview

This catalog documents the comprehensive failure patterns that emerge when AI code assistants (like Claude) add features to existing applications. It serves as both a historical record of what went wrong in two real projects and a reference guide for prevention rules.

**Projects Analyzed**:
- **Project 1 (BROKEN)**: Ring Kissht Issue Tracker (`/issue-tracker/`)
- **Project 2 (PARTIALLY BROKEN)**: LOS Issue Tracker (`/los-issue-tracker/`)

---

## CATEGORY 1: Component Duplication Failures

### Pattern 1.1: Copy-Paste Form Pages Without Abstraction

**Severity**: CRITICAL
**Real Example**:
- **File 1**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/pages/SubmitPage.tsx` (391 lines)
- **File 2**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/pages/LoanIssueFormPage.tsx` (603 lines)

**Exact Duplication**:

Lines 43-68 in SubmitPage.tsx (file processing):
```typescript
const processFiles = (newFiles: File[]) => {
  setFileSizeWarning(null);
  const allFiles = [...(formData.attachmentFiles || []), ...newFiles];
  const validation = validateTotalFileSize(allFiles);

  if (!validation.valid) {
    toast.error(validation.message!);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    return;
  }
  // ... more code
};
```

Lines 169-192 in LoanIssueFormPage.tsx (identical logic, 92% code match):
```typescript
const processFiles = (newFiles: File[]) => {
  setFileSizeWarning(null);
  const allFiles = [...(formData.attachmentFiles || []), ...newFiles];
  const validation = validateTotalFileSize(allFiles);

  if (!validation.valid) {
    toast.error(validation.message!);
    if (fileInputRef.current) fileInputRef.current.value = '';
    return;
  }
  // ... more code (identical except minor formatting)
};
```

**Where They Diverge** (critical differences):
- SubmitPage.tsx line 99: `toast.success('Screenshot pasted!')`
- LoanIssueFormPage.tsx lines 219-242: Complex confirmation dialog asking user to ADD or REPLACE files
- SubmitPage.tsx lines 277-328: Simple file list rendering
- LoanIssueFormPage.tsx lines 502-550: Identical file rendering (100% duplication)

**The Maintenance Nightmare**:
1. **Bug Fix Asymmetry**: When a file upload bug is fixed in one component, the developer must remember to fix it in the other. The security audit (EDGE_CASES.md) shows this didn't happen—Image Upload Failure (Pattern 10) is marked UNFIXED in Project 2 but was never addressed in Project 1 either.

2. **Feature Divergence**: The paste event handling differs significantly:
   - SubmitPage always adds files to existing uploads (line 99)
   - LoanIssueFormPage asks whether to ADD or REPLACE (lines 219-242)
   - A new developer adding file features won't know which behavior is correct

3. **Type Divergence**:
   - SubmitPage uses `SubmissionFormData` type
   - LoanIssueFormPage uses `LoanIssueFormData` type
   - Both have `attachmentFiles?: File[]` but different field names elsewhere
   - A refactor to support new file types requires changes in 2 places

4. **Test Coverage Gap**: Both components have no tests. If a bug exists in one, automated tests won't catch that the other wasn't updated.

**What Should Have Happened**:

Extract a reusable `FileUploadForm` component:

```typescript
// src/components/FileUpload.tsx
interface FileUploadProps {
  files: File[];
  previews: Map<string, string>;
  onFilesChange: (files: File[]) => void;
  onRemove: (file: File) => void;
  warning?: string | null;
  uploadProgress?: UploadProgress | null;
  maxSize?: number;
}

export function FileUpload({
  files,
  previews,
  onFilesChange,
  onRemove,
  warning,
  uploadProgress,
  maxSize = 200 * 1024 * 1024,
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFiles = useCallback((newFiles: File[]) => {
    // SINGLE implementation shared by all pages
    const validation = validateTotalFileSize([...files, ...newFiles]);
    if (!validation.valid) {
      toast.error(validation.message!);
      return;
    }
    onFilesChange([...files, ...newFiles]);
  }, [files, onFilesChange]);

  // ... rest of component

  return (
    <>
      {/* Upload UI shared by all forms */}
    </>
  );
}
```

Then both pages use:
```typescript
// SubmitPage.tsx & LoanIssueFormPage.tsx
<FileUpload
  files={formData.attachmentFiles || []}
  previews={attachmentPreviews}
  onFilesChange={(newFiles) =>
    setFormData(prev => ({ ...prev, attachmentFiles: newFiles }))
  }
  onRemove={removeAttachment}
  warning={fileSizeWarning}
  uploadProgress={uploadProgress}
/>
```

**Detection Method**:
- AST-based similarity detection: flag functions/components with >80% code similarity
- Type checking: flag similar types with different names (SubmissionFormData vs LoanIssueFormData)
- Coverage gap detection: flag components with identical logic but no shared tests

**Prevention Rule**:
```
RULE: No copy-pasted functions across components
- If a function is needed in multiple components, extract it to:
  1. A custom hook (if it's stateful)
  2. A shared utility function (if it's pure)
  3. A child component (if it renders UI)
- Maximum allowed code similarity between files: 60% (excluding imports/types)
- Similarity >60% requires refactoring before commit
```

---

### Pattern 1.2: Duplicated Form Validation Logic Without Shared Schema

**Severity**: HIGH
**Real Example**:

SubmitPage.tsx lines 137-156 (form validation):
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!formData.actionable) {
    toast.error('Please select an actionable');
    return;
  }
  if (!formData.detailedActionable.trim()) {
    toast.error('Please provide detailed actionable');
    return;
  }
  if (!formData.lsqLink.trim()) {
    toast.error('Please provide LSQ Link');
    return;
  }
  if (!formData.urn.trim()) {
    toast.error('Please provide URN');
    return;
  }
  // ... 6 more validation checks
};
```

LoanIssueFormPage.tsx lines 273-294 (different validation, same pattern):
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!formData.entity) { toast.error('Please select an entity'); return; }
  if (!formData.issueType) { toast.error('Please select an issue type'); return; }
  if (showSubIssue && !formData.subIssue) { toast.error('Please select a sub-issue'); return; }
  // ... 8 more validation checks
};
```

**What Went Wrong**:
1. **No shared validation schema**: Each form reinvents validation with if-statement chains
2. **Client-side only**: No server-side validation (Firebase/Supabase won't reject invalid data)
3. **Inconsistent error messages**: "Please select..." vs "Please provide..."
4. **No localization support**: Error messages hardcoded in component
5. **Fragile to schema changes**: If required fields change, 2+ places need updating

**What Should Have Happened**:

Use Zod (already a dependency in Project 2) for shared schema:

```typescript
// src/types/validation.ts
import { z } from 'zod';

export const SubmissionFormSchema = z.object({
  actionable: z.string().min(1, 'Actionable is required'),
  detailedActionable: z.string().min(10, 'Must be at least 10 characters'),
  lsqLink: z.string().url('Must be a valid URL'),
  urn: z.string().min(1, 'URN is required'),
  attachmentFiles: z.array(z.instanceof(File)).optional(),
});

export type SubmissionFormData = z.infer<typeof SubmissionFormSchema>;

// In component:
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  try {
    const validData = SubmissionFormSchema.parse(formData);
    // Proceed with submission
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach(err => {
        const field = err.path.join('.');
        toast.error(`${field}: ${err.message}`);
      });
    }
  }
};
```

**Detection Method**:
- Find all `if (!formData.field)` patterns
- If the same field is validated in multiple components, flag for schema extraction
- Runtime validation (Zod/Superstruct) should be mandatory for forms that save to database

**Prevention Rule**:
```
RULE: All form data must use runtime validation schema
- All forms must have a Zod/Superstruct schema defined in types/
- Schema validation must happen before database write
- Same field validated in 2+ places = extract to shared schema
- Server-side validation must mirror client schema (no trust client)
```

---

## CATEGORY 2: UI/UX Fragmentation Failures

### Pattern 2.1: Inconsistent Color Usage Across Components

**Severity**: HIGH
**Real Example**:

Project 1 color usage extracted from source:

SubmitPage.tsx:
- Line 205: `bg-ring-50` (Ring brand light background)
- Line 206: `border-ring-200`
- Line 206: `text-ring-700` (Ring brand text)
- Line 359: `bg-ring-200` (Ring brand progress bar background)
- Line 361: `bg-ring-600` (Ring brand progress bar fill)
- Line 354: `bg-ring-50` (warning background)
- Line 356: `text-ring-700` (warning text)

But LoanIssueFormPage.tsx:
- Line 355: `bg-ring-50` (consistent)
- Line 356: `border-ring-200` (consistent)
- Line 356: `text-ring-700` (consistent)
- But ALSO uses:
  - Line 546: `bg-amber-50` (warning, should be ring-50)
  - Line 547: `border-amber-200` (should be ring-200)
  - Line 547: `text-amber-800` (should be ring-700)

**The Fragmentation Issue**:

1. **Brand Color Divergence**: Warnings use amber-* in LoanIssueFormPage but ring-* in SubmitPage
2. **No Design Token System**: Colors are scattered throughout files as magic strings
3. **Maintenance Nightmare**: If Ring brand color changes from #xxx to #yyy, 20+ files need updating
4. **Inconsistent UX**: Users see different colors for the same UI pattern across pages

**What Should Have Happened**:

Create a design token system in Tailwind config:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'brand': {
          50: '#f0f9ff',  // Ring brand light
          100: '#e0f2fe',
          200: '#bae6fd',
          600: '#0284c7',  // Ring brand primary
          700: '#0369a1',  // Ring brand dark
        },
        'semantic': {
          'success': '#10b981',  // emerald-500
          'warning': '#f59e0b',  // amber-500
          'error': '#ef4444',    // red-500
          'info': '#3b82f6',     // blue-500
        },
      },
    },
  },
};
```

Then use semantic tokens everywhere:
```typescript
// SubmitPage.tsx
<div className="bg-semantic-warning border-2 border-semantic-warning text-semantic-warning">

// LoanIssueFormPage.tsx
<div className="bg-semantic-warning border-2 border-semantic-warning text-semantic-warning">
// Now BOTH use same colors!
```

**Detection Method**:
- Extract all Tailwind color classes from all components
- Build a color usage map: `{ "bg-ring-50": [file1.tsx:205, file2.tsx:355, ...], "bg-amber-50": [file3.tsx:546] }`
- Flag when same semantic meaning uses different color tokens (e.g., warning as both amber-50 and ring-50)
- Enforce that arbitrary colors only exist in config, not in component classNames

**Prevention Rule**:
```
RULE: No arbitrary color values in component classNames
- All colors must be defined in tailwind.config.js
- Create semantic color tokens (success, warning, error, info) in config
- Flag usage of non-semantic Tailwind colors in components
- Enforce: 80%+ of colors should come from semantic tokens
- Design token changes go through config only, auto-propagate everywhere
```

---

### Pattern 2.2: Button and Card Styling Inconsistencies

**Severity**: MEDIUM
**Real Example**:

Project 1 Button component (`/src/components/ui/Button.tsx`):
```typescript
// Only SOME styling in the component
<button className={`px-4 py-2 rounded font-medium ${variantClasses}`}>
```

But buttons in SubmitPage.tsx (line 377-385) have inline classes:
```typescript
<Button
  type="submit"
  variant="primary"
  className="w-full"  // width is inline
  disabled={isSubmitting}
  isLoading={isSubmitting}
>
```

And in LoanIssueFormPage.tsx (line 590-598):
```typescript
<Button
  type="submit"
  variant="primary"
  className="w-full"  // same, but what if someone uses "w-80" elsewhere?
  disabled={isSubmitting}
  isLoading={isSubmitting}
>
```

**The Fragmentation**:
1. **Variant definitions unclear**: What exactly does "primary" style? Is it in Button.tsx or hardcoded?
2. **Size inconsistency**: Some buttons are `w-full`, others might be `w-80`. No consistency.
3. **Hover/focus states**: Are they consistent? Hard to tell without reading all files.
4. **Button content spacing**: "Submit" vs "Submit & Process" vs "Claim Ticket"—do all have same padding?

**The Cascade Effect**:
When a designer says "make buttons more rounded", a developer has to:
1. Find the Button component
2. Update the rounded value
3. Check all pages for inline overrides
4. Pray they didn't miss any

**What Should Have Happened**:

Define button variants completely in the component:

```typescript
// src/components/ui/Button.tsx
type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

const variantStyles: Record<ButtonVariant, string> = {
  primary: 'bg-ring-600 text-white hover:bg-ring-700 active:bg-ring-800',
  secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
  danger: 'bg-red-600 text-white hover:bg-red-700',
  ghost: 'bg-transparent text-ring-600 hover:bg-ring-50',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-md',
  md: 'px-4 py-2 text-base rounded-lg',
  lg: 'px-6 py-3 text-lg rounded-xl',
};

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading,
  children,
  disabled,
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      className={`
        font-medium transition-colors focus:outline-none focus:ring-2
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      {...props}
    >
      {isLoading ? <Spinner /> : children}
    </button>
  );
}
```

Now pages use it WITHOUT overrides:
```typescript
// SubmitPage.tsx
<Button variant="primary" size="lg">Submit</Button>

// LoanIssueFormPage.tsx
<Button variant="primary" size="lg">Submit & Process</Button>
// Same styling, no "className" overrides!
```

**Detection Method**:
- AST analysis of component props: flag any `className` prop that doesn't match predefined patterns
- If a component has both `variant="primary"` and `className="..."`, the className likely contains style overrides
- Check for duplicate Tailwind classes across files (multiple files defining the same button style independently)

**Prevention Rule**:
```
RULE: Components must encapsulate all styling
- UI components (Button, Badge, Card, Input) must define all their styles internally
- Props should control APPEARANCE (variant, size, color) not styling
- FORBIDDEN: className overrides in component props (except rare exceptions)
  - Allowed: <Button className="mt-4" /> (layout/spacing only)
  - Forbidden: <Button className="bg-red-500 px-8 py-3" /> (appearance)
- Variant lists must be exhaustive: if adding a new variant, must update component
- All button styles must be tested in Storybook to ensure consistency
```

---

### Pattern 2.3: Typography Inconsistencies (Font Size, Weight, Line Height)

**Severity**: MEDIUM
**Real Example**:

SubmitPage.tsx typography:
- Line 221: `<h1 className="text-2xl font-bold">Submit Form</h1>`
- Line 222: `<p className="text-sm text-gray-500">Fill out the form below...</p>`
- Line 241: `<label className="block text-sm font-medium text-gray-700">Attachments</label>`

LoanIssueFormPage.tsx typography:
- Line 394: `<h1 className="text-2xl font-bold">Loan Issue Form</h1>`
- Line 395: `<p className="text-sm text-gray-500">Submit loan issue details...</p>`
- Line 402: `<h3 className="text-sm font-semibold text-gray-900 border-b border-gray-200 pb-2">Issue Details</h3>`

**The Problem**:
1. **h1 + p pattern identical** in both pages (lucky match)
2. **h3 styling** (line 402 of LoanIssueFormPage) is UNIQUE—no h3 in SubmitPage
3. **Missing semantic hierarchy**: What's the relationship between text-sm + font-medium vs text-sm + font-semibold?
4. **No spacing standards**: Some labels have `mb-1.5`, others `mb-2`. Why the difference?

**What Should Have Happened**:

Define typography scale in design tokens:

```typescript
// src/styles/typography.ts
export const typography = {
  h1: 'text-4xl font-bold leading-tight tracking-tight',  // Page titles
  h2: 'text-2xl font-bold leading-tight',                  // Section headers
  h3: 'text-lg font-semibold leading-tight',               // Subsection headers
  h4: 'text-base font-semibold',                           // Small headers
  body: {
    lg: 'text-base leading-relaxed',                       // Default body text
    md: 'text-sm leading-normal',                          // Secondary text
    sm: 'text-xs leading-normal',                          // Tiny text (hints, captions)
  },
  label: 'text-sm font-medium text-gray-700',              // Form labels
  caption: 'text-xs text-gray-500',                        // Captions/hints
};

// Usage in component:
export function FormSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <h3 className={typography.h3}>
        {title}
      </h3>
      {children}
    </div>
  );
}
```

Then both pages use semantic components:
```typescript
<FormSection title="Issue Details">
  {/* Children */}
</FormSection>
```

**Detection Method**:
- Extract all `text-*` and `font-*` classes from all files
- Build a frequency map: `{ "text-sm font-medium": 15, "text-sm font-semibold": 8 }`
- Flag when the same semantic purpose (label, caption, heading) uses different style combinations
- Warning if >3 different combinations for the same semantic element (should be max 1)

**Prevention Rule**:
```
RULE: Typography must use predefined scale
- Create src/styles/typography.ts with semantic tokens
- All headings must use h1-h4 tokens
- All body text must use body.lg / body.md / body.sm
- All labels must use label token
- Direct Tailwind text/font classes only in design tokens file
- Refactor all inline text-* font-* classes to use semantic tokens
```

---

### Pattern 2.4: Spacing and Layout Inconsistencies

**Severity**: MEDIUM
**Real Example**:

SubmitPage.tsx spacing:
- Line 218: `<div className="max-w-xl mx-auto">`  — Container width
- Line 220: `<div className="mb-6">` — Margin between header and form
- Line 226: `<div className="card p-6">` — Card padding
- Line 227: `<form onSubmit={handleSubmit} className="space-y-5">` — Form field spacing

LoanIssueFormPage.tsx spacing:
- Line 392: `<div className="max-w-xl mx-auto">` — Same container width ✓
- Line 393: `<div className="mb-6">` — Same margin ✓
- Line 398: `<div className="card p-6">` — Same card padding ✓
- Line 399: `<form onSubmit={handleSubmit} className="space-y-6">` — **Different!** `space-y-6` not `space-y-5`

**The Fragmentation**:
1. **Inconsistent field spacing**: space-y-5 vs space-y-6 (0.25rem difference)
2. **Why different?** LoanIssueFormPage has more fields (31 inputs vs 12)—but is more spacing the solution?
3. **Not a conscious design decision**: Probably just copy-pasted and tweaked without thinking

**Downstream Effects**:
- User sees different "breathing room" between forms
- If designer requests "tighten spacing to space-y-4", developer must update both
- No consistency in vertical rhythm

**What Should Have Happened**:

Define spacing constants:

```typescript
// src/styles/spacing.ts
export const spacing = {
  form: {
    containerMaxWidth: 'max-w-xl',
    horizontalPadding: 'mx-auto',
    sectionMargin: 'mb-6',
    fieldGap: 'space-y-5',      // Standard form field spacing
    sectionGap: 'space-y-6',    // Between form sections
    groupGap: 'space-y-4',      // Within a group of related fields
  },
  card: {
    padding: 'p-6',
    borderRadius: 'rounded-lg',
    shadow: 'shadow-card',
  },
};

// Usage:
<div className={spacing.form.containerMaxWidth}>
  <form className={spacing.form.fieldGap}>
    {/* All fields automatically get consistent spacing */}
  </form>
</div>
```

**Detection Method**:
- Extract all margin/padding/gap classes: `mb-*`, `mt-*`, `p-*`, `space-y-*`, `gap-*`
- Build frequency map for each component type
- Flag when same element type has different spacing values across files
- If 2+ forms use different `space-y-*`, flag as inconsistency

**Prevention Rule**:
```
RULE: All spacing must use predefined scale
- Create src/styles/spacing.ts with tokens for:
  - Form field gaps (space-y-5)
  - Section gaps (space-y-6)
  - Card padding (p-6)
  - Container widths (max-w-xl)
- All containers must respect maxWidth tokens
- All forms must use same field spacing
- Justify any deviation (e.g., "extra spacing for long field lists") in comments
```

---

## CATEGORY 3: Role System Confusion Failures

### Pattern 3.1: Role Name Inconsistency Creating Security Bypasses

**Severity**: CRITICAL
**Real Example**:

Project 1 has ROLE CONFUSION:

File: `/src/types/index.ts` line 3:
```typescript
export type UserRole = 'sm' | 'tech_support_team' | 'product_support';
```

File: `/src/pages/SubmitPage.tsx` line 19:
```typescript
const { role } = useSimpleAuth();
```

File: `/src/contexts/SimpleAuthContext.tsx` lines 27-29:
```typescript
if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support') {
  setRole(storedRole);
  setIsAuthenticated(true);
}
```

File: `/src/App.tsx` lines 25, 36, 47:
```typescript
<ProtectedRoute allowedRoles={['sm']}>
<ProtectedRoute allowedRoles={['product_support']}>
<ProtectedRoute allowedRoles={['sm', 'tech_support_team']}>
```

**But in the ARCHITECTURE_GUIDE.md** and **actual Firestore rules**:
```
The documentation says there are only TWO roles:
- "Product Support" (submits forms)
- "Tech Support Team" (views submissions)

But TypeScript defines THREE:
- 'sm' (Sales Manager?)
- 'tech_support_team' (matches docs)
- 'product_support' (matches docs)

And routes use INCONSISTENT role names:
- Line 25: '/submit' route checks ['sm']
- Line 36: '/loan-issue' route checks ['product_support']
```

**The Security Vulnerability**:

A developer adds a new route and checks the wrong role:
```typescript
// New route for "create report"
<ProtectedRoute allowedRoles={['tech_support_team']}>
  <ReportPage />
</ProtectedRoute>
```

But they meant to allow BOTH support roles. However, because the role names are:
- Sometimes short ('sm')
- Sometimes long ('tech_support_team')
- Sometimes descriptive ('product_support')

...they can't remember which roles exist. They might:
1. Invent a new role name: `allowedRoles={['tech_support']}`—NOT IN TYPE
2. Use the wrong role: `allowedRoles={['product_support']}` when they meant 'sm'
3. Get no TypeScript error because TypeScript doesn't enforce that role names match values used in routes

**The Cascade Effect**:
1. A new developer adds role 'admin' in one place but 'administrator' in another
2. The type doesn't catch it
3. Some features only work with 'admin', some with 'administrator'
4. A security audit finds that certain users can't access features they should

Project 2 (LOS Issue Tracker) PARTIALLY FIXED this:

File: `/src/types/index.ts`:
```typescript
export type User = {
  role: 'product_support' | 'admin';
};
```

But they STILL have inconsistency. The auth context uses `'product_support'` and `'admin'`, which is good. But there's NO SINGLE SOURCE OF TRUTH for what roles exist.

**What Should Have Happened**:

Create an ENUM with single source of truth:

```typescript
// src/types/roles.ts
export enum UserRole {
  PRODUCT_SUPPORT = 'product_support',
  ADMIN = 'admin',
  TECH_SUPPORT = 'tech_support',  // If needed
}

export const ROLE_DESCRIPTIONS: Record<UserRole, string> = {
  [UserRole.PRODUCT_SUPPORT]: 'Submits queries',
  [UserRole.ADMIN]: 'Claims and resolves queries',
  [UserRole.TECH_SUPPORT]: 'Views all submissions',
};

// Type definition uses enum
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
}

// Route definition with TypeScript safety
type RouteConfig = {
  path: string;
  allowedRoles: UserRole[];
  component: React.ComponentType;
};

const ROUTES: RouteConfig[] = [
  {
    path: '/submit',
    allowedRoles: [UserRole.PRODUCT_SUPPORT],
    component: SubmitPage,
  },
  {
    path: '/admin',
    allowedRoles: [UserRole.ADMIN],
    component: AdminPanel,
  },
];

// Runtime check (TypeScript ensures allRole is valid enum value)
function hasAccess(userRole: UserRole, requiredRoles: UserRole[]): boolean {
  return requiredRoles.includes(userRole);
}
```

Now if a developer typos a role:
```typescript
// TypeScript ERROR: 'adminn' is not a valid UserRole
allowedRoles: [UserRole.ADMINN]  // ❌ COMPILE ERROR
```

**Detection Method**:
- Extract all string literals used as role values: `allowedRoles={['sm']}` → 'sm'
- Extract all role type definitions
- Build a set of unique role values used vs. defined
- Flag if roles used in code ≠ roles defined in types
- Flag if role is used as string literal (should use enum)
- Flag if same semantic role has 2+ different names (e.g., 'admin' vs 'administrator')

**Prevention Rule**:
```
RULE: All roles must use TypeScript enum from single file
- Define all possible roles in src/types/roles.ts as an ENUM
- Import roles from types/roles.ts, NEVER use string literals
- Every route/permission check must use enum values
- Role names must be snake_case (no abbreviations)
- If role is added/removed, update ONLY roles.ts
- Compile error if someone tries to use undefined role
- Document each role in ROLE_DESCRIPTIONS
```

---

### Pattern 3.2: Role-Based Access Control Without Centralized Permission Model

**Severity**: HIGH
**Real Example**:

Project 1 has permission checks scattered throughout:

File: `/src/pages/SubmitPage.tsx` line 19:
```typescript
const { role } = useSimpleAuth();
// Uses role but doesn't check it
```

File: `/src/App.tsx` lines 25, 36, 47, 58, 69, 80:
```typescript
<ProtectedRoute allowedRoles={['sm']}>
<ProtectedRoute allowedRoles={['product_support']}>
<ProtectedRoute allowedRoles={['sm', 'tech_support_team']}>
// Permission logic is in App.tsx, scattered across routes
```

File: `/src/components/ProtectedRoute.tsx`:
```typescript
// Probably checks: if (!allowedRoles.includes(role)) return <Unauthorized />
```

**The Problems**:
1. **Scattered checks**: Can't see all role checks in one place
2. **No role hierarchy**: Is 'sm' superior to 'product_support'? Unclear.
3. **No feature flags**: If a role should access "create report" but we haven't added the UI yet, how do we prevent access?
4. **No audit trail**: When a user accesses a route, we don't log which role was checked
5. **Hard to add permissions**: Adding a new permission (e.g., "admin can delete") requires:
   - Find all routes that should have this permission
   - Update each ProtectedRoute manually
   - Hope you didn't miss any

**What Should Have Happened**:

Create a centralized permission model:

```typescript
// src/permissions/model.ts
import { UserRole } from '@/types/roles';

// Define what each role can DO (not just access routes)
export const PERMISSIONS: Record<UserRole, Set<string>> = {
  [UserRole.PRODUCT_SUPPORT]: new Set([
    'submit:create',
    'submission:view_own',
    'submission:list_own',
  ]),
  [UserRole.ADMIN]: new Set([
    'submission:view_all',
    'submission:list_all',
    'submission:claim',
    'submission:resolve',
    'submission:delete',
    'admin:view_stats',
  ]),
  [UserRole.TECH_SUPPORT]: new Set([
    'submission:view_all',
    'submission:list_all',
  ]),
};

// Helper function
export function can(role: UserRole, action: string): boolean {
  return PERMISSIONS[role]?.has(action) ?? false;
}

// Usage in route:
interface RouteConfig {
  path: string;
  component: React.ComponentType;
  requiredPermission: string;
}

const ROUTES: RouteConfig[] = [
  {
    path: '/submit',
    component: SubmitPage,
    requiredPermission: 'submit:create',
  },
  {
    path: '/admin',
    component: AdminPanel,
    requiredPermission: 'admin:view_stats',
  },
];

// In App.tsx:
{ROUTES.map(route => (
  <Route
    key={route.path}
    path={route.path}
    element={
      <PermissionGate permission={route.requiredPermission}>
        <route.component />
      </PermissionGate>
    }
  />
))}

// Inside components:
export function SubmitButton() {
  const { role } = useAuth();

  if (!can(role, 'submit:create')) {
    return <button disabled>No permission</button>;
  }

  return <button>Submit</button>;
}
```

Now adding a new permission is ONE CHANGE:
```typescript
export const PERMISSIONS: Record<UserRole, Set<string>> = {
  [UserRole.PRODUCT_SUPPORT]: new Set([
    'submit:create',
    'submission:view_own',
    'submission:list_own',
    'submission:delete_own',  // ← Just add here
  ]),
  // ... rest auto-propagates everywhere can() is used
};
```

**Detection Method**:
- Find all permission checks in code: `role ===`, `allowedRoles.includes`, `role !==`
- Flag if same permission is checked in >1 place (should be centralized)
- Flag if permission logic is scattered across multiple files (should be in one model)
- Flag if permission names don't follow pattern `resource:action` (e.g., 'can_delete' should be 'submission:delete')

**Prevention Rule**:
```
RULE: All permissions must be centralized in permissions model
- Create src/permissions/model.ts with PERMISSIONS constant
- All role checks must go through can(role, action) helper
- Permission names must follow resource:action pattern
- Adding new permission = update PERMISSIONS constant ONLY
- No inline role checks in components (use can() helper)
- Audit log should record which permissions were checked on access
```

---

## CATEGORY 4: Architecture Layer Stacking Failures

### Pattern 4.1: Multiple Storage Backends Creating Consistency Problems

**Severity**: CRITICAL
**Real Example**:

Project 1 uses DUAL STORAGE:

File: `/src/lib/submissions.ts` lines 1-17:
```typescript
import {
  collection, doc, getDoc, getDocs, query, orderBy, where,
  serverTimestamp, runTransaction, onSnapshot, setDoc, updateDoc,
} from 'firebase/firestore';
import { db } from './firebase';
import { uploadFileToDrive, type UploadProgress } from './driveUpload';
```

This file imports BOTH:
1. **Firestore** (database) for document storage
2. **Google Drive** (file storage) for file uploads

File: `/src/lib/driveUpload.ts`:
```typescript
// Uploads files to Google Drive
// Returns shareable URLs for storing in Firestore
```

**The Architecture**:
```
React Component
    ↓ submits form
    ├→ uploadFileToDrive() → Google Drive (file storage)
    │   └→ Returns shareable URL
    └→ createSubmission() → Firestore (document storage)
        └→ Stores URL + metadata
```

**Where It Breaks**:

1. **Atomic transaction failure**:
   - File uploads to Google Drive ✓
   - Firestore write fails (network error, quota exceeded)
   - Result: File exists in Drive but metadata not saved
   - User doesn't know the submission was incomplete

2. **Storage quota limits**:
   - Google Drive has space limits
   - Firestore has transaction limits
   - If Drive upload succeeds but Firestore transaction fails, orphaned files pile up

3. **Orphaned file cleanup**:
   - There's no mechanism to cleanup Drive files if Firestore write fails
   - Result: Over time, Drive fills with data that app thinks doesn't exist

4. **Access control divergence**:
   - Drive has its own sharing model (shareable link)
   - Firestore has its own security rules
   - User might have access to Drive file but not the metadata (or vice versa)

5. **Cascading feature complexity**:
   When adding "delete submission" feature, you must:
   - Delete from Firestore ✓
   - Delete from Google Drive ✓
   - But what if Firestore delete succeeds and Drive delete fails?

**Real Bug That Happened**:

File: `/src/lib/submissions.ts` lines 98-102:
```typescript
// Set first file as legacy fields for backward compatibility
if (i === 0) {
  attachmentUrl = uploadResult.shareableUrl;
  attachmentDriveId = uploadResult.fileId;
}
```

This suggests they MIGRATED from single-file to multi-file uploads. But the legacy code is still there, creating two possible states:
- Old submissions: `attachmentUrl` field is populated, `attachments` array is empty
- New submissions: `attachmentUrl` is the first file, `attachments` array has all files
- Result: Query logic must handle both cases, creating bugs

**What Should Have Happened**:

Use a SINGLE storage backend for EVERYTHING:

Option 1 - **Firestore Storage** (recommended):
```typescript
// src/lib/storage.ts
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { storage } from './firebase';

export async function uploadFile(
  file: File,
  submissionId: string,
  onProgress?: (progress: UploadProgress) => void
): Promise<string> {
  // Upload to Firebase Storage (same Firebase project as Firestore)
  const storageRef = ref(storage, `submissions/${submissionId}/${file.name}`);

  await uploadBytes(storageRef, file);
  const downloadUrl = await getDownloadURL(storageRef);

  return downloadUrl;
}

// In submission creation:
async function createSubmission(data: SubmissionFormData, role: UserRole) {
  const submissionId = await generateSubmissionId();

  // Upload all files to Firebase Storage
  const attachmentUrls = [];
  for (const file of data.attachmentFiles || []) {
    const url = await uploadFile(file, submissionId);
    attachmentUrls.push(url);
  }

  // Store everything in Firestore (single transaction)
  const submissionRef = doc(db, 'submissions', submissionId);
  await setDoc(submissionRef, {
    id: submissionId,
    attachmentUrls,  // All in one field
    submittedBy: role,
    submittedAt: serverTimestamp(),
  });

  return submissionId;
}
```

**Benefits**:
- Single transaction (all-or-nothing)
- Atomic delete (delete Firestore doc → also deletes files via cascade rules)
- Single access control model
- No orphaned files
- No schema migration complexity

**Detection Method**:
- Build a dependency graph of storage systems used
- Flag if >1 external storage system is used (Drive + Firestore, S3 + Database, etc.)
- Flag if file uploads happen in different services (one module uses Drive, another uses Firebase)
- Trace data flow: if upload succeeds but database write fails, flag as consistency risk

**Prevention Rule**:
```
RULE: Use single storage backend per app
- Choose ONE: Firebase Storage, S3, or managed hosting
- All files must go to same backend
- Database (Firestore, PostgreSQL) stores ONLY metadata/URLs
- File deletion must be atomic with metadata deletion
- No file orphans: implement cleanup job if deletion fails
- Ban: uploadFileToDrive() + Firestore together
  - Use either: Firebase Storage + Firestore OR Google Drive + Database
  - Not both
```

---

### Pattern 4.2: Adding Services on Top of Existing Services Creates Dependency Explosion

**Severity**: HIGH
**Real Example**:

Project 2 (LOS Issue Tracker) has layered complexity:

File: `/src/hooks/useTickets.ts` lines 1-3:
```typescript
import { useState, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import type { Ticket } from '../types';
```

This hook depends on:
1. Supabase Client (for database queries)
2. React Hooks (for state management)

But then there's ALSO:

File: `/src/hooks/useTickets.ts` lines 31-70 (syncToSheets function):
```typescript
export async function syncToSheets(
  ticket: Ticket,
  operation: 'append' | 'update'
): Promise<{ success: boolean; error?: string }> {
  try {
    const { data, error: invokeError } = await supabase.functions.invoke('sync-to-sheets', {
      body: { ticket_number: ticket.ticket_number, operation },
    });
    // ...
  }
}
```

So now useTickets ALSO depends on:
3. Supabase Edge Functions (for Google Sheets sync)
4. Google Sheets API (via the Edge Function)

**The Dependency Stack**:
```
React Component
  ├→ useTickets() hook
  │   ├→ Supabase JS Client
  │   │   └→ PostgreSQL Database
  │   └→ Supabase Edge Functions
  │       └→ Google Sheets API
  │           └→ Google Service Account
```

**Where It Breaks**:

1. **Cascading failures**:
   - If Edge Function is down, `syncToSheets()` fails
   - The component doesn't know if it's a network error, permission error, or function not deployed
   - User sees generic "Sheet sync failed"

2. **Error handling explosion**:
   - Database error: handle with `err.code === 'PGRST301'`
   - Edge Function error: handle with HTTP status codes (4xx, 5xx)
   - Google Sheets error: hidden inside Edge Function logs
   - Component must handle all three → spaghetti code

3. **Testing nightmare**:
   - To test `useTickets`, must mock:
     - Supabase JS client
     - Supabase database responses
     - Edge Function invocation
     - Google Sheets API responses
   - 4 mocking layers instead of 1

4. **Debugging impossibility**:
   - "Sheet didn't update" could mean:
     - Database query wrong
     - Edge Function not deployed
     - Google Sheet ID secret not set
     - Service account permissions wrong
     - Network timeout on any layer
   - Debugging requires knowledge of 4 systems

File: `.deep-think/EDGE_CASES.md` line 8:
```markdown
### 1. sync-to-sheets Has Zero Authentication [FIXED 2026-02-12]
**Location**: `supabase/functions/sync-to-sheets/index.ts`

**Fix**: Added JWT verification via `createClient` + `auth.getUser()`.
Also re-fetches ticket from DB (M5 fix) and escapes all columns (M1 fix).
```

This shows the cascading complexity: to FIX one vulnerability, they had to:
1. Add JWT verification in Edge Function
2. Re-fetch ticket (adds database call)
3. Escape all columns (adds data sanitization logic)
4. Result: Simple "sync to sheets" is now 50+ lines of defensive code

**What Should Have Happened**:

Flatten the dependency stack. Options:

**Option 1: Move syncing to React Component (Simplest)**:
```typescript
// Remove Google Sheets sync from automatic flow
// Instead: User manually clicks "Sync to Sheets" button

export async function syncToSheets(ticket: Ticket): Promise<void> {
  // Call Edge Function explicitly only when user requests
  const response = await fetch(
    `${supabase.functions.url}/sync-to-sheets`,
    {
      method: 'POST',
      body: JSON.stringify({ ticket_number: ticket.ticket_number }),
      headers: { Authorization: `Bearer ${token}` },
    }
  );

  if (!response.ok) {
    throw new Error(`Sync failed: ${response.statusText}`);
  }
}

// In component:
async function handleRetrySync() {
  setIsSyncing(true);
  try {
    await syncToSheets(ticket);
    toast.success('Synced to Sheets!');
  } catch (err) {
    toast.error(`Sync error: ${err.message}`);
  } finally {
    setIsSyncing(false);
  }
}
```

**Benefits**:
- Clear separation: component requests sync when user asks
- Single error path: catch in component
- No cascading failures: Sheets sync is optional, not core

**Option 2: Create Facade Pattern (Recommended)**:
```typescript
// src/services/ticketService.ts - Single point of integration
class TicketService {
  private supabase = supabase;

  async createTicket(data: CreateTicketData): Promise<Ticket> {
    // 1. Create in database
    const ticket = await this.supabase
      .from('tickets')
      .insert([data])
      .select()
      .single();

    // 2. Sync to Sheets (non-blocking)
    this.syncToSheets(ticket).catch(err => {
      console.error('Sheets sync failed (non-blocking):', err);
    });

    return ticket;
  }

  private async syncToSheets(ticket: Ticket): Promise<void> {
    // Edge Function call encapsulated here
    // Only this method knows about Google Sheets
  }
}

// In hooks:
export function useTickets() {
  const ticketService = useMemo(() => new TicketService(), []);

  const createTicket = useCallback(async (data) => {
    // All complexity hidden in service
    return ticketService.createTicket(data);
  }, [ticketService]);
}

// In component:
async function handleSubmit(data) {
  try {
    const ticket = await ticketService.createTicket(data);
    toast.success('Created!');
  } catch (err) {
    toast.error(err.message);
  }
}
```

**Benefits**:
- All Sheets logic encapsulated in ONE service
- Component doesn't know about Sheets
- Easy to test (mock ticketService)
- Easy to remove/replace Sheets later

**Detection Method**:
- Build dependency graph: `useTickets` → `supabase.functions.invoke()` → Edge Function
- Flag if service A calls service B which calls service C (depth > 2)
- Count number of external APIs called from single hook: if >2, flag for refactoring
- Trace error paths: if error handling requires knowledge of 3+ systems, flag as untestable

**Prevention Rule**:
```
RULE: Services must not depend on other services
- Each service owns ONE responsibility (database OR email OR Sheets)
- If need to combine services, create a Facade
- No importing supabase.functions from a hook that also imports supabase.from()
- Maximum service depth: Component → Service → Database (3 layers)
- If adding a new integration (Sheets, Email, Slack), create NEW service, don't extend existing
- Dependencies should flow: Component → Service → Database/API
  Never: Component → Service1 → Service2 → Database
```

---

## CATEGORY 5: Type Safety Erosion Failures

### Pattern 5.1: Union Types Too Loose, Missing Fields at Runtime

**Severity**: HIGH
**Real Example**:

Project 1 type definition (`/src/types/index.ts` lines 14-45):
```typescript
export interface Submission {
  id: string;
  actionable: string;
  detailedActionable: string;
  lsqLink: string;
  urn: string;
  attachmentUrl?: string;  // ← Optional but sometimes required!
  attachmentDriveId?: string;  // ← Optional but sometimes required!
  attachments?: Attachment[];  // ← New field, not in old submissions
  comments?: string;
  submittedBy: UserRole;
  submittedAt: Timestamp;
  // ... more fields
  formType?: 'standard' | 'loan_issue';  // ← Discriminant added later
  entity?: string;
  issueType?: string;
  // ... 15 more optional fields
}
```

**The Problem**:

1. **Discriminated Union without discriminator check**:
   - `formType` SHOULD determine which other fields are present
   - But code doesn't check it:
   ```typescript
   const submission = await getSubmission(id);
   // TypeScript says: submission.entity could be undefined
   // But at runtime, if formType === 'loan_issue', it's always defined!

   console.log(submission.entity); // TypeScript warning but works if formType='loan_issue'
   ```

2. **Backward compatibility hack**:
   - Old submissions have `attachmentUrl` and `attachmentDriveId`
   - New submissions have `attachments` array
   - Code must handle BOTH:
   ```typescript
   const hasAttachments = submission.attachments && submission.attachments.length > 0;
   const legacyHasAttachment = submission.attachmentUrl && submission.attachmentUrl.length > 0;

   if (hasAttachments) {
     // Use new format
   } else if (legacyHasAttachment) {
     // Use old format
   }
   ```
   This is fragile. What if BOTH are present? What's the source of truth?

3. **Runtime crashes waiting to happen**:
   ```typescript
   // Type says attachmentFiles is optional
   const files = formData.attachmentFiles || [];

   // But in component:
   formData.attachmentFiles.map(file => ...)  // ← Crashes if undefined!
   ```

4. **Missing discriminator check**:
   ```typescript
   // This is valid TypeScript:
   const sub: Submission = {
     id: 'sub-1',
     actionable: 'follow up',
     formType: 'loan_issue',  // Says it's loan issue form
     // ... but missing entity, issueType, etc.!
   };

   // No TypeScript error! formType doesn't enforce the structure.
   ```

**What Should Have Happened**:

Use proper discriminated unions:

```typescript
// src/types/submissions.ts

// Base submission all forms share
interface BaseSubmission {
  id: string;
  submittedBy: UserRole;
  submittedAt: Timestamp;
  attachments: Attachment[];  // Always required, always array (not optional)
}

// Standard form variant
interface StandardSubmission extends BaseSubmission {
  formType: 'standard';
  actionable: string;  // Required for standard
  detailedActionable: string;
  lsqLink: string;
  urn: string;
}

// Loan issue form variant
interface LoanIssueSubmission extends BaseSubmission {
  formType: 'loan_issue';
  entity: string;  // Required for loan issue
  issueType: string;
  opportunityId: string;
  name: string;
  // NO actionable, detailedActionable, lsqLink (they don't exist on this form)
}

// Discriminated union
export type Submission = StandardSubmission | LoanIssueSubmission;

// Usage in component:
function renderSubmission(sub: Submission) {
  if (sub.formType === 'standard') {
    // TypeScript KNOWS sub has actionable, lsqLink, etc.
    // sub.entity would cause TypeScript ERROR! ✓
    return <div>{sub.actionable} - {sub.lsqLink}</div>;
  } else {
    // TypeScript KNOWS sub has entity, issueType, etc.
    // sub.lsqLink would cause TypeScript ERROR! ✓
    return <div>{sub.entity} - {sub.issueType}</div>;
  }
}
```

**For backward compatibility**, create migration:

```typescript
// Migrate old submissions to new structure
function migrateSubmission(old: any): Submission {
  // Detect form type from available fields
  const formType = old.formType || (old.entity ? 'loan_issue' : 'standard');

  if (formType === 'loan_issue') {
    return {
      id: old.id,
      formType: 'loan_issue',
      entity: old.entity!,  // Force non-null after migration
      issueType: old.issueType!,
      // ... all required fields
      submittedBy: old.submittedBy,
      attachments: old.attachments || [],
    } as LoanIssueSubmission;
  } else {
    return {
      id: old.id,
      formType: 'standard',
      actionable: old.actionable!,
      lsqLink: old.lsqLink!,
      attachments: old.attachments || [],
      submittedBy: old.submittedBy,
    } as StandardSubmission;
  }
}

// On fetch, always migrate
const rawSubmission = await getSubmissionFromDB(id);
const typeSafeSubmission = migrateSubmission(rawSubmission);
```

**Detection Method**:
- Analyze interfaces: flag if same interface has optional fields that are conditionally required
- Find all `?:` fields: if used with string literals like `if (obj.type === 'X')`, it's a discriminated union pattern
- Runtime checks: if code does `if (obj.discriminator === 'X') { doSomething(obj.conditionalField); }` where field is optional, flag
- Check queries: if fetching Submissions and some don't have attachmentUrl, flag inconsistent schema

**Prevention Rule**:
```
RULE: Use discriminated unions, never loose optional fields
- One interface = one shape
- Different shapes = separate interface with discriminator
- All required fields must be non-optional
- No optional field should be accessed without runtime guard
- Add type guards at query boundaries:
  - Firestore fetch → migrate + validate
  - API response → zod.parse()
  - Local storage → restore + validate
- Zero trust runtime data: always validate before using
```

---

### Pattern 5.2: Any Types Creating Silent Bugs

**Severity**: HIGH
**Real Example**:

Project 2 (`/src/hooks/useTickets.ts` lines 56):
```typescript
const result = data as { success?: boolean; error?: string };

if (!result?.success) {
  const errorMsg = result?.error || 'Unknown sync error';
  return { success: false, error: errorMsg };
}
```

Here they cast `data` (unknown type from async function call) to a specific type. But:

1. **No runtime validation**: `data` could be anything. What if API returns `{ error: 123 }`? TypeScript thinks `errorMsg` is string but it's a number.

2. **Missing properties**: What if API adds a new field in the future? TypeScript won't complain.

3. **Type widening in catch blocks**:
   ```typescript
   } catch (err) {
     const errorMsg = err instanceof Error ? err.message : String(err);
     return { success: false, error: `Network error: ${errorMsg}` };
   }
   ```
   Here `err` is `unknown`. They check `instanceof Error` but what if err is thrown as a string (`throw 'oops'`)? Works but not type-safe.

Project 1 (`/src/types/index.ts` line 20):
```typescript
export interface Submission {
  // ...
  reason?: string;  // ← What's this? Unclear
  nextSteps?: string[];  // ← Array or CSV string? Unclear
}
```

No type documentation. A developer might store `nextSteps` as JSON string instead of array, and code breaks at runtime.

**What Should Have Happened**:

Use Zod for runtime validation:

```typescript
// src/lib/api.ts
import { z } from 'zod';

// Define exact shape expected from API
const SyncToSheetsResponseSchema = z.object({
  success: z.boolean(),
  error: z.string().optional(),
});

type SyncToSheetsResponse = z.infer<typeof SyncToSheetsResponseSchema>;

export async function syncToSheets(
  ticket: Ticket,
  operation: 'append' | 'update'
): Promise<SyncToSheetsResponse> {
  try {
    const response = await supabase.functions.invoke('sync-to-sheets', {
      body: { ticket_number: ticket.ticket_number, operation },
    });

    // VALIDATE at runtime before using
    const validated = SyncToSheetsResponseSchema.parse(response.data);
    return validated;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    throw new Error(`Sync failed: ${errorMsg}`);
  }
}

// Usage: Now TypeScript AND runtime know the shape
const result = await syncToSheets(ticket, 'update');
if (!result.success) {
  console.log(result.error);  // TypeScript knows it's string | undefined
}
```

For submissions:

```typescript
// src/types/submissions.ts
import { z } from 'zod';

export const SubmissionSchema = z.object({
  id: z.string(),
  actionable: z.string(),
  nextSteps: z.array(z.string()),  // ← Now TypeScript KNOWS it's array of strings
  reason: z.string().describe('Why this action was taken'),  // ← Documented
  // ...
});

export type Submission = z.infer<typeof SubmissionSchema>;

// Use in queries:
const rawSubmission = await db.getSubmission(id);
const validSubmission = SubmissionSchema.parse(rawSubmission);
// Now TypeScript guarantees nextSteps is string[], never string
```

**Detection Method**:
- Find all `as Type` casts: flag as potential type erasure
- Find all `any` types: ban them
- Find all `unknown` types without subsequent validation: flag
- Runtime validators: check if API responses are validated with Zod/Superstruct before use

**Prevention Rule**:
```
RULE: No unvalidated data from external sources
- All API responses must be validated with Zod before use
- All data from localStorage/sessionStorage must be validated
- All data from user input (form) must be validated
- No `as Type` casts (use `Type.parse()` instead)
- No `any` types (use `unknown` + validation)
- Every function returning unknown/untrusted data must document what can throw
```

---

## CATEGORY 6: State Management Fragmentation

### Pattern 6.1: Multiple State Management Patterns in Same App

**Severity**: HIGH
**Real Example**:

Project 2 uses THREE different state management patterns:

1. **Context API** (AuthContext):
   ```typescript
   // src/context/AuthContext.tsx
   interface AuthContextType {
     currentUser: User | null;
     loading: boolean;
     authError: string | null;
   }
   ```

2. **Custom Hooks** (useTickets):
   ```typescript
   // src/hooks/useTickets.ts
   export function useTickets() {
     const [tickets, setTickets] = useState<Ticket[]>([]);
     const fetchOpenTickets = useCallback(async (page = 0) => {
       // Fetches and updates state
     }, []);
   }
   ```

3. **Component State** (ProductSupportView):
   ```typescript
   // src/pages/ProductSupportView.tsx
   const [submittedTickets, setSubmittedTickets] = useState<Ticket[]>([]);
   const [claimedTickets, setClaimedTickets] = useState<Ticket[]>([]);
   const [resolvedTickets, setResolvedTickets] = useState<Ticket[]>([]);
   ```

**Where It Breaks**:

1. **State duplication**:
   - `AuthContext` has `currentUser`
   - `useTickets` hook also knows the current user (passed as parameter)
   - Component also accesses `currentUser` from context
   - Result: Two sources of truth for user info

2. **Sync challenges**:
   - `useTickets` subscribes to realtime updates from Supabase
   - Component also fetches separately in useEffect
   - Both update independent state
   - User sees inconsistent data between component and hook

3. **Prop drilling vs Context confusion**:
   - AuthContext passed via Context API (no props)
   - Tickets passed as hook return value (props implicitly)
   - New developer doesn't know which to use for new features

4. **Real bug from EDGE_CASES.md**:
   ```markdown
   ### 5. Realtime Subscription Issues
   - No error handler: Connection failures = silent data staleness
   - No row-level filtering: All users see all activity
   - Hardcoded channel name: HMR/re-mounts create conflicting subscriptions
   ```

   This happens BECAUSE state management is fragmented:
   ```typescript
   // useTickets.ts creates subscription
   export function useTickets() {
     const [tickets, setTickets] = useState<Ticket[]>([]);

     // Subscribes with hardcoded channel name
     useEffect(() => {
       const subscription = supabase
         .channel('tickets-changes')  // ← Hardcoded!
         .on(
           'postgres_changes',
           { event: '*', schema: 'public', table: 'tickets' },
           () => fetchAllTickets()  // ← Full refetch on ANY change
         )
         .subscribe();
     }, []);
   }

   // But if component mounts twice (HMR), subscriptions conflict
   // And no one knows because error handler is missing
   ```

**What Should Have Happened**:

Consolidate state management into ONE pattern:

**Option 1: Context API for all data**:
```typescript
// src/context/AppContext.tsx
interface AppContextType {
  user: User | null;
  tickets: Ticket[];
  loading: boolean;
  error: string | null;
  fetchTickets: (filter?: string) => Promise<void>;
  claimTicket: (id: string) => Promise<void>;
  resolveTicket: (id: string, notes: string) => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Centralized data management
  const fetchTickets = useCallback(async (filter?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await supabase
        .from('tickets')
        .select('*')
        .filter(filter || 'status', 'eq', 'open');
      setTickets(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Single subscription, ONE place
    const unsub = supabase
      .channel(`tickets:${user?.id}`)  // Unique per user
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'tickets' },
        async (payload) => {
          console.log('Got update:', payload);
          await fetchTickets();  // Refetch when something changes
        }
      )
      .subscribe((status) => {
        if (status === 'CLOSED') {
          setError('Real-time connection lost');
        }
      });

    return () => {
      unsub?.unsubscribe();
    };
  }, [user?.id, fetchTickets]);

  return (
    <AppContext.Provider value={{ user, tickets, loading, error, fetchTickets, claimTicket, resolveTicket }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
```

Then components are simple:
```typescript
function TicketList() {
  const { tickets, loading, error } = useApp();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return tickets.map(t => <TicketCard key={t.id} ticket={t} />);
}
```

**Benefits**:
- Single source of truth for data
- Single subscription (no conflicts)
- Error handling in one place
- All data flows through same context

**Detection Method**:
- Count distinct state management patterns used: Context, hooks, component state
- If count >1, flag for consolidation
- Find duplicate state across files (user in 2+ places)
- Find competing subscriptions (2+ useEffect that fetch same data)

**Prevention Rule**:
```
RULE: Use ONE state management pattern app-wide
- Choose: Context API OR custom hooks OR Redux
- All data must flow through chosen pattern
- No duplicate state in multiple places
- Subscriptions centralized: one per data source
- Create custom hooks only for UI-specific state (form input, modal open/close)
- Data queries must go through single provider/hook
```

---

## CATEGORY 7: Route/Navigation Breakage

### Pattern 7.1: Role-Based Routes Without Proper Guards

**Severity**: CRITICAL
**Real Example**:

Project 1 (`/src/App.tsx` lines 17-87):
```typescript
function AppRoutes() {
  const { isAuthenticated, role } = useSimpleAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/submit"
        element={
          <ProtectedRoute allowedRoles={['sm']}>
            <Layout>
              <SubmitPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/loan-issue"
        element={
          <ProtectedRoute allowedRoles={['product_support']}>
            <Layout>
              <LoanIssueFormPage />
            </Layout>
          </ProtectedRoute>
        }
      />
      // ... more routes
    </Routes>
  );
}
```

**The Problems**:

1. **Silent failures**: If user access `/submit` with wrong role, what happens?
   - ProtectedRoute probably shows "Unauthorized" or redirects
   - But no one documents this behavior
   - Users get random redirects without explanation

2. **No fallback route**: Line 89-104 shows redirect logic:
   ```typescript
   <Route
     path="/"
     element={
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
     }
   />
   ```

   But what if `role` is undefined? The else-else-else hits `/submissions` even if user shouldn't access it!

3. **Dead routes**: If role 'tech_support_team' is defined in types but no route checks for it, `/submissions` is DEAD for that role:
   ```typescript
   <Route
     path="/submissions"
     element={
       <ProtectedRoute allowedRoles={['sm', 'tech_support_team']}>  // ← tech_support_team here
         <Layout>
           <SubmissionsListPage />
         </Layout>
       </ProtectedRoute>
     }
   />
   ```

   But if user logs in as 'tech_support_team', they get routed to `/submissions` by default. Circular reference!

4. **No loading state during auth check**:
   - `isAuthenticated` is from context
   - Context might still be loading
   - Routes render immediately, showing wrong page briefly (flash of content)

**What Should Have Happened**:

```typescript
// src/types/routes.ts
import { UserRole } from './roles';

interface RouteConfig {
  path: string;
  label: string;
  allowedRoles: UserRole[];
  component: React.ComponentType;
  exact?: boolean;
}

export const ROUTE_CONFIG: RouteConfig[] = [
  {
    path: '/submit',
    label: 'Submit',
    allowedRoles: [UserRole.PRODUCT_SUPPORT],
    component: SubmitPage,
  },
  {
    path: '/admin',
    label: 'Admin',
    allowedRoles: [UserRole.ADMIN],
    component: AdminPanel,
  },
  {
    path: '/submissions',
    label: 'Submissions',
    allowedRoles: [UserRole.TECH_SUPPORT],
    component: SubmissionsListPage,
  },
];

// src/components/RouterProvider.tsx
export function RouterProvider() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;  // Explicit loading state
  }

  if (!user) {
    return <Routes>
      <Route path="*" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
    </Routes>;
  }

  return (
    <Routes>
      {ROUTE_CONFIG.map(route => {
        const canAccess = route.allowedRoles.includes(user.role);

        return (
          <Route
            key={route.path}
            path={route.path}
            element={
              canAccess ? (
                <Layout>
                  <route.component />
                </Layout>
              ) : (
                <UnauthorizedPage role={user.role} attemptedPath={route.path} />
              )
            }
          />
        );
      })}

      {/* Default: route to first accessible route */}
      <Route
        path="/"
        element={
          <Navigate
            to={ROUTE_CONFIG.find(r => r.allowedRoles.includes(user.role))?.path || '/unauthorized'}
            replace
          />
        }
      />

      {/* Explicit 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
```

**Benefits**:
- Routes defined in ONE place
- No dead routes (all routes check roles)
- Explicit loading state (no flash)
- Clear default route logic
- Easy to add new routes without checking N places

**Detection Method**:
- Extract all routes and their role checks
- Build a matrix: Role × Route
- Flag if role used in types but no route checks for it (dead code)
- Flag if route checks a role that doesn't exist in types (inconsistency)
- Flag routes with no explicit guard (should fail fast)

**Prevention Rule**:
```
RULE: Centralize all routes and permission checks
- All routes must be defined in src/types/routes.ts
- Each route specifies allowedRoles array
- All TypeScript role values must appear in at least one route
- Roles used in routes must be defined in types/roles.ts
- Default route calculated from ROUTE_CONFIG, not hardcoded
- Every route MUST have explicit ProtectedRoute or public=true
- Add loading state to prevent flash of wrong content
```

---

## CATEGORY 8: Form Logic Fragmentation

### Pattern 8.1: Duplicated Form Validation Across Components

**Severity**: HIGH
**Real Example**: (Already covered in Pattern 1.2: Duplicated Form Validation Logic)

---

### Pattern 8.2: Different Form Error Handling Strategies

**Severity**: MEDIUM
**Real Example**:

SubmitPage.tsx error handling (lines 169-174):
```typescript
try {
  const submissionId = await createSubmission(
    formData,
    role,
    (progress) => setUploadProgress(progress)
  );
  setSuccess({ submissionId });
  toast.success(`Submission ${submissionId} created successfully!`);
} catch (error) {
  toast.error(error instanceof Error ? error.message : 'Failed to create submission');
}
```

LoanIssueFormPage.tsx error handling (lines 313-314):
```typescript
} catch (error) {
  toast.error(error instanceof Error ? error.message : 'Failed to create submission');
}
```

**Identical error handling** but let's look at form validation errors:

SubmitPage.tsx validation (lines 137-156):
```typescript
if (!formData.actionable) {
  toast.error('Please select an actionable');
  return;
}
// ... 10+ more if-statements, each `return`ing on error
```

But LoanIssueFormPage.tsx validation (lines 273-294):
```typescript
if (!formData.entity) { toast.error('Please select an entity'); return; }
if (!formData.issueType) { toast.error('Please select an issue type'); return; }
```

**The Problems**:

1. **Validation errors stop at first error** in both, but:
   - User sees one error, fixes it, re-submit, sees next error
   - Instead of seeing all 5 errors at once
   - Bad UX

2. **Toast errors scroll off screen**:
   - Multiple errors generated → multiple toasts pile up
   - User can't see them all
   - No persistent error display

3. **No form error state**:
   - Errors are only in toasts (transient)
   - No way to style fields red to show which failed
   - User can't tell which field is wrong

4. **Copy-paste inconsistency**:
   - Error messages differ: "Please select..." vs "Please provide..."
   - Some messages are helpful ("Format: IDEP..."), some aren't

**What Should Have Happened**:

```typescript
// src/lib/formValidation.ts
import { z } from 'zod';

export const SubmissionSchema = z.object({
  actionable: z.string().min(1, 'Actionable is required'),
  detailedActionable: z.string().min(1, 'Detailed actionable is required'),
  lsqLink: z.string().url('Must be a valid URL'),
  urn: z.string().min(1, 'URN is required'),
});

export const LoanIssueSchema = z.object({
  entity: z.enum(['Applicant', 'Co-applicant'], { message: 'Entity is required' }),
  issueType: z.string().min(1, 'Issue type is required'),
  // ... etc
});

export type ValidationError = Record<string, string>;  // fieldName → errorMessage

export function validateForm<T>(data: T, schema: z.ZodSchema): {
  success: boolean;
  errors?: ValidationError;
} {
  try {
    schema.parse(data);
    return { success: true };
  } catch (err) {
    if (err instanceof z.ZodError) {
      const errors: ValidationError = {};
      err.errors.forEach(error => {
        const field = error.path.join('.');
        errors[field] = error.message;
      });
      return { success: false, errors };
    }
    return { success: false, errors: { root: 'Validation failed' } };
  }
}

// src/components/FormField.tsx
interface FormFieldProps {
  name: string;
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;  // From validation result
  required?: boolean;
}

export function FormField({
  name,
  label,
  value,
  onChange,
  error,
  required,
}: FormFieldProps) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium">
        {label}
        {required && <span className="text-red-500">*</span>}
      </label>
      <input
        name={name}
        value={value}
        onChange={onChange}
        className={`
          px-3 py-2 border rounded-md
          ${error ? 'border-red-500 bg-red-50' : 'border-gray-300'}
        `}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}

// src/pages/SubmitPage.tsx
export default function SubmitPage() {
  const [formData, setFormData] = useState<SubmissionFormData>({...});
  const [validationErrors, setValidationErrors] = useState<ValidationError>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate ENTIRE form at once
    const { success, errors } = validateForm(formData, SubmissionSchema);

    if (!success) {
      setValidationErrors(errors || {});
      return;  // Don't submit, show all errors at once
    }

    // Clear errors if valid
    setValidationErrors({});

    // Submit...
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <FormField
        name="actionable"
        label="Actionable"
        value={formData.actionable}
        onChange={handleInputChange}
        error={validationErrors.actionable}
        required
      />

      <FormField
        name="lsqLink"
        label="LSQ Link"
        value={formData.lsqLink}
        onChange={handleInputChange}
        error={validationErrors.lsqLink}
        required
      />

      {/* All errors shown at once, fields highlighted red */}
    </form>
  );
}
```

**Benefits**:
- All validation errors shown at once
- Consistent error messages via Zod
- Fields highlighted red
- Easy to add validation rules (Zod schema)
- Same UX across all forms

**Detection Method**:
- Find all toast.error calls in form submissions
- If >1 per form, flag as fragmented error handling
- Check if validation errors are transient (toasts) or persistent (state)
- Flag if error messages are hardcoded strings (should be in schema)

**Prevention Rule**:
```
RULE: All form validation must be centralized and persist errors
- All form schemas defined in src/lib/formValidation.ts
- All validation via Zod (with error messages)
- Validation errors stored in state, not toasts
- Validation runs on entire form, shows all errors at once
- Error messages defined in schema, not components
- Each field displays its error inline
```

---

## CATEGORY 9: Database Schema Drift

### Pattern 9.1: Application Logic Assumes Schema Version Without Checking

**Severity**: CRITICAL
**Real Example**:

Project 1 has backward compatibility mess:

File: `/src/types/index.ts` lines 20-22:
```typescript
attachmentUrl?: string; // DEPRECATED: Google Drive shareable URL (kept for backward compatibility)
attachmentDriveId?: string; // DEPRECATED: Google Drive file ID (kept for backward compatibility)
attachments?: Attachment[]; // Array of attachments (multiple files support)
```

Code assumes OLD submissions have `attachmentUrl`, NEW have `attachments`:

File: `/src/lib/submissions.ts` lines 98-102:
```typescript
// Set first file as legacy fields for backward compatibility
if (i === 0) {
  attachmentUrl = uploadResult.shareableUrl;
  attachmentDriveId = uploadResult.fileId;
}
```

But what happens when:
1. Old submission migrated from `attachmentUrl` to `attachments`?
2. Both fields exist on same document?
3. Code doesn't know which to use?

**The Cascade**:

When displaying a submission, code must handle:
```typescript
if (submission.attachments && submission.attachments.length > 0) {
  // New format
} else if (submission.attachmentUrl) {
  // Old format
}
```

But if BOTH exist (partially migrated), which takes precedence? Undefined behavior = bugs.

Project 2 has migration files:

File listing:
```
migrations/001_add_google_sheets_fields.sql
migrations/009_storage_authenticated_upload.sql
migrations/015_optimize_rls_performance.sql
```

**The Problem**: 31 migrations with no versioning. If deploying to production and migration 12 fails, is the app in state of migration 11 or 12?

File: `/README.md` line 160-162:
```
3. **Google Sheets integration:** Run the migration that adds the extra columns:
   Copy the contents of **`migrations/001_add_google_sheets_fields.sql`** into the SQL Editor and run it.
```

Manual migration steps = human error. No way to know which migrations have been applied.

**What Should Have Happened**:

Implement schema versioning:

```typescript
// src/db/migrations/index.ts
interface Migration {
  version: number;
  name: string;
  up: (db: Database) => Promise<void>;
  down: (db: Database) => Promise<void>;  // Rollback support
}

export const MIGRATIONS: Migration[] = [
  {
    version: 1,
    name: 'initial_schema',
    up: async (db) => {
      await db.raw(`CREATE TABLE submissions (...)`);
    },
    down: async (db) => {
      await db.raw(`DROP TABLE submissions`);
    },
  },
  {
    version: 2,
    name: 'add_loan_issue_fields',
    up: async (db) => {
      await db.raw(`ALTER TABLE submissions ADD COLUMN entity VARCHAR(50)`);
    },
    down: async (db) => {
      await db.raw(`ALTER TABLE submissions DROP COLUMN entity`);
    },
  },
];

// src/db/migrator.ts
export async function runMigrations(db: Database) {
  // Get current version from DB
  const result = await db.raw(
    `SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1`
  );
  const currentVersion = result.rows[0]?.version ?? 0;

  // Run all pending migrations
  for (const migration of MIGRATIONS) {
    if (migration.version > currentVersion) {
      console.log(`Applying migration ${migration.version}: ${migration.name}`);
      await migration.up(db);
      await db.raw(
        `INSERT INTO schema_version (version, name, applied_at) VALUES (?, ?, NOW())`,
        [migration.version, migration.name]
      );
    }
  }
}

// In app startup:
async function main() {
  const db = await initDatabase();
  await runMigrations(db);  // Automatic, idempotent
  // Now app can trust schema is in correct state
}
```

And in code, trust the schema:
```typescript
// No more "if old format, else new format" checks
// Migrations ensure all submissions have 'attachments' array

export function getAttachments(submission: Submission): Attachment[] {
  // After migration, always exists, never null
  return submission.attachments;
}
```

**Detection Method**:
- Scan code for version checks (`if (obj.version === 1)` or legacy format checks)
- Look for commented-out/deprecated fields
- Find manual migration instructions in README (should be automated)
- Check if schema_version table/tracking exists

**Prevention Rule**:
```
RULE: Schema changes must be tracked and automatic
- Create migrations/ directory with numbered files (001_, 002_, etc)
- Each migration must have up() and down()
- Track applied migrations in database (schema_version table)
- Never manually run SQL—use migration runner
- Migrations must be idempotent (can run multiple times)
- No deprecated fields—migrate data in migration, not code
- Deploy always runs pending migrations automatically
```

---

## CATEGORY 10: Testing and Verification Gaps

### Pattern 10.1: No Component/Integration Tests Leads to Silent Regressions

**Severity**: HIGH
**Real Example**:

Project 1 has NO tests visible in the codebase. Zero.

Project 2 has minimal tests:
- `/src/types/__tests__/index.test.ts` (testing type utilities)
- `/src/utils/__tests__/time.test.ts` (testing time utils)
- `/src/utils/__tests__/imageUpload.test.ts` (testing image compression)

But MISSING tests for:
- Form components (TicketForm.tsx)
- Hooks (useTickets.ts)
- Pages (AdminView.tsx, ProductSupportView.tsx)
- Integrations (Supabase, Google Sheets sync)

**The Impact**:

From EDGE_CASES.md line 154:
```
| 5 | Realtime issues (3) | MEDIUM | No | UNFIXED |
```

This includes:
1. No error handler on realtime subscription
2. No row-level filtering
3. Hardcoded channel names creating conflicts

All UNFIXED. Why? Because there are NO TESTS for useTickets.ts. If there were:

```typescript
// src/hooks/__tests__/useTickets.test.ts
describe('useTickets', () => {
  it('should handle realtime subscription errors', async () => {
    const { result } = renderHook(() => useTickets(), {
      wrapper: SupabaseProvider,
    });

    // Simulate subscription error
    mockSupabase.channel.subscribe.mockImplementation(
      (callback) => {
        callback({ status: 'CLOSED' });  // Connection closed
      }
    );

    await waitFor(() => {
      expect(result.current.error).toContain('connection lost');
    });
  });

  it('should not create duplicate subscriptions on re-mount', () => {
    const { rerender } = renderHook(() => useTickets());

    const subscribeCall1 = mockSupabase.channel.subscribe.mock.calls.length;
    rerender();
    const subscribeCall2 = mockSupabase.channel.subscribe.mock.calls.length;

    // If subscriptions are properly cleaned up, calls should be same
    expect(subscribeCall2).toBe(subscribeCall1);
  });
});
```

This test would FAIL and expose the bug. Without tests, the bug remains hidden until production.

**Detection Method**:
- Count test files vs source files ratio
- If <20% of files have tests, flag as insufficient coverage
- Find components/hooks with no tests (should have tests for side effects)
- Look for `.skip()` or `.todo()` in tests (incomplete)

**Prevention Rule**:
```
RULE: Critical code paths must have integration tests
- Forms (especially validation) must have tests
- Hooks that do side effects (subscriptions, fetches) must have tests
- Database integrations must have tests
- Minimum coverage thresholds:
  - Business logic: 80%
  - Components: 60%
  - Utils: 90%
- Every EDGE_CASES.md entry must have a failing test before fix
- Pre-commit hook rejects commits that decrease coverage
```

---

## Prevention Rules Summary

### Architecture Level

```
RULE SET A: Component Organization
1. No copy-pasted functions across components
2. All UI components must encapsulate styling
3. All spacing/colors/typography must use design tokens
4. Extract form handling into reusable components

RULE SET B: Type Safety
5. All roles must use TypeScript enum
6. All data from external sources must be validated with Zod
7. Use discriminated unions for conditional types
8. No `any` types, no `as Type` casts

RULE SET C: State Management
9. Use ONE state management pattern app-wide
10. All data must flow through centralized provider/hook
11. Centralize all permissions in single model

RULE SET D: Database
12. Use single storage backend per app
13. Schema changes tracked automatically via migrations
14. No deprecated fields, migrate in migration layer

RULE SET E: Testing
15. Critical code paths must have integration tests
16. No EDGE_CASES.md item without failing test before fix
```

---

## Conclusion

These failure patterns emerge not from inherent flaws in the technologies used (React, Firebase, Supabase), but from:

1. **Inconsistent abstractions**: Components solving same problem differently
2. **Missing validation**: Data trusted without runtime verification
3. **Scattered logic**: Permissions, routes, validation spread across files
4. **Silent failures**: Errors not surfaced, regressions not caught
5. **Complexity accumulation**: Services stacked without clear boundaries

The prevention rules create a foundation where new features can be added safely. Each rule reduces the cognitive load on developers and creates natural enforcement points (TypeScript, linting, testing).

When Claude (or any AI) adds features to existing codebases, these rules should be the guardrails that prevent the fragmentation that broke Projects 1 and 2.
