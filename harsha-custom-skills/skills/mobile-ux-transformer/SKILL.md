---
name: mobile-ux-transformer
description: Tech-stack-agnostic 12-phase methodology for transforming desktop-first interfaces into mobile-optimized experiences. Covers thumb-zone ergonomics, touch-target sizing (44pt iOS / 48dp Android), gesture vocabulary, iOS vs Android platform conventions, mobile forms and navigation patterns, haptic feedback, WCAG 2.2 mobile compliance, Core Web Vitals mobile budgets, dark-mode, and responsive typography. Use when the user asks to convert a desktop design to mobile, audit an existing mobile interface, implement iOS/Android platform conventions, or optimize mobile conversion/ergonomics regardless of framework (React, Vue, Flutter, React Native, Swift, Kotlin, vanilla). Skip when building a native mobile app from scratch in a specific stack (use mobile-app-mastery or flutter-master) or when the request is desktop-only web design (use web-design-mastery).
---

# Mobile Experience Transformer Skill v3.0

> **Tech-Stack Agnostic Framework for World-Class Mobile UX Transformation**
> 
> Version 3.0 | January 2026 | 150+ Authoritative Sources Integrated

## Quick Stats That Matter

| Metric | Value | Source |
|--------|-------|--------|
| Mobile traffic share | 58-64% | Global web analytics 2024-2025 |
| Mobile commerce value | $2+ trillion/year | Industry reports |
| Mobile conversion rate | 1.8-2.96% vs 3.09-3.9% desktop | Baymard Institute |
| Mobile cart abandonment | 75.5-79.6% | E-commerce studies |
| Recoverable lost orders | $260 billion | Baymard checkout UX research |
| App vs web conversion | Apps convert 157% higher | Mobile commerce data |
| One-handed phone use | 49% of users | Ergonomics research |
| Thumb-driven interactions | 75% of all touches | Touch behavior studies |

---

## Skill Overview

This skill transforms any web interface into an optimized mobile experience using research-backed methodologies, platform-specific best practices, and measurable performance standards. It is **tech-stack agnostic** — applicable to React, Vue, Angular, Flutter, React Native, Swift, Kotlin, or vanilla HTML/CSS/JS.

### When to Use This Skill

- Converting desktop-first designs to mobile-first
- Optimizing existing mobile interfaces
- Creating new mobile experiences from scratch
- Auditing mobile UX for compliance and performance
- Implementing platform-specific conventions (iOS/Android)

### Reference Architecture

```
mobile-ux-transformer-v3/
├── SKILL.md                          # This file - main methodology
├── references/                       # Deep-dive reference documents
│   ├── 01-research-statistics.md     # Business case & ROI data
│   ├── 02-thumb-zone-ergonomics.md   # Touch ergonomics & screen zones
│   ├── 03-component-patterns.md      # Desktop→Mobile transformations
│   ├── 04-gesture-vocabulary.md      # Touch interaction patterns
│   ├── 05-platform-conventions.md    # iOS vs Android differences
│   ├── 06-form-design.md             # Form optimization patterns
│   ├── 07-navigation-patterns.md     # Mobile navigation systems
│   ├── 08-performance-budgets.md     # Core Web Vitals 2025 targets
│   ├── 09-accessibility-mobile.md    # WCAG 2.2 mobile compliance
│   ├── 10-haptic-feedback.md         # Tactile feedback patterns
│   ├── 11-typography-mobile.md       # Mobile typography system
│   ├── 12-dark-mode-design.md        # Dark/light mode implementation
│   └── 13-design-tokens.md           # Cross-platform design systems
├── code-snippets/                    # Ready-to-use implementations
│   ├── touch-targets.css
│   ├── responsive-typography.css
│   ├── bottom-navigation.html
│   ├── gesture-handlers.js
│   ├── platform-detection.js
│   ├── performance-monitoring.js
│   ├── haptic-feedback.js
│   └── accessibility-helpers.js
├── checklists/                       # Audit & testing checklists
│   ├── mobile-ux-audit.md
│   ├── accessibility-checklist.md
│   ├── performance-checklist.md
│   └── platform-compliance.md
└── case-studies/                     # Real-world transformation examples
    ├── ecommerce-transformation.md
    ├── saas-dashboard-mobile.md
    └── content-site-optimization.md
```

