# Format Specifications — Ultimate Debugger

Enhanced schema definitions extending gas-debugger's manifest system with fix quality scoring, verification levels, regression tests, code quality improvements, and context awareness.

**Note:** This specification builds upon and consolidates the gas-debugger format specs. All gas-debugger formats are fully supported with additional enhancements.

## Scan Output Formats (From gas-debugger)

### Concise Format (Default)

Optimized for LLM chaining - minimal tokens:

```json
{"bugs":[{"id":"B001","loc":"auth.py:45","cat":"security","sev":"high","desc":"SQL injection"}]}
```

Field abbreviations:
- `id`: Bug identifier
- `loc`: Location as file:line
- `cat`: Category
- `sev`: Severity
- `desc`: Description (keep under 50 chars)
- `cwe`: Optional CWE reference

### Detailed Format

For human review:

```yaml
bugs:
  - id: "B001"
    status: "pending"
    confidence: 0.85
    category: "security"
    severity: "high"
    location:
      file: "src/auth.py"
      line: 45
      function: "authenticate"
    description: "SQL injection vulnerability via string concatenation"
    cwe: "CWE-89"
    context:
      code_snippet: "query = f\"SELECT * FROM users WHERE id={user_id}\""
      suggestion: "Use parameterized query"
```

## Bug Manifest Schema (Enhanced)

```yaml
# .ultimate-debugger/bug-manifest.yaml

session:
  id: string              # Format: sess-YYYYMMDD-XXXXXX
  started: datetime        # ISO 8601
  original_goal: string    # What the user asked for
  project_path: string     # Absolute path to project root

  # NEW: Context detection results (from performance-debugger v2)
  context:
    project_type: enum     # 3d-experience | animation-site | react-spa | dashboard | hybrid
    detected_skills:       # Skills that generated this code
      - name: string       # e.g., "3d-web-graphics-mastery"
        confidence: float  # 0.0 - 1.0
        patterns_found:    # Which patterns were detected
          - string         # e.g., "gsap-proxy", "effect-composer", "delta-capping"
    device_tier: enum      # ultra | high | medium | low (target deployment)
    budget_profile: string # e.g., "budget-3d", "budget-spa"
    frameworks:            # Detected frameworks
      - name: string       # e.g., "react", "next", "three"
        version: string    # e.g., "19.2", "15.1", "0.170"

stats:
  total_found: integer
  pending: integer
  fixing: integer
  fixed: integer
  verified: integer
  ignored: integer
  # NEW stats
  regression_tests_added: integer
  code_improvements_made: integer
  fix_quality_avg: float   # Average fix quality score (0-25)

bugs:
  - id: string             # Format: B[A-F0-9]{6}
    status: enum           # pending | fixing | fixed | verified | ignored
    confidence: float      # 0.0 - 1.0
    category: enum         # security | logic | performance | quality | framework | type-safety | regression
    severity: enum         # critical | high | medium | low
    location:
      file: string         # Relative path from project root
      line: integer        # 1-indexed
      function: string     # Optional: containing function name
      component: string    # Optional: React component name
    description: string    # Brief description (max 200 chars)
    cwe: string            # Optional: CWE-XXX
    pattern_id: string     # Optional: e.g., "R-001", "T-002", "P4-003"

    # NEW: Context awareness
    context:
      intentional: boolean     # Was this pattern intentional (from another skill)?
      skill_source: string     # Which skill created this pattern
      within_budget: boolean   # Is this within the adaptive performance budget?
      fix_tier: enum           # safe | moderate | aggressive

    # NEW: Root cause analysis
    root_cause:
      hypothesis: string       # What we think caused this bug
      confirmed: boolean       # Has the hypothesis been tested?
      symptom_vs_root: enum    # symptom | root | unknown
      related_bugs: [string]   # IDs of related bugs (same root cause)

    # Fix tracking (enhanced)
    fix_applied: string
    fixed_at: datetime
    fix_diff:                  # Minimal diff
      - file: string
        line: integer
        before: string
        after: string

    # NEW: Fix quality scoring
    fix_quality:
      minimal: integer         # 1-5 (5 = smallest possible change)
      safe: integer            # 1-5 (5 = zero risk of side effects)
      clean: integer           # 1-5 (5 = improves readability)
      tested: integer          # 1-5 (5 = regression test included)
      root_cause: integer      # 1-5 (5 = fixes root cause, not symptom)
      total: integer           # Sum of above (target: 20+)

    # NEW: Verification with levels
    verification:
      level_reached: integer   # 1-8 (which level of verification passed)
      levels:
        syntax: boolean        # L1: AST parses
        types: boolean         # L2: TypeScript compiles
        lint: boolean          # L3: No new lint warnings
        tests: boolean         # L4: Existing tests pass
        regression: boolean    # L5: New regression test passes
        performance: boolean   # L6: No perf regression
        visual: boolean        # L7: Screenshot diff OK
        security: boolean      # L8: No new vulnerabilities
      verified_at: datetime
      confidence: float

    # NEW: Regression test
    regression_test:
      file: string             # Test file path
      test_name: string        # Test function name
      description: string      # What the test verifies

    # Ignore tracking (preserved from gas-debugger)
    ignore_rule: string
    ignored_at: datetime
```

