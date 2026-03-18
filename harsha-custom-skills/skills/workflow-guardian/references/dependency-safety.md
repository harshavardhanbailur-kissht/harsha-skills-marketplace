# Dependency Safety and Conflict Detection Guide

This guide teaches Claude to be defensive about dependencies in the Workflow Guardian ecosystem. Rather than "upgrading" or "modernizing" dependencies, the approach is to **preserve existing choices** and only add new packages when absolutely necessary.

## Core Philosophy

**DO NOT** modify dependencies as part of feature work. The moment you change a version, add a new package, or modify build config, you create potential conflicts and breaking changes. The safest approach is defensive conservatism: keep what works, add only what's needed.

---

## 1. Dependency Inventory Protocol

### 1.1 Project A: issue-tracker (Firebase-based)

**Production Dependencies:**
```json
{
  "firebase": "^10.7.1",          // Backend: Auth, Firestore, Storage, Functions
  "react": "^18.2.0",               // Framework (caret: allows 18.x)
  "react-dom": "^18.2.0",           // DOM rendering
  "react-router-dom": "^6.21.1",   // Client-side routing
  "react-hot-toast": "^2.4.1",     // Toast notifications
  "date-fns": "^3.2.0",             // Date utilities
  "googleapis": "^170.1.0",         // Google APIs integration
  "@vercel/node": "^5.5.25"         // Vercel serverless runtime
}
```

**Key Observations:**
- Uses **caret ranges** (^) for most deps - allows compatible minor/patch updates
- React 18 is established (not upgrading to 19)
- Firebase 10.x is pinned and substantial library
- Has explicit date handling (date-fns) - don't add moment.js or other date libs
- Toast notifications handled by react-hot-toast - don't add competing libs

**Dev Dependencies:**
```json
{
  "@types/react": "^18.2.46",       // Types for React 18
  "@types/react-dom": "^18.2.18",  // Types for React DOM 18
  "@vitejs/plugin-react": "^4.2.1", // Vite React plugin
  "autoprefixer": "^10.4.16",       // PostCSS for Tailwind
  "postcss": "^8.4.32",              // CSS processing
  "tailwindcss": "^3.4.0",           // Styling framework (v3)
  "typescript": "^5.3.3",            // TS compiler
  "vite": "^5.0.10",                 // Build tool (v5)
  "vite-plugin-compression": "^0.5.1" // Asset compression
}
```

**Build Chain:**
- Vite 5.x handles all bundling
- Tailwind v3 with PostCSS/autoprefixer
- TypeScript 5.x
- Two compression plugins (gzip + brotli) in vite.config.ts

---

### 1.2 Project B: los-issue-tracker (Supabase-based)

**Production Dependencies:**
```json
{
  "@fontsource/inter": "^5.2.8",                // Font loading
  "@supabase/supabase-js": "^2.91.0",          // Backend: Auth, DB, Storage
  "@tailwindcss/postcss": "^4.1.18",           // Tailwind v4 PostCSS
  "browser-image-compression": "^2.0.2",       // Client-side image optimization
  "framer-motion": "^12.29.0",                 // Animation library
  "lucide-react": "^0.563.0",                  // Icon library
  "react": "^19.2.0",                          // Framework (newer: v19)
  "react-dom": "^19.2.0"                       // DOM rendering
}
```

