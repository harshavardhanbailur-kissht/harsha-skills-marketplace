# Environment and Configuration Safety Reference

**Document Version:** 1.0
**Last Updated:** 2026-02-26
**Purpose:** Comprehensive guide to preventing application-breaking configuration changes when adding features to codebases
**Severity:** CRITICAL - Configuration file failures prevent entire application startup

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Environment Variables Safety](#environment-variables-safety)
3. [Build Configuration Safety](#build-configuration-safety)
4. [Tailwind CSS Configuration](#tailwind-css-configuration)
5. [TypeScript Configuration](#typescript-configuration)
6. [Feature Flags and Conditional Configuration](#feature-flags-and-conditional-configuration)
7. [Package.json and Lockfile Safety](#packagejson-and-lockfile-safety)
8. [Common Breakage Patterns](#common-breakage-patterns)
9. [Configuration Validation Checklist](#configuration-validation-checklist)
10. [Framework-Specific Patterns](#framework-specific-patterns)

---

## Executive Summary

Configuration files are the most critical component of any web application. When configuration breaks, the entire application fails to start. Unlike code bugs that may only affect certain features, configuration errors create catastrophic failures:

- Missing environment variables → Runtime crashes
- Broken build configuration → No bundle produced
- Invalid tsconfig paths → All imports fail
- Incorrect Tailwind content paths → Styles don't load
- Plugin conflicts → Build hangs or produces invalid output

**The Golden Rule:** When adding features, EXTEND existing configuration patterns rather than REPLACING them.

**DANGEROUS Approach:** "Let me update the configuration to be better optimized"
**SAFE Approach:** "I'll add the minimum config change needed, following the exact same pattern as existing entries"

---

## Environment Variables Safety

Environment variables represent one of the most fragile parts of application configuration because they control runtime behavior and can silently fail if missing or misnamed.

### Understanding the Prefix Security Model

Different frameworks enforce different prefixes to prevent accidentally exposing secrets:

#### Vite Environment Variables (VITE_ Prefix)

**Security Foundation:**
- Only variables prefixed with `VITE_` are exposed to client-side code
- This is Vite's built-in security boundary preventing accidental secret leakage
- Variables without the prefix remain server-only and never reach the browser

**How it Works:**
```javascript
// .env file
VITE_API_ENDPOINT=https://api.example.com
DATABASE_PASSWORD=supersecret  // Never exposed

// In component - works fine
const api = import.meta.env.VITE_API_ENDPOINT

// Attempting this fails silently
const pwd = import.meta.env.DATABASE_PASSWORD  // undefined
```

**File Loading Precedence (in order of precedence):**
1. `.env.local` (loaded in all cases, git-ignored)
2. `.env.[mode].local` (mode-specific, git-ignored, highest priority)
3. `.env.[mode]` (mode-specific, can be committed)
4. `.env` (general, can be committed)

**Critical TypeScript Setup:**
```typescript
// vite-env.d.ts - Required for type safety
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_ENDPOINT: string
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

**Safe Pattern for Adding New Variables:**
```bash
# DO: Add to .env in consistent format
VITE_FEATURE_NEW_DASHBOARD=true
VITE_NEW_API_TIMEOUT=5000

# DO: Document in .env.example (no actual values)
VITE_FEATURE_NEW_DASHBOARD=
VITE_NEW_API_TIMEOUT=

# DON'T: Add variables without prefix (won't be available)
# DON'T: Use VITE_ prefix for sensitive data
# DON'T: Change existing variable names (breaks imports)
```

**What NOT to Do:**
- Never store API keys, passwords, or tokens with `VITE_` prefix
- Never remove or rename existing `VITE_` variables
- Never change the prefix pattern mid-project
- Never expose database credentials (even with `VITE_` they'll be visible)

**References:**
- [Vite Environment Variables Guide](https://vite.dev/guide/env-and-mode)
- [How to Use Environment Variables in Vite.js](https://vueschool.io/articles/vuejs-tutorials/how-to-use-environment-variables-in-vite-js/)

---

#### Next.js Environment Variables (NEXT_PUBLIC_ Prefix)

**How Next.js Handles Variables:**
- Variables are inlined into the JavaScript bundle at BUILD TIME
- After build, changes to NEXT_PUBLIC_ variables have NO EFFECT
- Any NEXT_PUBLIC_ variable is hardcoded into every deployed bundle

**Critical Distinction from Vite:**
```javascript
// next.config.js or .env
NEXT_PUBLIC_API_URL=https://api.example.com
DATABASE_URL=postgresql://...  // Server-only

// In component
const api = process.env.NEXT_PUBLIC_API_URL  // Works (embedded at build)
const db = process.env.DATABASE_URL          // undefined in client
```

**Build-Time Lock-In Danger:**
```bash
# Development
NEXT_PUBLIC_FEATURE_FLAG=true

# Build happens - value hardcoded into bundle
npm run build

# Later: Someone changes .env in production
NEXT_PUBLIC_FEATURE_FLAG=false

# ERROR: Feature flag is STILL true in deployed bundle!
# Must rebuild and redeploy to change
```

**Safe Pattern:**
```bash
# .env.local (development only, git-ignored)
NEXT_PUBLIC_FEATURE_NEW_ANALYTICS=false
DATABASE_PASSWORD=devpassword

# .env (committed, safe defaults)
NEXT_PUBLIC_FEATURE_NEW_ANALYTICS=false

# .env.production (explicit for production builds)
NEXT_PUBLIC_FEATURE_NEW_ANALYTICS=true
```

**References:**
- [Next.js Environment Variables Guide](https://nextjs.org/docs/pages/guides/environment-variables)
- [Next.js Managing Environment Variables](https://blog.logrocket.com/configure-environment-variables-next-js/)

---

#### Create React App Environment Variables (REACT_APP_ Prefix)

**Safety Model:**
- All variables must start with `REACT_APP_` or they're ignored (not an error, just silently ignored)
- This prevents accidentally exposing environment variables from the machine

**Accessing Variables:**
```javascript
// .env
REACT_APP_VERSION=1.0.0
API_KEY=secret  // Silently ignored - won't reach client

// In component
console.log(process.env.REACT_APP_VERSION)  // "1.0.0"
console.log(process.env.API_KEY)            // undefined
console.log(process.env.NODE_ENV)           // "development" or "production"
```

**Restart Requirement:**
```bash
# After adding or modifying .env:
# Development server MUST be restarted
npm start  # or yarn start

# Without restart, old values remain in memory
```

**Safe Pattern:**
```
.env
.env.local          (git-ignored)
.env.development    (can be committed)
.env.development.local
.env.production     (can be committed)
.env.production.local (git-ignored)
```

**References:**
- [Create React App Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)
- [Managing Environment Variables in React](https://hub.qovery.com/guides/tutorial/managing-env-variables-in-create-react-app/)

---

### .env.example Pattern

**Purpose:** Document required variables without exposing secrets

**Correct Pattern:**
```bash
# .env.example - Safe to commit
VITE_API_ENDPOINT=
VITE_AUTH_PROVIDER=
DATABASE_URL=
DATABASE_PASSWORD=
API_TIMEOUT_MS=

# Include comments explaining each variable
# VITE_API_ENDPOINT: Public API endpoint for frontend calls
# DATABASE_URL: PostgreSQL connection string (server-side only)
# API_TIMEOUT_MS: Request timeout in milliseconds
```

**What NOT to Do:**
```bash
# WRONG: Never include actual values
VITE_API_ENDPOINT=https://production.api.example.com

# WRONG: Never include production secrets in example
DATABASE_PASSWORD=prod_password_123

# WRONG: Don't leave values empty without explanation
API_TIMEOUT_MS=
```

**Safe Implementation:**
1. Create `.env.example` with all required variables
2. Leave values empty (no defaults that reveal structure)
3. Add detailed comments explaining purpose and constraints
4. Include in version control
5. Document in README.md how to create `.env` from `.env.example`

---

### Runtime vs Build-Time Environment Variables

**Build-Time Variables (Vite, Next.js, CRA):**
- Evaluated when the build process runs
- Embedded directly into the output bundle
- Cannot change without rebuilding
- Smaller bundle size (known at build time)
- Examples: `VITE_`, `NEXT_PUBLIC_`, `REACT_APP_`

**Runtime Variables (Server-side only):**
- Not prefixed or marked as public
- Only accessible on Node.js backend
- Can change without restart (in some frameworks)
- Good for database credentials, API secrets
- Examples: `DATABASE_URL`, `API_KEY`, `PRIVATE_TOKEN`

**Safe Mixing Pattern:**
```javascript
// vite.config.ts
export default defineConfig({
  define: {
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __APP_VERSION__: JSON.stringify(process.env.VITE_APP_VERSION),
  }
})

// .env
VITE_APP_VERSION=1.0.0
DATABASE_URL=postgresql://...  // Never appears in bundle
```

---

## Build Configuration Safety

Build configuration files control how your application is compiled, bundled, and optimized. A broken build config means no deployment possible.

### Vite Configuration Safety

**Current Versions:** Vite 5.x, 6.x (2025-2026)

**Safe Configuration Pattern:**
```typescript
// vite.config.ts - Follow existing patterns
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import legacy from '@vitejs/plugin-legacy'

export default defineConfig({
  plugins: [
    react(),
    // NEW: Add plugin AFTER existing ones, following same pattern
    legacy({
      targets: ['defaults', 'not IE 11']
    })
  ],
  resolve: {
    alias: {
      '@': '/src',
      // NEW: Add alias following existing @ pattern
      '@components': '/src/components'
    }
  },
  build: {
    target: 'esnext',
    // Only modify if absolutely necessary
    minify: 'terser'
  }
})
```

**Plugin Order Critical Issues:**

Plugins execute in the order specified. Order matters because:
- Some plugins transform code before others process it
- Conflicting plugins can produce incorrect output
- Plugin A might process files that Plugin B also wants to handle

**Plugin Conflict Resolution:**
```typescript
// SAFE: Adding new plugin at end
plugins: [
  react(),        // Core framework
  vue(),          // Alternative framework
  svgr(),         // SVG handling
  newPlugin()     // NEW: Add at end, after core plugins
]

// DANGEROUS: Adding in middle or changing order
plugins: [
  react(),
  newPlugin(),    // Might interfere with react transformation
  vue()
]
```

**Common Plugin Conflicts (2025):**
1. **CSS Plugin Conflicts:** Custom CSS plugins may conflict with Vite's native CSS handling
   - Solution: Use file extension suffixes to prevent double-processing
2. **Framework Plugin Issues:** Multiple framework plugins (react + vue) need careful ordering
3. **Alias Conflicts:** Similar paths in alias can shadow each other
4. **Module Resolution:** Plugins changing how modules resolve can break imports

**Safe Pattern for Adding Plugins:**
```typescript
// DON'T: Replace or reorder existing plugins
// DO: Append new plugins at the end following same pattern
// DO: Use conditional loading for framework-specific plugins

import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd())

  const plugins = [
    react(),
    // Existing plugins stay
  ]

  // NEW: Conditionally add feature-specific plugin
  if (env.VITE_ENABLE_NEW_OPTIMIZATION) {
    plugins.push(optimizationPlugin())
  }

  return {
    plugins
  }
})
```

**Plugin Debugging Checklist:**
- [ ] Enable Vite debug logging: `vite build --debug`
- [ ] Check plugin compatibility with current Vite version
- [ ] Verify no duplicate plugins in config
- [ ] Ensure plugin versions support current Node.js version
- [ ] Test build in isolation: `vite build --outDir dist-test`
- [ ] Check for conflicting file handlers in plugins

**References:**
- [Vite Configuration Guide](https://vite.dev/config/)
- [Vite Troubleshooting Guide](https://vite.dev/guide/troubleshooting)
- [Fixing Plugin Configuration Errors in Vite](https://www.mindfulchase.com/explore/troubleshooting-tips/fixing-hmr-failures,-build-asset-issues,-and-plugin-configuration-errors-in-vite.html)

---

### Webpack Configuration Safety

**Safe Configuration Pattern:**
```javascript
// webpack.config.js - Extend, don't replace
module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js'
  },
  module: {
    rules: [
      // Existing rules
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      // NEW: Add new rule AFTER existing ones
      {
        test: /\.scss$/,
        use: ['style-loader', 'css-loader', 'sass-loader']
      }
    ]
  },
  plugins: [
    // Existing plugins
    new HtmlWebpackPlugin(),
    // NEW: Add plugins, watch for duplicates
    new MiniCssExtractPlugin()
  ]
}
```

**Critical Webpack Issues (2025):**

1. **Plugin Duplication in Production:**
   ```javascript
   // DANGEROUS: ModuleConcatenationPlugin enabled twice
   module.exports = {
     mode: 'production',  // Enables ModuleConcatenationPlugin by default
     plugins: [
       new webpack.optimize.ModuleConcatenationPlugin()  // ERROR: Now enabled twice
     ]
   }

   // SAFE: Remove explicit plugin in production mode
   module.exports = {
     mode: 'production',  // Let webpack handle it
     plugins: [
       // Don't manually add ModuleConcatenationPlugin
     ]
   }
   ```

2. **Loader Ordering Issues:**
   ```javascript
   // SAFE: Loaders execute right-to-left
   rules: [
     {
       test: /\.scss$/,
       use: [
         'style-loader',      // Last (inject into DOM)
         'css-loader',        // Middle (parse CSS)
         'sass-loader'        // First (compile SCSS)
       ]
     }
   ]

   // DANGEROUS: Wrong loader order
   rules: [
     {
       test: /\.scss$/,
       use: [
         'sass-loader',       // Would try to parse CSS as SCSS - broken
         'css-loader',
         'style-loader'
       ]
     }
   ]
   ```

3. **Webpack-Sources Version Conflicts:**
   ```javascript
   // SAFE: Use webpack's bundled version
   const { sources } = require('webpack')

   // DANGEROUS: Separate package may have version mismatch
   const sources = require('webpack-sources')
   ```

4. **File Caching and Loader Isolation:**
   ```javascript
   // SAFE: Each loader clearly defines what it handles
   rules: [
     { test: /\.png$/, type: 'asset/resource' },
     { test: /\.svg$/, type: 'asset/inline' }
   ]

   // DANGEROUS: Overlapping test patterns
   rules: [
     { test: /\.(png|svg)$/, loader: 'file-loader' },
     { test: /\.svg$/, loader: 'svg-loader' }  // Conflict!
   ]
   ```

**References:**
- [Webpack Plugin Documentation](https://webpack.js.org/concepts/plugins/)
- [Webpack Migration to v5](https://webpack.js.org/migrate/5/)
- [Enterprise Webpack Troubleshooting](https://www.mindfulchase.com/explore/troubleshooting-tips/build-bundling/enterprise-webpack-troubleshooting-deep-dive-into-build-and-bundling-failures.html)

---

### tsconfig.json Path Aliases Safety

**Critical Limitations:**
- Path aliases ONLY work at compile time (TypeScript → JavaScript)
- Runtime does NOT automatically resolve aliases
- Different build tools handle aliases differently
- Changing paths can break ALL imports simultaneously

**Safe Pattern:**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@utils/*": ["src/utils/*"]
      // NEW: Add following existing @ prefix pattern
    },
    "strict": true,
    "module": "esnext",
    "target": "es2020"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

**Dangerous Changes:**
```json
{
  // DANGEROUS: Removing existing paths breaks all imports
  // Old: "@": "src"
  // Deleted - now all @/* imports fail

  // DANGEROUS: Changing baseUrl
  "baseUrl": "src",  // Was ".", now EVERYTHING breaks

  // DANGEROUS: Changing strict settings
  "strict": false,   // Was true, now type errors hidden

  // DANGEROUS: Changing module resolution
  "moduleResolution": "node",  // Was "bundler", breaks monorepos
}
```

**Path Alias Gotchas:**

1. **TypeScript Only:**
   ```typescript
   // Works in .ts/.tsx with tsc
   import { Component } from '@components/Button'

   // Fails at runtime - alias not resolved
   // Needs: tsc-alias, esbuild-plugin-ts-paths, or bundler with alias support
   ```

2. **Monorepo Complexity:**
   ```json
   // Root tsconfig.json
   {
     "paths": {
       "@app/*": ["apps/main/src/*"],
       "@lib/*": ["packages/lib/src/*"]
     }
   }

   // PROBLEM: Child packages must import from root tsconfig
   // Cannot have separate paths per package
   // Coupling increases as monorepo grows
   ```

3. **Different Resolution per Tool:**
   ```javascript
   // Vite: Understands tsconfig.json paths automatically
   // Webpack: Needs webpack.config.js alias
   // Jest: Needs moduleNameMapper in jest.config.js
   // esbuild: Needs separate configuration

   // SAFE: Align all tools to prevent confusion
   // DANGEROUS: Different path resolution per tool
   ```

**Safe Implementation:**
```typescript
// src/vite-env.d.ts - Document all paths
/// <reference types="vite/client" />

declare module '@components/*'
declare module '@utils/*'
declare module '@stores/*'

// vite.config.ts - Match tsconfig.json exactly
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@utils': '/src/utils',
      '@stores': '/src/stores'
    }
  }
})

