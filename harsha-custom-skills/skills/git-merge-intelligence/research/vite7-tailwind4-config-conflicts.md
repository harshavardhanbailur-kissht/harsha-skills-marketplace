# Vite 7 & Tailwind CSS 4 Configuration Conflict Patterns: Research Guide

**Last Updated**: April 2026

---

## Table of Contents

1. [Vite Configuration Conflicts](#vite-configuration-conflicts)
2. [Tailwind CSS 4 Changes](#tailwind-css-4-changes)
3. [PostCSS Configuration Conflicts](#postcss-configuration-conflicts)
4. [Font and Asset Conflicts](#font-and-asset-conflicts)
5. [Resolution Strategies](#resolution-strategies)

---

## Vite Configuration Conflicts

### 1. Plugin Ordering Sensitivity (vite.config.ts)

When multiple branches add different Vite plugins, conflicts arise from plugin execution order rather than the code itself.

#### Key Principles

**Plugin Resolution Order** follows a deterministic sequence based on the `enforce` property:

1. `@vitejs/plugin-alias` (always first)
2. Plugins with `enforce: 'pre'` (run before Vite core)
3. Vite core plugins
4. Plugins without enforce specification
5. Vite build plugins
6. Plugins with `enforce: 'post'` (run after Vite core)
7. Vite post build plugins (minify, manifest, reporting)

**Reference**: [Vite Plugin API - Using Plugins](https://vite.dev/guide/using-plugins)

#### Common Conflict Scenarios

**Scenario A: Transform Plugin Order**
```typescript
// Branch A
plugins: [
  react(),
  tailwind(),
]

// Branch B
plugins: [
  vue(),
  tailwind(),
]

// Resolution: Consider enforce property
plugins: [
  react({ enforce: 'pre' }),
  vue(),
  tailwind(),
]
```

**Scenario B: Multiple Framework Plugins**
When merging branches that support different frameworks (React vs Vue), position them before tailwind() to ensure proper CSS processing order.

#### Debugging Strategy
- Enable debug logging: `vite build --debug`
- Use [vite-plugin-inspect](https://github.com/antfu/vite-plugin-inspect) to visualize the plugin execution stack
- Check console output for plugin ordering messages

#### Resolution Approach
- **Keep both plugins** if they serve different purposes
- **Use enforce** to explicitly order conflicting plugins
- **Test build output** to verify CSS is processed correctly
- **Never assume** alphabetical order—always verify with `--debug` flag

---

### 2. Vite 5/6/7 Migration Changes

Upgrading through Vite versions introduces breaking changes that create configuration conflicts.

#### Vite 5 → Vite 6 Breaking Changes

**CSS Output File Naming**
```typescript
// Vite 5 (old)
// build.lib.cssFileName defaults to 'style.css'

// Vite 6 (new, breaking)
// build.lib.cssFileName defaults to package.json 'name' field

// Resolution: Explicit configuration
export default {
  build: {
    lib: {
      cssFileName: 'style', // Forces 'style.css' like v5
    }
  }
}
```

**Condition Handling in resolve.conditions**
```typescript
// Vite 5 behavior: automatically adds internal conditions
resolve: {
  conditions: [] // Vite added some internally
}

// Vite 6 behavior: does NOT add internal conditions
resolve: {
  conditions: ['module', 'browser', 'default'] // Must be explicit
}
```

**Glob Pattern Braces**
- Vite 6 **no longer supports** range braces: `{01..03}` and incremental braces: `{2..8..2}`
- Migrate patterns to explicit lists if used in `include`/`exclude`

**Vite Runtime API → Module Runner API**
```typescript
// Vite 5 (experimental)
import { createViteRuntime } from 'vite'

// Vite 6 (breaking)
// Use Environment API and Module Runner instead
import { createEnvironment } from 'vite'
```

**Reference**: [Vite Migration from v5](https://v6.vite.dev/guide/migration)

#### Vite 6 → Vite 7 Breaking Changes

**CSS Minification Strategy**
```typescript
// Vite 7: Lightning CSS is default (faster)
// If you need esbuild behavior:
export default {
  build: {
    cssMinify: 'esbuild'
  }
}
```

**Import.meta.hot.accept() Changes**
```typescript
// Vite 6 (old)
import.meta.hot.accept('./path/to/module.js')

// Vite 7 (breaking)
import.meta.hot.accept(import.meta.url)
// OR use explicit module ID instead of URL
```

**Package.json resolve.mainFields**
```typescript
// Vite 7: No longer uses file content heuristics
// When both 'browser' and 'module' fields exist:
// Respects the order in resolve.mainFields

resolve: {
  mainFields: ['browser', 'module', 'main']
}
```

**splitVendorChunkPlugin Deprecation**
```typescript
// Old (deprecated in v5.2.7, removed in v7)
import { splitVendorChunkPlugin } from 'vite'
plugins: [splitVendorChunkPlugin()]

// New approach
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom']
        }
      }
    }
  }
}
```

**Reference**: [Vite Migration from v6](https://v7.vite.dev/guide/migration)

#### Merge Conflict Resolution

When merging branches with different Vite versions:

1. **Check target version** in package.json
2. **Identify breaking changes** between versions
3. **Update config** for ALL changes, not just conflicting sections
4. **Test build output** with `vite build`
5. **Verify type compatibility** if using TypeScript

---

### 3. Environment Variable Handling (.env files)

Vite loads environment variables in a specific precedence order, which creates conflicts when .env files are managed differently.

#### Environment Variable Priority Hierarchy

1. **Already-set OS environment variables** (highest priority, never overwritten)
2. **Mode-specific .env files** (e.g., `.env.production`, `.env.development`)
3. **Generic .env files** (.env, .env.local)

#### Key Rules

**Timing of Loading**
```typescript
// WRONG: Trying to use .env vars during config evaluation
export default {
  server: {
    port: process.env.VITE_PORT // undefined!
  }
}

// CORRECT: Use loadEnv() function
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    server: {
      port: env.VITE_PORT || 3000
    }
  }
})
```

Vite **deliberately delays** loading .env files until after the config has been resolved, because the set of files to load depends on config options like `root` and `envDir`.

**Reference**: [Vite Env Variables and Modes](https://vite.dev/guide/env-and-mode)

#### Naming Convention

All client-accessible environment variables **must be prefixed with `VITE_`**:
- `VITE_API_URL=...` ✓ (exposed to client)
- `API_URL=...` ✗ (ignored by Vite, not exposed)
- `SECRET_KEY=...` ✗ (never expose secrets with VITE_ prefix)

#### Merge Conflict Scenarios

**Scenario: Different .env configurations across branches**

```
# .env.production (from branch A)
VITE_API_URL=https://prod-api.example.com
VITE_LOG_LEVEL=error

# .env.production (from branch B)
VITE_API_URL=https://api.example.com
VITE_ANALYTICS_ID=ua-123456
```

**Resolution**:
- Keep **both** entries if they serve different purposes
- Use environment-specific overrides (`.env.staging`, `.env.local`)
- Do NOT rely on .env file merge—document expectations in README

#### Resolution Approach

- Always use `loadEnv()` when reading .env values in vite.config.ts
- Document which .env files are required
- Use `.env.example` to track expected variables
- For conflicting values, defer to production-safe defaults or require explicit user override

---

### 4. Build Configuration Conflicts

Build options like `rollupOptions`, `outDir`, and `base` create structural conflicts when both branches modify them.

#### rollupOptions Merging

```typescript
// Vite MERGES user-provided rollupOptions with internal Rollup options
export default {
  build: {
    rollupOptions: {
      input: 'src/index.js',
      output: {
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js'
      }
    }
  }
}
```

**Reference**: [Vite Build Options](https://vite.dev/config/build-options)

#### Known Merging Limitations

**Issue 1: Array Format Not Supported**
```typescript
// WRONG: Vite doesn't support RollupOptions[]
build: {
  rollupOptions: [
    { /* option A */ },
    { /* option B */ }
  ]
}
// Result: "Unknown input options" error

// CORRECT: Single object with deep merging
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react'],
        utils: ['lodash']
      }
    }
  }
}
```

**Issue 2: Plugin-Defined rollupOptions Conflicts**
When multiple plugins define `rollupOptions`, they don't merge automatically. Resolution:

```typescript
// Merge at config level explicitly
export default {
  build: {
    rollupOptions: {
      // Combine from both plugin sources
      output: {
        ...pluginAOutput,
        ...pluginBOutput,
      }
    }
  }
}
```

**Issue 3: Output Path Conflicts**
```typescript
// CONFLICTING: Can't have both
build: {
  rollupOptions: {
    output: {
      file: 'dist/bundle.js',     // Specific file
      dir: 'dist'                  // Directory
    }
  }
}

// RESOLVED: Choose one pattern
build: {
  rollupOptions: {
    output: [{
      file: 'dist/index.js'  // ESM entry
    }, {
      file: 'dist/index.cjs' // CommonJS entry
    }]
  }
}
```

#### outDir and base Conflicts

```typescript
// Branch A: Multi-tenant setup
export default {
  build: {
    outDir: 'dist/client'
  }
}

// Branch B: SPA with base path
export default {
  base: '/app/',
  build: {
    outDir: 'dist'
  }
}

// Resolution: Assess the actual requirements
export default {
  base: '/app/',
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        assetFileNames: '[name].[hash][extname]'
      }
    }
  }
}
```

#### Resolution Approach

1. **Understand merge semantics**: User config merges INTO Vite's internal config
2. **Test output structure**: Run `vite build` and verify dist/ layout
3. **Avoid plugin rollupOptions**: Define output options at top level
4. **Use explicit paths**: Always specify both entry AND output patterns
5. **Document output structure**: Keep README with build artifact layout

---

### 5. SSR Configuration Conflicts

SSR (Server-Side Rendering) configuration creates conflicts when the same modules are resolved differently for client vs. server.

#### Core SSR Configuration

```typescript
export default {
  ssr: {
    // External: Don't bundle these (expect them in server environment)
    external: ['express', '@db/driver'],

    // No-external: DO bundle these (not available in server environment)
    noExternal: ['some-universal-lib'],

    // Resolution conditions for SSR-specific exports
    resolve: {
      conditions: ['node', 'module'], // Not 'browser'
      externalConditions: ['node']
    }
  }
}
```

#### resolveId Hook SSR Flag

```typescript
// Plugin receives ssr flag in options
export default function myPlugin() {
  return {
    resolveId(id, importer, options) {
      if (options?.ssr) {
        // Handle SSR resolution differently
        return id.replace('.cjs', '.mjs')
      }
      // Client resolution
      return null
    }
  }
}
```

**Reference**: [Vite SSR Options](https://vite.dev/config/ssr-options)

#### Conflict Scenarios

**Scenario: External vs. No-External Conflict**
```typescript
// Branch A: Externalize auth library
ssr: { external: ['@auth/provider'] }

// Branch B: Bundle auth library
ssr: { noExternal: ['@auth/provider'] }

// Resolution: Test both approaches
// If library has side effects → external
// If library needs bundling for dependencies → noExternal
export default {
  ssr: {
    external: ['@auth/provider'],
    resolve: {
      conditions: ['node', 'module', 'import']
    }
  }
}
```

**Scenario: Condition Handling Differences**
```typescript
// Vite 5 default behavior (automatic)
ssr: {
  resolve: {
    conditions: [] // Vite added some internally
  }
}

// Vite 6+ required behavior (explicit)
ssr: {
  resolve: {
    conditions: ['node', 'module', 'import'],
    externalConditions: ['node']
  }
}
```

#### Resolution Approach

1. **Identify module type**: Browser-only, server-only, or universal?
2. **Test ssrLoadModule**: Use Vite's `ssrLoadModule()` to verify resolution
3. **Check resolve.conditions**: Ensure both client and SSR have correct conditions
4. **Avoid ssr flag inconsistency**: Plugin resolveId() must handle both paths
5. **Document decisions**: Clear comments on external vs. noExternal rationale

---

### 6. Dev Server Proxy Configuration Conflicts

Multiple branches may add different proxy rules for API development, creating conflicts that can't be auto-merged.

#### Proxy Configuration Basics

```typescript
export default {
  server: {
    proxy: {
      // Simple proxy
      '/api': 'http://localhost:3001',

      // Advanced with options
      '/socket': {
        target: 'http://localhost:3002',
        ws: true, // WebSocket support
        changeOrigin: true,
        pathRewrite: { '^/socket': '' }
      },

      // RegExp patterns
      '^/v[0-9]+/api': {
        target: 'http://localhost:3003',
        changeOrigin: true
      }
    }
  }
}
```

**Reference**: [Vite Server Options](https://vite.dev/config/server-options)

#### Important Rules

**Base Path Prefix**
```typescript
// If using non-relative base:
export default {
  base: '/admin/',
  server: {
    proxy: {
      // MUST include base prefix
      '/admin/api': 'http://localhost:3001',
      // NOT just '/api'
    }
  }
}
```

**RegExp Pattern Format**
```typescript
// Keys starting with ^ are interpreted as RegExp
'^/api/v[0-9]+': 'http://localhost:3001' // Valid regex
'/api': 'http://localhost:3001'           // String match

// Remember: ^ indicates regex
'^/static': 'http://cdn.example.com'      // Regex
```

#### Conflict Scenarios

**Scenario A: Multiple Microservices**
```typescript
// Branch A: Frontend + Auth service
server: {
  proxy: {
    '/api/auth': 'http://localhost:3001',
  }
}

// Branch B: Frontend + Notifications service
server: {
  proxy: {
    '/api/notifications': 'http://localhost:3002',
  }
}

// Resolution: MERGE both proxy routes
export default {
  server: {
    proxy: {
      '/api/auth': 'http://localhost:3001',
      '/api/notifications': 'http://localhost:3002',
      // Consider catch-all for other /api routes
      '/api': 'http://localhost:3003'
    }
  }
}
```

**Scenario B: WebSocket vs. HTTP Conflict**
```typescript
// Branch A: REST API only
'/api': { target: 'http://localhost:3001', ws: false }

// Branch B: Real-time with WebSocket
'/api': { target: 'http://localhost:3001', ws: true }

// Resolution: Enable WebSocket (safe for both)
'/api': {
  target: 'http://localhost:3001',
  ws: true,
  changeOrigin: true
}
```

**Scenario C: Path Rewrite Conflicts**
```typescript
// Branch A: Strips /api prefix
'/api': {
  target: 'http://localhost:3001',
  pathRewrite: { '^/api': '' }
}

// Branch B: Keeps /api prefix
'/api': {
  target: 'http://localhost:3001'
}

// Resolution: Match backend expectations
// Test which pattern your backend requires
```

#### Resolution Approach

1. **List all proxy routes**: Document what each branch adds
2. **Check for conflicts**: Same path with different targets = conflict
3. **Merge carefully**: Ensure catch-all routes don't shadow specific routes
4. **Test locally**: `npm run dev` and verify API calls work
5. **Order matters**: Check specific paths before general paths

#### HMR (Hot Module Reload) with Proxies

```typescript
// If Vite is behind a reverse proxy:
export default {
  server: {
    hmr: {
      protocol: 'wss',
      host: 'example.com',
      port: 443
    }
  }
}
```

---

## Tailwind CSS 4 Changes

### 1. The New @theme CSS Variable System

Tailwind CSS 4 fundamentally shifts from JavaScript configuration to CSS-first design using the `@theme` directive.

#### Architecture Shift

**Tailwind v3 Approach** (JavaScript-based):
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    colors: {
      primary: '#0a7ea4',
      secondary: '#f59e0b'
    },
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif']
      }
    }
  }
}
```

**Tailwind v4 Approach** (CSS-first):
```css
/* input.css */
@import "tailwindcss";

@theme {
  --color-primary: #0a7ea4;
  --color-secondary: #f59e0b;
  --font-sans: 'Inter', sans-serif;
}
```

**Reference**: [Tailwind CSS v4.0 Blog](https://tailwindcss.com/blog/tailwindcss-v4)

#### Design Token Naming and Utility Generation

```css
@theme {
  /* Color variables generate .text-primary, .bg-primary, etc. */
  --color-primary: #0a7ea4;
  --color-secondary: #f59e0b;

  /* Font variables generate .font-sans, .font-serif */
  --font-sans: ui-sans-serif, system-ui, sans-serif;
  --font-mono: 'Courier New', monospace;

  /* Spacing variables generate .w-xl, .h-lg, etc. */
  --spacing-xl: 2rem;
  --spacing-lg: 1.5rem;

  /* Border radius variables */
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
}
```

#### Regular CSS Variables vs. Theme Variables

```css
/* @theme generates utility classes */
@theme {
  --color-brand: #3490dc;  /* Creates .text-brand, .bg-brand, etc. */
}

/* :root does NOT generate utility classes */
:root {
  --custom-value: 100px;   /* Regular CSS variable, no .custom-value utility */
}

/* Use custom values with css() helper */
.my-custom {
  width: css('var(--custom-value)');
}
```

#### Component-Scoped Theme Variables

```css
/* Component-specific theme overrides */
.theme-dark {
  --color-bg: #1f2937;
  --color-text: #f3f4f6;
}
```

#### Namespace Conventions

Tailwind v4 generates utilities based on CSS variable namespace:

| Namespace | Generates | Example |
|-----------|-----------|---------|
| `--color-*` | Color utilities | `--color-primary` → `.text-primary`, `.bg-primary` |
| `--font-*` | Font utilities | `--font-sans` → `.font-sans` |
| `--spacing-*` | Space utilities | `--spacing-xl` → `.w-xl`, `.h-xl`, `.m-xl` |
| `--radius-*` | Radius utilities | `--radius-md` → `.rounded-md` |
| `--shadow-*` | Shadow utilities | `--shadow-lg` → `.shadow-lg` |
| `--blur-*` | Blur utilities | `--blur-md` → `.blur-md` |

---

### 2. CSS-First Configuration Benefits

Tailwind v4 eliminates the need for a separate JavaScript config file for most projects.

#### No More tailwind.config.js for Basic Projects

```bash
# Vite + Tailwind v3
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
# Creates: tailwind.config.js, postcss.config.js

# Vite + Tailwind v4
npm install -D @tailwindcss/postcss
# No config files needed—configure purely in CSS!
```

#### When You DO Need tailwind.config.js in v4

```javascript
// Only needed for:
// 1. Plugins (legacy JS plugins)
// 2. Advanced preprocessor options
// 3. Content path customization

export default {
  // Rarely needed now
  content: ['./src/**/*.{html,tsx}'],

  // For legacy plugins only
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms')
  ]
}
```

#### Content Path Discovery

```css
/* Tailwind v4 auto-discovers from:
   - HTML files in project
   - JSX/TSX component files
   - No explicit content config usually needed
*/

@import "tailwindcss";

@theme {
  --color-primary: #0a7ea4;
}
```

---

### 3. PostCSS Configuration Interaction Changes

Tailwind v4 changes how it integrates with PostCSS, moving from a plugin-based approach to a first-class integration.

#### Tailwind v3 PostCSS Setup

```javascript
// postcss.config.js (v3)
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    cssnano: {}
  }
}
```

#### Tailwind v4 PostCSS Setup

```javascript
// postcss.config.js (v4)
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},  // Still needed for older browser support
    // cssnano still works
  }
}
```

**Key Change**: `tailwindcss` → `@tailwindcss/postcss` (separate package)

#### Plugin Order (Still Matters!)

```javascript
// Recommended order:
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},      // 1st: Tailwind transforms
    'postcss-import': {},             // 2nd: Process imports (if used)
    'tailwindcss/nesting': {},        // 3rd: Nested CSS support (v3 compat)
    autoprefixer: {},                 // 4th: Add vendor prefixes
    // cssnano goes AFTER for minification
  }
}
```

**Reference**: [Tailwind CSS Installation - PostCSS](https://tailwindcss.com/docs/installation)

#### Autoprefixer Handling

```javascript
// v4 Behavior: LightningCSS handles many prefixes automatically
// Autoprefixer becomes optional for most cases

