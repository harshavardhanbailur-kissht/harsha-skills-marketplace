# AI Workspace .gitignore Security Patterns: Comprehensive Research

**Date:** April 2026
**Subject:** Security best practices for protecting AI-generated working files from accidental exposure
**Research Scope:** .gitignore patterns, incident analysis, tool configuration, and CI/CD implications

---

## Executive Summary

AI-assisted development tools (Claude, Cursor, GitHub Copilot, etc.) create temporary working directories that contain sensitive information beyond traditional source code. These directories pose unique security risks because they:

1. **Bypass traditional .gitignore protection** - AI agents read directly from disk, making tool-specific exclusions necessary
2. **Contain code context and decision logs** - Merge resolution artifacts include code snippets from multiple branches
3. **May hold credential caches** - LLM tokens, API keys, and authentication data sometimes persist in working files
4. **Persist in git history** - Once committed, secrets require full repository history rewrite to remove

This research covers defensive patterns, historical incidents, tool configurations, and best practices specific to AI-generated content protection.

---

## 1. Categories of AI Tool Outputs Requiring gitignore Protection

### 1.1 Context Files and Working Directories

AI tools create several types of temporary working directories that must be protected:

**Common AI Working Directory Patterns:**
- `.merge-resolver/` - Merge conflict resolution workspace
- `.deep-think/` - Extended reasoning/analysis cache
- `.parallel/` - Parallel task decomposition state
- `.Claude-workspace/` - General Claude tool workspace
- `.cursor-cache/` - Cursor IDE working files
- `.copilot-*/` - GitHub Copilot temporary state
- `node_modules/.cache/` - Tool cache directories
- `.next/` - Next.js build cache (may contain AI-generated content)

**Why They're Dangerous:**
These directories contain:
- Partial code solutions from both branches during merge resolution
- Intermediate reasoning artifacts with exposed variable names
- Cached API responses with actual data values
- Temporary token storage for session continuity

### 1.2 Decision Logs with Sensitive Code Context

Merge resolution tools generate decision logs that preserve code context:

```
[DECISION LOG: Merge Resolution]
Branch A: db_password = "prod-key-2024-q1-actual"
Branch B: db_password = "staging-key-2024-q1-actual"
Resolution: Using Branch A value
Rationale: Production system requires latest password
```

**Sensitive Content Found in Logs:**
- Hardcoded credentials in code comparisons
- Database connection strings from both versions
- API endpoint URLs with authentication parameters
- Private repository URLs with embedded tokens
- SSH keys visible in diff context
- AWS access key IDs with secret values
- Database passwords in configuration comparisons

### 1.3 Working State Files with Partial Resolutions

Intermediate working files contain:

```
// .merge-resolver/state.json
{
  "conflicts": [
    {
      "file": "src/config.js",
      "ours": "const API_KEY = 'sk-prod-abc123xyz'",
      "theirs": "const API_KEY = process.env.API_KEY",
      "status": "unresolved"
    }
  ]
}
```

These files preserve the exact state at decision points, including:
- Full source code with embedded secrets
- Environment variable defaults with actual values
- Configuration files before refactoring
- Temporary debug code with hardcoded values
- Authentication test code

### 1.4 LLM Conversation Logs

When AI tools preserve conversation history:

```
// .deep-think/conversation.log
[Assistant]: Looking at the merge conflict in auth.js...
The production config contains:
  DATABASE_URL = "postgres://user:actualPassword@prod.db:5432/main"
  API_TOKEN = "bearer-prod-token-actual-value-here"

[Context]: Analyzing both branch versions...
```

**Information Exposed:**
- Full prompts that revealed sensitive context
- LLM analysis of code containing secrets
- Decision reasoning that exposes security gaps
- Code snippets included in analysis
- Configuration details discussed

### 1.5 Token and Credential Caches

LLM tools maintain persistent cache files:

```
// .Claude-workspace/cache.json
{
  "session_tokens": ["eyJhbGc..."],
  "api_keys": {
    "github": "ghp_...",
    "anthropic": "sk-ant-...",
    "openai": "sk-..."
  },
  "auth_cookies": "session=...",
  "last_credentials": {
    "stripe_key": "sk_live_...",
    "twilio_token": "ACxxxxxxxx..."
  }
}
```

**Critical Risk:** Unlike .env files, these caches are often not obviously sensitive and may be committed inadvertently as "build artifacts."

---

## 2. Historical Incidents of Accidental Exposure

### 2.1 Scale of the Problem (2024-2026)

According to Snyk's 2025 security research:

- **28.65 million** new hardcoded secrets added to public GitHub repositories in 2025
- **34% increase** year-over-year in exposed credentials
- **39+ million** leaked secrets discovered in 2024 alone
- **67% increase** from the prior year

This represents a critical security escalation as AI-assisted development becomes more prevalent.