// jest.config.js - Align with both
module.exports = {
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1'
  }
}
```

**Breaking Change Detection:**
```bash
# After modifying tsconfig.json paths:
npm run build        # Check for import errors
npm test             # Jest may fail if moduleNameMapper wrong
npm run type-check   # tsc should pass
```

**References:**
- [TypeScript TSConfig Documentation](https://www.typescriptlang.org/tsconfig/)
- [Path Aliases in TypeScript](https://dev.to/larswaechter/path-aliases-with-typescript-in-nodejs-4353)
- [TypeScript Paths Could Be Evil](https://marianobe.cc/posts/tsconfig-paths-evil/)

---

## Tailwind CSS Configuration

**Current Status:** Tailwind v3.x (stable, widely supported) and v4.x (CSS-first, breaking changes)

### Tailwind v3 Configuration

**Safe Pattern:**
```javascript
// tailwind.config.js (v3.x)
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    // NEW: Add new directories following same pattern
    './src/components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      // SAFE: Use extend: {} to add, not override
      colors: {
        'brand-blue': '#0066cc'
      },
      spacing: {
        '128': '32rem'
      }
    }
  },
  plugins: [
    // Existing plugins
    require('@tailwindcss/forms')
  ]
}
```

**Critical Content Paths Issue:**

Content paths determine which files Tailwind scans for class names. Missing a directory means styles don't get generated:

```javascript
// DANGEROUS: Missing directory
content: [
  './src/**/*.{js,ts,jsx,tsx}'
  // Missing: './src/components/**/*.{js,ts,jsx,tsx}'
]

