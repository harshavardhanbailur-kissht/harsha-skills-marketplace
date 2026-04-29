# FinTech Domain Lens

**Version:** 1.0
**Last Updated:** 2026-03-25
**Scope:** FinTech-specific research framing, dimensions, query enrichment, and webapp views
**Activation:** User explicitly requests FinTech lens — never auto-detected

---

## Section 1: Activation & Philosophy

### When This Lens Activates

The FinTech lens activates ONLY when the user explicitly requests it:
- "use FinTech lens", "FinTech mode", "through a FinTech perspective"
- "I want to study this as a FinTech PM", "financial technology angle"
- "help me understand this for FinTech work"
- "analyze this from a fintech lens"

It does NOT auto-detect on keywords like "payments", "lending", or "banking". This is intentional — the same topic (e.g., "AI in fraud detection") yields very different research through a general lens vs. FinTech lens, and only the user knows which they want.

### What the FinTech Lens Does

The FinTech lens is an **overlay**, not a replacement. The standard 6+2 phase pipeline runs exactly as before. The FinTech lens modifies what happens WITHIN each phase:

| Phase | Standard Behavior | FinTech Lens Addition |
|-------|------------------|----------------------|
| Phase 1 (Planning) | Decompose into sub-questions | Add 10 FinTech dimension queries |
| Phase 2 (Breadth) | Tag themes | Tag entries with FinTech dimensions |
| Phase 3 (Depth) | Extract knowledge entries | Add FinTech metadata fields per entry |
| Phase 3.5 (Graph) | Build relationships | Add FinTech relationship types |
| Phase 4 (Verify) | Trace evidence chains | Prioritize regulatory & unit economics verification |
| Phase 4.5 (QA) | Score 0-50 | Add "FinTech Viability" score |
| Phase 5 (Assemble) | Deduplicate, normalize | Generate FinTech Executive Summary |
| Phase 6 (Webapp) | Knowledge graph + search | Add FinTech Dashboard view |

### What the FinTech Lens Does NOT Do

- Does not replace the generic pipeline
- Does not lower quality standards
- Does not auto-trigger on keywords
- Does not use a separate template (uses the generic template with FinTech view injection)
- Does not require different sub-agent architecture

---

## Section 2: The 10 FinTech Research Dimensions

Every knowledge entry gets tagged with which FinTech dimension(s) it serves. These are the dimensions critical when studying ANY FinTech-adjacent topic:

### Dimension 1: Regulatory & Compliance Architecture
**Question**: What regulatory frameworks govern this space? What licenses are required?
**What to research**: Licensing requirements (banking charter, NBFC, PPI, payment aggregator), compliance frameworks (KYC/AML, PCI-DSS, SOC2), regulatory bodies (RBI, SEBI, IRDAI, OCC, FCA, ECB), recent regulatory actions, sandbox programs
**Key frameworks**:
- India: RBI Master Directions on Digital Lending (effective May 8, 2025), FLDG cap at 5% of loan portfolio, RBI Payment Aggregator guidelines, SEBI registered investment advisor rules, DPDP Act (staged rollout)
- US: State-by-state money transmitter licensing, OCC fintech charter, CFPB oversight, SEC/FinCEN for crypto
- EU/UK: PSD2/PSD3, MiCA (crypto), FCA authorization, Open Banking mandates, GDPR for financial data
- Global: FATF recommendations, Basel III/IV capital requirements
**Query enrichment**: Add "[topic] fintech regulation", "[topic] licensing requirements", "[topic] compliance framework", "[topic] regulatory risk"
**Authoritative sources**: RBI circulars (rbi.org.in), CFPB guidance (consumerfinance.gov), FCA handbook (fca.org.uk), FATF reports (fatf-gafi.org)

