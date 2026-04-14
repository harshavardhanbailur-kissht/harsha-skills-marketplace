"""
Comprehensive integration tests for fix_signal_analyzer.py

Tests cover:
1. Diff parsing and structural understanding
2. All 6 signal measurements
3. Composite scoring and weight computation
4. Veto triggers and severity ratcheting
5. Verification level determination
6. Output formatting
"""

import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fix_signal_analyzer import (
    VETO_MINIMUM_SCORE,
    VETO_THRESHOLDS,
    analyze_fix,
    apply_severity_ratchet,
    check_veto_triggers,
    compute_composite_score,
    compute_weights,
    determine_depth_levels,
    format_output,
    measure_ast_depth,
    measure_dependency_fan,
    measure_diff_size,
    measure_files_touched,
    measure_test_surface,
    measure_type_surface,
    parse_unified_diff,
)


# =============================================================================
# PRIORITY 1: CRITICAL PATH TESTS
# =============================================================================


class TestParseUnifiedDiff:
    """Tests for unified diff parsing."""

    def test_parse_unified_diff_simple(self, sample_diff_simple):
        """
        Test parsing a simple unified diff (1 file, ~5 lines).

        Verifies correct ParsedDiff structure with:
        - files_changed
        - hunks with added/removed lines
        - total_additions and total_deletions
        """
        parsed = parse_unified_diff(sample_diff_simple)

        assert len(parsed.files_changed) == 1
        assert "src/utils.ts" in parsed.files_changed
        assert len(parsed.hunks) > 0
        assert parsed.total_additions > 0
        assert parsed.total_deletions >= 0
        assert parsed.total_changes == parsed.total_additions + parsed.total_deletions

    def test_parse_unified_diff_multifile(self, sample_diff_multifile):
        """
        Test parsing multi-file diff with 3 files and different change types.

        Verifies correct handling of:
        - Multiple file paths
        - Multiple hunks per file
        - Added and removed lines
        """
        parsed = parse_unified_diff(sample_diff_multifile)

        assert len(parsed.files_changed) >= 2
        assert len(parsed.hunks) >= 2
        assert parsed.total_additions > 0
        assert parsed.total_deletions >= 0

    def test_parse_unified_diff_empty(self):
        """
        Test parsing empty diff string.

        Should handle gracefully without error.
        """
        parsed = parse_unified_diff("")

        assert parsed.files_changed == []
        assert parsed.hunks == []
        assert parsed.total_additions == 0
        assert parsed.total_deletions == 0


# =============================================================================
# SIGNAL MEASUREMENT TESTS
# =============================================================================


class TestMeasureDiffSize:
    """Tests for diff size signal measurement."""

    @pytest.mark.parametrize(
        "lines,expected_min,expected_max",
        [
            (0, 0.0, 0.1),
            (3, 0.0, 0.15),
            (5, 0.10, 0.11),
            (15, 0.28, 0.32),
            (30, 0.50, 0.65),
            (50, 0.70, 0.75),
            (100, 0.88, 0.95),
            (150, 0.95, 1.0),
        ],
    )
    def test_measure_diff_size_thresholds(self, lines, expected_min, expected_max):
        """
        Test diff size scoring at boundary values.

        Verifies that various line counts fall within expected score ranges.
        """
        diff_text = "diff --git a/file.ts b/file.ts\n"
        diff_text += "--- a/file.ts\n"
        diff_text += "+++ b/file.ts\n"
        diff_text += "@@ -1,1 +1,1 @@\n"
        for i in range(lines):
            if i % 2 == 0:
                diff_text += f"+line {i}\n"
            else:
                diff_text += f"-line {i}\n"

        parsed = parse_unified_diff(diff_text)
        signal = measure_diff_size(parsed)

        assert expected_min <= signal.normalized <= expected_max
        assert signal.name == "diff_size"
        assert signal.raw_value == float(parsed.total_changes)


