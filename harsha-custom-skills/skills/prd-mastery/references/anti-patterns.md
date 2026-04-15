# PRD Anti-Patterns & Recovery Strategies

Common mistakes in PRD writing and how to avoid or fix them.

---

## Content Anti-Patterns

### 1. Over-Specification

**Symptoms:**
- 50+ page PRDs that nobody reads
- Implementation details instead of requirements
- Prescriptive UI specifications
- No room for engineering creativity

**Root Cause:**
Fear of ambiguity leading to excessive detail.

**Impact:**
- Teams lose patience and make assumptions anyway
- Document becomes outdated before development starts
- Stifles innovation and team ownership

**Recovery:**
- Focus on outcomes, not implementation
- Write testable acceptance criteria
- Separate stable context from evolving details
- Trust the team to find solutions

**Atlassian's Warning:**
> "By the time we've written a PRD it is almost always out of date."

---

### 2. Under-Specification

**Symptoms:**
- Vague requirements ("make it fast")
- Missing edge cases
- No acceptance criteria
- Undefined error handling

**Root Cause:**
Rushing to development or assuming shared understanding.

**Impact:**
- Team members make different assumptions
- Problems rear their ugly heads late in the game
- Rework and scope creep

**Recovery:**
- Include Given/When/Then acceptance criteria
- Document edge cases explicitly
- Define non-functional requirements numerically
- Review with QA early

---

### 3. Solutioning Too Early

**Symptoms:**
- Feature requests instead of problems
- No customer evidence
- "Build X" instead of "Solve Y"
- Jumping to UI mockups

**Root Cause:**
Skipping discovery work.

**Marty Cagan's Warning:**
> "PRDs written INSTEAD of discovery work—rather than after—represents the fundamental failure mode."

**Impact:**
- Building the wrong thing
- Low user adoption
- Wasted engineering effort

**Recovery:**
- Demonstrate problem validation through research
- Include customer quotes and data
- Use hypothesis format: "We believe X because Y"
- Add "Evidence" section to PRD

---

### 4. Missing Success Metrics

**Symptoms:**
- No metrics section
- High-level, unspecific goals ("improve user experience")
- No baseline measurements
- No measurement methodology

**Aakash Gupta's Observation:**
> "Metrics sections are often 'comically bad'—high-level, unspecific."

**Impact:**
- Can't measure success
- No accountability
- Feature ships but impact unknown

**Recovery:**
- Include usage metrics AND impact metrics
- Add dashboard mockups
- Define measurement methodology
- Distinguish key metrics (3-5) from leading indicators (3-5)

---

### 5. No Non-Goals Section

**Symptoms:**
- Scope keeps expanding
- "While we're at it..." requests
- No documented exclusions
- Stakeholder expectations misaligned

**Root Cause:**
Avoiding difficult scope conversations.

**Impact:**
- Scope creep
- Delayed launches
- Team burnout

**Recovery:**
- Explicit "Out of Scope" section
- Document deferred features
- Get sign-off on non-goals
- Reference non-goals when scope requests arise

---

## Process Anti-Patterns

### 6. PRD as Handoff Document

**Symptoms:**
- PM writes PRD in isolation
- Engineering sees spec only when "done"
- No collaboration during creation
- "Throw it over the wall" mentality

**Root Cause:**
Waterfall thinking in agile clothing.

**Atlassian's Warning:**
> "PMs writing requirements without team participation."

**Impact:**
- Missing technical feasibility issues
- Team lacks ownership
- Rework when constraints discovered

**Recovery:**
- Involve Product Trio from start
- Share drafts early and often
- Engineering input on approach
- Design collaboration on UX

---

### 7. Sign-Off as Gate

**Symptoms:**
- Requirements freeze after sign-off
- Changes require formal process
- Learning during development ignored
- Document becomes outdated

**Atlassian's Warning:**
> "Thorough sign-off required before starting, then requirements never updated because everyone signed off."

**Impact:**
- Document loses relevance
- Teams work around the spec
- Learning not incorporated

**Recovery:**
- Living document approach
- Version control with change log
- Regular update cadence
- Easy amendment process

---

### 8. Entire Project Spec'd Upfront

**Symptoms:**
- Months of planning before any building
- Complete spec for 6+ month project
- Detailed requirements for future phases
- No iteration based on learning

**Atlassian's Warning:**
> "Entire projects spec'd before any engineering work."

**Impact:**
- Analysis paralysis
- Outdated before development starts
- No room for learning

