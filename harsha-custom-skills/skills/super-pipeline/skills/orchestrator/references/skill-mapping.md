# Skill Mapping Reference

Complete guide to automatic skill discovery, task-to-skill routing, and multi-skill composition.

## Core Architecture

The foundation of automatic skill discovery comes from how VSCode, Obsidian, and the Model Context Protocol (MCP) handle extension loading. These systems share a critical pattern: **skills self-describe their capabilities through manifests**, and the host system discovers them through directory scanning combined with dynamic capability queries.

---

## Manifest-Based Self-Description

Skills are self-contained directories with declarative metadata:

```
skill-name/
├── manifest.json      # Metadata and capabilities
├── instructions.md    # Natural language instructions for LLM
└── handler.py         # Optional: custom execution logic
```

### Manifest Format

```json
{
  "id": "web-search-skill",
  "name": "Web Search",
  "version": "2.1.0",
  "description": "Search the web and retrieve information from URLs",
  "activationEvents": ["onIntent:search", "onKeyword:find", "onKeyword:lookup"],
  "capabilities": {
    "search": {
      "description": "Search the web for information",
      "inputSchema": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
      }
    }
  },
  "dependencies": ["internet-access"],
  "tags": ["research", "information-retrieval", "web"]
}
```

### Key Manifest Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Unique identifier | "web-search-skill" |
| `name` | Human-readable name | "Web Search" |
| `description` | What the skill does | "Search the web and retrieve information" |
| `activationEvents` | When to load/trigger | ["onIntent:search", "onKeyword:find"] |
| `capabilities` | Available operations | Schema definitions for each operation |
| `dependencies` | Required resources | ["internet-access"] |
| `tags` | Semantic categorization | ["research", "web"] |

---

## Three-Tier Task-to-Skill Mapping

Mapping incoming tasks to appropriate skills cannot rely on a single method. Robust matching requires combining three tiers:

### Tier 1: Keyword/Trigger Matching (Fast)

When a manifest declares `"activationEvents": ["onIntent:search", "onKeyword:find"]`, the orchestrator checks incoming tasks for exact matches before expensive calculations.

```python
def find_matching_skills_tier1(task: str, skills: List[Skill]) -> List[Tuple[Skill, float]]:
    matches = []
    task_lower = task.lower()
    
    for skill in skills:
        for event in skill.manifest.get("activationEvents", []):
            if event.startswith("onKeyword:"):
                keyword = event.split(":")[1].lower()
                if keyword in task_lower:
                    matches.append((skill, 1.0))  # High confidence
                    break
    
    return matches
```

**Best for**: Explicit commands, known triggers, fast initial filtering.

### Tier 2: Semantic Embedding Matching (Medium)

Uses vector similarity over skill descriptions and tags. Research shows sentence transformers like `all-MiniLM-L6-v2` provide excellent accuracy for matching natural language queries to capability descriptions.

```python
def find_matching_skills_tier2(task: str, skills: List[Skill], embedder) -> List[Tuple[Skill, float]]:
    task_embedding = embedder.encode(task)
    matches = []
    
    for skill in skills:
        similarity = cosine_similarity(task_embedding, skill.embedding)
        if similarity > 0.7:  # Threshold
            matches.append((skill, similarity))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)
```

**Best for**: Natural language queries, fuzzy matching, when skill count exceeds 50-100.

### Tier 3: LLM-Based Classification (High Accuracy)

When multiple skills match with similar confidence, or when the task is complex, invoke the LLM for disambiguation.

```python
def llm_select_skill(task: str, candidates: List[Skill], llm) -> Skill:
    prompt = f"""Given this task: "{task}"
    
Select the most appropriate skill from these options:
{chr(10).join(f'- {s.id}: {s.manifest["description"]}' for s in candidates)}

Respond with just the skill ID."""
    
    selected_id = llm.generate(prompt).strip()
    return next((s for s in candidates if s.id == selected_id), None)
```

**Best for**: Ambiguous cases, complex tasks, final disambiguation.

### Selection Decision Tree

```
Incoming Task
    │
    ├─► Tier 1: Check keyword/intent triggers
    │       │
    │       ├── Match found with high confidence → Use that skill
    │       │
    │       └── No match or multiple matches → Continue
    │
    ├─► Tier 2: Semantic embedding search
    │       │
    │       ├── Single high-confidence match (>0.85) → Use that skill
    │       │
    │       └── Multiple matches or uncertain → Continue
    │
    └─► Tier 3: LLM classification
            │
            └── Select from candidates with reasoning
```

---

## Weighted Scoring for Skill Selection

When multiple skills can handle a request, use weighted scoring across multiple dimensions:

### Scoring Dimensions

