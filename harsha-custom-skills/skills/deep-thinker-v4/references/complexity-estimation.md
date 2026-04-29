# Complexity Estimation Framework

## 30-Second Assessment Decision Tree

```
START
  ├─ Single isolated change? → TRIVIAL (1 file, GROUND phase only)
  ├─ Modify one subsystem? → SMALL (3-5 files, GROUND + partial DIVERGE)
  ├─ Cross-subsystem interaction? → MEDIUM (6-15 files, full workflow)
  └─ Architectural/multi-layer/stakeholder impact? → COMPLEX (15+ files, extended analysis)
```

## Four Complexity Dimensions

**Technical**: Code depth (surface vs algorithms), type system complexity, testing surface area.
- Trivial: Single function, no branching
- Small: Component boundaries, clear dependency
- Medium: Cross-layer calls, async/state management
- Complex: Distributed logic, multiple integration points

**Domain**: Business rule complexity, regulatory/compliance surface, user-facing impact.
- Trivial: Bug fix, internal refactor
- Small: Feature within known domain
- Medium: New feature touching multiple user flows
- Complex: Business logic changes, policy impact

**Integration**: External system dependencies, API changes, migration scope.
- Trivial: No external calls
- Small: One external system
- Medium: Multiple systems, data migration
- Complex: Coordination across teams, protocol changes

**Uncertainty**: Known unknowns at start, estimation confidence, reversibility.
- Trivial: Fully known
- Small: Minor unknowns
- Medium: Some gaps in understanding
- Complex: Significant unknowns, hard to reverse

## Depth Calibration Matrix

| Complexity | Files to Load | References Loaded | Time Budget | Analysis Depth |
|-----------|---------------|-------------------|------------|-----------------|
| TRIVIAL | 1-2 | complexity-estimation only | <15 min | Surface: verify correctness |
| SMALL | 3-5 | complexity-estimation, task-decomposition | 30 min | Standard: confirm boundaries |
| MEDIUM | 6-15 | all except exhaustive sections | 60 min | Deep: full dependency analysis |
| COMPLEX | 15+ | all references + context-engineering | 90+ min | Exhaustive: edge cases, pre-mortem |

## Kill Gate Pattern: DOWNGRADE Decision

After GROUND phase, evaluate:
- **Kill If**: No cross-subsystem calls found, change is isolated, reversible, no stakeholder coordination needed
- **Action**: Drop to SMALL complexity, truncate DIVERGE phase, skip STRESS on unaffected areas
- **Signal**: GROUND revealed less coupling than estimated

## Escalation Patterns: UPGRADE Decision

During analysis, escalate if:
- Discovery of hidden integration point (not in original scope)
- Stakeholder dependency not mentioned in brief
- Backward compatibility requirements discovered
- Feature flag or gradual rollout needed
- New uncertainty emerges in GROUND

## Complexity Heuristics

**Regret Minimization**: Ask "If I get this wrong, how bad?" Reversible mistakes → smaller complexity. Irreversible → escalate.

**File Count Proxy**: Count distinct files touched in solution. >15 typically COMPLEX.

**Stakeholder Count**: One team → SMALL, Multiple teams → MEDIUM, Cross-org → COMPLEX.

**Reversibility**: Can this be rolled back in <1 hour? Yes → lower complexity rating.

**Confidence Anchor**: How confident am I right now? <50% → escalate one level.

## Depth Calibration for Edge Cases

- **TRIVIAL**: No pre-mortem, skip STRESS phase
- **SMALL**: Lightweight STRESS (3-5 failure scenarios)
- **MEDIUM**: Full pre-mortem with 2-3 causal chains
- **COMPLEX**: Deep pre-mortem, cascading failure analysis, FMEA template required
