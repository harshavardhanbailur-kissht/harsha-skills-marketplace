# PHASE 0: SAFETY BOOTSTRAP

**Objective:** Initialize the merge resolution environment, verify filesystem permissions, and establish secure working state before any merge analysis begins.

**Critical Note:** This phase MUST complete successfully before proceeding to any subsequent phases. If any hard-stop condition is triggered, halt execution and report the blocker to the user.

---

## Step 1: Verify and Initialize `.gitignore`

### Check if `.gitignore` exists:
```bash
if [ ! -f ".gitignore" ]; then
  echo "[PHASE-0] Creating .gitignore (not found in repo)"
  touch .gitignore
else
  echo "[PHASE-0] .gitignore exists"
fi
```

### Add `.merge-resolver/` to `.gitignore`:
```bash
if ! grep -q "^\.merge-resolver/$" .gitignore; then
  echo ".merge-resolver/" >> .gitignore
  echo "[PHASE-0] Added .merge-resolver/ to .gitignore"
else
  echo "[PHASE-0] .merge-resolver/ already in .gitignore"
fi
```

### Add `.deep-think/` to `.gitignore`:
```bash
if ! grep -q "^\.deep-think/$" .gitignore; then
  echo ".deep-think/" >> .gitignore
  echo "[PHASE-0] Added .deep-think/ to .gitignore"
else
  echo "[PHASE-0] .deep-think/ already in .gitignore"
fi
```

### Hard-stop check: Can we write to `.gitignore`?
```bash
if [ ! -w ".gitignore" ]; then
  echo "[PHASE-0] HARD STOP: .gitignore is read-only"
  echo "Action required: Check filesystem permissions or repository configuration"
  exit 1
fi
echo "[PHASE-0] .gitignore is writable"
```

---

## Step 2: Create and Initialize `.merge-resolver/` Directory

### Create the directory structure:
```bash
mkdir -p .merge-resolver
echo "[PHASE-0] Created .merge-resolver/ directory"
```

### Hard-stop check: Can we write to `.merge-resolver/`?
```bash
if [ ! -w ".merge-resolver" ]; then
  echo "[PHASE-0] HARD STOP: .merge-resolver/ is not writable"
  echo "Action required: Check filesystem permissions"
  exit 1
fi
echo "[PHASE-0] .merge-resolver/ is writable"
```

---

## Step 3: Check Resume Mode

### Look for existing MERGE-CONTEXT.md:
```bash
if [ -f ".merge-resolver/MERGE-CONTEXT.md" ]; then
  echo "[PHASE-0] RESUME MODE DETECTED"
  echo "Reading existing merge context..."
  cat .merge-resolver/MERGE-CONTEXT.md
  echo ""
  echo "[PHASE-0] Checking Phase Status..."

  # Extract Phase Status from MERGE-CONTEXT.md
  PHASE_STATUS=$(grep "## Phase Status" .merge-resolver/MERGE-CONTEXT.md -A 20 | head -20)
  echo "$PHASE_STATUS"

  echo ""
  echo "[PHASE-0] Skipping to first incomplete phase (check Phase Status above)"
  exit 0
else
  echo "[PHASE-0] Fresh merge detected — initializing from templates"
fi
```

---

## Step 4: Initialize Template Files

### Initialize MERGE-CONTEXT.md from template:
```bash
cat > .merge-resolver/MERGE-CONTEXT.md << 'EOF'
# Merge Context

**Initialized:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Mode:** [TO BE DETERMINED]
**Status:** INITIALIZING

## PR Metadata
- Title: [pending]
- Source Branch: [pending]
- Destination Branch: [pending]
- PR URL: [pending]
- Intent: [pending]

## Branch Intent Analysis
- OURS Intent: [pending]
- THEIRS Intent: [pending]
- Intent Categories: FEATURE | REFACTOR | BUGFIX | HOTFIX | DEPENDENCY_UPDATE | MIGRATION | CHORE

## Conflict Inventory
- Total Conflicts: [pending]
- Conflicted Files: [pending]

## Bitbucket Integration
- Status: [pending]
- Mode: git-log-only OR bitbucket-full

## Phase Status
- [ ] Phase 0: Safety Bootstrap
- [ ] Phase 1: Context Building
- [ ] Phase 2: Triage & Classification
- [ ] Phase 3: Resolution Planning
- [ ] Phase 4: Execution
- [ ] Phase 5: Validation

## Credential Warnings
[No warnings yet]

EOF
  echo "[PHASE-0] Created .merge-resolver/MERGE-CONTEXT.md"
```

### Initialize CONFLICT-REGISTRY.json:
```bash
cat > .merge-resolver/CONFLICT-REGISTRY.json << 'EOF'
{
  "schema_version": "1.0",
  "initialized_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "mode": "PENDING",
  "total_conflicts": 0,
  "files": [],
  "summary": {
    "total": 0,
    "by_type": {
      "ADDITIVE": 0,
      "MODIFY_SAME": 0,
      "DELETE_MODIFY": 0,
      "RENAME_MODIFY": 0,
      "SEMANTIC": 0,
      "CONFIG": 0,
      "LOCKFILE": 0,
      "AUTH_SECURITY": 0
    },
    "by_complexity": {
      "TRIVIAL": 0,
      "MODERATE": 0,
      "COMPLEX": 0,
      "CRITICAL": 0
    },
    "by_batch": {
      "0": 0,
      "1": 0,
      "2": 0,
      "3": 0,
      "4": 0,
      "5": 0
    },
    "by_language": {},
    "dependencies_analyzed": false,
    "deep_think_candidates": 0
  },
  "batch_gates": {
    "0": { "status": "pending", "completed_at": null },
    "1": { "status": "pending", "completed_at": null },
    "2": { "status": "pending", "completed_at": null },
    "3": { "status": "pending", "completed_at": null },
    "4": { "status": "pending", "completed_at": null },
    "5": { "status": "pending", "completed_at": null }
  }
}
EOF
  echo "[PHASE-0] Created .merge-resolver/CONFLICT-REGISTRY.json"
```

