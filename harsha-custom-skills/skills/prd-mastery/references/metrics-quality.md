# PRD Metrics & Quality Measurement

Complete guide to measuring PRD effectiveness and quality.

---

## Google HEART Framework

### Framework Overview

| Dimension | Definition | Example Metrics |
|-----------|------------|-----------------|
| **H**appiness | User satisfaction | NPS, CSAT, survey scores |
| **E**ngagement | Depth of interaction | Session duration, actions per session |
| **A**doption | New user acquisition | Sign-ups, activations, onboarding completion |
| **R**etention | Users returning | DAU/MAU, churn rate, retention curves |
| **T**ask Success | Efficiency and effectiveness | Completion rate, time on task, error rate |

### Goals-Signals-Metrics (GSM) Process

**Step 1: Define Goal**
```
What is the desired outcome?
Example: Users find the search feature helpful
```

**Step 2: Identify Signals**
```
What user behaviors indicate goal achievement?
Example: Users click on search results, repeat searches decrease
```

**Step 3: Choose Metrics**
```
How do we measure the signals?
Example: Click-through rate on results, search refinement rate
```

### HEART Metrics by Product Type

**E-commerce:**
- Happiness: Post-purchase NPS
- Engagement: Products viewed per session
- Adoption: First purchase conversion
- Retention: Repeat purchase rate
- Task Success: Checkout completion rate

**SaaS/Productivity:**
- Happiness: CSAT after key workflows
- Engagement: Features used per session
- Adoption: Feature activation rate
- Retention: Weekly active usage
- Task Success: Task completion rate

**Content/Media:**
- Happiness: Content ratings
- Engagement: Watch time, scroll depth
- Adoption: New subscriber rate
- Retention: Return visitor rate
- Task Success: Content discovery success

---

## Success Metrics Specification

### Metric Definition Template
```markdown
## Metric: [Name]

### Definition
[Precise calculation formula]

### Data Source
[Where data comes from]

### Baseline
[Current value with date measured]

### Target
[Goal value with target date]

### Measurement Frequency
[How often measured]

### Owner
[Person responsible]

### Dashboard Location
[Where to view]
```

### Leading vs Lagging Indicators

**Lagging Indicators** (Outcomes):
- Revenue
- Customer acquisition
- Churn rate
- NPS score

**Leading Indicators** (Predictive):
- Feature engagement
- Onboarding completion
- Support ticket trends
- User activation events

### Shreyas Doshi's Approach
Distinguish between:
- **3-5 Key Metrics**: Primary success indicators
- **3-5 Leading Indicators**: Early warning/prediction metrics

### Counter-Metrics (Guardrails)

**Purpose:** Ensure optimization doesn't cause unintended harm

**Examples:**
| Primary Metric | Counter-Metric |
|----------------|----------------|
| Conversion rate | Cart abandonment rate |
| Engagement time | Support tickets |
| Feature adoption | System performance |
| Revenue per user | Customer satisfaction |

---

## PRD Quality Metrics

### Document Quality Indicators

**Clarity Score:**
- Reading level (aim for 8th grade)
- Sentence complexity
- Jargon usage
- Ambiguous terms count

**Completeness Checklist:**
- [ ] Problem statement with evidence
- [ ] Success metrics with baselines/targets
- [ ] Non-goals section
- [ ] User personas defined
- [ ] Acceptance criteria testable
- [ ] Edge cases documented
- [ ] Dependencies identified
- [ ] Risks with mitigations
- [ ] Timeline with milestones

**Traceability Score:**
- % of requirements linked to user needs
- % of requirements with test cases
- % of requirements with design specs

### Process Quality Metrics

| Metric | Good | Needs Improvement |
|--------|------|-------------------|
| Time to first draft | <1 week | >2 weeks |
| Review cycles | 1-2 | >3 |
| Questions from engineering | <5 per section | >10 per section |
| Scope changes after approval | <10% | >25% |
| Stakeholder sign-off time | <1 week | >2 weeks |

### Aakash Gupta's Common PRD Problems

**"Comically Bad" Metrics Sections:**
- High-level and unspecific
- No baselines provided
- Unmeasurable goals
- Missing measurement methodology

**Fix:** Include:
- Usage metrics (what users do)
- Impact metrics (business outcomes)
- Dashboard mockups
- Measurement infrastructure requirements

---

## Team Effectiveness Metrics

### Alignment Indicators

**Pre-Development:**
- Questions asked during PRD review
- Clarifications needed after kickoff
- Scope change requests before dev starts

**During Development:**
- Requirements interpretation issues
- Design deviation requests
- Blocked time due to unclear requirements

**Post-Development:**
- Features built not matching intent
- Post-launch fixes for missed requirements
- User complaints about missing functionality

### DACI Success Metrics

McKinsey research: Projects using DACI have **25% higher success rates**

