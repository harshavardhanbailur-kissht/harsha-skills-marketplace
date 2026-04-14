#!/bin/bash
# Ultimate Debugger — Claude Code Skill Installer
#
# Deploys the skill to Claude Code's skill discovery paths.
# Run from the skill's root directory:
#   chmod +x install.sh && ./install.sh
#
# Options:
#   --global    Install to ~/.claude/skills/ (available in all projects)
#   --project   Install to ./.claude/skills/ (current project only, default)
#   --uninstall Remove installed skill

set -euo pipefail

SKILL_NAME="ultimate-debugger"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---project}"

# Validate we're in the skill directory
if [ ! -f "$SCRIPT_DIR/SKILL.md" ]; then
    echo "❌ Error: SKILL.md not found. Run this script from the skill's root directory."
    exit 1
fi

case "$MODE" in
    --global)
        TARGET_DIR="$HOME/.claude/skills/$SKILL_NAME"
        echo "📦 Installing $SKILL_NAME globally to $TARGET_DIR"
        ;;
    --project)
        # Find project root (look for .git, package.json, etc.)
        PROJECT_ROOT="$(pwd)"
        while [ "$PROJECT_ROOT" != "/" ]; do
            if [ -d "$PROJECT_ROOT/.git" ] || [ -f "$PROJECT_ROOT/package.json" ]; then
                break
            fi
            PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
        done
        if [ "$PROJECT_ROOT" = "/" ]; then
            PROJECT_ROOT="$(pwd)"
        fi
        TARGET_DIR="$PROJECT_ROOT/.claude/skills/$SKILL_NAME"
        echo "📦 Installing $SKILL_NAME to project: $TARGET_DIR"
        ;;
    --uninstall)
        for dir in "$HOME/.claude/skills/$SKILL_NAME" ".claude/skills/$SKILL_NAME"; do
            if [ -d "$dir" ] || [ -L "$dir" ]; then
                rm -rf "$dir"
                echo "✅ Removed $dir"
            fi
        done
        echo "🗑️  Uninstall complete"
        exit 0
        ;;
    *)
        echo "Usage: $0 [--global|--project|--uninstall]"
        exit 1
        ;;
esac

# Create target directory
mkdir -p "$(dirname "$TARGET_DIR")"

# Remove old installation if exists
if [ -d "$TARGET_DIR" ] || [ -L "$TARGET_DIR" ]; then
    echo "  Removing previous installation..."
    rm -rf "$TARGET_DIR"
fi

# Copy skill files (exclude build/cache artifacts)
echo "  Copying skill files..."
mkdir -p "$TARGET_DIR"

rsync -a --exclude='.pytest_cache' \
         --exclude='pytest-cache-files-*' \
         --exclude='__pycache__' \
         --exclude='.debug-session' \
         --exclude='docs/' \
         --exclude='*.pyc' \
         "$SCRIPT_DIR/" "$TARGET_DIR/" 2>/dev/null || {
    # Fallback if rsync not available
    cp -R "$SCRIPT_DIR"/* "$TARGET_DIR/"
    # Clean up artifacts
    find "$TARGET_DIR" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
    find "$TARGET_DIR" -name '.pytest_cache' -type d -exec rm -rf {} + 2>/dev/null || true
    find "$TARGET_DIR" -name 'pytest-cache-files-*' -type d -exec rm -rf {} + 2>/dev/null || true
    find "$TARGET_DIR" -name '*.pyc' -delete 2>/dev/null || true
}

# Verify installation
FILE_COUNT=$(find "$TARGET_DIR" -type f | wc -l | tr -d ' ')
echo ""
echo "✅ Installed $SKILL_NAME ($FILE_COUNT files)"
echo "   Location: $TARGET_DIR"
echo ""
echo "   Trigger in Claude Code with:"
echo "     \"use ultimate debugger\" or \"debug this with ultimate debugger\""
echo ""

# Check PyYAML dependency
python3 -c "import yaml" 2>/dev/null || {
    echo "⚠️  PyYAML is required but not installed."
    echo "   Run: pip3 install pyyaml"
}
