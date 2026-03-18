# Prompting Guide for Code Analysis and Documentation

## How to Prompt for Architecture Explanation

### Anti-Pattern: Vague Architecture Requests

**WRONG:**
```
"Explain the architecture"
(Produces rambling, unfocused response)
```

**RIGHT:**
```
"Explain the order processing architecture in 3 paragraphs:
1. High-level flow (customer to delivery)
2. Key components and their responsibilities
3. Failure modes (what can go wrong)

Focus on: async vs sync decisions, why payments aren't batched

Code to analyze: src/orders/, src/payments/"
```

### Structured Architecture Prompts

#### Pattern 1: Understand System Boundaries

```
Analyze src/orders/:

1. What are the input boundaries? (What comes IN to this system?)
2. What are the output boundaries? (What goes OUT of this system?)
3. What internal systems does it depend on? (List with file paths)
4. What external systems does it depend on? (APIs, databases, etc.)
5. Draw this as a box diagram with arrows

Evidence should come from:
- Imports: grep "^from\|^import"
- Function signatures: grep "def " for I/O
- Integration points: grep "requests\|database\|queue"
```

#### Pattern 2: Extract Decision Rationale

```
For the cache invalidation strategy in src/cache/:

1. What choice was made? (specific implementation)
2. Why was it chosen? (from git history, comments, tests)
3. What alternatives exist? (other approaches)
4. What tradeoffs does it make? (speed vs consistency)
5. When would it fail? (edge cases)

Look for evidence in:
- Commit messages: git log -S "cache" --format="%s"
- Comments: grep -r "TODO\|HACK\|cache"
- Tests: grep -r "test.*cache" tests/
- Code patterns: Show how cache is used in 3 places
```

#### Pattern 3: Trace a Feature End-to-End

```
Trace order creation from API to database:

1. Entry point: Which endpoint?
2. Validation: What's checked?
3. Business logic: What calculations happen?
4. Persistence: What's stored where?
5. Side effects: What else happens? (notifications, analytics)
6. Error cases: What can go wrong at each step?

Show code snippets for each step.
Show a sequence diagram.
```

---

## How to Prompt for Code Intent Extraction

### Intent vs. Implementation

**WRONG interpretation:**
```
"This function does string parsing"
(Describes HOW, not WHY)
```

**RIGHT interpretation:**
```
"This function validates email addresses by checking
for @ symbol and domain. It's intentionally simple
(no regex) to avoid ReDoS attacks. See comment referencing CVE-2024-xxx."
(Describes WHY + HOW + CONSTRAINTS)
```

### Prompts for Extracting Intent

#### Pattern 1: Function Purpose Extraction

```
For each function in src/orders/service.py:

Show:
1. Function name and signature
2. Intent in 1 sentence (what's the business purpose?)
3. Key decision (why implemented this way?)
4. Known limitation (what it doesn't do)
5. Who calls this? (grep for callers)
6. What does it depend on? (internal and external)

Format as a table.
```

#### Pattern 2: Design Decision Extraction

```
What are the top 5 architectural decisions in this codebase?

For each:
1. What was decided?
2. When was it decided? (commit date from git log)
3. Who decided? (commit author)
4. Why? (look for PR description, commit message, comments)
5. Tradeoffs (what's the cost?)
6. Is it still being followed? (recent code matches decision)

Sort by recency and impact.
```

#### Pattern 3: Constraint Discovery

```
What constraints define this system's design?

Look for:
1. Performance constraints (max latency, throughput)
   - Evidence: Comments, config values, tests
2. Operational constraints (deployment, scaling)
   - Evidence: Infrastructure code, monitoring
3. Security constraints (encryption, auth)
   - Evidence: Security reviews, config, tests
4. Business constraints (cost, features, timeline)
   - Evidence: TODO comments, PR descriptions, config

For each constraint: where did it come from? Is it documented?
```

---

## Sub-Agent Prompt Templates

(For use when directing Claude Code Agent tool)

### Template 1: Documentation Generation

