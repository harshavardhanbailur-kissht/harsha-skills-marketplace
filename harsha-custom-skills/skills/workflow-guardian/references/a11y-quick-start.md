# Accessibility Preservation - Quick Start Guide

## One-Minute Summary

When adding features to an accessible application:

1. **DETECT** existing ARIA, keyboard handlers, focus patterns
2. **COPY** exact implementation from similar existing components
3. **VALIDATE** with automated testing (axe) and manual keyboard testing
4. **SHIP** knowing you didn't break accessibility

## Quick Detection Commands

```bash
# What ARIA is in use?
grep -r "aria-" /src --include="*.jsx" | sort | uniq

# What keyboard handlers exist?
grep -r "onKeyDown\|onKeyUp" /src --include="*.jsx"

# How are forms labeled?
grep -r "htmlFor\|aria-labelledby\|aria-label" /src --include="*.jsx" | grep input

# Are there modals with focus traps?
grep -r "role=\"dialog\"" /src --include="*.jsx"

# What focus patterns?
grep -r "useRef.*focus\|\.focus()\|tabIndex\|autoFocus" /src --include="*.jsx"
```

## The 3 Accessibility Breakages to Avoid

### 1. Icon buttons without aria-label
```jsx
// WRONG
<button>✕</button>  // Screen reader: "button" (no label)

// RIGHT
<button aria-label="Close">✕</button>
```

### 2. Modal without focus trap
```jsx
// WRONG
<div role="dialog">...</div>  // User can Tab out

// RIGHT
<div role="dialog" onKeyDown={(e) => {
  if (e.key === 'Tab' && e.shiftKey && ...) {
    e.preventDefault();
    lastElement.focus();
  }
}}>...</div>
```

### 3. Form inputs without labels
```jsx
// WRONG
<input type="email" />  // No label

// RIGHT
<label htmlFor="email">Email</label>
<input id="email" type="email" />
```

## Testing Checklist (2 minutes)

### Automated
```javascript
import { axe, toHaveNoViolations } from 'jest-axe';

test('component accessibility', async () => {
  const { container } = render(<YourComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Manual Keyboard
- [ ] Tab through page in logical order
- [ ] Buttons work with Enter AND Space
- [ ] Forms submittable with Enter
- [ ] Modals: Tab doesn't escape, Escape closes
- [ ] Focus visible on everything you can interact with

### Screen Reader
- [ ] Icon buttons announced with names
- [ ] Form labels announced with inputs
- [ ] Modal title announced as dialog
- [ ] Images have alt text (or alt="" for decorative)

## The Golden Rule

**Match the exact pattern from existing similar components.**

If buttons use `aria-label` for icons, new icon buttons use `aria-label`.
If modals use `useRef + focus()`, new modals use `useRef + focus()`.
If forms use `htmlFor`, new forms use `htmlFor`.

Copy-paste your way to consistency.

## References

- [Full Accessibility Preservation Guide](./accessibility-preservation.md) (1800+ lines)
- WCAG 2.2: https://www.w3.org/WAI/WCAG22/quickref/
- React Aria: https://react-aria.adobe.com/
- axe Testing: https://github.com/dequelabs/axe-core
