# Framework-Specific Gotchas for Workflow Guardian Skill

**Context**: This document captures framework-specific pitfalls and breaking changes relevant to two production React projects:
- **Ring Kissht Issue Tracker**: Firebase + React 18 + Vite 5 + Tailwind v3 + TypeScript (strict)
- **Los Issue Tracker**: Supabase + React 19 + Vite 7 + Tailwind v4 + TypeScript (strict)

These are warnings and defensive observations, not prescriptions for change.

---

## 1. Firebase Gotchas

### Security Rules Updates Required for New Collections

**Problem**: When adding new collections or sub-collections to Firestore, the security rules must be explicitly updated or the new data becomes inaccessible/unwritable.

**Current State** (Ring Kissht Issue Tracker):
```javascript
// firestore.rules - VERY PERMISSIVE (dev/testing)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /submissions/{submissionId} {
      allow read, create, update: if true;
      allow delete: if false;
    }
    match /counters/{counterId} {
      allow read, write: if true;
    }
  }
}
```

**Gotcha**: This allows all reads/writes for existing collections. Any NEW collection (e.g., `issues`, `attachments`, `workflows`, `audit_logs`) must be explicitly added:
```javascript
match /newCollection/{docId} {
  allow read, write: if true; // placeholder - update for production
}
```

**Without explicit rules**: New collections get the default deny policy. Writes will silently fail in the client, creating mysterious bugs.

**Production Risk**: If security rules are too permissive in dev but restrictive in production, the same code path works locally but fails in deployed environment.

---

### Cold Start & Latency with Cloud Functions

**Problem**: Firebase Cloud Functions have cold start delays (up to 10 seconds) on first invocation, especially after deployment.

**Current Setup** (Ring Kissht):
```json
{
  "functions": {
    "source": "functions",
    "predeploy": ["npm --prefix \"$RESOURCE_DIR\" run build"]
  }
}
```

**Gotchas**:
- First request to any function will be slow - users may think the app is broken
- Multiple rapid requests during cold start can timeout before the function initializes
- Concurrent requests are queued until function warms up
- Regional configuration is not visible in firebase.json - check your deployment setup

**Mitigation Approaches** (not prescriptions):
- Keep functions small and focused (smaller = faster cold start)
- Use scheduled functions sparingly
- Consider edge functions/Next.js API routes for low-latency needs

---

### Firestore Index Requirements for Complex Queries

**Problem**: Complex Firestore queries (compound queries with filters and ordering) require composite indexes. The SDK provides helpful errors, but indexes must be created before queries run.

**Observed** (Ring Kissht):
```javascript
// Stored in firestore.indexes.json
// Must be kept in sync with actual queries in code
```

**Gotchas When Adding Features**:
- A query like `where('status', '==', 'active').where('priority', '>', 2).orderBy('createdAt')` requires an auto-generated index
- Firestore provides a direct link in the error message, but requires explicit index creation
- Local emulator auto-creates indexes, production requires manual creation (or UI-based auto-creation if enabled)
- If index creation fails silently, queries will fail in production but work in development

**When Adding New Query Patterns**: Always test in production environment after deployment, or enable auto-index creation in Firestore console.

---

### Firebase Storage Rules Must Match Upload Patterns

**Current State** (Ring Kissht):
```json
"storage": {
  "rules": "storage.rules"
}
```

**Gotcha**: Storage rules are completely separate from Firestore rules. If you add new upload functionality (e.g., file attachments), the storage.rules file must be updated independently.

**Common Pattern**: Developers update Firestore rules, deploy, then forget to update/deploy storage rules separately. Upload code works locally (emulator) but fails in production.

**Command Difference**:
```bash
firebase deploy --only firestore:rules     # Firestore only
firebase deploy --only storage:rules       # Storage only
firebase deploy --only firestore:rules,storage  # Both
```

---

### Offline Persistence Cache Behavior Differences

**Problem**: Firestore's offline persistence cache (`enablePersistence()`) behaves differently between web and mobile, and between development and production.

**Gotchas**:
- Cache is stored in IndexedDB - size limit depends on browser quota
- Setting `experimentalAutoDetectLongPolling: true` in Firebase config can cause issues with older browsers
- Cache persists across browser restarts; if you're testing auth state changes, cache can interfere
- Cache invalidation is automatic (stale data is refreshed), but there's a window where stale data is served

