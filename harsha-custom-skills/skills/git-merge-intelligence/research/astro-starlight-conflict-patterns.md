# Astro and Starlight Documentation Site Conflict Patterns Research

**Research Date:** April 2026
**Scope:** Comprehensive analysis of merge conflicts in Astro and Starlight documentation sites
**Focus:** Configuration, content, and integration conflicts across multiple layers

---

## Executive Summary

Astro and Starlight projects feature complex layered configuration involving multiple integrations, each with dependency chains. Merge conflicts in these projects follow distinct patterns:

- **Configuration conflicts** are deterministic and resolvable through understanding dependency order
- **Content conflicts** are typically non-blocking (can keep both with metadata reconciliation)
- **Integration conflicts** require understanding the execution order model
- **Build validation** can catch most dangerous conflicts automatically

This document provides strategies for identifying, understanding, and safely resolving each class of conflict.

---

## 1. Astro Configuration Conflicts

### 1.1 astro.config.mjs Anatomy

The `astro.config.mjs` file is the root configuration point for all Astro projects. Its structure follows this pattern:

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [
    starlight({...}),    // integration 1
    react(),             // integration 2
    mdx(),               // integration 3
  ],
  output: 'static',      // or 'server'
  markdown: {...},
  vite: {...},
});
```

### 1.2 Integration Ordering and Dependencies

**Critical Finding:** Integration order matters significantly. According to [Astro Integration API documentation](https://docs.astro.build/en/reference/integrations-reference/), integrations run in the order they are configured.

**Key Principle:** Integrations should be order-agnostic, but when they are not, this must be documented. Common ordering constraints:

| Conflict Scenario | Solution |
|---|---|
| Starlight + Mermaid | Mermaid must come **before** Starlight in integrations array |
| MDX + Custom Remark plugins | MDX must come before remark/rehype plugins |
| Custom middleware + Astro middleware | Specify `pre` or `post` ordering |

**Merge Conflict Pattern:**
```
<<<<<<< HEAD
integrations: [
  starlight({...}),
  react(),
  astroMermaid({...}),  // branch A added here
]
=======
integrations: [
  astroMermaid({...}),  // branch B added here first
  starlight({...}),
  react(),
]
>>>>>>> feature
```

**Resolution Strategy:** Determine if either ordering is required by the plugins. If no hard constraint exists, preserve alphabetical or functional grouping. Test the resulting order with `astro build`.

### 1.3 Output Mode Changes

The `output` setting controls whether your site is static or server-rendered:

- `'static'` - Pre-render all pages (default, most compatible)
- `'server'` - Server-side rendering for all pages

**Source:** [Astro Configuration Reference](https://docs.astro.build/en/reference/configuration-reference/)

**Merge Conflict Pattern:**
```
astro.config.mjs differences:
- Branch A: output: 'static'
- Branch B: output: 'server'
```

**Resolution Strategy:**
1. Understand the feature branch's reason for the change
2. Check if build targets support it (Netlify/Vercel have different SSR support)
3. Default to `'static'` unless SSR is explicitly needed
4. Document the choice in PR description

**Testing:** Run `astro build` with each setting and verify artifact types (HTML files vs. `.astro` runtime files).

### 1.4 Astro 4 → 5 Breaking Changes

Reference: [Upgrade to Astro v5 Guide](https://docs.astro.build/en/guides/upgrade-to/v5/)

Major breaking changes that cause conflicts:

#### 1.4.1 Direct Script Rendering (v5.0)

**Change:** Removed `experimental.directRenderScript` flag. Scripts no longer hoist to `<head>`.

**Conflict Pattern:** One branch uses the experimental flag (Astro 4 or earlier v5.0-alpha), another removes it.

```javascript
// ❌ Conflict: Old code references removed feature
experimental: {
  directRenderScript: true,
},
```

**Resolution:** Remove the entire `experimental` section if only this flag was used.

#### 1.4.2 Vite v6 Upgrade

**Change:** Astro v5.0 upgrades to Vite v6.0.

**Conflict Pattern:** Custom `vite` configuration using Vite v5 APIs.

```javascript
// Potential conflict: Vite-specific plugins may break
vite: {
  plugins: [...],
  // v5 configs may conflict with v6
}
```

**Resolution:** Check [Vite migration guide](https://vitejs.dev/guide/migration.html) if custom Vite plugins exist. Test with `astro build`.

#### 1.4.3 MDX Integration Changes

**Change:** Astro v5.0 shifts JSX handling responsibility from Astro core to @astrojs/mdx package.

**Conflict Pattern:** MDX configuration differs between branches due to different Astro versions.

**Resolution:** Ensure @astrojs/mdx is properly configured and up-to-date. Run `astro check` to catch type issues.

#### 1.4.4 prerender Conflict Behavior

**Change:** New `prerenderConflictBehavior` option controls how Astro handles conflicting prerendered routes.

```javascript
// New in Astro 5:
export default defineConfig({
  build: {
    prerenderConflictBehavior: 'warn', // or 'error', 'ignore'
  },
});
```

**Conflict Pattern:** Branches add/configure this differently, affecting how dynamic route conflicts are handled.

**Resolution:** Choose the strictest setting that doesn't break the build. `'error'` is recommended for CI/CD.

### 1.5 Content Collections Schema Conflicts

Source: [Content Collections Documentation](https://docs.astro.build/en/guides/content-collections/)

Content collections use Zod schemas to validate frontmatter.

**Conflict Pattern:**

```
src/content/config.ts differences:
- Branch A adds new required field to schema
- Branch B doesn't add the field to frontmatter

