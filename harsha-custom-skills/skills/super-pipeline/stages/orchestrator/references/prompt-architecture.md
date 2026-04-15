# Prompt Architecture Reference

Complete guide to writing self-contained, execution-ready prompts for AI coding assistants.

## The Core Insight

**Prompts fail not from lack of information, but from implicit assumptions.** Experienced developers carry vast mental context they don't realize they're omitting—file structures, naming conventions, framework versions, domain terminology. A self-contained prompt must externalize this tacit knowledge into explicit specification.

Every prompt executed in a fresh chat window operates under zero prior context. The receiving AI knows nothing about your project, conventions, intent, or previous conversations.

---

## Six Non-Negotiable Components

Research across AI coding tools (Cursor, Claude Code, Aider) and military operation orders reveals six essential components:

### 1. Situation/Context (the "Given")
What exists right now. Technology stack with versions, relevant existing code patterns, project structure, environmental constraints.

**Answers**: "What world am I operating in?"

### 2. Mission/Objective (the "What")
A single, unambiguous statement of what needs to be accomplished. Military doctrine insists mission statements cover Who, What, When, Where, Why.

**For coding tasks**: what to build, where it fits, and the business/technical purpose.

### 3. Intent (the "Why It Matters")
Borrowed from Commander's Intent—explains the purpose behind the task so the AI can adapt when specifics don't apply.

**Critical question**: "If we accomplish nothing else, what must happen?"

This enables intelligent improvisation when edge cases arise.

### 4. Execution Constraints (the "How" and "How Not")
Explicit boundaries: what approaches to use, what to avoid, what libraries are permitted, what patterns to follow.

**Affirmative constraints work better** than negative ones: "use dependency injection" beats "don't use singletons."

### 5. Resources/References (the "With What")
Available tools, existing code to reference, relevant documentation, and anything that should inform implementation.

**Critical distinction**: what's available versus what must be created.

### 6. Success Criteria (the "Definition of Done")
How to verify completion. Not "make it work" but measurable conditions: tests pass, specific behavior achieved, performance threshold met.

**Aviation principle**: Responses should state actual values, not vague confirmations.

---

## Minimum Viable Context Hierarchy

### Always Include (Execution Blockers)
- **Primary objective** in first paragraph (LLMs attend best to beginning and end)
- **Technology stack with versions** (Node 18 vs Node 14 changes everything)
- **File paths and structure** for any code being modified
- **Actual code snippets** when referring to existing code (not descriptions)
- **Expected vs. actual behavior** for debugging tasks
- **Interface contracts** when integrating with existing systems

### Usually Include (Quality Enablers)
- Coding conventions and style preferences
- Error handling expectations (fail silently vs throw vs log)
- Test requirements (unit tests expected? what framework?)
- Related files that provide pattern context
- Domain terminology definitions for specialized contexts

### Conditionally Include (Enhancement Layer)
- Performance constraints (when they matter)
- Security considerations (for user-facing or data-handling code)
- Backwards compatibility requirements
- Rollback/reversibility needs

---

## The "Implicit Knowledge" Capture Checklist

Experienced developers take these for granted—prompts fail when they're omitted:

1. **Framework idioms**: React functional vs class components, Express middleware patterns
2. **Project conventions**: Where tests live, how files are named, import style
3. **Environment assumptions**: Browser vs Node, Docker vs local, dev vs prod
4. **State management**: How data flows, what's in scope, persistence model
5. **Error patterns**: How errors propagate, what gets logged, alerting implications
6. **Temporal context**: Current time, timezone, duration calculations (pre-compute these—LLMs struggle with time math)

---

## Context Compression vs. Completeness

LLMs suffer from **"lost in the middle"** degradation where accuracy drops 20%+ for information buried in long contexts, yet incomplete context causes assumption-based failures.

### Optimal Structure Rules

**Position critical information at the beginning**—LLMs exhibit primacy bias. Place mission statement, key constraints, and success criteria in the first 20% of the prompt.

**Use hierarchical structure with clear headers**—Markdown or XML tags (`<context>`, `<constraints>`, `<success_criteria>`) help models parse sections accurately.

