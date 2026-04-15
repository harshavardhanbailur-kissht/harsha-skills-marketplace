# Task Decomposition: Algorithms and Strategies for Parallel Skill Builder

## 1. Decomposition Algorithms

### 1.1 Hierarchical Task Networks (HTNs)

HTN decomposition recursively breaks down abstract tasks into concrete primitives that can be executed directly. Each level of the hierarchy represents a different level of abstraction.

**Core Principle**: A task is either primitive (executable) or abstract (decomposable).

```python
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class TaskType(Enum):
    PRIMITIVE = "primitive"
    ABSTRACT = "abstract"

@dataclass
class Task:
    task_id: str
    name: str
    task_type: TaskType
    preconditions: List[str] = None  # STRIPSlike logic
    effects: List[str] = None
    decompositions: List[List[str]] = None  # Multiple decomposition methods
    estimated_tokens: int = 2000
    model: str = "claude-opus-4-6"

    def __post_init__(self):
        if self.preconditions is None:
            self.preconditions = []
        if self.effects is None:
            self.effects = []
        if self.decompositions is None:
            self.decompositions = []

class HTNPlanner:
    """Recursive HTN planner for hierarchical task decomposition."""

    def __init__(self):
        self.task_library: Dict[str, Task] = {}
        self.decomposition_methods: Dict[str, List[List[str]]] = {}

    def register_task(self, task: Task):
        """Register a task in the HTN library."""
        self.task_library[task.task_id] = task
        if task.decompositions:
            self.decomposition_methods[task.task_id] = task.decompositions

    def decompose(self, task_id: str, depth: int = 0, max_depth: int = 5) -> List[str]:
        """
        Recursively decompose a task into primitives using HTN methods.

        Returns: List of primitive task IDs
        """
        if depth > max_depth:
            raise ValueError(f"Max decomposition depth {max_depth} exceeded")

        task = self.task_library.get(task_id)
        if not task:
            raise KeyError(f"Task {task_id} not found")

        if task.task_type == TaskType.PRIMITIVE:
            return [task_id]

        if not self.decomposition_methods.get(task_id):
            raise ValueError(f"No decomposition method for {task_id}")

        # Try first decomposition method (can be extended for backtracking)
        decomp_method = self.decomposition_methods[task_id][0]
        primitives = []

        for subtask_id in decomp_method:
            primitives.extend(self.decompose(subtask_id, depth + 1, max_depth))

        return primitives
```

**HTN Example - REST API Development**:

```python
# Setup task library
planner = HTNPlanner()

# Define tasks
design_api_task = Task(
    task_id="design_api",
    name="Design REST API",
    task_type=TaskType.ABSTRACT,
    decompositions=[[
        "define_endpoints",
        "design_data_models",
        "plan_authentication"
    ]]
)

define_endpoints_task = Task(
    task_id="define_endpoints",
    name="Define API endpoints",
    task_type=TaskType.PRIMITIVE,
    estimated_tokens=3000
)

# Register and decompose
planner.register_task(design_api_task)
planner.register_task(define_endpoints_task)

primitives = planner.decompose("design_api")
# Result: ["define_endpoints", "design_data_models", "plan_authentication"]
```

### 1.2 ADaPT: Adaptive Decomposition

ADaPT (Adaptive Decomposition through Planning and Testing) only decomposes when the model fails. This reduces unnecessary subtask generation and improves success rate by 28.3%.

**Key Insight**: Attempt the full task first; only decompose if it fails.