// Result: Classes in components/ directory don't get generated
// Styles silently don't load (no error message!)
```

**Safe Content Pattern:**
```javascript
// vite + react
content: [
  './index.html',           // HTML entry
  './src/**/*.{jsx,tsx}',   // React files
  './src/**/*.{js,ts}'      // TypeScript files
]

// next.js
content: [
  './pages/**/*.{js,ts,jsx,tsx}',
  './components/**/*.{js,ts,jsx,tsx}',
  './app/**/*.{js,ts,jsx,tsx}'
]

// Include all dynamic directories
// Be more specific than needed rather than too broad
```

**Extend vs Override:**

```javascript
// SAFE: Use extend to preserve defaults
module.exports = {
  theme: {
    extend: {
      colors: {
        'brand': '#123456'  // Adds to existing colors
      }
    }
  }
}

// DANGEROUS: Direct override replaces everything
module.exports = {
  theme: {
    colors: {
      'brand': '#123456'  // REMOVES all default colors!
    }
  }
}
```

**Plugin Addition Safety:**

```javascript
// SAFE: Add plugins in order
plugins: [
  require('@tailwindcss/forms'),
  require('@tailwindcss/typography'),
  // NEW: Add new plugins at end, following same pattern
  require('./plugins/custom-badge-plugin')
]

