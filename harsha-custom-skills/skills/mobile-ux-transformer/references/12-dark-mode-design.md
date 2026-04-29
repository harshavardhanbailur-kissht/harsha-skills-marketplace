# Dark Mode Design

> Implementation guide for light/dark theme systems

## Dark Mode Statistics

| Metric | Value |
|--------|-------|
| Users who enable dark mode | 82-91% |
| Users who prefer dark mode | 64% |
| OLED power savings | Up to 60% |
| Reduced eye strain reported | 73% |

---

## Design Principles

### 1. Avoid Pure Black

Pure black (#000000) creates harsh contrast and "halation" (text appears to glow).

```css
/* ❌ Avoid pure black */
.dark-mode {
  background: #000000;
  color: #ffffff;
}

/* ✅ Use near-black */
.dark-mode {
  background: #121212;
  color: #e0e0e0;
}

/* ✅ iOS-style dark */
.dark-mode {
  background: #1c1c1e;
  color: #ffffff;
}

/* ✅ Material dark */
.dark-mode {
  background: #121212;
  color: #e1e1e1;
}
```

### 2. Reduce Saturation

Bright saturated colors appear too vibrant on dark backgrounds.

```css
/* ❌ Full saturation on dark */
.dark-mode .primary {
  color: #007AFF; /* Too bright */
}

/* ✅ Reduced saturation */
.dark-mode .primary {
  color: #5AC8FA; /* Lighter, less saturated */
}
```

### 3. Maintain Hierarchy with Elevation

Dark mode uses surface elevation to show hierarchy.

```css
.dark-mode {
  --surface-0: #121212;  /* Base */
  --surface-1: #1e1e1e;  /* +1 elevation */
  --surface-2: #232323;  /* +2 elevation */
  --surface-3: #252525;  /* +3 elevation */
  --surface-4: #272727;  /* +4 elevation */
  --surface-8: #2d2d2d;  /* +8 elevation */
}
```

### 4. Use Semantic Color Tokens

```css
:root {
  /* Light mode */
  --color-background: #ffffff;
  --color-surface: #f5f5f5;
  --color-on-background: #1a1a1a;
  --color-on-surface: #333333;
  --color-primary: #007AFF;
  --color-error: #ff3b30;
}

@media (prefers-color-scheme: dark) {
  :root {
    /* Dark mode */
    --color-background: #121212;
    --color-surface: #1e1e1e;
    --color-on-background: #e0e0e0;
    --color-on-surface: #ffffff;
    --color-primary: #5AC8FA;
    --color-error: #ff6961;
  }
}
```

---

## Implementation Methods

### 1. CSS Media Query (System Preference)

```css
/* Light mode (default) */
:root {
  --bg: #ffffff;
  --text: #1a1a1a;
  --surface: #f5f5f5;
  --border: #e0e0e0;
}

/* Dark mode (system preference) */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121212;
    --text: #e0e0e0;
    --surface: #1e1e1e;
    --border: #333333;
  }
}

body {
  background-color: var(--bg);
  color: var(--text);
}
```

### 2. Class-Based Toggle (User Preference)

```html
<html data-theme="light">
```

```css
/* Light mode */
[data-theme="light"] {
  --bg: #ffffff;
  --text: #1a1a1a;
}

/* Dark mode */
[data-theme="dark"] {
  --bg: #121212;
  --text: #e0e0e0;
}

/* System default */
[data-theme="system"] {
  /* Use media query defaults */
}
```

```javascript
// Theme toggle
function setTheme(theme) {
  if (theme === 'system') {
    document.documentElement.removeAttribute('data-theme');
    localStorage.removeItem('theme');
  } else {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }
}

// On load: respect saved preference or system
function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
  }
}

// Listen for system changes
window.matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      // Only update if using system preference
      // CSS handles this automatically
    }
  });
```

### 3. Combined Approach (Best Practice)

```css
:root {
  /* Light mode defaults */
  --bg: #ffffff;
  --text: #1a1a1a;
  color-scheme: light dark; /* Hint to browser */
}

/* System preference dark */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #121212;
    --text: #e0e0e0;
  }
}

/* Explicit dark mode override */
[data-theme="dark"] {
  --bg: #121212;
  --text: #e0e0e0;
}

/* Explicit light mode override */
[data-theme="light"] {
  --bg: #ffffff;
  --text: #1a1a1a;
}
```

---

## Color Palette Examples

### iOS Dark Mode Colors

```css
.ios-dark {
  /* Backgrounds */
  --system-background: #000000;
  --secondary-background: #1c1c1e;
  --tertiary-background: #2c2c2e;
  --grouped-background: #000000;
  --secondary-grouped: #1c1c1e;
  
  /* Labels */
  --label: #ffffff;
  --secondary-label: rgba(235, 235, 245, 0.6);
  --tertiary-label: rgba(235, 235, 245, 0.3);
  --quaternary-label: rgba(235, 235, 245, 0.18);
  
  /* Fills */
  --primary-fill: rgba(120, 120, 128, 0.36);
  --secondary-fill: rgba(120, 120, 128, 0.32);
  --tertiary-fill: rgba(118, 118, 128, 0.24);
  --quaternary-fill: rgba(116, 116, 128, 0.18);
  
  /* Separator */
  --separator: rgba(84, 84, 88, 0.65);
  --opaque-separator: #38383a;
  
  /* System colors */
  --system-blue: #0a84ff;
  --system-green: #30d158;
  --system-red: #ff453a;
  --system-orange: #ff9f0a;
  --system-yellow: #ffd60a;
  --system-teal: #64d2ff;
  --system-purple: #bf5af2;
  --system-pink: #ff375f;
}
```

### Material Dark Mode Colors

```css
.material-dark {
  /* Surfaces */
  --surface: #121212;
  --surface-variant: #49454f;
  --on-surface: #e6e1e5;
  --on-surface-variant: #cac4d0;
  
  /* Primary */
  --primary: #d0bcff;
  --on-primary: #381e72;
  --primary-container: #4f378b;
  --on-primary-container: #eaddff;
  
  /* Secondary */
  --secondary: #ccc2dc;
  --on-secondary: #332d41;
  --secondary-container: #4a4458;
  --on-secondary-container: #e8def8;
  
  /* Tertiary */
  --tertiary: #efb8c8;
  --on-tertiary: #492532;
  --tertiary-container: #633b48;
  --on-tertiary-container: #ffd8e4;
  
  /* Error */
  --error: #f2b8b5;
  --on-error: #601410;
  --error-container: #8c1d18;
  --on-error-container: #f9dedc;
  
  /* Outline */
  --outline: #938f99;
  --outline-variant: #49454f;
}
```

---

## Image Handling

### Reducing Image Brightness

```css
/* Dim images in dark mode */
@media (prefers-color-scheme: dark) {
  img:not([src*=".svg"]) {
    filter: brightness(0.9);
  }
  
  img:hover {
    filter: brightness(1);
  }
}
```

### Dark Mode Specific Images

```html
<picture>
  <source srcset="image-dark.png" media="(prefers-color-scheme: dark)">
  <img src="image-light.png" alt="Description">
</picture>
```

### Logo Handling

```css
/* Invert logo for dark mode */
.logo {
  filter: none;
}

@media (prefers-color-scheme: dark) {
  .logo {
    filter: invert(1);
  }
}

/* Or use CSS to color SVG */
.logo svg {
  fill: var(--text-color);
}
```

---

## Shadows in Dark Mode

Shadows don't work well on dark backgrounds. Use elevation instead.

```css
/* Light mode: shadows */
.card {
  background: var(--surface);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Dark mode: elevation (lighter surface) */
@media (prefers-color-scheme: dark) {
  .card {
    background: var(--surface-1);
    box-shadow: none;
    /* Or subtle glow */
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.05);
  }
}
```

---

## Contrast Requirements

### WCAG Contrast Ratios

| Content | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Body text | 4.5:1 min | 4.5:1 min |
| Large text | 3:1 min | 3:1 min |
| UI components | 3:1 min | 3:1 min |

### Testing Contrast

```javascript
// Check contrast ratio
function getContrastRatio(fg, bg) {
  const l1 = getLuminance(fg);
  const l2 = getLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// Example: White text on #121212 = 15.3:1 ✅
// Example: #e0e0e0 on #121212 = 12.6:1 ✅
```

---

## Theme Toggle UI

```html
<div class="theme-toggle" role="group" aria-label="Theme selection">
  <button 
    class="theme-option" 
    data-theme="light"
    aria-pressed="false">
    <span class="icon">☀️</span>
    <span class="label">Light</span>
  </button>
  <button 
    class="theme-option" 
    data-theme="dark"
    aria-pressed="false">
    <span class="icon">🌙</span>
    <span class="label">Dark</span>
  </button>
  <button 
    class="theme-option active" 
    data-theme="system"
    aria-pressed="true">
    <span class="icon">🖥️</span>
    <span class="label">System</span>
  </button>
</div>
```

```css
.theme-toggle {
  display: flex;
  background: var(--surface);
  border-radius: 8px;
  padding: 4px;
  gap: 4px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
}

.theme-option.active,
.theme-option[aria-pressed="true"] {
  background: var(--primary);
  color: var(--on-primary);
}
```

---

## Testing Checklist

- [ ] All text meets contrast requirements
- [ ] Images aren't too bright
- [ ] Shadows replaced with elevation
- [ ] Brand colors adjusted for dark backgrounds
- [ ] Focus indicators visible
- [ ] Form inputs have clear borders
- [ ] Selection states are visible
- [ ] Works with system preference
- [ ] Manual toggle overrides system
- [ ] Preference persists across sessions
- [ ] Smooth transition between modes

---

## Key Takeaways

1. **Avoid pure black** — Use #121212 or #1c1c1e
2. **Reduce saturation** — Bright colors need adjustment
3. **Use elevation** — Instead of shadows
4. **Support system + manual toggle** — Three options: light, dark, system
5. **Test contrast** — 4.5:1 for text, 3:1 for UI
6. **Dim images** — Filter brightness in dark mode
