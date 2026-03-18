#!/usr/bin/env python3
"""
Workflow Guardian: Codebase Analyzer
====================================
Generates a structured JSON inventory of an existing codebase.
This is the first step of Phase 1 (Reconnaissance) — run this before making ANY changes.

Usage:
    python3 codebase_analyzer.py <project-root> [--output <path>]

Output:
    system-map.json in the project's .workflow-guardian/ directory (or --output path)

What it extracts:
    - File inventory (all source files, grouped by type)
    - Component tree (React/Vue/Svelte components with imports/exports)
    - Route map (extracted from router config files)
    - Style system (CSS architecture, Tailwind config, color tokens)
    - Data model (TypeScript types/interfaces)
    - Dependencies (package.json analysis)
    - Role definitions (auth-related constants and guards)
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict

# Directories to skip during analysis
SKIP_DIRS = {
    'node_modules', '.git', 'dist', 'build', '.next', '.nuxt',
    '.cache', 'coverage', '__pycache__', '.workflow-guardian',
    '.deep-think', 'vendor', '.turbo', '.vercel'
}

# File extensions to analyze
SOURCE_EXTENSIONS = {
    '.ts', '.tsx', '.js', '.jsx', '.vue', '.svelte',
    '.css', '.scss', '.less', '.sass',
    '.json', '.yaml', '.yml', '.toml',
    '.html', '.md'
}

COMPONENT_EXTENSIONS = {'.tsx', '.jsx', '.vue', '.svelte'}
STYLE_EXTENSIONS = {'.css', '.scss', '.less', '.sass'}
CONFIG_FILES = {
    'package.json', 'tsconfig.json', 'tailwind.config.js', 'tailwind.config.ts',
    'vite.config.ts', 'vite.config.js', 'next.config.js', 'next.config.ts',
    'firebase.json', 'firestore.rules', '.env', '.env.local', '.env.example',
    'supabase/config.toml'
}


def collect_files(root: Path) -> dict:
    """Collect all source files grouped by type."""
    files = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in SOURCE_EXTENSIONS or fname in CONFIG_FILES:
                rel_path = os.path.relpath(os.path.join(dirpath, fname), root)
                size = os.path.getsize(os.path.join(dirpath, fname))
                files[ext].append({
                    'path': rel_path,
                    'name': fname,
                    'size': size,
                    'lines': count_lines(os.path.join(dirpath, fname))
                })
    return dict(files)


def count_lines(filepath: str) -> int:
    """Count lines in a file, handling encoding errors."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def extract_imports(filepath: str) -> list:
    """Extract import statements from a JS/TS file."""
    imports = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # ES6 imports
        for match in re.finditer(
            r'import\s+(?:{[^}]*}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            content
        ):
            imports.append(match.group(1))

        # Dynamic imports
        for match in re.finditer(r'import\([\'"]([^\'"]+)[\'"]\)', content):
            imports.append(match.group(1))

        # require statements
        for match in re.finditer(r'require\([\'"]([^\'"]+)[\'"]\)', content):
            imports.append(match.group(1))

    except Exception:
        pass
    return imports


def extract_exports(filepath: str) -> dict:
    """Extract export information from a JS/TS file."""
    exports = {'default': None, 'named': []}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Default export
        default_match = re.search(
            r'export\s+default\s+(?:function|class|const|let|var)?\s*(\w+)',
            content
        )
        if default_match:
            exports['default'] = default_match.group(1)

        # Named exports
        for match in re.finditer(
            r'export\s+(?:function|class|const|let|var|interface|type|enum)\s+(\w+)',
            content
        ):
            exports['named'].append(match.group(1))

    except Exception:
        pass
    return exports


