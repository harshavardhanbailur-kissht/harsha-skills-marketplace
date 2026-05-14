# PRINCIPLES — `lap-jira-uniform-ticket`

The canon. Read this once at onboarding, then refer back when in doubt.

This skill builds Jira tickets for the Kissht LAP team. Every PM uses it. Every ticket comes out the same shape. The next skill in line — `kissht-field-release-notes` — reads those tickets and writes the field release note. If a ticket is shaped wrong, the release note breaks. That is why uniformity matters.

For the spine, see `PATTERN.md`. For voice rules, see `voice-and-style.md`.

---

## Why this skill exists

Three problems, one skill.

1. **Cross-PM inconsistency.** LAP has a dozen PMs filing tickets. Every PM has a slightly different shape. Some put AC at the top. Some skip QA scope. Some use Connextra; some don't. The downstream BCM, CCM, NCM, and BCPA cannot read four shapes in one morning.
2. **Release-note breakage.** `kissht-field-release-notes` extracts named stages, owners, system strings, branch outcomes, and contacts. If those are missing or buried in pseudocode, the release note ships incomplete or wrong.
3. **Onboarding cost.** A new PM joining LAP currently learns the ticket shape by reading 40 old tickets and copying the senior PM's voice. This skill is the shortcut: ask the questions, fill the spine, ship the ticket.

The goal is not to make tickets faster. The goal is to make every PM's ticket look like the same PM wrote it.

---

## 8 content principles

Every LAP ticket carries these eight things. If one is missing, the ticket is not done.

| # | Principle | What it means |
|---|---|---|
| 1 | **Release-note line at the top** | One operator-readable sentence the BCM can read at 9am. Lifts verbatim into the release note. |
| 2 | **Plain-English intent paragraph** | What this ticket does and why. No bullets. No jargon. Readable cold by a PM who joined yesterday. |
| 3 | **Current flow, only when something is changing** | Numbered steps. Names the workaround we are killing. Skip when the ticket is greenfield (no current flow exists). |
| 4 | **Proposed solution with consequences** | Numbered. Every rule names what the system does in response. No rule is allowed to dangle. |
| 5 | **System strings, verbatim, single-quoted** | Every panel label, dropdown value, status name, button, error message, SMS body. If the ticket changes user-facing copy, paste the exact string. |
| 6 | **QA scope** | Numbered scenarios the QA team will actually run. Names the back-to-back toggles, the refresh cases, the cross-stage checks. |
| 7 | **Open Considerations for BA** | Each unresolved assumption gets a name, a proposal, and an impact-of-being-wrong. Always carries an `Out of scope` line. |
| 8 | **Acceptance Criteria, lean** | 3 to 5 bullets, organised by area, observable in UAT. Never a re-listing of the proposed solution. |

The 8 principles map onto the spine in `PATTERN.md`. Each principle owns a section. No principle leaks into a section it does not own.

---

## 4 anti-principles

Things this skill refuses to do, and trains the PM to refuse.

| # | Anti-principle | Why we refuse |
|---|---|---|
| 1 | **No pseudocode** | No code blocks over five lines. No JSON schemas. No SQL. No function signatures. The audience is a BCM at 9am, not an engineer at a code review. Inline `'system_string'` quoting and matrix tables are the only allowed structured forms. |
| 2 | **No repetition** | Each section has one job. If the Intent paragraph and Proposed Solution step 1 say the same thing, one of them is wrong. The dedup pass (Phase 6) collapses restatement. |
| 3 | **No bloated AC** | AC is 3 to 5 bullets. Not 15. Not Given-When-Then. The body says how it works; AC just lists the done gates. If you cannot fit AC into 5 bullets, the body is doing AC's job and AC is doing the body's. |
| 4 | **No assumed context** | If a term is not in the glossary, it gets defined at first use OR it triggers a question. Ghost terms BLOCK the draft. The skill will not let you ship a ticket with `'XYZ stage'` undefined. |

---

## 5 skill-behavior principles

How the skill behaves when you run it.

1. **Socratic.** The skill asks questions one at a time. It does not draft until you have answered the questions for your ticket type. The locked design budget is 50 to 100 questions in extreme cases. Most tickets land in 20 to 40.
2. **Auto-search first.** Before asking you about related tickets, the skill searches the LAP Jira project (JQL) and LAP Confluence space (CQL). It surfaces what it found. You tag each result as parent / sibling / superseded / unrelated. This is not optional. The skill fails graceful when the search returns empty or fails.
3. **Asks 50 to 100 questions if needed.** No fast path. No express type. Same flow for a 5-line dropdown change as for a multi-stakeholder workflow rebuild. Pace control is by ticket type, not by PM impatience. If you want a 5-question shortcut, this skill is not for you — and the team uniformity goal is why.
4. **Never assumes.** When the skill is uncertain, it asks. When it has options, it presents them and asks you to pick. When you say something that contradicts an earlier answer, it surfaces the contradiction and asks you to reconcile.
5. **Only drafts when you confirm.** The intent paragraph gets drafted from your answers and shown to you for sign-off before the body. The body gets drafted from your answers and shown to you for sign-off before delivery. Nothing ships without your "yes".

