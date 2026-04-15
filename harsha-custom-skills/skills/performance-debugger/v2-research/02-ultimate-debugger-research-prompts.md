# Ultimate Debugger Research Prompts
# Target Model: Claude Opus 4.6 with Extended Thinking
# Date: 2026-02-06
# Foundation: Builds ON TOP of performance-debugger v2 (context-aware, tiered fixes, skill awareness)

---

## RESEARCH PROMPT 1: LLM-Assisted Bug Detection — Academic & Industry State of the Art (2024-2026)

You are a senior research engineer surveying the latest academic papers and industry tools for LLM-based bug detection and automated program repair. Focus on techniques that COMPLEMENT static analysis (not replace it) and that prevent introducing new bugs during fixes.

**Research the following from top-tier sources (ICSE, FSE, ASE, ISSTA, Google Research, Microsoft Research, Meta, academic arxiv):**

1. **LLM-Based Bug Detection Advances**:
   - LLMxCPG (2024): Code Property Graph + LLM for 67-91% context reduction — how does it work, what's the detection accuracy, how to integrate
   - RepairAgent (2024): Autonomous LLM agent that fixed 164 real bugs — architecture, tool use pattern, success/failure modes
   - ChatRepair (2024): $0.42 per bug fix — cost-efficiency techniques, prompt engineering for repair
   - SWE-bench results: What do top-performing agents (Devin, SWE-Agent, OpenHands, Agentless) do differently for bug detection vs. fix generation?
   - UniDebugger: Multi-language debugging with unified approach
   - Aider's approach to automated coding + testing loops
   - How GitHub Copilot Workspace handles bug detection and fix suggestion

2. **Semantic Analysis Beyond Regex**:
   - Tree-sitter for AST parsing in multiple languages (JS, TS, Python, Go, Rust)
   - Code Property Graphs (CPG) — Joern, CodeQL for vulnerability detection
   - Dataflow analysis for taint tracking (following user input through code)
   - Control flow analysis for detecting unreachable code, infinite loops
   - Type inference for detecting type confusion bugs in JavaScript/TypeScript
   - Call graph analysis for finding unused functions and dead code

3. **Bug Classification Taxonomies**:
   - CWE (Common Weakness Enumeration) top 25 for 2025
   - OWASP Top 10 for 2025
   - Google's bug taxonomy for JavaScript/TypeScript
   - React-specific bug patterns (hooks rules violations, stale closures, race conditions in effects)
   - Three.js-specific bugs (resource leaks, render loop mistakes, shader compilation failures)
   - Animation bugs (timing conflicts, cleanup failures, memory leaks from GSAP/Framer Motion)

4. **Fix Quality Assessment**:
   - How to verify a fix actually resolves the bug (not just passes syntax check)
   - How to detect when a fix introduces a NEW bug (regression detection)
   - Mutation testing for fix verification (PIT, Stryker)
   - Metamorphic testing for behavioral verification
   - Differential testing (compare behavior before/after fix)
   - Property-based testing (QuickCheck-style) for invariant verification

5. **Multi-File Bug Detection**:
   - Cross-module dependency analysis
   - API contract violation detection
   - Import/export consistency checking
   - Configuration drift detection (env vars, config files)
   - Database schema vs. code model mismatches

**Output format:** For each technique/paper, provide: core insight (1-2 sentences), detection accuracy (if reported), integration approach (how to use in a Claude skill), and limitations.

---

## RESEARCH PROMPT 2: Safe Code Fixing — Never Introduce New Bugs

You are a senior software reliability engineer specializing in safe automated program repair. Research techniques that ensure bug fixes don't break existing functionality or introduce new problems.

**Research the following:**

1. **Fix Safety Principles**:
   - Minimal change principle: why smaller diffs are safer (academic evidence)
   - One-bug-at-a-time discipline: preventing cascading fix failures
   - Behavioral preservation: ensuring fix only changes the buggy behavior
   - Regression test generation: creating tests that catch if the fix breaks something
   - Pre-fix snapshot: storing original code for rollback
   - Fix isolation: sandboxing changes to prevent side effects

