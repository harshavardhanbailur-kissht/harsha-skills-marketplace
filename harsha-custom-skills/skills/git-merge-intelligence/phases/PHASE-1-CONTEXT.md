# PHASE 1: CONTEXT BUILDING

**Objective:** Reconstruct the full merge context — who changed what, why, and how the two branches relate — so that every subsequent phase has the information it needs to make informed resolution decisions.

**Prerequisite**: Phase 0 COMPLETE (`.merge-resolver/MERGE-CONTEXT.md` must exist with Phase 0 marked COMPLETE)

---

## Overview

This phase builds the shared memory that drives all downstream decisions:
1. Identify source and destination branches from Git merge state
2. Extract commit histories for both branches (divergence point → HEAD)
3. Classify branch intent from commit messages and branch naming
4. Query Bitbucket API for PR metadata (if credentials available)
5. Extract reviewer comments and inline feedback
6. Build intent summary and write to MERGE-CONTEXT.md

**Expected Output**:
- `.merge-resolver/MERGE-CONTEXT.md` ← updated with full context, Phase 1 COMPLETE

---

## Execution Flow

### Step 1: Pre-flight Check

```bash
# Verify Phase 0 is COMPLETE
if ! grep -q "Phase 0.*COMPLETE" .merge-resolver/MERGE-CONTEXT.md 2>/dev/null; then
  echo "[PHASE-1] ERROR: Phase 0 not marked COMPLETE. Run Phase 0 first."
  exit 1
fi

# Verify we are in a merge state
if [ ! -f ".git/MERGE_HEAD" ]; then
  echo "[PHASE-1] ERROR: No merge in progress (.git/MERGE_HEAD missing)"
  echo "[PHASE-1] Checking for rebase state..."
  if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
    echo "[PHASE-1] Rebase in progress — this skill handles merge conflicts only."
    echo "To abort and switch to merge: git rebase --abort && git merge <branch>"
    exit 1
  fi
  echo "[PHASE-1] No merge or rebase detected. Run 'git merge <branch>' first."
  exit 1
fi

echo "[PHASE-1] Merge state confirmed"
```

### Step 2: Identify Branches

```bash
# Our branch (current HEAD before merge)
OUR_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "[PHASE-1] Our branch: $OUR_BRANCH"

# Their branch (incoming merge)
THEIR_COMMIT=$(cat .git/MERGE_HEAD)
echo "[PHASE-1] Their commit: $THEIR_COMMIT"

# Try to resolve their branch name
THEIR_BRANCH=$(git name-rev --name-only "$THEIR_COMMIT" 2>/dev/null | sed 's|remotes/origin/||')
echo "[PHASE-1] Their branch: $THEIR_BRANCH"

# Find the merge base (common ancestor)
MERGE_BASE=$(git merge-base HEAD "$THEIR_COMMIT")
echo "[PHASE-1] Merge base: $MERGE_BASE"

# Count commits since divergence
OUR_COMMITS=$(git rev-list --count "$MERGE_BASE"..HEAD)
THEIR_COMMITS=$(git rev-list --count "$MERGE_BASE".."$THEIR_COMMIT")
echo "[PHASE-1] Our commits since base: $OUR_COMMITS"
echo "[PHASE-1] Their commits since base: $THEIR_COMMITS"
```

### Step 3: Extract Commit Histories

```bash
# Our branch commits (most recent 50)
echo "[PHASE-1] Extracting our commit history..."
git log --oneline --no-merges "$MERGE_BASE"..HEAD | head -50 > /tmp/our_commits.txt

# Their branch commits (most recent 50)
echo "[PHASE-1] Extracting their commit history..."
git log --oneline --no-merges "$MERGE_BASE".."$THEIR_COMMIT" | head -50 > /tmp/their_commits.txt

# Detailed commits with stats (for intent analysis)
git log --format="%H|%s|%b" --no-merges "$MERGE_BASE"..HEAD | head -50 > /tmp/our_commits_detail.txt
git log --format="%H|%s|%b" --no-merges "$MERGE_BASE".."$THEIR_COMMIT" | head -50 > /tmp/their_commits_detail.txt
```

