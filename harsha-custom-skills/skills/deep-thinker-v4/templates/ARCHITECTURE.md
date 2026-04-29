# ARCHITECTURE: Design Approaches & Selected Solution

## The Three Approaches

### THE OBVIOUS: Fix Store Concurrency With a Mutex Lock Pattern
**What it is**: Add a lock mechanism to the Store class. Serialize all mutations through a queue enforced by an async lock.

**FOR**:
- Requires minimal changes to existing code
- Proven pattern (same as Redux thunk middleware)
- Easy to understand and debug
- No schema changes needed

**AGAINST**:
- Doesn't solve the underlying performance issue (Store was never designed for 5k-item lists)
- Lock contention under high concurrency becomes a bottleneck
- Doesn't address the hidden integrations (still need API versioning)
- Developers won't learn the concurrency model; bugs will recur

**Confidence**: MEDIUM — solves the stated bug but not the real problem

**Would fail if**:
- We add real-time collaboration (Figma-style cursors)
- User performs 100+ mutations/second
- We scale to hundreds of concurrent users

---

### THE CONTRARIAN: Rearchitect to Event Sourcing + CQRS
**What it is**: Flip the architecture. Commands (mutations) are immutable events. State is reconstructed from event history. Queries read from a separate materialized view.

**FOR**:
- Naturally handles concurrency (events are append-only)
- Enables audit trail for free (every change is logged)
- Supports time travel and undo/redo easily
- Can replay events to debug production issues
- Scales to thousands of concurrent mutations

**AGAINST**:
- Massive rewrite; 3-4 weeks of engineering
- Introduces eventual consistency (state not immediately visible)
- Requires event store (new infrastructure)
- Very high complexity for team unfamiliar with event sourcing
- Overkill for current scale (5k items is small)

**Confidence**: HIGH (proven pattern) but MEDIUM (risk: implementation complexity)

**Would fail if**:
- We need strict consistency (financial transactions)
- Latency must be < 10ms (event replay adds latency)
- Team lacks event sourcing experience (learning curve killer)

---

### THE MINIMUM: Accept Current Limitation; Optimize Frontend Rendering
**What it is**: Don't fix the concurrency bug in Store. Accept that rapid mutations (within 50ms) may lose intermediate state. Instead, solve the real bottleneck: frontend rendering of 5k items.

**FOR**:
- Minimal code changes (add virtualization library)
- Addresses the actual performance problem (400-800ms render time)
- 1-2 days of work
- Concurrency bug is rare in real user behavior (most users don't fire 2 mutations in 50ms)
- Users perceive faster app instantly

**AGAINST**:
- Leaves a known bug unfixed; bad for future maintainers
- Doesn't scale if we add real-time features later
- Business may view as "punting" the problem
- Won't help if heavy users discover the bug

**Confidence**: HIGH (low risk, high impact) × MEDIUM (feels incomplete)

**Would fail if**:
- Users do rapid bulk operations (multi-select delete + create)
- We add collaborative features requiring consistent state
- Bug bites us in production during peak usage

---

## Selected: The Obvious + Minimum Hybrid
**Why**: The OBVIOUS addresses the bug cleanly; the MINIMUM solves the real performance problem. Combined, they're high-confidence and deliver measurable value in 2 weeks.

**What was rejected and why**:
- **Event Sourcing**: Rejected because it's 3-4x the effort for the current scale. Revisit in 6 months if real-time collaboration becomes a requirement.
- **Pure Minimum**: Rejected because we should fix the known bug; leaving it breeds technical debt and surprises future developers.

---

## Component Structure
```
src/
├── state/
│   ├── Store.ts           (modified: add async lock)
│   ├── types.ts
│   └── __tests__/
├── ui/
│   ├── Dashboard.jsx      (modified: add react-window for virtualization)
│   ├── VirtualList.jsx    (new: wrapper component)
│   └── Icon.jsx
├── api/
│   ├── v1.ts              (existing: keep as-is)
│   └── v2.ts              (new: versioned schema for new clients)
├── models/
│   └── Entity.ts          (unchanged)
└── __tests__/
    ├── Store.concurrency.test.ts (new: regression suite)
    └── Dashboard.render.test.ts  (new: performance benchmarks)
```

---

## Data Model
**No changes to Entity or core types.**

```typescript
// Existing: unchanged
interface Entity {
  id: string;
  name: string;
  created_at: ISO8601;
  updated_at: ISO8601;
}

// API v1 (deprecated): existing clients
interface ExportResponseV1 {
  entities: Entity[];
  count: number;
}

// API v2 (new): forward-compatible
interface ExportResponseV2 {
  entities: Entity[];
  count: number;
  cursor?: string;           // pagination
  page_size: number;
  _version: "2.0.0";         // schema version tag
}
```

---

## State Design

### Store Mutation Locking (New)
```typescript
class Store<State> {
  private lock: AsyncLock = new AsyncLock();

  async mutate(fn: (state: State) => State): Promise<State> {
    return this.lock.acquire('mutation', async () => {
      // Only one mutation runs at a time
      this.state = fn(this.state);
      return this.state;
    });
  }
}
```

### UI Rendering with Virtualization (New)
```typescript
// Use react-window to render only visible items
<VirtualList
  items={items}                 // all 5k items in memory
  height={600}
  itemSize={50}
  renderItem={(item, index) => <ListItem key={item.id} item={item} />}
/>
```

---

## API Design

### Versioning Strategy
- **v1**: Existing schema (backwards compatible, no changes)
- **v2**: New schema with pagination support; available at `/api/v2/export`
- **Migration**: Notify external clients (Salesforce, mobile) of v2 availability; give 6-month notice before deprecating v1

### Headers for Version Negotiation
```
GET /api/export
Accept-Version: 2.0.0
```

---

## Integration Points

1. **With Salesforce Integration** (`undocumented-client-1`)
   - Currently calls `/api/v1/export`
   - No changes needed (v1 stays stable)
   - Notify team of v2 when ready

2. **With Legacy Mobile App** (`undocumented-client-2`)
   - Currently calls `/api/v1/export`
   - Same: v1 stays stable

3. **With Third-Party Dashboard** (`undocumented-client-3`)
   - Currently calls `/api/v1/export`
   - Same: v1 stays stable

---

## Migration Strategy

### Phase 1: Prepare (1 week)
- Add async lock to Store
- Add performance tests for rendering
- Create `/api/v2/export` endpoint (parallel to v1)

### Phase 2: Deploy (1 day)
- Deploy to staging with v2 endpoint enabled
- Run 24h smoke tests
- Canary deploy to 10% of production

### Phase 3: Monitor (2 weeks)
- Watch for Store lock contention (shouldn't happen)
- Monitor rendering performance (should see 400ms → 100ms improvement)
- External clients unaware; no action needed

### Phase 4: Deprecate (6 months later)
- Send formal deprecation notice to v1 clients
- Give 90-day notice before removal

---

## Next Phase
→ Proceed to **EDGE_CASES**: What could go wrong during execution?
