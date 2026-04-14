---
name: ultimate-debugging-tool
description: Systematic web debugging with root cause analysis, safe fixes, and framework-specific bug patterns for React, Next.js, Three.js, GSAP, and TypeScript.
---

> **Note:** This skill supersedes `ultimate-debugger` v2.0.0. If both coexist in `active/`, archive or remove `ultimate-debugger/` to prevent split-brain discovery.

# Ultimate Debugger

**Fix every bug. Break nothing. Leave the code better than you found it.**

> **Selective loading only.** Use the triage table to load only what you need. Never load all references at once. Scripts are EXECUTED via bash, not loaded into context.

## Core Workflow

```
SCAN → ANALYZE → FIX → VERIFY → COMMIT
  │        │       │       │        │
  ▼        ▼       ▼       ▼        ▼
Phase 0  Phase 1-2  Phase 3  Phase 4  Phase 5
Context  Root Cause  Design   L1-L8   Ship
```

## Absolute Safety Boundaries

- **NEVER** batch unrelated fixes — one fix, one verify, one commit
- **NEVER** skip L1-L4 verification (syntax, types, lint, tests)
- **NEVER** modify auth/payment code without full L1-L8 (`--full`)
- **NEVER** apply fix when confidence < 50% — escalate as `needs_review`
- **NEVER** load all reference files at once — triage table only

## Fix Validity — Hallucination Prevention

Before applying any fix that introduces a new import, package, or method call:
1. **Verify the package exists** in `package.json` / `requirements.txt`
   — do not apply a fix referencing a package that isn't installed
2. **Verify the method/API exists** in the installed version
   — check `node_modules/<pkg>/package.json` version, then docs
3. **Run version check**: `python3 scripts/version_checker.py <project>`
   validates all detected patterns against installed framework versions

Known hallucination rates (from LLM-assisted repair research):
- JavaScript packages: **21.7%** hallucination rate on fix suggestions
- Python packages: **5.2%**

**Rule:** If you cannot verify a method exists in the installed version,
mark the fix `needs_review` — do not mark it `fixed`.

## Triage: What Do I Read?

| Situation | Read | Then (if needed) |
|-----------|------|-------------------|
| React/hooks bug | `references/react-bugs.md` | `references/fix-safety.md` |
| Next.js bug | `references/nextjs-bugs.md` | `references/fix-safety.md` |
| Three.js/3D bug | `references/threejs-bugs.md` | `references/fix-safety.md` |
| GSAP/animation bug | `references/gsap-bugs.md` | `references/fix-safety.md` |
| TypeScript error | `references/typescript-bugs.md` | `references/fix-safety.md` |
| Bug won't reproduce | `references/debugging-methodology.md` | — |
| Race condition / concurrency bug | `references/debugging-methodology.md` | `references/fix-safety.md` |
| Security vulnerability (CWE/OWASP) | `references/security-bugs.md` | `references/fix-safety.md` |
| Performance issue | `references/core-web-vitals.md` | `references/adaptive-budgets.md` |
| React perf | `references/react-performance.md` | `references/performance-patterns.md` |
| Three.js perf | `references/threejs-webgl-performance.md` | `references/performance-patterns.md` |
| Memory leak | `references/memory-management.md` | `references/runtime-profiling.md` |
| Animation perf | `references/animation-performance.md` | `references/skill-awareness.md` |
| Mobile/device perf | `references/mobile-optimization.md` | `references/adaptive-budgets.md` |
| Code quality | `references/code-quality.md` | — |
| Fix pattern catalog | `references/performance-patterns.md` | — |
| Safe fix patterns | `references/fix-safety.md` | — |
| Writing tests | `references/testing-strategy.md` | `references/fix-safety.md` |
| Production monitoring | `references/production-integration.md` | `references/testing-strategy.md` |
| Context detection | `references/context-detection.md` | `references/adaptive-budgets.md` |
| Pipeline phases | `references/pipeline-phases.md` | — |
| Skill overview | `references/skill-map.md` | — |
| Other / unknown category | Start with `references/debugging-methodology.md` | `references/fix-safety.md` |

