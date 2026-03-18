---
description: Epistemic codebase documentation for handoffs — evidence-first, confidence-tagged, compliance-aware
argument-hint: "<path to codebase>"
---

# /codebase-documenter — Codebase Handoff Documenter V6

Generate handoff documentation using an epistemic pipeline: ANALYZE → DETECT → GATHER → GENERATE → VERIFY → OUTPUT. Every claim is confidence-tagged with evidence chains.

## Invocation

```
/codebase-documenter ./my-project
/codebase-documenter [point to a repo for knowledge transfer]
```

## Workflow

Load the `codebase-documenter` skill. Auto-detects fintech/healthcare/enterprise domains for compliance-specific documentation (PCI-DSS, HIPAA, SOC2, RBI).