// DANGEROUS: Plugins with conflicting utilities
plugins: [
  require('@tailwindcss/forms'),        // Styles form elements
  require('./custom-forms-plugin')      // Also styles form elements - conflict!
]
```

**References:**
- [Tailwind CSS Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Moving from Tailwind 3 to Tailwind 4 in Next.js](https://www.9thco.com/labs/moving-from-tailwind-3-to-tailwind-4)

---

### Tailwind v4 Breaking Changes

**Dramatic Shift:** Tailwind v4 moves from JavaScript config to CSS-first configuration using `@theme` directive.

**Major Breaking Changes:**

1. **CSS-First Configuration:**
   ```css
   /* v4: Define design system in CSS */
   @theme {
     --color-primary: #0066cc;
     --color-secondary: #ff6600;
   }
   ```

   ```javascript
   // v3: Define in JavaScript
   module.exports = {
     theme: {
       colors: {
         primary: '#0066cc'
       }
     }
   }
   ```

2. **Unsupported Configuration Options:**
   ```javascript
   // v3: Supported
   module.exports = {
     corePlugins: {
       preflight: false  // Disable Tailwind reset
     },
     safelist: [
       'bg-red-500',
       'text-white'
     ],
     separator: '__'
   }

   // v4: NONE of these are supported
   // No replacement for corePlugins
   // No replacement for safelist
   // Separator must use : only
   ```

3. **Container Utility Changes:**
   ```css
   /* v3: Options in config */
   module.exports = {
     theme: {
       container: {
         center: true,
         padding: '1rem'
       }
     }
   }

   /* v4: Use @layer and utilities instead */
   @layer utilities {
     .container {
       @apply mx-auto px-4;
     }
   }
   ```

4. **Variant Behavior Change:**
   ```css
   /* v3: Overriding gradient resets entire gradient */
   hover:from-red-500  // Loses to, via colors

   /* v4: Values are preserved */
   hover:from-red-500  // Keeps existing to, via colors
   ```

5. **Component Class Variants Broken:**
   ```css
   /* v3: Works fine */
   @layer components {
     .btn {
       @apply px-4 py-2 bg-blue-500 hover:bg-blue-600;
     }
   }

   /* v4: Variants don't work with component classes */
   /* Must use utility classes instead */
   ```

6. **Browser Support Changed:**
   ```
   v3: IE 11 support possible with polyfills
   v4: Requires Safari 16.4+, Chrome 111+, Firefox 128+
   ```

**v3 vs v4 Decision Matrix:**

| Criterion | v3 | v4 |
|-----------|----|----|
| Browser support needed | Old browsers | Modern only |
| Starting fresh | Good | Better |
| Migrating existing | Better | Risky |
| Custom plugins | Works | May break |
| Team familiarity | High | Low |
| Maintenance | Good | Active development |
| PostCSS dependency | Yes | Yes |

**Safe Recommendation (2025-2026):**
- NEW projects: v4 if targeting modern browsers only
- EXISTING projects: Stay on v3 unless critical feature needed
- v4 requires complete rewrite of configuration
- v4 not fully stable in all edge cases yet

**References:**
- [Tailwind CSS v4 Announcement](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind v4 Migration Guide](https://designrevision.com/blog/tailwind-4-migration)
- [Downgrading Tailwind v4 to v3 Lessons](https://medium.com/@pradeepgudipati/%EF%B8%8F-downgrading-from-tailwind-css-v4-to-v3-a-hard-earned-journey-back-to-stability-88aa841415bf)

---

## TypeScript Configuration

**Critical Impact:** TypeScript configuration affects type checking across the entire project. Broken tsconfig = all TypeScript features broken.

### Strict Mode Safety

```json
{
  "compilerOptions": {
    // DANGEROUS: Disabling strict catches fewer errors
    "strict": false,  // Was true

    // SAFE: Keep strict true, enable specific flags
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

**Why Strict Mode Matters:**
- `strict: false` hides type errors until runtime
- Allows `any` implicitly (defeats purpose of TypeScript)
- Enables code like `undefined.property` to "work" during development
- Causes crashes in production

**Safe Pattern When Relaxing:**
```json
{
  "compilerOptions": {
    "strict": true,
    // Exception: Only relax when importing untyped legacy code
    "noImplicitAny": false  // Allow any for legacy compatibility
  }
}
```

### Include/Exclude Patterns Safety

```json
{
  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "tests/**/*.ts"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.spec.ts"  // Files to skip
  ]
}
```

**Dangerous Include Changes:**
```json
{
  // SAFE
  "include": ["src/**/*"],

  // DANGEROUS: Including everything
  "include": ["**/*"],  // Now type-checks node_modules, dist, etc.

  // DANGEROUS: Excluding source files
  "exclude": ["src"],  // Now won't type-check source!
}
```

### Module Resolution Settings

**Vite/Next.js Safe Default:**
```json
{
  "compilerOptions": {
    "moduleResolution": "bundler",  // For Vite, Next.js, esbuild
    "resolveJsonModule": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true
  }
}
```

**Breaking Change: Changing moduleResolution**
```json
{
  // WAS: "bundler" (supports modern imports)
  "moduleResolution": "node",  // NOW: Stricter resolution

  // Result: Import statements work differently
  // Some dynamic imports fail
  // Monorepo workspace resolution breaks
}
```

**Safe Module Resolution Patterns:**

| Tool | Resolution | Pattern |
|------|-----------|---------|
| Vite | bundler | Modern, flexible |
| Next.js | bundler | Modern, flexible |
| TypeScript Node | node16 | Strict, CommonJS-aware |
| tsc only | classic | Strict |
| Monorepo | node | Shared resolution |

---

## Feature Flags and Conditional Configuration

Feature flags allow adding features without risk of breaking existing functionality. They work in configuration through environment variables and runtime checks.

### Feature Flag Patterns

**Environment-Based Feature Flags:**
```typescript
// config/features.ts
export const FEATURES = {
  NEW_DASHBOARD: process.env.VITE_FEATURE_NEW_DASHBOARD === 'true',
  NEW_ANALYTICS: process.env.VITE_FEATURE_NEW_ANALYTICS === 'true',
  BETA_API: import.meta.env.VITE_BETA_API === 'true'
}

// components/Dashboard.tsx
import { FEATURES } from '@/config/features'

export function Dashboard() {
  if (FEATURES.NEW_DASHBOARD) {
    return <NewDashboard />  // Feature flag enabled
  }
  return <LegacyDashboard /> // Existing behavior
}
```

**Configuration-Driven Feature Flags:**
```json
{
  "features": {
    "newDashboard": {
      "enabled": false,
      "rollout": 0,
      "enabledForUsers": ["admin@company.com"]
    },
    "newAnalytics": {
      "enabled": true,
      "rollout": 100
    }
  }
}
```

**Safe Feature Flag Practices:**

1. **Never Nest Feature Flags:**
   ```typescript
   // DANGEROUS: Feature flag inside feature flag
   if (FEATURES.NEW_DASHBOARD) {
     if (FEATURES.BETA_CHARTS) {  // Nested - complexity explodes
       return <BetaCharts />
     }
   }

   // SAFE: Evaluate once at top level
   const showNewDashboard = FEATURES.NEW_DASHBOARD && !isOldBrowser()
   const showBetaCharts = FEATURES.BETA_CHARTS && userIsAdmin

   return (
     <div>
       {showNewDashboard && <NewDashboard />}
       {showBetaCharts && <BetaCharts />}
     </div>
   )
   ```

2. **Cache Flag State Outside Loops:**
   ```typescript
   // DANGEROUS: Flag checked in loop
   const items = data.map(item => {
     if (FEATURES.NEW_DISPLAY) {  // Checked for each item
       return <NewItemDisplay item={item} />
     }
     return <OldItemDisplay item={item} />
   })

   // SAFE: Evaluate once, use in loop
   const useNewDisplay = FEATURES.NEW_DISPLAY
   const items = data.map(item =>
     useNewDisplay
       ? <NewItemDisplay item={item} />
       : <OldItemDisplay item={item} />
   )
   ```

3. **Short-Lived Feature Flags:**
   ```typescript
   // Feature flags are not permanent configuration
   // Plan removal from day one

   // DO: Add comment with removal plan
   // FEATURE_FLAG: Remove by 2026-03-31 after A/B test completes
   if (FEATURES.NEW_CHECKOUT) {
     return <NewCheckout />
   }

   // DO: Track usage with metrics
   // DON'T: Leave feature flag in code indefinitely
   // DON'T: Add dependencies on feature flag being present
   ```

4. **Separate Flags from Configuration:**
   ```typescript
   // WRONG: Using feature flags for configuration
   const API_TIMEOUT = FEATURES.SLOW_API_ENABLED ? 30000 : 5000

   // RIGHT: Use actual configuration
   const API_TIMEOUT = parseInt(process.env.VITE_API_TIMEOUT) || 5000

   // RIGHT: Use feature flags only for feature visibility
   const showBetaFeature = FEATURES.BETA_ENABLED
   ```

**References:**
- [Feature Flags 101 and Best Practices](https://launchdarkly.com/blog/what-are-feature-flags/)
- [The 12 Commandments of Feature Flags (2025)](https://octopus.com/devops/feature-flags/feature-flag-best-practices/)
- [Feature Toggles - Martin Fowler](https://martinfowler.com/articles/feature-toggles.html)

---

## Package.json and Lockfile Safety

Package.json and lockfiles control dependency versions. Incorrect changes break builds and introduce security vulnerabilities.

### Adding Dependencies Safely

**Safe Pattern:**
```bash
# Use package manager to add (creates lockfile entry)
npm install new-package
yarn add new-package
pnpm add new-package

# DON'T: Manually edit package.json
# DON'T: Manually edit lockfile
```

**Package.json Structure Safety:**
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "new-dep": "^1.0.0"  // Safe: Caret allows minor updates
  },
  "devDependencies": {
    "typescript": "~5.3.0"  // Safe: Tilde locks minor version
  },
  "peerDependencies": {
    "react": ">=16.8.0 <19"  // Safe: Broad range for libraries
  }
}
```

**Dangerous Version Specifications:**
```json
{
  "dependencies": {
    "exact-version": "1.2.3",      // Blocks all updates
    "too-loose": "*",              // Allows any version - unsafe
    "beta-version": "2.0.0-beta.1" // Beta in production - risky
  }
}
```

### Peer Dependency Conflicts in Monorepos

**Monorepo Dependency Hell:**
```
Root package.json:
  react: 18.2.0

packages/app1:
  react: 18.1.0  (conflicts!)

packages/app2:
  react: 17.0.0  (major conflict!)

Result: Multiple React versions loaded, state breaks
```

**Safe Monorepo Pattern:**
```json
{
  "name": "monorepo-root",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

```json
{
  "name": "package-app1",
  "peerDependencies": {
    "react": ">=18.0.0 <19",
    "react-dom": ">=18.0.0 <19"
  }
}
```

**Never Do:**
```json
{
  // DANGEROUS: Different versions per package
  "dependencies": {
    "react": "17.0.0"  // Package has old React
  },
  "peerDependencies": {
    "react": "^18.0.0" // But expects new React - conflict
  }
}
```

### Script Preservation

**Safe Script Modification:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    // NEW: Add script following same pattern
    "type-check": "tsc --noEmit",
    // KEEP: Existing scripts unchanged
    "lint": "eslint src"
  }
}
```

**Dangerous Script Changes:**
```json
{
  // DANGEROUS: Replacing build script changes behavior
  "scripts": {
    "build": "webpack"  // Was vite - now configuration doesn't match
  }
}
```

### Lockfile Integrity

**Critical Rules:**
```bash
# DO: Commit lockfile (npm-lock.json, yarn.lock, pnpm-lock.yaml)
git add package-lock.json

# DO: Let package manager update lockfile
npm install

# DANGEROUS: Manually edit lockfile
vim package-lock.json  # Never do this

# DANGEROUS: Delete lockfile without reason
rm package-lock.json   # Will cause non-deterministic installs

# SAFE: If lockfile corrupted, delete both and reinstall
rm package-lock.json
npm install
git add package-lock.json
```

**References:**
- [pnpm package.json Documentation](https://pnpm.io/package_json)
- [npm package.json Documentation](https://docs.npmjs.com/cli/v8/configuring-npm/package-json/)
- [Monorepo Dependency Management](https://bit.dev/blog/painless-monorepo-dependency-management-with-bit-l4f9fzyw/)

---

## Common Breakage Patterns

### Pattern 1: Missing Environment Variables

**Symptom:** Application starts but crashes immediately with "Cannot read property of undefined"

**Root Cause:**
```typescript
// src/api.ts
const endpoint = process.env.VITE_API_ENDPOINT  // undefined if not set

// component.tsx
fetch(endpoint + '/data')  // TypeError: Cannot read property '+' of undefined
```

**Prevention:**
```typescript
// env.ts - Validate and document all variables
export const config = {
  API_ENDPOINT: assertEnvVar('VITE_API_ENDPOINT'),
  API_TIMEOUT: parseInt(process.env.VITE_API_TIMEOUT || '5000', 10)
}

function assertEnvVar(name: string): string {
  const value = process.env[name] ?? import.meta.env[name]
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`)
  }
  return value
}

// Start gracefully with error message instead of cryptic runtime error
```

### Pattern 2: Vite Plugin Conflicts

**Symptom:** Build succeeds but CSS is incorrect, styles missing, or duplicate modules

**Root Cause:**
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [
    react(),
    customCSSPlugin(),      // Also processes CSS
    tailwindPlugin()        // Also processes CSS - CONFLICT
  ]
})
```

**Prevention:**
```typescript
export default defineConfig({
  plugins: [
    // Only one CSS processor
    react(),
    // Document why each plugin is needed
    tailwindPlugin(),
    // NEW: Add new tools as preprocess hooks, not full plugins
  ],
  css: {
    postcss: './postcss.config.js'  // Centralize CSS processing
  }
})
```

### Pattern 3: TypeScript Path Alias Breaking All Imports

**Symptom:** After modifying tsconfig.json paths, all imports fail

**Root Cause:**
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["src/*"],
      "@components": ["src/components"]  // Changed from "@components/*"
    }
  }
}
```

```typescript
// Was: import { Button } from '@components/Button'
// Now: import { Button } from '@components'  // File not found
```

**Prevention:**
```typescript
// Before making tsconfig changes:
// 1. Run full type check
npm run type-check

// 2. Search for all imports of the path being changed
grep -r "@components" src/

// 3. Run tests after change
npm test

// 4. Rebuild and verify
npm run build
```

### Pattern 4: Tailwind Content Paths Missing Directory

**Symptom:** New components don't get styles, but no error message

**Root Cause:**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{jsx,tsx}'
    // Missing: './src/components/**/*.{jsx,tsx}'
  ]
}
```

```typescript
// src/components/NewButton.tsx - Won't get Tailwind classes!
export function NewButton() {
  return <button className="bg-blue-500 px-4">Click</button>
  // Styles silently don't load - no error!
}
```

**Prevention:**
```javascript
// After adding new directories, check content paths
module.exports = {
  content: [
    './index.html',
    './src/**/*.{jsx,tsx}',  // Catch-all for src
    // Or be explicit:
    './src/pages/**/*.{jsx,tsx}',
    './src/components/**/*.{jsx,tsx}',
    './src/layouts/**/*.{jsx,tsx}'
  ]
}