**Keep prompts under 2,000 tokens when possible**—Beyond this threshold, middle-context degradation becomes significant. For complex tasks, split into sequential prompts.

**Separate "reference context" from "action instructions"**—Put code snippets and examples in clearly labeled reference sections; keep instructions crisp and direct.

### Inline vs. External Reference

| Inline (Cannot Reference) | External Reference OK |
|--------------------------|----------------------|
| The specific task and objective | General coding conventions |
| Interface contracts being implemented | Full framework documentation |
| Code being modified or extended | Architectural overview |
| Success criteria and constraints | Style guide |
| Domain terminology definitions | Historical decision context |

---

## Prompt Patterns by Task Type

### Setup and Scaffolding Tasks

**What they need**: Complete technology decisions, directory structure, configuration requirements, and dependency versions.

```markdown
# Context
New TypeScript project for a REST API service.
Tech stack: Node 20, Express 4.18, PostgreSQL 15, Prisma ORM.
Testing: Jest with supertest for integration tests.
Directory structure follows: src/{routes,services,models,middleware}

# Task
Scaffold the project with:
- Package.json with exact dependencies
- tsconfig.json for ES2022 target
- Prisma schema for PostgreSQL connection
- Basic Express server with health endpoint
- Jest configuration for TypeScript

# Constraints
- Use ESM imports (import/export), not CommonJS
- Include .env.example with required variables
- Add scripts: dev, build, test, db:migrate

# Success criteria
- `npm install && npm run dev` starts server on port 3000
- `curl localhost:3000/health` returns {"status": "ok"}
```

### Feature Implementation Tasks

**What they need**: Existing code patterns to follow, interface contracts, integration points, and explicit boundaries on what to modify.

```markdown
# Context
Adding user authentication to existing Express API.
Current auth: None (endpoints are unprotected)
User model exists in src/models/user.ts with: id, email, passwordHash
Existing patterns: Services return {success, data, error} objects

# Existing Code Reference
```typescript
// src/services/user.service.ts (pattern to follow)
export async function getUserById(id: string) {
  const user = await prisma.user.findUnique({where: {id}});
  if (!user) return {success: false, error: 'User not found'};
  return {success: true, data: user};
}
```

# Task
Implement JWT authentication:
1. Login endpoint: POST /auth/login (email, password) → JWT token
2. Middleware: authMiddleware that validates JWT, adds user to req
3. Protected route decorator/helper for applying middleware

# Constraints
- Use jsonwebtoken library
- Tokens expire in 24 hours
- Store JWT_SECRET in environment variable
- Follow existing service return pattern
- Do NOT modify existing user model

# Success criteria
- Login returns valid JWT for correct credentials
- Protected routes return 401 without valid token
- req.user populated on protected routes
```

### Research and Investigation Tasks

**What they need**: Explicit definition of "done"—research tasks fail most often because output expectations are undefined.

```markdown
# Context
Evaluating state management solutions for React Native app.
Current: Local useState/useContext, becoming unwieldy at ~50 components.
Requirements: Offline-first with sync, TypeScript support, debugging tools.

# Task
Research and recommend ONE state management solution.
Candidates to evaluate: Redux Toolkit, Zustand, Jotai, MobX.

# Research Criteria (evaluate each on)
1. TypeScript integration quality (1-5)
2. Offline persistence options
3. DevTools and debugging capabilities
4. Bundle size impact
5. Learning curve for team of 3 mid-level devs

# Output Format
## Recommendation: [Library Name]
### Why (3-5 sentences on key deciding factors)
### Comparison Table (all candidates, all criteria)
### Migration Path (from current useState approach)
### Risks (what could go wrong)

# Success criteria
- One clear recommendation with justification
- All four candidates evaluated on all five criteria
- Actionable migration path with estimated effort
```

### Bug Fix Tasks

**What they need**: Reproduction steps, actual error messages (verbatim), expected vs actual behavior, what has been tried.

