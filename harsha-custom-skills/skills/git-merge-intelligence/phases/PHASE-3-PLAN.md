# PHASE 3: RESOLUTION PLANNING

**Objective:** Transform the triaged conflict registry into an executable resolution plan — dependency-ordered batches with per-file resolution strategies, risk scores, and Deep Thinker invocation decisions.

**Prerequisite**: Phase 2 COMPLETE (`CONFLICT-REGISTRY.json` must exist with all files classified)

---

## Overview

This phase:
1. Reads CONFLICT-REGISTRY.json from Phase 2
2. Builds a dependency graph across all conflicted files
3. Applies Kahn's algorithm to compute topological batch ordering
4. Assigns resolution strategies per file based on conflict type + intent
5. Computes risk scores and identifies Deep Thinker candidates
6. Writes the batch execution plan to MERGE-CONTEXT.md
7. Generates per-batch execution manifests

**Expected Output**:
- `.merge-resolver/MERGE-CONTEXT.md` ← updated with batch execution plan
- `.merge-resolver/BATCH-PLAN.json` ← machine-readable execution plan
- `.merge-resolver/MERGE-CONTEXT.md` Phase 3 COMPLETE marker

---

## Execution Flow

### Step 1: Pre-flight Check

```bash
# Verify Phase 2 is COMPLETE
if ! grep -q "Phase 2.*COMPLETE" .merge-resolver/MERGE-CONTEXT.md; then
  echo "[PHASE-3] ERROR: Phase 2 not marked COMPLETE. Run Phase 2 first."
  exit 1
fi

# Verify CONFLICT-REGISTRY.json exists
if [ ! -f ".merge-resolver/CONFLICT-REGISTRY.json" ]; then
  echo "[PHASE-3] ERROR: CONFLICT-REGISTRY.json missing. Run Phase 2."
  exit 1
fi

echo "[PHASE-3] Pre-flight passed. Building resolution plan..."
```

### Step 2: Build Dependency Graph

**Goal**: Create a directed acyclic graph (DAG) where edges represent "must resolve before" relationships.

```python
import json

# Load registry
with open('.merge-resolver/CONFLICT-REGISTRY.json') as f:
    registry = json.load(f)

# Build adjacency list
# Edge: A → B means "A must be resolved before B"
graph = {}       # node → list of dependents
in_degree = {}   # node → count of dependencies

for file_entry in registry['files']:
    path = file_entry['path']
    graph.setdefault(path, [])
    in_degree.setdefault(path, 0)
    
    for dep in file_entry.get('depends_on', []):
        # Only track dependencies on OTHER conflicted files
        if dep in [f['path'] for f in registry['files']]:
            graph.setdefault(dep, [])
            graph[dep].append(path)
            in_degree[path] = in_degree.get(path, 0) + 1
```

### Step 3: Apply Kahn's Algorithm

**Kahn's algorithm** identifies safe parallel batches by repeatedly extracting zero-in-degree nodes.

```python
from collections import deque

def kahns_algorithm(graph, in_degree):
    """
    Returns list of batches, where each batch contains
    files that can be safely resolved in parallel.
    """
    batches = []
    queue = deque()
    
    # Initialize with zero-in-degree nodes
    for node in in_degree:
        if in_degree[node] == 0:
            queue.append(node)
    
    while queue:
        # Current batch: all zero-in-degree nodes
        batch = []
        next_queue = deque()
        
        while queue:
            node = queue.popleft()
            batch.append(node)
        
        batches.append(batch)
        
        # Remove this batch from graph, update in-degrees
        for node in batch:
            for dependent in graph.get(node, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    next_queue.append(dependent)
        
        queue = next_queue
    
    # Check for cycles
    resolved = sum(len(b) for b in batches)
    total = len(in_degree)
    if resolved < total:
        # Circular dependency detected
        unresolved = [n for n in in_degree if in_degree[n] > 0]
        return batches, unresolved  # Return partial + cycle members
    
    return batches, []

batches, cycles = kahns_algorithm(graph, in_degree)
```

**Cycle Handling:**

```python
if cycles:
    print(f"[PHASE-3] WARNING: Circular dependencies detected in {len(cycles)} files")
    print(f"[PHASE-3] Cycle members: {cycles}")
    # Strategy: Force cycle members into a single batch
    # They must be resolved together with manual coordination
    batches.append(cycles)  # Add as final batch
    print("[PHASE-3] Cycle members grouped into single forced batch")
```

