# Typography & Color Reference

## Typography Fundamentals

### Line Length (Characters Per Line)

**Optimal Range**: 50-75 characters
- Screens tolerate: 80-95 characters
- Below 45: Too many line breaks, jarring
- Above 90: Eye tracking difficulty

**CSS Implementation**:
```css
/* Optimal line length */
p {
  max-width: 65ch; /* ch = character width */
}

/* Responsive */
article {
  max-width: min(75ch, 90vw);
}
```

### Line Height (Leading)

**Optimal Range**: 1.4-1.6× font size
- WCAG 1.4.12 mandates: ≥1.5× for body text

**Impact** (increasing 100%→120%):
- **+20%** reading accuracy
- **-30%** eye strain reported

```css
body {
  line-height: 1.5; /* WCAG compliant */
}

h1, h2, h3 {
  line-height: 1.2; /* Tighter for headings */
}
```

### Font Size Minimums

| Platform | Minimum Body | Notes |
|----------|--------------|-------|
| Web | 16px | Browser default |
| iOS | 17pt | Dynamic Type base |
| Android/Material | 16sp | Scale-independent |

**Smaller Text** (captions, labels):
- Never below 12px
- Consider 14px as practical minimum

### Reading Speed by Font

**Key Finding** (Wallace et al. 2022, N=386+):
- **35% speed difference** between fastest/slowest fonts
- **82% of users' preferred fonts were NOT their fastest**

**Faster Fonts**:
- Higher x-height
- Open counters (a, e, o)
- Distinct letterforms

**Slower Factors**:
- Decorative serifs
- Tight letter spacing
- Low contrast strokes

### Case & Capitalization

| Style | Reading Speed | Use Case |
|-------|---------------|----------|
| Sentence case | Fastest | Body text |
| Title Case | Moderate | Headings |
| ALL CAPS | **10-19% slower** | Emphasis only |

**Never**: All caps for body text or long strings.

### Text Alignment

| Alignment | Best For |
|-----------|----------|
| Left-aligned | Body text (LTR languages) |
| Justified | Formal documents (with hyphenation) |
| Center | Short text, headings |
| Right-aligned | Numeric data, RTL languages |

**Justified Without Hyphenation**: Creates "rivers" of whitespace—avoid.

---

## Variable Fonts

### Performance Benefits

**Monotype Experiment**:
- File size: **88% reduction** (multiple weights in one file)
- Load time: 1800ms → 320ms (**82% faster**)
- CLS: 0.15 → 0.02 (**87% improvement**)

**Browser Support**: 96.12% (January 2026)

### Implementation

```css
@font-face {
  font-family: 'InterVariable';
  src: url('Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}

body {
  font-family: 'InterVariable', system-ui, sans-serif;
  font-weight: 400;
}

/* Optical sizing (if supported) */
h1 {
  font-optical-sizing: auto;
  font-weight: 700;
}
```

### Dark Mode Adjustments

**Problem**: Same font weight appears heavier on dark backgrounds (halation).

**Solution**:
- Body: 400 → 350-380
- Bold: 700 → 600-650

```css
@media (prefers-color-scheme: dark) {
  body {
    font-weight: 380;
  }
  strong, b {
    font-weight: 620;
  }
}
```

---

## Dyslexia Fonts: DEBUNKED

### Research Findings

**No Benefit Found in Peer-Reviewed Studies**:
- Wery & Diliberto (2017): OpenDyslexic no better than Arial
- Kuster et al. (2018, N=170+): No reading speed or accuracy improvement
- Rello & Baeza-Yates (2013): Preference ≠ performance

### What Actually Helps

**Letter Spacing +18%**:
- **+20% faster reading** (Zorzi et al. 2012, N=94)
- **-50% fewer errors**
- Works across font faces

**Implementation**:
```css
.dyslexia-friendly {
  letter-spacing: 0.12em; /* ~18% increase */
  word-spacing: 0.16em;
  line-height: 1.8;
}
```

**Other Evidence-Based Interventions**:
- Larger font size (minimum 14px)
- Higher line spacing (1.8+)
- Left-aligned text (not justified)
- Matte/off-white backgrounds
- Short line lengths (50-60ch)

---

## Dark Mode

### Eye Strain Claims: NOT SUPPORTED

**No conclusive evidence** dark mode reduces eye strain:
- Subjective preference exists
- Objective strain measures inconclusive
- May help in low-light environments only

### Halation Problem