---

## 12-Phase Transformation Methodology

### Phase 1: Mobile Context Analysis

**Objective:** Understand how users will interact with the interface on mobile devices.

**Key Questions:**
1. What tasks will users perform on mobile vs desktop?
2. What's the primary usage context? (commuting, at home, in-store)
3. What device capabilities are relevant? (camera, GPS, biometrics)
4. What's the expected network quality?

**Mobile Necessity Score Framework:**

| Score | Classification | Action |
|-------|---------------|--------|
| 5 | Essential | Must be mobile-first, feature-complete |
| 4 | Important | Full functionality, optimized experience |
| 3 | Useful | Core features, simplified workflow |
| 2 | Nice-to-have | Read-only or limited functionality |
| 1 | Desktop-only | Link to desktop or remove |

**Context Signals to Consider:**
- Time-of-day usage patterns
- Session duration expectations (mobile: 72 seconds average)
- Task completion requirements
- Environmental factors (lighting, movement, noise)

**Output:** Mobile context document with prioritized feature list

---

### Phase 2: Information Architecture Redesign

**Objective:** Restructure content hierarchy for mobile consumption patterns.

**Progressive Disclosure Principles:**
1. Show only essential information initially
2. Reveal details on demand
3. Use expandable sections for secondary content
4. Implement "read more" patterns for text blocks

**Content Priority Matrix:**

| Priority | Visibility | Examples |
|----------|-----------|----------|
| P0 - Critical | Always visible | Primary CTA, key status, navigation |
| P1 - Important | Above fold | Core content, secondary actions |
| P2 - Relevant | Below fold / collapsed | Supporting details, options |
| P3 - Optional | Hidden / menu | Settings, advanced features |

**Mobile IA Principles:**
- **Depth over breadth:** Fewer top-level items, deeper hierarchies
- **Task-oriented grouping:** Organize by user goals, not content type
- **Chunked content:** Break long content into scannable sections
- **F-pattern scanning:** Place key content top-left to mid-right

**Output:** Revised sitemap and content hierarchy document

---

### Phase 3: Thumb Zone Ergonomics

**Objective:** Position interactive elements within comfortable thumb reach.

**📖 Reference:** `references/02-thumb-zone-ergonomics.md`

**Three-Zone Model (Right-handed, portrait):**

```
┌─────────────────────────────┐
│      STRETCH ZONE (18%)     │  ← Destructive/rare actions
│         Hard to reach       │
├─────────────────────────────┤
│       REACH ZONE (33%)      │  ← Secondary actions
│        Moderate effort      │
├─────────────────────────────┤
│      NATURAL ZONE (49%)     │  ← Primary actions
│        Easy thumb arc       │  ← Navigation
│         Bottom area         │  ← Frequent interactions
└─────────────────────────────┘
```

**Touch Target Requirements (2024-2025 Standards):**

| Standard | Minimum Size | Recommended | Spacing |
|----------|-------------|-------------|---------|
| Apple HIG | 44×44 pt | 48×48 pt | 8pt minimum |
| Material Design 3 | 48×48 dp | 56×56 dp | 8dp minimum |
| WCAG 2.2 AA | 24×24 CSS px | 44×44 CSS px | Target + spacing ≥44px |
| WCAG 2.2 AAA | 44×44 CSS px | 48×48 CSS px | 8px minimum |