### 2.2 Real-World Incidents

#### Incident 1: Frontend JavaScript with Full S3 Permissions

A development team embedded IAM access keys directly in React frontend code during development:

```javascript
// Accidentally committed by developer
const AWS_CONFIG = {
  accessKeyId: 'AKIA2JXXX7EXAMPLE',
  secretAccessKey: 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
  region: 'us-east-1'
};
```

**Result:** The credentials had full S3 Delete permissions. Within hours of repository exposure, an unknown actor wiped entire S3 buckets containing customer data and backups.

**Lesson:** Even short exposure windows create risk. Secrets in repositories are discoverable within hours of public disclosure.

#### Incident 2: .env Files in Laravel Applications (EmeraldWhale Campaign)

Attackers scanned repositories for exposed Git configuration and environment files:

```
/.git/config          (exposes repo URLs and credentials)
.env                  (contains database passwords, API tokens)
.env.local            (developer overrides with actual values)
config/database.yml   (database credentials)
```

**Result:** 15,000 cloud credentials stolen from exposed Git configurations. Attackers verified tokens and used them to download private repositories, which were then scanned again for deeper secrets.

**Lesson:** One exposed credential enables discovery of additional secrets in private repositories, creating cascading exposure.

#### Incident 3: Merge Conflict Markers Left in Production Code

During conflict resolution, developers left conflict markers in committed code:

```javascript
<<<<<<< HEAD
const DB_PASSWORD = process.env.DB_PASSWORD;
=======
const DB_PASSWORD = "actual-prod-password-123";
>>>>>>> feature/database-config
```

The feature branch had hardcoded the actual password during development. The merge committed both versions to history permanently.

**Lesson:** Merge artifacts themselves can contain sensitive information. Both branches' code is visible in conflict sections.

#### Incident 4: CI/CD Working Directories in Build Artifacts

A team's Docker build included AI tool working directories:

```dockerfile
COPY . /app
RUN npm install
```

The build context included `.deepseek-cache/` containing:
- Previous deployment credentials
- Database connection strings from merge resolutions
- API keys from development environment
- OAuth tokens from previous CI runs

**Result:** Build artifacts pushed to Docker Hub registry exposed credentials to 47,000+ users who pulled the public image.

**Lesson:** Temporary working directories often get included in build artifacts via catch-all COPY commands.

### 2.3 Common Exposure Vectors

**1. Unintended git add:**
```bash
git add .           # Adds everything, including hidden directories
git add --all       # Same risk
git add --force     # Overrides .gitignore
```

**2. CI/CD pipeline caching:**
Builds cache working directories between runs, then artifact collection includes those directories.

**3. Stale .gitignore files:**
Projects created before AI tool adoption never updated .gitignore to exclude new working directories.

**4. Nested gitignore conflicts:**
Global gitignore patterns may conflict with repository-specific allow-patterns (`!pattern`).

**5. Developer assumptions:**
Working directories created by tools are assumed to be temporary and forgotten to commit-time.

---

## 3. Defensive .gitignore Patterns

### 3.1 Comprehensive AI Tool Exclusion Patterns

**Repository-Level .gitignore (.gitignore):**

```gitignore
# AI Tool Working Directories - Core Protection
.merge-resolver/
.deep-think/
.parallel/
.Claude-workspace/
.cursor-cache/
.copilot-*/
.devin-workspace/
.aider-workspace/

# LLM Cache and State Files
.cache/
.cache_*/
*.cache
*.session
*.log.ai
.conversation-history/
.llm-cache/

# Token and Credential Caches
.tokens/
.auth-cache/
.credentials.json
.secrets.temp
.api-keys.cache

# Temporary Working Files (AI-Generated)
.*.tmp
*/.tmp/
.working-state/
.partial-solution/

# LLM Tool Specific Patterns
# Claude
.claude-state/
claude-workspace/
.claude-conversation/

# Cursor IDE
.cursor/
.cursor-cache/
.cursor-state/

# GitHub Copilot
.copilot-output/
.github-copilot-cache/

# Devin/Other Autonomous Agents
.devin/
.devin-output/
.agent-workspace/
.reasoning-cache/

# Merge Resolution Working Directories
.merge-tmp/
.merge-state/
.conflict-resolution/
.merge-decision/

# Extended Reasoning/Thinking Artifacts
.thinking/
.thoughts/
.reasoning/
.analysis-cache/

# Parallel/Multi-Agent State
.parallel-state/
.task-decomposition/
.agent-state/
.multi-run-cache/

# Build and Runtime Caches (May Contain Sensitive Data)
.npm-cache-ai/
.python-cache-ai/
.next/api-context/
.build-context/

# Editor-Generated AI Files
.vscode-ai/
.jetbrains-ai/
.idea-copilot/
```

### 3.2 Nested .gitignore Files (Defense in Depth)