### Step 4: Merge Kahn's Batches with Phase 2 Semantic Batches

Phase 2 assigns semantic batches (0-5: configs → types → shared → impls → tests → docs).
Kahn's algorithm produces dependency-ordered batches.

**Merge strategy**: Use semantic batches as the primary ordering, Kahn's ordering as tiebreaker within each semantic batch.

```python
def merge_batch_orderings(semantic_batches, kahn_batches, registry):
    """
    Combine semantic batch assignments (Phase 2) with
    dependency ordering (Kahn's) into final execution plan.
    """
    final_plan = {}
    
    for file_entry in registry['files']:
        path = file_entry['path']
        semantic_batch = file_entry['batch']  # From Phase 2
        
        # Find Kahn's batch index
        kahn_batch = 0
        for i, batch in enumerate(kahn_batches):
            if path in batch:
                kahn_batch = i
                break
        
        # Final batch = max(semantic, kahn) — ensures dependencies are respected
        final_batch = max(semantic_batch, kahn_batch)
        
        final_plan[path] = {
            'semantic_batch': semantic_batch,
            'kahn_batch': kahn_batch,
            'final_batch': final_batch,
            'conflict_type': file_entry['conflict_type'],
            'complexity': file_entry['complexity']
        }
    
    return final_plan
```

### Step 5: Assign Resolution Strategies

For each file, determine the resolution approach based on conflict type, intent, and complexity.

**Strategy Selection Matrix:**

| Conflict Type | Our Intent: FEATURE | Our Intent: REFACTOR | Our Intent: BUGFIX | Our Intent: HOTFIX |
|---------------|--------------------|--------------------|-------------------|-------------------|
| **ADDITIVE** | KEEP_BOTH | KEEP_OURS (structure) | KEEP_THEIRS (preserve) | KEEP_THEIRS |
| **MODIFY_SAME** | MANUAL_MERGE | KEEP_OURS (structure) | DEEP_THINK | KEEP_OURS (fix) |
| **DELETE_MODIFY** | DEEP_THINK | KEEP_OURS (delete OK) | DEEP_THINK | KEEP_OURS |
| **RENAME_MODIFY** | DEEP_THINK | KEEP_OURS (new path) | DEEP_THINK | KEEP_THEIRS |
| **SEMANTIC** | DEEP_THINK | DEEP_THINK | DEEP_THINK | DEEP_THINK |
| **CONFIG** | MANUAL_MERGE | KEEP_OURS | MANUAL_MERGE | KEEP_OURS |
| **LOCKFILE** | REGENERATE | REGENERATE | REGENERATE | REGENERATE |
| **AUTH_SECURITY** | DEEP_THINK | DEEP_THINK | DEEP_THINK | DEEP_THINK |

**Strategy Definitions:**

| Strategy | Meaning | Automation Level |
|----------|---------|-----------------|
| `KEEP_OURS` | Accept our branch version entirely | Full auto |
| `KEEP_THEIRS` | Accept their branch version entirely | Full auto |
| `KEEP_BOTH` | Merge both additions (non-overlapping) | Semi-auto |
| `MANUAL_MERGE` | AI-assisted merge with human review flag | Semi-auto |
| `REGENERATE` | Delete and regenerate (lockfiles, generated code) | Full auto |
| `DEEP_THINK` | Invoke multi-expert Deep Thinker analysis | Manual |

```python
def assign_strategy(file_entry, our_intent, their_intent):
    """Assign resolution strategy based on conflict type and intent."""
    ct = file_entry['conflict_type']
    
    # Non-negotiable rules
    if ct == 'LOCKFILE':
        return 'REGENERATE'
    if ct == 'AUTH_SECURITY':
        return 'DEEP_THINK'
    if ct == 'SEMANTIC':
        return 'DEEP_THINK'
    
    # Intent-driven rules
    if ct == 'ADDITIVE':
        if our_intent == 'FEATURE' and their_intent == 'FEATURE':
            return 'KEEP_BOTH'
        if our_intent == 'REFACTOR':
            return 'KEEP_OURS'
        return 'KEEP_BOTH'
    
    if ct == 'MODIFY_SAME':
        if our_intent == 'HOTFIX':
            return 'KEEP_OURS'
        if their_intent == 'HOTFIX':
            return 'KEEP_THEIRS'
        return 'MANUAL_MERGE'
    
    if ct == 'DELETE_MODIFY':
        return 'DEEP_THINK'
    
    if ct == 'RENAME_MODIFY':
        return 'DEEP_THINK'
    
    if ct == 'CONFIG':
        return 'MANUAL_MERGE'
    
    return 'MANUAL_MERGE'  # Conservative default
```

