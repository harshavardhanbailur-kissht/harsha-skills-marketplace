# Git Rerere: Deep Dive Research

## Executive Summary

Git rerere (Reuse Recorded Resolution) is a powerful Git feature that allows developers to record how they resolve merge conflicts and automatically apply the same resolution when identical conflicts appear in the future. This is particularly valuable in complex workflows involving frequent rebasing, long-lived feature branches, or repeated merges. This research provides a comprehensive technical examination of rerere's internals, configuration, workflow, limitations, and integration opportunities for automated merge intelligence systems.

## 1. How Git Rerere Works Internally

### 1.1 Core Concept

Git rerere operates on the principle of recording and reusing conflict resolutions. When a merge conflict occurs (and rerere is enabled), Git:
1. Records the conflicted state (preimage)
2. Stores your manual resolution (postimage)
3. Later, when the same conflict is detected, automatically applies the recorded resolution

The key insight is that rerere identifies conflicts by their **content structure**, not by file paths, making it resilient to changes in file organization.

### 1.2 The Recording Process

When you encounter a conflict and rerere is active:

1. **Conflict Detection**: Git detects the merge conflict and notices rerere is enabled
2. **Hash Generation**: Git creates a SHA-1 hash of the conflicted hunks (stripped of conflict markers)
3. **Directory Creation**: A directory named after this hash is created in `.git/rr-cache/`
4. **Preimage Recording**: The conflicted content is stored as `preimage` file
5. **Manual Resolution**: You resolve the conflict manually in your working directory
6. **Postimage Recording**: When you complete the merge, Git stores your resolved version as `postimage`

The process is completely transparent—Git handles this automatically when rerere is enabled.

### 1.3 The Reuse Process

When rerere encounters a conflict it has seen before:

1. **Conflict Detection**: A new conflict occurs during merge/rebase
2. **Hash Matching**: Git generates the hash of the new conflict
3. **Cache Lookup**: The hash is matched against entries in `.git/rr-cache/`
4. **Three-Way Merge**: If found, Git performs a **three-way merge** between:
   - The earlier conflicted automerge result (preimage)
   - The earlier manual resolution (postimage)
   - The current conflicted automerge result
5. **Automatic Application**: If the three-way merge succeeds cleanly, the result is written to the working tree

This three-way merge approach is crucial: it ensures the cached resolution is still applicable in the current context before auto-applying it.

## 2. The `.git/rr-cache/` Directory Structure

### 2.1 Physical Layout

```
.git/rr-cache/
├── <hash1>/
│   ├── preimage
│   ├── postimage
│   └── thisimage (optional, temporary)
├── <hash2>/
│   ├── preimage
│   ├── postimage
│   └── thisimage (optional, temporary)
└── ...
```

### 2.2 Hash Naming

The hash is derived from the **conflict content itself**, not the filename. The calculation process:

1. **Normalization**: Conflict markers are stripped from the hunks
2. **Aggregation**: If multiple conflicts exist in one file, all hunks are concatenated
3. **Hashing**: SHA-1 hash is computed over the normalized content, with hunks separated by NUL characters
4. **Storage**: The hash becomes the directory name (e.g., `c96db5732e5a8fb4bb3f610d8ce4b167e3fe2580`)

### 2.3 File Contents

#### Preimage
- Contains the **conflicted content** as Git originally presented it
- Includes conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Represents both versions involved in the conflict
- Is the "before" state

#### Postimage
- Contains your **manually resolved version** of the same content
- Does NOT include conflict markers
- Represents the "after" state
- Is the cached resolution to be reused

#### Thisimage (Optional)
- A temporary bookkeeping file
- Used during multi-conflict resolution scenarios
- Tracks the most recently processed conflict
- Cleaned up after merge completion

### 2.4 Plain Text Format

These are plain text files—no binary encoding or compression. This makes them:
- Human-readable for debugging
- Easy to inspect and understand
- Lightweight in most cases
- Compatible with version control

## 3. Enabling Rerere

### 3.1 Global Configuration

Enable globally for all repositories:

```bash
git config --global rerere.enabled true
# OR
git config --global rerere.enabled 1
```

This setting persists in `~/.gitconfig`:
```
[rerere]
    enabled = true
```

### 3.2 Per-Repository Configuration

Enable for a single repository:

```bash
git config rerere.enabled true
```

Stored in `.git/config` for that repository only.