**~50% of people with astigmatism** experience halation:
- White text on black "blooms"
- Reduces readability
- More common than assumed

### Best Practices

| Element | Light Mode | Dark Mode |
|---------|------------|-----------|
| Background | #FFFFFF | #121212 (not pure black) |
| Text | #1A1A1A | #E0E0E0 (not pure white) |
| Contrast | 4.5:1+ | Higher (15.8:1 Material) |

**Material Design Dark Theme**:
- Surface: #121212
- Elevated surfaces: Lighter overlays
- Text: 87% white (high emphasis), 60% (medium), 38% (disabled)

### Adoption

**Android Dark Mode Usage**: 81.9%

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121212;
    --text: #E0E0E0;
    --text-secondary: rgba(255, 255, 255, 0.6);
  }
}
```

---

## Color Psychology: Evidence vs. Myth

### DEBUNKED Claims

**"Red makes you hungry"**:
- Contradicted by controlled studies (Schlintl & Schienle 2020, N=448)
- Fast food correlation ≠ causation

**Baker-Miller pink reduces aggression**:
- Failed replication (Genschow et al. 2015, N=59)
- Original study deeply flawed

**Pink-blue gender preferences are innate**:
- Culturally learned (Davis et al. 2021, N=232)
- Historical reversal in 20th century

### ESTABLISHED Effects

**Red Attention Capture**:
- Robust across 5+ independent labs
- Evolutionary basis (blood, ripe fruit)
- Use for alerts, errors, stop actions

**Blue Light & Arousal**:
- Blue light **increases** arousal (not calming)
- Via melanopsin at 446-477nm
- Avoid blue-heavy screens before sleep

### Cultural Color Meanings

| Color | West | East Asia |
|-------|------|-----------|
| Red | Danger, stop | Luck, prosperity |
| White | Purity, weddings | Death, mourning |
| Green | Go, nature | Islam (Middle East) |
| Yellow | Caution | Royalty (China) |

**Financial UI Color Reversal**:
- US/Europe: Green = gains, Red = losses
- Japan/China/Korea: **OPPOSITE** (red = positive)

---

## Color Vision Deficiency

### Prevalence

| Type | Males | Females |
|------|-------|---------|
| Total CVD | ~8% | ~0.5% |
| Deuteranomaly (weak green) | ~5% | <1% |
| Protanomaly (weak red) | ~1% | <1% |
| Tritanomaly (weak blue) | <1% | <1% |

### Design Requirements

**Never rely on color alone**:
```html
<!-- Bad: Color only -->
<span class="error" style="color: red;">Invalid</span>

<!-- Good: Color + icon + text -->
<span class="error">
  <svg class="icon-error">...</svg>
  Error: Invalid email format
</span>
```

**Safe Color Combinations**:
- Blue + Orange (most CVD-safe)
- Blue + Yellow
- Avoid: Red + Green together

### Testing Tools

- Sim Daltonism (macOS)
- Color Oracle (cross-platform)
- Chrome DevTools color vision simulation

---

## Contrast Requirements

### WCAG 2.x

| Level | Normal Text | Large Text | UI Components |
|-------|-------------|------------|---------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | N/A |

**Large Text**: ≥18pt regular, ≥14pt bold

### APCA (WCAG 3.0 Candidate)

Advanced Perceptual Contrast Algorithm:
- Lc 90: Preferred body text
- Lc 75: Minimum body text
- Lc 60: Large text, headlines
- Lc 45: Placeholder, secondary

**Key Difference**: APCA accounts for polarity (dark-on-light vs light-on-dark).

### Age-Related Contrast

| Age Range | Sensitivity |
|-----------|-------------|
| 20-29 | Baseline |
| 60-69 | ~70% of baseline |
| 70-74 | 40-70% of baseline |

**Implication**: Meet AAA (7:1) for aging populations.

---

## Data Visualization Colors

### Rainbow Colormaps: AVOID

**52 percentage point diagnostic accuracy loss** (Borkin et al. 2011)
- Perceptually non-uniform
- Creates false boundaries
- CVD-inaccessible

### Recommended Palettes

**Sequential** (low → high):
- Single hue, varying lightness
- Viridis, Cividis (CVD-safe)

**Diverging** (negative ↔ positive):
- Two hues meeting at neutral
- Blue-white-red (avoid for CVD-critical)

**Categorical**:
- Maximum 5-7 distinguishable colors
- Colorbrewer qualitative sets

---

## Visual Hierarchy

### Hierarchy Tools (Priority Order)

1. **Size**: Largest = most important
2. **Color/Contrast**: High contrast = emphasis
3. **Position**: Top-left (LTR) = first seen
4. **Whitespace**: More space = more importance
5. **Typography**: Weight, style
6. **Imagery**: Draws eye before text

### Establishing Hierarchy

```css
/* Clear hierarchy through type scale */
h1 { font-size: 2.5rem; font-weight: 700; }
h2 { font-size: 2rem; font-weight: 600; }
h3 { font-size: 1.5rem; font-weight: 600; }
body { font-size: 1rem; font-weight: 400; }
.caption { font-size: 0.875rem; color: #666; }
```

### F-Pattern Scanning

**CAUTION**: F-pattern indicates poor design
- Users resort to F-pattern when hierarchy is unclear
- Well-designed pages show more efficient patterns
- Don't design FOR F-pattern; design to prevent it

---

## Spacing & Layout

### Spacing Systems

**4px/8px Base Grid**:
```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
}
```

**Cognitive Benefit**: Consistent spacing aids pattern recognition (Gestalt proximity).

### The "Whitespace = Comprehension" Myth

**DEBUNKED**: The oft-cited "20% comprehension increase" has no valid source.
- Whitespace aids grouping (Gestalt)
- Whitespace affects aesthetics
- No direct comprehension relationship proven

### Responsive Typography

```css
/* Fluid typography */
h1 {
  font-size: clamp(1.75rem, 4vw + 1rem, 3.5rem);
}

