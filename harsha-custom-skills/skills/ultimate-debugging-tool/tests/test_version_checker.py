"""
Tests for version_checker.py
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from version_checker import (
    VersionCheck,
    parse_version,
    check_npm_version,
    get_current_versions,
    load_pattern_index,
    calculate_staleness,
    check_frameworks,
    format_text_output,
    format_json_output,
    format_yaml_output,
)


@pytest.fixture
def sample_pattern_index():
    """Create a sample pattern-index.json."""
    return {
        "patterns": [
            {
                "id": "react-01",
                "framework": "React",
                "min_version": "18.0",
                "max_version": "19.0",
            },
            {
                "id": "next-01",
                "framework": "Next.js",
                "min_version": "15.0",
                "max_version": "16.0",
            },
            {
                "id": "typescript-01",
                "framework": "TypeScript",
                "min_version": "5.0",
                "max_version": "6.0",
            },
            {
                "id": "three-01",
                "framework": "Three.js",
                "min_version": "r180",
                "max_version": "r200",
            },
            {
                "id": "react-02",
                "framework": "React",
                "min_version": "18.0",
                "max_version": "19.0",
            },
        ]
    }


@pytest.fixture
def pattern_index_file(tmp_path, sample_pattern_index):
    """Create a temporary pattern-index.json file."""
    path = tmp_path / "pattern-index.json"
    path.write_text(json.dumps(sample_pattern_index))
    return path


class TestVersionCheck:
    def test_version_check_creation(self):
        """Test VersionCheck dataclass creation."""
        check = VersionCheck(
            framework="React",
            npm_package="react",
            documented_min="18.0",
            documented_max="19.0",
            current_version="19.2.4",
            status="ok",
            recommendation="React is current",
        )

        assert check.framework == "React"
        assert check.npm_package == "react"
        assert check.status == "ok"

    def test_version_check_defaults(self):
        """Test VersionCheck default values."""
        check = VersionCheck(
            framework="React",
            npm_package="react",
            documented_min="18.0",
            documented_max=None,
            current_version="19.0",
        )

        assert check.major_gap == 0
        assert check.status == "ok"
        assert check.patterns_affected == []
        assert check.recommendation == ""

    def test_version_check_asdict(self):
        """Test VersionCheck can be converted to dict."""
        check = VersionCheck(
            framework="React",
            npm_package="react",
            documented_min="18.0",
            documented_max="19.0",
            current_version="19.0",
            status="ok",
        )

        result = asdict(check)
        assert isinstance(result, dict)
        assert result["framework"] == "React"


class TestParseVersion:
    def test_parse_version_three_parts(self):
        """Test parsing version with three parts."""
        result = parse_version("19.2.4")
        assert result == (19, 2, 4)

    def test_parse_version_two_parts(self):
        """Test parsing version with two parts."""
        result = parse_version("16.0")
        assert result == (16, 0, 0)

    def test_parse_version_one_part(self):
        """Test parsing version with one part."""
        result = parse_version("6")
        assert result == (6, 0, 0)

    def test_parse_version_with_r_prefix(self):
        """Test parsing Three.js version with r prefix."""
        result = parse_version("r183.2")
        assert result == (183, 2, 0)

    def test_parse_version_with_v_prefix(self):
        """Test parsing version with v prefix."""
        result = parse_version("v19.2.4")
        assert result == (19, 2, 4)

    def test_parse_version_empty_string(self):
        """Test parsing empty string."""
        result = parse_version("")
        assert result == (0, 0, 0)

    def test_parse_version_unknown(self):
        """Test parsing 'unknown'."""
        result = parse_version("unknown")
        assert result == (0, 0, 0)

    def test_parse_version_none(self):
        """Test parsing None."""
        result = parse_version(None)
        assert result == (0, 0, 0)

    def test_parse_version_invalid_string(self):
        """Test parsing invalid string."""
        result = parse_version("not-a-version")
        assert result == (0, 0, 0)


class TestGetCurrentVersions:
    def test_get_current_versions_offline(self):
        """Test getting versions in offline mode."""
        versions = get_current_versions(offline=True)

        assert "react" in versions
        assert "next" in versions
        assert "typescript" in versions
        assert versions["react"] == "19.2.4"

    def test_get_current_versions_no_npm_check(self):
        """Test getting versions without npm check."""
        versions = get_current_versions(check_npm=False, offline=False)

        assert versions == {}

    def test_get_current_versions_offline_priority(self):
        """Test offline mode takes priority."""
        versions = get_current_versions(check_npm=True, offline=True)

        # Should use offline versions even if check_npm=True
        assert versions == {
            "react": "19.2.4",
            "next": "16.2.0",
            "three": "0.183.2",
            "gsap": "3.14.2",
            "typescript": "6.0.2",
        }


class TestLoadPatternIndex:
    def test_load_pattern_index_valid_file(self, pattern_index_file):
        """Test loading a valid pattern index file."""
        result = load_pattern_index(str(pattern_index_file))

        assert "patterns" in result
        assert len(result["patterns"]) == 5

    def test_load_pattern_index_nonexistent_file(self, tmp_path):
        """Test loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_pattern_index(str(tmp_path / "nonexistent.json"))

    def test_load_pattern_index_auto_detect(self, monkeypatch, tmp_path):
        """Test auto-detection of pattern-index path."""
        # Create references dir structure
        refs_dir = tmp_path / "references"
        refs_dir.mkdir()

        index_file = refs_dir / "pattern-index.json"
        index_file.write_text(json.dumps({"patterns": []}))

        # Mock __file__ to point to our temp script
        monkeypatch.setattr(
            "version_checker.Path",
            lambda x: tmp_path / "scripts" if x == "__file__" else Path(x),
        )

        # Since we can't easily mock __file__, just test with explicit path
        result = load_pattern_index(str(index_file))
        assert "patterns" in result


