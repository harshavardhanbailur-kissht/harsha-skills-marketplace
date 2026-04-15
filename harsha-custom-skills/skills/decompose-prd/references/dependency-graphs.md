# Dependency Graph Generation & Analysis

## Overview

Once a PRD is decomposed into tasks, the dependency graph engine constructs a Directed Acyclic Graph (DAG) representing task dependencies and execution constraints. This graph enables:

- **Execution ordering**: Topological sort to determine which tasks can run first
- **Parallelization**: Identify tasks that can run concurrently
- **Critical path analysis**: Find the bottleneck path that determines minimum project duration
- **Bottleneck identification**: Tasks with many dependents that block others
- **Effort estimation**: Layer-based estimation accounting for parallelization

## DAG Construction Algorithm

### Dependency Types

Three types of dependencies define the task graph:

```python
DependencyType = {
    "hard": {
        "definition": "Task B cannot start until Task A is complete",
        "reason": "B needs A's output as input (code, data, specification)",
        "impact": "B is blocked until A finishes; critical path contributor",
        "example": "T-2.1.2 (token service) depends on T-2.1.1 (auth handler)"
    },
    "soft": {
        "definition": "Task B is preferred after Task A, but can start earlier if needed",
        "reason": "B benefits from A's context (e.g., design decision) but not strictly required",
        "impact": "Suggests optimal ordering, but can be overridden if B's output is needed urgently",
        "example": "T-3.1.2 (MFA setup) prefers T-3.1.1 (library integration) completed first"
    },
    "resource": {
        "definition": "Task A and Task B share a resource and should not run concurrently",
        "reason": "Both modify same file, API endpoint, database schema, etc.",
        "impact": "Creates serialization constraint; limits parallelism",
        "example": "Two tasks modifying auth.config.ts → serialize to avoid merge conflicts"
    }
}
```

### Dependency Extraction Algorithm

```python
def extract_task_dependencies(task: Task) -> Dict[str, List[str]]:
    """
    Extract all dependencies for a given task.
    Returns mapping of dependency_type -> list of prerequisite task IDs
    """
    dependencies = {
        "hard": [],
        "soft": [],
        "resource": []
    }

    # 1. Explicit dependencies from task specification
    dependencies["hard"].extend(task.prerequisite_tasks)

    # 2. Implicit dependencies: task's inputs are other task's outputs
    for other_task in all_tasks:
        if other_task.id == task.id:
            continue

        # Check if other_task produces files that this task needs
        other_outputs = set(other_task.expected_output.files)
        this_inputs = set(task.inputs.required_files)

        if other_outputs & this_inputs:  # Intersection
            dependencies["hard"].append(other_task.id)

    # 3. Feature-level dependencies: all tasks in a feature depend on prior feature
    # (if features have explicit ordering)
    if task.feature_id in feature_ordering:
        prior_feature = feature_ordering[task.feature_id]
        if prior_feature:
            prior_tasks = get_tasks_for_feature(prior_feature)
            for prior_task in prior_tasks:
                dependencies["soft"].append(prior_task.id)

    # 4. Infrastructure dependencies: all tasks that touch security, infra, etc.
    # should run after INFRA epics
    if is_user_facing_task(task):
        infra_tasks = get_tasks_for_epic("INFRA")
        if infra_tasks:
            dependencies["hard"].extend([t.id for t in infra_tasks])

    # 5. Resource conflicts: tasks modifying same file
    for other_task in all_tasks:
        this_files = set(task.expected_output.files)
        other_files = set(other_task.expected_output.files)

        if this_files & other_files:
            dependencies["resource"].append(other_task.id)

    # 6. Remove transitive dependencies (if A → B → C, don't include A → C)
    dependencies["hard"] = remove_transitive_dependencies(dependencies["hard"])

    return dependencies


def remove_transitive_dependencies(deps: List[str]) -> List[str]:
    """
    Remove transitive dependencies to keep graph minimal.
    If A depends on B and B depends on C, A depends on C implicitly
    through B; no need for direct A → C edge.
    """
    # Build dependency chains
    chains = {}
    for dep_id in deps:
        chains[dep_id] = get_transitive_deps(dep_id)

    # If dep1 is reachable from any other dep through dep chains, remove it
    minimal = []
    for dep1 in deps:
        is_transitive = False
        for dep2 in deps:
            if dep1 == dep2:
                continue
            if dep1 in chains.get(dep2, []):
                is_transitive = True
                break
        if not is_transitive:
            minimal.append(dep1)

    return minimal
```

