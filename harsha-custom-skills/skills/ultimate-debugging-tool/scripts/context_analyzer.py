#!/usr/bin/env python3
"""
Context Analyzer for Ultimate Debugger
Detects project type, frameworks, skill patterns, and sets adaptive budgets.
Run BEFORE any debugging or performance analysis.

Usage:
    python context_analyzer.py /path/to/project
    python context_analyzer.py /path/to/project --format json
    python context_analyzer.py /path/to/project --format yaml
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class FrameworkDetection:
    name: str
    version: str = ""
    confidence: float = 0.0


@dataclass
class SkillPattern:
    skill: str
    pattern: str
    confidence: float = 0.0
    file: str = ""
    line: int = 0


@dataclass
class ProjectContext:
    project_path: str = ""
    project_type: str = "unknown"  # 3d-experience | animation-site | react-spa | dashboard | hybrid
    project_type_confidence: float = 0.0
    frameworks: list = field(default_factory=list)
    skill_patterns: list = field(default_factory=list)
    applicable_patterns: list = field(default_factory=list)  # List of pattern IDs from pattern-index.json
    budget_profile: str = "budget-spa"  # default
    has_typescript: bool = False
    has_tests: bool = False
    package_manager: str = "unknown"
    source_files_count: int = 0
    total_lines: int = 0


# --- Dependency signals for project type ---
THREE_JS_DEPS = {"three", "@react-three/fiber", "@react-three/drei", "@react-three/postprocessing"}
ANIMATION_DEPS = {"gsap", "@gsap/react", "framer-motion", "lenis", "@studio-freight/lenis"}
REACT_DEPS = {"react", "react-dom", "next", "remix", "@remix-run/react", "gatsby"}
DASHBOARD_DEPS = {"chart.js", "recharts", "d3", "nivo", "victory", "ag-grid-react", "plotly.js"}
QUALITY_DEPS = {"detect-gpu", "@pmndrs/postprocessing", "postprocessing"}

# --- Skill pattern signatures ---
SKILL_3D_PATTERNS = {
    "gsap-proxy": r"gsap\.\w+\([^,]+,\s*\{[^}]*onUpdate",
    "lag-smoothing": r"lagSmoothing\s*\(\s*0\s*\)",
    "delta-capping": r"Math\.min\s*\(\s*\w+\.getDelta\(\)\s*,\s*1\s*/\s*30\s*\)",
    "effect-composer": r"EffectComposer|new\s+Effect(?:Composer|Pass)",
    "detect-gpu-tiers": r"getGPUTier|detectGPU|gpuTier",
    "mesh-physical": r"MeshPhysicalMaterial",
    "hdr-environment": r"RGBELoader|HDRCubeTextureLoader|useEnvironment",
    "studio-lighting": r"DirectionalLight.*DirectionalLight.*DirectionalLight",
    "pixel-ratio-cap": r"Math\.min\s*\(\s*window\.devicePixelRatio\s*,\s*[12]",
    "resource-dispose": r"\.dispose\s*\(\s*\)",
    "page-visibility": r"visibilitychange|document\.hidden",
}

SKILL_UIUX_PATTERNS = {
    "motion-timing-vars": r"--duration-(fast|normal|slow|instant)",
    "reduced-motion": r"prefers-reduced-motion",
    "ease-curves": r"--ease-(out|in|in-out)",
    "skeleton-screen": r"skeleton|Skeleton",
}

# --- File extension mapping ---
SOURCE_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".css", ".scss", ".less",
    ".html", ".vue", ".svelte",
    ".glsl", ".frag", ".vert", ".wgsl",
}

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", ".next", ".nuxt",
    "coverage", ".cache", ".turbo", "out", ".vercel",
    "__pycache__", ".debug-session", ".ultimate-debugger",
}


def read_package_json(project_path: str) -> Optional[dict]:
    """Read and parse package.json."""
    pkg_path = os.path.join(project_path, "package.json")
    if not os.path.exists(pkg_path):
        return None
    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def detect_frameworks(pkg: dict) -> list:
    """Detect frameworks from package.json dependencies."""
    frameworks = []
    all_deps = {}
    for dep_key in ("dependencies", "devDependencies", "peerDependencies"):
        if dep_key in pkg:
            all_deps.update(pkg[dep_key])

    framework_map = {
        "react": "React",
        "next": "Next.js",
        "@remix-run/react": "Remix",
        "gatsby": "Gatsby",
        "vue": "Vue",
        "svelte": "Svelte",
        "@angular/core": "Angular",
        "solid-js": "SolidJS",
        "three": "Three.js",
        "@react-three/fiber": "React Three Fiber",
        "gsap": "GSAP",
        "framer-motion": "Framer Motion",
        "lenis": "Lenis",
        "@studio-freight/lenis": "Lenis",
        "d3": "D3.js",
        "chart.js": "Chart.js",
        "recharts": "Recharts",
        "typescript": "TypeScript",
        "vitest": "Vitest",
        "jest": "Jest",
        "playwright": "Playwright",
        "cypress": "Cypress",
    }

    for dep_name, display_name in framework_map.items():
        if dep_name in all_deps:
            version = all_deps[dep_name].lstrip("^~>=<")
            frameworks.append(FrameworkDetection(
                name=display_name,
                version=version,
                confidence=1.0,
            ))

    return frameworks


def detect_project_type(pkg: dict, frameworks: list) -> tuple:
    """Determine project type from dependencies."""
    if pkg is None:
        return "unknown", 0.3

    all_deps = set()
    for dep_key in ("dependencies", "devDependencies"):
        if dep_key in pkg:
            all_deps.update(pkg[dep_key].keys())

    scores = {
        "3d-experience": 0.0,
        "animation-site": 0.0,
        "react-spa": 0.0,
        "dashboard": 0.0,
    }

    # Score based on dependencies
    for dep in all_deps:
        if dep in THREE_JS_DEPS:
            scores["3d-experience"] += 3.0
        if dep in ANIMATION_DEPS:
            scores["animation-site"] += 2.0
            scores["3d-experience"] += 0.5  # 3D sites also use animation
        if dep in REACT_DEPS:
            scores["react-spa"] += 1.5
        if dep in DASHBOARD_DEPS:
            scores["dashboard"] += 3.0
        if dep in QUALITY_DEPS:
            scores["3d-experience"] += 1.5

    # If 3D and animation both high, it's 3D (3D sites always have animation)
    if scores["3d-experience"] >= 3.0:
        scores["animation-site"] *= 0.5  # Reduce animation score for 3D projects

    # Find winner
    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    if best_score < 1.0:
        return "unknown", 0.3

    # Check for hybrid
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_scores) >= 2 and sorted_scores[1][1] > 2.0:
        if sorted_scores[0][1] - sorted_scores[1][1] < 2.0:
            return "hybrid", min(0.7, best_score / 10.0)

    confidence = min(0.95, best_score / 10.0)
    return best_type, confidence


def scan_for_skill_patterns(project_path: str) -> list:
    """Scan source files for skill pattern signatures."""
    patterns_found = []
    files_scanned = 0
    max_files = 200  # Limit for performance

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SOURCE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            files_scanned += 1
            if files_scanned > max_files:
                break

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except (IOError, PermissionError):
                continue

            rel_path = os.path.relpath(filepath, project_path)

            # Check 3D skill patterns
            for pattern_name, regex in SKILL_3D_PATTERNS.items():
                for match in re.finditer(regex, content):
                    line_num = content[:match.start()].count("\n") + 1
                    patterns_found.append(SkillPattern(
                        skill="3d-web-graphics-mastery",
                        pattern=pattern_name,
                        confidence=0.85,
                        file=rel_path,
                        line=line_num,
                    ))

            # Check UI/UX skill patterns
            for pattern_name, regex in SKILL_UIUX_PATTERNS.items():
                for match in re.finditer(regex, content):
                    line_num = content[:match.start()].count("\n") + 1
                    patterns_found.append(SkillPattern(
                        skill="ui-ux-mastery",
                        pattern=pattern_name,
                        confidence=0.75,
                        file=rel_path,
                        line=line_num,
                    ))

        if files_scanned > max_files:
            break

    return patterns_found


def count_source_files(project_path: str) -> tuple:
    """Count source files and estimate total lines."""
    file_count = 0
    total_lines = 0

    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SOURCE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            file_count += 1

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    total_lines += sum(1 for _ in f)
            except (IOError, PermissionError):
                continue

    return file_count, total_lines


def determine_budget_profile(project_type: str) -> str:
    """Map project type to budget profile."""
    return {
        "3d-experience": "budget-3d",
        "animation-site": "budget-animation",
        "react-spa": "budget-spa",
        "dashboard": "budget-dashboard",
        "hybrid": "budget-hybrid",
    }.get(project_type, "budget-spa")


def load_pattern_index(skill_path: str) -> list:
    """Load the structured pattern index from pattern-index.json."""
    index_path = os.path.join(skill_path, "references", "pattern-index.json")
    if not os.path.exists(index_path):
        return []
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("patterns", [])
    except (json.JSONDecodeError, IOError):
        return []


def map_applicable_patterns(ctx: ProjectContext, patterns: list) -> list:
    """Map detected frameworks to applicable bug patterns."""
    applicable = []
    framework_names = {f["name"].lower() for f in ctx.frameworks}

    # Map framework detection names to pattern framework names
    framework_map = {
        "react": "React",
        "next.js": "Next.js",
        "three.js": "Three.js",
        "react three fiber": "Three.js",
        "gsap": "GSAP",
        "framer motion": "GSAP",  # animation patterns may apply
        "typescript": "TypeScript",
    }

    detected_pattern_frameworks = set()
    for fw_name in framework_names:
        mapped = framework_map.get(fw_name)
        if mapped:
            detected_pattern_frameworks.add(mapped)

    for pattern in patterns:
        if pattern.get("framework") in detected_pattern_frameworks:
            applicable.append(pattern)

    return applicable


def analyze_project(project_path: str) -> ProjectContext:
    """Full project context analysis."""
    ctx = ProjectContext(project_path=project_path)

    # Read package.json
    pkg = read_package_json(project_path)

    if pkg:
        # Detect frameworks
        ctx.frameworks = [asdict(f) for f in detect_frameworks(pkg)]

        # Detect project type
        framework_objs = detect_frameworks(pkg)
        ctx.project_type, ctx.project_type_confidence = detect_project_type(pkg, framework_objs)

        # Check for TypeScript
        all_deps = {}
        for dep_key in ("dependencies", "devDependencies"):
            if dep_key in pkg:
                all_deps.update(pkg[dep_key])
        ctx.has_typescript = "typescript" in all_deps

        # Check for tests
        ctx.has_tests = any(d in all_deps for d in ("vitest", "jest", "playwright", "cypress", "@testing-library/react"))

        # Detect package manager
        if os.path.exists(os.path.join(project_path, "pnpm-lock.yaml")):
            ctx.package_manager = "pnpm"
        elif os.path.exists(os.path.join(project_path, "yarn.lock")):
            ctx.package_manager = "yarn"
        elif os.path.exists(os.path.join(project_path, "bun.lockb")):
            ctx.package_manager = "bun"
        elif os.path.exists(os.path.join(project_path, "package-lock.json")):
            ctx.package_manager = "npm"

    # Scan for skill patterns
    skill_patterns = scan_for_skill_patterns(project_path)
    ctx.skill_patterns = [asdict(p) for p in skill_patterns]

    # Boost confidence if skill patterns confirm project type
    skills_3d = [p for p in skill_patterns if p.skill == "3d-web-graphics-mastery"]
    if len(skills_3d) >= 3 and ctx.project_type == "3d-experience":
        ctx.project_type_confidence = min(0.95, ctx.project_type_confidence + 0.15)
    elif len(skills_3d) >= 3 and ctx.project_type != "3d-experience":
        ctx.project_type = "3d-experience"
        ctx.project_type_confidence = 0.8

    # Set budget profile
    ctx.budget_profile = determine_budget_profile(ctx.project_type)

    # Map applicable bug patterns
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_patterns = load_pattern_index(skill_dir)
    applicable = map_applicable_patterns(ctx, all_patterns)
    ctx.applicable_patterns = [
        {
            "id": p["id"],
            "title": p["title"],
            "severity": p.get("severity", "medium"),
            "reference_file": p.get("reference_file", "")
        }
        for p in applicable
    ]

    # Count source files
    ctx.source_files_count, ctx.total_lines = count_source_files(project_path)

    return ctx


def format_output(ctx: ProjectContext, fmt: str = "text") -> str:
    """Format the analysis output."""
    if fmt == "json":
        return json.dumps(asdict(ctx), indent=2, default=str)

    if fmt == "yaml":
        lines = ["# Project Context Analysis", f"project_path: {ctx.project_path}"]
        lines.append(f"project_type: {ctx.project_type}")
        lines.append(f"project_type_confidence: {ctx.project_type_confidence}")
        lines.append(f"budget_profile: {ctx.budget_profile}")
        lines.append(f"has_typescript: {ctx.has_typescript}")
        lines.append(f"has_tests: {ctx.has_tests}")
        lines.append(f"source_files: {ctx.source_files_count}")
        lines.append(f"total_lines: {ctx.total_lines}")
        lines.append(f"frameworks:")
        for fw in ctx.frameworks:
            lines.append(f"  - name: {fw['name']}")
            lines.append(f"    version: {fw['version']}")
        lines.append(f"skill_patterns_count: {len(ctx.skill_patterns)}")
        unique_skills = set(p["skill"] for p in ctx.skill_patterns)
        for skill in unique_skills:
            patterns = [p for p in ctx.skill_patterns if p["skill"] == skill]
            lines.append(f"  {skill}: {len(patterns)} patterns detected")
            unique_patterns = set(p["pattern"] for p in patterns)
            for pname in sorted(unique_patterns):
                lines.append(f"    - {pname}")
        lines.append(f"applicable_patterns_count: {len(ctx.applicable_patterns)}")
        if ctx.applicable_patterns:
            lines.append(f"applicable_patterns:")
            for pat in sorted(ctx.applicable_patterns, key=lambda p: p["id"]):
                lines.append(f"  - id: {pat['id']}")
                lines.append(f"    title: {pat['title']}")
                lines.append(f"    severity: {pat.get('severity', 'medium')}")
        return "\n".join(lines)

    # Text format (default)
    lines = [
        "=" * 60,
        "  ULTIMATE DEBUGGER — PROJECT CONTEXT ANALYSIS",
        "=" * 60,
        "",
        f"  Project:     {ctx.project_path}",
        f"  Type:        {ctx.project_type} (confidence: {ctx.project_type_confidence:.0%})",
        f"  Budget:      {ctx.budget_profile}",
        f"  TypeScript:  {'Yes' if ctx.has_typescript else 'No'}",
        f"  Tests:       {'Yes' if ctx.has_tests else 'No — RECOMMEND ADDING'}",
        f"  Pkg Manager: {ctx.package_manager}",
        f"  Source Files: {ctx.source_files_count}",
        f"  Total Lines: {ctx.total_lines:,}",
        "",
        "  FRAMEWORKS DETECTED:",
    ]

    if ctx.frameworks:
        for fw in ctx.frameworks:
            lines.append(f"    • {fw['name']} {fw['version']}")
    else:
        lines.append("    (none detected)")

    lines.append("")
    lines.append("  SKILL PATTERNS DETECTED:")

    if ctx.skill_patterns:
        unique_skills = set(p["skill"] for p in ctx.skill_patterns)
        for skill in sorted(unique_skills):
            patterns = [p for p in ctx.skill_patterns if p["skill"] == skill]
            lines.append(f"    {skill}: {len(patterns)} patterns")
            unique_patterns = set(p["pattern"] for p in patterns)
            for pname in sorted(unique_patterns):
                count = sum(1 for p in patterns if p["pattern"] == pname)
                lines.append(f"      • {pname} ({count}x)")
    else:
        lines.append("    (none detected — standard performance rules apply)")

    lines.extend([
        "",
        "  APPLICABLE BUG PATTERNS:",
    ])

    if ctx.applicable_patterns:
        # Group by severity
        by_severity = {}
        for pat in ctx.applicable_patterns:
            severity = pat.get("severity", "medium")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(pat)

        # Sort by severity (critical > high > medium > low)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for severity in sorted(by_severity.keys(), key=lambda s: severity_order.get(s, 999)):
            patterns = by_severity[severity]
            lines.append(f"    [{severity.upper()}]")
            for pat in sorted(patterns, key=lambda p: p["id"]):
                ref_file = pat.get("reference_file", "code-quality.md")
                lines.append(f"      {pat['id']}: {pat['title']} → See {ref_file}")
    else:
        lines.append("    (none detected — no known patterns in detected frameworks)")

    lines.extend([
        "",
        "  RECOMMENDATIONS:",
    ])

    if not ctx.has_tests:
        lines.append("    ⚠ No test framework detected. Add Vitest or Jest for regression testing.")
    if not ctx.has_typescript:
        lines.append("    ⚠ No TypeScript detected. Consider adding for type-safety bug prevention.")
    if ctx.project_type == "3d-experience" and not any(
        p["pattern"] == "detect-gpu-tiers" for p in ctx.skill_patterns
    ):
        lines.append("    ⚠ 3D project without quality tier system. Add detect-gpu for adaptive quality.")
    if ctx.project_type in ("animation-site", "3d-experience") and not any(
        p["pattern"] == "reduced-motion" for p in ctx.skill_patterns
    ):
        lines.append("    ⚠ Animation project missing prefers-reduced-motion. Accessibility requirement.")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python context_analyzer.py /path/to/project [--format json|yaml|text]")
        sys.exit(1)

    project_path = sys.argv[1]
    output_format = "text"

    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not os.path.isdir(project_path):
        print(f"Error: {project_path} is not a directory")
        sys.exit(1)

    context = analyze_project(project_path)
    print(format_output(context, output_format))
