# Frontend JavaScript Frameworks 2026: Comprehensive Reference

**Research Tier:** Maximum Scrutiny | **Analysis Date:** March 3, 2026 | **Status:** Production-Ready Frameworks

## Executive Summary (5-line TL;DR)
- React 19 dominates with 86.9M weekly downloads; use for most projects needing large ecosystem and hiring pool
- Svelte 5 (runes) and SolidJS offer best raw performance (50%+ smaller bundles, faster DOM ops than React); Svelte 5 now top satisfaction
- Vue 3.6 beta with Vapor Mode (now feature-complete) is the balanced choice: good performance, excellent DX, strong ecosystem
- Angular 20+ signals stable and default; v21+ zoneless rendering by default for significant performance gains
- HTMX/Alpine.js suit server-rendered apps needing minimal interactivity without SPA complexity

---

## Research Metadata

### Verification Method
Cross-referenced with [js-framework-benchmark](https://github.com/krausest/js-framework-benchmark), official framework documentation, [State of JS 2025](https://2025.stateofjs.com/), and npmtrends.com analytics.

### Queries Executed (10 core searches + 20+ supplementary)
- React 19/19.2 features, bundle size, performance, Server Components stable status
- Vue 3.5+/3.6 Vapor Mode compilation strategy and feature-complete beta status
- Svelte 5 runes adoption feedback, performance benchmarks, ecosystem growth
- Angular 19/20/21 signals, standalone components, zoneless rendering stability
- Solid.js fine-grained reactivity benchmarks, ecosystem maturity (still v1.9.x)
- JS framework benchmark 2025 results (startup, DOM updates, memory)
- NPM weekly downloads comparison: React (86.9M), Vue (7.4M), Angular (755K), SolidJS (1.65M), Svelte (2.06M)
- HTMX adoption metrics: 47.2K GitHub stars, production usage stories, State of JS rankings
- Qwik 1.18.0 current state, Builder.io investment, v2.0 roadmap
- State of JS 2025 survey: framework satisfaction rankings, usage trends, Svelte 5 top DX, Solid 5-year high satisfaction

**Contradictions Documented:** React hydration tradeoffs vs Qwik resumability, Virtual DOM vs fine-grained reactivity performance gaps

---

## Quick Reference Matrix

| Framework | Latest | Bundle (gzip) | NPM Weekly | GitHub Stars | Learning | TypeScript | When to Use |
|-----------|--------|---------------|-----------|--------------|----------|-----------|------------|
| **React** | 19.2+ | 42-54 KB | 86.9M | 230K | Medium | Native | Safe default, massive ecosystem, hiring pool |
| **Vue** | 3.6 beta | 34 KB | 7.4M | 209K | Easy | Native | Progressive enhancement, smooth learning curve |
| **Svelte** | 5+ | 3-10 KB | 2.06M | 83K | Easy | Via compiler | Performance-first, smallest bundle, best DX, top satisfaction |
| **Angular** | 20+ | Variable | 755K | 80K | Steep | Native | Enterprise scale, enforced architecture, signals stable |
| **Solid.js** | 1.9.11+ | 7 KB | 1.65M | 37K | Medium | Via babel | Fine-grained reactivity, benchmark champ, 5-year satisfaction high |
| **Qwik** | 1.18.0 | Variable | N/A | 30K | Medium-Steep | Native | Zero JS on initial load, resumability focus, v2.0 coming |
| **Preact** | 10.22+ | 3 KB | 13.5M | 36K | Easy | Via compat | React API with minimal footprint |
| **Alpine** | 3.14+ | 7 KB | N/A | 29K | Trivial | No | Light interactivity, jQuery replacement |
| **HTMX** | 1.9+ | 14 KB | N/A | 47.2K | Trivial | No | Server-driven HTML responses, hypermedia, renaissance 2026 |
| **Lit** | 3.1+ | 6 KB | N/A | 18K | Easy | Via TypeScript | Web components, design systems |

---

## Framework Deep Dives

### React 19.2+ (December 2024 → March 2026)

**Version Progression:** React 19 (Dec 2024), v19.1 (June 2025), v19.2+ stable (Oct 2025 onward, actively maintained March 2026)

**Bundle Size:** 42-54 KB gzipped (baseline). Increased from React 18 due to new APIs but improved tree-shaking capabilities. [React 19.2 Release Notes](https://react.dev/blog/2025/10/01/react-19-2)

**Key Features Added (2025-2026):**
- **Actions API** for async operations with automatic pending states and form resets
- **Server Components** now stable and recommended for data fetching (RSC directives stable)
- **useEffectEvent** hook for splitting event logic from effects
- **Partial Pre-rendering** in React DOM for hybrid rendering
- **Custom Element Support** with attribute/property distinction at SSR
- **Activity Component** (experimental) for conditional rendering with effect unmounting
- **32% render cycle reduction** in heavy update scenarios via expanded auto-batching [React 19.2](https://react.dev/blog/2024/12/05/react-19)

**NPM Weekly:** 86.9M downloads (significant growth from 57.7M in Feb; ecosystem solidifying)
**GitHub Stars:** 230K+ | **Dependents:** 5.1M+ packages

**When to Use:**
- Safest choice for long-lived, large-scale production apps
- Massive hiring pool and third-party ecosystem
- Job market demand remains highest
- Recommended for teams with 5+ developers
- Enterprise applications with strict SLA requirements

**Known Limitations/Gotchas:**
- Hydration mismatch debugging still challenging
- Larger bundle baseline vs Svelte/Preact makes initial load slower
- Actions API learning curve for Form handling
- Server Components add complexity for beginners
- useState loop risks on SSR

**Ecosystem Maturity:** Near-perfect (routing: Next.js/Remix, state: Redux/Zustand, UI: Material-UI, testing: Vitest/Jest)

---

### Vue 3.6 Beta (July 2025 → March 2026)

**Version Progression:** Vue 3.5.26 (maintenance mode end 2025), Vue 3.6 now in beta with Vapor Mode feature-complete

**Vapor Mode Status:** Feature-complete in v3.6 beta but still unstable/experimental. Performance parity with Solid and Svelte 5 in 3rd-party benchmarks. Requires `<script setup>` syntax. Major reactivity refactor with alien-signals improving performance and memory. [Vue Mastery on Vapor](https://www.vuemastery.com/blog/whats-next-for-vue-in-2025/)

**Composition API:** Stable in v3.5, will remain in Vapor Mode (opt-in for new compilation strategy).

**Bundle Size:** 34 KB standard Vue 3, ~6 KB Vapor Mode (when v3.7+ reaches stable)

**NPM Weekly:** 7.4M downloads (stable, consistent ecosystem)
**GitHub Stars:** 209K | **Dependents:** 920K+ packages

**When to Use:**
- Progressive enhancement: start simple, scale gradually
- Smoother onramp than React for junior developers
- Performance-conscious teams (Vapor Mode approaching stable; expect v3.7 mid-2026)
- Balanced ecosystem: not as massive as React, not niche like Solid
- TypeScript-first projects with native support

**Vapor Mode Trade-offs:**
- Beta status; feature-complete but not production-ready until v3.7+
- Opts into compilation-heavy approach similar to Svelte
- Limited ecosystem compatibility during beta phase
- All existing Vue components work; only gain Vapor benefits if refactored to `<script setup>`
- Recommend waiting for v3.7+ stable release (mid-late 2026) for production use

**Ecosystem:** Large (Nuxt for SSR, Pinia for state, Vue Router, Vitest)

---

### Svelte 5+ (December 2024 → March 2026)

**Runes System:** Replaces older reactivity model. `$state()`, `$props()`, `$derived()` enable explicit, fine-grained reactivity. Backward compatible; existing components work without changes, new features are opt-in. [Svelte Runes Guide](https://luminary.blog/techs/05-svelte5-refresher/)

**Bundle Size Advantage (Verified):**
- Basic app: 3-10 KB (vs React's 42-54 KB)
- 50% reduction vs Svelte 4 in existing apps
- 15-30% smaller production bundles + better tree-shaking
- No virtual DOM = direct DOM manipulation
- Load time 40% faster than equivalent React build [Svelte Benchmarks](https://www.scalablepath.com/javascript/svelte-5-review)

**Compiler Optimizations:** Svelte shifts work to build time. Reactive statements compiled to efficient imperative DOM updates. No runtime overhead for virtual DOM diffing.

**Developer Satisfaction:** Svelte 5 achieved top satisfaction ranking (91% retention) per State of JS 2025, above all other major frameworks for Developer Experience.

**NPM Weekly:** 2.06M downloads (strong growth trajectory, 4x increase from reported 500K)
**GitHub Stars:** 83K+ | **Dependents:** 180K+ packages

**When to Use:**
- Performance-critical applications (mobile, low-bandwidth)
- Personal projects or startups with small teams
- Green-field projects where you can avoid legacy dependencies
- Component-focused libraries where DX matters
- SEO-heavy content sites (faster first paint)

**Learning Curve:** Easiest of major frameworks (even easier than Vue)

**Known Limitations:**
- Smaller hiring pool than React (but growing rapidly)
- Component library ecosystem still developing (SvelteUI, Skeleton maturing)
- SSR story less mature than Next.js (SvelteKit improving)
- Runes optional; backward compatible with existing Svelte 4 codebases
- Class components not supported

**Ecosystem Maturity:** Good but not massive (SvelteKit for SSR, stores for state, community UI libraries)

---

### Angular 20+ (November 2025 → March 2026)

**Signals as First-Class (v20 STABLE):** All fundamental reactivity primitives now stable and graduated in v20: `signal()`, `effect()`, `linkedSignal()`, signal-based queries, inputs. Signals are the recommended primary state management approach for all new projects.

**Zoneless Rendering (v20.2+ STABLE):** Zoneless change detection now stable and production-ready. Default in Angular v21+. Provides 20-35% reduction in change detection cycles and lower CPU usage on large apps (100+ visible components). [Angular Zoneless Docs](https://angular.dev/guide/zoneless)

**Standalone Components:** Standalone pattern now default; legacy NgModules still supported but discouraged.

**Bundle Size:** Highly variable (20-100+ KB depending on configuration). Full Angular app with routing/forms significantly heavier than alternatives.

**NPM Weekly:** 755K downloads (enterprise adoption growing significantly from 434K)
**GitHub Stars:** 80K+ | **Dependents:** 380K+ packages

**When to Use:**
- Enterprise applications with 20+ developers
- Teams that prefer enforced architecture and opinions
- Strict typing requirements and class-based components
- Full-stack development (TypeScript everywhere)
- Mission-critical systems requiring strong patterns

**strictStandalone Flag:** Enables compiler to enforce standalone usage patterns

**Known Limitations:**
- Steepest learning curve of major frameworks
- Opinionated structure can feel restrictive for small projects
- Bundle bloat if not carefully optimized
- Hiring pool smaller than React
- Migrations from older versions complex

**Ecosystem:** Massive and mature (Angular Material, routing, testing, forms, HTTP client all included)

---

### Solid.js 1.9.11+ (Fine-Grained Reactivity Champion)

**Fine-Grained Reactivity:** Updates only specific affected DOM elements. React re-executes components; Solid granularly updates. [Fine-Grained Reactivity Docs](https://docs.solidjs.com/advanced-concepts/fine-grained-reactivity)

**Benchmark Performance:** Consistently top-performer across js-framework-benchmark metrics:
- 40% faster rendering than React (SolidJS benchmark data)
- Comparable to Svelte in most measurements
- Smallest memory footprint in update-heavy scenarios
- Direct DOM manipulation with compile-time optimizations

**Bundle Size:** 7 KB core (competitive with Svelte when minified)

**Satisfaction Record:** Solid holds 5-year high satisfaction ranking per State of JS 2025, despite being used by only 10% of respondents (consistent elite developer experience).

**NPM Weekly:** 1.65M downloads (rapid growth; 33x increase from 50K, showing strong ecosystem traction)
**GitHub Stars:** 37K+ | **Dependents:** Limited (emerging)

**When to Use:**
- High-frequency updates (real-time dashboards, data visualization, AI monitoring)
- Developers who understand reactive systems (from RxJS background)
- Performance benchmarks are non-negotiable requirement
- You want React mental model with fine-grained reactivity
- SolidStart meta-framework for full-stack apps
- E-commerce checkouts and real-time applications (40% of new Vite stacks per 2026 industry data)

**Known Limitations:**
- Still smaller hiring pool than React/Vue, but growing
- Limited third-party component library ecosystem (expanding)
- Younger community with fewer Stack Overflow answers
- SolidStart released v1.0+ (2025); ecosystem maturing
- Not ideal for junior developers unfamiliar with fine-grained reactivity

**Creator:** Ryan Carniato (independent developer, formerly Builder.io)

---

### Qwik 1.18.0 (Resumability Architecture)

**Resumability Core Concept:** Unlike hydration (download + execute entire framework), Qwik resumes from server state without hydration. Zero JavaScript on initial load with `<script>` injection pattern. [Qwik Resumability Docs](https://qwik.dev/docs/concepts/resumable/)

**Real-World Impact:** Builder.io reduced load times 60% migrating from React to Qwik by shipping zero-hydration interactive editor (official case study). Cutting-edge drag-and-drop performance.

**Bundle Size:** Highly variable; framework lazy-loads code on-demand. Initial payload minimal (no hydration penalty), total size accumulates based on user interactions.

**Current Status (March 2026):** Active development at v1.18.0; backward compatibility maintained. v2.0 roadmap focuses on lowering resumability costs around component boundaries and HTML encoding (no breaking changes planned).

**GitHub Stars:** 30K+ | **Dependents:** Growing

**When to Use:**
- SEO-critical sites (content, e-commerce) where FCP/LCP are business metrics
- Edge-first architectures (Netlify, Vercel edge functions)
- Zero-JS requirements for initial render
- Builder.io drag-and-drop editor patterns
- When resumability benefits outweigh ecosystem immaturity

**Qwik City Status:** Meta-framework (like Next.js) improving rapidly. Routing/layouts now React/Next.js-comparable maturity.

**Known Limitations:**
- Ecosystem smaller than React/Vue but growing
- Documentation solid but resumability paradigm unfamiliar to most developers
- Debugging resumability issues requires new mental models
- Plugin ecosystem emerging
- Team should understand resumability paradigm before adopting

**Investment:** Builder.io backing; active development roadmap for v2.0

---

### Preact 10.22+ (3 KB React Alternative)

**Size Advantage:** 3 KB gzipped vs React's 42+ KB. ~14x smaller. [Preact GitHub](https://github.com/preactjs/preact)

**preact/compat:** Compatibility layer enables 100% React component reuse (for most use cases). Can alias `react` → `preact/compat` in bundler.

**Use Cases:** Widget embedding, lightweight PWAs, performance-constrained environments, IoT dashboards

**When to Use:**
- Strict bundle size budget (under 10 KB total JS)
- Legacy environments (older devices, slow networks)
- Embedding widgets in third-party sites
- When ecosystem doesn't need full React complexity
- Progressive enhancement scenarios

**Trade-offs:**
- Smaller community means fewer tutorials/resources
- preact/compat has edge case incompatibilities
- Some React DevTools features unavailable

---

### Alpine.js 3.14+ (jQuery for Modern Web)

**Size & API:** ~7 KB gzipped. 15 attributes, 6 properties, 2 methods. Markup-driven interactivity. [Alpine.js Docs](https://alpinejs.dev/)

**Philosophy:** Write JavaScript-like behavior directly in HTML attributes. No build process required.

**When to Use:**
- Server-rendered apps (Rails, Laravel, Django) adding interactivity
- WordPress/Shopify themes needing light enhancements
- When full framework complexity is overkill
- Teams preferring template-driven development
- Rapid prototyping without build tooling

**vs jQuery:** Modern alternative using vanilla JS promises/fetch, smaller API surface, designed for declarative HTML

---

### HTMX 1.9+ (Hypermedia Architecture)

**Philosophy:** HTML over the Wire. Server sends back HTML fragments; HTMX swaps them into the DOM via AJAX. No SPA framework needed.

**Adoption Metrics (March 2026):** 47.2K GitHub stars (gained 3.2K since Feb), stabilized from peak hype. State of JS 2025 ranking consistent; 22nd most popular per Stack Overflow (3.3% adoption). Developer adoption remains niche (<0.1% production usage) but growing in enterprise internal tools and smaller company stacks. [HTMX Renaissance](https://www.softwareseni.com/the-htmx-renaissance-rethinking-web-architecture-for-2026/)

**When to Use:**
- Monolithic backends serving HTML (Rails, Django)
- Applications where server-side routing is natural fit
- Teams avoiding JavaScript complexity
- Content-heavy sites with minimal interactivity requirements
- Prefer REST/form semantics over client-side state management

**Known Limitations:**
- Most production apps still use React/Vue/Angular
- Limited component reusability across projects
- Network round-trips on every interaction
- Not suitable for offline-first applications

**Growing Trend:** Resurgent interest in server-driven UI patterns as complexity backlash to SPAs

---

### Lit 3.1+ (Web Components)

**Web Components Strategy:** Build reusable, framework-agnostic components using native Web Components APIs. Virtual DOM-free, minimal (~6 KB).

**Use Cases:**
- Design systems (Material Web Components by Google, Lightning Web Components by Salesforce)
- Micro frontends and component composition
- Multi-framework environments
- Enterprise component libraries

**When to Use:**
- Design system that must work across React/Vue/Angular projects
- Long-term component maintainability (browser standards vs framework churn)
- Enterprise architecture requiring micro frontends

**Ecosystem Gaps:** Smaller library ecosystem compared to React, Vue, or Angular

---

## Performance Benchmark Summary (2025-2026)

Based on [js-framework-benchmark (official results)](https://krausest.github.io/js-framework-benchmark/):

**Runtime Performance (DOM updates):**
1. Solid.js / Svelte 5 (consistently ~40-50% faster than React)
2. Qwik (zero hydration cost, but total size varies)
3. Vue 3 / Lit (competitive with Svelte in many scenarios)
4. React 19 (improved with batching, still vDOM overhead)
5. Angular (heavy with full configuration)

**Startup Performance (TTI/FCP):**
1. Qwik (zero JS on initial render)
2. Svelte 5 / Solid (minimal runtime)
3. Preact (smaller than React)
4. Vue 3
5. React 19
6. Angular (slowest)

**Memory Footprint:**
1. Solid.js (fine-grained reactivity = minimal object creation)
2. Svelte 5 (compiled approach)
3. Lit (Web Components native)
4. Preact / Vue
5. React
6. Angular (largest)

**Contradiction Note:** Benchmark results vary by measurement (startup vs sustained updates). Synthetic benchmarks don't capture real-world app complexity. [Framework Benchmarks Caveat](https://itnext.io/benchmarking-frontends-in-2025-f6bbf43b7721)

---

## Framework Selection Decision Tree

```
Do you need massive ecosystem + hiring pool?
├─ YES → React (safe default despite size)
├─ NO → Continue

Do you prioritize smallest bundle size + lean runtime?
├─ YES → Svelte 5 (if you accept smaller community)
├─ NO → Continue

Do you need enterprise-scale architecture enforced?
├─ YES → Angular (full batteries-included)
├─ NO → Continue

Do you want fine-grained reactivity + top performance benchmarks?
├─ YES → Solid.js (if you accept emerging ecosystem)
├─ NO → Continue

Do you need zero JS on initial render (SEO/edge-first)?
├─ YES → Qwik + Qwik City
├─ NO → Continue

Do you prefer progressive enhancement / easy learning?
├─ YES → Vue 3 (best balance)
├─ NO → Continue

Is this a lightweight widget or server-rendered site needing interactivity?
├─ YES → Alpine.js or HTMX
├─ NO → React (fallback)
```

---

## When NOT to Use a Framework

**Static Sites:** Use Astro, Hugo, or vanilla HTML. Pure frameworks overkill.

**Simple Interactivity:** Alpine.js / HTMX / vanilla JS sufficient. Full framework adds dead weight.

**Server-Rendered Monoliths:** HTMX + backend rendering often simpler than client-heavy SPA.

**Performance-Critical (Low-Bandwidth):** Preact or Svelte mandatory; React/Angular problematic.

---

## Emerging Trends (March 2026 Update)

1. **Signals Now Stable:** Angular v20+ signals fully stable and default; React experimenting; Solid dominates. Fine-grained reactivity proving superior to virtual DOM in measurable scenarios.
2. **Compiler-First Paradigm Solidifying:** Svelte 5 (91% retention), Vue Vapor Mode (feature-complete beta), Solid.js all demonstrate build-time optimization > runtime flexibility trade-off succeeding.
3. **Developer Experience Renaissance:** Svelte 5 top satisfaction (State of JS 2025), Solid maintains 5-year high; DX becoming primary differentiator over bundle size.
4. **Islands + Resumability:** Astro/Qwik patterns now influencing React (Partial Pre-rendering). Zero-hydration becoming table stakes for SEO-critical apps.
5. **Server-Driven UI Gaining:** HTMX stabilizing; hypermedia patterns resurgent in monolithic backends (Rails, Django, Laravel) as SPA complexity backlash.
6. **Ecosystem Diversity:** React still dominates (86.9M downloads), but alternative frameworks (Svelte 2.06M, Solid 1.65M) showing real ecosystem traction, not just hype.
7. **Web Components Maturity:** Native component model gaining traction for design systems (Material Web, Lightning Web Components). Long-term standardization advantage.

---

## Ecosystem Maturity Matrix

| Category | React | Vue | Svelte | Angular | Solid.js | Qwik |
|----------|-------|-----|--------|---------|----------|------|
| **Routing** | ⭐⭐⭐ (Next, Remix) | ⭐⭐⭐ (Nuxt, Router) | ⭐⭐ (SvelteKit) | ⭐⭐⭐ (Built-in) | ⭐⭐ (SolidStart) | ⭐⭐⭐ (Qwik City) |
| **State Mgmt** | ⭐⭐⭐ (Redux, Zustand, Tanstack) | ⭐⭐⭐ (Pinia, Tanstack) | ⭐⭐ (Stores) | ⭐⭐ (NgRx, signals) | ⭐⭐ (Custom, emerging) | ⭐⭐ (Emerging) |
| **UI Libraries** | ⭐⭐⭐ (Material, Chakra, Ant) | ⭐⭐ (Vuetify, Element) | ⭐⭐ (SvelteUI, Skeleton) | ⭐⭐⭐ (Material, PrimeNG) | ⭐ (Emerging) | ⭐ (Minimal) |
| **Testing** | ⭐⭐⭐ (Vitest, Jest, RTL, Playwright) | ⭐⭐⭐ (Vitest, RTL) | ⭐⭐⭐ (Vitest, Testing Lib) | ⭐⭐⭐ (Jest, Karma, Cypress) | ⭐⭐ (Vitest) | ⭐⭐ (Emerging) |
| **Docs** | ⭐⭐⭐ (Excellent) | ⭐⭐⭐ (Excellent) | ⭐⭐⭐ (Excellent, Interactive) | ⭐⭐ (Dense, Learning curve) | ⭐⭐ (Good but emerging) | ⭐⭐ (Catching up) |
| **Community** | ⭐⭐⭐ (Massive) | ⭐⭐⭐ (Large) | ⭐⭐ (Growing) | ⭐⭐⭐ (Enterprise-focused) | ⭐⭐ (Niche) | ⭐⭐ (Niche, growing) |
| **Job Market** | ⭐⭐⭐ (Dominant) | ⭐⭐ (Growing) | ⭐ (Emerging) | ⭐⭐ (Enterprise) | ⚪ (Minimal) | ⚪ (Minimal) |

---

## Cost & Licensing

**All covered frameworks:** MIT or Apache 2.0 open-source. Zero licensing costs.

**Tooling costs vary:**
- React/Vue: Free (build tools), but Next.js/Nuxt hosting (Vercel/Netlify) has paid tiers
- Angular: Free (backed by Google)
- Solid.js: Free (community-driven)
- Qwik: Free (Builder.io investment, free hosting on Netlify)

---

## Source Registry

| Source | URL | Last Verified |
|--------|-----|----------------|
| React 19.2 Release | https://react.dev/blog/2025/10/01/react-19-2 | Mar 3, 2026 |
| React 19 Server Components | https://react.dev/reference/rsc/server-components | Mar 3, 2026 |
| Vue 3.6 Vapor Mode | https://vueschool.io/articles/news/vn-talk-evan-you-preview-of-vue-3-6-vapor-mode/ | Mar 3, 2026 |
| Vue Mastery Vapor | https://www.vuemastery.com/blog/the-future-of-vue-vapor-mode/ | Mar 3, 2026 |
| Svelte 5 Review | https://www.scalablepath.com/javascript/svelte-5-review | Mar 3, 2026 |
| Svelte 5 Runes & Reactivity | https://blog.logrocket.com/exploring-runes-svelte-5/ | Mar 3, 2026 |
| Angular Zoneless Docs | https://angular.dev/guide/zoneless | Mar 3, 2026 |
| Angular Signals v20 | https://www.kellton.com/kellton-tech-blog/angular-20-new-features-guide | Mar 3, 2026 |
| Solid.js Ecosystem | https://www.johal.in/solidstart-solidjs-full-stack-vite-powered-ssr-2026/ | Mar 3, 2026 |
| Qwik 1.18.0 Status | https://www.builder.io/blog/qwik-2-coming-soon | Mar 3, 2026 |
| Astro 5.0 Release | https://astro.build/blog/astro-5/ | Mar 3, 2026 |
| Astro v6 Beta | https://astro.build/blog/astro-6-beta/ | Mar 3, 2026 |
| HTMX GitHub & Adoption | https://github.com/bigskysoftware/htmx | Mar 3, 2026 |
| HTMX Renaissance 2026 | https://www.softwareseni.com/the-htmx-renaissance-rethinking-web-architecture-for-2026/ | Mar 3, 2026 |
| NPM Weekly Downloads | https://tanstack.com/stats/npm | Mar 3, 2026 |
| State of JS 2025 | https://2025.stateofjs.com/ | Mar 3, 2026 |
| State of JS Meta-Frameworks | https://2025.stateofjs.com/en-US/libraries/meta-frameworks/ | Mar 3, 2026 |
| State of JS Front-End Frameworks | https://2025.stateofjs.com/en-US/libraries/front-end-frameworks/ | Mar 3, 2026 |
| JS Framework Benchmark (Official) | https://github.com/krausest/js-framework-benchmark | Mar 3, 2026 |
| Preact compat | https://preactjs.com/guide/v10/differences-to-react/ | Mar 3, 2026 |
| Alpine.js | https://alpinejs.dev/ | Mar 3, 2026 |
| Lit Web Components | https://lit.dev/ | Mar 3, 2026 |
| Frontend Benchmarking 2025 | https://itnext.io/benchmarking-frontends-in-2025-f6bbf43b7721 | Mar 3, 2026 |

---

## Critical Contradictions Documented

1. **React Dominance Paradox:** React's largest ecosystem (86.9M weekly downloads) + slowest runtime performance (vs Svelte/Solid). Bundle size vs ecosystem trade-off still unresolved by team size; React continues gaining despite theoretical disadvantages.

2. **Benchmarks vs Real World:** Synthetic benchmarks favor Solid/Svelte (40-50% faster), but React's ecosystem and tooling often deliver faster time-to-market despite higher runtime cost. Ecosystem value > raw performance for most teams.

3. **Vapor Mode Promise:** Vue's claimed 88% bundle reduction feature-complete but unproven in production due to beta status (v3.6). Wait for v3.7+ (mid-2026) before production use; ecosystem compatibility still limited.

4. **Qwik Resumability Benefit:** Zero-hydration advantage real and verified (Builder.io 60% improvement), but only measurable on extremely large interactive apps. Marginal gains (<5%) for typical CRUD applications.

5. **HTMX Hype vs Usage:** 47.2K stars but <0.1% production usage; "hypermedia renaissance" claims vs reality of SPA dominance in user-facing apps. Gaining traction in internal tools, monolithic backends only.

6. **Solid Growth vs Maturity:** SolidJS ecosystem downloads jumped 33x (50K → 1.65M), yet hiring pool remains minimal. Adoption rapid but real production deployments still sparse outside specific use cases.

---

**Last Updated:** March 3, 2026
**Next Review:** May 2026 (post-Vue 3.7, Qwik 2.0, Astro 6.0 release, Angular 21 stable)

<!-- PRICING_STABILITY: STABLE | Updated: 2026-03-03 | Core technology patterns. Pricing largely free/open-source or stable. -->

---
## Related References
- [Meta-Frameworks](./02-frontend-meta-frameworks.md) — Next.js, Nuxt, SvelteKit, Astro comparison
- [CSS & UI Libraries](./03-css-ui-libraries.md) — Tailwind, shadcn/ui, component libraries
- [i18n & Internationalization](./54-i18n-internationalization.md) — next-intl, react-i18next, locale routing
- [Performance Benchmarks](./47-performance-benchmarks.md) — Framework bundle sizes, Lighthouse scores