// Verify: Check that new components get styles after build
npm run build
// Manually inspect dist/index.css for new class names
```

### Pattern 5: PostCSS Plugin Order Breaking Styles

**Symptom:** CSS processes but output is malformed or incomplete

**Root Cause:**
```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('autoprefixer'),       // Adds vendor prefixes
    require('postcss-nested'),     // Expands nested CSS
    require('tailwindcss'),        // Generates Tailwind classes
    require('cssnano')             // Minifies (should be last!)
  ]
}

// If cssnano runs before tailwindcss, Tailwind classes get lost
```

**Prevention:**
```javascript
module.exports = {
  plugins: [
    // Order matters - transformation then optimization
    require('postcss-import'),     // 1. Import CSS files
    require('tailwindcss'),        // 2. Generate Tailwind classes
    require('autoprefixer'),       // 3. Add browser prefixes
    require('cssnano')             // 4. Minify last
  ]
}

// Document why each plugin is ordered this way
```

### Pattern 6: Package.json Peer Dependency Conflicts

**Symptom:** "peer dep missing" warning, or multiple versions of same package loaded

**Root Cause:**
```json
{
  "dependencies": {
    "react": "^17.0.0"
  },
  "peerDependencies": {
    "react": ">=18.0.0"
  }
}
```

**Prevention:**
```json
{
  "dependencies": {
    "react": "^18.2.0"  // Match peer dependency
  },
  "peerDependencies": {
    "react": ">=18.0.0 <19"  // Broad enough for flexibility
  }
}

