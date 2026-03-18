# React State Management Preservation Patterns for Workflow Guardian

A comprehensive guide to safely add features to React applications without breaking existing state management, providers, and custom hooks. This document covers architectural patterns from two production issue tracker applications.

---

## Table of Contents

1. [Provider Tree Mapping](#1-provider-tree-mapping)
2. [Context Contract Documentation](#2-context-contract-documentation)
3. [State Dependency Graph](#3-state-dependency-graph)
4. [Safe Patterns for Adding State](#4-safe-patterns-for-adding-state)
5. [Dangerous Patterns to Detect](#5-dangerous-patterns-to-detect)
6. [Realtime/Subscription Patterns](#6-realtimesubscription-patterns)
7. [Custom Hook Preservation](#7-custom-hook-preservation)
8. [Migration Patterns](#8-migration-patterns)

---

## 1. Provider Tree Mapping

### Why Provider Order Matters

The React context provider hierarchy creates a **dependency tree**. Providers at the top of the tree can be consumed by all children, but child providers cannot be consumed by parents. Adding a provider in the wrong position creates:

- **Dead providers**: Code that wraps children but is consumed nowhere (wasted renders)
- **Circular dependency issues**: Child providers trying to use parent context that hasn't been initialized
- **Cascading re-renders**: Deeply nested providers re-rendering entire subtrees

### Project 1: Ring Kissht Issue Tracker (Simple Pattern)

**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/App.tsx`

```tsx
function App() {
  return (
    <SimpleAuthProvider>                    {/* Layer 1: Auth (must be first) */}
      <AppRoutes />                         {/* All routes depend on auth context */}
    </SimpleAuthProvider>
  );
}
```

**Analysis**:
- **Single provider**: Minimal state surface
- **Auth-first pattern**: All routing depends on `SimpleAuthProvider`
- **No component providers**: Theme, ui state, etc. not shared
- **Strength**: Easy to understand, no provider coupling
- **Weakness**: Can't share non-auth state across routes

**How it works**:
1. `SimpleAuthProvider` initializes with `localStorage` check (side effect in provider)
2. `AppRoutes` uses `useSimpleAuth()` to read `isAuthenticated` and `role`
3. `ProtectedRoute` wraps page components, gates access based on role

### Project 2: LOS Issue Tracker (Layered Pattern)

**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/App.tsx`

```tsx
function App() {
  return (
    <ErrorBoundary>                         {/* Layer 1: Error isolation */}
      <AuthProvider>                        {/* Layer 2: Auth (critical) */}
        <ToastProvider>                     {/* Layer 3: Notifications */}
          <CommandPaletteProvider>          {/* Layer 4: Global search */}
            <AppContent />                  {/* All features depend on stack above */}
          </CommandPaletteProvider>
        </ToastProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
```

**Analysis**:

| Layer | Component | Dependencies | Consumers | Initialization |
|-------|-----------|--------------|-----------|-----------------|
| 1 | `ErrorBoundary` | None | Everything | Sync (constructor) |
| 2 | `AuthProvider` | None | AppContent | Async (useEffect + Supabase) |
| 3 | `ToastProvider` | Auth (via contexts) | Header, pages | Sync (local state) |
| 4 | `CommandPaletteProvider` | Auth (registerCommands uses useAuth) | Header | Sync (local state) |

**Critical dependency**: Layer 4 (`CommandPaletteProvider`) uses `useAuth()` in `Header`:

```tsx
function Header() {
  const { currentUser, logout } = useAuth();  // Must be inside AuthProvider!
  const { open: openCommandPalette, registerCommands } = useCommandPalette();

  useEffect(() => {
    if (!currentUser) return;
    const actionCommands = createActionCommands({ logout });
    registerCommands(actionCommands);  // Depends on both contexts
    return () => unregisterCommands(actionCommands.map(c => c.id));
  }, [currentUser, logout, registerCommands, unregisterCommands]);

  // ...
}
```

**If you moved CommandPaletteProvider above AuthProvider**:
```tsx
// BROKEN! CommandPaletteProvider > AuthProvider
<CommandPaletteProvider>
  <AuthProvider>
    <Header />  // Header tries useAuth() - works, but...
  </AuthProvider>
</CommandPaletteProvider>
```

What breaks:
- `registerCommands()` called in Header's effect
- Header hasn't mounted yet when CommandPalette initializes
- Timing-sensitive race conditions in command registration
- `useAuth()` works but context initialization order is wrong

### Provider Tree Mapping Checklist

When adding a new provider, document:

```markdown
## NewProvider

**Position in tree**: [BEFORE/AFTER which provider]
**Initialization type**: Sync | Async | Both
**Dependencies**: [List of contexts it consumes with useContext]
**Consumed by**: [Components/providers that use this context]
**Side effects**: [useEffect, subscriptions, etc.]

### Dependency visualization:
```
ErrorBoundary
├─ AuthProvider (async Supabase, session check)
│  ├─ ToastProvider (sync, no deps)
│  │  └─ CommandPaletteProvider (sync, uses useAuth in Header)
│  │     └─ AppContent
```

### Data flow:
- AuthProvider initializes → sets loading=false
- Header mounts → useAuth() reads currentUser
- Header registers commands → CommandPalette stores them

**NEVER** place a provider that consumes another context ABOVE its dependency.

---

## 2. Context Contract Documentation

### What is a "Context Contract"?

A contract is the **interface** a context exposes:
- What state it holds
- What methods it provides
- What components consume it
- What triggers re-renders
- What can be safely extended without breaking consumers

### Project 1: SimpleAuthContext

**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/contexts/SimpleAuthContext.tsx`

```tsx
interface SimpleAuthContextType {
  role: UserRole | null;                    // Auth state
  isAuthenticated: boolean;                 // Auth state
  login: (role: UserRole, password: string) => Promise<boolean>;  // Action
  logout: () => void;                       // Action
}
```

**Contract breakdown**:

| Member | Type | Consumers | Triggers Re-render | Safe to Extend? |
|--------|------|-----------|-------------------|-----------------|
| `role` | State | `AppRoutes`, `ProtectedRoute`, `ProductSupportDashboard` | Any role change | Yes - add new role type in UserRole union |
| `isAuthenticated` | State | `AppRoutes`, conditional rendering | Login/logout | No - toggle-only, no states between |
| `login()` | Action | `LoginPage` form submission | Sets state internally | Yes - add params, ensure backward compat |
| `logout()` | Action | Multiple header buttons | Clears all state | Yes - add cleanup steps |

**Implementation details**:

```tsx
export function SimpleAuthProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<UserRole | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialization: localStorage persistence
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const { role: storedRole } = JSON.parse(stored);
        if (storedRole === 'sm' || storedRole === 'tech_support_team' || storedRole === 'product_support') {
          setRole(storedRole);
          setIsAuthenticated(true);  // Always set both
        }
      } catch (error) {
        console.error('Failed to parse stored auth:', error);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setLoading(false);
  }, []);

  // ...
}
```

**Key observations**:
1. **Dual state**: `role` AND `isAuthenticated` must stay in sync
2. **Synchronized mutations**: `login()` sets both, `logout()` clears both
3. **Persistence layer**: localStorage is the source of truth on mount
4. **Error handling**: Try-catch on parse, removes invalid stored data

**Consumers**:
- `AppRoutes` - read role for routing decisions
- `ProtectedRoute` - read isAuthenticated for access control
- `LoginPage` - call login()
- Multiple - call logout()

**Safe extension example**:
```tsx
// SAFE: Add new method that calls existing setters
const loginAsGuest = async () => {
  setRole('guest');
  setIsAuthenticated(true);
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ role: 'guest' }));
};

// SAFE: Add new state alongside existing
const [sessionExpiry, setSessionExpiry] = useState<number | null>(null);

// SAFE: Add new computed value
const isAdmin = role === 'admin';

// DANGEROUS: Remove or rename existing context members
// const getRole = () => role;  // Changes contract!
```

### Project 2: AuthContext (Advanced)

**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/context/AuthContext.tsx`

```tsx
interface AuthContextType {
  currentUser: User | null;                      // State
  loading: boolean;                              // State
  authError: string | null;                      // State
  signInWithGoogle: () => Promise<void>;         // Action
  logout: () => Promise<void>;                   // Action
}
```

**Contract breakdown**:

| Member | Type | Initialization | Consumers | Invalidates | Re-render triggers |
|--------|------|---|-----------|-----------|-------------------|
| `currentUser` | State | Async (Supabase session check) | Header, AppContent, pages | logout() | New user logged in, role changed |
| `loading` | State | Derived from session check | AppContent (shows spinner) | Once per mount | Internal boolean toggle |
| `authError` | State | Null initially | LoginScreen (shows error msg) | logout() | signInWithGoogle() failure |
| `signInWithGoogle()` | Action | Async (OAuth redirect) | LoginScreen button | N/A | Sets loading, currentUser |
| `logout()` | Action | Async (Supabase signOut) | Header button, validation | N/A | Clears currentUser |

**Advanced features in this context**:

1. **Caching strategy** (preserves state across page reloads):
```tsx
function getCachedRole(email: string): { role: 'product_support' | 'admin'; name: string | null } | null {
  try {
    const raw = localStorage.getItem(ROLE_CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed.email === email.toLowerCase() && Date.now() - parsed.ts < CACHE_TTL_MS) {
      return { role: parsed.role, name: parsed.name };
    }
  } catch { /* ignore */ }
  return null;
}
```

**Why this matters for preservation**:
- Consumers expect instant re-hydration on mount
- Cache invalidation happens on logout (must call `clearCachedRole()`)
- Background revalidation doesn't re-render if cache is still valid

2. **Concurrency guards** (prevents race conditions):
```tsx
const processingRef = useRef(false);  // Track async processing
const resolvedEmailRef = useRef<string | null>(null);  // Track last resolved user

const handleSignedIn = useCallback(async (supabaseUser: SupabaseUser) => {
  // Prevent concurrent duplicate processing
  if (processingRef.current) {
    perfLog('handleSignedIn:skipped-processing');
    return;  // Silently skip duplicate call
  }

  const email = (supabaseUser.email || '').toLowerCase();

  // Skip re-processing if we already resolved this user
  if (resolvedEmailRef.current === email) {
    perfLog('handleSignedIn:skipped-already-resolved', { email });
    return;
  }

  // ... rest of processing
}, []);
```

**Consumers relying on this**:
- Pages can call async actions without checking if they're already in flight
- Multiple OAuth callbacks don't cause duplicate Supabase queries
- Cached values stay consistent across re-renders

3. **Subscription cleanup** (prevents memory leaks):
```tsx
const { data: { subscription } } = supabase.auth.onAuthStateChange(
  (event, session) => {
    // Sync handler (no async inside callback)
    perfLog('AuthProvider:onAuthStateChange', { event, hasSession: !!session });
    if (cancelled) return;  // Respect cleanup flag
    // ...
  }
);

return () => {
  cancelled = true;
  clearTimeout(safetyTimeout);
  subscription.unsubscribe();  // Must clean up Supabase listener
};
```

**Contract commitment**:
- Subscription is internal (consumers don't see it)
- Cleanup is guaranteed on unmount
- `cancelled` flag prevents state updates after unmount

### GoogleDriveContext (Conditional Feature)

**File**: `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/contexts/GoogleDriveContext.tsx`

```tsx
interface GoogleDriveContextType {
  isConfigured: boolean;        // Feature enabled?
  isInitialized: boolean;       // Gapi ready?
  isSignedIn: boolean;          // User signed in?
  isLoading: boolean;           // Loading state
  error: string | null;         // Error message
  signIn: () => Promise<void>;  // Auth action
  signOut: () => void;          // Unauth action
}
```

**Special pattern**: Feature flag in context

```tsx
const [isConfigured] = useState(isGoogleDriveConfigured());  // Read once on mount

useEffect(() => {
  if (!isConfigured) {  // If feature disabled, skip all setup
    setIsLoading(false);
    return;
  }

  // Otherwise, initialize...
}, [isConfigured]);
```

**Consumers can handle disabled features gracefully**:
```tsx
const { isConfigured } = useGoogleDrive();
if (!isConfigured) {
  return null;  // Don't show drive features
}
```

**Contract**:
- `isConfigured` never changes (determined at provider mount)
- If disabled, all other state stays at defaults
- No consumers need to handle initialization complexity

---

## 3. State Dependency Graph

### What is a Dependency Graph?

When Context A depends on Context B, and Component X depends on Context A, the full chain is:
```
Context B (upstream)
  ↓ (Context A reads it)
Context A
  ↓ (Component uses it)
Component X
```

Breaking any link in the chain breaks the whole system.

### Project 1: Ring Kissht (Simple Graph)

```
SimpleAuthContext (auth state)
├─ AppRoutes (reads: isAuthenticated, role)
│  └─ ProtectedRoute (reads: allowedRoles, checks context)
│     └─ Page components (Layout)
│
├─ LoginPage (calls: login())
└─ (various) logout button (calls: logout())
```

**If you add a new provider that depends on auth**:

```tsx
// WRONG position - will break if it tries to use useAuth()
function App() {
  return (
    <NewFeatureProvider>         {/* Too early - useAuth() will error */}
      <SimpleAuthProvider>       {/* Auth not initialized yet */}
        <AppRoutes />
      </SimpleAuthProvider>
    </NewFeatureProvider>
  );
}

// RIGHT position
function App() {
  return (
    <SimpleAuthProvider>
      <NewFeatureProvider>       {/* Auth ready, can use useAuth() */}
        <AppRoutes />
      </NewFeatureProvider>
    </SimpleAuthProvider>
  );
}
```

### Project 2: LOS Issue Tracker (Complex Graph)

```
ErrorBoundary
├─ AuthProvider
│  ├─ ToastProvider (no auth dependency)
│  │
│  ├─ CommandPaletteProvider
│  │  └─ Header (uses: useAuth() + useCommandPalette())
│  │     └─ registerCommands() (called by Header, stored by CommandPalette)
│  │
│  └─ AppContent
│     ├─ ProductSupportView
│     │  └─ useTickets() (calls: supabase from context)
│     │     └─ subscribeToChanges() (realtime subscription)
│     │
│     └─ AdminView
│        └─ useTickets() (same hook)
│
└─ useKeyboardShortcuts() (custom hook, no context)
└─ useDarkMode() (custom hook, localStorage only)
```

**Critical dependency chain** - when Header mounts:

1. **AuthProvider renders** → reads Supabase session, sets currentUser
2. **CommandPaletteProvider renders** → initializes context, waits for first registerCommands
3. **Header renders** → calls useAuth() (gets currentUser), gets useCommandPalette()
4. **Header useEffect fires** → calls registerCommands(createActionCommands({ logout }))
5. **CommandPalette stores commands** → ready for Ctrl+K search

**If you moved CommandPaletteProvider above AuthProvider**:

```tsx
// WRONG - breaks command registration timing
<CommandPaletteProvider>
  <AuthProvider>
    <Header />
  </AuthProvider>
</CommandPaletteProvider>

// What happens:
// 1. CommandPaletteProvider initializes (no commands yet)
// 2. AuthProvider starts async session check
// 3. Header tries to render (might render before auth is ready)
// 4. useAuth() is inside AuthProvider, so it works technically
// 5. BUT: Header's useEffect fires immediately, calls registerCommands
// 6. Which commands are registered? Only the ones available before auth checks

// Result: LogOut command might not register correctly, timing is fragile
```

**Safe new feature integration example**:

Suppose you want to add `NotificationPreferencesProvider` that lets users customize toast behavior:

```tsx
// Dependency analysis:
// - Depends on: Auth (need currentUser.id to load preferences)
// - Consumed by: ToastProvider (reads user's notification settings)
// - Initialization: Async (fetch from DB)

// Correct positioning:
<ErrorBoundary>
  <AuthProvider>
    <NotificationPreferencesProvider>  {/* After Auth! */}
      <ToastProvider>                   {/* Uses NotificationPrefs */}
        <CommandPaletteProvider>
          <AppContent />
        </CommandPaletteProvider>
      </ToastProvider>
    </NotificationPreferencesProvider>
  </AuthProvider>
</ErrorBoundary>

// Wrong positioning:
<ErrorBoundary>
  <NotificationPreferencesProvider>    {/* Too early! */}
    <AuthProvider>                      {/* Not initialized yet */}
      <ToastProvider>
        // ...
      </ToastProvider>
    </AuthProvider>
  </NotificationPreferencesProvider>
</ErrorBoundary>
```

### Detecting Circular Dependencies

A circular dependency is when:
- Context A depends on Context B
- Context B depends on Context A
- Or: A → B → C → A

**Example that creates a cycle**:

```tsx
// BAD: AuthContext tries to show toast notifications
export function AuthProvider({ children }: { children: ReactNode }) {
  const { showToast } = useToast();  // ERROR: ToastProvider is a child!

  // ...
}

// This creates: AuthProvider → depends on → ToastProvider
//               But ToastProvider is inside AuthProvider
//               = circular dependency, runtime error
```

**How to fix**:
1. Move ToastProvider above AuthProvider, OR
2. Move auth error handling to a component inside ToastProvider, OR
3. Use a separate error channel (modal, fallback UI) that doesn't depend on Toast

---

## 4. Safe Patterns for Adding State

### Pattern A: Add to Existing Context (Extending)

**Rule**: Only add state that logically belongs with existing state.

**Good candidates**:
- Authentication-related: `sessionExpiry`, `authProvider`, `lastLoginTime`
- Presentation of existing data: `selectedRole` (for admin view), `authErrors`
- Flags for existing features: `rememberMe`, `autoLogin`

**Example from SimpleAuthContext**:

```tsx
// SAFE extension - add password change functionality
const [passwordChangeError, setPasswordChangeError] = useState<string | null>(null);

const changePassword = async (oldPassword: string, newPassword: string): Promise<boolean> => {
  try {
    setPasswordChangeError(null);
    // Verify old password, update to new
    // ...
    return true;
  } catch (err) {
    setPasswordChangeError(err instanceof Error ? err.message : 'Failed to change password');
    return false;
  }
};

// Update context type
interface SimpleAuthContextType {
  // ... existing
  passwordChangeError: string | null;
  changePassword: (oldPassword: string, newPassword: string) => Promise<boolean>;
}
```

**When NOT to extend**:
- State belongs to a different domain (theme, notifications, etc.)
- Consumer count is low (only 1-2 components use it)
- The state is temporary/UI-only
- The new state depends on other contexts

### Pattern B: Create New Context (Right Position)

**Rule**: Place new context AFTER all contexts it depends on.

**Decision tree**:

```
Does your new state depend on Auth?
├─ YES: Place AFTER AuthProvider
│  └─ Does it also depend on Toast/Notifications?
│     ├─ YES: Place AFTER ToastProvider
│     └─ NO: Place RIGHT AFTER AuthProvider
│
└─ NO: Does it depend on any existing context?
   ├─ YES: Place AFTER that context
   └─ NO: Can place anywhere (near related code)
```

**Example: Adding ThemeContext to LOS Issue Tracker**

Project 2 already has `useDarkMode()` hook (no context provider). To centralize theme state:

```tsx
// Step 1: Create new context file
// context/ThemeContext.tsx

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    return (localStorage.getItem('app-theme') as Theme) || 'system';
  });

  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Apply theme to DOM
    // Watch system preference changes
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('app-theme', newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, isDark }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}

// Step 2: Update App.tsx (position AFTER ErrorBoundary, but placement flexible)

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>                 {/* New, no dependencies */}
        <AuthProvider>
          <ToastProvider>
            <CommandPaletteProvider>
              <AppContent />
            </CommandPaletteProvider>
          </ToastProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

// Alternative placement (if theme changes need to toast notifications):
function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ToastProvider>
          <ThemeProvider>              {/* After Toast */}
            <CommandPaletteProvider>
              <AppContent />
            </CommandPaletteProvider>
          </ThemeProvider>
        </ToastProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
```

**Step 3: Verify no circular dependencies**:
- ThemeProvider uses: localStorage (no context)
- Consumers of ThemeProvider: Header, components (no circular path)
- Safe ✓

### Pattern C: Convert Local State to Shared State

**When**: Multiple components duplicate the same state logic, or a component needs to expose state to siblings/cousins.

**Example from Project 2**: Multiple views need ticket data

**Before** (local state in each view):

```tsx
export function AdminView() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    const data = await supabase.from('tickets').select('*');
    setTickets(data || []);
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchTickets();
    const unsub = subscribeToChanges(fetchTickets);
    return unsub;
  }, []);

  // ... render tickets
}

export function ProductSupportView() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);

  // ... duplicate logic
}
```

**After** (shared hook + context):

```tsx
// Create custom hook that encapsulates logic (NOT a context, just a hook)
export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);

  const fetchOpenTickets = useCallback(async (page = 0) => {
    const from = page * PAGE_SIZE;
    const to = from + PAGE_SIZE - 1;
    const { data, error: err } = await supabase
      .from('tickets')
      .select('*')
      .eq('status', 'open')
      .order('submitted_at', { ascending: true })
      .range(from, to);

    if (err) throw err;
    const results = data || [];
    if (page === 0) {
      setTickets(results);
    } else {
      setTickets(prev => [...prev, ...results]);
    }
    return results;
  }, []);

  const subscribeToChanges = useCallback((callback, userEmail?, userRole?) => {
    const channelName = `tickets-${crypto.randomUUID()}`;
    const filter = userRole === 'product_support' && userEmail
      ? { event: '*', schema: 'public', table: 'tickets', filter: `submitted_by=eq.${userEmail}` }
      : { event: '*', schema: 'public', table: 'tickets' };

    const subscription = supabase
      .channel(channelName)
      .on('postgres_changes', filter, () => callback())
      .subscribe();

    return () => subscription.unsubscribe();
  }, []);

  return {
    tickets,
    fetchOpenTickets,
    subscribeToChanges,
    // ... other methods
  };
}

