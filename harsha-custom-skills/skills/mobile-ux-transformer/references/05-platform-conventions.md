# Platform Conventions

> iOS and Android design differences and implementation guidelines

## Platform Market Overview

| Region | iOS Share | Android Share |
|--------|----------|--------------|
| Global | ~28% | ~71% |
| USA | ~57% | ~42% |
| UK | ~52% | ~47% |
| India | ~4% | ~95% |
| Japan | ~66% | ~33% |
| Brazil | ~15% | ~84% |

**Key Insight:** Platform distribution varies significantly by region. Consider your target audience when deciding platform priorities.

---

## Visual Design Differences

### Typography

| Element | iOS (SF Pro) | Android (Roboto) |
|---------|-------------|------------------|
| Large Title | 34pt Bold | 32sp Regular |
| Title 1 | 28pt Regular | 24sp Medium |
| Title 2 | 22pt Regular | 20sp Medium |
| Title 3 | 20pt Semibold | 16sp Medium |
| Headline | 17pt Semibold | 16sp Medium |
| Body | 17pt Regular | 16sp Regular |
| Caption | 12pt Regular | 12sp Regular |

### CSS Typography Implementation

```css
/* System font stack for platform matching */
body {
  font-family: 
    -apple-system,           /* iOS/macOS */
    BlinkMacSystemFont,      /* Chrome on macOS */
    'Segoe UI',              /* Windows */
    Roboto,                  /* Android/Chrome OS */
    Oxygen-Sans, Ubuntu,     /* Linux */
    'Helvetica Neue',        /* Fallback */
    sans-serif;
}

/* Platform-specific adjustments */
.ios body {
  font-size: 17px;
  line-height: 1.35;
  -webkit-font-smoothing: antialiased;
}

.android body {
  font-size: 16px;
  line-height: 1.5;
}
```

### Color Systems

| Concept | iOS | Android (Material 3) |
|---------|-----|---------------------|
| Primary brand | Tint color | Primary color |
| Backgrounds | System background | Surface colors |
| Adaptive colors | Dynamic (light/dark) | Dynamic Color from wallpaper |
| Accent | System blue default | Secondary color |
| Error | System red | Error color |

### iOS Semantic Colors

```css
:root {
  /* iOS Light Mode */
  --ios-label: #000000;
  --ios-secondary-label: #3c3c4399;
  --ios-tertiary-label: #3c3c434c;
  --ios-system-background: #ffffff;
  --ios-secondary-background: #f2f2f7;
  --ios-grouped-background: #f2f2f7;
  --ios-separator: #3c3c4349;
  --ios-blue: #007aff;
  --ios-red: #ff3b30;
  --ios-green: #34c759;
}

@media (prefers-color-scheme: dark) {
  :root {
    /* iOS Dark Mode */
    --ios-label: #ffffff;
    --ios-secondary-label: #ebebf599;
    --ios-tertiary-label: #ebebf54c;
    --ios-system-background: #000000;
    --ios-secondary-background: #1c1c1e;
    --ios-grouped-background: #000000;
    --ios-separator: #38383a;
  }
}
```

### Material 3 Color Tokens

```css
:root {
  /* Material 3 Light Mode */
  --md-primary: #6750a4;
  --md-on-primary: #ffffff;
  --md-primary-container: #eaddff;
  --md-surface: #fffbfe;
  --md-surface-variant: #e7e0ec;
  --md-on-surface: #1c1b1f;
  --md-outline: #79747e;
  --md-error: #b3261e;
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Material 3 Dark Mode */
    --md-primary: #d0bcff;
    --md-on-primary: #381e72;
    --md-primary-container: #4f378b;
    --md-surface: #1c1b1f;
    --md-surface-variant: #49454f;
    --md-on-surface: #e6e1e5;
    --md-outline: #938f99;
    --md-error: #f2b8b5;
  }
}
```

---

## Navigation Patterns

### iOS Navigation

| Pattern | Usage | Implementation |
|---------|-------|----------------|
| Tab Bar | Primary navigation (3-5 items) | Fixed at bottom |
| Navigation Bar | Screen title, back, actions | Fixed at top |
| Back | Edge swipe or top-left button | System-provided |
| Modal | Temporary tasks | Slide up, swipe down to dismiss |

### Android Navigation