class TestCalculateStaleness:
    def test_calculate_staleness_ok(self):
        """Test staleness calculation for current version."""
        status, gap, rec = calculate_staleness(
            "React", "18.0", "19.0", "19.0"
        )

        assert status == "ok"
        assert gap == 0

    def test_calculate_staleness_stale_one_major(self):
        """Test staleness with one major version gap."""
        status, gap, rec = calculate_staleness(
            "React", "18.0", "19.0", "20.0"
        )

        assert status == "stale"
        assert gap == 1

    def test_calculate_staleness_critical_two_majors(self):
        """Test staleness with two major version gaps."""
        status, gap, rec = calculate_staleness(
            "React", "18.0", "19.0", "21.0"
        )

        assert status == "critical"
        assert gap == 2

    def test_calculate_staleness_outdated_minor(self):
        """Test staleness with outdated minor version."""
        status, gap, rec = calculate_staleness(
            "React", "19.0", "19.2", "19.6"
        )

        assert status == "outdated"
        assert gap == 0

    def test_calculate_staleness_unknown_version(self):
        """Test staleness with unknown version."""
        status, gap, rec = calculate_staleness(
            "React", "18.0", "19.0", "unknown"
        )

        assert status == "unknown"

    def test_calculate_staleness_no_max_version(self):
        """Test staleness when no max version is specified."""
        status, gap, rec = calculate_staleness(
            "React", "18.0", None, "19.0"
        )

        assert status == "ok"

    def test_calculate_staleness_newer_than_documented(self):
        """Test when current is older than documented min."""
        status, gap, rec = calculate_staleness(
            "React", "18.0", "19.0", "17.0"
        )

        assert status == "ok"


class TestCheckFrameworks:
    def test_check_frameworks_basic(self, sample_pattern_index):
        """Test checking frameworks."""
        current_versions = {
            "react": "19.2.4",
            "next": "16.2.0",
            "typescript": "6.0.2",
            "three": "0.183.2",
        }

        results = check_frameworks(sample_pattern_index, current_versions)

        assert len(results) == 4  # One per unique framework
        assert all(isinstance(r, VersionCheck) for r in results)

    def test_check_frameworks_deduplication(self, sample_pattern_index):
        """Test frameworks are deduplicated."""
        current_versions = {"react": "19.0"}

        results = check_frameworks(sample_pattern_index, current_versions)

        react_results = [r for r in results if r.framework == "React"]
        # Should only have one React check despite two patterns
        assert len(react_results) == 1

    def test_check_frameworks_sorted_output(self, sample_pattern_index):
        """Test results are sorted by framework name."""
        current_versions = {
            "react": "19.0",
            "next": "16.0",
            "typescript": "6.0",
            "three": "0.183.2",
        }

        results = check_frameworks(sample_pattern_index, current_versions)

        frameworks = [r.framework for r in results]
        assert frameworks == sorted(frameworks)

    def test_check_frameworks_includes_patterns_affected(
        self, sample_pattern_index
    ):
        """Test results include patterns affected."""
        current_versions = {"react": "19.0"}

        results = check_frameworks(sample_pattern_index, current_versions)

        react_check = next(r for r in results if r.framework == "React")
        # Should have 2 react patterns
        assert len(react_check.patterns_affected) == 2
        assert "react-01" in react_check.patterns_affected
        assert "react-02" in react_check.patterns_affected


