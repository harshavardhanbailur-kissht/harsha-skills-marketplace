# Mobile Typography

> Type systems optimized for small screens and touch interfaces

## Typography Fundamentals

### Minimum Sizes

| Element | Minimum | Recommended | Notes |
|---------|---------|-------------|-------|
| Body text | 16px | 17-18px | **Critical:** <16px triggers iOS zoom |
| Secondary text | 14px | 15px | Use sparingly |
| Captions | 12px | 13px | Labels, timestamps |
| Large titles | 28px | 34px | Screen headers |
| Buttons | 16px | 17px | Touch feedback area |

### Line Height (Leading)

| Content Type | Line Height | Ratio |
|-------------|-------------|-------|
| Body text | 24-28px | 1.4-1.6× |
| Headings | 1.1-1.3× | Tighter |
| UI labels | 1.2× | Compact |
| Buttons | 1.0-1.2× | Single line |

### Line Length (Measure)

| Device | Optimal Characters | Max Characters |
|--------|-------------------|----------------|
| Phone (portrait) | 30-40 | 50 |
| Phone (landscape) | 45-60 | 75 |
| Tablet | 50-75 | 90 |

---

## Platform Typography

### iOS Type Scale (SF Pro)

| Style | Size | Weight | Line Height |
|-------|------|--------|-------------|
| Large Title | 34pt | Bold | 41pt |
| Title 1 | 28pt | Regular | 34pt |
| Title 2 | 22pt | Regular | 28pt |
| Title 3 | 20pt | Regular | 25pt |
| Headline | 17pt | Semibold | 22pt |
| Body | 17pt | Regular | 22pt |
| Callout | 16pt | Regular | 21pt |
| Subhead | 15pt | Regular | 20pt |
| Footnote | 13pt | Regular | 18pt |
| Caption 1 | 12pt | Regular | 16pt |
| Caption 2 | 11pt | Regular | 13pt |

### Material Design Type Scale (Roboto)

| Style | Size | Weight | Line Height | Tracking |
|-------|------|--------|-------------|----------|
| Display Large | 57sp | Regular | 64sp | -0.25 |
| Display Medium | 45sp | Regular | 52sp | 0 |
| Display Small | 36sp | Regular | 44sp | 0 |
| Headline Large | 32sp | Regular | 40sp | 0 |
| Headline Medium | 28sp | Regular | 36sp | 0 |
| Headline Small | 24sp | Regular | 32sp | 0 |
| Title Large | 22sp | Regular | 28sp | 0 |
| Title Medium | 16sp | Medium | 24sp | 0.15 |
| Title Small | 14sp | Medium | 20sp | 0.1 |
| Body Large | 16sp | Regular | 24sp | 0.5 |
| Body Medium | 14sp | Regular | 20sp | 0.25 |
| Body Small | 12sp | Regular | 16sp | 0.4 |
| Label Large | 14sp | Medium | 20sp | 0.1 |
| Label Medium | 12sp | Medium | 16sp | 0.5 |
| Label Small | 11sp | Medium | 16sp | 0.5 |

---

## CSS Implementation

### System Font Stack

```css
:root {
  --font-system: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                  Oxygen-Sans, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, 
               Consolas, 'Liberation Mono', monospace;
}

body {
  font-family: var(--font-system);
  font-size: 16px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
```

### Fluid Typography

```css
/* Fluid type scale using clamp() */
:root {
  /* Body: 16px to 18px */
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  
  /* Small: 14px to 15px */
  --text-sm: clamp(0.875rem, 0.85rem + 0.125vw, 0.9375rem);
  
  /* Large: 18px to 20px */
  --text-lg: clamp(1.125rem, 1.05rem + 0.375vw, 1.25rem);
  
  /* H1: 28px to 34px */
  --text-h1: clamp(1.75rem, 1.5rem + 1.25vw, 2.125rem);
  
  /* H2: 22px to 28px */
  --text-h2: clamp(1.375rem, 1.2rem + 0.875vw, 1.75rem);
  
  /* H3: 18px to 22px */
  --text-h3: clamp(1.125rem, 1rem + 0.625vw, 1.375rem);
}

body { font-size: var(--text-base); }
h1 { font-size: var(--text-h1); }
h2 { font-size: var(--text-h2); }
h3 { font-size: var(--text-h3); }
```

