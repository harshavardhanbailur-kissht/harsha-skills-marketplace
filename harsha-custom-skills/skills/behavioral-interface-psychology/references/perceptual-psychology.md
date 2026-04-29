# Perceptual Psychology Reference

## Weber-Fechner Law & Logarithmic Perception

### Core Principle
Human perception is fundamentally **non-linear**. The relationship between physical stimulus intensity and perceived intensity follows logarithmic functions.

**Weber's Law**: ΔI/I = k (constant)
- The just-noticeable difference (JND) is proportional to the original stimulus intensity
- A 1-unit change from 10 feels the same as a 10-unit change from 100

**Fechner's Law**: S = k × log(I)
- Perceived sensation (S) is proportional to the logarithm of stimulus intensity (I)

### Audio Perception

**Volume Controls Must Use Logarithmic Curves**
- Linear slider movement should produce logarithmic amplitude change
- Formula for 60dB range: `amplitude = x⁴` (where x is slider position 0-1)
- Decibels are already logarithmic: 10dB increase = 10× power, 2× perceived loudness

**Critical Audio Thresholds**:
| Threshold | Value | Implication |
|-----------|-------|-------------|
| Minimum audible difference | ~1 dB | Steps smaller than this waste precision |
| Comfortable speech | 60-70 dB | Default volume target |
| Hearing damage threshold | 85 dB | Maximum for sustained exposure |
| Pain threshold | 120+ dB | Never output |

**Platform Implementations**:
- iOS: `AVAudioSession.setCategory()` with logarithmic gain curves
- Android: `AudioManager` uses 0-100 scale internally mapped logarithmically
- Web Audio API: Gain nodes require manual logarithmic conversion

### Visual Perception

**Brightness & Gamma Correction**

sRGB displays use gamma 2.2, meaning:
- RGB value 128/255 (50% digital) produces only **22% actual light output**
- RGB value 187/255 produces ~50% perceived brightness
- Linear gradients in RGB space appear uneven to human perception

**Perceptual Uniformity**:
- CIELAB/CIELUV color spaces designed for perceptual uniformity
- HSL/HSV are NOT perceptually uniform (avoid for color pickers)
- Use OKLCH or CIELAB for accessible color palette generation

**Contrast Perception (Weber Contrast)**:
```
C = (L_target - L_background) / L_background
```
- On dark backgrounds: small absolute differences more noticeable
- On light backgrounds: larger absolute differences needed

### Size & Distance Perception

**Size Estimation Errors**:
- Area estimation: Underestimate by 15-30% (use 1D lengths for comparisons)
- Volume estimation: Severe underestimation (avoid bubble charts for precision)
- Stevens' Power Law: Perceived area ≈ actual area^0.7

**Practical Application**:
- Pie charts: Limited to 3-5 segments maximum
- Bar charts: Superior for precise comparisons
- Circle size encoding: Use radius proportional to √value, not value

---

## Time Perception

### Subjective Duration

**Progress Bar Perception** (Harrison et al., CHI 2010, N=50):
- Backwards-moving ribbing: **11% reduction** in perceived duration
- Accelerating progress (slow→fast): Feels **shorter**
- Decelerating progress (fast→slow): Feels **longer**, highest abandonment

**Optimal Progress Design**:
1. Start slower, accelerate toward end
2. Use backwards-moving visual patterns
3. Never show stalled or backwards movement
4. For unknown duration: Use pulsing animation, not stuck spinner

### Response Time Thresholds

| Threshold | Effect | Design Implication |
|-----------|--------|-------------------|
| **100ms** | Instantaneous feel | Button feedback, form validation |
| **200-300ms** | Deliberate interaction | Transitions, hover states |
| **1 second** | Attention maintenance | Page loads, complex operations |
| **10 seconds** | Attention limit | Maximum before progress feedback required |

**Source**: Jakob Nielsen (usability research, 1990s), Card, Moran & Newell (1983)

### Animation Timing

**Frame Rate Perception**:
- 14 fps: Minimum for continuous motion perception
- 24 fps: Cinematic standard (motion blur aids perception)
- 60 fps: Gold standard for interfaces
- 90+ fps: Diminishing returns (VR exception: critical for presence)

