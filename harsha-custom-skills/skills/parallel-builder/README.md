# Parallel Skill Builder

A production-ready Python framework for decomposing complex features into parallel subtasks and executing them concurrently using Claude AI models.

## Overview

The Parallel Skill Builder consists of two main components:

1. **Planner** (`planner.py`): Decomposes feature descriptions into a DAG of parallel subtasks using Claude Opus 4.6
2. **Executor** (`executor.py`): Executes all subtasks in parallel using Claude Sonnet 4.6

## Architecture

### Planner Flow
```
Feature Description
        ↓
Claude Opus 4.6 Analysis
        ↓
Task Decomposition & DAG Creation
        ↓
Topological Sort (Kahn's Algorithm)
        ↓
Execution Layers Identified
        ↓
Optimized Prompts Generated
        ↓
Execution Plan (JSON)
```

### Executor Flow
```
Execution Plan (JSON)
        ↓
Load Tasks & Dependencies
        ↓
Execute Layer 1 (parallel tasks)
        ↓
Inject outputs into Layer 2
        ↓
Execute Layer 2 (parallel tasks)
        ↓
... (repeat for all layers)
        ↓
Execution Report (JSON)
```

## Installation

### Prerequisites
- Python 3.10+
- Anthropic SDK: `pip install anthropic`

### Setup
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### Step 1: Create Execution Plan

```bash
python scripts/planner.py \
  --feature "Build a REST API with authentication, database persistence, and real-time notifications" \
  --output plan.json \
  --verbose
```

**Example Output:**
```
Execution Plan Summary:
  Feature: Build a REST API with authentication, database persistence, and real-time notifications
  Tasks: 8
  Execution Layers: 3
  Estimated Tokens: 12000
  Estimated Cost: $0.0180

Tasks:
  - task_1: Design API Schema (no dependencies)
  - task_2: Implement Authentication Module (depends on: task_1)
  - task_3: Build Database Layer (depends on: task_1)
  - task_4: Create API Endpoints (depends on: task_2, task_3)
  - task_5: Implement WebSocket Handler (depends on: task_1)
  - task_6: Setup Notifications Service (depends on: task_5, task_4)
  - task_7: Write Integration Tests (depends on: task_4, task_6)
  - task_8: Create Documentation (depends on: task_4)

Execution Layers:
  Layer 0: task_1
  Layer 1: task_2, task_3, task_5
  Layer 2: task_4, task_6
  Layer 3: task_7, task_8
```

### Step 2: Execute Plan

```bash
python scripts/executor.py \
  --plan plan.json \
  --output-dir ./outputs \
  --concurrency 5 \
  --max-retries 3 \
  --report execution_report.json \
  --verbose
```

**Example Output:**
```
Execution Report Summary:
  Plan: plan.json
  Total Tasks: 8
  Successful: 8
  Failed: 0
  Success Rate: 100.0%
  Total Tokens: 14532
  Total Cost: $0.021849
  Total Time: 45.23s
  Output Directory: ./outputs
  Report: execution_report.json
```

## Script Details

### planner.py

#### Dataclasses
- `InterfaceContract`: Input/output specifications for subtasks
- `SubTask`: Individual task with dependencies and contracts
- `ExecutionLayer`: Group of tasks that can execute in parallel
- `ExecutionPlan`: Complete plan with tasks, layers, and cost estimates

#### Key Classes
- `TaskDecomposer`: Main orchestrator for feature decomposition
  - `decompose_feature()`: Breaks down feature into parallel subtasks
  - `_compute_execution_layers()`: Implements Kahn's Algorithm for topological sort
  - `_generate_task_prompts()`: Creates optimized prompts for Sonnet execution
  - `save_plan()`: Persists plan to JSON

#### Features
- Async/await with AsyncAnthropic client
- Kahn's Algorithm for dependency resolution
- Cost estimation (based on Opus pricing: $15/1M input, $45/1M output)
- Comprehensive logging and error handling
- CLI with argparse

#### Output: plan.json
```json
{
  "feature_description": "...",
  "tasks": [
    {
      "id": "task_1",
      "title": "Task Name",
      "description": "Detailed description",
      "dependencies": [],
      "prompt": "Optimized prompt for execution",
      "contract": {
        "input_spec": {"param": "description"},
        "output_spec": {"result": "description"},
        "constraints": ["constraint 1", "constraint 2"]
      }
    }
  ],
  "layers": [
    {
      "layer_id": 0,
      "task_ids": ["task_1"],
      "estimated_duration_seconds": 2.0
    }
  ],
  "estimated_total_tokens": 12000,
  "estimated_cost_usd": 0.018
}
```

### executor.py

#### Dataclasses
- `TaskResult`: Result of executing a single task
- `ExecutionReport`: Comprehensive execution metrics and results

#### Key Classes
- `TaskExecutor`: Main orchestrator for parallel task execution
  - `execute_plan()`: Loads plan and executes layers sequentially
  - `execute_task()`: Executes individual task with retry logic
  - `_load_plan()`: Validates and loads plan JSON
  - `save_report()`: Persists execution report

