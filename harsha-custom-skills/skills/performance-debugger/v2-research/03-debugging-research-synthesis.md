# LLM-Assisted Bug Detection and Automated Program Repair: State of the Art 2025-2026

## Research Synthesis & Analysis

This document synthesizes findings from cutting-edge research in LLM-assisted bug detection, automated program repair (APR), and production debugging. The research spans academic papers, industry benchmarks, and production tools to identify patterns applicable to building advanced debugging capabilities for Claude.

---

## 1. Top Academic Papers & LLM-Assisted Program Repair (2024-2026)

### 1.1 RepairAgent: Autonomous LLM-Based Program Repair

**What It Is:**
RepairAgent represents the first autonomous, agent-based approach to software repair using LLMs, presented at ICSE 2025. Unlike earlier approaches that rely on fixed prompts to generate patches in one pass, RepairAgent treats the LLM as an autonomous agent capable of planning and executing multi-step repair strategies.

**How It Works:**
RepairAgent implements a closed-loop system where the LLM:
- Gathers information about the bug through tool invocations (reading test failures, stack traces, repository structure)
- Collects "repair ingredients" (relevant code context, documentation, related implementations)
- Generates candidate patches
- Validates patches against test suites
- Iteratively refines attempts based on test results and error messages

Rather than a single forward pass, this creates an adaptive workflow where the model learns from failure modes within the same repair task.

**Performance Results:**
- Repaired 164 bugs on the Defects4J benchmark (Java)
- Fixed 39 bugs that prior techniques could not fix, including those missed by ChatRepair
- Average token cost: 270,000 tokens per bug (~$0.14 USD per bug using GPT-3.5 pricing)
- Token efficiency improved through selective tool use and iterative refinement

**How It Applies to Claude Debugging:**
RepairAgent demonstrates that multi-step planning with feedback loops significantly outperforms single-pass generation. For Claude's debugging assistant:
- Implement tool chains for gathering debugging context rather than relying on initial code context
- Use iterative hypothesis testing: generate candidate fixes, validate against tests, analyze failures, propose refined solutions
- Leverage conversation history to track what has been attempted and why
- Value the cost of thinking (token usage) as a resource to optimize through targeted information gathering

**Limitations:**
- High token cost per bug makes it expensive for large-scale deployment
- Requires tight integration with test suites and version control systems
- Works best on Java; generalization to dynamic languages requires further research
- Success depends heavily on test quality (more on this below)

---

### 1.2 ChatRepair: Lightweight Conversational Program Repair

**What It Is:**
ChatRepair represents an alternative approach to RepairAgent, focusing on minimal prompting overhead while leveraging GPT-3.5/GPT-4's few-shot capabilities. Published at ISSTA 2024, it demonstrates that effective bug repair doesn't require token-heavy agent architectures.

**How It Works:**
ChatRepair implements a simpler iterative loop:
1. Feed the model failing test assertions and error messages
2. Generate a patch
3. Execute against full test suite
4. Feed back exact failing assertions and buggy code lines
5. Re-prompt for improved patch (up to 5 rounds)

The key insight: test failure messages are highly informative to LLMs and reduce the need for extensive context gathering.

**Performance Results:**
- Fixed 162 out of 337 bugs on Defects4J (48% success rate)
- Cost: ~$0.42 per bug (significantly cheaper than RepairAgent)
- 5-round iterative prompting often achieves better fixes than single-pass generation
- More token-efficient than RepairAgent despite lower absolute success rate

**How It Applies to Claude Debugging:**
ChatRepair validates the principle that tight feedback loops matter more than exhaustive context. For Claude:
- Prioritize test failure messages and error output in the conversation loop
- Implement 3-5 round iterative fixing within a single conversation thread
- Use conversation history efficiently—don't require large context re-uploads
- Test output should drive the next hypothesis generation, not static code context

**Limitations:**
- 48% success rate on Defects4J means it fails on more complex bugs
- Requires executable test suites in the working environment
- Test quality directly impacts fix quality (weak tests enable plausible-but-incorrect patches)
- No explicit bug localization; relies on LLM reading stack traces

---

### 1.3 SWE-Bench Leaderboard Leaders & Patterns (2025)

**Current Top Performers:**

The SWE-Bench Verified leaderboard (as of June 2025) shows:
- **Claude Opus 4.5 + Live-SWE-agent: 79.2%** resolution rate on verified benchmark
- **Gemini 3 Pro + Live-SWE-agent: 77.4%** resolution
- **iSWE-Agent (Claude 4.5 Sonnet): 33%** on Java-specific tasks (Multi-SWE-Bench)

However, **private SWE-Bench Pro results** (unseen code) show:
- Claude Opus 4.1: 17.8% (down from 22.7% on public set)
- GPT-5: 14.9% (down from 23.1% on public set)

**Critical Finding: Generalization Gap**
The 4-8 point drop from public to private benchmarks reveals that memorization and overfitting to public datasets remains a major challenge. Systems that appear "solved" on public benchmarks still struggle on truly novel codebases.

**What Makes Top Performers Successful:**

1. **Effective Code Search & Localization:** Top systems spend significant computational effort finding relevant code files before attempting repairs. Rather than fixing the first error mentioned, they search repository structure to understand architecture.

2. **Test-Driven Iteration:** Unlike early APR systems that generate single patches, top performers treat tests as a conversation partner—examining which tests fail, understanding why, and iterating.

