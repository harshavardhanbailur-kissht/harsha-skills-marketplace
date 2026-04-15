# Dependency Graph: {PRD Title}

## Execution Summary
| Metric | Value |
|--------|-------|
| Total Epics | {N} |
| Total Features | {N} |
| Total Tasks | {N} |
| Execution Layers | {N} |
| Critical Path Length | {N} tasks |
| Max Parallelism | {N} concurrent |
| Sequential Estimate | {N} hours |
| Parallel Estimate | {N} hours |
| Speedup Ratio | {X}x |

## Mermaid DAG

```mermaid
graph TD
    classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef layer0 fill:#51cf66,stroke:#2b8a3e,color:#fff
    classDef layer1 fill:#339af0,stroke:#1864ab,color:#fff
    classDef layer2 fill:#845ef7,stroke:#5f3dc4,color:#fff
    classDef done fill:#868e96,stroke:#495057,color:#fff

    subgraph "E-1: {Epic 1 Name}"
        T1.1.1[T-1.1.1: {task}]:::layer0
        T1.1.2[T-1.1.2: {task}]:::layer0
        T1.2.1[T-1.2.1: {task}]:::layer1
        T1.1.1 --> T1.2.1
        T1.1.2 --> T1.2.1
    end

    subgraph "E-2: {Epic 2 Name}"
        T2.1.1[T-2.1.1: {task}]:::layer0
        T2.1.2[T-2.1.2: {task}]:::critical
        T2.1.1 --> T2.1.2
    end

    T1.2.1 --> T2.1.2
```

## Layer Breakdown

### Layer 0 — No Dependencies (Launch First)
| Task | Epic | Feature | Effort | Critical Path |
|------|------|---------|--------|:---:|
| T-1.1.1 | E-1 | F-1.1 | M | |
| T-1.1.2 | E-1 | F-1.1 | S | |
| T-2.1.1 | E-2 | F-2.1 | M | Yes |

### Layer 1 — Depends on Layer 0
| Task | Epic | Feature | Effort | Depends On | Critical Path |
|------|------|---------|--------|-----------|:---:|
| T-1.2.1 | E-1 | F-1.2 | L | T-1.1.1, T-1.1.2 | |
| T-2.1.2 | E-2 | F-2.1 | XL | T-2.1.1, T-1.2.1 | Yes |

## Critical Path
T-2.1.1 → T-1.2.1 → T-2.1.2
Total: {N} effort units

## Bottleneck Tasks
- T-{x}.{y}.{z}: {N} downstream dependents — delays here cascade
