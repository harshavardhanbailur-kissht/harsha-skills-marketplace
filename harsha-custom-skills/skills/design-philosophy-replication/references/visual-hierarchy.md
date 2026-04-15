# Visual Hierarchy & Color Psychology Reference

## Visual Hierarchy Principles

Visual hierarchy guides users through content by controlling where eyes move. Research shows users form impressions in **50 milliseconds**—hierarchy must be immediately apparent.

### The Four Pillars of Visual Hierarchy

### 1. Size

Larger elements signal higher importance. Our eyes are naturally drawn to bigger objects first.

**Implementation:**
- Primary CTAs: 1.5-2× larger than secondary elements
- Headlines: Noticeably bigger than body text (1.5-2× minimum)
- Important icons: Larger than decorative ones
- Hero sections: Use large imagery to capture attention
- Data visualization: Size encodes importance

**Ratio Guidelines:**
- H1 to body: 2.5-3× larger
- H2 to body: 2× larger
- H3 to body: 1.5× larger
- Primary button to secondary: 1.25× larger

### 2. Color and Contrast

High-contrast elements attract attention first. Strategic use of color creates emphasis.

**The 60-30-10 Rule:**
- **60% Dominant** — Neutral colors (backgrounds, large surfaces)
- **30% Secondary** — Supporting brand colors
- **10% Accent** — CTAs, highlights, key actions

**Contrast Applications:**
- Primary buttons: Highest contrast color pairing
- Important text: Dark on light (or vice versa)
- Links: Distinguishable from body text
- Alerts: High-contrast backgrounds (red/yellow/green)
- Focus indicators: High visibility rings

**Strategic Color Use:**
- Reserve your strongest color for the most important action
- Use muted colors for secondary elements
- Gray out disabled/inactive elements
- Ensure sufficient contrast for readability

### 3. Position and Placement

Users scan in predictable patterns. Leverage these patterns for hierarchy.

**F-Pattern (Text-Heavy Pages)**
```
████████████████████████████
████████████████████
█████████████
████████████████████████
█████████████████
██████████████████████
```
- Users scan horizontally across the top
- Then move down the left side
- Occasionally scanning right

**Use For:** Articles, blogs, documentation, search results

**Z-Pattern (Sparse/Landing Pages)**
```
1 ─────────────────────────→ 2
                              │
                              │
                              ↓
4 ←─────────────────────────── 3
```
- Top-left to top-right
- Diagonal to bottom-left
- Bottom-left to bottom-right

**Use For:** Landing pages, hero sections, simple layouts

**Gutenberg Diagram**
```
┌─────────────────────────────┐
│ Primary          Strong     │
│ Optical Area     Fallow     │
│                             │
│ Weak             Terminal   │
│ Fallow           Area       │
└─────────────────────────────┘
```
- Primary optical area (top-left): Logo, main headline
- Terminal area (bottom-right): CTAs

### 4. Whitespace (Negative Space)

Elements with more surrounding space receive more attention. Whitespace is not empty—it's a design tool.

**Applications:**
- Generous padding around primary CTAs (2-3× normal padding)
- Increased margins around important content
- Line spacing (leading) affects readability: 1.4-1.6× for body
- Letter spacing for headlines
- Section spacing to create visual chapters

**Whitespace Benefits:**
- Increases comprehension by 20%
- Creates visual breathing room
- Signals importance through isolation
- Improves scannability
- Reduces cognitive load

---

## Typography for Visual Hierarchy

### Type Scale

**Common Ratios:**

| Name | Ratio | Use Case |
|------|-------|----------|
| Minor Second | 1.067 | Minimal variation |
| Major Second | 1.125 | Subtle hierarchy |
| Minor Third | 1.2 | Moderate contrast |
| Major Third | 1.25 | Clear hierarchy |
| Perfect Fourth | 1.333 | Strong contrast |
| Augmented Fourth | 1.414 | Bold hierarchy |
| Perfect Fifth | 1.5 | Dramatic |
| Golden Ratio | 1.618 | Very dramatic |

**Standard Type Scale (1.25 ratio):**
```
72px — Display
48px — H1
36px — H2
28px — H3
22px — H4
18px — H5
16px — Body
14px — Small
12px — Caption
```

### Readability Standards

**Body Text:**
- Size: 16-20px (16px minimum)
- Line length: 45-75 characters (66 ideal)
- Line height: 1.4-1.6 (1.5 recommended)
- Letter spacing: Normal or slightly increased

**Headings:**
- Line height: 1.1-1.3 (tighter than body)
- Letter spacing: Can be slightly negative for large sizes
- Weight: 600-700 for emphasis

**Small Text:**
- Size: 12-14px
- Line height: 1.5-1.7 (looser than body)
- Use sparingly (captions, metadata)

### Font Pairing

**Contrast Principle:** Pair fonts that are different enough to create interest but similar enough to be harmonious.

**Safe Pairings:**
- Serif heading + Sans-serif body
- Geometric sans + Humanist sans
- Display font + Neutral body font

**Font Pairing Rules:**
1. Maximum 3 typefaces (heading, body, UI/accent)
2. Maintain mood alignment
3. Ensure x-height compatibility
4. Test at all sizes
5. Consider loading performance

