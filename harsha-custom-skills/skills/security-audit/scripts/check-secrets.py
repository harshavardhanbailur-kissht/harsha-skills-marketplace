#!/usr/bin/env python3
"""
Secret Scanner for Security Audit
Scans files for hardcoded secrets using high-confidence regex patterns.
Uses only Python stdlib - no external dependencies required.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# High-confidence secret patterns
SECRET_PATTERNS = {
    'aws_access_key': {
        'pattern': r'AKIA[0-9A-Z]{16}',
        'confidence': 'high',
        'description': 'AWS Access Key ID'
    },
    'aws_secret_key': {
        'pattern': r'(?i)aws[_-]?secret[_-]?(?:access[_-]?)?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?',
        'confidence': 'high',
        'description': 'AWS Secret Access Key'
    },
    'github_token_classic': {
        'pattern': r'ghp_[a-zA-Z0-9]{36}',
        'confidence': 'high',
        'description': 'GitHub Personal Access Token (Classic)'
    },
    'github_token_fine': {
        'pattern': r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}',
        'confidence': 'high',
        'description': 'GitHub Personal Access Token (Fine-grained)'
    },
    'github_oauth': {
        'pattern': r'gho_[a-zA-Z0-9]{36}',
        'confidence': 'high',
        'description': 'GitHub OAuth Token'
    },
    'stripe_live_key': {
        'pattern': r'sk_live_[a-zA-Z0-9]{24,}',
        'confidence': 'high',
        'description': 'Stripe Live Secret Key'
    },
    'stripe_test_key': {
        'pattern': r'sk_test_[a-zA-Z0-9]{24,}',
        'confidence': 'medium',
        'description': 'Stripe Test Secret Key'
    },
    'stripe_restricted': {
        'pattern': r'rk_live_[a-zA-Z0-9]{24,}',
        'confidence': 'high',
        'description': 'Stripe Restricted Key'
    },
    'google_api_key': {
        'pattern': r'AIza[0-9A-Za-z_-]{35}',
        'confidence': 'high',
        'description': 'Google API Key'
    },
    'slack_token': {
        'pattern': r'xox[baprs]-[0-9]{10,13}-[a-zA-Z0-9-]+',
        'confidence': 'high',
        'description': 'Slack Token'
    },
    'slack_webhook': {
        'pattern': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9]+/B[a-zA-Z0-9]+/[a-zA-Z0-9]+',
        'confidence': 'high',
        'description': 'Slack Webhook URL'
    },
    'sendgrid_key': {
        'pattern': r'SG\.[a-zA-Z0-9]{22}\.[a-zA-Z0-9]{43}',
        'confidence': 'high',
        'description': 'SendGrid API Key'
    },
    'twilio_key': {
        'pattern': r'SK[a-f0-9]{32}',
        'confidence': 'medium',
        'description': 'Twilio API Key'
    },
    'private_key_rsa': {
        'pattern': r'-----BEGIN RSA PRIVATE KEY-----',
        'confidence': 'high',
        'description': 'RSA Private Key'
    },
    'private_key_dsa': {
        'pattern': r'-----BEGIN DSA PRIVATE KEY-----',
        'confidence': 'high',
        'description': 'DSA Private Key'
    },
    'private_key_ec': {
        'pattern': r'-----BEGIN EC PRIVATE KEY-----',
        'confidence': 'high',
        'description': 'EC Private Key'
    },
    'private_key_openssh': {
        'pattern': r'-----BEGIN OPENSSH PRIVATE KEY-----',
        'confidence': 'high',
        'description': 'OpenSSH Private Key'
    },
    'private_key_pgp': {
        'pattern': r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
        'confidence': 'high',
        'description': 'PGP Private Key'
    },
    'generic_password': {
        'pattern': r'(?i)(?:password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
        'confidence': 'medium',
        'description': 'Hardcoded Password'
    },
    'generic_secret': {
        'pattern': r'(?i)(?:secret|api[_-]?key|auth[_-]?token)\s*[:=]\s*["\']([^"\']{16,})["\']',
        'confidence': 'medium',
        'description': 'Hardcoded Secret/API Key'
    },
    'jwt_secret': {
        'pattern': r'(?i)jwt[_-]?secret\s*[:=]\s*["\']([^"\']{8,})["\']',
        'confidence': 'medium',
        'description': 'JWT Secret'
    },
    'database_url': {
        'pattern': r'(?:mongodb|postgres|mysql|redis)://[^:]+:[^@]+@[^\s"\']+',
        'confidence': 'high',
        'description': 'Database Connection String with Credentials'
    },
    'heroku_api_key': {
        'pattern': r'(?i)heroku[_-]?api[_-]?key\s*[:=]\s*["\']?([a-f0-9-]{36})["\']?',
        'confidence': 'high',
        'description': 'Heroku API Key'
    },
    'npm_token': {
        'pattern': r'//registry\.npmjs\.org/:_authToken=([a-f0-9-]{36})',
        'confidence': 'high',
        'description': 'NPM Auth Token'
    },
    'pypi_token': {
        'pattern': r'pypi-[A-Za-z0-9_-]{50,}',
        'confidence': 'high',
        'description': 'PyPI API Token'
    },
    'mailchimp_key': {
        'pattern': r'[a-f0-9]{32}-us[0-9]{1,2}',
        'confidence': 'medium',
        'description': 'Mailchimp API Key'
    },
    'facebook_token': {
        'pattern': r'EAACEdEose0cBA[0-9A-Za-z]+',
        'confidence': 'high',
        'description': 'Facebook Access Token'
    },
    'twitter_bearer': {
        'pattern': r'AAAAAAAAAAAAAAAAAAAAAA[A-Za-z0-9%]+',
        'confidence': 'medium',
        'description': 'Twitter Bearer Token'
    },
}

# Directories to skip
EXCLUDE_DIRS = {
    '.git', 'node_modules', 'vendor', '__pycache__',
    'venv', '.venv', 'env', '.env', 'dist', 'build',
    '.tox', '.pytest_cache', '.mypy_cache', 'coverage',
    '.next', '.nuxt', 'bower_components', 'jspm_packages',
    'target', 'out', 'bin', 'obj', 'packages'
}

# File patterns to skip
EXCLUDE_PATTERNS = [
    r'\.min\.js$',
    r'\.map$',
    r'\.lock$',
    r'package-lock\.json$',
    r'yarn\.lock$',
    r'\.example$',
    r'\.sample$',
    r'\.template$',
    r'\.png$', r'\.jpg$', r'\.jpeg$', r'\.gif$', r'\.ico$', r'\.svg$',
    r'\.pdf$', r'\.doc$', r'\.docx$',
    r'\.zip$', r'\.tar$', r'\.gz$', r'\.rar$',
    r'\.exe$', r'\.dll$', r'\.so$', r'\.dylib$',
    r'\.pyc$', r'\.pyo$', r'\.class$',
    r'\.woff$', r'\.woff2$', r'\.ttf$', r'\.eot$',
]

# Compile exclude patterns
EXCLUDE_REGEX = [re.compile(p) for p in EXCLUDE_PATTERNS]


def should_scan_file(filepath: str) -> bool:
    """Determine if a file should be scanned."""
    # Skip binary files and patterns
    for regex in EXCLUDE_REGEX:
        if regex.search(filepath):
            return False

    # Skip very large files (>1MB)
    try:
        if os.path.getsize(filepath) > 1024 * 1024:
            return False
    except OSError:
        return False

    return True


def is_likely_example(filepath: str, line: str) -> bool:
    """Check if the finding is likely an example/placeholder."""
    filepath_lower = filepath.lower()
    line_lower = line.lower()

    # Example files
    if any(x in filepath_lower for x in ['.example', '.sample', '.template', 'example', 'sample', 'template', 'test', 'mock', 'fixture']):
        return True

    # Common placeholder values
    placeholders = [
        'your-api-key', 'your_api_key', 'yourapikey',
        'xxx', 'your-secret', 'your_secret', 'yoursecret',
        'changeme', 'change-me', 'change_me',
        'replace-me', 'replace_me', 'replaceme',
        'placeholder', 'example', 'sample',
        '<your', '${', '#{', '{{',
        'todo', 'fixme',
    ]

    return any(p in line_lower for p in placeholders)


def scan_file(filepath: str) -> List[Dict]:
    """Scan a single file for secrets."""
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except (IOError, OSError):
        return findings

    for line_num, line in enumerate(lines, 1):
        for secret_type, config in SECRET_PATTERNS.items():
            matches = re.finditer(config['pattern'], line)
            for match in matches:
                # Skip if it looks like an example
                if is_likely_example(filepath, line):
                    continue

                # Get the matched secret (redacted)
                secret = match.group(0)
                if len(secret) > 8:
                    redacted = secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
                else:
                    redacted = '*' * len(secret)

                findings.append({
                    'file': filepath,
                    'line': line_num,
                    'type': secret_type,
                    'description': config['description'],
                    'confidence': config['confidence'],
                    'match': redacted,
                    'context': line.strip()[:100]  # First 100 chars of line
                })

    return findings


def scan_directory(root_dir: str) -> Dict:
    """Scan entire directory tree for secrets."""
    root_dir = os.path.abspath(root_dir)
    all_findings = []
    files_scanned = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if not should_scan_file(filepath):
                continue

            files_scanned += 1
            file_findings = scan_file(filepath)

            # Convert to relative paths
            for finding in file_findings:
                finding['file'] = os.path.relpath(finding['file'], root_dir)

            all_findings.extend(file_findings)

    # Sort by confidence (high first) then by file
    all_findings.sort(key=lambda x: (0 if x['confidence'] == 'high' else 1, x['file'], x['line']))

    # Summary
    high_confidence = sum(1 for f in all_findings if f['confidence'] == 'high')
    medium_confidence = sum(1 for f in all_findings if f['confidence'] == 'medium')

    return {
        'scan_root': root_dir,
        'files_scanned': files_scanned,
        'total_findings': len(all_findings),
        'high_confidence': high_confidence,
        'medium_confidence': medium_confidence,
        'findings': all_findings,
        'findings_by_type': _group_by_type(all_findings)
    }


def _group_by_type(findings: List[Dict]) -> Dict[str, int]:
    """Group findings by secret type."""
    by_type = {}
    for finding in findings:
        secret_type = finding['type']
        by_type[secret_type] = by_type.get(secret_type, 0) + 1
    return by_type


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

    # Exit with error code if high-confidence secrets found
    if results['high_confidence'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
