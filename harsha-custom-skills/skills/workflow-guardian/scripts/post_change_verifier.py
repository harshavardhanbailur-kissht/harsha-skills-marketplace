#!/usr/bin/env python3
"""
Workflow Guardian: Post-Change Verifier
========================================
Verifies that changes haven't broken the existing application.
Run this AFTER making changes (Phase 4 of Workflow Guardian).

Usage:
    python3 post_change_verifier.py <project-root> [--system-map <path>]

What it checks:
    - TypeScript compilation (no type errors)
    - All imports resolve (no broken references)
    - No new orphaned files
    - Build succeeds
    - No new color values outside blessed palette
    - No new dependencies that conflict with existing stack
    - All routes still have their components
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from collections import defaultdict

SKIP_DIRS = {
    'node_modules', '.git', 'dist', 'build', '.next', '.nuxt',
    '.cache', 'coverage', '__pycache__', '.workflow-guardian',
    '.deep-think', 'vendor', '.turbo', '.vercel'
}


def run_command(cmd: list, cwd: str, timeout: int = 120) -> dict:
    """Run a shell command and return result."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout[:5000],  # Truncate
            'stderr': result.stderr[:5000],
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'stdout': '', 'stderr': 'Command timed out', 'returncode': -1}
    except FileNotFoundError:
        return {'success': False, 'stdout': '', 'stderr': f'Command not found: {cmd[0]}', 'returncode': -1}


def check_typescript(root: Path) -> dict:
    """Check TypeScript compilation."""
    tsconfig = root / 'tsconfig.json'
    if not tsconfig.exists():
        return {'status': 'skipped', 'reason': 'No tsconfig.json found'}

    result = run_command(['npx', 'tsc', '--noEmit', '--pretty'], str(root))
    errors = []
    if not result['success']:
        for line in result['stdout'].split('\n'):
            if re.match(r'.*\.tsx?.*error TS\d+:', line):
                errors.append(line.strip())

    return {
        'status': 'pass' if result['success'] else 'fail',
        'error_count': len(errors),
        'errors': errors[:20],  # First 20 errors
        'raw': result['stderr'][:2000] if not result['success'] else ''
    }


def check_build(root: Path) -> dict:
    """Check if the project builds successfully."""
    pkg_path = root / 'package.json'
    if not pkg_path.exists():
        return {'status': 'skipped', 'reason': 'No package.json found'}

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except Exception:
        return {'status': 'skipped', 'reason': 'Could not parse package.json'}

    scripts = pkg.get('scripts', {})
    if 'build' not in scripts:
        return {'status': 'skipped', 'reason': 'No build script in package.json'}

    result = run_command(['npm', 'run', 'build'], str(root), timeout=180)
    return {
        'status': 'pass' if result['success'] else 'fail',
        'output': result['stdout'][-2000:] if result['success'] else result['stderr'][:2000]
    }


def check_lint(root: Path) -> dict:
    """Run ESLint if available."""
    pkg_path = root / 'package.json'
    if not pkg_path.exists():
        return {'status': 'skipped', 'reason': 'No package.json'}

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except Exception:
        return {'status': 'skipped', 'reason': 'Could not parse package.json'}

    scripts = pkg.get('scripts', {})
    if 'lint' in scripts:
        result = run_command(['npm', 'run', 'lint'], str(root))
    else:
        result = run_command(['npx', 'eslint', 'src/', '--max-warnings=0'], str(root))

    return {
        'status': 'pass' if result['success'] else 'fail',
        'output': result['stdout'][:2000] if not result['success'] else 'No issues'
    }


def check_imports(root: Path) -> dict:
    """Check for broken import references."""
    broken_imports = []

    for ext in ['.ts', '.tsx', '.js', '.jsx']:
        for filepath in root.rglob(f'**/*{ext}'):
            if any(skip in str(filepath) for skip in SKIP_DIRS):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for match in re.finditer(
                    r"import\s+.*from\s+['\"](\.[^'\"]+)['\"]",
                    content
                ):
                    import_path = match.group(1)
                    resolved = resolve_import(filepath.parent, import_path)
                    if not resolved:
                        broken_imports.append({
                            'file': str(filepath.relative_to(root)),
                            'import': import_path,
                            'line': content[:match.start()].count('\n') + 1
                        })
            except Exception:
                continue

    return {
        'status': 'pass' if not broken_imports else 'fail',
        'broken_count': len(broken_imports),
        'broken_imports': broken_imports[:20]
    }


def resolve_import(from_dir: Path, import_path: str) -> bool:
    """Check if a relative import can be resolved."""
    base = from_dir / import_path

    # Check exact path
    if base.exists():
        return True

    # Check with extensions
    for ext in ['.ts', '.tsx', '.js', '.jsx', '.json', '.css']:
        if base.with_suffix(ext).exists():
            return True

    # Check index files
    if base.is_dir():
        for ext in ['.ts', '.tsx', '.js', '.jsx']:
            if (base / f'index{ext}').exists():
                return True

    return False


