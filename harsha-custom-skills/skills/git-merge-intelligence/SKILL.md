---
name: git-merge-intelligence
description: |
  Resolve merge conflicts at any scale with contextual understanding — from 5-file sprint fixes
  to 68-file polyglot conflicts across TypeScript, Go, Python, and config layers.
  Reconstructs intent from branch histories and Bitbucket PR metadata, classifies conflicted
  files into dependency-ordered batches, executes resolutions, and validates across tsc, go build,
  ESLint, and test layers. All state persists in .merge-resolver/ for compaction resilience.

  USE THIS SKILL WHEN:
  - "merge conflicts" or "N files in conflict"
  - "large merge" or "PR conflicts"
  - "resolve conflicts" or "merge is broken"
  - "conflict markers" in the codebase
  - User encounters merge failures or asks for help after `git merge`
---

# Git Merge Intelligence

Resolve merge conflicts with contextual understanding that bare Claude Code cannot achieve.

| Aspect | Detail |
|--------|--------|
| **Purpose** | Resolve merge conflicts at any scale with semantic awareness |
| **Output** | `.merge-resolver/` — context, registry, resolution log, decisions |
| **Phases** | SAFETY → CONTEXT → TRIAGE → PLAN → EXECUTE → VALIDATE |
| **Modes** | SPRINT (≤15 files), STANDARD (16-40), HEAVY (41+) |

## Hard Rules

1. **NEVER** call `git add`, `git commit`, `git push`, or `git merge` — resolve markers only
2. **NEVER** write credentials, tokens, or env var values to any file
3. **ALWAYS** run Phase 0 first — `.merge-resolver/` must be in `.gitignore` before any work
4. **ALWAYS** check `.gitignore` contains `.merge-resolver/` before writing to it
5. **ALWAYS** read `MERGE-CONTEXT.md` at the start of every phase for state recovery

## Mode Detection

Before anything else, count conflicted files:

```bash
git diff --name-only --diff-filter=U | wc -l
```

| Mode | Files | Behavior |
|------|-------|----------|
| **SPRINT** | ≤15 | No Bitbucket API. Lightweight context from git log. Single-batch resolution. |
| **STANDARD** | 16-40 | Bitbucket API if credentials available. Multi-batch with dependency ordering. |
| **HEAVY** | 41+ | Full analysis mandatory. Bitbucket API. Deep Thinker for complex conflicts. Batched execution. |

## Phase Execution Order

```
PHASE 0: SAFETY BOOTSTRAP     → Read phases/PHASE-0-SAFETY-BOOTSTRAP.md
    ↓
PHASE 1: CONTEXT BUILDING     → Read phases/PHASE-1-CONTEXT.md
    ↓
PHASE 2: TRIAGE & CLASSIFY    → Read phases/PHASE-2-TRIAGE.md
    ↓
PHASE 3: PLAN                 → Read phases/PHASE-3-PLAN.md
    ↓
PHASE 4: EXECUTE              → Read phases/PHASE-4-EXECUTE.md
    ↓
PHASE 5: VALIDATE             → Read phases/PHASE-5-VALIDATE.md
```

**Phase 0 is NEVER skippable.** Even in resume mode, verify `.gitignore` state.

## Resume Detection

On every invocation, check FIRST:

```bash
if [ -f ".merge-resolver/MERGE-CONTEXT.md" ]; then
  echo "RESUME MODE: Reading existing context..."
  # Read MERGE-CONTEXT.md to recover state
  # Skip completed phases, continue from first incomplete
else
  echo "FRESH START: Beginning Phase 0..."
fi
```

## Phase File Loading

Each phase file is **self-contained**. Load only the phase you need:

| Phase | File | Reads | Writes |
|-------|------|-------|--------|
| 0 | `phases/PHASE-0-SAFETY-BOOTSTRAP.md` | `.gitignore` | `.merge-resolver/`, `.gitignore` |
| 1 | `phases/PHASE-1-CONTEXT.md` | git log, Bitbucket API | `MERGE-CONTEXT.md` |
| 2 | `phases/PHASE-2-TRIAGE.md` | `MERGE-CONTEXT.md`, conflicted files | `CONFLICT-REGISTRY.json` |
| 3 | `phases/PHASE-3-PLAN.md` | `CONFLICT-REGISTRY.json`, research refs | `MERGE-CONTEXT.md` (batch plan) |
| 4 | `phases/PHASE-4-EXECUTE.md` | `CONFLICT-REGISTRY.json`, batch plan | Resolved files, `RESOLUTION-LOG.md` |
| 5 | `phases/PHASE-5-VALIDATE.md` | Resolved files, `RESOLUTION-LOG.md` | Validation results |

## Reference Files — Load When Needed

| Reference | Load When |
|-----------|-----------|
| `reference/BITBUCKET-API-GUIDE.md` | Phase 1, when Bitbucket credentials available |
| `reference/STACK-CONVENTIONS.md` | Phase 2-4, for language-specific resolution patterns |
| `reference/BATCH-DEPENDENCY-RULES.md` | Phase 2-3, for ordering conflicted files into batches |
| `reference/CONFLICT-TYPE-TAXONOMY.md` | Phase 2, for classifying conflict types |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/MERGE-CONTEXT.template.md` | Schema for persistent shared memory |
| `templates/CONFLICT-REGISTRY.template.json` | Per-file conflict tracking with status |
| `templates/BATCH-PLAN.template.json` | Machine-readable batch execution plan |
| `templates/RESOLUTION-LOG.template.md` | Decision audit trail |

## When Deep Thinker Is Needed

**INVOKE** full multi-expert analysis for:
- Semantic conflicts (type changes, interface evolution, cross-module)
- Security-critical code (auth, authorizers, token validation)
- Cross-language interface changes (TypeScript ↔ Go API contracts)
- Conflicts with confidence < 70%

**SKIP** deep analysis for:
- Simple additive conflicts (both branches add non-overlapping code)
- Whitespace / formatting conflicts
- Import ordering conflicts
- Lock file conflicts (regenerate instead)

## Confidence Levels

Every resolution decision gets a confidence tag:

| Level | Meaning | Action |
|-------|---------|--------|
| 🟢 GREEN | High confidence, validated | Auto-resolve |
| 🟡 YELLOW | Medium confidence, needs review | Resolve + flag for human review |
| 🔴 RED | Low confidence or security-critical | Present to human with full context |

## Architecture Reference

See `ARCHITECTURE-DECISIONS.md` for the full rationale behind every design decision.
See `.deep-think/merge-architecture-log.md` for the evolution of architectural thinking.

## Validation Order (Non-Negotiable)

```
1. TypeScript: tsc --noEmit          (catches type errors)
2. Go:         go build ./...        (catches compilation errors)
3. Go:         go vet ./...          (catches common mistakes)
4. ESLint:     npx eslint .          (catches style + logic issues)
5. Tests:      vitest run            (catches behavioral regressions)
6. Tests:      go test ./...         (catches Go behavioral regressions)
```

TypeScript before Go because type definitions often inform Go API contracts.
Go build before ESLint because compilation must pass before linting.
Tests last because they depend on all prior layers being correct.

## Anti-Patterns

| Anti-Pattern | Why Wrong | Instead |
|--------------|-----------|---------|
| Resolving tests before implementations | Tests depend on code | Batch tests last |
| Merging lock files manually | Always breaks | Regenerate: `npm install` / `go mod tidy` |
| Ignoring go.sum conflicts | Checksum mismatch | Delete go.sum, run `go mod tidy` |
| Resolving auth code without deep analysis | Security risk | Always invoke Deep Thinker |
| Skipping Phase 0 | Working files leak to git | Phase 0 is mandatory |