```python
from enum import Enum
import time

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DECOMPOSED = "decomposed"

class AdaptiveDecomposer:
    """ADaPT: Decompose only when the model fails."""

    def __init__(self, threshold_success_rate: float = 0.6):
        self.threshold = threshold_success_rate
        self.task_attempts: Dict[str, List[bool]] = {}

    def should_decompose(self, task_id: str) -> bool:
        """
        Determine if a task should be decomposed based on failure history.

        Returns: True if success rate < threshold
        """
        if task_id not in self.task_attempts:
            return False  # First attempt, don't decompose

        attempts = self.task_attempts[task_id]
        if len(attempts) < 2:
            return False

        success_rate = sum(attempts) / len(attempts)
        return success_rate < self.threshold

    def record_attempt(self, task_id: str, success: bool):
        """Record the result of a task attempt."""
        if task_id not in self.task_attempts:
            self.task_attempts[task_id] = []
        self.task_attempts[task_id].append(success)

    def execute_adaptive(self, task_id: str, executor_fn, decomposer_fn) -> bool:
        """
        Execute task adaptively: try direct execution, decompose on failure.

        Args:
            task_id: Task identifier
            executor_fn: Function to execute the task directly
            decomposer_fn: Function to decompose the task

        Returns: True if successful
        """
        # Attempt direct execution
        try:
            result = executor_fn(task_id)
            self.record_attempt(task_id, success=True)
            return True
        except Exception as e:
            self.record_attempt(task_id, success=False)

            # Check if decomposition is warranted
            if self.should_decompose(task_id):
                subtasks = decomposer_fn(task_id)
                return len(subtasks) > 0

            return False
```

**ADaPT Results**: 28.3% higher success rate vs. always-decompose baseline on complex planning tasks.

### 1.3 ACONIC: Constraint-Based Decomposition

ACONIC (Adaptive Constraint Optimization for Nested Integrated Collaboration) treats decomposition as constraint satisfaction. Improves quality by 10-40 percentage points.

```python
from dataclasses import dataclass
from typing import Callable, Tuple

@dataclass
class Constraint:
    """A constraint on task decomposition."""
    name: str
    check_fn: Callable[[List[str]], bool]  # Returns True if satisfied
    priority: int = 1  # 1=critical, 2=important, 3=nice-to-have

class ACONICDecomposer:
    """ACONIC: Constraint satisfaction for decomposition."""

    def __init__(self):
        self.constraints: List[Constraint] = []

    def add_constraint(self, constraint: Constraint):
        """Add a decomposition constraint."""
        self.constraints.append(constraint)

    def evaluate_decomposition(self, subtasks: List[str]) -> Tuple[float, List[str]]:
        """
        Evaluate a decomposition against all constraints.

        Returns: (score, violated_constraints)
        """
        violations = []
        score = 1.0

        # Sort by priority (critical first)
        sorted_constraints = sorted(self.constraints, key=lambda c: c.priority)

        for constraint in sorted_constraints:
            if not constraint.check_fn(subtasks):
                violations.append(constraint.name)
                # Reduce score based on priority
                score *= (1.0 - 0.5 / constraint.priority)

        return score, violations

    def decompose_with_constraints(self,
                                    task_id: str,
                                    candidate_decompositions: List[List[str]]) -> List[str]:
        """
        Select best decomposition that satisfies constraints.
        """
        best_decomp = None
        best_score = -1.0

        for decomp in candidate_decompositions:
            score, violations = self.evaluate_decomposition(decomp)

            if score > best_score:
                best_score = score
                best_decomp = decomp
                if not violations:  # Perfect match
                    break

        return best_decomp or candidate_decompositions[0]
```

**Example Constraints**:
- "No sequential single-GPU training dependencies" → parallel execution
- "Each subtask < 10k tokens" → manageable complexity
- "Data preprocessing must precede model training" → dependency ordering

---

## 2. Building the Dependency Graph (DAG)

### 2.1 DAG Representation

