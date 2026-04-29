# PHASE 2: CONFLICT TRIAGE

**Status**: Ready for execution
**Purpose**: Classify and triage all conflicted files into batches with dependency analysis
**Prerequisite**: Phase 1 COMPLETE (MERGE-CONTEXT.md must exist and be marked COMPLETE)

---

## Overview

This phase processes every conflicted file to:
1. Determine file type, language, and conflict classification
2. Extract and analyze conflict markers using git merge-base data
3. Assign conflict complexity and batch membership
4. Build dependency graph (imports → dependents)
5. Generate CONFLICT-REGISTRY.json with per-file metadata
6. Update MERGE-CONTEXT.md with inventory summary

**Expected Output**:
- `.merge-resolver/CONFLICT-REGISTRY.json` ← comprehensive file registry
- `.merge-resolver/MERGE-CONTEXT.md` ← Phase 2 completion marker

---

## Execution Flow

### Step 1: Pre-flight Check

```bash
# Verify Phase 1 is COMPLETE
if ! grep -q "Phase 1.*COMPLETE" .merge-resolver/MERGE-CONTEXT.md; then
  echo "ERROR: Phase 1 not marked COMPLETE. Stop."
  exit 1
fi

# Count conflicted files
CONFLICT_COUNT=$(git ls-files --unmerged | awk '{print $4}' | sort -u | wc -l)
echo "Found $CONFLICT_COUNT conflicted files"
```

### Step 2: Per-File Triage Loop

For **each** conflicted file:

#### 2.1: Determine File Type & Language

```bash
FILE="src/components/Button.tsx"

# Extract extension
EXT="${FILE##*.}"

# Map extension to language
case "$EXT" in
  ts|tsx)     LANGUAGE="typescript" ;;
  js|jsx)     LANGUAGE="javascript" ;;
  go)         LANGUAGE="go" ;;
  py)         LANGUAGE="python" ;;
  json)       LANGUAGE="json" ;;
  yaml|yml)   LANGUAGE="yaml" ;;
  css|scss)   LANGUAGE="css" ;;
  md)         LANGUAGE="markdown" ;;
  *)          LANGUAGE="unknown" ;;
esac

# Detect if special file
if [[ "$FILE" == "package.json" || "$FILE" == "package-lock.json" ]]; then
  LANGUAGE="json:lockfile"
elif [[ "$FILE" == "go.sum" ]]; then
  LANGUAGE="go:lockfile"
elif [[ "$FILE" == "poetry.lock" ]]; then
  LANGUAGE="python:lockfile"
fi
```

#### 2.2: Extract Conflict Content

```bash
# Base (common ancestor) version
git show :1:"$FILE" > /tmp/base.txt 2>/dev/null || echo "MISSING" > /tmp/base.txt

# Ours (current branch)
git show :2:"$FILE" > /tmp/ours.txt 2>/dev/null || echo "MISSING" > /tmp/ours.txt

# Theirs (incoming branch)
git show :3:"$FILE" > /tmp/theirs.txt 2>/dev/null || echo "MISSING" > /tmp/theirs.txt

# Store conflict sizes
BASE_SIZE=$(wc -l < /tmp/base.txt)
OURS_SIZE=$(wc -l < /tmp/ours.txt)
THEIRS_SIZE=$(wc -l < /tmp/theirs.txt)
```

#### 2.3: Classify Conflict Type

Use the taxonomy below to assign one primary conflict_type:

| Type | Detection | Resolution Hint |
|------|-----------|-----------------|
| **ADDITIVE** | Base is subset of both Ours and Theirs; no common deletions | KEEP_BOTH usually safe |
| **MODIFY_SAME** | All three versions differ; lines overlap in both Ours/Theirs | Needs manual analysis |
| **DELETE_MODIFY** | One branch deletes, other modifies; intent matters | Analyze semantic importance |
| **RENAME_MODIFY** | File path changed + content modified | Path resolution required |
| **SEMANTIC** | Compiles but may violate runtime/type contracts | Deep Thinker recommended |
| **CONFIG** | Configuration file (*.json, *.yaml, .env*); usually regenerated | Check if regeneration is safer |
| **LOCKFILE** | Lock/dependency file (package-lock.json, go.sum, poetry.lock) | REGENERATE (never manual merge) |
| **AUTH_SECURITY** | Authentication, authorization, secrets, cryptography, permissions | Always Deep Thinker |

