# Advanced Sub-Agent Orchestration Guide

## SECTION 1: Sub-Agent Spawning Decision Tree

When should you spawn sub-agents versus handling tasks inline?

```
┌─ Can this task be decomposed into independent parts?
│  ├─ YES → "Spawn parallel agents"
│  └─ NO  → Next question
│
├─ Does this task require specialized expertise/role?
│  ├─ YES → "Spawn with role-specific prompt"
│  └─ NO  → Next question
│
├─ Would isolated context improve focus?
│  ├─ YES → "Spawn sub-agent with narrow context"
│  └─ NO  → Next question
│
└─ Is this a complex multi-step operation?
   ├─ YES → "Spawn with sequential chaining"
   └─ NO  → "Handle inline"
```

### Decision Examples

**Example 1: "Build comprehensive knowledge base on React ecosystem"**
```
Can decompose? YES (routing, state, performance, testing, tools, advanced patterns)
Specialized expertise needed? YES (each domain has specialists)
Isolated context helps? YES (focused research better than broad)
→ DECISION: Spawn 6-8 parallel agents, each researching one domain
```

**Example 2: "Fix this bug in the code"**
```
Can decompose? NO (bug location depends on investigation)
Specialized expertise? MAYBE (could help, but overkill)
Isolated context helps? NO (need full codebase context)
Multi-step? YES (investigate → debug → test)
→ DECISION: Handle inline with extended thinking
```

**Example 3: "Verify accuracy of knowledge base"**
```
Can decompose? YES (each entry can be verified independently)
Specialized expertise? NO (same verification skill)
Isolated context helps? YES (narrow focus on specific entries)
→ DECISION: Spawn verification agents in waves
```

---

## SECTION 2: Optimal Sub-Agent Count Formula

How many agents should you spawn for a given research task?

### The Formula

```
optimal_count = min(
  max_parallel_limit,        // typically 10-15 based on orchestration overhead
  ceil(total_gaps / granularity),  // 1 agent per 2-3 gaps
  breadth_score             // wider topics need more agents
)

where:
- max_parallel_limit: Hard limit on concurrent agents (budget, coordination overhead)
- total_gaps: Number of knowledge gaps to fill
- granularity: How many gaps can one agent handle (typically 2-3)
- breadth_score: Topic breadth multiplier (1-15 range)
```

### Breadth Score Calculation

```
breadth_score = (num_domains / 2) + (complexity_factor) + (novelty_factor)

where:
- num_domains: How many distinct domains/topics? (1-30 range)
  Examples:
  - React fundamentals: 1-2 domains (core, ecosystem)
  - Machine Learning: 5-8 domains (supervised, unsupervised, reinforcement, NLP, vision, etc)
  - Fintech: 10-15 domains (payments, lending, trading, compliance, security, etc)

- complexity_factor: (0-5 range)
  Simple topics: 0
  Moderate complexity: 2
  Highly complex: 5

- novelty_factor: (0-3 range)
  Well-established field: 0
  Emerging field: 2
  Very new/cutting-edge: 3
```

### Worked Examples

**Example 1: React Ecosystem Deep-Dive**
```
Gaps identified: 15 knowledge gaps
- Core concepts (3 gaps): state management, rendering, hooks
- Libraries (5 gaps): routing, form handling, testing, performance, internationalization
- Patterns (3 gaps): component architecture, error handling, accessibility
- Production (4 gaps): deployment, monitoring, optimization, security

Calculation:
- total_gaps = 15
- granularity = 2 (each agent can cover 2-3 gaps)
- ceil(15 / 2.5) = 6 agents baseline
- breadth_score = (3 domains / 2) + 1 + 0 = 2.5
- optimal = min(15, 6, 2.5) = 2.5 → 3 agents

Agent Assignment:
- Agent 1: Core concepts + routing
- Agent 2: Form handling + testing + performance
- Agent 3: Architecture patterns + accessibility + production

Result: 3 focused agents with 5 gaps each
```