Result: Build fails with "Content entry frontmatter does not match schema"
```

**Schema Definition:**
```typescript
import { defineCollection, z } from 'astro:content';

const docs = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    // Branch A adds:
    published: z.date(),
    // Branch B doesn't add this to .mdx files
  }),
});
```

**Resolution Strategy:**

1. **Keep both schema changes** if both fields are necessary
2. **Make new fields optional** if only one branch requires them:
   ```typescript
   published: z.date().optional(),
   ```
3. **Update all content files** to include new required fields
4. **Verify with:** `astro check --validate`

**Testing:** Run `astro build` to validate all content against schema.

### 1.6 Markdown and MDX Configuration Conflicts

Source: [Markdown in Astro](https://docs.astro.build/en/guides/markdown-content/), [MDX Integration](https://docs.astro.build/en/guides/integrations-guide/mdx/)

**Configuration Options That Conflict:**

| Option | Conflict Type | Resolution |
|---|---|---|
| `markdown.syntaxHighlight` | Code theme preference | Accept one, document choice |
| `markdown.shikiConfig.theme` | Light/dark code theme | Merge into array or choose |
| `markdown.remarkPlugins` | Plugin order matters | Preserve order, test |
| `markdown.rehypePlugins` | Post-processing order | Can usually be combined |
| `markdown.gfm`, `markdown.smartypants` | Feature toggles | Usually compatible |

**Merge Conflict Example:**

```javascript
// markdown.remarkPlugins ordering matters
markdown: {
  remarkPlugins: [
<<<<<<< HEAD
    [remarksPluginA],
    [remarksPluginB],
=======
    [remarksPluginB],  // Different order
    [remarksPluginA],
>>>>>>> feature
  ],
}
```

**Resolution Strategy:**

1. **Remark plugins** execute in sequence - order matters for interdependent plugins
2. **Rehype plugins** generally don't depend on order
3. **Test order** by building and checking output
4. **Document plugin dependencies** in comments if order is non-obvious

---

## 2. Starlight Specific Conflicts

Source: [Starlight Configuration Reference](https://starlight.astro.build/reference/configuration/), [Starlight Sidebar Navigation](https://starlight.astro.build/guides/sidebar/)

### 2.1 Starlight Configuration Block in astro.config.mjs

Starlight is configured as an integration with extensive options:

```javascript
// astro.config.mjs
starlight({
  title: 'My Docs',
  sidebar: [...],
  defaultLocale: 'en',
  locales: {...},
  favicon: '...',
  components: {...},
})
```

**Conflict Pattern:** Multiple branches modify different Starlight options.

```
<<<<<<< HEAD
starlight({
  title: 'New Title',
  sidebar: [... 50 lines ],
  defaultLocale: 'en',
})
=======
starlight({
  title: 'Another Title',
  sidebar: [... different structure ],
  locales: { es: {...} },
})
>>>>>>> feature
```

**Resolution Strategy:** This is complex because Starlight options are nested. Approach:

1. **Merge high-level structure** (title, output format, defaultLocale)
2. **Preserve additions** from both branches when they don't conflict
3. **Manually reconcile sidebar** (see section 2.2)
4. **Manually reconcile locales** (see section 2.5)

### 2.2 Sidebar Configuration Conflicts

Source: [Starlight Sidebar Navigation](https://starlight.astro.build/guides/sidebar/), [Discussion on sidebar ordering](https://github.com/withastro/starlight/discussions/969)

The sidebar is the most commonly conflicted Starlight configuration.

**Sidebar Structure Options:**

1. **Manual array configuration:**
   ```javascript
   sidebar: [
     { label: 'Home', link: '/' },
     { label: 'Guides', items: [
         { label: 'Getting Started', link: '/guides/getting-started' },
       ]
     },
   ]
   ```

2. **Autogenerated from file structure:**
   ```javascript
   sidebar: 'auto',
   // OR with customization
   sidebar: [
     { label: 'Docs', collapsed: true, autogenerate: { directory: 'docs' } },
   ]
   ```

**Merge Conflict Pattern (Most Common):**

```javascript
<<<<<<< HEAD
sidebar: [
  { label: 'Docs', link: '/docs' },
  { label: 'API', items: [...] },
  { label: 'Examples', autogenerate: { directory: 'examples' } },
]
=======
sidebar: [
  { label: 'Welcome', link: '/' },
  { label: 'Docs', items: [...5 new items] },
  { label: 'Community', link: '/community' },
]
>>>>>>> feature
```

**Issues with Autogenerated Sidebars:**

According to [Starlight discussions](https://github.com/withastro/starlight/issues/1223), autogenerated folder order depends on the `order` property of the first page in each directory. This can cause conflicts when:

- Branch A reorders pages within directories
- Branch B adds/removes pages
- Result: Sidebar order changes unexpectedly

**Resolution Strategy:**

1. **Prefer autogeneration** when structure rarely changes
2. **Use manual sidebar** when you need strict control over navigation
3. **Preserve both branches' additions** when they don't conflict
4. **Test ordering** by building and checking the generated sidebar
5. **Document ordering logic** in comments if using complex autogeneration

**Example Merged Sidebar:**
```javascript
sidebar: [
  { label: 'Home', link: '/' },           // preserved from both
  { label: 'Getting Started', items: [
    // Combine items from both branches
    { label: 'Installation', link: '/getting-started/installation' },
    { label: 'Configuration', link: '/getting-started/config' },
    { label: 'First Project', link: '/getting-started/first-project' },
  ]},
  { label: 'Documentation', items: [
    // New docs from feature branch
    { label: 'Advanced Routing', link: '/docs/advanced-routing' },
    // Existing docs from main
    { label: 'Components', link: '/docs/components' },
  ]},
  { label: 'Examples', autogenerate: { directory: 'examples' } },
  { label: 'Community', link: '/community' },
]
```

### 2.3 Navigation Ordering and Link Structure

**Conflict Patterns:**

1. **Link path changes:** Page reorganization creates duplicate/conflicting links
   ```javascript
   // Branch A: /docs/guides/intro
   // Branch B: /guides/intro
   // Results in duplicate navigation
   ```

2. **Group nesting:** Different folder hierarchies
   ```javascript
   // Branch A groups under 'Docs' > 'Guides' > 'Installation'
   // Branch B groups under 'Getting Started' > 'Installation'
   // Same page, different navigation path
   ```

**Resolution Strategy:**

1. **Prefer consistency** - don't have same page in multiple locations
2. **Redirect old paths** using Astro redirects if paths changed
3. **Update internal links** when reorganizing (see section 4)
4. **Test with `astro build`** to catch broken links

### 2.4 Theme and Styling Conflicts

Source: [Starlight CSS and Styling](https://starlight.astro.build/guides/css-and-tailwind/), [Starlight Customization](https://starlight.astro.build/guides/customization/)

**Configuration Areas:**

1. **Theme colors:**
   ```javascript
   starlight({
     customCss: [
       './src/styles/custom.css',  // Branch A
     ],
   })
   // vs
   starlight({
     customCss: [
       './src/styles/theme.css',   // Branch B
       './src/styles/custom.css',
     ],
   })
   ```

2. **Dark mode settings:**
   ```javascript
   // Must provide at least one light AND one dark theme
   // Conflict: branch A defines theme, branch B redefines
   ```

**Dark/Light Mode Specific Issues:**

According to [Starlight discussions](https://github.com/withastro/starlight/discussions/1829):

- Light/dark classes apply to logo and hero images
- Code block themes must switch automatically when site theme changes
- Safari has compatibility issues with `<picture prefers-color-scheme>`

**Merge Pattern:**

```javascript
// Branch A: Single custom theme
const theme = 'github-light';

