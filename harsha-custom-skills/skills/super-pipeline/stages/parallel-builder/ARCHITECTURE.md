# Parallel Skill Builder - Architecture & Implementation Notes

## Design Philosophy

The Parallel Skill Builder is built on three core principles:

1. **Maximized Parallelization**: Identify and execute independent tasks concurrently
2. **Production Quality**: Robust error handling, retry logic, and comprehensive logging
3. **Cost Optimization**: Efficient prompt engineering and token tracking

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Parallel Skill Builder                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐              ┌──────────────────────┐ │
│  │   Planner Module     │              │  Executor Module     │ │
│  │ (planner.py)         │              │ (executor.py)        │ │
│  │                      │              │                      │ │
│  │ Input:               │              │ Input:               │ │
│  │ - Feature Description│              │ - Execution Plan     │ │
│  │                      │              │                      │ │
│  │ Output:              │              │ Output:              │ │
│  │ - Execution Plan     │              │ - Task Outputs       │ │
│  │                      │              │ - Execution Report   │ │
│  └──────────────────────┘              └──────────────────────┘ │
│           │                                       │               │
│           ├─ Claude Opus 4.6                      ├─ AsyncIO      │
│           ├─ Kahn's Algorithm                     ├─ Semaphores   │
│           ├─ Topological Sort                     ├─ Retries      │
│           └─ Prompt Generation                    └─ Token Tracking│
│                                                                   │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │                   Anthropic SDK (AsyncAnthropic)             ││
│  │              - Rate limiting via Semaphore                   ││
│  │              - Token usage tracking                          ││
│  │              - Cost calculation                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Planner Module (planner.py)

#### Responsibilities
- Parse feature descriptions using Claude Opus 4.6
- Decompose features into atomic subtasks
- Build dependency DAG from Claude's response
- Compute execution layers using topological sort
- Generate optimized prompts for executor
- Estimate costs and tokens

#### Key Classes

**TaskDecomposer**
```python
class TaskDecomposer:
    async def decompose_feature(feature: str) -> ExecutionPlan
    async def _generate_task_prompts(tasks: list, feature: str)
    def _compute_execution_layers(tasks: list) -> list[ExecutionLayer]
```

**Data Classes**
```python
@dataclass
class SubTask:
    id: str
    title: str
    description: str
    dependencies: list[str]
    prompt: str
    contract: InterfaceContract

@dataclass
class InterfaceContract:
    input_spec: dict[str, Any]
    output_spec: dict[str, Any]
    constraints: list[str]

@dataclass
class ExecutionLayer:
    layer_id: int
    task_ids: list[str]
    estimated_duration_seconds: float

@dataclass
class ExecutionPlan:
    feature_description: str
    tasks: list[SubTask]
    layers: list[ExecutionLayer]
    estimated_total_tokens: int
    estimated_cost_usd: float
```

#### Algorithms

**Kahn's Algorithm (Topological Sort)**
```
1. Calculate in-degree for each vertex (task)
2. Enqueue all vertices with in-degree 0 → Layer 0
3. For each vertex in queue:
   - Add to current layer
   - For each dependent vertex:
     - Decrease in-degree by 1
     - If in-degree becomes 0, enqueue for next layer
4. Repeat until all vertices processed
```

Time Complexity: O(V + E) where V=tasks, E=dependencies
Space Complexity: O(V + E)

#### JSON Extraction Strategy
```python
def _extract_json(text: str) -> dict:
    # Strategy 1: Extract from markdown code block
    if "```json...```" found:
        return parse_inner_json()

    # Strategy 2: Extract raw JSON object
    find_first_"{" and matching_"}"

    # Handles Claude's varied response formatting
```

#### Prompt Engineering for Opus

System prompt designed to:
1. Frame Claude as an expert software architect
2. Request specific JSON structure with example
3. Emphasize atomic, independently executable tasks
4. Include token estimation guidance
5. Maximize parallelization identification

### 2. Executor Module (executor.py)

#### Responsibilities
- Load and validate execution plans
- Execute tasks respecting layer dependencies
- Manage concurrent execution with rate limiting
- Inject dependency outputs into downstream tasks
- Track tokens and costs per task
- Implement retry logic with exponential backoff
- Produce comprehensive execution reports

#### Key Classes

**TaskExecutor**
```python
class TaskExecutor:
    async def execute_plan(plan_path: str, output_dir: Path) -> ExecutionReport
    async def execute_task(task_id: str, tasks_by_id: dict) -> TaskResult
    def _load_plan(plan_path: str) -> dict[str, Any]
```

