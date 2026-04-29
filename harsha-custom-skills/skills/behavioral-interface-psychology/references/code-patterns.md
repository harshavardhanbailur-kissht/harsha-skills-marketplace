# Code Patterns Reference - Behavioral Psychology Detection

## Quick Signal Reference

This file contains code patterns that signal behavioral psychology considerations—both positive implementations that honor human psychology and problematic patterns that may manipulate or harm users.

---

## Perceptual Psychology Signals

### Audio Implementation

**Volume Control - Logarithmic vs Linear:**
```javascript
// ❌ POOR: Linear mapping (psychoacoustically wrong)
volumeSlider.oninput = (e) => {
  audio.volume = e.target.value / 100;
};

// ✅ GOOD: Logarithmic/power curve (matches perception)
volumeSlider.oninput = (e) => {
  const linear = e.target.value / 100;
  audio.volume = Math.pow(linear, 4); // x⁴ for ~60dB range
};

// Also check gain nodes
gainNode.gain.value = linearValue; // ❌ Linear
gainNode.gain.exponentialRampToValueAtTime(...); // ✅ Exponential
```

### Brightness/Opacity

**Gamma Correction Awareness:**
```javascript
// ❌ POOR: Assumes linear relationship
const midGray = 128 / 255; // Actually produces ~22% brightness

// ✅ GOOD: Accounts for gamma
const perceptualMid = Math.pow(0.5, 1/2.2) * 255; // ~186
// Or use CSS color-mix with oklch for perceptual uniformity
```

### Animation Timing

**Duration and Easing:**
```css
/* Check animation durations are within perceptual thresholds */
.transition {
  transition: all 200ms ease-out; /* ✅ Within 100-500ms range */
}

.too-fast {
  transition: all 50ms; /* ❌ May be imperceptible */
}

.too-slow {
  transition: all 2s; /* ❌ Feels sluggish for micro-interactions */
}

/* Check for reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Randomness Implementation

**Perceived Randomness:**
```javascript
// ❌ POOR: True random (feels biased to users)
const shuffle = (arr) => arr.sort(() => Math.random() - 0.5);

// ✅ GOOD: Quasi-random with constraints
const shuffleWithSpacing = (arr, options) => {
  // Ensure same artist/category not repeated within N items
  // Add ±10-15% jitter to prevent pure repetition
  // Spotify/Apple Music approach
};
```

---

## Cognitive Architecture Signals

### Working Memory Respect

**Menu/Option Count:**
```jsx
// ❌ RED FLAG: Too many options without grouping
<nav>
  {items.map(item => <NavItem />)} {/* If items.length > 7-8 */}
</nav>

// ✅ GOOD: Chunked into groups
<nav>
  {groups.map(group => (
    <NavGroup label={group.label}>
      {group.items.map(item => <NavItem />)} {/* 3-4 per group */}
    </NavGroup>
  ))}
</nav>
```

**Form Complexity:**
```jsx
// Check form field count
const fields = formSchema.fields.length;
// OPTIMAL: 12-14 fields
// AVERAGE (problematic): 23.48 fields
// Each unnecessary field: 8-50% conversion decrease
```

### Attention Management

**Auto-save Implementation:**
```javascript
// ✅ GOOD: Auto-save with state indication
const saveState = {
  status: 'saved', // 'saving', 'error', 'unsaved'
  lastSaved: timestamp
};

// Visual indicator in UI
<SaveIndicator status={saveState.status} />

// ❌ POOR: Silent save without indication
// Users don't know if work is preserved
```

**Interruption Handling:**
```javascript
// ✅ GOOD: Preserve context on interruption
window.addEventListener('beforeunload', (e) => {
  if (hasUnsavedChanges) {
    saveToLocalStorage(formState);
    // Restore on return
  }
});

// Session state restoration
const restoreSession = () => {
  const saved = localStorage.getItem('session');
  if (saved && confirmRestore()) {
    restoreState(JSON.parse(saved));
  }
};
```

### Cognitive Load Reduction

**Progressive Disclosure:**
```jsx
// ✅ GOOD: Hide complexity until needed
<form>
  <BasicFields />
  <Disclosure label="Advanced options">
    <AdvancedFields />
  </Disclosure>
</form>

// ❌ POOR: All options visible immediately
<form>
  <BasicFields />
  <AdvancedFields /> {/* Always visible */}
</form>
```

---

## Input Modality Signals

### Touch Target Sizing

```css
/* Check minimum sizes */
.button {
  min-width: 44px;  /* iOS minimum */
  min-height: 44px;
  /* Or 48px for Material Design / better accessibility */
}

/* ❌ RED FLAG: Targets below threshold */
.small-button {
  width: 24px;  /* WCAG AA minimum - 15% error rate */
  height: 24px;
}

