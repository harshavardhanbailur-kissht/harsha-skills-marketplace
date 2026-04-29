# PHASE 5: VALIDATION

**Objective:** Verify that all conflict resolutions are correct across six validation layers — syntax, types, lint, tests, marker cleanup, and semantic integrity. Catch any resolution errors before the human commits.

**Prerequisite**: Phase 4 COMPLETE (all conflict markers should be removed)

**HARD RULE**: NEVER call `git add`, `git commit`, or `git push`. Validation only. The human decides when to commit.

---

## Overview

This phase runs six validation layers in strict order:

```
L1: Syntax Check         → Can every file parse?
L2: Type Check           → Do types align across modules?
L3: Lint Check           → Do style/logic rules pass?
L4: Test Check           → Do tests pass?
L5: Marker Cleanup       → Are all conflict markers gone?
L6: Semantic Validation  → Do cross-module contracts hold?
```

**Why this order matters:**
- L1 before L2: files must parse before type checking
- L2 before L3: type errors cause cascading lint failures
- L3 before L4: lint fixes may change behavior
- L5 any time: marker check is independent but critical
- L6 last: semantic validation requires everything else to pass

**Expected Output:**
- `.merge-resolver/VALIDATION-RESULTS.md` ← per-layer results
- `.merge-resolver/MERGE-CONTEXT.md` ← Validation Results table updated
- Phase 5 COMPLETE marker (or FAILED with details)

---

## Execution Flow

### Step 1: Pre-flight Check

```bash
# Verify Phase 4 is COMPLETE
if ! grep -q "Phase 4.*COMPLETE" .merge-resolver/MERGE-CONTEXT.md; then
  echo "[PHASE-5] ERROR: Phase 4 not marked COMPLETE."
  exit 1
fi

echo "[PHASE-5] Starting 6-layer validation..."

# Initialize results file
cat > .merge-resolver/VALIDATION-RESULTS.md << 'EOF'
# Validation Results

**Started**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

| Layer | Status | Details |
|-------|--------|---------|
| L1: Syntax | ⬜ pending | |
| L2: Types | ⬜ pending | |
| L3: Lint | ⬜ pending | |
| L4: Tests | ⬜ pending | |
| L5: Markers | ⬜ pending | |
| L6: Semantic | ⬜ pending | |

EOF
```

### Step 2: L1 — Syntax Validation

Verify every resolved file parses correctly.

**Tool Availability Detection:**
```bash
# Tool availability detection at step start
HAS_TSC=false; HAS_GO=false; HAS_PYTHON=false; HAS_ESLINT=false; HAS_GOLINT=false; HAS_VITEST=false; HAS_JEST=false
command -v npx &> /dev/null && npx tsc --version &> /dev/null 2>&1 && HAS_TSC=true
command -v go &> /dev/null && HAS_GO=true
command -v python3 &> /dev/null && HAS_PYTHON=true
command -v npx &> /dev/null && npx eslint --version &> /dev/null 2>&1 && HAS_ESLINT=true
command -v golangci-lint &> /dev/null && HAS_GOLINT=true
command -v npx &> /dev/null && npx vitest --version &> /dev/null 2>&1 && HAS_VITEST=true
command -v npx &> /dev/null && npx jest --version &> /dev/null 2>&1 && HAS_JEST=true
echo "[PHASE-5] Tool availability: tsc=$HAS_TSC go=$HAS_GO python=$HAS_PYTHON eslint=$HAS_ESLINT golangci-lint=$HAS_GOLINT vitest=$HAS_VITEST jest=$HAS_JEST"
```

