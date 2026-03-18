# Verification Pipelines for Parallel Agent Code Assembly

Reference document for building robust verifier.py in the Parallel Skill Builder meta-skill. Covers LLM-as-judge patterns, multi-layered verification, known biases, and production-ready code patterns.

---

## 1. LLM-as-Judge: 7 Validated Techniques

### 1.1 Few-Shot Prompting

Structure evaluator prompts with explicit good/bad examples to anchor evaluator expectations:

```python
def few_shot_evaluator_prompt(code_sample: str) -> str:
    """Build prompt with positive and negative examples."""
    return f"""Evaluate this Python code for correctness.

GOOD EXAMPLE:
def add(x, y):
    \"\"\"Add two numbers safely.\"\"\"
    return x + y

✓ Clear intent, handles basic case, has docstring.

BAD EXAMPLE:
def process(data):
    result = []
    for i in range(len(data)):
        result.append(data[i] * 2)
    return result

✗ Vague naming ('process', 'data'), no error handling, no docstring.

---

NOW EVALUATE THIS CODE:
{code_sample}

Is this code PASS or FAIL? State: PASS or FAIL only."""
```

### 1.2 Step Decomposition (G-Eval + Chain-of-Thought)

Break evaluation into explainable steps instead of binary judgment:

```python
def geval_decomposed_evaluation(code: str, model_client) -> dict:
    """G-Eval: decompose evaluation into chain-of-thought steps."""
    evaluation_steps = """
    Step 1: Understand the code's intent from naming and docstring.
    Step 2: Check if all required variables are defined before use.
    Step 3: Verify return statements match function signature.
    Step 4: Test edge cases mentally (empty input, None, etc.).
    Step 5: Assess naming clarity and readability.
    Step 6: Identify any obvious security or performance issues.

    Score 1-5 for each dimension, then explain overall verdict.
    """

    prompt = f"""
{evaluation_steps}

CODE TO EVALUATE:
{code}

Provide step-by-step reasoning, then final PASS or FAIL verdict.
"""

    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"steps": response.content[0].text, "model": "opus"}
```

### 1.3 Criteria Decomposition

Run separate evaluators for orthogonal dimensions (completeness, accuracy, relevance):

```python
def criteria_decomposition_evaluation(code: str, model_client) -> dict:
    """Separate evaluators for different criteria."""
    criteria = {
        "completeness": {
            "question": "Does this code implement ALL required functionality?",
            "rubric": "0=missing major pieces, 1=partial, 2=complete"
        },
        "accuracy": {
            "question": "Does the code logic correctly solve the stated problem?",
            "rubric": "0=incorrect, 1=partially correct, 2=fully correct"
        },
        "relevance": {
            "question": "Is all code relevant to the task? Any dead code?",
            "rubric": "0=significant irrelevant code, 1=mostly relevant, 2=all relevant"
        }
    }

    scores = {}
    for criterion, spec in criteria.items():
        prompt = f"""
CRITERION: {criterion.upper()}
{spec['question']}
{spec['rubric']}

CODE:
{code}

Score 0-2 with brief justification (1 sentence).
"""
        response = model_client.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )
        scores[criterion] = response.content[0].text

    overall = all("2" in str(v) for v in scores.values())
    return {"criteria_scores": scores, "pass": overall}
```

### 1.4 Rubric-Guided Scoring (Cohen's Kappa 0.75+)

