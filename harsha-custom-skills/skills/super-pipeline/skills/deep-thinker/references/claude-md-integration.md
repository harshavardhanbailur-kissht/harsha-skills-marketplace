# CLAUDE.md Integration Reference

How the deep-thinker skill integrates with CLAUDE.md project configuration.

## Table of Contents
- [Understanding CLAUDE.md](#understanding-claudemd)
- [Memory Hierarchy](#memory-hierarchy)
- [Deep-Thinker + CLAUDE.md](#deep-thinker--claudemd)
- [Template Patterns](#template-patterns)
- [MCP Server Integration](#mcp-server-integration)

---

## Understanding CLAUDE.md

CLAUDE.md is Claude Code's persistent memory system—a configuration file that loads into every conversation automatically.

### Key Characteristics

| Aspect | Behavior |
|--------|----------|
| **Loading** | Automatically loaded at session start |
| **Persistence** | Survives context compaction |
| **Scope** | Project-wide instructions |
| **Priority** | High (near system prompt level) |

### What CLAUDE.md Is For

✅ **Good uses**:
- Project conventions (naming, style)
- Key directories and architecture
- Common commands (build, test, deploy)
- Tech stack summary
- Important constraints

❌ **Not for**:
- Detailed procedures (use Skills)
- Large reference docs (use Skills/references)
- Deep analysis output (use .deep-think/)
- Implementation plans (use .deep-think/IMPLEMENTATION.md)

---

## Memory Hierarchy

Claude Code has a priority-ordered memory system:

```
Priority 1: Enterprise CLAUDE.md
  └── /Library/Application Support/ClaudeCode/CLAUDE.md (macOS)
  └── /etc/claude-code/CLAUDE.md (Linux)

Priority 2: User CLAUDE.md
  └── ~/.claude/CLAUDE.md

Priority 3: Project CLAUDE.md
  └── ./CLAUDE.md
  └── ./.claude/CLAUDE.md

Priority 4: Local Overrides
  └── ./CLAUDE.local.md (gitignored, personal)

Priority 5: Subtree CLAUDE.md
  └── ./src/CLAUDE.md (loaded when reading src/)
```

### Loading Behavior

- All levels load and merge
- Higher priority wins on conflicts
- Subtree files load dynamically when Claude reads those directories
- Local files for personal preferences (not committed)

---

## Deep-Thinker + CLAUDE.md

The deep-thinker skill complements CLAUDE.md—they serve different purposes.

### Separation of Concerns

| Aspect | CLAUDE.md | Deep-Thinker Output |
|--------|-----------|---------------------|
| Scope | Project conventions | Analysis & implementation plans |
| Persistence | Permanent | Per-feature analysis |
| Contents | How to work | What to build & why |
| Updates | Rare | Created per feature |

### Recommended CLAUDE.md for Deep-Thinker Projects

```markdown
# Project: {{PROJECT_NAME}}

## Overview
{{One-sentence project description}}

## Key Directories
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `.deep-think/` - Analysis output (created per feature)

## Tech Stack
- Frontend: {{tech}}
- Backend: {{tech}}
- Database: {{tech}}

## Commands
```bash
npm run dev      # Start development
npm run build    # Build for production
npm run test     # Run tests
```

## Conventions
- TypeScript strict mode
- Prettier for formatting
- Conventional commits

## Deep-Thinker Skill
This project uses the deep-thinker skill for comprehensive analysis.
- Analysis output: `.deep-think/` directory
- For executor: Read `.deep-think/EXECUTION_CHECKLIST.md`
- Analysis files are REFERENCE ONLY - do not execute from CLAUDE.md

## Additional Context
- Architecture: @docs/architecture.md
- API: @docs/api.md
```

### What NOT to Put in CLAUDE.md

```markdown
# DON'T DO THIS

## Current Analysis
- Login redesign analysis  ← This belongs in .deep-think/OVERVIEW.md
- Mobile auth edge cases

## Design Decisions
- Decided to use tabs for auth ← This belongs in .deep-think/ARCHITECTURE.md
- Selected phone + email approach
```

---

## Template Patterns

### Minimal CLAUDE.md

For simple projects:

```markdown
# Project Name

Brief description.

## Tech Stack
{{Stack}}

## Commands
{{Key commands}}
```

### Standard CLAUDE.md

For most projects:

```markdown
# {{Project Name}}

{{Description}}

## Key Directories
| Directory | Purpose |
|-----------|---------|
| `src/` | Source code |
| `tests/` | Tests |

## Tech Stack
- {{Category}}: {{Technology}}

## Commands
```bash
{{command}} # {{description}}
```

## Conventions
- {{Convention 1}}
- {{Convention 2}}

## Additional Context
- @docs/architecture.md
- @docs/api.md
```

### Deep-Thinker-Aware CLAUDE.md

For projects using the deep-thinker skill:

```markdown
# {{Project Name}}

{{Description}}

## Quick Start for Executor
1. Check `.deep-think/OVERVIEW.md` for analysis goals
2. Read `.deep-think/EXECUTION_CHECKLIST.md` for steps
3. Implement following the checklist

## Directories
- `src/` - Source code
- `.deep-think/` - Analysis output (per feature)

## Tech Stack
{{Stack}}

## Commands
{{Commands}}

## Conventions
{{Conventions}}

## Deep-Thinker Output Structure
- `OVERVIEW.md` - Goals, scope, success criteria
- `CURRENT_STATE.md` - Existing code analysis
- `ARCHITECTURE.md` - Design decisions with rationale
- `IMPLEMENTATION.md` - Micro-level implementation steps
- `EDGE_CASES.md` - All scenarios documented
- `EXECUTION_CHECKLIST.md` - For executor session

## Domain Skills Available
- `deep-thinker` - Comprehensive analysis before implementation
- `ui-ux-mastery-modular` - UI/UX design patterns

## Context
@docs/architecture.md
@docs/api.md
```

### Import Syntax

Use `@path` to reference detailed docs without bloating CLAUDE.md:

```markdown
## API Documentation
@docs/api/authentication.md
@docs/api/users.md
@docs/api/products.md
```

Claude reads these on demand, not upfront.

---

## MCP Server Integration

### Understanding MCP vs Skills

| Component | Purpose | Integration |
|-----------|---------|-------------|
| **MCP Servers** | External connectivity | Tool definitions |
| **Skills** | Domain expertise | Procedural knowledge |
| **CLAUDE.md** | Project config | Always-on context |
| **Deep-Thinker** | Analysis output | File-based persistence |

### MCP Servers for Deep Analysis

If you have MCP servers available:

```markdown
# In CLAUDE.md

## Connected Services (MCP)
- **Notion**: Project docs via mcp-notion
- **GitHub**: Code management via mcp-github

## Deep-Thinker + MCP Workflow
1. Deep-thinker creates comprehensive analysis
2. MCP can sync analysis to external docs (optional)
3. Executor session implements from .deep-think/
```

### MCP Server Recommendations

| Server | Use Case |
|--------|----------|
| `atlas-mcp-server` | Project/task management |
| `mcp-notion` | Documentation sync |
| `mcp-linear` | Issue tracking |
| `mcp-github` | PR/issue management |
| `mcp-filesystem` | File operations |

### Claude Max Constraints

For Claude Max users (no API):

- MCP works via Claude Desktop (stdio transport)
- Configure in `claude_desktop_config.json`
- Remote MCP via Settings → Connectors
- Skills work everywhere (file-based)

---

## Configuration Best Practices

### 1. Keep CLAUDE.md Under 100 Lines

LLMs follow ~150-200 instructions reliably. CLAUDE.md competes with system prompt.

### 2. Use Progressive Disclosure

```markdown
## API
Basic auth: Bearer token

For full API docs: @docs/api/README.md
```

### 3. Version Control CLAUDE.md

- Commit CLAUDE.md to repo
- Use CLAUDE.local.md for personal preferences
- Add CLAUDE.local.md to .gitignore

### 4. Update CLAUDE.md Rarely

- Project conventions change slowly
- Task state changes frequently
- Don't mix the two

### 5. Test CLAUDE.md Effectiveness

Ask Claude:
- "What's our coding style?"
- "How do I run tests?"
- "What's the project architecture?"

If Claude can't answer from CLAUDE.md, improve it.

---

## Troubleshooting

### CLAUDE.md Not Loading

Check file location:
```bash
# Should be at project root
ls -la CLAUDE.md
# Or in .claude directory
ls -la .claude/CLAUDE.md
```

### Conflicting Instructions

If CLAUDE.md conflicts with deep-thinker output:
- CLAUDE.md = project conventions (stable)
- Deep-thinker = analysis output (per-feature)
- Deep-thinker follows CLAUDE.md conventions

### Too Much Context

If CLAUDE.md is too large:
1. Move details to referenced files (@path)
2. Use subtree CLAUDE.md for module-specific rules
3. Consider Skills for procedural knowledge

### CLAUDE.md vs Skill vs .deep-think/ Confusion

| If it's about... | Put it in... |
|------------------|--------------|
| Project naming conventions | CLAUDE.md |
| How to analyze deeply | Skill (references/) |
| Build commands | CLAUDE.md |
| Self-review process | Skill (references/) |
| Tech stack | CLAUDE.md |
| Feature-specific analysis | .deep-think/
| Implementation steps | .deep-think/IMPLEMENTATION.md |
| Design decisions for feature | .deep-think/ARCHITECTURE.md |
