#!/usr/bin/env bash
# detect_environment.sh — Detect language, framework, test runner, and git status
# Usage: bash detect_environment.sh [project-root]
# Output: JSON to stdout

set -euo pipefail

PROJECT_ROOT="${1:-.}"
cd "$PROJECT_ROOT"

# --- Language Detection ---
LANGUAGE="unknown"
FRAMEWORK="unknown"

if [ -f "Cargo.toml" ]; then
    LANGUAGE="rust"
elif [ -f "go.mod" ]; then
    LANGUAGE="go"
elif [ -f "package.json" ]; then
    if [ -f "tsconfig.json" ] || grep -q '"typescript"' package.json 2>/dev/null; then
        LANGUAGE="typescript"
    else
        LANGUAGE="javascript"
    fi
elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "Pipfile" ]; then
    LANGUAGE="python"
elif [ -f "pom.xml" ]; then
    LANGUAGE="java"
    if grep -q "kotlin" pom.xml 2>/dev/null; then
        LANGUAGE="kotlin"
    fi
elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    if [ -f "build.gradle.kts" ] || ([ -f "build.gradle" ] && grep -q "kotlin" build.gradle 2>/dev/null); then
        LANGUAGE="kotlin"
    else
        LANGUAGE="java"
    fi
elif [ -f "Gemfile" ]; then
    LANGUAGE="ruby"
elif [ -f "composer.json" ]; then
    LANGUAGE="php"
elif ls *.csproj 1>/dev/null 2>&1 || ls *.sln 1>/dev/null 2>&1; then
    LANGUAGE="csharp"
fi

# --- Framework Detection ---
if [ -f "package.json" ]; then
    PKG=$(cat package.json 2>/dev/null || echo "{}")
    if echo "$PKG" | grep -q '"next"'; then FRAMEWORK="nextjs";
    elif echo "$PKG" | grep -q '"@angular/core"'; then FRAMEWORK="angular";
    elif echo "$PKG" | grep -q '"vue"'; then FRAMEWORK="vue";
    elif echo "$PKG" | grep -q '"svelte"'; then FRAMEWORK="svelte";
    elif echo "$PKG" | grep -q '"express"'; then FRAMEWORK="express";
    elif echo "$PKG" | grep -q '"fastify"'; then FRAMEWORK="fastify";
    elif echo "$PKG" | grep -q '"react"'; then FRAMEWORK="react";
    fi
fi
if [ "$LANGUAGE" = "python" ]; then
    REQS=""
    [ -f "requirements.txt" ] && REQS=$(cat requirements.txt 2>/dev/null)
    [ -f "pyproject.toml" ] && REQS="$REQS $(cat pyproject.toml 2>/dev/null)"
    if echo "$REQS" | grep -qi "django"; then FRAMEWORK="django";
    elif echo "$REQS" | grep -qi "fastapi"; then FRAMEWORK="fastapi";
    elif echo "$REQS" | grep -qi "flask"; then FRAMEWORK="flask";
    fi
fi
if [ "$LANGUAGE" = "ruby" ] && [ -f "Gemfile" ]; then
    if grep -q "rails" Gemfile 2>/dev/null; then FRAMEWORK="rails"; fi
fi
if [ "$LANGUAGE" = "go" ]; then
    if grep -q "gin-gonic" go.mod 2>/dev/null; then FRAMEWORK="gin";
    elif grep -q "echo" go.mod 2>/dev/null; then FRAMEWORK="echo";
    elif grep -q "fiber" go.mod 2>/dev/null; then FRAMEWORK="fiber";
    fi
fi

# --- Test Runner Detection ---
TEST_RUNNER="unknown"
TEST_COMMAND="unknown"

