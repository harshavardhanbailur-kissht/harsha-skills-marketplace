# Multi-Expert Stress Test — Advisory Board Simulation

## Origin

McKinsey's advisory board (Nobel laureates, leading economists) reviews MGI research
mid-project to challenge narratives and validate findings. They are NOT fact-checkers
but NARRATIVE REFINERS — they stress-test whether the story holds up under scrutiny.

This reference provides sub-agent prompts that simulate this advisory board review.

## The Three Experts

### Expert A: Domain Specialist
**Role**: Deep technical accuracy
**Questions they ask**:
- "Is this technically accurate? Are there nuances being glossed over?"
- "Would a practitioner in this field agree with this characterization?"
- "Are the specific claims backed by evidence from authoritative sources?"
- "Are there domain-specific factors being ignored?"

### Expert B: Skeptic / Red Teamer
**Role**: Find the weakest link
**Questions they ask**:
- "What's the weakest claim in this analysis? Why?"
- "If I wanted to tear this apart, where would I start?"
- "What evidence AGAINST this conclusion was not addressed?"
- "Is this conclusion driven by data or by narrative convenience?"
- "Are we confusing correlation with causation anywhere?"
- "Is survivorship bias affecting our sample?"

### Expert C: Practitioner / Decision-Maker
**Role**: Actionability and real-world applicability
**Questions they ask**:
- "So what? What should someone DO with this information?"
- "Is this actually actionable, or just interesting?"
- "What's missing that a decision-maker would need?"
- "Would this change how I allocate resources?"
- "What are the implementation risks not addressed?"

## Sub-Agent Dispatch Pattern

For Maximum scrutiny tier, spawn three sub-agents simultaneously:

```
Agent 1 (Expert A — Domain Specialist):
"You are a domain expert in [TOPIC]. Review these findings critically:
[INSERT FINDINGS]
Your task: Identify any technical inaccuracies, oversimplifications, or
domain-specific nuances being missed. Be specific. Cite what you find
problematic and what a correction would look like."

Agent 2 (Expert B — Skeptic):
"You are a research skeptic. Your job is to DISPROVE these findings:
[INSERT FINDINGS]
Your task: Search for evidence that CONTRADICTS these conclusions.
Find the weakest claims, identify logical gaps, check for survivorship
bias, correlation-causation confusion, and circular reasoning.
If you cannot find contradicting evidence, say so explicitly."

Agent 3 (Expert C — Practitioner):
"You are a senior executive who must decide whether to act on these findings:
[INSERT FINDINGS]
Your task: Assess actionability. What's missing that you'd need to make
a decision? Are recommendations specific enough? What implementation risks
are not addressed? What would make this 10x more useful?"
```

## Integration Pattern

After all three experts return:
1. Document areas of agreement (strengthen confidence)
2. Document areas of disagreement (preserve as contradictions)
3. For each disagreement, assess which expert's concern is most substantive
4. Update findings to address the strongest critiques
5. Note unresolved disagreements in the "Competing Positions" section

## Pre-Mortem Template

After expert simulation, run the mandatory pre-mortem:

```
"Imagine this research conclusion is WRONG. Imagine it was published
and 6 months later, reality proved it incorrect.

Working backward from that failure:
1. What is the most likely reason it was wrong?
2. What evidence would have predicted this failure?
3. What assumption was incorrect?
4. What data source was unreliable?
5. What alternative explanation was dismissed too quickly?"
```

Document 3-5 specific failure modes with probability assessments.

## When to Use Full Expert Simulation

| Scrutiny Tier | Expert Simulation | Pre-Mortem |
|---|---|---|
| Standard | Skip (not needed for factual lookups) | Skip |
| Enhanced | Run internally (no sub-agents needed) | Mandatory |
| Maximum | Full 3-agent dispatch + synthesis | Mandatory |

## CIA Structured Analytic Techniques Integration

### Devil's Advocacy (Beyond Skeptic Expert)
Formal structured opposition — not just criticism, but building the strongest
possible counter-case:
1. State the consensus conclusion explicitly
2. Build comprehensive counter-argument independently
3. Present with equal standing (not subordinate to main analysis)
4. Discuss merits of both positions
5. Revise conclusions where counter-argument identifies legitimate gaps

### Red Team Analysis (Full Independent Analysis)
For Maximum tier, go beyond Devil's Advocacy:
1. Red team develops INDEPENDENT analysis (not just critique)
2. Systematic assumption inversion: "Assume the opposite — is it defensible?"
3. Adversarial perspective: "What evidence would I need to disprove this?"
4. Generate alternative scenarios inconsistent with consensus
5. Stress-test: "Under what conditions does this analysis fail?"

### Key Assumptions Check (Before Stress Test)
1. Write down the analytical conclusion explicitly
2. List ALL premises — stated AND unstated
3. For each assumption: "Why MUST this be true? Under what conditions does it fail?"
4. Refine to core assumptions that MUST be true for conclusion to hold
5. These become the monitoring signposts

### Source Reliability Matrix (NATO Admiralty Code)
Rate each source on two dimensions:

**Source Reliability**: A (completely reliable) → F (cannot be judged)
**Information Credibility**: 1 (confirmed) → 6 (cannot be judged)

| Source Type | Typical Rating | Rationale |
|---|---|---|
| Peer-reviewed journal | B-C | Reviewed but variability exists |
| Official documentation | A-B | Highest editorial standards |
| Pre-print (ArXiv) | C-D | No external review |
| Company blog | D-E | Conflict of interest |
| LLM-generated summary | E-F | Unverified synthesis |
| Independent benchmark | B | Likely to expose limitations |

## Extended Panel (Maximum Tier)

Add two more experts for comprehensive coverage:

### Expert D: Security / Risk Specialist
**Questions**: "What are the vulnerabilities? What regulatory risks exist?
What data privacy concerns? What's the worst-case failure mode?"

### Expert E: Performance / Cost Engineer
**Questions**: "What are the bottlenecks? What's the total cost of ownership?
Does this scale? What happens under 10x load?"

## Tree of Thoughts (Structured Exploration)

For genuinely complex analysis, beyond expert simulation:
- Explore multiple reasoning paths simultaneously
- Evaluate each path before committing
- Backtrack when a path fails
- Score branches by evidence strength

**Empirical data** (NeurIPS 2023): Tree of Thoughts achieves 74% success
vs. 4% for Chain-of-Thought on complex reasoning tasks (18.5x improvement).
Use ToT when the analysis has multiple plausible paths with non-obvious tradeoffs.

## Anti-Patterns

- Don't launch biased expert prompts ("confirm that our finding is correct")
- Don't dismiss Expert B (skeptic) findings as "nitpicking"
- Don't skip Expert C (practitioner) — actionability IS quality
- Don't treat expert simulation as formality — integrate findings genuinely
- Don't resolve contradictions between experts silently — document them
- Don't confuse Devil's Advocacy (critique) with Red Team (independent analysis)
- Don't skip Key Assumptions Check — unstated assumptions are the #1 failure mode