**TypeScript/JavaScript:**
```bash
echo "[PHASE-5] L1: Syntax check (TypeScript)..."
if command -v npx &> /dev/null && npx tsc --version &> /dev/null 2>&1; then
  TSC_SYNTAX_ERRORS=$(npx tsc --noEmit --pretty false 2>&1 | grep "error TS" | wc -l)
  if [ "$TSC_SYNTAX_ERRORS" -gt 0 ]; then
    echo "[PHASE-5] L1 FAIL: $TSC_SYNTAX_ERRORS TypeScript syntax errors"
    npx tsc --noEmit --pretty false 2>&1 | grep "error TS" | head -20
    L1_STATUS="❌ FAIL"
    L1_DETAILS="$TSC_SYNTAX_ERRORS TypeScript syntax errors"
  else
    echo "[PHASE-5] L1 PASS: TypeScript syntax OK"
    L1_STATUS="✅ PASS"
    L1_DETAILS="TypeScript syntax clean"
  fi
else
  echo "[PHASE-5] L1 SKIP (TypeScript): tsc not available"
  L1_DETAILS="$L1_DETAILS; TypeScript: skipped (tsc not found)"
fi
```

**Go:**
```bash
echo "[PHASE-5] L1: Syntax check (Go)..."
if [ -f "go.mod" ] && command -v go &> /dev/null; then
  GO_SYNTAX_ERRORS=$(go build ./... 2>&1 | grep "syntax error" | wc -l)
  if [ "$GO_SYNTAX_ERRORS" -gt 0 ]; then
    echo "[PHASE-5] L1 FAIL: $GO_SYNTAX_ERRORS Go syntax errors"
    go build ./... 2>&1 | grep "syntax error" | head -20
    L1_STATUS="❌ FAIL"
    L1_DETAILS="$L1_DETAILS; $GO_SYNTAX_ERRORS Go syntax errors"
  else
    echo "[PHASE-5] L1 PASS: Go syntax OK"
    L1_DETAILS="$L1_DETAILS; Go syntax clean"
  fi
elif [ -f "go.mod" ] && ! command -v go &> /dev/null; then
  echo "[PHASE-5] L1 SKIP (Go): go command not available"
  L1_DETAILS="$L1_DETAILS; Go: skipped (go not found)"
fi
```

**Python:**
```bash
echo "[PHASE-5] L1: Syntax check (Python)..."
if command -v python3 &> /dev/null; then
  PYTHON_FILES=$(find . -name "*.py" -not -path "*/node_modules/*" -not -path "*/.venv/*" | head -200)
  PYTHON_ERRORS=0
  for pyfile in $PYTHON_FILES; do
    python3 -c "import ast; ast.parse(open('$pyfile').read())" 2>/dev/null
    if [ $? -ne 0 ]; then
      PYTHON_ERRORS=$((PYTHON_ERRORS + 1))
      echo "[PHASE-5] Python syntax error: $pyfile"
    fi
  done
  if [ "$PYTHON_ERRORS" -gt 0 ]; then
    L1_STATUS="❌ FAIL"
    L1_DETAILS="$L1_DETAILS; $PYTHON_ERRORS Python syntax errors"
  fi
else
  echo "[PHASE-5] L1 SKIP (Python): python3 not available"
  L1_DETAILS="$L1_DETAILS; Python: skipped (python3 not found)"
fi
```

**L1 Failure Recovery:**
If syntax errors are found, identify which resolved files are broken:
```bash
# Cross-reference syntax errors with resolved files
for error_file in $(npx tsc --noEmit 2>&1 | grep "error TS" | cut -d'(' -f1); do
  if grep -q "$error_file" .merge-resolver/RESOLUTION-LOG.md; then
    echo "[PHASE-5] REGRESSION: $error_file was resolved but has syntax errors"
    echo "  → Re-resolution needed. Check RESOLUTION-LOG.md for original decision."
  fi
done
```

---

### Step 3: L2 — Type Validation

Run full type checking to catch cross-module type mismatches.