### Step 6: Compute Risk Scores

Each file gets a risk score based on multiple factors:

```python
def compute_risk_score(file_entry, batch_depth, total_dependents):
    """
    Risk = confidence_weight × dependency_depth × blast_radius
    Returns: GREEN (≥70), YELLOW (40-69), RED (<40)
    """
    base_score = 100
    
    # Conflict type penalty
    type_penalties = {
        'ADDITIVE': 5,
        'MODIFY_SAME': 20,
        'DELETE_MODIFY': 35,
        'RENAME_MODIFY': 30,
        'SEMANTIC': 45,
        'CONFIG': 15,
        'LOCKFILE': 10,  # Low because we REGENERATE
        'AUTH_SECURITY': 50
    }
    base_score -= type_penalties.get(file_entry['conflict_type'], 20)
    
    # Complexity penalty
    complexity_penalties = {
        'TRIVIAL': 0,
        'MODERATE': 10,
        'COMPLEX': 25,
        'CRITICAL': 40
    }
    base_score -= complexity_penalties.get(file_entry['complexity'], 15)
    
    # Dependency depth penalty (deeper = more risk propagation)
    base_score -= min(batch_depth * 5, 20)
    
    # Blast radius penalty (more dependents = more impact)
    base_score -= min(total_dependents * 3, 15)
    
    # Clamp to 0-100
    score = max(0, min(100, base_score))
    
    # Classify
    if score >= 70:
        return score, 'GREEN'
    elif score >= 40:
        return score, 'YELLOW'
    else:
        return score, 'RED'
```

### Step 7: Identify Deep Thinker Candidates

```python
deep_think_candidates = []

for file_entry in registry['files']:
    needs_deep_think = False
    reasons = []
    
    # Rule 1: Strategy requires it
    if file_entry.get('resolution_strategy') == 'DEEP_THINK':
        needs_deep_think = True
        reasons.append(f"Strategy: DEEP_THINK (type={file_entry['conflict_type']})")
    
    # Rule 2: Risk score is RED
    if file_entry.get('risk_level') == 'RED':
        needs_deep_think = True
        reasons.append(f"Risk: RED (score={file_entry.get('risk_score', '?')})")
    
    # Rule 3: Auth/security file
    if 'auth' in file_entry['path'].lower() or 'security' in file_entry['path'].lower():
        needs_deep_think = True
        reasons.append("Path contains auth/security keywords")
    
    # Rule 4: Cross-language interface (TypeScript type used by Go)
    if file_entry.get('cross_language_dependency'):
        needs_deep_think = True
        reasons.append("Cross-language dependency detected")
    
    if needs_deep_think:
        deep_think_candidates.append({
            'path': file_entry['path'],
            'reasons': reasons
        })

print(f"[PHASE-3] Deep Thinker candidates: {len(deep_think_candidates)} files")
```

### Step 8: Generate BATCH-PLAN.json

```json
{
  "generated_at": "2026-04-08T10:00:00Z",
  "mode": "STANDARD",
  "total_files": 68,
  "total_batches": 6,
  "our_intent": "FEATURE",
  "their_intent": "REFACTOR",
  "batches": [
    {
      "batch_id": 0,
      "name": "Foundation (Configs & Lockfiles)",
      "files": [
        {
          "path": "package.json",
          "strategy": "MANUAL_MERGE",
          "risk_score": 55,
          "risk_level": "YELLOW",
          "deep_think": false,
          "notes": "Both branches add dependencies"
        },
        {
          "path": "go.sum",
          "strategy": "REGENERATE",
          "risk_score": 85,
          "risk_level": "GREEN",
          "deep_think": false,
          "notes": "Delete and run go mod tidy"
        }
      ],
      "batch_risk": "YELLOW",
      "gate": "Must complete before Batch 1"
    },
    {
      "batch_id": 1,
      "name": "Types & Interfaces",
      "files": [],
      "batch_risk": "GREEN",
      "gate": "Must complete before Batch 2"
    }
  ],
  "deep_think_queue": [
    {
      "path": "src/auth/jwt-verify.ts",
      "reasons": ["AUTH_SECURITY", "Risk: RED"],
      "priority": 1
    }
  ],
  "cycle_warnings": []
}
```