### Step 4: Classify Branch Intent

Analyze commit messages and branch names to determine intent.

**Branch Name Pattern Matching:**

| Pattern | Intent Category | Example |
|---------|----------------|---------|
| `feature/*`, `feat/*` | FEATURE | `feature/user-dashboard` |
| `fix/*`, `bugfix/*`, `hotfix/*` | BUGFIX / HOTFIX | `fix/login-crash` |
| `refactor/*`, `refact/*` | REFACTOR | `refactor/auth-module` |
| `chore/*`, `ci/*` | CHORE | `chore/update-deps` |
| `deps/*`, `dependency/*` | DEPENDENCY_UPDATE | `deps/react-19` |
| `migration/*`, `migrate/*` | MIGRATION | `migration/postgres-15` |
| `release/*` | RELEASE | `release/v2.3.0` |

**Conventional Commits Analysis:**

```python
def classify_commits(commits):
    """Classify intent from Conventional Commit prefixes."""
    intent_scores = {
        'FEATURE': 0, 'BUGFIX': 0, 'REFACTOR': 0,
        'HOTFIX': 0, 'DEPENDENCY_UPDATE': 0,
        'MIGRATION': 0, 'CHORE': 0
    }
    
    for commit in commits:
        msg = commit.lower()
        if msg.startswith('feat'):
            intent_scores['FEATURE'] += 1
        elif msg.startswith('fix'):
            intent_scores['BUGFIX'] += 1
        elif msg.startswith('refactor'):
            intent_scores['REFACTOR'] += 1
        elif msg.startswith('chore') or msg.startswith('ci'):
            intent_scores['CHORE'] += 1
        elif 'dependency' in msg or 'upgrade' in msg or 'bump' in msg:
            intent_scores['DEPENDENCY_UPDATE'] += 1
        elif 'migrat' in msg:
            intent_scores['MIGRATION'] += 1
        elif 'hotfix' in msg or 'critical' in msg:
            intent_scores['HOTFIX'] += 1
    
    # Return highest-scoring intent
    return max(intent_scores, key=intent_scores.get)
```

**Fallback Heuristics** (when Conventional Commits not used):

```bash
# Count types of changes
ADDED_FILES=$(git diff --name-status "$MERGE_BASE"..HEAD | grep "^A" | wc -l)
MODIFIED_FILES=$(git diff --name-status "$MERGE_BASE"..HEAD | grep "^M" | wc -l)
DELETED_FILES=$(git diff --name-status "$MERGE_BASE"..HEAD | grep "^D" | wc -l)
RENAMED_FILES=$(git diff --name-status "$MERGE_BASE"..HEAD | grep "^R" | wc -l)

# Heuristic classification
# High additions, low deletions → FEATURE
# High modifications, low additions → REFACTOR or BUGFIX
# High deletions → REFACTOR
# High renames → REFACTOR
```

### Step 5: Bitbucket API Integration (STANDARD/HEAVY Mode)

**Skip for SPRINT mode** — git log only.

**Check for credentials:**

```bash
# Check environment variables
if [ -n "$BB_WORKSPACE" ] && [ -n "$BB_REPO" ] && [ -n "$BB_API_TOKEN" ]; then
  echo "[PHASE-1] Bitbucket credentials available"
  BB_MODE="bitbucket-full"
else
  echo "[PHASE-1] No Bitbucket credentials — using git-log-only mode"
  BB_MODE="git-log-only"
fi
```

**If credentials available, fetch PR metadata:**

See `reference/BITBUCKET-API-GUIDE.md` for complete API patterns.

```bash
# Auto-detect PR ID from branch if not provided
if [ -z "$BB_PR_ID" ]; then
  echo "[PHASE-1] Auto-detecting PR ID for branch $THEIR_BRANCH..."
  BB_PR_ID=$(curl -s -u "username:$BB_API_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests?q=source.branch.name=\"$THEIR_BRANCH\"&state=OPEN" \
    | jq -r '.values[0].id // empty')
  
  if [ -z "$BB_PR_ID" ]; then
    echo "[PHASE-1] WARNING: Could not auto-detect PR ID. Falling back to git-log-only."
    BB_MODE="git-log-only"
  else
    echo "[PHASE-1] Detected PR #$BB_PR_ID"
  fi
fi
```

