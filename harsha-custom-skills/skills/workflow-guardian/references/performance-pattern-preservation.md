# Performance Pattern Preservation for Workflow Guardian

## Overview

Performance regressions are subtle—an application can still function correctly but become noticeably slow, janky, or unresponsive. The workflow-guardian skill must detect and prevent these regressions when adding features or refactoring code. Performance patterns in React are architectural decisions that must be preserved, not optimized independently.

**Key Principle:** When adding features to an existing React codebase, the primary responsibility is to **replicate existing performance patterns**, not to introduce optimization or reorganization.

---

## 1. React Memoization Patterns

### 1.1 Understanding React.memo()

`React.memo()` is a higher-order component that prevents re-renders when props haven't changed. It performs a shallow comparison of props.

#### Detection Pattern
```javascript
// EXISTING CODE WITH MEMOIZATION
const UserCard = memo(({ userId, userName }) => {
  return (
    <div className="user-card">
      <h2>{userName}</h2>
      <p>ID: {userId}</p>
    </div>
  );
});
```

#### Critical Preservation Rule
When adding a feature to a component wrapped in `memo()`, all new child components added to that tree should also be wrapped in `memo()`.

```javascript
// DANGEROUS: Adding new component without memo breaks memoization chain
const UserCard = memo(({ userId, userName }) => {
  return (
    <div className="user-card">
      <h2>{userName}</h2>
      <UserStats userId={userId} />  // NEW: Missing memo!
    </div>
  );
});

// SAFE: Replicate the memoization pattern
const UserStats = memo(({ userId }) => {
  return <p>Stats for user {userId}</p>;
});

const UserCard = memo(({ userId, userName }) => {
  return (
    <div className="user-card">
      <h2>{userName}</h2>
      <UserStats userId={userId} />
    </div>
  );
});
```

#### Cascading Re-render Problem
When a memoized component receives a prop that's a new reference each render (object, array, or function), it defeats memoization:

```javascript
// DANGEROUS: Breaks memoization chain despite memo()
const Parent = () => {
  const config = { theme: 'dark' };  // NEW OBJECT EVERY RENDER
  return <MemoizedChild config={config} />;  // memo() can't prevent re-render
};

const MemoizedChild = memo(({ config }) => {
  return <div>Theme: {config.theme}</div>;
});

// SAFE: Stable reference preserves memo effectiveness
const Parent = () => {
  const config = useMemo(() => ({ theme: 'dark' }), []);
  return <MemoizedChild config={config} />;
};
```

### 1.2 useMemo() Preservation

`useMemo()` caches expensive computations between renders. It's essential when:
- Computing expensive values that depend on props/state
- Creating objects/arrays that are dependencies for other hooks
- Memoized components receive these values as props

#### Detection Pattern
```javascript
// EXISTING CODE WITH useMemo
const DataProcessor = ({ largeDataset }) => {
  const processedData = useMemo(() => {
    return largeDataset
      .filter(item => item.active)
      .map(item => ({
        ...item,
        computed: expensiveCalculation(item)
      }));
  }, [largeDataset]);

  return <div>{JSON.stringify(processedData)}</div>;
};
```

#### When Adding Features to useMemo Components
If you add a new feature that depends on the memoized value, you must ensure it also uses memoization if it creates new references:

```javascript
// DANGEROUS: New feature breaks memoization chain
const DataProcessor = ({ largeDataset }) => {
  const processedData = useMemo(() => {
    return largeDataset.filter(item => item.active);
  }, [largeDataset]);

  // NEW FEATURE: Creates new display format every render
  const displayFormat = {
    style: 'compact',
    data: processedData
  };

  return <DisplayComponent format={displayFormat} />;  // Breaks memo
};

// SAFE: Preserve memoization for new feature
const DataProcessor = ({ largeDataset }) => {
  const processedData = useMemo(() => {
    return largeDataset.filter(item => item.active);
  }, [largeDataset]);

  // NEW FEATURE: Memoized to preserve reference
  const displayFormat = useMemo(() => ({
    style: 'compact',
    data: processedData
  }), [processedData]);

  return <DisplayComponent format={displayFormat} />;
};
```

### 1.3 useCallback() Preservation

`useCallback()` caches function references between renders, critical for:
- Event handlers passed to memoized components
- Functions used as dependencies in useEffect
- Callbacks passed to custom hooks

#### Detection Pattern
```javascript
// EXISTING CODE WITH useCallback
const SearchInput = memo(({ onSearch }) => {
  return (
    <input
      type="text"
      onChange={(e) => onSearch(e.target.value)}
    />
  );
});

const SearchContainer = ({ onResults }) => {
  const handleSearch = useCallback((query) => {
    const results = performSearch(query);
    onResults(results);
  }, [onResults]);

  return <SearchInput onSearch={handleSearch} />;
};
```

#### Functional State Update Pattern
When using `useCallback` with state, prefer functional state updates to minimize dependencies:

```javascript
// DANGEROUS: Stale closure - callback uses old state value
const Counter = () => {
  const [count, setCount] = useState(0);

  const increment = useCallback(() => {
    setCount(count + 1);  // STALE: uses count from initial render
  }, [count]);  // Must add count as dependency, defeating stability

  return <button onClick={increment}>{count}</button>;
};

// SAFE: Functional state updates avoid dependency
const Counter = () => {
  const [count, setCount] = useState(0);

  const increment = useCallback(() => {
    setCount(prev => prev + 1);  // Uses current state, stable callback
  }, []);  // No dependencies needed

  return <button onClick={increment}>{count}</button>;
};
```

### 1.4 React Compiler and Automatic Memoization (React 19+)

In React 19+, the React Compiler automatically applies memoization (equivalent to useMemo and useCallback) where safe. This changes the preservation strategy:

- **With Compiler:** You should NOT add manual memoization unless you need precise control
- **Without Compiler:** Replicate existing memoization patterns
- **Detection:** Check if `'use compiler'` directive is present at module top

```javascript
// React 19+ with Compiler directive
'use compiler';

// Compiler handles memoization automatically
const UserProfile = ({ userId, userName }) => {
  const userStats = calculateStats(userId);  // Auto-memoized by compiler

  return (
    <div>
      <h2>{userName}</h2>
      <Stats data={userStats} />
    </div>
  );
};
```

**Pattern Preservation with Compiler:**
- Do NOT add unnecessary useMemo/useCallback with compiler enabled
- The compiler is more effective without manual memoization interference
- Focus on structural improvements instead (component composition, state colocation)

---

## 2. Code Splitting Preservation

Code splitting reduces initial bundle size by dividing code into chunks loaded on-demand. Breaking code splitting patterns causes larger initial bundles and slower page load.

### 2.1 React.lazy() Pattern Detection

`React.lazy()` creates dynamic imports that bundlers split into separate chunks.

#### Detection Pattern
```javascript
// EXISTING CODE WITH CODE SPLITTING
const HeavyDashboard = lazy(() => import('./pages/Dashboard'));
const AdminPanel = lazy(() => import('./pages/AdminPanel'));

const App = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<HeavyDashboard />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </Suspense>
  );
};
```

#### Critical Rule: Don't Import Lazy Chunks at Module Top Level

```javascript
// DANGEROUS: Importing lazy component defeats code splitting
import HeavyDashboard from './pages/Dashboard';  // Bundle grows immediately!

const App = () => {
  return <HeavyDashboard />;
};

// SAFE: Use lazy() to preserve splitting
const HeavyDashboard = lazy(() => import('./pages/Dashboard'));

const App = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyDashboard />
    </Suspense>
  );
};
```

### 2.2 Dynamic Import Preservation

When adding new routes or features to a module with lazy loading, preserve the pattern:

```javascript
// EXISTING CODE STRUCTURE
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

const App = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Router>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Router>
    </Suspense>
  );
};

// DANGEROUS: Adding new feature at top level breaks splitting
import ProfilePage from './pages/Profile';  // NEW: Breaks splitting!

const App = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Router>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<ProfilePage />} />  // Bundled immediately
      </Router>
    </Suspense>
  );
};

// SAFE: Preserve code splitting for new features
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Profile = lazy(() => import('./pages/Profile'));  // NEW: Maintains splitting

const App = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Router>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/profile" element={<Profile />} />
      </Router>
    </Suspense>
  );
};
```

### 2.3 Webpack Magic Comments for Prefetching

Preserve existing prefetch/preload directives:

```javascript
// EXISTING PATTERN: Prefetch dashboard on idle
const Dashboard = lazy(() =>
  import(
    /* webpackChunkName: "dashboard" */
    /* webpackPrefetch: true */
    './pages/Dashboard'
  )
);

// SAFE: Match the pattern for new routes
const Reports = lazy(() =>
  import(
    /* webpackChunkName: "reports" */
    /* webpackPrefetch: true */
    './pages/Reports'
  )
);

// DANGEROUS: Missing magic comments breaks consistency
const Analytics = lazy(() => import('./pages/Analytics'));  // No chunk name, no prefetch
```

### 2.4 Import Path Analysis

When adding imports, check if they break splitting:

```javascript
// EXISTING LAZY MODULE
const Dashboard = lazy(() => import('./pages/Dashboard'));

// Dashboard.tsx contains:
export default DashboardPage;

// DANGEROUS: Importing named exports from lazy chunk
const DashboardUtils = lazy(() =>
  import('./pages/Dashboard').then(m => ({ default: m.Utils }))  // Complex workaround
);

// SAFE: Use intermediate module that re-exports
// dashboardUtils.ts
export { Utils } from './pages/Dashboard';

const DashboardUtils = lazy(() => import('./dashboardUtils'));
```

---

## 3. Virtualization Pattern Preservation

Virtualization renders only visible list items, critical for large datasets. Breaking virtualization patterns causes entire lists to render, destroying performance on lists with 1000+ items.

### 3.1 react-window Detection

```javascript
// EXISTING VIRTUALIZATION PATTERN
import { FixedSizeList } from 'react-window';

const UserList = ({ users }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      {users[index].name}
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={users.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

#### Critical Rule: Don't Remove Virtualization

```javascript
// DANGEROUS: Converting virtualized list to standard rendering
const UserList = ({ users }) => {
  return (
    <div>
      {users.map(user => (
        <div key={user.id}>{user.name}</div>  // Renders 1000+ DOM nodes
      ))}
    </div>
  );
};