### Dimension 2: Payment Rails & Infrastructure Integration
**Question**: What payment infrastructure does this touch? What rails does it ride on?
**What to research**: Payment networks (UPI, IMPS, NEFT/RTGS, SWIFT, ACH, SEPA, Faster Payments), card networks (Visa, Mastercard, RuPay), real-time payment systems, ISO 20022 migration, API banking, payment aggregator vs gateway distinction
**Key data points**:
- India UPI: 228.3B transactions processed (2025 cumulative), 21.7B transactions in January 2026 alone, NPCI infrastructure
- Global real-time payments: 266.2B transactions globally (2023), growing 42% YoY
- ISO 20022: Mandatory migration deadline for SWIFT by November 2025
- Account Aggregator (India): 2.61B linked accounts, consent-based financial data sharing
**Query enrichment**: Add "[topic] payment infrastructure", "[topic] UPI integration", "[topic] payment rails", "[topic] real-time payments"
**Authoritative sources**: NPCI data (npci.org.in), BIS payment statistics, Federal Reserve payment studies, EPC SEPA documentation

### Dimension 3: Trust, Security & Identity Architecture
**Question**: How is trust established? What identity and security infrastructure is required?
**What to research**: Digital identity systems (Aadhaar eKYC, DigiLocker, EU eIDAS), fraud prevention (ML-based, rule-based), authentication (biometric, multi-factor), data security (encryption at rest/transit, tokenization), cybersecurity compliance, privacy frameworks
**Key data points**:
- India Stack: Aadhaar (1.4B+ enrollments), eKYC cost ~₹3 vs traditional KYC ~₹500-700
- Global identity fraud losses: $52B+ annually (Javelin Strategy 2024)
- PCI-DSS v4.0: Mandatory compliance from March 2025
- Account takeover fraud growing 72% YoY in digital banking (NICE Actimize 2024)
**Query enrichment**: Add "[topic] identity verification", "[topic] fraud prevention", "[topic] KYC infrastructure", "[topic] data security fintech"
**Authoritative sources**: UIDAI (uidai.gov.in), PCI Security Standards Council, NIST cybersecurity framework, ENISA reports

### Dimension 4: Unit Economics & Financial Modeling
**Question**: Does the unit economics work? What are the margin structures?
**What to research**: Revenue models (interchange, spread, subscription, transaction fee, float income), cost structures (CAC, cost-to-serve, fraud losses, compliance costs), margin analysis, break-even analysis, capital efficiency
**Key benchmarks**:
- Neobank CAC: $5-35 (varies by market; India ~$2-8, US ~$20-50)
- Payment gateway take rate: 1.5-3.0% (India: MDR 0% on UPI, 0.5-2% on cards)
- Lending net interest margin: 3-15% (microfinance higher, secured lending lower)
- Insurance loss ratio: 60-80% (healthy), >90% (unsustainable)
- Wealth management fee compression: AUM fees declining from 1-2% to 0.25-0.75%
**Query enrichment**: Add "[topic] unit economics", "[topic] revenue model fintech", "[topic] take rate", "[topic] margin structure", "[topic] CAC LTV fintech"
**Authoritative sources**: Company filings (SEC EDGAR, MCA India), McKinsey Global Payments Report, BCG FinTech Control Tower, CB Insights FinTech reports

### Dimension 5: Customer Acquisition & Retention Economics
**Question**: How do customers discover, adopt, and stay with FinTech products?
**What to research**: Acquisition channels (digital, referral, embedded, agent-based), onboarding friction points, activation metrics, retention curves, churn drivers, trust barriers, network effects
**Key data points**:
- FinTech app retention: ~25% at Day 30 (industry average), top performers 40%+
- Digital lending conversion funnel: 100% apply → 60% complete KYC → 40% approved → 30% disburse
- Trust as barrier: 47% of users cite security concerns as reason for not using FinTech (EY Global FinTech Adoption Index)
- India vernacular onboarding: Apps supporting 5+ languages see 2-3x rural adoption
**Query enrichment**: Add "[topic] fintech customer acquisition", "[topic] fintech retention", "[topic] onboarding conversion", "[topic] trust barrier fintech"
**Authoritative sources**: EY Global FinTech Adoption Index, Sensor Tower app analytics, Appsflyer benchmarks, company investor presentations

