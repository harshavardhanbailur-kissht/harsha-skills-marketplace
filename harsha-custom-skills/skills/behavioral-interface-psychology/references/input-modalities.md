# Input Modalities Reference

## Keyboard Input

### Typing Speed Benchmarks

**Desktop** (Dhakal et al. 2018, N=168,000+):
| Population | Speed | Notes |
|------------|-------|-------|
| Average | 52 WPM | Touch typists |
| 95th percentile | ~100 WPM | Expert typists |
| Maximum observed | 120+ WPM | Professional |

**Mobile** (Palin et al. 2019, N=37,000+):
| Method | Speed | Notes |
|--------|-------|-------|
| Two-thumb | 38 WPM | Most common |
| One-thumb | 30 WPM | One-handed use |
| External keyboard | 56 WPM | Near desktop |

### Age-Related Differences

| Age Group | WPM | vs. Baseline |
|-----------|-----|--------------|
| 10-19 | 39.6 | Baseline |
| 20-29 | 51.3 | +30% |
| 30-39 | 51.9 | +31% (peak) |
| 40-49 | 48.4 | +22% |
| 50-59 | 26.3 | -34% |

### Autocorrect & Prediction

**Autocorrect Impact**:
- **+8.6 WPM** advantage (significant)
- Reduces substitution errors
- Can introduce new errors (wrong correction)

**Word Prediction Impact**:
- **-2.0 WPM** penalty
- Cognitive overhead of scanning suggestions
- Breaks flow of continuous typing

**Design Implication**: Enable autocorrect by default; make word prediction optional.

### Error Types

| Type | Frequency | Cause |
|------|-----------|-------|
| Substitution | 55.6% | Adjacent key hits |
| Omission | 33.3% | Skipped letters |
| Insertion | 11.1% | Double taps |

### Keyboard Shortcuts

**Critical Finding**: 81-90% of users NEVER use keyboard shortcuts

**Even Ctrl+F (Find)**:
- Only 10-19% use regularly
- Most scroll or give up

**Design Implications**:
- Never require shortcuts
- Always provide clickable alternatives
- Command palette (Cmd+K) improves discoverability
- Show shortcuts in menu items as education

### Keyboard Navigation (Accessibility)

**Requirements**:
- All interactive elements focusable
- Logical tab order
- Visible focus indicators
- Skip links for navigation

**WCAG 2.1 SC 2.1.1**: All functionality keyboard-accessible

```css
/* Required: Visible focus */
:focus {
  outline: 2px solid #005FCC;
  outline-offset: 2px;
}

/* Never: Remove focus outline */
:focus { outline: none; } /* VIOLATION */
```

---

## Voice Input

### Speed Advantage

**Voice is 3× faster than typing**:
- Voice: 153-161 WPM (natural speech rate)
- Typing: 52-53 WPM (average)
- Mobile typing: 30-38 WPM

### Accuracy Disparities (Critical)

**Word Error Rate by Demographic**:
| Group | WER | Relative |
|-------|-----|----------|
| White speakers | 19% | Baseline |
| Black speakers | 35% | +84% |

**Source**: Stanford/Georgetown study on commercial ASR systems

**Design Requirement**: 
- Always provide alternative input methods
- Test with diverse voice samples
- Monitor error rates across demographics

### Latency Thresholds

| Latency | User Perception |
|---------|-----------------|
| <300ms | Instantaneous |
| 300-500ms | Noticeable but acceptable |
| >500ms | Frustrating |
| >1000ms | Conversational flow broken |

### Privacy & Social Constraints

**Public Space Avoidance**: 78% avoid voice assistants in public

**Reasons**:
- Privacy concerns
- Social embarrassment
- Noise interference
- Cultural norms

**Design Implication**: Never make voice the only input option.

### User Frustration

**95%** of voice assistant users report frustration at some point

**Common Issues**:
- Recognition errors
- Wrong interpretation
- Limited understanding
- Repetitive failures

### Older Adult Voice Adoption

**Positive Findings** (JMIR mHealth 2021, age 74+):
- 90% found voice assistants easy to learn/use
- Use cases: 38.9% health questions, 28.2% music, 12.8% directions
- Perceived benefits evolve over time

---

## Pointer Input