**Critical Rules:**
- **Primary CTAs:** Always in natural thumb zone (bottom 40% of screen)
- **Navigation:** Bottom navigation bar for 3-5 primary destinations
- **Destructive actions:** Position in stretch zone (top corners) as safeguard
- **Spacing:** Minimum 8-10px between touch targets to prevent mis-taps

**Touch Target Sizing by Screen Position:**

| Position | Minimum Target | Reason |
|----------|---------------|--------|
| Bottom center | 44×44 pt | Natural zone, easy reach |
| Bottom corners | 48×48 pt | Edge of reach, needs extra size |
| Middle screen | 44×44 pt | Moderate reach |
| Top corners | 48×48 pt | Stretch zone, make larger |

**Output:** Annotated wireframes with thumb zone overlay

---

### Phase 4: Component Transformation

**Objective:** Convert desktop UI patterns to mobile-optimized equivalents.

**📖 Reference:** `references/03-component-patterns.md`

**Universal Transformation Rules:**

| Desktop Pattern | Mobile Pattern | Rationale |
|----------------|----------------|-----------|
| Data tables | Cards / List views | Horizontal scrolling is awkward |
| Modal dialogs | Bottom sheets / Full-screen | Better thumb reach |
| Hover tooltips | Long-press / Info icons | No hover on touch |
| Multi-column layouts | Single column | Screen width constraint |
| Horizontal navigation | Bottom tab bar / Hamburger | Thumb accessibility |
| Pagination | Infinite scroll / Load more | Continuous browsing |
| Dropdown select | Native picker / Full-screen selector | Better touch targets |
| Side panels | Full-screen overlays | Space constraint |
| Right-click menus | Long-press menus | Touch equivalent |
| Keyboard shortcuts | Gesture shortcuts | Touch equivalent |

**Component Decision Framework:**

```
IF component requires:
  - Hover state → Convert to tap/long-press
  - Fine pointer precision → Enlarge touch target
  - Horizontal space → Stack vertically or paginate
  - Keyboard input → Consider voice/camera alternatives
  - Multiple simultaneous views → Use progressive disclosure
```

**Output:** Component mapping document

---

### Phase 5: Touch Interaction Design

**Objective:** Design intuitive gesture-based interactions.

**📖 Reference:** `references/04-gesture-vocabulary.md`

**Universal Touch Gestures:**

| Gesture | Primary Use | Feedback Required |
|---------|-------------|-------------------|
| Tap | Select, activate | Visual + optional haptic |
| Double-tap | Zoom, like/favorite | Visual + haptic |
| Long-press | Context menu, drag mode | Haptic (required) |
| Swipe horizontal | Navigate, dismiss, reveal actions | Visual + haptic |
| Swipe vertical | Scroll, pull-to-refresh | Visual feedback |
| Pinch | Zoom in/out | Visual scaling |
| Drag | Reorder, move | Visual + continuous haptic |
| Two-finger swipe | Secondary scroll, system gesture | System-defined |

**Gesture Design Rules:**

1. **Discoverability:** Provide visual hints for non-obvious gestures
2. **Confirmation:** Always confirm destructive gesture actions
3. **Reversibility:** Allow undo for swipe-to-delete patterns
4. **Consistency:** Match platform conventions (iOS vs Android differ)
5. **Fallback:** Provide button alternatives for all gesture actions

**Platform-Specific Gesture Considerations:**

| Gesture | iOS Behavior | Android Behavior |
|---------|-------------|------------------|
| Edge swipe left | Back navigation (system) | App-defined |
| Edge swipe right | Forward (if available) | Open drawer (common) |
| Swipe down from top | Notification Center | Notification shade |
| Swipe up from bottom | Home / App Switcher | Home / Recent apps |

**Output:** Gesture mapping document with accessibility alternatives

---

### Phase 6: User Journey Optimization

**Objective:** Minimize steps and friction in mobile task flows.

**Journey Optimization Principles:**

