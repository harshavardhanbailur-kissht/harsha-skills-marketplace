# Fix Safety Guide: The Ultimate-Debugger Reference

This is the MOST CRITICAL reference file for the ultimate-debugger skill. Every bug fix must pass L1-L4 mandatory verification (Syntax, Types, Lint, Tests). L5-L8 levels are applied proportionally based on fix complexity, with automatic escalation to full L1-L8 for critical/high severity or unexpected L1-L4 signals.

## 1. The 8-Level Verification Hierarchy

### Level 1: SYNTAX
Parse the file with the correct parser. If it doesn't parse, the fix is broken.

**Implementation:**
- **JavaScript/JSX:** Use Babel (`@babel/parser`)
- **TypeScript:** Use TypeScript compiler (`tsc`)
- **CSS:** Use PostCSS or native CSS parser
- **JSON:** Use JSON.parse()

**Command:**
```bash
# JavaScript/TypeScript
npx tsc --noEmit src/**/*.ts

# JSX validation
npx babel src/ --parser=babel --no-babelrc > /dev/null

# JSON
node -c "JSON.parse(require('fs').readFileSync('file.json'))"
```

**Verification:** If the file doesn't parse, STOP. The fix is syntactically broken.

### Level 2: TYPES
Run `tsc --noEmit`. Zero new type errors allowed. Type errors mask real problems.

**Command:**
```bash
npx tsc --noEmit
```

**Red flags:**
- `any` type introduced (hides type safety)
- `@ts-ignore` or `@ts-expect-error` (bypasses safety)
- `as` casts without justification (lying to TypeScript)
- `Object` or `unknown` as catch-all types

**Verification:** Run full type check. No new errors. No type regressions.

### Level 3: LINT
Run ESLint or Biome. Zero new warnings. Linting catches:
- Unused variables (dead code)
- Unreachable code (logic error)
- Hook violations (React.rules-of-hooks)
- Missing exhaustive dependencies (stale closures)
- Missing error handling (unhandled promises)

**Command:**
```bash
npx eslint src/ --fix
npx biome lint src/ --fix
```

**Critical rules:**
- `eslint-plugin-react-hooks/exhaustive-deps` (catch stale closures)
- `no-undef` (catch typos)
- `no-unused-vars` (catch dead code)
- `no-unreachable` (catch logic errors)

**Verification:** Zero new warnings introduced by the fix.

### Level 4: TESTS
Run the full test suite. All existing tests must pass. If a test fails, the fix broke something.

**Command:**
```bash
npm test -- --coverage --testPathPattern="."
```

