# Mobile Accessibility Checklist

> WCAG 2.2 compliance checklist for mobile interfaces

## Touch Target Requirements (WCAG 2.5.8)

### Size Requirements
- [ ] All interactive elements ≥24×24 CSS pixels (AA minimum)
- [ ] Recommended: ≥44×44 CSS pixels (AAA / iOS standard)
- [ ] Touch targets not overlapping
- [ ] Adequate spacing between targets (≥8px)

### Exceptions
- [ ] Inline links in text may be smaller (but expand on tap)
- [ ] Native controls (browser defaults acceptable)
- [ ] Essential presentation (e.g., map pins)

---

## Perceivable (WCAG Principle 1)

### Text Alternatives (1.1)
- [ ] All images have appropriate alt text
- [ ] Decorative images have empty alt (`alt=""`)
- [ ] Complex images have extended descriptions
- [ ] Icon buttons have accessible labels
- [ ] Audio/video has text alternatives

### Time-Based Media (1.2)
- [ ] Video has captions
- [ ] Audio has transcripts
- [ ] Video has audio descriptions (if needed)
- [ ] Live content has captions (if applicable)

### Adaptable (1.3)
- [ ] Information conveyed through structure (headings, lists)
- [ ] Reading sequence is logical
- [ ] Instructions don't rely solely on sensory characteristics
- [ ] Content adapts to different orientations

### Distinguishable (1.4)
- [ ] Color not the only means of conveying information
- [ ] Text contrast ≥4.5:1 (normal), ≥3:1 (large)
- [ ] UI component contrast ≥3:1
- [ ] Text can be resized to 200% without loss
- [ ] Images of text avoided (use real text)
- [ ] Reflow: content works at 320px width
- [ ] Non-text contrast ≥3:1
- [ ] Text spacing adjustable without breaking

---

## Operable (WCAG Principle 2)

### Keyboard Accessible (2.1)
- [ ] All functionality available via keyboard/focus
- [ ] No keyboard traps
- [ ] Keyboard shortcuts can be disabled/remapped

### Enough Time (2.2)
- [ ] Timing can be adjusted for time limits
- [ ] Moving content can be paused
- [ ] No interruptions (or can be postponed)
- [ ] Session timeout warnings provided

### Seizures & Physical (2.3)
- [ ] No flashing more than 3 times per second
- [ ] Motion can be disabled

### Navigable (2.4)
- [ ] Skip links available
- [ ] Page has descriptive title
- [ ] Focus order is logical
- [ ] Link purpose clear from text
- [ ] Multiple ways to find pages
- [ ] Headings and labels descriptive
- [ ] Focus indicator visible

### Input Modalities (2.5)
- [ ] Gestures have single-pointer alternatives
- [ ] Down-event doesn't trigger action (use up-event)
- [ ] Accessible name matches visible label
- [ ] Motion-triggered actions have alternatives
- [ ] **Target size minimum 24×24px (WCAG 2.5.8)**
- [ ] **Dragging has alternatives (WCAG 2.5.7)**

---

## Understandable (WCAG Principle 3)

### Readable (3.1)
- [ ] Page language declared (`lang` attribute)
- [ ] Language changes marked

### Predictable (3.2)
- [ ] Focus doesn't trigger context change
- [ ] Input doesn't trigger unexpected change
- [ ] Navigation consistent across pages
- [ ] Components identified consistently

### Input Assistance (3.3)
- [ ] Error identification clear
- [ ] Labels/instructions provided
- [ ] Error suggestions offered
- [ ] Error prevention for important actions
- [ ] **Accessible authentication (no cognitive tests) (WCAG 3.3.8)**

---

## Robust (WCAG Principle 4)

### Compatible (4.1)
- [ ] Valid HTML
- [ ] Name, role, value for custom components
- [ ] Status messages announced to assistive tech

---

## Mobile-Specific Testing

### Screen Reader Testing (iOS)
- [ ] VoiceOver can navigate all content
- [ ] Swipe gestures work correctly
- [ ] Rotor options appropriate
- [ ] Custom actions announced
- [ ] Modal focus trapped correctly

### Screen Reader Testing (Android)
- [ ] TalkBack can navigate all content
- [ ] Swipe gestures work correctly
- [ ] Explore by touch works
- [ ] Content descriptions accurate
- [ ] Live regions update correctly

### Gesture Alternatives
| Gesture | Alternative Provided |
|---------|---------------------|
| Swipe to delete | [ ] Delete button |
| Pinch to zoom | [ ] Zoom controls |
| Drag to reorder | [ ] Move buttons |
| Long-press menu | [ ] Menu button |
| Pull to refresh | [ ] Refresh button |

### Dynamic Content
- [ ] Loading states announced
- [ ] Content updates announced (`aria-live`)
- [ ] Errors announced immediately
- [ ] Success confirmations announced
- [ ] Focus managed after content change

---

## Legal Compliance

### European Accessibility Act (EAA)
- [ ] EN 301 549 compliant (WCAG 2.1 AA)
- [ ] Effective date: June 28, 2025
- [ ] Accessibility statement published

### ADA (United States)
- [ ] WCAG 2.1 AA (recommended standard)
- [ ] No discrimination based on disability
- [ ] Reasonable accommodations available

### Section 508
- [ ] WCAG 2.0 AA compliant
- [ ] Applicable to federal agencies

---

## Tools for Testing

### Automated
- [ ] Axe DevTools
- [ ] WAVE
- [ ] Lighthouse Accessibility
- [ ] Pa11y

### Manual
- [ ] VoiceOver (iOS)
- [ ] TalkBack (Android)
- [ ] Switch Control testing
- [ ] Keyboard navigation
- [ ] Color contrast analyzer

---

## Signoff

**WCAG Version:** 2.2
**Conformance Level:** AA / AAA

| Principle | Pass | Fail | N/A |
|-----------|------|------|-----|
| Perceivable | | | |
| Operable | | | |
| Understandable | | | |
| Robust | | | |

**VoiceOver Tested:** [ ] Yes  **TalkBack Tested:** [ ] Yes

**Critical Issues:**
1. 
2. 

**Remediation Plan:**
1. 
2. 

**Auditor:** _________________ **Date:** _________________
