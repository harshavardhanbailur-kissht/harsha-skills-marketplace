# Prompt Engineering for Claude 4.x: Reference Guide for Parallel Skill Builder

*A comprehensive reference for crafting effective prompts when building subtask agents and parallel execution systems with Claude 4.6 (Opus) and Claude 3.5 (Sonnet).*

---

## 1. Core Techniques Ranked by Impact

### Why This Matters
The most impactful prompting techniques have a multiplicative effect on model performance. Implementing even 2-3 of these can improve accuracy by 30-50%.

---

### 1.1 Clarity & Directness (Impact: 40-50%)

**Why:** Vague instructions force the model to guess your intent. Direct, specific instructions reduce ambiguity and model uncertainty.

**Prompt Pattern:**
```
# Task: Extract customer names from support tickets
Role: You are a data extraction specialist.

Input: Raw support ticket text
Output: A JSON array of {name: string, confidence: number}

Constraints:
- Only extract names explicitly mentioned (confidence >= 0.8)
- Return empty array if no valid names found
- Ignore honorifics (Dr., Mr., Ms.)

Example:
Input: "Jane Smith called about her order"
Output: [{"name": "Jane Smith", "confidence": 0.95}]
```

**Do's:**
- Start with an explicit role statement
- Define inputs, outputs, and constraints upfront
- Use structured format (JSON, YAML, markdown tables)
- Specify confidence thresholds for uncertain judgments
- Provide 1-2 examples before asking for work

**Don'ts:**
- Use vague language: "help me understand", "what do you think"
- Skip the role definition
- Leave output format ambiguous
- Mix multiple tasks without explicit separation

---

### 1.2 Multishot Prompting (Impact: 25-35%)

**Why:** One example shows a pattern; multiple examples establish it. 3-5 well-chosen examples catch edge cases the model might miss.

**Prompt Pattern:**
```
# Task: Classify support ticket severity

Severity levels: critical (service down), high (major feature broken),
medium (minor issue), low (documentation/cosmetic)

Examples:
1. Input: "Login page returns 500 error for all users"
   Output: critical
   Reasoning: Service completely unavailable

2. Input: "Search results take 30 seconds to load"
   Output: medium
   Reasoning: Feature works but degraded performance

3. Input: "Button text is misaligned on mobile"
   Output: low
   Reasoning: Cosmetic issue, no functional impact

4. Input: "Users can't upload files larger than 100MB"
   Output: high
   Reasoning: Core feature blocked for some users

Now classify this ticket:
Input: "{ticket_content}"
Output: [severity level]
Reasoning: [2-3 sentence explanation]
```

**Do's:**
- Include 3-5 diverse examples covering normal + edge cases
- Show reasoning for each example
- Vary examples by difficulty level (easy, medium, tricky)
- Keep examples concise but realistic

**Don'ts:**
- Include only "happy path" examples
- Use overly simplified examples that don't reflect real data
- Provide more than 5-7 examples (diminishing returns + token cost)

---

### 1.3 Chain-of-Thought (CoT) (Impact: 15-25%)

**Why:** Forcing the model to explain its reasoning reduces hallucination and improves accuracy on complex tasks.

**Prompt Pattern:**
```
# Task: Determine if a code change introduces a security vulnerability

Step through your analysis:
1. Identify what security domains this code affects (auth, data access, injection)
2. List potential attack vectors for each domain
3. Check if the code validates/sanitizes inputs appropriately
4. Determine if there's a realistic exploitation path
5. Rate severity (critical/high/medium/low/none)

Code to review:
```python
user_id = request.args.get('user_id')
data = database.query(f"SELECT * FROM users WHERE id = {user_id}")
```

Your analysis:
1. Security domains affected: [your answer]
2. Attack vectors: [your answer]
3. Input validation: [your answer]
4. Exploitation path: [your answer]
5. Severity: [your answer]
```

**Do's:**
- Break complex tasks into 3-7 numbered steps
- Ask the model to show intermediate reasoning
- Use phrases: "Let's think step by step", "Before answering, consider..."
- Request explicit reasoning before final answers

**Don'ts:**
- Use CoT for simple classification tasks (adds tokens, minimal benefit)
- Skip step descriptions (just numbers confuse the model)
- Create more than 7 steps (diminishing returns)

---

### 1.4 XML Tags for Structured Output (Impact: 20-30%)

**Why:** XML tags guide the model to organize responses predictably. Models strongly prefer structured markup over prose when it's specified.

**Prompt Pattern:**
```
# Task: Analyze code quality of submitted solution

Analyze the provided code and respond in this exact XML structure:

<analysis>
  <complexity>
    <cyclomatic>[1-50 scale]</cyclomatic>
    <readability>[1-10 scale]</readability>
    <maintainability>[1-10 scale]</maintainability>
  </complexity>
  <patterns>
    <good>[List 2-3 positive patterns found]</good>
    <improve>[List 2-3 areas for improvement]</improve>
  </patterns>
  <summary>[2-3 sentence overall assessment]</summary>
</analysis>

Code to analyze:
[USER CODE HERE]
```

