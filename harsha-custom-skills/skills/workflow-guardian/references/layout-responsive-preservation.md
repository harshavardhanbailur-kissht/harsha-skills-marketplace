# Layout and Responsive Design Preservation Reference
## Protecting Application Layout Integrity

**Document Purpose**: This reference guide provides comprehensive patterns, detection methods, and defensive strategies for maintaining layout and responsive design consistency when adding features to existing applications. It prevents common layout breakages that occur when Claude adds new elements without respecting the existing grid structure, responsive patterns, and container design.

**Last Updated**: February 2026
**Skill**: workflow-guardian
**Coverage Area**: Layout structure preservation, responsive behavior maintenance, grid/flex pattern detection

---

## Table of Contents

1. [Overview](#overview)
2. [Core Layout Patterns](#core-layout-patterns)
3. [Grid and Flexbox Detection](#grid-and-flexbox-detection)
4. [Responsive Breakpoint Strategy](#responsive-breakpoint-strategy)
5. [Page Layout Templates](#page-layout-templates)
6. [Container and Wrapper Patterns](#container-and-wrapper-patterns)
7. [Overflow and Scrolling Patterns](#overflow-and-scrolling-patterns)
8. [Common Layout Breakages](#common-layout-breakages)
9. [Detection Methods](#detection-methods)
10. [Safe Implementation Practices](#safe-implementation-practices)

---

## Overview

### The Layout Preservation Problem

When Claude adds new features to applications, it often inadvertently breaks existing layouts by:

1. **Adding elements that don't fit the grid**: A new card added without considering grid-cols settings
2. **Breaking responsive behavior**: Adding breakpoint-dependent styles without respecting existing patterns
3. **Introducing incompatible patterns**: Mixing layout approaches (CSS Grid in a Flexbox container)
4. **Modifying container widths**: Adding constraints that differ from the established max-w-* pattern
5. **Creating overflow issues**: Adding content that breaks scroll behavior or triggers unwanted scrollbars
6. **Disrupting proportions**: Adding fixed-width elements to flexible layouts
7. **Breaking the document flow**: Using position: absolute/fixed without considering z-index and overflow ancestors

### Why This Matters

- **User Experience**: Layout breaks create visual chaos and reduce usability
- **Cross-Device Behavior**: Responsive breakages make apps unusable on mobile/tablet
- **Accessibility**: Layout changes can disrupt keyboard navigation and screen reader flow
- **Code Maintainability**: Each layout break requires debugging and fixes, increasing technical debt
- **Trust**: Users notice when an app "feels broken" after feature additions

### Defensive Framing

DANGEROUS: "I'll create a modern responsive layout for the new page"
SAFE: "I'll copy the exact layout structure from the nearest existing page, matching breakpoints, grid columns, and container widths"

---

## Core Layout Patterns

### Pattern Types in Modern Applications

#### 1. CSS Grid Layouts

Grid layouts use a multi-column structure with defined column counts, gaps, and responsive behavior.

**Characteristics**:
- Predictable column structure
- Consistent gutters/gaps
- Children automatically placed
- Grid-specific breakpoint rules

**Detection Signals**:
- `grid`, `grid-cols-*`, `grid-rows-*` classes
- `gap-*` or `gap-x-*`, `gap-y-*` classes
- `col-span-*`, `row-span-*` for spanning behavior
- Regular, repeating visual structure

**Example Grid Pattern (12-column layout)**:
```html
<!-- Existing pattern in application -->
<div class="grid grid-cols-12 gap-6 p-6">
  <div class="col-span-3 bg-gray-100">Sidebar</div>
  <div class="col-span-9 bg-white">Main Content</div>
</div>

<!-- Responsive variant -->
<div class="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6">
  <div class="md:col-span-3 bg-gray-100">Sidebar</div>
  <div class="md:col-span-9 bg-white">Main Content</div>
</div>

<!-- Adding new element: MATCH THE EXISTING STRUCTURE -->
<div class="grid grid-cols-12 gap-6 p-6">
  <div class="col-span-3 bg-gray-100">Sidebar</div>
  <div class="col-span-9 bg-white">Main Content</div>
  <!-- WRONG: Adding element outside the grid structure -->
  <!-- <div class="w-full">New Feature</div> -->

  <!-- CORRECT: New element respects grid (even if spanning full width) -->
  <div class="col-span-12 bg-blue-50">New Feature spanning full width</div>
</div>
```

**Common Tailwind Grid Classes**:
- `grid-cols-1`, `grid-cols-2`, `grid-cols-3`, `grid-cols-4`, `grid-cols-6`, `grid-cols-12`
- `grid-rows-1`, `grid-rows-2`, `grid-rows-3`, `grid-rows-6`
- `gap-1`, `gap-2`, `gap-3`, `gap-4`, `gap-6`, `gap-8`
- `col-span-1` through `col-span-12`
- `row-span-1` through `row-span-6`
- `auto-cols-min`, `auto-cols-max`, `auto-cols-fr`
- `auto-rows-min`, `auto-rows-max`, `auto-rows-fr`

#### 2. Flexbox Layouts

Flexbox creates flexible, direction-based layouts with alignment and distribution control.

**Characteristics**:
- Direction-based (row or column)
- Flexible sizing of children
- Powerful alignment and distribution
- Easier single-dimension layouts than Grid

**Detection Signals**:
- `flex`, `flex-col`, `flex-row` classes
- `justify-*` (main axis alignment)
- `items-*` (cross axis alignment)
- `flex-1`, `flex-grow`, `flex-shrink`
- `gap-*` for spacing

**Example Flexbox Pattern (Dashboard header)**:
```html
<!-- Existing pattern in application -->
<header class="flex items-center justify-between bg-white border-b px-6 py-4 gap-4">
  <h1 class="text-2xl font-bold">Dashboard</h1>
  <div class="flex items-center gap-3">
    <button>Search</button>
    <button>Settings</button>
  </div>
</header>

<!-- Adding new element: MATCH THE FLEX STRUCTURE -->
<!-- WRONG: Not respecting flex alignment and gaps -->
<header class="flex items-center justify-between bg-white border-b px-6 py-4 gap-4">
  <h1 class="text-2xl font-bold">Dashboard</h1>
  <div class="flex items-center gap-3">
    <button>Search</button>
    <button>Settings</button>
  </div>
  <div>New Feature</div> <!-- Breaks alignment -->
</header>

<!-- CORRECT: New element respects flex structure -->
<header class="flex items-center justify-between bg-white border-b px-6 py-4 gap-4">
  <h1 class="text-2xl font-bold">Dashboard</h1>
  <div class="flex items-center gap-3">
    <button>Search</button>
    <button>Settings</button>
    <button>New Feature</button> <!-- Added to flex group with gap-3 -->
  </div>
</header>
```

**Common Tailwind Flexbox Classes**:
- `flex`, `inline-flex`
- `flex-row`, `flex-col`, `flex-row-reverse`, `flex-col-reverse`
- `flex-wrap`, `flex-nowrap`, `flex-wrap-reverse`
- `justify-start`, `justify-center`, `justify-between`, `justify-around`, `justify-evenly`
- `items-start`, `items-center`, `items-end`, `items-baseline`, `items-stretch`
- `content-start`, `content-center`, `content-between`, `content-around`, `content-evenly`
- `gap-*` (from gap-0 to gap-96)
- `flex-1`, `flex-auto`, `flex-none`
- `grow`, `shrink`, `grow-0`, `shrink-0`

#### 3. Mixed Layout Patterns

Many applications combine Grid and Flexbox for different purposes.

**Example Pattern**:
```html
<!-- Page layout: Grid for regions (header, sidebar, content) -->
<div class="grid grid-cols-1 min-h-screen">
  <!-- Header: Flexbox for internal layout -->
  <header class="flex items-center justify-between bg-white border-b px-6 py-4">
    <h1 class="text-2xl font-bold">App</h1>
    <nav class="flex gap-4">
      <a>Home</a>
      <a>About</a>
    </nav>
  </header>

  <!-- Main content area: Grid for content layout -->
  <main class="grid grid-cols-12 gap-6 p-6 flex-1">
    <!-- Sidebar: Flexbox for stacking items -->
    <nav class="col-span-3 flex flex-col gap-2">
      <button>Item 1</button>
      <button>Item 2</button>
    </nav>

    <!-- Content: Grid for card layout -->
    <div class="col-span-9 grid grid-cols-3 gap-4">
      <div class="bg-white rounded-lg p-4">Card 1</div>
      <div class="bg-white rounded-lg p-4">Card 2</div>
      <div class="bg-white rounded-lg p-4">Card 3</div>
    </div>
  </main>
</div>

<!-- ADDING NEW FEATURE: Respect the hierarchy -->
<!-- New sidebar item: Use flex structure of parent -->
<nav class="col-span-3 flex flex-col gap-2">
  <button>Item 1</button>
  <button>Item 2</button>
  <button>Item 3 - New Feature</button> <!-- Matches gap-2 -->
</nav>

<!-- New content card: Use grid structure of parent -->
<div class="col-span-9 grid grid-cols-3 gap-4">
  <div class="bg-white rounded-lg p-4">Card 1</div>
  <div class="bg-white rounded-lg p-4">Card 2</div>
  <div class="bg-white rounded-lg p-4">Card 3</div>
  <div class="bg-white rounded-lg p-4">Card 4 - New Feature</div>
</div>
```

---

## Grid and Flexbox Detection

### Detecting Grid Patterns

#### Step 1: Scan for Grid Container Markers

```html
<!-- Search for these indicators in the codebase -->
<div class="grid ...">                    <!-- Base grid class -->
<div class="grid grid-cols-12 ...">       <!-- Specific column count -->
<div class="grid gap-6 ...">              <!-- Consistent gap -->
<div class="grid grid-cols-1 md:grid-cols-3 ..."> <!-- Responsive -->
```

#### Step 2: Identify Column Configuration

**Common column patterns**:
- `grid-cols-1` - Single column (mobile-first)
- `grid-cols-2` - Two columns (cards, pairs)
- `grid-cols-3` - Three columns (common dashboard)
- `grid-cols-4` - Four columns (product grids)
- `grid-cols-6` - Six columns (detailed layouts)
- `grid-cols-12` - Twelve columns (complex layouts)

**Detection method**:
```bash
# Search codebase for grid patterns
grep -r "grid-cols-" .
grep -r "grid gap-" .
grep -r "col-span-" .
```

**Matching strategy**:
- If adding to existing grid, use the same `grid-cols-*` value
- If spanning full width in a multi-column grid, use `col-span-N` matching total columns
- If adding a new row, match the gap pattern exactly

#### Step 3: Identify Gap Configuration

```html
<!-- Gap patterns establish visual breathing room -->
<div class="grid gap-2 ...">  <!-- Tight spacing -->
<div class="grid gap-4 ...">  <!-- Medium spacing (common) -->
<div class="grid gap-6 ...">  <!-- Comfortable spacing -->
<div class="grid gap-8 ...">  <!-- Generous spacing -->

<!-- Directional gaps -->
<div class="grid gap-x-4 gap-y-6 ...">  <!-- Different row/column gaps -->
```

**Detection method**:
```bash
grep -r "gap-[0-9]" .
grep -r "gap-x-" .
grep -r "gap-y-" .
```

**Matching strategy**:
- Always use consistent gap values across similar rows/columns
- Match horizontal gaps (gap-x-*) to existing patterns
- Match vertical gaps (gap-y-*) to existing patterns
- If unsure, `gap-4` or `gap-6` are industry standards

#### Step 4: Detect Auto-placement vs Explicit Positioning

```html
<!-- Auto-placement: Children fill grid automatically -->
<div class="grid grid-cols-3 gap-4">
  <div>1</div> <!-- Placed automatically in column 1 -->
  <div>2</div> <!-- Placed automatically in column 2 -->
  <div>3</div> <!-- Placed automatically in column 3 -->
  <div>4</div> <!-- Wraps to next row, column 1 -->
</div>

<!-- Explicit positioning: Children placed with span -->
<div class="grid grid-cols-12 gap-4">
  <div class="col-span-3">Sidebar</div>     <!-- 3 columns -->
  <div class="col-span-9">Content</div>    <!-- 9 columns -->
  <div class="col-span-12">Footer</div>    <!-- Full width -->
</div>
```

**Detection method**:
- Look for `col-span-*` classes - indicates explicit positioning
- Without spans - indicates auto-placement
- Pattern determines how to add new elements

### Detecting Flexbox Patterns

#### Step 1: Scan for Flex Container Markers

```html
<!-- Search for these indicators -->
<div class="flex ...">                  <!-- Base flex class -->
<div class="flex flex-col ...">         <!-- Column direction -->
<div class="flex items-center ...">     <!-- Vertical alignment -->
<div class="flex justify-between ...">  <!-- Horizontal distribution -->
```

#### Step 2: Identify Direction Configuration

```html
<!-- Row (default) -->
<div class="flex ...">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Column -->
<div class="flex flex-col ...">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Row reverse -->
<div class="flex flex-row-reverse ...">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Column reverse -->
<div class="flex flex-col-reverse ...">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

**Detection method**:
```bash
grep -r "flex-col" .
grep -r "flex-row" .
```

#### Step 3: Identify Alignment Configuration

```html
<!-- Main axis alignment (justify-*) -->
<div class="flex justify-start ...">      <!-- Items at start -->
<div class="flex justify-center ...">     <!-- Items centered -->
<div class="flex justify-between ...">    <!-- Items spaced apart -->
<div class="flex justify-around ...">     <!-- Items with space around -->
<div class="flex justify-evenly ...">     <!-- Items with equal space -->

<!-- Cross axis alignment (items-*) -->
<div class="flex items-start ...">       <!-- Align to start -->
<div class="flex items-center ...">      <!-- Centered alignment (common) -->
<div class="flex items-end ...">         <!-- Align to end -->
<div class="flex items-baseline ...">    <!-- Align to baseline -->
<div class="flex items-stretch ...">     <!-- Stretch to fill (default) -->
```

**Detection method**:
```bash
grep -r "justify-" .
grep -r "items-" .
```

**Common patterns**:
- `flex items-center justify-between` - Header layout (spread items with centered height)
- `flex flex-col items-center` - Centered column layout
- `flex justify-center items-center` - Centered both ways
- `flex items-stretch justify-between` - Full-height items spread apart

#### Step 4: Identify Flex Growth/Shrinking

```html
<!-- Fixed flex items -->
<div class="flex gap-4">
  <div class="w-32">Fixed width</div>
  <div class="w-48">Fixed width</div>
</div>

<!-- Flexible items -->
<div class="flex gap-4">
  <div class="flex-1">Takes 1 part</div>
  <div class="flex-1">Takes 1 part</div>
  <div class="flex-1">Takes 1 part</div>
</div>

<!-- Mixed sizing -->
<div class="flex gap-4">
  <div class="w-32 flex-shrink-0">Fixed sidebar</div>
  <div class="flex-1">Flexible content</div>
  <div class="w-48 flex-shrink-0">Fixed sidebar</div>
</div>
```

**Detection method**:
- `flex-1` indicates item grows to fill available space
- `flex-auto` indicates similar but different grow/shrink ratio
- `flex-none` indicates item doesn't grow or shrink
- `flex-shrink-0` indicates item won't shrink
- Width constraints (`w-*`) indicate fixed sizing

---

## Responsive Breakpoint Preservation

### Understanding Tailwind Breakpoints

Tailwind CSS uses a mobile-first approach by default. Breakpoints define screen widths where styles change.

#### Default Tailwind Breakpoints

```css
/* tailwind.config.js default breakpoints */
{
  sm: '640px',      /* Small devices (landscape phones) */
  md: '768px',      /* Medium devices (tablets) */
  lg: '1024px',     /* Large devices (desktops) */
  xl: '1280px',     /* Extra large devices (large desktops) */
  '2xl': '1536px'   /* 2XL devices (very large desktops) */
}
```

**What mobile-first means**:
- Base styles apply to all screen sizes
- Prefixed styles override at that breakpoint and above
- `md:w-full` means "width: full from md breakpoint upward"

#### Detecting Custom Breakpoints

Custom breakpoints are defined in `tailwind.config.js`:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      // Custom breakpoints in this application
      'tablet': '800px',
      'desktop': '1200px',
      'wide': '1600px',
    }
  }
}
```

**Search method**:
```bash
# Find tailwind config file
find . -name "tailwind.config.js" -o -name "tailwind.config.ts"
grep -A 20 "screens:" tailwind.config.js
```

### Common Responsive Patterns

#### Pattern 1: Mobile-First Stacking

```html
<!-- Mobile: Single column, Desktop: Multi-column -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
  <div class="bg-white rounded-lg p-4">Card 1</div>
  <div class="bg-white rounded-lg p-4">Card 2</div>
  <div class="bg-white rounded-lg p-4">Card 3</div>
</div>

<!-- Applied logic:
    Mobile (< 768px): grid-cols-1 (single column)
    Desktop (≥ 768px): md:grid-cols-3 (three columns)
    Mobile: gap-4 (smaller gap)
    Desktop: md:gap-6 (larger gap for better spacing)
-->

<!-- When adding similar cards, MUST match this pattern -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
  <div class="bg-white rounded-lg p-4">Card 4 - NEW</div>
</div>
```

#### Pattern 2: Responsive Typography

```html
<!-- Text size changes with screen size -->
<h1 class="text-xl md:text-2xl lg:text-3xl font-bold">
  Responsive Heading
</h1>

<!-- Applied logic:
    Mobile: text-xl (smaller heading)
    Tablet (≥ 768px): md:text-2xl (medium heading)
    Desktop (≥ 1024px): lg:text-3xl (large heading)
-->

<!-- When adding similar headings, MUST match this pattern -->
<h2 class="text-lg md:text-xl lg:text-2xl font-semibold">
  Similar Heading - NEW
</h2>
```

#### Pattern 3: Responsive Container Width

```html
<!-- Container becomes narrower on mobile -->
<div class="w-full px-4 md:px-6 lg:px-8 max-w-6xl mx-auto">
  Content
</div>

<!-- Applied logic:
    Mobile: full width with px-4 padding (16px on each side)
    Tablet: px-6 padding (24px on each side)
    Desktop: px-8 padding (32px on each side)
    All sizes: max-w-6xl (never wider than 1152px) centered with mx-auto
-->

<!-- When adding containers, MUST match this pattern -->
<div class="w-full px-4 md:px-6 lg:px-8 max-w-6xl mx-auto">
  New Content
</div>
```

#### Pattern 4: Responsive Sidebar Layout

```html
<!-- Mobile: Full-width stacked, Desktop: Sidebar + content -->
<div class="flex flex-col md:flex-row gap-4 md:gap-6">
  <!-- Sidebar -->
  <aside class="w-full md:w-1/4 md:flex-shrink-0">
    Sidebar content
  </aside>
  <!-- Main content -->
  <main class="w-full md:flex-1">
    Main content
  </main>
</div>

<!-- Applied logic:
    Mobile: flex-col (stacked vertically)
    Desktop: md:flex-row (side by side)
    Mobile: gap-4 (smaller spacing when stacked)
    Desktop: md:gap-6 (larger spacing when side-by-side)
    Sidebar: Fixed width on desktop (w-1/4), full width on mobile
    Content: Flexible on desktop (flex-1), full width on mobile
-->

<!-- When adding new sections, MUST respect this pattern -->
<div class="flex flex-col md:flex-row gap-4 md:gap-6">
  <aside class="w-full md:w-1/4 md:flex-shrink-0">
    Extended sidebar
  </aside>
  <main class="w-full md:flex-1">
    Extended content
  </main>
</div>
```

#### Pattern 5: Responsive Hiding/Showing

```html
<!-- Element visible only on certain breakpoints -->
<div class="hidden md:block">
  Show on tablet and up
</div>

<div class="block md:hidden">
  Show only on mobile
</div>

<div class="hidden lg:inline-flex items-center gap-2">
  Desktop-only layout
</div>

<!-- Applied logic:
    hidden: Hidden by default
    md:block: Shown from md breakpoint
    block md:hidden: Visible mobile, hidden from md up
-->
```

### Detection Strategy for Responsive Patterns

```bash
# Step 1: Find all responsive class prefixes used in codebase
grep -rE "(sm:|md:|lg:|xl:|2xl:)" . --include="*.html" --include="*.jsx" --include="*.tsx" | head -20

# Step 2: Identify most common breakpoint
grep -rE "(md:|lg:)" . --include="*.html" --include="*.jsx" --include="*.tsx" | cut -d: -f2 | sort | uniq -c | sort -rn

# Step 3: Check for custom breakpoints
cat tailwind.config.js | grep -A 10 "screens"

# Step 4: Analyze specific responsive patterns
grep -rE "grid-cols-1.*md:grid-cols" . --include="*.html"
grep -rE "flex-col.*md:flex-row" . --include="*.jsx"
```

### Mobile-First vs Desktop-First Detection

**Mobile-First (most common)**:
```html
<!-- Base styles apply to all sizes, breakpoints override upward -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Mobile: 1 column, Tablet: 2 columns, Desktop: 3 columns -->
</div>
```

**Desktop-First (less common)**:
```html
<!-- Base styles apply to large sizes, breakpoints override downward -->
<div class="grid lg:grid-cols-3 md:grid-cols-2 grid-cols-1">
  <!-- Desktop: 3 columns, Tablet: 2 columns, Mobile: 1 column -->
</div>
```

**Detection**:
- Mobile-first: Breakpoint prefixes increase in size (sm: → md: → lg: → xl:)
- Desktop-first: Uncommon, would have unusual ordering
- Tailwind default is mobile-first

---

## Page Layout Templates

### Template 1: Dashboard with Sidebar

**Structure**:
```html
<!-- Full-page grid with sidebar + content -->
<div class="grid grid-cols-1 lg:grid-cols-12 min-h-screen gap-6 p-6">
  <!-- Sidebar -->
  <aside class="lg:col-span-3 space-y-4">
    <nav class="flex flex-col gap-2">
      <button class="px-4 py-2 hover:bg-gray-100">Item 1</button>
      <button class="px-4 py-2 hover:bg-gray-100">Item 2</button>
    </nav>
  </aside>

  <!-- Main content -->
  <main class="lg:col-span-9 space-y-6">
    <!-- Header -->
    <header class="flex items-center justify-between bg-white rounded-lg p-4">
      <h1 class="text-2xl font-bold">Dashboard</h1>
      <button class="px-4 py-2 bg-blue-500 text-white rounded">Add</button>
    </header>

    <!-- Content grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white rounded-lg p-4">Card 1</div>
      <div class="bg-white rounded-lg p-4">Card 2</div>
    </div>
  </main>
</div>
```

**Key characteristics**:
- Sidebar and content are grid children
- `lg:col-span-3` for sidebar (3/12 on large)
- `lg:col-span-9` for content (9/12 on large)
- Full-width stacking on mobile (`grid-cols-1`)
- Internal content grids respect gap patterns
- `space-y-*` for vertical spacing between sections

**Safe addition strategy**:
```html
<!-- Adding new section to sidebar: Use flex structure -->
<aside class="lg:col-span-3 space-y-4">
  <nav class="flex flex-col gap-2">
    <button class="px-4 py-2 hover:bg-gray-100">Item 1</button>
    <button class="px-4 py-2 hover:bg-gray-100">Item 2</button>
    <button class="px-4 py-2 hover:bg-gray-100">Item 3 - NEW</button>
  </nav>
  <!-- Add new section respecting space-y-4 -->
  <div class="bg-gray-50 rounded-lg p-4">New sidebar section</div>
</aside>

<!-- Adding new card to content: Use grid structure -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div class="bg-white rounded-lg p-4">Card 1</div>
  <div class="bg-white rounded-lg p-4">Card 2</div>
  <div class="bg-white rounded-lg p-4">Card 3 - NEW</div>
</div>
```

### Template 2: Header + Content + Footer

**Structure**:
```html
<!-- Vertical stack with fixed header/footer -->
<div class="flex flex-col min-h-screen bg-gray-50">
  <!-- Fixed header -->
  <header class="bg-white border-b sticky top-0 z-10">
    <div class="px-4 md:px-6 lg:px-8 py-4 max-w-7xl mx-auto flex items-center justify-between">
      <h1 class="text-2xl font-bold">App</h1>
      <nav class="flex gap-4">
        <a class="hover:text-blue-500">Home</a>
        <a class="hover:text-blue-500">About</a>
      </nav>
    </div>
  </header>

  <!-- Flexible main content -->
  <main class="flex-1">
    <div class="px-4 md:px-6 lg:px-8 py-6 max-w-7xl mx-auto">
      <h2 class="text-xl font-bold mb-4">Page Title</h2>
      <div class="bg-white rounded-lg p-6">Content here</div>
    </div>
  </main>

  <!-- Fixed footer -->
  <footer class="bg-gray-900 text-white mt-12">
    <div class="px-4 md:px-6 lg:px-8 py-6 max-w-7xl mx-auto">
      <p>&copy; 2026 Company. All rights reserved.</p>
    </div>
  </footer>
</div>
```

**Key characteristics**:
- `flex flex-col` for vertical stacking
- `min-h-screen` ensures footer stays at bottom
- `flex-1` on main makes it grow to fill space
- `sticky top-0` on header keeps it visible while scrolling
- `z-10` ensures header stays above content
- Consistent `px-*` and `max-w-*` across sections
- `max-w-7xl` is common container width (1280px)

**Safe addition strategy**:
```html
<!-- Adding new navigation item to header -->
<nav class="flex gap-4">
  <a class="hover:text-blue-500">Home</a>
  <a class="hover:text-blue-500">About</a>
  <a class="hover:text-blue-500">New Link</a>
</nav>

<!-- Adding new content section to main -->
<main class="flex-1">
  <div class="px-4 md:px-6 lg:px-8 py-6 max-w-7xl mx-auto">
    <h2 class="text-xl font-bold mb-4">Page Title</h2>
    <div class="bg-white rounded-lg p-6">Content here</div>

    <!-- New section: Match padding and max-width of parent -->
    <div class="bg-white rounded-lg p-6 mt-6">New content section</div>
  </div>
</main>
```

### Template 3: Card Grid Layout

**Structure**:
```html
<!-- Multi-column responsive grid -->
<div class="grid gap-4 md:gap-6">
  <!-- Responsive column structure -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
    <!-- Card elements -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <h3 class="font-bold mb-2">Card Title</h3>
      <p class="text-gray-600 text-sm">Card content</p>
    </div>

    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <h3 class="font-bold mb-2">Card Title</h3>
      <p class="text-gray-600 text-sm">Card content</p>
    </div>

    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <h3 class="font-bold mb-2">Card Title</h3>
      <p class="text-gray-600 text-sm">Card content</p>
    </div>
  </div>
</div>
```

**Key characteristics**:
- `grid-cols-1` on mobile (full width)
- `sm:grid-cols-2` on small devices (2 columns)
- `lg:grid-cols-3` on large devices (3 columns)
- `gap-4 md:gap-6` for responsive spacing
- `rounded-lg shadow` for card styling
- `hover:shadow-lg` for interactive feedback
- Cards have consistent padding `p-4`

**Safe addition strategy**:
```html
<!-- Adding new card: Automatically placed in grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
  <!-- Existing cards -->
  <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
    <!-- ... -->
  </div>

  <!-- New card: Same structure -->
  <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
    <h3 class="font-bold mb-2">New Card</h3>
    <p class="text-gray-600 text-sm">New content</p>
  </div>
</div>
```

### Template 4: Two-Column Layout (Contained)

**Structure**:
```html
<!-- Max-width container with two columns -->
<div class="max-w-4xl mx-auto px-4 md:px-6 py-8">
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Left column (1/3 width on desktop) -->
    <aside class="md:col-span-1">
      <div class="sticky top-20 space-y-4">
        <div class="bg-white rounded-lg p-4 border">
          <h3 class="font-bold mb-2">Sidebar</h3>
          <ul class="space-y-2">
            <li><a class="hover:text-blue-500">Link 1</a></li>
            <li><a class="hover:text-blue-500">Link 2</a></li>
          </ul>
        </div>
      </div>
    </aside>

    <!-- Right column (2/3 width on desktop) -->
    <main class="md:col-span-2 space-y-6">
      <article class="bg-white rounded-lg p-6">
        <h2 class="text-2xl font-bold mb-4">Article Title</h2>
        <p class="text-gray-700 mb-4">Content paragraph 1</p>
        <p class="text-gray-700">Content paragraph 2</p>
      </article>
    </main>
  </div>
</div>
```

**Key characteristics**:
- `max-w-4xl` container (896px)
- `mx-auto` for centering
- Responsive padding `px-4 md:px-6`
- `grid-cols-1 md:grid-cols-3` for responsive layout
- `md:col-span-1` and `md:col-span-2` for column proportions
- `sticky top-20` on sidebar for sticky behavior
- `space-y-*` for consistent vertical spacing

---

## Container and Wrapper Patterns

### Container Width Patterns

#### Fixed Max-Width Containers (Most Common)

```html
<!-- Large container (1152px) -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Content
</div>

<!-- Medium container (896px) -->
<div class="max-w-4xl mx-auto px-4 md:px-6">
  Content
</div>

<!-- Small container (672px) -->
<div class="max-w-2xl mx-auto px-4">
  Content
</div>

<!-- XL container (1280px) -->
<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
  Content
</div>
```

**Tailwind max-width values**:
- `max-w-sm` - 384px
- `max-w-md` - 448px
- `max-w-lg` - 512px
- `max-w-xl` - 576px
- `max-w-2xl` - 672px
- `max-w-3xl` - 768px
- `max-w-4xl` - 896px
- `max-w-5xl` - 1024px
- `max-w-6xl` - 1152px
- `max-w-7xl` - 1280px

**Detection strategy**:
```bash
# Find which max-w-* values are used
grep -r "max-w-" . --include="*.html" --include="*.jsx" --include="*.tsx" | cut -d: -f2- | grep -o "max-w-[0-9a-z]*" | sort | uniq -c | sort -rn
```

**Safe addition strategy**:
```html
<!-- If adding to existing container: Use same max-w-* -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Existing content

  <!-- New content: Don't change the max-w-* value -->
  <div class="mt-6">New section respecting same max-width</div>
</div>

<!-- If adding new container: Match existing max-w-* in codebase -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  New container with same width as others
</div>
```

#### Full-Width Containers

```html
<!-- Full width with side padding -->
<div class="w-full px-4 md:px-6 lg:px-8">
  Content takes full width with responsive padding
</div>

<!-- Full width with background color -->
<div class="w-full bg-blue-50">
  <div class="px-4 md:px-6 lg:px-8 max-w-6xl mx-auto">
    Content with inner max-width
  </div>
</div>

<!-- Full width viewport height -->
<div class="w-full h-screen flex items-center justify-center">
  Hero section or large feature area
</div>
```

### Padding Patterns

#### Responsive Padding (Standard)

```html
<!-- Padding increases with screen size -->
<div class="px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8">
  Content with responsive padding
</div>

<!-- Logic:
    Mobile (< 768px): px-4 py-4 (16px)
    Tablet (≥ 768px): md:px-6 md:py-6 (24px)
    Desktop (≥ 1024px): lg:px-8 lg:py-8 (32px)
-->
```

#### Consistent Padding Values

```html
<!-- Cards with consistent internal padding -->
<div class="bg-white rounded-lg p-4 md:p-6">
  Card content
</div>

<!-- Padding options: p-2, p-3, p-4, p-6, p-8 -->
<!-- Patterns:
    p-4: Standard card/section padding
    p-6: Generous spacing
    p-2: Compact elements
-->
```

#### Section Spacing Patterns

```html
<!-- Vertical spacing between sections -->
<div class="space-y-6">
  <section class="bg-white rounded-lg p-6">Section 1</section>
  <section class="bg-white rounded-lg p-6">Section 2</section>
  <section class="bg-white rounded-lg p-6">Section 3</section>
</div>

<!-- Using space-y-* (gap between children):
    space-y-2: 8px gap
    space-y-4: 16px gap (common)
    space-y-6: 24px gap (generous)
    space-y-8: 32px gap (very generous)
-->
```

### Safe Container Addition

```html
<!-- WRONG: Inconsistent max-width -->
<div class="max-w-6xl mx-auto">
  <!-- Existing content using max-w-6xl -->
</div>
<div class="max-w-4xl mx-auto">
  <!-- Adding new section with different max-width = layout break -->
</div>

<!-- CORRECT: Consistent max-width -->
<div class="max-w-6xl mx-auto">
  <!-- Existing content using max-w-6xl -->
</div>
<div class="max-w-6xl mx-auto">
  <!-- New section uses same max-width = layout preserved -->
</div>

<!-- WRONG: Inconsistent padding -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Existing section
</div>
<div class="max-w-6xl mx-auto px-8">
  <!-- Adding section with only px-8 missing responsive values = mobile breaks -->
</div>

<!-- CORRECT: Consistent padding -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Existing section
</div>
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  <!-- New section matches padding pattern exactly -->
</div>
```

---

## Overflow and Scrolling Patterns

### Scroll Container Patterns

#### Horizontal Scrolling (Tables, Carousels)

```html
<!-- Horizontal scroll container -->
<div class="overflow-x-auto">
  <table class="w-full">
    <!-- Wide table that scrolls horizontally on small screens -->
  </table>
</div>

<!-- Horizontal scrolling content -->
<div class="overflow-x-auto">
  <div class="flex gap-4">
    <div class="flex-shrink-0 w-96">Card 1</div>
    <div class="flex-shrink-0 w-96">Card 2</div>
    <div class="flex-shrink-0 w-96">Card 3</div>
  </div>
</div>
```

**Key elements**:
- `overflow-x-auto` enables horizontal scrolling
- `flex-shrink-0` prevents flex items from shrinking
- Fixed widths (`w-96`) maintain card size
- Only appears on small screens if parent is constrained

#### Vertical Scrolling (Modals, Sidebars)

```html
<!-- Vertical scroll container -->
<div class="overflow-y-auto max-h-screen">
  Long content that scrolls vertically
</div>

<!-- Modal with scrollable body -->
<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg w-full max-w-2xl max-h-screen flex flex-col">
    <!-- Fixed header -->
    <div class="px-6 py-4 border-b flex-shrink-0">
      <h2 class="text-xl font-bold">Modal Title</h2>
    </div>

    <!-- Scrollable content -->
    <div class="px-6 py-4 overflow-y-auto flex-1">
      Long content area
    </div>

    <!-- Fixed footer -->
    <div class="px-6 py-4 border-t flex-shrink-0 flex gap-2">
      <button>Cancel</button>
      <button>Save</button>
    </div>
  </div>
</div>
```

**Key characteristics**:
- `overflow-y-auto` enables vertical scrolling
- `max-h-screen` prevents container from exceeding viewport
- `flex flex-col` for three-part structure
- `flex-shrink-0` on header/footer keeps them fixed
- `flex-1` on content allows it to scroll

#### No Scrolling (Overflow Hidden)

```html
<!-- Content clipped without scrollbars -->
<div class="overflow-hidden max-h-48">
  Content that gets clipped at max-height
</div>

<!-- Text truncation -->
<p class="truncate">Long text that gets cut off with ellipsis...</p>

<!-- Multi-line truncation -->
<p class="line-clamp-3">
  Long text that shows only 3 lines with ellipsis at end...
</p>
```

### Sticky Positioning Patterns

#### Sticky Header

```html
<!-- Header stays fixed while scrolling content below -->
<header class="sticky top-0 bg-white border-b z-10">
  <div class="px-6 py-4 flex items-center justify-between">
    <h1 class="text-2xl font-bold">Page Title</h1>
    <button>Action</button>
  </div>
</header>

<!-- Content scrolls under sticky header -->
<main class="p-6">
  Long content...
</main>
```

**Key elements**:
- `sticky` enables sticky positioning
- `top-0` positions it at top of scroll container
- `z-10` keeps it above content
- `bg-white` ensures it covers underlying content

#### Sticky Sidebar

```html
<!-- Three-column layout with sticky sidebar -->
<div class="flex gap-6">
  <!-- Sticky sidebar -->
  <aside class="w-64 flex-shrink-0">
    <div class="sticky top-20 space-y-4">
      <!-- Navigation items -->
    </div>
  </aside>

  <!-- Main content -->
  <main class="flex-1">
    Long scrolling content...
  </main>

  <!-- Sticky right column -->
  <aside class="w-48 flex-shrink-0">
    <div class="sticky top-20 space-y-4">
      <!-- Secondary items -->
    </div>
  </aside>
</div>
```

**Key elements**:
- `w-64 flex-shrink-0` fixed sidebar width
- `sticky top-20` accounting for header height
- Multiple sticky elements with same `top-20` spacing

### Preventing Overflow Issues

```html
<!-- WRONG: Content breaks out of container -->
<div class="w-full px-4">
  <div class="w-full">
    <!-- This div is w-full inside parent that's already constrained -->
    <!-- Creates horizontal scrollbar if content is wide -->
  </div>
</div>

<!-- CORRECT: Respect container constraints -->
<div class="w-full px-4">
  <div class="w-full max-w-full">
    <!-- Content respects parent width -->
  </div>
</div>

<!-- WRONG: Absolute positioning causes overlap -->
<div class="relative">
  <div class="absolute top-0 left-0 right-0">
    <!-- This overlaps all content below -->
  </div>
  <div class="mt-0">
    <!-- Gets overlapped by absolute element -->
  </div>
</div>

<!-- CORRECT: Absolute with z-index and proper structure -->
<div class="relative">
  <div class="absolute top-0 left-0 right-0 z-50 bg-white">
    <!-- Properly layered with z-index -->
  </div>
  <div class="pt-16">
    <!-- Padding accounts for absolute element -->
  </div>
</div>
```

---

## Common Layout Breakages

### Breakage 1: Adding Element Outside Grid

**Problem**:
```html
<!-- Existing layout: 3-column grid -->
<div class="grid grid-cols-3 gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- WRONG: Adding element that breaks grid -->
<div class="grid grid-cols-3 gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <div class="w-full">New item - BREAKS GRID ALIGNMENT</div>
</div>

<!-- Why it breaks:
    - New item isn't a grid child
    - Takes full width, pushing items around
    - Inconsistent with grid-cols-3 pattern
    - Creates layout instability
-->
```

**Solution**:
```html
<!-- CORRECT: Respect grid structure -->
<div class="grid grid-cols-3 gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <!-- New item is a grid child -->
  <div>Item 4 - fits in grid</div>
</div>

<!-- If item needs to span full width -->
<div class="grid grid-cols-3 gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <!-- Use col-span-3 for full width in 3-column grid -->
  <div class="col-span-3 bg-blue-50">New item spanning full width</div>
</div>
```

### Breakage 2: Inconsistent Responsive Breakpoints

**Problem**:
```html
<!-- Existing responsive pattern -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>

<!-- WRONG: Adding inconsistent responsive pattern -->
<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
  <!-- Uses different base (grid-cols-2 vs grid-cols-1) -->
  <!-- Uses different breakpoint (lg vs md) -->
  <!-- Creates inconsistent experience across app -->
</div>

<!-- Why it breaks on mobile:
    - First grid: 1 column on mobile (correct stacking)
    - Second grid: 2 columns on mobile (awkward narrow columns)
    - User sees inconsistent mobile experience
-->
```

**Solution**:
```html
<!-- CORRECT: Match existing responsive pattern -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>

<!-- New grid uses same pattern -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div>Card 4</div>
  <div>Card 5</div>
  <div>Card 6</div>
</div>

<!-- Consistent across all screen sizes and patterns -->
```

### Breakage 3: Breaking Sidebar/Content Proportions

**Problem**:
```html
<!-- Existing layout: 25% sidebar, 75% content -->
<div class="flex gap-6">
  <aside class="w-1/4">Sidebar</aside>
  <main class="flex-1">Content</main>
</div>

<!-- WRONG: Adding fixed-width element that changes proportions -->
<div class="flex gap-6">
  <aside class="w-1/4">Sidebar</aside>
  <main class="flex-1">Content</main>
  <div class="w-80">New sidebar - changes proportions</div>
</div>

<!-- Why it breaks:
    - Original: Sidebar takes 25%, main takes 75%
    - Modified: New div takes fixed 320px, shrinking main content
    - Proportions broken, main content cramped
    - Layout not responsive on smaller screens
-->
```

**Solution**:
```html
<!-- CORRECT: Respect existing proportions -->
<div class="flex gap-6">
  <aside class="w-1/4">Original sidebar</aside>
  <main class="flex-1">Content</main>
</div>

<!-- If adding content to sidebar: Add within sidebar -->
<div class="flex gap-6">
  <aside class="w-1/4 space-y-4">
    <div>Original sidebar content</div>
    <div>New sidebar content</div>
  </aside>
  <main class="flex-1">Content</main>
</div>

<!-- If truly adding new column: Use grid with explicit columns -->
<div class="grid grid-cols-12 gap-6">
  <aside class="col-span-3">Sidebar (25%)</aside>
  <main class="col-span-6">Content (50%)</main>
  <aside class="col-span-3">New sidebar (25%)</aside>
</div>
```

### Breakage 4: Introducing Different Container Widths

**Problem**:
```html
<!-- Existing containers use max-w-6xl -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Section 1 (max 1152px)
</div>

<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Section 2 (max 1152px)
</div>

<!-- WRONG: Adding section with different max-width -->
<div class="max-w-4xl mx-auto px-4 md:px-6 lg:px-8">
  <!-- Different max-width (896px) than others -->
  <!-- Creates inconsistent left/right margins -->
  <!-- Looks misaligned with sections above -->
</div>

<!-- Why it breaks:
    - Section 1-2: Edge alignment at 1152px
    - Section 3: Edges at 896px (narrower)
    - Asymmetrical margins on left/right
    - Looks broken and unprofessional
-->
```

**Solution**:
```html
<!-- CORRECT: Consistent container widths -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Section 1
</div>

<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Section 2
</div>

<!-- New section uses same max-width -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  Section 3 - NEW
</div>

<!-- All sections have consistent edge alignment -->
```

### Breakage 5: Adding Fixed/Absolute Elements Without Z-Index

**Problem**:
```html
<!-- Existing layout with scrollable content -->
<main class="overflow-y-auto">
  <section class="p-6">Content section 1</section>
  <section class="p-6">Content section 2</section>
</main>

<!-- WRONG: Adding absolute element without z-index -->
<main class="overflow-y-auto">
  <div class="absolute top-20 left-0 w-full bg-red-500">
    Alert message (gets hidden behind content)
  </div>
  <section class="p-6">Content section 1</section>
  <section class="p-6">Content section 2</section>
</main>

<!-- Why it breaks:
    - Absolute element has no z-index
    - Content scrolls over it
    - Alert is unreadable
    - User can't interact with it
-->
```

**Solution**:
```html
<!-- CORRECT: Fixed element with proper z-index -->
<main class="overflow-y-auto">
  <!-- Fixed alert with high z-index -->
  <div class="fixed top-20 left-0 w-full bg-red-500 z-50 p-4">
    Alert message (always visible)
  </div>

  <!-- Content has padding-top to avoid overlap -->
  <div class="pt-20">
    <section class="p-6">Content section 1</section>
    <section class="p-6">Content section 2</section>
  </div>
</main>

<!-- Or use sticky positioning for scroll-relative elements -->
<main>
  <div class="sticky top-0 bg-red-500 z-10 p-4">
    Alert message (sticks to top while scrolling)
  </div>
  <section class="p-6">Content section 1</section>
  <section class="p-6">Content section 2</section>
</main>
```

### Breakage 6: Breaking Natural Document Flow

**Problem**:
```html
<!-- Existing layout with proper flow -->
<div class="space-y-6">
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 1</h2>
  </div>
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 2</h2>
  </div>
</div>

<!-- WRONG: Adding float or absolute that breaks flow -->
<div class="space-y-6">
  <div class="float-right w-1/3">
    <!-- This floated element breaks space-y-6 spacing -->
    <!-- Content flows around it unpredictably -->
  </div>
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 1</h2>
  </div>
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 2</h2>
  </div>
</div>

<!-- Why it breaks:
    - Float removes element from normal flow
    - space-y-6 doesn't account for floated element
    - Content wraps around float awkwardly
    - Layout is unpredictable
-->
```

**Solution**:
```html
<!-- CORRECT: Maintain natural flow with grid/flex -->
<div class="space-y-6">
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 1</h2>
  </div>
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 2</h2>
  </div>
  <!-- New element respects space-y-6 -->
  <div class="bg-white p-6 rounded-lg">
    <h2>Section 3 - NEW</h2>
  </div>
</div>

<!-- Or use grid for side-by-side layout preserving flow -->
<div class="grid grid-cols-3 gap-6">
  <div class="col-span-2 bg-white p-6 rounded-lg">
    <h2>Main content</h2>
  </div>
  <div class="col-span-1 bg-white p-6 rounded-lg">
    <h2>Sidebar</h2>
  </div>
</div>
```

---

## Detection Methods

### Method 1: Automated Pattern Scanning

```bash
#!/bin/bash
# Scan for all grid patterns in codebase

echo "=== Grid Patterns ==="
grep -r "class=\"grid" . --include="*.html" --include="*.jsx" --include="*.tsx" | \
  cut -d: -f2- | \
  grep -o "grid[^\"]*" | \
  sort | uniq -c | sort -rn | head -10

echo -e "\n=== Grid Column Configurations ==="
grep -rE "grid-cols-[0-9]+" . --include="*.html" --include="*.jsx" --include="*.tsx" | \
  grep -o "grid-cols-[0-9]*" | \
  sort | uniq -c | sort -rn

echo -e "\n=== Gap Patterns ==="
grep -rE "gap-[0-9x-]+" . --include="*.html" --include="*.jsx" --include="*.tsx" | \
  grep -o "gap[^ \"]*" | \
  sort | uniq -c | sort -rn

echo -e "\n=== Flex Patterns ==="
grep -r "class=\"flex" . --include="*.html" --include="*.jsx" --include="*.tsx" | \
  cut -d: -f2- | \
  grep -o "flex[^\"]*" | \
  sort | uniq -c | sort -rn | head -10

echo -e "\n=== Responsive Breakpoints ==="
grep -rE "(sm:|md:|lg:|xl:|2xl:)" . --include="*.html" --include="*.jsx" --include="*.tsx" | \
  grep -o "[a-z]*:[a-z-]*" | \
  cut -d: -f1 | \
  sort | uniq -c | sort -rn
```

### Method 2: Manual Code Review Checklist

When adding new elements, review:

```
GRID STRUCTURES
- [ ] Identify parent grid's grid-cols-* value
- [ ] Check if element spans correct number of columns
- [ ] Verify gap matches parent gap-*
- [ ] Ensure col-span-* values are appropriate
- [ ] Check responsive grid-cols-* at each breakpoint

FLEXBOX STRUCTURES
- [ ] Identify parent flex's flex-col/flex-row
- [ ] Check justify-* and items-* alignment
- [ ] Verify gap-* matches parent gap
- [ ] Ensure flex-1/flex-none sizing is appropriate
- [ ] Check for flex-shrink-0 on fixed-width children

RESPONSIVE PATTERNS
- [ ] Base styles apply to mobile (< 640px)
- [ ] sm:* overrides at 640px+
- [ ] md:* overrides at 768px+
- [ ] lg:* overrides at 1024px+
- [ ] Consistent breakpoint usage across app

CONTAINER PATTERNS
- [ ] Identify max-w-* value of existing containers
- [ ] Use same max-w-* for new containers
- [ ] Verify px-* padding is responsive
- [ ] Check mx-auto centering

OVERFLOW HANDLING
- [ ] Identify if parent has overflow-auto/overflow-hidden
- [ ] Check for scroll containers
- [ ] Verify sticky positioning top-* values
- [ ] Ensure z-index is appropriate for layering
```

### Method 3: Browser DevTools Inspection

```javascript
// In browser console, detect layout structure
(function() {
  // Find grid containers
  const grids = document.querySelectorAll('[class*="grid"]');
  const gridPatterns = {};

  grids.forEach(grid => {
    const gridCols = Array.from(grid.classList)
      .find(cls => cls.startsWith('grid-cols-'));
    const gap = Array.from(grid.classList)
      .find(cls => cls.startsWith('gap-'));

    if (gridCols || gap) {
      const pattern = `${gridCols || 'default'} ${gap || 'no-gap'}`;
      gridPatterns[pattern] = (gridPatterns[pattern] || 0) + 1;
    }
  });

  console.table(gridPatterns);

  // Find flex containers
  const flexes = document.querySelectorAll('[class*="flex"]');
  const flexPatterns = {};

  flexes.forEach(flex => {
    const direction = Array.from(flex.classList)
      .find(cls => cls.includes('flex-col') || cls.includes('flex-row')) || 'flex-row';
    const align = Array.from(flex.classList)
      .find(cls => cls.startsWith('items-')) || 'default';

    const pattern = `${direction} ${align}`;
    flexPatterns[pattern] = (flexPatterns[pattern] || 0) + 1;
  });

  console.table(flexPatterns);
})();
```

---

## Safe Implementation Practices

### Practice 1: Copy Existing Components

**Instead of creating new:**
```html
<!-- DANGEROUS: Creating new component structure -->
<div class="w-11/12 p-5 mx-auto border rounded">
  New card with inconsistent styling
</div>
```

**Copy existing:**
```html
<!-- SAFE: Copy exact structure from existing card -->
<!-- From inspection of existing cards in codebase -->
<div class="max-w-6xl mx-auto px-4 md:px-6 lg:px-8">
  <!-- Copy this structure -->
  <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
    New card with identical styling
  </div>
</div>
```

### Practice 2: Test at Multiple Breakpoints

```html
<!-- After adding element, test at all breakpoints -->
<!-- Mobile: 375px - 600px -->
<!-- Tablet: 768px - 1024px -->
<!-- Desktop: 1280px+ -->

<!-- Example: Create in isolation, test responsiveness -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Test that:
       - Mobile: 1 column (full width, scrollable)
       - Tablet: 2 columns (fits screen)
       - Desktop: 3 columns (optimal spacing)
  -->
</div>
```

### Practice 3: Document Expected Behavior

```html
<!-- When adding complex layout, document it -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
  <!-- Layout:
       - Mobile: 1 column, gap-4 (16px)
       - Desktop: 3 columns, gap-6 (24px)
       - Container: max-w-6xl (1152px), centered
       - Cards: Use existing card component
  -->
  <div class="bg-white rounded-lg p-4 shadow">Card</div>
</div>
```

### Practice 4: Validate Against App Design System

Before adding layout:

```
VALIDATION CHECKLIST
- [ ] Grid columns match existing grids (1, 2, 3, 4, 6, or 12)
- [ ] Gaps match existing gaps (4, 6, or 8)
- [ ] Container max-width matches existing (6xl, 7xl, etc.)
- [ ] Padding breakpoints match existing (px-4 md:px-6 lg:px-8)
- [ ] Responsive breakpoints match (md: and lg: are standard)
- [ ] No new width values introduced
- [ ] No new gap values introduced
- [ ] No new breakpoints introduced
- [ ] Sticky/fixed positioning has proper z-index
- [ ] Overflow behavior matches parent
```

### Practice 5: Communicate Layout Dependencies

```
BEFORE ADDING FEATURE:
"I'll add this feature by:
1. Using the existing grid-cols-3 pattern
2. Matching the gap-6 spacing
3. Placing within max-w-6xl container
4. Using md: for responsive breakpoints (matching existing pattern)
5. Testing on mobile/tablet/desktop before deploying"

AVOID:
"I'll create a modern responsive layout"
"I'll style it however looks best"
"I'll use the latest layout practices"
```

---

## Conclusion

Layout and responsive design preservation requires:

1. **Pattern Detection**: Identify existing grid/flex patterns before adding elements
2. **Consistency**: Match existing container widths, gaps, and padding exactly
3. **Responsive Testing**: Verify behavior at all breakpoints (mobile, tablet, desktop)
4. **Defensive Addition**: Copy existing patterns rather than creating new ones
5. **Documentation**: Record what layout patterns are used and why

The key principle: **When adding features, copy the exact layout structure of nearby elements rather than creating new layout patterns.**

This prevents the common breakages that degrade user experience and creates code that is maintainable, consistent, and reliable across all devices.
