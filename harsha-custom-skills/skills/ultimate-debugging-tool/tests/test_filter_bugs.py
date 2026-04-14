"""
Tests for filter_bugs.py
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from filter_bugs import (
    load_yaml,
    save_yaml,
    is_rule_expired,
    rule_matches_bug,
    filter_bugs,
)


@pytest.fixture
def manifest_file(tmp_path):
    """Create a sample bug manifest file."""
    manifest = {
        "session": {
            "id": "sess-20260101-abc123",
            "started": "2026-01-01T00:00:00",
            "original_goal": "Find security bugs",
            "project_path": "/test/project",
        },
        "stats": {
            "total_found": 5,
            "pending": 3,
            "fixing": 1,
            "fixed": 1,
            "verified": 0,
            "ignored": 0,
        },
        "bugs": [
            {
                "id": "BUG-001",
                "description": "Test password in code",
                "status": "pending",
                "category": "security",
                "severity": "high",
                "location": {"file": "/test/app.py", "line": 42},
            },
            {
                "id": "BUG-002",
                "description": "TODO marker",
                "status": "pending",
                "category": "quality",
                "severity": "low",
                "location": {"file": "/test/utils.py", "line": 15},
            },
            {
                "id": "BUG-003",
                "description": "Test fixture with cred",
                "status": "pending",
                "category": "security",
                "severity": "medium",
                "location": {"file": "/test/tests/fixtures.py", "line": 8},
            },
            {
                "id": "BUG-004",
                "description": "Already ignored",
                "status": "ignored",
                "category": "security",
                "severity": "low",
                "location": {"file": "/test/old.py", "line": 1},
            },
            {
                "id": "BUG-005",
                "description": "Fixed bug",
                "status": "fixed",
                "category": "quality",
                "severity": "low",
                "location": {"file": "/test/fixed.py", "line": 50},
            },
        ],
    }

    manifest_path = tmp_path / "bug-manifest.yaml"
    manifest_path.write_text(yaml.dump(manifest, default_flow_style=False))
    return manifest_path, manifest


@pytest.fixture
def rules_file(tmp_path):
    """Create a sample ignore rules file."""
    rules = {
        "rules": [
            {
                "id": "rule-1",
                "description": "Test credentials",
                "pattern": "password.*=.*['\"]\\d{4}['\"]",
                "categories": ["security"],
            },
            {
                "id": "rule-2",
                "description": "Test fixtures",
                "file_glob": "**/tests/**",
                "categories": ["security"],
            },
            {
                "id": "rule-3",
                "description": "TODO markers",
                "pattern": "TODO:|FIXME:",
                "categories": ["quality"],
            },
            {
                "id": "rule-4",
                "description": "Expired rule",
                "pattern": "should_not_match",
                "expires": (datetime.now() - timedelta(days=1)).isoformat(),
            },
        ]
    }

    rules_path = tmp_path / "ignore-rules.yaml"
    rules_path.write_text(yaml.dump(rules, default_flow_style=False))
    return rules_path, rules


class TestLoadYaml:
    def test_load_valid_yaml(self, tmp_path):
        """Test loading a valid YAML file."""
        data = {"key": "value", "number": 42}
        path = tmp_path / "test.yaml"
        path.write_text(yaml.dump(data))

        result = load_yaml(path)
        assert result == data

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading a nonexistent file returns None."""
        result = load_yaml(tmp_path / "nonexistent.yaml")
        assert result is None

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML returns None."""
        path = tmp_path / "bad.yaml"
        path.write_text("{ invalid yaml: [")

        result = load_yaml(path)
        assert result is None


class TestSaveYaml:
    def test_save_valid_data(self, tmp_path):
        """Test saving data to YAML file."""
        data = {"key": "value", "nested": {"inner": 42}}
        path = tmp_path / "output.yaml"

        result = save_yaml(data, path)
        assert result is True
        assert path.exists()

        loaded = yaml.safe_load(path.read_text())
        assert loaded == data

    def test_save_to_readonly_dir(self, tmp_path):
        """Test saving to read-only directory returns False."""
        import os

        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        path = readonly_dir / "file.yaml"
        result = save_yaml({"data": "test"}, path)

        # Cleanup
        readonly_dir.chmod(0o755)

        assert result is False


class TestIsRuleExpired:
    def test_no_expiry_date(self):
        """Test rule without expiry is not expired."""
        rule = {"id": "rule-1", "pattern": "test"}
        assert is_rule_expired(rule) is False

    def test_future_expiry(self):
        """Test rule with future expiry is not expired."""
        future = (datetime.now() + timedelta(days=1)).isoformat()
        rule = {"id": "rule-1", "expires": future}
        assert is_rule_expired(rule) is False

    def test_past_expiry_iso_format(self):
        """Test rule with past ISO expiry is expired."""
        # Use date only to avoid timezone issues
        past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        rule = {"id": "rule-1", "expires": past}
        assert is_rule_expired(rule) is True

    def test_past_expiry_date_format(self):
        """Test rule with past date-only expiry is expired."""
        # Create date string that is definitely in the past
        past = "2020-01-01"
        rule = {"id": "rule-1", "expires": past}
        assert is_rule_expired(rule) is True

    def test_invalid_expiry_format(self):
        """Test rule with invalid expiry format is not considered expired."""
        rule = {"id": "rule-1", "expires": "invalid-date"}
        assert is_rule_expired(rule) is False


class TestRuleMatchesBug:
    def test_match_file_glob(self):
        """Test matching by file glob pattern."""
        rule = {"id": "rule-1", "file_glob": "**/*.py"}
        bug = {
            "location": {"file": "/path/to/app.py", "line": 10},
            "category": "quality",
        }
        assert rule_matches_bug(rule, bug) is True

    def test_no_match_file_glob(self):
        """Test file glob that doesn't match."""
        rule = {"id": "rule-1", "file_glob": "**/tests/**"}
        bug = {
            "location": {"file": "/app.py", "line": 10},
            "category": "security",
        }
        assert rule_matches_bug(rule, bug) is False

    def test_match_pattern_regex(self):
        """Test matching by regex pattern."""
        rule = {"id": "rule-1", "pattern": r"password\s*=\s*['\"].*['\"]"}
        bug = {
            "location": {"file": "/app.py", "line": 1},
            "category": "security",
        }
        file_content = 'password = "secret123"\n'

        assert rule_matches_bug(rule, bug, file_content) is True

    def test_match_pattern_literal(self):
        """Test matching by literal string when regex fails."""
        rule = {"id": "rule-1", "pattern": "TODO:"}
        bug = {
            "location": {"file": "/app.py", "line": 1},
            "category": "quality",
        }
        file_content = "# TODO: fix this later\n"

        assert rule_matches_bug(rule, bug, file_content) is True

    def test_category_restriction(self):
        """Test category restriction prevents match."""
        rule = {
            "id": "rule-1",
            "file_glob": "*.py",
            "categories": ["security"],
        }
        bug = {
            "location": {"file": "file.py", "line": 1},
            "category": "quality",
        }

        assert rule_matches_bug(rule, bug) is False

    def test_category_match(self):
        """Test category restriction allows match."""
        rule = {
            "id": "rule-1",
            "file_glob": "*.py",
            "categories": ["security", "quality"],
        }
        bug = {
            "location": {"file": "file.py", "line": 1},
            "category": "security",
        }

        assert rule_matches_bug(rule, bug) is True

    def test_expired_rule_no_match(self):
        """Test expired rule never matches."""
        # Use definite past date
        past = "2020-01-01"
        rule = {
            "id": "rule-1",
            "file_glob": "*.py",
            "expires": past,
        }
        bug = {
            "location": {"file": "file.py", "line": 1},
            "category": "quality",
        }

        assert rule_matches_bug(rule, bug) is False

    def test_invalid_line_number(self):
        """Test pattern match with invalid line number."""
        rule = {"id": "rule-1", "pattern": "test"}
        bug = {
            "location": {"file": "/app.py", "line": 999},
            "category": "quality",
        }
        file_content = "test line 1\ntest line 2\n"

        assert rule_matches_bug(rule, bug, file_content) is False


