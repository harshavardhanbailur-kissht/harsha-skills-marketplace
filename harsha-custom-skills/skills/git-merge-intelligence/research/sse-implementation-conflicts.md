# Server-Sent Events (SSE) Implementation Conflict Patterns

## Overview

Server-Sent Events enable efficient one-way, server-to-client real-time communication. However, when merging branches that modify SSE implementations, conflicts often result in **silent runtime failures** rather than build-time errors. Both the backend (event producer) and frontend (event consumer) must agree on event types, data formats, and authentication mechanisms. A successful merge requires validating the entire SSE contract, not just resolving syntax conflicts.

## 1. SSE Architecture Patterns

### 1.1 Authenticated Route Setup

SSE endpoints require authentication middleware that differs from standard HTTP responses because SSE maintains persistent connections:

```go
// Go example with middleware chain
router.GET("/api/events", authMiddleware, sseHandler)

func authMiddleware(c *gin.Context) {
    token := c.GetHeader("Authorization")
    if token == "" {
        c.JSON(401, gin.H{"error": "unauthorized"})
        return
    }
    // Validate token
    user, err := validateToken(token)
    if err != nil {
        c.JSON(401, gin.H{"error": "invalid token"})
        return
    }
    c.Set("user", user)
    c.Next()
}

func sseHandler(c *gin.Context) {
    c.Header("Content-Type", "text/event-stream")
    c.Header("Cache-Control", "no-cache")
    c.Header("Connection", "keep-alive")

    user := c.MustGet("user").(User)
    // Send authenticated events
}
```

```javascript
// Node.js example with middleware chain
app.get('/api/events', authMiddleware, sseHandler);

function authMiddleware(req, res, next) {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
        return res.status(401).json({ error: 'unauthorized' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (err) {
        res.status(401).json({ error: 'invalid token' });
    }
}

function sseHandler(req, res) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const userId = req.user.id;
    // Send authenticated events
}
```

**Merge Conflict Risk**: If both branches modify authentication middleware (JWT vs session cookies, different validation logic), the SSE endpoint may silently lose authentication validation.

### 1.2 In-Process Hub Pattern

The hub pattern manages connected clients and broadcasts events:

```go
// Go hub pattern
type Hub struct {
    clients    map[*Client]bool
    broadcast  chan Event
    register   chan *Client
    unregister chan *Client
    mu         sync.RWMutex
}

type Client struct {
    id       string
    conn     http.ResponseWriter
    events   chan Event
    done     chan struct{}
}

func (h *Hub) run() {
    for {
        select {
        case client := <-h.register:
            h.mu.Lock()
            h.clients[client] = true
            h.mu.Unlock()

        case event := <-h.broadcast:
            h.mu.RLock()
            for client := range h.clients {
                select {
                case client.events <- event:
                default:
                    // Client buffer full, skip
                }
            }
            h.mu.RUnlock()

        case client := <-h.unregister:
            h.mu.Lock()
            if _, ok := h.clients[client]; ok {
                delete(h.clients, client)
                close(client.events)
            }
            h.mu.Unlock()
        }
    }
}

func (h *Hub) broadcastEvent(event Event) {
    h.broadcast <- event
}
```

```javascript
// Node.js hub pattern
class Hub {
    constructor() {
        this.clients = new Set();
    }

    registerClient(client) {
        this.clients.add(client);
    }

    unregisterClient(client) {
        this.clients.delete(client);
    }

    broadcastEvent(event) {
        this.clients.forEach(client => {
            try {
                client.write(`data: ${JSON.stringify(event)}\n\n`);
            } catch (err) {
                // Client disconnected
                this.clients.delete(client);
            }
        });
    }
}

const hub = new Hub();
```

**Merge Conflict Risk**: If both branches change client tracking (from Set to Map, or change event buffering strategy), broadcasting may fail silently.

### 1.3 Broadcast on Mutation

Events are triggered when data changes in the application:

```go
// Go: broadcast on database mutation
func (svc *UserService) UpdateUser(ctx context.Context, user User) error {
    // Update database
    err := svc.db.Update(user)
    if err != nil {
        return err
    }

    // Broadcast event
    svc.hub.broadcastEvent(Event{
        Type: "user_updated",
        Data: map[string]interface{}{
            "id":   user.ID,
            "name": user.Name,
        },
    })

    return nil
}
```

