# Competitive Analysis — Weighted Scoring & Red-Teaming

## McKinsey's Approach to Competitive Research

McKinsey's differentiation in competitive analysis comes from:
1. **Preventing anchoring**: Don't evaluate the "obvious winner" first
2. **Weighted scoring**: Define criteria + weights BEFORE evaluating
3. **Red-teaming each option**: Find the best criticism of every contender
4. **Vendor bias detection**: Are "comparisons" actually sponsored content?
5. **Total cost of ownership**: Not just features, but migration, learning, lock-in
6. **"Do nothing" option**: Is the current solution actually adequate?

## Weighted Decision Matrix

### Step 1: Define Criteria (BEFORE evaluating any option)
- List 5-8 evaluation criteria based on PICO Outcome definition
- Assign weights (must sum to 100%) based on user's specific context
- Get agreement on criteria before any evaluation begins

### Step 2: Score Each Option (independently)
- Score 1-5 on each criterion
- Use evidence from research, not subjective impressions
- Document the evidence behind each score

### Step 3: Calculate Weighted Scores
- Score × Weight for each criterion
- Sum weighted scores per option
- The highest total wins — but check for hidden factors

### Step 4: Sensitivity Analysis
- What if weights change? Does the winner change?
- What if the worst-scored criterion improves? Does it matter?
- This prevents over-reliance on a single evaluation framework

## Red-Teaming Protocol

For EACH contender in the comparison:
1. Search for "[option] criticism limitations problems"
2. Search for "[option] migration away from post-mortem"
3. Search for "[option] vs alternatives comparison"
4. Document the STRONGEST criticism found
5. Assess whether the criticism is material or cosmetic

The goal: present the best CASE and best CRITICISM for each option.

## Total Cost of Ownership (TCO)

Beyond feature comparison:
- **Acquisition cost**: License, setup, implementation
- **Learning cost**: Training time, documentation quality, community support
- **Migration cost**: How hard to switch away? Data portability?
- **Maintenance cost**: Ongoing operations, updates, security patches
- **Lock-in cost**: Vendor dependency, proprietary formats, switching barriers
- **Opportunity cost**: What else could you do with these resources?

## The "Do Nothing" Option

Always include as a comparison baseline:
- Is the current solution actually adequate?
- What is the cost of NOT changing?
- What is the risk of changing?
- Sometimes "do nothing" is the optimal decision

## Vendor Bias Detection

Checklist for spotting sponsored "research":
- Does the comparison conveniently favor the publisher's product?
- Is there a disclosure statement about funding/sponsorship?
- Are criteria weighted to favor one specific option?
- Are competitors characterized fairly or with strawman arguments?
- Is the comparison dated (older competitor versions vs. newest)?

If vendor bias detected: Flag the source as Low reliability and seek
independent corroboration.

## Output Format

```markdown
## Competitive Analysis: [Topic]

### Evaluation Criteria
| Criterion | Weight | Rationale |
|---|---|---|

### Weighted Scores
| Option | Criterion 1 | Criterion 2 | ... | Total |
|---|---|---|---|---|

### Best Case for Each Option
- **Option A**: [strongest argument + evidence]
- **Option B**: [strongest argument + evidence]
- **Option C**: [strongest argument + evidence]

### Best Criticism of Each Option
- **Option A**: [strongest criticism + evidence]
- **Option B**: [strongest criticism + evidence]
- **Option C**: [strongest criticism + evidence]

### TCO Comparison
[Full cost breakdown per option]

### Recommendation
- **Winner**: [option] with [score]
- **Confidence**: [tag]
- **Key caveat**: [what would change this recommendation]
- **"Do nothing" assessment**: [is current state adequate?]
```