## Pipeline

**Phase 0 — Context:** `python3 scripts/context_analyzer.py <path>` — detect frameworks, classify issue, load applicable patterns.

**Phase 1 — Reproduce:** Minimal repro. Baseline metrics (FPS, memory, errors). Expected vs actual.

**Phase 2 — Root Cause:** Hypothesis → test → if wrong, new hypothesis. Trace data flow. `git blame`. Find ROOT cause not symptom.

**Phase 3 — Fix:** Minimal change. Classify: SAFE / MODERATE / AGGRESSIVE. Write regression test first. Run `python3 scripts/fix_signal_analyzer.py --diff <file>` for verification depth.

**Phase 4 — Verify (Adaptive L1-L8):**
- L1-L4 ALWAYS: Syntax → Types → Lint → Tests (mandatory floor)
- L5-L8 depth-gated via `--depth` (from fix_signal_analyzer):
  - ≥0.25 → +L5 regression + L6 perf scan
  - ≥0.50 → +L7 visual (snapshots + CSS/JSX)
  - ≥0.75 → +L8 security (dangerous patterns + dep audit)
- `--severity critical` → always L1-L8. `--severity high` → minimum L1-L6
- `--full` → force all L1-L8 regardless of depth

**Phase 5 — Ship:** Bug fix commit (minimal). Separate commit for quality. Update manifest. Scan for similar patterns.

## Quick Start

```bash
# 1. Detect frameworks
python3 scripts/context_analyzer.py <project>
# 2. Scan for bugs (pick category)
python3 scripts/scan_bugs.py <project> -c web        # React/Next.js
python3 scripts/scan_bugs.py <project> -c security    # XSS, injection
python3 scripts/scan_bugs.py <project> -c performance  # Perf anti-patterns
# 3. Fix one bug at a time, then verify
python3 scripts/verify_fix.py <bug-id> --depth 0.8
# 4. Critical bugs: force full verification
python3 scripts/verify_fix.py <bug-id> --full
```

## Bug Tracking

Initialize: `python3 scripts/init_debug_session.py <project>` → creates `.debug-session/` with manifest.

Workflow: Scan → Filter (`scripts/filter_bugs.py`) → Fix one → Verify → Report (`scripts/generate_report.py`).

Manifest persists bug state (pending → fixing → fixed → verified) in YAML to prevent context drift. See `references/format-specs.md` for schemas, `assets/ignore-rules-template.yaml` for false positive elimination.

## Scripts

| Script | Purpose |
|--------|---------|
| `context_analyzer.py` | Detect project type, frameworks, applicable patterns |
| `fix_signal_analyzer.py` | Measure fix complexity → verification depth (0.0-1.0). AST depth uses regex heuristics (~80% accuracy). Use `--verbose` to inspect raw signal scores. Dependency fan-out grep has 5s timeout — logs warning on large codebases. |
| `debug_pipeline.py` | Unified pipeline: context → signals → recommendations |
| `scan_bugs.py` | Scan by category: security, logic, performance, web, quality |
| `verify_fix.py` | L1-L4 mandatory + L5-L8 depth-gated verification |
| `filter_bugs.py` | Apply ignore rules to manifest (false positive elimination) |
| `init_debug_session.py` | Create debug session with manifest templates |
| `generate_report.py` | Generate session summary report |
| `version_checker.py` | Check framework versions against pattern-index.json |
| `avp_learner.py` | EMA weight tuning from escalation events |

## Anti-Patterns to Avoid

- **Symptom-fixing** — fixing the observable error instead of root cause
- **Batch fixes** — multiple unrelated changes in one commit → regressions
- **Skip verification** — marking fixed without running L1-L4 minimum
- **Framework-agnostic** — ignoring React/Next.js specific patterns
- **Silent assumptions** — changing timing/order without tests
