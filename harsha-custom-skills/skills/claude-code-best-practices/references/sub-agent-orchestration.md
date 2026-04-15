# Sub-Agent Orchestration Guide

How to design, invoke, and coordinate agents in Claude Code.

## Table of Contents
1. Task Tool Invocation
2. Agent Frontmatter Reference
3. Model Selection per Agent
4. Parallel vs Sequential Execution
5. Agent Teams (Experimental)
6. Git Worktree Isolation
7. Agent Memory
8. Delegation Best Practices
9. Common Failures

---

## 1. Task Tool Invocation

Agents are invoked ONLY via the Task tool. Never use bash commands.

```
Task(
  subagent_type="api-developer",
  description="Implement REST endpoints",
  prompt="Create CRUD endpoints for the User model following our API conventions...",
  model="sonnet"
)
```

**Required parameters:**
- `subagent_type` — Agent name (matches `.claude/agents/<name>.md`) or built-in type
- `description` — Short (3-5 words) summary
- `prompt` — Detailed task instructions

**Optional parameters:**
- `model` — Override agent's default model
- `isolation` — `"worktree"` for git worktree isolation
- `max_turns` — Limit agentic turns

**Built-in agent types:**
- `general-purpose` — Full tool access, balanced
- `Explore` — Fast codebase search (Glob, Grep, Read)
- `Plan` — Architecture planning (read-only tools)
- `Bash` — Command execution specialist
- `claude-code-guide` — Claude Code documentation expert

---

## 2. Agent Frontmatter Reference

Complete example with all fields:

```yaml
---
name: deploy-manager
description: Use this agent PROACTIVELY for deployment pipelines and release management
tools: Read, Write, Edit, Bash, Grep, Glob
disallowedTools: NotebookEdit
model: sonnet
permissionMode: acceptEdits
maxTurns: 25
skills:
  - deploy-checklist
  - rollback-procedures
mcpServers:
  - slack
  - name: pagerduty
    command: npx
    args: ["-y", "@pagerduty/mcp-server"]
memory: project
background: false
isolation: worktree
color: blue
---

You are a deployment manager. Follow deploy-checklist skill for pre-flight checks.
Use rollback-procedures if any step fails. Notify via Slack MCP.
```

---

## 3. Model Selection per Agent

Match model intelligence to task complexity:

| Agent Type | Recommended Model | Reasoning |
|---|---|---|
| Orchestrator/dispatcher | `haiku` | Just routes tasks, minimal reasoning |
| File search/exploration | `haiku` or `sonnet` | Pattern matching, not deep analysis |
| Code implementation | `sonnet` | Good balance of speed and quality |
| Code review | `sonnet` or `opus` | Needs nuanced understanding |
| Architecture planning | `opus` | Complex multi-factor reasoning |
| Security analysis | `opus` | Must catch subtle vulnerabilities |
| Test generation | `sonnet` | Systematic but not complex |

---

## 4. Parallel vs Sequential Execution

### Parallel (Multiple Task calls in same turn)

```
# Launch all at once for independent tasks
Task(subagent_type="test-writer", prompt="Write tests for auth module...")
Task(subagent_type="test-writer", prompt="Write tests for payment module...")
Task(subagent_type="doc-generator", prompt="Generate API documentation...")
```

**Use when:** Tasks are independent, no data dependencies, order doesn't matter.
**Combine with:** `isolation: worktree` to prevent file conflicts.

### Sequential (Task results feed into next Task)

```
# Step 1: Plan
result = Task(subagent_type="Plan", prompt="Design the API schema...")
# Step 2: Implement (uses plan output)
Task(subagent_type="api-developer", prompt="Implement the planned schema: {result}")
# Step 3: Test
Task(subagent_type="test-writer", prompt="Write tests for the new API endpoints")
```

**Use when:** Each step depends on the previous result.

---

## 5. Agent Teams (Experimental)

**Status:** Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true`

Agent Teams enable multiple agents working in parallel with direct communication (not just reporting to lead).

**Enable:**
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "true"
  }
}
```

**Key features:**
- Direct agent-to-agent communication
- Shared task list with dependency tracking
- File locking to prevent race conditions
- Display modes: in-process (single terminal) or split panes (tmux/iTerm2)

**Recommended team size:** 3-5 teammates (balances parallelism with coordination overhead)

**Navigation:**
- `Shift+Up/Down` — Navigate between teammates
- `Ctrl+F` (double-press) — Kill all background agents

