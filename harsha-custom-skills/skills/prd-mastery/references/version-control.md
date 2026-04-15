# PRD Version Control & Change Management

Complete guide to managing PRD versions, changes, and traceability.

---

## Semantic Versioning for Documents (SemVerDoc)

### Format: MAJOR.MINOR.PATCH

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| MAJOR | Significant structural changes, new sections | 1.0.0 → 2.0.0 |
| MINOR | Adding/removing sections, substantial content changes | 1.0.0 → 1.1.0 |
| PATCH | Typos, formatting, clarifications | 1.0.0 → 1.0.1 |

### Pre-release Labels
- `-draft` — Initial draft, not yet reviewed
- `-alpha` — Early review stage
- `-beta` — Stakeholder review in progress
- `-rc` — Release candidate, final review

### Example Version History
```
0.1.0-draft    Initial problem statement
0.2.0-draft    Added solution approach
0.3.0-alpha    First stakeholder review
0.4.0-beta     Incorporated engineering feedback
1.0.0-rc       Final review before approval
1.0.0          Approved and baselined
1.0.1          Fixed typo in acceptance criteria
1.1.0          Added edge case requirements
2.0.0          Major scope change after discovery
```

---

## Git-Based PRD Workflows

### GitHub Flow for Documentation

**Branch Naming Conventions:**
```
docs/feature-name           Feature PRD branch
docs/update-metrics         Update existing PRD
fix/typo-in-requirements    Minor fix
#155-add-security-section   Issue-linked branch
```

### Workflow Steps
1. Create feature branch from main
2. Make changes to PRD
3. Open Pull Request with description
4. Automated checks (linting, link validation)
5. Peer review and approval
6. Merge to main
7. Auto-generate PDF if needed

### Pull Request Template for PRDs
```markdown
## PRD Change Summary
[Brief description of changes]

## Type of Change
- [ ] New PRD
- [ ] Major revision (new sections, scope change)
- [ ] Minor revision (content updates)
- [ ] Patch (typos, formatting)

## Affected Sections
- [ ] Problem Statement
- [ ] Goals/Metrics
- [ ] Requirements
- [ ] Timeline
- [ ] Other: ___

## Stakeholders to Notify
@engineering @design @qa

## Checklist
- [ ] Version number updated
- [ ] Change log updated
- [ ] All links validated
- [ ] Spelling/grammar checked
- [ ] Stakeholder alignment confirmed
```

### GitHub Actions for PRDs
```yaml
name: PRD Validation
on:
  pull_request:
    paths:
      - 'prds/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check links
        uses: lycheeverse/lychee-action@v1
      - name: Lint Markdown
        uses: DavidAnson/markdownlint-cli2-action@v9
      - name: Generate PDF
        run: pandoc ${{ github.event.pull_request.changed_files }} -o output.pdf
```

---

## Change Control Process

### Mozilla Firefox Change Request Process

**Step 1: Submit Change Request**
- Via issue tracker (Bugzilla, Jira, etc.)
- Include: Rationale, impact, urgency

**Step 2: Weekly Triage**
- Review submitted requests
- Decision: Defer or Review

**Step 3: Weekly Review Meeting**
- Team discusses reviewed requests
- Decision: Accept or Reject

**Step 4: Implementation**
- Accepted changes incorporated within 2-3 days
- PRD version updated

**Step 5: Deferred Requests**
- Routed to future lists, labs, or discarded
- Documented for reference

### Change Request Template
```markdown
## Change Request ID: CR-[YYYY]-[NNN]

### Requester
[Name, Role, Date]

### Change Description
[What specifically needs to change]

### Rationale
[Why this change is needed]

### Impact Assessment
- Requirements affected: [REQ-001, REQ-002, ...]
- Timeline impact: [None | Minor | Major]
- Resource impact: [None | Minor | Major]
- Risk: [Low | Medium | High]

### Alternatives Considered
[Other approaches evaluated]

### Recommendation
[Approve | Defer | Reject]

### Approval
| Role | Name | Decision | Date |
|------|------|----------|------|
| PM | | | |
| Eng Lead | | | |
| Design | | | |
```

---

## Requirements Traceability Matrix (RTM)

### Structure
| Req ID | Description | Source | Priority | Status | Test Case | Design Ref |
|--------|-------------|--------|----------|--------|-----------|------------|
| FR-001 | [Requirement] | [User story/stakeholder] | [P0/P1/P2] | [Draft/Approved/Implemented] | TC-001 | UI-001 |

### Bidirectional Traceability

**Forward Traceability:** Requirement → Design → Code → Test
```
FR-001 → UI-001 → component.tsx → TC-001, TC-002
```

**Backward Traceability:** Test → Code → Design → Requirement
```
TC-001 → component.tsx → UI-001 → FR-001
```

