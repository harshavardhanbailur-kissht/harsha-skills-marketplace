# UI Consistency Enforcement Reference

**Purpose:** Guidelines for maintaining visual and structural consistency across UI changes in Tailwind/React applications.

**Key Principle:** Never introduce new design elements without matching existing patterns first.

---

## 1. Color Consistency Rules

### 1.1 Extract the Blessed Palette

Before any color changes, identify all colors currently in use:

```bash
# Search Tailwind config for defined colors
grep -A 50 "colors:" tailwind.config.js

# Search CSS variables in index.css or globals.css
grep "color\|--" index.css | grep -E ":(.*#|rgb|hsl)"

# Search for inline Tailwind color classes
grep -r "bg-\|text-\|border-" src/ | grep -oE "(bg|text|border)-(gray|amber|ring|purple|green|blue)-[0-9]{1,3}" | sort -u
```

### 1.2 Document the Blessed Palette

Create a single source of truth (Example from Project 1):

```javascript
// BLESSED PALETTE - Ring Kissht Issue Tracker
// Status Colors (non-negotiable):
// - Pending:     amber-100, amber-800
// - In Progress: ring-100, ring-800
// - Forwarded:   purple-100, purple-800
// - Resolved:    green-100, green-800

// Background Colors:
// - Primary backgrounds: ring-50, ring-200, ring-900
// - Secondary: gray-50, gray-100, gray-200, gray-900
// - White surfaces: white (not gray-50 for cards)

// Text Colors:
// - Primary text: gray-900
// - Secondary text: gray-600
// - Muted text: gray-500
// - Accent text: ring-700
```

### 1.3 When Adding New UI: Match Before Creating

**WRONG** - Introducing new colors:
```tsx
// DO NOT do this:
<div className="bg-blue-100 border-blue-300">
  {/* Blue was never used in the app */}
</div>
```

**RIGHT** - Search existing components first:
```tsx
// 1. Search for similar card/badge patterns:
grep -r "bg-.*-50.*border-.*-200" src/

// 2. Found this in StatusBadge.tsx:
const statusConfig = {
  pending: { bg: 'bg-amber-100', border: 'border-amber-200' }
};

// 3. Copy the exact pattern:
<div className="bg-amber-100 border border-amber-200">
  {/* Reuses existing blessed color pairs */}
</div>
```

### 1.4 Color Pair Rules

Colors come in validated sets. From Project 1 research:

```
Background + Border + Text pairs (blessed sets):
- amber-100   + amber-200   + amber-800 (warning/pending)
- ring-100    + ring-200    + ring-800  (primary/in-progress)
- purple-100  + purple-200  + purple-800 (forwarded)
- green-100   + green-200   + green-800 (success/resolved)
- gray-50     + gray-200    + gray-900  (neutral)
```

**Never mix pairs:**
```tsx
// WRONG:
<div className="bg-amber-100 border-gray-200 text-ring-800">

// RIGHT:
<div className="bg-amber-100 border-amber-200 text-amber-800">
```

---

## 2. Component Pattern Matching

### 2.1 Inventory Existing Components

Before building any UI element, find the existing version:

```bash
# Find all Button components
find src/ -name "*Button*" -o -name "*button*"

# Find all Card components
find src/ -name "*Card*" -o -name "*card*"

# Find form elements
find src/ -name "*Input*" -o -name "*Form*" -o -name "*Field*"
```

### 2.2 Extract Component Pattern

From Project 1 research, StatCard broken pattern:

```tsx
// PROBLEM: StatCard exists inline, doesn't use .card CSS pattern
function StatCard({ label, value, color }) {
  return (
    <div className={`rounded-lg border p-4 ${colorClasses[color]}`}>
      {/* Independent implementation, not coordinated */}
    </div>
  );
}
```

**Solution:**
```tsx
// 1. Identify that .card CSS pattern exists:
// CSS: .card { @apply bg-white rounded-lg border border-gray-200 shadow-card; }

// 2. Use it consistently:
function StatCard({ label, value, color }) {
  return (
    <div className={`card ${colorClasses[color]}`}>
      {/* Now uses blessed CSS component */}
    </div>
  );
}

// 3. If component library exists (shadcn, radix), use it EXCLUSIVELY:
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function StatCard() {
  return (
    <Card>
      <CardHeader>...</CardHeader>
      <CardContent>...</CardContent>
    </Card>
  );
}
```

### 2.3 Copy Exact className Patterns

When no component exists, replicate the className pattern exactly:

```tsx
// Found this button in ProductSupportDashboard.tsx:
<button className="inline-flex items-center gap-2 px-4 py-2
  bg-ring-700 text-white font-semibold rounded-md
  hover:bg-ring-800 focus:ring-2 focus:ring-ring-500">
  Save
</button>

// NEW button in another page - COPY EXACTLY:
<button className="inline-flex items-center gap-2 px-4 py-2
  bg-ring-700 text-white font-semibold rounded-md
  hover:bg-ring-800 focus:ring-2 focus:ring-ring-500">
  Create
</button>

// NOT this variation:
<button className="px-4 py-2 bg-ring-700 text-white rounded hover:bg-ring-800">
  {/* Missing: items-center, gap-2, font-semibold, focus states */}
</button>
```

---

## 3. Typography & Spacing Consistency

### 3.1 Extract Typography Scale

From Project 1 research (BROKEN):
```
Inconsistent H1 usage:
- ProductSupportDashboard: text-2xl
- SubmissionsListPage:     text-3xl
```

**Extract blessed scale:**

```bash
# Find all heading sizes
grep -r "text-[0-9]xl" src/ | grep -oE "text-[0-9]xl" | sort -u

# Find all font-weights
grep -r "font-\(bold\|semibold\|medium\|normal\)" src/ | grep -oE "font-[a-z]+" | sort -u
```

**Document the scale:**
```javascript
// BLESSED TYPOGRAPHY SCALE
// Headings follow 1.2x multiplier:
// H1: text-3xl font-bold      (30px)
// H2: text-2xl font-bold      (24px)
// H3: text-xl font-semibold   (20px)
// Body: text-base font-normal (16px)
// Small: text-sm font-normal  (14px)
// Tiny: text-xs font-normal   (12px)

// Text colors (semantic hierarchy):
// - Primary text: text-gray-900
// - Secondary text: text-gray-600
// - Muted text: text-gray-500
```

### 3.2 Enforce Hierarchy Matching

```tsx
// WRONG - breaks hierarchy:
<h1 className="text-2xl font-bold">Dashboard</h1>
<h2 className="text-lg font-medium">Submissions</h2>  {/* Should be text-xl */}
<p className="text-base">Description</p>

// RIGHT - follows blessed scale:
<h1 className="text-3xl font-bold">Dashboard</h1>
<h2 className="text-2xl font-bold">Submissions</h2>
<p className="text-base text-gray-600">Description</p>
```

### 3.3 Extract Spacing System

From Project 1 research (BROKEN):
```
Inconsistent gaps: gap-1, gap-2, gap-3, gap-4, gap-6
Inconsistent margins: mb-1.5, mb-2, mb-3, mb-4, mb-6, mb-8, mb-12
```

**Extract blessed spacing:**

```bash
# Find all spacing values
grep -r "gap-\|mb-\|mt-\|px-\|py-" src/ | \
  grep -oE "(gap|mb|mt|px|py)-([\d.]+)" | sort -u
```

**Document the scale:**
```javascript
// BLESSED SPACING SCALE (4px base unit)
// 4px:  use -1    (only for tight spacing)
// 8px:  use -2    (subtle gaps)
// 12px: use -3    (medium gaps)
// 16px: use -4    (default gap/padding)
// 20px: use -5    (uncommon)
// 24px: use -6    (large gaps)
// 32px: use -8    (section gaps)

// In practice:
const blessedSpacing = ['gap-2', 'gap-3', 'gap-4', 'gap-6'];
const blessedMargin = ['mb-4', 'mb-6', 'mb-8', 'mt-4', 'mt-6'];
const blessedPadding = ['p-4', 'px-4', 'py-2', 'p-6'];
```

---

## 4. Form Pattern Consistency

### 4.1 Extract Form Pattern

From Project 1 research (BROKEN - duplicated across pages):
```tsx
// ProductSupportDashboard.tsx:
<input
  className="w-full h-10 px-3 text-sm border border-gray-300 rounded-md
             focus:ring-2 focus:ring-ring-500 focus:border-transparent outline-none"
/>

// SubmissionsListPage.tsx: (identical duplication)
<input
  className="w-full h-10 px-3 text-sm border border-gray-300 rounded-md
             focus:ring-2 focus:ring-ring-500 focus:border-transparent outline-none"
/>
```

**Problem:** Changes require updating multiple files. **Solution:** Extract to component:

```tsx
// components/Input.tsx
export function Input(props) {
  return (
    <input
      className="w-full h-10 px-3 text-sm border border-gray-300 rounded-md
                 focus:ring-2 focus:ring-ring-500 focus:border-transparent outline-none"
      {...props}
    />
  );
}

// All pages:
import { Input } from '@/components/Input';
export function MyForm() {
  return <Input placeholder="Enter text" />;
}
```