// Use in components
export function AdminView() {
  const { tickets, fetchOpenTickets, subscribeToChanges } = useTickets();

  useEffect(() => {
    fetchOpenTickets();
    return subscribeToChanges(() => fetchOpenTickets(0));
  }, []);

  // ... render tickets
}

export function ProductSupportView() {
  const { currentUser } = useAuth();
  const { tickets, fetchMySubmittedTickets, subscribeToChanges } = useTickets();

  useEffect(() => {
    fetchMySubmittedTickets(currentUser!.email);
    return subscribeToChanges(() => fetchMySubmittedTickets(currentUser!.email), currentUser!.email, 'product_support');
  }, [currentUser]);

  // ... render tickets
}
```

**Key insight**: `useTickets()` is a **custom hook**, not a provider. It:
- Can be called multiple times per component tree (each gets own instance)
- Can depend on `useAuth()` without creating context nesting issues
- Can have local state that's not shared globally
- Provides a **contract** (interface) that consumers rely on

**When to create context vs. custom hook**:

| Aspect | Custom Hook | Context + Provider |
|--------|-------------|-------------------|
| **Shared instance** | One per component | One per provider tree |
| **Dependencies** | Can use other hooks | Can use other contexts |
| **Dependency injection** | Via hook params | Via provider nesting |
| **Data persistence** | Per-component refs | Across re-renders (shared) |
| **Use case** | Logic encapsulation | Global state sharing |

### Pattern D: Derived/Computed State

**Rule**: Computed values that don't need re-renders should be memoized; those that do should be in state.

**Example from AuthContext**:

```tsx
// DERIVED: Compute from existing state, no storage needed
const isLoading = loading;  // Just read from state
const userInitial = currentUser?.name.charAt(0).toUpperCase();  // Compute on render

