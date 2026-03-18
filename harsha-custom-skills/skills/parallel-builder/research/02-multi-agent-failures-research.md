# Research: Multi-Agent Failure Modes (MAST Framework) & Resilience Patterns

**Tier**: Maximum Scrutiny | **Date**: Feb 2026 | **Sources**: 10 validated
**Confidence**: HIGH (peer-reviewed NeurIPS 2025 spotlight + 1600+ annotated traces)

---

## Key Findings

### 1. MAST Taxonomy: 14 Failure Modes in 3 Categories (HIGH confidence)
UC Berkeley's MAST (Multi-Agent System Failure Taxonomy) analyzed 1,600+ traces across 7 MAS frameworks with 0.88 inter-annotator agreement (kappa).

**Category 1: System Design Issues**
- Poor prompt design, insufficient model capacity, missing tools
- Upstream specification flaws amplified in multi-agent contexts

**Category 2: Inter-Agent Misalignment (36.94% of failures) — LARGEST**
- FM-2.1: Unexpected conversation resets (2.20%)
- FM-2.2: Wrong assumptions instead of seeking clarification (6.80%)
- FM-2.3: Task derailment (7.40%)
- FM-2.4: Withholding crucial information (0.85%)
- FM-2.5: Ignoring other agents' input (1.90%)
- FM-2.6: Reasoning-action mismatch (13.2%) — **single largest failure mode**

**Category 3: Task Verification Gaps (21.30%)**
- FC3.1: Premature termination (6.20%)
- FC3.2: No/incomplete verification (8.20%)
- FC3.3: Incorrect verification (9.10%)

**Source**: [MAST arXiv:2503.13657](https://arxiv.org/abs/2503.13657), [MAST GitHub](https://github.com/multi-agent-systems-failure-taxonomy/MAST)

### 2. Key Insight: It's Orchestration, Not Models (HIGH confidence)
- Many failures stem from poor system DESIGN, not model performance
- Agents operate with incorrect assumptions, ignore peer input, fail to verify
- Simple context or communication protocols are INSUFFICIENT for FC2 failures
- FC2 failures demand deeper "social reasoning" capabilities
- No single error category disproportionately dominates → diverse failure landscape
- **Source**: [MAST NeurIPS 2025 Spotlight](https://openreview.net/forum?id=fAjbYBmonr)

### 3. Independent Verifier = +15.6% Improvement (HIGH confidence)
- Adding an independent verification agent improved ChatDev by 15.6%
- Verifier's sole responsibility: evaluate whether outputs meet requirements
- ChatDev shows 33-75% total failure rates without proper verification
- **Source**: [MAST Paper](https://arxiv.org/abs/2503.13657)

### 4. AI Code Generation Failure Rates (HIGH confidence)
From production analysis:
- 1-in-5 AI code snippets contain fake library references (slopsquatting)
- 45% security failure rate across 80 tasks + 100 models (Veracode 2025)
- 68% of AI code uses deprecated libraries; 31% have unpatched CVEs
- 43.5% task requirement conflicts; 31.9% factual knowledge gaps
- **Source**: [CSET Georgetown](https://cset.georgetown.edu/wp-content/uploads/CSET-Cybersecurity-Risks-of-AI-Generated-Code.pdf), [Veracode 2025](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)

### 5. Multi-Step Reasoning Degradation (HIGH confidence)
- 2-step reasoning: ~95% accuracy
- 4-step reasoning: ~80% accuracy
- 6+ step reasoning: ~50% accuracy
- Each step introduces ~10-15% error compounding
- **Mitigation**: Checkpointing, critic validation at each step, tree-of-thought

---

## Practical Mitigations for Our Skill

### Against FM-2.6 (Reasoning-Action Mismatch — 13.2%)
1. **Explicit interface contracts** between all subtasks
2. **Output schema validation** — verify JSON/code structure matches contract
3. **Boundary conditions** in every prompt — "Do NOT implement X"

### Against FM-2.2 (Wrong Assumptions — 6.80%)
1. Include **all dependency outputs verbatim** in downstream prompts
2. Never summarize — pass full context (use prompt caching to manage cost)
3. Each agent prompt states assumptions explicitly

### Against FC3 (Verification Gaps — 21.30%)
1. **Always** include independent Opus verification step
2. Verification uses different prompt than generation (prevent self-enhancement bias)
3. Binary PASS/FAIL verdict more stable than numeric scales

### Circuit Breaker Pattern (from research-analyst skill)
```python
class CircuitBreaker:
    CLOSED = "closed"     # Normal operation
    OPEN = "open"         # Requests blocked (fast-fail)
    HALF_OPEN = "half_open"  # Testing recovery

    def __init__(self, failure_threshold=5, timeout=120):
        self.state = self.CLOSED
        self.failure_count = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = self.OPEN
            self.last_failure_time = time.time()

    def can_execute(self) -> bool:
        if self.state == self.CLOSED:
            return True
        if self.state == self.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = self.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN: allow test traffic
```

### Knowledge Consistency Checking
- Cross-validate outputs from parallel agents for contradictions
- Confidence scoring: source_credibility * 0.3 + agreement_count * 0.4 + consistency * 0.3
- If confidence < 0.6, escalate for human review

---

## Source Registry
1. [MAST Paper arXiv:2503.13657](https://arxiv.org/abs/2503.13657)
2. [MAST GitHub](https://github.com/multi-agent-systems-failure-taxonomy/MAST)
3. [MAST NeurIPS 2025](https://openreview.net/forum?id=fAjbYBmonr)
4. [UC Berkeley Sky Lab MAST](https://sky.cs.berkeley.edu/project/mast/)
5. [MarkTechPost Analysis](https://www.marktechpost.com/2025/03/25/understanding-and-mitigating-failure-modes-in-llm-based-multi-agent-systems/)
6. [orq.ai Blog](https://orq.ai/blog/why-do-multi-agent-llm-systems-fail)
7. [Veracode 2025](https://www.veracode.com/resources/analyst-reports/2025-genai-code-security-report/)
8. [CSET Georgetown](https://cset.georgetown.edu/wp-content/uploads/CSET-Cybersecurity-Risks-of-AI-Generated-Code.pdf)
9. [ACM LLM Hallucinations](https://arxiv.org/html/2409.20550v1)
10. [Composable Contracts](https://openreview.net/forum?id=hq0lZ9u68G)