**When Adding Features**: If adding offline capability or relying on cached data:
- Test in incognito/private mode (no persistent cache)
- Clear IndexedDB during testing (DevTools > Application > IndexedDB)
- Don't assume realtime updates will work with persistence enabled

---

### Emulator vs Production Behavioral Differences

**Problem**: Firebase Emulator Suite is permissive by default, but production is restrictive. Features working in emulator may fail in production.

**Known Differences**:
- Rules are ignored in emulator (always allow) unless explicitly configured
- Authentication state persists differently in emulator
- Timestamps are UTC in both, but timezone handling differs in some SDKs
- Storage paths in emulator vs production may have different restrictions

**For Workflow Guardian**: If testing new Firebase features:
1. Test in emulator first (for development speed)
2. Deploy to a staging/dev Firebase project to catch rule issues
3. Never assume emulator behavior matches production

---

## 2. Supabase Gotchas

### Row Level Security (RLS) Policies Must Be Updated for New Tables

**Current State** (Los Issue Tracker):
```toml
[auth]
enable_signup = true
enable_confirmations = false
```

**Gotcha**: Unlike Firebase's centralized security rules, Supabase RLS policies are **per-table**. When you create a new table, no RLS policy exists by default, making the table world-readable unless you add a policy.

**Critical Risk**: A new `workflows` table with no RLS policy would be readable by ALL authenticated users, even if you intended it to be private.

**Example Risk**:
```sql
CREATE TABLE workflows (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  config JSONB
);
-- WITHOUT RLS policy or ENABLE ROW LEVEL SECURITY,
-- this table is readable by all authenticated users
```

**Correct Pattern** (must be paired):
```sql
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_can_only_access_own_workflows"
  ON workflows
  FOR ALL
  USING (auth.uid() = user_id);
```

**When Adding Features**:
- Every new table needs an explicit RLS policy before data is added
- Run `SELECT * FROM pg_policies WHERE tablename = 'workflows'` to verify policies exist
- Test policies by logging in as different users

---

### Edge Functions: Cold Start & Timeout Limits

**Current Setup** (Los Issue Tracker):
```toml
[functions.sync-to-sheets]
verify_jwt = true

[functions.notify-google-chat]
verify_jwt = false
```

**Gotchas**:
- Edge functions have 10-second timeout limit (vs 60s for backend functions)
- Cold start takes 1-3 seconds on first invocation
- Concurrent execution limits apply - high traffic can queue requests
- External API calls during cold start can timeout

**If Adding New Edge Functions**:
- Long-running operations (data processing, migrations) should use database triggers or backend functions
- Keep functions under 50KB of code
- Minimize dependencies (each import adds to cold start)

---

### Realtime Subscriptions: Channel Limits & Broadcasting Issues

**Current Feature** (Los Issue Tracker):
```toml
[realtime]
enabled = true
```

**Gotchas**:
- Each subscription takes up a connection slot
- High-frequency updates (polling every 100ms) will spam the server
- Broadcasting to channels with no listeners still consumes server resources
- Unsubscribing improperly leaves dangling connections

**Pattern Risk**:
```javascript
// ❌ If not cleaned up in useEffect cleanup, this leaks connections
const subscription = supabase
  .channel('issues')
  .on('postgres_changes', { event: 'INSERT' }, callback)
  .subscribe();
```

**Correct Pattern**:
```javascript
useEffect(() => {
  const subscription = supabase.channel('issues').on(...).subscribe();
  return () => subscription.unsubscribe(); // Clean up on unmount
}, []);
```

---

### Migration Ordering is Critical

**Current Setup** (Los Issue Tracker):
```toml
[db]
port = 54322
major_version = 17
```

**Gotcha**: Supabase migrations are ordered by timestamp. Running migrations out of order or skipping migrations can corrupt the schema.

**Risk Scenarios**:
- If you create migration A, then B, then run B before A → B fails (missing dependencies)
- If migration adds a constraint, then deletes it, replaying migration history will fail
- Local schema can drift from production if migrations are inconsistent

**When Deploying Feature Changes**:
- Always generate migrations in order
- Test full migration chain locally before deploying
- Never edit migration files after creation - create new migrations instead
- Check `supabase migration list` before deploying

---

### Auth Session Handling Edge Cases

**Current Config** (Los Issue Tracker):
```toml
[auth]
jwt_expiry = 3600
enable_refresh_token_rotation = true
refresh_token_reuse_interval = 10
```

