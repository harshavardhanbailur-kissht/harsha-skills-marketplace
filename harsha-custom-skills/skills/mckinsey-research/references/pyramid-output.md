# Pyramid Principle Output — Detailed Reference

## The Three Rules of the Pyramid (Barbara Minto)

1. **Hierarchical Necessity**: The point above must be a SUMMARY derived from those below
2. **Logical Consistency**: Ideas grouped together must be logically identical and properly ordered
3. **Structural Depth**: Facts → Arguments → Recommendations in strict hierarchy

## Presenting Top-Down

"Think from the bottom up, present from the top down."

```
APEX: Answer / Key Recommendation (1 sentence)
    ↓
LAYER 2: 3 Key Supporting Arguments (MECE — no overlaps, no gaps)
    ↓
LAYER 3: Evidence, data, case studies for each argument
```

## MECE: Mutually Exclusive, Collectively Exhaustive

- **ME**: No category overlaps; each element fits one and only one category
- **CE**: All possible options covered; no gaps in coverage
- **Rule of Three**: Organize supporting arguments into exactly 3 points
  - 2 points = second is probably too broad
  - 4+ points = you've failed to group logically

### MECE Test Questions
- "If I add all these categories together, do they cover 100% of the topic?"
- "Is there any overlap between these categories?"
- "Would an expert say 'you missed X'?"

## SCR Narrative Framework

**Situation** (25-30% of executive summary):
- Current landscape, context, baseline
- What the reader already knows or needs to know
- Sets the stage without judgment

**Complication** (included in first 25-30%):
- The problem, tension, disruption, or inflection point
- What changed? What broke? Why act now?
- Creates urgency and narrative tension

**Resolution** (60-70% of executive summary):
- The answer, recommendations, and actions
- Specific, sequenced, and resourceable
- Connected directly to business metrics the audience tracks

### SCQA Variant
Adds a "Question" between Complication and Answer:
"Given this complication, what must we ask ourselves?"
This creates explicit narrative tension — the reader WANTS the answer.

## Bold-Bullet Executive Summary Format

```markdown
## Executive Summary

**[Situation + Complication in 2-3 sentences setting context and urgency]**

**[Bold key finding #1 — the most important conclusion]**
- Supporting evidence with specific data point
- Source attribution

**[Bold key finding #2 — second most important]**
- Supporting evidence
- Source attribution

**[Bold key finding #3 — third most important]**
- Supporting evidence
- Source attribution

**[Bold recommendation — what to do about it]**
- Specific actions, sequenced, with expected outcomes
```

This format allows C-suite executives to grasp the complete argument
by scanning BOLD TEXT ONLY in 2-3 minutes.

## Visual Design Standards

### One Chart = One Idea
- Each visualization communicates exactly one insight
- Title IS the insight statement (not a description of the chart)
  - BAD: "Revenue by Quarter 2024-2025"
  - GOOD: "Revenue growth accelerated 47% after Q3 pricing change"

### Color as Function
- Neutral base palette for all data
- Single highlight color for the key takeaway data point
- Never decorative color — every color choice must have analytical meaning

### Annotation & Callouts
- Arrows pointing to the key data point
- Callout boxes explaining "what this means"
- No ambiguity — reader should not have to interpret

### Text Density
- If a slide looks like a Wikipedia article, it will be skipped
- Maximum 6 lines of text per visual
- White space IS a design element — do not fill every pixel

## Full Report Structure Template

