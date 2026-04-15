# Skill Awareness Guide for Performance Debugger

CRITICAL: This file prevents the performance debugger from flagging intentional patterns as performance issues. Always check this guide before recommending optimizations.

---

## 1. 3D Web Graphics Mastery — Pattern Map

### NEVER FLAG (Intentional Patterns)

| Pattern | Why Intentional | Safe Alternative |
|---------|-----------------|------------------|
| MeshPhysicalMaterial | Premium visual quality (transmission, clearcoat) | Reduce only if measured GPU bottleneck: try MeshStandard on mobile-low tier only |
| Post-processing (10 effects) | Merged via EffectComposer into 1-2 GPU passes | Reduce resolution of individual effects (half-res bloom) |
| Studio lighting (3-6 lights) | Cinematic lighting setup (key + fill + rim) | Bake static lights into lightmap |
| HDR environment maps | Required for realistic reflections | Reduce resolution (1024→512) |
| 2x pixel ratio desktop | Retina display quality | Cap at 1.5 only if GPU-bound |
| GSAP proxy pattern | REQUIRED for Three.js animation correctness | No alternative - this IS the correct pattern |
| lagSmoothing(0) | Prevents GSAP stutter with Lenis | No alternative - this IS required |
| Delta time capping 1/30 | Prevents animation jumps after tab switch | No alternative - this IS required |
| GPGPU particles (65k+) | GPU-computed, not JS overhead | Reduce count only on mobile-low |
| Raymarching 100 steps | Required for SDF rendering | Reduce steps only on mobile-low |
| Bloom intensity 1.0-2.0 | Cinematic glow effect | Reduce intensity only if measured issue |
| FogExp2 density 0.02-0.05 | Atmospheric depth | Never flag |
| IcosahedronGeometry detail:4 | Hero object quality | Use LOD system (already should exist) |
| Contact shadows + shadow maps | Different purposes (ground vs directional) | Never flag as "rendering twice" |

### ALWAYS FLAG (Genuine Issues)

| Pattern | Why It's a Problem | Fix |
|---------|-------------------|-----|
| new Vector3() in render loop | GC pressure every frame | Pre-allocate outside loop |
| Missing .dispose() calls | GPU memory leak | Add disposal in cleanup |
| No Page Visibility check | Wasted GPU when tab hidden | Pause render on hidden |
| No quality tier system | Same quality on all devices | Add detect-gpu + tiers |
| Direct gsap.to(mesh.position) | Incorrect Three.js animation | Use proxy pattern |
| Missing delta time capping | Animation teleportation | Add Math.min(delta, 1/30) |

---

## 2. UI/UX Mastery — Pattern Map

### NEVER FLAG

| Pattern | Why Intentional | Safe Alternative |
|---------|-----------------|------------------|
| --duration-fast: 200ms | Design system timing | Never override |
| --duration-normal: 300ms | Standard transitions | Never override |
| --ease-out: cubic-bezier(0,0,0.2,1) | Researched easing | Never override |
| prefers-reduced-motion | Accessibility compliance | REQUIRED - flag if MISSING |
| Skeleton screens | Perceived performance (20-30% faster) | Never remove |
| 44x44px touch targets | WCAG accessibility | REQUIRED minimum |
| Disney animation principles | UX best practice | Never simplify for perf |

### ALWAYS FLAG

| Pattern | Why It's a Problem | Fix |
|---------|-------------------|-----|
| Animation >700ms for simple actions | Exceeds UX timing guidance | Reduce to 200-300ms |
| Missing prefers-reduced-motion | Accessibility violation | Add media query |
| Auto-playing indefinite animations | Banner blindness + battery | Add pause/end state |

---

## 3. Pattern Conflict Resolution

When performance debugger recommendation conflicts with a skill pattern, apply this priority order:

1. **Safety/Accessibility (NON-NEGOTIABLE)**: prefers-reduced-motion, WCAG, keyboard navigation
2. **Measured performance issue**: If actually causing dropped frames, suggest MODERATE fix
3. **Intentional pattern within budget**: SKIP, log as intentional
4. **Intentional pattern exceeding budget**: Suggest MODERATE alternative, NOT removal
5. **Unknown pattern**: Flag with LOW confidence, suggest measurement first

### Conflict Resolution Template

```
DETECTED: MeshPhysicalMaterial on 15 objects
CONTEXT: 3d-web-graphics-mastery pattern (premium material)
STATUS: intentional-within-budget
MEASURED IMPACT: +2.1ms GPU per frame (within 3D GPU allowance)

SAFE ALTERNATIVE: None needed (within budget)
MODERATE ALTERNATIVE: Use MeshStandard for non-hero objects (saves ~0.8ms)
AGGRESSIVE ALTERNATIVE: Use MeshStandard for all (saves ~2.1ms, loses quality)

RECOMMENDATION: No action needed. Intentional and within budget.
```

---

## 4. How to Detect Skill Usage

Identify skill patterns through COMBINATION analysis, not single signals:

### 3D Web Graphics Mastery
Check for 3+ of these signals:
- Three.js + Babylon.js usage
- GSAP proxy pattern for animations
- EffectComposer for post-processing
- detect-gpu quality tier system
- Custom shaders or GPGPU techniques

### UI/UX Mastery
Check for 2+ of these signals:
- CSS custom properties for timing (--duration-*, --ease-*)
- prefers-reduced-motion media query
- Consistent component timing (200ms/300ms pattern)
- Skeleton screens or perceived performance patterns
- Accessibility-first implementation (44px targets)

### No Skill Patterns Detected
Apply standard performance rules without modification.

---

## Priority Rules

- **NEVER remove intentional patterns** — optimize around them instead
- **ALWAYS verify with measurement** — perceived performance vs actual performance differ
- **ALWAYS respect accessibility** — it's non-negotiable
- **ALWAYS preserve user intent** — designers choose these patterns deliberately