**Measure:**
- Decision cycle time
- Stakeholder satisfaction with process
- Requirement change frequency
- Cross-functional alignment score

---

## Post-Mortem PRD Reviews

### Retrospective Questions

**Problem Definition:**
- Did we solve the right problem?
- Was the problem clearly understood by all?
- Were customer insights accurate?

**Requirements Quality:**
- Were requirements clear?
- Were they complete?
- Were they accurate?
- How many revisions during development?

**Process Effectiveness:**
- Where did misunderstandings arise?
- What information was missing?
- What would we do differently?

### Post-Mortem Template
```markdown
## PRD Post-Mortem: [Feature Name]

### Summary
[Brief overview of what shipped]

### Success vs Goals
| Goal | Target | Actual | Status |
|------|--------|--------|--------|
| [Metric] | [Target] | [Actual] | ✅/❌ |

### What Went Well
- [Good outcome 1]
- [Good outcome 2]

### What Didn't Go Well
- [Issue 1]
- [Issue 2]

### Requirements Accuracy
- Requirements that were accurate: [%]
- Requirements that needed revision: [%]
- Missing requirements discovered: [count]

### Root Causes of Issues
[Analysis of why problems occurred]

### Lessons Learned
[Specific learnings for future PRDs]

### Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| [Action] | [Name] | [Date] |
```

---

## Continuous Improvement

### PRD Quality Improvement Cycle

```
1. Write PRD
     ↓
2. Execute development
     ↓
3. Measure outcomes
     ↓
4. Conduct post-mortem
     ↓
5. Identify improvements
     ↓
6. Update PRD template/process
     ↓
(Repeat)
```

### Common Improvement Areas

**Template Improvements:**
- Add missing sections discovered in post-mortems
- Remove sections that provide no value
- Improve prompts for common gaps

**Process Improvements:**
- Adjust review cycles
- Add/remove stakeholders
- Change approval workflows

**Training Improvements:**
- Address common mistakes
- Share best practices
- Update onboarding materials

---

## Measuring PRD-to-Product Alignment

### Requirements Coverage Analysis

**Formula:**
```
Coverage = (Implemented Requirements / Total Requirements) × 100
```

**Target:** 95%+ for must-haves, 80%+ for should-haves

### Scope Creep Measurement

**Formula:**
```
Scope Creep = (Final Requirements - Initial Requirements) / Initial Requirements × 100
```

**Healthy Range:** <15%
**Warning Zone:** 15-30%
**Critical:** >30%

### Time-to-Value Tracking

| Milestone | Planned | Actual | Variance |
|-----------|---------|--------|----------|
| PRD Approved | [Date] | [Date] | [Days] |
| Design Complete | [Date] | [Date] | [Days] |
| Dev Complete | [Date] | [Date] | [Days] |
| QA Complete | [Date] | [Date] | [Days] |
| Launch | [Date] | [Date] | [Days] |

---

## Benchmarks from Research

### CB Insights Startup Failure Analysis

483 post-mortems analyzed:

| Rank | Failure Reason | % |
|------|----------------|---|
| 1 | No market need | 35%+ |
| 2 | Ran out of cash | 38%+ |
| 3 | Wrong team | 23% |
| 4 | Outcompeted | 19% |
| 5 | Pricing issues | 18% |

**Key Finding:** Failures rarely have single cause—multiple factors compound.

**PRD Implication:** Validate market need (problem statement) rigorously.

### Industry Benchmarks

**PRD Revision Frequency:**
- Best teams: 2-3 revisions before approval
- Average teams: 5+ revisions
- Struggling teams: >10 revisions or none (rubber stamp)

**Time from PRD to Launch:**
- Small feature: 2-6 weeks
- Medium feature: 1-3 months
- Large initiative: 3-12 months

**Requirements Change Rate:**
- During development: <10% ideal, >25% problematic
- After launch: <5% for corrections

---

## Dashboard Requirements

### PRD Status Dashboard

```markdown
## Active PRDs

| PRD | Status | Owner | Target Date | Health |
|-----|--------|-------|-------------|--------|
| [Name] | [Draft/Review/Approved/Dev/Shipped] | [PM] | [Date] | 🟢/🟡/🔴 |

## Metrics Summary

### This Quarter
- PRDs Shipped: [N]
- Average Cycle Time: [N days]
- Scope Creep: [N%]
- Post-Launch Issues: [N]

### Quality Trends
[Chart showing quality metrics over time]
```

### Health Indicators

🟢 **Green:** On track, no issues
- Scope stable
- Timeline on track
- Stakeholders aligned

🟡 **Yellow:** At risk, needs attention
- Minor scope changes
- Timeline pressure
- Some stakeholder concerns

🔴 **Red:** Critical, intervention needed
- Major scope changes
- Timeline missed
- Stakeholder conflict
- Requirements unclear