// IN PROJECT 2:
function Header() {
  const { currentUser } = useAuth();

  // Computed inline (cheap)
  const userInitial = currentUser?.name.charAt(0).toUpperCase();

  return (
    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
      <span className="text-sm font-medium">{userInitial}</span>
    </div>
  );
}

// SAFER: Use useMemo if computation is expensive
function ExpensiveComponent() {
  const { tickets } = useTickets();

  const summedAmount = useMemo(() => {
    // Expensive calculation
    return tickets.reduce((sum, t) => sum + (t.amount || 0), 0);
  }, [tickets]);

  return <div>{summedAmount}</div>;
}

// In useDarkMode hook:
export function useDarkMode() {
  const [theme, setThemeState] = useState<Theme>(() => getStoredTheme());
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>(() => {
    const stored = getStoredTheme();
    return stored === 'system' ? getSystemTheme() : stored;
  });

  // resolvedTheme is DERIVED: computed from theme + system preference
  // But stored separately because it changes when system preference changes
  // It's STATE (re-renders when it changes) not just a computed value

  useEffect(() => {
    applyTheme(theme);
    setResolvedTheme(theme === 'system' ? getSystemTheme() : theme);
  }, [theme]);

  useEffect(() => {
    if (theme !== 'system') return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      setResolvedTheme(e.matches ? 'dark' : 'light');
    };
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  return { theme, resolvedTheme, isDark: resolvedTheme === 'dark', /* ... */ };
}
```

**Computed state rule**:
- If it changes independently (system theme preference), it needs its own state
- If it's only computed from existing state (initials, derived flags), compute inline
- If computation is expensive, use `useMemo`

---

## 5. Dangerous Patterns to Detect

### Pattern 1: Duplicated State Across Contexts

**Problem**: Same state stored in two places, out of sync.

**Example (DANGEROUS)**:

```tsx
// AuthContext
const [currentUser, setCurrentUser] = useState<User | null>(null);

// NEW: NotificationContext (WRONG)
const [currentUserId, setCurrentUserId] = useState<string | null>(null);  // DUPLICATE!

// In a component:
function AdminPanel() {
  const { currentUser } = useAuth();
  const { currentUserId } = useNotifications();

  // Are they the same? Depends on sync logic
  // What if auth completes before notification context initializes?
  // currentUser is set, but currentUserId is still null
}
```

**Why it's dangerous**:
- Race conditions during initialization
- One context updates, the other doesn't
- Hard to debug (state appears to change spontaneously)
- Multiple sources of truth

**Fix**:

```tsx
// Option 1: Derive from source of truth
export function useNotifications() {
  const { currentUser } = useAuth();  // Get from single source

  // Use currentUser here, don't duplicate
  const notifications = fetchNotifications(currentUser?.id);
}

// Option 2: Pass data from parent to child context
<AuthProvider>
  <NotificationProvider currentUser={currentUser}>
    <App />
  </NotificationProvider>
</AuthProvider>
```

### Pattern 2: Creating Circular Context Dependencies

**Problem**: Context A uses Context B, Context B uses Context A.

**Example (DANGEROUS)**:

```tsx
// AuthContext uses ToastContext
export function AuthProvider({ children }: { children: ReactNode }) {
  const { showToast } = useToast();  // CIRCULAR if ToastProvider is a child!

  useEffect(() => {
    // ...
    if (error) {
      showToast(error);  // Trying to use Toast while it's initializing
    }
  }, []);
}

// App.tsx
function App() {
  return (
    <AuthProvider>
      <ToastProvider>      {/* Can't use this inside AuthProvider! */}
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}
```

**Why it's dangerous**:
- ToastProvider hasn't initialized yet when AuthProvider tries to use it
- Runtime error: "useToast must be used within ToastProvider"
- Confusing dependency direction (parent depends on child)

**Fix**:

```tsx
// Option 1: Move ToastProvider above
function App() {
  return (
    <ToastProvider>        {/* Now AuthProvider can use useToast() */}
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ToastProvider>
  );
}

// Option 2: Handle errors without Toast in AuthProvider
// Show errors in component instead
export function LoginScreen() {
  const { authError, signInWithGoogle } = useAuth();
  const { showToast } = useToast();

  useEffect(() => {
    if (authError) {
      showToast({ type: 'error', message: authError });
    }
  }, [authError]);
}

// Option 3: Create shared error context that doesn't use Toast
const GlobalErrorContext = createContext(null);  // No Toast dependency
```

### Pattern 3: Adding State That Should Be Derived

**Problem**: Computing and storing a value that can be derived from existing state.

**Example (DANGEROUS)**:

```tsx
// In useTickets hook
const [tickets, setTickets] = useState<Ticket[]>([]);
const [isLoading, setIsLoading] = useState(false);
const [ticketCount, setTicketCount] = useState(0);  // DERIVED!
const [highPriorityCount, setHighPriorityCount] = useState(0);  // DERIVED!

const fetchTickets = useCallback(async () => {
  const results = await supabase.from('tickets').select('*');
  setTickets(results);
  setTicketCount(results.length);  // Computed from tickets!
  setHighPriorityCount(results.filter(t => t.priority === 'high').length);
}, []);

// Component:
function Dashboard() {
  const { tickets, ticketCount, isLoading } = useTickets();

  // Which is source of truth?
  // If tickets changes but ticketCount isn't updated, they're out of sync
}
```

**Why it's dangerous**:
- Synchronization burden: must update multiple states together
- Accidental stale data: forgot to update derived state
- Double rendering: update tickets, then derived state re-renders
- Hard to understand: which state is the source of truth?

**Fix**:

```tsx
export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchTickets = useCallback(async () => {
    const results = await supabase.from('tickets').select('*');
    setTickets(results);
    setIsLoading(false);
  }, []);

  return {
    tickets,
    isLoading,
    // Derived values (computed on render or in useMemo)
    ticketCount: tickets.length,
    highPriorityCount: tickets.filter(t => t.priority === 'high').length,
    hasHighPriority: tickets.some(t => t.priority === 'high'),
  };
}

// Component can compute too:
function Dashboard() {
  const { tickets, isLoading } = useTickets();

  // Derive locally if only used here
  const ticketCount = tickets.length;
  const highPriorityCount = tickets.filter(t => t.priority === 'high').length;
}
```

### Pattern 4: Breaking Provider Order

**Problem**: Moving providers changes initialization order, breaking dependencies.

**Example (DANGEROUS)**:

```tsx
// WRONG ORDER
function App() {
  return (
    <CommandPaletteProvider>        {/* Initializes first */}
      <AuthProvider>                {/* Initializes second */}
        <AppContent />              {/* Tries to register commands in Header */}
      </AuthProvider>               {/* But CommandPalette is already done initializing */}
    </CommandPaletteProvider>
  );
}

// What breaks:
// 1. CommandPaletteProvider initializes context (no commands registered yet)
// 2. AuthProvider starts async session check
// 3. Header renders (inside AuthProvider)
// 4. Header useEffect fires → registerCommands()
// 5. CommandPalette stores commands (but initialization race is now fragile)
```

**How to detect it**:

1. **Check providers for useContext calls**:
   ```tsx
   grep -r "useAuth()" src/  # Find all auth consumers
   grep -r "useToast()" src/  # Find all toast consumers
   ```

2. **Map initialization order**:
   ```
   App.tsx shows:
   <ErrorBoundary>
     <AuthProvider>      ← initializes with useEffect
       <ToastProvider>   ← initializes synchronously
         <CommandPaletteProvider>  ← uses useAuth() in Header
   ```

3. **For each context that uses another context, ensure parent comes first**

### Pattern 5: Over-Rendering from Poorly Structured Contexts

**Problem**: Context value object is recreated every render, causing all consumers to re-render.

**Example (DANGEROUS)**:

```tsx
// BAD: Value object created every render
export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  // Created fresh every render!
  const value = {
    currentUser,
    loading,
    signInWithGoogle: async () => { /* ... */ },
    logout: async () => { /* ... */ },
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Result: Every child re-renders when provider re-renders, even if state didn't change
```

**How it breaks**:
- Provider re-renders for any reason (parent update, etc.)
- Value object is new (different reference)
- React Context compares `oldValue === newValue`
- They're not equal, so all consumers re-render
- Header re-renders, which calls registerCommands again
- Expensive computations run unnecessarily

**Fix**:

```tsx
export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  // Use useMemo to keep same reference if deps didn't change
  const value = useMemo(
    () => ({
      currentUser,
      loading,
      signInWithGoogle: async () => { /* ... */ },
      logout: async () => { /* ... */ },
    }),
    [currentUser, loading]  // Only recreate if these change
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Even better: separate state and actions
const AuthStateContext = createContext<{ currentUser: User | null; loading: boolean } | undefined>(undefined);
const AuthActionsContext = createContext<{ signInWithGoogle: () => Promise<void>; logout: () => Promise<void> } | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  const stateValue = useMemo(
    () => ({ currentUser, loading }),
    [currentUser, loading]
  );

  const actionsValue = useMemo(
    () => ({
      signInWithGoogle: async () => { /* ... */ },
      logout: async () => { /* ... */ },
    }),
    []  // Actions never change
  );

  return (
    <AuthStateContext.Provider value={stateValue}>
      <AuthActionsContext.Provider value={actionsValue}>
        {children}
      </AuthActionsContext.Provider>
    </AuthStateContext.Provider>
  );
}
```

---

## 6. Realtime/Subscription Patterns

### Subscription Lifecycle

From `useTickets()` hook in Project 2:

```tsx
const subscribeToChanges = useCallback(
  (callback: () => void, userEmail?: string, userRole?: string) => {
    // Step 1: Create unique channel
    const channelName = `tickets-${crypto.randomUUID()}`;

    // Step 2: Configure filter based on user role
    const filter =
      userRole === 'product_support' && userEmail
        ? { event: '*' as const, schema: 'public', table: 'tickets', filter: `submitted_by=eq.${userEmail}` }
        : { event: '*' as const, schema: 'public', table: 'tickets' };

    // Step 3: Create subscription
    const subscription = supabase
      .channel(channelName)
      .on('postgres_changes', filter, () => {
        callback();  // Call provided callback when change happens
      })
      .subscribe((status, err) => {
        // Step 4: Handle subscription status
        if (status === 'TIMED_OUT' || status === 'CHANNEL_ERROR') {
          console.error('Realtime subscription error:', status, err);
        }
      });

    // Step 5: Return cleanup function
    return () => {
      subscription.unsubscribe();
    };
  },
  []
);
```

**Lifecycle in a component**:

```tsx
export function AdminView() {
  const { tickets, fetchMyClaimedTickets } = useTickets();
  const { currentUser } = useAuth();

  useEffect(() => {
    // MOUNT: Fetch initial data and subscribe
    if (currentUser) {
      fetchMyClaimedTickets(currentUser.name);

      // Subscribe to changes
      const unsubscribe = subscribeToChanges(
        () => fetchMyClaimedTickets(currentUser.name),
        currentUser.email,
        currentUser.role
      );

      // UNMOUNT: Cleanup subscription
      return () => {
        unsubscribe();  // Must call cleanup function
      };
    }
  }, [currentUser, fetchMyClaimedTickets, subscribeToChanges]);

  return (
    // Render tickets
  );
}
```

### Channel Naming Strategy

From Project 2:

```tsx
// GOOD: Unique channel per subscription
const channelName = `tickets-${crypto.randomUUID()}`;

// BAD: Static channel name, multiple subscriptions collide
const channelName = 'tickets-all';  // Two components = two subscriptions, same channel
// Risk: message loss, subscription conflicts
```

**Why unique channels matter**:
- Supabase client can have multiple subscriptions
- Each subscription should have its own channel
- Multiple subscriptions to same channel can cause message loss
- Use UUIDs or timestamp + component ID

### Filtering Strategy

From Project 2:

```tsx
// Scenario: Product support user sees only their own tickets
const filter =
  userRole === 'product_support' && userEmail
    ? { event: '*' as const, schema: 'public', table: 'tickets', filter: `submitted_by=eq.${userEmail}` }
    : { event: '*' as const, schema: 'public', table: 'tickets' };

// Result:
// - Admins: subscribe to ALL tickets changes
// - Support staff: subscribe to ONLY tickets they submitted
// - Database only sends relevant changes to client
```

**Rules**:
- Filter at the database level (Supabase Realtime)
- Don't subscribe to everything then filter in JS
- Use PostgREST filter syntax: `column=eq.value`, `column=gt.value`, etc.

### Error Handling for Dropped Connections

From Project 2:

```tsx
const subscription = supabase
  .channel(channelName)
  .on('postgres_changes', filter, () => {
    callback();
  })
  .subscribe((status, err) => {
    // Handle subscription lifecycle events
    if (status === 'TIMED_OUT') {
      // Connection attempt timed out
      console.error('Realtime subscription timed out:', err);
      // Could retry with exponential backoff
    } else if (status === 'CHANNEL_ERROR') {
      // Channel-level error
      console.error('Realtime channel error:', err);
      // Could show user notification
    }
    // Other statuses: SUBSCRIBED, UNSUBSCRIBED, etc.
  });
```

**Preservation rule**: When adding realtime features:

1. **Document subscription lifecycle** in component:
   ```tsx
   // Subscription lifecycle:
   // 1. useEffect mount: subscribe with current user's preferences
   // 2. useEffect cleanup: unsubscribe to prevent memory leak
   // 3. If currentUser changes: re-subscribe with new user's filter
   ```

2. **Ensure cleanup is called**:
   ```tsx
   useEffect(() => {
     const unsub = subscribeToChanges(callback);
     return () => unsub();  // MUST NOT forget
   }, [/* dependencies */]);
   ```

3. **Handle dependency changes**:
   ```tsx
   // If filter depends on user, re-subscribe when user changes
   useEffect(() => {
     if (!currentUser) return;
     const unsub = subscribeToChanges(callback, currentUser.email, currentUser.role);
     return () => unsub();
   }, [currentUser, callback]);  // currentUser in dependency array
   ```

4. **Consider subscription costs**:
   - Each subscription = open websocket
   - Too many subscriptions = memory leak
   - Reuse subscriptions across components if possible

### Non-blocking Fire-and-Forget Patterns

From Project 2 `useTickets.ts`:

```tsx
const createTicket = useCallback(async (ticketData: CreateTicketData): Promise<Ticket | null> => {
  try {
    const { data, error: err } = await supabase
      .from('tickets')
      .insert([{ /* ... */ }])
      .select()
      .single();

    if (err) throw err;

    if (data) {
      // ASYNC SYNC: Don't await, don't block UI
      syncToSheets(data as Ticket, 'append').then(result => {
        if (!result.success) {
          console.warn('Sheet sync failed (non-blocking):', result.error);
        }
      }).catch(err => {
        console.warn('Sheet sync error (non-blocking):', err);
      });
    }

    return data;
  } catch (e) {
    console.error('createTicket error:', e);
    return null;
  }
}, []);
```

**Pattern**:
```tsx
// Don't do this (blocks UI):
await syncToSheets(data);

// Do this instead (non-blocking):
syncToSheets(data).then(result => {
  if (!result.success) console.warn(result.error);
}).catch(err => console.warn(err));
```

---

## 7. Custom Hook Preservation

### Hook Interface Contract

A custom hook is a contract that consumers rely on:

```tsx
export function useTickets() {
  // Public interface (what consumers can see)
  const tickets: Ticket[];
  const fetchOpenTickets: (page?: number) => Promise<Ticket[] | null>;
  const createTicket: (data: CreateTicketData) => Promise<Ticket | null>;
  const subscribeToChanges: (callback: () => void, ...) => () => void;

  // Private implementation (internal state/helpers)
  const [tickets, setTickets] = useState([]);
  const PAGE_SIZE = 30;

  return {
    tickets,
    fetchOpenTickets,
    createTicket,
    subscribeToChanges,
  };
}
```

**The contract includes**:
- Return type (what properties/methods are exported)
- Parameter types (what arguments each method accepts)
- Return types of async methods
- Cleanup responsibilities (unsubscribe functions)

### Safe Modifications to Custom Hooks

**SAFE: Add new method**

```tsx
// Before
export function useTickets() {
  return {
    tickets,
    fetchOpenTickets,
    createTicket,
  };
}

// After (adding new functionality)
export function useTickets() {
  // NEW
  const archiveTicket = useCallback(async (ticketId: string) => {
    const { data, error } = await supabase
      .from('tickets')
      .update({ status: 'archived' })
      .eq('id', ticketId)
      .single();

    if (error) throw error;
    return data as Ticket;
  }, []);

  return {
    tickets,
    fetchOpenTickets,
    createTicket,
    archiveTicket,  // NEW - old callers don't use it
  };
}

// Existing consumers unaffected:
const { tickets, fetchOpenTickets } = useTickets();  // Still works
```

**SAFE: Add optional parameter**

```tsx
// Before
const fetchOpenTickets = useCallback(async (page = 0) => {
  // ...
}, []);

// After (optional param)
const fetchOpenTickets = useCallback(async (page = 0, filters?: { status?: string; priority?: 'high' | 'low' }) => {
  let query = supabase.from('tickets').select('*').eq('status', 'open');

  if (filters?.status) {
    query = query.eq('status', filters.status);
  }
  if (filters?.priority) {
    query = query.eq('priority', filters.priority);
  }

  const { data } = await query.range(from, to);
  return data || [];
}, []);

// Old callers still work:
fetchOpenTickets(0);  // Works, filters is optional
// New callers can use:
fetchOpenTickets(0, { status: 'claimed', priority: 'high' });
```

**SAFE: Change internal implementation**

```tsx
// Before (using ref)
const cacheRef = useRef<Map<string, Ticket[]>>(new Map());

// After (using localStorage for persistence across page reloads)
function getCachedTickets(key: string) {
  try {
    const cached = localStorage.getItem(`tickets-cache-${key}`);
    return cached ? JSON.parse(cached) : null;
  } catch { return null; }
}

// External interface unchanged:
const { tickets, fetchOpenTickets } = useTickets();  // Same return type
```

### DANGEROUS: Changes to Hook Contract

**DANGEROUS: Change return type**

```tsx
// Before
return {
  tickets: Ticket[],
  fetchOpenTickets: async (page: number) => Promise<Ticket[] | null>,
};

// After - BREAKS CONSUMERS
return {
  data: Ticket[],  // Renamed from 'tickets'
  fetch: async (page: number) => Promise<Ticket[]>,  // Changed param name
};

// All consumers break:
const { tickets } = useTickets();  // ERROR: tickets is now 'data'
```

**DANGEROUS: Remove or rename parameter**

```tsx
// Before
const createTicket = useCallback(async (ticketData: CreateTicketData) => {
  // ...
}, []);

// After - BREAKS CONSUMERS
const createTicket = useCallback(async (ticketData: CreateTicketData, options?: { skipSheetSync?: boolean }) => {
  // Fine so far - optional param
}, []);

// But this breaks:
const createTicket = useCallback(async (ticketNumber: string) => {  // PARAM CHANGED
  // ...
}, []);

// Consumer:
const result = await createTicket({ ...data });  // ERROR: expects string
```

**DANGEROUS: Change behavior without docs**

```tsx
// Before
const subscribeToChanges = useCallback((callback, userEmail?, userRole?) => {
  // Subscribes to all tickets OR user's tickets (based on role)
  // Returns unsubscribe function
  const unsub = subscription.subscribe();
  return () => unsub();
}, []);

// After - CHANGES BEHAVIOR without notice
const subscribeToChanges = useCallback((callback, userEmail?, userRole?) => {
  // NOW also auto-refetches initial data
  fetchAllTickets();  // Unexpected side effect!

  const unsub = subscription.subscribe();
  return () => unsub();
}, []);

// Consumer expects idempotent subscription, but gets auto-fetch:
useEffect(() => {
  const unsub = subscribeToChanges(callback);
  // Unexpected: component now fetches twice (once in effect, once in subscribe)
}, []);
```

### Hook Dependencies and Memoization

From `useTickets.ts`:

```tsx
export function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);

  const fetchOpenTickets = useCallback(async (page = 0) => {
    // ...
  }, []);  // Empty deps - function never recreated

  const subscribeToChanges = useCallback(
    (callback: () => void, userEmail?: string, userRole?: string) => {
      // ...
    },
    []  // Empty deps - callback stays stable
  );

  return {
    tickets,
    fetchOpenTickets,
    subscribeToChanges,
  };
}

