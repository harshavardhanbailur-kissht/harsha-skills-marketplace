# AVP Learning Loop CI/CD Integration Guide

## Prerequisites

To integrate AVP learning loop updates into your CI/CD pipeline, ensure you have:

- **Python 3.8+** installed
- **pyyaml** package installed (`pip install pyyaml`)
- A **project repository** where the `.ultimate-debugger/` directory can be committed
- The **ultimate-debugging-tool skill installed** in your project (run `./install.sh --project`)

## How the Learning Loop Works

The Adaptive Verification Pipeline (AVP) learns from escalation events—situations where a fix required deeper verification than the signal analyzer predicted. When an escalation occurs, an Exponential Moving Average (EMA) adjustment updates the weights of the signal that was underweighted, gradually tuning the prediction model to your project's specific complexity patterns.

The learning process is staged: cold-start projects use default weights for the first few escalations, then blend in learned weights as data accumulates. Without persistence—a shared learning log committed to your repository—the learning loop resets after every session. Integrating learning updates into CI/CD ensures the log file is maintained and weights evolve across all development cycles.

## Manual Escalation Logging

When a fix required deeper verification than AVP predicted, record the escalation event using this command:

```bash
python3 scripts/avp_learner.py \
  --log-path .ultimate-debugger/avp-learning-log.yaml \
  --action record \
  --event-json '{
    "event_id": "ESC-20260405-abc123",
    "timestamp": "2026-04-05T12:00:00Z",
    "bug_id": "<B_ID>",
    "project_type": "react-spa",
    "original_depth": 0.3,
    "original_category": "low",
    "escalated_to": 0.7,
    "trigger": "type_cascade",
    "signals_at_decision": {}
  }'
```

Replace:
- `<B_ID>`: Unique bug identifier (e.g., `BUG-1234`)
- `event_id`: Unique escalation identifier (e.g., `ESC-20260405-abc123`)
- `timestamp`: ISO 8601 timestamp of when the escalation occurred
- `project_type`: Your project type (e.g., `react-spa`, `nextjs-app`, `monorepo`)
- `original_depth`: The original depth score (0.0–1.0) that AVP predicted
- `escalated_to`: The actual depth required (0.0–1.0)
- `trigger`: The reason for escalation. Options include:
  - `type_cascade`: Type system rules cascaded deeper than expected
  - `distant_test_failure`: Tests failed far from the change
  - `lint_chain_reaction`: Linter errors spread beyond direct impact
  - `coverage_drop`: Code coverage fell unexpectedly
  - `manual_override`: Human judgment indicated deeper verification needed
- `original_category`: Bug severity category (e.g., `low`, `medium`, `high`)

## Viewing Current Learned Weights

To inspect the current learned weights and metadata, run:

```bash
python3 scripts/avp_learner.py \
  --log-path .ultimate-debugger/avp-learning-log.yaml \
  --action metrics --format text
```

This displays:
- Current weight values for each signal
- Metadata including event count and weight adjustment count
- The coefficient of variation (confidence measure)
- Whether learned weights are being applied or blended with defaults

## GitHub Actions Integration

Add this workflow to your repository at `.github/workflows/avp-learning.yml` to automatically update the learning log on every push to main:

```yaml
name: AVP Learning Loop

on:
  push:
    branches: [main]

jobs:
  avp-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: pip install pyyaml

      - name: Update AVP learning log
        run: |
          if [ -d .ultimate-debugger/pending-events ]; then
            for event_file in .ultimate-debugger/pending-events/*.json; do
              [ -f "$event_file" ] || continue
              python3 .claude/skills/ultimate-debugging-tool/scripts/avp_learner.py \
                --log-path .ultimate-debugger/avp-learning-log.yaml \
                --action record \
                --event-json "$(cat "$event_file")"
              rm "$event_file"
            done
            python3 .claude/skills/ultimate-debugging-tool/scripts/avp_learner.py \
              --log-path .ultimate-debugger/avp-learning-log.yaml \
              --action compute-weights
          fi

      - name: Commit updated weights
        run: |
          git config user.name "avp-bot"
          git config user.email "avp@noreply"
          git add .ultimate-debugger/avp-learning-log.yaml
          git diff --staged --quiet || git commit -m "chore: update AVP learned weights"
          git push
```

**How it works:**
1. On every push to `main`, the workflow checks for accumulated escalation events in `.ultimate-debugger/pending-events/`
2. If events exist, it processes each event file individually by calling `avp_learner.py --action record` with the event JSON
3. It removes each imported event file (it is now in the log)
4. It runs `--action compute-weights` to update the EMA-based weights
5. It commits the updated log file with a descriptive message
6. It pushes the changes back to the repository

This ensures the learning log remains synchronized across all CI/CD runs and developer environments.

## How to Verify It's Working

After at least 5 escalation events have been recorded, verify that the learning loop is active:

```bash
cat .ultimate-debugger/avp-learning-log.yaml | grep weight_adjustment_count
```

Look for:
- `weight_adjustment_count > 0`: The weights have been tuned based on escalations
- `total_events ≥ 5`: Enough data has been collected to begin learning
- `current_weights` differs from `default_weights`: The learned weights diverge from baseline

If these conditions are met, the learning loop is actively improving AVP's predictions for your project.

## Cold Start Timeline

The learning process progresses through distinct phases based on the number of escalation events recorded:

| Events | Blend Mode | Effect |
|--------|-----------|--------|
| 0–4 | 100% default | No learning yet — AVP uses only baseline weights |
| 5–14 | 70% default + 30% learned | Gentle tuning begins — 30% of predictions use learned weights |
| 15+ | Full learned (if CV < 0.3) | Signal weights fully adapted to your project patterns |

In cold start (< 5 events), AVP ignores learned weights and returns defaults. This prevents overfitting to a small sample. At 5–14 events, a blend reduces weight to outliers while still incorporating project-specific patterns. At 15+ events with coefficient of variation below 0.3 (low variance), the model is confident and switches to full learned weights.