// Branch B: Custom CSS files for dark theme
customCss: ['./src/styles/dark.css'],
```

**Resolution Strategy:**

1. **Combine custom CSS files** - both can be loaded
2. **Test dark/light mode switching** - verify logo, code blocks update
3. **Check Safari compatibility** if targeting Apple users
4. **Validate contrast ratios** for accessibility

### 2.5 Localization Configuration Conflicts

Source: [Starlight i18n Documentation](https://starlight.astro.build/guides/i18n/)

**Critical Constraint:** Cannot mix Starlight's `locales` config with Astro's `i18n` config.

**Conflict Pattern:**

```
<<<<<<< HEAD
// astro.config.mjs
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'fr', 'es'],
  routing: { prefixDefaultLocale: false },
}
=======
// Starlight's locales config
starlight({
  defaultLocale: 'en',
  locales: {
    en: { label: 'English' },
    fr: { label: 'Français' },
    es: { label: 'Español' },
  },
})
>>>>>>> feature
```

**Error This Causes:**
> "Cannot provide both an Astro i18n configuration and a Starlight locales configuration"

Source: [Configuration Error Issue #13551](https://github.com/withastro/astro/issues/13551)

**Resolution Strategy:**

1. **Choose one approach:**
   - **Use Starlight locales:** Simpler for pure documentation sites
   - **Use Astro i18n:** More flexible for multi-purpose sites
2. **Remove the other configuration entirely**
3. **Test with:**
   ```bash
   astro build
   ```

**Localization Routing Conflicts:**

When using Astro's `i18n`, watch for:
```javascript
i18n: {
  routing: {
    redirectToDefaultLocale: true,
    prefixDefaultLocale: true,  // MUST be true if using redirect
  }
}
```

**Error:** If `redirectToDefaultLocale` is true but `prefixDefaultLocale` is false, you get build errors.

---

## 3. Mermaid Integration Conflicts

Source: [astro-mermaid npm package](https://www.npmjs.com/package/astro-mermaid), [Extending Astro Markdown Processing](https://dev.to/fkurz/extending-astrojs-markdown-processing-with-remark-and-rehype-plugins-m1k)

### 3.1 Integration Ordering for Mermaid

**Critical Finding:** Mermaid must come **before** Starlight in the integrations array.

**Why:** Mermaid adds remark/rehype plugins that process diagram syntax before Starlight's markdown processing.

**Merge Conflict Pattern:**

```javascript
<<<<<<< HEAD
integrations: [
  starlight({...}),
  astroMermaid({...}),  // WRONG ORDER
]
=======
integrations: [
  astroMermaid({...}),
  starlight({...}),  // CORRECT ORDER
]
>>>>>>> feature
```

**Resolution:** Always place Mermaid before Starlight:
```javascript
integrations: [
  astroMermaid({...}),      // 1st
  starlight({...}),         // 2nd
  react(),                  // 3rd (optional)
]
```

### 3.2 Mermaid Configuration Options

Common Mermaid configuration conflicts:

```javascript
astroMermaid({
  // Theme configuration
  theme: 'default',           // Branch A
  // vs
  autoTheme: true,            // Branch B (auto-detect dark mode)

  // CSS class binding
  lazyLoad: true,             // lazy or immediate rendering

  // Diagram security
  securityLevel: 'antiscript', // security vs functionality
})
```

**Merge Strategy:**

| Option | Conflict Resolution |
|---|---|
| `autoTheme` | Usually prefer `true` for multi-theme sites |
| `theme` | Not needed if `autoTheme: true` |
| `lazyLoad` | Prefer `true` for performance |
| `securityLevel` | Keep `'antiscript'` for user-generated content |

### 3.3 Remark Plugin Ordering

According to documentation, remark plugin execution order is critical.

**Plugin Chain Pattern:**
```javascript
markdown: {
  remarkPlugins: [
    // Plugins that transform markdown
    'remark-gfm',              // GitHub-flavored markdown
    // Mermaid must come after basic markdown processing
    'astro-mermaid/remark',    // or custom remark-mermaid
    // Custom processors
    [myCustomPlugin, options],
  ],
  rehypePlugins: [
    // HTML-level plugins
    ['rehype-autolink-headings', {behavior: 'wrap'}],
    'rehype-slug',
  ],
}
```

**Conflict Resolution:**

1. **Mermaid remark plugin** should come after markdown basics
2. **Custom plugins** should come after Mermaid (or be tested)
3. **Rehype plugins** generally don't conflict (run on HTML)

### 3.4 Theme Configuration for Mermaid Diagrams

Mermaid diagrams need consistent theme with the site.

**Conflict Pattern:**

```javascript
// Branch A: Manual theme
astroMermaid({
  theme: 'dark',
  customCSS: 'path/to/dark-theme.css',
})