**Recovery:**
- Shape Up's "appetite" approach
- Spec current phase in detail
- Future phases as directional only
- Build-measure-learn cycles

---

### 9. Invisible Changes

**Symptoms:**
- Designers/developers unaware when requirements change
- No change notification system
- Silent updates to documents
- Version confusion

**Atlassian's Warning:**
> "Designers and developers not aware when requirements change."

**Impact:**
- Building to outdated requirements
- Misalignment between teams
- Frustration and rework

**Recovery:**
- Change notification system
- Version history with summaries
- Highlight recent changes
- Regular sync meetings

---

## Content Quality Anti-Patterns

### 10. Vacuous Content

**Symptoms:**
- Appears complete but says nothing
- Generic statements without specifics
- Copy-paste from other PRDs
- Filler text

**Aakash Gupta's Observation:**
> "Appearing complete with vacuous content."

**Impact:**
- False sense of alignment
- Interpretation varies
- Discovery during development

**Recovery:**
- Specific, measurable statements
- Concrete examples
- Peer review for substance
- Ask "so what?" for each section

---

### 11. Excessive Delegation to Design

**Symptoms:**
- "See mockups for details"
- No edge case documentation
- Relying on design to define behavior
- Missing error states

**Impact:**
- Edge cases discovered late
- Inconsistent behavior
- Design rework

**Recovery:**
- Document edge cases in PRD
- Error handling specifications
- State diagrams for complex flows
- Design and PRD complement each other

---

### 12. Lacking Customer Discovery

**Symptoms:**
- No customer evidence
- Assumptions presented as facts
- Internal opinions as requirements
- No validation of problem

**Impact:**
- Building unwanted features
- Low adoption
- Wasted resources

**Recovery:**
- Customer interview quotes
- Usage data analysis
- Competitive research
- Problem validation section

---

### 13. Not Compelling Enough

**Symptoms:**
- Team not excited
- Stakeholders unconvinced
- Passive approval
- Low energy in reviews

**Impact:**
- Mediocre execution
- Deprioritization risk
- Lack of advocacy

**Recovery:**
- Strong narrative arc
- Clear customer benefit
- Compelling vision
- Connect to company mission

---

## Structural Anti-Patterns

### 14. Buried Problems

**Symptoms:**
- Problem statement in middle or end
- Solution leads the document
- Features listed first
- "Why" comes after "what"

**Impact:**
- Misaligned priorities
- Solution-first thinking
- Weak problem understanding

**Recovery:**
- Problem statement first
- Evidence immediately after
- Solution section later
- Non-goals before features

---

### 15. Missing Context

**Symptoms:**
- Assumes reader knowledge
- No background section
- Jargon without definition
- Historical context missing

**Impact:**
- New team members confused
- Stakeholders misunderstand
- Context lost over time

**Recovery:**
- Background section
- Glossary for jargon
- Link to related documents
- Assume intelligent but uninformed reader

---

### 16. No Single Source of Truth

**Symptoms:**
- Requirements in multiple places
- Conflicting information
- Outdated copies circulating
- Confusion about current version

**Impact:**
- Building to wrong requirements
- Wasted discussion time
- Trust erosion

**Recovery:**
- Single canonical location
- Version control
- Clear ownership
- Deprecate old copies

---

## Recovery Framework

### For Any Anti-Pattern

**Step 1: Diagnose**
- Which anti-pattern(s) present?
- What's the root cause?
- What's the impact?

**Step 2: Address Root Cause**
- Process change needed?
- Skills development?
- Tool improvement?
- Culture shift?

**Step 3: Remediate Current PRD**
- Can it be fixed in place?
- Does it need rewrite?
- Who needs to be involved?

**Step 4: Prevent Recurrence**
- Template updates
- Checklist additions
- Review process changes
- Training needs

---

## PRD Quality Checklist

**Before Sharing:**
- [ ] Problem statement has evidence
- [ ] Success metrics have baselines and targets
- [ ] Non-goals explicitly listed
- [ ] Acceptance criteria are testable
- [ ] Edge cases documented
- [ ] No over-specification
- [ ] No under-specification
- [ ] Cross-functional input incorporated
- [ ] Compelling narrative
- [ ] Single source of truth established

**Before Sign-Off:**
- [ ] All stakeholder feedback addressed
- [ ] Technical feasibility confirmed
- [ ] Dependencies identified
- [ ] Risks with mitigations listed
- [ ] Living document process established
