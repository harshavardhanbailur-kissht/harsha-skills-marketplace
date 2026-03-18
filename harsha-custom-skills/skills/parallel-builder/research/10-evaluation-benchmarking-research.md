# Research 10: Agent Evaluation, Benchmarking & Quality Measurement

## Source Validation
- **Primary**: KDD 2025 Survey (Mohammadi et al.) — "Evaluation and Benchmarking of LLM Agents"
- **Industry**: Anthropic Engineering Blog — "Demystifying Evals for AI Agents"
- **Benchmarks**: SWE-bench Verified, Terminal-Bench, BrowserGym, WebArena
- **Meta-research**: "How to Correctly Report LLM-as-a-Judge Evaluations" (Nov 2025)
- **Scrutiny Level**: Maximum (KDD peer-reviewed + Anthropic engineering practice)

## Key Findings

### 1. Two-Dimensional Evaluation Taxonomy (KDD 2025)
Evaluation has two axes:
- **What to evaluate**: Behavior, capabilities, reliability, safety
- **How to evaluate**: Interaction modes, datasets, metric computation, tooling

Key insight: "Evaluating LLM agents is more complex than evaluating LLMs in isolation —
agents operate in dynamic, interactive environments where they reason, make plans,
execute tools, leverage memory, and collaborate"

### 2. Anthropic's Practical Eval Strategy (3 Dimensions)
From Descript's agent eval system:
1. **Don't break things** (safety/regression)
2. **Do what I asked** (task completion/correctness)
3. **Do it well** (quality/style)

Evolution: Manual grading → LLM graders with product-team criteria → periodic human calibration

### 3. Grader Types for Agent Evals
From Anthropic's Research system:
- **Groundedness checks**: Claims supported by sources?
- **Coverage checks**: Key facts included in answer?
- **Source quality checks**: Authoritative sources used?

For coding agents (Bolt AI pattern):
- **Static analysis grader**: Automated syntax/lint/type checking
- **Browser agent grader**: Test generated apps by interacting with them
- **LLM judge grader**: Instruction following, code style, completeness

### 4. LLM-as-a-Judge Best Practices (2025-2026)
- **Binary PASS/FAIL** more stable than numeric scores (confirmed in our research/04)
- **Rubric-guided** evaluation essential for consistency
- **MemAlign** (Feb 2026): Builds better LLM judges from human feedback with scalable memory
- **Reporting standards**: "How to Correctly Report LLM-as-a-Judge Evaluations" (Nov 2025)
  establishes methodology for reproducible judge evaluations

### 5. SWE-bench Progression (Benchmark for Code Agents)
- LLMs progressed from 40% → 80%+ in one year on SWE-bench Verified
- Agents receive GitHub issues → generate fixes → graded by test suite
- **Relevance to our skill**: Our verification pipeline should include test execution,
  not just static analysis and LLM judgment

### 6. Self-Evaluation for Skills (Our Application)
For measuring our parallel-skill-builder's output quality:

**Tier 1: Deterministic checks** (fast, cheap, always run)
- All files exist and are non-empty
- Python files pass ast.parse / py_compile
- Ruff lint passes with zero errors
- Bandit security scan passes
- Interface contracts satisfied (output matches schema)

**Tier 2: Automated functional checks** (medium cost)
- Generated tests actually pass
- API endpoints respond correctly
- Import graph is valid (no circular deps)
- Code coverage meets threshold

**Tier 3: LLM-as-judge checks** (expensive, run selectively)
- Rubric-guided quality assessment
- Cross-output coherence check
- Requirements coverage analysis
- Code style and documentation quality

### 7. Eval Pipeline for Skill Iteration
To improve our skill over time:
1. Define eval dataset: 10-20 representative feature requests
2. Run skill on each → collect outputs
3. Score with Tier 1-3 graders
4. Track metrics across skill versions
5. A/B test skill changes on eval dataset

## Applied Improvements
1. Add eval framework to skill (scripts/eval.py or templates/eval_rubric.md)
2. Enhance verifier.py with Tier 2 functional checks (test execution)
3. Add skill self-evaluation guide to SKILL.md
4. Document eval dataset creation process
5. Add metrics tracking to verification reports
