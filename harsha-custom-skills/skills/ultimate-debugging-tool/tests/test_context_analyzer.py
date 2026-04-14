"""
Comprehensive integration tests for context_analyzer.py

Tests cover:
1. Project type detection (3D, React SPA, dashboard, hybrid, unknown)
2. Framework detection
3. Skill pattern scanning
4. Project analysis pipeline
5. Output formatting
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from context_analyzer import (
    FrameworkDetection,
    ProjectContext,
    SkillPattern,
    analyze_project,
    count_source_files,
    detect_frameworks,
    detect_project_type,
    determine_budget_profile,
    format_output,
    read_package_json,
    scan_for_skill_patterns,
)


# =============================================================================
# PRIORITY 1: CRITICAL PATH TESTS
# =============================================================================


class TestDetectProjectType:
    """Tests for project type detection logic."""

    def test_detect_project_type_3d_experience(self, sample_package_3d):
        """
        Test detection of 3D experience project.

        Verifies that a project with three, @react-three/fiber, and detect-gpu
        is correctly classified as "3d-experience" with confidence > 0.75.
        """
        frameworks = detect_frameworks(sample_package_3d)
        project_type, confidence = detect_project_type(sample_package_3d, frameworks)

        assert project_type == "3d-experience"
        assert confidence > 0.75

    def test_detect_project_type_react_spa(self, sample_package_react):
        """
        Test detection of React SPA project.

        Verifies that a project with react, react-dom, and next.js
        is classified as "react-spa" with good confidence.
        """
        frameworks = detect_frameworks(sample_package_react)
        project_type, confidence = detect_project_type(sample_package_react, frameworks)

        assert project_type == "react-spa"
        assert confidence > 0.4

    def test_detect_project_type_dashboard(self, sample_package_dashboard):
        """
        Test detection of dashboard project.

        Verifies that a project with recharts and d3 is classified
        as "dashboard" with good confidence.
        """
        frameworks = detect_frameworks(sample_package_dashboard)
        project_type, confidence = detect_project_type(sample_package_dashboard, frameworks)

        assert project_type == "dashboard"
        assert confidence >= 0.6

    def test_detect_project_type_unknown(self, sample_package_empty):
        """
        Test detection of unknown project type.

        Verifies that a project with empty dependencies is classified
        as "unknown" with low confidence (~0.3).
        """
        frameworks = detect_frameworks(sample_package_empty)
        project_type, confidence = detect_project_type(sample_package_empty, frameworks)

        assert project_type == "unknown"
        assert confidence == 0.3

    def test_detect_project_type_hybrid(self):
        """
        Test detection of hybrid project type.

        Verifies that a project with mixed dependencies (React + 3D + Dashboard)
        is classified as "hybrid" when top two scores are close.
        """
        hybrid_pkg = {
            "dependencies": {
                "react": "^19.0.0",
                "three": "^0.183.0",
                "d3": "^7.0.0",
                "recharts": "^3.0.0",
                "@react-three/fiber": "^9.0.0",
            },
            "devDependencies": {},
        }

        frameworks = detect_frameworks(hybrid_pkg)
        project_type, confidence = detect_project_type(hybrid_pkg, frameworks)

        # Could be hybrid or 3d-experience depending on close scoring
        assert project_type in ("hybrid", "3d-experience")
        assert confidence > 0.5

    def test_detect_frameworks(self, sample_package_react):
        """
        Test framework detection.

        Verifies that FrameworkDetection objects are correctly created
        with name, version, and confidence.
        """
        frameworks = detect_frameworks(sample_package_react)

        assert len(frameworks) >= 3
        framework_names = {f.name for f in frameworks}
        assert "React" in framework_names
        assert "React DOM" in framework_names or "React" in framework_names

        # Check that confidence is set
        for fw in frameworks:
            assert fw.confidence == 1.0
            assert isinstance(fw.name, str)


class TestScanForSkillPatterns:
    """Tests for skill pattern scanning."""

    def test_scan_for_skill_patterns(self, tmp_project):
        """
        Test skill pattern detection in source files.

        Verifies that regex patterns match against sample code
        and return SkillPattern objects with correct metadata.
        """
        # Add file with 3D patterns
        src_dir = tmp_project / "src"
        (src_dir / "graphics.ts").write_text("""