// BUT still include it for:
// - Old browser support (IE 11, etc.)
// - Complex vendor-specific features
// - When LightningCSS doesn't cover your use case

module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {
      overrideBrowserslist: ['> 1%', 'last 2 versions']
    }
  }
}
```

---

### 4. Font Source Resolution Changes

Tailwind v4 changes how fonts are imported and resolved, affecting local and web fonts.

#### Tailwind v3 Font Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace']
    }
  }
}
```

```css
/* Fonts defined separately in CSS */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700');

@layer base {
  @font-face {
    font-family: 'JetBrains Mono';
    src: url('/fonts/jetbrains-mono.woff2') format('woff2');
  }
}
```

#### Tailwind v4 Font Configuration

```css
@import "tailwindcss";

@theme {
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700');

@font-face {
  font-family: 'JetBrains Mono';
  src: url('/fonts/jetbrains-mono.woff2') format('woff2');
  font-display: swap;
}
```

#### Local Font Files (Public Directory)

```css
/* Fonts in /public/fonts/ */
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom-font.woff2') format('woff2');
  font-display: swap;
}

@theme {
  --font-custom: 'CustomFont', serif;
}
```

**Critical Rule**: Use **root-absolute paths** (starting with `/`), not relative paths.
- ✓ Correct: `url('/fonts/font.woff2')`
- ✗ Wrong: `url('./fonts/font.woff2')`