// Consumer:
export function AdminView() {
  const { tickets, fetchOpenTickets, subscribeToChanges } = useTickets();

  useEffect(() => {
    fetchOpenTickets(0);
    const unsub = subscribeToChanges(() => fetchOpenTickets(0));
    return () => unsub();
  }, [fetchOpenTickets, subscribeToChanges]);  // Safe - functions never change
}
```

**Rule**: If your hook returns functions, memoize them so consumers don't re-run effects unnecessarily.

---

## 8. Migration Patterns

### Migration 1: useState → useContext

**Scenario**: Multiple components share theme state, currently each has local state.

**Phase 1: Create Hook**

```tsx
// Before: Each component manages its own theme
function Sidebar() {
  const [isDark, setIsDark] = useState(false);

  const toggleDark = () => setIsDark(!isDark);

  return <button onClick={toggleDark}>Toggle</button>;
}

// After: Extract to hook
export function useDarkMode() {
  const [theme, setThemeState] = useState<Theme>(() => getStoredTheme());
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>(() => {
    const stored = getStoredTheme();
    return stored === 'system' ? getSystemTheme() : stored;
  });

  useEffect(() => {
    applyTheme(theme);
    setResolvedTheme(theme === 'system' ? getSystemTheme() : theme);
  }, [theme]);

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem(STORAGE_KEY, newTheme);
  }, []);

  return { theme, resolvedTheme, isDark: resolvedTheme === 'dark', setTheme, toggleTheme, cycleTheme };
}

