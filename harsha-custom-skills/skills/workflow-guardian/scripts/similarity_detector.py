#!/usr/bin/env python3
"""
Component Similarity Detector for React/TypeScript Codebases

This script analyzes existing React/TypeScript components and detects similarities
with a proposed new component based on:
- Hook usage patterns
- State variables and their types
- JSX structure patterns
- Import patterns (Jaccard similarity)
- Form field types and validation
- Event handler patterns
- Custom hook usage
- Structural similarity (JSX nesting patterns)
- Form-specific comparison (field lists, validation, submit handlers)

Usage:
    python similarity_detector.py <project_root> [component_description] [options]

Options:
    --target <description>        Compare specific description against all components
    --threshold <percent>         Set minimum similarity % (default: 40)
    --format <json|markdown>      Output format (default: json)

Example:
    python similarity_detector.py /path/to/project "A form component that validates and submits user data with file attachments"
    python similarity_detector.py /path/to/project --target "contact form" --threshold 50 --format markdown
"""

import os
import re
import json
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime


@dataclass
class ComponentAnalysis:
    """Analysis results for a single component"""
    file_path: str
    component_name: str
    hooks_used: Set[str]
    state_variables: Dict[str, str]  # name -> type
    jsx_patterns: Set[str]
    imports: Set[str]
    form_fields: List[Dict]
    event_handlers: Set[str]
    file_size: int
    lines_of_code: int
    has_async_operations: bool
    has_error_handling: bool
    has_validation: bool
    has_file_upload: bool
    has_modal_or_dialog: bool
    custom_hooks: Set[str]
    jsx_nesting_depth: int = 0
    validation_rules: List[str] = field(default_factory=list)
    submit_handler_patterns: Set[str] = field(default_factory=set)
    field_names: Set[str] = field(default_factory=set)


@dataclass
class SimilarityScore:
    """Similarity score details between two components"""
    target_file: str
    target_name: str
    similarity_percentage: float
    matching_hooks: Set[str]
    matching_state_patterns: List[str]
    matching_jsx_patterns: Set[str]
    matching_form_fields: List[str]
    shared_features: List[str]
    reuse_potential: float  # percentage of logic that could be reused
    recommendation: str
    import_similarity: float = 0.0
    structural_similarity: float = 0.0
    form_similarity: float = 0.0
    form_field_overlap: float = 0.0
    base_component: Optional[str] = None
    reusable_sections: List[str] = field(default_factory=list)
    modification_effort: str = "medium"  # low, medium, high
    duplicate_risk: str = "none"  # none, low, medium, high


