# Regional & International PRD Practices

Global perspectives on product development documentation and processes.

---

## Japanese Product Development

### Toyota Production System (TPS) Influence

**Core Principles Applied to PRDs:**

| Principle | Application to Requirements |
|-----------|----------------------------|
| **Kaizen** | Continuous improvement of specs |
| **Jidoka** | Build quality into requirements |
| **Genchi Genbutsu** | Go see the actual problem firsthand |
| **Nemawashi** | Build consensus before formal approval |

### Chief Engineer System
- Senior engineer serves as "voice of customer"
- Responsible for entire value stream
- Makes final trade-off decisions
- System-level thinking over component thinking

### Set-Based Concurrent Engineering (SBCE)
- Explore multiple solutions simultaneously
- Delay convergence until maximum learning
- Front-load design while exploration space exists
- New cars developed in 15 months vs competitors' 24+

### Toyota's A3 Report Format
Single A3-size paper (11×17") containing:
```
Left Side (Problem/Analysis):
- Background/context
- Current state analysis
- Goal/target state
- Root cause analysis

Right Side (Solution/Action):
- Countermeasures
- Implementation plan
- Follow-up actions
- Expected results
```

### Nintendo Historical Practices
- Planning sheets included hexadecimal screen positions for every 8×8 tile
- Extreme precision enabling creative constraint
- Technical limitations drove innovation
- Documentation as design constraint

---

## German Engineering Documentation

### V-Model (V-Modell XT)

Developed by IABG for Federal Ministry of Defense.

**Structure:**
```
Requirements Analysis  ←→  Acceptance Testing
        ↓                         ↑
System Design          ←→  System Testing
        ↓                         ↑
Architecture Design    ←→  Integration Testing
        ↓                         ↑
Module Design          ←→  Unit Testing
        ↓                         ↑
              Implementation
```

**Key Distinctions:**
- Verification: "Are you building it right?"
- Validation: "Are you building the right thing?"

### German Engineering Characteristics

**Documentation Rigor:**
- Version-controlled specification documents
- Detailed change histories
- Multi-language support built in
- Traceability from requirements to tests

**SAP's Agile Transformation (18,000 developers)**
- Maintained German precision through:
  - Baseline phases
  - Prioritized delta requirements lists
  - Formal review gates
  - Documentation standards

### Bosch Practices
- Automotive SPICE (ASPICE) compliance
- ISO 26262 functional safety integration
- Detailed requirements traceability
- Systematic reuse across product lines

---

## Chinese Tech Company Practices

### ByteDance: Application Factory

**Strategy:**
- Test many applications with minimal resources
- Rapid iteration and learning
- Kill unsuccessful experiments quickly
- Over 80% of engineers use internal AI coding tools

**TikTok Development:**
- Data-driven feature decisions
- Rapid A/B testing cycle
- Algorithm-first product thinking
- Global localization from day one

### Xiaomi: Weekly MIUI Updates

**Process:**
- Friday weekly releases
- Crowd-sourced innovation from "Mi Fans"
- Community-driven feature prioritization
- Growth: 500 million Yuan → 30 billion Yuan in 3 years

**Community Integration:**
- Users vote on features
- Beta testing through community
- Direct feedback loops
- Documentation in community forums

### Alibaba & Tencent

**AI-Integrated Development:**
- Machine selection over manual selection
- Deep AI capability integration
- Scale-oriented architecture decisions
- Speed-to-market prioritization

**Documentation Culture:**
- Internal wiki systems
- Less formal than Western counterparts
- Emphasis on speed over documentation
- Living documents over formal specs

---

## Israeli Startup Culture

### Characteristics

**Minimal Documentation:**
- Velocity over documentation
- Rapid iteration cycles
- Oral culture with minimal written specs
- "Just build it" mentality

**Example: Wix acquiring Base44**
- 6-month-old startup acquired for $80 million
- Demonstrates rapid value creation
- Minimal formal PRD history

### "Vibe Coding" Approach
- Natural language prompts instead of traditional specs
- AI agents manage execution
- Users focus on intent
- Requirements emerge through iteration

### Monday.com Philosophy
- "Joint success over individual wins"
- Cross-company knowledge sharing
- "Startup for Startup" community
- Collaborative documentation

### Israeli PRD Characteristics
```markdown
## Typical Israeli Startup PRD
- 1 page maximum
- Problem + Solution focus
- Metrics-light (early stage)
- Emphasis on MVP definition
- Technical feasibility integrated
- Designer and developer co-create
```

---

## European Practices

### GDPR-Influenced Requirements

**Privacy by Design (Article 25):**
Every PRD must address:
```markdown
## Privacy Requirements
- Data minimization: Only collect necessary data
- Purpose limitation: Clear use case for each data point
- Storage limitation: Retention periods defined
- Accuracy: Update/correction mechanisms
- Integrity: Security measures specified
- Accountability: Documentation of compliance

## User Rights
- Right to access: Export functionality
- Right to rectification: Edit capabilities
- Right to erasure: Deletion mechanisms
- Right to portability: Data export formats
- Right to object: Opt-out mechanisms
- Right to restrict: Processing controls

## Data Processing
- Legal basis documented for each processing activity
- Data Protection Impact Assessment (DPIA) triggers
- Third-party processor requirements
- Cross-border transfer mechanisms
```

### European Accessibility Act (EAA)

**Timeline:** Effective June 28, 2025

**Scope:**
- Computers and operating systems
- Payment terminals and ATMs
- E-commerce websites and apps
- Banking services
- Transportation services
- E-books and readers

**Penalties by Country:**
| Country | Maximum Penalty |
|---------|-----------------|
| France | €300,000 |
| Spain | €1,000,000 |
| Hungary | €1,260,000 |
| Some countries | 5% annual turnover |

### EN 301 549 Standard
- European accessibility standard
- References WCAG 2.1 Level AA
- Additional requirements for software and hardware
- Harmonized standard for EU accessibility

---

## Indian IT Services Methodology

### Large IT Services Approach (TCS, Infosys, Wipro)

**Characteristics:**
- Heavy documentation for offshore handoff
- Detailed specifications for distributed teams
- Formal sign-off processes
- Waterfall-influenced even in agile

**Typical Documentation:**
```markdown
## Requirements Specification Document (RSD)
- Business requirements (BRD)
- Functional requirements (FRS)
- Technical requirements (TRS)
- Test requirements (TRS)
- Traceability matrix

## Handoff Documentation
- Detailed acceptance criteria
- Screen mockups with annotations
- Data dictionary
- Interface specifications
- Error handling matrix
```

### Offshore Development Considerations
- Time zone-optimized documentation
- Asynchronous communication emphasis
- Detailed context for remote teams
- Video walkthroughs for complex features

---

## Korean Tech Practices

### Samsung & LG

**Hardware-Software Integration:**
- Tight coupling of hardware and software specs
- Manufacturing constraint awareness
- Supply chain integration in requirements
- Multi-division coordination

### Naver & Kakao

**Super App Development:**
- Platform-first thinking
- Ecosystem integration requirements
- Multi-service coordination
- Local market customization

---

## Remote/Distributed Team Practices

### GitLab: Handbook-First

**Approach:**
- Document nearly everything publicly
- 2,000+ page handbook
- Documentation is definition of done
- Merge request-based changes

**Key Practice:**
> "If it's not in the handbook, it doesn't exist."

### Zapier: Three-Tool System

| Tool | Purpose |
|------|---------|
| Slack | Virtual office (1000+ public channels) |
| Async | "Like a blog meets Reddit" for important conversations |
| Quip | Documentation and collaboration |

**Bandwidth Spectrum:**
1. Async text (default)
2. Synchronous video (for tricky issues)
3. In-person (rare, for relationship building)

> "Raise bandwidth only for tricky issues."

### Async-First Best Practices

**From Sumeet Moghe's Async-First Playbook:**
1. Write team handbook as single source of truth
2. Tame instant messaging with explicit responsiveness expectations
3. Shift left on meetings (use as last resort)
4. Alternate between deep work and sharing for feedback

**Video Documentation:**
- Loom for product demos
- Design walkthroughs recorded
- Stakeholder presentations async
- "Watch parties" for recorded research sessions

### Time Zone Management
```markdown
## Async Collaboration Guidelines
- Documentation as primary communication
- Recorded meetings with summaries
- Overlap hours for synchronous needs: [specify hours]
- Clear response time expectations by priority
- Handoff documentation at day's end
```

---

## Regional PRD Adaptation Guide

### Factors to Consider

| Factor | High Documentation | Low Documentation |
|--------|-------------------|-------------------|
| Team distribution | Distributed/offshore | Co-located |
| Regulatory environment | Highly regulated | Startup/unregulated |
| Company stage | Enterprise | Early startup |
| Cultural expectation | German, Indian | Israeli, Chinese |
| Product complexity | Complex/hardware | Simple/software |

### Adaptation Strategies

**For Distributed Teams:**
- More explicit context
- Video supplements
- Clear async handoffs
- Comprehensive acceptance criteria

**For Regulated Industries:**
- Formal approval workflows
- Traceability matrices
- Compliance sections
- Audit documentation

**For Fast-Moving Startups:**
- One-page constraints
- Problem-focused
- Prototype as spec
- Oral supplements to written docs
