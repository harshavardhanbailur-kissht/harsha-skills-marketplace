#!/usr/bin/env python3
"""
Fix Signal Analyzer for Ultimate Debugger — Adaptive Verification Pipeline (AVP)

Analyzes a designed fix (diff) AFTER Phase 3 (Fix Design) and BEFORE Phase 4
(Implement & Verify) to determine the appropriate verification depth.

Core Principle: Classify the FIX, not the bug. Bug descriptions are unreliable
predictors of complexity. Fix characteristics (diff size, files touched, type
surface area, dependency fan-out) are measurable and objective.

Usage:
    python fix_signal_analyzer.py <diff_file_or_stdin> [options]
    python fix_signal_analyzer.py --diff /path/to/fix.diff
    python fix_signal_analyzer.py --files changed_file1.ts changed_file2.tsx
    python fix_signal_analyzer.py --diff fix.diff --project-type react-spa --format json
    cat fix.diff | python fix_signal_analyzer.py --stdin

Options:
    --diff PATH           Path to unified diff file
    --files PATH [PATH..] Changed file paths (analyzes current content)
    --stdin               Read diff from stdin
    --project-path PATH   Project root (for dependency fan-out detection)
    --project-type TYPE   Project type override (3d-experience | animation-site |
                          react-spa | dashboard | hybrid)
    --severity LEVEL      Bug severity (critical | high | medium | low)
    --format FORMAT       Output format (text | json | yaml)
    --weights PATH        Custom weights file (YAML)
    --verbose             Show detailed signal analysis

Signals Measured:
    1. diff_size        Lines changed (normalized by relative churn)
    2. files_touched    Count of modified files
    3. ast_depth        Nature of change (leaf | branch | structural)
    4. type_surface     Type system impact (new types, changed signatures)
    5. test_surface     Test coverage breadth
    6. dependency_fan   Downstream impact (callers affected)

Output:
    Composite verification_depth score (0.0 → 1.0) plus individual signals,
    depth decision (which verification levels L5-L8 are recommended), and
    any veto/ratchet overrides.

Design Decisions (see docs/avp-design-decisions.md):
    - Weighted sum with veto layer (not simple average)
    - Diffusion/entropy signals weighted highest (Kamei et al. 2012)
    - Relative churn normalization (Nagappan & Ball 2005)
    - Veto triggers prevent high-risk fixes from scoring low
    - Severity ratchet forces deep verification for critical/high bugs
    - Smooth thresholds with configurable boundaries
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict, Tuple


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class SignalScore:
    """Individual signal measurement with raw value and normalized score."""
    name: str
    raw_value: float = 0.0
    normalized: float = 0.0  # 0.0 - 1.0
    reasoning: str = ""


@dataclass
class VetoCheck:
    """Veto trigger that forces minimum composite score."""
    triggered: bool = False
    reason: str = ""
    minimum_score: float = 0.0


@dataclass
class DepthDecision:
    """Verification depth decision with level recommendations."""
    levels_required: list = field(default_factory=lambda: [1, 2, 3, 4])
    levels_recommended: list = field(default_factory=list)
    severity_override: bool = False
    veto_override: bool = False
    escalation_hints: list = field(default_factory=list)


@dataclass
class FixSignalReport:
    """Complete fix signal analysis report."""
    # Input metadata
    diff_file: str = ""
    project_path: str = ""
    project_type: str = "unknown"
    severity: str = "medium"

    # Individual signals
    signals: dict = field(default_factory=dict)

    # Composite score
    verification_depth: float = 0.0
    depth_category: str = "minimal"  # minimal | low | moderate | high | full

    # Veto and override checks
    veto: dict = field(default_factory=dict)
    severity_ratchet: dict = field(default_factory=dict)

    # Depth decision
    depth_decision: dict = field(default_factory=dict)

    # Weights used
    weights_used: dict = field(default_factory=dict)

    # Warnings and notes
    warnings: list = field(default_factory=list)


# =============================================================================
# SIGNAL WEIGHTS — Research-backed defaults
# =============================================================================
# Based on Kamei et al. (2012) JIT defect prediction, Hassan (2009) entropy
# metrics, and Nagappan & Ball (2005) relative code churn research.
#
# Diffusion/entropy signals are weighted highest because scattered changes
# across multiple files with structural modifications are the strongest
# predictors of regression risk.

DEFAULT_WEIGHTS = {
    "diff_size": 0.20,
    "files_touched": 0.15,
    "ast_depth": 0.20,
    "type_surface": 0.10,
    "test_surface": 0.12,
    "dependency_fan": 0.23,
}

# Project-type weight adjustments (additive deltas)
# Applied on top of DEFAULT_WEIGHTS when --project-type is specified
PROJECT_TYPE_ADJUSTMENTS = {
    "3d-experience": {
        "ast_depth": +0.05,
        "type_surface": -0.03,
        "dependency_fan": -0.02,
    },
    "animation-site": {
        "ast_depth": +0.04,
        "test_surface": -0.04,
    },
    "react-spa": {
        "test_surface": +0.05,
        "type_surface": +0.03,
        "dependency_fan": -0.05,
        "ast_depth": -0.03,
    },
    "dashboard": {
        "test_surface": +0.04,
        "diff_size": +0.03,
        "ast_depth": -0.04,
        "dependency_fan": -0.03,
    },
    "hybrid": {},  # No adjustments
}

# Depth thresholds — configurable boundaries for verification levels
# These use smooth transitions rather than hard cliffs
DEPTH_THRESHOLDS = {
    "L5_only": 0.25,      # verification_depth < 0.25 → L5 only
    "L5_L6": 0.50,        # 0.25 ≤ depth < 0.50 → L5 + L6
    "L5_L6_L7": 0.75,     # 0.50 ≤ depth < 0.75 → L5 + L6 + L7
    "full": 0.75,          # depth ≥ 0.75 → L5 + L6 + L7 + L8
}

# Veto thresholds — any single signal above these forces minimum composite
VETO_THRESHOLDS = {
    "dependency_fan": 0.80,
    "ast_depth": 0.85,
    "type_surface": 0.85,
}
VETO_MINIMUM_SCORE = 0.55


# =============================================================================
# DIFF PARSING
# =============================================================================

@dataclass
class DiffHunk:
    """A single hunk from a unified diff."""
    file_path: str = ""
    old_start: int = 0
    old_count: int = 0
    new_start: int = 0
    new_count: int = 0
    added_lines: list = field(default_factory=list)
    removed_lines: list = field(default_factory=list)
    context_lines: list = field(default_factory=list)


@dataclass
class ParsedDiff:
    """Complete parsed diff with file-level and line-level information."""
    files_changed: list = field(default_factory=list)
    hunks: list = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    total_changes: int = 0
    binary_files: list = field(default_factory=list)


def parse_unified_diff(diff_text: str) -> ParsedDiff:
    """Parse a unified diff into structured data."""
    result = ParsedDiff()
    current_file = None
    current_hunk = None

    # Track files
    file_pattern = re.compile(r'^(?:diff --git a/(.*?) b/|--- a/(.*)|(?:\+\+\+) b/(.*))')
    hunk_pattern = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')
    binary_pattern = re.compile(r'^Binary files .* differ$')

    for line in diff_text.splitlines():
        # Detect file header
        file_match = file_pattern.match(line)
        if file_match:
            path = file_match.group(1) or file_match.group(2) or file_match.group(3)
            if path and path not in result.files_changed and path != "/dev/null":
                current_file = path
                if current_file not in result.files_changed:
                    result.files_changed.append(current_file)
            continue

        # Detect binary files
        if binary_pattern.match(line):
            if current_file:
                result.binary_files.append(current_file)
            continue

        # Detect hunk header
        hunk_match = hunk_pattern.match(line)
        if hunk_match:
            current_hunk = DiffHunk(
                file_path=current_file or "",
                old_start=int(hunk_match.group(1)),
                old_count=int(hunk_match.group(2) or 1),
                new_start=int(hunk_match.group(3)),
                new_count=int(hunk_match.group(4) or 1),
            )
            result.hunks.append(current_hunk)
            continue

        # Parse hunk content
        if current_hunk is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current_hunk.added_lines.append(line[1:])
                result.total_additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                current_hunk.removed_lines.append(line[1:])
                result.total_deletions += 1
            elif line.startswith(" "):
                current_hunk.context_lines.append(line[1:])

    result.total_changes = result.total_additions + result.total_deletions
    return result


# =============================================================================
# SIGNAL 1: DIFF SIZE
# =============================================================================

def measure_diff_size(diff: ParsedDiff) -> SignalScore:
    """
    Measure diff size using relative churn normalization.

    Research basis: Nagappan & Ball (2005) showed relative code churn
    (normalized against component size) predicts defect density with 89%
    accuracy, while absolute line counts are weak predictors.

    Scoring:
        <5 lines changed   → 0.0-0.1 (surgical)
        5-15 lines          → 0.1-0.3 (targeted)
        16-30 lines         → 0.3-0.5 (moderate)
        31-50 lines         → 0.5-0.7 (significant)
        51-100 lines        → 0.7-0.9 (large)
        >100 lines          → 0.9-1.0 (very large)
    """
    total = diff.total_changes
    score = SignalScore(name="diff_size", raw_value=float(total))

    if total <= 0:
        score.normalized = 0.0
        score.reasoning = "No changes detected"
    elif total < 5:
        score.normalized = total * 0.02
        score.reasoning = f"{total} lines changed — surgical fix"
    elif total < 15:
        score.normalized = 0.10 + (total - 5) * 0.02
        score.reasoning = f"{total} lines changed — targeted fix"
    elif total < 30:
        score.normalized = 0.30 + (total - 15) * 0.013
        score.reasoning = f"{total} lines changed — moderate scope"
    elif total < 50:
        score.normalized = 0.50 + (total - 30) * 0.01
        score.reasoning = f"{total} lines changed — significant scope"
    elif total < 100:
        score.normalized = 0.70 + (total - 50) * 0.004
        score.reasoning = f"{total} lines changed — large scope"
    else:
        score.normalized = min(1.0, 0.90 + (total - 100) * 0.001)
        score.reasoning = f"{total} lines changed — very large scope (high risk)"

    return score


# =============================================================================
# SIGNAL 2: FILES TOUCHED
# =============================================================================

def measure_files_touched(diff: ParsedDiff) -> SignalScore:
    """
    Measure the number of distinct files modified.

    Research basis: Hassan (2009) entropy research shows file scatter is
    a strong predictor of defect risk. Changes across many files indicate
    diffusion, which correlates with higher regression probability.

    Scoring:
        1 file    → 0.0-0.1
        2 files   → 0.15-0.25
        3 files   → 0.30-0.45
        4-5 files → 0.50-0.70
        6+ files  → 0.75-1.0
    """
    count = len(diff.files_changed)
    score = SignalScore(name="files_touched", raw_value=float(count))

    if count <= 0:
        score.normalized = 0.0
        score.reasoning = "No files touched"
    elif count == 1:
        score.normalized = 0.08
        score.reasoning = "Single file — isolated change"
    elif count == 2:
        score.normalized = 0.22
        score.reasoning = "2 files — limited scope"
    elif count == 3:
        score.normalized = 0.40
        score.reasoning = "3 files — moderate spread"
    elif count <= 5:
        score.normalized = 0.50 + (count - 4) * 0.10
        score.reasoning = f"{count} files — significant diffusion"
    else:
        score.normalized = min(1.0, 0.75 + (count - 6) * 0.05)
        score.reasoning = f"{count} files — high diffusion (elevated risk)"

    return score


# =============================================================================
# SIGNAL 3: AST DEPTH
# =============================================================================

# Regex patterns for detecting structural changes in JS/TS/JSX/TSX
STRUCTURAL_PATTERNS = {
    # Function/method signature changes
    "function_declaration": re.compile(
        r'^\s*(?:export\s+)?(?:async\s+)?function\s+\w+\s*\('
    ),
    "arrow_function_named": re.compile(
        r'^\s*(?:export\s+)?(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?\('
    ),
    "method_definition": re.compile(
        r'^\s*(?:async\s+)?(?:get|set\s+)?\w+\s*\([^)]*\)\s*(?::\s*\w+)?\s*\{'
    ),
    # Class/interface definitions
    "class_declaration": re.compile(
        r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+\w+'
    ),
    "interface_declaration": re.compile(
        r'^\s*(?:export\s+)?(?:interface|type)\s+\w+'
    ),
    # Import/export structure
    "export_statement": re.compile(
        r'^\s*export\s+(?:default\s+|{)'
    ),
    "import_statement": re.compile(
        r'^\s*import\s+(?:{[^}]+}|[\w*]+)\s+from'
    ),
    # Enum definitions
    "enum_declaration": re.compile(
        r'^\s*(?:export\s+)?(?:const\s+)?enum\s+\w+'
    ),
}

BRANCH_PATTERNS = {
    # Control flow changes
    "if_statement": re.compile(r'^\s*(?:else\s+)?if\s*\('),
    "switch_statement": re.compile(r'^\s*switch\s*\('),
    "for_loop": re.compile(r'^\s*for\s*\('),
    "while_loop": re.compile(r'^\s*while\s*\('),
    "try_catch": re.compile(r'^\s*(?:try|catch|finally)\s*[({]'),
    "ternary": re.compile(r'\?\s*[^:]+\s*:'),
    # Conditional return/throw
    "conditional_return": re.compile(r'^\s*(?:return|throw)\s+'),
    # React hooks with deps
    "hook_with_deps": re.compile(r'use(?:Effect|Callback|Memo)\s*\('),
}

LEAF_PATTERNS = {
    # Value-only changes
    "string_literal": re.compile(r'^\s*["\'].*["\']'),
    "number_literal": re.compile(r'^\s*\d+'),
    "boolean_literal": re.compile(r'^\s*(?:true|false)'),
    "null_literal": re.compile(r'^\s*(?:null|undefined)'),
    "assignment_value": re.compile(r'=\s*["\'\d]'),
    "css_value": re.compile(r':\s*[\d#"\']'),
}


def measure_ast_depth(diff: ParsedDiff) -> SignalScore:
    """
    Measure the structural nature of AST changes using regex heuristics.

    Research basis: GumTree algorithm (Falleri et al.) classifies AST changes
    into leaf, branch, and structural categories. We use regex heuristics as
    a practical proxy that works without full AST parsing.

    Classification:
        Leaf (0.0-0.2):       Value changes, literals, simple assignments
        Branch (0.3-0.6):     Control flow changes, conditions, loops
        Structural (0.7-1.0): Function signatures, class definitions,
                              interfaces, export changes
    """
    score = SignalScore(name="ast_depth")
    structural_count = 0
    branch_count = 0
    leaf_count = 0

    all_changed_lines = []
    for hunk in diff.hunks:
        all_changed_lines.extend(hunk.added_lines)
        all_changed_lines.extend(hunk.removed_lines)

    if not all_changed_lines:
        score.raw_value = 0.0
        score.normalized = 0.0
        score.reasoning = "No code changes to analyze"
        return score

    for line in all_changed_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            continue

        # Check structural patterns first (highest priority)
        matched_structural = False
        for pattern_name, pattern in STRUCTURAL_PATTERNS.items():
            if pattern.search(stripped):
                structural_count += 1
                matched_structural = True
                break

        if matched_structural:
            continue

        # Check branch patterns
        matched_branch = False
        for pattern_name, pattern in BRANCH_PATTERNS.items():
            if pattern.search(stripped):
                branch_count += 1
                matched_branch = True
                break

        if matched_branch:
            continue

        # Default: count as leaf
        leaf_count += 1

    total = structural_count + branch_count + leaf_count
    if total == 0:
        score.raw_value = 0.0
        score.normalized = 0.0
        score.reasoning = "Only comments or blank lines changed"
        return score

    # Weighted classification score
    # Structural changes dominate the score
    structural_ratio = structural_count / total
    branch_ratio = branch_count / total

    # The score is driven by the presence of structural changes
    # Even one structural change raises the floor significantly
    if structural_count > 0:
        # Structural changes present → 0.55 minimum, scales up
        base = 0.55
        structural_boost = min(0.45, structural_ratio * 1.2)
        raw = base + structural_boost
        category = "structural"
    elif branch_count > 0:
        # Branch changes only → 0.25-0.55
        base = 0.25
        branch_boost = min(0.30, branch_ratio * 0.6)
        raw = base + branch_boost
        category = "branch"
    else:
        # Leaf changes only → 0.0-0.20
        raw = min(0.20, leaf_count * 0.02)
        category = "leaf"

    score.raw_value = raw
    score.normalized = min(1.0, raw)
    score.reasoning = (
        f"{category} change — {structural_count} structural, "
        f"{branch_count} branch, {leaf_count} leaf modifications"
    )
    return score


# =============================================================================
# SIGNAL 4: TYPE SURFACE
# =============================================================================

# Patterns that indicate type system impact
TYPE_IMPACT_PATTERNS = {
    # NOTE: These patterns match STRIPPED diff lines (parser removes leading +/-)
    # so patterns must NOT start with ^\+ — use ^\s* instead
    "new_interface": re.compile(
        r'^\s*(?:export\s+)?interface\s+\w+'
    ),
    "new_type": re.compile(
        r'^\s*(?:export\s+)?type\s+\w+\s*='
    ),
    "changed_signature": re.compile(
        r'^\s*(?:export\s+)?(?:async\s+)?function\s+\w+\s*\([^)]*:\s*\w+'
    ),
    "generic_type": re.compile(
        r'<\w+(?:\s+extends\s+\w+)?>'
    ),
    "type_assertion": re.compile(
        r'as\s+\w+|<\w+>'
    ),
    "enum_change": re.compile(
        r'^\s*(?:export\s+)?(?:const\s+)?enum\s+'
    ),
    "discriminated_union": re.compile(
        r'type\s+\w+\s*=\s*\{[^}]*\}\s*\|'
    ),
    "return_type": re.compile(
        r'\)\s*:\s*(?:Promise<)?\w+'
    ),
}


def measure_type_surface(diff: ParsedDiff) -> SignalScore:
    """
    Measure the type system impact of the change.

    Detects: new interfaces, new types, changed function signatures with types,
    generic type parameters, type assertions, enum changes, discriminated unions.

    Scoring:
        No type changes       → 0.0
        Minor type changes    → 0.1-0.3
        New types/interfaces  → 0.4-0.6
        Changed public types  → 0.7-0.9
        Multiple public API   → 0.9-1.0
    """
    score = SignalScore(name="type_surface")
    type_changes = {name: 0 for name in TYPE_IMPACT_PATTERNS}

    # Check added lines in the raw diff for type patterns
    for hunk in diff.hunks:
        # Check TypeScript/type-bearing files
        ext = os.path.splitext(hunk.file_path)[1].lower()
        if ext not in (".ts", ".tsx", ".d.ts", ".mts", ".cts"):
            continue

        for line in hunk.added_lines:
            for pattern_name, pattern in TYPE_IMPACT_PATTERNS.items():
                if pattern.search(line):
                    type_changes[pattern_name] += 1

    total_type_hits = sum(type_changes.values())
    score.raw_value = float(total_type_hits)

    # Count high-impact type changes
    public_type_changes = (
        type_changes["new_interface"]
        + type_changes["new_type"]
        + type_changes["enum_change"]
        + type_changes["discriminated_union"]
    )
    signature_changes = type_changes["changed_signature"] + type_changes["return_type"]

    if total_type_hits == 0:
        score.normalized = 0.0
        score.reasoning = "No type system changes detected"
    elif public_type_changes >= 3:
        score.normalized = min(1.0, 0.85 + public_type_changes * 0.03)
        score.reasoning = f"{public_type_changes} public type definitions changed — high type surface"
    elif public_type_changes >= 1:
        score.normalized = 0.45 + public_type_changes * 0.12
        score.reasoning = f"{public_type_changes} new types/interfaces — moderate type surface"
    elif signature_changes >= 1:
        score.normalized = 0.30 + signature_changes * 0.08
        score.reasoning = f"{signature_changes} signature changes — moderate type impact"
    else:
        score.normalized = min(0.30, total_type_hits * 0.06)
        score.reasoning = f"{total_type_hits} minor type annotations — low type surface"

    score.normalized = min(1.0, score.normalized)
    return score


# =============================================================================
# SIGNAL 5: TEST SURFACE
# =============================================================================

# Common test file patterns
TEST_FILE_PATTERNS = [
    re.compile(r'\.test\.[jt]sx?$'),
    re.compile(r'\.spec\.[jt]sx?$'),
    re.compile(r'__tests__/'),
    re.compile(r'\.stories\.[jt]sx?$'),
    re.compile(r'\.e2e\.[jt]sx?$'),
]

# Patterns that indicate test coverage for changed code
TEST_IMPORT_PATTERNS = re.compile(
    r'(?:import|require)\s*\(?\s*[\'"](?:\.\./)*([^\'"\s]+)[\'"]'
)


def measure_test_surface(diff: ParsedDiff, project_path: str = "") -> SignalScore:
    """
    Measure the breadth of test coverage impacted by the change.

    Estimates how many tests touch the changed code by:
    1. Checking if changed files have corresponding test files
    2. Counting test files that import changed modules
    3. Estimating test breadth from file count and project structure

    Scoring:
        <3 tests likely affected   → 0.0-0.2
        3-5 tests                  → 0.2-0.4
        6-10 tests                 → 0.4-0.7
        >10 tests or cross-module  → 0.7-1.0
    """
    score = SignalScore(name="test_surface")

    # Identify non-test changed files
    changed_source_files = []
    changed_test_files = []
    for f in diff.files_changed:
        is_test = any(p.search(f) for p in TEST_FILE_PATTERNS)
        if is_test:
            changed_test_files.append(f)
        else:
            changed_source_files.append(f)

    if not changed_source_files:
        score.raw_value = 0.0
        score.normalized = 0.0
        score.reasoning = "Only test files changed — test surface not applicable"
        return score

    # Estimate test coverage breadth
    estimated_test_count = 0

    # Method 1: Check for corresponding test files by naming convention
    for source_file in changed_source_files:
        base = os.path.splitext(source_file)[0]
        # Common patterns: foo.ts → foo.test.ts, foo.spec.ts
        for suffix in [".test", ".spec"]:
            for ext in [".ts", ".tsx", ".js", ".jsx"]:
                test_path = base + suffix + ext
                if project_path:
                    full_path = os.path.join(project_path, test_path)
                    if os.path.exists(full_path):
                        estimated_test_count += 1

    # Method 2: If project path available, search for imports of changed modules
    if project_path and os.path.isdir(project_path):
        changed_module_names = set()
        for f in changed_source_files:
            name = os.path.splitext(os.path.basename(f))[0]
            if name != "index":
                changed_module_names.add(name)

        # Quick scan of test files for imports
        test_dirs = ["__tests__", "tests", "test", "spec"]
        for test_dir in test_dirs:
            test_path = os.path.join(project_path, test_dir)
            if os.path.isdir(test_path):
                for root, dirs, files in os.walk(test_path):
                    for fname in files:
                        if any(p.search(fname) for p in TEST_FILE_PATTERNS):
                            fpath = os.path.join(root, fname)
                            try:
                                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                                    content = fh.read(4096)  # First 4KB
                                    for module_name in changed_module_names:
                                        if module_name in content:
                                            estimated_test_count += 1
                                            break
                            except (IOError, PermissionError):
                                continue

    # Method 3: Heuristic based on file count and directory structure
    if estimated_test_count == 0 and not project_path:
        # No project path, estimate from diff characteristics
        unique_dirs = set(os.path.dirname(f) for f in changed_source_files)
        estimated_test_count = len(changed_source_files) + len(unique_dirs)

    score.raw_value = float(estimated_test_count)

    # Determine if cross-module
    unique_dirs = set(os.path.dirname(f) for f in changed_source_files)
    is_cross_module = len(unique_dirs) > 1

    if estimated_test_count == 0:
        score.normalized = 0.05
        score.reasoning = "No test files detected for changed modules"
    elif estimated_test_count < 3:
        score.normalized = 0.10 + estimated_test_count * 0.05
        score.reasoning = f"~{estimated_test_count} tests affected — narrow coverage"
    elif estimated_test_count < 6:
        score.normalized = 0.25 + (estimated_test_count - 3) * 0.05
        score.reasoning = f"~{estimated_test_count} tests affected — moderate coverage"
    elif estimated_test_count < 10:
        score.normalized = 0.45 + (estimated_test_count - 6) * 0.06
        score.reasoning = f"~{estimated_test_count} tests affected — broad coverage"
    else:
        score.normalized = min(1.0, 0.75 + (estimated_test_count - 10) * 0.025)
        score.reasoning = f"~{estimated_test_count} tests affected — very broad coverage"

    if is_cross_module:
        score.normalized = min(1.0, score.normalized + 0.15)
        score.reasoning += " (cross-module)"

    return score


# =============================================================================
# SIGNAL 6: DEPENDENCY FAN-OUT
# =============================================================================

# Patterns to detect exported symbols
EXPORT_PATTERNS = [
    re.compile(r'export\s+(?:default\s+)?(?:function|class|const|let|var|enum|interface|type)\s+(\w+)'),
    re.compile(r'export\s+\{\s*([^}]+)\s*\}'),
    re.compile(r'module\.exports\s*=\s*(?:\{([^}]+)\}|(\w+))'),
]

# Patterns to detect function/class declarations (may be referenced)
DECLARATION_PATTERNS = [
    re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)'),
    re.compile(r'(?:export\s+)?class\s+(\w+)'),
    re.compile(r'(?:export\s+)?const\s+(\w+)\s*='),
]


def measure_dependency_fan(diff: ParsedDiff, project_path: str = "") -> SignalScore:
    """
    Measure downstream dependency impact using grep-based heuristics.

    Research basis: API breaking-change research (IEEE SANER 2017) shows 28%
    of API changes break backward compatibility. Fan-out is a critical signal.

    Method:
    1. Extract changed export/function names from the diff
    2. Search project files for references to those names
    3. Count unique files that reference changed symbols
    4. Score based on reference count and spread

    Scoring:
        0 callers affected         → 0.0-0.05
        1-2 callers                → 0.10-0.25
        3-4 callers                → 0.30-0.50
        5+ callers                 → 0.55-0.80
        Public API change detected → 0.80-1.0
    """
    score = SignalScore(name="dependency_fan")

    # Extract changed symbol names from the diff
    changed_symbols = set()
    is_public_api_change = False

    for hunk in diff.hunks:
        for line in hunk.added_lines + hunk.removed_lines:
            for pattern in EXPORT_PATTERNS:
                matches = pattern.findall(line)
                for match in matches:
                    if isinstance(match, tuple):
                        for m in match:
                            if m:
                                for sym in re.split(r'[,\s]+', m.strip()):
                                    sym = sym.strip().rstrip(',')
                                    if sym and len(sym) > 1 and sym.isidentifier():
                                        changed_symbols.add(sym)
                                        is_public_api_change = True
                    elif match:
                        for sym in re.split(r'[,\s]+', match.strip()):
                            sym = sym.strip().rstrip(',')
                            if sym and len(sym) > 1 and sym.isidentifier():
                                changed_symbols.add(sym)
                                is_public_api_change = True

            for pattern in DECLARATION_PATTERNS:
                matches = pattern.findall(line)
                for match in matches:
                    if match and len(match) > 1 and match.isidentifier():
                        changed_symbols.add(match)

    if not changed_symbols:
        score.raw_value = 0.0
        score.normalized = 0.05
        score.reasoning = "No exported symbols changed"
        return score

    # If project path available, search for references
    reference_count = 0
    referencing_files = set()

    if project_path and os.path.isdir(project_path):
        # Use grep to find references (fast, good enough for signal scoring)
        skip_dirs = {
            "node_modules", ".git", "dist", "build", ".next", ".nuxt",
            "coverage", ".cache", ".turbo", "out",
        }

        for symbol in list(changed_symbols)[:10]:  # Limit to top 10 symbols
            try:
                result = subprocess.run(
                    ["grep", "-rl", "--include=*.ts", "--include=*.tsx",
                     "--include=*.js", "--include=*.jsx",
                     f"\\b{symbol}\\b", project_path],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().splitlines():
                        # Exclude the changed files themselves
                        rel_path = os.path.relpath(line, project_path)
                        if rel_path not in diff.files_changed:
                            skip = any(d in rel_path for d in skip_dirs)
                            if not skip:
                                referencing_files.add(rel_path)
            except subprocess.TimeoutExpired:
                # BUG FIX: Log timeout instead of silently returning 0
                import logging
                logging.warning(
                    f"dependency_fan: grep timed out after 5s on {project_path}. "
                    f"Returning 0 references — score may underestimate impact. "
                    f"Consider increasing timeout for large codebases."
                )
                continue
            except FileNotFoundError:
                continue

        reference_count = len(referencing_files)
    else:
        # No project path: estimate from diff characteristics
        # If exports changed, assume moderate fan-out
        reference_count = len(changed_symbols) * 2 if is_public_api_change else 0

    score.raw_value = float(reference_count)

    if is_public_api_change and reference_count >= 5:
        score.normalized = min(1.0, 0.80 + reference_count * 0.02)
        score.reasoning = (
            f"Public API change — {reference_count} files reference "
            f"changed symbols ({', '.join(list(changed_symbols)[:5])})"
        )
    elif reference_count >= 5:
        score.normalized = 0.55 + (reference_count - 5) * 0.04
        score.reasoning = f"{reference_count} files reference changed symbols"
    elif reference_count >= 3:
        score.normalized = 0.30 + (reference_count - 3) * 0.10
        score.reasoning = f"{reference_count} callers affected — moderate fan-out"
    elif reference_count >= 1:
        score.normalized = 0.10 + reference_count * 0.08
        score.reasoning = f"{reference_count} callers affected — limited fan-out"
    elif is_public_api_change:
        score.normalized = 0.40
        score.reasoning = f"Public API symbols changed ({', '.join(list(changed_symbols)[:3])}) — unable to scan project"
    else:
        score.normalized = 0.05
        score.reasoning = "No downstream callers detected"

    score.normalized = min(1.0, score.normalized)
    return score


# =============================================================================
# COMPOSITE SCORING
# =============================================================================

def compute_weights(project_type: str, custom_weights: dict = None) -> dict:
    """
    Compute final signal weights based on project type and custom overrides.

    Uses DEFAULT_WEIGHTS as baseline, applies PROJECT_TYPE_ADJUSTMENTS,
    then normalizes so weights sum to 1.0.
    """
    weights = dict(DEFAULT_WEIGHTS)

    # Apply project-type adjustments
    if project_type in PROJECT_TYPE_ADJUSTMENTS:
        for signal, delta in PROJECT_TYPE_ADJUSTMENTS[project_type].items():
            if signal in weights:
                weights[signal] = max(0.01, weights[signal] + delta)

    # Apply custom overrides
    if custom_weights:
        for signal, value in custom_weights.items():
            if signal in weights:
                weights[signal] = max(0.01, value)

    # Normalize to sum to 1.0
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}

    return weights


def check_veto_triggers(signals: Dict[str, SignalScore]) -> VetoCheck:
    """
    Check if any single signal triggers a veto (forces minimum composite).

    Veto prevents the failure mode where a 1-line public API change scores
    low because diff_size is small. If any signal exceeds its veto threshold,
    the composite is forced to at least VETO_MINIMUM_SCORE.
    """
    veto = VetoCheck()
    triggers = []

    for signal_name, threshold in VETO_THRESHOLDS.items():
        if signal_name in signals:
            if signals[signal_name].normalized >= threshold:
                triggers.append(
                    f"{signal_name}={signals[signal_name].normalized:.2f} "
                    f"(threshold: {threshold})"
                )

    if triggers:
        veto.triggered = True
        veto.reason = f"Veto triggered by: {'; '.join(triggers)}"
        veto.minimum_score = VETO_MINIMUM_SCORE

    return veto


def apply_severity_ratchet(
    severity: str, verification_depth: float
) -> Tuple[float, Dict]:
    """
    Apply severity ratchet — forces minimum verification depth for
    critical and high severity bugs regardless of signal score.

    critical → full L1-L8 (force depth ≥ 0.80)
    high     → minimum L1-L6 (force depth ≥ 0.50)
    """
    ratchet = {
        "applied": False,
        "original_depth": verification_depth,
        "severity": severity,
    }

    if severity == "critical":
        if verification_depth < 0.80:
            ratchet["applied"] = True
            ratchet["reason"] = "Critical severity forces full L1-L8 verification"
            verification_depth = max(verification_depth, 0.80)
    elif severity == "high":
        if verification_depth < 0.50:
            ratchet["applied"] = True
            ratchet["reason"] = "High severity forces minimum L1-L6 verification"
            verification_depth = max(verification_depth, 0.50)

    return verification_depth, ratchet


def compute_composite_score(
    signals: Dict[str, SignalScore],
    weights: dict,
    veto: VetoCheck,
) -> float:
    """
    Compute weighted composite verification_depth score.

    Two-stage approach:
    1. Weighted sum of all signal scores
    2. Apply veto minimum if triggered

    Research basis: Weighted sum with veto layer, based on MCDM literature
    (MDPI 2023). Veto layer prevents high-risk signals from being averaged
    away by low-risk signals.
    """
    weighted_sum = 0.0
    for signal_name, weight in weights.items():
        if signal_name in signals:
            weighted_sum += weight * signals[signal_name].normalized

    # Apply veto minimum
    if veto.triggered:
        weighted_sum = max(weighted_sum, veto.minimum_score)

    return min(1.0, weighted_sum)


def determine_depth_levels(
    verification_depth: float, severity: str
) -> DepthDecision:
    """
    Determine which verification levels (L5-L8) are required based on
    the composite verification_depth score and severity.

    Mandatory: L1-L4 always run (Mandatory Floor safety net)
    L5-L8: Depth-proportional based on composite score
    """
    decision = DepthDecision()
    decision.levels_required = [1, 2, 3, 4]  # Always mandatory

    # Determine recommended levels beyond L4
    if verification_depth >= DEPTH_THRESHOLDS["full"]:
        decision.levels_recommended = [5, 6, 7, 8]
    elif verification_depth >= DEPTH_THRESHOLDS["L5_L6_L7"]:
        decision.levels_recommended = [5, 6, 7]
    elif verification_depth >= DEPTH_THRESHOLDS["L5_L6"]:
        decision.levels_recommended = [5, 6]
    elif verification_depth >= DEPTH_THRESHOLDS["L5_only"]:
        decision.levels_recommended = [5]
    else:
        decision.levels_recommended = []

    # Severity overrides
    if severity == "critical":
        decision.levels_recommended = [5, 6, 7, 8]
        decision.severity_override = True
    elif severity == "high":
        if 6 not in decision.levels_recommended:
            decision.levels_recommended = sorted(
                set(decision.levels_recommended) | {5, 6}
            )
            decision.severity_override = True

    # Escalation hints
    if verification_depth < 0.25 and severity in ("medium", "low"):
        decision.escalation_hints.append(
            "Low depth score — monitor L1-L4 for unexpected signals. "
            "Auto-escalation will promote to full if cascading errors detected."
        )

    return decision


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def analyze_fix(
    diff_text: str,
    project_path: str = "",
    project_type: str = "unknown",
    severity: str = "medium",
    custom_weights: dict = None,
) -> FixSignalReport:
    """
    Full fix signal analysis pipeline.

    Steps:
    1. Parse the diff
    2. Measure all 6 signals
    3. Compute weights (project-type adjusted)
    4. Check veto triggers
    5. Compute composite score
    6. Apply severity ratchet
    7. Determine verification levels
    """
    report = FixSignalReport(
        project_path=project_path,
        project_type=project_type,
        severity=severity,
    )

    # 1. Parse diff
    diff = parse_unified_diff(diff_text)
    if not diff.files_changed and not diff.hunks:
        report.warnings.append("Empty or unparseable diff provided")
        return report

    # 2. Measure signals
    signals = {}
    signals["diff_size"] = measure_diff_size(diff)
    signals["files_touched"] = measure_files_touched(diff)
    signals["ast_depth"] = measure_ast_depth(diff)
    signals["type_surface"] = measure_type_surface(diff)
    signals["test_surface"] = measure_test_surface(diff, project_path)
    signals["dependency_fan"] = measure_dependency_fan(diff, project_path)

    report.signals = {
        name: asdict(signal) for name, signal in signals.items()
    }

    # 3. Compute weights
    weights = compute_weights(project_type, custom_weights)
    report.weights_used = weights

    # 4. Check veto triggers
    veto = check_veto_triggers(signals)
    report.veto = asdict(veto)

    # 5. Compute composite score
    composite = compute_composite_score(signals, weights, veto)

    # 6. Apply severity ratchet
    composite, ratchet = apply_severity_ratchet(severity, composite)
    report.severity_ratchet = ratchet

    report.verification_depth = round(composite, 4)

    # Categorize depth
    if composite >= 0.75:
        report.depth_category = "full"
    elif composite >= 0.50:
        report.depth_category = "high"
    elif composite >= 0.25:
        report.depth_category = "moderate"
    elif composite >= 0.10:
        report.depth_category = "low"
    else:
        report.depth_category = "minimal"

    # 7. Determine verification levels
    decision = determine_depth_levels(composite, severity)
    report.depth_decision = asdict(decision)

    return report


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_output(report: FixSignalReport, fmt: str = "text") -> str:
    """Format the analysis report."""
    if fmt == "json":
        return json.dumps(asdict(report), indent=2, default=str)

    if fmt == "yaml":
        lines = ["# Fix Signal Analysis — Adaptive Verification Pipeline"]
        lines.append(f"project_type: {report.project_type}")
        lines.append(f"severity: {report.severity}")
        lines.append(f"verification_depth: {report.verification_depth}")
        lines.append(f"depth_category: {report.depth_category}")
        lines.append("")
        lines.append("signals:")
        for name, signal in report.signals.items():
            lines.append(f"  {name}:")
            lines.append(f"    normalized: {signal['normalized']}")
            lines.append(f"    raw_value: {signal['raw_value']}")
            lines.append(f"    reasoning: \"{signal['reasoning']}\"")
        lines.append("")
        lines.append("depth_decision:")
        dd = report.depth_decision
        lines.append(f"  levels_required: {dd.get('levels_required', [1,2,3,4])}")
        lines.append(f"  levels_recommended: {dd.get('levels_recommended', [])}")
        lines.append(f"  severity_override: {dd.get('severity_override', False)}")
        lines.append("")
        lines.append("veto:")
        lines.append(f"  triggered: {report.veto.get('triggered', False)}")
        if report.veto.get('triggered'):
            lines.append(f"  reason: \"{report.veto.get('reason', '')}\"")
        lines.append("")
        lines.append("severity_ratchet:")
        lines.append(f"  applied: {report.severity_ratchet.get('applied', False)}")
        if report.severity_ratchet.get('applied'):
            lines.append(f"  reason: \"{report.severity_ratchet.get('reason', '')}\"")
        lines.append("")
        lines.append(f"weights_used: {report.weights_used}")
        if report.warnings:
            lines.append("")
            lines.append("warnings:")
            for w in report.warnings:
                lines.append(f"  - \"{w}\"")
        return "\n".join(lines)

    # Text format (default)
    lines = [
        "=" * 66,
        "  ADAPTIVE VERIFICATION PIPELINE — FIX SIGNAL ANALYSIS",
        "=" * 66,
        "",
        f"  Project Type:  {report.project_type}",
        f"  Severity:      {report.severity}",
        "",
    ]

    # Composite score — large and visible
    depth = report.verification_depth
    bar_len = int(depth * 30)
    bar = "█" * bar_len + "░" * (30 - bar_len)
    lines.append(f"  VERIFICATION DEPTH: {depth:.2f}  [{bar}]")
    lines.append(f"  Category: {report.depth_category.upper()}")
    lines.append("")

    # Signals table
    lines.append("  SIGNAL SCORES:")
    lines.append("  " + "-" * 62)
    lines.append(
        f"  {'Signal':<18} {'Score':>6} {'Weight':>7}  {'Reasoning'}"
    )
    lines.append("  " + "-" * 62)

    for name in ["diff_size", "files_touched", "ast_depth",
                 "type_surface", "test_surface", "dependency_fan"]:
        if name in report.signals:
            sig = report.signals[name]
            weight = report.weights_used.get(name, 0)
            mini_bar = "▓" * int(sig["normalized"] * 10) + "░" * (10 - int(sig["normalized"] * 10))
            lines.append(
                f"  {name:<18} {sig['normalized']:>5.2f} "
                f"({weight:>4.0%})  {mini_bar}  {sig['reasoning']}"
            )
    lines.append("  " + "-" * 62)
    lines.append("")

    # Depth decision
    dd = report.depth_decision
    mandatory = dd.get("levels_required", [1, 2, 3, 4])
    recommended = dd.get("levels_recommended", [])
    all_levels = sorted(set(mandatory + recommended))

    level_names = {
        1: "Syntax", 2: "Types", 3: "Lint", 4: "Tests",
        5: "Regression", 6: "Performance", 7: "Visual", 8: "Security",
    }

    lines.append("  VERIFICATION LEVELS:")
    for lvl in range(1, 9):
        name = level_names[lvl]
        if lvl in mandatory:
            status = "██ MANDATORY"
        elif lvl in recommended:
            status = "▓▓ RECOMMENDED"
        else:
            status = "░░ skipped"
        lines.append(f"    L{lvl}: {name:<12}  {status}")
    lines.append("")

    # Veto check
    if report.veto.get("triggered"):
        lines.append(f"  ⚠ VETO: {report.veto['reason']}")
        lines.append(
            f"    Minimum composite forced to {report.veto['minimum_score']:.2f}"
        )
        lines.append("")

    # Severity ratchet
    if report.severity_ratchet.get("applied"):
        lines.append(f"  ⚠ SEVERITY RATCHET: {report.severity_ratchet['reason']}")
        lines.append(
            f"    Original depth: {report.severity_ratchet['original_depth']:.2f}"
            f" → Ratcheted: {report.verification_depth:.2f}"
        )
        lines.append("")

    # Escalation hints
    hints = dd.get("escalation_hints", [])
    if hints:
        lines.append("  ESCALATION NOTES:")
        for hint in hints:
            lines.append(f"    → {hint}")
        lines.append("")

    # Warnings
    if report.warnings:
        lines.append("  WARNINGS:")
        for w in report.warnings:
            lines.append(f"    ⚠ {w}")
        lines.append("")

    lines.append("=" * 66)
    return "\n".join(lines)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix Signal Analyzer — Adaptive Verification Pipeline (AVP)",
        epilog=(
            "Analyzes a code fix diff to determine verification depth. "
            "Part of the Ultimate Debugger skill."
        ),
    )
    parser.add_argument(
        "--diff", type=str, help="Path to unified diff file"
    )
    parser.add_argument(
        "--files", nargs="+", help="Changed file paths (reads current content)"
    )
    parser.add_argument(
        "--stdin", action="store_true", help="Read diff from stdin"
    )
    parser.add_argument(
        "--project-path", type=str, default="",
        help="Project root for dependency analysis"
    )
    parser.add_argument(
        "--project-type", type=str, default="unknown",
        choices=["3d-experience", "animation-site", "react-spa",
                 "dashboard", "hybrid", "unknown"],
        help="Project type for weight adjustment"
    )
    parser.add_argument(
        "--severity", type=str, default="medium",
        choices=["critical", "high", "medium", "low"],
        help="Bug severity level"
    )
    parser.add_argument(
        "--format", type=str, default="text",
        choices=["text", "json", "yaml"],
        help="Output format"
    )
    parser.add_argument(
        "--weights", type=str,
        help="Path to custom weights YAML file"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed analysis"
    )

    args = parser.parse_args()

    # Read diff input
    diff_text = ""

    if args.stdin:
        diff_text = sys.stdin.read()
    elif args.diff:
        if not os.path.exists(args.diff):
            print(f"Error: Diff file not found: {args.diff}", file=sys.stderr)
            sys.exit(1)
        with open(args.diff, "r", encoding="utf-8") as f:
            diff_text = f.read()
    elif args.files:
        # Generate a pseudo-diff from file paths
        # (useful when you have the files but not a diff)
        lines = []
        for fpath in args.files:
            lines.append(f"diff --git a/{fpath} b/{fpath}")
            lines.append(f"--- a/{fpath}")
            lines.append(f"+++ b/{fpath}")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.readlines()
                lines.append(f"@@ -1,{len(content)} +1,{len(content)} @@")
                for line in content:
                    lines.append(f"+{line.rstrip()}")
        diff_text = "\n".join(lines)
    else:
        # Try reading from stdin if nothing else provided
        if not sys.stdin.isatty():
            diff_text = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)

    # Load custom weights
    custom_weights = None
    if args.weights:
        try:
            import yaml
            with open(args.weights, "r") as f:
                custom_weights = yaml.safe_load(f)
        except ImportError:
            # Fallback: try JSON format
            with open(args.weights, "r") as f:
                custom_weights = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load weights file: {e}", file=sys.stderr)

    # Run analysis
    report = analyze_fix(
        diff_text=diff_text,
        project_path=args.project_path,
        project_type=args.project_type,
        severity=args.severity,
        custom_weights=custom_weights,
    )

    # Output
    print(format_output(report, args.format))


if __name__ == "__main__":
    main()