**Gotchas**:
- Refresh tokens rotate on use (if `enable_refresh_token_rotation = true`), old tokens become invalid
- JWT expiry is 1 hour by default - tokens can expire mid-session
- Simultaneous requests might both try to refresh, causing race conditions
- Session recovery after network disconnect can leave app in inconsistent state

**When Adding Auth-Dependent Features**:
- Implement token refresh before making API calls
- Handle 401 responses by triggering re-authentication
- Test session expiry (wait 1+ hour, make request, verify refresh works)

---

### PostgREST API Auto-Generation Behavior

**Current Feature** (Los Issue Tracker):
```toml
[api]
schemas = ["public", "storage", "graphql_public"]
max_rows = 1000
```

**Gotchas**:
- Every table automatically gets REST endpoints (`GET /table`, `POST /table`, etc.)
- Column names become URL parameters - spaces and special chars need encoding
- `max_rows = 1000` limits response size, preventing accidental full-table scans
- COUNT operations are slow on large tables (full scan required)

**When Adding Features**:
- New tables automatically expose REST endpoints - consider security implications
- Use `.limit(1000)` in queries to stay under max_rows
- Add database indexes for frequently-queried columns
- Test with realistic data volumes

---

## 3. Vite Gotchas

### Environment Variables Must Use VITE_ Prefix

**Current Setup** (Both projects use Vite):
```typescript
// vite.config.ts
// Only variables prefixed with VITE_ are accessible in browser code
```

**Gotcha**: Only environment variables starting with `VITE_` are exposed to the client-side bundle. All other env vars are stripped during build.

**Risk**: If your `.env` contains:
```
FIREBASE_API_KEY=...
VITE_FIREBASE_API_KEY=...  // ✅ This one is exposed
```

The first one won't be available in browser code, only `VITE_FIREBASE_API_KEY` will work.

**When Adding Features**:
- If adding new API keys, environment variables, or config: prefix with `VITE_`
- Remember: these ARE exposed in the built bundle (never put secrets here)
- Use server-side env vars for sensitive keys

---

### HMR Behavior with New Files

**Problem**: Hot Module Reload (HMR) in Vite dev server sometimes misses new files or doesn't trigger full reload.

**Gotcha**: If you create a new component/route file while dev server is running, Vite might not watch it immediately.

**Solution**: Stop and restart `npm run dev` after adding new files to ensure they're watched.

**Ring Kissht Observed** (Vite 5):
- File watcher sometimes misses new imports in node_modules
- Circular imports can break HMR without stopping the dev server

---

### Proxy Configuration for New API Endpoints

**Current Setup** (Both projects):
```typescript
// No proxy config observed in vite.config.ts
// Both projects connect directly to Firebase/Supabase APIs
```

**Gotcha**: If you need to proxy API requests (e.g., to avoid CORS), proxy config must be in vite.config.ts.