// Branch B: Auto-detect
astroMermaid({
  autoTheme: true,  // Uses html[data-theme]
})
```

**Merge Strategy:**

Prefer `autoTheme: true` when Starlight is present:

```javascript
starlight({...}),
astroMermaid({
  autoTheme: true,  // Reads from Starlight's theme
})
```

---

## 4. Documentation Content Conflicts

### 4.1 Frontmatter Conflicts

**Sources:** [Content Collections](https://docs.astro.build/en/guides/content-collections/), [Markdown Frontmatter Errors](https://docs.astro.build/en/reference/errors/invalid-content-entry-frontmatter-error/)

Frontmatter is metadata at the top of `.md` or `.mdx` files:

```yaml
---
title: Getting Started
description: How to get started
sidebar:
  order: 10
published: 2025-04-01
---
```

**Conflict Patterns:**

1. **Sidebar position conflicts:** Both branches reorder pages
   ```yaml
   # Branch A:
   sidebar:
     order: 5

   # Branch B:
   sidebar:
     order: 10

   # Result: Page appears in different sidebar positions
   ```

2. **Title/description changes:**
   ```yaml
   <<<<<<< HEAD
   title: "Installation Guide"
   description: "Step-by-step installation"
   =======
   title: "Get Started with Installation"
   description: "Complete setup instructions"
   >>>>>>> feature
   ```

3. **New fields added:** Branch adds field not in schema
   ```yaml
   published: 2025-04-01  # Branch A adds
   # vs (Branch B doesn't have this field)
   # Build fails if field is required in schema
   ```

**Resolution Strategy:**

1. **Title and description:** Keep both if possible; prefer more descriptive version
2. **Sidebar order:** Reconcile order to match sidebar structure
3. **New fields:** Ensure content collection schema supports them
4. **Required fields:** All must be present for build to succeed

**Testing:**
```bash
astro check --validate
astro build
```

### 4.2 MDX Component Import Conflicts

MDX files can import and use custom components:

```mdx
---
title: Advanced Guide
---

