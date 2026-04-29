# PHASE 4: CONFLICT RESOLUTION EXECUTION

**Objective:** Execute the batch resolution plan — resolve every conflicted file according to its assigned strategy, in dependency order, with checkpoint persistence after each batch.

**Prerequisite**: Phase 3 COMPLETE (`BATCH-PLAN.json` must exist with all strategies assigned)

**HARD RULE**: NEVER call `git add`, `git commit`, `git push`, or `git merge`. Only edit file contents to remove conflict markers. The human decides when to stage and commit.

---

## Overview

This phase:
1. Reads BATCH-PLAN.json from Phase 3
2. Executes batches sequentially (Batch 0 → 1 → 2 → ... → N)
3. Within each batch, resolves files using assigned strategies
4. Checkpoints progress after each batch (compaction-resilient)
5. Invokes Deep Thinker for RED/DEEP_THINK files
6. Logs every decision to RESOLUTION-LOG.md
7. Presents YELLOW/RED files for human review

**Expected Output**:
- Resolved source files (conflict markers removed)
- `.merge-resolver/RESOLUTION-LOG.md` ← decision audit trail
- `.merge-resolver/MERGE-CONTEXT.md` ← batch completion status
- `.merge-resolver/BATCH-PLAN.json` ← updated with per-file resolution status

---

## Execution Flow

### Step 1: Pre-flight Check

```bash
# Verify Phase 3 is COMPLETE
if ! grep -q "Phase 3.*COMPLETE" .merge-resolver/MERGE-CONTEXT.md; then
  echo "[PHASE-4] ERROR: Phase 3 not marked COMPLETE."
  exit 1
fi

# Verify BATCH-PLAN.json exists
if [ ! -f ".merge-resolver/BATCH-PLAN.json" ]; then
  echo "[PHASE-4] ERROR: BATCH-PLAN.json missing."
  exit 1
fi

# Check for resume: which batches are already done?
LAST_COMPLETED_BATCH=$(grep "Batch.*COMPLETE" .merge-resolver/MERGE-CONTEXT.md | tail -1 | grep -o "Batch [0-9]*" | awk '{print $2}')
if [ -n "$LAST_COMPLETED_BATCH" ]; then
  START_BATCH=$((LAST_COMPLETED_BATCH + 1))
  echo "[PHASE-4] RESUME: Starting from Batch $START_BATCH"
else
  START_BATCH=0
  echo "[PHASE-4] Fresh execution: Starting from Batch 0"
fi
```

### Step 2: Batch Execution Loop

For each batch in order:

```
FOR batch IN BATCH-PLAN.batches[START_BATCH..N]:
    1. Log batch start
    2. FOR EACH file IN batch.files:
        a. Read current file state (may have conflict markers)
        b. Apply resolution strategy
        c. Log decision to RESOLUTION-LOG.md
        d. Update file status in BATCH-PLAN.json
    3. Checkpoint: write batch completion to MERGE-CONTEXT.md
    4. Gate check: if batch has YELLOW/RED files, present for review
```

### Step 3: Resolution Strategy Implementations

#### 3.1: KEEP_OURS

Accept our branch version entirely. Remove conflict markers, keep `HEAD` content.

```bash
resolve_keep_ours() {
  local FILE="$1"
  echo "[PHASE-4] Resolving $FILE → KEEP_OURS"
  
  # Extract our version from merge index (stage 2)
  git show :2:"$FILE" > "$FILE"
  
  echo "[PHASE-4] ✓ $FILE resolved (KEEP_OURS)"
}
```

#### 3.2: KEEP_THEIRS

Accept their branch version entirely. Remove conflict markers, keep incoming content.

```bash
resolve_keep_theirs() {
  local FILE="$1"
  echo "[PHASE-4] Resolving $FILE → KEEP_THEIRS"
  
  # Extract their version from merge index (stage 3)
  git show :3:"$FILE" > "$FILE"
  
  echo "[PHASE-4] ✓ $FILE resolved (KEEP_THEIRS)"
}
```

#### 3.3: KEEP_BOTH

Merge both additions. For additive conflicts where both branches add non-overlapping code.

