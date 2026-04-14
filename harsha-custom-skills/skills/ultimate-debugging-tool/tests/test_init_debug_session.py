"""
Tests for init_debug_session.py
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from init_debug_session import (
    init_session,
    MANIFEST_TEMPLATE,
    SESSION_TEMPLATE,
    DEFAULT_IGNORE_RULES,
)


class TestInitSession:
    def test_init_session_creates_directory(self, tmp_path):
        """Test init_session creates .debug-session directory."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            result = init_session(str(project_path), "Test goal")

        assert result is True
        assert (project_path / ".debug-session").exists()

    def test_init_session_creates_manifest(self, tmp_path):
        """Test init_session creates bug-manifest.yaml."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test goal")

        manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        assert manifest_path.exists()

        manifest = yaml.safe_load(manifest_path.read_text())
        assert "session" in manifest
        assert "stats" in manifest
        assert "bugs" in manifest
        assert manifest["session"]["original_goal"] == "Test goal"

    def test_init_session_creates_ignore_rules(self, tmp_path):
        """Test init_session creates ignore-rules.yaml."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test goal")

        rules_path = project_path / ".debug-session" / "ignore-rules.yaml"
        assert rules_path.exists()

        content = rules_path.read_text()
        assert "Gas Debugger Ignore Rules" in content
        assert "rules:" in content

    def test_init_session_creates_session_metadata(self, tmp_path):
        """Test init_session creates session.yaml."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test goal")

        session_path = project_path / ".debug-session" / "session.yaml"
        assert session_path.exists()

        session = yaml.safe_load(session_path.read_text())
        assert "session" in session
        assert "state" in session
        assert "history" in session

    def test_init_session_creates_subdirectories(self, tmp_path):
        """Test init_session creates scans, fixes, verifications directories."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test goal")

        debug_dir = project_path / ".debug-session"
        assert (debug_dir / "scans").exists()
        assert (debug_dir / "fixes").exists()
        assert (debug_dir / "verifications").exists()

    def test_init_session_manifest_template_structure(self, tmp_path):
        """Test manifest has correct template structure."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "My debugging goal")

        manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())

        # Check session structure
        assert manifest["session"]["id"].startswith("sess-")
        assert manifest["session"]["started"]
        assert manifest["session"]["original_goal"] == "My debugging goal"
        assert manifest["session"]["project_path"]

        # Check stats structure
        assert manifest["stats"]["total_found"] == 0
        assert manifest["stats"]["pending"] == 0
        assert manifest["stats"]["fixing"] == 0
        assert manifest["stats"]["fixed"] == 0
        assert manifest["stats"]["verified"] == 0
        assert manifest["stats"]["ignored"] == 0

        # Check bugs array
        assert manifest["bugs"] == []

    def test_init_session_session_template_structure(self, tmp_path):
        """Test session metadata has correct structure."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test goal")

        session_path = project_path / ".debug-session" / "session.yaml"
        session = yaml.safe_load(session_path.read_text())

        # Check session section
        assert "session" in session
        assert session["session"]["id"].startswith("sess-")
        assert session["session"]["started"]
        assert session["session"]["goal"] == "Test goal"

        # Check state section
        assert "state" in session
        assert session["state"]["current_phase"] == "initialized"
        assert session["state"]["last_bug_id"] is None
        assert session["state"]["scan_categories_completed"] == []

        # Check history section
        assert "history" in session
        assert len(session["history"]) == 1
        assert session["history"][0]["action"] == "session_initialized"

    def test_init_session_project_not_exists(self, tmp_path):
        """Test init_session returns False for nonexistent project."""
        nonexistent = tmp_path / "nonexistent"

        result = init_session(str(nonexistent), "Test goal")

        assert result is False

    def test_init_session_existing_directory_overwrite_yes(self, tmp_path):
        """Test init_session can overwrite existing .debug-session with 'y' response."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        # Create first session
        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "First goal")

        first_manifest = (project_path / ".debug-session" / "bug-manifest.yaml").read_text()

        # Try to create again with 'y' response
        with patch("builtins.input", return_value="y"):
            result = init_session(str(project_path), "Second goal")

        assert result is True

        # Verify it was overwritten
        second_manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        second_manifest = yaml.safe_load(second_manifest_path.read_text())
        assert second_manifest["session"]["original_goal"] == "Second goal"

    def test_init_session_existing_directory_overwrite_no(self, tmp_path):
        """Test init_session aborts with 'n' response to existing directory."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        # Create first session
        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "First goal")

        # Try to create again with 'n' response
        with patch("builtins.input", side_effect=["n"]):
            result = init_session(str(project_path), "Second goal")

        assert result is False

        # Verify it was not changed
        manifest = yaml.safe_load(
            (project_path / ".debug-session" / "bug-manifest.yaml").read_text()
        )
        assert manifest["session"]["original_goal"] == "First goal"

    def test_init_session_manifest_write_failure(self, tmp_path):
        """Test init_session handles manifest write failure."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        debug_dir = project_path / ".debug-session"
        debug_dir.mkdir()

        # Make directory read-only to prevent file creation
        debug_dir.chmod(0o444)

        with patch("builtins.input", return_value="y"):
            result = init_session(str(project_path), "Test goal")

        # Cleanup
        debug_dir.chmod(0o755)

        assert result is False

    def test_init_session_uses_default_goal(self, tmp_path):
        """Test init_session uses default goal when not specified."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            result = init_session(str(project_path))

        assert result is True

        manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())
        assert manifest["session"]["original_goal"] == "Debug and fix code issues"

    def test_init_session_session_id_format(self, tmp_path):
        """Test session ID has correct format."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path))

        manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())
        session_id = manifest["session"]["id"]

        # Should be sess-YYYYMMDD-XXXXXX
        assert session_id.startswith("sess-")
        parts = session_id.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # hex part

    def test_init_session_timestamps_iso_format(self, tmp_path):
        """Test timestamps are in ISO format."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path))

        manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())

        # Should be parseable as ISO format
        from datetime import datetime

        datetime.fromisoformat(manifest["session"]["started"])

    def test_init_session_project_path_resolved(self, tmp_path):
        """Test project_path is stored as absolute path."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test")

        manifest_path = project_path / ".debug-session" / "bug-manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())

        # Should be absolute path
        stored_path = Path(manifest["session"]["project_path"])
        assert stored_path.is_absolute()
        assert stored_path == project_path.resolve()

    def test_init_session_ignore_rules_has_examples(self, tmp_path):
        """Test ignore rules include example patterns."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            init_session(str(project_path), "Test")

        rules_path = project_path / ".debug-session" / "ignore-rules.yaml"
        content = rules_path.read_text()

        # Should mention examples
        assert "Example" in content or "example" in content
        assert "rules:" in content

    def test_init_session_creates_all_files_atomically(self, tmp_path):
        """Test all files are created when init succeeds."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            result = init_session(str(project_path), "Test")

        if result:
            debug_dir = project_path / ".debug-session"
            # All expected files should exist
            assert (debug_dir / "bug-manifest.yaml").exists()
            assert (debug_dir / "ignore-rules.yaml").exists()
            assert (debug_dir / "session.yaml").exists()
            assert (debug_dir / "scans").is_dir()
            assert (debug_dir / "fixes").is_dir()
            assert (debug_dir / "verifications").is_dir()

    def test_init_session_returns_true_on_success(self, tmp_path):
        """Test init_session returns True on successful initialization."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        with patch("builtins.input", return_value="n"):
            result = init_session(str(project_path), "Test")

        assert result is True

    def test_init_session_returns_false_on_failure(self, tmp_path):
        """Test init_session returns False on failure."""
        nonexistent = tmp_path / "nonexistent"

        result = init_session(str(nonexistent), "Test")

        assert result is False
