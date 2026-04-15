# Performance Debugger Skill: Comprehensive Pros/Cons Analysis

## Date: 2026-02-06
## Purpose: Foundation for v2 redesign

---

## PROS (What Works Well - Keep in v2)

### P1: Persistent Bug Tracking via YAML Manifests
The YAML-based manifest system prevents context drift across long sessions. Bug state lives in files, not LLM memory. This is architecturally sound and should be preserved in v2.

### P2: Token Optimization (50-70% Reduction)
Structured manifests and phased scanning reduce redundant context. The strip-comments, send-only-relevant-functions, batch-similar-files approach is effective.

### P3: Category-Based Scanning
Separating security, logic, performance, and quality into distinct scan phases allows targeted analysis. Each category has specialized prompts.

### P4: Ignore Rules System
Pattern-based false positive filtering with expiration dates, JIRA tickets, and category restrictions. Prevents recurring false flags.

### P5: Verification Loop
Status tracking (pending → fixing → fixed → verified) ensures fixes are actually validated, not just applied.

### P6: Comprehensive Reference Documentation
The reference docs for React, Three.js, Core Web Vitals, memory, and mobile are detailed and well-researched.

### P7: Fix Patterns with Confidence Scores
Template-based fixes with 0.7-0.95 confidence scores help prioritize which fixes to apply first.

### P8: Report Generation
Multiple output formats (summary, detailed, JSON, markdown) serve different stakeholders.

### P9: Session Management
Init script creates proper directory structure with unique session IDs and timestamps.

---

## CONS (What's Broken - Fix in v2)

### CRITICAL FAILURES

#### C1: 60fps Checklist Is Actively Destructive
**Impact: HIGH** — User reports it "made my website worse than before."
The checklist applies blanket optimizations without understanding:
- Which patterns are intentional (MeshPhysicalMaterial, post-processing, GSAP proxy)
- Quality tiers (mobile 30fps is acceptable, desktop ultra allows expensive effects)
- The difference between "expensive by design" and "expensive by accident"
**Root cause:** No context awareness. It treats all code as if it should be minimal.

#### C2: Regex-Only Static Analysis Misses Context
**Impact: HIGH** — False positives everywhere.
Pattern matching cannot understand:
- Scope (is this `will-change` properly managed with cleanup?)
- Lifecycle (is this expensive operation in init or in render loop?)
- AST context (is this inside a `useMemo` already?)
- Intent (is this `MeshPhysicalMaterial` a deliberate premium choice?)
**Root cause:** No AST parsing, no scope analysis, no lifecycle detection.

#### C3: No Skill Awareness / Conflict Resolution
**Impact: HIGH** — Directly conflicts with 3D web graphics skill.
15+ patterns the 3D skill explicitly teaches are flagged as problems:
1. MeshPhysicalMaterial → flagged as "use MeshStandard"
2. Post-processing stack (10 effects) → flagged as "GPU hog"
3. Multiple lights (4-6) → flagged as "excessive"
4. HDR environment maps → flagged as "unnecessary"
5. 2x pixel ratio on desktop → flagged as "wasteful"
6. Bloom intensity 1.5 → flagged as "too high"
7. IcosahedronGeometry detail:4 → flagged as "reduce detail"
8. GPGPU particles (65k+) → flagged as "too many"
9. Lenis smooth scroll lerp:0.1 → flagged as "continuous jank"
10. Delta time capping at 1/30 → flagged as "artificial limit"
11. GSAP proxy pattern → flagged as "overhead"
12. lagSmoothing(0) → flagged as "disabling safety"
13. Multiple overlapping timeline animations → flagged as "wasteful"
14. Contact shadows + shadow maps → flagged as "rendering twice"
15. Raymarching 100 steps → flagged as "too many iterations"
**Root cause:** No mechanism to detect intentional patterns from other skills.