#### Font Format Specifications

```css
/* CORRECT format declarations */
@font-face {
  src: url('/fonts/font.woff2') format('woff2');
  src: url('/fonts/font.woff') format('woff');
  src: url('/fonts/font.ttf') format('truetype');  /* NOT 'ttf' */
  src: url('/fonts/font.eot') format('embedded-opentype');
  src: url('/fonts/font.otf') format('opentype');
}

/* Common mistake */
/* WRONG: format('ttf') */
/* CORRECT: format('truetype') */
```

#### Variable Fonts in Tailwind v4

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900');

@font-face {
  font-family: 'InterVar';
  src: url('/fonts/inter-var.woff2') format('woff2-variations');
  font-weight: 100 900;
}

@theme {
  --font-sans: 'InterVar', system-ui;
}
```

#### Resolution Approach

1. **Always use `/` prefix** for public assets
2. **Verify format names** (common mistake: `ttf` should be `truetype`)
3. **Place fonts in `/public/fonts/`** folder
4. **Use @font-face before @theme** that references fonts
5. **Test in development** with `npm run dev` before build

---

### 5. Plugin System Changes

Tailwind v4 introduces a new plugin approach while maintaining backward compatibility with JavaScript plugins.

#### Tailwind v3 JavaScript Plugins

```javascript
// tailwind.config.js
const plugin = require('tailwindcss/plugin')

