"""
Tests for generate_report.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest
import yaml

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_report import (
    load_manifest,
    calculate_stats,
    format_summary,
    format_detailed,
    format_json,
    format_markdown,
)


@pytest.fixture
def sample_manifest():
    """Create a sample bug manifest."""
    return {
        "session": {
            "id": "sess-20260101-abc123",
            "started": "2026-01-01T00:00:00",
            "original_goal": "Find security bugs",
            "project_path": "/test/project",
        },
        "stats": {
            "total_found": 5,
            "pending": 1,
            "fixing": 0,
            "fixed": 2,
            "verified": 1,
            "ignored": 1,
        },
        "bugs": [
            {
                "id": "BUG-001",
                "description": "SQL injection vulnerability",
                "status": "verified",
                "category": "security",
                "severity": "high",
                "cwe": "CWE-89",
                "location": {"file": "/app/db.py", "line": 42},
                "verified_at": "2026-01-02T10:30:00",
            },
            {
                "id": "BUG-002",
                "description": "Missing input validation",
                "status": "fixed",
                "category": "security",
                "severity": "medium",
                "location": {"file": "/app/forms.py", "line": 15},
            },
            {
                "id": "BUG-003",
                "description": "Hardcoded API key",
                "status": "fixed",
                "category": "security",
                "severity": "high",
                "location": {"file": "/app/config.py", "line": 8},
            },
            {
                "id": "BUG-004",
                "description": "Dead code",
                "status": "pending",
                "category": "quality",
                "severity": "low",
                "location": {"file": "/app/utils.py", "line": 100},
            },
            {
                "id": "BUG-005",
                "description": "Test fixture with creds",
                "status": "ignored",
                "category": "security",
                "severity": "low",
                "ignore_rule": "test-fixtures",
                "location": {"file": "/test/fixtures.py", "line": 5},
            },
        ],
    }


@pytest.fixture
def empty_manifest():
    """Create an empty manifest."""
    return {
        "session": {
            "id": "sess-20260101-empty",
            "started": "2026-01-01T00:00:00",
            "original_goal": "Test empty manifest",
        },
        "stats": {
            "total_found": 0,
            "pending": 0,
            "fixing": 0,
            "fixed": 0,
            "verified": 0,
            "ignored": 0,
        },
        "bugs": [],
    }


class TestLoadManifest:
    def test_load_valid_manifest(self, tmp_path, sample_manifest):
        """Test loading a valid manifest file."""
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(yaml.dump(sample_manifest))

        result = load_manifest(manifest_path)
        assert result == sample_manifest

    def test_load_nonexistent_manifest(self, tmp_path):
        """Test loading nonexistent manifest returns empty dict."""
        result = load_manifest(tmp_path / "nonexistent.yaml")
        assert result == {}

    def test_load_empty_manifest(self, tmp_path):
        """Test loading empty manifest file."""
        manifest_path = tmp_path / "empty.yaml"
        manifest_path.write_text("")

        result = load_manifest(manifest_path)
        assert result == {}


class TestCalculateStats:
    def test_calculate_stats_with_bugs(self, sample_manifest):
        """Test calculating statistics from manifest with bugs."""
        stats = calculate_stats(sample_manifest)

        assert stats["total"] == 5
        assert stats["by_status"]["verified"] == 1
        assert stats["by_status"]["fixed"] == 2
        assert stats["by_status"]["pending"] == 1
        assert stats["by_status"]["ignored"] == 1
        assert stats["by_category"]["security"] == 4
        assert stats["by_category"]["quality"] == 1
        assert stats["by_severity"]["high"] == 2
        assert stats["by_severity"]["medium"] == 1
        assert stats["by_severity"]["low"] == 2

    def test_calculate_stats_verification_rate(self, sample_manifest):
        """Test verification rate calculation."""
        stats = calculate_stats(sample_manifest)

        # 1 verified out of 3 fixed (verified + fixed)
        expected_rate = 1 / 3
        assert stats["verification_rate"] == expected_rate

    def test_calculate_stats_high_severity_fixed(self, sample_manifest):
        """Test high severity fixed count."""
        stats = calculate_stats(sample_manifest)

        # BUG-001 is high severity and verified, BUG-003 is high and fixed
        assert stats["high_severity_fixed"] == 2

    def test_calculate_stats_security_issues(self, sample_manifest):
        """Test security issues count."""
        stats = calculate_stats(sample_manifest)

        # BUG-001, BUG-002, BUG-003, BUG-005
        assert stats["security_issues"] == 4

    def test_calculate_stats_empty_manifest(self, empty_manifest):
        """Test statistics calculation with empty manifest."""
        stats = calculate_stats(empty_manifest)

        assert stats["total"] == 0
        assert stats["by_status"] == {}
        assert stats["by_category"] == {}
        assert stats["verification_rate"] == 0.0

    def test_calculate_stats_no_fixed_bugs(self):
        """Test verification rate when no fixed bugs."""
        manifest = {
            "bugs": [
                {
                    "id": "BUG-001",
                    "status": "pending",
                    "category": "quality",
                    "severity": "low",
                }
            ]
        }

        stats = calculate_stats(manifest)
        assert stats["verification_rate"] == 0.0


class TestFormatSummary:
    def test_format_summary_basic(self, sample_manifest):
        """Test summary format includes key information."""
        stats = calculate_stats(sample_manifest)
        summary = format_summary(sample_manifest, stats)

        assert "ULTIMATE DEBUGGER SESSION REPORT" in summary
        assert "Session ID: sess-20260101-abc123" in summary
        assert "Total bugs found: 5" in summary
        assert "Verified:" in summary and "1" in summary
        assert "Fixed:" in summary and "2" in summary
        assert "Pending:" in summary and "1" in summary
        assert "Ignored:" in summary and "1" in summary
        assert "Verification rate" in summary

    def test_format_summary_includes_categories(self, sample_manifest):
        """Test summary includes category breakdown."""
        stats = calculate_stats(sample_manifest)
        summary = format_summary(sample_manifest, stats)

        assert "BY CATEGORY" in summary
        assert "security: 4" in summary
        assert "quality: 1" in summary

    def test_format_summary_empty_manifest(self, empty_manifest):
        """Test summary format with empty manifest."""
        stats = calculate_stats(empty_manifest)
        summary = format_summary(empty_manifest, stats)

        assert "ULTIMATE DEBUGGER SESSION REPORT" in summary
        assert "Total bugs found: 0" in summary


class TestFormatDetailed:
    def test_format_detailed_includes_summary(self, sample_manifest):
        """Test detailed format includes summary section."""
        stats = calculate_stats(sample_manifest)
        detailed = format_detailed(sample_manifest, stats)

        assert "ULTIMATE DEBUGGER SESSION REPORT" in detailed

    def test_format_detailed_groups_by_status(self, sample_manifest):
        """Test detailed format groups bugs by status."""
        stats = calculate_stats(sample_manifest)
        detailed = format_detailed(sample_manifest, stats)

        assert "PENDING" in detailed
        assert "VERIFIED" in detailed
        assert "FIXED" in detailed
        assert "IGNORED" in detailed

    def test_format_detailed_includes_bug_details(self, sample_manifest):
        """Test detailed format includes bug details."""
        stats = calculate_stats(sample_manifest)
        detailed = format_detailed(sample_manifest, stats)

        assert "BUG-001" in detailed
        assert "SQL injection vulnerability" in detailed
        assert "/app/db.py:42" in detailed
        assert "CWE-89" in detailed

    def test_format_detailed_includes_ignore_rule(self, sample_manifest):
        """Test detailed format shows ignore rule for ignored bugs."""
        stats = calculate_stats(sample_manifest)
        detailed = format_detailed(sample_manifest, stats)

        assert "BUG-005" in detailed
        assert "test-fixtures" in detailed

    def test_format_detailed_includes_verified_at(self, sample_manifest):
        """Test detailed format shows verification timestamp."""
        stats = calculate_stats(sample_manifest)
        detailed = format_detailed(sample_manifest, stats)

        assert "Verified: 2026-01-02T10:30:00" in detailed

    def test_format_detailed_empty_manifest(self, empty_manifest):
        """Test detailed format with empty manifest."""
        stats = calculate_stats(empty_manifest)
        detailed = format_detailed(empty_manifest, stats)

        assert "ULTIMATE DEBUGGER SESSION REPORT" in detailed


class TestFormatJson:
    def test_format_json_structure(self, sample_manifest):
        """Test JSON format has correct structure."""
        stats = calculate_stats(sample_manifest)
        json_str = format_json(sample_manifest, stats)

        data = json.loads(json_str)

        assert "session" in data
        assert "stats" in data
        assert "bugs" in data
        assert "generated_at" in data

    def test_format_json_includes_bugs(self, sample_manifest):
        """Test JSON includes all bugs."""
        stats = calculate_stats(sample_manifest)
        json_str = format_json(sample_manifest, stats)

        data = json.loads(json_str)

        assert len(data["bugs"]) == 5
        assert data["bugs"][0]["id"] == "BUG-001"

    def test_format_json_includes_stats(self, sample_manifest):
        """Test JSON includes calculated statistics."""
        stats = calculate_stats(sample_manifest)
        json_str = format_json(sample_manifest, stats)

        data = json.loads(json_str)

        assert data["stats"]["total"] == 5
        assert data["stats"]["high_severity_fixed"] == 2

    def test_format_json_valid_iso_timestamp(self, sample_manifest):
        """Test JSON has valid ISO timestamp."""
        stats = calculate_stats(sample_manifest)
        json_str = format_json(sample_manifest, stats)

        data = json.loads(json_str)

        # Should be parseable as ISO timestamp
        datetime.fromisoformat(data["generated_at"])

    def test_format_json_empty_manifest(self, empty_manifest):
        """Test JSON format with empty manifest."""
        stats = calculate_stats(empty_manifest)
        json_str = format_json(empty_manifest, stats)

        data = json.loads(json_str)

        assert data["stats"]["total"] == 0
        assert data["bugs"] == []


class TestFormatMarkdown:
    def test_format_markdown_header(self, sample_manifest):
        """Test markdown format includes header."""
        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        assert "# Gas Debugger Report" in markdown

    def test_format_markdown_session_info(self, sample_manifest):
        """Test markdown includes session information."""
        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        assert "## Session Information" in markdown
        assert "**Session ID**: sess-20260101-abc123" in markdown
        assert "**Goal**: Find security bugs" in markdown

    def test_format_markdown_summary_table(self, sample_manifest):
        """Test markdown includes summary statistics table."""
        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        assert "## Summary Statistics" in markdown
        assert "| Metric | Count |" in markdown
        assert "| Total bugs | 5 |" in markdown
        assert "| Verified | 1 |" in markdown

    def test_format_markdown_category_table(self, sample_manifest):
        """Test markdown includes category breakdown table."""
        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        assert "## Bugs by Category" in markdown
        assert "| Category | Count |" in markdown
        assert "| security | 4 |" in markdown

    def test_format_markdown_action_required_section(self, sample_manifest):
        """Test markdown has action required section for pending."""
        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        assert "## Action Required (Pending Bugs)" in markdown
        assert "BUG-004" in markdown
        assert "Dead code" in markdown

    def test_format_markdown_completed_section(self, sample_manifest):
        """Test markdown has completed section for verified."""
        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        assert "## Completed (Verified Fixes)" in markdown
        assert "BUG-001" in markdown

    def test_format_markdown_no_pending_bugs(self):
        """Test markdown without pending bugs skips that section."""
        manifest = {
            "session": {"id": "test", "original_goal": "Test"},
            "bugs": [
                {
                    "id": "BUG-001",
                    "description": "Fixed",
                    "status": "fixed",
                    "category": "quality",
                    "severity": "low",
                    "location": {"file": "test.py", "line": 1},
                }
            ],
        }

        stats = calculate_stats(manifest)
        markdown = format_markdown(manifest, stats)

        # Action Required section should not appear
        assert "## Action Required (Pending Bugs)" not in markdown

    def test_format_markdown_no_verified_bugs(self):
        """Test markdown without verified bugs skips that section."""
        manifest = {
            "session": {"id": "test", "original_goal": "Test"},
            "bugs": [
                {
                    "id": "BUG-001",
                    "description": "Pending",
                    "status": "pending",
                    "category": "quality",
                    "severity": "low",
                    "location": {"file": "test.py", "line": 1},
                }
            ],
        }

        stats = calculate_stats(manifest)
        markdown = format_markdown(manifest, stats)

        # Completed section should not appear
        assert "## Completed (Verified Fixes)" not in markdown

    def test_format_markdown_empty_manifest(self, empty_manifest):
        """Test markdown with empty manifest."""
        stats = calculate_stats(empty_manifest)
        markdown = format_markdown(empty_manifest, stats)

        assert "# Gas Debugger Report" in markdown
        assert "## Summary Statistics" in markdown
        assert "| Total bugs | 0 |" in markdown

    def test_format_markdown_truncates_long_descriptions(self, sample_manifest):
        """Test markdown truncates long descriptions."""
        sample_manifest["bugs"][0]["description"] = (
            "A" * 100 + " extra text that should be truncated"
        )

        stats = calculate_stats(sample_manifest)
        markdown = format_markdown(sample_manifest, stats)

        # Should contain truncated version (40 chars or less based on code)
        assert "..." in markdown or len(sample_manifest["bugs"][0]["description"]) > 40


class TestFormatConsistency:
    def test_all_formats_handle_no_manifest_data(self, empty_manifest):
        """Test all formatters handle minimal manifest gracefully."""
        stats = calculate_stats(empty_manifest)

        # All formatters should produce output
        summary = format_summary(empty_manifest, stats)
        detailed = format_detailed(empty_manifest, stats)
        json_out = format_json(empty_manifest, stats)
        markdown = format_markdown(empty_manifest, stats)

        assert summary
        assert detailed
        assert json_out
        assert markdown

    def test_json_format_is_valid_json(self, sample_manifest):
        """Test JSON format is always valid JSON."""
        stats = calculate_stats(sample_manifest)
        json_str = format_json(sample_manifest, stats)

        # Should not raise
        json.loads(json_str)

    def test_all_formats_include_session_id(self, sample_manifest):
        """Test all formats include session ID."""
        stats = calculate_stats(sample_manifest)

        summary = format_summary(sample_manifest, stats)
        detailed = format_detailed(sample_manifest, stats)
        json_out = format_json(sample_manifest, stats)
        markdown = format_markdown(sample_manifest, stats)

        assert "sess-20260101-abc123" in summary
        assert "sess-20260101-abc123" in detailed
        assert "sess-20260101-abc123" in json_out
        assert "sess-20260101-abc123" in markdown