---

## 5 team-usage implications

Things that follow from the four points above and that affect the team.

1. **Skill voice = team voice.** Whatever this skill writes will be read by the entire downstream chain. The skill writes in Plain LAP English. If a PM overrides the voice, the override is the new team voice. The skill's voice rules in `voice-and-style.md` are not stylistic preferences — they are operator-grade constraints.
2. **Exemplars are canon.** The 6 LAP exemplars (table below) are the voice reference. When in doubt, read the closest exemplar to your ticket type. The skill quotes them directly when training new PMs.
3. **Skill teaches as it asks.** Each Socratic question is also a training prompt. After three or four ticket-writing sessions, a new PM has internalised the question structure and can write the spine cold. That is the explicit handoff path. The skill is not a permanent crutch.
4. **Versioning matters.** The skill is versioned alongside `kissht-field-release-notes`. When the release-notes skill changes its parser, the ticket spine in `PATTERN.md` changes in lockstep. Do not edit `PATTERN.md` without checking the release-notes side.
5. **Glossary is shared.** The glossary lives in `kissht-field-release-notes/references/lap-glossary.md`. This skill reads from it and adds to it. New terms surfaced during a session land in `LOCAL_GLOSSARY.md` for periodic promotion. One source of truth across both skills.

---

## The 6 LAP exemplars

Every PM should read at least the four marked **canonical**.

| Key | Type | Why it is canonical | Link |
|---|---|---|---|
| LAP-2039 | SC (gold) | Workaround removal, bidirectional toggle, exemplary BA Open Considerations format with named assumption + proposal + impact | https://kissht.atlassian.net/browse/LAP-2039 |
| LAP-2242 | RD | 10-rule Logic section with zero repetition; clean Approval Matrix; Role Definitions footer; QA Testing Notes that name the simulation method | https://kissht.atlassian.net/browse/LAP-2242 |
| LAP-2052 | RD | Per-system breakdown (Leadgen / LOS / SARAL / BT+Topup); plain-English intent; Sheet Link footer; cross-stage touchpoint coverage | https://kissht.atlassian.net/browse/LAP-2052 |
| LAP-1812 | WC | Best-in-class header with Primary / Secondary actor + Preconditions; verbatim SMS string; AC organised by area; Lovable prototype link | https://kissht.atlassian.net/browse/LAP-1812 |
| LAP-2046 | BO | Branching outcome with named cases (See / Do / Verify / Consequence) — read for BO shape | https://kissht.atlassian.net/browse/LAP-2046 |
| LAP-2048 | WC | Workflow change with new approval stage and SLA — read for WC shape | https://kissht.atlassian.net/browse/LAP-2048 |

When a PM disagrees with the skill, the order of authority is: exemplar > `PATTERN.md` > skill behaviour. The exemplars trump everything because they are written in the voice of senior LAP PMs and have survived contact with the BCM, CCM, BA, and QA teams.

---

## 3 external borrowings (adopted)

Three atomic patterns lifted from outside the LAP canon. Each survived the locked-principles check. See `external-patterns-research.md` for the full evaluation.

| Borrow | Source | Where it lands |
|---|---|---|
| **Release-note line** at the top of every ticket | GitLab feature proposal template | Header blockquote, above the body. One operator-readable sentence the release-notes skill lifts verbatim. |
| **Out of scope** line near AC | Shape Up "No-gos" + Notion "Non-goals" | Inside `Open Considerations for BA`. Prevents regression scope-creep — names what is explicitly NOT changing. |
| **Alternatives considered** 2 to 3 sentences | Google design-doc culture | Optional paragraph inside `Open Considerations for BA`. Used when the design picks one of several plausible approaches. |

---

## 3 external rejections

Three patterns the skill explicitly forbids.

| Rejection | Source | Why rejected |
|---|---|---|
| **Given-When-Then AC** | Atlassian's recommended form | Bloats AC into a regression script. The body's numbered logic IS the truth; AC is a thin derived view. |
| **Mandatory Connextra** ("As a / I want / so that") | Atlassian user-story page | Breaks the LAP-2052 / LAP-2046 voice. Allowed (LAP-1812 uses it) but never required. |
| **PR-FAQ press-release format** | Amazon Working Backwards | Marketing prose for an internal feature ticket. Wrong audience, wrong register. We borrow the "readable cold" gate; we reject the format. |

---

## When in doubt

- Read the closest exemplar.
- Re-read this file.
- Then read `PATTERN.md`.
- Then ask in #lap-pm-tooling.

The skill answers most disagreements by quoting back at you. If the skill cannot find a rule, it asks. It never invents one.