### DAG Validation: Cycle Detection

```python
def detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Detect cycles in the dependency graph using DFS.
    If cycles found, return them; if none, return empty list.

    Cycles indicate logical errors: task A needs B, B needs A.
    This is usually a sign that tasks are too coarse-grained.
    """
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node: str, path: List[str]) -> bool:
        visited.add(node)
        recursion_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in recursion_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
                return True

        path.pop()
        recursion_stack.remove(node)
        return False

    for task_id in graph:
        if task_id not in visited:
            dfs(task_id, [])

    return cycles


def resolve_cycle(cycle: List[str]) -> str:
    """
    Suggest resolution for a detected cycle.
    Common causes:
    1. Tasks are too coarse-grained; split one task
    2. Dependency is incorrect; should be soft not hard
    3. Architectural issue; need redesign
    """
    if len(cycle) == 2:
        # Two tasks depend on each other
        return f"Circular dependency: {cycle[0]} ← → {cycle[1]}. Likely tasks too coarse-grained; split."
    else:
        # Longer cycle
        return f"Circular dependency chain: {' ← '.join(cycle)}. Review task decomposition."
```

## Topological Sorting

Topological sort produces a linear ordering of tasks such that for every dependency, the predecessor is ordered before the successor. This ordering determines valid execution sequences.

```python
def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """
    Kahn's algorithm for topological sort.
    Returns a valid execution order where dependencies are respected.
    """
    from collections import deque

    # Calculate in-degree for each node
    in_degree = {task: 0 for task in graph}
    adjacency = {task: [] for task in graph}

    for task, deps in graph.items():
        for dep in deps:
            adjacency[dep].append(task)
            in_degree[task] += 1

    # Initialize queue with tasks having no dependencies
    queue = deque([task for task in graph if in_degree[task] == 0])
    sorted_list = []

    while queue:
        task = queue.popleft()
        sorted_list.append(task)

        # For each dependent of this task
        for dependent in adjacency[task]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(sorted_list) != len(graph):
        # Cycle detected (incomplete sort)
        raise ValueError("Cycle detected in dependency graph")

    return sorted_list
```

## Layer Assignment for Parallel Execution

Rather than executing tasks strictly sequentially, we assign tasks to execution layers, where all tasks in a layer can run in parallel (given sufficient agent capacity).

```python
def assign_layers(graph: Dict[str, List[str]]) -> Dict[int, List[str]]:
    """
    Assign each task to a layer (depth) such that:
    - Layer 0: Tasks with no dependencies (can start immediately)
    - Layer N: Tasks whose dependencies are all in layers 0 through N-1

    Returns mapping of layer_number -> list of task IDs
    """
    layers = {}
    task_layers = {}

    # Initialize: tasks with no dependencies are in layer 0
    layer_0 = [task for task in graph if len(graph[task]) == 0]
    layers[0] = layer_0
    for task in layer_0:
        task_layers[task] = 0

    current_layer = 1

    while len(task_layers) < len(graph):
        # Find tasks whose dependencies are all assigned to layers < current_layer
        next_layer_tasks = []

        for task in graph:
            if task in task_layers:
                continue  # Already assigned

            deps = graph[task]
            if all(dep in task_layers for dep in deps):
                # All dependencies assigned; this task can go in current layer
                max_dep_layer = max(task_layers[dep] for dep in deps)

                if max_dep_layer == current_layer - 1:
                    # Dependencies are all in previous layer
                    next_layer_tasks.append(task)

        if not next_layer_tasks:
            # No progress made; break to avoid infinite loop
            break

        layers[current_layer] = next_layer_tasks
        for task in next_layer_tasks:
            task_layers[task] = current_layer

        current_layer += 1

    return layers


def visualize_layers(layers: Dict[int, List[str]]):
    """Print layer structure for visualization"""
    for layer_num in sorted(layers.keys()):
        tasks = layers[layer_num]
        print(f"Layer {layer_num} ({len(tasks)} tasks, can run in parallel):")
        for task in tasks:
            print(f"  - {task}")
        print()
```

