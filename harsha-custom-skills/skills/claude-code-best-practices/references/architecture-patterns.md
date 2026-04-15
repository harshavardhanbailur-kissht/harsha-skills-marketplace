# Architecture Patterns: Commands, Agents, and Skills

This reference covers the three-tier Claude Code architecture and when to use each component.

## Table of Contents
1. Commands
2. Agents (Sub-Agents)
3. Skills
4. Decision Matrix
5. Orchestration Examples
6. String Substitutions
7. Known Issues

---

## 1. Commands

**Location:** `.claude/commands/<name>.md`
**Invocation:** `/command-name` (user-initiated only)
**Purpose:** Explicit, repeatable workflows with defined steps

### Frontmatter Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | What the command does (shown in `/` menu) |
| `argument-hint` | string | Autocomplete hint (e.g., `[issue-number]`) |
| `allowed-tools` | string | Tools allowed without permission prompts |
| `model` | string | Model to use (`haiku`, `sonnet`, `opus`) |

### When to Use Commands

- Multi-step procedures you run frequently (code review, deploy, PR creation)
- Workflows with side effects (git commits, Slack messages, file generation)
- Standard prompts with variable inputs
- Explicit user-initiated actions (user takes the wheel)

### Example: Code Review Command

```yaml
# .claude/commands/review.md
---
description: Review code changes against project standards
argument-hint: [file-or-branch]
allowed-tools: Read, Grep, Glob
model: sonnet
---

Review the code at $ARGUMENTS against the project coding standards.
Focus on: correctness, readability, test coverage, security.
Output a structured review with severity levels.
```

---

## 2. Agents (Sub-Agents)

**Location:** `.claude/agents/<name>.md`
**Invocation:** ONLY via `Task(subagent_type="agent-name", ...)` — never via bash
**Purpose:** Specialized workers with isolated context, tools, and models

### Frontmatter Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | required | Unique identifier (lowercase, hyphens) |
| `description` | string | required | When to invoke — use "PROACTIVELY" for auto-delegation |
| `tools` | list | inherits all | Comma-separated allowlist |
| `disallowedTools` | list | none | Tools to deny |
| `model` | string | inherit | `haiku`, `sonnet`, `opus`, `inherit` |
| `permissionMode` | string | default | `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions` |
| `maxTurns` | integer | unlimited | Max agentic turns before stopping |
| `skills` | list | none | Skills to preload (full content injected at startup) |
| `mcpServers` | list | none | MCP servers for this agent |
| `hooks` | object | none | PreToolUse, PostToolUse, Stop hooks |
| `memory` | string | none | Persistent memory scope: `user`, `project`, `local` |
| `background` | boolean | false | Always run as background task |
| `isolation` | string | none | `"worktree"` for git worktree isolation |
| `color` | string | none | CLI output color (green, magenta, blue, etc.) |

### When to Use Agents

- Different capability profiles needed (PM reads docs, Implementer writes code)
- Parallel work requiring isolation (use worktrees)
- Tasks needing restricted tool access
- Long-running background work
- Custom system prompts per role

### Agent Design Principles

**Feature-specific, not role-based:**
- ✅ `api-developer`, `frontend-reviewer`, `test-writer`, `deploy-manager`
- ❌ `QA Engineer`, `Backend Developer`, `Senior Architect`

**Clear descriptions enable auto-delegation:**
```yaml
# Good — specific and actionable
description: Use this agent PROACTIVELY when creating or modifying REST API endpoints

# Bad — vague, Claude won't know when to invoke
description: Helps with backend tasks
```

**Explicit tool whitelisting:**
```yaml
# Start from deny-all, add what's needed
tools: Read, Grep, Glob, Edit, Write, Bash
disallowedTools: NotebookEdit
```

---

## 3. Skills

**Location:** `.claude/skills/<name>/SKILL.md`
**Invocation:** Auto-discovered by Claude based on description, or manual `/skill-name`
**Purpose:** Reusable domain knowledge and expertise

### Frontmatter Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Display name & slash command (defaults to directory name) |
| `description` | string (max 1024 chars) | What skill does — primary auto-discovery mechanism |
| `argument-hint` | string | Autocomplete hint |
| `disable-model-invocation` | boolean | Prevent Claude from auto-invoking (use for /commit, /deploy) |
| `user-invocable` | boolean | Hide from `/` menu (background knowledge only) |
| `allowed-tools` | string | Tools allowed without permission prompts when skill active |
| `model` | string | Model to use when skill runs |
| `context` | string | `fork` for isolated subagent context |
| `agent` | string | Subagent type when `context: fork` |
| `hooks` | object | Lifecycle hooks |