```javascript
// Node.js: broadcast on database mutation
async updateUser(userId, userData) {
    // Update database
    const user = await User.findByIdAndUpdate(userId, userData);

    // Broadcast event
    hub.broadcastEvent({
        type: 'user_updated',
        data: {
            id: user._id,
            name: user.name,
        },
    });

    return user;
}
```

**Merge Conflict Risk**: Event types may diverge (one branch sends "user_updated", another sends "update"). If the mutation site changes in one branch and event broadcasting changes in another, events may not be triggered at all.

### 1.4 Connection Lifecycle Management

SSE connections require careful lifecycle handling:

```go
// Go: connection lifecycle
func sseHandler(c *gin.Context) {
    user := c.MustGet("user").(User)
    client := &Client{
        id:     user.ID,
        conn:   c.Writer,
        events: make(chan Event, 10),
        done:   make(chan struct{}),
    }

    // Register client
    hub.register <- client
    defer func() {
        hub.unregister <- client
        close(client.done)
    }()

    flusher, _ := c.Writer.(http.Flusher)

    for {
        select {
        case event := <-client.events:
            fmt.Fprintf(c.Writer, "event: %s\ndata: %s\n\n",
                event.Type, event.Data)
            flusher.Flush()

        case <-c.Request.Context().Done():
            return
        }
    }
}
```

```javascript
// Node.js: connection lifecycle
function sseHandler(req, res) {
    const client = res;
    const userId = req.user.id;

    hub.registerClient(client);

    // Connection cleanup
    res.on('close', () => {
        hub.unregisterClient(client);
    });

    res.on('error', () => {
        hub.unregisterClient(client);
    });

    // Keep connection alive with periodic comments
    const heartbeat = setInterval(() => {
        res.write(': heartbeat\n\n');
    }, 30000);

    res.on('close', () => clearInterval(heartbeat));
}
```

**Merge Conflict Risk**: If one branch adds heartbeat/keepalive logic and another changes the registration mechanism, clients may disconnect unexpectedly.

## 2. Backend SSE Conflict Patterns

### 2.1 Route Handler Conflicts

Both merge branches modify the SSE endpoint handler:

**Scenario**: Feature A adds user-specific event filtering. Feature B adds event aggregation.

```go
// Branch A: User-specific filtering
func sseHandler(c *gin.Context) {
    user := c.MustGet("user").(User)
    client := &Client{
        id:       user.ID,
        userId:   user.ID,
        conn:     c.Writer,
        events:   make(chan Event, 10),
    }

    hub.register <- client
    // ...filter events by userId
}
```

```go
// Branch B: Event aggregation
func sseHandler(c *gin.Context) {
    client := &Client{
        id:         uuid.New().String(),
        conn:       c.Writer,
        events:     make(chan Event, 100),  // Different buffer size
        aggregator: NewAggregator(),
    }

    hub.register <- client
    // ...aggregate events
}
```

**Merged result** (conflict marker resolution): Handler ends up with only one branch's logic, losing the other's functionality.

**Silent failure**: App builds successfully. SSE works but either:
- User-specific filtering is missing (user sees events for other users)
- Event aggregation is missing (frontend gets raw events instead of aggregated)

### 2.2 Client Management Changes

Both branches modify how clients are tracked and stored:

**Scenario**: Feature A changes from Set to Map for better tracking. Feature B adds client metadata.

```javascript
// Branch A: Use Map instead of Set
class Hub {
    constructor() {
        this.clients = new Map();  // id -> client
    }

    broadcastEvent(event) {
        this.clients.forEach((client, id) => {
            client.write(`data: ${JSON.stringify(event)}\n\n`);
        });
    }
}
```

```javascript
// Branch B: Add client metadata
class Hub {
    constructor() {
        this.clients = new Set();
    }

    registerClient(client) {
        client.metadata = {
            connectedAt: Date.now(),
            userId: extractUserId(client),
        };
        this.clients.add(client);
    }
}
```

