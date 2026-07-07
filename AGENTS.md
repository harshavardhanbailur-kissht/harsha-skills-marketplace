# Agent & contributor rules for this Claude plugin marketplace

## ⛔ Do NOT add `version` fields to plugin manifests — the omission is intentional

The manifests in this repo **deliberately have no `version` field**:
- `.claude-plugin/marketplace.json` — no top-level `version`, and **no `version` inside any `plugins[]` entry**
- every `*/.claude-plugin/plugin.json` — no `version`

### Why (do not "fix" this)
When a plugin or marketplace declares a `version`, Claude Code and Cowork **cache that
version string and refuse to pull new commits until the string changes.** That forced a
manual "bump version → remove plugin → re-add plugin" dance on every edit, and caused
stale-plugin glitches. With no `version`, **the git commit SHA is the version**, so every
push is automatically a new release and all clients update with no remove/re-add.

### Rules for any agent or human editing this repo
- ❌ Do NOT reintroduce a `version` key in `.claude-plugin/marketplace.json` (neither
  top-level nor inside a `plugins[]` entry).
- ❌ Do NOT reintroduce a `version` key in any `plugin.json`.
- ❌ Do NOT add cache-buster hacks (e.g. a static `buildId`) — they re-pin the cache the
  same way a `version` does and defeat SHA-based versioning.
- ❌ Do NOT pin plugin `source` entries to a specific `sha` / `tag` / `ref`. Keep `source`
  as a relative path (or otherwise unpinned) so updates flow.
- ✅ To ship a change: just commit and push. That push **is** the release.

If you believe a `version` is genuinely required, STOP and ask the repo owner
(Harshavardhan Bailur) first — do not add it unilaterally.
