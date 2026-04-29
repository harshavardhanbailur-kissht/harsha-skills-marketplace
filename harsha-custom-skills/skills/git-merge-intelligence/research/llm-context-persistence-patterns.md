# LLM Context Window Management and Persistent Context Patterns: A Comprehensive Research Guide

**Last Updated:** 2026-04-07
**Research Scope:** Claude Code, Cursor, LangChain/LangGraph, open-source agentic systems
**Target Audience:** LLM agent developers managing large-scale coding tasks

---

## Executive Summary

Large language models (LLMs) operate under fundamental constraints that challenge long-running agents: limited context windows (even 200K tokens are "full" after minutes of work), session resets between API calls, automatic context compaction, and token budget limitations. This research synthesizes engineering practices from Claude Code, Cursor, LangChain, and open-source agentic projects to establish patterns for building persistence-aware agents that survive and thrive across context boundaries.

**Key Finding:** The most resilient agents treat persistent state as a first-class artifact, not an afterthought. Files become the "memory backbone"—not browser caches, not Redis ephemera, but durably-written state that survives compaction and can be re-read in isolation.

---

## 1. The Problem: Context Loss Mechanisms

### 1.1 The Four Vectors of Context Loss

#### **1.1.1 Context Window Limits**

- Claude 3.5 Sonnet: 200K tokens input, 4,096 output
- Cursor Agent: 128K normal, 200K "max mode" (but effective context often 70-120K after truncation)
- The "effective context window" problem: models can process 200K tokens but may not effectively retrieve or reason over information beyond ~100K tokens
- Reference: [LLM Context Window Limitations in 2026 | Atlan](https://atlan.com/know/llm-context-window-limitations/)

#### **1.1.2 Session Resets**

Every API call starts with a clean slate. The model has no persistent memory of:
- Previous decisions made 10 turns ago
- Architectural patterns established earlier in the conversation
- Intermediate work completed but not yet consolidated

**Impact:** A developer debugging an issue across multiple files can exhaust 200K tokens in under an hour on real-world codebases, forcing a hard context reset mid-task.

#### **1.1.3 Automatic Context Compaction**

Claude Code automatically triggers compaction when:
- Context utilization reaches ~95% of the 200K window (~167K tokens)
- The threshold was raised from ~77-78% utilization in mid-2025
- The `/compact` command can be triggered manually to control the process

**What survives compaction:**
- System prompts remain intact
- Recent messages (last N turns, typically 5-10)
- File contents read very recently may be retained
- **What gets lost:** Earlier conversation turns, intermediate reasoning, earlier file reads, decision context from 20+ turns ago

Reference: [Compaction - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/compaction)

#### **1.1.4 Token Budget Constraints**

Real-world usage patterns show:
- Agentic work on serious projects: $60-200/month in token spend
- A single session debugging a 10K-line codebase can burn 150K-200K tokens
- File reads, search results, tool outputs, and conversation history accumulate non-linearly
- Reference: [Claude Code vs Cursor: Deep Comparison for Dev Teams [2025] - Qodo](https://www.qodo.ai/blog/claude-code-vs-cursor/)

### 1.2 Why This Matters for Long-Running Tasks

The combined effect creates a "context cliff": as tasks grow from hours to days, the probability of losing critical context approaches certainty. Session resets, compaction, and token budgets force a choice:

1. **Abandon long tasks** (impractical for real work)
2. **Work inefficiently** (repeatedly re-establish context)
3. **Build persistence explicitly** (the winning pattern)

---

## 2. Persistent Context File Patterns: The Universal Lingua Franca

### 2.1 Files as the Memory Backbone

The most successful agentic systems store state in files, not in ephemeral memory. This works because:

- **Simplicity:** Files are an abstraction agents understand and can reliably manipulate
- **Durability:** Files survive session resets and API call boundaries
- **Retrievability:** Agents can search, read, and selectively reference file contents
- **Resilience to compaction:** File reads trigger re-retention; important files stay accessible
- **External access:** Humans can inspect, edit, and understand state files without reverse-engineering the agent

**Engineering Pattern (from Letta and LangGraph communities):**

```
External Memory (Files) + Disciplined Retrieval Strategy
= Agents that effectively work within context windows
```

Reference: [Memory Blocks: The Key to Agentic Context Management | Letta](https://www.letta.com/blog/memory-blocks)

### 2.2 Format Selection: Markdown, JSON, YAML

#### **2.2.1 Token Efficiency Comparison**

Based on 2025-2026 benchmarks:

| Format | Efficiency | Use Case | Notes |
|--------|-----------|----------|-------|
| **Markdown** | 11,612 tokens (baseline) | State summaries, human+LLM readable | Best for prose, decisions, reasoning trails |
| **YAML** | 12,333 tokens (-8% vs. JSON) | Configuration-like state | 20-35% savings on large arrays vs. JSON |
| **JSON** | 13,869 tokens | Structured queries, machine-parsing | Ideal when schema validation is required |
| **CSV** | ~7,000 tokens | Tabular data | 40-50% better than JSON for tables |
| **TOON** | Custom format | Dense state serialization | 18-40% reduction vs. standard formats |

**Key Finding:** Markdown is 15% more token-efficient than JSON for mixed content (text + data). YAML saves 20-30% on complex hierarchical data.

References:
- [Markdown is 15% more token efficient than JSON - OpenAI Developer Community](https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742)
- [Compressing LLM Context Windows: Efficient Data Formats | Reinforcement Coding](https://www.reinforcementcoding.com/blog/context-compression-efficient-data-formats)
- [JSON vs YAML vs Markdown: The Token Benchmarks | ShShell.com](https://www.shshell.com/blog/token-efficiency-module-13-lesson-2-format-comparison)

#### **2.2.2 Format Recommendations**

**Use Markdown when:**
- State is a mixture of structured data + explanatory prose
- Human readability is important (debugging, handoff)
- Schema is loose or evolves frequently
- File will be read back by humans and LLMs equally

**Use JSON when:**
- Schema must be strict and enforced (API payloads, config)
- Data will be parsed by strict schema validators
- State is deeply nested or requires complex queries
- Integration with typed systems (TypeScript, Rust) is critical

**Use YAML when:**
- State is configuration-heavy or hierarchical
- You control the backend and can parse YAML cheaply
- Indentation-based hierarchy mirrors conceptual structure
- Cost optimization is critical (20-30% token savings vs. JSON)

**Use CSV when:**
- State is tabular (decision logs, metrics, traces)
- Rows need to be filtered or aggregated
- Compression is critical (40-50% savings vs. JSON)

### 2.3 Information Retention Through Compaction

**The Compaction Survival Principle:**

Files that are read or referenced in recent turns are more likely to be retained in the compaction summary. Therefore:

1. **Write state files early**, not deferred until the end
2. **Reference state files in messages** (cite them, quote them, reason about them)
3. **Include URLs or file paths** in recent context so they remain visible
4. **Use consistent naming** across all state files so agents naturally aggregate them into summaries

**Empirical Observation (from Claude Code users):**

When a file is actively referenced in the last 10-15 turns, its contents are almost always preserved during compaction. When a file hasn't been mentioned in 30+ turns, it risks being compressed into a brief summary or lost entirely.

---

## 3. What Information Survives Compaction in Claude Code

### 3.1 What IS Preserved

During automatic compaction, Claude Code intelligently retains:

1. **System Prompt** — Fully intact. Your instructions remain unchanged.
2. **Recent Messages** — Last ~5-15 turns remain in full context
3. **Recently-Read Files** — If you read a file in the last 10 turns, its full path and location stay accessible
4. **Tool Definitions** — Available tools remain registered
5. **Active Execution Context** — Current debugging session, current branch, current file being edited
6. **Critical Decisions** — Explicit decisions (e.g., "chose approach X over Y") tend to be summarized and retained

Reference: [The Fundamentals of Context Management and Compaction in LLMs | Medium](https://kargarisaac.medium.com/the-fundamentals-of-context-management-and-compaction-in-llms-171ea31741a2)

### 3.2 What IS Lost

1. **Early Conversation Turns** — Turns 1-20 may be compressed to a 1-2 sentence summary
2. **Intermediate Reasoning** — "Why we considered approach A before choosing B" reasoning is dropped
3. **Earlier File Reads** — Files read 25+ turns ago lose their full contents; only a brief record remains
4. **Detailed Error Messages** — Verbose stack traces and tool output logs are truncated
5. **Exploratory Dead Ends** — "We tried X, it didn't work" is compressed away

### 3.3 Designing State Files for Compaction Resilience

**Pattern 1: The State File as "North Star"**

Create a single authoritative state file that gets updated after each major phase and explicitly referenced in recent turns:

```markdown
# TASK_STATE.md

## Current Status
- Phase: [current_phase]
- Last Updated: [timestamp]
- Progress: X% complete

## Key Decisions
- [Decision 1]: [Reasoning]
- [Decision 2]: [Reasoning]

## Current Context
- Working on: [file/feature]
- Last issue: [issue description]
- Next steps: [3 steps]

## How to Resume
If compaction occurs, read this file first. The state above captures:
1. What we've decided
2. What we're doing now
3. What comes next

Then reference the detailed logs in LOG_TRACE.md if you need specifics.
```

**Pattern 2: Progressive Disclosure in State Files**

Structure files with summary-first, then detail:

```markdown
# ANALYSIS_RESULTS.md

## TL;DR (read this first, 2-3 sentences)
We found X issues affecting Y, root cause is Z.

## Summary (5-10 key findings)
1. Finding 1 (critical)
2. Finding 2 (important)
...

## Detailed Analysis (full details, appendix-style)
### Finding 1
- Evidence: ...
- Impact: ...
- Remediation: ...
```

When compaction occurs, the TL;DR and Summary survive. The detailed analysis may be compressed, but the agent can request it be re-read if needed.

**Pattern 3: Cross-Referenced State Files**

Maintain multiple state files that link to each other:

```markdown
# STATUS.md
- Architecture decisions: see ARCHITECTURE.md
- Token usage trends: see METRICS.md
- Current blockers: see BLOCKERS.md

# ARCHITECTURE.md
- Component 1: [spec]
- Component 2: [spec]
- See also: STATUS.md for decisions

# METRICS.md
- Token budget used: X/Y
- Estimated remaining: Z
- See also: STATUS.md for current phase
```

This creates multiple "entry points" to the state. When one file is partially compressed, the cross-references guide the agent to read the full picture.

---

## 4. Patterns for Compaction-Resilient Workflows

### 4.1 Write State Immediately, Not Deferred

**Anti-Pattern:**
```
[Agent works for 10 turns]
[Agent says: "I'll write a summary at the end of this session"]
[Context fills to 95%]
[Compaction triggers, summary never written]
```

**Pattern:**
```
[Agent completes first phase]
→ Writes PHASE_1_SUMMARY.md immediately
→ Continues with phase 2
[Agent completes second phase]
→ Updates STATUS.md with new progress
→ Continues with phase 3
```

**Practical Rule:** Write state files after every major goal achieved, not after the entire task completes. For a 12-hour coding session, write state files every 1-2 hours of agent time.

### 4.2 Make Each File Self-Contained

A state file should be readable in isolation, without requiring context from other files:

**Anti-Pattern (requires external context):**
```markdown
# DECISIONS.md
- Used approach X (see ANALYSIS.md for why)
- Implemented in files A, B, C (see ARCHITECTURE.md)
```

**Pattern (self-contained with cross-references):**
```markdown
# DECISIONS.md

## Decision 1: Use Approach X
- **Reason:** Approach X handles 95% of cases. Alternatives Y and Z were considered but:
  - Y: Too slow (benchmarks in BENCHMARKS.md)
  - Z: Too complex for our team (risks in RISK_ANALYSIS.md)
- **Tradeoff:** X trades memory for speed
- **Files Affected:** A, B, C
- **Timeline:** Implemented 2026-04-03 to 2026-04-05

---
*See also: BENCHMARKS.md for performance data, RISK_ANALYSIS.md for risk assessment*
```

### 4.3 Include "How to Resume" Instructions in State Files

Every state file should have a brief "resume guide" at the top:

```markdown
# [STATE_FILE_NAME].md

## How to Resume from This File

If you're reading this file because:

### Compaction just happened
1. Read the "Current Status" section below
2. Check "Next Steps" to understand what's in progress
3. Re-read DETAILED_TRACE.md if you need context on recent decisions

### This is a fresh session
1. Start with the "TL;DR" section
2. Skim "Current Status" to get oriented
3. Jump to "Next Steps" to understand what you'll be doing

### You're returning after a day or more
1. Read "Current Status" and "Key Decisions"
2. Review "Blockers" to understand what's in your way
3. Read "How We Got Here" to understand the journey

---

## TL;DR

[2-3 sentence summary of this state file's purpose and current status]

## Current Status

[...]
```

Reference: [Effective context engineering for AI agents | Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 4.4 Use Consistent Field Names Across State Files

When you have multiple state files, use the same field names for analogous concepts:

**Inconsistent (confuses agent and compaction):**
```markdown
# DECISIONS.md
- **Decision Made:** ...
- **Tradeoffs:** ...
- **Files Changed:** ...

# BLOCKERS.md
- **Issue:** ...
- **Risk Factor:** ...
- **Affected Code:** ...
```

**Consistent (agent and compaction easily find key info):**
```markdown
# DECISIONS.md
- **Decision:** ...
- **Tradeoff:** ...
- **Affected Files:** ...
- **Timestamp:** ...

# BLOCKERS.md
- **Decision:** ... (the decision this blocker is about)
- **Tradeoff:** ... (the tradeoff we made)
- **Affected Files:** ... (which files need fixing)
- **Timestamp:** ... (when discovered)
```

Field consistency lets compaction algorithms and future agents predict where to find information.

### 4.5 Put Most Important Context at the Top

When compaction truncates a file (preserving the first N lines), the top of the file must be the most critical:

**Anti-Pattern (details first):**
```markdown
# TRACE.md

### Edge case 1: When Y happens and Z is null
[20 lines of detail]

### Edge case 2: Timing race condition
[15 lines of detail]

## TL;DR
We found two edge cases that must be fixed.
```

**Pattern (summary first):**
```markdown
# TRACE.md

## TL;DR
We found two critical edge cases:
1. Y-null case (affects 2% of users, high severity)
2. Timing race (affects 5% of users, low severity)

---

### Edge case 1: When Y happens and Z is null
[20 lines of detail]

### Edge case 2: Timing race condition
[15 lines of detail]
```

### 4.6 Timestamp Every State Entry

Include ISO 8601 timestamps on all state entries so agents can reason about recency:

```markdown
# DECISIONS.md

- **Decision:** Use Redis for cache
  - **Made:** 2026-04-05T14:30:00Z
  - **Context:** Token budget growing 15% per day
  - **Next review:** 2026-04-10T14:30:00Z
```

This helps the compaction algorithm understand which state is "stale" and can be pruned vs. "fresh" and critical.

---

## 5. Engineering Blog Posts and Community Practices

### 5.1 Claude Code Practitioners

**Key Resource:** [What to Do When Claude Code Starts Compacting | Du'An Lightfoot](https://www.duanlightfoot.com/posts/what-to-do-when-claude-code-starts-compacting/)

**Key Advice from Claude Code users (2025-2026):**
- Trigger `/compact` manually every 2-3 hours, don't wait for auto-compaction
- Create a CONTEXT_CHECKPOINT.md file that gets updated every 15-20 turns
- Reference files explicitly in turn N+1 after reading them in turn N (keeps them fresh)
- Use `/compact --instructions "Preserve: decisions.md, architecture.md. Discard: debug logs older than 1 hour"` to control what survives

### 5.2 Cursor Agent Community

**Key Resource:** [Cursor Agent in Large Projects: 7 Solutions to Missing Files and Wrong Code | BetterLink Blog](https://eastondev.com/blog/en/posts/dev/20260110-cursor-agent-large-projects/)

**Patterns from Cursor developers:**
- Use "Auto Attached" + glob patterns instead of "always mode" → reduces token usage by 70%
- Don't enable Agent context on all files; use MCP dynamic context discovery
- Budget $60-200/month for serious agentic work
- Create a `.cursor_state` directory with status files the agent checks at the start of each turn

### 5.3 LangChain/LangGraph Community

**Key Resource:** [Persistence - LangGraph | LangChain Docs](https://docs.langchain.com/oss/python/langgraph/persistence)

**Checkpointing Pattern (from LangGraph):**

LangGraph checkpoints the entire graph state after every "super-step" (major action). The checkpoint model:

1. Each checkpoint has a unique `checkpoint_id` and associated `thread_id`
2. State is saved deterministically (same inputs → same state)
3. Supports thread-based retrieval: "resume from checkpoint X"

**LangGraph supports multiple backends:**
- **SQLite** (MemorySaver, SqliteSaver): Development and local workflows
- **PostgreSQL** (PostgresSaver): Production, concurrent writes
- **Redis** (checkpoint-redis): Fast session resumption, high-throughput
- **MongoDB:** Document-oriented state storage

**Key Lesson:** Checkpoint after every major action, not just task boundaries. Default granularity is correct.

Reference: [Memory overview - LangChain Docs](https://docs.langchain.com/oss/python/langgraph/memory)

### 5.4 Open Source: The Agent File Standard (.af)

**Key Project:** [Agent File Format on GitHub](https://github.com/letta-ai/agent-file)

The Agent File format (.af) is an open standard for serializing stateful AI agents. It packages:

1. **System Prompt** - Agent instructions
2. **Memory Blocks** - Persistent editable memory (personality, user preferences)
3. **Tool Schemas** - Tool configurations and signatures
4. **LLM Settings** - Model choice, temperature, etc.

Agent Files enable:
- Checkpointing and version control of agent state
- Transfer between compatible frameworks
- Human inspection and editing of agent behavior

**Relevant for this research:** Agent Files demonstrate that the market is converging on the idea that state needs explicit, standardized formats.

### 5.5 Context Compaction Best Practices (2025-2026 Consensus)

Reference: [AI Agent Context Compression: Strategies for Long-Running Sessions | Zylos Research](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies)

**The consensus approach:**

1. **Trigger at 70% utilization**, not 95%. Don't wait for auto-compaction.
2. **Anchored Iterative Summarization:** Keep last N turns in full, compress everything older
3. **Tool Call Clearing:** Discard tool results from >10 turns ago (agent rarely needs raw results)
4. **Failure-Driven Guideline Optimization (ACON):** Automatically refine your compaction prompt based on failures

**ACON Results (2025):**
- 26-54% reduction in peak token usage
- No fine-tuning required (gradient-free)
- No API costs (runs locally)

Reference: [The Fundamentals of Context Management and Compaction in LLMs | Isaac Kargar, Medium](https://kargarisaac.medium.com/the-fundamentals-of-context-management-and-compaction-in-llms-171ea31741a2)

---

## 6. State File Design Principles

### 6.1 Progressive Disclosure: Summary → Detail → Deep-Dive

Structure state files like a book with executive summary, main text, and appendix:

```markdown
# ANALYSIS.md

## Executive Summary (30 words, read first)
[TL;DR of findings]

## Main Analysis (500 words, read if context allows)
### Finding 1
### Finding 2
### Finding 3

## Deep-Dive (2000 words, read only if needed)
### Finding 1 - Detailed Evidence
- Evidence point 1
- Evidence point 2
- Evidence point 3
### Finding 2 - Detailed Evidence
...

## Appendix: Raw Data
[Unprocessed logs, traces, metrics]
```

**Why this works:**
- Compaction preserves the summary and main text
- Agent can explicitly request deep-dive if needed
- Humans can skim the summary without reading 2000 lines
- File size doesn't explode; it scales gracefully

### 6.2 Redundancy: Important Context Appears in Multiple Files

Critical context should appear in at least 2 places:

**Example:**
- **DECISIONS.md:** "Chose cache strategy X"
- **STATUS.md:** "Cache strategy: X (see DECISIONS.md for rationale)"
- **ARCHITECTURE.md:** "Cache layer uses strategy X per decision #3"

When compaction happens, if one file is truncated, the information is still available in another file.

### 6.3 Freshness Indicators: Timestamps on All Entries

Every piece of state should have a timestamp:

```markdown
# DECISIONS.md

## Decision 1: Use Redis for cache
- **Decided:** 2026-04-05 14:30 UTC
- **Context at time:** Memory pressure, P95 latency issues
- **Assumption:** Redis cluster costs < $500/month
  - **Assumption validated:** 2026-04-06 (YES)
- **Status:** In progress (50% implemented)
  - **Last updated:** 2026-04-07 10:15 UTC
```

Timestamps enable compaction algorithms to discard stale assumptions and preserve recent decisions.

### 6.4 Cross-References: Files Link to Each Other

Create a "web" of state files that reference each other:

```markdown
# STATUS.md
- **Architecture decisions:** DECISIONS.md
- **Current blockers:** BLOCKERS.md
- **Token budget:** METRICS.md → token_usage_trend
- **Phase progress:** see PHASES.md#current_phase

# DECISIONS.md
- See STATUS.md for current implementation progress
- See RISK_ANALYSIS.md for risk mitigation
- See BLOCKERS.md for issues

# BLOCKERS.md
- See DECISIONS.md for why we chose this approach
- See STATUS.md for timeline
```

Cross-references are lightweight ways to say "if you want more context on this, read this other file." Compaction preserves these links, allowing agents to navigate the state graph.

### 6.5 State as Event Log + Derived State

Instead of storing state as a single blob, use an event log pattern:

```markdown
# STATE_EVENTS.log

[2026-04-05 14:30:00] DECISION: cache_strategy=redis
[2026-04-05 14:31:00] DECISION: redis_cluster_provider=aws_elasticache
[2026-04-05 15:00:00] IMPLEMENTATION_STARTED: redis_integration
[2026-04-05 16:30:00] IMPLEMENTATION_BLOCKED: connection_pool_exhaustion
[2026-04-06 09:00:00] IMPLEMENTATION_RESUMED
[2026-04-06 12:00:00] IMPLEMENTATION_COMPLETE
[2026-04-06 14:00:00] DECISION: cache_ttl=3600
```

Then derive "current state" deterministically:

```markdown
# STATE_CURRENT.md

## Derived from STATE_EVENTS.log

- **Cache Strategy:** redis
- **Provider:** aws_elasticache
- **Implementation Status:** COMPLETE
- **TTL:** 3600 seconds
- **Last Status Update:** 2026-04-06 14:00:00
```

**Why this works:**
- Event log is immutable (append-only)
- Current state can be recomputed if compaction damages it
- State machine is explicit and debuggable
- Conflicts are handled by "latest event wins" or explicit resolution rules

---

## 7. Token-Efficient Encoding

### 7.1 How Much Context Fits in 10K Tokens?

**Rough estimates (depends on format and content):**

| Content Type | Tokens | Fits in 10K |
|---|---|---|
| 1 large decision (explanation + tradeoffs) | 200-300 | 30-50 copies |
| 1 code file (typical: 300 lines) | 500-800 | 12-20 copies |
| 1 debug trace (stack trace + context) | 300-500 | 20-33 copies |
| 1 architecture diagram (text-based) | 150-250 | 40-66 copies |
| Full codebase analysis (10K lines, 3 files) | 2,500-4,000 | 2-4 copies |
| Conversation history (10 turns) | 1,500-2,500 | 4-6 copies |

**Practical Rule of Thumb:** 10K tokens ≈ 40K characters of text, ≈ 10 pages of single-spaced prose, ≈ 3-4 medium source files.

For 200K context windows:
- Real usable context: ~150-170K tokens (20-30K reserved for output)
- At 50% utilization (75K tokens): room for ~30 large decisions + 15 code files + 5 debug traces
- At 95% utilization (160K tokens): approaching capacity for complex tasks

### 7.2 Compression Techniques

#### **7.2.1 Format Selection** (covered in detail in section 2.2)

- Markdown: 11,612 tokens (baseline)
- JSON: 13,869 tokens (+19% vs. Markdown)
- CSV: 7,000 tokens (-40% vs. Markdown, best for tables)
- TOON: Custom format achieving 18-40% reduction

#### **7.2.2 Abbreviations and Structured Notation**

Instead of prose, use symbols and abbreviations:

**Anti-Pattern (wordy):**
```markdown
The decision was made to use Approach X instead of Approach Y because:
1. Approach X is faster (500ms vs. 2000ms)
2. Approach X uses less memory (100MB vs. 500MB)
3. Approach X is simpler to maintain
```

**Pattern (compact notation):**
```markdown
## Decision: Use Approach X

- Speed: X=500ms, Y=2000ms (4x faster)
- Memory: X=100MB, Y=500MB (5x less)
- Maintenance: X=simpler
```

**Savings:** ~40% token reduction on decision logs.

#### **7.2.3 Removing Prose Filler**

**Anti-Pattern:**
```markdown
The following is a comprehensive analysis of the issues we found:

We performed an exhaustive review of the codebase and discovered several
important problems that need to be addressed. First, we found a critical
issue related to...
```

**Pattern:**
```markdown
## Issues Found

### Critical: [Issue Name]
- Evidence: [line X in file Y]
- Impact: [severity]
- Fix: [solution]
```

**Savings:** ~50% token reduction by removing introductory prose.

#### **7.2.4 Hierarchical Summarization**

Keep full details at the bottom, summaries at the top:

**Instead of:**
```
500 lines of detailed analysis
(maybe agents get context to read it all)
```

**Use:**
```
# Summary
- Finding 1: High impact
- Finding 2: Medium impact
- Finding 3: Low impact

# Details
## Finding 1: High impact
[50 lines]

## Finding 2: Medium impact
[50 lines]

## Finding 3: Low impact
[50 lines]
```

When compaction happens, the summary survives. Details can be re-read if needed.

### 7.3 When to Use JSON vs. Markdown for State

**Use JSON when you need:**
- Schema validation (e.g., state must pass a TypeScript interface)
- Machine parsing with no human reading
- API payloads that must be transmitted
- Structured queries ("get all decisions made after date X")

**Use Markdown when you need:**
- Human readability (debugging, handoff, inspection)
- Mix of prose explanation + structured data
- Flexible schema that evolves frequently
- Token efficiency (15% better than JSON)

**Hybrid approach (recommended):**
```markdown
# STATE.md (Markdown for human + LLM reading)

## Decisions (structured data in Markdown table)
| Decision | Date | Status | Reason |
|---|---|---|---|
| Use Redis | 2026-04-05 | In Progress | Performance |
| Use AWS RDS | 2026-04-04 | Completed | Reliability |

## Analysis (prose explanation)
The decision to use Redis was driven by...

---

## EXPORT (JSON for machine parsing)
```json
{
  "decisions": [
    {"name": "Use Redis", "date": "2026-04-05", ...}
  ]
}
```
```

---

## 8. Recommended Workflows for Compaction-Resilient Development

### 8.1 The "Checkpoint Ritual" (Every 2-3 Hours)

```
[Agent completes major goal or reaches 50% context usage]

→ Step 1: Write CHECKPOINT.md
   - What we've accomplished
   - What we decided
   - Current blockers
   - Next 3 steps

→ Step 2: Update METRICS.md
   - Tokens used so far
   - Tokens remaining
   - Estimated completion

→ Step 3: Trigger /compact (manual)
   - Preserve: DECISIONS.md, ARCHITECTURE.md, CHECKPOINT.md
   - Can discard: Raw debug logs older than 1 hour

→ Step 4: Reference checkpoint in next message
   - "Resuming from checkpoint at [timestamp]"
   - Agent knows to read CHECKPOINT.md first
```

### 8.2 State File Hierarchy (Multi-Scale Persistence)

**Minute-scale (session state):**
```
CURRENT_TASK.md         ← What we're doing right now
ACTIVE_ISSUES.md        ← Problems we're solving
```

**Hour-scale (phase state):**
```
PHASE_SUMMARY.md        ← What we accomplished this phase
DECISIONS_PHASE_N.md    ← Decisions made in this phase
BLOCKERS_PHASE_N.md     ← Issues we hit
```

**Day-scale (project state):**
```
PROJECT_STATUS.md       ← Overall progress
ARCHITECTURE.md         ← System design
DECISIONS.md            ← All strategic decisions (all time)
METRICS.md              ← Token usage, time spent, velocity
```

**Week+ scale (institutional knowledge):**
```
LEARNED_PATTERNS.md     ← What we learned (reusable)
LESSONS.md              ← Mistakes, successes, next time
README.md               ← How to continue this project
```

### 8.3 Token Budget Tracking

Create a METRICS.md file that updates every N turns:

```markdown
# METRICS.md (Updated every 10 turns)

## Session Statistics (started 2026-04-07 10:00 UTC)

- **Total tokens used:** 45,000 / 200,000 (22.5%)
- **Tokens used per turn:** ~1,800 (average)
- **Estimated remaining turns:** ~86 (at current burn rate)
- **Estimated time remaining:** ~8 hours (at 1 turn/min)

## Budget Allocation
- **Reserved for compaction:** 10,000 (5%)
- **Reserved for output:** 4,096 (2%)
- **Available for work:** 140,904 (70.5%)
- **Currently used:** 40,000 (20%)
- **Safety margin:** 20,000 (10%)

## Burn Rate Trends
- First hour: 2,000 tokens/turn (file exploration)
- Hours 2-4: 1,500 tokens/turn (normal work)
- Next predicted: 1,200 tokens/turn (if task is well-scoped)

## Recommendation
- **Current pace:** OK, will complete with ~30K tokens margin
- **Action:** Continue at current rate, but monitor if burn increases
- **Trigger checkpoint** when utilization reaches 50% (100K tokens)
```

---

## 9. Conclusion: The Emerging Standard

### 9.1 Convergence on Filesystem-First Architecture

By 2026, the consensus across Claude Code, Cursor, LangChain, and open-source projects has converged on:

1. **Files are the memory backbone** — Not ephemeral in-memory state
2. **Compaction-aware design** — Write state early, reference it in recent turns
3. **Progressive disclosure** — Summary first, details on demand
4. **Cross-references** — State files form a web, not isolated artifacts
5. **Timestamps everywhere** — Enable compaction to reason about recency
6. **Token efficiency** — Use Markdown (15% better than JSON) for mixed content, CSV for tables

### 9.2 Practical Starting Point

For a new long-running LLM project, start with this minimal state structure:

```
project/
├── STATUS.md              (updated every 2-3 hours)
├── DECISIONS.md           (updated as decisions are made)
├── ARCHITECTURE.md        (updated as architecture changes)
├── BLOCKERS.md            (updated as issues arise)
├── METRICS.md             (updated every 10 turns)
└── PHASE_N/
    ├── PHASE_SUMMARY.md
    └── DECISIONS_PHASE_N.md
```

Each file:
- Has a TL;DR at the top
- Includes timestamps on all entries
- Cross-references other files
- Can be read in isolation

### 9.3 Future Directions

**Emerging trends (2025-2026):**

1. **Automatic state summarization:** Tools that generate CHECKPOINT.md automatically
2. **State file versioning:** Git-like history of state mutations with diffs
3. **Cross-session state transfer:** Format standards (Agent File, TOON) enabling agents to pick up where others left off
4. **Dynamic context refresh:** MCP-driven mechanisms to keep state files hot during compaction
5. **Compaction optimization:** ACON-like approaches that learn what compaction strategies work best for your task

The field is moving toward **persistent context as infrastructure**, not as an afterthought.

---

## 10. References and Resources

### Core Documentation
- [Compaction - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/compaction)
- [Context Compaction - Anthropic Cookbook](https://platform.claude.com/cookbook/tool-use-automatic-context-compaction)
- [Effective Context Engineering for AI Agents | Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### Context Window Management
- [LLM Context Window Limitations in 2026 | Atlan](https://atlan.com/know/llm-context-window-limitations/)
- [Memory Blocks: The Key to Agentic Context Management | Letta](https://www.letta.com/blog/memory-blocks)
- [Agent State Management | Hendricks AI](https://hendricks.ai/insights/agent-state-management-persistent-context-ai-systems)

### Format Comparison & Token Efficiency
- [Markdown is 15% more token efficient than JSON | OpenAI Community](https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742)
- [Compressing LLM Context Windows | Reinforcement Coding](https://www.reinforcementcoding.com/blog/context-compression-efficient-data-formats)
- [LLM Token Optimization | Redis Blog](https://redis.io/blog/llm-token-optimization-speed-up-apps/)

### Claude Code Practitioners
- [What to Do When Claude Code Starts Compacting | Du'An Lightfoot](https://www.duanlightfoot.com/posts/what-to-do-when-claude-code-starts-compacting/)
- [Compaction - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/compaction)

### Cursor Agent
- [Claude Code vs Cursor | Builder.io](https://www.builder.io/blog/cursor-vs-claude-code)
- [Cursor Agent in Large Projects | BetterLink Blog](https://eastondev.com/blog/en/posts/dev/20260110-cursor-agent-large-projects/)

### LangChain/LangGraph
- [Persistence - LangGraph Docs](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Memory Overview - LangGraph Docs](https://docs.langchain.com/oss/python/langgraph/memory)
- [LangGraph & Redis | Redis Blog](https://redis.io/blog/langgraph-redis-build-smarter-ai-agents-with-memory-persistence/)

### Open Source Standards
- [Agent File Format (.af) | GitHub](https://github.com/letta-ai/agent-file)
- [LangGraph - Build Resilient Language Agents | GitHub](https://github.com/langchain-ai/langgraph)
- [Deep Agents | GitHub](https://github.com/langchain-ai/deepagents)

### Compaction Research & Best Practices
- [AI Agent Context Compression Strategies | Zylos Research](https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies)
- [The Fundamentals of Context Management and Compaction | Isaac Kargar, Medium](https://kargarisaac.medium.com/the-fundamentals-of-context-management-and-compaction-in-llms-171ea31741a2)
- [Building an Internal Agent: Context Window Compaction | Irrational Exuberance](https://lethain.com/agents-context-compaction/)

### Token Efficiency & Optimization
- [Token Efficiency and Compression Techniques | Medium](https://medium.com/@anicomanesh/token-efficiency-and-compression-techniques-in-large-language-models-navigating-context-length-05a61283412b)
- [Context Compression Techniques: Reduce Costs by 50% | SitePoint](https://www.sitepoint.com/optimizing-token-usage-context-compression-techniques/)

---

## Appendix A: Checklist for Building Compaction-Resilient Systems

- [ ] Create STATUS.md file as the "north star" for current task state
- [ ] Write state after every major goal, not deferred until task end
- [ ] Use Markdown for mixed prose + data (15% better than JSON)
- [ ] Include TL;DR at the top of every state file
- [ ] Add "How to Resume" instructions in state files
- [ ] Timestamp every decision and status update
- [ ] Cross-reference between related state files
- [ ] Trigger manual `/compact` at 50-70% context utilization
- [ ] Reference state files explicitly in recent turns (keeps them hot)
- [ ] Track token burn rate in METRICS.md
- [ ] Create state file hierarchy: minute-scale, hour-scale, day-scale, week+ scale
- [ ] Test that each state file is readable in isolation
- [ ] Use consistent field names across all state files
- [ ] Include file paths in cross-references for easy access
- [ ] Maintain event log + derived state pattern for reproducibility

---

---

## Appendix: Git Merge Conflict Context Persistence

For AI-assisted merge conflict resolution, context persistence directly prevents resolution inconsistency. This section synthesizes merge-specific patterns.

### The Merge Context Problem

When an AI agent resolves merge conflicts across multiple context windows (e.g., a complex 50-file merge that spans multiple Claude Code sessions), without persistent state:

1. **Conflict re-resolution**: Earlier sessions resolve the same file differently on subsequent sessions
2. **Semantic inconsistency**: Decision to accept "left" on a method signature change in file A is forgotten when resolving a related method in file B
3. **Testing regression**: Earlier sessions may have noted "needs additional tests post-merge"; this knowledge is lost

**Solution**: Persist merge decisions and semantic context in structured files.

### Merge Decision Persistence Pattern

**File: `.merge_context.md`** (Human + AI readable)

```markdown
# Merge Context: feature/new-auth → main

## Merge Details
- **Date Started**: 2026-03-15 10:00 UTC
- **Source**: feature/new-auth (commit abc123def)
- **Target**: main (commit 456789ghi)
- **Conflict Count**: 23 files

## Semantic Decisions (Non-Negotiable)
These decisions apply across ALL affected files:

### 1. Authentication Flow Architecture
**Decision**: Use token-based auth with automatic refresh (rather than manual refresh calls)
**Files Affected**: 
  - src/auth/authenticator.ts
  - src/auth/session.ts
  - src/auth/interceptors.ts
**Rationale**: Automatic refresh simplifies integration points and reduces boilerplate

### 2. Method Signature Changes
**Decision**: Adopt new optional parameter pattern: `(user: User, options?: SessionOptions)`
**Files Affected**:
  - src/auth/session.ts
  - src/auth/validators.ts
**Rationale**: Backward compatible; allows gradual rollout of new features

### 3. Import Path Organization
**Decision**: Use absolute imports from `@/` alias (not relative imports)
**Files Affected**: All 23 conflicting files
**Rationale**: Matches existing codebase style; reduces relative path brittleness

## Conflicts Resolved ✓

### src/auth/authenticator.ts
- **Type**: Import reorganization + method addition
- **Resolution**: Accepted both sides (non-overlapping changes)
- **Confidence**: 95%
- **Rationale**: Feature branch added new OAuth methods; main added new imports. Both safe together.

### src/auth/session.ts
- **Type**: Method signature change + implementation detail
- **Resolution**: Accepted feature branch (left)
- **Confidence**: 88%
- **Rationale**: Feature branch's optional parameter pattern aligns with decision #2. Main's version is older.

## Conflicts Pending ⏳

### src/config/defaults.ts (High Priority)
```
OURS:    const MAX_RETRY = 3;
THEIRS:  const MAX_RETRY = 5;
```
**Context**: Feature branch increases retry limit for reliability; main keeps current value
**Decision Needed**: Aligns with decision #1 (auto-refresh). Higher retry count supports automatic recovery.
**Recommendation**: Accept THEIRS (5)

### src/auth/interceptors.ts (Medium Priority)
**Type**: Interceptor registration pattern changed
**Ours**: Uses deprecated `registerInterceptor()`
**Theirs**: Uses new `middleware` pattern
**Decision Needed**: Feature branch modernizes. Accept theirs, but check for test coverage.

## Post-Merge Tasks
- [ ] Update tests in `tests/auth/session.test.ts` (method signature changed)
- [ ] Add integration tests for automatic token refresh
- [ ] Verify backward compatibility with existing OAuth consumers
- [ ] Run `npm run lint` to catch import path issues
- [ ] Deploy to staging environment for E2E testing
```

**Why This Works**:
- Semantic decisions are explicit and referenced by file (prevents re-deciding)
- Rationale explains *why* (prevents contradictory decisions in later files)
- Confidence scores flag review needs
- Post-merge tasks are documented (prevents testing gaps)

### Conflict Resolution Decision Log

**File: `.merge_resolutions.jsonl`** (JSONL = newline-delimited JSON, efficient for appending)

```jsonl
{"timestamp": "2026-03-15T10:15:00Z", "file": "src/auth/authenticator.ts", "lines": "1-50", "decision": "both", "confidence": 0.95, "rationale": "non-overlapping imports"}
{"timestamp": "2026-03-15T10:30:00Z", "file": "src/auth/session.ts", "lines": "120-145", "decision": "left", "confidence": 0.88, "rationale": "feature branch matches architectural decision"}
{"timestamp": "2026-03-15T11:00:00Z", "file": "src/config/defaults.ts", "lines": "18-20", "decision": "right", "confidence": 0.85, "rationale": "aligns with auto-refresh strategy; higher retry count needed"}
```

**Benefits**:
- Append-only (never overwrite; full audit trail)
- Easy to re-read after context reset: `tail -20 .merge_resolutions.jsonl`
- Machine-parseable for validation: verify no contradictions between decisions
- Token-efficient (JSONL is ~15% better than JSON format)

### Merge Conflict Validation Against Semantic Decisions

After context reset, validate that resolved conflicts align with documented semantic decisions:

```bash
#!/bin/bash
# validate_merge_consistency.sh

# Read semantic decisions
DECISIONS=$(cat .merge_context.md | grep -A 5 "^### ")

# For each resolved conflict, check against semantic decisions
while IFS= read -r resolution; do
  file=$(echo "$resolution" | jq -r '.file')
  decision=$(echo "$resolution" | jq -r '.decision')
  
  # Check if file was supposed to follow semantic decision #1 (token auth)
  if [[ "$file" =~ auth && "$decision" == "left" ]]; then
    # Verify that "left" aligns with auto-refresh decision
    echo "✓ $file: resolution aligns with 'auto-refresh' decision"
  fi
done < <(cat .merge_resolutions.jsonl | jq -s '.[]')
```

This validation ensures:
1. No contradictory decisions across files
2. All resolutions align with documented semantic architecture
3. Inconsistencies are caught before final merge

### Information Retention During Compaction

For merge operations spanning multiple Claude Code sessions, reference merge state files strategically:

**In conversation**: Always cite the merge context file when resuming:
```
I'm resuming the merge from main into feature/new-auth. 
Current state is documented in .merge_context.md:
- 23 total conflicts
- 12 resolved (confidence 85%+)
- 11 pending

The semantic architecture decisions are:
1. Token-based auth with automatic refresh
2. Optional parameter pattern for method signatures
3. Absolute imports using @/ alias

Continuing with src/config/defaults.ts...
```

By citing the file in recent messages, the entire merge context survives compaction. When compaction occurs, the agent resumes with full knowledge of:
- Semantic decisions already made
- Conflicts already resolved
- Architecture constraints

**Impact**: Post-compaction, the agent continues deterministically without re-deciding conflicts.

### Multi-Session Merge Workflows

For very large merges (100+ files), split across multiple Claude Code sessions:

**Session 1**: Analyze conflicts, categorize by type, create `.merge_context.md`
**Session 2**: Resolve "auto-mergeable" conflicts (imports, non-overlapping)
**Session 3**: Resolve "semantic" conflicts (method signatures, config)
**Session 4**: Resolve "manual review" conflicts (logic changes, architectural)
**Session 5**: Validate all resolutions, run tests, deploy

Each session reads the same `.merge_context.md` and appends to `.merge_resolutions.jsonl`. The merge operation becomes a stateful, multi-agent process with explicit handoffs.

---

**This research document is a living reference.** As agentic AI practices evolve, expected updates:
- Q3 2026: Compaction standardization and tooling maturity
- Q4 2026: Multi-session state transfer patterns; merge conflict coordination
- 2027: Automatic state summarization and compression tuning