```python
def score_skill(skill: Skill, task: str, context: dict) -> float:
    score = 0.0
    
    # Specificity: How precisely does this skill match? (40%)
    specificity = calculate_specificity(skill, task)
    score += specificity * 0.4
    
    # Proficiency: Historical success rate (30%)
    success_rate = metrics.get_success_rate(skill.id)
    score += success_rate * 0.3
    
    # Availability: Current load and latency (20%)
    availability = 1.0 - load_balancer.get_load(skill.id)
    score += availability * 0.2
    
    # User preference: Explicit configuration (10%)
    preference = context.get("skill_preferences", {}).get(skill.id, 0.5)
    score += preference * 0.1
    
    return score
```

### Specificity Matching

A skill declaring "handles Python code formatting" should score higher than one declaring "handles code" when the task mentions Python.

Implemented through hierarchical matching against skill tags and capability descriptions.

### Bullseye Routing Pattern

Provides graceful degradation:

1. Start with exact capability matches
2. Expand to related capabilities
3. Finally fall back to general-purpose skills

This prevents task failures when the perfect skill is unavailable.

---

## Execution Prompt Composition

Once skills are selected, the orchestrator generates an execution prompt that includes relevant skill instructions.

### Dynamic Prompt Generation

```python
def generate_execution_prompt(task: str, selected_skills: List[Skill]) -> str:
    skill_instructions = []
    
    for skill in selected_skills:
        instructions = skill.instruction_path.read_text()
        skill_instructions.append(f"""
## {skill.manifest['name']} Instructions

{instructions}

### Available Operations:
{format_capabilities(skill.manifest['capabilities'])}
""")
    
    return f"""You are an AI assistant with access to specialized skills.

TASK: {task}

AVAILABLE SKILLS:
{chr(10).join(skill_instructions)}

Use these skills as needed to complete the task. When invoking a skill, 
use the exact operation names and parameter schemas defined above.
"""
```

### Key Principle

Inject skill-specific context **only when needed**, avoiding context pollution that degrades agent quality.

---

## Multi-Skill Composition

### Orchestration vs. Choreography

For AI skill composition, **orchestration wins** over choreography because it provides:
- Visibility into execution state
- Clearer debugging
- Deterministic control flow
- Essential for explaining AI decisions

### The Saga Pattern

Each skill execution is a local transaction; if a later step fails, compensating transactions undo earlier work:

```python
class SkillSaga:
    def __init__(self, skills: List[Skill]):
        self.skills = skills
        self.completed = []
    
    async def execute(self, context: dict) -> dict:
        try:
            for skill in self.skills:
                result = await skill.execute(context)
                self.completed.append((skill, result))
                context = {**context, **result}
            return context
        except Exception as e:
            await self.compensate()
            raise
    
    async def compensate(self):
        for skill, result in reversed(self.completed):
            if hasattr(skill, 'compensate'):
                await skill.compensate(result)
```

### Dependency Resolution

Build a directed acyclic graph of skill invocations:

```python
def resolve_dependencies(skills: List[Skill]) -> List[List[Skill]]:
    """Returns skills grouped by execution tier (parallel within tier)"""
    graph = {}
    for skill in skills:
        deps = skill.manifest.get("dependencies", [])
        graph[skill.id] = [d for d in deps if d in skill_registry]
    
    # Topological sort into execution tiers
    tiers = []
    remaining = set(graph.keys())
    
    while remaining:
        tier = [s for s in remaining if all(d not in remaining for d in graph[s])]
        tiers.append([skill_registry[s] for s in tier])
        remaining -= set(tier)
    
    return tiers
```

### Parallel Skill Execution

```python
async def execute_parallel_skills(skills: List[Skill], context: dict):
    results = await asyncio.gather(
        *[skill.execute(context) for skill in skills],
        return_exceptions=True
    )
    
    # Aggregate results, handling partial failures
    aggregated = {}
    for skill, result in zip(skills, results):
        if isinstance(result, Exception):
            aggregated[skill.id] = {"error": str(result), "fallback": skill.get_fallback()}
        else:
            aggregated[skill.id] = result
    
    return aggregated
```

---

## Subagent Pattern

For complex skills, invoke them as isolated subagents that receive their own focused prompt. Only the final result returns to the main agent, preventing "context rot."

### When to Use Subagents

- Skill requires extensive instructions
- Task is complex enough to need dedicated context
- Multiple skills might interfere with each other
- Skill output is well-defined and can be cleanly passed back

### Subagent Invocation

```python
async def invoke_as_subagent(skill: Skill, task_context: dict) -> dict:
    subagent_prompt = f"""
You are a specialized agent for {skill.manifest['name']}.

{skill.instructions}

## Task
{task_context['specific_task']}

## Input
{json.dumps(task_context['input'])}

## Required Output Format
{skill.output_schema}
"""
    
    result = await llm.generate(subagent_prompt)
    return parse_structured_output(result, skill.output_schema)
```

---

## Circuit Breakers

Protect against cascading failures when skills become unavailable:

```python
class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"
    
    def __init__(self, failure_threshold=5, reset_timeout=30):
        self.state = self.CLOSED
        self.failures = 0
        self.threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure = None
    
    async def call(self, func, *args):
        if self.state == self.OPEN:
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = self.HALF_OPEN
            else:
                raise CircuitOpenError()
        
        try:
            result = await func(*args)
            self.failures = 0
            self.state = self.CLOSED
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = self.OPEN
                self.last_failure = time.time()
            raise
```

---

## Complete Orchestration Architecture

### Five-Layer Design

| Layer | Responsibility | Key Patterns |
|-------|----------------|--------------|
| **Discovery** | Find and load skills | Directory scanning, file watching, manifest parsing |
| **Registry** | Index capabilities | Plugin registry, embedding index, activation event mapping |
| **Routing** | Match tasks to skills | Keyword matching, semantic search, LLM classification |
| **Composition** | Combine multiple skills | Saga pattern, parallel execution, dependency resolution |
| **Execution** | Run skills durably | Durable execution, compensation, circuit breakers |

### Complete Task Handling Flow

```python
class SkillOrchestrator:
    async def handle_task(self, task: str, context: dict) -> dict:
        # 1. Find matching skills (tiered matching)
        candidates = self.registry.find_matching_skills(task)
        
        # 2. Score and select
        scores = [(s, self.score_skill(s, task, context)) for s in candidates]
        selected = [s for s, score in scores if score > 0.5]
        
        if not selected:
            return self.handle_no_capability(task)
        
        # 3. Resolve dependencies and order
        execution_tiers = self.resolve_dependencies(selected)
        
        # 4. Generate execution prompt
        prompt = self.generate_execution_prompt(task, selected)
        
        # 5. Execute with durability
        result = await self.durable_executor.run(
            workflow=self.execute_tiers,
            args=(execution_tiers, prompt, context),
            compensation=self.compensate_all
        )
        
        return result
```

---

## Skill Registration Workflow

### Convention-Based Discovery

New skills require zero orchestrator changes through convention:

```
skills/
├── web-search/
│   ├── manifest.json
│   ├── instructions.md
│   └── handler.py
├── code-execution/
│   ├── manifest.json
│   ├── instructions.md
│   └── handler.py
└── data-analysis/
    ├── manifest.json
    └── instructions.md
```

### Directory Watching

```python
class SkillWatcher:
    def __init__(self, registry: SkillRegistry, skills_dir: Path):
        self.registry = registry
        self.observer = Observer()
        self.observer.schedule(
            SkillDirectoryHandler(registry),
            str(skills_dir),
            recursive=True
        )
    
    def start(self):
        self.observer.start()

class SkillDirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith("manifest.json"):
            skill_dir = Path(event.src_path).parent
            self.registry.register_skill(skill_dir)
    
    def on_modified(self, event):
        if event.src_path.endswith("manifest.json"):
            skill_dir = Path(event.src_path).parent
            self.registry.reload_skill(skill_dir)
```

### Key Principle

The **manifest schema is the contract**—any directory with a valid manifest becomes a discoverable skill without touching orchestrator code.

---

## Skill Activation in Execution Prompts

When generating prompts, include skill activation hints:

```markdown
## Required Skills
This task may require the following capabilities:
- **web-search**: For retrieving current information
- **code-execution**: For running and testing code
- **file-creation**: For generating output files

## Skill Usage
When you need to use a skill:
1. State which skill capability you're using
2. Provide the required inputs per the schema
3. Process the skill output before continuing
```

---

## Tool Description Best Practices

The critical lesson from AutoGPT and BabyAGI: **tool descriptions must be precise and differentiated**.

### Bad Description
```
"handles data"
```

### Good Description
```
"parses CSV files and extracts column statistics including mean, 
median, mode, and standard deviation for numeric columns"
```

### Description Guidelines

1. **Be specific**: Include exact operations, not vague categories
2. **Mention input/output**: What goes in, what comes out
3. **State limitations**: What the skill cannot do
4. **Differentiate**: How this differs from similar skills
5. **Include examples**: Typical use cases

---

## Key Insights for Skill Design

### Skills Should Be First-Class Entities
By adopting MCP's dynamic capability discovery, VSCode's activation events, and LangChain's tool schemas, an orchestrator can automatically integrate new skills without code changes.

### Weighted Scoring Enables Reliability
Combined with circuit breakers and compensation logic, this ensures reliable operation even when individual skills fail.

### The Trade-Off
This architecture trades some performance (embedding calculations, LLM routing calls) for dramatic gains in extensibility and maintainability. For systems where skills evolve frequently, this trade-off decisively favors automatic discovery.

### Context is King
Each skill's instructions should assume zero prior context—the orchestrator will provide what's needed through the execution prompt.

### Composition Over Complexity
Prefer composing simple skills over building complex monolithic ones. Simple skills are easier to test, debug, and replace.