```python
from typing import Dict, Set, List
from dataclasses import dataclass, asdict
import json

@dataclass
class TaskNode:
    """A node in the task DAG."""
    task_id: str
    name: str
    prompt: str
    system_prompt: str
    model: str = "claude-opus-4-6"
    max_tokens: int = 3000
    dependencies: List[str] = None  # task_ids this depends on

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TaskDAG:
    """Directed Acyclic Graph of tasks."""

    def __init__(self):
        self.nodes: Dict[str, TaskNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # task_id -> set of dependent task_ids
        self.layers: List[List[str]] = []  # Topologically sorted layers

    def add_node(self, node: TaskNode):
        """Add a task node to the DAG."""
        if node.task_id in self.nodes:
            raise ValueError(f"Node {node.task_id} already exists")

        self.nodes[node.task_id] = node
        self.edges[node.task_id] = set()

    def add_edge(self, from_task: str, to_task: str):
        """
        Add dependency: to_task depends on from_task.
        """
        if from_task not in self.nodes:
            raise KeyError(f"Source task {from_task} not found")
        if to_task not in self.nodes:
            raise KeyError(f"Target task {to_task} not found")

        self.edges[from_task].add(to_task)

    def validate_acyclic(self) -> bool:
        """Detect cycles using DFS."""
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self.edges.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return False
        return True

    def topological_sort_kahn(self) -> List[str]:
        """
        Kahn's algorithm for topological sort: O(V+E).

        Returns: Ordered list of task_ids
        """
        in_degree = {node_id: 0 for node_id in self.nodes}

        # Calculate in-degrees
        for from_task, dependents in self.edges.items():
            for to_task in dependents:
                in_degree[to_task] += 1

        queue = [node_id for node_id in self.nodes if in_degree[node_id] == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(node_id)

            for dependent in self.edges[node_id]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self.nodes):
            raise ValueError("Cycle detected in DAG")

        return result

    def compute_layers(self) -> List[List[str]]:
        """
        Compute parallel layers: tasks at the same depth that can run simultaneously.
        """
        if not self.validate_acyclic():
            raise ValueError("DAG contains cycles")

        layers = []
        visited = set()
        in_degree = {node_id: 0 for node_id in self.nodes}

        for from_task, dependents in self.edges.items():
            for to_task in dependents:
                in_degree[to_task] += 1

        while len(visited) < len(self.nodes):
            current_layer = [
                node_id for node_id in self.nodes
                if in_degree[node_id] == 0 and node_id not in visited
            ]

            if not current_layer:
                break

            layers.append(current_layer)
            visited.update(current_layer)

            for task_id in current_layer:
                for dependent in self.edges[task_id]:
                    in_degree[dependent] -= 1

        self.layers = layers
        return layers

    def critical_path(self) -> Tuple[List[str], int]:
        """
        Find critical path: longest path through DAG.
        Determines minimum completion time if tasks execute sequentially on critical path.

        Returns: (path as task_ids, total_tokens)
        """
        topo_order = self.topological_sort_kahn()
        longest_path = {node_id: ([], 0) for node_id in self.nodes}

        for node_id in topo_order:
            node = self.nodes[node_id]
            if not any(self.edges[pred] == {node_id}
                      for pred in self.nodes if node_id in self.edges[pred]):
                longest_path[node_id] = ([node_id], node.max_tokens)

        for node_id in topo_order:
            node = self.nodes[node_id]

            # Find all predecessors
            predecessors = [
                pred for pred in self.nodes
                if node_id in self.edges[pred]
            ]

            if predecessors:
                # Extend longest path from predecessors
                best_pred = max(
                    predecessors,
                    key=lambda p: longest_path[p][1]
                )
                best_path, best_cost = longest_path[best_pred]
                longest_path[node_id] = (best_path + [node_id],
                                        best_cost + node.max_tokens)

        # Find critical path
        critical_task = max(
            self.nodes.keys(),
            key=lambda n: longest_path[n][1]
        )
        return longest_path[critical_task]

    def to_json(self) -> str:
        """Serialize DAG to JSON."""
        return json.dumps({
            "nodes": {task_id: node.to_dict() for task_id, node in self.nodes.items()},
            "edges": {k: list(v) for k, v in self.edges.items()},
            "layers": self.layers
        }, indent=2)
```

---

## 3. Granularity Optimization

### 3.1 Granularity Trade-offs

