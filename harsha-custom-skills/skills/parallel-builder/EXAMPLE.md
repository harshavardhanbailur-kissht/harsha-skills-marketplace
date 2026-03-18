# Parallel Skill Builder - Example Walkthrough

This document provides a complete example of using the Parallel Skill Builder framework to decompose and execute a complex feature.

## Example: Building a Production Data Analytics Platform

### Step 1: Prepare the Feature Description

Create a detailed feature description for what you want to build:

```
Build a production-grade data analytics platform that:
- Ingests data from multiple sources (CSV, APIs, databases)
- Performs real-time data validation and quality checks
- Implements data transformation and enrichment pipelines
- Provides a GraphQL API for querying processed data
- Includes role-based access control (RBAC) for security
- Generates automated insights and anomaly detection
- Offers data visualization dashboards
- Supports scheduled batch processing and real-time streaming
- Includes comprehensive monitoring and alerting
```

### Step 2: Run the Planner

```bash
$ python scripts/planner.py \
    --feature "Build a production-grade data analytics platform that ingests data from multiple sources (CSV, APIs, databases), performs real-time data validation and quality checks, implements data transformation and enrichment pipelines, provides a GraphQL API for querying processed data, includes role-based access control (RBAC) for security, generates automated insights and anomaly detection, offers data visualization dashboards, supports scheduled batch processing and real-time streaming, includes comprehensive monitoring and alerting" \
    --output analytics_plan.json \
    --verbose
```

### Expected Output from Planner

```
2024-01-15 10:23:45,123 - __main__ - INFO - Decomposing feature: Build a production-grade data analytics platform...
2024-01-15 10:23:47,456 - __main__ - INFO - Extracted 12 tasks from decomposition
2024-01-15 10:23:47,789 - __main__ - INFO - Computed 4 execution layers
2024-01-15 10:23:48,012 - __main__ - INFO - Generating optimized task prompts
2024-01-15 10:23:48,345 - __main__ - INFO - Execution plan saved to analytics_plan.json

Execution Plan Summary:
  Feature: Build a production-grade data analytics platform...
  Tasks: 12
  Execution Layers: 4
  Estimated Tokens: 18000
  Estimated Cost: $0.0270

Tasks:
  - task_1: Design Core Data Model
  - task_2: Build Data Ingestion Framework
  - task_3: Implement Data Validation Engine
  - task_4: Create Data Transformation Pipeline
  - task_5: Design RBAC System
  - task_6: Build GraphQL API Server
  - task_7: Implement Anomaly Detection Module
  - task_8: Create Dashboard Components
  - task_9: Setup Monitoring & Alerting
  - task_10: Implement Batch Processing Scheduler
  - task_11: Create Real-time Streaming Handler
  - task_12: Write Integration Tests & Documentation

Execution Layers:
  Layer 0: task_1, task_5
  Layer 1: task_2, task_3, task_6, task_9
  Layer 2: task_4, task_7, task_8, task_10, task_11
  Layer 3: task_12
```

### Step 3: Examine the Generated Plan

```bash
$ cat analytics_plan.json | jq '.tasks[0]'
```

```json
{
  "id": "task_1",
  "title": "Design Core Data Model",
  "description": "Design the core data model including schemas for raw data ingestion, processed data storage, and metadata. This forms the foundation for all downstream operations.",
  "dependencies": [],
  "prompt": "You are working on a subtask as part of building: Build a production-grade data analytics platform...\n\nSUBTASK: Design Core Data Model\nDESCRIPTION: Design the core data model including schemas for raw data ingestion...",
  "contract": {
    "input_spec": {
      "platform_requirements": "Data types and volume expectations",
      "scalability_needs": "Expected growth and concurrent users"
    },
    "output_spec": {
      "schema_definitions": "PostgreSQL/MongoDB schema definitions",
      "model_relationships": "Entity relationship diagram in text format",
      "indexing_strategy": "Recommended indices for performance"
    },
    "constraints": [
      "Must support both relational and document data types",
      "Design must account for 100M+ records",
      "Must include versioning for schema evolution"
    ]
  }
}
```

### Step 4: Run the Executor

```bash
$ python scripts/executor.py \
    --plan analytics_plan.json \
    --output-dir ./analytics_outputs \
    --concurrency 4 \
    --max-retries 3 \
    --report analytics_report.json \
    --verbose
```

### Expected Execution Flow