### Example Layer Assignment

```
Original tasks: T-1.1.1 → T-1.1.2 → T-1.1.3 (sequential)
               T-2.1.1 → T-2.1.2 (sequential, independent from above)
               T-3.1.1 → T-3.1.2 → T-3.1.3 (sequential, independent)

Layer Assignment:
Layer 0: [T-1.1.1, T-2.1.1, T-3.1.1]  ← Can all start in parallel
Layer 1: [T-1.1.2, T-2.1.2, T-3.1.2]  ← Can all start once their Layer 0 deps finish
Layer 2: [T-1.1.3, T-3.1.3]            ← Final tasks
Layer 3: []                             ← All done

Sequential estimate: 6 tasks × 1 unit = 6 units
Parallelized estimate: 3 + 3 + 2 = 8 units (but tasks run in parallel, so actual time is max per layer)
```

## Critical Path Analysis

The critical path is the longest dependency chain from start to finish. Any delay in a critical path task delays the entire project.

```python
def find_critical_path(graph: Dict[str, List[str]], task_effort: Dict[str, float]) -> Dict:
    """
    Find the critical path (longest path in the DAG).
    Uses dynamic programming to calculate longest path from each task to end.
    """
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def longest_path_from(task: str) -> float:
        """Longest path from this task to any terminal node"""
        if task not in graph or len(graph[task]) == 0:
            # Terminal node
            return task_effort.get(task, 0)

        # Maximum of (this task's effort + longest path from any dependent)
        dependents = [other for other, deps in graph.items() if task in deps]

        if not dependents:
            return task_effort.get(task, 0)

        return task_effort.get(task, 0) + max(longest_path_from(dep) for dep in dependents)

    # Find all tasks that are on the critical path
    critical_path_tasks = []
    current = None

    # Start from a task with no dependencies
    for task in graph:
        if len(graph[task]) == 0:
            if current is None or longest_path_from(task) > longest_path_from(current):
                current = task

    # Trace the critical path
    visited = set()
    critical_path_tasks = [current]

    while True:
        current_effort = task_effort.get(current, 0)
        dependents = [other for other, deps in graph.items() if current in deps]

        if not dependents:
            break  # Reached end

        # Find the dependent that leads to longest remaining path
        next_task = max(dependents, key=longest_path_from)
        critical_path_tasks.append(next_task)
        current = next_task

        if current in visited:
            break  # Cycle detected; stop
        visited.add(current)

    # Calculate critical path length and float for all tasks
    critical_path_length = sum(task_effort.get(t, 0) for t in critical_path_tasks)
    critical_set = set(critical_path_tasks)

    float_values = {}
    for task in graph:
        longest = longest_path_from(task)
        critical_length = critical_path_length
        float_values[task] = critical_length - longest

    return {
        "critical_path": critical_path_tasks,
        "critical_path_length": critical_path_length,
        "critical_tasks": critical_set,
        "float_by_task": float_values  # 0 for critical tasks, >0 for non-critical
    }
```

### Interpreting Critical Path Analysis

```python
critical_info = find_critical_path(graph, task_efforts)

# Tasks with float = 0 are critical path
for task in graph:
    float_value = critical_info["float_by_task"][task]
    if float_value == 0:
        print(f"{task}: CRITICAL - delay blocks entire project")
    else:
        print(f"{task}: Has {float_value} units of slack; can be delayed")

# Visualization
print(f"Critical path: {' ← '.join(critical_info['critical_path'])}")
print(f"Critical path length: {critical_info['critical_path_length']} units")
print(f"Minimum project duration: {critical_info['critical_path_length']} weeks")
```

## Parallelism Limits and Capacity Planning

While the DAG shows what *could* be parallel, practical constraints limit actual parallelism:

### Agent Capacity Constraints

