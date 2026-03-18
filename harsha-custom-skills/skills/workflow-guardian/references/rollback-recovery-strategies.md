# Rollback and Recovery Strategies for Workflow-Guardian

## Overview

This reference document provides comprehensive guidance on **rollback and recovery procedures** for the workflow-guardian skill. When Phase 4 (Verification) detects that changes have broken the application, Claude needs clear, structured procedures to identify the failure and recover safely.

The fundamental principle: **Always design changes so they can be undone in reverse order.**

---

## Part 1: Core Principles

### 1.1 The Safety-First Philosophy

**DANGEROUS APPROACH:**
- Make 10 changes at once
- Run verification
- Something breaks
- Spend 2 hours diagnosing which of 10 changes caused it
- Manually fix multiple components

**SAFE APPROACH:**
- Make ONE change
- Verify it works
- Commit to git with clear message
- Next change builds on known-good state
- If verification fails, rollback is one atomic commit

### 1.2 The "Breadcrumb Trail" Pattern

Every commit is a safe checkpoint you can return to:

```
main branch:
  ├─ commit: "feat: Add auth module" ✓ VERIFIED
  ├─ commit: "feat: Add route to auth page" ✓ VERIFIED
  ├─ commit: "feat: Connect auth to state management" ✓ VERIFIED
  ├─ commit: "feat: Update navbar for auth user" ✓ VERIFIED
  └─ commit: "feat: Add profile page" ✗ FAILED VERIFICATION
```

If the last commit fails, rollback is a single command: `git reset --hard HEAD~1`

### 1.3 Atomic Commits Principle