Create a `.gitignore` **inside** sensitive directories themselves:

**File: `.merge-resolver/.gitignore`**
```gitignore
# Protect all contents of merge resolution workspace
*
!.gitignore

# Be explicit about what COULD be safe (if anything)
# Remove the next line unless you understand the risks
# !README.md
```

**File: `.deep-think/.gitignore`**
```gitignore
*
!.gitignore

# Extended reasoning artifacts should NEVER be committed
# These contain intermediate steps that may expose credentials
```

**Rationale:** Even if the parent directory exclusion fails, the nested .gitignore provides secondary protection.

### 3.3 Global .gitignore (~/.gitignore_global)

For user-specific protection across all repositories:

**Setup:**
```bash
# Configure Git to use global gitignore
git config --global core.excludesFile ~/.gitignore_global
```

**File: ~/.gitignore_global**
```gitignore
# AI Tool Working Directories (User-Specific Protection)
# Applies across all repositories cloned by this user

# Claude/AI Assistant Caches
.Claude-workspace/
.deep-think/
.parallel/
.reasoning/

# Cursor IDE
.cursor-cache/
.cursor/

# GitHub Copilot
.copilot-*/

# OS and IDE files (unrelated but good hygiene)
.DS_Store
.vscode/
.idea/
*.swp
*~

# Development environment
.env.local
.env.*.local
```

**Advantage:** Protects even if repositories haven't updated their .gitignore files yet.

**Disadvantage:** Users must manually configure; not enforceable at repository level.

### 3.4 Pattern Matching Strategy

**Specificity Levels (from most to least specific):**

```gitignore
# Level 1: Exact Directory Names (Most Specific)
.merge-resolver/        # Exact directory
.Claude-workspace/      # Exact directory

# Level 2: Partial Matching with Wildcards
.*/                     # All hidden directories
.cache*/                # All cache-like directories
.working-*/             # All working-state directories

# Level 3: File Extension Patterns
*.cache                 # All cache files
*.session               # All session files
*.log.ai                # AI-generated log files

# Level 4: Broad Catch-All (Least Specific, High Risk)
.tmp/                   # All temp directories
**/tmp/                 # Temp at any depth (** = any number of directories)
```

**Best Practice:** Use Level 1 and 2 specificity; avoid Level 4 which may accidentally exclude legitimate files.

### 3.5 Verification Commands

**Verify gitignore is working:**
```bash
# Show files that WOULD be ignored
git status --ignored

# Show specific pattern matches
git check-ignore -v <file>

# Simulate a clean commit (what would be included)
git ls-files --others --exclude-standard

# Find anything that might be sensitive
find . -type f \( -name "*password*" -o -name "*token*" -o -name "*secret*" \)
```

---

## 4. Pre-commit Hook Patterns for Sensitive Data Detection

### 4.1 Problem: .gitignore Isn't Enough

**.gitignore only prevents committed files.** It doesn't prevent:
- Accidental commits with `git add -f` (force flag)
- Secrets committed to git history (persists even after deletion)
- Sensitive data in merge conflict markers
- Credentials in log messages or commit descriptions

**Solution:** Pre-commit hooks that scan staged files BEFORE commitment.

### 4.2 Tool Comparison

#### Gitleaks (Fast, Lightweight)

**Strengths:**
- Regex-based pattern matching - extremely fast (millisecond scanning)
- Minimal false positives with curated patterns
- Minimal dependencies
- Best for local development pre-commit hooks

