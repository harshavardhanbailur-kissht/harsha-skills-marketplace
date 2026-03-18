---
name: kissht-release-notes-mastery
description: |
  Comprehensive release notes generation, stakeholder-specific user guide creation, and Jira automation system for Kissht/Ring fintech products (LAP LOS, UP/Ring, Saral LSQ). Transforms raw Jira ticket data into tailored, AI-generated documentation for Product Managers, QA Engineers, Developers, Training Teams, Business Analysts, Operations, and Leadership.

  USE THIS SKILL WHEN the user mentions: release notes, release documentation, stakeholder guides, user guides from Jira, Kissht releases, LAP release notes, Ring release notes, ticket summaries, sprint documentation, changelog generation, release communication, training materials from releases, QA test impact notes, developer changelog, BA impact analysis, operations runbook from releases, Jira-to-documentation pipeline, automated release notes, release announcements, or when they want to generate any form of documentation from completed Jira tickets for different team roles.

  Also trigger when: building release note web apps, automating Jira webhook-to-docs pipelines, creating stakeholder-filtered views of releases, generating role-based release communications, or setting up scheduled release note generation that runs automatically when tickets are marked Done in Jira.
---

# Kissht Release Notes Mastery

A comprehensive system for transforming Jira ticket completions into stakeholder-specific release documentation, user guides, and automated communication pipelines for the Kissht/Ring fintech ecosystem.

## Architecture Overview

```
kissht-release-notes-mastery/
├── SKILL.md                          ← You are here (core workflow + orchestration)
├── references/
│   ├── stakeholder-profiles.md       ← Role definitions, needs, information density, frameworks
│   ├── content-generation.md         ← AI content patterns, NLP classification, tone per role
│   ├── jira-automation.md            ← Webhook setup, API patterns, GAS, scheduled generation
│   ├── kissht-domain.md              ← LAP LOS journey, terminology, RBI compliance, AA framework
│   ├── web-app-patterns.md           ← Web app generation, search, accessibility, cognitive load
│   └── orchestration-patterns.md     ← Pipeline state machine, sub-agents, quality scoring
├── scripts/
│   ├── generate_release_notes.py     ← Core: transforms ticket data → stakeholder docs
│   ├── jira_poller.py                ← Polls Jira for Done tickets, triggers generation
│   └── build_web_guide.py            ← Generates self-contained HTML stakeholder guide
├── templates/
│   ├── pm-guide.md                   ← Product Manager release template
│   ├── qa-guide.md                   ← QA impact & regression template
│   ├── dev-guide.md                  ← Developer changelog template
│   ├── training-guide.md             ← Training team SOP update template
│   ├── ba-guide.md                   ← Business Analyst impact analysis template
│   └── ops-guide.md                  ← Operations runbook update template
└── assets/
    └── guide-viewer.html             ← Self-contained web viewer template
```

## When to Load References

**ALWAYS load first:**
→ `references/stakeholder-profiles.md` (defines WHO gets WHAT)
→ `references/kissht-domain.md` (domain context for accurate content)

**Load based on task:**

| Task | Load |
|------|------|
| Generate stakeholder-specific guides | `references/content-generation.md` + relevant `templates/*.md` |
| Set up Jira automation pipeline | `references/jira-automation.md` |
| Build web app for guide access | `references/web-app-patterns.md` |
| Understand pipeline architecture | `references/orchestration-patterns.md` |
| Classify tickets with NLP | `references/content-generation.md` (NLP Classification section) |
| Check RBI compliance implications | `references/kissht-domain.md` (RBI Regulatory section) |
| Full end-to-end setup | Load ALL references |

## Core Workflow

### Phase 1: Understand the Release Context

Before generating anything, gather these inputs:

1. **Release data source** — One of:
   - CSV export from Google Sheets (LAP Release Notes Tracker)
   - Direct Jira JQL query results
   - Manual ticket list from the user
   - Webhook payload from Jira automation

2. **Target stakeholders** — Which roles need guides:
   - Product Manager (strategic impact, feature narrative, metrics)
   - QA Engineer (test impact, regression areas, edge cases)
   - Developer (technical changelog, code areas, API changes)
   - Training Team (SOP updates, user-facing changes, screenshots needed)
   - Business Analyst (process impact, journey changes, data flow)
   - Operations (runbook updates, monitoring changes, rollback info)
   - Leadership (executive summary, business impact, risk assessment)

3. **Release metadata** — Sprint/version, date range, project (LAP/UP/Ring)

### Phase 2: Classify & Enrich Tickets

For each ticket, determine:

**Feature Category** (from Kissht domain knowledge):
- Document Management, KYC & Identity, Sales PD & Property
- Credit & Bureau, Transaction & Sanction, LOS Panel & Operations
- Multi-Applicant & Top-Up, Data Consistency, General Fixes

**Journey Stage** (LAP loan lifecycle):
- Applicant Valid → Applicant Onboarded
- Applicant Onboarded → CPA Verified
- BRE Approved → CPA Verified
- Sales PD Complete
- IPA Pending → Disbursed