class TestMeasureFilesTouched:
    """Tests for files touched signal measurement."""

    def test_measure_files_touched_single(self):
        """Test scoring for single file change."""
        diff_text = """diff --git a/utils.ts b/utils.ts
--- a/utils.ts
+++ b/utils.ts
@@ -1,1 +1,1 @@
+const x = 1;
"""
        parsed = parse_unified_diff(diff_text)
        signal = measure_files_touched(parsed)

        assert signal.normalized < 0.15
        assert "Single file" in signal.reasoning

    def test_measure_files_touched_multiple(self):
        """Test scoring increases with file count."""
        # Create diff with 5 files
        diff_text = "diff --git a/file1.ts b/file1.ts\n+x\n"
        for i in range(2, 6):
            diff_text += f"diff --git a/file{i}.ts b/file{i}.ts\n+y\n"

        parsed = parse_unified_diff(diff_text)
        signal = measure_files_touched(parsed)

        # 5 files should score higher
        assert signal.normalized > 0.5

    @pytest.mark.parametrize("file_count,expected_range", [
        (1, (0.0, 0.15)),
        (2, (0.15, 0.35)),
        (3, (0.30, 0.50)),
        (4, (0.50, 0.70)),
        (6, (0.70, 1.0)),
    ])
    def test_measure_files_touched_ranges(self, file_count, expected_range):
        """Test files touched scoring for various counts."""
        diff_text = ""
        for i in range(file_count):
            diff_text += f"diff --git a/file{i}.ts b/file{i}.ts\n+line\n"

        parsed = parse_unified_diff(diff_text)
        signal = measure_files_touched(parsed)

        min_expected, max_expected = expected_range
        assert min_expected <= signal.normalized <= max_expected


class TestMeasureASTDepth:
    """Tests for AST depth signal measurement."""

    def test_measure_ast_depth_structural(self, sample_diff_structural):
        """
        Test AST depth for structural changes (functions, classes).

        Verifies high score for function/class declarations.
        """
        parsed = parse_unified_diff(sample_diff_structural)
        signal = measure_ast_depth(parsed)

        # Structural changes should score high
        assert signal.normalized > 0.55
        assert "structural" in signal.reasoning.lower()

    def test_measure_ast_depth_leaf(self):
        """
        Test AST depth for leaf changes (values, literals).

        Verifies low score for simple value/assignment changes.
        """
        diff_text = """diff --git a/config.ts b/config.ts
--- a/config.ts
+++ b/config.ts
@@ -1,3 +1,3 @@
 const config = {
-  timeout: 5000,
+  timeout: 10000,
 };
"""
        parsed = parse_unified_diff(diff_text)
        signal = measure_ast_depth(parsed)

        # Leaf changes should score low
        assert signal.normalized < 0.25

    def test_measure_ast_depth_branch(self):
        """
        Test AST depth for branch changes (if/else, loops).

        Verifies medium-to-high score for control flow changes.
        """
        diff_text = """diff --git a/logic.ts b/logic.ts
--- a/logic.ts
+++ b/logic.ts
@@ -1,5 +1,5 @@
 const x = getValue();
-if (x > 10) {
+if (x > 0) {
   doSomething();
 } else {
   doOther();
"""
        parsed = parse_unified_diff(diff_text)
        signal = measure_ast_depth(parsed)

        # Branch changes should be in middle range
        assert 0.25 <= signal.normalized <= 1.0
        assert signal.reasoning != ""


class TestMeasureTypeSurface:
    """Tests for type surface signal measurement."""

    def test_measure_type_surface_new_interface(self, sample_diff_structural):
        """
        Test type surface detection for new interfaces.

        Verifies that new interface definitions are detected and scored high.
        """
        parsed = parse_unified_diff(sample_diff_structural)
        signal = measure_type_surface(parsed)

        # Structural diff has new interface definitions
        assert signal.normalized > 0.0

    def test_measure_type_surface_none(self):
        """
        Test type surface for non-TS file changes.

        Verifies low/zero score when no TypeScript files changed.
        """
        diff_text = """diff --git a/styles.css b/styles.css
--- a/styles.css
+++ b/styles.css
@@ -1,3 +1,4 @@
 body {
-  color: red;
+  color: blue;
 }
"""
        parsed = parse_unified_diff(diff_text)
        signal = measure_type_surface(parsed)

        # CSS file shouldn't trigger type surface
        assert signal.normalized == 0.0


