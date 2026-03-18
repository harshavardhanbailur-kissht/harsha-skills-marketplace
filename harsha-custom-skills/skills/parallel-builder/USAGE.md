# Parallel Skill Builder - Complete Usage Guide

## Overview

The Parallel Skill Builder consists of two production-ready Python scripts for verifying and merging outputs from multiple parallel agents:

1. **verifier.py** - Multi-layered verification pipeline with LLM judge and iterative fixing
2. **merger.py** - Intelligent output consolidation with semantic conflict resolution

## Prerequisites

```bash
# Install Anthropic SDK
pip install anthropic

# Optional: Install Ruff for enhanced linting
pip install ruff

# Set API key
export ANTHROPIC_API_KEY="your-api-key"
```

## Script 1: verifier.py

### Purpose
Verifies outputs from parallel agents through a 3-stage pipeline:
1. Static analysis (syntax checking + optional Ruff linting)
2. Duplicate/conflict detection across outputs
3. LLM-as-judge evaluation with iterative fixing

### Usage

#### Basic Usage
```bash
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Build a REST API for task management with async support"
```

#### With Custom Parameters
```bash
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Feature description" \
  --max-iterations 5 \
  --output-report ./verification_report.json
```

### CLI Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--outputs-dir` | Path | Yes | - | Directory containing Python output files |
| `--original-request` | str | Yes | - | Original task/feature request |
| `--max-iterations` | int | No | 3 | Maximum fix attempts per file |
| `--output-report` | Path | No | `outputs_dir/verification_report.json` | Report output path |

### Output Report Structure

```json
{
  "timestamp": "2025-02-19T10:30:00.123456",
  "original_request": "Feature description",
  "total_files": 5,
  "verified_files": 5,
  "passed_files": 5,
  "failed_files": 0,
  "summary": "Verification completed: 5/5 files passed (100%)",
  "duplicates_across_outputs": [...],
  "conflicts_across_outputs": [...],
  "files": {
    "path/to/file.py": {
      "file_path": "path/to/file.py",
      "syntax_valid": true,
      "syntax_errors": [],
      "overall_score": 0.95,
      "final_status": "PASS",
      "fix_attempts": 0,
      "rubric_scores": [
        {
          "name": "COMPLETENESS",
          "score": 0.95,
          "feedback": "All requirements addressed",
          "status": "PASS"
        },
        {
          "name": "CORRECTNESS",
          "score": 0.95,
          "feedback": "Code is syntactically and logically correct",
          "status": "PASS"
        },
        {
          "name": "CONSISTENCY",
          "score": 0.95,
          "feedback": "Code follows consistent style",
          "status": "PASS"
        },
        {
          "name": "INTEGRATION",
          "score": 0.90,
          "feedback": "Can be merged with other outputs",
          "status": "PASS"
        }
      ]
    }
  }
}
```

### Key Features

#### Multi-Stage Verification
1. **Static Analysis**: Runs Ruff if available, falls back to AST syntax checking
2. **Duplicate Detection**: Finds duplicate code blocks across files
3. **Conflict Detection**: Identifies conflicting function/class definitions
4. **LLM Judge**: Uses Claude Opus 4.6 with rubric-based evaluation
5. **Iterative Fixing**: Employs Sonnet 4.6 to fix issues up to max_iterations

#### Evaluation Rubric
Each file is evaluated on 4 criteria (0.0-1.0 scale):
- **COMPLETENESS**: All requirements addressed, no gaps
- **CORRECTNESS**: Syntactically and semantically correct code
- **CONSISTENCY**: Uniform style and naming conventions
- **INTEGRATION**: Compatible with other outputs, clear interfaces

#### LLMLOOP Pattern
Temperature increases with fix attempts to encourage diverse solutions:
- Attempt 1: temperature=0.3
- Attempt 2: temperature=0.5
- Attempt 3: temperature=0.7

#### Bias Mitigation
- Random presentation order to LLM judge reduces anchoring bias
- Multiple evaluation criteria prevent single-factor bias
- Structured JSON output enables consistent scoring

### Example Workflow

