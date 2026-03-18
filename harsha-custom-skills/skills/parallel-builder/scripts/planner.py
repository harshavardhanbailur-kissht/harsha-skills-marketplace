#!/usr/bin/env python3
"""
Parallel Skill Builder - Planner Module

Decomposes feature descriptions into a DAG of parallel subtasks using Claude Opus 4.6.
Implements topological sorting to identify execution layers for parallelization.

Usage:
    python planner.py --feature "Build a REST API with authentication" --output plan.json
"""

import argparse
import asyncio
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from anthropic import AsyncAnthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class InterfaceContract:
    """Specifies input/output contracts for a subtask."""

    input_spec: dict[str, Any]
    output_spec: dict[str, Any]
    constraints: list[str] = field(default_factory=list)


@dataclass
class SubTask:
    """Represents a single subtask in the execution DAG."""

    id: str
    title: str
    description: str
    dependencies: list[str] = field(default_factory=list)
    prompt: str = ""
    contract: InterfaceContract = field(default_factory=lambda: InterfaceContract(
        input_spec={}, output_spec={}
    ))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "dependencies": self.dependencies,
            "prompt": self.prompt,
            "contract": {
                "input_spec": self.contract.input_spec,
                "output_spec": self.contract.output_spec,
                "constraints": self.contract.constraints,
            },
        }


@dataclass
class ExecutionLayer:
    """Represents a layer of tasks that can execute in parallel."""

    layer_id: int
    task_ids: list[str] = field(default_factory=list)
    estimated_duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "layer_id": self.layer_id,
            "task_ids": self.task_ids,
            "estimated_duration_seconds": self.estimated_duration_seconds,
        }


@dataclass
class ExecutionPlan:
    """Complete execution plan with tasks, layers, and dependencies."""

    feature_description: str
    tasks: list[SubTask] = field(default_factory=list)
    layers: list[ExecutionLayer] = field(default_factory=list)
    estimated_total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "feature_description": self.feature_description,
            "tasks": [task.to_dict() for task in self.tasks],
            "layers": [layer.to_dict() for layer in self.layers],
            "estimated_total_tokens": self.estimated_total_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class TaskDecomposer:
    """Decomposes feature descriptions into parallel subtasks using Claude Opus."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the task decomposer.

        Args:
            api_key: Optional Anthropic API key. Uses ANTHROPIC_API_KEY env var if not provided.
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-opus-4-6"

    async def decompose_feature(self, feature_description: str) -> ExecutionPlan:
        """
        Decompose a feature description into a DAG of parallel subtasks.

        Args:
            feature_description: High-level description of the feature to build.

        Returns:
            ExecutionPlan containing tasks, layers, and dependencies.

        Raises:
            ValueError: If the response cannot be parsed or contains invalid structure.
        """
        logger.info(f"Decomposing feature: {feature_description}")

        system_prompt = """You are an expert software architect specializing in breaking down complex features into parallel subtasks.

Your task is to analyze a feature description and decompose it into a DAG (Directed Acyclic Graph) of subtasks that can be executed in parallel.

REQUIREMENTS:
1. Each subtask must be atomic and independently executable
2. Identify all dependencies between subtasks
3. Provide clear, actionable descriptions for each subtask
4. Include estimated tokens needed for each subtask (use 500-2000 range)
5. For each subtask, specify:
   - Unique ID (task_1, task_2, etc.)
   - Descriptive title
   - Detailed description
   - List of task IDs it depends on (empty if no dependencies)
   - Input specification (what data it needs)
   - Output specification (what it will produce)
   - Constraints or requirements

OUTPUT FORMAT (respond with valid JSON):
{
  "tasks": [
    {
      "id": "task_1",
      "title": "Task Title",
      "description": "Detailed description of what this task does",
      "dependencies": [],
      "input_spec": {"param_name": "description"},
      "output_spec": {"result_name": "description"},
      "constraints": ["constraint 1", "constraint 2"],
      "estimated_tokens": 800
    }
  ],
  "notes": "Brief explanation of decomposition strategy and parallelization opportunities"
}