**Do's:**
- Use nested XML for hierarchical data
- Specify tag names that are semantic (not generic like "output")
- Combine with examples showing expected output structure
- Keep tag hierarchy shallow (2-3 levels max)

**Don'ts:**
- Mix XML tags with prose instructions (commit fully to structure)
- Create overly deep nesting (hard for model to track)
- Use generic tags like <result>, <answer>, <data>
- Forget to show examples of what filled-in XML looks like

---

## 2. Model-Specific Differences: Sonnet 3.5 vs Opus 4.6

### Why This Matters
Choosing the wrong model wastes budget and latency. Opus 4.6 excels at complex reasoning; Sonnet 3.5 is fast and cheap for straightforward tasks. Using the right model for each subtask can cut costs by 40-60%.

---

### 2.1 Capability Comparison Table

| Capability | Sonnet 3.5 | Opus 4.6 | Recommendation |
|---|---|---|---|
| **Complex reasoning** | 75/100 | 95/100 | Use Opus for multi-step logic, novel problems |
| **Speed** | 95/100 | 70/100 | Use Sonnet for time-sensitive tasks |
| **Cost** | 70/100 | 30/100 | Use Sonnet for bulk processing, APIs |
| **Code generation** | 85/100 | 92/100 | Opus for complex; Sonnet for straightforward |
| **Factual accuracy** | 82/100 | 90/100 | Opus for fact-dependent tasks |
| **Instruction following** | 88/100 | 94/100 | Opus for precise format requirements |

---

### 2.2 When to Use Each Model

**Use Sonnet 3.5 for:**
- Data extraction, classification (low cognitive load)
- API responses, high-throughput scenarios
- Straightforward code tasks (loops, basic functions)
- Time-critical workflows (e.g., chat, real-time analysis)
- Budget-constrained projects

**Example Sonnet Task:**
```
# Task: Extract email and phone from ticket

Input: "Contact Jane at jane.smith@company.com or 555-0123"
Extract email and phone in JSON format.
Expected output: {"email": "jane.smith@company.com", "phone": "555-0123"}
```

**Use Opus 4.6 for:**
- Multi-step reasoning, complex logic
- Novel problem-solving, original synthesis
- Security/vulnerability analysis
- Deep code review, architectural decisions
- High-stakes accuracy requirements
- Nuanced writing (marketing copy, diplomacy)

**Example Opus Task:**
```
# Task: Identify architectural risks in microservice design

System: [Complex architecture description]
Consider:
1. Service dependencies and cascading failures
2. Data consistency patterns across services
3. Operational complexity and debugging difficulty
4. Security boundaries and trust assumptions

Provide detailed risk analysis with severity ratings.
```

---

### 2.3 Pricing & Token Efficiency

**As of 2026 (approximate pricing):**
```
Sonnet 3.5:  $3 per 1M input tokens,  $15 per 1M output tokens
Opus 4.6:    $15 per 1M input tokens, $75 per 1M output tokens
```

**Cost calculation for parallel tasks:**
```
Scenario: Process 1000 items with 500 token average response
Sonnet: 1000 * (500 input + 500 output) * $0.000015/token = $15
Opus:   1000 * (500 input + 500 output) * $0.000075/token = $75

→ For bulk processing, Sonnet saves 80% cost
→ For 10 items needing deep reasoning, Opus's better accuracy might save revision rounds
```

---

### 2.4 Effort Parameter Tuning

**What it does:** Controls how much time the model spends on thinking (within extended thinking budgets).

**Sonnet 3.5 effort levels:**
```
effort: "low"    → ~20% extended thinking time (fast, lower accuracy)
effort: "medium" → ~50% extended thinking time (balanced)
effort: "high"   → ~80% extended thinking time (thorough, slower)
```

**Opus 4.6 effort levels:**
```
effort: "low"    → Skip extended thinking for fast response
effort: "medium" → ~40% budget allocated to thinking
effort: "high"   → ~80% budget allocated to thinking (deep reasoning)
```

**Tuning guidance:**
- Start with `effort: "medium"` for Opus (balanced accuracy/speed)
- Use `effort: "low"` for Sonnet on straightforward classification
- Use `effort: "high"` for Opus on novel, high-stakes reasoning
- Never use `effort: "high"` for bulk processing (too slow + expensive)

---

## 3. Extended Thinking: When, How, and Budget Management

### Why This Matters
Extended thinking can improve accuracy by 20-40% on complex tasks, but costs 3-5x more tokens and is slower. Using it wisely is critical for cost control.

---

