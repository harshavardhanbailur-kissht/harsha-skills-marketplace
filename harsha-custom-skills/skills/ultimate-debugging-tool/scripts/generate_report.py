#!/usr/bin/env python3
"""
Generate a debugging session report.

Produces a summary of all bugs found, fixed, verified, and ignored
during the debugging session.

Usage:
    python generate_report.py [--manifest PATH] [--format FORMAT]

Formats:
    summary   - Brief stats and key findings (default)
    detailed  - Full report with all bugs
    json      - Machine-readable JSON
    markdown  - Markdown for documentation

Example:
    python generate_report.py
    python generate_report.py --format markdown > report.md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml
except ImportError:
    print("❌ Error: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Load the bug manifest."""
    if not manifest_path.exists():
        return {}
    return yaml.safe_load(manifest_path.read_text()) or {}


def calculate_stats(manifest: Dict) -> Dict[str, Any]:
    """Calculate detailed statistics from manifest."""
    bugs = manifest.get("bugs", [])
    
    stats = {
        "total": len(bugs),
        "by_status": {},
        "by_category": {},
        "by_severity": {},
        "high_severity_fixed": 0,
        "security_issues": 0,
        "verification_rate": 0.0,
    }
    
    fixed_count = 0
    verified_count = 0
    
    for bug in bugs:
        status = bug.get("status", "unknown")
        category = bug.get("category", "unknown")
        severity = bug.get("severity", "unknown")
        
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        if status in ["fixed", "verified"]:
            fixed_count += 1
            if severity == "high":
                stats["high_severity_fixed"] += 1
        
        if status == "verified":
            verified_count += 1
        
        if category == "security":
            stats["security_issues"] += 1
    
    if fixed_count > 0:
        stats["verification_rate"] = verified_count / fixed_count
    
    return stats


def format_summary(manifest: Dict, stats: Dict) -> str:
    """Generate brief summary report."""
    session = manifest.get("session", {})
    
    lines = [
        "=" * 50,
        "ULTIMATE DEBUGGER SESSION REPORT",
        "=" * 50,
        "",
        f"Session ID: {session.get('id', 'N/A')}",
        f"Goal: {session.get('original_goal', 'N/A')}",
        f"Started: {session.get('started', 'N/A')}",
        "",
        "📊 SUMMARY",
        "-" * 30,
        f"Total bugs found: {stats['total']}",
        f"  ✅ Verified:  {stats['by_status'].get('verified', 0)}",
        f"  🔧 Fixed:     {stats['by_status'].get('fixed', 0)}",
        f"  ⏳ Pending:   {stats['by_status'].get('pending', 0)}",
        f"  🚫 Ignored:   {stats['by_status'].get('ignored', 0)}",
        "",
        f"Verification rate: {stats['verification_rate']:.0%}",
        f"High severity fixed: {stats['high_severity_fixed']}",
        "",
        "📁 BY CATEGORY",
        "-" * 30,
    ]
    
    for cat, count in sorted(stats["by_category"].items()):
        lines.append(f"  {cat}: {count}")
    
    lines.extend(["", "=" * 50])
    
    return "\n".join(lines)


def format_detailed(manifest: Dict, stats: Dict) -> str:
    """Generate detailed report with all bugs."""
    lines = [format_summary(manifest, stats)]
    
    bugs = manifest.get("bugs", [])
    
    # Group by status
    for status in ["pending", "fixing", "fixed", "verified", "ignored"]:
        status_bugs = [b for b in bugs if b.get("status") == status]
        if not status_bugs:
            continue
        
        lines.extend([
            "",
            f"📋 {status.upper()} ({len(status_bugs)})",
            "-" * 40,
        ])
        
        for bug in status_bugs:
            loc = bug.get("location", {})
            lines.extend([
                f"",
                f"  [{bug['id']}] {bug.get('description', 'No description')}",
                f"    File: {loc.get('file', 'N/A')}:{loc.get('line', 'N/A')}",
                f"    Category: {bug.get('category', 'N/A')} | Severity: {bug.get('severity', 'N/A')}",
            ])
            
            if bug.get("cwe"):
                lines.append(f"    CWE: {bug['cwe']}")
            
            if bug.get("ignore_rule"):
                lines.append(f"    Ignore rule: {bug['ignore_rule']}")
            
            if bug.get("verified_at"):
                lines.append(f"    Verified: {bug['verified_at']}")
    
    return "\n".join(lines)