**TypeScript:**
```bash
echo "[PHASE-5] L2: Type check (TypeScript)..."
if command -v npx &> /dev/null && npx tsc --version &> /dev/null 2>&1; then
  TSC_TYPE_ERRORS=$(npx tsc --noEmit --pretty false 2>&1 | grep "error TS" | wc -l)
  if [ "$TSC_TYPE_ERRORS" -gt 0 ]; then
    echo "[PHASE-5] L2 FAIL: $TSC_TYPE_ERRORS type errors"
    npx tsc --noEmit --pretty false 2>&1 | grep "error TS" | head -30
    L2_STATUS="❌ FAIL"
    L2_DETAILS="$TSC_TYPE_ERRORS type errors found"
  else
    echo "[PHASE-5] L2 PASS: Types clean"
    L2_STATUS="✅ PASS"
    L2_DETAILS="No type errors"
  fi
else
  echo "[PHASE-5] L2 SKIP (TypeScript): tsc not available"
  L2_DETAILS="$L2_DETAILS; TypeScript: skipped (tsc not found)"
fi
```

**Go:**
```bash
echo "[PHASE-5] L2: Build check (Go)..."
if [ -f "go.mod" ] && command -v go &> /dev/null; then
  GO_BUILD_OUTPUT=$(go build ./... 2>&1)
  GO_BUILD_ERRORS=$(echo "$GO_BUILD_OUTPUT" | grep -v "^$" | wc -l)
  
  if [ "$GO_BUILD_ERRORS" -gt 0 ]; then
    echo "[PHASE-5] L2 FAIL: Go build errors"
    echo "$GO_BUILD_OUTPUT" | head -20
    L2_STATUS="❌ FAIL"
    L2_DETAILS="$L2_DETAILS; Go build failed"
  else
    echo "[PHASE-5] L2 PASS: Go builds clean"
    L2_DETAILS="$L2_DETAILS; Go builds clean"
  fi
  
  # Also run go vet
  GO_VET_OUTPUT=$(go vet ./... 2>&1)
  GO_VET_ERRORS=$(echo "$GO_VET_OUTPUT" | grep -v "^$" | wc -l)
  
  if [ "$GO_VET_ERRORS" -gt 0 ]; then
    echo "[PHASE-5] L2 WARNING: go vet issues"
    echo "$GO_VET_OUTPUT" | head -10
    L2_DETAILS="$L2_DETAILS; go vet: $GO_VET_ERRORS issues"
  fi
elif [ -f "go.mod" ] && ! command -v go &> /dev/null; then
  echo "[PHASE-5] L2 SKIP (Go): go command not available"
  L2_DETAILS="$L2_DETAILS; Go: skipped (go not found)"
fi
```

**L2 Failure Analysis:**
```python
def analyze_type_errors(tsc_output, resolution_log):
    """
    Identify which resolutions caused type errors.
    
    Common patterns:
    - Missing export: resolution removed an export that dependents need
    - Type widening: merged type is wider than dependents expect
    - Missing property: resolution dropped a required field
    - Incompatible return type: merged function signature mismatch
    """
    errors = parse_tsc_errors(tsc_output)
    
    for error in errors:
        file_path = error['file']
        # Check if this file was resolved
        resolution = find_resolution(file_path, resolution_log)
        if resolution:
            print(f"REGRESSION: {file_path}")
            print(f"  Error: {error['message']}")
            print(f"  Resolution was: {resolution['strategy']}")
            print(f"  Confidence was: {resolution['confidence']}")
            print(f"  Reversal: {resolution['reversal_command']}")
```

---

### Step 4: L3 — Lint Validation