module.exports = {
  plugins: [
    plugin(function({ addUtilities, matchVariant }) {
      addUtilities({
        '.snap-type-inline': {
          'scroll-snap-type': 'inline',
        }
      })

      matchVariant('nth', (value) => {
        return `.nth-child(${value}) &`
      })
    })
  ]
}
```

#### Tailwind v4 CSS-Based Plugins

```css
@import "tailwindcss";

@utility snap-type-inline {
  scroll-snap-type: inline;
}

@custom-variant nth (value) {
  .nth-child(value) &
}

@theme {
  --color-primary: #0a7ea4;
}
```

#### Using Legacy JavaScript Plugins in v4

```css
@import "tailwindcss";

/* Load legacy v3-style JS plugins */
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
@plugin "./my-plugin.js";

@theme {
  --color-primary: #0a7ea4;
}
```

#### New Plugin Directives

| Directive | Purpose | v3 Equivalent |
|-----------|---------|---------------|
| `@utility` | Define custom utilities | `addUtilities()` |
| `@custom-variant` | Define custom variants | `matchVariant()`, `addVariant()` |
| `@plugin` | Load JS plugins | `plugins: [...]` |
| `@theme` | Define design tokens | `theme: { ... }` |

#### Custom Utilities Example

```css
/* v4 CSS approach */
@utility custom-glow {
  @apply rounded-lg shadow-lg;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Can be used as */
<div class="custom-glow">...</div>
```

#### Conditional Custom Utilities

```css
@utility btn-primary {
  @apply px-4 py-2 rounded font-semibold text-white bg-primary;

  &:hover {
    opacity: 0.9;
  }
}

@custom-variant hocus {
  &:hover,
  &:focus {
    @media (hover: none) {
      &:focus-visible {
        ...
      }
    }
  }
}
```

#### Migration Path from v3

```javascript
// v3 Plugin before migration
const plugin = require('tailwindcss/plugin')

module.exports = {
  plugins: [
    plugin(function({ addBase, addComponents, addUtilities }) {
      addBase({ 'html': { scrollBehavior: 'smooth' } })
      addComponents({ '.card': { borderRadius: '0.5rem', padding: '1rem' } })
      addUtilities({ '.line-clamp-1': { overflow: 'hidden', 'text-overflow': 'ellipsis' } })
    })
  ]
}
```

```css
/* v4 Equivalent in CSS */
@import "tailwindcss";

@layer base {
  html {
    scroll-behavior: smooth;
  }
}

@layer components {
  .card {
    @apply rounded-lg p-4;
  }
}

@utility line-clamp-1 {
  overflow: hidden;
  text-overflow: ellipsis;
}
```

#### Resolution Approach

1. **Prefer CSS-based plugins** for new projects
2. **Legacy plugins still work** with `@plugin` directive
3. **No need for tailwind.config.js** if using CSS plugins only
4. **Test utility generation** by running build and inspecting output
5. **Document custom utilities** in code comments

---

## PostCSS Configuration Conflicts

### 1. Plugin Order Sensitivity

PostCSS processes plugins sequentially, and order matters critically.

#### Standard Plugin Order

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    'postcss-import': {},              // 1. Resolve @import
    'postcss-mixins': {},              // 2. Expand mixins
    '@tailwindcss/postcss': {},        // 3. Tailwind directives
    'postcss-nested': {},              // 4. Unwrap nested selectors
    'autoprefixer': {},                // 5. Add vendor prefixes
    'cssnano': {}                      // 6. Minify (only for production)
  }
}
```

#### Why Order Matters

- **`postcss-import` FIRST**: Must resolve imports before Tailwind sees them
- **`@tailwindcss/postcss` EARLY**: Needs to process @theme, @utility before other plugins
- **`autoprefixer` LATE**: Should prefix already-processed Tailwind output
- **`cssnano` LAST**: Minifies the final result

#### Common Ordering Mistakes

```javascript
// WRONG: Autoprefixer before Tailwind
{
  'autoprefixer': {},
  '@tailwindcss/postcss': {}
}

// Problem: Autoprefixer can't prefix Tailwind utilities it hasn't seen yet

// CORRECT: Tailwind before Autoprefixer
{
  '@tailwindcss/postcss': {},
  'autoprefixer': {}
}
```

---

### 2. Autoprefixer Configuration Conflicts

When both branches customize autoprefixer, conflicts arise from different browser target specifications.

#### Browser Target Configuration

```javascript
// Branch A: Modern browsers only
module.exports = {
  plugins: {
    'autoprefixer': {
      overrideBrowserslist: ['last 2 versions', 'not dead']
    }
  }
}

// Branch B: Legacy browser support
module.exports = {
  plugins: {
    'autoprefixer': {
      overrideBrowserslist: ['> 0.5%', 'last 2 versions', 'Firefox ESR']
    }
  }
}

// Resolution: Choose based on product requirements
// Modern (no IE11): last 2 versions, > 1%
// Legacy: Include Firefox ESR, add specific versions
module.exports = {
  plugins: {
    'autoprefixer': {
      overrideBrowserslist: ['> 1%', 'last 2 versions']
    }
  }
}
```

#### Avoiding Double-Processing

```bash
# If Autoprefixer runs in your build pipeline elsewhere:
vite build --no-autoprefixer
# OR configure in vite.config.ts:

export default {
  build: {
    cssMinify: false // Disable if pipeline handles it
  }
}
```

---

### 3. postcss-import Conflicts

When modifying CSS import paths or order, conflicts arise with CSS preprocessing.

#### Import Resolution

```css
/* index.css */
@import "tailwindcss";      /* Must come first */
@import "./variables.css";  /* Then custom variables */
@import "./components.css"; /* Then component overrides */

@theme {
  --color-primary: #0a7ea4;
}
```

#### Branch Conflicts

```css
// Branch A: Imports in one order
@import "tailwindcss";
@import "./theme.css";
@import "./utilities.css";

// Branch B: Different import order
@import "./utilities.css";
@import "tailwindcss";
@import "./theme.css";
```

**Resolution**: Establish consistent order with comments:
```css
/* Order matters: */
/* 1. Tailwind base & utilities */
/* 2. Custom theme variables */
/* 3. Component overrides */
/* 4. Utility classes */

@import "tailwindcss";
@import "./variables/theme.css";
@import "./components/index.css";
@import "./utilities/custom.css";
```

---

## Font and Asset Conflicts

### 1. Font Import Conflicts in CSS

Multiple branches may add different font sources, creating duplicates or conflicts.

#### Conflict Scenario

```css
/* Branch A: Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700');

/* Branch B: Local fonts */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
}

/* Conflict: Inter is defined twice from different sources */
```

#### Resolution Strategies

**Option 1: Use Google Fonts Only**
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900');

@theme {
  --font-sans: 'Inter', system-ui;
}
```

**Option 2: Self-Hosted Fonts Only**
```css
@font-face {
  font-family: 'Inter';
  src:
    url('/fonts/inter-100.woff2') format('woff2'),
    url('/fonts/inter-400.woff2') format('woff2'),
    url('/fonts/inter-700.woff2') format('woff2');
  font-weight: 100 700;
  font-display: swap;
}

@theme {
  --font-sans: 'Inter', system-ui;
}
```

**Option 3: Fallback Chain**
```css
/* Google Fonts with local fallback */
@import url('https://fonts.googleapis.com/css2?family=Inter');

@font-face {
  font-family: 'Inter-Local';
  src: url('/fonts/inter.woff2') format('woff2');
}

@theme {
  --font-sans: 'Inter', 'Inter-Local', system-ui;
}
```

#### Best Practices

- Choose **one source per font** (Google OR local, not both)
- Use **`font-display: swap`** for custom fonts (improves LCP)
- **Specify all weights** needed upfront
- **Test across browsers** for font loading behavior
- **Monitor font file sizes** (gzip the woff2 files)

---

### 2. Public Directory Asset Conflicts

Static assets in `/public/` can conflict when both branches add overlapping files.

#### Conflict Scenario

```
public/
├── fonts/
│   ├── inter.woff2         (Branch A)
│   └── custom-font.woff2   (Branch B)
├── images/
│   ├── logo.svg            (Both branches, different versions)
│   └── favicon.ico
└── config.json             (Both branches, different content)
```

#### Path Resolution in Vite

```typescript
// Vite serves /public files at root
// /public/fonts/inter.woff2 → http://localhost:5173/fonts/inter.woff2

// Reference with leading slash (root-absolute)
@font-face {
  src: url('/fonts/inter.woff2'); // ✓ Correct
  src: url('fonts/inter.woff2');  // ✗ Wrong (relative)
}
```

#### Resolution Approach

1. **List all public assets** from both branches
2. **Check for duplicates**: Same filename, different content
3. **For images**: Usually OK to keep both (use in different places)
4. **For config files**: Must merge or choose one
5. **Document structure**: Add `public/README.md` listing assets

#### Build-Time Asset Optimization

```typescript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  // Assets smaller than this are inlined as base64
  build: {
    assetsInlineLimit: 4096, // 4KB
  }
})
```

---

### 3. Image Optimization Plugin Conflicts

Different image optimization plugins can conflict when both branches add them.

#### Conflict Scenario

```typescript
// Branch A: Sharp-based optimization
import imagemin from 'vite-plugin-imagemin'
import imageminJpegtran from 'imagemin-jpegtran'
import imageminPngquant from 'imagemin-pngquant'

