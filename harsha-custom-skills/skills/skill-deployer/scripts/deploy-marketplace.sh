#!/usr/bin/env bash
# Publish a skill to a Claude plugin marketplace GitHub repo.
# Usage: bash deploy-marketplace.sh <skill-folder> <repo-url> <plugin-folder>
#
# Clones the repo to a fresh working directory, drops the skill into
# <plugin-folder>/skills/<skill-name>/, bumps patch version in marketplace.json
# and <plugin-folder>/.claude-plugin/plugin.json if present, commits, and pushes
# to origin/<default-branch>. Skills are invoked via the Skill tool (their
# SKILL.md name is the slug); no sibling commands/*.md file is generated, since
# a command name matching a skill slug collides at marketplace validation time.

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
LEGACY_CMD="$PLUGIN_FOLDER/commands/$SKILL_NAME.md"

# Remove any existing skill with the same name
REPLACED=0
if [[ -d "$SKILL_DEST" ]]; then
  git rm -rf "$SKILL_DEST" >/dev/null
  REPLACED=1
fi
# Purge legacy sibling command file if it exists (collides with skill slug at
# marketplace validation).
if [[ -f "$LEGACY_CMD" ]]; then
  git rm "$LEGACY_CMD" >/dev/null
fi

# Drop the new skill in
mkdir -p "$PLUGIN_FOLDER/skills"
rsync -a \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='pytest-cache-files-*' \
  --exclude='.DS_Store' \
  --exclude='node_modules' \
  "$SKILL_PATH/" "$SKILL_DEST/"

# Align versions across marketplace.json and plugin.json, then bump patch.
# Previously bumped independently, which let them drift (1.2.1 vs 1.3.1 etc.).
python3 - "$PLUGIN_FOLDER" <<'PY'
import json, pathlib, sys
plugin_folder = sys.argv[1]

def parse(v):
    try: return tuple(int(x) for x in v.split("."))
    except Exception: return (0, 0, 0)

mp_path = pathlib.Path(".claude-plugin/marketplace.json")
pl_path = pathlib.Path(plugin_folder) / ".claude-plugin" / "plugin.json"
manifests = [p for p in (mp_path, pl_path) if p.exists()]
if not manifests:
    sys.exit(0)

versions = []
for p in manifests:
    d = json.loads(p.read_text())
    versions.append(parse(d.get("version", "0.0.0")))
hi = max(versions)
new = f"{hi[0]}.{hi[1]}.{hi[2] + 1}"

for p in manifests:
    d = json.loads(p.read_text())
    old = d.get("version", "")
    d["version"] = new
    p.write_text(json.dumps(d, indent=2) + "\n")
    print(f"bumped {p}: {old} -> {new}")
PY

# Pre-push validation: parse YAML frontmatter of every command and SKILL.md.
# Abort if anything is malformed so we don't ship a broken marketplace.
python3 - "$PLUGIN_FOLDER" <<'PY'
import pathlib, re, sys
try:
    import yaml
except ImportError:
    print("NOTE: PyYAML not installed; skipping strict YAML pre-push validation.")
    sys.exit(0)
plugin_folder = sys.argv[1]
root = pathlib.Path(plugin_folder)
errors = []
for p in list(root.glob("skills/*/SKILL.md")):
    text = p.read_text()
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not m:
        errors.append(f"  MISSING FRONTMATTER: {p}")
        continue
    try:
        fm = yaml.safe_load(m.group(1))
        if not isinstance(fm, dict):
            errors.append(f"  FRONTMATTER NOT A MAPPING: {p}")
    except yaml.YAMLError as e:
        errors.append(f"  YAML PARSE ERROR: {p}: {e}")
if errors:
    print("\n".join(errors))
    print("\nABORTING push — fix frontmatter above.")
    sys.exit(1)
print("frontmatter validated")
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
echo "  Clone:    $CLONE_DIR (safe to delete)"
echo ""
echo "Next: reinstall the marketplace plugin in Cowork to refresh the cache:"
echo "  Cowork -> Settings -> Plugins -> <marketplace> -> Update"
