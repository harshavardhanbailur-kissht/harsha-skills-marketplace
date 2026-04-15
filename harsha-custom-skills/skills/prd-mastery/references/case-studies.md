# PRD Case Studies: Iconic Products & Company Practices

Real-world examples and lessons from how top companies build products.

---

## Apple iPhone Development (ANPP Framework)

### Process Structure
- **Marketing Requirements Document (MRD)**: Market opportunity, customer needs
- **Engineering Requirements Document (ERD)**: Technical specifications
- **UX Specifications**: Detailed interaction design

### Key Practices
- Designers set own budgets, sometimes ignored manufacturing practicalities
- 4-6 week redesign/remanufacturing cycles run multiple times
- 6 weeks before launch: plastic screen replaced with glass (keys scratching prototype in pocket)
- Extreme secrecy with compartmentalized teams

### Lessons
- Willingness to make major changes late in development when quality demands it
- Design-led culture can override manufacturing convenience
- Iteration continues until "it feels right"

---

## Slack: "We Don't Sell Saddles Here"

### Context
Stewart Butterfield's internal memo written 2 weeks before preview launch.

### Core Insight
> "We are not in the business of selling saddles... we sell horseback riding."

### PRD Implications
- Product specs should focus on **transformation**, not features
- Because users don't know they want it, tolerance for flaws is extremely low
- First impressions matter disproportionately

### Key Quote
> "What we are selling is organizational transformation."

### Lesson
PRDs should articulate the transformation the product enables, not just feature lists.

---

## Airbnb: Emotional Design & Storyboards

### Snow White Approach
- Hired Pixar animator to create storyboards
- Mapped emotional moments throughout user journey
- Separate storyboards for: host process, guest process, hiring process

### Eleven Star Experience Exercise
Brian Chesky's framework:
- 1 star: Terrible experience
- 5 stars: Expected good experience
- 11 stars: Perfect experience without constraints (e.g., Elon Musk picks you up)

### PRD Application
- Map emotional highs and lows in user journey
- Design for peak positive moments
- Imagine perfect experience before constraining for reality

---

## Stripe: Documentation as Product

### Key Practices
- Documentation has dedicated Product Managers
- Created Markdoc (custom Markdown syntax for docs)
- Interactive code samples with user's actual API test keys
- No PMs for first 500 employees—developers acted as PMs

### Developer Experience (DX) Focus
- API design prioritizes "staying out of developer's way"
- State machine approach ensures predictable resource states
- Every API change reviewed for DX impact

### Lesson
For developer products, documentation quality IS product quality.

---

## Netflix: Experimentation-Driven Development

### A/B Testing Culture
- "ABlaze" platform runs thousands of tests simultaneously
- Users are in 10-15 experiments at any given time
- 80% of viewing comes from personalized recommendations
- Every significant change goes through rigorous A/B testing

### PRD Implications
Traditional upfront specs less important than:
- Hypotheses to test
- Experiment design
- Success metrics
- Rollback criteria

### Federated Platform Console
- Built on Spotify's Backstage
- Platform team of 150+ focused on developer enablement
- "Paved path" concept for first-class supported infrastructure

---

## Tesla: Software-Defined Vehicle

### Development Approach
- 50-developer team for 9+ vehicles (vs traditional 2,500+)
- Agile scrum with trunk-based development
- 3-hour sprint cycles for specific KPI improvements
- Flat organization: engineers report directly to leadership, decisions within 1 hour

### OTA Updates Innovation
> "If we had everything else but couldn't update the car over the air, I don't think we would have survived." — Craig Carlson, former VP

### Key Practices
- Model-based architecture enabling modular subsystem updates
- Triplex redundancy (three dual-core x86 processors running Linux)
- "Cutting the strings"—randomly shutting off flight computers mid-simulation

---

## Notion: Four-Point Product Review

### Team Structure
~15 PMs for 550 employees

### Review Process
1. **Statement of user problem**
2. **Possible directions** (3+ approaches with recommendation)
3. **Full solution** with high-fidelity designs
4. **Ship candidate** ready for quality check

### Planning Cadence
- Twice yearly planning
- Two-week aligned sprints across all teams

---

## Shopify: GSD System

### "Get Shit Done" Process
- OK1: Front-line reviewers (directors from product, UX, engineering, data)
- OK2: Senior leadership approval

### Culture
- CEO Tobi sets yearly themes written from merchant perspective
- Quality-focused work can have "zero metrics attached"

### Key Quote
> "We're working to significantly change the Admin look and feel for no reason other than it'll look better. There's zero metrics attached—the only thing that matters is that we look at it and think: That's rad." — VP Glen Coates

---

## Duolingo: Gamification Engine

### Results
- 350% growth acceleration
- 14% boost in day-14 retention from streak wagers alone

### Approach
- Dedicated Gamification Team
- Every feature runs through extensive A/B testing
- Data science partnership for feature validation
- Treat product development like game design