## Fix Entry Schema

```yaml
fix:
  bug_id: string
  timestamp: datetime

  # Root cause (must be filled before fixing)
  root_cause: string         # One-sentence explanation of WHY the bug exists

  # The fix itself
  changes:
    - file: string
      line: integer
      before: string         # Exact code being replaced
      after: string          # Replacement code
      reasoning: string      # Why this specific change

  # Fix classification
  tier: enum                 # safe | moderate | aggressive
  quality_impact: string     # For moderate/aggressive: what users notice

  # Quality scoring
  quality:
    minimal: integer         # 1-5
    safe: integer            # 1-5
    clean: integer           # 1-5
    tested: integer          # 1-5
    root_cause: integer      # 1-5
    total: integer           # Target: 20+

  # Regression test (REQUIRED for severity >= medium)
  regression_test:
    file: string             # Where the test lives
    test_name: string        # Test function name
    test_code: string        # The actual test code
```

## Code Improvement Entry Schema

```yaml
# Separate from bug fixes — tracked independently
improvement:
  id: string                 # Format: IMP-XXXXXX
  timestamp: datetime
  related_bug: string        # Bug ID that led to discovering this improvement

  type: enum                 # extract-constant | extract-function | add-types |
                             # remove-dead-code | add-docs | simplify-logic |
                             # improve-naming | add-error-handling

  location:
    file: string
    line: integer
    function: string

  description: string        # What was improved
  risk: enum                 # none | low | moderate (never high during debugging)

  changes:
    - file: string
      before: string
      after: string
```

## Verification Report Schema

```yaml
verification:
  bug_id: string
  timestamp: datetime

  # 8-level results
  levels:
    - level: 1
      name: "syntax"
      passed: boolean
      duration_ms: integer
      message: string

    - level: 2
      name: "types"
      passed: boolean
      duration_ms: integer
      message: string

    - level: 3
      name: "lint"
      passed: boolean
      duration_ms: integer
      message: string

    - level: 4
      name: "tests"
      passed: boolean
      duration_ms: integer
      tests_run: integer
      tests_passed: integer
      message: string

    - level: 5
      name: "regression"
      passed: boolean
      duration_ms: integer
      regression_test: string   # Test name
      message: string

    - level: 6
      name: "performance"
      passed: boolean
      metrics:
        frame_time_before: float
        frame_time_after: float
        memory_before: float
        memory_after: float
        bundle_size_change: integer
      message: string

    - level: 7
      name: "visual"
      passed: boolean
      screenshot_diff_percent: float
      message: string

    - level: 8
      name: "security"
      passed: boolean
      vulnerabilities_found: integer
      message: string

  # Overall result
  highest_level_passed: integer
  overall_confidence: float
  verdict: enum              # pass | fail | partial
  issues: [string]           # List of failure reasons
```

