## Getting Started

To make the learning loop accumulate across sessions, you need a persistent
environment. See `docs/avp-ci-integration.md` for a GitHub Actions workflow
that maintains the learning log between runs.

# Adaptive Verification Pipeline — Learning Loop

When escalation happens, it means the Fix Signal Analyzer underestimated complexity. This learning loop logs escalation events and enables weight tuning over time.

**Stateless Session Note**: Claude Code sessions are stateless, so the learning log file does not persist between invocations. The learning functionality is designed to degrade gracefully — default weights are always returned when no learning log exists. For learning to accumulate, run this script in a persistent environment (local project, CI/CD pipeline, etc.) where the log file can be maintained across multiple runs.

## Learning Log Schema

```yaml
# .ultimate-debugger/avp-learning-log.yaml

metadata:
  created: datetime
  last_updated: datetime
  total_events: integer
  project_type: string
  weight_adjustment_count: integer      # How many times weights were tuned

# Current weights (evolve over time)
current_weights:
  diff_size: float
  files_touched: float
  ast_depth: float
  type_surface: float
  test_surface: float
  dependency_fan: float

# Default weights (never change — baseline for comparison)
default_weights:
  diff_size: 0.20
  files_touched: 0.15
  ast_depth: 0.20
  type_surface: 0.10
  test_surface: 0.12
  dependency_fan: 0.23

# Escalation event history
escalation_events:
  - event_id: string               # Format: ESC-YYYYMMDD-XXXXXX
    timestamp: datetime
    bug_id: string                  # Links to bug manifest entry
    project_type: string

    # What the signal analyzer predicted
    original_depth: float           # Composite score at decision time
    original_category: enum         # minimal | low | moderate | high | full

    # What actually happened
    escalated_to: float             # New depth after escalation
    trigger: enum                   # type_cascade | distant_test_failure |
                                    #   lint_chain_reaction | coverage_drop |
                                    #   manual_override

    # Signal snapshot at decision time
    signals_at_decision:
      diff_size: float
      files_touched: float
      ast_depth: float
      type_surface: float
      test_surface: float
      dependency_fan: float

    # Outcome tracking (filled in after fix is complete)
    outcome: enum                   # fix_succeeded | fix_failed | required_rework
    outcome_details: string         # What happened after escalation
    lesson: string                  # What signal was underweighted

    # Context for debugging weight drift
    context:
      weights_at_time: dict         # Snapshot of weights when decision was made
      n_events_at_time: integer     # How many escalation events had occurred
      confidence_cv: float          # Coefficient of variation of weight estimates
```

## Weight Adjustment Strategy

### Progressive Confidence Model

Research shows reliable convergence requires N ≥ 15 samples for simple models. Use a progressive confidence approach that blends defaults with learned weights:

```
N < 5 escalations:   100% default weights (learning disabled)
N = 5-10:            70% default + 30% learned weights
N = 10-15:           50% default + 50% learned weights
N ≥ 15 and CV < 0.3: Full learned weights
```

### EMA Weight Update Formula

When an escalation event occurs, update the weight of the underweighted signal using Exponential Moving Average:

```
α = 2 / (1 + N)           # Decay factor (N = total escalation events)
                            # For N=10, α ≈ 0.18; for N=20, α ≈ 0.10

new_weight[signal] = α * observed_importance + (1 - α) * current_weight[signal]
```

Where `observed_importance` is calculated from the escalation event:
- If escalation caught a real bug → signal that was low gets importance boost
- If escalation was a false alarm → no adjustment

### Overfitting Prevention

Three safeguards prevent a single unusual event from permanently skewing weights:

1. **L2 Regularization**: Weight adjustments are bounded. No single weight can exceed 2× its default value or fall below 0.5× its default.

2. **Confidence Threshold**: Weights are only adjusted when the posterior coefficient of variation (CV = std/mean across recent events) falls below 0.3. High variance → insufficient signal → use defaults.

3. **Recency Bias Limit**: The EMA decay factor α ensures old events naturally decay in influence. A single event contributes at most α × 100% to the new weight.

### When NOT to Adjust Weights

- Fewer than 5 escalation events recorded (cold start)
- Posterior CV > 0.3 (too much variance in recent events)
- Escalation was triggered by flaky tests (false alarm)
- Manual override escalation (human judgment, not signal failure)

## Project-Type Segmentation

### Hierarchical Learning Model

Learning operates at two levels:

**Global level**: Population distribution of signal weights across all project types. Provides baseline for cold start and shrinkage target.

**Project-type level**: Per-type weight adjustments. A Three.js project's escalation patterns differ from a React SPA's. Maintain separate learning logs per project type.

**Shrinkage**: Project types with few escalation events (< 10) shrink toward global weights. Types with abundant data (> 30) can diverge significantly.

### Cold Start for New Project Types

When AVP encounters a project type with no prior escalation history:

1. Start with global default weights
2. If a similar project type has history, initialize from that type's weights
3. Begin accumulating escalation events
4. After 5 events, start blending learned weights at 30%
5. After 15 events, fully learned weights (if CV threshold met)

## Escalation Quality Metrics

Track these metrics to evaluate learning loop effectiveness:

| Metric | Formula | Target |
|--------|---------|--------|
| Precision | (escalations that caught bugs) / (total escalations) | > 70% |
| Recall | 1 - (production bugs from non-escalated) / (total non-escalated) | > 95% |
| Signal Precision | Per-signal: caught_bugs / times_triggered | Varies |
| Weight Stability | std(weight changes last 10 events) | < 0.05 |
| False Alarm Rate | false_alarms / total_escalations | < 30% |

## Analysis Workflow

### Weekly Review (Automated)

For each signal, compute:
1. How often it triggered escalation
2. Of those, how many caught real issues (signal precision)
3. Whether current weight reflects observed importance

### Quarterly Calibration

1. Compute calibration curves: predicted depth vs observed bug rate
2. Identify natural breakpoints where outcome distribution changes
3. Adjust depth thresholds (0.25, 0.50, 0.75) if observed outcomes diverge > 20%
4. Log all threshold and weight changes for audit trail
