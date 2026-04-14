# Refactoring Catalog (Language-Agnostic)

Dense reference of refactoring patterns, code smells, safety methodology, and
complexity metrics. Read this for ANY language.

## Table of Contents

1. [Code Smells — When to Refactor](#code-smells)
2. [Refactoring Patterns — How to Refactor](#refactoring-patterns)
3. [Safety Methodology](#safety-methodology)
4. [Incremental Strategies](#incremental-strategies)
5. [Git Safety Patterns](#git-safety-patterns)
6. [Complexity Metrics & Thresholds](#complexity-metrics)

---

## Code Smells

Code smells are heuristics that indicate refactoring opportunities. Each smell
includes what to look for and which refactoring(s) to apply.

### Bloaters

| Smell | Detection | Refactoring | Risk |
|-------|-----------|-------------|------|
| **Long Method** | >20 lines, multiple indent levels, hard to name | Extract Method, Decompose Conditional | Low |
| **Large Class** | >300 lines, >15 methods, multiple responsibilities | Extract Class, Extract Interface | Medium |
| **Primitive Obsession** | Strings for IDs/money/dates, parallel arrays | Replace with Value Object | Low |
| **Long Parameter List** | >4 params, same groups repeated | Introduce Parameter Object | Low |
| **Data Clumps** | Same 3+ variables always appear together | Extract Class | Low |

### OO Abusers

| Smell | Detection | Refactoring | Risk |
|-------|-----------|-------------|------|
| **Switch Statements** | Type-based switches duplicated across codebase | Replace Conditional with Polymorphism | High |
| **Temporary Field** | Fields only used in certain code paths | Extract Class | Low |
| **Refused Bequest** | Subclass ignores most parent methods | Replace Inheritance with Delegation | Medium |

### Change Preventers

| Smell | Detection | Refactoring | Risk |
|-------|-----------|-------------|------|
| **Divergent Change** | One class modified for many unrelated reasons | Extract Class (split by responsibility) | Medium |
| **Shotgun Surgery** | One change requires edits in 5+ files | Move Methods/Fields to consolidate | High |

### Dispensables

| Smell | Detection | Refactoring | Risk |
|-------|-----------|-------------|------|
| **Dead Code** | Unreachable paths, unused methods/variables | Remove Dead Code | Very Low |
| **Duplicate Code** | Copy-pasted blocks, same logic with minor variations | Extract Method, Pull Up Method | Low-Medium |
| **Speculative Generality** | Abstract classes with one subclass, unused hooks | Inline Class, Collapse Hierarchy | Very Low |
| **Lazy Class** | Class does almost nothing | Inline Class | Very Low |

### Couplers

| Smell | Detection | Refactoring | Risk |
|-------|-----------|-------------|------|
| **Feature Envy** | Method calls many methods on another object | Move Method to the envied class | Low-Medium |
| **Message Chains** | a.getB().getC().getD().do() chains | Hide Delegate | Medium |
| **Middle Man** | >50% of methods just delegate | Remove Middle Man | Low |

---

## Refactoring Patterns

### Composing Methods (Low Risk)

**Extract Method**: Move a code fragment into a new method with a descriptive name.
- When: Block handles a single logical task; duplicated in multiple places
- Safety: Verify extracted method has clear inputs/outputs; test covers both paths
- Anti-pattern: Don't extract trivial 1-line expressions

**Inline Method**: Replace a method with its body at the call site.
- When: Method body is as clear as the method name; too many trivial delegations
- Safety: Check all call sites; verify no subclass override

**Extract Variable**: Name a complex expression for readability.
- When: Expression is hard to understand at a glance
- Safety: Verify the expression has no side effects

**Replace Temp with Query**: Convert a local variable to a method call.
- When: Temp holds a value that could be computed; needed in multiple methods
- Safety: Ensure the computation is deterministic and has no side effects

### Moving Features (Medium Risk)

**Move Method**: Move a method to the class it interacts with most.
- When: Method uses more features of another class (Feature Envy)
- Safety: Update ALL call sites; check for polymorphic dispatch

**Move Field**: Move a field to where it's used most.
- When: Field accessed more by another class than its owner
- Safety: Update all accessors; check serialization

**Extract Class**: Split a class that does too much into two.
- When: Class has >2 distinct responsibilities
- Safety: Map all users of the original class; test both resulting classes

### Simplifying Conditionals (Low-Medium Risk)

**Decompose Conditional**: Extract complex conditions into named methods.
- When: `if (date.before(SUMMER_START) || date.after(SUMMER_END))` → `if (isNotSummer(date))`
- Safety: Name must accurately describe the condition

**Replace Nested Conditionals with Guard Clauses**: Use early returns.
- When: Deeply nested if/else obscures the main logic path
- Safety: Verify early returns don't skip cleanup/finally blocks

**Replace Conditional with Polymorphism**: Use subclasses instead of type switches.
- When: Same switch/case appears in multiple places switching on a type field
- Safety: HIGH RISK — requires creating class hierarchy; test exhaustively
- Anti-pattern: Don't use for simple 2-3 branch conditions

### Organizing Data (Low Risk)

**Encapsulate Field**: Replace public field with getter/setter.
- When: Direct field access prevents future validation/logging
- Safety: Find all direct accesses with grep

**Replace Magic Number with Constant**: Name hard-coded values.
- When: Numbers appear in code without explanation
- Safety: Verify the constant value matches ALL usages

**Introduce Parameter Object**: Group related parameters into an object.
- When: Same 3+ params appear in multiple method signatures
- Safety: Update all call sites

### Generalization (Medium-High Risk)

**Pull Up Method/Field**: Move shared member to superclass.
- When: Multiple subclasses have identical method/field
- Safety: Verify the member is truly identical across all subclasses

**Push Down Method/Field**: Move to specific subclass.
- When: Superclass member only used by one subclass
- Safety: Verify no other subclass or external code depends on it

**Substitute Algorithm**: Replace entire method body with better approach.
- When: A simpler/more efficient algorithm exists
- Safety: HIGH RISK — test with same inputs, verify identical outputs

---

## Safety Methodology

### The Safety Pyramid (Most Important First)

1. **Green tests before starting.** Never refactor a failing test suite.
2. **Clean git state.** Uncommitted changes make rollback impossible.
3. **One change at a time.** Test after each individual change.
4. **Immediate revert on failure.** Don't try to "fix the fix."
5. **Atomic commits.** Each change = one commit = one revertible unit.
6. **Preserve public API.** Internal structure changes only.

### Characterization Tests

Before refactoring untested code, capture its current behavior:
1. Call the code with known inputs
2. Record the actual output (even if "wrong")
3. Write a test asserting that output
4. Now you have a regression safety net

This is the fastest way to add a safety net to legacy code.

### The Mikado Method (for Large Refactorings)

1. Try the desired change
2. If it breaks, note what broke
3. Revert the change
4. Fix the prerequisite that broke
5. Repeat until the desired change works cleanly

This builds a dependency tree of safe, small changes.

### When to Abort a Refactoring

- Test coverage is too low to catch regressions (<60% coverage)
- The change cascades to >10 files (consider incremental strategy instead)
- You discover the "refactoring" actually requires behavior changes
- Three consecutive reverts on similar changes (the code is more coupled than expected)

---

## Incremental Strategies

For refactorings too large for a single pass:

### Strangler Fig
Gradually replace old code with new, routing traffic to the new implementation
incrementally. Old code is removed only after new code handles 100% of cases.
Best for: replacing entire modules or services.

### Branch by Abstraction
1. Create an abstraction layer (interface/abstract class)
2. Route all existing calls through the abstraction
3. Implement a new version behind the abstraction
4. Switch the abstraction to use the new version
5. Remove the old version
Best for: swapping implementations (e.g., new ORM, new HTTP client).

### Expand-Contract (Parallel Change)
1. **Expand**: Add the new way alongside the old way
2. **Migrate**: Move all callers to use the new way
3. **Contract**: Remove the old way
Best for: API changes, database schema changes.

---

## Git Safety Patterns

### Atomic Commits During Refactoring
- One behavior-preserving change per commit
- Tests must pass at every commit (bisect-friendly)
- Commit message format: `refactor: [what changed]`

### Separate Refactoring from Features
- Never mix refactoring commits with feature commits in the same PR
- Reviewers can verify behavior preservation when changes are isolated

### Checkpoint Strategy
```bash
# Before starting
git tag refactor-start

# After each successful step
git add -A && git commit -m "refactor: [description]"

# On failure — revert to last good commit
git checkout -- .

# If everything goes wrong — return to start
git reset --hard refactor-start
```

---

## Complexity Metrics

### Thresholds

| Metric | Low | Medium | High | Action |
|--------|-----|--------|------|--------|
| Cyclomatic Complexity | 1-5 | 6-10 | 11-20 | Refactor >10 |
| Cognitive Complexity | 1-8 | 9-15 | >15 | Refactor >15 |
| Method Length (lines) | 1-15 | 16-30 | >30 | Extract at >20 |
| Class Length (lines) | 1-200 | 200-400 | >400 | Split at >300 |
| Parameters | 1-3 | 4-5 | >5 | Object at >4 |
| Nesting Depth | 1-2 | 3 | >3 | Guard clauses at >3 |

### CLI Tools by Language

| Language | Tool | Command |
|----------|------|---------|
| Multi-language | lizard | `lizard [path] --CCN 10` |
| JS/TS | eslint | `eslint --rule 'complexity: [error, 10]'` |
| Python | radon | `radon cc [path] -s -n C` |
| Go | gocyclo | `gocyclo -over 10 .` |
| Go | gocognit | `gocognit -over 15 .` |
| Rust | clippy | `cargo clippy -- -W clippy::cognitive_complexity` |
| Java | PMD | `pmd check -d src -R category/java/design.xml` |

### Priority Formula for Refactoring Opportunities

```
Priority = (Impact × 2 + (6 - Risk)) / Effort
```

Where Impact, Risk, Effort are each scored 1-5.
- High Impact + Low Risk + Low Effort = highest priority
- Low Impact + High Risk + High Effort = skip