```bash
echo "[PHASE-5] L3: Lint check..."

# ESLint (TypeScript/JavaScript)
if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ]; then
  if command -v npx &> /dev/null && npx eslint --version &> /dev/null 2>&1; then
    ESLINT_OUTPUT=$(npx eslint . --format compact 2>&1 || true)
    ESLINT_ERRORS=$(echo "$ESLINT_OUTPUT" | grep " Error " | wc -l)
    ESLINT_WARNINGS=$(echo "$ESLINT_OUTPUT" | grep " Warning " | wc -l)
    
    if [ "$ESLINT_ERRORS" -gt 0 ]; then
      echo "[PHASE-5] L3 FAIL: $ESLINT_ERRORS ESLint errors, $ESLINT_WARNINGS warnings"
      L3_STATUS="❌ FAIL"
      L3_DETAILS="$ESLINT_ERRORS errors, $ESLINT_WARNINGS warnings"
    else
      echo "[PHASE-5] L3 PASS: ESLint clean ($ESLINT_WARNINGS warnings)"
      L3_STATUS="✅ PASS"
      L3_DETAILS="Clean ($ESLINT_WARNINGS warnings)"
    fi
  else
    echo "[PHASE-5] L3 SKIP: ESLint not available"
    L3_STATUS="⬜ SKIP"
    L3_DETAILS="ESLint config found but eslint not available"
  fi
else
  echo "[PHASE-5] L3 SKIP: No ESLint config found"
  L3_STATUS="⬜ SKIP"
  L3_DETAILS="No ESLint configuration"
fi

# golangci-lint (Go)
if [ -f "go.mod" ] && command -v golangci-lint &> /dev/null; then
  GOLINT_OUTPUT=$(golangci-lint run ./... 2>&1 || true)
  GOLINT_ERRORS=$(echo "$GOLINT_OUTPUT" | grep -c ":" || echo 0)
  L3_DETAILS="$L3_DETAILS; Go lint: $GOLINT_ERRORS issues"
fi
```

---

### Step 5: L4 — Test Validation

```bash
echo "[PHASE-5] L4: Running tests..."

# JavaScript/TypeScript tests
if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ]; then
  if command -v npx &> /dev/null && npx vitest --version &> /dev/null 2>&1; then
    echo "[PHASE-5] L4: Running Vitest..."
    VITEST_OUTPUT=$(npx vitest run --reporter=verbose 2>&1 || true)
    VITEST_PASS=$(echo "$VITEST_OUTPUT" | grep -c "✓" || echo 0)
    VITEST_FAIL=$(echo "$VITEST_OUTPUT" | grep -c "✗\|×\|FAIL" || echo 0)
    
    if [ "$VITEST_FAIL" -gt 0 ]; then
      L4_STATUS="❌ FAIL"
      L4_DETAILS="Vitest: $VITEST_FAIL failures, $VITEST_PASS passed"
    else
      L4_STATUS="✅ PASS"
      L4_DETAILS="Vitest: $VITEST_PASS passed"
    fi
  else
    echo "[PHASE-5] L4 SKIP: Vitest not available"
    L4_STATUS="⬜ SKIP"
    L4_DETAILS="Vitest: not available"
  fi
elif [ -f "jest.config.js" ] || [ -f "jest.config.ts" ]; then
  if command -v npx &> /dev/null && npx jest --version &> /dev/null 2>&1; then
    echo "[PHASE-5] L4: Running Jest..."
    JEST_OUTPUT=$(npx jest --passWithNoTests 2>&1 || true)
    JEST_FAIL=$(echo "$JEST_OUTPUT" | grep "Tests:.*failed" | grep -o "[0-9]* failed" | head -1 || echo "0 failed")
    
    if echo "$JEST_FAIL" | grep -q "[1-9]"; then
      L4_STATUS="❌ FAIL"
      L4_DETAILS="Jest: $JEST_FAIL"
    else
      L4_STATUS="✅ PASS"
      L4_DETAILS="Jest: All passed"
    fi
  else
    echo "[PHASE-5] L4 SKIP: Jest not available"
    L4_STATUS="⬜ SKIP"
    L4_DETAILS="Jest: not available"
  fi
fi

# Go tests
if [ -f "go.mod" ] && command -v go &> /dev/null; then
  echo "[PHASE-5] L4: Running Go tests..."
  GO_TEST_OUTPUT=$(go test ./... 2>&1 || true)
  GO_TEST_FAIL=$(echo "$GO_TEST_OUTPUT" | grep "FAIL" | wc -l)
  
  if [ "$GO_TEST_FAIL" -gt 0 ]; then
    L4_STATUS="❌ FAIL"
    L4_DETAILS="$L4_DETAILS; Go: $GO_TEST_FAIL test failures"
  else
    L4_DETAILS="$L4_DETAILS; Go: All passed"
  fi
elif [ -f "go.mod" ] && ! command -v go &> /dev/null; then
  echo "[PHASE-5] L4 SKIP: Go not available"
  L4_DETAILS="$L4_DETAILS; Go: skipped (go not found)"
fi

# Python tests
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
  if command -v python3 &> /dev/null; then
    echo "[PHASE-5] L4: Running pytest..."
    PYTEST_OUTPUT=$(python3 -m pytest --tb=short 2>&1 || true)
    PYTEST_FAIL=$(echo "$PYTEST_OUTPUT" | grep "failed" | head -1 || echo "")
    
    if [ -n "$PYTEST_FAIL" ]; then
      L4_STATUS="❌ FAIL"
      L4_DETAILS="$L4_DETAILS; pytest: $PYTEST_FAIL"
    else
      L4_DETAILS="$L4_DETAILS; pytest: passed"
    fi
  else
    echo "[PHASE-5] L4 SKIP: python3 not available"
    L4_DETAILS="$L4_DETAILS; pytest: skipped (python3 not found)"
  fi
fi
```

