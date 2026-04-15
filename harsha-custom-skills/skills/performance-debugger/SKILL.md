---
name: performance-debugger
description: Context-aware performance optimization and debugging system for web applications. Detects project type, respects intentional design patterns from other skills (3D graphics, UI/UX, animations), and provides measurement-backed fixes with safe/moderate/aggressive tiers. Handles animation jank, memory leaks, Core Web Vitals, Three.js/WebGL, React, GSAP, Framer Motion, and mobile optimization. Complements gas-debugger for unified debugging + performance workflows.
---

# Performance Debugger v2 — Context-Aware

**Mission: Measure first, understand intent, optimize what actually matters.**

## Core Principle

NEVER blindly optimize. Always:
1. **Detect** what the project is (3D experience? React SPA? Animation-heavy marketing site?)
2. **Measure** actual performance (is there even a problem?)
3. **Respect** intentional design patterns (MeshPhysicalMaterial, post-processing, GSAP animations)
4. **Offer tiered fixes** (safe → moderate → aggressive, with quality trade-off descriptions)

## Quick Start

```
PHASE 0: CONTEXT DETECTION (always first)
    │
    ├── Analyze package.json, imports, file structure
    ├── Detect project type (3d-experience | react-spa | animation-site | dashboard | hybrid)
    ├── Detect skill patterns (3D Graphics Mastery, UI/UX Mastery signatures)
    ├── Set adaptive performance budgets for detected type + device tier
    │
    ▼
PHASE 1: MEASUREMENT (before any code changes)
    │
    ├── Generate profiling harness (paste-in-DevTools snippets)
    ├── Identify actual bottlenecks (CPU vs GPU, which phase of frame pipeline)
    ├── Establish baseline metrics (FPS, frame time p95, memory, CWV)
    │
    ▼
PHASE 2: ANALYSIS (context-aware static + heuristic)
    │
    ├── Smart pattern detection (scope-aware, lifecycle-aware)
    ├── Flag genuine issues vs. intentional patterns
    ├── Categorize by impact (measured or estimated)
    │
    ▼
PHASE 3: FIX GENERATION (tiered)
    │
    ├── SAFE fixes (no visual change: code splitting, lazy loading, cleanup)
    ├── MODERATE fixes (minor visual change: shadow quality, texture res)
    ├── AGGRESSIVE fixes (visible quality reduction: disable effects, simplify)
    │
    ▼
PHASE 4: VERIFICATION (measurement-backed)
    │
    ├── Re-measure with same profiling harness
    ├── Compare before/after metrics
    ├── Verify visual quality preserved (for safe/moderate fixes)
    └── Document actual improvement
```

## Phase 0: Context Detection

Before ANY performance analysis, detect the project context. Read `references/context-detection.md` for the full detection system.

### Project Type Detection

Analyze `package.json` dependencies and source imports:

| Signal | Project Type | Budget Profile |
|--------|-------------|----------------|
| `three`, `@react-three/fiber` | 3D Experience | `budget-3d` |
| `gsap`, `lenis`, `framer-motion` (no three) | Animation Site | `budget-animation` |
| `react`, `next`, `remix` (no three/gsap) | React SPA | `budget-spa` |
| `chart.js`, `recharts`, `d3` (primary) | Data Dashboard | `budget-dashboard` |
| Mixed signals | Hybrid | `budget-hybrid` |

### Skill Pattern Detection

Check for patterns from known Claude skills. If detected, RESPECT them:

**3D Web Graphics Mastery signatures:**
- `MeshPhysicalMaterial` → intentional premium material, do NOT suggest MeshStandard
- `EffectComposer` with merged passes → intentional post-processing, do NOT remove
- GSAP proxy pattern (`gsap.to(proxy, { onUpdate })`) → correct Three.js animation
- `lagSmoothing(0)` → intentional stutter prevention
- `Math.min(clock.getDelta(), 1/30)` → intentional delta capping
- `detect-gpu` + quality tiers → intentional adaptive quality system
- Studio lighting (3+ lights) → intentional premium lighting

**UI/UX Mastery signatures:**
- CSS custom properties for motion timing (`--duration-fast`, `--ease-out`)
- `prefers-reduced-motion` media queries → accessibility compliance
- Disney animation principles (squash/stretch, anticipation)

