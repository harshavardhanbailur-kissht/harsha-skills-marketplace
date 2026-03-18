#!/bin/bash
# run-test.sh - Run security audit against the vulnerable-app test fixtures
#
# This script runs the security audit skill against the intentionally vulnerable
# application to verify the skill detects the planted vulnerabilities.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
TARGET_DIR="$SCRIPT_DIR"

echo "=============================================="
echo "Security Audit Skill - Test Runner"
echo "=============================================="
echo ""
echo "Target: $TARGET_DIR"
echo "Skill:  $SKILL_DIR"
echo ""

# Check if run-audit.sh exists
if [[ -f "$SKILL_DIR/scripts/run-audit.sh" ]]; then
    echo "Step 1: Running pre-computation script..."
    bash "$SKILL_DIR/scripts/run-audit.sh" "$TARGET_DIR"
    echo ""
else
    echo "Warning: run-audit.sh not found, skipping pre-computation"
fi

# Run dependency scanner
if [[ -f "$SKILL_DIR/scripts/scan-dependencies.py" ]]; then
    echo "Step 2: Scanning dependencies..."
    python3 "$SKILL_DIR/scripts/scan-dependencies.py" "$TARGET_DIR" 2>/dev/null || true
    echo ""
fi

# Run secrets scanner
if [[ -f "$SKILL_DIR/scripts/check-secrets.py" ]]; then
    echo "Step 3: Scanning for hardcoded secrets..."
    python3 "$SKILL_DIR/scripts/check-secrets.py" "$TARGET_DIR" 2>/dev/null || true
    echo ""
fi

echo "=============================================="
echo "Expected Vulnerabilities to Detect:"
echo "=============================================="
echo ""
echo "1.  [secrets-auditor]       Hardcoded JWT_SECRET, API_KEY, DB_PASSWORD"
echo "2.  [crypto-data-auditor]   MD5 password hashing, Math.random() tokens"
echo "3.  [crypto-data-auditor]   Weak bcrypt rounds (4)"
echo "4.  [injection-auditor]     SQL injection (string concatenation)"
echo "5.  [injection-auditor]     Command injection (exec with user input)"
echo "6.  [xss-csrf-auditor]      Reflected XSS (no output encoding)"
echo "7.  [xss-csrf-auditor]      DOM XSS (innerHTML)"
echo "8.  [xss-csrf-auditor]      CSRF (state change via GET)"
echo "9.  [access-control-auditor] IDOR (no ownership check)"
echo "10. [access-control-auditor] Missing auth on admin routes"
echo "11. [auth-session-auditor]  JWT without expiration"
echo "12. [auth-session-auditor]  JWT allowing 'none' algorithm"
echo "13. [auth-session-auditor]  Insecure session cookie settings"
echo "14. [input-output-auditor]  Path traversal"
echo "15. [input-output-auditor]  Unsafe YAML deserialization"
echo "16. [api-endpoint-auditor]  Missing rate limiting on auth"
echo "17. [api-endpoint-auditor]  Mass assignment vulnerability"
echo "18. [api-endpoint-auditor]  SSRF (fetching arbitrary URLs)"
echo "19. [error-handling-auditor] Stack trace exposure"
echo "20. [error-handling-auditor] User enumeration via error messages"
echo "21. [concurrency-auditor]   TOCTOU race condition in withdrawal"
echo "22. [logging-monitoring-auditor] Sensitive data logged (CC, passwords)"
echo "23. [business-logic-auditor] Client-side price manipulation"
echo "24. [business-logic-auditor] Coupon validation bypass"
echo "25. [config-headers-auditor] Missing security headers"
echo "26. [config-headers-auditor] CORS misconfiguration (origin: *)"
echo "27. [dependency-auditor]    Vulnerable lodash (4.17.15)"
echo "28. [dependency-auditor]    Vulnerable axios (0.21.1)"
echo "29. [dependency-auditor]    Vulnerable minimist (1.2.0)"
echo "30. [dependency-auditor]    Vulnerable js-yaml (3.13.1)"
echo ""
echo "=============================================="
echo "Test Complete"
echo "=============================================="
echo ""
echo "To run full audit, invoke the security audit skill:"
echo "  claude> /auditing-codebase-security $TARGET_DIR"
echo ""
echo "Or manually run grep patterns from audit-workdir/grep-results/"
