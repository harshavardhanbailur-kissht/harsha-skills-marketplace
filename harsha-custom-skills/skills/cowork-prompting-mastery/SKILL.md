---
name: cowork-prompting-mastery
description: |
  Translates raw user requests into Cowork-optimized prompts. Invoke when the user wants to: convert a rough ask into a production Cowork prompt, rewrite an existing prompt, debug why a Cowork session went wrong, score a prompt's quality, choose between Chat / Cowork / Code, or set up context (identity files, folder instructions, skills). Primary job is translation — user says "I want X", skill outputs the optimized prompt that will actually produce X. Secondary jobs are review, scoring, and surface selection. Triggers: "convert this prompt", "optimize for Cowork", "rewrite for Cowork", "how do I prompt Cowork to...", "fix this prompt", "score this prompt", "Cowork vs Code", "why did Cowork fail", "prompt template", "agentic prompt".
---

# Cowork Prompting Mastery

## What this skill does

**Primary mode — Translation.** User gives a raw ask ("help me put together a Q1 report from these files"). Skill returns an optimized Cowork prompt the user can paste into a new session. No 8-question interrogation for simple cases.

**Secondary modes:** prompt review/scoring, surface selection (Chat vs Cowork vs Code), context-engineering setup, debugging failed sessions.

Outputs are always concrete: a prompt in a code block, a scored rubric, a fix list. Not a lecture.

---

## Cowork architecture — the minimum you need

Cowork is an agentic runtime. A sandboxed Linux VM runs locally; model inference runs in Anthropic's cloud. Every prompt is a delegation brief to an autonomous agent with real tools.

