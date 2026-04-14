# Systematic Debugging Methodology

A reference guide to prevent "fix one bug, create two more" through scientific, systematic debugging.

## 1. The Scientific Debugging Method

Adapted from Andreas Zeller's systematic approach. Follow these steps rigorously.

### Step 1: Observe
State the actual behavior vs. expected behavior with precision.

**Bad:** "The app is broken."
**Good:** "Clicking the submit button shows 'Error 500' instead of redirecting to the thank you page."

### Step 2: Reproduce
Make the bug happen consistently. Find the minimal reproduction case.

**Example:**
```
Steps to reproduce:
1. Create new user account with email "test@example.com"
2. Submit registration form
3. Observe: Email field shows "test@example.co" (missing 'm')

Minimal case: Just entering email "test@example.com" and clicking submit
```

**Checklist:**
- Can you reproduce it every time, or only sometimes?
- Does it happen on all browsers, all devices, or specific ones?
- Is there a specific data input that triggers it?

### Step 3: Hypothesize
Form a specific hypothesis: "I think X causes Y because Z."

**Bad:** "Something in the form validation is broken."
**Good:** "I think the email field regex is truncating the domain because it's using `/(.+)@(.+)/` which stops at the first match instead of greedy matching."

### Step 4: Predict
"If my hypothesis is correct, then when I do A, I should see B."

**Example:** "If the regex is the problem, then entering 'user@sub.domain.co.uk' should show 'user@sub.domain.co' (truncated at first dot in domain). Let me test this."

### Step 5: Test
Run the experiment. Check if you see the predicted behavior.

```javascript
// Hypothesis: regex is non-greedy
const regex = /(.+)@(.+)/;
const email = "test@sub.domain.com";
const match = email.match(regex);
console.log(match[2]); // Predicted: "sub" (if non-greedy)
                       // Actual: "sub.domain.com" (if greedy)
```

**If prediction matches reality:** You found the likely cause.
**If prediction doesn't match:** Revise hypothesis, go back to Step 3.

### Step 6: Conclude
Once you've confirmed the cause, fix it deliberately and test again.

**Bad fix:** Change the regex without understanding why.
**Good fix:** Change to greedy matching AND add test cases for edge cases like multi-level domains.

---

## 2. Binary Search Debugging

Find which change introduced the bug by systematically eliminating possibilities.

### Git Bisect (for commit-level bugs)

When you know the app worked at commit A, but is broken at commit B, binary search the commits between them.

```bash
# Start bisect
git bisect start
git bisect bad HEAD          # Current commit is broken
git bisect good v1.2.0       # Last known good version

# Git checks out a commit midway. Test it.
npm run test
# If broken: git bisect bad
# If working: git bisect good

# Repeat until git finds the exact breaking commit
git bisect reset
```

**Advantage:** Finds the exact commit that introduced the bug without reading all the code.

**Example result:** "Aha! Bug was introduced in commit abc123 'Refactor user validation.' Let me look at that specific change."

### Comment-Out Bisection (for code-level bugs)

When you have a file with multiple changes and one introduced the bug, bisect the code.

```javascript
// Original code (broken)
function validateEmail(email) {
  const trimmed = email.trim();
  const domain = trimmed.split('@')[1];
  const isValid = domain.includes('.') && domain.length > 3;
  return isValid && validateDNS(domain); // <-- One of these is broken
}

// Binary search: disable half the logic
function validateEmail(email) {
  const trimmed = email.trim();
  const domain = trimmed.split('@')[1];
  // const isValid = domain.includes('.') && domain.length > 3;
  // return isValid && validateDNS(domain); // Disabled
  return true; // Does bug still exist?
}

// If bug is gone: problem is in the disabled code
// If bug remains: problem is in the enabled code
// Repeat with remaining half
```

### When to Use Each

| Situation | Use |
|-----------|-----|
| Bug appeared in last week's commits | Git bisect |
| Bug in file modified by 3+ developers | Git bisect |
| Bug in code section you just changed | Comment-out bisection |
| Intermittent bug (timing-related) | Add logging, narrow down with bisection |

---

## 3. Data Flow Tracing

Find where data goes wrong by tracing it from symptom to source.

### General Approach

1. Identify where the bug appears (the symptom)
2. Trace backwards: where did this data come from?
3. Add strategic logging or breakpoints at each step
4. When data is correct at step X but wrong at step X+1, you found the problem

