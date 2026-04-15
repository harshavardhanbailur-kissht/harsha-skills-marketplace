# React Performance Reference

## 1. React Compiler (19+)

### Auto-Memoization
React Compiler automatically memoizes components and values without explicit `React.memo()` or `useMemo()`. It runs during build-time and requires `babel-plugin-react-compiler`.

**Detection Pattern:**
```bash
# Check if compiler is installed
npm list babel-plugin-react-compiler

# Verify in babel config
grep -r "babel-plugin-react-compiler" babel.config.js .babelrc
```

**What It Catches:**
- Stable values and functions at component level
- Simple derived state patterns
- Safe to memoize re-renders

**What It Misses:**
- Complex object mutations in closures
- External library side effects (e.g., gsap animations)
- Dynamic array/object creation in event handlers that rely on reference equality

**Fix: Enable compiler**
```javascript
// babel.config.js
module.exports = {
  plugins: [['babel-plugin-react-compiler']],
};
```

---

## 2. Server Components (RSC)

### Payload Optimization
Move data fetching and heavy computations to Server Components. Only send serializable React elements to client.

**Client Boundary Placement Pattern:**
```javascript
// app/page.js (Server Component)
import { Suspense } from 'react';
import ClientCounter from './ClientCounter';
import expensiveData from './expensive-compute';

export default async function Page() {
  const data = await expensiveData(); // Runs on server only
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ClientCounter initialData={data} />
    </Suspense>
  );
}

// ClientCounter.js (Client Component)
'use client';
export default function ClientCounter({ initialData }) {
  const [count, setCount] = useState(0);
  return <div>{count}</div>;
}
```

**Streaming SSR:**
- Use `Suspense` boundaries to stream chunks incrementally
- Client receives HTML before all data loads
- Prevents waterfall requests

```javascript
export default function Page() {
  return (
    <div>
      <Header />
      <Suspense fallback={<Skeleton />}>
        <SlowComponent />
      </Suspense>
    </div>
  );
}
```

---

## 3. Concurrent Features

### useTransition for Non-Urgent Updates
Wrap state updates that don't need immediate feedback (search filtering, sorting).

**Detection Pattern:**
```javascript
// BEFORE: Blocks UI during expensive filter
const [query, setQuery] = useState('');
const results = useMemo(() =>
  expensiveFilter(items, query),
  [query]
);

// AFTER: Non-blocking transition
const [isPending, startTransition] = useTransition();
const [query, setQuery] = useState('');

const handleChange = (e) => {
  startTransition(() => {
    setQuery(e.target.value);
  });
};
```

### useDeferredValue for Expensive Renders
Defers re-rendering of expensive components while keeping UI responsive.

```javascript
const [value, setValue] = useState('');
const deferredValue = useDeferredValue(value);

const results = useMemo(
  () => expensiveSearch(deferredValue),
  [deferredValue]
);

return (
  <>
    <input onChange={(e) => setValue(e.target.value)} />
    <List items={results} />
  </>
);
```

### Suspense Boundaries
Wrap async data fetching with Suspense for graceful loading states.

```javascript
<Suspense fallback={<LoadingSpinner />}>
  <AsyncDataComponent />
</Suspense>
```

---

## 4. State Management

### Zustand v5 Selective Subscriptions
Zustand automatically prevents re-renders when only unselected state changes.

```javascript
import { create } from 'zustand';

const useStore = create((set) => ({
  count: 0,
  user: { name: 'John', age: 30 },
  increment: () => set(state => ({ count: state.count + 1 })),
}));

// Only re-renders when count changes
function Counter() {
  const count = useStore(state => state.count);
  return <div>{count}</div>;
}

// Only re-renders when user.name changes
function UserName() {
  const name = useStore(state => state.user.name);
  return <div>{name}</div>;
}
```

### Context Splitting
Avoid cascading re-renders by splitting context into separate providers.

**Before (anti-pattern):**
```javascript
const AppContext = createContext();

export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState([]);

  return (
    <AppContext.Provider value={{ user, theme, notifications }}>
      {children}
    </AppContext.Provider>
  );
}

// Any change to user/theme/notifications causes full tree re-render
```

**After (fix):**
```javascript
const UserContext = createContext();
const ThemeContext = createContext();
const NotificationsContext = createContext();

export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState([]);

  return (
    <UserContext.Provider value={user}>
      <ThemeContext.Provider value={theme}>
        <NotificationsContext.Provider value={notifications}>
          {children}
        </NotificationsContext.Provider>
      </ThemeContext.Provider>
    </UserContext.Provider>
  );
}
```

### Jotai Atoms
Fine-grained reactivity with atom-based state.

