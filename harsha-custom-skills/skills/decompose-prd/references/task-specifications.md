# AI-Executable Task Specification Format

## Overview

A task specification is a detailed description of a single atomic unit of work that a Claude agent can execute with zero clarifying questions. This document defines the specification format, quality rubric, common anti-patterns, and mapping from PRD requirements to task acceptance criteria.

## The "Zero Questions Test"

This is the core principle: **Every task spec must be executable by a Claude agent without asking for clarification.**

### What Does This Mean?

The agent should be able to answer these questions without making assumptions:

1. **What am I building?** (Clear objective, not "build the feature")
2. **Why am I building it?** (Context and rationale)
3. **What do I start with?** (Specific input files, dependencies, data)
4. **What should I produce?** (Exact output files and format)
5. **What technologies should I use?** (Stack and libraries specified)
6. **How do I know when I'm done?** (Acceptance criteria that are objectively testable)
7. **What am I explicitly NOT doing?** (Boundary conditions and non-goals)
8. **Are there any constraints or gotchas?** (Technical requirements, security, performance)
9. **How does this connect to other tasks?** (Dependencies, integration points)

If the agent would need to ask even one clarifying question, the spec is incomplete.

### The Zero Questions Test in Practice

Bad spec:
```
Task: Implement the login feature
- Objective: Add login capability
- Do this using React and Node.js
- Make sure it's secure
```

Agent questions:
- What specific login methods (email/password, SSO, biometric)?
- What's the database schema?
- Should I create the backend endpoints or just the frontend?
- What "secure" means? OAuth? JWT? Bcrypt?
- File paths?

Good spec:
```
Task: T-1.1.1 Create LoginForm component
- Objective: React component for email/password login form with client-side validation
- Context: Part of Auth epic; form submits to existing /api/auth/login endpoint
- Inputs: Tailwind CSS already configured; useAuth hook from src/hooks/useAuth.ts
- Output: src/components/LoginForm.tsx with unit test
- Stack: React 18 + TypeScript, Tailwind CSS, React Hook Form
- Technical: Use crypto-js for temporary encryption of password in transit (decrypted by HTTPS)
- Do NOT: Implement backend endpoint, password reset flow (T-1.2.1), or 2FA (T-1.3.1)
- AC: Form renders with email and password fields, validates on blur, submits valid data
- Testing: test file uses vitest + React Testing Library, covers happy path and validation errors
```

Fewer questions because specifics are clear.

## Complete Task Specification Schema

Here's the complete structure that every task should include:

```yaml
###############################################################################
# TASK HEADER
###############################################################################

Task ID: T-{epic}.{feature}.{task}
Title: [Action Verb] [Object]
Epic ID: E-{number}
Feature ID: F-{number}.{number}
Status: pending | in_progress | completed | blocked

###############################################################################
# OBJECTIVE: What must be produced (exactly, unambiguously, measurably)
###############################################################################

Objective: |
  [Single paragraph describing what will be built]
  [Specific deliverable, not vague goal]
  [Measurable, testable outcome]

  Example:
  "Create a React component that renders a login form with email and password
   fields, validates input on blur using React Hook Form, displays errors
   inline, and submits form data to the /api/auth/login endpoint via POST."

  NOT: "Implement login functionality" (too vague)
  NOT: "Make login work" (undefined)
  NOT: "Create an awesome login UX" (subjective)

###############################################################################
# CONTEXT: Project background and conventions
###############################################################################

Context: |
  Project: [Name and brief description]
  Tech Stack: [Relevant technologies]
  Architecture: [Relevant architectural patterns]
  Conventions: [Coding standards, naming, patterns used in codebase]
  Related Work: [Other tasks or PRD sections providing context]

  Example:
  "Project: E-commerce platform (MERN stack)
   Architecture: Modular frontend with hook-based state, REST backend
   Conventions: Components in src/components/, organized by feature;
                TypeScript strict mode; Tailwind CSS for styling
   Related: This task enables F-1.2 (OAuth integration) in E-1"

###############################################################################
# INPUTS: What this task depends on
###############################################################################

Inputs:
  Dependencies:
    Hard (must complete first):
      - T-1.0.1: Database schema established  [task_id: brief reason]
      - T-2.1.1: Authentication service ready [reason]

    Soft (preferred before this, not blocking):
      - T-2.2.1: API documentation written [reason]

    Resource (shared):
      - T-1.4.2: Auth configuration [conflict type]

  Required Files:
    - src/hooks/useAuth.ts     [how used]
    - tailwind.config.js       [how used]
    - src/styles/index.css     [how used]

  From PRD:
    - REQ-001: Support email/password authentication
    - REQ-002: Validate email format
    - REQ-003: Handle authentication failures gracefully

  External Resources:
    - [Optional: third-party services, APIs, documentation links]

###############################################################################
# EXPECTED OUTPUT: What will be produced
###############################################################################

Expected Output:
  Files to Create:
    - src/components/LoginForm.tsx
    - src/components/__tests__/LoginForm.test.tsx
    - src/types/auth.ts (update existing with LoginFormProps interface)

  Files to Modify:
    - src/pages/auth/login.tsx (integrate LoginForm component)

  Format & Language:
    - TypeScript with strict mode
    - React 18 functional component
    - Tailwind CSS classes only (no inline styles)
    - JSX with proper typing

  Size Estimate:
    - LoginForm.tsx: ~150 lines (component + prop types)
    - LoginForm.test.tsx: ~200 lines (6 test cases)
    - auth.ts: +10 lines (one interface)

  Definition of Done:
    - Code compiles without errors or warnings
    - All unit tests pass
    - Code passes linting (eslint, prettier, typescript)
    - Changes reviewed and merged to main branch

###############################################################################
# TECHNICAL REQUIREMENTS: Technologies and constraints
###############################################################################

Technical Requirements:
  Stack:
    - React: 18.2+
    - TypeScript: 5.0+
    - React Hook Form: 7.45+
    - Tailwind CSS: 3.3+
    - vitest: 0.34+ (for testing)
    - @testing-library/react: 14.0+

  Design Patterns:
    - Use React Hook Form for form state and validation
    - Custom hooks for reusable logic (already have useAuth)
    - Composition pattern for error display

  Code Structure:
    - Keep component file under 150 lines
    - Move complex validation to separate utility file if needed
    - Use TypeScript interfaces for all props

  Performance:
    - Debounce blur validation by 300ms to avoid excessive re-renders
    - Memoize component with React.memo to prevent parent re-renders
    - No unnecessary re-renders (use useCallback where needed)

  Security:
    - Never log passwords or sensitive data
    - Use HTTPS only (enforced by environment, not this task)
    - Sanitize error messages (don't leak user existence from "user not found")
    - CSRF protection: rely on httpOnly cookies set by backend

  Accessibility:
    - ARIA labels for form inputs (aria-label or aria-labelledby)
    - Error messages associated with inputs (aria-describedby)
    - Proper heading hierarchy
    - Keyboard navigation working (Tab, Enter to submit)
    - Color not sole means of conveying error state

  Browser Support:
    - Chrome, Firefox, Safari, Edge (latest versions)
    - Mobile responsive (tested at 375px, 768px, 1024px widths)

###############################################################################
# BOUNDARY CONDITIONS: What this task does NOT do
###############################################################################

Boundary Conditions:
  Do NOT Implement:
    - Password reset flow (separate task T-1.2.1)
    - OAuth provider integration (separate task T-1.2.2)
    - Two-factor authentication (separate task T-1.3.1)
    - User registration/signup (separate epic)
    - Session persistence/remember me (separate task)
    - Internationalization (separate cross-cutting task)

  Do NOT Modify:
    - Backend API endpoints (owned by T-2.1.3)
    - Authentication service (owned by T-2.1.2)
    - API client configuration (owned by T-0.1.1)
    - Global styles or Tailwind config (frozen)

  Assumptions:
    - /api/auth/login endpoint already exists and works (T-2.1.3)
    - useAuth hook exists and provides login() function (T-2.1.1)
    - Tailwind CSS is configured and imported globally
    - TypeScript strict mode is enabled
    - Test environment (vitest) is configured
    - This form will be used on a dedicated login page

  What's Out of Scope:
    - Mobile app version (web only)
    - Email verification (separate workflow)
    - Rate limiting (handled by backend)
    - Session timeout handling (handled by middleware)

###############################################################################
# ACCEPTANCE CRITERIA: How to verify completion
###############################################################################

Acceptance Criteria:

  Functionality:
    ✓ Component renders a form with email and password input fields
    ✓ Email field validates format on blur (must be valid email address)
    ✓ Password field requires minimum 8 characters on blur
    ✓ Inline error messages appear next to invalid fields
    ✓ Form button is disabled until both fields are valid
    ✓ On submit, form data is passed to useAuth().login() with correct format
    ✓ Success: after submission, no error shown (handled by parent)
    ✓ Error: if login fails, error message displayed above form

  Visual & UX:
    ✓ Component renders with Tailwind styling matching design system
    ✓ Error states have red text and icon (per design system)
    ✓ Loading state shows spinner in button during submission
    ✓ Form is responsive on mobile (looks good at 375px width)
    ✓ Form fields are properly spaced and labeled

  Code Quality:
    ✓ TypeScript compiles with strict mode, no @ts-ignore
    ✓ All props and state are fully typed
    ✓ ESLint passes (no warnings)
    ✓ Prettier formatted
    ✓ No unused imports or variables
    ✓ Comments explain non-obvious logic

  Testing:
    ✓ Unit test file included with >80% coverage
    ✓ Tests cover happy path: valid input → submission
    ✓ Tests cover validation: invalid email, short password
    ✓ Tests cover error handling: API returns 401
    ✓ All tests pass locally and in CI
    ✓ No console errors or warnings during tests

  Integration:
    ✓ Component integrates cleanly into src/pages/auth/login.tsx
    ✓ No console errors when rendered in browser
    ✓ No TypeScript errors in importing files
    ✓ Works with existing useAuth hook without modifications
    ✓ Fits into existing navigation flow

###############################################################################
# VERIFICATION: How to test and validate
###############################################################################

Verification:

  Syntax Verification:
    Command: `npx tsc --noEmit`
    Expected: No TypeScript errors
    Command: `npx eslint src/components/LoginForm.tsx`
    Expected: No linting errors
    Command: `npx prettier --check src/components/LoginForm.tsx`
    Expected: File is properly formatted

  Unit Testing:
    Command: `npm run test -- LoginForm.test.tsx`
    Expected: All tests pass, coverage >80%
    Manual: Open component in Storybook (if available) and verify rendering

  Functional Testing:
    1. Navigate to /login page
    2. Type invalid email → verify error appears on blur
    3. Type valid email, short password → verify password error
    4. Type valid credentials → verify submit enabled
    5. Click submit → verify login attempt
    6. If login fails → verify error message shown

  Integration Testing:
    Command: `npm run test:integration`
    Expected: Login form integration tests pass

  Manual Code Review:
    - Check component follows project conventions
    - Verify accessibility (keyboard nav, ARIA labels)
    - Check for security issues
    - Verify error handling is graceful

###############################################################################
# DEPENDENCIES AND BLOCKING
###############################################################################

Prerequisite Tasks:
  - T-2.1.2: Implement authentication service (must provide login() function)
  - T-2.1.3: Create /api/auth/login endpoint (must exist and be working)

Tasks Blocked by This:
  - T-1.1.2: Add OAuth provider selection UI (needs LoginForm as base)
  - T-1.2.1: Implement password reset flow (needs email field from LoginForm)

Critical Path Impact: On critical path? [ ] Yes  [ ] No
  If yes: Any delays delay overall project completion

###############################################################################
# NOTES AND REFERENCES
###############################################################################

Notes:
  - This is the base login form; OAuth variant created in separate task
  - Component is intentionally simple; business logic in useAuth hook
  - Consider future: rate limiting (backend), brute force protection (backend)

References:
  - PRD Section: "User Authentication" (REQ-001 through REQ-003)
  - Design: Figma link to login screen mockup
  - Related Docs: src/docs/ARCHITECTURE.md, src/docs/FORM-PATTERNS.md
  - External: React Hook Form documentation, Tailwind CSS docs
```