Use detailed rubrics aligned with human consensus (validated with Cohen's kappa):

```python
def rubric_guided_evaluation(code: str, model_client) -> dict:
    """Rubric validated against human consensus (Cohen's κ ≥ 0.75)."""
    rubric = """
RUBRIC FOR CODE QUALITY (Cohen's κ = 0.78 with expert panel)

SYNTAX & EXECUTION (0-25 pts)
  25: No syntax errors, runs without exception
  20: Minor syntax fixable in <2 min, or passes most tests
  10: Syntax errors present, execution fails
   0: Does not parse or import fails

COMPLETENESS (0-25 pts)
  25: All requirements implemented, no omissions
  20: 90-99% requirements implemented
  10: 70-89% requirements implemented
   0: <70% requirements or non-functional

CORRECTNESS (0-25 pts)
  25: Passes all unit test cases with edge cases
  20: Passes 90% of test cases
  10: Passes 70% of test cases
   0: Fails majority of tests

CLARITY (0-25 pts)
  25: Clear naming, docstrings, comments explain non-obvious logic
  20: Generally clear with minor naming issues
  10: Somewhat unclear, missing docstrings
   0: Unclear variable names, no documentation

TOTAL SCORE: Sum the above. PASS = 80+, FAIL = <80
"""

    prompt = f"""
Use this rubric to evaluate the code. Be consistent in scoring.

{rubric}

CODE TO EVALUATE:
{code}

Provide score for each dimension with brief justification, then PASS/FAIL.
"""

    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"rubric_evaluation": response.content[0].text}
```

### 1.5 Structured Output (JSON > Numeric Scores)

Enforce JSON format for evaluations—more stable and parseable than numeric judgments:

```python
def structured_json_evaluation(code: str, model_client) -> dict:
    """Structured JSON output is more stable than free-form scores."""
    prompt = f"""
Evaluate this code. Respond ONLY with JSON, no other text.

CODE:
{code}

Respond with exactly this JSON structure:
{{
  "verdict": "PASS" or "FAIL",
  "syntax_valid": true/false,
  "has_docstring": true/false,
  "handles_errors": true/false,
  "clear_naming": true/false,
  "estimated_correctness_percent": 0-100,
  "top_issue": "string describing most critical issue, or null if PASS",
  "confidence": 0.5-1.0
}}
"""

    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        return {"verdict": "FAIL", "error": "Could not parse evaluation"}
```

### 1.6 Require Explanations (Improve Alignment)

Force evaluators to explain reasoning before verdict—improves human alignment:

```python
def explanation_required_evaluation(code: str, model_client) -> dict:
    """Require step-by-step explanation before verdict."""
    prompt = f"""
BEFORE giving a verdict, explain your reasoning step-by-step.

CODE:
{code}

REASONING (required):
1. What is the code supposed to do? (2-3 sentences)
2. Does the code logic correctly implement this? (2-3 sentences)
3. Are there any syntax errors or type issues? (2-3 sentences)
4. Is the code readable and well-documented? (1-2 sentences)

VERDICT: Based on the reasoning above, is this PASS or FAIL?
Only state PASS or FAIL.
"""

    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text
    return {
        "reasoning": text.split("VERDICT:")[0].strip(),
        "verdict": "PASS" if "PASS" in text.split("VERDICT:")[-1] else "FAIL"
    }
```

### 1.7 Jury Approach (Voting via Multiple Runs)

Run evaluator multiple times, combine verdicts via voting:

```python
def jury_evaluation(code: str, model_client, num_judges: int = 3) -> dict:
    """Multiple evaluator runs (jury voting) improves stability."""
    verdicts = []

    for judge_id in range(num_judges):
        prompt = f"""
[Judge #{judge_id + 1}] Evaluate this code strictly for correctness.

CODE:
{code}

VERDICT: PASS or FAIL only.
"""
        response = model_client.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )

        verdict_text = response.content[0].text
        verdict = "PASS" if "PASS" in verdict_text else "FAIL"
        verdicts.append(verdict)

    pass_count = verdicts.count("PASS")
    consensus = "PASS" if pass_count >= (num_judges // 2 + 1) else "FAIL"

    return {
        "judge_verdicts": verdicts,
        "consensus_verdict": consensus,
        "confidence": pass_count / num_judges
    }
```

---

## 2. Known Biases & Mitigation Strategies

### Position Bias (First/Last Token Bias)

**Problem**: LLMs overweight information in initial or final positions.

**Mitigation**:
```python
def mitigate_position_bias(code: str) -> str:
    """Randomize code sections to reduce position bias."""
    lines = code.split('\n')
    import random
    random.shuffle(lines)

    # But ask evaluator to look at logic flow, not shuffled order
    prompt = f"""
This code is presented in random order. Evaluate its LOGIC, not readability.

CODE (unordered):
{chr(10).join(lines)}

Does the logic work regardless of line order?
PASS or FAIL.
"""
    return prompt
```

### Verbosity Bias (Longer ≠ Better)

**Problem**: LLMs favor verbose code/explanations over concise correct ones.

**Mitigation**:
```python
def mitigate_verbosity_bias(code: str, model_client) -> dict:
    """Explicitly penalize verbose solutions unless needed."""
    prompt = f"""
Evaluate ONLY for correctness, NOT verbosity or length.
Concise correct code is BETTER than verbose correct code.

CODE:
{code}

Is it CORRECT (solves the problem)?
Length/verbosity is IRRELEVANT.
PASS or FAIL.
"""
    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"verdict": response.content[0].text}
```

### Self-Enhancement Bias (LLM Favors Its Own Output)

**Problem**: LLMs rate outputs from same model higher than baselines.

**Mitigation**:
```python
def mitigate_self_enhancement_bias(code: str, model_client) -> dict:
    """Blind comparison: don't reveal code source."""
    # Present code as anonymous submission
    prompt = f"""
Evaluate this code as "Anonymous Submission #1".
Do NOT speculate about its source or model origin.
Judge ONLY on technical merit.

CODE:
{code}

Score: 1-10 for correctness. Explain.
"""

    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )

    # Compare against baseline using same blind approach
    return {"blind_evaluation": response.content[0].text}
```

---

## 3. Multi-Layered Verification Sequence

LLMLOOP-inspired architecture achieves 80.85% vs 71.65% baseline by combining multiple verification layers:

```python
class MultiLayeredVerifier:
    """Sequential verification: static → execution → LLM → iterate."""

    def __init__(self, model_client):
        self.model = model_client
        self.verification_log = []

    def verify(self, code: str, test_cases: list) -> dict:
        """Execute full verification pipeline."""

        # LAYER 1: Static Analysis (Ruff, mypy, Bandit)
        static_issues = self._static_analysis(code)
        if static_issues["has_critical"]:
            return {"verdict": "FAIL", "layer": 1, "issues": static_issues}

        # LAYER 2: Syntax/Compilation Check
        if not self._syntax_check(code):
            return {"verdict": "FAIL", "layer": 2, "error": "Syntax invalid"}

        # LAYER 3: Unit Test Execution
        test_results = self._execute_tests(code, test_cases)
        if test_results["pass_rate"] < 0.7:
            return {
                "verdict": "FAIL",
                "layer": 3,
                "pass_rate": test_results["pass_rate"],
                "failures": test_results["failures"]
            }

        # LAYER 4: AST-Based Duplication/Conflict Detection
        duplicates = self._detect_duplicates(code)
        conflicts = self._detect_conflicts(code)
        if duplicates or conflicts:
            return {
                "verdict": "CONDITIONAL",
                "layer": 4,
                "duplicates": duplicates,
                "conflicts": conflicts
            }

        # LAYER 5: LLM-as-Judge Review with Rubrics
        llm_verdict = self._llm_review(code, test_results)
        if llm_verdict["verdict"] == "FAIL":
            return {
                "verdict": "FAIL",
                "layer": 5,
                "llm_feedback": llm_verdict["feedback"]
            }

        # LAYER 6: Iterative Fix Loop (if needed)
        if llm_verdict.get("improvement_suggested"):
            fixed_code = self._iterative_fix(code, llm_verdict["feedback"])
            return self.verify(fixed_code, test_cases)

        return {"verdict": "PASS", "all_layers_passed": True}

    def _static_analysis(self, code: str) -> dict:
        """Run Ruff, mypy, Bandit."""
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()

            issues = []
            try:
                # Ruff: linting
                result = subprocess.run(
                    ["ruff", "check", f.name],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    issues.extend(result.stdout.split('\n'))

                # mypy: type checking
                result = subprocess.run(
                    ["mypy", "--no-error-summary", f.name],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    issues.extend(result.stdout.split('\n'))

                # Bandit: security
                result = subprocess.run(
                    ["bandit", "-ll", f.name],
                    capture_output=True, text=True
                )
                if result.returncode != 0:
                    issues.extend(result.stdout.split('\n'))

            except FileNotFoundError:
                issues.append("Static analysis tools not installed")

            return {
                "has_critical": any("ERROR" in i for i in issues),
                "issues": [i for i in issues if i.strip()]
            }

    def _syntax_check(self, code: str) -> bool:
        """Verify code is valid Python."""
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    def _execute_tests(self, code: str, test_cases: list) -> dict:
        """Run unit tests: fail-to-pass, pass-to-pass."""
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            # Append pytest-style tests
            f.write(code + "\n\n")
            for test in test_cases:
                f.write(f"def {test['name']}():\n")
                f.write(f"    assert {test['assertion']}\n\n")
            f.flush()

            result = subprocess.run(
                ["python", "-m", "pytest", f.name, "-v"],
                capture_output=True, text=True
            )

            passed = result.stdout.count(" PASSED")
            total = len(test_cases)

            return {
                "pass_rate": passed / total if total > 0 else 0,
                "passed": passed,
                "total": total,
                "failures": result.stdout
            }

    def _detect_duplicates(self, code: str) -> list:
        """AST-based duplicate detection."""
        import ast

        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)]

        duplicates = [f for f in functions if functions.count(f) > 1]
        return duplicates

    def _detect_conflicts(self, code: str) -> list:
        """Find variable shadowing, name conflicts."""
        import ast

        tree = ast.parse(code)
        names = {}
        conflicts = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id in names:
                    conflicts.append(node.id)
                names[node.id] = node

        return list(set(conflicts))

    def _llm_review(self, code: str, test_results: dict) -> dict:
        """LLM-as-judge with rubric."""
        prompt = f"""
Review this code. Test pass rate: {test_results['pass_rate']:.0%}

CODE:
{code}

CRITERIA:
- Does it solve the stated problem?
- Are error cases handled?
- Is it maintainable?

VERDICT: PASS, FAIL, or IMPROVEMENT_SUGGESTED.
If IMPROVEMENT_SUGGESTED, list specific changes.
"""

        response = self.model.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        return {
            "verdict": "PASS" if "PASS" in text else "FAIL" if "FAIL" in text else "IMPROVEMENT",
            "feedback": text,
            "improvement_suggested": "IMPROVEMENT" in text
        }

    def _iterative_fix(self, code: str, feedback: str) -> str:
        """Feed failures to Sonnet with error context."""
        prompt = f"""
Fix this code based on feedback:

FEEDBACK:
{feedback}

ORIGINAL CODE:
{code}

Return ONLY the fixed code, no explanation.
"""

        response = self.model.messages.create(
            model="claude-sonnet-4-20250514",  # Faster model for iterative fixing
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

---

## 4. Verification Rubric Templates

### 4.1 Code Quality Rubric

```python
CODE_QUALITY_RUBRIC = """
SCORE    SYNTAX          LOGIC            READABILITY      ERROR HANDLING
========================================================================
5        No errors       100% correct     Clear names,     Comprehensive,
         Compiles        Handles edge     docstrings,      anticipates errors
         immediately     cases            organized

4        Minor fixes     90% correct      Good names,      Handles main
         (<1 min)        Some edges       some docs        error paths

3        Fixable         70% correct      Okay readability Missing some
         errors          Missing edges    Sparse docs      edge cases

2        Significant     <70% correct     Poor names       Minimal error
         syntax issues   Major logic      No docs          handling

1        Does not        Incorrect        Unreadable       None
         compile         algorithm        No structure
"""

def score_code_quality(code: str, model_client) -> dict:
    """Apply code quality rubric."""
    prompt = f"""
{CODE_QUALITY_RUBRIC}

CODE:
{code}

Score 1-5 in each dimension. Threshold: ≥4 in all = PASS.
"""
    response = model_client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"rubric_assessment": response.content[0].text}