```bash
# 1. Run agents in parallel (produces outputs/)
# Agent 1, 2, 3, ... generate code files

# 2. Verify all outputs
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Implement async database connection pool"

# 3. Check report
cat ./outputs/verification_report.json | jq '.summary'

# 4. If failures, examine report and refine agent prompts
# Fixed files in report show fix_attempts > 0
```

### Return Codes
- `0`: All files verified successfully
- `1`: Some files failed verification
- `130`: User interrupt (Ctrl+C)

---

## Script 2: merger.py

### Purpose
Intelligently merges verified outputs from multiple parallel agents into cohesive final output with semantic conflict resolution.

### Usage

#### Basic Usage
```bash
python merger.py \
  --outputs-dir ./outputs \
  --merged-dir ./merged
```

#### With Execution Plan
```bash
python merger.py \
  --outputs-dir ./outputs \
  --plan ./plan.json \
  --merged-dir ./merged \
  --output-report ./merge_report.json
```

### CLI Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--outputs-dir` | Path | Yes | - | Directory with verified outputs |
| `--plan` | Path | No | - | Execution plan JSON (for interface contracts) |
| `--merged-dir` | Path | No | `outputs_dir` | Output directory for merged files |
| `--output-report` | Path | No | `merged_dir/merge_report.json` | Report output path |

### Output Structure

```
merged/
├── merged.py                 # All Python files combined
├── merged.md                 # All documentation combined
├── manifest.json             # Inventory of merged files
└── merge_report.json         # Detailed merge report
```

### Output Report Structure

```json
{
  "timestamp": "2025-02-19T10:35:00.123456",
  "total_input_files": 5,
  "total_output_files": 2,
  "summary": "Merge completed: 2 output files from 5 input files. Conflicts: 0 (0 unresolved)",
  "files_merged": [
    {
      "output_path": "merged/merged.py",
      "source_files": ["outputs/agent1.py", "outputs/agent2.py"],
      "merge_strategy": "code_combine",
      "line_count": 450,
      "conflicts_resolved": 1,
      "warnings": []
    }
  ],
  "conflicts": [
    {
      "file_paths": ["outputs/agent1.py", "outputs/agent2.py"],
      "conflict_type": "duplicate_definition",
      "severity": "MEDIUM",
      "description": "Duplicate definition: process_request",
      "resolution": "Kept implementation from agent1.py"
    }
  ],
  "unresolved_conflicts": [],
  "warnings": []
}
```

### Merge Strategies

#### 1. Code Combine (Python files)
- Deduplicates imports (removes duplicates, sorts alphabetically)
- Extracts all function/class definitions
- Removes duplicate definitions, keeps first occurrence
- Preserves import order and code structure
- Resolves semantic conflicts using Sonnet

**Example**:
```python
# Input files
# agent1.py
import asyncio
def process(): pass

# agent2.py
import asyncio
import aiohttp
def process(): pass  # Duplicate!

# merged.py
import aiohttp
import asyncio

def process(): pass  # Only one kept
```

#### 2. Document Assemble (Markdown/text files)
- Extracts sections from documents (by heading level)
- Orders sections logically by heading level
- Deduplicates identical sections
- Preserves section content

**Example**:
```markdown
# Input files
# agent1.md
## Overview
...
## Installation
...

# agent2.md
## Installation
...
## Usage
...

# merged.md
## Overview
...
## Installation
...
## Usage
...
```

#### 3. Manifest (Mixed/other types)
- Creates organized inventory of all files
- Documents merge strategy per file type
- Lists source files for traceability

### Key Features

#### Intelligent Merging
- **Import Deduplication**: Removes duplicate imports, preserves order
- **Definition Deduplication**: Keeps first implementation of functions/classes
- **Section Organization**: Documents assembled in logical order
- **Manifest Creation**: Complete inventory of merged outputs

#### Semantic Conflict Resolution
- Detects duplicate definitions across files
- Uses Claude Sonnet 4.6 to intelligently resolve conflicts
- Preserves conflict resolution reasoning in reports

#### Edge Case Handling
- Missing output files: Gracefully skips unavailable files
- Incompatible interfaces: Reports conflicts for manual review
- Circular references: Detects and warns in report

