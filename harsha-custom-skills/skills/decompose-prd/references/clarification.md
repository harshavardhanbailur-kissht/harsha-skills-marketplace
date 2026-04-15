# Clarification & Ambiguity Resolution

## Why Clarification Matters

Ambiguity in PRDs is the #1 source of multi-agent failure. According to MAST FM-2.6 research, reasoning-action mismatch causes **13.2% of all multi-agent task failures**. Most of these mismatches stem from teams making different assumptions about the same ambiguous requirement.

When a PRD says "the system should be fast" without defining what "fast" means, different engineers will implement different solutions:
- One team optimizes for response time (100ms SLA)
- Another optimizes for throughput (1000 req/sec)
- A third assumes "fast" means "faster than competitor X"

All three implementations are technically correct, but incompatible. The resulting decomposed tasks will be incoherent.

**Prevention is cheaper than rework.** By identifying and resolving ambiguities upfront during decomposition, we prevent weeks of rework downstream.

## Ambiguity Classification Taxonomy

Ambiguities fall into six distinct categories, each requiring different questioning approaches:

### 1. SCOPE Ambiguity
**Definition:** Uncertainty about whether something is in or out of the current PRD.

**Indicators:**
- "May also support X in the future"
- "If time permits, add feature Y"
- "Similar to competitor Z" (which aspect?)
- Missing explicit exclusions ("This doesn't include admin panel" vs silence about it)
- Feature descriptions that reference related features without clear boundaries

**Example:**
```
PRD: "Build user dashboard with data visualization"
Questions:
- Does "data visualization" include real-time charts or just static tables?
- Can users export data, or only view it?
- Is admin analytics dashboard in scope, or is this user-facing only?
```

### 2. TECHNICAL Ambiguity
**Definition:** Uncertainty about which technology, architecture pattern, or implementation approach to use.

**Indicators:**
- "Scalable database solution" (SQL? NoSQL? Graph DB?)
- "RESTful API" (v1? v2? Pagination strategy?)
- "Microservices architecture" (function-per-feature or domain-driven?)
- "Mobile app" (native? cross-platform framework? Which one?)
- No architecture decisions documented

**Example:**
```
PRD: "Support real-time user presence notifications"
Questions:
- WebSocket vs Server-Sent Events vs polling?
- Redis pub/sub vs message queue vs database polling?
- Push notifications or in-app only?
```

### 3. PRIORITY Ambiguity
**Definition:** Uncertainty about which features are MVP vs nice-to-have, or which comes first.

**Indicators:**
- "All features are equally important"
- Multiple unordered feature lists
- No clear MVP definition
- "Phase 2" mentioned without MVP/Phase 1 clarity
- Vague launch criteria

**Example:**
```
PRD lists 8 features:
- User auth
- Email notifications
- SMS notifications
- Push notifications
- File uploads
- Advanced search
- Analytics dashboard
- Admin panel

Question: Which are MVP for launch, and what's the Phase 2 plan?
```

### 4. DEPENDENCY Ambiguity
**Definition:** Uncertainty about whether feature A needs feature B to function, or if they can be developed in parallel.

**Indicators:**
- "Integration with external X" (hard or soft dependency?)
- "Requires feature Y" (truly blocking or just preferred?)
- No dependency diagram
- Circular references ("A needs B, B needs A")
- Conditional dependencies ("If platform is iOS, then feature X is needed")

**Example:**
```
PRD: "Build notification system with email, SMS, push"
Questions:
- Is the notification preference center required before launch, or can we hard-code defaults?
- Does SMS require carrier partnerships (external dependency)?
- Can we launch with email-only, then add SMS/push in Phase 2?
```

### 5. METRIC Ambiguity
**Definition:** Uncertainty about how to measure success for a requirement.

**Indicators:**
- "Improve user engagement" (by what %)
- "Fast performance" (no SLA specified)
- "Scalable system" (to what scale?)
- "Reliable service" (uptime target? RTO/RPO?)
- Success metrics missing entirely

**Example:**
```
PRD: "Reduce customer support load with self-service FAQ"
Questions:
- Success metric: reduce tickets by X%? Deflection rate?
- SLA on FAQ search response time?
- Target: 80% of common questions answered?
```

### 6. STAKEHOLDER Ambiguity
**Definition:** Uncertainty about who the user/approver is or what they value.