When an intentional pattern is detected, mark it as:
```
STATUS: intentional-pattern
SKILL: 3d-web-graphics-mastery
PATTERN: post-processing-stack
ACTION: monitor-only (unless measured bottleneck)
SAFE-ALTERNATIVE: reduce effect resolution (half-res bloom)
```

### Adaptive Budgets

See `references/adaptive-budgets.md` for complete budget matrix. Summary:

| Project Type | FPS Desktop | FPS Mobile | LCP | INP | Draw Calls | GPU Usage |
|-------------|-------------|------------|-----|-----|------------|-----------|
| 3D Experience | 60 | 30 | <4s | <300ms | <500 | 70-90% OK |
| Animation Site | 60 | 60 | <2.5s | <200ms | N/A | <50% |
| React SPA | 60 | 60 | <2.5s | <200ms | N/A | <30% |
| Dashboard | 60 | 30 | <3s | <100ms | N/A | <20% |

## Phase 1: Measurement

ALWAYS measure before suggesting fixes. See `references/runtime-profiling.md` for full profiling toolkit.

### Quick Profiling Harness (paste in DevTools console)

Generate a measurement snippet for the detected project type:

**For animation/3D projects — Frame Time Analysis:**
```javascript
// Frame Time Profiler — paste in DevTools console
(()=>{const f=[],d=5000;let l=performance.now();const m=t=>{const dt=t-l;if(dt<1000)f.push(dt);l=t;if(t-f[0]<d)requestAnimationFrame(m);else{const s=[...f].sort((a,b)=>a-b);console.table({'Frames':s.length,'Avg':+(s.reduce((a,b)=>a+b)/s.length).toFixed(2)+'ms','P50':+s[Math.floor(s.length*.5)].toFixed(2)+'ms','P95':+s[Math.floor(s.length*.95)].toFixed(2)+'ms','P99':+s[Math.floor(s.length*.99)].toFixed(2)+'ms','Jank(>16.67ms)':s.filter(t=>t>16.67).length,'Severe(>50ms)':s.filter(t=>t>50).length})}};requestAnimationFrame(m)})();
```

**For React apps — Re-render Analysis:**
```javascript
// Check for unnecessary re-renders
// In React DevTools > Profiler > "Highlight updates when components render"
// Or programmatically with why-did-you-render
```

**For CWV-focused — Core Web Vitals:**
```javascript
// CWV Quick Check
import('https://unpkg.com/web-vitals@4?module').then(m=>{
  m.onLCP(console.log);m.onINP(console.log);m.onCLS(console.log);
});
```

### What to Measure

| Project Type | Primary Metrics | Secondary Metrics |
|-------------|----------------|-------------------|
| 3D Experience | Frame time p95, GPU time, draw calls | Memory growth, texture VRAM |
| Animation Site | Frame time during animation, jank count | CLS during animation, INP |
| React SPA | INP, re-render count, bundle size | LCP, CLS, memory |
| Dashboard | INP, data render time | Memory over time, list performance |

## Phase 2: Context-Aware Analysis

Read `references/performance-patterns.md` for complete detection patterns.

### Issue Categories (P1-P7)

**P1: Animation & Rendering** → `references/animation-performance.md`
**P2: JavaScript Performance** → (inline patterns below)
**P3: React-Specific** → `references/react-performance.md`
**P4: Three.js / WebGL** → `references/threejs-webgl-performance.md`
**P5: Memory & Resources** → `references/memory-management.md`
**P6: Core Web Vitals** → `references/core-web-vitals.md`
**P7: Mobile & Cross-Device** → `references/mobile-optimization.md`

### Context-Aware Detection Rules

When scanning, apply these context rules:

```
IF project_type == '3d-experience':
  - SKIP: MeshPhysicalMaterial warnings (intentional)
  - SKIP: post-processing stack warnings (intentional if using EffectComposer)
  - SKIP: multiple lights warnings (intentional studio lighting)
  - SKIP: GSAP proxy overhead warnings (required pattern)
  - FLAG: object creation inside useFrame/render loop (genuine issue)
  - FLAG: missing resource disposal (genuine issue)
  - FLAG: unbounded texture loading without cleanup (genuine issue)
  - FLAG: missing delta time capping (genuine issue)

IF project_type == 'animation-site':
  - SKIP: GSAP ScrollTrigger setup warnings (intentional)
  - SKIP: Lenis smooth scroll continuous interpolation (intentional)
  - SKIP: will-change on animated elements (intentional IF with cleanup)
  - FLAG: will-change WITHOUT cleanup (genuine issue)
  - FLAG: animating layout properties (genuine issue)
  - FLAG: missing prefers-reduced-motion support (accessibility issue)
  - FLAG: scroll handler without RAF/passive (genuine issue)

IF project_type == 'react-spa':
  - Apply all React patterns (P3)
  - FLAG: inline objects in JSX
  - FLAG: missing memo on expensive components
  - FLAG: context causing cascading re-renders
  - CHECK: React Compiler present? (may auto-fix memoization)

ALWAYS flag regardless of project type:
  - Memory leaks (P5-001 through P5-006)
  - Missing image dimensions (P6-003)
  - Render-blocking resources (P6-002)
  - Non-passive touch/wheel listeners (P1-007)
```

## Phase 3: Tiered Fix Generation

Every fix MUST be categorized:

### SAFE Fixes (No Visual Change)
- Code splitting and lazy loading
- Resource cleanup and disposal
- Event listener cleanup
- Bundle optimization
- Image optimization (format, compression)
- Preload/prefetch critical resources
- Passive event listeners
- Memory leak fixes

### MODERATE Fixes (Minor Visual Change)
- Reduce shadow map resolution (2048 → 1024)
- Reduce post-processing resolution (half-res bloom)
- Lower MSAA samples (8 → 4)
- Reduce particle count by 30%
- Simplify easing curves
- Reduce texture resolution by one tier

### AGGRESSIVE Fixes (Visible Quality Reduction)
- Disable post-processing effects
- Switch MeshPhysicalMaterial → MeshStandardMaterial
- Disable shadows entirely
- Reduce geometry detail significantly
- Remove animation effects
- Lower pixel ratio below 1.5

**Present aggressive fixes with explicit trade-off:**
```
AGGRESSIVE FIX: Disable SSAO post-processing
QUALITY IMPACT: Removes ambient occlusion depth effect from 3D scene
PERFORMANCE GAIN: ~3-5ms per frame on mid-range GPU
RECOMMENDATION: Only apply if measured GPU time exceeds budget by >30%
```

## Phase 4: Verification

After applying fixes, RE-MEASURE using the same profiling harness from Phase 1.

```
VERIFICATION REPORT:
┌─────────────────────────────────────────┐
│ Metric           │ Before  │ After     │
├─────────────────────────────────────────┤
│ Frame time p95   │ 24.3ms  │ 14.8ms   │ ✅ Under 16.67ms
│ Jank frames      │ 12%     │ 2%       │ ✅ Under 5%
│ Memory growth    │ 3MB/min │ 0.4MB/min│ ✅ Under 1MB/min
│ LCP              │ 3.2s    │ 2.1s     │ ✅ Under 2.5s
│ Visual quality   │ Premium │ Premium  │ ✅ Preserved
└─────────────────────────────────────────┘
```

## Integration with Gas Debugger

This skill extends gas-debugger's performance category (P-category bugs). When used together:
1. Gas debugger handles bug detection (security, logic, quality)
2. This skill handles performance optimization with context awareness
3. Both share the YAML manifest system for tracking
4. This skill adds `context` and `tier` fields to bug entries

## References

Load these as needed based on the detected project type:

- `references/context-detection.md` — Project type detection, skill fingerprinting, adaptive budgets
- `references/adaptive-budgets.md` — Complete budget matrix by project type × device tier
- `references/animation-performance.md` — GSAP, Framer Motion, CSS, Lenis, Web Animations API
- `references/threejs-webgl-performance.md` — Three.js r170+, WebGPU, GPU profiling, quality tiers
- `references/react-performance.md` — React 19+, Server Components, concurrent features
- `references/core-web-vitals.md` — INP, LCP, CLS 2025-2026 techniques
- `references/memory-management.md` — Leak detection, resource lifecycle, object pooling
- `references/mobile-optimization.md` — Device tiers, adaptive quality, touch, network
- `references/runtime-profiling.md` — LoAF, Performance Observer, DevTools snippets, Lighthouse CI
- `references/performance-patterns.md` — All fix patterns with context-aware detection
- `references/skill-awareness.md` — Patterns from other skills to respect (3D, UI/UX, etc.)
- `references/research-sources.md` — Academic and industry sources (2025-2026)