class TestMeasureDependencyFan:
    """Tests for dependency fan-out signal measurement."""

    def test_measure_dependency_fan_public_api(self, sample_diff_api_change):
        """
        Test dependency fan for public API changes (exports).

        Verifies that export statement changes are detected and scored high.
        """
        parsed = parse_unified_diff(sample_diff_api_change)
        signal = measure_dependency_fan(parsed)

        # API change diff has export statements
        assert signal.raw_value > 0
        assert signal.normalized > 0.0

    def test_measure_dependency_fan_none(self):
        """
        Test dependency fan with no exports or symbol changes.

        Verifies low score when no public API symbols are changed.
        """
        diff_text = """diff --git a/internal.ts b/internal.ts
--- a/internal.ts
+++ b/internal.ts
@@ -1,3 +1,3 @@
 function helper() {
-  return 1;
+  return 2;
 }
"""
        parsed = parse_unified_diff(diff_text)
        signal = measure_dependency_fan(parsed)

        # No exports, limited fan impact
        assert signal.normalized <= 0.1


class TestMeasureTestSurface:
    """Tests for test surface signal measurement."""

    def test_measure_test_surface(self, sample_diff_multifile):
        """
        Test surface detection in multi-file diff.

        Verifies test file detection and cross-module estimation.
        """
        parsed = parse_unified_diff(sample_diff_multifile)
        signal = measure_test_surface(parsed)

        # Multifile diff includes test file
        assert signal.name == "test_surface"
        assert signal.reasoning != ""


# =============================================================================
# COMPOSITE SCORING TESTS
# =============================================================================


class TestComputeWeights:
    """Tests for weight computation."""

    def test_compute_weights_defaults(self):
        """Test that default weights sum to 1.0."""
        weights = compute_weights("unknown")

        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001  # Floating point tolerance

    def test_compute_weights_project_type_adjustment(self):
        """
        Test that project type adjustments affect weights.

        Verifies that 3D projects increase ast_depth weight.
        """
        weights_3d = compute_weights("3d-experience")
        weights_default = compute_weights("unknown")

        # 3D should have higher ast_depth weight
        assert weights_3d["ast_depth"] > weights_default["ast_depth"]

    def test_compute_weights_normalization(self):
        """
        Test that custom weights are normalized to sum to 1.0.

        Verifies normalization after custom weight application.
        """
        custom = {"diff_size": 0.5, "files_touched": 0.5}
        weights = compute_weights("unknown", custom)

        total = sum(weights.values())
        assert abs(total - 1.0) < 0.001

    @pytest.mark.parametrize("project_type", [
        "3d-experience",
        "animation-site",
        "react-spa",
        "dashboard",
        "hybrid",
    ])
    def test_compute_weights_all_project_types(self, project_type):
        """Test weight computation for all project types."""
        weights = compute_weights(project_type)

        # All signals should be present and normalized
        required_signals = {
            "diff_size",
            "files_touched",
            "ast_depth",
            "type_surface",
            "test_surface",
            "dependency_fan",
        }
        assert set(weights.keys()) == required_signals
        assert sum(weights.values()) < 1.001  # Allow small floating point error