def format_json(manifest: Dict, stats: Dict) -> str:
    """Generate JSON report."""
    report = {
        "session": manifest.get("session", {}),
        "stats": stats,
        "bugs": manifest.get("bugs", []),
        "generated_at": datetime.now().isoformat()
    }
    return json.dumps(report, indent=2)


def format_markdown(manifest: Dict, stats: Dict) -> str:
    """Generate Markdown report."""
    session = manifest.get("session", {})
    bugs = manifest.get("bugs", [])
    
    lines = [
        "# Gas Debugger Report",
        "",
        "## Session Information",
        "",
        f"- **Session ID**: {session.get('id', 'N/A')}",
        f"- **Goal**: {session.get('original_goal', 'N/A')}",
        f"- **Started**: {session.get('started', 'N/A')}",
        f"- **Generated**: {datetime.now().isoformat()}",
        "",
        "## Summary Statistics",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total bugs | {stats['total']} |",
        f"| Verified | {stats['by_status'].get('verified', 0)} |",
        f"| Fixed | {stats['by_status'].get('fixed', 0)} |",
        f"| Pending | {stats['by_status'].get('pending', 0)} |",
        f"| Ignored | {stats['by_status'].get('ignored', 0)} |",
        "",
        f"**Verification Rate**: {stats['verification_rate']:.0%}",
        "",
        "## Bugs by Category",
        "",
        "| Category | Count |",
        "|----------|-------|",
    ]
    
    for cat, count in sorted(stats["by_category"].items()):
        lines.append(f"| {cat} | {count} |")
    
    # Pending bugs (action items)
    pending = [b for b in bugs if b.get("status") == "pending"]
    if pending:
        lines.extend([
            "",
            "## Action Required (Pending Bugs)",
            "",
        ])
        for bug in pending:
            loc = bug.get("location", {})
            lines.extend([
                f"### [{bug['id']}] {bug.get('description', 'No description')}",
                "",
                f"- **File**: `{loc.get('file', 'N/A')}:{loc.get('line', 'N/A')}`",
                f"- **Category**: {bug.get('category', 'N/A')}",
                f"- **Severity**: {bug.get('severity', 'N/A')}",
            ])
            if bug.get("cwe"):
                lines.append(f"- **CWE**: {bug['cwe']}")
            lines.append("")
    
    # Verified bugs (completed)
    verified = [b for b in bugs if b.get("status") == "verified"]
    if verified:
        lines.extend([
            "",
            "## Completed (Verified Fixes)",
            "",
            "| Bug ID | Description | File | Verified |",
            "|--------|-------------|------|----------|",
        ])
        for bug in verified:
            loc = bug.get("location", {})
            lines.append(
                f"| {bug['id']} | {bug.get('description', '')[:40]}... | "
                f"`{Path(loc.get('file', '')).name}:{loc.get('line', '')}` | "
                f"{bug.get('verified_at', 'N/A')[:10]} |"
            )
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate debugging session report"
    )
    parser.add_argument("--manifest", "-m", default=".debug-session/bug-manifest.yaml",
                       help="Path to bug manifest")
    parser.add_argument("--format", "-f", default="summary",
                       choices=["summary", "detailed", "json", "markdown"],
                       help="Output format")
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)
    
    manifest = load_manifest(manifest_path)
    stats = calculate_stats(manifest)
    
    formatters = {
        "summary": format_summary,
        "detailed": format_detailed,
        "json": format_json,
        "markdown": format_markdown,
    }
    
    output = formatters[args.format](manifest, stats)
    print(output)


if __name__ == "__main__":
    main()