plugins: [
  imagemin({
    plugins: [
      imageminJpegtran(),
      imageminPngquant()
    ]
  })
]

// Branch B: AVIF with fallback
import viteImagemin from 'vite-plugin-imagemin'

plugins: [
  viteImagemin({
    mozjpeg: { quality: 80 },
    pngquant: { quality: [0.6, 0.8] }
  })
]

// Conflict: Different plugins with same functionality
```

#### Resolution Approach

1. **Choose one optimization strategy**: Pick A or B, don't mix
2. **Understand compression trade-offs**:
   - Sharp-based: Better JPEG/PNG, slower build
   - AVIF: Modern format, better compression, slower browsers
   - No optimization: Fast build, larger assets
3. **Test output**:
   ```bash
   npm run build
   ls -lah dist/
   # Check asset sizes and formats
   ```
4. **Document choice**: Add comment explaining why in vite.config.ts

#### Recommended Setup (Vite 7)

```typescript
// Vite 7 uses esbuild with LightningCSS for fast builds
// Image optimization via plugin is optional

import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    assetsInlineLimit: 4096,
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name].[hash][extname]'
      }
    }
  }
})
```

---

## Resolution Strategies

### 1. Config Files: Regenerate vs. Merge

Decision tree for choosing between regeneration and manual merge.

#### Regenerate Scenario

Use regeneration when:
- Core structure changed (Vite 5→6 breaking changes)
- Tool had significant config format changes
- Merge would be complex or error-prone
- Both branches diverged significantly

```bash
# Back up current config
cp vite.config.ts vite.config.ts.backup

