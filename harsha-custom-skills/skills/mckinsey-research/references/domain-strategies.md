# Domain-Specific Research Strategies

## Why Domain Strategies Matter

Different domains have different authoritative sources, decay rates, red flags,
and research patterns. Using a generic research approach across all domains
produces shallow, unreliable results. This reference provides domain-specific
protocols for the 6 most common research domains.

## Domain 1: Software Engineering

**Source Hierarchy** (most to least authoritative):
1. Official documentation (docs, specs, RFCs)
2. Source code and changelogs
3. GitHub issues and discussions (from maintainers)
4. MDN Web Docs (for web technologies)
5. Established tech blogs (official engineering blogs)
6. Stack Overflow (with 58.4% obsolescence caveat)
7. Tutorial sites and personal blogs (verify against official docs)

**Decay Rate**: 6-18 months for frameworks; 3-6 months for APIs

**Production Viability Signals** (more valuable than stars):
- npm/PyPI dependent count (strongest single indicator)
- Release cadence and recency
- Issue response time (maintainer health)
- Contributor count and retention
- Fork-to-star ratio (>=1:10 = active usage)
- OpenSSF Scorecard (if available)

**Red Flags**:
- No commits in 6+ months (potential abandonment)
- README says "use X instead" (deprecated)
- Only 1-2 contributors (bus factor risk)
- No test suite or CI/CD
- Security vulnerabilities in dependency chain

**Search Pattern**:
1. Official docs first (always)
2. GitHub repo health check
3. npm/PyPI package page (download trends, dependents)
4. "alternatives to [X]" + "[X] vs [Y]"
5. "[X] production issues" + "[X] migration"

## Domain 2: Business & Market Research

**Source Hierarchy**:
1. Company filings (10-K, annual reports, investor presentations)
2. Industry associations and trade bodies
3. Government statistics (census, BLS, national statistical offices)
4. Analyst reports (Goldman Sachs, McKinsey, Gartner — with bias awareness)
5. Industry publications (trade journals)
6. Business news (FT, WSJ, Bloomberg)
7. Company press releases (promotional — verify independently)

**Decay Rate**: 3-5 years for market sizing; 1-2 years for competitive landscape

**Red Flags**:
- Market size figures without methodology
- "The market will reach $X billion" without named source
- Competitor analysis from one competitor's website
- Surveys with <500 respondents presented as definitive
- Survivorship bias (only successful case studies)

**Search Pattern**:
1. Official filings and financial data
2. Industry association reports
3. Multiple analyst estimates (compare, don't cherry-pick)
4. "[industry] market failure" + "[industry] challenges"
5. Regulatory landscape check

## Domain 3: Fintech & Regulatory

**Source Hierarchy**:
1. Official regulator sites (RBI, SEBI, IRDAI, IFSCA)
2. Official gazettes and regulatory circulars
3. Law firm analysis (Cyril Amarchand, AZB, Khaitan)
4. Industry body publications (FIDC, IBA, NASSCOM)
5. Fintech industry reports (BCG, Redseer, Inc42)
6. Fintech blogs and news (with heavy verification)

**Decay Rate**: ~6 months (regulatory changes are frequent)

**Critical Rules**:
- ALWAYS check official regulator sites FIRST
- Distinguish "technically possible" from "legally permitted"
- Cross-reference any regulatory claim against official circular
- Check effective dates — regulations may be announced but not yet effective
- Watch for state-level vs central-level regulatory differences

**Red Flags**:
- Regulatory claim without circular number
- "RBI allows..." without date and specific circular reference
- Compliance advice from non-legal sources
- Outdated regulatory references (check effective date)

## Domain 4: Academic / Scientific Research

**Source Hierarchy**:
1. Systematic reviews and meta-analyses
2. Randomized controlled trials (RCTs)
3. Observational studies (with methodology assessment)
4. Expert consensus and guidelines
5. Narrative reviews
6. Case reports and expert opinion

**Decay Rate**: 5-10 years for foundational work; 18-24 months for applied fields

**Quality Checks**:
- Peer review status (pre-print vs published)
- Pre-registration (reduces selective reporting)
- Sample size adequacy
- Effect size (not just p-value significance)
- Replication status (has this been replicated?)
- Journal legitimacy (check DOAJ, not just impact factor)
- Retraction status (check Retraction Watch)

**Red Flags**:
- p-values exactly at 0.05 boundary
- No confidence intervals reported
- "Revolutionary" or "breakthrough" language
- Small sample sizes with large claims
- Conflicts of interest not disclosed
- Published in predatory journals

## Domain 5: Legal / Compliance

**Source Hierarchy**:
1. Primary legal text (statutes, regulations, case law)
2. Official regulatory guidance and interpretations
3. Bar-licensed attorney analysis (named, with jurisdiction)
4. Legal databases (Westlaw, LexisNexis)
5. Law firm blogs (verify against primary text)
6. General legal information sites (low reliability)

**Decay Rate**: 12-36 months for regulations; jurisdiction-dependent

**Critical Rules**:
- ALWAYS cite primary legal text, not interpretations
- Specify jurisdiction (law varies by location)
- Check for amendments and updates since publication
- Note whether law has been tested in court
- Distinguish between law, regulation, guidance, and opinion

## Domain 6: Emerging Technology / AI

**Source Hierarchy**:
1. Published papers with code and benchmarks
2. Official model/product documentation
3. Independent benchmarks and evaluations
4. Official engineering blogs (Google AI, Meta AI, etc.)
5. ArXiv pre-prints (with replication caveat)
6. Tech journalist coverage (variable quality)
7. Twitter/social media discourse (signal + noise)

**Decay Rate**: 3-12 months (fastest-moving domain)

**Quality Checks**:
- Are benchmarks reproducible? (Code available?)
- Are claims independently verified?
- Is this vaporware or shipping product?
- How does it perform outside cherry-picked examples?
- What are the failure modes?

**Red Flags**:
- Benchmarks only on author-selected tasks
- No code release with paper
- "Achieves SOTA" without specifying on what exactly
- No discussion of limitations or failure cases
- Comparisons only against outdated baselines

## Cross-Domain Rules

Regardless of domain, ALWAYS:
1. Start with the highest-authority sources for that domain
2. Apply domain-specific decay rate to temporal tagging
3. Watch for domain-specific red flags
4. Use the domain's standard search pattern before custom queries
5. Cross-reference domain-specialist sources with generalist sources
6. Document which domain strategy was applied in the source registry