### Prevent iOS Zoom on Inputs

```css
/* Critical: Inputs must be 16px to prevent iOS auto-zoom */
input, select, textarea {
  font-size: 16px;
  font-size: max(16px, 1rem);
}
```

---

## Dynamic Type Support

### iOS Dynamic Type

```swift
// Swift: Support Dynamic Type
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true

// Custom fonts with Dynamic Type
let customFont = UIFont(name: "CustomFont", size: 17)!
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)
label.adjustsFontForContentSizeCategory = true
```

### CSS for System Font Scaling

```css
/* Support user font size preference */
html {
  font-size: 100%; /* Respects browser/system setting */
}

/* Use rem for scalability */
body {
  font-size: 1rem; /* Scales with user preference */
}

/* Test with browser zoom 200% */
@media (min-resolution: 2dppx) {
  /* High DPI adjustments if needed */
}
```

---

## Text Truncation

### Single Line Truncation

```css
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

### Multi-Line Truncation (Line Clamp)

```css
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

### Responsive Truncation

```css
.card-title {
  /* 1 line on mobile, 2 on tablet */
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (min-width: 768px) {
  .card-title {
    -webkit-line-clamp: 2;
  }
}
```

---

## Web Font Optimization

### Font Display Strategy

```css
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2'),
       url('font.woff') format('woff');
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* Show fallback immediately, swap when loaded */
}

/* Alternatives:
   - font-display: optional;  // Use font only if cached (best for CLS)
   - font-display: fallback;  // Short block, then swap
   - font-display: block;     // Hide text until font loads
*/
```

### Preload Critical Fonts

```html
<head>
  <link rel="preload" href="font-regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="font-bold.woff2" as="font" type="font/woff2" crossorigin>
</head>
```

### Subset Fonts

```bash
# Using pyftsubset to create subset with only used characters
pyftsubset font.ttf \
  --output-file=font-subset.woff2 \
  --flavor=woff2 \
  --layout-features='kern,liga' \
  --unicodes="U+0000-00FF,U+0131,U+0152-0153"
```

---

## Readability Guidelines

### Contrast Ratios

| Text Type | Minimum Contrast |
|-----------|-----------------|
| Body text | 4.5:1 (WCAG AA) |
| Large text (18pt+) | 3:1 |
| Placeholder text | 4.5:1 (don't reduce) |

### Letter Spacing (Tracking)

```css
/* Headings: slightly tighter */
h1, h2, h3 {
  letter-spacing: -0.02em;
}

/* All caps: increase spacing */
.uppercase {
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Small text: increase spacing */
.caption {
  font-size: 12px;
  letter-spacing: 0.03em;
}
```

### Word Spacing

```css
/* Justified text needs word spacing control */
.justified {
  text-align: justify;
  word-spacing: 0.05em;
  hyphens: auto;
}
```

---

## Accessibility

### Screen Reader Considerations

```html
<!-- Abbreviations -->
<abbr title="Web Content Accessibility Guidelines">WCAG</abbr>

<!-- Numbers -->
<span aria-label="4 thousand 5 hundred">4.5K</span>

<!-- Icons with text -->
<span aria-hidden="true">⚠️</span>
<span>Warning message</span>
```

### Text Resize Testing

Test all content at:
- 100% (default)
- 150% 
- 200% (WCAG requirement)
- 400% (for low vision users)

---

## Quick Reference

### Do's

- ✅ Use 16px+ for body text
- ✅ Support Dynamic Type / user preferences
- ✅ Use system font stack for performance
- ✅ Preload critical web fonts
- ✅ Use `font-display: swap` or `optional`
- ✅ Test at 200% zoom

### Don'ts

- ❌ Use <16px for input fields
- ❌ Use fixed font sizes (px) for everything
- ❌ Load multiple font weights unnecessarily
- ❌ Rely only on font weight for hierarchy
- ❌ Use thin fonts on low-res screens
- ❌ Justify text without hyphens