# Regenerate from scratch
npm create vite@latest
# OR for existing tool
npx tailwindcss init -p

# Then carefully merge back essential customizations
```

#### Merge Scenario

Use manual merge when:
- Both branches added different features
- Conflicts are in distinct config sections
- Change is version-compatible (no breaking changes)
- Merging preserves both features

```typescript
// Example: Merge two plugins
// Branch A adds React plugin
// Branch B adds Vue plugin

// Merged result: Both plugins
plugins: [
  react({ enforce: 'pre' }),
  vue(),
  tailwind()
]
```

#### Decision Matrix

| Situation | Regenerate | Merge |
|-----------|------------|-------|
| Major version upgrade | ✓ | - |
| Both branches add plugins | - | ✓ |
| Different env files | - | ✓ |
| Conflicting rollupOptions | ✓ | - |
| Proxy config additions | - | ✓ |

---

### 2. Plugin Ordering: How to Determine Correct Order

Algorithm for resolving plugin order conflicts.

#### Step 1: Classify by Type

```typescript
// Identify what each plugin does
const plugins = [
  'Input plugins' (read files): postcss-import, vite-plugin-glob
  'Transform plugins' (modify): tailwind, vue, react, svelte
  'Output plugins' (bundle): rollup-plugin-minify
  'Post plugins' (finalize): autoprefixer, cssnano
]
```

#### Step 2: Apply Enforce Rules

```typescript
// Vite core runs plugins in this order
[
  alias,                    // Always first
  ...plugins with enforce: 'pre',
  ...vite core,
  ...plugins without enforce,
  ...vite build plugins,
  ...plugins with enforce: 'post',
  vite post build
]
```

#### Step 3: Test with --debug

```bash
vite build --debug
# Output shows plugin execution order
# Verify correct order with test build
```

#### Step 4: Validate Output

```bash
npm run build
# Check dist/ for expected files
# Look for errors in build output
# Verify CSS/JS in browser
```

---

### 3. Tailwind Class Conflicts in Components

Specificity implications when component classes conflict.

#### Conflict Scenario

```jsx
// Branch A: Text utilities
function Card() {
  return <div className="text-gray-900 text-lg">Content</div>
}