// Component:
function Sidebar() {
  const { isDark, toggleTheme } = useDarkMode();
  return <button onClick={toggleTheme}>Toggle</button>;
}
```

**Phase 2: Add Context Provider (Optional)**

```tsx
// If many consumers need the same instance:
interface DarkModeContextValue {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  isDark: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  cycleTheme: () => void;
}

const DarkModeContext = createContext<DarkModeContextValue | null>(null);

export function DarkModeProvider({ children }: { children: ReactNode }) {
  const darkMode = useDarkMode();
  return (
    <DarkModeContext.Provider value={darkMode}>
      {children}
    </DarkModeContext.Provider>
  );
}

export function useDarkModeContext() {
  const context = useContext(DarkModeContext);
  if (!context) throw new Error('useDarkModeContext must be used within DarkModeProvider');
  return context;
}

// App.tsx
function App() {
  return (
    <DarkModeProvider>
      <AppContent />
    </DarkModeProvider>
  );
}

// Component:
function Header() {
  const { isDark, toggleTheme } = useDarkModeContext();
  return <button onClick={toggleTheme}>Toggle</button>;
}
```

**Phase 3: Deprecate Old Pattern**

```tsx
// DEPRECATED
function Sidebar() {
  const [isDark, setIsDark] = useState(false);  // OLD
  // USE useDarkModeContext() INSTEAD
  const { isDark, toggleTheme } = useDarkModeContext();
}
```

**Why phases matter**:
1. **Phase 1**: Works everywhere, consumers can opt-in gradually
2. **Phase 2**: Shared instance for consumers that need it
3. **Phase 3**: Remove old pattern after all consumers migrated

### Migration 2: useContext → External State Management (Zustand/Redux)

**When**: Contexts become too complex, need sophisticated state management (undo/redo, time-travel debugging, etc.)

**Phase 1: Create Store**

```tsx
// Create Zustand store (replacing AuthContext)
import { create } from 'zustand';