### 3.1 Extended Thinking vs. Standard Reasoning

**Extended Thinking = Internal scratchpad**
```
budget_tokens: 10000  # The model can "think" for up to 10k tokens internally
                      # These tokens count toward your quota but are worth the cost
                      # for complex reasoning tasks
```

**Standard Reasoning = Direct response**
```
# No budget_tokens parameter
# Model responds directly without internal deliberation
# Faster, cheaper, but less accurate on complex tasks
```

---

### 3.2 When to Use Extended Thinking

**Use extended thinking when:**
- Task involves novel reasoning (not in training data patterns)
- High accuracy cost: errors are expensive
- Problem is multi-step with potential dead-ends
- You have budget (not cost-critical path)

**Example where extended thinking pays off:**
```
# Task: Design a distributed system for X

This is novel: the model must synthesize multiple concepts
(CAP theorem, consistency models, failure modes, load patterns)
into a coherent design. Extended thinking helps avoid
inconsistent reasoning paths.

Use: budget_tokens: 15000, effort: "high"
```

**Don't use extended thinking when:**
- Task is straightforward classification
- You need <1 second response time
- Throughput is critical (processing millions of items)
- Cost is the primary constraint

**Example where extended thinking wastes tokens:**
```
# Task: Is this word spelled correctly?

Input: "recieved"
Output: false

Standard reasoning is fine. Extended thinking adds no value.
Skip budget_tokens parameter entirely.
```

---

### 3.3 Budget Token Caps & Practical Limits

**Setting appropriate budgets:**
```
Task complexity          budget_tokens    typical output tokens
Simple classification    2000             100-300
Moderate analysis        5000             300-800
Complex reasoning        15000            500-1500
Very deep synthesis      25000+           1000-2000
```

**Example: Setting budget for code review**
```
{
  "model": "claude-opus-4-6",
  "max_tokens": 2000,  # Output limit
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000  # Internal thinking limit
  },
  "messages": [
    {
      "role": "user",
      "content": "Review this code for security issues..."
    }
  ]
}
```

**Managing costs with extended thinking:**
```
# Scenario: Review 100 functions for security

Option A (Extended thinking for all):
100 functions × (10k thinking + 500 output) × $0.000075/token = $75

Option B (Adaptive - extended thinking only for complex):
20 complex × (10k thinking + 500 output) × $0.000075 = $15
80 simple × (0 thinking + 300 output) × $0.000075 = $1.80
Total: $16.80 (77% savings)

→ Use adaptive thinking: extended for high-complexity, skip for straightforward
```

---

### 3.4 Adaptive vs. Manual Extended Thinking

**Manual (recommended for parallel agents):**
```
# You decide upfront which tasks need extended thinking
# Pro: Predictable cost, consistent behavior
# Con: Requires classification logic

if task.complexity > threshold:
    use_extended_thinking = true
    budget_tokens = 10000
else:
    use_extended_thinking = false
```

**Adaptive (not recommended for parallel agents):**
```
# Model decides if it needs to think longer
# Pro: Theoretically optimal
# Con: Unpredictable cost, latency varies wildly
# Not suitable for parallel execution (can't batch if latency varies)

# Skip this for parallel skill builder—stick with manual
```

**Recommendation:** For parallel skill builder, use **manual extended thinking** with upfront complexity classification.

---

## 4. System Prompt Optimization

### Why This Matters
System prompts set context that applies to all turns. Well-designed system prompts reduce per-task prompt size by 20-30% and improve consistency. Poor system prompts create confusion and waste tokens.

---

### 4.1 What Goes in System vs. User Turn

**System prompt is for:**
```
- Stable context that applies to ALL tasks in a session
- Role/persona definition (e.g., "You are a security expert")
- Output format preferences (e.g., "Always use JSON")
- Behavioral guidelines (e.g., "Be concise", "Show reasoning")
- Constraints (e.g., "Do not use external APIs")
```

**User turn is for:**
```
- Specific task definition
- Input data
- Task-specific parameters
- Examples relevant to THIS task
- One-time instructions
```

**Example system prompt:**
```
You are a code review specialist for security vulnerabilities.

Guidelines:
- Respond in JSON format: {severity: string, issues: array, summary: string}
- Be concise: max 2 sentences per issue
- Only flag confirmed vulnerabilities (confidence >= 0.8)
- Ignore style/convention issues
- Assume standard secure coding practices are known
```

**Example user turn (for that system context):**
```
Review this code for security issues:

```javascript
const userId = req.query.id;
const user = await db.query(`SELECT * FROM users WHERE id = ${userId}`);
```
```

**Combined effect:**
- System prompt sets expectations once
- User turn is 50% smaller (no format specs, role definitions repeated)
- Model response is consistent across tasks

---

### 4.2 Role Definition Patterns

