---
name: claude-code-best-practices
description: Comprehensive Claude Code best practices covering architecture patterns, CLAUDE.md configuration, context window management, sub-agent orchestration, skills design, hooks system, MCP servers, permissions, cost optimization, and anti-patterns. Use this skill PROACTIVELY whenever setting up a Claude Code project, creating CLAUDE.md files, designing skills or agents, configuring hooks or MCP servers, optimizing context window usage, debugging Claude Code behavior, or reviewing Claude Code configuration. Also trigger when users mention Claude Code architecture, agent teams, worktrees, permissions, sandbox, progressive disclosure, or development workflows like RPI or plan-then-execute.
---

# Claude Code Best Practices

You are a Claude Code architecture expert. This skill provides validated, cross-referenced best practices for building high-quality Claude Code projects — covering architecture, configuration, orchestration, and optimization.

**Source Registry:** This skill synthesizes practices from official Anthropic documentation (docs.claude.com, code.claude.com), the community reference repository (github.com/shanraisshan/claude-code-best-practice), Boris Cherny's recommendations, HumanLayer's ACE framework, and validated community patterns as of March 2026.

---

## Quick Decision Matrix

Before diving into references, use this decision matrix to route your query:

| You Want To... | Read This Reference |
|---|---|
| Set up CLAUDE.md or monorepo config | `references/claude-md-guide.md` |
| Design skills, agents, or commands | `references/architecture-patterns.md` |
| Manage context window / reduce costs | `references/context-and-costs.md` |
| Orchestrate sub-agents or agent teams | `references/sub-agent-orchestration.md` |
| Configure hooks, MCP, or permissions | `references/hooks-mcp-permissions.md` |
| Write better skills (progressive disclosure) | `references/skills-design.md` |
| Avoid common mistakes | `references/anti-patterns.md` |
| Choose a development workflow | `references/workflow-patterns.md` |
| Prepare for PTC, Agent Teams, emerging features | `references/emerging-patterns.md` |

---

## Core Architecture: Command → Agent → Skill

Claude Code uses a three-tier orchestration pattern:

```
User → Command (entry point) → Agent (specialized worker) → Skill (reusable knowledge)
```

**Command** (`.claude/commands/<name>.md`): User-facing entry points invoked via `/command-name`. Handles user interaction, orchestrates the workflow. Use for explicit, repeatable procedures with side effects (commits, deployments, messages).

**Agent** (`.claude/agents/<name>.md`): Specialized workers with custom system prompts, tools, models, and permissions. Invoked ONLY via the Task tool — never via bash. Use when you need different capabilities, isolated context, or parallel delegation.

**Skill** (`.claude/skills/<name>/SKILL.md`): Reusable domain knowledge that Claude auto-discovers based on relevance. Use for expertise, patterns, and routines that should activate contextually.

**Key Rule:** Commands are explicit (user takes the wheel). Skills are discovered (Claude decides relevance). Agents change who does the work and what they can access.

---

## The 10 Golden Rules

These are the highest-impact practices validated across all sources:

1. **Keep CLAUDE.md under 200 lines.** Beyond this, adherence drops. Split with `@imports` or `.claude/rules/` files.

2. **Manual `/compact` at 50% context.** Don't wait for auto-compaction at 95% — that's the "Agent Dumb Zone" where reasoning degrades.

3. **Start every complex task in Plan Mode.** Review and refine the plan before execution. This halves token consumption and doubles quality.

4. **Create feature-specific agents, not role-based ones.** "api-developer" and "frontend-reviewer" outperform generic "QA Engineer" or "Backend Developer" agents.

5. **Use skills for progressive disclosure.** Don't preload everything into CLAUDE.md. Let skills auto-trigger based on context relevance.

6. **Use wildcard permissions over blanket skips.** `Bash(npm run *)` and `Edit(/src/**)` instead of `--dangerously-skip-permissions`.

7. **One focused task per session.** Use `/clear` between unrelated work to prevent context pollution.

8. **Always give Claude a way to verify its work.** Tests, screenshots, type-checking — verification creates 2-3x quality improvement.

9. **Commit immediately after each task completion.** This creates recovery points and feeds git history for future context.

10. **Update Claude Code daily.** The tool updates frequently with significant improvements. Check the changelog.

---

## Settings Hierarchy (Precedence Order)

Understanding scope precedence prevents configuration conflicts:

1. **Managed** (highest) — Organization policies, MDM, `managed-settings.json`
2. **CLI arguments** — Temporary session overrides (`--model`, `--agent`)
3. **Local** — `.claude/settings.local.json` (personal, gitignored)
4. **Project** — `.claude/settings.json` (team-shared, committed)
5. **User** (lowest) — `~/.claude/settings.json` (global personal)

Array settings (permissions, hooks) MERGE across scopes (concatenated, deduplicated). Scalar settings use highest-precedence value.

---

## Known Limitations (March 2026)

Be aware of these documented issues when advising:

| Issue | Status | Impact | Reference |
|---|---|---|---|
| Progressive disclosure loads full skill tokens at startup | GitHub #14882 | Higher token cost than expected | `references/skills-design.md` |
| `context: fork` ignored when skill invoked via Skill tool | GitHub #17283 | Skills run in main context, not forked | `references/architecture-patterns.md` |
| `$CLAUDE_TOOL_INPUT` empty in some hook contexts | GitHub #9567 | Hook scripts can't inspect tool input | `references/hooks-mcp-permissions.md` |
| Tool Search auto mode may not trigger reliably | GitHub #19890 | MCP tool overhead not reduced | `references/context-and-costs.md` |
| Agent Teams experimental | Requires env flag | Not production-stable | `references/sub-agent-orchestration.md` |
| PTC currently API-only (coming to CLI/Cowork/Chat) | Design for it now | ~37% token reduction when it lands | `references/context-and-costs.md` |

---

## Reference Files

| File | Purpose | When to Read |
|---|---|---|
| `references/architecture-patterns.md` | Command/Agent/Skill patterns, decision matrix, examples | Designing project structure |
| `references/claude-md-guide.md` | CLAUDE.md configuration, monorepo loading, @imports, .claude/rules | Setting up or optimizing CLAUDE.md |
| `references/context-and-costs.md` | Context window strategy, model selection, cost optimization | Managing tokens and spending |
| `references/sub-agent-orchestration.md` | Agent frontmatter, Task tool, agent teams, worktrees, memory | Building multi-agent systems |
| `references/skills-design.md` | Skill frontmatter, progressive disclosure, naming, discovery | Creating or improving skills |
| `references/hooks-mcp-permissions.md` | 16 hook events, MCP config, permission wildcards, sandbox | Configuring infrastructure |
| `references/anti-patterns.md` | 12 documented anti-patterns with fixes | Reviewing or debugging setups |
| `references/workflow-patterns.md` | RPI, Plan-Execute, ACE, Ralph Wiggum, CI/CD integration | Choosing development methodology |
| `references/emerging-patterns.md` | PTC, Dynamic Web Filtering, Tool Use Examples, Agent Teams evolution | Future-proofing workflows |
