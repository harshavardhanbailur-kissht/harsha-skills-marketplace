#!/usr/bin/env bash
# Install a skill into Claude Code (~/.claude/skills/).
# Usage: bash deploy-claude-code.sh <skill-folder>
# Archives any existing skill with the same name as <name>.bak.<timestamp>/.

set -euo pipefail

SKILL_PATH="${1:-}"
[[ -n "$SKILL_PATH" ]] || { echo "ERROR: usage: deploy-claude-code.sh <skill-folder>"; exit 2; }
SKILL_PATH="${SKILL_PATH/#\~/$HOME}"

[[ -d "$SKILL_PATH" ]] || { echo "ERROR: $SKILL_PATH not found"; exit 1; }
[[ -f "$SKILL_PATH/SKILL.md" ]] || { echo "ERROR: $SKILL_PATH/SKILL.md missing"; exit 1; }

SKILL_NAME=$(awk '/^name: /{print $2; exit}' "$SKILL_PATH/SKILL.md" | tr -d '"'"'"'')
[[ -n "$SKILL_NAME" ]] || { echo "ERROR: SKILL.md has no 'name:' field"; exit 1; }

CC_DIR="$HOME/.claude/skills"
mkdir -p "$CC_DIR"
cd "$CC_DIR"

TS=$(date +%Y%m%d-%H%M%S)

# Archive any existing folder with the same name
if [[ -d "$SKILL_NAME" ]]; then
  BAK="${SKILL_NAME}.bak.${TS}"
  mv "$SKILL_NAME" "$BAK"
  echo "archived: ~/.claude/skills/$BAK"
fi

# Copy the new skill, excluding cache junk
rsync -a \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='pytest-cache-files-*' \
  --exclude='.DS_Store' \
  --exclude='node_modules' \
  "$SKILL_PATH/" "$CC_DIR/$SKILL_NAME/"

FILE_COUNT=$(find "$CC_DIR/$SKILL_NAME" -type f | wc -l | tr -d ' ')
echo "installed: ~/.claude/skills/$SKILL_NAME/ ($FILE_COUNT files)"
echo "Restart Claude Code to pick up the new skill."
