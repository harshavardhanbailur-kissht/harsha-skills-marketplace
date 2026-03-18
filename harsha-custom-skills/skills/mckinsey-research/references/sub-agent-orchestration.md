# Sub-Agent Orchestration

## When to Use Sub-Agents

Use sub-agents when:
- Multiple INDEPENDENT research vectors exist (not sequential dependencies)
- Main context >60% utilized (need fresh context for deep research)
- High-cost subtasks (50+ file reads or web searches per vector)
- Verification tasks (need unbiased second opinion without orchestrator bias)

Do NOT use sub-agents when:
- Simple factual lookups (Standard tier)
- Sequential dependencies (each step needs previous output)
- Research scope is narrow enough for single-agent handling

## Spawn Decision Algorithm

```
IF research_vectors > 3 AND vectors_are_independent:
    USE sub-agents
ELIF main_context_utilization > 60%:
    USE sub-agents for remaining vectors
ELIF any_single_vector_requires > 50_searches:
    USE sub-agent for that vector
ELSE:
    Handle in main context
```

## Optimal Agent Count

Determine agent count by matching gaps to practical context constraints:

| Research Scope | Expected Gaps | Recommended Agents | Rationale |
|---|---|---|---|
| Small (<10 entries) | 3-5 | 3-5 agents | One agent per gap, manageable collation |
| Medium (10-30) | 5-15 | 5-8 agents | Prioritize by severity; some gaps can share agents |
| Large (30-100) | 10-30 | 8-12 in 2 waves | Wave 1 resolves top gaps; Wave 2 fills remaining |
| Massive (100+) | 20-50+ | 8-12 per wave, 2-3 waves | More waves, not more agents per wave |

**Practical ceiling**: Beyond ~10 concurrent agents, each agent's token budget shrinks
enough to degrade individual research quality. Prefer fewer, better-resourced agents.
If 20+ gaps exist, use waves rather than launching all at once.

**Budget allocation**: Reserve 30-40% of total context budget for synthesis and
verification. Don't spend everything on search.

## Sub-Agent Types

### Explorer
- Broad search on a sub-question
- Returns findings with sources
- Neutral framing (no embedded conclusion)

### Validator
- Takes a specific claim
- Tries to DISPROVE it
- Returns evidence for AND against

### Contrarian
- Searches specifically for criticism, failures, alternatives
- "Why [X] fails" and "migration away from [X]" searches
- Returns strongest counter-arguments

### Deep-Diver
- Goes deep on one promising thread identified by Explorers
- Reads primary sources, not just summaries
- Returns detailed analysis of one narrow topic

### Verifier (QA)
- Spot-checks 20% of merged knowledge base
- Verifies source accuracy
- Checks confidence justification
- Identifies missing context

## Prompt Template for Sub-Agents

Every sub-agent prompt MUST include:

```xml
<role>
You are a research agent investigating: [specific topic].
You must search for evidence from MULTIPLE perspectives.
</role>

<context>
[Background information the agent needs — keep neutral]
</context>

<task>
Research: [specific research question — neutrally framed]
Execute these search types: [primary, criticism, evolution — as applicable]
</task>

<constraints>
- Search for evidence AGAINST the obvious answer, not just for it
- Tag every claim with confidence (likelihood + evidence quality)
- Include sources with full provenance
- Flag contradictions — do NOT resolve them
</constraints>

<output_schema>
Return findings as structured JSON:
{
  "topic": "string",
  "findings": [
    {
      "claim": "string",
      "likelihood": "Certain|Highly Likely|Likely|Possible|Unlikely",
      "evidence_quality": "High|Moderate|Low|Very Low",
      "sources": [{"id": "src_X", "title": "", "url": "", "date": "", "type": ""}],
      "caveats": "string",
      "contradicting_evidence": "string or null"
    }
  ],
  "competing_positions": [],
  "gaps_identified": [],
  "search_log": ["what was searched and what was found"]
}
</output_schema>
```

**CRITICAL**: Never embed the orchestrator's preferred hypothesis in the prompt.
Frame all prompts neutrally. The sub-agent should not know which answer the
orchestrator expects.

## Wave-Based Dispatch (for Massive Research)

When 20+ gaps exist, don't launch all agents at once:

### Wave 1: High-Priority Gaps (6-10 agents)
- Launch agents for the highest-severity gaps
- These are the gaps that would invalidate the entire research if unfilled

### Between Waves: Re-Analysis
- Collate Wave 1 results
- Re-assess remaining gaps (some may be resolved by Wave 1 findings)
- Re-prioritize based on new information

### Wave 2+: Targeted Deep-Dives (6-8 agents per wave)
- Focus on remaining gaps and areas needing depth
- May include Verifier agents for quality assurance

### Termination Criteria
- Stop when: <15% of original gaps remain unfilled
- OR: Return on investment drops below 1.5 (new insights / search cost)
- OR: Saturation detected (new searches aren't adding information)

## Result Collation (6-Step Algorithm)

### Step 1: Parse
Extract structured knowledge entries from each agent's output.
Handle format variations — some agents may not return perfect JSON.

### Step 2: Merge
Add new entries to the main knowledge base. Match against existing
entries by topic and claim similarity.

### Step 3: Detect Conflicts
For each new entry, check if it contradicts existing entries.
Use semantic similarity + claim polarity to detect contradictions.

### Step 4: Resolve (or Preserve)
Apply resolution hierarchy:
1. Multiple independent sources (3+) > single source
2. Most recent > older (within same quality tier)
3. Official documentation > blog > opinion
4. Empirical data > theoretical argument
5. **If unresolvable: PRESERVE BOTH as competing positions**

### Step 5: De-duplicate
Compute content signatures. Merge entries that cover the same claim
from the same source. Boost confidence when multiple agents independently
confirm the same finding.

### Step 6: Cross-Reference
Update relationship links between entries. New entries may create
connections that didn't exist before. Validate cross-references.

## Error Handling

| Error | Response |
|-------|----------|
| Agent returns no results | Reduce scope, re-dispatch with simpler query |
| Agent returns contradictory findings | Apply resolution hierarchy; preserve if unresolvable |
| Agent timeout | Split oversized task into smaller agents |
| Duplicate findings across agents | Merge with confidence boost |
| Agent fails to follow output schema | Parse what's usable, flag missing fields |

## Verification Agent Pattern

After collation, dispatch a Verifier agent:

```
Spot-check the following knowledge base entries:
[random 20% selection]

For each entry:
1. Verify the cited source exists and is accessible
2. Verify the source actually supports the stated claim
3. Check if confidence rating matches evidence strength
4. Identify any missing context or caveats
5. Flag any entries that need correction

Return: {verified: [], needs_correction: [], notes: []}
```

## Orchestration Checklist

- [ ] Gap identification completed
- [ ] Agent count determined (budget-aware)
- [ ] Prompts generated (neutral, XML-structured, with output schema)
- [ ] Independent agents launched in SINGLE message (parallel)
- [ ] Results collated (6-step algorithm)
- [ ] Conflicts resolved or preserved
- [ ] Verification agent spot-checked 20%
- [ ] Cross-references updated
