# Git Merge Intelligence Research

## Files in This Directory

### git-conflict-anatomy.md
A comprehensive, expert-level research document covering the complete anatomy of Git conflict markers and three-way merge information.

**Covers:**
1. Basic conflict marker structure (`<<<<<<<`, `=======`, `>>>>>>>`)
2. Enhanced diff3 style with common ancestor markers (`|||||||`)
3. Hidden merge information in Git index stages (:1:, :2:, :3:)
4. Merge metadata files (ORIG_HEAD, MERGE_HEAD, MERGE_MSG)
5. File-level resolution with `--ours` and `--theirs`
6. Complete merge index stage model (stages 0-3)
7. Special cases for binary files, submodules, and deletions
8. Querying unmerged files with `git ls-files -u`
9. Common ancestor finding and criss-cross merges
10. Practical programmatic extraction with scripts and Python examples

**Key Audience:** Developers building merge tools, conflict resolution systems, and Git integration software.

**Notable Insights:**
- The semantic inversion of "ours" and "theirs" during rebase operations
- How to programmatically extract base/ours/theirs using `git show :1:/:2:/:3:`
- The complete merge context available in .git/ metadata files
- How criss-cross merges create multiple valid merge bases
- Building intelligent merge tools that leverage full three-way context

## Research Methodology

This document synthesizes official Git documentation, core Git references, technical blog posts, and community resources. Every factual claim includes source citations as Markdown hyperlinks to:
- Official git-scm.com documentation
- Git man pages and kernel documentation
- Published technical blog posts
- Community tutorials and guides

## For Building Merge Intelligence Tools

This research document provides the foundational knowledge for:
- Custom merge strategies and conflict analyzers
- IDE merge conflict resolution features
- Automated conflict detection and resolution
- Semantic/language-aware merge tools
- Merge conflict visualization and explanation systems
- Audit trails and merge decision tracking

---

Generated: 2026-04-07
Research Agent: Claude (Haiku 4.5)