// Branch B: Text utilities with different values
function Card() {
  return <div className="text-gray-700 text-base">Content</div>
}

// Merged conflict: Which text color and size wins?
```

#### Specificity Rules in Tailwind

```css
/* All Tailwind utilities have equal specificity (1 class) */
.text-gray-900 /* specificity: 0-1-0 */
.text-gray-700 /* specificity: 0-1-0 */

/* CSS order matters: Last wins */
/* In dev: order depends on utility import order */
/* In production: consistent order from utility generation */
```

#### Resolution Approach

**Option 1: Component Version Agreement**
```jsx
// Agreed-upon base styles in component
function Card({ className = '' }) {
  return (
    <div className={`text-gray-900 text-lg ${className}`}>
      Content
    </div>
  )
}

// Users can override with props
<Card className="text-gray-700" /> // Won't override due to cascade
```

**Option 2: Tailwind Layer**
```css
/* Define component base in @layer */
@layer components {
  .card-text {
    @apply text-gray-900 text-lg;
  }
}
```

```jsx
// Use component class instead of inline
function Card() {
  return <div className="card-text">Content</div>
}
```

**Option 3: CSS Modules (No Tailwind Conflict)**
```tsx
import styles from './Card.module.css'

function Card() {
  return <div className={styles.card}>Content</div>
}
```

#### Testing Class Behavior

```javascript
// In browser console during dev
const el = document.querySelector('.card')
const styles = window.getComputedStyle(el)
console.log(styles.color)    // Check which color wins
console.log(styles.fontSize) // Check which size wins
```

---

### 4. When to Run `npx tailwindcss init` to Regenerate

Decision criteria for regenerating Tailwind config.

#### DO Regenerate When

1. **Major version upgrade** (v3→v4)
   ```bash
   npx tailwindcss init
   # Creates fresh v4 config structure
   ```

2. **Content paths are broken**
   ```bash
   # If classes aren't generating, regenerate with correct paths
   npx tailwindcss init --with-ts
   ```

3. **Config structure corrupted**
   ```bash
   # If config syntax errors, start fresh
   ```

#### DON'T Regenerate When

1. **Just adding @theme variables**
   ```css
   /* Edit CSS directly, no regeneration needed */
   @theme {
     --color-new: #ffffff;
   }
   ```

2. **Merging two branches' customizations**
   ```javascript
   // Manually merge rather than regenerate
   export default {
     theme: {
       ...branchA.theme,
       ...branchB.theme
     }
   }
   ```

3. **Adding plugins**
   ```javascript
   // Append to plugins array
   plugins: [existingPlugins, newPlugin]
   ```

#### Safe Regeneration Process

```bash
# 1. Backup current config
cp tailwind.config.js tailwind.config.js.backup
cp postcss.config.js postcss.config.js.backup

# 2. Remove old config
rm tailwind.config.js postcss.config.js

# 3. Regenerate
npx tailwindcss init -p

# 4. Restore customizations from backup
# - Review backup file
# - Manually add back custom theme, plugins, etc.