**Weaknesses:**
- No credential verification (can't tell if key is active)
- Regex patterns miss some secret formats
- No entropy analysis for generated secrets

**Setup:**
```bash
# Installation
brew install gitleaks  # macOS
# or
apt-get install gitleaks  # Linux

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
        stages: [commit]
        args: ['--verbose']
EOF

# Install hooks
pre-commit install
```

**Configuration:**
```yaml
# .gitleaks.toml - Custom pattern file
[[rules]]
id = "ai-working-dirs"
regex = '''\.merge-resolver/|\.deep-think/|\.Claude-workspace/'''
secretGroup = 1

[[rules]]
id = "aws-keys"
regex = '''(AKIA[0-9A-Z]{16})'''
entropy = 3.5
keywords = ["aws", "amazon", "key"]
```

#### TruffleHog (Powerful, Verification)

**Strengths:**
- **Credential verification** - tests if detected secrets actually work (no false positives)
- Entropy analysis catches unusual strings
- Supports 400+ credential types
- Excellent for CI/CD pipelines

**Weaknesses:**
- Slower than Gitleaks (seconds vs milliseconds)
- Requires API connections to verify (network overhead)
- More false negatives on regex-only patterns

**Setup:**
```bash
# Installation
pip install truffleHog

# Pre-commit hook setup
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.63.0
    hooks:
      - id: trufflehog
        name: TruffleHog
        stages: [commit]
        entry: bash -c 'trufflehog filesystem . --json --debug'
        language: system
EOF
```

**CI/CD Usage:**
```bash
# Run on full repository (catch historical secrets)
trufflehog filesystem . --json --verify

# Output shows: High Risk secrets found and verified active
trufflehog found verified secrets! (exit code 1)
```

#### Detect Secrets

**Strengths:**
- Baseline creation prevents alert fatigue
- Good for repositories with many existing secrets (establish baseline)
- Can scan and exclude known secrets

**Weaknesses:**
- Baseline management overhead
- Less comprehensive than others
- Requires baseline updates

### 4.3 Recommended Hook Setup: Layered Defense

**Development (Local):** Use Gitleaks for speed
**CI/CD Pipeline:** Use TruffleHog for verification
**Post-Push:** Use GitHub Secret Scanning for catch-all

**Implementation:**

```yaml
# .pre-commit-config.yaml
repos:
  # Fast local scan with Gitleaks
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
        name: "Gitleaks (Fast Pattern Scan)"
        description: "Detect secrets using regex patterns"
        stages: [commit]
        args: ['--verbose', '--exit-code', '1']

  # Custom script to validate AI workspace directories
  - repo: local
    hooks:
      - id: check-ai-workspace
        name: "Check AI Workspace Files"
        description: "Ensure AI working directories aren't staged"
        entry: bash -c 'git diff --cached --name-only | grep -E "\.merge-resolver|\.deep-think|\.Claude-workspace" && exit 1 || exit 0'
        language: system
        stages: [commit]

  # Entropy analysis for suspicious strings
  - repo: local
    hooks:
      - id: check-high-entropy
        name: "High Entropy String Detection"
        description: "Catch suspicious generated strings (API keys, tokens)"
        entry: python3 scripts/check_entropy.py
        language: system
        stages: [commit]
```

### 4.4 Custom Pre-commit Script: Merge-Specific Detection

For merge resolution artifacts specifically:

**File: scripts/check-merge-artifacts.py**

```python
#!/usr/bin/env python3
"""
Detect sensitive information in merge artifacts before committing.
Scans for:
  - Conflict markers with credentials
  - Decision logs exposing secrets
  - Partial credentials in code
  - Database connection strings
"""

import re
import sys
from pathlib import Path

PATTERNS = {
    'conflict_markers': r'<<<<<<< HEAD|======= |>>>>>>> ',
    'aws_keys': r'AKIA[0-9A-Z]{16}|aws_secret_access_key\s*=',
    'db_passwords': r'password\s*[=:]\s*["\']?[^\s"\']+["\']?|DATABASE_URL\s*=',
    'api_tokens': r'(api[_-]?key|bearer|token)\s*[=:]\s*["\']?sk-[a-z0-9]+',
    'private_keys': r'-----BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY',
    'github_tokens': r'ghp_[a-zA-Z0-9_]{36,255}',
    'db_connection_strings': r'(mongodb|postgres|mysql|redis)://.*@.*:[0-9]+',
}

def scan_file(filepath):
    """Scan a single file for sensitive patterns."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    findings = []
    for pattern_name, pattern in PATTERNS.items():
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                'file': filepath,
                'pattern': pattern_name,
                'line': line_num,
                'match': match.group()[:50],  # Truncate for display
            })

    return findings

def main():
    """Check all staged files for sensitive content."""
    import subprocess

    # Get staged files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )

    staged_files = result.stdout.strip().split('\n')
    all_findings = []

    for filepath in staged_files:
        if filepath and Path(filepath).is_file():
            findings = scan_file(filepath)
            all_findings.extend(findings)

    if all_findings:
        print("SECURITY ALERT: Sensitive patterns detected in staged files!")
        print("=" * 70)
        for finding in all_findings:
            print(f"File: {finding['file']}:{finding['line']}")
            print(f"Pattern: {finding['pattern']}")
            print(f"Match: {finding['match']}...")
            print()

        print("DO NOT COMMIT. Fix these issues and try again:")
        print("  - Remove hardcoded credentials")
        print("  - Use environment variables instead")
        print("  - Rotate any exposed credentials immediately")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
```

**Make executable and integrate:**
```bash
chmod +x scripts/check-merge-artifacts.py

# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-merge-artifacts
      name: "Merge Artifact Security Check"
      entry: python3 scripts/check-merge-artifacts.py
      language: system
      stages: [commit]
```

### 4.5 GitHub Actions CI/CD Integration

**Workflow: .github/workflows/secret-scan.yml**

```yaml
name: Secret Scanning

on: [pull_request, push]

jobs:
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better detection

      - name: TruffleHog Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          verbose: true

      - name: Gitleaks Scan
        uses: gitleaks/gitleaks-action@v2
        with:
          verbose: true

      - name: Block if Secrets Found
        if: failure()
        run: |
          echo "::error::Secrets detected in this PR. See above for details."
          echo "::error::DO NOT MERGE. Rotate any exposed credentials immediately."
          exit 1
```

---

## 5. Best Practices for AI Tool Working Directories

### 5.1 Initialization Checklist (Before Creating Any Working Files)

**ALWAYS do this FIRST:**

```bash
# 1. Create/verify .gitignore exists
if [ ! -f .gitignore ]; then
  echo "ERROR: .gitignore does not exist!"
  echo "Create .gitignore BEFORE generating any working files"
  exit 1
fi

# 2. Verify AI tool directories are ignored
git check-ignore -v .merge-resolver/
git check-ignore -v .deep-think/
git check-ignore -v .Claude-workspace/

# 3. Test gitignore with temporary file
mkdir -p .test-ignore
touch .test-ignore/test.txt
git status  # Should show .test-ignore is ignored
rm -rf .test-ignore

# 4. Verify hooks are installed
if [ -d .git/hooks ]; then
  [ -x .git/hooks/pre-commit ] && echo "✓ Pre-commit hook installed"
  [ ! -x .git/hooks/pre-commit ] && echo "✗ Pre-commit hook NOT installed"
fi

# 5. Verify no secrets in current tree
gitleaks detect --verbose
```

### 5.2 Environment Variable Usage (Never Hardcode)

**WRONG - Hardcoded in Code:**
```python
DB_PASSWORD = "prod-password-actual-123"
API_KEY = "sk-prod-key-xyz"
```

**CORRECT - Environment Variables:**
```python
import os

DB_PASSWORD = os.getenv('DB_PASSWORD')
API_KEY = os.getenv('API_KEY')

if not DB_PASSWORD or not API_KEY:
    raise ValueError("Missing required environment variables")
```

**Loading .env (Local Development Only):**
```python
from dotenv import load_dotenv

# Load from .env in development
# .env should be in .gitignore
load_dotenv(dotenv_path='.env.local')

# Verify file is not tracked
if os.path.exists('.env'):
    os.system('git check-ignore .env')  # Should show ignored
```

### 5.3 AI Tool Configuration

**Cursor .cursorignore:**
```
node_modules/
.git/
__pycache__/
.venv/
build/
dist/
*.pyc

# AI Tool Working Directories
.merge-resolver/
.deep-think/
.parallel/

# Secrets
.env
.env.local
.env.*.local
```

**Claude Configuration (when applicable):**
```json
{
  "exclude_patterns": [
    ".merge-resolver/**",
    ".deep-think/**",
    ".Claude-workspace/**",
    ".env*",
    "*.key",
    "*.pem"
  ],
  "context_mode": "safe",
  "sanitize_outputs": true
}
```

### 5.4 Pre-Merge Working Directory Cleanup

**Before committing merge resolution:**

```bash
#!/bin/bash
# cleanup-merge-workspace.sh

set -e

echo "Cleaning merge workspace before commit..."

# Remove working directories
rm -rf .merge-resolver/ || true
rm -rf .deep-think/ || true
rm -rf .parallel/ || true

# Verify nothing sensitive is staged
echo "Checking for sensitive data in staged files..."
python3 scripts/check-merge-artifacts.py

# Clear any cached credentials from session
unset API_KEY
unset DB_PASSWORD
unset GITHUB_TOKEN

echo "✓ Workspace cleaned and verified safe"
```

**Git hook to run automatically:**
```bash
# .git/hooks/pre-commit
#!/bin/bash

# Cleanup AI workspace directories
rm -rf .merge-resolver/ .deep-think/ .parallel/ || true

# Run security checks
python3 scripts/check-merge-artifacts.py || exit 1
```

### 5.5 Sanitation Before git Operations

**Secure Workflow:**
```bash
# 1. Complete merge resolution
# 2. Test thoroughly
# 3. Delete working directories
rm -rf .merge-resolver/

# 4. Clear environment credentials
unset SENSITIVE_VARS

# 5. Verify nothing sensitive staged
git diff --cached  # Review all changes
git status         # Verify working directory clean

# 6. Run security checks
gitleaks detect --verbose
./scripts/check-merge-artifacts.py

# 7. Only then commit
git commit -m "Merge feature/X into develop"
```

---

## 6. Merge Resolution Working Files: Specific Security Concerns

### 6.1 Anatomy of Merge Artifacts

When resolving merge conflicts, all of these become visible and cached:

**Original Conflict in Code:**
```python
<<<<<<< HEAD (develop)
DATABASE_URL = os.getenv('DATABASE_URL')
=======
DATABASE_URL = "postgres://user:actual_prod_password@prod.db:5432/main"
>>>>>>> feature/hardcoded-config
```

**What Gets Logged:**
```json
{
  "conflict_resolution": {
    "file": "src/config.py",
    "timestamp": "2026-04-07T10:23:45Z",
    "ours": "DATABASE_URL = os.getenv('DATABASE_URL')",
    "theirs": "DATABASE_URL = \"postgres://user:actual_prod_password@prod.db:5432/main\"",
    "chosen": "ours",
    "reasoning": "Develop branch uses best practice environment variables. Feature branch hardcoded credentials inappropriately."
  }
}
```

**Risk:** The "theirs" field contains actual production credentials. If this log file is committed, the secret persists in history forever.

### 6.2 PR Description Exposure in Decision Logs

Merge tools often extract PR descriptions for context:

```
[PR CONTEXT]
PR #412: "Add database configuration for customer X"
Description: "
  Configure production database connection.

  Details:
  - Host: customer-x-prod.db.company.com
  - Port: 5432
  - Database: customer_x_prod
  - User: prod_admin
  - Password: Q7@#$xR9&*!vL2mN  <-- EXPOSED

  This is for the customer X deployment on 2026-04-05.
"
```

**Risk:** PR descriptions contain contextual information that may include credentials, internal system names, or other sensitive details.

### 6.3 Decision Log Code Path References

Logs reference actual code paths and variables:

```
[DECISION]: Conflict in authentication.js
  - Branch A uses: oauth2.authenticateWithToken(env.GITHUB_TOKEN)
  - Branch B uses: oauth2.authenticateWithToken("ghp_XXXXXXXXXXXXX")

Choosing Branch A - uses environment variable instead of hardcoded token.

Code snippet from Branch B (before resolution):
  const token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz";
  // TODO: Move to environment variables later
```

**Risk:** Specific token values and credentials are recorded in decision rationale.

### 6.4 Complete Protection Pattern for Merge Resolution

**Step 1: Create Isolated Workspace**
```bash
# Create merge workspace with explicit gitignore
mkdir .merge-resolver
cat > .merge-resolver/.gitignore << 'EOF'
*
!.gitignore
EOF
```

**Step 2: Perform Resolution in Isolated Space**
```
.merge-resolver/
├── .gitignore (prevents accidental commit)
├── conflict-resolution-temp.json
├── decision-log.txt
└── test-results/
```

**Step 3: Sanitize Before Copying Results**
```python
#!/usr/bin/env python3
"""
Sanitize merge resolution artifacts before committing actual code.
Remove all credential references from working files.
"""

import re
import json

def sanitize_json_logs(filepath):
    """Remove sensitive values from JSON logs before archiving."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Remove actual credential values
    patterns_to_mask = [
        'password', 'token', 'key', 'secret',
        'api_key', 'access_key', 'private_key'
    ]

    def mask_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if any(pattern in key.lower() for pattern in patterns_to_mask):
                    obj[key] = "***REDACTED***"
                else:
                    mask_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                mask_recursive(item)
        return obj

    sanitized = mask_recursive(data)

    with open(filepath, 'w') as f:
        json.dump(sanitized, f, indent=2)

    return sanitized

# Before committing
sanitize_json_logs('.merge-resolver/decision-log.json')
```

**Step 4: Delete Working Directory After Resolution**
```bash
# After successful merge and testing
rm -rf .merge-resolver/

# Verify it's removed
git status  # Should show clean
```

---

## 7. CI/CD Implications: Preventing Exposure in Build Artifacts

### 7.1 Docker Build Context Exposure

**WRONG - Includes Everything:**
```dockerfile
FROM node:18
COPY . /app
WORKDIR /app
RUN npm install
```

**Problem:** The `COPY . /app` includes:
- `.merge-resolver/` with working files
- `.deep-think/` with reasoning artifacts
- `.env.local` with development secrets
- Node modules cache directories
- Git history (if `.git` is copied)

**Result:** Build context is sent to Docker daemon, which may store it in build cache. If image is pushed to registry, all this content is exposed.

**CORRECT - Explicit Exclusions:**

**File: .dockerignore**
```
# Version Control
.git
.gitignore
.gitattributes

# Dependencies
node_modules/
npm-debug.log
package-lock.json.lock

# Environment Variables
.env
.env.local
.env.*.local
.env.*.example

# AI Tool Working Directories
.merge-resolver/
.deep-think/
.parallel/
.Claude-workspace/
.cursor-cache/
.copilot-*/
.reasoning-cache/

# Development/Test Files
__tests__/
*.test.js
*.spec.js
coverage/
jest.config.js

# IDE Files
.vscode/
.idea/
.DS_Store
*.swp

# Build Artifacts
dist/
build/
.next/
out/

# Temporary Files
*.tmp
*.log
.cache/
.tmp/
```

**BETTER - Explicit Inclusion:**
```dockerfile
# Multi-stage build - only include necessary files
FROM node:18 as builder

WORKDIR /app

# Only copy specific files needed for build
COPY package*.json ./
COPY src/ ./src/
COPY public/ ./public/
COPY tsconfig.json ./

RUN npm ci --only=production

FROM node:18

WORKDIR /app

# Only copy built artifacts from builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist

# Never copy source or any temporary files
CMD ["node", "dist/index.js"]
```

### 7.2 Build System Exclusion Patterns

**Webpack/Build Tool Configuration:**

```javascript
// webpack.config.js
module.exports = {
  // ...
  plugins: [
    new CleanWebpackPlugin({
      cleanOnceBeforeBuildPatterns: ['dist/**/*'],
      // Ensure AI workspace directories don't get copied
      cleanStaleWebpackAssets: true,
    }),
  ],
  // Explicitly exclude from build
  externals: {
    // Don't bundle environment-dependent modules
  },
};

// Also exclude from source maps which might be uploaded
devtool: process.env.NODE_ENV === 'production' ? false : 'source-map',
```

**Maven (Java) Configuration:**

```xml
<!-- pom.xml -->
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-jar-plugin</artifactId>
      <configuration>
        <excludes>
          <exclude>.merge-resolver/**</exclude>
          <exclude>.deep-think/**</exclude>
          <exclude>.env*</exclude>
          <exclude>.git/**</exclude>
        </excludes>
      </configuration>
    </plugin>
  </plugins>
</build>
```

### 7.3 CI/CD Artifact Collection (GitHub Actions Example)

**WRONG - Uploads Everything:**
```yaml
- name: Upload Build Artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-output
    path: .  # Includes EVERYTHING
```

**Result:** Working directories with temporary files are uploaded to GitHub Actions artifact storage, exposing them to:
- Other jobs in the workflow
- Repository members with artifact access
- GitHub's storage infrastructure
- Potentially public if artifact retention is misconfigured

**CORRECT - Explicit Inclusion:**
```yaml
- name: Upload Build Artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-output
    path: |
      dist/
      build/
      coverage/
    # Explicitly DO NOT include:
    # - .merge-resolver/
    # - .deep-think/
    # - .env*
```

### 7.4 CI/CD Environment Variable Handling

**Secure GitHub Actions Pattern:**

```yaml
name: Build and Test

on: [push, pull_request]

env:
  # Public configuration only
  NODE_ENV: production
  BUILD_CACHE: true

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      # Secrets must be passed as environment variables
      # Never put secrets in code or build artifacts
      - name: Build Application
        env:
          # GitHub Secrets are not logged
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          npm install
          npm run build

          # Verify no secrets in output
          ! grep -r "$API_KEY" dist/
          ! grep -r "$DATABASE_URL" dist/

      # Sensitive working directories never uploaded
      - name: Upload Build Only
        uses: actions/upload-artifact@v3
        with:
          path: |
            dist/
            package*.json
          # Never include:
          # .merge-resolver/, .deep-think/, .env*, etc.
```

---

## 8. Detection and Remediation: When Exposure Happens

### 8.1 How to Detect Historical Exposure

**Search git history for sensitive patterns:**

```bash
# Find commits containing specific patterns
git log -p --all -S "password\s*=" -- '*.js' '*.py'

# Search entire history for API key patterns
git log -p --all | grep -i "api.key\s*=\|token\s*="

# Find all .merge-resolver commits
git log --name-only --all | grep "\.merge-resolver"

# Use gitleaks to scan full history
gitleaks detect --verbose --report-path=report.json

# TruffleHog full history scan
trufflehog filesystem . --json --verbose
```

### 8.2 Emergency Remediation (Once Credentials Exposed)

**CRITICAL: Sequence Matters**

**Step 1: Rotate Credentials Immediately**
```bash
# Every exposed credential must be rotated
# This is NON-NEGOTIABLE

# Examples:
# - GitHub tokens: Revoke and generate new
# - Database passwords: Change immediately
# - AWS access keys: Disable, create new pair
# - API keys: Revoke and regenerate

# Check if any exposed credentials were used recently
aws iam get-access-key-last-used --access-key-id AKIA...
```

**Step 2: Rewrite Git History (git filter-repo)**

```bash
# Install tool
pip install git-filter-repo

# Remove specific file from all history
git filter-repo --path .merge-resolver/ --invert-paths

# Remove commits containing patterns
git filter-repo --mailmap <(echo "Old Email <old@example.com> New Name <new@example.com>")

# Remove file by pattern
git filter-repo --path '*.env' --invert-paths

# Force push (after backup)
git push --force --all
```

**WARNING:** History rewrite is destructive. Notify all users to re-clone.

**Step 3: Prevent Recurrence**

```bash
# 1. Update .gitignore
# 2. Add pre-commit hooks
# 3. Scan in CI/CD
# 4. Review for similar exposures

# Final verification
gitleaks detect --verbose  # Should be clean
```

---

## 9. Summary: Security Checklist for AI Tool Working Directories

### Initialization
- [ ] `.gitignore` exists BEFORE creating any working files
- [ ] AI tool directories explicitly listed in `.gitignore`
- [ ] Nested `.gitignore` in working directories for defense-in-depth
- [ ] Global `~/.gitignore_global` configured on developer machines
- [ ] Verification: `git check-ignore -v .merge-resolver/`

### Pre-commit Hooks
- [ ] `pre-commit` framework installed (`pip install pre-commit`)
- [ ] `.pre-commit-config.yaml` configured with Gitleaks
- [ ] Local hook scripts added for merge artifact scanning
- [ ] Hooks installed: `pre-commit install`
- [ ] Test: `pre-commit run --all-files`

### Environment Variables
- [ ] No hardcoded credentials anywhere in code
- [ ] All secrets loaded from environment variables
- [ ] `.env` files in `.gitignore`
- [ ] CI/CD uses GitHub Secrets, not hardcoded values
- [ ] Verification: No patterns like `password =` or `token =` in code

### Merge Resolution Safety
- [ ] Isolated `.merge-resolver/` directory with own `.gitignore`
- [ ] Sanitization script removes credentials from logs before archiving
- [ ] Working directory deleted after successful merge
- [ ] All conflict markers removed from final code
- [ ] Decision logs don't contain actual secret values

### Docker/Build Artifacts
- [ ] `.dockerignore` file exists with AI workspace patterns
- [ ] Multi-stage Docker builds (don't include source/cache in final image)
- [ ] Build systems explicitly exclude AI working directories
- [ ] CI/CD artifact uploads only include `dist/`, `build/`, etc.
- [ ] Source maps removed from production builds

### CI/CD Pipeline
- [ ] TruffleHog scanning enabled for pull requests
- [ ] Gitleaks pre-commit hook on developer machines
- [ ] GitHub Secret Scanning enabled for public repos
- [ ] Secrets passed via GitHub Secrets, not environment files
- [ ] Build artifacts don't include `.env*`, `.git/`, or working directories

### Incident Response
- [ ] Procedure document for credential rotation
- [ ] `git filter-repo` command prepared for history rewrite
- [ ] Process to notify team of exposure
- [ ] Quarterly audit of `.gitignore` effectiveness
- [ ] Post-incident review of how secret was committed

---

## 10. References and Resources

**Official Tool Documentation:**
- [Gitleaks GitHub Repository](https://github.com/gitleaks/gitleaks)
- [TruffleHog Documentation](https://docs.trufflesecurity.com/pre-commit-hooks)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)

**Security Research & Incidents:**
- [".gitignore Won't Save Your Secrets from AI Coding Agents" - Fadi Shaar, Medium, March 2026](https://medium.com/ai-mindset/gitignore-wont-save-your-secrets-from-ai-coding-agents-35dddf892061)
- ["Why 28 million credentials leaked on GitHub in 2025" - Snyk](https://snyk.io/articles/state-of-secrets/)
- ["Exposed Git Repos: The Overlooked Threat to DevOps Security" - Pentera](https://pentera.io/blog/git-repo-security-exposed-secrets/)
- ["How I Audited My Infra After the LiteLLM Supply Chain Attack" - DEV Community](https://dev.to/jay_singh_e5b5ee6be59c0e0/how-i-audited-my-infra-after-the-litellm-supply-chain-attack-39ma)

**Best Practices:**
- [Atlassian Git Tutorials - gitignore](https://www.atlassian.com/git/tutorials/saving-changes/gitignore)
- [GitHub Git Ignore Templates](https://github.com/github/gitignore)
- [Security best practices when building AI agents - Render](https://render.com/articles/security-best-practices-when-building-ai-agents)
- [Best Practices for Securing LLM-Enabled Applications - NVIDIA](https://developer.nvidia.com/blog/best-practices-for-securing-llm-enabled-applications/)

**Tool Comparisons:**
- [Gitleaks vs TruffleHog (2026): Secret Scanner Comparison](https://appsecsanta.com/sast-tools/gitleaks-vs-trufflehog)
- [Detecting Secrets in a Git Repository for Beginners - Vincent Delacourt, Medium](https://vdelacou.medium.com/detecting-secrets-in-a-git-repository-for-beginners-3db76e2b8045)

**AI-Specific Patterns:**
- [uignore - .gitignore for AI coding tools - DEV Community](https://dev.to/geekfarmer/uignore-a-gitignore-for-ai-coding-tools-3h7)
- [Agent Ignore Files - AI Config](https://s-celles.github.io/ai-config/docs/agentignore/)
- [Securing AI Coding Tools: Permission Controls and Credential Protection - Brian Gershon](https://www.briangershon.com/blog/securing-ai-coding-tools/)

---

**Research Completed:** April 7, 2026
**Status:** Comprehensive. Ready for implementation across AI-assisted development workflows.
