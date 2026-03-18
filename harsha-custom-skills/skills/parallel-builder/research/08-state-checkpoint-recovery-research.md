# Research 08: State Management, Checkpointing & Recovery

## Source Validation
- **Primary**: SagaLLM (VLDB 2025, Chang et al.) — peer-reviewed database venue
- **Secondary**: ALAS (arXiv May 2025), LangGraph durable execution docs
- **Framework**: LangGraph state management for multi-agent workflows
- **Scrutiny Level**: Maximum (VLDB publication + production framework docs)

## Key Findings

### 1. SagaLLM: Saga Pattern for Multi-Agent LLM Systems
SagaLLM adapts the distributed systems Saga pattern to LLM orchestration:
- **Problem**: LLMs are stateless — each interaction is independent, no native
  mechanism to sustain state across sequential interactions
- **Solution**: Modular checkpointing + compensable execution + persistent memory
- **Three state dimensions**:
  - Application State (S_A): Domain objects, entity states, checkpoints/snapshots
  - Operation State (S_O): Execution metadata, inputs/outputs, reasoning chains,
    compensation metadata
  - Context State: LLM conversation history and tool call records

**Key insight**: "Without systematic transaction management, LLM-based systems risk
state inconsistency, operation losses, and incoherent recovery procedures"

### 2. Compensating Transactions (Critical Pattern)
When a multi-step workflow fails partway through:
- **Without saga**: Partial state left inconsistent, manual cleanup needed
- **With saga**: Each step defines a compensating action (rollback)
- **For our skill**: If task 5 of 7 fails during merge, compensation logic can:
  1. Revert merged files to pre-merge state
  2. Re-execute failed task with adjusted parameters
  3. Resume from last successful checkpoint

### 3. Checkpoint Architecture for Our Pipeline
Recommended checkpoint points in our 4-phase workflow:
- **Post-Plan**: Save execution plan JSON (already doing this)
- **Post-Layer**: After each execution layer completes, checkpoint all outputs
- **Post-Verify**: After verification, checkpoint verified outputs + report
- **Post-Merge**: Final checkpoint before delivery

Checkpoint format (proposed):
```json
{
  "checkpoint_id": "uuid",
  "phase": "execute",
  "layer": 2,
  "completed_tasks": ["task_1", "task_2", "task_3"],
  "pending_tasks": ["task_4"],
  "task_outputs": { "task_1": "path/to/output" },
  "token_usage": { "total": 45000, "by_task": {} },
  "timestamp": "iso8601",
  "resumable": true
}
```

### 4. Durable Execution (LangGraph Pattern)
Production-grade workflow resumability:
- Save progress at key points → pause → resume exactly where left off
- **Idempotent operations**: If retried after failure, same effect as first execution
- **Thread-based tracking**: Each workflow instance has unique thread ID
- **Checkpointer backends**: Redis (fast) or SQL/NoSQL (durable)
- **Concurrency control**: Row locking or optimistic concurrency

### 5. ALAS: Adaptive Recovery Under Disruption
- When previously valid plans become infeasible due to disruptions, stateless LLMs
  cannot revalidate without rollback
- ALAS proposes structured planning + adaptive re-execution
- Relevant to our skill: if an agent's output invalidates another agent's assumptions,
  we need detection + re-planning, not just retry

### 6. Recovery Strategies (Ranked by Cost)
1. **Retry with same params** (cheapest): Works for transient API failures
2. **Retry with adjusted params** (+temperature, different prompt): Works for quality failures
3. **Partial re-execution** (from checkpoint): Re-run only failed layer + downstream
4. **Full re-plan** (most expensive): When failure reveals fundamental plan issues

## Applied Improvements
1. Add checkpoint/resume capability to executor.py (save state after each layer)
2. Add compensating transaction logic for merge rollback
3. Implement idempotent task execution (check if output already exists)
4. Add resume flag to CLI: `--resume checkpoint.json`
5. Document recovery strategies in SKILL.md error handling section