```javascript
import { atom, useAtom } from 'jotai';

const countAtom = atom(0);
const userAtom = atom({ name: 'John' });

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

---

## 5. List Virtualization

### TanStack Virtual
Render only visible items in large lists.

```javascript
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }) {
  const parentRef = useRef(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  const virtualItems = virtualizer.getVirtualItems();

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualItems.map(virtualItem => (
          <div key={virtualItem.key} data-index={virtualItem.index}>
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Dynamic Heights with Key Strategies
Use stable, semantic keys (not array index).

```javascript
// BAD: Index as key (breaks virtualization)
{items.map((item, index) => <Item key={index} />)}

// GOOD: Stable ID
{items.map(item => <Item key={item.id} {...item} />)}
```

---

## 6. Bundle Splitting

### React.lazy + Code Splitting
Load components on-demand.

```javascript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Route-Based vs Component-Based Splitting
Route-based: split at pages; Component-based: split at feature boundaries.

```javascript
// Route-based (ideal for Next.js pages)
const AdminPage = lazy(() => import('./pages/Admin'));
const UserPage = lazy(() => import('./pages/User'));

// Component-based (within pages)
const MediaUploader = lazy(() => import('./components/MediaUploader'));
const AdvancedSettings = lazy(() => import('./components/AdvancedSettings'));
```

### Prefetching Chunks
Preload chunks for better UX.

```javascript
// Next.js automatic prefetch on link hover
import Link from 'next/link';

export default function Nav() {
  return <Link href="/about" prefetch>About</Link>;
}

// Manual prefetch
const chunk = lazy(() => import('./Heavy'));
React.startTransition(() => {
  import('./Heavy'); // Preload
});
```

---

## 7. Detection Patterns for Common Issues

### Inline Objects in JSX
**Detection Pattern:**
```javascript
// BAD: Object created on every render
<Component style={{ color: 'red', fontSize: '16px' }} />
<List items={items.map(i => ({ ...i, active: false }))} />
```

**Context Check:**
- Function component re-renders frequently
- Child components receive new object reference each render

**Safe Fix:**
```javascript
// EXTRACT TO CONSTANT
const styles = { color: 'red', fontSize: '16px' };
<Component style={styles} />

// OR MEMOIZE
const memoizedItems = useMemo(() =>
  items.map(i => ({ ...i, active: false })),
  [items]
);
<List items={memoizedItems} />

// OR USE OBJECT WITH useMemo
const mappedItems = useMemo(() => ({
  color: 'red',
  fontSize: '16px',
}), []);
```

---

### Missing memo on Expensive Components
**Detection Pattern:**
```javascript
// BAD: Expensive render on every parent update
function ExpensiveList({ items }) {
  const processed = items.map(expensiveTransform);
  return <div>{processed.map(item => <Item key={item.id} />)}</div>;
}
```

**Context Check:**
- Component takes props that rarely change
- Component renders expensive calculations
- Parent re-renders frequently for unrelated reasons

**Safe Fix:**
```javascript
const ExpensiveList = React.memo(({ items }) => {
  const processed = items.map(expensiveTransform);
  return <div>{processed.map(item => <Item key={item.id} />)}</div>;
}, (prev, next) => {
  // Custom comparison: only re-render if items array reference changes
  return prev.items === next.items;
});
```

---

### Missing useCallback
**Detection Pattern:**
```javascript
// BAD: New function reference each render
<Button onClick={() => handleClick(id)} />
```

**Context Check:**
- Function passed to memoized child component
- Function used as dependency in useEffect

**Safe Fix:**
```javascript
const handleClick = useCallback((id) => {
  // handle click
}, [id]); // Only recreate if id changes

<Button onClick={handleClick} />
```

---

### Context Causing Cascading Re-renders
**Detection Pattern:**
```javascript
// BAD: All consumers re-render on any value change
const MyContext = createContext();
<MyContext.Provider value={{ user, settings, ui }}>
  {children}
</MyContext.Provider>

// Usage: re-renders entire tree when settings change
const { settings } = useContext(MyContext);
```

**Context Check:**
- Multiple consumers, only some use specific values
- High-frequency updates (animations, scroll events)

**Safe Fix:**
```javascript
// Split into separate contexts
const UserContext = createContext();
const SettingsContext = createContext();

<UserContext.Provider value={user}>
  <SettingsContext.Provider value={settings}>
    {children}
  </SettingsContext.Provider>
</UserContext.Provider>

// Or use custom hook with selector
const useContextValue = (selector) => {
  const context = useContext(MyContext);
  return useMemo(() => selector(context), [context, selector]);
};
```

---

### State Updates in useEffect Loop
**Detection Pattern:**
```javascript
// BAD: Infinite loop or wasteful updates
useEffect(() => {
  setState(computeValue()); // Updates trigger effect again
}, []);

// BAD: Missing dependencies
useEffect(() => {
  setData(items.length);
}, []);
```

**Context Check:**
- useEffect has state setter but no dependency array
- State dependency missing from array

**Safe Fix:**
```javascript
// Use proper dependencies
useEffect(() => {
  // Only runs when items changes
  setData(items.length);
}, [items]);

// Or use derived state (React 19)
const data = useMemo(() => items.length, [items]);

// Or use useTransition for deferred updates
const [isPending, startTransition] = useTransition();
useEffect(() => {
  startTransition(() => {
    setData(items.length);
  });
}, [items]);
```

---

### Missing key Prop in Lists
**Detection Pattern:**
```javascript
// BAD: No key or index as key
{items.map((item, i) => <Item key={i} data={item} />)}
```

**Context Check:**
- List items have input fields (lose focus/value)
- List items have local state that gets mixed up
- List order can change

**Safe Fix:**
```javascript
// Use stable, unique identifier
{items.map(item => <Item key={item.id} data={item} />)}

// For new items without IDs, generate once
const itemsWithKeys = useMemo(() =>
  items.map((item, i) => ({
    ...item,
    _key: item.id || `${item.name}-${i}`
  })),
  [items]
);
{itemsWithKeys.map(item => <Item key={item._key} data={item} />)}
```

---

## Performance Measurement

```javascript
// Measure component render time
useEffect(() => {
  performance.mark('component-start');

  return () => {
    performance.mark('component-end');
    performance.measure('component', 'component-start', 'component-end');
    const measure = performance.getEntriesByName('component')[0];
    console.log(`Render time: ${measure.duration}ms`);
  };
}, []);

// Profiler API
import { Profiler } from 'react';

<Profiler id="List" onRender={(id, phase, actualDuration) => {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}}>
  <ExpensiveList items={items} />
</Profiler>
```
