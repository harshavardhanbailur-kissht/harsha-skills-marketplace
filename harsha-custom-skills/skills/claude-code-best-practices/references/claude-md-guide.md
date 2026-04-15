# CLAUDE.md Configuration Guide

Comprehensive guide to CLAUDE.md — Claude Code's persistent memory and configuration system.

## Table of Contents
1. What Goes in CLAUDE.md
2. Size Guidelines
3. Loading Behavior
4. Monorepo Strategy
5. @import System
6. .claude/rules/ Directory
7. CLAUDE.local.md
8. Configuration Template

---

## 1. What Goes in CLAUDE.md

CLAUDE.md is advisory context, not deterministic rules. Structure it as knowledge Claude should always have:

**Include:**
- Project context: One-liner orientation ("This is a Next.js e-commerce app with Stripe integration")
- Code style: Formatting preferences, naming conventions, architectural patterns
- Commands: Exact build/test/lint/deploy commands (`npm run test`, `cargo build --release`)
- Decisions: Why the team chose X over Y (prevents Claude from suggesting Y)
- Common mistakes: "Never use `any` type in TypeScript files" with reasoning

**Exclude:**
- Secrets, API keys, or credentials (use environment variables)
- Redundant information already in package.json, tsconfig, etc.
- Overly specific rules that belong in linting config
- Temporary notes (use CLAUDE.local.md)

---

## 2. Size Guidelines

| Source | Recommendation | Context |
|---|---|---|
| Official docs | Under 200 lines | "Keep files concise — longer files consume more context" |
| HumanLayer | ~60 lines | "Frontier thinking models attend to ~150-200 instructions" |
| Community consensus | Under 300 lines | Frontier LLMs handle ~150-200 instructions consistently |
| Boris Cherny | Keep lean | "Ruthlessly prune; treat as living document" |

**What happens when too long:**
- Claude consumes more context tokens per session
- Adherence to individual rules degrades
- Important instructions get lost in noise
- Cost increases with every API call

**Recommended approach:** Start at 50-100 lines covering the essentials. Add rules only when you observe Claude making the same mistake twice. Review and prune monthly.

---

## 3. Loading Behavior

### Ancestor Loading (UP the Directory Tree)

At session startup, Claude walks UP from the current working directory to the filesystem root, loading every CLAUDE.md it finds:

```
/home/user/myproject/packages/frontend/  ← working directory
/home/user/myproject/packages/CLAUDE.md  ← loaded (ancestor)
/home/user/myproject/CLAUDE.md           ← loaded (ancestor)
```

This happens immediately at startup.

### Descendant Loading (DOWN, Lazy)

CLAUDE.md files in subdirectories load ON DEMAND when Claude reads or edits files in those directories:

```
/myproject/
├── CLAUDE.md                    ← Always loaded (ancestor)
├── frontend/
│   ├── CLAUDE.md               ← Loaded when editing frontend/ files
│   └── src/App.tsx
├── backend/
│   ├── CLAUDE.md               ← Loaded when editing backend/ files
│   └── src/server.ts
└── api/
    ├── CLAUDE.md               ← Loaded when editing api/ files
    └── src/routes.ts
```

**Siblings never load:** Editing `frontend/` files does NOT trigger `backend/CLAUDE.md`. Each directory's CLAUDE.md is independent.

---

## 4. Monorepo Strategy

For monorepos, use hierarchical CLAUDE.md files:

**Root CLAUDE.md (~50-100 lines):**
```markdown
# Project: MyApp Monorepo

This is a TypeScript monorepo using pnpm workspaces.

## Build & Test
- `pnpm install` — Install dependencies
- `pnpm build` — Build all packages
- `pnpm test` — Run all tests
- `pnpm lint` — Run ESLint + Prettier

## Coding Standards
- Use TypeScript strict mode everywhere
- Prefer functional components with hooks
- All API responses use the shared `ApiResponse<T>` type from @myapp/types
- Never commit to main directly — always use feature branches

## Architecture
- packages/frontend — Next.js 14 app
- packages/backend — Express API server
- packages/shared — Shared types and utilities
```

**Package-specific CLAUDE.md (~30-60 lines):**
```markdown
# Frontend Package (Next.js 14)

## Framework Patterns
- Use App Router (not Pages Router)
- Server Components by default; add 'use client' only when needed
- Data fetching via server actions, not client-side API calls

## Testing
- `pnpm test:frontend` — Jest + React Testing Library
- Test files colocated: `Component.test.tsx` next to `Component.tsx`

## State Management
- Server state: React Query
- Client state: Zustand (not Redux)
```

---

## 5. @import System

CLAUDE.md files can import additional files:

```markdown
@.claude/rules/typescript-conventions.md
@.claude/rules/api-design.md
@docs/architecture-decisions.md
```

**Rules:**
- Both relative and absolute paths work
- Relative paths resolve from the file containing the import (not working directory)
- Maximum import depth: 5 hops (prevents circular imports)
- First-time imports show an approval dialog listing files
- Imported files can recursively import other files

**When to use imports vs inline:**
- Import when content is shared across multiple CLAUDE.md files
- Import when content exceeds ~50 lines (keeps CLAUDE.md scannable)
- Keep inline when content is short and specific to this directory

---

## 6. .claude/rules/ Directory

All markdown files in `.claude/rules/` auto-load with the same priority as CLAUDE.md:

```
.claude/
├── rules/
│   ├── typescript.md     ← Auto-loaded
│   ├── testing.md        ← Auto-loaded
│   ├── api-design.md     ← Auto-loaded
│   └── security.md       ← Auto-loaded
└── settings.json
```

**Advantages over @imports:**
- No explicit import statements needed
- Files auto-discovered
- Easier to manage modularly
- Good for team-maintained rule sets

**File scoping with frontmatter:**
```yaml
---
paths:
  - "src/api/**"
  - "src/routes/**"
---
# API Design Rules
Only apply these rules when working with API files.
```

Rules with `paths` only load when Claude works on matching files, reducing context noise.

---

## 7. CLAUDE.local.md

Personal project-specific preferences. Automatically:
- Added to `.gitignore`
- Loaded alongside CLAUDE.md
- NOT shared with team

**Use for:**
- Personal sandbox URLs
- Preferred test data
- Local development environment specifics
- Temporary experimental rules

```markdown
# My Local Preferences

## Dev Environment
- Use port 3001 (3000 is taken by another project)
- My test user: harsha@test.local

## Current Focus
- Working on the auth refactor — always check auth/ first
```

---

## 8. Configuration Template

Minimal starting template:

```markdown
# [Project Name]

[One sentence describing what this project is and its tech stack.]

## Build & Test
- `[install command]`
- `[build command]`
- `[test command]`
- `[lint command]`

## Coding Standards
- [2-3 most important conventions]
- [Framework-specific pattern to follow]
- [Pattern to avoid and why]

## Architecture
- [Brief description of directory structure]
- [Key architectural decisions]
```

Keep it under 50 lines to start. Add rules only when Claude makes the same mistake twice. Prune monthly.
