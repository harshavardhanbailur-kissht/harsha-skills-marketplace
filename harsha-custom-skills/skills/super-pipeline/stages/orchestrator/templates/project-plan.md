# Project Structure Template

Use this template for organizing project tasks into phases with clear status tracking, 
next actions, and blockers.

---

## Template

```markdown
# Project: [Project Name]

## Overview
[1-2 sentence description of the project]

**Appetite**: [Timeframe - e.g., 2 weeks]
**Status**: Phase [X] of [Y] | [N]/[M] tasks complete
**Last Updated**: [Date]

---

## Progress Summary

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| 1. [Phase Name] | ✅ Complete | X/X | 100% |
| 2. [Phase Name] | 🔄 In Progress | Y/Z | YY% |
| 3. [Phase Name] | ⏳ Not Started | 0/W | 0% |

---

## PHASE 1: [Phase Name] [STATUS]

### [Track Name] (if multiple tracks)
- [x] #1 [Task title] (Size)
- [x] #2 [Task title] (Size)
- [ ] #3 [Task title] (Size) ← CURRENT
- [ ] #4 [Task title] (Size) — BLOCKED BY: #3

### Checkpoint
- [ ] [Binary verification item]
- [ ] [Binary verification item]

---

## PHASE 2: [Phase Name] [STATUS]

### [Track A Name] (parallel)
- [ ] #5 [Task title] (Size)
- [ ] #6 [Task title] (Size)

### [Track B Name] (parallel)
- [ ] #7 [Task title] (Size)

### Checkpoint
- [ ] [Binary verification item]

---

## NEXT ACTIONS
*Tasks that can be started immediately*

1. **#[N]** [Task title] (Size, estimate)
   - [Brief context if helpful]
2. **#[M]** [Task title] (Size, estimate)

---

## BLOCKED
*Tasks waiting on dependencies*

| Task | Blocked By | Notes |
|------|------------|-------|
| #[X] [Title] | #[Y] | [Optional context] |
| #[Z] [Title] | External: [What] | [Expected resolution] |

---

## DISCOVERY
*Timeboxed research tasks*

- [ ] **SPIKE**: [Question] ([timebox])
  - Question: [What we need to learn]
  - Output: [Decision doc / PoC / "need more research"]
  - May spawn: [Potential tasks]

---

## DECISIONS
*Link to ADRs made during this project*

- [ADR-XXX: Title](link) - [Brief summary]
- [ADR-YYY: Title](link) - [Brief summary]

---

## RISKS & BLOCKERS

| Risk/Blocker | Impact | Mitigation | Owner |
|--------------|--------|------------|-------|
| [Description] | High/Med/Low | [Plan] | [Who] |

---

## NOTES
[Any additional context, lessons learned, or important information]
```

---

## Filled Example

