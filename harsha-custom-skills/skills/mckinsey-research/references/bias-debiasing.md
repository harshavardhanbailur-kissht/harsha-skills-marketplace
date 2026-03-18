# Procedural Debiasing System

## Why Procedural, Not Declarative

Teaching about bias has "moderate to no effect" on actual bias reduction.
Procedural interventions — mandatory workflow steps — produce measurable
improvements. This reference implements debiasing as NON-SKIPPABLE checkpoints.

## 9 Documented LLM Biases

### 1. Confirmation Bias
- **What**: Preferentially seeking/weighting evidence that confirms initial hypothesis
- **Procedural fix**: Test with OPPOSING hypotheses FIRST. Search for disconfirming
  evidence before confirming evidence. Log evidence for ALL hypotheses before evaluating.
- **Checkpoint**: "Have I searched for evidence AGAINST my leading hypothesis?"

### 2. Pattern Amplification Bias
- **What**: AI amplifies patterns from training data, treating correlations as causation
- **Procedural fix**: Check statistical distributions. Ask "is this a real pattern or
  an artifact of training data?" Require independent statistical evidence.
- **Checkpoint**: "Am I citing a real-world pattern or reflecting training data?"

### 3. Recency Bias
- **What**: Overweighting recent sources, underweighting foundational older work
- **Procedural fix**: Require balance — at least one foundational source (5+ years old)
  for every recent source. Ask "has the fundamental truth changed, or just the details?"
- **Checkpoint**: "Have I included foundational sources alongside recent ones?"

### 4. Authority Bias
- **What**: Accepting claims from prestigious sources without critical evaluation
- **Procedural fix**: Validate claims from authoritative sources against at least one
  NON-authority source. Ask "would I accept this if it came from an unknown author?"
- **Checkpoint**: "Have I validated prestigious claims against independent evidence?"

### 5. Semantic Bias
- **What**: Different framing of the same question produces different conclusions
- **Procedural fix**: Rephrase the research question 2-3 different ways. Search each.
  Compare results. If framing changes the answer, the evidence is weak.
- **Checkpoint**: "Does my conclusion survive reframing?"

### 6. Availability Cascade
- **What**: Frequently cited claims become "true" through repetition, not evidence
- **Procedural fix**: For any widely-repeated claim, trace to ORIGINAL source. Search
  for what ISN'T being said. Look for the dog that didn't bark.
- **Checkpoint**: "Am I citing repetition or independent evidence?"

### 7. Coherence Bias
- **What**: Preferring conclusions that form a neat, coherent narrative over messy truth
- **Procedural fix**: Explicitly test for logical contradictions. Ask "is this conclusion
  neat because reality IS neat, or because I'm oversimplifying?"
- **Checkpoint**: "Have I preserved genuine messiness or forced coherence?"

### 8. Statistical Reasoning Bias
- **What**: Mishandling base rates, sample sizes, p-values, confidence intervals
- **Procedural fix**: Require numerical decomposition for any statistical claim. Don't
  accept "significant" without checking methodology. Verify sample sizes.
- **Checkpoint**: "Have I verified the statistics, not just cited them?"

### 9. Consensus Bias
- **What**: Treating majority opinion as evidence when it may be groupthink
- **Procedural fix**: For any consensus claim, require at least one contrarian search.
  Find the strongest DISSENTING voice and evaluate their evidence.
- **Checkpoint**: "Have I found and evaluated the strongest dissenting evidence?"

## Mandatory Bias Checkpoints

Execute these at TWO mandatory points in the workflow:

### Checkpoint A: After Phase 2 (Before Search)
Before executing ANY search:
1. Review hypotheses — are they genuinely different or slight variations?
2. Check for anchoring — is one hypothesis clearly "favored" already?
3. Verify at least one hypothesis contradicts the "obvious" answer
4. Ensure search queries don't embed bias (neutral framing)

### Checkpoint B: After Phase 5 (Before Stress Test)
Before declaring synthesis complete:
1. **Confirmation check**: Is evidence weighted fairly across hypotheses?
2. **Recency check**: Are foundational sources adequately represented?
3. **Authority check**: Did prestigious sources get unearned weight?
4. **Circular check**: Do "independent" sources trace to the same original?
5. **Consensus check**: Has contrarian evidence been genuinely evaluated?
6. **Coherence check**: Have contradictions been preserved or forced into narrative?

### Evidence Re-Weighting Protocol
When bias is detected:
1. Identify the biased dimension (source, framing, weighting)
2. Apply correction: search for evidence from the OPPOSITE direction
3. Re-evaluate the finding with balanced evidence
4. Document the bias detected and correction applied
5. If correction changes the conclusion, flag as "bias-sensitive finding"

## Integration with Workflow

| Phase | Bias Risk | Checkpoint |
|-------|-----------|-----------|
| Phase 1 (Scope) | Framing bias in question | Neutral rewrite mandatory |
| Phase 2 (Hypotheses) | Anchoring to "obvious" answer | Checkpoint A |
| Phase 3 (Search) | Confirmation bias in queries | Vary search order |
| Phase 4 (Validation) | Authority bias | Non-authority validation |
| Phase 5 (Synthesis) | All 9 biases | Checkpoint B |
| Phase 6 (Stress Test) | Coherence bias | Expert disagreement preservation |

## Empirical Evidence (2024-2025 Research)

### Anchoring Bias in LLMs Is Quantified
- Anchoring index: 0.37 (models retain ~37% of anchor difference)
- Affects 22-61% of questions depending on domain
- Mechanism: "shallow-layer acting" — bias at shallow computation levels
- Simple mitigations (CoT, Reflection) do NOT reduce expert anchoring
- Source: Lou et al. 2025, He et al. 2025

### Sycophancy Is Amplified by Training
- RLHF training INCREASES sycophancy (Sharma et al., ICLR 2024)
- Preference models sacrifice truthfulness for sycophantic appeal
- Larger, reasoning-capable models resist better (EMNLP 2025)
- Procedural fix: Generate competing hypotheses regardless of user framing

### Procedural > Declarative (Empirically)
- 80% of procedural debiasing strategies were effective (Meade et al., ACL 2022)
- Self-Debiasing improved scores on ALL bias benchmarks
- But: debiasing training impact drops 4 weeks post-intervention
- Implication: Procedures must be embedded in EVERY execution, not trained once

### Multi-Agent Debate Reduces Bias
- 3 agents debating: 50% → 98% accuracy on arithmetic (2023)
- 4 agents, 5 rounds: 76% → 88% on reasoning tasks
- Heterogeneous agents outperform identical by ~3.5%
- 2 debate rounds capture most gains

### Structured Prompting Reduces Errors
- Structured prompts: >99% schema adherence vs conversational
- Up to 60% fewer integration errors
- Reasoning LMs show marginal gains; non-reasoning LMs benefit more
- Source: 2025 empirical study

### ADaPT Framework Validated
- 28.3% improvement on ALFWorld, 27% on WebShop, 33% on TextCraft
- Mechanism: Only decompose when execution FAILS (not pre-decomposed)
- Source: NAACL 2024
