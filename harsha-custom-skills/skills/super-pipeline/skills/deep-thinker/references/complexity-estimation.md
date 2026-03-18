# Complexity Estimation Reference

Framework for rapidly assessing problem complexity and calibrating thinking depth in the Deep Thinker skill.

## Table of Contents
- [Why Complexity Matters](#why-complexity-matters)
- [30-Second Assessment](#30-second-assessment)
- [Complexity Dimensions](#complexity-dimensions)
- [Depth Calibration Matrix](#depth-calibration-matrix)
- [Output Level Mapping](#output-level-mapping)
- [Complexity Escalation](#complexity-escalation)
- [Estimation Heuristics](#estimation-heuristics)

---

## Why Complexity Matters

The Deep Thinker currently produces all 8 analysis files for every problem, regardless of scope. This is inefficient:

- **Trivial problem** ("rename a variable"): Wastes tokens on OPTIMIZATIONS, CREATIVE_IDEAS, full EDGE_CASES
- **Medium problem** ("add newsletter feature"): Appropriate depth, all 8 files needed
- **Complex problem** ("redesign authentication system"): 8 files are minimum, may need even deeper thinking

**The Goal**: Estimate complexity first, then calibrate output appropriately.

---

## 30-Second Assessment

### The Quick Decision Tree

```
1. How many distinct systems does this touch?
   - One system only → Likely Trivial/Small
   - 2-3 systems → Likely Small/Medium
   - 4+ systems or fundamental change → Likely Medium/Complex

2. How many unknowns are present?
   - Clear requirements, known APIs → Likely Trivial/Small
   - Some ambiguity, minor unknowns → Likely Small/Medium
   - Major unknowns, competing requirements → Likely Medium/Complex

3. What's the blast radius if wrong?
   - Only affects one component → Likely Trivial/Small
   - Breaks some features but recoverable → Likely Small/Medium
   - Could break production or data → Likely Medium/Complex

4. Is this reversible?
   - Easy to undo or rollback → Reduce estimated complexity by 1 level
   - Hard to reverse → Increase estimated complexity by 1 level
```

### Quick Assessment Questions

Ask yourself these in order (takes ~30 seconds):

1. **"Does this change touch one file or many?"**
   - One file → Trivial/Small
   - 2-3 files → Small/Medium
   - 4+ files → Medium/Complex

2. **"Are there security implications?"**
   - No → Standard assessment
   - Yes → Add one complexity level

3. **"Is this reversible?"**
   - Fully reversible → Standard assessment
   - Hard/impossible to reverse → Add one complexity level

4. **"Are there regulatory/compliance requirements?"**
   - No → Standard assessment
   - Yes → Add one complexity level

5. **"Is this foundational (will other features build on it)?"**
   - No → Standard assessment
   - Yes → Add one complexity level

---

## Complexity Dimensions

### Technical Complexity

**Low (Trivial/Small)**
- Single algorithm or simple change
- No new APIs or integrations
- Isolated from other systems
- Example: Add a new button, format a date field

**Medium (Small/Medium)**
- Multiple algorithms interacting
- Involves 2-3 existing APIs
- Cross-file changes but not cross-system
- Example: Add input validation, improve sorting

**High (Medium/Complex)**
- Complex algorithms with interdependencies
- Requires new API integrations or contracts
- Touches architecture or shared components
- Example: Add real-time notifications, implement caching layer

### Domain Complexity

**Low (Trivial/Small)**
- Well-defined business logic
- No competing requirements
- Clear success criteria
- Example: Display user's name on profile

**Medium (Small/Medium)**
- Some business rule ambiguity
- Minor competing concerns
- Stakeholder alignment needed
- Example: Implement discount calculation with special cases

**High (Medium/Complex)**
- Ambiguous or evolving business rules
- Multiple competing requirements
- Regulatory or compliance implications
- Example: Implement fraud detection, GDPR compliance

### Integration Complexity

**Low (Trivial/Small)**
- No external integrations
- Uses existing, well-known APIs
- No data migration needed
- Example: Add logging to existing function

**Medium (Small/Medium)**
- Integrates with 1-2 external APIs
- Some data transformation needed
- Minor backward compatibility concerns
- Example: Add payment gateway integration

**High (Medium/Complex)**
- Integrates with 3+ external systems
- Significant data migration/transformation
- Critical backward compatibility requirements
- Example: Migrate database schema, swap authentication provider

### Uncertainty Complexity

**Low (Trivial/Small)**
- All requirements clear
- No ambiguities
- Full context available
- Example: "Add a red button next to the blue button"

**Medium (Small/Medium)**
- Minor ambiguities in requirements
- Some unknowns about existing code
- Partial context, can make reasonable assumptions
- Example: "Improve search performance" (what search, what's slow?)

**High (Medium/Complex)**
- Major requirement ambiguities
- Significant unknowns about system behavior
- Missing critical context
- Example: "Make everything work better" or "Ensure system is scalable"

---

## Depth Calibration Matrix

### Map Complexity to Thinking Depth and Output

| Complexity | Time to Implement | Output Files | Analysis Depth | Expert Depth |
|-----------|------------------|--------------|---|---|
| **Trivial** | < 5 min | Inline answer, no files | Surface | No file output needed |
| **Small** | 5-30 min | 3: OVERVIEW, IMPLEMENTATION, EDGE_CASES | Standard | Main path + common errors |
| **Medium** | 30 min - 4 hrs | 6: all except CREATIVE_IDEAS, OPTIMIZATIONS | Deep | All paths + edge cases + alternatives |
| **Complex** | 4+ hrs or foundational | All 8 files at exhaustive depth | Exhaustive | Full expert panel + race conditions + future |

### What Each Level Means

**Trivial (No Files)**
- Problem is solved in 30 seconds of thinking
- Answer can be inline in conversation
- No persistent output needed
- Example response: "Yes, you can use a Set for O(1) lookups"

**Small (3 Files)**
- OVERVIEW: What we're building and why
- IMPLEMENTATION: Step-by-step, but less granular than Medium
- EDGE_CASES: Happy paths + common error states
- No need for ARCHITECTURE (simple enough) or OPTIMIZATIONS (minimal gain)

**Medium (6 Files)**
- OVERVIEW: Comprehensive goals and success criteria
- CURRENT_STATE: Understanding what exists
- ARCHITECTURE: Multiple approaches considered and selected
- IMPLEMENTATION: Detailed steps with file:line references
- EDGE_CASES: All scenarios, error states, race conditions
- EXECUTION_CHECKLIST: Ordered, atomic steps
- Skip CREATIVE_IDEAS and OPTIMIZATIONS (not critical path)

**Complex (All 8 Files)**
- All files included at exhaustive depth
- OVERVIEW: Foundational impact, long-term vision
- ARCHITECTURE: Deep trade-off analysis, future extensibility
- IMPLEMENTATION: Micro-steps with exact context
- EDGE_CASES: Every conceivable scenario, failure modes, race conditions
- OPTIMIZATIONS: Performance and code quality ideas
- CREATIVE_IDEAS: Ways to exceed expectations
- EXECUTION_CHECKLIST: Atomic, reversible steps

---

## Output Level Mapping

### How to Decide Output Level

Start with your 30-second assessment. Then refine:

#### Deciding Between Trivial and Small

**Use Trivial if:**
- Question can be answered in 2-3 sentences
- No follow-up implementation needed
- Executor won't need detailed steps
- Examples: "Can we use X?" "What's the best way to Y?"

**Use Small if:**
- Answer requires structured thinking
- Executor needs specific steps to implement
- Requires understanding current state + changes
- Examples: "Add a button here" "Refactor this function"

#### Deciding Between Small and Medium

**Use Small if:**
- Changes are isolated to one area
- Minimal impact on other systems
- Straightforward implementation path
- Low uncertainty

**Use Medium if:**
- Changes impact 2-3 different areas
- Need architectural decisions (even small ones)
- Some alternatives to consider
- Medium uncertainty about approach

#### Deciding Between Medium and Complex

**Use Medium if:**
- 30 min - 4 hours of implementation
- Clear success criteria
- Impact contained to one feature
- Standard complexity, no foundational elements

**Use Complex if:**
- 4+ hours of implementation
- This is foundational (other features will build on it)
- Architectural decisions have long-term impact
- High uncertainty requiring extensive exploration
- Security, performance, or compliance implications

---

## Complexity Escalation

### When Initial Assessment Was Wrong

**Signs You Underestimated**

As you begin analysis, watch for:
- "I need to understand X system before I can decide" → Dependencies grew
- "Wait, there's a design pattern we need to reconsider" → Architecture more complex
- "This interacts with Y in unexpected ways" → System interactions more intricate
- "We need to handle scenarios I didn't initially consider" → Edge cases multiplied
- "This will need to scale/be secure/integrate differently than expected" → Non-functional requirements more complex

**What To Do**

1. **Stop and reassess** - Don't push forward with insufficient depth
2. **Acknowledge escalation** - "Initial assessment: Small. Revised: Medium. Here's why..."
3. **Expand output** - Add missing files (ARCHITECTURE, OPTIMIZATIONS, etc.)
4. **Restart analysis in those files** - Don't try to "add them incrementally"
5. **Signal to executor** - Make complexity change explicit in OVERVIEW

**Example Escalation**

```
Initial: Small complexity (add a checkbox)
30 seconds in: Wait, this checkbox needs to persist across sessions?
5 minutes in: And sync across devices? And integrate with the settings API?

New Assessment: Medium complexity
New Output: All 6 files (not just 3)
Signal: "OVERVIEW.md - Complexity Escalation"
```

### When You Overestimated

**Signs You Overestimated**

- You're 10 minutes in and could explain it in 2 paragraphs
- All edge cases fit on one page
- There's no real architectural decision to make
- Alternatives are obvious and quickly evaluated

**What To Do**

1. **Don't waste tokens** - Stop the exhaustive analysis
2. **Compress appropriately** - Move from Medium to Small output
3. **Signal the change** - "Revised assessment: Smaller than initially thought"
4. **Keep what's valuable** - Don't delete files, just reduce depth

---

## Estimation Heuristics

### The Regret Minimization Rule

When in doubt between two complexity levels:
- **Overestimating costs**: Wasted thinking tokens, slower response
- **Underestimating costs**: Executor discovers gaps, asks questions, requires deeper rethink

**When uncertain, go one level deeper.** Wasted tokens are cheaper than executor friction.

### File Count Heuristic

Count files that will change:

```
1 file changed → Trivial/Small
2-3 files changed → Small/Medium
4-5 files changed → Medium
6+ files changed → Medium/Complex
Affects database schema → Add 1 level
Affects APIs → Add 1 level
Affects security → Add 1 level
```

### Stakeholder Complexity Heuristic

- **0 stakeholders** (personal tool): Lower complexity
- **1 stakeholder** (one team feature): Standard assessment
- **2+ stakeholders**: Add 1 complexity level
- **Regulatory/compliance**: Add 1-2 levels

### Time Estimation Heuristic

If implementation will take:
- < 5 minutes → Trivial
- 5-30 minutes → Small
- 30 min - 4 hours → Medium
- 4+ hours → Complex

(Use as secondary check, not primary assessment)

### The "Would an executor ask questions?" Test

Ask yourself: "If I passed these files to another Claude session, would they ask clarifying questions?"

- **No questions expected** → Complexity is right
- **Minor questions** → You're probably right, but could add depth
- **Major questions** → You underestimated complexity by 1 level

---

## Practical Workflow

### When You Receive a Problem

1. **Read the problem** (30 seconds)
2. **Ask the 5 quick questions** (30 seconds)
3. **Make initial assessment** (e.g., "This looks Medium")
4. **Start analysis with that depth**
5. **Monitor for escalation signals**
6. **If signals appear, expand output and re-assess**
7. **If analysis is too easy, compress output**
8. **Document your assessment** in OVERVIEW.md

### The Assessment Section of OVERVIEW.md

Always include this section:

```markdown
## Complexity Assessment

**Initial Assessment**: [Trivial/Small/Medium/Complex]
**Revised Assessment**: [If changed, explain why and when]
**Reasoning**:
- [ ] Files affected: [number and list]
- [ ] Systems touched: [number and types]
- [ ] Unknowns: [list major unknowns]
- [ ] Reversibility: [easy/medium/hard to reverse]
- [ ] Foundational: [will other features build on this?]

**Assessment Confidence**: [High/Medium/Low - if Low, note areas of uncertainty]
```

This documents your thinking for the executor and shows where you escalated complexity during analysis.

