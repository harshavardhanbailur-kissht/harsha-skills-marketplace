# Component Patterns Reference

## Button Patterns

### Anatomy

```
┌─────────────────────────────────────┐
│  [icon]   Label Text   [icon]      │
│                                     │
│  └── padding: 12-16px vertical     │
│      padding: 16-24px horizontal   │
└─────────────────────────────────────┘
```

### Size Variants

| Size | Min Height | Padding (V/H) | Font Size | Touch Target |
|------|------------|---------------|-----------|--------------|
| xs   | 28px       | 4px / 8px     | 12px      | Not recommended |
| sm   | 32px       | 6px / 12px    | 14px      | 44×32px minimum |
| md   | 40px       | 8px / 16px    | 16px      | 44×40px ✓ |
| lg   | 48px       | 12px / 24px   | 18px      | 48×48px ✓ |
| xl   | 56px       | 16px / 32px   | 20px      | 56×56px ✓ |

### Visual Hierarchy

**Primary Button**
- Solid fill with brand color
- Highest contrast
- Use for main action
- **One per view/section**

```css
.btn-primary {
  background: var(--color-primary-500);
  color: white;
  font-weight: 600;
}
```

**Secondary Button**
- Outline or lower contrast fill
- For supporting actions
- Multiple allowed per view

```css
.btn-secondary {
  background: transparent;
  border: 2px solid var(--color-primary-500);
  color: var(--color-primary-500);
}
```

**Tertiary/Ghost Button**
- Text-only, minimal styling
- For low-priority actions
- Often used inline

```css
.btn-tertiary {
  background: transparent;
  color: var(--color-primary-500);
  text-decoration: underline;
}
```

**Destructive Button**
- Red color scheme
- For delete, remove, cancel actions
- Should require confirmation

```css
.btn-destructive {
  background: var(--color-error-500);
  color: white;
}
```

### State Styles

```css
/* Default */
.btn {
  background: var(--color-primary-500);
  transition: all 150ms ease-out;
}

/* Hover - Slightly darker/lighter */
.btn:hover {
  background: var(--color-primary-600);
}

/* Active/Pressed - Darkest, slight inset */
.btn:active {
  background: var(--color-primary-700);
  transform: translateY(1px);
}

/* Focus - Visible ring for keyboard navigation */
.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-200);
}

/* Disabled - Reduced opacity */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

/* Loading - Show spinner, disable interaction */
.btn--loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}
.btn--loading::after {
  content: '';
  position: absolute;
  /* spinner styles */
}
```

### Placement Guidelines

- Primary action on **right** (Western reading direction)
- Destructive actions **away** from primary
- Group related actions together
- Submit buttons **close to last form field**
- Mobile: Consider thumb reach zones

---

## Form Patterns

### Input Anatomy

```
Label * (required indicator)
┌────────────────────────────────────────┐
│ Placeholder text                       │
└────────────────────────────────────────┘
Helper text or character count

Error state:
Label *
┌────────────────────────────────────────┐ ← Red border
│ Invalid input                          │
└────────────────────────────────────────┘
⚠️ Specific error message with icon
```

### Input Sizing

| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| sm   | 36px   | 8px 12px | 14px |
| md   | 44px   | 10px 14px | 16px |
| lg   | 52px   | 12px 16px | 18px |

**Note:** 44px minimum for touch targets. 16px minimum font to prevent iOS zoom.

### Input States

```css
/* Default */
.input {
  height: 44px;
  padding: 10px 14px;
  border: 1px solid var(--color-neutral-300);
  border-radius: 6px;
  font-size: 16px;
  transition: all 150ms ease-out;
}

/* Hover */
.input:hover {
  border-color: var(--color-neutral-400);
}

/* Focus */
.input:focus {
  outline: none;
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

/* Error */
.input--error {
  border-color: var(--color-error-500);
}
.input--error:focus {
  box-shadow: 0 0 0 3px var(--color-error-100);
}

/* Success */
.input--success {
  border-color: var(--color-success-500);
}

/* Disabled */
.input:disabled {
  background: var(--color-neutral-100);
  cursor: not-allowed;
  opacity: 0.7;
}
```

### Label Patterns

**Top-aligned (Recommended)**
```
Label
┌──────────────┐
│ Input        │
└──────────────┘
```
- Fastest completion time
- Works for all field widths
- Best for long or complex labels