interface AuthState {
  // State
  currentUser: User | null;
  loading: boolean;
  authError: string | null;

  // Actions
  setCurrentUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setAuthError: (error: string | null) => void;
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  currentUser: null,
  loading: true,
  authError: null,

  setCurrentUser: (user) => set({ currentUser: user }),
  setLoading: (loading) => set({ loading }),
  setAuthError: (error) => set({ authError: error }),

  signInWithGoogle: async () => {
    set({ loading: true, authError: null });
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: window.location.origin },
      });
      if (error) set({ authError: error.message });
    } finally {
      set({ loading: false });
    }
  },

  logout: async () => {
    await supabase.auth.signOut();
    set({ currentUser: null, authError: null });
  },
}));
```

**Phase 2: Create Adapter Hook**

```tsx
// Adapter hook so existing code still works
export function useAuth() {
  return useAuthStore((state) => ({
    currentUser: state.currentUser,
    loading: state.loading,
    authError: state.authError,
    signInWithGoogle: state.signInWithGoogle,
    logout: state.logout,
  }));
}

// Existing consumers unchanged:
const { currentUser, signInWithGoogle } = useAuth();  // Same interface
```

**Phase 3: Update Initialization**

```tsx
// Store initialization happens once in App
function AppInit() {
  useEffect(() => {
    const unsubscribe = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        // Use store actions instead of context setters
        const { setCurrentUser, setAuthError } = useAuthStore.getState();

        const email = session.user.email || '';
        const result = await fetchAllowedUser(email);

        if (result.status === 'found') {
          const user = buildUser(session.user, result.role, result.name);
          setCurrentUser(user);
          setAuthError(null);
        } else {
          setCurrentUser(null);
          setAuthError('Not authorized');
        }
      }
    });

    return () => unsubscribe();
  }, []);

  return null;
}

