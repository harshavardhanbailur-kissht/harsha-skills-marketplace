# Quick Reference: V6 Skill Cheat Sheet

## Phase-by-Phase Quick Steps

### Phase 1: Analyze Codebase (1-2 hours)

```
Quick checklist:
□ Primary language and framework (grep -r "import\|require")
□ Total LOC (wc -l src/*)
□ Test coverage (grep -r "test" tests/ | wc -l)
□ Key dependencies (cat requirements.txt | head -20)
□ Architecture type (code-patterns.md: MVC? Microservices? Other?)
□ Main entry point (app.py? main.py? index.js?)

Output: 1-page overview of what this system is
```

### Phase 2: Map Architecture (2-3 hours)

```
Quick checklist:
□ Major components (find . -maxdepth 2 -type d)
□ Data flow (grep -r "database\|api\|queue")
□ External dependencies (stripe? database? cache?)
□ Error handling (grep -r "except\|try\|raise")
□ Configuration (grep -r "config\|environ\|getenv")

Use: code-patterns.md + language-patterns.md
Output: Architecture diagram + component list
```

### Phase 3: Extract Key Behaviors (2-3 hours)

```
Quick checklist:
□ Public APIs (grep -r "@app\|@route\|def handlers")
□ Data models (grep -r "class.*Model\|@dataclass\|interface")
□ Business logic (grep -r "def.*calculate\|def.*validate\|def.*process")
□ Error scenarios (grep -r "except\|HTTPException\|custom errors")
□ Test coverage (for critical paths)

Use: evidence-patterns.md + language-patterns.md
Output: API reference + data model diagrams
```

### Phase 4: Verify and Validate (2-3 hours)

```
Quick checklist:
□ Run tests (pytest / npm test / go test)
□ Check critical paths (trace order creation, payment, etc.)
□ Verify assumptions (does code match documentation?)
□ Cross-validate (code + tests + git agree?)
□ Check for inconsistencies (comments vs code)

Use: accuracy-verification.md + cross-validation.md
Output: Verification report, confidence scores
```

### Phase 5: Generate Documentation (2-3 hours)

```
Quick checklist:
□ Write overview (what is this system?)
□ Document architecture (why designed this way?)
□ List APIs (all endpoints, with examples)
□ Explain data models (entities and relationships)
□ Document configuration (how to run/deploy)
□ Add examples (working code snippets)
□ Include diagrams (Mermaid or ASCII)

Use: output-formats.md + cognitive-patterns.md
Output: Complete markdown documentation with YAML frontmatter
```

---

## Common Patterns Lookup

### "How do I document this pattern?"

**Microservices?**
- Use code-patterns.md: Microservices section
- Check separate git repos, independent deployment
- Verify service-to-service communication (REST, async)
- Document each service separately

**Authentication/OAuth?**
- Use security-documentation.md: Authentication section
- Show flow (login → token → validation)
- Document token format (JWT vs session)
- Example: curl with auth header

**Database queries?**
- Use language-patterns.md: Import analysis
- Check for ORM (SQLAlchemy, Django ORM, etc.)
- Document schema (data-models.md)
- Show example queries in tests

**Async processing?**
- Check for async keywords (async/await, @task, @celery.task)
- Document queue (Redis, RabbitMQ, SQS)
- Show job definition and result handling
- Example: enqueue and process flow

**Error handling?**
- Use security-documentation.md + completeness-checklists.md
- List all error types (grep -r "raise\|throw")
- Document each with recovery strategy
- Show in tests what triggers each error

**Configuration?**
- Find config sources (env vars, config files, defaults)
- Use completeness-checklists.md: Configuration section
- Document each parameter: name, type, default, purpose
- Example: .env file with explanations

---

## File Reference Guide

### Which Reference File Should I Use?

| Question | File |
|----------|------|
| "What patterns does this code use?" | code-patterns.md |
| "How does this language work?" | language-patterns.md |
| "Is this claim verified?" | evidence-patterns.md |
| "How do I explain this to different audiences?" | cognitive-patterns.md |
| "Is documentation complete?" | completeness-checklists.md |
| "What format should I use?" | output-formats.md |
| "How do I prompt for information?" | prompting-guide.md |
| "What technical debt is here?" | technical-debt.md |
| "How do I document security?" | security-documentation.md |
| "Should I use web research?" | web-research-patterns.md |
| "Why was this decided?" | decision-capture.md |
| "How do I draw diagrams?" | visual-documentation.md |
| "Do multiple sources agree?" | cross-validation.md |
| "How to verify accuracy?" | accuracy-verification.md |

---

## Common Commands

```bash
# Find main entry point
grep -r "if __name__\|def main\|function main" src/ | head -5

# Count functions/classes
grep -r "^def \|^class " src/ --include="*.py" | wc -l

# Find TODOs (decision markers)
grep -r "TODO\|HACK\|BUG\|FIXME" src/ --include="*.py"

# Extract public APIs
grep -r "@route\|@app\|@get\|@post" src/ --include="*.py"

# Find external dependencies
grep -r "^from\|^import" src/ | cut -d: -f2 | sort | uniq | head -30

# Check test coverage
find tests -name "test_*.py" | wc -l

# View git history for pattern
git log -S "pattern_name" --oneline | head -10

# Find code size
wc -l $(find src -name "*.py") | tail -1

# List directories (architecture)
find src -maxdepth 2 -type d | sort
```

