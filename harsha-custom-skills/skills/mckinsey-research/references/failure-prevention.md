# Failure Prevention & QA Pipeline

## Why This Exists

AI research has documented failure modes. 5.2% of AI code references hallucinated
packages. 45% of AI-generated code has security vulnerabilities. 58.4% of Stack
Overflow answers are obsolete when posted. This reference provides the QA pipeline
that catches these failures BEFORE they reach the output.

## 6-Stage QA Pipeline

Run ALL stages before delivering ANY research output.

### Stage 1: Hallucination Detection
**What**: Spot-check claims against their cited sources.
**Procedure**:
1. Randomly select 20% of claims in the output
2. For each: re-read the cited source
3. Verify the claim is ACTUALLY supported (not just mentioned)
4. Check for subtle distortions (correct fact, wrong context)
5. Flag any claim where source doesn't fully support the assertion

**Common hallucination patterns**:
- Correct statistic, wrong source
- Real company, fabricated product
- Existing concept, invented details
- Plausible but non-existent citation

### Stage 2: Circular Source Detection
**What**: Verify that "independent" evidence chains are truly independent.
**Procedure**:
1. For each finding with 2+ sources, trace each to its PRIMARY origin
2. Map the citation chain: Source A cites -> Source B cites -> Original
3. If multiple sources trace to the same original, they are NOT independent
4. Flag as "single-source with multiple citations" (not triangulated)
5. Check for Wikipedia citogenesis (false claim -> Wikipedia -> cited as fact)

### Stage 3: API/Package Existence Verification
**What**: If research references any code, verify packages/APIs exist.
**Procedure**:
1. Extract all package names, API endpoints, and function references
2. Verify each exists in the official registry (npm, PyPI, etc.)
3. Check version compatibility (does the referenced version exist?)
4. Verify API endpoints are current (not deprecated or removed)

**Slopsquatting risk**: 5.2% of AI-recommended packages don't exist.
Attackers register these names with malicious code.

### Stage 4: Deprecated Library Detection
**What**: Check that all technology references are current.
**Procedure**:
1. For each library/framework referenced, check the latest version
2. Compare referenced version to current stable release
3. Flag any with deprecation warnings or "use X instead" notices
4. Check if APIs mentioned still exist in current versions
5. Verify migration paths exist if deprecated

**Known risk**: 68% of AI-generated code uses deprecated libraries.
31% reference libraries with unpatched CVEs.

### Stage 5: Knowledge Staleness Assessment
**What**: Compare findings against domain-specific decay rates.
**Procedure**:
1. For each finding, check `knowledge_as_of` against current date
2. Apply domain-specific half-life (see temporal-validity.md)
3. Flag any finding past its half-life as "potentially stale"
4. For stale findings, attempt a quick refresh search
5. If refresh contradicts original finding, update or flag

### Stage 6: Evidence Integrity Audit
**What**: Final integrity check on the evidence chain.
**Procedure**:
1. Verify sources actually support the claims they're cited for
2. Check that confidence tags match actual evidence strength
3. Verify contradictions are preserved (not silently resolved)
4. Check that caveats are present for every major claim
5. Ensure provenance chain is complete (no orphaned claims)

## Known Failure Patterns

### 1. Slopsquatting (Critical)
- 5.2% of commercial AI-generated packages, 21.7% of open-source
- Attackers register hallucinated package names with malware
- **Prevention**: Always verify package existence before referencing

### 2. Deprecated-but-Popular
- AI generates deprecated APIs because they dominate training data
- 68% of AI code uses deprecated libraries
- **Prevention**: Version check against current releases

### 3. Circular Citations
- Sources cite each other without independent primary evidence
- Creates illusion of triangulation
- **Prevention**: Trace every claim to its primary source

### 4. Vendor-Sponsored "Comparisons"
- Marketing disguised as independent research
- Often appears on seemingly neutral tech blogs
- **Prevention**: Check for disclosure, sponsorship, affiliate links

### 5. Survivorship Bias
- Only successful cases get documented and indexed
- Creates false impression of success rates
- **Prevention**: Explicitly search for failures and post-mortems

### 6. Model Update Fragility
- Research/skills that work with one model version may break with next
- API changes, capability changes, behavior changes
- **Prevention**: Pin to specific model versions, add update triggers

### 7. 45% Security Failure Rate
- Nearly half of AI-generated code has security vulnerabilities
- 70%+ in Java specifically
- **Prevention**: Cross-reference security practices, don't trust AI security code

### 8. Multi-Agent Coordination Failures
- 41-86.7% of multi-agent systems fail in production
- Results may be incomplete, contradictory, or lost
- **Prevention**: Verification checkpoints between agents, collation audit

## Knowledge Translation Framework (CIHR Model)

When research feeds into downstream work (skills, code, decisions):

### Stage 1: Knowledge Creation
- Systematic review synthesis of all findings
- Quality assessment of evidence base
- Gap identification

### Stage 2: Adaptation
- Contextual customization for target use case
- Actionability filtering (can this become a procedure?)
- TRL gating (only include findings with working examples)

### Stage 3: Implementation
- Convert findings to actionable instructions
- Maintain provenance chain (every instruction traces to evidence)
- Add failure mode documentation

### Stage 4: Evaluation
- Monitor usage and outcomes
- Track failure incidents against predicted failure modes
- Update evidence when new information emerges

## QA Checklist (Quick Reference)

Before ANY delivery:
- [ ] 20% of claims spot-checked against sources (Stage 1)
- [ ] Circular sources identified and flagged (Stage 2)
- [ ] All code references verified to exist (Stage 3)
- [ ] No deprecated libraries/APIs without warning (Stage 4)
- [ ] No findings past domain half-life without warning (Stage 5)
- [ ] Provenance chain complete (Stage 6)
- [ ] Confidence tags match actual evidence (Stage 6)
- [ ] Contradictions preserved (Stage 6)
