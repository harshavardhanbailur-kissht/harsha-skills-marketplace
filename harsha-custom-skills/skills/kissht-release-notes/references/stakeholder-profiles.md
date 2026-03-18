# Stakeholder Profiles & Information Needs

## Table of Contents
1. [Product Manager](#product-manager)
2. [QA Engineer](#qa-engineer)
3. [Developer](#developer)
4. [Training Team](#training-team)
5. [Business Analyst](#business-analyst)
6. [Operations Team](#operations-team)
7. [Leadership](#leadership)
8. [Information Density Matrix](#information-density-matrix)

---

## Product Manager

**Role context**: Owns product vision, prioritization, and stakeholder communication. Needs to understand what shipped, why it matters, and how to communicate it to business stakeholders.

**Information needs**:
- Feature narrative: What changed and why it matters for the business
- Metrics impact: How changes affect conversion, TAT, error rates, user satisfaction
- Adoption requirements: Does this need user training, communication, or feature flags?
- Dependencies: Were there cross-team or cross-system dependencies?
- Strategic alignment: How does this release move the product roadmap forward?

**Tone**: Strategic, outcome-focused, business-impact language. Avoid deep technical details.

**Structure preferences**:
- Executive summary (3-5 bullets, biggest wins)
- Feature-by-feature breakdown grouped by theme
- Metrics dashboard (before/after where available)
- Stakeholder communication draft
- What's next / upcoming releases preview

**Critical fields per ticket**:
- Release Note Title (grouped by announcement)
- Business Context (1-sentence enrichment)
- Audience Impact (which user roles affected)
- Status Badge (Critical Fix / Live Now / Enhancement)
- Cycle Time (delivery velocity signal)

---

## QA Engineer

**Role context**: Validates releases, owns regression testing, catches edge cases. Needs to understand exactly what changed, where the risk is, and what to test.

**Information needs**:
- Technical change scope: Which modules, APIs, forms, and data flows were modified
- Regression surface: What existing functionality could be affected
- Edge cases: Co-applicant flows, boundary values, error states
- Test data requirements: What test scenarios need specific data setups
- Environment considerations: Staging vs production differences

**Tone**: Precise, technical, risk-aware. Emphasize what could break.

**Structure preferences**:
- Change impact matrix (module × change type × risk level)
- Regression test scope (prioritized by risk)
- New test cases needed (with acceptance criteria)
- Known limitations / edge cases
- Test environment setup notes

**Critical fields per ticket**:
- Summary (exact bug/feature description)
- Feature Category (module affected)
- Journey Stage (which flow to test)
- Priority (Highest = highest regression risk)
- Issue Type (Bug vs Story = different test approach)

---

## Developer

**Role context**: Implements features, fixes bugs, maintains codebase. Needs to understand what was deployed, code areas affected, and any technical debt implications.

**Information needs**:
- Code changes: Which services, modules, APIs were modified
- Data model changes: Schema updates, migration requirements
- API surface: New endpoints, changed parameters, deprecations
- Configuration changes: Feature flags, environment variables, settings
- Technical debt: Workarounds that need future cleanup

**Tone**: Technical, concise, code-aware. Reference specific systems and data flows.

**Structure preferences**:
- Technical changelog (grouped by service/module)
- Breaking changes (if any)
- Migration notes
- API documentation updates needed
- Code review observations / patterns

**Critical fields per ticket**:
- Summary (technical description)
- Feature Category (code module)
- Assignee (developer who implemented — point of contact for questions)
- Contributors (who else touched the code)
- Ticket Link (direct access to implementation details)

---

## Training Team

**Role context**: Creates and maintains SOPs, user guides, and training materials. Needs to understand what users will experience differently and what training materials need updating.

**Information needs**:
- User-visible changes: What does the user see/do differently?
- Before/after behavior: Exact description of old vs new behavior
- Screenshot requirements: Which screens changed and need new screenshots
- SOP updates needed: Which SOPs are affected by this release
- Training urgency: Is this a critical change that needs immediate training?

**Tone**: User-friendly, step-by-step, process-oriented. Write as if explaining to the end user.

**Structure preferences**:
- "What Changed" summary (user-facing language only)
- SOP update checklist (which documents to update)
- Before/After comparison table
- Screenshot requirements list
- Training priority (Mandatory / Recommended / Informational)
- FAQ: "What if users ask about X?"

**Critical fields per ticket**:
- Business Context (user-facing description)
- Audience Impact (which user roles need training)
- Journey Stage (which process flow changed)
- Status Badge (Critical Fix = mandatory training)
- Release Note Title (grouping for training modules)

---

## Business Analyst

**Role context**: Bridges business requirements and technical implementation. Needs to understand how changes affect business processes, data flows, and system integrations.

**Information needs**:
- Process impact: Which business processes are affected
- Journey modifications: Changes to the loan lifecycle stages
- Data flow changes: How data moves differently between systems
- Integration impacts: Saral ↔ LOS, LSQ ↔ LAP, AA, Bureau connections
- Requirements traceability: Do changes fulfill the original BRD/PRD?

**Tone**: Analytical, process-oriented, data-aware. Map changes to business rules.

**Structure preferences**:
- Process impact assessment (per journey stage)
- Data flow diagrams (if applicable)
- Integration change summary
- Requirements coverage matrix
- Gap analysis (what was supposed to ship vs what shipped)

**Critical fields per ticket**:
- Journey Stage (process mapping)
- Feature Category (business domain)
- Business Context (change rationale)
- Summary (requirement description)
- Related tickets (dependency mapping)

---

## Operations Team

**Role context**: Manages day-to-day system operations, incident response, and production monitoring. Needs to understand operational impact and any runbook changes.

**Information needs**:
- Deployment details: When was this released, any downtime?
- Monitoring changes: New alerts, changed thresholds, new dashboards
- Rollback plan: How to revert if issues arise
- Manual intervention: Any one-time actions needed post-release
- Known issues: Outstanding bugs or limitations in this release

**Tone**: Operational, action-oriented, incident-aware. Focus on "what do I need to do."

**Structure preferences**:
- Deployment summary (date, version, environment)
- Operational checklist (pre/post deployment actions)
- Monitoring & alerting changes
- Rollback procedure
- Known issues & workarounds
- Escalation contacts

**Critical fields per ticket**:
- Priority (Highest = ops-critical)
- Status Badge (Critical Fix = production impact)
- Assignee (escalation contact)
- Feature Category (system area)
- Cycle Time (was this a rushed fix?)

---

## Leadership

**Role context**: Strategic oversight, resource allocation, risk management. Needs high-level understanding of release quality, team velocity, and business impact.

**Information needs**:
- Executive summary (1 paragraph)
- Key metrics: Tickets shipped, bug/feature ratio, cycle time trends
- Business impact: Revenue, compliance, user satisfaction implications
- Risk assessment: Any outstanding high-priority issues
- Team performance: Delivery velocity, cross-team collaboration

**Tone**: Executive, concise, metrics-driven. No technical details.

**Structure preferences**:
- 1-paragraph executive summary
- Key numbers dashboard
- Top 3 wins and top 3 risks
- Team shoutouts
- Next sprint preview

---

## Information Density Matrix

This matrix defines how much detail each stakeholder gets for each data dimension:

| Dimension | PM | QA | Dev | Training | BA | Ops | Leadership |
|-----------|----|----|-----|----------|----|----|-----------|
| Technical Detail | Low | High | Full | None | Medium | Medium | None |
| Business Impact | Full | Low | Low | Medium | Full | Low | Full |
| User-Facing Changes | High | Medium | Low | Full | High | Low | Medium |
| Test Implications | Low | Full | Medium | None | Low | Low | None |
| Code References | None | Medium | Full | None | None | Medium | None |
| Process Changes | High | Low | Low | High | Full | Medium | Medium |
| Metrics/Data | High | Medium | Low | Low | High | Medium | Full |
| Risk Assessment | Medium | High | Medium | Low | Medium | Full | High |
| Action Items | Medium | Full | Medium | Full | Medium | Full | Low |

**Reading the matrix**: "Full" means include comprehensive detail. "None" means actively exclude this dimension — it's noise for this stakeholder.

## Stakeholder Priority by Release Type

When generating guides, prioritize stakeholders based on release content:

| Release Contains | Priority Stakeholders |
|-----------------|----------------------|
| Critical production fixes | Ops → QA → Dev → PM → Leadership |
| New features | PM → Training → BA → QA → Dev |
| UI/UX improvements | Training → PM → QA → BA |
| Data/integration fixes | Dev → BA → QA → Ops |
| Compliance changes | Leadership → BA → Training → PM → QA |
| Performance improvements | Dev → Ops → QA → PM |
| RBI regulatory updates | Leadership → BA → Ops → Training → PM → QA |
| Security/data privacy | Ops → Dev → Leadership → BA → QA |
| Account Aggregator changes | Dev → BA → QA → PM → Training |

---

## Research-Backed Stakeholder Frameworks

### PM: RICE Prioritization Integration
When generating PM guides, map release items to RICE dimensions:
- **Reach**: How many users/borrowers does this change affect?
- **Impact**: Scale 1-3 (1=minimal, 2=moderate, 3=massive)
- **Confidence**: VERIFIED (tested in prod), HIGH (QA passed), MEDIUM (logic inferred), LOW (untested edge case)
- **Effort**: Cycle time as proxy (< 3 days = low, 3-10 = medium, 10+ = high)

### QA: ISTQB-Aligned Test Classification
Map changes to ISTQB test levels for QA guides:
- **Unit-level changes** → Developer-owned, mention in Dev guide only
- **Integration-level** → API contract changes, Saral↔LOS sync → P1 QA focus
- **System-level** → End-to-end journey changes → Full regression scope
- **Acceptance-level** → User-facing behavior changes → Training + QA co-validation

Risk-based test prioritization (ISO 29119 aligned):
- **Likelihood** × **Impact** = Test Priority
- High likelihood + High impact = P1 Mandatory
- High likelihood + Low impact = P2 Standard
- Low likelihood + High impact = P2 Standard (but monitor closely)
- Low likelihood + Low impact = P3 Smoke test only

### Ops: SRE Runbook Patterns (Google SRE Handbook)
Structure Ops guides following SRE best practices:
- **Service-Level Indicators (SLIs)**: What metrics define "working" for this change
- **Error Budget Impact**: Does this release consume error budget?
- **Toil Reduction**: Did this release automate any manual operational work?
- **Incident Playbook**: If this breaks, what's the 5-step response?

### Training: Kirkpatrick L&D Model
Classify training needs using Kirkpatrick levels:
- **Level 1 — Reaction**: Will users notice this change? → Informational communication
- **Level 2 — Learning**: Do users need new knowledge? → SOP update + FAQ
- **Level 3 — Behavior**: Do users need to change workflow? → Mandatory training session
- **Level 4 — Results**: Will this affect business KPIs? → Track adoption metrics post-training

### BA: Value Stream Mapping
For BA guides, map changes to the value stream:
- **Lead Time**: From ticket creation to production (full pipeline)
- **Process Time**: Actual development + testing time
- **Wait Time**: Time in queues (code review, QA queue, deployment queue)
- **%C&A** (% Complete & Accurate): Were requirements fully met? Track partial deliveries.

### Leadership: Balanced Scorecard Alignment
Map releases to balanced scorecard perspectives:
- **Financial**: Revenue impact, cost reduction, compliance penalty avoidance
- **Customer**: Borrower experience improvement, NPS-affecting changes
- **Internal Process**: TAT reduction, automation gains, manual work eliminated
- **Learning & Growth**: New capabilities, tech debt reduction, team skill development

---

## Confidence Level System

Every AI-generated content item in stakeholder guides must carry a confidence tag:

| Level | Tag | Meaning | Action |
|-------|-----|---------|--------|
| VERIFIED | `[✓]` | Directly supported by ticket data, tested in prod | Use as-is |
| HIGH | `[H]` | Strong inference from ticket summary + category | Review recommended |
| MEDIUM | `[M]` | Inferred from domain patterns, not explicit in data | PM/BA should validate |
| LOW | `[L]` | Extrapolated from similar tickets, may be inaccurate | Must verify before publishing |
| UNKNOWN | `[?]` | Cannot determine from available data | Flag for manual enrichment |

Rules for confidence assignment:
- Ticket summary explicitly states the change → VERIFIED
- Category + journey stage implies the change → HIGH
- Similar tickets in the past had this pattern → MEDIUM
- Inferred from general domain knowledge → LOW
- No data supports this claim → UNKNOWN (or omit entirely)

**Fintech-specific hallucination prevention**: NEVER generate specific numbers (interest rates, fee amounts, score thresholds, regulatory limits) unless they appear verbatim in ticket data. For financial figures, always tag as [?] unless VERIFIED.

---

## AMEC Integrated Evaluation Framework

Use AMEC (Association for Measurement and Evaluation of Communication) principles to measure stakeholder guide effectiveness:

| Dimension | Metric | How to Measure |
|-----------|--------|----------------|
| **Outputs** | Guides generated per sprint | Count of stakeholder docs produced |
| **Out-takes** | Guide access rate per stakeholder | Track tab views in web app (analytics) |
| **Outcomes** | Action completion rate | % of SOP updates completed after Training guide |
| **Organizational Impact** | Sprint quality improvement | Bug escape rate trending down over sprints |

### Stakeholder Engagement Scoring

Each guide should be evaluated post-release on these dimensions:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Actionability** | 30% | Does the reader know exactly what to do after reading? |
| **Accuracy** | 25% | Are all ticket references, counts, and claims correct? |
| **Relevance** | 20% | Was role-irrelevant information filtered out? |
| **Timeliness** | 15% | Was the guide available within 24h of sprint close? |
| **Completeness** | 10% | Were all Done tickets accounted for in the guide? |

### Multi-Channel Distribution Matrix

| Stakeholder | Primary Channel | Secondary Channel | Format Preference |
|------------|----------------|-------------------|-------------------|
| PM | Slack #product-releases | Email digest | Web app (PM tab) |
| QA | Slack #qa-releases | Confluence page | Markdown + checklist |
| Dev | Slack #dev-releases | Git tag changelog | Keep-a-Changelog format |
| Training | Email (mandatory) | Slack #training-updates | Word doc + SOP checklist |
| BA | Email | Confluence wiki | Process flow diagrams |
| Ops | PagerDuty note / Slack #ops | Runbook update PR | Markdown runbook format |
| Leadership | Email (exec summary) | Monthly deck | 1-page PDF brief |

### Kissht-Specific Contributor Recognition Patterns

From analysis of 693+ Kissht LAP tickets:
- **Top 5 assignees handle ~53% of all tickets** — Recognize these contributors prominently in Dev + Leadership guides
- **9 distinct feature categories** identified — Use for consistent grouping across all guides
- **8 release announcement groups** typical per sprint — Optimal for PM narrative structure
- **Bug:Story ratio of ~2:1** — Most sprints are fix-heavy; frame PM guides accordingly (reliability narrative, not feature narrative)
- **73.6% of tickets lack linked epics** — Classification must rely on keyword-based NLP, not epic grouping