class ComponentAnalyzer:
    """Analyzes React/TypeScript component files"""

    REACT_HOOKS = {
        'useState', 'useEffect', 'useContext', 'useRef', 'useCallback',
        'useMemo', 'useReducer', 'useLayoutEffect', 'useImperativeHandle',
        'useDebugValue', 'useDeferredValue', 'useTransition', 'useId',
        'useSyncExternalStore'
    }

    COMMON_PATTERNS = {
        'form-handling': [
            r'useState.*form',
            r'handleSubmit',
            r'handleInputChange',
            r'onChange.*input',
            r'form.*onSubmit'
        ],
        'file-handling': [
            r'fileInput',
            r'File\[\]',
            r'\.files',
            r'FormData',
            r'upload',
            r'preview'
        ],
        'api-calls': [
            r'await.*fetch',
            r'axios\.',
            r'supabase\.',
            r'api\.',
            r'\.then\(',
            r'\.catch\('
        ],
        'validation': [
            r'validate',
            r'error.*message',
            r'setError',
            r'trim\(',
            r'\.length',
            r'regex|RegExp|pattern'
        ],
        'modal-dialog': [
            r'Modal',
            r'Dialog',
            r'isOpen',
            r'onClose',
            r'z-\d+',
            r'backdrop',
            r'overlay'
        ],
        'animation': [
            r'motion\.',
            r'AnimatePresence',
            r'framer-motion',
            r'transition',
            r'animate',
            r'@keyframes'
        ]
    }

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.components: Dict[str, ComponentAnalysis] = {}

    def analyze_project(self) -> Dict[str, ComponentAnalysis]:
        """Analyze all components in the project"""
        src_dir = self.project_root / 'src'

        if not src_dir.exists():
            print(f"Warning: src directory not found at {src_dir}")
            return {}

        component_files = list(src_dir.rglob('*.tsx')) + list(src_dir.rglob('*.ts'))
        component_files += list(src_dir.rglob('*.jsx')) + list(src_dir.rglob('*.js'))

        for file_path in component_files:
            # Skip node_modules, dist, build
            if any(part in file_path.parts for part in ['node_modules', 'dist', 'build', '.next']):
                continue

            try:
                analysis = self.analyze_file(file_path)
                if analysis:
                    self.components[str(file_path)] = analysis
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}", file=sys.stderr)

        return self.components

    def analyze_file(self, file_path: Path) -> ComponentAnalysis | None:
        """Analyze a single component file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        # Skip if not a React component (no JSX/export)
        if 'export' not in content or ('<' not in content and '>' not in content):
            return None

        lines = content.split('\n')
        component_name = self._extract_component_name(content, file_path)

        form_fields = self._extract_form_fields(content)

        return ComponentAnalysis(
            file_path=str(file_path),
            component_name=component_name,
            hooks_used=self._extract_hooks(content),
            state_variables=self._extract_state_variables(content),
            jsx_patterns=self._extract_jsx_patterns(content),
            imports=self._extract_imports(content),
            form_fields=form_fields,
            event_handlers=self._extract_event_handlers(content),
            file_size=len(content),
            lines_of_code=len(lines),
            has_async_operations=self._has_async_operations(content),
            has_error_handling=self._has_error_handling(content),
            has_validation=self._has_validation(content),
            has_file_upload=self._has_file_upload(content),
            has_modal_or_dialog=self._has_modal_or_dialog(content),
            custom_hooks=self._extract_custom_hooks(content),
            jsx_nesting_depth=self._calculate_jsx_nesting_depth(content),
            validation_rules=self._extract_validation_rules(content),
            submit_handler_patterns=self._extract_submit_patterns(content),
            field_names={f['name'] for f in form_fields}
        )

    def _extract_component_name(self, content: str, file_path: Path) -> str:
        """Extract the exported component name"""
        # Try to find default export function
        match = re.search(r'export\s+default\s+function\s+(\w+)', content)
        if match:
            return match.group(1)

        # Try named export
        match = re.search(r'export\s+function\s+(\w+)', content)
        if match:
            return match.group(1)

        # Fallback to file name
        return file_path.stem

    def _extract_hooks(self, content: str) -> Set[str]:
        """Extract React hooks used"""
        hooks = set()
        for hook in self.REACT_HOOKS:
            if re.search(rf'\b{hook}\s*\(', content):
                hooks.add(hook)
        return hooks

    def _extract_custom_hooks(self, content: str) -> Set[str]:
        """Extract custom hook usage"""
        custom_hooks = set()
        # Match patterns like useCustomHook, useFoo, useBar
        matches = re.findall(r'\b(use[A-Z]\w+)\s*\(', content)
        for match in matches:
            if match not in self.REACT_HOOKS:
                custom_hooks.add(match)
        return custom_hooks

    def _extract_state_variables(self, content: str) -> Dict[str, str]:
        """Extract useState declarations and infer types"""
        state_vars = {}

        # Match useState patterns
        pattern = r'const\s+\[\s*(\w+)\s*,\s*\w+\s*\]\s*=\s*useState\s*(?:<([^>]+)>)?\s*\(\s*([^)]+)\)'
        matches = re.findall(pattern, content)

        for name, type_annotation, initial_value in matches:
            if type_annotation:
                state_vars[name] = type_annotation
            else:
                # Infer type from initial value
                inferred_type = self._infer_type_from_value(initial_value)
                state_vars[name] = inferred_type

        return state_vars

    def _infer_type_from_value(self, value: str) -> str:
        """Infer TypeScript type from initial value"""
        value = value.strip()
        if value == 'false' or value == 'true':
            return 'boolean'
        elif value == 'null':
            return 'any'
        elif value.startswith('{'):
            return 'object'
        elif value.startswith('['):
            return 'array'
        elif value.startswith('"') or value.startswith("'"):
            return 'string'
        elif value.isdigit():
            return 'number'
        elif value == 'new Map()':
            return 'Map'
        else:
            return 'unknown'

    def _extract_jsx_patterns(self, content: str) -> Set[str]:
        """Extract JSX structure patterns"""
        patterns = set()

        # Form elements
        if re.search(r'<form', content):
            patterns.add('form')
        if re.search(r'<input', content):
            patterns.add('input')
        if re.search(r'<textarea', content):
            patterns.add('textarea')
        if re.search(r'<select', content):
            patterns.add('select')
        if re.search(r'<button', content):
            patterns.add('button')
        if re.search(r'<label', content):
            patterns.add('label')

        # Layout
        if re.search(r'<div.*className.*flex', content):
            patterns.add('flex-layout')
        if re.search(r'<div.*className.*grid', content):
            patterns.add('grid-layout')
        if re.search(r'<div.*className.*space-', content):
            patterns.add('spaced-layout')

        # Components
        if re.search(r'<Button', content):
            patterns.add('Button')
        if re.search(r'<Modal|<Dialog', content):
            patterns.add('Modal')
        if re.search(r'<motion\.', content):
            patterns.add('animation')
        if re.search(r'<Toast', content):
            patterns.add('Toast')
        if re.search(r'<Card', content):
            patterns.add('Card')

        return patterns

    def _extract_imports(self, content: str) -> Set[str]:
        """Extract import statements"""
        imports = set()

        # Match import statements
        pattern = r'from\s+["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)

        for match in matches:
            # Extract library name (first part before /)
            lib = match.split('/')[0].replace('@', '')
            imports.add(lib)

        return imports

    def _extract_form_fields(self, content: str) -> List[Dict]:
        """Extract form field information"""
        fields = []

        # Find all input/textarea/select patterns
        input_pattern = r'<(input|textarea|select)\s+[^>]*(?:name=["\'"](\w+)["\'])[^>]*type=["\'"](\w+)["\']'
        select_pattern = r'<Select[^>]*(?:name=["\'"](\w+)["\'])[^>]*'

        for match in re.finditer(input_pattern, content):
            element, name, field_type = match.groups()
            fields.append({
                'name': name or 'unnamed',
                'type': field_type,
                'element': element
            })

        for match in re.finditer(select_pattern, content):
            name = match.group(1)
            fields.append({
                'name': name or 'unnamed',
                'type': 'select',
                'element': 'select'
            })

        return fields

    def _extract_event_handlers(self, content: str) -> Set[str]:
        """Extract event handler patterns"""
        handlers = set()

        # Find all event handler methods
        pattern = r'(handle\w+|on\w+)\s*='
        matches = re.findall(pattern, content)

        for match in set(matches):
            handlers.add(match)

        return handlers

    def _has_async_operations(self, content: str) -> bool:
        """Check if component has async operations"""
        return bool(re.search(r'\basync\s+\w+|\.then\(|\.catch\(|await\s+\w+', content))

    def _has_error_handling(self, content: str) -> bool:
        """Check if component has error handling"""
        return bool(re.search(r'error|Error|\[error\]|setError', content))

    def _has_validation(self, content: str) -> bool:
        """Check if component has validation"""
        return bool(re.search(r'validate|invalid|required|pattern|regex', content, re.IGNORECASE))

    def _has_file_upload(self, content: str) -> bool:
        """Check if component has file upload"""
        return bool(re.search(r'type=["\']file["\']|File\[|\.files|fileInput|upload', content))

    def _has_modal_or_dialog(self, content: str) -> bool:
        """Check if component is a modal or dialog"""
        return bool(re.search(r'<Modal|<Dialog|modal|dialog|isOpen|onClose|backdrop|overlay', content, re.IGNORECASE))

    def _calculate_jsx_nesting_depth(self, content: str) -> int:
        """Calculate maximum JSX nesting depth"""
        max_depth = 0
        current_depth = 0

        for char in content:
            if char == '<':
                # Check if it's a JSX opening tag (not a comparison)
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '>':
                # Check if closing tag
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _extract_validation_rules(self, content: str) -> List[str]:
        """Extract validation rule patterns"""
        rules = []

        # Pattern matching for common validation
        patterns = {
            'required': r'required|\.required\(\)',
            'email': r'email|@|\.email\(\)',
            'min_length': r'minLength|\.min\(|min:|length\s*[<>]',
            'max_length': r'maxLength|\.max\(|max:|length\s*[>]',
            'pattern': r'pattern|regex|RegExp|\.matches\(|test\(',
            'numeric': r'number|numeric|isNaN|parseInt|parseFloat',
            'alpha': r'alpha|letters|isAlpha',
            'custom': r'custom.*validation|validator\.|validate\w+\('
        }

        for rule_name, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                rules.append(rule_name)

        return rules

    def _extract_submit_patterns(self, content: str) -> Set[str]:
        """Extract submit/form submission handler patterns"""
        patterns = set()

        # Submission patterns
        if re.search(r'handleSubmit|onSubmit', content):
            patterns.add('handleSubmit')
        if re.search(r'async.*submit|await.*submit', content, re.IGNORECASE):
            patterns.add('async_submit')
        if re.search(r'preventDefault|stopPropagation', content):
            patterns.add('preventDefault')
        if re.search(r'FormData|new FormData', content):
            patterns.add('form_data_api')
        if re.search(r'axios\.|fetch\(|fetch\s', content):
            patterns.add('api_call')
        if re.search(r'then\(.*finally\(|catch\(', content):
            patterns.add('promise_chain')
        if re.search(r'try\s*{.*catch\s*{', content):
            patterns.add('try_catch')
        if re.search(r'toast|notification|alert', content, re.IGNORECASE):
            patterns.add('user_feedback')
        if re.search(r'redirect|navigate|push.*route', content, re.IGNORECASE):
            patterns.add('navigation')
        if re.search(r'setSuccess|successMessage|success.*state', content):
            patterns.add('success_state')

        return patterns


class SimilarityDetector:
    """Detects similarity between components"""

    def __init__(self, analyzer: ComponentAnalyzer, threshold: int = 40):
        self.analyzer = analyzer
        self.threshold = threshold

    def detect_similarities(self, proposed_description: str, limit: int = 10) -> List[SimilarityScore]:
        """
        Detect similar components based on description of proposed component

        Args:
            proposed_description: Description of the new component to be created
            limit: Maximum number of results to return

        Returns:
            List of SimilarityScore objects, sorted by similarity
        """
        # Analyze the proposed component description
        proposed_features = self._analyze_description(proposed_description)

        # Compare with existing components
        scores = []
        for file_path, analysis in self.analyzer.components.items():
            score = self._calculate_similarity(analysis, proposed_features)
            if score.similarity_percentage >= self.threshold:  # Use configurable threshold
                scores.append(score)

        # Sort by similarity percentage (descending)
        scores.sort(key=lambda x: x.similarity_percentage, reverse=True)

        return scores[:limit]

    def _analyze_description(self, description: str) -> Dict[str, set]:
        """Extract features from description"""
        description_lower = description.lower()

        features = {
            'hooks': set(),
            'patterns': set(),
            'keywords': set(),
            'imports': set(),
            'validation_rules': set(),
            'submit_patterns': set(),
            'field_names': set(),
            'form_related': False,
            'file_upload': False,
            'validation': False,
            'async': False,
            'modal': False,
            'animation': False,
            'error_handling': False,
        }

        # Keyword analysis
        keywords = {
            'form': ['form', 'input', 'field', 'submit', 'validation'],
            'file': ['file', 'upload', 'attachment', 'image', 'video', 'document'],
            'api': ['api', 'fetch', 'request', 'async', 'async operation', 'call'],
            'validation': ['validate', 'validation', 'check', 'verify'],
            'modal': ['modal', 'dialog', 'popup', 'overlay'],
            'animation': ['animation', 'animate', 'transition', 'motion'],
            'error': ['error', 'error handling', 'exception'],
            'state': ['state', 'useState', 'useReducer'],
            'hooks': ['hook', 'effect', 'context', 'ref'],
        }

        for category, keywords_list in keywords.items():
            if any(kw in description_lower for kw in keywords_list):
                if category == 'form':
                    features['form_related'] = True
                elif category == 'file':
                    features['file_upload'] = True
                elif category == 'validation':
                    features['validation'] = True
                    features['validation_rules'].add('required')
                elif category == 'api':
                    features['async'] = True
                    features['submit_patterns'].add('api_call')
                elif category == 'modal':
                    features['modal'] = True
                elif category == 'animation':
                    features['animation'] = True
                elif category == 'error':
                    features['error_handling'] = True
                else:
                    features['keywords'].add(category)

        # Extract potential library names from description
        lib_patterns = {
            'react': r'react',
            'typescript': r'typescript|type',
            'tailwind': r'tailwind|classname',
            'framer': r'framer|motion',
            'toast': r'toast|notification',
        }

        for lib, pattern in lib_patterns.items():
            if re.search(pattern, description_lower):
                features['imports'].add(lib)

        # Extract field names if mentioned
        if features['form_related']:
            # Look for "field", "field1 field2", or similar patterns
            field_matches = re.findall(r'(?:field[s]?|input[s]?|box[es]?|area[s]?)\s+(?:named?|called?|with?|like?|for?|such\s+as)?\s*["\']?(\w+)["\']?', description)
            for match in field_matches[:5]:
                features['field_names'].add(match.lower())

        return features

    def _calculate_similarity(self, analysis: ComponentAnalysis, proposed: Dict[str, set]) -> SimilarityScore:
        """Calculate similarity score between component and proposed description"""

        score = 0.0
        max_score = 0.0

        # Feature matching (30% weight) - forms weighted higher
        feature_weights = {
            'form_related': (analysis.form_fields, 15),  # Increased from 10
            'file_upload': (analysis.has_file_upload, 10),
            'validation': (analysis.has_validation, 8),
            'async': (analysis.has_async_operations, 8),
            'modal': (analysis.has_modal_or_dialog, 6),
            'animation': ('animation' in analysis.jsx_patterns, 5),
            'error_handling': (analysis.has_error_handling, 6),
        }

        for feature, (has_feature, weight) in feature_weights.items():
            max_score += weight
            if proposed[feature]:
                if isinstance(has_feature, list):
                    if has_feature:  # Non-empty list
                        score += weight
                elif isinstance(has_feature, bool):
                    if has_feature:
                        score += weight

        # Hook matching (25% weight)
        max_score += 25
        common_hooks = analysis.hooks_used & proposed['hooks']
        hook_similarity = len(common_hooks) / max(len(analysis.hooks_used), 1) if analysis.hooks_used else 0
        score += hook_similarity * 25

        # Pattern matching (20% weight)
        max_score += 20
        common_patterns = analysis.jsx_patterns & proposed['patterns']
        pattern_similarity = len(common_patterns) / max(len(analysis.jsx_patterns), 1) if analysis.jsx_patterns else 0
        score += pattern_similarity * 20

        # Import similarity using Jaccard index (10% weight)
        max_score += 10
        import_similarity = self._calculate_jaccard_similarity(analysis.imports, proposed['imports'])
        score += import_similarity * 10

        # Structural similarity (JSX nesting) (10% weight)
        max_score += 10
        structural_similarity = self._calculate_structural_similarity(analysis)
        score += (structural_similarity / 100) * 10

        # Form-specific scoring if form-related
        form_similarity = 0.0
        form_field_overlap = 0.0
        if proposed['form_related'] and analysis.form_fields:
            form_similarity, form_field_overlap = self._calculate_form_similarity(analysis, proposed)
            # Adjust overall score for strong form matches
            if form_field_overlap > 50:
                score += (form_field_overlap / 100) * 5

        # Normalize to percentage
        similarity_percentage = (score / max_score * 100) if max_score > 0 else 0

        # Determine reuse potential
        reuse_potential = self._estimate_reuse_potential(analysis, proposed)

        # Generate recommendation
        recommendation = self._generate_recommendation(similarity_percentage, reuse_potential, analysis)

        # Determine base component and sections
        base_component = analysis.component_name if similarity_percentage >= 60 else None
        reusable_sections = self._identify_reusable_sections(analysis, proposed, similarity_percentage)
        modification_effort = self._estimate_effort(similarity_percentage, len(analysis.form_fields))
        duplicate_risk = self._assess_duplication_risk(form_field_overlap, similarity_percentage)

        return SimilarityScore(
            target_file=analysis.file_path,
            target_name=analysis.component_name,
            similarity_percentage=round(similarity_percentage, 1),
            matching_hooks=analysis.hooks_used,
            matching_state_patterns=list(analysis.state_variables.keys())[:5],
            matching_jsx_patterns=analysis.jsx_patterns,
            matching_form_fields=[f['name'] for f in analysis.form_fields[:5]],
            shared_features=self._extract_shared_features(analysis, proposed),
            reuse_potential=round(reuse_potential, 1),
            recommendation=recommendation,
            import_similarity=round(import_similarity * 100, 1),
            structural_similarity=round(structural_similarity, 1),
            form_similarity=round(form_similarity, 1),
            form_field_overlap=round(form_field_overlap, 1),
            base_component=base_component,
            reusable_sections=reusable_sections,
            modification_effort=modification_effort,
            duplicate_risk=duplicate_risk
        )

    def _estimate_reuse_potential(self, analysis: ComponentAnalysis, proposed: Dict[str, set]) -> float:
        """Estimate percentage of code that could be reused"""

        # More matching features = higher reuse potential
        matching_features = 0
        total_features = 7

        if proposed['form_related'] and analysis.form_fields:
            matching_features += 1
        if proposed['file_upload'] and analysis.has_file_upload:
            matching_features += 1
        if proposed['validation'] and analysis.has_validation:
            matching_features += 1
        if proposed['async'] and analysis.has_async_operations:
            matching_features += 1
        if proposed['modal'] and analysis.has_modal_or_dialog:
            matching_features += 1
        if proposed['animation'] and 'animation' in analysis.jsx_patterns:
            matching_features += 1
        if proposed['error_handling'] and analysis.has_error_handling:
            matching_features += 1

        return (matching_features / total_features) * 100

    def _extract_shared_features(self, analysis: ComponentAnalysis, proposed: Dict[str, set]) -> List[str]:
        """Extract shared features between component and proposed"""
        features = []

        if proposed['form_related'] and analysis.form_fields:
            features.append(f"Form handling ({len(analysis.form_fields)} fields)")
        if proposed['file_upload'] and analysis.has_file_upload:
            features.append("File upload capability")
        if proposed['validation'] and analysis.has_validation:
            features.append("Input validation")
        if proposed['async'] and analysis.has_async_operations:
            features.append("Async operations")
        if proposed['modal'] and analysis.has_modal_or_dialog:
            features.append("Modal/Dialog structure")
        if proposed['animation'] and 'animation' in analysis.jsx_patterns:
            features.append("Animation/transitions")
        if proposed['error_handling'] and analysis.has_error_handling:
            features.append("Error handling")

        return features

    def _calculate_jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        """Calculate Jaccard similarity between two sets (imports in this case)"""
        if not set_a and not set_b:
            return 1.0
        if not set_a or not set_b:
            return 0.0

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)

        return intersection / union if union > 0 else 0.0

    def _calculate_structural_similarity(self, analysis: ComponentAnalysis) -> float:
        """Calculate structural similarity based on JSX nesting patterns"""
        # Simple heuristic: components with similar nesting depth likely have similar structures
        # For form components: expect depth 15-25
        # For simple components: expect depth 5-15
        # For complex components: expect depth 25+

        if analysis.jsx_nesting_depth == 0:
            return 0.0

        # Normalize nesting depth to 0-100 scale
        # Most components fall in 10-30 range
        normalized = min(100, (analysis.jsx_nesting_depth / 30) * 100)
        return normalized

    def _calculate_form_similarity(self, analysis: ComponentAnalysis, proposed: Dict[str, set]) -> Tuple[float, float]:
        """Calculate form-specific similarity"""
        if not analysis.form_fields or not proposed['form_related']:
            return 0.0, 0.0

        # Calculate field overlap
        proposed_field_count = len(proposed.get('field_names', set()))
        actual_field_count = len(analysis.form_fields)

        if proposed_field_count == 0 and actual_field_count == 0:
            field_overlap = 100.0
        elif proposed_field_count == 0 or actual_field_count == 0:
            field_overlap = 0.0
        else:
            # Overlap based on proportion of fields
            overlap_count = min(proposed_field_count, actual_field_count)
            max_count = max(proposed_field_count, actual_field_count)
            field_overlap = (overlap_count / max_count) * 100

        # Calculate validation rule overlap
        proposed_validations = proposed.get('validation_rules', set())
        validation_overlap = 0.0
        if analysis.validation_rules and proposed_validations:
            validation_set_a = set(analysis.validation_rules)
            validation_set_b = set(proposed_validations) if isinstance(proposed_validations, (list, set)) else set()
            if validation_set_a and validation_set_b:
                validation_overlap = len(validation_set_a & validation_set_b) / len(validation_set_a | validation_set_b) * 100

        # Calculate submit handler overlap
        handler_overlap = 0.0
        proposed_handlers = proposed.get('submit_patterns', set())
        if analysis.submit_handler_patterns and proposed_handlers:
            handler_overlap = len(analysis.submit_handler_patterns & proposed_handlers) / max(
                len(analysis.submit_handler_patterns | proposed_handlers), 1
            ) * 100

        # Weighted average: fields (50%), validation (30%), submit handlers (20%)
        form_similarity = (field_overlap * 0.5) + (validation_overlap * 0.3) + (handler_overlap * 0.2)

        return form_similarity, field_overlap

    def _identify_reusable_sections(self, analysis: ComponentAnalysis, proposed: Dict[str, set], similarity: float) -> List[str]:
        """Identify which sections of the component can be reused"""
        sections = []

        if similarity < 50:
            return sections

        if analysis.form_fields:
            sections.append("Form structure & field handling")

        if analysis.has_validation:
            sections.append("Validation logic")

        if analysis.has_error_handling:
            sections.append("Error handling patterns")

        if analysis.has_async_operations:
            sections.append("Async operation patterns")

        if analysis.has_file_upload:
            sections.append("File upload handling")

        if analysis.custom_hooks:
            sections.append(f"Custom hooks: {', '.join(list(analysis.custom_hooks)[:3])}")

        if analysis.event_handlers:
            sections.append("Event handler structure")

        return sections[:5]  # Return top 5

    def _estimate_effort(self, similarity: float, field_count: int) -> str:
        """Estimate modification effort needed"""
        if similarity >= 80:
            return "low"
        elif similarity >= 60:
            return "low" if field_count <= 3 else "medium"
        elif similarity >= 40:
            return "medium"
        else:
            return "high"

    def _assess_duplication_risk(self, form_field_overlap: float, similarity: float) -> str:
        """Assess if there's a high duplication risk"""
        if similarity >= 80 or form_field_overlap >= 70:
            return "high"
        elif similarity >= 65 or form_field_overlap >= 50:
            return "medium"
        elif similarity >= 50 or form_field_overlap >= 30:
            return "low"
        else:
            return "none"

    def _generate_recommendation(self, similarity: float, reuse: float, analysis: ComponentAnalysis) -> str:
        """Generate recommendation based on scores"""

        if similarity >= 80:
            return f"EXTEND: This component is very similar ({similarity}% match). Consider extending or parameterizing it with props."
        elif similarity >= 65:
            return f"EXTEND/COPY: {similarity}% similarity found. You can extend this component with variants or use copy-then-modify pattern."
        elif similarity >= 50:
            return f"COPY-THEN-MODIFY: {similarity}% similarity. Copy and modify this component as a starting point ({reuse}% reuse potential)."
        elif similarity >= 40:
            return f"REFERENCE: {similarity}% similarity. Use this component as a reference for patterns ({reuse}% reuse potential)."
        else:
            return "CREATE NEW: No significant similarities found. Safe to create new component."


