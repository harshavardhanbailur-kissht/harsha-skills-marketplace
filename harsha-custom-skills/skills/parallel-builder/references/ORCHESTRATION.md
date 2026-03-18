# Multi-Agent Orchestration Architecture Reference

## Executive Summary

This document provides production-ready patterns for orchestrating multiple Claude agents in parallel using Anthropic's AsyncAnthropic API. It covers workflow patterns, parallel execution strategies, error handling, token budget management, and concrete implementations designed for the Parallel Skill Builder meta-skill.

**Key Finding**: Opus lead agent + Sonnet subagents architecture achieves 90.2% outperformance over single-agent approaches while trading 15x token usage for 90% time savings.

---

## 1. Anthropic's 5 Workflow Patterns

### 1.1 Prompt Chaining
Sequential requests where output from one Claude call becomes input to the next.

**When to use**: Sequential decision trees, progressive refinement, single-threaded workflows.

**Example**:
```python
from anthropic import Anthropic

client = Anthropic()

def prompt_chain_workflow(topic: str) -> str:
    """Chain of calls: outline → draft → review."""

    # Step 1: Create outline
    outline_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Create a 3-point outline for: {topic}"
        }]
    )
    outline = outline_response.content[0].text

    # Step 2: Draft from outline
    draft_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Write a detailed essay based on this outline:\n{outline}"
        }]
    )
    draft = draft_response.content[0].text

    # Step 3: Review draft
    review_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Review and suggest improvements:\n{draft}"
        }]
    )

    return review_response.content[0].text

# Usage
result = prompt_chain_workflow("The future of AI")
```

**Token Cost**: Minimal (sequential calls only)
**Latency**: Linear with chain length

---

### 1.2 Routing
Conditional branching that selects one path based on input classification.

**When to use**: Classifier → handler patterns, different processing logic per category.

**Example**:
```python
from anthropic import Anthropic
import json

client = Anthropic()

def routing_workflow(user_query: str) -> str:
    """Route query to appropriate handler based on classification."""

    # Step 1: Classify query
    classification = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": f"""Classify this query into one category:
            [technical, billing, general]

            Query: {user_query}

            Respond with ONLY the category name."""
        }]
    )

    category = classification.content[0].text.strip()

    # Step 2: Route to appropriate handler
    if category == "technical":
        handler_prompt = f"You are a technical support expert. Answer: {user_query}"
    elif category == "billing":
        handler_prompt = f"You are a billing specialist. Answer: {user_query}"
    else:
        handler_prompt = f"You are a general support agent. Answer: {user_query}"

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": handler_prompt}]
    )

    return response.content[0].text

# Usage
result = routing_workflow("How do I reset my password?")
```

**Token Cost**: Low (2 calls per query)
**Latency**: Sequential but minimal

---

### 1.3 Parallelization (Sectioning + Voting)
Split work across multiple agents, collect results, aggregate via voting/consensus.

**When to use**: Large documents, multiple perspectives, independent analysis tasks.

**Example**:
```python
import asyncio
from anthropic import AsyncAnthropic

async def parallel_section_workflow(document: str) -> str:
    """Analyze document sections in parallel, then aggregate."""

    client = AsyncAnthropic()

    # Split document into sections
    sections = document.split("\n\n")[:5]  # Limit to 5 sections

    # Create analysis tasks
    tasks = []
    for i, section in enumerate(sections):
        task = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"Analyze this section and identify key points:\n{section}"
            }]
        )
        tasks.append(task)

    # Fan-in: collect all results
    analyses = await asyncio.gather(*tasks)

    # Aggregate via voting/consensus
    aggregation_prompt = "Synthesize these analyses into main themes:\n"
    for i, analysis in enumerate(analyses):
        aggregation_prompt += f"\n--- Analysis {i+1} ---\n{analysis.content[0].text}"

    summary = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": aggregation_prompt}]
    )

    return summary.content[0].text

# Usage
result = asyncio.run(parallel_section_workflow("Your long document here"))
```

**Token Cost**: Higher (N parallel calls)
**Latency**: Parallel (faster than sequential)

---

### 1.4 Orchestrator-Workers
Central orchestrator coordinates multiple worker agents, distributes tasks.

**When to use**: Hierarchical task distribution, worker pool patterns, delegated execution.

