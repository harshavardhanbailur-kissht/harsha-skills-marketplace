# 02 — Question Taxonomy

## Categories (in order of appearance in Phase 4)

The order is causal: each category depends on the prior categories' answers. Reordering breaks the dependency chain — for example, you cannot ask scenario questions before context questions because you don't yet know what flow the scenarios branch off.

```
A. Intent          (what + why)                    — 2-3 questions, always asked
B. Context         (current flow, what's broken)   — 2-4 questions, asked when there is a current flow
C. Scope           (which systems, which roles)    — 2-3 questions, always asked
D. Vocabulary      (stage / role / system strings) — 1-3 questions, always asked
E. Scenario        (every if-branch, every edge)   — N questions, N = number of branches; type-driven
F. Matrix          (cross-product dimensions)      — asked once, only if Phase 3 detected RD or BO with ≥2 dimensions
G. Auto-comm       (SMS/email/notification copy)   — asked once, only if PM mentioned an auto-action
H. Silent-action   (system does X invisibly)       — asked once, only if PM mentioned an auto-population or callback
I. Non-overridable (system decides, no override)   — asked once, only if PM mentioned an irrevocable rule
J. QA Scope        (what to verify)                — 3-5 questions, always asked
K. BA Scope        (assumptions to confirm)        — 2-4 questions, always asked
L. Acceptance      (the 3-bullet test)             — 1-2 questions, always asked
M. Sources         (links, sheets, attachments)    — 1 question, always asked
N. Contacts        (humans for the contact block)  — 1 question, always asked
```

### Stop-condition principle

Every category has either a **count cap** (no more than N questions) or a **type-driven count** (one question per detected branch, role, system, etc., up to a hard cap). The skill never asks an open-ended "anything else?" without a structured re-prompt — that produces conversation drift.

## Per-category question specifications

### A. Intent (always asked — cap: 3)

The Intent paragraph in the final ticket is what becomes the release-notes "Why it changed" beat. Without it, the release note opens with mechanical detail and no business framing.

| # | Question | Stop condition |
|---|---|---|
| A1 | "In one sentence, what behaviour are we changing?" | Single sentence, present-tense verb. If the PM gives a paragraph, ask "what's the one-sentence version?" |
| A2 | "Why now? What broke or what's the business trigger?" | One sentence naming the problem (a complaint, a regulatory ask, a metric, a manual workaround). |
| A3 (conditional) | "Who feels the pain today?" | Asked only if A2 didn't already name a role. Stops when ≥1 role is named. |

**Skip rule**: if the PM's opening message already contains a clear what+why, the skill confirms it back ("So the intent is: ___. Correct?") and skips A1+A2.

### B. Context — current flow (asked when type ∈ {WC, MX, BO, SF}; skipped for pure RD when there is no flow to replace — cap: 4)

The Current state block is the operator's anchor. Without it, the release-note "Old flow / New flow" beat is unresolvable.

| # | Question | Stop condition |
|---|---|---|
| B1 | "Walk me through what the operator does today, step by step." | PM names ≥1 role + ≥1 named stage + ≥3 ordered steps. |
| B2 | "Where in those steps is the friction?" | PM names a specific step number from B1. |
| B3 (conditional) | "Are there workarounds people use today?" | Asked when B2 is "they fill in junk values" or similar. Stops when the workaround is named. |
| B4 (conditional) | "Is this in any way captured in a Confluence SOP today?" | Asked when no Confluence page came back from Phase 1. Stops when PM either provides a page-id or says "no SOP exists." |

### C. Scope (always asked — cap: 3)

| # | Question | Stop condition |
|---|---|---|
| C1 | "Which systems are touched? LSQ, LOS, LMS, Finbox, Digio, …?" | PM names ≥1 system. |
| C2 | "Which roles' workflow changes? BCM, CCM, NCM, BCPA, CCPA, BOM, COM, NSM, SM, BM, Auditor, Applicant, Co-applicant, …?" | PM names ≥1 role. List from `references/lap-glossary.md` is offered as a checkbox prompt, not free-text. |
| C3 (conditional) | "Which loan journeys? Fresh / SARAL / BT+TopUp / Internal TopUp?" | Asked when ticket touches eligibility or document flow. Stops when journeys are named or "all journeys" is confirmed. |

### D. Vocabulary (always asked — cap: 3)

This is where the glossary contract gets enforced. Every named stage, every dropdown label, every status string the PM uses is checked against the glossary in real time. Mismatches block progress until resolved.