**Detection algorithm**:

```python
def classify_conflict(file, base, ours, theirs, language):
    # Priority 1: Special file types
    if file.endswith(('.json.lock', '.lock', 'go.sum', 'poetry.lock')):
        return 'LOCKFILE'
    if file.startswith('.') and file.endswith('env'):
        return 'CONFIG'
    if 'auth' in file.lower() or 'permission' in file.lower():
        if language in ['typescript', 'javascript', 'python', 'go']:
            return 'AUTH_SECURITY'

    # Priority 2: File type heuristics
    if language in ['json', 'yaml', 'toml']:
        return 'CONFIG'

    # Priority 3: Structural analysis
    base_lines = set(base.splitlines())
    ours_lines = set(ours.splitlines())
    theirs_lines = set(theirs.splitlines())

    ours_additions = ours_lines - base_lines
    ours_deletions = base_lines - ours_lines
    theirs_additions = theirs_lines - base_lines
    theirs_deletions = base_lines - theirs_lines

    # Overlap check
    overlap_add = ours_additions & theirs_additions
    overlap_del = ours_deletions & theirs_deletions

    if overlap_add and not overlap_del:
        return 'ADDITIVE'
    if overlap_del and not overlap_add:
        return 'DELETE_MODIFY'
    if overlap_add and overlap_del:
        return 'MODIFY_SAME'

    return 'MODIFY_SAME'  # Default to conservative
```

#### 2.4: Assign Complexity

Based on conflict type, file size, and language:

| Complexity | Criteria |
|-----------|----------|
| **TRIVIAL** | ADDITIVE, <50 lines, no imports affected |
| **MODERATE** | MODIFY_SAME, 50-200 lines, clear semantic boundaries |
| **COMPLEX** | MODIFY_SAME, 200+ lines; OR DELETE_MODIFY; OR multiple functions affected |
| **CRITICAL** | LOCKFILE, AUTH_SECURITY, or SEMANTIC conflicts |

```python
def assign_complexity(conflict_type, file_size, language, imports_count):
    if conflict_type == 'LOCKFILE':
        return 'CRITICAL'
    if conflict_type == 'AUTH_SECURITY':
        return 'CRITICAL'
    if conflict_type == 'SEMANTIC':
        return 'CRITICAL'

    if conflict_type == 'ADDITIVE' and file_size < 50:
        return 'TRIVIAL'
    if conflict_type == 'DELETE_MODIFY':
        return 'COMPLEX'

    if file_size < 50:
        return 'MODERATE'
    if file_size < 200:
        return 'MODERATE'

    return 'COMPLEX'
```

#### 2.5: Determine Batch Assignment

**Batch 0: Foundation (Configs & Lockfiles)**

Files to place in Batch 0 (cite: polyglot-dependency-analysis.md):
- `package.json`, `package-lock.json`, `yarn.lock`
- `go.mod`, `go.sum`
- `tsconfig.json`, `jsconfig.json`
- `Dockerfile`, `docker-compose.yml`
- `amplify.yml`, `.serverless.yml`
- `.env*`, `env.example`
- `postcss.config.js`, `postcss.config.cjs`
- `vite.config.ts`, `vite.config.js`
- `tailwind.config.js`, `tailwind.config.ts`
- `babel.config.js`
- `jest.config.js`, `vitest.config.ts`
- `next.config.js`, `nuxt.config.ts`

**Batch 1: Types & Interfaces**