import { Alert, CodeBlock } from '../components/docs';

<Alert type="info">
  Important information
</Alert>
```

**Conflict Pattern:**

```mdx
<<<<<<< HEAD
import { Alert, CodeBlock } from '../components/docs';
import { CustomCard } from '../components/custom';

<Alert>Text</Alert>
<CustomCard>More text</CustomCard>
=======
import { Alert } from '../components/ui';  // Different import path

<Alert>Text</Alert>
>>>>>>> feature
```

**Resolution Strategy:**

1. **Deduplicate imports:** Use one import statement per component
2. **Update paths:** If components moved, update all files
3. **Check component compatibility:** Different versions may have different props
4. **Test MDX rendering:** `astro build` will fail if components don't exist

### 4.3 Cross-Reference and Link Conflicts

When pages are reorganized, links break.

**Conflict Pattern:**

```markdown
# Branch A: Pages reorganized
Old link: [Getting Started](/docs/getting-started)
New location: /guide/setup/getting-started

# Branch B: Different reorganization
Old link: [Getting Started](/docs/getting-started)
New location: /getting-started

# Both branches break if main has different structure
```

**Link Types in Astro:**

1. **Relative links:** `./other-page` (safest for reorganization)
2. **Root-relative links:** `/docs/page` (breaks if path changes)
3. **Absolute links:** `https://docs.example.com/page` (external)

**Resolution Strategy:**