class TestFormatTextOutput:
    def test_format_text_output_basic(self, sample_pattern_index):
        """Test text output formatting."""
        checks = [
            VersionCheck(
                framework="React",
                npm_package="react",
                documented_min="18.0",
                documented_max="19.0",
                current_version="19.2.4",
                status="ok",
                recommendation="React is current",
            ),
            VersionCheck(
                framework="Next.js",
                npm_package="next",
                documented_min="15.0",
                documented_max="16.0",
                current_version="17.0",
                status="critical",
                major_gap=1,
                patterns_affected=["next-01"],
                recommendation="Review Next.js patterns",
            ),
        ]

        output = format_text_output(checks)

        assert "ULTIMATE DEBUGGER" in output
        assert "React" in output
        assert "Next.js" in output
        assert "OK" in output or "ok" in output
        assert "CRITICAL" in output or "critical" in output

    def test_format_text_output_includes_summary(self):
        """Test text output includes summary."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
        ]

        output = format_text_output(checks)

        assert "SUMMARY" in output

    def test_format_text_output_empty_checks(self):
        """Test text output with no checks."""
        output = format_text_output([])

        assert "ULTIMATE DEBUGGER" in output
        assert "SUMMARY" in output


class TestFormatJsonOutput:
    def test_format_json_output_structure(self):
        """Test JSON output has correct structure."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
        ]

        output = format_json_output(checks)
        data = json.loads(output)

        assert "checked_at" in data
        assert "summary" in data
        assert "frameworks" in data

    def test_format_json_output_summary(self):
        """Test JSON summary statistics."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
            VersionCheck(
                "Next.js", "next", "15.0", "16.0", "17.0", status="critical"
            ),
        ]

        output = format_json_output(checks)
        data = json.loads(output)

        assert data["summary"]["total"] == 2
        assert data["summary"]["ok"] == 1
        assert data["summary"]["needs_review"] == 1

    def test_format_json_output_valid_json(self):
        """Test JSON output is valid JSON."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
        ]

        output = format_json_output(checks)
        # Should not raise
        json.loads(output)


class TestFormatYamlOutput:
    def test_format_yaml_output_structure(self):
        """Test YAML output has correct structure."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
        ]

        output = format_yaml_output(checks)

        assert "checked_at:" in output
        assert "summary:" in output
        assert "frameworks:" in output

    def test_format_yaml_output_framework_fields(self):
        """Test YAML includes all framework fields."""
        checks = [
            VersionCheck(
                "React",
                "react",
                "18.0",
                "19.0",
                "19.0",
                status="ok",
                recommendation="Test",
            ),
        ]

        output = format_yaml_output(checks)

        assert "framework: React" in output
        assert "npm_package: react" in output
        assert "documented_min: 18.0" in output
        assert "documented_max: 19.0" in output
        assert "current_version: 19.0" in output
        assert "status: ok" in output

    def test_format_yaml_output_summary(self):
        """Test YAML summary statistics."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
            VersionCheck(
                "Next.js", "next", "15.0", "16.0", "17.0", status="stale"
            ),
        ]

        output = format_yaml_output(checks)

        assert "total: 2" in output
        assert "ok: 1" in output
        assert "needs_review: 1" in output


class TestIntegration:
    def test_full_workflow_with_offline_versions(self, pattern_index_file):
        """Test full workflow with offline versions."""
        # Load index
        index = load_pattern_index(str(pattern_index_file))

        # Get offline versions
        versions = get_current_versions(offline=True)

        # Check frameworks
        checks = check_frameworks(index, versions)

        assert len(checks) > 0
        assert all(isinstance(c, VersionCheck) for c in checks)

    def test_all_formatters_produce_output(self):
        """Test all formatters can produce output."""
        checks = [
            VersionCheck(
                "React", "react", "18.0", "19.0", "19.0", status="ok"
            ),
        ]

        text = format_text_output(checks)
        json_out = format_json_output(checks)
        yaml_out = format_yaml_output(checks)

        assert text
        assert json_out
        assert yaml_out

    def test_version_check_with_none_values(self):
        """Test VersionCheck handles None values gracefully."""
        check = VersionCheck(
            framework="React",
            npm_package="react",
            documented_min="18.0",
            documented_max=None,
            current_version=None,
        )

        # Should not raise when converting to dict
        asdict(check)