/* Container queries for component-level */
@container (min-width: 400px) {
  .card-title { font-size: 1.5rem; }
}
```

---

## Icons & Typography Together

### Recognition Rates

**Icon-Only Recognition**:
- Hamburger menu (☰): 52%
- Gear (settings): 76%
- Share: Platform-inconsistent

**Icon + Label**: **88% correct** vs 60% icon-only (+28pp)

### Implementation

```html
<!-- Accessible icon with label -->
<button>
  <svg aria-hidden="true">...</svg>
  <span>Settings</span>
</button>

<!-- Icon-only with accessible name -->
<button aria-label="Settings">
  <svg aria-hidden="true">...</svg>
</button>
```

### Universal Icons (Only 3)

1. 🏠 House = Home
2. 🖨️ Printer = Print  
3. 🔍 Magnifying glass = Search

**Everything else requires labels for clarity.**

---

## Quick Detection Signals

### Typography Honored
- Line length 50-75ch
- Line height ≥1.5
- Font size ≥16px body
- Sentence case for body text
- Left-aligned text (LTR)

### Color Used Appropriately
- Never color-only meaning
- Sufficient contrast (4.5:1+)
- CVD-safe combinations
- Cultural considerations

### Dark Mode Implemented Well
- Not pure black (#121212+ not #000000)
- Reduced font weight
- Higher contrast maintained
- Off-white text (#E0E0E0)

### Visual Hierarchy Clear
- Obvious importance order
- Consistent spacing system
- Type scale with clear levels
- Whitespace for grouping

---

## Code Patterns to Detect

### Good Patterns
```css
/* Typography fundamentals */
body {
  font-size: 16px;
  line-height: 1.5;
}

article {
  max-width: 65ch;
}

/* Dark mode with reduced weight */
@media (prefers-color-scheme: dark) {
  body { font-weight: 380; }
}

/* Color not sole indicator */
.error {
  color: #D32F2F;
  border-left: 3px solid #D32F2F;
}
.error::before {
  content: "⚠ ";
}
```

### Warning Patterns
```css
/* Line length too long */
article { width: 100%; } /* No max-width */

/* Insufficient line height */
body { line-height: 1.2; }

/* Small font */
body { font-size: 12px; }

/* Pure black dark mode */
body.dark { background: #000000; }

/* Color-only meaning */
.status-good { color: green; }
.status-bad { color: red; }
/* No other indicator */
```

### Accessibility Checks
```javascript
// Contrast check
function meetsWCAG(foreground, background) {
  const ratio = getContrastRatio(foreground, background);
  return {
    AA: ratio >= 4.5,
    AAA: ratio >= 7,
    largeAA: ratio >= 3
  };
}

// Color meaning check
// Search for color-only states
const colorOnlyRisk = element.style.color && 
  !element.querySelector('svg, img, [aria-label]');
```
