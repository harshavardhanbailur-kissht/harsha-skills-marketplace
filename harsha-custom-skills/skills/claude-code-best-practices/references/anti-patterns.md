# Anti-Patterns Catalog

12 documented anti-patterns encountered by Claude Code users, with causes, symptoms, and fixes.

---

## 1. Kitchen Sink Session

**Symptom:** Claude gives confused, contradictory, or irrelevant responses mid-session.

**Cause:** Starting with one task, switching to unrelated work, then returning to the first task — filling context with irrelevant information.

**Impact:** Wastes 40-60% of context window on noise.

**Fix:**
- Use `/clear` between unrelated tasks
- Each session should have a single, focused purpose
- If task direction changes significantly, start fresh

---

## 2. Context Amnesia (The "Dumb Zone")

**Symptom:** Claude "forgets" earlier instructions, repeats itself, or makes contradictory statements.

**Cause:** Operating near 95% context capacity where auto-compaction triggers, degrading reasoning quality. Or simply: LLMs don't have persistent memory — context outside the window disappears.

**Impact:** Quality drops dramatically; Claude becomes unreliable.

**Fix:**
- Manual `/compact` at 50% context usage (not 95%)
- Set `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50`
- Comprehensive CLAUDE.md for persistent knowledge
- Use agent memory for cross-session learning

---

## 3. Over-Correcting Failures

**Symptom:** Instructions become increasingly rigid with ALWAYS/NEVER/MUST rules. CLAUDE.md grows to 500+ lines of corrections.

**Cause:** After two failed corrections, adding more constraints instead of re-thinking the approach.

**Impact:** Context pollution; rigid rules cause new failures elsewhere.

**Fix:**
- After two failed attempts on the same issue, `/clear` and write a better initial prompt incorporating learnings
- Explain WHY instead of adding rigid constraints
- Use examples instead of rules
- Prune CLAUDE.md monthly — remove rules Claude follows naturally

---

## 4. Monolithic Skills

**Symptom:** One massive skill trying to cover everything. SKILL.md exceeds 1000 lines.

**Cause:** Not breaking domain knowledge into focused, modular skills.

**Impact:** High token consumption; Claude can't find relevant information within the skill.

**Fix:**
- Break into focused skills (one domain per skill)
- Use progressive disclosure: SKILL.md routes to reference files
- Keep SKILL.md under 500 lines; move details to `references/`
- Multiple small skills auto-trigger better than one large skill

---

## 5. Agent Sprawl

**Symptom:** Dozens of agents with overlapping responsibilities. Unclear which agent handles what.

**Cause:** Creating agents for every possible task without clear boundaries.

**Impact:** Claude can't select the right agent; invocation failures from vague descriptions.

**Fix:**
- Feature-specific agents with mutually exclusive descriptions
- 3-7 agents for most projects is sufficient
- Each agent should have a clear, non-overlapping purpose
- Use skills for knowledge, agents for delegation with different capabilities

---

## 6. Permission Fatigue

**Symptom:** Rubber-stamping every permission prompt without reading it. Or: using `--dangerously-skip-permissions` to avoid prompts entirely.

**Cause:** Too many safe operations requiring approval; no middle ground.

**Impact:** Either security risks from rubber-stamping, or complete bypass of safety checks.

**Fix:**
- Use wildcard permissions: `Bash(npm run *)`, `Edit(/src/**)`
- Enable sandbox mode for OS-level isolation
- Pre-approve known-safe operations in settings.json
- Use `acceptEdits` permission mode for trusted edit sessions

---

## 7. Vague Agent Descriptions

**Symptom:** Claude doesn't auto-delegate to the right agent, or ignores agents entirely.

**Cause:** Agent descriptions are too generic ("Helps with backend tasks").

**Impact:** Manual `/agent-name` invocation needed every time; defeats auto-delegation purpose.

