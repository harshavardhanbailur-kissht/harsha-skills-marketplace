"""
Shared test fixtures for Ultimate Debugger test suite.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_project(tmp_path):
    """
    Create a temporary project directory with package.json and sample source files.
    """
    # Create package.json
    package_json = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
        },
        "devDependencies": {
            "typescript": "^6.0.0",
            "vitest": "^2.0.0",
        },
    }

    pkg_path = tmp_path / "package.json"
    pkg_path.write_text(json.dumps(package_json, indent=2))

    # Create sample source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "index.ts").write_text("export const version = '1.0.0';")
    (src_dir / "utils.ts").write_text("""
export function add(a: number, b: number): number {
  return a + b;
}
""")

    # Create a test directory
    test_dir = tmp_path / "__tests__"
    test_dir.mkdir()
    (test_dir / "utils.test.ts").write_text("""
import { add } from '../src/utils';
describe('utils', () => {
  it('adds numbers', () => {
    expect(add(1, 2)).toBe(3);
  });
});
""")

    # Create node_modules (should be excluded from scanning)
    nm_dir = tmp_path / "node_modules"
    nm_dir.mkdir()
    (nm_dir / "react").mkdir()
    (nm_dir / "react" / "package.json").write_text("{}")

    return tmp_path


@pytest.fixture
def load_fixture(fixtures_dir):
    """
    Load a fixture file by name.

    Usage: load_fixture('sample_package_react.json')
    """
    def _load(filename: str):
        path = fixtures_dir / filename
        with open(path, 'r') as f:
            if filename.endswith('.json'):
                return json.load(f)
            else:
                return f.read()
    return _load


@pytest.fixture
def sample_package_react(load_fixture):
    """Load sample React package.json fixture."""
    return load_fixture('sample_package_react.json')


@pytest.fixture
def sample_package_3d(load_fixture):
    """Load sample 3D package.json fixture."""
    return load_fixture('sample_package_3d.json')


@pytest.fixture
def sample_package_dashboard(load_fixture):
    """Load sample dashboard package.json fixture."""
    return load_fixture('sample_package_dashboard.json')


@pytest.fixture
def sample_package_empty(load_fixture):
    """Load sample empty package.json fixture."""
    return load_fixture('sample_package_empty.json')


@pytest.fixture
def sample_diff_simple(load_fixture):
    """Load simple unified diff fixture."""
    return load_fixture('sample_diff_simple.patch')


@pytest.fixture
def sample_diff_multifile(load_fixture):
    """Load multi-file unified diff fixture."""
    return load_fixture('sample_diff_multifile.patch')


@pytest.fixture
def sample_diff_api_change(load_fixture):
    """Load API change unified diff fixture (exports)."""
    return load_fixture('sample_diff_api_change.patch')


@pytest.fixture
def sample_diff_structural(load_fixture):
    """Load structural change unified diff fixture."""
    return load_fixture('sample_diff_structural.patch')
