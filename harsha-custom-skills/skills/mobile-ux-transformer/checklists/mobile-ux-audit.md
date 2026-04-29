# Mobile UX Audit Checklist

> Comprehensive checklist for evaluating mobile interface quality

## Pre-Audit Setup

- [ ] Identify target devices (iOS, Android, specific models)
- [ ] Define breakpoints to test (360px, 375px, 390px, 412px, etc.)
- [ ] Prepare real devices for testing (not just simulators)
- [ ] Set up screen recording for usability sessions
- [ ] Define key user journeys to evaluate

---

## Touch & Interaction

### Touch Targets
- [ ] All buttons/links ≥44×44px (iOS) / 48×48dp (Android)
- [ ] Touch targets have ≥8px spacing between them
- [ ] No overlapping touch targets
- [ ] Close/dismiss buttons easily reachable
- [ ] Form inputs meet minimum size requirements

### Thumb Zone
- [ ] Primary actions in bottom 40% of screen
- [ ] Navigation accessible with one hand
- [ ] Destructive actions in top corners (harder to reach)
- [ ] FAB positioned in lower right (if used)
- [ ] No critical actions requiring two-handed use

### Gestures
- [ ] Standard gestures work as expected (swipe, pinch, etc.)
- [ ] Custom gestures have visible hints/onboarding
- [ ] All gestures have button alternatives (accessibility)
- [ ] Edge gestures don't conflict with system navigation
- [ ] Pull-to-refresh implemented where expected

### Feedback
- [ ] Visual feedback on all taps
- [ ] Haptic feedback for significant actions
- [ ] Loading states clearly indicated
- [ ] Success/error states communicated
- [ ] Button states (default, pressed, disabled) distinguishable

---

## Navigation

### Pattern
- [ ] Appropriate pattern for content type (tabs, drawer, etc.)
- [ ] 3-5 items maximum in bottom navigation
- [ ] Icons accompanied by labels
- [ ] Current location clearly indicated
- [ ] Consistent navigation across screens

### Back Navigation
- [ ] iOS: Edge swipe works
- [ ] Android: System back works correctly
- [ ] Back button visible when needed
- [ ] Navigation history maintained properly
- [ ] Deep links return to correct context

### Search
- [ ] Search easily accessible
- [ ] Search results relevant and well-formatted
- [ ] Recent/suggested searches provided
- [ ] Clear/cancel search easy to tap
- [ ] Keyboard dismissed appropriately

---

## Typography & Readability

### Text Size
- [ ] Body text ≥16px (prevents iOS zoom)
- [ ] Line height 1.4-1.6 for body text
- [ ] Line length 30-40 characters on mobile
- [ ] Headings have clear hierarchy
- [ ] Text resizable to 200% without breaking

### Contrast
- [ ] Text contrast ≥4.5:1 (normal text)
- [ ] Large text contrast ≥3:1
- [ ] UI components contrast ≥3:1
- [ ] Works in both light and dark modes
- [ ] No text over complex backgrounds

### Readability
- [ ] No horizontal scrolling for text
- [ ] Important text not clipped/truncated
- [ ] Adequate paragraph spacing
- [ ] Lists properly formatted
- [ ] Links distinguishable from body text

---

## Forms

### Layout
- [ ] Single-column layout
- [ ] Top-aligned or floating labels
- [ ] Logical field order
- [ ] Related fields grouped
- [ ] Progress indicator for multi-step forms

### Inputs
- [ ] Correct input types (email, tel, number, etc.)
- [ ] Autocomplete attributes set
- [ ] Input hints/placeholder text helpful
- [ ] Character limits communicated
- [ ] Required fields indicated

### Validation
- [ ] Inline validation as user types
- [ ] Clear error messages
- [ ] Errors associated with fields (aria-describedby)
- [ ] Submit disabled until valid (or clear feedback)
- [ ] Focus moves to first error on submit