**Generic role (weak):**
```
You are a helpful assistant.
```

**Specific role (strong):**
```
You are a security architect with 15 years of experience designing
distributed systems. Your expertise: threat modeling, cryptography,
access control. Your communication style: direct, technical, no hand-waving.
```

**Why the difference matters:**
- Generic roles don't guide model behavior
- Specific roles anchor expectations and improve output quality
- Detailed experience description helps model calibrate language

**Production-ready role definitions:**
```
# For code review
You are a senior code reviewer with expertise in: Python/JavaScript,
performance optimization, testing best practices. Your role: provide
actionable feedback on code quality, readability, and efficiency.
Flag only issues with clear impact (not stylistic preferences).

# For data analysis
You are a data analyst. Your expertise: SQL, statistical analysis,
data visualization, interpretation of complex datasets. Your role:
extract insights from raw data and present them clearly with evidence.
Quantify findings—always provide specific numbers and percentages.

# For creative writing
You are a professional copywriter specializing in marketing and
narrative voice. Your expertise: brand messaging, persuasion,
storytelling, audience psychology. Your role: create compelling,
concise copy that drives action while maintaining authenticity.
```

---

### 4.3 System Prompt Template for Parallel Agents

```
You are a {ROLE_NAME} agent in a parallel execution framework.

Your expertise: {SPECIFIC_SKILLS}

Operational constraints:
- You work on ONE isolated subtask at a time
- You do NOT see other agent outputs or context
- You receive exactly {INPUT_FORMAT} as input
- You MUST output exactly {OUTPUT_FORMAT}
- Maximum response length: {MAX_TOKENS} tokens

Output format (non-negotiable):
{SCHEMA_OR_EXAMPLES}

Guidelines:
- {BEHAVIORAL_GUIDELINE_1}
- {BEHAVIORAL_GUIDELINE_2}
- {BEHAVIORAL_GUIDELINE_3}

Red flags to avoid:
- {COMMON_MISTAKE_1}
- {COMMON_MISTAKE_2}
```

**Filled example:**
```
You are a data validation agent in a parallel extraction framework.

Your expertise: JSON schema validation, type checking, business logic validation

Operational constraints:
- You validate ONE record at a time (no cross-record analysis)
- You receive JSON input from upstream extraction
- You output validation result in standardized format
- Maximum response: 500 tokens

Output format:
{
  "valid": boolean,
  "errors": [{"field": string, "reason": string}],
  "warnings": [{"field": string, "note": string}],
  "metadata": {"validation_rule_version": string}
}

Guidelines:
- Be strict on type checking; lenient on formatting
- Flag missing required fields as errors (not warnings)
- Suggest fixes for common validation failures
- Never attempt to auto-correct data—only report issues

Red flags to avoid:
- Don't make assumptions about missing data
- Don't modify input values
- Don't combine multiple validation failures into one error
```

---

## 5. Token Efficiency Strategies

### Why This Matters
Token efficiency directly impacts cost and latency. A well-optimized prompt can be 50-70% cheaper than a naive one while maintaining quality.

---

### 5.1 Prompt Caching (90% Savings Potential)

**What it is:**
Cache parts of your prompt (system message, static context) so they're reused across multiple API calls.

**Savings:**
```
Without caching: 100 requests × (5000 token system + 500 token user) = 550,000 tokens
With caching:    5000 token system (cached, paid once) + 100 × 500 = 50,500 tokens
Savings: 91%
```

**How to use:**
```python
# Only cache the system message and static context
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": "You are a security code reviewer...",
            "cache_control": {"type": "ephemeral"}  # ← Cache this
        }
    ],
    messages=[
        {
            "role": "user",
            "content": f"Review this code: {code_snippet}"  # ← Not cached
        }
    ]
)
```

**Caching rules:**
- Cache system messages (stable context)
- Cache long static context blocks (e.g., reference docs)
- Don't cache user input (it varies per request)
- Minimum cache size: 1024 tokens (smaller caches have high overhead)

**Practical example for parallel agents:**
```python
# System prompt cached across 1000 parallel validation tasks
SYSTEM_PROMPT = """You are a data validator...
[500 tokens of detailed validation rules]"""

for item in parallel_items:
    response = client.messages.create(
        model="claude-opus-4-6",
        system=[{"type": "text", "text": SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": f"Validate: {item}"  # ← Varies per call
        }]
    )
```

---

### 5.2 Batch Processing (50% Savings Potential)

**What it is:**
Submit multiple requests in one batch for processing at off-peak times (cheaper rates, 50% discount typical).

**Savings:**
```
On-demand:  100 requests × $0.000075 per token = $7.50
Batch mode: 100 requests × $0.000035 per token = $3.50 (53% savings)

Trade-off: 24-48 hour latency vs. real-time
```