2. **Automated Regression Detection**:
   - Differential testing before/after fix
   - Snapshot testing for UI components (React Testing Library, Playwright)
   - Contract testing for API endpoints
   - Property-based testing for invariant preservation
   - Type checking as regression gate (TypeScript strict mode)
   - ESLint/Biome as quality gate (ensure fix passes all linting rules)

3. **Fix Verification Hierarchy** (what to check, in what order):
   Level 1: Syntax validity (AST parses cleanly)
   Level 2: Type correctness (TypeScript compiles, no new type errors)
   Level 3: Lint compliance (no new warnings/errors)
   Level 4: Unit tests pass (all existing tests still green)
   Level 5: Integration tests pass (cross-module behavior unchanged)
   Level 6: Performance verification (no regression in frame time, bundle size)
   Level 7: Visual verification (screenshot diff for UI changes)
   Level 8: Security verification (no new vulnerabilities introduced)

4. **Common Fix Failure Modes**:
   - Fix removes bug but breaks related feature
   - Fix is correct but introduces performance regression
   - Fix works in isolation but conflicts with concurrent code changes
   - Fix addresses symptom but not root cause (bug returns in different form)
   - Fix introduces new dependency that bloats bundle
   - Fix changes public API signature (breaking downstream consumers)
   - Fix creates dead code or unused imports

5. **Rollback Strategies**:
   - Git-based rollback (stash, revert, cherry-pick)
   - Feature flags for gradual rollout of fixes
   - Canary deployments for production fixes
   - A/B testing fixes in production
   - Automated rollback on metric regression

6. **Fix Templates That Don't Break Things**:
   For each common bug type, provide a SAFE fix template:
   - Null/undefined access → optional chaining with fallback
   - Missing error handling → try/catch with proper error propagation
   - Memory leak → cleanup in useEffect return / AbortController
   - Race condition → AbortController / stale closure prevention
   - XSS vulnerability → DOMPurify sanitization
   - SQL injection → parameterized queries
   - Infinite loop → loop guard with max iterations
   - Stale closure → useRef for latest value pattern

**Output format:** For each technique, provide: why it prevents new bugs, implementation approach, cost (time/complexity), and when to skip it.

---

## RESEARCH PROMPT 3: Code Quality Improvement During Debugging

You are a senior software craftsman who believes debugging is an opportunity to improve code quality, not just fix the immediate bug. Research techniques for opportunistic refactoring during bug fixes.

**Research the following:**

1. **Boy Scout Rule Applied to Debugging**:
   - "Leave the code better than you found it" — how to scope improvements
   - When to refactor during a bug fix vs. when to defer
   - How to separate fix commits from improvement commits (clean git history)
   - Risk assessment: which improvements are safe during debugging, which aren't

2. **Code Smell Detection (Automated)**:
   - Cyclomatic complexity thresholds (>10 = warning, >20 = refactor)
   - Cognitive complexity (SonarQube metric) — better than cyclomatic for readability
   - Duplicate code detection (jscpd, PMD CPD)
   - Long function detection (>50 lines = warning, >100 = refactor)
   - Deep nesting detection (>3 levels = warning, >5 = refactor)
   - God class/module detection (>300 lines, >20 methods)
   - Magic number detection (hardcoded values without named constants)
   - Dead code detection (unused exports, unreachable branches)
   - Inconsistent naming conventions
   - Missing TypeScript types (any usage, implicit any)