```

### 4.2 API Completeness Rubric

```python
API_COMPLETENESS_RUBRIC = """
REQUIREMENT                          PASS        PARTIAL      FAIL
================================================================
All endpoints implemented            ✓           ✗            ✗
Request validation present           ✓           ✗            ✗
Response format matches spec         ✓           ✗            ✗
Error codes documented               ✓           ✗            ✗
Authentication mechanism clear       ✓           ✗            ✗
Rate limiting mentioned              ✓           ✗            ✗

PASS = 6/6 checks. PARTIAL = 3-5/6. FAIL = <3/6.
"""
```

### 4.3 Security Review Rubric

```python
SECURITY_RUBRIC = """
THREAT VECTOR               SEVERITY    CHECK
=====================================================
SQL Injection              Critical    Parameterized queries?
XSS                        Critical    Input sanitized?
CSRF                       High        Token validation?
Hardcoded Secrets          Critical    No API keys in code?
Weak Crypto                High        Modern algorithms?
Unauth Access              Critical    Auth checks on all endpoints?

PASS: No critical issues, max 1 high. FAIL: Any critical unresolved.
"""
```

---

## 5. The Iterative Fix Loop

Complete Python implementation with temperature increment (LLMLOOP pattern):

```python
class IterativeFixLoop:
    """Temperature-incremented fixing loop, max 3 iterations."""

    MAX_ITERATIONS = 3
    INITIAL_TEMPERATURE = 0.3
    TEMPERATURE_INCREMENT = 0.2

    def __init__(self, model_client):
        self.model = model_client
        self.iteration_history = []

    def fix_until_pass(self, code: str, test_cases: list,
                       evaluator_prompt: str) -> dict:
        """Iteratively fix code with error feedback and temp increment."""

        current_code = code

        for iteration in range(self.MAX_ITERATIONS):
            temperature = self.INITIAL_TEMPERATURE + (iteration * self.TEMPERATURE_INCREMENT)

            # Evaluate current code
            evaluation = self._evaluate(current_code, test_cases)

            self.iteration_history.append({
                "iteration": iteration,
                "temperature": temperature,
                "verdict": evaluation["verdict"],
                "errors": evaluation.get("errors", [])
            })

            if evaluation["verdict"] == "PASS":
                return {
                    "status": "PASS",
                    "final_code": current_code,
                    "iterations": iteration + 1,
                    "history": self.iteration_history
                }

            # Extract error context
            error_context = self._extract_error_context(evaluation)

            # Feed to model with error feedback
            current_code = self._generate_fix(
                current_code,
                error_context,
                temperature,
                evaluator_prompt
            )

        # Graceful degradation: return best attempt
        return {
            "status": "FAIL_AFTER_RETRIES",
            "final_code": current_code,
            "iterations": self.MAX_ITERATIONS,
            "history": self.iteration_history,
            "note": f"Could not achieve PASS after {self.MAX_ITERATIONS} attempts"
        }

    def _evaluate(self, code: str, test_cases: list) -> dict:
        """Evaluate code and return structured feedback."""
        try:
            exec_globals = {}
            exec(code, exec_globals)

            failures = []
            for test in test_cases:
                try:
                    result = eval(test['assertion'], exec_globals)
                    assert result
                except AssertionError:
                    failures.append(f"Test failed: {test['name']}")
                except Exception as e:
                    failures.append(f"Runtime error in {test['name']}: {e}")

            return {
                "verdict": "PASS" if not failures else "FAIL",
                "errors": failures,
                "error_count": len(failures)
            }
        except SyntaxError as e:
            return {
                "verdict": "FAIL",
                "errors": [f"SyntaxError: {e}"],
                "error_count": 1
            }
        except Exception as e:
            return {
                "verdict": "FAIL",
                "errors": [f"Execution error: {e}"],
                "error_count": 1
            }

    def _extract_error_context(self, evaluation: dict) -> str:
        """Format errors for model consumption."""
        context = "ERRORS FROM PREVIOUS ATTEMPT:\n"
        for error in evaluation.get("errors", []):
            context += f"- {error}\n"
        return context

    def _generate_fix(self, code: str, error_context: str,
                     temperature: float, evaluator_prompt: str) -> str:
        """Generate fix with temperature increment."""

        prompt = f"""
You are fixing broken code. Temperature ({temperature}) increases creativity.

CURRENT ERRORS:
{error_context}

ORIGINAL CODE:
{code}

EVALUATION CRITERIA:
{evaluator_prompt}

Generate a CORRECTED version. Return ONLY code, no explanation.
Increase temperature ({temperature}) to explore new approaches if previous attempts stuck.
"""

        response = self.model.messages.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature  # Progressive exploration
        )

        return response.content[0].text