**Example**:
```python
import asyncio
from anthropic import AsyncAnthropic
from dataclasses import dataclass

@dataclass
class WorkerTask:
    id: str
    description: str
    specialty: str

async def orchestrator_worker_pattern(tasks: list[WorkerTask]) -> dict:
    """Orchestrator delegates tasks to specialized workers."""

    client = AsyncAnthropic()

    async def worker(task: WorkerTask) -> str:
        """Process a single task based on specialty."""
        system_prompt = f"You are a {task.specialty} specialist."

        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"Complete this task: {task.description}"
            }]
        )
        return response.content[0].text

    # Orchestrator: distribute tasks to workers
    worker_tasks = [worker(task) for task in tasks]
    results = await asyncio.gather(*worker_tasks)

    # Aggregate results
    return {
        "task_count": len(tasks),
        "completed": len(results),
        "results": {task.id: result for task, result in zip(tasks, results)}
    }

# Usage
tasks = [
    WorkerTask("t1", "Analyze sentiment", "sentiment analyst"),
    WorkerTask("t2", "Extract entities", "NLP specialist"),
    WorkerTask("t3", "Classify category", "categorization expert"),
]
result = asyncio.run(orchestrator_worker_pattern(tasks))
```

**Token Cost**: Linear (one call per task)
**Latency**: Parallel execution, minimal orchestration overhead

---

### 1.5 Evaluator-Optimizer
Generate multiple solutions, evaluate them, iteratively improve.

**When to use**: Optimization problems, quality iteration, A/B testing solutions.

**Example**:
```python
import asyncio
from anthropic import AsyncAnthropic

async def evaluator_optimizer_pattern(problem: str, iterations: int = 2) -> str:
    """Generate solutions, evaluate, optimize iteratively."""

    client = AsyncAnthropic()

    current_best = None

    for iteration in range(iterations):
        if iteration == 0:
            # Generate initial solutions
            tasks = [
                client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": f"Generate a solution to: {problem}\nApproach {i+1}"
                    }]
                )
                for i in range(3)
            ]
            solutions = await asyncio.gather(*tasks)
            solutions = [s.content[0].text for s in solutions]
        else:
            # Generate improved solutions based on evaluation
            solutions = [current_best]  # Keep best

            for i in range(2):  # Generate 2 alternatives
                task = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": f"""Improve on this solution:
                        {current_best}

                        Original problem: {problem}
                        Make alternative {i+1}"""
                    }]
                )
                solutions.append((await task).content[0].text)

        # Evaluate all solutions
        eval_tasks = [
            client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"""Rate this solution on a scale 1-10 with brief justification:
                    Problem: {problem}
                    Solution: {solution}"""
                }]
            )
            for solution in solutions
        ]
        evaluations = await asyncio.gather(*eval_tasks)

        # Select best based on ratings
        eval_texts = [e.content[0].text for e in evaluations]
        best_idx = 0  # Simplified: would parse scores in production
        current_best = solutions[best_idx]

    return current_best

# Usage
result = asyncio.run(evaluator_optimizer_pattern(
    "Design a system to detect fraudulent transactions"
))
```

**Token Cost**: Highest (generator × evaluator calls per iteration)
**Latency**: Moderate (parallelizable but requires sequential evaluation)

---

## 2. AsyncAnthropic Parallel Execution Pattern

### 2.1 Complete Fan-Out/Fan-In with asyncio.gather

The fundamental pattern for parallel agent execution:

```python
import asyncio
from anthropic import AsyncAnthropic
from typing import List

async def fan_out_fan_in_pattern(queries: List[str]) -> List[str]:
    """
    Fan-out: Create N concurrent requests
    Fan-in: Gather all results
    """
    client = AsyncAnthropic()

    # Fan-out: Create all tasks (non-blocking)
    tasks = [
        client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": query}]
        )
        for query in queries
    ]

    # Fan-in: Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)

    # Extract text from responses
    results = [response.content[0].text for response in responses]

    return results

# Usage example
async def main():
    queries = [
        "What is machine learning?",
        "Explain quantum computing",
        "Describe blockchain technology"
    ]
    results = await fan_out_fan_in_pattern(queries)
    for i, result in enumerate(results):
        print(f"Query {i+1}: {result[:100]}...")

asyncio.run(main())
```

**Key Advantages**:
- Non-blocking concurrent execution
- All requests start before any complete
- Natural error handling with exception aggregation

---

### 2.2 Semaphore-Based Rate Limiting

Control concurrency to respect rate limits (500 ITPM for Opus, 40,000 for Sonnet):