**If Adding Backend Routes or API Gateway**:
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:3000'
    }
  }
})
```

Without this, dev server won't proxy requests, but production might work differently (depending on hosting).

---

### Build Optimization & Chunk Splitting

**Current Setup** (Both projects):
```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        // Ring Kissht: firebase chunk + vendor chunk
        firebase: ['firebase/app', 'firebase/auth', ...],
        vendor: ['react', 'react-dom', ...],

        // Los Issue Tracker: supabase chunk + vendor chunk
        supabase: ['@supabase/supabase-js'],
        vendor: ['react', 'react-dom'],
      },
    },
  },
}
```

**Gotchas**:
- Large entry bundle can delay first paint
- Manual chunks are correct strategy, but oversplitting creates too many small files (bad for HTTP/1.1)
- Chunk names change on every build if not configured (breaks caching)
- Async dynamic imports create extra requests

**When Adding Features**:
- Heavy libraries (charts, editors) should go in their own chunk via dynamic import
- Avoid importing entire libraries on startup
- Test bundle size with `npm run build && npm run preview`

---

### Import Resolution Differences from Webpack

**Current Setup** (Both projects):
```typescript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
}
```

**Gotchas**:
- Vite's import resolution is stricter than Webpack
- Circular imports cause issues more often
- File extensions must match exactly (`.ts` vs `.tsx`)
- `node_modules/.bin` scripts don't auto-resolve

**When Adding Features**:
- Test imports explicitly: `import { Foo } from '@/components/Foo'` (not `'@/components'` expecting auto-index)
- Avoid circular dependencies between components

---

## 4. React 18 vs 19 Differences

### Strict Mode Double-Rendering (React 18 Still Applies)

**Ring Kissht Issue Tracker**: React 18.2.0

**Gotcha**: In development mode with Strict Mode enabled, all components render twice to help detect side effects.

```javascript
// Development (Strict Mode):
// Component renders → cleanup → Component renders again
// This can cause bugs if side effects aren't idempotent
```

**When Adding Features**:
- Ensure side effects in useEffect are idempotent (safe to run multiple times)
- Database writes should be unique (check for duplicates on insert)
- API calls should be deduplicated

---

### useEffect Cleanup Timing Differences

**Problem**: The timing of cleanup functions varies between React versions.

**React 18**: Cleanup runs after effect, sometimes asynchronously.

**Gotcha**: Cleanup might run AFTER the next effect has started, not before.

```javascript
useEffect(() => {
  const subscription = firebase.firestore()
    .collection('submissions')
    .onSnapshot(listener);

  return () => subscription.unsubscribe(); // Cleanup
}, []);
```

If the component unmounts and remounts quickly, cleanup might not run before the new effect starts, causing double subscriptions.

---

### Concurrent Features Impact (React 18)

**Gotcha**: React 18 enables concurrent rendering, which means renders can be interrupted and resumed.

**Risk with Firebase/Firestore**:
- Render can be paused mid-way
- State updates outside of event handlers might not batch correctly
- flushSync() from 'react-dom' can force synchronous renders if needed

**When Adding Features**: Avoid side effects outside of useEffect hooks.

---

### React 19 Breaking Changes (Los Issue Tracker: React 19.2.0)

**Los Issue Tracker** uses React 19, which has breaking changes:

#### New Hooks (React 19):
```javascript
// useActionState - for form submissions with server actions
// useFormStatus - read form submission state
// useOptimistic - show optimistic updates while pending

// These don't exist in React 18, so they're not in Ring Kissht
```

#### Ref Handling Changes (React 19):
```javascript
// React 19: Pass ref directly as prop
<Component ref={myRef} />

// NOT the old React 18 style:
// <Component innerRef={myRef} /> // This no longer works in 19
```

#### JSX Namespace Change (React 19):
```javascript
// React 18: JSX namespace was global
// React 19: JSX namespace is React.JSX
// This affects TypeScript - global JSX types no longer exist
```

**Risk**: Code written for React 18 might break in React 19 due to ref and JSX changes.

---

### use() Hook Expansion (React 19)

**Problem**: The `use()` hook in React 19 is more versatile than React 18, but behaves differently.

**React 18**: `use()` mainly for Server Components and Promises.

**React 19**: `use()` works in client components too, can read context directly, can await async data.

**Gotcha**: React 18 code might not take advantage of new `use()` capabilities, so migrating from 18 to 19 opens up new patterns that need testing.

---

## 5. Tailwind v3 vs v4 Differences

### Configuration Format Changes (Critical)

**Ring Kissht Issue Tracker**: Tailwind v3.4.0
```javascript
// tailwind.config.js - Traditional config format
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: { ring: {...}, gold: {...} },
      fontFamily: { sans: [...], mono: [...] },
    }
  },
  plugins: [],
}
```

**Los Issue Tracker**: Tailwind v4.1.18
```javascript
// tailwind.config.js - Still exists, but much simpler
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  // All theming now in CSS via @theme directives
}
```

**Gotcha**: In v4, configuration is moved to CSS files using `@theme` directives, NOT in JavaScript.

```css
/* Tailwind v4 requires CSS configuration */
@import "tailwindcss";

