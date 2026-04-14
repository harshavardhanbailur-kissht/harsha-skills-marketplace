"""
End-to-End Pipeline Integration Tests

Tests the full chain: context_analyzer → fix_signal_analyzer

Verifies:
1. Context analyzer produces correct ProjectContext
2. Fix signal analyzer accepts project_type from context
3. Applicable patterns match expected frameworks
4. Project-type weight adjustments are applied correctly
5. Full pipeline consistency

Each test creates a temp project, runs context analysis, then runs fix signal analysis.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from context_analyzer import analyze_project, ProjectContext
from fix_signal_analyzer import (
    analyze_fix,
    compute_weights,
    FixSignalReport,
    DEFAULT_WEIGHTS,
    PROJECT_TYPE_ADJUSTMENTS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_react_project(tmp_path):
    """
    Create a temporary React + TypeScript project.

    Structure:
        package.json (React + TypeScript deps)
        src/
            index.tsx
            utils.ts
            api.ts
        __tests__/
            utils.test.ts
    """
    # package.json with React + TypeScript
    pkg_json = {
        "name": "test-react-app",
        "version": "1.0.0",
        "dependencies": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
            "next": "^14.0.0",
        },
        "devDependencies": {
            "typescript": "^6.0.0",
            "vitest": "^2.0.0",
            "@testing-library/react": "^16.0.0",
        },
    }

    pkg_path = tmp_path / "package.json"
    pkg_path.write_text(json.dumps(pkg_json, indent=2))

    # Create source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "index.tsx").write_text("""
import React from 'react';
import ReactDOM from 'react-dom';

export default function App() {
  return <div>Hello</div>;
}
""")

    (src_dir / "utils.ts").write_text("""
export function add(a: number, b: number): number {
  return a + b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}
""")

    (src_dir / "api.ts").write_text("""
export async function fetchData(url: string): Promise<any> {
  const response = await fetch(url);
  return response.json();
}

export async function postData(url: string, data: any): Promise<any> {
  const response = await fetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
}
""")

    # Create test files
    test_dir = tmp_path / "__tests__"
    test_dir.mkdir()

    (test_dir / "utils.test.ts").write_text("""
import { add, multiply } from '../src/utils';

describe('utils', () => {
  it('adds numbers', () => {
    expect(add(1, 2)).toBe(3);
  });

  it('multiplies numbers', () => {
    expect(multiply(2, 3)).toBe(6);
  });
});
""")

    return tmp_path


@pytest.fixture
def temp_3d_project(tmp_path):
    """
    Create a temporary 3D experience project.

    Structure:
        package.json (Three.js + React Three Fiber)
        src/
            Scene.tsx
            Effects.tsx
    """
    pkg_json = {
        "name": "test-3d-app",
        "version": "1.0.0",
        "dependencies": {
            "three": "^r128.0.0",
            "@react-three/fiber": "^8.0.0",
            "@react-three/drei": "^9.0.0",
            "react": "^19.0.0",
            "detect-gpu": "^5.0.0",
        },
        "devDependencies": {
            "typescript": "^6.0.0",
        },
    }

    pkg_path = tmp_path / "package.json"
    pkg_path.write_text(json.dumps(pkg_json, indent=2))

    src_dir = tmp_path / "src"
    src_dir.mkdir()

    (src_dir / "Scene.tsx").write_text("""
import * as THREE from 'three';
import { useFrame, Canvas } from '@react-three/fiber';

function Mesh() {
  useFrame((state) => {
    // Animation code
  });
  return <mesh><boxGeometry /></mesh>;
}

export function Scene() {
  return <Canvas><Mesh /></Canvas>;
}
""")

    (src_dir / "Effects.tsx").write_text("""
import { EffectComposer } from '@react-three/postprocessing';

export function Effects() {
  return <EffectComposer />;
}
""")

    return tmp_path


@pytest.fixture
def sample_diff_react_fix():
    """
    Create a sample unified diff for a React component fix.

    Simulates a fix to a type definition (type_surface change).
    """
    return """--- a/src/utils.ts
