#!/usr/bin/env python3
"""
Dependency Scanner for Security Audit
Scans package manifests and reports dependencies with live + offline vulnerability check.
Uses only Python stdlib - no external dependencies required.

SCANNING STRATEGY (priority order):
1. Live tools (npm audit, pip-audit, osv-scanner, trivy) — most current CVE data
2. Bundled database — offline fallback for known high-impact vulnerabilities

Live tools are called if available on PATH. If unavailable, falls back gracefully to
the bundled database. The bundled DB is ALWAYS checked as a supplementary source.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


# ============================================================================
# BUNDLED KNOWN VULNERABILITIES DATABASE
# High-impact, commonly encountered vulnerable package versions
# Format: package_name -> list of {max_vuln, fixed, cve, severity, description}
# ============================================================================

KNOWN_VULNERABILITIES = {
    # ===================
    # NPM PACKAGES
    # ===================
    'lodash': [
        {'max_vuln': '4.17.20', 'fixed': '4.17.21', 'cve': 'CVE-2021-23337', 'severity': 'high', 'desc': 'Command injection via template'},
        {'max_vuln': '4.17.15', 'fixed': '4.17.16', 'cve': 'CVE-2020-8203', 'severity': 'high', 'desc': 'Prototype pollution'},
        {'max_vuln': '4.17.11', 'fixed': '4.17.12', 'cve': 'CVE-2019-10744', 'severity': 'critical', 'desc': 'Prototype pollution'},
    ],
    'axios': [
        {'max_vuln': '1.6.7', 'fixed': '1.6.8', 'cve': 'CVE-2024-39338', 'severity': 'high', 'desc': 'SSRF via server-side relative URL'},
        {'max_vuln': '0.21.1', 'fixed': '0.21.2', 'cve': 'CVE-2021-3749', 'severity': 'high', 'desc': 'ReDoS vulnerability'},
    ],
    'express': [
        {'max_vuln': '4.17.2', 'fixed': '4.17.3', 'cve': 'CVE-2022-24999', 'severity': 'high', 'desc': 'Open redirect via qs prototype pollution'},
    ],
    'jsonwebtoken': [
        {'max_vuln': '8.5.1', 'fixed': '9.0.0', 'cve': 'CVE-2022-23529', 'severity': 'critical', 'desc': 'Insecure key retrieval'},
        {'max_vuln': '8.5.1', 'fixed': '9.0.0', 'cve': 'CVE-2022-23540', 'severity': 'high', 'desc': 'Algorithm confusion attack'},
    ],
    'minimist': [
        {'max_vuln': '1.2.5', 'fixed': '1.2.6', 'cve': 'CVE-2021-44906', 'severity': 'critical', 'desc': 'Prototype pollution'},
        {'max_vuln': '0.2.3', 'fixed': '0.2.4', 'cve': 'CVE-2020-7598', 'severity': 'medium', 'desc': 'Prototype pollution'},
    ],
    'node-fetch': [
        {'max_vuln': '2.6.6', 'fixed': '2.6.7', 'cve': 'CVE-2022-0235', 'severity': 'high', 'desc': 'Exposure of sensitive info'},
        {'max_vuln': '3.1.0', 'fixed': '3.1.1', 'cve': 'CVE-2022-0235', 'severity': 'high', 'desc': 'Exposure of sensitive info'},
    ],
    'jquery': [
        {'max_vuln': '3.4.1', 'fixed': '3.5.0', 'cve': 'CVE-2020-11023', 'severity': 'medium', 'desc': 'XSS in jQuery.htmlPrefilter'},
        {'max_vuln': '3.4.1', 'fixed': '3.5.0', 'cve': 'CVE-2020-11022', 'severity': 'medium', 'desc': 'XSS in jQuery.htmlPrefilter'},
    ],
    'path-parse': [
        {'max_vuln': '1.0.6', 'fixed': '1.0.7', 'cve': 'CVE-2021-23343', 'severity': 'medium', 'desc': 'ReDoS'},
    ],
    'glob-parent': [
        {'max_vuln': '5.1.1', 'fixed': '5.1.2', 'cve': 'CVE-2020-28469', 'severity': 'high', 'desc': 'ReDoS'},
    ],
    'ua-parser-js': [
        {'max_vuln': '0.7.31', 'fixed': '0.7.32', 'cve': 'CVE-2022-25927', 'severity': 'high', 'desc': 'ReDoS'},
    ],
    'moment': [
        {'max_vuln': '2.29.3', 'fixed': '2.29.4', 'cve': 'CVE-2022-31129', 'severity': 'high', 'desc': 'ReDoS in date parsing'},
    ],
    'sanitize-html': [
        {'max_vuln': '2.7.0', 'fixed': '2.7.1', 'cve': 'CVE-2022-25887', 'severity': 'medium', 'desc': 'XSS via nested tags'},
    ],
    'helmet': [
        {'max_vuln': '4.6.0', 'fixed': '5.0.0', 'cve': 'CVE-2022-24895', 'severity': 'medium', 'desc': 'CSP bypass'},
    ],
    'tar': [
        {'max_vuln': '6.1.10', 'fixed': '6.1.11', 'cve': 'CVE-2021-37712', 'severity': 'high', 'desc': 'Arbitrary file overwrite'},
    ],
    'shell-quote': [
        {'max_vuln': '1.7.2', 'fixed': '1.7.3', 'cve': 'CVE-2021-42740', 'severity': 'critical', 'desc': 'Command injection'},
    ],
    'ansi-regex': [
        {'max_vuln': '5.0.0', 'fixed': '5.0.1', 'cve': 'CVE-2021-3807', 'severity': 'high', 'desc': 'ReDoS'},
    ],

    # ===================
    # PYTHON PACKAGES
    # ===================
    'django': [
        {'max_vuln': '4.2.10', 'fixed': '4.2.11', 'cve': 'CVE-2024-24680', 'severity': 'high', 'desc': 'DoS via intcomma filter'},
        {'max_vuln': '3.2.24', 'fixed': '3.2.25', 'cve': 'CVE-2024-24680', 'severity': 'high', 'desc': 'DoS via intcomma filter'},
        {'max_vuln': '4.1.12', 'fixed': '4.1.13', 'cve': 'CVE-2023-46695', 'severity': 'high', 'desc': 'DoS via UsernameField'},
    ],
    'flask': [
        {'max_vuln': '2.3.1', 'fixed': '2.3.2', 'cve': 'CVE-2023-30861', 'severity': 'high', 'desc': 'Cookie manipulation'},
    ],
    'pillow': [
        {'max_vuln': '9.4.0', 'fixed': '9.5.0', 'cve': 'CVE-2023-44271', 'severity': 'high', 'desc': 'DoS via TIFF file'},
        {'max_vuln': '10.0.0', 'fixed': '10.0.1', 'cve': 'CVE-2023-50447', 'severity': 'critical', 'desc': 'Arbitrary code execution'},
    ],
    'requests': [
        {'max_vuln': '2.31.0', 'fixed': '2.32.0', 'cve': 'CVE-2024-35195', 'severity': 'medium', 'desc': 'Certificate verification bypass'},
    ],
    'jinja2': [
        {'max_vuln': '3.1.3', 'fixed': '3.1.4', 'cve': 'CVE-2024-34064', 'severity': 'medium', 'desc': 'XSS via xmlattr filter'},
    ],
    'cryptography': [
        {'max_vuln': '41.0.7', 'fixed': '42.0.0', 'cve': 'CVE-2024-26130', 'severity': 'high', 'desc': 'NULL pointer dereference'},
        {'max_vuln': '41.0.5', 'fixed': '41.0.6', 'cve': 'CVE-2023-49083', 'severity': 'high', 'desc': 'NULL pointer dereference'},
    ],
    'werkzeug': [
        {'max_vuln': '3.0.1', 'fixed': '3.0.2', 'cve': 'CVE-2024-34069', 'severity': 'high', 'desc': 'RCE via debugger'},
        {'max_vuln': '2.3.7', 'fixed': '2.3.8', 'cve': 'CVE-2023-46136', 'severity': 'high', 'desc': 'RCE via debugger'},
    ],
    'urllib3': [
        {'max_vuln': '2.0.6', 'fixed': '2.0.7', 'cve': 'CVE-2023-45803', 'severity': 'medium', 'desc': 'Cookie leakage on redirect'},
        {'max_vuln': '1.26.17', 'fixed': '1.26.18', 'cve': 'CVE-2023-45803', 'severity': 'medium', 'desc': 'Cookie leakage on redirect'},
    ],
    'certifi': [
        {'max_vuln': '2023.5.7', 'fixed': '2023.7.22', 'cve': 'CVE-2023-37920', 'severity': 'high', 'desc': 'Removal of e-Tugra root certificate'},
    ],
    'aiohttp': [
        {'max_vuln': '3.8.5', 'fixed': '3.8.6', 'cve': 'CVE-2023-49081', 'severity': 'high', 'desc': 'HTTP request smuggling'},
    ],
    'sqlalchemy': [
        {'max_vuln': '1.4.45', 'fixed': '1.4.46', 'cve': 'CVE-2023-30530', 'severity': 'medium', 'desc': 'SQL injection via limit/offset'},
    ],
    'pyyaml': [
        {'max_vuln': '5.3.1', 'fixed': '5.4', 'cve': 'CVE-2020-14343', 'severity': 'critical', 'desc': 'Arbitrary code execution'},
    ],
    'paramiko': [
        {'max_vuln': '3.3.1', 'fixed': '3.4.0', 'cve': 'CVE-2023-48795', 'severity': 'medium', 'desc': 'Terrapin attack'},
    ],

    # ===================
    # RUBY GEMS
    # ===================
    'rails': [
        {'max_vuln': '7.0.8', 'fixed': '7.0.8.1', 'cve': 'CVE-2024-26143', 'severity': 'medium', 'desc': 'ReDoS in Accept header'},
        {'max_vuln': '7.1.3', 'fixed': '7.1.3.1', 'cve': 'CVE-2024-26143', 'severity': 'medium', 'desc': 'ReDoS in Accept header'},
    ],
    'nokogiri': [
        {'max_vuln': '1.15.5', 'fixed': '1.16.0', 'cve': 'CVE-2024-25062', 'severity': 'high', 'desc': 'Use-after-free in libxml2'},
        {'max_vuln': '1.14.2', 'fixed': '1.14.3', 'cve': 'CVE-2023-29469', 'severity': 'medium', 'desc': 'NULL pointer dereference'},
    ],
    'rack': [
        {'max_vuln': '3.0.8', 'fixed': '3.0.9', 'cve': 'CVE-2024-25126', 'severity': 'medium', 'desc': 'ReDoS in content type parsing'},
    ],
    'puma': [
        {'max_vuln': '6.3.1', 'fixed': '6.4.0', 'cve': 'CVE-2023-40175', 'severity': 'high', 'desc': 'HTTP request smuggling'},
    ],
}


def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Parse a version string into a comparable tuple.
    Handles common version formats: 1.2.3, ^1.2.3, ~1.2.3, >=1.2.3, etc.
    """
    if not version_str:
        return (0,)

    # Strip leading operators and whitespace
    clean = re.sub(r'^[~^>=<!\s]+', '', version_str.strip())

    # Handle version ranges like "1.2.3 - 2.0.0"
    if ' - ' in clean:
        clean = clean.split(' - ')[0]

    # Handle version with || (take first)
    if '||' in clean:
        clean = clean.split('||')[0].strip()

    parts = clean.split('.')
    result = []
    for p in parts:
        # Extract just the numeric part (handles 1.2.3-beta, 1.2.3rc1, etc.)
        match = re.match(r'(\d+)', p)
        if match:
            result.append(int(match.group(1)))
    return tuple(result) if result else (0,)


