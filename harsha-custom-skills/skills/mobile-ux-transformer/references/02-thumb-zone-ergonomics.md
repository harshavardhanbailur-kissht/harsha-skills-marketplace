# Thumb Zone Ergonomics

> Research-backed guidelines for designing within comfortable reach

## The Science of Thumb Reach

### How Users Hold Their Phones

| Grip Style | Usage Percentage | Primary Interaction |
|------------|------------------|---------------------|
| One-handed (thumb) | 49% | Thumb only |
| Cradled | 36% | Index finger |
| Two-handed | 15% | Both thumbs |

**Key Insight:** Nearly half of all users operate their phones one-handed, making thumb reachability critical for primary interactions.

### Thumb Reach Anatomy

The thumb's natural arc creates distinct reachability zones:

```
┌─────────────────────────────────┐
│                                 │
│     STRETCH ZONE (18%)          │
│     Hard to reach               │
│     ⚠️ Risky for important      │
│        actions                  │
│                                 │
├─────────────────────────────────┤
│                                 │
│     REACH ZONE (33%)            │
│     Requires stretching         │
│     📋 Secondary content        │
│     🔧 Settings, options        │
│                                 │
├─────────────────────────────────┤
│                                 │
│     NATURAL ZONE (49%)          │
│     Easy thumb arc              │
│     ✅ Primary navigation       │
│     ✅ Main CTAs                │
│     ✅ Frequent actions         │
│                                 │
└─────────────────────────────────┘
```

### Zone Engagement Data

| Zone | Engagement Rate | Error Rate | Recommendation |
|------|----------------|------------|----------------|
| Natural | Baseline (100%) | Lowest | Primary actions |
| Reach | -28% engagement | +15% errors | Secondary actions |
| Stretch | -43% engagement | +32% errors | Rare/destructive only |

---

## Touch Target Specifications

### Platform Requirements Comparison

| Standard | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| Apple HIG | 44×44 pt | 48×48 pt | iOS points |
| Material Design 3 | 48×48 dp | 56×56 dp | Android dp |
| WCAG 2.2 AA | 24×24 CSS px | 44×44 CSS px | Accessibility minimum |
| WCAG 2.2 AAA | 44×44 CSS px | 48×48 CSS px | Enhanced accessibility |

### Converting Units

```css
/* iOS points to CSS pixels (standard displays) */
1 pt ≈ 1 CSS px

/* Android dp to CSS pixels (mdpi baseline) */
1 dp = 1 CSS px at 160dpi

/* Practical recommendation for web */
.touch-target {
  min-width: 44px;
  min-height: 44px;
}
```

### Touch Target Sizing by Position

| Screen Position | Minimum Target | Rationale |
|-----------------|---------------|-----------|
| Bottom center | 44×44 px | Easy natural zone reach |
| Bottom corners | 48×48 px | Edge of thumb arc |
| Middle screen | 44×44 px | Moderate reach |
| Top corners | 48×48 px | Stretch zone compensation |
| Near notch/dynamic island | 52×52 px | Avoid system gestures |

---

## Touch Target Spacing

### Minimum Spacing Requirements

| Standard | Minimum Spacing |
|----------|-----------------|
| Apple HIG | 8 pt between targets |
| Material Design 3 | 8 dp between targets |
| WCAG 2.2 | Target + spacing ≥ 24px |

### Spacing Implementation

```css
/* Button group with proper spacing */
.button-group {
  display: flex;
  gap: 8px; /* Minimum spacing */
}

.button-group .button {
  min-width: 44px;
  min-height: 44px;
  padding: 12px 16px;
}

/* List items with touch targets */
.list-item {
  min-height: 48px; /* Full row is target */
  padding: 12px 16px;
}

.list-item + .list-item {
  border-top: 1px solid var(--border);
  /* No additional spacing needed - row height provides it */
}
```

### Common Spacing Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Inline links too close | Accidental taps | Add padding or use buttons |
| Icon buttons touching | Miss-taps | Add 8px+ gap |
| List items too short | Hard to tap | Minimum 48px height |
| Form fields stacked tight | Input errors | 16px vertical gap |

---

## Handedness Considerations

### Right vs Left-Handed Users

| Population | Percentage | Implications |
|------------|------------|--------------|
| Right-handed | 90% | Default optimization |
| Left-handed | 10% | Consider mirrored layout |

### Right-Handed Thumb Zone (Portrait)