1. **Reduce steps:** Mobile users expect 30-50% fewer steps than desktop
2. **Eliminate redundancy:** Never ask for information twice
3. **Smart defaults:** Pre-fill based on context, history, location
4. **Progress indication:** Always show where user is in multi-step flows
5. **Exit points:** Allow saving/resuming at any point

**Mobile Journey Metrics:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Steps to complete | ≤3 for common tasks | Count screens/interactions |
| Time to complete | ≤60 seconds for common tasks | User testing |
| Error rate | ≤5% | Analytics |
| Abandonment rate | ≤20% for critical flows | Funnel analysis |

**Step Reduction Techniques:**

- **Combine screens:** Merge related inputs on single view
- **Progressive loading:** Show content while loading more
- **Inline editing:** Edit in place, don't navigate to edit screen
- **Batch actions:** Allow multi-select for repetitive tasks
- **Contextual actions:** Show relevant actions based on selection

**Checkout Optimization (Critical for E-commerce):**

| Optimization | Impact |
|-------------|--------|
| Guest checkout | -23% abandonment |
| Progress indicator | -18% abandonment |
| Remove one field | Expedia saved $12M/year from one field |
| Autofill support | -28% form time |
| Mobile payment (Apple/Google Pay) | +40% conversion for impulse purchases |

**Output:** Optimized user flow diagrams

---

### Phase 7: Device Capability Integration

**Objective:** Leverage mobile-specific hardware capabilities.

**High-Impact Capabilities:**

| Capability | Use Cases | Permission Required |
|------------|-----------|-------------------|
| Camera | Photo upload, barcode scan, AR, document capture | Yes |
| GPS/Location | Local search, delivery, check-in, maps | Yes |
| Biometrics | Authentication, payment authorization | Yes |
| Haptic engine | Feedback, notifications, confirmations | No |
| Accelerometer | Shake gestures, orientation, fitness | No |
| Microphone | Voice input, audio messages, voice search | Yes |
| NFC | Contactless payments, device pairing | Yes (varies) |
| Push notifications | Re-engagement, updates, alerts | Yes |

**Capability Integration Patterns:**

1. **Progressive enhancement:** Feature works without capability, enhanced with it
2. **Permission timing:** Request only when needed, with clear context
3. **Fallback paths:** Always provide non-capability alternative
4. **Error handling:** Graceful degradation if capability unavailable

**Biometric Authentication Best Practices:**

```javascript
// iOS Face ID / Touch ID
// - Provide passcode fallback
// - Explain why biometrics help
// - Don't require biometrics for non-sensitive features

// Android BiometricPrompt
// - Support multiple biometric types
// - Handle device compatibility (API 23+)
// - Provide PIN/pattern fallback
```

**Output:** Capability integration plan

---

### Phase 8: Form Design Optimization

**Objective:** Create friction-free form experiences.

**📖 Reference:** `references/06-form-design.md`

**Mobile Form Statistics:**
- **81%** form abandonment rate (mobile)
- **15.4 seconds** faster completion with single-column layouts
- **$12 million/year** saved by Expedia removing one form field
- **26%** abandon due to account creation requirements

**Form Design Rules:**

| Rule | Implementation |
|------|----------------|
| Single column only | Never use multi-column forms on mobile |
| Top-aligned labels | Or floating labels (Material Design style) |
| Input type matching | Use correct HTML5 input types |
| Autocomplete attributes | Enable browser/password manager autofill |
| Inline validation | Validate as user types, not on submit |
| Error prevention | Disable submit until valid, use input masks |
| Keyboard optimization | Show appropriate keyboard for each field |

**HTML5 Input Types for Mobile:**

```html
<!-- Phone number - brings up phone pad -->
<input type="tel" autocomplete="tel">

<!-- Email - shows @ and .com keys -->
<input type="email" autocomplete="email">

<!-- Credit card - numeric with spaces -->
<input type="text" inputmode="numeric" autocomplete="cc-number">

<!-- One-time codes - numeric, enables SMS autofill -->
<input type="text" inputmode="numeric" autocomplete="one-time-code">

<!-- URL - shows / and .com keys -->
<input type="url" autocomplete="url">

<!-- Search - shows search key instead of return -->
<input type="search">
```