Files to place in Batch 1 (cite: typescript-conflict-resolution-guide.md):
- `*.d.ts` (TypeScript declaration files)
- `src/types/**/*.ts`, `src/types/**/*.tsx`
- `src/interfaces/**/*.ts`
- `src/schemas/**/*.ts`
- `*.pb.ts`, `*.proto` (Protobuf definitions)
- GraphQL schema files (`*.graphql`, `schema.ts`)
- API contract files (`api.ts`, `contracts/*.ts`)

**Batch 2: Shared Utilities & Middleware**

Files to place in Batch 2 (cite: python-lambda-authorizer-conflicts.md):
- `src/middleware/**/*`
- `src/utils/**/*` (excluding test files)
- `src/helpers/**/*`
- `src/auth/**/*` (auth middleware, not sensitive auth logic)
- `src/lib/**/*` (general libraries)
- `lambda/authorizer/**/*` (Lambda authorizers)
- `src/context/**/*` (React/Vue context providers)

**Batch 3: Implementations**

Files to place in Batch 3 (cite: react19-conflict-patterns.md, go125-gin-conflict-patterns.md):
- `src/components/**/*.tsx`, `src/components/**/*.jsx`
- `src/pages/**/*`
- `src/routes/**/*`
- `src/handlers/**/*` (HTTP handlers, AWS Lambda handlers)
- `src/services/**/*`
- `src/api/**/*` (API endpoints, services)
- `cmd/**/*.go` (Go command entry points)
- `internal/handlers/**/*.go`
- `internal/routes/**/*.go`

**Batch 4: Tests**

Files to place in Batch 4 (cite: vitest-test-conflict-patterns.md):
- `*.test.ts`, `*.test.tsx`, `*.test.js`, `*.test.jsx`
- `*.spec.ts`, `*.spec.tsx`, `*.spec.js`, `*.spec.jsx`
- `*_test.go`
- `tests/**/*`
- `__tests__/**/*`
- `test/**/*`

**Batch 5: Docs & CI**

Files to place in Batch 5 (cite: astro-starlight-conflict-patterns.md):
- `docs/**/*.md`, `*.md` (excluding root README)
- `.github/workflows/**/*` (GitHub Actions)
- `.gitlab-ci.yml`, `.circleci/config.yml`
- `astro.config.mjs`, `astro.config.ts`
- `README.md`, `CONTRIBUTING.md`

**SPRINT MODE Optimization** (≤15 files):
- Assign all files to Batch 0
- Skip dependency analysis (too expensive for small merges)
- Process sequentially in a single batch

**Assignment Logic**:

```python
def assign_batch(file_path, file_size):
    # Batch 0: Configs
    if matches_batch_0_patterns(file_path):
        return 0

    # Batch 1: Types & Interfaces
    if matches_batch_1_patterns(file_path):
        return 1

    # Batch 2: Shared Utilities
    if matches_batch_2_patterns(file_path):
        return 2

    # Batch 3: Implementations
    if matches_batch_3_patterns(file_path):
        return 3

    # Batch 4: Tests
    if matches_batch_4_patterns(file_path):
        return 4

    # Batch 5: Docs & CI (fallback)
    return 5
```

#### 2.6: Dependency Analysis (STANDARD/HEAVY MODE ONLY)

**Skip for SPRINT mode** (≤15 files).

For STANDARD/HEAVY merges:

```bash
# For each file, extract import statements (language-specific)
# Example: TypeScript
grep -E "^import|^export.*from|^require" "$FILE" | \
  sed -E "s|.*from ['\"]([^'\"]+)['\"].*|\1|" | \
  sed -E "s|.*require\(['\"]([^'\"]+)['\"]\).*|\1|" > /tmp/imports.txt

# Resolve relative imports to absolute paths
# ./utils/helper -> src/utils/helper
# ../types/User -> src/types/User
# @/components/Button -> src/components/Button

# Map import to actual source files
# Collect set of "depends_on" (files this file imports)
# Collect set of "depended_by" (files that import this file)
```