## Quality Rubric for Task Specifications

Rate each task on a scale of 1-5 for each dimension. Total score should be ≥4.0.

### 1. Completeness (Are all sections filled with specific values?)

**5 - Excellent**:
- All sections present and populated
- Objective is crystal clear, no ambiguity
- Specific file paths listed
- Dependencies fully enumerated
- Constraints spelled out

**4 - Good**:
- All major sections present
- Minor gaps (e.g., one missing file path)
- Mostly specific, one or two vague phrases

**3 - Fair**:
- Most sections present but some thin
- Mix of specific and vague language
- Missing some technical details

**2 - Poor**:
- Several missing sections
- Heavy use of vague language ("improve", "implement feature")
- Incomplete file lists or dependencies

**1 - Inadequate**:
- Major sections missing
- Mostly vague ("do the thing")
- Cannot execute without many questions

### 2. Clarity (Is language unambiguous? Do terms have clear meaning?)

**5 - Excellent**:
- Every requirement stated objectively
- No ambiguous words ("good", "appropriate", "nice")
- Technical terms precisely defined
- No conflicting requirements

**4 - Good**:
- Mostly clear with minor vague spots
- One or two subjective terms (acceptable context)
- Technical terms defined or well-known

**3 - Fair**:
- Mix of clear and unclear sections
- Some vague language ("should be fast", "user-friendly")
- Some technical terms not defined

