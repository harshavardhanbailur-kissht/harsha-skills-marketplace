# Verification Patterns and Debugging Agent Design

Comprehensive guide for embedding verification at design time and building debugging agents 
that catch execution drift.

## Table of Contents
1. [Core Principle](#core-principle)
2. [Verification Criteria Framework](#verification-criteria-framework)
3. [Automated vs Manual Verification](#automated-vs-manual-verification)
4. [Debugging Agent Design](#debugging-agent-design)
5. [Plan-Reality Comparison](#plan-reality-comparison)
6. [Error Taxonomy](#error-taxonomy)
7. [Task-Type Verification Checklists](#task-type-verification-checklists)
8. [Remediation Workflow](#remediation-workflow)
9. [Verification Cadence](#verification-cadence)
10. [Key Design Principles](#key-design-principles)

---

## Core Principle

**Verification must be embedded at design time, not bolted on afterward.** When a debugging agent 
compares original plans against execution, it needs:
- Machine-parseable acceptance criteria
- Explicit evaluation rubrics
- Separation between automatic checks and AI judgment

Critical finding from MIT's self-correction studies: Pure LLM self-evaluation without external 
grounding frequently fails because **verifiers repeat the same errors as executors**.

Effective debugging agents must either:
1. Use external verification sources (tests, linters, API calls)
2. Structurally isolate verification from generation (Chain-of-Verification)

---

## Verification Criteria Framework

### SMART-T Principle

Every criterion must be:
- **S**pecific
- **M**easurable
- **A**chievable
- **R**elevant
- **T**estable
- **T**inary (PASS/FAIL only)

The most important characteristic: **every criterion must resolve to PASS or FAIL with no room 
for interpretation.**

### Given/When/Then Format

The ideal structure for AI-parseable criteria (from BDD):

| Component | Purpose | Verification Role |
|-----------|---------|-------------------|
| **Given** | Pre-conditions before behavior | Check state setup |
| **When** | Action being performed | Trigger execution |
| **Then** | Expected observable outcomes | Assert results |

**Example:**
```gherkin
Given the user has valid credentials in the system
  And the API rate limit has not been exceeded
When the user submits a login request with correct password
Then the system returns a 200 status code within 500ms
  And the response includes a valid JWT token
  And the user session is recorded in the audit log
```

### Common Criteria Failures

| Failure Mode | Example | Why It Fails | Fix |
|--------------|---------|--------------|-----|
| Vague qualifiers | "fast," "user-friendly" | No measurable target | "Response time <500ms" |
| Implementation focus | "Uses React hooks" | Tests implementation not behavior | "Component re-renders on state change" |
| Missing edge cases | Only happy-path | Partial coverage | Add failure conditions |
| Compound criteria | Multiple requirements in one | Partial pass possible | One criterion per requirement |

### Two-Layer Verification

Distinguish "done" from "done correctly":

| Layer | Purpose | Scope | Example |
|-------|---------|-------|---------|
| **Definition of Done** | Process/quality standards | ALL tasks | Code reviewed, tests pass, documented |
| **Acceptance Criteria** | Functional correctness | SPECIFIC task | Login returns valid JWT within 500ms |

---

## Automated vs Manual Verification

### High-Confidence Automated Verification

| Category | What Can Be Checked | Tools/Methods |
|----------|---------------------|---------------|
| File existence | Required files, configs, docs present | Filesystem checks |
| Compilation | Build success, dependency resolution | CI/CD pipeline |
| Test execution | Unit/integration tests pass/fail | Test frameworks |
| Linting/formatting | Style rules, syntax correctness | ESLint, Prettier, etc. |
| API responses | Endpoint availability, status codes, schema | Contract testing |
| Security patterns | Hardcoded secrets, known CVE patterns | SAST tools |
| Performance metrics | Response time vs thresholds | Benchmarks |
| Type safety | Type mismatches in typed languages | Compilers |

### Judgment-Required Verification

AI can assist but not deterministically verify:

| Category | Why Automation Fails | AI Role |
|----------|---------------------|---------|
| Code quality/readability | Subjective; team context-dependent | Flag patterns, request human review |
| Design adherence | Requires understanding business goals | Compare against documented patterns |
| Algorithm appropriateness | Domain knowledge required | Identify alternatives, surface trade-offs |
| UX considerations | Human perception required | Check accessibility, flag for review |
| Performance acceptability | Context-dependent thresholds | Compare against stated requirements |
| Business logic correctness | Domain expertise needed | Trace to requirements, flag gaps |

Key insight from Microsoft Research: Code review rarely detects "deep, subtle, or macro-level 
issues"—those require judgment.

### Three-Tier Verification Approach

```
TIER 1 - AUTOMATED (High Confidence)
├── Build/compile status
├── Test results and coverage
├── Linting and formatting
├── Security scans
└── API contract validation

TIER 2 - AI-ASSISTED (Medium Confidence)  
├── Requirements traceability check
├── Pattern matching against known anti-patterns
├── Documentation completeness
└── Scope deviation detection

TIER 3 - FLAGGED FOR REVIEW (Low Confidence)
├── Architectural decisions
├── Complex business logic
├── UX and design quality
└── Performance trade-off assessment
```

---

## Debugging Agent Design

### Core Prompt Structure

```markdown
# Debugging Verification Agent

You are a verification agent comparing plan execution against original specifications. 
Your role is CRITICAL ASSESSMENT, not approval-seeking. Be skeptical by default.

## Original Plan
{original_task_definition}

## Acceptance Criteria
{acceptance_criteria_in_given_when_then_format}

## Execution Artifacts
{code_changes, logs, test_results, outputs}

## Verification Process

### Step 1: Automated Check Results
Review these deterministic checks (provided by system):
- Build status: {pass/fail}
- Test results: {summary}
- Linting: {summary}
- Coverage: {metrics}

### Step 2: Requirement-by-Requirement Verification
For EACH acceptance criterion:
1. State the criterion
2. Identify the evidence that should demonstrate it
3. Evaluate: PASS, FAIL, or CANNOT_VERIFY
4. If not PASS, explain the gap

### Step 3: Scope Analysis
- List what was specified but NOT implemented (Missing)
- List what was implemented but NOT specified (Extraneous)
- List what deviated from specification (Deviated)

### Step 4: Root Cause Analysis (for failures)
- Immediate cause: What directly caused the failure?
- Contributing factors: What conditions enabled it?
- Root cause: Why did this happen fundamentally?
- Category: [Plan_Error | Execution_Error | Environmental | Context_Loss]

## Output Format
Return structured JSON:
{
  "overall_status": "PASS" | "FAIL" | "PARTIAL",
  "confidence": 0.0-1.0,
  "criteria_results": [
    {
      "criterion": "...",
      "status": "PASS" | "FAIL" | "CANNOT_VERIFY",
      "evidence": "...",
      "gap_description": "..." // if not PASS
    }
  ],
  "scope_analysis": {
    "missing": [...],
    "extraneous": [...],
    "deviated": [...]
  },
  "errors": [
    {
      "type": "Missing|Wrong|Incomplete|Deviated|Regression",
      "severity": "Critical|High|Medium|Low",
      "description": "...",
      "root_cause": "...",
      "remediation": "Patch|Replan|Defer"
    }
  ],
  "recommendations": [...],
  "requires_human_review": [...]
}
```

### Critical Design Principles

1. **Embed evaluation criteria directly** in the prompt (Constitutional AI pattern)—
   don't ask "is this good?" but "does this meet criterion X?"

2. **Require reasoning before judgment**—asking for rationale before score improves 
   accuracy significantly

3. **Use factored verification** (Chain-of-Verification pattern)—evaluate each 
   criterion independently to prevent cascading errors

4. **Separate from executor context**—the verifier should NOT see the executor's 
   "thinking" to avoid copying the same errors

5. **Include few-shot examples** of good and bad verification decisions to calibrate

---

## Plan-Reality Comparison

### Requirements Traceability Matrix

| Requirement ID | Acceptance Criterion | Implementation Reference | Test Reference | Status | Notes |
|---------------|---------------------|-------------------------|----------------|--------|-------|
| REQ-001 | Given/When/Then | file.ts:lines | test_req001.ts | PASS | — |
| REQ-002 | Given/When/Then | — | — | MISSING | Not implemented |

### Four Deviation Types

| Deviation | Description | Detection |
|-----------|-------------|-----------|
| **Scope Reduction** | Required features not implemented | Forward traceability gaps |
| **Scope Creep** | Unrequested features added | Backward traceability orphans |
| **Specification Deviation** | Implemented differently than specified | Criterion-by-criterion comparison |
| **Quality Deviation** | Met functional requirements but poorly | Judgment-based assessment |

### Questions for Detecting "Technically Complete But Wrong"

1. Does the implementation achieve the *stated goal* or just the *literal requirements*?
2. Are there side effects not addressed in the original specification?
3. Does the approach introduce technical debt that wasn't authorized?
4. Could a simpler solution have achieved the same outcome?
5. Does the implementation align with established architectural patterns?

### Handling Execution Improvements

When execution diverges positively:
1. **Flag the deviation** (it's still a deviation from contract)
2. **Categorize as improvement** vs unauthorized change
3. **Document the rationale** if discoverable
4. **Recommend plan update** to reflect improvement for future reference

The original plan is the contract—even beneficial deviations should be tracked.

---

## Error Taxonomy

Based on Orthogonal Defect Classification (ODC) and Beizer's taxonomy:

| Error Type | Description | Example | Detection Difficulty |
|------------|-------------|---------|---------------------|
| **Missing** | Required functionality absent | Function not implemented | Low—forward traceability |
| **Incomplete** | Partial implementation | Edge cases not handled | Medium—requires thorough testing |
| **Wrong** | Incorrect implementation | Logic error, wrong algorithm | Medium—tests catch some |
| **Deviated** | Different from specification | Alternative approach taken | Medium—requires plan comparison |
| **Extraneous** | Unrequested additions | Features not in spec | Low—backward traceability |
| **Regression** | Previously working broken | Fix broke other feature | Low—regression tests |
| **Integration** | Components don't work together | API contract mismatch | Medium—integration tests |
| **Context Loss** | Correct per instructions, wrong for actual goal | Misunderstood requirement | High—requires original context |

### ODC Qualifiers

Apply to all error types:
- **Wrong**: Code exists but does wrong thing
- **Missing**: Required code/logic doesn't exist
- **Extraneous**: Unnecessary code that shouldn't exist

### Error Prioritization

| Severity | Definition | Response Time |
|----------|------------|---------------|
| **Critical (S1)** | System unusable, data loss, security breach | Same day hotfix |
| **High (S2)** | Major feature broken, no workaround | This sprint |
| **Medium (S3)** | Feature impaired, workaround exists | Next sprint |
| **Low (S4)** | Minor inconvenience, cosmetic | Backlog |

### Distinguishing Errors from Reasonable Changes

| Characteristic | Error | Reasonable Change |
|----------------|-------|-------------------|
| Intentionality | Unintended deviation | Deliberate decision |
| Documentation | Not documented | Change request exists |
| Impact assessment | Not evaluated | Trade-offs considered |
| Communication | Stakeholders unaware | Stakeholders informed |
| Value | Negative or neutral | Positive improvement |

---

## Task-Type Verification Checklists

### Code Implementation Tasks

**Automated checks:**
- [ ] Compiles without errors
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Linting passes with no new violations
- [ ] No security vulnerabilities detected
- [ ] Code coverage maintained or improved

**AI-assisted checks:**
- [ ] Each acceptance criterion has corresponding evidence
- [ ] Error handling covers specified failure modes
- [ ] API contracts match specification
- [ ] Required documentation exists

**Judgment-required:**
- [ ] Solution approach appropriate for the problem
- [ ] Code readable and maintainable
- [ ] Edge cases adequately handled
- [ ] Performance acceptable for use case

### Bug Fix Tasks

**Automated checks:**
- [ ] Regression test added (fails on old code, passes on new)
- [ ] All existing tests still pass
- [ ] No new warnings or errors introduced

**AI-assisted checks:**
- [ ] Fix addresses stated root cause, not just symptoms
- [ ] Related functionality tested
- [ ] Fix scope limited to affected area

**Judgment-required:**
- [ ] No unintended side effects
- [ ] Fix is appropriate (not a workaround)
- [ ] Similar bugs prevented by this fix

### Refactoring Tasks

**Automated checks:**
- [ ] All tests pass (behavior unchanged)
- [ ] Coverage maintained
- [ ] Performance not degraded (benchmarks)

**AI-assisted checks:**
- [ ] Changes bounded to stated scope
- [ ] No functional changes introduced

**Judgment-required:**
- [ ] Code more readable/maintainable than before
- [ ] Abstraction level appropriate
- [ ] Team would approve approach

### Documentation Tasks

**Automated checks:**
- [ ] File exists in expected location
- [ ] Markdown renders correctly
- [ ] All links valid
- [ ] Code examples compile/run

**AI-assisted checks:**
- [ ] Required sections present
- [ ] References to code accurate

**Judgment-required:**
- [ ] Content accurate and up-to-date
- [ ] Appropriate detail level for audience
- [ ] Examples helpful and relevant

---

## Remediation Workflow

### Triage Decision Tree

```
Error Detected
    │
    ├─► Is it blocking Definition of Done? ──YES──► Hotfix this sprint
    │       │
    │       NO
    │       │
    ├─► Is it on critical user path? ──YES──► Priority for next sprint
    │       │
    │       NO
    │       │
    ├─► Does workaround exist? ──YES──► Add to backlog
    │       │
    │       NO
    │       │
    └─► Assess severity/priority matrix ──► Schedule accordingly
```

### Patch vs Replan Decision

| Condition | Patch (Tactical) | Replan (Strategic) |
|-----------|------------------|-------------------|
| Issue scope | Isolated, clear root cause | Systemic, design-level |
| Fix risk | Low, doesn't affect architecture | Requires architectural change |
| Recurrence | First occurrence | Third+ time in same area |
| Technical debt | Acceptable | Unacceptable accumulation |
| Time estimate | Hours/days | Days/weeks |

### Fix Task Structure

```yaml
fix_task:
  title: "Fix: [Brief description of error]"
  type: bug_fix
  
  original_error:
    reference: error_id
    type: Missing|Wrong|Incomplete|etc
    root_cause: "..."
    
  acceptance_criteria:
    - Given the conditions that triggered the original error
      When the same action is performed
      Then the expected behavior occurs
    - Given the fix is deployed
      When regression tests run
      Then all tests pass including new regression test
      
  verification_requirements:
    - Regression test added
    - Root cause addressed (not just symptoms)
    - Related functionality verified
    
  scope_constraints:
    - Limit changes to affected module
    - No refactoring beyond fix scope
```

### Preventing Fix Cycles

1. **Write test first** for every bug—test should fail before fix, pass after
2. **Require change impact analysis** before implementing fix
3. **Run full regression suite** on every fix
4. **Code review fixes** even when they seem simple
5. **Track "fix churn"** as quality metric—repeated fixes signal need for replan
6. **Root cause analysis mandatory** for Critical/High severity

---

## Verification Cadence

### When to Verify

| Cadence | Best For | Trade-offs |
|---------|----------|------------|
| **Per-task** | High-risk, complex tasks | Maximum coverage, higher overhead |
| **Per-milestone** | Well-defined deliverables | Good balance, may accumulate issues |
| **Continuous** | CI/CD environments | Immediate feedback, requires automation |

### Recommended Hybrid Approach

```
CONTINUOUS (every commit)
├── Automated checks (build, lint, test)
├── Security scans
└── Coverage thresholds

PER-TASK (task completion)
├── Acceptance criteria verification
├── AI-assisted plan comparison
└── Scope deviation check

PER-MILESTONE (sprint/release)
├── Full Definition of Done audit
├── Integration verification
├── Accumulated technical debt review
└── Human review of flagged items
```

### Verification Timing and Context Compaction

Since context compaction is the core problem:

1. **Verify BEFORE context compaction** when possible—capture full context
2. **Embed verification results** in compacted context—future tasks see what was verified
3. **Re-verify after long gaps**—if significant time passes, context may have drifted

### Handling Dependent Tasks

1. Verify dependencies complete before starting dependent task
2. Include dependency verification status in dependent task's context
3. Re-verify integration points when dependent task completes
4. Flag if dependency was modified after dependent task started

---

## Key Design Principles

### 1. Verification Independence is Critical

Chain-of-Verification research: if verifier sees executor's reasoning, it copies errors. 
Debugging agent must be **structurally isolated** from executor context.

Should see:
- Original plan
- Acceptance criteria
- Artifacts produced

Should NOT see:
- Executor's "thinking"
- Intermediate reasoning

### 2. External Grounding Improves Verification

MIT self-correction research: LLM self-evaluation alone "does not work well" without 
external feedback sources.

Rely on:
- Actual test execution results (not self-assessment)
- Real linter output (not judgment of code style)
- API response validation (not prediction of what would return)

### 3. Context Loss is Its Own Error Category

Traditional taxonomies don't include "correct per instructions, wrong for actual goal." 
In AI orchestration, **Context Loss errors** deserve special treatment.

### 4. The Original Plan is Sacred

Even beneficial deviations should be flagged. The plan represents the contract between 
planning and execution. Consistent improvements indicate planning needs improvement.

### 5. Verification Criteria at Planning Time

Criteria written after execution get reverse-engineered from what was built rather than 
what was needed. Require Given/When/Then criteria before task execution begins.

### 6. Explicit Rubrics for Judgment

"Is this code good?" gets inconsistent answers.
"Does this code: (a) handle null inputs, (b) log errors, (c) follow naming conventions?" 
gets consistent answers.

### 7. Reflexion Pattern for Learning

Reflexion framework: verbal self-reflection stored in memory improves future performance. 
Store debugging findings and surface when similar tasks arise.

### 8. False Positives Kill Verification

A system that cries wolf gets ignored. Prioritize **precision over recall**—better to 
miss some issues than flag everything.

### 9. Structured Output for Machine Consumption

Verification results need to be **machine-parseable** (JSON/YAML), not narrative reports. 
Debugging agent output becomes input for next planning cycle.

### 10. Separate Verification from Remediation

Debugging agent should NOT attempt fixes. Its job: produce clear, prioritized list of 
findings. Separate remediation process decides what to do about findings.