### Dimension 6: Embedded Finance & Platform Strategy
**Question**: Is the opportunity in standalone products or embedded distribution?
**What to research**: BaaS (Banking-as-a-Service) models, embedded lending/insurance/payments, API-first distribution, platform economics, white-label vs branded, B2B2C models
**Key data points**:
- Embedded finance market: $138B revenue by 2026 (Lightyear Capital), projected $384B by 2029
- BaaS providers: Solarisbank (EU), Synapse→Column (US), M2P (India), Railsr (UK)
- Embedded lending: 33% of SMB lending expected through non-bank platforms by 2028 (McKinsey)
- Insurance embedded in e-commerce: 5-10x higher conversion vs standalone distribution
**Query enrichment**: Add "[topic] embedded finance", "[topic] BaaS", "[topic] API banking", "[topic] platform fintech", "[topic] B2B2C finance"
**Authoritative sources**: Lightyear Capital embedded finance reports, a]6z FinTech newsletters, McKinsey Banking Annual Review, Simon-Kucher pricing studies

### Dimension 7: Credit Risk & Underwriting Models
**Question**: How is credit risk assessed? What data and models power underwriting?
**What to research**: Traditional scoring (CIBIL, FICO, Experian), alternative data scoring (phone metadata, transaction history, psychometrics), ML underwriting models, credit bureau infrastructure, collection strategies, NPA/delinquency benchmarks
**Key data points**:
- India credit bureau coverage: ~600M individuals (CIBIL/TransUnion), but only ~200M with meaningful credit history
- Alternative data uplift: 15-25% improvement in default prediction for thin-file borrowers (World Bank)
- NBFC gross NPA: 4.0-6.5% industry average (RBI FSR 2025), top digital lenders targeting <3%
- FLDG model: RBI cap at 5% of outstanding loan portfolio, 120-day cover window
- Account Aggregator for underwriting: Consent-based bank statement analysis replacing physical statement uploads
**Query enrichment**: Add "[topic] credit scoring", "[topic] alternative data underwriting", "[topic] NPA delinquency", "[topic] FLDG", "[topic] credit risk model"
**Authoritative sources**: RBI Financial Stability Report, CIBIL/TransUnion reports, World Bank CGAP studies, Microfinance Institutions Network (MFIN) data

### Dimension 8: Financial Inclusion & Impact
**Question**: Does this expand access to underserved populations? What's the inclusion opportunity?
**What to research**: Unbanked/underbanked populations, Tier 2-4 city opportunity, gender gap in financial access, agricultural finance, microfinance, impact measurement frameworks, government schemes (PMJDY, PMSBY)
**Key data points**:
- India financial inclusion: PMJDY 520M+ accounts opened, but ~30% remain dormant
- Global unbanked: 1.4B adults without a bank account (World Bank Findex 2021), declining from 1.7B in 2017
- Women's financial inclusion gap: 6 percentage points globally, 12+ points in South Asia (Findex)
- India Tier 2-4 digital payments: Growing 2.5x faster than Tier 1 cities
- Microfinance portfolio: ₹4.2 lakh crore in India (MFIN Q3 FY25), serving 75M+ borrowers
**Query enrichment**: Add "[topic] financial inclusion", "[topic] unbanked population", "[topic] tier 2 fintech", "[topic] microfinance", "[topic] impact fintech"
**Authoritative sources**: World Bank Global Findex, PMJDY dashboard (pmjdy.gov.in), NABARD annual report, MFIN Micrometer, CGAP publications

### Dimension 9: Cross-Border & Multi-Currency Strategy
**Question**: Does this involve cross-border flows? What FX and compliance considerations apply?
**What to research**: Remittance corridors, cross-border payment infrastructure, FX management, correspondent banking, SWIFT alternatives, trade finance, multi-currency wallets, regulatory arbitrage
**Key data points**:
- India inward remittances: $129B (2024, World Bank), largest recipient globally
- Cross-border payment costs: Average 6.2% for $200 remittance (World Bank Q3 2024), target <3% by SDG 10.c
- SWIFT gpi: 50%+ of payments credited within 30 minutes (2024)
- India Liberalised Remittance Scheme (LRS): $250K/year cap per individual, RBI reporting requirements
- Stablecoin cross-border: $2.6T+ in on-chain transfer volume (2024), growing as settlement layer
**Query enrichment**: Add "[topic] cross-border payments", "[topic] remittance", "[topic] FX management fintech", "[topic] multi-currency", "[topic] trade finance"
**Authoritative sources**: World Bank Remittance Prices Worldwide, RBI LRS data, BIS cross-border payments report, SWIFT BI Watch