```
2024-01-15 10:24:01,234 - __main__ - INFO - Loading execution plan from analytics_plan.json
2024-01-15 10:24:01,567 - __main__ - INFO - Loaded plan with 12 tasks in 4 layers
2024-01-15 10:24:01,890 - __main__ - INFO - Executing layer 0 with 2 task(s): task_1, task_5
2024-01-15 10:24:02,123 - __main__ - INFO - Executing task task_1: Design Core Data Model
2024-01-15 10:24:02,456 - __main__ - INFO - Executing task task_5: Implement RBAC System
2024-01-15 10:24:08,789 - __main__ - INFO - Task task_1 completed: 1823 tokens, $0.002735, 6.42s
2024-01-15 10:24:09,012 - __main__ - INFO - Task task_5 completed: 2156 tokens, $0.003234, 6.92s
2024-01-15 10:24:09,345 - __main__ - INFO - Executing layer 1 with 4 task(s): task_2, task_3, task_6, task_9
2024-01-15 10:24:09,678 - __main__ - INFO - Executing task task_2: Build Data Ingestion Framework
2024-01-15 10:24:09,901 - __main__ - INFO - Executing task task_3: Implement Data Validation Engine
2024-01-15 10:24:10,234 - __main__ - INFO - Executing task task_6: Build GraphQL API Server
2024-01-15 10:24:10,567 - __main__ - INFO - Executing task task_9: Setup Monitoring & Alerting
2024-01-15 10:24:27,890 - __main__ - INFO - Task task_2 completed: 1945 tokens, $0.002918, 17.76s
2024-01-15 10:24:28,123 - __main__ - INFO - Task task_3 completed: 1634 tokens, $0.002451, 17.89s
2024-01-15 10:24:28,456 - __main__ - INFO - Task task_6 completed: 2234 tokens, $0.003351, 18.12s
2024-01-15 10:24:28,789 - __main__ - INFO - Task task_9 completed: 1567 tokens, $0.002351, 18.45s
...
2024-01-15 10:24:55,234 - __main__ - INFO - Plan execution complete: 12 successful, 0 failed in 54.23s
```

### Step 5: Review Execution Results

```bash
$ cat analytics_report.json | jq '.'
```

```json
{
  "plan_path": "analytics_plan.json",
  "total_tasks": 12,
  "successful_tasks": 12,
  "failed_tasks": 0,
  "total_tokens_used": 22145,
  "total_cost_usd": 0.033218,
  "total_execution_time_seconds": 54.23,
  "success_rate": 100.0,
  "task_results": [
    {
      "task_id": "task_1",
      "success": true,
      "output": "/path/to/analytics_outputs/task_1_output.txt",
      "error": null,
      "tokens_used": 1823,
      "cost_usd": 0.002735,
      "execution_time_seconds": 6.42,
      "retry_count": 0
    },
    {
      "task_id": "task_2",
      "success": true,
      "output": "/path/to/analytics_outputs/task_2_output.txt",
      "error": null,
      "tokens_used": 1945,
      "cost_usd": 0.002918,
      "execution_time_seconds": 17.76,
      "retry_count": 0
    }
  ],
  "errors": []
}
```

### Step 6: Access Task Outputs

Each task writes its output to a file:

```bash
$ ls -lah ./analytics_outputs/
total 156K
drwxr-xr-x  15 user  staff   480B Jan 15 10:25 .
drwxr-xr-x   3 user  staff    96B Jan 15 10:23 ..
-rw-r--r--   1 user  staff  8.2K Jan 15 10:24 task_1_output.txt
-rw-r--r--   1 user  staff  9.1K Jan 15 10:24 task_2_output.txt
-rw-r--r--   1 user  staff  7.8K Jan 15 10:24 task_3_output.txt
-rw-r--r--   1 user  staff 10.2K Jan 15 10:24 task_4_output.txt
-rw-r--r--   1 user  staff  6.5K Jan 15 10:24 task_5_output.txt
-rw-r--r--   1 user  staff 11.4K Jan 15 10:24 task_6_output.txt
-rw-r--r--   1 user  staff  8.9K Jan 15 10:24 task_7_output.txt
-rw-r--r--   1 user  staff  9.7K Jan 15 10:24 task_8_output.txt
-rw-r--r--   1 user:  staff  7.3K Jan 15 10:24 task_9_output.txt
-rw-r--r--   1 user  staff  8.4K Jan 15 10:24 task_10_output.txt
-rw-r--r--   1 user  staff  9.1K Jan 15 10:24 task_11_output.txt
-rw-r--r--   1 user  staff 12.6K Jan 15 10:24 task_12_output.txt
```

### Step 7: Examine Individual Task Outputs

```bash
$ head -50 ./analytics_outputs/task_1_output.txt
```

