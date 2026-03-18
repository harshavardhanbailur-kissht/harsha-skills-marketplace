# Quick Start Guide

## 60-Second Setup

```bash
# 1. Install dependencies
pip install anthropic ruff

# 2. Set API key
export ANTHROPIC_API_KEY="sk-..."

# 3. Verify and merge outputs
python scripts/verifier.py --outputs-dir ./outputs --original-request "Your task"
python scripts/merger.py --outputs-dir ./outputs --merged-dir ./final
```

## Two Commands You Need

### Command 1: Verify
```bash
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Describe what you asked the agents to build"
```

**Output**: `verification_report.json` with pass/fail status and scores

### Command 2: Merge
```bash
python merger.py \
  --outputs-dir ./outputs \
  --merged-dir ./final
```

**Output**: `merged/merged.py` + `merge_report.json`

## What Each Script Does

### verifier.py (753 lines)
1. **Syntax check** - Valid Python?
2. **Duplicate check** - Duplicate code blocks?
3. **LLM judge** - Quality evaluation (0-1 score)
4. **Auto-fix** - Fixes issues automatically (3 attempts)

### merger.py (679 lines)
1. **Parse files** - Reads all outputs
2. **Merge smart** - Combines code intelligently
3. **Resolve conflicts** - Auto-fixes duplicate definitions
4. **Create report** - Documents what was merged

## Example: Build a REST API

```bash
# Setup
mkdir my_project && cd my_project
mkdir outputs
export ANTHROPIC_API_KEY="sk-..."

# Suppose you asked 3 agents to build:
# - Agent 1: database module
# - Agent 2: API routes
# - Agent 3: authentication

# They created: outputs/agent1.py, agent2.py, agent3.py

# Verify all outputs
python ../scripts/verifier.py \
  --outputs-dir ./outputs \
  --original-request "Build REST API with async DB and auth"

# Result: outputs/verification_report.json
# Shows: 3 files, 3 passed, 0 failed ✓

# Merge everything
python ../scripts/merger.py \
  --outputs-dir ./outputs \
  --merged-dir ./final

# Result: final/merged.py (all 3 files combined)
```

## Understanding the Reports

### verifier.py Report
```json
{
  "passed_files": 3,
  "failed_files": 0,
  "files": {
    "outputs/agent1.py": {
      "overall_score": 0.94,      ← Quality (0-1)
      "final_status": "PASS",     ← Pass/Fail
      "fix_attempts": 1,          ← How many fixes
      "rubric_scores": [
        {
          "name": "COMPLETENESS",
          "score": 0.95
        },
        // ... more criteria
      ]
    }
  }
}
```

### merger.py Report
```json
{
  "total_input_files": 3,
  "total_output_files": 1,
  "conflicts": [
    {
      "conflict_type": "duplicate_definition",
      "severity": "MEDIUM",
      "description": "Duplicate definition: process_request",
      "resolution": "Kept first implementation"
    }
  ],
  "unresolved_conflicts": []  ← Should be empty
}
```

## Evaluation Criteria (verifier.py)

Each file gets 4 scores:

| Criteria | Meaning | Pass Threshold |
|----------|---------|---|
| **Completeness** | All requirements? | > 0.8 |
| **Correctness** | Code works? | > 0.8 |
| **Consistency** | Style uniform? | > 0.8 |
| **Integration** | Merges cleanly? | > 0.8 |

Overall score = average of 4 criteria

## Merge Strategies

### Python Files (.py)
- Deduplicates imports
- Removes duplicate functions/classes
- Keeps first implementation
- Combines all into `merged.py`

### Documents (.md, .txt)
- Combines sections by heading
- Removes duplicate sections
- Maintains logical order
- Creates `merged.md`

### Mixed Types
- Creates `manifest.json` with file inventory

## Troubleshooting

**Problem**: Rate limit errors
```
Solution: Add 30-second delay between runs
python verifier.py ... && sleep 30 && python merger.py ...
```

**Problem**: "Import not found"
```
Solution: Install anthropic
pip install anthropic>=0.20.0
```

**Problem**: "API key invalid"
```
Solution: Set environment variable correctly
export ANTHROPIC_API_KEY="sk-..." (not in quotes for bash)
```

**Problem**: Files still have issues after verify
```
Solution: Check verification_report.json for failures
cat outputs/verification_report.json | jq '.files | to_entries[] | select(.value.final_status=="FAIL")'
```

## Performance Expectations

For 3 output files:
- **Verification**: 2-3 minutes
- **Merging**: 1-2 minutes
- **Total**: ~5 minutes

API calls made: ~13 (during verification)

## File Structure

```
outputs/
├── agent1.py        ← Inputs (from parallel agents)
├── agent2.py
├── agent3.py
├── verification_report.json  ← verifier.py output
└── (after merger.py)
    ├── merged.py    ← Final merged code
    ├── manifest.json
    └── merge_report.json
```

## Exit Codes

```
0 = Success
1 = Failures/Errors
130 = User interrupted (Ctrl+C)
```

## Advanced Options

### Custom max iterations
```bash
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Task" \
  --max-iterations 5  # More fix attempts
```

### Custom report path
```bash
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Task" \
  --output-report ./my_report.json
```

### With execution plan
```bash
python merger.py \
  --outputs-dir ./outputs \
  --plan ./plan.json  # Optional: for interface validation
  --merged-dir ./final
```

## What Happens Behind the Scenes

### verifier.py
1. Checks Python syntax (AST parsing)
2. Runs Ruff linter if available
3. Finds duplicate code blocks
4. Finds conflicting definitions
5. Sends each file to Claude Opus 4.6 for evaluation
6. If fails: sends to Claude Sonnet 4.6 for fixing
7. Re-evaluates fixed code
8. Repeats up to 3 times with increasing creativity
9. Generates report

### merger.py
1. Groups files by type (.py, .md, etc.)
2. For Python: extracts imports, deduplicates, combines
3. For documents: extracts sections, reorders, deduplicates
4. Detects conflicts (duplicate function names)
5. Sends conflicts to Claude Sonnet for resolution
6. Creates merged files and manifest
7. Generates report

## Integration with Your Workflow

```
Your prompt to Claude
    ↓
Claude splits into parallel tasks
    ↓
3+ Claude instances run in parallel
    ↓
Each produces outputs/{agentN}.py
    ↓
python verifier.py       ← HERE
    ↓
Verification report
    ↓
python merger.py         ← HERE
    ↓
outputs/merged.py        ← Your final result!
```

## Next Steps

1. **Read full docs**: See `USAGE.md` for complete options
2. **Run example**: Create test files in `outputs/` and run both scripts
3. **Integrate**: Add to your parallel skill workflow
4. **Customize**: Modify prompts in rubric or merge strategies

## Support

- **Full docs**: USAGE.md
- **Architecture**: PRODUCTION_SCRIPTS_SUMMARY.md
- **Examples**: See EXAMPLE.md in parent directory

Good luck with your parallel builds!
