#!/usr/bin/env python3
"""
Unified Debug Pipeline for Ultimate Debugger

Chains context_analyzer.py and fix_signal_analyzer.py into a single,
coherent debugging workflow.

Core Flow:
    Phase 0: Analyze project context (frameworks, patterns, TypeScript, tests)
    Phase 3→4: (Optional) Analyze fix signals (diff depth, complexity)
    Synthesis: Generate unified recommendations and reference files

Usage:
    python debug_pipeline.py <project-path> [options]
    python debug_pipeline.py /tmp/test_proj --context-only --format text
    python debug_pipeline.py /tmp/test_proj --diff fix.diff --severity high --format json
    python debug_pipeline.py /tmp/test_proj --diff fix.diff --format yaml

Required:
    project-path          Path to project root

Optional:
    --diff DIFF           Path to unified diff file (enables signal analysis)
    --severity LEVEL      Bug severity: critical|high|medium|low (default: medium)
    --format FORMAT       Output format: text|json|yaml (default: text)
    --context-only        Only run context analysis (skip signal analysis)
    --verbose             Show detailed signal breakdown
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict

# Import the analyzer modules from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from context_analyzer import analyze_project, ProjectContext
    from fix_signal_analyzer import analyze_fix, FixSignalReport
except ImportError as e:
    print(f"Error: Could not import analyzer modules: {e}", file=sys.stderr)
    sys.exit(1)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class DebugReport:
    """Unified debugging report combining context and signal analysis."""

    # From context_analyzer
    project_path: str = ""
    project_type: str = "unknown"
    project_type_confidence: float = 0.0
    frameworks: list = field(default_factory=list)
    applicable_patterns: list = field(default_factory=list)
    has_typescript: bool = False
    has_tests: bool = False
    source_files_count: int = 0
    total_lines: int = 0

    # From fix_signal_analyzer (if diff provided)
    verification_depth: float = 0.0
    depth_category: str = ""
    signals: dict = field(default_factory=dict)
    levels_required: list = field(default_factory=list)
    levels_recommended: list = field(default_factory=list)
    veto_triggered: bool = False
    severity_override: bool = False

    # Synthesized recommendations
    recommendations: list = field(default_factory=list)
    priority_patterns: list = field(default_factory=list)  # Top patterns by severity
    reference_files_needed: list = field(default_factory=list)  # Which ref files to read


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

def generate_recommendations(context: ProjectContext, signal_report: Optional[FixSignalReport] = None) -> tuple:
    """
    Generate actionable recommendations from combined analysis.

    Returns:
        (recommendations_list, priority_patterns_list, reference_files_list)
    """
    recommendations = []
    reference_files = set()

    # 1. TypeScript recommendation
    if not context.has_typescript:
        recommendations.append(
            "No TypeScript detected. Add TypeScript for type-safety bug prevention "
            "(consider: npm install -D typescript, tsconfig.json, migrate .js → .ts)."
        )

    # 2. Test framework recommendation
    if not context.has_tests:
        recommendations.append(
            "No test framework detected. Add Vitest or Jest for regression testing "
            "(consider: npm install -D vitest @vitest/ui or jest)."
        )

    # 3. Map applicable patterns to prioritized list (by severity)
    priority_patterns = []
    by_severity = {}

    for pattern in context.applicable_patterns:
        severity = pattern.get("severity", "medium")
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(pattern)

        # Track reference files
        ref_file = pattern.get("reference_file", "")
        if ref_file:
            reference_files.add(ref_file)

    # Build priority list: critical → high → medium → low
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    for severity in sorted(by_severity.keys(), key=lambda s: severity_order.get(s, 999)):
        patterns = by_severity[severity]
        for pat in sorted(patterns, key=lambda p: p.get("id", "")):
            priority_patterns.append({
                "id": pat.get("id", ""),
                "title": pat.get("title", ""),
                "severity": severity,
                "reference_file": pat.get("reference_file", "")
            })

    # 4. Signal-based recommendations (if diff provided)
    if signal_report:
        signals = signal_report.signals

        # High dependency fan-out
        if signals.get("dependency_fan", {}).get("normalized", 0) >= 0.80:
            recommendations.append(
                f"⚠ HIGH dependency_fan (0.85+): Review all modules that import changed exports. "
                f"Risk of cascading failures."
            )

        # High AST depth
        if signals.get("ast_depth", {}).get("normalized", 0) >= 0.85:
            recommendations.append(
                "⚠ HIGH ast_depth: Structural changes detected. Recommend architectural review "
                "and comprehensive regression testing."
            )

        # Type surface impact
        if signals.get("type_surface", {}).get("normalized", 0) >= 0.70:
            recommendations.append(
                "Type system changes detected. Ensure all consumers handle new/changed types. "
                "Run type-check and update dependent code."
            )

        # Add verification level recommendation
        levels_req = signal_report.depth_decision.get("levels_required", [1, 2, 3, 4])
        levels_rec = signal_report.depth_decision.get("levels_recommended", [])

        level_names = {
            1: "Syntax", 2: "Types", 3: "Lint", 4: "Tests",
            5: "Regression", 6: "Performance", 7: "Visual", 8: "Security"
        }

        req_names = [level_names.get(l, f"L{l}") for l in levels_req if l > 4]
        rec_names = [level_names.get(l, f"L{l}") for l in levels_rec if l > 4]

        if req_names:
            recommendations.append(
                f"Verification levels required: {', '.join(req_names)}"
            )
        if rec_names:
            recommendations.append(
                f"Additional verification levels recommended: {', '.join(rec_names)}"
            )

        # Reference for fix safety procedures
        recommendations.append(
            "Read references/fix-safety.md for L5-L8 verification procedures and checklists."
        )
        reference_files.add("fix-safety.md")

    # 5. Framework-specific recommendations
    framework_names = {f.get("name", "").lower() for f in context.frameworks}

    if "react" in framework_names:
        if not any("react" in p.get("reference_file", "").lower() for p in context.applicable_patterns):
            recommendations.append(
                "React project detected. Review references/react-bugs.md for common pitfalls "
                "(hooks, closures, re-renders)."
            )
            reference_files.add("react-bugs.md")
        # Always add performance refs for React projects
        reference_files.add("react-performance.md")

    if "next.js" in framework_names:
        if not any("nextjs" in p.get("reference_file", "").lower() for p in context.applicable_patterns):
            recommendations.append(
                "Next.js project detected. Review references/nextjs-bugs.md for framework-specific issues."
            )
            reference_files.add("nextjs-bugs.md")
        # Always add mobile optimization for Next.js projects
        reference_files.add("mobile-optimization.md")

    if "three.js" in framework_names:
        recommendations.append(
            "Three.js/3D project detected. Verify GPU memory cleanup and shader compilation. "
            "Run WebGL error checks. See references/performance-patterns.md for P1-P7 fix catalog."
        )
        reference_files.add("threejs-bugs.md")
        reference_files.add("performance-patterns.md")
        reference_files.add("threejs-webgl-performance.md")

    return recommendations, priority_patterns, sorted(list(reference_files))


# =============================================================================
# UNIFIED ANALYSIS
# =============================================================================

def run_unified_pipeline(
    project_path: str,
    diff_file: Optional[str] = None,
    severity: str = "medium",
    context_only: bool = False,
    verbose: bool = False,
) -> DebugReport:
    """
    Run the full unified debugging pipeline.

    Steps:
    1. Run context analyzer
    2. (Optional) Run fix signal analyzer
    3. Synthesize recommendations
    """

    report = DebugReport(project_path=project_path)

    # Phase 0: Context analysis
    try:
        context = analyze_project(project_path)
        report.project_path = context.project_path
        report.project_type = context.project_type
        report.project_type_confidence = context.project_type_confidence
        report.frameworks = context.frameworks
        report.applicable_patterns = context.applicable_patterns
        report.has_typescript = context.has_typescript
        report.has_tests = context.has_tests
        report.source_files_count = context.source_files_count
        report.total_lines = context.total_lines
    except Exception as e:
        print(f"Error during context analysis: {e}", file=sys.stderr)
        return report

    # Phase 3→4: Signal analysis (optional)
    signal_report = None
    if diff_file and not context_only:
        if not os.path.exists(diff_file):
            print(f"Error: Diff file not found: {diff_file}", file=sys.stderr)
            return report

        try:
            with open(diff_file, "r", encoding="utf-8") as f:
                diff_text = f.read()

            signal_report = analyze_fix(
                diff_text=diff_text,
                project_path=project_path,
                project_type=report.project_type,
                severity=severity,
            )

            # Populate signal data into report
            report.verification_depth = signal_report.verification_depth
            report.depth_category = signal_report.depth_category
            report.signals = signal_report.signals
            report.levels_required = signal_report.depth_decision.get("levels_required", [1, 2, 3, 4])
            report.levels_recommended = signal_report.depth_decision.get("levels_recommended", [])
            report.veto_triggered = signal_report.veto.get("triggered", False)
            report.severity_override = signal_report.severity_ratchet.get("applied", False)

        except Exception as e:
            print(f"Error during signal analysis: {e}", file=sys.stderr)
            return report

    # Synthesis: Generate recommendations
    try:
        recommendations, priority_patterns, ref_files = generate_recommendations(context, signal_report)
        report.recommendations = recommendations
        report.priority_patterns = priority_patterns
        report.reference_files_needed = ref_files
    except Exception as e:
        print(f"Error during recommendation synthesis: {e}", file=sys.stderr)

    return report


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_text_output(report: DebugReport) -> str:
    """Format report as human-readable text."""

    lines = [
        "=" * 64,
        "  ULTIMATE DEBUGGER — UNIFIED ANALYSIS REPORT",
        "=" * 64,
        "",
        "  PROJECT CONTEXT",
        "  " + "─" * 60,
        f"  Type:          {report.project_type} (confidence: {report.project_type_confidence:.0%})",
        f"  Frameworks:    {', '.join(f['name'] for f in report.frameworks) if report.frameworks else '(none)'}",
        f"  Tests:         {'Yes' if report.has_tests else 'No'}",
        f"  TypeScript:    {'Yes' if report.has_typescript else 'No'}",
        f"  Source Files:  {report.source_files_count}",
        f"  Total Lines:   {report.total_lines:,}",
        "",
    ]

    # Applicable patterns
    lines.extend([
        "  APPLICABLE BUG PATTERNS ({} total)".format(len(report.applicable_patterns)),
        "  " + "─" * 60,
    ])

    if report.applicable_patterns:
        by_severity = {}
        for pat in report.applicable_patterns:
            severity = pat.get("severity", "medium")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(pat)

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for severity in sorted(by_severity.keys(), key=lambda s: severity_order.get(s, 999)):
            patterns = by_severity[severity]
            lines.append(f"  [{severity.upper()}] {len(patterns)} patterns")
            for pat in sorted(patterns, key=lambda p: p.get("id", ""))[:5]:  # Show top 5
                ref_file = pat.get("reference_file", "code-quality.md")
                lines.append(f"    {pat.get('id', '')}: {pat.get('title', '')} → {ref_file}")
            if len(patterns) > 5:
                lines.append(f"    ... and {len(patterns) - 5} more")
    else:
        lines.append("  (none detected)")

    # Fix signal analysis (if diff provided)
    if report.verification_depth > 0:
        lines.extend([
            "",
            "  FIX SIGNAL ANALYSIS",
            "  " + "─" * 60,
        ])

        depth = report.verification_depth
        bar_len = int(depth * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        lines.append(f"  Verification Depth: {depth:.2f}  [{bar}]")
        lines.append(f"  Category:           {report.depth_category.upper()}")
        lines.append("")

        # Signal breakdown
        if report.signals:
            lines.append("  Signal Scores:")
            for name in ["diff_size", "files_touched", "ast_depth", "type_surface", "test_surface", "dependency_fan"]:
                if name in report.signals:
                    sig = report.signals[name]
                    normalized = sig.get("normalized", 0)
                    mini_bar = "▓" * int(normalized * 10) + "░" * (10 - int(normalized * 10))
                    lines.append(f"    {name:<18} {normalized:.2f}  {mini_bar}")
            lines.append("")

        # Verification levels
        lines.append("  Verification Levels:")
        level_names = {
            1: "Syntax", 2: "Types", 3: "Lint", 4: "Tests",
            5: "Regression", 6: "Performance", 7: "Visual", 8: "Security",
        }
        for lvl in range(1, 9):
            name = level_names[lvl]
            if lvl in report.levels_required:
                status = "██ MANDATORY"
            elif lvl in report.levels_recommended:
                status = "▓▓ RECOMMENDED"
            else:
                status = "░░ skipped"
            lines.append(f"    L{lvl}: {name:<12}  {status}")

        if report.veto_triggered:
            lines.append("    ⚠ VETO: High-risk fix — full verification required")

        lines.append("")

    # Recommendations
    if report.recommendations:
        lines.extend([
            "  RECOMMENDATIONS",
            "  " + "─" * 60,
        ])
        for i, rec in enumerate(report.recommendations, 1):
            # Word wrap at 56 chars
            words = rec.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > 56:
                    lines.append(f"  {i}. {line}")
                    line = word
                    i = ""  # Don't repeat number
                else:
                    line = f"{line} {word}".strip()
            if line:
                lines.append(f"  {i}. {line}" if i else f"     {line}")
        lines.append("")

    # Reference files
    if report.reference_files_needed:
        lines.extend([
            "  REFERENCE FILES TO LOAD",
            "  " + "─" * 60,
        ])
        for ref_file in sorted(report.reference_files_needed):
            # Count applicable patterns from this file
            count = sum(1 for p in report.applicable_patterns
                       if ref_file in p.get("reference_file", ""))
            if count > 0:
                lines.append(f"  • {ref_file} ({count} applicable patterns)")
            else:
                lines.append(f"  • {ref_file}")
        lines.append("")

    lines.append("=" * 64)
    return "\n".join(lines)


def format_json_output(report: DebugReport) -> str:
    """Format report as JSON."""
    return json.dumps(asdict(report), indent=2, default=str)


def format_yaml_output(report: DebugReport) -> str:
    """Format report as YAML."""
    lines = ["# ULTIMATE DEBUGGER — UNIFIED ANALYSIS REPORT"]

    lines.append("project_context:")
    lines.append(f"  path: {report.project_path}")
    lines.append(f"  type: {report.project_type}")
    lines.append(f"  type_confidence: {report.project_type_confidence}")
    lines.append(f"  has_typescript: {report.has_typescript}")
    lines.append(f"  has_tests: {report.has_tests}")
    lines.append(f"  source_files: {report.source_files_count}")
    lines.append(f"  total_lines: {report.total_lines}")

    if report.frameworks:
        lines.append("  frameworks:")
        for fw in report.frameworks:
            lines.append(f"    - name: {fw.get('name', '')}")
            lines.append(f"      version: {fw.get('version', '')}")

    if report.applicable_patterns:
        lines.append("  applicable_patterns_count: {}".format(len(report.applicable_patterns)))

    if report.verification_depth > 0:
        lines.append("")
        lines.append("fix_signal_analysis:")
        lines.append(f"  verification_depth: {report.verification_depth}")
        lines.append(f"  depth_category: {report.depth_category}")
        lines.append(f"  veto_triggered: {report.veto_triggered}")
        lines.append(f"  severity_override: {report.severity_override}")

        if report.signals:
            lines.append("  signals:")
            for name, sig in report.signals.items():
                lines.append(f"    {name}:")
                lines.append(f"      normalized: {sig.get('normalized', 0)}")
                lines.append(f"      reasoning: \"{sig.get('reasoning', '')}\"")

    if report.recommendations:
        lines.append("")
        lines.append("recommendations:")
        for rec in report.recommendations:
            lines.append(f"  - {rec}")

    if report.reference_files_needed:
        lines.append("")
        lines.append("reference_files:")
        for ref in report.reference_files_needed:
            lines.append(f"  - {ref}")

    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Ultimate Debugger — Unified Analysis Pipeline",
        epilog="Chains context analysis and fix signal analysis into one workflow.",
    )

    parser.add_argument(
        "project_path",
        help="Path to project root",
    )

    parser.add_argument(
        "--diff",
        type=str,
        default=None,
        help="Path to unified diff file (enables signal analysis)",
    )

    parser.add_argument(
        "--severity",
        type=str,
        default="medium",
        choices=["critical", "high", "medium", "low"],
        help="Bug severity: critical|high|medium|low (default: medium)",
    )

    parser.add_argument(
        "--format",
        type=str,
        default="text",
        choices=["text", "json", "yaml"],
        help="Output format: text|json|yaml (default: text)",
    )

    parser.add_argument(
        "--context-only",
        action="store_true",
        help="Only run context analysis (skip signal analysis)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed signal breakdown",
    )

    args = parser.parse_args()

    # Validate project path
    if not os.path.isdir(args.project_path):
        print(f"Error: {args.project_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Run pipeline
    report = run_unified_pipeline(
        project_path=args.project_path,
        diff_file=args.diff,
        severity=args.severity,
        context_only=args.context_only,
        verbose=args.verbose,
    )

    # Format and output
    if args.format == "json":
        output = format_json_output(report)
    elif args.format == "yaml":
        output = format_yaml_output(report)
    else:  # text (default)
        output = format_text_output(report)

    print(output)


if __name__ == "__main__":
    main()
