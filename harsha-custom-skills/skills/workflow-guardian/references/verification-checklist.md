# Post-Change Verification Checklist Reference

**Purpose**: Verify that code changes don't introduce regressions. Use this checklist immediately after making changes and before committing.

---

## 1. Automated Verification (Run First)

Execute these commands in sequence. If any fail, the change is not ready for commit.

```bash
# TypeScript compilation check
npx tsc --noEmit

# Linting check
npx eslint src/

# Build verification
npm run build

# Run tests (if they exist)
npm test

# ESM import validation (check for broken imports)
node -e "import('./dist/index.js').catch(e => { console.error('Import failed:', e); process.exit(1) })"
```

**What to look for**:
- No TypeScript errors (`error TS[####]`)
- No ESLint violations (or violations were pre-existing)
- Build completes without warnings about missing files
- All tests pass (or test count unchanged from baseline)
- No `Cannot find module` errors

**Common failures and fixes**:
- `Cannot find module 'X'`: Check import path is relative and file exists
- `error TS1192`: Import/export mismatch; verify exported symbol exists
- Build fails silently: Check `tsconfig.json` includes all source files

---

## 2. Route Verification

For each route in the application's route map:

1. **Navigate to the route**: Visit the URL directly (e.g., `/dashboard`, `/settings`)
2. **Verify component renders**: Page displays without 404 or blank screen
3. **Check route guard enforcement**:
   - If role-protected: log in as unauthorized user, verify redirect
   - Example: Product Support route should redirect Admin users to `/unauthorized`
4. **Verify navigation flows work end-to-end**:
   - Form submission → success toast → redirect to list → new item visible
   - Example: Create issue → redirect to issues page → new issue appears in table

**Test matrix** (example for issue tracker):
| Route | Component | Auth Required | Roles Allowed | Navigation Source |
|-------|-----------|---------------|---------------|-------------------|
| `/issues` | IssueList | Yes | Admin, Support | Header menu |
| `/issues/:id` | IssueDetail | Yes | Admin, Support | IssueList click |
| `/issues/new` | IssueForm | Yes | Support | Create button |
| `/admin` | AdminPanel | Yes | Admin | Header menu |

---

## 3. Data Flow Verification

Trace data through the complete pipeline: **Input → State → API → Database → Display**

### Form Submission Test
```
1. Fill form field → State updates (verify with React DevTools)
2. Submit form → API call succeeds (check Network tab)
3. Verify database receives data: SELECT * FROM issues WHERE created_at > NOW() - INTERVAL 1 minute
4. Navigate to list view → New entry appears in table with all fields
5. Click detail view → All submitted fields display correctly
```

### List/Table Verification
- [ ] All column headers match database fields
- [ ] All rows display complete data (no truncation or missing values)
- [ ] Pagination/sorting still works if present
- [ ] Empty state message shows when no data exists

### Detail View Verification
- [ ] All form fields pre-populate from database
- [ ] All fields match their values in the database
- [ ] Related data (foreign keys) resolve correctly
- [ ] Timestamps display in correct timezone

**Real regression example** (from research):
```
Issue: Google Sheets integration added but ticket description didn't sync
Root cause: Description field missing from sync mapping
Detection: Data showed correctly in app, but not in Sheets
Prevention: Test that every field in form appears in database AND in third-party sync
```

---

## 4. Role Access Verification

Test access control for each user role in the system.

**Test procedure for each role** (e.g., Admin, Support, Guest):
1. Log in as user with that role
2. Navigate to each route in the route map
3. Record: Can access? Should access? Match expected?
4. Check for role-specific UI elements (buttons, fields, sections)

**Verification checklist**:
- [ ] Admin can access `/admin` → Support cannot (redirects or 403)
- [ ] Support can access `/issues` → Admin can also access (no regression)
- [ ] Guest cannot access any protected route → redirects to login
- [ ] Edit/Delete buttons hidden for read-only users
- [ ] Form fields disabled appropriately (e.g., status field for Support users)

**Common role regressions**:
- Role check moved to wrong component (some pages skip it)
- Role value changed in code but not in database/auth context
- New route added without role guard (security leak)
- UI element shows for wrong role (confusion, security issue)

---

## 5. UI Regression Detection

Check for unintended visual changes.

### Color Palette Consistency
```bash
# Find all color values in modified files
grep -r "color:\s*#\|bg-\|text-\|border-" src/components/ModifiedComponent.tsx | head -20
```

Expected colors (document your palette):
- Primary: `#007ACC` (blue)
- Success: `#28A745` (green)
- Danger: `#DC3545` (red)
- Background: `#FFFFFF` or `#F5F5F5`

**Look for**:
- [ ] New hex colors not in palette (e.g., `#FF00FF` is unplanned)
- [ ] Hardcoded colors in component (should use CSS variables or theme)
- [ ] Tailwind classes with custom colors (should use `@apply` for consistency)