// Run this to detect conflicts:
// npm ls react
// pnpm audit
// yarn audit
```

### Pattern 7: Runtime Config Changes Need Restart

**Symptom:** Changed .env file but app uses old values

**Root Cause:**
```bash
# Development server is running
# Changed .env file
VITE_API_ENDPOINT=https://old-api.com
# to
VITE_API_ENDPOINT=https://new-api.com

# But server never reloaded - still using old value!
```

**Prevention:**
```bash
# MUST restart after changing .env
npm start  # Stop (Ctrl+C)
npm start  # Restart - picks up new values
```

**Better Solution:**
```typescript
// Use ConfigLoader that detects changes
// Or use environment-specific build:
npm run build:prod  # Builds with .env.production
npm run build:dev   # Builds with .env.development
```

---

## Configuration Validation Checklist

### Pre-Feature-Addition Checklist

Before adding any new configuration:

- [ ] **Environment Variables**
  - [ ] Do I need a new env variable?
  - [ ] Is it prefixed correctly (VITE_, NEXT_PUBLIC_, REACT_APP_)?
  - [ ] Have I added it to .env.example?
  - [ ] Is it marked as required in documentation?
  - [ ] Have I added TypeScript type definitions?

- [ ] **Build Configuration**
  - [ ] Does my change extend existing patterns?
  - [ ] Am I adding or replacing configuration?
  - [ ] Does my change conflict with existing plugins?
  - [ ] Have I tested the build?
  - [ ] Does build size increase significantly?

- [ ] **TypeScript**
  - [ ] Have I checked tsconfig.json paths?
  - [ ] Do new imports match existing path patterns?
  - [ ] Does type-checking still pass?
  - [ ] Have I added type definitions for new modules?

- [ ] **Tailwind**
  - [ ] Do content paths include new directories?
  - [ ] Am I extending theme or replacing it?
  - [ ] Have I tested that styles load?
  - [ ] Any plugin conflicts?

- [ ] **Package.json**
  - [ ] Have I used npm install/yarn add?
  - [ ] Do peer dependencies align?
  - [ ] Is lockfile updated?
  - [ ] No conflicts in npm ls output?

- [ ] **Testing**
  - [ ] Does full build pass?
  - [ ] Do tests still pass?
  - [ ] Does app start without errors?
  - [ ] Are there no console warnings related to config?

### Post-Feature-Addition Testing

After adding configuration changes:

```bash
# Full verification sequence
npm run build        # Check compilation
npm run type-check   # Verify types
npm test             # Run test suite
npm run lint         # Check code quality
npm start            # Test dev server startup