**Verification criteria:**
- All tests pass (not just the new ones)
- No test timeouts (performance didn't regress)
- Coverage doesn't decrease
- No flaky tests introduced

**Red flag:** "This test was already flaky" is not an excuse.

### Level 5: REGRESSION TEST
Write a test that would have caught THIS specific bug. Run it. It must pass with the fix and fail without it.

**Template:**
```javascript
describe('BUG-1234: [Bug title]', () => {
  it('reproduces the original bug', () => {
    const input = /* the data that triggered the bug */;
    const result = functionUnderTest(input);
    expect(result).toBe(expectedOutput);
  });

  it('handles edge case that triggered the bug', () => {
    // Test the specific condition that was broken
  });
});
```

**Verification:**
- Run with the fix: PASS
- Run without the fix (revert code): FAIL
- Add to test suite permanently

### Level 6: PERFORMANCE
Run profiling harness. Frame time p95 must not increase. Bundle size must not increase by >1KB. Memory growth must not increase.

**Metrics to measure:**
- Frame time p95 (time to interactive)
- Bundle size (gzip + minified)
- Memory growth (initial load → steady state)
- GC pause time (if applicable)

**Command:**
```bash
npm run perf:profile
npm run perf:bundle-analyze
npm run perf:memory
```

**Thresholds:**
- Frame time p95: No increase
- Bundle size: <1KB increase
- Memory: No unexpected growth

**Red flags:**
- "It's probably fine" without measurement
- Lazy loading removed to "simplify" code
- Memoization removed without justification

### Level 7: VISUAL
For UI changes: take screenshot before/after. Compare pixel-perfect. No unintended visual changes for SAFE/MODERATE tier fixes.

**Steps:**
1. Checkout main branch
2. Run app, take screenshot of affected component
3. Checkout fix branch
4. Run app, take screenshot of same component
5. Compare: intentional changes only

**Tools:**
- Jest snapshots for component rendering
- Percy or Chromatic for visual regression
- Manual pixel-perfect comparison for critical UI

**Verification:** Only intended visual changes present.

### Level 8: SECURITY
For security fixes: verify the vulnerability is actually closed. Try to exploit it. Check for related vulnerabilities in nearby code.

**For XSS fixes:**
```javascript
// Before fix: vulnerability exists
const html = userInput; // "alert('xss')"
element.innerHTML = html; // EXPLOITED

// After fix: vulnerability closed
element.textContent = userInput; // Safe
// OR
const sanitized = DOMPurify.sanitize(userInput);
element.innerHTML = sanitized; // Safe
```

**Verification steps:**
1. Create exploit payload
2. Try to trigger vulnerability with fix: FAILS
3. Remove fix, try payload again: SUCCEEDS (proves vulnerability was real)
4. Search nearby code for similar vulnerabilities

**Related checks:**
- XSS: Check innerHTML, dangerouslySetInnerHTML, eval, Function()
- CSRF: Verify token present, check SameSite cookie
- SQL Injection: Verify parameterized queries, not string concat
- Command Injection: Verify shell escaping, use safe APIs

---

## 2. Safe Fix Templates

### Template 1: Null/Undefined Access

**SAFE approach:**
```javascript
// Option A: Optional chaining with fallback
const value = obj?.prop?.nested ?? defaultValue;

// Option B: Guard clause
if (!obj?.prop) {
  return handleMissing();
}
const value = obj.prop;

// Option C: Non-null assertion (only if 100% certain)
const value = obj.prop!; // Type system proves it's not null
```

**UNSAFE approach:**
```javascript
// WRONG: Non-null assertion without proof
const value = obj.prop!; // Lies to TypeScript

// WRONG: Empty catch (silently fails)
try {
  return obj.prop.method();
} catch {
  return undefined; // What actually went wrong?
}

// WRONG: Falsy trap (0 is not null)
const count = obj.count || 1; // Breaks if count is 0
```

**Verification:**
- No type assertions without justification
- Fallback values are meaningful
- All null paths handled

### Template 2: Missing Cleanup (useEffect)

**SAFE approach:**
```javascript
// Async operations with AbortController
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/data', { signal: controller.signal })
    .then(r => r.json())
    .then(data => setState(data))
    .catch(err => {
      if (err.name !== 'AbortError') console.error(err);
    });

  return () => controller.abort();
}, []);

// Event listeners
useEffect(() => {
  const handler = (e) => handleEvent(e);
  window.addEventListener('resize', handler);
  return () => window.removeEventListener('resize', handler);
}, []);

// Timers
useEffect(() => {
  const id = setTimeout(() => setState(true), 1000);
  return () => clearTimeout(id);
}, []);
```

**UNSAFE approach:**
```javascript
// WRONG: No cleanup
useEffect(() => {
  fetch('/api/data').then(r => r.json()).then(setState);
}, []); // Memory leak on unmount

// WRONG: Just adding cleanup without thinking
useEffect(() => {
  window.addEventListener('scroll', () => {});
  return () => {}; // Cleanup removed the listener but not stored handler
}, []);
```

**Verification:**
- Return cleanup function from useEffect
- Cleanup actually removes listeners/timers/subscriptions
- Test with React StrictMode (runs effects twice)

### Template 3: Stale Closure

**SAFE approach:**
```javascript
// Option A: Proper dependency array
useEffect(() => {
  const timer = setInterval(() => {
    // Can access 'count' because it's in dependencies
    setCount(count + 1);
  }, 1000);
  return () => clearInterval(timer);
}, [count]); // Include all dependencies

// Option B: useRef for latest value
const countRef = useRef(count);
useEffect(() => {
  countRef.current = count;
}, [count]);

useEffect(() => {
  const timer = setInterval(() => {
    setCount(countRef.current + 1); // Always has latest value
  }, 1000);
  return () => clearInterval(timer);
}, []); // No dependency on count, timer never recreated

// Option C: Functional updates
useEffect(() => {
  const timer = setInterval(() => {
    setCount(prev => prev + 1); // prev is always current
  }, 1000);
  return () => clearInterval(timer);
}, []); // Empty deps OK because of functional update
```

**UNSAFE approach:**
```javascript
// WRONG: Ignoring eslint-disable warning
useEffect(() => {
  const timer = setInterval(() => {
    // count is stale, but we're silencing the warning
    setCount(count + 1);
  }, 1000);
  return () => clearInterval(timer);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []); // Stale closure, but ignored

// WRONG: Adding all deps blindly (causes infinite loop)
useEffect(() => {
  const handler = () => setData([...data]);
  window.addEventListener('change', handler);
  return () => window.removeEventListener('change', handler);
}, [data]); // Creates new handler every time data changes
```

**Verification:**
- ESLint exhaustive-deps passes without disable
- No infinite loops (set dependency array correctly)
- Test with and without dependencies

### Template 4: Memory Leak

**SAFE approach:**
```javascript
// Identify the leak source, then fix it
class Component {
  listeners = [];

  subscribe(callback) {
    this.listeners.push(callback);
    // WRONG: No return, caller can't unsubscribe

    // RIGHT: Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }
}

// Usage
const unsubscribe = component.subscribe(handler);
// Later:
unsubscribe(); // Actually removes the listener
```

**UNSAFE approach:**
```javascript
// WRONG: Setting to null without removing root cause
let listener = handler;
// Later:
listener = null; // Listener still in listeners array!

// WRONG: Circular reference
const obj = { ref: obj }; // Creates garbage collection issue
// Setting obj = null doesn't help; GC can't collect it
```

**Verification:**
- Take heap snapshot before/after
- Check for retained event listeners
- Verify cleanup functions are called
- Test with long-running app (steady memory usage)

### Template 5: Race Condition

**SAFE approach:**
```javascript
// AbortController + stale response check
const [version, setVersion] = useState(0);

useEffect(() => {
  const controller = new AbortController();
  const currentVersion = version;

  fetch(`/api/data?v=${version}`, { signal: controller.signal })
    .then(r => r.json())
    .then(data => {
      if (currentVersion === version) {
        // This response is still relevant
        setState(data);
      }
      // If version changed, we ignore this response (was superseded)
    });

  return () => controller.abort();
}, [version]);

// Mutex/lock pattern (for complex state)
let pending = false;
async function handleClick() {
  if (pending) return; // Already processing
  pending = true;
  try {
    const result = await fetch();
    setState(result);
  } finally {
    pending = false;
  }
}
```

**UNSAFE approach:**
```javascript
// WRONG: Trying to catch the race
try {
  const data = await fetch1();
  setState(data);
} catch {
  // Hides the race condition
}

// WRONG: Adding delays (timing-dependent)
await sleep(100); // Now it works... sometimes
setState(data);

// WRONG: Ignoring Promise rejection
fetch().then(setState); // Unhandled if fetch fails
```

**Verification:**
- Simulate slow network (DevTools throttling)
- Trigger rapid state changes
- Verify only latest request's response is used
- Test with React.StrictMode (renders twice)

### Template 6: XSS (Cross-Site Scripting)

**SAFE approach:**
```javascript
// Option A: textContent instead of innerHTML
element.textContent = userInput; // Always safe, treats as text

// Option B: Sanitization library
import DOMPurify from 'dompurify';
const sanitized = DOMPurify.sanitize(userInput);
element.innerHTML = sanitized; // Removes all dangerous tags

// Option C: Parameterized/safe APIs
// React: automatically escapes by default
<div>{userInput}</div> // Safe, rendered as text

// Canvas/WebGL: use native APIs, not string concat
ctx.fillText(userInput, x, y); // No XSS vector

// URLs: use URL constructor
const url = new URL('https://example.com?' + new URLSearchParams({ query: userInput }));
element.href = url.href; // URL-safe
```

**UNSAFE approach:**
```javascript
// WRONG: Regex-based sanitization (always bypassable)
const sanitized = userInput.replace(/<script>/gi, ''); // Easily bypassed: <scr<script>ipt>
element.innerHTML = sanitized;

// WRONG: Encoding only (misses contexts)
const encoded = userInput.replace(/</g, '&lt;'); // Safe for HTML, not for JavaScript
element.innerHTML = `<img onerror="alert('${encoded}')">`; // Still XSS!

// WRONG: Template literals with user input
element.innerHTML = `<div>${userInput}</div>`; // Direct interpolation, vulnerable

// WRONG: dangerouslySetInnerHTML without sanitization (React)
<div dangerouslySetInnerHTML={{ __html: userInput }} /> // XSS vulnerability
```

**Verification:**
- Payload: `<img src=x onerror="alert('xss')">`
- Payload: `<svg onload="alert('xss')">`
- Payload: `javascript:alert('xss')`
- Try each with the fix: no alert
- Remove fix, try payload: alert fires (proves vulnerability was real)

### Template 7: Infinite Loop/Render

**SAFE approach:**
```javascript
// Option A: Remove the trigger
// WRONG: state in render causes infinite loop
function Component() {
  const [count, setCount] = useState(0);
  setCount(count + 1); // Runs on every render, calls setCount, triggers re-render
  return <div>{count}</div>;
}

// RIGHT: Move to useEffect with proper deps
function Component() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    setCount(count + 1); // Runs once, not on every render
  }, [count]);
  return <div>{count}</div>;
}

// Option B: Add guard + max iterations
let renderCount = 0;
function safeRender() {
  if (renderCount > 100) {
    console.error('Infinite render detected');
    return null;
  }
  renderCount++;
  return <Component />;
}

// Option C: Wrong dependency array
// WRONG: Object created fresh on each render
const config = { timeout: 5000 }; // New object each time
useEffect(() => {
  setup(config);
}, [config]); // Dependency changed, runs every render

// RIGHT: Move outside or memoize
const config = useMemo(() => ({ timeout: 5000 }), []);
useEffect(() => {
  setup(config);
}, [config]); // Same object, runs once
```

**UNSAFE approach:**
```javascript
// WRONG: break without fixing root cause
while (true) {
  setState(value);
  if (iterations > 100) break; // "Fixes" the loop but doesn't solve it
}

// WRONG: Adding return without fixing cause
useEffect(() => {
  setState(data);
  if (data) return; // Still causes re-render, just stops second time
}, [data]); // Dependency on data causes loop
```

**Verification:**
- Render component, check for hanging browser
- Devtools Performance tab: no excessive renders
- React DevTools: check render count (should be 1, 2 with StrictMode)
- Test with large dependency arrays: no loops

### Template 8: Type Error

**SAFE approach:**
```javascript
// Option A: Proper type narrowing with typeof
function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase(); // value is narrowed to string
  }
  return value.toFixed(2); // value is narrowed to number
}

// Option B: instanceof check
function handle(obj: unknown) {
  if (obj instanceof Error) {
    return obj.message; // obj is Error
  }
  return String(obj);
}

// Option C: Discriminated unions
type Result = { success: true; data: string } | { success: false; error: string };
function process(result: Result) {
  if (result.success) {
    return result.data; // TypeScript knows data exists
  }
  return result.error; // TypeScript knows error exists
}

// Option D: User-defined type guard
function isString(value: unknown): value is string {
  return typeof value === 'string';
}
if (isString(value)) {
  return value.length; // value is string
}
```

**UNSAFE approach:**
```javascript
// WRONG: Type assertion (lying to TypeScript)
const str = value as string; // Assertion, no runtime check
return str.length; // Crashes if value wasn't a string

// WRONG: any type (disables type safety)
const value: any = getData();
value.anything(); // Type error hidden until runtime

// WRONG: @ts-ignore (bypasses safety)
// @ts-ignore
value.nonexistentProp; // Type error silenced

// WRONG: Non-null assertion without proof
const value = getMaybeString()!;
return value.length; // What if getMaybeString() returned null?
```

**Verification:**
- Run `tsc --strict` (strict null checks)
- No `as` casts without documentation
- No `any` types
- No `@ts-ignore` comments

---

## 3. Regression Prevention Protocol

**BEFORE fixing the bug:**
```bash
# Write a test that fails (proves the bug exists)
npm test -- BUG-1234 # Test fails
```

**AFTER fixing the bug:**
```bash
# Run the test (proves the fix works)
npm test -- BUG-1234 # Test passes

# Run all tests (proves we didn't break anything)
npm test # All tests pass
```

**ALWAYS add the test to the suite:**
```javascript
// tests/BUG-1234.test.js
describe('BUG-1234: [Short bug description]', () => {
  it('reproduces the original bug scenario', () => {
    const input = /* trigger data */;
    const result = brokenFunction(input);
    expect(result).toBe(expectedOutput);
  });

  it('handles related edge case', () => {
    // Secondary edge case that also failed
  });
});
```

**Verification checklist:**
- [ ] Test fails without the fix
- [ ] Test passes with the fix
- [ ] Test is in permanent test suite
- [ ] All other tests still pass
- [ ] Test name starts with BUG-XXXX for easy tracking

---

## 4. Common Fix Failure Modes

| Failure Mode | Cause | Prevention |
|---|---|---|
| Fix removes bug but breaks related feature | Limited testing scope | Run full test suite, integration tests |
| Fix introduces performance regression | No measurement | Profile before/after, check bundle size |
| Fix works in isolation but conflicts with other code | No integration testing | Test with dependent modules |
| Fix addresses symptom, not root cause | Shallow analysis | Root cause analysis first, write test that proves fix |
| Fix introduces new dependency that bloats bundle | No dep review | Check bundle impact, use alternatives |
| Fix changes public API signature | No API review | Check all callers, use deprecation period |
| Fix creates dead code | Incomplete refactoring | Run linter, check code coverage |
| Fix breaks in edge cases | Limited test coverage | Write edge case tests, use property-based testing |
| Fix has unintended visual changes | No visual testing | Take screenshots before/after |
| Fix breaks accessibility | No a11y testing | Run axe-core, test with screen reader |

---

## 5. Rollback Strategy

**Pre-fix: Prepare for rollback**
```bash
# Create a branch for the fix
git checkout -b fix/BUG-1234

# Or stash changes
git stash
```

**During fix: Commit early, commit often**
```bash
git add specific-file.js
git commit -m "Fix: narrow down issue to specific-file.js"

git add another-file.js
git commit -m "Fix: address root cause in another-file.js"

git add tests/
git commit -m "Add regression test for BUG-1234"
```

**If verification fails: Rollback immediately**
```bash
# Option A: Branch-based rollback
git checkout main

# Option B: Stash-based rollback
git stash pop # Restores the stashed changes

# Option C: Individual file rollback
git checkout HEAD -- broken-file.js

# Option D: Undo last commit (keeps changes)
git reset --soft HEAD~1
```

**Production: Feature flags for gradual rollout**
```javascript
if (featureFlags.get('FIX_BUG_1234')) {
  // New code path
  return fixedBehavior();
} else {
  // Old code path (for rollback)
  return originalBehavior();
}
```

**NEVER do this:**
```bash
# WRONG: Force push over history
git push --force origin main

# WRONG: Revert without documenting reason
git revert <commit> # No explanation

# WRONG: Rebase after pushing (rewrites history)
git rebase -i main
```

---

## 6. Fix Quality Scoring Rubric

Score each dimension 1-5 (higher is better):

### Minimal (Diff size)
- **5:** 1-3 lines changed (surgical fix)
- **4:** 4-10 lines changed (targeted fix)
- **3:** 11-30 lines changed (moderate refactor)
- **2:** 31-100 lines changed (large refactor)
- **1:** >100 lines changed (rewrite, high risk)

### Safe (Side effects)
- **5:** Zero risk of side effects
- **4:** Low risk (isolated change)
- **3:** Moderate risk (mitigated by tests)
- **2:** High risk (changes shared code)
- **1:** Changes public API, impacts callers

### Clean (Code quality)
- **5:** Exemplary (reference-quality code)
- **4:** Good (clear, maintainable)
- **3:** Acceptable (works, readable)
- **2:** Messy (works but hard to read)
- **1:** Sloppy (copy-paste, hacks)

### Tested (Test coverage)
- **5:** Regression test + edge cases
- **4:** Regression test + happy path
- **3:** Manual test, no automated test
- **2:** Runs without error
- **1:** Untested

### Root Cause (Does it fix the root?)
- **5:** Root cause eliminated
- **4:** Root cause mitigated
- **3:** Symptom fixed (fragile)
- **2:** Workaround (may break later)
- **1:** Band-aid (doesn't address issue)

### Scoring Example
```
Fix for BUG-1234: Null pointer exception on profile page

Minimal:     5 (changed 2 lines: added null check)
Safe:        5 (only affects error path)
Clean:       5 (simple guard clause)
Tested:      4 (regression test, happy path)
Root Cause:  5 (identified where null came from, fixed it)

Total Score: 24/25 (96%)
Quality: EXCELLENT - Ready to merge
```

### Quality Tiers
- **24-25:** EXCELLENT - Merge immediately
- **20-23:** GOOD - Review and merge
- **15-19:** ACCEPTABLE - Address concerns before merge
- **10-14:** POOR - Rethink approach
- **<10:** REJECT - Rewrite required

---

## Quick Reference Checklist

Before submitting any bug fix:

- [ ] Code parses without syntax errors (Level 1)
- [ ] No new type errors (Level 2: `tsc --noEmit`)
- [ ] No new lint warnings (Level 3: `eslint --fix`)
- [ ] All tests pass (Level 4: `npm test`)
- [ ] Regression test written and passes (Level 5)
- [ ] Performance metrics stable (Level 6)
- [ ] Visual changes intentional (Level 7)
- [ ] Security vulnerability closed (Level 8, if applicable)
- [ ] Diff is minimal and focused
- [ ] Root cause addressed, not just symptom
- [ ] Test is added to permanent test suite
- [ ] Rollback plan documented
- [ ] Quality score is >15/25

**If any item is unchecked, DO NOT MERGE.**
