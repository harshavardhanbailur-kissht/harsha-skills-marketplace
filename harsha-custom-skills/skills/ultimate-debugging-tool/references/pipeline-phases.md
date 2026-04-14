# Debugging Pipeline — Detailed Phase Descriptions

**Purpose:** Complete reference for each phase in the debugging pipeline (Phase 0 through Phase 5).

**Relevant Skills:** Ultimate Debugger (self-contained with integrated debugging and performance analysis)

---

## Phase 0: Context & Triage

**Includes built-in capabilities:**
- Project type detection (3D, animation, React SPA, dashboard, hybrid)
- Skill pattern detection (3D Graphics Mastery, UI/UX Mastery)
- Adaptive budgets

**Add triage classification:**

| Symptom | Classification | Primary Skill |
|---------|---------------|---------------|
| App crashes / throws error | BUG → this skill | Fix the error |
| App is slow / janky | PERFORMANCE → this skill | Measure + optimize |
| App works but code is messy | QUALITY → this skill | Refactor safely |
| App has security vulnerability | SECURITY BUG → this skill | Fix + verify |
| App has visual glitch | BUG → this skill | Reproduce + fix |
| App leaks memory | BUG + PERFORMANCE → this skill | Fix leak + verify |

### Phase 0 Checklist

- [ ] Run `python scripts/context_analyzer.py <project-path>` to detect project type and frameworks
- [ ] Classify symptom into one of the six categories above
- [ ] Identify which reference files are relevant (use Quick Triage table)
- [ ] Gather context: recent changes (git log), previous similar bugs, environment details

---

## Phase 2: Root Cause Analysis

See `references/debugging-methodology.md` for the full systematic approach and detailed examples.

### The 5-Step Root Cause Protocol

1. **Reproduce**: Can you make the bug happen consistently? If not, look for race conditions, timing issues, or environment-specific triggers.

2. **Isolate**: Narrow down to the smallest code path. Comment out code, use binary search (bisect commits), reduce to minimal reproduction.

3. **Hypothesize**: "I think the bug is caused by [specific mechanism]." Be specific: "The stale closure in useEffect captures the old state value because handleClick is not in the deps array."

4. **Test**: Add a console.log, breakpoint, or assertion that would PROVE your hypothesis. If it doesn't prove it, your hypothesis is wrong.

5. **Verify Root vs Symptom**: Ask "If I fix this, will the bug NEVER return?" If the answer is "maybe," you're fixing a symptom, not the root cause.

### Common Root Cause Patterns