**Merged result**: If Map/Set conflict is resolved, one branch's metadata logic is lost.

**Silent failure**:
- Broadcasting might work but metadata isn't tracked (monitoring breaks)
- Or metadata works but broadcasting iterates wrong data structure (events don't send)

### 2.3 Event Type Conflicts

Both branches add new event types with different naming or structure:

**Scenario**: Feature A sends "notification_sent". Feature B sends "alert_created".

```javascript
// Branch A event types
hub.broadcastEvent({
    type: 'notification_sent',
    data: {
        id: notify.id,
        message: notify.text,
        userId: notify.recipient,
    },
});
```

```javascript
// Branch B event types
hub.broadcastEvent({
    type: 'alert_created',
    data: {
        alertId: alert.id,
        alertMessage: alert.message,
        targetUser: alert.userId,
    },
});
```

**Merged result**: Both event types coexist in backend code.

**Silent failure**: If frontend only listens for one event type, the other is silently ignored. App appears to work but real-time updates for one feature are missing.

### 2.4 Authentication Middleware Changes

Both branches modify authentication on SSE routes:

**Scenario**: Feature A adds role-based filtering. Feature B switches from Bearer tokens to session cookies.

```go
// Branch A: Role-based middleware
func authMiddleware(c *gin.Context) {
    token := c.GetHeader("Authorization")
    user, _ := validateToken(token)

    if user.Role != "admin" {
        c.AbortWithStatus(403)
        return
    }

    c.Set("user", user)
    c.Next()
}
```

```go
// Branch B: Session-based middleware
func authMiddleware(c *gin.Context) {
    session, _ := store.Get(c.Request, "session")
    if session.IsNew {
        c.AbortWithStatus(401)
        return
    }

    user := session.Values["user"]
    c.Set("user", user)
    c.Next()
}
```

**Silent failure**:
- One authentication mechanism is lost (users can't connect)
- Or role filtering is skipped (users see events they shouldn't)

### 2.5 Timeout/Keepalive Configuration Conflicts

Both branches change connection timeout or keepalive settings:

**Scenario**: Feature A sets 5-minute timeout. Feature B disables keepalive for bandwidth.

```javascript
// Branch A: 5-minute timeout
const SSE_TIMEOUT = 5 * 60 * 1000;

setInterval(() => {
    if (Date.now() - lastActivity > SSE_TIMEOUT) {
        closeConnection();
    }
}, 30000);
```

```javascript
// Branch B: No keepalive
function sseHandler(req, res) {
    res.setHeader('Connection', 'close');  // Disable keepalive
    // Send events without periodic heartbeats
}
```

**Silent failure**: Connections drop unexpectedly or keepalive stops working, but no error is logged.

### 2.6 Concurrent Connection Limit Changes

Both branches modify connection limits:

**Scenario**: Feature A limits to 1000 concurrent connections. Feature B implements per-user limits.

```go
// Branch A: Global limit
var (
    maxConnections = 1000
    currentConns   = 0
)

func sseHandler(c *gin.Context) {
    if currentConns >= maxConnections {
        c.JSON(503, gin.H{"error": "service unavailable"})
        return
    }
    currentConns++
    defer func() { currentConns-- }()
    // ...
}
```

```go
// Branch B: Per-user limit
func sseHandler(c *gin.Context) {
    user := c.MustGet("user").(User)
    userConns := countUserConnections(user.ID)

    if userConns >= 5 {
        c.JSON(429, gin.H{"error": "too many connections"})
        return
    }
    // ...
}
```

**Silent failure**: One limit mechanism is lost. Either connections grow unbounded or valid user connections are rejected.

## 3. Frontend EventSource Conflict Patterns

### 3.1 EventSource URL Changes

Both branches modify the SSE endpoint URL:

**Scenario**: Feature A changes `/api/events` to `/api/stream/events`. Feature B adds version prefix `/v2/api/events`.

```javascript
// Branch A
const eventSource = new EventSource('/api/stream/events');
```

```javascript
// Branch B
const eventSource = new EventSource('/v2/api/events');
```

**Silent failure**: If one URL is chosen and the backend is on a different branch, requests 404 but the error is silently caught. App appears to load but no updates arrive.

### 3.2 Event Handler Registration Conflicts

Both branches register handlers for different or overlapping events:

**Scenario**: Feature A listens for "notification_sent". Feature B listens for "user_updated".

```javascript
// Branch A
eventSource.addEventListener('notification_sent', (event) => {
    const notification = JSON.parse(event.data);
    showNotification(notification);
});
```

```javascript
// Branch B
eventSource.addEventListener('user_updated', (event) => {
    const user = JSON.parse(event.data);
    updateUserUI(user);
});
```

**Silent failure**: Only one handler is registered (depends on merge resolution). The other feature silently doesn't work.

### 3.3 Reconnection Logic Conflicts

Both branches implement reconnection differently:

**Scenario**: Feature A uses exponential backoff. Feature B uses fixed delay with max retries.

```javascript
// Branch A: Exponential backoff
let retries = 0;
const maxRetries = 10;

eventSource.onerror = () => {
    if (retries >= maxRetries) {
        console.error('Max reconnection attempts reached');
        return;
    }

    const delay = Math.pow(2, retries) * 1000;
    retries++;

    setTimeout(() => {
        eventSource = new EventSource(url);
    }, delay);
};
```

```javascript
// Branch B: Fixed delay with max retries
let attempts = 0;

eventSource.onerror = () => {
    if (attempts >= 3) {
        console.error('Reconnection failed');
        return;
    }

    attempts++;
    setTimeout(() => {
        eventSource = new EventSource(url);
    }, 5000);  // Fixed 5 second delay
};
```

**Silent failure**: Whichever logic is chosen may not match the backend's expectations. If frontend disconnects too aggressively or doesn't reconnect, users see stale data.

### 3.4 State Management for SSE Data Conflicts

Both branches manage SSE data state differently:

**Scenario**: Feature A stores events in a Redux store. Feature B uses local component state.

```javascript
// Branch A: Redux store
eventSource.addEventListener('user_updated', (event) => {
    const user = JSON.parse(event.data);
    dispatch(updateUser(user));
});
```

```javascript
// Branch B: Component state
eventSource.addEventListener('user_updated', (event) => {
    const user = JSON.parse(event.data);
    setUser(user);
});
```

**Silent failure**: State updates go to the wrong place. One branch updates Redux but components read local state, or vice versa. UI appears to work but data is out of sync.

### 3.5 Error Handling Changes

Both branches implement error handling differently:

**Scenario**: Feature A logs errors to monitoring. Feature B shows user notifications.

```javascript
// Branch A: Monitoring
eventSource.onerror = () => {
    logToSentry({
        level: 'error',
        message: 'SSE connection failed',
        timestamp: Date.now(),
    });
};
```

```javascript
// Branch B: User notification
eventSource.onerror = () => {
    showToast({
        type: 'error',
        message: 'Real-time updates unavailable',
    });
};
```

**Silent failure**: One error handling approach is lost. Errors aren't logged to monitoring OR users aren't notified.

## 4. Silent Runtime Failures vs Build Failures

### 4.1 Build Failures (Detectable)

These are caught at compile or import time:

```javascript
// ❌ Build failure: missing import
const hub = new Hub();  // Error: Hub is not defined

// ❌ Build failure: type error
function broadcastEvent(event: Event) {
    const data = JSON.stringify(event);
    return data + 123;  // Error: cannot add string and number
}

// ❌ Build failure: missing function
hub.sendEvent(event);  // Error: sendEvent is not a function
```

### 4.2 Silent Failures (Most Dangerous)

These pass build/tests but break functionality:

**Silent Failure #1: Event Type Mismatch**
```javascript
// Backend (Branch A)
hub.broadcastEvent({
    type: 'update',
    data: newData,
});

// Frontend (Branch B)
eventSource.addEventListener('change', (event) => {
    // This never fires because backend sends 'update'
    updateUI(JSON.parse(event.data));
});
```

Result: App builds and runs. EventSource connection succeeds. But no UI updates occur. User sees stale data. This is the most dangerous pattern.

**Silent Failure #2: Authentication State Not Passed**
```go
// Backend: Route handler removes auth check
func sseHandler(c *gin.Context) {
    // Feature branch removes the authentication check
    // Now everyone gets all events
    hub.register <- &Client{id: "unknown"}
}

// Frontend: Still sends auth header
eventSource := new EventSource('/api/events', {
    headers: {'Authorization': 'Bearer ' + token},
});
```

Result: Connection succeeds. But server ignores the token. App works but security is broken.

**Silent Failure #3: Connection Drops Without Reconnect**
```javascript
// Backend: New branch sets keepalive to 0
res.setHeader('Connection', 'close');

// Frontend: Old reconnection logic assumes connection persists
if (eventSource.readyState === EventSource.CONNECTING) {
    // Never actually reconnects properly
}
```

Result: Connections drop after first message. Frontend doesn't properly reconnect. Real-time updates stop.

**Silent Failure #4: Buffer Overrun**
```go
// Branch A: Small buffer
client.events = make(chan Event, 10)

// Branch B: Processing is slow
for event := range client.events {
    processEvent(event)  // Takes 5 seconds per event
}
```

Result: With small buffer and slow processing, events are dropped. No error. Just missing updates.

## 5. Testing SSE After Merge

### 5.1 Manual Testing Checklist

After merging SSE-related changes:

1. **Event Type Validation**
   - Backend: `grep -r "broadcastEvent" src/` and list all event types
   - Frontend: `grep -r "addEventListener" src/` and list all listener registrations
   - Verify exact match of event type strings (case-sensitive)

2. **Connection Establishment**
   ```bash
   # Test with curl and see raw SSE stream
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3000/api/events

   # Should see:
   # event: event_type
   # data: {"key":"value"}
   ```

3. **Authentication Verification**
   - Test with valid token: Should connect
   - Test with invalid token: Should reject (not connect successfully then fail silently)
   - Test with no token: Should reject with clear error
   - Test with wrong auth method (header vs cookie): Should work if both branches were merged

4. **Keepalive/Heartbeat**
   ```bash
   # Connect and wait without events
   curl -H "Authorization: Bearer TOKEN" http://localhost:3000/api/events

   # Should see heartbeat messages (comments starting with ':')
   # or nothing but connection stays open for 5+ minutes
   ```

5. **Data Format**
   - Capture real event from backend
   - Parse in frontend and log to console
   - Verify all expected fields are present
   - Check data types (strings, numbers, nested objects)

### 5.2 What to Check After Resolution

**Backend checks**:
```bash
# 1. Verify authentication middleware is applied
grep -B5 -A5 "router.GET.*events" config.go | grep -i auth

# 2. Check event broadcast calls exist
grep -r "broadcastEvent\|hub.broadcast" src/ | wc -l

# 3. Verify event types match between broadcast and mutation
grep -r "type.*:" src/ | grep -i event

# 4. Check connection lifecycle
grep -r "register\|unregister" src/ | grep -i client
```

**Frontend checks**:
```bash
# 1. Verify URL matches backend route
grep -r "new EventSource" src/ | head -1
# Compare with: grep -r "router.GET.*events" backend/

# 2. Check all event listeners
grep -r "addEventListener" src/ | awk '{print $NF}' | sort

# 3. Verify event handler logic
grep -A10 "addEventListener.*update" src/

# 4. Check reconnection strategy
grep -r "onerror\|CONNECTING\|OPEN" src/events.js
```

### 5.3 Integration Test Patterns

```javascript
// Integration test: Event production and consumption
describe('SSE After Merge', () => {
    let client;
    let eventCount = 0;

    beforeEach(async () => {
        // Connect to SSE
        client = new EventSource(
            'http://localhost:3000/api/events',
            { headers: { 'Authorization': 'Bearer ' + testToken } }
        );

        eventCount = 0;
    });

    afterEach(() => {
        client.close();
    });

    // Test 1: Connection with proper authentication
    test('should connect with valid token', (done) => {
        client.onopen = () => {
            expect(client.readyState).toBe(EventSource.OPEN);
            done();
        };

        client.onerror = () => {
            fail('Connection failed');
        };
    });

    // Test 2: Event types match
    test('should receive expected event types', (done) => {
        const expectedTypes = new Set(['user_updated', 'notification_sent']);
        const receivedTypes = new Set();

        client.addEventListener('user_updated', (event) => {
            receivedTypes.add('user_updated');
        });

        client.addEventListener('notification_sent', (event) => {
            receivedTypes.add('notification_sent');
        });

        client.onerror = () => {
            fail('Connection error');
        };

        // Trigger mutation that should broadcast event
        setTimeout(() => {
            fetch('/api/user/123', {
                method: 'PUT',
                body: JSON.stringify({ name: 'Updated' }),
                headers: { 'Authorization': 'Bearer ' + testToken },
            }).then(() => {
                // Wait for event to arrive
                setTimeout(() => {
                    expect(receivedTypes.size).toBe(expectedTypes.size);
                    done();
                }, 500);
            });
        }, 100);
    });

    // Test 3: Data format validation
    test('should send properly formatted event data', (done) => {
        client.addEventListener('user_updated', (event) => {
            const data = JSON.parse(event.data);

            expect(data).toHaveProperty('id');
            expect(data).toHaveProperty('name');
            expect(typeof data.id).toBe('string');
            expect(typeof data.name).toBe('string');

            done();
        });
    });

    // Test 4: Connection lifecycle
    test('should handle reconnection after disconnect', (done) => {
        let firstConnection = true;

        client.onopen = () => {
            if (!firstConnection) {
                // Successfully reconnected
                done();
            }
            firstConnection = false;
        };

        // Simulate disconnect after 1 second
        setTimeout(() => {
            client.close();

            // Reconnect
            setTimeout(() => {
                client = new EventSource(
                    'http://localhost:3000/api/events',
                    { headers: { 'Authorization': 'Bearer ' + testToken } }
                );
                // onopen should fire again
            }, 500);
        }, 1000);
    });

    // Test 5: Authentication enforcement
    test('should reject connection with invalid token', (done) => {
        const badClient = new EventSource(
            'http://localhost:3000/api/events',
            { headers: { 'Authorization': 'Bearer invalid_token' } }
        );

        badClient.onerror = () => {
            badClient.close();
            done();
        };

        // Should error within 2 seconds
        setTimeout(() => {
            fail('Invalid token was accepted');
        }, 2000);
    });
});
```

## 6. Resolution Strategies

### 6.1 Understanding SSE State Dependencies

SSE endpoints are **stateful** — the order of operations matters:

```
1. Client connects → authenticated
2. Client registers in hub → added to broadcast list
3. Mutation happens → triggers broadcast
4. Hub sends to client → client receives event
5. Frontend processes event → UI updates
```

If you break any link:
- No registration: events aren't sent
- Wrong event type: events are sent but ignored
- No authentication: security is compromised
- No broadcast trigger: mutations don't produce events

### 6.2 Both Sides Must Agree

**Critical Rule**: The backend handler and frontend EventSource must form a contract:

**Contract Elements**:
1. **URL**: Frontend and backend route must match exactly
   ```
   Frontend: new EventSource('/api/events')
   Backend:  router.GET('/api/events', handler)
   ```

2. **Authentication**: Frontend sends what backend expects
   ```
   Frontend: headers: { 'Authorization': 'Bearer ' + token }
   Backend:  token := c.GetHeader('Authorization')
   ```

3. **Event Types**: Backend sends what frontend listens for
   ```
   Backend:  broadcastEvent({type: 'user_updated', ...})
   Frontend: addEventListener('user_updated', handler)
   ```

4. **Data Format**: Event data structure must match
   ```
   Backend:  {id: user.ID, name: user.Name}
   Frontend: const {id, name} = JSON.parse(event.data)
   ```

5. **Connection Behavior**: Keepalive, timeouts, reconnection
   ```
   Backend:  heartbeat every 30 seconds
   Frontend: don't timeout < 60 seconds
   ```

### 6.3 Merge Resolution Process

**Step 1: Identify the Contract**
```bash
# Find backend endpoint
grep -r "GET.*events\|POST.*events" backend/

# Find frontend EventSource
grep -r "new EventSource" frontend/

# Extract the contract elements
```

**Step 2: Validate Both Branches**
```bash
# Backend branch check
git show branch-a:backend/handlers/sse.go | grep -A5 "broadcastEvent"
git show branch-b:backend/handlers/sse.go | grep -A5 "broadcastEvent"

# Frontend branch check
git show branch-a:frontend/hooks/useSSE.js | grep "addEventListener"
git show branch-b:frontend/hooks/useSSE.js | grep "addEventListener"
```

**Step 3: Resolve Systematically**

For each conflict:
1. Keep both features if they're independent
2. Merge event types and handlers
3. Ensure matching event type strings (case-sensitive)
4. Verify authentication mechanism works for both branches
5. Check timeouts/keepalive compatibility

Example resolution:
```javascript
// Merged frontend (both listeners)
eventSource.addEventListener('user_updated', handleUserUpdate);
eventSource.addEventListener('notification_sent', handleNotification);

// Merged backend (both broadcasts)
hub.broadcastEvent({type: 'user_updated', data: ...});
hub.broadcastEvent({type: 'notification_sent', data: ...});
```

**Step 4: Always Check Both Sides**

```bash
# After resolution, grep the merged files
echo "=== Backend event types ===" && grep -r "type.*:" backend/ | grep -i event
echo "=== Frontend listeners ===" && grep -r "addEventListener" frontend/

# They must match exactly
```

### 6.4 Common Merge Mistakes and Fixes

**Mistake 1: Keeping only one branch's event handler**
```javascript
// ❌ Wrong: Only notification_sent listener remains
eventSource.addEventListener('notification_sent', handle1);
// user_updated listener was lost

// ✅ Right: Both listeners
eventSource.addEventListener('user_updated', handleUser);
eventSource.addEventListener('notification_sent', handleNotif);
```

**Mistake 2: Route handler lost authentication**
```go
// ❌ Wrong: Conflict resolved to remove auth check
func sseHandler(c *gin.Context) {
    // No auth validation!
    hub.register <- &Client{...}
}

// ✅ Right: Keep authentication
func sseHandler(c *gin.Context) {
    if !c.GetBool("authenticated") {
        c.AbortWithStatus(401)
        return
    }
    hub.register <- &Client{...}
}
```

**Mistake 3: Event type mismatch**
```javascript
// ❌ Wrong: Case mismatch or different name
// Backend sends: {type: 'UserUpdated'}
// Frontend listens for: addEventListener('user_updated')

// ✅ Right: Exact match
// Backend: {type: 'user_updated'}
// Frontend: addEventListener('user_updated')
```

**Mistake 4: URL mismatch**
```javascript
// ❌ Wrong: Different URLs in different places
// Branch A: new EventSource('/api/events')
// Branch B: new EventSource('/api/stream/events')
// After merge: only one works

// ✅ Right: Single canonical URL
// Both agree: new EventSource('/api/events')
// Backend: router.GET('/api/events', handler)
```

## 7. Verification Checklist After Merge

Use this checklist after resolving SSE conflicts:

- [ ] **URL Agreement**: Backend route and frontend EventSource URL match exactly
- [ ] **Event Types**: Grep both files and list all event types — must match exactly (case-sensitive)
- [ ] **Event Handlers**: All event listeners from both branches are present in merged code
- [ ] **Broadcast Calls**: All mutation sites that should trigger events are present and call broadcast
- [ ] **Authentication**: Auth middleware is applied to SSE route in merged code
- [ ] **Data Format**: Event data structure is consistent (same field names across branches)
- [ ] **Connection Lifecycle**: Register and unregister logic is complete
- [ ] **Keepalive/Heartbeat**: Heartbeat or timeout logic is configured
- [ ] **Reconnection Logic**: Error handler and reconnection strategy are present
- [ ] **Test Locally**: Run manual test above and verify events flow end-to-end
- [ ] **Check Logs**: No "undefined event type" or "handler not found" errors
- [ ] **State Management**: SSE data updates go to the right place (Redux, Context, local state)

## References

- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Go `http` package documentation](https://pkg.go.dev/net/http)
- [Node.js EventEmitter patterns](https://nodejs.org/en/docs/guides/blocking-vs-non-blocking/)
- [Reconnection and Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