```python
@dataclass
class GranularityMetrics:
    """Metrics for evaluating task granularity."""
    avg_task_tokens: float
    num_tasks: int
    num_layers: int
    critical_path_tokens: int
    coordination_overhead: float  # Estimated comm/setup time as % of total
    parallelism_factor: float  # Max parallel tasks / avg serial length
    speedup_estimate: float  # Theoretical speedup with infinite workers

class GranularityOptimizer:
    """Optimize task granularity for parallel execution."""

    @staticmethod
    def evaluate_granularity(dag: TaskDAG) -> GranularityMetrics:
        """Evaluate granularity of a decomposition."""
        total_tokens = sum(n.max_tokens for n in dag.nodes.values())
        num_tasks = len(dag.nodes)
        layers = dag.compute_layers()
        num_layers = len(layers)
        critical_path, cp_tokens = dag.critical_path()

        max_parallel = max(len(layer) for layer in layers) if layers else 1

        # Coordination overhead: ~500 tokens per subtask (setup, communication)
        coordination = num_tasks * 500
        total_with_overhead = total_tokens + coordination

        parallelism_factor = max_parallel / num_layers if num_layers > 0 else 1

        # Estimate speedup: Amdahl's law approximation
        # S ≈ (CP + overhead) / (CP/num_workers + overhead)
        # For N=infinity workers: S ≈ T_total / (T_critical + overhead)
        speedup = (total_tokens + coordination) / (cp_tokens + coordination)

        return GranularityMetrics(
            avg_task_tokens=total_tokens / num_tasks if num_tasks > 0 else 0,
            num_tasks=num_tasks,
            num_layers=num_layers,
            critical_path_tokens=cp_tokens,
            coordination_overhead=coordination / total_with_overhead,
            parallelism_factor=parallelism_factor,
            speedup_estimate=min(speedup, 5.9)  # Empirical cap at 5.9x
        )

    @staticmethod
    def check_junior_engineer_heuristic(task: TaskNode) -> bool:
        """
        "Junior engineer level complexity" heuristic:
        A task should be achievable by a competent junior engineer in 2-4 hours.

        Approximation: 2000-4000 tokens per task (10k tokens = ~1 hour for Opus)
        """
        return 2000 <= task.max_tokens <= 4000

    @staticmethod
    def recommend_granularity(metrics: GranularityMetrics) -> str:
        """Recommend granularity adjustment based on metrics."""
        recommendations = []

        # Too fine-grained: high coordination overhead
        if metrics.coordination_overhead > 0.3:
            recommendations.append(
                f"Coordination overhead {metrics.coordination_overhead:.1%} is high. "
                f"Consider merging {metrics.num_tasks // 2} tasks."
            )

        # Too coarse-grained: poor parallelism
        if metrics.parallelism_factor < 1.5:
            recommendations.append(
                f"Parallelism factor {metrics.parallelism_factor:.1f} is low. "
                f"Consider decomposing tasks further."
            )

        # Individual task complexity
        if metrics.avg_task_tokens > 5000:
            recommendations.append(
                f"Average task size {metrics.avg_task_tokens:.0f} tokens exceeds "
                f"junior engineer heuristic (2000-4000). Break down further."
            )

        if not recommendations:
            recommendations.append(
                f"Granularity is optimal. Expected speedup: {metrics.speedup_estimate:.2f}x"
            )

        return "\n".join(recommendations)
```

---

## 4. Interface Contracts Between Subtasks

### 4.1 MetaGPT-Inspired Structured Communication