**Left-aligned**
```
Label   ┌──────────────┐
        │ Input        │
        └──────────────┘
```
- Slower completion
- Good for short, consistent labels
- Compact vertical space

**Floating Label**
```
┌──────────────────────┐
│ Label (small, top)   │
│ Input value          │
└──────────────────────┘
```
- Space-efficient
- Potential accessibility issues
- Requires animation

### Validation Patterns

**Inline Validation (Recommended)**
- Validate on blur (when user leaves field)
- Don't validate during typing (annoying)
- Show success for correct input
- 22% higher success rates than submit-only

**Error Message Requirements:**
- Specific (what went wrong)
- Actionable (how to fix)
- Positioned near the field
- Include icon (not just color)
- Persist until fixed

```
Email address
┌────────────────────────────────────────┐
│ user@invalid                           │
└────────────────────────────────────────┘
⚠️ Please enter a valid email address (e.g., name@example.com)
```

### Form Layout Rules

1. **Single column** — Always (multi-column confuses reading order)
2. **Logical grouping** — Related fields together
3. **Progressive complexity** — Easy fields first (name, email)
4. **Clear sections** — Visual breaks between groups
5. **Visible labels** — Never placeholder-only
6. **Smart defaults** — Pre-fill when possible

---

## Card Patterns

### Anatomy

```
┌────────────────────────────────────────┐
│ ┌────────────────────────────────────┐ │
│ │          Image/Media               │ │
│ │          (optional)                │ │
│ └────────────────────────────────────┘ │
│                                        │
│  Eyebrow/Category                      │
│  Card Title                            │
│  Subtitle or metadata                  │
│                                        │
│  Body content goes here with          │
│  supporting description text that     │
│  can span multiple lines...           │
│                                        │
│  ┌────────────┐  ┌────────────┐       │
│  │  Primary   │  │ Secondary  │       │
│  └────────────┘  └────────────┘       │
└────────────────────────────────────────┘
```

### Standard Styles

```css
.card {
  background: white;
  border-radius: 8px; /* 4-16px range */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 16px; /* 16-24px */
  transition: all 200ms ease-out;
}

/* Clickable card */
.card--clickable {
  cursor: pointer;
}

.card--clickable:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card--clickable:active {
  transform: translateY(0);
}

/* Card sections */
.card__image {
  margin: -16px -16px 16px;
  border-radius: 8px 8px 0 0;
}

.card__eyebrow {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary-500);
  margin-bottom: 4px;
}

.card__title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.card__subtitle {
  font-size: 14px;
  color: var(--color-neutral-500);
  margin-bottom: 12px;
}

.card__body {
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-neutral-700);
}

.card__actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-neutral-200);
}
```

### Card Variants

**Basic Card** — Content container with shadow
**Interactive Card** — Clickable, hover states
**Media Card** — Image + content
**Horizontal Card** — Side-by-side layout
**Stat Card** — Large number + label
**Profile Card** — Avatar + user info

---

## Navigation Patterns

### Desktop Header

```
┌─────────────────────────────────────────────────────────────┐
│ [Logo]      Nav 1    Nav 2    Nav 3    Nav 4       [CTA]   │
└─────────────────────────────────────────────────────────────┘
```

**Specifications:**
- Height: 60-80px
- Logo: Links to home
- Nav items: 5-7 max
- Gap between items: 24-32px
- Primary CTA: Right side
- Sticky: Consider for long pages

```css
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.nav {
  display: flex;
  gap: 32px;
}

.nav__link {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-neutral-700);
  text-decoration: none;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all 150ms ease-out;
}

.nav__link:hover,
.nav__link--active {
  color: var(--color-primary-500);
  border-bottom-color: var(--color-primary-500);
}
```

### Mobile Navigation

**Hamburger Menu**
```
┌────────────────────────────────┐
│ [Logo]                    [☰] │  ← Hamburger trigger
└────────────────────────────────┘

Expanded:
┌────────────────────────────────┐
│ [Logo]                    [×] │
├────────────────────────────────┤
│  Home                         │
│  Products                     │
│  About                        │
│  Contact                      │
│                               │
│  ┌──────────────────────────┐ │
│  │       Get Started        │ │
│  └──────────────────────────┘ │
└────────────────────────────────┘
```