**Example 2: Deep Dive on Transformer Architecture**
```
Gaps identified: 8 knowledge gaps
- Attention mechanism (2 gaps)
- Architecture details (2 gaps)
- Training strategies (2 gaps)
- Modern variants (2 gaps)

Calculation:
- total_gaps = 8
- ceil(8 / 2.5) = 4 agents baseline
- breadth_score = (2 domains / 2) + 4 (high complexity) + 0 = 5
- optimal = min(15, 4, 5) = 4 agents

Result: 4 specialist agents, one per domain
```

**Example 3: Comprehensive Market Analysis for Fintech**
```
Gaps identified: 30 knowledge gaps
- Payment systems (4 gaps)
- Lending platforms (4 gaps)
- Trading/investing (4 gaps)
- Cryptocurrency (4 gaps)
- Regulation & compliance (5 gaps)
- Infrastructure & security (4 gaps)
- Business models (5 gaps)

Calculation:
- total_gaps = 30
- ceil(30 / 2.5) = 12 agents baseline
- breadth_score = (7 domains / 2) + 5 (high complexity) + 1 (emerging) = 8.5
- optimal = min(15, 12, 8.5) = 8.5 → 8-9 agents

Result: 8-9 specialist agents covering different fintech domains
```

---

## SECTION 3: Multi-Pass Research Architecture

For large research projects, use a three-pass approach: breadth first, then depth, then verification.

### The Three-Pass Model

```
PASS 1: BREADTH RESEARCH (3-5 agents in parallel)
├── Agent 1: Overview and landscape search
├── Agent 2: Key players, platforms, technologies
├── Agent 3: Recent developments (last 6-12 months)
├── Agent 4: Common challenges and known solutions
└── Agent 5: Best practices and industry standards

Duration: 15-30 seconds
Output: Initial knowledge map with 30-50 entries
Quality: Good overview, may have gaps

COLLATION STEP (2-3 seconds)
├── Merge results from all agents
├── Identify duplicates and conflicts
├── Build dependency map
└── Identify deep-dive targets

PASS 2: DEPTH RESEARCH (5-10 agents in parallel, targeting specific gaps)
├── Agent 6: Deep dive on [Gap 1] ← Based on Pass 1 findings
├── Agent 7: Deep dive on [Gap 2]
├── Agent 8: Deep dive on [Gap 3]
├── Agent 9: Deep dive on [Gap 4]
└── Agent 10: Deep dive on [Gap 5]

Duration: 30-60 seconds
Output: Expanded knowledge base with 80-120 entries
Quality: Deep technical understanding, comprehensive coverage

COLLATION STEP (2-3 seconds)
├── Merge with Pass 1 results
├── Update dependency relationships
├── Verify no new conflicts introduced
└── Check coverage against original scope

PASS 3: VERIFICATION (2-3 agents)
├── Agent V1: Fact-check top 20 claims (highest importance)
├── Agent V2: Cross-reference statistics and numbers
└── Agent V3: Verify source reliability and recency

Duration: 20-40 seconds
Output: Confidence-tagged entries, conflict resolutions
Quality: Verified, trusted knowledge base

FINAL COLLATION (2-3 seconds)
├── Merge verification feedback
├── Update confidence levels
├── Resolve identified conflicts
└── Final knowledge base ready

TOTAL TIME: 60-120 seconds for comprehensive research
TOTAL TOKENS: 80K-150K depending on depth and breadth
```

### Implementation Details

**Pass 1: Breadth Prompts**

Agent 1 (Overview):
```xml
<task_description>
Provide a high-level overview of [topic]. What is it? Who uses it?
Why is it important? What are the major categories/areas?
</task_description>
```

Agent 2 (Key Players):
```xml
<task_description>
Identify the top 15-20 key players, platforms, and technologies in [topic].
For each, provide: name, what they do, market position, approximate market share.
</task_description>
```

