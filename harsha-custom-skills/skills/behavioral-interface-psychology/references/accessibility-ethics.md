# Accessibility & Ethics Reference

## WCAG Requirements & Research

### Touch Target Requirements

**WCAG 2.2 Level AA (SC 2.5.8):**
- Minimum target size: 24×24 CSS pixels
- OR minimum spacing of 24px between targets

**WCAG 2.2 Level AAA:**
- Minimum target size: 44×44 CSS pixels

**Platform Guidelines:**
| Platform | Minimum | Recommended |
|----------|---------|-------------|
| Apple iOS | 44×44pt | 44×44pt |
| Android Material | 48×48dp (~9mm) | 48×48dp |
| WCAG AA | 24×24px | - |
| WCAG AAA | 44×44px | 44×44px |

**Research Validation:**
- Error rates at 24px: 15%
- Error rates at 44px: 3%
- **5× error difference** between minimum AA and AAA

**Touch Accuracy Formula (Bi & Zhai, 2016):**
```
P(success) = 1 - exp(-πW²/4σ²)
```
Where W = target width, σ = touch precision (~8-10mm)

### Contrast Requirements

**WCAG 2.x Requirements:**
| Level | Normal Text | Large Text | UI Components |
|-------|-------------|------------|---------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | Not specified |

Large text = 18pt (24px) or 14pt (18.5px) bold

**APCA (WCAG 3.0 Candidate Algorithm):**
- Preferred body text: Lc 90
- Minimum body text: Lc 75
- Large text: Lc 60
- Accounts for: polarity, font size, weight, spatial frequency

**Age-Related Contrast Needs:**
- Contrast sensitivity decline: 1.4-2.5× reduced from age 20 to 74
- Cataracts reduce contrast sensitivity significantly
- Higher contrast benefits ALL users, not just those with disabilities

### Reduced Motion Requirements

**WCAG 2.1 SC 2.3.3 (Animation from Interactions):**
- Motion animation triggered by interaction can be disabled
- Exception: animation essential to functionality

**Vestibular Dysfunction Prevalence:**
- 35% of adults 40+ have vestibular dysfunction
- Motion can trigger vertigo, nausea, disorientation

**Implementation:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Safe Motion Alternatives:**
- Opacity fades (generally safe)
- Instant state changes
- Subtle scale (avoid large transforms)

### Keyboard Navigation

**Keyboard Usage Research:**
- 81-90% never use keyboard shortcuts
- Ctrl+F non-users: 90% (search within page)
- Command palette (Cmd+K): improves discoverability

**Requirements:**
- All interactive elements keyboard accessible
- Visible focus indicators (2px minimum, 3:1 contrast)
- Logical tab order (follows visual flow)
- Skip links for repetitive content

**Focus Management Patterns:**
```javascript
// Focus trap for modals
const focusableElements = modal.querySelectorAll(
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
);
const firstFocusable = focusableElements[0];
const lastFocusable = focusableElements[focusableElements.length - 1];

// Return focus when modal closes
previouslyFocusedElement.focus();
```

### Screen Reader Optimization

**ARIA Usage Guidelines:**
- First rule of ARIA: Don't use ARIA (use semantic HTML)
- Second rule: Don't change native semantics unless necessary
- Third rule: All interactive ARIA controls must be keyboard accessible

**Common ARIA Patterns:**
```html
<!-- Live regions for dynamic content -->
<div aria-live="polite" aria-atomic="true">
  <!-- Content updates announced -->
</div>

<!-- Custom controls need roles -->
<div role="button" tabindex="0" aria-pressed="false">
  Toggle
</div>

<!-- Accessible names -->
<button aria-label="Close dialog">×</button>
```

**Testing Requirements:**
- Test with actual screen readers (NVDA, VoiceOver, JAWS)
- Automated tools catch only ~30% of issues
- Manual testing essential

---

## Dark Patterns & Manipulation Ethics

### Dark Pattern Prevalence Research

**Princeton/University of Chicago Study (2019):**
- 10% of 11,000 e-commerce sites employ deceptive practices
- Most common: urgency, scarcity, social proof manipulation

**Zurich University Study (Mobile Apps):**
- 95% of 240 Google Play apps used dark patterns
- Privacy-related dark patterns most prevalent

**Categories of Dark Patterns:**
1. **Nagging** - Repeated requests for action
2. **Obstruction** - Making things difficult (e.g., cancellation)
3. **Sneaking** - Hidden costs, forced continuity
4. **Interface Interference** - Confusing UI, trick questions
5. **Forced Action** - Requiring unnecessary steps
6. **Social Engineering** - Manufactured urgency/scarcity

### Manipulation vs Persuasion Thresholds