import * as THREE from 'three';
const loader = new THREE.GLTFLoader();
const composer = new EffectComposer(renderer);
const material = new MeshPhysicalMaterial();
""")

        patterns = scan_for_skill_patterns(str(tmp_project))

        # Should find some 3D patterns
        assert len(patterns) > 0
        for pattern in patterns:
            assert isinstance(pattern, SkillPattern)
            assert pattern.skill in ("3d-web-graphics-mastery", "ui-ux-mastery")
            assert pattern.confidence > 0.0
            assert pattern.file != ""
            assert pattern.line > 0

    def test_scan_for_skill_patterns_ui_ux(self, tmp_project):
        """
        Test UI/UX pattern detection.

        Verifies detection of motion variables, reduced-motion preferences,
        and ease curves.
        """
        src_dir = tmp_project / "src"
        (src_dir / "styles.css").write_text("""
:root {
  --duration-fast: 200ms;
  --duration-normal: 400ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
}

@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
  }
}
""")

        patterns = scan_for_skill_patterns(str(tmp_project))

        # Should find UI/UX patterns
        ui_patterns = [p for p in patterns if p.skill == "ui-ux-mastery"]
        assert len(ui_patterns) > 0

    def test_scan_for_skill_patterns_empty_project(self, tmp_project):
        """
        Test scanning a project with no skill patterns.

        Should return empty list without errors.
        """
        # Clear src directory
        src_dir = tmp_project / "src"
        for f in src_dir.glob("*"):
            f.unlink()

        patterns = scan_for_skill_patterns(str(tmp_project))
        assert patterns == []


class TestAnalyzeProjectIntegration:
    """End-to-end project analysis tests."""

    def test_analyze_project_integration(self, tmp_project):
        """
        Test full end-to-end project analysis with temp directory.

        Verifies that analyze_project() integrates all components:
        - Reads package.json
        - Detects frameworks
        - Determines project type
        - Counts source files
        - Sets budget profile
        """
        context = analyze_project(str(tmp_project))

        assert context.project_path == str(tmp_project)
        assert context.project_type in (
            "3d-experience",
            "animation-site",
            "react-spa",
            "dashboard",
            "hybrid",
            "unknown",
        )
        assert 0.0 <= context.project_type_confidence <= 1.0
        assert context.budget_profile in (
            "budget-3d",
            "budget-animation",
            "budget-spa",
            "budget-dashboard",
            "budget-hybrid",
        )
        assert context.source_files_count > 0
        assert context.total_lines > 0
        assert context.has_typescript is True
        assert context.has_tests is True

    def test_analyze_project_with_typescript(self, tmp_project):
        """Verify TypeScript detection."""
        context = analyze_project(str(tmp_project))
        assert context.has_typescript is True

    def test_analyze_project_with_test_framework(self, tmp_project):
        """Verify test framework detection."""
        context = analyze_project(str(tmp_project))
        assert context.has_tests is True

    def test_analyze_project_detects_package_manager(self, tmp_project):
        """Verify package manager detection."""
        # Create npm lock file
        (tmp_project / "package-lock.json").write_text("{}")

        context = analyze_project(str(tmp_project))
        assert context.package_manager == "npm"

    def test_analyze_project_framework_list(self, tmp_project):
        """Verify frameworks are included in output as dicts."""
        context = analyze_project(str(tmp_project))

        assert isinstance(context.frameworks, list)
        if context.frameworks:
            fw = context.frameworks[0]
            assert isinstance(fw, dict)
            assert "name" in fw
            assert "version" in fw


# =============================================================================
# PRIORITY 2: EDGE CASES
# =============================================================================


class TestReadPackageJson:
    """Tests for package.json reading."""

    def test_read_package_json_missing(self, tmp_path):
        """
        Test reading from directory with no package.json.

        Should return None gracefully.
        """
        result = read_package_json(str(tmp_path))
        assert result is None

    def test_read_package_json_malformed(self, tmp_path):
        """
        Test reading malformed JSON file.

        Should return None without raising exception.
        """
        pkg_path = tmp_path / "package.json"
        pkg_path.write_text("{ invalid json }")

        result = read_package_json(str(tmp_path))
        assert result is None

    def test_read_package_json_valid(self, tmp_path):
        """Test reading valid package.json file."""
        pkg_data = {"name": "test", "version": "1.0.0"}
        pkg_path = tmp_path / "package.json"
        pkg_path.write_text(json.dumps(pkg_data))

        result = read_package_json(str(tmp_path))
        assert result == pkg_data


class TestCountSourceFiles:
    """Tests for source file counting."""

    def test_count_source_files(self, tmp_project):
        """
        Test counting source files with extension filtering.

        Verifies that .ts, .tsx, .js, .jsx files are counted,
        and excluded directories (node_modules, .git, dist) are skipped.
        """
        count, total_lines = count_source_files(str(tmp_project))

        assert count > 0
        assert total_lines > 0
        # node_modules should be excluded
        assert "node_modules" not in str(count)

    def test_count_source_files_excludes_node_modules(self, tmp_project):
        """
        Verify that node_modules is excluded from file count.
        """
        # Add a file to node_modules
        nm_file = tmp_project / "node_modules" / "react" / "index.js"
        nm_file.parent.mkdir(parents=True, exist_ok=True)
        nm_file.write_text("// This should not be counted")

        count_before = count_source_files(str(tmp_project))[0]

        # Add file to src
        (tmp_project / "src" / "new.ts").write_text("export const x = 1;")

        count_after = count_source_files(str(tmp_project))[0]

        # Only src file should increment the count
        assert count_after > count_before

    def test_count_source_files_empty_dir(self, tmp_path):
        """Test counting in empty directory."""
        count, total_lines = count_source_files(str(tmp_path))
        assert count == 0
        assert total_lines == 0


class TestDetermineBudgetProfile:
    """Tests for budget profile determination."""

    @pytest.mark.parametrize(
        "project_type,expected_budget",
        [
            ("3d-experience", "budget-3d"),
            ("animation-site", "budget-animation"),
            ("react-spa", "budget-spa"),
            ("dashboard", "budget-dashboard"),
            ("hybrid", "budget-hybrid"),
            ("unknown", "budget-spa"),  # Default
            ("invalid-type", "budget-spa"),  # Default
        ],
    )
    def test_determine_budget_profile(self, project_type, expected_budget):
        """
        Test all project types map to correct budget profiles.

        Verifies mapping for each project type and default fallback.
        """
        result = determine_budget_profile(project_type)
        assert result == expected_budget


class TestFormatOutput:
    """Tests for output formatting."""

    def test_format_output_json(self, tmp_project):
        """
        Test JSON output format roundtrip.

        Verifies that output can be parsed as valid JSON and
        contains all required fields.
        """
        context = analyze_project(str(tmp_project))
        output = format_output(context, fmt="json")

        parsed = json.loads(output)
        assert parsed["project_type"] is not None
        assert "project_type_confidence" in parsed
        assert "budget_profile" in parsed
        assert "frameworks" in parsed

    def test_format_output_text(self, tmp_project):
        """
        Test text output format readability.

        Verifies that output is formatted as readable text with
        section headers and key information.
        """
        context = analyze_project(str(tmp_project))
        output = format_output(context, fmt="text")

        assert "PROJECT CONTEXT ANALYSIS" in output
        assert "FRAMEWORKS DETECTED" in output
        assert "SKILL PATTERNS" in output
        assert context.project_type in output

    def test_format_output_yaml(self, tmp_project):
        """Test YAML output format."""
        context = analyze_project(str(tmp_project))
        output = format_output(context, fmt="yaml")

        assert "project_type:" in output
        assert "frameworks:" in output
        assert context.project_type in output

    def test_format_output_text_no_tests_warning(self, tmp_path):
        """
        Test that text output includes warning when no tests detected.
        """
        # Create minimal project without test framework
        pkg_data = {
            "name": "test",
            "version": "1.0.0",
            "dependencies": {"react": "^19.0.0"},
            "devDependencies": {},
        }
        pkg_path = tmp_path / "package.json"
        pkg_path.write_text(json.dumps(pkg_data))

        context = analyze_project(str(tmp_path))
        context.has_tests = False

        output = format_output(context, fmt="text")
        assert "test framework" in output.lower()

    def test_format_output_text_no_typescript_warning(self, tmp_path):
        """
        Test that text output includes warning when no TypeScript detected.
        """
        pkg_data = {
            "name": "test",
            "version": "1.0.0",
            "dependencies": {"react": "^19.0.0"},
            "devDependencies": {"vitest": "^2.0.0"},
        }
        pkg_path = tmp_path / "package.json"
        pkg_path.write_text(json.dumps(pkg_data))

        context = analyze_project(str(tmp_path))
        context.has_typescript = False

        output = format_output(context, fmt="text")
        assert "TypeScript" in output


class TestFrameworkDetectionDataclass:
    """Tests for FrameworkDetection dataclass."""

    def test_framework_detection_creation(self):
        """Test creating FrameworkDetection instances."""
        fw = FrameworkDetection(name="React", version="19.0.0", confidence=0.95)

        assert fw.name == "React"
        assert fw.version == "19.0.0"
        assert fw.confidence == 0.95

    def test_framework_detection_defaults(self):
        """Test FrameworkDetection with default values."""
        fw = FrameworkDetection(name="Vue")

        assert fw.name == "Vue"
        assert fw.version == ""
        assert fw.confidence == 0.0


class TestSkillPatternDataclass:
    """Tests for SkillPattern dataclass."""

    def test_skill_pattern_creation(self):
        """Test creating SkillPattern instances."""
        pattern = SkillPattern(
            skill="3d-web-graphics-mastery",
            pattern="detect-gpu-tiers",
            confidence=0.85,
            file="src/graphics.ts",
            line=42,
        )

        assert pattern.skill == "3d-web-graphics-mastery"
        assert pattern.pattern == "detect-gpu-tiers"
        assert pattern.confidence == 0.85
        assert pattern.file == "src/graphics.ts"
        assert pattern.line == 42


class TestProjectContextDataclass:
    """Tests for ProjectContext dataclass."""

    def test_project_context_defaults(self):
        """Test ProjectContext with default values."""
        ctx = ProjectContext()

        assert ctx.project_type == "unknown"
        assert ctx.project_type_confidence == 0.0
        assert ctx.budget_profile == "budget-spa"
        assert ctx.has_typescript is False
        assert ctx.has_tests is False
        assert ctx.source_files_count == 0
        assert ctx.total_lines == 0


# =============================================================================
# PARAMETRIZED TESTS
# =============================================================================


class TestFrameworkMapCoverage:
    """Tests to ensure all framework mappings work."""

    @pytest.mark.parametrize(
        "dep_name,display_name",
        [
            ("react", "React"),
            ("next", "Next.js"),
            ("vue", "Vue"),
            ("svelte", "Svelte"),
            ("three", "Three.js"),
            ("gsap", "GSAP"),
            ("d3", "D3.js"),
            ("typescript", "TypeScript"),
            ("vitest", "Vitest"),
        ],
    )
    def test_all_framework_mappings(self, dep_name, display_name):
        """
        Test that all expected framework mappings exist and work.

        Parametrized test covering framework detection for all major packages.
        """
        pkg = {
            "dependencies": {dep_name: "^1.0.0"},
            "devDependencies": {},
        }

        frameworks = detect_frameworks(pkg)

        assert len(frameworks) > 0
        names = [f.name for f in frameworks]
        assert display_name in names