**Indicators:**
- Multiple personas mentioned without clear primary user
- No stakeholder approval matrix
- "Users want X" (which users? All segments?)
- Feature requirements from stakeholders without prioritization
- No definition of "done" or sign-off criteria

**Example:**
```
PRD: "Build reporting dashboard"
Questions:
- Primary users: executives, managers, or analysts?
- Does each user role need different views?
- Who approves the dashboard design?
```

## Ambiguity Detection Heuristics

### Pattern 1: Vague Adjectives
**Red flags:** "fast", "scalable", "user-friendly", "robust", "efficient", "intuitive", "elegant"

These words are opinion-laden and mean different things to different people.

**Detection strategy:** Search for common vague words and flag them.

**Resolution pattern:**
```
Vague: "The system should be scalable"
Clarified: "Scale to handle 1M daily active users with <100ms response time"
```

### Pattern 2: Missing Quantifiers
**Red flags:** "support multiple X", "handle large Y", "support many Z", "reasonable limits"

**Detection strategy:** Find requirements that use relative terms without absolute thresholds.

**Resolution pattern:**
```
Vague: "Support multiple file formats for imports"
Clarified: "Initially support CSV, JSON, XML. Extensible for others?"
```

### Pattern 3: Implied Requirements
**Red flags:** "like competitor Y", "similar to X", "industry standard", "best practice"

These require the reader to have knowledge they may not have.

**Detection strategy:** Find all comparative references and call them out.

**Resolution pattern:**
```
Vague: "Notification system similar to Slack"
Clarified: "Does this mean: threading? Reactions? Mention notifications? All three?"
```

### Pattern 4: Contradictory Requirements
**Red flags:** Feature A requires X, but Feature B requires not-X.

**Detection strategy:** Extract implications of each feature and check for contradictions.

**Example:**
```
Feature A: "Support real-time synchronization across 10 devices"
Feature B: "Offline-first, minimizing server communication"
Contradiction: Real-time sync with many devices requires constant server communication.
Resolution: Which takes priority? Or do we need selective sync?
```

### Pattern 5: Missing Sections
**Red flags:** Complete PRD structure with conspicuous gaps.

**Common missing sections:**
- No security requirements mentioned
- No performance targets defined
- No compliance/regulatory requirements
- No disaster recovery/business continuity plans
- No rollback strategy for features
- No monitoring/observability requirements

**Detection strategy:** Use a checklist of expected sections.

## Question Generation Patterns

### Pattern 1: Scope Questions
**Template:**
```
"The PRD mentions [X] but doesn't specify if [Y] is included.
Should [Y] be in scope for this implementation, or is it out of scope?"
```

**Concrete example:**
```
"The PRD mentions user authentication but doesn't specify if social login is included.
Should social login (Google, GitHub, Apple) be in scope for this implementation?
Options:
- Yes, all three (Google, GitHub, Apple)
- Yes, but only Google
- No, username/password only
- Other"
```

### Pattern 2: Technical Decision Questions
**Template:**
```
"The PRD requires [feature] but doesn't specify the implementation approach.
Which direction should we take?"
```

**Concrete example:**
```
"The PRD requires real-time notifications but doesn't specify the technology.
Which approach should we use?
Options:
- WebSocket for persistent connections
- Server-Sent Events (SSE) for server→client streaming
- Polling every X seconds
- Push notifications (FCM, APNs)
- Other"
```

### Pattern 3: Priority/Phasing Questions
**Template:**
```
"The PRD lists [N] features but doesn't prioritize them clearly.
For launch, which should be MVP and which should be Phase 2?"
```

**Concrete example:**
```
"The PRD lists 5 notification channels: email, SMS, push, Slack, webhook.
For MVP launch, which are essential and which can wait for Phase 2?
Options:
- Email + push (most platforms support)
- Email only (safest, lowest risk)
- All 5 (highest ambition)
- Custom: [you specify]"
```

### Pattern 4: Dependency Questions
**Template:**
```
"Feature [A] seems to depend on feature [B].
Is [B] a hard blocker for [A], or can they be developed in parallel?"
```

**Concrete example:**
```
"The notifications feature depends on user preferences (where users choose channels).
Is the preference center a hard requirement for launch, or can we:
Options:
- Hard blocker: both launch together
- Soft: launch with hard-coded defaults, build UI in Phase 2
- Soft: launch with basic defaults, iterate
- Other"
```

