# Context Window Management for Large PRDs

## The Challenge

PRDs come in many sizes. A typical feature PRD is 5-10 pages. But enterprise PRDs can be 50-100 pages. A token budget of 200,000 seems unlimited, but it's not when you consider:

- System prompt + skill instructions: ~3,000 tokens
- Full PRD content: 10,000-50,000 tokens
- Working memory (thinking, analysis): 30,000 tokens
- Output space (task decomposition): 20,000 tokens
- External tool calls (Notion MCP, AskUserQuestion): 5,000 tokens

**Total reserved:** ~60,000 tokens minimum

This leaves 140,000 tokens working budget. A 30-page PRD (15,000 tokens) combined with complex analysis quickly exhausts this.

## Early Detection: Estimating PRD Size

### Rule of Thumb
```
1 page of PRD ≈ 500 tokens
5 pages ≈ 2,500 tokens
10 pages ≈ 5,000 tokens
20 pages ≈ 10,000 tokens
50 pages ≈ 25,000 tokens
100 pages ≈ 50,000 tokens
```

### Automatic Detection
When the PRD is first uploaded, estimate its size:

```python
# Pseudocode
prd_char_count = len(prd_content)
estimated_tokens = prd_char_count / 4  # rough estimate: 4 chars per token

if estimated_tokens > 15000:
    activate_chunking_strategy()
    log_warning("Large PRD detected. Using chunking approach.")
```

### User Input
Ask directly: "This PRD is quite large. Should I use a chunking strategy to stay within context limits, or process it all at once?"

### Decision Rule
```
If PRD tokens > 15,000:
  → Use Section-Based Chunking (Phase-based processing)
Else if PRD tokens > 25,000:
  → Use Two-Pass Analysis (compress then decompose)
Else:
  → Process normally (full PRD in memory)
```

## Strategy 1: Section-Based Chunking

**Best for:** Well-structured PRDs with clear sections

### How It Works

**Step 1: Extract Structure (very light processing)**

Read through the PRD once, extract only:
- All section headings and sub-headings
- Estimated token count per section
- Key keywords per section

Output: Table of Contents

```markdown
# PRD Structure

## 1. Overview (500 tokens)
- Vision
- Success metrics
- Timeline

## 2. User Requirements (2000 tokens)
- User personas
- User flows
- Feature list

## 3. Technical Requirements (1500 tokens)
- Architecture
- Technology stack
- Performance targets

## 4. Security & Compliance (800 tokens)
- Authentication
- Data privacy
- Regulatory requirements
```

Token cost: ~1000 tokens total (brief read)

**Step 2: Identify Epics from Structure Only (no deep reading)**

Based on section titles and feature list, propose an epic hierarchy:

```
Epic 1: User Onboarding (covers sections 1 + 2.1)
Epic 2: Core Features (covers section 2.2-2.4)
Epic 3: Advanced Analytics (covers section 2.5)
Epic 4: Security & Compliance (covers section 4)
```

Prompt: "Based on the PRD structure, I propose these 4 epics. Does this grouping make sense?"

Token cost: ~500 tokens (brief analysis)

**Step 3: For Each Epic, Load Only Relevant Sections**

When decomposing Epic 1, load:
- Overview section (relevant context)
- Section 2.1 (user onboarding details)
- Security section (auth requirements)
- Skip: Advanced Analytics, other epics' details

Process those sections deeply to extract features and tasks.

```
PRD Load Pattern:
Full read: Overview only (~500 tokens)
Targeted reads:
  - Epic 1 decomposition: Load sections 1 + 2.1 + 4 (~2000 tokens)
  - Epic 2 decomposition: Load sections 1 + 2.2-2.4 + 4 (~2500 tokens)
  - Epic 3 decomposition: Load sections 1 + 2.5 + 4 (~1500 tokens)
  - Epic 4 decomposition: Load sections 4 fully (~800 tokens)
```

