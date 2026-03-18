# Thinking Depth Management Reference

Patterns for managing analysis depth and ensuring comprehensive coverage.

## Table of Contents
- [Depth Hierarchy](#depth-hierarchy)
- [When to Go Deeper](#when-to-go-deeper)
- [File-Based Persistence](#file-based-persistence)
- [Thinking Triggers](#thinking-triggers)

---

## Depth Hierarchy

### Analysis Depth Levels

| Level | Depth | When to Use |
|-------|-------|-------------|
| **Surface** | Quick overview | Never - not enough for execution |
| **Standard** | Covers main cases | Simple, well-understood problems |
| **Deep** | Includes edge cases | Most features |
| **Exhaustive** | Every scenario | Complex, critical, or foundational work |

### What Each Level Includes

**Surface (Avoid)**
- General description
- No specifics
- *Not useful for execution*

**Standard**
- Main happy path
- Common error states
- Basic implementation steps

**Deep**
- All happy paths
- All error states
- Edge cases
- Alternatives considered
- Micro-level implementation

**Exhaustive**
- Everything in Deep
- Race conditions
- Security implications
- Performance considerations
- Future extensibility
- Creative enhancements

---

## When to Go Deeper

### Depth Decision Matrix

| Factor | Go Deeper If |
|--------|--------------|
| **Foundational** | This will be built upon |
| **Complex** | Multiple interacting parts |
| **Critical** | Failure would be severe |
| **Novel** | No existing pattern to follow |
| **Ambiguous** | Requirements unclear |

### Questions to Assess Depth Needed

1. Will other code depend on this?
2. Are there security implications?
3. Are there performance implications?
4. Is the requirement clear or vague?
5. How bad would a bug be?

---

## File-Based Persistence

### Why Files Matter

All analysis goes to `.deep-think/` files because:
1. **Survives context compaction** - thinking isn't lost
2. **Executor can read it** - separate session can implement
3. **Human can review it** - transparent thinking
4. **Iteratable** - can be refined over sessions

### What to Persist

| Should Persist | Should NOT Persist |
|----------------|-------------------|
| Design decisions | Intermediate reasoning |
| Rationale for choices | Dead-end explorations |
| Implementation steps | Verbose explanations |
| Edge cases | Redundant information |
| File:line references | General knowledge |

### File Size Guidelines

| File | Target Size | If Too Long |
|------|-------------|-------------|
| OVERVIEW.md | 1-2 pages | Tighten scope statement |
| CURRENT_STATE.md | 2-4 pages | Focus on relevant code |
| ARCHITECTURE.md | 2-4 pages | Summarize alternatives |
| IMPLEMENTATION.md | 3-6 pages | Keep micro-level detail |
| EDGE_CASES.md | 2-4 pages | Use tables efficiently |
| OPTIMIZATIONS.md | 1-2 pages | Prioritize suggestions |
| CREATIVE_IDEAS.md | 1-2 pages | Top ideas only |
| EXECUTION_CHECKLIST.md | 1-2 pages | Concise steps |

---

## Thinking Triggers

### Phrases That Deepen Analysis

Use these in your thinking to ensure depth:

| Trigger | Effect |
|---------|--------|
| "Consider all possible scenarios" | Broadens coverage |
| "Explore alternative methodologies" | Generates options |
| "Think through edge cases exhaustively" | Finds failures |
| "What would fail? How?" | Reveals risks |
| "What would make this exceptional?" | Elevates quality |
| "What would a senior engineer question?" | Finds gaps |

### Self-Prompting Pattern

When stuck or unsure if deep enough:

```
I need to think more deeply about [TOPIC].

Questions to explore:
1. What are all the ways this could go wrong?
2. What assumptions am I making?
3. What would a skeptical reviewer ask?
4. What edge cases haven't I considered?
5. What would make this truly excellent?
```

---

## Quality Indicators

### Signs of Insufficient Depth

- Vague language ("handle appropriately")
- Missing file:line references
- Only happy path documented
- No alternatives considered
- "TBD" or placeholder content

### Signs of Good Depth

- Specific file:line references
- All scenarios documented
- Multiple alternatives with rationale
- Prevention and recovery for failures
- Micro-level implementation detail
- Executor could work from files alone