Agent 3 (Recent Developments):
```xml
<task_description>
What are the most significant developments in [topic] from the last 6-12 months?
Focus on: new platforms, regulatory changes, major breakthroughs, significant failures.
</task_description>
```

Agent 4 (Challenges):
```xml
<task_description>
What are the common challenges, problems, and pain points in [topic]?
For each challenge, what are the known solutions or best practices?
</task_description>
```

Agent 5 (Best Practices):
```xml
<task_description>
What are the industry best practices and standards in [topic]?
Include: technical best practices, operational standards, governance approaches.
</task_description>
```

**Pass 2: Depth Prompts** (Generated based on Pass 1 gaps)

```xml
<task_description>
Deep dive into [specific gap identified in Pass 1].
Provide comprehensive understanding of:
- Foundational concepts
- Technical details and mechanisms
- Current state-of-the-art
- Major research or developments
- Open questions or areas of uncertainty

Use Pass 1 findings as context and extend them.
</task_description>
```

**Pass 3: Verification Prompts**

Agent V1 (Fact-Check):
```xml
<task_description>
You will receive a set of research findings on [topic].
Fact-check each claim against your knowledge.
Mark each as: VERIFIED, QUESTIONABLE, INCORRECT, CANNOT_VERIFY
For questionable/incorrect claims, explain the issue.
</task_description>

<input_data>
Pass 1 and Pass 2 findings (JSON array)
</input_data>

<output_schema>
{
  "findings_assessment": [
    {
      "finding_id": "string",
      "original_claim": "string",
      "verification_status": "VERIFIED|QUESTIONABLE|INCORRECT|CANNOT_VERIFY",
      "confidence": "HIGH|MEDIUM|LOW",
      "explanation": "string",
      "suggested_correction": "string (if incorrect)"
    }
  ]
}
</output_schema>
```

---

## SECTION 4: Dispatch Patterns with Implementation

How to launch agents in your system.

### Pattern 1: Parallel Fan-Out (All at Once)

**When to Use**: When agents are independent and can all run simultaneously.

**Implementation**:
```
Dispatch all agents in a SINGLE message to ensure parallel execution.

Message structure:
"Launch these 5 research agents in parallel:

AGENT 1: Research React fundamentals
AGENT 2: Research React ecosystem (libraries)
AGENT 3: Research React patterns
AGENT 4: Research React performance
AGENT 5: Research React production deployment

[Include full prompts for each agent]
"
```

**Advantages**:
- Maximum parallelism
- Fastest total execution time
- Efficient use of latency budget

**Disadvantages**:
- Can't use results from some agents to inform others
- Message size limit (200K tokens) for many agents
- All-or-nothing failure (if one agent fails, have to retry all)

### Pattern 2: Wave Dispatch (Phased Execution)

**When to Use**: When later agents need context from earlier agents.

**Implementation**:
```
WAVE 1: Launch 5 breadth agents in parallel
[Wait for results: 20-30 seconds]

COLLATE results → Identify gaps

WAVE 2: Launch 8 depth agents informed by Wave 1 results
[Wait for results: 40-60 seconds]

COLLATE results → Run verification

WAVE 3: Launch 2-3 verification agents
[Wait for results: 20-40 seconds]

FINAL COLLATION → Synthesize all results
```

**Advantages**:
- Each wave informs the next
- Adaptive research (focus on identified gaps)
- Quality improves with each wave
- Recovery: if a wave produces poor results, can retry

**Disadvantages**:
- Longer total execution time (sequential waves)
- Requires collation logic between waves

### Pattern 3: Hybrid Dispatch (Parallel + Sequential)

**Best of both worlds**: Some agents run in parallel, some run sequentially.