/* ✅ Spacing between targets */
.button-group button {
  margin: 8px; /* Prevents mis-taps */
}
```

### Keyboard Accessibility

```jsx
// ✅ GOOD: Keyboard handlers on custom components
<div 
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>

// ❌ POOR: Click only, no keyboard support
<div onClick={handleClick}>
```

**Skip Links:**
```html
<!-- ✅ Should be first focusable element -->
<body>
  <a href="#main" class="skip-link">Skip to main content</a>
  <header>...</header>
  <main id="main">...</main>
</body>
```

### Voice Input Considerations

```javascript
// Check for voice input handling
const speechRecognition = new webkitSpeechRecognition();

// ✅ GOOD: Handles errors gracefully
speechRecognition.onerror = (event) => {
  if (event.error === 'no-speech') {
    showFeedback('No speech detected. Try again.');
  }
  // Fallback to text input
  showTextInput();
};

// ✅ GOOD: Shows interim results for feedback
speechRecognition.interimResults = true;
speechRecognition.onresult = (event) => {
  const interim = event.results[0][0].transcript;
  showInterimFeedback(interim); // Visual feedback
};
```

### Haptic Feedback

```javascript
// Check for haptic implementation
if ('vibrate' in navigator) {
  // ✅ GOOD: Short, appropriate feedback
  navigator.vibrate(25); // 25-30ms minimum pulse
  
  // ❌ POOR: Long, annoying vibration
  navigator.vibrate(500);
  
  // ✅ GOOD: Pattern for distinct feedback
  navigator.vibrate([25, 50, 25]); // Pattern
}
```

---

## Form & Input Signals

### Validation Patterns

```jsx
// ✅ GOOD: Inline validation (22% higher success)
<input 
  onChange={(e) => {
    const error = validate(e.target.value);
    setFieldError(error); // Show immediately
  }}
/>
{error && <ErrorMessage>{error}</ErrorMessage>}

// ❌ POOR: Validation only on submit
<form onSubmit={(e) => {
  const errors = validateAll(formData);
  // User has to find and fix errors
}}>
```

### Password Implementation

```jsx
// ✅ GOOD: Show/hide toggle (standard expectation)
<input 
  type={showPassword ? 'text' : 'password'}
/>
<button onClick={() => setShowPassword(!showPassword)}>
  {showPassword ? 'Hide' : 'Show'}
</button>

// ✅ GOOD: NIST-compliant strength meter
<PasswordStrengthMeter
  minLength={15}  // NIST: 15+ characters
  checkCommonPasswords={true}
  noCompositionRules={true}  // No "must have symbol" etc.
/>

// ❌ POOR: Outdated composition rules
if (!/[A-Z]/.test(password)) error('Must have uppercase');
if (!/[0-9]/.test(password)) error('Must have number');
```

### Phone Number Fields

```jsx
// ⚠️ CAUTION: Phone fields reduce conversion 48-52%
// Only include if truly necessary

// ✅ GOOD: Optional and explained
<label>
  Phone (optional) - for delivery updates only
  <input type="tel" />
</label>

// ❌ POOR: Required without explanation
<input type="tel" required />
```

---

## E-Commerce Signals

### Checkout Flow

```javascript
// Check checkout step count
const checkoutSteps = ['cart', 'shipping', 'payment', 'confirm'];
// OPTIMAL: 3-4 steps with clear progress

// ✅ GOOD: Progress indication
<ProgressBar 
  steps={checkoutSteps} 
  current={currentStep}
  showLabels={true}
/>

// ❌ POOR: No progress indication or many steps
```

### Price Display

```jsx
// ❌ DARK PATTERN: Drip pricing
<ProductCard>
  <Price>$99</Price>
  {/* Fees revealed at checkout */}
</ProductCard>

// ✅ GOOD: Total price upfront
<ProductCard>
  <Price>$129</Price>
  <PriceBreakdown>
    <span>Product: $99</span>
    <span>Shipping: $20</span>
    <span>Tax: $10</span>
  </PriceBreakdown>
</ProductCard>
```

### Urgency & Scarcity

```jsx
// ❌ DARK PATTERN: Fake urgency
const [timeLeft, setTimeLeft] = useState(3600);
useEffect(() => {
  const timer = setInterval(() => {
    setTimeLeft(prev => prev <= 0 ? 3600 : prev - 1); // Resets!
  }, 1000);
}, []);

// ❌ DARK PATTERN: Fake scarcity
<Badge>Only 2 left!</Badge> {/* Not connected to real inventory */}

// ✅ LEGITIMATE: Real inventory
<Badge>
  {inventory <= 5 && `Only ${inventory} left`}
</Badge>
```

### Promo Code Fields

```jsx
// ⚠️ PROBLEMATIC: Prominent promo field (27% abandonment to search)
<input placeholder="Enter promo code" className="prominent" />

