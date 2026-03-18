# Developer Changelog Template

## Usage
Technical changelog for developers. Focuses on code areas, API changes, and implementation details.

---

# Release Notes: [PROJECT] [VERSION] — Developer Changelog

**Release Date**: [RELEASE_DATE]
**Services Affected**: [SERVICE_LIST]
**Total Changes**: [COUNT] ([BUGS] fixes, [STORIES] features)

---

## Technical Summary

[1-2 sentence overview of what services/modules were touched and why]

---

## Changes by Module

### [MODULE_NAME / FEATURE_CATEGORY]

#### [TICKET_KEY]: [SUMMARY]
- **Type**: [Bug / Story / Sub-task]
- **Priority**: [Highest / High / Medium / Low]
- **Assignee**: [NAME]
- **Contributors**: [NAMES]
- **Code Area**: [Service/module/component path]
- **Change Description**: [What was changed technically]
- **Root Cause** (bugs only): [What caused the issue]
- **Jira**: [LINK]

---

[Repeat per ticket, grouped by module]

---

## Breaking Changes

| Change | Affected Area | Migration Required |
|--------|-------------|-------------------|
| [Change] | [Area] | [Yes/No — details] |

---

## API Changes

| Endpoint | Method | Change Type | Description |
|----------|--------|-----------|-------------|
| [path] | [GET/POST/PUT] | [New/Modified/Deprecated] | [What changed] |

---

## Data Model Changes

| Table/Entity | Column/Field | Change | Migration |
|-------------|-------------|--------|-----------|
| [entity] | [field] | [Added/Modified/Removed] | [migration notes] |

---

## Configuration Changes

| Config | Old Value | New Value | Service |
|--------|----------|-----------|---------|
| [key] | [old] | [new] | [service] |

---

## Technical Debt

| Item | Ticket | Severity | Notes |
|------|--------|----------|-------|
| [Workaround] | [KEY] | [H/M/L] | [What needs cleanup] |

---

## Contributor Summary

| Developer | Tickets | Primary Areas |
|-----------|---------|-------------|
| [Name] | [Count] | [Modules] |

---

## Dependency Updates

| Package | From | To | Reason |
|---------|------|-----|--------|
| [package] | [v1] | [v2] | [reason] |
