---
description: Systematic web debugging — root cause analysis, safe fixes, framework-specific bug patterns, CWE security detectors, and race-condition protocol
argument-hint: "<bug description, error, or path to scan>"
---

# /ultimate-debugging-tool — Ultimate Debugging Tool

Supersedes `ultimate-debugger` v2.0.0. Adds 5 CWE security detectors (CWE-601, 942, 1321, 943, 347), concurrency/race-condition debugging protocol, hallucination-prevention gating on new imports, AVP CI/CD integration, and a `security-bugs.md` reference with 10 CWE fix templates.

## Invocation

```
/ultimate-debugging-tool React component re-renders infinitely on state change
/ultimate-debugging-tool Intermittent failure in async checkout flow
/ultimate-debugging-tool Audit ./src for CWE security patterns
/ultimate-debugging-tool Three.js memory leak after route change
```

## Workflow

Load the `ultimate-debugging-tool` skill and execute the 5-phase pipeline: context/triage → reproduction/measurement → root cause → fix design with adaptive L1–L8 verification → ship with manifest update. One bug, one verify, one commit. Never applies a fix when confidence < 50% or when a referenced package/method cannot be verified in the installed version.