**Status Classification**:
- `Critical Fix` — Production blockers, financial accuracy, compliance
- `Live Now` — Feature enhancements, workflow improvements
- `Enhancement` — UX improvements, minor fixes

**Audience Impact** — Which roles are affected:
- Sales RM, BCM, CPA, Central Ops, Finance, Branch Ops, All Users

### Phase 3: Generate Stakeholder-Specific Content

Read `references/content-generation.md` for the full content generation patterns. The key principle: **same tickets, different stories**.

Each stakeholder guide transforms the same release data through a different lens:

**Product Manager** → Feature narrative, business metrics, adoption tracking
**QA Engineer** → Test matrix, regression scope, edge case identification
**Developer** → Technical changelog, code paths affected, API surface changes
**Training Team** → SOP deltas, user-facing behavior changes, screenshot lists
**Business Analyst** → Process flow changes, data model impacts, journey modifications
**Operations** → Monitoring changes, alert thresholds, rollback procedures

### Phase 4: Output Generation

Output options (user chooses):

1. **Individual Markdown guides** — One .md file per stakeholder
2. **Single HTML web app** — Self-contained viewer with role-based tabs (read `references/web-app-patterns.md`)
3. **Word documents** — Professional .docx per stakeholder (use docx skill)
4. **Automated pipeline** — Scheduled generation from Jira (read `references/jira-automation.md`)

### Phase 5: Automation Setup (Optional)

For teams that want release notes generated automatically when tickets are marked Done:

1. **Jira Webhook** → Google Apps Script → Sheets accumulation
2. **Scheduled Poll** → Python script checks Jira periodically
3. **Batch Generation** → On sprint close, generate all stakeholder guides
4. **Distribution** → Slack/email notification with guide links

Read `references/jira-automation.md` for complete setup including:
- Google Apps Script webhook receiver
- Jira automation rule configuration
- Scheduled polling with the `schedule` skill
- API-driven generation triggered by Jira status transitions

## Content Quality Standards

Every generated guide must:

1. **Be role-appropriate** — A QA engineer doesn't need business metrics; a PM doesn't need code paths
2. **Include ticket traceability** — Every claim links back to a specific Jira ticket
3. **Use Kissht terminology correctly** — LAP, LOS, Saral, LSQ, BRE, CPA, PD, CAM, KFS (see domain reference)
4. **Classify impact accurately** — Critical Fix vs Enhancement vs Live Now
5. **Be actionable** — Each guide tells the reader what THEY need to do differently
6. **Carry confidence tags** — Every AI-inferred claim must be tagged with confidence level (VERIFIED/HIGH/MEDIUM/LOW/UNKNOWN)
7. **Pass fintech hallucination check** — No fabricated financial figures, regulatory references, or system behaviors
8. **Meet the verification checklist** — Pre-publication checks in content-generation.md must all pass
9. **Flag RBI compliance implications** — Any ticket touching KFS, audit trails, data localization, or consent must be escalated to Leadership + BA
10. **Account for LAP vs UP differences** — Ensure classification respects product-specific patterns (see kissht-domain.md)

## Research-Backed Quality Framework

### COSTAR Content Generation Method
Every stakeholder guide is generated using the COSTAR framework (Context, Objective, Style, Tone, Audience, Response format). See `references/content-generation.md` for full implementation.

### Confidence Tagging System
All AI-generated content carries accuracy tags:
- `[✓]` VERIFIED — Directly from ticket data
- `[H]` HIGH — Strong inference from ticket + category
- `[M]` MEDIUM — Inferred from domain patterns
- `[L]` LOW — Extrapolated, may be inaccurate
- `[?]` UNKNOWN — Needs manual enrichment

### Verification Loops
Before publishing any guide:
1. Cross-check ticket counts against source data
2. Validate all Jira links resolve correctly
3. Verify no PII or credentials leaked into guides
4. Confirm financial figures trace to source (no fabrication)
5. Ensure domain terminology matches glossary
6. Run the pre-publication checklist from content-generation.md

### RBI Compliance Awareness
This skill includes RBI Digital Lending Directions awareness. Any change touching:
- Key Fact Statement (KFS) display
- Borrower consent or data sharing
- Account Aggregator integration
- Audit trail or transaction logging
- Data localization requirements

...is automatically flagged as compliance-critical and elevated in Leadership, BA, and Ops guides.

### Domain Priority Matrix
Classification uses weighted keyword scoring (see content-generation.md):
- High-confidence keywords (weight 3): Bureau, CIBIL, KYC, Saral sync, sanction
- Medium-confidence keywords (weight 2): LOS panel, smart view, field mapping
- Low-confidence keywords (weight 1): fix, issue, bug (catch-all)
- Score ≥ 3 = confident classification; < 3 = flag for manual review

## Task Detection Matrix

This skill auto-triggers based on user intent. Use this matrix to route to the correct workflow:

| User Intent | Primary Workflow | Load These References |
|------------|-----------------|----------------------|
| "Generate release notes from Jira" | Phase 1→5 full pipeline | stakeholder-profiles + kissht-domain + content-generation |
| "Create a QA guide for this sprint" | Single-stakeholder generation | stakeholder-profiles + content-generation + templates/qa-guide |
| "Set up Jira automation" | Automation setup | jira-automation |
| "Build a web app for release notes" | Web app generation | web-app-patterns + content-generation |
| "Classify these tickets" | Classification only | kissht-domain + content-generation (NLP section) |
| "What changed in this release?" | Quick summary (Leadership view) | stakeholder-profiles + templates/leadership-guide |
| "Create release notes for all stakeholders" | Full multi-guide generation | ALL references |
| "Automate weekly release notes" | Scheduled task setup | jira-automation + schedule skill |

## Orchestration Architecture

This skill follows a **state-driven pipeline** pattern (adapted from the Project Orchestrator skill):

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  ACCUMULATE │────→│   CLASSIFY   │────→│   GENERATE   │
│  (Jira data)│     │ (NLP + rules)│     │ (per-stakeholder)│
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                    ┌──────────────┐     ┌────────┴───────┐
                    │  DISTRIBUTE  │←────│    REVIEW      │
                    │ (Slack/email)│     │ (verification) │
                    └──────────────┘     └────────────────┘
```

Each phase creates a **checkpoint** enabling resume-after-failure. See `references/jira-automation.md` for the full state model.

### Quality Gates Between Phases

| Transition | Quality Gate |
|-----------|-------------|
| Accumulate → Classify | All ticket keys valid, no duplicates, minimum 5 tickets |
| Classify → Generate | >80% tickets classified with HIGH+ confidence, compliance flags set |
| Generate → Review | All stakeholder guides rendered, ticket counts match source |
| Review → Distribute | Pre-publication checklist passes (content-generation.md), no PII leaks |

## Verification-First Quality Framework

Adapted from the Codebase Handoff Documenter's confidence-first approach:

### Pre-Publication Verification (Mandatory)

Before ANY guide is shared with stakeholders:

1. **Ticket Integrity**: Every ticket key in guides exists in source data
2. **Count Accuracy**: Total tickets, bugs, stories match source exactly
3. **Financial Claims**: Zero fabricated numbers (interest rates, fees, thresholds)
4. **Domain Terminology**: All terms match `references/kissht-domain.md` glossary
5. **PII Check**: No real Aadhaar numbers, PAN numbers, phone numbers, or credentials
6. **Link Validity**: All Jira links are well-formed (`https://kissht.atlassian.net/browse/LAP-XXXX`)
7. **Compliance Flags**: All RBI-touching tickets flagged in Leadership, BA, and Ops guides
8. **Confidence Tags**: Every AI-inferred claim carries [✓]/[H]/[M]/[L]/[?] tag
9. **Audience Filtering**: No technical jargon in Training guide, no business metrics in Dev guide

### Hallucination Detection (8 Red Flags)

From deep research quality frameworks — watch for these in generated content:

1. **Overly specific stats without source** — "Improved performance by exactly 47.3%"
2. **Too-clean claims** — "Zero errors after deployment"
3. **Fabricated regulatory references** — "As per RBI circular..." without ticket evidence
4. **Unknown system names** — Systems not in kissht-domain.md architecture
5. **Date errors** — Future dates, impossible timelines
6. **Unattributed quotes** — "The team agreed..." without ticket evidence
7. **Score/threshold fabrication** — CIBIL thresholds not from ticket data
8. **Logical inconsistencies** — Same ticket classified differently in two guides

## Integration Points

This skill works with other skills:

- **docx skill** → For professional Word document output
- **xlsx skill** → For spreadsheet-based release trackers
- **pptx skill** → For release review presentation decks
- **schedule skill** → For automated periodic generation
- **frontend-blitz skill** → For building the web-based guide viewer (if complex UI needed)
- **mcp-builder skill** → For building a Jira MCP server for direct integration

## Quick Start Examples

**Example 1: "Generate release notes for the latest LAP sprint"**
1. Load `references/stakeholder-profiles.md` + `references/kissht-domain.md`
2. Ask user for ticket data source (CSV, Jira query, or ticket list)
3. Classify tickets by category, journey, and audience
4. Ask which stakeholders need guides
5. Generate using appropriate templates

**Example 2: "Set up automatic release note generation from Jira"**
1. Load `references/jira-automation.md`
2. Provide Google Apps Script for Jira webhook
3. Configure scheduled polling
4. Set up batch generation on sprint close
5. Create distribution channel (Slack/email)

**Example 3: "Build a web app where each team can access their release notes"**
1. Load `references/web-app-patterns.md`
2. Generate self-contained HTML with role-based tabs
3. Include search, filtering by date/category/priority
4. Add Jira deep-links for ticket traceability

**Example 4: "Create a training guide from the last release for the ops team"**
1. Load `references/content-generation.md` + `templates/training-guide.md`
2. Filter tickets to ops-relevant changes
3. Generate SOP update document with before/after behavior
4. Highlight mandatory training items vs informational