---

## 6. Git Worktree Isolation

Each agent gets an isolated git worktree, preventing file conflicts during parallel work.

**Configuration:**
```yaml
# In agent frontmatter
isolation: worktree
```

Or via CLI:
```bash
claude --worktree
```

**Cleanup behavior:**
- **No changes:** Worktree and branch automatically removed
- **Changes exist:** Claude prompts to keep or remove
  - Keep: preserves directory and branch for later
  - Remove: deletes worktree, branch, and uncommitted changes

**Hook events (v2.1.49+):**
- `WorktreeCreate` — Fired when worktree created
- `WorktreeRemove` — Fired when worktree removed

**Custom VCS:** Configure these hooks for SVN, Perforce, or Mercurial support.

---

## 7. Agent Memory

Persistent knowledge that survives across sessions. Introduced v2.1.33.

### Three Scopes

| Scope | Path | Git-tracked | Shared | Best For |
|---|---|---|---|---|
| `user` | `~/.claude/agent-memory/<agent>/` | No | No | Cross-project knowledge |
| `project` | `.claude/agent-memory/<agent>/` | Yes | Yes | Team-shared patterns |
| `local` | `.claude/agent-memory-local/<agent>/` | No | No | Personal project-specific |

### How It Works

1. First 200 lines of `MEMORY.md` injected into agent's system prompt at startup
2. Agent reads/writes memory freely via Read, Write, Edit tools
3. If exceeds 200 lines, agent moves details into topic-specific files
4. Topic files load on-demand when agent needs them

### Configuration

```yaml
---
name: code-reviewer
description: Reviews code for quality and patterns
memory: project
---
As you review code, update your memory with recurring patterns.
Before reviewing, check memory for known issues.
```

### Memory structure

```
.claude/agent-memory/code-reviewer/
├── MEMORY.md                  # Primary (first 200 lines injected)
├── react-patterns.md          # Topic: common React issues
├── security-checklist.md      # Topic: security review points
└── performance-tips.md        # Topic: performance patterns found
```

---

## 8. Delegation Best Practices

### Context is King

Every Task invocation creates a FRESH agent instance. Provide complete context:

```
Task(
  subagent_type="api-developer",
  prompt="""
  Create a REST endpoint for user registration.

  Context:
  - Framework: Express.js with TypeScript
  - Database: PostgreSQL via Prisma ORM
  - Auth: JWT tokens stored in httpOnly cookies
  - Validation: Use zod schemas (see src/schemas/)

  Files to reference:
  - src/routes/auth.ts (existing auth patterns)
  - src/schemas/user.ts (user schema)
  - prisma/schema.prisma (database schema)

  Requirements:
  - POST /api/users/register
  - Validate email, password (min 8 chars), name
  - Hash password with bcrypt
  - Return 201 with user object (no password)
  - Return 409 if email exists

  Success criteria:
  - Endpoint handles all edge cases
  - Follows existing code patterns in auth.ts
  - Includes error handling middleware
  """
)
```

### Tool Scoping by Role

| Role | Tools | Rationale |
|---|---|---|
| PM/Analyst | Read, Grep, Glob, WebSearch | Read-only analysis |
| Architect | Read, Grep, Glob, Write (plans only) | Design, not implementation |
| Implementer | Read, Write, Edit, Bash, Grep, Glob | Full coding access |
| Reviewer | Read, Grep, Glob | Analysis without modification |
| Tester | Read, Write, Bash, Grep | Write tests, run them |

---

## 9. Common Failures

### Invocation Failures (Most Common)

| Failure | Cause | Fix |
|---|---|---|
| Agent not triggered | Vague description | Use "PROACTIVELY" + specific context |
| Wrong agent selected | Overlapping descriptions | Make descriptions mutually exclusive |
| Agent has no context | Prompt too brief | Include files, patterns, requirements |
| Agent uses wrong tools | Tool inheritance | Explicit `tools:` whitelist |
| Agent loops forever | No exit criteria | Set `maxTurns` + clear success criteria |

### Architecture Failures

- **Subagents can't spawn subagents:** Flatten to sequential Tasks or use Skills
- **Shell invocation:** `claude agent-name` does NOT work — must use Task tool
- **Context bleeding:** Each agent gets fresh context; don't assume shared state
- **Worktree conflicts:** Without `isolation: worktree`, parallel agents may overwrite files
