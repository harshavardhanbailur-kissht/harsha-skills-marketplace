# Research 07: Agent Teams & Production Orchestration Patterns

## Source Validation
- **Primary**: Anthropic Engineering Blog (multi-agent research system), Claude Code Docs (agent-teams)
- **Secondary**: TechCrunch (Opus 4.6 launch), SitPoint guide, alexop.dev analysis
- **Empirical**: 16-agent C compiler stress test (~2000 sessions, $20K, 100K lines)
- **Scrutiny Level**: Maximum (direct Anthropic engineering sources)

## Key Findings

### 1. Agent Teams vs Subagents (Critical Distinction)
Subagents: Run within single session, report only to parent, no peer communication.
Agent Teams: Independent context windows, peer-to-peer messaging, shared task board.

**Implication for our skill**: Our executor.py currently uses the subagent pattern
(parent dispatches → workers execute → parent collects). This is correct for API-level
orchestration. Agent Teams is a Claude Code feature, not an API primitive. Our skill
should document when to use each:
- **API orchestration** (our scripts): When building standalone tools, CI pipelines, production services
- **Agent Teams** (Claude Code): When humans are in the loop during development

### 2. Orchestrator-Worker Architecture (Validated by Anthropic)
Anthropic's own Research system confirms our architecture:
- Lead agent (Opus) analyzes query → develops strategy → spawns subagents (Sonnet)
- 90.2% outperformance over single-agent Opus (matches our reference)
- Key lesson: "Each subagent needs an objective, output format, tools/sources guidance,
  and clear task boundaries" — validates our Interface Contracts approach

### 3. Production Delegation Patterns
From Anthropic's engineering:
- **Teach the orchestrator how to delegate**: Without detailed task descriptions, agents
  duplicate work, leave gaps, or fail to find necessary information
- **Scale effort to query complexity**: Agents struggle to judge appropriate effort —
  embed scaling rules in prompts (matches our Model-Effort Matrix)
- **Test harness design is critical**: For long-running teams, design tests that keep
  agents on track without human oversight

### 4. Four Orchestration Archetypes
- **Leader**: Single coordinator dispatching to workers (our current pattern)
- **Swarm**: Specialized agents self-organizing around tasks
- **Pipeline**: Sequential handoff chain (A → B → C)
- **Watchdog**: Observer agent monitoring quality/progress

**Enhancement opportunity**: Add a Watchdog agent concept to our verification pipeline —
a lightweight monitor that tracks progress across parallel workers and flags stalls/anomalies.

### 5. Subagent Execution Best Practices (2026)
- Parallelism cap: 10 concurrent operations (queue more, execute in batches of 10)
- Each Task spawns with ~20K token overhead — don't over-parallelize
- Recommended agent count: 3-4 specialized agents maximum for most tasks
- "Most sub-agent failures aren't execution failures — they're invocation failures"
  (insufficient context in prompts)

### 6. Token Economics of Multi-Agent
- Active multi-agent sessions consume 3-4x more tokens than single-threaded
- Plan first (cheap) → execute in parallel (expensive but fast)
- Set CLAUDE_CODE_SUBAGENT_MODEL to run workers on cheaper model
- Context isolation prevents cross-contamination but multiplies base token cost

### 7. 16-Agent Stress Test Results
Anthropic built a Rust C compiler using 16 agents:
- ~2000 Claude Code sessions, $20K API cost
- 100K lines of code output
- Can compile Linux kernel on x86, ARM, RISC-V
- Key challenges: race conditions, message ordering, graceful degradation

## Contradictions & Nuances
- Agent Teams documentation says "experimental" — production stability unknown
- Swarms feature (Jan 2026) has "documented reliability issues"
- 3-4 agent recommendation contradicts 16-agent stress test — the difference is
  task scope and human oversight level

## Applied Improvements
1. Add Watchdog pattern to verification pipeline
2. Document subagent vs Agent Teams decision matrix
3. Add invocation quality guidelines to prompt templates
4. Set parallelism limits (max 10 concurrent, recommend 3-5 for most tasks)
5. Add token overhead awareness to cost optimization stack
