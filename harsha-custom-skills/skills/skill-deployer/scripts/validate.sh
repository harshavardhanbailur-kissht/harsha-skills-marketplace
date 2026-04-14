#!/usr/bin/env bash
# Pre-flight validation for a skill folder.
# Usage: bash validate.sh <skill-folder>
# Exits 0 on pass, non-zero on fail. Prints a human-readable report either way.

set -euo pipefail

SKILL_PATH="${1:-}"
[[ -n "$SKILL_PATH" ]] || { echo "ERROR: usage: validate.sh <skill-folder>"; exit 2; }

# Expand ~
SKILL_PATH="${SKILL_PATH/#\~/$HOME}"

FAIL=0
warn() { echo "  WARN: $1"; }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
pass() { echo "  PASS: $1"; }

echo "Validating: $SKILL_PATH"

# --- folder exists ---
[[ -d "$SKILL_PATH" ]] && pass "folder exists" || { fail "folder not found"; exit 1; }

# --- SKILL.md present ---
SKILL_MD="$SKILL_PATH/SKILL.md"
[[ -f "$SKILL_MD" ]] && pass "SKILL.md present" || fail "SKILL.md missing at root"

# --- frontmatter has name ---
if [[ -f "$SKILL_MD" ]]; then
  SKILL_NAME=$(awk '/^name: /{print $2; exit}' "$SKILL_MD" | tr -d '"'"'"'')
  if [[ -n "${SKILL_NAME:-}" ]]; then
    pass "skill name: $SKILL_NAME"
  else
    fail "frontmatter missing 'name:' field"
  fi

  # --- frontmatter has description ---
  if grep -q "^description: " "$SKILL_MD"; then
    pass "description present"
  else
    warn "description missing — recommended for skill discovery"
  fi
fi

# --- no secrets ---
if grep -rIl --exclude-dir=node_modules --exclude-dir=__pycache__ \
    -E '(api[_-]?key|secret|password|token|private[_-]?key)' "$SKILL_PATH" \
    2>/dev/null | grep -qv -E '\.(md|rst|txt)$'; then
  warn "possible secret references found — review files before publishing"
fi

if find "$SKILL_PATH" -maxdepth 4 -type f \( -name '.env' -o -name '.env.*' -o -name 'credentials.json' -o -name '.credentials.json' \) 2>/dev/null | grep -q .; then
  fail "env/credentials file found in skill folder — remove before publishing"
fi

# --- no absolute user paths hardcoded ---
if grep -rIl --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude-dir=.pytest_cache \
    -E '(^|[^a-zA-Z])(/Users/[^/]+|/home/[^/]+)' "$SKILL_PATH" 2>/dev/null | head -5 | grep -q .; then
  warn "hardcoded absolute user paths detected — skills should be portable"
fi

# --- cache junk (informational; rsync will strip) ---
CACHE_COUNT=$(find "$SKILL_PATH" \( -name '__pycache__' -o -name '.pytest_cache' -o -name 'pytest-cache-files-*' -o -name '.DS_Store' \) 2>/dev/null | wc -l | tr -d ' ')
if [[ "$CACHE_COUNT" -gt 0 ]]; then
  warn "$CACHE_COUNT cache/junk entries found (will be excluded on deploy)"
fi

echo ""
if [[ "$FAIL" -eq 0 ]]; then
  echo "RESULT: PASS — ready to deploy"
  echo "SKILL_NAME=$SKILL_NAME"
  exit 0
else
  echo "RESULT: FAIL — $FAIL blocker(s). Fix before deploying."
  exit 1
fi
