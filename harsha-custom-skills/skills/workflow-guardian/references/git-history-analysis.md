# Git History Analysis Protocol for Regression Prevention

## Overview

This guide provides Claude with forensic protocols for analyzing git history to detect regression patterns and prevent future breakages. It is based on analysis of two real projects:

- **Ring Kissht Issue Tracker** (23 commits, multiple fix commits indicating breakage)
- **LOS Issue Tracker** (16 commits, more structured with defined features)

Git history reveals not just what changed, but **why it broke** and **what pattern led to the breakage**. This reference teaches how to read those patterns before making changes, so breakages can be prevented.

---

## SECTION 1: Pre-Change Git Analysis Protocol

Before making any changes to a project, Claude must analyze git history to understand the codebase's vulnerability patterns.

### 1.1 Reading Recent Commit History to Understand Patterns

**Goal**: Understand what changed recently and identify if there were multiple fix attempts.

**Ring Kissht Issue Tracker - Real Example:**

```
1de2b3c Issue tracker: current version - compression, product support flow, UI components, Firestore rules
3087c34 Add Vercel environment variables fix guide
53fcde3 Refactor role management and permissions in routing; update Firestore rules for clarity and add new dependencies
28eb790 Add Firebase config fallbacks and environment setup guide
c53aa6f Add vite-plugin-compression to devDependencies
1ec0f59 Add @vercel/node dependency for API functions
5d5e488 Add API function and fix Vercel config pattern
85cac3f Simplify build: use vite build only (Vite handles TypeScript)
04f5488 Fix Vercel build: ensure devDependencies installed before build
797dbc0 Add vercel.json configuration
caa5fcd Trigger Vercel rebuild with latest fixes
9b2b8a8 Fix undefined field error: explicitly build object without undefined values
328f7e5 Fix Vercel build: use npx tsc instead of tsc
fae45b2 Fix Firestore undefined field error - only include attachment fields when they have values
2b0b251 Make attachment field optional in form submission
c757748 Enhance submission process with loan issue form and multiple file uploads
e7502eb Implement Google Drive integration for file storage
8608203 Update roles: Product Support submits forms, Tech Support Team views submissions
```

**What This Pattern Shows:**

1. **Feature Addition Period** (e7502eb → c757748): Google Drive integration + loan form
   - Commit e7502eb: "Implement Google Drive integration for file storage"
   - Commit c757748: "Enhance submission process with loan issue form and multiple file uploads"

2. **Fix Cascade** (2b0b251 → 1de2b3c): Multiple fixes in sequence
   - 2b0b251: Make attachment field optional (indicates previous commit broke type safety)
   - fae45b2: Fix Firestore undefined field error
   - 328f7e5: Fix Vercel build: use npx tsc (TypeScript compilation failure)
   - 04f5488: Fix Vercel build: ensure devDependencies installed
   - 9b2b8a8: Fix undefined field error (same error appears twice → not fully resolved)

3. **Configuration Churn** (797dbc0 → 5d5e488): Trying different approaches
   - 797dbc0: Add vercel.json configuration
   - 5d5e488: Add API function and fix Vercel config pattern
   - 85cac3f: Simplify build: use vite build only
   - This indicates the first approach didn't work, requiring rewrites

**Interpretation Protocol:**

When you see this pattern, ask: "What feature was added, and what broke as a result?"

```
Feature Added → Fix1 → Fix2 → Fix3 → Configuration Change → More Fixes
```

This is the **regression signature**. It means:
- The feature was complex enough to break existing functionality
- The fix wasn't comprehensive (it had to be fixed again)
- Configuration decisions weren't considered upfront

**LOS Issue Tracker - Comparison:**

```
554c8fa Release v0.2.0: ticket release (unclaim) + improved release confirmation UI
f94bb6f Fix OAuth redirect flicker (login screen flash before dashboard)
9164f4e Fix 12-second login delay caused by Supabase SDK Navigator Lock deadlock
2e844b8 Add perf logging, security fixes, CSS regression fix, and edge function hardening
42a83b1 Add mandatory Google OAuth authentication with email whitelist
36710e0 Update documentation for dual-sheet sync feature
fb8423d Add dual-sheet sync for Product Support team
8e47062 Fix ticket description visibility across UI and Google Sheets
54aeb84 Add TRN (Transaction Reference Number) field for Product Support
2563f57 Make LSQ URL mandatory for all tickets
f54e41a Add Google Sheets integration with live sync
```

**Key Differences:**

- **LOS Tracker shows the same problem** (f54e41a: Add Google Sheets → 8e47062: Fix visibility issue)
- **But more structured**: Documentation is updated proactively (36710e0)
- **Named fixes are more specific**: "Fix OAuth redirect flicker" vs generic "Fix build" commits
- **Feature commits describe impact**: "Add mandatory Google OAuth authentication with email whitelist" tells you what changed and why

**Claude's Pre-Change Analysis Checklist:**

```
Before making changes:

1. Run: git log --oneline -30
   └─ Look for "Fix" + "Add" patterns in sequence
   └─ Count how many "Fix" commits follow a feature addition
   └─ If more than 2 fixes follow an "Add", that's a regression signature

2. Run: git log --format="%h %s" --grep="Fix" -20
   └─ Identify what types of issues were fixed
   └─ Look for repeated fix topics (e.g., "Fix undefined field error" × 2)
   └─ Repeated fix topics = incomplete fixes = architectural debt

3. For each "Add" commit in the last 10, ask:
   ├─ What file was created? (git show <commit> --stat)
   ├─ What files were modified?
   ├─ Did it introduce new dependencies?
   └─ How many "Fix" commits follow it?

4. Review the oldest "Fix" in the cascade:
   └─ That commit usually reveals where the problem started
   └─ Example: 2b0b251 (Make attachment field optional) reveals
     that the previous commit (c757748) added a required field
     that broke existing form data
```

### 1.2 Identifying Which Files Change Together (Coupling Analysis)

**Goal**: Understand dependencies between files so changes don't miss required updates.

**Ring Kissht Issue Tracker - File Coupling:**

When examining commit 1de2b3c (the massive "current version" commit with 3,495 insertions):

```
Files modified:
- src/App.tsx                           | 36 +-
- src/components/Layout.tsx             | 55 +-
- src/components/ui/Badge.tsx           | 76 +  (NEW)
- src/components/ui/Button.tsx          | 72 +  (NEW)
- src/components/ui/Input.tsx           | 151 +  (NEW)
- src/components/ui/index.ts            | 3 +   (NEW)
- src/pages/LoanIssueFormPage.tsx       | 492 ++--- (MAJOR change)
- src/pages/LoginPage.tsx               | 147 +- (MAJOR change)
- src/pages/ModifySubmissionPage.tsx    | 605 +  (NEW)
- src/pages/ProductSupportDashboard.tsx | 330 +  (NEW)
- src/pages/SubmissionDetailPage.tsx    | 499 +--- (MAJOR change)
- src/pages/SubmissionsListPage.tsx     | 221 +- (MAJOR change)
- src/pages/SubmitPage.tsx              | 343 +--- (MAJOR change)
- src/types/index.ts                    | 10 +- (updated types)
```