### Heading Hierarchy
- [ ] Page uses h1 once at top
- [ ] All h2/h3/h4 follow logical nesting (no h2 → h4 jump)
- [ ] No more than 3 heading levels per page

### Form Element Consistency
- [ ] All input fields have same height/padding
- [ ] Labels are above inputs (or consistently placed)
- [ ] Error messages in same color and position
- [ ] Submit buttons use consistent styling

### Responsive Design
- [ ] Resize browser to 375px (mobile) → layout stacks vertically
- [ ] No horizontal scrolling on mobile
- [ ] Touch targets (buttons) are 44px+ minimum
- [ ] Text readable without zooming (minimum 16px)

---

## 6. Change Impact Cross-Reference

**Before committing, compare your changes against the Impact Report.**

### Generate Impact Report
```bash
# Show all modified files
git diff --name-only HEAD~1

# Show what each file exports/imports
grep -E "^export|^import" src/ModifiedFile.ts
```

### Verification Steps
1. **List all modified files** → Compare to Impact Report
   - Expected in report? ✓ OK
   - Not in report? ⚠️ Investigate if change was accidental
2. **Check for new dependencies**:
   ```bash
   npm ls --depth=0  # Compare to previous baseline
   ```
   - New package added? Verify it was intentional
3. **Check for new routes**:
   ```bash
   grep -r "Route\|path=" src/App.tsx src/routes/
   ```
   - New route added? Verify it's in Impact Report

**Common unintended changes**:
- Modified a utility file intending to change only one function, but broke others
- Added a dev dependency that shipped to production
- Added a new route for testing, forgot to remove it
- Changed component export, breaking other imports

---

## 7. Minimum Viable Verification (Quick Changes Only)

**Use this abbreviated checklist ONLY for:**
- Bug fixes in isolated functions
- UI tweaks (color, spacing only)
- Documentation updates

**Minimum steps**:
```bash
✓ npm run build          # Project builds
✓ npx tsc --noEmit      # TypeScript compiles
✓ npm test -- --testNamePattern="ModifiedFeature"  # Related tests pass
```

**Then manually test**:
1. Navigate to the modified feature
2. Verify it works as intended
3. Verify closely-related features still work (don't break importers)

**Example**: Changing button color from blue to green
- ✓ Build succeeds
- ✓ TypeScript clean
- ✓ Related component tests pass
- ✓ Button displays in green
- ✓ Form still submits successfully (button was clickable)

---

## Real Regression Examples (From Research)

### Example 1: Silent Data Model Break
```
Commit: Added optional attachments field to form
  └─ Form validation didn't check for undefined values
  └─ Firestore rejected undefined fields
  └─ Data silently lost: form appeared to submit successfully
  └─ Discovered 4 commits later when debugging data loss

Prevention: In Data Flow Verification (step 3), check:
  1. Create issue WITH attachments → succeeds
  2. Create issue WITHOUT attachments → verify all other fields saved
  3. Check database: SELECT * → all rows have complete data
```

### Example 2: Build System Cascade Failure
```
Commit: Refactored build system (vite → tsc)
  └─ 5 follow-up "fix" commits needed
  └─ Each fix uncovered new missing piece:
     1. DevDependencies not installed
     2. tsc command not found (needed npx)
     3. TypeScript configuration mismatch
     4. Still needed another fix

Prevention: Before refactoring build:
  1. Test build in clean environment (delete node_modules, npm ci)
  2. Test build on deployment platform (Vercel, Firebase, etc.)
  3. Don't commit if build fails even once
```

### Example 3: Authentication Feature Cascade
```
Commit: Added Google OAuth authentication
  └─ Broke 3 things simultaneously:
     1. UI flicker: login screen showed before redirect
     2. Login delay: 12-second wait from async race condition
     3. Edge function security: didn't harden functions for OAuth

Prevention: When adding auth features:
  1. Test login flow end-to-end (no flicker)
  2. Time login process (should be <2 seconds)
  3. Check edge functions still enforce auth (run Route Verification step 3)
  4. Test authorization changes don't break existing roles
```

---

## Quick Reference: Command Checklist

```bash
# BEFORE COMMIT: Run all these
npm run build                           # Must succeed
npx tsc --noEmit                        # Must be clean
npx eslint src/                         # Should be clean
npm test                                # Should pass
grep -r "import.*ModifiedFile" src/    # Check for broken imports
git diff --name-only HEAD~1             # Review what changed
npm ls --depth=0                        # Verify dependencies
```

---

## When to Stop and Debug

Stop and investigate further if:
- ❌ Build fails for any reason
- ❌ TypeScript has errors
- ❌ Any test fails (related or unrelated)
- ❌ A modified file doesn't compile
- ❌ An importer of modified code breaks
- ❌ A route returns 404 or blank screen
- ❌ Form submission silently fails (no error toast)
- ❌ Role-protected route accessible to wrong user
- ❌ Data doesn't appear in database after form submission
- ❌ Any modified file differs from Impact Report

**Do not commit** until all these are resolved.
