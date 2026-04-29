# Context Engineering: Depth Management & File-Based Persistence

## Depth Hierarchy

**Surface**: One-pass reading, identify main points, surface assumptions.
- Use when: Time-limited, high-level decision needed, complexity is SMALL
- Output: Bullet-point summary, 1-2 key insights
- Sample size: 20% of codebase

**Standard**: Targeted code reading, trace key flows, validate assumptions.
- Use when: Normal decision-making, complexity is MEDIUM, time allows 30-60 min
- Output: Flow diagrams, decision trees, confidence ratings
- Sample size: 40% of codebase (touched files + dependencies)

**Deep**: Exhaustive analysis, edge cases, performance characteristics, all failure scenarios.
- Use when: High-stakes decision, complexity is COMPLEX, time allows 60-90 min
- Output: Architecture diagrams, pre-mortem analysis, FMEA, monitoring plan
- Sample size: 70% of codebase (all related systems)

**Exhaustive**: Complete understanding, all permutations, all edge cases, no assumptions.
- Use when: Life-critical system, complexity is COMPLEX + Uncertainty is high
- Output: Formal proof of correctness, exhaustive test matrix, legal/compliance review
- Sample size: 100% of codebase
- Warning: Rarely justified; usually "deep" suffices

## When to Go Deeper: Decision Matrix

| Signal | Depth Bump |
|--------|-----------|
| Discovery of hidden integration point | Surface → Standard |
| File count exceeds estimate by 30% | Standard → Deep |
| Stakeholder count > 1 | Standard → Deep |
| Irreversible change (schema, migration) | Standard → Deep |
| Regulatory/compliance risk | Any level → Deep or Exhaustive |
| Uncertainty discovered in GROUND | Bump up 1 level |
| Change affects payment/auth/PII | Standard → Exhaustive |

**Decision Logic**: After GROUND phase, re-assess. If signals above are present, escalate depth before DIVERGE.

## File-Based Persistence: Why Files Beat Memory

**Problem with In-Memory Analysis**:
- Context window fills up with intermediate notes
- Can't easily refer back to earlier findings
- Loses structure when switching between tasks
- Hard to collaborate (can't share working notes)

**Solution - Persistent Analysis Files**:

```
SCOPE.md       - Problem statement, constraints, success criteria
GROUND.md      - Code findings, assumptions validated, dependency map
DIVERGE.md     - 3+ alternative approaches, trade-off matrix
STRESS.md      - Failure scenarios, pre-mortem narratives, edge cases
EDGE_CASES.md  - FMEA template, systematic edge case sweep
SYNTHESIZE.md  - Decision summary, executor brief, rollback plan
```

**Benefits**:
- Each phase writes its output before reading next phase input
- Can re-read earlier findings without losing context
- Executor brief references specific file paths and line numbers
- Easy to share with stakeholders for review
- Future similar decisions can reference previous analysis

## Progressive Externalization Pattern

**Rule**: Write each file completely before starting next phase.

```
START
├─ Complete SCOPE.md (checkpoint: problem is clear)
├─ Complete GROUND.md (checkpoint: current state is documented)
├─ Complete DIVERGE.md (checkpoint: alternatives are evaluated)
├─ Complete STRESS.md (checkpoint: risks are identified)
├─ Complete EDGE_CASES.md (checkpoint: failure modes are catalogued)
└─ Complete SYNTHESIZE.md (checkpoint: decision is ready)
```

**Why Checkpoint Between Phases**:
- Forces closure on phase work
- Makes hand-off to executor explicit
- Prevents analysis sprawl (working on 5 things at once)
- Each file can be reviewed independently
- Easier to estimate time (we know phase takes ~15 min per depth level)

## Context Budget Management by Complexity

**TRIVIAL Complexity**:
- Target: 15 min total
- Depth: Surface only
- Files: Just SCOPE.md + short GROUND.md
- Skip: DIVERGE, STRESS, SYNTHESIZE as separate files (combine into brief)
- Context budget: <5K tokens

**SMALL Complexity**:
- Target: 30 min total
- Depth: Standard
- Files: SCOPE.md, GROUND.md, DIVERGE.md (short), brief SYNTHESIZE
- Skip: Exhaustive STRESS and EDGE_CASES
- Context budget: 20-30K tokens

**MEDIUM Complexity**:
- Target: 60 min total
- Depth: Deep
- Files: All 6 files with full detail
- Detail level: Each file 80-120 lines
- Context budget: 40-60K tokens

**COMPLEX Complexity**:
- Target: 90+ min total
- Depth: Deep + Exhaustive for high-risk areas
- Files: All 6 files, with extended STRESS and EDGE_CASES
- Detail level: Each file 150-200 lines
- May need multiple passes or async research
- Context budget: 70-100K tokens

**Estimation Formula**:
```
Context Used = (File Count × 50 tokens/file) + (Depth Level × 10K tokens) + (Risk Level × 5K tokens)

Example: MEDIUM complexity, 10 files, high risk
= (10 × 50) + (Deep = 30K) + (High = 5K) = 35.5K tokens
```

## Quality Indicators of Sufficient Depth

**Surface Depth Done When**:
- Main problem is stated in one sentence
- Affected files are listed
- 2+ critical assumptions are documented

**Standard Depth Done When**:
- Key code flows are traced with examples
- All major dependencies are identified
- Trade-offs between 2 approaches are documented
- Confidence tags are applied to main decisions

**Deep Depth Done When**:
- Edge cases are systematically explored (Input × State × Timing × External)
- Pre-mortem identifies 3+ failure narratives
- Performance characteristics are estimated
- Rollback procedure is written
- All CRITICAL risks have mitigation

**Exhaustive Depth Done When**:
- All permutations of edge cases are covered
- Legal/compliance review is done
- Security audit is complete
- Performance testing is done (not estimated)
- Production monitoring and alerting plan is complete

## Escalation Signal Checklist

During analysis, check for depth escalation triggers:

- [ ] Found integration with system I didn't know about? ESCALATE
- [ ] Realized change affects >1 team? ESCALATE
- [ ] Discovered irreversible data change? ESCALATE
- [ ] Any assumption hasn't been validated? ESCALATE
- [ ] Edge case could cause data loss? ESCALATE
- [ ] Failure scenario would affect >100 users? ESCALATE
- [ ] Change touches payment/auth/PII? ESCALATE

If any box is checked, increase depth by 1 level before continuing.

## File Template Structure (Depth-Agnostic)

All files follow same structure, just vary in detail:

```
# [Phase Name]

## Key Findings / Decisions
[Top 2-3 bullets, most important insight first]

## [Subsection 1]
[Content]

## [Subsection 2]
[Content]

## Confidence & Unknowns
Confidence: [VERIFIED/HIGH/MEDIUM/LOW]
Unknowns: [What would change our decision]
Escalation Needed: [YES/NO with reason]
```

This makes it easy to skim at any depth level - always check "Confidence & Unknowns" at end of file.