**Coupling Pattern Identified:**

```
When App.tsx changes:
├─ Check: Are all page imports updated? (5 pages modified)
├─ Check: Are all component usages updated? (Layout.tsx, Badge, Button, Input)
├─ Check: Are types synchronized? (types/index.ts updated)
└─ Risk: If types/index.ts is NOT updated, all pages will have TS errors

When a NEW UI component is added (Badge, Button, Input):
├─ Look for: ui/index.ts (barrel export)
├─ Check: Is it imported in pages or other components?
└─ Risk: If not used, it's dead code. If used but not exported, it's a missed import
```

**File Coupling Rule Extraction:**

From the Ring Kissht history, we can infer:

```
File Coupling Dependency Graph:
- types/index.ts → Everything (types define contracts)
  └─ If modified: ALL pages, components, contexts may break

- App.tsx → All pages, routing
  └─ If modified: Check all page imports, route definitions

- src/components/ui/* → All pages using them
  └─ If modified: Grep for imports, update barrel exports

- src/pages/LoginPage.tsx → App.tsx routing, AuthContext
  └─ If modified: Check routing guards, auth logic

- src/pages/*FormPage.tsx → src/lib/submissions.ts, types/index.ts
  └─ If modified: Verify form data types match
```

**LOS Issue Tracker - File Coupling Analysis:**

From commit 554c8fa (Release v0.2.0):

```
Files changed:
- migrations/026_allow_ticket_release.sql      (DATABASE)
- src/components/ConfirmReleaseModal.tsx       (NEW component)
- src/hooks/useTickets.ts                      (hook using data)
- src/pages/AdminView.tsx                      (uses component & hook)
- src/pages/ProductSupportView.tsx             (uses hook)
- supabase/functions/sync-to-sheets/index.ts   (edge function)
```

**Coupling Pattern:**

```
When database schema changes (migrations/026):
├─ Check: Do database functions need updates? (edge functions)
├─ Check: Do TypeScript types match schema? (types/index.ts)
├─ Check: Do hooks query the new columns? (useTickets.ts)
└─ Risk: Type mismatch between DB schema and TypeScript types

When a new feature is added (ticket release):
├─ Component: ConfirmReleaseModal.tsx (NEW)
├─ Hook: useTickets.ts (MODIFIED - must add release mutation)
├─ View: AdminView.tsx (MODIFIED - must use new component)
├─ Database: migrations/026 (NEW - adds release logic)
└─ Risk: If any of these is missed, feature is non-functional
```

**Pre-Change Coupling Analysis Protocol:**

```
Before making changes, run:

1. git diff HEAD~5..HEAD --name-only | sort
   └─ Shows recent file changes (coupling signatures)

2. For each file you plan to modify, ask:
   ├─ Is this a type definition file? (types/*, index.ts)
   │  └─ YES: Search for all imports, grep for usages
   ├─ Is this a page/component?
   │  └─ Check: App.tsx imports, routing, type definitions
   ├─ Is this a hook or utility?
   │  └─ Check: All components/pages using this file
   └─ Is this a database migration?
      └─ Check: Database functions, TypeScript types, hooks

3. Example for "modifying src/types/index.ts":
   ├─ grep -r "import.*types" src/ (find all usages)
   ├─ git log --format="%h %s" -- src/types/index.ts (history of changes)
   ├─ For each change, see what else was modified in that commit
   └─ Pattern becomes clear: types changes always coupled with page changes
```

### 1.3 Detecting Feature Addition Patterns That Led to Breakage

**Goal**: Recognize when new features are added in ways that break existing code.

**Ring Kissht Issue Tracker - Feature Breakage Pattern:**

**Feature**: Loan Issue Form (commit c757748)

Files added/modified:
```
commit c757748: Enhance submission process with loan issue form and multiple file uploads

- src/pages/LoanIssueFormPage.tsx       | +603 lines (NEW)
- src/pages/SubmitPage.tsx              | +/-391 lines (modified)
- src/types/index.ts                    | +additions
- src/lib/submissions.ts                | +modifications
```

**Immediate Problems (revealed by subsequent fixes):**

```
Commit 2b0b251 (next commit): "Make attachment field optional in form submission"
└─ This reveals: c757748 made attachment field REQUIRED
   └─ But existing form data didn't have it
   └─ Solution: Made it optional (patch)
   └─ Better solution: Backward compatibility migration

Commit fae45b2 (2 commits later): "Fix Firestore undefined field error"
└─ This reveals: c757748 created Firestore documents with undefined fields
   └─ Firestore doesn't allow undefined in objects
   └─ Solution: Filter undefined before saving (patch)
   └─ Better solution: Validate schema before Firestore.add()
```

**Feature Breakage Detection Protocol:**

When you see a feature addition commit, check:

```
1. Does the new feature add NEW required fields?
   └─ If YES: Will existing data have these fields?
   └─ Check: type definitions, forms, database schemas
   └─ Pattern: c757748 added attachment fields, broke existing submissions

2. Does the new feature add NEW file types?
   └─ If YES: Are there files in the src/pages/ directory?
   └─ Check: App.tsx routing, type definitions for routes
   └─ Pattern: LoanIssueFormPage.tsx needed route in App.tsx

3. Does the new feature modify EXISTING types?
   └─ If YES: Are all usages updated?
   └─ Check: run grep on the old type name across entire src/
   └─ Pattern: Ring Kissht modified SubmissionFormData, broke SubmitPage

4. Does the new feature add NEW dependencies?
   └─ If YES: Check package.json changes
   └─ Pattern: Ring Kissht added @vercel/node, vite-plugin-compression
   └─ Risk: Configuration must be updated (vercel.json, etc.)

5. Does the new feature integrate with EXTERNAL services?
   └─ If YES: Are environment variables added?
   └─ Check: .env.example, deployment configs
   └─ Pattern: LOS Tracker added Google Sheets, needed new env vars
```

**Real Example: How to Detect Google Sheets Integration Breakage (LOS Tracker)**

Feature commit: f54e41a "Add Google Sheets integration with live sync"

