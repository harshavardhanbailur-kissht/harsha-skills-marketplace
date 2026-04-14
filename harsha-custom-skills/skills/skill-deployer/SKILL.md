---
name: skill-deployer
description: One-sweep deployment of a local Claude skill to Claude Code and Cowork. Takes a skill folder, installs it to ~/.claude/skills for Claude Code, and publishes it to a Claude plugin marketplace GitHub repo so Cowork picks it up on plugin reinstall. Use when the user wants to make an existing skill folder available in both Claude Code and Cowork in one go, package a skill as a marketplace plugin, or update a skill already published in their marketplace.
---

# Skill Deployer

**Turn any local skill folder into a live Claude Code + Cowork skill in one sweep.**

## When to Use

Invoke when the user says things like:
- "install this skill in claude code and cowork"
- "publish this skill to my marketplace"
- "add this skill to claude code and co work in one go"
- "deploy this skill everywhere"
- "update my marketplace with this new skill"

## What You Need From The User

Before running the script, collect three things (use `AskUserQuestion` if any are missing):

1. **Source skill folder** — absolute or `~`-relative path to a folder containing a `SKILL.md` at the root. Example: `~/Downloads/claude skills/ultimate-debugging-tool`.
2. **Marketplace repo URL** — the user's plugin marketplace on GitHub. Example: `https://github.com/user/my-skills-marketplace.git`. Skip the marketplace half if the user only wants Claude Code.
3. **Plugin folder name inside the marketplace** — most marketplaces look like `<repo>/<plugin-name>/skills/<skill-name>/`. Ask the user what their plugin sub-folder is called (e.g. `harsha-custom-skills`). If they don't know, `cd` into a fresh clone of the repo, inspect the top-level directories, and pick the one that contains `skills/` and `commands/` subfolders.

If the skill already exists in the marketplace under a different name (a stub, an older version), that stub will be removed and the new one replaces it. Ask the user if they want to archive or force-replace when that happens.

## Absolute Safety Boundaries

- **NEVER** force-push to the marketplace branch. Always commit and push via fast-forward.
- **NEVER** skip the Claude Code backup step — always archive the existing `~/.claude/skills/<skill-name>/` as `<skill-name>.bak.<timestamp>/` before overwriting.
- **NEVER** commit `__pycache__`, `.pytest_cache`, `pytest-cache-files-*`, `.DS_Store`, or `node_modules/` to the marketplace. The script excludes these; don't bypass the exclude list.
- **NEVER** commit secrets, `.env` files, or `.credentials.json` from the skill folder — if the source contains any, stop and warn the user.
- **NEVER** attempt the push from within a sandbox without credentials — if you're in Cowork, hand the generated installer script to the user and have them run it on their Mac (their credentials live there).

## Workflow

### Step 1 — Validate inputs

```bash
bash scripts/validate.sh <skill-path>
```

Checks: folder exists, `SKILL.md` present with a `name:` frontmatter field, no secrets, no obvious cache junk. If validation fails, surface the exact reason to the user — don't try to auto-fix.

### Step 2 — Deploy to Claude Code

```bash
bash scripts/deploy-claude-code.sh <skill-path>
```

This copies the skill into `~/.claude/skills/<skill-name>/`, archiving any existing folder with the same name. `<skill-name>` is read from the `name:` field in the source SKILL.md frontmatter.

### Step 3 — Deploy to marketplace (optional)

```bash
bash scripts/deploy-marketplace.sh <skill-path> <repo-url> <plugin-folder>
```

This clones the marketplace repo to a fresh `~/Downloads/<repo-name>-update-<timestamp>/`, drops the skill into `<plugin-folder>/skills/<skill-name>/`, generates a slash-command at `<plugin-folder>/commands/<skill-name>.md` from the skill's frontmatter description, bumps patch version in `marketplace.json` and `plugin.json` if they exist, commits with a descriptive message, and pushes to `origin/<default-branch>`.

### Step 4 — Cowork reinstall instructions

After the push succeeds, tell the user to refresh Cowork's plugin cache:

> Open Cowork → Settings → Plugins → `<marketplace name>` → **Update**.
> Or from the Cowork command bar: `/plugin` → pick marketplace → Update.

The new skill appears in Cowork's skill list as `<plugin-folder>:<skill-name>`.

### Step 5 — Verify

- Claude Code: quit and relaunch. `/` menu should now show `/<skill-name>` (if the marketplace step was run, or if a slash command was added manually to `~/.claude/commands/`).
- Cowork: in the skills autocomplete, typing `/` then the skill name should show it under the plugin namespace.

## Running From Inside Cowork

If you're Claude inside a Cowork sandbox, you cannot push to GitHub — the sandbox has no credentials. Instead:

1. Run validation from the sandbox (read-only checks are fine).
2. Write a combined installer script to `~/Projects/install-<skill-name>.sh` (Projects is writable for content).
3. Tell the user to run `bash ~/Projects/install-<skill-name>.sh` in Terminal on their Mac — it uses their existing git credentials.

See `scripts/generate-installer.sh` for the script generator.

## Scripts

| Script | Purpose |
|--------|---------|
| `validate.sh` | Pre-flight: folder exists, SKILL.md has `name:` frontmatter, no secrets, no cache junk |
| `deploy-claude-code.sh` | Archive existing + rsync skill into `~/.claude/skills/` |
| `deploy-marketplace.sh` | Clone repo, drop skill + command, bump versions, commit, push |
| `generate-installer.sh` | Emit a self-contained installer to `~/Projects/install-<skill>.sh` for users to run on their host when the agent is in a credentials-less sandbox |

## Anti-Patterns to Avoid

- **Force-overwriting Claude Code skills without a backup** — always archive first; users can lose days of customization otherwise
- **Pushing cache junk to the marketplace** — bloats the plugin and ships stale test data; excludes in rsync are mandatory
- **Silent version bumps** — always tell the user what you bumped from → to (marketplace.json AND plugin.json)
- **Copying a skill that references absolute paths to the user's machine** — skills must be portable; flag any `/Users/...` or `/home/...` string in SKILL.md or scripts
- **Deploying to both targets without confirming the skill works in one first** — Claude Code install is cheap to roll back; a bad marketplace commit is not