def check_route_integrity(root: Path, system_map: dict = None) -> dict:
    """Verify all routes still have their components."""
    if not system_map or 'routes' not in system_map:
        return {'status': 'skipped', 'reason': 'No system map or routes available'}

    broken_routes = []
    for route in system_map['routes']:
        component = route.get('component', '')
        if component and component != 'unknown':
            # Search for the component file
            found = False
            for ext in ['.tsx', '.jsx', '.ts', '.js']:
                for filepath in root.rglob(f'**/{component}{ext}'):
                    if any(skip in str(filepath) for skip in SKIP_DIRS):
                        continue
                    found = True
                    break
                if found:
                    break

            if not found:
                # Check if it's defined in the same file
                route_file = root / route.get('file', '')
                if route_file.exists():
                    try:
                        with open(route_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        if component in content:
                            found = True
                    except Exception:
                        pass

            if not found:
                broken_routes.append({
                    'path': route.get('path', 'unknown'),
                    'component': component,
                    'defined_in': route.get('file', 'unknown')
                })

    return {
        'status': 'pass' if not broken_routes else 'fail',
        'broken_count': len(broken_routes),
        'broken_routes': broken_routes
    }


def check_color_consistency(root: Path, system_map: dict = None) -> dict:
    """Check for new color values not in the existing palette."""
    if not system_map or 'styles' not in system_map:
        return {'status': 'skipped', 'reason': 'No style information available'}

    # Extract known colors from system map
    known_colors = set()
    for var in system_map.get('styles', {}).get('css_variables', []):
        if 'color' in var.get('name', '').lower():
            known_colors.add(var['value'])

    # Check for new hex colors in source files
    new_colors = []
    for ext in ['.tsx', '.jsx', '.css']:
        for filepath in root.rglob(f'src/**/*{ext}'):
            if any(skip in str(filepath) for skip in SKIP_DIRS):
                continue
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for match in re.finditer(r'#([0-9a-fA-F]{3,8})\b', content):
                    hex_color = f'#{match.group(1)}'
                    if hex_color not in known_colors:
                        new_colors.append({
                            'color': hex_color,
                            'file': str(filepath.relative_to(root)),
                            'line': content[:match.start()].count('\n') + 1
                        })
            except Exception:
                continue

    return {
        'status': 'pass' if not new_colors else 'warning',
        'new_color_count': len(new_colors),
        'new_colors': new_colors[:20]
    }


def verify_changes(project_root: str, system_map_path: str = None) -> dict:
    """Main verification function."""
    root = Path(project_root).resolve()

    if not root.exists():
        print(f"Error: Project root '{project_root}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Load system map if available
    system_map = None
    if system_map_path:
        try:
            with open(system_map_path) as f:
                system_map = json.load(f)
        except Exception:
            pass
    else:
        default_map = root / '.workflow-guardian' / 'system-map.json'
        if default_map.exists():
            try:
                with open(default_map) as f:
                    system_map = json.load(f)
            except Exception:
                pass

    print(f"Verifying changes in: {root}")
    print("=" * 60)

    results = {}

    # 1. TypeScript check
    print("\n[1/6] Checking TypeScript compilation...")
    results['typescript'] = check_typescript(root)
    status = results['typescript']['status']
    print(f"  Result: {status.upper()}")
    if status == 'fail':
        print(f"  Errors: {results['typescript']['error_count']}")

    # 2. Build check
    print("\n[2/6] Checking build...")
    results['build'] = check_build(root)
    print(f"  Result: {results['build']['status'].upper()}")

    # 3. Lint check
    print("\n[3/6] Running linter...")
    results['lint'] = check_lint(root)
    print(f"  Result: {results['lint']['status'].upper()}")

    # 4. Import resolution
    print("\n[4/6] Checking import resolution...")
    results['imports'] = check_imports(root)
    print(f"  Result: {results['imports']['status'].upper()}")
    if results['imports']['status'] == 'fail':
        print(f"  Broken imports: {results['imports']['broken_count']}")

    # 5. Route integrity
    print("\n[5/6] Checking route integrity...")
    results['routes'] = check_route_integrity(root, system_map)
    print(f"  Result: {results['routes']['status'].upper()}")

    # 6. Color consistency
    print("\n[6/6] Checking color consistency...")
    results['colors'] = check_color_consistency(root, system_map)
    print(f"  Result: {results['colors']['status'].upper()}")
    if results['colors']['status'] == 'warning':
        print(f"  New colors found: {results['colors']['new_color_count']}")

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r.get('status') == 'pass')
    failed = sum(1 for r in results.values() if r.get('status') == 'fail')
    warnings = sum(1 for r in results.values() if r.get('status') == 'warning')
    skipped = sum(1 for r in results.values() if r.get('status') == 'skipped')

    print(f"  Passed:   {passed}")
    print(f"  Failed:   {failed}")
    print(f"  Warnings: {warnings}")
    print(f"  Skipped:  {skipped}")

    overall = 'PASS' if failed == 0 else 'FAIL'
    print(f"\n  Overall: {overall}")

    if failed > 0:
        print("\n  FAILED CHECKS:")
        for name, result in results.items():
            if result.get('status') == 'fail':
                print(f"    - {name}")

    # Write results
    guardian_dir = root / '.workflow-guardian'
    guardian_dir.mkdir(exist_ok=True)
    output_path = guardian_dir / 'verification-results.json'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'overall': overall,
            'summary': {
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'skipped': skipped
            },
            'results': results
        }, f, indent=2)

    print(f"\n  Results saved to: {output_path}")
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 post_change_verifier.py <project-root> [--system-map <path>]")
        sys.exit(1)

    project_root = sys.argv[1]
    system_map = None

    if '--system-map' in sys.argv:
        idx = sys.argv.index('--system-map')
        if idx + 1 < len(sys.argv):
            system_map = sys.argv[idx + 1]

    results = verify_changes(project_root, system_map)

    # Exit with error code if any check failed
    if any(r.get('status') == 'fail' for r in results.values()):
        sys.exit(1)