**2 - Poor**:
- Frequent vague language
- Ambiguous requirements
- Poorly defined technical terms

**1 - Inadequate**:
- Heavily subjective ("make it awesome")
- Many undefined terms
- Contradictory requirements

### 3. Testability (Can acceptance criteria be verified objectively?)

**5 - Excellent**:
- All AC are binary pass/fail
- No subjective elements ("looks good")
- Testing approach is clear
- Coverage is comprehensive

**4 - Good**:
- Most AC are testable
- One or two slightly subjective (but mostly clear)
- Testing approach defined

**3 - Fair**:
- AC mix of objective and subjective
- Some testing approach unclear
- Coverage gaps

**2 - Poor**:
- Many AC are subjective ("works well")
- Testing approach vague
- No clear way to verify completion

**1 - Inadequate**:
- AC are mostly aspirational, not testable
- No testing guidance
- Completion is ambiguous

### 4. Boundedness (Is scope clearly limited? Are non-goals explicit?)

**5 - Excellent**:
- Clear scope boundaries
- Explicit "Do NOT" list
- No assumption that task owner knows what to ignore
- Out-of-scope items listed with rationale

**4 - Good**:
- Mostly clear boundaries
- Some non-goals explicit
- Scope is generally limited

**3 - Fair**:
- Somewhat clear boundaries
- Minimal non-goals specified
- Could expand in multiple directions

**2 - Poor**:
- Vague scope
- Few non-goals specified
- Could easily expand beyond intention

**1 - Inadequate**:
- No clear scope limits
- No non-goals
- Task could absorb infinite work

### 5. Independence (How much coupling to other tasks?)

**5 - Excellent**:
- Minimal coupling to other tasks
- All dependencies listed and justified
- Task is parallelizable
- Changes unlikely to require other task modifications

**4 - Good**:
- Some coupling but well-managed
- Dependencies clear
- Task can proceed once deps complete

**3 - Fair**:
- Moderate coupling
- Some hidden dependencies possible
- Parallelism somewhat limited

**2 - Poor**:
- High coupling to multiple tasks
- Dependencies unclear
- Likely to discover missing dependencies during execution

