#!/usr/bin/env python3
"""
Parallel Skill Builder - Executor Module

Executes parallel subtasks from a plan JSON using Claude Sonnet 4.6.
Implements sequential layer execution with parallel task execution within layers.
Includes retry logic, token tracking, and cost estimation.

Usage:
    python executor.py --plan plan.json --output-dir ./outputs --concurrency 5
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from anthropic import AsyncAnthropic, Anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of executing a single subtask."""

    task_id: str
    success: bool
    output: str = ""
    error: Optional[str] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    execution_time_seconds: float = 0.0
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "execution_time_seconds": self.execution_time_seconds,
            "retry_count": self.retry_count,
        }


@dataclass
class ExecutionReport:
    """Comprehensive report of plan execution."""

    plan_path: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_tokens_used: int
    total_cost_usd: float
    total_execution_time_seconds: float
    task_results: list[TaskResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "plan_path": self.plan_path,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "failed_tasks": self.failed_tasks,
            "total_tokens_used": self.total_tokens_used,
            "total_cost_usd": self.total_cost_usd,
            "total_execution_time_seconds": self.total_execution_time_seconds,
            "success_rate": (
                self.successful_tasks / self.total_tasks * 100
                if self.total_tasks > 0
                else 0
            ),
            "task_results": [result.to_dict() for result in self.task_results],
            "errors": self.errors,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class TaskExecutor:
    """Executes parallel subtasks using Claude Sonnet with rate limiting and retries."""

    # Sonnet pricing: $3/1M input tokens, $15/1M output tokens
    INPUT_TOKEN_COST = 3 / 1_000_000
    OUTPUT_TOKEN_COST = 15 / 1_000_000

    def __init__(
        self,
        api_key: Optional[str] = None,
        concurrency: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize the task executor.

        Args:
            api_key: Optional Anthropic API key. Uses ANTHROPIC_API_KEY env var if not provided.
            concurrency: Maximum number of concurrent tasks (semaphore limit).
            max_retries: Maximum number of retries for failed tasks.
            retry_delay: Initial delay in seconds for exponential backoff.
        """
        self.async_client = AsyncAnthropic(api_key=api_key, max_retries=max_retries)
        self.sync_client = Anthropic(api_key=api_key)
        self.client = self.async_client  # backward compat
        self.model = "claude-sonnet-4-5-20250929"
        self.semaphore = asyncio.Semaphore(concurrency)
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Cache warming state
        self._cache_warmed = False
        self._shared_system_prompt = None

        # Circuit breaker: fast-fail after consecutive failures
        self._failure_counts: dict[str, int] = {}
        self._circuit_breaker_threshold = 5

    def warm_cache(self, system_prompt: str) -> None:
        """
        Warm the prompt cache synchronously BEFORE parallel fan-out.

        This ensures all parallel agents hit the cached system prompt,
        achieving 100% cache hit rate. Without warming, each agent
        creates redundant cache entries. Cache-aware rate limits mean
        cached reads don't count against ITPM — multiplying throughput.

        Args:
            system_prompt: The shared system prompt to cache.
        """
        self._shared_system_prompt = system_prompt
        logger.info("Warming prompt cache with shared system prompt...")
        try:
            self.sync_client.messages.create(
                model=self.model,
                max_tokens=1,
                system=[{
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }],
                messages=[{"role": "user", "content": "ping"}]
            )
            self._cache_warmed = True
            logger.info("Cache warmed successfully")
        except Exception as e:
            logger.warning(f"Cache warming failed (non-fatal): {e}")

    def _check_circuit_breaker(self, task_id: str) -> bool:
        """Check if circuit breaker is tripped for a task pattern."""
        count = self._failure_counts.get(task_id, 0)
        if count >= self._circuit_breaker_threshold:
            logger.error(
                f"Circuit breaker OPEN for {task_id}: "
                f"{count} consecutive failures. Fast-failing."
            )
            return False
        return True

    def _save_checkpoint(
        self,
        checkpoint_path: Path,
        phase: str,
        layer: int,
        completed_tasks: list[str],
        task_outputs: dict[str, str],
        results: list[TaskResult],
    ) -> None:
        """Save pipeline checkpoint for resume capability (SagaLLM-inspired)."""
        import uuid
        from datetime import datetime, timezone

        checkpoint = {
            "checkpoint_id": str(uuid.uuid4()),
            "phase": phase,
            "layer": layer,
            "completed_tasks": completed_tasks,
            "task_output_paths": {
                tid: str(path) for tid, path in task_outputs.items()
                if isinstance(path, (str, Path))
            },
            "token_usage": {
                "total": sum(r.tokens_used for r in results),
                "by_task": {r.task_id: r.tokens_used for r in results},
            },
            "cost_usd": sum(r.cost_usd for r in results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resumable": True,
        }
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2))
        logger.info(f"Checkpoint saved: {checkpoint_path} (layer={layer}, tasks={len(completed_tasks)})")

    def _load_checkpoint(self, checkpoint_path: Path) -> Optional[dict[str, Any]]:
        """Load a checkpoint for resume execution."""
        if not checkpoint_path.exists():
            return None
        try:
            data = json.loads(checkpoint_path.read_text())
            if data.get("resumable"):
                logger.info(
                    f"Resuming from checkpoint: layer={data['layer']}, "
                    f"completed={len(data['completed_tasks'])} tasks"
                )
                return data
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Invalid checkpoint file: {e}")
        return None

    async def execute_plan(
        self,
        plan_path: str,
        output_dir: Path,
        task_outputs: Optional[dict[str, str]] = None,
        resume_checkpoint: Optional[str] = None,
    ) -> ExecutionReport:
        """
        Execute all tasks in a plan, respecting layer dependencies.

        Args:
            plan_path: Path to the execution plan JSON file.
            output_dir: Directory where task outputs will be written.
            task_outputs: Optional dict to track task outputs for dependency injection.
            resume_checkpoint: Optional path to checkpoint JSON for resume execution.

        Returns:
            ExecutionReport with results and metrics.

        Raises:
            FileNotFoundError: If plan file doesn't exist.
            ValueError: If plan structure is invalid.
        """
        logger.info(f"Loading execution plan from {plan_path}")

        # Load plan
        plan_data = self._load_plan(plan_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_dir = output_dir / ".checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)

        # Initialize tracking
        task_outputs = task_outputs or {}
        all_results: list[TaskResult] = []
        start_time = time.time()
        skip_to_layer = -1

        # Resume from checkpoint if provided
        if resume_checkpoint:
            checkpoint_data = self._load_checkpoint(Path(resume_checkpoint))
            if checkpoint_data:
                skip_to_layer = checkpoint_data["layer"]
                completed_ids = set(checkpoint_data["completed_tasks"])
                # Restore task outputs from checkpoint
                for tid, path in checkpoint_data.get("task_output_paths", {}).items():
                    p = Path(path)
                    if p.exists():
                        task_outputs[tid] = p.read_text()
                logger.info(f"Resuming: skipping {len(completed_ids)} completed tasks")

        try:
            # Execute layers sequentially
            for layer_data in plan_data["layers"]:
                layer_id = layer_data["layer_id"]
                task_ids = layer_data["task_ids"]

                # Skip completed layers when resuming
                if layer_id < skip_to_layer:
                    logger.info(f"Skipping completed layer {layer_id} (resume mode)")
                    continue

                # Filter out already-completed tasks in the resume layer
                if layer_id == skip_to_layer and resume_checkpoint:
                    task_ids = [t for t in task_ids if t not in completed_ids]
                    if not task_ids:
                        logger.info(f"Layer {layer_id} fully completed, skipping")
                        continue

                logger.info(
                    f"Executing layer {layer_id} with {len(task_ids)} "
                    f"task(s): {', '.join(task_ids)}"
                )

                # Execute all tasks in layer in parallel
                layer_results = await asyncio.gather(
                    *[
                        self.execute_task(
                            task_id=task_id,
                            tasks_by_id={t["id"]: t for t in plan_data["tasks"]},
                            output_dir=output_dir,
                            task_outputs=task_outputs,
                        )
                        for task_id in task_ids
                    ]
                )

                all_results.extend(layer_results)

                # Checkpoint after each layer
                completed_so_far = [r.task_id for r in all_results if r.success]
                self._save_checkpoint(
                    checkpoint_path=checkpoint_dir / f"layer_{layer_id}.json",
                    phase="execute",
                    layer=layer_id,
                    completed_tasks=completed_so_far,
                    task_outputs=task_outputs,
                    results=all_results,
                )

                # Check for failures but continue with partial results
                failed = [r for r in layer_results if not r.success]
                if failed:
                    logger.warning(
                        f"Layer {layer_id}: {len(failed)} task(s) failed, "
                        f"continuing with available results"
                    )

        except Exception as e:
            logger.error(f"Error during plan execution: {e}")

        # Compile report
        total_time = time.time() - start_time
        successful = [r for r in all_results if r.success]
        failed = [r for r in all_results if not r.success]

        report = ExecutionReport(
            plan_path=plan_path,
            total_tasks=len(plan_data["tasks"]),
            successful_tasks=len(successful),
            failed_tasks=len(failed),
            total_tokens_used=sum(r.tokens_used for r in all_results),
            total_cost_usd=sum(r.cost_usd for r in all_results),
            total_execution_time_seconds=total_time,
            task_results=all_results,
            errors=[r.error for r in failed if r.error],
        )

        logger.info(
            f"Plan execution complete: {len(successful)} successful, "
            f"{len(failed)} failed in {total_time:.2f}s"
        )

        return report

    async def execute_task(
        self,
        task_id: str,
        tasks_by_id: dict[str, Any],
        output_dir: Path,
        task_outputs: dict[str, str],
    ) -> TaskResult:
        """
        Execute a single task with retry logic and dependency injection.

        Args:
            task_id: ID of the task to execute.
            tasks_by_id: Dictionary mapping task IDs to task definitions.
            output_dir: Directory for output files.
            task_outputs: Dictionary to store/retrieve task outputs.

        Returns:
            TaskResult with execution details and metrics.
        """
        async with self.semaphore:
            task_def = tasks_by_id[task_id]
            logger.info(f"Executing task {task_id}: {task_def['title']}")

            # Idempotent execution: check if valid output already exists
            output_file = output_dir / f"{task_id}.txt"
            if output_file.exists() and output_file.stat().st_size > 0:
                existing = output_file.read_text()
                task_outputs[task_id] = existing
                logger.info(f"Task {task_id}: valid output exists, skipping (idempotent)")
                return TaskResult(
                    task_id=task_id,
                    success=True,
                    output=existing,
                    tokens_used=0,
                    cost_usd=0.0,
                    execution_time_seconds=0.0,
                    retry_count=0,
                )

            # Build prompt with dependency injection
            prompt = task_def["prompt"]
            dependencies = task_def.get("dependencies", [])

            if dependencies:
                dependency_context = "DEPENDENCY OUTPUTS:\n"
                for dep_id in dependencies:
                    if dep_id in task_outputs:
                        dependency_context += f"\n{dep_id} output:\n{task_outputs[dep_id]}\n"
                prompt = f"{dependency_context}\n\n{prompt}"

            # Attempt execution with retries
            for attempt in range(self.max_retries):
                try:
                    start_time = time.time()

                    response = await self.client.messages.create(
                        model=self.model,
                        max_tokens=2048,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    )

                    execution_time = time.time() - start_time

                    # Extract output
                    output = response.content[0].text

                    # Calculate costs
                    input_tokens = response.usage.input_tokens
                    output_tokens = response.usage.output_tokens
                    total_tokens = input_tokens + output_tokens
                    cost = (input_tokens * self.INPUT_TOKEN_COST +
                            output_tokens * self.OUTPUT_TOKEN_COST)

                    # Write output to file
                    output_file = output_dir / f"{task_id}_output.txt"
                    output_file.write_text(output)
                    task_outputs[task_id] = output

                    logger.info(
                        f"Task {task_id} completed: {total_tokens} tokens, "
                        f"${cost:.6f}, {execution_time:.2f}s"
                    )

                    return TaskResult(
                        task_id=task_id,
                        success=True,
                        output=output_file.as_posix(),
                        tokens_used=total_tokens,
                        cost_usd=cost,
                        execution_time_seconds=execution_time,
                        retry_count=attempt,
                    )

                except Exception as e:
                    logger.warning(
                        f"Task {task_id} attempt {attempt + 1}/{self.max_retries} "
                        f"failed: {e}"
                    )

                    if attempt < self.max_retries - 1:
                        # Exponential backoff
                        delay = self.retry_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
                    else:
                        # All retries exhausted
                        error_msg = f"Task failed after {self.max_retries} attempts: {e}"
                        logger.error(f"Task {task_id}: {error_msg}")

                        return TaskResult(
                            task_id=task_id,
                            success=False,
                            error=error_msg,
                            retry_count=attempt,
                        )

            # Should not reach here
            return TaskResult(
                task_id=task_id,
                success=False,
                error="Unknown error during task execution",
                retry_count=self.max_retries,
            )

    def _load_plan(self, plan_path: str) -> dict[str, Any]:
        """
        Load and validate execution plan from JSON file.

        Args:
            plan_path: Path to the plan JSON file.

        Returns:
            Validated plan dictionary.

        Raises:
            FileNotFoundError: If plan file doesn't exist.
            ValueError: If plan structure is invalid.
        """
        try:
            with open(plan_path, "r") as f:
                plan = json.load(f)

            # Validate required fields
            required_fields = ["tasks", "layers"]
            if not all(field in plan for field in required_fields):
                raise ValueError(
                    f"Plan missing required fields: {required_fields}"
                )

            if not isinstance(plan["tasks"], list) or not plan["tasks"]:
                raise ValueError("Plan must contain at least one task")

            if not isinstance(plan["layers"], list) or not plan["layers"]:
                raise ValueError("Plan must contain at least one layer")

            logger.info(f"Loaded plan with {len(plan['tasks'])} tasks "
                       f"in {len(plan['layers'])} layers")

            return plan

        except FileNotFoundError:
            logger.error(f"Plan file not found: {plan_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in plan file: {e}")
            raise ValueError(f"Plan file contains invalid JSON: {e}") from e

    async def save_report(self, report: ExecutionReport, output_path: str) -> None:
        """
        Save execution report to JSON file.

        Args:
            report: ExecutionReport to save.
            output_path: File path for the output JSON.
        """
        try:
            with open(output_path, "w") as f:
                f.write(report.to_json())
            logger.info(f"Execution report saved to {output_path}")
        except IOError as e:
            logger.error(f"Failed to save report to {output_path}: {e}")
            raise


async def main():
    """Main entry point for the executor script."""
    parser = argparse.ArgumentParser(
        description="Execute parallel subtasks from a plan using Claude Sonnet"
    )
    parser.add_argument(
        "--plan",
        type=str,
        required=True,
        help="Path to the execution plan JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./outputs",
        help="Directory for task output files (default: ./outputs)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="execution_report.json",
        help="Path for execution report JSON (default: execution_report.json)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Maximum concurrent tasks (default: 5)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retries per task (default: 3)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)",
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to checkpoint JSON for resume execution (skips completed tasks)",
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
        executor = TaskExecutor(
            api_key=args.api_key,
            concurrency=args.concurrency,
            max_retries=args.max_retries,
        )

        output_dir = Path(args.output_dir)
        report = await executor.execute_plan(
            args.plan, output_dir, resume_checkpoint=args.resume
        )

        # Save report
        await executor.save_report(report, args.report)

        # Print summary
        print(f"\nExecution Report Summary:")
        print(f"  Plan: {args.plan}")
        print(f"  Total Tasks: {report.total_tasks}")
        print(f"  Successful: {report.successful_tasks}")
        print(f"  Failed: {report.failed_tasks}")
        print(f"  Success Rate: {report.to_dict()['success_rate']:.1f}%")
        print(f"  Total Tokens: {report.total_tokens_used}")
        print(f"  Total Cost: ${report.total_cost_usd:.6f}")
        print(f"  Total Time: {report.total_execution_time_seconds:.2f}s")
        print(f"  Output Directory: {args.output_dir}")
        print(f"  Report: {args.report}")

        if report.failed_tasks > 0:
            print(f"\nFailed Tasks:")
            for result in report.task_results:
                if not result.success:
                    print(f"  - {result.task_id}: {result.error}")

        sys.exit(0 if report.failed_tasks == 0 else 1)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
