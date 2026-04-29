# ESM and TypeScript Module Resolution Conflict Patterns

## Overview

This research covers conflict patterns that emerge during Git merges when branches diverge in ESM/CommonJS module systems, TypeScript configuration, and import path structures. These conflicts are particularly insidious because many are invisible to the TypeScript compiler but cause runtime failures.

---

## 1. ESM Fundamentals That Affect Merging

### 1.1 `"type": "module"` in package.json

Setting `"type": "module"` in package.json converts **all `.js` files in the package** to ESM, regardless of their extension. This is a binary toggle with significant consequences:

**Implications:**
- All `.js` files are executed as ESM (using the ESM module system)
- `require()` calls in those files will fail at runtime with `ERR_REQUIRE_NOT_SUPPORTED`
- Top-level `await` becomes available but makes the file async
- `import.meta` becomes available but `require` and `__dirname`/`__filename` disappear
- Default exports vs named exports change semantics
- Merge conflicts: If one branch adds `"type": "module"` but another adds CommonJS packages, both may be trying to use incompatible patterns

**Detection Pattern:**
```json
// package.json
{
  "type": "module",  // This line changes ALL .js interpretation
  "main": "./dist/index.js"
}
```

### 1.2 `.mjs` vs `.cjs` vs `.js` Extension Handling

Extension-based module determination provides explicit control:

| Extension | Module System | Notes |
|-----------|---------------|-------|
| `.mjs` | ESM (always) | Explicit, always parsed as ESM regardless of package.json |
| `.cjs` | CommonJS (always) | Explicit, always parsed as CommonJS regardless of package.json |
| `.js` | Determined by package.json `"type"` | If `"type": "module"`, parsed as ESM; otherwise CommonJS |
| `.ts` (pre-transpile) | Determined by tsconfig.json `"module"` | TypeScript setting determines output module type |

**Merge Conflict Scenario:**
- Branch A: Renames files from `.js` to `.mjs` for explicit ESM
- Branch B: Adds `"type": "module"` to package.json
- Merge: Conflict in intent—redundant `.mjs` files with `"type": "module"` setting

### 1.3 Named Exports vs Default Exports: Semantics Changes After Merge

ESM changes how exports work compared to CommonJS:

**CommonJS (single default export):**
```javascript
module.exports = { foo: 1, bar: 2 };
// Usage: const { foo, bar } = require('module');
```

**ESM with named exports (explicit exports):**
```javascript
export const foo = 1;
export const bar = 2;
// Usage: import { foo, bar } from 'module';
```

**ESM with default export (equivalent to CommonJS default):**
```javascript
export default { foo: 1, bar: 2 };
// Usage: import mod from 'module';
```

**Merge Conflict Risk:**
- Branch A refactors to named exports: `export const config = { ... }`
- Branch B refactors to default export: `export default { ... }`
- After merge: Import statements may use the wrong syntax, causing "export not found" errors invisible to tsc if not using strict module checking

### 1.4 `import.meta` vs `require` Conflicts

**`import.meta` (ESM only):**
```typescript
import.meta.url          // URL of current module
import.meta.main         // True if module is entry point
import.meta.resolve()    // Resolve specifier relative to current module
```

**`require` (CommonJS only):**
```javascript
require('module')
require.resolve('module')
module.exports = ...
__filename, __dirname    // Available in CommonJS only
```

**Conflict Pattern During Merge:**
- Branch A: Migrates to ESM, uses `import.meta.url` to construct file paths
- Branch B: Adds CommonJS utilities that use `require.resolve()`
- Merge: If the resolved code is ESM, `require.resolve()` is undefined. If resolved code is CommonJS, `import.meta` is undefined.
- **Runtime error**: `TypeError: Cannot read property 'url' of undefined` or `require is not defined`
- **Compiler doesn't catch**: These errors don't appear in `tsc` unless `--moduleResolution` is set correctly AND the code paths are analyzed

---

## 2. TypeScript moduleResolution Conflicts

### 2.1 `"bundler"` vs `"node16"` vs `"nodenext"` — Different Resolution Algorithms

TypeScript's `moduleResolution` setting fundamentally changes how imports are resolved:

#### `"node"` (legacy, deprecated)
- Oldest algorithm, doesn't understand `exports` field
- Will eventually be removed
- **Should not be used for new projects**

#### `"node16"`
- Understands Node.js v16+ module resolution rules
- Implements the full Node.js algorithm including `exports` field, conditional exports
- Requires `.js` extensions in ESM imports (even for `.ts` source files)
- Strict about module vs moduleResolution pairing: must use `"module": "es2022"` or higher with corresponding `"moduleResolution": "node16"`
- **Status**: Stable, recommended for Node.js libraries

#### `"nodenext"`
- Currently equivalent to `"node16"`
- Designed to be future-proof: will update when Node.js changes
- **Status**: Recommended for long-term Node.js compatibility; preferred over `"node16"`

#### `"bundler"`
- Designed for bundler-based projects (Vite, Next.js, Webpack, Esbuild)
- Understands `exports` and conditional exports like Node.js
- **Differs from node16/nodenext**: Does **not** require `.js` extensions in relative imports
- Assumes bundler will handle path resolution and module emission
- **Status**: Recommended for frontend and bundled applications

### 2.2 `.js` Extension Requirement in ESM Imports (Even for `.ts` Source Files)

This is a critical and confusing requirement:

**When using `"moduleResolution": "node16"` or `"nodenext"` in ESM mode:**

```typescript
// ❌ WRONG in node16/nodenext ESM
import { foo } from './utils';
import { bar } from '../lib/bar';

// ✅ CORRECT in node16/nodenext ESM
import { foo } from './utils.js';
import { bar } from '../lib/bar.js';
```

**Why:** Node.js ESM resolution requires explicit file extensions. Even though you're writing `.ts` source files, the TypeScript compiler respects Node.js's actual behavior: it won't magically find `utils.ts` when you write `import ... from './utils'`. The extension must be `.js` (the output file type), not `.ts`.

**When using `"moduleResolution": "bundler"`:**

```typescript
// ✅ ALSO CORRECT in bundler mode (no extension needed)
import { foo } from './utils';
```

**Merge Conflict Pattern:**
- Branch A: Written for `"moduleResolution": "bundler"`, imports without `.js` extensions
- Branch B: Migrated to `"moduleResolution": "node16"`, all imports have `.js` extensions
- Merge: Mixed imports cause tsc errors in node16/nodenext mode
- Resolution: Normalize all imports to one style, or ensure both branches use the same `moduleResolution`

### 2.3 Path Alias Conflicts (`@/*`, `~/`) — tsconfig paths vs vite resolve.alias

This is one of the most common merge conflicts in monorepos and bundler-based projects:

**tsconfig.json approach (TypeScript):**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
    }
  }
}
```

**vite.config.ts approach (Bundler):**
```typescript
export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      '@utils': fileURLToPath(new URL('./src/utils', import.meta.url))
    }
  }
});
```

**Merge Conflict Scenarios:**

1. **Configuration Divergence:**
   - Branch A: Adds new alias `@hooks/*` to tsconfig.json only
   - Branch B: Adds new alias `@styles/*` to vite.config.ts only
   - Result after merge: TypeScript knows `@hooks` but Vite doesn't know `@styles` (or vice versa)
   - Error: Vite bundling fails even though tsc passes

2. **Path Mismatch:**
   - Branch A: `"@/*": ["src/*"]`
   - Branch B: `"@/*": ["app/*"]`
   - After merge: One branch's imports resolve to wrong directory
   - Runtime: Module loads wrong implementation

3. **Wildcard Pattern Conflict:**
   - tsconfig uses `@/*` pattern with wildcard
   - vite uses explicit path without wildcard
   - After merge: Partial alias coverage creates hard-to-debug import failures

**Solution Pattern:**
Use `vite-tsconfig-paths` plugin to auto-sync, or maintain single source of truth in tsconfig and reference it in vite.config.ts

### 2.4 `baseUrl` Conflicts

`baseUrl` in tsconfig.json changes how all relative imports are resolved:

```json
{
  "compilerOptions": {
    "baseUrl": ".",        // Current: resolve from project root
    "baseUrl": "src"       // Alternative: resolve from src/
  }
}
```

**Merge Conflict:**
- Branch A sets `"baseUrl": "."` and uses imports like `import { foo } from 'lib/utils'`
- Branch B sets `"baseUrl": "src"` and expects `import { foo } from 'lib/utils'` to resolve to `src/lib/utils`
- After merge: Same import path resolves to different files
- **Invisible to tsc if using loose checking**, but breaks at runtime if combined with path re-exports

---

## 3. Import Path Conflicts

### 3.1 Both Branches Reorganize File Structure → Import Paths Diverge

This is the structural merge conflict:

**Branch A refactors:**
```
src/
  utils.ts           (was: src/lib/utils.ts)
  components/
    Button.ts        (was: src/ui/Button.ts)
```

**Branch B refactors:**
```
src/
  helpers/
    index.ts         (new organization)
    string.ts
  features/
    Button/
      Button.tsx
      index.ts
```

**After merge:**
- Files from both branches exist in different locations
- Import statements on each branch point to old locations that no longer match
- Circular dependencies may be created by intermediate imports during reorganization
- Tree-shaking optimizations become ineffective because the bundler can't trace imports through reorganized structure

### 3.2 Barrel File (index.ts) Conflicts — Export Reorganization

Barrel files (`index.ts`) that re-export from multiple modules create complex merge conflicts:

**Branch A's index.ts:**
```typescript
export { Button } from './Button';
export { Input } from './Input';
export { Modal } from './Modal';
```

**Branch B's index.ts:**
```typescript
export { Button } from '../ui/Button';
export { Checkbox } from '../ui/Checkbox';
export { Select } from '../ui/Select';
```

**Merge Conflict Result:**
```typescript
export { Button } from './Button';        // Branch A
export { Input } from './Input';          // Branch A
export { Modal } from './Modal';          // Branch A
export { Button } from '../ui/Button';    // Branch B - DUPLICATE!
export { Checkbox } from '../ui/Checkbox';// Branch B
export { Select } from '../ui/Select';    // Branch B
```

**Issues:**
1. Duplicate exports cause TypeScript error if both Button implementations exist
2. Tree-shaking cannot optimize because barrel re-exports everything
3. Build time increases due to circular dependency analysis

### 3.3 Circular Dependency Introduction Through Merge

Merging changes from both branches can create circular dependencies that didn't exist before:

**Branch A introduces:**
```
src/
  hooks/
    useAuth.ts    (imports from useStorage)
  storage/
    useStorage.ts (no circular dependency yet)
```

**Branch B introduces:**
```
src/
  storage/
    useStorage.ts (now imports from hooks/useAuth for validation)
  hooks/
    useAuth.ts    (no circular dependency yet)
```

**After merge:** `hooks/useAuth` imports `storage/useStorage` which imports `hooks/useAuth` — circular!

**ESM specific issue:** ESM uses live bindings, so circular dependencies partially work but access to uninitialized bindings returns `undefined`, causing runtime errors invisible to tsc.

### 3.4 Tree-Shaking Implications of Import Changes

Tree-shaking effectiveness depends on static, analyzable import structure:

**Before merge (tree-shakable):**
```typescript
// index.ts
export { Button } from './Button';
export { Input } from './Input';

// app.ts
import { Button } from './index';
```

**After merge (tree-shaking breaks):**
```typescript
// index.ts - now has multiple sources
const Button = require('./Button');     // Branch A adds CommonJS
export { Button };

export { Input } from './Input';        // Branch B keeps ESM
```

**Result:** Bundler cannot determine statically which exports are safe to remove, so nothing is removed. Bundle size increases.

---

## 4. Runtime-Only Errors (Invisible to tsc)

### 4.1 Dynamic import() Conflicts

Dynamic imports behave differently between CommonJS and ESM:

**ESM dynamic import:**
```typescript
const module = await import('./dynamic.js');
// Returns: { default?, namedExport1?, namedExport2? }
```

**CommonJS require:**
```javascript
const module = require('./dynamic.js');
// Returns: module.exports object directly
```

**Merge Conflict Pattern:**
- Branch A: Uses dynamic imports with `.then()` for ESM
- Branch B: Uses dynamic imports expecting CommonJS-like behavior
- After merge: Same dynamic import path, different expectations
- tsc error: Invisible if using loose typing
- Runtime error: "Cannot read property 'default' of undefined"

### 4.2 Missing File Extension in ESM Mode

Node.js ESM requires explicit file extensions; omitting them causes runtime errors:

```typescript
// ESM mode, moduleResolution: node16
// ❌ Runtime error: ERR_MODULE_NOT_FOUND
import { foo } from './utils';

// ✅ Works
import { foo } from './utils.js';
```

**Merge Conflict:**
- Branch A wrote code without extensions (for bundler/browser environment)
- Branch B wrote code with extensions (for Node.js ESM)
- Merge: If project switches to Node.js ESM, Branch A's imports break
- tsc doesn't catch this if using `moduleResolution: bundler`

### 4.3 Top-Level Await Conflicts

Top-level `await` is ESM-only and causes conflicts when merged with CommonJS:

**ESM file with top-level await:**
```typescript
// db.ts (ESM)
const connection = await connectToDatabase();
export { connection };
```

**CommonJS file trying to require it:**
```javascript
// app.js (CommonJS)
const { connection } = require('./db.js');  // ❌ ERR_REQUIRE_ASYNC_MODULE
```

**Why:** CommonJS `require()` is synchronous; it cannot wait for ESM's top-level `await`. Node.js v20+ partially supports `require(esm)` but only if the ESM file has **no top-level await**.

**Merge Conflict Pattern:**
- Branch A: Migrates database module to ESM with top-level await for clean initialization
- Branch B: Keeps application in CommonJS, uses `require('./db')`
- After merge: Runtime error only when this code path executes
- tsc doesn't catch it (depends on target and moduleResolution)

### 4.4 JSON Import Assertion Changes

Node.js ESM requires import assertions for JSON files:

**Node.js 17.1+:**
```typescript
// ✅ Correct in ESM
import config from './config.json' assert { type: 'json' };

// ❌ Runtime error: ERR_IMPORT_ASSERTION_TYPE_MISSING
import config from './config.json';
```

**Merge Conflict:**
- Branch A: Written before Node 17, imports JSON without assertion
- Branch B: Updated to Node 17+, requires assertion
- After merge: Both patterns may coexist; one fails at runtime
- tsc error: Only if using `"module": "esnext"` or `"nodenext"`; invisible otherwise

---

## 5. package.json Conflict Patterns

### 5.1 `"type": "module"` vs `"type": "commonjs"` — Binary Toggle

`"type"` field is binary and changes all `.js` file interpretation:

```json
// Option A: All .js files are ESM
{ "type": "module" }

// Option B: All .js files are CommonJS (default if omitted)
{ "type": "commonjs" }
```

**Merge Conflict:**
- Branch A adds `"type": "module"` to migrate to ESM
- Branch B adds CommonJS packages/dependencies that expect CommonJS
- After merge: Both branches expect different module systems for same `.js` files
- Error: Most runtime errors only occur when the conflicted code path executes

**Detection:** Grep package.json for `"type"` field; if missing from merge, it defaults to CommonJS

### 5.2 `"exports"` Field Conflicts — Conditional Exports, Subpath Patterns

The `"exports"` field defines which entry points are available and can use conditional exports:

**Branch A exports:**
```json
{
  "exports": {
    ".": "./dist/index.js",
    "./utils": "./dist/utils.js"
  }
}
```

**Branch B exports:**
```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.js"
    },
    "./utils": {
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.js"
    }
  }
}
```

**After merge:** If both exist in conflict markers, one pattern is lost or both are present (invalid)

**Conditional Exports Pattern (Branch B more sophisticated):**
```json
{
  "exports": {
    ".": {
      "import": "./esm/index.js",
      "require": "./cjs/index.js",
      "types": "./dist/index.d.ts"
    }
  }
}
```

**Merge Issue:** Conditional exports prevent dual-package hazard (where same package runs in two different contexts with different code), but merging patterns from both branches can break the conditional logic.

### 5.3 `"main"` vs `"module"` vs `"exports"` Precedence

These three fields have different precedence and purpose:

| Field | Purpose | Precedence |
|-------|---------|-----------|
| `"main"` | Default CommonJS entry point | Used only if `"exports"` absent |
| `"module"` | ESM entry point (non-standard but widely used) | Used by bundlers; ignored by Node.js |
| `"exports"` | Specifies all available exports; supports conditions | Highest precedence in Node.js v12.7+ |

**Conflict Scenario:**
```json
{
  "main": "./dist/cjs/index.js",      // Branch A
  "module": "./dist/esm/index.js",    // Branch B adds this
  "exports": {                         // Branch B adds this too
    ".": "./dist/index.js"
  }
}
```

**Problem:**
- Different tools prioritize these fields differently
- `"exports"` overrides both `"main"` and `"module"` in Node.js
- Some build tools only read `"module"`
- Result: Different entry points loaded in different contexts

**Detection Pattern:**
After merge, check if `"exports"` field exists—if yes, `"main"` and `"module"` may be ignored and should be updated or removed

---

## 6. Resolution Strategies and Detection

### 6.1 How to Detect Module Resolution Issues After Merge

**Strategy 1: TypeScript Compiler Diagnostics**
```bash
npx tsc --noEmit --diagnostics
npx tsc --traceResolution 2>&1 | head -100
```

This shows exactly which paths TypeScript tried to resolve and where it succeeded/failed. Useful but only catches type-level issues.

**Strategy 2: ESLint Module Resolution Plugin**
```bash
npm install eslint-plugin-import
```

Configure to detect unresolved imports, missing extensions (for node16), and circular dependencies.

**Strategy 3: Runtime Execution Testing**
```bash
# Test actual module loading (before build)
node --input-type=module --eval "import('./src/index.js')"

# For CommonJS
node -e "require('./src/index.js')"
```

**Strategy 4: Package Export Validation**
```bash
# Verify exports field is valid
npm exec -c "package-exports-validator"

# Or manually test
node -e "console.log(require.resolve('your-package', { paths: ['.'] }))"
```

**Strategy 5: Static Analysis of Merged Code**
```bash
# Find all import statements and check consistency
grep -r "^import\|^export" src/ | sort | uniq -c
grep -r "require\|import.meta" src/ | sort | uniq -c
```

### 6.2 Tools: `tsc --traceResolution`, Node.js `--conditions` Flag

#### TypeScript's `--traceResolution` Flag

```bash
tsc --traceResolution > resolution-trace.txt 2>&1
```

**Output example:**
```
======== Resolving module './utils' from '/project/src/app.ts' ========
Using cached result from module name 'utils' found in 'node_modules/@types/utils', which has content: '/project/node_modules/@types/utils/index.d.ts'
======== Module name './utils' was successfully resolved to '/project/src/utils.ts' ========
```

**What it shows:**
- Every resolution attempt (tried path, why it was rejected or accepted)
- Which package.json fields were consulted
- Caching decisions
- Exact resolution time per module

**Use after merge to verify:**
- No conflicting resolutions for same import path
- All `baseUrl` and path aliases resolve correctly
- No circular dependency chains (if resolution attempts same module twice)

#### Node.js `--conditions` Flag

Controls which conditional exports are selected:

```bash
node --conditions=require ./app.js    # Use "require" condition
node --conditions=import ./app.js     # Use "import" condition (default for ESM)
```

**In package.json exports:**
```json
{
  "exports": {
    ".": {
      "require": "./dist/cjs/index.js",
      "import": "./dist/esm/index.js",
      "default": "./dist/index.js"
    }
  }
}
```

**Merge detection:** After merge, test both conditions:
```bash
node --conditions=require --input-type=module --eval "import('index.js')"
node --conditions=import --input-type=module --eval "import('index.js')"
```

If one condition's path doesn't exist, merge introduced a break.

### 6.3 When to Regenerate Lock Files (package-lock.json, pnpm-lock.yaml)

**Always regenerate lock files after module resolution changes:**

```bash
# npm
rm package-lock.json && npm install

# pnpm
rm pnpm-lock.yaml && pnpm install

# yarn
rm yarn.lock && yarn install
```

**Specific merge scenarios requiring lock file regeneration:**

1. **If package.json `"type"` field changed:** All dependencies need re-evaluation for ESM vs CommonJS compat
2. **If package.json `"exports"` field changed:** Entry points may resolve to different versions
3. **If tsconfig.json `"moduleResolution"` changed:** Type definitions resolution changes
4. **If `.npmrc` or similar configuration changed:** Resolution algorithm may differ

**Why:** Lock files cache resolution metadata. If resolution rules change, cached data becomes stale and causes inconsistent installs across machines.

**Validation after regeneration:**
```bash
npm list --depth=0      # Verify no duplicate versions
npm audit               # Check security
npm ls --omit=dev       # Verify production deps resolve
```

---

## 7. Merge Conflict Checklist and Patterns

### Pre-Merge Validation

**In the merge conflict resolution phase:**

- [ ] Check if `package.json` has conflicting `"type"` field
- [ ] Check if `tsconfig.json` has conflicting `"moduleResolution"` or `"module"` settings
- [ ] Check if both branches modified `package.json` `"exports"` field
- [ ] Verify no duplicate entries in barrel files (`index.ts`)
- [ ] Check for path alias conflicts between `tsconfig.json` and `vite.config.ts`
- [ ] Scan for conflicting imports of same module from different paths
- [ ] Test dynamic imports for `await` vs callback expectations
- [ ] Verify JSON imports have assertions if target is Node.js 17.1+
- [ ] Check for `.js` extension consistency in imports

### Post-Merge Validation

**After completing merge:**

```bash
# 1. Lint module resolution
npx tsc --noEmit
npx eslint --plugin import src/

# 2. Check for import inconsistencies
grep -r "from '[^.][^/]" src/ | head -20  # Unqualified imports
grep -r "assert {" src/                    # JSON import assertions

# 3. Verify exports
node --input-type=module --eval "import('./src/index.js').then(() => console.log('✓ ESM entry works'))"

# 4. Check package.json validity
npm exec -c "jq '.type, .main, .module, .exports' package.json"

# 5. Run type checking with diagnostics
tsc --traceResolution --noEmit 2>&1 | grep -i "conflict\|fail" | head -10

# 6. Test actual imports
node -e "console.log(Object.keys(require('./dist/index.js')))" 2>&1

# 7. Regenerate lock files
rm package-lock.json && npm install
```

### Common Merge Conflict Markers and What They Mean

**Conflicting module system declaration:**
```
<<<<<<< HEAD
"type": "module"
=======
"type": "commonjs"
>>>>>>> feature-branch
```
→ Decision: Which branch is the module system target? Affects all `.js` interpretation.

**Conflicting tsconfig moduleResolution:**
```
<<<<<<< HEAD
"moduleResolution": "bundler"
=======
"moduleResolution": "nodenext"
>>>>>>> feature-branch
```
→ Decision: Are you targeting a bundler or Node.js? Affects import extension requirements.

**Conflicting exports field:**
```
<<<<<<< HEAD
"exports": {
  ".": "./dist/index.js"
}
=======
"exports": {
  ".": {
    "import": "./dist/esm/index.js",
    "require": "./dist/cjs/index.js"
  }
}
>>>>>>> feature-branch
```
→ Decision: Are you supporting dual ESM/CommonJS? Merge should use the more complete (conditional) version.

**Conflicting import paths after file reorganization:**
```typescript
<<<<<<< HEAD
import { Button } from './ui/Button';
=======
import { Button } from '../components/Button';
>>>>>>> feature-branch
```
→ Decision: File exists in one location only after merge; use the actual new location, then update both imports.

---

## 8. Real-World Examples

### Example 1: ESM Migration Merge Conflict

**Branch A (ESM Migration):**
- Sets `"type": "module"` in package.json
- Changes all imports to include `.js` extensions
- Removes `require()` statements, replaces with `import`
- Uses `import.meta.url` for file paths

**Branch B (Feature Development):**
- Adds new CommonJS middleware
- Uses `require()` to load modules
- Adds JSON config imports without assertions
- Uses `__dirname` for path construction

**After merge:**
```json
// package.json - CONFLICT
<<<<<<< HEAD
"type": "module"
=======
"type": "commonjs"
>>>>>>> feature-branch
```

**Correct resolution:**
Choose one (`"type": "module"`), then:
1. Convert Branch B's middleware to ESM
2. Replace `__dirname` with `import.meta.url`
3. Add `.js` extensions to imports
4. Add `assert { type: 'json' }` to JSON imports
5. Test with `node --input-type=module`

### Example 2: Path Alias Desynchronization

**Branch A (tsconfig updates):**
```json
// tsconfig.json
"paths": {
  "@/*": ["src/*"],
  "@api/*": ["src/api/*"],
  "@styles/*": ["src/styles/*"]
}
```

**Branch B (Vite config updates):**
```typescript
// vite.config.ts
alias: {
  '@': './src',
  '@components': './src/components'
  // Missing @api and @styles!
}
```

**After merge:**
- tsc understands `@styles`, but Vite doesn't
- Vite build fails with "Failed to resolve" for `@styles` imports
- But tsc passes because it doesn't know what Vite understands

**Solution:**
1. Update both tsconfig and vite.config to have matching aliases
2. Or: Use `vite-tsconfig-paths` plugin to auto-sync

### Example 3: Circular Dependency Introduction

**Branch A (Utilities refactor):**
```typescript
// src/auth/useAuth.ts
import { validate } from '../validation';
export function useAuth() { ... }

// src/validation/index.ts
export function validate(data) { ... }
```

**Branch B (Storage integration):**
```typescript
// src/validation/index.ts (Branch B modifies it)
import { useAuth } from '../auth/useAuth';  // NEW: needs auth for validation

export function validate(data) {
  const auth = useAuth();
  // ...
}
```

**After merge:**
- `auth/useAuth` imports from `validation`
- `validation` imports from `auth/useAuth`
- Circular dependency created!

**In ESM:** When circular dependency is encountered, accessing the circular import returns `undefined` because the binding hasn't been initialized yet.

**Runtime error:**
```
TypeError: useAuth is not a function
  at Object.validate (validation/index.ts:2:12)
```

**Detection:** `tsc --traceResolution` shows circular resolution path, or use:
```bash
npx eslint --plugin import --rule import/no-cycle=error src/
```

**Solution:** Extract shared utilities into third module:
```typescript
// src/shared/validators.ts
export function validateUser(data) { ... }

// src/validation/index.ts
import { validateUser } from '../shared/validators';
export { validateUser as validate };

// src/auth/useAuth.ts (no dependency on validation anymore)
import { validateUser } from '../shared/validators';
```

---

## 9. TypeScript and Build Tool Integration

### ESM Module Configuration Matrix

| Setting | Value | Use Case | Notes |
|---------|-------|----------|-------|
| `"type"` | `"module"` | All `.js` files are ESM | package.json only |
| `"module"` | `"esnext"` / `"es2022"` | TypeScript output module format | tsconfig.json |
| `"moduleResolution"` | `"nodenext"` | Node.js library with ESM | tsconfig.json |
| `"moduleResolution"` | `"bundler"` | Frontend app with bundler | tsconfig.json |
| `"allowImportingTsExtensions"` | `true` | Allow `.ts` in imports (esbuild only) | tsconfig.json, rare |
| `"skipLibCheck"` | `true` | Skip type checking dependencies | tsconfig.json (can hide type conflicts) |

### Build Tool Configuration Priority

When merging, understand tool precedence:

1. **Node.js** reads `package.json` `"exports"` > `"main"`
2. **TypeScript** reads tsconfig.json settings > package.json
3. **Bundlers** (Vite, Webpack) read tsconfig.json paths + bundler config (may conflict)
4. **Type definitions** resolved via tsconfig.json `"types"` field and `@types` packages

### Validation Script (Post-Merge)

```bash
#!/bin/bash
set -e

echo "=== Module Resolution Merge Validation ==="

# Check package.json
echo "1. Checking package.json..."
if grep -q '"type"\s*:\s*"module"' package.json && grep -q '"type"\s*:\s*"commonjs"' package.json; then
    echo "ERROR: Conflicting type fields in package.json"
    exit 1
fi

# Check tsconfig.json
echo "2. Checking tsconfig.json..."
tsc --noEmit || exit 1

# Check module resolution
echo "3. Tracing module resolution..."
tsc --traceResolution --noEmit 2>&1 | grep -i "error" && exit 1 || true

# Check for import inconsistencies
echo "4. Checking import consistency..."
UNRESOLVED=$(grep -r "from '[^.]" src/ | grep -v "node_modules" | grep -v ".js'" | wc -l)
if [ $UNRESOLVED -gt 0 ]; then
    echo "WARNING: $UNRESOLVED imports without .js extension found"
fi

# Check exports field validity
echo "5. Validating exports field..."
node -e "
const pkg = require('./package.json');
if (pkg.exports) {
  if (typeof pkg.exports === 'string') {
    console.log('✓ Simple exports field valid');
  } else {
    const keys = Object.keys(pkg.exports);
    console.log(\`✓ Conditional exports with \${keys.length} conditions\`);
  }
}
" || echo "No exports field"

echo "=== All checks passed ==="
```

---

## 10. References and Further Reading

### Official Documentation
- [TypeScript: Modules - Choosing Compiler Options](https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html)
- [TypeScript: Modules - Theory](https://www.typescriptlang.org/docs/handbook/modules/theory.html)
- [TypeScript: Modules - ESM/CJS Interoperability](https://www.typescriptlang.org/docs/handbook/modules/appendices/esm-cjs-interop.html)
- [Node.js: Modules - Packages](https://nodejs.org/api/packages.html)
- [Node.js: Modules - ECMAScript modules](https://nodejs.org/api/esm.html)

### Advanced Topics
- [Andrew Branch: Is `nodenext` right for libraries that don't target Node.js?](https://blog.andrewbran.ch/is-nodenext-right-for-libraries-that-dont-target-node-js/)
- [TypeScript Issue: moduleResolution node16 conflicts with "type": "module" packages](https://github.com/microsoft/TypeScript/issues/53045)
- [Guide to the package.json `exports` field](https://hirok.io/posts/package-json-exports)
- [Dual package hazard](https://github.com/nodejs/modules/issues/409)

### Tree-Shaking and Bundling
- [Smashing Magazine: Tree-Shaking: A Reference Guide](https://www.smashingmagazine.com/2021/05/tree-shaking-reference-guide/)
- [Blog: My journey through the ESM Tree Shaking forest](https://blog.pixelastic.com/2025/01/14/journey-esm-tree-shaking/)

### Practical Guides
- [Node.js, TypeScript and ESM: it doesn't have to be painful](https://dev.to/a0viedo/nodejs-typescript-and-esm-it-doesnt-have-to-be-painful-438e)
- [NodeJS, Typescript, and the infuriating ESM errors](https://thedrlambda.medium.com/nodejs-typescript-and-the-infuriating-esm-errors-828b77e7ecd3)
- [Stop Struggling with Path Aliases in Vite + TypeScript + React](https://medium.com/@tusharupadhyay691/stop-struggling-with-path-aliases-in-vite-typescript-react-heres-the-ultimate-fix-1ce319eb77d0)
- [Fixing Circular Dependency Issues in JavaScript Modules](https://medium.com/@Adekola_Olawale/fixing-circular-dependency-issues-in-javascript-modules-24c953345520)

### Tools and Utilities
- [TypeScript: TSConfig Reference - traceResolution](https://www.typescriptlang.org/tsconfig/traceResolution.html)
- [TypeScript: TSConfig Reference - moduleResolution](https://www.typescriptlang.org/tsconfig/moduleResolution.html)
- [IanVS/ts-module-resolution-examples](https://github.com/IanVS/ts-module-resolution-examples)
- [vite-tsconfig-paths](https://www.npmjs.com/package/vite-tsconfig-paths)

---

## Conclusion

ESM and TypeScript module resolution conflicts during merges are particularly dangerous because many are invisible to the TypeScript compiler. The most critical safeguards are:

1. **Enforce consistent `"type"` and `"moduleResolution"` settings** across branches
2. **Synchronize path aliases** between tsconfig.json and bundler configuration
3. **Validate after merge** using both static analysis (`tsc`, `eslint-plugin-import`) and runtime testing
4. **Regenerate lock files** after any module resolution configuration changes
5. **Audit for circular dependencies**, top-level await, and dynamic import patterns
6. **Test both ESM and CommonJS paths** if supporting dual formats via conditional exports

A single missed conflict in module resolution can cause runtime failures that don't appear until specific code paths execute in production.
