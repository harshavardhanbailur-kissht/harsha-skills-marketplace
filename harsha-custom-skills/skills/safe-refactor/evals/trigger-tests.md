# Trigger Tests for safe-refactor

## Should Trigger (7)

1. "refactor this file to reduce the cyclomatic complexity, it's getting hard to follow the logic"
2. "clean up the code in src/utils/ — there's a lot of duplication and dead code"
3. "this function has gotten way too long, can you break it up into smaller pieces without changing what it does"
4. "i want to modernize our python codebase — convert os.path to pathlib, add type hints, replace old string formatting with f-strings"
5. "make this more maintainable — the nesting is 6 levels deep and there are magic numbers everywhere"
6. "we've got a god class in UserService.java that handles auth, validation, email, and database — can you decompose it safely"
7. "simplify this typescript file, there's a bunch of any types and callback hell that should be cleaned up"

## Should NOT Trigger (3)

8. "add a dark mode toggle to the settings page" — This is a FEATURE request, not refactoring
9. "fix the bug where users can't log in after password reset" — This is a BUG fix, not refactoring
10. "review this PR and tell me if the code looks good" — This is CODE REVIEW, not refactoring