### 3.3 Manual Directory Creation

Alternatively, create the directory explicitly:

```bash
mkdir -p .git/rr-cache
```

This manually enables rerere for that repository (less common than config setting).

### 3.4 Additional Configuration: rerere.autoupdate

By default, when rerere auto-resolves a conflict, it updates the working tree file but **not the index** (staging area). To also update the index automatically:

```bash
git config --global rerere.autoupdate true
```

**Important Distinction**:
- **rerere.enabled = true**: Records and auto-applies resolutions
- **rerere.autoupdate = true**: Also stages (adds to index) auto-resolved files

When `autoupdate` is disabled (default), you'll see `git add` as a necessary step:
```bash
git rerere  # Auto-resolves
git add <file>  # Still required
git commit  # Complete the merge
```

With `autoupdate = true`, the file is staged automatically, making the workflow smoother.

## 4. The Conflict Resolution Workflow

### 4.1 First Encounter: Recording a Resolution

**Scenario**: You're merging a feature branch that conflicts with main.

```bash
git merge feature-branch
# CONFLICT (content): Merge conflict in config.py
# Automatic merge failed; fix conflicts and then commit the result.
```

With rerere enabled, you'll see:
```
Recorded preimage for 'config.py'
```

Git has automatically hashed and recorded the conflict.

**Your manual resolution**:
```bash
# Edit config.py, resolve the conflict manually
# Remove conflict markers, choose the right version(s)
git add config.py
git commit -m "Merge feature-branch"
```

Upon commit, git rerere records your resolution:
```
Recorded resolution for 'config.py'
```

### 4.2 Second Encounter: Reusing the Resolution

Later, you're rebasing the same branch or another branch with the same conflict:

```bash
git rebase main
# CONFLICT (content): Merge conflict in config.py
```

If rerere recognizes this conflict (same hash):
```
config.py: Recorded resolution
config.py: Resolved using recorded resolution
```

**If autoupdate is enabled**, the file is automatically staged and resolved. **If disabled**, you'll see:
```bash
git rerere status
# Recorded resolution for 'config.py'
git add config.py
git rebase --continue
```

### 4.3 Visualization: Single vs. Multiple Conflicts

**Single conflict in a file**:
```
Hash = SHA1(conflict_hunk)
Directory: .git/rr-cache/<hash>/
Files: preimage, postimage
```

**Multiple conflicts in one file**:
```
Hash = SHA1(hunk1 + NUL + hunk2 + NUL + hunk3)
Directory: .git/rr-cache/<hash>/
Files: preimage (contains all 3 conflicts), postimage (resolved)
```

Rerere treats all conflicts in a single record together—you can't selectively reuse just one conflict from a file with multiple conflicts.

## 5. Hashing and Conflict Identification

### 5.1 Conflict Hash Generation

The hash is the **fingerprint of the conflict content**, calculated as:

1. **Extract conflict hunks** from the merge automerge result
2. **Normalize**:
   - Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
   - Remove the common ancestor version (the `|||||||` section)
   - Keep only the two conflicting versions
3. **Concatenate**: Join all hunks with NUL (`\0`) separators
4. **Hash**: Compute SHA-1 of the normalized content

### 5.2 What Constitutes a "Match"

Two conflicts are considered identical if they have the **same hash**, which means:

- **Content matches**: The conflicting lines are identical
- **Structure matches**: The conflict spans the same line ranges in relation to surrounding context
- **File name is irrelevant**: The same conflict in `file1.py` or `file2.py` will match
- **Context matters**: If surrounding code changes, the hash changes

### 5.3 Three-Way Merge Verification

Even with a hash match, rerere performs a **three-way merge** to ensure the cached resolution is still valid:

```
Inputs to three-way merge:
├── Cached preimage (the original conflict)
├── Cached postimage (the recorded resolution)
└── Current conflicted version (what Git computed during this merge)
```

If this merge succeeds cleanly, the resolution is applied. If it fails, rerere refuses to auto-apply and requires manual intervention.

**Why this matters**: The surrounding context might have evolved, making the old resolution incompatible with the current state. The three-way merge detects this.

### 5.4 Collision and Uniqueness

SHA-1 collisions are cryptographically negligible for practical purposes. Each recorded conflict gets a unique directory based on its content signature.

## 6. Git Rerere Subcommands

### 6.1 `git rerere status`