### React Example: Component shows wrong user data

```javascript
// Symptom: UserCard displays old name after editing

// Trace backwards:
// 1. UserCard receives props
console.log("UserCard received props:", props.user); // Step 1

// 2. Where do props come from? Parent component
// In parent:
console.log("State in parent:", this.state.user);     // Step 2

// 3. Where does state come from? API call or prop from grandparent
// In API call:
console.log("API response:", response.data);          // Step 3

// Data flow: Grandparent → API → Parent state → UserCard props → Display
// Start logging at each step, find where it breaks
```

### Three.js Example: Visual glitch in 3D scene

```javascript
// Symptom: Object appears in wrong position

// Trace backwards:
// 1. Render loop displays the object
console.log("Rendering object at:", mesh.position); // Step 1

// 2. Where is position set? Material/geometry setup
console.log("Geometry vertices:", geometry.attributes.position); // Step 2

// 3. Where does geometry come from? Model loading
console.log("Loaded model:", loadedData);           // Step 3

// Data flow: Asset load → Geometry setup → Material assignment → Render
// Log at each step to find where position becomes incorrect
```

### React Animation Example: Animation jank or stalls

```javascript
// Symptom: Animation stutters or doesn't update

// Trace backwards:
// 1. requestAnimationFrame callback
function animationLoop(time) {
  console.log("RAF fired, time:", time);             // Step 1

  // 2. State update
  setProgress(time / duration);
  console.log("State update triggered");              // Step 2

  // 3. Trigger (what started the animation?)
  // In useEffect or event handler
  console.log("Animation started by:", triggerSource); // Step 3
}

// Data flow: Trigger → State update → RAF callback → Render
```

**Key:** Insert `console.log()` at every step. Find where data changes unexpectedly.

---

## 4. Common Root Cause Patterns

Learn to recognize these patterns. They account for 80% of bugs.

### Off-by-One Errors

**Symptom:** Array index out of bounds, missing last item, extra item

```javascript
// BROKEN: Loop condition is <, but should be <=
for (let i = 0; i < array.length - 1; i++) {
  console.log(array[i]); // Skips last element
}

// BROKEN: Using length instead of length - 1
const lastIndex = array.length; // Out of bounds!

// BROKEN: 0-indexed confusion
const thirdElement = array[3]; // Gets 4th element, not 3rd

// FIXED: Be explicit about boundaries
for (let i = 0; i < array.length; i++) { }
const lastIndex = array.length - 1;
const thirdElement = array[2];
```

**Fix:** Add boundary tests (empty array, single element, multiple elements).

### Stale State / Closures

**Symptom:** Component shows old data, click handler uses outdated value

```javascript
// BROKEN: Closure captured staleCount at component mount
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const handleClick = () => {
      console.log("Count is:", count); // Always 0!
    };
    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, []); // Missing dependency!

  return <button onClick={() => setCount(count + 1)}>+</button>;
}

// FIXED: Include count in dependency array
useEffect(() => {
  const handleClick = () => {
    console.log("Count is:", count); // Latest value
  };
  window.addEventListener('click', handleClick);
  return () => window.removeEventListener('click', handleClick);
}, [count]); // Include dependency
```

**Fix:** Check dependency arrays. Use `useRef` for mutable latest values.

### Race Conditions

**Symptom:** Intermittent wrong data, duplicated actions, occasional crashes

```javascript
// BROKEN: Two async operations compete
function fetchData(id) {
  fetch(`/api/user/${id}`).then(r => r.json()).then(data => {
    setUser(data); // Might be old data if another fetch completes first!
  });
}

// Called twice quickly:
// fetchData(1) starts
// fetchData(2) starts
// fetchData(2) completes first, setUser(user2)
// fetchData(1) completes second, setUser(user1) — Wrong!

// FIXED: Abort previous requests
let abortController = null;

function fetchData(id) {
  if (abortController) abortController.abort();
  abortController = new AbortController();

  fetch(`/api/user/${id}`, { signal: abortController.signal })
    .then(r => r.json())
    .then(data => setUser(data));
}
```

**Fix:** Use `AbortController`, mutex pattern, or sequential queuing.

### Resource Leaks

**Symptom:** Memory grows over time, app gets slower with each interaction