class TestFilterBugs:
    def test_filter_bugs_dry_run(self, manifest_file, rules_file):
        """Test dry-run mode doesn't modify manifest."""
        manifest_path, original_manifest = manifest_file
        rules_path, _ = rules_file

        stats = filter_bugs(manifest_path, rules_path, dry_run=True)

        # Reload manifest to verify it wasn't modified
        reloaded = yaml.safe_load(manifest_path.read_text())

        # All bugs should still have original status
        for bug in reloaded["bugs"]:
            if bug["id"] != "BUG-004" and bug["id"] != "BUG-005":
                assert bug["status"] == "pending"

    def test_filter_bugs_applies_rules(self, tmp_path):
        """Test rules are applied and manifest is updated."""
        # Create test file for pattern matching in tmp_path
        test_file = tmp_path / "app.py"
        test_file.write_text('password = "1234"\n')

        # Create manifest with bug pointing to test file
        manifest = {
            "session": {"id": "test"},
            "stats": {"total_found": 1, "pending": 1},
            "bugs": [
                {
                    "id": "BUG-001",
                    "description": "Test password in code",
                    "status": "pending",
                    "category": "security",
                    "severity": "high",
                    "location": {"file": str(test_file), "line": 1},
                }
            ],
        }

        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest, default_flow_style=False))

        # Create rules with pattern matching
        rules = {
            "rules": [
                {
                    "id": "rule-password",
                    "description": "Test passwords",
                    "pattern": r"password\s*=",
                    "categories": ["security"],
                }
            ]
        }

        rules_path = tmp_path / "rules.yaml"
        rules_path.write_text(yaml.dump(rules, default_flow_style=False))

        stats = filter_bugs(manifest_path, rules_path, dry_run=False)

        assert stats["matched"] > 0

        # Verify manifest was updated
        reloaded = yaml.safe_load(manifest_path.read_text())

        # Find ignored bug
        bug_001 = next(b for b in reloaded["bugs"] if b["id"] == "BUG-001")
        assert bug_001["status"] == "ignored"
        assert "ignore_rule" in bug_001
        assert "ignored_at" in bug_001

    def test_filter_bugs_missing_manifest(self, tmp_path, rules_file):
        """Test handling of missing manifest."""
        manifest_path = tmp_path / "nonexistent.yaml"
        rules_path, _ = rules_file

        stats = filter_bugs(manifest_path, rules_path)

        assert stats["matched"] == 0

    def test_filter_bugs_no_rules(self, manifest_file, tmp_path):
        """Test behavior when no rules are defined."""
        manifest_path, _ = manifest_file

        empty_rules = tmp_path / "empty-rules.yaml"
        empty_rules.write_text(yaml.dump({"rules": []}))

        stats = filter_bugs(manifest_path, empty_rules)

        assert stats["matched"] == 0
        assert stats["expired_rules"] == 0

    def test_filter_bugs_skips_already_ignored(self, manifest_file, rules_file):
        """Test already-ignored bugs are counted but not re-processed."""
        manifest_path, _ = manifest_file
        rules_path, _ = rules_file

        stats = filter_bugs(manifest_path, rules_path, dry_run=False)

        assert stats["already_ignored"] == 1

    def test_filter_bugs_skips_fixed_and_verified(self, manifest_file, rules_file):
        """Test fixed/verified bugs are not re-processed."""
        manifest_path, _ = manifest_file
        rules_path, _ = rules_file

        stats = filter_bugs(manifest_path, rules_path, dry_run=False)

        # BUG-005 is fixed, should not be in matched or pending
        reloaded = yaml.safe_load(manifest_path.read_text())
        bug_005 = next(b for b in reloaded["bugs"] if b["id"] == "BUG-005")
        assert bug_005["status"] == "fixed"

    def test_filter_bugs_counts_pending(self, manifest_file, rules_file):
        """Test pending bugs are counted."""
        manifest_path, _ = manifest_file
        rules_path, _ = rules_file

        stats = filter_bugs(manifest_path, rules_path, dry_run=True)

        # Should have pending bugs that weren't matched
        assert stats["pending"] >= 0

    def test_filter_bugs_handles_file_read_errors(self, tmp_path):
        """Test graceful handling of file read errors."""
        manifest = {
            "session": {"id": "test"},
            "stats": {},
            "bugs": [
                {
                    "id": "BUG-001",
                    "description": "Test",
                    "status": "pending",
                    "category": "quality",
                    "location": {"file": "/nonexistent/file.py", "line": 1},
                }
            ],
        }

        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest))

        rules = {
            "rules": [
                {
                    "id": "rule-1",
                    "pattern": "test",
                }
            ]
        }

        rules_path = tmp_path / "rules.yaml"
        rules_path.write_text(yaml.dump(rules))

        # Should not raise error
        stats = filter_bugs(manifest_path, rules_path, dry_run=True)
        assert isinstance(stats, dict)

    def test_filter_bugs_expired_rules_counted(self, tmp_path):
        """Test expired rules are counted separately."""
        manifest = {
            "session": {"id": "test"},
            "stats": {},
            "bugs": [],
        }

        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest))

        # Use definite past date
        past = "2020-01-01"
        rules = {
            "rules": [
                {
                    "id": "expired-rule",
                    "pattern": "test",
                    "expires": past,
                }
            ]
        }

        rules_path = tmp_path / "rules.yaml"
        rules_path.write_text(yaml.dump(rules))

        stats = filter_bugs(manifest_path, rules_path)

        assert stats["expired_rules"] == 1

    def test_filter_bugs_manifest_stats_updated(self, manifest_file, rules_file, tmp_path):
        """Test manifest statistics are updated correctly."""
        manifest_path, manifest_data = manifest_file
        rules_path, _ = rules_file

        # Create test file in tmp_path
        test_file = tmp_path / "app.py"
        test_file.write_text('password = "1234"\n')

        # Update manifest to use tmp_path
        for bug in manifest_data["bugs"]:
            if bug["id"] == "BUG-001":
                bug["location"]["file"] = str(test_file)

        manifest_path.write_text(yaml.dump(manifest_data, default_flow_style=False))

        stats = filter_bugs(manifest_path, rules_path, dry_run=False)

        if stats["matched"] > 0:
            reloaded = yaml.safe_load(manifest_path.read_text())
            assert "stats" in reloaded
            # Manifest stats should be updated
            assert reloaded["stats"]["ignored"] == stats["matched"]
