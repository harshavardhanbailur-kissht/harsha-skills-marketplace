# PRD Frameworks & Methodologies

Complete reference for all major PRD frameworks and methodologies.

---

## Amazon PR-FAQ (Working Backwards)

### Core Concept
Write a press release announcing the finished product BEFORE building anything. Forces customer-centric thinking.

### Structure

**Part 1: Press Release (1 page)**
```
HEADLINE: [Attention-grabbing product announcement]

SUBHEADLINE: [One sentence describing target customer and benefit]

SUMMARY PARAGRAPH:
[City, Date] — [Company] today announced [Product], which enables 
[target customer] to [key benefit]. [Product] solves [problem] by 
[solution approach].

PROBLEM PARAGRAPH:
[Describe the customer problem in detail. Use customer language.]

SOLUTION PARAGRAPH:
[Describe how the product solves the problem. Focus on benefits, 
not features.]

QUOTE FROM COMPANY LEADER:
"[Aspirational quote about why this matters]" — [Name, Title]

HOW IT WORKS:
[Simple description of how customer uses the product]

CUSTOMER QUOTE:
"[Testimonial from target customer perspective]" — [Persona Name]

CALL TO ACTION:
[How customers can learn more or get started]
```

**Part 2: FAQ Section (2-5 pages)**

*External FAQs (Customer perspective):*
- What is [Product]?
- How does it work?
- Why should I use it instead of [alternative]?
- How much does it cost?
- How do I get started?
- What if I have problems?

*Internal FAQs (Business perspective):*
- What's the market size?
- How will we make money?
- What resources are required?
- What are the key risks?
- What's the timeline?
- What are the key milestones?
- Why now?
- What's the competitive landscape?

### Process
1. Write PR-FAQ draft
2. Circulate for feedback
3. Revise based on pushback
4. Present in meeting (15-20 min silent reading, then discussion)
5. Senior people speak LAST
6. Most PR-FAQs don't get approved — filtering weak ideas is a feature

### Key Insight
> "Start by writing the press release, nail it. Write FAQs to add meat to the skeleton." — Werner Vogels, Amazon CTO

---

## Spotify DIBB Framework

### Structure

**D - Data**: Observable facts and metrics
```
- User research findings
- Analytics data
- Market research
- Competitive intelligence
```

**I - Insight**: Interpretation of data
```
- What patterns emerge?
- What does the data tell us?
- What's the underlying cause?
```

**B - Belief**: Hypothesis based on insight
```
- We believe [hypothesis]
- This will result in [expected outcome]
- Because [reasoning]
```

**B - Bet**: Actionable initiative
```
- We will [specific action]
- Success looks like [measurable outcome]
- We'll know in [timeframe]
```

### Bets Board Structure
| Column | Purpose |
|--------|---------|
| Backlog | Ideas not yet prioritized |
| Next Up | Ready for upcoming cycle |
| In Progress | Currently being built |
| Shipped | Released to users |
| Validated/Killed | Measured and decided |

### Company Bets vs Team Bets
- **Company Beliefs**: 3-5 year strategic focus areas
- **Company Bets**: 6-12 month cross-organizational projects
- **Team Bets**: Sprint-level work aligned to company bets

### Documentation Format
Two-page maximum:
- Page 1: Overview (sponsor, stakeholders, success metrics)
- Page 2: DIBB summary explaining "why" and "what"

---

## Basecamp Shape Up

### Core Concept
Fixed time, variable scope. 6-week cycles with shaped work.

### Pitch Document (5 Ingredients)

**1. Problem**
```
Raw idea or use case
Why this matters now
Who is affected
What's the current workaround
```

**2. Appetite**
```
NOT "how long will it take" but "how much time is this worth"
Small Batch: 1-2 weeks
Big Batch: 6 weeks
```

**3. Solution**
```
Breadboarding: Rough flow diagrams
Fat Marker Sketches: Intentionally rough UI concepts
Key insight: Abstract enough to leave room for interpretation
```

**4. Rabbit Holes**
```
Technical risks identified
Complexity that could explode scope
Areas requiring research spikes
```

**5. No-Gos**
```
Explicit exclusions
Features NOT included
Adjacent problems NOT addressed
```

### Betting Table Process
- Pitches are "bet on" or not
- Rejected pitches are discarded (important ideas resurface)
- No product backlog maintained
- Each cycle starts fresh

### Key Principle
> "Shaped work is rough, solved, and bounded. It's rough because the details are left for the builders. It's solved because the main elements are figured out. It's bounded because the appetite is set."

---

## Figma's Modern PRD (Yuhki Yamashita)

### Three Phases

**Phase 1: Problem Alignment**
```
- Problem Statement
- Why now?
- Success criteria
- Goals (measurable AND immeasurable)
```

**Phase 2: Solution Alignment**
```
- Key features
- User flows
- Embedded Figma designs (live updates)
- Edge cases
- Technical considerations
```