def extract_components(root: Path, files: dict) -> list:
    """Extract React/Vue/Svelte component information."""
    components = []

    for ext in COMPONENT_EXTENSIONS:
        if ext not in files:
            continue
        for file_info in files[ext]:
            filepath = root / file_info['path']
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Detect component type
                is_page = '/pages/' in file_info['path'] or '/views/' in file_info['path']
                is_layout = 'layout' in file_info['name'].lower()

                # Extract props interface
                props = []
                props_match = re.search(
                    r'(?:interface|type)\s+\w*Props\w*\s*(?:=\s*)?{([^}]+)}',
                    content
                )
                if props_match:
                    for prop in re.finditer(r'(\w+)\s*[?:]', props_match.group(1)):
                        props.append(prop.group(1))

                # Extract hooks used
                hooks = list(set(re.findall(r'(use\w+)\s*\(', content)))

                # Extract state declarations
                state_vars = []
                for match in re.finditer(
                    r'const\s+\[(\w+),\s*set\w+\]\s*=\s*useState',
                    content
                ):
                    state_vars.append(match.group(1))

                imports = extract_imports(str(filepath))
                exports = extract_exports(str(filepath))

                components.append({
                    'name': exports['default'] or Path(file_info['name']).stem,
                    'path': file_info['path'],
                    'type': 'page' if is_page else ('layout' if is_layout else 'component'),
                    'lines': file_info['lines'],
                    'props': props,
                    'hooks': hooks,
                    'state_vars': state_vars,
                    'imports': imports,
                    'local_imports': [i for i in imports if i.startswith('.') or i.startswith('@/')],
                    'external_imports': [i for i in imports if not i.startswith('.') and not i.startswith('@/')]
                })
            except Exception:
                continue

    return components


def extract_routes(root: Path) -> list:
    """Extract route definitions from the codebase."""
    routes = []

    # Search for common router files
    router_patterns = [
        'src/App.tsx', 'src/App.jsx', 'src/router.ts', 'src/router.tsx',
        'src/routes.ts', 'src/routes.tsx', 'app/layout.tsx',
        'pages/_app.tsx', 'src/main.tsx'
    ]

    for pattern in router_patterns:
        for filepath in root.glob(pattern):
            if any(skip in str(filepath) for skip in SKIP_DIRS):
                continue
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # React Router patterns
                for match in re.finditer(
                    r'<Route\s+[^>]*path\s*=\s*[\'"]([^\'"]+)[\'"][^>]*'
                    r'(?:element\s*=\s*{?\s*<(\w+)|component\s*=\s*{?\s*(\w+))?',
                    content
                ):
                    route = {
                        'path': match.group(1),
                        'component': match.group(2) or match.group(3) or 'unknown',
                        'file': str(filepath.relative_to(root))
                    }

                    # Check for role guards in the surrounding context
                    line_start = max(0, content.rfind('\n', 0, match.start()))
                    line_end = content.find('\n', match.end())
                    context = content[line_start:line_end]

                    role_match = re.search(
                        r'allowedRoles\s*=\s*{?\s*\[([^\]]+)\]',
                        context
                    )
                    if role_match:
                        route['roles'] = [
                            r.strip().strip("'\"")
                            for r in role_match.group(1).split(',')
                        ]
                    routes.append(route)

                # Next.js app router (directory-based)
                if 'app/' in str(filepath):
                    pages_dir = root / 'app'
                    if pages_dir.exists():
                        for page_file in pages_dir.rglob('page.tsx'):
                            route_path = '/' + str(
                                page_file.parent.relative_to(pages_dir)
                            ).replace('\\', '/')
                            if route_path == '/.':
                                route_path = '/'
                            routes.append({
                                'path': route_path,
                                'component': 'page',
                                'file': str(page_file.relative_to(root))
                            })

            except Exception:
                continue

    return routes


