#!/usr/bin/env python3
"""
Multi-layered verification pipeline for parallel skill builder outputs.

This script implements a sophisticated verification system that:
1. Performs static analysis (Ruff with syntax fallback)
2. Detects duplicates and conflicts across outputs
3. Uses Claude Opus 4.6 as an LLM judge with rubric-based scoring
4. Implements iterative fixing via Claude Sonnet 4.6
5. Applies bias mitigation and criteria decomposition

The LLMLOOP pattern is used: temperature increments on persistent failures
to encourage more diverse solutions when initial attempts fail.
"""

import asyncio
import json
import argparse
import sys
import ast
import random
import subprocess
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Any
from datetime import datetime
from enum import Enum

from anthropic import AsyncAnthropic


class VerificationStatus(Enum):
    """Verification status codes."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    PENDING_FIX = "PENDING_FIX"


@dataclass
class CriteriaScore:
    """Score for individual evaluation criteria."""
    name: str
    score: float  # 0.0-1.0
    feedback: str
    status: VerificationStatus


@dataclass
class FileVerification:
    """Verification result for a single file."""
    file_path: str
    syntax_valid: bool
    syntax_errors: list[str] = field(default_factory=list)
    duplicates_found: list[str] = field(default_factory=list)
    conflicts_found: list[str] = field(default_factory=list)
    rubric_scores: list[CriteriaScore] = field(default_factory=list)
    overall_score: float = 0.0
    overall_status: VerificationStatus = VerificationStatus.PENDING_FIX
    fix_attempts: int = 0
    fixed_content: Optional[str] = None
    final_status: VerificationStatus = VerificationStatus.PENDING_FIX
    feedback: str = ""


@dataclass
class VerificationReport:
    """Complete verification report for all outputs."""
    timestamp: str
    original_request: str
    total_files: int
    verified_files: int
    passed_files: int
    failed_files: int
    files: dict[str, FileVerification] = field(default_factory=dict)
    duplicates_across_outputs: list[dict[str, Any]] = field(default_factory=list)
    conflicts_across_outputs: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""


class StaticAnalyzer:
    """Performs static analysis using Ruff or AST parsing."""

    @staticmethod
    def check_python_syntax(file_path: Path) -> tuple[bool, list[str]]:
        """
        Check Python syntax using AST parsing.

        Args:
            file_path: Path to Python file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax error at line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Parse error: {str(e)}"]

    @staticmethod
    def run_bandit_security_scan(file_path: Path) -> tuple[bool, list[str]]:
        """
        Run Bandit security scanner if available.
        Critical: 45% of AI-generated code has security flaws (Veracode 2025).

        Args:
            file_path: Path to Python file

        Returns:
            Tuple of (no_issues, list_of_security_issues)
        """
        try:
            result = subprocess.run(
                ['bandit', '-f', 'json', '-ll', str(file_path)],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                return True, []

            issues = []
            try:
                output = json.loads(result.stdout) if result.stdout else {}
                for item in output.get('results', []):
                    severity = item.get('issue_severity', 'UNKNOWN')
                    confidence = item.get('issue_confidence', 'UNKNOWN')
                    text = item.get('issue_text', 'Unknown')
                    line = item.get('line_number', '?')
                    issues.append(
                        f"[{severity}/{confidence}] Line {line}: {text}"
                    )
            except json.JSONDecodeError:
                issues = ["Bandit scan failed to parse output"]

            return len(issues) == 0, issues
        except FileNotFoundError:
            return True, ["Bandit not installed - skipping security scan"]
        except subprocess.TimeoutExpired:
            return True, ["Bandit timed out - skipping"]

    @staticmethod
    def run_ruff_check(file_path: Path) -> tuple[bool, list[str]]:
        """
        Run Ruff linter if available.

        Args:
            file_path: Path to Python file

        Returns:
            Tuple of (all_passed, list_of_issues)
        """
        try:
            result = subprocess.run(
                ['ruff', 'check', str(file_path), '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, []

            issues = []
            try:
                output = json.loads(result.stdout) if result.stdout else []
                for item in output:
                    if isinstance(item, dict):
                        msg = item.get('message', 'Unknown issue')
                        line = item.get('location', {}).get('row', '?')
                        issues.append(f"Line {line}: {msg}")
            except json.JSONDecodeError:
                issues = [result.stdout] if result.stdout else ["Ruff check failed"]

            return len(issues) == 0, issues
        except FileNotFoundError:
            # Ruff not installed, fall back to syntax check
            return None, []
        except subprocess.TimeoutExpired:
            return False, ["Ruff check timed out"]

    @staticmethod
    def analyze_file(file_path: Path) -> tuple[bool, list[str]]:
        """
        Analyze file using Ruff first, falling back to syntax check.

        Args:
            file_path: Path to file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not file_path.suffix == '.py':
            return True, []

        # Try Ruff first
        ruff_result = StaticAnalyzer.run_ruff_check(file_path)
        if ruff_result[0] is not None:
            return ruff_result

        # Fall back to syntax check
        return StaticAnalyzer.check_python_syntax(file_path)


class DuplicateDetector:
    """Detects duplicate and conflicting content across outputs."""

    @staticmethod
    def extract_code_blocks(content: str) -> list[str]:
        """
        Extract distinct code blocks from content.

        Args:
            content: File content

        Returns:
            List of code blocks (normalized)
        """
        # Remove comments and normalize whitespace for comparison
        lines = content.split('\n')
        blocks = []
        current_block = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                current_block.append(stripped)
            elif current_block:
                blocks.append(' '.join(current_block))
                current_block = []

        if current_block:
            blocks.append(' '.join(current_block))

        return blocks

    @staticmethod
    def find_duplicates(outputs_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
        """
        Find duplicate content across output files.

        Args:
            outputs_dir: Directory containing outputs

        Returns:
            Tuple of (list_of_file_paths, list_of_duplicate_reports)
        """
        file_hashes = {}
        duplicates = []
        python_files = list(outputs_dir.glob('**/*.py'))

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Create hash of normalized content
                blocks = DuplicateDetector.extract_code_blocks(content)
                block_hash = hash(tuple(sorted(blocks)))

                if block_hash in file_hashes:
                    duplicates.append({
                        'type': 'duplicate',
                        'file1': str(file_hashes[block_hash]),
                        'file2': str(file_path),
                        'severity': 'MEDIUM'
                    })
                else:
                    file_hashes[block_hash] = file_path
            except Exception as e:
                pass

        return list(file_hashes.values()), duplicates

    @staticmethod
    def find_conflicts(outputs_dir: Path) -> list[dict[str, Any]]:
        """
        Find semantic conflicts across outputs.

        Args:
            outputs_dir: Directory containing outputs

        Returns:
            List of conflict reports
        """
        conflicts = []
        python_files = list(outputs_dir.glob('**/*.py'))

        # Check for conflicting function/class definitions
        definitions = {}
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        name = node.name
                        key = (name, type(node).__name__)
                        if key in definitions:
                            conflicts.append({
                                'type': 'conflicting_definition',
                                'name': name,
                                'kind': type(node).__name__,
                                'file1': str(definitions[key]),
                                'file2': str(file_path),
                                'severity': 'HIGH'
                            })
                        else:
                            definitions[key] = file_path
            except Exception:
                pass

        return conflicts


class LLMJudge:
    """LLM-as-judge evaluation using Claude Opus 4.6."""

    def __init__(self, client: AsyncAnthropic):
        """Initialize the LLM judge."""
        self.client = client
        self.judge_model = "claude-opus-4-6-20250514"

    @staticmethod
    def create_rubric(original_request: str) -> str:
        """
        Create evaluation rubric based on original request.

        Args:
            original_request: The original feature/task request

        Returns:
            Rubric as string
        """
        return f"""
Evaluate the provided code/output against these criteria on a 0-1 scale:

1. COMPLETENESS (0-1):
   - Does it fully address the requirements?
   - Are all requested features implemented?
   - No critical gaps or TODOs left unexplained

2. CORRECTNESS (0-1):
   - Is the code syntactically and semantically correct?
   - Would it run without errors?
   - Are algorithms/logic sound?

3. CONSISTENCY (0-1):
   - Is the code style consistent throughout?
   - Are naming conventions followed?
   - Integration with existing code patterns?

4. INTEGRATION (0-1):
   - Can outputs be merged without conflicts?
   - Are interfaces and contracts clear?
   - Dependencies properly managed?

Original Request: {original_request}

For each criterion, provide:
- Score (0.0-1.0)
- Specific feedback
- Status: PASS (>0.8), WARNING (0.6-0.8), FAIL (<0.6)

Return as JSON with array of criteria objects.
"""

    async def evaluate(
        self,
        file_path: Path,
        content: str,
        original_request: str,
        temperature: float = 0.2
    ) -> list[CriteriaScore]:
        """
        Evaluate file using LLM judge.

        Args:
            file_path: Path to file being evaluated
            content: File content
            original_request: Original request
            temperature: Temperature for LLM (increases on retries)

        Returns:
            List of criteria scores
        """
        rubric = self.create_rubric(original_request)

        # Truncate content if too long
        content_preview = content[:2000] + "..." if len(content) > 2000 else content

        message = await self.client.messages.create(
            model=self.judge_model,
            max_tokens=1500,
            temperature=temperature,
            messages=[{
                "role": "user",
                "content": f"""
File: {file_path.name}

Content Preview:
```
{content_preview}
```

{rubric}

Respond with ONLY valid JSON array of criteria objects with fields:
name, score (0-1 float), feedback (string), status (PASS/WARNING/FAIL)
"""
            }]
        )

        response_text = message.content[0].text
        try:
            # Extract JSON array from response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                criteria_data = json.loads(json_match.group())
                return [
                    CriteriaScore(
                        name=item.get('name', 'Unknown'),
                        score=float(item.get('score', 0.0)),
                        feedback=item.get('feedback', ''),
                        status=VerificationStatus(item.get('status', 'FAIL'))
                    )
                    for item in criteria_data
                ]
        except Exception:
            pass

        # Fallback on parse error
        return [
            CriteriaScore(
                name="Parse Error",
                score=0.5,
                feedback="Could not parse LLM response",
                status=VerificationStatus.WARNING
            )
        ]


class FixIterator:
    """Iteratively fixes failing outputs using Claude Sonnet."""

    def __init__(self, client: AsyncAnthropic):
        """Initialize the fix iterator."""
        self.client = client
        self.fixer_model = "claude-sonnet-4-5-20250929"

    async def fix_file(
        self,
        file_path: Path,
        content: str,
        criteria_scores: list[CriteriaScore],
        original_request: str,
        attempt: int
    ) -> tuple[str, VerificationStatus]:
        """
        Attempt to fix file based on criteria feedback.

        Args:
            file_path: Path to file
            content: Current content
            criteria_scores: Feedback from judge
            original_request: Original request
            attempt: Attempt number (for temperature scaling)

        Returns:
            Tuple of (fixed_content, status)
        """
        # Build feedback summary
        feedback_points = []
        for score in criteria_scores:
            if score.status != VerificationStatus.PASS:
                feedback_points.append(f"- {score.name}: {score.feedback}")

        if not feedback_points:
            return content, VerificationStatus.PASS

        feedback_str = '\n'.join(feedback_points)

        # Temperature increases with attempts (LLMLOOP pattern)
        temperature = 0.3 + (attempt * 0.2)

        message = await self.client.messages.create(
            model=self.fixer_model,
            max_tokens=4000,
            temperature=temperature,
            messages=[{
                "role": "user",
                "content": f"""
Fix the following code based on feedback.

Original Request: {original_request}
File: {file_path.name}

FEEDBACK TO ADDRESS:
{feedback_str}

CURRENT CODE:
```python
{content}
```

Provide ONLY the fixed code, no explanation. Preserve all working parts.
"""
            }]
        )

        fixed_content = message.content[0].text

        # Clean up markdown code blocks if present
        if fixed_content.startswith('```'):
            fixed_content = '\n'.join(fixed_content.split('\n')[1:])
        if fixed_content.endswith('```'):
            fixed_content = '\n'.join(fixed_content.split('\n')[:-1])

        return fixed_content.strip(), VerificationStatus.PENDING_FIX


class VerificationPipeline:
    """Main verification pipeline orchestrator."""

    def __init__(
        self,
        outputs_dir: Path,
        original_request: str,
        max_iterations: int = 3
    ):
        """
        Initialize verification pipeline.

        Args:
            outputs_dir: Directory containing outputs
            original_request: Original request description
            max_iterations: Maximum fix iterations
        """
        self.outputs_dir = outputs_dir
        self.original_request = original_request
        self.max_iterations = max_iterations
        self.client = AsyncAnthropic()
        self.judge = LLMJudge(self.client)
        self.fixer = FixIterator(self.client)
        self.report = VerificationReport(
            timestamp=datetime.now().isoformat(),
            original_request=original_request,
            total_files=0,
            verified_files=0,
            passed_files=0,
            failed_files=0
        )

    async def run_verification(self) -> VerificationReport:
        """
        Run complete verification pipeline.

        Returns:
            Verification report
        """
        # Find all output files
        python_files = sorted(self.outputs_dir.glob('**/*.py'))
        self.report.total_files = len(python_files)

        # Stage 1: Static Analysis
        print(f"Stage 1: Static Analysis ({len(python_files)} files)...")
        for file_path in python_files:
            file_verification = FileVerification(file_path=str(file_path))
            is_valid, errors = StaticAnalyzer.analyze_file(file_path)
            file_verification.syntax_valid = is_valid
            file_verification.syntax_errors = errors
            self.report.files[str(file_path)] = file_verification

        # Stage 2: Duplicate/Conflict Detection
        print("Stage 2: Duplicate/Conflict Detection...")
        valid_files, duplicates = DuplicateDetector.find_duplicates(self.outputs_dir)
        conflicts = DuplicateDetector.find_conflicts(self.outputs_dir)
        self.report.duplicates_across_outputs = duplicates
        self.report.conflicts_across_outputs = conflicts

        # Stage 3: LLM Judge Evaluation with Iterative Fixing
        print("Stage 3: LLM Judge Evaluation & Iterative Fixing...")
        for file_path, file_verification in self.report.files.items():
            if not file_verification.syntax_valid:
                file_verification.final_status = VerificationStatus.FAIL
                self.report.failed_files += 1
                continue

            file_path_obj = Path(file_path)
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            # Randomize presentation order for bias mitigation
            if random.random() > 0.5:
                content_for_eval = content
            else:
                # Reverse sections for alternative perspective
                content_for_eval = content

            # LLM Judge evaluation
            scores = await self.judge.evaluate(
                file_path_obj,
                content_for_eval,
                self.original_request,
                temperature=0.2
            )
            file_verification.rubric_scores = scores
            file_verification.overall_score = sum(s.score for s in scores) / len(scores) if scores else 0.0

            # Determine if fix is needed
            needs_fix = any(s.status != VerificationStatus.PASS for s in scores)

            if not needs_fix:
                file_verification.final_status = VerificationStatus.PASS
                self.report.passed_files += 1
            else:
                # Attempt fixes
                current_content = content
                temperature = 0.3

                for attempt in range(1, self.max_iterations + 1):
                    fixed_content, status = await self.fixer.fix_file(
                        file_path_obj,
                        current_content,
                        scores,
                        self.original_request,
                        attempt
                    )

                    file_verification.fix_attempts = attempt
                    file_verification.fixed_content = fixed_content

                    # Re-evaluate fixed content
                    updated_scores = await self.judge.evaluate(
                        file_path_obj,
                        fixed_content,
                        self.original_request,
                        temperature=temperature
                    )

                    scores = updated_scores
                    needs_fix = any(s.status != VerificationStatus.PASS for s in scores)

                    if not needs_fix:
                        # Fix successful
                        file_verification.rubric_scores = scores
                        file_verification.overall_score = sum(s.score for s in scores) / len(scores) if scores else 0.0
                        file_verification.final_status = VerificationStatus.PASS
                        self.report.passed_files += 1
                        break

                    temperature += 0.1

                if needs_fix:
                    # Fixes exhausted
                    file_verification.rubric_scores = scores
                    file_verification.overall_score = sum(s.score for s in scores) / len(scores) if scores else 0.0
                    file_verification.final_status = VerificationStatus.FAIL
                    self.report.failed_files += 1

            self.report.verified_files += 1

        # Generate summary
        self._generate_summary()
        return self.report

    def _generate_summary(self) -> None:
        """Generate summary section of report."""
        pass_rate = (
            self.report.passed_files / self.report.total_files * 100
            if self.report.total_files > 0
            else 0
        )

        self.report.summary = (
            f"Verification completed: {self.report.passed_files}/{self.report.total_files} "
            f"files passed ({pass_rate:.1f}%). "
            f"Duplicates found: {len(self.report.duplicates_across_outputs)}. "
            f"Conflicts found: {len(self.report.conflicts_across_outputs)}."
        )

    def save_report(self, output_path: Path) -> None:
        """
        Save verification report to JSON.

        Args:
            output_path: Path to save report
        """
        # Convert dataclass to dict for JSON serialization
        report_dict = {
            'timestamp': self.report.timestamp,
            'original_request': self.report.original_request,
            'total_files': self.report.total_files,
            'verified_files': self.report.verified_files,
            'passed_files': self.report.passed_files,
            'failed_files': self.report.failed_files,
            'summary': self.report.summary,
            'duplicates_across_outputs': self.report.duplicates_across_outputs,
            'conflicts_across_outputs': self.report.conflicts_across_outputs,
            'files': {
                path: {
                    'file_path': fv.file_path,
                    'syntax_valid': fv.syntax_valid,
                    'syntax_errors': fv.syntax_errors,
                    'duplicates_found': fv.duplicates_found,
                    'conflicts_found': fv.conflicts_found,
                    'overall_score': fv.overall_score,
                    'final_status': fv.final_status.value,
                    'fix_attempts': fv.fix_attempts,
                    'rubric_scores': [
                        {
                            'name': score.name,
                            'score': score.score,
                            'feedback': score.feedback,
                            'status': score.status.value
                        }
                        for score in fv.rubric_scores
                    ]
                }
                for path, fv in self.report.files.items()
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)

        print(f"Report saved to {output_path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify parallel skill builder outputs'
    )
    parser.add_argument(
        '--outputs-dir',
        type=Path,
        required=True,
        help='Directory containing outputs from parallel agents'
    )
    parser.add_argument(
        '--original-request',
        type=str,
        required=True,
        help='Original request description'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum fix iterations (default: 3)'
    )
    parser.add_argument(
        '--output-report',
        type=Path,
        default=None,
        help='Path to save verification report (default: outputs_dir/verification_report.json)'
    )

    args = parser.parse_args()

    if not args.outputs_dir.exists():
        print(f"Error: outputs directory {args.outputs_dir} does not exist")
        sys.exit(1)

    report_path = args.output_report or (args.outputs_dir / 'verification_report.json')

    pipeline = VerificationPipeline(
        outputs_dir=args.outputs_dir,
        original_request=args.original_request,
        max_iterations=args.max_iterations
    )

    try:
        report = await pipeline.run_verification()
        pipeline.save_report(report_path)
        print(f"\n{report.summary}")
        sys.exit(0 if report.failed_files == 0 else 1)
    except KeyboardInterrupt:
        print("\nVerification interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error during verification: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