## Session Report Schema

```yaml
report:
  session_id: string
  duration_minutes: integer
  project_type: string

  stats:
    total_bugs: integer
    by_status:
      verified: integer
      fixed: integer
      pending: integer
      ignored: integer
    by_category:
      security: integer
      logic: integer
      performance: integer
      quality: integer
      framework: integer
      type_safety: integer
    by_severity:
      critical: integer
      high: integer
      medium: integer
      low: integer

    # NEW: Quality metrics
    avg_fix_quality: float       # Average of all fix quality totals
    regression_tests_added: integer
    code_improvements_made: integer
    verification_rate: float     # % of fixes that reached level 4+
    high_quality_fixes: integer  # Fixes scoring 20+ quality

  # NEW: Lessons learned
  patterns_found:
    - pattern: string            # Bug pattern ID (e.g., "R-001")
      count: integer             # How many times found
      recommendation: string     # How to prevent in future

  # NEW: Code quality delta
  quality_delta:
    dead_code_removed: integer   # Lines of dead code removed
    types_added: integer         # TypeScript types added
    docs_added: integer          # JSDoc comments added
    complexity_reduced: integer  # Functions simplified
```

## Ignore Rules Schema (From gas-debugger)

```yaml
# .debug-session/ignore-rules.yaml or .ultimate-debugger/ignore-rules.yaml

rules:
  - id: string              # Unique identifier (kebab-case)

    # Matching criteria (at least one required)
    pattern: string         # Regex or literal string to match
    file_glob: string       # Glob pattern for file paths

    # Optional filters
    categories: [string]    # Only apply to these bug categories

    # Documentation (required)
    reason: string          # Why this rule exists

    # Optional metadata
    expires: date           # YYYY-MM-DD format, rule ignored after
    ticket: string          # Reference to tracking ticket
    owner: string           # Team or person responsible
    created: date           # When rule was added

    # Optional actions
    on_expiry:
      action: enum          # convert_to_error | delete | notify
      notify: [string]      # Notification channels
```

### Common Ignore Rule Categories

- **Test fixtures** (`file_glob: tests/**`) - Test code has different requirements
- **Development credentials** (`pattern: password.*test`) - Dev/test only
- **Vendor code** (`file_glob: vendor/**`) - Third-party code not under our control
- **Generated code** (`file_glob: **/generated/**`) - Auto-generated files
- **Legacy code** (`file_glob: src/legacy/**`) - Scheduled for migration
- **TODO markers** (`pattern: "TODO:|FIXME:"`) - Intentional technical debt
- **Internal APIs** (`pattern: "@no_auth_required"`) - Isolated network patterns

## Status Codes (Enhanced)

| Status | Description | Next Actions |
|--------|-------------|--------------|
| `pending` | Bug identified, not yet addressed | Prioritize, then fix or ignore |
| `fixing` | Root cause confirmed, implementing fix | Complete fix, write regression test |
| `fixed` | Fix applied, regression test written | Run 8-level verification |
| `verified` | Fix confirmed at level 4+ | Complete (commit) |
| `ignored` | Matched ignore rule or intentional pattern | Log reason, review at expiry |

## Severity Levels (Enhanced)

| Level | Description | Response | Verification Level |
|-------|-------------|----------|-------------------|
| `critical` | Security vuln, data loss, crash | Immediate | Must reach L8 |
| `high` | Logic error affecting users | Same day | Must reach L5 |
| `medium` | Performance issue, minor logic | Same sprint | Must reach L4 |
| `low` | Code quality, maintainability | Backlog | Must reach L3 |

## Category Definitions (Enhanced)

