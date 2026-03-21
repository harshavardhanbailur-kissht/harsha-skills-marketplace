---
name: ultimate-debugger
description: "Unified debugging, performance optimization, and code quality system. Builds on gas-debugger (persistent bug tracking, YAML manifests) and performance-debugger v2 (context-aware, tiered fixes, skill awareness). Adds safe fixing methodology that NEVER introduces new bugs, systematic root cause analysis, cross-framework bug patterns (React 19+, Next.js 15+, Three.js, GSAP, TypeScript), code quality improvement during debugging, and measurement-backed verification. Use when debugging code, fixing bugs, optimizing performance, or improving code quality."
---

# Ultimate Debugger

**Mission: Fix every bug. Break nothing. Leave the code better than you found it.**

## Foundational Principles

1. Measure before touching code
2. Understand root causes before fixing
3. Address one bug at a time
4. Only implement safe fixes
5. Improve while fixing (Boy Scout Rule)
6. Maintain context awareness across skills

## Architecture

Inherits from:
- **gas-debugger**: YAML manifests, session management, persistent bug tracking
- **performance-debugger v2**: Context detection, adaptive budgets, tiered fixes

Adds:
- Safe fixing methodology
- Cross-framework bug patterns
- Code quality improvement during debugging
- Measurement-backed verification

## Debugging Pipeline (5 Phases)

### Phase 1: Context & Triage

Detect project type, framework versions, and classify symptoms:
- Identify bug category (S/L/P/Q/F/T)
- Assess severity and impact
- Check for related known issues

### Phase 2: Reproduce & Measure

Establish baseline with profiling:
- Create minimal reproduction
- Capture metrics before any changes
- Document exact reproduction steps

### Phase 3: Root Cause Analysis

Systematic 5-step protocol:
1. **Reproduce** — Confirm the bug consistently
2. **Isolate** — Narrow to smallest code surface
3. **Hypothesize** — Form testable theories
4. **Test** — Validate each hypothesis
5. **Verify** — Confirm root vs symptom

### Phase 4: Fix Design & Implementation

Minimal, verified changes:
- Design the smallest possible fix
- Run through 8-level verification hierarchy
- Score fix quality across 5 dimensions

### Phase 5: Improvement & Commit

Code quality enhancement (Boy Scout Rule):
- Safe improvements only (extract constants, add JSDoc, etc.)
- Prohibited: large refactoring, dependency upgrades during bug fixes
- Final verification pass

## 8-Level Verification Hierarchy

Every fix must pass ALL levels:

| Level | Check | Tool |
|-------|-------|------|
| 1 | Syntax validation | Parser |
| 2 | TypeScript compilation | `tsc --noEmit` |
| 3 | Linting compliance | ESLint/Biome |
| 4 | Existing tests pass | Test runner |
| 5 | Regression tests | New test for bug |
| 6 | Performance metrics | Profiler comparison |
| 7 | Visual verification | UI screenshot (if applicable) |
| 8 | Security assessment | OWASP check |

## Bug Categories

**From gas-debugger:**
- **S** — Security vulnerabilities
- **L** — Logic errors
- **P** — Performance issues
- **Q** — Quality/maintainability

**From performance-debugger v2:**
- **P1-P7** — Performance severity tiers

**New categories:**
- **F** — Framework-specific bugs
- **T** — Type safety issues

## Fix Quality Scoring

| Dimension | Score Range | Target |
|-----------|-----------|--------|
| Minimalism | 1-5 | Smallest possible change |
| Safety | 1-5 | Zero new bugs introduced |
| Cleanliness | 1-5 | Code left better than found |
| Testing | 1-5 | Regression test added |
| Root Cause | 1-5 | True root cause addressed |

**Target: 20+ out of 25**

## Framework Coverage

- **React 19+** — Server components, use() hook, concurrent features
- **Next.js 15+** — App router, server actions, caching
- **Three.js** — Memory leaks, disposal, render loops
- **GSAP** — Animation conflicts, cleanup, ScrollTrigger
- **TypeScript** — Type narrowing, generics, declaration files

## Safe Improvements (Allowed During Bug Fixes)

- Extract magic numbers to named constants
- Add JSDoc comments
- Improve variable names for clarity
- Add missing type annotations
- Extract repeated logic to helper functions

## Prohibited During Bug Fixes

- Large-scale refactoring
- Dependency upgrades
- Architecture changes
- Feature additions
- Style/formatting-only changes

## Reference Files

| Reference | Purpose |
|-----------|---------|
| `references/debugging-methodology.md` | Systematic debugging approaches |
| `references/fix-safety.md` | Safe fix implementation protocols |
| `references/code-quality.md` | Code quality standards and patterns |
| `references/framework-bugs.md` | Framework-specific bug patterns |
| `references/testing-strategy.md` | Testing approaches for bug fixes |
| `references/production-integration.md` | Production deployment guidance |
| `references/format-specs.md` | Output format specifications |

## Integration Points

- **3D Graphics Mastery** — Three.js debugging patterns
- **UI/UX Mastery** — Visual regression verification
- **Workflow Guardian** — Safe change verification
- **Deep Thinker** — Complex bug root cause analysis

---

*Ultimate Debugger — Unified debugging and code quality system*
