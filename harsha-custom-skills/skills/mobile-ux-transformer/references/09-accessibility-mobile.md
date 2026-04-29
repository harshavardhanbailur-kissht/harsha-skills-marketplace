# Mobile Accessibility

> WCAG 2.2 compliance and mobile-specific accessibility requirements

## Legal Landscape (2024-2025)

### Current Regulations

| Regulation | Effective | Requirement | Scope |
|------------|-----------|-------------|-------|
| **European Accessibility Act** | June 28, 2025 | EN 301 549 (WCAG 2.1 AA) | E-commerce, banking, transportation, telecom |
| **ADA Title II** (US) | April 2026-2027 | WCAG 2.1 AA | State/local government digital services |
| **ADA Title III** (US) | Ongoing | WCAG 2.1 AA (de facto) | Public accommodations |
| **Section 508** (US) | Current | WCAG 2.0 AA | Federal agencies |
| **AODA** (Ontario) | Current | WCAG 2.0 AA | Ontario organizations |

### Lawsuit Statistics

- **4,061** ADA digital accessibility lawsuits in 2022
- **2× increase** from 2018 levels
- **97%** of websites fail basic accessibility
- **$100 return per $1** invested in accessibility (Forrester)

---

## WCAG 2.2 Mobile-Critical Success Criteria

### Touch Target Size (2.5.8)

**Minimum:** 24×24 CSS pixels (Level AA)
**Enhanced:** 44×44 CSS pixels (Level AAA)

```css
/* Meet AA minimum */
.touch-target-aa {
  min-width: 24px;
  min-height: 24px;
}

/* Target AAA for better UX */
.touch-target-aaa {
  min-width: 44px;
  min-height: 44px;
}

/* Inline links need padding */
.inline-link {
  padding: 8px 4px;
  margin: -8px -4px;
}
```

### Target Spacing

The sum of target size + spacing must be at least 24px.

```css
/* Example: 20px button + 4px spacing = 24px total */
.button-group {
  display: flex;
  gap: 4px;
}

.button-group .button {
  min-width: 20px;
  min-height: 20px;
}
```

### Dragging Movements (2.5.7)

Any functionality requiring dragging must have a single-pointer alternative.

```html
<!-- Drag to reorder list -->
<ul class="reorderable">
  <li>
    <span class="drag-handle" aria-label="Drag to reorder">⋮⋮</span>
    <span class="item-text">Item 1</span>
    <!-- Single-pointer alternative -->
    <button class="move-up" aria-label="Move up">↑</button>
    <button class="move-down" aria-label="Move down">↓</button>
  </li>
</ul>
```

### Accessible Authentication (3.3.8)

Authentication must not require:
- Memorizing passwords/codes
- Solving puzzles (CAPTCHA)
- Cognitive function tests

**Allowed methods:**
- Password managers (autocomplete enabled)
- Copy-paste functionality
- Biometrics (Face ID, fingerprint)
- Magic links
- OAuth/SSO

```html
<!-- Enable password manager autofill -->
<input 
  type="password" 
  autocomplete="current-password"
  id="password"
  name="password">

<!-- OTP autofill from SMS -->
<input 
  type="text" 
  inputmode="numeric" 
  autocomplete="one-time-code"
  pattern="[0-9]{6}"
  maxlength="6">
```

---

## Screen Reader Support

### Mobile Screen Reader Usage

| Screen Reader | Platform | Market Share |
|--------------|----------|--------------|
| VoiceOver | iOS | 72% |
| TalkBack | Android | 29% |
| Other | Various | <1% |

### Essential VoiceOver Gestures

| Gesture | Action |
|---------|--------|
| Single tap | Select item |
| Double tap | Activate |
| Swipe left/right | Previous/next item |
| Three-finger swipe | Scroll |
| Two-finger tap | Pause speech |
| Two-finger scrub (Z) | Go back |

### Essential TalkBack Gestures

| Gesture | Action |
|---------|--------|
| Single tap | Select item |
| Double tap | Activate |
| Swipe left/right | Previous/next item |
| Two-finger scroll | Scroll |
| Swipe down then right | Global context menu |
| Swipe up then right | Local context menu |

---

## ARIA for Mobile

### Accessible Labels

```html
<!-- Icon button needs label -->
<button aria-label="Close dialog">
  <svg aria-hidden="true"><!-- X icon --></svg>
</button>

<!-- Complex label with description -->
<button 
  aria-label="Add to cart" 
  aria-describedby="price-info">
  <svg aria-hidden="true"><!-- Cart icon --></svg>
</button>
<span id="price-info" class="sr-only">iPhone 15 Pro - $999</span>
```

### Live Regions

```html
<!-- Announce dynamic updates -->
<div 
  role="status" 
  aria-live="polite" 
  aria-atomic="true"
  class="cart-status">
  3 items in cart
</div>

<!-- Urgent announcements -->
<div 
  role="alert" 
  aria-live="assertive">
  Form submitted successfully
</div>
```

### Modal/Dialog

```html
<div 
  role="dialog" 
  aria-modal="true" 
  aria-labelledby="dialog-title"
  aria-describedby="dialog-desc">
  <h2 id="dialog-title">Confirm Delete</h2>
  <p id="dialog-desc">Are you sure you want to delete this item?</p>
  <button>Cancel</button>
  <button>Delete</button>
</div>
```

### Tab Navigation