### Dimension 10: Funding Structure & Capital Strategy
**Question**: How is this funded? What capital structure is appropriate?
**What to research**: Venture funding trends, debt vs equity mix, co-lending models, securitization, ABS (asset-backed securities), warehouse lending, balance sheet vs marketplace lending, regulatory capital requirements
**Key data points**:
- India FinTech funding: $2.4B in 2025, India is 3rd largest FinTech funding destination globally
- Global FinTech funding: $51.9B in 2024 (CB Insights), down from $132B peak in 2021
- India FinTech unicorns: 16+ (including Razorpay, PhonePe, CRED, Zerodha, PolicyBazaar, Pine Labs)
- Co-lending model: NBFC + bank partnerships, RBI co-lending guidelines (Nov 2020), enables lower-cost capital access
- Securitization: India direct assignment + PTC volume ₹1.8 lakh crore (FY24, ICRA), growing 20%+ YoY
- Global FinTech unicorns: 404 as of 2025 (CB Insights)
**Query enrichment**: Add "[topic] fintech funding", "[topic] co-lending model", "[topic] securitization fintech", "[topic] fintech valuation", "[topic] capital structure"
**Authoritative sources**: CB Insights State of FinTech, Tracxn India FinTech report, ICRA securitization reports, RBI co-lending guidelines, Dealroom.co

---

## Section 3: Phase-by-Phase FinTech Lens Behavior

### Phase 1 FinTech Enhancement: Query Planning

For each of the 10 FinTech dimensions, generate 1-2 additional queries beyond the standard decomposition. This means a FinTech lens research typically has 15-25 queries vs the standard 5-10.

**Example**: Topic = "Buy Now Pay Later (BNPL)"
Standard queries (5-10): BNPL market overview, consumer behavior, default rates, regulation, major players...
FinTech-added queries (10-15):
- Regulatory: "BNPL regulation RBI digital lending guidelines 2025", "BNPL CFPB enforcement actions"
- Payment Rails: "BNPL UPI integration merchant onboarding", "BNPL card network partnerships"
- Trust/Security: "BNPL identity verification thin-file borrowers", "BNPL fraud patterns"
- Unit Economics: "BNPL unit economics merchant discount rate vs late fees", "BNPL break-even customer cohort"
- Acquisition: "BNPL customer acquisition checkout integration conversion", "BNPL retention repeat usage rate"
- Embedded: "BNPL embedded in e-commerce platforms Shopify Amazon", "BNPL white-label BaaS providers"
- Credit Risk: "BNPL default rates vs credit cards", "BNPL alternative data scoring young borrowers"
- Inclusion: "BNPL financial inclusion credit-invisible consumers", "BNPL Tier 2-3 city adoption India"
- Cross-Border: "BNPL cross-border e-commerce FX settlement", "BNPL multi-currency merchant"
- Funding: "BNPL securitization ABS market", "BNPL funding runway venture vs debt capital"

### Phase 2 FinTech Enhancement: Breadth Tagging

During breadth scan, tag each discovered source/theme with FinTech dimensions:
```
Theme: "BNPL Default Rates Rising" → FinTech Dimensions: [credit_risk, unit_economics, regulatory]
Theme: "RBI Digital Lending Rules" → FinTech Dimensions: [regulatory, credit_risk]
Theme: "BNPL Checkout Conversion" → FinTech Dimensions: [acquisition, embedded_finance, unit_economics]
```

After Phase 2, generate a **FinTech Dimension Coverage Matrix**:
```
FINTECH DIMENSION COVERAGE (after breadth scan):
- Regulatory & Compliance:     ████████░░ (8 sources)  ✓ Good
- Payment Rails:               ██████░░░░ (6 sources)  ✓ Good
- Trust & Security:            ████░░░░░░ (4 sources)  ⚠ Needs depth
- Unit Economics:              ███░░░░░░░ (3 sources)  ⚠ Needs depth
- Customer Acquisition:        ██░░░░░░░░ (2 sources)  ✗ Gap — add queries
- Embedded Finance:            █████░░░░░ (5 sources)  ✓ Good
- Credit Risk:                 ██████░░░░ (6 sources)  ✓ Good
- Financial Inclusion:         ██░░░░░░░░ (2 sources)  ✗ Gap — add queries
- Cross-Border:                █░░░░░░░░░ (1 source)   ✗ Gap — add queries
- Funding & Capital:           ███░░░░░░░ (3 sources)  ⚠ Needs depth
```

