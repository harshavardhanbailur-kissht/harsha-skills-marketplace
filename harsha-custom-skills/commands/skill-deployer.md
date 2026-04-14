---
description: One-sweep deployment of a local Claude skill to Claude Code and Cowork. Takes a skill folder, installs it to ~/.claude/skills for Claude Code, and publishes it to a Claude plugin marketplace GitHub repo so Cowork picks it up on plugin reinstall.
argument-hint: "<skill-folder> [<repo-url> <plugin-folder>]"
---

# /skill-deployer

One-sweep deployment of a local Claude skill to Claude Code and Cowork. Takes a skill folder, installs it to `~/.claude/skills` for Claude Code, and publishes it to a Claude plugin marketplace GitHub repo so Cowork picks it up on plugin reinstall.

## Invocation

```
/skill-deployer <skill-folder> <repo-url> <plugin-folder>
```

Example:

```
/skill-deployer ~/Downloads/claude\ skills/my-new-skill \
    https://github.com/user/my-marketplace.git \
    my-plugin-folder
```

## Workflow

Load the `skill-deployer` skill and follow its SKILL.md workflow:

1. Validate the source skill folder (SKILL.md present, no secrets, no cache junk).
2. Archive any existing `~/.claude/skills/<name>/` and install the new one.
3. Clone the marketplace repo, drop the skill into `<plugin-folder>/skills/<name>/`, generate a slash command, bump patch versions in `marketplace.json` and `plugin.json`, commit, and push.
4. Tell the user to reinstall the marketplace plugin in Cowork to refresh the cache.

If running inside a credentials-less sandbox (Cowork), the skill generates `~/Projects/install-<name>.sh` for you to run in Terminal on your Mac instead of pushing directly.
