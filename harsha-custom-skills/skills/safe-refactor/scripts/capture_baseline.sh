#!/usr/bin/env bash
# capture_baseline.sh — Run tests, capture metrics, create git checkpoint
# Usage: bash capture_baseline.sh [project-root] [test-command]
# Output: JSON to stdout

set -euo pipefail

PROJECT_ROOT="${1:-.}"
TEST_COMMAND="${2:-}"
cd "$PROJECT_ROOT"

if [ -z "$TEST_COMMAND" ]; then
    echo '{"error": "No test command provided. Usage: capture_baseline.sh [project-root] [test-command]"}' >&2
    exit 1
fi

# --- Create git checkpoint ---
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TAG_NAME="refactor-baseline-${TIMESTAMP}"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    # Check for clean working directory
    DIRTY=$(git status --porcelain 2>/dev/null)
    if [ -n "$DIRTY" ]; then
        echo '{"error": "Git working directory is not clean. Commit or stash changes first.", "dirty_files": "'"$(echo "$DIRTY" | head -10 | tr '\n' ';')"'"}' >&2
        exit 1
    fi
    git tag "$TAG_NAME" 2>/dev/null || true
    BASELINE_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
else
    TAG_NAME="none"
    BASELINE_COMMIT="not_a_git_repo"
fi

# --- Run tests and capture output ---
TEST_OUTPUT_FILE=$(mktemp)
TEST_EXIT_CODE=0

# Run the test command, capture output and exit code
eval "$TEST_COMMAND" > "$TEST_OUTPUT_FILE" 2>&1 || TEST_EXIT_CODE=$?

TEST_OUTPUT=$(cat "$TEST_OUTPUT_FILE")

# --- Parse test results ---
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0
PARSE_METHOD="regex"

# Try to extract counts based on common test output patterns
# Jest/Vitest pattern: "Tests: X passed, Y failed, Z total"
if echo "$TEST_OUTPUT" | grep -qE "(Tests|Test Suites):.*passed"; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ skipped' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ total' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PARSE_METHOD="jest-vitest"
# Pytest pattern: "X passed, Y failed, Z skipped" or "X passed in Ys"
elif echo "$TEST_OUTPUT" | grep -qE '[0-9]+ passed'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ skipped' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
    PARSE_METHOD="pytest"
# Go test pattern: "ok" or "FAIL" per package, "--- PASS/FAIL" per test
elif echo "$TEST_OUTPUT" | grep -qE '(--- PASS|--- FAIL|^ok |^FAIL)'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -cE '--- PASS' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -cE '--- FAIL' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -cE '--- SKIP' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
    PARSE_METHOD="go-test"
# Cargo test pattern: "test result: ok. X passed; Y failed; Z ignored"
elif echo "$TEST_OUTPUT" | grep -qE 'test result:'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ ignored' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
    PARSE_METHOD="cargo-test"
# RSpec pattern: "X examples, Y failures"
elif echo "$TEST_OUTPUT" | grep -qE '[0-9]+ examples?'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ examples?' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failures?' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ pending' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$((TOTAL - FAILED - SKIPPED))
    PARSE_METHOD="rspec"
# PHPUnit pattern: "OK (X tests, Y assertions)" or "Tests: X, Assertions: Y, Failures: Z"
elif echo "$TEST_OUTPUT" | grep -qE '(OK \([0-9]+ test|Tests: [0-9]+)'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ test' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE 'Failures: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE 'Skipped: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$((TOTAL - FAILED - SKIPPED))
    PARSE_METHOD="phpunit"
# dotnet test pattern: "Passed! - Failed: X, Passed: Y, Skipped: Z, Total: W"
elif echo "$TEST_OUTPUT" | grep -qE '(Passed!|Failed!).*Total:'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE 'Total: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE 'Passed: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE 'Failed: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE 'Skipped: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PARSE_METHOD="dotnet-test"
# Maven/Gradle JUnit pattern: "Tests run: X, Failures: Y, Errors: Z, Skipped: W"
elif echo "$TEST_OUTPUT" | grep -qE 'Tests run: [0-9]+'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE 'Tests run: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED_COUNT=$(echo "$TEST_OUTPUT" | grep -oE 'Failures: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    ERROR_COUNT=$(echo "$TEST_OUTPUT" | grep -oE 'Errors: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$((FAILED_COUNT + ERROR_COUNT))
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE 'Skipped: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$((TOTAL - FAILED - SKIPPED))
    PARSE_METHOD="junit"
# Mocha pattern: "X passing" "Y failing"
elif echo "$TEST_OUTPUT" | grep -qE '[0-9]+ passing'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passing' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failing' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ pending' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
    PARSE_METHOD="mocha"
else
    # Fallback: use exit code
    if [ "$TEST_EXIT_CODE" -eq 0 ]; then
        PASSED=1; TOTAL=1
        PARSE_METHOD="exit-code-only"
    else
        FAILED=1; TOTAL=1
        PARSE_METHOD="exit-code-only"
    fi
fi

# --- Line count ---
LOC=$(wc -l $(find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.kt" -o -name "*.rb" -o -name "*.php" -o -name "*.cs" \) 2>/dev/null | grep -v node_modules | grep -v vendor | grep -v target | grep -v __pycache__ | grep -v .venv | grep -v dist | grep -v build | head -500) 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")

# Cleanup
rm -f "$TEST_OUTPUT_FILE"

# --- Output JSON ---
cat <<EOF
{
  "baseline_tag": "$TAG_NAME",
  "baseline_commit": "$BASELINE_COMMIT",
  "test_exit_code": $TEST_EXIT_CODE,
  "tests_pass": $([ "$TEST_EXIT_CODE" -eq 0 ] && echo "true" || echo "false"),
  "total": $TOTAL,
  "passed": $PASSED,
  "failed": $FAILED,
  "skipped": $SKIPPED,
  "parse_method": "$PARSE_METHOD",
  "lines_of_code": $LOC,
  "timestamp": "$TIMESTAMP"
}
EOF