# Visual verification
# 1. Check that app loads in browser
# 2. Check browser console for errors
# 3. Check styles load correctly
# 4. Check API calls work
```

### Emergency Rollback

If configuration breaks the application:

```bash
# Get original configuration
git diff HEAD~1 vite.config.ts      # See what changed
git diff HEAD~1 tsconfig.json

# Revert safely
git checkout HEAD -- vite.config.ts  # Restore one file
git diff                             # Verify only config changed
npm install                          # Reinstall with old config
npm start                            # Test
```

---

## Framework-Specific Patterns

### Next.js Environment Variables

**Three-Tier Pattern:**
```bash
# .env (committed, safe defaults)
NEXT_PUBLIC_APP_NAME=MyApp
DATABASE_URL=postgresql://localhost

# .env.local (git-ignored, dev overrides)
NEXT_PUBLIC_DEBUG=true
DATABASE_PASSWORD=devpassword

# .env.production (committed, production config)
NEXT_PUBLIC_DEBUG=false
# DATABASE_PASSWORD should NOT be here - use secrets instead
```

**Critical Build-Time Behavior:**
```typescript
// next.config.js - Understand timing
export default {
  env: {
    NEXT_PUBLIC_BUILD_TIME: new Date().toISOString(),
    API_KEY: process.env.API_KEY  // Only available at build time
  }
}