### Gamification Elements
- Streaks with wagers
- Leagues and leaderboards
- Hearts/lives system
- XP and levels
- Achievement badges

---

## Linear: Taste-Driven Development

### Philosophy
- No A/B tests
- No metrics per project
- No durable teams
- Taste-driven decisions

### Documentation Approach
- Specs are 1-2 pages maximum
- Context → Usage Scenarios → Milestones structure
- Start with least likely to change, end with most likely to change

---

## DoorDash: Launch Process

### Phases
1. **Initiation/Kickoff**: Pod alignment
2. **Brief Creation**: Problem/approach/risks/expected impact
3. **Brief Review**: Stakeholder alignment
4. **Design Review**: UX validation
5. **PRD Creation**: Detailed requirements
6. **Testing Party**: Internal testing
7. **Dogfooding**: Employee use
8. **Launch Readiness Meeting**: Go/no-go decision
9. **Launch**: Phased rollout

### Key Practice
- DRI (Directly Responsible Individual) assigned to each launch
- "Crawl-walk-run" approach to rollout

---

## SpaceX: Lean Software Development

### Team Structure
- ~50 developers for 9+ vehicles (vs traditional 2,500+)
- No traditional aerospace documentation overhead

### Testing Approach
- "Table rocket" testing: all flight computers laid out and connected
- "Cutting the strings": randomly shutting off systems mid-simulation
- Triplex redundancy with voting logic

### Key Insight
Pentagon advisory panel recommended DoD adopt SpaceX practices for faster software development.

---

## Kubernetes: KEP Process

### Enhancement Proposal Structure
- Summary
- Motivation
- Product Requirements
- Design Documentation
- Risk Analysis
- Production Readiness Review

### Lifecycle
Provisional → Implementable → Implemented

### Governance
- Special Interest Groups (SIGs) provide technical oversight
- All changes through GitHub pull requests
- One of most transparent PRD systems globally

---

## UK Government Digital Service (GDS)

### Phase-Based Approach
1. **Discovery**: Understand user needs
2. **Alpha**: Prototype and test
3. **Beta**: Build and iterate
4. **Live**: Continuous improvement

### 18-Point Service Standard
- User-centered design
- Accessibility by default
- Agile methodology
- Service assessments by specialist panels

### 10 Design Principles
1. Start with user needs
2. Do less
3. Design with data
4. Do the hard work to make it simple
5. Iterate. Then iterate again.
6. This is for everyone
7. Understand context
8. Build digital services, not websites
9. Be consistent, not uniform
10. Make things open: it makes things better

---

## Product Failure Case Studies

### Google+ ($585M, 8 years)
**Root Causes:**
- Unclear value proposition
- Users spent 3-5 seconds/day vs 7+ hours on Facebook
- Forced integration through mandatory G+ profiles
- Complex UX (Circles feature) confused mainstream users

**Lesson:** Network effects create massive incumbency advantages requiring substantially better experiences.

### Google Wave (50 days post-launch)
**Root Causes:**
- No clear product definition—couldn't answer what it replaced
- 195-page tutorial required
- "The UI allowed for all things but guided you on none"

**Lesson:** Software doesn't exist in vacuum—consider full user experience across toolset.

### Quibi ($1.75B, 6 months)
**Root Causes:**
- Built "on-the-go" mobile content during COVID lockdowns
- No social sharing—blocked screenshots and viral distribution
- Leadership blamed COVID while ignoring product-market fit

**Lesson:** "No business plan survives first contact with a customer" — Test hypotheses before massive investment.

### Snapchat 2018 Redesign
**Impact:**
- 1.3 million Change.org petition signatures
- 83% negative App Store reviews
- 36% ad revenue decline

**Root Cause:** Major UX changes deployed without beta testing, prioritizing business goals over user experience.

### CB Insights Failure Analysis (483 post-mortems)
| Rank | Reason | % of Failures |
|------|--------|---------------|
| 1 | No market need | 35%+ |
| 2 | Ran out of cash | 38%+ |
| 3 | Wrong team | 23% |
| 4 | Outcompeted | 19% |
| 5 | Pricing issues | 18% |

**Key Finding:** "There is rarely one reason for failure"—most involve multiple compounding factors.

---

## Mozilla Firefox: Change Control Process

### Documented Process
1. Submit Change Request via Bugzilla
2. Weekly Triage (defer/review decision)
3. Weekly Review during team meetings
4. Acceptance incorporated within 2-3 days
5. Deferred requests routed to future lists, labs, or discarded

### PRD Lessons
- Formal change request process prevents scope creep
- Regular triage maintains velocity
- Clear escalation paths for decisions

---

## Next.js/Vercel: RFC-Driven Development

### Process
- Major architecture decisions start as public RFCs
- GitHub Discussions for community input
- Tradeoff decisions made transparently

### Feature Lifecycle
Experimental → Beta → Stable → Deprecated

### Lesson
For developer tools, open development process builds trust and community investment.