```
┌─────────────────────────────────┐
│  ❌ Hard    │    Moderate    │ ❌│
│  Stretch    │                │   │
├─────────────┼────────────────┼───┤
│             │    Easier      │ ⚠️│
│  Moderate   │                │   │
├─────────────┼────────────────┼───┤
│             │                │   │
│    Easy     │     BEST       │ ✅│
│             │    Natural     │   │
└─────────────┴────────────────┴───┘
   Left Edge      Center       Right
```

### Left-Handed Thumb Zone (Portrait)

```
┌─────────────────────────────────┐
│ ❌│    Moderate    │  Hard    ❌│
│   │                │  Stretch   │
├───┼────────────────┼────────────┤
│ ⚠️│    Easier      │            │
│   │                │  Moderate  │
├───┼────────────────┼────────────┤
│   │                │            │
│ ✅│     BEST       │    Easy    │
│   │    Natural     │            │
└───┴────────────────┴────────────┘
  Left       Center         Right
```

### Designing for Both Hands

1. **Center primary actions** to work for both hands
2. **Bottom navigation** accessible from either side
3. **Swipe actions** work in both directions
4. **Consider offering settings** to switch dominant hand

```css
/* Handedness-adaptive navigation */
.nav-primary-action {
  /* Center for universal access */
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
}

/* Or allow user preference */
.left-handed .nav-primary-action {
  left: 16px;
  transform: none;
}

.right-handed .nav-primary-action {
  left: auto;
  right: 16px;
  transform: none;
}
```

---

## Screen Size Considerations

### Modern Device Dimensions

| Device Category | Screen Height | Thumb Reach % |
|-----------------|--------------|---------------|
| Small (iPhone SE) | 667 pt | ~65% reachable |
| Standard (iPhone 14) | 844 pt | ~55% reachable |
| Large (iPhone 15 Pro Max) | 932 pt | ~45% reachable |
| Foldable (outer) | ~600 pt | ~70% reachable |
| Foldable (inner) | ~1000+ pt | ~40% reachable |

### Reachability Solutions for Large Screens

| Platform | Feature | How It Works |
|----------|---------|--------------|
| iOS | Reachability | Double-tap home area, screen slides down |
| Android | One Handed Mode | Swipe on gesture bar, UI shrinks |
| Samsung | One Hand Operation | Customizable gestures for navigation |

### Design Implications for Large Screens

```css
/* Adapt navigation height based on screen size */
.bottom-nav {
  height: 56px;
  padding-bottom: env(safe-area-inset-bottom);
}

/* On larger screens, increase target size */
@media (min-height: 800px) {
  .bottom-nav {
    height: 64px;
  }
  
  .nav-item {
    min-height: 56px;
  }
}

/* For very large screens, consider floating nav */
@media (min-height: 900px) {
  .bottom-nav {
    margin: 0 16px 16px;
    border-radius: 16px;
    left: 16px;
    right: 16px;
    width: auto;
  }
}
```

---

## Action Placement Strategy

### What Goes Where

| Zone | Action Types | Examples |
|------|-------------|----------|
| **Natural Zone** | Primary actions, Navigation, Frequent taps | Submit, Next, Tab bar, FAB |
| **Reach Zone** | Secondary actions, Content viewing | Settings, Filters, Scrollable content |
| **Stretch Zone** | Destructive actions, Rare operations | Delete, Close, Advanced settings |

### Strategic Placement Examples

#### E-commerce Product Page
```
┌─────────────────────────────────┐
│ [Back]              [Share][♥] │ ← Stretch (rare actions)
│                                 │
│        Product Image            │
│                                 │
│                                 │ ← Reach (content viewing)
│   Title                         │
│   Price                         │
│   Description...                │
│                                 │
├─────────────────────────────────┤
│ [Add to Cart]      [Buy Now]   │ ← Natural (primary CTAs)
└─────────────────────────────────┘
```

#### Social Feed
```
┌─────────────────────────────────┐
│ [Menu]      Title      [Search]│ ← Stretch
│                                 │
│   ┌─────────────────────────┐  │
│   │     Post Content        │  │
│   │                         │  │ ← Reach (scroll/read)
│   │                         │  │
│   │   [♥] [💬] [↗]         │  │ ← Lower reach (engagement)
│   └─────────────────────────┘  │
│                                 │
├─────────────────────────────────┤
│ [Home] [Search] [+] [Inbox] [Me]│ ← Natural (navigation)
└─────────────────────────────────┘
```

---

## Implementation Code Examples

### CSS Touch Target System

