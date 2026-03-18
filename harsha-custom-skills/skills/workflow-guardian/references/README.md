# Workflow Guardian Reference Documentation

This directory contains comprehensive documentation for safely maintaining and extending React applications without breaking existing state management.

## Files

### git-history-analysis.md (1423 lines)

**Complete forensic guide for analyzing git history to detect and prevent regressions.**

A comprehensive reference for understanding code quality patterns through commit history:

1. **Pre-Change Git Analysis Protocol** - How to read git history before making changes
   - Understanding recent commit patterns
   - Identifying file coupling and dependencies
   - Detecting feature additions that led to breakage
   - Finding "fix" commits to understand what broke

2. **Regression Pattern Detection** - Recognizing unstable code patterns
   - Commits where features broke things (with real examples)
   - Fix cascades (Fix → Fix → Fix = incomplete solutions)
   - Architecture decisions vs. implementation commits
   - File addition patterns and their risks

3. **Change Coupling Analysis** - Which files must change together
   - Type definitions coupled with implementations
   - Database migrations coupled with types and hooks
   - App.tsx routing coupled with all pages
   - UI component library coupled with all consumers

4. **Commit Message Forensics** - What messages reveal about code quality
   - "Fix" in message = previous breakage
   - "Add" in message = check for duplication risk
   - "Remove" in message = orphan risk
   - "Refactor" in message = regression risk
   - Commit quality metrics (Ring Kissht 2/5 vs LOS Tracker 4/5)

5. **Git-Based Verification** - Using git to catch errors after changes
   - git diff --stat for change scope verification
   - git diff for detecting unintended changes
   - Finding missing dependencies through file analysis
   - Red flags that indicate problems

6. **Branch Strategy for Safe Features** - How to structure changes
   - Feature branch isolation workflow
   - Incremental commits for easy rollback
   - Pre-merge verification checklist (19 items)
   - One concern per commit principle

### state-management-preservation.md (2044 lines)

**Complete guide to state management patterns in React applications.**

A production-tested reference covering:

1. **Provider Tree Mapping** - How to document and understand provider nesting order
   - Simple single-provider pattern (Ring Kissht Issue Tracker)
   - Complex layered pattern (LOS Issue Tracker)
   - Why order matters and how it breaks

2. **Context Contract Documentation** - Defining what each context exposes
   - What state is held
   - What methods are available
   - Who consumes it
   - What triggers re-renders
   - Safe vs. dangerous extensions

3. **State Dependency Graph** - Mapping which contexts depend on others
   - Simple dependency chains
   - Complex multi-level dependencies
   - Detecting circular dependencies

4. **Safe Patterns for Adding State** - Four approved approaches
   - Adding to existing context (extending)
   - Creating new context (right position)
   - Converting local state to shared state
   - Derived/computed state

5. **Dangerous Patterns to Detect** - Five critical anti-patterns
   - Duplicated state across contexts
   - Circular context dependencies
   - Adding state that should be derived
   - Breaking provider order
   - Over-rendering from poorly structured contexts

6. **Realtime/Subscription Patterns** - Safe async patterns
   - Subscription lifecycle (mount → subscribe → cleanup)
   - Channel naming and filtering
   - Error handling for dropped connections
   - Non-blocking fire-and-forget patterns

7. **Custom Hook Preservation** - How hooks form a contract
   - Hook interface and what consumers rely on
   - Safe modifications (new methods, optional params)
   - Dangerous changes (renamed exports, behavior changes)
   - Memoization best practices

8. **Migration Patterns** - How to safely upgrade state management
   - Phase 1-3 migrations from useState → useContext → Zustand
   - Adding persistence layers
   - Rollback strategies

## Real Code Examples

All patterns illustrated with **actual production code** from:

- `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/`
  - SimpleAuthContext (157 lines)
  - GoogleDriveContext (103 lines)
  - Simple provider pattern

- `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/`
  - AuthContext (368 lines, advanced patterns)
  - useTickets hook (303 lines, subscriptions)
  - useDarkMode hook (120 lines, context + hook pattern)
  - useFocusTrap hook (163 lines)
  - useKeyboardShortcuts hook (185 lines)

## How to Use This Guide

**When adding a feature:**
1. Check section 3 (State Dependency Graph) - where should it live in provider tree?
2. Check section 2 (Context Contract) - what existing contexts will it use?
3. Follow section 4 (Safe Patterns) - which pattern fits your use case?
4. Check section 5 (Dangerous Patterns) - what mistakes to avoid?

**When modifying existing state:**
1. Document the current contract (section 2)
2. Verify dependencies don't become circular (section 3)
3. Check if your change is safe (section 7 for hooks, section 2 for contexts)
4. Plan migration if needed (section 8)

**When debugging state issues:**
1. Map the provider tree (section 1)
2. Check for anti-patterns (section 5)
3. Verify subscription cleanup (section 6)
4. Check for circular dependencies (section 3)

## Key Principles

- **One source of truth** - Each piece of state lives in exactly one place
- **Dependency flows downward** - Parents provide to children, never circular
- **Contract stability** - Don't break what consumers depend on
- **Clear initialization** - Always know when state is ready
- **Graceful degradation** - Handle missing contexts gracefully
- **Thoughtful composition** - Use right tool for right job (hook vs context)

## Quick Checklist

Before committing state management changes:

- [ ] Provider tree documented and dependencies clear
- [ ] Context contracts defined (what's exposed, what consumers use)
- [ ] No circular dependencies
- [ ] All safe patterns followed
- [ ] No dangerous anti-patterns present
- [ ] Subscriptions properly cleaned up
- [ ] No breaking changes to hooks/contexts
- [ ] Re-renders not excessive
- [ ] Error handling present
- [ ] Documentation updated