3. **Multi-Artifact Integration:** Best systems combine multiple signal types: error messages, test failures, stack traces, repository structure, git history, and related implementations.

4. **Conversation-Based Planning:** Top-performing agents plan repairs through conversation (visible in prompts/responses) rather than black-box internal reasoning.

**How It Applies to Claude Debugging:**
The SWE-Bench leader insights reveal that raw model capability (though important) is less determinative than search strategy and iteration discipline:
- Invest in repository navigation tools for Claude (file finding, dependency graphs, search)
- Structure debugging around test-driven iteration cycles
- Combine multiple artifact types in context before generation
- Make planning visible in conversation (what are we searching for? why?)

**Limitations:**
- Generalization to private datasets remains the unsolved challenge
- Leaderboard inflation risk—systems may optimize for known test patterns
- No unified metric for code quality, test suite quality, or long-term maintainability
- SWE-Bench emphasizes GitHub issues; other bug types (security, performance) underrepresented

---

### 1.4 Recent Survey: LLM-Based APR Taxonomies & Paradigms (2025)

**Key Research Findings:**

A comprehensive 2025 survey in the IEEE Transactions on Software Engineering identified these dominant design paradigms:

1. **LLM-as-Patch-Generator:** Feed buggy code + context → generate patch (basic approach, ~30-40% success on Defects4J)

2. **LLM-as-Agent:** Integrate tools, test execution, code search → iterative repair (RepairAgent model, ~40-50% success)

3. **LLM-as-Feedback-Analyzer:** Process test failures, stack traces → guide next iteration (ChatRepair model, efficiency-focused)

4. **Hybrid Multi-Artifact Integration:** Combine program analysis, LLMs, graph-based code representations (emerging, 2025)

Most effective recent work uses Paradigm 2 (agent-based) or 4 (hybrid), showing that pure generation is insufficient.

**Critical Insight: Test Suite Quality Correlation**

Research shows that the "capable-tests ratio" (percentage of tests specifically designed to catch real bugs, not just achieve coverage) correlates more strongly with APR success than raw test coverage percentage. A small suite of targeted tests enables better repair validation than large suites with weak assertions.

This has profound implications: you cannot separate bug-fixing quality from test quality. Fixing bugs without understanding test intent produces plausible-but-wrong patches.

**Limitations of Current Taxonomies:**
- Most taxonomies focus on Java; generalization to JavaScript/TypeScript, Python unclear
- Limited treatment of cross-cutting concerns (refactoring during repair, performance impact)
- Insufficient analysis of failure modes beyond "patch doesn't pass tests"

---

## 2. Safe Automated Fixing: Preventing Regression & Introducing New Bugs

### 2.1 The Regression Testing Problem in APR

**What It Is:**
When APR systems generate patches, they face a dilemma: how do we know a patch is actually correct versus merely plausible (passes a finite test suite but introduces new bugs)?

Research on "When APR Meets Regression Testing" examined this across 2 million patches. Key finding: **every patch is a code change**, and code changes have regression risk.

**How Regression Testing Works:**

Traditional regression test selection (RTS) is "safe" if it selects *all* tests that may be affected by code changes. Method-level and statement-level RTS significantly outperform class-level approaches.

For APR specifically:
- Each candidate patch is treated as a revision
- RTS techniques select only tests likely affected by that specific patch's changes
- This reduces execution time from O(n) full test runs to O(1) or O(log n)

**Key Metrics for Safe Repairs:**

1. **Capable-Tests Ratio:** The percentage of tests specifically designed to catch real bugs (not coverage-driven). Systems with capable-tests ratio > 0.7 show 56.3% prevention of incorrect patches without blocking correct ones.

2. **Mutation Score Correlation:** Tests that survive high mutation rates (still passing with intentionally mutated code) indicate weak test assertions. This reveals which tests need strengthening.

3. **Test Coverage Depth:** Line coverage alone is insufficient. Tests must exercise the change in multiple execution contexts.

**How It Applies to Claude Debugging:**

Safe fixing requires a verification hierarchy:
1. **Immediate:** Does the patch pass all tests? (necessary but insufficient)
2. **Short-term:** Do we understand *why* the test passed? What was the root cause?
3. **Medium-term:** Are there related tests that should be checked? Dependencies that might break?
4. **Long-term:** Has similar code been changed elsewhere? Might the fix create consistency issues?

Claude should implement this hierarchy:
- First pass: run full test suite, report results
- Second pass: analyze test failure messages to understand what root cause the patch addresses
- Third pass: search for related code patterns that might be affected
- Fourth pass: perform lightweight static analysis to catch obvious new issues (unused variables introduced, type mismatches)

**Limitations:**
- RTS techniques assume tests are deterministic and reproducible; flaky tests undermine the approach
- Defining "safe" is context-dependent; some applications tolerate minor regressions more than others
- The capable-tests ratio is hard to compute automatically and requires human judgment about test intent

---

### 2.2 Production Tools & Their Verification Strategies

**Cursor's Approach:**
Cursor scans code changes against a main branch, rates potential bugs it finds, and offers one-click fixes. The verification model:
- Detects changes in branch vs main
- Applies static analysis to find likely issues in changed lines
- Generates fixes targeting those specific issues
- User reviews in editor context before committing

Strength: Fast, integrated with editor workflow
Weakness: No test execution; relies on static analysis heuristics

**GitHub Copilot Workspace (2025):**
GitHub's newer agent mode enables multi-file modifications with:
- Proposed changes to multiple files
- Running tests before opening PR
- Suggesting only fixes that pass tests