### 4.2 Form Label + Input + Error Pattern

```tsx
// BLESSED form pattern (extract from one working form):
<div className="mb-4">
  <label className="block text-sm font-medium text-gray-900 mb-2">
    Field Label
  </label>
  <input
    className="w-full h-10 px-3 text-sm border border-gray-300 rounded-md
               focus:ring-2 focus:ring-ring-500 focus:border-transparent outline-none"
  />
  {error && (
    <p className="text-xs text-red-600 mt-1">{error}</p>
  )}
</div>
```

**Use consistently:**
```tsx
// All forms must follow this exact pattern
// Same label styling, input height, error message color, spacing
```

### 4.3 Validation Feedback Pattern

```tsx
// BLESSED: Find how one form shows validation
// Example patterns:
// - Inline error under input: text-xs text-red-600 mt-1
// - Toast notification: using existing toast component
// - Border highlight: focus:ring-2 focus:ring-red-500
// - Success state: border-green-500, text-green-600

// When adding form validation, match the pattern exactly:
{error && <p className="text-xs text-red-600 mt-1">{error}</p>}  // NOT: text-sm, NOT: mt-2
```

---

## 5. Post-Change Visual Consistency Check

### 5.1 Verify No New Colors Introduced

After making UI changes, verify against blessed palette:

```bash
# Find all color classes in changed files
grep -r "bg-\|text-\|border-" src/pages/YourChangedPage.tsx | \
  grep -oE "(bg|text|border)-(gray|amber|ring|purple|green|blue)-[0-9]{1,3}" | sort -u

# Compare against blessed palette (documented in step 1.2)
# If you see colors NOT in the blessed list, REVERT them:
# WRONG: bg-blue-100 (if blue not blessed)
# RIGHT: bg-ring-100 (use blessed alternative)
```

### 5.2 Verify Component Pattern Usage

```bash
# Search for new inline styling (suspicious):
grep -r "style={{" src/pages/YourChangedPage.tsx

# If found, convert to className or component:
// WRONG:
<div style={{ backgroundColor: '#fff', padding: '16px' }}>

// RIGHT:
<div className="bg-white p-4">
// OR
import { Card } from '@/components/Card';
<Card>...</Card>
```

### 5.3 Verify Heading Hierarchy Maintained

```bash
# Check all heading sizes in changed files:
grep -r "<h[1-6]" src/pages/YourChangedPage.tsx

# Compare against blessed scale from step 3.1:
// Check: Does H2 use text-2xl? (not text-xl or text-3xl)
// Check: Is H3 smaller than H2?
// Check: Do all headings match the documented multiplier ratio?
```

### 5.4 Verify Form Elements Match Pattern

```bash
# Find all input elements:
grep -r "<input\|<select\|<textarea" src/pages/YourChangedPage.tsx

# Check:
// - All use same blessed className pattern?
// - All have same height (h-10)?
// - All have same border color (border-gray-300)?
// - All have same focus ring (focus:ring-ring-500)?
// - Error messages use text-xs text-red-600?
```

### 5.5 Automated Consistency Check

```bash
# Create a pre-commit script:
#!/bin/bash
# Check for non-blessed colors
if grep -r "bg-\|text-\|border-" src/ | \
   grep -E "(bg|text|border)-(cyan|indigo|lime|sky|slate)-[0-9]{1,3}"; then
  echo "ERROR: Non-blessed colors detected. Use only: gray, amber, ring, purple, green"
  exit 1
fi

# Check for inline styles
if grep -r "style={{" src/; then
  echo "ERROR: Inline styles found. Use Tailwind classes instead."
  exit 1
fi

# Check for duplicate form patterns
if diff <(grep -A5 "className.*border-gray-300" src/pages/PageA.tsx) \
        <(grep -A5 "className.*border-gray-300" src/pages/PageB.tsx) > /dev/null; then
  echo "WARNING: Duplicate form patterns. Consider extracting to component."
fi
```

---

## 6. Quick Reference Checklist

**Before adding any new UI:**

- [ ] Found existing component/pattern of same type?
- [ ] Copied exact className from existing element?
- [ ] Color pair from blessed palette?
- [ ] Typography size matches hierarchy scale?
- [ ] Spacing from blessed spacing values?
- [ ] Form elements use extracted form component?
- [ ] No inline `style={}` attributes?
- [ ] No new Tailwind classes outside blessed list?

**After changes:**

- [ ] Ran color consistency check (no new color values)?
- [ ] Verified components use blessed patterns?
- [ ] Verified heading hierarchy maintained?
- [ ] Verified form elements match pattern?
- [ ] Checked adjacent elements still align visually?

