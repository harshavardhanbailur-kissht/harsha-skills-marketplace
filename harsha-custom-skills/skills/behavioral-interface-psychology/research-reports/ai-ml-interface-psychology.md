# AI/ML Interface Psychology Research

## Executive Summary

This research compilation synthesizes evidence-based findings from CHI papers, Google PAIR research, Microsoft HAX toolkit, IBM AI UX guidelines, and Nielsen Norman Group research on human-AI interaction.

---

## 1. Confidence Indicators for AI Outputs

### Display Format Research

**Threshold Mapping:**
- Green for high confidence (>=85%)
- Yellow for medium (60-84%)
- Red for low (<60%)

**Key CHI 2025 Finding:** Confidence alignment significantly impacts decision-making quality.

**Critical Finding:** Confidence ratings did **not** enhance users' ability to detect AI-generated hallucinations.

**Verbal vs Numeric Uncertainty:**
- **Medium verbalized uncertainty** (e.g., "It could be...") consistently leads to higher user trust, satisfaction, and task performance

### Practical Thresholds

| Confidence Level | Visual Indicator | User Action Suggested |
|-----------------|------------------|----------------------|
| >=85% (High) | Green check/solid | Accept with verification |
| 60-84% (Medium) | Orange/yellow caution | Review carefully |
| <60% (Low) | Red warning/faded | Seek additional validation |

---

## 2. Explanation UI (Explainable AI)

### User Comprehension Research

**LIME vs. SHAP:**
- Data scientists who work daily on ML and XAI **tend to overtrust** explanations
- Converting SHAP scores into more digestible forms increases understanding

**Saliency Map Study:**
- **Users did not prefer any approach** regarding trust or explanation satisfaction
- **Grad-CAM** demonstrated highest user abilities
- Mathematical metrics often counterintuitively related to user understanding

**N=4,302 Study Finding:**
- AI explanations enhanced task performance when AI prediction confidence is high or users' self-confidence is low

### Counterfactual Explanations

**Critical Factors:**
1. **Feasibility** - Most influential factor
2. **Trust** - Belief that suggested changes would bring intended outcomes

### Cognitive Load Considerations

**N=271 physicians study:**
- Different explanation types strongly influence cognitive load, task performance, and task time

**Progressive Disclosure Pattern:**
- Reveals complexity gradually
- Improves learnability, efficiency, and error rate

---

## 3. AI Hallucination Handling

### User Detection of Errors

**Critical Finding:** In unfamiliar domains, people trust AI-generated answers without critical evaluation.

### Trust Recovery Research

**Trust Repair Strategies (ranked):**
1. **Model Update** - Most effective; can surpass pre-violation trust
2. **Apologies** - Substantially effective
3. **Explanation with Solution** - Users want solutions, not just explanations
4. **Denial** - Perceived as deceptive; **avoid this approach**

### Warning/Disclaimer Effectiveness

**Critical Finding:** Labels and generic disclaimers **do not necessarily induce scepticism** and have limited practical value.

**More Effective:** Retroactive debunking that specifically counters misinformation.

---

## 4. User Mental Models of AI

### Anthropomorphism Effects

- Highly anthropomorphic avatars correlate with **elevated empathy and trust**
- **Caution:** Link between humanlike cues and trust is **profoundly subgroup-dependent**
- Excessive anthropomorphism may **damage trust** (uncanny valley)

### Over-Trust and Under-Trust

- Mere knowledge of AI-generated advice causes **overreliance**
- **UC Merced Study:** ~two-thirds of people in simulated life-or-death decisions allowed robots to change their minds
- Detailed explanations often lead to **overreliance**, not calibrated trust

### Algorithm Aversion vs. Appreciation

- Higher trust in algorithms for **lower-degree unstructured tasks**
- Higher trust in humans for **complex unstructured tasks**

---

## 5. Human-AI Collaboration

### Task Allocation

- Research shows human-AI collaboration is **"not very collaborative yet"**
- Explanations support humans to follow AI when accurate or **overrule AI when wrong**

### Override and Correction UX

- Users prefer **high levels of human control and lower AI autonomy**
- When systems initiate delegation uninvited, it **increases perceived self-threat**

### Feedback Loops

**Design Principles:**
- Make feedback collection frictionless
- Acknowledge feedback receipt
- Communicate when adjustments will occur
- Show how feedback benefits user

---

## 6. Key Frameworks

### Microsoft HAX Toolkit - 18 Guidelines

**Four Categories:**
1. **Initially:** Make clear what system can do and how well
2. **During Interaction:** Take context into consideration
3. **When Wrong:** Support graceful degradation and recovery
4. **Over Time:** Manage changes cautiously

### Google PAIR Guidebook

**Six Chapters:**
1. User Needs + Success Definition
2. Data Collection + Evaluation
3. Mental Models
4. Explainability + Trust
5. Feedback + Control
6. Errors + Graceful Failure

---

## Myths Debunked

| Myth | Reality |
|------|---------|
| More explanation = more trust | Detailed explanations often lead to **overreliance** |
| Confidence displays help detect hallucinations | Confidence ratings did **not enhance** detection |
| More humanlike = more trust universally | Effect is **profoundly subgroup-dependent** |
| Users distrust algorithms | Many show **algorithm appreciation** |
| Users want maximum automation | Users prefer **high human control** |

---

## Sources

- CHI 2025 - AI Confidence Research
- Microsoft HAX Toolkit
- Google PAIR Guidebook
- IBM Design for AI
- Nielsen Norman Group
