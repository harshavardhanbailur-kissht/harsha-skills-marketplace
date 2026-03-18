# Fact-Checking Pipeline

## Purpose

Structured claim verification following IFCN (International Fact-Checking Network)
principles. Provides a triage system for deciding HOW deeply to verify claims, and
a multi-level verification procedure for each depth.

## IFCN Core Principles

1. **Nonpartisanship and Fairness** — Check claims regardless of who makes them
2. **Transparency of Sources** — Document where verification evidence comes from
3. **Transparency of Funding** — Note potential financial biases in sources
4. **Transparency of Methodology** — Document HOW claims were verified
5. **Open and Honest Corrections** — When findings change, document the change

## Claim Triage (Before Investigation)

Not all claims need deep verification. Triage first:

### Categorize the Claim
| Category | Example | Verification Need |
|----------|---------|------------------|
| Factual | "Revenue was $5.2B in 2024" | Verifiable — check |
| Opinion | "This is the best approach" | Not fact-checkable — label as opinion |
| Prediction | "Market will grow 30%" | Check methodology, not truth value |
| Statistical | "45% of users prefer X" | Check source, methodology, sample |
| Technical | "Library X supports feature Y" | Verify against official docs |
| Regulatory | "RBI mandates X" | Verify against official circular |

### Assess Verifiability
- **Fully verifiable**: Can be checked against primary sources
- **Partially verifiable**: Core claim checkable, but details uncertain
- **Unverifiable**: No accessible primary source exists — flag explicitly

### Evaluate Impact
- **High impact**: Claim shapes a key finding or recommendation
- **Medium impact**: Claim supports but doesn't define a finding
- **Low impact**: Background context, peripheral detail

**Triage decision**: Impact x Verifiability determines verification depth:
- High impact + fully verifiable = Level 3-4
- High impact + partially verifiable = Level 2-3
- Medium/Low + verifiable = Level 1-2
- Any + unverifiable = Label as unverifiable, don't present as fact

## Verification Levels

### Level 1: Quick Check (5 minutes)
**When**: Low-impact factual claims, background context
**Procedure**:
1. Does the cited source actually contain this claim?
2. Is the source a reasonable authority for this type of claim?
3. Is the information current (within domain decay rate)?

**Pass criteria**: Source exists, contains claim, is reasonably authoritative.

### Level 2: Moderate Verification (15 minutes)
**When**: Medium-impact claims, statistical claims
**Procedure**:
1. All Level 1 checks
2. Find a second independent source confirming the claim
3. Check for obvious contradictions from other sources
4. Verify statistical methodology if applicable (sample size, methodology)
5. Check if the claim has been corrected or updated since publication

**Pass criteria**: 2+ independent sources agree, no obvious contradictions.

### Level 3: Deep Verification (30+ minutes)
**When**: High-impact claims, key findings, regulatory claims
**Procedure**:
1. All Level 2 checks
2. Trace claim to its PRIMARY source (not secondary citations)
3. Read the primary source in full context (not just the cited sentence)
4. Check for qualifications, caveats, and conditions in the primary source
5. Search for contradictions: "[claim] criticism" + "[claim] debunked"
6. Verify the claim hasn't been superseded by newer information
7. Check for circular citation patterns

**Pass criteria**: Primary source verified, context preserved, no contradictions.

### Level 4: Expert Consultation (simulate)
**When**: Critical claims that shape major conclusions, novel/surprising claims
**Procedure**:
1. All Level 3 checks
2. Run multi-expert simulation (Domain specialist + Skeptic + Practitioner)
3. Each expert independently evaluates the claim
4. Document expert consensus or disagreement
5. If experts disagree, preserve the disagreement in output

**Pass criteria**: Expert panel consensus, or documented disagreement.

## Primary Source Hunt

For every important claim, trace the citation chain:

```
Blog post says "X" → citing news article → citing analyst report → citing survey
                                                                         ^
                                                                 PRIMARY SOURCE
```

**Procedure**:
1. Start with the claim as cited
2. Follow the citation/reference to its source
3. Follow THAT source's citation to ITS source
4. Continue until you reach the primary (original) source
5. Read the primary source in context
6. Verify the claim survived the citation chain accurately

**Common distortions in citation chains**:
- Nuanced finding becomes absolute claim
- Conditional result becomes universal truth
- Correlation becomes causation
- Specific context becomes general rule
- Preliminary finding becomes established fact

## Circular Source Detection

**What**: Sources that appear independent but trace to the same origin.

**Detection procedure**:
1. Map citation chain for each source supporting a claim
2. If chains converge to the same original, they're NOT independent
3. Check for the "Wikipedia citogenesis" pattern:
   - False/unsourced claim added to Wikipedia
   - News sites cite Wikipedia
   - Wikipedia cites the news sites back
   - Claim appears "well-sourced" but is entirely circular

**Red flags for circular sources**:
- Multiple sources all published within a short time window
- All sources use the same specific statistic or phrasing
- None of the sources cite original research or primary data
- Sources cite each other but not an external authority

## Correction Protocol

When verification reveals an error:

1. **Document the error**: What was wrong, how it was discovered
2. **Identify impact**: What other findings depend on this claim?
3. **Correct or remove**: Update the claim with corrected information
4. **Update confidence**: Lower confidence tags for affected findings
5. **Note in output**: Add to "Corrections" section if the error was significant
6. **Check cascade**: Verify no downstream conclusions rest on the error

## Source Reliability Assessment

For each source, assess:

| Factor | Weight | Assessment |
|--------|--------|-----------|
| Author credentials | 20% | Verifiable expertise in this domain? |
| Publication quality | 20% | Peer-reviewed? Reputable outlet? |
| Methodology transparency | 20% | Is the methodology explained? |
| Potential conflicts | 15% | Financial interests? Sponsorship? |
| Track record | 15% | Has this source been accurate historically? |
| Currency | 10% | Is this information current? |

**Reliability score**: Weighted sum (0-100)
- 80-100: HIGH — use with confidence
- 60-79: MODERATE — use with caveats
- 40-59: LOW — corroborate with better sources
- 0-39: VERY LOW — don't use as primary evidence