**Fetch and cache PR data:**

```bash
if [ "$BB_MODE" = "bitbucket-full" ]; then
  # Fetch PR metadata
  curl -s -u "username:$BB_API_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID" \
    > .merge-resolver/pr_metadata.json
  
  # Extract PR description for intent analysis
  PR_TITLE=$(jq -r '.title' .merge-resolver/pr_metadata.json)
  PR_DESCRIPTION=$(jq -r '.description' .merge-resolver/pr_metadata.json)
  
  # Fetch PR comments
  curl -s -u "username:$BB_API_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/comments?pagelen=100" \
    > .merge-resolver/pr_comments.json
  
  # Fetch PR commits
  curl -s -u "username:$BB_API_TOKEN" \
    "https://api.bitbucket.org/2.0/repositories/$BB_WORKSPACE/$BB_REPO/pullrequests/$BB_PR_ID/commits?pagelen=100" \
    > .merge-resolver/pr_commits.json
  
  echo "[PHASE-1] PR metadata, comments, and commits cached"
fi
```

**Extract intent-enriching signals from PR:**

```python
def extract_pr_intent(pr_metadata, pr_comments):
    """Extract additional intent signals from PR data."""
    signals = []
    
    # PR title intent
    title = pr_metadata.get('title', '')
    if any(kw in title.lower() for kw in ['breaking', 'major']):
        signals.append('BREAKING_CHANGE')
    if any(kw in title.lower() for kw in ['wip', 'draft', 'poc']):
        signals.append('EXPERIMENTAL')
    
    # Reviewer comments with explicit intent
    for comment in pr_comments:
        content = comment.get('content', {}).get('raw', '')
        if 'should be in' in content.lower() or 'move this to' in content.lower():
            signals.append('REVIEWER_RESTRUCTURE_REQUEST')
        if 'security' in content.lower() or 'vulnerability' in content.lower():
            signals.append('SECURITY_CONCERN_RAISED')
        if 'approved' in content.lower() or 'lgtm' in content.lower():
            signals.append('REVIEWER_APPROVED')
    
    return signals
```

### Step 6: List Conflicted Files

```bash
# Get all conflicted files
CONFLICTED_FILES=$(git diff --name-only --diff-filter=U)
CONFLICT_COUNT=$(echo "$CONFLICTED_FILES" | wc -l)

echo "[PHASE-1] Conflicted files ($CONFLICT_COUNT total):"
echo "$CONFLICTED_FILES"

# Store for Phase 2
echo "$CONFLICTED_FILES" > .merge-resolver/conflicted_files.txt
```

### Step 7: Write MERGE-CONTEXT.md

Update `.merge-resolver/MERGE-CONTEXT.md` with all collected context:

```bash
cat > .merge-resolver/MERGE-CONTEXT.md << CONTEXT_EOF
# Merge Resolution Context

> Persistent shared memory for git-merge-intelligence.
> Every phase reads this first. Every phase writes results here.

## Meta
- **Created**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Last Updated**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Mode**: $MODE
- **Conflict Count**: $CONFLICT_COUNT
- **Repository**: $(basename $(git rev-parse --show-toplevel))

## Phase Status
- [x] Phase 0: Safety Bootstrap — COMPLETE
- [x] Phase 1: Context Building — COMPLETE
- [ ] Phase 2: Triage & Classification
- [ ] Phase 3: Resolution Planning
- [ ] Phase 4: Execution
- [ ] Phase 5: Validation

## PR Metadata
- **Title**: ${PR_TITLE:-"N/A — no Bitbucket credentials"}
- **Description**: ${PR_DESCRIPTION:-"N/A"}
- **Source Branch**: $THEIR_BRANCH
- **Destination Branch**: $OUR_BRANCH
- **PR URL**: ${BB_PR_URL:-"N/A"}
- **Bitbucket Status**: $BB_MODE

## Branch Intent Analysis

### Our Branch ($OUR_BRANCH)
- **Intent Category**: $OUR_INTENT
- **Summary**: $OUR_SUMMARY
- **Commits Since Base**: $OUR_COMMITS
- **Key Commits**:
$(head -10 /tmp/our_commits.txt | sed 's/^/  - /')

### Their Branch ($THEIR_BRANCH)
- **Intent Category**: $THEIR_INTENT
- **Summary**: $THEIR_SUMMARY
- **Commits Since Base**: $THEIR_COMMITS
- **Key Commits**:
$(head -10 /tmp/their_commits.txt | sed 's/^/  - /')

## Conflict Inventory
- **Total Files**: $CONFLICT_COUNT
- **Conflicted Files**:
$(cat .merge-resolver/conflicted_files.txt | sed 's/^/  - /')

## Merge Base
- **Commit**: $MERGE_BASE
- **Date**: $(git log -1 --format="%ci" $MERGE_BASE)

## PR Signals (from Bitbucket, if available)
${PR_SIGNALS:-"N/A — git-log-only mode"}

## Credential Warnings
$(grep "Credential Warnings" -A 5 .merge-resolver/MERGE-CONTEXT.md 2>/dev/null || echo "[No warnings]")

CONTEXT_EOF

echo "[PHASE-1] MERGE-CONTEXT.md updated with full context"
```