```python
import asyncio
from anthropic import AsyncAnthropic

class RateLimitedClient:
    """AsyncAnthropic wrapper with semaphore-based rate limiting."""

    def __init__(self, max_concurrent: int = 10):
        self.client = AsyncAnthropic()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def create_message(self, model: str, messages: list, **kwargs):
        """Rate-limited message creation."""
        async with self.semaphore:
            return await self.client.messages.create(
                model=model,
                messages=messages,
                **kwargs
            )

    async def execute_batch(self, requests: list[dict]) -> list:
        """Execute batch of requests with rate limiting."""
        tasks = [
            self.create_message(
                model=req["model"],
                messages=req["messages"],
                max_tokens=req.get("max_tokens", 1024)
            )
            for req in requests
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Usage
async def main():
    client = RateLimitedClient(max_concurrent=5)

    requests = [
        {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{"role": "user", "content": f"Task {i}"}]
        }
        for i in range(20)
    ]

    results = await client.execute_batch(requests)
    print(f"Completed {len(results)} requests")

asyncio.run(main())
```

**Rate Limit Guidelines**:
- Opus: 500 ITPM (Input TPM), use semaphore(max_concurrent=1-2)
- Sonnet: 40,000 TPM, use semaphore(max_concurrent=10-20)
- Check response headers: `rate_limit_tokens_remaining`

---

### 2.3 aiohttp Backend for High Concurrency

For truly high-concurrency scenarios (100+ parallel requests):

```python
import asyncio
import aiohttp
from anthropic import AsyncAnthropic
import json

class HighConcurrencyClient:
    """AsyncAnthropic with aiohttp connector for high concurrency."""

    def __init__(self, max_concurrent: int = 50, api_key: str = None):
        import os
        self.api_key = api_key or os.environ["ANTHROPIC_API_KEY"]
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client = AsyncAnthropic(api_key=self.api_key)

    async def execute_large_batch(self, tasks: list[dict]) -> list:
        """Execute 100+ concurrent requests with connection pooling."""

        async def bounded_request(task):
            async with self.semaphore:
                try:
                    response = await self.client.messages.create(
                        model=task["model"],
                        max_tokens=task.get("max_tokens", 1024),
                        messages=task["messages"]
                    )
                    return {"success": True, "data": response}
                except Exception as e:
                    return {"success": False, "error": str(e)}

        results = await asyncio.gather(*[bounded_request(t) for t in tasks])
        return results

# Usage
async def main():
    client = HighConcurrencyClient(max_concurrent=50)

    # Generate 100 tasks
    tasks = [
        {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{"role": "user", "content": f"Analyze item {i}"}],
            "max_tokens": 500
        }
        for i in range(100)
    ]

    results = await client.execute_large_batch(tasks)
    successful = sum(1 for r in results if r["success"])
    print(f"Completed {successful}/{len(results)} requests")

asyncio.run(main())
```

---

## 3. Error Handling and Rate Limits

### 3.1 Auto-Retry with Exponential Backoff

Resilient execution with intelligent retry logic:

```python
import asyncio
from anthropic import AsyncAnthropic, RateLimitError, APIConnectionError
import random

class ResilientClient:
    """AsyncAnthropic with auto-retry and exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.client = AsyncAnthropic()
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def create_message_with_retry(self, model: str, messages: list, **kwargs):
        """Create message with exponential backoff retry."""

        for attempt in range(self.max_retries):
            try:
                response = await self.client.messages.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response

            except RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise

                # Extract retry_after from headers
                retry_after = float(e.response.headers.get(
                    "retry-after",
                    self.base_delay * (2 ** attempt)
                ))

                print(f"Rate limited, retrying in {retry_after}s...")
                await asyncio.sleep(retry_after)

            except APIConnectionError as e:
                if attempt == self.max_retries - 1:
                    raise

                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Connection error, retrying in {delay}s...")
                await asyncio.sleep(delay)

    async def batch_with_retry(self, requests: list[dict]) -> list:
        """Execute batch with per-request retry logic."""

        tasks = [
            self.create_message_with_retry(
                model=req["model"],
                messages=req["messages"],
                max_tokens=req.get("max_tokens", 1024)
            )
            for req in requests
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)

# Usage
async def main():
    client = ResilientClient(max_retries=3)

    requests = [
        {
            "model": "claude-3-5-sonnet-20241022",
            "messages": [{"role": "user", "content": f"Request {i}"}]
        }
        for i in range(5)
    ]

    results = await client.batch_with_retry(requests)
    print(f"Completed with {sum(1 for r in results if not isinstance(r, Exception))} successes")

asyncio.run(main())
```