**Recommended Screen Fonts:**
- Sans-serif: Inter, Roboto, Open Sans, Source Sans Pro, SF Pro
- Serif: Georgia, Merriweather, Lora, Source Serif Pro
- Monospace: SF Mono, JetBrains Mono, Fira Code

---

## Color Psychology in Design

### Color Associations

**Blue**
- Trust, security, professionalism, calm
- **Use for:** Finance, healthcare, corporate, technology
- **Examples:** Banks, LinkedIn, IBM, Healthcare apps
- **Caution:** Can feel cold or impersonal

**Green**
- Success, safety, growth, nature, money
- **Use for:** Confirmations, positive actions, environmental, finance
- **Examples:** Success messages, proceed buttons, eco-brands
- **Caution:** Many shades have different associations

**Red**
- Urgency, danger, passion, importance, errors
- **Use for:** Alerts, warnings, sale banners, errors, stop actions
- **Examples:** Error states, clearance sales, emergency
- **Caution:** Use sparingly—creates anxiety

**Orange**
- Energy, enthusiasm, warmth, creativity
- **Use for:** Secondary CTAs, highlights, youth-oriented
- **Examples:** Call-to-action (alternative to red), creative tools
- **Caution:** Can feel cheap if overused

**Yellow**
- Optimism, caution, warmth, attention
- **Use for:** Warnings (with dark text), highlights, cheerful brands
- **Examples:** Warning messages, sticky notes, featured content
- **Caution:** Hard to read, needs high contrast

**Purple**
- Creativity, luxury, wisdom, mystery
- **Use for:** Premium brands, creative products, spirituality
- **Examples:** Luxury goods, creative tools, wellness
- **Caution:** Can feel juvenile in bright shades

**Black**
- Sophistication, elegance, power, formality
- **Use for:** Luxury brands, fashion, high-end products
- **Examples:** Premium tiers, fashion brands
- **Caution:** Can feel heavy if overused

**White**
- Cleanliness, simplicity, space, purity
- **Use for:** Backgrounds, negative space, minimalist design
- **Examples:** Apple, healthcare, modern design
- **Caution:** Needs sufficient content contrast

### Color Accessibility

**Never Rely on Color Alone**
- 8% of men and 0.5% of women are colorblind
- Pair color with icons, text labels, or patterns
- Test with colorblindness simulators

**Contrast Ratios (WCAG):**

| Element | AA Standard | AAA Standard |
|---------|-------------|--------------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18px+) | 3:1 | 4.5:1 |
| UI components | 3:1 | Not defined |

**Tools for Testing:**
- WebAIM Contrast Checker
- Stark (Figma plugin)
- Chrome DevTools accessibility audit

### Building Color Palettes

**From Extraction:**
1. Identify primary brand color
2. Generate semantic colors (success, error, warning, info)
3. Create neutral scale (50-900)
4. Define surface colors
5. Establish text colors for each surface

**Color Palette Structure:**
```
Primary:    50, 100, 200, 300, 400, 500, 600, 700, 800, 900
Secondary:  50, 100, 200, 300, 400, 500, 600, 700, 800, 900
Neutral:    50, 100, 200, 300, 400, 500, 600, 700, 800, 900

Semantic:
- Success: green-500 (with 50, 100, 900 variants)
- Error: red-500 (with 50, 100, 900 variants)
- Warning: yellow-500 (with 50, 100, 900 variants)
- Info: blue-500 (with 50, 100, 900 variants)
```

---

## Applying Hierarchy in Practice

### Landing Page Hierarchy

```
1. Logo (brand anchor, top-left)
   ↓
2. Headline (largest text, above fold)
   ↓
3. Subheadline (supporting message)
   ↓
4. Primary CTA (high contrast, prominent)
   ↓
5. Hero image/video (visual anchor)
   ↓
6. Secondary content (features, benefits)
   ↓
7. Social proof (testimonials, logos)
   ↓
8. Secondary CTA (reinforcement)
   ↓
9. Footer (navigation, legal)
```

### Dashboard Hierarchy

```
1. Navigation (persistent, subdued)
2. Page title (context)
3. Key metrics (large numbers, prominent)
4. Primary action (contextual)
5. Data visualizations (supporting)
6. Detailed tables (scannable)
7. Filters/controls (accessible but not dominant)
```

### Form Hierarchy

```
1. Form title (purpose)
2. Section headers (grouping)
3. Labels (clear, visible)
4. Input fields (consistent sizing)
5. Helper text (subdued)
6. Error messages (high contrast when present)
7. Primary submit (prominent)
8. Secondary actions (subdued)
```

---

## Common Hierarchy Mistakes

**Competing Elements**
- Multiple elements fighting for attention
- Fix: Establish clear primary, secondary, tertiary levels

**Everything is Bold**
- When everything is emphasized, nothing is
- Fix: Be selective with emphasis

**No Visual Entry Point**
- Users don't know where to start
- Fix: Create an obvious focal point

**Inconsistent Styling**
- Similar elements styled differently
- Fix: Establish and follow component patterns

**Poor Contrast**
- Important elements don't stand out
- Fix: Increase contrast for key elements

**Cluttered Layout**
- Too much competing for attention
- Fix: Add whitespace, remove unnecessary elements