@theme {
  --color-primary: #1e40af;
  --color-primary-light: #3b82f6;
  --radius: 0.5rem;
}
```

**Risk**: Copying v3 theme config to v4 and expecting it to work will result in ignored configuration.

---

### CSS Import System Changes (v4 Breaking)

**Tailwind v3**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Tailwind v4**:
```css
@import "tailwindcss";
/* That's it - no @tailwind directives */
```

**Gotcha**: Old @tailwind directives won't work in v4. CSS files need complete rewrite.

**Los Issue Tracker** uses v4, so its CSS setup is different. If porting code between projects, CSS files must match the Tailwind version.

---

### Dynamic Class Generation (Critical for React)

**Problem**: Tailwind's JIT compiler works in both v3 and v4, but there's a key difference in how dynamic classes are handled.

**v3**: Dynamic classes like `className={\`bg-\${color}\`}` don't always work (needs safelist).

**v4**: Dynamic classes work better, but still have limitations.

**Gotcha**: Avoid dynamic class strings:
```javascript
// ❌ Might not be generated
<div className={`bg-${color}-500`} />

// ✅ Use this instead (hardcoded classes)
<div className={color === 'red' ? 'bg-red-500' : 'bg-blue-500'} />
```

Both projects use this pattern, so be cautious when adding new dynamic styling.

---

### @apply Behavior Changes (v4)

**Tailwind v3**: `@apply` could include any utility, including responsive modifiers:
```css
.btn {
  @apply px-4 py-2 bg-blue-500 md:px-6 hover:bg-blue-600;
}
```

**Tailwind v4**: `@apply` no longer accepts responsive or state modifiers - must use CSS instead:
```css
.btn {
  @apply px-4 py-2 bg-blue-500;

  &:hover {
    @apply bg-blue-600;
  }

  @media (min-width: 768px) {
    @apply px-6;
  }
}
```

**Los Issue Tracker** uses v4, so if component CSS uses `@apply`, verify it doesn't include responsive/state modifiers.

---

### Dark Mode Implementation (v3 vs v4)

**Tailwind v3**:
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media'
}
```

```html
<html class="dark">
  <div class="bg-white dark:bg-gray-900"></div>
</html>
```

**Tailwind v4**:
```css
@theme {
  color-scheme: light dark;
}

/* Dark mode is configured in CSS */
```

**Gotcha**: Dark mode setup differs between versions. Ring Kissht (v3) and Los Issue Tracker (v4) have different dark mode implementations.

---

### New Utilities in v4

**Examples**:
- `--radius` custom property replaces hardcoded border-radius
- `color-mix()` for opacity instead of CSS custom properties
- Container queries built-in (no @tailwindcss/container-queries plugin)

**When Adding Features**:
- Check if a utility exists before writing custom CSS
- Los Issue Tracker (v4) has more built-in utilities - don't copy v3 workarounds

---

### Browser Support Changes

**Tailwind v3**: Works with ES5 browsers (IE11 with polyfills)

**Tailwind v4**: Requires modern CSS features:
- `@property` (Safari 16.4+)
- `color-mix()` (Safari 15.4+)
- CSS custom properties (all modern browsers)

**Gotcha**: v4 won't work on older browsers. Los Issue Tracker explicitly targets modern browsers only.

---

## 6. Cross-Framework Gotchas

### Firebase + React 18: Auth State Listener Patterns (Ring Kissht)

**Problem**: Firebase auth state persists across component unmounts, but React strict mode tests this twice.

**Gotcha Pattern**:
```javascript
// ❌ Will cause double subscription in dev strict mode
const [user, setUser] = useState(null);

useEffect(() => {
  firebase.auth().onAuthStateChanged(setUser);
}, []);
```

**Better Pattern**:
```javascript
const [user, setUser] = useState(null);

useEffect(() => {
  const unsubscribe = firebase.auth().onAuthStateChanged(setUser);
  return () => unsubscribe(); // Cleanup required
}, []);
```

**Risk**: Without cleanup, auth listener accumulates on each render cycle, causing multiple state updates.

---

### Supabase + React 19: Session Management Patterns (Los Issue Tracker)

**Problem**: Supabase sessions need explicit refresh logic, especially with React 19's new async capabilities.

**Gotcha**: `use()` hook in React 19 can await promises, but session refresh needs careful timing.

```javascript
// React 19 - might cause timing issues if not careful
const session = use(supabase.auth.getSession());
```

**Better Pattern**:
```javascript
useEffect(() => {
  const {
    data: { subscription },
  } = supabase.auth.onAuthStateChange((event, session) => {
    setSession(session);
  });

  return () => subscription?.unsubscribe();
}, []);
```

---

### Tailwind + React: Dynamic Class Generation Pitfalls

**Both Projects**: Tailwind v3 and v4 both have limitations with dynamic classes.

**Gotcha**:
```javascript
// ❌ Won't work - dynamic string
const statusColor = status === 'open' ? 'red' : 'green';
<div className={`text-${statusColor}-500`} />

