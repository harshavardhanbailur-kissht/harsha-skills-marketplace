# Gap Analysis Engine

## Purpose

Before writing output, systematically check for holes in the research.
This prevents delivering incomplete analysis with false confidence.

## 4 Gap Types

### 1. Coverage Gaps
Topics that are mentioned or referenced but never explained.
- **Detection**: Extract all proper nouns, key terms, and references from findings.
  Cross-reference against the list of topics with dedicated analysis.
- **Severity**: HIGH if referenced 5+ times without explanation. MEDIUM if 2-4 times.
- **Example**: Report mentions "MECE decomposition" 8 times but never defines it.

### 2. Depth Gaps
Entries exist but lack sufficient substance.
- **Detection**: Flag any finding with <100 words of supporting evidence.
  Flag any finding with only 1 source.
- **Severity**: HIGH if the finding is a key claim. LOW if peripheral.
- **Example**: "Company X has strong market position" with no data to support it.

### 3. Conflict Gaps
Contradictory information exists without resolution or acknowledgment.
- **Detection**: Compare claims across findings. Flag when Finding A contradicts
  Finding B and neither is tagged as a competing position.
- **Severity**: CRITICAL if both claims are key findings. MEDIUM if peripheral.
- **Example**: Finding 1 says market is growing; Finding 3 says market is declining.

### 4. Assumption Gaps
Unstated prerequisites that the analysis depends on but doesn't document.
- **Detection**: For each conclusion, ask "what must be true for this to hold?"
  Check if those prerequisites are stated and evidenced.
- **Severity**: HIGH if the assumption is questionable. LOW if universally accepted.
- **Example**: Assumes regulatory environment remains stable, but doesn't state this.

## Gap Severity Scoring

```
severity = (impact * 0.6) + (difficulty * 0.3) + (recency * 0.1)
```

Where:
- **impact** (1-5): How much does this gap affect the overall conclusion?
- **difficulty** (1-5): How hard is this gap to fill? (5 = very hard)
- **recency** (1-5): How time-sensitive is this gap? (5 = very urgent)

Score interpretation:
- 4.0-5.0: CRITICAL — must fill before delivery
- 3.0-3.9: HIGH — should fill if time permits
- 2.0-2.9: MEDIUM — document as limitation
- 1.0-1.9: LOW — note for future research

## Gap Detection Algorithm

1. **Extract all references**: Capitalized terms, proper nouns, acronyms,
   technologies, companies, frameworks mentioned anywhere in findings.

2. **Build topic index**: List all topics that have dedicated analysis.

3. **Cross-reference**: For each reference, check if it has dedicated analysis.
   If referenced 3+ times without analysis, flag as coverage gap.

4. **Depth check**: For each analyzed topic, measure evidence depth.
   <100 words OR <2 sources = depth gap.

5. **Conflict scan**: Compare all key claims pairwise. Flag contradictions
   without competing-position documentation.

6. **Assumption audit**: For each conclusion, list implicit assumptions.
   Flag any that aren't stated and evidenced.

## Coverage Calculation

```
coverage = (addressed_topics / total_identified_topics) * 100
```

| Scrutiny Tier | Minimum Coverage | Action if Below |
|---|---|---|
| Standard | 70% | Document gaps as limitations |
| Enhanced | 85% | Attempt to fill critical gaps |
| Maximum | 95% | Launch additional sub-agents for unfilled gaps |

## Saturation Detection

Track diminishing returns during research:

```
saturation_ratio = new_insights_this_round / search_cost_this_round
```

- If saturation_ratio < 0.1: Research is saturated, stop searching
- If saturation_ratio 0.1-0.3: Marginal returns, consider stopping
- If saturation_ratio > 0.3: Still productive, continue

**Domain-specific saturation thresholds**:
- Well-documented topics (React, Python): saturate quickly (3-5 search rounds)
- Niche topics: may need 10+ rounds before saturation
- Contradictory topics: may never fully saturate — set time limit

## Remaining Gap Documentation

For each unfilled gap, document in the output:

```
## Gaps & Limitations

### Unfilled Gap: [topic]
- **Type**: [Coverage / Depth / Conflict / Assumption]
- **Severity**: [score] ([Critical / High / Medium / Low])
- **Why unfilled**: [sources unavailable / time constraint / out of scope]
- **Impact on conclusions**: [how this gap affects reliability]
- **Recommended next steps**: [what research would fill this gap]
```

## Integration with Phases

| Phase | Gap Analysis Action |
|-------|-------------------|
| Phase 1 (Scope) | Identify expected topics — set initial coverage target |
| Phase 3 (Search) | Track which topics have been addressed by searches |
| Phase 5 (Synthesis) | Run full gap detection algorithm |
| Phase 7 (Gap Analysis) | Calculate coverage, severity score, saturation |
| Phase 8 (Output) | Document all remaining gaps in output |
| Phase 9 (QA) | Verify gap documentation is complete |