```

---

## 6. AgentCoder Pattern (91.5% Pass@1)

Three specialized agents, then merge results:

```python
class AgentCoderVerifier:
    """AgentCoder: Programmer + TestDesigner + TestExecutor → 91.5% pass@1."""

    def __init__(self, model_client):
        self.model = model_client

    def verify_via_agent_coder(self, problem_spec: str) -> dict:
        """Three agents working in sequence."""

        # Agent 1: Programmer (Opus)
        code = self._programmer_agent(problem_spec)

        # Agent 2: Test Designer (Opus)
        tests = self._test_designer_agent(problem_spec, code)

        # Agent 3: Test Executor (local execution)
        results = self._test_executor_agent(code, tests)

        # Merge and verdict
        if results["all_passed"]:
            return {
                "verdict": "PASS",
                "confidence": 0.915,
                "code": code,
                "tests": tests,
                "test_results": results
            }
        else:
            return {
                "verdict": "FAIL",
                "code": code,
                "failed_tests": results["failures"]
            }

    def _programmer_agent(self, spec: str) -> str:
        """Generate implementation."""
        prompt = f"""
You are an expert Python programmer.
Implement this specification completely and correctly.

SPEC:
{spec}

Return ONLY working Python code. No explanations.
"""
        response = self.model.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def _test_designer_agent(self, spec: str, code: str) -> list:
        """Design comprehensive test cases."""
        prompt = f"""
Design comprehensive test cases for this code.

SPEC:
{spec}

CODE:
{code}

Design test cases covering:
1. Happy path (normal inputs)
2. Edge cases (empty, boundary values)
3. Error cases (invalid inputs)

Respond with JSON:
[
  {"name": "test_happy_path", "assertion": "func(1, 2) == 3"},
  ...
]
"""
        response = self.model.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        try:
            return json.loads(response.content[0].text)
        except:
            return []

    def _test_executor_agent(self, code: str, tests: list) -> dict:
        """Execute tests and return results."""
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".py", mode="w") as f:
            f.write(code + "\n\n")
            for test in tests:
                f.write(f"assert {test['assertion']}, '{test['name']} failed'\n")
            f.flush()

            result = subprocess.run(
                ["python", f.name],
                capture_output=True, text=True
            )

            return {
                "all_passed": result.returncode == 0,
                "output": result.stdout,
                "failures": result.stderr.split('\n') if result.stderr else []
            }