```bash
resolve_keep_both() {
  local FILE="$1"
  local LANG="${2:-unknown}"
  echo "[PHASE-4] Resolving $FILE → KEEP_BOTH"
  
  # Extract three versions from git index
  git show :1:"$FILE" > /tmp/merge_base.txt 2>/dev/null || touch /tmp/merge_base.txt
  git show :2:"$FILE" > /tmp/merge_ours.txt 2>/dev/null || touch /tmp/merge_ours.txt
  git show :3:"$FILE" > /tmp/merge_theirs.txt 2>/dev/null || touch /tmp/merge_theirs.txt
  
  # Inline Python script to parse conflict markers and merge both sides
  local MERGED_OUTPUT
  MERGED_OUTPUT=$(python3 << 'PYTHON_EOF'
import sys
import json

def resolve_keep_both_py(file_content, language):
    """Parse conflict markers and merge both sides intelligently."""
    lines = file_content.split('\n')
    result = []
    in_conflict = False
    ours_block = []
    theirs_block = []
    section = None
    
    for line in lines:
        if line.startswith('<<<<<<<'):
            in_conflict = True
            section = 'ours'
            ours_block = []
            theirs_block = []
        elif line.startswith('=======') and in_conflict:
            section = 'theirs'
        elif line.startswith('>>>>>>>') and in_conflict:
            in_conflict = False
            merged = merge_blocks(ours_block, theirs_block, language)
            result.extend(merged)
        elif in_conflict:
            if section == 'ours':
                ours_block.append(line)
            else:
                theirs_block.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def merge_blocks(ours, theirs, language):
    """Merge two code blocks, deduplicating imports and merging configs."""
    if language in ['typescript', 'javascript', 'js', 'ts']:
        ours_imports = [l for l in ours if l.strip().startswith('import')]
        ours_code = [l for l in ours if not l.strip().startswith('import')]
        theirs_imports = [l for l in theirs if l.strip().startswith('import')]
        theirs_code = [l for l in theirs if not l.strip().startswith('import')]
        all_imports = list(dict.fromkeys(ours_imports + theirs_imports))
        return all_imports + ours_code + theirs_code
    
    elif language == 'go':
        return merge_go_imports(ours, theirs)
    
    elif language == 'python':
        return merge_python_imports(ours, theirs)
    
    elif language in ['json']:
        return merge_json_blocks(ours, theirs)
    
    elif language in ['yaml', 'yml']:
        return merge_yaml_blocks(ours, theirs)
    
    elif language in ['css', 'scss']:
        return merge_css_blocks(ours, theirs)
    
    else:
        return ours + theirs

def merge_go_imports(ours, theirs):
    """Merge Go import blocks, deduplicating multi-line imports."""
    seen = set()
    merged = []
    for block in [ours, theirs]:
        for line in block:
            stripped = line.strip()
            if stripped and stripped not in seen:
                merged.append(line)
                seen.add(stripped)
    return merged

def merge_python_imports(ours, theirs):
    """Merge Python imports: stdlib → third-party → local."""
    stdlib_set = {'os', 'sys', 're', 'json', 'math', 'datetime', 'collections', 'itertools', 'functools'}
    stdlib_imports = []
    third_party = []
    local_imports = []
    
    for block in [ours, theirs]:
        for line in block:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('from') or stripped.startswith('import'):
                parts = stripped.split()
                module = parts[1] if len(parts) > 1 else ''
                if module in stdlib_set:
                    if stripped not in stdlib_imports:
                        stdlib_imports.append(line)
                elif module.startswith('.'):
                    if stripped not in local_imports:
                        local_imports.append(line)
                else:
                    if stripped not in third_party:
                        third_party.append(line)
    
    return stdlib_imports + [''] * (1 if stdlib_imports and third_party else 0) + third_party + [''] * (1 if third_party and local_imports else 0) + local_imports

def merge_json_blocks(ours, theirs):
    """Merge JSON objects: prefer theirs for conflicts, keep both for new keys."""
    try:
        ours_text = '\n'.join(ours).strip()
        theirs_text = '\n'.join(theirs).strip()
        ours_obj = json.loads(ours_text) if ours_text else {}
        theirs_obj = json.loads(theirs_text) if theirs_text else {}
        merged = {**ours_obj, **theirs_obj}
        return json.dumps(merged, indent=2).split('\n')
    except:
        return ours + theirs

def merge_yaml_blocks(ours, theirs):
    """Merge YAML blocks: prefer theirs, keep both for additions."""
    merged = {}
    for line in ours + theirs:
        if ':' in line:
            key, val = line.split(':', 1)
            merged[key.strip()] = val.strip()
    return [f"{k}: {v}" for k, v in merged.items()]

def merge_css_blocks(ours, theirs):
    """Merge CSS: deduplicate selectors and rule blocks."""
    seen = set()
    merged = []
    for line in ours + theirs:
        stripped = line.strip()
        if stripped and stripped not in seen:
            merged.append(line)
            seen.add(stripped)
    return merged

# Read working copy with conflict markers
try:
    with open(sys.argv[1], 'r') as f:
        content = f.read()
except:
    content = ""

language = sys.argv[2] if len(sys.argv) > 2 else "unknown"
resolved = resolve_keep_both_py(content, language)
print(resolved)
PYTHON_EOF
"$FILE" "$LANG"
  )
  
  if [ $? -eq 0 ] && [ -n "$MERGED_OUTPUT" ]; then
    echo "$MERGED_OUTPUT" > "$FILE"
    git add "$FILE"
    echo "[PHASE-4] ✓ $FILE resolved (KEEP_BOTH)"
  else
    # Fallback: simple marker removal and concatenation
    sed -i '/^<<<<<<<\|^=======\|^>>>>>>>/d' "$FILE"
    git add "$FILE"
    echo "[PHASE-4] ⚠ $FILE resolved via fallback (KEEP_BOTH)"
  fi
}
```