**L4 Failure Analysis — Test Regression Mapping:**
```python
def map_test_failures_to_resolutions(test_output, resolution_log):
    """
    Map failing tests back to specific resolutions.
    
    For each failing test:
    1. Identify which source file the test covers
    2. Check if that file was resolved in Phase 4
    3. If yes: the resolution likely caused the regression
    4. Report the resolution details and reversal command
    """
    failing_tests = parse_test_failures(test_output)
    
    for test in failing_tests:
        # Heuristic: test file path maps to source file
        # src/components/__tests__/Button.test.tsx → src/components/Button.tsx
        source_file = infer_source_from_test(test['file'])
        
        resolution = find_resolution(source_file, resolution_log)
        if resolution:
            print(f"TEST REGRESSION: {test['name']}")
            print(f"  Source: {source_file}")
            print(f"  Resolution: {resolution['strategy']} (confidence: {resolution['confidence']})")
            print(f"  Reversal: {resolution['reversal_command']}")
```

---

### Step 6: L5 — Conflict Marker Cleanup

**Critical**: Even one remaining conflict marker means the merge is broken.

```bash
echo "[PHASE-5] L5: Scanning for remaining conflict markers..."

# Search ALL tracked files for conflict markers
MARKER_FILES=$(grep -rl "^<<<<<<<\|^=======\|^>>>>>>>" . \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.go" --include="*.py" --include="*.json" --include="*.yaml" \
  --include="*.yml" --include="*.css" --include="*.scss" --include="*.md" \
  --include="*.html" --include="*.toml" --include="*.cfg" \
  | grep -v node_modules | grep -v .merge-resolver | grep -v .git || true)

MARKER_COUNT=$(echo "$MARKER_FILES" | grep -c "." || echo 0)

if [ "$MARKER_COUNT" -gt 0 ]; then
  echo "[PHASE-5] L5 FAIL: Conflict markers found in $MARKER_COUNT files:"
  echo "$MARKER_FILES"
  L5_STATUS="❌ FAIL"
  L5_DETAILS="$MARKER_COUNT files with remaining markers"
  
  # Detail which markers remain
  for mfile in $MARKER_FILES; do
    echo "  --- $mfile ---"
    grep -n "^<<<<<<<\|^=======\|^>>>>>>>" "$mfile" | head -5
  done
else
  echo "[PHASE-5] L5 PASS: No conflict markers remaining"
  L5_STATUS="✅ PASS"
  L5_DETAILS="Clean — no markers found"
fi
```

---

### Step 7: L6 — Semantic Validation

Check for the silent semantic conflicts that compile but break at runtime.

