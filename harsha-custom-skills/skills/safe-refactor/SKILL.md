---
name: safe-refactor
description: "Safely refactor code with test-verified incremental changes, automatic rollback on failure, and multi-language support. Use this skill whenever the user asks to refactor code, clean up code, improve code quality or readability, reduce complexity, simplify code, fix code smells, pay down technical debt, modernize code, convert or migrate legacy patterns (e.g., callbacks to async/await, old APIs to modern equivalents), or make code more maintainable. Also trigger when the user wants to break up or decompose large functions/classes, extract components into separate modules, remove dead or unused code, or restructure code without breaking things. Trigger on mentions of messy code, spaghetti code, god classes, deeply nested logic, magic numbers, or legacy cleanup. This skill is essential for ANY refactoring task — even small ones — because it enforces the safety net that prevents regressions."
argument-hint: "[file or directory path] [optional: specific refactoring goal]"
---

# Safe Refactor

Incrementally refactor code with a verified safety net. Every change is tested before
and after. Failed tests trigger immediate revert. Public APIs are preserved.

## When NOT to Use

Refactoring is a narrow, specific discipline: behavior-preserving structural change. These adjacent tasks look similar but need different tools:

- **Adding new features** — Use workflow-guardian. Features change behavior; refactoring preserves it.
- **Fixing bugs** — Bug fixes intentionally change behavior ("the wrong output becomes the right output"). If the user says "fix" and names a defect, they want a behavior change, not a restructure.
- **Code review without changes** — If they want an opinion, not a diff, just read the code and discuss. Don't spin up the safety machinery.
- **Performance optimization** — Often changes observable behavior (timing, allocations, ordering). Treat as a separate task with benchmarks, not tests.
- **Security fixes** — Usually change behavior (reject previously-accepted inputs, redact previously-exposed data). Handle as a targeted bug fix.
- **No test suite exists** — Refactoring without tests is flying blind. Offer to add characterization tests first (see Phase 2 guidance below).
- **Exploratory "let me see what this does"** — Read and explain. Don't modify.

## Core Workflow

```
USER REQUEST
      |
[0. TRIAGE] -------------- is this actually refactoring? is scope clear?
      |
[1. ENVIRONMENT CHECK] --- detect language, test runner, git status
      |
[2. BASELINE CAPTURE] ---- run tests, record metrics, create git checkpoint
      |
[3. ANALYSIS] ------------ identify opportunities, score by impact/risk/effort
      |
[4. INCREMENTAL EXECUTE] - one change at a time, test after each, revert on fail
      |
[5. REPORT] -------------- summary of changes, metrics delta, remaining opportunities
      |
DONE (all tests still pass)
```

### Two Paths: Quick vs. Full

Not every refactoring needs the full five-phase ceremony. Pick the path that matches the scope:

- **Quick Path** (single file, one specific change, <30 lines affected): Skip Phase 3 (no analyzer subagent). Do the change yourself, run tests, commit. Still honor the safety rules — baseline, atomic commit, test after change, revert on failure.
- **Full Path** (multi-file cleanup, "refactor this module," unclear scope): Run all five phases including the analyzer subagent. The overhead is worth it when there are many candidate changes to prioritize.

When in doubt, use the Full Path. The cost is a few extra minutes; the benefit is better prioritization and fewer missed opportunities.

## Safety Rules (and why each one exists)

These rules are the backbone of safe refactoring. They aren't arbitrary — each one exists to prevent a specific failure mode that has burned real teams. Follow them unless the user explicitly overrides one for a specific reason.

1. **All tests pass before starting.** A failing test suite is a broken compass — you can't tell whether *your* change caused the next failure. If baseline tests fail, stop and surface them to the user; offer to skip the failing ones or fix them first before proceeding.

