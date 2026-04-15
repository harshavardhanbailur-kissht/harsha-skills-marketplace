---
name: prd-mastery
description: Comprehensive Product Requirements Document (PRD) creation, review, and optimization covering all industries, methodologies, and best practices. Use when creating PRDs, product specs, feature requirements, user stories, technical specifications, or any product documentation. Covers Amazon PR-FAQ, Figma's approach, Shape Up pitches, Spotify DIBB, industry-specific requirements (healthcare, fintech, automotive, gaming, AI), accessibility/i18n, security specs, cross-functional collaboration, and AI-era PRD practices. Triggers for any PRD creation, review, template generation, or product specification task.
---

# PRD Mastery Skill

Complete guide for creating world-class Product Requirements Documents across all industries, company stages, and product types.

## Core Philosophy

**PRDs have evolved from 100-page waterfall specifications to living, collaborative artifacts that prioritize problems over solutions.** The best PRDs combine problem-centric thinking with measurable outcomes, cross-functional collaboration, and continuous updates.

### Critical Principle: Discovery Before Documentation

> "PRDs are written INSTEAD of discovery work—rather than after—represents the fundamental failure mode." — Marty Cagan

PRDs document validated problems and solutions, not replace the discovery process.

## Quick Start Workflow

### Step 1: Determine PRD Type Needed

| Context | PRD Type | Length |
|---------|----------|--------|
| Early startup | One-pager | 1 page |
| Feature addition | Lightweight PRD | 2-3 pages |
| Major initiative | Comprehensive PRD | 5-10 pages |
| Regulated industry | Compliance PRD | 10-20+ pages |
| AI product | AI-specific PRD | 3-5 pages + AI sections |

### Step 2: Select Framework

Choose based on company culture:
- **Amazon-style**: PR-FAQ (Working Backwards) — See `references/frameworks.md#amazon-pr-faq`
- **Startup velocity**: Shape Up Pitch — See `references/frameworks.md#shape-up`
- **Data-driven**: Spotify DIBB — See `references/frameworks.md#spotify-dibb`
- **Design-led**: Figma's approach — See `references/frameworks.md#figma-prd`
- **Traditional**: Comprehensive PRD — See `references/templates.md`

### Step 3: Load Relevant References

Based on product type, load appropriate reference files:
- **Industry-specific requirements**: `references/industry-requirements.md`
- **Accessibility/i18n**: `references/accessibility-i18n.md`
- **Security/performance**: `references/security-performance.md`
- **AI products**: `references/ai-era.md`
- **Cross-functional collaboration**: `references/collaboration.md`

## Universal PRD Structure

Every PRD should contain these sections (depth varies by context):

```
1. PROBLEM DEFINITION (Most important)
   - Problem statement with evidence
   - Customer pain points (productivity, financial, process, support)
   - Quantified impact
   - Customer quotes/research findings

2. GOALS & SUCCESS METRICS
   - Primary goal tied to company objectives
   - Success metrics with baselines and targets
   - Counter-metrics (guardrails)
   - Leading vs lagging indicators

3. NON-GOALS (Explicit scope boundaries)
   - What we're NOT building
   - Deferred features
   - Out-of-scope use cases

4. TARGET USERS
   - Primary persona(s)
   - Use cases and jobs-to-be-done
   - User journey context

5. SOLUTION
   - Proposed approach (not implementation details)
   - Key features/capabilities
   - User flows
   - Design references (embedded prototypes preferred)

6. REQUIREMENTS
   - Functional requirements
   - Non-functional requirements (performance, security, scalability)
   - Acceptance criteria (Given/When/Then format)
   - Edge cases

7. DEPENDENCIES & RISKS
   - Technical dependencies
   - Team dependencies
   - Key risks and mitigations
   - Open questions

8. TIMELINE & MILESTONES
   - Phase breakdown
   - Key milestones
   - Launch criteria
```

## PRD Writing Best Practices