// SAFE: Add features while preserving virtualization
import { FixedSizeList } from 'react-window';

const UserList = ({ users, onUserSelect }) => {
  const Row = memo(({ index, style }) => (
    <div style={style} onClick={() => onUserSelect(users[index])}>
      <UserCard user={users[index]} />  // NEW FEATURE: Still virtualized
    </div>
  ));

  return (
    <FixedSizeList
      height={600}
      itemCount={users.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

### 3.2 VariableSizeList Preservation

When list items have variable heights, preserve the pattern:

```javascript
// EXISTING VARIABLE SIZE LIST
import { VariableSizeList } from 'react-window';

const PostList = ({ posts }) => {
  const listRef = useRef();
  const itemSizes = useMemo(
    () => posts.map(post => post.height || 100),
    [posts]
  );

  const getItemSize = useCallback(
    index => itemSizes[index],
    [itemSizes]
  );

  const Row = ({ index, style }) => (
    <div style={style}>{posts[index].content}</div>
  );

  return (
    <VariableSizeList
      ref={listRef}
      itemCount={posts.length}
      itemSize={getItemSize}
      height={800}
      width="100%"
    >
      {Row}
    </VariableSizeList>
  );
};

// DANGEROUS: Converting to fixed size breaks dynamic content
const PostList = ({ posts }) => {
  return (
    <FixedSizeList
      itemCount={posts.length}
      itemSize={100}  // Cuts off long posts!
      height={800}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{posts[index].content}</div>
      )}
    </FixedSizeList>
  );
};

// SAFE: Preserve variable sizing pattern
import { VariableSizeList } from 'react-window';

const PostList = ({ posts, onPostClick }) => {
  const listRef = useRef();
  const itemSizes = useMemo(
    () => posts.map(post => post.height || 100),
    [posts]
  );

  const getItemSize = useCallback(
    index => itemSizes[index],
    [itemSizes]
  );

  const Row = memo(({ index, style }) => (
    <div style={style} onClick={() => onPostClick(posts[index])}>
      <PostCard post={posts[index]} />  // NEW FEATURE
    </div>
  ));

  return (
    <VariableSizeList
      ref={listRef}
      itemCount={posts.length}
      itemSize={getItemSize}
      height={800}
      width="100%"
    >
      {Row}
    </VariableSizeList>
  );
};
```

### 3.3 Overscan Configuration Preservation

```javascript
// EXISTING PATTERN: Overscan to prevent flash of empty space
const VirtualizedGrid = ({ items }) => {
  return (
    <FixedSizeList
      itemCount={items.length}
      itemSize={100}
      overscanCount={10}  // Pre-render 10 items outside viewport
      height={600}
      width="100%"
    >
      {({ index, style }) => (
        <GridItem item={items[index]} style={style} />
      )}
    </FixedSizeList>
  );
};

// DANGEROUS: Removing overscan causes visual flashing
const VirtualizedGrid = ({ items }) => {
  return (
    <FixedSizeList
      itemCount={items.length}
      itemSize={100}
      // overscanCount removed - causes flashing on scroll
      height={600}
      width="100%"
    >
      {({ index, style }) => (
        <GridItem item={items[index]} style={style} />
      )}
    </FixedSizeList>
  );
};
```

### 3.4 Infinite Scroll / Windowed Infinite Loader Preservation

```javascript
// EXISTING PATTERN: Virtualized infinite scroll
import { FixedSizeList } from 'react-window';
import InfiniteLoader from 'react-window-infinite-loader';

const InfiniteList = ({ items, hasMore, loadMore }) => {
  const isItemLoaded = useCallback(
    index => index < items.length,
    [items.length]
  );

  const Row = ({ index, style }) => {
    if (!isItemLoaded(index)) {
      return <div style={style}>Loading...</div>;
    }
    return <div style={style}>{items[index].text}</div>;
  };

  return (
    <InfiniteLoader
      isItemLoaded={isItemLoaded}
      itemCount={hasMore ? items.length + 1 : items.length}
      loadMoreItems={loadMore}
    >
      {({ onItemsRendered, ref }) => (
        <FixedSizeList
          ref={ref}
          onItemsRendered={onItemsRendered}
          itemCount={hasMore ? items.length + 1 : items.length}
          itemSize={50}
          height={600}
          width="100%"
        >
          {Row}
        </FixedSizeList>
      )}
    </InfiniteLoader>
  );
};

// SAFE: Add features while preserving infinite scroll pattern
const InfiniteList = ({ items, hasMore, loadMore, onItemClick }) => {
  const isItemLoaded = useCallback(
    index => index < items.length,
    [items.length]
  );

  const Row = memo(({ index, style }) => {
    if (!isItemLoaded(index)) {
      return <div style={style}>Loading...</div>;
    }
    return (
      <div style={style} onClick={() => onItemClick(items[index])}>
        <ItemCard item={items[index]} />  // NEW FEATURE: Still virtualized
      </div>
    );
  });

  return (
    <InfiniteLoader
      isItemLoaded={isItemLoaded}
      itemCount={hasMore ? items.length + 1 : items.length}
      loadMoreItems={loadMore}
    >
      {({ onItemsRendered, ref }) => (
        <FixedSizeList
          ref={ref}
          onItemsRendered={onItemsRendered}
          itemCount={hasMore ? items.length + 1 : items.length}
          itemSize={50}
          height={600}
          width="100%"
        >
          {Row}
        </FixedSizeList>
      )}
    </InfiniteLoader>
  );
};
```

---

## 4. Data Fetching Performance Patterns

Data fetching libraries (TanStack Query, SWR, Apollo) implement caching, deduplication, and stale-while-revalidate patterns that must be preserved.

### 4.1 TanStack Query Pattern Detection

```javascript
// EXISTING TANSTACK QUERY PATTERN
import { useQuery, useQueryClient } from '@tanstack/react-query';

const useUserData = (userId) => {
  return useQuery({
    queryKey: ['users', userId],
    queryFn: async () => {
      const res = await fetch(`/api/users/${userId}`);
      return res.json();
    },
    staleTime: 1000 * 60 * 5,  // 5 minutes
    gcTime: 1000 * 60 * 10,      // 10 minutes
  });
};

const UserProfile = ({ userId }) => {
  const { data, isLoading, error } = useUserData(userId);
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <div>{data.name}</div>;
};
```

#### Critical Rule: Preserve Query Key Structure

Query keys must be consistent and never hardcoded in multiple places:

```javascript
// DANGEROUS: Different query key structure defeats caching
const UserProfile = ({ userId }) => {
  const { data: profile } = useQuery({
    queryKey: ['user', userId],  // Different structure!
    queryFn: () => fetchUser(userId),
  });

  const { data: stats } = useQuery({
    queryKey: ['users', userId, 'stats'],  // Different nesting!
    queryFn: () => fetchUserStats(userId),
  });

  return <div>{profile?.name}</div>;
};

// SAFE: Centralize query keys and preserve structure
// queryKeys.ts
export const userQueries = {
  all: ['users'] as const,
  lists: () => [...userQueries.all, 'list'] as const,
  list: (filters) => [...userQueries.lists(), { filters }] as const,
  details: () => [...userQueries.all, 'detail'] as const,
  detail: (id) => [...userQueries.details(), id] as const,
  stats: (id) => [...userQueries.detail(id), 'stats'] as const,
};

const useUserData = (userId) => {
  return useQuery({
    queryKey: userQueries.detail(userId),
    queryFn: () => fetchUser(userId),
    staleTime: 1000 * 60 * 5,
  });
};

const useUserStats = (userId) => {
  return useQuery({
    queryKey: userQueries.stats(userId),
    queryFn: () => fetchUserStats(userId),
  });
};
```

### 4.2 Cache Invalidation Pattern Preservation

```javascript
// EXISTING CACHE INVALIDATION PATTERN
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { userQueries } from './queryKeys';

const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (user) => {
      const res = await fetch(`/api/users/${user.id}`, {
        method: 'PUT',
        body: JSON.stringify(user),
      });
      return res.json();
    },
    onSuccess: (data) => {
      // Invalidate both detail and list queries
      queryClient.invalidateQueries({
        queryKey: userQueries.detail(data.id),
      });
      queryClient.invalidateQueries({
        queryKey: userQueries.lists(),
      });
    },
  });
};

// DANGEROUS: Adding new mutation without proper invalidation
const useAddUserTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, tag }) => {
      const res = await fetch(`/api/users/${userId}/tags`, {
        method: 'POST',
        body: JSON.stringify({ tag }),
      });
      return res.json();
    },
    onSuccess: () => {
      // MISSING: No invalidation of affected queries!
      // This leaves user list showing stale data
    },
  });
};

// SAFE: New mutation follows cache invalidation pattern
const useAddUserTag = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, tag }) => {
      const res = await fetch(`/api/users/${userId}/tags`, {
        method: 'POST',
        body: JSON.stringify({ tag }),
      });
      return res.json();
    },
    onSuccess: (data) => {
      // Invalidate affected queries
      queryClient.invalidateQueries({
        queryKey: userQueries.detail(data.userId),
      });
      queryClient.invalidateQueries({
        queryKey: userQueries.lists(),
      });
    },
  });
};
```

### 4.3 SWR Pattern Preservation

```javascript
// EXISTING SWR PATTERN: Stale-while-revalidate
import useSWR from 'swr';

const fetcher = (url) => fetch(url).then(r => r.json());

const UserDashboard = ({ userId }) => {
  const { data, error, isLoading, mutate } = useSWR(
    `/api/users/${userId}`,
    fetcher,
    {
      revalidateOnFocus: true,
      dedupingInterval: 60000,  // Deduplicate for 1 minute
    }
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error</div>;

  return <div>{data.name}</div>;
};

// DANGEROUS: Removing SWR for standard fetch breaks caching
const UserDashboard = ({ userId }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(setData);
  }, [userId]);  // No deduplication, no caching, unnecessary refetches

  return <div>{data?.name}</div>;
};

// SAFE: Add features while preserving SWR pattern
const UserDashboard = ({ userId }) => {
  const { data: userData, error, isLoading, mutate } = useSWR(
    `/api/users/${userId}`,
    fetcher,
    { dedupingInterval: 60000 }
  );

  const { data: stats } = useSWR(
    userId ? `/api/users/${userId}/stats` : null,  // Dependent query
    fetcher,
    { dedupingInterval: 60000 }
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error</div>;

  return (
    <div>
      <h2>{userData.name}</h2>
      <UserStats stats={stats} />  // NEW FEATURE: Uses SWR pattern
    </div>
  );
};
```

### 4.4 Dependent Query Pattern Preservation

```javascript
// EXISTING DEPENDENT QUERY PATTERN
const useUserWithPosts = (userId) => {
  const { data: user } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => fetchUser(userId),
  });

  const { data: posts } = useQuery({
    queryKey: ['posts', 'user', userId],
    queryFn: () => fetchUserPosts(userId),
    enabled: !!user,  // Only fetch when user exists
  });

  return { user, posts };
};

// DANGEROUS: Adding dependent query without enabled flag
const useUserWithPosts = (userId) => {
  const { data: user } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => fetchUser(userId),
  });

  const { data: posts } = useQuery({
    queryKey: ['posts', 'user', userId],
    queryFn: () => fetchUserPosts(userId),
    // enabled flag missing - fetches even when user is undefined
  });

  return { user, posts };
};

// SAFE: New dependent query follows pattern
const useUserWithPostsAndComments = (userId) => {
  const { data: user } = useQuery({
    queryKey: ['users', userId],
    queryFn: () => fetchUser(userId),
  });

  const { data: posts } = useQuery({
    queryKey: ['posts', 'user', userId],
    queryFn: () => fetchUserPosts(userId),
    enabled: !!user,
  });

  const { data: comments } = useQuery({
    queryKey: ['comments', 'user', userId],
    queryFn: () => fetchUserComments(userId),
    enabled: !!user,  // PRESERVED: Only fetch with user data
  });

  return { user, posts, comments };
};
```

---

## 5. Render Performance Patterns

### 5.1 Key Prop Patterns

The `key` prop must be stable and unique within a list. Using array indices as keys is a common performance regression.

#### Detection Pattern
```javascript
// EXISTING PATTERN: Stable IDs
const UserList = ({ users, onSelect }) => {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id} onClick={() => onSelect(user)}>  // Stable ID
          {user.name}
        </li>
      ))}
    </ul>
  );
};
```

#### Critical Rule: Never Use Index as Key in Dynamic Lists

```javascript
// DANGEROUS: Index keys in mutable list
const TodoList = ({ todos, onToggle }) => {
  return (
    <ul>
      {todos.map((todo, index) => (
        <li key={index} onClick={() => onToggle(index)}>  // DANGER!
          {todo.text}
        </li>
      ))}
    </ul>
  );
};

// When user reorders: todos = [C, A, B]
// React thinks: [A, B, C] -> [C, A, B] (just re-sorted!)
// But state is tied to key "0", "1", "2" (always same 3 items)
// Result: State corruption, wrong checkmarks appear

// SAFE: Use stable IDs
const TodoList = ({ todos, onToggle }) => {
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id} onClick={() => onToggle(todo.id)}>
          {todo.text}
        </li>
      ))}
    </ul>
  );
};
```

#### Exception: Paginated Lists

Index keys are acceptable when list content is static per page:

```javascript
// SAFE WITH INDEX: Paginated list (content doesn't change within page)
const PaginatedUsers = ({ users, currentPage }) => {
  return (
    <ul>
      {users.map((user, index) => (
        <li key={index}>  // OK: Page content is static
          {user.name}
        </li>
      ))}
    </ul>
  );
};
```

### 5.2 Conditional Rendering Optimization

```javascript
// EXISTING PATTERN: Efficient conditional rendering
const DataDisplay = memo(({ data, showDetails, expanded }) => {
  return (
    <div>
      <h2>{data.title}</h2>
      {showDetails && <Details data={data} />}  // Only renders when needed
      {expanded && (
        <ExpandedContent data={data} />  // Heavy component, conditional
      )}
    </div>
  );
});

// DANGEROUS: Always rendering, hiding with CSS (keeps components in tree)
const DataDisplay = memo(({ data, showDetails, expanded }) => {
  return (
    <div>
      <h2>{data.title}</h2>
      <Details data={data} style={{ display: showDetails ? 'block' : 'none' }} />
      <ExpandedContent data={data} style={{ display: expanded ? 'block' : 'none' }} />
      {/* Always in React tree, always mounted, always re-renders */}
    </div>
  );
});

// SAFE: New features follow conditional pattern
const DataDisplay = memo(({ data, showDetails, expanded, showMetadata }) => {
  return (
    <div>
      <h2>{data.title}</h2>
      {showDetails && <Details data={data} />}
      {expanded && <ExpandedContent data={data} />}
      {showMetadata && <Metadata data={data} />}  // NEW: Also conditional
    </div>
  );
});
```

### 5.3 Fragment Usage Patterns

```javascript
// EXISTING PATTERN: Proper fragment usage
const CardList = ({ cards }) => {
  return (
    <>
      {cards.map(card => (
        <Fragment key={card.id}>
          <CardHeader card={card} />
          <CardBody card={card} />
        </Fragment>
      ))}
    </>
  );
};

// DANGEROUS: Wrapping in unnecessary divs increases DOM depth
const CardList = ({ cards }) => {
  return (
    <div>
      {cards.map(card => (
        <div key={card.id}>
          <CardHeader card={card} />
          <CardBody card={card} />
        </div>  // Extra wrapper increases DOM nesting
      ))}
    </div>
  );
};

// SAFE: New features use appropriate wrapping
const CardList = ({ cards, isGrid }) => {
  return (
    <>
      {cards.map(card => (
        <Fragment key={card.id}>
          <CardHeader card={card} />
          <CardBody card={card} />
          {isGrid && <CardFooter card={card} />}  // NEW: Still uses fragment
        </Fragment>
      ))}
    </>
  );
};
```

### 5.4 Avoiding Inline Object/Function Creation

```javascript
// EXISTING PATTERN: Pre-defined objects/functions
const SearchFilters = memo(({ onFilter }) => {
  const defaultFilters = { status: 'active', limit: 20 };  // Outside JSX

  return (
    <button onClick={() => onFilter(defaultFilters)}>
      Reset Filters
    </button>
  );
});

// DANGEROUS: Inline object creation (new reference every render)
const SearchFilters = memo(({ onFilter }) => {
  return (
    <button onClick={() => onFilter({ status: 'active', limit: 20 })}>
      Reset Filters
    </button>
  );
});

// SAFE: New features follow stable reference pattern
const SearchFilters = memo(({ onFilter, onAdvancedFilter }) => {
  const defaultFilters = useMemo(
    () => ({ status: 'active', limit: 20 }),
    []
  );
  const advancedFilters = useMemo(
    () => ({ status: 'active', limit: 20, sort: 'date' }),
    []
  );

  return (
    <>
      <button onClick={() => onFilter(defaultFilters)}>Reset</button>
      <button onClick={() => onAdvancedFilter(advancedFilters)}>
        Advanced Reset  {/* NEW: Stable reference */}
      </button>
    </>
  );
});
```

---

## 6. Bundle Size Awareness

Adding imports can increase bundle size significantly. Tree-shaking must be considered.

### 6.1 Import Cost Detection

```javascript
// SAFE: Tree-shakeable import
import { debounce } from 'lodash-es';

// DANGEROUS: Full library import (entire lodash bundled)
import { debounce } from 'lodash';

// SAFE: Named import
import { get } from 'lodash-es';

// DANGEROUS: Using get but importing entire object utils
import * as utils from './utils';  // If utils exports 10 helpers, all bundled
```

### 6.2 Dynamic Import for Heavy Dependencies

```javascript
// EXISTING PATTERN: Dynamic import for editor
const useMarkdownEditor = () => {
  const [Editor, setEditor] = useState(null);

  useEffect(() => {
    import('react-markdown-editor').then(module => {
      setEditor(() => module.default);
    });
  }, []);

  return Editor;
};

// DANGEROUS: Static import of heavy dependency
import MarkdownEditor from 'react-markdown-editor';  // Added to main bundle (500KB+)

// SAFE: Match existing dynamic import pattern
const useCodeHighlighter = () => {
  const [Highlighter, setHighlighter] = useState(null);

  useEffect(() => {
    import('prism-react-renderer').then(module => {
      setHighlighter(() => module.default);
    });
  }, []);

  return Highlighter;
};
```

### 6.3 Re-export Detection to Preserve Splitting

```javascript
// EXISTING PATTERN: Re-exports in separate modules
// components/index.ts
export { Button } from './Button';
export { Input } from './Input';

// pages/Dashboard.tsx
import { Button, Input } from '../components';  // Gets split properly

// DANGEROUS: Direct import from nested modules breaks structure
import Button from '../components/Button';  // Might be fine, but inconsistent

// SAFE: Follow existing re-export pattern
// pages/NewPage.tsx
import { Button, Select } from '../components';  // Consistent, maintains structure
```

---

## 7. Common Performance Breakages and Detection

### 7.1 Parent State Update Cascading Re-renders

```javascript
// DANGEROUS: State in parent causes all children to re-render
const Parent = () => {
  const [filter, setFilter] = useState('');
  const [items, setItems] = useState([]);

  return (
    <>
      <input value={filter} onChange={e => setFilter(e.target.value)} />
      <ItemList items={items} />  // Re-renders on every keystroke!
      <Stats items={items} />     // Re-renders on every keystroke!
    </>
  );
};

// SAFE: Colocate state with where it's needed
const Parent = () => {
  const [items, setItems] = useState([]);

  return (
    <>
      <FilterInput />  {/* State lives here, doesn't affect other children */}
      <ItemList items={items} />
      <Stats items={items} />
    </>
  );
};

const FilterInput = () => {
  const [filter, setFilter] = useState('');
  return <input value={filter} onChange={e => setFilter(e.target.value)} />;
};
```

### 7.2 useEffect Dependency Array Omission

```javascript
// DANGEROUS: Missing dependency array causes infinite re-renders
const UserProfile = ({ userId }) => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(setUserData);
    // NO DEPENDENCY ARRAY: Runs on every render, infinite fetching
  });

  return <div>{userData?.name}</div>;
};

// SAFE: Explicit dependency array
const UserProfile = ({ userId }) => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(setUserData);
  }, [userId]);  // Only re-run when userId changes

  return <div>{userData?.name}</div>;
};

// DANGEROUS: Stale dependency array (missing userId)
const UserProfile = ({ userId }) => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(r => r.json())
      .then(setUserData);
  }, []);  // STALE: userId change is ignored, doesn't refetch

  return <div>{userData?.name}</div>;
};
```

### 7.3 Breaking Existing Debounce/Throttle Patterns

```javascript
// EXISTING PATTERN: Debounced search
const useSearchUsers = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const debouncedSearch = useCallback(
    debounce(async (q) => {
      const data = await fetch(`/api/search?q=${q}`).then(r => r.json());
      setResults(data);
    }, 300),
    []
  );

  const handleChange = useCallback((value) => {
    setQuery(value);
    debouncedSearch(value);
  }, [debouncedSearch]);

  return { query, results, handleChange };
};

// DANGEROUS: Removing debounce breaks responsiveness
const useSearchUsers = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleChange = async (value) => {
    setQuery(value);
    const data = await fetch(`/api/search?q=${value}`).then(r => r.json());
    setResults(data);
    // Fetches immediately on every keystroke - heavy API load!
  };

  return { query, results, handleChange };
};

// SAFE: Add features while preserving debounce
const useSearchUsers = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);  // NEW FEATURE

  const debouncedSearch = useCallback(
    debounce(async (q) => {
      const data = await fetch(`/api/search?q=${q}`).then(r => r.json());
      setResults(data);
    }, 300),
    []
  );

  const debouncedSuggestions = useCallback(
    debounce(async (q) => {
      const data = await fetch(`/api/suggestions?q=${q}`).then(r => r.json());
      setSuggestions(data);
    }, 300),
    []
  );

  const handleChange = useCallback((value) => {
    setQuery(value);
    debouncedSearch(value);
    debouncedSuggestions(value);  // NEW: Also debounced
  }, [debouncedSearch, debouncedSuggestions]);

  return { query, results, suggestions, handleChange };
};
```

### 7.4 Breaking Existing Pagination/Infinite Scroll

```javascript
// EXISTING PATTERN: Infinite scroll with cursor
const useInfiniteUsers = () => {
  const [users, setUsers] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(true);

  const loadMore = useCallback(async () => {
    const data = await fetch(
      `/api/users?${cursor ? `cursor=${cursor}` : ''}`
    ).then(r => r.json());

    setUsers(prev => [...prev, ...data.users]);  // APPEND not replace
    setCursor(data.nextCursor);
    setHasMore(!!data.nextCursor);
  }, [cursor]);

  return { users, hasMore, loadMore };
};

// DANGEROUS: Replacing data instead of appending breaks infinite scroll
const useInfiniteUsers = () => {
  const [users, setUsers] = useState([]);

  const loadMore = useCallback(async () => {
    const data = await fetch(`/api/users`).then(r => r.json());
    setUsers(data.users);  // REPLACE: Loses previous items!
  }, []);

  return { users, loadMore };
};

// SAFE: New feature preserves append pattern
const useInfiniteUsers = () => {
  const [users, setUsers] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [pinnedUsers, setPinnedUsers] = useState([]);  // NEW FEATURE

  const loadMore = useCallback(async () => {
    const data = await fetch(
      `/api/users?${cursor ? `cursor=${cursor}` : ''}`
    ).then(r => r.json());

    setUsers(prev => [...prev, ...data.users]);  // PRESERVED: Append
    setCursor(data.nextCursor);
    setHasMore(!!data.nextCursor);
  }, [cursor]);

  const addPinnedUser = useCallback((user) => {
    setPinnedUsers(prev => [user, ...prev]);  // NEW: Also appends
  }, []);

  return { users, pinnedUsers, hasMore, loadMore, addPinnedUser };
};
```

---

## 8. Detection Checklist for Code Review

When reviewing code for performance pattern preservation:

### For React.memo / useMemo / useCallback
- [ ] Existing memoization patterns identified
- [ ] New components added to memoized trees also memoized
- [ ] New expensive computations wrapped in useMemo
- [ ] Callbacks passed to memoized components use useCallback
- [ ] Dependency arrays are correct and minimal
- [ ] No manual memoization added when React Compiler enabled

### For Code Splitting
- [ ] lazy() patterns preserved for new routes
- [ ] No top-level imports added to lazy modules
- [ ] Webpack magic comments maintained
- [ ] Dynamic imports use consistent chunk naming

### For Virtualization
- [ ] Virtualized lists not converted to standard rendering
- [ ] overscanCount configuration preserved
- [ ] Row components wrapped in memo
- [ ] infinite scroll patterns maintained

### For Data Fetching
- [ ] Query key structure consistent
- [ ] Cache invalidation rules applied to new mutations
- [ ] Dependent queries use enabled flag
- [ ] No hardcoded fetch calls mixed with library usage

### For Render Performance
- [ ] List keys are stable IDs, not indices
- [ ] Heavy components use conditional rendering, not display:none
- [ ] No inline objects/functions in render
- [ ] Fragments used instead of divs where appropriate

### For Bundle Size
- [ ] No importing entire libraries for single functions
- [ ] Heavy dependencies use dynamic import
- [ ] Named imports used (not default imports of utils)

### For Common Breakages
- [ ] State colocated, not lifted unnecessarily
- [ ] useEffect dependency arrays complete
- [ ] Existing debounce/throttle patterns preserved
- [ ] Infinite scroll appends, doesn't replace

---

## 9. Sources and Further Reading

Performance pattern research based on current React best practices (2025-2026):

- [React Performance Optimization: 15 Best Practices for 2025 - DEV Community](https://dev.to/alex_bobes/react-performance-optimization-15-best-practices-for-2025-17l9)
- [React Performance Optimization: Best Techniques for Faster, Smoother Apps in 2025 - Growin](https://www.growin.com/blog/react-performance-optimization-2025/)
- [Meta's React Compiler 1.0 Brings Automatic Memoization to Production - InfoQ](https://www.infoq.com/news/2025/12/react-compiler-meta/)
- [React Stack Patterns](https://www.patterns.dev/react/react-2026/)
- [React 19: Auto-Memoization: Cleaner Code, Better Performance](https://javascript.plainenglish.io/react-19-auto-memoization-cleaner-code-better-performance-e7a0629c5819)
- [How to useMemo and useCallback: you can remove most of them - DeveloperWay](https://www.developerway.com/posts/how-to-use-memo-use-callback)
- [Understanding useMemo and useCallback - Josh W. Comeau](https://www.joshwcomeau.com/react/usememo-and-usecallback/)
- [useMemo - React Official Docs](https://react.dev/reference/react/useMemo)
- [useCallback - React Official Docs](https://react.dev/reference/react/useCallback)
- [When to useMemo and useCallback - Kent C. Dodds](https://kentcdodds.com/blog/usememo-and-usecallback)
- [Code-Splitting – React Official Docs](https://legacy.reactjs.org/docs/code-splitting.html)
- [Code Splitting in React - GeeksforGeeks](https://www.geeksforgeeks.org/reactjs/code-splitting-in-react/)
- [Implementing Code Splitting and Lazy Loading in React](https://www.greatfrontend.com/blog/code-splitting-and-lazy-loading-in-react)
- [Code Splitting - Webpack Official Docs](https://webpack.js.org/guides/code-splitting/)
- [Virtualize large lists with react-window - web.dev](https://web.dev/articles/virtualize-long-lists-react-window)
- [List Virtualization - Patterns.dev](https://www.patterns.dev/vanilla/virtual-lists/)
- [How to virtualize large lists using react-window - LogRocket Blog](https://blog.logrocket.com/how-to-virtualize-large-lists-using-react-window/)
- [React Query vs TanStack Query vs SWR: A 2025 Comparison - Refine](https://refine.dev/blog/react-query-vs-tanstack-query-vs-swr-2025/)
- [Caching clash: SWR vs. TanStack Query for React - LogRocket Blog](https://blog.logrocket.com/swr-vs-tanstack-query-react/)
- [React key attribute: best practices for performant lists - DeveloperWay](https://www.developerway.com/posts/react-key-attribute)
- [Lists and Keys – React Official Docs](https://legacy.reactjs.org/docs/lists-and-keys.html)
- [Object & array dependencies in the React useEffect Hook - Ben Ilegbodu](https://www.benmvp.com/blog/object-array-dependencies-react-useEffect-hook/)
- [React re-renders guide: everything, all at once - DeveloperWay](https://www.developerway.com/posts/react-re-renders-guide)
- [How to Prevent Re-renders in React Components in 2025 - DEV Community](https://dev.to/cristianalex_17/how-to-prevent-re-renders-in-react-components-in-2025-4ea5)
- [React State Management in 2025: What You Actually Need - DeveloperWay](https://www.developerway.com/posts/react-state-management-2025)

---

## 10. Workflow Guardian Integration

### How to Use This Reference

1. **Detection Phase**: When analyzing code changes, scan for patterns in Section 1-7
2. **Pattern Matching**: Identify existing performance patterns in the codebase
3. **Change Analysis**: Compare new code against existing patterns
4. **Checklist Verification**: Use Section 8 checklist for code review
5. **Recommendation**: Flag deviations with specific examples from this guide

### Example Integration

```
DETECTED PATTERN: React.memo used on UserCard component
NEW CODE ADDS: UserStats child component to UserCard
CHECK: Is UserStats also wrapped in memo?
STATUS: VIOLATION - Breaking memoization chain
RECOMMENDATION: Wrap UserStats in React.memo() to match pattern
CODE EXAMPLE: See Section 1.1 "Cascading Re-render Problem"
```

This reference guide ensures workflow-guardian can reliably identify performance pattern violations and provide developers with specific, actionable guidance based on their existing codebase patterns.