**Example: Market Research**
```
PARALLEL LAUNCH (all in one message):
- Agent 1: Research market size and growth
- Agent 2: Research competitor landscape
- Agent 3: Research customer segments
- Agent 4: Research industry trends

[Wait 30-40 seconds]

COLLATION: Merge results, identify synthesis gaps

SEQUENTIAL SYNTHESIS (one message):
- Agent 5: Synthesize all findings into market analysis

[Wait 20 seconds]

VERIFICATION (in parallel):
- Agent 6: Verify market size claims
- Agent 7: Verify competitor information
```

**Benefits**:
- Parallelism where possible (breadth research)
- Sequential where needed (synthesis)
- Balanced latency and quality

### Pattern 4: Cascade Dispatch (Dependency-Aware)

**When to Use**: When agents depend on each other in a DAG (directed acyclic graph).

**Example: API Design Research**
```
LAYER 1 (Prerequisite):
├─ Agent 1: Research REST architectural constraints

LAYER 2 (Depends on Layer 1):
├─ Agent 2: Research REST API design best practices
├─ Agent 3: Research GraphQL as REST alternative
├─ Agent 4: Research gRPC and other protocols

LAYER 3 (Depends on Layer 2):
├─ Agent 5: Synthesize API design patterns for different use cases
```

**Implementation**: Build dependency graph, launch agents respecting dependencies.

---

## SECTION 5: Result Collation Strategy

When N agents return results, how do you combine them into a unified knowledge base?

### 10-Step Collation Process

**Step 1: Parse Each Agent's Output**
```python
agent_results = []
for agent_response in agent_responses:
    try:
        parsed = json.parse(agent_response)
        agent_results.append(parsed)
    except JSONDecodeError:
        # Handle parse error (see error handling section)
        pass
```

**Step 2: Validate Against Schema**
```python
for agent_result in agent_results:
    for entry in agent_result:
        is_valid = validate_against_schema(entry, KNOWLEDGE_ENTRY_SCHEMA)
        if not is_valid:
            # Tag as schema_error for later handling
            entry['_validation_error'] = true
```

**Step 3: Assign IDs if Missing**
```python
id_counter = get_max_existing_id()
for agent_result in agent_results:
    for entry in agent_result:
        if not entry.get('id'):
            id_counter += 1
            entry['id'] = f"entry-{id_counter}"
```

**Step 4: Detect Duplicates**
```python
# Use title similarity (Levenshtein distance or semantic similarity)
def find_duplicates(entries, threshold=0.85):
    duplicates = []
    for i, entry1 in enumerate(entries):
        for j, entry2 in enumerate(entries[i+1:]):
            similarity = string_similarity(entry1['title'], entry2['title'])
            if similarity > threshold:
                duplicates.append((entry1, entry2, similarity))
    return duplicates

# Flag duplicates for merging
```

**Step 5: Merge Duplicates**
```python
def merge_duplicate_entries(entry1, entry2):
    """Keep the richer content, combine sources."""
    return {
        'id': entry1['id'],  # Keep first ID
        'title': entry1['title'],
        'content': longer_content(entry1['content'], entry2['content']),
        'confidence': max_confidence(entry1['confidence'], entry2['confidence']),
        'source': merge_sources(entry1['source'], entry2['source']),
        'related_ids': merge_related(entry1['related_ids'], entry2['related_ids'])
    }
```

**Step 6: Detect Conflicts**
```python
# Same topic, different claims = conflict
def find_conflicts(entries):
    """Identify entries about same topic with contradictory claims."""
    conflicts = []
    for i, entry1 in enumerate(entries):
        for j, entry2 in enumerate(entries[i+1:]):
            if topic_match(entry1, entry2):
                if claims_contradict(entry1, entry2):
                    conflicts.append({
                        'entry1': entry1,
                        'entry2': entry2,
                        'issue': 'contradictory_claims'
                    })
    return conflicts
```

**Step 7: Flag Conflicts for Resolution**
```python
# Mark conflicting entries with a flag for manual review
for conflict in conflicts:
    conflict['entry1']['_flagged_conflict'] = {
        'conflicting_with': conflict['entry2']['id'],
        'issue': 'contradictory claims'
    }
    conflict['entry2']['_flagged_conflict'] = {
        'conflicting_with': conflict['entry1']['id'],
        'issue': 'contradictory claims'
    }
```

