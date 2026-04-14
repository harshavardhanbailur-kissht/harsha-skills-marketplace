#!/usr/bin/env python3
"""
Scan code for bugs with token-optimized output.

Produces concise JSON output suitable for LLM processing while
maintaining full bug details in the manifest.

Uses contextual pattern matching with confidence scoring to minimize
false positives. Each detection requires multiple signals and meets
a minimum confidence threshold of 0.6.

Usage:
    python scan_bugs.py <path> [--category CATEGORY] [--output FORMAT]

Categories:
    security    - Auth, injection, secrets, XSS
    logic       - Null checks, boundaries, race conditions
    performance - N+1 queries, layout thrashing, scroll jank, CLS, React re-renders, Three.js
    quality     - Dead code, naming, complexity
    all         - Run all categories

Output formats:
    concise     - Minimal JSON for LLM chaining (default)
    detailed    - Full YAML for human review
    manifest    - Update bug-manifest.yaml directly

Example:
    python scan_bugs.py ./src --category security --output concise
    python scan_bugs.py ./src --category all --output manifest
"""

import argparse
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib

# Minimum confidence threshold for reporting bugs
MIN_CONFIDENCE = 0.6

# Bug category definitions with contextual patterns
CATEGORIES = {
    "security": {
        "name": "Security Vulnerabilities",
        "patterns": [
            {"id": "sqli", "cwe": "CWE-89", "desc": "SQL Injection", "min_conf": 0.7},
            {"id": "xss", "cwe": "CWE-79", "desc": "Cross-Site Scripting", "min_conf": 0.7},
            {"id": "hardcoded-secret", "cwe": "CWE-798", "desc": "Hardcoded Credentials", "min_conf": 0.8},
            {"id": "path-traversal", "cwe": "CWE-22", "desc": "Path Traversal", "min_conf": 0.7},
            {"id": "command-injection", "cwe": "CWE-78", "desc": "Command Injection", "min_conf": 0.75},
            {"id": "open-redirect", "cwe": "CWE-601", "desc": "Open Redirect", "min_conf": 0.75},
            {"id": "permissive-cors", "cwe": "CWE-942", "desc": "Permissive CORS", "min_conf": 0.75},
            {"id": "prototype-pollution", "cwe": "CWE-1321", "desc": "Prototype Pollution", "min_conf": 0.75},
            {"id": "nosql-injection", "cwe": "CWE-943", "desc": "NoSQL Injection", "min_conf": 0.75},
            {"id": "jwt-alg-none", "cwe": "CWE-347", "desc": "JWT Algorithm None", "min_conf": 0.75},
        ]
    },
    "logic": {
        "name": "Logic Errors",
        "patterns": [
            {"id": "null-deref", "desc": "Potential Null Dereference", "min_conf": 0.65},
            {"id": "off-by-one", "desc": "Off-by-One Error", "min_conf": 0.7},
            {"id": "race-condition", "desc": "Potential Race Condition", "min_conf": 0.7},
            {"id": "unhandled-exception", "desc": "Unhandled Exception", "min_conf": 0.65},
        ]
    },
    "performance": {
        "name": "Performance Issues",
        "patterns": [
            {"id": "n-plus-one", "desc": "N+1 Query Pattern", "min_conf": 0.7},
            {"id": "unbounded-list", "desc": "Unbounded Collection", "min_conf": 0.65},
            {"id": "expensive-loop", "desc": "Expensive Operation in Loop", "min_conf": 0.7},
            # P1: Animation & Rendering
            {"id": "layout-animation", "desc": "Animating layout properties (use transform)", "min_conf": 0.8},
            {"id": "layout-thrashing", "desc": "Layout thrashing: read then write", "min_conf": 0.7},
            {"id": "unthrottled-scroll", "desc": "Scroll handler without RAF throttling", "min_conf": 0.8},
            {"id": "non-passive-listener", "desc": "Non-passive touch/wheel listener", "min_conf": 0.85},
            # P2: JavaScript
            {"id": "missing-debounce", "desc": "Rapid-fire event without debounce/throttle", "min_conf": 0.65},
            # P3: React
            {"id": "inline-jsx-object", "desc": "Inline object/array in JSX props", "min_conf": 0.75},
            # P4: Three.js / WebGL
            {"id": "render-loop-alloc", "desc": "Object allocation in render/animation loop", "min_conf": 0.85},
            {"id": "uncapped-pixel-ratio", "desc": "Uncapped devicePixelRatio (cap at 2)", "min_conf": 0.9},
            # P6: Core Web Vitals
            {"id": "image-no-dimensions", "desc": "Image without width/height (causes CLS)", "min_conf": 0.8},
        ]
    },
    "quality": {
        "name": "Code Quality",
        "patterns": [
            {"id": "dead-code", "desc": "Potentially Dead Code", "min_conf": 0.6},
            {"id": "magic-number", "desc": "Magic Number", "min_conf": 0.65},
            {"id": "deep-nesting", "desc": "Deep Nesting", "min_conf": 0.65},
        ]
    },
    "web": {
        "name": "Web/React/Next.js Issues",
        "patterns": [
            {"id": "dangerous-html", "cwe": "CWE-79", "desc": "dangerouslySetInnerHTML usage", "min_conf": 0.7},
            {"id": "missing-cleanup", "desc": "useEffect without cleanup", "min_conf": 0.65},
            {"id": "stale-closure", "desc": "Stale closure in useEffect/useCallback", "min_conf": 0.65},
            {"id": "env-leak", "desc": "Server env exposed to client", "min_conf": 0.75},
            {"id": "ssr-window", "desc": "window/localStorage in SSR context", "min_conf": 0.7},
            {"id": "missing-key", "desc": "Missing key prop in list rendering", "min_conf": 0.65},
        ]
    }
}


def generate_bug_id(file_path: str, line: int, pattern_id: str) -> str:
    """Generate a unique, reproducible bug ID."""
    content = f"{file_path}:{line}:{pattern_id}"
    hash_val = hashlib.md5(content.encode()).hexdigest()[:6]
    return f"B{hash_val.upper()}"