**Data Classes**
```python
@dataclass
class TaskResult:
    task_id: str
    success: bool
    output: str
    error: Optional[str]
    tokens_used: int
    cost_usd: float
    execution_time_seconds: float
    retry_count: int

@dataclass
class ExecutionReport:
    plan_path: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_tokens_used: int
    total_cost_usd: float
    total_execution_time_seconds: float
    task_results: list[TaskResult]
    errors: list[str]
```

#### Concurrency Model

**Semaphore-Based Rate Limiting**
```python
semaphore = asyncio.Semaphore(concurrency)

async def execute_task(...):
    async with semaphore:
        # This task's execution is counted against the limit
        response = await self.client.messages.create(...)
        # Semaphore automatically queues excess tasks
```

Advantages:
- Simple and effective rate limiting
- Built into asyncio
- Configurable per command-line argument
- Prevents API overload

#### Layer Execution Flow

```python
for layer in plan["layers"]:
    # Execute all tasks in layer in parallel
    results = await asyncio.gather(
        *[execute_task(task_id) for task_id in layer["task_ids"]]
    )

    # Move to next layer only after all tasks in current layer complete
    # This ensures dependency order is respected
```

#### Dependency Injection

```python
# Build prompt with dependency outputs
prompt = task_def["prompt"]

if dependencies:
    dependency_context = "DEPENDENCY OUTPUTS:\n"
    for dep_id in dependencies:
        dependency_context += f"\n{dep_id} output:\n{task_outputs[dep_id]}\n"
    prompt = f"{dependency_context}\n\n{prompt}"
```

Enables downstream tasks to:
- Reference upstream results
- Make data-driven decisions
- Adapt their approach based on dependency outputs

#### Retry Strategy

**Exponential Backoff**
```
Attempt 1: Immediate (0s)
Attempt 2: Wait 1.0s
Attempt 3: Wait 2.0s
Attempt 4: Wait 4.0s
Attempt 5: Wait 8.0s
...
Attempt N: Wait 2^(N-1) * initial_delay seconds
```

Handles:
- Transient API errors
- Rate limiting (429 responses)
- Temporary network issues
- Claude overload

#### File-Based Output Architecture

**Why Not Coordinator Pattern?**
```
❌ Coordinator (Anti-pattern):
   Task 1 → Coordinator
   Task 2 → Coordinator
   Task 3 → Coordinator
   Bottleneck: All outputs routed through single process

✓ File-Based (Optimal):
   Task 1 → task_1_output.txt
   Task 2 → task_2_output.txt
   Task 3 → task_3_output.txt
   Benefits: Scalable, no bottleneck, easy debugging
```

#### Token Tracking

**Per-Task Metrics**
```python
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
total_tokens = input_tokens + output_tokens

cost = (input_tokens * INPUT_TOKEN_COST +
        output_tokens * OUTPUT_TOKEN_COST)
```

**Cost Models**
```python
# Sonnet 4.6
INPUT_TOKEN_COST = 3 / 1_000_000      # $3 per 1M input tokens
OUTPUT_TOKEN_COST = 15 / 1_000_000    # $15 per 1M output tokens

# Opus 4.6 (in planner)
INPUT_TOKEN_COST = 15 / 1_000_000     # $15 per 1M input tokens
OUTPUT_TOKEN_COST = 45 / 1_000_000    # $45 per 1M output tokens
```

## Data Flow

### Planning Phase

```
Feature Description
    ↓
[Planner.decompose_feature]
    ↓
AsyncAnthropic.messages.create()
    ↓
Claude Opus 4.6 Analysis
    ↓
JSON Response (tasks with dependencies)
    ↓
[Planner._extract_json]
    ↓
Structured Task List
    ↓
[Planner._compute_execution_layers]
    ↓
Kahn's Algorithm
    ↓
Execution Layers (parallel groups)
    ↓
[Planner._generate_task_prompts]
    ↓
Optimized Prompts for Sonnet
    ↓
[Planner.save_plan]
    ↓
plan.json (Execution Plan)
```

### Execution Phase

```
plan.json (Execution Plan)
    ↓
[Executor.execute_plan]
    ↓
[Executor._load_plan] - Validation
    ↓
For each layer:
    ↓
[asyncio.gather] - Parallel execution
    ↓
For each task:
    ├─ [Executor.execute_task] (with Semaphore)
    ├─ Dependency Injection
    ├─ AsyncAnthropic.messages.create()
    ├─ Claude Sonnet 4.6 Execution
    ├─ Retry Logic (exponential backoff)
    ├─ Token Tracking
    ├─ Output File Writing
    └─ TaskResult
    ↓
ExecutionReport
    ↓
[Executor.save_report]
    ↓
execution_report.json
```

## Error Handling Strategy

### Planner Errors

1. **JSON Parsing Failures**
   - Strategy: Multiple extraction methods
   - Fallback: Try markdown blocks, then raw JSON
   - Result: Clear error message if all methods fail

