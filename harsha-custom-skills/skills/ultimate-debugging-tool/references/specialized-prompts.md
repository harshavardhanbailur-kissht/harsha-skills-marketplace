# Specialized Debugging Prompts

Optimized prompts for different bug categories. Use these templates for maximum detection accuracy with minimal tokens.

## Security Scanning Prompt

```
You are a security auditor. Analyze this code for vulnerabilities.

FOCUS ON:
- SQL injection (CWE-89): String concatenation in queries
- XSS (CWE-79): Unsanitized output in HTML
- Command injection (CWE-78): os.system, subprocess with user input
- Path traversal (CWE-22): File operations with user-controlled paths
- Hardcoded secrets (CWE-798): Passwords, API keys, tokens in code

For each finding, if vulnerable, identify the fix approach.

OUTPUT FORMAT (JSON only, no prose):
{"bugs":[{"id":"B001","loc":"file.py:42","cat":"security","cwe":"CWE-89","sev":"high","desc":"SQL injection via f-string","fix":"Use parameterized query"}]}

If no bugs found: {"bugs":[]}

CODE:
```

### Security Detection Tips

- Check for `f"SELECT` or `f'SELECT` patterns
- Look for `+ query` or `% query` string operations
- Flag any `password =`, `secret =`, `api_key =` literals
- Watch for `eval(`, `exec(`, `os.system(` with variables
- Check `open(` with user-controllable paths

## Logic Bug Scanning Prompt

```
You are a code quality expert. Analyze for logic errors.

FOCUS ON:
- Null/None dereference: Accessing attributes without null check
- Off-by-one errors: Array bounds, loop conditions
- Race conditions: Shared state in async/threaded code
- Unhandled exceptions: Bare except, missing error handling
- Type mismatches: Implicit conversions, wrong types

OUTPUT FORMAT (JSON only):
{"bugs":[{"id":"B001","loc":"file.py:42","cat":"logic","sev":"medium","desc":"Potential null dereference on user.name"}]}

CODE:
```

### Logic Detection Tips

- Look for `.get(` without default value checks
- Check `for i in range(len(` patterns (often off-by-one)
- Flag `except:` or `except Exception:` with just `pass`
- Watch for `if x:` when `if x is not None:` is needed
- Check async functions modifying shared state

## Performance Scanning Prompt

```
You are a performance engineer. Identify inefficiencies.

FOCUS ON:
- N+1 queries: Database calls inside loops
- Unbounded growth: Lists/dicts without size limits
- Expensive operations in loops: I/O, regex compilation
- Memory leaks: Resources not closed, circular refs
- O(n²) algorithms: Nested loops over same collection

OUTPUT FORMAT (JSON only):
{"bugs":[{"id":"B001","loc":"file.py:42","cat":"performance","sev":"medium","desc":"N+1 query pattern in user loop"}]}

CODE:
```

### Performance Detection Tips

- Check for `for` loops containing `.query(`, `.filter(`, `.get(`
- Look for `.append(` inside `while True` without bounds
- Flag `re.compile` inside loops (should be module-level)
- Watch for nested `for x in items: for y in items:`
- Check file/connection handles without `with` statement

## Code Quality Scanning Prompt

```
You are a code reviewer. Identify quality issues.

FOCUS ON:
- Dead code: Unreachable statements, unused variables
- Magic numbers: Unexplained numeric literals
- Deep nesting: >3 levels of indentation
- Long functions: >50 lines without clear purpose
- Poor naming: Single letters, misleading names

OUTPUT FORMAT (JSON only):
{"bugs":[{"id":"B001","loc":"file.py:42","cat":"quality","sev":"low","desc":"Magic number 86400 (should be SECONDS_PER_DAY)"}]}

CODE:
```

## Combined Efficient Scan

For scanning all categories in one pass (use only when codebase is small):

```
Analyze for bugs in these categories: security, logic, performance, quality.

Priority order:
1. Security (high severity) - MUST report all
2. Logic (medium severity) - Report if clear
3. Performance (medium severity) - Report if obvious
4. Quality (low severity) - Report top 3 only

OUTPUT: Concise JSON, max 20 bugs total
{"bugs":[{"id":"B001","loc":"file:line","cat":"category","sev":"high|medium|low","desc":"brief"}]}
```

## Fix Generation Prompt

After identifying a bug, use this prompt to generate fixes:

```
Bug: {bug_description}
Location: {file}:{line}
CWE: {cwe_if_applicable}

Generate a minimal fix (prefer 2-5 lines over larger changes).

Requirements:
1. Fix ONLY the specific vulnerability
2. Preserve existing functionality
3. Follow existing code style
4. Add brief comment explaining the fix

OUTPUT FORMAT:
```yaml
fix:
  bug_id: "{bug_id}"
  changes:
    - line: {line_number}
      before: "original code"
      after: "fixed code"
  reasoning: "Why this fix works"
```
```

## Verification Prompt

After applying a fix:

```
Bug: {bug_description}
Original code: {before}
Fixed code: {after}

Verify:
1. Does the fix address the specific vulnerability?
2. Does the fix introduce any NEW issues?
3. Is the fix minimal and focused?
4. Would this pass code review?

OUTPUT (JSON):
{"verified":true,"confidence":0.95,"notes":"Parameterized query prevents injection"}

OR if issues found:
{"verified":false,"confidence":0.3,"issues":["Fix incomplete - still concatenates user_type"]}
```

## Token Optimization Tips

1. **Strip comments** before sending code to LLM
2. **Send only relevant functions**, not entire files
3. **Use line numbers** instead of repeating code
4. **Batch similar files** (same language/framework)
5. **Cache common patterns** - don't re-analyze unchanged code

### Concise Output Enforcement

Add to any prompt:
```
CRITICAL: Output ONLY valid JSON. No markdown, no explanation, no preamble.
```

### Context Reduction

For large files, provide skeleton:
```
File: auth.py (245 lines)
Imports: flask, sqlite3, hashlib
Functions: login(42-67), register(69-98), hash_password(100-105)
Classes: UserAuth(107-180)

Analyze function: login (lines 42-67)
[paste only those lines]
```
