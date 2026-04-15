# Cross-Functional Collaboration for PRDs

Complete guide for collaborative PRD development across teams and functions.

---

## The Product Trio Model

### Definition
**Product Trio = PM + Design Lead + Engineering Lead**

The core decision-making unit for product development.

### Responsibilities

| Role | PRD Contribution |
|------|------------------|
| **Product Manager** | Problem definition, success metrics, prioritization, stakeholder alignment |
| **Design Lead** | User experience, flows, prototypes, usability requirements |
| **Engineering Lead** | Technical feasibility, architecture constraints, implementation approach |

### Collaboration Principles

**From Teresa Torres (Continuous Discovery Habits):**
- Weekly customer touchpoints together
- Joint discovery sessions
- Shared ownership of outcomes
- Collaborative decision-making

**Atlassian Triad Model:**
- Full autonomy to make decisions without manager sign-off
- Designers and developers pair to tackle work chunks
- No handoffs—continuous collaboration

---

## Spotify's TPD Trio

**Tribe Level: TPD = Tribe Lead + Product Lead + Design Lead**

### Structure
```
Company Level
    ↓
Tribe (collection of squads)
    - TPD Trio (strategic alignment)
    ↓
Squad (execution team)
    - Product Trio (tactical decisions)
```

### Alliances
- Form when multiple Trios collaborate on larger projects
- Temporary structures for cross-cutting initiatives
- Dissolve when project completes

---

## Decision-Making Frameworks

### DACI (Developed at Intuit)

| Role | Responsibility |
|------|----------------|
| **D**river | Corrals stakeholders, collates information, drives to decision |
| **A**pprover | Has final say, one person only |
| **C**ontributors | Provide expertise and input, no decision authority |
| **I**nformed | Need updates, no direct involvement |

**McKinsey Finding:** Projects using DACI have 25% higher success rates.

### RACI for PRDs

| Stakeholder | Role |
|-------------|------|
| Product Manager | **R**esponsible (writes/owns) |
| Engineering Lead | **C**onsulted |
| Design Lead | **C**onsulted |
| Executive Sponsor | **A**ccountable |
| QA Lead | **I**nformed |
| Legal | **I**nformed or **C**onsulted |
| Marketing | **I**nformed |
| Customer Success | **I**nformed or **C**onsulted |

### Amazon's "Disagree and Commit"
- Debate thoroughly
- Once decision made, full commitment from all
- No revisiting unless new information emerges
- Senior people speak last in discussions

---

## Engineering Collaboration

### Early Involvement Principles

**Problem:**
> "If you're just using your engineers to code, you're only getting about half their value." — Marty Cagan

**Solution:**
- Include engineers in discovery
- Share problem definition before solution
- Seek technical perspective on feasibility
- Value engineering input on approach

### Engineer PRD Input

**What Engineers Should Contribute:**
- Technical feasibility assessment
- Architecture implications
- Dependency identification
- Effort estimation ranges
- Risk identification
- Performance considerations
- Technical debt implications

### Technical Feasibility Reviews

```markdown
## Technical Review Checklist
- [ ] Architecture fits existing patterns
- [ ] No blocking technical dependencies
- [ ] Performance requirements achievable
- [ ] Security requirements implementable
- [ ] Scale requirements addressed
- [ ] Data model implications understood
- [ ] API design reviewed
- [ ] Integration points identified
```

---

## Design Collaboration

### Design-PRD Integration

**Modern Approach: Prototype as PRD**
- Figma embeds in PRD (live updates)
- Interactive prototypes > static mockups
- Design and requirements co-evolve
- Designers participate in requirements definition

### Design Review Process

```markdown
## Design Review Stages
1. **Conceptual Review**
   - Problem framing
   - Initial directions (3+ options)
   - Alignment on approach

2. **Detailed Review**
   - User flows complete
   - Edge cases addressed
   - Component specifications
   - Accessibility reviewed

3. **Final Review**
   - Pixel-perfect specifications
   - Animation/interaction details
   - Developer handoff ready
   - Design QA criteria defined
```

### Design Handoff Specifications
- Component library references
- Spacing and layout rules
- Color tokens
- Typography specifications
- Responsive breakpoints
- Interaction states
- Animation timing

---

## QA Collaboration

### Shift-Left Testing

**QA Involvement Timeline:**
| Phase | QA Activity |
|-------|-------------|
| Requirements | Review for testability |
| Design | Review for edge cases |
| Development | Create test cases |
| Implementation | Continuous testing |
| Release | Regression testing |

### QA Requirements Review

**What QA Should Validate:**
- Completeness of requirements
- Correctness of logic
- Consistency across features
- Testability of acceptance criteria
- Traceability to test cases

### Requirements Traceability Matrix (RTM)

```markdown
| Req ID | Requirement | Test Cases | Status |
|--------|-------------|------------|--------|
| FR-001 | [Requirement text] | TC-001, TC-002 | Draft |
| FR-002 | [Requirement text] | TC-003 | Approved |
```

**RTM Benefits:**
- Ensures test coverage
- Identifies gaps
- Supports regression analysis
- Enables impact analysis for changes

---

## Legal & Compliance Collaboration

### When to Involve Legal

