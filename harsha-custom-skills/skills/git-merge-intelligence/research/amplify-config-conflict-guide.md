# AWS Amplify Configuration Conflict Patterns: Comprehensive Research Guide

**Research Date:** April 2026
**Scope:** Amplify Gen 1 & Gen 2, Hosting & Backend Configuration
**Focus Areas:** amplify.yml structure, backend configuration, environment variables, conflict resolution strategies

---

## Table of Contents

1. [amplify.yml Structure and Conflict Patterns](#amplifyml-structure-and-conflict-patterns)
2. [amplify.yml Specific Gotchas](#amplifyml-specific-gotchas)
3. [Amplify Backend Conflicts](#amplify-backend-conflicts)
4. [Environment Variable Conflicts](#environment-variable-conflicts)
5. [Resolution Strategies](#resolution-strategies)
6. [Common Deployment Failures After Merge](#common-deployment-failures-after-merge)
7. [References and Sources](#references-and-sources)

---

## 1. amplify.yml Structure and Conflict Patterns

### 1.1 Build Phases Overview

The `amplify.yml` file is the build specification file that defines how AWS Amplify Hosting builds and deploys your application. It uses YAML syntax and includes sections for `version`, `env`, `backend`, `frontend`, and `test`.

**Three core build phases execute in sequence:**

#### **preBuild Phase**
- Runs **before** the actual build starts, but **after** Amplify installs dependencies
- Typical use: environment setup, custom dependency installation, configuration preparation
- **Conflict Pattern:** Two branches adding different preBuild scripts without proper merging can cause one script to overwrite the other
- **Example conflict scenario:** Feature branch runs custom setup script; main branch adds dependency checks—merged result only includes one
- **Impact:** Missing build dependencies, configuration not applied, build artifacts in wrong state

#### **build Phase**
- Runs compile/transpilation steps
- Typical use: running `npm run build`, `yarn build`, `next build`, etc.
- **Conflict Pattern:** Both branches change the build command or add different build flags
- **Example conflict:** Main branch: `npm run build`, Feature branch: `npm run build -- --legacy-deps` → Both need to be reconciled
- **Impact:** Wrong build output, missing optimizations, incorrect artifacts directory

#### **postBuild Phase**
- Runs **after** build completes and Amplify copies artifacts to output directory
- Typical use: post-processing, notification, cleanup, test execution
- **Conflict Pattern:** Multiple branches adding test commands, notifications, or cleanup scripts
- **Impact:** Tests don't run, notifications fail, artifacts get corrupted/deleted

### 1.2 Environment Variable Blocks

Environment variables in `amplify.yml` can be defined in multiple places, creating conflict-prone scenarios:

```yaml
env:
  variables:
    API_ENDPOINT: https://api.example.com
    LOG_LEVEL: INFO
```

**Safe vs Unsafe Resolutions:**

| Scenario | Safe Resolution | Unsafe Resolution |
|----------|-----------------|-------------------|
| Different env vars per branch | Merge both sets; override duplicate keys only | Keep only one set, losing branch-specific vars |
| Same var, different values | Define branch-specific overrides in Amplify Console | Hardcode value in amplify.yml |
| Build-time vs runtime vars | Use Amplify's env var system for both | Mix env vars between different runtime contexts |
| Sensitive values | Use Amplify Console for secrets, not amplify.yml | Commit sensitive values in YAML file |

**Key gotcha:** Environment variables defined in `customHeaders` section of amplify.yml are NOT interpolated—they're treated as literal strings. Use variables only in build phases, not in header definitions.

### 1.3 Redirect Rules and Ordering Sensitivity

Redirect and rewrite rules must be ordered carefully because Amplify processes them top-to-bottom and stops at the first match.

**Example conflict scenario:**
```yaml
# Branch A
rewrites:
  - source: /api/<*>
    target: /index.html
    status: 200

# Branch B
rewrites:
  - source: /api/v2/<*>
    target: https://apiv2.example.com
    status: 200
```

**What happens on merge:** If Branch A's broader `/api/<*>` rule comes first, Branch B's `/api/v2/<*>` rule never executes—the v2 requests get rewritten to index.html instead.

**Ordering sensitivity rules:**
- More specific patterns must come BEFORE more general patterns
- Exact paths before wildcards
- Single-level paths before multi-level paths
- API routes before catch-all static routes

**Common merge failure:** Opposite ordering between branches causes silent failures where some routes no longer work.

### 1.4 Custom Headers (CSP, CORS) and Conflicting Blocks

Custom headers enable security policies and cross-origin access control.

**Structure:**
```yaml
customHeaders:
  - pattern: /api/*
    headers:
      - key: Access-Control-Allow-Origin
        value: https://example.com
      - key: Content-Security-Policy
        value: "default-src 'self'; script-src 'self' 'unsafe-inline'"
```

**How Amplify interprets conflicts:**

1. **Duplicate patterns:** Last one wins (no merge, last definition overwrites)
2. **Same header in different patterns:** Both apply (no conflict at definition level)
3. **Conflicting header values:** Only the last pattern's header is used
4. **Multiple origins in CORS:** Amplify static headers cannot use comma-separated lists—only one origin per header block

**Conflict patterns:**
- Branch A: Restrictive CSP (`default-src 'self'`)
- Branch B: Permissive CSP (`default-src *`)
- Merged result: Branch B's permissive policy overwrites Branch A's security

**Critical gotcha:** You cannot dynamically add multiple origins to CORS headers in static Amplify configuration. If you need multiple origins, you must either:
1. Use a Lambda@Edge function to handle dynamic CORS
2. Use one origin per environment
3. Handle CORS in application code

**AWS recommendations:** Migrate custom headers from amplify.yml to separate `customHttp.yml` file to reduce merge conflicts and simplify version control.

### 1.5 Cache Configuration

Cache paths specify which directories to preserve between builds, reducing build time.

```yaml
cache:
  paths:
    - node_modules/**/*
    - .next/cache/**/*
    - build/**/*
```

**Conflict scenarios:**
- Branch A caches `node_modules/**/*` for faster builds
- Branch B adds cache for `.cache/` directory for different tooling
- Merge creates longer cache paths list (no true conflict, but can cause cache size issues)

**Real problem:** Conflicting baseDirectory + cache paths:
```yaml
artifacts:
  baseDirectory: dist
cache:
  paths:
    - dist/**/*  # ← PROBLEM: trying to cache the build output
```

**Impact:** Build artifacts get cached but shouldn't be—next build reuses stale artifacts, causing deployment of old code.

### 1.6 Build Artifacts Specification

The `artifacts` section tells Amplify where build output lives:

```yaml
artifacts:
  baseDirectory: dist
  files:
    - '**/*'
  name: BuildArtifacts
```

**Conflict patterns:**
- Branch A: `baseDirectory: build` (Create React App default)
- Branch B: `baseDirectory: dist` (Vite default)
- Merged result: Amplify looks in wrong directory, finds no artifacts → blank site/404 errors

**Critical gotchas:**
1. **Wrong baseDirectory:** Most common cause of "blank site deployed" after merge
   - Amplify can't find built files
   - No error shown in build logs; deployment appears successful
   - Site shows 404 for all routes

2. **Absolute paths:** Amplify doesn't allow traversing outside project root
   - Absolute path like `/home/user/dist` gets silently ignored
   - Build appears successful but artifacts aren't included
   - Difficult to debug

3. **Missing baseDirectory:** If both branches omit it, default is repository root—likely wrong

4. **Dynamic baseDirectory:** Some monorepo setups need different baseDirectory per package
   - Merge conflicts when both branches modify monorepo structure
   - One branch's `baseDirectory: packages/web/dist` conflicts with another's
   - Must coordinate in merge resolution

---

## 2. amplify.yml Specific Gotchas

### 2.1 YAML Indentation Sensitivity

YAML is strict about indentation. A common mistake causes silent failures:

```yaml
# WRONG - missing colon after 'build'
phases:
  build
    commands:
      - npm run build

# CORRECT
phases:
  build:
    commands:
      - npm run build
```

**Merge conflict gotcha:** Conflict markers can misalign indentation:
```yaml
phases:
  preBuild:
<<<<<<< HEAD
    commands:
      - echo "Installing deps"
      - npm install
=======
    commands:
      - npm ci
>>>>>>> feature/branch
  build:
    commands:
      - npm run build
```

After manual resolution, indentation may be wrong, causing YAML parse errors.

**Resolution:** Always validate YAML syntax after merging. Use online YAML linters or:
```bash
python -m yaml amplify.yml
```

### 2.2 Environment-Specific Overrides

Amplify supports two mechanisms for environment-specific (dev/prod) configuration:

#### **Mechanism 1: Amplify Console Branch Overrides**
- Configure in Amplify Console UI under App Settings → Environment Variables
- Can set branch-specific overrides per variable
- **Pro:** Doesn't cause merge conflicts, cleaner git history
- **Con:** Configuration lives outside version control

#### **Mechanism 2: amplify.yml Conditional Logic**
```yaml
phases:
  preBuild:
    commands:
      - if [ "$AWS_BRANCH" == "production" ]; then cp .env.prod .env; fi
      - if [ "$AWS_BRANCH" == "dev" ]; then cp .env.dev .env; fi
```

**Merge conflict:** Different branches add different conditions:
```yaml
# Branch A adds
- if [ "$AWS_BRANCH" == "staging" ]; then npm run build:staging; fi

# Branch B adds
- if [ "$AWS_BRANCH" == "production" ]; then npm run build:prod; fi
```

Safe merge: Both conditions can coexist, but must maintain correct indentation and syntax.

### 2.3 Branch-Specific Build Settings

Amplify applies build settings to **all branches** unless an `amplify.yml` exists in the repository. When multiple branches modify `amplify.yml`:

**Scenario 1: Different frameworks per branch**
- Main branch: React (uses `build` command)
- Feature branch: Migrating to Next.js (uses `next build` command)
- After merge: Which command runs? → The merged amplify.yml determines it

**Scenario 2: Temporary feature branch configuration**
- Feature branch adds experimental build flag: `npm run build -- --experimental`
- Main branch doesn't have this flag
- If feature branch gets merged first, experimental flag becomes default

**Best practice:** Keep amplify.yml consistent across branches. Use branch-specific variables in Amplify Console instead.

### 2.4 When Both Branches Modify the Same Phase

This is the most dangerous merge scenario:

```yaml
# ORIGINAL
phases:
  build:
    commands:
      - npm run build

# Branch A (adds linting)
phases:
  build:
    commands:
      - npm run lint
      - npm run build

# Branch B (adds bundle analysis)
phases:
  build:
    commands:
      - npm run build
      - npm run analyze
```

**Three-way merge result (automatic):**
```yaml
phases:
  build:
    commands:
      - npm run lint
      - npm run build
      - npm run analyze
```

**Is this safe?** Depends on command dependencies:
- If `analyze` depends on `build` completing first: ✓ Safe
- If `lint` is slow and should be optional: ✗ Might slow down all builds
- If `analyze` requires intermediate artifacts from `build`: ✓ Safe

**Manual review required for every multi-branch modification to same phase.**

---

## 3. Amplify Backend Conflicts

### 3.1 amplify/backend Configuration Changes

Amplify backend resources (API, Database, Auth, Functions) are defined in `amplify/backend/` directory.

**File structure prone to conflicts:**
```
amplify/
├── backend/
│   ├── backend-config.json          ← Metadata about all resources
│   ├── api/
│   │   └── [apiname]/
│   │       ├── schema.graphql
│   │       ├── parameters.json
│   │       ├── transform.conf.json
│   ├── function/
│   │   └── [functionname]/
│   │       ├── src/
│   │       ├── parameters.json
│   │       ├── amplify.state
│   ├── auth/
│   └── storage/
```

**Common conflicts:**

1. **backend-config.json conflicts**
   - When one branch creates new resource, another modifies existing
   - Example:
     ```json
     // Branch A adds new API
     {
       "api": {
         "existing-api": {...},
         "new-api": {...}  // Added by Branch A
       }
     }

     // Branch B modifies auth
     {
       "auth": {
         "resource": {...}  // Modified by Branch B
       }
     }
     ```
   - Merge is straightforward if modifying different resources
   - Complex if both branches modify same resource (e.g., both change Auth config)

2. **Function parameter conflicts**
   - `amplify/backend/function/[name]/parameters.json` tracks Lambda layer dependencies
   - When both branches add Lambda layers:
     ```json
     // Branch A
     {
       "env": "dev",
       "lambdaLayers": ["layer-a"]
     }

     // Branch B
     {
       "env": "dev",
       "lambdaLayers": ["layer-b"]
     }
     ```
   - Three-way merge can't intelligently combine array items
   - Manual merge needed: `"lambdaLayers": ["layer-a", "layer-b"]`

3. **Unmanaged changes causing conflicts**
   - CloudFormation resources modified outside Amplify (via AWS Console)
   - Example: Cognito user pool manually updated
   - Next `amplify push` sees discrepancy, can't automatically resolve
   - Error: "Auth Cloudformation Template is out of sync with actual Cognito Resource"

### 3.2 CloudFormation Template Conflicts

Amplify auto-generates CloudFormation templates in `amplify/backend/[category]/[resource]/cloudformation-template.json`.

**These files should NOT be committed to git** because they're regenerated on `amplify push`. However, when they are committed and both branches modify resources:

```json
// Branch A modifies API schema
{
  "Resources": {
    "GraphQLAPI": {
      "Properties": {
        "Name": "api-with-new-type"
      }
    }
  }
}

// Branch B adds Lambda to API
{
  "Resources": {
    "GraphQLAPI": {
      "Properties": {
        "Name": "api"
      }
    },
    "LambdaDataSource": {
      "Type": "AWS::AppSync::DataSource"
    }
  }
}
```

**After merge:** Conflict markers in CloudFormation JSON. Resolving them by hand is error-prone because:
- JSON structure must remain valid
- Resource dependencies must be preserved
- References like `!Ref` and `!GetAtt` can be split by conflict markers

**Best practice:** Delete CloudFormation templates from git and regenerate on each push.

### 3.3 Function Configuration Conflicts

Lambda functions defined in `amplify/backend/function/[name]/` experience conflicts when:

1. **Different branches add same environment variable to same function**
   - Branch A: `DB_PASSWORD=secret`
   - Branch B: `DB_PASSWORD=different-secret`
   - Merge creates conflict in `.env` or `parameters.json`

2. **Both branches update Lambda layer references**
   - Branch A: Adds utility layer
   - Branch B: Upgrades existing layer to new version
   - Conflict in `parameters.json` lambdaLayers array

3. **Function code changes in incompatible ways**
   - Branch A: Changes function signature (parameters)
   - Branch B: Changes return type
   - Both modifying `index.js` → git conflict in source code
   - Compounded by Amplify's tracking of function state

### 3.4 API Schema Conflicts (GraphQL)

GraphQL schema defined in `amplify/backend/api/[apiname]/schema.graphql` is particularly conflict-prone:

```graphql
# Branch A adds a new type
type Product @model {
  id: ID!
  name: String!
}

# Branch B modifies User type
type User @model {
  id: ID!
  email: String!
  role: String  # Branch B adds this field
}
```

**Safe merge:** Both branches modify different types → straightforward merge.

**Unsafe merge scenarios:**

1. **Same type modified differently**
   ```graphql
   # Branch A
   type Post @model {
     id: ID!
     title: String!
     content: String! @auth(rules: [{allow: owner}])  # Branch A adds auth
   }

   # Branch B
   type Post @model {
     id: ID!
     title: String!
     content: String! @search  # Branch B makes searchable
   }
   ```
   - Merge conflict in schema
   - If resolved incorrectly, one directive lost
   - Missing `@auth` = security issue; missing `@search` = feature gone

2. **Directive conflicts**
   - Branch A: Adds `@auth(rules: ...)`
   - Branch B: Adds `@function` to same field
   - After merge: Both directives present but may not be intended

3. **Schema version drift**
   - Branch A: Modifies schema, deploys (CloudFormation updated)
   - Branch B: Works from old schema version
   - Merge happens after Branch A deployed
   - `amplify push` from Branch B detects schema mismatch
   - Error: "Pushing stale GraphQL schema"

**Resolution:** Regenerate from Amplify Console if schema becomes out of sync.

---

## 4. Environment Variable Conflicts

### 4.1 When Both Branches Add Different Env Vars

**Scenario:**
```bash
# Branch A
AWS_BRANCH=main → REACT_APP_API_URL=https://api-prod.com

# Branch B
AWS_BRANCH=develop → REACT_APP_API_URL=https://api-dev.com
```

**Git conflict in `.env` file (if committed):**
```
<<<<<<< HEAD
REACT_APP_API_URL=https://api-prod.com
REACT_APP_LOG_LEVEL=error
=======
REACT_APP_API_URL=https://api-dev.com
REACT_APP_LOG_LEVEL=debug
>>>>>>> feature/dev-env
```

**Safe resolution:** Merge both sets and use branch-specific logic:
```bash
if [ "$AWS_BRANCH" = "main" ]; then
  REACT_APP_API_URL=https://api-prod.com
else
  REACT_APP_API_URL=https://api-dev.com
fi
```

**Or better:** Use Amplify Console branch overrides instead of committing `.env` files.

### 4.2 Secret Management Conflicts

Amplify supports secrets in two ways:

1. **Amplify Console environment variables** (secure, not in git)
2. **Committed .env files** (DANGER: secrets in git history)

**Conflict pattern:**
- Branch A: Commits `.env` with database password
- Branch B: Adds API key to `.env`
- After merge: Both secrets in `.env` file
- Even after deletion from repo, secrets remain in git history

**Safe approach:**
- Never commit `.env` files with secrets
- Use `.env.example` template with placeholder values
- Use Amplify Console or AWS Secrets Manager for actual values
- Resolve merge conflicts in `.env.example`, not `.env`

### 4.3 Build-Time vs Runtime Env Var Confusion

**Build-time variables** (embedded during build):
```javascript
// Built at compile time
const API_URL = process.env.REACT_APP_API_URL;
```

**Runtime variables** (read when app loads):
```javascript
// Read at runtime
const API_URL = window.__ENV__.API_URL;
```

**Conflict scenario:**
```yaml
# Branch A: React app expecting build-time vars
env:
  variables:
    REACT_APP_API_URL: https://api.example.com

# Branch B: Next.js SSR expecting runtime vars available to Lambda
env:
  variables:
    API_URL: https://api.example.com  # ← Different name, used at runtime
```

After merge, one branch's vars are ignored because they're not in the right format for that branch's runtime.

**Reality check:** Next.js SSR environment variables require special handling because Lambda functions execute server-side code and need variables different from client-side code.

**Safe approach:**
- Document which vars are build-time vs runtime
- Use clear naming: `REACT_APP_*` for React build-time, `NEXT_PUBLIC_*` for Next.js client
- Use Amplify Console to manage both sets

---

## 5. Resolution Strategies

### 5.1 amplify.yml: Regenerate Rather Than Manually Merge

**The gold standard approach:**

When amplify.yml has complex conflicts across multiple sections:

1. **Identify what changed in each branch**
   ```bash
   git show Branch-A:amplify.yml > amplify-a.yml
   git show Branch-B:amplify.yml > amplify-b.yml
   diff amplify-a.yml amplify-b.yml
   ```

2. **Download the version from Amplify Console**
   - Go to App Settings → Build settings
   - Download the current amplify.yml
   - This version is known to be syntactically valid

3. **Manually apply intentional changes from each branch**
   ```bash
   # Don't merge conflict markers; instead:
   # 1. Start with console version
   # 2. Add changes from Branch A that make sense
   # 3. Add changes from Branch B that make sense
   # 4. Test locally before pushing
   ```

4. **Validate YAML syntax**
   ```bash
   python -m yaml amplify.yml
   # or online at https://www.yamllint.com/
   ```

5. **Test build configuration locally**
   - Run build commands locally to verify
   - Check that artifacts appear in expected directory
   - Verify environment variables are present

### 5.2 Validation: amplify push --check and Dry-Run Approaches

**Amplify CLI does NOT have a native `--check` or `--dry-run` flag** for `amplify push`. However, alternatives exist:

#### **Manual Validation Steps:**

1. **Syntax validation**
   ```bash
   amplify status  # Shows if config is parseable
   ```

2. **Local testing**
   ```bash
   npm run build  # Run build locally
   # Check that artifacts are in the correct baseDirectory
   ls dist/       # Or whatever baseDirectory is set to
   ```

3. **Environment variable verification**
   ```bash
   # Verify all required env vars are set
   printenv | grep REACT_APP_
   # or
   set | grep AWS_
   ```

4. **Mock/local development**
   ```bash
   # For backend changes, use local mocking
   amplify mock api      # Local AppSync development
   amplify mock function # Local Lambda testing
   ```

5. **Create preview before pushing**
   - Use Amplify Console pull request previews
   - Deploy to a temporary branch first
   - Verify behavior in staging environment

#### **Why no native dry-run?**
- CloudFormation does support change sets, but Amplify abstracts away direct CF management
- Feature has been requested (GitHub issue #366 in amplify-cli) but not yet implemented
- Amplify's approach is to use branch deployments for validation instead

### 5.3 Testing Build Configurations Locally Before Pushing

**Comprehensive local validation process:**

```bash
#!/bin/bash
# Pre-push validation script

set -e  # Exit on first error

echo "1. Validating amplify.yml syntax..."
python -m yaml amplify.yml || exit 1

echo "2. Checking environment variables..."
if [ -f .env ]; then
  source .env
fi
echo "   Expected vars: REACT_APP_API_URL, REACT_APP_ENV"
[ ! -z "$REACT_APP_API_URL" ] || echo "WARNING: REACT_APP_API_URL not set"

echo "3. Running build locally..."
npm install
npm run build

echo "4. Verifying artifacts..."
if [ ! -d "dist" ]; then
  echo "ERROR: dist directory not found!"
  exit 1
fi

if [ ! -f "dist/index.html" ]; then
  echo "ERROR: dist/index.html not found!"
  exit 1
fi

echo "5. Checking artifact size (rough sanity check)..."
SIZE=$(du -sh dist | awk '{print $1}')
echo "   Build artifact size: $SIZE"

echo "6. Validating redirect rules..."
# If using customHttp.yml, validate path patterns
if [ -f "customHttp.yml" ]; then
  python -m yaml customHttp.yml || exit 1
fi

echo "✓ All checks passed! Safe to push."
```

**Key validations before push:**

| Validation | Command | Why |
|-----------|---------|-----|
| YAML syntax | `python -m yaml amplify.yml` | Catches indentation/formatting errors |
| Build success | `npm run build` | Catches missing dependencies, wrong build script |
| Artifacts exist | `ls [baseDirectory]` | Catches wrong baseDirectory |
| Key files present | `test -f [baseDirectory]/index.html` | Verifies build completed |
| Environment variables | `printenv \| grep REACT_APP_` | Catches missing required vars |
| Redirect patterns | `grep -r "source:" customHttp.yml` | Validates glob syntax |

---

## 6. Common Amplify Deployment Failures After Merge

### 6.1 Build Script Errors

**Symptom:** Build phase fails with command not found or syntax error.

**Common causes after merge:**

1. **Conflicting build commands**
   ```bash
   # Branch A: npm
   npm run build

   # Branch B: yarn
   yarn build

   # Merged result: Both commands present, first one fails if yarn not installed
   ```

2. **Missing build phase entirely**
   - `preBuild` installs dependencies but `build` phase empty
   - Merge accidentally deleted build command

3. **Script references wrong package manager**
   ```bash
   # Changed from npm to yarn mid-project
   npm ci  # But package-lock.json says npm
   # vs
   yarn install  # But yarn.lock not committed
   ```

**Resolution:**
```bash
# Check what's actually in amplify.yml
cat amplify.yml | grep -A 5 "build:"

# Run the build locally to verify
npm run build 2>&1

# Check if lock files are consistent
ls package-lock.json yarn.lock
```

### 6.2 Missing Environment Variables

**Symptom:** Build succeeds but app crashes at runtime with "env var undefined" errors.

**Causes after merge:**

1. **Env var defined in one branch, not the other**
   ```bash
   # Branch A sets REACT_APP_API_URL in Amplify Console
   # Branch B doesn't know about this, build works locally but fails in Amplify
   ```

2. **Branch-specific override lost during merge**
   - Console override for dev branch deleted
   - Merge resolved conflict by keeping only main branch setting

3. **Wrong environment variable scope**
   ```yaml
   # set in preBuild (build-time)
   - export REACT_APP_VAR=value

   # But app expects it in customHeaders (doesn't work, headers aren't interpolated)
   ```

**Debugging steps:**
```bash
# In Amplify Console, check actual build logs
# Search for "environment" in logs

# Verify variables are set in your branch override
# App Settings → Environment Variables → Check branch override

# Verify variable is used correctly
grep -r "process.env.REACT_APP_" src/
```

### 6.3 Wrong Redirect Ordering

**Symptom:** Specific routes (like `/api/v2/*`) return wrong content (like serving index.html).

**Causes after merge:**

1. **Rewrite rules in wrong order**
   ```yaml
   rewrites:
     - source: /api/<*>
       target: /index.html
       status: 200
     - source: /api/v2/<*>
       target: https://apiv2.example.com
       status: 200
   ```
   First rule matches and rewrites all `/api/` requests, second rule never executes.

2. **Redirect conditions not honored**
   - Branch A: `source: ^/admin/.*` (regex, not glob)
   - Branch B: `source: /admin/<*>` (glob pattern)
   - Mixed after merge, some patterns interpreted incorrectly

3. **Lost redirect rule entirely**
   - One branch adds route, merge conflict not properly resolved
   - Deleted accidentally during conflict resolution

**Debugging:**
```bash
# Check the order in amplify.yml
cat amplify.yml | grep -A 20 "rewrites:"

# Test pattern matching locally
# /api/v2/users → Should match /api/v2/<*>, not /api/<*>

# Remember: Amplify uses glob patterns, not regex
# <*> matches one or more characters
# ** matches any depth
```

### 6.4 Cache Invalidation Issues

**Symptom:** Deployed app shows old code; hard refresh doesn't help; looks like stale cache.

**Causes after merge:**

1. **baseDirectory changed, causing old artifacts to be served**
   ```yaml
   # Old
   baseDirectory: build

   # New (after merge)
   baseDirectory: dist

   # Amplify still serves old build/ directory from cache
   ```

2. **Cache headers prevent new deployment from being served**
   ```yaml
   customHeaders:
     - pattern: '*'
       headers:
         - key: Cache-Control
           value: max-age=31536000  # One year!
   ```
   Browser cached old version, new version not fetched.

3. **Build artifacts path conflict**
   ```yaml
   cache:
     paths:
       - dist/**/*  # Caching build output (wrong!)
   artifacts:
     baseDirectory: dist
   ```
   Cached old `dist/`, new build doesn't overwrite cached version.

**Resolution:**
```bash
# 1. Verify correct baseDirectory
grep baseDirectory amplify.yml

# 2. Check cache paths don't include artifacts
grep -A 5 "cache:" amplify.yml

# 3. In Amplify Console: Hosting > All apps > App name
#    Click "Deployment history"
#    Full site cache → Clear cache

# 4. Hard refresh in browser
# Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### 6.5 Complete Checklist: Post-Merge Deployment Validation

Before deploying after a merge:

- [ ] **YAML Syntax:** `python -m yaml amplify.yml` passes
- [ ] **Build runs locally:** `npm run build` succeeds
- [ ] **Artifacts in correct dir:** `ls [baseDirectory]/index.html` exists
- [ ] **Environment variables set:** `echo $REACT_APP_VAR` shows correct value
- [ ] **Redirect rules ordered:** More specific patterns before general patterns
- [ ] **No hardcoded secrets:** `grep -r "password\|secret\|key" amplify.yml`
- [ ] **Backend resources:** `amplify status` shows no conflicts or drift
- [ ] **No cached artifacts:** Check `cache.paths` doesn't include `artifacts.baseDirectory`
- [ ] **Branch-specific overrides correct:** Verify in Amplify Console Environment Variables
- [ ] **Custom headers valid:** CSP, CORS headers syntactically correct
- [ ] **Function configs:** Any Lambda layer deps are present
- [ ] **GraphQL schema:** No conflicting directives (if using API)
- [ ] **git status clean:** `git status` shows no unresolved conflicts

---

## 7. References and Sources

### Official AWS Documentation

- [Build specification reference - AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/yml-specification-syntax.html) - Complete YAML structure specification
- [Configuring the build settings for an Amplify application](https://docs.aws.amazon.com/amplify/latest/userguide/build-settings.html) - Console-based configuration guidance
- [Setting custom headers - AWS Amplify Hosting](https://docs.aws.amazon.com/amplify/latest/userguide/setting-custom-headers.html) - Custom headers and redirects
- [Using environment variables in an Amplify application](https://docs.aws.amazon.com/amplify/latest/userguide/environment-variables.html) - Env var management
- [Editing the build specification](https://docs.aws.amazon.com/amplify/latest/userguide/edit-build-settings.html) - How to modify amplify.yml

### Community Resources and Guides

- [Amplify.yml Examples: The Complete Cookbook (2025 Edition)](https://awswithatiq.com/amplify-yml-examples-the-complete-cookbook-2025-edition/) - Practical amplify.yml patterns and examples
- [Mastering Deployment: Your Guide to Using amplify.yml for AWS Amplify & ReactJS](https://awswithatiq.com/mastering-deployment-your-guide-to-using-amplify-yml-for-aws-amplify-reactjs/) - Detailed deployment guide
- [How to Configure Amplify Redirects and Rewrites](https://oneuptime.com/blog/post/2026-02-12-configure-amplify-redirects-and-rewrites-/view) - Redirect and rewrite rules guide
- [How to Set Up Amplify Custom Headers and Cache Control](https://oneuptime.com/blog/post/2026-02-12-set-up-amplify-custom-headers-and-cache-control/view) - Cache and header configuration
- [How to Configure Amplify Branch-Based Deployments](https://oneuptime.com/blog/post/2026-02-12-configure-amplify-branch-based-deployments/view) - Multi-branch deployment strategies
- [How to Add Environment Variables to AWS Amplify for React/Node Apps](https://www.codestudy.net/blog/how-to-add-environment-variables-to-aws-amplify/) - Environment variable troubleshooting

### GitHub Issues and Community Reports

- [Merge conflicts with multi-env with amplify remove/update](https://github.com/aws-amplify/amplify-cli/issues/819) - Multi-environment merge conflicts
- [Repeated merge conflicts due to multi-env workflow](https://github.com/aws-amplify/amplify-cli/issues/1850) - Systematic merge conflict patterns
- [Consistent and extreme amount of git conflicts on merge](https://github.com/aws-amplify/amplify-cli/issues/7938) - Lambda layer conflict patterns
- [Different build command for different branch](https://github.com/aws-amplify/amplify-hosting/issues/3076) - Branch-specific build configuration
- [Cannot use environment variables in custom headers section](https://github.com/aws-amplify/amplify-hosting/issues/644) - Known limitation of headers section
- [Artifacts baseDirectory needs hardcoded path](https://github.com/aws-amplify/amplify-hosting/issues/582) - baseDirectory configuration issues
- [Custom Access-Control-Allow Headers not showing up](https://github.com/aws-amplify/amplify-hosting/issues/1563) - CORS header configuration problems
- [Amplify push dry run feature request](https://github.com/aws-amplify/amplify-cli/issues/366) - Request for dry-run capability
- [How to get CORS working?](https://github.com/aws-amplify/amplify-hosting/issues/3169) - CORS configuration troubleshooting

### API and Backend Configuration

- [Set up Amplify GraphQL API](https://docs.amplify.aws/gen1/javascript/build-a-backend/graphqlapi/set-up-graphql-api/) - GraphQL schema and API setup
- [Environment variables for Functions](https://docs.amplify.aws/cli/function/env-vars/) - Lambda function environment variable management
- [Troubleshooting - Amplify Docs](https://docs.amplify.aws/gen1/javascript/tools/cli/project/troubleshooting/) - General troubleshooting guide
- [Configuring monorepo build settings](https://docs.aws.amazon.com/amplify/latest/userguide/monorepo-configuration.html) - Monorepo-specific configuration

### Testing and Validation

- [Mocking and testing - Amplify Gen 1](https://docs.amplify.aws/gen1/react/tools/cli/usage/mock/) - Local testing with mock API
- [Setting up end-to-end Cypress tests](https://docs.aws.amazon.com/amplify/latest/userguide/running-tests.html) - Test phase configuration

---

## Appendix: Quick Reference Tables

### Conflict Severity Matrix

| Area | Severity | Detection | Recovery |
|------|----------|-----------|----------|
| Build command | Critical | Build fails immediately | Verify locally first |
| baseDirectory | Critical | Site blank/404s | Check artifacts exist locally |
| Redirect order | High | Specific routes fail silently | Review rule ordering |
| Env variables | High | Runtime errors | Check Amplify Console vars |
| YAML indentation | Critical | Parse error | Validate syntax online |
| Cache config | Medium | Stale content served | Clear cache in Console |
| Custom headers | Medium | CORS/CSP not applied | Verify syntax |
| Lambda layers | High | Deploy fails | Resolve array conflicts manually |

### When to Use Each Resolution Strategy

| Scenario | Strategy |
|----------|----------|
| Complex multi-section conflict | Regenerate from Amplify Console |
| Only env vars conflicted | Resolve in Amplify Console UI |
| Build phase conflict | Manual review, test locally |
| baseDirectory changed | Use console version as base |
| Redirect rules conflicted | Manual ordering review required |
| YAML syntax broken | Validate with linter, reformat |
| Multiple branches on one resource | Coordinate with team on intent |
| Automated conflict resolution | Run test suite before merge |

---

**Document Version:** 1.0
**Last Updated:** April 2026
**Research Scope:** Amplify CLI v7-v12, Amplify Hosting, Gen 1 & Gen 2
**Confidence Level:** High (based on official documentation and reported issues)