**1 - Inadequate**:
- Extremely coupled
- Dependencies unclear or tangled
- Cannot proceed independently

## Scoring Rubric Summary

| Score | Overall Quality | Action |
|-------|-----------------|--------|
| 4.5-5.0 | Excellent | Ready to execute |
| 4.0-4.4 | Good | Minor refinements okay, can execute |
| 3.5-3.9 | Fair | Should refine before execution |
| 3.0-3.4 | Poor | Needs significant revision |
| <3.0 | Inadequate | Rewrite required |

## Common Task Specification Anti-Patterns

### Anti-Pattern 1: Vague Objective

**Bad**:
```
Objective: Implement the payment feature
```

**Why it fails**: Doesn't answer what "payment feature" means. Process credit cards? Digital wallets? Subscription billing? Which of these?

**Good**:
```
Objective: Create a PaymentMethodForm component that accepts credit card details
(card number, expiry, CVV), validates them using Stripe.js, and passes valid
card tokens to the usePayment() hook for server-side processing.
```

---

### Anti-Pattern 2: Missing File Paths

**Bad**:
```
Expected Output:
  - Authentication service implementation
  - Unit tests
```

**Why it fails**: Where should these go? What filename? Agent doesn't know.

**Good**:
```
Expected Output:
  Files to Create:
    - src/services/AuthService.ts
    - src/services/__tests__/AuthService.test.ts
```

---

### Anti-Pattern 3: No Boundary Conditions

**Bad**:
```
Objective: Implement user management
```

**Why it fails**: Does this include: signup? password reset? email verification? profile editing? role-based access? All of it? None of it?

**Good**:
```
Objective: Implement user profile editing (name, email, avatar)

Do NOT Implement:
  - User signup/registration (separate epic)
  - Password reset (separate task T-1.2.1)
  - Email verification (handled by backend)
  - Role management (separate task)
  - Account deletion (separate task)
```

---

### Anti-Pattern 4: Acceptance Criteria Without Given/When/Then

**Bad**:
```
AC: Should handle errors gracefully
AC: Should be performant
AC: Must work on mobile
```

**Why it fails**: How do you test "gracefully"? What's "performant"? How do you know you're done?

**Good**:
```
AC: Given invalid email, when user submits, then error "Invalid email format" appears below field
AC: Given valid form, when user submits, then API call completes within 2 seconds
AC: Given mobile viewport (375px), when page loads, then form fits without horizontal scroll
```

---

### Anti-Pattern 5: Overspecifying Implementation Details

**Bad**:
```
Use FastAPI with Pydantic models, configure CORS with allow_origins=["*"],
implement rate limiting with 100 requests per minute, use PostgreSQL with
async-pg, set connection pool size to 20...
```

**Why it fails**: This over-constrains how the task is completed and may be wrong. Is `allow_origins=["*"]` a security requirement or an implementation detail?

**Good**:
```
Tech Stack:
  - FastAPI
  - PostgreSQL
  - Pydantic for validation

Technical Requirements:
  - Performance: handle 100 concurrent requests
  - Security: CORS restrict to whitelisted domains (see config/cors.json)
  - Database: connection pooling configured (see DATABASE_POOL_SIZE env var)

Implementation is flexible as long as requirements are met.
```

---

### Anti-Pattern 6: Task Lacks Testing Approach

**Bad**:
```
Acceptance Criteria:
  - Component renders correctly
  - User can click button
  - Data is saved
```

**Why it fails**: "Renders correctly" - how do you verify? Manual inspection? Automated test? Screenshot comparison?

**Good**:
```
Acceptance Criteria:
  - Component renders: vitest + React Testing Library, element present in DOM
  - Button is clickable: test clicks button, verifies onClick handler called
  - Data is saved: test submits form, verifies POST request sent to /api/data with correct payload

Verification:
  Command: npm run test -- Component.test.tsx
  Expected: All tests pass, >80% coverage
  Manual: Use component in browser, verify button responds to clicks
```

