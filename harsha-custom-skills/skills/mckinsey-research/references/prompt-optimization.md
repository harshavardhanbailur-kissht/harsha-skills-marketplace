# Prompt Optimization for Sub-Agents

## Why Prompt Engineering Matters for Sub-Agents

Every sub-agent dispatched by this skill gets a prompt engineered for maximum
research quality. The difference between a naive prompt and an optimized prompt
is dramatic — optimized prompts produce 2-3x more actionable findings with
better source quality and fewer hallucinations.

## Model Selection Decision Tree

| Model | Use When | Strengths |
|-------|----------|-----------|
| Haiku | Simple web searches, pattern finding | Speed, cost efficiency |
| Sonnet | Default for most sub-agents, moderate synthesis | Balance of speed + quality |
| Opus | Deep reasoning, contradiction resolution, high-stakes | Maximum depth and nuance |

**Default**: Use Sonnet for Explorer and Contrarian agents. Use Opus for
Validator agents and final synthesis. Use Haiku only for simple lookups.

## Prompt Structure (XML-Native)

Every sub-agent prompt MUST use XML structure:

```xml
<role>
[Who the agent is — specific, not generic]
[Motivation — why this research matters]
</role>

<context>
[Background information — neutrally framed]
[What has already been researched — avoid duplication]
[Domain context — source hierarchy, decay rate]
</context>

<task>
[Specific research question — ONE clear question]
[Required search types — which of the 6 types apply]
[What to focus on — not "research everything"]
</task>

<constraints>
[Mandatory behaviors — debiasing, triangulation]
[What NOT to do — don't embed bias, don't skip contrarian check]
[Time/scope boundaries]
</constraints>

<output_schema>
[Exact JSON structure for findings]
[Required fields — claim, likelihood, evidence_quality, sources, caveats]
[Maximum length guidance]
</output_schema>

<success_criteria>
[What constitutes a complete, high-quality response]
[Minimum number of sources]
[Required evidence types]
</success_criteria>
```

## Key Prompt Principles

### 1. Role-First Design
Define the role BEFORE the task. This frames all subsequent reasoning.
- BAD: "Research X" (no role context)
- GOOD: "You are a senior research analyst specializing in [domain].
  Your research will inform [specific decision]. Research [X]."

### 2. Neutral Framing (CRITICAL)
Never embed the orchestrator's preferred hypothesis in the prompt.
- BAD: "Research why React is the best choice for our fintech app"
- GOOD: "Research the strengths and weaknesses of React for fintech applications,
  compared to alternatives. Evaluate evidence for AND against."

### 3. Explicit Output Schema
Define exactly what JSON structure the agent must return. This prevents:
- Missing fields
- Inconsistent formatting
- Difficulty merging results from multiple agents

### 4. Disconfirmation Instruction
Every prompt MUST include: "Search for evidence AGAINST the expected answer,
not just evidence supporting it."

### 5. Confidence Metadata Required
Every prompt MUST require: "Tag every claim with both likelihood
(Certain/Highly Likely/Likely/Possible/Unlikely) AND evidence quality
(High/Moderate/Low/Very Low)."

## Extended Thinking Budget Management

When dispatching sub-agents that need deep reasoning:

| Trigger Word | Thinking Depth | Token Budget |
|---|---|---|
| "think" | Low | ~4,000 tokens |
| "think hard" | Medium | ~10,000 tokens |
| "think harder" | High | ~20,000 tokens |
| "ultrathink" | Maximum | ~32,000 tokens |

**When to use maximum thinking**:
- Contradiction resolution between sources
- Complex multi-factor analysis
- High-stakes conclusions with nuanced evidence
- Synthesizing 10+ sources into coherent findings

**When NOT to over-allocate thinking**:
- Simple factual lookups
- Single-source verification
- Straightforward data extraction

## Token Budget Management

```
total_budget = available_context_tokens
search_budget = total_budget * 0.6     # For searching and gathering
synthesis_budget = total_budget * 0.3   # For thinking and synthesizing
output_budget = total_budget * 0.1      # For formatting the response
```

For multi-agent dispatch:
```
tokens_per_agent = (total_context * 0.4) / number_of_agents
reserve_for_collation = total_context * 0.3
```

## Anti-Patterns in Sub-Agent Prompts

- **Embedding bias**: "Research why X is better than Y" (pre-judges outcome)
- **Scope creep**: "Research everything about X" (too broad, shallow results)
- **Missing output schema**: Agent returns unstructured text (hard to merge)
- **No disconfirmation**: Agent only searches for supporting evidence
- **No confidence tags**: Findings have no reliability metadata
- **Over-specification**: Constraining the agent so much it can't discover anything
- **Sequential when parallel**: Launching agents one at a time when they're independent

## Template: Explorer Agent

```xml
<role>
You are a research explorer investigating [specific subtopic].
Your findings will be combined with other researchers' work to build
a comprehensive analysis of [broader topic].
</role>

<context>
[1-3 sentences of background — neutrally framed]
Domain: [domain name]
Source hierarchy: [ordered list for this domain]
Information decay rate: [X months]
</context>

<task>
Research question: [specific, neutral question]
Execute these searches:
1. Primary: [direct search for the topic]
2. Criticism: [search for problems and limitations]
3. Evolution: [search for history and trends]
Find 5-10 high-quality sources. Prioritize [domain-specific authority].
</task>

<constraints>
- Search for evidence AGAINST the expected answer
- Tag every claim with confidence (likelihood + evidence quality)
- Include full source provenance
- Flag contradictions — do NOT resolve them
- Do not use sources older than [decay rate] unless foundational
</constraints>

<output_schema>
{
  "topic": "string",
  "findings": [...],
  "competing_positions": [...],
  "gaps_identified": [...],
  "search_log": [...]
}
</output_schema>
```

## Template: Validator Agent

```xml
<role>
You are a research validator. Your job is to try to DISPROVE the
following claim. Find the strongest evidence against it.
</role>

<context>
Claim to validate: "[specific claim]"
Source of claim: [where it came from]
Current confidence: [likelihood + evidence quality]
</context>

<task>
1. Search for evidence that CONTRADICTS this claim
2. Search for cases where this claim failed or was wrong
3. Check if the cited sources actually support the claim
4. Assess whether the evidence quality rating is appropriate
5. Find the strongest counter-argument
</task>

<output_schema>
{
  "claim": "string",
  "validation_result": "CONFIRMED|WEAKENED|REFUTED|UNCERTAIN",
  "supporting_evidence": [...],
  "contradicting_evidence": [...],
  "recommended_confidence": {...},
  "notes": "string"
}
</output_schema>
```