def extract_styles(root: Path, files: dict) -> dict:
    """Extract styling system information including design tokens and color palettes."""
    styles = {
        'architecture': 'unknown',
        'colors': {},
        'tailwind_config': None,
        'css_files': [],
        'css_variables': [],
        'tailwind_colors_used': [],
        'color_palette_inventory': {},
        'spacing_scale': [],
        'typography_scale': []
    }

    # Check for Tailwind
    tailwind_configs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.startswith('tailwind.config'):
                tailwind_configs.append(os.path.join(dirpath, fname))

    if tailwind_configs:
        styles['architecture'] = 'tailwind'
        try:
            with open(tailwind_configs[0], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            styles['tailwind_config'] = str(Path(tailwind_configs[0]).relative_to(root))

            # Extract custom colors from theme.extend.colors or colors
            for pattern in [
                r'colors\s*:\s*{([^}]+(?:{[^}]+}[^}]*)*)}',
                r'extend\s*:\s*{[^}]*colors\s*:\s*{([^}]+(?:{[^}]+}[^}]*)*)}'
            ]:
                color_section = re.search(pattern, content, re.DOTALL)
                if color_section:
                    styles['colors']['tailwind_custom'] = color_section.group(1).strip()
                    # Extract individual color names
                    for color_match in re.finditer(r'(\w+(?:-\d+)?)\s*:', color_section.group(1)):
                        color_name = color_match.group(1)
                        if color_name not in styles['tailwind_colors_used']:
                            styles['tailwind_colors_used'].append(color_name)
                    break

            # Extract spacing scale
            spacing_match = re.search(
                r'(?:extend\s*:\s*)?spacing\s*:\s*{([^}]+)}',
                content, re.DOTALL
            )
            if spacing_match:
                for space_match in re.finditer(r'["\']?([\w-]+)["\']?\s*:\s*["\']([^"\']+)["\']', spacing_match.group(1)):
                    styles['spacing_scale'].append({
                        'name': space_match.group(1),
                        'value': space_match.group(2)
                    })

        except Exception:
            pass

    # Extract CSS variables from index.css or global.css using os.walk
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname in ['index.css', 'global.css', 'globals.css', 'app.css']:
                css_file = Path(dirpath) / fname
                try:
                    with open(css_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    styles['css_files'].append(str(css_file.relative_to(root)))

                    # Extract CSS variables
                    for match in re.finditer(r'--([\w-]+)\s*:\s*([^;]+);', content):
                        var_name = match.group(1)
                        var_value = match.group(2).strip()
                        styles['css_variables'].append({
                            'name': f'--{var_name}',
                            'value': var_value,
                            'file': str(css_file.relative_to(root))
                        })

                        # Categorize color variables
                        if 'color' in var_name.lower():
                            category = var_name.split('-')[1] if '-' in var_name else 'other'
                            if category not in styles['color_palette_inventory']:
                                styles['color_palette_inventory'][category] = []
                            styles['color_palette_inventory'][category].append({
                                'name': var_name,
                                'value': var_value
                            })

                    # Extract @apply patterns (Tailwind)
                    for match in re.finditer(
                        r'\.(\w[\w-]*)\s*{[^}]*@apply\s+([^;]+);',
                        content
                    ):
                        styles['colors'][f'.{match.group(1)}'] = match.group(2).strip()

                except Exception:
                    continue

    # Detect and extract Tailwind color usage from components
    if styles['architecture'] == 'tailwind':
        tailwind_classes = set()
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                if Path(fname).suffix in COMPONENT_EXTENSIONS:
                    filepath = Path(dirpath) / fname
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        # Find Tailwind color utility classes
                        for match in re.finditer(
                            r'(?:bg|text|border|ring|shadow)-(\w+(?:-\d+)?)',
                            content
                        ):
                            color_class = match.group(1)
                            tailwind_classes.add(color_class)
                    except Exception:
                        continue
        styles['tailwind_colors_used'] = sorted(list(tailwind_classes))

    # Detect CSS-in-JS
    if not tailwind_configs:
        has_styled = any(
            'styled-components' in str(f['path']) or '@emotion' in str(f['path'])
            for ext_files in files.values() for f in ext_files
        )
        if has_styled:
            styles['architecture'] = 'css-in-js'
        elif any(ext in files for ext in ['.module.css', '.module.scss']):
            styles['architecture'] = 'css-modules'

    return styles


def extract_types(root: Path, files: dict) -> list:
    """Extract TypeScript type/interface definitions."""
    types = []
    type_files = [f for ext in ['.ts', '.tsx'] if ext in files for f in files[ext]]

    for file_info in type_files:
        filepath = root / file_info['path']
        # Skip files outside src/
        if 'node_modules' in file_info['path'] or 'dist' in file_info['path']:
            continue
        # Prioritize type definition files
        if not any(kw in file_info['path'].lower() for kw in ['type', 'interface', 'model', 'schema']):
            if file_info['lines'] > 100:  # Skip large non-type files
                continue

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract interfaces
            for match in re.finditer(
                r'(?:export\s+)?interface\s+(\w+)\s*(?:extends\s+([^{]+))?\s*{([^}]+)}',
                content, re.DOTALL
            ):
                fields = []
                for field_match in re.finditer(
                    r'(\w+)\s*(\?)?:\s*([^;\n]+)',
                    match.group(3)
                ):
                    fields.append({
                        'name': field_match.group(1),
                        'optional': bool(field_match.group(2)),
                        'type': field_match.group(3).strip().rstrip(',')
                    })

                types.append({
                    'name': match.group(1),
                    'kind': 'interface',
                    'extends': match.group(2).strip() if match.group(2) else None,
                    'fields': fields,
                    'file': file_info['path']
                })

            # Extract type aliases
            for match in re.finditer(
                r'(?:export\s+)?type\s+(\w+)\s*=\s*([^;]+);',
                content
            ):
                types.append({
                    'name': match.group(1),
                    'kind': 'type',
                    'definition': match.group(2).strip(),
                    'file': file_info['path']
                })

        except Exception:
            continue

    return types


def extract_roles(root: Path) -> dict:
    """Extract role definitions and auth patterns."""
    roles = {
        'definitions': [],
        'guards': [],
        'auth_system': 'unknown'
    }

    # Only scan src/ directory for roles (avoid scanning everything)
    src_dir = root / 'src'
    scan_dirs = [src_dir] if src_dir.exists() else [root]

    for scan_dir in scan_dirs:
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                ext = Path(fname).suffix.lower()
                if ext not in {'.ts', '.tsx', '.js', '.jsx'}:
                    continue
                filepath = Path(dirpath) / fname
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Find role arrays/enums
                    for match in re.finditer(
                        r'(?:roles|ROLES|userRoles|allowedRoles)\s*[:=]\s*[\[{]([^\]}>]+)[\]}>]',
                        content
                    ):
                        role_values = re.findall(r"['\"](\w+)['\"]", match.group(1))
                        if role_values:
                            roles['definitions'].append({
                                'values': role_values,
                                'file': str(filepath.relative_to(root))
                            })

                    # Detect auth system
                    if 'firebase/auth' in content or 'FirebaseAuth' in content:
                        roles['auth_system'] = 'firebase'
                    elif 'supabase' in content.lower() and 'auth' in content.lower():
                        roles['auth_system'] = 'supabase'
                    elif '@auth0' in content:
                        roles['auth_system'] = 'auth0'
                    elif 'next-auth' in content or 'NextAuth' in content:
                        roles['auth_system'] = 'nextauth'

                except Exception:
                    continue

    return roles


def extract_form_patterns(root: Path, files: dict) -> list:
    """Extract form components, fields, validation patterns, and API endpoints."""
    forms = []

    # Scan component files for form patterns
    for ext in COMPONENT_EXTENSIONS:
        if ext not in files:
            continue

        for file_info in files[ext]:
            filepath = root / file_info['path']
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Skip files without form indicators
                if not any(keyword in content for keyword in [
                    'onSubmit', 'handleSubmit', 'useForm', 'Formik',
                    'form', 'Form', '<input', '<textarea', '<select'
                ]):
                    continue

                # Detect form type
                is_form_file = any(keyword in file_info['name'].lower() for keyword in ['form', 'submit', 'modal'])

                # Extract form name
                form_name = None
                name_match = re.search(r'(?:function|const)\s+(\w*(?:Form|Submit|Modal)\w*)', content)
                if name_match:
                    form_name = name_match.group(1)

                if not form_name and is_form_file:
                    form_name = Path(file_info['name']).stem

                if not form_name:
                    continue

                # Extract form fields
                fields = []

                # From useState declarations with form state pattern
                for match in re.finditer(
                    r'const\s+\[(\w+),\s*set\w+\]\s*=\s*useState\s*\(\s*{([^}]+)}',
                    content, re.DOTALL
                ):
                    state_name = match.group(1)
                    if 'form' in state_name.lower() or 'data' in state_name.lower():
                        # Extract field names from object initialization
                        for field_match in re.finditer(r'(\w+)\s*:', match.group(2)):
                            fields.append({
                                'name': field_match.group(1),
                                'source': 'useState',
                                'type': 'unknown'
                            })

                # From form input elements
                for match in re.finditer(
                    r'(?:name|id)\s*=\s*["\']([^"\']+)["\']|name\s*:\s*["\']([^"\']+)["\']',
                    content
                ):
                    field_name = match.group(1) or match.group(2)
                    if field_name and not any(f['name'] == field_name for f in fields):
                        fields.append({
                            'name': field_name,
                            'source': 'input_element',
                            'type': 'unknown'
                        })

                # Detect validation patterns
                validation_type = 'none'
                validation_library = None

                if 'Zod' in content or 'z.object' in content or 'z.string()' in content:
                    validation_type = 'schema'
                    validation_library = 'zod'
                elif 'yup' in content.lower():
                    validation_type = 'schema'
                    validation_library = 'yup'
                elif 'Formik' in content:
                    validation_type = 'formik'
                    validation_library = 'formik'
                elif 'react-hook-form' in content or 'useForm' in content:
                    validation_type = 'hook-form'
                    validation_library = 'react-hook-form'
                elif re.search(r'if\s*\(\s*!\w+\.trim\(\)', content):
                    validation_type = 'manual'

                # Detect form submission endpoint
                submission_endpoint = None
                endpoint_patterns = [
                    r'(?:fetch|axios|supabase|api)\s*\(\s*["\']([^"\']+)["\']',
                    r'url\s*:\s*["\']([^"\']+)["\']',
                    r'endpoint\s*[:=]\s*["\']([^"\']+)["\']',
                    r'await\s+(?:create|submit|post)(?:Issue|Form|Data|Submission)\s*\(\s*["\']([^"\']+)["\']'
                ]

                for pattern in endpoint_patterns:
                    match = re.search(pattern, content)
                    if match:
                        submission_endpoint = match.group(1)
                        break

                # Only add if we found meaningful form data
                if fields or submission_endpoint:
                    forms.append({
                        'name': form_name,
                        'path': file_info['path'],
                        'lines': file_info['lines'],
                        'fields': fields[:20],  # Limit to first 20 fields
                        'field_count': len(fields),
                        'validation': {
                            'type': validation_type,
                            'library': validation_library
                        },
                        'submission_endpoint': submission_endpoint,
                        'has_file_upload': 'File' in content or 'file' in content.lower()
                    })

            except Exception:
                continue

    return forms


def extract_provider_tree(root: Path, files: dict) -> dict:
    """Extract Context providers and their hierarchical structure."""
    providers = {
        'contexts': [],
        'providers': [],
        'provider_hierarchy': None
    }

    # Search for Context definitions
    for ext in {'.ts', '.tsx', '.js', '.jsx'}:
        if ext not in files:
            continue

        for file_info in files[ext]:
            filepath = root / file_info['path']
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find Context.create calls
                for match in re.finditer(
                    r'(?:const|export\s+const)\s+(\w*Context\w*)\s*=\s*(?:React\.)?createContext',
                    content
                ):
                    context_name = match.group(1)
                    providers['contexts'].append({
                        'name': context_name,
                        'file': file_info['path'],
                        'type': 'context'
                    })

                # Find Provider components
                for match in re.finditer(
                    r'(?:export\s+)?(?:function|const)\s+(\w*Provider\w*)\s*\(\s*{?\s*children',
                    content
                ):
                    provider_name = match.group(1)

                    # Extract what contexts it provides
                    provides = []
                    context_match = re.search(
                        rf'{provider_name}[^}}]*?\.Provider[^>]*?value\s*=\s*{{([^}}]+)}}',
                        content,
                        re.DOTALL
                    )
                    if context_match:
                        for ctx_ref in re.finditer(r'(\w*Context\w*)', context_match.group(1)):
                            provides.append(ctx_ref.group(1))

                    providers['providers'].append({
                        'name': provider_name,
                        'file': file_info['path'],
                        'provides': provides,
                        'lines': file_info['lines'],
                        'type': 'provider'
                    })

            except Exception:
                continue

    # Try to detect provider hierarchy from App.tsx or main entry
    app_files = ['src/App.tsx', 'src/App.jsx', 'src/main.tsx', 'pages/_app.tsx', 'app/layout.tsx']
    for app_file in app_files:
        app_path = root / app_file
        if app_path.exists():
            try:
                with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
                    app_content = f.read()

                # Extract provider nesting order
                hierarchy = []
                for match in re.finditer(r'<(\w*Provider\w*)(?:\s|>)', app_content):
                    provider_name = match.group(1)
                    if provider_name not in hierarchy:
                        hierarchy.append(provider_name)

                if hierarchy:
                    providers['provider_hierarchy'] = hierarchy
                    break

            except Exception:
                continue

    return providers


def extract_hook_dependencies(root: Path, files: dict) -> dict:
    """Extract custom hooks and their dependency graph."""
    hooks = {
        'custom_hooks': [],
        'hook_dependencies': [],
        'data_fetching_hooks': []
    }

    for ext in {'.ts', '.tsx', '.js', '.jsx'}:
        if ext not in files:
            continue

        for file_info in files[ext]:
            filepath = root / file_info['path']
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find custom hook definitions (use* exports)
                for match in re.finditer(
                    r'(?:export\s+)?(?:function|const)\s+(use\w+)\s*\(',
                    content
                ):
                    hook_name = match.group(1)

                    # Check if it calls other hooks
                    calls_other_hooks = []
                    for hook_call in re.finditer(r'(use\w+)\s*\(', content[match.start():]):
                        called_hook = hook_call.group(1)
                        if called_hook != hook_name and called_hook not in calls_other_hooks:
                            calls_other_hooks.append(called_hook)

                    # Check if it fetches data
                    fetches_data = bool(re.search(
                        r'(?:useEffect|fetch|axios|supabase|firebase|EventSource)',
                        content[match.start():match.start() + 500]
                    ))

                    hook_info = {
                        'name': hook_name,
                        'file': file_info['path'],
                        'calls_hooks': calls_other_hooks,
                        'fetches_data': fetches_data
                    }

                    hooks['custom_hooks'].append(hook_info)

                    if fetches_data:
                        hooks['data_fetching_hooks'].append(hook_name)

                    # Add dependencies
                    for called_hook in calls_other_hooks:
                        hooks['hook_dependencies'].append({
                            'from': hook_name,
                            'to': called_hook,
                            'file': file_info['path']
                        })

            except Exception:
                continue

    return hooks


def extract_realtime_subscriptions(root: Path, files: dict) -> list:
    """Extract realtime subscriptions (Firebase, Supabase, WebSocket, EventSource)."""
    subscriptions = []

    for ext in COMPONENT_EXTENSIONS:
        if ext not in files:
            continue

        for file_info in files[ext]:
            filepath = root / file_info['path']
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Firebase onSnapshot
                for match in re.finditer(
                    r'(?:onSnapshot|onValue)\s*\(\s*(?:ref\s*\(\s*)?([^,\)]+)\s*[,\)]',
                    content
                ):
                    subscriptions.append({
                        'type': 'firebase',
                        'target': match.group(1).strip(),
                        'component': file_info['path'],
                        'method': 'onSnapshot'
                    })

                # Supabase realtime subscription
                for match in re.finditer(
                    r'\.on\s*\(\s*["\'](\w+)["\'][,\)]',
                    content
                ):
                    if 'supabase' in content.lower():
                        subscriptions.append({
                            'type': 'supabase',
                            'event': match.group(1),
                            'component': file_info['path'],
                            'method': 'channel.on'
                        })

                # WebSocket
                for match in re.finditer(
                    r'new\s+WebSocket\s*\(\s*["\']([^"\']+)["\']',
                    content
                ):
                    subscriptions.append({
                        'type': 'websocket',
                        'url': match.group(1),
                        'component': file_info['path']
                    })

                # EventSource
                for match in re.finditer(
                    r'new\s+EventSource\s*\(\s*["\']([^"\']+)["\']',
                    content
                ):
                    subscriptions.append({
                        'type': 'eventsource',
                        'url': match.group(1),
                        'component': file_info['path']
                    })

            except Exception:
                continue

    return subscriptions


def extract_dependencies(root: Path) -> dict:
    """Extract dependency information from package.json."""
    pkg_path = root / 'package.json'
    if not pkg_path.exists():
        return {}

    try:
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)

        return {
            'name': pkg.get('name', 'unknown'),
            'dependencies': pkg.get('dependencies', {}),
            'devDependencies': pkg.get('devDependencies', {}),
            'scripts': pkg.get('scripts', {}),
            'framework': detect_framework(pkg),
            'build_tool': detect_build_tool(pkg)
        }
    except Exception:
        return {}


def detect_framework(pkg: dict) -> str:
    """Detect the primary framework from package.json."""
    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

    if 'next' in deps:
        return 'nextjs'
    elif 'nuxt' in deps:
        return 'nuxt'
    elif '@angular/core' in deps:
        return 'angular'
    elif 'svelte' in deps or '@sveltejs/kit' in deps:
        return 'svelte'
    elif 'vue' in deps:
        return 'vue'
    elif 'react' in deps:
        return 'react'
    return 'unknown'


def detect_build_tool(pkg: dict) -> str:
    """Detect the build tool from package.json."""
    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

    if 'vite' in deps:
        return 'vite'
    elif 'webpack' in deps:
        return 'webpack'
    elif 'esbuild' in deps:
        return 'esbuild'
    elif 'next' in deps:
        return 'next (built-in)'
    elif 'parcel' in deps:
        return 'parcel'
    return 'unknown'


def analyze_codebase(project_root: str, output_path: str = None) -> dict:
    """Main analysis function."""
    root = Path(project_root).resolve()

    if not root.exists():
        print(f"Error: Project root '{project_root}' does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing codebase at: {root}")

    # Collect files
    print("  Collecting files...")
    files = collect_files(root)

    total_files = sum(len(f) for f in files.values())
    total_lines = sum(fi['lines'] for f in files.values() for fi in f)
    print(f"  Found {total_files} source files ({total_lines} total lines)")

    # Extract components
    print("  Extracting components...")
    components = extract_components(root, files)
    print(f"  Found {len(components)} components")

    # Extract routes
    print("  Extracting routes...")
    routes = extract_routes(root)
    print(f"  Found {len(routes)} routes")

    # Extract styles
    print("  Analyzing style system...")
    styles = extract_styles(root, files)
    print(f"  Style architecture: {styles['architecture']}")

    # Extract types
    print("  Extracting type definitions...")
    types = extract_types(root, files)
    print(f"  Found {len(types)} type definitions")

    # Extract roles
    print("  Analyzing role system...")
    roles = extract_roles(root)
    print(f"  Auth system: {roles['auth_system']}")

    # Extract dependencies
    print("  Analyzing dependencies...")
    deps = extract_dependencies(root)

    # Extract form patterns
    print("  Analyzing form patterns...")
    forms = extract_form_patterns(root, files)
    print(f"  Found {len(forms)} forms")

    # Extract provider tree
    print("  Analyzing context providers...")
    providers = extract_provider_tree(root, files)
    print(f"  Found {len(providers['contexts'])} contexts, {len(providers['providers'])} providers")

    # Extract hook dependencies
    print("  Analyzing custom hooks...")
    hooks = extract_hook_dependencies(root, files)
    print(f"  Found {len(hooks['custom_hooks'])} custom hooks")

    # Extract realtime subscriptions
    print("  Detecting realtime subscriptions...")
    subscriptions = extract_realtime_subscriptions(root, files)
    print(f"  Found {len(subscriptions)} subscriptions")

    # Build system map
    system_map = {
        'project_root': str(root),
        'analysis_timestamp': __import__('datetime').datetime.now().isoformat(),
        'summary': {
            'total_files': total_files,
            'total_lines': total_lines,
            'framework': deps.get('framework', 'unknown'),
            'build_tool': deps.get('build_tool', 'unknown'),
            'style_architecture': styles['architecture'],
            'auth_system': roles['auth_system'],
            'component_count': len(components),
            'route_count': len(routes),
            'type_count': len(types),
            'form_count': len(forms),
            'context_count': len(providers['contexts']),
            'provider_count': len(providers['providers']),
            'hook_count': len(hooks['custom_hooks']),
            'subscription_count': len(subscriptions)
        },
        'files': files,
        'components': components,
        'routes': routes,
        'styles': styles,
        'types': types,
        'roles': roles,
        'dependencies': deps,
        'forms': forms,
        'providers': providers,
        'hooks': hooks,
        'subscriptions': subscriptions
    }

    # Write output
    if not output_path:
        guardian_dir = root / '.workflow-guardian'
        guardian_dir.mkdir(exist_ok=True)
        output_path = str(guardian_dir / 'system-map.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(system_map, f, indent=2, default=str)

    print(f"\nSystem map written to: {output_path}")
    print(f"\nSummary:")
    print(f"  Framework:    {system_map['summary']['framework']}")
    print(f"  Build tool:   {system_map['summary']['build_tool']}")
    print(f"  Styles:       {system_map['summary']['style_architecture']}")
    print(f"  Auth:         {system_map['summary']['auth_system']}")
    print(f"  Components:   {system_map['summary']['component_count']}")
    print(f"  Routes:       {system_map['summary']['route_count']}")
    print(f"  Types:        {system_map['summary']['type_count']}")
    print(f"  Forms:        {system_map['summary']['form_count']}")
    print(f"  Contexts:     {system_map['summary']['context_count']}")
    print(f"  Providers:    {system_map['summary']['provider_count']}")
    print(f"  Custom hooks: {system_map['summary']['hook_count']}")
    print(f"  Subscriptions:{system_map['summary']['subscription_count']}")
    print(f"  Total files:  {system_map['summary']['total_files']}")
    print(f"  Total lines:  {system_map['summary']['total_lines']}")

    return system_map


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 codebase_analyzer.py <project-root> [--output <path>]")
        sys.exit(1)

    project_root = sys.argv[1]
    output = None

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output = sys.argv[idx + 1]

    analyze_codebase(project_root, output)