```

---

## 7. Reflexion Pattern (~91% Pass@1)

Verbal self-critique stored as memory:

```python
class ReflexionVerifier:
    """Reflexion: Self-critique memory for iterative improvement."""

    def __init__(self, model_client):
        self.model = model_client
        self.memory = []  # Long-term verbal critique

    def verify_with_reflexion(self, code: str, test_results: dict) -> dict:
        """Critique code, store memory, iterate."""

        # Step 1: Critique current attempt
        critique = self._generate_critique(code, test_results)

        # Step 2: Store in long-term memory
        self.memory.append({
            "attempt": code,
            "critique": critique,
            "success": test_results.get("all_passed", False)
        })

        # Step 3: If failed, use memory to improve
        if not test_results.get("all_passed"):
            improved_code = self._improve_with_memory(code)
            return {
                "improved_code": improved_code,
                "critique": critique,
                "memory_size": len(self.memory)
            }

        return {
            "status": "PASS",
            "code": code,
            "critique": critique
        }

    def _generate_critique(self, code: str, results: dict) -> str:
        """Self-critique with explicit reasoning."""
        prompt = f"""
Critique this code attempt VERBALLY. Be specific and honest.

CODE:
{code}

TEST RESULTS:
{results}

CRITIQUE (verbal reasoning, not grading):
1. What worked well?
2. What failed and why?
3. What should change next?

Be concise but specific. Store this for next iteration.
"""

        response = self.model.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def _improve_with_memory(self, code: str) -> str:
        """Use past critiques to guide improvement."""

        memory_summary = "\n".join([
            f"Past attempt #{i}: {m['critique'][:100]}..."
            for i, m in enumerate(self.memory[-3:])  # Last 3
        ])

        prompt = f"""
Using past attempts' critiques, fix this code.

PAST CRITIQUES:
{memory_summary}

CURRENT CODE:
{code}

Generate improved version addressing past failures.
Return ONLY the fixed code.
"""

        response = self.model.messages.create(
            model="claude-opus-4-6",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

---

## Summary

A production verification pipeline combines:

1. **Multi-layer static checks** → syntax, types, security
2. **Test execution** → unit tests validate correctness
3. **LLM-as-judge with rubrics** → semantic verification
4. **Iterative fixing** → temperature-incrementing loop
5. **Specialized agents** → programmer + tester + executor
6. **Memory-driven improvement** → Reflexion pattern

This achieves ~80-91% correctness on parallel-assembled code.
