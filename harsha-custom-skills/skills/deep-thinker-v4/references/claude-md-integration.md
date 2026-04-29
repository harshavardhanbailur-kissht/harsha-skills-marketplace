# CLAUDE.md Integration: Deep Thinker v4.0

## Understanding CLAUDE.md Memory Hierarchy

CLAUDE.md (and related config files) form a layered memory system. Deep Thinker reads from this hierarchy at SCOPE phase entry to understand constraints.

### Memory Layers (Precedence Order)

1. **Enterprise Layer** (`~/.claude/enterprise.md`)
   - Company-wide tool usage, security policies, approved libraries
   - Rarely changes; applies to all projects
   - *Deep Thinker reads:* Approved tech stack, security constraints

2. **User Layer** (`~/.claude/user.md`)
   - Personal workflows, preferred patterns, coding standards
   - User-specific defaults; overridable per-project
   - *Deep Thinker reads:* Code style preferences, testing expectations

3. **Project Layer** (`.claude/CLAUDE.md` at repo root)
   - **Most important for Deep Thinker**
   - Project goals, tech decisions, team norms, known risks
   - Applied to all analyses in this project
   - *Deep Thinker reads:* Everything (see below)

4. **Local Layer** (`.claude/local.md`)
   - Developer-specific overrides for this environment
   - Temporary; not committed
   - *Deep Thinker reads:* Local debugging flags, performance constraints

5. **Subtree Layer** (`.claude/CLAUDE.md` in subdirectory)
   - Narrows scope for specific feature/module
   - Overrides project layer for this subtree only
   - *Deep Thinker reads:* Module-specific constraints when scoped to subtree

---

## Separation of Concerns

### CLAUDE.md = Persistent Project Configuration
- What is the project trying to achieve?
- What constraints are non-negotiable?
- What patterns have we learned?
- Who are stakeholders?
- What are known risks?

**Ownership:** Team/project maintainers. Committed to repo.

### .deep-think/ = Per-Analysis Output
- How do we solve THIS problem?
- What analysis path did we take?
- What trade-offs did we make?
- What did we learn?
- What are next steps?

**Ownership:** Claude during analysis. Not committed (usually).

**They don't overlap.** CLAUDE.md constrains the search space. .deep-think/ documents the journey within that space.

---

## Reading CLAUDE.md Before SCOPE Phase

At analysis start, Deep Thinker should:

```
1. Locate relevant CLAUDE.md files
   └─ Start at project root, traverse up if needed
   └─ Check for subtree configs if scoped

2. Extract constraints:
   ├─ Hard constraints (non-negotiable)
   ├─ Soft preferences (guidelines)
   ├─ Known risks (project history)
   ├─ Stakeholder concerns
   └─ Tech stack boundaries

3. Document findings in SCOPE.md:
   ├─ "Constraints from CLAUDE.md:"
   ├─ "Team norms from project layer:"
   ├─ "Known risks to avoid:"
   └─ "Reference: [path/to/CLAUDE.md]"

4. Validate scope against project goals:
   └─ "Does this analysis advance [stated project goal]?"
```

**Key question:** "What would the team reject?" Answer this from CLAUDE.md, not from guessing.

---

## CLAUDE.md Informs the Complexity Gate

Deep Thinker uses CLAUDE.md to calibrate whether a problem needs full 5-phase analysis or can shortcut:

**Complexity Gate Decision:**
```
SHALLOW (SCOPE + GROUND only):
  ├─ Problem is within a single well-known subsystem (CLAUDE.md confirms)
  ├─ No unknown dependencies (CLAUDE.md maps team/system structure)
  └─ Risk is low (CLAUDE.md history shows no surprises here)

MEDIUM (SCOPE + GROUND + DIVERGE):
  ├─ Multiple subsystems involved
  ├─ Some unknowns in dependencies
  └─ Moderate risk (interesting but not critical)

DEEP (All 5 phases):
  ├─ Architectural implications (CLAUDE.md goal-critical)
  ├─ High unknowns (CLAUDE.md flags as known-hard-problem)
  └─ Team consensus required (CLAUDE.md lists stakeholders)
```

**Example:**
- "Refactor module X: CLAUDE.md says it's stable, internal-only → SHALLOW"
- "Integrate new payment API: CLAUDE.md says it touches billing, audit, compliance → DEEP"

---

## Minimal CLAUDE.md Template for Deep-Thinker-Aware Projects

For teams adopting Deep Thinker, use this template. Commit it to `.claude/CLAUDE.md`:

```markdown
# Project Context for Deep Thinker

## Project Goal
[1-2 sentence north star. Deep Thinker uses this to validate scope alignment.]

## Tech Stack & Constraints
- **Language(s)**: [e.g., Python 3.10+, TypeScript 5.0+]
- **Approved frameworks**: [e.g., Django, React, FastAPI]
- **Database**: [e.g., PostgreSQL, read-only access]
- **Deployment**: [e.g., Docker, AWS Lambda]
- **Non-negotiable**: [e.g., GDPR compliance, single-region]

## Subsystem Ownership
- **Auth**: Owner + Slack handle
- **Database**: Owner + Slack handle
- **API**: Owner + Slack handle
- [Add your subsystems]

## Known Risks / Lessons Learned
- [Risk 1]: Why it matters. How to avoid it.
- [Risk 2]: Why it matters. How to avoid it.

## Team Norms
- Code reviews required before merge
- Tests must cover [threshold]%
- [Your standard]

## Stakeholders for Major Decisions
- **Product**: [Name], approves scope changes
- **Security**: [Name], approves auth/data changes
- **Ops**: [Name], approves deployment changes

## Analysis Defaults
- **Typical complexity**: [SHALLOW / MEDIUM / DEEP]
- **Thinking budget**: [Phase 1-2 only / Full 5 phases]
- **Success metrics source**: [Team OKRs / README / other]
```

**Why this matters:** Deep Thinker reads this once and never needs to ask. All analyses in this project automatically honor these constraints.

---

## When CLAUDE.md Is Missing

If a project has no CLAUDE.md:

1. **At SCOPE entry**, Deep Thinker should note: "No project config found. Assuming MEDIUM complexity."
2. **Explicit discovery phase**: Spend extra time in SCOPE asking clarifying questions
3. **Document findings**: Write a minimal CLAUDE.md template as part of EXECUTION_CHECKLIST
4. **Recommend to team**: "Consider creating `.claude/CLAUDE.md` for consistency"

This prevents analysis scope creep and helps future Claude sessions help the same project.

---

## Subtree Scoping Example

If analyzing `src/payments/` specifically:

```
Project has: .claude/CLAUDE.md (general)
Also has: src/payments/.claude/CLAUDE.md (specific to payments)

Deep Thinker reads BOTH and merges:
  ├─ Inherit project goals + tech stack
  ├─ Override with payments-specific constraints
  ├─ Note strict compliance needs (from payments CLAUDE.md)
  └─ Result: SCOPE.md cites both files
```

**Output in SCOPE.md:**
```
## Constraints
- [General]: PostgreSQL, TypeScript, Docker (from project)
- [Payments-specific]: PCI-DSS compliance, audit logging (from subtree)
- [Reference]: .claude/CLAUDE.md + src/payments/.claude/CLAUDE.md
```

This prevents accidentally treating payment code with generic-project rigor.