### Traceability Levels
| Level | From | To |
|-------|------|-----|
| L1 | Business Requirement | Functional Requirement |
| L2 | Functional Requirement | Design Specification |
| L3 | Design Specification | Code Module |
| L4 | Code Module | Test Case |

### Coverage Analysis
- All requirements must have at least one test case
- Orphan tests (no linked requirement) flagged for review
- Untested requirements highlighted

---

## Baseline Management

### What is a Baseline?
A frozen snapshot of approved requirements at a specific point in time.

### When to Baseline
- After initial approval (v1.0.0)
- Before major development phases
- At each release milestone
- Before significant scope changes

### Baseline Document Content
```markdown
## Baseline Record

### Baseline ID: BL-[YYYY]-[NNN]
### PRD Version: [X.Y.Z]
### Date: [YYYY-MM-DD]
### Approved By: [Names and roles]

### Included Requirements
[List of all requirements in this baseline]

### Exclusions
[Requirements explicitly not in this baseline]

### Change History from Previous Baseline
[Summary of changes since last baseline]
```

### Managing Changes to Baselined Requirements
1. **Identify** the change needed
2. **Assess** impact on timeline, resources, risk
3. **Document** in change request
4. **Review** with change control board
5. **Approve/Reject** formally
6. **Implement** if approved
7. **Re-baseline** if significant

---

## Document Update Practices

### Ben Horowitz's Principle
> "Update PRDs daily or weekly minimum"

### Update Frequency Guidelines
| Stage | Update Frequency |
|-------|------------------|
| Discovery | As insights emerge |
| Active Development | Weekly minimum |
| Stable/Maintenance | As needed |
| Post-Launch | Based on learnings |

### Change Notification Strategy

**Critical Updates (Push):**
- Scope changes
- Timeline changes
- Requirement additions/removals
- Notify all stakeholders immediately

**Minor Updates (Aggregate):**
- Clarifications
- Typo fixes
- Weekly digest to stakeholders

### Changelog Format
```markdown
## Changelog

### [1.2.0] - 2024-01-15
#### Added
- REQ-045: Password complexity requirements
- Edge case for timeout handling

#### Changed
- REQ-012: Updated performance target from 200ms to 150ms

#### Removed
- REQ-008: Removed legacy integration requirement

#### Fixed
- Clarified acceptance criteria for REQ-023
```

---

## Tools for Version Control

### Document Platforms with Version History
| Tool | Version Control | Collaboration | Best For |
|------|-----------------|---------------|----------|
| Notion | Page history | Real-time | Startups/SMBs |
| Confluence | Page versions | Comments | Enterprise |
| Coda | Revision history | Interactive tables | Mid-size teams |
| Google Docs | Version history | Real-time | Ad-hoc collaboration |
| GitHub | Full git | PR workflow | Developer-heavy teams |

### Git-Based Documentation Tools
- **GitBook**: Markdown with git backend
- **Docusaurus**: React-based docs with versioning
- **MkDocs**: Python-based, Material theme popular
- **Notion + GitHub Sync**: Hybrid approach

### Requirements Management Tools
- **Jama Connect**: Full traceability, compliance-ready
- **Polarion**: ALM with requirements management
- **Helix RM**: Enterprise requirements management
- **Jira + Requirements Plugin**: Lightweight option

---

## When to Update vs. Create New PRD

### Update Existing PRD When:
- Clarifications needed
- Minor scope adjustments
- Metrics refinement
- Timeline updates
- Bug fixes in requirements

### Create New PRD When:
- Fundamentally different problem
- New product/feature (not iteration)
- Different user segment
- Separate release cycle
- Distinct success criteria

### Version vs. New Document Decision Tree
```
Is this the same product/feature?
├── No → Create new PRD
└── Yes → Is the core problem the same?
    ├── No → Create new PRD
    └── Yes → Is this a major pivot?
        ├── Yes → Major version bump (2.0.0)
        └── No → Minor/patch version bump
```

---

## Audit Trail Requirements

### For Regulated Industries

**Minimum Audit Trail Data:**
- Who made the change
- When the change was made
- What was changed (before/after)
- Why the change was made (rationale)
- Who approved the change

### Audit-Ready Documentation
```markdown
## Revision Record

| Rev | Date | Author | Approver | Change Description | Rationale |
|-----|------|--------|----------|-------------------|-----------|
| 1.0 | 2024-01-01 | J. Smith | M. Johnson | Initial release | N/A |
| 1.1 | 2024-01-15 | J. Smith | M. Johnson | Added REQ-045 | Security audit finding |
| 2.0 | 2024-02-01 | A. Brown | M. Johnson | Scope expansion | Customer feedback |
```

### Retention Requirements by Industry
| Industry | Minimum Retention | Standard |
|----------|-------------------|----------|
| Healthcare | 6 years | HIPAA |
| Financial | 7 years | SOX, SEC |
| Automotive | 15+ years | Product liability |
| Aviation | Life of product + 2 years | FAA |
| Defense | Per contract | MIL-STD |
