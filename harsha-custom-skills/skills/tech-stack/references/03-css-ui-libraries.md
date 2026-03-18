# CSS & UI Component Libraries Reference Guide

**Last Updated:** February 2025
**Scope:** CSS frameworks, UI component libraries, styling solutions
**Target Audience:** Tech stack advisors, frontend architects

## Executive Summary (5-line TL;DR)
- Tailwind CSS v4 is the default choice: build-time, zero-runtime, massive ecosystem, 4x faster engine
- shadcn/ui + Radix primitives = best headless component strategy (copy-paste, full ownership, accessible)
- CSS-in-JS (styled-components, Emotion) declining due to runtime overhead; migrate to build-time solutions
- For Vue: use Nuxt UI or PrimeVue; for Svelte: use Skeleton or shadcn-svelte; for Angular: use Angular Material
- Native CSS (container queries, :has(), nesting, @layer) now covers 80% of preprocessor use cases

---

## Research Metadata

**Methodology:** Multi-source web search, npm trends, GitHub metrics, performance benchmarks
**Research Queries Used:**
- Tailwind CSS v4 2025 features & engine architecture
- shadcn/ui adoption & ecosystem growth
- CSS-in-JS runtime performance impacts
- Headless UI library comparisons (Radix, React Aria, Headless UI)
- Vue/Svelte UI ecosystem 2025
- Native CSS capabilities 2025

**Verification Sources:**
- Official documentation (Tailwind, MUI, Chakra, Radix)
- npm trends & download statistics
- GitHub star counts & release notes
- Performance benchmarks & case studies
- Community feedback & discussions

---

## CSS Approaches: Runtime vs Build-Time vs Zero-Runtime

### Comparison Matrix

| Approach | Runtime | Build-Time | Zero-Runtime | Example | Performance | DX | Learning Curve |
|----------|---------|-----------|--------------|---------|-------------|----|----|
| **Utility-First (Tailwind v4)** | No | Yes (JIT) | Yes | `<div class="px-4 py-2 bg-blue-500">` | Excellent | Fast | Low |
| **CSS Modules** | No | Yes | Yes | `.module.css` scoped imports | Excellent | Good | Low-Mid |
| **Vanilla Extract** | No | Yes | Yes | Zero-runtime CSS-in-TS | Excellent | Excellent | Mid |
| **Panda CSS** | No | Yes | Yes | Type-safe CSS-in-JS (build-time) | Excellent | Excellent | Mid |
| **CSS-in-JS (Styled Components)** | **Yes** | No | No | `styled.div\`color: blue;\`` | Good-Poor | Good | Mid |
| **UnoCSS** | No | Yes (JIT) | Yes | Atomic CSS, Tailwind alternative | Excellent | Fast | Low |
| **Open Props** | No | Yes | Yes | CSS custom properties | Excellent | Excellent | Low-Mid |
| **Native CSS** | No | Yes | Yes | Nesting, :has(), @layer | Excellent | Mid | Low-Mid |

**Key Finding:** Zero-runtime solutions dominate 2025. Runtime CSS-in-JS adds 12-35ms initial render overhead.

---

## Tailwind CSS v4: The New Standard

**Release Date:** January 22, 2025 (stable)
**Major Innovation:** Oxide engine (Rust-based compiler)

### Core Features

1. **Oxide Engine (5x-100x faster builds)**
   - Rust compiler replaces JavaScript pipeline
   - Full builds: 5x faster
   - Incremental builds: 100x faster (microseconds)
   - Direct CSS processing (no JS AST conversion)

2. **CSS-First Configuration**
   - Configuration now lives in CSS files (not JavaScript)
   - `@theme` directive for design tokens
   - Example:
     ```css
     @import "tailwindcss";
     @theme {
       --color-primary: #3b82f6;
     }
     ```

3. **Zero Configuration**
   - Single import: `@import "tailwindcss";`
   - Automatic content detection (no content array)
   - Works out-of-the-box

4. **Modern CSS Features First-Class**
   - Container queries native support
   - Cascade layers (@layer)
   - Registered custom properties
   - color-mix() function
   - 3D transforms

### Bundle Size & Performance
- Zero runtime overhead
- Generate only used classes
- Smaller output than v3 for most projects
- SSR-friendly