**When to use:**
- End-of-day bulk processing
- Non-urgent analysis tasks
- Parallel agent frameworks (can wait for batch completion)
- Cost-optimized background jobs

**When NOT to use:**
- Real-time responses needed
- Interactive user-facing tasks
- Latency-critical paths

**Batch request format:**
```json
{
  "custom_id": "task-001",
  "params": {
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "system": "You are a code reviewer...",
    "messages": [
      {"role": "user", "content": "Review this code: ..."}
    ]
  }
}
```

**Recommended approach for parallel skill builder:**
```
For non-urgent parallel tasks:
1. Collect tasks throughout the day
2. Submit batch at 8 PM
3. Poll results starting at 8 AM next day
4. Process results in parallel

Savings: 50% cost, slight latency increase
```

---

### 5.3 Effort Parameter Optimization

**Trade-off matrix:**
```
Effort    Thinking Time    Output Quality    Speed      Cost
low       Minimal          70-80%            Fast       +0%
medium    Moderate         85-90%            Medium     +50%
high      Extensive        90-95%            Slow       +150%
```

**Decision tree:**
```
Is accuracy critical and task complex?
├─ Yes → effort: "high"
└─ No: Is speed critical?
   ├─ Yes → effort: "low"
   └─ No: effort: "medium" (default, balanced)
```

**Examples:**
```
# Security vulnerability detection: effort: "high" (accuracy critical)
# Customer email routing: effort: "medium" (balanced)
# Sentiment classification: effort: "low" (speed, volume critical)
# Architectural design review: effort: "high" (high stakes)
```

---

### 5.4 Right-Sizing Model Selection

**Decision matrix:**
```
Task type              Accuracy needed    Volume      → Model choice
Classification         Medium (80%)       High        → Sonnet (cheap, fast)
Code review            High (90%+)        Medium      → Opus (accurate)
Bulk extraction        Low (70%)          Very high   → Sonnet (cheap)
Novel reasoning        High (90%+)        Low         → Opus (capable)
Straightforward task   Low-medium         Any         → Sonnet (efficient)
Complex architecture   High (95%+)        Low         → Opus + thinking
```

**Cost-aware selection:**
```
# Example: Process 100k support tickets for sentiment

Bad approach: Use Opus for all (100k × 1000 tokens × $0.000075 = $7,500)

Smart approach:
- Use Sonnet for 95k simple cases (95k × 1000 × $0.000015 = $1,425)
- Use Opus for 5k complex cases (5k × 1000 × $0.000075 = $375)
- Total: $1,800 (76% savings vs. all-Opus)

Classifier: Sonnet → complexity score → route to Sonnet or Opus
```

---

## 6. Prefilled Response Migration (Deprecated in 4.6)

### Why This Matters
Claude 4.6 deprecates the `prefilled_message` parameter. You need alternative strategies for JSON control and output formatting.

---

### 6.1 What Changed

**Old approach (4.5 and earlier):**
```python
# Deprecated—don't use
response = client.messages.create(
    messages=[
        {"role": "user", "content": "Extract data in JSON..."},
        {"role": "assistant", "content": "{\"status\": \"",  # ← Prefilled preamble
         "prefilled_message": True}
    ]
)
```

**Why deprecated:** Models in 4.6+ are better at following format instructions directly without prefilling.

---

### 6.2 Alternative 1: XML Wrapper (Recommended)

**Pattern:**
```python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[
        {
            "role": "user",
            "content": """Extract customer data and respond ONLY with:

<extraction>
  <name>...</name>
  <email>...</email>
  <phone>...</phone>
</extraction>

Input: "Contact John Smith at john@company.com, call 555-0123"
"""
        }
    ]
)
```

**Why it works:**
- Models strongly prefer structured XML
- No need for prefilling
- Self-contained, easy to parse
- Works consistently across model versions

---

### 6.3 Alternative 2: JSON Schema (Strong Type Control)

**Pattern:**
```python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[
        {
            "role": "user",
            "content": """Extract data matching this schema EXACTLY:

{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string", "format": "email"},
    "phone": {"type": "string", "pattern": "^[0-9-]+$"}
  },
  "required": ["name", "email"]
}

Input: "John Smith, john@company.com, 555-0123"
Respond ONLY with valid JSON matching the schema above.
"""
        }
    ]
)
```

**Why it works:**
- Clear type constraints
- Self-documenting
- Parseable as JSON-Schema
- Reduces hallucination on format

---

### 6.4 Alternative 3: Markdown Code Blocks

**Pattern:**
```python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[
        {
            "role": "user",
            "content": """Respond with a JSON code block:

```json
{
  "name": "...",
  "email": "...",
  "phone": "..."
}
```

Extract from: "John Smith, john@company.com, 555-0123"
"""
        }
    ]
)

# Extract JSON from response
import json
json_str = response.content[0].text
parsed = json.loads(json_str.split("```json\n")[1].split("\n```")[0])
```

