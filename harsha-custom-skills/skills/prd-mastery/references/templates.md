# PRD Templates Reference

Complete collection of PRD templates from top practitioners and companies.

---

## Lenny Rachitsky's 1-Pager Template

### Philosophy
- Keep it short
- Problem statement first
- Continuously refer back to the problem

### Structure
```markdown
# [Feature Name] PRD

## Problem
[What problem are we solving? Include data/evidence.]

## Goals
[What does success look like?]

## Success Criteria
[How will we measure success?]
- Metric 1: [baseline] → [target]
- Metric 2: [baseline] → [target]

## Intended Audience
[Who is this for?]

## Proposed Solution
[High-level approach - leave room for team creativity]

## Key User Flows
[Critical paths through the feature]

## Non-Goals
[What we're explicitly NOT doing]

## Open Questions
[What we still need to figure out]

## Timeline
[Key milestones]
```

### Available On
- Atlassian Confluence template
- Google Doc template

---

## Kevin Yien's PRD (Stripe/Square)

### 5-Stage Status System
| Stage | Purpose |
|-------|---------|
| Draft | Initial problem framing |
| Problem Review | Stakeholder alignment on problem |
| Solution Review | Validate proposed approach |
| Launch Review | Pre-release readiness |
| Launched | Post-ship documentation |

### Structure
```markdown
# [Feature Name]

**Status:** [Draft | Problem Review | Solution Review | Launch Review | Launched]
**Author:** [Name]
**Last Updated:** [Date]

## Background
[Context and history. Why are we looking at this now?]

## Problem Statement
[Clear articulation of the problem. Include data.]

## Goals
### Primary Goal
[The main outcome we're trying to achieve]

### Secondary Goals
[Additional benefits]

### Non-Goals
[Explicit exclusions - "drawing the perimeter of the solution space"]

## Success Metrics
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| [Name] | [Current] | [Goal] | [How measured] |

## Proposed Solution
[High-level approach. Think of this like drawing the perimeter of the solution space.]

### User Experience
[How users will interact with this]

### Technical Approach
[High-level technical direction]

## Alternatives Considered
[Other approaches we evaluated and why we didn't choose them]

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk] | [H/M/L] | [H/M/L] | [How addressed] |

## Dependencies
[Other teams, systems, or features this depends on]

## Timeline
| Milestone | Target Date |
|-----------|-------------|
| [Phase 1] | [Date] |
| [Phase 2] | [Date] |
| [Launch] | [Date] |

## Open Questions
- [ ] [Question 1]
- [ ] [Question 2]

## Appendix
[Supporting materials, research, designs]
```

---

## Figma PRD Template (Yuhki Yamashita)

### Structure
```markdown
# [Feature Name] Product Spec

## Phase 1: Problem Alignment

### Problem Statement
[What customer problem are we solving?]

### Why Now?
[Why is this the right time to solve this?]

### Goals
#### Measurable
- [OKR-style goal 1]
- [OKR-style goal 2]

#### Immeasurable (Equally Important)
- [Quality goal]
- [User sentiment goal]

### Success Criteria
[How we'll know we succeeded]

---

## Phase 2: Solution Alignment

### Key Features
| Feature | Description | Priority |
|---------|-------------|----------|
| [Feature] | [What it does] | [Must/Should/Could] |

### User Flows
[Embedded Figma prototypes here - LIVE, not static]

### Edge Cases
| Scenario | Behavior |
|----------|----------|
| [Edge case] | [Expected behavior] |

### Technical Considerations
[Architecture notes, API needs, performance requirements]

---

## Phase 3: Launch Readiness

### Cross-Functional Checklist
- [ ] **Legal**: [Approval status]
- [ ] **Security**: [Review status]
- [ ] **Privacy**: [GDPR/CCPA compliance]
- [ ] **Marketing**: [Launch materials ready]
- [ ] **Support**: [Documentation/training complete]
- [ ] **Analytics**: [Instrumentation complete]

### Rollout Plan
| Stage | Audience | Criteria to Advance |
|-------|----------|---------------------|
| Alpha | Internal | [Criteria] |
| Beta | 5% users | [Criteria] |
| GA | 100% | [Criteria] |
```