| Symptom | Common Root Cause | Trap (Don't Fix This Way) |
|---------|------------------|--------------------------|
| Null reference error | Missing null check upstream | Adding `?.` everywhere (masks the real issue) |
| Stale data displayed | Stale closure or missing dependency | Adding all deps (may cause infinite loop) |
| Memory growing | Missing cleanup in useEffect | Adding cleanup without understanding what leaks |
| Intermittent crash | Race condition in async code | Adding try/catch (hides the race condition) |
| Wrong data rendered | State update in wrong lifecycle | Moving setState call (may break other behavior) |
| Animation glitch | Missing delta time or cleanup | Reducing animation complexity (destroys intent) |

### Tools & Techniques for Phase 2

**Breakpoint Debugging:**
- Set breakpoint at suspected location
- Inspect local variables and call stack
- Step through execution line-by-line
- Watch expressions to track state changes

**Logging & Instrumentation:**
- Add console.log to trace data flow
- Use timestamps to detect timing issues
- Log before/after state changes
- Remove logs once root cause found

**Binary Search (for non-reproducible bugs):**
- Use `git bisect` to find the commit that introduced the bug
- Narrow suspect code to narrower and narrower ranges
- Test hypothesis at each bisect step

**Minimal Reproduction:**
- Strip to absolute minimum code that triggers the bug
- Remove all "noise" (styling, unrelated features)
- Test in isolation from the rest of the codebase
- Share minimal repro with team for faster debugging

---

## Phase 3: Fix Design — The Fix Safety System

See `references/fix-safety.md` for the complete verification system and safe fix templates.

### The 8-Level Verification Hierarchy

Every fix MUST pass levels 1-4. Levels 5-8 are recommended for high-severity bugs.

```
Level 1: SYNTAX ─── Does it parse? (AST validity)
    ↓
Level 2: TYPES ──── Does TypeScript compile? (No new type errors)
    ↓
Level 3: LINT ───── Does it pass linting? (No new warnings)
    ↓
Level 4: TESTS ──── Do existing tests pass? (No regressions)
    ↓
Level 5: REGRESSION ── Does the new test for THIS bug pass?
    ↓
Level 6: PERFORMANCE ─ No frame time / memory / bundle regression?
    ↓
Level 7: VISUAL ───── Screenshot diff OK? (For UI changes)
    ↓
Level 8: SECURITY ─── No new vulnerabilities introduced?
```

### Fix Quality Scoring

Rate every fix on these dimensions:

| Dimension | Score | Meaning |
|-----------|-------|---------|
| **Minimal** | 1-5 | 5 = smallest possible change; 1 = rewrote half the file |
| **Safe** | 1-5 | 5 = zero risk of side effects; 1 = changes public API |
| **Clean** | 1-5 | 5 = improves readability; 1 = "slop" code |
| **Tested** | 1-5 | 5 = regression test included; 1 = no test |
| **Root Cause** | 1-5 | 5 = fixes root cause; 1 = patches symptom |

**Target: 20+ total (all 4s or better). Below 15 = reject the fix and try again.**

### Fix Templates (Safe Patterns That Don't Break Things)

See `references/fix-safety.md` for complete templates. Quick reference:

| Bug Type | Safe Fix Pattern | NEVER Do This |
|----------|-----------------|---------------|
| Null access | Optional chaining + fallback value | `!` (non-null assertion) |
| Missing cleanup | useEffect return + AbortController | Cleanup without testing it works |
| Stale closure | useRef for latest value, or add to deps | Add all deps blindly |
| Memory leak | Dispose all resources in cleanup | Just null the references |
| Race condition | AbortController + ignore stale response | try/catch (hides the race) |
| XSS | DOMPurify.sanitize() | innerHTML = '' (might miss cases) |
| Infinite loop | Guard condition + max iterations | Just add a break statement |
| Type error | Proper type narrowing + discriminated union | Cast with `as` |

### Phase 3 Deliverables

Before moving to Phase 4, prepare:

1. **Minimal fix code** — smallest possible change to address root cause
2. **Regression test** — test that would FAIL before the fix, PASS after
3. **Quality score** — 20+ points across all five dimensions
4. **Impact assessment** — which files/functions are affected

---

## Phase 4: Adaptive Verification (AVP)

### Core Principle

**Classify the fix, not the bug.** Bug descriptions are unreliable predictors of complexity. Fix characteristics — diff size, files touched, AST change nature, type surface area, dependency fan-out — are measurable and objective.

### Fix Signal Analyzer

Run the analyzer on the designed fix diff:

```bash
# From a diff file
python scripts/fix_signal_analyzer.py --diff fix.diff --project-type react-spa --severity medium

# From stdin (e.g., git diff output)
git diff HEAD~1 | python scripts/fix_signal_analyzer.py --stdin --severity high --format json

# With project path for dependency analysis
python scripts/fix_signal_analyzer.py --diff fix.diff --project-path /path/to/project
```

The analyzer measures six signals:

| Signal | What It Measures | Low (0.0-0.2) | High (0.8-1.0) |
|--------|------------------|----------------|-----------------|
| `diff_size` | Lines changed (relative churn) | <5 lines | >50 lines |
| `files_touched` | Count of modified files | 1 file | 4+ files |
| `ast_depth` | Nature of AST change | Leaf (value change) | Structural (signature, control flow) |
| `type_surface` | Type system impact | No new types | New interfaces, changed public types |
| `test_surface` | Test coverage breadth | <3 tests affected | >10 tests, cross-module |
| `dependency_fan` | Downstream caller impact | 0 callers affected | 5+ callers, public API changed |

Signals are combined into a composite `verification_depth` score (0.0 → 1.0) using research-backed weighted aggregation with a veto layer to prevent high-risk signals from being averaged away by low-risk ones.

### Three Independent Safety Nets

These are non-negotiable design constraints:

1. **Mandatory Floor**: L1-L4 always execute for every fix. There is no path that bypasses syntax, type, lint, or test verification. A 1-line typo fix still gets all four.

2. **Auto-Escalation**: If L1-L4 results reveal unexpected complexity (type errors cascading beyond changed files, distant test failures, lint chain reactions, coverage drops), the pipeline automatically promotes to full L1-L8 depth.

3. **Severity Ratchet**: Critical severity → always full L1-L8. High severity → always minimum L1-L6. These overrides apply regardless of the signal analyzer's score.

For a catastrophic miss, all three safety nets must fail simultaneously.

### Depth Decision Levels

| Verification Depth | Levels Beyond L4 | Category |
|--------------------|--------------------|----------|
| 0.00 - 0.25 | L5 only (regression test) | Minimal |
| 0.25 - 0.50 | L5 + L6 (+ performance) | Moderate |
| 0.50 - 0.75 | L5 + L6 + L7 (+ visual) | High |
| 0.75 - 1.00 | L5 + L6 + L7 + L8 (full) | Full |

### Auto-Escalation Triggers

After L1-L4 complete, monitor for these signals:

| Trigger | Detection | Implication |
|---------|-----------|-------------|
| Type cascade | `tsc` errors in files NOT in the fix diff | Hidden type-level dependencies |
| Distant test failure | Test fails in a module with no imports from changed files | Shared state or integration coupling |
| Lint chain reaction | New warnings in unmodified files | Export changes affecting dependents |
| Coverage drop | Overall coverage decreased in unmodified files | Fix added uncovered paths |

Any trigger detected → auto-promote to full L1-L8 verification.

### Learning Loop

Escalation events are logged to `.ultimate-debugger/avp-learning-log.yaml`. Over time, this data tunes signal weights to improve prediction accuracy. See `references/avp-learning.md` for the full schema and weight adjustment strategy.

---

## Phase 5: Improve While Fixing (Boy Scout Rule)

See `references/code-quality.md` for the full approach.

### Safe Improvements During Debugging (Separate Commit)

These are SAFE to do alongside a bug fix (in a separate commit):

| Improvement | Risk | Time | When |
|-------------|------|------|------|
| Extract magic number → named constant | None | 1 min | Always |
| Add JSDoc to function you just debugged | None | 2 min | Always |
| Add missing TypeScript types | Low | 5 min | When touching the file |
| Extract helper function from long function | Low | 5 min | If function >50 lines |
| Add missing error handling | Low | 3 min | When you find a bare catch |
| Remove dead code you confirmed is unused | Low | 2 min | When you verified it during debugging |
| Add TODO with ticket ref for known limitation | None | 1 min | Always |

### NEVER Do These During a Bug Fix

| Improvement | Why Not | When Instead |
|-------------|---------|-------------|
| Large refactoring | High regression risk | Separate PR |
| Dependency upgrade | May introduce new bugs | Separate PR |
| Architecture change | Too many side effects | Planning session |
| Style/formatting changes | Pollutes git blame | Automated formatter PR |
| Adding new features | Scope creep | Separate ticket |

### Phase 5 Deliverables

1. **Commit 1:** Bug fix (minimal, isolated)
2. **Commit 2 (optional):** Code quality improvements (separate, atomic)
3. **Updated bug manifest:** Status = `verified`, root cause + fix documented
4. **Lesson learned:** What pattern could prevent this bug in the future?
5. **Similarity audit:** Are there other instances of this pattern in the codebase?

---

## Bug Categories (Extended)

### Debugging categories (built-in):
- **S: Security** — Injection, XSS, CSRF, auth bypass, secrets exposure
- **L: Logic** — Null refs, off-by-one, race conditions, wrong conditions
- **P: Performance** — N+1 queries, memory leaks, expensive loops, jank
- **Q: Quality** — Dead code, magic numbers, deep nesting, missing types
- **P1-P7**: Animation, JavaScript, React, Three.js, Memory, CWV, Mobile

### New in ultimate-debugger:
- **F: Framework** — React hooks violations, Next.js SSR bugs, Three.js resource bugs, GSAP cleanup
- **T: Type Safety** — TypeScript `any` usage, missing null checks, incorrect narrowing
- **R: Regression** — Bugs that were fixed before and returned

---

## Framework-Specific Patterns

See the framework-specific reference files for detailed patterns with safe fixes:

- **React 19+**: See `references/react-bugs.md` for stale closures, hydration mismatches, Server/Client boundary errors, useEffect race conditions
- **Next.js 15+**: See `references/nextjs-bugs.md` for cache invalidation, Server Action errors, middleware bypass (CVE-2025-29927)
- **Three.js**: See `references/threejs-bugs.md` for resource disposal, render loop stopping, object creation in animate loop
- **GSAP**: See `references/gsap-bugs.md` for context reversion, ScrollTrigger refresh, Lenis desync
- **TypeScript**: See `references/typescript-bugs.md` for `any` masking, type narrowing, strict mode
