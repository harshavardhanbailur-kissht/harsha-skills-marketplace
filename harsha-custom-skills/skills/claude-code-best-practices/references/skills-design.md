# Skills Design Guide

How to design, structure, and optimize Claude Code skills for maximum effectiveness.

## Table of Contents
1. Skill Anatomy
2. Progressive Disclosure Pattern
3. Writing Effective Descriptions
4. SKILL.md Body Guidelines
5. Bundled Resources
6. Agent Skills (Preloaded)
7. Plugins
8. Testing Skills
9. Known Issues

---

## 1. Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    — Executable code for deterministic tasks
    ├── references/ — Docs loaded into context as needed
    └── assets/     — Templates, icons, fonts used in output
```

### Naming Rules

- Name: 1-64 characters, lowercase, hyphens only
- Must match directory name
- Becomes the slash command: `/skill-name`

---

## 2. Progressive Disclosure Pattern

Skills use a three-level loading system to minimize token consumption:

| Level | What Loads | When | Token Impact |
|---|---|---|---|
| **1. Metadata** | Name + description | Always at startup | ~100-200 tokens each |
| **2. SKILL.md body** | Full instructions | When skill triggers | Variable (target <500 lines) |
| **3. Bundled resources** | Reference files, scripts | On-demand within skill | Unlimited (loaded as needed) |

### Design for Progressive Disclosure

```yaml
# SKILL.md — Level 2 (loaded on trigger)
---
name: api-security
description: API security patterns for Express.js and FastAPI applications
---

# API Security Patterns

Quick reference for securing API endpoints.

## Decision Matrix
| Framework | Read This Reference |
|---|---|
| Express.js | `references/express-security.md` |
| FastAPI | `references/fastapi-security.md` |
| General | `references/owasp-api-top10.md` |
```

The SKILL.md routes to the right reference file. Only the relevant reference loads into context.

### Token Budget Reality

**⚠️ Known Issue (GitHub #14882):** As of March 2026, skills currently consume their full token count at startup, not true 3-level lazy loading. Budget accordingly:

- Skill descriptions: 2% of context window
- With 10 skills: ~2,000 tokens for descriptions alone
- SKILL.md bodies add significantly when triggered

**Mitigation:** Keep SKILL.md under 500 lines. Move detailed content to `references/` files.

---

## 3. Writing Effective Descriptions

The description is the PRIMARY auto-discovery mechanism. Claude reads all descriptions and decides which skills are relevant.

### Good Descriptions

```yaml
# Specific, with trigger contexts
description: >
  API security patterns for Express.js and FastAPI. Use PROACTIVELY when
  creating API endpoints, adding authentication, configuring CORS,
  implementing rate limiting, or reviewing API security.
```

```yaml
# Lists concrete trigger scenarios
description: >
  Comprehensive database migration guide for Prisma ORM. Triggers when
  creating migrations, modifying schemas, handling data migrations,
  resolving migration conflicts, or setting up Prisma in new projects.
```

### Bad Descriptions

```yaml
# Too vague — Claude won't know when to trigger
description: Helps with security stuff

# Too narrow — misses valid trigger scenarios
description: Reviews SQL injection in Express routes
```

### Description Rules

- Max 1024 characters
- No XML tags
- Include both WHAT the skill does AND WHEN to use it
- Use "PROACTIVELY" to encourage auto-invocation
- Be slightly "pushy" — Claude under-triggers rather than over-triggers
- List specific keywords users might mention

---

## 4. SKILL.md Body Guidelines

### Size Targets

| Size | Recommendation |
|---|---|
| Under 200 lines | Ideal — full content in SKILL.md |
| 200-500 lines | Acceptable — use clear structure |
| Over 500 lines | Split into references/ files with routing table |

### Writing Style

- Use imperative form ("Run the tests", not "You should run the tests")
- Explain WHY, not just WHAT — Claude reasons better with understanding
- Avoid excessive ALWAYS/NEVER/MUST — explain reasoning instead
- Include examples with concrete input/output pairs
- Use a decision matrix to route to reference files

### Structure Pattern

```markdown
# [Skill Name]

