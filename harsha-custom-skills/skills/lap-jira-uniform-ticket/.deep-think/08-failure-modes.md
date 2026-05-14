# 08 — Failure Modes

10 ways this skill can fail in production. Each entry: what it looks like, how to detect it, how to handle it gracefully without breaking the locked principles (no fast path, quality over speed, cross-PM uniformity).

The 3 highest-risk failures are F1, F4, and F8 — flagged at the top of the report.

---

## F1 — PM rage-quits the questioning

**What it looks like.** PM has answered 30 questions, the skill is on its 31st, and the PM types "just write it" / "skip the rest" / "I don't have time for this" / "/lap-ticket abort". A critical Phase-4 gate hasn't passed yet. This is the highest-volume risk in production and the locked "no fast path" principle creates a real tension.

**Detection.** Three signals:
- Explicit verbal abort signal in the PM's message (regex: "skip", "abort", "just write it", "enough", "stop asking", "I'll fill it later").
- Three consecutive 1-3 word answers to narrative questions.
- 60+ minutes of session wall-clock with no answer in the last 10 minutes.

**Handling.**
- Skill acknowledges the PM's signal in one sentence: "I hear you. The 'no fast path' rule means I can't skip the gates entirely, but I can ship a partial."
- Skill writes the partial draft using only the answered categories. Every unanswered MUST slot is rendered as `[BLOCKED — needs PM input: <category code>]`.
- Skill marks the ticket `[DRAFT — INCOMPLETE]` in the title and adds a footer: `Skipped questions: <list with category codes>`. The downstream release-notes skill detects these markers and refuses to consume.
- Skill asks the PM whether to (a) push the partial to Jira so the PM can finish it later in the Jira UI, or (b) save the partial to `.lap-ticket-session/` for a later resume, or (c) discard.

**Why this preserves the locked principle.** The skill never silently produces a complete-looking ticket from incomplete input. Either the gaps are visible (BLOCKED markers) or the work is held for resumption.

---

## F2 — PM gives a 3-word answer to a complex question

**What it looks like.** Skill asks E1 (the proposed change) for a WC ticket. PM answers "add new approval stage."

**Detection.** Answer length < 15 words for any narrative question (E, B1, K2, J1) where the spine slot needs ≥1 paragraph or numbered list.

**Handling.**
- Skill does NOT shame, scold, or call out laziness. It re-asks with structure:

> "Got it — `add new approval stage`. To draft the WC spine I need a bit more. Walk me through three things in turn (one at a time):
> a) The trigger condition for the new stage (e.g., loan amount > 7L, region = MH, source = ETB).
> b) The owner role for the new stage (BCM / CCM / NCM / SCH / NCM-IPA).
> c) The exit conditions / SLA / what happens at SLA breach.
> Start with (a)."

- Per the file 03 cap, max 5 follow-ups per category. After 5 follow-ups still producing thin answers, the skill writes "best-effort answer captured; will validate at Phase 7" and moves on. Phase 7 then likely catches the gap and surgically re-enters the category.

---

## F3 — PM uploads a Loom and expects the skill to extract everything

**What it looks like.** PM types "see Loom: <url>" and stops. No textual answers.

**Detection.** First Phase-4 turn after Loom upload contains nothing but the URL.

**Handling.**
- If the host environment has video/transcript extraction (e.g., a `lap-screen-analyzer` skill, or Granola transcript MCP), the skill calls it: "Pulling Loom transcript..."
- The skill then summarises what it heard and asks the PM to confirm: "From the Loom I extracted: [bullet list]. Is this what you want in the ticket? I'll then ask follow-ups to fill the spine."
- If no extraction tool is available, the skill banner-warns: "I can't process video directly in this environment. Please paste the key beats as text — I'll then ask follow-ups to fill the spine."
- The Loom URL is preserved in the Sources footer regardless.

**Why this matters.** Looms are increasingly the PM's lingua franca; rejecting them outright pushes PMs back to free-form Jira. But the skill doesn't pretend to extract what it can't.

---

## F4 — Auto-search returns 50 related tickets, all noise

**What it looks like.** Phase 1 JQL on a generic intent ("change the dropdown values") returns the cap of 10 tickets, none of which are actually related. Phase 2 verify is then a 10-question slog of "no, no, no, no..."

**Detection.** PM tags ≥7 of the first 8 candidates as `unrelated`.