**Autocomplete Attributes (Critical for Conversion):**

| Field | Autocomplete Value |
|-------|-------------------|
| Full name | `name` |
| Email | `email` |
| Phone | `tel` |
| Street address | `street-address` |
| City | `address-level2` |
| State/Province | `address-level1` |
| ZIP/Postal code | `postal-code` |
| Country | `country-name` |
| Credit card number | `cc-number` |
| Card expiry | `cc-exp` |
| Card CVV | `cc-csc` |
| Username | `username` |
| Current password | `current-password` |
| New password | `new-password` |
| OTP code | `one-time-code` |

**Minimum Input Sizing (Critical for iOS):**
```css
/* Prevent iOS zoom on focus - minimum 16px font size */
input, select, textarea {
  font-size: 16px; /* 16px minimum prevents zoom */
  font-size: max(16px, 1rem); /* Fluid alternative */
}
```

**Output:** Optimized form specifications

---

### Phase 9: Navigation Pattern Implementation

**Objective:** Implement intuitive, thumb-accessible navigation.

**📖 Reference:** `references/07-navigation-patterns.md`

**Navigation Pattern Selection:**

| Pattern | Best For | Item Count |
|---------|----------|------------|
| Bottom tab bar | Primary navigation | 3-5 items |
| Hamburger menu | Secondary navigation | 5+ items |
| Top tabs | Content categories | 2-7 items |
| Floating action button | Primary action | 1 action |
| Search | Content discovery | N/A |

**Bottom Tab Bar Rules:**

1. **3-5 items maximum** (5 is the absolute max)
2. **Icon + label** always (icons alone are ambiguous)
3. **Selected state** clearly distinguished
4. **Fixed position** at bottom of viewport
5. **Safe area respect** on notched devices

**Bottom Tab Bar Implementation:**

```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px; /* Standard height */
  padding-bottom: env(safe-area-inset-bottom); /* Notch safety */
  display: flex;
  justify-content: space-around;
  background: var(--surface);
  border-top: 1px solid var(--border);
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  min-height: 48px; /* Touch target */
  gap: 4px;
}
```

**Back Navigation Patterns:**

| Platform | Primary Method | Secondary |
|----------|---------------|-----------|
| iOS | Edge swipe (right) | Back button (top-left) |
| Android | System back button | Toolbar up button |
| Web | Browser back | In-app back button |

**Output:** Navigation architecture document

---

### Phase 10: Platform-Specific Adaptation

**Objective:** Respect iOS and Android conventions.

**📖 Reference:** `references/05-platform-conventions.md`

**Critical Platform Differences:**

| Element | iOS | Android |
|---------|-----|---------|
| Primary font | SF Pro | Roboto |
| Navigation | Bottom tabs preferred | Bottom tabs or drawer |
| Back navigation | Edge swipe + top-left button | System back button |
| Action placement | Top-right | FAB or top-right |
| Switches | Rounded, no labels | Material switches |
| Alerts | Centered, rounded | Material dialogs |
| Haptics | Taptic Engine (refined) | Variable (device-dependent) |

**iOS-Specific Requirements:**

- **Dynamic Type:** Support system font size settings
- **Safe areas:** Respect notch, home indicator, status bar
- **SF Symbols:** Use Apple's icon system for consistency
- **Liquid Glass (iOS 26+):** Translucent surfaces, dynamic lighting

**Android-Specific Requirements:**

- **Material Design 3:** Follow Material component guidelines
- **Predictive back:** Support new back gesture animation
- **Edge-to-edge:** Full-screen content with system bar handling
- **Foldables:** Support different screen states and orientations

**Platform Detection for Styling:**