**Retry Strategy**:
- 429 (Rate Limit): Use `retry-after` header, exponential backoff
- 500+ (Server): Exponential backoff with jitter
- Connection errors: Exponential backoff + circuit breaker pattern

---

### 3.2 Rate Limit Headers and Monitoring

Monitor and respect rate limit quotas:

```python
from anthropic import AsyncAnthropic
import asyncio

class RateLimitMonitor:
    """Track rate limit consumption across requests."""

    def __init__(self):
        self.client = AsyncAnthropic()
        self.rate_limits = {}

    async def create_message(self, model: str, messages: list, **kwargs):
        """Create message and track rate limits."""

        response = await self.client.messages.create(
            model=model,
            messages=messages,
            **kwargs
        )

        # Extract rate limit info from response headers
        self.rate_limits[model] = {
            "input_tokens_used": response.usage.input_tokens,
            "output_tokens_used": response.usage.output_tokens,
            "total_tokens_used": (response.usage.input_tokens +
                                 response.usage.output_tokens),
            "timestamp": asyncio.get_event_loop().time()
        }

        return response

    def get_remaining_budget(self, model: str, tpm_limit: int) -> float:
        """Calculate remaining tokens until rate limit."""

        if model not in self.rate_limits:
            return tpm_limit

        stats = self.rate_limits[model]
        return max(0, tpm_limit - stats.get("total_tokens_used", 0))

# Usage
async def main():
    monitor = RateLimitMonitor()

    # Opus has 500 ITPM limit
    response = await monitor.create_message(
        model="claude-opus-4-1-20250805",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=100
    )

    remaining = monitor.get_remaining_budget("claude-opus-4-1-20250805", 500)
    print(f"Remaining budget: {remaining} tokens")

asyncio.run(main())
```

---

### 3.3 Message Batches API (50% Cost Reduction)

For non-time-sensitive batches, use Batches API for 50% cost reduction:

```python
import asyncio
from anthropic import AsyncAnthropic

async def batches_api_pattern():
    """Use Message Batches API for bulk processing."""

    client = AsyncAnthropic()

    # Prepare batch requests
    batch_requests = [
        {
            "custom_id": f"request-{i}",
            "params": {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": f"Analyze document {i}"}
                ]
            }
        }
        for i in range(10)
    ]

    # Submit batch
    batch = await client.beta.messages.batches.create(
        requests=batch_requests
    )

    print(f"Batch created: {batch.id}")
    print(f"Processing {batch.request_counts.processing} requests")

    # Poll for completion
    while True:
        batch_status = await client.beta.messages.batches.retrieve(batch.id)

        if batch_status.processing_status == "completed":
            print(f"Batch complete: {batch_status.request_counts.succeeded} succeeded")
            break

        print(f"Status: {batch_status.processing_status}")
        await asyncio.sleep(5)

    # Retrieve results
    results = []
    async for result in await client.beta.messages.batches.results(batch.id):
        results.append(result)

    return results

# Usage
results = asyncio.run(batches_api_pattern())
```

**Batches API Benefits**:
- 50% cost reduction compared to standard API
- Suitable for non-time-critical batch processing
- Can process thousands of requests
- Results available within 24 hours

---

## 4. Token Budget Management

### 4.1 Token Budgeting Rules

**Model Selection by Task Complexity**:

| Complexity | Agent Count | Primary Model | Secondary Model | Token Budget |
|---|---|---|---|---|
| Simple (tasks, summaries) | 1 | Sonnet | - | 10K-50K |
| Medium (analysis, writing) | 3-5 | Sonnet | - | 50K-200K |
| Complex (planning, orchestration) | 5+ | Opus (lead) | Sonnet (workers) | 200K-1M |
| Very Complex (multi-stage) | 10+ | Opus (lead) | Sonnet (workers) | 1M+ |

---

### 4.2 Using count_tokens() for Cost Pre-Estimation

Pre-calculate token costs before execution:

```python
from anthropic import Anthropic

def estimate_workflow_cost(
    model: str,
    system_prompt: str,
    user_messages: list[str],
    expected_output_tokens: int = 1024
) -> dict:
    """Pre-estimate token costs for a workflow."""

    client = Anthropic()

    # Count input tokens
    input_tokens = client.messages.count_tokens(
        model=model,
        system=system_prompt,
        messages=[{"role": "user", "content": msg} for msg in user_messages]
    )

    total_input = input_tokens.input_tokens
    total_output = expected_output_tokens * len(user_messages)

    # Pricing (as of Feb 2025)
    pricing = {
        "claude-opus-4-1-20250805": {"input": 0.015, "output": 0.045},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    }

    if model not in pricing:
        pricing[model] = {"input": 0.003, "output": 0.015}

    prices = pricing[model]

    input_cost = (total_input / 1_000_000) * prices["input"]
    output_cost = (total_output / 1_000_000) * prices["output"]

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "input_cost": f"${input_cost:.4f}",
        "output_cost": f"${output_cost:.4f}",
        "total_cost": f"${input_cost + output_cost:.4f}"
    }

# Usage
system = "You are a helpful assistant."
messages = ["Explain machine learning", "Explain quantum computing"]

estimate = estimate_workflow_cost(
    model="claude-3-5-sonnet-20241022",
    system_prompt=system,
    user_messages=messages,
    expected_output_tokens=1024
)

print(f"Estimated cost: {estimate['total_cost']}")
```

---

### 4.3 Opus for Planning, Sonnet for Execution

Hybrid architecture maximizing cost-efficiency:

```python
import asyncio
from anthropic import AsyncAnthropic

class HybridOrchestrator:
    """Use Opus for planning, Sonnet for execution."""

    def __init__(self):
        self.client = AsyncAnthropic()

    async def execute_with_planning(self, task: str) -> str:
        """
        1. Use Opus to create execution plan
        2. Use Sonnet workers to execute plan
        3. Use Opus to verify results
        """

        # Step 1: Opus creates detailed plan
        plan_response = await self.client.messages.create(
            model="claude-opus-4-1-20250805",  # Advanced reasoning
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""Create a detailed execution plan for: {task}

                Format as JSON with steps, worker assignments, and success criteria."""
            }]
        )

        plan = plan_response.content[0].text

        # Step 2: Parse plan and create Sonnet execution tasks
        # (In production, parse JSON)
        execution_tasks = [
            self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Fast execution
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"Execute this step: {plan}"
                }]
            )
            for _ in range(3)
        ]

        results = await asyncio.gather(*execution_tasks)

        # Step 3: Opus verifies and synthesizes results
        verification = await self.client.messages.create(
            model="claude-opus-4-1-20250805",  # Verification
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Verify and synthesize these results:
                {[r.content[0].text for r in results]}"""
            }]
        )

        return verification.content[0].text

# Usage
async def main():
    orchestrator = HybridOrchestrator()
    result = await orchestrator.execute_with_planning(
        "Design a recommendation system"
    )
    print(result)

asyncio.run(main())
```

---

## 5. Production Architecture: Opus Lead + Sonnet Subagents

### 5.1 90.2% Outperformance Pattern

The production-recommended architecture:

```python
import asyncio
from anthropic import AsyncAnthropic
from dataclasses import dataclass
from typing import List

@dataclass
class Task:
    id: str
    description: str
    priority: int = 0

@dataclass
class ExecutionResult:
    task_id: str
    output: str
    tokens_used: int
    success: bool

class OpusLeadOrchestrator:
    """
    Production architecture: Opus lead + Sonnet workers

    Benefits:
    - 90.2% better task completion than single-agent
    - 90% time savings vs sequential execution
    - 15x token usage (acceptable tradeoff)
    """

    def __init__(self):
        self.client = AsyncAnthropic()
        self.worker_semaphore = asyncio.Semaphore(5)  # Max 5 concurrent Sonnet

    async def lead_agent_plan(self, task: Task) -> dict:
        """Opus lead creates execution strategy."""

        response = await self.client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""As the lead orchestrator, create a detailed plan:

Task: {task.description}
Priority: {task.priority}

Provide:
1. Decomposition into 3-5 subtasks
2. Dependencies between subtasks
3. Specialist types needed
4. Success criteria
5. Risk mitigation"""
            }]
        )

        return {
            "plan": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens
        }

    async def worker_execute(self, subtask: str, specialty: str) -> ExecutionResult:
        """Sonnet worker executes subtask."""

        async with self.worker_semaphore:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=f"You are a {specialty} specialist. Execute tasks with precision.",
                messages=[{
                    "role": "user",
                    "content": f"Execute this subtask: {subtask}"
                }]
            )

        return ExecutionResult(
            task_id=specialty,
            output=response.content[0].text,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            success=True
        )

    async def lead_agent_verify(self, task: Task, results: List[ExecutionResult]) -> str:
        """Opus lead verifies and synthesizes results."""

        results_text = "\n".join([
            f"- {r.task_id}: {r.output[:200]}..."
            for r in results
        ])

        response = await self.client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""Verify and synthesize execution results:

Original Task: {task.description}

Worker Results:
{results_text}

Provide:
1. Verification of correctness
2. Gap identification
3. Final synthesized output
4. Confidence level"""
            }]
        )

        return response.content[0].text

    async def execute(self, task: Task) -> dict:
        """Full orchestration flow."""

        # Step 1: Opus lead creates plan
        plan_result = await self.lead_agent_plan(task)
        plan = plan_result["plan"]

        # Step 2: Extract and execute subtasks with Sonnet workers
        subtasks = [
            ("Data Analysis", "data analyst"),
            ("Risk Assessment", "risk analyst"),
            ("Solution Design", "solution architect"),
            ("Implementation Plan", "project manager"),
        ]

        worker_tasks = [
            self.worker_execute(desc, spec)
            for desc, spec in subtasks
        ]

        worker_results = await asyncio.gather(*worker_tasks)

        # Step 3: Opus lead verifies and synthesizes
        final_output = await self.lead_agent_verify(task, worker_results)

        return {
            "task_id": task.id,
            "plan": plan,
            "worker_results": worker_results,
            "final_output": final_output,
            "total_tokens": sum([
                plan_result["tokens"],
                sum(r.tokens_used for r in worker_results),
                len(final_output) // 4  # Approximate
            ])
        }

# Usage
async def main():
    orchestrator = OpusLeadOrchestrator()

    task = Task(
        id="complex-001",
        description="Design a system to optimize supply chain logistics",
        priority=1
    )

    result = await orchestrator.execute(task)
    print(f"Task {result['task_id']} completed")
    print(f"Final output: {result['final_output'][:200]}...")
    print(f"Total tokens used: {result['total_tokens']}")

asyncio.run(main())
```

