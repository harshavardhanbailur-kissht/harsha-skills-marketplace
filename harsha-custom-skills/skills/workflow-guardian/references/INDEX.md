# Workflow-Guardian References Index

This directory contains comprehensive guides for preventing breaking changes when adding features to applications.

## Accessibility (A11y) Resources

### 1. **accessibility-preservation.md** (1881 lines, 55KB)
The complete, comprehensive reference for detecting and preserving accessibility patterns.

**Contents:**
- Executive summary of accessibility preservation approach
- WCAG 2.2 compliance requirements (with tables)
- Detection methods for finding existing accessibility patterns
- ARIA pattern preservation guide
- Keyboard navigation preservation patterns
- Focus management strategies
- Screen reader compatibility patterns
- Visual accessibility preservation (contrast, focus indicators, motion)
- 7 common accessibility breakage patterns with examples
- Component-specific pattern matching (buttons, modals, forms, tabs, dropdowns)
- Testing & validation strategies (automated + manual)
- Quick reference checklists
- Comprehensive references and standards

**Best for:** Deep research, comprehensive understanding, implementation details

**Key sections:**
- "Common Accessibility Breakages" - patterns to AVOID
- "Detection Methods" - how to find what's already accessible
- "Component-Specific Pattern Matching" - exact patterns for each UI element
- "Testing & Validation Strategies" - how to verify you didn't break anything

---

### 2. **a11y-quick-start.md** (2.8KB)
Quick reference guide for rapid implementation and testing.

**Contents:**
- One-minute summary of the approach
- Quick detection commands (bash/grep)
- The 3 most common accessibility breakages
- 2-minute testing checklist
- The golden rule: match existing patterns

**Best for:** Quick lookup, team onboarding, before-you-code checklist

**Use when:** You need a fast reference before implementing

---

## Quick Navigation

### Common Questions Answered

**"How do I detect what accessibility is already in use?"**
→ See `accessibility-preservation.md` → Section "Detection Methods: Finding Existing Accessibility"

**"What are the most common ways I'll break accessibility?"**
→ See `accessibility-preservation.md` → Section "Common Accessibility Breakage Patterns"

**"How do I test keyboard navigation?"**
→ See `a11y-quick-start.md` → "Testing Checklist" section
→ OR see `accessibility-preservation.md` → Section "Testing & Validation Strategies"

**"How should I implement a new button/modal/form?"**
→ See `accessibility-preservation.md` → Section "Component-Specific Pattern Matching"

**"What is aria-label vs aria-labelledby?"**
→ See `accessibility-preservation.md` → Section "ARIA Pattern Preservation" → "Labeling & Description"

**"Does my change break focus management?"**
→ See `accessibility-preservation.md` → Section "Focus Management Patterns"

**"What's WCAG 2.2 and why does it matter?"**
→ See `accessibility-preservation.md` → Section "WCAG 2.2 Compliance Requirements"

---

## The Core Principle

When adding features to an accessible application:

1. **DETECT** - Find what accessibility patterns exist (ARIA attributes, keyboard handlers, focus management)
2. **DOCUMENT** - Record the exact patterns and implementations
3. **MATCH** - Use the same pattern in your new code
4. **VALIDATE** - Test with automated tools and manual testing

**Key rule**: Copy patterns from existing similar components. Don't invent new accessibility approaches.

---

## Reference Files Organization

```
references/
├── INDEX.md                          (This file)
├── accessibility-preservation.md     (1881 lines - comprehensive guide)
├── a11y-quick-start.md              (Quick reference)
├── README_SIMILARITY_DETECTION.md   (Pattern detection methodology)
└── ... (other reference materials)
```

---

## Legal Context (2026)

- **WCAG 2.2** is the current standard (October 2023)
- **EU Accessibility Act** is enforceable (June 2025 onwards)
- **ADA Title II** enforcement begins April 2026
- **Accessibility lawsuits** increased 37% in 2025
- **Overlay tools** (AccessiBe, AudioEye) do NOT provide legal compliance

For details, see `accessibility-preservation.md` → "Executive Summary" → "Legal & Business Context"

---

## Most Common Breakages (Summary)

When adding features, watch out for:

1. **Icon buttons without aria-label**
   ```jsx
   <button>✕</button>  // WRONG - no label
   <button aria-label="Close">✕</button>  // RIGHT
   ```

2. **Modals without focus trap**
   ```jsx
   <div role="dialog">  // WRONG - Tab can escape
   <div role="dialog" onKeyDown={...}>  // RIGHT - Tab trapped
   ```

3. **Form inputs without labels**
   ```jsx
   <input type="email" />  // WRONG - no label
   <label htmlFor="email">Email</label><input id="email" />  // RIGHT
   ```

4. **Removing existing aria-* attributes during refactoring**
5. **Breaking heading hierarchy (h1 → h3 skip)**
6. **Adding buttons without keyboard support (Enter/Space)**
7. **Not implementing focus restoration after modal close**

For details, see `accessibility-preservation.md` → "Common Accessibility Breakage Patterns"

---

## Quick Testing (2 minutes)

```javascript
// Automated
import { axe } from 'jest-axe';
const results = await axe(container);
expect(results).toHaveNoViolations();

// Manual Keyboard
- Tab through page
- Enter on buttons
- Space on buttons
- Escape closes modals
- Focus visible everywhere

// Screen Reader
- Icon buttons announced with labels
- Form labels announced with inputs
- Modal announced as dialog
```

For details, see `a11y-quick-start.md` or `accessibility-preservation.md` → "Testing & Validation Strategies"

---

## Tools Referenced

- **axe-core**: Automated accessibility testing
- **jest-axe**: Integration with React Testing Library
- **React Testing Library**: Component testing with accessibility focus
- **WebAIM Contrast Checker**: Manual contrast validation
- **WAVE**: Browser-based accessibility evaluation
- **React Aria**: Adobe's accessibility component library (reference)

---

## Document Metadata

- **Created**: February 26, 2026
- **Approach**: Pattern detection and preservation (not implementation from scratch)
- **Scope**: React applications, WCAG 2.2 AA compliance
- **Updated**: Quarterly
- **Version**: 1.0

---

## Related Files in workflow-guardian

- `SKILL.md` - Main skill documentation
- `README_SIMILARITY_DETECTION.md` - Pattern detection methodology
- `scripts/` - Implementation scripts
- `templates/` - Code templates

---

## Next Steps

1. Read `a11y-quick-start.md` (5 minutes)
2. Reference `accessibility-preservation.md` as needed for specifics
3. Use the quick detection commands before implementing
4. Run automated tests with axe-core
5. Do manual keyboard and screen reader testing
6. Deploy with confidence

---

**Remember**: Match existing patterns. Don't invent new ones. Test before shipping.