2. **API Errors**
   - Rate limiting (429): Let AsyncAnthropic handle
   - Authentication (401): Fail fast with clear message
   - Server errors (5xx): Propagate up

3. **Validation Errors**
   - Circular dependencies: Log warning, continue
   - Invalid task structure: Raise ValueError

### Executor Errors

1. **Plan Loading Errors**
   - Missing file: FileNotFoundError with path
   - Invalid JSON: JSONDecodeError with context
   - Invalid structure: ValueError with missing fields

2. **Task Execution Errors**
   - Network errors: Retry with exponential backoff
   - API errors: Retry, then fail gracefully
   - Output write errors: Log and continue

3. **Graceful Degradation**
   - Partial failures: Continue with other layers
   - Continue with available results
   - Report failures in execution_report.json

## Performance Characteristics

### Time Complexity

**Planner**
```
O(T) where T = number of tasks extracted
- JSON extraction: O(|response|)
- Topological sort: O(T + D) where D = dependencies
- Prompt generation: O(T)
Total: O(T + D + |response|)
```

**Executor**
```
O(L * max(task_times)) where L = number of layers
- Sequential layer execution: L iterations
- Parallel within layer: max task time (not sum)
- Token tracking: O(1) per task
Total: Linear in layers, parallelized within layers
```

### Space Complexity

**Planner**: O(T + D)
- Store all tasks and dependencies

**Executor**: O(T + outputs)
- Store task outputs, execution results

### Typical Metrics

```
Feature Decomposition: 2-5 seconds
Average Tasks Generated: 8-15
Execution Layers: 3-5

Per-Task Execution Time: 2-20 seconds
Concurrent Tasks: limited by semaphore (default 5)
Layer Parallelization Speedup: 1.5-3x depending on dependencies
```

## Security Considerations

### API Key Management
- Read from ANTHROPIC_API_KEY environment variable
- Optional --api-key CLI argument (use with caution)
- Never log or display API keys

### Output Files
- Written to specified output directory
- No sensitive data in task prompts (user responsibility)
- Reported in execution_report.json with absolute paths

### Dependency Injection
- Injects upstream outputs into downstream prompts
- Assumes outputs are safe to include
- User responsible for sanitizing if needed

## Testing Strategy

### Unit Tests (should be added)
```python
def test_kahns_algorithm():
    """Test topological sort correctness"""

def test_json_extraction():
    """Test various JSON response formats"""

def test_cost_calculation():
    """Test token to cost conversion"""

def test_retry_logic():
    """Test exponential backoff behavior"""
```

### Integration Tests (should be added)
```python
async def test_full_decomposition_flow():
    """Test complete planner flow"""

async def test_full_execution_flow():
    """Test complete executor flow"""

async def test_dependency_injection():
    """Test downstream tasks receive upstream outputs"""
```

### Manual Testing
```bash
# Quick test with small feature
python planner.py --feature "Build a simple calculator"

# Test executor with generated plan
python executor.py --plan plan.json --output-dir outputs
```

## Future Enhancements

1. **Distributed Execution**
   - Multiple machines executing tasks in parallel
   - Task state persistence across machines

2. **Advanced Caching**
   - Prompt caching (mentioned in requirements, ready for implementation)
   - Results caching for identical subtasks

3. **Adaptive Concurrency**
   - Automatic semaphore tuning based on API responses
   - Dynamic adjustment for rate limit headers

4. **Better Prompt Optimization**
   - Few-shot examples in system prompt
   - Chain-of-thought prompting for complex tasks

5. **Output Aggregation**
   - Automated report generation from task outputs
   - Integration with external tools (Github, Notion, etc.)

6. **Monitoring & Observability**
   - Prometheus metrics export
   - Structured logging for log aggregation
   - Task execution timeline visualization

## Configuration & Tuning

### Recommended Settings

**Conservative (cost-focused)**
```bash
--concurrency 2
--max-retries 5
```

**Balanced (default)**
```bash
--concurrency 5
--max-retries 3
```

**Aggressive (speed-focused)**
```bash
--concurrency 10
--max-retries 1
```

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-...           # Anthropic API key
PYTHONUNBUFFERED=1                 # Force unbuffered output
LOG_LEVEL=DEBUG                    # Logging level
```

## Deployment Considerations

### Docker
```dockerfile
FROM python:3.10-slim
RUN pip install anthropic==0.28.0
COPY scripts/ /app/
ENTRYPOINT ["python", "/app/planner.py"]
```

### CI/CD
- Run planner as preprocessing step
- Run executor with generated plan
- Archive outputs and reports

### Monitoring
- Log all API calls
- Track token usage trends
- Alert on unusual costs

---

This architecture document provides the technical foundation for understanding, maintaining, and extending the Parallel Skill Builder framework.