```javascript
// BROKEN: Event listener never removed
function setupListener() {
  window.addEventListener('resize', handleResize);
}

// Called multiple times → multiple listeners → memory leak

// BROKEN: Timer never cleared
useEffect(() => {
  setInterval(() => {
    fetchData(); // Interval keeps firing even after unmount
  }, 1000);
}, []);

// FIXED: Clean up in useEffect return
useEffect(() => {
  const handleResize = () => { /* ... */ };
  window.addEventListener('resize', handleResize);

  return () => {
    window.removeEventListener('resize', handleResize); // Cleanup
  };
}, []);

// FIXED: Clear timer
useEffect(() => {
  const interval = setInterval(() => {
    fetchData();
  }, 1000);

  return () => clearInterval(interval); // Cleanup
}, []);
```

**Fix:** Always cleanup in `useEffect` return, use `AbortController`, call `dispose()`.

### State Management Bugs

**Symptom:** UI doesn't reflect expected state, wrong data displayed

```javascript
// BROKEN: Assuming state updates immediately
const [items, setItems] = useState([]);

function addItem() {
  setItems([...items, newItem]);
  console.log(items); // Still empty! State updated asynchronously
}

// BROKEN: Wrong dependency causes stale data
useEffect(() => {
  const filtered = items.filter(item => item.type === filterType);
  setFilteredItems(filtered);
}, []); // Missing filterType dependency!

// FIXED: State updates are batched, don't rely on immediate updates
function addItem() {
  const updated = [...items, newItem];
  setItems(updated);
  // Use 'updated' if you need the new state immediately
}

// FIXED: Include all dependencies
useEffect(() => {
  const filtered = items.filter(item => item.type === filterType);
  setFilteredItems(filtered);
}, [items, filterType]); // Complete dependency list
```

**Fix:** Use React DevTools to verify state flow. Check dependency arrays.

### Timing / Async Bugs

**Symptom:** Works sometimes, fails other times, intermittent failures

```javascript
// BROKEN: Assuming operations complete in order
function processOrder() {
  const customer = fetchCustomer(id); // Returns Promise
  const items = fetchItems(cartId);   // Returns Promise
  createOrder(customer, items); // customer and items are still Promises!
}

// BROKEN: Not handling errors
fetch('/api/data').then(processData);
// If fetch fails, code silently breaks

// FIXED: Make execution order explicit with await
async function processOrder() {
  const customer = await fetchCustomer(id);
  const items = await fetchItems(cartId);
  createOrder(customer, items); // Now has actual values
}

// FIXED: Parallel execution when possible
async function processOrder() {
  const [customer, items] = await Promise.all([
    fetchCustomer(id),
    fetchItems(cartId)
  ]);
  createOrder(customer, items);
}

// FIXED: Add error handling
async function processOrder() {
  try {
    const [customer, items] = await Promise.all([...]);
    createOrder(customer, items);
  } catch (error) {
    console.error('Order processing failed:', error);
    setErrorMessage('Failed to process order');
  }
}
```

**Fix:** Use `await` and `Promise.all()` to make dependencies explicit. Add error handling.

---

## 5. Debugging Heuristics

Rules of thumb that work 90% of the time.

### "What Changed?"

Most bugs come from recent changes. Check git history first.

```bash
git log --oneline -10
# Look at recent commits related to the bug area
git diff HEAD~1
# See exactly what changed
```

### "Simplify"

Remove code until the bug disappears. The last removed code is the culprit.

```javascript
// Start here (bug exists):
function processUser(user) {
  const name = user.name.trim().toLowerCase();
  const email = user.email.toLocaleLowerCase();
  const age = calculateAge(user.birthDate);
  validateEmail(email);
  updateDatabase(user.id, name, email, age);
  sendWelcomeEmail(email);
}

// Remove half the code:
function processUser(user) {
  const name = user.name.trim().toLowerCase();
  const email = user.email.toLocaleLowerCase();
  // const age = calculateAge(user.birthDate);
  // validateEmail(email);
  // updateDatabase(user.id, name, email, age);
  // sendWelcomeEmail(email);
}

// Does bug still exist? If yes, problem is in remaining code
// If no, problem is in removed code. Narrow it down further.
```

### "Check Assumptions"

The bug is in what you ASSUME works, not what you KNOW is broken.

