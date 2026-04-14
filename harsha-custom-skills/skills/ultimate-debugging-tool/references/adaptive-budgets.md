# Adaptive Performance Budgets

Context-aware budget matrix for performance debugging. Select the profile matching your project type, then apply device-tier constraints.

## Budget Profiles by Project Type

### budget-3d (Three.js/WebGL)

| Metric | Desktop Ultra | Desktop High | Mobile High | Mobile Low |
|--------|---------------|--------------|-------------|-----------|
| **FPS Target** | 60 | 60 | 30-60 | 30 |
| **Draw Calls** | <500 | <300 | <100 | <50 |
| **Triangles** | <1M | <500K | <100K | <50K |
| **Heap Memory** | <200MB | <150MB | <100MB | <64MB |
| **GPU Utilization** | 70-90% OK | <70% | <60% | <50% |

**Allowed Features**: Post-processing (EffectComposer merged passes), MeshPhysicalMaterial, multiple lights (studio lighting).

**CWV Targets**: LCP <4s (3D loading exemption), INP <300ms, CLS <0.1.

---

### budget-animation (GSAP/Framer Motion/Lenis)

| Metric | Desktop | Mobile |
|--------|---------|--------|
| **FPS Target** | 60 (mandatory) | 60 target, 30 acceptable |
| **Individual Animation** | <300ms (micro), <800ms (transitions) | Same |
| **JS Bundle** | <200KB compressed | <200KB compressed |
| **Scroll Smoothness** | Mandatory 60fps | Best-effort 60fps |

**CWV Targets (Strict)**: LCP <2.5s, INP <200ms, CLS <0.1.

**Allowed**: GSAP overhead (ScrollTrigger, smooth scroll), will-change with cleanup.

---

### budget-spa (React/Next.js/Remix)

| Metric | Target |
|--------|--------|
| **FPS (Interactions)** | 60 |
| **Initial JS Bundle** | <200KB |
| **Initial CSS Bundle** | <50KB |
| **Re-render Budget** | <16ms per component tree |
| **TTI (Hydration)** | <3.5s |
| **List Render (100 items)** | <100ms |

**CWV Targets (Very Strict)**: LCP <2.5s, INP <200ms (target <150ms), CLS <0.1.

---

### budget-dashboard (Data-Heavy Apps)

| Metric | Desktop | Mobile |
|--------|---------|--------|
| **FPS (Interactions)** | 60 | — |
| **FPS (Data Rendering)** | 30 OK | 30 acceptable |
| **INP (Critical)** | <100ms | <150ms |
| **Table/List Render (1K rows, virtualized)** | <200ms | <400ms |
| **Chart Render (Initial)** | <500ms | <1s |
| **Chart Render (Updates)** | <100ms | <200ms |
| **Memory Growth (8h session)** | Monitor | Monitor |

---

### budget-hybrid (React + Three.js)

Apply the **most permissive** budget where domains overlap:
- **3D sections**: Use `budget-3d` rules.
- **Non-3D React sections**: Use `budget-spa` rules.
- **Shared resources** (bundle size, memory): Combine limits (e.g., JS <350KB total).

---

## Device Tier Detection

Use navigator APIs to auto-select tier:

```javascript
// deviceMemory (Chrome, Edge, Opera)
// hardwareConcurrency (all modern browsers)
// detect-gpu library for GPU detection

const tier = {
  Ultra: deviceMemory >= 8 && dedicatedGPU && hardwareConcurrency >= 8,
  High: deviceMemory >= 4 && hardwareConcurrency >= 4,
  Medium: deviceMemory >= 2 && deviceMemory < 4,
  Low: deviceMemory < 2
};
```

| Tier | RAM | GPU | CPU Cores | Platform |
|------|-----|-----|-----------|----------|
| Ultra | 8GB+ | Dedicated (RTX/RX 6xxx+) | 8+ | Desktop |
| High | 4GB+ | Integrated/mid-range | 4+ | Desktop |
| Medium | 2-4GB | Mobile mid/high (iPhone 13+, Pixel 6+) | 4+ | Mobile |
| Low | <2GB | Mobile low/mid | <4 | Mobile |

---

## Alert Thresholds

For each metric, flag status:

- **GREEN**: ≤80% of budget (normal operation).
- **YELLOW**: 80-100% of budget (monitor, suggest safe optimizations).
- **RED**: >100% of budget (flag immediately, suggest tiered fixes).

Example: FPS budget of 60 → GREEN: ≥60fps, YELLOW: 48-59fps, RED: <48fps.

---

## Budget Override Protocol

### 1. Inline Override (Comment)
```javascript
// @perf-budget: fps=30, gpu=80%, inp=300ms
```

### 2. Project-Level Config
Create `.perfrc.json` at project root:
```json
{
  "budget": "budget-3d",
  "deviceTier": "Medium",
  "overrides": {
    "fps": 30,
    "gpu": 80,
    "inpMs": 300
  }
}
```

### 3. Quality Tier System
If a quality/detail system exists (e.g., ultra/high/medium/low settings), defer to its thresholds and ignore this matrix.

---

## Usage

1. **Identify project type** → select matching profile.
2. **Detect device tier** → apply row constraints.
3. **Monitor metrics** → flag GREEN/YELLOW/RED.
4. **Override if needed** → use `.perfrc.json` or inline comments.
