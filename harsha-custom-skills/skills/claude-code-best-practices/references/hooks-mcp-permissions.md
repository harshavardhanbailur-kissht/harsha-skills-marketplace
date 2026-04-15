# Hooks, MCP Servers, and Permissions

Configuration guide for Claude Code's infrastructure layer.

## Table of Contents
1. Hooks System (16 Events)
2. Hook Handler Types
3. MCP Server Configuration
4. Permissions System
5. Sandbox Mode
6. CLI Flags Reference
7. Known Issues

---

## 1. Hooks System (16 Events)

Hooks run deterministic scripts outside the agentic loop during specific lifecycle events.

| Event | When Fired | Matcher | Can Block |
|---|---|---|---|
| `SessionStart` | Session begins/resumes | No | No |
| `SessionEnd` | Session terminates | No | No |
| `UserPromptSubmit` | User submits prompt | No | No |
| `PreToolUse` | Before tool execution | Yes | Yes (exit 2) |
| `PostToolUse` | After tool succeeds | Yes | No |
| `PostToolUseFailure` | After tool fails | Yes | No |
| `PermissionRequest` | Permission dialog appears | Yes | Yes |
| `Notification` | Notification sent | Yes | No |
| `Stop` | Claude finishes responding | No | No |
| `SubagentStart` | Subagent spawned | Yes | No |
| `SubagentStop` | Subagent finishes | Yes | No |
| `TeammateIdle` | Agent team member going idle | Yes | No |
| `TaskCompleted` | Task marked complete | Yes | No |
| `ConfigChange` | Config file changes mid-session | Yes | No |
| `WorktreeCreate` | Worktree being created (v2.1.49+) | Yes | Yes |
| `WorktreeRemove` | Worktree being removed (v2.1.49+) | Yes | Yes |
| `PreCompact` | Before context compaction | Yes | No |

### Matcher Patterns

```
"Bash"              # Exact match
"Edit|Write"        # Multiple tools (regex OR, no spaces)
"mcp__.*"           # All MCP tools
"mcp__memory__.*"   # Specific MCP server
"*" or ""           # All tools (wildcard)
```

### Exit Codes

| Code | Meaning | Behavior |
|---|---|---|
| 0 | Success | JSON output parsed from stdout |
| 2 | Block | Blocks the operation; stderr fed back to Claude |
| Other | Error | Non-blocking error; stderr shown in verbose mode |

### Environment Variables

| Variable | Availability | Description |
|---|---|---|
| `$CLAUDE_PROJECT_DIR` | All hooks | Current project directory |
| `$CLAUDE_PLUGIN_ROOT` | Plugin hooks | Plugin root directory |
| `$CLAUDE_ENV_FILE` | SessionStart | Path to write `export` statements |
| `$CLAUDE_TOOL_NAME` | Tool hooks | Name of the tool |
| `$CLAUDE_TOOL_INPUT` | Tool hooks | JSON input (⚠️ may be empty — known bug) |
| `$CLAUDE_TOOL_OUTPUT` | PostToolUse | Tool output |

### Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate-command.sh",
            "timeout": 5000,
            "once": true
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/log-changes.sh",
            "timeout": 1000
          }
        ]
      }
    ]
  }
}
```

**Configuration locations (all merge):**
- `~/.claude/settings.json` — User scope
- `.claude/settings.json` — Project scope (committed)
- `.claude/settings.local.json` — Local scope (gitignored)
- Plugin `hooks/hooks.json` — When plugin enabled
- Agent frontmatter `hooks:` field — While agent active

---

## 2. Hook Handler Types

### Command (Default)

```json
{
  "type": "command",
  "command": "./scripts/validate.sh",
  "timeout": 5000,
  "once": true
}
```

### HTTP (v2.1.49+)

```json
{
  "type": "http",
  "url": "https://api.example.com/webhook",
  "timeout": 10000,
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

Environment variable interpolation supported in headers. Control allowed vars with `httpHookAllowedEnvVars` setting.

### Prompt

Sends prompt to Claude model for evaluation:
```json
{
  "type": "prompt",
  "prompt": "Is this bash command safe to execute?"
}
```

### Agent

Spawns a subagent with tool access:
```json
{
  "type": "agent",
  "agent": "security-checker"
}
```

---

## 3. MCP Server Configuration

### Configuration Locations

| Location | Scope | Shared | Use For |
|---|---|---|---|
| `.mcp.json` (project root) | Project | Yes (git) | Team-shared servers |
| `.claude/settings.local.json` | Local | No | Personal servers |
| `~/.claude/settings.json` | User | No | Global servers |
| Agent frontmatter `mcpServers:` | Subagent | N/A | Agent-specific servers |

**Precedence:** Subagent > Project > User

### Transport Types

**stdio** (local process):
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

**http** (remote endpoint):
```json
{
  "mcpServers": {
    "remote-api": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

### Essential MCP Servers (Start Here)

| Server | Purpose | Why |
|---|---|---|
| **Context7** | Up-to-date library docs | Prevents hallucinated APIs |
| **Playwright** | Browser automation | Autonomous UI testing |
| **DeepWiki** | GitHub documentation | Architecture & API surface |

**Community consensus:** Start with 3-5 servers. Each idle server consumes tokens for tool descriptions.

### MCP Permission Controls

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["context7", "playwright"],
  "disabledMcpjsonServers": ["experimental"],
  "permissions": {
    "allow": [
      "mcp__context7__*",
      "mcp__playwright__browser_snapshot"
    ],
    "deny": [
      "mcp__dangerous-server__*"
    ]
  }
}
```

### Tool Search (Auto Mode)

When MCP tool descriptions exceed 10% of context, Tool Search activates automatically:
- Only search-style descriptions loaded initially
- Full tool definitions loaded on-demand
- Saves ~85% of MCP token overhead

```json
{
  "env": {
    "ENABLE_TOOL_SEARCH": "auto:10"
  }
}
```

---

## 4. Permissions System

### Wildcard Syntax

**Bash commands (glob patterns):**
```
Bash(npm run *)          # Any npm run command
Bash(git commit *)       # Git commit with any args
Bash(git * main)         # git checkout main, git merge main
Bash(* --version)        # Any command with --version
Bash(ls *)               # ls with args (NOT lsof)
Bash(ls*)                # ls AND lsof (no space = prefix match)
```

**File paths (gitignore spec):**
```
Read(~/.zshrc)           # Specific file from home
Edit(/src/**/*.ts)       # All .ts files recursively (relative to project root)
Read(//tmp/scratch.txt)  # Absolute path (double slash)
Write(src/**)            # All files under src/
```

**Path prefix meanings:**
- `//path` — Absolute filesystem path
- `~/path` — Home directory
- `/path` — Relative to project root (NOT absolute!)
- `path` or `./path` — Relative to current directory

**MCP tools:**
```
mcp__puppeteer__*                    # All tools from puppeteer server
mcp__context7__resolve_library_id    # Specific tool
```

**Agents:**
```
Agent(Explore)           # Built-in Explore agent
Agent(my-custom-agent)   # Custom agent
```

### Allow/Ask/Deny Hierarchy

Rules evaluated: **deny → ask → allow** (first match wins)

```json
{
  "permissions": {
    "allow": [
      "Edit(*)",
      "Write(*)",
      "Bash(npm run *)",
      "Bash(git *)",
      "mcp__context7__*"
    ],
    "ask": [
      "Bash(rm *)",
      "Bash(git push *)"
    ],
    "deny": [
      "Read(.env)",
      "Read(./secrets/**)"
    ],
    "additionalDirectories": ["../shared-libs/"]
  }
}
```

### Permission Modes

| Mode | Behavior |
|---|---|
| `default` | Prompts on first use of each tool |
| `acceptEdits` | Auto-accepts file edit permissions |
| `plan` | Read-only analysis, no modifications |
| `dontAsk` | Auto-denies unless pre-approved |
| `bypassPermissions` | Skips all prompts (requires safe environment) |

---

## 5. Sandbox Mode

OS-level isolation for Bash commands. Enable via `/sandbox` command.

### File Isolation

- **Default:** Read/write in current directory and subdirectories
- **Configurable:**

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "filesystem": {
      "allowWrite": ["./src/", "./tests/"],
      "denyWrite": ["./config/", "./.env"],
      "denyRead": ["~/.ssh/", "~/.aws/"]
    },
    "network": {
      "allowedDomains": ["api.github.com", "registry.npmjs.org"],
      "allowLocalBinding": true
    }
  }
}
```

### OS-Level Enforcement

- **macOS:** Seatbelt framework (out-of-box)
- **Linux/WSL2:** Bubblewrap isolation
- **WSL1:** NOT supported (requires WSL2+)

### Auto-Allow Behavior

When `autoAllowBashIfSandboxed: true`:
- Bash commands that can be sandboxed execute WITHOUT permission prompts
- Commands that can't be sandboxed (e.g., non-allowed network) fall back to regular permission flow
- Works independently of permission mode

---

## 6. CLI Flags Reference (Most Useful)

### Session Management
```bash
claude                          # Start interactive session
claude "query"                  # Start with initial prompt
claude -p "query"               # Print mode (non-interactive)
claude -c                       # Continue most recent conversation
claude -r "session" "query"     # Resume specific session
claude --worktree               # Start in isolated git worktree
```

### Model & Agent
```bash
claude --model opus             # Override model
claude --agent my-agent         # Use specific agent
claude --permission-mode plan   # Start in plan mode
```

### Permissions & Tools
```bash
claude --allowedTools "Bash(npm *),Edit(*)"
claude --disallowedTools "NotebookEdit"
```

### System Prompt
```bash
claude --system-prompt "Custom prompt"        # Replace entire prompt
claude --append-system-prompt "Extra rules"   # Append to default
```

### Automation (Print Mode)
```bash
claude -p "query" --output-format json
claude -p "query" --max-turns 10
claude -p "query" --max-budget-usd 5.00
claude -p "query" --json-schema '{"type":"object",...}'
```

---

## 7. Known Issues

| Issue | Workaround |
|---|---|
| `$CLAUDE_TOOL_INPUT` empty in hooks (GitHub #9567) | Parse tool info from other env vars |
| `CLAUDE_ENV_FILE` empty in SessionStart (GitHub #15840) | Use alternative env setup |
| Hook env var docs contradictory (GitHub #19357) | Test behavior in your environment |
| HTTP hooks require explicit URL allowlisting | Add to `allowedHttpHookUrls` |