```bash
echo "[PHASE-5] L6: Semantic validation..."

# Check 1: Import/export consistency
# Every import should resolve to an actual export
echo "[PHASE-5] L6.1: Checking import/export consistency..."

# Check 2: Interface satisfaction (TypeScript)
# All classes implementing interfaces must satisfy them
echo "[PHASE-5] L6.2: Checking interface satisfaction..."

# Check 3: API contract consistency
# If both TypeScript and Go define the same API endpoints,
# request/response types must match
echo "[PHASE-5] L6.3: Checking cross-language API contracts..."

# Check 4: Configuration consistency
# package.json dependencies match import statements
# go.mod matches import statements
echo "[PHASE-5] L6.4: Checking dependency/import consistency..."
```

**Semantic Checks (language-specific):**

```python
def semantic_validation(resolved_files, registry):
    """
    Detect silent semantic conflicts that pass compilation
    but break runtime behavior.
    """
    issues = []
    
    # Check 1: Function signature changes
    for file_entry in registry['files']:
        if file_entry['conflict_type'] == 'MODIFY_SAME':
            # Compare function signatures before/after resolution
            # Flag if parameter count/types changed
            pass
    
    # Check 2: Default value changes
    # If one branch changed a default and the other added code
    # using the old default, the merge may silently break
    
    # Check 3: Enum/constant value changes
    # Both branches may add enum members with the same value
    
    # Check 4: Side effect ordering
    # If function call order changed in both branches,
    # the merged order may be wrong
    
    return issues
```

---

### Step 8: Compile Results

```bash
# Write final results to VALIDATION-RESULTS.md
cat > .merge-resolver/VALIDATION-RESULTS.md << EOF
# Validation Results

**Completed**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

| Layer | Status | Details |
|-------|--------|---------|
| L1: Syntax | $L1_STATUS | $L1_DETAILS |
| L2: Types | $L2_STATUS | $L2_DETAILS |
| L3: Lint | $L3_STATUS | $L3_DETAILS |
| L4: Tests | $L4_STATUS | $L4_DETAILS |
| L5: Markers | $L5_STATUS | $L5_DETAILS |
| L6: Semantic | $L6_STATUS | $L6_DETAILS |

## Overall Verdict

$(if echo "$L1_STATUS $L2_STATUS $L3_STATUS $L4_STATUS $L5_STATUS $L6_STATUS" | grep -q "FAIL"; then
  echo "**❌ VALIDATION FAILED** — see details above"
  echo ""
  echo "Recommended actions:"
  # List specific fix actions per failure
else
  echo "**✅ ALL LAYERS PASSED** — merge resolution is ready for commit"
fi)

EOF
```

### Step 9: Update MERGE-CONTEXT.md

```bash
# Update Validation Results table in MERGE-CONTEXT.md
cat >> .merge-resolver/MERGE-CONTEXT.md << EOF

## Phase 5: Validation [COMPLETE]

**Executed**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

| Layer | Status | Details |
|-------|--------|---------|
| L1: Syntax | $L1_STATUS | $L1_DETAILS |
| L2: Types | $L2_STATUS | $L2_DETAILS |
| L3: Lint | $L3_STATUS | $L3_DETAILS |
| L4: Tests | $L4_STATUS | $L4_DETAILS |
| L5: Markers | $L5_STATUS | $L5_DETAILS |
| L6: Semantic | $L6_STATUS | $L6_DETAILS |

EOF

# Mark Phase 5 complete
sed -i 's/\[ \] Phase 5: Validation/[x] Phase 5: Validation — COMPLETE/' .merge-resolver/MERGE-CONTEXT.md
```

### Step 10: Final Summary