**Why it works:**
- Models learn to use markdown code blocks naturally
- Easy to extract with string parsing
- Good for long-form structured output

---

### 6.5 Migration Checklist

```
For each place you used prefilled_message:

□ Change to XML wrapper (simplest)
OR
□ Change to JSON Schema specification (stricter)
OR
□ Change to markdown code blocks (flexible)

□ Test that output format is correct
□ Update parsing logic to extract from response
□ Verify no regressions in format consistency
```

---

## 7. Prompt Templates for Subtask Agents

### Why This Matters
Parameterized templates enable scaling: one template × many parameter sets = parallel agents with consistent behavior.

---

### 7.1 Template Structure for Task Decomposition

**Generic template:**
```
# Task: {TASK_NAME}
Role: {ROLE_DESCRIPTION}

Input format: {INPUT_SPECIFICATION}
Output format: {OUTPUT_SPECIFICATION}

Context (read-only):
{CONTEXT_INFORMATION}

Parameters:
- {PARAMETER_1}: {VALUE_1}
- {PARAMETER_2}: {VALUE_2}

Examples:
{EXAMPLE_1}
{EXAMPLE_2}

Constraints:
- {CONSTRAINT_1}
- {CONSTRAINT_2}

Your task:
{SPECIFIC_INSTRUCTION}
```

---

### 7.2 Dependency Injection Pattern

**Problem:** Subtask agents need to know about earlier results, but each runs independently.

**Solution:** Pass previous results as read-only context.

**Example:**
```python
def create_validation_agent_prompt(
    extracted_data: dict,
    validation_rules: str,
    downstream_expectations: str
) -> str:
    return f"""
Task: Validate extracted customer data

Context from previous agent:
Extraction agent output:
{json.dumps(extracted_data, indent=2)}

Validation rules:
{validation_rules}

Downstream requirements (data will be used for):
{downstream_expectations}

Your task:
1. Check each field against validation rules
2. Verify data is compatible with downstream use case
3. Report errors and suggested fixes

Output format:
<validation>
  <valid>true/false</valid>
  <errors>[list of {field, issue, suggestion}]</errors>
</validation>
"""
```

