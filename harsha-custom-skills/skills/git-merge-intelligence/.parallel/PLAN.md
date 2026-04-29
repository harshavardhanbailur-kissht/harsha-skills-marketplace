# Parallel Execution Plan — Fix All Evaluation Defects

## Feature: Reconcile template-phase schema drift, create missing deliverables, fix all material defects
## Created: 2026-04-08

## Dependency Graph

Layer 0 (parallel — no dependencies):
- [ ] TASK-001: Fix Phase 0 CONFLICT-REGISTRY.json to match template schema
- [ ] TASK-002: Fix Phase 0 MERGE-CONTEXT.md initialization to match template schema
- [ ] TASK-003: Create templates/BATCH-PLAN.template.json
- [ ] TASK-004: Add missing fields to MERGE-CONTEXT.template.md (Merge Base, PR Signals)
- [ ] TASK-005: Create SIMULATION-RESULTS.md (sprint + heavy scenarios)

Layer 1 (verification — depends on all Layer 0):
- [ ] TASK-006: Full cross-file consistency validation
