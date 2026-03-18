# Architecture Decision Record (ADR)

**Title**: {{DECISION_TITLE}}

**Status**: {{PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED_BY #NNN}}

**ADR Number**: {{ADR_NUMBER}} | **Date**: {{DATE}} | **Author(s)**: {{NAMES}}

---

## Context

### Problem Statement

{{Clear, concise description of the problem or decision that needs to be made}}

**Why Now?**: {{What triggered this decision? What changed?}}

**Who Is Affected?**: {{Teams, services, users impacted}}

### Background

{{Historical context, previous decisions, or related decisions}}

**Related ADRs**:
- [ADR-{{NUMBER}}: {{Title}}](./adr-{{NUMBER}}.md)
- [ADR-{{NUMBER}}: {{Title}}](./adr-{{NUMBER}}.md)

### Constraints & Requirements

**Must Have**:
- {{Requirement 1}}: {{Description}}
- {{Requirement 2}}: {{Description}}

**Should Have**:
- {{Requirement 1}}: {{Description}}

**Nice to Have**:
- {{Requirement 1}}: {{Description}}

**Non-Requirements** (explicitly OUT of scope):
- {{Non-requirement}}: {{Why?}}

---

## Decision

### The Choice

{{Clear statement of the decision made}}

**We have decided to**: {{Use technology X for purpose Y}} | {{Adopt pattern Z}} | {{Change architecture to A}}

### Implementation Approach

{{How will this be implemented? Key steps?}}

```
Phase 1 (Weeks 1-2): {{Phase description}}
Phase 2 (Weeks 3-4): {{Phase description}}
Phase 3 (Weeks 5+): {{Phase description}}
```

**Code Example** (if applicable):

```javascript
// Before (old approach)
{{OLD_CODE_EXAMPLE}}

// After (new approach)
{{NEW_CODE_EXAMPLE}}
```

**Configuration**:

```yaml
# config.yaml
decision:
  approach: {{chosen_approach}}
  enabled: true
  parameters:
    {{key}}: {{value}}
```

---

## Alternatives Considered

### Alternative 1: {{ALTERNATIVE_NAME}}

**Description**: {{What would this involve?}}

**Pros**:
- ✓ {{Advantage 1}}
- ✓ {{Advantage 2}}

**Cons**:
- ✗ {{Disadvantage 1}}
- ✗ {{Disadvantage 2}}

**Estimated Cost**:
- Development: {{EFFORT}} ({{PERSON_WEEKS}})
- Infrastructure: {{COST_PER_MONTH}}
- Maintenance: {{EFFORT_PER_MONTH}}

**Estimated Timeline**: {{WEEKS}} weeks to full implementation

**Viability**: {{VIABLE | NOT_VIABLE | RISKY}} because {{REASON}}

---

### Alternative 2: {{ALTERNATIVE_NAME}}

**Description**: {{Description}}

**Pros**: {{Advantages}}

**Cons**: {{Disadvantages}}

**Cost**: {{Development}}, {{Infrastructure}}, {{Maintenance}}

**Timeline**: {{WEEKS}} weeks

**Viability**: {{VIABLE | NOT_VIABLE}}

---

### Alternative 3: {{ALTERNATIVE_NAME}}

**Description**: {{Description}}

**Pros**: {{Advantages}}

**Cons**: {{Disadvantages}}

---

### Why Not Alternative X?

{{Explanation for why certain alternatives were rejected}}

**Alternative X was rejected because**: {{Specific reasons why this doesn't work for us}}

---

## Consequences

### Positive Consequences

✓ **{{Consequence 1}}**: {{Benefit and impact}}

✓ **{{Consequence 2}}**: {{Benefit and impact}}

✓ **{{Consequence 3}}**: {{Benefit and impact}}

### Negative Consequences

✗ **{{Consequence 1}}**: {{Risk or cost}}
  - Mitigation: {{How to address this?}}

✗ **{{Consequence 2}}**: {{Risk or cost}}
  - Mitigation: {{How to address this?}}

### Neutral Consequences

— **{{Consequence}}**: {{No clear impact}} (neutral because {{reason}})

---

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Performance** | {{Improvement}} | {{Penalty}} |
| **Complexity** | {{Simplification}} | {{Added complexity}} |
| **Scalability** | {{Improvement}} | {{Limitation}} |
| **Maintenance** | {{Reduction}} | {{Increase}} |
| **Cost** | {{Savings}} | {{Expense}} |

**Largest Trade-off**: {{What are we giving up the most?}} → {{Why is it worth it?}}

---

## Success Criteria

How will we know this decision was successful?

- [ ] {{Metric 1}}: {{Target value}} (measure: {{How?}})
- [ ] {{Metric 2}}: {{Target value}} (measure: {{How?}})
- [ ] {{Metric 3}}: {{Target value}} (measure: {{How?}})

**Measurement Plan**:
```
Week 1-2: {{Baseline metrics}}
Week 3-4: {{Early signals}}
Month 2: {{KPI review}}
Month 3+: {{Ongoing monitoring}}
```

**Decision Gate**: {{Date}} — Reevaluate if metrics not on track

---

## Implementation Plan

### Timeline

| Phase | Tasks | Owner | Duration | Deadline |
|-------|-------|-------|----------|----------|
| **Design** | {{Task 1}}, {{Task 2}} | {{Person}} | 1 week | {{Date}} |
| **Development** | {{Task 1}}, {{Task 2}} | {{Person}} | 2 weeks | {{Date}} |
| **Testing** | {{Task 1}}, {{Task 2}} | {{Person}} | 1 week | {{Date}} |
| **Rollout** | {{Task 1}}, {{Task 2}} | {{Person}} | 1 week | {{Date}} |

### Rollout Strategy

**Phased Rollout**:
1. **Canary** ({{DATE}}): {{Percentage}}% of traffic → Monitor {{METRICS}}
2. **Gradual** ({{DATE}}): {{Percentage}}% → Monitor {{METRICS}}
3. **Full** ({{DATE}}): {{Percentage}}% → All users/systems

**Rollback Plan**: {{How to quickly revert if things go wrong?}}

```bash
# If issues detected, rollback:
git revert {{COMMIT_HASH}}
git push origin main
# OR feature flag: set FEATURE_FLAG_{{NAME}} = false
```

### Dependencies

- {{Dependency 1}}: {{What must happen first?}}, Owner: {{Person}}, ETA: {{Date}}
- {{Dependency 2}}: {{What must happen first?}}, Owner: {{Person}}, ETA: {{Date}}

### Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-----------|--------|-----------|
| {{Risk}} | {{HIGH/MEDIUM/LOW}} | {{HIGH/MEDIUM/LOW}} | {{How to prevent/handle}} |
| {{Risk}} | {{HIGH/MEDIUM/LOW}} | {{HIGH/MEDIUM/LOW}} | {{How to prevent/handle}} |

---

## Pre-Mortem: What Could Go Wrong?

**Imagine it's {{DATE + 3 MONTHS}} and this decision failed. What happened?**

1. **{{Failure Scenario 1}}**
   - Root cause: {{Why?}}
   - How to prevent: {{Preventive measure}}
   - How to detect: {{Early warning sign}}

2. **{{Failure Scenario 2}}**
   - Root cause: {{Why?}}
   - How to prevent: {{Preventive measure}}
   - How to detect: {{Early warning sign}}

3. **{{Failure Scenario 3}}**
   - Root cause: {{Why?}}
   - How to prevent: {{Preventive measure}}
   - How to detect: {{Early warning sign}}

**Most Likely Failure**: {{What's the most probable way this could fail?}}

**Most Costly Failure**: {{What failure would hurt the most?}}

---

## Review Triggers

When should we reconsider this decision?

- **Metric Degradation**: If {{METRIC}} drops below {{THRESHOLD}} (check monthly)
- **Business Change**: If {{BUSINESS_EVENT}} occurs (e.g., acquisition, major pivot)
- **Technology Change**: If {{NEW_TECH}} becomes available that is {{CAPABILITY_IMPROVEMENT}}
- **Incident**: If {{INCIDENT_TYPE}} occurs related to this decision
- **Scheduled Review**: {{DATE}} (annual review)

**Decision Owner's Authority**: {{Name}} has authority to revisit this decision if triggers occur

---

## Cost Analysis

### Development Cost

- **Effort**: {{PERSON_WEEKS}} ({{HOURLY_RATE}} × {{HOURS}} = {{COST}})
- **Infrastructure Setup**: {{COST}}
- **Training**: {{PERSON_WEEKS}} at {{HOURLY_RATE}} = {{COST}}

**Total Development Cost**: {{TOTAL_COST}}

### Ongoing Cost

| Component | Monthly Cost | Annual Cost |
|-----------|---|---|
| {{Component}} | {{COST}} | {{ANNUAL}} |
| {{Component}} | {{COST}} | {{ANNUAL}} |
| **Total** | {{MONTHLY}} | {{ANNUAL}} |

### ROI

**Expected Payback Period**: {{MONTHS}} months

**Annual Savings/Value**: {{SAVINGS}} ({{BREAKDOWN}})

---

## Communication & Approval

### Approval Status

| Stakeholder | Role | Status | Date |
|---|---|---|---|
| {{Person}} | {{Role}} | ✓ Approved / ⏳ Pending | {{Date}} |
| {{Person}} | {{Role}} | ✓ Approved / ⏳ Pending | {{Date}} |
| {{Person}} | {{Role}} | ✓ Approved / ⏳ Pending | {{Date}} |

### Feedback Received

- {{Person}}: {{Feedback}} — {{Addressed in}} {{section}}
- {{Person}}: {{Feedback}} — {{Addressed in}} {{section}}

### Communication Plan

- [ ] Share with engineering team (Slack: {{CHANNEL}})
- [ ] Share with product team (Slack: {{CHANNEL}})
- [ ] Share with affected customers (Email, blog post)
- [ ] Document in architecture handbook
- [ ] Present in {{FORUM}} (date: {{DATE}})

---

## References & Reading

**Related Documentation**:
- [Architecture Guide](../architecture.md)
- [Style Guide](../style-guide.md)

**External References**:
- [{{Source}}]({{URL}}) — {{Why relevant?}}
- [{{Source}}]({{URL}}) — {{Why relevant?}}

**Decision Records**:
- [ADR-{{NUMBER}}: {{Related decision}}](./adr-{{NUMBER}}.md)

---

## Appendix: Detailed Analysis

### Market Research

{{Any external research, benchmarking, or competitive analysis?}}

### Technical Analysis

{{Deep dive into technical details if needed}}

### Cost-Benefit Analysis

| Factor | Current | Proposed | Difference |
|--------|---------|----------|-----------|
| {{Factor}} | {{Current}} | {{Proposed}} | {{Difference}} |

---

**Status**: {{PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED}}

**Last Updated**: {{DATE}} by {{AUTHOR}}

**Next Review**: {{DATE}}

---

## Quick Reference

**TL;DR**: {{One sentence summary of the decision}}

**The Gist**: {{One paragraph summary}}

**Key Trade-off**: {{Most important trade-off in one sentence}}
