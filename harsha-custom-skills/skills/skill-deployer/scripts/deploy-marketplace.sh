#!/usr/bin/env bash
# Publish a skill to a Claude plugin marketplace GitHub repo.
# Usage: bash deploy-marketplace.sh <skill-folder> <repo-url> <plugin-folder>
#
# Clones the repo to a fresh working directory, drops the skill into
# <plugin-folder>/skills/<skill-name>/, generates a slash command at
# <plugin-folder>/commands/<skill-name>.md from the SKILL.md frontmatter,
# bumps patch version in marketplace.json and <plugin-folder>/.claude-plugin/plugin.json
# if present, commits, and pushes to origin/<default-branch>.

set -euo pipefail

SKILL_PATH="${1:-}"
REPO_URL="${2:-}"
PLUGIN_FOLDER="${3:-}"

[[ -n "$SKILL_PATH" && -n "$REPO_URL" && -n "$PLUGIN_FOLDER" ]] || {
  echo "ERROR: usage: deploy-marketplace.sh <skill-folder> <repo-url> <plugin-folder>"
  exit 2
}
SKILL_PATH="${SKILL_PATH/#\~/$HOME}"

[[ -d "$SKILL_PATH" ]] || { echo "ERROR: $SKILL_PATH not found"; exit 1; }
[[ -f "$SKILL_PATH/SKILL.md" ]] || { echo "ERROR: $SKILL_PATH/SKILL.md missing"; exit 1; }

SKILL_NAME=$(awk '/^name: /{print $2; exit}' "$SKILL_PATH/SKILL.md" | tr -d '"'"'"'')
SKILL_DESC=$(awk 'BEGIN{desc=""} /^description: /{sub(/^description: /, ""); desc=$0} END{gsub(/^["'"'"']|["'"'"']$/, "", desc); print desc}' "$SKILL_PATH/SKILL.md")
[[ -n "$SKILL_NAME" ]] || { echo "ERROR: SKILL.md has no 'name:' field"; exit 1; }

REPO_NAME=$(basename "$REPO_URL" .git)
TS=$(date +%Y%m%d-%H%M%S)
CLONE_DIR="$HOME/Downloads/${REPO_NAME}-update-${TS}"

echo ">>> Cloning $REPO_URL -> $CLONE_DIR"
git clone "$REPO_URL" "$CLONE_DIR"
cd "$CLONE_DIR"

[[ -d "$PLUGIN_FOLDER" ]] || { echo "ERROR: plugin folder '$PLUGIN_FOLDER' not found in repo"; exit 1; }

SKILL_DEST="$PLUGIN_FOLDER/skills/$SKILL_NAME"
CMD_DEST="$PLUGIN_FOLDER/commands/$SKILL_NAME.md"

# Remove any existing skill + command with the same name
REPLACED=0
if [[ -d "$SKILL_DEST" ]]; then
  git rm -rf "$SKILL_DEST" >/dev/null
  REPLACED=1
fi
if [[ -f "$CMD_DEST" ]]; then
  git rm "$CMD_DEST" >/dev/null
fi

# Drop the new skill in
mkdir -p "$PLUGIN_FOLDER/skills" "$PLUGIN_FOLDER/commands"
rsync -a \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='pytest-cache-files-*' \
  --exclude='.DS_Store' \
  --exclude='node_modules' \
  "$SKILL_PATH/" "$SKILL_DEST/"

# Generate the slash command file
ESC_DESC=$(printf '%s' "$SKILL_DESC" | sed 's/"/\\"/g')
cat > "$CMD_DEST" <<CMD
---
description: ${ESC_DESC:-Load the $SKILL_NAME skill}
argument-hint: "<arguments for $SKILL_NAME>"
---

# /$SKILL_NAME

$SKILL_DESC

## Invocation

\`\`\`
/$SKILL_NAME <your arguments>
\`\`\`

## Workflow

Load the \`$SKILL_NAME\` skill and follow its SKILL.md workflow.
CMD

# Bump patch version in marketplace.json (repo root) and plugin.json (plugin folder)
python3 - "$PLUGIN_FOLDER" <<'PY'
import json, pathlib, sys
plugin_folder = sys.argv[1]

def bump_patch(v):
    parts = v.split(".")
    if len(parts) != 3: return v
    try:
        parts[2] = str(int(parts[2]) + 1)
    except ValueError:
        return v
    return ".".join(parts)

for p in [
    pathlib.Path(".claude-plugin/marketplace.json"),
    pathlib.Path(plugin_folder) / ".claude-plugin" / "plugin.json",
]:
    if p.exists():
        d = json.loads(p.read_text())
        old = d.get("version", "")
        if old:
            d["version"] = bump_patch(old)
            p.write_text(json.dumps(d, indent=2) + "\n")
            print(f"bumped {p}: {old} -> {d['version']}")
PY

# Commit + push
git add -A
ACTION="Add"
[[ "$REPLACED" -eq 1 ]] && ACTION="Update"
git -c commit.gpgsign=false commit -m "$ACTION skill: $SKILL_NAME

Deployed via skill-deployer. See $PLUGIN_FOLDER/skills/$SKILL_NAME/SKILL.md
for full description and workflow."

DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
echo ">>> Pushing to origin/$DEFAULT_BRANCH"
git push origin "HEAD:$DEFAULT_BRANCH"

echo ""
echo "=== DONE ==="
echo "  Skill:    $SKILL_NAME"
echo "  Repo:     $REPO_URL"
echo "  Path:     $PLUGIN_FOLDER/skills/$SKILL_NAME/"
echo "  Command:  $PLUGIN_FOLDER/commands/$SKILL_NAME.md"
echo "  Clone:    $CLONE_DIR (safe to delete)"
echo ""
echo "Next: reinstall the marketplace plugin in Cowork to refresh the cache:"
echo "  Cowork -> Settings -> Plugins -> <marketplace> -> Update"