If any dimension has <3 sources, add targeted queries before proceeding to Phase 3.

### Phase 3 FinTech Enhancement: Entry Metadata

Each knowledge entry gets additional FinTech metadata fields:

```json
{
  "id": "entry-rbi-digital-lending",
  "title": "RBI Digital Lending Guidelines 2025",
  "category": "regulation",
  "content": "...",
  "confidence": "VERIFIED",
  "source": "rbi.org.in",

  "ft_dimensions": ["regulatory", "credit_risk"],
  "ft_viability": "HIGH",
  "ft_decision_relevance": "Build vs. compliance risk — affects product launch by 6-12 months and requires NBFC partnership",
  "ft_so_what": "Any digital lending product in India MUST comply with RBI Direct Lending guidelines. LSPs cannot touch funds. FLDG capped at 5%. Must partner with regulated entity or obtain NBFC license.",
  "ft_who_cares": ["Chief Compliance Officer", "Head of Lending", "CEO", "Legal"],
  "ft_timeframe": "Immediate — already in effect",
  "ft_geography": "India"
}
```

**FinTech-specific metadata fields explained**:
- `ft_dimensions`: Which of the 10 FinTech dimensions this entry serves (array, 1-3 values)
- `ft_viability`: HIGH (directly impacts build/launch feasibility), MEDIUM (informs product strategy), LOW (background context)
- `ft_decision_relevance`: One sentence explaining what FinTech decision this informs
- `ft_so_what`: The "so what?" synthesis — what should a FinTech builder DO with this information
- `ft_who_cares`: Which stakeholders need this information
- `ft_timeframe`: When is this relevant? (immediate, 3-6 months, 12+ months)
- `ft_geography`: Geographic relevance (India, US, EU/UK, Global, specific corridor)

### Phase 3.5 FinTech Enhancement: FinTech Relationship Types

In addition to the standard 6 relationship types, the FinTech lens adds:

- **Regulates**: One entry (regulation) governs behavior in another (product/market)
- **Settles-through**: Payment flow settles through a specific rail or infrastructure
- **Lends-to / Borrows-from**: Capital flow direction between entities
- **Competes-with**: Two companies/products competing for same customer segment
- **Embeds-in**: One product/service is embedded within another platform
- **Requires-license**: One entry requires regulatory license from another

### Phase 4.5 FinTech Enhancement: Viability Scoring

In addition to the standard 5-dimension QA score (0-50), FinTech lens adds a 6th dimension:

**FinTech Viability (0-10)**:
- 10: Directly determines build/kill decision with specific regulatory, economic, or infrastructure data
- 8-9: Strongly informs product strategy with concrete benchmarks or compliance requirements
- 6-7: Useful context that shapes FinTech-specific thinking
- 4-5: Background information, industry context
- 2-3: Tangentially relevant to FinTech angle
- 0-1: Not actionable for FinTech work

Entries with FinTech Viability <4 are deprioritized (not removed) in the FinTech Dashboard view.

### Phase 5 FinTech Enhancement: Executive Summary

After assembly, automatically generate a FinTech Executive Summary:

```
FINTECH EXECUTIVE SUMMARY: [Topic]
Generated: [Date]

THE OPPORTUNITY
[2-3 sentences from Dimensions 4+5+8 entries, highest confidence — market gap, underserved segment, unit economics potential]

THE INFRASTRUCTURE
[Payment rails, identity systems, and platform dependencies from Dimensions 2+3+6]

THE REGULATION
[Critical compliance requirements, license needs, and timeline impacts from Dimension 1]

THE RISK PROFILE
[Credit risk benchmarks, fraud patterns, and delinquency data from Dimension 7]

THE UNIT ECONOMICS
[Revenue model, margin structure, CAC/LTV benchmarks from Dimension 4]

THE MARKET
[Funding landscape, comparable valuations, and capital strategy from Dimension 10]

INCLUSION OPPORTUNITY
[Financial inclusion angle, underserved segments from Dimension 8]

CROSS-BORDER CONSIDERATIONS
[If applicable: FX, corridors, multi-currency from Dimension 9]

BIGGEST RISKS
[Top 3 from Dimensions 1 + 7 + 4 — regulatory, credit, and economic risks]

RECOMMENDED NEXT STEPS
[3-5 actionable items derived from highest-viability entries]
```

