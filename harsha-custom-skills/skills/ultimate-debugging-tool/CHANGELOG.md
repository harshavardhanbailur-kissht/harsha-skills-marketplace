# Ultimate Debugger — Changelog

All notable changes to this skill are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.1.1] — 2026-04-05

### Added
- **references/security-bugs.md**: Fix templates for all 10 CWE patterns (S-001 through S-010) with safe code, regression tests, and severity ratings
- **.skillignore**: Prevents `research/` folder (~124KB) from being loaded into LLM context
- Security vulnerability triage row pointing to `references/security-bugs.md`
- Fallback "Other / unknown category" triage row
- 6 new tests: CORS `setHeader`/`set`/`header` detection, specific-origin false positive, JWT multiline ±8 context (with and without algorithms)

### Fixed
- **SKILL.md frontmatter**: `name: ultimate-debugger` → `name: ultimate-debugging-tool` (prevents collision with v2.0.0 skill)
- **detect_permissive_cors()**: Now detects `res.setHeader('Access-Control-Allow-Origin', '*')`, `res.set()`, `res.header()`, and `headers.set()` — the most common Node.js CORS patterns
- **detect_jwt_alg_none()**: Context window expanded from ±2 to ±8 lines to catch `algorithms` parameter in standard multi-line `jwt.verify()` calls

### Testing
- 494 tests passing (120 scan_bugs + 374 others)

## [2.1.0] — 2026-04-05

### Added
- **5 new CWE security patterns in scan_bugs.py**: CWE-601 (Open Redirect),
  CWE-942 (Permissive CORS), CWE-1321 (Prototype Pollution), CWE-943 (NoSQL
  Injection), CWE-347 (JWT Algorithm None) — restoring full Gen 1 security
  coverage. Each has a detector function + tests.
- **Concurrency debugging protocol** in references/debugging-methodology.md
  (Section 7): identification signatures, requestId tracing protocol, 3 fix
  patterns (AbortController, useRef mutex, sequential guard), the one rule
  (never fix a race with try/catch or setTimeout).
- **AVP CI/CD integration guide** at docs/avp-ci-integration.md: GitHub
  Actions workflow, manual escalation logging, cold-start progression table.
  Makes the EMA learning loop usable in persistent environments.
- **Race condition row** in SKILL.md triage table.

### Changed
- **SKILL.md**: Added Fix Validity / Hallucination Prevention section (JS
  package hallucination rate 21.7%, import validation rule before applying fix).
  Added AST heuristic accuracy note to fix_signal_analyzer.py script row.
- **references/avp-learning.md**: Added "Getting Started" section at top
  linking to avp-ci-integration.md.

## [2.0.0] — 2026-04-02

### Added
- **Adaptive Verification Pipeline (AVP)**: Fix Signal Analyzer with 6-signal measurement
- **Pattern Index** (pattern-index.json): Machine-readable catalog of 24 bug patterns with min/max framework versions
- **Context→Pattern Mapping**: context_analyzer.py now outputs applicable bug patterns from pattern-index.json
- **Per-Framework Bug Files**: Split framework-bugs.md into react-bugs.md, nextjs-bugs.md, threejs-bugs.md, gsap-bugs.md, typescript-bugs.md
- **Loading Strategy**: Quick Triage table in SKILL.md for selective reference loading (avoid context bloat)
- **Integration Tests**: 109 tests for context_analyzer.py and fix_signal_analyzer.py
- **Version Checker**: scripts/version_checker.py for automated staleness detection (quarterly run)
- **AVP Learner**: scripts/avp_learner.py implementing the EMA learning loop (weight tuning from escalation events)
- **Debug Pipeline**: scripts/debug_pipeline.py chaining context→signals→recommendations
- **Skill Map**: references/skill-map.md documenting file structure and data flow
- **Version Management**: Version check cadence and learning loop review schedule moved to references/skill-map.md

### Changed
- **N-001 (Stale Cache Data)**: Updated for Next.js 16 "use cache" directive (backward compatible with 15.x)
- **N-004 (Middleware Security Bypass)**: Marked as resolved in 15.2.3+ (CVE-2025-29927) with max_version: 15.2.2
- **T-005 (WebGL Context Loss)**: Added WebGPU guidance for r171+ (WebGPURenderer async init, context restoration)
- **SKILL.md**: Slimmed from 426 to ~91 lines (~1,360 tokens); detailed phases extracted to pipeline-phases.md for modularity
- **All framework sections**: Added version labels (min_version/max_version) and "Last Validated" dates from pattern-index.json

