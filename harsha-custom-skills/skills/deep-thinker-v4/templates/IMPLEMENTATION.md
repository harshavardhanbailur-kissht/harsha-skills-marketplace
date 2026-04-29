# IMPLEMENTATION: Step-by-Step Execution Plan

## Step-by-Step Guide

### Step 1: Add Async Lock Library
**Location**: `package.json`

**What to do**: Install async-lock dependency

**Code approach**:
```json
{
  "dependencies": {
    "async-lock": "^1.4.0"
  }
}
```

**Micro-details**:
- Version 1.4.0 is stable, no breaking changes expected
- Library is 8.5KB; adds <1% to bundle

**Watch out for**:
- Package name is "async-lock" (not "asynclock")
- Run `npm install` after modifying package.json

**Verification**: `npm ls async-lock` returns 1.4.0

---

### Step 2: Refactor Store to Use Lock
**Location**: `src/state/Store.ts`

**Dependencies**: After Step 1 (async-lock must be installed)

**What to do**: Wrap all mutations in an async lock

**Code approach**:
```typescript
import AsyncLock from 'async-lock';

class Store<State> {
  private lock = new AsyncLock();
  private state: State;

  async mutate(fn: (state: State) => State): Promise<State> {
    return this.lock.acquire('state', async () => {
      this.state = fn(this.state);
      this.notifySubscribers();
      return this.state;
    });
  }

  // Keep subscribe/unsubscribe unchanged
  subscribe(listener: (state: State) => void): () => void {
    // existing implementation
  }
}
```

