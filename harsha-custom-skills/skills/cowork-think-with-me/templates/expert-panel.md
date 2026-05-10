# Expert Panel Template

Use this template when creating `EXPERT_PANEL.md` after expert panel discussion.

```markdown
## Panel Composition

| # | Expert | Domain | Selected Because |
|---|--------|--------|-----------------|
| 1 | Product Manager (anchor) | Strategy, prioritization | Always included |
| 2 | [Expert Name] | [Domain] | [Why this expert is relevant to this decision] |
| 3 | [Expert Name] | [Domain] | [Why relevant] |

## Missing Expertise
[Domains that were relevant but not represented on the panel. Note how this gap may have
affected the analysis.]

Example: "No Pricing Strategist on this panel. Fee structure analysis relied on PM and
Business Analyst perspectives, which may underweight pricing psychology and elasticity
considerations."

## Panel Discussion

### [Expert 1: Product Manager]
**Key contribution:** [What this expert surfaced that others didn't]
**Options advocated for:** [Which options this expert favored and why]
**Concerns raised:** [Specific risks or trade-offs this expert flagged]

### [Expert 2: ...]
**Key contribution:** [...]
**Options advocated for:** [...]
**Concerns raised:** [...]

## Points of Agreement
[Where did all or most experts converge? These are high-confidence signals.]

## Points of Disagreement
[Where did experts diverge? These are decision points requiring user judgment.]

| Topic | Expert A Position | Expert B Position | Resolution |
|-------|------------------|------------------|------------|
| [e.g., Migration timing] | [Big-bang — lower transition cost] | [Rolling — lower blast radius] | [User to decide] |

## Surprising Insights
[Options or considerations that no single expert would have surfaced alone — 
emerged from the cross-pollination of expert perspectives]

## Panel Limitations
[What this panel could NOT evaluate due to missing expertise, missing data, or
out-of-domain considerations]
```

## Selection Protocol

1. Read the problem statement
2. Identify the 2-3 most relevant domains
3. Always include PM as anchor
4. Add 2-4 domain experts based on the problem
5. For pricing decisions: include Pricing/Revenue Strategist
6. For lending/payment decisions: include Finance/Treasury Lead
7. For migration/sunset decisions: include Migration/Transition Lead
8. Document panel selection reasoning in this file

## Expert Interaction Model

Experts surface options and critiques during enumeration and ranking. They do NOT vote — 
the user decides. Each expert contributes through their domain lens:

- **During enumeration:** "From a [domain] perspective, there's an option we haven't named..."
- **During ranking:** "From a [domain] perspective, the downside of option X is..."
- **During synthesis:** "The [domain] risk that cuts across multiple options is..."
