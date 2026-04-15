# Emerging Patterns & Future-Proofing

Capabilities that are API-available or experimental today but expected to become standard across Claude Code, Cowork, and Chat. Design for these now so your workflows benefit immediately when they ship.

## Table of Contents
1. Programmatic Tool Calling (PTC)
2. Dynamic Web Filtering
3. Tool Use Examples
4. Agent Teams Evolution
5. Future-Proofing Checklist

---

## 1. Programmatic Tool Calling (PTC)

**Current Status (March 2026):** Available on Claude API (Opus 4.6, Sonnet 4.6). Not yet in Claude Code CLI, Cowork, or Chat — but this is clearly on the roadmap as the infrastructure exists at the model level.

### What PTC Does

Instead of each tool call requiring a full round-trip (inference → tool → inference → tool → inference), PTC lets Claude write Python code that orchestrates multiple tools in a single inference pass. Only stdout enters context — intermediate results stay in the container.

**Traditional (3 tools = 3 inference passes):**
```
Claude → tool1() → Claude → tool2() → Claude → tool3() → Claude
```

**PTC (3 tools = 1 inference pass):**
```
Claude → Python(tool1() + tool2() + tool3()) → stdout → Claude
```

### Benefits

- **~37% token reduction** for multi-tool sequences
- **Batch processing:** Loop over items in one pass
- **Early termination:** Stop when success criteria met (no wasted inference)
- **Data filtering:** Claude filters results in code before they enter context
- **Chained operations:** Complex data pipelines in a single pass

### Architecture Patterns (Design for These Now)

**Pattern 1: Multi-Source Data Aggregation**
```python
# PTC will orchestrate this in one pass
results = {}
for db in ["west", "east", "central"]:
    data = await query_database(f"SELECT SUM(revenue) FROM sales WHERE region='{db}'")
    results[db] = data[0]["revenue"]

# Only the summary enters context, not all raw query results
print(f"Revenue by region: {results}")
```

**Pattern 2: Filtered Search**
```python
# Fetch many results, filter to relevant ones
all_results = await web_search("Claude Code hooks system")
relevant = [r for r in all_results if "PreToolUse" in r.content or "PostToolUse" in r.content]
print(f"Found {len(relevant)} relevant results out of {len(all_results)}")
for r in relevant:
    print(f"- {r.title}: {r.url}")
```

**Pattern 3: Batch File Processing**
```python
# Process all test files without individual tool calls
import glob
files = glob.glob("src/**/*.test.ts", recursive=True)
failures = []
for f in files:
    content = await read_file(f)
    if "skip" in content.lower() or "todo" in content.lower():
        failures.append(f)
print(f"Files needing attention: {failures}")
```

### Current Limitations (API-level)

- No MCP tools (standard tools only)
- No web tools (WebFetch, WebSearch)
- No structured outputs alongside PTC
- Container lifetime: ~4.5 minutes
- Not available on Bedrock or Vertex (API and Foundry only)

### How to Prepare

1. **Identify multi-tool sequences** in your workflows — these will benefit most
2. **Structure data pipelines** as batch operations where possible
3. **Design for stdout-as-interface** — agents that summarize before returning
4. **Use sub-agents for complex tool chains** today — these will naturally convert to PTC later

---

## 2. Dynamic Web Filtering

**Current Status:** Available at API level. Expected in Claude Code.

Claude writes code to filter web search/fetch results before they enter context:

```
Query → Search results → Claude filters via code → Relevant content only → Claude reasons
```

**Results:** 24% fewer input tokens. Sonnet 4.6: +13.3pp accuracy. Opus 4.6: +16.3pp accuracy.

### How to Prepare

- Design skills that search broadly then filter narrowly
- Structure reference lookups as "search then extract" patterns
- Prefer targeted queries with post-filtering over narrow queries that might miss results

---

## 3. Tool Use Examples

**Current Status:** Available at API level. Partially used in Claude Code via tool descriptions.

Adding concrete input examples to tool schemas dramatically improves tool usage accuracy (72% → 90%):

```json
{
  "name": "create_ticket",
  "input_schema": { ... },
  "input_examples": [
    {
      "title": "Login page returns 500 error",
      "priority": "critical",
      "assignee": "oncall-team",
      "labels": ["bug", "auth", "production"]
    }
  ]
}
```

### How to Prepare

- When building MCP servers, include `input_examples` in tool definitions
- When designing skills that use tools, include example invocations in the SKILL.md
- Document expected tool input/output formats explicitly

---

## 4. Agent Teams Evolution

**Current Status:** Experimental (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true`).

Agent Teams will mature into a stable feature. Current capabilities:
- Direct agent-to-agent communication
- Shared task list with dependency tracking
- File locking for race condition prevention
- Split-pane display in tmux/iTerm2

### How to Prepare

- Design agents with clear, non-overlapping responsibilities (they need to coordinate)
- Use `isolation: worktree` for agents that modify files (prevents conflicts)
- Keep agent count to 3-5 per team (coordination overhead scales quadratically)
- Write agent descriptions that enable peer discovery ("I handle X, delegate Y to...")

---

## 5. Future-Proofing Checklist

When designing Claude Code projects, audit against this checklist:

- [ ] **Multi-tool sequences identified** — Will convert to PTC for ~37% token savings
- [ ] **Data pipelines designed as batch operations** — Natural PTC candidates
- [ ] **MCP tool schemas include examples** — Ready for Tool Use Examples
- [ ] **Agents have clear boundaries** — Ready for Agent Teams coordination
- [ ] **Agents use worktree isolation** — Required for parallel Agent Teams
- [ ] **Search operations use broad-then-filter pattern** — Ready for Dynamic Web Filtering
- [ ] **Skills designed for progressive disclosure** — Will benefit from true lazy loading when GitHub #14882 resolves
- [ ] **Context fork patterns ready** — Will work correctly when GitHub #17283 resolves