**Consistency > Absolute Rate**: A steady 30fps feels better than 60fps with drops to 30fps

**Animation Duration Guidelines**:
| Animation Type | Duration | Rationale |
|---------------|----------|-----------|
| Micro-interactions | 100-200ms | Fast feedback |
| Transitions | 200-300ms | Smooth but not slow |
| Complex animations | 300-500ms | Allow comprehension |
| Dramatic effects | 500-1000ms | Emphasis, rare use |

---

## Probability & Randomness Perception

### The Gambler's Fallacy Problem

Humans expect "true random" to alternate more than it actually does:
- After 5 heads, we expect tails (but probability remains 50%)
- Three identical items in a row feels "broken" even if random
- Clustering feels like bias

### Shuffle Algorithms

**True Random Feels Biased**:
- Spotify abandoned true random shuffle
- Apple introduced "smart shuffle" to reduce perceived repetition

**Quasi-Random Solutions**:
- Low-discrepancy sequences (Halton, Sobol)
- ±10-15% jitter from even distribution
- Minimum spacing constraints between similar items

**Design Guidance**:
```
// Bad: True random
const next = Math.floor(Math.random() * items.length);

// Better: Weighted random with recency penalty
const weights = items.map((item, i) => 
  recentlyPlayed.includes(i) ? 0.1 : 1.0
);
const next = weightedRandom(items, weights);
```

### Risk & Probability Display

**Humans Cannot Accurately Perceive Probabilities**:
- Overweight small probabilities (lottery effect)
- Underweight large probabilities
- Perceive 0.01% and 1% as similarly "rare"

**Effective Formats**:
| Format | Use Case | Example |
|--------|----------|---------|
| Natural frequencies | Medical risk | "3 in 1000" vs "0.3%" |
| Icon arrays | Health outcomes | 100 person icons, 3 highlighted |
| Absolute numbers | Comparisons | "1 in 50" vs "2 in 100" |

**Avoid**: Percentages below 1%, relative risk alone ("50% more likely" is meaningless without base rate)

---

## Gestalt Principles

### Core Principles with Implementation

**1. Proximity**
- Elements close together perceived as grouped
- Implementation: Consistent spacing systems (4px/8px grid)
- Code signal: `gap`, `margin`, `padding` consistency

**2. Similarity**
- Similar elements perceived as related
- Implementation: Consistent styling for related functions
- Code signal: Shared CSS classes, design tokens

**3. Continuity**
- Eye follows smooth paths
- Implementation: Alignment grids, visual flow
- Code signal: `align-items`, grid systems

**4. Closure**
- Mind completes incomplete shapes
- Implementation: Implied boundaries, whitespace grouping
- Code signal: Borderless card designs with shadow/spacing

**5. Figure-Ground**
- Foreground elements distinguished from background
- Implementation: Elevation, contrast, blur
- Code signal: `z-index`, `box-shadow`, `backdrop-filter`

**6. Common Fate**
- Elements moving together perceived as grouped
- Implementation: Coordinated animations
- Code signal: Shared animation triggers, choreographed motion

### Practical Application Matrix

| Principle | Spacing Impact | Color Impact | Motion Impact |
|-----------|---------------|--------------|---------------|
| Proximity | Primary | Secondary | N/A |
| Similarity | Secondary | Primary | Secondary |
| Continuity | Primary | Secondary | Primary |
| Closure | Primary | Secondary | N/A |
| Figure-Ground | Secondary | Primary | Secondary |
| Common Fate | N/A | Secondary | Primary |

---

## Shape & Form Psychology

### Curvature Preference

**Rounded Shapes Preferred** (Bar & Neta, 2006):
- Effect observable at 84ms exposure (pre-conscious)
- Curved contours: Approach motivation
- Sharp angles: Threat/avoidance response
- Amygdala activation for angular shapes

### Squircle Geometry

**Apple's Superellipse** (iOS 7+):
```
|x/a|^n + |y/b|^n = 1, where n ≈ 5.2
```

**Benefits**:
- G2 curvature continuity (smooth acceleration of curve)
- No abrupt tangent changes at corners
- Feels more "natural" than CSS border-radius

**CSS Approximation** (limited):
```css
/* True squircle requires SVG or canvas */
border-radius: 22%; /* Rough approximation */
```