**KEEP_BOTH Detailed Logic for Common Patterns:**

```python
def resolve_keep_both(file_content, language):
    """
    Parse conflict markers and keep both sides.
    Handles import deduplication and logical ordering.
    """
    lines = file_content.split('\n')
    result = []
    in_conflict = False
    ours_block = []
    theirs_block = []
    section = None  # 'ours' or 'theirs'
    
    for line in lines:
        if line.startswith('<<<<<<<'):
            in_conflict = True
            section = 'ours'
            ours_block = []
            theirs_block = []
        elif line.startswith('=======') and in_conflict:
            section = 'theirs'
        elif line.startswith('>>>>>>>') and in_conflict:
            in_conflict = False
            # Merge both blocks
            merged = merge_blocks(ours_block, theirs_block, language)
            result.extend(merged)
        elif in_conflict:
            if section == 'ours':
                ours_block.append(line)
            else:
                theirs_block.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def merge_blocks(ours, theirs, language):
    """Merge two code blocks with language-aware logic."""
    
    if language in ['typescript', 'javascript', 'js', 'ts']:
        # TypeScript/JavaScript: deduplicate imports, preserve order
        ours_imports = [l for l in ours if l.strip().startswith('import')]
        ours_code = [l for l in ours if not l.strip().startswith('import')]
        theirs_imports = [l for l in theirs if l.strip().startswith('import')]
        theirs_code = [l for l in theirs if not l.strip().startswith('import')]
        
        all_imports = list(dict.fromkeys(ours_imports + theirs_imports))
        return all_imports + ours_code + theirs_code
    
    elif language == 'go':
        # Go: merge import blocks, handle multi-line imports
        seen = set()
        merged = []
        for line in ours + theirs:
            stripped = line.strip()
            if stripped and stripped not in seen and not stripped.startswith('//'):
                merged.append(line)
                seen.add(stripped)
        return merged
    
    elif language == 'python':
        # Python: organize imports (stdlib → third-party → local) with blank separators
        stdlib_set = {'os', 'sys', 're', 'json', 'math', 'datetime', 'collections', 
                      'itertools', 'functools', 'pathlib', 'typing', 'subprocess', 'logging'}
        stdlib_imports = []
        third_party = []
        local_imports = []
        
        for line in ours + theirs:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Identify import category
            if stripped.startswith('from') or stripped.startswith('import'):
                parts = stripped.split()
                module = parts[1] if len(parts) > 1 else ''
                # Remove trailing period for relative imports
                module = module.rstrip('.')
                
                if module in stdlib_set or module.startswith('__'):
                    if stripped not in stdlib_imports:
                        stdlib_imports.append(line)
                elif module.startswith('.'):
                    if stripped not in local_imports:
                        local_imports.append(line)
                else:
                    if stripped not in third_party:
                        third_party.append(line)
        
        result = []
        if stdlib_imports:
            result.extend(stdlib_imports)
        if third_party:
            if result:
                result.append('')
            result.extend(third_party)
        if local_imports:
            if result:
                result.append('')
            result.extend(local_imports)
        return result if result else (ours + theirs)
    
    elif language == 'json':
        # JSON: merge top-level object keys, prefer theirs for conflicts
        try:
            ours_text = '\n'.join(ours).strip()
            theirs_text = '\n'.join(theirs).strip()
            ours_obj = json.loads(ours_text) if ours_text and ours_text != '{}' else {}
            theirs_obj = json.loads(theirs_text) if theirs_text and theirs_text != '{}' else {}
            merged = {**ours_obj, **theirs_obj}
            return json.dumps(merged, indent=2).split('\n')
        except (json.JSONDecodeError, ValueError):
            return ours + theirs
    
    elif language in ['yaml', 'yml']:
        # YAML: merge top-level keys, prefer theirs for conflicts
        merged = {}
        for line in ours + theirs:
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    if key:
                        merged[key] = val
        return [f"{k}: {v}" for k, v in merged.items()] if merged else (ours + theirs)
    
    elif language in ['css', 'scss', 'sass']:
        # CSS/SCSS: merge rule blocks, deduplicate selectors
        seen = set()
        merged = []
        for line in ours + theirs:
            stripped = line.strip()
            if stripped and stripped not in seen and not stripped.startswith('/*'):
                merged.append(line)
                seen.add(stripped)
        return merged if merged else (ours + theirs)
    
    else:
        # Default fallback: concatenate both blocks
        return ours + theirs
```