### Pattern 5: Metric/Success Questions
**Template:**
```
"The requirement [X] doesn't define success criteria.
How will we measure if [X] is working?"
```

**Concrete example:**
```
"The PRD says 'improve user engagement with notifications.'
How do we measure success?
Options:
- Engagement increase of 20%+ (specific metric: DAU? Session length? Feature usage?)
- Notification delivery rate >99%
- User satisfaction >4.5/5
- Custom metric: [you specify]"
```

## Using AskUserQuestion Tool Effectively

### Grouping Strategy
Group related questions but don't exceed **4 questions per tool call**. Cognitive load matters.

**Good grouping:**
```
Call 1: Scope questions (3 questions about what's in/out)
Call 2: Technical decisions (2 questions about architecture)
Call 3: Priority/phasing (2 questions about MVP vs Phase 2)
```

**Bad grouping:**
```
Call 1: 8 random questions about everything
(User will get overwhelmed and give inaccurate answers)
```

### Question Quality Standards

Each question should have **2-4 concrete options**:
- Too few options (only 2): yes/no questions that might miss nuance
- Too many options (5+): decision paralysis
- Always include "Other" or "Custom" for unexpected answers

**Good options:**
```
- Option A (concrete, specific)
- Option B (concrete, specific)
- Option C (concrete, specific)
- Other: [user describes their preference]
```

**Avoid:**
```
- Yes/No (too binary)
- "What would you prefer?" (open-ended, hard to process)
- "Our recommendation" (biases the answer)
```

### Front-Load High-Impact Questions
Ask questions in order of impact on decomposition:

1. **MVP vs Phase 2** (affects scope of all tasks)
2. **Major technical decisions** (affects task dependencies)
3. **Key integrations** (affects external dependencies)
4. **Specific success metrics** (affects acceptance criteria)
5. **Detailed ambiguities** (edge cases, nice-to-haves)

### Example: Effective Question Call
```
AskUserQuestion with:

1. "The PRD lists 8 notification types (email, SMS, push, Slack, webhook, Teams, Discord, custom HTTP).
   For MVP launch, which are required?
   - Email + push (essential)
   - All 8 (high ambition)
   - Email only (minimal)
   - Custom: [specify]"

2. "The PRD says notifications should be 'real-time'. Does this mean:
   - <100ms latency (strict real-time)
   - <1 second (practical real-time)
   - <5 seconds (eventual consistency)
   - Custom threshold: [specify]"

3. "For notification preferences, should users be able to:
   - Mute per-channel (email on, SMS off)
   - Mute per-notification-type (only marketing emails off)
   - Both
   - Only channel-level control"

4. "What's the external dependency situation:
   - We use SendGrid for email (already integrated)
   - We need to integrate new services (Twilio, FCM, etc.)
   - We'll use internal service (more work, more control)
   - Other"
```

## Decision Logging

Every clarification must be logged with:

1. **Question asked** - the exact ambiguity flagged
2. **Options provided** - what we proposed
3. **Decision made** - what the user/stakeholder chose
4. **Rationale** - why this decision matters
5. **Impact** - which decomposition elements depend on this

**Example log entry:**
```markdown
### Clarification: Real-time Notification Latency

**Question:** The PRD says "real-time notifications" but doesn't define latency SLA.

**Options provided:**
- <100ms (strict real-time, expensive)
- <1 second (practical real-time, moderate cost)
- <5 seconds (eventual consistency, low cost)

**Decision:** <1 second latency SLA

**Rationale:** Balances user experience (feels instantaneous) with implementation cost (no need for WebSocket infrastructure)

**Impact:**
- Technical approach: Server-Sent Events instead of WebSocket (saves ~2 weeks engineering)
- Database: Standard SQL sufficient (no need for real-time database)
- Tasks: T-3.2 (notification delivery) and T-3.3 (delivery verification) depend on this
```

## Confidence Scoring

Rate each decomposition decision using a three-level confidence scale:

### HIGH Confidence
**Criteria:** Explicitly stated in PRD with clear acceptance criteria

**Example:**
```
Requirement: "Support OAuth 2.0 with Google and GitHub providers"
Confidence: HIGH
Reasoning: Explicitly names which providers, clear technical standard (OAuth 2.0)
```