// During build:
// 1. .env and .env.production loaded
// 2. All env values embedded into JavaScript
// 3. Production deployment uses hardcoded values
// 4. Runtime env changes have NO EFFECT
```

**Safe Next.js Pattern:**
```typescript
// lib/config.ts
export const config = {
  appName: process.env.NEXT_PUBLIC_APP_NAME,
  apiEndpoint: process.env.NEXT_PUBLIC_API_ENDPOINT,
  // Server-only access:
  dbPassword: process.env.DATABASE_PASSWORD
}

// pages/api/data.ts - Server-side: can access all env
export default async function handler(req, res) {
  const db = connect(process.env.DATABASE_PASSWORD)
  return res.json(await db.getData())
}

// components/Client.tsx - Client-side: only public vars
export function Component() {
  return <a href={config.apiEndpoint}>API</a>
}
```

---

### React Vite Environment Variables

**Pattern with TypeScript:**
```typescript
// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_API_ENDPOINT: string
  readonly VITE_DEBUG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// src/config.ts
export const config = {
  appTitle: import.meta.env.VITE_APP_TITLE,
  apiEndpoint: import.meta.env.VITE_API_ENDPOINT,
  debug: import.meta.env.VITE_DEBUG === 'true'
}
```

**Safe Usage:**
```typescript
// src/api.ts
import { config } from './config'

export const API_BASE = config.apiEndpoint

export async function fetchData() {
  const response = await fetch(`${API_BASE}/data`)
  if (config.debug) {
    console.log('API Response:', response)
  }
  return response.json()
}
```

---

## Conclusion

Configuration safety is the foundation of stability. Every configuration file you modify is a potential point of catastrophic failure. Apply these principles:

1. **Understand the impact** - Know what each config setting controls
2. **Extend, don't replace** - Add to existing patterns rather than replacing them
3. **Validate early** - Check configuration during development, not in production
4. **Document changes** - Add comments explaining why each config entry exists
5. **Test completely** - Run full build and test suite after any config change
6. **Plan rollbacks** - Know how to revert if something breaks
7. **Use version control** - Never make configuration changes without git tracking

Configuration is the most fragile part of your application. Treat it with appropriate caution.

---

## Quick Reference: Safe Modification Patterns

### Adding Environment Variables
```bash
# Safe
1. Add to .env and .env.example
2. Add TypeScript types
3. Document purpose
4. Restart dev server
5. Test application

# Unsafe
1. Add only to .env (forget .env.example)
2. No types defined
3. Use different names in different places
4. Don't restart
5. Hope it works
```

### Adding Build Configuration
```typescript
// Safe
plugins: [
  ...existingPlugins,
  newPlugin()  // Add, don't replace
]

// Unsafe
plugins: [
  newPlugin(),  // Replace entire plugins array
  existingPlugin()
]
```

### Adding Tailwind Classes
```javascript
// Safe
content: [
  ...existingPaths,
  './new-directory/**/*.{jsx,tsx}'
]

// Unsafe
content: [
  './new-directory/**/*.{jsx,tsx}'  // Replace entire paths
]
```

### Modifying Dependencies
```bash
# Safe
npm install new-package
git add package.json package-lock.json

# Unsafe
vim package.json              # Manual editing
rm package-lock.json          # Delete without reason
git add package.json only     # Forget lockfile
```

---

## Additional Resources

- **Vite Documentation:** [https://vite.dev/](https://vite.dev/)
- **Next.js Documentation:** [https://nextjs.org/docs](https://nextjs.org/docs)
- **Tailwind CSS Documentation:** [https://tailwindcss.com/docs](https://tailwindcss.com/docs)
- **TypeScript Configuration:** [https://www.typescriptlang.org/tsconfig/](https://www.typescriptlang.org/tsconfig/)
- **Webpack Documentation:** [https://webpack.js.org/](https://webpack.js.org/)
- **PostCSS Documentation:** [https://postcss.org/](https://postcss.org/)

---

*This reference document should be updated when new framework versions introduce breaking changes or new patterns emerge in the ecosystem. Last review: 2026-02-26*