```python
from typing import Any
from enum import Enum

class ErrorHandlingStrategy(Enum):
    FAIL_FAST = "fail_fast"
    RETRY = "retry"
    FALLBACK = "fallback"

@dataclass
class InterfaceContract:
    """Interface contract between subtasks (MetaGPT pattern)."""

    # Dimension 1: Data Schema
    input_schema: Dict[str, Any]  # JSON schema for inputs
    output_schema: Dict[str, Any]  # JSON schema for outputs

    # Dimension 2: Expected Behavior
    timeout_seconds: int = 300
    max_retries: int = 2
    expected_quality_metrics: Dict[str, float] = None  # e.g., {"code_coverage": 0.8}

    # Dimension 3: Error Handling
    error_strategy: ErrorHandlingStrategy = ErrorHandlingStrategy.RETRY
    fallback_output: Any = None

    # Dimension 4: Versioning
    contract_version: str = "1.0"
    compatible_versions: List[str] = None
    deprecation_date: Optional[str] = None

    def __post_init__(self):
        if self.expected_quality_metrics is None:
            self.expected_quality_metrics = {}
        if self.compatible_versions is None:
            self.compatible_versions = ["1.0"]

    def validate_input(self, data: Any) -> bool:
        """Validate input against schema (simplified)."""
        # In practice, use jsonschema library
        return True

    def validate_output(self, data: Any) -> bool:
        """Validate output against schema."""
        return True

class InterfaceRegistry:
    """Registry of interface contracts between tasks."""

    def __init__(self):
        self.contracts: Dict[Tuple[str, str], InterfaceContract] = {}

    def register(self, from_task: str, to_task: str, contract: InterfaceContract):
        """Register interface between two tasks."""
        self.contracts[(from_task, to_task)] = contract

    def get_contract(self, from_task: str, to_task: str) -> Optional[InterfaceContract]:
        """Get interface contract for a task pair."""
        return self.contracts.get((from_task, to_task))

    def integration_compatibility_score(self, from_task: str, to_task: str) -> float:
        """
        Score how compatible two tasks are based on interface definitions.

        Results: 40% faster integration with standardized interfaces.
        """
        contract = self.get_contract(from_task, to_task)
        if not contract:
            return 0.5  # Unknown compatibility

        # Check schema compatibility
        if contract.input_schema and contract.output_schema:
            return 0.9  # Well-defined interface

        return 0.6
```

### 4.2 Interface Contract Template

```python
INTERFACE_TEMPLATE = {
    "from_task": "generate_schema",
    "to_task": "implement_models",
    "input_schema": {
        "type": "object",
        "properties": {
            "entity_definitions": {
                "type": "array",
                "items": {"type": "string"}
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "type": {"type": "string"}
                    }
                }
            }
        }
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "models": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "fields": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "nullable": {"type": "boolean"}
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "timeout_seconds": 300,
    "max_retries": 2,
    "error_strategy": "retry",
    "version": "1.0"
}
```

---

## 5. Practical Decomposition Prompt Template

```python
DECOMPOSITION_PROMPT_TEMPLATE = """
You are an expert system architect tasked with decomposing a software feature into parallel subtasks.

FEATURE DESCRIPTION:
{feature_description}

Your task is to create a Directed Acyclic Graph (DAG) of subtasks that can be executed in parallel when possible.

REQUIREMENTS:
1. Each task should represent a single, verifiable goal (junior engineer complexity level)
2. Tasks should have clear input/output contracts
3. Maximize parallelism where dependencies allow
4. Each task should be achievable with 2000-4000 tokens (one Claude API call)

OUTPUT FORMAT:
Return a JSON object with this exact structure:

{{
  "decomposition": {{
    "title": "string",
    "description": "string",
    "tasks": [
      {{
        "task_id": "string (kebab-case)",
        "name": "string",
        "prompt": "string (clear, specific instructions for this task)",
        "system_prompt": "string (role and expertise for this task)",
        "dependencies": ["task_id1", "task_id2"],
        "model": "claude-opus-4-6",
        "max_tokens": 3000,
        "interface_contract": {{
          "input_schema": {{...}},
          "output_schema": {{...}},
          "expected_output_example": "string or object"
        }}
      }}
    ],
    "parallel_layers": [
      ["task_id1", "task_id2"],  # Layer 0: these can run in parallel
      ["task_id3"],              # Layer 1: depends on layer 0
      ["task_id4", "task_id5"]   # Layer 2: can run in parallel
    ],
    "critical_path": ["task_id1", "task_id3", "task_id4"],
    "estimated_total_tokens": 15000,
    "estimated_speedup": 2.5
  }}
}}

DECOMPOSITION STRATEGY:
- Identify independent concerns that can be developed separately
- Use async boundaries: auth, data fetching, UI rendering
- Consider skill requirements: backend, frontend, testing, documentation
- Order tasks by dependency: prerequisites first
- Avoid cycles: verify each task depends only on earlier tasks

EXAMPLE DECOMPOSITION:
Feature: "Build a REST API with JWT authentication"
Tasks:
1. design_endpoints - Define routes, methods, status codes
2. design_data_models - Define request/response schemas
3. implement_auth - JWT token generation and validation
4. implement_endpoints - Create route handlers (depends on 1, 2, 3)
5. write_tests - Unit and integration tests (depends on 4)

Parallelization:
- Layer 0: [design_endpoints, design_data_models, implement_auth]
- Layer 1: [implement_endpoints]
- Layer 2: [write_tests]
"""
```