#### 3.4: MANUAL_MERGE

AI-assisted merge with semantic understanding. This is the core intelligence.

```python
def resolve_manual_merge(file_path, base, ours, theirs, intent_ours, intent_theirs, language):
    """
    Intelligent merge using semantic analysis.
    
    Process:
    1. Parse conflict regions
    2. For each region, analyze what changed and why
    3. Apply intent-driven resolution
    4. Validate result compiles (language-specific)
    5. Assign confidence level
    """
    
    # Read all three versions
    # Identify conflict hunks
    # For each hunk:
    #   - What did ours change? (diff base → ours)
    #   - What did theirs change? (diff base → theirs)
    #   - Are changes compatible?
    #   - If yes: merge both changes
    #   - If no: use intent to decide priority
    
    # Intent rules:
    # HOTFIX > BUGFIX > FEATURE > REFACTOR > CHORE
    # Higher priority intent wins in direct conflict
    
    # Language-specific merge:
    # TypeScript: preserve type annotations from the broader type
    # Go: preserve interface satisfaction
    # Python: preserve function signatures
    # JSON: deep-merge objects, concatenate arrays (deduplicated)
    
    pass
```

**Per-Language MANUAL_MERGE Rules:**

| Language | Merge Rule |
|----------|-----------|
| TypeScript | Wider types win (union > intersection). Preserve all exports. |
| Go | Interface must remain satisfied. Struct field order follows Go convention (exported first). |
| Python | Function signature from newer commit wins. Preserve all decorators. |
| JSON (package.json) | Deep merge `dependencies`, `devDependencies`. Higher version wins. Scripts: keep both. |
| YAML (docker-compose) | Deep merge services. Preserve all port mappings. |
| CSS/SCSS | Keep both rules. Later rule wins for property conflicts. |
| Markdown | Keep both content sections. Resolve heading conflicts by content. |

#### 3.5: REGENERATE

Delete the file and regenerate from source.