**Handling.**
- After 7 `unrelated` tags, skill stops asking and announces: "These auto-search results are noise. Re-running with tighter keywords."
- Skill asks the PM: "What's the most distinctive 2-3 word phrase from your intent that's unlikely to appear in unrelated LAP tickets? I'll re-run the search."
- Re-runs JQL/CQL with the PM-supplied phrase. New candidate set replaces the old.
- If second pass also fails (≥4 unrelated of first 5), skill banner-accepts "auto-search produced no useful results" and moves to Phase 3 with `RELATED.md = (empty)`. The PM is not punished for the skill's poor recall.

**Why this matters.** Forcing the PM through a long Phase 2 of useless tagging is the fastest way to PM rage-quit (F1). Bounding the noise pass is a prerequisite for the auto-search-first principle being workable.

---

## F5 — Glossary is empty / first-time install

**What it looks like.** PM installed `lap-jira-uniform-ticket` before `kissht-field-release-notes`, or the glossary files are unreadable, or the marketplace install is incomplete.

**Detection.** Phase 1 step 4 fails to read `lap-glossary.md` / `lap-stages.md` / `lap-roles.md`.

**Handling.** (Per file 05.)
- Skill banner-warns: "I can't load the LAP glossary. Falling back to local-only mode — every term will be treated as new and asked about. This is going to be slow."
- Hardcoded minimal seed: BCM, CCM, NCM, Credit PD, Final Sanction Pending.
- All new terms go to `LOCAL_GLOSSARY.md`.
- Post-delivery, the skill writes `GLOSSARY_BOOTSTRAP.md` and prompts the PM to install `kissht-field-release-notes` and merge.

---

## F6 — PM is writing a ticket type the skill has no template for

**What it looks like.** PM is filing a Spike, an Initiative, a Container Epic, a Tech Debt cleanup, or a Bug — issue types the skill's 5 spines (WC/BO/SC/RD/MX) don't cover. Or a Story/Epic that genuinely doesn't match any signal.

**Detection.**
- At Phase 0, if PM picks Bug → immediate hand-off (F-Bug below).
- At Phase 3, if no signal scores ≥3 after the Phase-2 expansion loop → fallback to SC type with banner.
- At Phase 0, if PM types issue type other than Story / Epic / Task / Bug → hand-off to a generic template.

**Handling.**
- **Bug:** Skill responds "Bugs use the LAP bug template, not this skill. Hand-off message: <link to bug template>." Session ends.
- **Spike / Initiative:** Skill loads `templates/spine-fallback.md` (universal structure: Intent → Description → Logic → QA → BA → AC → Sources). Banner: "This is a [Spike], which doesn't fit the 5 standard types. Using fallback spine."
- **No signal at all:** Per file 02, defaults to SC with banner.

The fallback exists so the skill never refuses to produce a ticket. Refusal pushes the PM back to free-form Jira — the failure we're trying to prevent.

---

## F7 — Compaction loses session state

**What it looks like.** PM came back the next day after a context compaction (or the conversation was archived and resumed); the skill has no memory of the in-progress session.

**Detection.** PM types "let's continue" / "where were we" / "/lap-ticket resume" with no in-conversation context.

**Handling.**
- Skill checks `.lap-ticket-session/` for active sessions. If found, lists them: "I see in-progress sessions: <list with last-modified>. Resume which?"
- On resume, loads SESSION_STATE.md to determine current phase + next action, loads INTENT.md / RELATED.md / TYPE.md / ANSWERS.md, and continues from where it left off.
- If multiple sessions and the PM picks one, the others stay parked (no auto-cleanup; PM may genuinely have multiple drafts).

This is the deep-thinker memory-loss defence applied to a conversation skill.

---

## F8 — Two PMs filing overlapping tickets simultaneously

**What it looks like.** Paras filed LAP-2367 yesterday on PAN re-verification; today Mohini independently asks the skill to file a ticket on PAN re-verification. Without detection, two slightly-different tickets ship and the team has to reconcile.

**Detection.** At Phase 1 auto-search, if the candidate list contains a ticket whose title canonicalises to within 60% similarity of the new intent statement AND was created within the last 14 days AND has status In Progress / To Do (i.e., not closed), the skill flags collision.