```markdown
# Bug Report
Users report checkout fails intermittently with "Payment processing failed"

# Reproduction Steps
1. Add item to cart (any item)
2. Proceed to checkout
3. Enter test card 4242424242424242
4. Submit payment
5. ~20% of attempts fail with generic error

# Error Context
```
Error in payment.service.ts:47
StripeError: Your card was declined. (code: card_declined)
But user card is test card that should never decline
```

# Expected Behavior
Test cards always succeed in test mode

# Actual Behavior
Intermittent failures, no pattern in timing

# Already Investigated
- Stripe dashboard shows no corresponding declined charges
- Error happens before Stripe API call returns
- Network logs show request never reaching Stripe

# Environment
- Production: Stripe live mode (but same issue in test mode)
- Node 18.17.0, stripe npm 14.5.0

# Task
Identify root cause and fix the intermittent payment failure.

# Success criteria
- Root cause identified with evidence
- Fix implemented and tested
- 100 consecutive test transactions succeed
```

### Integration Tasks

**What they need**: Complete interface contracts on both sides—what existing system expects, what new component must provide.

```markdown
# Context
Integrating Stripe payment processing into checkout flow.

# Existing Interface (what checkout expects)
```typescript
interface PaymentProcessor {
  createPaymentIntent(amount: number, currency: string): Promise<{clientSecret: string}>;
  confirmPayment(paymentIntentId: string): Promise<{success: boolean, error?: string}>;
  handleWebhook(payload: string, signature: string): Promise<WebhookEvent>;
}
```

# Stripe API Context
Using Stripe API version 2024-12-18.
Webhook events needed: payment_intent.succeeded, payment_intent.failed

# Task
Implement StripePaymentProcessor class that satisfies PaymentProcessor interface.

# Constraints
- Use stripe npm package
- Store STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET in env
- Log all Stripe API errors with request IDs
- Return user-friendly errors, not raw Stripe errors

# Success criteria
- Class compiles and satisfies interface
- Unit tests mock Stripe client and verify all three methods
- Webhook signature validation working
```

---

## Anti-Pattern Catalog

### Ambiguity Anti-Patterns

| Anti-Pattern | Example | Why It Fails | Fix |
|--------------|---------|--------------|-----|
| Subjective terms | "Make it faster" | No measurable target | "Reduce response time from 2s to under 500ms" |
| Referential ambiguity | "Update it to handle the edge case" | What is "it"? Which edge case? | "Update validateEmail() to handle plus-addressing like user+tag@domain.com" |
| Scope ambiguity | "Refactor the auth module" | What aspects? To what end? | "Refactor auth module to use dependency injection for testability" |
| Missing negative constraints | "Build a login form" | May include things you don't want | "Build a login form. Do not include 'remember me' or social login." |

### Context Anti-Patterns

| Anti-Pattern | Example | Why It Fails | Fix |
|--------------|---------|--------------|-----|
| Lost in the middle | Critical info in paragraph 5 of 10 | LLMs attend poorly to middle content | Move critical info to first paragraph |
| Context dump | Including entire codebase | Dilutes signal, causes confusion | Include only files being modified + pattern examples |
| Implicit dependencies | "Use the standard approach" | Standard to whom? | "Use the repository pattern as shown in user.repository.ts" |
| Session-dependent references | "As we discussed" | Fresh context has no history | Repeat all relevant context |

### Structural Anti-Patterns

| Anti-Pattern | Example | Why It Fails | Fix |
|--------------|---------|--------------|-----|
| Overloaded prompts | "Build frontend, backend, and deploy scripts" | Multiple complex tasks, partial completion | One task per prompt |
| Missing the question | "Here's my code" (no ask) | AI doesn't know what you need | Always include explicit action request |
| Conflicting instructions | "Be brief but comprehensive" | Impossible to satisfy both | Prioritize: "Be comprehensive; length is acceptable" |
| No success criteria | "Implement caching" | How to verify completion? | "Implement caching; repeated calls within 60s should return cached response" |

---

## Prompt Drift Prevention

Prompts "drift" from original intent through several mechanisms:

1. **Scope creep during execution**: AI discovers related issues and addresses them unsolicited
2. **Implicit goal replacement**: AI substitutes its interpretation of "good code" for your actual requirements
3. **Pattern overfitting**: AI locks onto an example pattern and applies it where inappropriate
4. **Confirmation theater**: AI produces plausible-looking output that passes surface inspection but fails actual requirements

**Prevention Strategies**:
- Include explicit scope boundaries ("Do NOT modify tests")
- Specify verification steps ("Run the test suite before considering complete")
- Define acceptance criteria that can be mechanically verified

---

## Quality Checklist

### Before Execution

**Mission Clarity**
- [ ] Single, unambiguous objective stated in first paragraph
- [ ] Success criteria are measurable/verifiable, not subjective
- [ ] Scope boundaries explicitly defined (what's in, what's out)

**Context Completeness**
- [ ] Technology stack with specific versions included
- [ ] Relevant existing code provided as snippets (not references to files AI can't see)
- [ ] All referenced variables, functions, or patterns are defined or shown
- [ ] Interface contracts specified for integration points

**Assumption Elimination**
- [ ] No pronouns without clear antecedents ("it," "the above," "that function")
- [ ] No subjective terms without definitions ("fast," "clean," "better")
- [ ] No implicit domain knowledge assumed
- [ ] Time/date calculations pre-computed (not left to AI)

**Structure Verification**
- [ ] Critical information appears in first 20% of prompt
- [ ] Clear section headers separate context from instructions
- [ ] One primary objective (complex tasks split into sequential prompts)
- [ ] Output format explicitly specified

**Fresh Context Test**
- [ ] Prompt makes sense without any prior conversation
- [ ] All referenced files/code are included inline
- [ ] Someone unfamiliar with the project could understand the task
- [ ] No "as mentioned earlier" or "continuing from before" references

---

## Key Insights

### Commander's Intent is Critical
Including a one-sentence intent ("This caching layer exists to reduce database load during traffic spikes; cache invalidation correctness matters more than hit rate") dramatically improves AI decision-making.

### The 1/3-2/3 Rule
Don't over-specify implementation details. Specify the contract (inputs, outputs, constraints) and let the AI apply its expertise. Micromanaging every line leads to worse code than clear constraints with execution freedom.

### Position Encoding Dominates
LLMs recall beginning and end content far better than middle content. Prompt structure matters as much as prompt content. Always place mission, constraints, and success criteria in the first section.

### Silent Failures are the New Challenge
Newer models increasingly produce code that runs without errors but doesn't work correctly—removing safety checks, creating fake output, passing surface tests while fundamentally broken. Explicit test specifications and verification steps are critical.

### Examples Beat Abstractions
"For an LLM, examples are the 'pictures' worth a thousand words." One concrete input/output example communicates more reliably than paragraphs of abstract requirements.

---

## Universal Execution Template

```markdown
# [Task Title - Verb + Object + Purpose]

## Intent
[One sentence: WHY this task matters and what success enables]
If we accomplish nothing else: [the ONE non-negotiable requirement]

## Context
**Tech Stack**: [Language/version, frameworks/versions, key dependencies]
**Environment**: [Dev/prod, OS, runtime constraints]
**Current State**: [What exists now relevant to this task]

## Existing Code Reference
```[language]
// [filepath]
[Relevant code snippet showing patterns to follow]
```

## Task
[Single, clear objective statement]

### Requirements
- [Specific requirement 1]
- [Specific requirement 2]

### Constraints
- MUST: [Required approaches/patterns]
- MUST NOT: [Explicitly forbidden approaches]
- SHOULD: [Preferred but flexible]

## Interface Contract
**Input**: [What the code receives, with types]
**Output**: [What the code returns, with types]
**Errors**: [How errors should be handled/surfaced]

## Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Verification step - e.g., "All tests pass"]

## Out of Scope
- [Explicit exclusion 1]
- [Explicit exclusion 2]
```

This structure ensures every prompt answers: What world am I in? What do you want? Why does it matter? What are the boundaries? How do I verify completion?