def compare_versions(v1: Tuple[int, ...], v2: Tuple[int, ...]) -> int:
    """
    Compare two version tuples.
    Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    # Pad shorter tuple with zeros
    max_len = max(len(v1), len(v2))
    v1_padded = v1 + (0,) * (max_len - len(v1))
    v2_padded = v2 + (0,) * (max_len - len(v2))

    if v1_padded < v2_padded:
        return -1
    elif v1_padded > v2_padded:
        return 1
    return 0


def check_vulnerabilities(name: str, version: str) -> List[Dict[str, Any]]:
    """
    Check a package against the bundled known vulnerabilities database.

    Args:
        name: Package name (case-insensitive)
        version: Version string

    Returns:
        List of vulnerability records matching this package/version
    """
    vulns = []
    name_lower = name.lower()

    if name_lower not in KNOWN_VULNERABILITIES:
        return vulns

    try:
        current = parse_version(version)
    except Exception:
        return vulns

    for vuln in KNOWN_VULNERABILITIES[name_lower]:
        try:
            max_vuln = parse_version(vuln['max_vuln'])
            # Current version is vulnerable if <= max_vuln
            if compare_versions(current, max_vuln) <= 0:
                vulns.append({
                    'cve': vuln['cve'],
                    'severity': vuln['severity'],
                    'description': vuln['desc'],
                    'vulnerable_version': vuln['max_vuln'],
                    'fixed_version': vuln['fixed'],
                    'current_version': version
                })
        except Exception:
            continue

    return vulns


def find_manifest_files(root_dir: str) -> Dict[str, List[str]]:
    """Find all package manifest files in the directory tree."""
    manifests = {
        'npm': [],      # package.json
        'pip': [],      # requirements.txt, setup.py, pyproject.toml
        'bundler': [],  # Gemfile
        'go': [],       # go.mod
        'maven': [],    # pom.xml
        'gradle': [],   # build.gradle
        'cargo': [],    # Cargo.toml
        'composer': [], # composer.json
    }

    exclude_dirs = {
        'node_modules', 'vendor', '.git', '__pycache__',
        'venv', '.venv', 'env', '.env', 'dist', 'build',
        '.tox', '.pytest_cache', '.mypy_cache'
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if filename == 'package.json':
                manifests['npm'].append(filepath)
            elif filename in ('requirements.txt', 'requirements-dev.txt', 'requirements-prod.txt'):
                manifests['pip'].append(filepath)
            elif filename == 'setup.py':
                manifests['pip'].append(filepath)
            elif filename == 'pyproject.toml':
                manifests['pip'].append(filepath)
            elif filename == 'Gemfile':
                manifests['bundler'].append(filepath)
            elif filename == 'go.mod':
                manifests['go'].append(filepath)
            elif filename == 'pom.xml':
                manifests['maven'].append(filepath)
            elif filename == 'build.gradle' or filename == 'build.gradle.kts':
                manifests['gradle'].append(filepath)
            elif filename == 'Cargo.toml':
                manifests['cargo'].append(filepath)
            elif filename == 'composer.json':
                manifests['composer'].append(filepath)

    return {k: v for k, v in manifests.items() if v}


def parse_package_json(filepath: str) -> List[Dict[str, Any]]:
    """Parse npm package.json file."""
    dependencies = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for dep_type in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
            if dep_type in data:
                for name, version in data[dep_type].items():
                    dependencies.append({
                        'name': name,
                        'version': version,
                        'type': 'production' if dep_type == 'dependencies' else 'development'
                    })
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return dependencies


def parse_requirements_txt(filepath: str) -> List[Dict[str, Any]]:
    """Parse pip requirements.txt file."""
    dependencies = []
    version_pattern = re.compile(r'^([a-zA-Z0-9_-]+)\s*([<>=!~]+\s*[\d.]+(?:,\s*[<>=!~]+\s*[\d.]+)*)?')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith('-'):
                    continue

                match = version_pattern.match(line)
                if match:
                    name = match.group(1)
                    version = match.group(2) or '*'
                    dependencies.append({
                        'name': name,
                        'version': version.strip(),
                        'type': 'development' if 'dev' in filepath.lower() else 'production'
                    })
    except IOError as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return dependencies


def parse_gemfile(filepath: str) -> List[Dict[str, Any]]:
    """Parse Ruby Gemfile."""
    dependencies = []
    gem_pattern = re.compile(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            in_dev_group = False
            for line in f:
                line = line.strip()

                if 'group :development' in line or 'group :test' in line:
                    in_dev_group = True
                elif line == 'end':
                    in_dev_group = False

                match = gem_pattern.search(line)
                if match:
                    dependencies.append({
                        'name': match.group(1),
                        'version': match.group(2) or '*',
                        'type': 'development' if in_dev_group else 'production'
                    })
    except IOError as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return dependencies


def parse_go_mod(filepath: str) -> List[Dict[str, Any]]:
    """Parse Go go.mod file."""
    dependencies = []
    require_pattern = re.compile(r'^\s*([^\s]+)\s+([^\s]+)')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            in_require_block = False
            for line in f:
                line = line.strip()

                if line.startswith('require ('):
                    in_require_block = True
                    continue
                elif line == ')':
                    in_require_block = False
                    continue

                if in_require_block or line.startswith('require '):
                    if line.startswith('require '):
                        line = line[8:].strip()

                    match = require_pattern.match(line)
                    if match and not match.group(1).startswith('//'):
                        dependencies.append({
                            'name': match.group(1),
                            'version': match.group(2),
                            'type': 'production'
                        })
    except IOError as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return dependencies


def parse_cargo_toml(filepath: str) -> List[Dict[str, Any]]:
    """Parse Rust Cargo.toml file."""
    dependencies = []
    section_pattern = re.compile(r'^\[([^\]]+)\]')
    dep_pattern = re.compile(r'^([a-zA-Z0-9_-]+)\s*=\s*(?:"([^"]+)"|{[^}]*version\s*=\s*"([^"]+)")')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            current_section = ''
            for line in f:
                line = line.strip()

                section_match = section_pattern.match(line)
                if section_match:
                    current_section = section_match.group(1)
                    continue

                if 'dependencies' in current_section:
                    dep_match = dep_pattern.match(line)
                    if dep_match:
                        version = dep_match.group(2) or dep_match.group(3) or '*'
                        dep_type = 'development' if 'dev' in current_section else 'production'
                        dependencies.append({
                            'name': dep_match.group(1),
                            'version': version,
                            'type': dep_type
                        })
    except IOError as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return dependencies


def parse_composer_json(filepath: str) -> List[Dict[str, Any]]:
    """Parse PHP composer.json file."""
    dependencies = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for dep_type in ['require', 'require-dev']:
            if dep_type in data:
                for name, version in data[dep_type].items():
                    if name != 'php':  # Skip PHP version requirement
                        dependencies.append({
                            'name': name,
                            'version': version,
                            'type': 'production' if dep_type == 'require' else 'development'
                        })
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

    return dependencies


def _tool_available(tool_name: str) -> bool:
    """Check if a CLI tool is available on PATH."""
    try:
        subprocess.run([tool_name, '--version'], capture_output=True, timeout=10)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


def run_npm_audit(cwd: str) -> Optional[Dict]:
    """Run npm audit if available. Provides live CVE data from GitHub Advisory DB."""
    try:
        result = subprocess.run(
            ['npm', 'audit', '--json'],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return None


def run_pip_audit(cwd: str) -> Optional[Dict]:
    """Run pip-audit if available. 98% recall rate against OSV + PyPI Advisory DB."""
    try:
        # Check for requirements.txt or pyproject.toml
        req_file = os.path.join(cwd, 'requirements.txt')
        args = ['pip-audit', '--format', 'json']
        if os.path.exists(req_file):
            args.extend(['-r', req_file])
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return None


def run_osv_scanner(cwd: str) -> Optional[Dict]:
    """
    Run osv-scanner if available. Google's OSV.dev database covers 40+ languages.
    Provides guided remediation (minimum version bumps) in v2.0+.
    """
    try:
        result = subprocess.run(
            ['osv-scanner', 'scan', '--recursive', '--format', 'json', cwd],
            capture_output=True,
            text=True,
            timeout=180
        )
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return None


def run_trivy(cwd: str) -> Optional[Dict]:
    """
    Run trivy filesystem scan if available. Covers multi-language + container + IaC.
    Uses NVD + vendor-specific databases.
    """
    try:
        result = subprocess.run(
            ['trivy', 'fs', '--format', 'json', '--scanners', 'vuln', cwd],
            capture_output=True,
            text=True,
            timeout=180
        )
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return None


def scan_directory(root_dir: str) -> Dict[str, Any]:
    """Main function to scan directory for dependencies."""
    root_dir = os.path.abspath(root_dir)
    manifests = find_manifest_files(root_dir)

    results = {
        'scan_root': root_dir,
        'manifests': [],
        'total_dependencies': 0,
        'production_dependencies': 0,
        'development_dependencies': 0,
        'vulnerabilities': [],
        'vulnerability_summary': {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        },
        'audit_results': {}
    }

    parsers = {
        'npm': parse_package_json,
        'pip': parse_requirements_txt,
        'bundler': parse_gemfile,
        'go': parse_go_mod,
        'cargo': parse_cargo_toml,
        'composer': parse_composer_json,
    }

    all_vulnerabilities = []

    for manager, files in manifests.items():
        parser = parsers.get(manager)
        if not parser:
            continue

        for filepath in files:
            deps = parser(filepath)
            rel_path = os.path.relpath(filepath, root_dir)

            # Check each dependency against bundled vulnerability database
            deps_with_vulns = []
            for dep in deps:
                dep_copy = dep.copy()
                vulns = check_vulnerabilities(dep['name'], dep['version'])
                if vulns:
                    dep_copy['vulnerabilities'] = vulns
                    for vuln in vulns:
                        vuln_record = {
                            'package': dep['name'],
                            'version': dep['version'],
                            'manifest': rel_path,
                            'manager': manager,
                            'type': dep['type'],
                            **vuln
                        }
                        all_vulnerabilities.append(vuln_record)
                        # Update severity counts
                        sev = vuln.get('severity', 'medium').lower()
                        if sev in results['vulnerability_summary']:
                            results['vulnerability_summary'][sev] += 1
                deps_with_vulns.append(dep_copy)

            manifest_entry = {
                'manager': manager,
                'file': rel_path,
                'dependencies': deps_with_vulns,
                'count': len(deps_with_vulns)
            }
            results['manifests'].append(manifest_entry)

            for dep in deps:
                results['total_dependencies'] += 1
                if dep['type'] == 'production':
                    results['production_dependencies'] += 1
                else:
                    results['development_dependencies'] += 1

    # Store bundled DB vulnerabilities
    results['vulnerabilities'] = all_vulnerabilities
    results['total_vulnerabilities'] = len(all_vulnerabilities)

    # ================================================================
    # LIVE CVE SCANNING (primary source — more current than bundled DB)
    # Each tool is called if available. Results stored under audit_results.
    # ================================================================
    live_tools_used = []
    live_tools_skipped = []

    # npm audit (JavaScript/Node.js — GitHub Advisory DB)
    if manifests.get('npm'):
        npm_dir = os.path.dirname(manifests['npm'][0])
        if _tool_available('npm'):
            npm_audit = run_npm_audit(npm_dir)
            if npm_audit:
                results['audit_results']['npm'] = npm_audit
                live_tools_used.append('npm-audit')
            else:
                live_tools_skipped.append('npm-audit (ran but no output)')
        else:
            live_tools_skipped.append('npm-audit (not installed)')

    # pip-audit (Python — OSV + PyPI Advisory DB, 98% recall)
    if manifests.get('pip'):
        pip_dir = os.path.dirname(manifests['pip'][0])
        if _tool_available('pip-audit'):
            pip_result = run_pip_audit(pip_dir)
            if pip_result:
                results['audit_results']['pip'] = pip_result
                live_tools_used.append('pip-audit')
            else:
                live_tools_skipped.append('pip-audit (ran but no output)')
        else:
            live_tools_skipped.append('pip-audit (not installed)')

    # osv-scanner (Universal — Google OSV.dev, 40+ languages)
    if _tool_available('osv-scanner'):
        osv_result = run_osv_scanner(root_dir)
        if osv_result:
            results['audit_results']['osv-scanner'] = osv_result
            live_tools_used.append('osv-scanner')
        else:
            live_tools_skipped.append('osv-scanner (ran but no output)')
    else:
        live_tools_skipped.append('osv-scanner (not installed)')

    # trivy (Multi-language + containers + IaC — NVD + vendor DBs)
    if _tool_available('trivy'):
        trivy_result = run_trivy(root_dir)
        if trivy_result:
            results['audit_results']['trivy'] = trivy_result
            live_tools_used.append('trivy')
        else:
            live_tools_skipped.append('trivy (ran but no output)')
    else:
        live_tools_skipped.append('trivy (not installed)')

    # Metadata for audit report
    results['live_scanning'] = {
        'tools_used': live_tools_used,
        'tools_skipped': live_tools_skipped,
        'bundled_db_used': True,  # Always used as supplementary
        'note': 'Bundled DB provides offline fallback. Install live tools for current CVE data: npm (built-in), pip-audit, osv-scanner, trivy'
    }

    if not live_tools_used:
        print("WARNING: No live CVE scanning tools found on PATH. Using bundled DB only (may be stale).", file=sys.stderr)
        print("Install recommended tools: pip install pip-audit; go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest", file=sys.stderr)

    return results


def main():
    """Entry point."""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.getcwd()

    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    results = scan_directory(root_dir)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