**Scarcity Signals:**
| Pattern | Ethics |
|---------|--------|
| Actual inventory display | ✓ Legitimate |
| "Only 3 left!" (if true) | ✓ Legitimate |
| Fake countdown timers | ✗ Manipulation |
| Artificial scarcity | ✗ Manipulation |
| Impact: Fake urgency damages brand trust up to 45% |

**Social Proof:**
| Pattern | Ethics |
|---------|--------|
| Actual review counts | ✓ Legitimate |
| Real purchase notifications | ✓ Legitimate |
| Fabricated activity indicators | ✗ Manipulation |
| Filtered reviews hiding negative | ✗ Manipulation |

**Defaults:**
| Pattern | Ethics |
|---------|--------|
| User-beneficial defaults | ✓ Legitimate |
| Privacy-protective defaults | ✓ Legitimate |
| Pre-checked consent boxes | ✗ Illegal (GDPR) |
| Opt-out buried in settings | ✗ Manipulation |

### Regulatory Landscape

**GDPR (EU):**
- Pre-checked consent boxes prohibited
- Withdrawal must be as easy as giving consent
- Dark patterns explicitly targeted in enforcement
- Meta fined €1.3 billion (2023)

**COPPA (US - Children):**
- Applies to children under 13
- Verifiable parental consent required
- Prohibition on behavioral advertising to children
- FTC Epic Games: $275M COPPA violations + $245M refunds

**California Age-Appropriate Design Code (2024):**
- Applies to users under 18
- Bans dark patterns targeting minors
- Privacy by default for children
- Requires Data Protection Impact Assessments

**UK Online Safety Act 2023:**
- Content moderation requirements
- Age verification obligations
- Design safety for children

**EU Digital Services Act:**
- Platform design obligations
- Algorithmic transparency
- Prohibition on deceptive interface practices

**FTC Actions (US):**
- Increased enforcement on dark patterns
- Focus on subscription traps, hidden fees
- "Click to cancel" rule for subscriptions

### Ethical Design Framework

**Deceptive by Design Test:**
1. Would users feel deceived if they understood the mechanism?
2. Does it exploit cognitive biases against user interest?
3. Would the company be embarrassed if pattern was publicized?
4. Does it make the undesired action artificially difficult?

**Autonomy-Preserving Design:**
- Clear information before decisions
- Equal prominence for all options
- Easy reversibility
- No artificial urgency or scarcity
- Transparent defaults with easy changes

---

## Cognitive Accessibility

### Attention & Focus Support

**ADHD Considerations:**
- Minimize distractions in critical paths
- Clear visual hierarchy
- Progress indicators for multi-step processes
- Save state for interrupted sessions

**Autism Spectrum Considerations:**
- Predictable, consistent interfaces
- Clear, literal language
- Avoid ambiguous icons without labels
- Sensory sensitivity (motion, contrast, sound)

### Reading & Comprehension Support

**Dyslexia Accommodations:**

**DEBUNKED - Specialized Fonts:**
- OpenDyslexic/Dyslexie: NO benefit in peer-reviewed studies
- Wery & Diliberto (2017), Kuster et al. (2018): N=170+ participants
- Font shape is NOT the factor

**VALIDATED - Spacing Benefits:**
- Extra-large letter spacing (+18%): 20% faster reading
- 50% fewer errors (Zorzi et al. 2012, N=94)
- Increased line spacing: measurable improvement

**Evidence-Based Accommodations:**
- Increased letter spacing (letter-spacing: 0.12em minimum)
- Increased word spacing (word-spacing: 0.16em minimum)
- Line height 1.5-2.0×
- Left-aligned text (not justified)
- Short line lengths (50-75 characters)

### Memory Support

**Working Memory Limitations:**
- 4±1 chunks (Cowan 2001)
- Progressive disclosure of complexity
- Clear state indication
- Undo/redo support
- Auto-save with visible confirmation

### Low-Literacy Support

**Plain Language Principles:**
- Short sentences (15-20 words average)
- Common words (avoid jargon)
- Active voice
- One idea per paragraph
- Meaningful headings

**Visual Support:**
- Icons WITH labels
- Step-by-step with numbers
- Examples and illustrations
- Consistent terminology

---

## Accessibility Across Modalities

### Visual Impairment Support

**Low Vision (Not Blindness):**
- Scalable text (up to 200%)
- High contrast options
- Avoid text in images
- Sufficient spacing

**Color Vision Deficiency:**
- 8% males, 0.5% females affected
- Never use color alone for meaning
- Provide secondary indicators (icons, patterns, labels)
- Test with simulation tools

**Blindness:**
- Full screen reader compatibility
- Descriptive alt text for meaningful images
- Proper heading structure
- Accessible data visualizations (tables, text alternatives)

### Hearing Impairment Support