### Fitts's Law

**Core Formula**: MT = a + b × log₂(2D/W)
- MT: Movement time
- D: Distance to target
- W: Target width
- ID: log₂(2D/W) = Index of Difficulty

### Throughput Comparison

| Input Device | Throughput (bits/s) | Relative |
|--------------|---------------------|----------|
| Direct touch | 6.85-7.52 | Fastest |
| Mouse | 3.7-4.9 | Baseline |
| Trackpad | 1.89-2.16 | 50% slower |
| Eye tracking | 2.0-3.5 | Variable |

### Touch Target Size Requirements

| Standard | Minimum | Recommended |
|----------|---------|-------------|
| Apple iOS | 44×44pt | 44×44pt |
| Material Design | 48×48dp | 48×48dp |
| WCAG 2.2 AA | 24×24px | - |
| WCAG 2.2 AAA | 44×44px | - |

### Error Rates by Target Size

| Size | Error Rate | Notes |
|------|------------|-------|
| 44px | 3% | Acceptable |
| 24px | 15% | 5× worse |
| <24px | >20% | Unusable |

### Spacing Requirements

**Minimum Gap**: 8px between touch targets

**Edge Targets**: 
- Screen edges are "infinite" width (Fitts's Law)
- Place important actions at edges
- But: Mobile edge-to-edge screens lose this advantage

### Mouse-Specific Patterns

**Steering Law** (tunnel navigation):
- Time proportional to length/width ratio
- Long narrow menus are difficult
- Dropdown submenus: Add delay before close

**Hover States**:
- Mouse: Hover reveals tooltips/submenus
- Touch: No hover equivalent
- Must design for both modalities

---

## Haptic Feedback

### Physiological Basis

**Mechanoreceptors**:
| Type | Frequency | Function |
|------|-----------|----------|
| Pacinian | 250 Hz (optimal) | Vibration detection |
| Meissner | 10-50 Hz | Light touch |
| Merkel | 0.4-3 Hz | Sustained pressure |
| Ruffini | 15-400 Hz | Skin stretch |

### Timing Thresholds

| Parameter | Value | Effect |
|-----------|-------|--------|
| Maximum latency | 50ms | Feel responsive |
| Minimum pulse duration | 25-30ms | Perceivable |
| Minimum inter-pulse gap | 15-20ms | Distinguishable |

### Pattern Vocabulary

**Reliably Distinguishable Patterns**: 5-9 (Azadi et al. 2014)

**Design Implication**: Don't create complex haptic "languages"

### Typing Performance Impact

| Condition | WPM | Improvement |
|-----------|-----|-------------|
| Without haptic | 29.0-33.0 | Baseline |
| With haptic | 36.5-38.5 | +18-22% |

### Platform Haptic APIs

**iOS UIFeedbackGenerator Types**:
- `.impact` (light/medium/heavy)
- `.selection` (picker scrolling)
- `.notification` (success/warning/error)

**Android VibrationEffect**:
```kotlin
// Predefined effects (Android 10+)
VibrationEffect.createPredefined(EFFECT_CLICK)
VibrationEffect.createPredefined(EFFECT_TICK)

// Custom waveform
VibrationEffect.createWaveform(timings, amplitudes, -1)
```

---

## Gesture Input

### Learning Curves

**Acquisition Speed**:
- Trials to plateau: 10-15
- Weeks to automaticity: 3-5

**Retention**:
- Well-learned gestures: Highly stable
- Rarely-used gestures: Forgotten quickly

### Discoverability Problem

**Swipe Gesture Awareness**: 18-85% (huge variance)

**Implication**: Hidden gestures are accessibility barriers

### Teaching Gestures

**Dynamic Guides**:
- With guides: 27% error rate
- Without guides: 43% error rate
- 37% improvement

**Onboarding Strategies**:
1. Animated hints on first use
2. "Tip" overlays
3. Tutorial mode
4. Gesture trails

### Age-Related Capacity

**Older Adults Maximum**: 6 gesture pairs

**Simplification Required**:
- Fewer gestures
- Larger movement tolerance
- Longer timeout for multi-touch
- Always provide alternatives

### Cross-Platform Gesture Conflicts

| Gesture | iOS | Android | Conflict |
|---------|-----|---------|----------|
| Edge swipe | Back navigation | Varies by launcher | ⚠️ |
| Swipe down | Notification center | Same | ✓ |
| Pinch | Zoom | Same | ✓ |
| Long press | Context menu | Same | ✓ |

### Gesture vs Tap Trade-offs

| Factor | Gesture | Tap |
|--------|---------|-----|
| Discoverability | Low | High |
| Speed (expert) | Fast | Moderate |
| Accessibility | Poor | Good |
| Error rate (novice) | High | Low |

---

## Multi-Modal Input

### Complementary Modalities

**Redundant Input**:
- Voice + touch for confirmation
- Keyboard + mouse for navigation

**Parallel Input**:
- Holding with one hand, tapping with other
- Eye tracking + hand gesture

### Modal Switching Costs

**Context Switch Penalty**: 0.5-2 seconds

**Design Guidance**:
- Don't force modality switches mid-task
- Allow completing actions in started modality
- Provide modality-appropriate alternatives

---

## Accessibility Considerations

### Input Method Requirements

**WCAG 2.1 Requirements**:
- 2.1.1: Keyboard accessible
- 2.5.1: Pointer gestures have alternatives
- 2.5.2: Pointer cancellation (down vs up)
- 2.5.4: Motion actuation alternatives

### Input Alternatives Matrix

| Primary | Alternative 1 | Alternative 2 |
|---------|--------------|---------------|
| Touch tap | Keyboard Enter | Voice command |
| Swipe gesture | Button | Keyboard arrow |
| Drag & drop | Cut/paste | Move dialog |
| Hover | Long press | Focus |
| Voice command | Text input | Menu selection |

---

## Quick Detection Signals

### Keyboard Input Honored
- All actions keyboard-accessible
- Visible focus indicators
- Logical tab order
- Shortcuts shown but not required

### Voice Input Honored
- Always has alternative input
- Latency <500ms
- Error recovery clear
- Privacy-respecting defaults

### Pointer Input Honored
- Touch targets ≥44×44px
- 8px+ spacing between targets
- Edge placement for key actions
- Hover alternatives for touch

### Haptic Input Honored
- Latency <50ms
- Standard platform patterns used
- Limited pattern vocabulary
- Confirmatory feedback for actions

### Gesture Input Honored
- Gestures are discoverable
- Dynamic guides for learning
- Always have alternatives
- Limited gesture vocabulary

---

## Code Patterns to Detect

### Good Patterns
```javascript
// Keyboard accessible
<button onClick={action}>Click or Enter</button>

// Touch target size
.button {
  min-width: 44px;
  min-height: 44px;
  padding: 12px 16px;
}

// Focus visible
.interactive:focus-visible {
  outline: 2px solid #0066CC;
  outline-offset: 2px;
}

// Gesture alternative
<SwipeableItem
  onSwipe={archive}
  alternativeAction={<ArchiveButton />}
/>

// Voice fallback
{voiceSupported ? <VoiceInput /> : <TextInput />}
```

### Warning Patterns
```javascript
// Focus removal (VIOLATION)
*:focus { outline: none; }

// Tiny touch targets
.icon-button { width: 24px; height: 24px; }

// Gesture-only action
<SwipeToDelete /> // No button alternative

// Voice-only feature
{/* No keyboard/touch fallback */}

// Keyboard trap
onKeyDown={(e) => e.preventDefault()}

// Hover-dependent (no touch support)
.menu:hover .submenu { display: block; }
```

### Platform-Specific Checks

**iOS**:
```swift
// Haptic feedback
let generator = UIImpactFeedbackGenerator(style: .medium)
generator.impactOccurred()

// Touch targets (44pt minimum)
button.frame.size = CGSize(width: 44, height: 44)
```

**Android**:
```kotlin
// Haptic feedback
view.performHapticFeedback(HapticFeedbackConstants.CONFIRM)

// Touch targets (48dp minimum)
android:minWidth="48dp"
android:minHeight="48dp"
```

**Web**:
```javascript
// Vibration API (limited support)
navigator.vibrate(200);

// Touch target CSS
.touch-target {
  min-width: 44px;
  min-height: 44px;
  touch-action: manipulation;
}
```