**Fix:**
```yaml
# Bad
description: Helps with backend tasks

# Good
description: Use this agent PROACTIVELY when creating or modifying REST API endpoints, database queries, or authentication middleware
```

---

## 8. CLAUDE.md Bloat

**Symptom:** CLAUDE.md exceeds 300 lines. Rules contradict each other. Claude ignores half the rules.

**Cause:** Adding rules without pruning. Team members adding rules without coordination.

**Impact:** Important rules lost in noise; higher token cost every session.

**Fix:**
- Cap at 200 lines
- Split into `.claude/rules/` files with `paths:` scoping
- Use `@imports` for shared content
- Review and prune monthly
- Move domain knowledge to skills (load on-demand vs always)

---

## 9. Debugging Without Hypothesis

**Symptom:** Sending raw stack traces asking "fix this" without context or analysis.

**Cause:** Treating Claude as a magic fix-it tool rather than a reasoning partner.

**Impact:** 3x more tokens consumed; Claude explores randomly instead of systematically.

**Fix:**
- Provide hypothesis: "I think the error is because X. Can you verify?"
- Include relevant context: what changed recently, what you've tried
- Narrow the scope: specific file, function, or behavior
- Use plan mode for diagnosis before jumping to fixes

---

## 10. Legacy Project Anti-Pattern

**Symptom:** Claude makes suggestions incompatible with existing codebase conventions.

**Cause:** Launching Claude on a legacy project without an onboarding phase.

**Impact:** 45% of suggestions incompatible in legacy codebases (SFEIR study).

**Fix:**
- Create CLAUDE.md documenting conventions BEFORE starting work
- Have Claude read key files first: "Read src/auth/ and understand our authentication patterns before making changes"
- Use plan mode initially: let Claude learn the codebase
- Run `/init` to generate starter CLAUDE.md

---

## 11. Trust-Then-Verify Gap

**Symptom:** Claude produces plausible-looking code that fails on edge cases.

**Cause:** Not giving Claude a way to verify its own work.

**Impact:** Bugs discovered late; false confidence in AI-generated code.

**Fix:**
- Always give Claude a verification step: "Write the code, then write tests, then run them"
- Use TDD: describe the expected behavior, write tests first, then implement
- Run existing test suites after changes
- Different model for review (e.g., implement with Sonnet, review with Opus)
- Boris Cherny: "Giving Claude a way to verify its work creates 2-3x quality improvement"

---

## 12. Library Dismissal

**Symptom:** Claude writes from-scratch implementations instead of using established libraries.

**Cause:** AI models default to generating code rather than discovering and using existing solutions.

**Impact:** Reinventing the wheel with well-known bugs; missing community-audited security fixes.

**Fix:**
- Add to CLAUDE.md: "Prefer established libraries over custom implementations"
- Be specific: "Use bcrypt for password hashing, not custom hash functions"
- Equip Claude with Context7 MCP server for up-to-date library documentation
- Review dependencies before implementation

---

## Quick Reference: Anti-Pattern → Fix

| Anti-Pattern | One-Line Fix |
|---|---|
| Kitchen Sink Session | `/clear` between unrelated tasks |
| Context Amnesia | `/compact` at 50%, not 95% |
| Over-Correcting | Explain WHY, not add more MUST/NEVER |
| Monolithic Skills | Split into focused skills with references/ |
| Agent Sprawl | 3-7 feature-specific agents with clear boundaries |
| Permission Fatigue | Wildcard permissions + sandbox mode |
| Vague Descriptions | Use "PROACTIVELY" + specific trigger scenarios |
| CLAUDE.md Bloat | Cap at 200 lines; use .claude/rules/ for overflow |
| Debugging Blind | Provide hypothesis and narrow scope |
| Legacy Without Onboarding | Create CLAUDE.md + `/init` before work |
| Trust-Then-Verify | Always include test/verify step |
| Library Dismissal | "Prefer established libraries" in CLAUDE.md |
