# The Definitive Claude Sonnet 4.5 Prompting Reference

## SECTION 1: Model Characteristics & Capabilities

### Model Specifications
- **Model ID**: claude-sonnet-4-5-20250929
- **Release Date**: September 29, 2025
- **Context Window**: 200K tokens (standard), 1M tokens (beta)
- **Performance Tier**: Balanced speed and intelligence (faster than Opus, smarter than Haiku)
- **Extended Thinking**: Manual budget control, minimum 1024 tokens per request
- **Availability**: General availability, optimized for production workflows

### Core Behavioral Traits
1. **Literal Instruction Following**: Sonnet 4.5 interprets instructions precisely. What you say is what you get. It does not infer unstated requirements or add value beyond the specification.

2. **No Hidden Helpfulness**: Unlike earlier models, Sonnet 4.5 does not try to be "helpful" by doing things you didn't ask for. This is a feature—it means prompts are more predictable and reliable.

3. **Structured Thinking Capability**: When extended thinking is enabled, it reasons thoroughly through problems with explicit internal deliberation before responding. This internal reasoning is hidden from the user by default but improves output quality.

4. **Token Efficiency**: Produces concise outputs without unnecessary elaboration when not requested. Adds detail only when specifically asked.

5. **Constraint Respect**: Honors output format constraints, token limits, and structured requirements with high fidelity.

### Optimal Use Cases
- Production API workflows requiring consistent, predictable behavior
- Code generation and technical implementation
- Complex multi-step reasoning with extended thinking enabled
- Structured data extraction and transformation
- Research synthesis with clear output schemas
- Parallel agent orchestration in multi-agent systems
- Tasks requiring high instruction fidelity

### Performance Characteristics by Task Type
| Task Type | Latency | Quality | Cost | Best For |
|-----------|---------|---------|------|----------|
| Simple classification | 2-4s | Excellent | Low | Filtering, categorization |
| Code generation | 8-15s | Excellent | Medium | Implementation, debugging |
| Analysis & synthesis | 15-30s | Excellent | Medium | Research, summarization |
| Extended thinking (16K+) | 30-60s | Expert | High | Complex reasoning, planning |

---

## SECTION 2: The 10 Golden Rules of Sonnet 4.5 Prompting

### Rule 1: Be Explicit, Not Implicit
**Core Principle**: Sonnet 4.5 does exactly what you write, nothing more. Do not rely on inference or assumed context.

**Why It Matters**: Unlike humans, Sonnet 4.5 will not read between the lines. If you say "analyze this document," it may provide a surface-level analysis. If you say "analyze this document for security vulnerabilities, architectural weaknesses, and performance issues," it will be thorough in those three areas.

**Examples**:
- ❌ "Summarize this research paper"
- ✅ "Extract exactly three key findings from this research paper, each 1-2 sentences, focusing on methodology, results, and implications"

- ❌ "Write a function to process data"
- ✅ "Write a Python function that accepts a list of dictionaries, filters out entries with null values in the 'amount' field, and returns a sorted list by creation timestamp in descending order"

**Implementation**:
- Always specify the exact output format
- List all requirements explicitly
- Include scope boundaries
- Name what you want—don't assume it will be inferred

---

### Rule 2: Structure with XML Tags
**Core Principle**: Organize your prompts with semantic XML tags. This creates clarity in instruction parsing and enables better prompt composition.

**Why It Matters**: XML tags are semantic delimiters. They make your intentions machine-readable. Sonnet 4.5 (and all Claude models) parse XML-structured prompts with higher accuracy than unstructured prose.

**Standard Tag Set**:
```xml
<role_definition></role_definition>     <!-- Who is the model acting as? -->
<context></context>                     <!-- Background information -->
<task_description></task_description>   <!-- What needs to be done? -->
<input_data></input_data>               <!-- What data is provided? -->
<output_schema></output_schema>         <!-- What format should output take? -->
<constraints></constraints>             <!-- What are the limits/rules? -->
<examples></examples>                   <!-- Show format with examples -->
<anti_patterns></anti_patterns>         <!-- What NOT to do? -->
<success_criteria></success_criteria>   <!-- How do we measure success? -->
```

**Why Each Tag**:
- **role_definition**: Frames the model's expertise and perspective
- **context**: Provides necessary background without cluttering task description
- **task_description**: Crystal-clear objective statement
- **input_data**: Shows what will be provided
- **output_schema**: Defines exact output format (CRITICAL)
- **constraints**: Sets boundaries and rules
- **examples**: Demonstrates format and expectations
- **anti_patterns**: Prevents common mistakes
- **success_criteria**: Makes evaluation explicit

**Example Structure**:
```xml
<role_definition>
You are a senior software architect with 15 years of experience evaluating
architectural decisions in distributed systems. You assess tradeoffs between
consistency, availability, and partition tolerance.
</role_definition>

<context>
This company is migrating from a monolithic application to microservices.
They need to choose between event-driven architecture and request-response
based services for inter-service communication.
</context>

<task_description>
Compare event-driven and request-response architectures for this migration,
evaluating them across: consistency guarantees, operational complexity,
latency characteristics, and team skill requirements.
</task_description>

<input_data>
You will be provided with: current traffic patterns, team composition,
existing infrastructure, and SLA requirements.
</input_data>

<output_schema>
Return a JSON object with this exact structure:
{
  "recommendation": "event_driven|request_response",
  "confidence": 0.0-1.0,
  "pros": [{"architecture": "...", "pro": "...", "weight": 0.0-1.0}],
  "cons": [{"architecture": "...", "con": "...", "weight": 0.0-1.0}],
  "implementation_roadmap": [{"phase": int, "steps": [string], "duration_weeks": int}],
  "risks": [{"risk": "...", "mitigation": "..."}]
}
</output_schema>

<constraints>
- Respond ONLY with valid JSON
- Each pro/con must have a weight between 0 (minor) and 1 (critical)
- Recommendation must be justified by weighted comparison
- Assume team can learn new patterns within 3 months
- Budget for implementation: 6 months maximum
</constraints>

<anti_patterns>
- Do NOT recommend based on industry trends—base on their specific context
- Do NOT suggest both equally without commitment to one
- Do NOT ignore team skill constraints
- Do NOT propose architectural patterns that require 5+ new tools
</anti_patterns>

<success_criteria>
- Recommendation is backed by weighted pro/con analysis
- Each phase is actionable and achievable in stated timeframe
- Risks are identified and have mitigations
- Answer demonstrates understanding of their constraints
</success_criteria>
```

---

### Rule 3: Define Output Schema First
**Core Principle**: Always specify what you want BEFORE describing the task. Output format should appear early in the prompt.

**Why It Matters**: When the model knows the exact output format upfront, it structures its thinking to produce that format. This is more efficient than asking for a format retroactively.

**Approaches**:

1. **JSON Schema (Most Precise)**:
```xml
<output_schema>
Return a JSON array where each element conforms to this schema:
{
  "id": "string — unique identifier",
  "title": "string — descriptive title (max 100 chars)",
  "description": "string — detailed explanation (max 500 chars)",
  "confidence": "VERIFIED|HIGH|MEDIUM|LOW|UNKNOWN",
  "source": "string — where this information comes from",
  "related_ids": ["string"] — IDs of related entries
}

CRITICAL: Return ONLY the JSON array. No markdown code fences. No preamble or explanation.
</output_schema>
```

2. **Structured Markdown**:
```xml
<output_schema>
Return results in this format for each item:

## [Title]
- Confidence: [VERIFIED|HIGH|MEDIUM|LOW]
- Summary: [1-2 sentences]
- Key Points:
  * [Point 1]
  * [Point 2]
  * [Point 3]
- Sources: [comma-separated sources]
- Related Topics: [comma-separated topics]
</output_schema>
```

3. **Key-Value Structured Output**:
```xml
<output_schema>
For each finding, respond with exactly this structure:

FINDING: [Title]
CONFIDENCE: [VERIFIED|HIGH|MEDIUM|LOW]
EVIDENCE: [Supporting evidence, 1-3 sentences]
SOURCE: [Source URL or document]
IMPACT: [Why this matters, 1 sentence]
NEXT_STEPS: [What to investigate next, if applicable]
---
</output_schema>
```

**Critical Rule**: The more precisely you define format, the more reliable the output.

---

### Rule 4: Use Action Verbs
**Core Principle**: Use strong, specific verbs that describe exact actions, not general descriptions.

