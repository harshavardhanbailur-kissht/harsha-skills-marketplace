# Evidence Synthesis — From Raw Findings to Validated Claims

## Triangulation Requirements

Every factual claim presented as established needs **minimum 2 independent sources**.

| Claim Type | Min Sources | Validation Method |
|---|---|---|
| Factual statement | 2 independent | Source triangulation |
| API/library behavior | Official docs + 1 example | Direct verification |
| Performance claim | 2 independent benchmarks | Methodological triangulation |
| Security claim | Official advisory + expert | Authority + lateral reading |
| Regulatory claim | Official regulator source | Primary source verification |
| Best practice | 3+ authoritative sources | Community consensus check |
| "X > Y" comparison | Controlled comparison + 2 opinions | Competitive analysis mode |

If only 1 source exists: tag as **"single-source claim — lower confidence"**.

## Confidence Tagging System

Two SEPARATE dimensions (never conflate):

### Likelihood (How probable is this claim?)
- **Certain**: No reasonable doubt; multiple authoritative sources agree
- **Highly Likely**: Strong evidence, minor caveats
- **Likely**: Preponderance of evidence supports it; some gaps
- **Possible**: Some evidence supports it; significant uncertainty
- **Unlikely**: Evidence is weak or contradictory

### Evidence Quality (How good is the supporting evidence?)
- **High**: Official sources, peer-reviewed, independently verifiable
- **Moderate**: Credible secondary sources, expert opinions, well-sourced blogs
- **Low**: Single source, unverifiable claims, forum posts, promotional content
- **Very Low**: No verifiable source, speculation, AI-generated without validation

**Example combinations:**
- "AI adoption reached 78% in enterprises" — Likelihood: Highly Likely, Evidence: High (McKinsey survey, 33K respondents)
- "React will be obsolete by 2028" — Likelihood: Unlikely, Evidence: Low (blog speculation)
- "Quantum computing will transform finance" — Likelihood: Likely, Evidence: Moderate (expert opinions + early use cases)

## Diagnostic Evidence Evaluation (ACH)

From Analysis of Competing Hypotheses:

**Focus on evidence that DIFFERENTIATES between hypotheses**, not evidence
that merely confirms one.

- "This supports H1" = mildly useful
- "This supports H1 AND contradicts H2" = DIAGNOSTIC — much more valuable
- "This is consistent with all hypotheses" = non-diagnostic — ignore for ranking

The most likely hypothesis has the **LEAST evidence against it**,
not the most evidence for it.

## Mandatory Contrarian Check

For EVERY major finding, explicitly search for:
- "criticism of [finding]"
- "problems with [finding]"
- "alternatives to [finding]"
- "[finding] is wrong"

This cannot be skipped for Enhanced or Maximum scrutiny tiers.

If contrarian evidence exists: **document it in Competing Positions**.
If contrarian evidence does NOT exist: **note the absence explicitly**.

## Synthesis Trap Detection

Watch for these failure modes:
1. **Conclusion no individual source supports**: Combining sources A and B
   to produce claim C that neither A nor B actually makes
2. **Cherry-picking**: Selecting only supporting evidence, ignoring contradictions
3. **Circular sources**: "Independent" sources that trace to the same original
4. **Vendor-sponsored evidence**: "Research" that is actually marketing
5. **Temporal mismatch**: Combining findings from different time periods
   without acknowledging that conditions may have changed

## Circular Source Detection

1. Trace every claim to its PRIMARY (original) source
2. Check if "independent" sources share the same original
3. Look for Wikipedia citogenesis (false info → Wikipedia → cited as fact)
4. Verify citations actually support the claims attached to them
5. If two sources cite each other: they count as ONE source, not two

## Denzin's Four Types of Triangulation

Go beyond simple source-counting. Use structured triangulation:

### Type 1: Data Triangulation
Multiple sources across three dimensions:
- **Time**: Data from different time periods (not just latest)
- **Space**: Data from different geographies/contexts
- **Persons**: Data from different stakeholder groups
Convergences across all three dimensions = strongest evidence.

### Type 2: Investigator Triangulation
Multiple independent analysts examine the same evidence:
- In AI context: dispatch parallel sub-agents with identical data
- Compare findings independently before synthesis
- Agreements boost confidence; disagreements require investigation

### Type 3: Methodological Triangulation
Different methods applied to the same question:
- **Within-method**: Multiple search strategies on same topic
- **Between-method**: Combine quantitative data + qualitative analysis
- Method-specific artifacts become visible through comparison

### Type 4: Theory Triangulation
Competing theoretical frameworks interpreting the same data:
- Analyze findings through 2+ different analytical lenses
- Example: Evaluate a market through Porter's Five Forces AND through
  resource-based view — do they agree?
- Convergence across theories = robust finding

## GRADE Evidence Grading

For formal evidence quality assessment (Maximum scrutiny tier):

### Four Certainty Levels
- **HIGH**: Very confident. Further research unlikely to change assessment
- **MODERATE**: Moderately confident. Further research could change assessment
- **LOW**: Low confidence. Further research very likely to change assessment
- **VERY LOW**: Any estimate is highly uncertain

### Six Downgrade Factors
Starting from baseline, downgrade certainty for:
1. **Risk of bias**: Design flaws, incomplete data, selective reporting
2. **Inconsistency** (I²>75%): Large variability across sources not explained
3. **Indirectness**: Evidence doesn't directly address the question at hand
4. **Imprecision**: Wide confidence intervals, small sample sizes
5. **Publication bias**: Missing contrary evidence, asymmetric evidence base
6. **Other**: Violation of assumptions, unclear relationships

### AI Research Adaptation
AI research starts at VERY LOW baseline (not HIGH like clinical trials):
- Downgrade for: no version control, non-deterministic results, code unavailable
- Upgrade for: replicated across models, multiple independent benchmarks, code released

## Handling Heterogeneous Evidence

When sources use different methods, measures, or contexts:

1. **Don't force meta-analysis**: If sources are too different, use narrative synthesis
2. **Stratify by methodology**: Group findings by study type before comparing
3. **Subgroup analysis**: Pre-specify groupings (by model type, domain, benchmark)
4. **Sensitivity analysis**: Test if conclusions change when assumptions vary
5. **Report heterogeneity explicitly**: "These findings varied because [specific reasons]"

## The Synthesis Process

1. **Organize by hypothesis**: Group evidence under each competing hypothesis
2. **Apply Denzin's triangulation**: Check data, investigator, method, theory convergence
3. **Identify diagnostic evidence**: Which evidence differentiates hypotheses?
4. **Apply ACH**: Which hypothesis has the least evidence against it?
5. **Grade evidence (GRADE)**: Assign certainty level with explicit downgrade rationale
6. **Tag confidence**: Assign likelihood + evidence quality to each finding
7. **Preserve contradictions**: Don't resolve — document both sides
8. **Run contrarian check**: Search for criticism of major findings
9. **Handle heterogeneity**: Stratify, run subgroup analysis, report variation
10. **Build evolution narrative**: How did we get here? Where is it going?