```markdown
# Project: Task Management API

## Overview
REST API for task management with authentication, CRUD operations, and real-time updates.

**Appetite**: 2 weeks
**Status**: Phase 2 of 4 | 9/18 tasks complete
**Last Updated**: 2024-01-20

---

## Progress Summary

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| 1. Foundation | ✅ Complete | 4/4 | 100% |
| 2. Authentication | 🔄 In Progress | 5/5 | 100% |
| 3. Core CRUD | 🔄 In Progress | 0/4 | 0% |
| 4. Real-time | ⏳ Not Started | 0/3 | 0% |
| 5. Polish | ⏳ Not Started | 0/2 | 0% |

---

## PHASE 1: Foundation ✅ COMPLETE

- [x] #1 Initialize Express project with TypeScript (S, 1hr)
- [x] #2 Configure PostgreSQL with Prisma ORM (M, 2hr)
- [x] #3 Set up Jest testing framework (S, 1hr)
- [x] #4 Create CI pipeline with GitHub Actions (M, 2hr)

### Checkpoint ✅
- [x] `npm install && npm run dev` starts server
- [x] `npm test` runs without errors
- [x] CI pipeline triggers on push

---

## PHASE 2: Authentication ✅ COMPLETE

- [x] #5 Design User schema and migrations (S, 1hr)
- [x] #6 Implement registration endpoint (M, 3hr)
- [x] #7 Implement login with JWT (M, 3hr)
- [x] #8 Add auth middleware for protected routes (S, 2hr)
- [x] #9 Write auth integration tests (M, 2hr)

### Checkpoint ✅
- [x] Can register new user via API
- [x] Can login and receive JWT
- [x] Protected routes return 401 without token

---

## PHASE 3: Core CRUD 🔄 IN PROGRESS

### Data Models
- [ ] #10 Design Project and Task schemas (M, 2hr) ← CURRENT
- [ ] #11 Add task status enum and transitions (S, 1hr) — BLOCKED BY: #10

### API Endpoints (parallel after #10)
- [ ] #12 Implement Project CRUD endpoints (M, 4hr) — BLOCKED BY: #10
- [ ] #13 Implement Task CRUD endpoints (L, 6hr) — BLOCKED BY: #10
- [ ] #14 Add task filtering and pagination (M, 3hr) — BLOCKED BY: #13

### Checkpoint
- [ ] Projects can be created, read, updated, deleted
- [ ] Tasks can be created within projects
- [ ] Task filtering by status works

---

## PHASE 4: Real-time ⏳ NOT STARTED

- [ ] **SPIKE**: Evaluate Socket.io vs native WebSocket (2hr timebox)
  - Question: Which WebSocket approach for real-time task updates?
  - May spawn: WebSocket implementation task
- [ ] #15 Implement WebSocket connection handling (M, 3hr) — BLOCKED BY: SPIKE
- [ ] #16 Broadcast task changes to connected clients (M, 3hr) — BLOCKED BY: #15

### Checkpoint
- [ ] WebSocket connection established from client
- [ ] Task updates broadcast to all connected clients

---

## PHASE 5: Polish ⏳ NOT STARTED

- [ ] #17 Generate OpenAPI documentation (M, 2hr)
- [ ] #18 Performance test with 100 concurrent users (M, 3hr)

### Checkpoint
- [ ] API documentation accessible at /docs
- [ ] Performance baseline documented

---

## NEXT ACTIONS

1. **#10** Design Project and Task schemas (M, 2hr)
   - Need to decide on task status values - see Slack thread
   - Reference User schema pattern from #5

---

## BLOCKED

| Task | Blocked By | Notes |
|------|------------|-------|
| #11 Task status enum | #10 Schema design | Waiting on status values decision |
| #12 Project CRUD | #10 Schema design | Ready once schema done |
| #13 Task CRUD | #10 Schema design | Ready once schema done |
| #14 Task filtering | #13 Task CRUD | Needs basic CRUD first |
| #15 WebSocket impl | SPIKE | Need SPIKE result first |

---

## DISCOVERY

- [ ] **SPIKE**: Evaluate Socket.io vs native WebSocket (2hr timebox)
  - Question: Which approach for real-time task updates?
  - Criteria: Bundle size, browser support, ease of implementation
  - Output: Decision doc with recommendation
  - May spawn: Implementation task with chosen approach

---

## DECISIONS

- [ADR-001: PostgreSQL for database](docs/decisions/0001-postgresql.md) - Chosen for JSON support and Prisma compatibility
- [ADR-002: JWT for authentication](docs/decisions/0002-jwt-auth.md) - Stateless auth for horizontal scaling
- ADR-003: Task status values - PENDING (need input from PM)

---

## RISKS & BLOCKERS

| Risk/Blocker | Impact | Mitigation | Owner |
|--------------|--------|------------|-------|
| Task status values undefined | Medium | Meeting scheduled with PM Monday | Sarah |
| WebSocket approach unclear | Low | SPIKE scheduled for Phase 4 | Mike |

---

## NOTES

- Frontend team expects API ready by end of week 2
- Consider adding soft deletes for tasks (future enhancement)
- Performance baseline should include realistic data volume (~1000 tasks)
```

---

## Structure Guidelines

### Phase Organization
- 3-5 phases typical for 2-week project
- Each phase has clear outcome/checkpoint
- Phases are sequential; tracks within phases can be parallel

### Task Notation
- `[x]` = Complete
- `[ ]` = Not started or in progress
- `← CURRENT` = Currently being worked on
- `— BLOCKED BY: #X` = Waiting on dependency
- `(S/M/L)` = Size estimate

### Checkpoints
- Binary items only (yes/no verifiable)
- 3-5 items per phase
- Verify before moving to next phase

### Discovery Section
- All research/spike tasks
- Explicit timeboxes
- Clear output requirements

### Keep Updated
- Update status markers as work progresses
- Move completed tasks to [x]
- Update NEXT ACTIONS daily
- Reflect decisions in DECISIONS section