### Keyboard
- [ ] Appropriate keyboard for each field
- [ ] "Next" button moves to next field
- [ ] "Done" dismisses keyboard or submits
- [ ] Keyboard doesn't cover active field
- [ ] Form scrolls properly with keyboard open

---

## Performance

### Core Web Vitals
- [ ] LCP ≤2.5 seconds
- [ ] INP ≤200 milliseconds
- [ ] CLS ≤0.1

### Loading
- [ ] Initial load under 3 seconds on 4G
- [ ] Skeleton/loading states for async content
- [ ] Images lazy loaded (except LCP)
- [ ] No layout shifts during load
- [ ] Critical CSS inlined

### Resources
- [ ] Total page weight ≤500KB compressed
- [ ] JavaScript ≤170KB
- [ ] Images optimized (WebP/AVIF)
- [ ] Fonts subset and preloaded
- [ ] Third-party scripts audited

### Offline
- [ ] Graceful handling of offline state
- [ ] Meaningful offline page (if PWA)
- [ ] Data cached appropriately
- [ ] User informed of connectivity issues

---

## Accessibility

### Screen Reader
- [ ] All content accessible via VoiceOver/TalkBack
- [ ] Logical reading order
- [ ] Images have alt text
- [ ] Buttons/links have accessible names
- [ ] Dynamic content announced (aria-live)

### Focus
- [ ] Focus indicator visible
- [ ] Focus order matches visual order
- [ ] Focus trapped in modals
- [ ] Focus restored after modal close
- [ ] Skip link available

### Motion
- [ ] Respects prefers-reduced-motion
- [ ] No auto-playing animations
- [ ] Animations can be paused/stopped
- [ ] No flashing content (seizure risk)

### Alternative Interactions
- [ ] All gestures have button alternatives
- [ ] Drag operations have alternatives
- [ ] Time-based actions can be extended
- [ ] No cognitive function tests for auth

---

## Platform Conventions

### iOS
- [ ] Safe areas respected (notch, home indicator)
- [ ] Standard iOS patterns used
- [ ] Translucency/blur effects appropriate
- [ ] Dynamic Type supported
- [ ] SF Symbols used (or appropriate icons)

### Android
- [ ] Edge-to-edge design implemented
- [ ] Material Design patterns followed
- [ ] Predictive back supported (Android 14+)
- [ ] System bars handled properly
- [ ] Foldable considerations (if applicable)

---

## Content

### Hierarchy
- [ ] Most important content visible first
- [ ] Progressive disclosure implemented
- [ ] Collapsible sections for long content
- [ ] Scanning-friendly (headers, bullets)
- [ ] Key actions always visible

### Media
- [ ] Images appropriately sized
- [ ] Video has controls
- [ ] Captions available for video
- [ ] Audio has transcripts
- [ ] No auto-playing media

---

## Error Handling

- [ ] Error messages human-readable
- [ ] Clear recovery path from errors
- [ ] Network errors handled gracefully
- [ ] Form errors clearly indicated
- [ ] 404/error pages mobile-friendly

---

## Testing Signoff

### Devices Tested
- [ ] iPhone (specify model)
- [ ] Android (specify model)
- [ ] Tablet (if applicable)

### Conditions Tested
- [ ] Portrait orientation
- [ ] Landscape orientation
- [ ] Dark mode
- [ ] Light mode
- [ ] With VoiceOver/TalkBack
- [ ] With text scaled to 200%
- [ ] On slow network (3G)

### Audit Summary

| Category | Pass | Fail | N/A |
|----------|------|------|-----|
| Touch & Interaction | | | |
| Navigation | | | |
| Typography | | | |
| Forms | | | |
| Performance | | | |
| Accessibility | | | |
| Platform | | | |
| Content | | | |
| Error Handling | | | |

**Overall Score:** ___ / 100

**Critical Issues:**
1. 
2. 
3. 

**Recommendations:**
1. 
2. 
3. 

**Audited By:** _________________ **Date:** _________________