**Step 8: Update Relationships**
```python
# Build related_ids based on content overlap
def find_related_entries(entries):
    for entry in entries:
        related = []
        for other in entries:
            if entry['id'] != other['id']:
                # Semantic similarity, keyword overlap, etc.
                if content_similarity(entry, other) > 0.6:
                    related.append(other['id'])
        entry['related_ids'] = related
```

**Step 9: Build Category Hierarchy**
```python
# Extract/infer categories from all entries
categories = set()
for entry in entries:
    # From explicit category field if present
    if 'category' in entry:
        categories.add(entry['category'])
    # From title keywords if not explicit
    else:
        inferred = infer_category(entry['title'])
        categories.add(inferred)

# Build hierarchy
category_tree = build_hierarchy(categories)
```

**Step 10: Generate Collation Report**
```python
report = {
    'total_entries_from_agents': sum(len(r) for r in agent_results),
    'duplicates_merged': num_duplicates_merged,
    'conflicts_flagged': num_conflicts,
    'final_entry_count': len(final_entries),
    'coverage_by_category': calculate_coverage(),
    'confidence_distribution': {
        'VERIFIED': count_by_confidence('VERIFIED'),
        'HIGH': count_by_confidence('HIGH'),
        'MEDIUM': count_by_confidence('MEDIUM'),
        'LOW': count_by_confidence('LOW')
    },
    'flagged_entries': [e for e in final_entries if '_flagged_conflict' in e],
    'warnings': identify_warnings()
}
```

---

## SECTION 6: Error Handling & Recovery

What happens when agents fail, produce bad output, or time out?

### Error Scenarios & Recovery

| Scenario | Detection | Recovery Strategy |
|----------|-----------|-------------------|
| **Empty Response** | Response length < 50 chars | Retry with rephrased prompt + extended thinking enabled |
| **Non-JSON Output** | JSON.parse() fails | Extract text blocks, create fallback entry manually |
| **Hallucination** | Claims are unverifiable or contradicted | Tag as LOW confidence, flag for verification |
| **Timeout** | No response after deadline | Log gap as unfilled, retry with simpler prompt |
| **Duplicate Content** | Hash collision or title similarity > 0.9 | Merge entries, keep richest version |
| **Scope Creep** | Content off-topic vs original gap | Filter by relevance, keep only related content |
| **Parsing Error** | Agent response invalid JSON | Extract usable fields, tag with schema_error |
| **Format Violation** | Output doesn't match schema | Attempt to extract expected fields, flag incomplete |

### Detailed Recovery Procedures

**Recovery 1: Retry with Extended Thinking**
```xml
<!-- First attempt (simple) -->
<task_description>
Research [topic]
</task_description>

<!-- Agent response: Empty or minimal -->
<!-- RECOVERY: Retry with thinking -->

<task_description>
Research [topic]. Think thoroughly about what aspects to cover.
Provide comprehensive findings with citations.
</task_description>

<thinking_budget>
Enable extended thinking with 8000 token budget.
</thinking_budget>
```

**Recovery 2: Manual Fallback Creation**
```python
def handle_non_json_response(text_response, gap_info):
    """Create fallback entry when agent response isn't valid JSON."""
    entry = {
        'id': generate_id(),
        'title': gap_info['gap_title'],
        'content': text_response[:500],  # Take first 500 chars
        'confidence': 'LOW',  # Mark as low confidence
        'source': 'direct_generation',
        '_notes': 'Entry created from non-JSON agent response; may need verification',
        'related_ids': []
    }
    return entry
```

**Recovery 3: Flagging for Verification**
```python
def flag_unverifiable_claim(entry):
    """Mark entries with unverifiable claims."""
    entry['_requires_verification'] = {
        'reason': 'claims_unverifiable',
        'action': 'verify against primary sources',
        'priority': 'HIGH'
    }
    entry['confidence'] = 'LOW'
    return entry
```