```bash
resolve_regenerate() {
  local FILE="$1"
  echo "[PHASE-4] Resolving $FILE → REGENERATE"
  
  case "$FILE" in
    package-lock.json|yarn.lock|pnpm-lock.yaml)
      # Accept ours package.json first (should already be resolved)
      git show :2:"$FILE" > "$FILE" 2>/dev/null || true
      echo "[PHASE-4] NOTE: Run 'npm install' after all conflicts resolved to regenerate"
      ;;
    go.sum)
      # Delete and regenerate
      git show :2:"$FILE" > "$FILE" 2>/dev/null || true
      echo "[PHASE-4] NOTE: Run 'go mod tidy' after all conflicts resolved to regenerate"
      ;;
    poetry.lock)
      git show :2:"$FILE" > "$FILE" 2>/dev/null || true
      echo "[PHASE-4] NOTE: Run 'poetry lock' after all conflicts resolved to regenerate"
      ;;
    *)
      # Unknown lockfile — keep ours as safe default
      git show :2:"$FILE" > "$FILE"
      echo "[PHASE-4] WARNING: Unknown lockfile type. Kept OURS version."
      ;;
  esac
  
  echo "[PHASE-4] ✓ $FILE resolved (REGENERATE)"
}
```

#### 3.6: DEEP_THINK

Invoke multi-expert analysis for complex/security-critical conflicts.

```
DEEP THINKER INVOCATION:

For each DEEP_THINK file:

1. Prepare context:
   - Base version (git show :1:FILE)
   - Ours version (git show :2:FILE)  
   - Theirs version (git show :3:FILE)
   - File's role in architecture (from dependency graph)
   - Intent analysis for both branches
   - Review comments (if available from Bitbucket)

2. Expert panel:
   - Security Expert (for AUTH_SECURITY files)
   - Language Expert (TypeScript/Go/Python specialist)
   - Architecture Expert (cross-module impact assessment)

3. Output:
   - Recommended resolution
   - Confidence level (GREEN/YELLOW/RED)
   - Uncertainty notes
   - Reversal commands

4. If confidence < 70% (RED):
   - DO NOT auto-resolve
   - Present to human with full expert analysis
   - Include specific questions for the developer
```

### Step 4: Decision Logging

Every resolution decision is logged to `.merge-resolver/RESOLUTION-LOG.md`:

```markdown
### Decision: src/types/user.ts

- **Timestamp**: 2026-04-08T10:15:00Z
- **Batch**: 1 (Types & Interfaces)
- **Conflict Type**: MODIFY_SAME
- **Strategy**: MANUAL_MERGE
- **Resolution**: Merged both type extensions — ours added `lastLogin: Date`, theirs added `preferences: UserPrefs`
- **Confidence**: 🟢 GREEN (85)
- **Reasoning**: Both branches extend the same interface with non-overlapping fields. No type narrowing detected.
- **Reversal**: `git show :2:src/types/user.ts > src/types/user.ts`
- **Reviewed By**: AI (auto-resolved)

---
```

### Step 5: Batch Checkpoint

After each batch completes, write checkpoint:

```bash
checkpoint_batch() {
  local BATCH_ID="$1"
  local RESOLVED="$2"
  local TOTAL="$3"
  local TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  # Append to MERGE-CONTEXT.md
  cat >> .merge-resolver/MERGE-CONTEXT.md << EOF

### Batch $BATCH_ID Checkpoint [$TIMESTAMP]
- Resolved: $RESOLVED / $TOTAL files
- Status: COMPLETE
EOF

  echo "[PHASE-4] Batch $BATCH_ID checkpoint written"
}
```

### Step 6: Human Review Gate

For YELLOW and RED files, present review context:

```markdown
## Files Requiring Human Review

### 🔴 RED: src/auth/jwt-verify.ts
**Why**: AUTH_SECURITY conflict with structural changes to token validation
**What changed**:
- OURS: Added refresh token rotation logic
- THEIRS: Changed JWT signing algorithm from HS256 to RS256
**AI Recommendation**: Keep THEIRS (algorithm upgrade is security-critical)
**Confidence**: 35% — algorithm change affects all downstream token validation
**Question for Developer**: Does the refresh token rotation logic need to be updated for RS256?
**Reversal**: `git show :2:src/auth/jwt-verify.ts > src/auth/jwt-verify.ts`

### 🟡 YELLOW: src/api/billing/charge.ts
**Why**: SEMANTIC conflict — payment amount calculation changed in both branches
**What changed**:
- OURS: Added discount calculation
- THEIRS: Changed tax rate computation
**AI Recommendation**: Merged both changes; discount applied before tax
**Confidence**: 58% — order of operations (discount before tax vs tax before discount) unclear
**Question for Developer**: Should discounts be applied before or after tax calculation?
**Reversal**: `git show :2:src/api/billing/charge.ts > src/api/billing/charge.ts`
```