```python
def calculate_actual_parallelism(layers: Dict[int, List[str]],
                                 available_agents: int = 5) -> Dict:
    """
    Calculate actual execution schedule given agent capacity.
    Typical: 5-7 concurrent agents = reasonable parallelism.
    """
    schedule = {}
    current_time = 0

    for layer_num in sorted(layers.keys()):
        tasks_in_layer = layers[layer_num]

        # How many "slots" do we have?
        # If layer has more tasks than agents, some must wait
        num_batches = (len(tasks_in_layer) + available_agents - 1) // available_agents

        for batch_idx in range(num_batches):
            batch_tasks = tasks_in_layer[
                batch_idx * available_agents:(batch_idx + 1) * available_agents
            ]
            for task in batch_tasks:
                schedule[task] = {
                    "start_time": current_time,
                    "layer": layer_num,
                    "batch": batch_idx
                }

            current_time += 1  # Each batch takes 1 time unit

    return schedule


def identify_bottlenecks(graph: Dict[str, List[str]]) -> List[str]:
    """
    Identify tasks that are blocking many others.
    These are coordination points and risk areas.
    """
    dependent_count = {}

    for task in graph:
        dependent_count[task] = 0

    # Count how many tasks depend (directly or transitively) on each task
    for task in graph:
        for dep in graph[task]:
            if dep not in dependent_count:
                dependent_count[dep] = 0
            dependent_count[dep] += 1

    # Sort by dependent count
    bottlenecks = sorted(dependent_count.items(), key=lambda x: x[1], reverse=True)
    return [task for task, count in bottlenecks if count > 2]
```

## Output Format: JSON Dependency Representation

```python
DependencyGraphOutput = {
    "metadata": {
        "total_tasks": int,
        "total_dependencies": int,
        "num_layers": int,
        "min_sequential_duration": float,  # Sum all task efforts
        "min_parallel_duration": float,    # Sum of critical path
        "speedup_ratio": float,            # sequential / parallel
        "recommended_parallelism": int     # suggested concurrent agents
    },

    "tasks": {
        "T-X.Y.Z": {
            "id": "T-X.Y.Z",
            "title": str,
            "dependencies": {
                "hard": ["T-A.B.C", ...],
                "soft": ["T-D.E.F", ...],
                "resource": ["T-G.H.I", ...]
            },
            "layer": int,
            "critical_path": bool,
            "float": float,
            "estimated_effort": "S" | "M" | "L" | "XL",
            "bottleneck": bool
        }
    },

    "layers": {
        "0": ["T-1.1.1", "T-2.1.1", ...],
        "1": ["T-1.1.2", "T-2.1.2", ...],
        ...
    },

    "critical_path": [
        "T-X.Y.Z → T-A.B.C → T-D.E.F"
    ],

    "bottlenecks": [
        {
            "task": "T-X.Y.Z",
            "dependent_count": int,
            "risk_level": "high" | "medium" | "low"
        }
    ]
}
```

## Mermaid Diagram Generation

Convert the dependency graph to Mermaid format for visualization:

```python
def generate_mermaid_diagram(graph: Dict[str, List[str]],
                             critical_tasks: set) -> str:
    """
    Generate Mermaid graph definition for visualization.
    Uses:
    - TD (top-down) layout
    - Red for critical path
    - Green for layer 0 (can start immediately)
    - Blue for other tasks
    """
    mermaid = "graph TD\n"

    # Add nodes with styling
    for task in graph:
        if task in critical_tasks:
            # Critical path: red/error style
            mermaid += f"    {task_to_node_id(task)}[{task}]:::critical\n"
        elif len(graph[task]) == 0:
            # No dependencies: green/success style
            mermaid += f"    {task_to_node_id(task)}[{task}]:::layer0\n"
        else:
            # Normal: blue/info style
            mermaid += f"    {task_to_node_id(task)}[{task}]:::normal\n"

    # Add edges
    mermaid += "\n"
    for task, deps in graph.items():
        for dep in deps:
            mermaid += f"    {task_to_node_id(dep)} --> {task_to_node_id(task)}\n"

    # Add styling
    mermaid += """
    classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff,font-weight:bold;
    classDef layer0 fill:#51cf66,stroke:#2f9e44,color:#fff;
    classDef normal fill:#4dabf7,stroke:#1971c2,color:#fff;
    """

    return mermaid


def task_to_node_id(task: str) -> str:
    """Convert task ID to safe Mermaid node ID"""
    return task.replace("-", "_").replace(".", "_")
```