```javascript
// Assumption: user object always has a name field
const name = user.name; // What if user is null?

// Better: Verify your assumption
if (!user || !user.name) {
  console.error("Invalid user object:", user);
  return null;
}
const name = user.name;
```

### "Read the Error"

Error messages and stack traces often pinpoint the exact problem.

```
TypeError: Cannot read property 'toLocaleLowerCase' of undefined
  at processUser (app.js:42)
  at handleSubmit (app.js:128)
```

**This tells you:** Line 42 in app.js, something is undefined when calling `toLocaleLowerCase`. Check your assumptions about that value.

### "Check Boundaries"

Bugs hide at the edges: empty arrays, null objects, zero values, max values, Unicode.

```javascript
// Test cases for array function:
const array = [];         // Empty
const array = [1];        // Single element
const array = [1, 2, 3];  // Multiple
const array = new Array(1000); // Large

// Test cases for string:
const str = "";           // Empty
const str = "a";          // Single char
const str = "🎉emoji";   // Unicode
const str = "a".repeat(10000); // Very long
```

### "Follow the Data"

Trace actual values. Don't assume what a variable contains.

```javascript
// Bad debugging:
// "user.id should be 123, so the fetch must be wrong"

// Good debugging:
console.log("user object:", user);
console.log("user.id type:", typeof user.id, "value:", user.id);
console.log("fetch URL being called:", `/api/users/${user.id}`);
// Now you SEE the actual data, not what you assumed
```

### "Sleep On It"

Step away for 15 minutes. Fresh eyes find bugs faster than staring at the same code for an hour.

---

## 6. Preventing Bug Reintroduction

Prevent the same bug from happening again.

### 1. Write a Regression Test

For EVERY bug you fix, write a test that would have caught it.

```javascript
// Bug: Email validation was cutting off domain
// Test:
describe('validateEmail', () => {
  it('accepts emails with multi-level domains', () => {
    expect(validateEmail('user@sub.domain.co.uk')).toBe(true);
    expect(validateEmail('test@example.com')).toBe(true);
  });

  it('rejects invalid emails', () => {
    expect(validateEmail('invalid')).toBe(false);
    expect(validateEmail('user@')).toBe(false);
  });
});
```

### 2. Add Invariant Assertions

Document assumptions in code. Fail loudly if they're violated.

```javascript
function processOrder(items, customerId) {
  // Invariant: items must not be empty
  console.assert(items.length > 0, 'Order cannot have zero items');

  // Invariant: customer must exist
  console.assert(customerId > 0, 'Invalid customer ID');

  const total = items.reduce((sum, item) => sum + item.price, 0);

  // Invariant: total must be positive
  console.assert(total > 0, 'Order total must be positive');

  return createOrder(customerId, items, total);
}
```

### 3. Document in Commit Message

Commit messages should explain the bug AND why the fix works.

```
WRONG:
commit abc123
  Fix email validation

RIGHT:
commit abc123
  Fix: Email validation regex was non-greedy

  Bug: validateEmail was cutting domains at first dot,
  turning "user@sub.domain.com" into "user@sub".

  Root cause: Regex /.+@.+/ was non-greedy, matching
  minimal domain. Changed to /.+@.+$/ with greedy
  quantifier and added test cases for multi-level domains.

  Fixes #1234
```

### 4. Search for Similar Patterns

Once you fix a bug, search the codebase for similar problems.

```bash
# If you fixed an off-by-one error in loop condition:
grep -r "for.*< .*\.length - 1" .

# If you fixed a missing cleanup in useEffect:
grep -r "useEffect.*addEventListener" .

# Review each match to see if it has the same bug
```

### 5. Add to Project's Common Bugs Checklist

Create a document tracking bugs your team commonly makes.

```markdown
# Common Bugs in Our Project

## Off-by-one in array loops
- Pattern: `for (i = 0; i < array.length - 1; i++)`
- Check all loops against this pattern in code review

## Missing cleanup in useEffect
- Pattern: `addEventListener` without cleanup
- Require: All `addEventListener` must have `removeEventListener` in return

## Stale closures
- Pattern: Event handlers without dependency array
- Check: Every useEffect with event handlers has complete deps
```

---

## Quick Debugging Checklist

When you encounter a bug, work through this systematically:

- [ ] **Reproduce** — Can you make it happen consistently?
- [ ] **Observe** — What changed? What should happen vs. what actually happens?
- [ ] **Trace** — Follow data from symptom backwards to source
- [ ] **Hypothesis** — What do I think is causing this? Why?
- [ ] **Test** — Does the data confirm or refute my hypothesis?
- [ ] **Fix** — Make the minimal change to correct the root cause
- [ ] **Verify** — Does the bug disappear? Did you create new bugs?
- [ ] **Test** — Write a regression test so this doesn't happen again
- [ ] **Prevent** — Are there similar patterns in the codebase?

---

## 7. Concurrency & Race Condition Debugging Protocol

Race conditions are among the hardest bugs to debug because they are non-deterministic. This section provides a systematic protocol to identify, isolate, and fix concurrency bugs correctly.

### 7.1 How to Identify a Concurrency Bug vs. a Logic Bug

Concurrency bugs have distinctive signatures that differ from regular logic bugs. Before writing a single fix, check if your bug exhibits 2 or more of these signs:

**Four Diagnostic Signatures:**

1. **Intermittent** — The bug does not happen on every run. Same code path, same input, sometimes it works, sometimes it fails.

2. **Heisenbug** — The bug disappears when you add `console.log` statements. The act of observing (logging) changes the behavior, usually by introducing tiny delays that alter timing.

3. **Timing-dependent** — The bug changes behavior with network throttling or CPU slowdown. Throttling the network in DevTools makes it worse or better. Running on a slower machine changes the outcome.

4. **Order-dependent** — Adding a `setTimeout` delay fixes the symptom (masking, not fixing). For example, wrapping one async operation in `setTimeout(..., 100)` makes the bug go away.

**Decision rule:** If 2 or more are true, treat it as concurrency, not logic. Do not use a logic debugging approach—you will waste hours.

### 7.2 The Identification Protocol — Before Touching Any Code

The key to fixing race conditions is understanding the overlap. Never write a fix until you understand exactly which operations overlap in time. Follow this 4-step protocol:

**Step 1: Add a requestId to every async operation**

Each async operation needs a unique identifier so you can track it through logs:

```javascript
async function fetchUserData(userId) {
  const reqId = Math.random().toString(36).slice(2, 8);
  console.log(`[${reqId}] fetch started for user ${userId}`);

  try {
    const response = await fetch(`/api/users/${userId}`);
    const data = await response.json();
    console.log(`[${reqId}] fetch resolved with data:`, data);
    return data;
  } catch (error) {
    console.log(`[${reqId}] fetch aborted or failed:`, error.message);
    throw error;
  }
}
```

**Step 2: Log start/resolve/abort with that ID**

Every state change in the async operation must log with the ID:

```javascript
async function fetchUserData(userId) {
  const reqId = Math.random().toString(36).slice(2, 8);

  console.log(`[${reqId}] fetch started`);
  const response = await fetch(`/api/users/${userId}`);

  console.log(`[${reqId}] fetch resolved`);
  const data = await response.json();

  console.log(`[${reqId}] response parsed, setting state`);
  setUser(data);

  // If this operation gets aborted:
  console.log(`[${reqId}] fetch aborted — stale`);
}
```

**Step 3: Read the log. Find which IDs overlap in time.**

Open the browser console and read the logs from top to bottom:

```
[a3x4f2] fetch started
[b8k2q1] fetch started
[a3x4f2] fetch resolved
[b8k2q1] fetch resolved
```

Here, both started before either resolved. That's the race. `b8k2q1` might resolve first, but `a3x4f2` might overwrite its data.

```
[a3x4f2] fetch started
[a3x4f2] fetch resolved
[b8k2q1] fetch started
[b8k2q1] fetch resolved
```

Here, they do not overlap. No race.

**Step 4: The overlap IS the race. Now you know what to fix.**

Once you see the overlap in the logs, you've found the root cause. Do not write the fix until this step is complete. You must know WHICH operations race, not just guess.

**Rule:** Do not write the fix until Step 4 is complete. Skipping this step leads to incorrect or incomplete fixes.

### 7.3 The Three Correct Fix Patterns

There are only three correct patterns for fixing race conditions. Any other approach (try/catch, delay, promise ordering) is a mask, not a fix.

#### Pattern A — AbortController (Fetch Races, Most Common)

Use this when multiple `fetch` calls can happen in quick succession and you want only the latest to succeed.

