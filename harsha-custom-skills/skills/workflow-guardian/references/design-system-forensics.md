# Design System Forensics Reference Guide

**For: Workflow Guardian Skill**
**Purpose:** Extract, document, and enforce design consistency across web applications
**Status:** Comprehensive reference for CSS/design system analysis

---

## Table of Contents

1. [Design Token Extraction Protocol](#design-token-extraction-protocol)
2. [Pattern Library Extraction](#pattern-library-extraction)
3. [Consistency Audit Checklist](#consistency-audit-checklist)
4. [Real Examples from Both Projects](#real-examples-from-both-projects)
5. [The "Blessed Patterns" System](#the-blessed-patterns-system)
6. [CSS Architecture Detection](#css-architecture-detection)
7. [Tailwind-Specific Forensics](#tailwind-specific-forensics)

---

## Design Token Extraction Protocol

This protocol extracts EVERY design token from an existing codebase systematically. Apply this when onboarding with a new project.

### 1. Color Palette Extraction

#### Step 1.1: Extract from Tailwind Config
Check `tailwind.config.js` or `tailwind.config.ts` for color definitions in the `theme.extend.colors` object.

**Example from Project 1 (issue-tracker):**
```javascript
// /sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/tailwind.config.js
colors: {
  ring: {
    50: '#e8ecfd',
    100: '#d4d9f7',
    200: '#a9b3ef',
    300: '#7a88e5',
    400: '#4a5bd9',
    500: '#2a3dc9',
    600: '#1e2fb3',
    700: '#13239c',  // Brand Primary
    800: '#111f7d',
    900: '#0e1a6b',
  },
  gold: {
    50: '#faf8f3',
    100: '#f5f0e3',
    200: '#e8dfc5',
    // ... (omitted for brevity)
    500: '#857037',  // Brand Gold
  },
}
```

**Extraction Checklist:**
- [ ] Read the entire `colors` object
- [ ] Note brand colors (usually at 500/700 levels)
- [ ] Identify semantic colors (primary, secondary, accent, danger, warning, success)
- [ ] Check for custom shades (colors with unusual suffixes)
- [ ] Record RGB/HSL alternatives if used

**Project 1 Color Palette:**
| Token | Value | Usage |
|-------|-------|-------|
| ring-700 | #13239c | Primary brand color (buttons, links) |
| ring-50 to ring-900 | Full scale | All ring-color variants |
| gold-500 | #857037 | Accent/special highlighting |

#### Step 1.2: Extract from CSS Custom Properties (CSS Variables)
Check `index.css` for `:root` CSS variables that define the design system.

**Example from Project 2 (los-issue-tracker):**
```css
/* /sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/index.css */
:root {
  /* Primary - Professional Navy */
  --color-primary-50: #eff2ff;
  --color-primary-100: #e0e7ff;
  --color-primary-200: #c7d2fe;
  --color-primary-300: #a5b4fc;
  --color-primary-400: #7886f7;
  --color-primary-500: #13239c;  /* Main brand color from Pay with Ring */
  --color-primary-600: #0f1c7a;
  --color-primary-700: #0c1660;
  --color-primary-800: #09114d;
  --color-primary-900: #060b3a;

  /* Semantic Surface Colors */
  --color-surface: #ffffff;
  --color-surface-secondary: var(--color-neutral-50);
  --color-border: var(--color-neutral-200);
  --color-text-primary: var(--color-neutral-900);

  /* Status Colors */
  --color-status-open: var(--color-warning-500);
  --color-status-claimed: var(--color-primary-500);
  --color-status-resolved: var(--color-success-500);

  /* Issue Type Colors */
  --color-issue-pan: #dc2626;
  --color-issue-pan-bg: #fef2f2;
  --color-issue-swapping: #ea580c;
  --color-issue-swapping-bg: #fff7ed;
  /* ... 10+ more issue type colors ... */
}
```

**Extraction Checklist:**
- [ ] Find all CSS variables in `:root`
- [ ] Categorize by type (primary, secondary, status, issue types)
- [ ] Note semantic vs. direct color assignments
- [ ] Check for color pairs (foreground + background)
- [ ] Record if variables reference other variables (composition)

**Project 2 Color Organization:**
- Primary (10-level scale): `--color-primary-50` through `--color-primary-900`
- Accent (10-level scale): `--color-accent-50` through `--color-accent-900`
- Secondary (10-level scale)
- Success, Warning, Danger colors
- Issue-specific colors (pan, swapping, wrong, system, link, old, bt, other)
- Semantic colors (surface, border, text hierarchy)

#### Step 1.3: Extract from Component Usage
Scan component files for hardcoded color classNames to catch any colors NOT in config.

**Search Strategy:**
```bash
grep -r "bg-\|text-\|border-\|ring-" src/components --include="*.tsx" | grep -v "node_modules"
```

**Example Findings from Project 1:**
- All components use Tailwind utility classes: `bg-ring-700`, `text-gray-600`, `bg-green-100`
- No arbitrary color values found (good practice)
- All colors map to tailwind config

**Extraction Result:**
Create a color palette reference document:
```
# Color Palette Reference

## Brand Colors (Primary)
- ring-700: #13239c (Primary action color)
- ring-50 to ring-900: Full tonal scale for variations

## Semantic Colors
- Gray scale: gray-50 to gray-900
- Success: green-100, green-500, green-800
- Warning/Danger: red-*, amber-*

## Status-Specific Colors (Project 2 only)
- Open: warning colors (amber)
- Claimed: primary colors (navy)
- Resolved: success colors (green)

## Issue Type Colors (Project 2 only)
- PAN Issue: red (#dc2626)
- System Issue: purple (#9333ea)
- Link Expired: blue (#2563eb)
- ... (8+ more types with specific colors)
```

### 2. Typography Scale Extraction

#### Step 2.1: Extract Font Families
Check Tailwind config and CSS for font definitions.

**Project 1 (issue-tracker):**
```javascript
// tailwind.config.js
fontFamily: {
  sans: ['Manrope', 'system-ui', '-apple-system', 'sans-serif'],
  mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
}
```

**Project 2 (los-issue-tracker):**
```css
/* index.css */
--font-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
--font-display: 'Manrope', 'Inter', sans-serif;  /* For hero sections */
--font-mono: ui-monospace, 'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace;
```

**Font Stack Analysis:**
| Font | Usage | Project 1 | Project 2 |
|------|-------|----------|----------|
| Manrope | Primary sans-serif | Yes | Display (secondary) |
| Inter | Not primary | No | Primary sans-serif |
| System fonts | Fallback | Yes | Yes |
| JetBrains Mono / SF Mono | Monospace | Yes | Yes |

#### Step 2.2: Extract Font Sizes
Record all font size tokens from config.

**Project 1:** Uses Tailwind defaults (no custom fontSize in config shown)

**Project 2 (Extended):**
```css
/* CSS Variables with 1.333 Perfect Fourth ratio */
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.333rem;     /* 21px - H5 */
--text-2xl: 1.777rem;    /* 28px - H4 */
--text-3xl: 2.369rem;    /* 38px - H3 */
--text-4xl: 3.157rem;    /* 51px - H2 */
--text-5xl: 4.209rem;    /* 67px - H1/Display */
```

**Extraction Result:**
```
# Typography Scale

## Font Families
Primary (Body): Manrope (Project 1) or Inter (Project 2)
Monospace: JetBrains Mono (Project 1) or SF Mono (Project 2)

## Font Sizes
xs: 12px  (metadata, captions)
sm: 14px  (secondary text, labels)
base: 16px (body text, default)
lg: 18px  (emphasized body)
xl: 21px  (small headings - H5)
2xl: 28px (H4)
3xl: 38px (H3)
4xl: 51px (H2)
5xl: 67px (H1/Display)

## Font Weights
light: 300
normal: 400
medium: 500
semibold: 600
bold: 700
extrabold: 800
```

#### Step 2.3: Extract Line Heights
Check for custom line height tokens.

**Project 2:**
```css
--leading-tight: 1.25;      /* Headings */
--leading-snug: 1.375;      /* Subheadings */
--leading-normal: 1.5;      /* Body text */
--leading-relaxed: 1.625;   /* Long-form content */
--leading-loose: 1.75;      /* Captions */
```

**Extraction Checklist:**
- [ ] Find all line height definitions
- [ ] Map to font sizes (tight for headings, normal/relaxed for body)
- [ ] Check if Tailwind fontSize config includes line heights

### 3. Spacing Scale Extraction

#### Step 3.1: Base Spacing Unit
Identify the base spacing unit (usually 4px, 8px, or 16px).

**Project 1:** Uses standard Tailwind (4px base)
- px-3 = 12px (3 × 4)
- px-4 = 16px (4 × 4)
- px-5 = 20px (5 × 4)

**Project 2:** Uses custom CSS variable scale based on 8px
```css
--space-0: 0;
--space-0-5: 0.125rem;    /* 2px */
--space-1: 0.25rem;       /* 4px */
--space-1-5: 0.375rem;    /* 6px */
--space-2: 0.5rem;        /* 8px */
--space-3: 0.75rem;       /* 12px */
--space-4: 1rem;          /* 16px */
--space-5: 1.25rem;       /* 20px */
--space-6: 1.5rem;        /* 24px */
--space-8: 2rem;          /* 32px */
--space-10: 2.5rem;       /* 40px */
--space-12: 3rem;         /* 48px */
--space-16: 4rem;         /* 64px */
--space-20: 5rem;         /* 80px */
```

#### Step 3.2: Extract Common Spacing Patterns
Scan components for padding/margin patterns.

**Project 1 Component (Button):**
```tsx
// Base button: h-11 px-5
// sm variant: h-9 px-3
// lg variant: h-12 px-6
```

**Project 1 Component (Card):**
```tsx
// Card: shadow-card (no custom padding defined in CSS)
```

**Project 1 Component (Input):**
```tsx
// Input: h-11 px-3
// Label: mb-1.5
// Error message: mt-1.5
```

**Project 2 Component (Input):**
```tsx
// Input: px-3 py-2.5
// Container: space-y-1.5
// Hint: text-sm (no padding utilities)
```

**Extraction Result:**
```
# Spacing System

## Base Unit: 4px (Tailwind) and 8px (CSS variables in Project 2)

## Common Padding Patterns
Buttons:
  - Small: h-9 px-3 (36px height, 12px horizontal)
  - Medium: h-11 px-5 (44px height, 20px horizontal)
  - Large: h-12 px-6 (48px height, 24px horizontal)

Cards/Containers:
  - p-4 (16px all sides)
  - p-3 (12px all sides)

Inputs:
  - h-11 px-3 (44px height, 12px horizontal)
  - py-2.5 px-3 (10px vertical, 12px horizontal in Project 2)

## Common Margin Patterns
Spacing between elements:
  - mb-2 (8px)
  - mb-3 (12px)
  - mb-4 (16px)
  - mt-1.5, mb-1.5 (6px for labels/error text)
```

### 4. Border & Radius Extraction

#### Step 4.1: Extract Border Radius Values

**Project 1:**
```javascript
borderRadius: {
  '4xl': '2rem',
}
// (Uses Tailwind defaults: rounded, rounded-md, rounded-lg, etc.)
```

**Project 2:**
```css
--radius-xs: 0.25rem;   /* 4px */
--radius-sm: 0.375rem;  /* 6px */
--radius-md: 0.5rem;    /* 8px - cards */
--radius-lg: 0.75rem;   /* 12px - larger cards */
--radius-xl: 1rem;      /* 16px - modals */
--radius-2xl: 1.5rem;   /* 24px - hero sections */
--radius-3xl: 2rem;     /* 32px - premium elements */
--radius-full: 9999px;  /* Pills, circular elements */
```

#### Step 4.2: Extract Border Styles from Components

**Project 1 Component Usage:**
```tsx
// Cards: rounded-lg border border-gray-200
// Inputs: rounded-md border border-gray-300
// Buttons: rounded-md
```

**Project 2 Component Usage:**
```tsx
// Cards: rounded-lg shadow
// Inputs: rounded-lg border
// Badges: rounded-md or rounded-full
```

**Extraction Result:**
```
# Border & Radius System

## Border Radius Scales
xs: 4px    (small components)
sm: 6px    (slight rounding)
md: 8px    (cards, default)
lg: 12px   (larger cards, containers)
xl: 16px   (modals, dialogs)
2xl: 24px  (hero sections)
3xl: 32px  (premium/special elements)
full: 50%  (pills, badges, circles)

## Border Widths
1px: Standard border (default)
2px: Focus rings

## Border Color Patterns
Default: border-gray-200 or border-neutral-300
Strong: border-gray-300 or border-neutral-300
Focus/error: border-{color}-500

## Component-Specific Border Patterns
Cards: 1px solid border-gray-200
Inputs: 1px solid border-gray-300 (error: border-red-500)
Buttons: No border (except secondary which uses border-ring-300)
Focus: 2px ring outline with ring-offset-2
```

### 5. Shadow Extraction

#### Step 5.1: Extract Shadow Definitions

**Project 1:**
```javascript
boxShadow: {
  'sm': '0 1px 2px rgba(0,0,0,0.05)',
  'md': '0 2px 4px rgba(0,0,0,0.08)',
  'lg': '0 4px 8px rgba(0,0,0,0.10)',
  'card': '0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)',
}
```

**Project 2:**
```css
--shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.03);
--shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.05), 0 1px 2px -1px rgb(0 0 0 / 0.05);
--shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.06);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.08), 0 8px 10px -6px rgb(0 0 0 / 0.06);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.15);

/* Colored shadows */
--shadow-primary: 0 10px 30px -5px rgba(19, 35, 156, 0.15);
--shadow-accent: 0 10px 30px -5px rgba(254, 206, 50, 0.20);
--shadow-success: 0 10px 30px -5px rgba(94, 184, 109, 0.15);
```

**Extraction Result:**
```
# Shadow System

## Elevation Levels
xs: Minimal elevation (1px)
sm: Subtle shadow
md: Standard card shadow
lg: Higher elevation
xl: Prominent elements
2xl: Maximum elevation

## Colored Shadows (Project 2)
Primary: Navy shadow (brand color)
Accent: Yellow/gold shadow
Success: Green shadow
(Used for premium/highlighted elements)

## Component Shadow Usage
Cards: shadow-md or shadow
Buttons: None (except hover states may add shadow)
Modals: shadow-xl or shadow-2xl
Hover states: shadow-md (upgrade from shadow-sm)
```

### 6. Animation & Transition Extraction

#### Step 6.1: Extract Durations and Timing Functions

**Project 1:**
```javascript
animation: {
  'shimmer': 'shimmer 1.5s infinite',
  'spin-slow': 'spin 2s linear infinite',
}
```

**Project 2:**
```css
--duration-instant: 75ms;
--duration-fast: 150ms;
--duration-normal: 300ms;   /* Pay with Ring standard */
--duration-slow: 500ms;
--duration-slower: 800ms;

--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
--ease-smooth: cubic-bezier(0.45, 0, 0.15, 1);
```

#### Step 6.2: Extract Keyframes

**Project 1:**
```css
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

**Project 2:**
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(254, 206, 50, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(254, 206, 50, 0);
  }
}
```

**Extraction Result:**
```
# Animation System

## Duration Scales
instant: 75ms    (immediately visible)
fast: 150ms      (snappy interactions)
normal: 300ms    (standard transitions)
slow: 500ms      (deliberate animations)
slower: 800ms    (entrance animations)

## Timing Functions
in-out: cubic-bezier(0.4, 0, 0.2, 1) - Default easing
out: cubic-bezier(0, 0, 0.2, 1) - Exit/dismiss animations
in: cubic-bezier(0.4, 0, 1, 1) - Entrance animations
bounce: cubic-bezier(0.34, 1.56, 0.64, 1) - Playful animations
smooth: cubic-bezier(0.45, 0, 0.15, 1) - Natural/smooth

## Keyframe Animations
shimmer: Loading skeleton animation
fadeInUp: Enter from bottom with fade
slideInRight: Slide in from left with fade
scaleIn: Scale from 0.95 to 1 with fade
pulse-glow: Pulsing glow effect (accent color)
pulse-subtle: Opacity pulse (0.7 to 1)

## Usage Patterns
Page transitions: fadeInUp
Modal/drawer entrance: slideInRight
Scale-based elements: scaleIn
Loading placeholders: shimmer
Attention-grabbing: pulse-glow (gold color in Project 2)
```

### 7. Breakpoint Extraction

#### Step 7.1: Extract Responsive Breakpoints

Both projects use default Tailwind breakpoints (no custom breakpoints found):
```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

#### Step 7.2: Scan Components for Responsive Usage

**Project 1 (Layout):**
```tsx
// max-w-7xl mx-auto - container constraint
// px-4 sm:px-6 lg:px-8 - responsive padding
// flex items-center h-14 - standard height
```

**Project 2 (TicketCard):**
```tsx
// flex flex-wrap items-center gap-2 - responsive wrapping
// overflow-x-auto - horizontal scroll on mobile
// max-w-4xl max-h-full - modal size constraints
```

**Extraction Result:**
```
# Responsive Breakpoints

## Tailwind Breakpoints (Default)
sm: 640px    (landscape phones)
md: 768px    (tablets)
lg: 1024px   (small laptops)
xl: 1280px   (laptops)
2xl: 1536px  (desktops)

## Common Responsive Patterns
Padding: px-4 sm:px-6 lg:px-8
Container: max-w-7xl mx-auto
Typography: text-base lg:text-lg
Display: block md:inline-block
Layout: flex flex-col md:flex-row

## Container Query Approach
max-w-7xl: Standard max width for content
mx-auto: Center content
px-4 (mobile) / px-6-8 (desktop)
```

---

## Pattern Library Extraction

This section documents how to identify and extract reusable component patterns from the codebase.

### 1. Button Patterns

#### Project 1 Button Component

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/components/ui/Button.tsx`

```typescript
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;          // 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: ButtonSize;                 // 'sm' | 'md' | 'lg'
  isLoading?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: 'bg-ring-700 text-white font-semibold hover:bg-ring-800 focus:ring-ring-500',
  secondary: 'bg-white text-ring-700 border border-ring-300 hover:bg-ring-50 focus:ring-ring-500',
  ghost: 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:ring-gray-400',
  destructive: 'bg-red-600 text-white font-semibold hover:bg-red-700 focus:ring-red-500',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-11 px-5 text-base',
  lg: 'h-12 px-6 text-base',
};
```

**Project 1 Button Usage in Real Components:**
```tsx
// From Layout.tsx
<button className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors">
  Logout
</button>

// Using Button component
<Button variant="primary" size="md">Click me</Button>
<Button variant="secondary" size="sm">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive" isLoading>Deleting...</Button>
```

#### Project 2 Button Component

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/ui/Button.tsx`

```typescript
interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  variant?: ButtonVariant;          // 'primary' | 'secondary' | 'ghost' | 'danger' | 'success'
  size?: ButtonSize;                 // 'sm' | 'md' | 'lg'
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  children: ReactNode;
  fullWidth?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: `
    bg-[#0f1c7a] text-white
    hover:bg-[#0c1660]
    focus-visible:ring-[#13239c]/50
    disabled:bg-[#7886f7]
  `,
  secondary: `
    bg-[#f7f7f7] text-[#374151] border border-[#e5e7eb]
    hover:bg-[#e5e7eb] hover:border-[#d1d5db]
    focus-visible:ring-[#9ca3af]/50
    disabled:bg-[#f7f7f7] disabled:text-[#9ca3af]
  `,
  ghost: `
    bg-transparent text-[#4b5563]
    hover:bg-[#f7f7f7] hover:text-[#111827]
    focus-visible:ring-[#9ca3af]/50
    disabled:text-[#9ca3af]
  `,
  danger: `
    bg-[#dc2626] text-white
    hover:bg-[#b91c1c]
    focus-visible:ring-[#ef4444]/50
    disabled:bg-[#f87171]
  `,
  success: `
    bg-[#4da45d] text-white
    hover:bg-[#3d904d]
    focus-visible:ring-[#5eb86d]/50
    disabled:bg-[#86efac]
  `,
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm min-h-[36px] gap-1.5',
  md: 'px-4 py-2 text-sm min-h-[44px] gap-2',
  lg: 'px-6 py-3 text-base min-h-[52px] gap-2.5',
};
```

**Project 2 Button Usage in Real Components:**
```tsx
// From TicketCard.tsx
<Button
  variant={action.variant === 'danger' ? 'danger' : action.variant === 'secondary' ? 'secondary' : 'primary'}
  size="sm"
  onClick={action.onClick}
  loading={action.loading}
  className="flex-1"
>
  {action.label}
</Button>
```

**Button Pattern Summary:**
| Aspect | Project 1 | Project 2 |
|--------|-----------|----------|
| Variants | 4 (primary, secondary, ghost, destructive) | 5 (primary, secondary, ghost, danger, success) |
| Sizes | 3 (sm, md, lg) | 3 (sm, md, lg) |
| Height/Padding | Fixed heights (h-9/11/12) | Min-heights (36/44/52px) |
| Icons | Not supported | Supported (leftIcon, rightIcon) |
| Loading State | isLoading prop | loading prop |
| Animation | Built-in focus ring | Framer Motion whileTap/Hover |
| Focus Style | focus:ring | focus-visible:ring |

### 2. Card Patterns

#### Project 1 Card CSS

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/index.css`

```css
.card {
  @apply bg-white rounded-lg border border-gray-200 shadow-card;
}
```

**Project 1 Card Usage:**
- Minimal use of the `.card` class
- Components build their own card-like structures

#### Project 2 Card Component (TicketCard)

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/TicketCard.tsx`

```tsx
<motion.article
  className={`
    bg-white
    rounded-lg shadow
    p-4
    hover:shadow-md
    transition-shadow duration-fast
    focus-within:ring-2 focus-within:ring-primary-500/50
    ${className}
  `}
>
  {/* Card content with semantic HTML */}
  <header className="flex flex-wrap items-center gap-2 mb-3">
    {/* Badges */}
  </header>

  <p className="text-sm text-neutral-700 mb-3">
    {/* Description */}
  </p>

  <footer className="flex items-center justify-between text-xs text-neutral-600 pt-3 border-t border-neutral-200">
    {/* Footer info */}
  </footer>
</motion.article>
```

**Project 2 StatsCard Component**

```tsx
<motion.div
  className={`
    bg-white
    rounded-lg shadow
    p-4
    ${className}
  `}
>
  <div className="flex items-start justify-between">
    <div className="space-y-1">
      <p className="text-sm text-neutral-500">{title}</p>
      <p className={`text-2xl font-bold ${colorStyle.value}`}>{value}</p>
    </div>
    {icon && (
      <div className={`p-2 rounded-lg ${colorStyle.icon}`}>
        {icon}
      </div>
    )}
  </div>
</motion.div>
```

**Card Pattern Summary:**
```
# Card Pattern Library

## Base Card Structure
bg-white
rounded-lg          (8px or md radius)
shadow or shadow-md (elevation)
p-4                 (16px padding)
border border-gray-200 or border-neutral-200 (light border)

## Interactive States
hover:shadow-md     (upgrade shadow on hover)
transition-shadow duration-fast (smooth shadow transition)

## Special Cases
focus-within:ring   (card itself has focus)
border-t border-neutral-200 (footer separator)

## Content Hierarchy
<header> with badges/metadata
<main content> with primary text
<footer> with supporting info

## Spacing Within Cards
mb-3: Between header and content
mb-3: Between content and footer
pt-3 border-t: Footer section separator
gap-2: Between badges in header
```

### 3. Form Input Patterns

#### Project 1 Input Component

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/components/ui/Input.tsx`

```typescript
const baseInputStyles = `
  block w-full h-11 px-3 border border-gray-300 rounded-md
  text-gray-900 placeholder-gray-400 text-base
  focus:outline-none focus:ring-2 focus:ring-ring-500 focus:border-transparent
  disabled:bg-gray-100 disabled:cursor-not-allowed
  transition-colors
`;

const errorInputStyles = 'border-red-500 focus:ring-red-500';
const labelStyles = 'block text-sm font-medium text-gray-700 mb-1.5';
const errorMessageStyles = 'mt-1.5 text-sm text-red-600 flex items-center gap-1';
```

**Project 1 Input Usage:**
```tsx
<Input
  label="Email"
  type="email"
  required
  error={errors.email}
/>
```

#### Project 2 Input Component

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/ui/Input.tsx`

```typescript
<div className="space-y-1.5">
  {/* Label with required indicator */}
  <label className="block text-sm font-medium text-[#374151]">
    {label}
    {optional ? (
      <span className="ml-1 text-[#9ca3af] font-normal">(optional)</span>
    ) : (
      <span className="ml-0.5 text-[#ef4444]">*</span>
    )}
  </label>

  {/* Input wrapper with icons */}
  <div className="relative">
    {leftIcon && (
      <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9ca3af] pointer-events-none">
        {leftIcon}
      </div>
    )}

    <input
      className={`
        w-full px-3 py-2.5
        ${leftIcon ? 'pl-10' : ''}
        ${rightIcon ? 'pr-10' : ''}
        bg-white
        border rounded-lg
        text-[#111827]
        placeholder:text-[#9ca3af]
        transition-colors duration-150
        focus:outline-none focus:ring-2 focus:ring-offset-0
        disabled:bg-[#fafbfc] disabled:text-[#707070] disabled:cursor-not-allowed
        ${
          hasError
            ? 'border-[#ef4444] focus:ring-[#ef4444]/20 focus:border-[#ef4444]'
            : 'border-[#d1d5db] focus:ring-[#13239c]/20 focus:border-[#13239c]'
        }
      `}
      aria-invalid={hasError}
      aria-describedby={[hasError && errorId, hint && hintId].filter(Boolean).join(' ')}
      aria-required={!optional}
    />

    {hasError && (
      <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[#ef4444]">
        <AlertCircle className="w-5 h-5" aria-hidden="true" />
      </div>
    )}
  </div>

  {/* Hint text */}
  {hint && !hasError && (
    <p id={hintId} className="text-sm text-[#707070]">
      {hint}
    </p>
  )}

  {/* Error message */}
  {hasError && (
    <p id={errorId} role="alert" className="text-sm text-[#dc2626] flex items-center gap-1.5">
      <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
      {error}
    </p>
  )}
</div>
```

**Input Pattern Summary:**
```
# Input Pattern Library

## Base Structure (Both Projects)
block w-full          (full width container)
px-3 py-2.5          (horizontal/vertical padding)
border rounded        (1px border, rounded corners)
text-base/sm         (readable font size)
placeholder:text-*   (muted placeholder text)

## Border Behavior
border-gray-300 (normal state)
focus:ring-2 focus:ring-offset-2 (focus state)
border-red-500 focus:ring-red-500 (error state)

## Label Styling
block text-sm font-medium text-gray-700
mb-1.5 (spacing from input)

## Error Messaging (Project 1)
mt-1.5 text-sm text-red-600
flex items-center gap-1 (with icon)

## Advanced Features (Project 2)
Icon support (leftIcon, rightIcon)
hint prop for help text
optional indicator
aria labels for accessibility
Tighter spacing (space-y-1.5)
Ring offset removed (ring-offset-0)

## Disabled State
bg-gray-100 cursor-not-allowed opacity-reduced
```

### 4. Badge/Tag Patterns

#### Project 1 Badge Component

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/components/ui/Badge.tsx`

```typescript
// Status Badge
const statusConfig: Record<SubmissionStatus, { bg: string; text: string; dot: string; label: string }> = {
  pending: {
    bg: 'bg-amber-100',
    text: 'text-amber-800',
    dot: 'bg-amber-500',
    label: 'Pending',
  },
  in_progress: {
    bg: 'bg-ring-100',
    text: 'text-ring-800',
    dot: 'bg-ring-500',
    label: 'In Progress',
  },
  resolved: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    dot: 'bg-green-500',
    label: 'Resolved',
  },
};

export function StatusBadge({ status, showDot = true }: BadgeProps) {
  const config = statusConfig[status];
  return (
    <span className={`
      inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
      ${config.bg} ${config.text}
    `}>
      {showDot && <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />}
      {config.label}
    </span>
  );
}
```

#### Project 2 Badge Components

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/ui/Badge.tsx`

```typescript
// Issue Type Badge
const ISSUE_TYPE_CONFIG: Record<IssueType, IssueTypeConfig> = {
  pan_issue: {
    label: 'PAN Issue',
    icon: <AlertCircle className="w-3.5 h-3.5" />,
    className: 'bg-issue-pan-bg text-issue-pan',
  },
  swapping: {
    label: 'Swapping',
    icon: <RefreshCcw className="w-3.5 h-3.5" />,
    className: 'bg-issue-swapping-bg text-issue-swapping',
  },
  // ... more types ...
};

export function IssueTypeBadge({
  issueType,
  showIcon = true,
  size = 'md',
  className = '',
}: IssueTypeBadgeProps) {
  const config = ISSUE_TYPE_CONFIG[issueType];
  const sizeClasses = size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-xs';
  return (
    <span className={`
      inline-flex items-center gap-1.5 rounded-md font-medium
      ${sizeClasses}
      ${config.className}
      ${className}
    `}>
      {showIcon && <span aria-hidden="true">{config.icon}</span>}
      {config.label}
    </span>
  );
}

// Status Badge (different from Project 1)
const STATUS_CONFIG: Record<StatusType, StatusConfig> = {
  open: {
    label: 'Open',
    icon: <Clock className="w-3.5 h-3.5" />,
    className: 'bg-status-open-bg text-status-open',
  },
  claimed: {
    label: 'Claimed',
    icon: <UserCheck className="w-3.5 h-3.5" />,
    className: 'bg-status-claimed-bg text-status-claimed',
  },
  resolved: {
    label: 'Resolved',
    icon: <CheckCircle className="w-3.5 h-3.5" />,
    className: 'bg-status-resolved-bg text-status-resolved',
  },
};

// Count Badge (unique to Project 2)
export function CountBadge({ count, variant = 'default', className = '' }: CountBadgeProps) {
  return (
    <span className={`
      inline-flex items-center justify-center
      min-w-[20px] h-5 px-1.5
      rounded-full text-xs font-medium
      ${COUNT_VARIANT_CLASSES[variant]}
      ${className}
    `}>
      {count}
    </span>
  );
}
```

**Badge Pattern Summary:**
```
# Badge Pattern Library

## Base Badge Structure
inline-flex items-center
px-2.5 py-0.5 or px-1.5 py-0.5 (tight padding)
rounded-md or rounded-full (radius)
text-xs font-medium (small, bold text)

## Color Pattern: {bg-color}bg {text-color}
bg-{color}-100 (light background)
text-{color}-800 (dark text for contrast)

## Icon Pattern
gap-1.5 (spacing from icon)
w-3.5 h-3.5 (icon size)
aria-hidden="true" (accessibility)

## Variants by Project 1
Status badges with colored dots
Simple labels
Pill shape (rounded-full) for some variants

## Variants by Project 2
Multiple badge types (Issue, Status, Ticket, Category, SubIssue, Role, Count)
Icons included in many variants
Size support (sm/md)
Semantic CSS variables for colors
Role badges with rounded-full
Count badges with min-w for number alignment

## Sizing Pattern
sm: px-1.5 py-0.5 text-xs
md: px-2 py-1 text-xs (Project 2) or px-2.5 py-0.5 text-xs (Project 1)

## Color Usage
Semantic colors (primary, success, danger, warning)
Issue-specific colors (custom palette in Project 2)
Status colors (open/claimed/resolved)
```

### 5. Table Patterns

#### Project 1 Table Utilities

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/index.css`

```css
.table-header {
  @apply px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider;
}

.table-cell {
  @apply px-4 py-3 text-sm text-gray-700;
}

.table-row {
  @apply border-b border-gray-100 hover:bg-gray-50 transition-colors;
}
```

**Table Pattern Summary:**
```
# Table Pattern Library

## Header Styling
px-4 py-3 (generous padding)
text-xs font-semibold uppercase (emphasis)
text-gray-600 (subtle color)
tracking-wider (letter spacing)

## Cell Styling
px-4 py-3 (match header padding)
text-sm text-gray-700 (readable)

## Row Styling
border-b border-gray-100 (bottom border)
hover:bg-gray-50 (subtle hover highlight)
transition-colors (smooth interaction)
```

### 6. Modal/Dialog Patterns

#### Project 2 Image Modal (TicketCard)

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/TicketCard.tsx`

```tsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4"
  onClick={() => setSelectedImage(null)}
  role="dialog"
  aria-modal="true"
  aria-label="Image preview"
>
  <motion.div
    initial={{ scale: 0.9, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    exit={{ scale: 0.9, opacity: 0 }}
    className="relative max-w-4xl max-h-full"
    onClick={(e) => e.stopPropagation()}
  >
    <button
      onClick={() => setSelectedImage(null)}
      className="
        absolute -top-12 right-0
        p-2 rounded-full
        text-white hover:text-neutral-300
        hover:bg-white/10
        transition-colors
        focus:outline-none focus-visible:ring-2 focus-visible:ring-white
      "
      aria-label="Close image preview"
    >
      <X className="w-6 h-6" />
    </button>
    <img
      src={selectedImage}
      alt="Full size preview"
      className="max-w-full max-h-[80vh] object-contain rounded-lg"
    />
  </motion.div>
</motion.div>
```

**Modal Pattern Summary:**
```
# Modal/Dialog Pattern Library

## Backdrop
fixed inset-0 (full screen overlay)
bg-black/75 (dark overlay with transparency)
z-50 (high stacking context)
flex items-center justify-center (centering)

## Modal Container
relative (for positioned absolute children)
max-w-4xl max-h-full (size constraints)
rounded-lg (border radius)

## Close Button
absolute -top-12 right-0 (positioned outside modal)
p-2 rounded-full (compact icon button)
text-white hover:text-neutral-300 (light theme)
hover:bg-white/10 (subtle hover)
focus-visible:ring-2 focus-visible:ring-white (focus)

## Animations
Framer Motion for smooth enter/exit
scale 0.9 to 1 (zoom in effect)
opacity 0 to 1 (fade effect)

## Accessibility
role="dialog" aria-modal="true"
aria-label for context
Logical tab order
```

### 7. Layout Patterns

#### Project 1 Layout Component

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/components/Layout.tsx`

```tsx
<div className="min-h-screen bg-gray-50 flex flex-col">
  {/* Header */}
  <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-14">
        {/* Logo and nav */}
      </div>
    </div>
  </header>

  {/* Main content */}
  <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {children}
  </main>

  {/* Footer */}
  <footer className="bg-white border-t border-gray-200">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      {/* Footer content */}
    </div>
  </footer>
</div>
```

**Layout Pattern Summary:**
```
# Layout Pattern Library

## Page Structure
min-h-screen (full viewport height)
flex flex-col (vertical layout)
bg-gray-50 (subtle background)

## Header
sticky top-0 z-40 (sticks to top, below modals)
bg-white border-b border-gray-200 (separation)
h-14 (standard header height - 56px)

## Container Width
max-w-7xl (1280px max width)
mx-auto (centered)
px-4 sm:px-6 lg:px-8 (responsive padding)

## Main Content
flex-1 (takes remaining height)
px-4 sm:px-6 lg:px-8 py-8 (responsive padding + top/bottom)
max-w-7xl w-full mx-auto (constraint + centering)

## Footer
bg-white border-t border-gray-200 (separation from content)
py-4 (compact padding)

## Z-Index Hierarchy
z-40: Header (sticky)
z-50: Modals
z-70+: Tooltips, popovers, toasts
```

---

## Consistency Audit Checklist

Before adding ANY visual element, Claude must run through this checklist to ensure consistency with the established design system.

### Pre-Implementation Checklist

- [ ] **Color Check**
  - [ ] Is the primary color in the blessed color palette?
  - [ ] Are all tints/shades from the approved scale?
  - [ ] Are semantic colors used correctly (primary for actions, danger for destructive)?
  - [ ] Is dark mode (if applicable) supported?
  - [ ] No arbitrary hex colors like `#f0f0f0` - use the palette

- [ ] **Spacing Check**
  - [ ] Is padding/margin using the established spacing scale?
  - [ ] Common values: 4px, 8px, 12px, 16px, 20px, 24px, 32px
  - [ ] Are element gaps consistent with spacing scale?
  - [ ] Vertical spacing follows pattern (mb-2, mb-3, mb-4)?
  - [ ] No arbitrary values like `padding: 13px`

- [ ] **Typography Check**
  - [ ] Font size is from the approved scale (xs, sm, base, lg, xl, 2xl, etc.)?
  - [ ] Font weight is semantic (normal, medium, semibold, bold)?
  - [ ] Line height matches the size (heading vs. body)?
  - [ ] Text color is from semantic palette (text-primary, text-secondary, etc.)?
  - [ ] No inline styles with custom font sizes

- [ ] **Component Check**
  - [ ] Does a similar component already exist in the codebase?
  - [ ] If yes, use it rather than creating a new variant
  - [ ] Are all component props properly typed?
  - [ ] Does the component follow the established pattern?
  - [ ] Is the component exported and documented?

- [ ] **Border & Radius Check**
  - [ ] Border radius uses the scale (xs, sm, md, lg, xl, full)?
  - [ ] Border colors are from the palette (border-gray-200)?
  - [ ] No arbitrary border-radius values like `border-radius: 7px`

- [ ] **Shadow Check**
  - [ ] Shadow uses the established scale (sm, md, lg)?
  - [ ] Shadow matches the elevation purpose (card, modal, overlay)?
  - [ ] No custom shadow definitions

- [ ] **Animation Check**
  - [ ] Animation uses approved durations (fast, normal, slow)?
  - [ ] Animation uses approved easing functions?
  - [ ] No custom keyframes without justification
  - [ ] Respects prefers-reduced-motion

- [ ] **Responsive Check**
  - [ ] Mobile-first approach (base styles, then sm:, md:, lg:)?
  - [ ] Breakpoints match Tailwind defaults (sm 640px, md 768px, lg 1024px)?
  - [ ] No custom breakpoints without justification
  - [ ] Touch targets at least 44x44px

- [ ] **Dark Mode Check** (if applicable)
  - [ ] Color scheme has dark mode variants
  - [ ] Uses semantic color variables
  - [ ] Text contrast is sufficient (WCAG AA)
  - [ ] No hardcoded colors that don't work in dark mode

- [ ] **Accessibility Check**
  - [ ] Focus styles are visible (ring with offset)
  - [ ] Text color contrast is sufficient (4.5:1 minimum)
  - [ ] Interactive elements have proper ARIA labels
  - [ ] Semantic HTML is used (button, label, etc.)
  - [ ] No keyboard traps

- [ ] **Browser/CSS Support Check**
  - [ ] No CSS Grid/Flexbox only without fallbacks (if supporting older browsers)
  - [ ] CSS custom properties work in target browsers
  - [ ] No arbitrary CSS that breaks under constraints

### Real-World Audit Checklist

**Scenario: Adding a new "warning" button variant**

Before coding:
- [ ] Is there already a button variant for warnings? (Check: destructive is for errors, ghost for subtle)
- [ ] What color should the warning button use? (Check: Warning palette uses amber)
- [ ] What size options does it need? (Check: Existing buttons have sm/md/lg)
- [ ] Does it follow the button spec for padding/height? (Check: md should be h-11 px-5)
- [ ] What's the hover state color? (Check: One shade darker in the palette)

**Scenario: Adding a new card type**

Before coding:
- [ ] What spacing does the card need? (Check: Cards typically p-4)
- [ ] What shadow level? (Check: Standard cards use shadow-md)
- [ ] What border color? (Check: border-gray-200)
- [ ] Border radius? (Check: rounded-lg)
- [ ] Is a separate component needed, or just className composition?

---

## Real Examples from Both Projects

### Button Comparison

#### Project 1 Primary Button
```tsx
// Usage:
<Button variant="primary" size="md">Save</Button>

// Renders as:
className="
  inline-flex items-center justify-center font-medium rounded-md transition-colors
  focus:outline-none focus:ring-2 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed
  bg-ring-700 text-white font-semibold
  hover:bg-ring-800 focus:ring-ring-500
  h-11 px-5 text-base
"
```

#### Project 2 Primary Button
```tsx
// Usage:
<Button variant="primary" size="md">Save</Button>

// Renders as:
className="
  inline-flex items-center justify-center
  font-medium rounded-lg
  transition-colors duration-fast
  focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
  disabled:cursor-not-allowed disabled:opacity-60
  bg-[#0f1c7a] text-white
  hover:bg-[#0c1660]
  focus-visible:ring-[#13239c]/50
  disabled:bg-[#7886f7]
  px-4 py-2 text-sm min-h-[44px] gap-2
"
```

**Key Differences:**
| Aspect | Project 1 | Project 2 |
|--------|-----------|----------|
| Size handling | Fixed h-11 | Min-height 44px |
| Focus state | focus:ring | focus-visible:ring |
| Disabled opacity | 50% | 60% |
| Hover color | One shade darker | Calculated from palette |
| Border radius | rounded-md | rounded-lg |
| Animation | transition-colors | transition-colors duration-fast |

### Card Comparison

#### Project 1 Card Basic
```tsx
<div className="bg-white rounded-lg border border-gray-200 shadow-card p-4">
  {/* Content */}
</div>
```

#### Project 2 Card (TicketCard)
```tsx
<motion.article
  className="
    bg-white
    rounded-lg shadow
    p-4
    hover:shadow-md
    transition-shadow duration-fast
    focus-within:ring-2 focus-within:ring-primary-500/50
  "
>
  {/* Semantic structure with header/footer */}
</motion.article>
```

**Key Differences:**
| Aspect | Project 1 | Project 2 |
|--------|-----------|----------|
| Shadow | Custom shadow-card | Standard shadow/shadow-md |
| Hover behavior | None specified | Upgrade shadow + animate |
| Focus handling | None | focus-within:ring |
| Animation library | None | Framer Motion |
| Semantic HTML | Plain div | article/header/footer |
| Border | Explicit border-gray-200 | None (shadow provides depth) |

### Input Comparison

#### Project 1 Input
```tsx
<input
  className="
    block w-full h-11 px-3 border border-gray-300 rounded-md
    text-gray-900 placeholder-gray-400 text-base
    focus:outline-none focus:ring-2 focus:ring-ring-500 focus:border-transparent
    disabled:bg-gray-100 disabled:cursor-not-allowed
    transition-colors
  "
/>
```

#### Project 2 Input
```tsx
<input
  className="
    w-full px-3 py-2.5
    bg-white
    border rounded-lg
    text-[#111827]
    placeholder:text-[#9ca3af]
    transition-colors duration-150
    focus:outline-none focus:ring-2 focus:ring-offset-0
    disabled:bg-[#fafbfc] disabled:text-[#707070] disabled:cursor-not-allowed
    border-[#d1d5db] focus:ring-[#13239c]/20 focus:border-[#13239c]
  "
/>
```

**Key Differences:**
| Aspect | Project 1 | Project 2 |
|--------|-----------|----------|
| Height | h-11 (44px) | No fixed height, py-2.5 (10px) |
| Ring offset | ring-offset-2 | ring-offset-0 |
| Focus border | border-transparent | border-[color] |
| Disabled bg | gray-100 | #fafbfc |
| Disabled text | Inherited | #707070 |
| Color values | Tailwind tokens | CSS vars as hex |
| Duration | No explicit duration | duration-150 |

### Badge Comparison

#### Project 1 Status Badge
```tsx
<span className="
  inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
  bg-amber-100 text-amber-800
">
  <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
  Pending
</span>
```

#### Project 2 Issue Badge
```tsx
<span className="
  inline-flex items-center gap-1.5 rounded-md font-medium
  px-2 py-1 text-xs
  bg-issue-pan-bg text-issue-pan
">
  <AlertCircle className="w-3.5 h-3.5" aria-hidden="true" />
  PAN Issue
</span>
```

**Key Differences:**
| Aspect | Project 1 | Project 2 |
|--------|-----------|----------|
| Shape | rounded-full (pill) | rounded-md (subtle) |
| Icon type | Colored dot | Lucide icon |
| Icon size | w-1.5 h-1.5 | w-3.5 h-3.5 |
| Color variables | Tailwind utilities | Custom CSS variables |
| Size variants | Single size | sm/md support |
| Padding | px-2.5 py-0.5 | px-2 py-1 (md) or px-1.5 py-0.5 (sm) |

### Status Badge Difference

Project 1 uses: `pending`, `in_progress`, `forwarded`, `resolved`
Project 2 uses: `open`, `claimed`, `resolved`

These are domain-specific differences, not design system inconsistencies.

---

## The "Blessed Patterns" System

This system maintains a curated list of approved patterns and prevents deviation from the design system.

### How to Build the Blessed List

#### Step 1: Extract from CSS Files
Read `index.css` and note all `@layer components` and custom class definitions.

**Project 1 Blessed Classes:**
```
.btn, .btn-primary, .btn-secondary, .btn-ghost, .btn-destructive
.input, .input-error, .input-label, .input-error-message
.card
.badge, .badge-dot
.skeleton
.line-clamp-1, .line-clamp-2
.table-header, .table-cell, .table-row
```

**Project 2: No @apply classes defined**
Uses CSS variables for everything, so blessed list is from components and color tokens.

#### Step 2: Extract from Components
List all exported components that are "approved" for use.

**Project 1 UI Components:**
- `Button` (variants: primary, secondary, ghost, destructive; sizes: sm, md, lg)
- `Input` (with label, error, required support)
- `Textarea` (with label, error, required support)
- `Select` (with label, error, required support)
- `StatusBadge` (variants: pending, in_progress, forwarded, resolved)
- `Badge` (variants: default, success, warning, error, info)

**Project 2 UI Components:**
- `Button` (variants: primary, secondary, ghost, danger, success; sizes: sm, md, lg; icons)
- `IconButton` (sized button for icons)
- `Input` (with label, error, hint, icons, optional)
- `Textarea` (with label, error, hint, optional)
- `Select` (with label, error, hint, leftIcon, optional)
- `IssueTypeBadge` (all issue types)
- `StatusBadge` (open, claimed, resolved)
- `TicketBadge`, `QueryCategoryBadge`, `SubIssueBadge`, `RoleBadge`, `CountBadge`
- `TicketCard`, `CompactTicketCard`
- `StatsCard`, `MiniStat`

#### Step 3: Create Forbidden List

**Forbidden Patterns (things NOT to do):**
- [ ] Don't create custom `<div className="inline-flex ...">` - use Badge component
- [ ] Don't style buttons with arbitrary classNames - use Button component
- [ ] Don't use hardcoded colors like `#f0f0f0` - use color palette
- [ ] Don't create custom border radius values like `rounded-2.5`
- [ ] Don't use custom shadow definitions
- [ ] Don't use arbitrary gap/margin values
- [ ] Don't create new button variants without discussion
- [ ] Don't use custom font sizes outside the scale
- [ ] Don't use custom animations without justification
- [ ] Don't apply styles with `!important` (except for utility reset)

### How to Handle New Patterns

**Scenario: Need a new button variant "tertiary"**

1. **Check if it exists**: Search codebase for existing variants
2. **Justify the need**: Does primary/secondary/ghost not cover this?
3. **Define the spec**:
   ```
   Tertiary Button Spec:
   - Background: Use accent color (gold in Project 1)
   - Text: Use primary text color
   - Border: 1px solid accent-300
   - Hover: Darker accent background
   - Size: Follow existing size system
   ```
4. **Get approval**: Document and add to blessed list
5. **Implement**: Add to Button component
6. **Export**: Make sure it's available from components

### How to Propose Design System Extensions

**Process:**
1. Document the requirement clearly
2. Show why existing patterns don't cover it
3. Propose the new token/pattern with examples
4. Check for conflicts with existing colors/spacing
5. Update the blessed list
6. Add to documentation

**Example Extension Request:**
```
Title: Add "loading" state color token

Current Issue:
Loading states use primary color, but this can be confusing with active states.

Proposed Solution:
Add --color-loading: #6b7280 (neutral gray) to semantic colors

Usage:
- Loading spinners and skeleton placeholders
- "Loading..." button text
- Disabled-but-not-error states

Impact:
- Adds 1 new color variable
- Improves semantic clarity
- No changes to existing components required
```

---

## CSS Architecture Detection

This section shows how to detect what CSS strategy an app uses and what it means for design consistency.

### Detection Checklist

- [ ] **Tailwind CSS**: Does `tailwind.config.js` exist?
- [ ] **Tailwind plugins**: Are there plugins in the config?
- [ ] **@apply rules**: Does `index.css` have `@layer components` with `@apply`?
- [ ] **CSS Modules**: Are there `.module.css` files?
- [ ] **CSS-in-JS**: Are there `styled-components` or `emotion` imports?
- [ ] **BEM/SMACSS**: Are there naming patterns like `.button--primary`?
- [ ] **CSS variables**: Does `:root` have `--color-*` variables?
- [ ] **Custom classNames**: Are there arbitrary classNames in JSX?

### Project 1 Architecture: Tailwind + @apply

**Evidence:**
```
✓ tailwind.config.js exists
✓ index.css has @tailwind directives
✓ @layer components with @apply for button, input, card, badge, table
✓ CSS variables: None (uses Tailwind tokens)
✓ CSS Modules: No
✓ CSS-in-JS: No
✓ BEM naming: No
✓ Arbitrary classNames: Some (template literals in components)
```

**Characteristics:**
- All styling is Tailwind utilities or @apply components
- Color tokens defined in `tailwind.config.js`
- Custom components use `@apply` to compose utility classes
- Some inline className strings (not ideal but acceptable)

**Design System Impact:**
- Easy to audit (all colors in one config file)
- All sizes/spacing in Tailwind defaults or config
- Consistent breakpoints
- Limited dark mode support (requires Tailwind's dark: prefix)

### Project 2 Architecture: Tailwind + CSS Variables

**Evidence:**
```
✓ tailwind.config.js exists
✓ index.css has CSS variables in :root
✓ tailwind.config.js extends with `var(--color-*)`
✓ CSS Modules: No
✓ CSS-in-JS: No (except Framer Motion for animation)
✓ BEM naming: No
✓ Arbitrary hex values in classNames: Yes (problematic)
```

**Characteristics:**
- Uses CSS custom properties for tokens (colors, spacing, shadows, etc.)
- Tailwind configured to use CSS variables
- Components use semantic color names (primary, accent, secondary)
- Arbitrary hex values in some components (anti-pattern)

**Design System Impact:**
- Great for theme switching (change :root variables)
- Dark mode ready (add media query for `prefers-color-scheme`)
- Values are centralized and documented
- Some deviation from blessed palette in component code (arbitrary hex values)

### Architecture Comparison

| Aspect | Project 1 | Project 2 |
|--------|-----------|----------|
| Core CSS Framework | Tailwind only | Tailwind + CSS variables |
| Color Definition | tailwind.config.js | index.css :root |
| Component Styling | @apply in CSS | className strings |
| Custom Properties | None | Full token system |
| Dark Mode Support | Limited | Full support (prefers-color-scheme) |
| Maintenance | All tokens in JS | Tokens in CSS |
| Theme Switching | Not supported | Supported (change :root) |
| Arbitrary Values | Minimal | Some (hex strings) |
| Animation | CSS keyframes | Framer Motion + CSS |
| Consistency Risk | Low | Medium (arbitrary values) |

### Mixed Architecture Detection

**Red Flags for Mixed Approaches:**
- [ ] Both Tailwind utilities AND CSS Modules in same project
- [ ] CSS-in-JS imports alongside Tailwind
- [ ] Both `@apply` and inline styles in components
- [ ] Different components using different styling approaches
- [ ] Some colors from config, some hardcoded

**Project 1-2 Mixed Elements:**
- Project 1 uses `@apply` but also inline `className` strings (acceptable blend)
- Project 2 mixes semantic CSS vars with arbitrary hex values (problematic)
- Project 2 uses Framer Motion for animations (library choice, not CSS architecture issue)

---

## Tailwind-Specific Forensics

Since both projects use Tailwind, here's detailed guidance for extracting Tailwind-specific information.

### 1. Reading tailwind.config.js

#### Structure Inspection
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Custom theme extensions
      colors: { /* ... */ },
      fontFamily: { /* ... */ },
      fontSize: { /* ... */ },
      // ... more theme properties
    },
  },
  plugins: [],
}
```

**What to Extract:**
- [ ] Content paths (which files Tailwind scans)
- [ ] Custom color definitions
- [ ] Custom font families
- [ ] Custom font sizes
- [ ] Custom spacing/sizing
- [ ] Custom border radius
- [ ] Custom shadows
- [ ] Custom animations
- [ ] Plugins in use

#### Project 1 tailwind.config.js Analysis
```javascript
// Colors
colors: {
  ring: { 50-900 scale },    // Brand primary
  gold: { 50-900 scale },    // Accent
  // No other custom colors (uses Tailwind defaults for gray, red, green, etc.)
}

// Fonts
fontFamily: {
  sans: ['Manrope', ...],
  mono: ['JetBrains Mono', ...],
  // No display font (uses sans as default)
}

// Additions
fontSize: { '2xs': '0.625rem' },   // Extra small size
borderRadius: { '4xl': '2rem' },   // Extra large radius
boxShadow: {
  'sm', 'md', 'lg', 'card'
},
animation: {
  'shimmer', 'spin-slow'
},
```

**Extraction Summary:**
- Minimal custom theme
- Only brand colors are custom (ring, gold)
- One new font size and border radius
- Custom shadows for cards
- Two custom animations

#### Project 2 tailwind.config.js Analysis
```javascript
// Colors - extensive custom palette
colors: {
  primary, accent, secondary, neutral,
  success, warning, danger,
  surface, border, text,
  status, issue (8+ types)
  // All mapped to CSS variables
}

// Fonts
fontFamily: {
  sans: ['Inter', ...],
  display: ['Manrope', ...],   // Unique display font
  mono: ['ui-monospace', ...],
}

// Additions
fontSize: {
  // Maps CSS variables
}
borderRadius: {
  // Maps CSS variables
}
boxShadow: {
  // Standard + colored shadows
}
transitionDuration, transitionTimingFunction, zIndex, animation, keyframes
// All via CSS variables
```

**Extraction Summary:**
- Extensive custom theme (semantic palette)
- All colors defined as CSS variables
- Display font variant
- Comprehensive token system

### 2. Detecting Custom Color Scales

**Project 1 Method: Direct hex values**
```javascript
ring: {
  50: '#e8ecfd',
  100: '#d4d9f7',
  // ... light to dark scale
  500: '#2a3dc9',
  700: '#13239c',    // Primary
  900: '#0e1a6b',
}
```

**How to Verify:**
- [ ] Are all 10 shades present (50-900)?
- [ ] Is there a primary level (usually 500 or 700)?
- [ ] Do values go from light (#fff-ish) to dark?
- [ ] Are values evenly distributed?

**Project 2 Method: CSS variable references**
```javascript
primary: {
  50: 'var(--color-primary-50)',
  // ...
  500: 'var(--color-primary-500)',
  // ...
}
```

**How to Verify:**
- [ ] Check that CSS variables are defined in index.css
- [ ] Verify values match across config and CSS
- [ ] Check for consistency in variable naming

### 3. Finding @apply Usage

**Search Strategy:**
```bash
grep -n "@apply" src/index.css
```

**Project 1 Results:**
```
@apply antialiased text-gray-900 bg-gray-50;
@apply inline-flex items-center justify-center font-medium rounded-md transition-colors;
@apply focus:outline-none focus:ring-2 focus:ring-offset-2;
@apply disabled:opacity-50 disabled:cursor-not-allowed;
// ... many more @apply statements
```

**Analysis:**
- Uses @apply to create reusable component classes (`.btn`, `.input`, etc.)
- Combines multiple utilities into single class
- Improves maintainability over inline classNames

**Pattern Recognition:**
```css
.btn {
  @apply inline-flex items-center justify-center font-medium rounded-md transition-colors;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
  @apply disabled:opacity-50 disabled:cursor-not-allowed;
}
// Base button class with all interactive states
```

### 4. Detecting Tailwind Plugins

**Checklist:**
- [ ] Search `tailwind.config.js` for `plugins: [...]`
- [ ] Check `package.json` for `@tailwindcss/*` packages
- [ ] Look for plugin-specific syntax in CSS

**Project 1 Findings:**
```javascript
plugins: [],  // No plugins
```

**Project 2 Findings:**
```javascript
plugins: [],  // No plugins
```

**Common Plugins to Look For:**
- `@tailwindcss/forms` - Enhanced form styling
- `@tailwindcss/typography` - Rich text styling
- `@tailwindcss/container-queries` - Container queries
- `@tailwindcss/aspect-ratio` - Aspect ratio utility
- Third-party plugins for themes, animations, etc.

### 5. Checking for !important Overrides

**Search Strategy:**
```bash
grep -n "!important" src/**/*.{ts,tsx,css}
```

**Why it Matters:**
- !important breaks specificity and maintainability
- Indicates design system conflict or workaround
- Should be extremely rare

**Project 1 Findings:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Analysis:**
- Only !important in prefers-reduced-motion (justified)
- No arbitrary overrides in components
- Good practice

### 6. Extracting Custom Utilities

**Pattern to Find:**
```
@layer utilities {
  .custom-class {
    /* custom CSS */
  }
}
```

**Project 1 Custom Utilities:**
```css
@layer utilities {
  .line-clamp-1, .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: ...
    // Text truncation utilities
  }

  .table-header, .table-cell, .table-row {
    // Table styling utilities
  }
}
```

**Project 2 Custom Utilities:**
- None found (uses CSS variables instead)

### 7. Verifying Tailwind Integration

**Checklist:**
- [ ] `@tailwind base;` at top of index.css?
- [ ] `@tailwind components;` present?
- [ ] `@tailwind utilities;` present?
- [ ] Order is: base → components → utilities?
- [ ] CSS layers properly organized?

**Project 1:**
```css
@import url('https://fonts.googleapis.com/...');
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base { /* ... */ }
@layer components { /* ... */ }
@layer utilities { /* ... */ }
```

**Status:** ✓ Properly configured

**Project 2:**
```css
@import "tailwindcss";
/* CSS variables in :root */
/* Custom animations, base styles, utilities */
```

**Status:** ✓ Properly configured (using newer @import syntax)

---

## Summary: Quick Reference for Claude

### When Starting a New Project, Extract:

1. **Colors**
   - Run tailwind.config.js through colors extractor
   - Scan index.css for CSS variables
   - Check for any hardcoded hex values
   - Document semantic color usage

2. **Typography**
   - fontFamily from config
   - fontSize scale
   - fontWeight values
   - lineHeight recommendations

3. **Spacing**
   - Base unit (4px, 8px, 16px)
   - Common padding/margin values
   - Gap/gap-x/gap-y patterns

4. **Components**
   - Export all UI components
   - List variants for each
   - Document props and defaults
   - Check for @apply usage

5. **Design Tokens**
   - Create blessed list
   - Document forbidden patterns
   - List custom utilities
   - Verify CSS architecture

### When Adding New Elements, Verify:

**Color:**
- [ ] Is the color in the blessed palette?
- [ ] Is it the right semantic color (primary, danger, etc.)?
- [ ] Does it work in light and dark modes?

**Spacing:**
- [ ] Is the value from the approved scale?
- [ ] Does it align with surrounding elements?

**Typography:**
- [ ] Is the size from the scale?
- [ ] Is the weight semantic?
- [ ] Is the color from the text hierarchy?

**Components:**
- [ ] Does a similar component exist?
- [ ] Am I using the approved pattern?
- [ ] Is it properly exported?

**Responsive:**
- [ ] Mobile-first approach?
- [ ] Breakpoints match Tailwind defaults?
- [ ] Touch targets 44x44px minimum?

**Accessibility:**
- [ ] Focus styles visible?
- [ ] Color contrast sufficient?
- [ ] Semantic HTML used?
- [ ] ARIA labels present?

### File Paths for Reference

**Project 1 (issue-tracker):**
- Config: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/tailwind.config.js`
- Styles: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/index.css`
- Components: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/components/ui/`

**Project 2 (los-issue-tracker):**
- Config: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/tailwind.config.js`
- Styles: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/index.css`
- Components: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/components/ui/`

---

**Document Version:** 1.0
**Last Updated:** 2026-02-26
**Status:** Comprehensive Reference
**Coverage:** 450+ lines of detailed forensics guidance