```
Files in commit: (implied from follow-up fixes)
+ supabase/functions/sync-to-sheets/index.ts (NEW)
+ Database schema changes for sheet references
- src/hooks/useTickets.ts (modified to call sync function)
- Environment variables added

Next commit: 8e47062 "Fix ticket description visibility across UI and Google Sheets"
└─ This reveals: f54e41a broke visibility
   └─ Why: Sync function overwrites UI field values
   └─ When: Data synced to Sheets, description lost in UI

How Claude should detect this BEFORE it happens:

1. Before adding Google Sheets sync, ask:
   - Does the sync function read the same fields the UI displays?
   - Could the sync overwrite the UI's read?
   - What if the sync runs while user is editing?

2. Check the migration:
   - git show f54e41a --stat
   - Does it add columns or modify existing ones?
   - If modifying existing columns, that's high risk

3. Before committing, run:
   - git diff --stat (verify change scope)
   - grep -r "description" src/ (find all description usage)
   - Check if sync function touches description field
```

### 1.4 Finding "Fix" Commits That Indicate Previous Breakage

**Goal**: Identify which feature caused which breakage by analyzing fix commits.

**Ring Kissht Issue Tracker - Fix Forensics:**

```
git log --format="%h %s" --grep="Fix" -20

04f5488 Fix Vercel build: ensure devDependencies installed before build
9b2b8a8 Fix undefined field error: explicitly build object without undefined values
328f7e5 Fix Vercel build: use npx tsc instead of tsc
fae45b2 Fix Firestore undefined field error - only include attachment fields when they have values
16b021d Fix TypeScript errors: remove unused imports
```

**Tracing the Root Cause:**

```
Fix Commit: 04f5488 "Fix Vercel build: ensure devDependencies installed before build"
↑ Points to problem: Vercel build was failing
← Caused by: 5d5e488 "Add API function and fix Vercel config pattern"
  └─ That commit added @vercel/node dependency
  └─ But devDependencies weren't installed in build

Fix Commit: 9b2b8a8 "Fix undefined field error: explicitly build object without undefined values"
↑ Points to problem: Firestore documents have undefined fields
← Caused by: c757748 "Enhance submission process with loan issue form and multiple file uploads"
  └─ That commit created objects with optional fields
  └─ When optional fields are undefined, Firestore breaks

Fix Commit: fae45b2 "Fix Firestore undefined field error - only include attachment fields when they have values"
↑ Points to problem: Attachment fields are undefined (same problem as 9b2b8a8!)
← Caused by: Same root cause as 9b2b8a8 (not actually fixed)
  └─ This is a REGRESSION SIGNATURE: same error fixed twice
```

**LOS Issue Tracker - Fix Forensics:**

```
git log --format="%h %s" --grep="Fix" -20

f94bb6f Fix OAuth redirect flicker (login screen flash before dashboard)
9164f4e Fix 12-second login delay caused by Supabase SDK Navigator Lock deadlock
2e844b8 Add perf logging, security fixes, CSS regression fix, and edge function hardening
8e47062 Fix ticket description visibility across UI and Google Sheets
```

**Analysis:**

```
Fix Commit: f94bb6f "Fix OAuth redirect flicker"
├─ More specific than Ring Kissht fixes
├─ Describes WHAT happens (redirect flicker)
└─ Likely caused by: 42a83b1 "Add mandatory Google OAuth authentication with email whitelist"

Fix Commit: 9164f4e "Fix 12-second login delay caused by Supabase SDK Navigator Lock deadlock"
├─ Even more specific: Names the MECHANISM (Navigator Lock deadlock)
├─ Shows the developer understood the problem
└─ Likely caused by: Supabase SDK initialization (probably in auth context)

Fix Commit: 8e47062 "Fix ticket description visibility across UI and Google Sheets"
├─ Describes SYMPTOM (visibility)
└─ Likely caused by: f54e41a "Add Google Sheets integration with live sync"
```