Total tokens for full decomposition: 500 + 2000 + 2500 + 1500 + 800 = 7,300 tokens

Compare to: full PRD in memory at 15,000 tokens. We save 7,700 tokens and have better focus.

**Step 4: Cross-Reference and Build Dependencies**

After all epics decomposed independently, do a final pass:
- Check for implicit dependencies between epics
- Flag any contradictions discovered
- Validate no feature is duplicated across epics

Token cost: ~1000 tokens (comparison analysis)

### Implementation Checklist

- [ ] Extract table of contents with section token estimates
- [ ] Propose epic grouping based on sections
- [ ] Confirm epic grouping with user (if in interactive mode)
- [ ] For each epic: load relevant PRD sections, decompose deeply
- [ ] Store epic decomposition results (avoid re-reading sections)
- [ ] Final cross-reference pass for consistency
- [ ] Output: complete decomposition (same quality as full-read approach)

**Token savings:** 40-60% reduction for large PRDs

---

## Strategy 2: Two-Pass Analysis

**Best for:** PRDs with lots of detail but clear intent

### How It Works

**Pass 1: Compress the PRD**

Read the entire PRD once. Output:

1. **Executive Summary** (~500 tokens)
   - Vision in 2-3 sentences
   - Key success metrics
   - Timeline

2. **Requirement List** (~1000 tokens)
   - Flat list of all requirements (not hierarchical yet)
   - One line per requirement
   - Keep context brief

3. **Dependency Matrix** (~500 tokens)
   - Which requirements depend on which
   - External dependencies (APIs, infrastructure, stakeholders)

4. **Assumptions & Gaps** (~300 tokens)
   - Ambiguities detected
   - Missing information flagged
   - Assumptions we made

Token cost: ~5,000 tokens to read full PRD + ~2,300 tokens to compress = 7,300 tokens

**Pass 2: Use Compressed Artifact for Decomposition**

Forget the original PRD. Use only:
- Executive Summary
- Requirement List
- Dependency Matrix
- Assumptions & Gaps

Decompose based on this ~2,300 token artifact instead of the 15,000 token original.

This gives:
- Full understanding (we read everything in Pass 1)
- Smaller context footprint (compressed artifact in decomposition)
- Focus on structure, not details (no distractions from original PRD)

Token cost for decomposition: ~6,000 tokens (same complexity, but smaller source)

**Total token cost:** 7,300 (Pass 1) + 6,000 (Pass 2) = 13,300 tokens

Compare to: full PRD approach at 10,000 (read) + 12,000 (decompose) = 22,000 tokens. We save 8,700 tokens.

### Implementation Checklist

- [ ] Read full PRD end-to-end
- [ ] Generate executive summary (vision, metrics, timeline)
- [ ] Extract flat requirement list
- [ ] Build dependency matrix (requirement A → requirement B)
- [ ] Document assumptions and gaps
- [ ] (Optional) Ask clarification questions based on gaps
- [ ] Use compressed artifact for all downstream decomposition
- [ ] Output: complete decomposition (same quality as original approach)

**Token savings:** 30-40% reduction

---

## Strategy 3: Hierarchical Processing

**Best for:** Very large PRDs (100+ pages) with clear epics

### How It Works

**Tier 1: Identify Epics (structure only)**
- Load PRD sections with epic names and high-level descriptions
- Don't load detailed feature/task specs yet
- Output: Epic definitions

**Tier 2: For Each Epic, Identify Features**
- Load PRD sections relevant to that epic
- Extract features (ignore task-level details)
- Output: Feature definitions per epic

**Tier 3: For Each Feature, Identify Tasks**
- Load PRD task-level details for that feature only
- Extract tasks and acceptance criteria
- Output: Task definitions per feature

### Example Flow