#### C4: No Runtime Measurement
**Impact: HIGH** — All "optimization" is guesswork.
The skill suggests fixes without ever measuring:
- Actual frame times (are we actually dropping frames?)
- GPU vs CPU bottleneck (is the fix targeting the right thing?)
- Memory pressure (is this leak actually causing issues?)
- Network waterfall (what's the real loading bottleneck?)
**Root cause:** Pure static analysis with no profiling integration.

### SIGNIFICANT ISSUES

#### C5: No Quality Tier Understanding
Doesn't know about ultra/high/medium/low quality tiers. Tries to optimize everything to "low" regardless of target device capability.

#### C6: No Adaptive Performance Budgets
Single budget regardless of:
- Project type (marketing site vs. dashboard vs. 3D experience)
- Target devices (desktop ultra vs. mobile low-end)
- User's stated priorities (quality vs. performance)

#### C7: Scripts Are Python-Only
Web projects need JS/TS tooling. The Python scanner can detect patterns but can't integrate with:
- Chrome DevTools Protocol
- Lighthouse API
- Bundle analyzers (webpack-bundle-analyzer, vite-plugin-visualizer)
- Performance Observer API

#### C8: No Animation-Specific Debugging
Missing understanding of:
- GSAP timeline debugging (Timeline.getChildren(), .pause(), .progress())
- Framer Motion layout animations
- CSS animation performance (composite vs. paint vs. layout layers)
- Web Animations API
- Animation frame scheduling

#### C9: No Progressive Enhancement / Tiered Fixes
Every fix is presented as equally important. No separation between:
- **Safe fixes** (won't change visual output: code splitting, lazy loading)
- **Moderate fixes** (minor visual change: reduce shadow quality, simplify easing)
- **Aggressive fixes** (visible quality reduction: remove post-processing, lower geometry)

#### C10: No Measurement Verification
Fix verification checks syntax only. Doesn't verify:
- Frame rate actually improved
- Memory usage actually decreased
- Core Web Vitals actually got better
- Visual quality wasn't destroyed

### MINOR ISSUES

#### C11: No Bundle Analysis Integration
Mentions bundle size but doesn't provide actual analysis scripts or integration guidance.

#### C12: No CI/CD Performance Regression
Mentions Lighthouse CI but doesn't provide working configs or automation scripts.

#### C13: Research Sources Need Updating
Current sources are from 2024-2025. Need 2025-2026 updates for:
- Long Animation Frames API (replacing Long Tasks)
- Scheduler.yield()
- View Transitions API performance
- React 19+ performance patterns
- WebGPU performance characteristics

#### C14: No WebGL/GPU Profiling Guidance
Missing integration with:
- Spector.js for WebGL debugging
- WebGPU profiling APIs
- GPU memory monitoring
- Shader compilation timing

---

## FAILURE MODE ANALYSIS

### Failure Mode 1: "The Blanket Optimizer"
**Trigger:** User runs performance scan on a 3D web experience
**What happens:** Skill flags MeshPhysicalMaterial, post-processing, particles, multiple lights, GSAP animations
**Result:** User applies all fixes → Premium 3D experience becomes flat, lifeless, amateur-looking
**Why:** No context awareness, no quality tier detection, no skill pattern recognition

### Failure Mode 2: "The False Alarm"
**Trigger:** User runs performance scan on a well-optimized React app
**What happens:** Regex patterns match `will-change`, `requestAnimationFrame`, inline objects in JSX
**Result:** User "fixes" things that were already properly managed
**Why:** Regex can't see scope, lifecycle, or surrounding context (e.g., will-change with cleanup)

### Failure Mode 3: "The Wrong Target"
**Trigger:** User has a slow website and runs performance scan
**What happens:** Skill finds 20+ "issues" but the actual bottleneck is a 2MB unoptimized hero image
**Result:** User spends hours fixing minor JS patterns while the real problem persists
**Why:** No runtime profiling to identify actual bottlenecks, no prioritization by measured impact

### Failure Mode 4: "The Device-Blind Fix"
**Trigger:** User targets mobile performance
**What happens:** Skill suggests same fixes as desktop, doesn't understand quality tiers
**Result:** Mobile gets no special treatment, or desktop gets unnecessarily degraded
**Why:** No device tier detection, no adaptive budgets

### Failure Mode 5: "The Unverified Improvement"
**Trigger:** User applies suggested fixes
**What happens:** Syntax verification passes, but actual performance is worse (e.g., removing will-change causes layout recalculation)
**Result:** User believes they optimized when they actually regressed
**Why:** No measurement-based verification, only syntax checking