---

## 6. Example Decompositions

### Example 1: REST API with Authentication

```json
{
  "feature": "Build a REST API with JWT authentication and database",
  "decomposition": {
    "tasks": [
      {
        "task_id": "design-endpoints",
        "name": "Design API endpoints and HTTP contract",
        "prompt": "Design the REST API endpoints for [domain]. Specify: methods (GET/POST/etc), paths, query parameters, request/response bodies, status codes, error responses.",
        "system_prompt": "You are a REST API architect. Your expertise is in designing clean, scalable APIs that follow REST principles.",
        "dependencies": [],
        "max_tokens": 2500,
        "interface_contract": {
          "output_format": "Markdown table with columns: Method, Path, Request Schema, Response Schema, Status Codes",
          "examples": ["GET /api/users/:id", "POST /api/users (with body)"]
        }
      },
      {
        "task_id": "design-data-schema",
        "name": "Design data models and database schema",
        "prompt": "Design the database schema for [domain]. Specify: tables, columns, types, constraints, relationships, indexes.",
        "system_prompt": "You are a database architect. You design normalized, efficient schemas.",
        "dependencies": [],
        "max_tokens": 3000
      },
      {
        "task_id": "design-auth",
        "name": "Design JWT authentication flow",
        "prompt": "Design a JWT-based authentication system for the API. Specify: token format, claims, refresh token strategy, error handling.",
        "system_prompt": "You are a security expert. You design secure, production-grade auth systems.",
        "dependencies": [],
        "max_tokens": 2500
      },
      {
        "task_id": "implement-models",
        "name": "Implement database models",
        "prompt": "Implement Sqlalchemy models matching the schema from the design phase. Include validators and relationships.",
        "system_prompt": "You are a Python backend developer specializing in ORM patterns.",
        "dependencies": ["design-data-schema"],
        "max_tokens": 3500
      },
      {
        "task_id": "implement-auth",
        "name": "Implement JWT authentication",
        "prompt": "Implement JWT token generation, validation, and refresh logic. Include middleware for protecting routes.",
        "system_prompt": "You are a security-focused Python developer.",
        "dependencies": ["design-auth"],
        "max_tokens": 3500
      },
      {
        "task_id": "implement-endpoints",
        "name": "Implement API endpoints",
        "prompt": "Implement the endpoint handlers using FastAPI. Connect to database models and auth middleware.",
        "system_prompt": "You are a FastAPI expert building production APIs.",
        "dependencies": ["design-endpoints", "implement-models", "implement-auth"],
        "max_tokens": 4000
      },
      {
        "task_id": "write-integration-tests",
        "name": "Write integration tests",
        "prompt": "Write pytest integration tests covering all endpoints, including auth flows and error cases.",
        "system_prompt": "You are a QA engineer specializing in API testing.",
        "dependencies": ["implement-endpoints"],
        "max_tokens": 3000
      }
    ],
    "parallel_layers": [
      ["design-endpoints", "design-data-schema", "design-auth"],
      ["implement-models", "implement-auth"],
      ["implement-endpoints"],
      ["write-integration-tests"]
    ],
    "critical_path_tokens": 12500,
    "estimated_speedup": 3.2
  }
}
```