**Deaf/Hard of Hearing:**
- Captions for video content
- Transcripts for audio
- Visual alternatives for audio cues
- Sign language interpretation (where feasible)

### Motor Impairment Support

**Physical Limitations:**
- Large touch targets (minimum 44×44px)
- Adequate spacing between targets
- Alternatives to dragging
- Keyboard accessibility
- Voice control compatibility
- Adjustable timeouts

**Tremor Accommodations:**
- Hover delay before activation
- Confirmation for destructive actions
- Undo capabilities
- Avoid precision-required interactions

---

## Code Detection Patterns

### Accessibility Implementation Signals

**Semantic HTML Usage:**
```html
<!-- GOOD: Semantic -->
<nav aria-label="Main navigation">
  <button aria-expanded="false" aria-controls="menu">Menu</button>
  <ul id="menu">
    <li><a href="/home">Home</a></li>
  </ul>
</nav>

<!-- POOR: Divs with handlers -->
<div onclick="toggleMenu()">Menu</div>
<div id="menu">
  <div onclick="navigate('/home')">Home</div>
</div>
```

**Focus Management:**
```javascript
// Check for focus trap implementation
const trapFocus = (element) => {
  const focusableEls = element.querySelectorAll(focusableSelectors);
  // Implementation should exist for modals/dialogs
};

// Check for focus restoration
modalCloseButton.addEventListener('click', () => {
  modal.close();
  triggerButton.focus(); // Must restore focus
});
```

**Skip Links:**
```html
<!-- Should be first focusable element -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

**Reduced Motion Respect:**
```css
/* Check for this media query */
@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}
```

### Dark Pattern Detection

**Subscription Cancellation Flow:**
```javascript
// RED FLAG: Cancellation requires multiple steps
const cancelSteps = [
  'confirm-intent',
  'select-reason', 
  'speak-to-agent',  // Obstruction
  'counter-offer',   // Nagging
  'final-confirm'
];

// COMPLIANT: Direct cancellation
const cancel = async () => {
  await api.cancelSubscription();
  showConfirmation();
};
```

**Consent Implementation:**
```html
<!-- VIOLATION: Pre-checked -->
<input type="checkbox" checked name="marketing">

<!-- COMPLIANT: Unchecked default -->
<input type="checkbox" name="marketing">

<!-- VIOLATION: Dark pattern button styling -->
<button class="btn-primary">Accept All</button>
<button class="text-gray-400 text-xs">Manage Preferences</button>

<!-- COMPLIANT: Equal prominence -->
<button class="btn-secondary">Accept All</button>
<button class="btn-secondary">Manage Preferences</button>
```

**Fake Urgency Detection:**
```javascript
// RED FLAG: Timer that resets or is not based on real deadline
const fakeTimer = setInterval(() => {
  if (timeLeft <= 0) {
    timeLeft = 3600; // Resets!
  }
}, 1000);

// LEGITIMATE: Real deadline
const realDeadline = new Date('2024-12-25T23:59:59');
const timeLeft = realDeadline - Date.now();
```

---

## Testing & Validation

### Automated Testing Limitations

**What Automated Tools Catch (~30%):**
- Missing alt text
- Contrast ratio failures
- Missing form labels
- Invalid ARIA usage
- Heading hierarchy issues

**What Requires Manual Testing (~70%):**
- Screen reader user experience
- Keyboard navigation logic
- Focus management
- Content comprehension
- Cognitive accessibility

### Testing Tools

**Automated:**
- axe-core (Deque)
- WAVE
- Lighthouse accessibility audit
- Pa11y

**Manual Testing:**
- Screen readers: NVDA, VoiceOver, JAWS
- Keyboard-only navigation
- Browser zoom 200%
- Color blindness simulators
- Reduced motion testing

### Compliance Documentation

**VPAT (Voluntary Product Accessibility Template):**
- Required for government procurement (Section 508)
- Documents conformance level per WCAG criterion
- Identifies known issues and roadmap

**Accessibility Statement:**
- Current conformance status
- Known limitations
- Contact for accessibility issues
- Commitment to improvement

---

## Key Takeaways for Code Analysis

1. **Check touch target sizes** - Below 44px = accessibility issue
2. **Verify contrast ratios** - Use APCA for accuracy
3. **Look for prefers-reduced-motion** - Absence = vestibular risk
4. **Check keyboard accessibility** - All interactions must work
5. **Verify ARIA usage** - Prefer semantic HTML
6. **Detect dark patterns** - Pre-checked boxes, fake urgency, obstruction
7. **Check consent flows** - Equal prominence, easy withdrawal
8. **Verify focus management** - Traps in modals, restoration on close
9. **Look for skip links** - Essential for keyboard users
10. **Check for spacing controls** - Dyslexia support via CSS
