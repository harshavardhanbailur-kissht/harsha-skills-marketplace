# Problem-Solving & Debugging

## Scientific Debugging Method

```
OBSERVE → HYPOTHESIZE → PREDICT → TEST → CONCLUDE → ITERATE
```

### Process
1. **Reproduce consistently** - If you can't reproduce, you can't reliably fix
2. **Gather evidence** - Error messages, console output, network requests, recent changes
3. **Formulate hypothesis** - Write it down: "The bug is caused by X because Y"
4. **Design test** - Change ONE variable at a time
5. **Execute & analyze** - Did test confirm or refute hypothesis?
6. **Document** - Root cause, fix, prevention

## Binary Search Debugging

When you have no idea where the bug is:
```
1. Find two points: working vs not working
2. Test the midpoint
3. Bug is in the failing half
4. Repeat until isolated
```

**Git bisect:**
```bash
git bisect start
git bisect bad          # Current is broken
git bisect good abc123  # This commit worked
# Git checks out middle, you test, mark good/bad
```

## The 5 Whys

```
Problem: Users can't log in
Why? → Session token is invalid
Why? → Token expired immediately  
Why? → Server clock is wrong
Why? → NTP service stopped
Why? → Container doesn't have NTP access
ROOT CAUSE: Container networking config
```

## Chrome DevTools

### Console
```javascript
console.table(arrayOrObject)      // Formatted table
console.group('Section')          // Collapsible groups
console.time('operation')         // Timing
console.trace()                   // Stack trace
```

### Breakpoints
- **Line-of-code**: Click line number
- **Conditional**: Right-click → "Add conditional breakpoint"
- **Logpoints**: Log without pausing
- **DOM**: Right-click element → "Break on subtree modifications"
- **XHR**: Pause on specific network requests

### Stepping
- `F8` Resume
- `F10` Step over
- `F11` Step into
- `Shift+F11` Step out

## Common Bug Quick Fixes

### JavaScript
| Symptom | Cause | Fix |
|---------|-------|-----|
| "undefined is not a function" | Calling on null | Optional chaining `?.` |
| "Cannot read property of undefined" | Data not loaded | Check loading state |
| "Maximum call stack exceeded" | Infinite recursion | Add base case |
| State not updating | Object mutation | Use spread operator |
| useEffect infinite loop | Wrong deps array | Audit dependencies |

### React
| Symptom | Cause | Fix |
|---------|-------|-----|
| Too many re-renders | Missing memo | `React.memo`, `useMemo`, `useCallback` |
| State updates not reflecting | Stale closure | Functional updates `setState(prev => ...)` |
| Hydration mismatch | Server/client differ | `useEffect` for client-only code |

### Network
| Symptom | Cause | Fix |
|---------|-------|-----|
| CORS error | Server config | Add CORS headers server-side |
| 401 Unauthorized | Token issue | Check auth header, expiration |
| 500 Error | Server bug | Check server logs |

### CSS
| Symptom | Cause | Fix |
|---------|-------|-----|
| Styles not applying | Specificity | DevTools → inspect applied styles |
| Flexbox not working | Missing display | Add `display: flex` to parent |
| Z-index not working | Missing position | Add `position: relative` |

## Before Asking for Help Checklist

- [ ] Exact error message copied
- [ ] Can reproduce consistently
- [ ] Checked browser console
- [ ] Checked server/terminal logs
- [ ] Tried incognito (no extensions)
- [ ] Cleared cache
- [ ] Checked for typos
- [ ] Verified imports
- [ ] Dependencies installed
- [ ] Compared working vs non-working code
- [ ] Searched error message online
- [ ] Reviewed recent changes (git diff)
