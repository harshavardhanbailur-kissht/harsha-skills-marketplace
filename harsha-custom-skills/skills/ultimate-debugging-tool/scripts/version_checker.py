#!/usr/bin/env python3
"""
Framework Version Checker for Ultimate Debugger
Checks current framework versions against documented patterns and flags staleness.
Run quarterly to detect version drift in pattern-index.json.

Usage:
    python scripts/version_checker.py
    python scripts/version_checker.py --format json
    python scripts/version_checker.py --format yaml
    python scripts/version_checker.py --offline  # For testing without network
    python scripts/version_checker.py --no-check-npm  # Don't query npm registry
    python scripts/version_checker.py --pattern-index /path/to/pattern-index.json
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


# Hardcoded known versions for offline mode (April 2026)
OFFLINE_VERSIONS = {
    "react": "19.2.4",
    "next": "16.2.0",
    "three": "0.183.2",
    "gsap": "3.14.2",
    "typescript": "6.0.2"
}

# Map framework names to npm package names
FRAMEWORK_NPM_MAP = {
    "React": "react",
    "Next.js": "next",
    "Three.js": "three",
    "GSAP": "gsap",
    "TypeScript": "typescript"
}


@dataclass
class VersionCheck:
    """Result of checking a single framework."""
    framework: str
    npm_package: str
    documented_min: str
    documented_max: Optional[str]
    current_version: str
    major_gap: int = 0
    status: str = "ok"  # ok|outdated|stale|critical
    patterns_affected: List[str] = field(default_factory=list)
    recommendation: str = ""


def parse_version(version_str: str) -> tuple:
    """
    Parse version string into (major, minor, patch).
    Handles formats: "16.0", "19.2.4", "r183.2", "6.0.2"
    Returns: (major, minor, patch) as ints, or (0, 0, 0) on parse error.
    """
    if not version_str or version_str == "unknown":
        return (0, 0, 0)

    # Strip 'r' prefix (Three.js versions like "r183.2")
    version_str = version_str.lstrip("r").lstrip("v")

    # Split by dots
    parts = version_str.split(".")
    try:
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except (ValueError, IndexError):
        return (0, 0, 0)


def check_npm_version(package_name: str) -> Dict:
    """
    Query npm registry for latest version info.

    Args:
        package_name: npm package name (e.g., "react", "next")

    Returns:
        dict with 'name', 'version', 'success', and optional 'error'
    """
    url = f"https://registry.npmjs.org/{package_name}/latest"
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "ultimate-debugger"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return {
                "name": package_name,
                "version": data.get("version", "unknown"),
                "success": True
            }
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        return {
            "name": package_name,
            "version": "unknown",
            "success": False,
            "error": str(e)
        }


def get_current_versions(check_npm: bool = True, offline: bool = False) -> Dict[str, str]:
    """
    Get current versions of all frameworks.

    Args:
        check_npm: If True, query npm registry; if False, return empty dict
        offline: If True, use hardcoded known versions

    Returns:
        dict mapping npm package names to version strings
    """
    if offline:
        return OFFLINE_VERSIONS.copy()

    if not check_npm:
        return {}

    versions = {}
    for framework, npm_package in FRAMEWORK_NPM_MAP.items():
        result = check_npm_version(npm_package)
        if result["success"]:
            versions[npm_package] = result["version"]

    return versions


def load_pattern_index(pattern_index_path: Optional[str] = None) -> Dict:
    """
    Load pattern-index.json.

    Args:
        pattern_index_path: Path to pattern-index.json. If None, auto-detect.

    Returns:
        Parsed JSON dict
    """
    if pattern_index_path:
        index_path = Path(pattern_index_path)
    else:
        # Auto-detect relative to this script
        script_dir = Path(__file__).parent
        index_path = script_dir.parent / "references" / "pattern-index.json"

    if not index_path.exists():
        raise FileNotFoundError(f"pattern-index.json not found at {index_path}")

    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_staleness(
    framework: str,
    documented_min: str,
    documented_max: Optional[str],
    current_version: str
) -> tuple:
    """
    Calculate staleness status.

    Returns:
        (status, major_gap, recommendation)
        status: "ok" | "outdated" | "stale" | "critical"
        major_gap: difference in major version
    """
    if current_version == "unknown":
        return ("unknown", 0, "Unable to determine current version")

    current = parse_version(current_version)
    doc_min = parse_version(documented_min) if documented_min else (0, 0, 0)
    doc_max = parse_version(documented_max) if documented_max else None

    current_major = current[0]
    doc_max_major = doc_max[0] if doc_max else current_major

    major_gap = current_major - doc_max_major

    # Status logic
    if major_gap > 0:
        if major_gap >= 2:
            status = "critical"
            recommendation = f"Review {framework} patterns for {current_major}.x compatibility (major version gap: {major_gap})"
        else:
            status = "stale"
            recommendation = f"Review {framework} patterns for {current_major}.x compatibility"
    elif major_gap == 0:
        # Check minor version
        current_minor = current[1]
        doc_max_minor = doc_max[1] if doc_max else 0
        minor_gap = current_minor - doc_max_minor

        if minor_gap >= 3:
            status = "outdated"
            recommendation = f"Consider reviewing {framework} patterns (minor version {minor_gap} ahead)"
        else:
            status = "ok"
            recommendation = f"{framework} patterns current"
    else:
        status = "ok"
        recommendation = f"{framework} patterns current (or documented max ahead of npm)"

    return (status, major_gap, recommendation)


def check_frameworks(
    pattern_index: Dict,
    current_versions: Dict[str, str]
) -> List[VersionCheck]:
    """
    Check all frameworks in pattern-index.json.

    Returns:
        list of VersionCheck objects
    """
    results = []

    # Build a map of framework -> patterns
    framework_patterns = {}
    for pattern in pattern_index.get("patterns", []):
        fw = pattern["framework"]
        if fw not in framework_patterns:
            framework_patterns[fw] = []
        framework_patterns[fw].append(pattern["id"])

    # Check each unique framework
    seen_frameworks = set()
    for pattern in pattern_index.get("patterns", []):
        framework = pattern["framework"]
        if framework in seen_frameworks:
            continue
        seen_frameworks.add(framework)

        npm_package = FRAMEWORK_NPM_MAP.get(framework)
        if not npm_package:
            continue

        doc_min = pattern.get("min_version", "unknown")
        doc_max = pattern.get("max_version")
        current = current_versions.get(npm_package, "unknown")

        status, major_gap, recommendation = calculate_staleness(
            framework, doc_min, doc_max, current
        )

        check = VersionCheck(
            framework=framework,
            npm_package=npm_package,
            documented_min=doc_min,
            documented_max=doc_max,
            current_version=current,
            major_gap=major_gap,
            status=status,
            patterns_affected=framework_patterns.get(framework, []),
            recommendation=recommendation
        )
        results.append(check)

    # Sort by framework name for consistent output
    results.sort(key=lambda x: x.framework)
    return results


def format_text_output(checks: List[VersionCheck]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 64)
    lines.append("  ULTIMATE DEBUGGER — FRAMEWORK VERSION CHECK")
    lines.append("=" * 64)
    lines.append(f"  Checked: {datetime.now().strftime('%B %d, %Y')}")
    lines.append("")

    # Table header
    lines.append("  FRAMEWORK         DOCUMENTED    CURRENT     STATUS")
    lines.append("  " + "─" * 60)

    # Status icon map
    status_icons = {
        "ok": "✅ OK",
        "outdated": "⚠️  OUTDATED",
        "stale": "⚠️  STALE",
        "critical": "🔴 CRITICAL",
        "unknown": "❓ UNKNOWN"
    }

    ok_count = 0
    needs_review = 0

    for check in checks:
        icon = status_icons.get(check.status, "?")

        # Format documented versions
        if check.documented_max:
            doc_version = f"{check.documented_min}–{check.documented_max}"
        else:
            doc_version = f"{check.documented_min}+"

        # Format line
        fw_col = check.framework.ljust(17)
        doc_col = doc_version.ljust(13)
        curr_col = check.current_version.ljust(11)

        lines.append(f"  {fw_col} {doc_col} {curr_col} {icon}")

        # Add recommendation line if needed
        if check.status != "ok":
            lines.append(f"    → {len(check.patterns_affected)} patterns affected: {', '.join(check.patterns_affected)}")
            lines.append(f"    → Recommend: {check.recommendation}")
            needs_review += 1
        else:
            ok_count += 1

    # Summary
    lines.append("  " + "─" * 60)
    total = len(checks)
    lines.append(f"  SUMMARY: {ok_count}/{total} frameworks current, {needs_review}/{total} need review")
    lines.append("=" * 64)

    return "\n".join(lines)


def format_json_output(checks: List[VersionCheck]) -> str:
    """Format results as JSON."""
    data = {
        "checked_at": datetime.now().isoformat(),
        "summary": {
            "total": len(checks),
            "ok": len([c for c in checks if c.status == "ok"]),
            "needs_review": len([c for c in checks if c.status != "ok"])
        },
        "frameworks": [asdict(c) for c in checks]
    }
    return json.dumps(data, indent=2)


def format_yaml_output(checks: List[VersionCheck]) -> str:
    """Format results as YAML."""
    lines = []
    lines.append(f"checked_at: {datetime.now().isoformat()}")
    lines.append("summary:")
    lines.append(f"  total: {len(checks)}")
    lines.append(f"  ok: {len([c for c in checks if c.status == 'ok'])}")
    lines.append(f"  needs_review: {len([c for c in checks if c.status != 'ok'])}")
    lines.append("frameworks:")

    for check in checks:
        lines.append(f"  - framework: {check.framework}")
        lines.append(f"    npm_package: {check.npm_package}")
        lines.append(f"    documented_min: {check.documented_min}")
        lines.append(f"    documented_max: {check.documented_max}")
        lines.append(f"    current_version: {check.current_version}")
        lines.append(f"    major_gap: {check.major_gap}")
        lines.append(f"    status: {check.status}")
        lines.append(f"    patterns_affected: {check.patterns_affected}")
        lines.append(f"    recommendation: {check.recommendation}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check framework versions against pattern-index.json"
    )
    parser.add_argument(
        "--pattern-index",
        type=str,
        default=None,
        help="Path to pattern-index.json (auto-detect if omitted)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--check-npm",
        action="store_true",
        default=True,
        help="Query npm registry (default: True)"
    )
    parser.add_argument(
        "--no-check-npm",
        action="store_true",
        help="Don't query npm registry"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use hardcoded known versions (for testing)"
    )

    args = parser.parse_args()

    check_npm = not args.no_check_npm

    try:
        # Load pattern index
        pattern_index = load_pattern_index(args.pattern_index)

        # Get current versions
        current_versions = get_current_versions(
            check_npm=check_npm,
            offline=args.offline
        )

        # Check frameworks
        checks = check_frameworks(pattern_index, current_versions)

        # Format output
        if args.format == "json":
            output = format_json_output(checks)
        elif args.format == "yaml":
            output = format_yaml_output(checks)
        else:  # text
            output = format_text_output(checks)

        print(output)

        # Exit with error code if any frameworks need review
        needs_review = any(c.status != "ok" for c in checks)
        sys.exit(1 if needs_review else 0)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