**Handling.**
- Skill announces: "I see LAP-2367 (Paras Arora, 2 days old, In Progress) covers similar scope. Three options:
> a) This IS the same work — continue on LAP-2367 (I'll redirect this session there).
> b) This is a sibling — I'll link as `relates to: LAP-2367` and continue.
> c) These are unrelated — proceed independently. I'll skip this collision check."
- PM picks; selection logged in `COLLISION.md`.
- Option (a) re-routes to enrichment-of-existing flow (Phase 0 detected the existing key).
- Option (b) ensures the new ticket has the link in the Related section.
- Option (c) lets the work proceed with explicit acknowledgment.

This is the cross-PM uniformity discipline at the workflow layer, not just the rendering layer.

---

## F9 — Jira API failure mid-Phase-8

**What it looks like.** PM picked push-to-Jira destination. Phase 8 calls `editJiraIssue` and gets a 5xx, a network timeout, or an ADF validation error.

**Detection.** API call returns non-2xx, or the round-trip diff (Phase 8 step 4) shows the body wasn't accepted.

**Handling.**
- On 5xx / timeout: retry with exponential backoff up to 3 times. If still failing, fall back to writing `DRAFT.md` to a markdown file at the user-specified path AND keeping the reserved Jira key with the stub body. PM is told: "Jira push failed after 3 retries. I've saved the markdown to <path>. Open LAP-<key> in Jira and paste manually, or rerun /lap-ticket deliver to retry."
- On ADF validation error: skill compares the offending markdown (typically a complex table or nested list) against ADF spec, simplifies the offender (table → bulleted list, nested list flattened), and retries. If still failing, falls back to markdown-file mode.
- The reserved Jira key is never lost. PM can always paste manually.

---

## F10 — PM contradicts themselves and refuses to resolve

**What it looks like.** PM said in B1 "BCM clicks Mark as Complete and the case moves to Final Sanction Pending"; in E1 they said "after Mark as Complete the case stays in Credit PD." Skill flags. PM says "both are right, just write the ticket."

**Detection.** A contradiction logged to CONTRADICTIONS.md. PM's resolution attempt is itself ambiguous (says "both right" / "skip" / non-resolving).

**Handling.**
- Skill does not silently proceed with one version. It writes both versions into the relevant slot prefixed with `[CONTRADICTION — PM unresolved]:` and adds a footer note: `BA: please resolve the contradiction in <slot> before sprint planning.`
- The downstream release-notes skill detects the contradiction marker and refuses to consume until BA resolves.
- This is the "make the gap visible" pattern from F1.

**Why not force resolution.** Forcing resolution risks the PM picking arbitrarily to escape the question; surfacing the contradiction to BA is more honest.

---

## F-Bug — PM picked Bug at Phase 0

**Detection.** Issue type = Bug at Phase 0.

**Handling.** Skill responds:

> "This skill is for Story / Epic / Task — it produces tickets that the release-notes skill consumes. Bugs use the LAP bug template (different shape, different consumers): <link to bug template>. If this should be a Story (e.g., a defect that's actually a missing feature), restart with Story."

Session ends at Phase 0. No partial state left around.

---

## Summary table

| # | Failure | Detection | Severity | Handling pattern |
|---|---|---|---|---|
| F1 | PM rage-quits | Verbal signal / 3 short answers / 60min idle | High | Partial draft with BLOCKED markers; ship or hold |
| F2 | 3-word answer to complex Q | Length < 15 words on narrative | Medium | Re-ask with structured sub-prompts; cap at 5 follow-ups |
| F3 | Loom dump, no text | First turn is just URL | Medium | Try transcript extraction; else ask for text beats |
| F4 | Auto-search noise | ≥7 unrelated of first 8 | High | Re-run with PM-supplied phrase; bound at 2 attempts |
| F5 | Empty glossary | Glossary load fails Phase 1 | Medium | Bootstrap mode with 5-term seed; export GLOSSARY_BOOTSTRAP |
| F6 | No template / Bug / Spike | Issue type or no signal | Medium | Hand-off (Bug) / fallback spine (everything else) |
| F7 | Compaction loses state | "let's continue" with no context | Medium | Resume from .lap-ticket-session/ |
| F8 | Two PMs overlap | Title 60% similar + recent + open | High | Three-option chooser (continue / sibling / independent) |
| F9 | Jira API fails | Non-2xx or round-trip diff fails | Medium | Retry / simplify / fall back to markdown |
| F10 | PM unresolved contradiction | CONTRADICTIONS.md + non-resolving answer | Medium | Both versions rendered with [CONTRADICTION] marker |
