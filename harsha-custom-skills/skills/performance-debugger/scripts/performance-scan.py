#!/usr/bin/env python3
"""
Performance Debugger - Static Analysis Scanner

Scans JavaScript/TypeScript/CSS files for performance anti-patterns.
Outputs issues in a structured format for automated fixing.

Usage:
    python performance-scan.py /path/to/project [--output json|yaml]
"""

import os
import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Category(Enum):
    ANIMATION = "P1"
    JAVASCRIPT = "P2"
    REACT = "P3"
    THREEJS = "P4"
    MEMORY = "P5"
    CWV = "P6"

@dataclass
class Issue:
    id: str
    category: str
    code: str
    title: str
    file: str
    line: int
    column: int
    severity: str
    confidence: float
    snippet: str
    fix_available: bool
    description: str

# Pattern definitions
PATTERNS = {
    # P1: Animation & Rendering
    "P1-001": {
        "title": "Animating layout properties",
        "pattern": r"transition:\s*[^;]*(width|height|top|left|right|bottom|margin|padding)",
        "file_types": [".css", ".scss", ".less"],
        "severity": Severity.HIGH,
        "confidence": 0.90,
        "description": "Animating layout properties causes expensive reflow. Use transform instead.",
        "fix_available": True,
    },
    "P1-002": {
        "title": "Layout thrashing pattern",
        "pattern": r"(offsetWidth|offsetHeight|offsetTop|offsetLeft|clientWidth|clientHeight|getBoundingClientRect)\s*[;\n][^}]*\.style\.",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.CRITICAL,
        "confidence": 0.75,
        "description": "Reading layout properties then writing causes synchronous layout. Batch reads before writes.",
        "fix_available": True,
    },
    "P1-004": {
        "title": "setTimeout/setInterval for animation",
        "pattern": r"set(Timeout|Interval)\s*\([^)]+,\s*\d+\s*\)[^;]*(?:transform|position|animate|style)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.MEDIUM,
        "confidence": 0.70,
        "description": "setTimeout/setInterval is not synchronized with display refresh. Use requestAnimationFrame.",
        "fix_available": True,
    },
    "P1-006": {
        "title": "Scroll handler without RAF throttling",
        "pattern": r"addEventListener\s*\(\s*['\"]scroll['\"](?!.*requestAnimationFrame)(?!.*ticking)(?!.*throttle)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.HIGH,
        "confidence": 0.85,
        "description": "Scroll handlers fire frequently. Throttle with requestAnimationFrame.",
        "fix_available": True,
    },
    "P1-007": {
        "title": "Non-passive touch/wheel listener",
        "pattern": r"addEventListener\s*\(\s*['\"](?:touchstart|touchmove|wheel)['\"](?!.*passive)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.HIGH,
        "confidence": 0.95,
        "description": "Missing passive: true causes scroll delay. Add { passive: true }.",
        "fix_available": True,
    },

    # P2: JavaScript Performance
    "P2-004": {
        "title": "Missing debounce/throttle on input handler",
        "pattern": r"addEventListener\s*\(\s*['\"](?:input|keyup|keydown|resize|mousemove)['\"](?!.*debounce)(?!.*throttle)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.MEDIUM,
        "confidence": 0.70,
        "description": "Rapid-fire events should be debounced or throttled.",
        "fix_available": True,
    },

    # P3: React-specific
    "P3-001": {
        "title": "Inline object/array in JSX",
        "pattern": r"<\w+[^>]*\s(?:style|options|config|data)=\{\{",
        "file_types": [".jsx", ".tsx"],
        "severity": Severity.MEDIUM,
        "confidence": 0.85,
        "description": "Inline objects create new references every render, causing unnecessary re-renders.",
        "fix_available": True,
    },
    "P3-005": {
        "title": "Missing key prop in map",
        "pattern": r"\.map\s*\([^)]*\)\s*=>\s*(?:<[^>]*(?!key=))[^}]*\)",
        "file_types": [".jsx", ".tsx"],
        "severity": Severity.HIGH,
        "confidence": 0.80,
        "description": "Missing key prop in list causes reconciliation issues.",
        "fix_available": True,
    },

    # P4: Three.js
    "P4-001": {
        "title": "Object creation in render loop",
        "pattern": r"function\s+(?:animate|render|update|tick)\s*\([^)]*\)\s*\{[^}]*new\s+(?:THREE\.)?(?:Vector[234]|Quaternion|Matrix[34]|Euler)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.CRITICAL,
        "confidence": 0.95,
        "description": "Creating objects in render loop causes GC pressure and jank. Pre-allocate outside loop.",
        "fix_available": True,
    },
    "P4-002": {
        "title": "Direct GSAP animation on Three.js object",
        "pattern": r"gsap\.(?:to|from|fromTo)\s*\(\s*\w+\.(?:position|rotation|scale|quaternion)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.HIGH,
        "confidence": 0.90,
        "description": "GSAP doesn't understand Three.js objects. Use proxy pattern with onUpdate.",
        "fix_available": True,
    },
    "P4-004": {
        "title": "Uncapped pixel ratio",
        "pattern": r"setPixelRatio\s*\(\s*window\.devicePixelRatio\s*\)",
        "file_types": [".js", ".jsx", ".ts", ".tsx"],
        "severity": Severity.HIGH,
        "confidence": 0.95,
        "description": "High pixel ratios (3x) massively increase GPU load. Cap at 2.",
        "fix_available": True,
    },

    # P5: Memory leaks
    "P5-001": {
        "title": "setInterval without cleanup",
        "pattern": r"useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*setInterval[^}]*(?!\bclearInterval)",
        "file_types": [".jsx", ".tsx"],
        "severity": Severity.CRITICAL,
        "confidence": 0.90,
        "description": "setInterval without clearInterval in cleanup causes memory leak.",
        "fix_available": True,
    },
    "P5-002": {
        "title": "addEventListener without cleanup",
        "pattern": r"useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*addEventListener[^}]*(?!\bremoveEventListener)(?!\babort)",
        "file_types": [".jsx", ".tsx"],
        "severity": Severity.CRITICAL,
        "confidence": 0.85,
        "description": "addEventListener without removeEventListener in cleanup causes memory leak.",
        "fix_available": True,
    },

    # P6: Core Web Vitals
    "P6-003": {
        "title": "Image without dimensions",
        "pattern": r"<img[^>]*(?!.*(?:width|height))[^>]*>",
        "file_types": [".html", ".jsx", ".tsx"],
        "severity": Severity.HIGH,
        "confidence": 0.90,
        "description": "Images without width/height cause layout shift (CLS).",
        "fix_available": True,
    },
}