| Pattern | Usage | Implementation |
|---------|-------|----------------|
| Bottom Navigation | Primary navigation (3-5 items) | Fixed at bottom |
| Navigation Drawer | Many destinations | Hamburger menu |
| Top App Bar | Title, navigation, actions | Fixed at top |
| Back | System back button/gesture | Hardware/gesture |
| Predictive Back | Preview destination | Android 13+ |

### Navigation Code Comparison

```html
<!-- iOS-style Navigation Bar -->
<header class="ios-nav-bar">
  <button class="back-button">
    <svg><!-- Chevron --></svg>
    <span>Back</span>
  </button>
  <h1 class="nav-title">Page Title</h1>
  <button class="action-button">Edit</button>
</header>

<!-- Android-style Top App Bar -->
<header class="md-top-app-bar">
  <button class="nav-button" aria-label="Menu">
    <svg><!-- Hamburger or back arrow --></svg>
  </button>
  <h1 class="headline">Page Title</h1>
  <button class="action-button" aria-label="Search">
    <svg><!-- Search icon --></svg>
  </button>
  <button class="action-button" aria-label="More">
    <svg><!-- More icon --></svg>
  </button>
</header>
```

```css
/* iOS Navigation Bar */
.ios-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 44px;
  padding: 0 16px;
  padding-top: env(safe-area-inset-top);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 0.5px solid var(--ios-separator);
}

.ios-nav-bar .nav-title {
  font-size: 17px;
  font-weight: 600;
  text-align: center;
}

.ios-nav-bar .back-button {
  display: flex;
  align-items: center;
  color: var(--ios-blue);
  font-size: 17px;
}

/* Material Top App Bar */
.md-top-app-bar {
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 4px;
  padding-top: env(safe-area-inset-top);
  background: var(--md-surface);
}

.md-top-app-bar .headline {
  flex: 1;
  font-size: 22px;
  font-weight: 400;
  margin-left: 16px;
}

.md-top-app-bar .nav-button,
.md-top-app-bar .action-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}
```

---

## Component Differences

### Buttons

| Aspect | iOS | Android (Material 3) |
|--------|-----|---------------------|
| Corner radius | 8-12pt (rounded rect) | 20dp (stadium shape) |
| Height | 44pt minimum | 40dp minimum |
| Text | Semibold | Medium |
| States | Highlighted (darker) | Ripple effect |

### Switches

| Aspect | iOS | Android |
|--------|-----|---------|
| Shape | Rounded capsule | Rounded with thumb |
| Label | No built-in label | Can include label |
| Size | Fixed (51×31 pt) | Variable |
| Animation | Slide | Slide with ripple |

```html
<!-- iOS Toggle -->
<label class="ios-switch">
  <input type="checkbox">
  <span class="switch-track"></span>
</label>

<!-- Material Switch -->
<label class="md-switch">
  <input type="checkbox">
  <span class="switch-track">
    <span class="switch-thumb"></span>
  </span>
</label>
```

### Dialogs/Alerts

| Aspect | iOS | Android |
|--------|-----|---------|
| Position | Center | Center |
| Width | Fixed width | Varies (280-560dp) |
| Corner radius | 14pt | 28dp |
| Buttons | Stacked (2) or side-by-side | Side-by-side |
| Destructive action | Red, left position | Text, right position |

```html
<!-- iOS Alert -->
<div class="ios-alert">
  <h2 class="alert-title">Delete Item?</h2>
  <p class="alert-message">This action cannot be undone.</p>
  <div class="alert-actions">
    <button class="alert-button cancel">Cancel</button>
    <button class="alert-button destructive">Delete</button>
  </div>
</div>

<!-- Material Dialog -->
<div class="md-dialog">
  <h2 class="dialog-headline">Delete item?</h2>
  <p class="dialog-supporting">This action cannot be undone.</p>
  <div class="dialog-actions">
    <button class="md-text-button">Cancel</button>
    <button class="md-text-button">Delete</button>
  </div>
</div>
```

---

## Safe Areas & Notches

### iOS Safe Areas

```css
/* Full safe area handling */
.container {
  padding-top: env(safe-area-inset-top);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
}

/* Fixed elements need safe areas */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding-bottom: env(safe-area-inset-bottom);
}

.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding-top: env(safe-area-inset-top);
}

/* Viewport meta tag */
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

### Android Display Cutouts

```css
/* Android cutout handling */
@supports (padding-top: env(safe-area-inset-top)) {
  .header {
    padding-top: env(safe-area-inset-top);
  }
}