**Why It Matters**: Action verbs create commitment and specificity. They distinguish between "describe what you know" and "implement a working solution."

**Verb Comparison**:
| Weak | Strong |
|------|--------|
| Discuss approaches | Implement solution and explain tradeoffs |
| Suggest improvements | Identify and prioritize 5 specific improvements |
| Describe the process | Generate step-by-step procedure with estimated duration |
| Explain the concept | Teach the concept using 3 concrete examples |
| Find relevant information | Search and extract exactly 10 verified facts |
| Review the code | Identify security vulnerabilities and suggest fixes |
| Analyze the market | Identify 3 market opportunities and competitive positioning |
| Consider the impact | Quantify financial impact with conservative estimates |

**Implementation**:
```xml
<task_description>
✅ Implement a Python class that validates email addresses using SMTP verification
✅ Generate a test suite with 15 test cases covering edge cases
✅ Optimize the validation timeout to <2 seconds per address

❌ Create an email validation solution
❌ Write code to validate emails
❌ Think about how to check if emails are real
</task_description>
```

---

### Rule 5: Provide Context and Motivation
**Core Principle**: Explain WHY the task matters, not just WHAT needs to be done. Context improves reasoning quality.

**Why It Matters**: When the model understands the motivation and context, it makes better decisions about tradeoffs, scope, and approach. Context enables appropriate prioritization.

**What to Include**:
- **Problem Context**: What's the underlying problem?
- **Constraints**: What are the real-world limitations?
- **Success Criteria**: How will we know it worked?
- **Stakeholders**: Who uses this output? What are their needs?
- **Existing Approaches**: What's been tried before?
- **Failure Modes**: What would count as a bad solution?

**Example**:
```xml
<context>
We're building a machine learning system to automatically tag customer support tickets.
The current manual tagging process takes 3 hours per 100 tickets and has low consistency.

Stakeholders:
- Support team: Needs faster routing to specialists (SLA: 95% correct tag)
- ML platform team: Needs maintainable, explainable predictions
- Management: Wants cost savings and improved CSAT scores

Constraints:
- Model must run on CPU-only servers (no GPU budget)
- Latency budget: <500ms per ticket
- Can't access personally identifiable information
- Must support A/B testing new tags without retraining

Success criteria:
- F1-score ≥ 0.85 on validation set
- 90%+ ticket routing accuracy
- <200ms p95 latency
- Top 3 features are interpretable
- Can add new tags without full retrain

Previous attempts:
- Rule-based system: 60% accuracy, high maintenance
- Naive Bayes: 70% accuracy, too simplistic
- BERT fine-tuning: 92% accuracy, but 5GB model, CPU latency unacceptable
</context>
```

This context enables better reasoning about which approach to recommend.

---

### Rule 6: Leverage Extended Thinking for Complex Tasks
**Core Principle**: Enable extended thinking for multi-step reasoning, complex analysis, and problem-solving. Disable for straightforward generation.

**Why It Matters**: Extended thinking trades latency for reasoning quality. The model thinks through complex problems thoroughly before responding. This is worth the extra time for genuinely complex tasks but wasteful for simple ones.

**When to Enable Extended Thinking**:
✅ Multi-step problem solving (architecture design, strategic planning)
✅ Complex analysis requiring synthesis (research, due diligence, technical evaluation)
✅ Constraint satisfaction (optimization, tradeoff analysis)
✅ Novel problem-solving (no straightforward answer)
✅ Code generation for complex systems
✅ Security/safety critical decisions

**When NOT to Enable**:
❌ Simple classification or tagging
❌ Factual retrieval (just looking up information)
❌ Straightforward generation (formatting, copying)
❌ High-volume batch operations (too expensive)
❌ When you need sub-second latency

**Budget Sizing Guide**:

| Task Complexity | Budget | Use Case | Example |
|-----------------|--------|----------|---------|
| Simple reasoning | 4K-8K tokens | Single-step decisions, basic analysis | "Is this SQL injection?" |
| Moderate analysis | 8K-16K tokens | Multi-factor evaluation, comparisons | "Compare 3 cloud providers" |
| Complex reasoning | 16K-32K tokens | Architecture design, strategic planning | "Design microservices migration" |
| Deep synthesis | 32K-64K tokens | Comprehensive research, novel problems | "Analyze market disruption patterns" |
| Expert analysis | 64K+ tokens | High-stakes decisions, novel domains | "Navigate complex regulatory landscape" |

**Implementation**:
```xml
<thinking_budget>
Enable extended thinking with 16000 token budget.
This is a complex architectural decision requiring evaluation of 5 approaches
across 8 dimensions with consideration of long-term maintenance costs.
Thinking budget is appropriate for the decision importance.
</thinking_budget>
```

**How Sonnet 4.5 Uses Thinking**:
1. (Internal) Model reads your prompt
2. (Internal) Model allocates thinking budget and begins reasoning
3. (Internal) Model thoroughly explores the problem space
4. (Internal) Model evaluates approaches and identifies issues
5. (Response) Model outputs final answer

The internal reasoning is NOT shown to you but dramatically improves output quality.

---

### Rule 7: One Task Per Prompt
**Core Principle**: Each prompt should address one primary task or goal. Don't bundle unrelated tasks.

**Why It Matters**: Multi-task prompts create ambiguity about prioritization. The model may address one task superficially to have room for the other. Single-task prompts are clearer, more focused, and produce better results.

**Task Bundling Anti-Patterns**:

❌ "Analyze this code AND generate tests AND suggest optimizations AND document it"
✅ Split into 4 focused prompts:
1. Prompt 1: "Analyze this code and identify issues"
2. Prompt 2: "Generate 20 unit tests"
3. Prompt 3: "Suggest 5 specific performance optimizations"
4. Prompt 4: "Generate API documentation"

❌ "Research React ecosystem, Vue ecosystem, and Angular ecosystem, then compare them"
✅ Split into 4 focused prompts:
1. Prompt 1: "Research React ecosystem thoroughly"
2. Prompt 2: "Research Vue ecosystem thoroughly"
3. Prompt 3: "Research Angular ecosystem thoroughly"
4. Prompt 4: "Compare them across 8 dimensions"

**Exception**: Tasks that are genuinely sequential and depend on each other can be in one prompt.

✅ "First, identify the top 3 security vulnerabilities in this code. Then, for each vulnerability, generate a fixed version."
(This is OK because step 2 depends on step 1.)

**Implementation**:
Define a clear PRIMARY goal. Everything should support that goal.
```xml
<task_description>
PRIMARY GOAL: Design the database schema for an e-commerce order system.

[Only include context, examples, constraints that serve this primary goal]

SECONDARY GOALS: (If you must have them, be explicit)
- Include migration strategy from legacy system
- Explain indexing strategy

OUT OF SCOPE:
- API design
- Frontend implementation
- Search optimization (separate task)
- Reporting infrastructure (separate task)
</task_description>
```

---

### Rule 8: Include Anti-Patterns
**Core Principle**: Tell the model explicitly what NOT to do. This prevents common mistakes and keeps output focused.

**Why It Matters**: Anti-patterns are learned failures. They guide the model away from ineffective approaches. Being explicit about anti-patterns focuses effort on good solutions.

**What to Include**:
- Common mistakes you've seen before
- Approaches that sound good but don't work in your context
- Scope creep patterns to avoid
- Output quality problems to prevent
- Assumptions that are wrong for your situation

**Examples**:

```xml
<anti_patterns>
DO NOT:
- Suggest solutions requiring Docker; we use Kubernetes exclusively
- Recommend open-source tools with <1k GitHub stars; we need mature projects
- Propose architectural changes without migration strategy
- Ignore compliance requirements; this is a healthcare product
- Suggest generic "best practices"; we need context-specific recommendations
- Recommend 5+ new tools; we have tool proliferation problem
- Suggest solutions more expensive than rewriting in-house
- Ignore team skill constraints; we don't have Rust expertise
- Propose solutions requiring 6+ months implementation
- Present options equally; commit to your recommendation
</anti_patterns>
```

Another example:

```xml
<anti_patterns>
DO NOT:
- Include general information about React; only address their specific performance problem
- Suggest refactoring unless you've identified a concrete performance issue with numbers
- Use the word "optimize" without explaining what you're optimizing for
- Recommend class components; they use hooks exclusively
- Suggest third-party libraries without explaining why they're better than in-house solutions
- Make assumptions about their infrastructure; only work with what they've specified
</anti_patterns>
```

