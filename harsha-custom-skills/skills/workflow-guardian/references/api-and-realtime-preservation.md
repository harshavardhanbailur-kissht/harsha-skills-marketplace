# API & Realtime Subscription Preservation Guide
## For Workflow Guardian: Match, Don't Fix

**CRITICAL FRAMING:** This document teaches you to PRESERVE existing API patterns and contracts, not to improve them. When adding features, your job is to:

1. **Match** the exact function signatures and patterns already in use
2. **Don't Fix** existing error handling, naming conventions, or architectural decisions
3. **Preserve** all realtime subscription patterns, even if they have documented bugs
4. **Document** what exists before you touch anything
5. **Add Alongside** rather than refactor existing implementations

---

## 1. Service Layer Contract Documentation

### 1.1 Supabase useTickets Hook - Complete API Surface

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/hooks/useTickets.ts`

This hook is the PRIMARY service layer for LOS Issue Tracker. Every function has a documented contract that must be preserved.

#### Function: `fetchOpenTickets(page?: number)`
```typescript
// SIGNATURE (IMMUTABLE)
fetchOpenTickets(page = 0): Promise<Ticket[] | null>

// CONTRACT
- Parameter: page (0-indexed page number for pagination)
- Returns: Array of Ticket objects or null on error
- Side Effect: Updates internal state via setTickets()
- Pagination: Uses PAGE_SIZE = 30
- Query Filter: .eq('status', 'open')
- Order: ascending by 'submitted_at'
- Error Handling: Returns null, logs to console.error
- Pagination Behavior on page > 0: APPENDS to existing state (.prev => [...prev, ...results])
- Pagination Behavior on page = 0: REPLACES state (setTickets(results))