Strength: Integrated CI/CD awareness, can see test results immediately
Weakness: Works best on small, self-contained changes; struggles across large codebases

**Aider (Open Source):**
Aider provides LLM-assisted editing with explicit verification:
- Regenerate only changed lines (reduces diff size)
- User sees diffs before applying
- Can run tests and iterate within the conversation

Strength: Strong on transparency; user maintains final control
Weakness: Requires user to manually verify tests; limited automation

**Comparison:**
All three tools implement the principle: **verification is a UI concern, not just a backend concern**. The way changes are presented matters as much as whether they pass tests. Claude should follow this pattern: show changes in diffs, allow acceptance/rejection, explain the reasoning.

**Limitations:**
- None of these tools achieve >80% correct-first-time on complex changes
- All trade automation for safety—more automation = more risk of incorrect changes
- Limited ability to detect subtle bugs (performance regressions, subtle state changes)

---

### 2.3 Mutation Testing for Fix Verification (Stryker & Beyond)

**What It Is:**
Mutation testing is a quality assurance technique: introduce small intentional changes (mutations) to code, run tests, verify tests catch the changes. High mutation survival rate indicates weak tests.

Stryker (JavaScript) is the production tool for this. A 2026 report showed:
- Initial mutation score: 62%
- After identifying and strengthening tests: 88%
- This indicates tests were missing 26% of potential bugs

**How It Works for Debugging:**

When Claude proposes a fix, mutation testing answers: "If we slightly change the fix (mutation), would tests still pass?"

Example: A proposed fix changes `if (x > 5)` to `if (x >= 5)`. Mutation testing would:
1. Mutate the fixed code (e.g., `if (x > 4)`)
2. Run tests
3. If tests still pass, mutation survived—tests are weak
4. If tests fail, mutation died—tests are adequate

This is expensive (runs test suite many times) but provides high confidence in fix correctness.

**Limitations for Production Use:**
- Extremely slow: can take hours on large test suites
- Requires strong test infrastructure (deterministic, fast tests)
- Not practical for real-time debugging; useful for final verification of important fixes
- Only catches bugs tests could theoretically detect; misses categories tests don't cover

**How It Applies to Claude:**
Rather than full mutation testing, Claude could implement **lightweight mutation checks**:
- Change arithmetic operators (`+` to `-`, `*` to `/`)
- Change comparison operators (`>` to `>=`, `==` to `!=`)
- Add/remove conditionals
- Ask: "If we made this small change to my fix, would tests catch it?"

This gives confidence without the full computational cost.

---

## 3. AST-Based Bug Detection for JavaScript/TypeScript

### 3.1 Tree-Sitter: Beyond Regex-Based Linting

**What It Is:**
Tree-Sitter is a parser generator and incremental parsing library that builds concrete syntax trees (CSTs) for source files. Unlike regular expressions, tree-sitter understands language structure: scope, nesting, context.

**Why It Matters for Bug Detection:**

Regex-based approaches (traditional linting) struggle with:
- Nested patterns: finding unused variables in nested scopes
- Cross-line patterns: tracking variable definitions across blocks
- Context-dependent rules: is `eval()` dangerous here? depends on whether it's user input

Tree-Sitter handles all three through its query language, allowing pattern matching on the AST.

**Practical Bug Detection Examples:**

1. **Detect eval() usage (XSS vulnerability):**
   ```
   Tree-Sitter Query: (call_expression function: (identifier) @function)
   Check: @function == "eval"
   ```
   This catches `eval(x)` but not `Math.eval(x)` (false positive), which regex would misclassify.

2. **Detect unreachable code:**
   ```
   Pattern: code after return/throw/break in same block
   Tree-Sitter: Understand block boundaries, identify dead code
   Regex: Would fail on multi-line constructs
   ```

3. **Detect unused function parameters:**
   ```
   Tree-Sitter: Scope analysis—understand parameter scope, track all identifiers in that scope
   Regex: Cannot understand scope at all
   ```

**Accuracy Improvements:**
Research shows AST-based detection achieves:
- 70-80% precision/recall on structural patterns
- Versus 40-50% for regex-based approaches
- Reason: regex has high false positive rate; AST eliminates false positives

**How It Applies to Claude Debugging:**

Claude should implement Tree-Sitter query support for JavaScript/TypeScript:
- Before proposing a fix, query the AST for patterns related to the bug
- Example: If fixing a "null reference" bug, query for `?.` optional chaining usage, check if null checks exist
- Use AST queries to find related code patterns that might have the same bug
- Generate test cases that exercise the specific AST patterns being fixed

**Limitations:**
- Tree-Sitter is a parser, not a type checker; cannot detect type-level bugs
- False negatives: subtle bugs that don't show syntactic patterns are invisible
- Learning curve: tree-sitter queries are non-trivial to write
- Limited to publicly available language grammars

---

### 3.2 CodeQL: Semantic Program Analysis

**What It Is:**
CodeQL treats source code as queryable data. It builds a database of code facts (variables, functions, data flow) and allows SQL-like queries to find vulnerabilities.

**How It Differs from Tree-Sitter:**

Tree-Sitter focuses on syntax. CodeQL adds semantics: data flow analysis, control flow analysis, type information.

Example: "Find all places where user input reaches a dangerous function (SQL injection)."
- Tree-Sitter could find calls to `query(x)`
- CodeQL traces: where did `x` come from? Is it user-controlled? Through how many transformations?