### Step 7: Mark Phase 4 Complete

```bash
# Count results
TOTAL=$(jq '.batches[].files | length' .merge-resolver/BATCH-PLAN.json | paste -sd+ | bc)
GREEN=$(grep -c "🟢" .merge-resolver/RESOLUTION-LOG.md || echo 0)
YELLOW=$(grep -c "🟡" .merge-resolver/RESOLUTION-LOG.md || echo 0)
RED=$(grep -c "🔴" .merge-resolver/RESOLUTION-LOG.md || echo 0)

# Update Phase Status
sed -i 's/\[ \] Phase 4: Execution/[x] Phase 4: Execution — COMPLETE/' .merge-resolver/MERGE-CONTEXT.md

echo "[PHASE-4] ========================================"
echo "[PHASE-4] Phase 4 (Execution) COMPLETE"
echo "[PHASE-4] ========================================"
echo ""
echo "Results:"
echo "  Total resolved: $TOTAL"
echo "  🟢 GREEN (auto-resolved): $GREEN"
echo "  🟡 YELLOW (needs review): $YELLOW"
echo "  🔴 RED (needs human): $RED"
echo ""
echo "Next: PHASE-5-VALIDATE.md"
```

---

## SPRINT Mode Execution

When MODE = SPRINT (≤15 files):
- All files in single batch
- No batch gating
- Sequential resolution (no parallelism)
- Skip Deep Thinker unless AUTH_SECURITY detected
- Minimal logging (one-line per file)

---

## Error Recovery

| Error | Recovery |
|-------|----------|
| File write fails | Restore from merge index (`git show :2:FILE`) |
| Conflict markers remain after resolution | Re-analyze; may be nested conflict |
| Confidence drops below threshold mid-batch | Pause batch, present for review |
| Context compaction during execution | Read MERGE-CONTEXT.md checkpoints to resume |

**Compaction Recovery Protocol:**
1. Read `.merge-resolver/MERGE-CONTEXT.md`
2. Find last completed batch checkpoint
3. Read `.merge-resolver/BATCH-PLAN.json` for file statuses
4. Resume from first unresolved file in first incomplete batch

---

## Success Criteria

Phase 4 is COMPLETE when:

✓ All files have been resolved (conflict markers removed)
✓ RESOLUTION-LOG.md contains a decision entry for every file
✓ BATCH-PLAN.json statuses updated (resolved/needs-human)
✓ MERGE-CONTEXT.md shows all batch checkpoints
✓ Human review items clearly documented with questions
✓ No remaining `<<<<<<<` markers in any resolved file

**Verification:**
```bash
# Check for remaining conflict markers
REMAINING=$(grep -r "^<<<<<<<" --include="*.ts" --include="*.tsx" --include="*.go" --include="*.py" --include="*.json" . | grep -v node_modules | grep -v .merge-resolver | wc -l)
if [ "$REMAINING" -gt 0 ]; then
  echo "[PHASE-4] WARNING: $REMAINING conflict markers still present"
else
  echo "[PHASE-4] ✓ All conflict markers resolved"
fi
```

**Next**: Phase 5 (VALIDATE) runs multi-layer validation

---

## References
- typescript-conflict-resolution-guide.md (Sections 3-7: Type Merging, Import Resolution)
- go125-gin-conflict-patterns.md (Sections 2-5: Struct Merging, Interface Patterns)
- react19-conflict-patterns.md (Sections 3-6: Component Merging, Hook Patterns)
- python-lambda-authorizer-conflicts.md (Sections 2-4: Handler Merging)
- ai-decision-audit-trail-patterns.md (Sections 2-4: Decision Records, Reversal)
- compaction-resilient-workflow-patterns.md (Sections 3-5: Checkpoint Design)