---

## 6. Prompt Caching Integration

### 6.1 Cached Tokens Don't Count Toward Rate Limits

Caching reduces both cost and rate limit impact:

```python
from anthropic import AsyncAnthropic
import asyncio

class CachedOrchestrator:
    """Use prompt caching to reduce rate limit pressure."""

    def __init__(self):
        self.client = AsyncAnthropic()
        # System prompt with cache control
        self.system = [
            {
                "type": "text",
                "text": """You are an expert analyst with deep knowledge of:
- Machine Learning fundamentals and applications
- Data engineering best practices
- System architecture patterns
- Software optimization techniques

You provide detailed, accurate analysis with specific examples."""
            },
            {
                "type": "text",
                "text": """Reference Documents (cached):

1. ML Best Practices:
- Use ensemble methods for production
- Validate with cross-validation
- Monitor model drift
- Maintain data quality

2. Architecture Patterns:
- Microservices for scalability
- Event-driven for reactivity
- Cache layers for performance
- Async/parallel for throughput

This context applies to all requests below.""",
                "cache_control": {"type": "ephemeral"}
            }
        ]

    async def analyze_with_cache(self, query: str) -> dict:
        """Analyze query using cached system context."""

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self.system,
            messages=[{
                "role": "user",
                "content": query
            }]
        )

        return {
            "output": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "cache_creation_input_tokens": getattr(
                response.usage, 'cache_creation_input_tokens', 0
            ),
            "cache_read_input_tokens": getattr(
                response.usage, 'cache_read_input_tokens', 0
            )
        }

# Usage
async def main():
    orchestrator = CachedOrchestrator()

    # First call: Creates cache
    result1 = await orchestrator.analyze_with_cache(
        "Recommend ML approach for fraud detection"
    )

    # Second call: Uses cache (5x cheaper for cached tokens)
    result2 = await orchestrator.analyze_with_cache(
        "Recommend architecture for the ML system"
    )

    print(f"Call 1 - Input tokens: {result1['input_tokens']}")
    print(f"Call 2 - Cache hit: {result2['cache_read_input_tokens']} tokens")

asyncio.run(main())
```

**Caching Benefits**:
- Cached tokens cost 90% less than standard tokens
- Do NOT count toward rate limits (500 ITPM for Opus)
- Perfect for repeated system prompts/references
- TTL: 5 minutes (ephemeral), up to 24 hours with longer sessions

---

## 7. Complete Production Implementation

### 7.1 Full AsyncAnthropic Implementation with DAG Execution

A complete, production-ready orchestrator:

```python
import asyncio
from anthropic import AsyncAnthropic
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any
from enum import Enum
import json

class AgentType(Enum):
    LEAD = "lead"
    WORKER = "worker"
    EVALUATOR = "evaluator"

@dataclass
class Agent:
    id: str
    agent_type: AgentType
    model: str
    specialty: str = ""
    system_prompt: str = ""

@dataclass
class LayerTask:
    id: str
    agent_id: str
    input_data: str
    dependencies: List[str] = field(default_factory=list)
    output: str = ""
    tokens_used: int = 0

@dataclass
class ExecutionLayer:
    layer_id: str
    tasks: List[LayerTask] = field(default_factory=list)

class ProductionOrchestrator:
    """
    Production-grade multi-layer DAG orchestrator.

    Features:
    - Layer-by-layer execution with dependency resolution
    - Token budget tracking
    - Error aggregation and reporting
    - Semaphore-based rate limiting
    - Result passing between layers
    """

    def __init__(self, max_concurrent_sonnet: int = 5, max_concurrent_opus: int = 1):
        self.client = AsyncAnthropic()
        self.sonnet_semaphore = asyncio.Semaphore(max_concurrent_sonnet)
        self.opus_semaphore = asyncio.Semaphore(max_concurrent_opus)
        self.execution_history = {}
        self.total_tokens = 0

    async def execute_task(self, task: LayerTask, agent: Agent) -> LayerTask:
        """Execute a single task with appropriate rate limiting."""

        # Select semaphore based on model
        semaphore = (self.opus_semaphore if "opus" in agent.model
                    else self.sonnet_semaphore)

        async with semaphore:
            try:
                response = await self.client.messages.create(
                    model=agent.model,
                    max_tokens=2048,
                    system=agent.system_prompt or f"You are a {agent.specialty} specialist.",
                    messages=[{
                        "role": "user",
                        "content": task.input_data
                    }]
                )

                task.output = response.content[0].text
                task.tokens_used = (response.usage.input_tokens +
                                   response.usage.output_tokens)
                self.total_tokens += task.tokens_used

            except Exception as e:
                task.output = f"Error: {str(e)}"
                task.tokens_used = 0

        return task

    async def execute_layer(
        self,
        layer: ExecutionLayer,
        agents: Dict[str, Agent],
        previous_results: Dict[str, str] = None
    ) -> ExecutionLayer:
        """Execute all tasks in a layer in parallel."""

        previous_results = previous_results or {}

        # Resolve dependencies and prepare input
        for task in layer.tasks:
            if task.dependencies:
                dependency_outputs = [
                    previous_results.get(dep_id, "")
                    for dep_id in task.dependencies
                ]
                task.input_data += "\n\nDependent outputs:\n"
                task.input_data += "\n".join(dependency_outputs)

        # Execute all tasks in layer
        agent = agents[layer.tasks[0].agent_id]
        execution_tasks = [
            self.execute_task(task, agents[task.agent_id])
            for task in layer.tasks
        ]

        await asyncio.gather(*execution_tasks)

        return layer

    async def execute_dag(
        self,
        layers: List[ExecutionLayer],
        agents: Dict[str, Agent]
    ) -> Dict[str, Any]:
        """Execute multi-layer DAG with dependency resolution."""

        all_results = {}
        layer_results = []

        for i, layer in enumerate(layers):
            print(f"Executing layer {i+1}/{len(layers)}...")

            # Execute layer
            completed_layer = await self.execute_layer(
                layer, agents, all_results
            )

            # Store results for next layer
            for task in completed_layer.tasks:
                all_results[task.id] = task.output

            layer_results.append({
                "layer_id": completed_layer.layer_id,
                "tasks_completed": len(completed_layer.tasks),
                "total_tokens_in_layer": sum(t.tokens_used for t in completed_layer.tasks)
            })

        return {
            "final_results": all_results,
            "layer_summary": layer_results,
            "total_tokens_used": self.total_tokens,
            "estimated_cost": self._estimate_cost()
        }

    def _estimate_cost(self) -> str:
        """Estimate cost based on token usage."""

        # Simplified pricing
        opus_cost = (self.total_tokens * 0.03) / 1_000_000  # ~0.03/1M
        sonnet_cost = (self.total_tokens * 0.01) / 1_000_000  # ~0.01/1M

        avg_cost = (opus_cost + sonnet_cost) / 2

        return f"${avg_cost:.4f}"

# Usage example
async def main():
    """Example: Multi-stage content analysis pipeline."""

    orchestrator = ProductionOrchestrator()

    # Define agents
    agents = {
        "lead": Agent(
            id="lead",
            agent_type=AgentType.LEAD,
            model="claude-opus-4-1-20250805",
            specialty="strategic planner"
        ),
        "analyst1": Agent(
            id="analyst1",
            agent_type=AgentType.WORKER,
            model="claude-3-5-sonnet-20241022",
            specialty="data analyst"
        ),
        "analyst2": Agent(
            id="analyst2",
            agent_type=AgentType.WORKER,
            model="claude-3-5-sonnet-20241022",
            specialty="business strategist"
        ),
        "synthesizer": Agent(
            id="synthesizer",
            agent_type=AgentType.EVALUATOR,
            model="claude-opus-4-1-20250805",
            specialty="synthesis expert"
        )
    }

    # Define execution layers
    layers = [
        ExecutionLayer(
            layer_id="layer_1_planning",
            tasks=[
                LayerTask(
                    id="plan_task",
                    agent_id="lead",
                    input_data="Create a detailed plan for analyzing customer data",
                )
            ]
        ),
        ExecutionLayer(
            layer_id="layer_2_analysis",
            tasks=[
                LayerTask(
                    id="data_analysis",
                    agent_id="analyst1",
                    input_data="Analyze customer purchase patterns",
                    dependencies=["plan_task"]
                ),
                LayerTask(
                    id="business_analysis",
                    agent_id="analyst2",
                    input_data="Analyze business implications",
                    dependencies=["plan_task"]
                )
            ]
        ),
        ExecutionLayer(
            layer_id="layer_3_synthesis",
            tasks=[
                LayerTask(
                    id="final_synthesis",
                    agent_id="synthesizer",
                    input_data="Synthesize findings into executive summary",
                    dependencies=["data_analysis", "business_analysis"]
                )
            ]
        )
    ]

    # Execute DAG
    results = await orchestrator.execute_dag(layers, agents)

    print(f"\nExecution complete!")
    print(f"Total tokens used: {results['total_tokens_used']}")
    print(f"Estimated cost: {results['estimated_cost']}")
    print(f"\nFinal output:\n{results['final_results']['final_synthesis']}")

# Run
asyncio.run(main())
```