---

### Rule 9: Match Prompt Complexity to Task Complexity
**Core Principle**: Simple tasks need simple prompts. Complex tasks need complex prompts. Don't over-engineer simple requests.

**Why It Matters**: Prompt complexity introduces overhead and error surface. A 500-token prompt for a simple task creates latency and cost without benefit. A 200-word prompt for a complex decision loses important nuance.

**Complexity Calibration**:

| Task Complexity | Prompt Length | Structure | Thinking |
|-----------------|---------------|-----------|----------|
| Classification | 100-200 tokens | Simple, minimal | No |
| Straightforward analysis | 300-500 tokens | Structured, brief | No |
| Multi-factor evaluation | 500-1K tokens | XML-structured with examples | Maybe 8K |
| Complex design/strategy | 1-2K tokens | Comprehensive XML, detailed context | 16K+ |
| Novel/ambiguous problem | 2K+ tokens | Full structure, extensive examples, constraints | 32K+ |

**Don't Over-Prompt**:
```xml
❌ OVER-ENGINEERED:
<role_definition>
You are an expert system engineer with 20+ years of experience in distributed
systems, cloud architecture, storage systems, networking, and database design.
You have deep knowledge of CAP theorem, PACELC theorem, eventual consistency,
strong consistency models, and distributed consensus algorithms. You've worked
at Google, Amazon, Meta, and Microsoft. You understand the tradeoffs between
operational complexity, cost, latency, and consistency. You have strong opinions
about technology choices backed by experience...
</role_definition>

<task_description>
Should we use Redis or Memcached for caching?
</task_description>

✅ APPROPRIATELY SIMPLE:
<task_description>
Should we use Redis or Memcached for caching our product database queries?
We need: sub-100ms response times, persistence after crashes, support for complex
data structures (sets, hashes). Team has Redis experience.
</task_description>
```

For simple tasks, be direct. For complex tasks, be comprehensive.

---

### Rule 10: Iterate, Don't Over-Engineer
**Core Principle**: Start with a simple prompt. Add complexity only when you encounter problems. This minimizes latency and cost while building better prompts over time.

**Why It Matters**: Over-engineered prompts are premature optimization. You can't know all edge cases in advance. Iteration is faster and cheaper than trying to build the perfect prompt upfront.

**Iteration Pattern**:
```
1. START: Write the simplest viable prompt (50-200 tokens)
2. RUN: Get results
3. EVALUATE: Are results acceptable?
   - YES: Done. Document the prompt.
   - NO: Identify the problem
4. IMPROVE: Add structure/context/examples to address the problem
5. RERUN: Compare new results to baseline
6. REPEAT from step 3
```

**Example Iteration**:

**Attempt 1 (Too Simple)**:
```
Extract 5 key findings from this research paper.
```
Result: Superficial findings, missing technical depth.

**Attempt 2 (Added Structure)**:
```xml
<task_description>
Extract 5 key findings from this research paper. Focus on:
1. Novel methodology or approach
2. Unexpected results
3. Limitations acknowledged by authors
4. Implications for future work
5. Practical applications
</task_description>
```
Result: Better, but findings lack sufficient detail and source citations.

**Attempt 3 (Added Format)**:
```xml
<task_description>
Extract 5 key findings from this research paper. Focus on:
1. Novel methodology or approach
2. Unexpected results
3. Limitations acknowledged by authors
4. Implications for future work
5. Practical applications
</task_description>

<output_schema>
For each finding return:
- Finding: [1-2 sentence statement]
- Significance: [Why this matters]
- Evidence: [What in the paper supports this]
- Source: [Section/page reference]
- Applications: [Practical implications]
</output_schema>
```
Result: Excellent. Findings are detailed, cited, and well-formatted.

**Document the Winner**: When iteration produces good results, document the final prompt for reuse.

---

## SECTION 3: XML Tag Architecture & Patterns

### The Complete Tag Hierarchy

```xml
<prompt>
  <role_definition>
    <!-- Who is the model? What expertise and perspective? -->
  </role_definition>

  <context>
    <!-- Background information, constraints, stakeholders, success criteria -->
  </context>

  <task_description>
    <!-- What needs to be done? Primary objective clearly stated. -->
  </task_description>

  <input_data>
    <!-- What will be provided as input? -->
  </input_data>

  <output_schema>
    <!-- Exact format of response. JSON, markdown, etc. -->
  </output_schema>

  <constraints>
    <!-- Rules, limits, boundaries, assumptions -->
  </constraints>

  <examples>
    <!-- Show expected behavior with 1-3 worked examples -->
  </examples>

  <anti_patterns>
    <!-- Explicitly what NOT to do -->
  </anti_patterns>

  <success_criteria>
    <!-- How do we measure if this is good? -->
  </success_criteria>

  <thinking_budget>
    <!-- Only if using extended thinking -->
  </thinking_budget>
</prompt>
```

### Tag Descriptions with Detailed Examples

#### 1. Role Definition
Establishes who the model is and what expertise it has. This frames the perspective and quality bar.

```xml
<role_definition>
You are a principal engineer at a FAANG company with 18 years of experience
in distributed systems. You've designed systems serving 10M+ QPS. You
understand the tradeoffs between consistency, availability, partition
tolerance, and operational complexity. You make pragmatic decisions based
on the specific constraints, not general "best practices."
</role_definition>
```

**Why This Works**:
- Specific experience level (18 years, not "very experienced")
- Concrete context (FAANG, 10M+ QPS)
- Pragmatic mindset (context-aware, not dogmatic)
- Technical depth implied

**Anti-Example**:
```xml
<role_definition>
You are an expert. Be helpful and thorough.
</role_definition>
```
Too vague. Doesn't establish perspective or quality bar.

#### 2. Context
Provides background necessary for good reasoning. Include stakeholders, constraints, history, and success metrics.

```xml
<context>
COMPANY: Mid-size fintech startup (50 engineers, $10M ARR)

PROBLEM: Currently using a monolithic Python Django application (3 years old).
As the platform scales, we're hitting:
- Deployment bottleneck (every deploy affects the entire system)
- Scalability limits (can't handle peak load without vertical scaling)
- Team scaling limits (hard to parallelize work across teams)
- Database load (single PostgreSQL instance, read replicas only)

STAKEHOLDERS:
- Engineering leadership: Wants modularity and clear team ownership
- Product: Needs predictable release cycle (weekly deploys)
- Operations: Needs clear boundaries for incident response
- Finance: Wants to optimize cloud spend

CONSTRAINTS:
- Budget: Can't afford major infrastructure overhaul ($200K/year max)
- Timeline: Needs gradual migration, no big-bang rewrite
- Team: Mostly Python experience, some Go, no Rust
- Infrastructure: Already on AWS, using Kubernetes

CURRENT STATE:
- Daily active users: 100K
- Peak QPS: 2,500 (5x average)
- Database: PostgreSQL 14, 2TB data, 80% read, 20% write
- Main bottlenecks: Python serialization, shared database connections

SUCCESS CRITERIA:
- Enable independent team deployments
- Reduce deployment risk and time
- Handle 10M DAU without vertical scaling
- Reduce database load by 60%
- Teams can parallelize work without coordination
</context>
```

**What Makes This Good**:
- Specific numbers (enables realistic recommendations)
- Multiple stakeholder perspectives
- Concrete constraints (budget, timeline, skills)
- Current metrics (baseline for evaluation)
- Clear success criteria

#### 3. Task Description
Crystal-clear statement of what needs to be done. One primary objective.

```xml
<task_description>
PRIMARY OBJECTIVE: Design a microservices migration strategy for our
platform that enables team autonomy and reduces database load.

The strategy should:
1. Identify the 3-5 highest-value services to extract first
2. Define clear service boundaries
3. Specify data ownership and synchronization strategy
4. Provide a 12-month implementation roadmap
5. Estimate resource requirements and cloud cost impact

Focus on pragmatism over architectural purity. We need recommendations
that work with our team size and budget.
</task_description>
```

#### 4. Input Data
Specifies what data will be provided. Acts as a contract between user and model.

```xml
<input_data>
You will receive:
- Current application code structure and directory layout
- Database schema (tables, relationships, indexes)
- Daily usage patterns and traffic distribution
- Team organization (team sizes, specialties)
- Current deployment pipeline
</input_data>
```

#### 5. Output Schema
Most critical tag. Defines exactly what format the response should be in.