def is_comment_or_string(line: str, col: int) -> bool:
    """Check if position is within a comment or string (basic check)."""
    # Simple heuristic: check if # comes before position
    hash_pos = line.find('#')
    if hash_pos != -1 and hash_pos < col:
        return True
    return False


def detect_sql_injection(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect SQL injection patterns.
    Requires BOTH query execution AND string interpolation/formatting.
    """
    confidence = 0.0

    # Check for query execution methods
    exec_patterns = [r'\.execute\s*\(', r'cursor\s*\.\s*execute', r'\.query\s*\(',
                     r'db\s*\.\s*query', r'\.execute\s*async']
    has_exec = any(re.search(p, line, re.IGNORECASE) for p in exec_patterns)

    if not has_exec:
        return 0.0

    # Check for dangerous string interpolation on same line or adjacent lines
    context = '\n'.join(lines[max(0, line_num-3):min(len(lines), line_num+2)])

    # Look for f-strings, format(), or % formatting with SELECT
    dangerous_patterns = [
        r'f["\']SELECT\s',
        r'f["\'][^"\']*\{[^}]*\}[^"\']*SELECT',
        r'\.format\s*\([^)]*SELECT',
        r'%\s*\(.*SELECT',
    ]
    has_interpolation = any(re.search(p, context, re.IGNORECASE) for p in dangerous_patterns)

    if has_interpolation:
        confidence = 0.85
    elif re.search(r'query.*=' if not has_interpolation else r'', line, re.IGNORECASE):
        confidence = 0.65

    return confidence


def detect_xss(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect XSS patterns in JavaScript/TypeScript files.
    Requires unsafe DOM manipulation AND user-controlled input.
    """
    confidence = 0.0

    # Check for unsafe DOM methods
    unsafe_methods = [r'\.innerHTML\s*=', r'document\.write\s*\(',
                      r'\.html\s*\(', r'insertAdjacentHTML']
    has_unsafe_dom = any(re.search(p, line, re.IGNORECASE) for p in unsafe_methods)

    if not has_unsafe_dom:
        return 0.0

    # Check if assignment comes from request/user input
    context = '\n'.join(lines[max(0, line_num-5):min(len(lines), line_num+1)])
    user_input_patterns = [r'req\s*\.\s*(query|body|params)', r'request\s*\[',
                          r'urlParams', r'queryString', r'\.getParameter']
    has_user_input = any(re.search(p, context) for p in user_input_patterns)

    if has_user_input:
        confidence = 0.85
    else:
        # Unsafe DOM method alone is medium confidence
        confidence = 0.65

    return confidence


def detect_hardcoded_secret(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect hardcoded secrets.
    Requires assignment of secret variable AND value assignment on same line.
    """
    confidence = 0.0

    # Check for secret variable names
    secret_patterns = [r'(password|api_key|secret|token|apikey|private_key|auth_token)\s*=',
                      r'(PASSWORD|API_KEY|SECRET|TOKEN|PRIVATE_KEY)\s*=']
    has_secret_var = any(re.search(p, line, re.IGNORECASE) for p in secret_patterns)

    if not has_secret_var:
        return 0.0

    # Check if value is hardcoded (not None, empty, or from environment/config)
    if re.search(r'=\s*(None|\'\'|""|\$|os\.environ|config\.|getenv)', line, re.IGNORECASE):
        return 0.2  # Likely not hardcoded

    # Check for actual hardcoded value
    if re.search(r'=\s*["\'][^"\']{4,}["\']', line):
        confidence = 0.9

    return confidence


def detect_path_traversal(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect path traversal.
    Requires file operation with user-supplied path.
    """
    confidence = 0.0

    # Check for file operations
    file_ops = [r'open\s*\(', r'\.read\s*\(', r'\.write\s*\(', r'os\.path',
               r'pathlib\.Path', r'\.open\s*\(']
    has_file_op = any(re.search(p, line) for p in file_ops)

    if not has_file_op:
        return 0.0

    # Check for traversal patterns or user input
    if re.search(r'["\']\.\./', line) or re.search(r'["\']\.\.\\', line):
        confidence = 0.9
    elif re.search(r'open\s*\(\s*(request|user|input|args|argv)', line, re.IGNORECASE):
        confidence = 0.8

    return confidence


def detect_command_injection(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect command injection.
    Requires shell execution AND string interpolation/user input.
    """
    confidence = 0.0

    # Check for shell execution
    shell_exec = [r'os\.system\s*\(', r'subprocess\s*\.\s*(call|run|Popen)',
                 r'shell\s*=\s*True', r'exec\s*\(']
    has_shell_exec = any(re.search(p, line) for p in shell_exec)

    if not has_shell_exec:
        return 0.0

    context = '\n'.join(lines[max(0, line_num-3):min(len(lines), line_num+2)])

    # Check for user input or string interpolation
    dangerous = [r'f["\'][^"\']*\{[^}]*\}', r'\.format\s*\(', r'%\s*\(',
                r'request|user|input|args']
    has_interpolation = any(re.search(p, context, re.IGNORECASE) for p in dangerous)

    if has_interpolation:
        confidence = 0.85
    else:
        confidence = 0.65

    return confidence


def detect_null_deref(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect potential null/None dereference.
    Requires .get() call immediately followed by attribute access without None check.
    """
    confidence = 0.0

    # Pattern: .get(...).something or .get(...)[something]
    dangerous = re.search(r'\.get\s*\([^)]*\)\s*[\.\[]', line)
    if not dangerous:
        return 0.0

    # Check if there's a None guard or try-except nearby
    context = '\n'.join(lines[max(0, line_num-2):min(len(lines), line_num+1)])

    if re.search(r'if\s+.*is\s+not\s+None|if\s+.*\:', context):
        return 0.3  # Likely guarded

    confidence = 0.8
    return confidence


def detect_off_by_one(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect off-by-one errors.
    Requires range/length check with suspicious indexing patterns.
    """
    confidence = 0.0

    # Check for range operations
    if not re.search(r'range\s*\(\s*len', line):
        return 0.0

    # Check for suspicious index operations nearby
    context = '\n'.join(lines[max(0, line_num-2):min(len(lines), line_num+3)])

    suspicious = [r'\[\s*i\s*\+\s*1\s*\]', r'\[\s*i\s*-\s*1\s*\]',
                 r'<\s*len\s*\(', r'<=\s*len\s*\(']

    if any(re.search(p, context) for p in suspicious):
        confidence = 0.75

    return confidence


def detect_race_condition(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect potential race conditions.
    Requires async/threading without synchronization primitives.
    """
    confidence = 0.0

    # Check for concurrency markers
    async_markers = [r'threading\s*\.', r'async\s+def', r'await\s+',
                    r'\.spawn\s*\(', r'Thread\s*\(']

    has_async = any(re.search(p, line) for p in async_markers)
    if not has_async:
        return 0.0

    # Check for lack of synchronization
    context = '\n'.join(lines[max(0, line_num-5):min(len(lines), line_num+5)])

    sync_primitives = [r'Lock\s*\(', r'Semaphore', r'\.acquire', r'\.release',
                      r'mutex', r'critical_section']
    has_sync = any(re.search(p, context) for p in sync_primitives)

    if not has_sync:
        confidence = 0.75
    else:
        confidence = 0.3

    return confidence


def detect_unhandled_exception(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect unhandled exceptions (bare except or pass).
    """
    confidence = 0.0

    # Bare except or except Exception with pass
    if re.search(r'except\s*:', line):
        if re.search(r'pass\s*$', line):
            confidence = 0.85
        else:
            confidence = 0.65

    return confidence


def detect_n_plus_one(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect N+1 query patterns.
    Requires BOTH loop construct AND database query on similar lines.
    """
    confidence = 0.0

    # Check for loop
    if not re.search(r'^\s*(for|while)\s+', line):
        return 0.0

    # Check context for DB operations
    context = '\n'.join(lines[max(0, line_num-1):min(len(lines), line_num+6)])

    db_patterns = [r'\.query\s*\(', r'\.filter\s*\(', r'\.execute\s*\(',
                  r'SELECT\s+', r'\.fetch\w*\s*\(',
                  r'\.objects\.get\s*\(', r'session\.get\s*\(', r'db\.get\s*\(']

    has_db = any(re.search(p, context, re.IGNORECASE) for p in db_patterns)

    if has_db:
        confidence = 0.8

    return confidence


def detect_unbounded_list(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect unbounded collection growth.
    Requires BOTH unbounded loop (while True) AND list growth operation.
    """
    confidence = 0.0

    # Check for while True or infinite loop
    if not re.search(r'while\s+True|while\s+1', line):
        return 0.0

    # Check context for append/grow operations
    context = '\n'.join(lines[min(len(lines), line_num):min(len(lines), line_num+10)])

    growth_ops = [r'\.append\s*\(', r'\.extend\s*\(', r'\.insert\s*\(',
                 r'\.add\s*\(', r'\+=\s*\[']

    if any(re.search(p, context) for p in growth_ops):
        confidence = 0.8

    return confidence


def detect_expensive_loop(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect expensive operations in loops.
    Requires BOTH loop AND expensive operation (not 'import').
    """
    confidence = 0.0

    # Check for loop
    if not re.search(r'^\s*(for|while)\s+', line):
        return 0.0

    # Check context for expensive operations
    context = '\n'.join(lines[max(0, line_num-1):min(len(lines), line_num+6)])

    expensive = [r'open\s*\(', r'requests\s*\.\s*\w+', r'subprocess\s*\.\s*(call|run)',
                r'time\s*\.sleep', r'\.read\s*\(', r'\.write\s*\(']

    if any(re.search(p, context) for p in expensive):
        confidence = 0.8

    return confidence


def detect_dead_code(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect potentially dead code markers.
    Requires explicit TODO/FIXME, not just pass statements.
    Supports Python (#), JS/TS (//), and block comment (/* */) syntax.
    """
    confidence = 0.0

    # Python-style comments: # TODO, # FIXME, etc.
    if re.search(r'#\s*(TODO|FIXME|XXX|HACK)\b', line):
        confidence = 0.7
    # JS/TS single-line comments: // TODO, // FIXME, etc.
    elif re.search(r'//\s*(TODO|FIXME|XXX|HACK)\b', line):
        confidence = 0.7
    # JS/TS block comments: /* TODO */, /** FIXME */
    elif re.search(r'/\*+\s*(TODO|FIXME|XXX|HACK)\b', line):
        confidence = 0.7
    elif re.search(r'^\s*\.\.\.\s*$', line):
        confidence = 0.65

    return confidence


def detect_magic_number(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect magic numbers (numeric literals without explanation).
    Requires numeric constant in comparison/assignment outside known patterns.
    """
    confidence = 0.0

    # Exclude common safe patterns
    if re.search(r'(range|len|count|size|width|height|timeout|port)\s*[=<>]', line, re.IGNORECASE):
        return 0.0

    # Look for suspicious magic numbers
    if re.search(r'==\s*\d{3,}|!=\s*\d{3,}|>\s*\d{3,}|<\s*\d{3,}', line):
        confidence = 0.7

    return confidence


def detect_deep_nesting(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect deep nesting (6+ levels) with noise filtering.
    Auto-detects indent width (2 or 4 spaces) from file context.
    Skips trivial lines (except/pass/return/break/continue/raise) to
    reduce false positives in Python try/except chains.
    """
    # Skip blank lines and trivial single-keyword lines
    stripped_content = line.strip()
    if not stripped_content:
        return 0.0
    # Skip lines that are just error handling / flow control boilerplate
    trivial_patterns = (
        'except', 'pass', 'return', 'break', 'continue', 'raise',
        'else:', 'elif ', 'finally:', 'except ', '} else {', '} catch',
        '} finally', '});', '})', '}', ')', '],',
    )
    if any(stripped_content.startswith(p) for p in trivial_patterns):
        return 0.0

    # Count leading spaces/tabs
    indent = len(line) - len(line.lstrip())
    if indent == 0:
        return 0.0

    # Auto-detect indent width from surrounding lines
    indent_width = 4  # default
    for nearby in lines[max(0, line_num-20):line_num+1]:
        stripped = len(nearby) - len(nearby.lstrip())
        if stripped == 2:
            indent_width = 2
            break

    nesting_level = indent // indent_width

    # Require 6+ nesting levels (raised from 5 to reduce noise)
    if nesting_level >= 6:
        confidence = 0.7 + (min(nesting_level - 6, 2) * 0.1)  # Cap at 0.9
        return confidence

    return 0.0


def detect_dangerous_html(line: str, line_num: int, lines: List[str]) -> float:
    """Detect dangerouslySetInnerHTML usage in React/JSX."""
    if re.search(r'dangerouslySetInnerHTML', line):
        # Check if there's sanitization nearby
        context = '\n'.join(lines[max(0, line_num-5):min(len(lines), line_num+3)])
        if re.search(r'DOMPurify|sanitize|xss|escape', context, re.IGNORECASE):
            return 0.5  # Sanitized — lower confidence
        return 0.85
    return 0.0


def detect_missing_cleanup(line: str, line_num: int, lines: List[str]) -> float:
    """Detect useEffect with subscriptions/timers but no cleanup return."""
    if not re.search(r'useEffect\s*\(', line):
        return 0.0
    # Look ahead for the effect body — find the matching closing
    body = '\n'.join(lines[line_num:min(len(lines), line_num + 20)])
    has_subscription = bool(re.search(
        r'addEventListener|setInterval|setTimeout|subscribe|\.on\(|WebSocket|EventSource',
        body
    ))
    has_cleanup = bool(re.search(r'return\s*\(\s*\)\s*=>|return\s*\(\s*\)\s*\{|return\s+function', body))
    if has_subscription and not has_cleanup:
        return 0.75
    return 0.0


def detect_stale_closure(line: str, line_num: int, lines: List[str]) -> float:
    """Detect likely stale closures in useEffect/useCallback with empty deps."""
    # Match useEffect(() => { ... }, [])  with empty dependency array
    if not re.search(r'(?:useEffect|useCallback)\s*\(', line):
        return 0.0
    body = '\n'.join(lines[line_num:min(len(lines), line_num + 15)])
    has_empty_deps = bool(re.search(r',\s*\[\s*\]\s*\)', body))
    # Check if body references state/props (indicators of stale closure)
    uses_state = bool(re.search(r'\b(?:set\w+|props\.\w+|state\.\w+)\b', body))
    if has_empty_deps and uses_state:
        return 0.70
    return 0.0


def detect_env_leak(line: str, line_num: int, lines: List[str]) -> float:
    """Detect server-side env vars leaking to client code."""
    # process.env without NEXT_PUBLIC_ prefix in client-facing files
    match = re.search(r'process\.env\.(\w+)', line)
    if not match:
        return 0.0
    env_var = match.group(1)
    # NEXT_PUBLIC_ and REACT_APP_ are designed for client exposure
    if env_var.startswith(('NEXT_PUBLIC_', 'REACT_APP_', 'VITE_')):
        return 0.0
    # Check if this is in a server file (OK)
    file_context = '\n'.join(lines[:5])
    if re.search(r"'use server'|getServerSideProps|getStaticProps", file_context):
        return 0.0
    return 0.80


def detect_ssr_window(line: str, line_num: int, lines: List[str]) -> float:
    """Detect direct window/document/localStorage access without SSR guard."""
    if not re.search(r'\b(?:window\.|document\.|localStorage\.|sessionStorage\.)', line):
        return 0.0
    # Check for SSR guard nearby
    context = '\n'.join(lines[max(0, line_num-5):min(len(lines), line_num+1)])
    has_guard = bool(re.search(
        r'typeof\s+window\s*[!=]==?\s*["\']undefined|typeof\s+document\s*[!=]==?\s*["\']undefined|useEffect|componentDidMount',
        context
    ))
    if has_guard:
        return 0.0
    return 0.70


def detect_missing_key(line: str, line_num: int, lines: List[str]) -> float:
    """Detect .map() in JSX without key prop."""
    if not re.search(r'\.map\s*\(\s*(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>', line):
        return 0.0
    # Look at the JSX returned — check next few lines for key=
    body = '\n'.join(lines[line_num:min(len(lines), line_num + 5)])
    has_map_jsx = bool(re.search(r'<\w+', body))
    has_key = bool(re.search(r'key\s*=', body))
    if has_map_jsx and not has_key:
        return 0.70
    return 0.0


def detect_layout_animation(line: str, line_num: int, lines: List[str]) -> float:
    """Detect CSS transitions/animations on layout properties (causes reflow)."""
    layout_props = r'(width|height|top|left|right|bottom|margin|padding)'
    if re.search(rf'transition\s*:[^;]*{layout_props}', line):
        return 0.90
    if re.search(rf'animation\s*:[^;]*{layout_props}', line):
        return 0.85
    return 0.0


def detect_layout_thrashing(line: str, line_num: int, lines: List[str]) -> float:
    """Detect read-then-write layout thrashing pattern."""
    read_props = r'(offsetWidth|offsetHeight|offsetTop|offsetLeft|clientWidth|clientHeight|getBoundingClientRect|scrollTop|scrollLeft|scrollWidth|scrollHeight)'
    if not re.search(read_props, line):
        return 0.0
    # Check if style write follows within 3 lines
    lookahead = '\n'.join(lines[line_num:min(len(lines), line_num + 4)])
    if re.search(r'\.style\.', lookahead):
        return 0.80
    return 0.0


def detect_unthrottled_scroll(line: str, line_num: int, lines: List[str]) -> float:
    """Detect scroll/resize handler without RAF or throttle."""
    if not re.search(r'addEventListener\s*\(\s*[\'"](?:scroll|resize)[\'"]', line):
        return 0.0
    context = '\n'.join(lines[max(0, line_num - 3):min(len(lines), line_num + 10)])
    if re.search(r'requestAnimationFrame|throttle|debounce|ticking|rafId', context, re.IGNORECASE):
        return 0.0
    return 0.85


def detect_non_passive_listener(line: str, line_num: int, lines: List[str]) -> float:
    """Detect touch/wheel listeners without passive: true."""
    if not re.search(r'addEventListener\s*\(\s*[\'"](?:touchstart|touchmove|wheel)[\'"]', line):
        return 0.0
    # Check same line and next line for passive
    context = '\n'.join(lines[line_num:min(len(lines), line_num + 3)])
    if re.search(r'passive\s*:\s*true', context):
        return 0.0
    return 0.95


def detect_missing_debounce(line: str, line_num: int, lines: List[str]) -> float:
    """Detect rapid-fire event handlers without debounce/throttle."""
    if not re.search(r'addEventListener\s*\(\s*[\'"](?:input|keyup|keydown|keypress|mousemove)[\'"]', line):
        return 0.0
    context = '\n'.join(lines[max(0, line_num - 3):min(len(lines), line_num + 10)])
    if re.search(r'debounce|throttle|setTimeout|requestAnimationFrame', context, re.IGNORECASE):
        return 0.0
    return 0.70


def detect_inline_jsx_object(line: str, line_num: int, lines: List[str]) -> float:
    """Detect inline object/array literals in JSX props (causes re-renders)."""
    # Match: <Component style={{...}} or options={{...}} or data={[...]}
    if re.search(r'<\w+[^>]*\s(?:style|options|config|data|columns|items)\s*=\s*\{\{', line):
        return 0.85
    if re.search(r'<\w+[^>]*\s(?:style|options|config|data|columns|items)\s*=\s*\{\[', line):
        return 0.85
    return 0.0


def detect_render_loop_alloc(line: str, line_num: int, lines: List[str]) -> float:
    """Detect object allocation inside render/animation loops (GC pressure)."""
    # Check if we're inside a render-loop-like function
    # Look backwards for function context
    lookback = '\n'.join(lines[max(0, line_num - 15):line_num + 1])
    in_loop = bool(re.search(
        r'function\s+(?:animate|render|update|tick|loop|draw|onFrame)\s*\(|'
        r'useFrame\s*\(\s*(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>|'
        r'requestAnimationFrame',
        lookback
    ))
    if not in_loop:
        return 0.0
    # Check for allocations on this line
    if re.search(r'new\s+(?:THREE\.)?(?:Vector[234]|Quaternion|Matrix[34]|Euler|Color|Box3|Sphere|Ray)', line):
        return 0.95
    if re.search(r'new\s+(?:Float32Array|Uint8Array|ArrayBuffer|Array)\s*\(', line):
        return 0.80
    return 0.0


def detect_uncapped_pixel_ratio(line: str, line_num: int, lines: List[str]) -> float:
    """Detect uncapped window.devicePixelRatio (causes GPU overload on 3x screens)."""
    if re.search(r'setPixelRatio\s*\(\s*window\.devicePixelRatio\s*\)', line):
        return 0.95
    if re.search(r'devicePixelRatio\s*\)', line) and not re.search(r'Math\.min|Math\.max|clamp', line):
        # Broader check — devicePixelRatio used without capping
        context = '\n'.join(lines[max(0, line_num - 1):min(len(lines), line_num + 2)])
        if not re.search(r'Math\.min|Math\.max|clamp|\?\s*\d', context):
            return 0.85
    return 0.0


def detect_image_no_dimensions(line: str, line_num: int, lines: List[str]) -> float:
    """Detect <img> tags without width/height (causes CLS)."""
    if not re.search(r'<img\s', line, re.IGNORECASE):
        return 0.0
    # Check this line and next 2 lines for the full tag
    tag_context = '\n'.join(lines[line_num:min(len(lines), line_num + 3)])
    # Find closing >
    close = tag_context.find('>')
    if close == -1:
        tag_context = line  # fall back to just this line
    else:
        tag_context = tag_context[:close + 1]
    has_width = bool(re.search(r'\bwidth\s*=', tag_context, re.IGNORECASE))
    has_height = bool(re.search(r'\bheight\s*=', tag_context, re.IGNORECASE))
    # Next.js Image component handles this automatically
    if re.search(r'<Image\s', line):
        return 0.0
    if has_width and has_height:
        return 0.0
    if has_width or has_height:
        return 0.7  # partial — still causes CLS
    return 0.90


def detect_open_redirect(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect open redirect vulnerabilities.
    Requires redirect call AND unsanitized user input.
    """
    # Primary signal: redirect patterns
    primary_signals = [
        r'res\.redirect\s*\(',
        r'window\.location\s*=',
        r'location\.href\s*=',
    ]
    has_redirect = any(re.search(p, line, re.IGNORECASE) for p in primary_signals)

    if not has_redirect:
        return 0.0

    # Check 3-line context for danger signals
    context = '\n'.join(lines[max(0, line_num - 2):min(len(lines), line_num + 2)])

    # Danger signals: user input sources
    danger_signals = [
        r'req\.query',
        r'req\.params',
        r'req\.body',
        r'searchParams',
    ]
    has_danger = any(re.search(p, context, re.IGNORECASE) for p in danger_signals)

    if not has_danger:
        return 0.0

    # Safe signal: allowlist/whitelist check nearby
    safe_signals = [
        r'whitelist',
        r'allowlist',
        r'ALLOWED_',
        r'approved',
        r'trusted',
    ]
    has_safe = any(re.search(p, context, re.IGNORECASE) for p in safe_signals)

    if has_safe:
        return 0.5  # Reduced confidence if safe check exists

    return 0.85


def detect_permissive_cors(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect permissive CORS configuration.
    Requires Access-Control-Allow-Origin header or cors middleware with '*' or true.
    """
    # Danger signal: wildcard or unrestricted origin on current line
    # Match header syntax: Access-Control-Allow-Origin: *
    if re.search(r"Access-Control-Allow-Origin\s*:\s*['\"]?\*['\"]?", line, re.IGNORECASE):
        return 0.85

    # Match function call syntax: res.setHeader('Access-Control-Allow-Origin', '*')
    # Also covers res.set(), res.header(), response.headers.set()
    if re.search(
        r"""(?:setHeader|\.set|\.header|headers\.set)\s*\(\s*['"]Access-Control-Allow-Origin['"]\s*,\s*['"]?\*['"]?\s*\)""",
        line, re.IGNORECASE
    ):
        return 0.85

    # Check multi-line context for CORS patterns with dangerous config
    context = '\n'.join(lines[max(0, line_num - 2):min(len(lines), line_num + 2)])

    # Check for cors({ origin: '*' }) or cors({ origin: true })
    if re.search(r"cors\s*\(\s*\{\s*origin\s*:\s*(?:['\"]?\*['\"]?|true)", context, re.IGNORECASE):
        return 0.80

    # Detect cors() with no config — defaults to origin: '*' in Express
    if re.search(r'app\.use\s*\(\s*cors\s*\(\s*\)\s*\)', context, re.IGNORECASE):
        return 0.75

    # Detect cors middleware import without any restrictive config nearby
    if re.search(r'cors\s*\(\s*\)', context, re.IGNORECASE):
        return 0.75

    return 0.0


def detect_prototype_pollution(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect prototype pollution vulnerabilities.
    Requires unsanitized user input assigned to object properties via bracket notation.
    """
    # Primary signal: bracket assignment with user input key
    user_input_patterns = [
        r'req\.body',
        r'req\.query',
        r'req\.params',
        r'params',
        r'input',
        r'data',
    ]

    # Check for direct bracket assignment: obj[key] = userInput
    if re.search(r'\[.*\]\s*=', line):
        context = '\n'.join(lines[max(0, line_num - 2):min(len(lines), line_num + 2)])
        if any(re.search(p, context) for p in user_input_patterns):
            return 0.80

    # Check for Object.assign or _.merge with user input
    # First check for the patterns with explicit user input
    assign_patterns = [
        r'Object\.assign\s*\(\s*\{\s*\}\s*,\s*(?:' + '|'.join(user_input_patterns) + ')',
        r'_\.merge\s*\([^,]*,\s*(?:' + '|'.join(user_input_patterns) + ')',
    ]
    if any(re.search(p, line) for p in assign_patterns):
        return 0.75

    # Also check for Object.assign({}, variable) where variable comes from user input
    context = '\n'.join(lines[max(0, line_num - 3):min(len(lines), line_num + 2)])
    if re.search(r'Object\.assign\s*\(\s*\{\s*\}\s*,\s*\w+\s*\)', line):
        # Check if this variable was assigned from user input
        if any(re.search(p, context) for p in user_input_patterns):
            return 0.75

    # Check for _.merge with variable
    if re.search(r'_\.merge\s*\([^,]+,\s*\w+\s*\)', line):
        if any(re.search(p, context) for p in user_input_patterns):
            return 0.75

    # Check for JSON.parse without schema validation
    if re.search(r'JSON\.parse\s*\(.*\)', context) and any(re.search(p, context) for p in user_input_patterns):
        return 0.75

    return 0.0


def detect_nosql_injection(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect NoSQL injection vulnerabilities.
    Requires NoSQL query with user-controlled operators like $where, $ne, etc.
    """
    # Primary signal: NoSQL methods
    primary_signals = [
        r'\.find\s*\(',
        r'\.findOne\s*\(',
        r'\.aggregate\s*\(',
        r'\.where\s*\(',
    ]
    has_nosql = any(re.search(p, line) for p in primary_signals)

    if not has_nosql:
        return 0.0

    # Check context for dangerous operators and user input
    context = '\n'.join(lines[max(0, line_num - 2):min(len(lines), line_num + 2)])

    # Danger signals: MongoDB operators
    dangerous_ops = [
        r'\$where',
        r'\$ne',
        r'\$gt',
        r'\$lt',
        r'\$in',
        r'\$regex',
    ]
    has_dangerous_op = any(re.search(p, context) for p in dangerous_ops)

    if not has_dangerous_op:
        return 0.0

    # Check for user input in same context
    user_input_patterns = [
        r'req\.query',
        r'req\.body',
        r'req\.params',
    ]
    has_user_input = any(re.search(p, context) for p in user_input_patterns)

    if not has_user_input:
        return 0.0

    # High confidence if $where with user input
    if re.search(r'\$where', context):
        return 0.85

    # Lower confidence for other operators
    return 0.80


def detect_jwt_alg_none(line: str, line_num: int, lines: List[str]) -> float:
    """
    Detect JWT signature verification bypasses.
    Requires jwt.verify without algorithms or with algorithm: 'none'.
    """
    # Danger signal 1: jwt.decode without verify (fast path)
    if re.search(r'jwt\.decode\s*\(', line) and not re.search(r'jwt\.verify\s*\(', line):
        return 0.80

    # Primary signal: jwt.verify
    primary_signal = r'jsonwebtoken\.verify\s*\(|jwt\.verify\s*\('
    if not re.search(primary_signal, line):
        return 0.0

    # Check multi-line context for algorithms parameter (±8 lines for multi-line jwt.verify calls)
    context = '\n'.join(lines[max(0, line_num - 8):min(len(lines), line_num + 8)])

    # Danger signal 2: algorithms: ['none'] or algorithm: 'none'
    if re.search(r'algorithms\s*:\s*\[[\'"]none[\'"]\]|algorithm\s*:\s*[\'"]none[\'"]', context, re.IGNORECASE):
        return 0.85

    # Danger signal 3: jwt.verify without algorithms parameter at all
    if re.search(primary_signal, line):
        # Check if algorithms parameter exists in context
        if not re.search(r'algorithms\s*:', context):
            return 0.75

    return 0.0


def check_pattern(pattern_id: str, line: str, line_num: int, lines: List[str],
                 file_ext: str) -> float:
    """
    Check a specific pattern and return confidence score.
    """
    if pattern_id == "sqli":
        return detect_sql_injection(line, line_num, lines)
    elif pattern_id == "xss":
        # Only check XSS in JS/TS files
        if file_ext not in ['.js', '.ts', '.jsx', '.tsx']:
            return 0.0
        return detect_xss(line, line_num, lines)
    elif pattern_id == "hardcoded-secret":
        return detect_hardcoded_secret(line, line_num, lines)
    elif pattern_id == "path-traversal":
        return detect_path_traversal(line, line_num, lines)
    elif pattern_id == "command-injection":
        return detect_command_injection(line, line_num, lines)
    elif pattern_id == "null-deref":
        return detect_null_deref(line, line_num, lines)
    elif pattern_id == "off-by-one":
        return detect_off_by_one(line, line_num, lines)
    elif pattern_id == "race-condition":
        return detect_race_condition(line, line_num, lines)
    elif pattern_id == "unhandled-exception":
        return detect_unhandled_exception(line, line_num, lines)
    elif pattern_id == "n-plus-one":
        return detect_n_plus_one(line, line_num, lines)
    elif pattern_id == "unbounded-list":
        return detect_unbounded_list(line, line_num, lines)
    elif pattern_id == "expensive-loop":
        return detect_expensive_loop(line, line_num, lines)
    # Performance: web-specific detectors
    elif pattern_id == "layout-animation":
        if file_ext not in ['.css', '.scss', '.less']:
            return 0.0
        return detect_layout_animation(line, line_num, lines)
    elif pattern_id == "layout-thrashing":
        if file_ext not in ['.js', '.jsx', '.ts', '.tsx']:
            return 0.0
        return detect_layout_thrashing(line, line_num, lines)
    elif pattern_id == "unthrottled-scroll":
        if file_ext not in ['.js', '.jsx', '.ts', '.tsx']:
            return 0.0
        return detect_unthrottled_scroll(line, line_num, lines)
    elif pattern_id == "non-passive-listener":
        if file_ext not in ['.js', '.jsx', '.ts', '.tsx']:
            return 0.0
        return detect_non_passive_listener(line, line_num, lines)
    elif pattern_id == "missing-debounce":
        if file_ext not in ['.js', '.jsx', '.ts', '.tsx']:
            return 0.0
        return detect_missing_debounce(line, line_num, lines)
    elif pattern_id == "inline-jsx-object":
        if file_ext not in ['.jsx', '.tsx']:
            return 0.0
        return detect_inline_jsx_object(line, line_num, lines)
    elif pattern_id == "render-loop-alloc":
        if file_ext not in ['.js', '.jsx', '.ts', '.tsx']:
            return 0.0
        return detect_render_loop_alloc(line, line_num, lines)
    elif pattern_id == "uncapped-pixel-ratio":
        if file_ext not in ['.js', '.jsx', '.ts', '.tsx']:
            return 0.0
        return detect_uncapped_pixel_ratio(line, line_num, lines)
    elif pattern_id == "image-no-dimensions":
        if file_ext not in ['.html', '.jsx', '.tsx']:
            return 0.0
        return detect_image_no_dimensions(line, line_num, lines)
    elif pattern_id == "dead-code":
        return detect_dead_code(line, line_num, lines)
    elif pattern_id == "magic-number":
        return detect_magic_number(line, line_num, lines)
    elif pattern_id == "deep-nesting":
        return detect_deep_nesting(line, line_num, lines)
    # Web/React/Next.js detectors
    elif pattern_id == "dangerous-html":
        if file_ext not in ['.jsx', '.tsx', '.js', '.ts']:
            return 0.0
        return detect_dangerous_html(line, line_num, lines)
    elif pattern_id == "missing-cleanup":
        if file_ext not in ['.jsx', '.tsx', '.js', '.ts']:
            return 0.0
        return detect_missing_cleanup(line, line_num, lines)
    elif pattern_id == "stale-closure":
        if file_ext not in ['.jsx', '.tsx', '.js', '.ts']:
            return 0.0
        return detect_stale_closure(line, line_num, lines)
    elif pattern_id == "env-leak":
        if file_ext not in ['.jsx', '.tsx', '.js', '.ts']:
            return 0.0
        return detect_env_leak(line, line_num, lines)
    elif pattern_id == "ssr-window":
        if file_ext not in ['.jsx', '.tsx', '.js', '.ts']:
            return 0.0
        return detect_ssr_window(line, line_num, lines)
    elif pattern_id == "missing-key":
        if file_ext not in ['.jsx', '.tsx', '.js', '.ts']:
            return 0.0
        return detect_missing_key(line, line_num, lines)
    # New security detectors
    elif pattern_id == "open-redirect":
        if file_ext not in ['.js', '.ts', '.jsx', '.tsx']:
            return 0.0
        return detect_open_redirect(line, line_num, lines)
    elif pattern_id == "permissive-cors":
        if file_ext not in ['.js', '.ts', '.jsx', '.tsx']:
            return 0.0
        return detect_permissive_cors(line, line_num, lines)
    elif pattern_id == "prototype-pollution":
        if file_ext not in ['.js', '.ts', '.jsx', '.tsx']:
            return 0.0
        return detect_prototype_pollution(line, line_num, lines)
    elif pattern_id == "nosql-injection":
        if file_ext not in ['.js', '.ts', '.jsx', '.tsx']:
            return 0.0
        return detect_nosql_injection(line, line_num, lines)
    elif pattern_id == "jwt-alg-none":
        if file_ext not in ['.js', '.ts', '.jsx', '.tsx']:
            return 0.0
        return detect_jwt_alg_none(line, line_num, lines)

    return 0.0


def scan_file(file_path: Path, categories: List[str]) -> List[Dict[str, Any]]:
    """
    Scan a single file for bugs using contextual pattern matching.

    Returns list of bug dictionaries in concise format.
    Only reports bugs with confidence >= MIN_CONFIDENCE.
    """
    bugs = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return bugs

    file_ext = file_path.suffix.lower()

    for category in categories:
        if category not in CATEGORIES:
            continue

        cat_info = CATEGORIES[category]

        for pattern in cat_info["patterns"]:
            pattern_id = pattern["id"]
            min_conf = pattern.get("min_conf", MIN_CONFIDENCE)

            for line_num, line_content in enumerate(lines, 1):
                # Skip empty lines and pure comments (Python #, JS/TS //)
                stripped = line_content.strip()
                if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                    continue

                # Calculate confidence for this pattern
                confidence = check_pattern(pattern_id, line_content, line_num - 1, lines, file_ext)

                # Only report if confidence meets threshold
                if confidence >= min_conf:
                    bug_id = generate_bug_id(str(file_path), line_num, pattern_id)

                    bug = {
                        "id": bug_id,
                        "loc": f"{file_path}:{line_num}",
                        "cat": category,
                        "sev": "high" if category == "security" else "medium",
                        "desc": pattern["desc"],
                        "pattern_id": pattern_id,
                        "confidence": round(confidence, 2),
                    }

                    if "cwe" in pattern:
                        bug["cwe"] = pattern["cwe"]

                    # Avoid duplicates
                    if not any(b["id"] == bug_id for b in bugs):
                        bugs.append(bug)

    return bugs


def scan_directory(path: Path, categories: List[str], 
                   extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Recursively scan a directory for bugs.
    """
    if extensions is None:
        extensions = [
            '.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
            '.css', '.scss', '.json', '.html', '.vue', '.svelte',
            '.java', '.go', '.rb', '.php', '.c', '.cpp', '.h',
        ]
    
    all_bugs = []
    
    # Get all matching files
    files = []
    if path.is_file():
        files = [path]
    else:
        for ext in extensions:
            files.extend(path.rglob(f"*{ext}"))
    
    # Filter out common non-source directories
    exclude_dirs = {
        '.git', 'node_modules', '__pycache__', 'venv', '.venv',
        'dist', 'build', '.next', '.nuxt', 'coverage', '.cache',
        '.turbo', 'out', '.debug-session',
    }
    files = [f for f in files if not any(d in f.parts for d in exclude_dirs)]
    
    print(f"📂 Scanning {len(files)} files...", file=sys.stderr)
    
    for file_path in files:
        bugs = scan_file(file_path, categories)
        all_bugs.extend(bugs)
    
    return all_bugs


def format_concise(bugs: List[Dict[str, Any]]) -> str:
    """Format bugs as concise JSON (token-optimized)."""
    # Strip to minimal fields
    minimal_bugs = []
    for bug in bugs:
        minimal = {
            "id": bug["id"],
            "loc": bug["loc"],
            "cat": bug["cat"],
            "sev": bug["sev"],
            "desc": bug["desc"],
            "conf": bug.get("confidence", 0.0)
        }
        if "cwe" in bug:
            minimal["cwe"] = bug["cwe"]
        minimal_bugs.append(minimal)

    return json.dumps({"bugs": minimal_bugs}, separators=(',', ':'))


def format_detailed(bugs: List[Dict[str, Any]]) -> str:
    """Format bugs as detailed YAML for human review."""
    import yaml

    detailed_bugs = []
    for bug in bugs:
        detailed = {
            "id": bug["id"],
            "status": "pending",
            "confidence": bug.get("confidence", 0.7),
            "category": bug["cat"],
            "severity": bug["sev"],
            "location": {
                "file": bug["loc"].rsplit(":", 1)[0],
                "line": int(bug["loc"].rsplit(":", 1)[1]),
            },
            "description": bug["desc"],
        }
        if "cwe" in bug:
            detailed["cwe"] = bug["cwe"]
        detailed_bugs.append(detailed)

    return yaml.dump({"bugs": detailed_bugs}, default_flow_style=False, sort_keys=False)


def update_manifest(bugs: List[Dict[str, Any]], manifest_path: Path) -> bool:
    """Update the bug manifest with new bugs."""
    import yaml

    if not manifest_path.exists():
        print(f"❌ Error: Manifest not found at {manifest_path}", file=sys.stderr)
        print("   Run init_debug_session.py first.", file=sys.stderr)
        return False

    # Load existing manifest
    manifest = yaml.safe_load(manifest_path.read_text())

    # Convert bugs to manifest format
    existing_ids = {b["id"] for b in manifest.get("bugs", [])}

    new_bugs = []
    for bug in bugs:
        if bug["id"] not in existing_ids:
            manifest_bug = {
                "id": bug["id"],
                "status": "pending",
                "confidence": bug.get("confidence", 0.7),
                "category": bug["cat"],
                "severity": bug["sev"],
                "location": {
                    "file": bug["loc"].rsplit(":", 1)[0],
                    "line": int(bug["loc"].rsplit(":", 1)[1]),
                },
                "description": bug["desc"],
                "fix_applied": None,
                "verified_at": None,
            }
            if "cwe" in bug:
                manifest_bug["cwe"] = bug["cwe"]
            new_bugs.append(manifest_bug)

    # Merge with existing
    manifest["bugs"] = manifest.get("bugs", []) + new_bugs

    # Update stats
    stats = {"total_found": 0, "pending": 0, "fixing": 0, "fixed": 0, "verified": 0, "ignored": 0}
    for b in manifest["bugs"]:
        stats["total_found"] += 1
        status = b.get("status", "pending")
        if status in stats:
            stats[status] += 1
    manifest["stats"] = stats

    # Write back
    manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False))

    print(f"✅ Updated manifest: {len(new_bugs)} new bugs added", file=sys.stderr)
    print(f"   Total: {stats['total_found']} | Pending: {stats['pending']}", file=sys.stderr)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Scan code for bugs with token-optimized output",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", help="File or directory to scan")
    parser.add_argument("--category", "-c", default="all",
                       choices=["security", "logic", "performance", "quality", "web", "all"],
                       help="Bug category to scan for (quality is noisy — use explicitly)")
    parser.add_argument("--output", "-o", default="concise",
                       choices=["concise", "detailed", "manifest"],
                       help="Output format")
    parser.add_argument("--manifest-path", "-m", default=None,
                       help="Path to bug-manifest.yaml (default: <path>/.debug-session/bug-manifest.yaml)")
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"❌ Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)
    
    # Determine categories — 'all' excludes noisy 'quality' by default
    if args.category == "all":
        categories = [k for k in CATEGORIES.keys() if k != "quality"]
    else:
        categories = [args.category]
    
    # Run scan
    bugs = scan_directory(path, categories)
    
    print(f"🔍 Found {len(bugs)} potential issues", file=sys.stderr)
    
    # Output based on format
    if args.output == "concise":
        print(format_concise(bugs))
    elif args.output == "detailed":
        print(format_detailed(bugs))
    elif args.output == "manifest":
        manifest_path = Path(args.manifest_path) if args.manifest_path else \
                       (path / ".debug-session" / "bug-manifest.yaml" if path.is_dir() else \
                        path.parent / ".debug-session" / "bug-manifest.yaml")
        if update_manifest(bugs, manifest_path):
            # Also output concise for LLM consumption
            print(format_concise(bugs))
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