def format_report(scores: List[SimilarityScore], format_type: str = "text") -> str:
    """Format similarity detection report in requested format"""

    if format_type.lower() == "markdown":
        return format_markdown_report(scores)
    else:
        return format_text_report(scores)


def format_text_report(scores: List[SimilarityScore]) -> str:
    """Format as human-readable text report"""

    if not scores:
        return "No similar components found. Creating a new component is safe.\n"

    report = "SIMILARITY DETECTION REPORT\n"
    report += "=" * 80 + "\n\n"

    for i, score in enumerate(scores, 1):
        report += f"{i}. {score.target_name} ({score.similarity_percentage}% similar)\n"
        report += f"   File: {score.target_file}\n"
        report += f"   Reuse Potential: {score.reuse_potential}%\n"
        report += f"   Duplication Risk: {score.duplicate_risk.upper()}\n"

        if score.import_similarity > 0:
            report += f"   Import Similarity: {score.import_similarity}%\n"

        if score.form_similarity > 0:
            report += f"   Form Similarity: {score.form_similarity}%\n"
            report += f"   Form Field Overlap: {score.form_field_overlap}%\n"

        if score.shared_features:
            report += f"   Shared Features:\n"
            for feature in score.shared_features:
                report += f"     - {feature}\n"

        if score.matching_hooks:
            report += f"   Common Hooks: {', '.join(sorted(score.matching_hooks))}\n"

        if score.matching_form_fields:
            report += f"   Similar Form Fields: {', '.join(score.matching_form_fields)}\n"

        if score.reusable_sections:
            report += f"   Reusable Sections:\n"
            for section in score.reusable_sections:
                report += f"     - {section}\n"

        report += f"   Modification Effort: {score.modification_effort.upper()}\n"
        report += f"   Recommendation: {score.recommendation}\n"
        report += "\n"

    return report