**Tools the prompt can assume exist** (non-exhaustive — the exact set depends on what's connected):
- **Filesystem & shell:** `read`, `write`, `edit`, `bash` in granted folders.
- **Web:** `web_search`, `web_fetch`.
- **Delegation:** sub-agents (independent context windows), `skills` (procedural knowledge), `plugins`.
- **Interaction:** `AskUserQuestion` (structured multiple-choice clarification), `TodoWrite` (visible progress tracker).
- **Connectors:** MCP servers (Gmail, Drive, Notion, Slack, Calendar, Jira, etc.) and a registry (`search_mcp_registry`, `suggest_connectors`) when a connector isn't already installed.
- **Computer use:** screen/mouse/keyboard with tiered app permissions (browsers → read-only; IDEs/terminals → click-only; everything else → full).
- **Artifacts:** `create_artifact` renders a persistent HTML page in the sidebar that can call connectors on each open — use for recurring dashboards, trackers, interactive explorers over live data.
- **Folder access:** `request_cowork_directory` prompts the user to grant a folder if one wasn't pre-selected.
- **Scheduling:** recurring / timed execution for prompts that should run without the user initiating.

**Architectural facts that shape every prompt:**
- Cowork costs materially more tokens per session than Chat — VM initialization, tool schemas, identity files, skill manifests all load before the user's prompt starts. Treat Cowork sessions as a budgeted resource.
- Each sub-agent gets its own context window. Splitting work across sub-agents is the strongest defense against context exhaustion.
- **Files persist across compaction and sessions. Conversation history does not.** If a piece of state needs to survive, it must live in a file.
- Folder access is opt-in. If the prompt references a folder that wasn't granted, Claude will pause. Use `request_cowork_directory` in the prompt or pre-select the folder.
- Computer-use has tiered permissions. Browsers = read-only from computer-use (use the Claude-in-Chrome MCP to click); IDEs/terminals = click-only (use bash for shell commands).

---

## Translation mode — the default workflow

When the user hands you a raw ask, run this loop:

```
1. CLASSIFY the ask:
   - Is it a Cowork task at all? (file paths, multi-step execution, local files, connectors → yes.
     Single factual question or brainstorm with no artifacts → no, recommend Chat.)
   - Risk tier: read-only / create-only / modify-existing / destructive.
   - Complexity: trivial, standard, ambiguous, multi-phase.

2. FILL GAPS without interrogating:
   - If file paths are implied ("my downloads folder"), assume standard paths (~/Downloads)
     and note the assumption in a one-line comment at the top of the output prompt.
   - If output location is unspecified, default to a sensible path and say so.
   - If the task clearly has unknowns that would change the whole approach
     (audience, format, scope), use AskUserQuestion — but ask at most 3 structured
     multiple-choice questions, never an open-ended interview.

3. PICK A TEMPLATE:
   Trivial/low-risk    → Template A
   Standard            → Template B
   Ambiguous/high-risk → Template C (with AskUserQuestion baked in)
   Heavy context       → Template D (XML-structured)

4. ASSEMBLE the prompt using the 5-Component Anatomy.

5. SCORE with the rubric. If any dimension < 4, revise that dimension before returning.

6. RETURN the prompt in a single code block, plus a 1-3 line note on assumptions made
   and any suggested folder access or connectors the user should enable before running.
```

Do not make the user answer 8 questions unless they explicitly ask for guided construction.

---

## The one rule: outcomes over instructions

Every validated source converges here: **describe the end state, not the steps.** Cowork plans its own approach. Prescribing implementation prevents adaptation, adds noise, burns context, and produces worse results.

```
BAD — micromanaging implementation:
"Open the PPTX template. Extract the color scheme using
 python-pptx. Create a new presentation. Apply those colors.
 Read meeting-notes.md. Add the content to slides..."

GOOD — delegating the outcome:
"Build a presentation matching the design of
 brand-template.pptx in ~/Templates/.
 Content source: meeting-notes.md in ~/Projects/q1/.
 Save as Q1-update.pptx in ~/Desktop/presentations/.
 Don't screenshot during creation."
```

### Action-first framing (with one caveat)
Lead with the action verb for plain-text prompts. Cut throat-clearing ("Can you help me...", "I was wondering if..."). **Exception:** XML-structured prompts (Template D) lead with `<context>`, not a verb — the structure carries the framing.

---

## The 5-Component Prompt Anatomy

Build every Cowork prompt from these. Match depth to complexity and risk.

**1. END STATE (required)** — What does "done" look like?
```
End state: A formatted 15-page Q1 report as .docx with
           executive summary, department breakdowns, and
           data appendix.
```

**2. INPUTS (required when files involved)** — Real paths, never "my folder."
```
Inputs: financials.xlsx and dept-updates/ in ~/Projects/q1/.
Template: quarterly-template.docx in ~/Templates/.
```

**3. CONSTRAINTS (required for any file-modifying task)** — What NOT to do.
```
Constraints:
- Don't delete or modify source files
- Don't screenshot during creation
- Don't add sections not in the template
- Keep each section under 2 pages
```

**4. QUALITY BAR (recommended for complex work)** — Testable criteria.
```
Quality bar:
- Every number must trace to a cell in financials.xlsx
- Tone: executive-level, not technical
- Zero placeholder text or TODO markers
```

**5. VERIFICATION & OUTPUT (recommended — proportional to risk)** — Plan gates and audit trails.
```
Process: Show me your plan before creating files.
Output: Save to ~/Reports/Q1/. Create actions.log.
```

**Audit-trail proportionality.** The `actions.log` / `what-changed.md` ceremony is for prompts that modify multiple files, touch destructive operations, or run unattended. For a single-file create or a trivial rename, skip it — ceremony burns tokens without reducing risk.

---

## Four Prompt Templates

### Template A — Quick Delegation (simple, low-risk)
```
[ACTION VERB] [deliverable] from [inputs at explicit path].
Save to [output path]. Don't [key constraint].
```

### Template B — Outcome-First Brief (standard complexity)
```
End state: [concrete deliverable description]
Inputs: [file paths and data sources]
Constraints:
- [negative constraint]
- [scope constraint]
- [format constraint]
Output: Save to [path].
Show me the plan before executing. Create actions.log if >3 files touched.
```

### Template C — Guided Clarification (ambiguous or high-stakes)
```
Goal: [TASK] so that [SUCCESS CRITERIA].
Inputs: [folder/files to read first].

Before executing, use AskUserQuestion to resolve:
  - [specific ambiguity 1]
  - [specific ambiguity 2]
  - [specific ambiguity 3]
Ask at most 3 structured multiple-choice questions — do not free-form interrogate.

Surface assumptions as questions, not as pre-filled defaults.
```

### Template D — XML-Structured Brief (complex, multi-context)
```xml
<context>
I'm [role] preparing [deliverable] for [audience].
The source materials are in [path].
</context>

<task>
Create [deliverable] that [specific requirements].
</task>

<constraints>
- Don't [negative constraint]
- Format: [specification]
- Length: [limit]
- Tone: [description]
</constraints>

<quality_bar>
- [testable criterion 1]
- [testable criterion 2]
</quality_bar>

<output>
Save to [path]. Show plan first. Create actions.log.
</output>
```

**Selection guide:** A for file moves, conversions, simple generation. B for document creation, data processing, multi-file workflows. C for ambiguous work or when you're unsure what "good" looks like. D for prompts with heavy context, multiple concerns, or when Claude needs to parse a complex brief reliably.

---

## When to recommend an Artifact instead of a file

Artifacts (`create_artifact`) render a live HTML page in the sidebar. They persist across sessions and can call MCP connectors on each open for fresh data.

**Recommend an artifact when:** the user will want to look at this again and the underlying data changes over time. Status trackers, weekly digests over connector data, interactive explorers, recurring reports.

**Do not recommend an artifact when:** the output is a one-off static visualization, the user wants a file to email/share, or there's no connector data to refresh.

If you're translating a raw ask and the phrasing contains "page I can check", "dashboard", "tracker", "each morning", "keep an eye on" — strongly consider recommending an artifact output instead of a .docx / .md file, and say so in the assumptions note.

---

## XML tags — when they matter here

In Chat, XML tags are organizational convenience. In Cowork, they become structural when the prompt is long enough that sections need clean boundaries.

**Use XML tags when:**
- Separating instructions from quoted context or examples (prevents context-as-instruction confusion)
- Defining phase boundaries in multi-step prompts (prevents phase collapse)
- Embedding reference content inline (clear delimiter between your words and quoted material)
- Providing examples with expected reasoning (include `<thinking>` to shape planning)

**Don't use XML tags when:**
- Prompt fits Template A or B (overhead without benefit)
- You're writing a mobile/Dispatch prompt (keep it short)

---

## Prompt Quality Scoring Rubric

Score any Cowork prompt 1–10 on each dimension.

```
DIMENSION                    1 (worst)              10 (best)
─────────────────────────────────────────────────────────────
1. OUTCOME CLARITY           Vague verb, no         Concrete deliverable,
                             deliverable described  format, location named

2. INPUT SPECIFICITY         "My files", "the doc"  ~/explicit/path/file.ext
                                                    for every input

3. CONSTRAINT COVERAGE       Zero negative          Constraints matched to
                             constraints            risk (deletion, scope, format)

4. RISK-APPROPRIATE GATES    No plan gate for       Approval gates matched
                             destructive operations to reversibility

5. CONTEXT EFFICIENCY        Entire prompt is       Lean prompt pointing at
                             inline prose           files, no ceremony inflation
```

### Pass criteria (both must hold)

1. **Total ≥ 40.**
2. **Per-dimension floor:** no dimension scores below 4. (A total of 40 with one dimension at 1 is not production-ready — that single failing dimension can destroy the output.)

```
TOTAL 40-50 AND floor met: Ship it.
TOTAL 35-39 OR one dim at 4-5: Acceptable for low-risk tasks only.
TOTAL < 35 OR any dim < 4:     Revise before running.
TOTAL < 25:                    Rewrite from scratch using the templates.
```

Special case: a prompt with **Risk-Appropriate Gates < 6** for a destructive or irreversible operation is a hard fail regardless of total.

---

## The 9 Prompt Review Failure Modes

When reviewing a prompt or debugging a bad session:

```
1. VAGUE VERB — "Clean up", "organize", "fix" without specifics.
   Risk: destructive file operations interpreted broadly.
   Fix: replace with exact actions + "don't delete anything."

2. PHANTOM INPUTS — "My folder", "the document", "that spreadsheet."
   Risk: wrong files processed, Claude guesses paths.
   Fix: ~/explicit/paths/to/file.ext for every input.

3. MISSING GUARDRAILS — No negative constraints at all.
   Risk: screenshots burning context, unrequested additions, scope creep.
   Fix: add ≥1 "don't" per file-modifying operation.

4. IMPLEMENTATION LEAKAGE — Step-by-step instructions instead of outcome.
   Risk: prevents better approaches, wastes context tokens.
   Fix: describe end state. Remove all how-to steps.

5. PHASE COLLAPSE — All instructions for complex work given at once.
   Risk: Claude tries everything simultaneously, quality degrades.
   Fix: phased execution with checkpoints (references/chain-and-state.md).

6. NO APPROVAL GATE — File-modifying task with no "show plan first."
   Risk: irreversible changes before you review.
   Fix: "Propose your approach before making any changes."

7. CONTEXT GLUTTONY — Too many folders, too much inline content.
   Risk: re-reading loops, token burn, compaction.
   Fix: scope folder access, tell Claude which dirs to ignore.

8. CHATBOT FRAMING — Conversational prompt with no file references.
   Risk: paying Cowork overhead for Chat-level capability.
   Fix: if no files involved → recommend Chat.

9. MISSING AUDIT TRAIL — Multi-file or destructive task with no change log.
   Risk: no way to review, verify, or recover from mistakes.
   Fix: "Create what-changed.md listing every action taken." (Skip for trivial tasks.)
```

---

## 10 Foundational Laws

1. **Name inputs and outputs with real paths.** Point at files, don't paste content.

2. **Specify what NOT to do.** Without negative constraints, Cowork improvises deletion, formatting, scope, and screenshots — often badly.

3. **Match supervision to reversibility.** Read-only → trust. Create-only → review. Modify → plan-first. Delete → step-by-step + backup.

4. **Batch related work.** One session with 3 related tasks beats 3 separate sessions. Each session reloads global instructions, identity files, skills.

5. **Use the filesystem as memory.** Files survive compaction. Conversations don't. Write progress, decisions, and state to `.cowork-state/` or an equivalent directory.

6. **Keep identity files lean.** Beyond a few thousand words of ABOUT ME / global instructions, Cowork summarizes loosely instead of reading carefully. Treat this as a budget.

7. **Ask for a change log when the blast radius warrants it.** For multi-file or destructive operations, end the prompt with "create what-changed.md." Skip for trivial single-file tasks.

8. **Front-load critical constraints.** Rules at the top of the prompt survive compaction longer than rules at the bottom. Put safety-critical instructions first.

9. **Lead with the action verb — except in XML-structured prompts.** For plain prose prompts, cut throat-clearing and start with "Create", "Analyze", "Move", "Generate." For Template D, lead with `<context>` and let the structure carry the framing.

10. **Design for restart.** Before any complex workflow, ask: "If Claude forgot this entire conversation but could read all files, could it continue?" If no → add filesystem state.

---

## Translation Examples (raw ask → optimized prompt)

### Example 1: Trivial file conversion (Template A)

**Raw ask:** *"convert these images in downloads to pdf"*

**Optimized:**
```
Convert every .png, .jpg, and .jpeg in ~/Downloads/ to a single combined PDF.
Save to ~/Downloads/images.pdf. Don't delete the source images.
```

*Assumptions: all images in ~/Downloads go into one PDF; originals preserved.*

---

### Example 2: Standard document creation (Template B)

**Raw ask:** *"help me put together a Q1 report from my sales data"*

**Optimized:**
```
End state: A Q1 sales report as .docx with executive summary,
regional breakdown, product-line breakdown, and a one-page
risks/recommendations section.

Inputs: sales-q1/ folder in ~/Data/ (contains monthly CSVs).
Template (if present): quarterly-template.docx in ~/Templates/.

Constraints:
- Don't modify source CSVs
- Don't screenshot during creation
- Keep total under 12 pages
- Every number must trace to a cell in the source CSVs

Output: Save to ~/Reports/Q1-2026/q1-sales.docx.
Show the structure outline before writing. Create actions.log.
```

*Assumptions: monthly CSVs in ~/Data/sales-q1/; no explicit template — skip if absent. Grant Claude access to ~/Data, ~/Templates, and ~/Reports before running.*

---

### Example 3: Ambiguous high-stakes reorganization (Template C)

**Raw ask:** *"clean up my projects folder, it's a mess"*

**Optimized:**
```
Goal: Reorganize ~/Projects/ into a cleaner structure without losing any files.
Inputs: all contents of ~/Projects/ (read-only during planning).

Before executing, use AskUserQuestion to resolve:
- Organization axis (by client / by year / by project type / by status)
- What to do with files older than 2 years (archive / keep inline / delete)
- Whether to preserve existing subfolder names or rename to a convention

Ask at most 3 structured multiple-choice questions.

Then: show me the complete move plan — every file, current path, new path —
as a table before executing anything. Wait for explicit approval.
Don't delete anything — moves only. Create what-changed.md with full move log.
```

*Assumptions: user wants reorganization, not deletion. Plan-first gate is mandatory because the operation is bulk and reversible only with the move log.*

---

### Example 4: Recurring tracker (recommend Artifact)

**Raw ask:** *"give me a page I can check each morning for my open Jira tickets"*

**Optimized (with artifact recommendation):**
```
Create an artifact (create_artifact) titled "My Open Jira Tickets" that:
- Calls searchJiraIssuesUsingJql with assignee = currentUser() AND status != Done
- Renders as a table with: Key, Summary, Status, Priority, Updated
- Groups by project, sorts by Priority then Updated
- Refetches on every open (do not cache data)
- Includes a "last refreshed" timestamp
- Shows an empty-state message if zero tickets

Before writing the artifact, call searchJiraIssuesUsingJql once with a sample JQL
to inspect the actual response shape — build the parser against observed data,
not assumed shape.
```

*Assumptions: user has the Atlassian connector authenticated. Output is an artifact, not a file, because the point is a live page the user re-opens.*

---

### Example 5: Heavy-context technical brief (Template D)

**Raw ask:** *"write a security audit of the auth flow in my repo"*

**Optimized:**
```xml
<context>
I'm a solo developer auditing the authentication flow of a Next.js + Supabase app.
The repo is in ~/code/myapp/. The auth code lives under src/app/(auth)/ and
src/lib/auth/. The app is pre-production — findings should be prioritized by
severity, not by blast radius.
</context>

<task>
Produce a security audit of the authentication flow covering:
- Session handling (cookies, JWT, refresh)
- Password and OAuth flows
- CSRF, CORS, rate limiting
- Secrets handling (.env, edge-runtime exposure)
- Authorization checks on protected routes

Output a report grouped by severity (Critical / High / Medium / Low), each finding
with: location (file:line), evidence quote, impact, recommended fix.
</task>

<constraints>
- Don't modify any source code — read-only audit
- Don't run the app or execute any scripts
- Don't include generic OWASP boilerplate — every finding must cite this repo
- Skip findings I cannot act on without refactoring the framework
</constraints>

<quality_bar>
- Every finding must quote the actual line from the repo
- Severity must be justified by exploitability, not theoretical risk
- No false positives — if uncertain, mark as "needs verification" and explain why
</quality_bar>

<output>
Save to ~/code/myapp/docs/security-audit-2026-04.md.
Show me the list of files you plan to inspect before reading them in full.
</output>
```

*Assumptions: read-only audit, no code changes. Grant Claude access to ~/code/myapp before running.*

---

## Prompt Builder Workflow — for guided construction

Use this only when the user explicitly asks for step-by-step help, not as the default path.

```
STEP 1 — IDENTIFY THE SURFACE
  Is this actually a Cowork task? Or is it better suited to Chat/Code?
  Rule of thumb: no file paths and no multi-step execution → Chat.
  Code repo + git + tests → Code. Everything else → Cowork.

STEP 2 — NAME THE END STATE
  Push for specifics: file format, page/slide count, location, audience.
  If the output should be re-openable and data changes over time → artifact, not file.

STEP 3 — MAP THE INPUTS
  Convert vague references to explicit paths.
  Verify files exist in granted folders. If folders aren't granted,
  add "use request_cowork_directory to prompt for access to X" to the prompt.

STEP 4 — DETERMINE RISK → SET GATES
  Read-only (analysis, research): no gate needed.
  Create-only (new files, no modification): lightweight gate.
  Modify-existing (edit files in place): plan-first gate required.
  Destructive (delete, reorganize, bulk rename): step-by-step approval + backup.

STEP 5 — ADD CONSTRAINTS
  Always at least one "don't" constraint for file-modifying work.
  Check for: screenshot risk, scope creep risk, deletion risk.

STEP 6 — SET QUALITY BAR
  Simple tasks: skip.
  Important deliverables: 2-3 testable criteria.
  High-stakes: add a self-review checklist.

STEP 7 — CHOOSE TEMPLATE
  Match to A/B/C/D based on complexity. Assemble. Score with rubric.

STEP 8 — TOKEN HYGIENE CHECK
  Prompt unreasonably long? Move inline content to a file and point at it.
  Critical constraints buried? Front-load them.
```

---

## Reference files — when to load

| Reference | Load When |
|-----------|-----------|
| `references/prompt-patterns-library.md` | User needs a scenario-specific prompt (documents, data, research, meetings, scheduling, etc.) |
| `references/surface-mastery.md` | Cowork vs Code vs Chat comparison, choosing surfaces, migration, token economics |
| `references/chain-and-state.md` | Multi-step execution, compaction defense, filesystem state, handoffs, approval gates |
| `references/context-engineering.md` | Identity files, folder structure, global instructions, skills, projects, token budgeting |
| `references/advanced-orchestration.md` | Parallel research, self-correction, sub-agents, scheduling, dispatch, Computer Use |
| `references/failure-modes.md` | Debugging bad sessions, risk calibration, token waste, anti-patterns, correction toolkit |