### Example Workflow

```bash
# 1. Run verifier first
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Build REST API"

# 2. Check verification passed
# All files should have final_status: PASS

# 3. Merge outputs
python merger.py \
  --outputs-dir ./outputs \
  --merged-dir ./final_output

# 4. Inspect merged results
cat ./final_output/manifest.json
cat ./final_output/merged.py

# 5. Review merge report for conflicts
cat ./final_output/merge_report.json | jq '.conflicts'
```

### Return Codes
- `0`: All files merged successfully (no unresolved conflicts)
- `1`: Merge completed but unresolved conflicts exist
- `130`: User interrupt (Ctrl+C)

---

## Complete Pipeline Example

### Setup
```bash
# Create working directory
mkdir parallel-build && cd parallel-build
export ANTHROPIC_API_KEY="sk-..."

# Create output directory (populated by your agents)
mkdir outputs
# agent1.py, agent2.py, agent3.py would be placed here
```

### Execute Pipeline
```bash
# 1. Verify outputs
python verifier.py \
  --outputs-dir ./outputs \
  --original-request "Implement task management API with async database support" \
  --max-iterations 3 \
  --output-report ./verification_report.json

# 2. Check results
cat verification_report.json | jq '.summary'

# 3. If all passed, merge
python merger.py \
  --outputs-dir ./outputs \
  --merged-dir ./final_output \
  --output-report ./merge_report.json

# 4. Verify merge
cat final_output/merge_report.json | jq '.summary'

# 5. Review final code
cat final_output/merged.py
```

### Expected Output
```
✓ Verification completed: 3/3 files passed (100%)
✓ Merge completed: 1 output file from 3 input files. Conflicts: 0 (0 unresolved)
```

---

## Architecture Details

### verifier.py Components

```python
StaticAnalyzer       # Ruff + AST syntax checking
DuplicateDetector    # Block extraction and hashing
LLMJudge             # Claude Opus 4.6 evaluation
FixIterator          # Claude Sonnet 4.6 fixes
VerificationPipeline # Orchestrates 3-stage pipeline
```

### merger.py Components

```python
CodeMerger           # Import dedup, definition extraction
DocumentMerger       # Section extraction and assembly
ConflictResolver     # Sonnet-based semantic resolution
Merger               # Orchestrates merge process
```

---

## Advanced Usage

### Custom Rubric
To modify evaluation criteria, edit the `LLMJudge.create_rubric()` method in verifier.py

### Execution Plan Format
The optional `plan.json` should contain interface definitions:
```json
{
  "tasks": [
    {
      "id": "task1",
      "outputs": ["database.py"],
      "interfaces": {
        "Database": ["connect", "query", "close"]
      }
    }
  ]
}
```

### Environment Variables
- `ANTHROPIC_API_KEY`: Required for Claude API access
- `MAX_TOKENS`: Optional token limit override (default: 4000)

---

## Troubleshooting

### API Rate Limits
If you hit rate limits, add delays between script runs:
```bash
python verifier.py ... && sleep 30 && python merger.py ...
```

### Large Outputs
For files > 2000 lines, content is truncated for LLM evaluation. Consider splitting into smaller modules.

### Memory Issues
For very large projects, process outputs in batches by agent.

### Missing Dependencies
```bash
# Install all requirements
pip install anthropic ruff
```

---

## Performance Characteristics

| Component | Time | API Calls |
|-----------|------|-----------|
| Static Analysis | O(n) files | 0 |
| Duplicate Detection | O(n²) files | 0 |
| LLM Judge (3 files) | ~30s | 3 |
| Fix Iterations (3x3) | ~90s | 9 |
| Code Merge | O(n) files | 0 |
| Conflict Resolution | ~10s | 1 |

**Total for 3 files**: ~2-3 minutes, ~13 API calls

---

## License & Credits

These production scripts implement the Parallel Skill Builder meta-skill architecture with:
- LLMLOOP pattern for adaptive solving
- Bias mitigation strategies
- Comprehensive error handling
- Structured output formats