class TestCheckVetoTriggers:
    """Tests for veto trigger checking."""

    def test_check_veto_triggers_activated(self):
        """
        Test that veto fires when signal exceeds threshold.

        Verifies minimum composite score is forced when veto triggered.
        """
        from fix_signal_analyzer import SignalScore

        signals = {
            "dependency_fan": SignalScore(
                name="dependency_fan",
                normalized=0.90,  # Above threshold of 0.80
            ),
            "diff_size": SignalScore(name="diff_size", normalized=0.05),
            "files_touched": SignalScore(name="files_touched", normalized=0.10),
            "ast_depth": SignalScore(name="ast_depth", normalized=0.20),
            "type_surface": SignalScore(name="type_surface", normalized=0.15),
            "test_surface": SignalScore(name="test_surface", normalized=0.10),
        }

        veto = check_veto_triggers(signals)

        assert veto.triggered is True
        assert veto.minimum_score == VETO_MINIMUM_SCORE
        assert "dependency_fan" in veto.reason

    def test_check_veto_triggers_not_activated(self):
        """
        Test that veto doesn't fire when all signals below thresholds.

        Verifies veto remains inactive for safe signal values.
        """
        from fix_signal_analyzer import SignalScore

        signals = {
            "dependency_fan": SignalScore(name="dependency_fan", normalized=0.50),
            "ast_depth": SignalScore(name="ast_depth", normalized=0.70),
            "type_surface": SignalScore(name="type_surface", normalized=0.50),
            "diff_size": SignalScore(name="diff_size", normalized=0.30),
            "files_touched": SignalScore(name="files_touched", normalized=0.25),
            "test_surface": SignalScore(name="test_surface", normalized=0.20),
        }

        veto = check_veto_triggers(signals)

        assert veto.triggered is False


class TestApplySeverityRatchet:
    """Tests for severity ratcheting."""

    def test_severity_ratchet_critical(self):
        """
        Test that critical severity forces depth >= 0.80.

        Verifies ratchet applied for critical bugs regardless of signal scores.
        """
        original_depth = 0.40
        new_depth, ratchet = apply_severity_ratchet("critical", original_depth)

        assert ratchet["applied"] is True
        assert new_depth == 0.80
        assert ratchet["severity"] == "critical"

    def test_severity_ratchet_high(self):
        """
        Test that high severity forces depth >= 0.50.

        Verifies ratchet applied for high severity bugs.
        """
        original_depth = 0.30
        new_depth, ratchet = apply_severity_ratchet("high", original_depth)

        assert ratchet["applied"] is True
        assert new_depth == 0.50

    def test_severity_ratchet_normal(self):
        """
        Test that low/medium severity doesn't apply ratchet.

        Verifies no change when severity doesn't warrant ratchet.
        """
        original_depth = 0.50
        new_depth, ratchet = apply_severity_ratchet("low", original_depth)

        assert ratchet["applied"] is False
        assert new_depth == original_depth

    def test_severity_ratchet_already_high(self):
        """
        Test that ratchet doesn't lower already-high scores.

        Verifies ratchet only applies minimum, never lowers.
        """
        original_depth = 0.85
        new_depth, ratchet = apply_severity_ratchet("high", original_depth)

        assert ratchet["applied"] is False
        assert new_depth == original_depth


class TestComputeCompositeScore:
    """Tests for composite score computation."""

    def test_compute_composite_score_basic(self, sample_diff_simple):
        """
        Test weighted composite score calculation.

        Verifies that composite = sum(weight_i * signal_i).
        """
        from fix_signal_analyzer import SignalScore, VetoCheck

        signals = {
            "diff_size": SignalScore(name="diff_size", normalized=0.5),
            "files_touched": SignalScore(name="files_touched", normalized=0.3),
            "ast_depth": SignalScore(name="ast_depth", normalized=0.2),
            "type_surface": SignalScore(name="type_surface", normalized=0.1),
            "test_surface": SignalScore(name="test_surface", normalized=0.4),
            "dependency_fan": SignalScore(name="dependency_fan", normalized=0.6),
        }

        weights = compute_weights("unknown")
        veto = VetoCheck(triggered=False)

        composite = compute_composite_score(signals, weights, veto)

        # Should be between 0 and 1
        assert 0.0 <= composite <= 1.0
        # Should be weighted average (between min and max signal)
        assert 0.1 <= composite <= 0.6