### MEDIUM Confidence
**Criteria:** Reasonably inferred from context but not explicitly stated

**Example:**
```
Requirement: "Users should be able to update their profile"
Inferred: Username, email, password, avatar, bio are editable
Confidence: MEDIUM
Reasoning: Standard profile fields are implied, but PRD doesn't explicitly list all fields
```

### LOW Confidence
**Criteria:** Assumption made due to ambiguity; flagged for review

**Example:**
```
Requirement: "Support multiple notification channels"
Assumption: Initially implement email, SMS, push; others in Phase 2
Confidence: LOW
Reasoning: PRD doesn't define which channels or phasing. This is an assumption that needs stakeholder confirmation.
Flag: Confirm with PM before assigning tasks
```

### Confidence Scoring in Decomposition Output

Include confidence scores at two levels:

**Task level:**
```markdown
## T-3.2: Email Notification Delivery

Status: Not Started
Effort: M
Confidence: HIGH ✓

**Why HIGH:** PRD explicitly requires "deliver notifications via email"
```

**Decision level:**
```markdown
## Implementation Decision: Queue Technology

Decision: Use Redis pub/sub for notification queue
Confidence: MEDIUM ⚠️

**Why MEDIUM:**
- Explicitly required: "queue-based notification delivery"
- Not specified: which queue technology (Redis, RabbitMQ, AWS SQS)
- We chose Redis based on existing infrastructure, but alternatives exist
- Recommendation: Validate with infrastructure team
```

## Handling Ambiguity Across Different Skill Phases

### During ANALYZE Phase
When you're reading the PRD for the first time:
- Mark all vague language
- List all missing sections
- Note all comparative references
- Flag all implied requirements

**Output:** Ambiguity list (~30-50 items for typical 20-page PRD)

### During CLARIFY Phase
When you're asking questions:
- Group by category (scope, technical, priority, etc.)
- Ask highest-impact questions first
- Limit to 4 questions per tool call
- Wait for user responses before asking follow-ups

**Output:** Clarification log with decisions

### During DECOMPOSE Phase
When you're building the task tree:
- Mark confidence levels on each task
- Trace dependencies back to clarifications
- Flag tasks that depend on LOW confidence decisions
- Call out contradictions if they emerge

**Output:** Task tree with confidence metadata

## Ambiguity Prevention: Checklists for Different PRD Types

### Feature PRD Checklist
- [ ] MVP definition clear (features in/out)?
- [ ] Success metrics defined (not just "improve X")?
- [ ] User roles/personas defined?
- [ ] External dependencies identified?
- [ ] Security/compliance requirements listed?
- [ ] Performance targets specified?
- [ ] Rollback/migration strategy?
- [ ] Monitoring/observability requirements?

### Technical PRD Checklist
- [ ] Architecture decisions explained?
- [ ] Technology choices justified?
- [ ] Scalability targets quantified?
- [ ] Performance SLAs defined?
- [ ] Testing strategy specified?
- [ ] Deployment approach detailed?
- [ ] Backward compatibility requirements?
- [ ] Observability/alerting strategy?

### Integration PRD Checklist
- [ ] External system behavior documented?
- [ ] Error handling scenarios specified?
- [ ] Retry/timeout policies defined?
- [ ] Data mapping fully specified?
- [ ] Authentication/authorization approach?
- [ ] Monitoring/alerting for integration?
- [ ] Fallback behavior if external system fails?
- [ ] Data consistency guarantees?

## When to Skip Clarification

**Note:** Not every ambiguity needs clarification. Use judgment.

**Skip if:**
- The ambiguity affects Phase 2+ work (out of scope for MVP)
- Reasonable defaults exist and low cost to change later
- Technical approach is flexible (multiple valid solutions)
- Not on critical path to launch

**Always clarify if:**
- Affects MVP scope or feature completeness
- Creates hard dependency between teams
- Impacts success metrics or acceptance criteria
- Is on critical path to launch
- Requires external dependencies (API keys, infrastructure, etc.)

## Summary

Clarification is the foundation of coherent task decomposition. By systematically identifying and resolving the six types of ambiguity (scope, technical, priority, dependency, metric, stakeholder), you prevent downstream rework and ensure all teams are solving the same problem.

**Key takeaway:** 30 minutes of clarification questions now saves weeks of rework later.