| Category | Description | Examples |
|----------|-------------|----------|
| `security` | Vulnerabilities, auth bypass, injection | XSS, CSRF, SQL injection, secrets exposure |
| `logic` | Incorrect behavior | Null deref, race condition, wrong condition |
| `performance` | Slowness, resource waste | Memory leak, jank, excessive re-renders |
| `quality` | Maintainability issues | Dead code, magic numbers, deep nesting |
| `framework` | Framework-specific bugs | Hooks violations, hydration mismatch, disposal |
| `type-safety` | TypeScript issues | `any` usage, missing null checks, bad narrowing |
| `regression` | Previously fixed bug returned | Test missing, fix incomplete, new code reintroduced |

## Report Format (From gas-debugger)

### Summary Stats

```json
{
  "session_id": "sess-20241222-abc123",
  "duration_minutes": 45,
  "stats": {
    "total": 15,
    "by_status": {
      "verified": 8,
      "fixed": 2,
      "pending": 3,
      "ignored": 2
    },
    "by_category": {
      "security": 5,
      "logic": 6,
      "performance": 3,
      "quality": 1
    },
    "verification_rate": 0.80,
    "high_severity_fixed": 4
  }
}
```

**Note:** Ultimate Debugger extends this with additional quality metrics, regression test counts, and code improvement tracking (see Session Report Schema above).

## Fix Signal Analysis Schema (AVP — Adaptive Verification Pipeline)

```yaml
# New fields added to each bug entry in the manifest
# These complement the existing verification block (not replace it)
fix_signals:
  verification_depth: float      # 0.0-1.0 composite score
  depth_category: enum           # minimal | low | moderate | high | full
  escalated: boolean             # Was this auto-promoted by L1-L4 findings?
  escalation_reason: string      # Why (if escalated)
  escalation_trigger: string     # Which specific trigger fired
  original_depth: float          # Score before escalation (for learning)

  signals:
    diff_size: float             # 0.0-1.0 — Lines changed (relative churn)
    files_touched: float         # 0.0-1.0 — Count of modified files
    ast_depth: float             # 0.0-1.0 — Nature of AST change (leaf/branch/structural)
    type_surface: float          # 0.0-1.0 — Type system impact
    test_surface: float          # 0.0-1.0 — Test coverage breadth
    dependency_fan: float        # 0.0-1.0 — Downstream caller impact

  # Depth decision record
  depth_decision:
    levels_required: [integer]   # Which levels were determined necessary (always [1,2,3,4])
    levels_recommended: [integer] # Additional levels from signal analysis (subset of [5,6,7,8])
    levels_executed: [integer]   # Which levels actually ran (may differ if escalated)
    severity_override: boolean   # Did the severity ratchet force deeper verification?
    veto_override: boolean       # Did a veto trigger force minimum composite?

  # Weights used for this analysis
  weights_used:
    diff_size: float
    files_touched: float
    ast_depth: float
    type_surface: float
    test_surface: float
    dependency_fan: float

  # Veto information
  veto:
    triggered: boolean
    reason: string
    minimum_score: float
```

### Auto-Escalation Event Schema

```yaml
# Recorded when L1-L4 results trigger auto-promotion to full L1-L8
escalation_event:
  bug_id: string
  timestamp: datetime
  original_depth: float          # Signal analyzer's predicted depth
  escalated_to: float            # New depth after escalation
  trigger: enum                  # type_cascade | distant_test_failure |
                                 #   lint_chain_reaction | coverage_drop
  trigger_details:
    affected_files: [string]     # Files where unexpected signals appeared
    in_diff: boolean             # Were affected files in the original diff?
    error_count: integer         # How many unexpected errors/warnings
    message: string              # Human-readable description
  outcome: enum                  # verified_clean | caught_regression |
                                 #   false_alarm | inconclusive
```

## Fix Quality Score Interpretation

| Total Score | Rating | Action |
|-------------|--------|--------|
| 22-25 | Excellent | Ship with confidence |
| 18-21 | Good | Acceptable for most bugs |
| 15-17 | Acceptable | OK for low-severity only |
| 10-14 | Poor | Rework the fix |
| <10 | Reject | Start over with better root cause analysis |