**Phase 3: Launch Readiness**
```
Cross-functional checklists:
- [ ] Legal review
- [ ] Security review
- [ ] Marketing assets
- [ ] Support documentation
- [ ] Rollout criteria
- [ ] Metrics instrumentation
```

### Key Practices
- Ask "why one more time than you need"
- Include immeasurable goals alongside KPIs
- Native Figma embeds enable live design updates
- Prototype IS the spec

---

## Linear's Minimalist Approach

### Philosophy
No A/B tests. No metrics per project. No durable teams. Taste-driven development.

### Three Principles
1. Start with highest level, get more granular
2. Start with widest audience, get narrower
3. Start with what's least likely to change, end with what changes most

### Document Structure (1-2 pages max)

**Context**
```
The fundamental "why"
Strategic alignment
Market context
```

**Usage Scenarios**
```
Real-life narratives (not user stories)
Day-in-the-life descriptions
Emotional context included
```

**Milestones**
```
Phases of build
Incremental deliverables
Ship dates (not deadlines)
```

### Key Quote
> "Specs should be 1-2 pages." — Nan Yu, Linear

---

## Intercom's One-Page "Intermission"

### Constraint
Every product specification MUST fit on single A4 page. If it doesn't fit, clarity is insufficient.

### Format: Job Stories
```
When [situation],
I want to [motivation],
So I can [expected outcome].
```

### Philosophy
- Inspired by Facebook's oral culture over Google's documentation
- Forces ruthless prioritization
- Brevity = clarity
- If you can't explain it simply, you don't understand it

---

## Opportunity Solution Trees (Teresa Torres)

### Structure
```
                    [Desired Outcome]
                           |
            --------------------------------
            |              |               |
      [Opportunity 1] [Opportunity 2] [Opportunity 3]
            |              |               |
         -------        -------         -------
         |     |        |     |         |     |
      [Sol A][Sol B] [Sol C][Sol D]  [Sol E][Sol F]
         |     |        |     |         |     |
      [Exp] [Exp]    [Exp] [Exp]     [Exp] [Exp]
```

### Components
- **Outcomes**: Business results (often Key Results from OKRs)
- **Opportunities**: Customer needs, pain points, desires
- **Solutions**: Ideas addressing opportunities
- **Experiments**: Tests validating solutions

### Key Practice
Weekly customer touchpoints with Product Trio (PM, Design, Engineering)

---

## Jobs-to-be-Done (JTBD) Integration

### Job Statement Format
```
When [situation/trigger],
I want to [motivation/job],
So I can [expected outcome/benefit].
```

### Job Stories vs User Stories
| User Story | Job Story |
|------------|-----------|
| As a [persona] | When I [situation] |
| I want [feature] | I want to [motivation] |
| So that [benefit] | So I can [outcome] |

### Forces Framework
```
Push: Pain with current solution
Pull: Attraction of new solution
Anxiety: Fear of change
Habit: Comfort with status quo
```

---

## Prioritization Frameworks

### RICE Scoring
```
Score = (Reach × Impact × Confidence) ÷ Effort

Reach: Users affected per quarter
Impact: 3=Massive, 2=High, 1=Medium, 0.5=Low, 0.25=Minimal
Confidence: 100%=High, 80%=Medium, 50%=Low
Effort: Person-months
```

### MoSCoW
```
Must-Have: ~60% of scope
  - Critical for launch
  - No workaround exists
  
Should-Have: ~20% of scope
  - Important but not critical
  - Workaround exists
  
Could-Have: ~20% of scope
  - Nice to have
  - First to cut if needed
  
Won't-Have: Explicit exclusions
  - Not this release
  - Documented for future
```

### Kano Model
```
Basic Needs: Expected, cause dissatisfaction if missing
Performance Needs: Linear satisfaction increase
Excitement Needs (Delighters): Unexpected, create delight
```

### ICE Scoring
```
Score = Impact × Confidence × Ease
Each rated 1-10
```

### WSJF (Weighted Shortest Job First)
```
WSJF = Cost of Delay ÷ Job Duration

Cost of Delay = User-Business Value + Time Criticality + Risk Reduction
```

---

## Design Sprint as PRD Alternative

### Jake Knapp's 5-Day Sprint
| Day | Activity | Output |
|-----|----------|--------|
| Monday | Map & Target | Problem definition |
| Tuesday | Sketch | Solution concepts |
| Wednesday | Decide | Storyboard |
| Thursday | Prototype | Realistic prototype |
| Friday | Test | Validated learnings |

### Sprint Brief = Lightweight PRD
- Long-term goal
- Sprint questions
- Map of user journey
- Target moment

---

## North Star Framework Integration

### Metric Selection by Business Type
| Business Type | North Star Metric |
|---------------|-------------------|
| Attention (Media) | Time spent |
| Transaction (Marketplace) | Number of transactions |
| Productivity (SaaS) | Tasks completed / time saved |

### PRD Success Metrics Should Connect To
1. North Star Metric (company level)
2. Team-level input metrics
3. Feature-specific metrics
4. Guardrail metrics (what should NOT decrease)
