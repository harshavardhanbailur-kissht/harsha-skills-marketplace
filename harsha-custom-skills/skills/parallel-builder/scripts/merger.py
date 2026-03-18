#!/usr/bin/env python3
"""
Intelligent merger for parallel skill builder outputs.

This script takes verified outputs from multiple parallel agents and merges them
into a cohesive final output with semantic conflict resolution.

Features:
- Intelligently combines code files respecting import order and deduplication
- Assembles documents with logical section ordering
- Handles mixed content types with organized manifest
- Uses Sonnet 4.6 for semantic conflict resolution
- Comprehensive merge reporting with conflict logs
"""

import asyncio
import json
import argparse
import sys
import ast
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
from datetime import datetime
from enum import Enum

from anthropic import AsyncAnthropic


class MergeStrategy(Enum):
    """Strategy for merging different content types."""
    CODE_COMBINE = "code_combine"
    DOCUMENT_ASSEMBLE = "document_assemble"
    MANIFEST = "manifest"


@dataclass
class MergeConflict:
    """Represents a merge conflict."""
    file_paths: list[str]
    conflict_type: str  # 'duplicate', 'conflicting_definition', 'incompatible_interface'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    description: str
    resolution: Optional[str] = None


@dataclass
class MergedFile:
    """Metadata for a merged file."""
    output_path: str
    source_files: list[str]
    merge_strategy: str
    line_count: int
    conflicts_resolved: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass
class MergeReport:
    """Complete merge report."""
    timestamp: str
    total_input_files: int
    total_output_files: int
    files_merged: list[MergedFile] = field(default_factory=list)
    conflicts: list[MergeConflict] = field(default_factory=list)
    unresolved_conflicts: list[MergeConflict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: str = ""


class CodeMerger:
    """Merges Python code files intelligently."""

    @staticmethod
    def extract_imports(content: str) -> tuple[list[str], str]:
        """
        Extract imports from Python code.

        Args:
            content: Python code content

        Returns:
            Tuple of (imports_list, code_without_imports)
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return [], content

        imports = []
        other_lines = []
        import_end = 0

        for i, line in enumerate(content.split('\n')):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(line)
                import_end = i + 1
            elif stripped and not stripped.startswith('#'):
                break

        if imports:
            remaining_content = '\n'.join(content.split('\n')[import_end:])
            return imports, remaining_content

        return [], content

    @staticmethod
    def extract_definitions(content: str) -> dict[str, tuple[int, str]]:
        """
        Extract function and class definitions from code.

        Args:
            content: Python code content

        Returns:
            Dict of {name: (line_number, definition_block)}
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {}

        definitions = {}
        lines = content.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                start_line = node.lineno - 1
                end_line = node.end_lineno or start_line + 1

                definition_block = '\n'.join(lines[start_line:end_line])
                definitions[node.name] = (start_line, definition_block)

        return definitions

    @staticmethod
    def merge_python_files(file_contents: dict[str, str]) -> str:
        """
        Merge multiple Python files intelligently.

        Args:
            file_contents: Dict of {file_path: content}

        Returns:
            Merged content
        """
        all_imports = set()
        code_sections = []
        seen_definitions = {}

        # Extract and deduplicate imports
        for file_path, content in file_contents.items():
            imports, code = CodeMerger.extract_imports(content)
            all_imports.update(imports)

            # Extract definitions to avoid duplicates
            definitions = CodeMerger.extract_definitions(code)
            for name, (line_num, definition) in definitions.items():
                if name not in seen_definitions:
                    seen_definitions[name] = (file_path, definition)
                    code_sections.append(definition)

        # Sort imports for consistency
        sorted_imports = sorted(all_imports)

        # Add any remaining code that isn't a definition
        for file_path, content in file_contents.items():
            imports, code = CodeMerger.extract_imports(content)
            definitions = CodeMerger.extract_definitions(code)

            # Extract code that's not a definition
            lines = code.split('\n')
            for i, line in enumerate(lines):
                in_definition = False
                for def_name, (def_line, _) in definitions.items():
                    if i >= def_line:
                        in_definition = True
                        break

                if not in_definition and line.strip() and not line.strip().startswith('#'):
                    code_sections.append(line)

        merged = '\n'.join(sorted_imports)
        if sorted_imports:
            merged += '\n\n'
        merged += '\n'.join(code_sections)

        return merged.strip()


class DocumentMerger:
    """Merges document files intelligently."""

    @staticmethod
    def extract_sections(content: str) -> list[tuple[int, str, str]]:
        """
        Extract sections from markdown/text document.

        Args:
            content: Document content

        Returns:
            List of (level, heading, content)
        """
        sections = []
        lines = content.split('\n')
        current_section = []
        current_heading = ''
        current_level = 0

        for line in lines:
            if line.startswith('#'):
                if current_section:
                    sections.append((current_level, current_heading, '\n'.join(current_section)))
                    current_section = []

                level = len(line) - len(line.lstrip('#'))
                current_heading = line.lstrip('#').strip()
                current_level = level
            else:
                current_section.append(line)

        if current_section:
            sections.append((current_level, current_heading, '\n'.join(current_section)))

        return sections

    @staticmethod
    def merge_documents(file_contents: dict[str, str]) -> str:
        """
        Merge multiple document files.

        Args:
            file_contents: Dict of {file_path: content}

        Returns:
            Merged document
        """
        all_sections = []

        for file_path, content in file_contents.items():
            sections = DocumentMerger.extract_sections(content)
            all_sections.extend(sections)

        # Sort by heading level and remove duplicates
        sorted_sections = sorted(all_sections, key=lambda x: (x[0], x[1]))

        merged = []
        seen_headings = set()

        for level, heading, content in sorted_sections:
            if heading not in seen_headings:
                merged.append('#' * level + ' ' + heading)
                merged.append(content)
                merged.append('')
                seen_headings.add(heading)

        return '\n'.join(merged).strip()


class ConflictResolver:
    """Resolves semantic conflicts using Sonnet."""

    def __init__(self, client: AsyncAnthropic):
        """Initialize conflict resolver."""
        self.client = client
        self.resolver_model = "claude-sonnet-4-5-20250929"

    async def resolve_conflict(
        self,
        conflict: MergeConflict,
        file_contents: dict[str, str]
    ) -> tuple[str, Optional[str]]:
        """
        Attempt to resolve semantic conflict using LLM.

        Args:
            conflict: Conflict to resolve
            file_contents: Contents of conflicting files

        Returns:
            Tuple of (resolved_content, resolution_note)
        """
        conflict_files_content = '\n\n'.join(
            f"FILE: {fpath}\n```\n{file_contents[fpath]}\n```"
            for fpath in conflict.file_paths
            if fpath in file_contents
        )

        message = await self.client.messages.create(
            model=self.resolver_model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""
Resolve the following merge conflict intelligently.

Conflict Type: {conflict.conflict_type}
Severity: {conflict.severity}
Description: {conflict.description}

Conflicting Files:
{conflict_files_content}

Provide the merged/resolved content that combines both approaches.
Return ONLY the resolved code, no explanation.
"""
            }]
        )

        resolved_content = message.content[0].text
        resolution_note = f"Resolved by LLM: {conflict.conflict_type}"

        return resolved_content, resolution_note

    async def detect_and_resolve_conflicts(
        self,
        merged_content: str,
        file_contents: dict[str, str]
    ) -> tuple[str, list[MergeConflict], list[str]]:
        """
        Detect and attempt to resolve conflicts in merged content.

        Args:
            merged_content: Merged content to check
            file_contents: Source file contents

        Returns:
            Tuple of (resolved_content, conflicts, resolution_notes)
        """
        conflicts = []
        resolved_conflicts = []
        notes = []

        # Check for duplicate definitions
        try:
            tree = ast.parse(merged_content)
            definitions = {}

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    name = node.name
                    if name in definitions:
                        conflict = MergeConflict(
                            file_paths=list(file_contents.keys()),
                            conflict_type='duplicate_definition',
                            severity='MEDIUM',
                            description=f"Duplicate definition: {name}"
                        )
                        conflicts.append(conflict)
                    else:
                        definitions[name] = node
        except SyntaxError:
            pass

        # Attempt to resolve conflicts
        for conflict in conflicts:
            if conflict.severity == 'MEDIUM':
                resolved, note = await self.resolve_conflict(conflict, file_contents)
                resolved_conflicts.append(resolved)
                notes.append(note)

        # Update merged content if conflicts were resolved
        if resolved_conflicts and len(resolved_conflicts) == len(conflicts):
            merged_content = '\n\n'.join(resolved_conflicts)

        return merged_content, conflicts, notes


class Merger:
    """Main merger orchestrator."""

    def __init__(
        self,
        outputs_dir: Path,
        plan: Optional[dict[str, Any]] = None
    ):
        """
        Initialize merger.

        Args:
            outputs_dir: Directory containing outputs
            plan: Optional execution plan with interface contracts
        """
        self.outputs_dir = outputs_dir
        self.plan = plan or {}
        self.client = AsyncAnthropic()
        self.conflict_resolver = ConflictResolver(self.client)
        self.report = MergeReport(
            timestamp=datetime.now().isoformat(),
            total_input_files=0,
            total_output_files=0
        )

    def _group_files_by_type(self) -> dict[str, list[Path]]:
        """
        Group output files by type.

        Returns:
            Dict of {file_type: list_of_paths}
        """
        grouped = {}

        for file_path in self.outputs_dir.glob('**/*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix not in grouped:
                    grouped[suffix] = []
                grouped[suffix].append(file_path)

        return grouped

    def _determine_merge_strategy(
        self,
        files: list[Path]
    ) -> MergeStrategy:
        """
        Determine merge strategy based on file types.

        Args:
            files: Files to merge

        Returns:
            Merge strategy
        """
        if all(f.suffix == '.py' for f in files):
            return MergeStrategy.CODE_COMBINE

        if any(f.suffix in ['.md', '.txt'] for f in files):
            return MergeStrategy.DOCUMENT_ASSEMBLE

        return MergeStrategy.MANIFEST

    async def merge_outputs(self) -> MergeReport:
        """
        Run complete merge process.

        Returns:
            Merge report
        """
        grouped_files = self._group_files_by_type()
        self.report.total_input_files = sum(len(files) for files in grouped_files.values())

        # Process each file type group
        for file_type, files in grouped_files.items():
            if not files:
                continue

            strategy = self._determine_merge_strategy(files)
            print(f"Merging {len(files)} {file_type} files using {strategy.value}...")

            file_contents = {}
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents[str(file_path)] = f.read()
                except UnicodeDecodeError:
                    # Skip binary files
                    continue

            if not file_contents:
                continue

            # Merge based on strategy
            if strategy == MergeStrategy.CODE_COMBINE:
                merged_content = CodeMerger.merge_python_files(file_contents)

                # Resolve conflicts
                merged_content, conflicts, resolution_notes = (
                    await self.conflict_resolver.detect_and_resolve_conflicts(
                        merged_content,
                        file_contents
                    )
                )

                self.report.conflicts.extend(conflicts)

                # Save merged file
                output_path = self.outputs_dir / f'merged{file_type}'
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(merged_content)

                merged_file = MergedFile(
                    output_path=str(output_path),
                    source_files=[str(p) for p in files],
                    merge_strategy=strategy.value,
                    line_count=len(merged_content.split('\n')),
                    conflicts_resolved=len(conflicts)
                )
                self.report.files_merged.append(merged_file)
                self.report.total_output_files += 1

            elif strategy == MergeStrategy.DOCUMENT_ASSEMBLE:
                merged_content = DocumentMerger.merge_documents(file_contents)

                output_path = self.outputs_dir / f'merged{file_type}'
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(merged_content)

                merged_file = MergedFile(
                    output_path=str(output_path),
                    source_files=[str(p) for p in files],
                    merge_strategy=strategy.value,
                    line_count=len(merged_content.split('\n'))
                )
                self.report.files_merged.append(merged_file)
                self.report.total_output_files += 1

        # Create manifest
        self._create_manifest()

        # Generate summary
        self._generate_summary()

        return self.report

    def _create_manifest(self) -> None:
        """Create manifest of merged outputs."""
        manifest = {
            'timestamp': self.report.timestamp,
            'total_files': self.report.total_output_files,
            'files': []
        }

        for merged_file in self.report.files_merged:
            manifest['files'].append({
                'output_path': merged_file.output_path,
                'source_files': merged_file.source_files,
                'merge_strategy': merged_file.merge_strategy,
                'line_count': merged_file.line_count,
                'conflicts_resolved': merged_file.conflicts_resolved,
                'warnings': merged_file.warnings
            })

        manifest_path = self.outputs_dir / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        print(f"Manifest saved to {manifest_path}")

    def _generate_summary(self) -> None:
        """Generate summary section of report."""
        conflict_count = len(self.report.conflicts)
        unresolved_count = len(self.report.unresolved_conflicts)

        self.report.summary = (
            f"Merge completed: {self.report.total_output_files} output files from "
            f"{self.report.total_input_files} input files. "
            f"Conflicts: {conflict_count} ({unresolved_count} unresolved)."
        )

    def save_report(self, output_path: Path) -> None:
        """
        Save merge report to JSON.

        Args:
            output_path: Path to save report
        """
        report_dict = {
            'timestamp': self.report.timestamp,
            'total_input_files': self.report.total_input_files,
            'total_output_files': self.report.total_output_files,
            'summary': self.report.summary,
            'files_merged': [
                {
                    'output_path': mf.output_path,
                    'source_files': mf.source_files,
                    'merge_strategy': mf.merge_strategy,
                    'line_count': mf.line_count,
                    'conflicts_resolved': mf.conflicts_resolved,
                    'warnings': mf.warnings
                }
                for mf in self.report.files_merged
            ],
            'conflicts': [
                {
                    'file_paths': c.file_paths,
                    'conflict_type': c.conflict_type,
                    'severity': c.severity,
                    'description': c.description,
                    'resolution': c.resolution
                }
                for c in self.report.conflicts
            ],
            'unresolved_conflicts': [
                {
                    'file_paths': c.file_paths,
                    'conflict_type': c.conflict_type,
                    'severity': c.severity,
                    'description': c.description
                }
                for c in self.report.unresolved_conflicts
            ],
            'warnings': self.report.warnings
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)

        print(f"Report saved to {output_path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Merge parallel skill builder outputs'
    )
    parser.add_argument(
        '--outputs-dir',
        type=Path,
        required=True,
        help='Directory containing verified outputs'
    )
    parser.add_argument(
        '--plan',
        type=Path,
        default=None,
        help='Optional execution plan JSON for understanding interface contracts'
    )
    parser.add_argument(
        '--merged-dir',
        type=Path,
        default=None,
        help='Output directory for merged results (default: same as outputs-dir)'
    )
    parser.add_argument(
        '--output-report',
        type=Path,
        default=None,
        help='Path to save merge report (default: merged_dir/merge_report.json)'
    )

    args = parser.parse_args()

    if not args.outputs_dir.exists():
        print(f"Error: outputs directory {args.outputs_dir} does not exist")
        sys.exit(1)

    # Load execution plan if provided
    plan = None
    if args.plan and args.plan.exists():
        try:
            with open(args.plan, 'r', encoding='utf-8') as f:
                plan = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading plan: {e}")
            sys.exit(1)

    merged_dir = args.merged_dir or args.outputs_dir
    merged_dir.mkdir(parents=True, exist_ok=True)

    report_path = args.output_report or (merged_dir / 'merge_report.json')

    merger = Merger(
        outputs_dir=args.outputs_dir,
        plan=plan
    )

    try:
        report = await merger.merge_outputs()
        merger.save_report(report_path)
        print(f"\n{report.summary}")
        sys.exit(0 if len(report.unresolved_conflicts) == 0 else 1)
    except KeyboardInterrupt:
        print("\nMerge interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error during merge: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