## Effort Estimation

Effort estimation accounts for both sequential and parallel execution:

```python
def estimate_project_effort(tasks: Dict[str, Task],
                           graph: Dict[str, List[str]]) -> Dict:
    """
    Estimate effort under sequential vs. parallel execution.
    """
    # Map task IDs to effort values
    effort_estimates = {
        "S": 1,   # Small: 500-800 tokens
        "M": 2,   # Medium: 800-1500 tokens
        "L": 3,   # Large: 1500-2500 tokens
        "XL": 4   # Extra large: 2500-4000 tokens
    }

    # Sequential: sum of all task efforts
    total_sequential = sum(
        effort_estimates.get(task.estimated_effort, 2)
        for task in tasks.values()
    )

    # Parallel: max effort per layer
    layers = assign_layers(graph)
    total_parallel = sum(
        max(
            effort_estimates.get(tasks[task_id].estimated_effort, 2)
            for task_id in layer_tasks
        )
        for layer_tasks in layers.values()
    )

    speedup = total_sequential / total_parallel if total_parallel > 0 else 1.0

    return {
        "sequential_effort": total_sequential,
        "parallel_effort": total_parallel,
        "speedup_ratio": speedup,
        "estimated_sequential_duration": f"{total_sequential} weeks",
        "estimated_parallel_duration": f"{total_parallel} weeks with {len(layers)} layers",
        "recommended_team_size": min(7, len(assign_layers(graph)[max(assign_layers(graph).keys())])),
        "critical_path_length": find_critical_path(graph, {
            t_id: effort_estimates.get(t.estimated_effort, 2)
            for t_id, t in tasks.items()
        })["critical_path_length"]
    }
```

## Complete Example: E-Commerce Order Processing

**Tasks** (simplified):
```
T-2.1.1: Create Order model (S)
T-2.1.2: Implement OrderService (M)
T-2.1.3: Create REST API endpoints (M)
T-1.1.1: Create OrderForm component (S)
T-1.1.2: Add form submission handling (M)
T-3.1.1: Add order validation logic (M)
```

**Dependencies**:
```
T-2.1.1 → T-2.1.2 (OrderService needs Order model)
T-2.1.2 → T-2.1.3 (API needs service)
T-2.1.1 → T-3.1.1 (Validation needs model)
T-2.1.2 → T-1.1.2 (Form submission needs service)
T-1.1.1 → T-1.1.2 (Submission handler needs form)
```

**Layer Assignment**:
```
Layer 0: T-2.1.1, T-1.1.1        (2 tasks, parallel)
Layer 1: T-2.1.2, T-1.1.2, T-3.1.1 (3 tasks, parallel)
Layer 2: T-2.1.3                  (1 task)
```

**Critical Path**: T-2.1.1 → T-2.1.2 → T-2.1.3 (length 1+2+2 = 5 units)

**Estimates**:
- Sequential: 1+2+2+1+2+2 = 10 units (10 weeks)
- Parallel: max(1,1) + max(2,2,2) + max(2) = 1 + 2 + 2 = 5 units (5 weeks)
- Speedup: 10/5 = 2x

**Mermaid**:
```
graph TD
    T_2_1_1[T-2.1.1: Create Order model]:::normal
    T_2_1_2[T-2.1.2: OrderService]:::critical
    T_2_1_3[T-2.1.3: REST API]:::critical
    T_1_1_1[T-1.1.1: OrderForm]:::layer0
    T_1_1_2[T-1.1.2: Form handling]:::normal
    T_3_1_1[T-3.1.1: Validation]:::normal

    T_2_1_1 --> T_2_1_2
    T_2_1_2 --> T_2_1_3
    T_2_1_1 --> T_3_1_1
    T_2_1_2 --> T_1_1_2
    T_1_1_1 --> T_1_1_2
```