[1-2 sentence purpose statement]

## Quick Decision Matrix
[Table routing to reference files based on user's situation]

## Core Concepts
[Essential knowledge needed for ALL uses of this skill]

## Reference Files
[Table of reference files with when-to-read guidance]
```

---

## 5. Bundled Resources

### Scripts (Deterministic Tasks)

```
scripts/
├── validate-config.sh    — Config validation (runs without loading into context)
├── generate-report.py    — Report generation
└── scan-dependencies.py  — Dependency scanning
```

Scripts execute without loading their content into context. Ideal for repetitive, deterministic operations.

### References (On-Demand Knowledge)

```
references/
├── express-security.md   — Loaded only when working with Express
├── fastapi-security.md   — Loaded only when working with FastAPI
└── owasp-api-top10.md    — Loaded when reviewing API security
```

For large reference files (>300 lines), include a table of contents at the top.

### Assets (Output Templates)

```
assets/
├── report-template.md    — Used in report generation
├── config-template.json  — Template for new configs
└── icons/                — Images for generated content
```

---

## 6. Agent Skills (Preloaded)

Skills can be preloaded into agents via the `skills:` frontmatter field:

```yaml
# .claude/agents/api-developer.md
---
name: api-developer
skills:
  - api-security
  - database-patterns
  - testing-conventions
---
```

**Behavior:** Full SKILL.md content is injected into the agent's system prompt at startup.

**Implications:**
- Agent always has this knowledge — no trigger needed
- Adds to agent's token budget
- Best for small, essential skills (under 200 lines)

**Agent-only skills:**
```yaml
# .claude/skills/api-conventions/SKILL.md
---
name: api-conventions
user-invocable: false
---
```

Setting `user-invocable: false` hides from the `/` menu but still allows Claude to invoke via Skill tool and agents to preload.

---

## 7. Plugins

Plugins package skills, agents, commands, and hooks for distribution.

### Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── hooks/
│   └── hooks.json
└── .mcp.json
```

### Namespacing

Plugin skills use `plugin-name:skill-name` format to prevent conflicts:
```
/my-plugin:api-security
```

### .skill File Format

Packaged skills for distribution. Created with:
```bash
python -m scripts.package_skill <path/to/skill-folder>
```

### Agent Skills Open Standard

As of December 2025, Anthropic released Agent Skills as an open standard. Skills are compatible across:
- Claude Code
- OpenAI Codex CLI
- ChatGPT
- Any Agent Skills-compatible platform

---

## 8. Testing Skills

### Evaluation Framework

Use the skill-creator skill for systematic testing:

1. **Write test prompts** — Realistic user queries the skill should handle
2. **Run with-skill and baseline** — Compare skill vs no-skill results
3. **Grade against assertions** — Quantitative pass/fail criteria
4. **Human review** — Qualitative evaluation via eval viewer
5. **Iterate** — Improve skill based on feedback

### Test Case Design

```json
{
  "skill_name": "api-security",
  "evals": [
    {
      "id": 1,
      "prompt": "I'm building a REST API with Express.js and need to add authentication. The API handles user data including emails and payment info.",
      "expected_output": "Should cover JWT, CORS, rate limiting, input validation, and data encryption",
      "files": []
    }
  ]
}
```

### Description Optimization

After skill is stable, optimize the description for triggering accuracy:

1. Generate 20 eval queries (10 should-trigger, 10 should-not-trigger)
2. Review with user
3. Run optimization loop
4. Apply best description

---

## 9. Known Issues

| Issue | Impact | Status |
|---|---|---|
| Full token loading at startup (GitHub #14882) | Higher costs than expected | Open |
| `context: fork` ignored via Skill tool (GitHub #17283) | Skills run in main context | Open |
| `/clear` didn't reset cached skills | Fixed February 2026 | Resolved |
| Skills from `--add-dir` not auto-loading | Fixed February 2026 | Resolved |
| Character budget now scales with context (2% of window) | Better for large contexts | v2.1.59+ |