**Trigger Conditions:**
- New data collection
- Third-party integrations
- Payment processing
- User-generated content
- International expansion
- Terms of service changes
- Privacy policy updates
- Contractual obligations
- Regulated industries

### Legal Review Process

```markdown
## Legal Review Request
- Feature summary (1 paragraph)
- Data handling description
- Privacy implications
- Risk assessment (PM perspective)
- Timeline constraints
- Specific questions for legal
```

### Compliance Integration

**PRD Compliance Section:**
```markdown
## Compliance Requirements

### Applicable Regulations
- [ ] GDPR
- [ ] CCPA
- [ ] HIPAA
- [ ] PCI-DSS
- [ ] SOX
- [ ] Other: ___

### Compliance Activities
| Activity | Owner | Status |
|----------|-------|--------|
| Privacy review | Legal | Pending |
| Security review | Security | Pending |
| Data classification | Data team | Complete |

### Documentation Required
- [ ] Privacy Impact Assessment
- [ ] Security Assessment
- [ ] Compliance sign-off
```

---

## Marketing & GTM Collaboration

### Product-Marketing Alignment

**Marketing Input to PRD:**
- Target segment validation
- Competitive positioning
- Messaging requirements
- Launch timing constraints
- Pricing considerations

**PRD Output for Marketing:**
- Feature descriptions (customer-facing)
- Value propositions
- Use cases for messaging
- Launch criteria

### GTM Section Template

```markdown
## Go-to-Market Requirements

### Target Audience
- Primary segment: [description]
- Secondary segment: [description]

### Positioning
- Category: [how this is categorized]
- Key differentiators: [list]
- Competitive comparison: [brief]

### Launch Requirements
- [ ] Marketing materials ready
- [ ] Sales enablement complete
- [ ] Support documentation
- [ ] Customer communication plan

### Success Metrics (Marketing)
- Awareness: [metric]
- Adoption: [metric]
- Engagement: [metric]
```

---

## Customer Success Collaboration

### Customer Success Input

**What CS Should Contribute:**
- Common customer pain points
- Feature requests patterns
- Support ticket analysis
- Customer feedback themes
- Churn risk factors
- Expansion opportunities

### Customer Success Requirements

```markdown
## Support Requirements

### Documentation
- [ ] Help center articles
- [ ] Video tutorials
- [ ] FAQ updates
- [ ] Release notes

### Training
- [ ] CS team training
- [ ] Sales team training
- [ ] Customer webinar

### Support Preparation
- Known limitations documented
- Workarounds identified
- Escalation path defined
- SLA implications noted
```

---

## Security Team Collaboration

### Security Review Triggers

**When Security Review Required:**
- New authentication/authorization
- New data storage
- Third-party integrations
- API changes
- Infrastructure changes
- Sensitive data handling
- Compliance-related features

### Security Review Process

```markdown
## Security Review Request

### Feature Summary
[Brief description]

### Security Considerations
- Authentication: [describe]
- Authorization: [describe]
- Data handling: [describe]
- Third parties: [list]

### Risk Assessment (PM)
- [ ] High risk
- [ ] Medium risk
- [ ] Low risk

### Questions for Security Team
1. [Specific question]
2. [Specific question]
```

---

## Data Science Collaboration

### Analytics Requirements

```markdown
## Analytics Requirements

### Events to Track
| Event Name | Trigger | Properties |
|------------|---------|------------|
| feature_viewed | Page load | user_id, timestamp |
| action_completed | Form submit | user_id, duration |

### Metrics Definition
| Metric | Calculation | Owner |
|--------|-------------|-------|
| Conversion rate | Completions / Views | Data |
| Time to complete | Avg(completed_at - started_at) | Data |

### Dashboard Requirements
- [ ] Real-time dashboard
- [ ] Daily/weekly reports
- [ ] Anomaly alerting
```

### ML/AI Collaboration

**For AI Features:**
- Model performance requirements
- Training data specifications
- Inference latency constraints
- Evaluation methodology
- Monitoring requirements

---

## Stakeholder Alignment Process

### Alignment Stages

```
1. Early Alignment (Problem)
   - Share problem definition
   - Gather input and concerns
   - Build shared understanding
   
2. Solution Alignment
   - Present proposed approach
   - Address concerns
   - Document decisions
   
3. Launch Alignment
   - Cross-functional readiness
   - Final sign-offs
   - Launch criteria confirmed
```

### Conflict Resolution

**When Stakeholders Disagree:**
1. Document all perspectives
2. Identify root of disagreement
3. Seek additional data if available
4. Escalate to Approver if needed
5. Document decision rationale
6. Apply "disagree and commit"

### Communication Cadence

| Update Type | Frequency | Audience |
|-------------|-----------|----------|
| Status update | Weekly | All stakeholders |
| Deep dive | As needed | Affected parties |
| Decision request | As needed | DACI participants |
| Launch update | Pre-launch | All stakeholders |

---

## Review Meeting Best Practices

### Pre-Meeting
- Circulate materials 24-48 hours ahead
- Specify what feedback is needed
- Identify required attendees

### During Meeting
- Time-boxed discussion
- Focus on decisions needed
- Capture action items
- Assign owners and deadlines

### Post-Meeting
- Document decisions
- Share meeting notes
- Track action items
- Update PRD accordingly
