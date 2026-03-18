---
name: web-dev-brainstorm
description: |
  Comprehensive web development problem-solving, tech stack selection, and debugging skill for solo developers and APMs. Triggers on: (1) Tech stack decisions - "what framework", "React vs Vue", "which database", "best hosting", (2) Architecture - "how to structure", "folder organization", "project setup", (3) Debugging - "why isn't this working", "how to debug", "stuck on", "error with", (4) Performance - "slow app", "optimize", "improve speed", (5) Learning - "tutorial hell", "how to learn", "where to start", (6) Security - "is this secure", "authentication", "protect my app", (7) Database - "PostgreSQL vs", "Supabase vs Firebase", (8) State management - "Redux vs Zustand", "how to manage state", (9) Any web development brainstorming, decision-making, or problem-solving discussion.
---

# Web Development Problem-Solving Framework

## Reference Navigation

**Load the relevant reference file(s) BEFORE answering:**

| Question Type | Reference File |
|---------------|----------------|
| Stuck/debugging/errors | `references/problem-solving.md` |
| Framework/library choice | `references/frontend-guide.md` |
| Database/backend/hosting | `references/backend-guide.md` |
| Project structure/patterns | `references/architecture.md` |
| Auth/security/protection | `references/security.md` |
| Slow app/optimization | `references/performance.md` |
| Quick comparisons | `references/decision-matrices.md` |
| Building specific app type | `references/common-scenarios.md` |
| Best practices/what to avoid | `references/anti-patterns.md` |
| Learning/career/growth | `references/learning-strategies.md` |

## Core Philosophy

### The Golden Stack (Default Recommendation)
When user has no strong preferences, recommend:
- **Frontend**: Next.js 15+ (App Router) + TypeScript + Tailwind CSS
- **Backend**: Next.js API Routes / Server Actions
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **State**: TanStack Query (server) + Zustand (client, if needed)
- **Hosting**: Vercel
- **Cost**: $0-25/month for most projects

Only deviate when there's a specific, articulable reason.

### Decision Framework
```
1. What's the SIMPLEST solution that works?
2. What are the CONSTRAINTS? (budget, timeline, skills)
3. What's the MIGRATION PATH if this doesn't work?
```

## Response Templates

### For Tech Stack Questions
```
**Recommendation**: [Clear choice]
**Why**: [2-3 sentences]
**Get started**: [Concrete command/step]
**Consider alternatives if**: [Conditions]
```

### For Debugging Questions
```
**Likely cause**: [Most probable issue]
**Verify with**: [Diagnostic step]
**Fix**: [Concrete solution]
**If that doesn't work**: [Next thing to try]
```

### For "How to Build X" Questions
```
**Approach**:
1. [MVP phase]
2. [Core features]
3. [Polish]

**Stack**: [Recommendations]
**Start here**: [First step]
**Watch out for**: [Common pitfall]
```

## Anti-Patterns in Responses

❌ Decision paralysis ("it depends on many factors...")
❌ Enterprise solutions for solo projects
❌ Over-engineering ("you might need microservices later")
❌ Recommending deprecated technologies

✅ Clear recommendations with reasoning
✅ Optimize for shipping, not perfection
✅ Consider user's skill level
✅ Provide concrete next steps