// ✅ BETTER: Hidden behind disclosure
<Disclosure label="Have a promo code?">
  <input placeholder="Enter code" />
</Disclosure>

// ✅ BEST: Auto-apply available discounts
useEffect(() => {
  const discount = findApplicableDiscount(cart, user);
  if (discount) applyDiscount(discount);
}, [cart]);
```

---

## Notification & Permission Signals

### Permission Request Timing

```javascript
// ❌ POOR: Immediate on page load
window.onload = () => {
  Notification.requestPermission();
};

// ✅ GOOD: After value demonstration
subscribeButton.onclick = async () => {
  // User has shown intent
  const permission = await Notification.requestPermission();
};

// ✅ BETTER: Pre-permission explanation
const requestNotifications = async () => {
  const accepted = await showExplanationModal({
    title: 'Stay updated',
    description: 'Get notified when your order ships',
    benefits: ['Order updates', 'Delivery tracking']
  });
  
  if (accepted) {
    await Notification.requestPermission();
  }
};
```

### Notification Frequency

```javascript
// ✅ GOOD: Rate limiting
const COOLDOWN = 4 * 60 * 60 * 1000; // 4 hours
const canNotify = () => {
  const last = localStorage.getItem('lastNotification');
  return !last || Date.now() - last > COOLDOWN;
};

// ✅ GOOD: Batching
const notificationQueue = [];
const batchNotifications = debounce(() => {
  if (notificationQueue.length > 0) {
    sendBatchedNotification(notificationQueue);
    notificationQueue.length = 0;
  }
}, 30000);
```

---

## Loading & Performance Signals

### Progress Indication

```javascript
// ✅ GOOD: Non-linear progress (feels faster)
const displayProgress = (actual) => {
  // Front-load perceived progress
  return Math.sqrt(actual) * 100;
  // Or: easeOutQuad curve
};

// ❌ POOR: Linear progress
const displayProgress = (actual) => actual * 100;
```

### Skeleton Screens

```jsx
// ✅ GOOD: Matches actual content structure
<SkeletonLoader>
  <div className="skeleton-avatar" style={{ width: 48, height: 48 }} />
  <div className="skeleton-text" style={{ width: '60%' }} />
  <div className="skeleton-text" style={{ width: '40%' }} />
</SkeletonLoader>

// Note: Research shows skeletons increase perceived speed
// but may slow actual task completion (cognitive load of parsing)
```

### Optimistic UI

```javascript
// ✅ GOOD: Optimistic updates for high-success operations
const likeMutation = useMutation({
  mutationFn: likePost,
  onMutate: async (postId) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries(['posts']);
    // Optimistically update
    queryClient.setQueryData(['posts'], (old) =>
      old.map(p => p.id === postId ? {...p, liked: true} : p)
    );
  },
  onError: (err, postId, context) => {
    // Rollback on error
    queryClient.setQueryData(['posts'], context.previousPosts);
  }
});
```

---

## Dark Pattern Detection

### Consent & Defaults

```html
<!-- ❌ ILLEGAL (GDPR): Pre-checked consent -->
<input type="checkbox" checked name="marketing" />

<!-- ✅ COMPLIANT: Unchecked default -->
<input type="checkbox" name="marketing" />
```

```jsx
// ❌ DARK PATTERN: Asymmetric button styling
<button className="btn-primary">Accept All</button>
<button className="text-gray-400 text-sm">Manage</button>

// ✅ COMPLIANT: Equal visual weight
<button className="btn-secondary">Accept All</button>
<button className="btn-secondary">Manage Preferences</button>
```

### Subscription Cancellation

```javascript
// ❌ DARK PATTERN: Obstruction
const cancelFlow = [
  'confirm-intent',
  'select-reason',
  'speak-to-agent',     // Forced human interaction
  'counter-offer',       // Retention attempt
  'second-confirmation', // Extra friction
  'final-cancel'
];

// ✅ COMPLIANT: Direct cancellation
const cancel = async () => {
  const confirmed = await confirm('Cancel subscription?');
  if (confirmed) {
    await api.cancel();
    showConfirmation('Subscription cancelled');
  }
};
```

### Confirmshaming

```jsx
// ❌ DARK PATTERN: Guilt-tripping option labels
<Modal>
  <p>Sign up for our newsletter?</p>
  <button>Yes, I want great deals!</button>
  <button>No, I don't like saving money</button> {/* Confirmshaming */}
</Modal>

// ✅ GOOD: Neutral language
<Modal>
  <p>Sign up for our newsletter?</p>
  <button>Yes, subscribe</button>
  <button>No, thanks</button>
</Modal>
```

### Roach Motel (Hard to Exit)

```jsx
// ❌ DARK PATTERN: Easy signup, hard cancellation
// Signup: 2 clicks
// Cancellation: Call customer service during business hours