**Purpose**: Display paths with conflicts whose resolutions will be (or have been) recorded.

```bash
git rerere status
```

**Output**:
```
<file1>
<file2>
```

Shows files that:
- Currently have unresolved conflicts in the working directory
- Will have resolutions recorded when you commit

**Useful for**: Checking what conflicts are being tracked before commit.

### 6.2 `git rerere diff`

**Purpose**: Show the difference between the current conflict state and the recorded resolution.

```bash
git rerere diff
```

**Output**: A unified diff showing:
- Left side: Current conflicted content (what you're seeing)
- Right side: Recorded resolution (what was cached)

**Use case**: Verify the cached resolution makes sense before accepting it.

### 6.3 `git rerere remaining`

**Purpose**: Display paths with conflicts that **cannot** be auto-resolved by rerere.

```bash
git rerere remaining
```

**Output**: Paths that:
- Have conflicts but no cached resolution exists
- Have conflicts that rerere recognizes but the three-way merge failed
- Have untrackable conflicts (e.g., submodule conflicts)

**Useful for**: Identifying which conflicts still need manual resolution.

### 6.4 `git rerere forget <pathspec>`

**Purpose**: Forget (delete) the recorded resolution for a specific path.

```bash
git rerere forget config.py
# OR
git rerere forget '*.py'
```

**Effect**:
- Removes the cached resolution from `.git/rr-cache/`
- Useful if you recorded an incorrect resolution
- Can be re-recorded by resolving the conflict again

**Note**: Uses gitignore-style pathspec, not full file paths.

### 6.5 `git rerere clear`

**Purpose**: Reset all metadata used by rerere for the current merge/rebase session.

```bash
git rerere clear
```

**Effect**:
- Clears temporary conflict state (thisimage files)
- Used when aborting a merge/rebase to clean up
- Safe to use; doesn't delete cached resolutions

**Use case**: After `git merge --abort` or `git rebase --abort` to clean up rerere's temporary state.

### 6.6 `git rerere gc`

**Purpose**: Garbage collect old recorded resolutions.

```bash
git rerere gc
```

**Pruning Policy** (default):
- **Unresolved conflicts**: Deleted if older than 15 days
- **Resolved conflicts**: Deleted if older than 60 days

**Reasoning**: Very old cached resolutions are unlikely to be relevant (code has evolved too much).

**Customization**: Modify with config options (see Git documentation for `gc.rerefDays` and `gc.refsExpireDays`).

## 7. Limitations and When Rerere Fails

### 7.1 Conflict Marker Detection Failures

**Problem**: If a file naturally contains lines that resemble Git conflict markers, rerere may:
- Fail to detect the actual conflict
- Fail to record the resolution
- Produce incorrect results

**Example**:
```python
# This looks like a conflict marker but isn't
if <<<<<<< feature:
    handle_feature()
```

**Mitigation**: Rare in practice; avoid conflict-marker-like syntax in your code.

### 7.2 Context-Dependent Failures

**Problem**: If the surrounding code changes significantly, the cached resolution might not apply cleanly.

**Scenario**:
```
Session 1: Resolve conflict in lines 50-60
Cached resolution works for that context

Session 2: Different feature changes lines 30-40, causing different context
Conflict happens again in lines 75-85
Three-way merge fails; rerere refuses to apply the cached resolution
```

**Result**: You'll see the conflict again and must resolve manually.

### 7.3 Submodule Conflicts

**Problem**: Rerere cannot handle submodule conflicts.

**Output**:
```
git rerere remaining
# Lists submodule paths
```

**Reason**: Submodule conflicts aren't text-based conflicts; they involve commit references.

**Solution**: Handle submodule conflicts manually.

### 7.4 File Rename Conflicts

**Problem**: Structural conflicts (file renames) aren't tracked by rerere.

**Scenario**:
- Branch A: Renames `utils.py` to `utilities.py`
- Branch B: Edits `utils.py`
- Merge: Structural conflict (rename vs. modify)

**Result**: Rerere cannot help; requires manual resolution.

**Reason**: Rename detection is a different conflict type from content conflicts.

### 7.5 Binary File Conflicts

**Problem**: Rerere only handles text files.

**Binary files**:
- Cannot be three-way merged
- Cannot have conflict markers
- Cannot be auto-resolved by rerere

**Solution**: Use `.gitattributes` to specify `ours` or `theirs` merge strategies for binary files.

### 7.6 Incomplete or Wrong Resolutions

**Problem**: If you record a resolution incorrectly, it will be reused incorrectly.

**Example**:
```
First merge: You resolve incorrectly (but git commit succeeds)
Cached resolution: Wrong resolution is stored
Second merge: Same wrong resolution auto-applied
Result: Bug propagates silently
```

**Detection**:
```bash
git rerere diff  # Review cached resolution
git rerere forget <file>  # Delete wrong resolution
# Resolve correctly and commit again
```

**Mitigation**: Use tests to catch incorrect resolutions; code review cached resolutions when first recorded.

### 7.7 Heuristics Are Not 100% Guaranteed

**From Pro Git documentation**: "Because rerere heuristics are not 100% guaranteed to be relevant (the context might have changed…), Git will refuse to auto-finalize a rerere-helped operation."

**Behavior**:
```bash
git rebase main
# CONFLICT resolved by rerere
# Rebase stops; requires 'git rebase --continue' to finalize
```

Even with successful auto-resolution, Git requires manual finalization to ensure you reviewed the auto-applied changes.

## 8. Using Rerere in Team Workflows

### 8.1 Sharing Rr-Cache with Team Members

**Challenge**: `.git/rr-cache/` is local by default; conflicts resolved by one developer aren't automatically available to others.

**Approaches**:

#### Approach 1: Central Rr-Cache Repository

Create a shared repository specifically for conflict resolutions:

```bash
# On a shared server or Git hosting service
# Create: shared-rerere-cache.git

# Each developer
git clone shared-rerere-cache.git ~/.git-rr-cache-shared
# Configure Git to use this shared cache
git config --global rerere.cacheLocation ~/.git-rr-cache-shared
```

**Workflow**:
1. Developer A resolves a conflict → recorded in shared cache
2. Developer A: `git push` to shared-rerere-cache
3. Developer B: `git pull` shared-rerere-cache to sync
4. Developer B: Same conflict → rerere finds it in shared cache

**Pros**: Centralized, explicit control
**Cons**: Requires manual sync steps; adds infrastructure

#### Approach 2: Git-BPF Integration

The git-bpf tool automates sharing:

```bash
gem install git-bpf
git bpf share-rerere-cache
# Automatically publishes conflict resolutions
```

**Workflow**:
- Integrated into branch-per-feature workflow
- Resolutions automatically shared when merged to integration branch
- Teammates pull latest resolutions

**Pros**: Automatic, minimal overhead
**Cons**: Requires git-bpf adoption

#### Approach 3: Symlinks to Shared Location

```bash
# NFS mount or shared filesystem
ln -s /shared/git-rr-cache ~/.git/rr-cache
```

**Pros**: Transparent sharing, no additional tooling
**Cons**: Requires shared filesystem (NFS, etc.); scalability issues

#### Approach 4: Gitignore + Commit (Anti-pattern)

**Not recommended**: Committing `.git/rr-cache/` to the repository.

Reasons:
- Creates large commits
- Causes merge conflicts in the rr-cache itself
- Hard to maintain across branches

### 8.2 Team Best Practices

1. **Enable globally in team guidelines**:
   ```bash
   git config --global rerere.enabled true
   git config --global rerere.autoupdate true
   ```

2. **Document shared cache location** in team onboarding docs.

3. **Establish a sync cadence** if using central repository.

4. **Code review merged resolutions** when first committed.

5. **Use `git rerere diff`** to verify cached resolutions before accepting them.

6. **Prune old resolutions regularly**:
   ```bash
   git rerere gc
   ```

## 9. Rerere and Rebase Workflows

### 9.1 Why Rebase + Rerere Is Powerful

Rebasing often causes the same conflicts to reappear:

**Scenario**:
- Feature branch created from main 10 commits ago
- Main has evolved; rebase needed
- First rebase: Resolve conflict in `config.py`
- Two weeks later: Need to rebase on newer main
- Second rebase: **Same conflict in `config.py` appears again**

**Without rerere**: Manually resolve the same conflict twice
**With rerere**: Second rebase auto-resolves

### 9.2 Rebase with Rerere Enabled

```bash
git rebase main
# CONFLICT (content): Merge conflict in config.py
# config.py: Recorded resolution
# config.py: Resolved using recorded resolution
#
# Successfully rebased and updated refs/heads/feature.
```

The rebase automatically applies the cached resolution and continues.

### 9.3 Important Caveat: Manual Review Still Required

Even with auto-resolution, Git may require finalization:

```bash
git rebase main
# config.py: Resolved using recorded resolution
# Applied 5 commits, resolved 1 conflict
#
# If there are conflicts in this rebase, you need to resolve them and use
# "git rebase --continue" to continue rebasing.
```

Always verify the auto-applied resolution with:
```bash
git log --oneline -3  # Review recent commits
git diff HEAD~1       # Review what was applied
git rebase --continue  # Finalize if correct
```

### 9.4 Long-Lived Branch Pattern

**Use case**: A branch that's kept up-to-date with main but not merged yet.

**Workflow**:
```bash
# Initial merge (resolve conflicts, record them)
git merge main

# Two weeks later: keep branch up-to-date
git merge main  # Again: same conflicts auto-resolved

# One month later
git merge main  # Again: same conflicts auto-resolved

# Finally, merge to main (history is clean, no new conflicts)
git merge main
```

**Benefit**: Rerere eliminates the repetitive conflict resolution, saving hours on long-lived branches.

## 10. Leveraging Rerere for AI-Powered Merge Intelligence

### 10.1 Design Considerations for AI Skills

An AI-powered merge resolution skill could integrate with rerere in several ways:

#### Pattern 1: Pre-Rerere Checking

```
if git rerere recognizes conflict:
    apply cached resolution
    AI verification: Confirm cached resolution is semantically correct
else:
    AI analysis: Attempt intelligent resolution
    if confident:
        apply AI resolution
        record in rerere cache
```

**Benefit**: Leverage human wisdom (from previous resolutions) before attempting AI inference.

#### Pattern 2: Conflict Classification

```
conflict_type = classify(conflict)

if conflict_type == "simple_merge":
    # Let rerere handle it
    git rerere
    return
elif conflict_type == "semantic_merge":
    # AI is needed
    AI.resolve(files, context, tests)
elif conflict_type == "structural":
    # Manual intervention needed
    alert_developer()
```

**Benefit**: Route different conflict types to appropriate resolution methods.

#### Pattern 3: Rerere Cache Enrichment

```
if git rerere auto-applies resolution:
    store additional metadata:
    - AI confidence in the cached resolution
    - Test results that validated the resolution
    - Context/commit messages around the conflict
    - Domain-specific resolution metadata

next_time:
    retrieve enriched metadata
    higher confidence in auto-application
```

**Benefit**: Build higher-confidence rerere by storing validation data.

### 10.2 Practical Integration Points

1. **Post-rerere validation**:
   - After rerere auto-applies, run tests
   - If tests fail, flag for manual review
   - Update rerere cache with test results

2. **Semantic analysis**:
   - Analyze intent behind both conflicting versions
   - Ensure cached resolution preserves both intents
   - Flag semantically suspicious cached resolutions

3. **Domain-aware caching**:
   - For API conflicts, semantic merging might be better than rerere
   - For configuration, rerere usually sufficient
   - Route based on file type/domain

4. **Cache management**:
   - Monitor rerere cache size (`git rerere gc` output)
   - Alert if too many old unresolved conflicts
   - Analyze which cached resolutions are most frequently used

## 11. Performance Implications

### 11.1 Disk Space Usage

**Per-conflict overhead**:
- Small conflicts: 100-500 bytes (preimage + postimage)
- Large conflicts: Up to a few KB
- Metadata overhead: Negligible

**Scale analysis**:
- 100 recorded conflicts: ~500 KB
- 1000 recorded conflicts: ~5 MB
- 10,000 recorded conflicts: ~50 MB

For most projects, this is trivial.

### 11.2 Lookup and Application Performance

**Three-way merge overhead**: Negligible
- SHA-1 hash computation: Microseconds
- Directory lookup: Milliseconds
- Three-way merge: Milliseconds per conflict

**Result**: Rerere adds <100ms per merge, imperceptible to users.

### 11.3 Repository-Wide Implications

**Global rerere (all repositories)**:
- If enabled globally on shared filesystems (NFS)
- If many projects have large rr-cache directories
- Aggregate bloat could emerge

**Management strategy**:
```bash
# Regular maintenance
git rerere gc  # Remove old resolutions
git rerere gc --aggressive  # More aggressive cleanup
```

**Selective enabling**:
- Enable per-project for high-merge-activity repos
- Disable globally if storage concerns arise
- Use team guidelines to manage proliferation

### 11.4 Recommendations

1. **Enable by default** in most workflows (cost is negligible)
2. **Run `git rerere gc` monthly** in shared repositories
3. **Monitor rr-cache size** if managing many projects
4. **Profile before optimization** (rerere is rarely a bottleneck)

## 12. Edge Cases and Advanced Scenarios

### 12.1 Multiple Conflicts in One File

**Scenario**: `utils.py` has conflicts at two locations.

**Behavior**:
```
Recorded preimage for 'utils.py'
(Both conflict hunks are in one preimage file)
```

**Storage**: Single hash, single pair of preimage/postimage files containing both conflicts.

**Reuse**: When rerere finds the hash match:
- Both conflicts are resolved together
- Cannot selectively apply only one conflict's resolution
- All-or-nothing application

### 12.2 Same Conflict in Different Files

**Scenario**: `config.py` and `settings.py` have the exact same conflict (content-wise).

**Behavior**:
```
Hash(config.py conflict) == Hash(settings.py conflict)
Both stored in same .git/rr-cache/<hash>/ directory
```

**Reuse**: When either file has a matching conflict:
- Same cached resolution applied to both
- Demonstrates that rerere is content-based, not path-based

### 12.3 Partial Three-Way Merge Failure

**Scenario**: Rerere finds cached resolution, but three-way merge fails.

**Output**:
```bash
git rebase main
# config.py: Recorded resolution
# config.py: Resolution recorded for config.py
# CONFLICT (content): Merge conflict in config.py
```

The cached resolution is noted, but not applied (three-way merge failed).

**Reason**: The surrounding context has evolved too much; cached resolution isn't compatible.

**Recovery**:
```bash
git rerere remaining  # config.py listed
# Manual resolution required
# Re-record new resolution
```

### 12.4 Rebase with Dropped Commits

**Scenario**: During rebase, a commit is dropped.

```bash
git rebase -i main
# User marks a commit as 'drop'
# Later commits with conflicts appear
```

**Behavior**: Rerere still works; dropped commits don't affect cached resolution matching.

### 12.5 Merge Strategies and Rerere

**Interaction with merge strategies**:

```bash
git merge -s recursive -X ours main
# With rerere enabled, both mechanisms work
# Recursive strategy + rerere's recorded resolutions
```

**Order of operations**:
1. Merge strategy is applied (e.g., `-X ours`)
2. Rerere is run if conflicts remain
3. Manual resolution if neither strategy nor rerere succeeds

### 12.6 Cherry-Pick with Rerere

**Scenario**: Cherry-picking a commit introduces a conflict.

```bash
git cherry-pick abc123
# CONFLICT
# conflict.py: Recorded resolution (if hash matches)
# conflict.py: Resolved using recorded resolution
```

Rerere works the same way with cherry-pick as with merge/rebase.

### 12.7 Conflict Markers in Version Control

**Gotcha**: If you accidentally commit a file with conflict markers:

```
<<<<<<< HEAD
version 1
=======
version 2
>>>>>>> branch
```

**Behavior**: Rerere may treat this as a "recorded conflict" on next merge, causing unexpected auto-resolutions.

**Prevention**: Commit hooks to reject conflict markers.

## 13. Detecting and Fixing Incorrect Resolutions

### 13.1 Detecting Wrong Cached Resolutions

**Strategy 1: Code review**
```bash
git rerere diff  # Review before accepting auto-resolution
git show --cached  # Review staged changes
```

**Strategy 2: Test-driven detection**
```bash
git rerere  # Auto-resolve
npm test  # Or your test command
if tests fail:
    git rerere forget <file>  # Discard wrong resolution
```

**Strategy 3: Commit message auditing**
```bash
git log --grep="Merge"  # Find merge commits
git show <hash>  # Review resolution quality
```

### 13.2 Fixing Incorrect Resolutions

**Process**:
```bash
# 1. Identify the wrong resolution
git rerere remaining  # Lists unresolved conflicts
git rerere diff  # Compare to current state

# 2. Discard the cached resolution
git rerere forget <file>

# 3. Resolve manually
# Edit file, resolve correctly

# 4. Re-record
git add <file>
git commit  # Rerere records new (correct) resolution

# 5. Verify
git log --oneline -1  # Confirm commit
```

### 13.3 Bulk Cleanup

If multiple resolutions are wrong:

```bash
# Option 1: Selective deletion
git rerere forget 'src/*.py'

# Option 2: Full reset
rm -rf .git/rr-cache  # Delete all cached resolutions

# Option 3: Aggressive garbage collection
git rerere gc --aggressive
```

## 14. Configuration Reference

### 14.1 Core Settings

```bash
# Enable rerere
git config --global rerere.enabled true

# Auto-stage resolved files
git config --global rerere.autoupdate true

# Custom cache location
git config --global rerere.cacheLocation /path/to/cache
```

### 14.2 Garbage Collection Settings

```bash
# Prune unresolved conflicts older than N days
git config --global gc.rerefDays 15

# Prune resolved conflicts older than N days
git config --global gc.refsExpireDays 60
```

### 14.3 Per-Repository Override

```bash
cd /path/to/repo
git config rerere.enabled false  # Disable for this repo
git config rerere.autoupdate false  # Manual staging required
```

## 15. Practical Workflows

### 15.1 Feature Branch Integration Workflow

```bash
# Initial setup
git config --global rerere.enabled true

# Create feature branch
git checkout -b feature/new-feature

# Work on feature, push, create PR

# Periodically sync with main (record conflicts)
git fetch origin
git merge origin/main  # Resolve conflicts once, record them

# Later merges/rebases auto-resolve
git merge origin/main  # Conflicts auto-resolved

# Final merge
git merge origin/main  # Likely no conflicts due to rerere
```

### 15.2 Rebase-Focused Workflow

```bash
# Setup
git config --global rerere.enabled true
git config --global rerere.autoupdate true  # Smooth rebase experience

# Feature branch
git checkout -b feature/update

# Rebase on main (conflicts recorded)
git rebase main

# Two weeks later: rebase again
git rebase main  # Same conflicts auto-resolved

# Clean history, ready to merge
git push origin feature/update
```

### 15.3 Multi-Target Merge Workflow

```bash
# Merging to multiple release branches
git merge origin/release-1.0  # Resolve, record
git merge origin/release-2.0  # Same conflicts auto-resolved
git merge origin/release-3.0  # Same conflicts auto-resolved
```

## 16. Troubleshooting

### 16.1 Rerere Not Working

**Symptom**: Conflicts not being auto-resolved.

**Checks**:
```bash
# Is rerere enabled?
git config rerere.enabled  # Should output 'true'

# Does rr-cache directory exist?
ls -la .git/rr-cache/

# Are there any cached resolutions?
ls .git/rr-cache/  # Should show hash directories if cached
```

**Solutions**:
```bash
# Enable rerere
git config --global rerere.enabled true

# Create rr-cache if needed
mkdir -p .git/rr-cache

# Test with a new conflict
git merge test-branch  # Should show "Recorded preimage"
```

### 16.2 Conflicts Not Being Recorded

**Symptom**: Rerere not recording resolutions even though enabled.

**Cause**: Conflict markers not recognized (file encoding, line endings).

**Solution**:
```bash
# Check file encoding
file config.py

# Normalize line endings
git config core.autocrlf true  # On Windows
git config core.safecrlf true  # Warn about CRLF issues

# Re-resolve and commit
git add config.py
git commit
```

### 16.3 Too Many Stale Cached Resolutions

**Symptom**: `.git/rr-cache/` growing too large.

**Solution**:
```bash
git rerere gc  # Standard cleanup
git rerere gc --aggressive  # More aggressive cleanup
```

## 17. Comparing Rerere with Alternatives

### 17.1 vs. Merge Commit Strategies

**Merge strategies** (e.g., `-X ours`, `-X theirs`):
- Apply pre-defined rules
- Don't learn from previous resolutions
- Faster for simple cases

**Rerere**:
- Learns from human resolutions
- Smarter for repeated scenarios
- Complements merge strategies

### 17.2 vs. Manual Conflict Resolution

**Manual resolution**:
- Full control
- Time-consuming for repeated conflicts
- Prone to inconsistencies

**Rerere**:
- Consistent
- Automatic on subsequent conflicts
- Still allows manual override

### 17.3 vs. AI-Powered Merge Tools

**AI tools** (e.g., specialized merge intelligence):
- Understand intent semantically
- Can generate new solutions
- Compute-intensive

**Rerere**:
- Fast (cached)
- Proven solutions (from humans)
- Lightweight

**Ideal**: Combine both. Use rerere first (fast), then AI for unresolved conflicts.

## 18. Research Conclusion

Git rerere is a mature, lightweight feature that excels at eliminating repetitive conflict resolution. Its internal design (content-based hashing, three-way verification) makes it reliable despite its simplicity. The main limitations are well-understood: submodule conflicts, structural changes (renames), and binary files require manual handling.

For teams using frequent merges or rebases, enabling rerere globally is a low-cost, high-benefit decision. Integration with AI-powered merge tools can further enhance conflict resolution quality by leveraging both cached resolutions and semantic analysis.

The most significant opportunities for enhancement are:
1. **Sharing rr-cache across teams** (improving with git-bpf-like tooling)
2. **Validation layers** (testing cached resolutions before application)
3. **Semantic enrichment** (storing intent metadata alongside cached resolutions)
4. **AI integration** (using AI for conflicts rerere can't handle)

## Sources

Research compiled from the following authoritative sources:

- [Git - Rerere | Pro Git Book](https://git-scm.com/book/en/v2/Git-Tools-Rerere)
- [Git - git-rerere Documentation](https://git-scm.com/docs/git-rerere)
- [Git Rerere (Reuse Recorded Resolution) | Graph AI Engineering Glossary](https://www.graphapp.ai/engineering-glossary/git/git-rerere-reuse-recorded-resolution)
- [Ubuntu Manual Page: git-rerere](https://manpages.ubuntu.com/manpages/xenial/en/man1/git-rerere.1.html)
- [Mastering Git Rerere: Solving Repetitive Merge Conflicts with Ease | This Dot Labs](https://www.thisdot.co/blog/mastering-git-rerere-solving-repetitive-merge-conflicts-with-ease)
- [Resolving conflicts with git-rerere | Atlassian Blog](https://www.atlassian.com/blog/bitbucket/resolving-conflicts-with-git-rerere)
- [Fix conflicts only once with git rerere | Christophe Porteneuve | Medium](https://medium.com/@porteneuve/fix-conflicts-only-once-with-git-rerere-7d116b2cec67)
- [Using git's rerere feature to escape recurring conflict hell | GitHub Gist](https://gist.github.com/skipcloud/f1033afb4fa5681d69fa63458cc95928)
- [Git Rerere: Reuse Recorded Resolution | Sasha Vinčić Blog](https://sasha.vincic.org/blog/2024/07/git-rerere-streamline-conflict-resolution)
- [Git git-rerere(1) Manual Page | Linux Manual Pages](https://man7.org/linux/man-pages/man1/git-rerere.1.html)
- [Git Deep Dive: Mastering rerere | DEV Community](https://dev.to/louis7/git-deep-dive-mastering-rerere-12jm)
- [Git rerere - Reuse Conflict Resolutions Like a Pro | DEV Community](https://dev.to/louis7/git-rerere-reuse-conflict-resolutions-like-a-pro-1g88)
- [Reuse Recorded Resolution | Git Refresher](https://arcelopera.github.io/git_refresher/More/git_rerere/)
- [Git Rerere: Reuse Recorded Resolution | Compile N Run](https://www.compilenrun.com/docs/devops/git/git-advanced-features/git-rerere/)
- [Git rerere ♲. Reuse the knowledge wisely | Milan Brankovic | Medium](https://medium.com/@milan.brankovic/git-rerere-5756deed4824)
- [How to Use Git Rerere to Resolve Merge Conflicts Effortlessly | LabEx](https://labex.io/tutorials/git-how-to-use-git-rerere-to-resolve-merge-conflicts-effortlessly-411648/)
- [Git/rerere.c | GitHub - git/git Repository](https://github.com/git/git/blob/master/rerere.c)
- [Resolve Git Merge Conflicts with Claude Code | Vibe Sparking AI](https://www.vibesparking.com/en/blog/ai/claude-code/practices/2025-09-17-git-merge-conflict-resolution/)
- [Hacking git-rerere | Edward Z. Yang's Blog](http://blog.ezyang.com/2010/01/hacking-git-rerere/)

---

**Document Version**: 1.0
**Date**: April 2026
**Research Focus**: Technical deep dive for AI merge intelligence integration