function App() {
  return (
    <>
      <AppInit />
      <Header />
      <Main />
    </>
  );
}
```

**Phase 4: Remove Context**

```tsx
// DELETE AuthContext.tsx
// DELETE AuthProvider component
// All code now uses useAuth() hook (backed by Zustand)
```

**Benefits of migration**:
- Better debugging: Zustand DevTools, Redux DevTools
- Simpler state updates: no need for useCallback memoization
- Better code splitting: store initialization separate from rendering
- Easier testing: mock store directly

### Migration 3: Adding Persistence Layer

**Scenario**: User preferences need to persist across sessions.

**Before**: State only lives in component/hook

```tsx
export function useDarkMode() {
  const [theme, setThemeState] = useState<Theme>('light');  // Always resets to 'light'

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
  }, []);

  return { theme, setTheme };
}
```

**After**: Add localStorage persistence

```tsx
export function useDarkMode() {
  const [theme, setThemeState] = useState<Theme>(() => {
    // Initialize from localStorage
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'light' || stored === 'dark' || stored === 'system') {
        return stored;
      }
    } catch { /* ignore */ }
    return 'system';
  });

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    // Persist to localStorage
    try {
      localStorage.setItem(STORAGE_KEY, newTheme);
    } catch { /* quota exceeded or private mode */ }
  }, []);

  return { theme, setTheme };
}
```

**Key rules for safe persistence**:
1. **Initialize from storage** (if available)
2. **Always wrap in try-catch** (private mode, quota exceeded)
3. **Validate stored data** (ensure it's the right type)
4. **Clear on logout** (in auth context, call `localStorage.removeItem(STORAGE_KEY)`)
5. **Don't persist sensitive data** (tokens, passwords, PII)

### Rollback Strategy

When migrating state management, keep ability to rollback:

```tsx
// Keep old context temporarily
export const legacyAuthContext = createContext(null);