def format_markdown_report(scores: List[SimilarityScore]) -> str:
    """Format as markdown report with recommendations"""

    if not scores:
        return "## Similarity Detection Results\n\nNo similar components found. Creating a new component is safe.\n"

    report = "# Component Similarity Detection Report\n\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Summary section
    report += "## Summary\n\n"
    high_risk = [s for s in scores if s.duplicate_risk == "high"]
    medium_risk = [s for s in scores if s.duplicate_risk == "medium"]
    report += f"- **Total similar components found:** {len(scores)}\n"
    report += f"- **High duplication risk:** {len(high_risk)}\n"
    report += f"- **Medium duplication risk:** {len(medium_risk)}\n"

    if high_risk:
        report += "\n### Critical Findings\n\n"
        for score in high_risk[:3]:
            report += f"**{score.target_name}** ({score.similarity_percentage}% match)\n"
            report += f"- {score.recommendation}\n"
            report += f"- Duplicate Risk: **{score.duplicate_risk.upper()}**\n\n"

    # Detailed results
    report += "## Detailed Analysis\n\n"

    for i, score in enumerate(scores, 1):
        report += f"### {i}. {score.target_name}\n\n"
        report += f"**Location:** `{score.target_file}`\n\n"

        # Key metrics
        report += "**Metrics:**\n\n"
        report += f"| Metric | Value |\n"
        report += f"|--------|-------|\n"
        report += f"| Overall Similarity | {score.similarity_percentage}% |\n"
        report += f"| Reuse Potential | {score.reuse_potential}% |\n"

        if score.import_similarity > 0:
            report += f"| Import Similarity | {score.import_similarity}% |\n"

        if score.form_similarity > 0:
            report += f"| Form Similarity | {score.form_similarity}% |\n"
            report += f"| Form Field Overlap | {score.form_field_overlap}% |\n"

        report += f"| Modification Effort | {score.modification_effort.upper()} |\n"
        report += f"| Duplication Risk | {score.duplicate_risk.upper()} |\n\n"

        # Shared features
        if score.shared_features:
            report += "**Shared Features:**\n\n"
            for feature in score.shared_features:
                report += f"- {feature}\n"
            report += "\n"

        # Reusable sections
        if score.reusable_sections:
            report += "**Reusable Sections:**\n\n"
            for section in score.reusable_sections:
                report += f"- {section}\n"
            report += "\n"

        # Matching hooks
        if score.matching_hooks:
            report += f"**Common Hooks:** `{', '.join(sorted(score.matching_hooks))}`\n\n"

        # Matching form fields
        if score.matching_form_fields:
            report += f"**Similar Form Fields:** `{', '.join(score.matching_form_fields)}`\n\n"

        # Base component recommendation
        if score.base_component and score.similarity_percentage >= 60:
            report += f"**Suggested Base Component:** `{score.base_component}`\n\n"
            report += f"**How to Proceed:**\n\n"
            if score.similarity_percentage >= 80:
                report += f"1. Extend `{score.base_component}` by adding a `variant` prop\n"
                report += f"2. Parameterize different form fields using props\n"
                report += f"3. Reuse validation and submission logic\n\n"
            else:
                report += f"1. Copy `{score.base_component}` as a starting point\n"
                report += f"2. Modify form fields and validation as needed\n"
                report += f"3. Effort: {score.modification_effort.upper()}\n\n"

        # Recommendation
        report += f"**Recommendation:**\n\n"
        report += f"> {score.recommendation}\n\n"

        report += "---\n\n"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Component Similarity Detector for React/TypeScript Codebases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python similarity_detector.py /path/to/project "A form component with file upload"
  python similarity_detector.py /path/to/project --target "contact form" --threshold 50
  python similarity_detector.py /path/to/project "Form component" --format markdown
        """
    )

    parser.add_argument('project_root', help='Root directory of the React/TypeScript project')
    parser.add_argument('description', nargs='?', default=None, help='Description of proposed component')
    parser.add_argument('--target', help='Compare specific description against all components')
    parser.add_argument('--threshold', type=int, default=40, help='Minimum similarity percentage (default: 40)')
    parser.add_argument('--format', choices=['json', 'markdown', 'text'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of results (default: 10)')

    args = parser.parse_args()

    # Get description from either positional or --target argument
    description = args.target if args.target else args.description
    if not description:
        description = "Form component with file upload and validation"

    # Validate project root
    if not Path(args.project_root).exists():
        print(f"Error: Project root '{args.project_root}' does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing components in {args.project_root}...", file=sys.stderr)

    # Analyze project
    analyzer = ComponentAnalyzer(args.project_root)
    components = analyzer.analyze_project()

    if not components:
        print("No React components found in the project.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(components)} components", file=sys.stderr)
    print(f"Analyzing proposed component: \"{description}\"", file=sys.stderr)
    print(f"Similarity threshold: {args.threshold}%\n", file=sys.stderr)

    # Detect similarities with configurable threshold
    detector = SimilarityDetector(analyzer, threshold=args.threshold)
    scores = detector.detect_similarities(description, limit=args.limit)

    # Output based on format
    if args.format == 'json':
        json_output = {
            'timestamp': datetime.now().isoformat(),
            'project_root': args.project_root,
            'description': description,
            'threshold': args.threshold,
            'total_components_analyzed': len(components),
            'similar_components_found': len(scores),
            'similar_components': [
                {
                    'file': score.target_file,
                    'name': score.target_name,
                    'similarity_percentage': score.similarity_percentage,
                    'reuse_potential': score.reuse_potential,
                    'import_similarity': score.import_similarity,
                    'form_similarity': score.form_similarity,
                    'form_field_overlap': score.form_field_overlap,
                    'structural_similarity': score.structural_similarity,
                    'shared_features': score.shared_features,
                    'reusable_sections': score.reusable_sections,
                    'modification_effort': score.modification_effort,
                    'duplicate_risk': score.duplicate_risk,
                    'recommendation': score.recommendation,
                }
                for score in scores
            ]
        }
        print(json.dumps(json_output, indent=2))
    else:
        # Text or Markdown format
        report = format_report(scores, format_type=args.format)
        print(report)


if __name__ == '__main__':
    main()