// ✅ Works - hardcoded classes
<div className={status === 'open' ? 'text-red-500' : 'text-green-500'} />

// ✅ Also works - static class with CSS variable
<div className="text-current" style={{ color: statusColor }} />
```

**Risk**: Copy-pasting code with dynamic classes between projects will silently fail if tailwind config differs.

---

### TypeScript Strict Mode Differences Between Projects

**Ring Kissht**: `"strict": true`
```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**Los Issue Tracker**: Also `"strict": true` with similar settings
```json
{
  "extends": "eslint-plugin-react-hooks/recommended",
  "strict": true
}
```

**Gotcha**: Both projects enforce strict TypeScript, but react-hooks ESLint plugin versions differ.

**Risk**: Code working in Ring Kissht (React 18) might have type errors in Los Issue Tracker (React 19) due to:
- Different @types/react versions
- React 19 JSX namespace changes
- Ref handling API changes

**When Sharing Code Between Projects**:
- Run TypeScript compiler on both projects
- Test useCallback/useMemo hooks - react-hooks plugin rules differ
- Check ref patterns (innerRef vs ref prop)

---

### Vite Build Differences Between Projects

**Ring Kissht** (Vite 5.0.10):
```typescript
// Chunk splitting strategy
manualChunks: {
  firebase: ['firebase/app', ...],
  vendor: ['react', 'react-dom'],
}
```

**Los Issue Tracker** (Vite 7.2.4):
```typescript
// Chunk splitting strategy (more modern)
manualChunks: {
  supabase: ['@supabase/supabase-js'],
  vendor: ['react', 'react-dom'],
}
```

**Gotcha**: Vite 7 has changes from Vite 5:
- Build optimization differs
- Plugin API might differ
- Rollup options might have subtle differences

**When Migrating Code**:
- Don't assume bundle size will be the same
- Test `npm run build` on both versions
- Verify chunk names don't have timestamp hashes breaking caching

---

## 7. Defensive Recommendations for Workflow Guardian

### Before Adding Features:

1. **Check Security Rules**: Review firebase.rules and RLS policies before adding collections/tables
2. **Test Emulator vs Staging**: Always test new Firebase features in both emulator and staging Firebase project
3. **Verify Environment Variables**: Ensure all new env vars have VITE_ prefix and are in .env files
4. **Build in Both Projects**: Run `npm run build` in both projects to verify no breaking changes
5. **Type Check Strictly**: Run `tsc --noEmit` to catch React/TypeScript version incompatibilities
6. **Test Dark Mode & Responsive**: Both projects have complex Tailwind configs - test all theme variations

### When Migrating Code Between Projects:

1. **Account for React Version**: React 18 code might break in React 19 (ref patterns, JSX namespace)
2. **Account for Tailwind Version**: v3 to v4 requires CSS config changes, dynamic classes behave differently
3. **Account for TypeScript Versions**: Run type checker, don't just assume compatibility
4. **Re-test After Copy-Paste**: Don't assume code works just because it compiled elsewhere

### Testing Checklist for New Features:

- [ ] Works in development (`npm run dev`)
- [ ] Works in production build (`npm run build && npm run preview`)
- [ ] Security rules/RLS policies tested for new collections/tables
- [ ] Environment variables are all prefixed with VITE_
- [ ] TypeScript strict mode passes on both projects
- [ ] Dark mode works if using Tailwind colors
- [ ] No dynamic class generation (hardcode class strings)
- [ ] Firebase/Supabase auth state properly cleaned up in effects
- [ ] No circular imports
- [ ] Bundle size doesn't increase unexpectedly

---

## Sources & References

- [Supabase Migration Guides](https://supabase.com/docs/guides/platform/migrating-to-supabase)
- [Vite Breaking Changes](https://vite.dev/changes/)
- [Tailwind CSS v3 to v4 Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)
- [Firebase Documentation](https://firebase.google.com/docs)
- [React 18 Concurrent Features](https://react.dev/blog/2022/03/29/react-v18)
- [Common Mistakes Adding Features to React Apps](https://blog.logrocket.com/10-mistakes-react-developers-make/)

---

**Document Status**: Research-based defensive guide, not implementation guidance. All observations are warnings to watch for, not prescriptions for change.

**Last Updated**: February 2026

**Scope**: Framework-specific gotchas relevant to Ring Kissht Issue Tracker and Los Issue Tracker projects.