### Step 8: Mark Phase 1 Complete

```bash
# Mark Phase 1 complete in MERGE-CONTEXT.md
sed -i 's/- \[ \] Phase 1: Context Building/- [x] Phase 1: Context Building — COMPLETE/' .merge-resolver/MERGE-CONTEXT.md

echo "[PHASE-1] ========================================"
echo "[PHASE-1] Phase 1 (Context Building) COMPLETE"
echo "[PHASE-1] ========================================"
echo ""
echo "Context summary:"
echo "  Mode: $MODE"
echo "  Our branch: $OUR_BRANCH ($OUR_INTENT)"
echo "  Their branch: $THEIR_BRANCH ($THEIR_INTENT)"
echo "  Conflicts: $CONFLICT_COUNT files"
echo "  Bitbucket: $BB_MODE"
echo ""
echo "Next: PHASE-2-TRIAGE.md"
```

---

## SPRINT Mode Shortcut

When MODE = SPRINT (≤15 files), this phase is lightweight:

1. Skip Bitbucket API entirely
2. Use git log for intent (last 10 commits only)
3. Use branch name heuristics for intent classification
4. Write minimal MERGE-CONTEXT.md
5. Proceed directly to Phase 2

```bash
if [ "$MODE" = "SPRINT" ]; then
  echo "[PHASE-1] SPRINT mode — lightweight context building"
  # Only extract branch names, merge base, and conflict list
  # Skip API calls, detailed commit analysis, reviewer comments
fi
```

---

## Graceful Degradation

| Failure | Fallback |
|---------|----------|
| Bitbucket API returns 401 | Switch to git-log-only mode |
| Bitbucket API returns 404 | PR not found; use git log for intent |
| Bitbucket API returns 429 | Rate limited; switch to git-log-only |
| No Conventional Commits | Use file-change heuristics + branch name |
| Merge base not found | Use `git merge-base --octopus` or `--fork-point` |
| Branch name unresolvable | Use commit hash as identifier |

---

## Success Criteria

Phase 1 is COMPLETE when:

✓ Source and destination branches identified
✓ Merge base computed
✓ Commit histories extracted for both branches
✓ Intent classification assigned to both branches
✓ Conflicted file list generated
✓ Bitbucket metadata cached (or gracefully degraded)
✓ MERGE-CONTEXT.md fully populated with Phase 1 COMPLETE marker

**Next**: Phase 2 (TRIAGE) reads MERGE-CONTEXT.md and classifies each conflicted file

---

## References
- intent-extraction-from-pr-signals.md (Sections 1-3: PR Patterns, Commit Analysis)
- bitbucket-api-complete-reference.md (Sections 2-5: Authentication, PR Metadata)
- git-conflict-anatomy.md (Sections 1-2: Merge State, MERGE_HEAD)
- compaction-resilient-workflow-patterns.md (Sections 2-3: State Persistence)