### When to Use Skills

- Specialized domain knowledge that should activate contextually
- Patterns and routines Claude should discover automatically
- Background knowledge for agents (via `skills:` field in agent frontmatter)
- Reusable expertise across projects

### Priority Resolution (Name Conflicts)

1. **Enterprise** (highest) — Organization-wide managed settings
2. **Personal** (`~/.claude/skills/`) — All projects
3. **Project** (`.claude/skills/`) — This project only
4. **Plugin** — Namespaced with `plugin-name:skill-name`

### Key Distinctions

| | `disable-model-invocation: true` | `user-invocable: false` |
|---|---|---|
| **Effect** | Blocks Skill tool invocation entirely | Hides from `/` menu only |
| **Use For** | Dangerous operations (/deploy, /send-message) | Agent-only background knowledge |
| **Can Claude invoke?** | No | Yes (via Skill tool) |

---

## 4. Decision Matrix

| Scenario | Use | Why |
|---|---|---|
| "Run my deploy checklist" | **Command** | Explicit, user-initiated, has side effects |
| "Know our API conventions" | **Skill** | Background knowledge, auto-discovered |
| "Write tests in parallel" | **Agent** | Needs isolated context, different tools |
| "Format commit messages" | **Skill** | Pattern/convention, discovered contextually |
| "Review PR + post comments" | **Command** | Multi-step, explicit workflow, side effects |
| "Parse weather data for SVG" | **Agent + Skill** | Agent fetches data, skill has domain knowledge |
| "Apply security headers" | **Skill** | Domain expertise, auto-triggered |

---

## 5. Orchestration Examples

### Weather Orchestrator (Command → Agent → Skill)

```yaml
# .claude/commands/weather-orchestrator.md
---
description: Fetch weather and create SVG card
model: haiku
---
1. Ask user for temperature unit
2. Use Task tool to invoke weather-agent
3. Use Skill tool to invoke weather-svg-creator
```

```yaml
# .claude/agents/weather-agent.md
---
name: weather-agent
description: Use this agent PROACTIVELY when you need to fetch weather data
tools: WebFetch, Read
model: sonnet
skills:
  - weather-fetcher
---
Fetch weather data using the weather-fetcher skill patterns.
```

```yaml
# .claude/skills/weather-fetcher/SKILL.md
---
name: weather-fetcher
description: Fetch weather from wttr.in API
user-invocable: false
---
Fetch current temperature using WebFetch to wttr.in API.
```

### Deploy Pipeline (Command → Sequential Agents)

```yaml
# .claude/commands/deploy.md
---
description: Run deploy pipeline with validation
allowed-tools: Bash, Read, Task
model: sonnet
---
1. Task(subagent_type="test-runner", prompt="Run full test suite")
2. If tests pass: Task(subagent_type="deploy-agent", prompt="Deploy to staging")
3. Task(subagent_type="health-checker", prompt="Verify staging health")
```

---

## 6. String Substitutions

Available in commands and skills:

| Variable | Purpose | Example |
|---|---|---|
| `$ARGUMENTS` | All arguments passed | `/review src/api.ts` → `src/api.ts` |
| `$N` / `$ARGUMENTS[N]` | Nth argument (0-based) | `$0` = first argument |
| `${CLAUDE_SESSION_ID}` | Current session ID | For logging, file naming |
| `` !`command` `` | Dynamic context (shell output injected before prompt) | `` !`git status` `` |

**Shell substitution runs BEFORE Claude sees the prompt.** Use for injecting dynamic context like git status, file lists, or environment info.

**Error handling:** Use fallbacks: `` !`git status 2>/dev/null || echo "Not a git repository"` ``

---

## 7. Known Issues (March 2026)

- **`context: fork` ignored:** When skills invoked via Skill tool, `context: fork` and `agent:` fields are ignored — skill runs in main context instead (GitHub #17283)
- **Subagents can't spawn subagents:** Use Skills or sequential chaining for multi-level delegation
- **Auto-delegation unreliable:** Claude often ignores appropriate sub-agents unless explicitly named; use "PROACTIVELY" in descriptions and be specific
- **Task tool only:** Shell commands (`claude agent-name`) will NOT trigger agents
