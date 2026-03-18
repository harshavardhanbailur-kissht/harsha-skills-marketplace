# Research: Adaptive Task Decomposition & Granularity Optimization

**Tier**: Maximum Scrutiny | **Date**: Feb 2026 | **Sources**: 8 validated
**Confidence**: HIGH (peer-reviewed NAACL 2024 + production implementations)

---

## Key Findings

### 1. ADaPT: Failure-Triggered Decomposition (HIGH confidence)
- **Core mechanism**: Only decompose when executor fails — not upfront
- Planner decomposes failed subtask into sub-subtasks connected by AND/OR operators
- Each subtask recursively assigned to ADaPT (failure-triggered recursion)
- Tasks decomposed only as deeply as needed for success

**Results**:
- ALFWorld: +28.3% improvement over non-decomposed baseline
- WebShop: +27% improvement
- TextCraft: +33% improvement

**Decomposition depth**: Automatically scales with task complexity
- d_max tested: 1-3 levels; consistent improvement with deeper decomposition
- Average depth 1.9 for depth-2 tasks, 2.8 for depth-3 tasks

**Source**: [ADaPT NAACL 2024](https://aclanthology.org/2024.findings-naacl.264/), [arXiv:2311.05772](https://arxiv.org/abs/2311.05772)

### 2. Follow-up: SCOPE (2025) — Faster Than ADaPT (MODERATE confidence)
- One-shot hierarchical planner with LLM-generated subgoals at initialization
- Pretrains lightweight student model for execution
- ADaPT: 0.52 success rate, 164.4s inference time
- SCOPE: 0.56 success rate, much faster inference
- Suggests upfront planning + lightweight execution can beat adaptive decomposition
- **Source**: [ICLR 2025](https://openreview.net/pdf?id=mPdmDYIQ7f)

### 3. Optimal Depth: 3-4 Levels Maximum (HIGH confidence)
| Level | Coordination Cost | Error Propagation |
|---|---|---|
| 1 | O(1) | 85% success |
| 2 | O(n) | 72% success |
| 3 | O(n²) | 61% success |
| 4+ | O(n³) | 52% success |

- Each level adds ~10-15% error propagation
- Coordination overhead grows exponentially
- Humans and LLMs maintain ~3-4 levels of active context
- **Practical rule**: Strict maximum of 4 levels; prefer 3 for most tasks
- **Source**: [ADaPT experiments](https://arxiv.org/abs/2311.05772), [Decomposition-Coordination ref](file:decomposition-coordination.md)

### 4. Granularity Sweet Spot: "Junior Engineer Complexity" (HIGH confidence)
**When decomposition HURTS**:
- Subtasks too interdependent (violating independence assumptions)
- Communication overhead exceeds parallelization benefit
- Coordinator complexity exceeds executor complexity
- Knowledge context lost across task boundaries

**When decomposition HELPS**:
- Tasks can genuinely execute in parallel
- Failure recovery easier at finer granularity
- Specialized agents excel at subtasks
- Resource constraints make focused depth preferable

**Optimal target per subtask**:
- 2000-4000 output tokens
- Single, clear, verifiable goal
- Review should take seconds, not minutes
- An intern could figure it out with sufficient instructions

### 5. Breadth-Depth Allocation (HIGH confidence)
**Power Law**: Number of deep-dive topics = Capacity^0.75
- Doubling capacity only increases coverage by 1.4x (not 2x)
- Low capacity → breadth-first (survey many topics)
- High capacity → depth-first (deep dive on best leads)

**Budget split**: 20-30% exploration / 70-80% validation
- Compress exploration to force focus on high-value work
- After √N sources, expect ~70% of remaining to be redundant

---

## Recommendations for Our Skill

### Hybrid Decomposition Strategy
1. **Upfront planning** (SCOPE-inspired): Use Opus to generate full DAG at initialization
2. **Adaptive refinement** (ADaPT-inspired): If a subtask fails, decompose further
3. **Max 3 layers** for most features; only go to 4 for truly complex systems
4. Each subtask targets 2000-4000 output tokens

### DAG Construction Rules
1. Every task_id in dependencies must exist in the tasks array
2. No circular dependencies (it's a DAG — validate with Kahn's algorithm)
3. Layer assignments must respect dependencies
4. Each prompt must be self-contained with ALL needed context
5. Always include a final integration/assembly task in the last layer
6. Keep total under 15 tasks for most features (5-10 is ideal)

### Interface Contract Specification
```json
{
  "task_id": "task_001",
  "contract": {
    "inputs": {
      "from_tasks": ["task_000"],
      "expected_data": "SQLAlchemy User model with id, email, hashed_password fields",
      "format": "Python module with class definitions"
    },
    "outputs": {
      "format": "FastAPI router module",
      "key_exports": ["router (APIRouter)"],
      "file_type": ".py",
      "validation": "Must import from task_000 output"
    },
    "boundaries": [
      "Does NOT define database models",
      "Does NOT implement JWT logic",
      "Does NOT write tests"
    ],
    "assumptions": [
      "Database session available via dependency injection",
      "Auth middleware handles token validation"
    ]
  }
}
```

---

## Source Registry
1. [ADaPT NAACL 2024](https://aclanthology.org/2024.findings-naacl.264/)
2. [ADaPT arXiv](https://arxiv.org/abs/2311.05772)
3. [ADaPT Project Page](https://allenai.github.io/adaptllm/)
4. [SCOPE ICLR 2025](https://openreview.net/pdf?id=mPdmDYIQ7f)
5. [Amazon Science: Task Decomposition](https://www.amazon.science/blog/how-task-decomposition-and-smaller-llms-can-make-ai-more-affordable)
6. [Breadth-Depth Research](https://elifesciences.org/articles/76985)
7. [Hierarchical Multi-Agent Taxonomy](https://arxiv.org/html/2508.12683)
8. [Composable Contracts](https://openreview.net/forum?id=hq0lZ9u68G)