1. **Prefer relative links** for documentation
2. **Update all links** when page path changes
3. **Use `astro-link-validator`** to catch broken links:
   ```bash
   npm install astro-link-validator
   ```
4. **Verify with build:**
   ```bash
   astro build
   ```

**Example: Safe Reorganization**

```
Before:
src/content/docs/
├── getting-started.md
└── advanced/setup.md

After merge:
src/content/docs/
├── guide/
│   ├── getting-started.md
│   └── advanced-setup.md

Updates needed in linking pages:
[Getting Started](../guide/getting-started)  # relative
```

---

## 5. Resolution Strategies

### 5.1 Configuration File Merge Strategy

**Dependency Chain Understanding:**

```
Astro Core (astro.config.mjs)
    ↓
Integrations (order matters)
    ├─ Starlight
    │   ├─ sidebar config
    │   ├─ i18n config
    │   └─ theme config
    ├─ Mermaid
    │   └─ theme config
    └─ MDX
        └─ markdown config
```

**Merge Process:**

1. **Identify each change** in both branches
2. **Check dependency chain:** Does change A depend on change B?
3. **Verify order:** Do integrations need specific order?
4. **Test incrementally:** Build after each major change

**Example Merge:**

```javascript
// RESULT: Merged astro.config.mjs
import starlight from '@astrojs/starlight';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';
import astroMermaid from 'astro-mermaid';

export default defineConfig({
  // From main: base URL
  base: '/docs',

  // From feature: new output mode (test this!)
  output: 'server',

  // Integrations: critical order
  integrations: [
    astroMermaid({
      autoTheme: true,
    }),
    starlight({
      title: 'My Documentation',
      // From main: existing sidebar
      // From feature: new locales
      sidebar: [...],
      locales: {
        en: { label: 'English' },
        fr: { label: 'Français' },
      },
    }),
    react(),
    mdx(),
  ],

  // From main: markdown settings
  markdown: {
    syntaxHighlight: 'shiki',
  },

  // From feature: custom Vite config
  vite: {
    ssr: {
      external: ['some-dep'],
    },
  },
});
```

### 5.2 Content File Merge Strategy

**Philosophy:** Frontmatter metadata is usually "keep both," but validate structure.

**Merge Approach:**

1. **Keep all frontmatter fields** from both branches (unless duplicates)
2. **Reconcile sidebar order** based on final structure
3. **Update links** to match new page locations
4. **Validate schema** with `astro check`

**Example:**

```mdx
---
# Keep fields from both branches
title: "Getting Started Guide"
description: "Complete setup instructions"

# Reconcile sidebar order
sidebar:
  order: 5

# New field from feature branch
published: 2025-04-01
authors: ["Alice", "Bob"]
---

# Content from both branches (manual review needed)
```

### 5.3 When to Regenerate vs. Manually Merge

**Regenerate Configuration When:**
- Major version upgrade (Astro 4 → 5)
- Plugin API changes
- Large structural changes
- You don't understand the conflicts

**Manually Merge When:**
- Small, isolated changes
- You understand both versions
- Changes complement each other
- Performance or specific features depend on exact config

**Regeneration Process:**

```bash
# 1. Back up current config
cp astro.config.mjs astro.config.mjs.bak

# 2. Start from scratch
rm astro.config.mjs

# 3. Use create-astro to generate base
npx create-astro@latest --template starlight ./temp

# 4. Copy new base config
cp temp/astro.config.mjs .

# 5. Manually reapply custom changes from backup
# Review both versions side-by-side

# 6. Test
astro build
```

---

## 6. Build Validation