---

## Asana Spec Template (Jackie Bavaro)

### Structure
```markdown
# [Feature Name] Spec

## The Opportunity
[What's the opportunity we're pursuing?]

## Problem Statement
[Specific problem with evidence]

## Hypothesis
We believe [hypothesis]
We'll know we're right if [success criteria]

## Narrative Vision
[Story of how this will work for a real user. Day-in-the-life format.]

## User Stories
As a [persona],
I want [capability],
So that [benefit].

### Acceptance Criteria
- Given [context]
- When [action]
- Then [result]

## Scope

### In Scope
- [Feature 1]
- [Feature 2]

### Out of Scope
- [Exclusion 1]
- [Exclusion 2]

## Design
[Link to designs or embedded mockups]

## Technical Approach
[Engineering perspective on implementation]

## Metrics & Analytics
| Event | Trigger | Properties |
|-------|---------|------------|
| [Event name] | [When fired] | [Data captured] |

## Launch Plan
[Rollout strategy]

## Risks
[What could go wrong]
```

---

## Intercom One-Pager

### Constraint
MUST fit on single A4 page.

### Structure
```markdown
# [Feature Name]

## Job Story
When [situation],
I want to [motivation],
So I can [expected outcome].

## Problem (2-3 sentences max)
[Clear, concise problem statement]

## Solution (2-3 sentences max)
[High-level approach]

## Success Metrics
- [Metric 1]: [target]
- [Metric 2]: [target]

## Key Risks
- [Risk 1]
- [Risk 2]

## Timeline
[Single line with key date]
```

---

## Linear PRD Template

### Structure
```markdown
# [Feature Name]

## Context
[The fundamental "why" - strategic context, market situation]

## Usage Scenarios

### Scenario 1: [Name]
[Narrative description of real user situation]

### Scenario 2: [Name]
[Another usage narrative]

## Milestones
| Phase | Deliverable | Target |
|-------|-------------|--------|
| 1 | [What ships] | [When] |
| 2 | [What ships] | [When] |
```

---

## HashiCorp PRD Template

### Structure
```markdown
# [Feature Name] PRD

## Status
[Draft | In Review | Approved | Implementing]

## Overview
[Brief description]

## User Research (Most Important Section)
### Research Findings
[What we learned from users]

### User Quotes
> "[Direct quote]" — [User role]

### Pain Points Identified
1. [Pain point]
2. [Pain point]

## Requirements

### Functional Requirements
| ID | Requirement | Priority | Questions for RFC |
|----|-------------|----------|-------------------|
| FR-1 | [Requirement] | [P0/P1/P2] | [What RFC needs to answer] |

### Non-Functional Requirements
| Category | Requirement |
|----------|-------------|
| Performance | [Spec] |
| Security | [Spec] |
| Scalability | [Spec] |

## Acceptance Criteria
[Written like test cases - objective so anyone can validate]

## RFC Questions
[Specific questions the RFC (how to build) must answer]
```

---

## DoorDash Launch Document

### Structure
```markdown
# [Feature Name] Launch Brief

## DRI (Directly Responsible Individual)
[Name]

## Problem
[What problem are we solving?]

## Approach
[High-level solution]

## Expected Impact
[Quantified benefit]

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|

## Launch Phases

### Phase 1: Testing Party
- Internal testing with employees
- [Specific test scenarios]

### Phase 2: Dogfooding
- Extended internal use
- [Feedback collection plan]

### Phase 3: Limited Launch
- [% of users]
- [Geographic scope]

### Phase 4: Full Launch
- [Rollout criteria]

## Launch Readiness Checklist
- [ ] Engineering complete
- [ ] QA sign-off
- [ ] Design approval
- [ ] Legal review
- [ ] Marketing ready
- [ ] Support trained
- [ ] Metrics instrumented
- [ ] Rollback plan documented
```

---

## Shopify GSD (Get Shit Done) Format