3. **Safe Refactoring Patterns**:
   - Extract function (reduce complexity without changing behavior)
   - Extract constant (eliminate magic numbers)
   - Introduce parameter object (reduce function parameter count)
   - Replace conditional with polymorphism
   - Extract component (React: break up large components)
   - Move related code closer (cohesion improvement)
   - Simplify boolean expressions (De Morgan's law, early returns)
   - Replace nested conditionals with guard clauses

4. **Code Quality Metrics That Matter**:
   - Maintainability Index (Visual Studio metric)
   - Technical Debt Ratio (SonarQube)
   - Test coverage (line, branch, statement)
   - Bundle impact (how much does this module contribute to bundle size?)
   - Import depth (how deep in the dependency tree?)
   - Change frequency (files that change often need more care)

5. **Documentation Improvements During Debugging**:
   - Adding JSDoc/TSDoc for functions touched during debugging
   - Adding inline comments explaining WHY (not what) for complex logic
   - Adding TODO with ticket references for known limitations
   - Updating README when debugging reveals incorrect documentation
   - Adding type annotations where missing

6. **Testing Improvements During Debugging**:
   - Writing regression tests for the bug being fixed
   - Adding edge case tests discovered during debugging
   - Converting manual test steps to automated tests
   - Adding performance assertions (frame time, memory limits)
   - Adding accessibility assertions (axe-core integration)

**Output format:** For each technique, provide: when to apply (during debugging vs. separate PR), risk level (safe/moderate/risky), time cost, and code example.

---

## RESEARCH PROMPT 4: Cross-Framework Bug Patterns (React, Next.js, Three.js, GSAP, 2025-2026)

You are a senior full-stack developer who debugs across multiple frameworks daily. Research the most common and subtle bug patterns specific to each major framework, with fixes that don't introduce new issues.

**Research the following:**

1. **React 19+ Bug Patterns**:
   - Hooks rules violations (conditional hooks, hooks in loops)
   - Stale closure bugs (useEffect capturing old state)
   - Race conditions in useEffect (fetch without AbortController)
   - Infinite re-render loops (setState in useEffect without deps)
   - Context value instability (inline objects as context value)
   - Server Component vs Client Component boundary mistakes
   - Hydration mismatches (SSR vs client rendering differences)
   - React Compiler compatibility issues
   - Suspense boundary error handling gaps
   - useTransition misuse (wrapping synchronous code)

2. **Next.js 15+ Bug Patterns**:
   - App Router caching issues (stale data, cache invalidation)
   - Server Action error handling (missing try/catch, improper revalidation)
   - Dynamic route parameter type errors
   - Middleware execution order bugs
   - Image optimization misconfiguration
   - Environment variable exposure (server vs client)
   - Streaming SSR hydration edge cases

3. **Three.js Bug Patterns**:
   - Memory leaks from undisposed resources (geometry, material, texture, render target)
   - Render loop not stopping when component unmounts
   - Shader compilation failures (GLSL errors, missing uniforms)
   - Object creation in animation loop (GC pressure)
   - Camera aspect ratio not updating on resize
   - Event listener leaks on canvas
   - WebGL context loss handling
   - Z-fighting from overlapping geometries
   - Incorrect matrix updates (updateMatrixWorld not called)

4. **GSAP + Animation Bug Patterns**:
   - Timeline not killed on component unmount (memory leak)
   - ScrollTrigger not refreshed after DOM changes
   - GSAP context not reverted (gsap.context() cleanup)
   - Conflicting tweens on same property
   - lagSmoothing interaction with tab visibility
   - Lenis scroll position desync with ScrollTrigger
   - Framer Motion AnimatePresence exit animation not firing
   - CSS transition conflicting with JS animation

5. **TypeScript Bug Patterns**:
   - Incorrect type narrowing (type guards that don't actually narrow)
   - any type masking real bugs
   - Enum pitfalls (numeric enums, const enums in declaration files)
   - Generic constraint mistakes
   - Module augmentation conflicts
   - Declaration merging unexpected behavior

6. **Cross-Framework Integration Bugs**:
   - React + Three.js: useFrame cleanup, R3F reconciler vs vanilla Three.js state
   - React + GSAP: useGSAP hook cleanup, context revert
   - Next.js + Three.js: SSR issues with canvas, dynamic imports required
   - GSAP + Lenis + ScrollTrigger: initialization order matters

**Output format:** For each bug pattern, provide: symptoms (what the user sees), root cause, detection approach, safe fix, and common mistake when fixing.

---

## RESEARCH PROMPT 5: Production Debugging & Observability

You are a senior SRE/DevOps engineer building a production debugging pipeline. Research how to connect development debugging with production observability.

**Research the following:**

1. **Error Tracking Integration**:
   - Sentry setup for React/Next.js (error boundaries, source maps)
   - LogRocket for session replay and error context
   - Datadog RUM for real-user performance + errors
   - Custom error boundary patterns that capture actionable context
   - Source map security (upload to error tracker, don't expose to users)

2. **Performance Monitoring in Production**:
   - web-vitals library integration (LCP, INP, CLS, TTFB)
   - Custom performance marks for business metrics
   - Real User Monitoring (RUM) vs Synthetic Monitoring
   - Performance budgets in CI (Lighthouse CI assertions)
   - Percentile-based alerting (P75, P95 thresholds)

3. **Debugging Production Issues**:
   - How to reproduce production bugs locally
   - Feature flag systems for safe fix deployment
   - Canary releases with automatic rollback
   - Blue-green deployments for zero-downtime fixes
   - Hot module replacement in development for faster debugging

4. **Logging Best Practices**:
   - Structured logging (JSON format with context)
   - Log levels: when to use error, warn, info, debug
   - Performance impact of logging (async vs sync, batching)
   - Sensitive data redaction in logs
   - Correlation IDs for request tracing

5. **CI/CD Performance Gates**:
   - Bundle size checks in PR (bundlewatch, size-limit)
   - Lighthouse CI in GitHub Actions
   - Visual regression testing (Chromatic, Percy)
   - TypeScript strict mode as CI gate
   - ESLint/Biome performance rules

**Output format:** For each area, provide: setup instructions, what it catches, integration cost, and how it feeds back into the debugging skill.

---

## RESEARCH PROMPT 6: JavaScript/TypeScript AST-Based Bug Detection

You are a senior tooling engineer building AST-based analysis tools. Research how to use Abstract Syntax Trees for more accurate bug detection than regex patterns.

**Research the following:**

1. **Tree-sitter for Multi-Language Parsing**:
   - Tree-sitter JavaScript/TypeScript grammar
   - Incremental parsing for large files
   - Query syntax for pattern matching (S-expressions)
   - Integration with Node.js (tree-sitter npm package)
   - Performance characteristics (can it handle 1000+ files?)

2. **AST Patterns for Common Bugs**:
   - Detecting hooks called inside conditionals (React rules of hooks)
   - Detecting missing cleanup in useEffect
   - Detecting object creation inside render functions
   - Detecting stale closures (variable captured but not in deps array)
   - Detecting unused imports and dead exports
   - Detecting type-unsafe operations (property access on possibly null)

3. **ESLint Custom Rules**:
   - Writing custom ESLint rules for project-specific patterns
   - eslint-plugin-react-hooks (how it detects exhaustive deps)
   - eslint-plugin-react-perf (how it detects inline objects)
   - Performance of custom ESLint rules
   - Sharing rules across projects

4. **CodeQL for Vulnerability Detection**:
   - CodeQL JavaScript/TypeScript queries
   - Taint tracking for XSS, injection detection
   - Custom CodeQL queries for project-specific patterns
   - GitHub Advanced Security integration
   - Performance: is it practical for real-time debugging?

5. **Scope Analysis**:
   - Variable scope tracking (is this in module scope, function scope, block scope?)
   - Closure analysis (what variables are captured?)
   - Lifetime analysis (when is this object created vs destroyed?)
   - Import/export dependency graph
   - Call graph construction for dead code detection

**Output format:** For each technique, provide: accuracy improvement over regex (estimated %), implementation complexity, language support, and integration pattern.

---

## RESEARCH PROMPT 7: Debugging Mental Models & Systematic Approaches

You are a senior engineering educator teaching debugging methodology. Research the best systematic approaches to debugging that prevent "fix one bug, create two more."

**Research the following:**

1. **Scientific Debugging Method**:
   - Andreas Zeller's "Why Programs Fail" methodology
   - Hypothesis-driven debugging (form hypothesis → test → refine)
   - Delta debugging (systematically narrow down failure cause)
   - Binary search debugging (bisect the code/commits)
   - Rubber duck debugging (explain the code to find the bug)

2. **Root Cause Analysis**:
   - 5 Whys technique applied to software bugs
   - Fishbone (Ishikawa) diagram for complex bugs
   - Fault tree analysis for critical systems
   - Distinguishing symptoms from root causes
   - When the bug you see isn't the bug you have

3. **Debugging Heuristics**:
   - "What changed?" — most bugs are caused by recent changes
   - "Simplify" — reduce to minimal reproduction
   - "Check assumptions" — the bug is usually in what you assumed worked
   - "Read the error message" — it often tells you exactly what's wrong
   - "Check the boundaries" — off-by-one, null, empty, overflow
   - "Follow the data" — trace the actual values through the code

4. **Common Bug Archetypes**:
   - Off-by-one errors (loop bounds, array indexing)
   - Null/undefined access (missing null checks, optional chaining)
   - Race conditions (async operations, shared state)
   - Resource leaks (files, connections, event listeners, timers)
   - State management bugs (stale state, wrong update order)
   - Encoding/decoding errors (UTF-8, URL encoding, Base64)
   - Floating point precision (comparison, accumulation)
   - Time-related bugs (timezones, DST, leap years, date parsing)
   - Caching bugs (stale data, cache invalidation)

5. **Preventing Bug Reintroduction**:
   - Writing regression tests for every bug fixed
   - Adding invariant assertions to critical code paths
   - Code review checklists for common mistake areas
   - Pre-commit hooks for automated detection
   - Postmortem documentation (what happened, why, how to prevent)

**Output format:** For each approach, provide: when to use, step-by-step process, example application, and how to encode it into a debugging skill.

---

## RESEARCH PROMPT 8: Modern Testing Strategies for Bug Prevention

You are a senior QA engineer designing testing strategies that prevent bugs before they ship. Research modern testing approaches relevant to React/Three.js/animation web applications.

**Research the following:**

1. **Testing Pyramid for Modern Web Apps**:
   - Unit tests: Vitest, Jest (fast, isolated)
   - Integration tests: React Testing Library (component behavior)
   - E2E tests: Playwright, Cypress (full user flows)
   - Visual regression: Chromatic, Percy (screenshot comparison)
   - Performance tests: Lighthouse CI, custom benchmarks
   - Accessibility tests: axe-core, Pa11y

2. **React Testing Best Practices (2025-2026)**:
   - Testing hooks with renderHook
   - Testing Server Components
   - Testing Suspense boundaries
   - Testing error boundaries
   - Mocking modules and APIs
   - Testing animations (GSAP, Framer Motion)

3. **Three.js Testing**:
   - Headless rendering with node-canvas or headless-gl
   - Snapshot testing for 3D scenes
   - Performance benchmarking for render loops
   - Memory leak testing with heap snapshots
   - WebGL context mock for unit tests

4. **Property-Based Testing**:
   - fast-check library for JavaScript
   - Generating random inputs to find edge cases
   - Shrinking failures to minimal reproduction
   - When property tests are more effective than example tests

5. **Mutation Testing**:
   - Stryker for JavaScript/TypeScript
   - How mutation testing reveals weak tests
   - Kill score as a quality metric
   - When mutation testing is worth the cost

**Output format:** For each strategy, provide: setup, what bugs it catches, ROI estimate, and integration with debugging workflow.