# 5. Test
npm run dev
npm run build
```

---

### 5. Comprehensive Merge Resolution Checklist

Final checklist when resolving Vite + Tailwind configuration conflicts.

#### Pre-Merge Assessment

- [ ] Identify all conflicting files:
  - `vite.config.ts`
  - `tailwind.config.js` / CSS theme files
  - `postcss.config.js`
  - `.env*` files
  - `package.json` scripts

- [ ] Check Vite version in both branches
  - [ ] Are they the same version?
  - [ ] Do any require version upgrades?

- [ ] Check Tailwind version in both branches
  - [ ] Both v3, both v4, or mixed?
  - [ ] Do they require migration?

#### Vite Config Merge Checklist

- [ ] **Plugins**
  - List all plugins from both branches
  - Identify overlapping plugins (keep one)
  - Add `enforce: 'pre'` or `enforce: 'post'` if needed
  - Test with `vite build --debug`

- [ ] **Environment Variables**
  - Merge .env files (no duplicates)
  - Ensure all vars prefixed with `VITE_`
  - Document required env vars in README

- [ ] **Build Config**
  - Merge `rollupOptions` at object level (don't nest arrays)
  - Verify `outDir`, `base`, `lib` settings
  - Test `vite build` output

- [ ] **Server Config**
  - Merge proxy routes (combine all)
  - Verify HMR settings if behind proxy
  - Test `vite dev` and API calls

- [ ] **SSR Config** (if applicable)
  - Merge `external` and `noExternal` lists
  - Verify `resolve.conditions`
  - Test with `vite build --ssr`

#### Tailwind Config Merge Checklist

- [ ] **v3 vs v4 Compatibility**
  - If upgrading to v4: Regenerate config structure
  - If staying in v3: Keep JavaScript config
  - Test utility generation

- [ ] **CSS Theme Variables**
  - Consolidate `@theme` declarations
  - Check for duplicate variable names
  - Verify naming conventions (--color-*, --font-*, etc.)

- [ ] **Plugins**
  - List all Tailwind plugins from both branches
  - Check for JavaScript-based vs CSS-based plugins
  - Use `@plugin` directive for legacy JS plugins (v4)

- [ ] **Content Paths**
  - Verify Tailwind can find all component files
  - Test with `npm run build`
  - Check for missing utility classes

#### PostCSS Config Merge Checklist

- [ ] **Plugin Order**
  - Verify `postcss-import` is first
  - Ensure `@tailwindcss/postcss` comes before other processors
  - Place `autoprefixer` after Tailwind
  - Put `cssnano` last (production only)

- [ ] **Autoprefixer Settings**
  - Set appropriate `overrideBrowserslist`
  - Avoid duplicate prefixing
  - Test build output with `npm run build`

#### Font and Asset Checklist

- [ ] **Font Files**
  - Check for duplicate font definitions
  - Verify all `@font-face` src paths use leading `/`
  - Confirm format names are correct (`truetype` not `ttf`)

- [ ] **Public Assets**
  - List all `/public/` files from both branches
  - Resolve duplicate image conflicts
  - Update CSS/HTML references if needed

#### Testing and Validation

- [ ] **Development Build**
  ```bash
  npm install
  npm run dev
  # Check: Dev server starts, no build errors
  # Check: Styles load correctly, no FOUC
  # Check: HMR works, refresh on save
  ```

- [ ] **Production Build**
  ```bash
  npm run build
  # Check: Build completes without errors
  # Check: dist/ contains expected files
  # Check: CSS is minified, file sizes reasonable
  ```

- [ ] **Asset Loading**
  - Open dist/index.html in browser
  - Check Network tab: All assets load
  - Check Console: No 404 errors for fonts/images
  - Check Styles: Colors, fonts, spacing correct

- [ ] **Cross-Browser Testing**
  - Test in Chrome (latest)
  - Test in Firefox (latest)
  - Test in Safari (latest)
  - Test on mobile (iOS/Android)

#### Documentation

- [ ] Create MERGE_NOTES.md documenting:
  - Conflicts encountered
  - Resolution decisions made
  - Plugins added/modified
  - Environment variables required
  - Build/deploy changes

- [ ] Update README.md with:
  - Vite version requirement
  - Tailwind version (v3 or v4)
  - Any special build commands
  - Environment setup instructions

---

## References

### Official Documentation

- [Vite Configuration](https://vite.dev/config/)
- [Vite Migration Guides](https://vite.dev/guide/migration)
- [Vite Plugin API](https://vite.dev/guide/api-plugin)
- [Vite Server Options - Proxy](https://vite.dev/config/server-options)
- [Vite SSR Options](https://vite.dev/config/ssr-options)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Tailwind CSS Theme Variables](https://tailwindcss.com/docs/theme)
- [Tailwind CSS Installation](https://tailwindcss.com/docs/installation)

### Community Resources

- [Vite GitHub Discussions - Plugin Ordering](https://github.com/vitejs/vite/discussions/1815)
- [Tailwind CSS v4 Blog](https://tailwindcss.com/blog/tailwindcss-v4)
- [Tailwind CSS GitHub Discussions - Plugin System](https://github.com/tailwindlabs/tailwindcss/discussions/15715)
- [Git Merge Conflict Resolution Guide](https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts)

### Related Tools

- [vite-plugin-inspect](https://github.com/antfu/vite-plugin-inspect) - Visualize plugin transformations
- [PostCSS Documentation](https://postcss.org/)
- [Rollup Configuration](https://rollupjs.org/configuration/)

---

**Document Version**: 1.0
**Target Audience**: Developers resolving Vite + Tailwind config merges
**Scope**: Vite 5/6/7, Tailwind CSS 3/4, PostCSS configuration
**Last Verified**: April 2026