**JSON Format**:
```xml
<output_schema>
Return a JSON object with this exact structure:

{
  "migration_strategy": {
    "timeline_months": number,
    "estimated_cost_dollars": number,
    "team_headcount_months": number,
    "services": [
      {
        "name": "string — service name",
        "priority": "CRITICAL|HIGH|MEDIUM",
        "extraction_order": number,
        "rationale": "string — why extract this service",
        "estimated_effort_months": number,
        "team_size": number,
        "data_migration": {
          "strategy": "event_sourcing|snapshot_sync|dual_write",
          "estimated_duration_days": number,
          "risk_level": "LOW|MEDIUM|HIGH"
        },
        "dependencies": ["service_name"],
        "success_metrics": [string]
      }
    ],
    "risks": [
      {
        "risk": "string",
        "probability": "LOW|MEDIUM|HIGH",
        "impact": "string",
        "mitigation": "string"
      }
    ],
    "alternative_approaches": [
      {
        "name": "string",
        "pros": [string],
        "cons": [string],
        "recommended": boolean
      }
    ]
  }
}

CRITICAL RULES:
- Return ONLY valid JSON
- No markdown code fences
- No explanatory text
- No additional fields
</output_schema>
```

**Markdown Format**:
```xml
<output_schema>
Use this markdown structure for each service:

## Service Name
- **Priority**: CRITICAL | HIGH | MEDIUM
- **Extraction Order**: 1 (1st to extract), 2, etc.
- **Effort**: X months
- **Team Size**: X engineers
- **Rationale**: [Why extract this first?]
- **Data Migration Strategy**:
  - Approach: [event_sourcing | snapshot_sync | dual_write]
  - Duration: X days
  - Risk: [LOW | MEDIUM | HIGH]
- **Dependencies**: [List other services]
- **Success Metrics**: [How do we know this succeeded?]

## Risks and Mitigations
[List key risks with mitigations]

## Alternative Approaches
[Describe 2 alternative strategies with pros/cons]
</output_schema>
```

#### 6. Constraints
Rules and boundaries for the response.

```xml
<constraints>
- Assume team can learn new technologies within 3 months
- Can't introduce more than 2 new technologies
- Must use only AWS services we already have (no new vendor lock-in)
- Assume we can hire 2-3 senior engineers (6 month ramp time)
- Must support parallel teams working without heavy coordination
- Services must be independently deployable
- Database reads and writes can diverge (eventual consistency OK)
- Can't shut down old monolith until >95% functionality extracted
</constraints>
```

#### 7. Examples
Show the expected format and quality with 1-3 worked examples.

```xml
<examples>
<example>
SERVICE: User Service
PRIORITY: CRITICAL
EXTRACTION_ORDER: 1
RATIONALE: Most frequently accessed component, no complex state, clear boundaries
EFFORT: 4 months
TEAM_SIZE: 2 senior engineers
DATA_MIGRATION:
  Strategy: Event sourcing (user creation, updates are immutable events)
  Duration: 10 days (small dataset, ~500K users)
  Risk: LOW (read-only during migration, can roll back)
DEPENDENCIES: None (extracted first)
SUCCESS_METRICS:
  - 100% user read requests served by new service
  - <50ms p95 latency
  - 99.99% availability
  - <10 database queries per user session

SERVICE: Payment Service
PRIORITY: CRITICAL
EXTRACTION_ORDER: 2
RATIONALE: High-value, complex logic, performance bottleneck
EFFORT: 6 months
TEAM_SIZE: 3 engineers (including payments expertise)
DATA_MIGRATION:
  Strategy: Snapshot sync (consistent snapshot copied, then live updates streamed)
  Duration: 3 days
  Risk: MEDIUM (financial data, need careful verification)
DEPENDENCIES: User Service (needs to call user service for customer lookup)
SUCCESS_METRICS:
  - All payment processing on new service
  - <100ms p95 latency including network call to User Service
  - 99.9% availability (higher than current 99.5%)
  - Revenue reconciliation within $0.01
</example>
</examples>
```

#### 8. Anti-Patterns
Explicitly what NOT to do.

```xml
<anti_patterns>
DO NOT:
- Recommend complete rewrite; assume gradual migration only
- Suggest services that require synchronous calls across 3+ hops
- Ignore team's Python experience; don't recommend full language switch
- Propose architectural patterns that worked at 100M+ scale but don't suit 100K DAU
- Ignore data consistency issues; eventual consistency must be explicit
- Recommend solutions more expensive than status quo (we need cost-neutral migration)
- Suggest immediate full microservices architecture; too ambitious
- Ignore operational complexity; each service adds monitoring and alerting overhead
- Propose event-driven architecture without considering operational expertise gaps
- Give generic advice; all recommendations must be specific to their constraints
</anti_patterns>
```

#### 9. Success Criteria
How do we evaluate if the output is good?

```xml
<success_criteria>
- Migration strategy is pragmatic and achievable within 12 months
- Each service can be independently deployed and scaled
- Extraction order makes sense (dependencies are clear)
- Effort estimates are realistic (based on team size and complexity)
- Risk mitigations are concrete and specific
- Cost impact is quantified with specific numbers
- Alternative approaches are considered and rejected with reasoning
- Strategy respects team constraints (skills, budget, timeline)
- Strategy moves the needle on current bottlenecks (database, deployment)
</success_criteria>
```

#### 10. Thinking Budget
Only include if using extended thinking.

```xml
<thinking_budget>
Enable extended thinking with 24000 token budget.
This is a complex architectural decision with tradeoffs across team structure,
technical feasibility, cost, timeline, and operational complexity. The decision
impacts the company for 3+ years, so thorough reasoning is appropriate.
</thinking_budget>
```

---

## SECTION 4: Extended Thinking Mastery

### When Extended Thinking Provides Value

**Enable Extended Thinking For**:
1. Architecture and design decisions (multi-factor tradeoffs)
2. Strategic planning (complex dependencies, long-term impact)
3. Problem-solving with no obvious answer (novel challenges)
4. Constraint satisfaction (optimization under multiple constraints)
5. Code generation for complex systems (understanding interdependencies)
6. Security and safety analysis (considering attack vectors)
7. Complex research synthesis (connecting disparate sources)
8. Novel domain exploration (learning and reasoning simultaneously)

**Example**: "Design a data pipeline for processing 10 Billion events/day at <1 second latency" → Use extended thinking (tradeoffs between batch/streaming, storage, compute cost, operational complexity).

**Don't Enable Extended Thinking For**:
1. Simple classification or categorization
2. Fact retrieval (looking up information)
3. Straightforward text generation
4. High-volume batch operations
5. Tasks requiring sub-second response time
6. Content that doesn't benefit from deliberation

**Example**: "Classify this text as SPAM or NOT_SPAM based on keywords" → Don't use extended thinking (high volume, simple pattern matching).

### Extended Thinking Budget Sizing

The budget determines how much reasoning the model does before responding. More budget = better thinking but higher cost and latency.

**Budget Allocation Formula**:
```
reasoning_budget = base_complexity * (task_depth * novelty_factor) + safety_margin

where:
- base_complexity: 4K (simple), 8K (moderate), 16K (complex)
- task_depth: 1.0 (straightforward), 2.0 (multi-step), 3.0+ (highly complex)
- novelty_factor: 1.0 (standard task), 1.5 (somewhat novel), 2.0+ (very novel)
- safety_margin: 0-20% for reserve capacity
```

**Concrete Budget Examples**:

| Budget | Duration | Task Type | Example |
|--------|----------|-----------|---------|
| 4K-6K tokens | 5-10s | Simple reasoning | "Is this SQL injection vulnerable?" |
| 8K-12K tokens | 10-20s | Moderate analysis | "Compare 3 database options for our use case" |
| 16K-24K tokens | 20-40s | Complex design | "Design microservices migration strategy" |
| 32K-48K tokens | 40-90s | Deep synthesis | "Analyze market disruption in fintech" |
| 64K+ tokens | 90s+ | Expert-level reasoning | "Navigate complex regulatory landscape" |

**Cost Consideration**: Extended thinking costs 3-4x more than regular inference. Justify the spend with problem importance.

### Prompting for Better Thinking