### Language Rules
- Use Subject-Verb-Object format
- Active voice ("User enters data" not "Data is entered")
- Strong auxiliaries: "shall", "must", "will not" (not "may", "should", "could")
- Avoid adjectives without measurement ("fast", "intuitive", "user-friendly")
- Use parentheses for logical clarity: "(A and B) or C"

### Requirements Format
```
REQ-001: [Requirement Title]
Priority: Must-Have | Should-Have | Could-Have
Description: The system shall [specific behavior]
Acceptance Criteria:
  - Given [precondition]
  - When [action]
  - Then [expected result]
Rationale: [Why this matters]
```

### Metrics Specification
```
Metric: [Name]
Definition: [Precise calculation]
Baseline: [Current value]
Target: [Goal value]
Measurement: [How/when measured]
Owner: [Responsible party]
```

## Template Selection Guide

### By Company Stage

**Pre-seed/Seed**: Use `assets/templates/one-pager.md`
- Focus on MVP definition
- Informal, founder-driven
- 1-2 pages max

**Series A**: Use `assets/templates/lightweight-prd.md`
- Structured user stories
- Basic metrics section
- 2-3 pages

**Series B+/Enterprise**: Use `assets/templates/comprehensive-prd.md`
- Full stakeholder sign-off
- Compliance sections
- Traceability to test cases
- 5-10+ pages

### By Industry

Load `references/industry-requirements.md` for:
- **Healthcare**: FDA design controls, HIPAA, IEC 62304
- **Fintech**: PCI-DSS, KYC/AML, SOC 2
- **Automotive**: ISO 26262, ASPICE, SOTIF
- **Aviation**: DO-178C, DAL levels
- **Gaming**: GDD format, monetization specs
- **AI Products**: Model requirements, safety, bias testing

## Anti-Patterns to Avoid

See `references/anti-patterns.md` for complete list. Critical ones:

1. **Over-specification**: 50+ page PRDs nobody reads
2. **Solutioning too early**: Jumping to features before validating problem
3. **Missing success metrics**: Vague or unmeasurable goals
4. **No Non-Goals section**: Invites scope creep
5. **Static document**: Not updated as learning accumulates
6. **PRD instead of discovery**: Writing specs before customer validation

## Review Checklist

Before finalizing any PRD:

- [ ] Problem statement has quantified evidence
- [ ] Success metrics have baselines and targets
- [ ] Non-goals explicitly defined
- [ ] Acceptance criteria are testable
- [ ] Edge cases documented
- [ ] Dependencies identified
- [ ] Risks with mitigations listed
- [ ] Stakeholders reviewed and aligned
- [ ] Cross-functional input incorporated (Design, Eng, QA)

## Reference Files

Load these as needed:

| File | When to Use |
|------|-------------|
| `references/frameworks.md` | Choosing/implementing methodology |
| `references/templates.md` | Specific template examples |
| `references/industry-requirements.md` | Regulated or specialized industries |
| `references/case-studies.md` | Learning from iconic products |
| `references/accessibility-i18n.md` | Accessibility or multi-language |
| `references/security-performance.md` | Security or performance specs |
| `references/regional-practices.md` | Global/cultural considerations |
| `references/collaboration.md` | Cross-functional processes |
| `references/anti-patterns.md` | Common mistakes to avoid |
| `references/ai-era.md` | AI/ML product requirements |
| `references/version-control.md` | Change management |
| `references/metrics-quality.md` | Measuring PRD effectiveness |

## Asset Templates

Ready-to-use templates in `assets/templates/`:
- `one-pager.md` — Minimal PRD for startups
- `lightweight-prd.md` — Standard feature PRD
- `comprehensive-prd.md` — Full enterprise PRD
- `amazon-prfaq.md` — PR-FAQ format
- `shape-up-pitch.md` — Basecamp pitch format
- `ai-product-prd.md` — AI/ML specific template
