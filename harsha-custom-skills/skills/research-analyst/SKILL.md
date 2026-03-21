---
name: research-analyst
description: "Epistemic research engine that transforms how Claude researches ANY topic. Embeds procedural debiasing, source validation, and quality gates directly into the research workflow as mandatory checkpoints. 7-phase pipeline: scope, hypotheses, systematic search, source validation, evidence synthesis, contradiction analysis, structured output. Use when researching topics, evaluating libraries/frameworks/tools, competitive analysis, validating claims, comparing technologies, or doing thorough research on any subject."
---

# Research Analyst

Epistemic research engine that transforms how Claude researches ANY topic. Embeds procedural debiasing, source validation, and quality gates directly into the research workflow — not as awareness statements, but as mandatory checkpoints that cannot be skipped.

## Why This Skill Exists

Replaces Claude's default "search-summarize-present" pattern with structured debiasing, mandatory validation checkpoints, and full provenance tracking.

## Core Principles

- Procedural debiasing at every phase
- Source validation as mandatory gates
- Competing hypotheses before conclusions
- Full provenance tracking with inline citations
- Contradiction analysis before presenting findings

## How It Works — 7-Phase Research Workflow

### Phase 1: SCOPE & DECOMPOSE

Break the research question into MECE sub-questions. Define what counts as evidence. Set scope boundaries.

### Phase 2: GENERATE COMPETING HYPOTHESES

Before searching, generate multiple competing hypotheses. This prevents confirmation bias by ensuring Claude looks for evidence against initial assumptions.

### Phase 3: SYSTEMATIC SEARCH

Structured search across multiple source types. Each source gets a reliability rating. Search strategy documents what was NOT found as well.

### Phase 4: SOURCE VALIDATION

Mandatory checkpoint — every source must pass validation:
- Authority: Who created this? What's their expertise?
- Recency: When was this published? Is it still valid?
- Corroboration: Do independent sources confirm this?
- Bias check: What perspective does this source represent?

### Phase 5: EVIDENCE SYNTHESIS

Map evidence to hypotheses. Weight by source quality. Identify gaps in evidence.

### Phase 6: CONTRADICTION ANALYSIS & PRE-MORTEM

Actively seek contradicting evidence. Run pre-mortem: "Imagine this conclusion is wrong — what would have caused that?"

### Phase 7: STRUCTURED OUTPUT

Present findings with:
- Confidence levels for each claim
- Inline citations with provenance
- Explicit uncertainty markers
- Competing interpretations where evidence is ambiguous

## Specialized Research Modes

| Mode | When to Use |
|------|------------|
| **Technology Evaluation** | Evaluating libraries, frameworks, tools |
| **Competitive Analysis** | Analyzing competitive landscape |
| **Fintech Research** | Financial technology domain research |
| **Skill Creation Research** | Researching best practices for new skills |
| **Claim Verification** | Fact-checking specific claims |

## V2.0 Enhancements

- **Inline Citation Standard**: Every factual claim tagged with source
- **Write-Time Citation Gate (Phase 7.5)**: Blocks uncited claims before output
- **Retroactive Audit Mode**: Verify citations in existing documents

## Sub-Agent Research Dispatch

For large research tasks, dispatch sub-agents to research sub-questions in parallel, then synthesize results.

## Reference Files

| Reference | Purpose |
|-----------|---------|
| `references/` | Core methodology, expanded knowledge base, domain-specific references |
| `templates/` | Output templates for structured findings |
| `research/` | Research data and findings |
| `evals/` | Evaluation criteria and results |

## Anti-Patterns — What NOT to Do

- Do not skip validation phases to save tokens
- Do not present first-found results as conclusions
- Do not ignore contradicting evidence
- Do not claim certainty without corroboration
- Do not use single-source conclusions

## Integration with Other Skills

- **Deep Research**: Complementary — deep-research for synthesis, research-analyst for validation
- **McKinsey Research**: research-analyst provides evidence, McKinsey structures the narrative
- **Deep Thinker**: research-analyst feeds validated findings into deep thinking

## Quick-Start Decision Tree

- Need to research something? → Start Phase 1
- Evaluating a technology? → Use Technology Evaluation mode
- Fact-checking a claim? → Use Claim Verification mode
- Comparing options? → Phase 2 (competing hypotheses) is critical

---

*Research Analyst v2.0 — Epistemic research with mandatory validation gates*