**Don't Say This**:
- "Think step by step" (vague, doesn't specify what to think about)
- "Consider all possibilities" (too broad)
- "Be thorough" (not actionable)

**Say This Instead**:
- "Consider this thoroughly, thinking about [specific dimensions]"
- "Identify assumptions you're making, then evaluate if they're valid"
- "List 3-5 alternative approaches, then explain why you prefer the recommended approach"
- "For each tradeoff, quantify the cost-benefit"
- "What could go wrong? What's the mitigation for each risk?"

**Example with Thinking**:
```xml
<task_description>
Design a caching strategy for our product API.

For your analysis, explicitly consider:
1. What data should be cached vs. computed on-demand?
2. How do we maintain cache consistency with writes?
3. What's the cost-benefit of each caching layer (in-process, Redis, CDN)?
4. What happens if cache fails? How do we handle cache stampedes?
5. How do we monitor and tune cache hit rates over time?

Identify your key assumptions, then challenge them.
</task_description>

<thinking_budget>
Enable extended thinking with 16000 token budget.
</thinking_budget>
```

This gives the thinking process specific dimensions to explore.

### Extended Thinking with Tool Use

**Critical Pattern**: In multi-turn conversations with tool use, PRESERVE the thinking blocks.

When a model uses extended thinking and then calls tools:
1. The thinking happens FIRST (hidden)
2. The model chooses which tools to call
3. Tool results come back
4. The model uses previous thinking context + new tool results for final response

This is powerful because the thinking informs tool choice and interpretation.

### Anti-Patterns with Extended Thinking

❌ **Anti-Pattern 1: Overly Prescriptive Steps**
```xml
❌ Think through these exact steps:
1. First, identify the top 3 problems
2. Then, for each problem, generate 5 solutions
3. Then, evaluate each solution
4. Then, rank them

✅ Better: Think through the major problems and their solutions.
Evaluate your reasoning at each step.
```

Why: Prescribing exact steps prevents the model from finding better reasoning paths.

❌ **Anti-Pattern 2: Insufficient Budget**
```xml
❌ <thinking_budget>2000</thinking_budget>
for: "Design a global distributed system for 10B requests/day"

✅ <thinking_budget>32000</thinking_budget>
for: "Design a global distributed system for 10B requests/day"
```

Why: Insufficient budget prevents thorough reasoning.

❌ **Anti-Pattern 3: Budget Mismatch**
```xml
❌ Enable thinking for simple classification task

✅ Reserve thinking for complex decision/design tasks
```

Why: Thinking is expensive. Only use when reasoning quality matters more than cost/latency.

❌ **Anti-Pattern 4: Asking for Thinking in the Output**
```xml
❌ "Show me your thinking process. First, state your assumptions..."

✅ <thinking_budget>16000</thinking_budget>
[don't ask to see thinking—it's internal]
```

Why: Thinking is internal. Asking to see it wastes tokens on explanation instead of reasoning.

---

## SECTION 5: Output Schema Enforcement

Output schema enforcement is critical for production systems. Sonnet 4.5 respects schemas more reliably than earlier models.

### Three Enforcement Approaches

#### Approach 1: JSON Schema (API Level - Most Reliable)
When you have API access to Claude, send a JSON Schema in the request. This is the most reliable because the API enforces it.

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "temperature": 0,
  "schema": {
    "type": "object",
    "properties": {
      "findings": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "confidence": {"enum": ["VERIFIED", "HIGH", "MEDIUM", "LOW"]},
            "source": {"type": "string"}
          },
          "required": ["id", "title", "confidence"]
        }
      }
    },
    "required": ["findings"]
  }
}
```

The API will enforce this structure. If Sonnet's output doesn't match, the API rejects it.

#### Approach 2: Prompt-Based Enforcement (For Tool Contexts)
When you don't have access to JSON Schema enforcement (like in Claude Code, Cowork, or via Skill invocations), enforce schema through prompting.

This is what the deep-research-synthesizer skill uses.

```xml
<output_schema>
Return a JSON array. Each element MUST have exactly these fields:

{
  "id": "string — unique identifier",
  "title": "string — descriptive title",
  "content": "string — detailed content",
  "confidence": "VERIFIED|HIGH|MEDIUM|LOW|UNKNOWN",
  "source": "string — source URL or document",
  "related_ids": ["string"] — array of related entry IDs
}

CRITICAL ENFORCEMENT RULES:
1. Return ONLY the JSON array
2. No markdown code fences (no triple backticks)
3. No explanatory text before or after
4. No fields other than those specified
5. All required fields must be present
6. Confidence must be exactly one of: VERIFIED, HIGH, MEDIUM, LOW, UNKNOWN
7. Each entry must have valid JSON syntax
</output_schema>
```

The more explicit and strict you are, the better compliance you get.

#### Approach 3: Example-Based Enforcement
Show the exact format you want with 1-2 complete examples.

```xml
<examples>
EXAMPLE 1:
{
  "id": "react-virtual-dom-001",
  "title": "React Virtual DOM Reconciliation Algorithm",
  "content": "React uses a virtual DOM to track component state changes. When state updates occur, React creates a new virtual tree and compares (diffs) it against the previous tree. The diffing algorithm uses heuristics: same element type = likely same tree, elements with keys in lists are matched by key. Only differences are applied to the real DOM.",
  "confidence": "VERIFIED",
  "source": "https://react.dev/learn/render-and-commit",
  "related_ids": ["react-rendering-002", "react-hooks-001"]
}

EXAMPLE 2:
{
  "id": "vue-reactivity-001",
  "title": "Vue 3 Reactivity System",
  "content": "Vue 3 uses JavaScript Proxies to create reactive objects. When you access or modify properties on a reactive object, Vue tracks dependencies. When a property changes, Vue automatically updates components that depend on it. This enables fine-grained reactivity without manual dependency declaration.",
  "confidence": "HIGH",
  "source": "https://vuejs.org/guide/extras/reactivity-in-depth.html",
  "related_ids": ["vue-computed-001", "vue-watchers-001"]
}
```

### Schema Enforcement Best Practices

1. **Be Explicit**: Don't assume the model will infer format. State it clearly.

2. **Use Constraints Section**: Add rules about format in the constraints section.

3. **Validate Immediately**: If you receive output, validate it matches schema before using it.

4. **Retry with Feedback**: If output doesn't match schema, retry with specific feedback:
```
Your previous response included extra fields and markdown code fences.
Return ONLY a valid JSON array with no additional text.
```

5. **Provide Escape Hatch**: For unexpected cases, have a fallback format:
```xml
If you cannot provide the requested format, return:
{
  "error": true,
  "reason": "explanation of why",
  "raw_response": "your best effort response"
}
```

---

## SECTION 6: Domain-Specific Prompt Templates

### Template 1: Technology Research

```xml
<role_definition>
You are a senior technology analyst and architect with 15+ years of experience
evaluating technologies. You assess technologies based on: production readiness,
community maturity, long-term viability, operational complexity, and fit for
specific use cases. You are pragmatic, not dogmatic. You recommend technologies
that solve specific problems, not trendy solutions.
</role_definition>

<context>
[Company/problem context]
EVALUATION CONSTRAINTS:
- Team skill level: [junior | mid-level | senior]
- Infrastructure: [cloud provider, existing tools]
- Timeline: [when decision must be made, when implementation happens]
- Budget: [cost constraints, if any]
- Scale requirements: [QPS, data volume, users, etc.]
</context>

<task_description>
Evaluate [Technology X] vs [Technology Y] vs [Technology Z] for [specific use case].
Provide a clear recommendation backed by weighted tradeoff analysis.
</task_description>

<input_data>
You will receive:
- Requirements and use case details
- Team composition and experience
- Current infrastructure and tooling
- Constraints (timeline, budget, scale)
</input_data>

<output_schema>
{
  "recommendation": "technology_name",
  "confidence": "HIGH|MEDIUM|LOW",
  "evaluation_matrix": {
    "criteria": [
      {
        "name": "string",
        "weight": 0.0-1.0,
        "scores": {
          "technology_x": 0-10,
          "technology_y": 0-10,
          "technology_z": 0-10
        },
        "rationale": "string"
      }
    ]
  },
  "pros": [
    {"technology": "string", "pro": "string", "weight": 0.0-1.0}
  ],
  "cons": [
    {"technology": "string", "con": "string", "weight": 0.0-1.0}
  ],
  "implementation_path": [
    {"phase": int, "duration_weeks": int, "steps": [string], "team_size": int}
  ],
  "risks": [
    {"risk": "string", "mitigation": "string", "probability": "LOW|MEDIUM|HIGH"}
  ]
}
</output_schema>