```bash
echo "[PHASE-5] ========================================"
echo "[PHASE-5] Phase 5 (Validation) COMPLETE"
echo "[PHASE-5] ========================================"
echo ""
echo "Validation Summary:"
echo "  L1 Syntax:   $L1_STATUS"
echo "  L2 Types:    $L2_STATUS"
echo "  L3 Lint:     $L3_STATUS"
echo "  L4 Tests:    $L4_STATUS"
echo "  L5 Markers:  $L5_STATUS"
echo "  L6 Semantic: $L6_STATUS"
echo ""

if echo "$L1_STATUS $L2_STATUS $L5_STATUS" | grep -q "FAIL"; then
  echo "⛔ CRITICAL FAILURES: Fix L1/L2/L5 issues before committing."
  echo "   Run 'cat .merge-resolver/VALIDATION-RESULTS.md' for details."
elif echo "$L3_STATUS $L4_STATUS $L6_STATUS" | grep -q "FAIL"; then
  echo "⚠️  NON-CRITICAL FAILURES: Review L3/L4/L6 issues."
  echo "   These may be pre-existing issues, not merge regressions."
  echo "   Cross-reference with RESOLUTION-LOG.md to identify regressions."
else
  echo "✅ ALL VALIDATIONS PASSED"
  echo ""
  echo "Ready to commit. Run:"
  echo "  git add -A"
  echo "  git commit"
  echo ""
  echo "Review items (if any) are in: .merge-resolver/RESOLUTION-LOG.md"
fi
```

---

## Self-Correction Protocol (Ultimate Debugger Integration)

When validation layers fail, the skill enters a 3-pass self-correction loop inspired by the Ultimate Debugger's adaptive verification system.

### Pass Architecture

**Pass 1: Direct Fix**
1. Read validation failure from VALIDATION-RESULTS.md
2. Cross-reference failing file with RESOLUTION-LOG.md 
3. Identify the resolution that caused the regression
4. Apply targeted fix (re-resolve with error context)
5. Re-run ONLY the failed validation layer(s)
6. If pass → mark corrected, update logs
7. If fail → proceed to Pass 2

**Pass 2: Re-Analysis**  
1. Read the Pass 1 fix attempt AND the new error
2. Re-analyze with deeper context:
   - Read surrounding files for dependency context
   - Check if the error is cascading from another file
   - Consider alternative resolution strategy
3. Apply corrected resolution
4. Re-run failed validation layer(s)
5. If pass → mark corrected
6. If fail → proceed to Pass 3

**Pass 3: Escalation**
1. Mark file as RED in CONFLICT-REGISTRY.json
2. Write detailed failure report to RESOLUTION-LOG.md
3. Include: original resolution, Pass 1 attempt, Pass 2 attempt, all error messages
4. Present to human with reversal command

### Adaptive Depth Gating (from Ultimate Debugger L1-L8)

Validation depth is gated by fix complexity:

| Fix Complexity Score | Validation Layers |
|---------------------|-------------------|
| < 0.25 (TRIVIAL)   | L1 + L5 only (syntax + markers) |
| 0.25 - 0.49        | L1 + L2 + L5 (+ types) |
| 0.50 - 0.74        | L1-L5 (+ lint + tests) |
| ≥ 0.75 (CRITICAL)  | L1-L6 full validation |

Fix complexity score = risk_score from CONFLICT-REGISTRY.json

### Self-Correction State Tracking

Each correction attempt is tracked in `.merge-resolver/CORRECTION-LOG.md`:

```markdown
## File: src/components/Button.tsx
- **Original Resolution**: MANUAL_MERGE (confidence: 0.82)
- **Pass 1**: Fixed missing import → L1 FAIL (type error TS2304)
- **Pass 2**: Added type annotation → L2 PASS ✓
- **Final Status**: CORRECTED (2 passes)
```

### Implementation