```html
<div role="tablist" aria-label="Content sections">
  <button 
    role="tab" 
    aria-selected="true" 
    aria-controls="panel-1"
    id="tab-1">
    Overview
  </button>
  <button 
    role="tab" 
    aria-selected="false" 
    aria-controls="panel-2"
    id="tab-2">
    Details
  </button>
</div>

<div 
  role="tabpanel" 
  id="panel-1" 
  aria-labelledby="tab-1">
  Overview content...
</div>

<div 
  role="tabpanel" 
  id="panel-2" 
  aria-labelledby="tab-2"
  hidden>
  Details content...
</div>
```

---

## Color & Contrast

### Contrast Requirements

| Content | Minimum Ratio (AA) | Enhanced (AAA) |
|---------|-------------------|----------------|
| Normal text | 4.5:1 | 7:1 |
| Large text (18pt+/14pt bold+) | 3:1 | 4.5:1 |
| UI components | 3:1 | 3:1 |
| Graphical objects | 3:1 | 3:1 |

### Testing Contrast

```javascript
// Calculate contrast ratio
function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function getLuminance(hex) {
  const rgb = hexToRgb(hex);
  const [r, g, b] = rgb.map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
```

### Color Not Sole Indicator

```html
<!-- ❌ Bad: Color only indicates error -->
<input class="error" style="border-color: red">

<!-- ✅ Good: Color + icon + text -->
<div class="form-field error">
  <input aria-invalid="true" aria-describedby="error-msg">
  <span class="error-icon" aria-hidden="true">⚠️</span>
  <span id="error-msg" class="error-message">Email is required</span>
</div>
```

---

## Motion & Animation

### Reduced Motion

```css
/* Provide reduced motion alternative */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Or selectively disable specific animations */
.animated-element {
  animation: slideIn 0.3s ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    opacity: 1;
  }
}
```

### Auto-Playing Content

```html
<!-- Video with controls, no autoplay -->
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English">
</video>

<!-- If autoplay needed, provide pause control -->
<div class="video-container">
  <video autoplay muted loop id="bg-video">...</video>
  <button 
    class="pause-button" 
    aria-label="Pause background video"
    onclick="document.getElementById('bg-video').paused ? 
             document.getElementById('bg-video').play() : 
             document.getElementById('bg-video').pause()">
    ⏸️
  </button>
</div>
```

---

## Focus Management

### Focus Visibility

```css
/* Custom focus indicator */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Remove default only when custom provided */
:focus:not(:focus-visible) {
  outline: none;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :focus-visible {
    outline-width: 3px;
  }
}
```

### Focus Trapping in Modals

```javascript
class FocusTrap {
  constructor(element) {
    this.element = element;
    this.focusableSelectors = [
      'button:not([disabled])',
      'a[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])'
    ].join(',');
  }
  
  activate() {
    this.previousFocus = document.activeElement;
    const focusable = this.element.querySelectorAll(this.focusableSelectors);
    this.firstFocusable = focusable[0];
    this.lastFocusable = focusable[focusable.length - 1];
    
    this.element.addEventListener('keydown', this.handleKeydown.bind(this));
    this.firstFocusable?.focus();
  }
  
  handleKeydown(e) {
    if (e.key !== 'Tab') return;
    
    if (e.shiftKey && document.activeElement === this.firstFocusable) {
      e.preventDefault();
      this.lastFocusable.focus();
    } else if (!e.shiftKey && document.activeElement === this.lastFocusable) {
      e.preventDefault();
      this.firstFocusable.focus();
    }
  }
  
  deactivate() {
    this.element.removeEventListener('keydown', this.handleKeydown);
    this.previousFocus?.focus();
  }
}
```

---

## Testing Checklist

### Automated Testing

- [ ] axe-core audit passes
- [ ] Lighthouse accessibility score >90
- [ ] Color contrast checker passes
- [ ] HTML validation (no ARIA errors)

### Manual Testing

- [ ] VoiceOver navigation works logically (iOS)
- [ ] TalkBack navigation works logically (Android)
- [ ] All interactive elements accessible via swipe
- [ ] Focus order matches visual order
- [ ] Touch targets ≥44×44px (or ≥24px with spacing)
- [ ] Text resizable to 200% without loss
- [ ] Works in landscape and portrait
- [ ] Content visible with system font size increased
- [ ] Color is not sole indicator of information
- [ ] Animations can be disabled

### Screen Reader Testing Script

```
1. Enable VoiceOver/TalkBack
2. Navigate through entire page with swipes
3. Verify all content is announced
4. Verify all controls are operable
5. Test forms (labels, errors, submission)
6. Test modals (focus trap, close)
7. Test dynamic content (live regions)
8. Disable VoiceOver/TalkBack
```

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Missing button label | Add `aria-label` or visible text |
| Image without alt | Add `alt=""` (decorative) or descriptive alt |
| Form without labels | Associate `<label>` with `for` attribute |
| Color-only error | Add icon, text, or border |
| Auto-playing video | Add pause control, or remove autoplay |
| Small touch targets | Increase to 44×44px minimum |
| No focus indicator | Add `:focus-visible` styles |
| Modal doesn't trap focus | Implement focus trap |
| Dynamic content not announced | Use `aria-live` regions |
| Swipe gesture only | Provide button alternative |

---

## Resources

- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [Apple Accessibility](https://developer.apple.com/accessibility/)
- [Android Accessibility](https://developer.android.com/guide/topics/ui/accessibility)
- [axe-core](https://github.com/dequelabs/axe-core)
- [WebAIM](https://webaim.org/)
