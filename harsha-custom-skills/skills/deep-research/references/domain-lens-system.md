# Domain Lens System

Domain lenses are **overlays** on the standard 6+2 phase pipeline. They enrich research with domain-specific query angles, metadata fields, quality bars, and webapp views — without replacing the core pipeline.

**When to read this file**: Before activating any domain lens, or when adding a new lens. The per-lens specifications live in their own files (`domain-pm.md`, `domain-fintech.md`, `domain-proptech.md`).

---

## Architecture

```
Standard Pipeline (always runs):  Phase 1 → 2 → 3 → 3.5 → 4 → 4.5 → 5 → 6
                                    ↑       ↑       ↑              ↑       ↑
Domain Lens (overlay):          Queries  Tags   Metadata        QA+     Views
```

Each domain lens is a separate reference file loaded only when activated. The SKILL.md stays lean; domain logic lives in `references/domain-*.md`.

---

## Available Domain Lenses

| Lens | Activation | Reference File | What It Does |
|------|-----------|----------------|-------------|
| **PropTech** | Auto-detect on PropTech keywords, OR user explicitly requests. (Note: PropTech retains auto-detect for backward compatibility with v2.5. New lenses should use explicit-trigger only.) | `references/domain-proptech.md` | PropTech market taxonomy, property type facets, geographic specificity, regulatory accuracy, Leaflet map view |
| **Product Management** | User explicitly requests ("PM lens", "PM mode", "through a PM perspective") | `references/domain-pm.md` | 10 PM dimensions overlay, PM Dashboard view, Executive Summary, actionability scoring, stakeholder tagging |
| **FinTech** | User explicitly requests ("FinTech lens", "FinTech mode", "through a FinTech perspective") | `references/domain-fintech.md` | 10 FinTech dimensions overlay (Regulatory, Payment Rails, Trust/Security, Unit Economics, Acquisition, Embedded Finance, Credit Risk, Inclusion, Cross-Border, Funding), FinTech Dashboard view, viability scoring, geography tagging, regulatory timeline |

---

## How Lenses Modify the Pipeline

Lenses do NOT replace phases. They modify what happens WITHIN each phase:

- **Phase 1**: Add domain-specific queries (PM lens adds 10-15 extra queries across 10 dimensions)
- **Phase 2**: Tag entries with domain dimensions (PM tags entries as "competitive", "market_size", etc.)
- **Phase 3**: Add domain metadata fields per entry (PM adds `pm_actionability`, `pm_so_what`, `pm_who_cares`)
- **Phase 3.5**: Add domain relationship types (PM adds "competes-with", "enables", "blocks")
- **Phase 4.5**: Add domain QA dimension (PM adds "PM Actionability" 0-10 score)
- **Phase 5**: Generate domain executive summary (PM generates structured PM Executive Summary)
- **Phase 6**: Add domain webapp view (PM adds PM Dashboard organized by 10 dimensions)

---

## PM Lens Quick Reference

When PM lens is active, read `references/domain-pm.md` for the complete specification. Key features:

**10 PM Research Dimensions** — every entry gets tagged:
1. Opportunity Landscape (pain points, unmet needs)
2. Competitive Positioning (who else, white space)
3. Market Size & Addressability (TAM/SAM/SOM)
4. Customer Segments & Value (who, what value)
5. Metrics & Measurement (North Star, KPIs)
6. Go-to-Market Strategy (channels, adoption)
7. Solution Patterns (what exists, UX patterns)
8. Validation & Experimentation (assumptions, failure modes)
9. Business Model & Unit Economics (pricing, LTV/CAC)
10. Strategic Context & Constraints (regulatory, dependencies)

**PM-specific outputs**:
- PM Dimension Coverage Matrix (after Phase 2 — shows research gaps)
- PM Executive Summary (after Phase 5 — structured opportunity/market/competition brief)
- PM Dashboard webapp view (Phase 6 — entries organized by dimension, actionability-sorted)
- Stakeholder filter (filter entries by who needs to see them)

**PM Actionability scoring** (0-10, added to QA):
- 10: Directly changes a build/ship/kill decision
- 6-7: Informs strategy with concrete data
- 2-3: Background context only

---

## FinTech Lens Quick Reference

When FinTech lens is active, read `references/domain-fintech.md` for the complete specification. Key features:

**10 FinTech Research Dimensions** — every entry gets tagged:
1. Regulatory & Compliance Architecture (licenses, RBI/FCA/OCC, compliance frameworks)
2. Payment Rails & Infrastructure Integration (UPI, SWIFT, card networks, real-time payments)
3. Trust, Security & Identity Architecture (eKYC, fraud prevention, PCI-DSS, Aadhaar)
4. Unit Economics & Financial Modeling (revenue models, margins, CAC/LTV, break-even)
5. Customer Acquisition & Retention Economics (onboarding, trust barriers, retention curves)
6. Embedded Finance & Platform Strategy (BaaS, B2B2C, API-first distribution)
7. Credit Risk & Underwriting Models (scoring, alternative data, NPA, FLDG)
8. Financial Inclusion & Impact (unbanked, Tier 2-4, microfinance, gender gap)
9. Cross-Border & Multi-Currency Strategy (remittance, FX, corridors, stablecoins)
10. Funding Structure & Capital Strategy (venture, co-lending, securitization, warehouse)

**FinTech-specific outputs**:
- FinTech Dimension Coverage Matrix (after Phase 2 — shows research gaps)
- FinTech Executive Summary (after Phase 5 — opportunity/regulation/unit economics/risk brief)
- FinTech Dashboard webapp view (Phase 6 — entries by dimension, viability-sorted)
- Geography filter (filter entries by India/US/EU/Global)
- Regulatory timeline (entries sorted chronologically by compliance deadlines)
- Stakeholder filter (filter by Compliance, Product, Risk, Finance)

**FinTech Viability scoring** (0-10, added to QA):
- 10: Directly determines build/kill decision with regulatory or economic data
- 6-7: Informs product strategy with concrete benchmarks
- 2-3: Background context only

**Validated market data included**:
- Global FinTech market: $300-400B (2025), CAGR 16-18% (cross-validated 3 sources)
- India FinTech market: $142-155B (2025) (cross-validated 3 sources)
- 11-segment market taxonomy with key players (global + India)
- India Stack infrastructure data (UPI, Aadhaar, Account Aggregator, OCEN)
- Regulatory timeline with specific circular numbers and effective dates

---

## PropTech Lens Quick Reference

When PropTech lens is active, read `references/domain-proptech.md` for the complete specification. Key features:
- 4-pass research architecture (Landscape → Segment → Verify → Synthesis)
- PropTech-specific data sources (ATTOM, CoreLogic, Knight Frank, CREDAI)
- 5-tier confidence with industry-specific authority rules
- Geographic specificity (US vs India vs UK)
- Market data recency requirement (2024+)
- PropTech webapp template with Leaflet map views, property cards, market segment filters

---

## Adding New Domain Lenses

To add a new domain (e.g., Healthcare, EdTech, Cybersecurity):
1. Create `references/domain-<name>.md` following the structure of `domain-pm.md`
2. Define: activation triggers, dimension taxonomy, query enrichment, metadata fields, quality bar, webapp views
3. Add an entry to the "Available Domain Lenses" table in SKILL.md (and in this file)
4. Add a `<Name>LensProcessor` class to `scripts/build_knowledge_app.py` (inherit from `BaseLensProcessor`) and a `--<name>-lens` CLI flag
5. No other files need modification — the core pipeline is domain-agnostic