**Recovery 4: Timeout Handling**
```python
def handle_agent_timeout(agent_id, gap_info):
    """Log timeout, plan retry or escalation."""
    return {
        'agent_id': agent_id,
        'gap_id': gap_info['gap_id'],
        'status': 'timeout',
        'action': 'retry_in_next_wave',
        'priority': 'MEDIUM'
    }
```

---

## SECTION 7: Quality Scoring for Agent Outputs

Not all agent outputs are created equal. Score each output to determine inclusion quality.

### 5-Dimension Quality Score

**Dimension 1: Completeness** (0-10)
```
Does the agent's output fully address the original gap/task?
10 = Comprehensive coverage of all aspects
7 = Covers main aspects, some minor gaps
4 = Covers only some aspects
1 = Minimal coverage, major gaps
0 = Doesn't address the task
```

**Dimension 2: Specificity** (0-10)
```
Is the content specific and concrete, or vague and generic?
10 = Highly specific with concrete examples and details
7 = Specific with some examples
4 = Mix of specific and generic
1 = Mostly generic/vague
0 = No useful content
```

**Dimension 3: Source Quality** (0-10)
```
Are sources authoritative and current?
10 = Primary sources, peer-reviewed, or official documentation
7 = Authoritative secondary sources, current (2024+)
4 = Mixed source quality, some outdated
1 = Questionable sources, outdated
0 = No sources or completely unreliable
```

**Dimension 4: Structure** (0-10)
```
Is the output well-organized and properly formatted?
10 = Perfect structure, valid JSON, clear organization
7 = Good structure with minor formatting issues
4 = Adequate structure with some organization problems
1 = Poor structure, hard to parse
0 = Unusable structure
```

**Dimension 5: Confidence Accuracy** (0-10)
```
Are confidence tags appropriate and honest?
10 = Confidence tags are accurate and well-justified
7 = Mostly accurate with minor overstatement
4 = Some inaccurate confidence ratings
1 = Confidence tags are misleading
0 = No confidence tags or completely wrong
```

### Scoring Formula & Thresholds

```
quality_score = (completeness + specificity + source_quality + structure + confidence) / 5

THRESHOLDS:
- 9-10: Excellent. Include without modification.
- 7-8: Good. Include with minor verification.
- 5-6: Acceptable. Include but flag for verification.
- 3-4: Poor. Retry with modified prompt or discard.
- 0-2: Unusable. Discard, mark gap as unfilled.

MINIMUM INCLUSION THRESHOLD: 5.0
```

### Quality Scoring Implementation

```python
def score_agent_output(entries):
    """Score and filter agent output by quality."""
    scored_entries = []

    for entry in entries:
        completeness = score_completeness(entry)
        specificity = score_specificity(entry)
        source_quality = score_source_quality(entry)
        structure = score_structure(entry)
        confidence_accuracy = score_confidence_accuracy(entry)

        overall_score = (
            completeness + specificity + source_quality +
            structure + confidence_accuracy
        ) / 5

        entry['_quality_score'] = {
            'overall': round(overall_score, 1),
            'completeness': completeness,
            'specificity': specificity,
            'source_quality': source_quality,
            'structure': structure,
            'confidence_accuracy': confidence_accuracy
        }

        if overall_score >= MINIMUM_THRESHOLD:
            scored_entries.append(entry)
        else:
            # Log for retry
            log_poor_quality_entry(entry, overall_score)

    return scored_entries
```

---

## SECTION 8: Scaling Strategies for Large Knowledge Bases

When you need 100+ entries or managing 30+ gaps, special strategies apply.

### Wave Dispatch for Large Scales

**Problem**: Launching 30 agents at once creates coordination overhead.

**Solution**: Organize into waves of 10, with brief wait between waves.

