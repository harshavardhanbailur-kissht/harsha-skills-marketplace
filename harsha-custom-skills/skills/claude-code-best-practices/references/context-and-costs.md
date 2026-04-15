# Context Window Management & Cost Optimization

Strategies for managing Claude Code's 200K token context window and minimizing costs.

## Table of Contents
1. Context Window Anatomy
2. The Agent Dumb Zone
3. Compaction Strategy
4. Model Selection (80/20 Rule)
5. Cost Reduction Techniques
6. Token Budget Monitoring
7. Extended Thinking Configuration
8. Known Limitations

---

## 1. Context Window Anatomy

Claude Code operates within a 200K token context window. Here's what consumes it:

| Component | Typical Tokens | Can Control? |
|---|---|---|
| System prompt (base) | ~269 | No |
| Tool instructions | 500-2,000 | Partially (disallowedTools) |
| CLAUDE.md + rules | 1,000-5,000 | Yes — keep lean |
| MCP tool descriptions | 100-500 per tool | Yes — use Tool Search |
| Skill descriptions | ~100-200 each | Yes — limit skills |
| Conversation history | Grows over time | Yes — compact/clear |
| File contents (Read) | Varies | Yes — read selectively |
| Extended thinking | Up to 31,999 | Yes — adjust budget |

**The key insight:** Everything above the conversation competes for space. A 5,000-token CLAUDE.md + 15 MCP servers + 10 skills can consume 15-20% of context before you type anything.

---

## 2. The Agent Dumb Zone

Auto-compaction triggers at ~95% context capacity by default. When Claude operates near this threshold:

- Reasoning quality degrades significantly
- Claude "forgets" earlier instructions and context
- Output becomes repetitive or contradictory
- Tool usage becomes less strategic

**Prevention:** Manual `/compact` at 50% usage. This preserves more context for meaningful work.

**How to check:** Use `/context` command to visualize token usage as a grid.

---

## 3. Compaction Strategy

### Manual Compaction

Run `/compact` proactively at ~50% context usage. Optionally provide focus:

```
/compact Focus on the API refactoring discussion
```

This tells the compaction algorithm what to prioritize retaining.

### Environment Override

```bash
# Set auto-compact threshold to 50% (default is ~95%)
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 claude
```

Or in settings.json:
```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"
  }
}
```

### Session Management

- `/clear` — Start fresh (lose all context). Use between unrelated tasks.
- `/compact` — Summarize and compress. Use mid-session to extend productive life.
- New session — Each `/command` invocation or new terminal starts fresh.

**Rule of thumb:** One focused task per session. If the task changes direction significantly, `/clear` and start fresh with a better prompt.

---

## 4. Model Selection (80/20 Rule)

Strategic model selection saves 40-60% on costs:

| Model | Best For | Cost Profile |
|---|---|---|
| **Haiku** | Simple orchestration, commands, quick lookups | ~$0.80/M input |
| **Sonnet** | Standard coding, agent work, most tasks (80% of work) | ~$3/M input |
| **Opus** | Complex reasoning, architecture decisions, code review (20%) | ~$15/M input |

**Practical strategy:**
1. Start every session on Sonnet (default)
2. Switch to Opus only for deep analysis, complex refactoring, or critical review
3. Use Haiku for orchestrator commands that just dispatch to agents
4. Set per-agent models: `model: haiku` for simple agents, `model: opus` for complex ones

**Settings:**
```json
{
  "model": "sonnet"
}
```

Switch mid-session: `/model opus` or `/model haiku`

---

## 5. Cost Reduction Techniques

### Quick Wins (Immediate Impact)

1. **Specific requests:** "Add input validation to the login function in auth.ts" uses far fewer tokens than "review my authentication code"
2. **Use `/clear` between tasks:** Prevents context pollution from unrelated work
3. **Plan mode:** Halves token consumption for analysis phases
4. **`.claudeignore` file:** Like .gitignore, reduces file reading tokens by ~25% on standard projects

### Configuration Optimizations

```json
{
  "env": {
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "ENABLE_TOOL_SEARCH": "auto:10",
    "BASH_MAX_OUTPUT_LENGTH": "5000"
  }
}
```

- `ENABLE_TOOL_SEARCH`: Defers MCP tool descriptions when they exceed N% of context (default: 10%)
- `BASH_MAX_OUTPUT_LENGTH`: Truncates bash output to prevent token floods

### Architectural Savings

- **Fewer MCP servers:** Start with 3-5 essential servers, not 15+. Each idle server still consumes tokens for tool descriptions.
- **Skills over CLAUDE.md:** Move domain knowledge from CLAUDE.md to skills. Skills load description-only (~100 tokens) until needed; CLAUDE.md loads fully every session.
- **Feature-specific agents:** Small, focused agents use less context per task than one large general agent.
- **Sandbox mode:** Reduces permission prompts (which consume tokens for each approval interaction).

### MCP Tool Search

When tool descriptions exceed 10% of context, Tool Search activates:
- Only search-style tool descriptions loaded initially
- Full tool definitions loaded on-demand when needed
- Saves ~85% of MCP token overhead

**Manual override:**
```json
{
  "env": {
    "ENABLE_TOOL_SEARCH": "auto:5"
  }
}
```

---

## 6. Token Budget Monitoring

### Commands

| Command | What It Shows |
|---|---|
| `/context` | Visual grid of token usage |
| `/cost` | Detailed session spending (API users) |
| `/usage` | Plan limits and rate limits |

### Status Line Plugin

Custom status line shows real-time context/cost:

```json
{
  "statusLine": {
    "command": "echo \"Tokens: $(cat /tmp/claude-context 2>/dev/null || echo 'N/A')\"",
    "interval": 10
  }
}
```

### Budget Limits (Print Mode)

For automation/CI, set hard limits:

```bash
claude -p "review this PR" --max-budget-usd 5.00
```

---

## 7. Extended Thinking Configuration

Extended thinking (enabled by default) uses a 31,999 token budget. Thinking tokens are billed as output tokens (more expensive).

**Reduce for simple tasks:**
- Lower the thinking budget for routine work
- Disable entirely for simple lookups

**Keep high for:**
- Complex architectural decisions
- Multi-step reasoning problems
- Security review and code analysis

```json
{
  "alwaysThinkingEnabled": true
}
```

---

## 8. Known Limitations

- **Programmatic Tool Calling (PTC):** Currently API-only (Opus 4.6, Sonnet 4.6) as of March 2026, but expected to land in Claude Code, Cowork, and Chat. PTC lets Claude write Python to orchestrate multiple tools in a single inference pass — yielding ~37% token reduction and enabling batch processing, early termination, and data filtering before context. **Design workflows that will benefit from PTC now** (multi-tool sequences, batch operations, data pipelines) so you're ready when it ships. Current API capabilities: no MCP tools, no web tools, ~4.5min container lifetime. See `references/emerging-patterns.md` for PTC architecture patterns.
- **Tool Search auto mode:** May not trigger reliably despite exceeding threshold (GitHub #19890). Monitor with `/context`.
- **Progressive disclosure incomplete:** Skills currently load full token count at startup, not true 3-level lazy loading (GitHub #14882). Budget accordingly.
- **No deterministic output:** Even with `temperature=0`, outputs vary due to floating-point arithmetic, MoE routing, and infrastructure differences. Design systems robust to variation.
