# Source Validation — Type-Specific Quality Framework

## Universal Red Flags (Any Domain)
- No publication date
- Promotional language ("revolutionary", "game-changing", "disrupting")
- No citations or source attribution
- Absolute certainty ("always", "never", "the only way")
- Vague methodology ("we analyzed..." without specifics)
- AI-generated content markers (generic structure, no specific examples)
- Single-author with no verifiable credentials

## Universal Green Flags (Any Domain)
- Clear authorship with verifiable credentials
- Regular maintenance and updates
- Explicit methodology section
- Acknowledges limitations and trade-offs
- Specific, concrete examples from production use
- Linked references to primary sources

## Technical Sources (Libraries, APIs, Frameworks)

| Check | Signal | Tool |
|---|---|---|
| Active maintenance | Last commit < 3 months | GitHub/GitLab |
| Bus factor | 3+ active contributors | GitHub insights |
| Production users | Dependents count > stars | npm/PyPI stats |
| Security posture | OpenSSF Scorecard | scorecard.dev |
| Fork-to-star ratio | ≥1:10 = active usage | GitHub |
| Deprecation | README says "use X instead" | README check |
| Documentation quality | Complete API docs, examples | Docs site |

**Always check official documentation directly** — never rely solely on blog posts.

## Business/Market Sources

| Check | Signal | Assessment |
|---|---|---|
| Primary vs secondary | Original research vs. summary | Primary > secondary |
| Author credentials | Verifiable industry expertise | LinkedIn/bio check |
| Funding disclosure | Sponsored content declared | Check footer/disclaimer |
| Publication reputation | Established media vs. content farm | Lateral reading |
| Data recency | Published within domain half-life | Date check |
| Methodology transparency | Sample size, collection method stated | Read methodology |

## Academic Sources

| Check | Signal | Assessment |
|---|---|---|
| Peer review status | Published in indexed journal | Check DOAJ |
| Pre-registration | Hypothesis registered before study | Check OSF |
| Sample size | Adequate for claimed effect | Power analysis |
| P-values | Not suspiciously just below 0.05 | Verify statistics |
| Retraction status | Check for retractions | Retraction Watch |
| Citation quality | Supporting vs. contrasting citations | Scite.ai model |
| Journal legitimacy | Indexed, impact factor | Check DOAJ |

## Web Content (Blogs, Forums, Social)

Apply SIFT method:
1. **Stop**: Don't immediately trust
2. **Investigate the source**: What do others say about this author/site?
3. **Find better coverage**: Is there an official or primary source?
4. **Trace claims**: Does the cited source actually support the claim?

### Stack Overflow Caveat
58.4% of Stack Overflow answers are already obsolete when posted.
Treat as starting point for investigation, NOT as authoritative source.
Always verify against official documentation.

## Consulting/Industry Reports

| Check | Signal | Assessment |
|---|---|---|
| Funding source | Client-funded vs. independent | Bias assessment |
| Vendor comparison | "Independent" or vendor-sponsored | Check disclosures |
| Methodology access | Published or proprietary | Reproducibility |
| Sample disclosure | Survey size and methodology | Quality check |
| Paywall status | Free (brand-building) vs. paid (commercial) | Access model |

## Validation Process Per Source

For each source used in the research:
1. Classify type (technical/business/academic/web/consulting)
2. Apply type-specific checks above
3. Assign reliability: High / Moderate / Low
4. Document in Source Registry with full metadata
5. If reliability is Low: flag the finding and seek additional corroboration