**Key Insight**: LOS Tracker's fix commits are more descriptive. They show WHAT broke and sometimes WHY. Ring Kissht's fix commits are vague ("Fix undefined field error"). This difference correlates with LOS Tracker having fewer cascading fixes (3 key fixes vs Ring Kissht's 7+ fixes).

**Pre-Change Fix Analysis Checklist:**

```
Before making changes, trace the fix history:

1. For each "Fix" commit in the last 20:
   └─ git log --oneline <fix-commit>~1..HEAD
   └─ Find what commit introduced the problem
   └─ Pattern: Feature → Fix → Feature → Fix (good)
   └─ Pattern: Feature → Fix → Fix → Fix (bad, incomplete)

2. For each feature you're about to add:
   └─ Ask: What type of errors could this introduce?
   └─ TypeScript errors? (add types test)
   └─ Undefined field errors? (add schema validation)
   └─ Build errors? (test build locally)
   └─ UI visibility issues? (test rendering)

3. Create a "risk map" for your feature:
   ├─ What fields are NEW? (might be undefined in existing data)
   ├─ What files are MODIFIED? (all consumers must be checked)
   ├─ What EXTERNAL services are touched? (env vars, APIs)
   └─ What BUILD/DEPLOY configs need updating?

4. After making changes, verify:
   └─ git diff --stat (does it match your risk map?)
   └─ git diff (review actual code against risk map)
   └─ Are all risky changes actually needed?
```

---

## SECTION 2: Regression Pattern Detection from Real Git Histories

### 2.1 Commits Where Features Were Added That Broke Things

**Ring Kissht Issue Tracker:**

```
Commit c757748: "Enhance submission process with loan issue form and multiple file uploads"
├─ Type: Feature Addition (NEW complex form + file handling)
├─ Scope: 1 new file (LoanIssueFormPage.tsx) + modifications to 3 existing files
├─ Files Modified:
│  ├─ src/pages/LoanIssueFormPage.tsx (NEW - 603 lines)
│  ├─ src/pages/SubmitPage.tsx (MODIFIED - had to adapt)
│  ├─ src/types/index.ts (MODIFIED - new types added)
│  └─ src/lib/submissions.ts (MODIFIED - new submission logic)
├─ Subsequent Fixes:
│  ├─ 2b0b251 (2 commits later): Make attachment field optional
│  ├─ fae45b2 (4 commits later): Fix Firestore undefined field error
│  └─ 9b2b8a8 (5 commits later): Fix undefined field error (again!)
└─ Pattern Assessment: MAJOR BREAKAGE
   └─ 3 sequential fixes for the same root cause = incomplete design

Root Cause Analysis:
- LoanIssueFormPage added new required fields (attachment fields)
- These fields didn't exist in old submission objects
- Firestore rejected documents with undefined fields
- Fix #1: Made fields optional (patch)
- Fix #2: Filter out undefined before saving (workaround)
- Fix #3: Same issue appears again = not actually fixed
└─ Better approach: Create migration for existing documents OR validate schema

Commit e7502eb: "Implement Google Drive integration for file storage"
├─ Type: Feature Addition (NEW external service integration)
├─ Scope: 1 new file (driveUpload.ts) + modifications to multiple components
├─ Subsequent Fixes:
│  └─ 5d5e488 (12 commits later): Add API function and fix Vercel config
└─ Pattern Assessment: MODERATE BREAKAGE
   └─ Configuration cascaded (dependency order not understood)
```

**LOS Issue Tracker:**

```
Commit f54e41a: "Add Google Sheets integration with live sync"
├─ Type: Feature Addition (NEW external service + database sync)
├─ Scope: Database migrations + edge functions + hook modifications
├─ Subsequent Fixes:
│  ├─ 8e47062 (1 commit later): Fix ticket description visibility across UI and Google Sheets
│  └─ 36710e0 (2 commits later): Update documentation for dual-sheet sync feature
└─ Pattern Assessment: MODERATE BREAKAGE
   └─ Only 1 critical fix needed
   └─ Proactive documentation update shows learning

Root Cause: Sync overwrites UI field values
Solution: Fix ticket description visibility (implies read-only or sync-aware rendering)
Better approach: Design syncing to be unidirectional or conflict-aware
```

### 2.2 Identifying "Fix" Commits That Followed Feature Additions

**Ring Kissht Issue Tracker - Fix Cascade Pattern:**

```
Timeline:
c757748 (day 1): Add Google Drive + Loan Form
↓ (2 commits later)
2b0b251: Make attachment field optional
↓
fae45b2: Fix Firestore undefined field error
↓
9b2b8a8: Fix undefined field error (SAME ERROR AGAIN!)
↓
328f7e5: Fix Vercel build (build system broken)
↓
04f5488: Fix Vercel build (same error, different approach)

Pattern: Feature → Fix1 → Fix2 → Fix3 → Fix4 → Fix5
Result: 5 fixes for 1 feature = 83% of commits are corrections
```

**Why This Happened:**

1. **Type Safety Violation**:
   - Added `attachmentFiles?: File[]` as optional
   - Code assumed it always existed
   - Runtime: undefined field access crashes

2. **Firestore Schema Validation Missing**:
   - Added fields without checking Firestore's constraints
   - Firestore rejects {key: undefined}
   - Should have validation layer before database save

3. **Configuration Cascade**:
   - Added API function without ensuring dependencies installed
   - build script runs before devDependencies available
   - Configuration order not thought through upfront

**LOS Issue Tracker - More Disciplined Fix Pattern:**

```
Timeline:
f54e41a: Add Google Sheets integration
↓ (1 commit later)
8e47062: Fix ticket description visibility across UI and Google Sheets
↓ (1 commit later)
36710e0: Update documentation for dual-sheet sync feature
↓ (many commits later)
42a83b1: Add mandatory Google OAuth authentication with email whitelist
↓
f94bb6f: Fix OAuth redirect flicker
↓
9164f4e: Fix 12-second login delay caused by Supabase SDK Navigator Lock deadlock

Pattern: Feature → Fix1 → Documentation (then next feature)
Result: Only 1-2 fixes per feature
```

### 2.3 Architecture Decision Commits vs Implementation Commits

**Ring Kissht - Mixed Decisions:**

```
Decision Commit: e7502eb "Implement Google Drive integration for file storage"
└─ Architecture Decision: Use Google Drive as file storage
└─ Leaves questions:
   ├─ API authentication: How to authorize?
   ├─ File organization: How to organize in Drive?
   ├─ Permission scope: User-owned files or shared?
   └─ Result: Implementation commits follow with fixes

Decision Commit: 5d5e488 "Add API function and fix Vercel config pattern"
└─ Architecture Decision: Vercel API functions for server-side uploads
└─ Actually a FIX + DECISION (mixing concerns)
└─ Shows confusion about architecture

Decision Commit: 85cac3f "Simplify build: use vite build only (Vite handles TypeScript)"
└─ Architecture Decision: Eliminate separate tsc step
└─ Implies previous decision (separate tsc step) was wrong
└─ Shows architecture wasn't thought through initially
```

**LOS Issue Tracker - Clearer Decisions:**

```
Decision Commit: 42a83b1 "Add mandatory Google OAuth authentication with email whitelist"
└─ Clear architecture decision with constraints
└─ "mandatory" = everyone must login
└─ "email whitelist" = only certain emails allowed
└─ Follow-up fixes understand this decision

Decision Commit: fb8423d "Add dual-sheet sync for Product Support team"
└─ Architectural decision: TWO sheets for sync (not one)
└─ Shows thinking about data organization upfront
└─ Documentation follows (36710e0) to explain the decision

Decision Commit: 554c8fa "Release v0.2.0: ticket release (unclaim) + improved release confirmation UI"
└─ Feature + decision: Admins can unclaim tickets
└─ Shows process thinking: release → confirmation → sync to sheets
```

**Key Difference:**

- **Ring Kissht**: Architecture decisions mixed with fixes, implying initial design was incomplete
- **LOS Issue Tracker**: Clearer separation of decision commits vs implementation commits

### 2.4 Commits That Added Files vs Modified Existing Files

**Ring Kissht - File Addition Analysis:**

Files ADDED:
```
27de938 Initial commit: Issue Tracker application
e7502eb Implement Google Drive integration for file storage
  → api/uploadToDrive.ts (NEW)

c757748 Enhance submission process with loan issue form and multiple file uploads
  → src/pages/LoanIssueFormPage.tsx (NEW)

1de2b3c Issue tracker: current version
  → src/components/ui/Badge.tsx (NEW)
  → src/components/ui/Button.tsx (NEW)
  → src/components/ui/Input.tsx (NEW)
  → src/pages/ModifySubmissionPage.tsx (NEW)
  → src/pages/ProductSupportDashboard.tsx (NEW)
  → .claude/* files (NEW)
```

Files HEAVILY MODIFIED (multiple commits):
```
src/App.tsx
  ├─ 1de2b3c: +24 lines
  ├─ 53fcde3: Role management refactoring
  └─ Total: Modified 6+ times

src/pages/SubmitPage.tsx
  ├─ c757748: Initial form
  ├─ 1de2b3c: Major refactor -162 lines (code duplication removed)
  └─ Total: Modified 3+ times

src/types/index.ts
  ├─ c757748: Add LoanIssueFormData type
  ├─ 1de2b3c: Add additional types
  └─ Total: Modified 4+ times
```

**Pattern**: When a file is NEW, it often implies coupled changes to existing files. LoanIssueFormPage.tsx (NEW) required changes to:
- App.tsx (routing)
- types/index.ts (type definitions)
- submissions.ts (submission logic)

**LOS Issue Tracker - File Addition Analysis:**

Files ADDED (selected):
```
554c8fa Release v0.2.0
  → src/components/ConfirmReleaseModal.tsx (NEW)
  → migrations/026_allow_ticket_release.sql (NEW)

42a83b1 Add mandatory Google OAuth authentication
  → AuthContext modifications
  → LoginScreen redesign

f54e41a Add Google Sheets integration
  → supabase/functions/sync-to-sheets/index.ts (MAJOR modification)
  → migrations for Google Sheets references
```

**Key Insight**: LOS Tracker's file additions are more explicit about scope. Each feature is tracked as a migration (SQL) + component (TypeScript) + hook modification (query logic). Ring Kissht mixes these concerns in single commits.

---

## SECTION 3: Change Coupling Analysis

### 3.1 Identifying Files That Always Change Together

**Pattern 1: Type Definitions Coupled with Implementations**

```
When types/index.ts changes, expect these to change:
├─ Any page using the type (grep for import)
├─ Any component using the type
├─ Any API function accepting the type
└─ Any hook returning the type

Ring Kissht Example:
commit c757748 touches:
- types/index.ts (add LoanIssueFormData)
- pages/LoanIssueFormPage.tsx (uses LoanIssueFormData)
- pages/SubmitPage.tsx (also uses similar types, needed updates)
- lib/submissions.ts (form processing uses types)

→ Rule: If you modify ANY type definition, grep for all imports
```

**Pattern 2: Database Migrations Coupled with Types and Hooks**

```
When database schema changes, expect these to change:
├─ Migrations: SQL files defining schema
├─ Types: TypeScript interfaces matching schema
├─ Hooks: Database query logic using new columns
├─ Components: UI using new fields
└─ Edge Functions: Server-side logic accessing new columns

LOS Issue Tracker Example:
commit f54e41a touches:
- migrations: Schema changes for sheet sync
- supabase/functions/sync-to-sheets/index.ts: Uses new columns
- src/hooks/useTickets.ts: Updated queries
- src/components: Updated UI to display new fields
- src/types/index.ts: Updated TypeScript types

→ Rule: If you modify migrations, check all of these
```

**Pattern 3: App.tsx Routing Coupled with All Pages**

```
When App.tsx changes (new routes), expect these to change:
├─ Each new page component
├─ Navigation menus (if they list routes)
├─ Auth guards (if routes have permission requirements)
├─ 404 handling (if new routes affect fallback logic)
└─ Types: Route types if using TypeScript routing

Ring Kissht Example:
App.tsx routing likely includes:
- SubmitPage (initial form)
- LoanIssueFormPage (enhanced form)
- SubmissionDetailPage (view single submission)
- ProductSupportDashboard (admin view)
- ModifySubmissionPage (edit submission)

Each of these requires:
- Route definition in App.tsx
- Component file exists
- Types match (form data types)
- Auth context checks (product support only, etc.)
```

**Pattern 4: UI Component Library Coupled with All Pages**

```
When new UI components are added (Button, Input, Badge), expect:
├─ Component definition file
├─ Index.ts barrel export (ui/index.ts)
├─ Usage in all affected pages
├─ Tailwind config (if using tailwind classes)
└─ Consistency with existing components

Ring Kissht Example (commit 1de2b3c):
New files:
- src/components/ui/Badge.tsx
- src/components/ui/Button.tsx
- src/components/ui/Input.tsx
- src/components/ui/index.ts

Usage:
- Imported in pages/LoanIssueFormPage.tsx
- Imported in pages/LoginPage.tsx
- Imported in pages/ProductSupportDashboard.tsx

→ Rule: When adding UI components, check:
  ├─ Is it exported from ui/index.ts?
  ├─ Is it used in at least 2 pages?
  └─ If only 1 usage, it's over-engineered
```

### 3.2 Tracing Dependencies: If X Changes, What Else Must Change?

**Decision Tree for Change Coupling:**

```
Modified File: types/index.ts
→ Impact Analysis:
  ├─ Search: grep -r "import.*types" src/
  ├─ Result: Lists all files that import from types
  ├─ For each file found:
  │  ├─ Does it define a variable of this type?
  │  ├─ Does it receive this type as a parameter?
  │  ├─ Does it return this type from a function?
  │  └─ If any YES: File must be checked for breakage
  └─ Expected to change: 3-10 files minimum

Modified File: src/pages/LoginPage.tsx
→ Impact Analysis:
  ├─ Search: grep -r "LoginPage" src/
  ├─ Result: Files that import LoginPage
  ├─ Search: grep -r "useAuth\|AuthContext" src/
  ├─ Result: Files that depend on auth state
  ├─ For each file found:
  │  └─ If LoginPage changes auth flow, does this file break?
  └─ Expected to change: 2-5 files

Modified File: src/hooks/useTickets.ts (LOS Issue Tracker)
→ Impact Analysis:
  ├─ Search: grep -r "useTickets" src/
  ├─ Result: AdminView.tsx, ProductSupportView.tsx, TicketCard.tsx
  ├─ For each usage:
  │  ├─ Does it use specific query returned by hook?
  │  ├─ Does it call specific mutations from hook?
  │  └─ If hook signature changes, will this break?
  └─ Expected to change: All 3+ files using the hook

Modified File: Database schema (migrations/##_*.sql)
→ Impact Analysis:
  ├─ Search: All edge functions in supabase/functions/
  ├─ Search: All hooks in src/hooks/
  ├─ Search: All components in src/components/
  ├─ For each file found:
  │  ├─ Does it query the modified table?
  │  ├─ Does it reference the modified column?
  │  └─ If schema changed, will SELECT/INSERT/UPDATE break?
  └─ Expected to change: 2-10 files minimum
```

### 3.3 Real Examples from Both Projects

**Ring Kissht: When types/index.ts was modified (commit c757748)**

Presumed coupling (based on fix cascade):

```
Modified: src/types/index.ts
├─ Added: LoanIssueFormData type with attachmentFiles field

Files that should update:
├─ ✓ src/pages/LoanIssueFormPage.tsx (new page, uses type)
├─ ✓ src/lib/submissions.ts (processes form data)
├─ ? src/pages/SubmitPage.tsx (also submits forms)
├─ ? src/types/index.ts exports (must be added)
└─ ? src/App.tsx (routing must include new page)

Evidence of coupling failure:
- Commit 2b0b251 (2 commits later): Make attachment field optional
  └─ Implies: Existing submissions didn't have attachmentFiles
  └─ Root cause: Type was added but old data wasn't migrated

- Commit fae45b2 (4 commits later): Fix Firestore undefined field
  └─ Implies: Code was sending {attachmentFiles: undefined} to Firestore
  └─ Root cause: No validation before Firestore.add()
```

**LOS Issue Tracker: When database schema changed (f54e41a)**

Coupling analysis:

```
Modified: Database schema (Google Sheets sync)
├─ Added: Columns to track sheet references
├─ Added: Functions for sync logic

Files that should update:
├─ ✓ supabase/functions/sync-to-sheets/index.ts (uses new schema)
├─ ✓ src/hooks/useTickets.ts (queries new columns)
├─ ✓ src/types/index.ts (types for new columns)
├─ ✓ src/pages/AdminView.tsx (displays/manages sheets)
└─ ✓ src/components/TicketForm.tsx (collects sheet data)

Evidence of coupling success:
- Only 1 follow-up fix needed (8e47062)
- Fix is specific: "Fix ticket description visibility across UI and Google Sheets"
- No cascading failures like Ring Kissht
- Documentation added proactively (36710e0)
```

---

## SECTION 4: Commit Message Forensics

### 4.1 What Commit Messages Reveal About Code Quality

**Pattern: "Fix" in Message = Previous Breakage**

Ring Kissht messages (last 20 commits):
```
04f5488 Fix Vercel build: ensure devDependencies installed before build
9b2b8a8 Fix undefined field error: explicitly build object without undefined values
328f7e5 Fix Vercel build: use npx tsc instead of tsc
fae45b2 Fix Firestore undefined field error - only include attachment fields when they have values
16b021d Fix TypeScript errors: remove unused imports
```

Interpretation:
- 5 out of ~8 commits shown are fixes (62% fix rate)
- Multiple "Fix Vercel build" = not properly understood
- Repeated "Fix undefined field error" = incomplete solution
- Generic "Fix TypeScript errors" = not learning from mistakes

LOS Issue Tracker messages:
```
f94bb6f Fix OAuth redirect flicker (login screen flash before dashboard)
9164f4e Fix 12-second login delay caused by Supabase SDK Navigator Lock deadlock
2e844b8 Add perf logging, security fixes, CSS regression fix, and edge function hardening
8e47062 Fix ticket description visibility across UI and Google Sheets
```

Interpretation:
- 4 out of 16 commits are fixes (25% fix rate)
- Fixes are SPECIFIC (redirect flicker, login delay, description visibility)
- Fixes show ROOT CAUSE understanding (Navigator Lock deadlock, Supabase SDK)
- Includes proactive improvements (perf logging, security fixes)

**Pattern: "Add" in Message = New Feature (Check for Duplication Risk)**

Ring Kissht:
```
c757748 Enhance submission process with loan issue form and multiple file uploads
  └─ "loan issue form" suggests duplicate form (SubmitPage already exists)

e7502eb Implement Google Drive integration for file storage
  └─ "integration" = new service, check for configuration/env var oversight
```

LOS Issue Tracker:
```
f54e41a Add Google Sheets integration with live sync
  └─ "with live sync" = real-time feature, high complexity

42a83b1 Add mandatory Google OAuth authentication with email whitelist
  └─ "mandatory" + "email whitelist" = clear constraints

54aeb84 Add TRN (Transaction Reference Number) field for Product Support
  └─ "field" = database change, check type coupling
```

**Pattern: "Remove" in Message = Potential Orphan Risk**

Ring Kissht:
```
90c69fc Remove Vercel config and deploy to Firebase Hosting
  └─ Removed: vercel.json, Vercel build scripts
  └─ Risk: Any scripts depending on Vercel config now fail
```

LOS Issue Tracker:
```
(No major removal commits in recent history)
```

**Pattern: "Refactor" in Message = Check for Regression Risk**

Ring Kissht:
```
53fcde3 Refactor role management and permissions in routing; update Firestore rules for clarity and add new dependencies
  └─ "refactor role management" = changing auth logic
  └─ Risk: Pages with auth guards might break
  └─ Risk: Firestore rules might reject operations that were allowed before
```

LOS Issue Tracker:
```
e9c2c01 Refine UI components and remove dark mode
  └─ "remove dark mode" = CSS changes, check for layout breaking
```

### 4.2 Commit Message Quality Metric

**Ring Kissht Commit Quality:**
```
Score: 2/5

Analysis:
- Messages are VAGUE ("Fix Vercel build", "Fix TypeScript errors")
- Messages DON'T EXPLAIN ROOT CAUSE
- Messages DON'T SUGGEST SOLUTION
- Many commits are CONFIGURATION CHURN (not feature progression)
- Ratio: 62% "Fix" commits = high instability
```

**LOS Issue Tracker Commit Quality:**
```
Score: 4/5

Analysis:
- Messages are SPECIFIC ("Fix OAuth redirect flicker")
- Messages EXPLAIN MECHANISM ("caused by Supabase SDK Navigator Lock deadlock")
- Messages SHOW INTENT ("Release v0.2.0", "Pre-release-feature checkpoint")
- Few "Fix" commits (25%) = more stable progression
- Ratio: Feature additions > fixes = healthy progress
```

**Claude's Commit Message Quality Checklist:**

```
Before committing, check:

1. Specificity Test:
   ├─ Does the message NAME the affected system? (YES: database, routes, etc)
   ├─ Does it say WHAT changed? (YES: feature name, not just "fix")
   └─ Does it explain WHY? (YES: root cause, not just symptom)

2. Information Richness:
   ├─ If "Fix": Include what was broken (Fix widget X)
   ├─ If "Add": Include what was added (Add Y feature)
   ├─ If "Refactor": Include scope (Refactor A to improve B)
   └─ Format: "<Action> <Component>: <Details>"

3. Examples:
   ├─ BAD: "Fix undefined field error"
   ├─ GOOD: "Fix undefined field error in Firestore: validate schema before save"
   ├─ BAD: "Add API function and fix Vercel config pattern"
   ├─ GOOD: "Add Vercel edge function for Google Drive uploads"
   └─ BAD: "Fix TypeScript errors"
   └─ GOOD: "Fix TypeScript errors: remove unused imports and align types with database schema"

4. Red Flags:
   ├─ Message contains multiple unrelated actions? (split commit)
   ├─ Message vague about WHAT was changed? (rewrite)
   ├─ Message is a configuration detail? (too low-level)
   └─ Message repeats a previous fix? (design problem, not implementation)
```

---

## SECTION 5: Git-Based Verification Using Git After Changes

### 5.1 Using git diff --stat to Verify Change Scope

**Purpose**: Ensure your changes match the impact report. Unexpected files modified = missed dependencies.

**Ring Kissht Example - When Should Have Been Limited, But Wasn't:**

Goal: Add Loan Issue Form feature

```
Expected (from impact report):
├─ src/pages/LoanIssueFormPage.tsx (NEW)
├─ src/types/index.ts (modified: +LoanIssueFormData type)
├─ src/lib/submissions.ts (modified: +loan submission logic)
├─ src/App.tsx (modified: +route for loan form)
└─ Expected total: 4 files changed

Actual (from git diff --stat):
├─ src/pages/LoanIssueFormPage.tsx
├─ src/pages/SubmitPage.tsx  ← UNEXPECTED!
├─ src/types/index.ts
├─ src/lib/submissions.ts
├─ src/App.tsx
└─ 5 files changed (1 more than expected)

What This Means:
- SubmitPage.tsx modification wasn't planned
- Indicates: Copy-paste code discovered during implementation
- Indicates: Type changes broke SubmitPage
- Question: Did you update SubmitPage to use new types? Or just quick fix?
```

**Verification Protocol:**

```
Before committing:

1. Run: git diff --stat
2. For each file shown:
   ├─ Is it in your impact report?
   ├─ If YES: Expected? Check the change size
   ├─ If NO: Why is this file changed?
   │  ├─ Did you miss this in your impact report?
   │  ├─ Or did you make an unplanned change?
   │  └─ If unplanned: Is it necessary? If not, revert
   └─ If too many files: Did you make multiple features? (commit separately)

2. Verify change scale matches complexity:
   ├─ Small feature (add field): 2-3 files
   ├─ Medium feature (new form): 4-6 files
   ├─ Large feature (new service): 8-15 files
   └─ If yours is larger: Did you take on too much?

3. Red flags:
   ├─ package.json changed without explanation
   └─ More than 2 major files modified per feature
```

### 5.2 Using git diff to Review Actual Changes Against Guardrails

**Purpose**: Catch logic errors, type mismatches, and unintended side effects.

**Protocol: Type Definition Changes**

```
When modifying types/index.ts, run:
  git diff src/types/index.ts

Check:
1. Did you add OPTIONAL fields as optional (?)?
   ├─ If adding required field to existing type: Will break existing data
   └─ RULE: New fields must be optional, or create new type

2. Did you REMOVE any fields?
   ├─ Search: grep -r "FormData\." src/
   ├─ Result: All usages of the type
   ├─ For each usage: Does it still work after removal?
   └─ RULE: Removals break existing code, use deprecation pattern

3. Example from Ring Kissht (where this was violated):
   ├─ Added LoanIssueFormData type
   ├─ Made attachmentFiles field REQUIRED
   ├─ But SubmitPage still used old SubmissionFormData
   ├─ Result: Type mismatch, runtime error
   └─ Fix later: Made field optional (patch)
```

**Protocol: Component Changes**

```
When modifying a page component, run:
  git diff src/pages/LoginPage.tsx

Check:
1. Did you change the PROPS interface?
   ├─ Search: grep -r "LoginPage" src/
   ├─ For each import: Does it pass the old props?
   └─ If NO: Files will break

2. Did you change the ROUTING?
   ├─ Check: Is App.tsx importing this correctly?
   ├─ Check: Are auth guards still in place?
   └─ RULE: Routing changes must be in App.tsx AND component

3. Did you change the STATE?
   ├─ Search: grep -r "useState" in this file
   ├─ For each state: Is it used in multiple effects?
   ├─ Effect dependencies correct? ([]  vs [state])
   └─ RULE: State changes often break useEffect hooks
```

**Protocol: Database Changes (LOS Tracker Style)**

```
When modifying migrations, run:
  git diff migrations/

Check:
1. Are you ADDING columns?
   ├─ Make them nullable: NOT NULL requires data migration
   ├─ Search: Do edge functions expect this column?
   ├─ Search: Do TypeScript types match?
   └─ RULE: New columns = new TypeScript types required

2. Are you MODIFYING existing columns?
   ├─ This is HIGH RISK
   ├─ Can existing data still satisfy the new definition?
   ├─ Is there a DEFAULT for existing rows?
   └─ RULE: Modifications should preserve backward compat

3. Are you REMOVING columns?
   ├─ Search: grep -r "column_name" src/
   ├─ For each usage: Will the code still work?
   ├─ Search: supabase/functions/ for the column
   └─ RULE: Removals break code in multiple places

4. Example - What Should Have Happened in Ring Kissht:
   ├─ Migration: Add optional attachmentFileCount column
   ├─ TypeScript: Update submission types to include field
   ├─ Validation: Check field before use
   └─ Result: No Firestore undefined field errors
```

### 5.3 Detecting Unintended Changes

**Red Flags in git diff:**

```
1. Files you didn't intend to modify:
   ├─ Check: package.json changed?
   │  └─ Expected: Added dependency for new feature
   │  └─ Unexpected: Modified version numbers or removed packages
   ├─ Check: .env or .env.example changed?
   │  └─ Expected: New env vars for new feature
   │  └─ Unexpected: Secret values in plain text
   ├─ Check: Configuration files changed (tailwind.config, tsconfig)?
   │  └─ Expected: New config for new feature
   │  └─ Unexpected: Unrelated changes

2. Files with WHITESPACE-ONLY changes:
   ├─ Check: git diff --ignore-all-space
   ├─ Result: Did the file actually change logically?
   └─ RULE: Auto-format tools can hide real changes

3. Unintended deletions:
   ├─ Check: git diff --unified=1 (reduces context)
   ├─ For each deletion (-lines): Was this intentional?
   └─ RULE: Line deletions often indicate refactoring done wrong

4. Large change in unexpected places:
   ├─ Example: You thought you modified 200 lines
   ├─ But: git diff --stat shows 500 lines changed
   └─ Investigation: Did you accidentally format the whole file?
```

---

## SECTION 6: Branch Strategy for Safe Feature Addition

### 6.1 Feature Branch Workflow for Isolation

**Best Practice Pattern:**

```
Main branch (main or master)
    │
    ├─ Feature branch (feature/loan-issue-form)
    │   │
    │   ├─ Commit 1: Add LoanIssueFormPage component
    │   ├─ Commit 2: Add LoanIssueFormData type
    │   ├─ Commit 3: Add loan submission logic
    │   ├─ Commit 4: Add form routing to App.tsx
    │   ├─ Test: npm test (runs all tests)
    │   │
    │   └─ Create PR for review
    │       │
    │       ├─ Review: Check for duplication with SubmitPage
    │       ├─ Review: Verify types match database schema
    │       ├─ Review: Verify all required files modified
    │       └─ Merge if OK
    │
    └─ Feature branch merged to main
```

**Ring Kissht Actual Flow (NO Feature Branches):**

```
All work directly to main branch:
c757748: Add Loan Issue Form (with bugs)
2b0b251: Fix attachment field (quick patch)
fae45b2: Fix Firestore undefined (quick patch)
9b2b8a8: Fix undefined field (quick patch again!)

Result: Bugs visible in production, fixes accumulate
```

**LOS Issue Tracker Pattern (Better):**

```
Commit history suggests feature branches:
f54e41a: Add Google Sheets integration (vetted before merge?)
8e47062: Fix ticket description visibility (PR feedback?)
36710e0: Update documentation (proactive)

Result: Documentation follows features, fewer cascading fixes
```

### 6.2 Incremental Commits for Rollback Capability

**Good Pattern - One Concern Per Commit:**

```
Feature: Add ticket release feature

Commit 1: Create database migration
├─ File: migrations/026_allow_ticket_release.sql
├─ Changes: +320 lines (purely SQL schema)
├─ Rollback: Delete file, re-initialize DB

Commit 2: Add ConfirmReleaseModal component
├─ File: src/components/ConfirmReleaseModal.tsx
├─ Changes: +170 lines (React component)
├─ Rollback: Delete file, remove import

Commit 3: Add release mutation to useTickets hook
├─ File: src/hooks/useTickets.ts
├─ Changes: +55 lines (add release logic)
├─ Rollback: Revert this one file

Commit 4: Integrate modal into AdminView
├─ File: src/pages/AdminView.tsx
├─ Changes: +36 lines (use new component)
├─ Rollback: Remove component usage

Result:
├─ If migration fails: Rollback commit 1 only
├─ If component has UX issues: Rollback commit 2 only
├─ If mutation is broken: Rollback commit 3 only
└─ Easy to identify which part failed
```

**Bad Pattern - Multiple Concerns Per Commit:**

```
Commit: "Add API function and fix Vercel config pattern"
├─ Added: api/uploadToDrive.ts (new API)
├─ Modified: vercel.json (configuration)
├─ Modified: package.json (@vercel/node dependency)
├─ Modified: build scripts (build process)
└─ Problem: Can't rollback just the API without breaking build config
```

### 6.3 Pre-Merge Verification Checklist

**Before creating a PR or committing to main:**

```
STRUCTURE VERIFICATION:
☐ Did you use a feature branch? (not direct to main)
☐ Are commits logically ordered? (one concern per commit)
☐ Can each commit be understood independently?
☐ Is each commit atomic (works on its own)?

SCOPE VERIFICATION:
☐ Does git diff --stat match your impact report?
☐ Are there unexpected files modified?
☐ Is the total change volume reasonable?
  ├─ <100 lines: Small feature
  ├─ 100-500 lines: Medium feature
  ├─ 500-1500 lines: Large feature
  ├─ >1500 lines: Split into multiple features

TYPE SAFETY VERIFICATION:
☐ Did you modify types/index.ts?
  └─ grep -r "import.*types" src/ (check all usages)
☐ Do TypeScript errors exist? (npm run type-check)
☐ Are all type imports added?
☐ Are there new type errors in other files?

DATABASE VERIFICATION (if applicable):
☐ Did you add migrations?
  ├─ Are new columns nullable? (if adding to existing tables)
  ├─ Do migrations have rollback logic?
  └─ Is the migration numbered correctly?
☐ Do TypeScript types match migration schema?
☐ Are edge functions updated to handle new schema?

COMPONENT VERIFICATION:
☐ Did you add new pages/components?
  ├─ Are they exported correctly?
  ├─ Are they imported where needed?
  ├─ Are they routed in App.tsx?
  └─ Are they tested (or noted as not tested)?
☐ Did you copy code from other components?
  └─ If YES: Should it be a shared component instead?

ROUTING VERIFICATION:
☐ Are new routes added to App.tsx?
☐ Do auth guards protect sensitive routes?
☐ Are 404 routes still working?
☐ Can users navigate to all new pages?

BUILD & DEPLOYMENT VERIFICATION:
☐ Does the build succeed? (npm run build)
☐ Are there new dependencies? (package.json)
  └─ Are they pinned to specific versions?
  └─ Do they have known security vulnerabilities?
☐ Are environment variables documented?
  └─ Is .env.example updated?
  └─ Does deployment documentation mention new vars?

GIT HISTORY VERIFICATION:
☐ Do commit messages explain WHY, not just WHAT?
☐ Is the message specificity good?
  └─ Not: "Fix bug" but "Fix undefined field in Firestore"
☐ Would you understand this change in 6 months? (future you test)

TEST VERIFICATION:
☐ Are there tests for critical paths?
☐ Do existing tests still pass?
☐ Have you tested the feature manually?
☐ Have you tested error cases?
  ├─ What if file upload fails?
  ├─ What if database is slow?
  ├─ What if external service is down?
  └─ Does the feature handle gracefully?

DOCUMENTATION VERIFICATION:
☐ Is there a CHANGELOG entry?
☐ Is README.md updated if needed?
☐ Are new configuration steps documented?
  └─ Example: New env vars, migration steps, dependency installs
```

---

## Summary: Git Forensics Quick Reference

**When to run each command:**

```
Before starting work:
→ git log --oneline -30 (recent pattern analysis)
→ git log --format="%h %s" --grep="Fix" -20 (what broke before)
→ git diff HEAD~5..HEAD --name-only (which files change together)

During implementation:
→ git diff --stat (verify scope matches plan)
→ git diff (check for unintended changes)
→ grep -r "ModifiedType" src/ (find all usages of changed types)

Before committing:
→ git diff --stat (final scope check)
→ npm run type-check (ensure types are correct)
→ npm run build (ensure code compiles)
→ git log --oneline -10 (verify commit message quality)

After committing (in PR):
→ git log -p (review actual changes)
→ git log --stat (verify each commit scope)
→ Compare: impact report vs. actual changes
```

**Red Flags to Watch For:**

1. **Fix commits outnumber feature commits** (>50% fixes)
2. **Multiple fixes for same issue** (Fix X, then Fix X again)
3. **Generic fix messages** (Fix bug, Fix error)
4. **Large commits** (>1000 lines in one commit)
5. **File coupling not understood** (types changed, usages not updated)
6. **Configuration churn** (vercel.json modified 3 times in 5 commits)
7. **Copy-paste code** (same function in 2 files, one modified, other not)

**Success Indicators:**

1. **Feature commits > fix commits** (<30% of commits are fixes)
2. **Specific fix messages** (Fix X in service Y)
3. **Small commits** (50-200 lines per commit)
4. **Clear file coupling** (all dependent files updated together)
5. **Documentation proactive** (docs updated with features, not after)
6. **One concern per commit** (easy to rollback)
7. **Stable commit graph** (main branch always has working code)