### Fixed
- context_analyzer.py frameworks field now uses list of dicts (was breaking with asdict())
- pattern-index.json reference_file fields updated to use split file names (react-bugs.md, not framework-bugs.md)
- Version checker properly handles Three.js "r171" notation in version parsing

### Deprecated
- framework-bugs.md (replaced by framework-specific files: react-bugs.md, nextjs-bugs.md, etc.)

## [1.0.0] — 2026-02-06

### Added
- Initial release: Unified debugging + performance optimization + code quality system
- Inherits from gas-debugger (YAML bug manifests, category scanning, ignore rules, token optimization)
- Inherits from performance-debugger v2 (context detection, adaptive budgets, tiered fixes, skill awareness)
- **8-level verification hierarchy** (L1-L8) for safe fixing
  - L1-L4: Quick checks (syntax, smoke tests, basic regression)
  - L5-L6: Deep verification (integration tests, cross-browser, performance profiling)
  - L7-L8: Production gates (Sentry alerts, Web Vitals, CI/CD checks)
- **24 cross-framework bug patterns** (React 19+, Next.js 15+, Three.js r171+, GSAP 3.12+, TypeScript 5+)
  - React: 8 patterns (hooks, SSR, context, Suspense, compiler)
  - Next.js: 4 patterns (caching, server actions, env vars, middleware security)
  - Three.js: 5 patterns (memory, performance, WebGL, rendering)
  - GSAP: 4 patterns (context cleanup, ScrollTrigger, Lenis sync, conflicting tweens)
  - TypeScript: 3 patterns (any type, null checks, type narrowing)
- context_analyzer.py: Project type detection (3d-experience, animation-site, react-spa, dashboard, hybrid)
- fix_signal_analyzer.py: 6-signal fix complexity assessment
- Fix quality scoring (5 dimensions: syntax, logic, perf, type-safe, breaking-free; target 20+)
- Production integration guides (Sentry, Web Vitals, CI/CD gates)
- Safe fix templates (8 templates for common bug patterns)
- Regression prevention (test templates for every safe fix pattern)

### Documentation
- SKILL.md: 426 lines covering missions, principles, architecture, quick triage, pipeline phases, verification levels
- references/debugging-methodology.md: Reproduction, root cause analysis, measurement strategies
- references/fix-safety.md: 8-level verification hierarchy with checklists for L1-L8
- references/react-bugs.md: React patterns (16.8+, 18.0+, 19.0+)
- references/nextjs-bugs.md: Next.js patterns (10.0+, 13.0+, 15.0+)
- references/threejs-bugs.md: Three.js patterns (r171+)
- references/gsap-bugs.md: GSAP patterns (3.12+)
- references/typescript-bugs.md: TypeScript patterns (5.0+)
- references/code-quality.md: Refactoring during debugging (Boy Scout Rule)
- references/production-integration.md: Sentry, Web Vitals, CI/CD gates
- references/testing-strategy.md: Test templates for 24 patterns
- references/format-specs.md: VersionCheck, FixQuality, AVP signal structures (JSON/YAML)
- references/avp-design-decisions.md: Why 6 signals? Why EMA learning? Trade-offs documented

### Testing
- 109 integration tests covering context_analyzer.py and fix_signal_analyzer.py
- Test suite verifies framework detection, pattern matching, version parsing, signal scoring

---

## Changelog Guidelines

When updating this skill, add entries to the top of this changelog under a new version section.

**Types of changes:**
- **Added**: New features or documentation
- **Changed**: Changes to existing functionality
- **Fixed**: Bug fixes
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features

**Version format:** Semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes (safe fix patterns removed, verification levels restructured)
- MINOR: New patterns, scripts, or docs
- PATCH: Bug fixes, minor improvements

**When to release:**
- MAJOR: Annual (or on critical security patterns like CVE-2025-29927)
- MINOR: After 10+ new patterns documented or significant script additions
- PATCH: Bug fixes, version updates to existing patterns