### Migration Path
- Most v3 projects upgrade automatically
- Config migration: manual for complex themes
- Recommended for all new projects

**Sources:**
- [Tailwind CSS v4 Release](https://tailwindcss.com/blog/tailwindcss-v4)
- [Oxide Engine Architecture](https://tailwindcss.com/blog/tailwindcss-v4-alpha)

---

## CSS Frameworks & Build-Time Solutions

### CSS Modules
**Use Case:** Established, zero-runtime CSS
**Bundle Size:** Minimal (only used styles)
**Customization:** Limited (class names are fixed)
**Learning Curve:** Low

**Strengths:**
- True scoped CSS (no naming conflicts)
- Zero runtime overhead
- Works with any meta-framework
- Great caching (separate CSS files)

**Weaknesses:**
- No dynamic theming without CSS variables
- Limited component composition
- Class name API constraints

---

### Vanilla Extract
**Use Case:** Type-safe CSS-in-TypeScript
**Bundle Size:** Zero-runtime, minimal output
**Customization:** Excellent (full TypeScript power)
**Learning Curve:** Mid-High

**Strengths:**
- Full TypeScript type safety for styles
- Zero runtime overhead
- Excellent for design systems
- Works with React Server Components

**Weaknesses:**
- Steeper learning curve than CSS Modules
- Smaller ecosystem than Tailwind
- Build-time only (no dynamic styles)

---

### Panda CSS
**Use Case:** Type-safe styling at scale
**Bundle Size:** Zero-runtime, ~5-8KB gzipped generated code
**Customization:** Excellent (multi-variant support)
**Learning Curve:** Mid

**Key Differentiators:**
- Multi-variant system (like CSS-in-JS but at build-time)
- Auto-generated TypeScript types
- Server Component compatible
- No "class explosion" (styles applied via `css()` function)
- Example:
  ```typescript
  const styles = css({ color: "blue", fontSize: "lg" });
  ```

**vs Tailwind:**
- Panda: Organized, type-safe, no class clutter
- Tailwind: Fast prototyping, utility-first, visible classes

**2025 Trend:** Adoption growing for enterprise design systems

**Source:** [Panda CSS 2025 Guide](https://medium.com/@sofia_marques/type-safe-styling-in-2025-why-panda-css-just-works-90c5321f0243)

---

### UnoCSS
**Use Case:** Lightweight atomic CSS alternative
**Bundle Size:** 8-15KB gzipped
**Customization:** Good (preset-based)
**Learning Curve:** Low

**Strengths:**
- Instant mode (no JIT compilation)
- Smaller than Tailwind for small projects
- Preset system highly customizable
- Works with Vite, Webpack, Rollup

**Weaknesses:**
- Smaller ecosystem than Tailwind
- Less documentation
- Not suitable for large projects

---

### Open Props
**Use Case:** CSS custom properties foundation
**Bundle Size:** 3-8KB (pick what you use)
**Customization:** Excellent (CSS variables)
**Learning Curve:** Low

**Approach:**
- Provides semantic CSS variables
- No build tool required
- Example: `var(--color-primary), var(--space-sm)`
- Mix-and-match with other solutions

---

### Native CSS (2025 Capabilities)

**What's Now Possible Without Frameworks:**

1. **CSS Nesting** (100% browser support 2025)
   ```css
   .card {
     padding: var(--space-md);
     &:hover {
       box-shadow: var(--shadow-lg);
     }
   }
   ```

2. **:has() Selector** (parent selection)
   ```css
   .container:has(> .error) {
     border-color: red;
   }
   ```

3. **Container Queries** (component-level responsiveness)
   ```css
   @container (min-width: 400px) {
     .card { display: grid; }
   }
   ```

4. **@layer** (cascade management)
   ```css
   @layer utilities { .p-4 { padding: 1rem; } }
   @layer components { .btn { ... } }
   ```

5. **CSS Custom Properties** (dynamic theming)
   ```css
   :root { --primary: #3b82f6; }
   .btn { color: var(--primary); }
   ```

**2025 Impact:** Many projects no longer need a CSS framework for basic styling. However, utility-first (Tailwind) still faster for rapid development.

---

## React UI Component Libraries

### Component Library Comparison Table

| Library | Components | Bundle (gzipped) | NPM Weekly | GitHub Stars | Accessibility | Customization | Learning Curve | Best For |
|---------|-----------|-----------------|-----------|-------------|---------------|---------------|----------------|----------|
| **shadcn/ui** | 50+ | 88 KB* | 250K+ | 106K | WAI-ARIA | Excellent | Low | Copy-paste, Tailwind |
| **Radix UI** | 40+ | 35-50 KB | 1.3M | 26K | WAI-ARIA | Excellent | Mid | Design systems |
| **MUI v6** | 60+ | 133 KB | 6M | 92K | WAI-ARIA | Good | Mid | Enterprise Material |
| **Ant Design 5** | 50+ | 120 KB | 2M | 90K | WAI-ARIA | Good | Mid | Enterprise China |
| **Chakra UI v3** | 50+ | 45 KB | 500K | 37K | WAI-ARIA | Excellent | Low-Mid | React, custom themes |
| **Mantine v7** | 100+ | 65 KB | 280K | 28K | WAI-ARIA | Excellent | Low | Full-featured apps |
| **NextUI v2** | 30+ | 40 KB | 150K | 13K | WAI-ARIA | Excellent | Low | Beautiful defaults |
| **Headless UI** | 12 | 20 KB | 1.35M | 25K | WAI-ARIA | Excellent | Low | Tailwind integration |
| **React Aria** | Hooks | 30 KB | 260K | 11K | Adobe a11y | Excellent | Mid | A11y-first |
| **Park UI** | 30+ | 50 KB | 50K | 8K | WAI-ARIA | Excellent | Low | Ark + Panda |

*shadcn/ui is copy-paste; bundle size varies per project (only install used components)

### The "shadcn/ui Effect": Why Copy-Paste Changed Everything

**The Shift (2023-2025):**
- **Before:** Install dependency, accept opinionated styles/components
- **After:** Copy source code, full control, can fork/modify components

**Why It Matters:**
1. **Ownership:** Users own the component code
2. **Customization:** Trivial to modify components for specific needs
3. **Vendor Lock-In:** Avoided (code lives in your repo, not node_modules)
4. **Bundle Size:** Pay for what you use (no unused components)
5. **Community Over Hierarchy:** Component updates come from community, not library maintainers

**2025 Reality:**
- shadcn/ui is "default UI lib of LLMs" (Tony Dinh, DevUtils founder)
- 106K+ GitHub stars, 250K+ weekly npm installs
- 90K+ projects actively using it
- Ecosystem exploded: builders, themes, alternative implementations

**Ecosystem Examples:**
- shadcn-svelte (copy-paste for Svelte)
- shadcn-vue (community Vue adaptation)
- Reka UI (from shadcn creator, next-gen headless)
- Hundreds of component builders/theme tools

**Source:** [Rise of shadcn/ui 2025](https://saasindie.com/blog/shadcn-ui-trends-and-future)

---

### Key Library Highlights

#### Radix UI (Headless Primitives)
**Philosophy:** Unstyled, accessible, composable
**Bundle:** 35-50 KB (tree-shakeable)
**Accessibility:** Full WAI-ARIA
**Best For:** Design system foundations

- Foundation of shadcn/ui
- Works with any CSS solution
- Excellent for custom design systems
- Stable, battle-tested (used at Vercel, etc.)

#### MUI v6 (Material Enterprise)
**Release:** 2024, with v7 planned H1 2025
**New in v6:**
- CSS Variables (theme generation)
- Pigment CSS integration (opt-in zero-runtime)
- Grid v2 with gap property
- React 19 support
- Future: ESM improvements in v7

**Best For:** Enterprise apps needing Material Design
**Caution:** Bundle size is 133KB (largest in category)

#### Chakra UI v3 (Ark Rewrite)
**Major Rewrite:** Now uses Ark UI (headless) + Panda CSS foundation
**Performance:** Significant improvements with state machines
**New Components:** ColorPicker, DatePicker coming
**Release:** Stable in 2025, Ark v5 released March 2025

**Key Change:** Variant-based system ("recipes") for cleaner API

#### Mantine v7 (100+ Components)
**Strengths:**
- Largest component count (100+)
- 280K weekly downloads
- Full-featured (forms, modals, notifications, etc.)
- Excellent hooks integration
- Great documentation

**Learning Curve:** Lowest of "full-featured" libraries

#### NextUI v2 (Tailwind Foundation)
**Strengths:**
- Beautiful pre-styled components
- Tailwind-based (familiar to Tailwind users)
- Smaller bundle than MUI
- Server Component support

---

## Headless UI & Accessibility-First

### Radix UI vs Headless UI vs React Aria (2025 Comparison)

**Radix UI**
- 40+ components
- Most flexible for customization
- Tree-shakeable, small bundles
- Strongest on customization depth

**Headless UI**
- 12 core components
- Tailwind Labs (trusted source)
- Simplest API
- Best Tailwind integration
- Vue + React support

**React Aria (Adobe)**
- Behavior hooks (not pre-built components)
- 260K weekly downloads
- Backed by Adobe accessibility expertise
- Best for a11y-first projects
- Need to build UI layer yourself

**Decision Tree:**
```
Need full control over styling?
  → Radix UI (40+ components, very flexible)

Tailwind user, minimal components?
  → Headless UI (simple, Tailwind-perfect)

Accessibility is top priority?
  → React Aria (Adobe-backed, a11y hooks)

Copy-paste components?
  → shadcn/ui (uses Radix + Tailwind)
```

**Source:** [Radix vs Headless vs Aria 2025](https://blog.logrocket.com/headless-ui-alternatives-radix-primitives-react-aria-ark-ui/)

---

## Vue UI Libraries (2025)

| Library | Components | Bundle | NPM Weekly | Stars | Best For |
|---------|-----------|--------|-----------|-------|----------|
| **Vuetify 3** | 80+ | Heavy | 700K | 41K | Material Design |
| **PrimeVue** | 90+ | Mid | 200K | 10K | Enterprise |
| **Radix Vue/Reka UI** | 30+ | Small | 50K | 5K | Headless design |
| **shadcn-vue** | 50+ | ~88KB | 30K | 4K | Copy-paste |

### Standouts

**Vuetify 3**
- Most popular Vue component library
- 41K GitHub stars
- 700K weekly downloads
- Material Design spec
- **Downside:** Heavy bundle, less flexible styling

**PrimeVue**
- 90+ components (most in Vue ecosystem)
- Lighter than Vuetify
- Great Tailwind CSS integration
- Enterprise-focused
- PrimeTek backing

**Reka UI (ex-Radix Vue)**
- Rebranded 2025 (from Radix Vue)
- Headless approach
- WAI-ARIA compliant
- Best for custom design systems

**shadcn-vue** (Community)
- Copy-paste shadcn components for Vue
- Growing ecosystem
- 50+ components available

---

## Svelte UI Libraries (2025)

| Library | Type | Svelte 5? | Tailwind | Best For |
|---------|------|-----------|---------|----------|
| **shadcn-svelte** | Copy-paste | Yes | Yes | Copy-paste Tailwind |
| **Bits UI** | Headless | Yes | Yes | Custom components |
| **Skeleton** | Pre-styled | Yes | Yes | Design systems |

### Svelte Specifics

**shadcn-svelte**
- Copy-paste component CLI
- Uses Bits UI underneath
- Svelte 5 + Tailwind v4 support
- New chart component (LayerChart)
- Growing ecosystem

**Bits UI**
- Headless primitives for Svelte 5
- Zero-styled, maximum customization
- Native Svelte reactivity
- Works perfectly with Tailwind

**Skeleton UI**
- Pre-styled design system
- Full Figma support
- Built on Zag.js (like Ark UI)
- ARIA support + keyboard navigation
- Opinionated but flexible

---

## Bundle Size Analysis (2025)

### Performance Impact by Approach

| Category | Size | Impact | Recommendation |
|----------|------|--------|-----------------|
| **No UI Library** (CSS Modules + native) | 0 | Baseline | Small projects |
| **Tailwind v4 only** | 8-20 KB | Minimal | Most projects |
| **Headless UI + Tailwind** | 25-35 KB | Very Low | Tailwind users |
| **Radix UI + CSS** | 35-50 KB | Low | Design systems |
| **Mantine** | 65 KB | Low-Mid | Full-featured |
| **Chakra UI v3** | 45 KB | Low-Mid | Theme flexibility |
| **NextUI** | 40 KB | Low-Mid | Beautiful defaults |
| **MUI** | 133 KB | High | Enterprise only |
| **Ant Design** | 120 KB | High | Enterprise only |

**CSS-in-JS Runtime Overhead (2025):**
- Styled Components: +100ms load time, 3-8ms per re-render
- Emotion: Similar to Styled Components
- Zero-runtime solutions (Linaria, Panda): No overhead

**Source:** [CSS-in-JS Performance 2025](https://markaicode.com/css-in-js-vs-css-modules-performance-analysis-2025/)

---

## Accessibility Compliance Comparison

**All modern libraries (2025) meet WCAG 2.1 AA:**

| Aspect | Radix | MUI | Chakra | Mantine | shadcn/ui | Headless UI |
|--------|-------|-----|--------|---------|-----------|------------|
| **WCAG 2.1 AA** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Keyboard Nav** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Screen Readers** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Color Contrast** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Focus Mgmt** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Standout:** React Aria (Adobe) for accessibility-first approach

---

## Decision Tree: "Which CSS/UI Approach?"

```
START: Choose CSS Approach
│
├─ NEW PROJECT / RAPID PROTOTYPING?
│  └─ → Tailwind CSS v4 (fastest path to production)
│
├─ ENTERPRISE / MATERIAL DESIGN?
│  ├─ → MUI v6 (standard enterprise choice)
│  └─ → Ant Design (if China ecosystem needed)
│
├─ CUSTOM DESIGN SYSTEM?
│  ├─ → Panda CSS + Ark UI (type-safe, modern)
│  └─ → Vanilla Extract (TypeScript-native)
│
├─ MAXIMUM CUSTOMIZATION?
│  ├─ → Headless UI + CSS Modules (simplicity)
│  └─ → Radix UI + CSS (max flexibility)
│
├─ BEAUTIFUL DEFAULTS, MINIMAL CONFIG?
│  ├─ → shadcn/ui (copy-paste, Tailwind)
│  ├─ → NextUI (Tailwind pre-styled)
│  └─ → Chakra UI v3 (React, flexible)
│
├─ FULL-FEATURED COMPONENT SET?
│  ├─ → Mantine (100+ components)
│  └─ → PrimeVue (for Vue)
│
└─ FRAMEWORK SPECIFIC?
   ├─ REACT → shadcn/ui (default 2025)
   ├─ VUE → Vuetify (Material) or Reka UI (headless)
   └─ SVELTE → shadcn-svelte or Bits UI
```

---

## Performance Impact Analysis

### Runtime CSS-in-JS vs Build-Time vs Utility-First (2025)

**Runtime CSS-in-JS (Styled Components, Emotion)**
- Initial render: +12-35ms overhead
- Re-render: +3-8ms per styled component
- Bundle size: +15-45KB
- 2025 Trend: **Declining** (being phased out for React Server Components)
- **Use Only If:** Dynamic theming is critical requirement

**Build-Time CSS-in-JS (Panda CSS, Vanilla Extract)**
- Initial render: 0ms overhead
- Re-render: 0ms overhead
- Bundle size: Minimal (+5-8KB)
- Type safety: Full (TypeScript)
- 2025 Trend: **Growing** (becoming enterprise standard)

**Utility-First (Tailwind v4)**
- Initial render: 0ms overhead
- Re-render: 0ms overhead
- Bundle size: Minimal (8-20KB)
- DX: Fastest prototyping
- 2025 Trend: **Dominant** (most new projects)

**CSS Modules + Native CSS**
- Initial render: 0ms overhead
- Re-render: 0ms overhead
- Bundle size: Minimal (separate CSS files, browser cached)
- 2025 Trend: **Viable alternative** (especially with container queries)

**Recommendation:** Default to zero-runtime solutions in 2025. Runtime CSS-in-JS only for specific dynamic theming needs.

---

## Gaps & Limitations (2025)

### Remaining Unsolved Problems

1. **Dark Mode & Theme Switching**
   - Tailwind: Works well (class-based)
   - CSS-in-JS: Excellent (runtime + CSS variables)
   - Panda: Good (CSS variables at build-time)
   - Limitation: No perfect solution for instant switching

2. **Dynamic Component Styling**
   - shadcn/ui: Limited (copy-paste components)
   - Radix: Limited (bring-your-own styles)
   - MUI: Full support (runtime theming)
   - Gap: Headless libraries require external solution

3. **Server Component Compatibility**
   - Tailwind: ✓ Excellent
   - Panda: ✓ Excellent
   - Chakra v3: ✓ Good
   - CSS-in-JS: ✗ No (cannot serialize styles in RSC)

4. **Incremental Migration**
   - Gap: No library makes it trivial to migrate old projects
   - Reality: Usually full rewrite needed

5. **CSS-in-TS Type Safety**
   - Panda: ✓ Excellent
   - Vanilla Extract: ✓ Excellent
   - Tailwind: Partial (CVA + clsx, not native)
   - Gap: Tailwind ecosystem still catching up

---

## Source Registry

### Official Documentation
- [Tailwind CSS Official](https://tailwindcss.com/)
- [Radix UI Primitives](https://www.radix-ui.com/)
- [MUI Material-UI](https://mui.com/)
- [Chakra UI](https://chakra-ui.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Mantine](https://mantine.dev/)

### Research Sources (2025)
- [Tailwind CSS v4 Release](https://tailwindcss.com/blog/tailwindcss-v4)
- [Rise of shadcn/ui 2025](https://saasindie.com/blog/shadcn-ui-trends-and-future)
- [CSS-in-JS Performance 2025](https://markaicode.com/css-in-js-vs-css-modules-performance-analysis-2025/)
- [Panda CSS vs Tailwind Guide](https://medium.com/@sofia_marques/type-safe-styling-in-2025-why-panda-css-just-works-90c5321f0243)
- [Radix vs Headless vs Aria Comparison](https://blog.logrocket.com/headless-ui-alternatives-radix-primitives-react-aria-ark-ui/)
- [MUI v6 Release Notes](https://mui.com/blog/material-ui-v6-is-out/)
- [Chakra UI v3 & Ark Integration](https://chakra-ui.com/blog/announcing-v3)
- [Native CSS Features 2025](https://blog.logrocket.com/native-css-nesting/)
- [Vue UI Comparison 2025](https://uibakery.io/blog/top-vue-component-libraries)
- [shadcn-svelte Documentation](https://www.shadcn-svelte.com/)

---

## Quick Reference: 2025 Recommendations by Use Case

### Startup / MVP / Rapid Prototyping
**Stack:** Tailwind v4 + shadcn/ui
**Rationale:** Fastest to market, copy-paste components, zero configuration
**Bundle:** ~95 KB (combined)

### Enterprise Application
**Stack:** Panda CSS + Ark UI or MUI v6
**Rationale:** Type safety, design system, performance
**Bundle:** 45-133 KB

### Design System
**Stack:** Vanilla Extract or Panda CSS + Radix UI
**Rationale:** Type-safe tokens, zero-runtime, composable
**Bundle:** 35-50 KB (base)

### Content Site / Blog
**Stack:** Native CSS + minimal framework
**Rationale:** Lightweight, SEO-friendly, no overhead
**Bundle:** <20 KB

### Full-Featured CRUD App
**Stack:** Mantine or Chakra UI v3
**Rationale:** 100+ pre-built components, forms, hooks
**Bundle:** 45-65 KB

### Accessibility-First Project
**Stack:** React Aria + custom CSS
**Rationale:** Adobe-backed, a11y hooks, behavior-focused
**Bundle:** 30 KB + custom CSS

---

## Version History & Future Outlook

### Stable (Recommended Production Use)
- Tailwind CSS v4 (Jan 2025)
- Radix UI v1 (mature, stable)
- shadcn/ui v0.9+
- MUI v6
- Chakra UI v3
- Mantine v7

### In Development / Near Release
- MUI v7 (H1 2025) - ESM improvements
- Ark UI v5+ (March 2025)
- Svelte 5 ecosystem updates

### Sunset / Not Recommended
- CSS-in-JS for React Server Components (runtime conflict)
- Chakra UI v2 (v3 available)
- Tailwind CSS v3 (v4 incomparably faster)

---

**Document Version:** 1.0
**Last Verified:** February 2025
**Maintenance:** Quarterly review recommended

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->

---
## Related References
- [Frontend Frameworks](./01-frontend-frameworks.md) — Framework selection drives CSS/UI choices
- [Meta-Frameworks](./02-frontend-meta-frameworks.md) — Framework-specific UI ecosystems
- [Performance Benchmarks](./47-performance-benchmarks.md) — Bundle size and CSS performance data