<constraints>
- Recommendation must be backed by weighted analysis
- If technologies are equally qualified, commit to the simpler one
- Ignore industry trends; focus on specific context
- Team skill constraints are binding (can't recommend requiring 6-month learning curve)
- Budget constraints are binding (cost-prohibitive tech = automatically out)
- Assume implementation within stated timeline
</constraints>

<anti_patterns>
DO NOT:
- Recommend based on "everyone is using it"
- Suggest tech that requires more expertise than team has
- Ignore operational complexity and monitoring requirements
- Propose solutions more expensive than current approach (unless justified by major benefit)
- Assume unlimited budget or timeline
- Recommend technology without clear problem it solves for them
</anti_patterns>

<success_criteria>
- Recommendation is justified by specific tradeoff analysis
- Weights reflect true importance for their use case
- Implementation path is realistic and detailed
- Risks are identified and have concrete mitigations
- Team can execute on the recommendation within constraints
</success_criteria>

<thinking_budget>
Enable extended thinking with 16000 token budget for complex multi-factor comparison.
</thinking_budget>
```

### Template 2: Business/Market Research

```xml
<role_definition>
You are a market research analyst and business strategist with 12+ years of experience
at top consulting firms. You identify market trends, competitive dynamics, and strategic
opportunities using data-driven analysis. You think systematically about market structure,
customer needs, and competitive positioning. You are skeptical of hype and grounded in
evidence.
</role_definition>

<context>
[Market segment, company's position, timeline]
ANALYSIS SCOPE:
- Market size and growth trajectory
- Key competitors and their positioning
- Customer segments and their needs
- Emerging trends and disruption vectors
- Regulatory and macro factors
</context>

<task_description>
Analyze [market/segment] to identify [growth opportunities | competitive threats |
market shifts]. Provide strategic recommendations backed by data.
</task_description>

<output_schema>
{
  "market_overview": {
    "total_addressable_market": "string with estimate",
    "growth_rate": "string with % and timeframe",
    "key_segments": [
      {"segment": "string", "size": "string", "growth": "string", "characteristics": "string"}
    ]
  },
  "competitive_landscape": {
    "major_competitors": [
      {
        "name": "string",
        "market_share": "percentage or estimate",
        "positioning": "string",
        "strengths": [string],
        "weaknesses": [string]
      }
    ]
  },
  "trends_and_dynamics": [
    {
      "trend": "string",
      "evidence": "string",
      "impact_timeline": "string",
      "winners": [string],
      "losers": [string]
    }
  ],
  "opportunities": [
    {
      "opportunity": "string",
      "rationale": "string",
      "timeline": "string",
      "investment_required": "string",
      "potential_upside": "string",
      "probability_of_success": "LOW|MEDIUM|HIGH"
    }
  ],
  "risks": [
    {"risk": "string", "probability": "LOW|MEDIUM|HIGH", "mitigation": "string"}
  ]
}
</output_schema>

<constraints>
- Base analysis on available data (don't fabricate statistics)
- If data is limited, clearly state assumptions
- Opportunities must be plausible and actionable
- Timelines must be realistic
- Confidence levels must be honest
</constraints>

<anti_patterns>
DO NOT:
- Present opinions as facts
- Ignore competitive threats
- Overestimate market size based on TAM inflation
- Recommend entering markets without clear differentiation
- Ignore regulatory headwinds
- Present all opportunities as equally viable
</anti_patterns>

<thinking_budget>
Enable extended thinking with 24000 token budget for comprehensive market analysis.
</thinking_budget>
```

### Template 3: Scientific/Academic Research

```xml
<role_definition>
You are an expert researcher and academic with deep knowledge in [field]. You
critically evaluate research, identify methodological strengths and weaknesses,
and synthesize findings across multiple studies. You distinguish between well-supported
conclusions and speculation.
</role_definition>

<task_description>
Synthesize research on [topic] to provide a comprehensive overview of current understanding.
Focus on: methodological rigor, consensus areas, active debates, and open questions.
</task_description>

<output_schema>
{
  "topic_overview": "string",
  "consensus_findings": [
    {
      "finding": "string",
      "supporting_studies": [string],
      "confidence_level": "HIGH|MEDIUM",
      "evidence_quality": "string"
    }
  ],
  "active_debates": [
    {
      "debate": "string",
      "position_1": {"proponents": [string], "rationale": "string"},
      "position_2": {"proponents": [string], "rationale": "string"},
      "current_consensus": "string"
    }
  ],
  "methodological_gaps": [string],
  "emerging_research_areas": [string],
  "open_questions": [string]
}
</output_schema>

<constraints>
- Only cite studies you can reasonably expect the model to know
- Distinguish between consensus and minority positions
- Acknowledge methodological limitations in studies
- Don't extrapolate beyond what data supports
</constraints>
```

### Template 4: Legal/Compliance Research

```xml
<role_definition>
You are a legal analyst specializing in [jurisdiction/domain] with expertise in
regulatory compliance and risk management. You analyze regulations, identify
compliance requirements, and assess legal risks. You are thorough and conservative
in risk assessment.
</role_definition>

<task_description>
Analyze [regulatory domain] to identify: applicable regulations, compliance requirements,
enforcement patterns, and areas of legal uncertainty for [company/activity].
</task_description>

<output_schema>
{
  "applicable_regulations": [
    {
      "regulation": "string",
      "jurisdiction": "string",
      "requirements": [string],
      "enforcement_agency": "string",
      "penalties_for_violation": "string"
    }
  ],
  "compliance_checklist": [string],
  "areas_of_uncertainty": [
    {
      "issue": "string",
      "conflicting_interpretations": "string",
      "risk_level": "LOW|MEDIUM|HIGH",
      "recommended_approach": "string"
    }
  ],
  "enforcement_patterns": [
    {
      "agency": "string",
      "recent_enforcement_actions": [string],
      "focus_areas": [string]
    }
  ],
  "recommendations": [string]
}
</output_schema>

<constraints>
- Acknowledge that this is informational, not legal advice
- Conservative in risk assessment (err on side of caution)
- Flag ambiguous areas clearly
- Recommend legal counsel for specific guidance
</constraints>

<anti_patterns>
DO NOT:
- Provide legal advice (that requires a lawyer)
- Minimize legitimate risks
- Ignore jurisdiction-specific variations
- Treat all regulations as equally important
</anti_patterns>
```

### Template 5: Product/UX Research

```xml
<role_definition>
You are a product strategist and UX researcher with 10+ years of experience. You
think systematically about user needs, product-market fit, and feature prioritization.
You base recommendations on user research, not assumptions.
</role_definition>

<task_description>
Research [user segment] to understand: needs, pain points, usage patterns, and
feature preferences. Provide recommendations for product strategy.
</task_description>

<output_schema>
{
  "user_segment_overview": {
    "segment_size": "string",
    "key_characteristics": [string],
    "primary_use_cases": [string]
  },
  "identified_needs": [
    {
      "need": "string",
      "user_quote_or_evidence": "string",
      "current_solution_gap": "string",
      "importance": "CRITICAL|HIGH|MEDIUM|LOW"
    }
  ],
  "pain_points": [
    {
      "pain_point": "string",
      "frequency": "COMMON|OCCASIONAL|RARE",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "user_impact": "string"
    }
  ],
  "feature_recommendations": [
    {
      "feature": "string",
      "user_need_addressed": "string",
      "estimated_user_impact": "string",
      "implementation_complexity": "LOW|MEDIUM|HIGH",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW"
    }
  ],
  "product_strategy_implications": [string]
}
</output_schema>
```

---

## SECTION 7: Prompt Chaining Patterns

Prompt chaining is the practice of connecting prompts sequentially, where the output of one prompt becomes the input to the next. This enables complex workflows.

### Pattern 1: Sequential Chain (Linear Flow)
```
AGENT A (Research) → output → AGENT B (Synthesis) → output → AGENT C (Verification)
```

Use when each stage depends on previous results.

**Example**:
1. Agent A: "Research React performance optimization techniques"
2. Agent B: "Synthesize Agent A's findings into a best practices guide"
3. Agent C: "Verify claims from Agent B against current React documentation"

**Prompt Structure for Sequential Chain**:
```xml
<!-- Agent B receives Agent A's output as input -->
<task_description>
You will receive research findings from a previous agent that researched
React performance optimization. Synthesize these findings into a coherent
best practices guide.

Input: [JSON array from Agent A]

Your task: Create a structured best practices guide organized by category.
</task_description>
```

### Pattern 2: Fan-Out Chain (Parallel Execution)
```
         → AGENT 1 ────┐
        /              │
COORDINATOR            ├→ MERGE AGENT
        \              │
         → AGENT 2 ────┘
```

Use when independent agents can work in parallel, then results are merged.

**Example**:
1. Coordinator: "Decompose the analysis of AI/ML trends into 5 independent research tasks"
2. Agent 1: "Research Large Language Model trends"
3. Agent 2: "Research Computer Vision advances"
4. Agent 3: "Research Reinforcement Learning developments"
5. Agent 4: "Research AI Ethics and Safety"
6. Agent 5: "Research AI Infrastructure/Tooling"
7. Merge Agent: "Synthesize all 5 research reports into a comprehensive AI/ML landscape overview"

**Key**: Agents 1-5 run in parallel. Then Merge Agent runs sequentially.

### Pattern 3: Iterative Chain (Refinement Loop)
```
AGENT A → Result → AGENT B (Verify) → If gaps found → AGENT A (Refined) → ...
```

Use when you need quality refinement through verification.

**Example**:
1. Agent A: "Research microservices best practices"
2. Agent B: "Verify Agent A's claims and identify gaps"
3. If gaps found:
   - Agent A (round 2): "Fill these specific gaps: [from Agent B]"
   - Agent B (round 2): "Verify updated findings"
4. If verified:
   - Done

**Implementation**:
```
PASS 1:
Research Agent: "Thoroughly research microservices best practices"
Result: Initial knowledge base with 50 entries

Verify Agent: "Check each of the 50 entries. Are they accurate?
Are there major gaps? Return gaps list."
Result: List of 15 gaps

PASS 2 (if gaps exist):
Research Agent: "Fill these specific gaps: [list of 15]"
Result: Updated knowledge base with 65 entries

Verify Agent: "Re-verify new entries and check if original gaps are filled"
Result: Confirmation or new gaps
```

### Pattern 4: Hierarchical Chain (Coordination)
```
              COORDINATOR
              /    |     \
        AGENT 1  AGENT 2  AGENT 3
              \    |      /
              SYNTHESIZER
```

Use for complex decomposition with central coordination.

**Example: Deep research on "Building Scalable APIs"**

Coordinator decomposes into:
1. Architecture Agent: "Research API architectural patterns"
2. Performance Agent: "Research API performance optimization"
3. Security Agent: "Research API security best practices"

Synthesizer:
"Combine findings from all 3 agents into a comprehensive guide on building scalable APIs"

---

## SECTION 8: Sub-Agent Prompt Generation Algorithm

This is the systematic process for generating optimal prompts for sub-agents in a research workflow.

### Algorithm Steps

**Step 1: Identify Task Type**
```
Is this task:
a) Research/Exploration (gather information on a topic)
   → Use research-oriented role and prompt
b) Analysis/Synthesis (combine/compare information)
   → Use analytical role
c) Verification/Quality (check accuracy, find gaps)
   → Use critical/verification role