### Initialize RESOLUTION-LOG.md:
```bash
cat > .merge-resolver/RESOLUTION-LOG.md << 'EOF'
# Resolution Decision Audit Trail

**Started:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Decision Log
[No decisions yet]

EOF
  echo "[PHASE-0] Created .merge-resolver/RESOLUTION-LOG.md"
```

---

## Step 5: Scan for Credential Patterns (Non-Blocking Warnings)

**Objective:** Detect potentially exposed secrets in staged files without blocking merge resolution.

### Check for AWS keys (AKIA pattern):
```bash
echo "[PHASE-0] Scanning for AWS credential patterns..."
if git diff --cached --name-only | xargs grep -l "AKIA[0-9A-Z]\{16\}" 2>/dev/null; then
  echo "[PHASE-0] WARNING: Possible AWS access keys found in staged files"
  echo "  Action: Review staged changes before committing"
  echo "" >> .merge-resolver/MERGE-CONTEXT.md
  echo "## Credential Warnings" >> .merge-resolver/MERGE-CONTEXT.md
  echo "- AWS keys (AKIA pattern) detected in staged files" >> .merge-resolver/MERGE-CONTEXT.md
fi
```

### Check for private keys (-----BEGIN pattern):
```bash
echo "[PHASE-0] Scanning for private key patterns..."
if git diff --cached --name-only | xargs grep -l "-----BEGIN.*PRIVATE KEY" 2>/dev/null; then
  echo "[PHASE-0] WARNING: Possible private keys found in staged files"
  echo "  Action: Review staged changes before committing"
  echo "- Private key material (-----BEGIN) detected in staged files" >> .merge-resolver/MERGE-CONTEXT.md
fi
```

### Check for database URLs with embedded passwords:
```bash
echo "[PHASE-0] Scanning for database URL patterns..."
if git diff --cached --name-only | xargs grep -E "(postgresql|mysql|mongodb)://[^:]+:[^@]+@" 2>/dev/null; then
  echo "[PHASE-0] WARNING: Possible database URLs with passwords found in staged files"
  echo "  Action: Review staged changes before committing"
  echo "- Database URLs with embedded credentials detected in staged files" >> .merge-resolver/MERGE-CONTEXT.md
fi
```

---

## Step 6: Detect Mode Based on Conflict Count

**Objective:** Classify the merge complexity to tailor resolution strategy.

### Count conflicted files:
```bash
CONFLICT_COUNT=$(git diff --name-only --diff-filter=U | wc -l)
echo "[PHASE-0] Detected $CONFLICT_COUNT conflicted files"
```

### Determine and assign MODE:
```bash
if [ "$CONFLICT_COUNT" -le 15 ]; then
  MODE="SPRINT"
  echo "[PHASE-0] MODE: SPRINT (≤15 conflicts)"
elif [ "$CONFLICT_COUNT" -le 40 ]; then
  MODE="STANDARD"
  echo "[PHASE-0] MODE: STANDARD (16-40 conflicts)"
else
  MODE="HEAVY"
  echo "[PHASE-0] MODE: HEAVY (41+ conflicts)"
fi
```

### Write mode to MERGE-CONTEXT.md:
```bash
sed -i "s/\*\*Mode:\*\* \[TO BE DETERMINED\]/**Mode:** $MODE/" .merge-resolver/MERGE-CONTEXT.md
sed -i "s/- Total Conflicts: \[pending\]/- Total Conflicts: $CONFLICT_COUNT/" .merge-resolver/MERGE-CONTEXT.md
echo "[PHASE-0] Wrote MODE=$MODE to MERGE-CONTEXT.md"
```

---

## Step 7: Mark Phase 0 as Complete

### Update Phase Status:
```bash
# Update Phase 0 status to COMPLETE
sed -i "s/- \[ \] Phase 0: Safety Bootstrap/- [x] Phase 0: Safety Bootstrap — COMPLETE/" .merge-resolver/MERGE-CONTEXT.md

echo "[PHASE-0] ========================================"
echo "[PHASE-0] Phase 0 (Safety Bootstrap) COMPLETE"
echo "[PHASE-0] ========================================"
echo ""
echo "Next: PHASE-1-CONTEXT.md"
```

---

## Summary

PHASE-0 accomplishes:
1. ✓ Gitignore verification and security setup
2. ✓ Filesystem permission validation
3. ✓ Directory structure initialization
4. ✓ Resume mode detection
5. ✓ Credential exposure scanning (warnings only)
6. ✓ Conflict complexity classification
7. ✓ Mode assignment and persistence

**Exit Code:** 0 on success, 1 on hard-stop conditions

**References:**
- ai-workspace-gitignore-security.md (security bootstrap decisions)