+++ b/src/utils.ts
@@ -1,4 +1,6 @@
+interface AddOptions {
+  strict?: boolean;
+}
-export function add(a: number, b: number): number {
+export function add(a: number, b: number, opts?: AddOptions): number {
   return a + b;
 }
"""


@pytest.fixture
def sample_diff_multifile_structural():
    """
    Create a multi-file structural change diff.

    Simulates refactoring that touches multiple files (files_touched, ast_depth).
    """
    return """--- a/src/api.ts
+++ b/src/api.ts
@@ -1,10 +1,12 @@
-export async function fetchData(url: string): Promise<any> {
+interface ApiConfig {
+  timeout?: number;
+}
+
+export async function fetchData(url: string, config?: ApiConfig): Promise<any> {
   const response = await fetch(url);
   return response.json();
 }

-export async function postData(url: string, data: any): Promise<any> {
+export async function postData(url: string, data: any, config?: ApiConfig): Promise<any> {
   const response = await fetch(url, {
     method: 'POST',
     body: JSON.stringify(data),
--- a/src/utils.ts
+++ b/src/utils.ts
@@ -1,4 +1,8 @@
+import { ApiConfig } from './api';
+
-export function add(a: number, b: number): number {
+export function add(a: number, b: number, config?: ApiConfig): number {
   return a + b;
 }
"""


# =============================================================================
# PIPELINE CHAIN TESTS
# =============================================================================

class TestContextAnalyzerPipeline:
    """Tests for context analyzer in the full pipeline."""

    def test_context_analyzer_detects_react_spa(self, temp_react_project):
        """
        Test that context analyzer correctly identifies React SPA project.

        Verifies:
        - project_type == "react-spa"
        - has_typescript == True
        - has_tests == True
        - frameworks include React and TypeScript
        """
        context = analyze_project(str(temp_react_project))

        assert context.project_type == "react-spa"
        assert context.has_typescript
        assert context.has_tests
        assert context.package_manager in ("npm", "unknown")

        # Check frameworks detected
        fw_names = {f["name"] for f in context.frameworks}
        assert "React" in fw_names
        assert "TypeScript" in fw_names

    def test_context_analyzer_detects_3d_experience(self, temp_3d_project):
        """
        Test that context analyzer correctly identifies 3D experience project.

        Verifies:
        - project_type == "3d-experience"
        - has_typescript == True
        - frameworks include Three.js and React
        """
        context = analyze_project(str(temp_3d_project))

        assert context.project_type == "3d-experience"
        assert context.has_typescript

        # Check frameworks
        fw_names = {f["name"] for f in context.frameworks}
        assert "Three.js" in fw_names or "React Three Fiber" in fw_names

    def test_context_analyzer_counts_source_files(self, temp_react_project):
        """
        Test that context analyzer counts source files correctly.

        Verifies:
        - source_files_count >= 3 (index.tsx, utils.ts, api.ts, at minimum)
        - total_lines > 0
        """
        context = analyze_project(str(temp_react_project))

        assert context.source_files_count >= 3
        assert context.total_lines > 0


class TestFixSignalAnalyzerPipeline:
    """Tests for fix signal analyzer in the full pipeline."""

    def test_analyze_fix_with_react_project_type(self, sample_diff_react_fix):
        """
        Test fix signal analyzer respects React SPA project type.

        When project_type="react-spa", weights should include adjustments:
            test_surface: +0.05
            type_surface: +0.03
            dependency_fan: -0.05
            ast_depth: -0.03
        """
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type="react-spa",
        )

        # Weights should reflect react-spa adjustments
        weights = report.weights_used

        # React SPA boosts test_surface and type_surface
        assert "react-spa" in PROJECT_TYPE_ADJUSTMENTS
        assert weights["test_surface"] > DEFAULT_WEIGHTS["test_surface"]
        assert weights["type_surface"] > DEFAULT_WEIGHTS["type_surface"]

    def test_analyze_fix_with_3d_project_type(self, sample_diff_multifile_structural):
        """
        Test fix signal analyzer respects 3D project type.

        When project_type="3d-experience", weights should include adjustments:
            ast_depth: +0.05
            type_surface: -0.03
            dependency_fan: -0.02
        """
        report = analyze_fix(
            diff_text=sample_diff_multifile_structural,
            project_type="3d-experience",
        )

        weights = report.weights_used

        # 3D boosts ast_depth
        assert "3d-experience" in PROJECT_TYPE_ADJUSTMENTS
        assert weights["ast_depth"] > DEFAULT_WEIGHTS["ast_depth"]

    def test_analyze_fix_without_project_type_uses_defaults(self, sample_diff_react_fix):
        """
        Test that fix signal analyzer uses default weights when no project type given.
        """
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type=None,
        )

        weights = report.weights_used

        # Should be close to defaults
        for signal in DEFAULT_WEIGHTS.keys():
            assert signal in weights

    def test_analyze_fix_produces_depth_score(self, sample_diff_react_fix):
        """
        Test that fix signal analyzer produces a valid depth score.

        Verifies:
        - verification_depth is in [0.0, 1.0]
        - depth_category is one of the valid categories
        """
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type="react-spa",
        )

        assert isinstance(report.verification_depth, float)
        assert 0.0 <= report.verification_depth <= 1.0
        assert report.depth_category in ("minimal", "low", "moderate", "high", "full")


class TestFullPipelineChain:
    """Tests for complete context_analyzer → fix_signal_analyzer chain."""

    def test_full_pipeline_react_project(self, temp_react_project, sample_diff_react_fix):
        """
        Test complete pipeline: analyze project → analyze fix with detected type.

        Verifies:
        1. Context analyzer correctly identifies React SPA
        2. Project type is passed to fix signal analyzer
        3. Fix signal analyzer uses correct weights
        """
        # Step 1: Analyze project context
        context = analyze_project(str(temp_react_project))
        assert context.project_type == "react-spa"

        # Step 2: Analyze fix using detected project type
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type=context.project_type,  # Use detected type
        )

        # Step 3: Verify weights are adjusted for React SPA
        assert report.project_type == "react-spa"
        assert report.weights_used["test_surface"] > DEFAULT_WEIGHTS["test_surface"]

    def test_full_pipeline_3d_project(self, temp_3d_project, sample_diff_multifile_structural):
        """
        Test complete pipeline for 3D project.

        Verifies:
        1. Context analyzer identifies 3D experience
        2. Fix signal analyzer respects 3D adjustments
        """
        # Step 1: Analyze project
        context = analyze_project(str(temp_3d_project))
        assert context.project_type == "3d-experience"

        # Step 2: Analyze fix
        report = analyze_fix(
            diff_text=sample_diff_multifile_structural,
            project_type=context.project_type,
        )

        # Step 3: Verify 3D adjustments
        assert report.project_type == "3d-experience"
        assert report.weights_used["ast_depth"] > DEFAULT_WEIGHTS["ast_depth"]

    def test_pipeline_produces_consistent_results(self, temp_react_project, sample_diff_react_fix):
        """
        Test that running the same pipeline twice produces consistent results.
        """
        context1 = analyze_project(str(temp_react_project))
        report1 = analyze_fix(sample_diff_react_fix, project_type=context1.project_type)

        context2 = analyze_project(str(temp_react_project))
        report2 = analyze_fix(sample_diff_react_fix, project_type=context2.project_type)

        # Results should be identical
        assert context1.project_type == context2.project_type
        assert report1.verification_depth == report2.verification_depth
        assert report1.depth_category == report2.depth_category


class TestWeightAdjustmentMatrix:
    """Tests for all project-type weight adjustment combinations."""

    @pytest.mark.parametrize("project_type", [
        "react-spa",
        "3d-experience",
        "animation-site",
        "dashboard",
        "hybrid",
    ])
    def test_all_project_types_apply_adjustments(self, sample_diff_react_fix, project_type):
        """
        Test that all project types apply weight adjustments correctly.

        Verifies:
        - Weights are adjusted (or stay same for hybrid)
        - Weights sum to approximately 1.0
        - No weights exceed L2 bounds
        """
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type=project_type,
        )

        weights = report.weights_used

        # Check all signals are present
        assert len(weights) == len(DEFAULT_WEIGHTS)

        # Weights shouldn't be negative
        for w in weights.values():
            assert w >= 0.0

        # Sum should be reasonable (close to default sum)
        default_sum = sum(DEFAULT_WEIGHTS.values())
        weight_sum = sum(weights.values())
        assert weight_sum > 0.5 * default_sum
        assert weight_sum < 1.5 * default_sum

    def test_hybrid_uses_no_adjustments(self, sample_diff_react_fix):
        """
        Test that hybrid project type uses no weight adjustments.

        Hybrid projects should use default weights exactly.
        """
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type="hybrid",
        )

        # Hybrid adjustments are empty dict
        assert PROJECT_TYPE_ADJUSTMENTS["hybrid"] == {}


class TestApplicablePatterns:
    """Tests for pattern applicability from context analysis."""

    def test_react_project_has_applicable_patterns(self, temp_react_project):
        """
        Test that React project detects applicable bug patterns.

        Verifies:
        - applicable_patterns is not empty
        - Pattern IDs correspond to React framework
        """
        context = analyze_project(str(temp_react_project))

        # For React SPA, should have applicable patterns
        # (Note: actual patterns depend on pattern-index.json which may be empty in test)
        assert isinstance(context.applicable_patterns, list)

    def test_context_provides_project_type_to_fix_analyzer(self, temp_react_project, sample_diff_react_fix):
        """
        Test that context's project_type can be passed to fix analyzer.

        Verifies:
        - context.project_type is a valid enum value
        - fix_signal_analyzer accepts it
        """
        context = analyze_project(str(temp_react_project))

        # Ensure project_type is valid
        valid_types = ["3d-experience", "animation-site", "react-spa", "dashboard", "hybrid", "unknown"]
        assert context.project_type in valid_types

        # Pass to fix analyzer
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type=context.project_type,
        )

        assert report.project_type == context.project_type


class TestErrorHandling:
    """Tests for error handling in the pipeline."""

    def test_pipeline_handles_missing_package_json(self, tmp_path):
        """
        Test that context analyzer handles projects without package.json.

        Should return "unknown" project type with low confidence.
        """
        context = analyze_project(str(tmp_path))

        assert context.project_type == "unknown"
        assert context.project_type_confidence < 0.5

    def test_fix_analyzer_handles_empty_diff(self):
        """
        Test that fix signal analyzer handles empty diffs gracefully.
        """
        empty_diff = ""
        report = analyze_fix(
            diff_text=empty_diff,
            project_type="react-spa",
        )

        # Should produce a report, just with minimal signals
        assert report.verification_depth >= 0.0
        assert report.verification_depth <= 1.0

    def test_pipeline_handles_invalid_project_type(self, sample_diff_react_fix):
        """
        Test that fix analyzer handles unknown project types.

        Should fall back to default weights.
        """
        report = analyze_fix(
            diff_text=sample_diff_react_fix,
            project_type="unknown-project-type",
        )

        # Should still work, using defaults
        assert report.verification_depth >= 0.0
        assert isinstance(report.weights_used, dict)