// New code uses store
export function useAuth() {
  return useAuthStore();
}

// Old code can still work (if needed)
export function useLegacyAuth() {
  return useContext(legacyAuthContext);
}

// Gradually migrate components:
// 1. New components use useAuth()
// 2. Old components keep using legacyAuth
// 3. Once all migrated, remove legacy code

// If migration breaks something:
// - Revert App.tsx to use AuthProvider instead of store init
// - Old context still there, consumers still work
// - No mass refactoring needed
```

---

## Conclusion

### Checklist for Safe State Management Changes

When modifying state architecture:

- [ ] **Provider tree**: Documented dependencies and order
- [ ] **Context contracts**: What state, methods, consumers
- [ ] **Dependency graph**: All contexts mapped, no circular deps
- [ ] **Safe patterns**: Using appropriate pattern (hook, context, custom hook, store)
- [ ] **Tests**: Updated if state shape changed
- [ ] **Migrations**: Phased approach if major change
- [ ] **Cleanup**: Subscriptions unsubscribed, refs cleared
- [ ] **Memoization**: Functions memoized to prevent child re-renders
- [ ] **Performance**: No over-rendering from context updates
- [ ] **Error handling**: Graceful degradation if context unavailable
- [ ] **Documentation**: What the state means, how to extend it

### Red Flags During Code Review

If you see these patterns, flag them:

1. **Circular dependencies** - Context A uses Context B, Context B uses Context A
2. **Duplicated state** - Same value stored in multiple contexts
3. **Recreated context value** - `value={{ state, method }}` not memoized
4. **Missing cleanup** - useEffect returns nothing, subscriptions leak
5. **Wrong provider order** - Provider uses context from child
6. **Breaking changes** - Hook interface changed without migration
7. **Derived state in state** - Value computed from existing state also stored
8. **Missing error boundaries** - Context initialization failure crashes app

### Key Principles

1. **Source of truth** - One place for each piece of data
2. **Dependency flow** - Always parent to child, never circular
3. **Contract stability** - Don't break consumer interfaces
4. **Graceful degradation** - Features work even if context fails
5. **Clear initialization** - Understand when and where state is ready
6. **Thoughtful composition** - Choose right tool for each state pattern