def scan_file(file_path: Path, patterns: dict) -> List[Issue]:
    """Scan a single file for performance issues."""
    issues = []

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return issues

    lines = content.split('\n')
    file_ext = file_path.suffix

    for code, pattern_def in patterns.items():
        if file_ext not in pattern_def["file_types"]:
            continue

        pattern = pattern_def["pattern"]

        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            col_num = match.start() - content.rfind('\n', 0, match.start())

            # Get snippet (context around match)
            start_line = max(0, line_num - 2)
            end_line = min(len(lines), line_num + 2)
            snippet = '\n'.join(lines[start_line:end_line])

            issue = Issue(
                id=f"{code}-{file_path.name}-{line_num}",
                category=code.split('-')[0],
                code=code,
                title=pattern_def["title"],
                file=str(file_path),
                line=line_num,
                column=col_num,
                severity=pattern_def["severity"].value,
                confidence=pattern_def["confidence"],
                snippet=snippet[:200],
                fix_available=pattern_def["fix_available"],
                description=pattern_def["description"],
            )
            issues.append(issue)

    return issues


def scan_directory(dir_path: Path, patterns: dict, exclude_dirs: List[str] = None) -> List[Issue]:
    """Recursively scan directory for performance issues."""
    if exclude_dirs is None:
        exclude_dirs = ['node_modules', '.git', 'dist', 'build', 'coverage', '__pycache__']

    issues = []
    file_types = set()
    for p in patterns.values():
        file_types.update(p["file_types"])

    for file_path in dir_path.rglob('*'):
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue

        if file_path.suffix in file_types:
            issues.extend(scan_file(file_path, patterns))

    return issues


def generate_report(issues: List[Issue], format: str = 'json') -> str:
    """Generate report in specified format."""

    # Sort by severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    issues.sort(key=lambda x: severity_order.get(x.severity, 4))

    # Summary
    summary = {
        'total_issues': len(issues),
        'by_severity': {},
        'by_category': {},
        'auto_fixable': sum(1 for i in issues if i.fix_available),
    }

    for issue in issues:
        summary['by_severity'][issue.severity] = summary['by_severity'].get(issue.severity, 0) + 1
        summary['by_category'][issue.category] = summary['by_category'].get(issue.category, 0) + 1

    report = {
        'summary': summary,
        'issues': [asdict(i) for i in issues],
    }

    if format == 'json':
        return json.dumps(report, indent=2)
    elif format == 'yaml':
        # Simple YAML output
        lines = ['summary:']
        for k, v in summary.items():
            if isinstance(v, dict):
                lines.append(f'  {k}:')
                for k2, v2 in v.items():
                    lines.append(f'    {k2}: {v2}')
            else:
                lines.append(f'  {k}: {v}')
        lines.append('')
        lines.append('issues:')
        for issue in issues:
            lines.append(f'  - code: {issue.code}')
            lines.append(f'    file: {issue.file}')
            lines.append(f'    line: {issue.line}')
            lines.append(f'    severity: {issue.severity}')
            lines.append(f'    title: {issue.title}')
        return '\n'.join(lines)
    else:
        # Plain text
        lines = ['Performance Scan Results', '=' * 50, '']
        lines.append(f"Total issues: {summary['total_issues']}")
        lines.append(f"Auto-fixable: {summary['auto_fixable']}")
        lines.append('')

        for issue in issues:
            lines.append(f"[{issue.severity.upper()}] {issue.code}: {issue.title}")
            lines.append(f"  File: {issue.file}:{issue.line}")
            lines.append(f"  {issue.description}")
            lines.append('')

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Performance Debugger Scanner')
    parser.add_argument('path', type=str, help='Path to project directory')
    parser.add_argument('--output', '-o', choices=['json', 'yaml', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--category', '-c', type=str, help='Filter by category (P1-P6)')
    parser.add_argument('--severity', '-s', choices=['critical', 'high', 'medium', 'low'],
                        help='Minimum severity level')

    args = parser.parse_args()

    project_path = Path(args.path)
    if not project_path.exists():
        print(f"Error: Path {args.path} does not exist")
        return 1

    # Filter patterns if category specified
    patterns = PATTERNS
    if args.category:
        patterns = {k: v for k, v in PATTERNS.items() if k.startswith(args.category)}

    # Scan
    if project_path.is_file():
        issues = scan_file(project_path, patterns)
    else:
        issues = scan_directory(project_path, patterns)

    # Filter by severity if specified
    if args.severity:
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        min_severity = severity_order[args.severity]
        issues = [i for i in issues if severity_order.get(i.severity, 4) <= min_severity]

    # Output report
    report = generate_report(issues, args.output)
    print(report)

    return 0 if not issues else 1


if __name__ == '__main__':
    exit(main())
