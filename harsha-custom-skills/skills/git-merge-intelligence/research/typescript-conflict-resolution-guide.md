# TypeScript-Specific Merge Conflict Resolution: A Comprehensive Guide

## Executive Summary

TypeScript's advanced type system introduces a unique class of merge conflicts that differ fundamentally from regular JavaScript merges. While many conflicts appear syntactically valid and pass basic compilation checks, they can introduce subtle type errors, break type safety guarantees, and create runtime issues. This guide provides comprehensive strategies for identifying and resolving TypeScript-specific conflicts in TypeScript 5.x projects.

---

## Part 1: TypeScript 5.x Type System Features Creating Tricky Conflicts

TypeScript's sophisticated type system creates conflict scenarios that surface only during deeper type analysis. Understanding these features is essential for proper merge resolution.

### 1.1 Interface Extension vs Replacement

**The Problem:**
[Interfaces support declaration merging, which means you can define multiple interfaces with the same name, and TypeScript will merge them into a single interface with the combined properties and methods.](https://www.typescriptlang.org/docs/handbook/declaration-merging.html) When two branches extend the same interface differently, Git's three-way merge cannot understand the semantic intent.

**Conflict Scenario:**
```typescript
// Base version
interface User {
  id: string;
  name: string;
}

// Branch A: extends with admin properties
interface User {
  isAdmin: boolean;
  permissions: string[];
}

// Branch B: extends with profile properties
interface User {
  avatar: string;
  bio: string;
}
```

**Resolution Strategy:**
When both branches extend the same interface with different properties:
1. **Keep both merges** - TypeScript will automatically merge both declarations
2. Verify with `tsc --noEmit` that all properties coexist without conflicts
3. Be cautious when both branches add properties with the same name but different types - this causes a compile error

**What Not To Do:**
- Do NOT replace one interface extension with another
- Do NOT assume that last-edit-wins semantics apply (they don't for declaration merging)

**Validation:**
```bash
tsc --noEmit --strict
# Verify: "User interface combines properties from both branches"
```

---

### 1.2 Generic Constraints: Merging Code That Changes Type Parameters

**The Problem:**
Generic constraints use the `extends` keyword to restrict type parameters. When two branches modify constraint logic differently, the merged result may have incompatible constraints or circular dependencies.

**Conflict Scenario:**
```typescript
// Base
function merge<T extends object>(a: T, b: T): T {
  return { ...a, ...b };
}

// Branch A: adds property constraint
function merge<T extends { id: string }>(a: T, b: T): T {
  return { ...a, ...b };
}

// Branch B: adds different constraint
function merge<T extends { name: string }>(a: T, b: T): T {
  return { ...a, ...b };
}
```

**Resolution Strategy:**
1. Identify the actual intent of each constraint
2. Use intersection constraints if both are necessary: `<T extends { id: string } & { name: string }>`
3. Use conditional types to create branching logic based on constraint satisfaction
4. Test with concrete types to ensure the merged constraint works as intended

**Validation:**
```bash
# Test with concrete implementations
tsc --noEmit
# Verify: Function accepts objects that satisfy ALL constraints
```

**Key Insight:**
Generic constraints in git merges often represent incompatible design decisions. Consider:
- Are both constraints necessary?
- Can they be combined with intersection types?
- Should they be in separate overloads?

---

### 1.3 `as const` Patterns: Const Assertions and Type Narrowing

**The Problem:**
[`as const` assertions create immutable literal types from values, changing TypeScript's inference from general types to specific literal values.](https://blog.logrocket.com/complete-guide-const-assertions-typescript/) When two branches apply `as const` differently to the same values, type inference diverges.

**Conflict Scenario:**
```typescript
// Base
const STATUS = {
  active: 'active',
  inactive: 'inactive'
};

// Branch A: adds as const
const STATUS = {
  active: 'active',
  inactive: 'inactive'
} as const;

// Branch B: modifies to use enum
enum STATUS {
  ACTIVE = 'active',
  INACTIVE = 'inactive'
}
```

**The Issue:**
- With `as const`: properties are `readonly` and typed as literal values (`'active'`, not `string`)
- Without `as const`: properties are mutable and typed as `string`
- This affects type inference downstream and breaks type safety when merged incorrectly

**Resolution Strategy:**
1. **Prefer `as const` for constants** - it provides better type inference and prevents accidental mutations
2. Verify that all usages work with `readonly` properties
3. Check for discriminated union patterns that depend on literal types
4. Use `satisfies` (TS 4.9+) to validate the object structure while preserving literal types

**Best Practice:**
```typescript
// Resolved version - use as const for literal preservation
const STATUS = {
  active: 'active',
  inactive: 'inactive'
} as const;

type StatusType = typeof STATUS[keyof typeof STATUS]; // 'active' | 'inactive'
```

---

### 1.4 The `satisfies` Operator (TypeScript 4.9+)

**What It Does:**
[The `satisfies` operator validates that an expression matches a type without changing the inferred type.](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html) Unlike type assertions with `as`, it preserves literal types.

**How It Affects Merges:**
When merging code that uses `satisfies` differently, the type validation guarantees may diverge.

**Conflict Scenario:**
```typescript
// Base
const config = {
  port: 3000,
  host: 'localhost'
};

// Branch A: validates with satisfies
const config = {
  port: 3000,
  host: 'localhost'
} satisfies { port: number; host: string };

// Branch B: validates with explicit type
const config: { port: number; host: string } = {
  port: 3000,
  host: 'localhost'
};
```

**The Difference After Merge:**
- `satisfies`: Type of config is `{ port: 3000; host: 'localhost' }` (literal types preserved)
- Explicit type: Type of config is `{ port: number; host: string }` (widened types)

**Resolution Strategy:**
1. Prefer `satisfies` for configuration objects where literal types matter
2. Use explicit type annotations only when widening is intentional
3. Remember: `as const satisfies Type` first applies `as const`, then validates
4. Validate merged code with type inference checks:

```bash
tsc --noEmit
# Check: typeof config should be narrower type, not widened type
```

**Post-Merge Validation:**
```typescript
// Verify literal type preservation
const config = { port: 3000 } satisfies { port: number };
type ConfigType = typeof config; // { port: 3000 } not { port: number }
```

---

### 1.5 Discriminated Unions: Adding Different Discriminants in Branches

**The Problem:**
[Discriminated unions combine union types with literal types, using a shared literal property (discriminant) so TypeScript can narrow the union automatically.](https://medium.com/@s35919223/demystifying-discriminated-unions-in-typescript-ea3d6180b733) When branches add different discriminants to a union, type narrowing breaks.

**Conflict Scenario:**
```typescript
// Base
type Response =
  | { status: 'success'; data: unknown }
  | { status: 'error'; error: string };

// Branch A: adds a timestamp discriminant
type Response =
  | { status: 'success'; data: unknown; timestamp: number }
  | { status: 'error'; error: string; timestamp: number };

// Branch B: adds a requestId discriminant
type Response =
  | { status: 'success'; data: unknown; requestId: string }
  | { status: 'error'; error: string; requestId: string };
```

**Merged Result (Broken):**
```typescript
type Response =
  | { status: 'success'; data: unknown; timestamp: number; requestId: string }
  | { status: 'error'; error: string; timestamp: number; requestId: string };
```

This loses the semantic intent that both properties should be on all variants.

**Resolution Strategy:**
1. **Identify discriminant intent**: Is the property essential to distinguish types, or just metadata?
2. **Combine metadata properties**: Create a base type for common properties
3. **Preserve discriminant structure**:

```typescript
type Response =
  | {
      status: 'success';
      data: unknown;
      timestamp: number;
      requestId: string
    }
  | {
      status: 'error';
      error: string;
      timestamp: number;
      requestId: string
    };
```

4. **Test narrowing**:
```typescript
const handler = (response: Response) => {
  if (response.status === 'success') {
    // TypeScript should infer: { status: 'success'; data: unknown; ... }
    const data = response.data; // ✓ Available
  }
};
```

**Validation:**
```bash
tsc --noEmit --strict
# Verify: Type narrowing works correctly with the merged discriminant
```

---

### 1.6 Template Literal Types: Merging Type-Level String Manipulation

**The Problem:**
[Template literal types build on string literal types and expand into many strings via unions.](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html) When branches extend template literal types differently, type unions can explode or become incompatible.

**Conflict Scenario:**
```typescript
// Base
type HttpMethod = 'GET' | 'POST';
type Endpoint = `/${HttpMethod}`;

// Branch A: expands methods
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Endpoint = `/${HttpMethod}`;

// Branch B: expands pattern
type Endpoint = `/${HttpMethod}` | `/${HttpMethod}/:id`;
```

**Merged Result:**
```typescript
type Endpoint = 'GET' | 'POST' | 'PUT' | 'DELETE';
// Now Endpoint might be either `/GET` or `/PUT/:id`, but type is ambiguous
```

**Resolution Strategy:**
1. **Keep metadata and pattern separate**:
```typescript
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type EndpointPattern = `/${HttpMethod}` | `/${HttpMethod}/:id`;
```

2. **Expand unions carefully**: Verify the Cartesian product doesn't create unintended combinations
3. **Test type inference**:
```typescript
const endpoint: EndpointPattern = '/GET'; // ✓
const endpoint: EndpointPattern = '/GET/123'; // ✓
const endpoint: EndpointPattern = '/INVALID'; // ✗
```

4. **Validate with string pattern matching**:
```bash
tsc --noEmit --strict
# Verify: Template literal expansion creates expected union members
```

---

### 1.7 Conditional Types: Resolution When Both Branches Modify Logic

**The Problem:**
Conditional types enable type-level branching: `T extends Condition ? TrueType : FalseType`. When both branches modify the condition or result types, the merged logic may be contradictory.

**Conflict Scenario:**
```typescript
// Base
type IsString<T> = T extends string ? true : false;

// Branch A: adds null handling
type IsString<T> = T extends string | null ? true : false;

// Branch B: adds distribution over unions
type IsString<T> = T extends string[] ? false : T extends string ? true : false;
```

**Merged Conflict:**
The resolution becomes ambiguous - should null be treated as string-like? How should arrays be handled?

**Resolution Strategy:**
1. **Document the conditional's purpose**: What is it trying to determine?
2. **Establish clear precedence**: Order conditions from most specific to most general
3. **Use correct form**:
```typescript
// Correct: more specific conditions first
type IsString<T> = T extends string[] ? false
                 : T extends string | null ? true
                 : false;
```

4. **Test with diverse types**:
```typescript
type T1 = IsString<string>; // true
type T2 = IsString<string[]>; // false
type T3 = IsString<number>; // false
type T4 = IsString<null>; // true
```

5. **Watch for distributive conditional types**: When `T` is a union, conditional types distribute:
```typescript
type Result = IsString<string | number>;
// Equivalent to: IsString<string> | IsString<number> = true | false
```

---

## Part 2: What `tsc --noEmit` Catches vs. Doesn't Catch

### 2.1 What `tsc --noEmit` Catches

`tsc --noEmit` performs full type checking without emitting JavaScript files. It catches:

**✓ Type Errors:**
- Type mismatches in assignments
- Missing properties on objects
- Function argument type mismatches
- Incompatible interface implementations

**✓ Import/Export Issues:**
- Non-existent imports
- Missing export declarations
- Re-export inconsistencies

**✓ Generic Violations:**
- Generic constraints not satisfied
- Type parameter mismatches
- Incorrect generic bounds

**✓ Interface Mismatches:**
- Missing required properties
- Property type conflicts
- Invalid method signatures

**✓ Declaration Merging Conflicts:**
- Interface property type conflicts (when the same property is declared with different types)
- Enum member value collisions

**Example - Catches:**
```typescript
interface User { id: string; }
interface User { id: number; } // ✗ Error: Subsequent property declarations must have the same type

const user: User = { id: 123 }; // ✗ Error if id should be string
```

---

### 2.2 What `tsc --noEmit` Doesn't Catch

**✗ Runtime Behavior Changes:**
TypeScript removes types during compilation - it cannot verify runtime behavior. If a merge changes logic but preserves types, `tsc --noEmit` won't detect it.

**Example - Misses:**
```typescript
// Original
function calculatePrice(quantity: number): number {
  return quantity * 10;
}

// Merged (type-wise identical, logic broken)
function calculatePrice(quantity: number): number {
  return quantity * 5; // Wrong calculation, but types are still valid
}
```

**✗ Logic Errors Within Type-Safe Code:**
```typescript
// Type-safe but logically wrong
function processOrder(items: Order[]): boolean {
  return items.length === 0; // Should check items.length > 0
}
```

**✗ Incorrect Type Assertions (`as any`):**
[Type assertions bypass type checking. Using `as any` silences all type errors.](https://betterstack.com/community/guides/scaling-nodejs/type-assertions-casting/) If a merge introduces `as any` to hide a genuine type incompatibility, `tsc --noEmit` won't catch it.

```typescript
// Original
const data: string = getData();

// Merged with hidden issue
const data: string = (getData() as any) as string; // Hides real type problem
```

**✗ Dead Code Paths:**
Unreachable code won't be flagged unless explicitly enabled:
```typescript
function example(value: string | number): void {
  if (typeof value === 'string') {
    console.log(value.toUpperCase());
  } else if (typeof value === 'string') { // Dead condition, but valid syntax
    console.log(value.toLowerCase());
  }
}
```

**✗ Incomplete Type Coverage:**
Missing `case` statements in `switch` statements over unions won't be caught without exhaustiveness checking:
```typescript
type Action = 'CREATE' | 'UPDATE' | 'DELETE';

function handleAction(action: Action): void {
  switch (action) {
    case 'CREATE': break; // Missing UPDATE and DELETE cases
  }
}
```

---

### 2.3 Comparing `tsc --noEmit` vs `tsc --noEmit --strict`

**Standard `tsc --noEmit`:**
- Catches type incompatibilities
- Allows implicit `any` types
- Allows nullable value access without checks
- Permits `this` binding issues

**`tsc --noEmit --strict` enables:**
- `noImplicitAny`: Requires explicit types, no implicit `any`
- `strictNullChecks`: `null` and `undefined` are distinct types
- `strictFunctionTypes`: Stricter function parameter checking
- `strictBindCallApply`: Validates `bind`, `call`, `apply` correctly
- `strictPropertyInitialization`: Requires class properties to be initialized

**Impact on Merge Validation:**
Use `tsc --noEmit --strict` as your definitive validation tool. It catches:
- Missing null checks
- Implicit type widening
- Unsafe type coercions

```bash
# Standard check (less strict)
tsc --noEmit

# Thorough check (recommended for merge validation)
tsc --noEmit --strict
```

---

## Part 3: Common TypeScript Merge Conflict Patterns

### 3.1 Import Statement Conflicts

**Pattern:**
Both branches add different imports, causing Git to mark lines as conflicting.

**Conflict Example:**
```typescript
<<<<<<< HEAD
import { User } from './models/user';
import { validateUser } from './validators/user';
=======
import { User } from './models/user';
import { UserService } from './services';
>>>>>>> feature/new-service
```

**Resolution Strategy:**
1. **Keep all imports** - they serve different purposes
2. **Alphabetize** - maintain import order for consistency
3. **Group by source** - organize imports logically
4. **Validate imports exist**:

```bash
tsc --noEmit
# Verify: All imports resolve to actual modules
```

**Resolved:**
```typescript
import { User } from './models/user';
import { validateUser } from './validators/user';
import { UserService } from './services';
```

**Pitfall - Import Map Conflicts:**
When both branches change path aliases in `tsconfig.json`, the last one wins. Handle this in `tsconfig.json` conflicts (see Part 4).

---

### 3.2 Barrel File (index.ts) Conflicts

**Pattern:**
Export list diverges when both branches add or re-export different modules.

**Conflict Example - index.ts:**
```typescript
<<<<<<< HEAD
export { User } from './user';
export { Role } from './role';
export { validateUser } from './validators';
=======
export { User } from './user';
export { Permission } from './permission';
export { AuthService } from './services';
>>>>>>> feature/auth
```

**Problem with Barrel Files:**
[Barrel files (re-exporting from index.ts) can cause circular imports, tree-shaking issues, and performance problems.](https://tkdodo.eu/blog/please-stop-using-barrel-files) When merging, ensure:

1. **No circular imports**: Verify no module imports from the barrel file it's exported from
2. **Keep meaningful exports only**: Don't re-export everything
3. **Maintain order**: Group related exports together

**Resolution Strategy:**
1. **Keep all non-conflicting exports**
2. **Verify each export's source file exists**
3. **Check for circular dependencies**:

```bash
tsc --noEmit
# If errors appear about circular imports, review barrel structure
```

**Best Practice - Alternative to Barrel:**
For application code, avoid barrel files. Instead, import directly:
```typescript
// Instead of: import { User } from './models'
import { User } from './models/user'; // Direct import
```

---

### 3.3 Type Definition Conflicts

**Pattern:**
Both branches define the same type differently, and Git marks it as conflicting.

**Conflict Example:**
```typescript
<<<<<<< HEAD
type UserRole = 'admin' | 'user' | 'guest';
=======
type UserRole = {
  name: string;
  permissions: string[];
};
>>>>>>> feature/role-refactor
```

**Resolution Strategy:**
1. **Understand the semantic change**: Is this intentional refactoring or conflicting designs?
2. **If both are needed**, rename to distinguish intent:
```typescript
type UserRoleString = 'admin' | 'user' | 'guest';
type UserRoleObject = {
  name: string;
  permissions: string[];
};
```

3. **Update all usages**: Propagate the renamed type throughout the codebase
4. **Validate type safety**:

```bash
tsc --noEmit --strict
# Verify: All references use the correct type definition
```

---

### 3.4 Enum Member Conflicts

**Pattern:**
Both branches add enum members, potentially with overlapping values.

**Conflict Example:**
```typescript
enum Status {
<<<<<<< HEAD
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending',
=======
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  ARCHIVED = 'archived',
>>>>>>> feature/archive
}
```

**Key Rules from TypeScript:**
[When merging enums, only one declaration can omit an initializer for its first element.](https://bobbyhadz.com/blog/typescript-merge-2-enums) If both branches add members with the same value, TypeScript will error.

**Resolution Strategy:**
1. **Combine all members**:
```typescript
enum Status {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending',
  ARCHIVED = 'archived',
}
```

2. **Verify no duplicate values**:
```typescript
const values = Object.values(Status);
const uniqueValues = new Set(values);
// Ensure: uniqueValues.size === values.length
```

3. **Test enum usage**:
```bash
tsc --noEmit --strict
# Verify: All enum values are distinct and usable
```

---

### 3.5 Module Augmentation Conflicts

**Pattern:**
Both branches augment the same module, either merging declarations or overwriting them.

**Background:**
[Module augmentation means the compiler merges two separate declarations with the same name into a single definition.](https://www.typescriptlang.org/docs/handbook/declaration-merging.html) Conflicts occur when augmentations contradict each other.

**Conflict Example:**
```typescript
// Base: express.d.ts augmentation
declare global {
  namespace Express {
    interface Request {
      user?: User;
    }
  }
}

// Branch A: adds auth middleware type
declare global {
  namespace Express {
    interface Request {
      user?: User;
      isAuthenticated?: boolean;
    }
  }
}

// Branch B: adds request ID
declare global {
  namespace Express {
    interface Request {
      user?: User;
      requestId?: string;
    }
  }
}
```

**Resolution Strategy:**
1. **Ensure augmentation file is a module**: It must have an import to be treated as augmentation, not module declaration
2. **Combine interface declarations**: They will merge automatically
3. **Use interfaces, not type aliases**: [Interfaces are "open" and support declaration merging, while type aliases are "closed."](https://www.technetexperts.com/typescript-module-augmentation-fix/)

**Correct Merged Augmentation:**
```typescript
import 'express'; // Required to make this a module augmentation

declare global {
  namespace Express {
    interface Request {
      user?: User;
      isAuthenticated?: boolean;
      requestId?: string;
    }
  }
}
```

**Validation:**
```bash
tsc --noEmit --strict
# Verify: All augmented properties are available on the target type
```

---

## Part 4: tsconfig.json Conflict Patterns

### 4.1 compilerOptions Conflicts

**Pattern:**
Both branches change different compiler options, or the same option differently.

**Conflict Example:**
```json
{
  "compilerOptions": {
<<<<<<< HEAD
    "target": "ES2020",
    "module": "ESNext",
    "strict": true,
    "resolveJsonModule": true,
=======
    "target": "ES2019",
    "module": "commonjs",
    "strict": false,
    "noImplicitAny": true,
>>>>>>> feature/legacy-support
  }
}
```

**Resolution Strategy:**
1. **Understand the intent**: Why did each branch change these options?
2. **Determine the project's minimum target**: Use the most restrictive requirement
3. **Enable stricter checking incrementally**: Start with `strict: true`, then disable specific rules if needed

**Best Practice Resolution:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "strict": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

**Validation:**
```bash
tsc --noEmit
# Verify: All files compile successfully with the merged config
```

---

### 4.2 `paths` Alias Conflicts

**Pattern:**
Both branches define path aliases, and TypeScript's default behavior overwrites rather than merges.

**Conflict Example:**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
<<<<<<< HEAD
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"],
=======
      "@services/*": ["src/services/*"],
      "@api/*": ["src/api/*"],
>>>>>>> feature/new-modules
    }
  }
}
```

**The Problem:**
When a child `tsconfig.json` extends a base config, child paths completely override parent paths - they don't merge.

**Resolution Strategy:**
1. **Combine all paths in a single location**:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"],
      "@services/*": ["src/services/*"],
      "@api/*": ["src/api/*"]
    }
  }
}
```

2. **For monorepos**, define paths in `tsconfig.base.json`, not individual project configs
3. **Use consistent prefixes**: Establish a naming convention (`@` for internal paths)

**Validation:**
```bash
tsc --noEmit
# Verify: All path aliases resolve correctly
```

---

### 4.3 `include`/`exclude` Pattern Conflicts

**Pattern:**
Both branches modify which files TypeScript analyzes.

**Conflict Example:**
```json
{
  "include": [
<<<<<<< HEAD
    "src/**/*",
    "tests/**/*"
=======
    "src/**/*",
    "scripts/**/*",
    "migrations/**/*"
>>>>>>> feature/migrations
  ]
}
```

**Resolution Strategy:**
1. **Determine the actual scope**: Which directories should TypeScript check?
2. **Combine all necessary patterns**:
```json
{
  "include": [
    "src/**/*",
    "tests/**/*",
    "scripts/**/*",
    "migrations/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build"
  ]
}
```

3. **Add explicit excludes** to prevent checking unwanted directories

**Validation:**
```bash
tsc --noEmit
# Verify: All expected files are included, no build artifacts are checked
```

---

### 4.4 `moduleResolution` Changes

**Pattern:**
Branches change how TypeScript resolves module paths.

**Conflict Example:**
```json
{
  "compilerOptions": {
<<<<<<< HEAD
    "moduleResolution": "node",
=======
    "moduleResolution": "bundler",
>>>>>>> feature/modern-resolution
  }
}
```

**Impact:**
- `node`: CommonJS-style resolution
- `bundler`: ESM with bundler semantics
- Mismatches can break module resolution

**Resolution Strategy:**
1. **Understand the module system**: Is the project ESM or CommonJS?
2. **Choose based on output target**:
   - For Node.js packages: `"nodeNext"` (auto-detects based on package.json type)
   - For bundled code: `"bundler"`
   - Default safe choice: `"node"`

3. **Validate resolution**:
```bash
tsc --noEmit
# Verify: All imports resolve correctly with the chosen module resolution
```

---

## Part 5: Resolution Strategies and Validation Workflows

### 5.1 When to Keep "Ours" vs "Theirs" vs "Both"

**Decision Matrix:**

| Conflict Type | Keep Ours | Keep Theirs | Keep Both |
|---|---|---|---|
| **Type Definitions** | If our definition is more specific | If more general/flexible | Usually not - merge semantically |
| **Imports** | Only if theirs duplicates | Only if ours duplicates | Usually keep all |
| **Interfaces** | Never - let both merge | Never - let both merge | Usually yes (declaration merging) |
| **Generics** | If constraint is critical | If less restrictive | Combine with intersection if both needed |
| **`as const` patterns** | If literal types required | If wider types acceptable | Usually both - use `as const` for both |
| **Enums** | If smaller set needed | If more members needed | Combine all members |
| **Module augmentations** | If overwriting intentional | If extending intentional | Extend - merge augmentations |
| **Path aliases** | Only unique paths | Only unique paths | Keep all non-overlapping |

**Guidelines:**
1. **Default to "keep both"** unless there's semantic conflict
2. **Never choose arbitrarily** - understand why each branch made its change
3. **Test thoroughly** after resolution - `tsc --noEmit --strict`

---

### 5.2 How to Validate a Resolution

**Three-Phase Validation:**

**Phase 1: Syntax Check**
```bash
# Ensure valid TypeScript syntax
tsc --noEmit
```

**Phase 2: Strict Type Check**
```bash
# Verify type safety with strictest settings
tsc --noEmit --strict
```

**Phase 3: Linting**
```bash
# Check code style and patterns
eslint src/
prettier --check src/
```

**Complete Validation Script:**
```bash
#!/bin/bash
set -e

echo "Phase 1: Syntax validation..."
tsc --noEmit

echo "Phase 2: Strict type checking..."
tsc --noEmit --strict

echo "Phase 3: Linting..."
eslint src/
prettier --check src/

echo "All validations passed!"
```

---

### 5.3 What `tsc --noEmit --strict` Catches That Standard `tsc --noEmit` Doesn't

**Additional Checks Enabled:**

1. **Implicit Any Types**
```typescript
// Standard tsc --noEmit: ✓ Passes
// tsc --noEmit --strict: ✗ Error - missing type annotation
function process(value) { /* ... */ }
```

2. **Null/Undefined Handling**
```typescript
// Standard: ✓ Passes
// Strict: ✗ Error - value might be null
const length = (value: string | null).length;
```

3. **Function Parameter Variance**
```typescript
// Standard: ✓ Passes
// Strict: ✗ Checks function parameter covariance more strictly
const handler: (value: string | number) => void = (value: string) => {};
```

4. **Class Property Initialization**
```typescript
// Standard: ✓ Passes
// Strict: ✗ Error - property not initialized in constructor
class User {
  name: string; // Must initialize in constructor
}
```

---

### 5.4 Post-Merge Best Practices

**Immediately After Resolution:**

1. **Run full test suite**:
```bash
npm test
```

2. **Check type errors**:
```bash
tsc --noEmit --strict
```

3. **Reformat code**:
```bash
prettier --write src/
```

4. **Verify imports are organized**:
```bash
eslint --fix src/
```

5. **Run type-aware linting**:
```bash
eslint --max-warnings 0 src/
```

**Before Committing:**

```bash
# Comprehensive check
npm run type-check && npm test && npm run lint
```

**In CI/CD:**

Ensure every merge resolution is validated:
```yaml
# .github/workflows/merge-validation.yml
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: tsc --noEmit --strict
      - run: npm test
      - run: npm run lint
```

---

## Part 6: Advanced Scenarios

### 6.1 Discriminated Union + Generic Merge

**Scenario:**
A branch adds a generic type parameter to a discriminated union while another adds a new discriminant.

**Conflict:**
```typescript
// Original
type Request<T> =
  | { type: 'get'; url: string; payload?: T }
  | { type: 'post'; url: string; data: T };

// Branch A: non-generic
type Request =
  | { type: 'get'; url: string }
  | { type: 'post'; url: string; data: unknown };

// Branch B: adds timeout discriminant
type Request<T> =
  | { type: 'get'; url: string; payload?: T; timeout?: number }
  | { type: 'post'; url: string; data: T; timeout?: number };
```

**Resolution:**
Keep the generic version with optional timeout:
```typescript
type Request<T> =
  | { type: 'get'; url: string; payload?: T; timeout?: number }
  | { type: 'post'; url: string; data: T; timeout?: number };

// Verify narrowing still works
const handler = <T,>(req: Request<T>) => {
  if (req.type === 'post') {
    const data: T = req.data; // ✓ Correctly inferred
  }
};
```

---

### 6.2 Complex Type Constraint Merging

**Scenario:**
Generic constraints from different branches are incompatible.

**Conflict:**
```typescript
// Branch A
function transform<T extends { id: string }>(value: T): string {
  return value.id;
}

// Branch B
function transform<T extends { name: string }>(value: T): string {
  return value.name;
}
```

**Solution 1 - Overload:**
```typescript
function transform<T extends { id: string }>(value: T): string;
function transform<T extends { name: string }>(value: T): string;
function transform(value: any): string {
  return value.id || value.name;
}
```

**Solution 2 - Union Constraint:**
```typescript
function transform<T extends { id: string } | { name: string }>(value: T): string {
  return 'id' in value ? value.id : value.name;
}
```

**Validation:**
```bash
tsc --noEmit --strict
# Test both constraint types work
```

---

## Part 7: Common Pitfalls and How to Avoid Them

### 7.1 Pitfall: Blindly Using `any`

**Mistake:**
```typescript
// Suppresses all type checking
const merged: any = createMergedValue();
```

**Impact:**
Loss of type safety; future type errors won't be caught.

**Fix:**
Use a specific type, or use `unknown` if unsure:
```typescript
const merged: SomeType = createMergedValue();
// or
const merged: unknown = createMergedValue();
if (typeof merged === 'object' && merged !== null && 'prop' in merged) {
  const value = merged.prop; // Now safe to access
}
```

---

### 7.2 Pitfall: Ignoring Circular Dependency Warnings

**Mistake:**
Resolving a merge creates a circular import:
```typescript
// models/user.ts
export { validateUser } from './validators'; // validators imports from here!
```

**Impact:**
Runtime errors, module loading issues.

**Fix:**
Use `tsc --noEmit` to catch these before commit.

---

### 7.3 Pitfall: Not Running Tests After Resolution

**Mistake:**
Resolving a merge passes `tsc --noEmit` but breaks runtime behavior.

**Impact:**
Merge conflicts that compile but don't work.

**Fix:**
Always run full test suite after resolving:
```bash
npm test
```

---

## Conclusion

TypeScript's advanced type system creates unique merge conflicts that transcend simple syntactic resolution. Effective TypeScript merge conflict resolution requires:

1. **Understanding type system semantics** - How generics, discriminated unions, and conditional types interact
2. **Using appropriate validation** - `tsc --noEmit --strict` as the primary validation tool
3. **Testing thoroughly** - Both type checking and runtime behavior
4. **Following patterns** - Consistent approach to barrel files, imports, and configuration
5. **Documentation** - Record why each resolution decision was made

By following this guide and validating every merge with `tsc --noEmit --strict`, you can resolve TypeScript conflicts confidently while maintaining type safety and code quality.

---

## References

- [TypeScript: Documentation - Declaration Merging](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)
- [TypeScript: Documentation - Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript: Release Notes - TypeScript 4.9 (satisfies operator)](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
- [TypeScript: Documentation - Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
- [A Complete Guide to const Assertions in TypeScript - LogRocket](https://blog.logrocket.com/complete-guide-const-assertions-typescript/)
- [Demystifying Discriminated Unions in TypeScript - Medium](https://medium.com/@s35919223/demystifying-discriminated-unions-in-typescript-ea3d6180b733)
- [TypeScript Generic Constraints - TypeScript Tutorial](https://www.typescripttutorial.net/typescript-tutorial/typescript-generic-constraints/)
- [Common TypeScript Module Problems - LogRocket](https://blog.logrocket.com/common-typescript-module-problems-how-to-solve/)
- [Please Stop Using Barrel Files - TkDodo](https://tkdodo.eu/blog/please-stop-using-barrel-files)
- [How to Merge TypeScript Enums - bobbyhadz](https://bobbyhadz.com/blog/typescript-merge-2-enums)
- [Module Augmentation in TypeScript - DigitalOcean](https://www.digitalocean.com/community/tutorials/module-augmentation)
- [Augment TypeScript Module Types Without Overriding - TechNetExperts](https://www.technetexperts.com/typescript-module-augmentation-fix/)
- [Understanding TypeScript's Strict Compiler Option - Better Stack](https://betterstack.com/community/guides/scaling-nodejs/typescript-strict-option/)
- [TypeScript: TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
