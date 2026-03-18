# Accessibility (A11y) Preservation Reference
## Preventing Breaking Changes in Accessible Applications

**Document Purpose**: This reference guide helps Claude detect and preserve existing accessibility patterns when modifying or adding features to applications. It focuses on detecting what's already accessible and matching those patterns exactly, rather than introducing new (potentially conflicting) accessibility implementations.

**Critical Principle**: When adding features to an existing accessible application, match the EXACT accessibility patterns already in use. Do not introduce new accessibility libraries, patterns, or approaches unless the application explicitly uses them.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [WCAG 2.2 Compliance Requirements](#wcag-22-compliance-requirements)
3. [Detection Methods: Finding Existing Accessibility](#detection-methods)
4. [ARIA Pattern Preservation](#aria-pattern-preservation)
5. [Keyboard Navigation Preservation](#keyboard-navigation-preservation)
6. [Focus Management Patterns](#focus-management-patterns)
7. [Screen Reader Compatibility](#screen-reader-compatibility)
8. [Visual Accessibility Preservation](#visual-accessibility-preservation)
9. [Common Accessibility Breakage Patterns](#common-accessibility-breakages)
10. [Component-Specific Pattern Matching](#component-specific-patterns)
11. [Testing & Validation Strategies](#testing-validation)
12. [Quick Reference Checklist](#quick-reference-checklist)

---

## Executive Summary

### The A11y Preservation Problem

When adding features to an accessible application, developers frequently:
- **Remove existing ARIA attributes** during UI refactoring
- **Break focus management** by adding modals or components without focus traps
- **Ignore keyboard navigation requirements** on new interactive elements
- **Create inconsistent patterns** by using different accessibility approaches than existing code
- **Introduce heading hierarchy violations** by inserting new content
- **Add unlabeled buttons or form inputs** when existing UI has proper labels

### The Solution: Pattern Detection & Matching

Rather than implementing accessibility from scratch:
1. **Detect** what accessibility patterns exist in the codebase
2. **Document** the exact patterns used (ARIA attributes, focus management approach, keyboard handlers)
3. **Match** those patterns exactly in new features
4. **Validate** that new code follows the same approach

### Legal & Business Context

- **WCAG 2.2** is the current W3C standard (October 2023)
- **EU Accessibility Act** is now enforceable (June 2025)
- **ADA Title II enforcement** begins April 2026
- **Lawsuit volume** increased 37% in 2025
- **Overlay tools** (AccessiBe, AudioEye) do NOT provide legal compliance

---

## WCAG 2.2 Compliance Requirements

### Conformance Levels
- **Level A**: Basic minimum accessibility
- **Level AA**: Recommended standard for most web applications
- **Level AAA**: Enhanced accessibility (optional, specialized use cases)

### Critical WCAG 2.2 Success Criteria

#### **Perception (Accessible to All Senses)**

| Criterion | Level | What It Means | Red Flags |
|-----------|-------|---------------|-----------|
| 1.1.1 Non-text Content | A | All images, icons, and custom graphics need alt text | Icon buttons without aria-label |
| 1.4.3 Contrast (Minimum) | AA | Text needs 4.5:1 contrast; large text 3:1 | Low-contrast focus indicators |
| 1.4.11 Non-text Contrast | AA | UI components need 3:1 minimum contrast | Light gray on white disabled states |
| 1.4.13 Content on Hover/Focus | AA | Additional content must remain visible | Tooltip disappears when tabbing away |
| 2.4.7 Focus Visible | AA | Focus indicator must be visible | outline: none without replacement |

#### **Operable (Keyboard & Input)**

| Criterion | Level | What It Means | Red Flags |
|-----------|-------|---------------|-----------|
| 2.1.1 Keyboard | A | All functionality keyboard accessible | Button click-only, no Enter/Space support |
| 2.1.2 No Keyboard Trap | A | Focus shouldn't get stuck | Modal without focus trap escaping |
| 2.4.3 Focus Order | A | Logical, meaningful tab order | tabIndex="999" chaos without purpose |
| 2.4.8 Focus Visible (Enhanced) | AAA | Enhanced focus visibility | No visible focus indicator at all |
| 2.5.5 Target Size | AAA | Click/tap targets 24×24 CSS pixels | 16×16px buttons on mobile |

#### **Understandable (Clear & Predictable)**

| Criterion | Level | What It Means | Red Flags |
|-----------|-------|---------------|-----------|
| 3.2.4 Consistent Identification | A | Interactive elements behave consistently | "Submit" button in form 1, "Send" in form 2 |
| 3.3.2 Labels or Instructions | A | Form inputs must be labeled | Floating label without associated label element |
| 3.3.3 Error Suggestion | AA | Provide help with fixing errors | Error message without suggestion |

#### **Robust (Compatible with Assistive Tech)**

| Criterion | Level | What It Means | Red Flags |
|-----------|-------|---------------|-----------|
| 4.1.2 Name, Role, Value | A | Components expose role, state, value to AT | Custom dropdown with no role="listbox" |
| 4.1.3 Status Messages | AA | Live region announcements work correctly | Alert doesn't announce without aria-live |

### WebAIM Million 2025 Most Common Failures
1. **Low Contrast Text** - 79.1% of pages (unchanged from 2024)
2. **Missing Form Labels** - 59.9% of pages
3. **Missing Alt Text** - 54.4% of pages
4. **Broken ARIA Implementation** - 28.1% of pages with ARIA

---

## Detection Methods: Finding Existing Accessibility

### 1. Codebase Analysis Strategy

#### Step 1: Search for ARIA Usage
```bash
# Find all ARIA attributes in use
grep -r "aria-" /path/to/project --include="*.jsx" --include="*.tsx" --include="*.js"

# Count ARIA patterns
grep -r "aria-label" /path/to/project --include="*.jsx" | wc -l
grep -r "aria-describedby" /path/to/project --include="*.jsx" | wc -l
grep -r "aria-live" /path/to/project --include="*.jsx" | wc -l
grep -r "aria-hidden" /path/to/project --include="*.jsx" | wc -l
grep -r "role=" /path/to/project --include="*.jsx" | wc -l
```

#### Step 2: Search for Focus Management
```bash
# Find useRef for focus
grep -r "useRef.*focus\|focus()" /path/to/project --include="*.jsx" --include="*.tsx"

# Find tabIndex usage
grep -r "tabIndex" /path/to/project --include="*.jsx" | wc -l

# Find onKeyDown/onKeyUp handlers
grep -r "onKeyDown\|onKeyUp" /path/to/project --include="*.jsx" | wc -l

# Find autoFocus
grep -r "autoFocus" /path/to/project --include="*.jsx" | wc -l
```

#### Step 3: Identify Form Accessibility
```bash
# Find label associations
grep -r "htmlFor=" /path/to/project --include="*.jsx" | wc -l
grep -r "<label" /path/to/project --include="*.jsx" | wc -l

# Find aria-labelledby
grep -r "aria-labelledby" /path/to/project --include="*.jsx" | wc -l
```

#### Step 4: Screen Reader Patterns
```bash
# Find alt text patterns
grep -r "alt=" /path/to/project --include="*.jsx" | wc -l
grep -r 'alt=""' /path/to/project --include="*.jsx"  # Decorative images

# Find live regions
grep -r "aria-live" /path/to/project --include="*.jsx"
```

### 2. Visual Inspection Checklist

When opening an application, check for:

```
VISUAL ACCESSIBILITY SIGNS:
☐ Focus indicators visible on buttons (blue outline, ring, border)
☐ Consistent focus styling across all interactive elements
☐ Sufficient color contrast (text readable, not faded)
☐ Skip navigation link at top (usually "Skip to content")
☐ Heading structure visible (h1 at top, proper nesting)

KEYBOARD NAVIGATION SIGNS:
☐ Can navigate with Tab key through all buttons
☐ Can navigate through form fields in logical order
☐ Can close modals with Escape key
☐ Can submit forms with Enter key
☐ Focus wraps in modals (tab from last → first)

SCREEN READER SIGNS (browser DevTools):
☐ Buttons have accessible names (aria-label or text content)
☐ Form inputs have labels (htmlFor association or aria-labelledby)
☐ Images have alt text (or alt="" for decorative)
☐ Modals announced as dialogs (role="dialog")
☐ Live regions exist for status updates
```

### 3. Automated Detection in Code

#### Parsing ARIA from JSX
```javascript
// Pattern to detect existing ARIA attributes
const ariaPattern = /aria-\w+\s*=\s*["'`]/g;
const rolePattern = /role\s*=\s*["']([^"']+)["']/g;
const labelPattern = /aria-label\s*=\s*["']([^"']+)["']/g;

// Extract from component string
function detectAriaPatterns(jsxString) {
  const ariaMatches = jsxString.match(ariaPattern) || [];
  const roles = [...jsxString.matchAll(rolePattern)].map(m => m[1]);
  const labels = [...jsxString.matchAll(labelPattern)].map(m => m[1]);

  return {
    ariaCount: ariaMatches.length,
    rolesUsed: [...new Set(roles)],
    labelStrategy: labels.length > 0 ? 'aria-label' : 'content-based'
  };
}
```

#### Detecting Focus Management Approach
```javascript
// Look for useRef + focus pattern
const hasFocusRefPattern = /useRef.*focus\(\)/.test(code);

// Look for tabIndex usage
const hasTabIndexManagement = /tabIndex\s*=/.test(code);

// Look for autoFocus usage
const hasAutoFocus = /autoFocus/.test(code);

// Result: Codebase uses [tabIndex, useRef+focus()] for focus management
```

#### Detecting Keyboard Handler Patterns
```javascript
// Check what keyboard handlers are used
const hasOnKeyDown = /onKeyDown\s*=/.test(code);
const hasOnKeyUp = /onKeyUp\s*=/.test(code);
const hasOnKeyPress = /onKeyPress\s*=/.test(code);  // Deprecated, but check anyway

// Check which keys are handled
const handlesEscape = /key\s*===\s*['"]Escape['"]|key.*Escape/.test(code);
const handlesEnter = /key\s*===\s*['"]Enter['"]|key.*Enter/.test(code);
const handlesArrows = /key.*Arrow/.test(code);
```

---

## ARIA Pattern Preservation

### Understanding ARIA Attributes

ARIA stands for **Accessible Rich Internet Applications**. It provides:
- **Role**: What the element does (button, dialog, tab, etc.)
- **State**: Current condition (expanded, selected, disabled, etc.)
- **Property**: Characteristics (label, description, live region type, etc.)

### Common ARIA Attributes by Purpose

#### **Labeling & Description**
```jsx
// Pattern 1: aria-label (simple, self-contained label)
<button aria-label="Close dialog">✕</button>

// Pattern 2: aria-labelledby (link to element's text)
<div id="modal-title">Delete Account</div>
<div role="dialog" aria-labelledby="modal-title" />

// Pattern 3: aria-describedby (additional context)
<input
  id="password"
  aria-describedby="pwd-hint"
  type="password"
/>
<div id="pwd-hint">At least 12 characters</div>

// DETECTION: Check which pattern is used in existing code
```

#### **Widget Roles**
```jsx
// Custom buttons
<div role="button" tabIndex="0" onKeyDown={handleKeyDown}>
  Click me
</div>

// Custom tabs
<div role="tablist">
  <button role="tab" aria-selected={isActive}>Tab 1</button>
  <button role="tab" aria-selected={!isActive}>Tab 2</button>
</div>

// Modals/Dialogs
<div role="dialog" aria-labelledby="title" aria-modal="true">
  <h2 id="title">Confirm Action</h2>
</div>

// Menus
<ul role="menu">
  <li role="menuitem">Save</li>
  <li role="menuitem">Delete</li>
</ul>

// Lists
<ul role="listbox">
  <li role="option" aria-selected={isSelected}>Option 1</li>
</ul>

// PRESERVATION: When adding similar components, use exact same role + attribute combination
```

#### **State & Property Attributes**
```jsx
// aria-expanded: for menus, accordions, collapsibles
<button aria-expanded={isOpen} aria-controls="menu">
  Menu
</button>
<ul id="menu" hidden={!isOpen}>...</ul>

// aria-selected: for tabs, options
<button role="tab" aria-selected={activeTab === 'tab1'}>
  Tab 1
</button>

// aria-disabled: for disabled custom components (not <button disabled>)
<div role="button" aria-disabled={isDisabled}>
  Submit
</div>

// aria-checked: for custom checkboxes
<div role="checkbox" aria-checked={isChecked}>
  Accept terms
</div>

// aria-pressed: for toggle buttons
<button aria-pressed={isPressed}>
  Mute
</button>

// aria-hidden: hide decorative elements from screen readers
<span aria-hidden="true">→</span>

// PATTERN MATCHING: Extract existing usage like:
// - If component uses aria-expanded, all similar components should too
// - If aria-hidden used for icons, apply to all decorative icons
```

#### **Live Regions**
```jsx
// aria-live="polite" - announce when convenient (status messages, notifications)
<div aria-live="polite" aria-atomic="true" className="status">
  Changes saved successfully
</div>

// aria-live="assertive" - interrupt user (errors, urgent alerts)
<div aria-live="assertive" aria-atomic="true" className="error">
  Payment failed. Please try again.
</div>

// DETECTION: Search for aria-live in existing code
// PRESERVATION: New status messages must use same aria-live pattern
```

### Pattern Detection Workflow

#### Step 1: Identify Existing ARIA Patterns
```javascript
// For each component type found in codebase:
const patternMap = {
  buttons: {
    standard: '<button>Label</button>',           // Uses native semantics
    custom: '<div role="button" tabIndex="0">',  // Custom ARIA pattern
    iconOnly: '<button aria-label="Close">✕</button>', // Uses aria-label
  },
  dialogs: {
    pattern: `
      <div role="dialog" aria-labelledby="title" aria-modal="true">
        <h2 id="title">Dialog Title</h2>
      </div>
    `,
    hasLabelledBy: true,
    hasModal: true,
  },
  forms: {
    labelPattern: 'htmlFor association',  // <label htmlFor="input-id">
    orAria: 'aria-labelledby',            // <input aria-labelledby="label-id">
  }
};
```

#### Step 2: Extract Exact Attributes
When you find a pattern in use, document EXACTLY what's used:
```
EXAMPLE EXTRACTION:
Component: Modal Dialog
Location: /src/components/ConfirmDialog.jsx
Pattern Found:
  - role="dialog"
  - aria-labelledby="dialog-title"
  - aria-modal="true"
  - aria-describedby="dialog-description" (if present)
  - Focus trap implemented with useRef + focus()
  - Close button has aria-label="Close"

WHEN ADDING NEW MODAL:
Must use identical: role, aria-labelledby, aria-modal
If description exists, must use aria-describedby
Must implement same focus trap pattern
```

#### Step 3: Match When Adding Similar Components
```javascript
// WRONG: Introducing new ARIA approach
function NewButton({ label }) {
  // Different from existing: using data attributes instead of aria-label
  return <button data-tooltip={label}>✕</button>;
}

// RIGHT: Matching existing pattern
function NewButton({ label }) {
  // Same as existing buttons in codebase
  return <button aria-label={label}>✕</button>;
}
```

### Common ARIA Breakages to Avoid

#### **Breakage #1: Removing aria-label During Cleanup**
```jsx
// EXISTING CODE (accessible)
<button aria-label="Close dialog">✕</button>

// BREAKING CHANGE: Removing aria-label
<button>✕</button>  // Screen reader says "button" with no label

// CORRECT: Keep aria-label
<button aria-label="Close dialog">✕</button>
```

#### **Breakage #2: Changing Role Inconsistently**
```jsx
// EXISTING: Custom button using role="button"
<div role="button" tabIndex="0" onKeyDown={handleKeyDown}>
  Action
</div>

// BREAKING: Using native button in new place
<button>New Action</button>  // Inconsistent approach

// CORRECT: Match the existing pattern
<div role="button" tabIndex="0" onKeyDown={handleKeyDown}>
  New Action
</div>
```

#### **Breakage #3: Forgetting aria-hidden on Decorative Elements**
```jsx
// EXISTING: Decorative icon properly hidden
<span aria-hidden="true">→</span> Menu

// BREAKING: New decorative icon without aria-hidden
<span>✓</span> Success  // Screen reader announces "checkmark" unnecessarily

// CORRECT: Apply same pattern
<span aria-hidden="true">✓</span> Success
```

---

## Keyboard Navigation Preservation

### Understanding Keyboard Accessibility

Keyboard navigation is essential for:
- **Blind users** using screen readers (keyboard primary input)
- **Motor disabilities** (cannot use mouse)
- **Power users** who navigate faster with keyboard
- **Mobile users** without precise mouse/pointer control

### Tab Order & Focus Management

#### **The tabIndex Attribute**
```jsx
// tabIndex="0" - Include in natural tab order (preferred)
<button>Save</button>  // implicit tabIndex="0"
<div role="button" tabIndex="0">Custom button</div>

// tabIndex="-1" - Remove from tab order (focus programmatically only)
<div tabIndex="-1">Content not in tab order</div>
<button tabIndex="-1" hidden>Hidden button</button>

// tabIndex="1+" - ANTI-PATTERN, avoid! (Creates non-logical order)
<button tabIndex="3">Should be 2nd</button>
<button tabIndex="1">Should be 1st</button>
<button tabIndex="2">Should be 3rd</button>
// This confuses keyboard users. Instead, use CSS order or source order.
```

#### **Detection Strategy for Tab Order**
```bash
# Search for tabIndex usage patterns
grep -r "tabIndex" /src --include="*.jsx"

# Count positive tabIndex (problematic)
grep -r "tabIndex=\"[1-9]" /src --include="*.jsx" | wc -l

# Check if tabIndex="0" or tabIndex="-1" only (good)
grep -r "tabIndex=\"0\"\|tabIndex=\"-1\"" /src --include="*.jsx"
```

#### **Focus Order Preservation Example**
```jsx
// EXISTING: Logical tab order by source order
function Dialog() {
  return (
    <div role="dialog">
      <h2>Confirm Delete</h2>
      <button>Cancel</button>
      <button>Delete</button>
    </div>
  );
}
// Tab order: Dialog → h2 → Cancel button → Delete button ✓

// BREAKING: Adding element with wrong tabIndex
function Dialog() {
  return (
    <div role="dialog">
      <h2>Confirm Delete</h2>
      <button tabIndex="2">Cancel</button>
      <button tabIndex="1">Delete</button>
      <button>Extra action</button>
    </div>
  );
}
// Tab order: Delete → Extra action → Cancel (confusing!) ✗

// CORRECT: Keep natural tab order
function Dialog() {
  return (
    <div role="dialog">
      <h2>Confirm Delete</h2>
      <button>Cancel</button>
      <button>Delete</button>
      <button>Extra action</button>  // Naturally last
    </div>
  );
}
// Tab order: Dialog → Cancel → Delete → Extra action ✓
```

### Keyboard Event Handlers

#### **Common Patterns**
```jsx
// Pattern 1: onKeyDown for immediate response
<input
  onKeyDown={(e) => {
    if (e.key === 'Enter') submitForm();
    if (e.key === 'Escape') closeDialog();
  }}
/>

// Pattern 2: onKeyDown with preventDefault for custom behavior
<div
  role="button"
  tabIndex="0"
  onKeyDown={(e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  Custom button
</div>

// Pattern 3: Arrow key navigation (menus, listboxes, tabs)
<ul role="listbox" onKeyDown={(e) => {
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    setSelectedIndex(prev => (prev + 1) % items.length);
  }
  if (e.key === 'ArrowUp') {
    e.preventDefault();
    setSelectedIndex(prev => (prev - 1 + items.length) % items.length);
  }
}}>
  {items.map((item, i) => (
    <li key={i} role="option" aria-selected={selectedIndex === i}>
      {item}
    </li>
  ))}
</ul>

// DETECTION: Extract which keys are handled
// PRESERVATION: New similar components must handle same keys
```

#### **Detection: What Keys Are Handled?**
```bash
# Find all keyboard patterns in use
grep -rE "key\s*===|key\s*==\s" /src --include="*.jsx" | sort | uniq

# Look for specific patterns
grep -r "'Enter'\|'Escape'\|'ArrowDown'" /src --include="*.jsx"
```

### Focus Traps in Modals

Modals must prevent focus from leaving the dialog. Users should Tab within the dialog, and when they Tab past the last element, focus wraps to the first element (and vice versa with Shift+Tab).

#### **Implementation Pattern**
```jsx
function Modal({ isOpen, onClose }) {
  const firstButtonRef = useRef(null);
  const lastButtonRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift+Tab on first element → focus last element
      if (document.activeElement === firstButtonRef.current) {
        e.preventDefault();
        lastButtonRef.current.focus();
      }
    } else {
      // Tab on last element → focus first element
      if (document.activeElement === lastButtonRef.current) {
        e.preventDefault();
        firstButtonRef.current.focus();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div role="dialog" onKeyDown={handleKeyDown} aria-modal="true">
      <button ref={firstButtonRef} onClick={onClose}>Cancel</button>
      {/* Modal content */}
      <button ref={lastButtonRef} onClick={handleAction}>Confirm</button>
    </div>
  );
}
```

#### **Detection: Is Focus Trap Present?**
```javascript
// Check if modal/dialog implements focus trap
const hasFocusTrap = /useRef.*focus|onKeyDown.*Tab|aria-modal/.test(componentCode);

// PRESERVATION: All modals must have focus trap
// If adding a modal, check existing modals first and copy pattern
```

### Keyboard Handler Preservation

#### **Pattern Documentation Template**
```
KEYBOARD PATTERNS IN USE:

Component: MenuButton
File: /src/components/MenuButton.jsx
Keyboard handlers:
  - Key 'Enter': Open menu
  - Key ' ' (Space): Open menu
  - Key 'Escape': Close menu
  - Key 'ArrowDown': Focus next menu item
  - Key 'ArrowUp': Focus previous menu item

When adding new MenuButton:
Must implement identical key handlers
Must not add additional key behaviors (consistency)
Must preventDefault for custom key handling
```

#### **Common Keyboard Pattern Breakages**

```jsx
// BREAKAGE #1: Icon button with no keyboard handler
<button>✕</button>  // Can click, but keyboard handler missing if pattern exists

// BREAKAGE #2: Removing key handler
// EXISTING: Tabs handled for navigation
<div onKeyDown={(e) => e.key === 'Enter' && submit()}>

// NEW: Forgot to add handler
<div>  // Can't submit with Enter

// BREAKAGE #3: Inconsistent key handling across similar components
// Component A: Uses onKeyDown
// Component B: Uses onKeyUp (different!)

// CORRECT: Match the pattern
```

---

## Focus Management Patterns

### useRef + focus() Pattern

#### **Common Pattern**
```jsx
// Pattern: Save ref to element, call focus() when needed
function SearchWithFocus() {
  const inputRef = useRef(null);

  const handleSearch = async () => {
    const results = await fetchResults();
    // After results load, focus the results
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <>
      <input ref={inputRef} onChange={handleSearch} />
      {/* Results below */}
    </>
  );
}
```

#### **Detection: When useRef + focus() is Used**
```bash
# Find all useRef usage for focus management
grep -rE "useRef.*focus\(\)|\.current\.focus\(\)" /src --include="*.jsx"

# Document which components use this pattern
```

#### **Modal Focus Management Pattern**
```jsx
// When modal opens: focus first element
// When modal closes: restore focus to trigger button

function Modal({ isOpen, onClose, trigger }) {
  const modalRef = useRef(null);
  const triggerRef = trigger; // Passed from parent

  useEffect(() => {
    if (isOpen) {
      // Move focus into modal
      const firstFocusable = modalRef.current?.querySelector('button, [href], input');
      firstFocusable?.focus();
    } else {
      // Restore focus to trigger
      triggerRef?.current?.focus();
    }
  }, [isOpen]);

  return <div ref={modalRef} role="dialog">...</div>;
}
```

#### **PRESERVATION: Focus Management Template**
```javascript
// When adding new dynamic UI (modal, dropdown, etc.):
// MUST implement:
// 1. Save ref to trigger element
// 2. Move focus to new UI when shown
// 3. Restore focus to trigger when closed

// DETECTION: Check what focus pattern is used
// MATCHING: Use exact same pattern for consistency
```

### autoFocus Attribute

#### **Pattern Detection**
```bash
# Find autoFocus usage
grep -r "autoFocus" /src --include="*.jsx"
```

#### **When to Use autoFocus**
```jsx
// Good: Modal dialog should focus first input
<input autoFocus placeholder="Search" />

// Careful: Redirecting focus on page load might not be accessible
<input autoFocus />  // Keyboard user expects focus on main content

// Detection: Is autoFocus used for dialogs/modals? Use same for consistency.
// Detection: Is autoFocus avoided for page load? Respect that pattern.
```

### Route-Based Focus Management

When pages navigate, focus should reset to logical place (usually main content).

```jsx
// Pattern: Reset focus on route change
function Layout() {
  const mainRef = useRef(null);

  useEffect(() => {
    // Route changed, reset focus
    mainRef.current?.focus();
  }, [location.pathname]);

  return (
    <>
      <header>...</header>
      <main ref={mainRef} tabIndex="-1">
        {/* Content */}
      </main>
    </>
  );
}

// Detection: Look for useEffect with location dependency
// Preservation: Implement same pattern for new routes
```

---

## Screen Reader Compatibility

### Heading Hierarchy

Screen readers rely on proper heading structure. Users navigate by headings.

#### **Correct Hierarchy**
```jsx
// CORRECT: Logical nesting
<h1>Website Title</h1>
  <h2>Section 1</h2>
    <h3>Subsection 1.1</h3>
    <h3>Subsection 1.2</h3>
  <h2>Section 2</h2>

// WRONG: Jumping levels
<h1>Website</h1>
<h3>Subsection</h3>  // Skipped h2! ✗

// WRONG: Multiple h1s without structure
<h1>Website</h1>
<h1>Another Main Title</h1>  // Confusing to screen reader ✗
```

#### **Detection Pattern**
```javascript
// Analyze heading structure
const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
const headingLevels = Array.from(headings).map(h => parseInt(h.tagName[1]));

function validateHeadingHierarchy(levels) {
  for (let i = 1; i < levels.length; i++) {
    const diff = levels[i] - levels[i-1];
    if (diff > 1) {
      console.warn(`Skipped heading level: h${levels[i-1]} → h${levels[i]}`);
    }
  }
}
```

#### **Preservation: Heading Checklist**
```
When adding new content:
☐ No h1 jumping (at most one per page)
☐ No level skipping (h2 → h4 is wrong)
☐ Headings follow content structure logically
☐ Headings are descriptive (not "Click Here", use "Submit Payment")
```

### Image Alt Text Patterns

```jsx
// Pattern 1: Meaningful image with alt text
<img src="photo.jpg" alt="Team meeting in conference room" />

// Pattern 2: Decorative image (hidden from screen readers)
<img src="spacer.gif" alt="" aria-hidden="true" />
// OR
<img src="decorative-line.svg" alt="" />  // alt="" signals decorative

// Pattern 3: Icon in button with aria-label
<button aria-label="Save">
  <SaveIcon />
</button>
// Icon alt text NOT needed, button label is sufficient

// Pattern 4: Icon as visual aid (already described in text)
<p>
  <InfoIcon alt="" />
  This is important information
</p>
// Icon hidden, text describes content
```

#### **Detection: Alt Text Strategy**
```bash
# Find all images and check alt text
grep -r "<img" /src --include="*.jsx" | grep -v "alt="

# Check alt="" (decorative)
grep -r 'alt=""' /src --include="*.jsx"

# Check if aria-hidden used consistently
grep -r 'alt="".*aria-hidden\|aria-hidden.*alt=""' /src
```

#### **Preservation: Alt Text Checklist**
```
When adding images:
☐ Meaningful images have descriptive alt text
☐ Decorative images have alt=""
☐ Icons in buttons use aria-label (not alt)
☐ Alt text matches existing pattern in codebase
```

### Form Label Association

Screen readers need to know which label goes with which input.

#### **Pattern 1: htmlFor Association (Preferred)**
```jsx
<label htmlFor="email-input">Email address</label>
<input id="email-input" type="email" />

// Screen reader announces: "Email address, input, type email"
```

#### **Pattern 2: aria-labelledby (For Complex Labels)**
```jsx
<label id="password-label">
  Password
  <span aria-hidden="true">*</span>
</label>
<input aria-labelledby="password-label" type="password" />

// Screen reader announces: "Password, input, type password"
```

#### **Pattern 3: aria-label (Last Resort)**
```jsx
<input aria-label="Search products" type="text" />

// Use only when label element can't be used
```

#### **Detection: Which Pattern is Used?**
```bash
# Find form label patterns
grep -r "htmlFor=" /src --include="*.jsx" | wc -l
grep -r "aria-labelledby=" /src --include="*.jsx" | wc -l
grep -r "aria-label=" /src --include="*.jsx" | grep "input\|textarea"

# Analyze consistency
# If htmlFor is used 50+ times and aria-labelledby 2 times,
# new forms should use htmlFor pattern
```

#### **Preservation: Form Label Checklist**
```
When adding form inputs:
☐ Input has label (htmlFor association OR aria-labelledby OR aria-label)
☐ Label pattern matches existing code (don't mix approaches)
☐ Required indicator accessible (not just visual *)
☐ Error messages associated (aria-describedby or aria-errormessage)
☐ Help text associated (aria-describedby)
```

### Live Regions for Dynamic Content

Live regions announce content changes to screen readers without page reload.

#### **Pattern: Status Message**
```jsx
// aria-live="polite" - don't interrupt user
<div aria-live="polite" aria-atomic="true">
  {successMessage}  // Announces when message updates
</div>

// aria-live="assertive" - interrupt user (errors only)
<div aria-live="assertive">
  {errorMessage}  // Announces immediately
</div>
```

#### **Detection: Is aria-live Used?**
```bash
# Find live region implementations
grep -r "aria-live" /src --include="*.jsx"

# Check if polite or assertive
grep -r "aria-live=\"polite\"\|aria-live=\"assertive\"" /src
```

#### **Preservation: Live Region Checklist**
```
When adding status messages:
☐ Uses aria-live="polite" or "assertive"
☐ aria-atomic="true" for complete message announcement
☐ Pattern matches existing messages in codebase
☐ Not overused (doesn't announce every minor update)
```

---

## Visual Accessibility Preservation

### Focus Indicator Styles

#### **Required Properties**
```css
/* Focus indicator must be visible */
button:focus {
  outline: 2px solid #0066cc;  /* 2px minimum thickness */
  outline-offset: 2px;
  /* OR */
  border: 2px solid #0066cc;
}

/* Contrast requirement: 3:1 minimum */
/* If button is white on gray background:
   Focus outline must contrast with both */

/* For custom focus indicators */
button:focus-visible {
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.25);
}

/* Minimum size: 3x3px at 1x zoom */
/* Focus indicator must meet this size requirement */
```

#### **Detection: What's the Focus Style?**
```bash
# Find focus styles in CSS/styled-components
grep -r ":focus\|:focus-visible\|:focus-within" /src --include="*.css"
grep -r "focus" /src --include="*.styled.js" --include="*.module.css"

# Extract outline/border/shadow properties
# Document: Is outline used? What color? What offset?
```

#### **Detection JavaScript**
```javascript
// Get computed focus style
const button = document.querySelector('button');
button.focus();
const style = window.getComputedStyle(button);
console.log('outline:', style.outline);
console.log('outline-offset:', style.outlineOffset);
console.log('box-shadow:', style.boxShadow);
```

#### **Preservation: Focus Style Checklist**
```
When styling new components:
☐ Focus indicator visible (not outline: none)
☐ Matches existing focus style (outline, border, or shadow)
☐ Minimum 2px thickness
☐ At least 3:1 contrast with background
☐ Outline-offset at least 2px (not touching edge)
```

### Color Contrast

#### **WCAG 2.2 Requirements**
```
Normal text (< 18pt): 4.5:1 contrast ratio
Large text (>= 18pt or 14pt bold): 3:1 contrast ratio
UI Components (borders, icons): 3:1 contrast ratio
Focus indicators: 3:1 contrast ratio
```

#### **Detection: Test Contrast**
```javascript
// Get element colors
const element = document.querySelector('.text');
const style = window.getComputedStyle(element);
const bgColor = style.backgroundColor;  // rgb(255, 255, 255)
const fgColor = style.color;            // rgb(80, 80, 80)

// Calculate contrast ratio (simplified)
// Use: https://www.w3.org/WAI/WCAG21/Techniques/general/G17
function getContrastRatio(rgb1, rgb2) {
  // Extract RGB values and calculate relative luminance
  // Compare and return ratio
}
```

#### **Tool: WebAIM Contrast Checker**
Use browser DevTools or automated tools:
```bash
# npm package
npm install axe-core
# Then test in DevTools: axe.run()

# Browser extension: axe DevTools
# Identifies contrast failures automatically
```

#### **Preservation: Contrast Checklist**
```
When styling components:
☐ Text contrast at least 4.5:1 (normal) or 3:1 (large)
☐ Disabled states still 3:1 minimum
☐ Focus indicators 3:1 contrast
☐ Icons 3:1 contrast with background
☐ Matches existing color theme (don't introduce lower contrast)
```

### Motion & Animation

#### **WCAG 2.2: Animations**
```css
/* Respect prefers-reduced-motion setting */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Users with vestibular disorders may experience nausea from animations */
```

#### **Detection: Animation Usage**
```bash
# Find CSS animations/transitions
grep -r "@keyframes\|animation:\|transition:" /src --include="*.css"

# Check for prefers-reduced-motion handling
grep -r "prefers-reduced-motion" /src --include="*.css"
```

#### **Preservation: Animation Checklist**
```
When adding animations:
☐ Animations are not required (content accessible without)
☐ prefers-reduced-motion media query respected
☐ No animations on page load (user didn't trigger)
☐ Autoplay of animations: very rare, requires user control
```

---

## Common Accessibility Breakage Patterns

### Breakage Pattern #1: Icon-Only Buttons Without Labels

```jsx
// BREAKING
function NavBar() {
  return (
    <nav>
      <button>☰</button>        {/* No label, screen reader says "button" */}
      <button>🔍</button>        {/* No label, screen reader says "button" */}
      <button>👤</button>        {/* No label, screen reader says "button" */}
    </nav>
  );
}

// CORRECT
function NavBar() {
  return (
    <nav>
      <button aria-label="Open menu">☰</button>
      <button aria-label="Search">🔍</button>
      <button aria-label="Profile">👤</button>
    </nav>
  );
}

// DETECTION
// Search: <button>[^<]*[☰🔍👤ℹ️✕✓][^<]*</button> without aria-label
// These are likely unlabeled icon buttons
```

### Breakage Pattern #2: Breaking Heading Hierarchy

```jsx
// EXISTING: Proper hierarchy
<h1>My App</h1>
<h2>About Section</h2>

// BREAKING: Adding h3 without h2
<h1>My App</h1>
<h2>About Section</h2>
<h3>Team Details</h3>    {/* This was in existing code */}
<h3>New Feature</h3>     {/* Added without h2 container */}

// CORRECT: Maintain hierarchy
<h1>My App</h1>
<h2>About Section</h2>
  <h3>Team Details</h3>
<h2>New Feature</h2>      {/* New section, use h2 */}
  <h3>Details</h3>
```

### Breakage Pattern #3: Creating Modals Without Focus Trap

```jsx
// EXISTING: Modal with focus trap
function ExistingModal() {
  const firstRef = useRef(null);
  const lastRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Tab' && e.shiftKey && document.activeElement === firstRef.current) {
      e.preventDefault();
      lastRef.current.focus();
    }
  };

  return <div role="dialog" onKeyDown={handleKeyDown}>...</div>;
}

// BREAKING: New modal without focus trap
function NewModal() {
  return (
    <div role="dialog">
      {/* User can Tab out of modal - accessibility broken! */}
    </div>
  );
}

// CORRECT: Copy exact pattern from existing modal
function NewModal() {
  const firstRef = useRef(null);
  const lastRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Tab' && e.shiftKey && document.activeElement === firstRef.current) {
      e.preventDefault();
      lastRef.current.focus();
    }
  };

  return <div role="dialog" onKeyDown={handleKeyDown}>...</div>;
}
```

### Breakage Pattern #4: Images Without Alt Text When Existing Images Have Alt

```jsx
// EXISTING: Images properly alt-texted
<img src="team.jpg" alt="Engineering team at company picnic" />
<img src="spacer.gif" alt="" />  {/* Decorative, hidden */}

// BREAKING: New image without alt
<img src="office.jpg" />  {/* No alt text! */}

// CORRECT: Add alt text matching pattern
<img src="office.jpg" alt="Open office workspace with desks" />
<img src="divider.svg" alt="" />  {/* Decorative, matching pattern */}
```

### Breakage Pattern #5: Form Inputs Without Labels When Pattern Exists

```jsx
// EXISTING: Forms use htmlFor pattern
<label htmlFor="email">Email address</label>
<input id="email" type="email" />

<label htmlFor="password">Password</label>
<input id="password" type="password" />

// BREAKING: New form input without label
<input id="phone" type="tel" />  {/* No label! */}

// CORRECT: Follow existing pattern
<label htmlFor="phone">Phone number</label>
<input id="phone" type="tel" />
```

### Breakage Pattern #6: Removing Keyboard Handlers When Adding Features

```jsx
// EXISTING: Custom dropdown with keyboard support
function Dropdown() {
  return (
    <div
      role="listbox"
      onKeyDown={(e) => {
        if (e.key === 'ArrowDown') selectNext();
        if (e.key === 'ArrowUp') selectPrev();
        if (e.key === 'Enter') confirm();
        if (e.key === 'Escape') close();
      }}
    >
      {items.map(item => <div key={item.id}>{item.label}</div>)}
    </div>
  );
}

// BREAKING: Adding item without keyboard support
function Dropdown() {
  return (
    <div role="listbox">
      {items.map(item => (
        <div key={item.id}>
          {item.label}
          {item.isNew && <span>NEW!</span>}  {/* No keyboard handler for this! */}
        </div>
      ))}
    </div>
  );
}

// CORRECT: Maintain keyboard handler
function Dropdown() {
  return (
    <div
      role="listbox"
      onKeyDown={(e) => {
        if (e.key === 'ArrowDown') selectNext();
        if (e.key === 'ArrowUp') selectPrev();
        if (e.key === 'Enter') confirm();
        if (e.key === 'Escape') close();
      }}
    >
      {items.map(item => (
        <div key={item.id}>
          {item.label}
          {item.isNew && <span aria-hidden="true">NEW!</span>}  {/* Decorative indicator */}
        </div>
      ))}
    </div>
  );
}
```

### Breakage Pattern #7: Creating New Components Without Matching ARIA

```jsx
// EXISTING: Buttons use aria-label consistently
<button aria-label="Close">×</button>
<button aria-label="Save">💾</button>

// BREAKING: New button ignores pattern
<button title="Refresh">🔄</button>  {/* Using title instead of aria-label */}

// CORRECT: Match existing pattern
<button aria-label="Refresh">🔄</button>
```

---

## Component-Specific Pattern Matching

### Buttons & Click Handlers

#### **Detection Template**
```javascript
// For each button in codebase, extract:
// 1. Is it native <button> or custom role="button"?
// 2. Does it have aria-label, visible text, or both?
// 3. Does it handle keyboard (onKeyDown)?
// 4. Is there aria-pressed for toggle buttons?

const buttonPatterns = {
  standard: '<button>Save</button>',              // Native, text content
  iconLabel: '<button aria-label="Close">×</button>', // Icon + aria-label
  custom: '<div role="button" tabIndex="0" onKeyDown={...}>',
  toggle: '<button aria-pressed={isPressed}>Mute</button>',
};
```

#### **Preservation Checklist**
```
When adding buttons:
☐ Use native <button> if possible (preferred)
☐ If custom role="button": must have tabIndex="0"
☐ If custom role="button": must have onKeyDown handler (Enter/Space)
☐ Icon buttons: must have aria-label (match existing)
☐ Toggle buttons: must have aria-pressed (match existing)
```

### Modals & Dialogs

#### **Detection Template**
```javascript
// For each modal/dialog:
// 1. Has role="dialog"?
// 2. Has aria-labelledby (and matching id)?
// 3. Has aria-modal="true"?
// 4. Has focus trap (useRef + focus)?
// 5. Closes on Escape key?
// 6. Focus restored to trigger after close?

const modalPattern = {
  role: 'dialog',
  ariaLabelledBy: 'modal-title',
  ariaModal: true,
  focusTrap: true,
  escapeToClose: true,
  focusRestoration: true,
};
```

#### **Preservation Checklist**
```
When adding modals:
☐ role="dialog"
☐ aria-labelledby pointing to title element
☐ aria-modal="true"
☐ Focus trap prevents Tab-out
☐ Escape key closes modal
☐ Focus returns to trigger button after close
☐ Matches exact implementation of existing modals
```

### Form Fields & Labels

#### **Detection Template**
```javascript
// For each form field:
// 1. What labeling pattern: htmlFor, aria-labelledby, aria-label?
// 2. Is required indicator accessible? (aria-required or <span aria-label="required">*)
// 3. Error messages: aria-describedby or aria-errormessage?
// 4. Help text: aria-describedby?
// 5. Placeholder: complementary to label or replacing it?

const formPattern = {
  labelingStrategy: 'htmlFor',  // or 'aria-labelledby' or 'aria-label'
  requiredIndicator: 'aria-required',
  errorHandling: 'aria-describedby',
  helpTextPattern: 'aria-describedby',
  placeholderRole: 'complementary',  // Not replacing label
};
```

#### **Preservation Checklist**
```
When adding form inputs:
☐ Label associated with input (htmlFor match)
☐ Required indicator accessible (aria-required + visual *)
☐ Error messages connected (aria-describedby="error-id")
☐ Help text visible and connected (aria-describedby="help-id")
☐ Placeholder does NOT replace label
☐ Input type correct (email, tel, date, etc.)
☐ Validation messages announced to screen readers
```

### Tabs & Navigation

#### **Detection Template**
```javascript
// For each tab pattern:
// 1. Uses role="tablist", role="tab", role="tabpanel"?
// 2. aria-selected tracks current tab?
// 3. aria-controls links tab to panel?
// 4. Keyboard: ArrowLeft/Right to switch tabs?
// 5. Home/End keys jump to first/last tab?

const tabPattern = {
  roles: ['tablist', 'tab', 'tabpanel'],
  stateTracking: 'aria-selected',
  relationship: 'aria-controls',
  keyboardNavigation: ['ArrowLeft', 'ArrowRight', 'Home', 'End'],
};
```

#### **Preservation Checklist**
```
When adding tab navigation:
☐ role="tablist" on container
☐ role="tab" on each tab button
☐ role="tabpanel" on content panels
☐ aria-selected="true/false" on tabs
☐ aria-controls linking tab to panel
☐ ArrowLeft/Right switches tabs
☐ Home/End jumps to first/last tab
☐ Enter/Space doesn't do anything (tabs already in tab order)
```

### Dropdowns & Select Menus

#### **Detection Template**
```javascript
// For each dropdown:
// 1. Is it native <select> or custom role="listbox"?
// 2. aria-expanded indicates open/closed?
// 3. aria-owns or aria-controls links button to menu?
// 4. Menu items: role="option"?
// 5. aria-selected tracks current option?
// 6. Keyboard: ArrowDown/Up, Home/End, Enter/Space?

const dropdownPattern = {
  type: 'custom',  // or 'native'
  triggerExpanded: 'aria-expanded',
  trigger: 'aria-controls or aria-owns',
  itemRole: 'option',
  itemSelection: 'aria-selected',
  keyboard: ['ArrowDown', 'ArrowUp', 'Home', 'End', 'Enter'],
};
```

#### **Preservation Checklist**
```
When adding dropdowns:
☐ Use native <select> if possible
☐ If custom: aria-expanded on trigger
☐ aria-controls or aria-owns linking trigger to menu
☐ role="listbox" on menu container
☐ role="option" on menu items
☐ aria-selected tracking selection
☐ ArrowDown/Up navigates items
☐ Home/End jumps to first/last
☐ Enter selects current item
☐ Escape closes menu
☐ Match existing dropdown pattern exactly
```

---

## Testing & Validation Strategies

### Automated Testing Approach

#### **axe-core (Browser Extension + npm)**
```bash
# Install
npm install @axe-core/react

# Use in React Testing Library
import { axe, toHaveNoViolations } from 'jest-axe';

describe('Modal Accessibility', () => {
  test('modal should have no accessibility violations', async () => {
    const { container } = render(<Modal isOpen={true} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

#### **React Testing Library (Recommended)**
```javascript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('Button Accessibility', () => {
  test('button should be keyboard accessible', async () => {
    const user = userEvent.setup();
    render(<button onClick={() => {}}>Save</button>);

    const button = screen.getByRole('button', { name: /save/i });
    expect(button).toBeInTheDocument();

    // Test keyboard interaction
    await user.tab();
    expect(button).toHaveFocus();

    await user.keyboard('{Enter}');
    expect(clickHandler).toHaveBeenCalled();
  });

  test('icon button should have aria-label', () => {
    render(<button aria-label="Close">×</button>);
    const button = screen.getByRole('button', { name: /close/i });
    expect(button).toBeInTheDocument();
  });

  test('modal should trap focus', async () => {
    const user = userEvent.setup();
    render(<Modal isOpen={true} />);

    const firstButton = screen.getByRole('button', { name: /cancel/i });
    const lastButton = screen.getByRole('button', { name: /confirm/i });

    firstButton.focus();
    await user.keyboard('{Shift>}{Tab}{/Shift}');
    expect(lastButton).toHaveFocus();  // Focus wrapped
  });
});
```

#### **Manual Keyboard Testing**
```
KEYBOARD TEST PROCEDURE:

1. BASIC NAVIGATION
   - Open app
   - Press Tab repeatedly
   - Verify focus moves through interactive elements
   - Verify focus order makes sense (left-to-right, top-to-bottom)
   - Verify no focus traps on page load

2. BUTTON TESTING
   - Focus each button with Tab
   - Press Enter → button should activate
   - Press Space → button should activate
   - (Both Enter and Space should work)

3. FORM TESTING
   - Tab through all inputs
   - Type in text fields
   - Press Tab to move between fields
   - Check radio buttons with arrow keys or space
   - Select dropdown options with arrow keys + enter

4. MODAL TESTING
   - Tab through modal (should not escape)
   - Shift+Tab from first element → should jump to last
   - Press Escape → modal should close
   - After close, focus should return to trigger button

5. MENU/DROPDOWN TESTING
   - Tab to trigger button
   - Press Enter or Space → menu opens
   - Arrow keys navigate items
   - Enter selects item
   - Escape closes menu without selecting
```

#### **Screen Reader Testing**
```
SCREEN READER TEST PROCEDURE:

Minimum: NVDA (Windows) or JAWS (Windows)

1. DOCUMENT STRUCTURE
   - Go to top (screen reader mode)
   - Verify single H1 at top
   - Navigate by headings (H key in NVDA)
   - Verify heading hierarchy (no skipped levels)
   - Verify content structure makes sense

2. BUTTON TESTING
   - Navigate to button (B key in NVDA)
   - Verify button name announced correctly
   - Verify "button" role announced
   - For icon buttons: verify aria-label announced (not just icon)

3. FORM TESTING
   - Navigate to form fields (F key in NVDA)
   - Verify label announced with field
   - Verify field type announced (text, email, checkbox, etc.)
   - Verify required status announced (if aria-required)
   - Verify error messages announced (if aria-live)
   - Verify help text announced (if aria-describedby)

4. MODAL TESTING
   - Modal opens
   - Verify dialog role announced
   - Verify title announced
   - Verify focus moves to modal
   - Tab through modal options
   - Verify focus trapped (no escape)
   - Escape closes modal
   - Verify focus returns to trigger

5. IMAGE TESTING
   - Use images list view
   - Meaningful images: alt text describes content
   - Decorative images: alt="" (image not listed)
   - Icon buttons: button name used (image not read)

6. LIVE REGION TESTING
   - Perform action triggering status message
   - Verify message announced without page refresh
   - Verify urgent messages (aria-live="assertive") interrupt immediately
   - Verify polite messages wait until user pause
```

### Contrast Checking

#### **Automated Contrast Testing**
```bash
# Using WAVE (WebAIM)
# Browser extension or online tool
# Identifies low contrast text automatically

# Using axe
npm install @axe-core/react
# axe automatically tests contrast ratios
```

#### **Manual Contrast Checking**
```
USE: WebAIM Contrast Checker
https://webaim.org/resources/contrastchecker/

1. Identify text color (foreground)
2. Identify background color
3. Enter both into checker
4. Verify 4.5:1 (normal text) or 3:1 (large text)
5. For focus indicators: verify 3:1 minimum
```

---

## Quick Reference Checklist

### Pre-Implementation: Detection Phase

```
ACCESSIBILITY AUDIT CHECKLIST

□ ARIA PATTERNS
  □ Run: grep -r "aria-" /src --include="*.jsx" | sort | uniq
  □ Document all aria-* attributes found
  □ Extract common patterns (aria-label, aria-labelledby, aria-live)
  □ Note which components use ARIA vs native semantics

□ KEYBOARD NAVIGATION
  □ Run: grep -r "onKeyDown\|onKeyUp" /src --include="*.jsx"
  □ Document which keys are handled
  □ Check for tabIndex patterns
  □ Identify focus management approach (useRef, autoFocus, etc.)

□ FORM ACCESSIBILITY
  □ Run: grep -r "<label\|htmlFor\|aria-label" /src --include="*.jsx"
  □ Document label strategy (htmlFor, aria-labelledby, aria-label)
  □ Note required indicator patterns
  □ Document error handling patterns

□ HEADING STRUCTURE
  □ Extract all headings from HTML
  □ Verify hierarchy (no skipped levels)
  □ Check h1 count (should be 1)
  □ Verify logical nesting

□ IMAGE ALT TEXT
  □ Run: grep -r "<img" /src --include="*.jsx"
  □ Document alt text strategy
  □ Check for alt="" patterns (decorative)
  □ Verify aria-hidden consistency

□ FOCUS INDICATORS
  □ Check CSS for :focus styles
  □ Document outline/border/shadow properties
  □ Verify contrast (3:1 minimum)
  □ Test visual visibility in browser

□ MODAL/DIALOG PATTERNS
  □ Run: grep -r "role=\"dialog\"" /src --include="*.jsx"
  □ Document role attributes used
  □ Check for focus trap implementation
  □ Verify Escape key handler
  □ Check focus restoration on close
```

### During Implementation: Matching Phase

```
WHEN ADDING NEW FEATURES:

□ BUTTONS
  ☐ Use native <button> if possible
  ☐ If custom role="button": match exact ARIA pattern
  ☐ Icon buttons: use aria-label (match existing labels)
  ☐ Toggle buttons: add aria-pressed (if existing code uses it)

□ MODALS
  ☐ Copy focus trap from existing modal (exact code)
  ☐ Copy role/aria attributes (dialog, labelledby, modal)
  ☐ Copy close-on-Escape handler
  ☐ Copy focus restoration logic

□ FORMS
  ☐ Match existing label pattern (htmlFor, aria-labelledby, aria-label)
  ☐ Add aria-required if existing forms use it
  ☐ Add aria-describedby for errors/help text
  ☐ Add aria-invalid for error state (if existing code does)

□ NAVIGATION/KEYBOARDS
  ☐ Match onKeyDown handler pattern (same keys, same approach)
  ☐ Match tabIndex pattern (avoid positive tabIndex)
  ☐ Match focus management approach (useRef, autoFocus)

□ VISUAL ELEMENTS
  ☐ Match focus indicator style (outline, border, or shadow)
  ☐ Verify focus contrast (3:1 minimum)
  ☐ Test in multiple browsers
  ☐ Check prefers-reduced-motion media query usage

□ CONTENT
  ☐ Maintain heading hierarchy (no skipped levels)
  ☐ Add alt text to images (matching existing pattern)
  ☐ Use aria-hidden for decorative elements (matching pattern)
  ☐ Add aria-live for status messages (if existing code uses it)
```

### Post-Implementation: Validation Phase

```
BEFORE SHIPPING:

□ AUTOMATED TESTING
  ☐ Run axe() in testing library tests
  ☐ Verify zero violations
  ☐ Test focus management (keyboard + programmatic)
  ☐ Test form inputs and labels

□ MANUAL KEYBOARD TESTING
  ☐ Tab through entire page
  ☐ Tab enters and exits modals correctly
  ☐ Buttons work with Enter and Space
  ☐ Forms submittable with Enter
  ☐ Escape closes modals
  ☐ No focus traps on page load

□ SCREEN READER TESTING
  ☐ Buttons have names (NVDA announces them)
  ☐ Form labels associated with inputs
  ☐ Modal title announced
  ☐ Images have alt text (or alt="")
  ☐ Headings hierarchical
  ☐ Live regions announce correctly

□ VISUAL TESTING
  ☐ Focus indicators visible on all platforms
  ☐ Contrast meets 4.5:1 (text) or 3:1 (focus)
  ☐ No color-only communication
  ☐ Animations respect prefers-reduced-motion

□ REGRESSION TESTING
  ☐ Existing buttons still accessible
  ☐ Existing modals still have focus traps
  ☐ Existing forms still have labels
  ☐ No ARIA attributes removed
  ☐ No keyboard handlers deleted
  ☐ Heading hierarchy intact
```

---

## References & Standards

### WCAG 2.2 Specification
- [W3C WCAG 2.2 Standard](https://www.w3.org/WAI/WCAG22/quickref/)
- Effective since October 5, 2023
- Enforceable under EAA (EU) and ADA (USA as of April 2026)

### React Accessibility Resources
- [React Legacy Docs: Accessibility](https://legacy.reactjs.org/docs/accessibility.html)
- [React Aria Components](https://react-aria.adobe.com/)
- [Ariakit Components](https://ariakit.org/components)

### Keyboard Navigation
- [UXPin: Keyboard Navigation Patterns](https://www.uxpin.com/studio/blog/keyboard-navigation-patterns-complex-widgets/)
- [FreeCodeCamp: Keyboard Accessibility](https://www.freecodecamp.org/news/designing-keyboard-accessibility-for-complex-react-experiences/)

### Testing & Tools
- [axe-core: Accessibility Testing](https://github.com/dequelabs/axe-core)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [jest-axe: Testing Integration](https://github.com/nickcolley/jest-axe)
- [WebAIM: Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WAVE: Web Accessibility Evaluation Tool](https://wave.webaim.org/)

### Best Practices & Guidelines
- [WebAIM Million 2025 Report](https://webaim.org/articles/million) (79.1% low contrast, 59.9% missing labels)
- [AllAccessible: WCAG 2.2 Compliance Checklist](https://www.allaccessible.org/blog/wcag-22-compliance-checklist-implementation-roadmap)
- [Building for Everyone: 2025 Accessibility Guide](https://medium.com/@thewcag/building-for-everyone-the-developers-guide-to-accessible-web-technologies-in-2025-f5b05c92b82b)
- [Web Accessibility Best Practices 2025](https://www.broworks.net/blog/web-accessibility-best-practices-2025-guide)
- [W3C ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)

### Legal Context
- **ADA Title II**: April 2026 deadline for entity-specific compliance
- **EU Accessibility Act**: June 2025 enforcement began
- **Lawsuit Trends**: 37% increase in accessibility lawsuits in 2025
- **Overlay Effectiveness**: Overlay tools (AccessiBe, AudioEye) do NOT provide legal compliance

---

## Document Metadata

- **Created**: February 26, 2026
- **Purpose**: Accessibility preservation for workflow-guardian Claude skill
- **Scope**: React applications, WCAG 2.2 AA compliance
- **Approach**: Pattern detection and matching (not implementation from scratch)
- **Maintenance**: Review quarterly for emerging accessibility patterns
- **Version**: 1.0

---

## Summary: The Core Principle

When Claude adds features to an accessible application:

1. **DETECT** what accessibility patterns exist (ARIA, keyboard, focus, labels, etc.)
2. **DOCUMENT** the exact patterns and implementations found
3. **MATCH** those patterns exactly in new code (don't introduce new approaches)
4. **VALIDATE** that new code follows the same accessibility strategy

**DO NOT**: Implement accessibility from scratch, introduce new ARIA libraries, or change existing patterns.

**DO**: Copy proven patterns, test with existing tools, and preserve what works.