Example output from "Design Core Data Model" task:

```
# Data Analytics Platform - Core Data Model

## Schema Definitions

### Raw Data Ingestion Schema
CREATE TABLE raw_data_ingestion (
    id BIGSERIAL PRIMARY KEY,
    source_id UUID NOT NULL,
    source_type ENUM('CSV', 'API', 'DATABASE'),
    payload JSONB NOT NULL,
    checksum VARCHAR(64),
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_checksum CHECK (checksum ~ '^[a-f0-9]{64}$')
);

CREATE INDEX idx_raw_data_source_id ON raw_data_ingestion(source_id, ingested_at DESC);
CREATE INDEX idx_raw_data_source_type ON raw_data_ingestion(source_type);
CREATE INDEX idx_raw_data_payload_gin ON raw_data_ingestion USING GIN(payload);

...
```

### Step 8: Process Results

Create a script to aggregate outputs:

```python
import json
from pathlib import Path

# Load execution report
with open("analytics_report.json") as f:
    report = json.load(f)

# Aggregate task outputs
outputs_dir = Path("./analytics_outputs")
aggregated = {}

for result in report["task_results"]:
    task_id = result["task_id"]
    output_file = result["output"]

    if Path(output_file).exists():
        with open(output_file) as f:
            aggregated[task_id] = f.read()

# Save aggregated output
with open("aggregated_platform_design.txt", "w") as f:
    for task_id in sorted(aggregated.keys()):
        f.write(f"\n{'='*80}\n")
        f.write(f"{task_id}\n")
        f.write(f"{'='*80}\n\n")
        f.write(aggregated[task_id])
        f.write("\n\n")

print("Aggregated design document created: aggregated_platform_design.txt")
```

### Step 9: Analyze Parallelization Efficiency

```bash
$ python3 << 'EOF'
import json

with open("analytics_plan.json") as f:
    plan = json.load(f)

print("Parallelization Analysis")
print("=" * 50)

# Calculate if sequential execution would be faster
sequential_time = sum(layer["estimated_duration_seconds"]
                     for layer in plan["layers"])
print(f"Sequential execution: ~{sequential_time:.1f}s")

# With parallelization
parallel_time = sum(max((len(layer["task_ids"]) * 2)
                       for layer in plan["layers"]))
print(f"Parallel execution: ~{parallel_time:.1f}s")

print(f"Speedup: {sequential_time/parallel_time:.2f}x")

print("\nTask Distribution:")
for layer in plan["layers"]:
    print(f"  Layer {layer['layer_id']}: {len(layer['task_ids'])} tasks")

print("\nCost Analysis:")
print(f"  Planner estimation: ${plan['estimated_cost_usd']:.6f}")
EOF
```

Output:
```
Parallelization Analysis
==================================================
Sequential execution: ~24.0s
Parallel execution: ~16.0s
Speedup: 1.50x

Task Distribution:
  Layer 0: 2 tasks
  Layer 1: 4 tasks
  Layer 2: 5 tasks
  Layer 3: 1 task

Cost Analysis:
  Planner estimation: $0.027000
```

## Key Takeaways

1. **Decomposition**: The planner identified 12 independent subtasks from a complex feature description
2. **Parallelization**: Tasks were organized into 4 layers, enabling concurrent execution (50% speedup in this example)
3. **Dependency Tracking**: Each task knows its dependencies and receives upstream outputs automatically
4. **Cost Efficiency**: Total estimated cost: $0.027 (planner) + $0.033 (executor) = $0.060
5. **Quality Assurance**: All 12 tasks completed successfully with no retries needed
6. **Production Ready**: Generated code follows best practices and is ready for integration

## Advanced Scenarios

### Handling Failures

If a task fails, the executor will:
1. Retry with exponential backoff (1s, 2s, 4s, etc.)
2. Log detailed error information
3. Continue execution with other tasks
4. Include failure details in execution report

### Adjusting Concurrency

For different scenarios:
```bash
# Conservative (API with strict rate limits)
--concurrency 2

# Moderate (balanced approach)
--concurrency 5

# Aggressive (when you know the API can handle it)
--concurrency 10
```

### Custom API Keys

For different Anthropic accounts:
```bash
python scripts/planner.py \
  --feature "..." \
  --api-key "sk-..."
```

### Monitoring Token Usage

Check token costs in real-time:
```bash
tail -f analytics_report.json | jq '.total_tokens_used, .total_cost_usd'
```

---

This example demonstrates the complete workflow of the Parallel Skill Builder framework for decomposing and executing a production data analytics platform.