// WHY THIS MATTERS
- Callers depend on NULL return to detect errors (don't throw)
- Callers depend on state append vs replace behavior for pagination
- If you add a new subscription or filter, you cannot change this signature
```

#### Function: `fetchMySubmittedTickets(submitterName: string)`
```typescript
// SIGNATURE (IMMUTABLE)
fetchMySubmittedTickets(submitterName: string): Promise<Ticket[] | null>

// CONTRACT
- Parameter: submitterName (exact email or name string, case-sensitive as stored)
- Returns: Array of Ticket objects or null on error
- Side Effect: Updates internal state via setTickets() - REPLACES (not append)
- Query Filter: .eq('submitted_by', submitterName)
- Order: descending by 'submitted_at' (most recent first)
- Error Handling: Returns null, logs to console.error
- Pagination: NO pagination - always fetches ALL matching tickets in one query

// WHY THIS MATTERS
- Always replaces state, unlike fetchOpenTickets which appends on page > 0
- Product support users rely on this to see ONLY their own tickets
- No pagination parameter - designed for limited dataset (product support == one user)
```

#### Function: `fetchMyClaimedTickets(adminName: string, statusFilter?: 'claimed' | 'resolved', page?: number)`
```typescript
// SIGNATURE (IMMUTABLE)
fetchMyClaimedTickets(
  adminName: string,
  statusFilter?: 'claimed' | 'resolved',
  page = 0
): Promise<Ticket[] | null>

// CONTRACT
- Parameter 1: adminName (NOT USED - kept for backward compatibility)
- Parameter 2: statusFilter (optional filter: 'claimed' | 'resolved')
- Parameter 3: page (0-indexed pagination)
- Returns: Array of Ticket objects or null on error
- Side Effect: Updates internal state
- Pagination: Uses PAGE_SIZE = 30
- Query Filters (compound):
  * .eq('claimed_by', adminName)  [even though param ignored, internally uses JWT]
  * if statusFilter: .eq('status', statusFilter)
  * if NO statusFilter: .in('status', ['claimed', 'resolved'])
- Order: descending by 'claimed_at'
- Pagination: APPEND on page > 0, REPLACE on page = 0
- Error Handling: Returns null, logs to console.error

// WHY THIS MATTERS
- adminName parameter is IGNORED but kept for backward compatibility
- Actual claimed_by is set server-side from JWT (migration 028)
- If statusFilter is omitted, returns BOTH claimed AND resolved (not just claimed)
- State append/replace behavior mirrors fetchOpenTickets
- Callers must NOT pass adminEmail expecting it to filter - it's silently ignored
```

#### Function: `createTicket(ticketData: CreateTicketData)`
```typescript
// SIGNATURE (IMMUTABLE)
interface CreateTicketData {
  lsq_url: string;
  trn: string;
  image_urls: string[];
  description: string;
  issue_type: string;
  sub_issue?: string;
  submitted_by: string;
  query_category?: string;
  sub_category?: string;
  issue_date?: string;
  current_stage?: string;
}

createTicket(ticketData: CreateTicketData): Promise<Ticket | null>

// CONTRACT
- Returns: Single Ticket object on success, null on error
- Database Default: status = 'open'
- Database Default: current_stage = ticketData.current_stage ?? 'Submitted'
- Side Effect 1: Inserts one row into 'tickets' table
- Side Effect 2: ASYNC (non-blocking) - triggers syncToSheets('append')
  * If syncToSheets fails, it's logged as warning but doesn't fail the create
  * Caller does NOT await this, caller does NOT see the result
- Query: .insert([{...}]).select().single()
- Error Handling: Returns null on error, logs full error details

// WHY THIS MATTERS
- Sync to Sheets is FIRE-AND-FORGET (non-blocking)
- Caller sees success before sheet sync completes
- If you add another async operation alongside syncToSheets, use same fire-and-forget pattern
- DO NOT make syncToSheets blocking - would break existing UX
- Error structure: { message, details, hint } - all three properties can be logged
```

#### Function: `claimTicket(ticketId: string, _adminName: string)`
```typescript
// SIGNATURE (IMMUTABLE)
claimTicket(ticketId: string, _adminName: string): Promise<Ticket | null>

// CONTRACT
- Parameter 1: ticketId (UUID of ticket)
- Parameter 2: _adminName (IGNORED - kept for backward compatibility)
- Returns: Updated Ticket object on success, null on error
- Side Effect 1: Calls RPC 'ticket_action' with action='claim'
  * RPC validates ownership and status from JWT (migration 028)
  * RPC is the actual lock - prevents race condition at DB level
- Side Effect 2: ASYNC (non-blocking) - triggers syncToSheets('update')
- Error Handling: Returns null on error, logs to console.error
- RPC Parameters:
  {
    p_ticket_id: ticketId,
    p_action: 'claim',
    // Note: claimed_by is set server-side from JWT, not sent from client
  }

// WHY THIS MATTERS
- Actual work is done in RPC, not in the hook
- If two admins claim simultaneously:
  * Loser gets null result (RPC returns no rows due to WHERE status='open' not matching)
  * Caller sees error, triggers UI refresh
- If you add a new action (not 'claim', 'release', 'resolve'), use new RPC, don't reuse this
- Fire-and-forget sheet sync pattern is consistent with createTicket
```

#### Function: `releaseTicket(ticketId: string, _adminEmail: string)`
```typescript
// SIGNATURE (IMMUTABLE)
releaseTicket(ticketId: string, _adminEmail: string): Promise<Ticket | null>

// CONTRACT
- Parameter 1: ticketId (UUID of ticket)
- Parameter 2: _adminEmail (IGNORED - kept for backward compatibility)
- Returns: Updated Ticket object on success, null on error
- Side Effect 1: Calls RPC 'ticket_action' with action='release'
  * RPC validates ownership from JWT
- Side Effect 2: ASYNC (non-blocking) - triggers syncToSheets('update')
- Error Handling: Returns null on error, logs to console.error

// WHY THIS MATTERS
- Same pattern as claimTicket, same fire-and-forget sheet sync
- RPC validates that the calling admin owns the ticket (from JWT)
```

#### Function: `resolveTicket(ticketId: string, _adminEmail: string, resolution: ResolveData)`
```typescript
// SIGNATURE (IMMUTABLE)
interface ResolveData {
  recommended_action: string;
  next_steps?: string;
  resolution_notes: string;
}

resolveTicket(
  ticketId: string,
  _adminEmail: string,
  resolution: ResolveData
): Promise<Ticket | null>

// CONTRACT
- Parameter 1: ticketId (UUID of ticket)
- Parameter 2: _adminEmail (IGNORED - kept for backward compatibility)
- Parameter 3: resolution (required notes and action)
- Returns: Updated Ticket object on success, null on error
- Side Effect 1: Calls RPC 'ticket_action' with:
  {
    p_ticket_id: ticketId,
    p_action: 'resolve',
    p_resolution_notes: resolution.resolution_notes,
    p_recommended_action: resolution.recommended_action,
    p_next_steps: resolution.next_steps ?? null,
  }
- RPC Guards:
  * Validates status='claimed' (from EDGE_CASES.md fix)
  * Validates claimed_by=current_user_email (from EDGE_CASES.md fix)
- Side Effect 2: ASYNC (non-blocking) - triggers syncToSheets('update')
- Error Handling: Returns null on error, logs to console.error

// WHY THIS MATTERS
- FIXED edge case: No longer allows resolving tickets not claimed by user
- RPC now does compound filter: status='claimed' AND claimed_by=admin_email
- If you add validation, add it to RPC, not to this hook (RPC is authoritative)
```

#### Function: `subscribeToChanges(callback, userEmail?, userRole?)`
```typescript
// SIGNATURE (IMMUTABLE)
subscribeToChanges(
  callback: () => void,
  userEmail?: string,
  userRole?: string
): () => void

// CONTRACT
- Parameter 1: callback - function to invoke when changes occur
- Parameter 2: userEmail (optional) - used only if userRole = 'product_support'
- Parameter 3: userRole (optional) - determines filter scope
- Returns: unsubscribe function (call to disconnect)
- Subscription Channel Name: 'tickets-${crypto.randomUUID()}'
  * CRITICAL: Each call generates a NEW unique channel name
  * Multiple subscriptions = multiple channels (not a problem, not ideal)
- Postgres Changes Filter:
  {
    event: '*',        // ALL events (INSERT, UPDATE, DELETE)
    schema: 'public',
    table: 'tickets',
    // Filter only if product_support user + email provided:
    filter: userRole === 'product_support' && userEmail
      ? `submitted_by=eq.${userEmail}`
      : undefined
  }
- Callback Invoked: On ANY postgres change matching filter
- Error Handling: Two cases in subscribe() callback:
  * 'TIMED_OUT' - logged as console.error
  * 'CHANNEL_ERROR' - logged as console.error
  * No handler provided to caller - errors are silent
- Cleanup: unsubscribe() called in useEffect return

// KNOWN BUGS (DOCUMENTED BUT UNFIXED - DO NOT FIX)
1. No row-level filtering for admins
   - Admin users see activity patterns for ALL tickets, not just their claimed ones
   - This is DOCUMENTED in EDGE_CASES.md item #5 as UNFIXED
   - When you add realtime features, preserve this behavior - don't add filtering

2. Hardcoded channel naming collision risk
   - Random UUID prevents simple collisions, but HMR/re-mounts could create stale subscriptions
   - EDGE_CASES.md mentions this, it's a known issue
   - If you add new subscriptions, use same pattern: unique UUID per instance

3. Silent subscription failures
   - If connection drops, callback won't fire - data becomes stale
   - No reconnection attempt, no user feedback
   - This is by design (or neglect), preserve this behavior

// WHY THIS MATTERS
- Callback receives NO data - it's empty () => void
- Caller must re-fetch via fetchOpenTickets or similar to get actual data
- Subscription is "notify me something changed, not what changed"
- If you add a new subscription alongside this, use the SAME pattern:
  * Random UUID channel name
  * Empty callback (no data passed)
  * Same error handling (silent logging only)
```

#### Function: `syncToSheets(ticket: Ticket, operation: 'append' | 'update')`
```typescript
// SIGNATURE (IMMUTABLE)
syncToSheets(
  ticket: Ticket,
  operation: 'append' | 'update'
): Promise<{ success: boolean; error?: string }>

// CONTRACT
- Parameter 1: ticket (full Ticket object from DB)
- Parameter 2: operation ('append' for new, 'update' for existing)
- Returns: Object with success boolean and optional error string
- Caller Responsibility: Handle result (show toast, log, etc.)
- Implementation:
  * Invokes Supabase edge function 'sync-to-sheets'
  * Body: { ticket_number, operation }
  * Response is awaited and parsed
  * If FunctionsHttpError: extracts error from response body
  * If non-FunctionsHttpError: catches as normal error
- Error Categorization:
  * invokeError.context instanceof Response => parse response.json()
  * Otherwise use invokeError.message
  * All error details logged to console.error
- Return Structure:
  {
    success: result?.success === true,
    error: result?.error || 'Unknown sync error'
  }

// WHY THIS MATTERS
- NO LONGER fire-and-forget (changed from earlier async pattern)
- Caller MUST handle the returned { success, error }
- Used by createTicket, claimTicket, releaseTicket, resolveTicket
- All of THOSE functions ignore the result and use .then()/.catch()
- If you add a new operation (not 'append'/'update'), define it in edge function too
```

### 1.2 AuthContext - Session & Auth Contract

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/src/context/AuthContext.tsx`

#### Context API Surface
```typescript
// EXPORTED CONTEXT
interface AuthContextType {
  currentUser: User | null;           // null during loading, during auth error, or if logged out
  loading: boolean;                   // true while checking session, false when complete
  authError: string | null;           // null if no error, human-readable string if error
  signInWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}

// EXPORTED HOOK
function useAuth(): AuthContextType
```

#### Function: `signInWithGoogle()`
```typescript
// SIGNATURE (IMMUTABLE)
signInWithGoogle(): Promise<void>

// CONTRACT
- No parameters
- Returns: Promise that resolves when OAuth flow initiated (not when complete)
- Side Effect 1: Clears authError (sets to null)
- Side Effect 2: Initiates OAuth flow via supabase.auth.signInWithOAuth
- OAuth Options:
  {
    provider: 'google',
    options: {
      redirectTo: window.location.origin,
      queryParams: { hd: 'kissht.com' },  // Restrict to @kissht.com domain
    }
  }
- Error Handling: If OAuth error occurs, sets authError to error.message
- Navigation: Browser redirects to Google login, then back to app
- Promise Semantics: Resolves after OAuth initiates, not after user completes login

// WHY THIS MATTERS
- Domain restriction (@kissht.com) is enforced at OAuth level
- Actual auth is async - promise resolves before login complete
- Additional domain validation happens in handleSignedIn (secondary check)
- If you add SSO provider, mirror this pattern exactly
```

#### Function: `logout()`
```typescript
// SIGNATURE (IMMUTABLE)
logout(): Promise<void>

// CONTRACT
- No parameters
- Returns: Promise that resolves when logout complete
- Side Effects:
  1. Clears resolvedEmailRef.current = null
  2. Clears role cache via clearCachedRole()
  3. Calls supabase.auth.signOut()
  4. Sets currentUser = null
  5. Sets authError = null
- Cache Cleanup: Both localStorage AND sessionStorage are cleared
- Result: User is completely logged out, no cached state remains

// WHY THIS MATTERS
- Call order matters: refs cleared, cache cleared, auth cleared, state cleared
- If you add auth-related state, clear it in logout too
- localStorage uses key 'los_cached_role'
- sessionStorage cleanup is for legacy key
```

#### State Machine: Authentication Flow

The auth flow is complex and has several defensive patterns. Understanding it prevents breaking realtime or async behavior.

```
┌─────────────────────────────────────────────────────────────┐
│ INITIAL STATE: Depends on Storage                            │
├─────────────────────────────────────────────────────────────┤
│ hasStoredSession() = true  (localStorage has 'sb-*-auth-token')
│    → loading = true initially
│                                                               │
│ hasStoredSession() = false AND hasOAuthCallback() = true
│    → loading = true (OAuth redirect in progress)
│                                                               │
│ Both false                                                    │
│    → loading = false immediately (show login)
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ OAUTH FLOW (on /callback or after signInWithGoogle)         │
├─────────────────────────────────────────────────────────────┤
│ 1. onAuthStateChange fires with (SIGNED_IN || INITIAL_SESSION)
│                                                               │
│ 2. setTimeout(() => processUser(user), 0)  [DEFERRED]
│    Reason: Supabase SDK holds Navigator Lock during callback.
│    Calling Supabase API inside callback = deadlock.
│    setTimeout(0) defers to next macrotask (lock released).
│                                                               │
│ 3. processUser(user):
│    - Mark userProcessed = true (prevent duplicate)
│    - Call handleSignedIn(user)
│    - Set loading = false in finally
│                                                               │
│ 4. handleSignedIn(user):
│    a. Check processingRef to prevent concurrent processing
│    b. Extract email, lowercase it
│    c. Check if already resolved (resolvedEmailRef)
│       - If same email: skip processing
│       - If different: process new user
│    d. Domain check: reject if not @kissht.com
│    e. Cache lookup: getCachedRole(email)
│       - If hit: set user immediately, set loading=false
│         Then revalidate in background (non-blocking)
│       - If miss: query allowed_users table (blocking)
│    f. Query result processing:
│       - If not_found (PGRST116): sign out, clear cache, error
│       - If error: set auth error, keep loading=true
│       - If found: cache role, set user, set loading=false
└─────────────────────────────────────────────────────────────┘

// KEY INVARIANT
processingRef.current = true during handleSignedIn
This prevents overlapping handleSignedIn calls.

// KEY INVARIANT
userProcessed = true after entering processUser
This prevents the onAuthStateChange callback firing SIGNED_IN twice
(it can fire both INITIAL_SESSION and SIGNED_IN during OAuth redirect).

// SAFETY TIMEOUT
If auth hangs, safetyTimeout fires after AUTH_TIMEOUT_MS (12s)
and forces loading=false to prevent infinite spinner.
```

#### Caching Strategy: Role Cache
```typescript
// CACHE KEY: localStorage['los_cached_role']
// CACHE VALUE: JSON { email, role, name, ts }
// CACHE TTL: 8 hours (CACHE_TTL_MS = 8 * 3600000)

// cacheRole(email, role, name)
- Saves to localStorage
- Called on successful login
- Called during background revalidation if role changed

// getCachedRole(email)
- Reads from localStorage
- Checks TTL: returns null if cache expired
- Used during handleSignedIn for instant render

// clearCachedRole()
- Removes from localStorage AND sessionStorage
- Called on logout
- Called on domain rejection
- Called when background revalidation finds user not authorized

// WHY DUAL CLEANUP
- sessionStorage cleanup is for legacy (old code used sessionStorage)
- localStorage is current
- On logout, clear both to be safe
```

---

## 2. Realtime Subscription Preservation - From Supabase Patterns

### 2.1 LOS Issue Tracker: subscribeToChanges() Pattern

The `subscribeToChanges()` function in useTickets hook demonstrates the Supabase realtime subscription pattern used in this project.

**Current Implementation Pattern:**
```typescript
subscribeToChanges(
  callback: () => void,
  userEmail?: string,
  userRole?: string
) => (() => void)

// Pattern:
// 1. Create unique channel name: `tickets-${crypto.randomUUID()}`
// 2. Build filter based on role:
//    - If userRole='product_support' && userEmail: row-level filter
//    - Else: table-level subscription
// 3. on('postgres_changes', filter, callback)
// 4. subscribe with error handler (logs only)
// 5. Return unsubscribe function
```

**Critical Rules for Adding New Subscriptions:**

1. **Channel Naming**
   - MUST use unique UUID per instance: `${description}-${crypto.randomUUID()}`
   - DO NOT reuse hardcoded channel names
   - DO NOT share channels between different subscription instances
   - This prevents HMR/re-mount collision bugs

2. **Callback Semantics**
   - Callback takes NO parameters: `() => void`
   - Callback does NOT receive changed data
   - Callback purpose: signal "something changed, re-fetch"
   - Caller must manually re-fetch data (e.g., fetchOpenTickets())
   - This is architectural pattern, DO NOT change it

3. **Error Handling**
   - Subscribe with status callback in second parameter
   - Check status === 'TIMED_OUT' || status === 'CHANNEL_ERROR'
   - Log error to console.error
   - DO NOT throw error to caller
   - DO NOT attempt reconnection (not implemented)
   - This is pattern, even though it's defensive-only (errors are silent)

4. **Filter Scope**
   - Product support users: row-level filter on submitted_by
   - Admin users: NO additional filtering (all tickets visible)
   - DO NOT add admin role-level filtering (documented as UNFIXED in EDGE_CASES.md)
   - If you add new subscriptions for admins, preserve visibility of all tickets

5. **Cleanup**
   - Return unsubscribe function
   - Call in useEffect return statement
   - unsubscribe() disconnects the channel

**Example: How to Add New Subscription Without Breaking Existing**

If you wanted to add a subscription for a new entity (e.g., comments):

```typescript
// DO THIS (pattern match):
export function useComments() {
  const subscribeToCommentChanges = useCallback(
    (callback: () => void, ticketId: string) => {
      const channelName = `comments-${ticketId}-${crypto.randomUUID()}`;

      const subscription = supabase
        .channel(channelName)
        .on('postgres_changes',
          {
            event: '*' as const,
            schema: 'public',
            table: 'comments',
            filter: `ticket_id=eq.${ticketId}`
          },
          () => {
            callback();  // Empty callback, no data passed
          }
        )
        .subscribe((status, err) => {
          if (status === 'TIMED_OUT' || status === 'CHANNEL_ERROR') {
            console.error('Comments subscription error:', status, err);
          }
        });

      return () => {
        subscription.unsubscribe();
      };
    },
    []
  );

  return { subscribeToCommentChanges };
}

// DO NOT DO THIS (breaks pattern):
// - DO NOT pass data in callback
// - DO NOT use hardcoded channel name
// - DO NOT skip error handler
// - DO NOT return unsubscribe function - return subscription object
// - DO NOT add reconnection logic
```

### 2.2 Using Subscriptions in Components

**Pattern from AdminView and other components:**

```typescript
// In useEffect:
useEffect(() => {
  const unsubscribe = useTickets().subscribeToChanges(
    () => {
      // Refresh data when change detected
      fetchOpenTickets(0);
    },
    currentUser.email,
    currentUser.role
  );

  return () => {
    unsubscribe();
  };
}, [currentUser]);

// Key points:
// 1. Call subscribeToChanges() in useEffect
// 2. Store returned unsubscribe function
// 3. Call unsubscribe() in cleanup (return statement)
// 4. Include dependencies (currentUser) to recreate subscription if user changes
```

---

## 3. Firebase Service Patterns (Ring Kissht Issue Tracker)

### 3.1 Firebase Initialization Contract

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/lib/firebase.ts`

```typescript
// EXPORTED MODULES
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
export const functions = getFunctions(app);

// KEY: Singleton Pattern
- Multiple initializations allowed (getApp() handles re-init)
- Services exported as module-level constants
- Emulator connections happen at module load time if DEV && VITE_USE_EMULATORS='true'

// CONFIG SOURCE
- Uses environment variables: VITE_FIREBASE_*
- Fallback to hardcoded values if env vars missing
- In production: Environment variables MUST be set
- In development: Emulators auto-connect if flag set

// WHY THIS MATTERS
- Import these objects, do not re-initialize
- All Firestore operations use the same `db` instance
- All Storage operations use the same `storage` instance
- Emulator detection is automatic - no code changes needed
```

### 3.2 Firestore CRUD Operations Pattern

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/lib/submissions.ts`

#### Contract: Submission ID Generation
```typescript
// PATTERN: Atomic Counter + Transaction
async generateSubmissionId(): Promise<string>

// IMPLEMENTATION
- Uses Firestore transaction (ACID guaranteed)
- Counter stored in COUNTERS_COLLECTION, document 'SUBMISSION_COUNTER'
- Each call: get current value, increment, save, return formatted ID
- Format: `SUB-${String(nextValue).padStart(4, '0')}`
  * Example: SUB-0001, SUB-0002, etc.
- Transaction ensures no duplicate IDs (server-side atomic)

// WHY THIS MATTERS
- If you add a new entity that needs IDs, use same transaction pattern
- DO NOT use client-side random IDs (fragile, can collide)
- DO NOT use client-side timestamps (clock drift)
- Transaction returns the ID, caller doesn't need to re-fetch
```

#### Contract: Create Submission with Attachments
```typescript
async createSubmission(
  data: SubmissionFormData,
  role: UserRole,
  onUploadProgress?: (progress: UploadProgress) => void
): Promise<string>

// INPUT CONTRACT
interface SubmissionFormData {
  actionable: string;
  detailedActionable: string;
  lsqLink: string;
  urn: string;
  // Multiple files support (new) + single file fallback (backward compat):
  attachmentFiles?: File[];
  attachmentFile?: File;
  comments?: string;
}

// RETURNS: Submission ID (string) on success, throws on error

// SIDE EFFECTS
1. Generates unique submission ID via generateSubmissionId()
2. For each file in attachmentFiles (or single attachmentFile):
   a. Uploads to Google Drive via uploadFileToDrive()
   b. Stores file metadata: { url, driveId, fileName, fileSize }
   c. Updates onUploadProgress callback with total progress
3. Determines assignedTo based on submitter role:
   - role='product_support' → assignedTo='sm'
   - role='sm' → assignedTo='product_support'
   - Other roles → assignedTo=null
4. Creates document in Firestore:
   - Collection: 'submissions'
   - Doc ID: submissionId
   - Fields:
     {
       id: submissionId,
       actionable, detailedActionable, lsqLink, urn,
       submittedBy: role,
       assignedTo: assignedTo,
       status: 'pending',
       createdAt: serverTimestamp(),
       submittedAt: serverTimestamp(),
       // Optional fields (only if provided):
       attachmentUrl, attachmentDriveId, attachments, comments
     }

// KEY INVARIANT
- serverTimestamp() used for created/submitted times (server-side, not client clock)
- Backward compatibility: both single-file fields (attachmentUrl, attachmentDriveId)
  and new multi-file field (attachments) are populated
- Undefined fields are omitted from document (not stored as null)

// PROGRESS TRACKING
- onUploadProgress called for each file
- Tracks cumulative progress across ALL files
- Percentage: (uploadedSoFar + currentFileProgress) / totalSize
- Used for progress bar UI

// ERROR HANDLING
- Throws if uploadFileToDrive fails (partial upload aborts)
- Throws if Firestore setDoc fails
- No cleanup of orphaned uploaded files if creation fails (EDGE_CASES.md item #10)
```

#### Contract: Query Operations - Pattern
```typescript
// PATTERN EXAMPLES (all follow same structure):

async getSubmissionById(submissionId: string): Promise<Submission | null>
async getAllSubmissions(): Promise<Submission[]>
async getSubmissionsAssignedTo(role: UserRole): Promise<Submission[]>
async getSubmissionsByStatus(status: SubmissionStatus): Promise<Submission[]>
async getSubmissionsBySubmitter(role: UserRole): Promise<Submission[]>

// COMMON PATTERN
- Collection: SUBMISSIONS_COLLECTION = 'submissions'
- Query order: orderBy('submittedAt', 'desc') - most recent first
- Optional where clauses depending on function purpose
- Returns: Array of Submission objects from snapshot.docs
- Error handling: Throws on error (unlike Supabase useTickets which returns null)

// WHY THIS MATTERS
- All queries return full array (no pagination built-in)
- Order is always by submittedAt, descending
- If you add new query, use same structure:
  * Build query with collection() + query() + where/orderBy
  * getDocs() to execute
  * Map snapshot.docs to typed objects
  * Throw on error
```

#### Contract: Realtime Subscriptions - Pattern
```typescript
// SUBSCRIBE PATTERN
function subscribeToSubmissions(
  callback: (submissions: Submission[]) => void
): () => void

// IMPLEMENTATION
- Builds query: collection + orderBy('submittedAt', 'desc')
- Calls onSnapshot(query, callback)
- onSnapshot fires immediately with current data
- onSnapshot fires again on any change
- Callback receives full array of documents (not changes)
- Returns unsubscribe function

// OTHER SUBSCRIBE FUNCTIONS
- subscribeToSubmissionsAssignedTo(role, callback): () => void
- subscribeToSubmissionsBySubmitter(role, callback): () => void
- Same pattern, different filters

// WHY THIS MATTERS
- Callback signature: (data) => void (receives data, unlike Supabase pattern)
- onSnapshot provides FULL array, not delta
- Return value is unsubscribe function
- If subscription fails, no error handler provided to onSnapshot
- To add new subscription, copy this pattern exactly
```

### 3.3 Google Drive Upload Integration

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/issue-tracker/src/lib/driveUpload.ts`

#### Contract: Upload via Firebase Function
```typescript
async uploadFileToDrive(
  file: File,
  submissionId: string,
  onProgress?: (progress: UploadProgress) => void
): Promise<UploadResult>

// INPUT
- file: File object from <input type="file">
- submissionId: string (SUB-XXXX format)
- onProgress: optional callback for progress tracking

// OUTPUT
{
  fileId: string;
  fileName: string;
  shareableUrl: string;
  webViewLink: string;
}

// PROCESS
1. Convert file to Base64
2. Call Firebase Function at hardcoded Vercel URL:
   'https://issue-tracker-three-lyart.vercel.app/api/uploadToDrive'
3. Send POST with JSON body:
   {
     file: { name, data (base64), mimeType },
     submissionId
   }
4. Parse response JSON as UploadResult
5. Invoke onProgress at 0%, 50%, 100%

// CRITICAL: Hardcoded URL
- NOT using import.meta.env for function URL
- URL is hardcoded to Vercel deployment
- This is fragile but persistent approach
- If you add new upload function, use same URL pattern

// ERROR HANDLING
- If response not ok: parse response.json(), throw error
- If JSON parse fails: throw generic HTTP error
- If file-to-base64 fails: throw error
- All errors thrown (not caught)

// PROGRESS SEMANTICS
- Called at 0% (before base64 conversion)
- Called at 50% (after base64 conversion)
- Called at 100% (after function returns)
- Percentage values are synthetic (not real upload tracking)
```

#### Contract: File Size Validation
```typescript
// Two functions with same pattern:

validateFileSize(file: File): {
  valid: boolean;
  warning: boolean;
  message?: string;
  sizeMB: number;
}

validateTotalFileSize(files: File[]): {
  valid: boolean;
  warning: boolean;
  message?: string;
  totalSizeMB: number;
}

// LIMITS
- Warning threshold: 100 MB
- Hard limit: 200 MB

// RETURN LOGIC
- If over 200 MB: { valid: false, warning: false, message }
- If 100-200 MB: { valid: true, warning: true, message }
- If under 100 MB: { valid: true, warning: false, no message }

// WHY THIS MATTERS
- Warning and error are distinct (valid+warning is possible)
- Caller must check both `valid` and `warning` separately
- If you add size validation elsewhere, use same thresholds
```

---

## 4. Edge Function Preservation (Supabase)

### 4.1 sync-to-sheets Function

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/supabase/functions/sync-to-sheets/index.ts`

#### Function Signature & Entry Point
```typescript
// serve() HTTP handler - called via supabase.functions.invoke()

POST /sync-to-sheets
Content-Type: application/json
Authorization: Bearer ${jwt_token} (from client)
  OR _internal_secret header (from DB trigger)

CORS: Validated via getCorsHeaders()
```

#### Authentication Contract (CRITICAL FIX 2026-02-12)
```typescript
// TWO authentication paths (mutually exclusive):

PATH 1: Frontend (JWT-authenticated)
- Header: Authorization: Bearer ${supabase_jwt}
- Function validates JWT via:
  const supabaseAuth = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { Authorization: authHeader } }
  })
  const { data: { user }, error } = await supabaseAuth.auth.getUser()
- If user not found: return 401 Unauthorized
- callerIdentity = user.email

PATH 2: Database Trigger (Internal Secret)
- Body: { _internal_secret, ... }
- Function validates: body._internal_secret === SYNC_INTERNAL_SECRET
- SYNC_INTERNAL_SECRET from environment (must be strong)
- If mismatch: return 401 Unauthorized
- callerIdentity = 'db-trigger'

// CRITICAL: Do not accept requests without one of these
- No Authorization header AND no _internal_secret → 401
- This is the fix for EDGE_CASES.md item #1
```

#### Request/Response Contract
```typescript
// REQUEST BODY
{
  ticket_number: number,      // required, must be integer
  operation: 'append' | 'update',  // required, only these two
  _internal_secret?: string   // optional, for DB triggers
}

// RESPONSE (200 OK)
{
  success: true,
  ticket_number: number,
  operation: string
}

// RESPONSE (4xx/5xx Error)
{
  success: false,
  error: string  // client-facing message (safe to expose)
}

// STATUS CODES
- 400: Missing fields, invalid operation, invalid types
- 401: Unauthorized (auth failed)
- 404: Ticket not found in DB
- 500: Internal error (config, Google Sheets API, etc.)
```

#### Core Logic: Database Re-fetch (CRITICAL FIX)
```typescript
// CRITICAL: Function re-fetches ticket from DB using SERVICE_ROLE key
const supabaseAdmin = createClient(
  SUPABASE_URL,
  SUPABASE_SERVICE_ROLE_KEY  // Admin key, bypasses RLS
)

const { data: dbTicket, error: fetchError } = await supabaseAdmin
  .from("tickets")
  .select("*")
  .eq("ticket_number", ticket_number)
  .single()

// WHY THIS MATTERS
- Does NOT trust client-provided data
- Uses SERVICE_ROLE_KEY to ensure data integrity
- If ticket doesn't exist: return 404 (caller can't create fake tickets)
- This is the fix for edge case: prevents formula injection + ensures accuracy
```

#### Sheet Sync Logic
```typescript
// PARALLEL SYNC TO TWO SHEETS
const results = await Promise.allSettled([
  syncToSheet(SHEET_ID, "Original Sheet"),
  syncToSheet(SHEET_ID_DUPLICATE, "Duplicate Sheet"),
])

// COLLECT ERRORS
- If either sheet fails, error is collected but function returns 200 (partial success)
- Response: { success: (errors.length === 0), errors: [...] }

// WHY THIS MATTERS
- Both sheets kept in sync
- One failure doesn't prevent other sheet from updating
- Partial success is better than atomic failure
```

#### Row Formatting: Column Mapping
```typescript
// formatTicketRow(ticket): string[]
// Returns array with 18 columns (A-R):

A: Ticket Number (TKT-XXX)
B: Date
C: LSQ Link
D: TRN (CHANGED from ticketNumber in fix)
E: Current Stage (Closed/Under Review/Submitted)
F: Query Category
G: Sub-Category
H: Employee Name (claimed_by or assigned admin)
I: Status (Resolved/Pending/Raised)
J: Working Status
K: Comment - Action
L: PREM Comment
M: Raised At (timestamp in IST)
N: Pending Timestamp (claimed_at in IST)
O: Resolved Timestamp (resolved_at in IST)
P: TAT (Pending to Resolved) in format "2h 30m"
Q: TAT (Raised to Resolved) in format "2h 30m"
R: Description (all user input)

// ESCAPING (CRITICAL FIX - M1)
- All columns escaped via escapeSheetValue()
- Prevents formula injection: =, +, -, @, \t, \r characters prefixed with '
- Newlines removed (Sheets formatting issue)
- This is the fix for EDGE_CASES.md: formula injection protection
```

#### Error Handling: Client-Facing Messages
```typescript
// Server logs full error for debugging
console.error("❌ Edge Function error:", err);

// But returns safe message to client
// SAFE messages (can expose details):
- "Missing required fields: ..."
- "Invalid payload: ..."
- "Invalid operation: ..."
- These are input validation errors

// SAFE messages (specific):
- "Unauthorized" (401)
- "Ticket not found" (404)

// UNSAFE messages (hidden from client):
- "GOOGLE_SHEET_ID not configured" → "Internal server error" (500)
- "SERVICE_ACCOUNT_KEY invalid" → "Internal server error" (500)
- "Google Sheets API error" → "Internal server error" (500)

// WHY THIS MATTERS
- Config errors don't leak internal details to browser
- Logs preserve full error for server debugging
- Client sees non-specific error, knows request failed
```

### 4.2 notify-google-chat Function

**File:** `/sessions/peaceful-practical-hawking/mnt/harshavardhanbailur/Desktop/Ring Kissht/Los Issue tracker/los-issue-tracker/supabase/functions/notify-google-chat/index.ts`

#### Authentication Contract
```typescript
// SINGLE authentication path (from DB trigger):
- Body: { _internal_secret, ticket, ... }
- Validates: body._internal_secret === NOTIFY_INTERNAL_SECRET
- If mismatch: return 401 Unauthorized
- If missing: return 401 Unauthorized

// DESIGN NOTE
- This function is called from PostgreSQL trigger (server-side)
- No JWT auth path (unlike sync-to-sheets)
- Uses internal secret only
```

#### Request/Response Contract
```typescript
// REQUEST BODY
{
  ticket: {
    unique_number: string,          // TKT-XXX
    ticket_number: number,
    description: string,            // HIGHEST PRIORITY in message
    submitted_by: string,
    trn: string | null,
    lsq_url: string,
    resolution_notes: string | null,
    recommended_action: string | null,
    resolved_at: string,            // ISO timestamp
  },
  _internal_secret: string
}

// RESPONSE (200 OK)
{
  success: true,
  ticket_number: string,
  timestamp: string  // ISO timestamp when processed
}

// RESPONSE (4xx/5xx)
{
  success: false,
  error: string,
  timestamp: string
}

// STATUS CODES
- 400: Missing ticket, invalid payload structure
- 401: Unauthorized (_internal_secret mismatch)
- 500: Google Chat API error, config error
```

#### Payload Validation
```typescript
// validateTicketPayload(ticket): TypeGuard
- Ensures all required fields present
- Type-checks each field
- Returns TypeScript type guard boolean
- Called before processing

// REQUIRED FIELDS
- unique_number: string
- ticket_number: number
- description: string
- submitted_by: string
- lsq_url: string
- resolved_at: string

// OPTIONAL FIELDS
- trn: string | null
- resolution_notes: string | null
- recommended_action: string | null
```

#### Message Formatting
```typescript
// createChatMessage(ticket): Google Chat Card V2 format
- Header with title "🎉 Ticket Resolved" and ticket number
- Sections with widgets:
  1. Ticket Number (bold)
  2. Description (highest priority, wraps)
  3. Submitted By (bold)
  4. TRN (if present)
  5. Resolution Notes / Action Taken (fallback to recommended_action)
  6. Resolved At (IST timezone, medium date + short time)
  7. Button: "View LSQ" (opens lsq_url)

// TIMESTAMP FORMATTING
- Locale: 'en-IN' (India)
- Timezone: 'Asia/Kolkata' (IST)
- Style: medium date + short time
- Example: "Feb 12, 2026, 3:45 PM"
```

#### Retry Logic
```typescript
// sendToGoogleChat(message, maxRetries=3)
- Exponential backoff: 2^attempt * 1000 ms
  * Attempt 1 fails → retry after 2s
  * Attempt 2 fails → retry after 4s
  * Attempt 3 fails → retry after 8s
  * Attempt 4 fails → give up
- Each attempt logs attempt number and result
- Returns { success, error } on final failure

// WHY THIS MATTERS
- Transient network failures don't lose notifications
- Each attempt is logged (helps debug Google Chat API issues)
- After 3 attempts, notification is abandoned (don't retry forever)
- If you add similar async operations, use same retry pattern
```

---

## 5. API Error Handling Patterns

### Pattern Documentation from Both Projects

#### Supabase Error Pattern (useTickets)
```typescript
// RETURN NULL ON ERROR (not throw)
const fetchOpenTickets = useCallback(async (page = 0) => {
  try {
    const { data, error: err } = await supabase.from('tickets').select('*');
    if (err) throw err;
    // ... return data
  } catch (e) {
    console.error('fetchOpenTickets error:', e);
    return null;  // ← Explicit null return
  }
}, []);

// IMPLICATIONS
- Caller checks for null: if (!result) { show error }
- No exception thrown to caller (caller can't use try/catch)
- Error details logged to console (for debugging)
- UI doesn't crash on API error

// ERROR DETAIL LOGGING
- Supabase errors have { message, details, hint }
- All three logged: console.error('Error details:', ex.message, ex.details, ex.hint)
- Caller doesn't see these details (null returned)

// PATTERN TO PRESERVE
- If you add new API call, return null on error
- Log error details to console for debugging
- Don't throw exceptions to caller
```

#### Firebase Error Pattern (submissions)
```typescript
// THROW ON ERROR (not null)
const createSubmission = async (data, role, onProgress) => {
  try {
    // ... perform Firestore operations
    await setDoc(docRef, submissionData);
    return submissionId;  // ← Return success value
  } catch (error) {
    throw error;  // ← Throw to caller
  }
};

// IMPLICATIONS
- Caller uses try/catch to handle errors
- Caller can catch specific Firestore error types
- Error is propagated up call stack
- UI must handle exception

// PATTERN TO PRESERVE
- If you add new Firestore operation, throw on error
- Don't swallow exceptions
- Caller is responsible for error handling
```

#### Toast/UI Error Pattern (Components)
```typescript
// EXAMPLE from ticket operations:
const handleCreateTicket = async () => {
  try {
    const ticket = await createTicket(data);
    if (!ticket) {
      showErrorToast('Failed to create ticket');
      return;
    }
    showSuccessToast('Ticket created!');

    // Async sheet sync - error logged but not shown
    syncToSheets(ticket, 'append').then(result => {
      if (!result.success) {
        console.warn('Sheet sync failed:', result.error);
      }
    });
  } catch (error) {
    showErrorToast('Unexpected error');
  }
};

// PATTERNS
1. Check return value (null check for Supabase functions)
2. Show error toast to user if null/error
3. Async operations don't block UI (fire-and-forget)
4. Fire-and-forget errors are logged, not shown (non-critical)

// PATTERN TO PRESERVE
- Match existing error UI pattern in component
- Use showErrorToast() for user-facing errors
- Log to console for debugging
- Fire-and-forget operations don't show toast on error
```

#### Edge Function Error Pattern (sync-to-sheets)
```typescript
// CATEGORIZE ERRORS FOR CLIENT RESPONSE
try {
  // ... operations
} catch (err) {
  const errorMessage = err instanceof Error ? err.message : "Unknown error";
  let clientMessage: string;
  let statusCode = 500;

  if (errorMessage.includes("Missing required fields")) {
    clientMessage = errorMessage;
    statusCode = 400;
  } else if (errorMessage.includes("Unauthorized")) {
    clientMessage = "Unauthorized";
    statusCode = 401;
  } else {
    // Config/internal errors
    clientMessage = "Internal server error";
    statusCode = 500;
  }

  return new Response(JSON.stringify({ success: false, error: clientMessage }), {
    status: statusCode,
    headers: { ...corsHeaders, "Content-Type": "application/json" }
  });
}

// PATTERN
1. Catch all errors
2. Extract error message
3. Categorize into client-safe vs internal-only
4. Return appropriate status code
5. Log full error server-side (not sent to client)

// PATTERN TO PRESERVE
- Input validation errors (safe) have status 400
- Auth errors have status 401
- Ticket not found has status 404
- Config/API errors (unsafe) have status 500
```

---

## 6. Safe Feature Addition Patterns

### When Adding New Functionality, Use These Recipes

#### Recipe 1: Add New API Endpoint (Supabase)
```typescript
// STEP 1: Copy existing endpoint signature exactly
// Example: copying fetchOpenTickets to fetchClosedTickets

const fetchClosedTickets = useCallback(async (page = 0) => {
  try {
    const from = page * PAGE_SIZE;
    const to = from + PAGE_SIZE - 1;
    const { data, error: err } = await supabase
      .from('tickets')
      .select('*')
      .eq('status', 'closed')  // ← ONLY CHANGE: different filter
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
  } catch (e) {
    console.error('fetchClosedTickets error:', e);
    return null;  // ← MATCH: return null on error
  }
}, []);

// RETURNS: useTickets hook returns { ..., fetchClosedTickets }
```

#### Recipe 2: Add New Subscription (Supabase)
```typescript
// STEP 1: Use unique channel name with UUID
// STEP 2: Match callback signature: () => void
// STEP 3: Use same error handling pattern

const subscribeToCommentChanges = useCallback(
  (callback: () => void, ticketId: string) => {
    const channelName = `ticket-comments-${ticketId}-${crypto.randomUUID()}`;

    const subscription = supabase
      .channel(channelName)
      .on('postgres_changes',
        {
          event: '*' as const,
          schema: 'public',
          table: 'comments',
          filter: `ticket_id=eq.${ticketId}`
        },
        () => {
          callback();  // ← Empty callback, no data passed
        }
      )
      .subscribe((status, err) => {
        if (status === 'TIMED_OUT' || status === 'CHANNEL_ERROR') {
          console.error('Comment subscription error:', status, err);
        }
      });

    return () => {
      subscription.unsubscribe();
    };
  },
  []
);

// RETURNS: useTickets hook returns { ..., subscribeToCommentChanges }
```

#### Recipe 3: Add New Firestore Query
```typescript
// STEP 1: Match existing query pattern
// STEP 2: Order by submittedAt descending
// STEP 3: Throw on error

export async function getSubmissionsByPriority(
  priority: string
): Promise<Submission[]> {
  const q = query(
    collection(db, SUBMISSIONS_COLLECTION),
    where('priority', '==', priority),  // ← New filter
    orderBy('submittedAt', 'desc')      // ← Standard order
  );
  const snapshot = await getDocs(q);

  return snapshot.docs.map(doc => doc.data() as Submission);
  // ← No try/catch - let error throw to caller
}
```

#### Recipe 4: Add New Firestore Subscription
```typescript
// STEP 1: Match onSnapshot pattern
// STEP 2: Callback receives data array
// STEP 3: Return unsubscribe function

export function subscribeToSubmissionsByPriority(
  priority: string,
  callback: (submissions: Submission[]) => void
): () => void {
  const q = query(
    collection(db, SUBMISSIONS_COLLECTION),
    where('priority', '==', priority),
    orderBy('submittedAt', 'desc')
  );

  return onSnapshot(q, (snapshot) => {
    const submissions = snapshot.docs.map(doc => doc.data() as Submission);
    callback(submissions);  // ← Pass data to callback
  });
}
```

#### Recipe 5: Add New Edge Function (Supabase)
```typescript
// STEP 1: Use same HTTP handler pattern
// STEP 2: Authenticate same way (JWT or internal secret)
// STEP 3: Validate input, handle errors categorically

serve(async (req: Request) => {
  const corsHeaders = getCorsHeaders(req);

  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // AUTH: JWT or internal secret (same pattern)
    const authHeader = req.headers.get("Authorization");
    const body = await req.json();

    if (!authHeader && !body._internal_secret) {
      return new Response(
        JSON.stringify({ success: false, error: "Unauthorized" }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // VALIDATE INPUT
    const { required_field_1, required_field_2 } = body;
    if (!required_field_1 || !required_field_2) {
      throw new Error("Missing required fields");
    }

    // PERFORM OPERATION
    // ... business logic here

    // SUCCESS RESPONSE
    return new Response(
      JSON.stringify({ success: true, data: result }),
      { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (err) {
    // ERROR HANDLING: Categorize for client
    const errorMessage = err instanceof Error ? err.message : "Unknown error";
    let clientMessage = "Internal server error";
    let statusCode = 500;

    if (errorMessage.includes("Missing required fields")) {
      clientMessage = errorMessage;
      statusCode = 400;
    }

    console.error("❌ Edge Function error:", err);
    return new Response(
      JSON.stringify({ success: false, error: clientMessage }),
      { status: statusCode, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
```

---

## 7. Data Flow Preservation Map

### Complete Flow for Core Operations

#### Flow 1: User Creates Ticket (LOS Issue Tracker)
```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION: Click "Create Ticket" button                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ COMPONENT (TicketForm.tsx)  │
        │ - Validates input           │
        │ - Calls createTicket()      │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ HOOK (useTickets.createTicket)          │
        │ - Calls supabase.from('tickets')       │
        │   .insert([ticketData])                 │
        │ - Returns Ticket object                 │
        │ - Fire-and-forget: call syncToSheets() │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ DATABASE (Supabase: tickets table)      │
        │ - Inserts row                           │
        │ - Assigns UUID (auto)                   │
        │ - Sets submitted_at = NOW()             │
        │ - Sets status = 'open'                  │
        │ - Postgres trigger fires (async)        │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ POSTGRES TRIGGER (on tickets INSERT)    │
        │ - Calls notify_on_ticket_created()      │
        │ - Invokes notify-google-chat edge fn    │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ EDGE FUNCTION (notify-google-chat)      │
        │ - Gets ticket details from DB           │
        │ - Formats Google Chat message           │
        │ - Sends to webhook with retry (3x)      │
        │ - Returns success/error                 │
        └──────────────────────────────────────────┘
                       │
                       │ (Async - doesn't block component)
                       │
        ┌──────────────▼──────────────────────────┐
        │ COMPONENT Receives Ticket Object        │
        │ - Shows success toast                   │
        │ - Updates local state                   │
        │ - UI reflects new ticket immediately    │
        └──────────────────────────────────────────┘

// CRITICAL POINTS
1. Sheet sync (syncToSheets) happens AFTER component renders
   - Fire-and-forget pattern
   - Component doesn't wait for it

2. Google Chat notification is async via trigger
   - Happens after DB write
   - Not visible to component

3. If sync or notification fails, component doesn't know
   - Sheet sync logs warning (console)
   - Google Chat failure logged on server
   - User sees success (data in DB is good)

// KEY INVARIANT
Do not move syncToSheets() into the component - it would block UI
Do not make sheet sync blocking - current pattern is correct
```

#### Flow 2: Admin Claims Ticket (LOS Issue Tracker)
```
┌─────────────────────────────────────────────────────────────┐
│ ADMIN ACTION: Click "Claim" button                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ COMPONENT (AdminView)       │
        │ - Disable button (prevent   │
        │   double-click via          │
        │   claimingId state guard)   │
        │ - Calls claimTicket()       │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ HOOK (useTickets.claimTicket)           │
        │ - Calls supabase.rpc('ticket_action')   │
        │   { action: 'claim' }                   │
        │ - RPC validates: status='open'          │
        │ - Returns updated Ticket or null        │
        │ - Fire-and-forget: call syncToSheets()  │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ RPC FUNCTION (ticket_action)            │
        │ - Atomic update in DB                   │
        │ - WHERE status='open' AND               │
        │   claimed_by IS NULL                    │
        │ - SET claimed_by = current_user_email   │
        │ - SET claimed_at = NOW()                │
        │ - SET status = 'claimed'                │
        │ - WHERE clause acts as optimistic lock  │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ RESULT (Two possible outcomes)          │
        │                                         │
        │ Case A: You won the race                │
        │   - RPC returns updated ticket          │
        │   - Hook returns ticket object          │
        │   - Component shows success             │
        │                                         │
        │ Case B: You lost the race               │
        │   - RPC returns empty (WHERE matched 0) │
        │   - Hook throws error                   │
        │   - Component shows error toast         │
        │   - User clicks refresh, tries again    │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ SUBSCRIPTION (subscribeToChanges fires) │
        │ - Other admins receive notification     │
        │ - Their hook callbacks fire             │
        │ - They re-fetch open tickets            │
        │ - They see ticket now claimed           │
        └──────────────────────────────────────────┘

// RACE CONDITION HANDLING
- Optimistic lock at DB level (WHERE clause)
- Loser gets null, sees error
- No deadlock (DB serializes)
- No duplicate claims

// KEY INVARIANT
Do not add client-side debouncing (UI does it via claimingId state)
Do not change RPC WHERE clause (it's the lock)
Do not add retry logic (caller should retry manually)
```

#### Flow 3: Subscription Notification (Realtime Updates)
```
┌─────────────────────────────────────────────────────────────┐
│ ADMIN A: Claims ticket (as above)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ DATABASE: tickets row       │
        │ INSERT audit log            │
        │ Trigger fires (postgres)    │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ Postgres NOTIFY             │
        │ (Realtime channel dispatch) │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ Supabase Realtime Engine                │
        │ - Listens to public.tickets changes     │
        │ - Matches subscriptions by:             │
        │   * schema: 'public'                    │
        │   * table: 'tickets'                    │
        │   * event: '*'                          │
        │   * filter: userRole-dependent          │
        └──────────────┬──────────────────────────┘
                       │
        ├─────────────────────────────────────────────────┐
        │                                                 │
   ┌────▼──────────────────┐  ┌─────────────────────────▼────┐
   │ ADMIN B (watching     │  │ PRODUCT SUPPORT USER C       │
   │ all tickets)          │  │ (watching own tickets only)   │
   │                       │  │                              │
   │ Filter NOT matched:   │  │ Filter MATCHED:              │
   │ submitted_by=C_email  │  │ submitted_by=C_email         │
   │ (this ticket is A's)  │  │ (C submitted this ticket)    │
   │                       │  │                              │
   │ No notification!      │  │ Callback fires!              │
   └───────────────────────┘  │ Call fetchMySubmittedTickets │
                               │ UI updates                  │
                               └──────────────────────────────┘

// CRITICAL BEHAVIOR
- Admin B: sees ALL tickets changing, gets notification
- Support C: sees only OWN tickets, gets notification if C's ticket changed
- This is asymmetric by design (documented but not ideal)

// KEY INVARIANT
Do NOT add admin-level filtering (EDGE_CASES.md #5 is unfixed)
Do NOT change callback semantics (no data passed)
Do NOT add reconnection logic (not implemented)
```

#### Flow 4: Firebase Submission Creation (Ring Kissht)
```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION: Submit form (Issue Tracker)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ COMPONENT (SubmissionForm)              │
        │ - Validates form data                   │
        │ - Calls createSubmission(data, role)    │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ HOOK (submissions.createSubmission)     │
        │ Step 1: generateSubmissionId()          │
        │ - Firestore transaction                 │
        │ - Increment SUBMISSION_COUNTER          │
        │ - Return SUB-0123 format                │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ For each file in attachmentFiles:       │
        │                                         │
        │ Step 2a: uploadFileToDrive()            │
        │ - Convert file to Base64                │
        │ - Call Firebase Function via HTTP       │
        │ - Response: { fileId, shareableUrl }   │
        │ - Call onProgress callback              │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ FIREBASE FUNCTION (uploadToDrive)       │
        │ [Deployed on Vercel]                    │
        │ - Receives Base64 + metadata            │
        │ - Uploads to Google Drive               │
        │ - Returns file metadata                 │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ Step 2b: Build attachments array        │
        │ - url, driveId, fileName, fileSize      │
        │ - Also set legacy fields for compat:    │
        │   attachmentUrl, attachmentDriveId      │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ Step 3: setDoc(docRef, submissionData)  │
        │ - Collection: 'submissions'             │
        │ - Doc ID: SUB-0123                      │
        │ - Fields: id, form data, attachments,   │
        │   timestamps, assignment, status       │
        │ - serverTimestamp() for timestamps      │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ FIRESTORE: Document created             │
        │ - Realtime listeners triggered          │
        │ - subscribeToSubmissions callbacks fire │
        │ - subscribeToSubmissionsAssignedTo()    │
        │   fires if assignedTo matches          │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────▼──────────────────────────┐
        │ COMPONENT Receives Submission ID        │
        │ - Shows success toast                   │
        │ - Clears form                           │
        │ - Navigation (optional)                 │
        │ - Other subscribers see new submission  │
        │   via realtime update                   │
        └──────────────────────────────────────────┘

// CRITICAL DIFFERENCES FROM SUPABASE
- Throws errors instead of returning null
- Callback receives data (not empty)
- onProgress tracks multi-file upload

// KEY INVARIANT
Do NOT change error handling (throw, don't return null)
Do NOT change upload sequencing (sequential, not parallel)
Do NOT skip serverTimestamp() for dates
```

---

## 8. Common Modification Pitfalls & Prevention

### Pitfall 1: Changing Function Signatures
```
BAD:
// Old
fetchOpenTickets(page = 0): Promise<Ticket[] | null>

// New (changed signature!)
fetchOpenTickets(page = 0, filters?): Promise<TicketQueryResult>
// ↑ Breaks all callers expecting Ticket[]
// ↑ Breaks null-check error handling

GOOD:
// Old
fetchOpenTickets(page = 0): Promise<Ticket[] | null>

// New (add alongside, don't modify)
fetchOpenTicketsFiltered(filters, page = 0): Promise<Ticket[] | null>
// ↑ New function with new signature
// ↑ Old function untouched
// ↑ Callers can opt-in to new version
```

### Pitfall 2: Adding Error Handling Where There Was None
```
BAD:
// Old
subscribeToChanges(callback, userEmail?, userRole?) {
  // No error handler
  const subscription = supabase.channel(name)
    .on('postgres_changes', filter, () => callback())
    .subscribe((status, err) => {
      if (status === 'TIMED_OUT') {
        // MODIFIED: now it throws!
        throw new Error('Subscription failed');
      }
    });
}
// ↑ Now throws in subscriber callback
// ↑ Caller not expecting exception
// ↑ Component crashes

GOOD:
// Keep original pattern
subscribeToChanges(callback, userEmail?, userRole?) {
  const subscription = supabase.channel(name)
    .on('postgres_changes', filter, () => callback())
    .subscribe((status, err) => {
      if (status === 'TIMED_OUT' || status === 'CHANNEL_ERROR') {
        console.error('Subscription error:', status, err);
        // ← Still silent from caller perspective
      }
    });
}
```

### Pitfall 3: Making Fire-and-Forget Operations Blocking
```
BAD:
// Old (fire-and-forget)
if (data) {
  syncToSheets(data as Ticket, 'append').then(result => {
    if (!result.success) {
      console.warn('Sheet sync failed:', result.error);
    }
  });
}
return data;  // Return immediately

// New (blocking)
if (data) {
  const syncResult = await syncToSheets(data as Ticket, 'append');
  if (!syncResult.success) {
    throw new Error('Sheet sync failed: ' + syncResult.error);
  }
}
return data;
// ↑ Now await blocks ticket creation
// ↑ Component shows loading longer
// ↑ UI feels sluggish

GOOD:
// Keep fire-and-forget pattern
if (data) {
  syncToSheets(data as Ticket, 'append').then(result => {
    if (!result.success) {
      console.warn('Sheet sync failed (non-blocking):', result.error);
    }
  }).catch(err => {
    console.warn('Sheet sync error (non-blocking):', err);
  });
}
return data;
```

### Pitfall 4: Sharing Subscription Channels
```
BAD:
// Hardcoded channel name (collision risk)
const channelName = 'tickets-changes';  // Shared across instances!

subscribeToChanges(callback) {
  const subscription = supabase.channel(channelName)  // ← Reused!
    .on('postgres_changes', filter, () => callback())
    .subscribe();

  return () => subscription.unsubscribe();
}

// Call it twice:
const unsub1 = subscribeToChanges(() => log('sub1'));
const unsub2 = subscribeToChanges(() => log('sub2'));
// ↑ Both use same channel!
// ↑ Both callbacks fire on same event
// ↑ If unsub1() called, unsub2 breaks

GOOD:
// Unique channel per instance
const channelName = `tickets-${crypto.randomUUID()}`;  // ← Unique!

subscribeToChanges(callback) {
  const subscription = supabase.channel(channelName)
    .on('postgres_changes', filter, () => callback())
    .subscribe();

  return () => subscription.unsubscribe();
}

// Call it twice:
const unsub1 = subscribeToChanges(() => log('sub1'));
const unsub2 = subscribeToChanges(() => log('sub2'));
// ↑ Different channels
// ↑ Each maintains own state
// ↑ Independent cleanup
```

### Pitfall 5: Changing Query Behavior Silently
```
BAD:
// Old
fetchMyClaimedTickets(adminName, statusFilter?, page = 0) {
  // ...
  if (statusFilter) {
    query = query.eq('status', statusFilter);
  } else {
    query = query.in('status', ['claimed', 'resolved']);  // ← Returns BOTH
  }
}

// Caller expects:
// No filter → get claimed tickets only
result = fetchMyClaimedTickets(adminName);  // Expects claimed only!

// New (silent change!)
} else {
  query = query.eq('status', 'claimed');  // ← Now only claimed
  // ↑ Caller sees different data
  // ↑ No error thrown
  // ↑ Logic subtly broken
}

GOOD:
// Keep original behavior
} else {
  query = query.in('status', ['claimed', 'resolved']);
}
// ← Don't change, even if confusing
```

---

## Summary: The Match, Don't Fix Philosophy

When adding features to Workflow Guardian:

1. **Document First** - Read existing patterns in BOTH projects
2. **Copy Exactly** - Match signatures, error handling, naming
3. **Add Alongside** - New functions alongside old, not replacing
4. **Test Compatibility** - Ensure old code still works unchanged
5. **Preserve Bugs** - Don't fix known issues (they have dependencies)
6. **Log Decisions** - Comment why you're matching a pattern, not improving it

**This is defensive programming:** The codebase has evolved with hidden dependencies. Changing patterns breaks things in ways that aren't obvious. Preserve what works, even if it seems suboptimal.