**Bottom Tab Bar** (Recommended for apps)
```
┌────────────────────────────────────┐
│  🏠       🔍       ➕       👤     │
│ Home   Search    Add    Profile   │
└────────────────────────────────────┘
```

**Tab Bar Specifications:**
- Max 5 items
- Icon + label (not icon-only)
- Touch targets: 44×44px minimum
- Active state: Color change + label
- Height: 49-56px

---

## Modal/Dialog Patterns

### Anatomy

```
┌─────────────────────────────────────────┐
│ Modal Title                        [×]  │
├─────────────────────────────────────────┤
│                                         │
│  Modal content goes here. This can      │
│  include forms, text, images, or        │
│  any other content type.                │
│                                         │
├─────────────────────────────────────────┤
│                   [Cancel]  [Confirm]   │
└─────────────────────────────────────────┘
```

### Specifications

- **Width:** 400-500px (simple), 600-800px (complex)
- **Max height:** 90vh with scroll
- **Backdrop:** rgba(0, 0, 0, 0.5)
- **Border radius:** 8-12px
- **Padding:** 24px

### Behavior Requirements

- **Focus trap:** Tab cycles within modal
- **ESC to close:** Always
- **Click outside:** Optional (not for destructive actions)
- **Primary action:** Right side
- **Scroll:** Internal, not page
- **Animation:** Fade + scale (200-300ms)

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modal-enter 200ms ease-out;
}

@keyframes modal-enter {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-neutral-200);
}

.modal__body {
  padding: 24px;
  overflow-y: auto;
}

.modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-neutral-200);
}
```

---

## Loading States

### Skeleton Screens (Preferred for Content)

```
┌────────────────────────────────────────┐
│ ████████████████                       │  ← Title
│ ██████████                             │  ← Subtitle
│                                        │
│ ████████████████████████████████████   │  ← Body
│ ██████████████████████████             │
│ ████████████████████████████████       │
│                                        │
│ ┌──────────┐  ┌──────────┐             │  ← Buttons
│ │▓▓▓▓▓▓▓▓▓▓│  │▓▓▓▓▓▓▓▓▓▓│             │
│ └──────────┘  └──────────┘             │
└────────────────────────────────────────┘
```

**Best Practices:**
- Match approximate content dimensions
- Use subtle animation (pulse or shimmer)
- Show immediately (no delay)
- Better than spinners for content loading

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-neutral-200) 25%,
    var(--color-neutral-100) 50%,
    var(--color-neutral-200) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Spinner (For Actions)

**Use For:**
- Button loading states
- Form submissions
- Short operations

**Specifications:**
- Size: Match context (16px inline, 24px button, 48px page)
- Duration: Continuous rotation
- Minimum display: 500ms (prevent flash)
- Include text when possible

### Progress Bar (For Known Duration)

**Use For:**
- File uploads
- Multi-step processes
- Known-length operations

```css
.progress {
  height: 8px;
  background: var(--color-neutral-200);
  border-radius: 4px;
  overflow: hidden;
}

.progress__bar {
  height: 100%;
  background: var(--color-primary-500);
  transition: width 300ms ease-out;
}
```

---

## Toast/Notification Patterns

### Types

| Type | Color | Auto-dismiss | Icon |
|------|-------|--------------|------|
| Success | Green | 3-5s | ✓ Checkmark |
| Info | Blue | 5s | ℹ️ Info |
| Warning | Yellow/Orange | Persist | ⚠️ Warning |
| Error | Red | Persist | ✕ Error |

### Anatomy

```
┌─────────────────────────────────────────────┐
│ ✓  Action completed successfully       [×]  │
└─────────────────────────────────────────────┘
```

### Position

- **Desktop:** Top-right or bottom-right
- **Mobile:** Top or bottom, full-width
- **Stack:** New toasts push others (max 3-5 visible)

```css
.toast-container {
  position: fixed;
  top: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 9999;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: toast-enter 200ms ease-out;
}

.toast--success { border-left: 4px solid var(--color-success-500); }
.toast--error { border-left: 4px solid var(--color-error-500); }
.toast--warning { border-left: 4px solid var(--color-warning-500); }
.toast--info { border-left: 4px solid var(--color-info-500); }

@keyframes toast-enter {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```
