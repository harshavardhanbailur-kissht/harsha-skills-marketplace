---
description: Safely refactor code with test-verified incremental changes, automatic rollback on failure, and multi-language support
argument-hint: "[file or directory path] [optional: specific refactoring goal]"
---

# /safe-refactor — Test-Verified Incremental Refactoring

Refactor code with a verified safety net: every change is tested before and after, failed tests trigger immediate revert, and public APIs are preserved. Supports JS/TS, Python, Go, Rust, Java/Kotlin, Ruby, PHP, C#.

## Invocation

```
/safe-refactor src/utils/parser.py
/safe-refactor src/api clean up duplication and dead code
/safe-refactor UserService.java decompose the god class
/safe-refactor [file or directory] [optional goal]
```

## Workflow

Load the `safe-refactor` skill and follow its six-phase pipeline: Triage → Environment Check → Baseline Capture → Analysis → Incremental Execute → Report. Safety rules are non-negotiable (green tests before starting, clean git state, atomic commits, test after every change, immediate revert on failure, public API preserved, no behavior changes).