```markdown
# [Research Topic]: [One-Line Conclusion]

## Executive Summary
[SCR format — see bold-bullet template above]

## Research Metadata
- Scrutiny Tier: [Standard/Enhanced/Maximum]
- Date: [ISO-8601]
- Sub-questions investigated: [list]
- Searches executed: [count and types]
- Sources evaluated: [found → screened → included]
- Competing hypotheses tested: [count]

## Key Findings

### Finding 1: [Bold Claim Statement]
[2-3 paragraph analysis with evidence]
- **Likelihood**: [Certain/Highly Likely/Likely/Possible/Unlikely]
- **Evidence Quality**: [High/Moderate/Low/Very Low]
- **Sources**: [src_001, src_003, src_007]
- **Caveats**: [conditions under which this might not hold]

### Finding 2: [Bold Claim Statement]
[repeat pattern — MECE organized]

### Finding 3: [Bold Claim Statement]
[repeat pattern]

## Competing Positions
### Position A: [Name/Description]
- Evidence supporting: [specific sources and data]
- Strength of evidence: [assessment]

### Position B: [Name/Description]
- Evidence supporting: [specific sources and data]
- Strength of evidence: [assessment]

### Current Assessment
[Which position evidence favors and WHY]

### What Would Change This Assessment
[Specific conditions or evidence that would shift the conclusion]

## Evolution & Context
### How We Got Here
[Historical narrative — what problem was being solved, what was replaced]

### Current State
[Present situation in context]

### Where It's Going
[Emerging trends, successors, trajectory]

## Pre-Mortem: What If We're Wrong
| Failure Mode | Probability | What Would Change Assessment |
|---|---|---|
| [Description] | [High/Medium/Low] | [Specific trigger] |

## Gaps & Limitations
- What couldn't be determined: [list]
- What needs further research: [list]
- Known biases in this research: [list]

## Source Registry
| ID | Type | Title | URL | Date | Reliability |
|---|---|---|---|---|---|
| src_001 | [official/academic/blog/repo] | [title] | [url] | [date] | [High/Moderate/Low] |
```

## Advanced McKinsey Communication Techniques

### The Governing Thought
The single most important idea — sits at the top of the pyramid.
- Answers the primary business/research question
- Is actionable (implies a recommendation)
- Drives ALL supporting arguments
- Must be stated BEFORE writing begins (not discovered during writing)
- Test: "If the reader remembers only ONE thing, what should it be?"

### The "So What?" Test
Every finding, every chart, every paragraph must pass: "Why does this matter?"
- If removing it doesn't weaken the argument: remove it
- Apply to every slide/section: does every element prove the title claim?
- Weak: "Competitor Analysis" → Strong: "Competitor X threatens 15% market share"

### Day One Hypothesis
Form initial hypothesis BEFORE deep research (not after):
1. Hours 1-4: Gather initial information (quick scan of landscape)
2. Hours 5-8: Pattern recognition (3-5 most likely root causes)
3. Hour 24: Formulate testable hypothesis
4. Guide all subsequent research toward validating OR refuting this hypothesis
5. Be willing to pivot when evidence contradicts

### Issue Tree Decomposition
Break problems into MECE sub-problems (not mind maps):
- **Diagnostic trees**: "Why?" questions (root cause analysis)
- **Solution trees**: "How?" questions (alternative solutions)
- Each level answers the question completely
- Test: If evidence covers only some branches, the tree is not collectively exhaustive

### SCQA vs SCR — When to Use Each
| Framework | Best For | Audience |
|---|---|---|
| SCQA (Situation-Complication-Question-Answer) | Executive presentations, building buy-in | Unfamiliar audience, needs narrative tension |
| SCR (Situation-Complication-Resolution) | Technical reports, direct recommendations | Familiar audience, wants speed |

### Ghost Deck Method
Build the storyline BEFORE populating data:
1. Write hypothesis-driven headlines for each section
2. Map the narrative journey (problem → why it matters → solution → implementation)
3. Identify data gaps (what evidence is missing for each headline?)
4. Fill in evidence and analysis (only after structure is complete)
- Use "dot-dash" outline: dots = narrative arguments, dashes = proof points

### Handling Uncertainty Without Hedging
Don't use "may/could/possibly" without structure:
- **No-regrets moves**: Actions that pay off regardless → definitive language
- **Options/hedging**: Preserve flexibility → "Recommend pilot before full deployment"
- **Scenario planning**: Multiple futures → "Base case: 8% growth; downside: 2%"
- **Cone of uncertainty**: Confidence bands → "80% confidence range: $40M-$60M"

## Quality Checklist for Output

- [ ] Governing thought stated explicitly at the top
- [ ] Executive summary follows SCR/SCQA with 60-70% Resolution
- [ ] Bold-bullet format scannable in 2-3 minutes
- [ ] Exactly 3-5 key findings (MECE organized)
- [ ] Every finding passes the "So What?" test
- [ ] Every finding has confidence + evidence quality tags
- [ ] Competing positions documented (not silently resolved)
- [ ] Evolution narrative included
- [ ] Pre-mortem completed with failure modes
- [ ] Source registry with full provenance
- [ ] Gaps and limitations explicitly stated
- [ ] Uncertainty handled via scenarios, not hedging
- [ ] Charts/visuals follow one-idea principle (if applicable)
- [ ] Issue tree shows MECE decomposition of the problem