```javascript
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    // Cancel any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create a new controller for this request
    abortControllerRef.current = new AbortController();
    const reqId = Math.random().toString(36).slice(2, 8);

    console.log(`[${reqId}] fetch started for user ${userId}`);

    fetch(`/api/users/${userId}`, { signal: abortControllerRef.current.signal })
      .then(res => res.json())
      .then(data => {
        // Check if this is still the current request
        // (not strictly necessary with AbortController, but good practice)
        console.log(`[${reqId}] fetch resolved`);
        setUser(data);
      })
      .catch(error => {
        // AbortError is expected when request is cancelled
        if (error.name === 'AbortError') {
          console.log(`[${reqId}] fetch aborted — stale`);
        } else {
          console.error(`[${reqId}] fetch error:`, error);
        }
      });

    // Cleanup: abort on unmount or when userId changes
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [userId]);

  return user ? <div>{user.name}</div> : <div>Loading...</div>;
}
```

**When to use:** Every time you fetch based on a prop or state that can change (userId, searchTerm, filters, etc.).

#### Pattern B — useRef for Latest Value (Stale Closures in Event Handlers)

Use this when an event handler needs to access the latest state value, not a stale closure.

```javascript
function SearchBox() {
  const [query, setQuery] = useState('');
  const queryRef = useRef(query); // Keep ref in sync with state

  useEffect(() => {
    queryRef.current = query; // Update ref whenever query changes
  }, [query]);

  const handleSearch = () => {
    // Use ref.current, not the query from closure
    // This is the LATEST value, not what it was at mount time
    console.log('Searching for:', queryRef.current);
    fetch(`/api/search?q=${queryRef.current}`);
  };

  useEffect(() => {
    // Event listener that needs latest query
    const handleKeyDown = (event) => {
      if (event.key === 'Enter') {
        // Use ref.current, not query from closure
        handleSearch();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []); // Empty deps is OK because we use ref, not closure

  return (
    <input
      value={query}
      onChange={e => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

**When to use:** When event listeners or callbacks added at mount need to access current state, but you can't change the dependency array.

#### Pattern C — Sequential Mutex (Operations That Must Not Overlap)

Use this when operations must complete one at a time and never in parallel (form submissions, payment flows, irreversible operations).

```javascript
function PaymentForm() {
  const [isProcessing, setIsProcessing] = useState(false);
  const isProcessingRef = useRef(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Prevent concurrent submissions
    if (isProcessingRef.current) {
      console.log('Submission already in progress');
      return;
    }

    isProcessingRef.current = true;
    setIsProcessing(true);
    const reqId = Math.random().toString(36).slice(2, 8);

    console.log(`[${reqId}] payment started`);

    try {
      const response = await fetch('/api/payments', {
        method: 'POST',
        body: JSON.stringify({ amount: 100 })
      });

      const data = await response.json();
      console.log(`[${reqId}] payment resolved`);
      setOrderComplete(true);
    } catch (error) {
      console.error(`[${reqId}] payment failed:`, error);
      setError('Payment failed. Please try again.');
    } finally {
      isProcessingRef.current = false;
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" placeholder="Card number" />
      <button type="submit" disabled={isProcessing}>
        {isProcessing ? 'Processing...' : 'Pay'}
      </button>
    </form>
  );
}
```

**When to use:** Form submissions, payment processing, database writes, or any operation that must not happen twice simultaneously.

### 7.4 The One Rule (Cannot Be Missed)

There is one critical rule you must follow. Violating it creates a false sense of security while leaving the race condition intact.

**Never fix a race condition with:**
- **try/catch** — This hides the error, but does not eliminate the race. The stale operation still overwrites the new one.
- **setTimeout delay** — This masks the timing, but breaks under load. Add a 100ms delay and it works in development, then fails in production under network congestion.
- **Re-ordering awaits without understanding the overlap** — Moving `await` statements around without first identifying the overlap (Step 4 above) is random guessing.

**The only valid fixes are:**
1. **Stale response is discarded** — The new result overwrites the old (AbortController pattern)
2. **Operations complete in a guaranteed safe order** — Operations cannot happen in parallel, or if they do, order doesn't matter (Mutex pattern)
3. **Latest value is always accessible** — State/closure is never stale (useRef pattern)

Anything else is a mask. It will work in some conditions and fail in others. Debug your fix the same way you debugged the original bug: add requestId logging, trigger the race, read the logs, and verify the overlap is eliminated.