2. **Clean git working directory.** Uncommitted changes make `git checkout -- .` unsafe (it would wipe the user's in-progress work). Ask the user to commit or stash before starting.

3. **Atomic commits after every successful change.** One change per commit means any step can be reverted in isolation later. It also makes `git bisect` useful if a regression surfaces days later.

4. **Run tests after every individual change, not after a batch.** If you change 5 things and tests fail, you now have to debug 5 things at once. The whole point of incremental refactoring is keeping failures attributable to a single edit.

5. **Failed test → immediate revert, not "let me fix the test too."** The temptation to fix-the-fix is strong, but now you're debugging two changes at once. Revert, understand what broke, try a different approach or skip the opportunity. The exception: if the revert itself fails (git weirdness), stop and tell the user.

6. **Preserve public API signatures.** Function names, parameter types, return types, and exported interfaces must not change unless the user explicitly requests it. Breaking callers turns a refactoring into a migration — a different, larger task.

7. **No behavior changes.** If a change would alter output, timing, side effects, or errors for any input, it's not a refactoring — it's a feature or a bug fix. When in doubt, ask: "would any existing test need to change?" If yes, stop.

### Flaky Test Handling

Real test suites have occasional flakes (timing, network, ordering). A single failure isn't always a real regression. When a test fails after your change:

1. **Re-run the failing tests once** (not the whole suite — just the failures).
2. If they pass on re-run AND the failure wasn't obviously caused by your change, treat it as a flake. Log the flake in `.refactor-manifest.md` and proceed.
3. If they fail again, revert as usual.
4. **Do not loop more than once.** Three consecutive re-runs is thrashing, not verification.

This prevents false reverts that would erode confidence in the skill, while keeping the safety net intact for real regressions.

## .refactor-manifest.md (Compaction Resilience)

Create `.refactor-manifest.md` in the project root to survive context compaction.
Read this file at the START of every turn. Update it after every change.

```markdown
# Refactor Manifest
## Session: [timestamp]
## Target: [file/directory]
## Language: [detected]
## Test Runner: [detected]
## Test Command: [exact command]
## Baseline: [X passed, Y failed, Z skipped]

## Completed
- [x] Step 1: [description] — commit [hash]
- [x] Step 2: [description] — commit [hash]

## In Progress
- [ ] Step 3: [description]

## Remaining
- [ ] Step 4: [description] (impact:4, risk:2, effort:1)
- [ ] Step 5: [description] (impact:3, risk:3, effort:2)

## Reverted
- Step X: [description] — REVERTED (test failure: [details])
```

**Read this manifest before doing anything.** If it exists, resume from where you left off.

---

## Phase 0: Triage (30 seconds)

Before firing up scripts and subagents, do a fast sanity check. Most refactoring requests are clear, but catching a misframed task here saves a lot of wasted work.

Ask yourself:
1. **Is this actually a refactoring?** If the user describes a behavior change (new feature, bug fix, performance goal), stop and redirect. See the "When NOT to Use" section.
2. **Is the scope obvious?** If the user says "clean up this file" and points at a specific file, scope is clear. If they say "refactor the backend," ask one clarifying question: "Do you want me to focus on a specific file/module, or run a full scan and propose a prioritized list?"
3. **Are there obvious test gaps?** Glance at the test folder. If the target code has no tests at all, surface this before starting — offer to add characterization tests first, or confirm the user wants to proceed without a safety net.

Output a one-line restatement of what you're about to do, then proceed. Example:
> "Refactoring `src/utils/parser.py` for readability — Quick Path, baseline tests first."

This keeps the user oriented and catches misunderstandings before any files change.

## Phase 1: Environment Check

Run the environment detection script:

```bash
bash <skill-path>/scripts/detect_environment.sh [project-root]
```

This outputs JSON with: language, framework, test_runner, test_command, git_status, git_clean.

If git is not clean, STOP. Tell the user to commit or stash changes first.

If no test runner is detected, ask the user for the test command.

**Read the language-specific reference file** for the detected language:
- JavaScript/TypeScript → `references/javascript-typescript.md`
- Python → `references/python.md`
- Go → `references/go.md`
- Rust → `references/rust.md`
- Java/Kotlin → `references/java-kotlin.md`
- Ruby, PHP, C# → `references/ruby-php-csharp.md`
- Any language → `references/refactoring-catalog.md` (always useful)

## Phase 2: Baseline Capture

Run the baseline capture script:

```bash
bash <skill-path>/scripts/capture_baseline.sh [project-root] [test-command]
```

This:
1. Creates a git checkpoint tag `refactor-baseline-[timestamp]`
2. Runs the test suite
3. Captures test results (total, passed, failed, skipped)
4. Outputs JSON baseline metrics

If any tests FAIL at baseline, STOP. Report the failures to the user.
Refactoring requires a green test suite.

Create the `.refactor-manifest.md` with baseline data.

### If There Are No Tests (Characterization Tests)

When the target code has no test coverage, don't just refuse — offer the user a path:

1. Read the target code and identify its public entry points.
2. For each entry point, call it with a small set of representative inputs and record the actual output (even if the output looks "wrong" — the goal is capturing *current* behavior).
3. Write assertions against those recorded outputs. These are characterization tests: they pin down what the code does today.
4. Commit them as "test: characterize current behavior of X" — now you have a safety net.
5. Refactor against these tests.

Characterization tests aren't a statement about what the code *should* do. They're a snapshot of what it *does* do, which is exactly what you need to detect regressions during refactoring.

## Phase 3: Analysis

Launch the analyzer subagent to identify refactoring opportunities:

```
Agent tool:
  prompt: Contents of <skill-path>/agents/analyzer.md
  + "Target: [file/directory path]"
  + "Language: [detected language]"
  + "User goal: [what the user asked for]"
  description: "Analyze refactoring opportunities"
  model: sonnet
```

The analyzer returns a prioritized list scored by:
- **Impact** (1-5): How much does this improve the code?
- **Risk** (1-5): How likely is this to break something?
- **Effort** (1-5): How many lines/files change?
- **Priority**: (Impact * 2 + (6 - Risk)) / Effort — higher is better

Present the top 10 opportunities to the user. Ask which to proceed with,
or confirm "all" to execute in priority order.

## Phase 4: Incremental Execution

For EACH approved refactoring opportunity, in priority order:

### Step 4a: Plan the Change
- Identify exact files and lines to modify
- Confirm the change is behavior-preserving
- Check that public API signatures are unchanged

### Step 4b: Apply the Change
- Make the minimum edit needed
- Follow patterns from the language-specific reference file

### Step 4c: Verify

```bash
bash <skill-path>/scripts/verify_step.sh [project-root] [test-command]
```

**If tests PASS:**
1. Commit: `git add -A && git commit -m "refactor: [description]"`
2. Update `.refactor-manifest.md` — move to Completed
3. Proceed to next opportunity

**If tests FAIL:**
1. Re-run just the failing tests once (rule out flakes — see Flaky Test Handling above).
2. If still failing, revert: `git checkout -- .`
3. Log in `.refactor-manifest.md` under Reverted with failure reason
4. Skip this opportunity, proceed to next

### Step 4d: Check for Cascade Effects
After every 3 successful changes, do a full test run to catch any
interaction effects between refactorings.

### Step 4e: Communicate Progress

The user should never wonder "what is it doing?" during a long refactor. Keep them oriented:

- After the first successful change, surface a brief confirmation: "✓ Step 1: [description] — committed. Running step 2 of N."
- Every 3 changes (aligned with the cascade check), post a short progress summary showing completed / remaining / reverted counts.
- On a revert, say so immediately with the failure reason — don't hide it. The user needs to know if their code had a hidden coupling.
- Skip the narration for each individual test run — that's noise.

The goal is calm, outcome-focused updates: enough signal that the user can leave the tab and come back, not a running commentary.

## Phase 5: Report

After all opportunities are processed (or user says stop):

```markdown
# Refactoring Report

## Summary
- Changes applied: X of Y attempted
- Changes reverted: Z (with reasons)
- Tests: [before] → [after]

## Changes Made
1. [description] — [file:line] — commit [hash]
2. [description] — [file:line] — commit [hash]

## Remaining Opportunities
1. [description] — skipped because [reason]

## Metrics Delta
- Complexity: [before] → [after] (if measurable)
- Lines of code: [before] → [after]
```

If ALL changes were reverted, tell the user honestly — the code may be more
tightly coupled than expected, or the test suite may not cover enough to
refactor safely. Suggest adding characterization tests first.

---

## Reference Files

Read these as needed — they contain dense, actionable patterns:

| File | When to Read |
|------|-------------|
| `references/refactoring-catalog.md` | Always — language-agnostic patterns, code smells |
| `references/javascript-typescript.md` | JS/TS projects (React, Node, Deno, Bun) |
| `references/python.md` | Python projects (Django, Flask, FastAPI) |
| `references/go.md` | Go projects |
| `references/rust.md` | Rust projects |
| `references/java-kotlin.md` | JVM projects (Spring, Android) |
| `references/ruby-php-csharp.md` | Ruby, PHP 8+, C#/.NET projects |
| `references/test-runner-parsing.md` | Understanding test output formats |
| `agents/analyzer.md` | Subagent prompt for codebase analysis |

## Scripts

All scripts are deterministic (no LLM reasoning), cross-platform (macOS + Linux),
and output JSON for easy parsing:

| Script | Purpose |
|--------|---------|
| `scripts/detect_environment.sh` | Detect language, framework, test runner, git status |
| `scripts/capture_baseline.sh` | Run tests, capture metrics, create git checkpoint |
| `scripts/verify_step.sh` | Run tests after each change, report pass/fail |

## Key Principles

**Why incremental?** A single large refactoring that breaks tests is nearly
impossible to debug. Ten small refactorings with test verification after each
one means you always know exactly which change caused a failure.

**Why atomic commits?** If change #7 out of 10 breaks something a week later,
you can `git revert` just that one commit without losing changes 1-6 and 8-10.

**Why preserve public APIs?** Refactoring is about internal quality. If callers
need to change, that's a migration, not a refactoring. Scope creep here is
the #1 cause of "refactoring that broke everything."

**Why revert immediately on test failure?** The temptation is to "fix the fix."
But now you're debugging two changes at once — the refactoring AND the fix.
Revert, understand why it failed, and try a different approach.