### Structure
```markdown
# [Feature Name]

## OK1 Review
**Reviewers:** [Directors from Product, UX, Engineering, Data]

## Vision
[Written from merchant perspective: "Here's why I love Shopify because..."]

## Problem
[Merchant pain point]

## Solution
[Approach - may include "zero metrics attached" for quality-focused work]

## Theme Alignment
[How this connects to CEO's yearly theme]

## OK2 Review
**Reviewers:** [Senior leadership]
```

---

## Amazon 6-Pager Format

### Rules
- Maximum 6 pages narrative
- No bullet points - full sentences and paragraphs
- Appendix can be unlimited
- Read silently for 15-30 minutes at meeting start
- Discussion follows reading
- Senior people speak last

### Structure
```markdown
# [Initiative Name]

## Introduction
[Set the context. What is this about?]

## Goals
[What are we trying to achieve? Be specific.]

## Tenets
[Principles that will guide decisions]

## State of the Business
[Current situation with data]

## Lessons Learned
[What have we learned from past attempts?]

## Strategic Priorities
[Key focus areas]

## Appendix
[Supporting data, charts, detailed analysis - unlimited length]
```

---

## Shreyas Doshi Pre-mortem Template

### Structure
```markdown
# [Feature Name] Pre-mortem

## Assume: It's 6 months from now and this project failed.

### What went wrong?
[List all possible failure modes]

### Category: Unclear Problem
- [ ] We didn't validate the problem existed
- [ ] We solved the wrong problem
- [ ] Market changed

### Category: Execution
- [ ] Took too long
- [ ] Quality issues
- [ ] Technical blockers

### Category: Adoption
- [ ] Users didn't understand it
- [ ] Didn't solve their actual workflow
- [ ] Better alternatives emerged

### Mitigations
| Failure Mode | Prevention | Detection |
|--------------|------------|-----------|
| [Mode] | [How to prevent] | [How to detect early] |
```

---

## Enterprise PRD Template (Regulated)

### Structure
```markdown
# [Feature Name] Product Requirements Document

**Document ID:** PRD-[YYYY]-[NNN]
**Version:** [X.Y.Z]
**Status:** [Draft | Review | Approved | Implemented]
**Classification:** [Public | Internal | Confidential]

## Document Control
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | [Date] | [Name] | Initial version |

## Approvals
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Engineering Lead | | | |
| Security | | | |
| Legal | | | |
| Compliance | | | |

## 1. Executive Summary
[Brief overview for executives]

## 2. Business Context
### 2.1 Background
### 2.2 Business Objectives
### 2.3 Success Metrics
### 2.4 ROI Analysis

## 3. Scope
### 3.1 In Scope
### 3.2 Out of Scope
### 3.3 Future Considerations

## 4. Requirements
### 4.1 Functional Requirements
[Numbered, traceable requirements]

### 4.2 Non-Functional Requirements
#### 4.2.1 Performance
#### 4.2.2 Security
#### 4.2.3 Scalability
#### 4.2.4 Availability
#### 4.2.5 Compliance

### 4.3 Integration Requirements
### 4.4 Data Requirements
### 4.5 Reporting Requirements

## 5. User Experience
### 5.1 User Personas
### 5.2 User Journeys
### 5.3 Wireframes/Mockups

## 6. Technical Architecture
[High-level technical approach]

## 7. Security & Compliance
### 7.1 Security Requirements
### 7.2 Regulatory Compliance
### 7.3 Data Privacy

## 8. Testing Requirements
### 8.1 Acceptance Criteria
### 8.2 Test Scenarios

## 9. Implementation Plan
### 9.1 Phases
### 9.2 Timeline
### 9.3 Resources

## 10. Risks & Mitigations

## 11. Dependencies

## 12. Appendices
### A. Glossary
### B. References
### C. Supporting Documentation

## Requirements Traceability Matrix
| Req ID | Description | Test Case | Status |
|--------|-------------|-----------|--------|
| FR-001 | [Requirement] | TC-001 | [Status] |
```