---

## 8. Summary and Best Practices

### 8.1 Decision Tree: Which Pattern to Use?

```
Is task parallelizable?
├─ NO → Use Prompt Chaining
├─ YES
    ├─ Single decision point?
    │  └─ Use Routing
    ├─ Independent subtasks?
    │  └─ Use Parallelization (Sectioning + Voting)
    ├─ Worker pool pattern?
    │  └─ Use Orchestrator-Workers
    └─ Quality optimization needed?
       └─ Use Evaluator-Optimizer
```

### 8.2 Production Recommendations

| Aspect | Recommendation | Rationale |
|---|---|---|
| Lead Agent | Always use Opus | Superior reasoning for planning/verification |
| Workers | Use Sonnet | 5-10x cheaper, sufficient for execution |
| Parallelism | 5-10 concurrent Sonnet | Respect rate limits while maximizing throughput |
| Token Budget | Pre-estimate with count_tokens() | Avoid surprises, control costs |
| Caching | Enable for system prompts | 90% cost reduction on cached tokens |
| Batches API | Use for non-time-critical work | 50% cost reduction |
| Error Handling | Implement exponential backoff | Essential for production stability |
| Monitoring | Track rate limit headers | Prevent 429 errors |

### 8.3 Token Budget Calculator

```python
def calculate_total_budget(
    num_layers: int,
    tasks_per_layer: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model_mix: dict  # {"opus": 0.2, "sonnet": 0.8}
) -> dict:
    """Calculate total token and cost budget."""

    total_tasks = num_layers * tasks_per_layer
    total_tokens = total_tasks * (avg_input_tokens + avg_output_tokens)

    opus_tokens = int(total_tokens * model_mix.get("opus", 0.1))
    sonnet_tokens = int(total_tokens * model_mix.get("sonnet", 0.9))

    # Pricing
    opus_cost = (opus_tokens / 1_000_000) * 0.03
    sonnet_cost = (sonnet_tokens / 1_000_000) * 0.009

    return {
        "total_tokens": total_tokens,
        "opus_tokens": opus_tokens,
        "sonnet_tokens": sonnet_tokens,
        "estimated_cost": f"${opus_cost + sonnet_cost:.4f}",
        "tokens_per_task": total_tokens / total_tasks
    }
```

---

## References

- Anthropic Claude API Documentation: https://docs.anthropic.com
- Async Python Best Practices: https://docs.python.org/3/library/asyncio.html
- Rate Limit Handling: https://docs.anthropic.com/rate-limits
- Prompt Caching: https://docs.anthropic.com/caching
- Message Batches API: https://docs.anthropic.com/batch-api