```javascript
// Detect platform
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
const isAndroid = /Android/.test(navigator.userAgent);

// Apply platform-specific class
document.documentElement.classList.add(isIOS ? 'ios' : 'android');
```

```css
/* Platform-specific styling */
.ios .button { border-radius: 12px; }
.android .button { border-radius: 20px; }

.ios .nav-title { font-weight: 600; text-align: center; }
.android .nav-title { font-weight: 500; text-align: left; }
```

**Output:** Platform adaptation specifications

---

### Phase 11: Performance Optimization

**Objective:** Meet Core Web Vitals and mobile performance standards.

**📖 Reference:** `references/08-performance-budgets.md`

**Core Web Vitals 2025 Thresholds:**

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5-4.0s | >4.0s |
| **INP** (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 |

> **Note:** INP replaced FID as of March 2024. Only 65% of mobile sites pass INP vs 93% that passed FID.

**Performance Budget:**

| Resource | Budget |
|----------|--------|
| Total page weight | ≤500 KB compressed |
| JavaScript | ≤170 KB |
| CSS | ≤50 KB |
| Images (initial viewport) | ≤200 KB |
| Web fonts | ≤100 KB |
| Time to Interactive | ≤3.5s on 4G |

**Business Impact of Performance:**

| Improvement | Result |
|------------|--------|
| Vodafone: 31% LCP improvement | +8% sales |
| Swappie: 55% LCP, 91% CLS improvement | +42% revenue |
| Pinterest: PWA implementation | +40% faster perceived load |
| Every 1s delay | -7-20% conversions |

**Critical Performance Optimizations:**

1. **Images:**
   - Use AVIF > WebP > JPEG
   - Implement responsive images with srcset
   - Lazy load below-fold images
   - Never lazy load LCP image

2. **JavaScript:**
   - Code split by route
   - Defer non-critical JS
   - Use `scheduler.yield()` to break long tasks

3. **CSS:**
   - Inline critical CSS (<14KB)
   - Load non-critical CSS async
   - Avoid layout-triggering properties in animations

4. **Fonts:**
   - Use `font-display: swap`
   - Preload critical fonts
   - Subset fonts to used characters

**Output:** Performance optimization plan

---

### Phase 12: Accessibility Implementation

**Objective:** Ensure WCAG 2.2 compliance and inclusive design.

**📖 Reference:** `references/09-accessibility-mobile.md`

**Mobile Accessibility Requirements:**

| Requirement | Standard | Implementation |
|------------|----------|----------------|
| Touch target size | WCAG 2.5.8 | ≥24×24px (AA), ≥44×44px (AAA) |
| Target spacing | WCAG 2.5.8 | ≥24px between targets |
| Dragging alternatives | WCAG 2.5.7 | Provide button alternatives |
| Cognitive auth | WCAG 3.3.8 | No memory/puzzle tests |
| Color contrast | WCAG 1.4.3 | ≥4.5:1 text, ≥3:1 UI |
| Text resize | WCAG 1.4.4 | Support up to 200% zoom |

**Screen Reader Support:**

| Platform | Screen Reader | Usage Share |
|----------|--------------|-------------|
| iOS | VoiceOver | 72% of mobile AT users |
| Android | TalkBack | 29% of mobile AT users |

**Essential ARIA for Mobile:**

```html
<!-- Accessible button -->
<button aria-label="Close dialog" aria-describedby="close-hint">
  <svg>...</svg>
</button>
<span id="close-hint" class="sr-only">Closes the current dialog and returns to the main screen</span>

<!-- Live region for updates -->
<div aria-live="polite" aria-atomic="true">
  Cart updated: 3 items
</div>

<!-- Loading state -->
<button aria-busy="true" aria-disabled="true">
  <span class="spinner" aria-hidden="true"></span>
  Loading...
</button>
```

**Legal Compliance (2024-2025):**

| Regulation | Effective | Requirement |
|------------|-----------|-------------|
| European Accessibility Act | June 28, 2025 | EN 301 549 (WCAG 2.1 AA) |
| ADA Title II (US) | April 2026-2027 | WCAG 2.1 AA for gov services |
| Existing ADA | Now | Risk of lawsuits (4,061 in 2022) |

**Accessibility Testing Checklist:**

- [ ] VoiceOver/TalkBack navigation works logically
- [ ] All interactive elements have accessible names
- [ ] Focus order matches visual order
- [ ] Touch targets meet minimum sizes
- [ ] Color is not sole indicator of information
- [ ] Motion can be disabled (prefers-reduced-motion)
- [ ] Text can be resized to 200% without loss
- [ ] Forms have proper labels and error messages

**Output:** Accessibility audit report and remediation plan

---

## Quick Reference: Transformation Checklist

### Pre-Flight

- [ ] Mobile context analysis complete
- [ ] Content priority defined
- [ ] Target devices/breakpoints identified
- [ ] Performance budget established
- [ ] Platform conventions documented

### Design Phase

- [ ] Single-column layouts (mobile)
- [ ] Touch targets ≥44×44pt
- [ ] Navigation in thumb zone
- [ ] Forms optimized (single column, correct input types)
- [ ] Gestures documented with alternatives
- [ ] Typography ≥16px body text

### Development Phase

- [ ] Responsive images implemented
- [ ] Critical CSS inlined
- [ ] JavaScript code-split
- [ ] Haptic feedback integrated
- [ ] Platform detection working
- [ ] Offline/PWA capability (if applicable)

### Testing Phase

- [ ] Core Web Vitals passing
- [ ] Real device testing (iOS + Android)
- [ ] Screen reader testing
- [ ] Thumb zone usability verified
- [ ] Form completion tested
- [ ] Slow network testing (3G)

### Launch Phase

- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Analytics capturing mobile events
- [ ] App store compliance (if native)
- [ ] Accessibility statement published

---

## Reference File Index

| # | File | Description |
|---|------|-------------|
| 01 | `research-statistics.md` | Business case, ROI data, industry benchmarks |
| 02 | `thumb-zone-ergonomics.md` | Touch ergonomics, screen zones, handedness |
| 03 | `component-patterns.md` | Desktop→Mobile pattern transformations |
| 04 | `gesture-vocabulary.md` | Touch gestures, platform differences, feedback |
| 05 | `platform-conventions.md` | iOS vs Android design conventions |
| 06 | `form-design.md` | Mobile form optimization, input types |
| 07 | `navigation-patterns.md` | Navigation systems, patterns, implementation |
| 08 | `performance-budgets.md` | Core Web Vitals, optimization techniques |
| 09 | `accessibility-mobile.md` | WCAG 2.2, screen readers, legal compliance |
| 10 | `haptic-feedback.md` | Haptic patterns, platform APIs |
| 11 | `typography-mobile.md` | Type scale, readability, Dynamic Type |
| 12 | `dark-mode-design.md` | Dark mode implementation, color systems |
| 13 | `design-tokens.md` | Cross-platform design systems, tokens |

---

## Sources & Standards Referenced

### Platform Guidelines
- Apple Human Interface Guidelines (iOS 18+, iOS 26 Liquid Glass)
- Google Material Design 3 (including Expressive update)
- WCAG 2.2 (W3C)
- EN 301 549 (European Accessibility Standard)

### Research Sources
- Nielsen Norman Group mobile studies
- Baymard Institute checkout/form research
- Google Web Vitals documentation
- MDN Web Docs
- Platform-specific accessibility documentation

### Industry Data
- Global mobile commerce statistics
- Core Web Vitals origin data (Chrome UX Report)
- Mobile conversion benchmarks
- Accessibility lawsuit data

---

*Mobile Experience Transformer Skill v3.0 — Comprehensive mobile UX transformation framework with 150+ integrated sources*
