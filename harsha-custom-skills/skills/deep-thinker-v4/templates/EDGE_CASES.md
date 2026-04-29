# EDGE_CASES: Stress Testing the Design

## Pre-Mortem Narratives
**Three failure stories with causal chains**

### Failure Story 1: Lock Contention Becomes New Bottleneck
**Narrative**:

We deploy the async lock to production. For three weeks, everything is smooth. Then during peak hours (4-6pm ET), we see a 10x latency spike on mutation endpoints (100ms → 1000ms+). The alert fires, and the on-call engineer starts investigating. They find that users performing bulk operations (delete 50 items, create 50 items in rapid succession) are all queued behind the lock. The first mutation takes 100ms, and because 500 users are doing the same thing, each subsequent mutation waits 500x + 100ms = 50s. Users report the UI is frozen.

**Causal chain**:
1. Lock is global (one lock for entire Store) instead of per-entity
2. Peak hours have 500 concurrent users, each doing bulk operations
3. Each operation acquires lock for 100ms
4. Queue builds: 500 × 100ms = 50s wait time per user
5. Users perceive frozen UI
6. Increased error rate as requests timeout

**Prevention**:
- Monitor lock queue depth and P99 latency in staging
- Use per-entity locks instead of global lock
- Implement lock timeout (fail fast if wait > 1s)
- Load test with 500+ concurrent users before deploy

---

### Failure Story 2: Virtualization Bug Breaks for Users with Screen Readers
**Narrative**:

We deploy the react-window virtualization to production. The UI is blazingly fast: rendering goes from 800ms to 80ms. We celebrate. A week later, support gets an email from an accessibility advocate: "Your app is completely broken for screen reader users. I can't navigate the list anymore." They're right. The virtualized list only renders visible items in the DOM. Screen readers can't see off-screen items, so they report "list has 10 items" instead of "5,000 items." A user with a vision impairment can't navigate the full dataset.

**Causal chain**:
1. react-window only renders visible items (optimization)
2. Hidden items aren't in the DOM
3. Screen reader (JAWS, NVDA) can't see hidden items
4. User can only navigate 15 visible items, not 5,000
5. User perception: app is broken, data is missing
6. Accessibility violation; potential legal liability

**Prevention**:
- Test with screen reader (free: NVDA on Windows, VoiceOver on Mac)
- Use aria-live regions to announce data changes
- Implement keyboard navigation alongside virtualization
- Add a text alternative: "List has 5,000 items; scroll to load more"

---

### Failure Story 3: Database Migration Deadlock During Rollout
**Narrative**:

We coordinate with DevOps to add a new index to the database schema for the v2 API. They schedule the migration for 2am ET (low traffic). The migration starts: `CREATE INDEX idx_entity_created_at ON entities(created_at);` The process takes 5 minutes. During those 5 minutes, a production deployment of a critical bug fix happens to roll out (uncoordinated). The new code tries to read from the table while the index lock is held. MySQL hits a deadlock: the migration holds a lock, the new query waits, the new query's transaction blocks other queries. Cascading failures. For 7 minutes, the app is partially unavailable. Customers complain.

**Causal chain**:
1. Migration and deployment weren't coordinated
2. Index creation holds a table lock in MySQL
3. Concurrent queries in new code try to read the table
4. Deadlock occurs
5. Transactions block; queries timeout
6. Cascading failures across dependent services
7. 7-minute outage

**Prevention**:
- Coordinate all schema changes with deployment schedule (no concurrent deploys)
- Use online schema change tools (Percona pt-online-schema-change) that don't lock
- Test migration in staging with realistic load first
- Have a rollback plan (drop index if issues arise)

---

## Constraint Verification

| Hard Constraint | Satisfied? | How Specifically |
|-----------------|-----------|------------------|
| Backwards compat with v1 API | YES | v1 endpoint unchanged; v2 is new path (/api/v2/export) |
| No PII in logs | YES | Store.mutate() doesn't log state; only error messages logged |
| Performance < 500ms | CONDITIONAL | Database: 50ms (no change). Rendering: 800ms → 80ms (passes). Total: ~130ms (PASS) |
| Concurrency safety | YES | Async lock serializes mutations; one at a time |
| Compliance (audit trail) | PARTIAL | Lock prevents concurrent mutations (audit-safe). No formal audit log yet; defer to future |

---

## Systematic Edge Sweep

| Dimension | Normal | Boundary | Adversarial |
|-----------|--------|----------|-------------|
| **INPUT: Entity count** | 100-5,000 | 0 items, 1 item, 1M items | Negative count? NaN? Null? |
| **INPUT: Mutation rate** | 1-10 mutations/sec | 100 mutations/sec, 0 mutations | 1,000 mutations/sec from bot |
| **INPUT: Payload size** | 1KB entity | 100MB entity | 1GB entity; corrupt JSON |
| **STATE: Lock queue** | 0-5 waiting | 100 waiting, lock timeout triggered | Deadlock (lock waits on itself) |
| **STATE: Memory** | 50MB (5k items) | 500MB (50k items) | 5GB (OOM killer invoked) |
| **TIMING: Response latency** | 50-200ms | 1000ms (timeout threshold) | Network partition (no response) |
| **TIMING: Browser GC pause** | 10-50ms | 200ms pause (jank visible) | Continuous GC thrashing |
| **EXTERNAL: Database down** | Normal operation | Timeout after 5s | Persistent 500 errors |
| **EXTERNAL: Cache miss** | Hit rate 80% | Hit rate 0% (cold cache) | Cache server down |

---

## The Single Biggest Risk
**Lock contention under peak load.**

If we get the lock granularity wrong (global instead of per-entity), or if peak traffic is higher than we modeled, the lock queue can become a bottleneck worse than the original bug. The fix (per-entity locks) is straightforward, but we must validate in staging with realistic load. Recommend load testing with 500+ concurrent users performing 10+ mutations/second before production deploy.

---

## Security Considerations

1. **Input Validation**: Validate all mutation payloads (type, size, content)
   - Reject entities > 1MB
   - Reject mutation rate > 100/sec per user (rate limit)
   - Sanitize rich text in entity.name (no XSS)

2. **State Serialization**: Store state in memory; never serialize to untrusted storage
   - Current: ✓ In-memory only
   - Future: If we add persistence, encrypt at rest

3. **API Versioning**: v1 locked; no schema changes until deprecation
   - External clients can trust v1 forever
   - v2 can evolve freely

4. **Concurrency & Atomicity**: Lock ensures mutations don't race
   - No two mutations run simultaneously
   - State is always consistent

---

## Accessibility Scenarios

1. **Screen Reader User**: Navigating a list of 5k items
   - Risk: Virtualization breaks screen reader
   - Mitigation: Add aria-live regions; implement keyboard navigation; test with NVDA/JAWS

2. **Motor Impairment**: User with tremor clicking rapidly
   - Risk: Rapid clicks trigger lock contention
   - Mitigation: Debounce UI handlers; show loading state; don't queue if already processing

3. **Colorblind User**: Relying on color alone to indicate state
   - Risk: Locked state shown only by color
   - Mitigation: Use color + icon + text labels (not color alone)

4. **Low Vision**: Relying on high contrast and zoom
   - Risk: Virtualized list may not render properly when zoomed
   - Mitigation: Test at 200% zoom; ensure font sizes are readable

---

## Next Phase
→ Proceed to **IMPLEMENTATION**: Step-by-step guide for building this.
