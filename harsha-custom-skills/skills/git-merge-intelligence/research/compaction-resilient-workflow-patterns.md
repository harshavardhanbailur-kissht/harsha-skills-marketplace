# Compaction-Resilient Workflow Patterns for Agentic AI Systems

## Executive Summary

Teams building production agentic workflows with Claude Code, Cursor, and similar AI-driven development environments face a critical challenge: **context compaction**. When the context window fills (typically at 95% capacity), the system automatically summarizes conversation history, discarding intermediate reasoning and earlier context. This causes agents to forget what they've done, repeat work, and make inconsistent decisions.

This research document synthesizes patterns, architectures, and practices developed by teams surviving session resets and context loss. The core insight is **writing all state to files immediately and designing workflows where each invocation reads complete state from files rather than relying on conversation memory**.

---

## 1. The Compaction Problem

### How Context Compaction Works

Claude Code and similar systems manage a finite context window (typically 200K tokens) across:
- System prompt and tool definitions
- Conversation history (messages and tool outputs)
- Recent file reads
- Persistent memory (CLAUDE.md, auto-memory)
- Loaded skills

When approximately 95% of the context is consumed, the system triggers **automatic compaction**, which:

1. **Preserves**: System prompt, recent critical messages, persistent rules (CLAUDE.md)
2. **Discards**: Older conversational reasoning, intermediate findings, tool output history
3. **Summarizes**: Earlier conversation into condensed summary (if needed)