| # | Question | Stop condition |
|---|---|---|
| D1 | "Confirm the named stage(s) involved." | Each named stage appears verbatim in the glossary OR the PM adds it (with owner) and we extend the glossary. |
| D2 | "What are the exact UI strings? Form names, button labels, dropdown values, status names." | Each string is captured in `'single quotes'` exactly as it appears on the panel. The skill does NOT paraphrase — if the PM types "the consider toggle," the skill asks "what does the panel actually say next to that toggle?" |
| D3 (conditional) | "What are the system field / API key names?" | Asked when ticket touches an integration. Stops when each name is captured (e.g., `mandate_amount`, `applicantConsentStatus`). |

### E. Scenario (type-driven — one question per branch, hard cap: 12)

This is the Branching Outcome heart. For type WC and SF, there are typically 1-3 branches (happy + 1 alt). For type BO, there are 2-N branches. For type MX, branches live inside one stage of a workflow.

| # | Question | Stop condition |
|---|---|---|
| E1 | "List every distinct outcome the operator might see after this action." | PM enumerates ≥2 outcomes for BO; ≥1 for SF/WC. Each outcome becomes Case 1, Case 2, … |
| E2..En | For each outcome: "What does the operator see? What do they do? If silent, how do they verify?" | Three slots filled per Case (See / Do / Verify). Verify slot can be "no verification needed — system handles it" but must be explicit. |
| E_edge | "What's the bypass / exception? E.g., 'CCM unavailable, NCM forwards to themselves.'" | At least one bypass named OR PM confirms "no exceptions." |
| E_time | "Are there time-windowed rules? E.g., 'within 72 hours' or 'expires in 10 days.'" | Each window quoted with unit; PM confirms "no time windows" if none. |

**Hard cap**: 12 cases. If PM tries to enumerate more, the skill responds "this looks like 2 tickets — should we scope this one to the first N branches and file a sibling for the rest?" (this is the over-scope detector — see file 07).

### F. Matrix (asked once when Phase 3 = RD with ≥2 dimensions, OR when E1 produced ≥4 cases that share dimensions — cap: 1 question, response is a structured table)

| # | Question | Stop condition |
|---|---|---|
| F1 | "What are the two (or three) dimensions, and what are the values on each?" Then: "Fill in the cell for every combination — including the cells where the answer is 'not applicable' or 'fallback to default.'" | A complete matrix table with no empty cells. Empty cells are explicit "N/A" or "default." |

LAP-2046's applicability matrix and LAP-2242's approval matrix both came from this question. The forcing function of "every cell" prevents the common failure where the PM lists a few cases and forgets the corner cases.

### G. Auto-comm (asked once when keyword "SMS" / "email" / "notification" / "alert" / "WhatsApp" appears in any prior answer — cap: 2)

| # | Question | Stop condition |
|---|---|---|
| G1 | "What's the exact verbiage of the SMS / email? Quote it character-for-character." | PM provides verbatim copy OR explicitly says "the verbiage will be drafted separately and shared in a comment." |
| G2 (conditional) | "Should the operator also send this manually as a backup?" | Yes / No — the manual-backup paired pattern is a release-note non-negotiable. |

### H. Silent action (asked once when PM uses words "auto-populated," "system fills," "callback applied," "automatically" — cap: 2)

| # | Question | Stop condition |
|---|---|---|
| H1 | "Which fields does the system populate silently?" | List of field names. |
| H2 | "Does the operator need to verify those fields, or trust the system?" | Explicit answer — drives the "you don't have to check anything" pattern in the release note. |

### I. Non-overridable rules (asked once when PM uses words "cannot be changed," "irrevocable," "system decides," "no manual override" — cap: 1)

| # | Question | Stop condition |
|---|---|---|
| I1 | "What exactly cannot be overridden, and what should the operator do if they want to challenge it?" | Two-part answer: the rule, the escalation path. |

### J. QA Scope (always asked — cap: 5)

| # | Question | Stop condition |
|---|---|---|
| J1 | "What's the happy-path verification?" | One bullet describing the primary positive scenario test. |
| J2 | "What's the bidirectional / toggle / regression check?" | Asked for all SF tickets; for others, skip. |
| J3 | "What downstream surfaces should be verified?" | Each downstream system (LMS, sanction letter, eligibility, FOIR, dashboards) named. |
| J4 | "What's the state-refresh check? Real-time vs. needs-logout vs. needs-stage-re-entry." | Explicit answer — comes from LAP-2039 lesson. |
| J5 | "What are the regression-blast surfaces — anything that previously worked and must still work?" | Single sentence; "none" is acceptable but must be explicit. |