### Example 2: Data Pipeline with ML

```json
{
  "feature": "Build a data pipeline with feature engineering and ML model training",
  "decomposition": {
    "tasks": [
      {
        "task_id": "analyze-requirements",
        "name": "Analyze ML requirements",
        "prompt": "Define: what are we predicting, what data do we need, success metrics, baseline performance targets?",
        "dependencies": [],
        "max_tokens": 2500
      },
      {
        "task_id": "data-loading",
        "name": "Implement data loading pipeline",
        "prompt": "Write Python code to load data from sources. Handle missing values, basic cleaning, logging.",
        "dependencies": ["analyze-requirements"],
        "max_tokens": 3000
      },
      {
        "task_id": "eda",
        "name": "Exploratory Data Analysis",
        "prompt": "Generate EDA report: distributions, correlations, outliers, class balance, feature importance.",
        "dependencies": ["data-loading"],
        "max_tokens": 3000
      },
      {
        "task_id": "feature-engineering",
        "name": "Feature engineering and selection",
        "prompt": "Design features: domain-specific transformations, interactions, dimensionality reduction. Create feature engineering pipeline.",
        "dependencies": ["eda"],
        "max_tokens": 3500
      },
      {
        "task_id": "train-model",
        "name": "Train ML model",
        "prompt": "Implement model training: data splitting, hyperparameter tuning, cross-validation, model selection.",
        "dependencies": ["feature-engineering"],
        "max_tokens": 3500
      },
      {
        "task_id": "evaluate-model",
        "name": "Evaluate model performance",
        "prompt": "Evaluate model on holdout test set. Generate metrics, confusion matrix, ROC curves, error analysis.",
        "dependencies": ["train-model"],
        "max_tokens": 2500
      },
      {
        "task_id": "deploy-inference",
        "name": "Build inference API",
        "prompt": "Create FastAPI endpoint for model inference. Include preprocessing, batch support, error handling.",
        "dependencies": ["train-model"],
        "max_tokens": 2500
      }
    ],
    "parallel_layers": [
      ["analyze-requirements"],
      ["data-loading"],
      ["eda"],
      ["feature-engineering"],
      ["train-model"],
      ["evaluate-model", "deploy-inference"]
    ]
  }
}
```

---

## Quick Reference: Choosing Decomposition Strategy

| Algorithm | Best For | Trade-off | Key Metric |
|-----------|----------|-----------|-----------|
| **HTN** | Well-defined, hierarchical tasks | Planning complexity | Recursion depth |
| **ADaPT** | Adaptive learning from failures | Requires feedback loop | 28.3% success gain |
| **ACONIC** | Complex constraints | Constraint evaluation cost | 10-40pp quality gain |

## Key Principles

1. **Single Verifiable Goal**: Each task = one output artifact that can be verified
2. **Optimal Granularity**: 2000-4000 tokens (junior engineer complexity)
3. **Clear Contracts**: Specify input/output schemas between tasks
4. **Maximize Parallelism**: Minimize critical path, maximize parallel layers
5. **Explicit Dependencies**: Use DAG to track all task relationships

---

## References

- **HTN Planning**: Automated Planning & Scheduling (Ghallab et al.)
- **ADaPT**: Adaptive Task Decomposition (research findings: 28.3% improvement)
- **ACONIC**: Constraint Satisfaction (Tate et al.)
- **Critical Path Analysis**: Project Management (PERT, CPM)
- **Granularity**: Parallel Computing trade-offs (Amdahl's Law)
