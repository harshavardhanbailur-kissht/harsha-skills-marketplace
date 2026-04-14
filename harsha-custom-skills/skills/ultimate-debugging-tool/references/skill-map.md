# Ultimate Debugger — Skill Map

**Status:** Fully self-contained (as of April 2, 2026)

**Purpose:** Navigate the skill's structure and find the right reference for your task.

**Last Updated:** April 2, 2026

---

## Overview: Self-Contained Architecture

This skill is now **fully self-contained**. All content previously distributed across `gas-debugger` and `performance-debugger` has been absorbed into unified reference files.

**Python scripts** require PyYAML (specified in `requirements.txt`). Reference files have no external dependencies—everything you need is here.

**Key principle:** Slim core (SKILL.md), modular references. Load only what you need.

---

## Core File

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **SKILL.md** | Orchestration hub, pipeline overview, triage decisions | Always (loaded first) | ~91 lines (~1,360 tokens) |

---

## Reference Documents — By Use Case

### Debugging Workflow

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **debugging-methodology.md** | Scientific debugging method, hypothesis testing, data flow tracing | When root cause is elusive | 653 lines |
| **pipeline-phases.md** | Phase 0-5 workflow, checklists, deliverables | When debugging phase details needed | 530 lines |
| **fix-safety.md** | 8-level verification hierarchy, fix templates, safe patterns | When designing and implementing fixes | 818 lines |

### Code Quality & Best Practices

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **code-quality.md** | Boy Scout Rule, code smells, safe refactoring patterns | When improving code during debugging | 343 lines |

### Framework & Technology-Specific Patterns

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **react-bugs.md** | React 19+ bug patterns (R-001 to R-008) | When debugging React/hooks bugs | 683 lines |
| **nextjs-bugs.md** | Next.js 15+/16+ patterns (N-001 to N-004) | When debugging Next.js | 494 lines |
| **threejs-bugs.md** | Three.js patterns (T-001 to T-005) | When debugging 3D rendering bugs | 622 lines |
| **gsap-bugs.md** | GSAP/animation patterns (G-001 to G-004) | When debugging animation issues | 447 lines |
| **typescript-bugs.md** | TypeScript patterns (TS-001 to TS-003) | When debugging type system issues | 341 lines |

### Performance & Runtime Analysis (Absorbed from performance-debugger)

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **context-detection.md** | Framework detection, project profiling, capability mapping | When analyzing project context | 263 lines |
| **adaptive-budgets.md** | Token budgets, cost estimation, resource constraints | When planning verification scope | 214 lines |
| **runtime-profiling.md** | Memory profiling, execution tracing, bottleneck identification | When investigating performance issues | 382 lines |
| **core-web-vitals.md** | CWV metrics, LCP/FID/CLS monitoring, thresholds | When debugging frontend performance | 463 lines |
| **memory-management.md** | Memory leaks, GC patterns, heap analysis | When debugging memory issues | 769 lines |
| **skill-awareness.md** | Self-reflection, decision logging, improvement tracking | When tuning skill behavior | 225 lines |

### GAS Debugging (Absorbed from gas-debugger)

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **specialized-prompts.md** | Targeted prompts for different bug types and contexts | When structuring queries for specific domains | 226 lines |
| **format-specs.md** | YAML schemas for bug reports, fix reports, GAS queries | When generating structured output | 425 lines |

### Testing & Production

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **testing-strategy.md** | Testing pyramid, regression tests, property-based testing | When writing tests for fixes | 637 lines |
| **production-integration.md** | Error tracking (Sentry), Web Vitals, CI/CD gates | When deploying fixes | 717 lines |

### Advanced Features & Design

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **avp-learning.md** | Learning loop schema, EMA, confidence weighting | When tuning AVP adaptation | 166 lines |

### Machine-Readable Catalog

| File | Purpose | When to Read | Size |
|------|---------|-------------|------|
| **pattern-index.json** | Machine-readable pattern catalog (24 patterns) | Used by `context_analyzer.py` automatically | 24 patterns |

---

## Executable Scripts

All scripts located in `scripts/` directory. Run via command line (do NOT load into context).

### Debug Session Initialization & Management (from gas-debugger)

| Script | Purpose | Input | Output | Run When |
|--------|---------|-------|--------|----------|
| **init_debug_session.py** | Initialize debugging environment, set up logging | Project path + config | Session metadata (YAML) | Session start |
| **scan_bugs.py** | Scan codebase for known bug patterns | Project path | Bug findings (JSON/YAML) | Early discovery phase |
| **filter_bugs.py** | Filter and prioritize bug findings by severity | Bug findings + rules | Filtered results (YAML) | After scan |

### Core Analysis