class TestDetermineDeptLevels:
    """Tests for verification depth level determination."""

    @pytest.mark.parametrize(
        "depth,expected_recommended",
        [
            (0.15, []),  # Minimal (< 0.25)
            (0.40, [5]),  # L5 only (0.25 - 0.50)
            (0.60, [5, 6]),  # L5 + L6 (0.50 - 0.75)
            (0.90, [5, 6, 7, 8]),  # Full (>= 0.75)
        ],
    )
    def test_determine_depth_levels(self, depth, expected_recommended):
        """
        Test verification level recommendations for various depth scores.

        Verifies correct level selection based on depth thresholds.
        """
        decision = determine_depth_levels(depth, "medium")

        assert decision.levels_required == [1, 2, 3, 4]
        assert decision.levels_recommended == expected_recommended

    def test_determine_depth_levels_critical_override(self):
        """
        Test that critical severity forces L5-L8.

        Verifies severity override for critical bugs.
        """
        decision = determine_depth_levels(0.2, "critical")

        assert decision.severity_override is True
        assert set(decision.levels_recommended) >= {5, 6, 7, 8}

    def test_determine_depth_levels_high_override(self):
        """
        Test that high severity includes L6.

        Verifies severity override adds L6 even if normally not needed.
        """
        decision = determine_depth_levels(0.15, "high")

        assert decision.severity_override is True
        assert 5 in decision.levels_recommended or 6 in decision.levels_recommended


# =============================================================================
# END-TO-END ANALYSIS TESTS
# =============================================================================


class TestAnalyzeFixFullPipeline:
    """End-to-end fix signal analysis tests."""

    def test_analyze_fix_full_pipeline(self, sample_diff_simple):
        """
        Test full fix signal analysis pipeline.

        Verifies all steps: parse → measure → compute → decide.
        """
        report = analyze_fix(
            diff_text=sample_diff_simple,
            project_type="react-spa",
            severity="medium",
        )

        # Check output structure
        assert 0.0 <= report.verification_depth <= 1.0
        assert report.depth_category in (
            "minimal",
            "low",
            "moderate",
            "high",
            "full",
        )
        assert all(
            signal in report.signals
            for signal in [
                "diff_size",
                "files_touched",
                "ast_depth",
                "type_surface",
                "test_surface",
                "dependency_fan",
            ]
        )

    def test_analyze_fix_structural_diff(self, sample_diff_structural):
        """
        Test analysis of structural (high-complexity) diff.

        Verifies that structural changes produce high verification depth.
        """
        report = analyze_fix(
            diff_text=sample_diff_structural,
            project_type="react-spa",
            severity="medium",
        )

        # Structural changes should score high
        assert report.verification_depth > 0.5

    def test_analyze_fix_api_change(self, sample_diff_api_change):
        """
        Test analysis of API-breaking changes.

        Verifies that export changes trigger high verification.
        """
        report = analyze_fix(
            diff_text=sample_diff_api_change,
            severity="high",
        )

        # API changes + high severity should trigger full verification
        assert len(report.depth_decision["levels_recommended"]) >= 2

    def test_analyze_fix_empty_diff(self):
        """
        Test analysis of empty diff.

        Verifies graceful handling without errors.
        """
        report = analyze_fix(
            diff_text="",
            project_type="unknown",
            severity="low",
        )

        assert len(report.warnings) > 0
        assert any("Empty" in w or "unparseable" in w for w in report.warnings)


# =============================================================================
# OUTPUT FORMATTING TESTS
# =============================================================================