### Icon Shape Conventions

**Near-Universal Recognition** (only 3):
1. 🏠 House = Home
2. 🖨️ Printer = Print
3. 🔍 Magnifying glass = Search

**Everything Else Requires Labels**:
- Hamburger menu (☰): Only 52% recognition
- Share icon: Platform-inconsistent
- Gear: 76% recognition for "settings"

---

## Pattern Detection & Attention

### Preattentive Processing (<250ms)

**Features detected automatically**:
- Color (hue, saturation)
- Size
- Orientation (line angle)
- Motion
- Position

**NOT preattentive** (require serial search):
- Conjunctions (red AND circular)
- Complex patterns
- Text content

### Design Implications

**Dashboard Alerts**: Use preattentive features
```css
/* Good: Color immediately visible */
.alert-critical { background: #FF4444; }

/* Bad: Requires reading */
.alert-critical { border-left: 2px solid #FF4444; }
.alert-critical::before { content: "CRITICAL"; }
```

**Data Visualization**: One preattentive feature per encoding
```
// Good: Color = category, Size = value
// Bad: Color = category AND status (conjunction)
```

---

## Visual Search & Scanning

### Eye Movement Patterns

**Saccades**: Rapid jumps (200-250°/sec)
- Average fixation: 200-300ms
- Cannot process during saccade

**F-Pattern** (Nielsen, 2006):
- CAUTION: Indicates poor design, not goal state
- Users scan in F when content lacks clear hierarchy
- Well-designed pages show more efficient patterns

### First Impressions

**50ms Exposure** (Lindgaard et al., 2006):
- Aesthetic judgment formed
- Correlates with later trustworthiness ratings
- Users decide to stay or leave

**2.6 Second Rule**:
- Core value proposition must be clear
- Primary action visible without scrolling
- Brand identity established

---

## Haptic & Vestibular Perception

### Touch Perception Thresholds

**Vibration**:
- Optimal frequency: 250 Hz (Pacinian corpuscles)
- Maximum latency: 50ms for responsive feel
- Minimum pulse: 25-30ms
- Minimum gap: 15-20ms between pulses
- Pattern vocabulary: 5-9 distinguishable patterns

### Motion Sickness (Vestibular)

**Prevalence**: 35% of adults 40+ have vestibular dysfunction

**Triggers**:
- Parallax scrolling
- Motion-locked backgrounds
- Zoom/scale animations
- Auto-playing video

**Mitigation**:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Cross-Modal Perception

### Audio-Visual Binding

**McGurk Effect**: Visual lip movements alter perceived speech sounds
- Implication: Video and audio must be perfectly synced

**Temporal Binding Window**:
- Audio-visual: ±80ms
- Beyond this: Perceived as separate events

### Synesthetic Design Principles

| Visual | Audio Correlation |
|--------|-------------------|
| Bright | High pitch |
| Dark | Low pitch |
| Sharp | Staccato |
| Curved | Smooth, legato |
| Large | Loud |
| Small | Quiet |

**Application**: Loading sounds should match visual progress

---

## Evidence Quality Notes

### Strong (Replicated, Large N)
- Weber-Fechner logarithmic relationships
- Response time thresholds (100ms/1s/10s)
- Rounded shape preference
- Preattentive features

### Moderate (Peer-reviewed, Limited Replication)
- Progress bar perception (Harrison et al.)
- 50ms aesthetic judgment
- Gestalt grouping strengths

### Implementation Convention (Not Empirically Validated)
- Specific animation durations
- Exact gamma correction values
- Spacing system multiples

---

## Quick Detection Signals

**Logarithmic Perception Honored**:
- Volume: `Math.pow()`, `log()`, exponential curves
- Brightness: sRGB-aware calculations
- Size: Square root scaling for areas

**Time Perception Honored**:
- Progress: Accelerating animations
- Response: <100ms for immediate feedback
- Duration: Appropriate animation lengths

**Randomness Perception Honored**:
- Shuffle: Recency penalties, spacing constraints
- Probability: Natural frequencies, icon arrays

**Pattern Recognition Honored**:
- Consistent spacing systems
- Preattentive alert features
- Clear visual hierarchy