| Script | Purpose | Input | Output | Run When |
|--------|---------|-------|--------|----------|
| **context_analyzer.py** | Detect project type, frameworks, applicable patterns | `<project-path>` | ProjectContext (JSON/YAML) | Phase 0 (setup) |
| **fix_signal_analyzer.py** | Measure fix complexity (6 signals) → verification depth | Fix diff + project type | FixSignalReport (verification_depth) | Phase 3 (after fix design) |

**fix_signal_analyzer.py usage:**
```bash
python3 scripts/fix_signal_analyzer.py --diff fix.diff --project-type react-spa --severity medium
git diff HEAD~1 | python3 scripts/fix_signal_analyzer.py --stdin --severity high --format json
```

### Fix Verification & Reporting (from gas-debugger)

| Script | Purpose | Input | Output | Run When |
|--------|---------|-------|--------|----------|
| **verify_fix.py** | Verify fix correctness, safety, and completeness | Fix diff + test results | Verification report (YAML) | Phase 4 (verification) |
| **generate_report.py** | Generate comprehensive debugging report | Analysis results + logs | Structured report (HTML/MD/JSON) | Phase 5 (completion) |

### Learning & Adaptive Loop

| Script | Purpose | Action | Output | Run When |
|--------|---------|--------|--------|----------|
| **avp_learner.py** | Record escalation events, compute AVP weight adjustments | record, status, metrics | Learning metrics (YAML) | After Phase 4 escalation |

**avp_learner.py usage:**
```bash
python3 scripts/avp_learner.py --action status
python3 scripts/avp_learner.py --action record --signal type_cascade --project-type react-spa
python3 scripts/avp_learner.py --action compute-weights
```

### Unified Pipeline

| Script | Purpose | Input | Output | Run When |
|--------|---------|-------|--------|----------|
| **debug_pipeline.py** | Full pipeline: context → analyze → verify → report | Project path + fix diff | Complete debugging report | Full debugging session |

**Usage:**
```bash
python3 scripts/debug_pipeline.py <project-path> --diff <fix.diff>
```

### Maintenance & Version Checking

| Script | Purpose | Input | Output | Run When |
|--------|---------|-------|--------|----------|
| **version_checker.py** | Check framework versions against documented patterns | (auto-detects) | Version compatibility report | During setup or maintenance |

---

## Assets & Configuration

