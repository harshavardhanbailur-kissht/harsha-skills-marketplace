# Failure Recovery & Pre-Mortem Analysis

## Failure Taxonomy

**Input Failures**: Bad assumptions about data format, API contracts, or config structure.
- Example: Expecting JSON array, receive object; assuming case sensitivity where none exists

**State Failures**: Race conditions, initialization order, or stale cache assumptions.
- Example: Modifying state before initialization; async completion order assumptions

**Timing Failures**: Timeout assumptions, latency expectations, or synchronization gaps.
- Example: Expecting sub-100ms response; hardcoded timeout that's too aggressive

**External Failures**: Third-party API changes, deprecations, or behavioral assumptions.
- Example: Assuming email delivery is synchronous; API version breaking change

**Resource Failures**: Memory, connection pool, or rate limit exhaustion.
- Example: Unbounded loop creating objects; connection leak under load

**Logic Failures**: Boundary conditions, rounding errors, or off-by-one mistakes.
- Example: Array slice [0, length] instead of [0, length); rounding that accumulates error

## Severity Levels

**CRITICAL**: Data loss, security breach, cascading infrastructure failure. Must test before deploy.
**HIGH**: Feature broken, user-facing error, performance degradation. Requires rollback plan.
**MEDIUM**: Edge case failure, incomplete feature, degraded experience. Can monitor and patch.
**LOW**: Warning logs, performance on non-critical path, rare edge case. Can ship with monitoring.

## Pre-Mortem Analysis: Klein's Narrative Method

Instead of bullet lists, write SHORT NARRATIVE STORIES of how failure happens:

**Template**:
```
Scenario: [1-2 sentence setup]
Trigger: [What actually breaks things]
Cascade: [How it spreads or compounds]
Impact: [User/system consequence]
Root Cause: [Why the design allowed this]
Preventive Action: [Code change, test, monitoring]
```

**Example**:
```
Scenario: Mobile user on 3G tries to login simultaneously on phone and web app.
Trigger: Two login requests hit auth service within 50ms; state mutation race condition.
Cascade: Second request overwrites first, creating two sessions pointing to same account.
Impact: User data visible in both sessions; logout on one doesn't clear other.
Root Cause: Session state stored without atomic compare-and-swap; async writes not coordinated.
Preventive Action: Use distributed lock (Redis) for session creation; test parallel login scenario.
```

## Cascading Failure Pattern

Map linked failures into causal chains:

```
[Input: malformed config]
  → [State: invalid initialization]
    → [Logic: wrong boundary condition]
      → [Resource: unbounded memory allocation]
        → [External: API rate limit hit]
          → [Timing: request timeout]
            → USER IMPACT: service unavailable
```

Identify break points where chain can be cut:
- Validate config early (Input gate)
- Add initialization checks (State gate)
- Test boundary conditions (Logic gate)
- Set resource limits (Resource gate)
- Implement backoff (External gate)
- Add monitoring (Timing gate)

## Analysis Failure Modes

**Shallow Analysis**: Stopping at "this code looks right" without testing assumptions.
- Fix: Always ask "how could this fail?" for each component.

**Domain Mismatch**: Analyzing without understanding business rules or user workflows.
- Fix: GROUND phase must include stakeholder validation of assumptions.

**Anchoring on First Idea**: Getting committed to initial hypothesis, ignoring contradictory findings.
- Fix: DIVERGE phase forces generation of 3+ alternative approaches; score each honestly.

**Confirmation Bias in Edge Case Exploration**: Only looking for failures you expect.
- Fix: Use systematic sweep (Input × State × Timing × External) before declaring complete.

**Missing Reversibility Assessment**: Assuming all changes can be rolled back.
- Fix: For each file, mark: REVERSIBLE (feature flag, config) vs IRREVERSIBLE (schema, migration).

## FMEA Template for EDGE_CASES.md

| Category | Failure Mode | Severity | Likelihood | Detection | RPN | Mitigation |
|----------|--------------|----------|------------|-----------|-----|-----------|
| INPUT | Null/undefined field | HIGH | MEDIUM | Unit test | 12 | Schema validation |
| STATE | Race condition on writes | CRITICAL | LOW | Integration test | 8 | Distributed lock |
| TIMING | Timeout too aggressive | HIGH | MEDIUM | Load test | 12 | Dynamic backoff |
| EXTERNAL | API deprecation | MEDIUM | LOW | Contract test | 6 | Version pinning |
| RESOURCE | Memory leak under load | HIGH | LOW | Stress test | 8 | Profiling, pooling |
| LOGIC | Off-by-one in loop | MEDIUM | MEDIUM | Unit test | 9 | Boundary test case |

## Systematic Edge Case Sweep

For each dimension, ask "What breaks if...?"

**Input**: null, empty, oversized, wrong type, encoding issue, unicode edge case, special chars

**State**: uninitialized, partially initialized, stale cache, concurrent modification, rollback scenario

**Timing**: zero latency, infinite latency, timeout during startup, timeout during shutdown, concurrent requests

**External**: service down, slow response, invalid response, breaking API change, rate limit, connection reset

Write 2-3 failure narratives for high-probability + high-impact combinations only. Don't enumerate all 100 combinations.

## Pre-Mortem Checklist

Before SYNTHESIZE phase, run through:
- [ ] Are all CRITICAL failures covered with mitigation?
- [ ] Can this change be rolled back in under 1 hour?
- [ ] Are all assumptions about external systems documented?
- [ ] Is there a monitoring alert for top 3 failure scenarios?
- [ ] Have we tested worst-case resource consumption?
- [ ] Do we have feature flag or gradual rollout plan?