```
WAVE 1 (10 agents): Breadth coverage
[Wait 40 seconds for completion]
[Collate: 50-70 entries, identify gaps]

WAVE 2 (10 agents): Depth on identified gaps
[Wait 50 seconds]
[Collate: 100-140 entries, identify remaining gaps]

WAVE 3 (8 agents): Fill specialized remaining gaps
[Wait 40 seconds]
[Collate: 120-180 entries]

WAVE 4 (5 agents): Verification and gap filling
[Wait 30 seconds]
[Final collation: 150-200 verified entries]

TOTAL TIME: ~3-4 minutes
TOTAL TOKENS: 150K-250K
```

### Priority-Based Research

**Approach**: Research CRITICAL gaps first, then IMPORTANT, then NICE-TO-HAVE.

```python
def prioritize_gaps(gaps):
    """Sort gaps by criticality."""
    critical = [g for g in gaps if g['priority'] == 'CRITICAL']
    important = [g for g in gaps if g['priority'] == 'IMPORTANT']
    nice_to_have = [g for g in gaps if g['priority'] == 'NICE_TO_HAVE']

    return critical + important + nice_to_have

# Research in priority order
for gap in prioritize_gaps(all_gaps):
    launch_research_agent(gap)
    if time_budget_exhausted():
        break
```

**Benefits**:
- Ensures critical knowledge gets covered
- Graceful degradation if time/budget runs out
- Can stop early once critical coverage is complete

### Dependency-Aware Research Ordering

**Approach**: Research foundational topics before advanced ones.

```python
def build_dependency_graph(gaps):
    """Build DAG of gaps where some depend on understanding others."""
    graph = {}
    for gap in gaps:
        dependencies = identify_prerequisites(gap)
        graph[gap['id']] = {
            'gap': gap,
            'depends_on': dependencies
        }
    return graph

def topological_sort_gaps(graph):
    """Return gaps in order where prerequisites are researched first."""
    return topological_sort(graph)

# Example:
# 1. "How does React work?" (foundational)
# 2. "React hooks implementation" (depends on 1)
# 3. "Performance optimization" (depends on 1, 2)
# 4. "Custom hooks patterns" (depends on 2)
```

### Budget-Aware Model Selection

**Strategy**: Use cheaper models for simple tasks, expensive for complex.

```python
def select_model_for_gap(gap):
    """Choose model based on gap complexity."""
    complexity_score = assess_complexity(gap)

    if complexity_score < 3:
        return 'haiku'  # Cheap, fast, good for simple lookups
    elif complexity_score < 7:
        return 'sonnet'  # Balanced cost/quality, good for most tasks
    else:
        return 'opus'  # Most capable, for complex reasoning
```

**Cost Breakdown**:
```
Haiku: $0.80/1M input, $4/1M output (cheapest)
Sonnet: $3/1M input, $15/1M output (balanced)
Opus: $15/1M input, $45/1M output (most capable)

Example project:
- 50 simple research gaps → Haiku
- 20 analysis gaps → Sonnet
- 5 complex synthesis → Opus

Total cost: Significantly lower than all-Sonnet approach
```

---

## SECTION 9: Advanced Collation Patterns

Beyond basic merging, sophisticated strategies for complex scenarios.

### Pattern 1: Conflict Resolution with Evidence

**Scenario**: Two agents report contradictory findings.

```
Agent 1: "React 19 removed Context API"
Agent 2: "React 19 still supports Context API with improvements"

Resolution approach:
1. Source check: Which agent cited better sources?
2. Recency check: Which claim is more current?
3. Specificity check: Which is more precisely worded?
4. Create merged entry with both claims + resolution
```

