# Compaction Resilience

## The Problem This Solves

LLM context windows compact. Long sessions get summarized. Users return to a session hours or days
later. Without a file-based state contract, the skill loses track of where it is and has to
reconstruct from memory — which is unreliable.

Compaction resilience means: any new Claude session, given access to the `.think-session/` folder,
can recover exactly where the previous session left off, with enough fidelity to continue
seamlessly.

---

## Folder Structure

```
.think-session/
├── SESSION_STATE.md        # Written first, updated after every phase completes
├── PROBLEM.md              # Written once at session start, never overwritten
├── AXES.md                 # Written after axis identification phase
├── OPTIONS.md              # Appended as options are discovered, not replaced
├── RANKING.md              # Written after ranking phase
├── EXPERT_PANEL.md         # Written after expert panel phase
├── CROSS_QUESTIONS.md      # Appended each time a user override occurs
└── DECISION_DOC.md         # Written only at session end (synthesis phase)
```

### File Creation Order

Files are created in this order, mirroring the session phases:

1. `SESSION_STATE.md` — created immediately when session starts, before anything else
2. `PROBLEM.md` — created after problem statement is confirmed with user
3. `AXES.md` — created after axis identification is complete
4. `OPTIONS.md` — created when first option is identified; appended throughout enumeration
5. `CROSS_QUESTIONS.md` — created on first user override; appended on each subsequent override
6. `RANKING.md` — created after ranking is complete
7. `EXPERT_PANEL.md` — created after expert panel discussion is complete
8. `DECISION_DOC.md` — created only when synthesis is complete

Files that don't exist indicate phases not yet reached. This is meaningful information for recovery.

---

## SESSION_STATE.md Format

This is the single most important file. It must be self-sufficient — a recovering Claude session
should be able to understand the full state from this file alone before reading any other.

```markdown
## Session: [brief problem description, 1 line]
## Started: [date/time or session identifier]
## Current Phase: [Enumerate | Rank | Expert Panel | Synthesize | Build | Complete]

## Progress:
- [x] Problem definition
- [x] Axis identification ([N] axes identified)
- [x] Option enumeration ([N] options across [N] axes)
- [ ] Ranking
- [ ] Expert panel
- [ ] Synthesis / decision doc

## Next Action:
[One sentence describing exactly what should happen next. Be specific enough that a new session
can start executing immediately.]
Example: "Begin ranking 14 options against 4 criteria: user impact, implementation effort,
reversibility, and stakeholder risk."

## User Overrides: [N] (see CROSS_QUESTIONS.md)

## Axes Identified:
[List axis names, one per line — no need for detail here, AXES.md has full detail]

## Options Count by Axis:
[Axis name]: [N] options
[Axis name]: [N] options
...

## Notes for Recovery:
[Any context a recovering session needs that doesn't fit above. E.g., "User indicated they want
to focus on mobile-first options only." or "User is time-constrained — they said 45 minutes
maximum."]
```

Update SESSION_STATE.md at the end of every phase. Do not wait until the session ends.

---

## Recovery Protocol

When a new session opens and is given access to `.think-session/`, follow this order:

### Step 1: Read SESSION_STATE.md
This tells you:
- Where the session is in the phase sequence
- What was completed
- Exactly what to do next

Do not read any other file until you have read SESSION_STATE.md in full.

### Step 2: Read PROBLEM.md
Re-ground in the problem. Every decision in the session was made in context of this problem
statement. Do not rely on the summary in SESSION_STATE.md — read the full PROBLEM.md.

### Step 3: Read phase files in order
Read only the files that exist:

```
AXES.md → OPTIONS.md → CROSS_QUESTIONS.md → RANKING.md → EXPERT_PANEL.md
```

Skip files that don't exist — their absence means that phase wasn't reached.

### Step 4: Resume

Open the recovery with a brief sync to the user:

```
Resuming your think-with-me session on [topic].

We're at: [current phase from SESSION_STATE.md]
Completed: [brief list of what's done]
Next: [next action from SESSION_STATE.md]

Ready to continue — should I pick up where we left off?
```

Then wait for confirmation before proceeding. The user may have changed their mind about direction
since the last session.

---

## File Naming and Ordering Conventions

**All filenames are uppercase with underscores.** This is intentional — it makes the `.think-session/`
folder visually distinct from project files and easy to identify in a file listing.

**No version numbers in filenames.** There is exactly one `OPTIONS.md`, not `OPTIONS_v2.md`.
Updates to content are made via append (OPTIONS.md) or full replacement (RANKING.md after re-rank).

**Appended files vs. replaced files:**

| File | Behavior |
|------|----------|
| PROBLEM.md | Write once, never overwrite |
| SESSION_STATE.md | Replace on every phase completion |
| AXES.md | Replace if axes are revised, otherwise write once |
| OPTIONS.md | Append as options are discovered |
| CROSS_QUESTIONS.md | Append on each new user override |
| RANKING.md | Replace if re-ranked, otherwise write once |
| EXPERT_PANEL.md | Write once after panel; replace only if panel re-run |
| DECISION_DOC.md | Write once at synthesis; never append |

**OPTIONS.md append format:**
Each new option added during enumeration should include a section header indicating which axis
it belongs to, so the file remains readable as it grows:

```markdown
## [Axis Name] — Option [N]: [Option Title]
[Description]
Added: [phase/step identifier]
```

---

## Edge Cases

**Session ends mid-enumeration:** SESSION_STATE.md marks `[ ] Ranking` and below as incomplete.
RANKING.md does not exist. Recovery reads OPTIONS.md to see what was found, then continues
enumeration or moves to ranking per user's preference.

**User explicitly closed without saving:** If `.think-session/` doesn't exist, there's nothing
to recover. Start fresh.

**Conflicting state:** If SESSION_STATE.md says ranking is complete but RANKING.md doesn't exist,
trust SESSION_STATE.md's "Next Action" field. It was written last. Note the inconsistency to the
user and re-run the missing phase.

**Multiple sessions on the same problem:** Do not create separate `.think-session/` folders per
session. One folder per decision. Continuation sessions append to the same files.
