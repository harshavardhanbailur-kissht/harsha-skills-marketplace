---
name: design-philosophy-replication
description: "Analyze any website URL to extract its complete design DNA (colors, typography, spacing, components, layout, motion), replicate the design accurately, and evolve it using research-backed UI/UX principles from Nielsen Norman Group, Material Design, Apple HIG, Baymard Institute, Stanford d.school, and academic sources. Use when: (1) User provides a website URL to replicate or analyze, (2) User wants to copy or mimic a website's design philosophy, (3) User asks to improve an existing design using UX principles, (4) User needs design tokens extracted from a site, (5) User wants to create a project with similar design philosophy to a reference site, (6) User asks about UI/UX best practices or design system principles. Outputs clean, maintainable code in any framework (React, Vue, HTML/CSS, Tailwind, etc.)."
---
# Design Philosophy Replication & Evolution

This skill enables extraction, replication, and intelligent improvement of any website's design system using research-backed principles from academic institutions and industry leaders.

## Core Workflow: Analyze → Extract → Replicate → Evolve

### Phase 1: Analyze (Extract Design DNA)

When given a website URL, use `web_fetch` to retrieve the page, then systematically extract six interconnected layers. See `references/extraction-techniques.md` for complete JavaScript code snippets.

**Layer 1: Color System**
Extract from CSS custom properties (`--color-*`, `--bg-*`, `--text-*`) and computed styles for `background-color`, `color`, `border-color`, `fill`, `stroke`. Identify hierarchy by context:
- Brand colors → logos, primary buttons
- Semantic colors → success/error/warning states
- Neutral colors → backgrounds, text
Score by usage frequency — high-confidence colors appear on interactive elements.

**Layer 2: Typography Scale**
Capture `font-family` stacks, `font-size` values, `font-weight`, `line-height`, `letter-spacing`. Detect modular scale ratios:
- **1.25 (Major Third)** — moderate contrast
- **1.333 (Perfect Fourth)** — clear hierarchy
- **1.618 (Golden Ratio)** — dramatic distinction

Standard tokens: 12/14/16/18/20/24/30/36/48/60/72px

**Layer 3: Spacing System**
Detect base unit by analyzing margin/padding/gap frequency:
- **4px base**: 4, 8, 12, 16, 20, 24, 32, 40, 48
- **8px base**: 8, 16, 24, 32, 40, 48, 64

**Layer 4: Layout Patterns**
Identify grid systems (`display: grid/flex`), breakpoints, container max-widths. Common patterns:
- 12-column grids
- Tailwind breakpoints: 640/768/1024/1280/1536px
- Bootstrap breakpoints: 576/768/992/1200/1400px

**Layer 5: Component Patterns**
Catalog cards, buttons, forms, navigation. See `references/component-patterns.md` for detailed specifications.

**Layer 6: Motion & Interactions**
Extract transitions, timing functions, durations:
- **150ms** — micro-interactions (hover)
- **300ms** — standard transitions
- **500ms** — complex animations
- Easing: `ease-out` (entering), `ease-in` (exiting), `ease-in-out` (state changes)

### Phase 2: Extract (Generate Design Tokens)

Output structured token system:

```json
{
  "colors": {
    "primary": { "500": "#3b82f6", "600": "#2563eb", "700": "#1d4ed8" },
    "neutral": { "50": "#f9fafb", "100": "#f3f4f6", "900": "#111827" },
    "semantic": { "success": "#10b981", "error": "#ef4444", "warning": "#f59e0b" }
  },
  "typography": {
    "fontFamily": { "sans": "Inter, system-ui, sans-serif", "serif": "Georgia, serif" },
    "fontSize": { "xs": "0.75rem", "sm": "0.875rem", "base": "1rem", "lg": "1.125rem", "xl": "1.25rem", "2xl": "1.5rem", "3xl": "1.875rem", "4xl": "2.25rem" },
    "fontWeight": { "normal": "400", "medium": "500", "semibold": "600", "bold": "700" },
    "lineHeight": { "tight": "1.25", "normal": "1.5", "relaxed": "1.625" }
  },
  "spacing": { "1": "0.25rem", "2": "0.5rem", "3": "0.75rem", "4": "1rem", "6": "1.5rem", "8": "2rem", "12": "3rem", "16": "4rem" },
  "radius": { "sm": "0.25rem", "md": "0.5rem", "lg": "0.75rem", "xl": "1rem", "full": "9999px" },
  "shadow": { "sm": "0 1px 2px rgba(0,0,0,0.05)", "md": "0 4px 6px rgba(0,0,0,0.1)", "lg": "0 10px 15px rgba(0,0,0,0.1)" },
  "duration": { "fast": "150ms", "normal": "300ms", "slow": "500ms" },
  "easing": { "default": "cubic-bezier(0.4, 0, 0.2, 1)", "in": "cubic-bezier(0.4, 0, 1, 1)", "out": "cubic-bezier(0, 0, 0.2, 1)" }
}
```

### Phase 3: Replicate

Generate code matching extracted design system in user's requested framework. See `references/code-output-patterns.md` for framework-specific templates.

### Phase 4: Evolve (Apply Research-Backed Improvements)

Apply improvements while preserving design identity. Reference files contain comprehensive guidance:

- `references/ux-principles.md` — Nielsen's 10 heuristics, Fitts's Law, Hick's Law, Miller's Law, Jakob's Law, cognitive load reduction
- `references/design-philosophies.md` — Dieter Rams' 10 principles, Apple HIG, Material Design, Fluent, Carbon
- `references/visual-hierarchy.md` — Size, color, position, whitespace, typography, color psychology
- `references/component-patterns.md` — Buttons, forms, cards, navigation, modals, loading states
- `references/extraction-techniques.md` — JavaScript code for extracting design tokens
- `references/code-output-patterns.md` — React/Tailwind, Vue, Plain CSS templates
- `references/evolution-framework.md` — Audit methodology, prioritization, A/B testing, conventions vs innovation

## Quick Reference: Critical Standards

**Touch Targets**: Minimum 44×44px (recommended 48×48px)
**Body Typography**: 16-20px, 45-75 char line length (66 ideal), 1.5× line-height
**Color Contrast**: Minimum 4.5:1 for text
**Button Hierarchy**: One primary per view, solid fill for primary, outline for secondary
**Form Validation**: Inline after blur (22% higher success rate), specific actionable messages
**Visual Hierarchy**: 60-30-10 color rule (dominant/secondary/accent)
**Motion**: Under 500ms, meaningful not decorative, respect reduced-motion preferences

## Quality Checklist

Before delivering any implementation:

- [ ] Primary action immediately obvious
- [ ] Touch targets ≥44px
- [ ] Body text ≥16px, line length 45-75 chars, line height 1.4-1.6
- [ ] All interactive elements have visible hover/focus/active states
- [ ] Focus states visible for keyboard navigation
- [ ] Consistent spacing scale throughout
- [ ] Color contrast ≥4.5:1 for text
- [ ] Labels visible (not placeholder-only)
- [ ] Error messages specific and actionable
- [ ] Animations under 500ms
- [ ] No new elements obscuring existing functionality