// ✅ GOOD: Symmetric effort
// Signup and cancellation both available in account settings
// Same number of steps
```

---

## Accessibility Implementation

### ARIA Usage

```jsx
// ✅ GOOD: Semantic HTML first
<button>Submit</button>
<nav><a href="/">Home</a></nav>

// ❌ POOR: ARIA when semantic would work
<div role="button" tabIndex={0}>Submit</div>

// ✅ GOOD: ARIA for custom widgets
<div 
  role="slider"
  aria-valuenow={50}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label="Volume"
  tabIndex={0}
/>
```

### Focus Management

```javascript
// ✅ GOOD: Focus trap in modal
const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef();
  
  useEffect(() => {
    if (isOpen) {
      const focusable = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      focusable[0]?.focus();
      
      // Trap focus within modal
      const handleTab = (e) => {
        if (e.key === 'Tab') {
          // Focus trapping logic
        }
      };
      document.addEventListener('keydown', handleTab);
      return () => document.removeEventListener('keydown', handleTab);
    }
  }, [isOpen]);
  
  // Return focus on close
  const prevFocus = useRef();
  useEffect(() => {
    if (isOpen) prevFocus.current = document.activeElement;
    else prevFocus.current?.focus();
  }, [isOpen]);
};
```

### Color Contrast

```javascript
// Check for contrast ratio calculations
const getContrastRatio = (color1, color2) => {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
};

// WCAG requirements:
// Normal text: 4.5:1 (AA), 7:1 (AAA)
// Large text: 3:1 (AA)
// UI components: 3:1
```

---

## Localization & Cultural

### RTL Support

```css
/* ✅ GOOD: CSS logical properties */
.sidebar {
  margin-inline-start: 1rem;  /* Works for LTR and RTL */
  padding-inline-end: 0.5rem;
}

/* ❌ POOR: Physical properties only */
.sidebar {
  margin-left: 1rem;  /* Doesn't adapt to RTL */
}
```

### Number/Currency Formatting

```javascript
// ✅ GOOD: Locale-aware formatting
const price = new Intl.NumberFormat(locale, {
  style: 'currency',
  currency: userCurrency
}).format(amount);

// ❌ POOR: Hardcoded formatting
const price = '$' + amount.toFixed(2);
```

### Financial Color Conventions

```javascript
// ✅ GOOD: Respects cultural conventions
const getGainLossColors = (locale) => {
  if (['ja', 'zh', 'ko'].some(l => locale.startsWith(l))) {
    return { gain: 'red', loss: 'green' }; // East Asian convention
  }
  return { gain: 'green', loss: 'red' }; // Western convention
};
```

---

## Performance Monitoring

### Core Web Vitals

```javascript
// ✅ GOOD: Monitoring in place
import { getLCP, getFID, getCLS, getINP } from 'web-vitals';

const sendToAnalytics = (metric) => {
  analytics.track('web-vitals', {
    name: metric.name,
    value: metric.value,
    delta: metric.delta
  });
};

getLCP(sendToAnalytics);
getFID(sendToAnalytics);
getCLS(sendToAnalytics);
getINP(sendToAnalytics);
```

### Resource Optimization

```html
<!-- ✅ GOOD: Critical resource hints -->
<link rel="preload" href="/fonts/main.woff2" as="font" crossorigin />
<link rel="preconnect" href="https://api.example.com" />
<link rel="prefetch" href="/next-page.html" />

<!-- ✅ GOOD: Lazy loading -->
<img loading="lazy" src="below-fold.jpg" />
<iframe loading="lazy" src="video.html" />
```

---

## Summary Checklist

**Perceptual:**
- [ ] Audio uses logarithmic volume curves
- [ ] Animations respect prefers-reduced-motion
- [ ] Animation durations 100-500ms range

**Cognitive:**
- [ ] Menu items ≤7-8 or chunked
- [ ] Form fields ≤14 with progressive disclosure
- [ ] Auto-save with visible status

**Input:**
- [ ] Touch targets ≥44px
- [ ] Keyboard support on custom widgets
- [ ] Skip links present

**E-Commerce:**
- [ ] No fake urgency/scarcity
- [ ] Price totals shown upfront
- [ ] Promo field not prominent

**Notifications:**
- [ ] Permission requests contextual
- [ ] Rate limiting/batching present

**Performance:**
- [ ] Progress bars use non-linear curves
- [ ] Optimistic UI for high-success operations
- [ ] Core Web Vitals monitored

**Ethics:**
- [ ] No pre-checked consent
- [ ] Equal prominence for options
- [ ] Easy cancellation flows

**Accessibility:**
- [ ] Semantic HTML before ARIA
- [ ] Focus management in modals
- [ ] Contrast ratios meet WCAG

**Localization:**
- [ ] CSS logical properties for RTL
- [ ] Locale-aware number formatting
- [ ] Cultural color conventions