### Phase 6 FinTech Enhancement: FinTech Dashboard View

The webapp gets an additional view mode (alongside Explore Mode and Learning Path):

**FinTech Dashboard View** — organized by the 10 dimensions:
- Each dimension is a card/section
- Entries within each dimension sorted by FinTech Viability (highest first)
- Color coding: GREEN (well-researched, 5+ entries), YELLOW (moderate, 2-4), RED (gap, 0-1)
- FinTech Executive Summary at the top
- "Viability Board" showing entries with HIGH ft_viability
- Geography filter: filter by ft_geography to focus on specific markets
- Regulatory timeline: entries with ft_timeframe sorted chronologically
- Stakeholder filter: filter by ft_who_cares to see what matters to specific roles

---

## Section 4: FinTech-Specific Sub-Agent Query Templates

When FinTech lens is active, sub-agents get FinTech-enriched prompts. Each sub-agent receives one additional instruction block:

```
FINTECH LENS ACTIVE — In addition to standard research:
1. For every key finding, assess: "So what? How does this affect FinTech product viability?"
2. Tag each finding with FinTech dimensions: [regulatory, payment_rails, trust_security, unit_economics, acquisition, embedded_finance, credit_risk, financial_inclusion, cross_border, funding_capital]
3. Note which stakeholders would care (Compliance, Product, Engineering, Finance, Risk)
4. Rate viability: HIGH (changes a build/launch/kill decision), MEDIUM (informs strategy), LOW (background)
5. If you find regulatory data, unit economics benchmarks, or credit risk metrics — these are HIGH priority, extract precisely with source and date
6. Flag geographic applicability: India, US, EU/UK, or Global
```

This is a lightweight addition (~120 tokens) that doesn't change the sub-agent's research behavior, just enriches its output tagging.

---

## Section 5: FinTech Lens Quality Bar

FinTech lens research has specific quality expectations beyond generic:

- **Regulatory claims**: Must cite specific regulation/circular number, issuing authority, and effective date. E.g., "RBI/DOR/FIN/REC/45/2024-25 dated April 30, 2024" not just "RBI guidelines"
- **Market sizing claims**: Must have 2+ independent sources, must specify methodology (top-down or bottom-up), must include year, geography, and segment scope
- **Unit economics claims**: Must specify currency, geography, product type, and whether public data or industry estimates. E.g., "India BNPL CAC ₹150-300 per transacting user (2024, industry estimate)" not just "low CAC"
- **Credit risk claims**: Must cite NPA definition used (30DPD, 60DPD, 90DPD), portfolio vintage, and sample size where available
- **Payment volume claims**: Must specify transaction count AND value, time period, and source. E.g., "UPI processed 16.6B transactions worth ₹23.4 lakh crore in December 2025 (NPCI)"
- **Funding claims**: Must be from 2024+ sources (funding landscape changes quarterly). Must cite round, amount, valuation if available, and date

---

## Section 6: FinTech Dimension Coverage Targets

A well-researched FinTech knowledge base should have:

| Dimension | Minimum Entries | Target Entries | Critical? |
|-----------|----------------|----------------|-----------|
| Regulatory & Compliance | 3 | 5-8 | YES — without this, can't ship legally |
| Payment Rails & Infrastructure | 2 | 4-6 | YES — without this, can't build the plumbing |
| Trust, Security & Identity | 2 | 3-5 | YES — without this, no user trust |
| Unit Economics & Financial Modeling | 3 | 5-8 | YES — without this, no business viability |
| Customer Acquisition & Retention | 2 | 3-5 | No — can be derived from comparable companies |
| Embedded Finance & Platform Strategy | 1 | 3-5 | No — only if distribution is via embedding |
| Credit Risk & Underwriting | 2 | 4-6 | YES for lending — without this, unsustainable defaults |
| Financial Inclusion & Impact | 1 | 2-4 | No — but critical for India market and impact investors |
| Cross-Border & Multi-Currency | 1 | 2-4 | Only if cross-border is in scope |
| Funding Structure & Capital | 2 | 3-5 | YES — without this, can't fund operations |