**Heuristic-based resolution**:
```python
def resolve_imports(file_path, imports):
    """Map import statements to actual file paths."""
    depends_on = []

    for imp in imports:
        # Absolute import (npm package)
        if not imp.startswith('.') and not imp.startswith('@/'):
            continue  # Skip external dependencies

        # Relative import
        if imp.startswith('./') or imp.startswith('../'):
            resolved = resolve_relative(file_path, imp)
            depends_on.append(resolved)

        # Alias import (@/)
        if imp.startswith('@/'):
            resolved = 'src/' + imp[2:]
            depends_on.append(resolved)

    return depends_on
```

**Build reverse dependency map**:
```python
depended_by = {}
for file in all_files:
    for dep in file.depends_on:
        if dep not in depended_by:
            depended_by[dep] = []
        depended_by[dep].append(file)
```

---

## Step 3: CONFLICT-REGISTRY.json Schema

Generate `.merge-resolver/CONFLICT-REGISTRY.json`:

```json
{
  "files": [
    {
      "path": "src/types/user.ts",
      "language": "typescript",
      "conflict_type": "MODIFY_SAME",
      "complexity": "MODERATE",
      "batch": 1,
      "size_lines": 45,
      "depends_on": [
        "src/types/auth.ts",
        "src/schemas/user-validation.ts"
      ],
      "depended_by": [
        "src/components/UserCard.tsx",
        "src/api/users.ts",
        "src/services/user-service.ts"
      ],
      "status": "pending",
      "confidence": null,
      "resolution_strategy": null,
      "notes": ""
    },
    {
      "path": "package.json",
      "language": "json:lockfile",
      "conflict_type": "MODIFY_SAME",
      "complexity": "CRITICAL",
      "batch": 0,
      "size_lines": 68,
      "depends_on": [],
      "depended_by": [],
      "status": "pending",
      "confidence": null,
      "resolution_strategy": null,
      "notes": "Both branches add dependencies; manual merge required"
    },
    {
      "path": "src/auth/jwt-verify.ts",
      "language": "typescript",
      "conflict_type": "AUTH_SECURITY",
      "complexity": "CRITICAL",
      "batch": 2,
      "size_lines": 120,
      "depends_on": [
        "src/types/auth.ts",
        "src/utils/crypto.ts"
      ],
      "depended_by": [
        "src/middleware/auth.ts",
        "lambda/authorizer/index.ts"
      ],
      "status": "pending",
      "confidence": null,
      "resolution_strategy": "DEEP_THINK",
      "notes": "Authentication logic; requires manual verification"
    }
  ],
  "summary": {
    "total": 68,
    "by_type": {
      "ADDITIVE": 20,
      "MODIFY_SAME": 30,
      "DELETE_MODIFY": 8,
      "RENAME_MODIFY": 2,
      "SEMANTIC": 4,
      "CONFIG": 2,
      "LOCKFILE": 1,
      "AUTH_SECURITY": 1
    },
    "by_complexity": {
      "TRIVIAL": 15,
      "MODERATE": 30,
      "COMPLEX": 20,
      "CRITICAL": 3
    },
    "by_batch": {
      "0": 5,
      "1": 8,
      "2": 12,
      "3": 28,
      "4": 10,
      "5": 5
    },
    "mode": "STANDARD",
    "dependencies_analyzed": true
  }
}
```

---

## Step 4: Update MERGE-CONTEXT.md

Append conflict inventory to `.merge-resolver/MERGE-CONTEXT.md`:

```markdown
## Phase 2: Conflict Triage [COMPLETE]

**Executed**: [TIMESTAMP]
**Total Files**: 68
**Conflicts by Type**:
- ADDITIVE: 20 (29%)
- MODIFY_SAME: 30 (44%)
- DELETE_MODIFY: 8 (12%)
- RENAME_MODIFY: 2 (3%)
- SEMANTIC: 4 (6%)
- CONFIG: 2 (3%)
- LOCKFILE: 1 (1%)
- AUTH_SECURITY: 1 (1%)

**Complexity Distribution**:
- TRIVIAL: 15 (22%)
- MODERATE: 30 (44%)
- COMPLEX: 20 (29%)
- CRITICAL: 3 (4%)

**Batch Distribution** (STANDARD mode):
- Batch 0 (Configs): 5 files
- Batch 1 (Types): 8 files
- Batch 2 (Shared): 12 files
- Batch 3 (Impls): 28 files
- Batch 4 (Tests): 10 files
- Batch 5 (Docs): 5 files

**High-Risk Files** (require Deep Thinker):
- src/auth/jwt-verify.ts (AUTH_SECURITY)
- src/api/billing/charge.ts (SEMANTIC)
- go.sum (LOCKFILE)
- package.json (MODIFY_SAME, critical dependency)

**Dependencies Analyzed**: Yes
**Mode**: STANDARD

---

**Status**: COMPLETE ✓
**Next Phase**: Phase 3 (PLAN)
```

---

## Step 5: HEAVY MODE Deep Thinker Invocation

For files classified as **SEMANTIC** or **AUTH_SECURITY**:

```bash
# Pseudo-code: invoke Deep Thinker pattern
for file in registry['files']:
  if file['conflict_type'] in ['SEMANTIC', 'AUTH_SECURITY']:
    context = build_deep_thinker_context(file)
    call_deep_thinker(context)
    # Store insights in file['notes']
```

---

## Batch Assignment Reference

All batch assignments cite research files:

| Batch | Primary Research | Pattern | Notes |
|-------|------------------|---------|-------|
| 0 | polyglot-dependency-analysis.md | Configs, lockfiles, dotfiles | Process first; enables everything else |
| 1 | typescript-conflict-resolution-guide.md | Type definitions, schemas, contracts | Consumed by Batches 2-3 |
| 2 | python-lambda-authorizer-conflicts.md | Utilities, middleware, auth middleware | Shared across Batch 3 |
| 3 | react19-conflict-patterns.md, go125-gin-conflict-patterns.md | Components, handlers, services | Largest batch; depends on 0-2 |
| 4 | vitest-test-conflict-patterns.md | Test files | Last code batch; minimal risk |
| 5 | astro-starlight-conflict-patterns.md | Docs, CI/CD | No runtime dependencies |

---

## Error Handling

If conflicts are detected during triage:

1. **Missing base version** (git merge-base failure):
   - Mark file status as "error" with note "Failed to extract base version"
   - Treat as COMPLEX conflict
   - Proceed to next file

2. **Unresolvable file path**:
   - Mark status as "error" with note "Unable to resolve import path"
   - Proceed to next file

3. **Circular dependencies**:
   - Flag in summary
   - Adjust batch assignments to break cycles
   - Document in MERGE-CONTEXT.md

---

## Success Criteria

Phase 2 is COMPLETE when:

✓ All conflicted files extracted and classified
✓ CONFLICT-REGISTRY.json generated with all required fields
✓ Dependency graph built (if STANDARD/HEAVY mode)
✓ MERGE-CONTEXT.md updated with Phase 2 COMPLETE marker
✓ No registry entries missing "conflict_type" or "batch"

### Mark Phase 2 Complete

```bash
# Update phase status
sed -i 's/- \[ \] Phase 2: Triage & Classification/- [x] Phase 2: Triage \& Classification — COMPLETE/' .merge-resolver/MERGE-CONTEXT.md

echo "[PHASE-2] ========================================"
echo "[PHASE-2] Phase 2 (Triage & Classification) COMPLETE"
echo "[PHASE-2] ========================================"
echo ""
echo "Next: PHASE-3-PLAN.md"
```

**Next**: Phase 3 (PLAN) reads CONFLICT-REGISTRY.json and creates resolution strategy