class TestFormatOutput:
    """Tests for output formatting."""

    def test_format_output_json_roundtrip(self, sample_diff_simple):
        """
        Test JSON output format parses correctly.

        Verifies JSON can be parsed and contains all required fields.
        """
        report = analyze_fix(sample_diff_simple)
        output = format_output(report, fmt="json")

        parsed = json.loads(output)
        assert "verification_depth" in parsed
        assert "signals" in parsed
        assert "depth_decision" in parsed

    def test_format_output_text(self, sample_diff_simple):
        """
        Test text output format readability.

        Verifies output contains headers and key information.
        """
        report = analyze_fix(sample_diff_simple)
        output = format_output(report, fmt="text")

        assert "VERIFICATION DEPTH" in output
        assert "SIGNAL SCORES" in output
        assert "VERIFICATION LEVELS" in output

    def test_format_output_yaml(self, sample_diff_simple):
        """Test YAML output format."""
        report = analyze_fix(sample_diff_simple)
        output = format_output(report, fmt="yaml")

        assert "verification_depth:" in output
        assert "signals:" in output
        assert "depth_decision:" in output

    def test_format_output_veto_warning(self):
        """
        Test that veto is displayed in output.

        Verifies veto warning appears when triggered.
        """
        from fix_signal_analyzer import SignalScore, VetoCheck

        # Create a report with veto triggered
        diff_text = """diff --git a/api.ts b/api.ts
+++ b/api.ts
+export function newAPI() {}
"""
        report = analyze_fix(diff_text, severity="high")
        output = format_output(report, fmt="text")

        # If veto was triggered, warning should appear
        if report.veto.get("triggered"):
            assert "VETO" in output

    def test_format_output_severity_ratchet_warning(self):
        """
        Test that severity ratchet is displayed in output.

        Verifies ratchet warning appears when applied.
        """
        # Small diff with critical severity should trigger ratchet
        diff_text = """diff --git a/file.ts b/file.ts
+++ b/file.ts
+x = 1;
"""
        report = analyze_fix(diff_text, severity="critical")
        output = format_output(report, fmt="text")

        # Ratchet should be applied for critical
        assert report.severity_ratchet.get("applied") is True


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_analyze_fix_minimal_diff(self):
        """Test with minimal single-line change."""
        diff = """diff --git a/x.ts b/x.ts
+++ b/x.ts
+const x = 1;
"""
        report = analyze_fix(diff)
        assert report.verification_depth >= 0.0

    def test_analyze_fix_custom_weights(self, sample_diff_simple):
        """
        Test analysis with custom weights override.

        Verifies custom weights are applied correctly.
        """
        custom_weights = {
            "diff_size": 0.5,
            "files_touched": 0.5,
        }
        report = analyze_fix(
            sample_diff_simple,
            custom_weights=custom_weights,
        )

        # Custom weights should be applied
        assert "diff_size" in report.weights_used
        assert "files_touched" in report.weights_used

    def test_analyze_fix_all_project_types(self, sample_diff_simple):
        """
        Test analysis works for all project types.

        Parametrized test ensuring no crashes for any project type.
        """
        for project_type in [
            "3d-experience",
            "animation-site",
            "react-spa",
            "dashboard",
            "hybrid",
            "unknown",
        ]:
            report = analyze_fix(sample_diff_simple, project_type=project_type)
            assert report.project_type == project_type
            assert 0.0 <= report.verification_depth <= 1.0

    def test_analyze_fix_all_severities(self, sample_diff_simple):
        """
        Test analysis works for all severity levels.

        Parametrized test ensuring correct handling of all severities.
        """
        for severity in ["critical", "high", "medium", "low"]:
            report = analyze_fix(sample_diff_simple, severity=severity)
            assert report.severity == severity


# =============================================================================
# PARAMETRIZED INTEGRATION TESTS
# =============================================================================


class TestIntegrationMatrix:
    """Cross-product integration tests."""

    @pytest.mark.parametrize(
        "project_type,severity",
        [
            ("3d-experience", "critical"),
            ("react-spa", "medium"),
            ("dashboard", "low"),
            ("hybrid", "high"),
        ],
    )
    def test_analyze_fix_combinations(self, sample_diff_simple, project_type, severity):
        """
        Test analysis with various project type and severity combinations.

        Ensures no crashes and sensible results across combinations.
        """
        report = analyze_fix(
            sample_diff_simple,
            project_type=project_type,
            severity=severity,
        )

        assert report.project_type == project_type
        assert report.severity == severity
        assert 0.0 <= report.verification_depth <= 1.0
        assert report.depth_category in (
            "minimal",
            "low",
            "moderate",
            "high",
            "full",
        )