Maximize parallelization: identify independent tasks that can run simultaneously."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Decompose this feature into parallel subtasks:\n\n{feature_description}",
                    }
                ],
            )

            # Extract JSON from response
            response_text = response.content[0].text
            task_data = self._extract_json(response_text)

            logger.info(f"Extracted {len(task_data['tasks'])} tasks from decomposition")

            # Build task objects
            tasks = []
            for task_info in task_data["tasks"]:
                contract = InterfaceContract(
                    input_spec=task_info.get("input_spec", {}),
                    output_spec=task_info.get("output_spec", {}),
                    constraints=task_info.get("constraints", []),
                )

                task = SubTask(
                    id=task_info["id"],
                    title=task_info["title"],
                    description=task_info["description"],
                    dependencies=task_info.get("dependencies", []),
                    contract=contract,
                )
                tasks.append(task)

            # Compute execution layers using topological sort
            layers = self._compute_execution_layers(tasks)

            # Generate optimized prompts for each task
            await self._generate_task_prompts(tasks, feature_description)

            # Estimate tokens and costs
            total_tokens = sum(
                task_info.get("estimated_tokens", 1000)
                for task_info in task_data["tasks"]
            )
            # Opus: $15/1M input, $45/1M output
            estimated_cost = (total_tokens * 1500) / 1_000_000

            plan = ExecutionPlan(
                feature_description=feature_description,
                tasks=tasks,
                layers=layers,
                estimated_total_tokens=total_tokens,
                estimated_cost_usd=estimated_cost,
            )

            logger.info(
                f"Execution plan created with {len(layers)} layers, "
                f"estimated {total_tokens} tokens, ${estimated_cost:.4f}"
            )

            return plan

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON in Claude response: {e}") from e
        except Exception as e:
            logger.error(f"Error during decomposition: {e}")
            raise

    def _extract_json(self, text: str) -> dict[str, Any]:
        """
        Extract JSON from response text, handling markdown code blocks.

        Args:
            text: Response text potentially containing JSON.

        Returns:
            Parsed JSON as dictionary.

        Raises:
            ValueError: If valid JSON cannot be extracted.
        """
        # Try to extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            text = json_match.group(1)

        # Also try finding raw JSON object
        try:
            start_idx = text.find("{")
            if start_idx != -1:
                # Try to find matching closing brace
                brace_count = 0
                for i in range(start_idx, len(text)):
                    if text[i] == "{":
                        brace_count += 1
                    elif text[i] == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            return json.loads(text[start_idx : i + 1])
        except json.JSONDecodeError:
            pass

        raise ValueError("Could not extract valid JSON from response")

    def _compute_execution_layers(self, tasks: list[SubTask]) -> list[ExecutionLayer]:
        """
        Compute execution layers using topological sort (Kahn's Algorithm).

        Identifies which tasks can run in parallel by grouping tasks into layers
        where all tasks in a layer have no dependencies on other tasks in that layer.

        Args:
            tasks: List of subtasks with dependencies.

        Returns:
            List of ExecutionLayer objects representing parallel execution groups.
        """
        # Build dependency graph
        task_by_id = {task.id: task for task in tasks}
        in_degree = {task.id: len(task.dependencies) for task in tasks}
        graph = {task.id: [] for task in tasks}

        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in graph:
                    graph[dep_id].append(task.id)

        layers = []
        processed = set()

        while len(processed) < len(tasks):
            # Find all tasks with in-degree 0
            current_layer_tasks = [
                task_id for task_id in in_degree if in_degree[task_id] == 0 and task_id not in processed
            ]

            if not current_layer_tasks:
                logger.warning("Circular dependency detected in task graph")
                break

            # Create layer
            layer = ExecutionLayer(
                layer_id=len(layers),
                task_ids=current_layer_tasks,
                estimated_duration_seconds=len(current_layer_tasks) * 2,  # Estimate 2s per task
            )
            layers.append(layer)

            # Update in-degrees for next layer
            for task_id in current_layer_tasks:
                processed.add(task_id)
                for dependent in graph[task_id]:
                    in_degree[dependent] -= 1

        logger.info(f"Computed {len(layers)} execution layers")
        return layers

    async def _generate_task_prompts(
        self, tasks: list[SubTask], feature_description: str
    ) -> None:
        """
        Generate optimized prompts for each subtask targeting Claude Sonnet.

        Args:
            tasks: List of subtasks to generate prompts for.
            feature_description: Original feature description for context.
        """
        logger.info("Generating optimized task prompts")

        for task in tasks:
            prompt = f"""You are working on a subtask as part of building: {feature_description}

SUBTASK: {task.title}
DESCRIPTION: {task.description}

INPUT SPECIFICATION:
{json.dumps(task.contract.input_spec, indent=2)}

OUTPUT SPECIFICATION:
{json.dumps(task.contract.output_spec, indent=2)}

CONSTRAINTS:
{chr(10).join(f"- {c}" for c in task.contract.constraints)}

Your task is to complete this subtask according to the specifications above.
Provide output in the exact format specified in the OUTPUT SPECIFICATION.
Ensure all constraints are satisfied.
Be thorough and production-ready in your implementation."""

            task.prompt = prompt

    async def save_plan(self, plan: ExecutionPlan, output_path: str) -> None:
        """
        Save the execution plan to a JSON file.

        Args:
            plan: ExecutionPlan to save.
            output_path: File path for the output JSON.
        """
        try:
            with open(output_path, "w") as f:
                f.write(plan.to_json())
            logger.info(f"Execution plan saved to {output_path}")
        except IOError as e:
            logger.error(f"Failed to save plan to {output_path}: {e}")
            raise


async def main():
    """Main entry point for the planner script."""
    parser = argparse.ArgumentParser(
        description="Decompose features into parallel subtasks using Claude Opus"
    )
    parser.add_argument(
        "--feature",
        type=str,
        required=True,
        help="Feature description to decompose",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="plan.json",
        help="Output file path for the execution plan (default: plan.json)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        decomposer = TaskDecomposer(api_key=args.api_key)
        plan = await decomposer.decompose_feature(args.feature)
        await decomposer.save_plan(plan, args.output)

        # Print summary
        print(f"\nExecution Plan Summary:")
        print(f"  Feature: {args.feature}")
        print(f"  Tasks: {len(plan.tasks)}")
        print(f"  Execution Layers: {len(plan.layers)}")
        print(f"  Estimated Tokens: {plan.estimated_total_tokens}")
        print(f"  Estimated Cost: ${plan.estimated_cost_usd:.4f}")
        print(f"  Output: {args.output}")

        # Print task details
        print(f"\nTasks:")
        for task in plan.tasks:
            deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
            print(f"  - {task.id}: {task.title}{deps}")

        # Print layers
        print(f"\nExecution Layers:")
        for layer in plan.layers:
            print(f"  Layer {layer.layer_id}: {', '.join(layer.task_ids)}")

        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
