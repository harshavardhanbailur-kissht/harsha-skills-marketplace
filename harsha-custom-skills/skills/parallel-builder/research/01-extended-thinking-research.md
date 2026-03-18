# Research: Claude 4.6 Extended Thinking & Effort Parameter Optimization

**Tier**: Maximum Scrutiny | **Date**: Feb 2026 | **Sources**: 8 validated
**Confidence**: HIGH (multiple official sources agree)

---

## Key Findings

### 1. Adaptive Thinking Replaces Manual budget_tokens (HIGH confidence)
- Claude Opus 4.6 (Feb 2026) introduces **adaptive thinking** as the recommended reasoning mode
- Model dynamically decides when and how much to reason based on task complexity
- Replaces the binary on/off extended thinking toggle
- Automatically enables **interleaved thinking** (reasoning between tool calls)
- **Source**: [Anthropic Claude Opus 4.6 announcement](https://www.anthropic.com/news/claude-opus-4-6), [Claude API docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

### 2. Effort Parameter: 4 Levels (HIGH confidence)
- **low**: Minimal reasoning, fastest, cheapest — use for simple agent workers
- **medium**: Balanced — good for routine subtasks
- **high** (default): Full reasoning — standard for most tasks
- **max**: Absolute highest capability — use for planning and verification only
- **Source**: [What's new in Claude 4.6](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6)

### 3. Interleaved Thinking: Critical for Agents (HIGH confidence)
- Claude 4 models can think **between tool calls** — not just before the first one
- Enables more sophisticated reasoning after receiving tool results
- budget_tokens can exceed max_tokens (it's total across all thinking blocks)
- Adaptive thinking automatically enables interleaved thinking
- Remove the old `interleaved-thinking-2025-05-14` beta header
- **Source**: [Building with extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

### 4. Manual budget_tokens Still Supported for Sonnet (MODERATE confidence)
- Sonnet 4.6 supports `thinking: {type: "enabled"}` with manual budget
- Minimum budget: 1,024 tokens
- Start at minimum, increase incrementally to find optimal range
- For budgets above 32K, use batch processing to avoid networking issues
- Thinking tokens billed as output tokens at standard rate
- **Source**: [Extended thinking docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

### 5. Agent Teams: Parallel Multi-Agent in Claude Code (MODERATE confidence)
- Research preview in Claude Code — multiple Opus 4.6 agents work in parallel
- Coordinating on shared goals (codebase reviews, large refactors, research)
- Token usage increases proportionally with agent count
- Off by default — opt-in feature
- **Source**: [VentureBeat](https://venturebeat.com/technology/anthropics-claude-opus-4-6-brings-1m-token-context-and-agent-teams-to-take), [IT Pro](https://www.itpro.com/technology/artificial-intelligence/anthropic-reveals-claude-opus-4-6-enterprise-focused-model-1-million-token-context-window)

---

## Practical Recommendations for Multi-Agent Systems

### Model-Effort Matrix
| Agent Role | Model | Effort | Thinking Mode |
|---|---|---|---|
| **Planner/Orchestrator** | Opus 4.6 | max | Adaptive |
| **Verification Judge** | Opus 4.6 | high | Adaptive |
| **Worker (complex)** | Sonnet 4.6 | high | Manual (budget: 8K-16K) |
| **Worker (routine)** | Sonnet 4.6 | medium | Manual (budget: 1K-4K) |
| **Worker (simple)** | Haiku 4.5 | low | None |

### Cost Optimization Strategy
1. Use **effort=medium** for Sonnet workers to reduce thinking token spend
2. Use **adaptive thinking** for Opus (let it decide — it's calibrated well)
3. For Sonnet workers on routine tasks, cap budget_tokens at 4096
4. Reserve **effort=max** only for planning and final verification
5. Thinking tokens are output tokens — they're 5x the price of input tokens

### Context & Compaction
- Opus 4.6: 200K context window (1M in beta at $10/$37.50 per M for long prompts)
- Use compaction for long-running agent tasks to summarize own context
- Don't rely on long context — models effectively utilize only 10-20% (research finding)

---

## Source Registry
1. [Anthropic: Claude Opus 4.6](https://www.anthropic.com/news/claude-opus-4-6)
2. [What's new in Claude 4.6](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6)
3. [Building with extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
4. [VentureBeat: Agent Teams](https://venturebeat.com/technology/anthropics-claude-opus-4-6-brings-1m-token-context-and-agent-teams-to-take)
5. [IT Pro: Opus 4.6 Enterprise](https://www.itpro.com/technology/artificial-intelligence/anthropic-reveals-claude-opus-4-6-enterprise-focused-model-1-million-token-context-window)
6. [MetaCTO: API Pricing](https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration)
7. [Digital Applied: Features & Benchmarks](https://www.digitalapplied.com/blog/claude-opus-4-6-release-features-benchmarks-guide)
8. [Amazon Bedrock: Extended Thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-extended-thinking.html)