```
You are documenting codebase: [REPO_PATH]

Phase 1: Analyze Architecture
1. Use code-patterns.md to identify patterns
2. Use language-patterns.md to understand language idioms
3. Extract 5-10 core architectural decisions
4. Document how code realizes each pattern

Phase 2: Analyze APIs
1. Find all public entry points (@route, @app, def handlers)
2. For each: document inputs, outputs, errors, business purpose
3. Cross-reference with tests to verify behavior
4. Mark undocumented APIs

Phase 3: Generate Output
1. Use output-formats.md to structure markdown
2. Include YAML frontmatter with metadata
3. Add evidence citations (file:line references)
4. Calculate handoff readiness score

Deliverable: Complete architecture.md with 95%+ API coverage
```

### Template 2: Code Pattern Recognition

```
Analyze [CODEBASE_PATH] for design patterns.

Step 1: Architectural Patterns
Use code-patterns.md to detect:
- MVC, microservices, event-driven, CQRS, hexagonal, clean architecture
- Confidence scoring: (Code evidence) + (Test evidence) + (Git evidence)

Step 2: Anti-Patterns
Identify god objects, circular dependencies, deep coupling, missing abstractions
For each: severity, location, remediation steps

Step 3: Language-Specific Idioms
Use language-patterns.md for [LANGUAGE]
Report: modernness, maturity, adherence to idioms

Step 4: Contrarian Analysis
For each pattern: document "why this might be wrong" and "better alternative"

Deliverable: pattern-analysis.md with confidence scores
```

### Template 3: Error Handling Audit

```
Audit error handling completeness.

Step 1: Extract All Errors
Find: raise, throw, HTTPException, custom exceptions
Categorize: validation, not-found, permission, timeout, internal

Step 2: Verify Documentation
For each error type:
- Is it documented (when, why)?
- Is there a test triggering it?
- Is recovery strategy documented?

Step 3: Find Gaps
Errors thrown but not documented
Documented errors with no code

Step 4: Cross-Reference
Grep documentation for error codes
Verify they match code exactly

Deliverable: errors-audit.md with coverage report
```

### Template 4: Test Coverage Analysis

```
Analyze test coverage and quality.

Step 1: Coverage Metrics
- Total test files and test count
- Lines covered by tests
- API endpoints with tests
- Error scenarios tested

Step 2: Test Quality
For each test file:
- Is it testing behavior or implementation?
- Does it use mocks appropriately?
- Are edge cases covered?

Step 3: Gaps
- Critical code paths without tests
- Error cases not tested
- Performance not benchmarked

Step 4: Testing Recommendations
- Where to add tests for highest impact
- How to improve test isolation
- Mocking/stubbing improvements

Deliverable: testing-report.md with priorities
```

---

## Unbiased Prompting: Avoiding Anchoring Bias

### The Problem: Anchoring Bias

When you suggest an interpretation, the AI anchors on it, even if wrong.

**WRONG (anchored):**
```
"This service probably uses caching. Does it?"
(AI is biased toward confirming caching)
```

**RIGHT (unanchored):**
```
"What mechanisms optimize performance in this service?
List all performance optimizations found in code."
(AI searches without preconception)
```

### Unbiased Prompt Patterns

#### Pattern 1: Open Discovery

**DON'T SAY:**
```
"Does this use a repository pattern?"
```

**DO SAY:**
```
"What abstraction patterns are used for data access?
List each pattern found with code evidence."
```

#### Pattern 2: Contradiction Seeking

**DON'T SAY:**
```
"This service is microservices-based, right?"
```

**DO SAY:**
```
"List evidence for and against this being a microservices architecture.
What would contradict each argument?"
```

#### Pattern 3: Alternative Hypothesis

**DON'T SAY:**
```
"Explain why they chose async processing"
```

**DO SAY:**
```
"What approaches to long-running tasks could work here?
Why was the chosen approach selected vs. alternatives?
What evidence indicates it was a deliberate choice vs. accidental?"
```

#### Pattern 4: Assumption Exposure

**DON'T SAY:**
```
"This is clearly using dependency injection"
```

**DO SAY:**
```
"What are the dependency resolution patterns in this codebase?
Assume nothing; show code evidence for each mechanism."
```

---

## Competing Hypotheses Prompts

Use when architecture is ambiguous or contradictory.

### Template: Multiple Competing Hypotheses