d) Organization/Categorization (structure information)
   → Use structural role
```

**Step 2: Select Role Definition**
Choose a role that matches expertise needed:
- Research: "Senior researcher with expertise in [domain]"
- Analysis: "Senior analyst who synthesizes complex information"
- Verification: "Critical evaluator who identifies gaps and inaccuracies"
- Synthesis: "Expert synthesizer who creates coherent frameworks"

**Step 3: Structure Context**
Include:
- Why is this task important?
- What will happen with the output?
- Who is the intended audience?
- What constraints apply?
- What success looks like

**Step 4: Define Task Description**
Be specific:
- What exactly should be researched/analyzed/verified?
- What depth is needed?
- What scope?
- What should NOT be included?

**Step 5: Specify Input Data**
Clearly state:
- What input will be provided?
- In what format?
- What assumptions can be made?

**Step 6: Define Output Schema**
Most critical step:
- JSON format (best for downstream processing)
- All required fields
- Example values for each field
- Validation rules

**Step 7: Add Task-Specific Constraints**
Examples:
- "Focus only on verified sources, not speculation"
- "Limit to top 10 findings by impact"
- "Each entry must be independently actionable"
- "Must support team learning within 1 week"

**Step 8: Include 1-2 Examples**
Show exactly what good output looks like:
```
EXAMPLE:
{
  "id": "react-hooks-001",
  "title": "React Hooks State Management",
  "content": "...",
  "confidence": "VERIFIED",
  "source": "https://..."
}
```

**Step 9: Add Anti-Patterns**
Explicitly what NOT to do:
```
DO NOT:
- Include theoretical concepts without practical examples
- Reference outdated documentation
- Mix different frameworks without clear distinction
- Use marketing language (only neutral technical language)
```

**Step 10: Set Success Criteria**
Measurable outcomes:
- "5-10 findings, each verified against primary sources"
- "Entries are specific and actionable, not generic advice"
- "Sources are cited and current (2023+)"
- "No duplicate entries"

**Step 11: Estimate Thinking Budget**
```
Simple research: 4K-8K
Moderate synthesis: 8K-16K
Complex analysis: 16K-24K
```

**Step 12: Review for Clarity**
Checklist:
- [ ] Role is clear and specific
- [ ] Task is unambiguous
- [ ] Output format is precisely defined
- [ ] Input data requirements are explicit
- [ ] Constraints are binding (no wiggle room)
- [ ] Anti-patterns prevent common mistakes
- [ ] Success criteria are measurable
- [ ] Thinking budget is justified

### Complete Generated Prompt Example

```xml
<role_definition>
You are a senior technology researcher with 12+ years of experience evaluating
web framework ecosystems. You understand both theoretical architecture and
practical production requirements. You distinguish between mature frameworks
and emerging projects.
</role_definition>

<context>
This research is for a technology selection guide for a mid-size team deciding
between modern web frameworks. The guide will help them understand each framework's
strengths, limitations, and appropriate use cases. Accuracy is critical because
incorrect recommendations could lead to poor technology choices.

Stakeholders:
- Engineering teams evaluating frameworks
- Architects making technology decisions
- Product teams estimating implementation timelines

Success means: Teams can make informed decisions based on accurate, current information.
</context>

<task_description>
Research the [Framework Name] web framework ecosystem. Focus on:
1. Architecture and design philosophy
2. Ecosystem maturity and community size
3. Performance characteristics and benchmarks
4. Learning curve and developer experience
5. Production use cases and companies using it
6. Common pain points and limitations

Provide verified findings, not speculation or marketing claims.
</task_description>

<input_data>
You will receive the framework name and any specific context about use case.
</input_data>

<output_schema>
Return a JSON array of findings, where each finding has:
{
  "id": "framework-topic-###",
  "title": "string — specific finding title",
  "content": "string — 2-4 sentence detailed explanation",
  "confidence": "VERIFIED|HIGH|MEDIUM|LOW",
  "source": "string — URL or document reference",
  "related_ids": ["id"] — related finding IDs
}
</output_schema>

<constraints>
- Return ONLY JSON array, no other text
- Confidence must be VERIFIED (for primary sources) or HIGH (for reliable secondary sources)
- Each finding must be independently understandable
- Sources must be current (2023+)
- No speculation about future development
- Focus on production-ready versions, not alpha/beta
</constraints>

<examples>
{
  "id": "react-vdom-001",
  "title": "React Virtual DOM Reconciliation Algorithm",
  "content": "React maintains a virtual representation of the DOM and performs diffing against previous versions. The reconciliation algorithm is key to performance—it identifies minimal changes and applies only those to the real DOM. React uses heuristics: same element type = likely same subtree, elements with keys in lists are matched by key.",
  "confidence": "VERIFIED",
  "source": "https://react.dev/learn/render-and-commit",
  "related_ids": ["react-rendering-002"]
}
</examples>

<anti_patterns>
DO NOT:
- Include theoretical concepts without production evidence
- Reference outdated versions (cite current LTS versions only)
- Use subjective language (good/bad/best—only specific tradeoffs)
- Include framework marketing claims without verification
- Mix up frameworks (e.g., confuse Vue composition API with React hooks)
- Speculate about future development or roadmaps
</anti_patterns>

<success_criteria>
- 10-15 verified findings covering the 6 key areas
- Each finding cites a primary or authoritative secondary source
- Sources are current (2023+)
- Findings are specific and technical, not generic
- No duplication across findings
- Confidence levels are honest and justified
</success_criteria>