| Location | Purpose | File | Used By |
|----------|---------|------|---------|
| **assets/** | Ignore rules template (from gas-debugger) | `ignore-rules-template.yaml` | `init_debug_session.py` |

---

## Developer Documentation

| Location | Purpose | File | When to Read |
|----------|---------|------|-------------|
| **docs/** | Design decisions and research citations | `avp-design-decisions.md` | When questioning skill architecture |

---

## Testing & Quality Assurance

| File | Purpose | Test Count |
|------|---------|-----------|
| **tests/test_context_analyzer.py** | Context detection and project profiling | 47 |
| **tests/test_fix_signal_analyzer.py** | Signal analysis and complexity measurement | 62 |
| **tests/test_avp_learner.py** | Learning loop and weight adaptation | ~20 |
| **tests/test_pipeline_integration.py** | End-to-end pipeline integration | ~15 |

**Run all tests:**
```bash
pytest tests/ -v
pytest tests/test_context_analyzer.py -v    # Specific file
pytest -k "test_detect_react" -v            # By name pattern
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      DEBUGGING SESSION START                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────┐
    │ PHASE 0: CONTEXT & TRIAGE            │
    │ Run: init_debug_session.py           │
    │      context_analyzer.py <path>      │
    │      scan_bugs.py <path>             │
    └──────────────┬───────────────────────┘
                   │
                   ├─→ Detect project type, frameworks
                   ├─→ Load applicable patterns
                   ├─→ Scan for known bugs
                   └─→ Filter by severity
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ PHASE 1: REPRODUCE & MEASURE         │
    │ Reference: pipeline-phases.md        │
    │ Reference: runtime-profiling.md      │
    │ Reference: core-web-vitals.md        │
    └──────────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ PHASE 2: ROOT CAUSE ANALYSIS         │
    │ Reference: debugging-methodology.md  │
    │ Reference: pipeline-phases.md        │
    │ Reference: memory-management.md      │
    └──────────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ PHASE 3: FIX DESIGN                  │
    │ Reference: fix-safety.md             │
    │ Reference: specialized-prompts.md    │
    └──────────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ Run: fix_signal_analyzer.py           │
    │ Measures: diff_size, files_touched,  │
    │ ast_depth, type_surface, test_surface│
    │ dependency_fan → verification_depth  │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ PHASE 4: ADAPTIVE VERIFICATION (AVP) │
    │ Run: verify_fix.py                   │
    │ Reference: pipeline-phases.md        │
    │ Reference: adaptive-budgets.md       │
    │                                      │
    │ L1-L4: Mandatory (syntax, type,     │
    │        lint, tests)                  │
    │                                      │
    │ If escalation signals:               │
    │   → Run avp_learner.py               │
    │   → Auto-escalate to L1-L8           │
    │                                      │
    │ L5-L8: Depth-proportional            │
    │        (regression, perf, visual,   │
    │         security)                    │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ PHASE 5: IMPROVE & COMMIT            │
    │ Run: generate_report.py              │
    │ Reference: code-quality.md           │
    │ Reference: pipeline-phases.md        │
    └──────────────┬───────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────┐
    │ PRODUCTION INTEGRATION               │
    │ Reference: production-integration.md │
    │ Reference: testing-strategy.md       │
    └──────────────────────────────────────┘
```

---

## Quick Reference: When to Read What

**New to this skill?**
1. Read: SKILL.md (front-to-back)
2. Then: Choose references based on your situation

**React bug?**
1. Read: react-bugs.md (find pattern: R-001, R-002, etc.)
2. Reference: fix-safety.md (safe patterns)
3. Reference: debugging-methodology.md (if root cause unclear)

**Performance issue?**
1. Read: core-web-vitals.md (metric thresholds)
2. Reference: runtime-profiling.md (bottleneck analysis)
3. Reference: memory-management.md (if memory-related)
4. Reference: production-integration.md (monitoring setup)

**Complex fix (high verification_depth)?**
1. Run: `fix_signal_analyzer.py --diff <fix.diff>`
2. Read: adaptive-budgets.md (resource planning)
3. Reference: fix-safety.md (L5-L8 verification)

**Extending the skill?**
1. Read: docs/avp-design-decisions.md (architecture)
2. Reference: skill-awareness.md (self-reflection)
3. Reference: avp-learning.md (adaptation mechanisms)

**Not sure what's happening?**
1. Run: `context_analyzer.py <project-path>`
2. Run: `scan_bugs.py <project-path>`
3. Read: debugging-methodology.md (scientific method)
4. Reference: pipeline-phases.md (workflow context)

---

## File Size Summary

| Category | Count | Total Size |
|----------|-------|-----------|
| Core (SKILL.md) | 1 | ~91 lines |
| Debugging workflow | 3 | 1,901 lines |
| Code quality | 1 | 343 lines |
| Framework-specific | 5 | 2,587 lines |
| Performance (absorbed) | 6 | 2,216 lines |
| GAS/Reporting (absorbed) | 2 | 651 lines |
| Testing & production | 2 | 1,354 lines |
| Advanced (AVP) | 1 | 166 lines |
| **Total reference docs** | 21 | **9,458 lines** |
| Scripts (executable) | 10 | 2,400+ lines |
| Tests (unit + integration) | 4 | 1,427 lines |

---

## File Structure

```
ultimate-debugger/
├── SKILL.md                              # Orchestration hub
├── references/
│   ├── debugging-methodology.md
│   ├── pipeline-phases.md
│   ├── fix-safety.md
│   ├── code-quality.md
│   ├── react-bugs.md
│   ├── nextjs-bugs.md
│   ├── threejs-bugs.md
│   ├── gsap-bugs.md
│   ├── typescript-bugs.md
│   ├── context-detection.md              # (from performance-debugger)
│   ├── adaptive-budgets.md               # (from performance-debugger)
│   ├── runtime-profiling.md              # (from performance-debugger)
│   ├── core-web-vitals.md                # (from performance-debugger)
│   ├── memory-management.md              # (from performance-debugger)
│   ├── skill-awareness.md                # (from performance-debugger)
│   ├── specialized-prompts.md            # (from gas-debugger)
│   ├── format-specs.md                   # (merged with gas-debugger schemas)
│   ├── avp-learning.md
│   ├── pattern-index.json
│   └── skill-map.md                      # (this file)
├── scripts/
│   ├── init_debug_session.py             # (from gas-debugger)
│   ├── scan_bugs.py                      # (from gas-debugger)
│   ├── filter_bugs.py                    # (from gas-debugger)
│   ├── context_analyzer.py
│   ├── fix_signal_analyzer.py
│   ├── verify_fix.py                     # (from gas-debugger)
│   ├── generate_report.py                # (from gas-debugger)
│   ├── avp_learner.py
│   ├── debug_pipeline.py
│   └── version_checker.py
├── assets/
│   └── ignore-rules-template.yaml        # (from gas-debugger)
├── docs/
│   └── avp-design-decisions.md           # (moved from references/)
├── tests/
│   ├── test_context_analyzer.py
│   ├── test_fix_signal_analyzer.py
│   ├── test_avp_learner.py
│   ├── test_pipeline_integration.py
│   └── fixtures/
└── CHANGELOG.md
```

---

## Design Principles

1. **Self-contained:** No external dependencies on sibling skills
2. **Modular:** Reference files by use case, not by internal hierarchy
3. **Layered:** SKILL.md → references → scripts → tests
4. **Pragmatic:** Core functionality stable; advanced features optional
5. **Documented:** Every file has clear purpose and when to read it