Source: [TypeScript in Astro](https://docs.astro.build/en/guides/typescript/), [@astrojs/check](https://www.npmjs.com/package/@astrojs/check), [Astro Link Validator](https://github.com/rodgtr1/astro-link-validator)

### 6.1 astro build — Full Build Validation

The most comprehensive validation tool.

**What It Catches:**
- Content schema violations
- Missing imported components
- Broken relative links (some cases)
- TypeScript errors (if configured)
- Integration errors
- Missing page routes

**Run After Merge:**
```bash
astro build
```

**Common Build Failures Post-Merge:**

| Error | Cause | Fix |
|---|---|---|
| "Content entry frontmatter does not match schema" | Schema version conflict | Update frontmatter fields |
| "Cannot find module" | Import path changed | Update import paths |
| "Unknown directive" | MDX component not imported | Add import statement |
| "No routes found" | Content structure broken | Check src/content/ structure |
| Integration init error | Order/config mismatch | Review astro.config.mjs |

### 6.2 astro check — TypeScript Validation

Validates `.astro` files and type safety without full build.

**Install:**
```bash
npm install -D @astrojs/check typescript
```

**Run:**
```bash
astro check --validate
```

**What It Checks:**
- TypeScript type errors
- Undefined variables
- Component prop types
- Content collection types

**Example Output:**
```
src/pages/index.astro
  > 5:8 Type "string | undefined" cannot be used as index.

src/content/config.ts
  > 12:5 'published' is declared but never used.
```

### 6.3 Link Checking — astro-link-validator

Automated link validation during builds.

**Install:**
```bash
npm install -D astro-link-validator
```

**Configure in astro.config.mjs:**
```javascript
import astroLinkValidator from 'astro-link-validator';

export default defineConfig({
  integrations: [
    astroLinkValidator({
      checkExternal: false,  // Network requests are slow
      onError: 'throw',      // Fail build on broken links
    }),
  ],
});
```

**What It Validates:**
- Internal page links (`/docs/page`)
- Asset references (`/images/logo.png`)
- HTML element links (`<a>`, `<img>`, `<script>`, `<link>`, `<iframe>`)
- Relative and root-relative links

**Performance Note:** External link checking disabled by default because each URL requires a network request.

### 6.4 Build Validation Checklist

After resolving conflicts and before merging:

- [ ] `astro check` passes without errors
- [ ] `astro build` completes successfully
- [ ] No TypeScript errors shown
- [ ] Content schema validates (all required fields present)
- [ ] Link validator (if installed) reports no broken links
- [ ] Dark/light mode switching works
- [ ] All sidebar links are valid
- [ ] Localized pages (if applicable) all build
- [ ] Mermaid diagrams (if present) render correctly

---

## 7. Common Conflict Scenarios and Solutions

### Scenario 1: Adding Mermaid to Starlight Docs

**Conflict:**
```javascript
integrations: [
  // Both branches add Mermaid, different configs
<<<<<<< HEAD
  astroMermaid({ theme: 'dark' }),
  starlight({...}),
=======
  starlight({...}),
  astroMermaid({ autoTheme: true }),
>>>>>>> feature
]
```

**Solution:**
```javascript
integrations: [
  astroMermaid({
    autoTheme: true,  // Prefer auto for theme consistency
  }),
  starlight({...}),
]
```

### Scenario 2: Reorganizing Documentation Structure

**Conflict:** Pages moved, sidebar updated differently in each branch.

**Resolution Process:**

1. Decide on final structure (coordinate with team)
2. Move all files to final locations
3. Update frontmatter `sidebar: order` values
4. Update all internal links using relative paths
5. Run `astro build` to verify

### Scenario 3: Upgrading Astro 4 to 5 with Active Feature Branch

**Conflict:** Main branch upgrades to Astro 5, feature branch on Astro 4.

**Best Approach:**

1. Rebase feature branch on updated main
2. Update feature branch's astro.config.mjs to v5 format
3. Remove deprecated options
4. Test with `astro build`
5. Verify feature still works in v5

### Scenario 4: Multiple Locale Additions

**Conflict:**

```javascript
// Branch A: Adds Spanish
locales: {
  en: { label: 'English' },
  es: { label: 'Español' },
}

// Branch B: Adds French
locales: {
  en: { label: 'English' },
  fr: { label: 'Français' },
}
```

**Solution:**

```javascript
locales: {
  en: { label: 'English' },
  es: { label: 'Español' },
  fr: { label: 'Français' },
}
```

**Additional Step:** Ensure translation files exist:
```
src/content/docs/
├── en/index.md
├── es/index.md
└── fr/index.md
```

---

## 8. Tools and Commands Reference

### Essential Commands

```bash
# Check for type/schema errors
astro check --validate

# Full build (catches most issues)
astro build

# Dev server (catches some issues earlier)
astro dev

# Check specific file
astro check src/content/config.ts
```

### Git Merge Tools

```bash
# Use Astro-aware merge tool (if configured)
git mergetool

# Show specific file from branches
git show HEAD:astro.config.mjs
git show feature:astro.config.mjs

# Check conflicted files
git status
```

### Validation Tools

```bash
# TypeScript checking
npm install -D @astrojs/check

# Link validation
npm install -D astro-link-validator

# Linting (optional)
npm install -D eslint-plugin-astro
```

---

## 9. Prevention Strategies

### Configuration Best Practices

1. **Document integration order:** Add comments in astro.config.mjs
   ```javascript
   integrations: [
     astroMermaid({...}),    // ⚠️ Must come before Starlight
     starlight({...}),
   ]
   ```

2. **Separate concerns:** Move large config blocks to separate files
   ```javascript
   // astro.config.mjs
   import { starlightConfig } from './config/starlight';
   import { mermaidConfig } from './config/mermaid';

   export default defineConfig({
     integrations: [
       astroMermaid(mermaidConfig),
       starlight(starlightConfig),
     ],
   });
   ```

3. **Version lock critical dependencies:**
   ```json
   {
     "dependencies": {
       "astro": "^5.0.0",
       "@astrojs/starlight": "^0.25.0",
       "astro-mermaid": "^0.5.0"
     }
   }
   ```

### Content Best Practices

1. **Use relative links** for internal documentation
2. **Define sidebar clearly** in config, not file structure
3. **Keep frontmatter schema in sync** across team
4. **Document page location requirements** if content order matters

### Git Workflow

1. **Create focused branches** — one feature per branch
2. **Avoid long-lived branches** — merge frequently
3. **Test configuration** before pushing — `astro build`
4. **Document config changes** in commit messages

---

## 10. References and Resources

### Official Documentation
- [Astro Configuration Reference](https://docs.astro.build/en/reference/configuration-reference/)
- [Astro Integration API](https://docs.astro.build/en/reference/integrations-reference/)
- [Upgrade to Astro v5](https://docs.astro.build/en/guides/upgrade-to/v5/)
- [Starlight Configuration Reference](https://starlight.astro.build/reference/configuration/)
- [Starlight Sidebar Navigation](https://starlight.astro.build/guides/sidebar/)
- [Starlight i18n Guide](https://starlight.astro.build/guides/i18n/)

### Integration Guides
- [Content Collections](https://docs.astro.build/en/guides/content-collections/)
- [Markdown in Astro](https://docs.astro.build/en/guides/markdown-content/)
- [MDX Integration](https://docs.astro.build/en/guides/integrations-guide/mdx/)
- [TypeScript in Astro](https://docs.astro.build/en/guides/typescript/)

### Validation Tools
- [@astrojs/check npm package](https://www.npmjs.com/package/@astrojs/check)
- [astro-link-validator GitHub](https://github.com/rodgtr1/astro-link-validator)
- [astro-mermaid npm package](https://www.npmjs.com/package/astro-mermaid)

### Community Resources
- [Extending Astro Markdown Processing](https://dev.to/fkurz/extending-astrojs-markdown-processing-with-remark-and-rehype-plugins-m1k)
- [Astro GitHub Issues](https://github.com/withastro/astro/issues)
- [Starlight GitHub Discussions](https://github.com/withastro/starlight/discussions)

---

## Appendix: Conflict Decision Tree

```
Merge conflict detected in Astro/Starlight project
│
├─ astro.config.mjs?
│  ├─ Integration order issue?
│  │  └─ Place Mermaid before Starlight, test order
│  ├─ Output mode changed?
│  │  └─ Choose based on deployment target
│  ├─ New integration added?
│  │  └─ Check if order-dependent
│  └─ Markdown/MDX config changed?
│     └─ Merge plugins, test plugin order
│
├─ src/content/config.ts?
│  ├─ Schema changed?
│  │  └─ Merge schemas, make new fields optional if needed
│  └─ Update all content files to match schema
│
├─ src/content/docs/**/*.md(x)?
│  ├─ Frontmatter conflicts?
│  │  └─ Keep all fields, reconcile sidebar order
│  ├─ Content/imports changed?
│  │  └─ Manual merge, update import paths
│  └─ Link path changed?
│     └─ Update all links using relative paths
│
└─ Build and validate
   ├─ astro check --validate
   ├─ astro build
   ├─ Verify dark/light modes
   └─ If any failure, review above steps
```

---

**Document Version:** 1.0
**Last Updated:** April 2026
**Scope:** Astro 4.x - 5.x, Starlight 0.20+