<thinking_budget>
Enable extended thinking with 8000 token budget. This is straightforward research
on established frameworks with well-documented information.
</thinking_budget>
```

---

## SECTION 9: Anti-Patterns Encyclopedia

Comprehensive list of prompt anti-patterns that lead to poor results with Sonnet 4.5.

### Anti-Pattern 1: Vague Instructions
**Problem**: Vague prompts produce minimal, surface-level outputs.

❌ **Bad**:
```
Summarize this research paper
```

✅ **Good**:
```xml
<task_description>
Extract 5 key findings from this research paper, focusing on:
1. Novel methodology or approach
2. Unexpected results
3. Limitations of the study
4. Implications for future research
5. Practical applications

Each finding should be 2-3 sentences with a citation to the specific section.
</task_description>
```

### Anti-Pattern 2: Over-Prompting
**Problem**: Elaborately complex prompts for simple tasks waste tokens and create ambiguity.

❌ **Bad** (for simple task):
```xml
<role_definition>
You are an expert system engineer with 25 years of experience at FAANG companies.
[500 words of background]
</role_definition>

<context>
[1000 words of contextual information]
</context>

<task_description>
Classify this text as SPAM or NOT_SPAM
</task_description>
```

✅ **Good** (for simple task):
```
Classify this text as SPAM or NOT_SPAM. Return only: SPAM or NOT_SPAM
```

### Anti-Pattern 3: "Think Step by Step" Without Thinking Enabled
**Problem**: Saying "think step by step" when extended thinking is disabled creates weird behavior.

❌ **Bad**:
```
Think step by step about this complex architecture decision.

[But thinking is NOT enabled in the API call]
```

✅ **Good**:
```xml
Consider this complex architecture decision thoroughly, evaluating tradeoffs
across consistency, availability, cost, and operational complexity.

<thinking_budget>
Enable extended thinking with 16000 token budget.
</thinking_budget>
```

### Anti-Pattern 4: Bundled Multiple Tasks
**Problem**: Multiple tasks in one prompt create ambiguity about prioritization.

❌ **Bad**:
```
Review this code for bugs, write tests, optimize performance, and document it
```

✅ **Good**:
```
Task 1: Identify bugs and security issues in this code
Task 2: [In separate prompt] Write comprehensive test suite
Task 3: [In separate prompt] Suggest performance optimizations
Task 4: [In separate prompt] Generate documentation
```

### Anti-Pattern 5: No Output Format Specification
**Problem**: Without format specification, output is generic and unstructured.

❌ **Bad**:
```
Research microservices architecture
```

✅ **Good**:
```xml
<output_schema>
Return a JSON array of findings, each with:
{
  "topic": "string",
  "key_points": ["string"],
  "best_practices": ["string"],
  "common_mistakes": ["string"]
}
</output_schema>
```

### Anti-Pattern 6: Aggressive Tool-Use Prompting
**Problem**: Prompting for tool use when it's not needed causes wasted API calls.

❌ **Bad**:
```
You must use web search to find current information.
You should use web search to verify every claim.
Always use web search for research tasks.
```

✅ **Good**:
```
Use your existing knowledge. You have training data through 2024.
Only use web search if you need information about recent events (last 30 days).
```

### Anti-Pattern 7: Prescribing Exact Reasoning Steps
**Problem**: When thinking is enabled, prescribing exact steps prevents better reasoning paths.

❌ **Bad** (with thinking enabled):
```
Think through this step by step:
1. First identify the 3 biggest problems
2. Then for each problem, generate 5 solutions
3. Then evaluate each
4. Then rank them
```

✅ **Good** (with thinking enabled):
```
Think thoroughly about the major problems and potential solutions.
Evaluate your reasoning at each step.
```

### Anti-Pattern 8: Insufficient Budget for Complex Tasks
**Problem**: Low thinking budget for complex tasks prevents thorough reasoning.

❌ **Bad**:
```xml
<thinking_budget>2000</thinking_budget>

<task_description>
Design a complete microservices architecture for a company scaling from
100K to 10M users, considering consistency, availability, cost, and team structure.
</task_description>
```

✅ **Good**:
```xml
<thinking_budget>32000</thinking_budget>

<task_description>
Design a complete microservices architecture for a company scaling from
100K to 10M users...
</task_description>
```

### Anti-Pattern 9: Ambiguous Success Criteria
**Problem**: Without clear success criteria, evaluation is subjective and unreliable.

❌ **Bad**:
```
Generate a good analysis of the market opportunity.
```

✅ **Good**:
```xml
<success_criteria>
- Market size is quantified with specific numbers
- Growth rate is projected with assumptions stated
- Competitive positioning is specific (not generic)
- Opportunities are actionable (not theoretical)
- All claims cite sources or stated assumptions
</success_criteria>
```

### Anti-Pattern 10: Not Providing Examples
**Problem**: Without examples, the model must infer what you want.

❌ **Bad**:
```xml
<output_schema>
Return JSON with findings
</output_schema>
```

✅ **Good**:
```xml
<output_schema>
Return JSON with findings. Example:
{
  "finding": "React's Virtual DOM enables efficient updates",
  "source": "https://react.dev/...",
  "importance": "HIGH"
}
</output_schema>
```

---

## SECTION 10: Performance Optimization

Strategies for optimizing token usage, latency, and cost when using Sonnet 4.5 at scale.

### Token Budget Management for Sub-Agents

**Principle**: Different agents have different token needs. Right-size each agent's budget.

**Budget Allocation Framework**:
```
Total Project Budget: 100K tokens
Number of Sub-Agents: 10

Base allocation: 100K / 10 = 10K per agent

Adjust by complexity:
- Simple research: 6K
- Moderate analysis: 12K
- Complex synthesis: 20K
```

**Token Optimization**:
1. **Input Compression**: Summarize context rather than including full documents
2. **Output Constraints**: Specify JSON (compact) over markdown
3. **Thinking Budget**: Use thinking only for complex tasks, not simple ones
4. **Examples**: Provide 1 example, not 5 (diminishing returns)

### Model Selection by Agent Type

| Agent Type | Model | Cost | Latency | Quality |
|-----------|-------|------|---------|---------|
| Simple research | Haiku | Low | Very Fast | Good |
| Analysis/synthesis | Sonnet | Medium | Medium | Excellent |
| Complex reasoning | Opus | High | Slow | Expert |
| Verification | Haiku | Low | Very Fast | Good |
| Final synthesis | Sonnet/Opus | Medium/High | Medium/Slow | Excellent |

**Recommendation**: Use Haiku for breadth research (many independent lookups). Use Sonnet for synthesis and complex analysis. Use Opus only for high-stakes decisions.

### Parallel Dispatch Minimizes Wall-Clock Time

**Sequential Execution**:
```
Agent 1: 10s
Agent 2: 10s  (waits for Agent 1)
Agent 3: 10s  (waits for Agents 1-2)
Total time: 30s
```

**Parallel Execution**:
```
Agent 1: 10s ┐
Agent 2: 10s ├─ All run simultaneously
Agent 3: 10s ┘
Total time: 10s (3x faster!)
```

**Implementation**: When launching multiple independent agents, include them all in the same message to ensure parallel execution.

### Context Window Packing Efficiency

Sonnet 4.5 has 200K context window. Use it effectively:

**Inefficient Packing**:
- Long, repetitive context
- Multiple examples showing the same thing
- Verbose instructions

**Efficient Packing**:
- Concise context (assume domain knowledge)
- One example per concept
- Compressed instructions (XML tags provide structure)
- Removal of redundancy

**Rule of Thumb**:
- Your prompt should be 5-10% of the context window (10K-20K tokens max)
- Reserve the rest for complex tasks that need longer outputs

---

## CONCLUSION

Sonnet 4.5 is optimized for production use: reliable, fast, and cost-effective. Mastering these 10 rules and techniques enables:

1. **Predictable Results**: Explicit prompts produce consistent outputs
2. **Efficient Reasoning**: Extended thinking delivers expert-level analysis
3. **Reliable Structure**: Output schemas enforce format compliance
4. **Scalable Workflows**: Sub-agent orchestration handles complex decomposition
5. **Optimized Cost**: Right-sized thinking budgets and model selection

The key is: **be explicit, be structured, be iterative, and respect the model's capabilities**.

Start simple. Add complexity only when needed. Measure results. Iterate.