#### Features
- Semaphore-based concurrency control (prevents rate limiting)
- Exponential backoff retry logic (configurable max retries)
- Dependency output injection into downstream prompts
- Per-task output file writing (not coordinator-based)
- Token tracking and cost calculation (Sonnet: $3/1M input, $15/1M output)
- Graceful degradation (continues with partial results on failures)
- Progress logging and reporting

#### Output: execution_report.json
```json
{
  "plan_path": "plan.json",
  "total_tasks": 8,
  "successful_tasks": 8,
  "failed_tasks": 0,
  "total_tokens_used": 14532,
  "total_cost_usd": 0.021849,
  "total_execution_time_seconds": 45.23,
  "success_rate": 100.0,
  "task_results": [
    {
      "task_id": "task_1",
      "success": true,
      "output": "/path/to/task_1_output.txt",
      "error": null,
      "tokens_used": 1823,
      "cost_usd": 0.002735,
      "execution_time_seconds": 5.12,
      "retry_count": 0
    }
  ],
  "errors": []
}
```

## Command Line Options

### planner.py
```
--feature TEXT           Feature description to decompose (required)
--output FILE           Output file path for execution plan (default: plan.json)
--api-key TEXT          Anthropic API key (uses ANTHROPIC_API_KEY if not provided)
--verbose               Enable verbose logging
--help                  Show help message
```

### executor.py
```
--plan FILE             Path to execution plan JSON file (required)
--output-dir DIR        Directory for task output files (default: ./outputs)
--report FILE           Path for execution report JSON (default: execution_report.json)
--concurrency N         Maximum concurrent tasks (default: 5)
--max-retries N         Maximum retries per task (default: 3)
--api-key TEXT          Anthropic API key (uses ANTHROPIC_API_KEY if not provided)
--verbose               Enable verbose logging
--help                  Show help message
```

## Implementation Details

### Kahn's Algorithm (Topological Sort)
The planner uses Kahn's Algorithm to identify execution layers:
1. Compute in-degree for each task (number of dependencies)
2. Identify all tasks with in-degree 0 (no dependencies) → Layer 0
3. Remove these tasks, decrement in-degree of dependents
4. Repeat until all tasks are assigned to layers

This ensures:
- Maximum parallelization of independent tasks
- Correct ordering of dependent tasks
- Detection of circular dependencies

### Dependency Injection
When a task is executed, outputs from its dependencies are prepended to its prompt:
```
DEPENDENCY OUTPUTS:

task_1 output:
[content of task_1 output]

[original task prompt]
```

This allows downstream tasks to make decisions based on upstream results.

### Rate Limiting
The executor uses asyncio.Semaphore to limit concurrent API calls:
- Prevents hitting API rate limits
- Configurable concurrency (default: 5)
- Internally queues excess tasks

### Retry Strategy
Exponential backoff with configurable max retries:
- Attempt 1: immediate retry
- Attempt 2: wait 1s
- Attempt 3: wait 2s
- Attempt 4: wait 4s
- And so on...

## Error Handling

### Planner Errors
- **JSON Parsing**: Handles markdown code blocks and raw JSON objects
- **Circular Dependencies**: Detects and logs circular dependency issues
- **API Errors**: Caught and re-raised with context

### Executor Errors
- **Missing Plan File**: Clear error message with path
- **Invalid Plan Structure**: Validates required fields
- **Task Execution Failures**: Retries with exponential backoff, then gracefully degrades
- **Partial Failures**: Continues execution with available results

## Cost Estimation

### Planner (Claude Opus 4.6)
- Input: $15 per 1M tokens
- Output: $45 per 1M tokens
- Estimated in plan.json

### Executor (Claude Sonnet 4.6)
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Tracked in execution_report.json

## Performance Characteristics

### Execution Time
- Sequential layer execution: depends on number of layers
- Parallel within layer: T = max(task times) rather than sum
- Typical overhead: <1s per layer

### Token Usage
- Varies by task complexity
- Average 1000-2000 tokens per task
- Reported in execution_report.json

## Example Workflow

```bash
#!/bin/bash

# Create execution plan
python scripts/planner.py \
  --feature "Implement a machine learning pipeline with data preprocessing, model training, and evaluation" \
  --output ml_pipeline_plan.json \
  --verbose

# Execute plan
python scripts/executor.py \
  --plan ml_pipeline_plan.json \
  --output-dir ./ml_outputs \
  --concurrency 3 \
  --report ml_execution_report.json \
  --verbose

# Check results
cat ml_execution_report.json | jq '.success_rate, .total_cost_usd'
ls -la ./ml_outputs/
```

## Best Practices

1. **Feature Descriptions**: Be specific and detailed about requirements
2. **Concurrency**: Start with 3-5, increase only if needed (avoid rate limiting)
3. **Retries**: Default of 3 is reasonable for most use cases
4. **Output Directory**: Use separate directories for different plans to avoid conflicts
5. **Monitoring**: Use --verbose flag during initial testing

## Limitations

- Maximum task count: limited by Claude's context window
- Circular dependencies: detected but cause early termination
- Task interdependencies: assumes outputs are serializable as text
- No distributed execution: all tasks run in single process

## License

Production-ready code for Anthropic Claude framework.
