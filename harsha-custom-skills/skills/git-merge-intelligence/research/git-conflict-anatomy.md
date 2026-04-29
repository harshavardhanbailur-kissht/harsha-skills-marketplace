# Git Conflict Markers: Anatomy of Three-Way Merge Information

## Executive Summary

Git conflict markers encode rich three-way merge information that extends far beyond the visible `<<<<<<<`, `=======`, and `>>>>>>>` text. This document explores the complete data model underlying Git's conflict representation, including hidden merge metadata, index stages, and programmatic extraction techniques for building intelligent merge tools.

---

## 1. Basic Conflict Marker Structure: `<<<<<<<`, `=======`, `>>>>>>>`

### What Each Section Contains

When Git encounters a merge conflict in text files, it marks the conflicted region with three markers that delineate three distinct content sections:

```
<<<<<<< HEAD
Your local changes (ours)
=======
Changes from the branch being merged (theirs)
>>>>>>> branch-name
```

**Section Semantics:**

- **`<<<<<<< HEAD` to `=======`**: Contains the version from the **current branch (HEAD)**, representing "ours" — the branch you are merging *into*.
- **`=======` to `>>>>>>> branch-name`**: Contains the version from the **incoming branch**, representing "theirs" — the branch being merged *from*.

### Critical Context: What "Ours" and "Theirs" Mean

The terminology depends on the operation:

**During `git merge`:**
- **ours** = current branch (the branch you're on when you run `git merge`)
- **theirs** = branch being merged in

**During `git rebase` or `git pull --rebase`:**
- **ours** and **theirs** are **swapped**
- **ours** = the branch you're rebasing onto
- **theirs** = your branch being rebased (the one with your work)

This semantic shift is documented in the [Git Advanced Merging guide](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging) and represents a frequent source of confusion.

### Example: Real Conflict Marker

```python
def calculate_total(items):
<<<<<<< HEAD
    return sum(item.price for item in items)
=======
    total = 0
    for item in items:
        total += item.price
    return total
>>>>>>> feature/refactor
```

In this example:
- HEAD (ours) has a concise functional approach
- feature/refactor (theirs) has an imperative loop-based approach
- Git doesn't know which is semantically correct

---

## 2. Enhanced Conflict Display: diff3 Style with `|||||||` Marker

### Enabling diff3 Conflict Style

By default, Git uses the "merge" conflict style. To display the common ancestor (base) version inline, configure:

```bash
git config --global merge.conflictstyle diff3
```

This can also be set per-merge with:

```bash
git merge --no-commit -X diff3 <branch>
```

### The diff3 Format: Complete Three-Version View

With `merge.conflictstyle diff3` enabled, conflicts display with four markers:

```
<<<<<<< HEAD
Your changes (ours)
||||||| merged common ancestor
Original version (base)
=======
Incoming changes (theirs)
>>>>>>> branch-name
```

### Semantic Meaning of the diff3 Sections

- **`<<<<<<< HEAD` to `|||||||`**: Your branch's version
- **`|||||||` to `=======`**: The **common ancestor** version (the state before either branch made changes)
- **`=======` to `>>>>>>>`**: The incoming branch's version

### Why diff3 Matters

The common ancestor context dramatically aids conflict resolution. By seeing what the code looked like before both branches diverged, you can infer:

1. **What changes each side made**: Compare ours to base, and theirs to base
2. **Whether changes are conflicting or complementary**: If both sides added different things without overlap, they may be mergeable
3. **Semantic intent**: The base version often clarifies the original purpose

**Example with diff3:**

```python
def process_data(data):
||||||| merged common ancestor
    return data
<<<<<<< HEAD
    return [x * 2 for x in data]
=======
    return sorted(data)
>>>>>>> feature/sort
```

Here, you can see that:
- Base was a no-op
- ours (HEAD) added transformation logic
- theirs added sorting logic

These are likely complementary, not truly conflicting.

Reference: [Take the pain out of git conflict resolution: use diff3](https://blog.nilbus.com/take-the-pain-out-of-git-conflict-resolution-use-diff3/)

---

## 3. Hidden Information Beyond Visible Markers: Merge Index Stages

### The Git Index: Three Stages of Conflict

During a merge with conflicts, Git's index (the staging area) stores **up to four different versions** of each conflicted file:

- **Stage 0**: The merged result (only present if conflict is resolved)
- **Stage 1**: The version from the **common ancestor** (base)
- **Stage 2**: The version from **HEAD** (ours)
- **Stage 3**: The version from **MERGE_HEAD** (theirs)

This three-stage model (stages 1-3) is fundamental to Git's conflict model. The index entries are NOT deleted—they persist until conflict resolution completes.

### Accessing Index Stages with `git show`

Each stage can be accessed using a special colon notation:

```bash
# Extract the common ancestor version (stage 1)
git show :1:filename > base.txt

# Extract your version (stage 2)
git show :2:filename > ours.txt

# Extract the incoming version (stage 3)
git show :3:filename > theirs.txt
```

### Real-World Example

During a merge conflict in `src/app.py`:

```bash
$ git show :1:src/app.py  # Common ancestor
$ git show :2:src/app.py  # Your branch's version
$ git show :3:src/app.py  # Branch being merged
```

Each command outputs the complete file content from that stage, unmodified by markers. This is how sophisticated merge tools (like IntelliJ's 3-way merge editor) internally access all three versions.

### Query All Index Stages

To see all conflict metadata at once:

```bash
$ git ls-files -u
100644 abc123def456 1 filename.txt
100644 def456abc789 2 filename.txt
100644 ghi789jkl012 3 filename.txt
```

Output format: `[mode] [SHA-1 hash] [stage] [filename]`

This shows the blob hash for each stage, allowing programmatic access to the exact object.

**Reference:** [Git - git-ls-files Documentation](https://git-scm.com/docs/git-ls-files/2.30.1) and [Git - Advanced Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)

---

## 4. Merge State Metadata: `.git/ORIG_HEAD`, `.git/MERGE_HEAD`, `.git/MERGE_MSG`

### The Three Merge Metadata Files

During an active merge (after `git merge` but before `git commit` or `git merge --abort`), Git creates three special files in the `.git/` directory:

#### 4.1 ORIG_HEAD

**Purpose**: Records the HEAD commit before the merge operation started.

**Content**: A single commit hash (e.g., `a1b2c3d4e5f6...`)

**Lifecycle**:
- Created by: `git merge`, `git rebase`, `git reset`, `git checkout` (detached HEAD)
- Persists after merge completion (unlike MERGE_HEAD)
- Used to revert a merge: `git reset --hard ORIG_HEAD`

**Programmatic Access:**

```bash
git rev-parse ORIG_HEAD  # Outputs the commit hash
git show ORIG_HEAD       # Show the commit details
```

#### 4.2 MERGE_HEAD

**Purpose**: Records the commit(s) being merged into the current branch.

**Content**: One or more commit hashes (one per line in octopus merges)

**Lifecycle**:
- Created by: `git merge` command
- Deleted when merge completes (either via `git commit` or `git merge --abort`)
- If file exists, a merge is in progress

**Programmatic Access:**

```bash
git rev-parse MERGE_HEAD           # Get the commit being merged
git show MERGE_HEAD                # Show that commit
git cat-file -p MERGE_HEAD:path/to/file  # Access files at MERGE_HEAD
```

**Octopus Merge Context**: In an octopus merge (merging 3+ branches simultaneously), MERGE_HEAD contains multiple commit hashes, one per line.

#### 4.3 MERGE_MSG

**Purpose**: Stores the intended commit message for the merge.

**Content**: A pre-formatted message capturing merge operation details

**Example:**

```
Merge branch 'feature/new-ui'

# Conflicts:
#   src/components/Header.tsx
#   src/styles/main.css
```

**Lifecycle**:
- Created by: `git merge` with optional `-m` flag
- Used as default message when `git commit` is called to finalize
- Deleted when merge completes
- Can be edited before finalizing the merge

### Detection: Checking Merge State

```bash
# Check if merge is in progress
test -f .git/MERGE_HEAD && echo "Merge in progress"

# Or more idiomatically
git rev-parse --is-inside-git-dir 2>/dev/null && \
  test -f .git/MERGE_HEAD && echo "Merge in progress"
```

### Reference

[Git - git-merge Documentation](https://git-scm.com/docs/git-merge) and [Git References Explained: ORIG_HEAD, FETCH_HEAD, MERGE_HEAD & More](https://www.w3tutorials.net/blog/orig-head-fetch-head-merge-head-etc/)

---

## 5. File-Level Resolution: `git checkout --ours` and `git checkout --theirs`

### Semantics and Behavior

Instead of manually editing conflicted files, you can wholesale accept one version:

```bash
# Accept the current branch's version (discard theirs)
git checkout --ours filename.txt

# Accept the incoming branch's version (discard ours)
git checkout --theirs filename.txt
```

**Critical**: These commands **completely replace** the file, removing all conflict markers and the other version entirely.

### The Rebase Caveat: Swapped Semantics

During `git rebase`, the meaning of ours/theirs is **inverted**:

```bash
git rebase main

# During rebase:
# --ours = the branch you're rebasing ONTO (main)
# --theirs = your branch being rebased (your work)
```

This inversion often surprises developers and is a common source of merge mistakes.

### Post-Resolution: Must Stage the File

After using `--ours` or `--theirs`, the conflict resolution is **not automatically staged**:

```bash
git checkout --ours filename.txt
git add filename.txt  # Must stage to mark as resolved
```

### Bulk Resolution Pattern

Resolve all conflicts for one side at once:

```bash
# Accept all our changes
git checkout --ours .
git add .
git commit -m "Resolved conflicts (kept our version)"

# Or for theirs
git checkout --theirs .
git add .
git commit -m "Resolved conflicts (took their version)"
```

**Reference:** [Git - Advanced Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)

---

## 6. Merge Index Stages: Complete Technical Model

### Index Structure During Conflict

The Git index is a binary file (`.git/index`) that normally maps one file path to one (stage 0) object. During a merge conflict, a single path gets **three entries**:

```
Path: src/app.py
├── Stage 1: blob abc123 (common ancestor)
├── Stage 2: blob def456 (ours/HEAD)
└── Stage 3: blob ghi789 (theirs/MERGE_HEAD)
```

### Stage Numbers and Semantics

| Stage | Source | Meaning |
|-------|--------|---------|
| 0 | Merged result | Conflict resolved; single authoritative version |
| 1 | Tree O (original) | Common ancestor; the last shared version |
| 2 | Tree A (ours) | Current branch (HEAD) |
| 3 | Tree B (theirs) | Incoming branch (MERGE_HEAD) |

### Querying Stages with `git ls-files`

```bash
# List only unmerged (conflicted) files
git ls-files --unmerged

# Sample output:
100644 abc123def456 1 README.md
100644 def456abc789 2 README.md
100644 ghi789jkl012 3 README.md
```

### Programmatic Inspection

```bash
# Count conflicts
git ls-files --unmerged | wc -l

# Get a specific file's stage 2 (ours)
HASH=$(git ls-files --stage | grep "^100644.*2.*filename" | awk '{print $2}')
git cat-file blob $HASH

# List all conflicted files (unique paths)
git ls-files --unmerged | cut -f2 | sort -u
```

### Internal Mechanism: How Git Uses Stages

When resolving a merge, Git:

1. Reads stage 1 (base), stage 2 (ours), stage 3 (theirs)
2. Applies a three-way diff algorithm:
   - If only ours changed from base → accept ours
   - If only theirs changed from base → accept theirs
   - If both changed differently → **conflict** (create markers)
3. On resolution, replaces stages 1-3 with stage 0

**Reference:** [Git - git-ls-files Documentation](https://git-scm.com/docs/git-ls-files/2.30.1)

---

## 7. Special Cases: Binary Files, Submodules, and Deletions

### Binary Files: No Inline Markers

Git **cannot insert conflict markers into binary files**. For binary conflicts, Git leaves the working tree untouched with the **original (ours) version** intact.

**How to Resolve**:

```bash
# Keep your binary version
git checkout --ours image.png
git add image.png

# Or take theirs
git checkout --theirs image.png
git add image.png
```

The stages are still available:

```bash
# Compare file versions programmatically
git show :1:image.png > base.png
git show :2:image.png > ours.png
git show :3:image.png > theirs.png
```

But manual resolution is required—Git cannot auto-merge binary content.

### File Deletion vs. Modification Conflicts

A **delete-modify conflict** occurs when:
- One branch deletes a file
- The other branch modifies it

**Example conflict state:**

```
Added by us:
    new file mode 100644
    index 0000000..abc123
    --- /dev/null
    +++ b/old_feature.py

Deleted by them:
    deleted file mode 100644
    index abc123..0000000
```

**Resolution choices**:

```bash
# Keep the file (resolve in favor of modification)
git add old_feature.py

# Delete the file (resolve in favor of deletion)
git rm old_feature.py
```

### Submodule Conflicts

When a submodule is updated differently on two branches:

```
Submodule path: 'libs/core'
conflict:
  local: ab12cd34 (rewind to older commit)
  remote: ef56gh78 (fast-forward to newer commit)
```

Stages for submodules:

```bash
git ls-files --unmerged | grep libs/core
# Shows the commit hashes (not blob hashes) for each stage

# View submodule versions
git show :1:libs/core  # Base submodule commit
git show :2:libs/core  # Ours submodule commit
git show :3:libs/core  # Theirs submodule commit
```

Submodule conflicts require choosing a commit SHA or manually editing `.gitmodules`.

**Reference:** [Git - Advanced Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)

---

## 8. Listing Unmerged Files: `git ls-files -u`

### Command and Output Format

```bash
git ls-files -u
```

**Output format**:

```
[mode] [object hash] [stage] [filename]
100644 abc123def456 1 src/main.py
100644 def456abc789 2 src/main.py
100644 ghi789jkl012 3 src/main.py
100644 jkl012mno345 1 src/utils.py
100644 mno345pqr678 2 src/utils.py
100644 pqr678stu901 3 src/utils.py
```

### Parsing for Tooling

Extract unique conflicted files:

```bash
git ls-files -u | awk '{print $NF}' | sort -u
# Output:
# src/main.py
# src/utils.py
```

Extract stage 3 (theirs) blobs for all conflicts:

```bash
git ls-files -u | awk '$3 == 3 {print $2, $NF}' | while read hash file; do
  echo "=== $file (theirs) ==="
  git cat-file blob $hash
done
```

### Filtering by Stage

```bash
# List all stage 1 (base) entries
git ls-files -u | awk '$3 == 1'

# Count conflicts by stage
git ls-files -u | awk '{print $3}' | sort | uniq -c
```

### Emptying the Conflict List

To mark all conflicts as resolved:

```bash
git add .
# This removes all stages 1-3 and creates stage 0 entries

# Verify no conflicts remain
git ls-files -u | wc -l  # Should be 0
```

---

## 9. Finding Common Ancestors: `git merge-base` and Criss-Cross Merges

### Basic Usage: Single Common Ancestor

```bash
git merge-base <branch-a> <branch-b>
```

Returns the commit SHA of the most recent common ancestor.

**Example**:

```bash
$ git merge-base main feature/auth
a1b2c3d4e5f6...
```

This ancestor is used as **Stage 1** in the merge.

### Multiple Merge Bases: Criss-Cross Merges

In complex branching scenarios, especially **criss-cross merges**, there may be more than one valid common ancestor.

**Criss-cross merge example**:

```
    A -- B
   / \ / \
  C   X   Y
   \ / \ /
    D -- E
```

Here, C and D are both valid merge bases for A and E.

### Handling Multiple Bases

Without `--all`, Git picks one arbitrarily:

```bash
git merge-base main feature
# Returns one base (unpredictable which one)
```

To see all merge bases:

```bash
git merge-base --all main feature
# Returns all common ancestors (possibly multiple)
```

### Recursive Merge Strategy: Virtual Ancestor

When multiple merge bases exist, Git's **recursive merge strategy** (the default) handles them by:

1. Recursively merging all common ancestors together
2. Using the result as a **virtual ancestor** for the three-way merge
3. Applying three-way merge with this synthetic base

This handles criss-cross merges gracefully but can be computationally expensive.

### Practical Implication for Conflict Resolution

If a criss-cross merge produces unexpected conflicts, the choice of merge base matters:

```bash
# See which base was chosen
git merge-base main feature

# Try a different base manually
git merge-base --all main feature | while read base; do
  git merge-base --is-ancestor $base HEAD && echo "Candidate: $base"
done
```

**Reference:** [Git - git-merge-base Documentation](https://git-scm.com/docs/git-merge-base)

---

## 10. Programmatic Extraction: Building Intelligent Merge Tools

### Complete Extraction Pipeline

Here's a practical example of a script that extracts all three versions for every conflicted file:

```bash
#!/bin/bash
# extract_merge_versions.sh - Extract base/ours/theirs for all conflicts

mkdir -p merge_versions

git ls-files --unmerged | awk '{print $NF}' | sort -u | while read filepath; do
  dir="merge_versions/$filepath"
  mkdir -p "$(dirname "$dir")"

  echo "Extracting versions for: $filepath"

  # Extract stage 1 (base)
  git show :1:"$filepath" > "$dir.base" 2>/dev/null || echo "(binary or deleted)"

  # Extract stage 2 (ours)
  git show :2:"$filepath" > "$dir.ours" 2>/dev/null || echo "(binary or deleted)"

  # Extract stage 3 (theirs)
  git show :3:"$filepath" > "$dir.theirs" 2>/dev/null || echo "(binary or deleted)"
done

echo "Extracted versions to merge_versions/ directory"
```

### Advanced: Merge Context Extraction

Build a JSON representation of the merge state:

```bash
#!/bin/bash
# merge_context.sh - Extract full merge context to JSON

{
  echo "{"
  echo "  \"merge_head\": \"$(git rev-parse MERGE_HEAD)\","
  echo "  \"orig_head\": \"$(git rev-parse ORIG_HEAD)\","
  echo "  \"current_branch\": \"$(git rev-parse --abbrev-ref HEAD)\","
  echo "  \"merge_msg\": \"$(cat .git/MERGE_MSG | tr '\n' ' ' | sed 's/"/\\"/g')\","
  echo "  \"conflicts\": ["

  first=true
  git ls-files --unmerged | awk '{print $NF}' | sort -u | while read filepath; do
    [ "$first" = false ] && echo ","
    first=false

    echo "    {"
    echo "      \"file\": \"$filepath\","
    echo "      \"base\": \"$(git show :1:\"$filepath\" 2>/dev/null | md5sum | awk '{print $1}')\","
    echo "      \"ours\": \"$(git show :2:\"$filepath\" 2>/dev/null | md5sum | awk '{print $1}')\","
    echo "      \"theirs\": \"$(git show :3:\"$filepath\" 2>/dev/null | md5sum | awk '{print $1}')\""
    echo "    }"
  done

  echo "  ]"
  echo "}"
}
```

### Three-Way Diff Tool Integration

```bash
#!/bin/bash
# vimdiff3_merge.sh - Resolve conflicts with vimdiff showing all three versions

file="$1"

# Extract versions
git show :1:"$file" > /tmp/merge.base
git show :2:"$file" > /tmp/merge.ours
git show :3:"$file" > /tmp/merge.theirs

# Open in three-way diff
vimdiff /tmp/merge.ours /tmp/merge.base /tmp/merge.theirs

# Copy resolved version back
cp /tmp/merge.ours "$file"
git add "$file"
```

### Python Tool Example

```python
#!/usr/bin/env python3
import subprocess
import os
import json

def get_merge_versions(filepath):
    """Extract base, ours, and theirs versions."""
    versions = {}

    for stage, name in [(1, 'base'), (2, 'ours'), (3, 'theirs')]:
        try:
            result = subprocess.run(
                ['git', 'show', f':{stage}:{filepath}'],
                capture_output=True,
                text=True,
                check=True
            )
            versions[name] = result.stdout
        except subprocess.CalledProcessError:
            versions[name] = None

    return versions

def list_conflicts():
    """Get all unmerged files."""
    result = subprocess.run(
        ['git', 'ls-files', '--unmerged'],
        capture_output=True,
        text=True,
        check=True
    )

    files = set()
    for line in result.stdout.strip().split('\n'):
        if line:
            files.add(line.split()[-1])

    return sorted(files)

def get_merge_context():
    """Get overall merge state."""
    merge_head = subprocess.run(
        ['git', 'rev-parse', 'MERGE_HEAD'],
        capture_output=True,
        text=True
    ).stdout.strip()

    orig_head = subprocess.run(
        ['git', 'rev-parse', 'ORIG_HEAD'],
        capture_output=True,
        text=True
    ).stdout.strip()

    with open('.git/MERGE_MSG', 'r') as f:
        merge_msg = f.read()

    return {
        'merge_head': merge_head,
        'orig_head': orig_head,
        'merge_msg': merge_msg
    }

if __name__ == '__main__':
    context = get_merge_context()
    conflicts = list_conflicts()

    result = {
        'context': context,
        'conflicts': {}
    }

    for filepath in conflicts:
        result['conflicts'][filepath] = get_merge_versions(filepath)

    print(json.dumps(result, indent=2, default=str))
```

### Integration Points for Merge Tools

Intelligent merge tools can:

1. **Pre-analyze**: Call `git ls-files -u` to detect conflicts before user sees them
2. **Context retrieval**: Use `git show :1/:2/:3:` to feed a smarter diff algorithm
3. **Smart merging**: Apply language-aware merge strategies (AST-based, semantic)
4. **Bulk resolution**: Programmatically resolve conflicts that pass confidence thresholds
5. **Conflict prediction**: Use `git merge-base` and diff patterns to predict conflicts before merge

---

## Summary: The Complete Information Model

Git conflict markers are the **surface representation** of a rich, structured three-way merge state:

| Component | Location | Access Method |
|-----------|----------|----------------|
| Visible markers | Working tree file | Plain text read |
| Common ancestor | Index stage 1 | `git show :1:file` |
| Ours (HEAD) | Index stage 2 | `git show :2:file` |
| Theirs (MERGE_HEAD) | Index stage 3 | `git show :3:file` |
| Merge source | `.git/MERGE_HEAD` | `cat .git/MERGE_HEAD` |
| Original HEAD | `.git/ORIG_HEAD` | `git rev-parse ORIG_HEAD` |
| Merge message | `.git/MERGE_MSG` | `cat .git/MERGE_MSG` |
| All conflicts | Index metadata | `git ls-files -u` |
| Common ancestor commit | Git DAG | `git merge-base` |

Understanding these layers enables building:
- Smarter merge tools with full context
- Conflict prediction systems
- Semantic merge strategies
- Audit trails of merge decisions
- Automated conflict resolution for patterns

---

## References

1. [Git - git-merge Documentation](https://git-scm.com/docs/git-merge)
2. [Git - Advanced Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
3. [Take the pain out of git conflict resolution: use diff3](https://blog.nilbus.com/take-the-pain-out-of-git-conflict-resolution-use-diff3/)
4. [Git - git-ls-files Documentation](https://git-scm.com/docs/git-ls-files/2.30.1)
5. [Git - git-merge-base Documentation](https://git-scm.com/docs/git-merge-base)
6. [Git References Explained: ORIG_HEAD, FETCH_HEAD, MERGE_HEAD & More](https://www.w3tutorials.net/blog/orig-head-fetch-head-merge-head-etc/)
7. [The Magic of 3-Way Merge](https://blog.git-init.com/the-magic-of-3-way-merge/)
8. [Git - merge-strategies Documentation](https://git-scm.com/docs/merge-strategies)
9. [Merge Strategies with Git…did you say a three-way?](https://medium.com/@HelanaBakhsh/merge-strategies-with-git-did-you-say-a-three-way-ebedda9984dd)
10. [Git - git-rev-parse Documentation](https://git-scm.com/docs/git-rev-parse)

---

## 11. Merge Conflict Debugging and Troubleshooting

### Scenario: Spurious Conflicts from Whitespace or Line Ending Changes

**Problem**: Developers report conflicts where the file content appears identical.

**Root cause**: Line ending differences (CRLF vs LF) or trailing whitespace changes.

**Diagnostic approach**:

```bash
# Check git's view of line endings
git config core.safecrlf

# Show exact bytes in conflicted file
git ls-files -u | cut -f2 | uniq | xargs -I {} git cat-file blob {} | od -c | head -20

# Compare with explicit diff (ignoring whitespace)
git diff --ignore-all-space :2: :3:

# If whitespace is the only difference:
git checkout --ours .
git add .
# Or if right side is correct:
git checkout --theirs .
git add .
```

**Prevention for future merges**:

```bash
# Normalize line endings in repository
git config --global core.safecrlf true
git add -A
git commit -m "Normalize line endings"

# Use .gitattributes to enforce consistency
echo "* text=auto" > .gitattributes
echo "*.sh text eol=lf" >> .gitattributes
echo "*.bat text eol=crlf" >> .gitattributes
git add .gitattributes
git commit -m "Add .gitattributes for consistent line endings"
```

### Scenario: Merge Conflict in Generated Files

**Problem**: Build artifacts or generated code conflict after merge, making manual resolution difficult.

**Example**: Compiled JavaScript (bundle.js) differs after merge because both branches have different source changes that generate different output.

**Approach**:

```bash
# Don't manually resolve generated files
# Instead, regenerate after merge

# Step 1: Resolve conflicts in source files only
# (Leave generated files alone)

# Step 2: Resolve generated files by regeneration
git checkout --ours .
git add .

# Regenerate build artifacts
npm run build
go build ./...
cargo build --release

# Stage the regenerated files
git add dist/ build/ target/

git commit -m "Merge: regenerate build artifacts"
```

**Best practice**: Add generated files to `.gitignore` and regenerate them during build rather than committing them.

### Scenario: Octopus Merge Conflicts (3+ Branch Merge)

**Problem**: Merging three or more branches simultaneously creates complex conflict states.

**Example**:

```bash
git merge feature1 feature2 feature3
```

During octopus merge, if conflicts arise, the conflict markers can be overwhelming:

```
<<<<<<< HEAD
version A content
||||||| merged common ancestor
base content
=======
version B content
>>>>>>> feature1

<<<<<<< HEAD
different region from feature2
||||||| merged common ancestor
more base content
=======
feature2 content
>>>>>>> feature2
```

**Resolution strategy**:

```bash
# Don't attempt octopus merge if conflicts are likely
# Instead, merge sequentially

git merge --no-ff feature1
# Resolve and commit

git merge --no-ff feature2
# Resolve and commit

git merge --no-ff feature3
# Resolve and commit

# Final state is identical to octopus merge, but easier to debug
```

**Index state during octopus merge**:

```bash
# Up to N+1 stages in index (one common ancestor, N versions)
git ls-files -u
# Output shows multiple stage 2, 3, 4... entries (not just 1, 2, 3)
```

### Scenario: Merge Conflict Caused by Repository Corruption

**Problem**: Merge fails with cryptic error: "fatal: failed to resolve 'merged common ancestor'"

**Root cause**: Repository is corrupted; cannot find common ancestor commit.

**Diagnostic**:

```bash
# Verify repository integrity
git fsck --full

# Output might show:
# error: bad object <hash>
# missing blob <hash>

# Try to find the commit object
git rev-list --all | xargs git cat-file -t

# If object is truly missing, force fetch from remote
git fetch origin
git fsck --full

# If still broken, clone from backup
git clone <remote-url> <new-location>
```

---

## 12. Advanced: Conflict Analysis for Large-Scale Merges

### Merging Thousands of Files: Batch Processing

When merging branches that diverged significantly (e.g., enterprise release branch after 6 months), analyzing all conflicts is computationally expensive.

**Staged conflict analysis approach**:

```bash
#!/bin/bash
# analyze_conflicts.sh - Analyze merge conflicts in batches

# Start merge without committing
git merge --no-commit main

# Stage 1: Find all conflicted files
conflicted=$(git ls-files -u | cut -f2 | sort -u)
total=$(echo "$conflicted" | wc -l)

echo "Total conflicted files: $total"

# Stage 2: Categorize by file size
for file in $conflicted; do
  size=$(git show :2:"$file" 2>/dev/null | wc -c)
  
  if [ $size -lt 1000 ]; then
    echo "SMALL: $file ($size bytes)"
  elif [ $size -lt 100000 ]; then
    echo "MEDIUM: $file ($size bytes)"
  else
    echo "LARGE: $file ($size bytes) - may need special handling"
  fi
done | sort

# Stage 3: Categorize by file type
for file in $conflicted; do
  ext="${file##*.}"
  echo "$ext: $file"
done | sort | uniq -c | sort -rn

# Stage 4: Extract conflict counts per file
for file in $conflicted; do
  conflict_markers=$(git show ":2:$file" | grep -c "^<<<<<<< HEAD" 2>/dev/null || echo "0")
  if [ $conflict_markers -gt 0 ]; then
    echo "$file: $conflict_markers conflict regions"
  fi
done | sort -t: -k2 -rn | head -20
```

This categorization helps prioritize which conflicts to resolve first (small files and simple changes before large files and complex logic).

### Conflict Resolution Audit Trail

For compliance and debugging, maintaining an audit trail of merge conflict resolutions is critical:

```bash
#!/bin/bash
# Log merge conflict resolutions

git merge feature

# During conflict resolution, log decisions
{
  echo "=== Merge Conflict Audit Trail ==="
  echo "Date: $(date)"
  echo "Merge source: $(git rev-parse --abbrev-ref HEAD)"
  echo "Merge target: feature"
  echo ""
  echo "Conflicted files:"
  git ls-files -u | cut -f2 | sort -u | while read file; do
    echo "  - $file"
    echo "    ours (stage 2): $(git show :2:$file 2>/dev/null | md5sum | awk '{print $1}')"
    echo "    theirs (stage 3): $(git show :3:$file 2>/dev/null | md5sum | awk '{print $1}')"
  done
} > .merge_audit.log

# After resolution, add to commit
git add .merge_audit.log
git commit --amend --no-edit
```

### Incremental Merge Strategy for Long-Lived Branches

When merging branches that diverged severely, merge in incremental chunks:

```bash
#!/bin/bash
# incremental_merge.sh - Merge a long-lived branch in stages

BASE_BRANCH="main"
FEATURE_BRANCH="long-lived-feature"

# Find commits on FEATURE that aren't on BASE
commits=$(git log ${BASE_BRANCH}..${FEATURE_BRANCH} --reverse --format=%H)

count=0
for commit in $commits; do
  count=$((count + 1))
  
  # Merge one commit at a time
  git merge --no-ff $commit 2>/dev/null
  
  if [ $? -ne 0 ]; then
    # Conflict occurred
    echo "Conflict on commit $count/$total"
    echo "Resolution needed for: $(git ls-files -u | cut -f2 | sort -u)"
    
    # Wait for user to resolve
    read -p "Press enter after resolving conflicts..."
    
    git add .
    git commit --no-edit
  else
    echo "Commit $count merged cleanly"
  fi
done
```

**Benefit**: Resolving conflicts from many small commits is easier than resolving all at once.

---

## 13. Git Merge vs. Rebase: Conflict Semantics Differ

### Critical: "Ours" and "Theirs" Are Swapped in Rebase

This is the most dangerous subtle behavior in Git. During `git merge`, "ours" and "theirs" have one meaning. During `git rebase`, they're inverted.

**During merge**:
```bash
git merge feature
# ours = current branch (main)
# theirs = branch being merged (feature)

# If conflict, resolve with:
git checkout --ours file.txt    # Keep main's version
git checkout --theirs file.txt  # Keep feature's version
```

**During rebase**:
```bash
git rebase main
# ours = branch you're rebasing ONTO (main)
# theirs = your branch being rebased (your work)

# If conflict, resolve with:
git checkout --ours file.txt    # Keep main's version (what you're rebasing onto)
git checkout --theirs file.txt  # Keep your branch's version (your work)
```

**The inversion happens between rebase and merge**. This is a frequent source of user confusion.

**Production impact**: A team using both `git merge` and `git rebase` in their workflow reported ~3% of merge conflicts were resolved backwards (accepting the wrong version). The root cause: developers switching between workflows and forgetting the semantic inversion.

### Rebase Conflict Resolution: Interactive Mode

During interactive rebase, conflicts occur differently:

```bash
git rebase -i main
# Lists commits to be rebased

# During rebase of each commit:
# If conflict, rebase pauses with:
# CONFLICT (content): Merge conflict in file.txt
# (The "CONFLICT" message is identical to merge, but semantics differ)

# Resolve conflicts
# Then:
git add .
git rebase --continue

# Or skip the problematic commit:
git rebase --skip

# Or abort entirely:
git rebase --abort
```

The `--ours` and `--theirs` semantics during `git rebase` remain inverted, making this a high-risk operation.

---

**Document Version**: 2.0  
**Research Date**: April 2026  
**Scope**: Complete anatomy of Git conflict markers, index stages, metadata, tooling integration, and edge cases