Reference: [How Claude Code works - Claude Code Docs](https://code.claude.com/docs/en/how-claude-code-works), [Context windows - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/context-windows)

### The Three Layers of Loss

**Layer 1: Conversational History Loss**
- Intermediate reasoning steps vanish
- Earlier questions about project structure are forgotten
- Discussion context from 100+ messages ago is gone
- The agent becomes unable to explain "why we decided X earlier"

**Layer 2: Implicit Context Loss**
- Architectural decisions established in early conversation disappear
- Code style preferences, naming conventions, design patterns become opaque
- Dependencies between tasks are lost
- Constraints on implementation approaches are forgotten

**Layer 3: Tool Output Loss**
- Git diffs, test output, build logs from earlier steps are cleared
- The agent can't reference "the test that failed on line 47"
- File read results are cached only temporarily

Reference: [Why Claude Loses Context After Compaction (And How to Prevent It)](https://docs.bswen.com/blog/2026-02-09-claude-context-loss-compaction/)

### The "Amnesia" Problem: Practical Impact

When compaction occurs mid-workflow:

1. **Repeated Work**: Agent doesn't know it already ran migration #1, runs it again → duplicate keys or constraint violations
2. **Inconsistent Decisions**: Agent decides to rename `user_id` to `userId` (first decision), then later (after compaction) decides to keep `user_id` (second decision), creating incompatible code
3. **Broken Dependencies**: Agent refactors module A (which was already refactored), then doesn't update module B that depends on A
4. **Constraint Violation**: Earlier work established "never modify config.prod.yml directly", but after compaction, agent edits it anyway
5. **Multi-Tab Coordination Failure**: When running multiple Claude Code sessions with explicit coordination rules in CLAUDE.md, tabs don't actually coordinate; tabs duplicate work silently without mutual exclusion

Reference: [The 4-Step Protocol That Fixes Claude Code Agent's Context Amnesia](https://medium.com/@ilyas.ibrahim/the-4-step-protocol-that-fixes-claude-codes-context-amnesia-c3937385561c), [Multi-tab coordination rules in CLAUDE.md are not enforced](https://github.com/anthropics/claude-code/issues/32292)

---

## 2. Checkpoint Formats That Work

### 2.1 JSON Checkpoint Schema

**Structure**: A machine-readable state file with versioning, timestamps, and schema validation.

```json
{
  "version": "1.0",
  "checkpoint_id": "ckpt-2026-03-15-14-32-001",
  "timestamp": "2026-03-15T14:32:45Z",
  "task_list": [
    {
      "id": "migrate-users-001",
      "name": "Migrate user table schema",
      "status": "completed",
      "completed_at": "2026-03-15T13:45:00Z",
      "result": {
        "rows_migrated": 15847,
        "duration_seconds": 234
      }
    },
    {
      "id": "migrate-sessions-002",
      "name": "Migrate session table schema",
      "status": "in_progress",
      "started_at": "2026-03-15T14:00:00Z",
      "current_step": "Creating index on new schema",
      "expected_completion": "2026-03-15T15:00:00Z"
    },
    {
      "id": "update-app-code-003",
      "name": "Update application code for new schema",
      "status": "pending",
      "dependencies": ["migrate-sessions-002"],
      "blocked_by": "migrate-sessions-002"
    }
  ],
  "completed_items": ["migrate-users-001"],
  "current_phase": "schema_migration",
  "next_action": "monitor and complete sessions table migration, then update app code",
  "decisions": [
    {
      "decision_id": "naming-001",
      "context": "Column naming convention",
      "decision": "Use snake_case for all database columns",
      "rationale": "Matches existing schema in legacy tables; ensures consistency across database",
      "made_at": "2026-03-15T10:30:00Z",
      "made_by_step": "planning-001"
    }
  ],
  "constraints": [
    "Never modify config.prod.yml directly; use environment variables",
    "All migrations must include rollback procedures",
    "Tests must pass before deployment"
  ],
  "error_log": [
    {
      "timestamp": "2026-03-15T13:20:00Z",
      "step": "migrate-users-001",
      "error": "Duplicate key error on email column",
      "resolution": "Added pre-migration deduplication step",
      "status": "resolved"
    }
  ],
  "file_state": {
    "migrations/001_user_schema.sql": "hash_abc123",
    "src/models/user.ts": "hash_def456",
    "tests/integration/migration.test.ts": "hash_ghi789"
  }
}
```

**Key Properties**:
- **Versioning**: Allows schema evolution
- **Task List**: Explicit status for each work item (pending/in_progress/completed/failed)
- **Decision Rationale**: Explains WHY decisions were made (so agent doesn't re-debate them)
- **Constraints**: Hard boundaries that persist across context resets
- **File State Hashes**: Quick verification that files haven't been unexpectedly modified
- **Error Log**: Tracks what went wrong and how it was resolved

**When to Use**: Large multi-phase projects, long-running refactors, critical infrastructure changes where decision consistency is mandatory.

Reference: [Checkpointing and Resuming Workflows](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming), [LangGraph State Management for Multi-Agent Workflows](https://medium.com/@bharatraj1918/langgraph-state-management-part-1-how-langgraph-manages-state-for-multi-agent-workflows-da64d352c43b)

### 2.2 Markdown State File with Structured Sections

**Structure**: Human-readable state in Markdown with clear section headers.

```markdown
# Project State: Database Migration (2026-03-15)

## Current Phase
- **Phase**: Schema Migration (Step 2 of 4)
- **Started**: 2026-03-15 10:00 UTC
- **Expected Completion**: 2026-03-15 16:00 UTC

## Task Progress

### Completed
- [x] Phase 1: Planning & Design Review (✓ 2026-03-15 12:30)
- [x] Phase 2a: User Table Migration (✓ 2026-03-15 13:45)

### In Progress
- [ ] Phase 2b: Session Table Migration (🔄 started 14:00)
  - Current step: Creating btree index on user_id
  - Estimated time remaining: 45 minutes

### Pending
- [ ] Phase 3: Application Code Updates (blocked by 2b)
- [ ] Phase 4: Deployment & Verification

## Critical Decisions Made
| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| Naming Convention | snake_case columns | Consistency with legacy tables | 2026-03-15 10:30 |
| Deployment Strategy | Blue-green | Zero downtime requirement | 2026-03-15 10:45 |
| Rollback Plan | DB restore + code revert | Must be fast (< 5min) | 2026-03-15 11:00 |

## System Constraints
- **Hard Rules**: Never edit config.prod.yml; always include rollback procedures
- **Testing**: All migrations must pass integration tests before advancing
- **Approval**: Phase 4 requires engineering lead sign-off

## Known Issues & Resolutions
| Issue | When | Resolution | Status |
|-------|------|-----------|--------|
| Duplicate email values | 2026-03-15 13:20 | Pre-migration deduplication added | ✓ Resolved |
| Index creation timeout | Expected | Increase timeout to 30min; add progress logging | Preventive |

## Next Immediate Action
Resume session table migration (Step 2b).
If query still running, monitor progress and estimate completion.
Do NOT restart the migration; continue the existing one.

## Files Involved
- `migrations/001_user_schema.sql` (hash: abc123def456)
- `migrations/002_session_schema.sql` (hash: def456ghi789)
- `src/models/user.ts` (hash: ghi789jkl012)
- `src/models/session.ts` (hash: jkl012mno345)
- Tests: `tests/integration/migration.test.ts` (hash: mno345pqr678)
```

**Advantages**:
- Human-readable for quick scanning
- Embeds rationale directly (agent understands context)
- Easy to version control and diff
- Can be reviewed by non-technical stakeholders

**When to Use**: Multi-phase projects, team coordination, situations where decision rationale must be visible and auditable.

### 2.3 Git-Based Checkpointing

**Pattern**: Use Git commits as checkpoints, with commit messages containing structured state.

```bash
# After each major phase, commit with structured message
git add -A
git commit -m "CHECKPOINT: User migration complete (15,847 rows)

[PHASE]: schema_migration
[STATUS]: completed
[TIMESTAMP]: 2026-03-15T13:45:00Z
[NEXT_ACTION]: Begin session table migration
[FILES_MODIFIED]:
  - migrations/001_user_schema.sql
  - src/models/user.ts
  - tests/integration/migration.test.ts
[DECISIONS]:
  - Column naming: snake_case (consistency with legacy)
[CONSTRAINTS]:
  - Never modify config.prod.yml directly
  - All migrations include rollback procedures
[ERRORS_ENCOUNTERED]:
  - Duplicate key on email (RESOLVED: added dedup step)
"
```

**Advantages**:
- Natural git history becomes audit trail
- Can revert to any checkpoint
- Supports multiple parallel agent branches (git worktrees)
- Teams can easily see what each agent did

**When to Use**: Teams using Git for coordination, multi-agent workflows with Cursor 2.0 (supports up to 8 agents with separate worktrees), situations where full version history is valuable.

Reference: [Cursor 2.0: Agent-First Architecture](https://www.digitalapplied.com/blog/cursor-2-0-agent-first-architecture-guide), [agentic-cursorrules on GitHub](https://github.com/s-smits/agentic-cursorrules)

### 2.4 File-Based State Machines

**Pattern**: Each file represents a state; agent reads current state from filename or file content, performs action, writes new state file.

```
project/.state/
├── current-phase.txt          # "schema_migration" or "testing" or "deployment"
├── migration-status.json      # detailed migration state
├── blocked-items.txt          # list of items waiting on others
├── decisions.md               # all decisions made so far
├── completed-tasks.log        # append-only log of completed tasks
└── next-action.txt            # explicit next step (for quick resume)
```

**Example Flow**:
1. Agent starts → reads `current-phase.txt` → sees "schema_migration"
2. Agent reads `migration-status.json` → sees user table done, session table in progress
3. Agent reads `next-action.txt` → "monitor session index creation"
4. Agent monitors; when done, appends to `completed-tasks.log`, updates `migration-status.json`, writes new `next-action.txt`
5. Context compaction occurs → no problem, all state is in files
6. Agent resumes in new session → reads all .state files again → continues from exact previous point

**Advantages**:
- Fail-safe: all state is persistent on disk, not in memory
- Quick to read on each invocation
- State transitions are explicit and auditable
- Supports idempotency checking (if task is already completed, skip it)

---

## 3. Architecture Patterns for Resilient Workflows

### 3.1 The "Stateless Handler" Pattern

**Core Idea**: Never rely on conversation memory. Each agent invocation reads ALL context from files, acts, and writes results back to files.

```
Every agent invocation:
  1. READ state from .claude/state/ (JSON, Markdown, or text files)
  2. DETERMINE current position and next action
  3. EXECUTE action
  4. WRITE results immediately to state files
  5. APPEND to progress log
```

**Implementation in Claude Code**:

```markdown
# CLAUDE.md (Persistent Rules)

## State-First Architecture

**CRITICAL**: Every action you take must be written to persistent state files immediately.
Never rely on conversation memory. Your only source of truth is files in `.claude/state/`.

### On Every Session Start
1. Read `.claude/state/current-phase.txt`
2. Read `.claude/state/checkpoint.json`
3. Read `.claude/state/decisions.md`
4. Read `.claude/state/next-action.txt`
5. Report: "Resuming from [phase], [status]. Next: [action]"

### On Every Action Completion
1. Update `.claude/state/checkpoint.json` with new task status
2. Append new line to `.claude/state/progress.log`
3. Write `.claude/state/next-action.txt` for the next session
4. Commit changes to git with checkpoint message

### What Happens When Context Compacts?
- You lose conversation history
- You still have all state files
- You restart with #3 above (read state files)
- You continue working without repeating anything

## Design Principles
- **No trust in memory**: Everything important is in files
- **Idempotent operations**: Tasks can be safely re-run
- **Append-only logs**: Progress can't be undone, only extended
- **Explicit state**: No guessing about current status
```

**Advantages**:
- Session resets are transparent (new session reads files, continues work)
- Idempotency is built-in
- Human observers can always understand current state by reading files

**Failure Mode It Prevents**: Agent forgets what it did yesterday, repeats work, creates duplicate migrations.

### 3.2 The "Progress Log" Pattern (Append-Only)

**Core Idea**: Maintain an immutable append-only log of all completed actions. Never overwrite; only append.

```
.claude/state/progress.log (APPEND ONLY, never overwrite)

[2026-03-15 10:00:00] STARTED: Database migration project
[2026-03-15 10:30:00] DECISION: Column naming → snake_case
[2026-03-15 10:45:00] DECISION: Blue-green deployment strategy
[2026-03-15 11:00:00] START: User table migration
[2026-03-15 13:45:00] COMPLETE: User table migration (15,847 rows migrated)
[2026-03-15 13:50:00] START: Session table migration
[2026-03-15 14:00:00] NOTE: Index creation in progress, ETA 45min
[2026-03-15 14:32:00] CONTEXT COMPACTION: Lost conversation history, using state files
[2026-03-15 14:33:00] RESUME: Continued session table migration from checkpoint
[2026-03-15 15:00:00] COMPLETE: Session table migration (42,103 rows)
```

**How It Works**:
- Every meaningful event is appended with a timestamp
- Log is complete audit trail
- Recovery: read log to understand everything that happened
- Decision consistency: if you see "DECISION: naming → snake_case", you know that's still the decision

**When an Agent Restarts**:
1. Read progress log from beginning
2. Understand full history of what was done
3. Identify last "COMPLETE" line
4. Resume from there

**Advantages**:
- Impossible to lose history
- Perfect for auditing and compliance
- Natural for replay-based recovery
- Handles context compaction transparently

Reference: [Append Only Log - Agentica](https://agentica.wiki/articles/append-only-log), [Agent Memory & State Management in Production](https://mindra.co/blog/agent-memory-and-state-management-in-production)

### 3.3 The "Resume Protocol"

**Pattern**: First action on EVERY invocation is to check for existing state and resume from checkpoint.

**Implementation**:

```typescript
// Pseudo-code: How an agent might implement this

async function agentInvocation() {
  // STEP 1: Check for existing checkpoint
  const checkpoint = readFile(".claude/state/checkpoint.json");

  if (checkpoint) {
    // STEP 2: Determine resume point
    const lastCompleted = checkpoint.completed_items[checkpoint.completed_items.length - 1];
    const nextTask = checkpoint.task_list.find(t => t.status === "in_progress" || t.status === "pending");

    // STEP 3: Report status (make it visible to observer)
    console.log(`Resuming from checkpoint (${checkpoint.timestamp})`);
    console.log(`Last completed: ${lastCompleted}`);
    console.log(`Next action: ${checkpoint.next_action}`);

    // STEP 4: Resume (don't ask, just continue)
    await resumeFromCheckpoint(checkpoint, nextTask);
  } else {
    // STEP 5: New work (no prior checkpoint)
    console.log("Starting new workflow");
    await startNewWorkflow();
  }
}
```

**Critical Properties**:
- **Automatic**: Don't ask the user; just resume
- **Transparent**: Report what you found and what you're doing
- **Idempotent**: If task is already completed, skip it (don't re-run)
- **Fast**: Load state silently, determine action, execute immediately

**What NOT to Do**:
- Don't present options ("Would you like to continue or restart?")
- Don't ask "where were we?" if the answer is in checkpoint.json
- Don't ignore completed items; mark them as done and move on

Reference: [Checkpointing and Resuming Workflows](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming)

### 3.4 Idempotent Operations

**Core Principle**: Every step must be safe to run multiple times. Idempotency means "running twice = running once".

**Database Migrations**:
```sql
-- GOOD: Idempotent (safe to run multiple times)
CREATE TABLE IF NOT EXISTS users_new (id BIGINT, ...);
INSERT INTO users_new SELECT * FROM users WHERE NOT EXISTS (SELECT 1 FROM users_new WHERE id=users.id);

-- BAD: Not idempotent (fails on second run)
CREATE TABLE users_new (id BIGINT, ...);
INSERT INTO users_new SELECT * FROM users;
```

**File Operations**:
```typescript
// GOOD: Idempotent
const config = readFile("config.json");
config.feature_flag_x = true;
writeFile("config.json", config);  // Safe to run twice; result is the same

// BAD: Not idempotent
appendToFile("config.json", 'feature_flag_x = true');  // Appends every time
```

**Code Refactoring**:
```typescript
// GOOD: Check first, then update
if (!codebase.includes("newImportPath")) {
  updateImports("oldPath", "newPath");
}

// BAD: Always update
updateImports("oldPath", "newPath");  // Fails if already updated
```

**Why It Matters**:
- Agent task is interrupted; task is marked as "in_progress" but not "completed"
- Session resets; new agent loads checkpoint, sees "in_progress", re-runs the task
- If operation is idempotent, no problem (result is correct)
- If operation is not idempotent, you get duplicates, errors, inconsistency

Reference: [Idempotent branch operations](https://github.com/anthropics/claude-code-action/issues/787)

---

## 4. What Teams Building with Claude Code / Cursor / Copilot Do

### 4.1 CLAUDE.md / .cursorrules Files as Persistent Context

**CLAUDE.md** (Claude Code) and **.cursorrules** (Cursor) are the primary mechanism for surviving context compaction.

**Key Principle**: Put rules that must survive compaction into these files.

**Structure**:
```markdown
# CLAUDE.md

## Critical Rules (These survive context compaction)

### State Management
- Read .claude/state/ files on every session start
- Write all decisions to .claude/state/decisions.md immediately
- Never rely on conversation memory for important context

### Architectural Decisions
- Use snake_case for all database columns
- All API endpoints use REST (no GraphQL)
- Frontend uses React hooks, no class components

### Constraints
- Never modify config.prod.yml directly; use environment variables
- All migrations include rollback procedures
- Tests must pass before committing

### Patterns
- Idempotent operations required for all database changes
- File modifications use checksums to detect conflicts
- Git commits include [CHECKPOINT] metadata for recovery

## Session-Specific Instructions
- Focus on: [current task from checkpoint]
- Don't repeat: [list of completed work]
- Watch for: [known failure modes]
```

**Best Practices** (from community):
- Keep under 200 lines (longer files consume more tokens and reduce adherence)
- Use imports/references to .claude/rules/ for large rulesets
- Update CLAUDE.md whenever you discover new architectural patterns
- Include version number so agent understands if rules have changed

Reference: [How Claude remembers your project](https://code.claude.com/docs/en/memory), [Using CLAUDE.MD files](https://claude.com/blog/using-claude-md-files), [Mastering Cursor Rules](https://pockit.tools/blog/mastering-cursor-rules-guide/)

### 4.2 Project-Specific Instruction Files

**Pattern**: Create .claude/rules/ directory with specialized instruction files loaded automatically.

```
.claude/rules/
├── database-migrations.md      # Rules specific to migrations
├── api-design.md               # Rules for API changes
├── testing.md                  # Rules for test coverage
├── security.md                 # Rules for security-sensitive changes
└── deployment.md               # Rules for production deploys
```

**Example: database-migrations.md**
```markdown
# Database Migration Rules

## All Migrations Must Have
- [ ] CREATE TABLE IF NOT EXISTS (idempotent)
- [ ] Rollback procedure (downgrade migration)
- [ ] Schema validation test
- [ ] Performance analysis (index impact)

## Naming Convention
- Table names: plural, snake_case (users, order_items)
- Columns: singular, snake_case (user_id, created_at)
- Indexes: idx_tablename_columns (idx_users_email)

## Pre-Migration Checklist
1. Backup production database
2. Test on staging environment
3. Prepare rollback procedure
4. Document schema changes
5. Get code review approval
```

**Advantages**:
- Specialized rules for different domains
- Rules are only loaded when relevant (file matching)
- Keeps context lean
- Rules are discoverable and maintainable

Reference: [Rules directory architecture](https://www.mintlify.com/VineeTagarwaL-code/claude-code/concepts/memory-context)

### 4.3 State Directories (.claude/, .cursor/)

**Convention**: Use hidden .claude/ or .cursor/ directory for all persistent state.

```
.claude/
├── state/                      # Current workflow state
│   ├── checkpoint.json
│   ├── decisions.md
│   ├── progress.log
│   ├── next-action.txt
│   └── constraints.txt
├── rules/                      # Reusable instruction files
│   ├── database-migrations.md
│   ├── api-design.md
│   ├── testing.md
│   └── security.md
├── memory/                     # Auto-saved learnings
│   ├── build-commands.md
│   ├── debugging-patterns.md
│   └── error-patterns.md
└── .gitignore                  # Exclude checkpoints from VCS if preferred
```

**What to Commit**:
- `.claude/rules/` (permanent rules)
- `.claude/CLAUDE.md` (if project-specific)

**What NOT to Commit** (optional):
- `.claude/state/` (ephemeral checkpoint)
- `.claude/memory/` (auto-generated learning)

**Multi-Agent Coordination**:
For teams using multiple agents simultaneously (Cursor 2.0):
```
.claude/coordination/
├── current-agent-id.txt        # Transient: which agent is working now
├── agent-history.json          # Permanent: log of all agent actions
├── blocked-items.txt           # Shared: work items waiting on each other
└── mutex-locks.json            # Simple coordination: who owns what
```

---

## 5. Failure Modes of Compaction

### 5.1 Repeated Work

**Scenario**: Agent runs schema migration twice.

**Root Cause**: Compaction discards that agent completed "migrate users" earlier.

**Symptom**:
```
Error: Duplicate key on users.email
Schema already has new structure (from first run)
Cannot re-create table that already exists
```

**Prevention**:
- Idempotent operations (CREATE TABLE IF NOT EXISTS)
- Checkpoint with completed_items list
- Resume protocol checks if item is already done

### 5.2 Inconsistent Decisions

**Scenario**:
- Session 1 (early): Agent decides to use snake_case for columns
- Compaction happens
- Session 2 (later): Agent decides to use camelCase for columns
- Result: Codebase has mixed styles, breaking consistency

**Root Cause**: Decision rationale was lost in compaction; agent re-debated question without context.

**Symptom**:
```
Column user_id in one table, userId in another
Inconsistent naming breaks code generation
Tests fail due to unexpected field names
```

**Prevention**:
- Write DECISIONS.md with rationale
- Include decision in every checkout
- Never re-debate decisions without checking state files

### 5.3 Broken Dependencies

**Scenario**:
- Task A: Refactor user model from `User` class to interfaces
- Task B: Update code that imports `User` (depends on A)
- Compaction happens after A, before B
- New session, agent doesn't know B is blocked on A
- Agent tries to do something else, forgets B

**Root Cause**: Dependencies between tasks were only in conversation, not in state files.

**Prevention**:
- Checkpoint.json includes task dependencies
- Resume protocol checks for blocked_by list
- Never forget a task (append-only log)

### 5.4 Constraint Violation

**Scenario**:
- Early in project: Agent says "Never modify config.prod.yml directly"
- This rule was in conversation only
- Compaction happens
- Later: Agent modifies config.prod.yml (the constraint is gone)

**Root Cause**: Constraints were conversational; they got compacted away.

**Symptom**:
```
config.prod.yml file modified in git
Production values leaked to version control
Fails security review
```

**Prevention**:
- Put all constraints in CLAUDE.md (survives compaction)
- Keep constraints.txt in state directory
- Review constraints before every action

Reference: [Multi-tab coordination failure](https://github.com/anthropics/claude-code/issues/32292), [BUG: Skills context lost after compaction](https://github.com/anthropics/claude-code/issues/13919)

### 5.5 Multi-Agent Coordination Failure

**Scenario** (Cursor 2.0 with multiple agents):
- Agent-A: starts migration, marks task as "in_progress"
- Agent-B: doesn't see that task is locked, also starts migration
- Both agents modify the same schema
- Result: Corrupted database state or conflicting changes

**Root Cause**: Agents don't coordinate on shared state; no mutual exclusion.

**Prevention**:
- Idempotent operations (both agents see same end state)
- Shared coordination file that agents check
- One agent per task (no parallel work on same resource)
- If parallelism needed, use event-sourcing (append-only events)

---

## 6. Mitigation Strategies

### 6.1 Write ALL Decisions to Files Immediately

**Never Rely on Memory**: The moment an architectural decision is made, write it to files.

**Implementation**:
```
When you decide: "All API endpoints use REST, no GraphQL"

1. Append to .claude/state/decisions.md:
   - **Decision ID**: api-001
   - **Context**: API architecture choice
   - **Decision**: REST-only, no GraphQL
   - **Rationale**: Simpler for team, works with existing infrastructure
   - **Date**: 2026-03-15 10:30 UTC
   - **Implications**: No GraphQL libraries, no query language

2. Update CLAUDE.md:
   - Add under "Architectural Decisions": "All API endpoints use REST (no GraphQL)"

3. When agent resumes after compaction:
   - Reads decisions.md → sees API-001
   - Reads CLAUDE.md → sees same rule
   - No ambiguity; decision is consistent
```

### 6.2 Include "Decision Rationale" in State Files

**Why**: When agent resumes and sees a decision, it must understand WHY. Otherwise it might debate the decision again.

**Decision Entry Template**:
```json
{
  "decision_id": "db-naming-001",
  "context": "Column naming convention for new schema",
  "decision": "Use snake_case for all columns",
  "rationale": "Consistency with existing legacy schema; matches PostgreSQL conventions; avoids camelCase/PascalCase complexity",
  "alternatives_considered": [
    {
      "option": "camelCase for columns",
      "pros": "Matches JavaScript conventions",
      "cons": "Breaks from existing tables; PostgreSQL suggests snake_case; harder for non-JS developers"
    }
  ],
  "date": "2026-03-15T10:30:00Z",
  "made_by_agent": "primary-agent",
  "implications": [
    "All new migrations must use snake_case",
    "ORM mappings must convert to camelCase in application layer",
    "Code generation tools must support this naming"
  ],
  "status": "final",
  "can_be_revisited": false
}
```

**Agent Behavior**:
When agent reads this, it understands not just the decision, but WHY it was made, and what would need to happen to change it. This prevents re-debating.

### 6.3 Use Timestamps to Detect Stale State

**Problem**: Agent resumes from old checkpoint; has stale data.

**Solution**: Timestamp everything; validate freshness.

```json
{
  "checkpoint_id": "ckpt-2026-03-15-14-32-001",
  "timestamp": "2026-03-15T14:32:45Z",
  "created_at": "2026-03-15T14:32:45Z",
  "last_updated": "2026-03-15T14:32:45Z",
  "expiry": "2026-03-16T14:32:45Z"
}
```

**Agent Logic**:
```
On resuming from checkpoint:
1. Read checkpoint.timestamp
2. Compare to current time
3. If older than N hours, verify still valid
   (Code might have changed; schema might have changed)
4. If questionable, ask for confirmation or re-assess
```

**Use Case**: You pause at 2pm, resume at next day 9am. Schema might have changed. Timestamp forces verification.

### 6.4 Include Checksums/Hashes to Verify File Integrity

**Problem**: You write state assuming files are X; agent resumes, files are Y; state is wrong.

**Solution**: Hash critical files; verify on resume.

```json
{
  "file_state": {
    "src/models/user.ts": {
      "hash": "sha256_abc123def456",
      "size_bytes": 4521,
      "modified": "2026-03-15T13:45:00Z"
    },
    "migrations/001_user_schema.sql": {
      "hash": "sha256_def456ghi789",
      "size_bytes": 2103,
      "modified": "2026-03-15T13:44:00Z"
    }
  }
}
```

**Agent Logic on Resume**:
```
For each file in file_state:
  1. Calculate current hash
  2. Compare to stored hash
  3. If different:
     - File was modified (by human or another agent)
     - Update checkpoint with new hash
     - Report: "src/models/user.ts was modified since last checkpoint"
     - Re-validate assumptions
```

**Use Case**: Prevents agent from assuming schema is "old version" when human already updated it.

---

## 7. Implementation Roadmap

### For Claude Code Projects

**Phase 1: Foundation** (Day 1)
1. Create `.claude/CLAUDE.md` with critical rules
2. Create `.claude/state/` directory
3. Create initial `checkpoint.json` with task list
4. Start appending to `progress.log`

**Phase 2: Resilience** (Days 2-3)
1. Implement resume protocol in your first message to Claude
2. Convert decisions to structured JSON entries
3. Create `constraints.txt` with hard boundaries
4. Test compaction by running `/context` command and verifying state files are still accessible

**Phase 3: Multi-Agent** (If needed)
1. Create `.claude/coordination/` directory
2. Implement simple mutex logic in `blocked-items.txt`
3. Each agent checks coordination before starting task
4. Test with multiple Claude Code windows

### For Cursor Projects

**Same Approach**:
- Use `.cursorrules` instead of CLAUDE.md
- Use same state directory structure
- Leverage Git worktrees for agent isolation (Cursor 2.0+)

### For Long-Running Workflows

**Additional**:
1. Implement scheduled task monitoring
2. Use append-only log as single source of truth
3. Add health checks (verify db state matches checkpoint)
4. Implement automatic recovery (detect and fix inconsistencies)

---

## 8. Key References

### Official Documentation
- [How Claude Code works - Claude Code Docs](https://code.claude.com/docs/en/how-claude-code-works)
- [Context windows - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [File checkpointing - Claude API Docs](https://platform.claude.com/docs/en/agent-sdk/file-checkpointing)
- [Checkpointing - Claude Code Docs](https://code.claude.com/docs/en/checkpointing)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Using CLAUDE.MD files](https://claude.com/blog/using-claude-md-files)
- [Best practices for coding with agents - Cursor](https://cursor.com/blog/agent-best-practices)

### Community Patterns
- [The Architecture of Persistent Memory for Claude Code - DEV Community](https://dev.to/suede/the-architecture-of-persistent-memory-for-claude-code-17d)
- [The Claude Code Memory Crisis - Maisum Hashim](https://www.maisumhashim.com/blog/claude-code-memory-crisis-persistent-context-systems)
- [The 4-Step Protocol That Fixes Claude Code Agent's Context Amnesia - Medium](https://medium.com/@ilyas.ibrahim/the-4-step-protocol-that-fixes-claude-codes-context-amnesia-c3937385561c)
- [Why Claude Loses Context After Compaction - BSWEN](https://docs.bswen.com/blog/2026-02-09-claude-context-loss-compaction/)
- [Mastering Cursor Rules - Pockit](https://pockit.tools/blog/mastering-cursor-rules-guide/)
- [agentic-cursorrules - GitHub](https://github.com/s-smits/agentic-cursorrules)

### Architectural Patterns
- [Stateful Graph Workflows - Agentic Design](https://agentic-design.ai/patterns/workflow-orchestration/stateful-graph-workflows)
- [Filesystem-Based Agent State - Awesome Agentic Patterns](https://agentic-patterns.com/patterns/filesystem-based-agent-state/)
- [Persistence and Checkpointing - LangGraph](https://oboe.com/learn/langgraph-agentic-programming-an3ov3/persistence-and-checkpointing-2)
- [Append Only Log - Agentica](https://agentica.wiki/articles/append-only-log)
- [Agent Memory & State Management in Production - Mindra](https://mindra.co/blog/agent-memory-and-state-management-in-production)
- [Checkpointing and Resuming Workflows - Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming)
- [LangGraph State Management for Multi-Agent Workflows - Medium](https://medium.com/@bharatraj1918/langgraph-state-management-part-1-how-langgraph-manages-state-for-multi-agent-workflows-da64d352c43b)

### Tools & Infrastructure
- [Cursor 2.0: Agent-First Architecture](https://www.digitalapplied.com/blog/cursor-2-0-agent-first-architecture-guide)
- [Subagents - Cursor Docs](https://cursor.com/docs/subagents)
- [How Claude Code Got Better by Protecting More Context](https://hyperdev.matsuoka.com/p/how-claude-code-got-better-by-protecting)
- [Claude Code Context Window Management - MindStudio](https://www.mindstudio.ai/blog/context-window-claude-code-manage-consistent-results)

---

## Conclusion

Context compaction is not a bug to work around; it's a feature to work with. By adopting file-based state patterns—JSON checkpoints, Markdown decisions, append-only logs, and resume protocols—teams can build agentic workflows that are not only resilient to session resets, but actually more transparent and auditable.

**The key insight**: Move all important state OUT of conversation memory and INTO files. Your agent becomes stateless (each session is fresh), but your workflow becomes stateful (all state is persistent on disk).

This mirrors how production systems have worked for decades: separation of concerns between computation (stateless) and storage (persistent). Apply the same principle to your AI agents, and context compaction stops being a problem.

---

## Appendix: Merge Conflict Workflow State Tracking

For AI-assisted merge conflict resolution, maintaining state across context resets is critical to avoid:
- Re-resolving conflicts that were already fixed
- Applying contradictory resolutions (accepting left on first pass, right on second)
- Losing context about semantic intent when merging complex code

### Merge State Checkpoint Example

```json
{
  "version": "1.0",
  "merge_operation": {
    "source_branch": "feature/refactor-auth",
    "target_branch": "main",
    "merge_base": "a1b2c3d4e5f6",
    "merge_initiated_at": "2026-03-15T10:00:00Z",
    "status": "in_progress"
  },
  "conflict_analysis": {
    "total_conflicts": 23,
    "conflicts_resolved": 12,
    "conflicts_pending": 11,
    "conflict_classification": {
      "auto_resolvable": 5,
      "manual_semantic": 4,
      "requires_testing": 2,
      "requires_human_review": 4
    }
  },
  "resolved_conflicts": [
    {
      "file": "src/auth/authenticator.ts",
      "region": "lines 45-78",
      "conflict_type": "import_reorganization",
      "resolution": "accepted_both",
      "resolved_by": "claude_ai",
      "resolved_at": "2026-03-15T10:15:00Z",
      "rationale": "Both sides added new imports; non-overlapping changes",
      "confidence": 95
    },
    {
      "file": "src/auth/session.ts",
      "region": "lines 120-145",
      "conflict_type": "method_signature_change",
      "resolution": "accepted_left",
      "resolved_by": "claude_ai",
      "resolved_at": "2026-03-15T10:30:00Z",
      "rationale": "Left side refactored method signature; right side added old version. Left is correct.",
      "confidence": 88
    }
  ],
  "pending_conflicts": [
    {
      "file": "src/config/defaults.ts",
      "line_range": "10-25",
      "conflict_type": "configuration_value_conflict",
      "our_version": "const MAX_RETRY = 3;",
      "their_version": "const MAX_RETRY = 5;",
      "status": "awaiting_decision",
      "options": [
        {
          "option": "accept_left",
          "rationale": "Conserves resources, aligns with performance constraints"
        },
        {
          "option": "accept_right",
          "rationale": "Improves reliability, aligns with new SLA requirements"
        },
        {
          "option": "custom",
          "rationale": "Use adaptive retry logic based on error type",
          "proposed_resolution": "const MAX_RETRY = error.retryable ? 5 : 3;"
        }
      ]
    }
  ],
  "semantic_decisions": [
    {
      "id": "auth-flow-decision-001",
      "context": "OAuth token refresh handling",
      "decision": "Use automatic refresh on token expiry (rather than explicit refresh calls)",
      "made_at": "2026-03-15T10:05:00Z",
      "affected_files": ["src/auth/token-manager.ts", "src/auth/interceptors.ts"],
      "files_implementing_decision": ["src/auth/token-manager.ts"],
      "files_not_yet_updated": ["src/auth/interceptors.ts"],
      "priority": "high"
    }
  ],
  "test_coverage_gaps": [
    {
      "file": "src/auth/session.ts",
      "change": "Method signature changed from (user: User) to (user: User, options?: SessionOptions)",
      "existing_test": "tests/auth/session.test.ts - 4 tests",
      "status": "needs_updating",
      "risk_level": "high"
    }
  ],
  "deployment_plan": {
    "merge_strategy": "merge_commit",
    "requires_testing": ["integration", "e2e"],
    "rollback_plan": "git reset --hard ORIG_HEAD && git revert <merge_commit>",
    "deployment_window": "scheduled for 2026-03-16T02:00:00Z (low-traffic period)"
  }
}
```

### Key Attributes for Merge Conflict State:

1. **Conflict Classification**: Distinguish auto-resolvable conflicts from those requiring human judgment
2. **Resolution Rationale**: Store *why* each conflict was resolved a certain way (prevents re-deciding)
3. **Confidence Scores**: Flag low-confidence resolutions that might need human review post-merge
4. **Semantic Decisions**: Track architectural/design decisions that span multiple conflicts (prevents inconsistency across files)
5. **Test Coverage**: Flag which tests need updating post-merge
6. **Dependency Tracking**: Note which files depend on the merge result

### Resume Protocol for Merge Workflows

When context resets mid-merge, the checkpoint enables resumption:

```bash
# Read checkpoint to understand current state
cat .merge_state.json | jq '.conflict_analysis'

# Identify conflicts still pending
git ls-files -u | wc -l  # Number of unmerged files
cat .merge_state.json | jq '.pending_conflicts | length'

# Validate that stored state matches current git state
for file in $(cat .merge_state.json | jq -r '.pending_conflicts[].file'); do
  if git ls-files -u | grep -q "$file"; then
    echo "OK: $file still unmerged (state matches)"
  else
    echo "WARNING: $file marked pending but no longer shows as conflicted"
  fi
done

# Resume with context from checkpoint
# No re-analyzing; go directly to next pending conflict
next_conflict=$(cat .merge_state.json | jq -r '.pending_conflicts[0]')
echo "Resuming with: $next_conflict"
```

This checkpoint-based approach ensures that:
1. Previously resolved conflicts are never touched again (eliminating duplicate work)
2. Pending conflicts are addressed consistently (using stored rationale)
3. Semantic decisions are preserved across context boundaries
4. Test coverage gaps are known before final merge
