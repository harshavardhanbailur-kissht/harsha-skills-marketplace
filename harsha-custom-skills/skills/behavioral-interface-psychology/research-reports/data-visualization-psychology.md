# Data Visualization Psychology Research

## Executive Summary

This report synthesizes research on visualization perception, including chart type selection, perceptual accuracy, color psychology, animation, dashboard design, and deceptive visualization patterns.

---

## 1. Chart Type Selection Psychology

### Pie Charts

**Perceptual Limitations:**
- Humans are better at comparing lengths than angles and areas
- Ineffective with more than 3-5 categories
- Exploded pie charts show significantly higher error rates

**Where They Work:**
- Comparing a category to total when close to 25% or 50%
- Most people identify segment magnitude within **plus/minus 3 percentage points**
- Mean bias around **1 percentage point**

**Donut vs Pie:** Similar accuracy; donut charts are no less accurate for part-to-whole comparisons.

### Bar vs Line Chart Comprehension

- Bar graphs facilitate association between bars and x-axis values
- Line graphs can impair differentiation of individual points
- Participants had better comprehension with bar charts for all tested decision types

### Area Chart Issues

- Human brain does not process area calculations well
- **Line-width illusion:** Humans evaluate distance at closest point rather than vertical distance
- Stacking distorts perception of individual category sizes

### Network Graph Cognitive Load

- Significant difficulty finding shortest paths with **>50 nodes** (high density)
- Even low-density graphs difficult with **>100 nodes**

---

## 2. Perceptual Accuracy by Encoding

### Cleveland & McGill Hierarchy (1984)

**Ranking (Most to Least Accurate):**
1. Position along a common scale
2. Positions along nonaligned scales
3. Length, direction, angle
4. Area
5. Volume, curvature
6. Shading, color saturation

### Weber's Law in Visualization

- JND (Just Noticeable Difference) increases with stimulus magnitude
- Can enhance charts by alleviating perceptual ambiguities

### Pre-attentive Features

**Processed in parallel (<250ms):**
- Color
- Orientation
- Shape
- Size/Length
- Movement
- Texture

---

## 3. Color in Visualization

### Palette Types

| Type | Best For | Key Guideline |
|------|----------|---------------|
| Sequential | Ordered data low-to-high | Light for low, dark for high |
| Diverging | Data with meaningful midpoint | Equal emphasis on extremes |
| Categorical | Qualitative data | Limit to **10 or fewer colors** |

### Rainbow Colormap Problems

- Visual errors up to **7.5% of total data variation**
- Creates false boundaries at color transitions
- **47% of hydrology papers** had scientifically incorrect visualizations
- Much slower and more error-prone than single-hue alternatives

### CVD-Safe Design

- Affects **>4%** of population
- WCAG 2.1 minimum contrast ratio: **4.5:1**
- Blue-yellow palettes most colorblind-friendly
- Use patterns and textures alongside color

---

## 4. Animation & Interaction

### Animated Transitions

- Can significantly improve graphical perception
- Gestalt principle of Common Fate: Objects with similar changes are grouped
- Avoid occlusion during transitions

### Animation Timing

| Duration | Use Case |
|----------|----------|
| 150-350ms | Product animation |
| 200-300ms | Small UI animations |
| 400-500ms | Larger motion |
| 1 second | Upper limit of user flow |

### Small Multiples vs Animation

- **Small multiples:** Faster performance, better for comparisons
- **Animation:** Better for seeing trends and movement
- **User preference:** Animation despite better performance with small multiples

---

## 5. Dashboard Psychology

### Information Density

- Working memory: **5-7 chunks** simultaneously (Miller's Law)
- Translate to **5-7 primary widgets** in viewport
- **<40% information density** correlates with **63% faster pattern recognition**

### Attention Patterns

- Top-left quadrant gains maximum attention
- Use F-pattern, Z-pattern, or Gutenberg diagram
- Warm colors highlight attention areas

### Alert Fatigue

- **<10% actionable** = significant noise problem
- Healthy systems: **30-50%** actionable rates
- Risk-based scoring ranks alerts by impact and likelihood

### Real-time Data Perception

- **13ms:** Fastest human visual processing rate
- **75-100ms:** Imperceptible degradation threshold
- **15 seconds:** Brain's continuity field for updates

---

## 6. Deceptive Visualization

### Truncated Axis Effects

- Leads to exaggeration or understatement of quantities
- Axis manipulations had **strongest negative effect** on interpretation accuracy
- Even high data literacy learners were misled

### 3D Chart Distortion

- Elements further from viewer appear smaller
- Can misrepresent data magnitude
- **No significant difference** in user understanding between 2D and 3D bar charts
- Users express preference for 2D when reading values

### Dual-Axis Manipulation

- Major issue in graph manipulation
- Inverted axis causes reversal of message, leading to false conclusions

---

## 7. Narrative Visualization

### Segel & Heer Framework (2010)

| Approach | Characteristics |
|----------|-----------------|
| Author-Driven | Linear path, heavy messaging, minimal interactivity |
| Reader-Driven | No prescribed ordering, high interactivity |

### Scrollytelling Effectiveness

- **67%** chose scrollytelling as "Engaging"
- **75%** expressed positive effects on reading experience
- Provides sense of control and discoverability

### Data-Ink Ratio (Tufte)

- "A large share of ink should present data-information"
- Minimize chartjunk
- **However:** Chartjunk may increase **memorability and engagement**

---

## Key Thresholds Summary

| Metric | Value | Source |
|--------|-------|--------|
| Dashboard widgets | 5-7 maximum | Miller's Law |
| Information density | <40% for fast recognition | UX Magazine |
| Pie chart accuracy | plus/minus 3 percentage points | SAGE |
| Network graph threshold (high density) | >50 nodes | arXiv |
| Network graph threshold (low density) | >100 nodes | arXiv |
| Rainbow colormap error | up to 7.5% | Copernicus |
| CVD population affected | >4% | PLOS ONE |
| WCAG contrast ratio | 4.5:1 minimum | WCAG 2.1 |
| Animation (small UI) | 200-300ms | NN/g |
| Animation (large motion) | 400-500ms | NN/g |
| Alert actionability (healthy) | 30-50% | Monte Carlo |
| Scrollytelling engagement | 67% | ACM DL |

---

## Sources

- Cleveland & McGill (1984) - Graphical Perception
- Heer & Bostock - Crowdsourcing Graphical Perception
- Heer & Robertson - Animated Transitions
- Segel & Heer - Narrative Visualization
- Baymard Institute
- Nielsen Norman Group