**Key principles:**
- Pass prior results as read-only context (don't ask agent to modify them)
- Make downstream expectations explicit
- Let agent focus on its specific job

---

### 7.3 Output Format Specification

**Weak specification:**
```
Output the result.
```

**Strong specification:**
```
Output format:
<result>
  <status>success|failure</status>
  <data>{actual result}</data>
  <error_code>{optional: error code if failed}</error_code>
  <reasoning>{2-3 sentence explanation}</reasoning>
</result>

Example:
<result>
  <status>success</status>
  <data>{"score": 0.87, "category": "high_quality"}</data>
  <reasoning>Meets all quality criteria with good clarity.</reasoning>
</result>
```

**Why it matters:**
- Downstream agents can parse output reliably
- Clear structure prevents hallucinated formats
- Examples show what success looks like

---

### 7.4 Complete Working Template

```
# Subtask Agent Template: Multi-step Analysis

**Task:** {TASK_ID}
**Role:** {ROLE_DESCRIPTION}

## Input
Structured input (JSON):
```json
{
  "subject": "{INPUT_DATA}",
  "context": "{CONTEXT_FROM_UPSTREAM}",
  "constraints": {
    "max_depth": 3,
    "confidence_threshold": 0.8
  }
}
```

## Output Format
```xml
<analysis>
  <summary>{1-2 sentence overview}</summary>
  <findings>
    <finding priority="critical|high|medium">
      <issue>{description}</issue>
      <evidence>{support from input}</evidence>
      <recommendation>{suggested action}</recommendation>
    </finding>
  </findings>
  <metadata>
    <confidence>0.0-1.0</confidence>
    <analysis_depth>1-5</analysis_depth>
  </metadata>
</analysis>
```

## Examples
Input:
```json
{"subject": "Query returns 500 errors intermittently"}
```
Output:
```xml
<analysis>
  <summary>Database connection pool exhaustion under load.</summary>
  <findings>
    <finding priority="critical">
      <issue>Connection pool size insufficient for peak load</issue>
      <evidence>Errors occur during business hours (9-5), suggesting load-driven</evidence>
      <recommendation>Increase pool size from 10 to 50 connections</recommendation>
    </finding>
  </findings>
  <metadata>
    <confidence>0.85</confidence>
    <analysis_depth>2</analysis_depth>
  </metadata>
</analysis>
```

## Constraints
- Base analysis on input provided only (no external assumptions)
- Flag confidence below 0.8 explicitly
- Limit to 3 findings (prioritize most important)
- Keep recommendations actionable

## Guidelines
1. {SPECIFIC_GUIDELINE_1}
2. {SPECIFIC_GUIDELINE_2}
3. {SPECIFIC_GUIDELINE_3}

Proceed with analysis.
```

---

## 8. Anti-Patterns to Avoid

### Why This Matters
Common mistakes waste tokens, produce poor outputs, or trigger unnecessary extended thinking. Avoiding these improves quality and cost.

---

### 8.1 Overtriggering Opus with Aggressive Language

**Anti-pattern (Bad):**
```
CRITICAL: Analyze this immediately with maximum detail!
You MUST provide deep analysis or the system fails.
Spend as much thinking time as needed—cost is NO OBJECT.
Be extremely thorough and leave no stone unturned!
```

**Why it's bad:**
- Aggressive language triggers defensive responses (model over-explains)
- "Cost is no object" wastes tokens on unnecessary detail
- "CRITICAL" and all-caps don't improve accuracy (actually harm it)
- Encourages extended thinking even when not needed

**Better approach:**
```
Analyze this for potential risks.
Focus on high-impact issues only.
Keep explanation concise: max 2 sentences per finding.
```

**Translation:**
- Replace urgency with clarity
- Specify brevity requirements
- Let the model self-regulate depth

---

### 8.2 Excessive Deliberation Prompts

**Anti-pattern (Bad):**
```
Before answering, think carefully about:
- What could go wrong?
- What assumptions are we making?
- What would an expert think?
- What edge cases exist?
- How confident are you really?
- What should we double-check?
- Why might you be wrong?

Then provide your answer.
```

**Why it's bad:**
- Triggers extended thinking unnecessarily
- Adds 1000+ tokens to every response
- Dilutes actual reasoning with meta-reasoning
- Doesn't improve output quality for simple tasks

**Better approach:**
```
Identify potential risks.
```

**Translation:**
- Use CoT only for complex tasks
- Trust the model to deliberate naturally
- Be specific about what to consider (not "think about everything")

---

### 8.3 Vague Instructions

**Anti-pattern (Bad):**
```
Please analyze the code and let me know what you think.
Give me insights into the data.
Tell me your thoughts on the proposal.
```

**Why it's bad:**
- Model must guess what "analyze" means
- Forces multiple clarification rounds
- Output lacks structure
- Hard to parse programmatically

**Better approach:**
```
Analyze the code for: (1) security vulnerabilities, (2) performance issues, (3) readability.
Output as JSON with format: {security: [], performance: [], readability: []}

Insight types: performance (measured impact), data_quality (% valid records), trends (month-over-month change)

Identify: (1) value proposition mismatches, (2) implementation feasibility risks, (3) go-to-market timing.
```

**Translation:**
- Always specify what "analyze" means in your domain
- Show output format examples
- Use structured requirements, not open-ended questions

---

### 8.4 Mixing Multiple Tasks in One Prompt

**Anti-pattern (Bad):**
```
Here's a code snippet. Also, can you review our architecture?
Plus, let me know if you think we should hire more engineers.
And what's your opinion on our tech stack?
```

**Why it's bad:**
- Model must decide what to prioritize
- Output is scattered and unfocused
- Hard to use output in pipelines
- Wastes tokens on wrong tasks

**Better approach:**
```
# Task 1: Code Review
[code snippet]
Output format: [JSON with findings]

---

# Task 2: Architecture Review
[system diagram]
Output format: [XML with issues]

---

Process Task 1 completely. Then process Task 2.
```

**Translation:**
- Split multi-task prompts into clearly separated sections
- Process sequentially, not in parallel
- For true parallel tasks, use separate API calls

---

### 8.5 Assuming Prior Knowledge

**Anti-pattern (Bad):**
```
Fix the regex. You know what I mean.
```

**Why it's bad:**
- Model doesn't have context
- Can't provide good fixes without seeing original
- Requires back-and-forth clarification

**Better approach:**
```
This regex doesn't match email addresses as intended:
Pattern: ^([a-z]+)@([a-z]+)\.([a-z]+)$
Current behavior: Matches "john@company.com" but not "john.doe@company.co.uk"
Goal: Match all valid email formats per RFC 5322

Provide a corrected regex with explanation.
```

**Translation:**
- Always provide full context
- Explain what's currently wrong
- Specify desired behavior clearly

---

### 8.6 Ignoring Output Format Drift

**Anti-pattern (Bad):**
```
# First call
Output as JSON.

{"field1": "value1"}

# Second call (no format specified)
{
  "field1": "value1",
  "new_field": "not in original format",
  "extra_nesting": {"nested": "value"}
}
```

**Why it's bad:**
- Format drifts between calls
- Downstream parsing breaks
- Requires manual cleanup

**Better approach:**
```
All responses must be valid JSON matching this schema:
{
  "type": "object",
  "properties": {
    "field1": {"type": "string"},
    "field2": {"type": "number"}
  },
  "required": ["field1", "field2"],
  "additionalProperties": false
}
```

**Translation:**
- Specify output schema once (put in system prompt)
- Include format specification with every multi-turn interaction
- Reject any deviation from spec

---

## 9. Summary & Quick Reference

### Decision Tree: Which Technique to Use?

```
Is accuracy critical?
├─ Yes: Do you have budget for extended thinking?
│  ├─ Yes → Use Opus + extended thinking + CoT
│  └─ No → Use Opus + multishot + XML tags
└─ No: Is speed critical?
   ├─ Yes → Use Sonnet + minimal prompting
   └─ No → Use Sonnet + multishot + clear instructions
```

### Checklist: Before Deploying a Prompt

```
□ Clarity: Is the task definition unambiguous?
□ Role: Is the model role clearly specified?
□ Examples: Are there 3-5 diverse examples?
□ Format: Is output format specified with schema/example?
□ Efficiency: Can I reduce token count by 20%?
□ Caching: Are there reusable system contexts I can cache?
□ Model: Is this the right model for this task?
□ Effort: Is extended thinking needed, or is it wasteful?
□ Structure: Are multi-task prompts split into sections?
□ Safety: Are there injection risks in user input?
```

### Token Budget Quick Reference

```
Task type                          System   User   Output   Thinking   Total
Simple classification              500      200    100      0          800
Code review (Opus)                 500      1000   500      5000       7000
Bulk data extraction (Sonnet)      300      300    200      0          800
Complex architecture design        500      2000   1000     15000      18500
Security vulnerability analysis    500      1000   500      10000      12000
```

### Cost Optimization Checklist

```
□ Using Sonnet for all bulk tasks? (Not Opus for high volume)
□ Caching system prompts? (90% savings for repeated tasks)
□ Using batch processing for non-urgent work? (50% savings)
□ Right-sizing effort parameter? (low for volume, high for accuracy)
□ Avoiding extended thinking on simple tasks?
□ Trimming examples from 5+ down to 3-4?
□ Using prompt caching for static context?
□ Consolidating separate API calls into batch?
```

---

## Appendix: Example Prompts Ready to Use

### A1: Security Code Review Agent

```
You are a security code reviewer with expertise in OWASP Top 10,
CWE/SANS, and common vulnerability patterns.

Analyze provided code for security issues only
(not style or performance).

Output format:
<security_review>
  <summary>Risk level: critical|high|medium|low</summary>
  <vulnerabilities>
    <issue cve="optional_cve" severity="critical|high|medium">
      <description>{vulnerable code pattern}</description>
      <impact>{business/technical impact}</impact>
      <fix>{code fix with explanation}</fix>
    </issue>
  </vulnerabilities>
  <confidence>0.0-1.0</confidence>
</security_review>

Guidelines:
- Only flag issues with confirmed exploitation paths
- Quantify impact where possible
- Suggest concrete fixes, not vague mitigations
```

### A2: Data Extraction Agent

```
Extract structured data from unstructured text.

Input: Raw text containing information to extract
Output: JSON object with extracted fields

Schema:
{
  "type": "object",
  "properties": {
    "extracted_fields": {
      "type": "array",
      "items": {
        "field_name": "string",
        "value": "string or null",
        "confidence": "number 0-1"
      }
    },
    "missing_fields": {
      "type": "array",
      "items": "string"
    }
  }
}

Guidelines:
- Extract only fields explicitly present
- Set confidence to 0.5-0.9 for ambiguous values
- Return null for missing/unclear fields
- List required but missing fields separately
```

### A3: Argument Validation Agent

```
Validate that provided arguments meet requirements.

Input: Arguments JSON object + schema definition
Output: Validation result with errors and fixes

Format:
<validation>
  <valid>true|false</valid>
  <errors>
    <error field="field_name">
      <issue>{what's wrong}</issue>
      <suggestion>{how to fix}</suggestion>
    </error>
  </errors>
</validation>

Rules:
- Type checking: strict
- Format validation: strict (regex, email, URL)
- Range validation: inclusive of boundaries
- Null/undefined: flag if required
```

---

## References & Further Learning

- Anthropic's official prompt engineering guide: https://docs.anthropic.com/en/docs/build-a-chatbot-with-claude
- Extended thinking details: https://docs.anthropic.com/en/docs/about/models/claude-3-5-sonnet#extended-thinking
- Batch processing API: https://docs.anthropic.com/en/docs/build-a-chatbot-with-claude
- Prompt caching details: https://docs.anthropic.com/en/docs/about/models/claude-3-5-sonnet#prompt-caching
- Model updates and latest capabilities: https://docs.anthropic.com/en/docs/about/models/claude

---

*Last updated: February 2026. For the latest model information, consult Anthropic's official documentation.*