### Step 9: Update MERGE-CONTEXT.md

Append the batch execution plan:

```markdown
## Phase 3: Resolution Planning [COMPLETE]

**Executed**: [TIMESTAMP]
**Strategy**: Dependency-ordered batch execution (Kahn's algorithm)

### Batch Execution Plan

**Batch 0: Foundation** (5 files, risk: YELLOW)
| File | Strategy | Risk | Deep Think |
|------|----------|------|------------|
| package.json | MANUAL_MERGE | 🟡 55 | No |
| go.sum | REGENERATE | 🟢 85 | No |
| tsconfig.json | KEEP_OURS | 🟢 78 | No |
| vite.config.ts | MANUAL_MERGE | 🟡 62 | No |
| tailwind.config.js | KEEP_BOTH | 🟢 80 | No |

**Batch 1: Types & Interfaces** (8 files, risk: GREEN)
...

**Batch 2: Shared / Middleware** (12 files, risk: YELLOW)
...

**Batch 3: Implementations** (28 files, risk: YELLOW)
...

**Batch 4: Tests** (10 files, risk: GREEN)
...

**Batch 5: Docs / CI** (5 files, risk: GREEN)
...

### Deep Thinker Queue (3 files)
1. src/auth/jwt-verify.ts — AUTH_SECURITY, Risk RED
2. src/api/billing/charge.ts — SEMANTIC conflict
3. src/middleware/cors.ts — Cross-language dependency

### Execution Rules
- Batches execute sequentially (0 → 1 → 2 → 3 → 4 → 5)
- Files within a batch may be resolved in parallel
- YELLOW batch: verify before proceeding to next batch
- RED files: present to human with full context before resolving
- REGENERATE files: execute regeneration commands, do not merge manually
```

### Step 10: Mark Phase 3 Complete

```bash
# Update phase status
sed -i 's/\[ \] Phase 3: Resolution Planning/[x] Phase 3: Resolution Planning — COMPLETE/' \
  .merge-resolver/MERGE-CONTEXT.md

echo "[PHASE-3] ========================================"
echo "[PHASE-3] Phase 3 (Resolution Planning) COMPLETE"
echo "[PHASE-3] ========================================"
echo ""
echo "Plan summary:"
echo "  Total batches: $TOTAL_BATCHES"
echo "  Deep Thinker candidates: $DEEP_THINK_COUNT"
echo "  Cycle warnings: $CYCLE_COUNT"
echo ""
echo "Next: PHASE-4-EXECUTE.md"
```

---

## SPRINT Mode Optimization

When MODE = SPRINT (≤15 files):
- Skip Kahn's algorithm (all files in single batch)
- Use Phase 2 semantic batch ordering directly
- No risk scoring (all files resolved sequentially)
- Deep Thinker only for AUTH_SECURITY files

---

## Error Handling

| Error | Recovery |
|-------|----------|
| CONFLICT-REGISTRY.json parse failure | Re-run Phase 2 |
| Circular dependency detected | Force into single batch + warn user |
| No conflicted files found | Merge may have auto-resolved; verify with `git status` |
| Risk score computation failure | Default to YELLOW for the file |

---

## Success Criteria

Phase 3 is COMPLETE when:

✓ Dependency graph built for all conflicted files
✓ Kahn's algorithm applied (or skipped for SPRINT)
✓ Every file has a resolution strategy assigned
✓ Risk scores computed for all files
✓ Deep Thinker candidates identified
✓ BATCH-PLAN.json generated
✓ MERGE-CONTEXT.md updated with Phase 3 COMPLETE marker

**Next**: Phase 4 (EXECUTE) reads BATCH-PLAN.json and resolves conflicts batch by batch

---

## References
- parallel-conflict-resolution-theory.md (Sections 1-9: Kahn's Algorithm, Batch Construction)
- polyglot-dependency-analysis.md (Sections 4-8: Dependency Graphs, Heuristics)
- intent-extraction-from-pr-signals.md (Sections 2-6: Intent Classification)
- large-scale-merge-patterns.md (Sections 3-5: Batch Sizing, Risk Cascading)