If any "Critical" dimension has <minimum entries after Phase 3, trigger additional queries before proceeding.

---

## Section 7: FinTech Market Taxonomy

### Segment Classification

When tagging FinTech entries, classify them into these validated market segments:

| Segment | Description | Key Players (Global) | Key Players (India) |
|---------|-------------|---------------------|---------------------|
| Digital Payments | Payment processing, wallets, POS | Stripe, Square, Adyen, PayPal | PhonePe, Paytm, Razorpay, BharatPe |
| Digital Lending | Consumer, SMB, BNPL | Affirm, Klarna, SoFi, LendingClub | KreditBee, MoneyTap, LazyPay, Kissht |
| Neobanking | Digital-only banking | Revolut, Chime, N26, Nubank | Jupiter, Fi Money, Niyo |
| WealthTech | Investment, robo-advisory | Robinhood, Wealthfront, eToro | Zerodha, Groww, Kuvera, Smallcase |
| InsurTech | Digital insurance distribution & underwriting | Lemonade, Root, Oscar | PolicyBazaar, Digit, Acko |
| RegTech | Compliance automation, KYC/AML | Chainalysis, ComplyAdvantage, Jumio | Signzy, IDfy, Perfios |
| Embedded Finance / BaaS | API-based financial services | Marqeta, Galileo, Unit | M2P, Decentro, Setu |
| Crypto & Digital Assets | Exchanges, DeFi, custody | Coinbase, Binance, Fireblocks | CoinDCX, WazirX, CoinSwitch |
| Trade Finance & B2B | Supply chain finance, B2B payments | C2FO, Taulia, Tradeshift | Vayana, KredX, Drip Capital |
| AgriFinTech | Agricultural lending and insurance | — | Jai Kisan, FarMart, DeHaat |
| Open Finance | Account aggregation, data sharing | Plaid, TrueLayer, Tink | Finvu, OneMoney, Sahamati ecosystem |

### Market Size Reference Data (Cross-Validated)

**Global FinTech Market**:
- Fortune Business Insights: $394.88B (2025) → $1.76T by 2034, CAGR 18.2%
- Mordor Intelligence: $320.81B (2025), CAGR 16.8% through 2030
- Expert Market Research: $264.80B (2025)
- **Synthesis**: Market size estimates vary $264-395B depending on segment inclusion. Use $300-400B as validated range for 2025 with 16-18% CAGR.
- **Confidence**: MEDIUM-HIGH — variance driven by definitional differences (whether crypto, insurtech, regtech are included)

**India FinTech Market**:
- BCG-PhonePe Pulse: $142B (2025), projected $1T by 2030
- RBSA Advisors: $150B (2025)
- EY/IAMAI: $155B (2025)
- **Synthesis**: $142-155B validated range for 2025. $1T by 2030 target widely cited but aggressive (requires 45%+ CAGR).
- **Confidence**: MEDIUM — the $1T projection depends heavily on regulatory stability and UPI monetization

**FinTech Unicorns**:
- Global: 404 FinTech unicorns (CB Insights, 2025)
- India: 16+ FinTech unicorns including Razorpay ($7.5B), PhonePe ($12B), CRED ($6.4B), Zerodha (~$3.6B based on reported profitability), PolicyBazaar (listed), Pine Labs ($5B)

---

## Section 8: India FinTech Infrastructure Deep-Dive

Since India is a primary research market, the FinTech lens includes validated India Stack infrastructure data:

### India Stack Components
| Layer | Component | Scale | Relevance |
|-------|-----------|-------|-----------|
| Identity | Aadhaar | 1.4B+ enrollments | eKYC backbone, cost ₹3 vs ₹500-700 traditional |
| Payments | UPI | 228.3B cumulative transactions | Real-time payment rail, 0% MDR |
| Data | Account Aggregator | 2.61B linked accounts | Consent-based financial data, credit underwriting |
| Lending | OCEN | Early stage | Open credit protocol, flow-based lending |
| Documents | DigiLocker | 270M+ users | Verified document sharing |
| Consent | DEPA framework | Active | Data Empowerment and Protection Architecture |