**Implementation**:
```python
def resolve_conflict(entry1, entry2):
    """Resolve contradictory claims."""
    # Score each by source quality and recency
    score1 = score_source_quality(entry1) + score_recency(entry1)
    score2 = score_source_quality(entry2) + score_recency(entry2)

    if score1 > score2:
        preferred = entry1
        questioned = entry2
    else:
        preferred = entry2
        questioned = entry1

    # Create merged entry
    return {
        'id': preferred['id'],
        'title': preferred['title'],
        'content': preferred['content'],
        'alternative_claims': [questioned['content']],
        'confidence': preferred['confidence'],
        'source': f"{preferred['source']} (preferred over {questioned['source']})",
        'conflict_resolved': True
    }
```

### Pattern 2: Relationship Discovery

**Approach**: Automatically identify how entries relate to each other.

```python
def discover_relationships(entries):
    """Find semantic relationships between entries."""
    relationships = {
        'requires': [],      # B requires understanding A
        'contradicts': [],   # Opposite claims
        'extends': [],       # Elaborates on
        'related_to': []     # General relevance
    }

    for entry in entries:
        for other in entries:
            if entry['id'] == other['id']:
                continue

            relation = determine_relationship(entry, other)
            if relation:
                relationships[relation['type']].append({
                    'from': entry['id'],
                    'to': other['id'],
                    'strength': relation['strength']
                })

    return relationships
```

### Pattern 3: Gap Coverage Analysis

**Approach**: After research, analyze what gaps remain.

```python
def analyze_gap_coverage(original_gaps, final_entries):
    """Determine which gaps were filled, which remain."""
    results = {
        'fully_covered': [],
        'partially_covered': [],
        'unfilled': [],
        'overfilled': []  # Extra entries on topic
    }

    for gap in original_gaps:
        coverage_score = calculate_coverage(gap, final_entries)

        if coverage_score >= 0.9:
            results['fully_covered'].append(gap)
        elif coverage_score >= 0.5:
            results['partially_covered'].append(gap)
        elif coverage_score == 0:
            results['unfilled'].append(gap)

    # Entries not tied to any gap
    results['overfilled'] = find_unexpected_entries(original_gaps, final_entries)

    return results
```

---

## SECTION 10: Orchestration Checklist

Before launching a multi-agent research project, validate:

```
PRE-LAUNCH CHECKLIST:

□ Task Decomposition
  □ Have you identified the right decomposition?
  □ Are sub-tasks independent?
  □ Is each sub-task clear and unambiguous?

□ Agent Configuration
  □ Do you have optimal agent count? (use formula)
  □ Is each prompt fully specified (role, task, schema)?
  □ Are thinking budgets right-sized?
  □ Are success criteria measurable?

□ Orchestration Strategy
  □ Have you chosen the right dispatch pattern (parallel/wave/cascade)?
  □ Do you have a collation strategy?
  □ Is error handling in place?
  □ Do you have timeout/retry logic?

□ Quality Assurance
  □ Do you have quality scoring in place?
  □ Are you verifying high-risk entries?
  □ Is there conflict detection?
  □ Can you track data lineage (which agent produced what)?

□ Resource Planning
  □ Have you estimated total token budget?
  □ Do you have cost analysis (Haiku vs Sonnet vs Opus)?
  □ Is your time budget realistic?
  □ Do you have fallback strategies if budget exceeded?

□ Monitoring & Logging
  □ Can you track progress in real-time?
  □ Do you have detailed logging of agent outputs?
  □ Can you identify which agents underperformed?
  □ Is there an audit trail for downstream debugging?

□ Knowledge Base Validation
  □ Have you validated final entries against schema?
  □ Do confidence levels make sense?
  □ Have conflicts been resolved?
  □ Is coverage adequate for your original goal?
```

---

## CONCLUSION

Advanced sub-agent orchestration enables:

1. **Scalable Research**: Handle 100+ entry knowledge bases efficiently
2. **Quality Control**: Multi-pass verification ensures accuracy
3. **Cost Optimization**: Wave dispatch and model selection control costs
4. **Reliability**: Error handling and recovery paths prevent failures
5. **Transparency**: Quality scoring and conflict detection surfaces issues

The key is: **decompose thoughtfully, dispatch strategically, collate carefully, verify rigorously**.