CodeQL builds a dataflow graph: inputs → transformations → dangerous functions.

**JavaScript/TypeScript CodeQL Performance:**

On the OWASP Top 10 vulnerabilities in JavaScript:
- CodeQL detects 300 vulnerabilities (31.3% of total)
- Higher precision (7.8%) than most SAST tools
- Underperforms on:
  - Dynamic behavior (JavaScript's eval, Function constructor)
  - Prototype pollution (complex object semantics)
  - Type-polymorphic vulnerabilities (same code, different runtime types)

**Key Finding:** Even the best semantic analysis tools only detect ~31% of real vulnerabilities. This gap reveals that JavaScript's dynamic nature defeats current static analysis.

**How It Applies to Claude Debugging:**

CodeQL's limitations matter: Claude cannot rely on static analysis alone to find bugs. But CodeQL excels for:
- Finding explicit code patterns: unused imports, missing null checks, type mismatches
- Tracing data flow: following input through transformations
- Detecting architectural violations: usage of deprecated APIs

Claude should use CodeQL-like analysis as one signal among many, not as the source of truth.

**Limitations:**
- 31% recall on JavaScript vulnerabilities—fundamentally limited by language dynamics
- Requires explicit modeling of each vulnerability type (new rules needed for new bugs)
- Slow database construction; not suitable for real-time analysis
- Best for Java/C++; weaker for dynamic languages

---

### 3.3 TypeScript Strict Mode: Type-Based Bug Prevention

**What It Is:**
TypeScript's strict mode enables a comprehensive set of type checking rules. Enabling `strict: true` in tsconfig.json activates:
- `noImplicitAny`: Reject variables/parameters without type annotations
- `strictNullChecks`: Null/undefined are distinct types, require explicit checks
- `strictPropertyInitialization`: Class properties must be initialized
- `strictBindCallApply`: bind/call/apply have strict signatures

**Impact on Bug Prevention:**

With `strictNullChecks` enabled:
- Prevents ~15-20% of production bugs (null reference errors)
- Requires explicit null checks, making bugs obvious in code review
- Catches TypeScript-specific bugs (type mismatches, missing properties)

Enabling strict mode on a legacy codebase typically reveals 500-2000 type errors, depending on size. Each requires explicit handling.

**Practical Example:**

```typescript
// Weak mode
function getValue(obj: any) {
  return obj.value; // Bug: obj might be null, value might not exist
}

// Strict mode
function getValue(obj: MyType | null): number {
  if (!obj) return 0; // Explicit null check
  if (!('value' in obj)) return 0; // Type guard
  return obj.value;
}
```

Strict mode forces the bug-prone code into an explicitly safe pattern.

**Implementation Strategy:**

For new projects: enable strict mode from day one (recommended).
For legacy projects: use typescript-strict-plugin to enable strict mode incrementally (file-by-file or directory-by-directory).

**How It Applies to Claude Debugging:**

Claude should assume strict mode is enabled and:
- Ask for TypeScript strict mode status upfront
- If not enabled, suggest enabling it as a fix
- When proposing fixes, assume strict null checks (add null checks, use optional chaining)
- Use type information to guide bug localization (type mismatches near error locations)

**Limitations:**
- Only catches type-level bugs; logic bugs still possible
- Requires TypeScript (not available in JavaScript)
- Strict mode enforcement may feel restrictive to developers unfamiliar with it
- Does not catch runtime bugs (type erasure at runtime)

---

### 3.4 ESLint Plugins for Real Bugs (Not Style)

**The Problem with ESLint:**

Most ESLint rules are style-focused (indentation, spacing, naming conventions). A 2025 benchmark found that many security-focused ESLint plugins miss 80% of real vulnerabilities.

**Best Plugins for Real Bug Detection:**

1. **eslint-plugin-sonarjs:**
   - Detects code smells: duplicated code, unreachable statements, cognitive complexity
   - Rule count: ~80 rules
   - Focuses on bugs and maintainability, not style

2. **eslint-plugin-import:**
   - Detects misspelled paths, circular dependencies
   - Catches mismatched named imports before runtime
   - High signal-to-noise ratio (few false positives)

3. **eslint-plugin-unicorn:**
   - 100+ rules for modern JavaScript patterns
   - Catches subtle issues: incorrect typeof checks, improper array construction
   - Example rule: prevent `new Array(n)` (creates sparse array) in favor of `Array(n).fill()`

4. **Security Plugins (2025):**
   - Some plugins now offer 6x more coverage (89 rules vs 14)
   - Cover web, mobile, API, and AI security
   - But still miss ~80% of real vulnerabilities (per 2025 benchmark)

**Key Insight:** Even best ESLint plugins are incomplete. They catch explicit patterns but miss:
- Complex logic bugs
- Control flow violations
- Type mismatches (without TypeScript)
- Performance issues

**How It Applies to Claude:**

Claude should:
1. Run ESLint (sonarjs, import, unicorn plugins) as a first-pass bug detector
2. Treat ESLint as finding *obvious* bugs only
3. Supplement with other analyses (tree-sitter, TypeScript type checking, custom heuristics)
4. When a fix passes ESLint, recognize that as "meets obvious standards," not "is correct"

**Limitations:**
- Plugin quality varies widely
- False positive rate increases with plugin count
- Not suitable for security-critical analysis (31.3% recall on real vulnerabilities)
- Requires configuration tuning per project

---

## 4. Production Debugging Integration: From Dev to Production

### 4.1 Sentry Integration for React/Next.js

**What It Is:**
Sentry is an application performance monitoring (APM) and error tracking platform. It captures exceptions, crashes, and slow transactions in production.

**How It Works:**

1. **Installation & Configuration:**
   ```javascript
   import * as Sentry from "@sentry/react";

   Sentry.init({
     dsn: "https://...", // Data Source Name
     environment: "production",
     tracesSampleRate: 0.1, // 10% of transactions
     integrations: [
       new Sentry.Replay({ maskAllText: true })
     ]
   });
   ```

2. **Data Capture:**
   - Exceptions: try/catch blocks, unhandled rejections
   - Performance: transaction tracing, slow transactions
   - Session replay: video-like reconstruction of user actions before/during error

3. **Grouping & Alerting:**
   - Errors are grouped by fingerprint (stack trace pattern)
   - Alerts sent to team when new errors appear or error rate exceeds threshold

**2025 Enhancements:**

- **React 19 Integration:** Error hooks now exposed—Sentry can use `Sentry.reactErrorHandler` to capture errors automatically
- **Environment Filtering:** Configuration now supports filtering non-critical errors (404s, expected network failures)
- **Release Tracking:** Errors can be associated with specific releases, enabling correlation with deployments
- **Custom Instrumentation:** Fine-grained tracing for specific code paths

**Key Metrics:**

1. **Error Volume:** Number and types of errors
2. **Error Rate:** Errors per session
3. **Affected Users:** How many unique users encountered each error
4. **Browser/Device:** Error clustering by platform
5. **Performance Impact:** Slowest transactions, bottlenecks

**How It Applies to Claude Debugging:**

Sentry data should feed directly into debugging:
- When Claude is asked to debug an issue, check if it exists in Sentry
- Use error grouping to understand if it's a known issue (recurring pattern) or novel
- Use session replay to understand user actions leading to error
- Use affected user count to prioritize: 1 user = lower priority, 10k users = critical

Claude's conversation should reference Sentry data: "Looking at Sentry, this error affects 847 users and is increasing. Most occur on Chrome 124. Let's focus on browser compatibility first."

**Limitations:**
- Sampling (10% transactions) means some errors are missed
- Session replay is privacy-sensitive; must be configured carefully
- High-volume error clustering can obscure root causes
- Sentry data lags production by minutes; not real-time

---

### 4.2 Web Vitals & Performance Monitoring

**What It Is:**
Core Web Vitals are Google's metrics for measuring user experience:
- **LCP (Largest Contentful Paint):** Time until largest content element renders (target: <2.5s)
- **INP (Interaction to Next Paint):** Delay from user interaction to visual response (target: <200ms)
- **CLS (Cumulative Layout Shift):** Measure of unexpected layout changes (target: <0.1)

These are now Google ranking factors and affect SEO.

**Web-Vitals Library (v4):**

The web-vitals JavaScript library measures all three metrics accurately:
```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log); // Cumulative Layout Shift
getLCP(console.log); // Largest Contentful Paint
getINP(console.log); // Interaction to Next Paint
```

Reports are collected and sent to analytics backend (Sentry, DataDog, custom).

**2025 Trends:**

- **AI-Driven Optimization:** 72% of companies now use AI tools for Core Web Vitals optimization
- **Predictive Preloading:** Navigation AI predicts user's next page and preloads, making page loads feel instant
- **Real-Time Monitoring:** Chrome DevTools now shows Core Web Vitals in Performance panel without recording

**How It Applies to Claude Debugging:**

Performance bugs often manifest as high Web Vitals scores. Claude should:
1. Ask: "What are your current Core Web Vitals?"
2. If LCP is high: investigate slow initial content render
3. If INP is high: investigate JavaScript execution during interactions
4. If CLS is high: investigate layout shifts (image loading, late-loading content)

Example: User reports slow app. Sentry shows no errors. Web-vitals show INP of 800ms (target 200ms). Claude should investigate JavaScript execution during interactions, particularly event listeners.

**Limitations:**
- Web Vitals measure user experience, not application correctness
- High Web Vitals don't prove absence of bugs
- Performance bugs are often subtle (specific to user's device, network, browser)
- Real-user data is noisy (device variation, network variation)

---

### 4.3 Lighthouse CI: Continuous Performance Auditing

**What It Is:**
Lighthouse is Google's auditing tool for performance, accessibility, SEO, and best practices. Lighthouse CI automates running Lighthouse on every commit.

**How It Works:**

1. **Setup in CI/CD Pipeline:**
   ```yaml
   - run: lhci autorun
     # Runs Lighthouse on configurable URLs
     # Compares against baseline
     # Asserts thresholds (e.g., performance > 90)
   ```

2. **Metrics Tracked:**
   - Performance Score (0-100)
   - Accessibility Score
   - Best Practices Score
   - SEO Score
   - Detailed metrics: FCP, LCP, CLS, TTI, Speed Index

3. **Regression Detection:**
   - Compares PR performance against main branch
   - Flags regressions (e.g., performance dropped 5 points)
   - Prevents merging if thresholds not met

**Recent Status (2025):**

- Lighthouse CI remains Google's official solution for performance CI
- Integrates with GitHub Actions, GitLab, Jenkins, others
- "Start slowly" recommendation: begin with reporting, progress to assertions over time

**How It Applies to Claude Debugging:**

If Claude is helping with a performance issue:
1. Run Lighthouse on both working (older) and broken (current) versions
2. Compare scores and metrics
3. Identify specific regressions: "LCP increased from 1.8s to 3.2s. This suggests image loading issue or JavaScript execution delay."
4. Use detailed metrics to pinpoint causes, then propose fixes

Example: Lighthouse shows performance score dropped from 85 to 72. Detailed metrics show LCP is 3.5s. Lighthouse recommends "Preload key requests." Claude can investigate what content is blocking initial render and add `<link rel="preload">`.

**Limitations:**
- Lighthouse runs in lab environment; doesn't capture real-user variance
- Performance improvements in lab don't always translate to production
- Requires stable test environment (network, device)
- Assertions can be too strict (fail on environmental noise) or too loose (allow real regressions)

---

### 4.4 Integration Pattern: Dev-to-Production Debugging Pipeline

**Best Practice Pattern:**

Modern teams use this integration:

1. **Development:**
   - Run tests locally
   - Use ESLint + TypeScript for obvious bugs
   - Run Lighthouse locally for performance

2. **Pre-Commit:**
   - Pre-commit hooks run ESLint, type checking, fast tests
   - Block commits if obvious issues found

3. **CI/CD:**
   - Full test suite runs
   - Lighthouse CI runs, prevents regression
   - Code scanning (CodeQL) runs, reports vulnerabilities
   - Build succeeds only if all checks pass

4. **Deployment:**
   - Changes go to staging first
   - Run smoke tests, performance benchmarks
   - Deploy to production

5. **Production Monitoring:**
   - Sentry captures errors, trends
   - Web-Vitals library measures real user experience
   - Alerts trigger on anomalies

6. **Feedback Loop:**
   - Production data informs development priorities
   - Most-impactful errors get fixed next
   - Performance regressions are visible immediately

**How It Applies to Claude:**

Claude should model this pipeline when helping with debugging:
- Start with: "What's the error?" (dev-time question)
- Progress to: "How do we prevent this bug in the future?" (testing/CI question)
- Include: "How are users affected?" (production monitoring question)

A complete debugging session would:
1. Reproduce locally (dev)
2. Identify root cause (dev)
3. Propose fix (dev)
4. Ensure tests pass (CI)
5. Verify performance not regressed (Lighthouse CI)
6. Check for similar issues elsewhere (code search)
7. Plan monitoring to catch recurrence (Sentry)

**Limitations:**
- This pipeline requires significant tooling investment
- Each stage adds latency; deployments take time
- Some bugs only appear in production with real data; hard to catch in dev/staging
- Feedback loops are slow (can take hours/days to detect issues after deployment)

---

## 5. Code Quality During Debugging: The Boy Scout Rule & Refactoring Safety

### 5.1 The Boy Scout Rule: "Leave Code Better Than You Found It"

**What It Is:**
Introduced to programming by Uncle Bob (Robert C. Martin) in *Clean Code*. The principle: whenever you touch code, improve it—even if you're just passing through.

Examples:
- Fixing a bug? Rename confusing variables in that function while you're at it.
- Investigating an issue? Extract duplicated code blocks.
- Writing a test? Simplify the code being tested.

**Benefits:**

1. **Reduces Technical Debt:** Small, continuous improvements prevent debt accumulation
2. **Improves Understanding:** Refactoring forces you to understand code thoroughly
3. **Catches Additional Bugs:** While refactoring, you often spot other issues
4. **Team Culture:** Everyone improving code incrementally beats large rewrite efforts

**Research Findings:**

- Teams following the boy scout rule report 30% reduction in overall code complexity
- Micro-refactoring during bug fixes accelerates future development
- Engineers spend less time debugging similar issues

**Practical Application:**

When debugging, the boy scout rule suggests a three-level fix:

1. **Level 1 (Required):** Fix the specific bug
   - Minimum change to make tests pass
   - Don't break anything else

2. **Level 2 (Recommended):** Improve the function containing the bug
   - Rename variables if confusing
   - Extract complex logic
   - Add comments explaining the fix

3. **Level 3 (Optional):** Improve related code
   - Are there similar bugs elsewhere? Fix them.
   - Is the error handling pattern weak? Strengthen it.
   - Are there tests missing? Add them.

**How It Applies to Claude Debugging:**

Claude should present fixes at all three levels and let the user choose:

```
## Level 1: Minimal Fix (Safe, Minimal Change)
Changed line 47: `if (x > 5)` → `if (x >= 5)`
Tests pass. Bug fixed.

## Level 2: Improved Function (Recommended)
Changed lines 42-52: Extract null check, rename variables for clarity
Changed line 47: Fixed comparison
Added comments explaining the fix

## Level 3: Related Improvements (Optional)
Found 3 similar potential bugs in related functions
Found test coverage gap (no test for boundary case x==5)
Simplified error handling in exception path
```

Users might choose Level 1 (fast fix) or Level 2 (maintain code) or Level 3 (proactive improvement).

**Limitations:**
- Refactoring risks introducing new bugs; requires strong test suite
- Not appropriate for emergency fixes (live production issue)
- "Better" is subjective; team standards needed
- Refactoring can obscure the original bug fix in code review

---

### 5.2 Cognitive Complexity & Safe Refactoring

**What It Is:**
Cognitive Complexity (SonarQube metric) measures how hard code is to understand, accounting for:
- Nested conditionals (deeper nesting = higher complexity)
- Boolean operators (multiple conditions = more mental load)
- Loop nesting
- Recursion depth

Unlike cyclomatic complexity (which counts paths), cognitive complexity counts mental strain.

**Refactoring Targets:**

SonarQube recommends targeting functions with cognitive complexity > 15:

```javascript
// High complexity (CC=12)
function processOrder(order) {
  if (order.items.length > 0) {
    for (let item of order.items) {
      if (item.price > 0) {
        if (item.quantity > 0) {
          if (order.customer.verified) {
            // ... nested logic
          } else {
            // error case
          }
        } else {
          // error case
        }
      }
    }
  }
}

// Lower complexity (CC=3) - same logic, better structure
function processOrder(order) {
  const validItems = order.items.filter(isValidItem);
  if (!validItems.length) return;

  for (const item of validItems) {
    processItem(item, order.customer);
  }
}
```

Refactoring reduced complexity through:
- Early returns (reduce nesting)
- Helper functions (extract logic)
- Filtering/mapping (replace nested conditionals)

**Safety During Refactoring:**

High cognitive complexity correlates with bugs (humans make mistakes understanding complex code). Refactoring to lower complexity reduces bug likelihood.

Research shows: reducing CC from 20 to 10 correlates with 20-30% fewer bugs in that function over next 6 months.

**How It Applies to Claude Debugging:**

When proposing a fix:
1. Calculate cognitive complexity of the fixed function
2. If CC > 15, suggest refactoring as part of Level 2/3 fix
3. Ensure test coverage exists before refactoring
4. Present refactoring separately from bug fix (two commits)

Example: Bug is in a function with CC=18. Propose:
- Commit 1: Add test coverage (refactoring safety)
- Commit 2: Minimal bug fix (changes 1 line)
- Commit 3: Refactoring to reduce CC to 8 (extract nested logic)

**Limitations:**
- Cognitive complexity is subjective; humans disagree on "hard to understand"
- Refactoring takes time; not always justified for low-risk functions
- Reducing CC doesn't guarantee bug-free code (logic bugs still possible)
- Automated CC calculation sometimes misses real complexity sources

---

### 5.3 Test-Driven Refactoring: Ensuring Correctness

**Pattern:**

Safe refactoring requires:
1. **Test Coverage:** Comprehensive tests for the function being refactored
2. **Refactor:** Change implementation without changing behavior
3. **Test Again:** Run same tests; ensure all still pass

This is the "Green-Red-Green" cycle:
- Green: Tests pass initially (good test coverage)
- Red: (Skipped; tests already green)
- Green: Tests pass after refactoring

If tests fail after refactoring, you've introduced a bug and can revert immediately.

**Limitations of Test-Driven Refactoring:**

- Requires high-quality test suite; weak tests don't catch refactoring bugs
- Some refactorings are hard to test (performance optimizations, caching)
- Tests can only verify observable behavior; internal refactorings might break invariants not tested

**How It Applies to Claude:**

Claude should:
1. Ask: "What tests cover this function?"
2. If insufficient, suggest adding tests first
3. Only refactor if tests exist
4. Show test results before/after refactoring

---

## 6. Synthesis: Building a Debugging Skill for Claude

### 6.1 Optimal Debugging Strategy Based on Research

Combining insights from all five areas, an ideal debugging strategy would:

**Phase 1: Immediate Context (Minutes)**
- User reports bug
- Claude gathers information: error message, environment, reproduction steps
- Check Sentry/error tracking for similar issues (production signal)
- Run tests locally to understand failure mode

**Phase 2: Root Cause Analysis (10-30 Minutes)**
- Use ESLint + TypeScript to identify obvious issues
- Use tree-sitter queries to find related patterns in codebase
- Search for similar bugs in code review history
- Analyze stack traces to narrow scope

**Phase 3: Multi-Hypothesis Generation (30-60 Minutes)**
- Generate 3-5 candidate root causes
- For each, predict what the fix would look like
- Order by likelihood based on context clues

**Phase 4: Iterative Fixing (1-2 Hours)**
- Generate minimal fix (Level 1)
- Run tests, check results
- If tests fail, analyze failure message and iterate (ChatRepair-style)
- Repeat 3-5 times until fix passes

**Phase 5: Validation & Improvement (30-60 Minutes)**
- Ensure fix passes all tests
- Check if tests are adequate (capable-tests ratio consideration)
- Identify related bugs that should be fixed
- Propose Level 2/3 improvements (refactoring, test additions)

**Phase 6: Long-Term Prevention (15-30 Minutes)**
- Plan monitoring (Sentry alerts)
- Suggest test additions to prevent recurrence
- Document the bug and fix for team knowledge base

**Estimated Total Time:** 2-3 hours for complex bugs, 30 min for simple bugs.

### 6.2 Key Principles for Claude Debugging

1. **Test-Driven Iteration:** Always verify against test suite, use test feedback to guide next hypothesis
2. **Multiple Signal Sources:** Combine error logs, test failures, static analysis, code search, production data
3. **Explicit Reasoning:** Make thinking visible—"We're seeing null reference errors on line 47, let's check if null checks exist"
4. **Verification Hierarchy:** Not all "passing tests" are equivalent; understand test quality
5. **Refactoring Awareness:** When fixing, consider if code quality improvements are appropriate
6. **Production Context:** Understand how many users affected, what their impact is, urgency level
7. **Risk Management:** Always present multiple fix options with explicit trade-offs
8. **Knowledge Preservation:** Document learnings for future debugging

### 6.3 Current Limitations & Honest Assessment

No current system achieves >80% first-time accuracy on diverse bugs:
- RepairAgent: 164/337 bugs (48.7%)
- ChatRepair: 162/337 bugs (48.1%)
- Claude Opus 4.5: 79.2% on SWE-bench verified, but only 17.8% on unseen codebases
- Sentry detection: Depends entirely on test quality; garbage in, garbage out

**Fundamental Limits:**
- Dynamic languages (JavaScript) are inherently hard to analyze statically
- Bugs requiring domain knowledge (why is this data structure wrong?) need human context
- Some bugs only reproduce under specific hardware/network conditions (timing bugs, race conditions)
- Test quality determines ceiling—perfect analysis can't exceed test quality

**What Current Systems Do Well:**
- Finding obvious syntax/type errors (AST + TypeScript)
- Detecting common vulnerability patterns (CodeQL, ESLint)
- Iterating based on test feedback (ChatRepair pattern works)
- Combining multiple artifact types (SWE-Bench agents)

**What Current Systems Struggle With:**
- Logic bugs in complex domain code
- Performance bugs (need profiling data, not static analysis)
- Security bugs in dynamic contexts (JavaScript eval patterns)
- Bugs requiring cross-service understanding (distributed systems)

---

## 7. Research-to-Practice Roadmap for Claude

### Short Term (Next 30 Days)
- [ ] Integrate tree-sitter queries for JavaScript pattern detection
- [ ] Connect to Sentry API to show error frequency/impact in conversations
- [ ] Implement test feedback loop (ChatRepair-style iteration)
- [ ] Add ESLint plugin recommendations (sonarjs, import, unicorn)

### Medium Term (2-3 Months)
- [ ] Implement repository navigation tools (search, dependency graphs)
- [ ] Add Lighthouse integration for performance debugging
- [ ] Develop mutation testing lightweight checks
- [ ] Build code quality assessment (cognitive complexity detection)

### Long Term (3-6 Months)
- [ ] Integrate CodeQL for semantic analysis
- [ ] Implement production-to-development feedback (Sentry → Claude)
- [ ] Build test quality assessment (capable-tests ratio estimation)
- [ ] Create debugging knowledge base (recurring bugs, patterns)

### Research Gaps to Monitor
- Generalization to unseen codebases (current 5-10 point drop is concerning)
- Security bug detection in JavaScript (current 31% recall unacceptable)
- Performance bug diagnosis without profiling data
- Multi-service bug diagnosis (microservices, distributed systems)

---

## 8. Key Sources & Further Reading

### Academic Papers
- [RepairAgent: An Autonomous, LLM-Based Agent for Program Repair](https://arxiv.org/abs/2403.17134) - ICSE 2025
- [A Survey of LLM-based Automated Program Repair](https://arxiv.org/html/2506.23749v1) - IEEE TSE 2025
- [When Automated Program Repair Meets Regression Testing](https://arxiv.org/html/2105.07311v2) - ACM TOSEM
- [LLM-based Agents for Automated Bug Fixing: How Far Are We?](https://arxiv.org/html/2411.10213v2) - 2024

### Benchmarks & Leaderboards
- [SWE-Bench Verified Leaderboard](https://www.swebench.com/) - Public benchmark
- [SWE-Bench Pro Leaderboard](https://scale.com/leaderboard/swe_bench_pro_public) - Private codebase evaluation
- [Defects4J](https://github.com/rjust/defects4j) - Java bug benchmark (854 bugs)

### Tools & Frameworks
- [Stryker Mutation Testing](https://stryker-mutator.io/) - JavaScript mutation testing
- [CodeQL](https://codeql.github.com/) - Semantic code analysis
- [Tree-Sitter](https://tree-sitter.github.io/) - Syntax tree parsing
- [SonarQube](https://www.sonarsource.com/products/sonarqube/) - Code quality platform
- [Sentry](https://sentry.io/) - Error tracking & monitoring
- [Lighthouse CI](https://googlechrome.github.io/lighthouse-ci/) - Performance CI/CD

### Production Tools
- [Cursor](https://www.cursor.com/) - AI-assisted code editor
- [GitHub Copilot Workspace](https://github.com/features/copilot/workspace) - Agent-based coding
- [Aider](https://aider.chat/) - LLM-assisted command-line editing

---

## Conclusion

The state of the art in 2025-2026 shows that LLM-assisted debugging works best when:

1. **Multi-phase approach:** Context gathering → analysis → hypothesis → iteration → validation → prevention
2. **Test-driven iteration:** Using test feedback to refine hypotheses (ChatRepair pattern)
3. **Multiple signal sources:** Combining static analysis, dynamic testing, production data, and code search
4. **Explicit reasoning:** Making thinking visible to users, not hiding behind black-box decisions
5. **Risk awareness:** Presenting trade-offs and limitations honestly

No system achieves >80% accuracy across diverse bugs. The 30% gap between public and private SWE-Bench results reveals fundamental generalization challenges. However, systems that excel at iteration, test-driven development, and multi-artifact integration show significantly better results than single-pass generation approaches.

For Claude, the roadmap emphasizes practical integration with existing tools (Sentry, Lighthouse, ESLint, TypeScript) rather than building novel AI capabilities. Leveraging domain-specific analysis tools + LLM-powered planning creates more reliable debugging experiences than pure LLM approaches.

The future likely involves tighter feedback loops: development-time tools informing debugging priorities, production errors feeding back to dev tools, and increasingly sophisticated test quality assessment. The missing piece in current systems is understanding test intent and test quality—a human concern that remains largely unautomated.