### Regulatory Timeline (India, Key Dates)
| Date | Regulation | Impact |
|------|-----------|--------|
| Sep 2022 | RBI Digital Lending Guidelines | LSPs cannot handle funds, all disbursals via regulated entity |
| Jun 2024 | RBI FLDG Framework | First-loss default guarantee capped at 5% of outstanding portfolio |
| May 2025 | RBI Digital Lending Directions (updated) | Enhanced disclosure, cooling-off period, grievance redressal |
| Staged 2025-26 | DPDP Act implementation | Data protection compliance for all FinTech, consent management |
| Ongoing | RBI Payment Aggregator licensing | PA license mandatory; deadline extensions for existing players |

---

## Section 9: Worked Example — "BNPL in India" Through FinTech Lens

### Standard Research Output (no FinTech lens):
```
Entries: 28
Categories: Market Overview (8), Consumer Behavior (6), Regulation (5), Risk (4), Technology (5)
Focus: What BNPL is, how it works, market trends, consumer adoption, basic regulatory environment
```

### FinTech Lens Research Output (same topic):
```
Entries: 42 (+14 FinTech-specific entries from enriched queries)
Categories: Same as above PLUS FinTech overlay
FinTech Dimensions:
  - Regulatory: 6 entries (RBI digital lending, FLDG cap, NBFC requirement, cooling-off period, state-level usury laws, DPDP Act impact)
  - Payment Rails: 4 entries (UPI Autopay for EMIs, merchant integration flows, NACH mandates, card-on-file tokenization)
  - Trust/Security: 3 entries (eKYC for thin-file, fraud patterns in BNPL, data privacy compliance)
  - Unit Economics: 5 entries (merchant discount rate 2-4%, late fee revenue, subvention model, break-even at 8-12 transactions/user/year, comparison with credit card interchange)
  - Acquisition: 4 entries (checkout integration conversion uplift 20-30%, merchant-funded acquisition, repeat rate benchmarks, category-specific adoption)
  - Embedded Finance: 3 entries (Shopify/Amazon BNPL integration, e-commerce embed vs standalone app, white-label BNPL-as-a-Service)
  - Credit Risk: 5 entries (30DPD delinquency 3-8% for prime, 12-20% for subprime, alternative data scoring for Gen Z, collection strategies, FLDG risk-sharing with merchants)
  - Financial Inclusion: 3 entries (credit-invisible users 200M+ in India, BNPL as credit-building tool, Tier 2-3 adoption patterns)
  - Cross-Border: 2 entries (cross-border e-commerce BNPL, FX settlement for international merchants)
  - Funding: 4 entries (BNPL ABS securitization growing, warehouse lending lines, co-lending with banks, venture funding for Indian BNPL down 60% from 2021 peak)

FinTech Executive Summary:
  THE OPPORTUNITY: 200M+ credit-invisible Indians can't get credit cards but shop online.
  BNPL fills the gap with instant checkout credit at ₹500-50,000 ticket sizes.

  THE REGULATION: RBI Digital Lending Guidelines require all BNPL providers to
  operate through regulated entities (NBFC). FLDG capped at 5%. Cooling-off period
  for loans >₹10,000. Non-compliance = license risk.

  THE UNIT ECONOMICS: Merchant discount rate 2-4% + late fees 1-2% of GMV.
  Break-even requires 8-12 transactions/user/year. Subvention models shift cost
  to merchant. Viable only at scale (>500K active users).

  THE RISK PROFILE: 30DPD delinquency 3-8% (prime), 12-20% (subprime/thin-file).
  FLDG cap means lender retains most risk. Alternative data scoring improves
  prediction by 15-25% for thin-file segments.

  BIGGEST RISKS:
  1. RBI regulatory tightening (lending rate cap speculation)
  2. Credit quality deterioration in subprime cohorts (30DPD >15%)
  3. Funding winter — venture + debt capital harder to access at current unit economics

  NEXT STEPS:
  1. Map NBFC partnership options (regulatory compliance)
  2. Build FLDG model at 5% cap — stress test credit quality scenarios
  3. Interview 15 merchants on checkout conversion uplift expectations
  4. Benchmark unit economics against Simpl, LazyPay, ZestMoney (shutdown lessons)
  5. Model break-even sensitivity on delinquency rates (3%, 5%, 8%, 12%)
```

---

**Last Updated**: 2026-03-25
**Status**: Production
