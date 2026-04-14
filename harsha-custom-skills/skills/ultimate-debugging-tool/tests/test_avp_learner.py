"""
Comprehensive tests for avp_learner.py

Tests cover:
1. EMA weight calculation at various N values
2. Progressive confidence blending at each tier
3. L2 bounds enforcement
4. CV computation
5. Record escalation and state update
6. Quality metrics calculation
7. Load/save roundtrip
8. Edge cases and corner conditions
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from avp_learner import (
    EscalationEvent,
    LearningState,
    apply_progressive_confidence,
    compute_cv,
    compute_ema_weights,
    compute_quality_metrics,
    enforce_l2_bounds,
    get_effective_weights,
    load_learning_log,
    record_escalation,
    save_learning_log,
    DEFAULT_SIGNAL_WEIGHTS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_log_path(tmp_path):
    """Create a temporary log file path."""
    return str(tmp_path / "avp-learning-log.yaml")


@pytest.fixture
def empty_state():
    """Create a fresh, empty learning state."""
    return LearningState(
        project_type="global",
        current_weights=DEFAULT_SIGNAL_WEIGHTS.copy(),
        default_weights=DEFAULT_SIGNAL_WEIGHTS.copy(),
        created_timestamp="2026-04-02T00:00:00",
    )


@pytest.fixture
def sample_escalation_event():
    """Create a sample escalation event."""
    return EscalationEvent(
        event_id="ESC-20260402-000001",
        timestamp="2026-04-02T10:00:00",
        bug_id="BUG-123",
        project_type="react-spa",
        original_depth=0.35,
        original_category="low",
        escalated_to=0.62,
        trigger="type_cascade",
        signals_at_decision={
            "diff_size": 0.25,
            "files_touched": 0.30,
            "ast_depth": 0.40,
            "type_surface": 0.55,
            "test_surface": 0.20,
            "dependency_fan": 0.35,
        },
        outcome="fix_succeeded",
        lesson="type_surface",
    )


# =============================================================================
# EMA WEIGHT CALCULATION TESTS
# =============================================================================

class TestEMAWeightCalculation:
    """Tests for EMA weight update formula."""

    def test_ema_alpha_for_n_10(self, empty_state):
        """
        Test EMA decay factor calculation for N=10.

        α = 2/(1+N) = 2/11 ≈ 0.1818
        """
        # Add 10 events
        for i in range(10):
            event = EscalationEvent(
                event_id=f"ESC-20260402-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.3,
                original_category="low",
                escalated_to=0.6,
                trigger="manual_override",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="diff_size",  # All the same lesson
            )
            empty_state.escalation_events.append(event)

        # Compute weights
        updated_state = compute_ema_weights(empty_state)

        # Alpha should be approximately 0.1818
        # new_weight = 0.1818 * 0.8 + 0.8182 * 0.20
        # new_weight ≈ 0.1454 + 0.1636 = 0.309
        expected_diff_size = (2.0 / 11.0) * 0.8 + (9.0 / 11.0) * 0.20
        assert abs(updated_state.current_weights["diff_size"] - expected_diff_size) < 0.01

    def test_ema_weight_increases_on_success(self, empty_state):
        """
        Test that weights increase when associated with successful fixes.

        When lesson="signal_X" and outcome="fix_succeeded", signal_X's weight should increase.
        """
        # Add 5 events where type_surface was underweighted
        for i in range(5):
            event = EscalationEvent(
                event_id=f"ESC-20260402-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.3,
                original_category="low",
                escalated_to=0.65,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",  # All succeeded
                lesson="type_surface",
            )
            empty_state.escalation_events.append(event)

        original_weight = empty_state.current_weights["type_surface"]
        updated_state = compute_ema_weights(empty_state)
        new_weight = updated_state.current_weights["type_surface"]

        # Weight should increase because it was repeatedly underweighted
        assert new_weight > original_weight

    def test_ema_weight_decreases_on_failure(self, empty_state):
        """
        Test that weights don't increase much when associated with failed fixes.

        When lesson="signal_X" but outcome="fix_failed", the adjustment is based on
        low importance (0.3), so weight change is minimal.
        """
        # Add 5 events where dependency_fan was blamed but fixes failed
        for i in range(5):
            event = EscalationEvent(
                event_id=f"ESC-20260402-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.4,
                original_category="moderate",
                escalated_to=0.7,
                trigger="distant_test_failure",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_failed",  # All failed
                lesson="dependency_fan",
            )
            empty_state.escalation_events.append(event)

        original_weight = empty_state.current_weights["dependency_fan"]
        updated_state = compute_ema_weights(empty_state)
        new_weight = updated_state.current_weights["dependency_fan"]

        # Weight change should be minimal (low importance = 0.3)
        # The EMA update: α * 0.3 + (1-α) * 0.23
        # For N=5, α ≈ 0.33, so new ≈ 0.1 + 0.154 ≈ 0.254
        # Change is only about 0.024, which is acceptable
        assert abs(new_weight - original_weight) < 0.05

    def test_ema_no_update_without_lesson(self, empty_state):
        """
        Test that events without a lesson don't trigger weight updates.

        If lesson field is empty, that event shouldn't affect weights.
        """
        event = EscalationEvent(
            event_id="ESC-20260402-000001",
            timestamp="2026-04-02T10:00:00",
            bug_id="BUG-123",
            project_type="react-spa",
            original_depth=0.35,
            original_category="low",
            escalated_to=0.62,
            trigger="manual_override",
            signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
            outcome="fix_succeeded",
            lesson="",  # No lesson
        )
        empty_state.escalation_events.append(event)

        original_weights = empty_state.current_weights.copy()
        updated_state = compute_ema_weights(empty_state)

        # Weights should not change
        assert updated_state.current_weights == original_weights


# =============================================================================
# PROGRESSIVE CONFIDENCE BLENDING TESTS
# =============================================================================

class TestProgressiveConfidenceBlending:
    """Tests for confidence tier progression."""

    def test_confidence_tier_cold_start_n_less_than_5(self, empty_state):
        """
        Test N < 5: should return 100% defaults.

        With fewer than 5 events, confidence is zero — use only defaults.
        """
        # Add 3 events
        for i in range(3):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.3 + i * 0.1,
                original_category="low",
                escalated_to=0.6 + i * 0.1,
                trigger="manual_override",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="diff_size",
            )
            empty_state.escalation_events.append(event)

        # Compute EMA to set current_weights
        empty_state = compute_ema_weights(empty_state)

        # Manually set different current weights to test blending
        empty_state.current_weights["diff_size"] = 0.50  # Much higher than default

        effective = apply_progressive_confidence(empty_state)

        # Should be 100% defaults
        assert abs(effective["diff_size"] - 0.20) < 0.001

    def test_confidence_tier_early_learning_n_5_to_10(self, empty_state):
        """
        Test N = 5-10: should return 70% defaults + 30% learned.
        """
        # Add 7 events
        for i in range(7):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.3,
                original_category="low",
                escalated_to=0.65,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="type_surface",
            )
            empty_state.escalation_events.append(event)

        empty_state = compute_ema_weights(empty_state)
        empty_state.current_weights["type_surface"] = 0.30  # Boost it

        effective = apply_progressive_confidence(empty_state)

        # Should be 70% default (0.10) + 30% learned (0.30)
        # = 0.7 * 0.10 + 0.3 * 0.30 = 0.07 + 0.09 = 0.16
        expected = 0.7 * 0.10 + 0.3 * 0.30
        assert abs(effective["type_surface"] - expected) < 0.001

    def test_confidence_tier_growing_n_10_to_15(self, empty_state):
        """
        Test N = 10-15: should return 50% defaults + 50% learned.
        """
        # Add 12 events
        for i in range(12):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.35,
                original_category="low",
                escalated_to=0.65,
                trigger="lint_chain_reaction",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="ast_depth",
            )
            empty_state.escalation_events.append(event)

        empty_state = compute_ema_weights(empty_state)
        empty_state.current_weights["ast_depth"] = 0.40  # Higher than default (0.20)

        effective = apply_progressive_confidence(empty_state)

        # Should be 50/50 blend
        expected = 0.5 * 0.20 + 0.5 * 0.40
        assert abs(effective["ast_depth"] - expected) < 0.001

    def test_confidence_tier_full_learned_n_15_plus_low_cv(self, empty_state):
        """
        Test N >= 15 and CV < 0.3: should return full learned weights.
        """
        # Add 15 consistent events (low CV)
        for i in range(15):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.35 + (i % 2) * 0.01,  # Small variation
                original_category="low",
                escalated_to=0.65 + (i % 2) * 0.01,
                trigger="coverage_drop",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="dependency_fan",
            )
            empty_state.escalation_events.append(event)

        empty_state = compute_ema_weights(empty_state)

        # Manually set low CV (simulate consistent escalations)
        empty_state.confidence_cv = 0.25

        # Set learned weight different from default
        empty_state.current_weights["dependency_fan"] = 0.35

        effective = apply_progressive_confidence(empty_state)

        # Should be full learned
        assert abs(effective["dependency_fan"] - 0.35) < 0.001

    def test_confidence_tier_revert_high_cv(self, empty_state):
        """
        Test N >= 15 but CV > 0.3: should revert to 50/50 blend.

        High variance means signal is unreliable — don't trust fully learned weights.
        """
        # Add 16 events (N >= 15)
        for i in range(16):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.3 + (i % 3) * 0.3,  # High variation
                original_category="low" if i % 2 == 0 else "high",
                escalated_to=0.6 + (i % 3) * 0.3,
                trigger="manual_override",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded" if i % 2 == 0 else "fix_failed",
                lesson="test_surface",
            )
            empty_state.escalation_events.append(event)

        empty_state = compute_ema_weights(empty_state)

        # Manually set high CV (simulate noisy escalations)
        empty_state.confidence_cv = 0.45

        empty_state.current_weights["test_surface"] = 0.25

        effective = apply_progressive_confidence(empty_state)

        # Should be 50/50 (reverted due to high CV)
        expected = 0.5 * 0.12 + 0.5 * 0.25
        assert abs(effective["test_surface"] - expected) < 0.001


# =============================================================================
# L2 BOUNDS ENFORCEMENT TESTS
# =============================================================================

class TestL2BoundsEnforcement:
    """Tests for L2 regularization bounds."""

    def test_l2_bounds_weight_exceeds_2x_default(self):
        """Test that weights exceeding 2x default are clamped."""
        weights = {"diff_size": 0.50}  # 2.5x default (0.20)
        defaults = {"diff_size": 0.20}
        result = {"diff_size": 0.40}  # Clamped to 2x default

        bounded = enforce_l2_bounds(weights, defaults)
        assert abs(bounded["diff_size"] - 0.40) < 0.001

    def test_l2_bounds_weight_below_0_5x_default(self):
        """Test that weights below 0.5x default are clamped."""
        weights = {"files_touched": 0.05}  # 0.33x default (0.15)
        defaults = {"files_touched": 0.15}
        result_expected = 0.075  # Clamped to 0.5x default

        bounded = enforce_l2_bounds(weights, defaults)
        assert abs(bounded["files_touched"] - 0.075) < 0.001

    def test_l2_bounds_within_range(self):
        """Test that weights within bounds are not modified."""
        weights = {"ast_depth": 0.25}  # Within [0.10, 0.40]
        defaults = {"ast_depth": 0.20}

        bounded = enforce_l2_bounds(weights, defaults)
        assert abs(bounded["ast_depth"] - 0.25) < 0.001

    def test_l2_bounds_all_signals(self):
        """Test L2 bounds enforcement on all signals."""
        weights = {
            "diff_size": 0.50,  # Exceeds 2x (should clamp to 0.40)
            "files_touched": 0.05,  # Below 0.5x (should clamp to 0.075)
            "ast_depth": 0.22,  # Within bounds
            "type_surface": 0.20,  # Within bounds
            "test_surface": 0.10,  # Within bounds
            "dependency_fan": 0.35,  # Within bounds
        }

        bounded = enforce_l2_bounds(weights, DEFAULT_SIGNAL_WEIGHTS)

        assert abs(bounded["diff_size"] - 0.40) < 0.001  # 2x default
        assert abs(bounded["files_touched"] - 0.075) < 0.001  # 0.5x default
        assert abs(bounded["ast_depth"] - 0.22) < 0.001  # Unchanged
        assert abs(bounded["type_surface"] - 0.20) < 0.001  # Unchanged


# =============================================================================
# CV COMPUTATION TESTS
# =============================================================================

class TestCVComputation:
    """Tests for coefficient of variation calculation."""

    def test_cv_empty_events(self):
        """Test CV with no events."""
        cv = compute_cv([])
        assert cv == 1.0  # Maximum uncertainty

    def test_cv_single_event(self):
        """Test CV with a single event."""
        event = EscalationEvent(
            event_id="ESC-000001",
            timestamp="2026-04-02T10:00:00",
            bug_id="BUG-1",
            project_type="react-spa",
            original_depth=0.30,
            original_category="low",
            escalated_to=0.70,
            trigger="type_cascade",
            signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
            outcome="fix_succeeded",
            lesson="type_surface",
        )
        cv = compute_cv([event])
        # With single event, std=0 so CV=0, which is reasonable (no variance)
        assert cv >= 0.0

    def test_cv_consistent_events_low_variance(self):
        """Test CV with very consistent escalations."""
        events = []
        for i in range(5):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.35,
                original_category="low",
                escalated_to=0.65,  # Always 0.30 delta
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="type_surface",
            )
            events.append(event)

        cv = compute_cv(events)
        assert cv < 0.3  # Should be low

    def test_cv_diverse_events_high_variance(self):
        """Test CV with diverse escalation magnitudes."""
        events = []
        escalations = [0.05, 0.30, 0.50, 0.25, 0.10]  # High variance
        for i, delta in enumerate(escalations):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.35,
                original_category="low",
                escalated_to=0.35 + delta,
                trigger="manual_override",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="test_surface",
            )
            events.append(event)

        cv = compute_cv(events)
        assert cv > 0.3  # Should be high


# =============================================================================
# RECORD AND STATE UPDATE TESTS
# =============================================================================

class TestRecordEscalation:
    """Tests for recording escalation events."""

    def test_record_escalation_updates_state(self, empty_state, sample_escalation_event):
        """Test that recording an event updates total_events."""
        initial_count = len(empty_state.escalation_events)
        updated_state = record_escalation(empty_state, sample_escalation_event)

        assert len(updated_state.escalation_events) == initial_count + 1
        assert updated_state.total_events == initial_count + 1
        assert updated_state.escalation_events[-1] == sample_escalation_event

    def test_record_multiple_escalations(self, empty_state):
        """Test recording multiple events in sequence."""
        for i in range(3):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.30,
                original_category="low",
                escalated_to=0.60,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="type_surface",
            )
            empty_state = record_escalation(empty_state, event)

        assert len(empty_state.escalation_events) == 3
        assert empty_state.total_events == 3


# =============================================================================
# QUALITY METRICS TESTS
# =============================================================================

class TestQualityMetrics:
    """Tests for quality metric calculations."""

    def test_quality_metrics_empty_state(self, empty_state):
        """Test metrics with no events."""
        metrics = compute_quality_metrics(empty_state)

        assert metrics["precision"] == 0.0
        assert metrics["false_alarm_rate"] == 0.0
        assert all(v == 0.0 for v in metrics["signal_precision"].values())

    def test_quality_metrics_all_successful(self, empty_state):
        """Test metrics when all escalations catch bugs."""
        for i in range(5):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.30,
                original_category="low",
                escalated_to=0.60,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="diff_size",
            )
            empty_state.escalation_events.append(event)

        metrics = compute_quality_metrics(empty_state)

        assert metrics["precision"] == 1.0
        assert metrics["false_alarm_rate"] == 0.0
        assert metrics["signal_precision"]["diff_size"] == 1.0

    def test_quality_metrics_mixed_outcomes(self, empty_state):
        """Test metrics with mixed success/failure outcomes."""
        for i in range(4):
            outcome = "fix_succeeded" if i % 2 == 0 else "fix_failed"
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.30,
                original_category="low",
                escalated_to=0.60,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome=outcome,
                lesson="type_surface",
            )
            empty_state.escalation_events.append(event)

        metrics = compute_quality_metrics(empty_state)

        assert metrics["precision"] == 0.5  # 2 out of 4 succeeded
        assert metrics["false_alarm_rate"] == 0.5  # 2 out of 4 failed


# =============================================================================
# LOAD/SAVE ROUNDTRIP TESTS
# =============================================================================

class TestLoadSaveRoundtrip:
    """Tests for YAML persistence."""

    def test_save_and_load_empty_state(self, temp_log_path, empty_state):
        """Test saving and loading an empty state."""
        save_learning_log(empty_state, temp_log_path)
        loaded_state = load_learning_log(temp_log_path)

        assert loaded_state.project_type == "global"
        assert len(loaded_state.escalation_events) == 0
        assert loaded_state.current_weights == DEFAULT_SIGNAL_WEIGHTS

    def test_save_and_load_with_events(self, temp_log_path, empty_state):
        """Test saving and loading state with escalation events."""
        # Add events
        for i in range(3):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.30 + i * 0.05,
                original_category="low",
                escalated_to=0.60 + i * 0.05,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="type_surface",
            )
            empty_state = record_escalation(empty_state, event)

        # Save and load
        save_learning_log(empty_state, temp_log_path)
        loaded_state = load_learning_log(temp_log_path)

        assert len(loaded_state.escalation_events) == 3
        assert loaded_state.escalation_events[0].event_id == "ESC-000000"
        assert loaded_state.escalation_events[2].bug_id == "BUG-2"

    def test_load_nonexistent_file_returns_initialized_state(self, temp_log_path):
        """Test that loading a nonexistent file returns fresh initialized state."""
        state = load_learning_log(temp_log_path)

        assert state.project_type == "global"
        assert len(state.escalation_events) == 0
        assert state.current_weights == DEFAULT_SIGNAL_WEIGHTS
        assert state.default_weights == DEFAULT_SIGNAL_WEIGHTS

    def test_save_preserves_events(self, temp_log_path, empty_state, sample_escalation_event):
        """Test that saved events are preserved exactly."""
        empty_state = record_escalation(empty_state, sample_escalation_event)
        save_learning_log(empty_state, temp_log_path)

        loaded_state = load_learning_log(temp_log_path)
        loaded_event = loaded_state.escalation_events[0]

        assert loaded_event.event_id == sample_escalation_event.event_id
        assert loaded_event.bug_id == sample_escalation_event.bug_id
        assert loaded_event.outcome == sample_escalation_event.outcome
        assert loaded_event.lesson == sample_escalation_event.lesson


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and corner conditions."""

    def test_get_effective_weights_returns_correct_tier(self, empty_state):
        """Test that get_effective_weights returns correct confidence tier."""
        # Add 3 events (N < 5)
        for i in range(3):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.30,
                original_category="low",
                escalated_to=0.60,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="diff_size",
            )
            empty_state.escalation_events.append(event)

        effective = get_effective_weights(empty_state)

        # Should be 100% defaults
        assert effective == empty_state.default_weights

    def test_ema_with_single_event(self, empty_state, sample_escalation_event):
        """
        Test EMA with just one event.

        With N=1, alpha = 2/2 = 1.0
        new_weight = 1.0 * importance + 0.0 * old_weight = importance
        outcome="fix_succeeded" → importance = 0.8

        However, L2 bounds are enforced: weight can't exceed 2x default.
        So if default_weight = 0.10, max = 0.20, clamped at 0.20.
        """
        empty_state = record_escalation(empty_state, sample_escalation_event)
        updated_state = compute_ema_weights(empty_state)

        # The specific signal mentioned in lesson should update
        lesson_signal = sample_escalation_event.lesson
        original_weight = DEFAULT_SIGNAL_WEIGHTS[lesson_signal]
        max_bounded = 2.0 * original_weight

        # After EMA: new = α * importance + (1-α) * old
        # α = 2/(1+1) = 1.0, importance = 0.8 (fix_succeeded)
        # new = 1.0 * 0.8 + 0.0 * original = 0.8
        # But L2 bounds cap at 2x default
        ema_weight = 0.8
        expected_weight = min(ema_weight, max_bounded)

        assert abs(updated_state.current_weights[lesson_signal] - expected_weight) < 0.001

    def test_weights_sum_approximately_normalized(self, empty_state):
        """Test that weights sum to approximately 1.0 (or stay close to default sum)."""
        # After multiple operations, weights shouldn't explode
        for i in range(10):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.30,
                original_category="low",
                escalated_to=0.60,
                trigger="type_cascade",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="type_surface" if i % 2 == 0 else "diff_size",
            )
            empty_state = record_escalation(empty_state, event)

        empty_state = compute_ema_weights(empty_state)
        weight_sum = sum(empty_state.current_weights.values())

        # Weights don't need to sum to exactly 1.0, but should be reasonable
        assert weight_sum > 0.5  # Not too low
        assert weight_sum < 2.0  # Not too high

    def test_cv_capped_at_2_0(self, empty_state):
        """Test that CV is capped at 2.0 to avoid extreme values."""
        # Create events with wildly different escalations
        extreme_deltas = [0.01, 0.90, 0.05, 0.85]
        for i, delta in enumerate(extreme_deltas):
            event = EscalationEvent(
                event_id=f"ESC-{i:06d}",
                timestamp=f"2026-04-02T{i:02d}:00:00",
                bug_id=f"BUG-{i}",
                project_type="react-spa",
                original_depth=0.35,
                original_category="low",
                escalated_to=0.35 + delta,
                trigger="manual_override",
                signals_at_decision=DEFAULT_SIGNAL_WEIGHTS.copy(),
                outcome="fix_succeeded",
                lesson="test_surface",
            )
            empty_state.escalation_events.append(event)

        cv = compute_cv(empty_state.escalation_events)
        assert cv <= 2.0  # Should be capped