/* Fallback for older Android */
.header {
  padding-top: 24px; /* Status bar height */
}

@media (min-height: 700px) {
  .header {
    padding-top: max(24px, env(safe-area-inset-top, 0px));
  }
}
```

---

## iOS 26 Liquid Glass Design

### Key Characteristics

- **Translucent surfaces** with frosted glass effect
- **Dynamic lighting** that responds to content
- **Layered depth** with subtle shadows
- **Fluid animations** between states
- **Transparent app icons** with depth

### Implementation

```css
/* Liquid Glass effect */
.glass-surface {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  box-shadow: 
    0 4px 30px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

@media (prefers-color-scheme: dark) {
  .glass-surface {
    background: rgba(40, 40, 40, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 
      0 4px 30px rgba(0, 0, 0, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
  }
}
```

---

## Material Design 3 Expressive

### Key Characteristics (2025)

- **Bolder colors** and dynamic theming
- **More expressive typography**
- **Spring-based animations** (bouncy, lively)
- **Enhanced personalization** via Dynamic Color
- **Gen Z appeal** (87% prefer expressive UI)

### Implementation

```css
/* Material 3 Expressive motion */
.md-expressive-button {
  transition: 
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.3s ease;
}

.md-expressive-button:active {
  transform: scale(0.95);
}

/* Dynamic elevation */
.md-card {
  --elevation: 1;
  box-shadow: 0 calc(var(--elevation) * 1px) calc(var(--elevation) * 3px) rgba(0,0,0,0.12);
  transition: --elevation 0.3s ease;
}

.md-card:hover {
  --elevation: 4;
}
```

---

## Platform Detection

### JavaScript Detection

```javascript
// Platform detection utility
const Platform = {
  isIOS: () => /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream,
  isAndroid: () => /Android/.test(navigator.userAgent),
  isMobile: () => /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
  
  // More specific detection
  isIPad: () => /iPad/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1),
  isIPhone: () => /iPhone/.test(navigator.userAgent),
  
  // OS version (iOS)
  getIOSVersion: () => {
    const match = navigator.userAgent.match(/OS (\d+)_(\d+)_?(\d+)?/);
    return match ? parseInt(match[1], 10) : null;
  },
  
  // OS version (Android)
  getAndroidVersion: () => {
    const match = navigator.userAgent.match(/Android (\d+)\.?(\d+)?/);
    return match ? parseFloat(match[1]) : null;
  }
};

// Apply platform class
document.documentElement.classList.add(
  Platform.isIOS() ? 'platform-ios' : 'platform-android'
);
```

### CSS Platform Targeting

```css
/* iOS-specific styles */
.platform-ios .button {
  border-radius: 12px;
  font-weight: 600;
}

.platform-ios .nav-title {
  text-align: center;
}

/* Android-specific styles */
.platform-android .button {
  border-radius: 20px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.platform-android .nav-title {
  text-align: left;
}
```

---

## Quick Reference: Key Differences

| Element | iOS | Android |
|---------|-----|---------|
| **Font** | SF Pro | Roboto |
| **Body text** | 17pt | 16dp |
| **Button radius** | 8-12pt | 20dp |
| **Touch target** | 44×44pt | 48×48dp |
| **Primary color** | System Blue (#007AFF) | Brand primary |
| **Back navigation** | Edge swipe + top-left | System back |
| **Tab bar position** | Bottom | Bottom (preferred) |
| **Action placement** | Top-right | FAB or top-right |
| **Pull to refresh** | Native spinner | Material indicator |
| **Haptics** | Taptic Engine | Variable |
| **Share** | Share sheet | Share intent |

---

## Best Practices

1. **Respect platform conventions** — Users expect familiar patterns
2. **Don't mix metaphors** — Avoid Android widgets on iOS and vice versa
3. **Test on both platforms** — Behavior differs in subtle ways
4. **Support both light/dark** — Platform default is respected
5. **Handle safe areas** — Different notch/cutout positions
6. **Match system fonts** — Feel native to each platform
7. **Use platform gestures** — Edge swipe behaviors differ
