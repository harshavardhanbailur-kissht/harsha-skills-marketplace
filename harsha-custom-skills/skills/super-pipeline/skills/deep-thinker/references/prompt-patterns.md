# Prompt Patterns Reference

Reasoning patterns for deep analysis and structured problem-solving.

## Table of Contents
- [Multi-Expert Simulation](#multi-expert-simulation)
- [ReAct Pattern](#react-pattern)
- [Chain-of-Thought](#chain-of-thought)
- [Tree of Thoughts](#tree-of-thoughts)
- [Plan-and-Execute](#plan-and-execute)
- [Constraint Satisfaction Analysis](#constraint-satisfaction-analysis)
- [Thinking Budget Management](#thinking-budget-management)

---

## Multi-Expert Simulation

Simulate a panel of experts with different specializations to get comprehensive analysis.

### Structure

```
EXPERT PANEL ANALYSIS: [TOPIC]

EXPERT A (Specialization):
[Analysis from this perspective]
Key concerns: [...]
Recommendations: [...]

EXPERT B (Specialization):
[Analysis from this perspective]
Key concerns: [...]
Recommendations: [...]

EXPERT C (Specialization):
[Analysis from this perspective]
Key concerns: [...]
Recommendations: [...]

PANEL DISCUSSION:
- Agreement points: [...]
- Disagreement points: [...]
- Resolution: [...]

SYNTHESIZED RECOMMENDATION:
[Combined insight from all experts]
```

### When to Use

- Complex features requiring multiple perspectives
- Architectural decisions with trade-offs
- Security-sensitive implementations
- User-facing features needing UX consideration
- Performance-critical code paths

### Multi-Expert Prompt Template

```markdown
## Analysis Request

### Feature/Problem
{{FEATURE_DESCRIPTION}}

### Expert Panel
Simulate three senior engineers analyzing this problem:

**BACKEND SPECIALIST**
Focus on: API design, data models, scalability, database interactions
Questions to address:
- How should data flow through the system?
- What are the performance implications?
- How does this integrate with existing services?

**FRONTEND/UX SPECIALIST**
Focus on: User experience, component design, state management, accessibility
Questions to address:
- How will users interact with this?
- What are all the UI states (loading, error, success)?
- How does this work on mobile vs desktop?

**SECURITY/RELIABILITY SPECIALIST**
Focus on: Attack vectors, data validation, error handling, edge cases
Questions to address:
- What could go wrong?
- How can this be abused?
- What are the failure modes?

### Panel Discussion
After individual analysis, the experts should:
1. Challenge each other's assumptions
2. Identify blind spots
3. Reach consensus on approach

### Output
Document the synthesized recommendation with rationale.
```

### Example: Mobile Login Feature

```
EXPERT PANEL ANALYSIS: Add Phone Number Login

BACKEND SPECIALIST:
- Need new endpoint: POST /auth/send-otp accepting {identifier, type}
- Phone validation requires E.164 format server-side
- SMS provider integration (Twilio/Vonage) needed
- Rate limiting: 3 per phone per 10 minutes (SMS costs more than email)
- Concerns: SMS delivery latency varies by carrier

FRONTEND/UX SPECIALIST:
- Country code selector needed (reuse existing CountrySelect?)
- Phone input mask for better UX: "+1 (___) ___-____"
- Default country from navigator.locale
- Tab vs toggle vs link for email/phone switch?
- Concerns: Form validation feedback timing

SECURITY SPECIALIST:
- Phone enumeration attack vector (rate limit strictly)
- SMS interception risk (consider backup codes)
- International phone format validation critical
- Concerns: Bot/spam abuse of SMS endpoint

PANEL DISCUSSION:
- Agreement: Need strict rate limiting, E.164 validation
- Disagreement: UI approach (tabs vs link)
- Resolution: Use "Use phone instead" link (less prominent, email preferred)

SYNTHESIZED RECOMMENDATION:
Implement phone login as secondary option with strict rate limiting,
country-aware input with E.164 validation, and clear error states.
```

### Specialized Expert Panels

**For API Design:**
- API Design Expert
- Client Integration Expert
- Documentation Expert

**For Data Migration:**
- Database Expert
- Data Integrity Expert
- Rollback Strategy Expert

**For Performance:**
- Frontend Performance Expert
- Backend Optimization Expert
- Infrastructure/Caching Expert

---

## ReAct Pattern

ReAct (Reasoning + Acting) interleaves thinking with tool exploration.

### Structure

```
Thought: [Reason about current situation and what to do next]
Action: [The specific action/tool to call]
Action Input: [Parameters for the action]
Observation: [Result from the action]
... (repeat until solved)
Thought: [Final reasoning]
Answer: [Final answer or result]
```

### When to Use

- Tasks requiring external tool interaction
- Information retrieval and verification
- Iterative refinement based on feedback
- Multi-step procedures with checkpoints

### ReAct Prompt Template

```markdown
## Task
{{TASK_DESCRIPTION}}

## Instructions
Work through this task step by step, alternating between thinking and acting.

For each step:
1. **Thought**: Reason about what you know and what you need to do next
2. **Action**: Choose an action (tool call, code execution, etc.)
3. **Observation**: Note the result of your action
4. **Repeat** until the task is complete

## Available Actions
- read_file: Read contents of a file
- write_file: Write content to a file
- run_command: Execute a shell command
- search: Search for information

## Begin
Thought: Let me analyze this task...
```

### Example

```
Thought: I need to fix the bug in auth.py. First, let me read the file.
Action: read_file
Action Input: {"path": "src/auth.py"}
Observation: [File contents showing login function]

Thought: I see the issue - line 45 doesn't handle null email.
Action: write_file
Action Input: {"path": "src/auth.py", "content": "...fixed code..."}
Observation: File written successfully.

Thought: Let me verify the fix by running tests.
Action: run_command
Action Input: {"command": "pytest test_auth.py"}
Observation: All tests passed.

Thought: The bug is fixed and verified.
Answer: Fixed null email handling in auth.py. All tests pass.
```

---

## Chain-of-Thought

CoT guides structured multi-step reasoning before reaching conclusions.

### Structure

```
<thinking>
Step 1: [First reasoning step]
Step 2: [Second reasoning step]
...
Step N: [Final reasoning step]
</thinking>

<answer>
[Conclusion based on reasoning]
</answer>
```

### When to Use

- Complex problems requiring multiple reasoning steps
- Mathematical or logical analysis
- Decisions with multiple factors
- Debugging and root cause analysis

### CoT Prompt Template

```markdown
## Problem
{{PROBLEM_DESCRIPTION}}

## Instructions
Think through this step by step before providing your answer.

Structure your response as:
1. Break down the problem into components
2. Analyze each component
3. Synthesize findings
4. Reach a conclusion

<thinking>
[Your step-by-step reasoning here]
</thinking>

<answer>
[Your final answer]
</answer>
```

### Zero-Shot CoT

Simply append "Let's think step by step" to any prompt:

```
Q: {{QUESTION}}

Let's think step by step.
```

This simple addition improves accuracy on reasoning tasks by 10-40%.

---

## Tree of Thoughts

ToT explores multiple reasoning paths, enabling backtracking and evaluation.

### Structure

```
Root Problem
├── Branch A: [Approach 1]
│   ├── Evaluation: [Score/Assessment]
│   └── Continue? [Yes/No]
├── Branch B: [Approach 2]
│   ├── Evaluation: [Score/Assessment]
│   └── Continue? [Yes/No]
└── Branch C: [Approach 3]
    ├── Evaluation: [Score/Assessment]
    └── Continue? [Yes/No]

Selected: Branch [X]
Final Solution: [...]
```

### When to Use

- Problems with multiple valid approaches
- Strategic planning with lookahead needed
- High-stakes decisions worth extra computation
- Creative problem-solving

**Note**: ToT uses significantly more tokens. Reserve for complex problems.

### ToT Prompt Template

```markdown
## Problem
{{PROBLEM_DESCRIPTION}}

## Instructions
Explore multiple approaches before committing to a solution.

### Phase 1: Generate Approaches
List 3 different ways to solve this problem:
1. [Approach A]
2. [Approach B]
3. [Approach C]

### Phase 2: Evaluate Each
For each approach, score on:
- Feasibility (1-10)
- Quality of outcome (1-10)
- Risk level (1-10, lower is better)

### Phase 3: Select and Execute
Choose the best approach and implement it.

If you hit a dead end, backtrack and try the next best approach.
```

---

## Plan-and-Execute

Separate planning from execution for complex multi-step tasks.

### Structure

```
## Planning Phase
Goal: [Ultimate goal]
Constraints: [Limitations]

Plan:
1. [Step 1] → Expected outcome: [...]
2. [Step 2] → Expected outcome: [...]
3. [Step 3] → Expected outcome: [...]

## Execution Phase
Step 1: [Execute] → Actual: [...] ✓/✗
Step 2: [Execute] → Actual: [...] ✓/✗
...

## Replan if Needed
[Adjust plan based on actual results]
```

### When to Use

- Multi-step projects
- Tasks where order matters
- When upfront planning saves time
- Coordinating across skills

### Plan-and-Execute Template

```markdown
## Goal
{{GOAL_DESCRIPTION}}

## Phase 1: Planning
Before taking any action, create a complete plan.

### Constraints
- {{Constraint 1}}
- {{Constraint 2}}

### Plan
| Step | Action | Expected Result | Dependencies |
|------|--------|-----------------|--------------|
| 1 | {{action}} | {{result}} | None |
| 2 | {{action}} | {{result}} | Step 1 |
| ... | ... | ... | ... |

### Risk Assessment
- What could go wrong?
- What's the fallback?

## Phase 2: Execution
Execute each step, noting actual vs expected results.

## Phase 3: Verification
Confirm all steps succeeded and goal is achieved.
```

---

## Constraint Satisfaction Analysis

Identify and document all constraints before designing solutions.

### Structure

```
CONSTRAINT ANALYSIS: [FEATURE]

HARD CONSTRAINTS (must satisfy):
- [ ] Constraint 1: [Description] | Verification: [How to check]
- [ ] Constraint 2: [Description] | Verification: [How to check]

SOFT CONSTRAINTS (should satisfy):
- [ ] Constraint 1: [Description] | Priority: [High/Medium/Low]
- [ ] Constraint 2: [Description] | Priority: [High/Medium/Low]

CONSTRAINT CONFLICTS:
- Conflict: [Constraint A] vs [Constraint B]
- Resolution: [How to handle]

DESIGN IMPLICATIONS:
- Because of [Constraint X], we must [Design Decision]
```

### When to Use

- Features with technical requirements
- Compliance-sensitive implementations
- Performance-critical features
- Accessibility requirements
- Backwards compatibility needs

### Constraint Satisfaction Template

```markdown
## Constraint Analysis: {{FEATURE}}

### Hard Constraints (Non-Negotiable)

| Constraint | Source | Verification |
|------------|--------|--------------|
| Must work offline | Product requirement | Test with network disabled |
| < 100ms response time | SLA | Performance benchmark |
| WCAG AA compliant | Legal requirement | Accessibility audit |
| Backwards compatible | Existing users | Integration tests pass |

### Soft Constraints (Desirable)

| Constraint | Priority | Trade-off |
|------------|----------|-----------|
| Reuse existing components | High | May limit design flexibility |
| Match current code style | Medium | Some refactoring OK |
| Minimize bundle size | Medium | Performance vs features |

### Constraint Conflicts

| Conflict | Resolution |
|----------|------------|
| Offline support vs real-time sync | Queue updates, sync when online |
| Rich animations vs performance | Use CSS transforms, limit particles |

### Design Decisions from Constraints

Based on constraint analysis:
1. **Architecture**: [Decision because of Constraint X]
2. **Technology**: [Decision because of Constraint Y]
3. **Scope**: [Decision because of Constraint Z]
```

### Example: Search Feature

```
CONSTRAINT ANALYSIS: Full-Text Search

HARD CONSTRAINTS:
- [x] Must search within 500ms (UX requirement)
- [x] Must support 10M+ records (data scale)
- [x] Must handle partial matches (user expectation)
- [x] No external services (infrastructure constraint)

SOFT CONSTRAINTS:
- [ ] Fuzzy matching for typos (Priority: High)
- [ ] Highlight matches in results (Priority: Medium)
- [ ] Search history (Priority: Low)

CONSTRAINT CONFLICTS:
- Conflict: 500ms latency vs 10M records without external services
- Resolution: Pre-compute search index, use client-side filtering for < 1000 results

DESIGN IMPLICATIONS:
- Must use in-memory search index (no Elasticsearch allowed)
- Need background indexing job for large datasets
- Consider pagination + server search for > 1000 results
```

---

## Thinking Budget Management

### Claude Code Thinking Triggers

Use these magic words to control thinking budget:

| Trigger | Budget | When to Use |
|---------|--------|-------------|
| "think" | Low | Simple tasks |
| "think hard" | Medium | Moderate complexity |
| "think harder" | High | Complex problems |
| "ultrathink" | Maximum (31,999 tokens) | Very complex analysis |

### Usage Examples

```markdown
# Low budget
Please think about how to fix this typo.

# Medium budget  
Think hard about the architecture for this feature.

# High budget
Think harder about potential security vulnerabilities.

# Maximum budget
Ultrathink: Analyze this complex system design and identify 
all potential failure modes, scalability issues, and 
optimization opportunities.
```

### When to Use Extended Thinking

**Use high budget for**:
- Architectural decisions
- Security analysis
- Complex debugging
- Multi-factor tradeoff analysis
- Strategic planning

**Avoid high budget for**:
- Simple tasks
- Clear requirements
- Well-defined procedures
- Time-sensitive operations

### Structured Thinking Request

```markdown
## Complex Analysis Request

I need you to deeply analyze this problem. Use extended thinking.

### Context
{{CONTEXT}}

### Question
{{QUESTION}}

### Analysis Requirements
1. Consider multiple perspectives
2. Identify edge cases
3. Evaluate tradeoffs
4. Provide confidence levels

### Output Format
<thinking>
[Deep analysis with multiple angles]
</thinking>

<recommendation>
[Final recommendation with rationale]
Confidence: [X]%
</recommendation>
```

---

## Pattern Selection Guide

| Situation | Pattern | Reason |
|-----------|---------|--------|
| Multiple perspectives needed | Multi-Expert | Get comprehensive analysis |
| Tool exploration needed | ReAct | Interleave reasoning with exploration |
| Complex reasoning | CoT | Structure thought process |
| Multiple approaches | ToT | Explore and compare options |
| Multi-step analysis | Plan-Execute | Separate planning from analysis |
| Technical requirements | Constraint Analysis | Ensure all constraints met |
| High complexity | Extended Thinking | More computation budget |

### Combining Patterns

For comprehensive analysis, combine patterns:

```
1. Multi-Expert → Get multiple perspectives
2. Constraint Analysis → Document requirements
3. ToT → Explore approaches
4. CoT → Deep-dive on selected approach
5. Plan-Execute → Structure implementation plan
```

Example:

```markdown
## Comprehensive Feature Analysis

### Phase 1: Expert Perspectives (Multi-Expert)
Simulate backend, frontend, and security experts analyzing this...

### Phase 2: Identify Constraints (Constraint Analysis)
Document hard and soft constraints...

### Phase 3: Explore Options (ToT)
Consider 3 architectural approaches...

### Phase 4: Analyze Selected (CoT)
Think through the chosen approach step by step...

### Phase 5: Plan Implementation (Plan-Execute)
Create detailed implementation plan for executor session...

### Output: .deep-think/ Files
Write all analysis to persistent files for executor session.
```