### K. BA Scope (always asked — cap: 4)

The BA Scope is for assumptions the PM has made that need to be confirmed (or contradicted) by a stakeholder before the ticket is locked. Each item carries a Proposal + Impact, per LAP-2039.

| # | Question | Stop condition |
|---|---|---|
| K1 | "What assumption are you making that, if wrong, would break this ticket?" | One assumption named. |
| K2 | "Is there a primary-applicant vs. co-applicant distinction we're handling correctly?" | Explicit yes/no with reasoning. (Comes from LAP-2039.) |
| K3 | "Are there preserved-but-disabled fields, audit trail concerns, or rollback semantics?" | Explicit answer or "N/A." |
| K4 | "Anything else the BA must confirm before this is locked?" | Free, but capped — if PM lists ≥3 things, the skill asks them to pick the top 3. |

### L. Acceptance Criteria (always asked — cap: 2)

The point is to keep AC LEAN. The skill explicitly fights bloat.

| # | Question | Stop condition |
|---|---|---|
| L1 | "Forget the QA test plan. In 3-5 bullets, what does 'this works' mean?" | 3-5 bullets, each a verifiable assertion, none repeating §3 verbatim. |
| L2 (conditional) | "Are there discrete areas (Generation / Consent / Signing / Storage) that need their own AC sub-block?" | Asked only when the ticket has ≥3 distinct functional areas (LAP-1812 pattern). |

**Anti-bloat enforcement**: if the PM provides >5 AC bullets in any sub-block, the skill asks "which 5 are the must-have?" and writes the rest into a comment for QA reference.

### M. Sources (always asked — cap: 1)

| # | Question | Stop condition |
|---|---|---|
| M1 | "Drop every source link: spreadsheets, prototypes, related Confluence pages, reference docs, regulatory citations." | At least one link OR explicit "no external sources." |

### N. Contacts (always asked — cap: 1)

| # | Question | Stop condition |
|---|---|---|
| N1 | "Confirm the contact humans: reporter, assignee, business sponsor. (I'll fill from Jira, you confirm.)" | PM confirms each name OR overrides. |

## Question budget per ticket type

The question taxonomy is the same; the **gating** differs. Each type triggers a known subset:

| Type | Mandatory categories | Conditional triggers | Realistic question count |
|---|---|---|---|
| **WC** Workflow Change | A, B, C, D, E, J, K, L, M, N | F (if matrix), G (if auto-comm), H (if silent), I (if non-override) | 18-26 |
| **BO** Branching Outcome | A, C, D, E, J, K, L, M, N | B (if there's a current flow being replaced), F (if matrix), G/H/I as triggered | 14-22 |
| **MX** Mixed | A, B, C, D, E, J, K, L, M, N | F, G, H, I as triggered | 22-30 |
| **RD** Reference-data | A, C, D, F, J, L, M, N | E (if any branching), K (if assumptions need confirming) | 10-16 |
| **SF** Single-form | A, B, C, D, E, J, K, L, M, N | rare F/G/H/I | 16-22 |

**The realistic count is the cap, not the floor.** PMs with sharp answers finish faster. The skill never pads with filler questions to "be thorough."

## Stop conditions, generally

A category is complete when:

1. Every mandatory question has a non-empty answer written to `ANSWERS.md`, OR
2. The PM has explicitly skipped a question with a logged justification (per cowork-think-with-me's cross-question protocol), OR
3. The conditional trigger never fired and the category is moot.

The skill **never** silently moves to the next category. Each category transition is an explicit announcement: "Category J (QA Scope) — 5 questions. Ready?"

## Anti-pattern: question stacking

The skill asks ONE question, waits for ONE answer, writes it down, then asks the next. No "and also, can you confirm…" follow-on questions in the same turn. This is the single most important behavioural rule, inherited directly from cowork-think-with-me.

If a PM volunteers an answer to a future question ("oh also the SMS copy is X"), the skill captures it to `ANSWERS.md` and skips that question when its turn comes — but does not jump categories.

## When the skill stops asking entirely

Phase 4 is complete when:

- All mandatory categories for the detected type have hit their stop condition.
- All triggered conditional categories have hit their stop condition.
- The PM has not introduced a new dimension in their last 2 answers (a heuristic check that we've reached saturation).

If the last condition is uncertain, the skill announces "I think we have enough. One last open prompt: anything you'd add that I haven't asked about?" — capped at one such prompt, then we move to Phase 5 regardless of the answer (which is captured to `ANSWERS.md` anyway).