**Key Observations:**
- Uses **caret ranges** (^) consistently
- React 19.x (newer than Project A's 18.x)
- Supabase for backend instead of Firebase
- Has animation library (framer-motion) - don't add React Spring or other motion libs
- Has icon library (lucide-react) - don't add react-icons or feather-icons
- **Tailwind v4** (newer) vs Project A's v3
- Image compression built-in - don't add competing libraries

**Dev Dependencies:**
```json
{
  "@eslint/js": "^9.39.1",                     // ESLint config
  "@testing-library/jest-dom": "^6.9.1",      // Testing utilities
  "@testing-library/react": "^16.3.2",        // React testing
  "@types/node": "^24.10.1",                  // Node type definitions
  "@types/react": "^19.2.5",                  // React 19 types
  "@types/react-dom": "^19.2.3",              // React 19 DOM types
  "@vitejs/plugin-react": "^5.1.1",           // Vite React plugin (v5)
  "autoprefixer": "^10.4.23",                 // PostCSS
  "eslint": "^9.39.1",                        // Linter (v9)
  "eslint-plugin-react-hooks": "^7.0.1",      // React Hooks rules
  "eslint-plugin-react-refresh": "^0.4.24",   // React Refresh plugin
  "globals": "^16.5.0",                       // Global variable definitions
  "jsdom": "^28.0.0",                         // DOM implementation for tests
  "postcss": "^8.5.6",                        // CSS processing (newer version)
  "tailwindcss": "^4.1.18",                   // Tailwind v4
  "typescript": "~5.9.3",                      // TS (tilde: patch-only updates)
  "typescript-eslint": "^8.46.4",             // TS linting
  "vite": "^7.2.4",                           // Build tool (v7 - newer)
  "vite-plugin-compression": "^0.5.1",        // Asset compression
  "vitest": "^4.0.18"                         // Unit test framework
}
```

**Build Chain:**
- Vite 7.x (newer than Project A's 5.x)
- Tailwind v4 with PostCSS/autoprefixer
- TypeScript 5.9.x with tilde range (patch-only)
- ESLint 9.x with flat config
- Vitest for unit tests
- Testing Library for React testing

---

## 2. Safe Dependency Addition Protocol

### 2.1 Four-Step Checklist Before Adding Any Dependency

**STEP 1: Check if already exists**
- Search package.json for similar functionality
- Example: before adding `axios`, check if `fetch` API is used
- Example: before adding `moment`, check for `date-fns`
- Example: before adding `zustand`, check for Context API usage

**STEP 2: Check version conflicts**
- If adding a new package, verify it's compatible with existing major versions
- Example: adding a React 19 plugin to a React 18 project creates conflict
- Example: adding Express to a Vite frontend project creates build conflicts
- Use `npm audit` to check for vulnerabilities after hypothetical addition

**STEP 3: Match version range style**
- Project A uses mostly **caret (^)** ranges
- Project B uses mostly **caret (^)** ranges, but TypeScript uses **tilde (~)**
- Example: if adding to Project A, use `^1.2.0` not `1.2.0` or `~1.2.0`
- Example: if adding to Project B, default to `^` unless it's a tool (then consider ~)

**STEP 4: Document the decision**
- Add a comment in package.json explaining why it's needed
- Example: `"framer-motion": "^12.29.0", // Animation for UI components`

### 2.2 How to Add a Safe New Dependency

**Scenario: Project A needs image upload preview**

UNSAFE approach:
```json
// DON'T: Upgrade React
"react": "^19.0.0",  // BREAKS everything using React 18 APIs
```

SAFE approach:
```json
// DO: Check if Canvas/Blob already used in codebase
// Then add only what's missing:
"react-dropzone": "^14.0.0",  // File upload with preview
```

**Scenario: Project B needs form validation**

UNSAFE approach:
```json
// DON'T: Add Formik + Zod
"formik": "^2.4.0",
"zod": "^3.22.0"  // Adds two competing solutions
```

SAFE approach:
```json
// DO: Use React Hook Form (light, minimal)
// Or check if HTML5 validation is sufficient first
"react-hook-form": "^7.48.0"  // If validation is essential
```

---

## 3. Dangerous Patterns to Avoid

### Pattern 1: Upgrading Core Frameworks as "Modernization"

```javascript
// DANGEROUS: "Let me upgrade React to the latest version"
{
  "react": "^18.2.0"  // Current
}
// BECOMES:
{
  "react": "^19.0.0"  // ALL existing code breaks
}
```

**Why it breaks:**
- Hooks changed in React 19 (useCallback, useMemo behavior)
- JSX transformation different
- Concurrent features may behave unexpectedly
- Testing library expectations change

**Safe alternative:**
- Leave React 18 alone in Project A
- Project B consciously chose React 19 - respect that choice
- If a feature requires React 19, say "this feature requires React 19 upgrade, which is a breaking change"

---

### Pattern 2: Adding "Better" Alternatives to Existing Solutions

```javascript
// DANGEROUS: "Let me add axios for better HTTP"
{
  "dependencies": {
    // Project A already uses Firebase + fetch
    "axios": "^1.6.0"  // Adds competing HTTP pattern
  }
}
```

**Why it breaks:**
- Two HTTP request libraries create confusion
- Some components use fetch, others use axios
- Inconsistent error handling
- Larger bundle size

**Safe alternative:**
```javascript
// Check: Does Firebase SDK handle the use case?
// Check: Can native fetch() work?
// Only add axios if genuinely needed for specific API
```

---

### Pattern 3: Adding Competing UI/Styling Solutions

```javascript
// DANGEROUS: "Let me add shadcn/ui components"
{
  "dependencies": {
    // Project A uses plain React + Tailwind
    "@shadcn/ui": "^0.4.0",  // Adds opinionated component layer
    "radix-ui": "^1.0.0"     // Adds accessibility lib
  }
}
```

**Why it breaks:**
- Tailwind-based project suddenly has pre-built components
- Component conflicts (custom vs library)
- Styling conflicts (custom CSS vs component defaults)
- Bundle bloat

**Safe alternative:**
```javascript
// If components needed: create custom Tailwind components
// OR: consciously adopt a component library project-wide
// NOT: mix two approaches
```

---

### Pattern 4: Adding State Management When Context Exists

```javascript
// DANGEROUS: "Let me add Redux for state"
{
  "dependencies": {
    // Projects likely using React Context
    "redux": "^4.2.0",
    "react-redux": "^8.1.0"  // Adds competing pattern
  }
}
```

**Why it breaks:**
- Project A: Firebase handles persistent state
- Project B: Likely has local Context or Supabase real-time
- Redux is overkill for these architectures
- Doubles state management code

**Safe alternative:**
```javascript
// Context API + custom hooks: proven to work
// Local state + useCallback: often sufficient
// Supabase real-time subscriptions: built-in
```

---

### Pattern 5: Modifying Build Configuration Unnecessarily

**vite.config.ts changes to avoid:**

```typescript
// DANGEROUS: Adding webpack config to Vite project
import webpack from 'webpack';  // VITE DOESN'T USE WEBPACK

// DANGEROUS: Installing eslint-webpack-plugin
// (Webpack doesn't run in Vite projects)

// DANGEROUS: Modifying tsconfig.json for "better" settings
"target": "ES2015",  // Don't change from ES2020/ES2022
```

**Why it breaks:**
- Vite and webpack are completely different tools
- Plugins incompatible
- Build failures
- TypeScript compilation errors

**Safe approach:**
```typescript
// Only modify vite.config.ts if:
// 1. Adding compression (already in example)
// 2. Adding aliases (already in example)
// 3. Changing output directory (rare)
// 4. Adding middleware for CSP headers (shown in Project B)

// Don't touch unless genuinely necessary
```

---

### Pattern 6: Changing TypeScript Configuration

```json
// DANGEROUS: Loosening strict mode to "move faster"
{
  "compilerOptions": {
    "strict": false,  // BREAKS type safety
    "skipLibCheck": false,  // BREAKS build
    "noImplicitAny": false  // DEFEATS the purpose of TS
  }
}
```

**Why it breaks:**
- Loses TypeScript's value
- Introduces runtime errors
- Makes refactoring unsafe
- Technical debt accumulates

**Safe approach:**
```json
// Keep existing tsconfig settings
// Project A: target ES2020, strict mode
// Project B: target ES2022, strict mode
// Only change if there's a specific incompatibility
```

---

## 4. Build Tool Preservation Rules

### 4.1 Vite Configuration in Both Projects

**Project A: vite.config.ts (5.0.10)**
```typescript
// What it does:
// 1. React plugin for JSX compilation
// 2. Two compression plugins (gzip + brotli)
// 3. Manual chunking for Firebase and vendor libraries
// 4. Source map disabled for smaller builds

// What NOT to do:
// ❌ Add webpack loaders - VITE DOESN'T USE WEBPACK
// ❌ Add postcss plugins - Already configured via postcss.config
// ❌ Change resolve.alias patterns - Breaks @ imports
// ❌ Remove compression - Increases bundle size
```

**Project B: vite.config.ts (7.2.4)**
```typescript
// What it does:
// 1. React plugin for JSX compilation
// 2. CSP header middleware for dev mode
// 3. Two compression plugins (gzip + brotli)
// 4. Manual chunking for Supabase and vendor libraries

// What NOT to do:
// ❌ Remove CSP headers - Breaks security testing
// ❌ Add esbuild configuration - Vite handles this
// ❌ Change build output directory - Breaks deployment
// ❌ Add Babel - Vite uses SWC/esbuild
```

### 4.2 TypeScript Configuration

**Project A: tsconfig.json**
```json
{
  "target": "ES2020",              // Don't lower this
  "lib": ["ES2020", "DOM", "DOM.Iterable"],
  "module": "ESNext",              // Don't change to CommonJS
  "strict": true,                  // Don't loosen
  "jsx": "react-jsx",              // Must stay for React 18
  "paths": { "@/*": ["./src/*"] }  // Don't change aliases
}
```

**Project B: tsconfig.app.json**
```json
{
  "target": "ES2022",              // Newer than Project A
  "lib": ["ES2022", "DOM", "DOM.Iterable"],
  "jsx": "react-jsx",              // For React 19
  "strict": true,                  // Don't loosen
  "erasableSyntaxOnly": true,      // Keep for safety
  "noUncheckedSideEffectImports": true  // Keep for tree-shaking
}
```

### 4.3 PostCSS and Tailwind

**Project A:**
```javascript
// tailwindcss: ^3.4.0
// postcss: ^8.4.32
// autoprefixer: ^10.4.16
// These work together: don't add competing CSS tools
// Don't add: Styled-components, Emotion, UnoCSS (conflicts)
```

**Project B:**
```javascript
// tailwindcss: ^4.1.18  (v4, newer)
// @tailwindcss/postcss: ^4.1.18  (v4 PostCSS)
// postcss: ^8.5.6
// autoprefixer: ^10.4.23
// Tailwind v4 is different: don't downgrade to v3
// Don't add competing CSS frameworks
```

---

## 5. Real Examples from Both Projects

### Example 1: Project A Dependencies - What Each Does

| Dependency | Purpose | Breaking If Changed |
|---|---|---|
| firebase ^10.7.1 | Auth, Firestore, Storage, Cloud Functions | Core backend - breaking |
| react ^18.2.0 | UI framework | ALL components depend on this |
| react-router-dom ^6.21.1 | Client-side routing | All routes break if removed |
| date-fns ^3.2.0 | Date formatting/manipulation | Any date handling breaks |
| googleapis ^170.1.0 | Google OAuth integration | Authentication breaks |
| react-hot-toast ^2.4.1 | Toast notifications | All success/error messages break |
| tailwindcss ^3.4.0 | Styling | All visual styling breaks |
| vite ^5.0.10 | Build tool | Build fails if removed |

**Safe additions to this project:**
- PDF generation: `pdfkit` (if really needed, no current solution)
- Advanced charting: `recharts` (if dashboards needed)
- Email validation: add to utils, don't add lib

**Unsafe additions:**
- Axios (already have fetch + Firebase)
- Moment.js (already have date-fns)
- Redux (Firebase already manages state)
- Next.js (already using Vite)

---

### Example 2: Project B Dependencies - What Each Does

| Dependency | Purpose | Breaking If Changed |
|---|---|---|
| @supabase/supabase-js ^2.91.0 | Auth, Database, Storage, Real-time | Core backend - breaking |
| react ^19.2.0 | UI framework | ALL components depend on this |
| framer-motion ^12.29.0 | Animations and transitions | UI animations break |
| lucide-react ^0.563.0 | Icon library | All icons break |
| tailwindcss ^4.1.18 | Styling (v4) | All visual styling breaks |
| browser-image-compression ^2.0.2 | Client-side image optimization | Image uploads slow |
| vite ^7.2.4 | Build tool | Build fails if removed |

**Safe additions to this project:**
- Form validation: `react-hook-form` (complementary to existing)
- Data fetching: already have Supabase
- Component libraries: Custom Tailwind + lucide (don't add shadcn)

**Unsafe additions:**
- Another HTTP client (Supabase SDK handles it)
- Another animation lib (framer-motion already there)
- Icon lib like react-icons (lucide-react already there)
- Routing: (might not need if SPA)

---

## 6. Dependency Conflict Detection Checklist

### Before Adding Any New Package, Verify:

- [ ] Is this functionality already provided by an existing dependency?
- [ ] Does this version conflict with existing major versions?
  - Existing React 18? Don't add React 19-specific libs
  - Existing Tailwind v3? Don't add v4-specific components
  - Existing Supabase? Don't add Firebase
- [ ] Is the version range style consistent?
  - Using caret (^) in this project? Use caret for new packages
  - Using tilde (~) for tools? Use tilde for new tools
- [ ] Does this create duplicate functionality?
  - Already have date-fns? Don't add moment
  - Already have framer-motion? Don't add react-spring
  - Already have Tailwind? Don't add styled-components
- [ ] Will this add substantial bundle size?
  - Check: `npm info PACKAGE size` before adding
  - Prefer smaller alternatives if available
- [ ] Does this require TypeScript or build config changes?
  - Minimize tsconfig.json changes
  - Only modify vite.config.ts if essential
- [ ] Are there existing similar patterns in the codebase?
  - If HTTP library exists, use it consistently
  - If state management pattern exists, follow it
  - If testing framework exists, use it

---

## 7. The Defensive Mindset

### Key Principles

1. **Preserve > Upgrade**: Existing dependencies work. Upgrading breaks things.
2. **Minimize > Add**: Every new dependency adds complexity and bundle size.
3. **Consistency > Novelty**: Following existing patterns is safer than experimenting.
4. **Build > Config**: Modify how code is written, not how it's built.
5. **Document > Assume**: Add comments explaining dependency choices.

### When in Doubt, Ask

Before modifying dependencies:

1. Does the feature require a new package?
   - Or can it be built with existing tools?
2. Is this package essential?
   - Or is it a "nice to have"?
3. What breaks if we upgrade?
   - List the breaking changes
4. Is there a lighter alternative?
   - Could a utility function replace it?
5. What's the bundle size impact?
   - Is it worth the added size?

### Red Flags

- "Let me upgrade React" → STOPS the task, ask why
- "Let me add a better HTTP library" → Check existing patterns first
- "Let me add Tailwind components library" → Custom components exist
- "Let me modify tsconfig for better settings" → Leave it alone
- "Let me add webpack" → Vite is the build tool
- "Let me simplify by removing validation" → Compromises type safety
- "This dependency is old, let me upgrade" → If it works, leave it

---

## 8. Summary: The Three Categories

### Green Light Dependencies (Safe)
- Bug fixes within version ranges
- Type definition packages
- Utility libraries with no conflicts
- Test frameworks (when not in conflict)

### Yellow Light Dependencies (Review)
- Major version upgrades
- Framework updates
- Build tool plugins
- Any change to tsconfig.json or vite.config.ts

### Red Light Dependencies (Dangerous)
- Replacing core frameworks
- Adding competing solutions
- Loosening type safety
- Upgrading without testing impact
- Adding webpack to Vite projects
- Modifying security settings

---

## Conclusion

The safest code is code that doesn't change. Every new dependency, every version bump, every configuration tweak is an opportunity for bugs. The Workflow Guardian skill should teach defensive programming: preserve what works, change only what's broken, and think deeply before adding anything new.

When in doubt, the answer is: "This works now. What problem are we solving by changing it?"