case "$LANGUAGE" in
    javascript|typescript)
        if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ] || [ -f "vitest.config.mts" ]; then
            TEST_RUNNER="vitest"
            TEST_COMMAND="npx vitest run"
        elif [ -f "jest.config.js" ] || [ -f "jest.config.ts" ] || [ -f "jest.config.mjs" ]; then
            TEST_RUNNER="jest"
            TEST_COMMAND="npx jest"
        elif [ -f "package.json" ]; then
            PKG=$(cat package.json 2>/dev/null || echo "{}")
            if echo "$PKG" | grep -q '"vitest"'; then
                TEST_RUNNER="vitest"
                TEST_COMMAND="npx vitest run"
            elif echo "$PKG" | grep -q '"jest"'; then
                TEST_RUNNER="jest"
                TEST_COMMAND="npx jest"
            elif echo "$PKG" | grep -q '"mocha"'; then
                TEST_RUNNER="mocha"
                TEST_COMMAND="npx mocha"
            fi
            # Check scripts.test in package.json
            SCRIPT_TEST=$(echo "$PKG" | grep -o '"test"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"//')
            if [ -n "$SCRIPT_TEST" ] && [ "$TEST_RUNNER" = "unknown" ]; then
                TEST_COMMAND="npm test"
                if echo "$SCRIPT_TEST" | grep -q "vitest"; then TEST_RUNNER="vitest";
                elif echo "$SCRIPT_TEST" | grep -q "jest"; then TEST_RUNNER="jest";
                elif echo "$SCRIPT_TEST" | grep -q "mocha"; then TEST_RUNNER="mocha";
                else TEST_RUNNER="npm-script"; fi
            fi
        fi
        ;;
    python)
        if [ -f "pytest.ini" ] || [ -f "conftest.py" ] || [ -f "setup.cfg" ]; then
            TEST_RUNNER="pytest"
            TEST_COMMAND="python -m pytest"
        elif [ -f "pyproject.toml" ] && grep -q '\[tool\.pytest' pyproject.toml 2>/dev/null; then
            TEST_RUNNER="pytest"
            TEST_COMMAND="python -m pytest"
        else
            # Default to pytest for Python projects (most common)
            TEST_RUNNER="pytest"
            TEST_COMMAND="python -m pytest"
        fi
        ;;
    go)
        TEST_RUNNER="go-test"
        TEST_COMMAND="go test ./..."
        ;;
    rust)
        TEST_RUNNER="cargo-test"
        TEST_COMMAND="cargo test"
        ;;
    java|kotlin)
        if [ -f "pom.xml" ]; then
            TEST_RUNNER="maven"
            TEST_COMMAND="mvn test"
        elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
            TEST_RUNNER="gradle"
            TEST_COMMAND="./gradlew test"
        fi
        ;;
    ruby)
        if [ -f ".rspec" ] || [ -d "spec" ]; then
            TEST_RUNNER="rspec"
            TEST_COMMAND="bundle exec rspec"
        elif [ -d "test" ]; then
            TEST_RUNNER="minitest"
            TEST_COMMAND="bundle exec rake test"
        fi
        ;;
    php)
        if [ -f "phpunit.xml" ] || [ -f "phpunit.xml.dist" ]; then
            TEST_RUNNER="phpunit"
            TEST_COMMAND="./vendor/bin/phpunit"
        fi
        ;;
    csharp)
        TEST_RUNNER="dotnet-test"
        TEST_COMMAND="dotnet test"
        ;;
esac

# --- Git Status ---
GIT_CLEAN="false"
GIT_STATUS="not a git repo"
GIT_BRANCH=""

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    DIRTY=$(git status --porcelain 2>/dev/null)
    if [ -z "$DIRTY" ]; then
        GIT_CLEAN="true"
        GIT_STATUS="clean"
    else
        GIT_STATUS="dirty"
    fi
else
    GIT_STATUS="not_a_git_repo"
fi

# --- File Count ---
FILE_COUNT=0
case "$LANGUAGE" in
    javascript|typescript) FILE_COUNT=$(find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" 2>/dev/null | grep -v node_modules | grep -v dist | grep -v build | wc -l | tr -d ' ') ;;
    python) FILE_COUNT=$(find . -name "*.py" 2>/dev/null | grep -v __pycache__ | grep -v .venv | grep -v venv | wc -l | tr -d ' ') ;;
    go) FILE_COUNT=$(find . -name "*.go" 2>/dev/null | grep -v vendor | wc -l | tr -d ' ') ;;
    rust) FILE_COUNT=$(find . -name "*.rs" 2>/dev/null | grep -v target | wc -l | tr -d ' ') ;;
    java|kotlin) FILE_COUNT=$(find . -name "*.java" -o -name "*.kt" 2>/dev/null | grep -v build | grep -v target | wc -l | tr -d ' ') ;;
    ruby) FILE_COUNT=$(find . -name "*.rb" 2>/dev/null | grep -v vendor | wc -l | tr -d ' ') ;;
    php) FILE_COUNT=$(find . -name "*.php" 2>/dev/null | grep -v vendor | wc -l | tr -d ' ') ;;
    csharp) FILE_COUNT=$(find . -name "*.cs" 2>/dev/null | grep -v bin | grep -v obj | wc -l | tr -d ' ') ;;
esac

# --- Output JSON ---
cat <<EOF
{
  "language": "$LANGUAGE",
  "framework": "$FRAMEWORK",
  "test_runner": "$TEST_RUNNER",
  "test_command": "$TEST_COMMAND",
  "git_clean": $GIT_CLEAN,
  "git_status": "$GIT_STATUS",
  "git_branch": "$GIT_BRANCH",
  "source_file_count": $FILE_COUNT,
  "project_root": "$(pwd)"
}
EOF