From [Atomic commits best practices](https://gitbybit.com/gitopedia/best-practices/atomic-commits):

> An atomic commit is an operation that applies a set of distinct changes as a single operation. If there is a failure before completion, all changes are reversed, ensuring the system remains in a consistent state.

**Benefits:**
- Easy rollback of specific features without touching unrelated code
- Clear commit history makes bisecting easier
- Each commit can be tested independently
- Reviewers can understand one logical change per commit

---

## Part 2: Pre-Change Safety Protocols

### 2.1 Creating the "Known Good State" Checkpoint

**BEFORE starting Phase 3 (Implementation):**

```bash
# 1. Ensure all current tests pass
npm test

# 2. Build succeeds with no errors
npm run build

# 3. Check for uncommitted changes (should be clean)
git status

# 4. Create a safety branch (optional but recommended for major changes)
git checkout -b feature/my-change

# 5. Document the baseline
git log --oneline -1  # Save this commit hash

# 6. Take a screenshot of affected pages (if UI changes)
# Tools: Screenshot tool, visual regression baseline
```

**Save this information:**
```markdown
## Baseline for Feature: [Feature Name]

- **Last Known Good Commit**: [hash]
- **Test Status**: All tests passing
- **Build Status**: No errors, bundle size: [size]
- **Screenshots**: [links to baseline screenshots]
- **Date**: [timestamp]
```

### 2.2 Establishing Test Baselines

From [Baseline Testing best practices](https://www.geeksforgeeks.org/software-testing/baseline-testing/):

Baseline testing establishes a standard of performance before changes are made. Every future test compares against this snapshot.

**Pre-change baseline captures:**

1. **Functional Tests**
   ```bash
   npm test -- --reporter=json > baseline-test-results.json
   ```

2. **Build Output**
   ```bash
   npm run build
   # Save bundle size and timing
   ```

3. **Type Checking**
   ```bash
   npx tsc --noEmit
   # No errors expected
   ```

4. **Visual Regression Baseline**
   ```bash
   # Take screenshots of key pages
   # Save pixel-perfect baseline images
   ```

5. **Runtime Performance**
   ```bash
   # Record initial load time, memory usage
   ```

### 2.3 Creating Feature Branches

```bash
# For major features, create isolated branches
git checkout -b feature/your-feature-name

# For hotfixes, create fix branches
git checkout -b fix/bug-description

# For experiments, create experiment branches
git checkout -b experiment/test-idea
```

**Advantages:**
- Main branch stays stable
- Easy to discard entire branch if needed: `git branch -D feature/your-feature`
- Can switch between branches without losing work: `git stash`

---

## Part 3: Incremental Implementation Pattern

### 3.1 The Make-One-Change Pattern

**The Workflow:**

```
1. Make ONE logical change (one file, one feature)
2. Save the file
3. Run verification (tests, build, type check)
4. If PASS: commit with clear message → next change
5. If FAIL: git diff to identify issue → fix → verify → commit
```

**Example Structure:**

```markdown
## Implementing User Auth

Phase 1: Auth Module (1 change)
- [ ] Create auth.ts module with login/logout functions
- [ ] Verify: Types compile, basic unit tests pass
- [ ] Commit: "feat: Add auth module"

Phase 2: Auth Page (1 change)
- [ ] Create login.tsx component
- [ ] Verify: Component renders, no console errors
- [ ] Commit: "feat: Add login page component"

Phase 3: Route Configuration (1 change)
- [ ] Add /login route to router config
- [ ] Verify: Route renders, no 404s
- [ ] Commit: "feat: Add login route"

Phase 4: State Management (1 change)
- [ ] Connect auth module to context/store
- [ ] Verify: State changes propagate
- [ ] Commit: "feat: Connect auth to state management"

Phase 5: UI Integration (1 change)
- [ ] Add login button to navbar
- [ ] Verify: Button appears, click navigates to /login
- [ ] Commit: "feat: Add login button to navbar"
```

### 3.2 When to Stop and Ask the User

**Stop and ask the user before committing if:**

1. **Behavioral change differs from specification**
   - "The spec says delete creates archive, but I implemented hard delete"
   - Get clarification before proceeding

2. **Multiple valid solutions exist**
   - "Should we use Redux or Context API for state management?"
   - Let user choose before investing in one approach

3. **Dependency chain breaks**
   - "Adding this feature requires updating 5 other components"
   - Document the scope change and get approval

4. **Performance concerns arise**
   - "This query could be slow on large datasets"
   - Discuss optimization vs. simple implementation

5. **Breaking change is unavoidable**
   - "This requires renaming the User type everywhere"
   - Flag the scope and get buy-in

### 3.3 Progressive Feature Implementation

**Skeleton → Data → Styling → Interactions**

```typescript
// Step 1: Skeleton (component structure, no logic)
export function UserProfile() {
  return (
    <div>
      <header>User Profile</header>
      <section>User details here</section>
      <section>User actions here</section>
    </div>
  );
}

// Verify: Component renders, no TypeScript errors ✓
// Commit: "feat: Add UserProfile component skeleton"

// Step 2: Add data (fetch user, display in template)
export function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <header>{user.name}</header>
      <section>{user.bio}</section>
      <section>{user.email}</section>
    </div>
  );
}

// Verify: Data loads, displays correctly ✓
// Commit: "feat: Add user data fetching to UserProfile"

// Step 3: Add styling (CSS, layout, visual design)
// (CSS changes only, no logic changes)
// Verify: Looks correct, responsive ✓
// Commit: "style: Update UserProfile styling"

// Step 4: Add interactions (edit mode, buttons, forms)
// (Add onClick handlers, form submissions)
// Verify: All buttons work, no console errors ✓
// Commit: "feat: Add edit functionality to UserProfile"
```

---

## Part 4: Git-Based Rollback Strategies

### 4.1 Understanding Git Reset Modes

From [Git Reset documentation](https://git-scm.com/docs/git-reset):

| Mode | HEAD | Staging Area | Working Dir | Use Case |
|------|------|--------------|-------------|----------|
| `--soft` | ✓ Moved | Unchanged | Unchanged | "Undo commit but keep changes staged" |
| `--mixed` | ✓ Moved | ✓ Cleared | Unchanged | "Undo commit and unstage, keep edits" |
| `--hard` | ✓ Moved | ✓ Cleared | ✓ Deleted | "Complete rollback, discard all changes" |

**When to use each:**

```bash
# --soft: I committed too early, let me add more before re-committing
git reset --soft HEAD~1
# Changes stay in staging area, just uncommit

# --mixed: I committed, want to unstage and redo parts
git reset --mixed HEAD~1
# Or just: git reset HEAD~1 (--mixed is default)
# Changes stay in working directory, unstaged

# --hard: Complete disaster, burn it all down
git reset --hard HEAD~1
# Dangerous! Discards all changes, cannot undo (unless reflog)
```

### 4.2 Safe Rollback: Using git revert

From [Git Revert documentation](https://git-scm.com/docs/git-revert):

**IMPORTANT:** `git revert` is safer than `git reset` for shared branches.

```bash
# BAD (for shared code): Rewrites history
git reset --hard HEAD~3
# Anyone who pulled now has conflicting history

# GOOD (for shared code): Creates new commit that undoes the change
git revert HEAD~2
# Creates a new commit with the inverse changes
# History is preserved, can be pushed safely
```

**Comparison:**

```
Before:
main: A -> B -> C -> D -> E

git reset --hard HEAD~2:
main: A -> B (C, D, E are gone)

git revert HEAD~2:
main: A -> B -> C -> D -> E -> E' (where E' undoes D)
```

### 4.3 Using git stash for Safety

From [Git Stash best practices](https://opensource.com/article/21/4/git-stash):

Stashing temporarily saves uncommitted changes without committing them.

```bash
# Save current work without committing
git stash

# Work on something else
git checkout main
git pull origin main

# Return to your work
git stash pop

# Or apply without removing from stash
git stash apply

# List all stashes
git stash list

# Named stashes for clarity
git stash save "WIP: auth component with hooks"
git stash pop stash@{0}

# Clean up old stashes
git stash drop stash@{2}
```

**Safety pattern for experimentation:**

```bash
# Before trying a risky change
git stash

# Make experimental change
# Test it
# If it works: continue developing (no need to unstash)
# If it fails: git checkout . && git stash pop to restore
```

### 4.4 Cherry-picking Specific Changes

From [Git Cherry-Pick documentation](https://git-scm.com/docs/git-cherry-pick):

Selectively apply commits from one branch to another.

```bash
# After rollback, reapply specific good commits
git cherry-pick abc123  # Apply commit abc123 to current branch

# Cherry-pick a range
git cherry-pick abc123..def456  # All commits from abc123 to def456

# Cherry-pick with strategy for conflicts
git cherry-pick --strategy=recursive -X theirs abc123

# If conflicts occur, resolve then continue
git add .
git cherry-pick --continue
```

**Scenario: Partial rollback**

```bash
# Commits were: A (good) -> B (good) -> C (bad) -> D (bad)
git reset --hard HEAD~2  # Back to B

# Now reapply only the good parts
git cherry-pick <hash-of-A>  # If A wasn't included in reset
# Or manually cherry-pick specific hunks of C/D if partially good
```

### 4.5 Using git diff to Understand Changes

```bash
# What changed in the last commit?
git diff HEAD~1

# What's uncommitted?
git diff

# What's staged?
git diff --cached

# Compare branches
git diff main..feature/my-change

# Show only file names
git diff --name-only

# Show detailed stats
git diff --stat

# Compare specific file across commits
git diff abc123..def456 -- src/components/Auth.tsx

# Visual diff in external tool
git difftool HEAD~1
```

**Use case: Verify a change before committing**

```bash
# Make a change
# Before committing, see exactly what changed:
git diff

# If it looks wrong, discard:
git checkout -- src/Auth.tsx

# If it looks right, stage and commit:
git add src/Auth.tsx
git commit -m "fix: Correct auth validation logic"
```

---

## Part 5: Feature Branch Workflow

### 5.1 Complete Feature Branch Workflow

```bash
# 1. Create feature branch from latest main
git checkout main
git pull origin main
git checkout -b feature/user-authentication

# 2. Make changes with atomic commits
git add src/auth.ts
git commit -m "feat: Add auth module with login/logout"

git add src/pages/Login.tsx
git commit -m "feat: Add login page component"

git add src/routes.ts
git commit -m "feat: Add /login route"

# 3. Before pushing, sync with main (main may have changed)
git fetch origin main
git rebase origin/main
# (Resolve any conflicts if main changed files you touched)

# 4. Push feature branch
git push origin feature/user-authentication

# 5. Create pull request (on GitHub/GitLab/etc)
# Wait for review and testing

# 6. Merge to main
git checkout main
git pull origin main
git merge feature/user-authentication
git push origin main

# 7. Clean up
git branch -d feature/user-authentication
git push origin -d feature/user-authentication
```

### 5.2 Aborting a Feature Branch

```bash
# If feature branch is broken beyond repair:

# Delete the branch without merging
git branch -D feature/user-authentication

# Delete from remote
git push origin -d feature/user-authentication

# Start fresh
git checkout main
git pull origin main
git checkout -b feature/user-authentication-v2
```

---

## Part 6: Verification Failure Triage

### 6.1 Decision Tree for Failure Diagnosis

```
Verification Failed
│
├─ TypeScript Compilation Fails
│  ├─ Missing import? → Add import statement
│  ├─ Type mismatch? → Check type definition, fix at source
│  ├─ Missing dependency? → npm install, update package.json
│  └─ Syntax error? → Check recent code edits
│
├─ Build Process Fails
│  ├─ Webpack/Vite config error? → Review config changes
│  ├─ Asset not found? → Check file paths
│  ├─ Memory exceeded? → Reduce bundle size
│  └─ Missing environment variables? → Check .env file
│
├─ Test Fails
│  ├─ Existing test broken? → Identify which test, check code change
│  ├─ New test needed? → Add test case for new feature
│  ├─ Test environment issue? → Check mock setup
│  └─ Timing/async issue? → Add await/proper async handling
│
├─ Runtime Error (Console)
│  ├─ TypeError? → Check null/undefined, add type guards
│  ├─ Reference error? → Import/export issue, check module
│  ├─ Event listener error? → Check callback signature
│  └─ API error? → Check endpoint, network request
│
├─ Visual Regression
│  ├─ Layout broken? → Check CSS changes, responsive design
│  ├─ Element missing? → Check if component renders
│  ├─ Element positioned wrong? → Check flexbox/grid changes
│  └─ Styling wrong? → Check CSS selectors, specificity
│
├─ State Management Break
│  ├─ Context not updating? → Check Provider placement
│  ├─ State stale? → Check dependency arrays in hooks
│  ├─ Wrong value? → Check reducer logic
│  └─ Provider missing? → Add Provider wrapper
│
├─ Route Not Rendering
│  ├─ Route not defined? → Add route configuration
│  ├─ Component not imported? → Add import
│  ├─ Route path conflict? → Check route order
│  └─ Layout wrapper missing? → Check parent routes
│
├─ Auth/Role System Break
│  ├─ User not logged in? → Check auth flow
│  ├─ Permissions missing? → Check role/permission logic
│  ├─ Token expired? → Check token refresh
│  └─ Session lost? → Check storage/cookies
│
└─ Data Model Break
   ├─ API contract mismatch? → Update API client
   ├─ Database schema mismatch? → Migration issue
   ├─ Serialization error? → Check data transformation
   └─ Foreign key constraint? → Check relational integrity
```

### 6.2 Identifying the Breaking Change

#### Method 1: git diff Recent Commits

```bash
# See what changed in the last few commits
git log --oneline -10
git show HEAD

# If it's obvious, rollback that commit
git reset --hard HEAD~1
```

#### Method 2: git bisect for Binary Search

From [Git Bisect guide](https://www.metaltoad.com/blog/beginners-guide-git-bisect-process-elimination):

If you have 100 commits and don't know which broke things:

```bash
# Mark the current state as bad
git bisect start
git bisect bad

# Mark a known good commit (maybe from weeks ago)
git bisect good abc123

# Git checks out the midpoint
# Test: does it work or fail?
git bisect good   # if it works
# or
git bisect bad    # if it fails

# Continue marking until git finds the first bad commit
git bisect reset  # exit bisect mode
```

**Binary search efficiency:** 100 commits → ~7 tests to find the culprit. 1000 commits → ~10 tests.

#### Method 3: Automated Testing with git bisect

```bash
# Create a test script that exits 0 (pass) or 1 (fail)
cat > test-feature.sh << 'EOF'
#!/bin/bash
npm test -- --testNamePattern="UserAuth" || exit 1
EOF

chmod +x test-feature.sh

# Let git bisect run the test automatically
git bisect start
git bisect bad HEAD
git bisect good abc123
git bisect run ./test-feature.sh

# Git automatically finds the breaking commit
git bisect reset
```

### 6.3 Specific Failure Recovery Procedures

#### Recovery: TypeScript Compilation Error

```bash
# 1. Identify the error
npm run build 2>&1 | head -20

# Example error: "src/components/Auth.tsx:15 - error TS2339:
#   Property 'isAuthenticated' does not exist on type 'User'"

# 2. Review the change
git diff HEAD~1 src/components/Auth.tsx

# 3. Options:
#    a) Fix the type definition (src/types/User.ts)
#    b) Fix the component to check the property exists
#    c) Rollback the change

# Option A: Fix types
git diff HEAD~1 -- src/types/User.ts
# Edit src/types/User.ts to add missing property
npm run build  # verify

# Option B: Fix component
git diff HEAD~1 -- src/components/Auth.tsx
# Edit component to use correct property name
npm run build  # verify

# Option C: Rollback (if fixing is complex)
git reset --hard HEAD~1
```

#### Recovery: Import Resolution Failure

```bash
# Error: "Cannot find module '@/components/Button'"

# 1. Check if file exists
ls -la src/components/Button.tsx

# 2. Check tsconfig paths configuration
cat tsconfig.json | grep -A 5 '"paths"'

# 3. Possible fixes:
#    a) File was moved but import not updated
#    b) File was renamed
#    c) tsconfig path alias is wrong

# Find all imports of the missing module
grep -r "@/components/Button" src/

# Update them to correct path
# sed -i 's|@/components/Button|@/components/buttons/Button|g' src/**/*.tsx

# Verify TypeScript compiles
npx tsc --noEmit

# Test in browser
npm run dev  # or npm start
```

#### Recovery: Test Failure

```bash
# 1. Identify which test failed
npm test -- --verbose 2>&1 | grep "FAIL\|PASS"

# 2. Run just that test to see detailed error
npm test -- --testNamePattern="UserAuth" --verbose

# 3. Understand the failure:
#    - Is the test wrong? (test needs updating for new behavior)
#    - Is the code wrong? (code change broke expected behavior)

# 4. Option A: Update test for intentional behavior change
vim src/__tests__/UserAuth.test.ts
npm test -- --testNamePattern="UserAuth"  # verify
git add src/__tests__/UserAuth.test.ts
git commit -m "test: Update UserAuth test for new behavior"

# 4. Option B: Fix code to match expected behavior
git diff HEAD~1 -- src/auth.ts
vim src/auth.ts  # revert the logic
npm test  # verify
git add src/auth.ts
git commit -m "fix: Restore UserAuth expected behavior"
```

#### Recovery: Visual Regression

```bash
# 1. Take a screenshot of broken page
# Store as: broken-screenshot.png

# 2. Compare to baseline screenshot
# Visual diff tools: diff-so-fancy, visual regression tools

# 3. Identify which CSS changed
git diff HEAD~1 -- src/styles/

# 4. Options:
#    a) Revert CSS changes
#    b) Fix CSS to match design
#    c) Update baseline if change is intentional

# Option A: Revert CSS
git checkout HEAD~1 -- src/styles/components.css
npm run build
npm run dev  # verify looks correct
git add src/styles/components.css
git commit -m "revert: Restore button styling"

# Option B: Fix CSS
vim src/styles/components.css
npm run dev  # test in browser
git add src/styles/components.css
git commit -m "fix: Correct button padding"

# Option C: Accept new look
# Take new screenshot and update baseline
```

#### Recovery: Runtime Error in Browser Console

```
Error: Cannot read property 'length' of undefined
  at UserList.tsx:45

# 1. Check the file and line
cat -n src/components/UserList.tsx | sed -n '40,50p'

# 2. Identify what's undefined
git show HEAD~1:src/components/UserList.tsx > /tmp/old.tsx
diff -u /tmp/old.tsx src/components/UserList.tsx

# 3. Determine root cause:
#    a) API data format changed
#    b) Component is receiving wrong props
#    c) State initialization missing

# Option A: API format changed
# Check API response format, update component to handle it

# Option B: Props issue
# Check parent component, verify props being passed

# Option C: State initialization
# Add fallback or guard:
const users = props.users ?? [];  // undefined safety
```

#### Recovery: State Management Break

```bash
# Symptom: State updates don't reflect in UI

# 1. Check if Provider is wrapping the component tree
git diff HEAD~1 -- src/App.tsx
# Should see: <AuthProvider><AppComponents/></AuthProvider>

# 2. Check Context definition
git diff HEAD~1 -- src/context/AuthContext.tsx
# Should have: React.createContext()

# 3. Check hook usage
git diff HEAD~1 -- src/components/UserProfile.tsx
# Should have: const { user } = useAuth()

# 4. Verify dependency arrays in useEffect
cat src/components/UserProfile.tsx | grep -A 3 "useEffect"
# If dependency array is missing, add it: useEffect(() => {...}, [])

# 5. Test the context
npm test -- UserProfile

# 6. If still broken, add console logging
git diff HEAD~1
# Add: console.log('Context value:', useAuth())
# Rebuild and check browser console
```

#### Recovery: Data Model Mismatch

```bash
# Error: POST /api/users failed - validation error

# 1. Check API contract vs client
# Get API error response
curl -X POST http://localhost:3000/api/users -H "Content-Type: application/json" -d '{"name":"Test"}'

# 2. Compare to what client is sending
grep -r "POST /api/users" src/

# 3. Check the type definition
cat src/types/User.ts

# 4. Options:
#    a) Update client to match API expectations
#    b) Update API validation to match client
#    c) Add migration to handle old format

# Option A: Update client
git diff HEAD~1 -- src/api/users.ts
# Check POST payload matches API schema
vim src/api/users.ts
npm test  # verify with API

# Option B: Update API
# Contact backend team to align

# Option C: Gradual migration
# Support both old and new formats
```

---

## Part 7: The Complete Recovery Workflow

### 7.1 When Verification Fails: Step-by-Step

```
VERIFICATION FAILED
│
├─ STEP 1: Document the failure
│  └─ What exactly failed? (test, build, visual, runtime)
│
├─ STEP 2: Capture evidence
│  ├─ Screenshot of error
│  ├─ Browser console output
│  ├─ Build log
│  └─ Test output
│
├─ STEP 3: Identify the breaking change
│  ├─ Run: git diff HEAD~1
│  ├─ Or run: git log --oneline -5
│  └─ Or use: git bisect for unknown change
│
├─ STEP 4: Decide: Rollback or Fix?
│  ├─ If fix is obvious (typo, small logic error) → FIX
│  ├─ If fix requires rethinking architecture → ROLLBACK
│  └─ If unsure → ROLLBACK first, then reapproach
│
├─ STEP 5A: Rollback path
│  ├─ git reset --hard HEAD~1 (if local)
│  ├─ git revert HEAD (if already pushed to shared branch)
│  └─ Verify rollback works: npm test && npm run build
│  └─ Commit rollback if using revert
│  └─ DONE, or restart with smaller change
│
├─ STEP 5B: Fix path
│  ├─ Understand root cause thoroughly
│  ├─ Make minimal fix (one file, one logic change)
│  ├─ Verify fix: npm test && npm run build
│  ├─ Test in browser if UI involved
│  ├─ Commit: git add . && git commit -m "fix: ..."
│  └─ DONE
│
└─ STEP 6: Analysis for future prevention
   └─ Did this reveal a gap in testing?
   └─ Should verification checklist be expanded?
   └─ Was change too large?
```

### 7.2 Example Recovery Scenario

**Scenario: Added new route, app won't compile**

```
FAILURE: "npm run build" fails with:
  Error: /Users/user/project/src/routes/index.ts:15
  Cannot find module './user-profile'

STEP 1: Document
  - Build fails, TypeScript compilation error
  - Route import is broken

STEP 2: Capture
  - Error: Cannot find module './user-profile'
  - File location: src/routes/index.ts

STEP 3: Identify change
  $ git diff HEAD~1

  +import UserProfile from './user-profile';
  +export const userRoute = {
  +  path: '/user',
  +  component: UserProfile
  +};

STEP 4: Decide
  - The file './user-profile' doesn't exist
  - Options:
    a) File was supposed to be created but wasn't
    b) File path is wrong
    c) Component not exported properly

STEP 5A: Quick assessment
  $ ls -la src/routes/user-profile*
  # File doesn't exist

  # Check if it's in different location
  $ find src -name "*profile*"
  src/components/UserProfile.tsx

STEP 5B: Fix
  # Update import path
  vim src/routes/index.ts

  # Change from:
  # import UserProfile from './user-profile';
  # To:
  # import UserProfile from '../components/UserProfile';

  $ npm run build  # verify
  $ npm test       # verify

  $ git add src/routes/index.ts
  $ git commit -m "fix: Correct import path for UserProfile in routes"

STEP 6: Test
  $ npm run dev
  # Navigate to /user route
  # Verify page renders correctly
```

### 7.3 Example: Catastrophic Failure Requiring Rollback

**Scenario: Refactored component tree, multiple cascading failures**

```
FAILURE: After refactoring Auth component:
  - 3 tests failing
  - 2 TypeScript errors
  - Visual regression: buttons invisible
  - Browser console: "useAuth is not defined" error

STEP 1: Document
  - Multiple failures across tests, types, and UI
  - Suggests structural change broke multiple systems

STEP 2: Assess fix complexity
  - 3 tests to fix
  - 2 types to fix
  - 1 visual bug
  - 1 runtime error
  - Total: 6-8 things to fix separately
  - Fix time: ~1 hour if each fix is simple, could be much longer

DECISION: Rollback is better than fix
  - Change was too large (too many side effects)
  - Suggests we should have made smaller incremental changes
  - Rollback, then redo with atomic commits

STEP 5: Rollback
  $ git reset --hard HEAD~1

  # Verify rollback worked
  $ npm test       # Should pass
  $ npm run build  # Should succeed
  $ npm run dev    # Should work in browser

  # Commit the rollback (if on shared branch)
  $ git log --oneline -1
  # Already rolled back in working directory

STEP 6: Replan
  The original change involved:
  1. Renaming useAuthContext to useAuth
  2. Moving auth.ts to services/auth.ts
  3. Changing Provider from AuthProvider to AuthContextProvider
  4. Refactoring AuthContext.ts structure

  BETTER approach:
  1. Rename useAuthContext → useAuth (test, commit)
  2. Move auth.ts to services/ (test, commit)
  3. Rename Provider (test, commit)
  4. Refactor AuthContext structure (test, commit)

  RESTART: git checkout -b feature/auth-refactor-v2
  # Make change #1, verify, commit
  # Make change #2, verify, commit
  # ... etc
```

---

## Part 8: Emergency Procedures

### 8.1 Complete Rollback to Known Good Commit

```bash
# Find the commit hash you want to rollback to
git log --oneline | head -20

# Example: abc123 "feat: Add user auth" was the last good commit

# Option 1: Soft rollback (keep changes in working directory)
git reset --soft abc123

# Option 2: Mixed rollback (changes stay, unstaged)
git reset --mixed abc123

# Option 3: Hard rollback (discard all changes, danger!)
git reset --hard abc123

# Verify you're at the right place
git log --oneline -1
git status

# If on a shared branch, use revert instead of reset
git revert HEAD~3..HEAD  # Creates new commits that undo the changes
```

### 8.2 Recovering Deleted Commits

```bash
# You accidentally did: git reset --hard HEAD~5

# Use git reflog to see recent HEAD movements
git reflog

# Example output:
# abc1234 HEAD@{0}: reset: moving to HEAD~5
# def5678 HEAD@{1}: commit: last real commit
# ghi9012 HEAD@{2}: commit: previous commit

# Recover the commit you deleted
git reset --hard def5678

# Or create a new branch from the old commit
git checkout -b recovery-branch def5678
```

### 8.3 Partial Rollback: Specific Files Only

```bash
# You want to keep most of your changes, but revert one file

# Revert a single file to previous version
git checkout HEAD~1 -- src/components/Auth.tsx

# This brings the old version into your working directory
git status  # shows Auth.tsx as modified

# Verify it looks correct
git diff src/components/Auth.tsx

# Commit the revert
git add src/components/Auth.tsx
git commit -m "fix: Revert Auth.tsx to previous version"

# Revert multiple files
git checkout HEAD~3 -- src/api/ src/types/
git status
git commit -m "fix: Revert API and type changes from 3 commits ago"
```

### 8.4 Database Migration Rollback

From [Database rollback strategies](https://www.liquibase.com/blog/database-rollbacks-the-devops-approach-to-rolling-back-and-fixing-forward):

**Safe migration practices:**

```sql
-- Always write reversible migrations
-- Forward migration (create new column)
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20);

-- Reverse migration (drop column) - MUST be in separate file or marked
ALTER TABLE users DROP COLUMN phone_number;

-- OR: use nullable columns with defaults (safer)
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) DEFAULT NULL;
-- To undo: ALTER TABLE users DROP COLUMN phone_number;
```

**Rollback procedure:**

```bash
# If migration tool supports rollback (Flyway, Liquibase, etc)
npm run migrate:rollback

# If manual, execute the DOWN script
psql -U user -d database -f migrations/002-revert-phone-number.sql

# Verify the schema
SELECT column_name FROM information_schema.columns WHERE table_name='users';

# Rebuild your TypeScript types to match
npm run generate:types
npm test  # verify app still works with old schema
```

### 8.5 Config File Recovery

```bash
# Config accidentally changed and broke the app

# Check what changed
git diff src/config.ts

# Option 1: Revert the config file
git checkout HEAD~1 -- src/config.ts
git add src/config.ts
git commit -m "fix: Revert config changes"

# Option 2: Restore from backup
cp /backup/config.ts.backup src/config.ts
git add src/config.ts
git commit -m "fix: Restore config from backup"

# Verify app works
npm test
npm run build
npm run dev
```

### 8.6 When to Abort and Ask for Help

**Stop development and ask the user if:**

1. **The breaking change affects multiple systems**
   - "This breaks auth, state management, and routes"
   - Suggests fundamental architecture issue
   - User decision needed on best approach

2. **Recovery requires decisions outside your scope**
   - "Fixing this requires choosing between 3 different architectures"
   - Present options, get user input

3. **You're going in circles**
   - Made 3 attempts to fix, each reveals new issues
   - May indicate misunderstanding of requirements
   - Ask user to clarify intended behavior

4. **Breaking change affects production data**
   - Migration deleted critical data
   - User must restore from backup and decide path forward

5. **Rollback reveals that spec was misunderstood**
   - "After rollback, I realize the original request meant something different"
   - Clarify requirements before restarting

**Template for escalation:**

```
## Verification Failed - Need User Guidance

**What broke:** [description]

**Root cause:** [what changed]

**Option A:** [Fix approach with time estimate]
**Option B:** [Alternative fix approach with time estimate]
**Option C:** [Rollback completely, restart with different design]

**Recommendation:** [Your professional assessment]

**Request:** Which option would you prefer?
```

---

## Part 9: The "Undo Stack" Pattern

### 9.1 Structuring Changes for Reversibility

Every change must be independently reversible. Structure your commits as:

```
Each commit = one logical, reversible change

Example for "Add User Dashboard":

✓ Commit 1: "feat: Create Dashboard component skeleton"
  - New file: src/components/Dashboard.tsx
  - Renders empty div
  - Reversible: git revert <hash>

✓ Commit 2: "feat: Add Dashboard route"
  - Modified: src/routes/index.ts
  - Added: { path: '/dashboard', component: Dashboard }
  - Reversible: git revert <hash>

✓ Commit 3: "feat: Fetch user data in Dashboard"
  - Modified: src/components/Dashboard.tsx
  - Added: useEffect with API call
  - Reversible: git revert <hash>

✓ Commit 4: "feat: Display user stats in Dashboard"
  - Modified: src/components/Dashboard.tsx
  - Added: JSX to display stats
  - Reversible: git revert <hash>

✓ Commit 5: "style: Add Dashboard styling"
  - Modified: src/components/Dashboard.css
  - Added: CSS for layout, colors
  - Reversible: git revert <hash>

If commit #4 breaks visual regression, only revert that commit:
git revert <hash-of-commit-4>

Commits #1, #2, #3, #5 remain intact.
```

### 9.2 Maintaining a Change Manifest

Keep a record of all changes:

```markdown
## Change Log for Feature: User Dashboard

### Overview
Adding a new Dashboard page showing user statistics and activity.

### Known Good Baseline
- Commit: abc123def456
- Date: 2024-01-15
- All tests passing: ✓
- Build size: 1.2MB

### Changes Made

#### Phase 1: Component Structure
- **Commit:** 123abc
- **Files Changed:**
  - NEW: src/components/Dashboard.tsx (empty skeleton)
- **What It Does:** Creates basic Dashboard component
- **Tests:** Component renders without error
- **Status:** ✓ Verified

#### Phase 2: Routing
- **Commit:** 456def
- **Files Changed:**
  - MODIFIED: src/routes/index.ts
- **What It Does:** Adds /dashboard route
- **Tests:** Route accessible, component renders
- **Status:** ✓ Verified

#### Phase 3: Data Loading
- **Commit:** 789ghi
- **Files Changed:**
  - MODIFIED: src/components/Dashboard.tsx (added useEffect)
  - MODIFIED: src/api/dashboard.ts (new endpoints)
- **What It Does:** Fetches user stats from API
- **Tests:** API call mocked, data loads correctly
- **Status:** ✓ Verified

#### Phase 4: UI Display
- **Commit:** 012jkl
- **Files Changed:**
  - MODIFIED: src/components/Dashboard.tsx (added JSX)
- **What It Does:** Renders stats, charts, tables
- **Tests:** All stats display, no console errors
- **Status:** ✓ Verified

#### Phase 5: Styling
- **Commit:** 345mno
- **Files Changed:**
  - NEW: src/components/Dashboard.css
- **What It Does:** Responsive layout, color scheme
- **Tests:** Mobile responsive, desktop layout correct
- **Status:** ✓ Verified

### Recovery Procedures

| Failure | Rollback Command | Rationale |
|---------|------------------|-----------|
| Styling broken | `git revert 345mno` | Only styling affected |
| Stats not displaying | `git revert 012jkl` | JSX change broke display |
| Data not loading | `git revert 789ghi` | API integration issue |
| Route not working | `git revert 456def` | Routing configuration |
| Whole feature broken | `git reset --hard abc123def456` | Return to known good |
```

---

## Part 10: Quick Reference Guide

### 10.1 Common Commands

```bash
# ===== BEFORE STARTING =====
git status                    # Clean working directory?
git log --oneline -1          # What's the current state?

# ===== DURING DEVELOPMENT =====
git add src/file.ts           # Stage specific file
git commit -m "feat: ..."     # Commit one logical change
git diff                      # What's changed before committing?
git diff HEAD~1               # What changed in last commit?

# ===== TESTING =====
npm test                      # Run tests
npm run build                 # Run build
npm run dev                   # Test in browser

# ===== IF SOMETHING BREAKS =====
git log --oneline -5          # See recent commits
git show HEAD                 # What's in the current commit?
git diff HEAD~1               # What changed?

# ===== ROLLING BACK =====
git reset --hard HEAD~1       # Hard rollback (local only!)
git revert HEAD~1             # Safe rollback (for shared branches)
git checkout HEAD~1 -- file.ts # Restore one file

# ===== FINDING THE CULPRIT =====
git bisect start              # Start binary search
git bisect bad                # Mark current as bad
git bisect good <hash>        # Mark known good
git bisect good/bad           # Mark each midpoint
git bisect reset              # Exit bisect

# ===== RECOVERY =====
git reflog                    # See all recent movements
git reset --hard <hash>       # Recover a deleted commit
git stash                     # Save work temporarily
git stash pop                 # Get work back
```

### 10.2 Decision Matrix

| Situation | Command | When |
|-----------|---------|------|
| Latest commit broke it (local) | `git reset --hard HEAD~1` | Not yet pushed |
| Latest commit broke shared branch | `git revert HEAD~1` | Already merged to main |
| Multiple commits broke it | `git bisect` | Don't know which commit |
| Want to undo commit but keep edits | `git reset --soft HEAD~1` | Will recommit differently |
| Want to discard all edits completely | `git checkout .` | Everything is broken |
| Accidentally deleted commits | `git reflog` then `git reset --hard <hash>` | Hopefully recent |
| Want to keep most, revert one file | `git checkout HEAD~1 -- file.ts` | Only one file wrong |
| Want to apply one commit to another branch | `git cherry-pick <hash>` | Selective copy |
| Want to save work without committing | `git stash` | Need to switch branches |

### 10.3 Mental Model: The Three Trees

Git has three "trees" that reset/checkout manipulate:

```
┌─────────────────────────────────────────────┐
│              Git Workflow                    │
├─────────────────────────────────────────────┤
│                                              │
│  Working Directory (your actual files)      │
│  ↓ git add
│  Staging Area (ready to commit)             │
│  ↓ git commit
│  Repository (committed history)             │
│                                              │
└─────────────────────────────────────────────┘
```

| Command | Working Dir | Staging | Repository |
|---------|-------------|---------|------------|
| `git reset --soft` | No change | No change | Move HEAD |
| `git reset --mixed` | No change | Clear | Move HEAD |
| `git reset --hard` | Clear | Clear | Move HEAD |
| `git checkout <file>` | Restore from staging | No change | No change |
| `git checkout HEAD <file>` | Restore from repo | No change | No change |

---

## Part 11: Prevention Strategies

### 11.1 Commit Discipline

**Good commit practices prevent most recovery situations:**

```bash
# ✓ Good: Focused commit
git add src/auth.ts src/__tests__/auth.test.ts
git commit -m "feat: Add password reset functionality

- Implement resetPassword() function
- Add unit tests for password reset
- Includes email validation"

# ✗ Bad: Dump commit
git add .
git commit -m "updates"
# Now if something breaks, what changed?

# ✓ Good: Atomic: one feature per commit
# Commit 1: "feat: Create auth module"
# Commit 2: "feat: Add login page route"
# Commit 3: "feat: Connect UI to auth module"

# ✗ Bad: Monolithic: too much change
# Commit 1: "feat: Complete user authentication system"
# (includes 10 different changes)
```

### 11.2 Pre-Commit Verification Checklist

Before committing, verify:

```bash
# 1. Tests pass
npm test
# All tests passing? ✓

# 2. Build succeeds
npm run build
# No errors? ✓

# 3. Type check passes
npx tsc --noEmit
# No type errors? ✓

# 4. Code is formatted
npm run lint:fix
# Any linting issues? ✓

# 5. Changes are minimal
git diff --stat
# Only expected files changed? ✓

# 6. No commented code
git diff | grep "^+\s*//"
# Any suspicious patterns? ✓

# Then commit:
git add src/changed-file.ts
git commit -m "feat: Specific, descriptive message"
```

### 11.3 Branch Protection Rules

Set up git hooks to prevent bad commits:

```bash
# .git/hooks/pre-commit (prevents committing broken code)
#!/bin/bash
set -e
npm run build
npm test
echo "✓ Commit verified - tests passed"
```

### 11.4 Code Review Prevention

Automated checks catch errors before they reach main:

```yaml
# CI/CD pipeline verification (GitHub Actions example)
name: Verify

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm ci
      - run: npm run build  # Build check
      - run: npm test       # Test check
      - run: npm run lint   # Lint check
      - run: npm run type-check  # Type check
```

If any step fails, code cannot be merged.

---

## Part 12: Real-World Recovery Scenarios

### Scenario 1: "Oops, I committed the wrong code"

```
Situation:
- Committed code for Feature A
- Realized it was supposed to be Feature B
- Haven't pushed yet

Resolution:

# Option 1: Undo commit, start over
git reset --soft HEAD~1
# Changes still in working directory
# Now make the right changes and recommit

# Option 2: Amend the commit
git add .
git commit --amend -m "feat: Feature B instead of A"

# Verify
npm test && npm run build
```

### Scenario 2: "Main branch is broken, I need to fix it NOW"

```
Situation:
- Someone merged broken code to main
- Whole team is blocked
- Need quick rollback

Resolution:

# Find the breaking commit
git log --oneline main | head -10

# Identify it: e.g., "abc123 feat: Add new widget"

# Rollback using revert (safe for shared branch!)
git revert abc123

# This creates a new commit that undoes the change
# Push the revert
git push origin main

# Team can continue
# The original commit is still in history (good for audit trail)

# Later, can do: git revert abc123^
# to re-apply it after it's been fixed
```

### Scenario 3: "I don't know which of 50 commits broke the tests"

```
Situation:
- Tests passed 2 days ago
- Tests fail now
- Made many commits since

Resolution:

# Create a test script
cat > find-break.sh << 'EOF'
#!/bin/bash
npm test --bail
EOF

chmod +x find-break.sh

# Start bisect
git bisect start
git bisect bad HEAD
git bisect good HEAD~50  # good 50 commits ago

# Let bisect run automatically
git bisect run ./find-break.sh

# After ~6 steps: "abc123 is the first bad commit"
git show abc123
git bisect reset

# Fix or revert that commit
```

### Scenario 4: "Changed state management, broke everything"

```
Situation:
- Refactored Redux to Context
- 8 failing tests
- 5 components with console errors
- Visual regressions everywhere

Resolution:

# Assess: This is a cross-cutting change
# Fixing 8 tests + 5 components + visuals = many hours

# Rollback decision:
git reset --hard HEAD~1

# Verify working:
npm test     # ✓ All pass
npm run dev  # ✓ No console errors

# Replan with atomic approach:
git checkout -b feature/redux-to-context-v2

# Make smaller changes:
# 1. Create Context (test, commit)
# 2. Add Provider to App (test, commit)
# 3. Migrate first consumer component (test, commit)
# 4. Migrate second consumer (test, commit)
# ... etc

# Much safer than all-at-once refactor
```

### Scenario 5: "Delete a file by mistake, need it back"

```
Situation:
- rm src/utils/helpers.ts
- Didn't git add it yet
- Oops!

Resolution:

# Option 1: If file is in git
git checkout HEAD -- src/utils/helpers.ts

# Option 2: If file was in previous commits
git checkout HEAD~5 -- src/utils/helpers.ts

# Option 3: Look in reflog
git reflog
git show <hash>:src/utils/helpers.ts > /tmp/helpers.ts
# Review /tmp/helpers.ts then move it back
```

---

## Part 13: Checklists for Workflow-Guardian

### Pre-Implementation Checklist

- [ ] Latest main branch pulled
- [ ] All tests passing in current state
- [ ] Build succeeds with no errors
- [ ] Working directory is clean (`git status` shows clean)
- [ ] Create feature branch if major change
- [ ] Document baseline (commit hash, test results, screenshots)
- [ ] Have a clear plan for atomic changes

### Per-Commit Checklist

- [ ] Made only ONE logical change
- [ ] Tests pass for this change (`npm test`)
- [ ] Build succeeds (`npm run build`)
- [ ] Type checking passes (`npx tsc --noEmit`)
- [ ] No console errors in browser
- [ ] Code is formatted and linted
- [ ] Commit message is clear and descriptive
- [ ] Ready to commit with `git commit`

### Post-Merge Checklist

- [ ] All tests pass
- [ ] Build succeeds
- [ ] Pushed to origin
- [ ] PR merged (if applicable)
- [ ] Feature branch cleaned up
- [ ] Feature works end-to-end in browser

### Verification Failure Checklist

- [ ] Documented what failed (test, build, runtime, visual)
- [ ] Captured error messages and screenshots
- [ ] Ran `git diff HEAD~1` to see what changed
- [ ] Identified root cause
- [ ] Decided: Fix or Rollback?
- [ ] If rolling back: `git reset --hard HEAD~1`
- [ ] If fixing: Made minimal fix, verified
- [ ] Tests pass after recovery
- [ ] Build succeeds after recovery
- [ ] Committed recovery (if using revert)

---

## References

**Git Fundamentals:**
- [Atomic commits best practices](https://gitbybit.com/gitopedia/best-practices/atomic-commits)
- [Git Reset documentation](https://git-scm.com/docs/git-reset)
- [Git Revert documentation](https://git-scm.com/docs/git-revert)
- [Git Stash best practices](https://opensource.com/article/21/4/git-stash)
- [Git Cherry-Pick documentation](https://git-scm.com/docs/git-cherry-pick)

**Advanced Recovery:**
- [Git Bisect guide - binary search for broken commits](https://www.metaltoad.com/blog/beginners-guide-git-bisect-process-elimination)
- [How to rollback Git changes safely](https://labex.io/tutorials/git-how-to-rollback-git-changes-safely-418148)
- [Git reset --soft vs --mixed vs --hard](https://www.geeksforgeeks.org/git/whats-the-difference-between-git-reset-mixed-soft-and-hard/)

**Testing and Verification:**
- [Baseline testing strategies](https://www.geeksforgeeks.org/software-testing/baseline-testing/)
- [Baseline testing best practices](https://www.virtuosoqa.com/post/baseline-testing)
- [TypeScript compilation error debugging](https://www.webdevtutor.net/blog/typescript-fail-test)

**Database Safety:**
- [Database rollback strategies in DevOps](https://www.liquibase.com/blog/database-rollbacks-the-devops-approach-to-rolling-back-and-fixing-forward)
- [Reversible database migrations with pgroll](https://xata.io/blog/pgroll-schema-migrations-postgres)
- [PlanetScale zero-downtime schema reverts](https://planetscale.com/blog/behind-the-scenes-how-schema-reverts-work)

---

## Summary

The most critical principle for workflow-guardian's rollback and recovery strategy:

**Make changes incrementally. Commit frequently. Verify after each change. Design every change to be independently reversible.**

This means:
1. One logical change per commit
2. Clear commit messages
3. Atomic commits (not bundled changes)
4. Feature branches for major work
5. Verify before committing
6. When something breaks, you can precisely identify and fix/rollback one piece at a time

This transforms the problem from "Something broke, I need to debug 50 commits" to "Change #7 broke something, revert it and try differently."

---

**Document Version:** 1.0
**Last Updated:** 2026-02-26
**For:** workflow-guardian Phase 4 (Verification) & Phase 5 (Recovery)