```
This codebase might follow different architectural styles.
Evaluate each hypothesis:

HYPOTHESIS A: "This is event-driven architecture"
Evidence FOR:
- [Find evidence: pub/sub, message brokers, async patterns]

Evidence AGAINST:
- [Find contradictions: synchronous calls, direct dependencies]

Confidence: [40-60%]

---

HYPOTHESIS B: "This is layered monolithic architecture"
Evidence FOR:
- [Find evidence: layer structure, vertical slicing]

Evidence AGAINST:
- [Find contradictions: service separation, microservices]

Confidence: [30-40%]

---

HYPOTHESIS C: "This is hybrid (layered + async components)"
Evidence FOR:
- [Find evidence: both layered and async]

Evidence AGAINST:
- [Find contradictions: inconsistent patterns]

Confidence: [30-40%]

---

Most likely: HYPOTHESIS A or C
Recommendation: [What makes this clear/unclear? What's needed?]
```

### When to Use Competing Hypotheses

- Architecture seems contradictory
- Code structure doesn't match documentation
- Multiple patterns visible but unclear which is primary
- System evolved and mixed patterns
- Need to understand architectural rationale

---

## Prompts for Different Expertise Levels

### For New Engineers

```
Document this system for a new engineer with [X] years experience.

Include:
1. Quick start: 5-minute orientation (what to run, what to read first)
2. Key concepts: 3-5 core abstractions explained
3. Common tasks: "How do I X?" (add endpoint, deploy, debug)
4. Architecture diagram (simplified, not complete)
5. Where to find answers: File organization, test examples, related docs

Avoid: Historical context, deprecated approaches, "clever" optimizations
Target reading time: 30 minutes
```

### For DevOps/SRE

```
Document operational aspects for DevOps engineer.

Include:
1. Deployment process: Build, test, deploy pipeline
2. Configuration: Environment variables, secrets, settings
3. Monitoring: Key metrics, dashboards, alerts
4. Troubleshooting: Common issues and resolution
5. Runbooks: Emergency procedures, rollback, escalation
6. Performance: Capacity, scaling, bottlenecks
7. Dependencies: External services, databases, queues

Avoid: Implementation details, design patterns
Target: Runnable/operational readiness
```

### For Security Auditor

```
Document security aspects for audit.

Include:
1. Authentication: Mechanism, implementation, testing
2. Authorization: Access control, privilege levels, validation
3. Data protection: Encryption (transit, at-rest), PII handling
4. Input validation: How inputs are sanitized
5. Error handling: No information leakage, logging
6. Dependencies: Vulnerability scanning results
7. Compliance: Standards addressed (OWASP, GDPR, etc.)
8. Audit trail: What's logged, retention

For each: evidence, test coverage, gaps
```

---

## Handling Incomplete or Contradictory Code

### Prompt for Unclear Architecture

```
The architecture in this code is unclear/contradictory.

For each section:
1. What's the apparent intent? (best guess from structure)
2. What contradicts it? (evidence against)
3. How could we clarify? (what's missing?)
4. Most likely explanation? (most probable intent)
5. Risk if wrong? (what breaks if misunderstood?)

Confidence level: [Low/Moderate/High]

Recommendation: Add comments/documentation here, or refactor for clarity
```

### Prompt for Dead Code

```
Identify dead code (code that's not called).

For each piece of dead code:
1. What does it do?
2. Why might it exist? (legacy, experiment, work-in-progress)
3. When was it last modified? (git blame)
4. Is it safe to remove? (any external dependencies)
5. Should we keep it? (future feature? example?)

Generate: dead-code-audit.md with recommendations
```

---

## Quality Assurance for Generated Documentation

### Prompt to Verify Documentation Quality

```
Verify this documentation against the code.

For each claim in documentation:
1. Find code evidence (file:line)
2. Find test evidence (test name)
3. Find git evidence (commit hash)
4. Identify contradictions
5. Assess confidence level

Report:
- Claims verified: ___
- Claims unverified: ___
- Claims contradicted: ___
- Average confidence: ___

For unverified claims: either remove or mark as "assumed"
For contradicted claims: update to match code
```

---

## Summary: Prompting Best Practices

- **Be specific:** "Analyze X" beats "explain the code"
- **Ask for structure:** "Create a table of..." produces better organization
- **Avoid anchoring:** Don't suggest answers, ask to discover
- **Request evidence:** "Show code references for each claim"
- **Expect iteration:** First pass is draft, refine with follow-ups
- **Use templates:** Structure prompts consistently
- **Verify outputs:** Spot-check against code before using
