# Temporal Validity System

## Why Temporal Validity Matters

Information decays. A perfectly valid finding today may be wrong in 6 months.
Different domains decay at different rates. This reference provides the framework
for tagging every finding with its expected lifespan and refresh triggers.

## Domain-Specific Decay Rates

| Domain | Half-Life | Decay Driver | Example |
|--------|-----------|-------------|---------|
| Security/vulnerabilities | Days-weeks | CVE disclosure, patches | "Library X is secure" |
| Software APIs | 3-6 months | Minor/major releases | "Use method X()" |
| Software frameworks | 6-18 months | Major version releases | "React best practice is..." |
| Fintech regulations (India) | ~6 months | RBI/SEBI circulars | "P2P lending limit is..." |
| ML/AI benchmarks | 6-12 months | New model releases | "GPT-4 leads on benchmark X" |
| UI/UX patterns | 18-36 months | New browser capabilities | "Hamburger menu is standard" |
| Business/economics | 3-5 years | Market shifts, disruptions | "Market size is $X billion" |
| Academic research | 5-10 years | Replication studies | "Study shows 30% improvement" |
| Legal/regulatory (general) | 12-36 months | New legislation | "GDPR requires..." |
| Mathematics/formal proofs | Indefinite | Never | "Algorithm X is O(n log n)" |
| Medical/health | 18-24 months | Clinical trial updates | "Treatment X is effective" |

## Temporal Tagging Procedure

Every finding in the output gets FOUR temporal metadata fields:

### 1. `knowledge_as_of`
The date of the most recent source supporting this finding.
- Use the ACTUAL publication/access date, not today's date
- If source has no date, flag as "undated source — treat as potentially stale"

### 2. `valid_until`
Estimated expiration date = `knowledge_as_of` + domain half-life.
- Software API: knowledge_as_of + 6 months
- Framework: knowledge_as_of + 12 months
- Regulation: knowledge_as_of + 6 months
- Security: knowledge_as_of + 30 days

### 3. `review_triggers`
Specific events that would invalidate this finding:
- "Major version release of [framework]"
- "New RBI circular on [topic]"
- "CVE disclosed for [library]"
- "Replication study published for [paper]"
- "Competitor launches [product]"

### 4. `temporal_dependencies`
Which other findings depend on this one being current:
- If finding A depends on finding B, and B expires, A must be re-evaluated
- Create a dependency graph for complex reports

## Decay Signal Detection

Watch for these indicators that information may be stale:

**Software Domain:**
- Version numbers in sources don't match current releases
- API methods mentioned in sources return deprecation warnings
- Release notes mention breaking changes since source date
- npm/PyPI shows newer major versions

**Business Domain:**
- Market size figures are 2+ years old
- Competitive landscape has changed (M&A, new entrants)
- Economic conditions have shifted significantly
- Regulatory environment has changed

**Academic Domain:**
- Replication attempts have been published
- Meta-analyses include newer studies
- Methodological criticisms have emerged
- Sample populations may no longer be representative

## Knowledge Refresh Workflow

When a finding approaches or passes its `valid_until`:

1. **Quick check**: Is the core claim still supported by current sources?
2. **Version check**: Has the subject (framework, regulation, etc.) been updated?
3. **Contradiction check**: Have new findings emerged that contradict?
4. **Re-tag**: Update temporal metadata with new dates
5. **Branch if needed**: Keep old version + new version if significantly different

## Integration with Scrutiny Tiers

| Tier | Temporal Requirement |
|------|---------------------|
| Standard | Tag `knowledge_as_of` on key findings |
| Enhanced | Full temporal tagging on all findings + review triggers |
| Maximum | Full tagging + dependency graph + active staleness detection |

## Staleness Severity

| Status | Meaning | Action |
|--------|---------|--------|
| Fresh | Within half-life period | Use confidently |
| Aging | 50-100% of half-life elapsed | Note in caveats |
| Stale | Past half-life | Explicit warning + refresh recommended |
| Expired | 2x past half-life | Do not use without re-verification |
