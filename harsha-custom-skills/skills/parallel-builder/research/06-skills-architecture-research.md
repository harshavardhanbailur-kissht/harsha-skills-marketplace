# Research: Agent Skills Open Standard & Composability Architecture

**Tier**: Maximum Scrutiny | **Date**: Feb 2026 | **Sources**: 8 validated
**Confidence**: HIGH (official Anthropic docs + agentskills.io spec)

---

## Key Findings

### 1. Agent Skills: Open Standard Adopted by OpenAI, Google, and Others (HIGH confidence)
- Anthropic launched Agent Skills as an open standard in December 2025
- Published at agentskills.io — "a simple, open format for giving agents new capabilities"
- OpenAI adopted the same format for Codex CLI and ChatGPT
- Compatible platforms: Claude Code, Claude.ai, ChatGPT, Codex CLI, Cursor, GitHub Copilot, Goose (Block), Gemini CLI, Roo Code, Windsurf, Amp, Factory
- Skills you create work across ALL platforms that adopt the standard
- **Source**: [Anthropic: Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [agentskills.io](https://agentskills.io/home)

### 2. Composability: The Industry Shift (HIGH confidence)
- Industry moving from monolithic agents to **composable agents** assembled from portable skill packages
- Agent starts minimal, acquires expertise as needed
- Skills = prompts that modify conversation context + permissions that modify execution context
- NOT traditional code — this achieves flexibility, safety, and composability
- **Source**: [New Stack](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/), [inference.sh](https://inference.sh/blog/skills/agent-skills-overview)

### 3. SKILL.md Anatomy (HIGH confidence)
Required fields:
- `name`: max 64 chars, lowercase letters/numbers/hyphens, must match directory name
- `description`: max 1024 chars — the PRIMARY triggering mechanism

Optional fields:
- `allowed-tools`: Restrict which tools the skill can use
- `model`: Override model for this skill
- `compatibility`: Required tools/dependencies
- `metadata`: Additional key-value pairs

Three-tier progressive disclosure:
- Level 1 (Always loaded): Name + description (~100 tokens)
- Level 2 (On trigger): Full SKILL.md body (<5K tokens ideal)
- Level 3 (As needed): References, scripts, assets (unlimited)

**Source**: [Claude API: Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview), [Deep Dive Blog](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

### 4. Meta-Tool Pattern: How Skills Actually Work (HIGH confidence)
- Claude Code exposes a single `Skill` tool
- Tool description contains `<available_skills>` XML section from all skills' frontmatter
- Claude matches user intent to skill descriptions using pure LLM reasoning
- No regex, embeddings, or classifiers — just the model's judgment
- This is why description quality is the #1 factor for triggering
- **Source**: [Deep Dive Blog](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)

### 5. Ecosystem & Distribution (MODERATE confidence)
- skills.sh: Primary distribution hub
- agentskills.io: Specification docs + discovery
- skillsmp.com: Independent directory with cross-platform aggregation
- skillhub.club: 20K+ skills with AI-evaluated quality ratings + playground
- GitHub: anthropics/skills (official repository)
- **Source**: [SkillsMP](https://skillsmp.com), [GitHub](https://github.com/anthropics/skills)

### 6. Skill Discovery & Scoping (HIGH confidence)
Skills are discovered from multiple scopes with priority:
1. **Enterprise** (highest priority)
2. **Personal** (~/.claude/skills/)
3. **Project** (.claude/skills/)
4. **Plugin** (from installed plugins)

Claude automatically loads relevant skills based on user intent matching against descriptions.
- **Source**: [Claude Help Center](https://support.claude.com/en/articles/12512176-what-are-skills)

### 7. Inter-Skill Communication: No Direct Mechanism (MODERATE confidence)
- Skills CANNOT explicitly reference other skills
- No direct inter-skill dependency mechanism
- Claude can load and coordinate multiple skills based on the task (implicit composability)
- The skill-creator meta-skill is the closest pattern to "a skill managing skills"
- **Workaround**: Write descriptions that naturally complement each other
- **Source**: [Getting Up To Speed Guide](https://codeagentsalpha.substack.com/p/claude-agent-skills-complete-getting)

---

## Recommendations for Our Meta-Skill

### Description Optimization
The description is everything for triggering. Our description should be "pushy" to prevent undertriggering:
```yaml
description: >
  Meta-skill that decomposes complex features into parallel subtasks, generates
  optimized prompts for Claude Sonnet 4.6 agents, executes them concurrently via
  the Anthropic API, and verifies the combined output with Claude Opus 4.6.
  Use this skill whenever the user wants to build something complex that benefits
  from parallel agent execution. Also triggers when: parallel agents, fan-out,
  multi-agent, task decomposition, orchestration, skill building pipeline,
  "build this with multiple agents", or any non-trivial multi-part deliverable.
```

### File Organization (Best Practice)
```
parallel-skill-builder/
├── SKILL.md                    # Core instructions (<500 lines)
├── scripts/                    # Deterministic operations
│   ├── planner.py
│   ├── executor.py
│   ├── verifier.py
│   └── merger.py
├── references/                 # Deep guidance loaded as needed
│   ├── PROMPT_ENGINEERING.md
│   ├── ORCHESTRATION.md
│   ├── DECOMPOSITION.md
│   └── VERIFICATION.md
├── research/                   # Research findings
│   ├── 01-extended-thinking-research.md
│   ├── 02-multi-agent-failures-research.md
│   ├── 03-task-decomposition-research.md
│   ├── 04-verification-pipeline-research.md
│   ├── 05-anthropic-api-patterns-research.md
│   └── 06-skills-architecture-research.md
├── templates/                  # Parameterized prompts
│   ├── subtask_prompt.md
│   ├── planner_system.md
│   └── verifier_rubric.md
└── examples/
    └── sample_decomposition.json
```

### Progressive Disclosure Strategy
1. SKILL.md (Level 2): Workflow overview, when to use, key patterns (~265 lines)
2. References (Level 3): Deep technical guides loaded when Claude needs detail
3. Research (Level 3): Evidence base for design decisions
4. Scripts (Level 3): Execute without loading code into context

### Cross-Platform Portability
Since Agent Skills is now an open standard, our skill works on:
- Claude Code & Claude.ai (primary target)
- Cursor, VS Code with Copilot
- ChatGPT / Codex CLI (if they adopt the format)
- Any agentskills.io-compatible platform

---

## Source Registry
1. [Anthropic: Agent Skills Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
2. [agentskills.io](https://agentskills.io/home)
3. [Claude API: Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
4. [Deep Dive Blog](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
5. [anthropics/skills GitHub](https://github.com/anthropics/skills)
6. [New Stack](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/)
7. [inference.sh Blog](https://inference.sh/blog/skills/agent-skills-overview)
8. [Claude Help Center](https://support.claude.com/en/articles/12512176-what-are-skills)