---

## Handoff Readiness Checklist

```
Documentation Completeness:
  □ Overview: What is this system?
  □ Architecture: Why designed this way?
  □ Components: What are the major parts?
  □ APIs: All endpoints documented
  □ Data models: Entities and relationships
  □ Configuration: How to set up
  □ Examples: Working code snippets
  □ Deployment: How to run/deploy

Quality Verification:
  □ Code matches documentation
  □ Tests verify documented behavior
  □ Git history explains decisions
  □ No contradictions found
  □ Confidence levels assigned
  □ Edge cases identified
  □ Error handling covered
  □ Security documented

Handoff Readiness Score: ___/100
  ✓ 90+: Ready now
  ✓ 75-89: Mostly ready (minor gaps)
  ✓ 60-74: Partially ready (significant gaps)
  ✓ <60: Needs more work
```

---

## Quick Prompts for Claude Code Agent

### "Analyze architecture"
```
Analyze [REPO_PATH] architecture:
1. What patterns are used? (MVC, microservices, etc.)
2. What are the major components?
3. How do they interact?
4. What are the data flows?

Use code-patterns.md and language-patterns.md for framework.
```

### "Document this module"
```
Document src/orders/ for handoff:
1. What does this module do?
2. What are the main classes/functions?
3. What tests exist?
4. What's the business purpose?
5. How does it integrate with other modules?

Include: code references, test examples, data models.
```

### "Find security issues"
```
Check [REPO_PATH] for security issues:
1. How is authentication handled?
2. What secrets are in the code?
3. Is input validated?
4. Is sensitive data encrypted?
5. Are error messages safe?

Use security-documentation.md format.
```

### "Verify claims"
```
Verify these documentation claims against code:
1. [Claim 1]
2. [Claim 2]
3. [Claim 3]

For each: find code evidence, test evidence, git evidence.
Use evidence-patterns.md for verification.
```

---

## Productivity Tips

### Time Savers

**Use ripgrep for fast searching:**
```bash
rg "pattern" src/  # Faster than grep
rg --type py "class" src/  # Search specific file type
```

**Generate diagrams from code:**
```bash
# Use Mermaid for automatic diagram generation
echo "graph LR
    A[Module 1] --> B[Module 2]" > diagram.mmd
```

**Automate API documentation:**
```bash
# Use Swagger/OpenAPI if available
grep -r "operationId\|summary\|description" . --include="*.yaml"
```

**Quick confidence scoring:**
```
If claim appears in:
  - Code: +30 points
  - Tests: +30 points
  - Git: +20 points
  - Comments: +20 points
  Total: score out of 100
```

### Avoiding Common Mistakes

**Don't:**
- Oversimplify architecture (add edge cases)
- Skip error handling (very important)
- Ignore technical debt (document it)
- Assume knowledge (explain everything)
- Claim without evidence (verify first)

**Do:**
- Verify assumptions
- Cross-reference sources
- Document trade-offs
- Explain decisions
- Update as code changes

---

## Glossary: Quick Reference Terms

| Term | Meaning |
|------|---------|
| Handoff readiness | Score (0-100) indicating how well documented |
| Circular evidence | Using same source twice to prove something |
| Triangulation | Using 3+ sources to verify claim |
| ADR | Architecture Decision Record (why we chose this) |
| MVC | Model-View-Controller architectural pattern |
| CQRS | Separate read and write models |
| Saga | Distributed transaction across services |
| PII | Personally Identifiable Information (protect!) |
| ACID | Atomicity, Consistency, Isolation, Durability |
| Eventual consistency | Data will be consistent eventually (but not now) |
| Idempotent | Calling twice = calling once (safe to retry) |
| Serialization | Converting object to storage format |
| Mocking | Fake implementation for testing |
| Regression | Bug that was fixed but came back |
| Technical debt | Code that works but costs to maintain |

---

## Quick Decision Tree: "Should I document this?"

```
Is this something someone needs to know to modify the system?
  ├─ YES: Document it
  │   ├─ Is it obvious from reading code?
  │   │   ├─ YES: Add comment in code, brief note in docs
  │   │   └─ NO: Detailed explanation needed
  │   └─ Add to relevant section
  │
  └─ NO: Probably skip, or add as optional reference
      ├─ But if it's part of explaining a major feature: include anyway
      └─ And if it's a decision that might be revisited: document why
```

---

## Final Checklist Before Publishing

```
□ All code references are valid (files exist, lines correct)
□ All examples are tested and work
□ No secrets exposed (API keys, passwords, tokens)
□ No personal information (email addresses, real usernames)
□ All diagrams are accurate and up-to-date
□ Links are not broken
□ Grammar and spelling checked
□ Confidence levels assigned
□ Sources cited
□ Reviewed by domain expert
□ Version number incremented
□ Changelog updated
```

---

## When in Doubt

1. **Verify against code** (code is truth)
2. **Check tests** (prove behavior)
3. **Review git** (understand decisions)
4. **Ask developers** (if unclear)
5. **Document uncertainty** (rather than guessing)

Remember: **Accurate and humble documentation is better than confident and wrong.**
