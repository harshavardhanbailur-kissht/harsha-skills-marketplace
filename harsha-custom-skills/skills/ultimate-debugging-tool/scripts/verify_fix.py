#!/usr/bin/env python3
"""
Verify a bug fix with lightweight, targeted checks.

Performs fast verification without full codebase re-scan:
1. Syntax validation (language-aware: Python, JavaScript, TypeScript)
2. Basic static checks on modified code
3. Diff analysis to ensure fix addresses the bug
4. Optional: Run affected tests

Usage:
    python verify_fix.py <bug_id> [--manifest PATH] [--run-tests]

Example:
    python verify_fix.py B001
    python verify_fix.py B001 --run-tests
    python verify_fix.py B001 --run-tests --update-manifest
"""

import argparse
import ast
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

try:
    import yaml
except ImportError:
    print("❌ Error: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


def detect_language(file_path: Path) -> str:
    """
    Detect the programming language from file extension.

    Returns: 'python', 'javascript', 'typescript', or 'unknown'
    """
    suffix = file_path.suffix.lower()

    if suffix == '.py':
        return 'python'
    elif suffix in ('.js', '.jsx'):
        return 'javascript'
    elif suffix in ('.ts', '.tsx'):
        return 'typescript'
    else:
        return 'unknown'


class VerificationResult:
    """Container for verification results."""
    
    def __init__(self, bug_id: str):
        self.bug_id = bug_id
        self.passed = True
        self.checks: List[Dict[str, Any]] = []
        self.issues: List[str] = []
        self.confidence = 1.0
    
    def add_check(self, name: str, passed: bool, message: str = "",
                  duration_ms: int = 0, confidence_impact: float = 0.0):
        """Add a verification check result.

        confidence_impact is ALWAYS applied (even for passed+SKIPPED/BLOCKED).
        This prevents 100% confidence when checks couldn't actually run.
        """
        self.checks.append({
            "name": name,
            "passed": passed,
            "message": message,
            "duration_ms": duration_ms
        })
        if not passed:
            self.passed = False
            self.issues.append(f"{name}: {message}")
        # Always apply confidence impact — BLOCKED/SKIPPED checks reduce
        # confidence even though they don't fail the overall result
        if confidence_impact > 0:
            self.confidence -= confidence_impact
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON/YAML output."""
        return {
            "bug_id": self.bug_id,
            "verified": self.passed,
            "confidence": max(0.0, self.confidence),
            "checks": self.checks,
            "issues": self.issues,
            "timestamp": datetime.now().isoformat()
        }
    
    def to_concise_json(self) -> str:
        """Token-optimized JSON output for LLM consumption."""
        return json.dumps({
            "verified": self.passed,
            "issues": self.issues,
            "confidence": round(max(0.0, self.confidence), 2)
        }, separators=(',', ':'))


def verify_syntax(file_path: Path) -> Tuple[bool, str, int]:
    """
    Verify file syntax via language-specific checkers.

    - Python: Uses ast.parse()
    - JavaScript/JSX: Uses node --check
    - TypeScript/TSX: Uses npx tsc --noEmit, falls back to node --check
    - Other: Skipped with informational message

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    language = detect_language(file_path)
    suffix = file_path.suffix.lower()

    if language == 'python':
        try:
            content = file_path.read_text()
            ast.parse(content)
            duration = int((time.time() - start) * 1000)
            return True, "Syntax valid", duration
        except SyntaxError as e:
            duration = int((time.time() - start) * 1000)
            return False, f"Syntax error at line {e.lineno}: {e.msg}", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"Parse error: {str(e)}", duration

    elif language == 'javascript':
        try:
            result = subprocess.run(
                ["node", "--check", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = int((time.time() - start) * 1000)

            if result.returncode == 0:
                return True, "Syntax valid", duration
            else:
                error_msg = result.stderr.strip() or "Syntax error"
                return False, error_msg, duration
        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            return False, "Syntax check timed out", duration
        except FileNotFoundError:
            duration = int((time.time() - start) * 1000)
            return True, "node not available (skipped syntax check)", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"Syntax check error: {str(e)}", duration

    elif language == 'typescript':
        # Pre-check: if no node_modules anywhere up the tree, skip tsc entirely
        # This avoids a 60s timeout while npx tries to download typescript
        _ts_project_root = file_path.parent
        _has_node_modules = False
        for _ in range(10):
            if (_ts_project_root / "node_modules").exists():
                _has_node_modules = True
                break
            _parent = _ts_project_root.parent
            if _parent == _ts_project_root:
                break
            _ts_project_root = _parent

        if not _has_node_modules:
            # No node_modules → tsc will fail or npx will timeout downloading
            # node --check doesn't work for .ts/.tsx (type annotations = syntax error,
            # .tsx = ERR_UNKNOWN_FILE_EXTENSION), so return BLOCKED immediately
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: node_modules missing (tsc unavailable, L1+L2 skipped)", duration

        # node_modules exists — run tsc with reduced timeout
        try:
            result = subprocess.run(
                ["npx", "--package", "typescript", "tsc", "--noEmit", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = int((time.time() - start) * 1000)

            if result.returncode == 0:
                return True, "L2 Type check passed", duration
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or ""
                # Distinguish environment issues from real type errors
                if any(s in error_msg for s in [
                    "Cannot find module", "Could not find a declaration file",
                    "node_modules", "ENOENT", "npm ERR"
                ]):
                    return True, f"BLOCKED: Environment issue (missing deps) — {error_msg[:100]}", duration
                return False, f"L2 Type error: {error_msg[:200]}", duration
        except FileNotFoundError:
            # Fall back to node --check
            try:
                result = subprocess.run(
                    ["node", "--check", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                duration = int((time.time() - start) * 1000)

                if result.returncode == 0:
                    return True, "L1 Syntax valid (parsed as JavaScript — tsc unavailable)", duration
                else:
                    error_msg = result.stderr.strip() or "Syntax error"
                    return False, f"L1 Syntax error: {error_msg}", duration
            except FileNotFoundError:
                duration = int((time.time() - start) * 1000)
                return True, "BLOCKED: npx/node not available (L1+L2 skipped)", duration
            except Exception as e:
                duration = int((time.time() - start) * 1000)
                return False, f"L1 Syntax check error: {str(e)}", duration
        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            # Timeout usually means npx is installing — environment, not syntax
            return True, "BLOCKED: tsc timed out (likely installing/missing deps — not a syntax error)", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"L2 Type check error: {str(e)}", duration

    elif suffix in ('.json',):
        # JSON: validate with json.loads
        try:
            content = file_path.read_text()
            json.loads(content)
            duration = int((time.time() - start) * 1000)
            return True, "JSON syntax valid", duration
        except json.JSONDecodeError as e:
            duration = int((time.time() - start) * 1000)
            return False, f"JSON syntax error at line {e.lineno}: {e.msg}", duration

    elif suffix in ('.css', '.scss'):
        # CSS: basic brace/semicolon balance check
        try:
            content = file_path.read_text()
            open_count = content.count('{')
            close_count = content.count('}')
            duration = int((time.time() - start) * 1000)
            if open_count != close_count:
                return False, f"CSS brace mismatch: {open_count} open, {close_count} close", duration
            return True, "CSS basic syntax valid", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"CSS check error: {str(e)}", duration

    elif suffix in ('.html', '.htm'):
        # HTML: basic tag balance check
        try:
            content = file_path.read_text()
            duration = int((time.time() - start) * 1000)
            # Very basic: check for unclosed critical tags
            for tag in ['html', 'head', 'body', 'div', 'script']:
                opens = len(re.findall(f'<{tag}[\\s>]', content, re.IGNORECASE))
                closes = len(re.findall(f'</{tag}>', content, re.IGNORECASE))
                if opens > closes:
                    return False, f"HTML unclosed <{tag}> tag ({opens} open, {closes} close)", duration
            return True, "HTML basic syntax valid", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"HTML check error: {str(e)}", duration

    else:
        # Unknown file type — reduce confidence, don't silently pass
        duration = int((time.time() - start) * 1000)
        return True, f"SKIPPED: No syntax checker for .{file_path.suffix} files (confidence reduced)", duration


def verify_types(file_path: Path) -> Tuple[bool, str, int]:
    """
    L2: Project-level type check.

    - TypeScript: runs `npx tsc --noEmit` from project root (finds tsconfig.json)
    - Python: runs `python3 -m mypy <file>` if available
    - Other: skipped

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    language = detect_language(file_path)

    if language == 'typescript':
        # Find project root by walking up to tsconfig.json or package.json
        project_root = file_path.parent
        for _ in range(10):
            if (project_root / "tsconfig.json").exists():
                break
            if (project_root / "package.json").exists():
                break
            parent = project_root.parent
            if parent == project_root:
                break
            project_root = parent

        if not (project_root / "tsconfig.json").exists():
            duration = int((time.time() - start) * 1000)
            return True, "SKIPPED: No tsconfig.json found (L2 type check not applicable)", duration

        # Check if node_modules exists — if not, deps aren't installed
        if not (project_root / "node_modules").exists():
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: node_modules missing (run npm/pnpm/yarn install first)", duration

        try:
            result = subprocess.run(
                ["npx", "--package", "typescript", "tsc", "--noEmit"],
                capture_output=True, text=True, timeout=60,
                cwd=str(project_root)
            )
            duration = int((time.time() - start) * 1000)
            if result.returncode == 0:
                return True, "L2 Type check passed (project-level tsc --noEmit)", duration
            else:
                # Filter errors to only those in our changed file
                our_errors = []
                rel_path = str(file_path.relative_to(project_root))
                for line in (result.stdout + result.stderr).splitlines():
                    if rel_path in line:
                        our_errors.append(line.strip())
                if our_errors:
                    return False, f"L2 Type errors in changed file: {'; '.join(our_errors[:3])}", duration
                else:
                    return True, "L2 Type check: errors exist but not in changed file", duration
        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: tsc timed out (60s) — likely environment issue", duration
        except FileNotFoundError:
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: npx not found (L2 type check skipped)", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"L2 Type check error: {str(e)}", duration

    elif language == 'python':
        # Try mypy if available
        try:
            result = subprocess.run(
                ["python3", "-m", "mypy", "--ignore-missing-imports", str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            duration = int((time.time() - start) * 1000)
            if result.returncode == 0:
                return True, "L2 Type check passed (mypy)", duration
            else:
                errors = result.stdout.strip().splitlines()
                return False, f"L2 Type errors: {errors[0] if errors else 'unknown'}", duration
        except (FileNotFoundError, subprocess.TimeoutExpired):
            duration = int((time.time() - start) * 1000)
            return True, "SKIPPED: mypy not available (L2 type check skipped)", duration

    else:
        duration = int((time.time() - start) * 1000)
        return True, f"SKIPPED: No type checker for {language} files", duration


def verify_lint(file_path: Path) -> Tuple[bool, str, int]:
    """
    L3: Project-level lint check.

    - JS/TS: runs `npx eslint <file>` if eslint config exists
    - Python: runs `python3 -m ruff check <file>` or `python3 -m flake8 <file>`
    - Other: skipped

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    language = detect_language(file_path)

    if language in ('javascript', 'typescript'):
        # Find project root
        project_root = file_path.parent
        for _ in range(10):
            if (project_root / "package.json").exists():
                break
            parent = project_root.parent
            if parent == project_root:
                break
            project_root = parent

        # Check if eslint config exists
        eslint_configs = [
            ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", ".eslintrc.yml",
            ".eslintrc.yaml", ".eslintrc", "eslint.config.js", "eslint.config.mjs",
            "eslint.config.cjs", "eslint.config.ts",
        ]
        has_eslint = any((project_root / c).exists() for c in eslint_configs)
        # Also check package.json for eslintConfig
        if not has_eslint and (project_root / "package.json").exists():
            try:
                pkg = json.loads((project_root / "package.json").read_text())
                has_eslint = "eslintConfig" in pkg
            except Exception:
                pass

        if not has_eslint:
            duration = int((time.time() - start) * 1000)
            return True, "SKIPPED: No ESLint config found (L3 lint skipped)", duration

        if not (project_root / "node_modules").exists():
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: node_modules missing (eslint needs deps installed)", duration

        try:
            result = subprocess.run(
                ["npx", "eslint", "--no-error-on-unmatched-pattern", str(file_path)],
                capture_output=True, text=True, timeout=30,
                cwd=str(project_root)
            )
            duration = int((time.time() - start) * 1000)
            if result.returncode == 0:
                return True, "L3 Lint passed (eslint)", duration
            else:
                errors = (result.stdout + result.stderr).strip().splitlines()
                error_lines = [l for l in errors if "error" in l.lower()][:3]
                return False, f"L3 Lint errors: {'; '.join(error_lines) or errors[0] if errors else 'unknown'}", duration
        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: eslint timed out (30s)", duration
        except FileNotFoundError:
            duration = int((time.time() - start) * 1000)
            return True, "BLOCKED: npx not found (L3 lint skipped)", duration

    elif language == 'python':
        # Try ruff first (fast), then flake8
        for linter, cmd in [("ruff", ["python3", "-m", "ruff", "check", str(file_path)]),
                            ("flake8", ["python3", "-m", "flake8", str(file_path)])]:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=15
                )
                duration = int((time.time() - start) * 1000)
                if result.returncode == 0:
                    return True, f"L3 Lint passed ({linter})", duration
                else:
                    errors = result.stdout.strip().splitlines()[:3]
                    return False, f"L3 Lint errors ({linter}): {'; '.join(errors)}", duration
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        duration = int((time.time() - start) * 1000)
        return True, "SKIPPED: No Python linter available (ruff/flake8)", duration

    else:
        duration = int((time.time() - start) * 1000)
        return True, f"SKIPPED: No linter for {language} files", duration


def verify_no_obvious_issues(file_path: Path, bug_line: int) -> Tuple[bool, str, int]:
    """
    Quick static check for obvious issues around the bug location.

    Checks for:
    - Python: TODO/FIXME markers, debug print statements, HACK comments
    - JavaScript/TypeScript: console.log in debug context, @ts-ignore, @ts-nocheck
    - TypeScript: 'any' type usage

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    issues = []
    language = detect_language(file_path)

    try:
        content = file_path.read_text()
        lines = content.split('\n')

        # Check ±5 lines around the bug
        start_line = max(0, bug_line - 6)
        end_line = min(len(lines), bug_line + 5)
        context = lines[start_line:end_line]

        for i, line in enumerate(context):
            actual_line = start_line + i + 1

            # Universal checks
            if 'TODO' in line or 'FIXME' in line:
                issues.append(f"Line {actual_line}: Contains TODO/FIXME marker")

            # Python-specific checks
            if language == 'python':
                if 'print(' in line and 'debug' in line.lower():
                    issues.append(f"Line {actual_line}: Debug print statement")

                if line.strip().startswith('#') and 'hack' in line.lower():
                    issues.append(f"Line {actual_line}: Contains HACK comment")

            # JavaScript/TypeScript-specific checks
            elif language in ('javascript', 'typescript'):
                if 'console.log(' in line and 'debug' in line.lower():
                    issues.append(f"Line {actual_line}: Debug console.log statement")

                if '@ts-ignore' in line or '@ts-nocheck' in line:
                    issues.append(f"Line {actual_line}: TypeScript suppression marker (@ts-ignore/@ts-nocheck)")

                # TypeScript-specific: 'any' type usage is a code smell
                if language == 'typescript' and ': any' in line:
                    issues.append(f"Line {actual_line}: Loose 'any' type annotation")

        duration = int((time.time() - start) * 1000)

        if issues:
            return False, "; ".join(issues[:3]), duration  # Limit to 3 issues
        return True, "No obvious issues found", duration

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        return False, f"Check failed: {str(e)}", duration


def verify_fix_addresses_bug(bug: Dict, file_content: str) -> Tuple[bool, str, int]:
    """
    Verify that the fix appears to address the original bug.
    
    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()
    
    bug_line = bug.get("location", {}).get("line", 0)
    bug_desc = bug.get("description", "").lower()
    cwe = bug.get("cwe", "")
    
    lines = file_content.split('\n')
    if bug_line <= 0 or bug_line > len(lines):
        duration = int((time.time() - start) * 1000)
        return False, f"Bug line {bug_line} out of range", duration
    
    line_content = lines[bug_line - 1].lower()
    
    # Check for common fix patterns based on bug type
    fix_indicators = {
        "sql injection": ["parameterized", "?", "%s", "prepare", "bind"],
        "cwe-89": ["parameterized", "?", "%s", "prepare", "bind"],
        "xss": ["escape", "sanitize", "encode", "textcontent"],
        "cwe-79": ["escape", "sanitize", "encode"],
        "hardcoded": ["config", "env", "getenv", "secret"],
        "cwe-798": ["config", "env", "getenv"],
        "null": ["if ", "is not none", "is none", "?.", "??"],
        "injection": ["sanitize", "validate", "escape", "whitelist"],
    }
    
    # Check if any fix indicator is present
    found_fix = False
    for keyword, indicators in fix_indicators.items():
        if keyword in bug_desc or keyword == cwe.lower():
            for indicator in indicators:
                if indicator in line_content:
                    found_fix = True
                    break
    
    duration = int((time.time() - start) * 1000)
    
    if found_fix:
        return True, "Fix pattern detected", duration
    
    # If we can't detect a fix pattern, return uncertain (not failed)
    return True, "Unable to verify fix pattern (manual review recommended)", duration


# =============================================================================
# L5-L8: DEPTH-GATED VERIFICATION LEVELS
# =============================================================================

# Depth thresholds — must match fix_signal_analyzer.py DEPTH_THRESHOLDS
DEPTH_THRESHOLDS = {
    "L5_only": 0.25,
    "L5_L6": 0.50,
    "L5_L6_L7": 0.75,
    "full": 0.75,
}


def compute_required_levels(depth: float, severity: str) -> set:
    """
    Determine which L5-L8 levels to run based on verification depth and severity.

    Mirrors fix_signal_analyzer.py's determine_verification_levels().
    Severity overrides: critical → always L5-L8, high → always L5-L6.
    """
    levels = set()

    if depth >= DEPTH_THRESHOLDS["full"]:
        levels = {5, 6, 7, 8}
    elif depth >= DEPTH_THRESHOLDS["L5_L6"]:
        levels = {5, 6, 7}
    elif depth >= DEPTH_THRESHOLDS["L5_only"]:
        levels = {5, 6}
    elif depth > 0:
        levels = {5}

    # Severity overrides
    if severity == "critical":
        levels = {5, 6, 7, 8}
    elif severity == "high":
        levels |= {5, 6}

    return levels


def verify_regression(file_path: Path, bug_id: str) -> tuple:
    """
    L5: Regression test coverage check.

    Checks:
    1. Does a test file exist for the changed source file?
    2. Does any test reference this bug ID (regression test)?
    3. If tests exist, are they passing? (delegates to L4 run_affected_tests)

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    language = detect_language(file_path)
    stem = file_path.stem

    # Build test file patterns
    if language == 'python':
        test_patterns = [f"test_{stem}.py", f"{stem}_test.py"]
    elif language in ('javascript', 'typescript'):
        test_patterns = [
            f"{stem}.test.js", f"{stem}.test.ts", f"{stem}.test.tsx",
            f"{stem}.spec.js", f"{stem}.spec.ts", f"{stem}.spec.tsx",
        ]
    else:
        duration = int((time.time() - start) * 1000)
        return True, f"SKIPPED: No test conventions for {language} files", duration

    # Search for test files
    search_dirs = [
        file_path.parent,
        file_path.parent / "tests",
        file_path.parent / "__tests__",
        file_path.parent.parent / "tests",
        file_path.parent.parent / "__tests__",
    ]

    found_test = None
    for d in search_dirs:
        if not d.exists():
            continue
        for pat in test_patterns:
            candidate = d / pat
            if candidate.exists():
                found_test = candidate
                break
        if found_test:
            break

    duration = int((time.time() - start) * 1000)

    if not found_test:
        return True, f"SKIPPED: No test file found for {file_path.name} (no regression coverage)", duration

    # Check if test references the bug ID (dedicated regression test)
    try:
        test_content = found_test.read_text(errors='ignore')
        has_bug_ref = bug_id in test_content
        has_regression_marker = bool(re.search(
            r'regression|bug.?fix|previously.?failed|should.?not.?regress',
            test_content, re.IGNORECASE
        ))

        if has_bug_ref:
            return True, f"L5 Regression: Test {found_test.name} references {bug_id} (dedicated regression test)", duration
        elif has_regression_marker:
            return True, f"L5 Regression: Test {found_test.name} has regression markers", duration
        else:
            return True, f"L5 Regression: Test {found_test.name} exists (consider adding regression test for {bug_id})", duration
    except Exception:
        return True, f"L5 Regression: Test {found_test.name} found but unreadable", duration


def verify_performance_check(file_path: Path, bug_line: int) -> tuple:
    """
    L6: Performance regression check.

    Checks for performance anti-patterns introduced by the fix:
    1. Nested iterations (O(n²))
    2. Expensive operations in potential hot paths
    3. Removed optimizations (memoization, lazy loading)
    4. Layout thrashing patterns
    5. Synchronous I/O in async context

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    suffix = file_path.suffix.lower()
    if suffix not in ['.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.py']:
        duration = int((time.time() - start) * 1000)
        return True, f"SKIPPED: Performance check not applicable for {suffix} files", duration

    try:
        content = file_path.read_text(errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        return False, f"L6 Performance: Could not read file: {e}", duration

    issues = []

    # Anti-patterns to detect in the fix area (±15 lines around bug)
    check_start = max(0, bug_line - 16)
    check_end = min(len(lines), bug_line + 15)
    check_lines = lines[check_start:check_end]
    check_block = '\n'.join(check_lines)

    # Pattern: Nested forEach/map (O(n²))
    if re.search(r'\.(?:forEach|map|filter|find)\s*\([^)]*\.(?:forEach|map|filter|find)', check_block):
        issues.append("Nested array iteration (O(n²) complexity)")

    # Pattern: JSON.parse(JSON.stringify()) deep clone
    if re.search(r'JSON\.parse\s*\(\s*JSON\.stringify', check_block):
        issues.append("Deep clone via JSON serialization (expensive)")

    # Pattern: RegExp construction in loop or render
    if re.search(r'(?:for|while|map|forEach|render|return)\s*[^}]*new\s+RegExp', check_block, re.DOTALL):
        issues.append("RegExp constructed in hot path")

    # Pattern: Synchronous DOM reads followed by writes (layout thrashing)
    if re.search(
        r'(?:offsetWidth|offsetHeight|clientWidth|clientHeight|getBoundingClientRect)'
        r'[^}]*\.style\.',
        check_block, re.DOTALL
    ):
        issues.append("Layout read → write pattern (forced reflow)")

    # Pattern: Missing cleanup in new useEffect
    if re.search(r'useEffect\s*\(\s*\(\)\s*=>\s*\{', check_block):
        if re.search(r'setInterval|addEventListener|subscribe', check_block):
            if not re.search(r'return\s*\(\s*\)\s*=>', check_block):
                issues.append("useEffect with subscription but no cleanup return")

    # Pattern: Unbounded data fetch without pagination
    if re.search(r'fetch\s*\([^)]*\)(?!.*limit|.*page|.*cursor|.*offset)', check_block, re.IGNORECASE):
        if re.search(r'\.then\s*\([^)]*=>.*setState|await.*set\w+\(', check_block, re.DOTALL):
            issues.append("Data fetch without visible pagination/limit")

    duration = int((time.time() - start) * 1000)

    if issues:
        return False, f"L6 Performance: {'; '.join(issues[:3])}", duration
    return True, "L6 Performance: No anti-patterns detected in fix area", duration


def verify_visual(file_path: Path, bug_line: int) -> tuple:
    """
    L7: Visual regression check.

    Tiered approach (tries best available, falls back gracefully):
    1. Component detection — is this a UI file?
    2. Jest snapshot tests — run if __snapshots__/ exists
    3. Structural CSS analysis — layout vs cosmetic property changes
    4. JSX structural analysis — conditional renders, className changes

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    suffix = file_path.suffix.lower()

    # === Step 1: Is this a UI component? ===
    is_ui_file = suffix in ['.jsx', '.tsx', '.css', '.scss', '.html', '.vue', '.svelte']

    if not is_ui_file and suffix in ['.js', '.ts']:
        try:
            content = file_path.read_text(errors='ignore')
            if re.search(r'return\s*\(?\s*<|React\.createElement|render\s*\(|\.jsx\b', content):
                is_ui_file = True
        except Exception:
            pass

    if not is_ui_file:
        duration = int((time.time() - start) * 1000)
        return True, "SKIPPED: Not a UI component (L7 visual not applicable)", duration

    # === Step 2: Jest snapshot tests ===
    snapshot_dir = file_path.parent / "__snapshots__"
    snap_candidates = []
    for ext in ['.test.tsx.snap', '.test.jsx.snap', '.test.js.snap',
                '.test.ts.snap', '.spec.tsx.snap', '.spec.js.snap']:
        snap_candidates.append(snapshot_dir / f"{file_path.stem}{ext}")

    found_snapshot = None
    for sc in snap_candidates:
        if sc.exists():
            found_snapshot = sc
            break

    if found_snapshot:
        # Derive the test file from the snapshot file name
        # e.g., __snapshots__/Button.test.tsx.snap → Button.test.tsx
        test_name = found_snapshot.name.replace('.snap', '')
        test_file = found_snapshot.parent.parent / test_name

        if test_file.exists():
            package_json = _find_package_json_for_visual(file_path)
            if package_json:
                try:
                    result = subprocess.run(
                        ["npx", "jest", str(test_file), "--ci", "--no-coverage"],
                        capture_output=True, text=True, timeout=30,
                        cwd=str(package_json.parent)
                    )
                    duration = int((time.time() - start) * 1000)
                    if result.returncode == 0:
                        return True, f"L7 Visual: Snapshot test passed ({test_file.name})", duration
                    else:
                        output = result.stdout + result.stderr
                        if 'snapshot' in output.lower() and ('obsolete' in output.lower() or 'written' in output.lower() or 'changed' in output.lower()):
                            return False, f"L7 Visual: Snapshot CHANGED — review visual diff in {test_file.name}", duration
                        return False, f"L7 Visual: Snapshot test failed ({test_file.name})", duration
                except subprocess.TimeoutExpired:
                    pass  # Fall through to structural analysis
                except FileNotFoundError:
                    pass  # npx not available, fall through

    # === Step 3: Structural CSS analysis ===
    if suffix in ['.css', '.scss']:
        try:
            content = file_path.read_text(errors='ignore')
            lines = content.split('\n')

            layout_props = {
                'width', 'height', 'margin', 'padding', 'top', 'left', 'right', 'bottom',
                'position', 'display', 'flex', 'grid', 'float', 'clear', 'overflow',
                'z-index', 'transform', 'min-width', 'max-width', 'min-height', 'max-height',
                'gap', 'grid-template', 'flex-direction', 'flex-wrap', 'align-items',
                'justify-content', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right',
                'padding-top', 'padding-bottom', 'padding-left', 'padding-right',
            }

            layout_changes = 0
            cosmetic_changes = 0

            check_range = range(max(0, bug_line - 10), min(len(lines), bug_line + 10))
            for i in check_range:
                line = lines[i].strip()
                prop_match = re.match(r'([\w-]+)\s*:', line)
                if prop_match:
                    prop = prop_match.group(1).lower()
                    if prop in layout_props:
                        layout_changes += 1
                    else:
                        cosmetic_changes += 1

            duration = int((time.time() - start) * 1000)
            if layout_changes > 0:
                return False, f"L7 Visual: {layout_changes} layout property change(s) near fix — visual review needed", duration
            elif cosmetic_changes > 0:
                return True, f"L7 Visual: Only cosmetic CSS changes detected ({cosmetic_changes} props)", duration
            return True, "L7 Visual: No layout-affecting CSS changes detected", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return True, f"L7 Visual: CSS analysis error: {e}", duration

    # === Step 4: JSX structural analysis ===
    if suffix in ['.jsx', '.tsx', '.js', '.ts']:
        try:
            content = file_path.read_text(errors='ignore')
            lines = content.split('\n')

            jsx_issues = []
            check_range = range(max(0, bug_line - 6), min(len(lines), bug_line + 6))
            for i in check_range:
                line = lines[i]
                # className or style prop changes
                if re.search(r'className\s*=|style\s*=\s*\{', line):
                    jsx_issues.append(f"Line {i+1}: className/style change")
                # Conditional rendering changes
                if re.search(r'return\s+null|&&\s*<|\?\s*<|\?\s*null|hidden|visible|display.*none', line):
                    jsx_issues.append(f"Line {i+1}: Conditional render/visibility change")
                # Component swap
                if re.search(r'<(?:div|span|section|article|main|header|footer|nav)\b', line):
                    if re.search(r'(?:hidden|aria-hidden|style=)', line):
                        jsx_issues.append(f"Line {i+1}: Element visibility change")

            duration = int((time.time() - start) * 1000)
            if jsx_issues:
                return False, f"L7 Visual: {'; '.join(jsx_issues[:2])} — visual review recommended", duration
            return True, "L7 Visual: No visual-impacting JSX patterns detected", duration
        except Exception:
            pass

    duration = int((time.time() - start) * 1000)
    return True, f"L7 Visual: UI file detected but no automated check available (manual review)", duration


def _find_package_json_for_visual(start_path: Path) -> Optional[Path]:
    """Find package.json walking up from start_path."""
    current = start_path.parent.resolve()
    for _ in range(10):
        pkg = current / "package.json"
        if pkg.exists():
            return pkg
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def verify_security_check(file_path: Path, bug: Dict) -> tuple:
    """
    L8: Security verification.

    Tiered approach:
    Tier 1 (always, zero deps): Dangerous pattern introduction check
    Tier 2 (always, zero deps): Exploit pattern persistence check (security bugs)
    Tier 3 (conditional): npm audit / pip-audit for dependency changes

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    issues = []

    try:
        content = file_path.read_text(errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        duration = int((time.time() - start) * 1000)
        return False, f"L8 Security: Could not read file: {e}", duration

    bug_line = bug.get("location", {}).get("line", 0)
    bug_cwe = bug.get("cwe", "")
    bug_desc = bug.get("description", "").lower()

    # === Tier 1: Dangerous pattern introduction check ===
    dangerous_patterns = {
        "eval()": r'\beval\s*\(',
        "Function() constructor": r'new\s+Function\s*\(',
        "innerHTML assignment": r'\.innerHTML\s*=',
        "shell=True": r'shell\s*=\s*True',
        "os.system()": r'os\.system\s*\(',
        "exec()": r'(?<!\.)exec\s*\(',
        "dangerouslySetInnerHTML": r'dangerouslySetInnerHTML',
        "__proto__ access": r'__proto__\s*[=\[]',
        "document.write": r'document\.write\s*\(',
        "pickle.loads": r'pickle\.loads?\s*\(',
        "yaml.load (unsafe)": r'yaml\.load\s*\([^)]*(?!Loader)[^)]*\)',
        "subprocess with string": r'subprocess\.\w+\s*\(\s*f["\']',
    }

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            continue
        # Skip test files — dangerous patterns are expected in tests
        if 'test' in file_path.stem.lower() or 'spec' in file_path.stem.lower():
            continue
        for name, pattern in dangerous_patterns.items():
            if re.search(pattern, line):
                issues.append(f"Line {line_num}: {name}")

    # === Tier 2: Exploit pattern persistence check ===
    is_security_bug = bool(
        bug_cwe or
        'security' in bug_desc or
        'injection' in bug_desc or
        'xss' in bug_desc or
        'auth' in bug_desc
    )

    if is_security_bug and bug_line > 0 and bug_line <= len(lines):
        vuln_patterns = {
            "CWE-89": [r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*\{', r'\.format\s*\([^)]*(?:SELECT|INSERT)'],
            "CWE-79": [r'\.innerHTML\s*=\s*[^"\'<]', r'dangerouslySetInnerHTML\s*=\s*\{\{.*__html\s*:\s*[^D]'],
            "CWE-798": [r'(?:password|api_key|secret|token)\s*=\s*["\'][^"\']{8,}["\']'],
            "CWE-78": [r'os\.system\s*\(\s*f["\']', r'subprocess.*shell\s*=\s*True.*(?:f["\']|\.format|\+\s*\w)'],
            "CWE-22": [r'open\s*\(\s*(?:request|user_input|params|args)'],
        }

        if bug_cwe in vuln_patterns:
            check_range = range(max(0, bug_line - 4), min(len(lines), bug_line + 4))
            for i in check_range:
                for vp in vuln_patterns[bug_cwe]:
                    if re.search(vp, lines[i], re.IGNORECASE):
                        issues.append(f"Line {i+1}: Original {bug_cwe} vulnerability pattern still present")
                        break

    # === Tier 3: Dependency audit ===
    if file_path.name in ('package.json', 'package-lock.json'):
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True, text=True, timeout=30,
                cwd=str(file_path.parent)
            )
            if result.returncode != 0:
                try:
                    audit = json.loads(result.stdout)
                    vulns = audit.get("metadata", {}).get("vulnerabilities", {})
                    critical = vulns.get("critical", 0)
                    high = vulns.get("high", 0)
                    if critical > 0 or high > 0:
                        issues.append(f"npm audit: {critical} critical, {high} high vulnerabilities")
                except (json.JSONDecodeError, KeyError):
                    pass
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    elif file_path.name in ('requirements.txt', 'Pipfile', 'pyproject.toml'):
        try:
            result = subprocess.run(
                ["python3", "-m", "pip_audit", "--format=json", "-r", str(file_path)],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                issues.append("pip-audit: Vulnerabilities found in Python dependencies")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    duration = int((time.time() - start) * 1000)

    if issues:
        # Deduplicate
        unique_issues = list(dict.fromkeys(issues))
        return False, f"L8 Security: {'; '.join(unique_issues[:3])}", duration
    return True, "L8 Security: No dangerous patterns or vulnerability persistence detected", duration


def find_package_json(start_path: Path) -> Optional[Path]:
    """Find package.json in start_path or any parent directory."""
    current = start_path.resolve()
    while current != current.parent:
        package_json = current / "package.json"
        if package_json.exists():
            return package_json
        current = current.parent
    return None


def detect_js_test_runner(package_json_path: Path) -> str:
    """
    Detect the JavaScript/TypeScript test runner from package.json.

    Returns: 'vitest', 'jest', or 'jest' (default)
    """
    try:
        import json
        content = package_json_path.read_text()
        package_json = json.loads(content)
        dev_deps = package_json.get("devDependencies", {})

        if "vitest" in dev_deps:
            return "vitest"
        elif "jest" in dev_deps:
            return "jest"
        else:
            return "jest"  # Default fallback
    except Exception:
        return "jest"  # Default fallback


def run_affected_tests(file_path: Path) -> Tuple[bool, str, int]:
    """
    Run tests that might be affected by changes to the file.

    Supports:
    - Python: pytest (test_*.py, *_test.py)
    - JavaScript/TypeScript: vitest or jest (*.test.js, *.spec.js, __tests__/*.test.js, etc.)

    Returns: (passed, message, duration_ms)
    """
    import time
    start = time.time()

    language = detect_language(file_path)

    # Try to find and run related tests
    if language == 'python':
        test_patterns = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"tests/test_{file_path.stem}.py",
            f"tests/{file_path.stem}_test.py",
        ]

        test_file = None
        for pattern in test_patterns:
            potential = file_path.parent / pattern
            if potential.exists():
                test_file = potential
                break
            potential = file_path.parent.parent / pattern
            if potential.exists():
                test_file = potential
                break

        if not test_file:
            duration = int((time.time() - start) * 1000)
            return True, "No related tests found", duration

        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            duration = int((time.time() - start) * 1000)

            if result.returncode == 0:
                return True, f"Tests passed: {test_file.name}", duration
            else:
                # Extract failure summary
                output = result.stdout + result.stderr
                if "FAILED" in output:
                    failed_count = output.count("FAILED")
                    return False, f"{failed_count} test(s) failed in {test_file.name}", duration
                return False, f"Test run failed: {test_file.name}", duration

        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            return False, "Tests timed out (>60s)", duration
        except FileNotFoundError:
            duration = int((time.time() - start) * 1000)
            return True, "pytest not available", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"Test error: {str(e)}", duration

    elif language in ('javascript', 'typescript'):
        # Find package.json to determine test runner
        package_json = find_package_json(file_path.parent)
        if not package_json:
            duration = int((time.time() - start) * 1000)
            return True, "package.json not found (skipped test discovery)", duration

        test_runner = detect_js_test_runner(package_json)

        # Test file patterns for JS/TS
        test_patterns = [
            f"__tests__/{file_path.stem}.test.js",
            f"__tests__/{file_path.stem}.test.ts",
            f"__tests__/{file_path.stem}.test.tsx",
            f"{file_path.stem}.test.js",
            f"{file_path.stem}.test.ts",
            f"{file_path.stem}.test.tsx",
            f"{file_path.stem}.spec.js",
            f"{file_path.stem}.spec.ts",
            f"{file_path.stem}.spec.tsx",
        ]

        test_file = None
        # Check in current directory and tests/ directory
        search_dirs = [file_path.parent, file_path.parent / "tests"]
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for pattern in test_patterns:
                potential = search_dir / pattern
                if potential.exists():
                    test_file = potential
                    break
            if test_file:
                break

        if not test_file:
            duration = int((time.time() - start) * 1000)
            return True, "No related tests found", duration

        try:
            if test_runner == "vitest":
                result = subprocess.run(
                    ["npx", "vitest", "run", "--reporter=verbose", str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=package_json.parent
                )
            else:  # jest
                result = subprocess.run(
                    ["npx", "jest", str(test_file), "--verbose"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=package_json.parent
                )

            duration = int((time.time() - start) * 1000)

            if result.returncode == 0:
                return True, f"Tests passed: {test_file.name}", duration
            else:
                output = result.stdout + result.stderr
                if "FAIL" in output or "failed" in output.lower():
                    failed_count = output.count("FAIL")
                    return False, f"{failed_count} test(s) failed in {test_file.name}", duration
                return False, f"Test run failed: {test_file.name}", duration

        except subprocess.TimeoutExpired:
            duration = int((time.time() - start) * 1000)
            return False, "Tests timed out (>60s)", duration
        except FileNotFoundError:
            duration = int((time.time() - start) * 1000)
            return True, "npx not available (test runner not found)", duration
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            return False, f"Test error: {str(e)}", duration

    else:
        # Unknown language
        duration = int((time.time() - start) * 1000)
        return True, f"Test discovery not supported for .{file_path.suffix} files", duration


def verify_fix(bug_id: str, manifest_path: Path, run_tests: bool = False,
               depth: float = 0.0, severity: str = "medium") -> VerificationResult:
    """
    Run verification checks for a specific bug fix.

    L1-L4: Always run (Mandatory Floor).
    L5-L8: Depth-gated based on verification_depth score from signal analyzer.

    Args:
        bug_id: The bug ID to verify
        manifest_path: Path to the bug manifest
        run_tests: Whether to run affected tests (L4)
        depth: Verification depth from signal analyzer (0.0-1.0)
        severity: Bug severity ('critical', 'high', 'medium', 'low')

    Returns:
        VerificationResult with all check results
    """
    result = VerificationResult(bug_id)
    
    # Load manifest
    if not manifest_path.exists():
        result.add_check("manifest", False, f"Manifest not found: {manifest_path}", 
                        confidence_impact=1.0)
        return result
    
    manifest = yaml.safe_load(manifest_path.read_text())
    
    # Find the bug
    bugs = manifest.get("bugs", [])
    bug = next((b for b in bugs if b["id"] == bug_id), None)
    
    if not bug:
        result.add_check("bug_lookup", False, f"Bug {bug_id} not found in manifest",
                        confidence_impact=1.0)
        return result
    
    # Get file info
    file_path = Path(bug.get("location", {}).get("file", ""))
    bug_line = bug.get("location", {}).get("line", 0)
    
    if not file_path.exists():
        result.add_check("file_exists", False, f"File not found: {file_path}",
                        confidence_impact=1.0)
        return result
    
    # === L1: Syntax validation ===
    passed, message, duration = verify_syntax(file_path)
    is_skipped = "SKIPPED:" in message or "BLOCKED:" in message
    conf_impact = 0.5 if not passed else (0.15 if is_skipped else 0)
    result.add_check("L1_syntax", passed, message, duration, conf_impact)

    if not passed and not is_skipped:
        # Don't continue if syntax is genuinely broken
        return result

    # === L2: Type check (project-level tsc/mypy) ===
    passed, message, duration = verify_types(file_path)
    is_skipped = "SKIPPED:" in message or "BLOCKED:" in message
    conf_impact = 0.3 if not passed else (0.10 if is_skipped else 0)
    result.add_check("L2_types", passed, message, duration, conf_impact)

    # === L3: Lint (eslint/ruff/flake8) ===
    passed, message, duration = verify_lint(file_path)
    is_skipped = "SKIPPED:" in message or "BLOCKED:" in message
    conf_impact = 0.2 if not passed else (0.05 if is_skipped else 0)
    result.add_check("L3_lint", passed, message, duration, conf_impact)

    # === L4: Tests ===
    if run_tests:
        passed, message, duration = run_affected_tests(file_path)
        result.add_check("L4_tests", passed, message, duration, 0.3 if not passed else 0)
    else:
        result.add_check("L4_tests", True, "SKIPPED: --run-tests not specified", 0, 0.05)

    # === Supplementary: Static heuristics + fix analysis (always run, lower weight) ===
    passed, message, duration = verify_no_obvious_issues(file_path, bug_line)
    result.add_check("heuristic_check", passed, message, duration, 0.05 if not passed else 0)

    file_content = file_path.read_text()
    passed, message, duration = verify_fix_addresses_bug(bug, file_content)
    result.add_check("fix_analysis", passed, message, duration, 0.1 if not passed else 0)

    # === Depth-gated L5-L8 ===
    required_levels = compute_required_levels(depth, severity)

    if 5 in required_levels:
        passed, message, duration = verify_regression(file_path, bug_id)
        is_skipped = "SKIPPED:" in message
        result.add_check("L5_regression", passed, message, duration,
                        0.15 if not passed and not is_skipped else (0.05 if is_skipped else 0))
    elif depth > 0:
        result.add_check("L5_regression", True,
                        "SKIPPED: Depth below L5 threshold (0.25)", 0, 0.0)

    if 6 in required_levels:
        passed, message, duration = verify_performance_check(file_path, bug_line)
        is_skipped = "SKIPPED:" in message
        result.add_check("L6_performance", passed, message, duration,
                        0.15 if not passed and not is_skipped else (0.05 if is_skipped else 0))
    elif depth > 0:
        result.add_check("L6_performance", True,
                        "SKIPPED: Depth below L6 threshold (0.50)", 0, 0.0)

    if 7 in required_levels:
        passed, message, duration = verify_visual(file_path, bug_line)
        is_skipped = "SKIPPED:" in message
        result.add_check("L7_visual", passed, message, duration,
                        0.10 if not passed and not is_skipped else (0.05 if is_skipped else 0))
    elif depth > 0:
        result.add_check("L7_visual", True,
                        "SKIPPED: Depth below L7 threshold (0.75)", 0, 0.0)

    if 8 in required_levels:
        passed, message, duration = verify_security_check(file_path, bug)
        is_skipped = "SKIPPED:" in message
        result.add_check("L8_security", passed, message, duration,
                        0.20 if not passed and not is_skipped else (0.05 if is_skipped else 0))
    elif depth > 0:
        result.add_check("L8_security", True,
                        "SKIPPED: Depth below L8 threshold (0.75)", 0, 0.0)

    return result


def update_manifest_status(bug_id: str, verified: bool, manifest_path: Path) -> bool:
    """Update bug status in manifest based on verification result."""
    try:
        manifest = yaml.safe_load(manifest_path.read_text())
        
        for bug in manifest.get("bugs", []):
            if bug["id"] == bug_id:
                if verified:
                    bug["status"] = "verified"
                    bug["verified_at"] = datetime.now().isoformat()
                else:
                    # Keep as 'fixed' but mark verification failed
                    bug["verification_failed"] = True
                    bug["verification_failed_at"] = datetime.now().isoformat()
                break
        
        # Update stats
        stats = manifest.get("stats", {})
        if verified:
            stats["verified"] = stats.get("verified", 0) + 1
            stats["fixed"] = max(0, stats.get("fixed", 0) - 1)
        manifest["stats"] = stats
        
        manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False))
        return True
        
    except Exception as e:
        print(f"❌ Error updating manifest: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Verify a bug fix with lightweight checks"
    )
    parser.add_argument("bug_id", help="Bug ID to verify (e.g., B001)")
    parser.add_argument("--manifest", "-m", default=".debug-session/bug-manifest.yaml",
                       help="Path to bug manifest")
    parser.add_argument("--run-tests", "-t", action="store_true",
                       help="Run affected tests as part of verification")
    parser.add_argument("--update-manifest", "-u", action="store_true",
                       help="Update manifest status based on result")
    parser.add_argument("--output", "-o", default="concise",
                       choices=["concise", "detailed"],
                       help="Output format")
    parser.add_argument("--depth", "-d", type=float, default=0.0,
                       help="Verification depth from signal analyzer (0.0-1.0). "
                            "Controls L5-L8: >=0.25→L5, >=0.50→L6+L7, >=0.75→L8")
    parser.add_argument("--severity", "-s", default="medium",
                       choices=["critical", "high", "medium", "low"],
                       help="Bug severity (critical/high override depth thresholds)")
    parser.add_argument("--full", action="store_true",
                       help="Force full L1-L8 verification (equivalent to --depth 1.0 --severity critical)")

    args = parser.parse_args()

    # --full overrides depth and severity
    if args.full:
        args.depth = 1.0
        args.severity = "critical"

    manifest_path = Path(args.manifest)

    levels_desc = ""
    if args.depth > 0:
        levels = compute_required_levels(args.depth, args.severity)
        if levels:
            level_names = {5: "Regression", 6: "Performance", 7: "Visual", 8: "Security"}
            levels_desc = f" + L{', L'.join(str(l) for l in sorted(levels))}"
    print(f"🔍 Verifying fix for {args.bug_id} (L1-L4{levels_desc})...", file=sys.stderr)

    result = verify_fix(args.bug_id, manifest_path, args.run_tests,
                       depth=args.depth, severity=args.severity)
    
    # Output results
    if args.output == "concise":
        print(result.to_concise_json())
    else:
        print(yaml.dump(result.to_dict(), default_flow_style=False))
    
    # Print summary to stderr
    if result.passed:
        print(f"\n✅ Verification PASSED (confidence: {result.confidence:.0%})", file=sys.stderr)
    else:
        print(f"\n❌ Verification FAILED", file=sys.stderr)
        for issue in result.issues:
            print(f"   - {issue}", file=sys.stderr)
    
    # Update manifest if requested
    if args.update_manifest:
        if update_manifest_status(args.bug_id, result.passed, manifest_path):
            print(f"📝 Manifest updated", file=sys.stderr)
    
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