```css
/* Base touch target mixin */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Expanded touch target for small visual elements */
.touch-target-expanded {
  position: relative;
}

.touch-target-expanded::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 44px;
  height: 44px;
  /* Invisible but tappable */
}

/* Icon button with proper touch target */
.icon-button {
  width: 24px; /* Visual size */
  height: 24px;
  padding: 10px; /* Expands to 44px */
  margin: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.icon-button:active {
  opacity: 0.7;
}
```

### JavaScript Touch Target Validation

```javascript
/**
 * Validates touch targets meet minimum size requirements
 * @param {number} minSize - Minimum size in pixels (default 44)
 * @returns {Array} Elements failing validation
 */
function validateTouchTargets(minSize = 44) {
  const interactive = document.querySelectorAll(
    'a, button, input, select, textarea, [role="button"], [tabindex]'
  );
  
  const failures = [];
  
  interactive.forEach(el => {
    const rect = el.getBoundingClientRect();
    
    if (rect.width < minSize || rect.height < minSize) {
      failures.push({
        element: el,
        width: rect.width,
        height: rect.height,
        selector: getSelector(el)
      });
    }
  });
  
  return failures;
}

function getSelector(el) {
  if (el.id) return `#${el.id}`;
  if (el.className) return `.${el.className.split(' ')[0]}`;
  return el.tagName.toLowerCase();
}

// Usage in development
if (process.env.NODE_ENV === 'development') {
  const failures = validateTouchTargets();
  if (failures.length) {
    console.warn('Touch target issues:', failures);
  }
}
```

### React Touch Target Component

```jsx
// TouchTarget.jsx
import React from 'react';
import styles from './TouchTarget.module.css';

/**
 * Wrapper ensuring minimum touch target size
 */
export function TouchTarget({ 
  children, 
  as: Component = 'button',
  minSize = 44,
  ...props 
}) {
  return (
    <Component 
      className={styles.touchTarget}
      style={{ '--min-size': `${minSize}px` }}
      {...props}
    >
      {children}
    </Component>
  );
}

// TouchTarget.module.css
.touchTarget {
  min-width: var(--min-size, 44px);
  min-height: var(--min-size, 44px);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
```

---

## Testing Touch Targets

### Manual Testing Checklist

- [ ] All buttons/links meet 44×44px minimum
- [ ] Spacing between targets ≥8px
- [ ] Primary actions in natural zone (bottom 40%)
- [ ] Destructive actions in stretch zone (top)
- [ ] Touch targets work with screen magnification
- [ ] No overlapping touch targets

### Automated Testing

```javascript
// Cypress test for touch targets
describe('Touch Target Compliance', () => {
  it('all interactive elements meet minimum size', () => {
    cy.visit('/');
    
    cy.get('a, button, input, [role="button"]').each($el => {
      const { width, height } = $el[0].getBoundingClientRect();
      expect(width).to.be.at.least(44);
      expect(height).to.be.at.least(44);
    });
  });
});
```

### Chrome DevTools Testing

1. Open DevTools → More Tools → Rendering
2. Enable "Emulate CSS media feature prefers-reduced-motion"
3. Use Device Mode with touch simulation
4. Manually verify target sizes with element inspector

---

## Common Patterns & Solutions

### Problem: Inline Text Links Too Small

```html
<!-- ❌ Bad: Tiny touch target -->
<p>Read our <a href="/terms">terms</a> and <a href="/privacy">privacy policy</a>.</p>

<!-- ✅ Better: Expanded touch targets -->
<p>Read our <a href="/terms" class="inline-link">terms</a> and 
   <a href="/privacy" class="inline-link">privacy policy</a>.</p>

<style>
.inline-link {
  padding: 8px 4px;
  margin: -8px -4px;
  text-decoration: underline;
}
</style>
```

### Problem: Close Button in Corner

```html
<!-- ❌ Bad: Small X in tight corner -->
<button class="close">×</button>

<!-- ✅ Better: Properly sized with padding -->
<button class="close" aria-label="Close dialog">
  <svg width="20" height="20" aria-hidden="true">...</svg>
</button>

<style>
.close {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
}
</style>
```

---

## Key Takeaways

1. **49% use one hand** — Design for thumb reach
2. **Bottom 40% is natural zone** — Place primary actions there
3. **44×44px minimum** — Non-negotiable for touch targets
4. **8px spacing** — Prevent accidental taps
5. **Large screens need adaptation** — Consider floating/adaptive nav
6. **Test on real devices** — Simulators miss ergonomic issues
