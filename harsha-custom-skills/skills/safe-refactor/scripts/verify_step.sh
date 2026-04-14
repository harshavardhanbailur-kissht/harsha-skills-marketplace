#!/usr/bin/env bash
# verify_step.sh — Run tests after a refactoring step, report pass/fail
# Usage: bash verify_step.sh [project-root] [test-command]
# Output: JSON to stdout
# Exit: 0 if tests pass, 1 if tests fail

set -euo pipefail

PROJECT_ROOT="${1:-.}"
TEST_COMMAND="${2:-}"
cd "$PROJECT_ROOT"

if [ -z "$TEST_COMMAND" ]; then
    echo '{"error": "No test command provided"}' >&2
    exit 1
fi

# --- Run tests ---
TEST_OUTPUT_FILE=$(mktemp)
TEST_EXIT_CODE=0
START_TIME=$(date +%s)

eval "$TEST_COMMAND" > "$TEST_OUTPUT_FILE" 2>&1 || TEST_EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

TEST_OUTPUT=$(cat "$TEST_OUTPUT_FILE")

# --- Parse results (same patterns as capture_baseline.sh) ---
TOTAL=0; PASSED=0; FAILED=0; SKIPPED=0

if echo "$TEST_OUTPUT" | grep -qE "(Tests|Test Suites):.*passed"; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ skipped' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ total' | tail -1 | grep -oE '[0-9]+' || echo "0")
elif echo "$TEST_OUTPUT" | grep -qE '[0-9]+ passed'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ skipped' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
elif echo "$TEST_OUTPUT" | grep -qE '(--- PASS|--- FAIL|^ok |^FAIL)'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -cE '--- PASS' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -cE '--- FAIL' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -cE '--- SKIP' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
elif echo "$TEST_OUTPUT" | grep -qE 'test result:'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ ignored' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
elif echo "$TEST_OUTPUT" | grep -qE '[0-9]+ examples?'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ examples?' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failures?' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ pending' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$((TOTAL - FAILED - SKIPPED))
elif echo "$TEST_OUTPUT" | grep -qE '(OK \([0-9]+ test|Tests: [0-9]+)'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ test' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE 'Failures: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE 'Skipped: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$((TOTAL - FAILED - SKIPPED))
elif echo "$TEST_OUTPUT" | grep -qE '(Passed!|Failed!).*Total:'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE 'Total: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE 'Passed: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE 'Failed: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE 'Skipped: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
elif echo "$TEST_OUTPUT" | grep -qE 'Tests run: [0-9]+'; then
    TOTAL=$(echo "$TEST_OUTPUT" | grep -oE 'Tests run: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FC=$(echo "$TEST_OUTPUT" | grep -oE 'Failures: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    EC=$(echo "$TEST_OUTPUT" | grep -oE 'Errors: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$((FC + EC))
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE 'Skipped: [0-9]+' | tail -1 | grep -oE '[0-9]+' || echo "0")
    PASSED=$((TOTAL - FAILED - SKIPPED))
elif echo "$TEST_OUTPUT" | grep -qE '[0-9]+ passing'; then
    PASSED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ passing' | tail -1 | grep -oE '[0-9]+' || echo "0")
    FAILED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failing' | tail -1 | grep -oE '[0-9]+' || echo "0")
    SKIPPED=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ pending' | tail -1 | grep -oE '[0-9]+' || echo "0")
    TOTAL=$((PASSED + FAILED + SKIPPED))
else
    if [ "$TEST_EXIT_CODE" -eq 0 ]; then PASSED=1; TOTAL=1;
    else FAILED=1; TOTAL=1; fi
fi

# --- Capture failure details if tests failed ---
FAILURE_SNIPPET=""
if [ "$TEST_EXIT_CODE" -ne 0 ]; then
    # Get last 20 lines of output for failure context
    FAILURE_SNIPPET=$(tail -20 "$TEST_OUTPUT_FILE" | sed 's/"/\\"/g' | tr '\n' '|' | head -c 500)
fi

rm -f "$TEST_OUTPUT_FILE"

# --- Output JSON ---
TESTS_PASS=$([ "$TEST_EXIT_CODE" -eq 0 ] && echo "true" || echo "false")

cat <<EOF
{
  "tests_pass": $TESTS_PASS,
  "exit_code": $TEST_EXIT_CODE,
  "total": $TOTAL,
  "passed": $PASSED,
  "failed": $FAILED,
  "skipped": $SKIPPED,
  "duration_seconds": $DURATION,
  "failure_snippet": "$FAILURE_SNIPPET"
}
EOF

# Exit with test result
exit $TEST_EXIT_CODE