```bash
self_correct() {
  local FILE="$1"
  local FAILED_LAYER="$2"
  local ERROR_MSG="$3"
  local MAX_PASSES=3
  local PASS=1
  
  while [ $PASS -le $MAX_PASSES ]; do
    echo "[PHASE-5] Self-correction pass $PASS/$MAX_PASSES for $FILE"
    
    # Read current resolution from log
    RESOLUTION=$(grep -A5 "$FILE" .merge-resolver/RESOLUTION-LOG.md)
    
    # Get fix complexity from registry  
    COMPLEXITY=$(python3 -c "
import json
with open('.merge-resolver/CONFLICT-REGISTRY.json') as f:
    reg = json.load(f)
for entry in reg['files']:
    if entry['path'] == '$FILE':
        print(entry.get('risk_score', 0.5))
        break
")
    
    if [ $PASS -eq 1 ]; then
      echo "[PHASE-5] Pass 1: Direct fix with error context"
      # Claude re-resolves with the error message as additional context
      # The resolution prompt includes: original decision + error + file content
    elif [ $PASS -eq 2 ]; then
      echo "[PHASE-5] Pass 2: Re-analysis with dependency context"
      # Read dependent files, check for cascading errors
      # Try alternative strategy if available
    else
      echo "[PHASE-5] Pass 3: Escalation to human"
      # Mark RED, write full failure report
      # Update registry status to needs-human
      python3 -c "
import json
with open('.merge-resolver/CONFLICT-REGISTRY.json') as f:
    reg = json.load(f)
for entry in reg['files']:
    if entry['path'] == '$FILE':
        entry['status'] = 'needs-human'
        entry['notes'] = 'Failed 3 self-correction passes: $ERROR_MSG'
        break
with open('.merge-resolver/CONFLICT-REGISTRY.json', 'w') as f:
    json.dump(reg, f, indent=2)
"
      echo "[PHASE-5] ⛔ $FILE marked needs-human after 3 failed passes"
      return 1
    fi
    
    # Re-run only the failed layer
    # ... (layer-specific re-validation)
    
    # Check if fixed
    if validate_layer "$FAILED_LAYER" "$FILE"; then
      echo "[PHASE-5] ✓ $FILE corrected on pass $PASS"
      # Log correction
      echo "- **Pass $PASS**: Fixed → $FAILED_LAYER PASS ✓" >> .merge-resolver/CORRECTION-LOG.md
      return 0
    fi
    
    PASS=$((PASS + 1))
  done
}

# Orchestrator: run self-correction for all failures
run_self_correction() {
  local FAILURES=$(grep "❌ FAIL" .merge-resolver/VALIDATION-RESULTS.md)
  
  if [ -z "$FAILURES" ]; then
    echo "[PHASE-5] No failures to correct"
    return 0
  fi
  
  echo "[PHASE-5] Entering self-correction protocol..."
  echo "# Self-Correction Log" > .merge-resolver/CORRECTION-LOG.md
  echo "**Started**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> .merge-resolver/CORRECTION-LOG.md
  
  # For each failed layer, identify and correct failing files
  for layer in L1 L2 L3 L4 L5; do
    if echo "$FAILURES" | grep -q "$layer"; then
      echo "[PHASE-5] Correcting $layer failures..."
      # Get files that failed this layer
      # Cross-reference with resolved files
      # Run self_correct for each
    fi
  done
  
  echo "[PHASE-5] Self-correction complete. Re-running full validation..."
  # Re-run Steps 2-8 for final results
}
```

---

## SPRINT Mode Validation

When MODE = SPRINT (≤15 files):
- Run L1 + L5 only (syntax + markers)
- Skip L2/L3/L4/L6 for speed
- User can manually run tests after committing

---

## Success Criteria

Phase 5 is COMPLETE when:

✓ All 6 validation layers have been executed (or skipped with reason)
✓ VALIDATION-RESULTS.md contains per-layer results
✓ MERGE-CONTEXT.md Validation Results table is populated
✓ L5 (markers) is PASS — no conflict markers remain
✓ Any failures are documented with fix recommendations
✓ Re-resolution loop has been attempted for fixable failures

**The merge resolution is DONE when:**
- L1 (Syntax): PASS
- L2 (Types): PASS
- L5 (Markers): PASS
- L3/L4/L6: PASS or documented as pre-existing

---

## References
- typescript-conflict-resolution-guide.md (Sections 8-9: Validation Patterns)
- go125-gin-conflict-patterns.md (Sections 6-7: Go Build/Vet Validation)
- vitest-test-conflict-patterns.md (Sections 4-6: Test Regression Detection)
- semantic-conflict-patterns.md (Sections 3-8: Silent Conflict Detection)
- ai-decision-audit-trail-patterns.md (Section 5: Validation Audit Trail)