---

### Anti-Pattern 7: Hidden Dependencies

**Bad**:
```
Task: Implement payment processing

Inputs:
  [none listed]
```

**Why it fails**: But the task obviously depends on an existing payment gateway account, API documentation, test credentials. These are hidden assumptions.

**Good**:
```
Task: Implement payment processing

Inputs:
  Dependencies:
    Hard:
      - T-INFRA-2.1: Configure Stripe account and API keys (needed for client_secret)
      - T-2.1.2: Create PaymentModel and database schema (needed for persistence)

  Required Files:
    - .env.local with STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
    - Stripe documentation and test card numbers

  From PRD:
    - REQ-021: Support Visa, Mastercard, Amex
    - REQ-022: Process refunds within 24 hours
```

---

### Anti-Pattern 8: Scope Creep Invitation

**Bad**:
```
Objective: Build the entire checkout experience

Includes:
  - Shopping cart review
  - Shipping address entry
  - Payment method selection
  - Order confirmation
  - Email receipt
  - Post-purchase recommendations
  - Inventory deduction
  - Analytics tracking
```

**Why it fails**: This is 5-6 tasks crammed into one. Will take 4000+ tokens to execute.

**Good**:
```
Objective: Create ShippingAddressForm component for collecting delivery address

Do NOT Implement:
  - Payment method UI (separate task T-1.2.2)
  - Order confirmation page (separate task T-1.3.1)
  - Email receipts (backend task T-2.2.1)
  - Analytics tracking (separate cross-cutting task)
  - Inventory deduction (backend task)
```

---

## Mapping PRD Requirements to Task Acceptance Criteria

Requirements from the normalized PRD are traced through decomposition and end up as acceptance criteria.

### The Traceability Chain

```
PRD Requirement
    ↓
  Epic
    ↓
  Feature
    ↓
  Task Acceptance Criteria
```

### Example Traceability

**PRD**:
```
REQ-015: "System must support OAuth 2.0 authentication with Google and GitHub
          and maintain user sessions for 30 days or until logout"
```

**Epic E-1 (Frontend — User Authentication)**:
```
Maps to: User can authenticate via OAuth providers and stay logged in
```

**Feature F-1.2 (OAuth Provider Selection)**:
```
Maps to: User selects and authenticates with OAuth provider (Google or GitHub)
```

**Task T-1.2.1** (Create OAuthProviderButtons component):
```
Acceptance Criteria:
  ✓ Component renders two buttons: "Login with Google", "Login with GitHub"
  ✓ Clicking button redirects to /auth/oauth?provider=google (or github)
  ✓ Buttons styled consistently with design system
  ✓ No sensitive data in client code (secrets handled by backend)
```

**Task T-2.1.4** (Implement OAuth authorization flow):
```
Acceptance Criteria:
  ✓ GET /auth/oauth/:provider initiates OAuth flow with provider
  ✓ On successful auth, creates session with 30-day expiry
  ✓ Session stored in httpOnly cookie (not localStorage)
  ✓ Session invalidated on logout
  ✓ Test: verify session expires after 30 days
```

### The Traceability Document

Each task should reference its source requirements:

```yaml
Task: T-1.2.1 Create OAuthProviderButtons component

Inputs:
  From PRD:
    - REQ-015: Must support OAuth 2.0 with Google and GitHub
    - REQ-016: Auth must be responsive and clear

Acceptance Criteria:
  [Each AC maps back to PRD requirement]

Verification:
  [How each REQ is validated through this task]
```

## Task Specification Template

Use this as a starting point for every task:

```yaml
###############################################################################
# TASK HEADER
###############################################################################

Task ID: T-{epic}.{feature}.{task}
Title: [Action Verb] [Object]
Epic ID: E-{number}
Feature ID: F-{number}.{number}

###############################################################################
# OBJECTIVE
###############################################################################

Objective: |
  [Clear, specific, measurable statement of what will be built]

###############################################################################
# CONTEXT
###############################################################################

Context: |
  [Project background, tech stack, architecture, conventions]

###############################################################################
# INPUTS
###############################################################################

Inputs:
  Dependencies:
    Hard:
      - [prerequisite task IDs and reasons]
    Soft:
      - [preferred task IDs and reasons]

  Required Files:
    - [specific file paths needed as input]

  From PRD:
    - [requirement IDs this task satisfies]

###############################################################################
# EXPECTED OUTPUT
###############################################################################

Expected Output:
  Files to Create:
    - [exact file paths]

  Files to Modify:
    - [exact file paths and sections]

  Format & Language:
    - [technology stack, language, framework]

  Size Estimate:
    - [lines of code, token estimate]

###############################################################################
# TECHNICAL REQUIREMENTS
###############################################################################

Technical Requirements:
  Stack:
    - [specific technologies and versions]

  Design Patterns:
    - [patterns to follow]

  Performance:
    - [performance constraints]

  Security:
    - [security requirements]

  Accessibility:
    - [a11y requirements]

###############################################################################
# BOUNDARY CONDITIONS
###############################################################################

Boundary Conditions:
  Do NOT Implement:
    - [list of out-of-scope items]

  Do NOT Modify:
    - [files owned by other tasks]

  Assumptions:
    - [what can be assumed about other tasks/systems]

###############################################################################
# ACCEPTANCE CRITERIA
###############################################################################

Acceptance Criteria:
  Functionality:
    ✓ [Given/When/Then or objective statement]
    ✓ [test case]
    ✓ [test case]

  Code Quality:
    ✓ [syntax, linting, formatting]

  Testing:
    ✓ [unit tests, coverage requirement]

  Integration:
    ✓ [how it connects to other tasks]

###############################################################################
# VERIFICATION
###############################################################################

Verification:
  Syntax Verification:
    Command: [command to run]
    Expected: [expected output]

  Unit Testing:
    Command: [command to run tests]
    Expected: [expected output]

  Functional Testing:
    [steps to verify manually]

  Integration Testing:
    [steps to verify works with adjacent tasks]

###############################################################################
# DEPENDENCIES
###############################################################################

Prerequisite Tasks:
  - [tasks that must complete first]

Tasks Blocked by This:
  - [tasks that depend on this completing]

Critical Path Impact: [ ] Yes  [ ] No

###############################################################################
# NOTES
###############################################################################

Notes:
  - [any additional context or gotchas]

References:
  - [links to relevant PRD sections, docs, design]
```

## Task Specification Quality Checklist

Before a task is considered ready for execution, verify:

- [ ] Task ID follows naming convention: T-{epic}.{feature}.{task}
- [ ] Title is action verb + object (not vague)
- [ ] Objective is specific and measurable (could be tested by machine)
- [ ] All required files listed with exact paths
- [ ] All dependencies enumerated (hard and soft)
- [ ] Boundary conditions explicitly stated ("Do NOT...")
- [ ] Acceptance criteria are binary testable (Given/When/Then or equivalent)
- [ ] No ambiguous language ("good", "appropriate", "fast", "user-friendly")
- [ ] Tech stack is specified (no undefined frameworks)
- [ ] Verification approach is clear (specific commands, expected output)
- [ ] Task is scoped to 2000-4000 tokens (junior engineer test)
- [ ] No questions would be asked by agent reading this spec
- [ ] Rubric score ≥4.0 across all five dimensions
- [ ] Traceability: clear path from PRD requirements to AC
- [ ] No hidden dependencies or assumptions
- [ ] Interdependencies with other tasks are minimal
- [ ] Code review criteria are clear

## Conclusion

A well-written task specification is a contract between the task creator and the task executor (the Claude agent). It promises that:

1. The task is clear and unambiguous
2. The task is completable in one session
3. Completion can be objectively verified
4. The task won't require unexpected scope expansion
5. The agent has all necessary context and inputs

When task specs meet these standards, execution is reliable and independent — multiple agents can work on multiple tasks in parallel without coordination overhead.