```
Load Budget: 200,000 tokens total
Reserved: 60,000 tokens
Working Budget: 140,000 tokens

Tier 1 (Epic extraction):
  - Load only section headers + epic descriptions
  - Cost: 2,000 tokens
  - Output: 10 epics defined

Tier 2 (Feature extraction):
  - For each of 10 epics:
    - Load relevant PRD sections (~800 tokens per epic)
    - Extract 3-5 features per epic
  - Cost: 10 * 800 = 8,000 tokens
  - Output: 40 features defined
  - Remaining budget: 130,000 tokens

Tier 3 (Task extraction):
  - For each of 40 features:
    - Load feature details (~300 tokens per feature)
    - Extract 3-5 tasks per feature
  - Cost: 40 * 300 = 12,000 tokens
  - Output: 160 tasks defined
  - Remaining budget: 118,000 tokens

Cross-reference + Cleanup:
  - Validate dependencies, check for contradictions
  - Cost: 5,000 tokens
  - Final budget: 113,000 tokens
```

This approach processes a 100,000-token PRD in sequential chunks, never loading the whole thing at once.

### Implementation Checklist

- [ ] Tier 1: Load PRD structure, extract epics
- [ ] Tier 2: For each epic, load relevant sections and extract features
- [ ] Tier 3: For each feature, load task-level details and extract tasks
- [ ] Final pass: cross-reference and validate
- [ ] Output: complete decomposition

**Token savings:** 50-70% reduction for very large PRDs

---

## Context Budget Allocation

When planning how to use your context window, reserve memory as follows:

### Fixed Overhead (~50,000 tokens)
```
System prompt + instructions: 3,000
Tool descriptions (Notion, AskUserQuestion, etc.): 2,000
Response formatting + headers: 1,000
Buffer for API responses/errors: 2,000
-----
Subtotal: 8,000 tokens
```

### Working Memory
```
PRD content (variable): 5,000-50,000 tokens
   (use chunking strategies if >15,000)

Analysis + thinking (extended thinking if available): 10,000-30,000 tokens
   (used for deep understanding, not output)

Output space (decomposition results): 20,000-40,000 tokens
   - Epics, features, tasks, acceptance criteria
   - Notion database schemas
   - Clarification documentation

Tool calls + responses: 5,000 tokens
   (Notion MCP, AskUserQuestion, etc.)
```

### Decision Rule

If (PRD tokens + working memory + output space) > 140,000:
  → Activate chunking strategy
  → Use targeted approach instead of full read

---

## Using Extended Thinking for Large PRDs

When available (Claude Opus 4.6 with ultrathink), use extended thinking strategically:

### When to Use Extended Thinking

**DO use for:**
- Phase 2 (ANALYZE): Deep understanding of PRD intent across unclear sections
- Phase 3 (DECOMPOSE): Complex dependency reasoning, critical path analysis
- Ambiguity resolution: figuring out what the PRD really means

**DON'T use for:**
- Phase 1 (STRUCTURE): Simple reading and extraction (wastes thinking budget)
- Phase 5 (FORMAT): Mechanical output generation (use fast inference instead)

### Token Impact

Extended thinking costs 2-3x normal tokens but provides much higher quality analysis. For large PRDs:

```
Scenario 1: Full PRD without extended thinking
  - Read: 10,000 tokens
  - Analyze: 15,000 tokens (fast, but may miss nuance)
  - Decompose: 12,000 tokens
  - Total: 37,000 tokens

Scenario 2: Full PRD with extended thinking on ANALYZE phase
  - Read: 10,000 tokens (fast)
  - Analyze: 40,000 tokens (extended thinking, 2-3x cost but much better)
  - Decompose: 12,000 tokens (fast)
  - Total: 62,000 tokens

Tradeoff: +25,000 tokens for much higher quality analysis. Worth it for complex PRDs.
```

### Usage Pattern