**Micro-details**:
- Lock key is 'state' (only one global lock for now; may refactor per-entity later)
- `acquire()` waits if another mutation is running
- `notifySubscribers()` is called after mutation (existing method, don't change signature)

**Watch out for**:
- All mutate() calls must now be `await`ed (breaking change for callers)
- Old code using `store.mutate(fn)` without await will fail
- Need to update all call sites (Step 5)

**Verification**:
```bash
npm test -- src/state/Store.test.ts
# Should pass; no behavior change for single mutations
```

---

### Step 3: Create Concurrency Regression Tests
**Location**: `src/state/__tests__/Store.concurrency.test.ts` (new file)

**Dependencies**: After Step 2 (modified Store exists)

**What to do**: Add tests to verify lock prevents race conditions

**Code approach**:
```typescript
import Store from '../Store';

describe('Store concurrency', () => {
  it('serializes concurrent mutations', async () => {
    const store = new Store({ count: 0 });
    const results: number[] = [];

    // Fire 5 mutations concurrently
    await Promise.all([
      store.mutate(s => { results.push(1); return { count: s.count + 1 }; }),
      store.mutate(s => { results.push(2); return { count: s.count + 1 }; }),
      store.mutate(s => { results.push(3); return { count: s.count + 1 }; }),
      store.mutate(s => { results.push(4); return { count: s.count + 1 }; }),
      store.mutate(s => { results.push(5); return { count: s.count + 1 }; }),
    ]);

    // All 5 mutations should complete
    expect(store.getState().count).toBe(5);
    // Results should be in order (no interleaving)
    expect(results).toEqual([1, 2, 3, 4, 5]);
  });
});
```

**Micro-details**:
- Tests use async/await syntax
- `Promise.all()` fires all mutations concurrently
- Lock should serialize them; results array proves no interleaving

**Watch out for**:
- This test will fail if the lock doesn't work (catch regressions)
- Timing is non-deterministic; use results array to verify, not execution order

**Verification**:
```bash
npm test -- Store.concurrency.test.ts
# Should pass
```

---

### Step 4: Install Virtualization Library & Update Dashboard
**Location**: `src/ui/Dashboard.jsx`

**Dependencies**: After Step 3 (Store is tested and working)

**What to do**:
1. Install react-window: `npm install react-window`
2. Replace the simple list renderer with VirtualList

**Code approach**:
```typescript
import { FixedSizeList } from 'react-window';

// Old (non-virtualized):
export function Dashboard({ items }) {
  return (
    <div>
      {items.map(item => <ListItem key={item.id} item={item} />)}
    </div>
  );
}

// New (virtualized):
export function Dashboard({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

**Micro-details**:
- `FixedSizeList` only renders visible items (50px height × visible rows)
- `style` prop is required; passed by react-window
- `itemSize={50}` must match actual CSS height of ListItem

**Watch out for**:
- If ListItem height ≠ 50px, rendering will have gaps
- Scrolling may feel janky if itemCount is huge; that's expected (still faster than rendering all)
- `width="100%"` assumes parent has a fixed width; adjust if needed

**Verification**:
```bash
npm test -- Dashboard.test.ts
# Should pass; visual check: scrolling is smooth even with 5k items
```

---

### Step 5: Update All Store.mutate() Call Sites
**Location**: `src/` (all files using store.mutate)

**Dependencies**: After Step 2 (mutate now returns Promise)

**What to do**: Add `await` to all `store.mutate()` calls

**Code approach**:
```typescript
// Old:
store.mutate(s => ({ ...s, count: s.count + 1 }));

// New:
await store.mutate(s => ({ ...s, count: s.count + 1 }));
```

**Micro-details**:
- Use grep to find all: `grep -r "store.mutate" src/ | grep -v "await"`
- Update in handlers, event listeners, side effects
- Make sure calling function is `async`

**Watch out for**:
- Forgetting to add `async` to function signature breaks await
- Old tests will fail if not updated
- Some code may be in try-catch blocks; add await inside try

**Verification**:
```bash
npm test
# All tests should pass
grep -r "store.mutate" src/ | grep -v "await"
# Should return 0 results (no un-awaited calls)
```

---

### Step 6: Create VirtualList Component (Optional Polish)
**Location**: `src/ui/VirtualList.jsx` (new file)

**Dependencies**: After Step 4 (react-window is installed)

**What to do**: Wrap FixedSizeList with accessibility enhancements

**Code approach**:
```typescript
import { FixedSizeList } from 'react-window';

export function VirtualList({ items, renderItem, itemSize = 50, height = 600 }) {
  const Row = ({ index, style }) => (
    <div style={style} role="option" aria-selected={false}>
      {renderItem(items[index], index)}
    </div>
  );

  return (
    <div role="listbox" aria-label={`List of ${items.length} items`}>
      <FixedSizeList
        height={height}
        itemCount={items.length}
        itemSize={itemSize}
        width="100%"
      >
        {Row}
      </FixedSizeList>
    </div>
  );
}
```

**Micro-details**:
- Adds ARIA roles for screen readers
- Exposes itemSize as prop (allows Dashboard to configure)
- `aria-label` announces total item count

**Watch out for**:
- Role="listbox" is for select-style lists; use role="list" if a navigation list
- Screen readers may not announce all items (virtual limitation); add hint text

**Verification**:
```bash
npm test -- VirtualList.test.ts
# Should pass
# Manual: test with NVDA (Windows) or VoiceOver (Mac)
```

---

### Step 7: Create API v2 Endpoint
**Location**: `src/api/v2.ts` (new file)

**Dependencies**: After Step 5 (no breaking changes to existing API)

**What to do**: Create a parallel endpoint with pagination support

**Code approach**:
```typescript
import express from 'express';
import { db } from '../db';

const router = express.Router();

router.get('/export', async (req, res) => {
  const page_size = parseInt(req.query.page_size || '100');
  const cursor = req.query.cursor || null;

  const limit = Math.min(page_size, 1000); // Cap at 1000
  const query = db.entities
    .orderBy('created_at')
    .limit(limit);

  if (cursor) {
    query.where('created_at', '>', cursor);
  }

  const entities = await query.select();
  const next_cursor = entities.length === limit ? entities[entities.length - 1].created_at : null;

  res.json({
    entities,
    count: entities.length,
    cursor: next_cursor,
    page_size: limit,
    _version: '2.0.0',
  });
});

export default router;
```

**Micro-details**:
- v2 is at `/api/v2/export` (distinct from v1 at `/api/v1/export`)
- Pagination uses cursor (not offset) for scalability
- `_version` tag allows clients to detect schema version

**Watch out for**:
- Cursor logic must be consistent (order by same field)
- Limit capped at 1000 to prevent abuse
- v1 endpoint remains completely unchanged

**Verification**:
```bash
npm test -- api/v2.test.ts
# Should pass
curl http://localhost:3000/api/v2/export?page_size=50
# Should return JSON with 50 entities and cursor
```

---

### Step 8: Update Server Entry Point
**Location**: `src/server.ts`

**Dependencies**: After Step 7 (v2 endpoint exists)

**What to do**: Register v2 router alongside v1

**Code approach**:
```typescript
import express from 'express';
import apiV1 from './api/v1';
import apiV2 from './api/v2';

const app = express();

app.use('/api/v1', apiV1);
app.use('/api/v2', apiV2);  // New

app.listen(3000, () => console.log('Server running on :3000'));
```

**Micro-details**:
- v1 and v2 coexist; no migration needed
- Both are live simultaneously
- External clients can migrate at their own pace

**Watch out for**:
- Ensure both routers are exported correctly
- Test that v1 still works (regression test)

**Verification**:
```bash
npm start
curl http://localhost:3000/api/v1/export
# Should return old schema
curl http://localhost:3000/api/v2/export
# Should return new schema with pagination
```

---

## Dependencies Between Steps (Explicit)

```
Step 1 (Install async-lock)
  ↓
Step 2 (Refactor Store) ← must await after this
  ↓
Step 3 (Concurrency tests) ← validates Step 2
  ↓
Step 5 (Update call sites) ← depends on Step 2, tested by Step 3
  ↓
Step 4 (Virtualization) ← independent; can happen in parallel with Steps 2-5
  ↓
Step 6 (VirtualList wrapper) ← optional; improves accessibility of Step 4
  ↓
Step 7 (API v2) ← independent; can happen in parallel
  ↓
Step 8 (Register v2) ← depends on Step 7
```

**Critical path** (must be sequential): 1 → 2 → 5 → Done
**Parallel work**: 4, 6, 7 can happen simultaneously while 2-5 are in progress

---

## File Changes Summary

| File | Type | Change | Risk | Testing |
|------|------|--------|------|---------|
| `package.json` | Modify | Add async-lock | Low | npm test |
| `src/state/Store.ts` | Modify | Add lock to mutate() | Medium | Store.test.ts, concurrency.test.ts |
| `src/state/__tests__/Store.concurrency.test.ts` | Create | Regression tests | Low | npm test |
| `src/ui/Dashboard.jsx` | Modify | Use react-window | Medium | Dashboard.test.ts, visual |
| `src/ui/VirtualList.jsx` | Create | Wrapper component | Low | VirtualList.test.ts |
| `src/` (all callers) | Modify | Add await to store.mutate | Medium | npm test (all) |
| `src/api/v2.ts` | Create | New API endpoint | Low | api/v2.test.ts |
| `src/server.ts` | Modify | Register /api/v2 router | Low | server.test.ts |

---

## Testing Approach

### Unit Tests
```bash
npm test -- Store.test.ts              # Existing tests (should still pass)
npm test -- Store.concurrency.test.ts  # New concurrency tests
npm test -- Dashboard.test.ts          # Existing tests (may need await updates)
npm test -- api/v2.test.ts             # New API tests
```

### Integration Tests
```bash
npm test -- integration/               # End-to-end flows
# Test: create entity → mutate → query v1 (unchanged)
# Test: create entity → mutate → query v2 (new pagination)
```

### Performance Tests
```bash
npm run perf:dashboard                 # Benchmark rendering
# Old: 800ms (5k items) → New: 80ms (virtualized)
```

### Load Tests (Staging Only)
```bash
npm run load:test -- --users 500 --mutations-per-sec 10
# Verify lock doesn't bottleneck
# Monitor lock queue depth (should stay < 5)
```

---

## Rollback Plan

### If Store Lock Causes Bottleneck
```typescript
// Revert to non-locking Store.mutate()
// 1. Remove async-lock from package.json
// 2. Revert Store.ts to simple assignment: this.state = fn(this.state)
// 3. Revert all await calls to non-await
// 4. Deploy; verify (5min downtime)
// Note: Concurrency bug returns, but at least system is responsive
```

### If Virtualization Breaks Rendering
```typescript
// Revert to non-virtualized list
// 1. Replace FixedSizeList with simple map() loop
// 2. Revert Dashboard.jsx to old implementation
// 3. Deploy; UI will be slow again (800ms) but correct
// 4. Investigate rendering issue separately
```

### If API v2 has Schema Issues
```typescript
// v2 is new, so external clients aren't using it yet
// 1. Fix schema in src/api/v2.ts
// 2. Redeploy; no external impact
// 3. If critical bug, just disable v2 endpoint and keep v1
```

### If Database Migration Fails
```typescript
// No schema changes in this plan, so this shouldn't happen
// But if it does:
// 1. Immediately roll back to previous deploy
// 2. Coordinate with DevOps; fix migration
// 3. Redeploy when migration is verified safe
```

---

## Next Phase
→ Proceed to **OPTIMIZATIONS** (if this is a complex feature) or **EXECUTION_CHECKLIST** (ready to execute).