```
# Phase 1: Read PRD (fast, no thinking needed)
PRD content understanding: FAST

# Phase 2: Analyze PRD intent (use thinking if available)
if available(extended_thinking):
  Run deep analysis with thinking enabled
  # Cost: ~25,000 tokens but very high quality
else:
  Run standard analysis
  # Cost: ~12,000 tokens, decent quality

# Phase 3: Decompose into tasks (use thinking for complex dependencies)
if available(extended_thinking):
  Use thinking for critical path and dependency resolution
else:
  Use fast inference for task creation
```

---

## Multi-Agent Context Optimization

If the decomposition task is handled by multiple sub-agents:

### Architecture

```
Main Agent: Coordinates, reads full PRD structure
  ↓ assigns epic decomposition to sub-agents

Sub-Agent 1: Decompose Epic A
  - Load only Epic A relevant sections (~2000 tokens)
  - Output: Features, tasks, dependencies for Epic A
  - Memory freed after: ~6000 tokens

Sub-Agent 2: Decompose Epic B
  - Load only Epic B relevant sections (~2000 tokens)
  - Output: Features, tasks, dependencies for Epic B
  - Memory freed after: ~6000 tokens

Sub-Agent 3: Decompose Epic C
  - (same pattern)

Main Agent: Receives all outputs
  - Validates cross-epic dependencies
  - Merges results into single decomposition
```

### Benefits

- Each sub-agent only holds one epic's details in memory
- Epic-by-epic processing scales to any PRD size
- Sub-agents can work in parallel (if available)
- Main agent focuses on integration and validation

### Context per Sub-Agent

```
Fixed overhead: ~8,000 tokens
Shared context (PRD overview, architecture, naming conventions): ~2,000 tokens
Epic-specific context (one epic): ~2,000 tokens
Output (tasks for one epic): ~10,000 tokens
-----
Total per sub-agent: ~22,000 tokens (very small)
```

Even with 10 epics, this approach scales: 22k * 10 = 220k tokens, with parallelization.

---

## Practical Decision Tree

Use this tree to choose a strategy:

```
1. Estimate PRD size in tokens
   ├─ <5,000 tokens
   │  └─ Process normally (full read + full decomposition)
   │
   ├─ 5,000-15,000 tokens
   │  └─ Process normally (still fits comfortably)
   │
   ├─ 15,000-30,000 tokens
   │  ├─ If well-structured (clear sections)?
   │  │  └─ Use Section-Based Chunking
   │  │
   │  └─ If poorly structured?
   │     └─ Use Two-Pass Analysis
   │
   ├─ 30,000-50,000 tokens
   │  └─ Use Two-Pass Analysis OR Hierarchical Processing
   │
   └─ >50,000 tokens
      └─ Use Hierarchical Processing (required)
```

---

## Monitoring & Adjustment

As you process the PRD:

### Track Token Usage
```
After Phase 1 (structure): check remaining budget
If low: activate chunking strategy before Phase 2
After Phase 2 (analysis): check remaining budget
If <50k tokens: reduce output verbosity in Phase 5
```

### Red Flags

- "Sorry, I've hit token limits" → You waited too long to chunk
- "I don't fully understand this section" → You had too little context for that epic
- "I can't process this output" → Output is too verbose, needs summarization

### Course Correction

If you run low on tokens:
- Stop deep analysis, focus on high-level decomposition only
- Reduce acceptance criteria detail
- Summarize multi-page feature descriptions into single-line summaries
- Focus on tasks, not full elaboration in each task

---

## Summary

Context management transforms decomposition from a "hope it fits" approach to a structured, scalable process:

1. **Detect early:** Estimate PRD size upfront
2. **Choose strategy:** Match strategy to PRD size and structure
3. **Process strategically:** Use chunking, two-pass, or hierarchical approaches
4. **Allocate budget:** Reserve memory for thinking, output, tools
5. **Use extended thinking** strategically for high-complexity analysis
6. **Monitor progress:** Track tokens remaining after each phase
7. **Adjust if needed:** Switch strategies if running low

Large PRDs are not a barrier to high-quality decomposition. They just require planning.
