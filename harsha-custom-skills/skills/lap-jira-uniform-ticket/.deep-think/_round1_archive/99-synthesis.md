# 99 — Synthesis: The Punchline Architecture

## Skill name
`lap-jira-uniform-ticket`

## One-line purpose
Socratic Jira-ticket builder for the Kissht LAP team that produces uniformly structured tickets (Story / Epic / Task) ready for ingestion by the `kissht-field-release-notes` skill.

## The architecture in one screen

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 0  Activate & set destination                                     │
│   - markdown vs. push-to-Jira                                           │
│   - issue type (Story / Epic / Task) — Bug routes elsewhere             │
│   - reserve Jira key (createJiraIssue stub) if pushing to Jira          │
│   GATE: SESSION_STATE.md created                                        │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 1  Auto-search Jira + Confluence                                  │
│   - JQL on intent keywords + recent LAP project tickets                 │
│   - CQL on intent keywords + canonical Confluence pages                 │
│   - load lap-glossary.md, lap-stages.md, lap-roles.md                   │
│   GATE: candidate sets returned to RELATED.md                           │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 2  Verify context with PM                                         │
│   - PM tags each related-ticket: parent / sibling / superseded / no     │
│   - PM confirms canonical Confluence sources                            │
│   - PM signs off scoped intent statement (1 paragraph)                  │
│   GATE: INTENT.md + RELATED.md confirmed                                │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 3  Detect ticket type                                             │
│   - Score signals → WC / BO / MX / RD / SF (or fallback)                │
│   - PM gets one override (logged, no second cross-question)             │
│   GATE: TYPE.md written with justification                              │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 4  Socratic decompose (the work)                                  │
│   - 14 categories A–N, type-driven mandatory + conditional triggers     │
│   - One question at a time, one answer at a time, written immediately   │
│   - Vocabulary check (Category D) enforced inline against glossary      │
│   - Contradiction detector after every new answer                       │
│   GATE: every mandatory + triggered category complete in ANSWERS.md     │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 5  Draft into the uniform spine                                   │
│   - Spine selected from TYPE.md                                         │
│   - Content sourced ONLY from INTENT.md + ANSWERS.md + RELATED.md       │
│   - Inline check: no UI string appears > 2x                             │
│   GATE: DRAFT.md exists, every spine slot filled or "N/A: ___"          │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 6  Anti-repetition pass                                           │
│   - Build assertion index → pairwise canonical-form matching            │
│   - DELETE / TRANSFORM / JUSTIFY / SPLIT each flagged pair              │
│   - Auto-apply DELETE + TRANSFORM; ask PM on JUSTIFY (max 5 prompts)    │
│   - Re-walk; max 2 dedup iterations                                     │
│   GATE: DEDUP.md complete, residuals justified                          │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 7  Validate against output gating checklist                       │
│   - Universal checks (U1–U16)                                           │
│   - Type-specific checks (WC1–8 / BO1–7 / MX1 / RD1–6 / SF1–6)          │
│   - Destination-specific checks (MD1–3 or JR1–6)                        │
│   - Loop back to specific phase per check; max 3 iterations             │
│   - 3 hard-stop failures: empty intent / empty proposal / no type       │
│   GATE: VALIDATION.md = PASS                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ PHASE 8  Deliver                                                        │
│   - markdown: write to user path, confirm overwrite if exists           │
│   - jira: convert to ADF, editJiraIssue, fetch back, diff               │
│   - Write DELIVERY.md with destination + ticket key                     │
│   - Archive .lap-ticket-session/<key>/ for collision detection          │
│   GATE: ticket lives in destination                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## State on disk: `.lap-ticket-session/<ticket-key-or-slug>/`

```
SESSION_STATE.md     current phase, next action, override count
INTENT.md            scoped intent paragraph (Phase 2)
RELATED.md           PM-confirmed related tickets + Confluence sources
TYPE.md              detected type + signal scores + override log
ANSWERS.md           every Phase 4 answer, organised by category
CONTRADICTIONS.md    detected contradictions and resolutions
DRAFT.md             Phase 5 output before dedup
DEDUP.md             Phase 6 dispositions per flagged pair
VALIDATION.md        Phase 7 results, iterations, warnings
DELIVERY.md          where it landed, ticket key, when
COLLISION.md         (if F8 fires) overlapping-PM detection
CROSS_QUESTIONS.md   PM overrides + cowork-think-with-me-style logs
LOCAL_GLOSSARY.md    (if glossary unreachable) local vocabulary additions
```

## Folder structure for the skill itself (executor reference)

```
lap-jira-uniform-ticket/
├── SKILL.md                                  ← workflow, principles, gates
├── references/
│   ├── PRINCIPLES.md                         ← the 8 content principles + anti-principles (existing)
│   ├── question-taxonomy.md                  ← from .deep-think/02
│   ├── ticket-type-detection.md              ← from .deep-think/03
│   ├── anti-repetition.md                    ← from .deep-think/04
│   ├── glossary-contract.md                  ← from .deep-think/05 — points at kissht-field-release-notes/references/lap-glossary.md
│   ├── output-gating-checklist.md            ← from .deep-think/06
│   ├── failure-recovery.md                   ← from .deep-think/07 grouped into 5 patterns
│   └── edge-cases.md                         ← from .deep-think/08
├── templates/
│   ├── spine-WC.md                           ← Workflow Change spine
│   ├── spine-BO.md                           ← Branching Outcome spine
│   ├── spine-MX.md                           ← Mixed spine (WC with embedded Cases)
│   ├── spine-RD.md                           ← Reference-data spine
│   ├── spine-SF.md                           ← Single-form spine
│   ├── spine-fallback.md                     ← Universal fallback (no type)
│   ├── spine-bug-handoff.md                  ← Hand-off message for Bugs
│   ├── spine-spike.md                        ← Spike spine (E10)
│   ├── spine-container-epic.md               ← Container-Epic spine (E3)
│   └── session-state.md                      ← SESSION_STATE.md template
├── examples/
│   ├── LAP-1812.md                           ← (existing)
│   ├── LAP-2039.md                           ← (existing)
│   ├── LAP-2046.md                           ← (existing)
│   ├── LAP-2048.md                           ← (existing)
│   ├── LAP-2052.md                           ← (existing)
│   └── LAP-2242.md                           ← (existing)
├── scripts/
│   └── (optional helpers: ADF conversion, JQL builder)
└── .deep-think/                              ← architecture rationale (this folder)
```

## What the executor session must build (handoff)

1. **SKILL.md** — encodes the 8-phase workflow with explicit gates, references the 8 principles, links templates and references. Modeled on cowork-think-with-me's structure (NON-NEGOTIABLE rules, complexity gate, activation workflow, anti-patterns).
2. **5 spine templates + 4 hand-off / specialty templates** — each spine literal-text with `{{slot}}` placeholders matching `ANSWERS.md` keys. The drafter substitutes; no generation.
3. **8 reference files** — distilled from the .deep-think/ files, action-oriented (the .deep-think/ files are rationale-oriented).
4. **Optional scripts** — markdown → ADF converter for Jira push, intent-keyword extractor for JQL/CQL builders. Both can be deferred to v2 if the skill is shipped markdown-first.

## The 5 architectural risks — surfaced explicitly

| Risk | What goes wrong | Mitigation built into design |
|---|---|---|
| **R1 PM friction at Phase 4** | The Socratic flow takes too long, PMs revolt | (a) Type detection trims to relevant categories; (b) front-load on urgency (E4); (c) partial-draft escape (F1); (d) plain-language fallback (F7); (e) one-question-at-a-time keeps each turn cheap |
| **R2 Cross-PM uniformity drift** | Two PMs answer the same question differently → tickets diverge in shape | (a) Question wording is templated, not free-form; (b) glossary normalisation makes vocabulary uniform; (c) spine templates are literal-text, no generation freedom; (d) Phase 7 gates the same checks for everyone |
| **R3 Glossary inflation / drift** | Each PM adds slightly different terms → glossary becomes redundant junk | (a) Phase 4 D prefers normalisation over addition; (b) synonyms list per term in glossary file; (c) periodic ops glossary-health pass (out of skill scope, flagged) |
| **R4 Type misdetection cascade** | Wrong type → wrong question set wasted → re-work | (a) Phase 3 detection uses 8 weighted signals + worked examples on all 6 exemplars; (b) PM override is one prompt; (c) F15 mid-Phase-4 type-switch protocol re-uses captured answers |
| **R5 Drift between our skill's output and the release-notes skill's contract** | The release-notes skill changes; our tickets stop being feedable | (a) Phase 7 universal checks (U2–U6) directly mirror the release-notes Phase 7 gate; (b) F18 round-trip — release-note failures comment back to our tickets; (c) version pinning of the dependency in skill metadata |

## The 6 deep-thinker failure modes — how each is addressed

| Failure mode | Where it bites | Defence |
|---|---|---|
| **Satisficing** | Picking the first phase model that "works" | File 01 documents 4 alternatives considered + reasons rejected. The 8-phase model is justified per phase against the failure it prevents (file 01 final table). |
| **Memory loss** | Skill forgets state across compactions | `.lap-ticket-session/` folder is mandatory; SESSION_STATE.md format mirrors cowork-think-with-me. Recovery protocol explicit (F9). |
| **Single-path exploration** | Only the obvious "ask & fill" loop considered | File 01 alternatives B (template-first) and A (single fluid Socratic) explicitly considered. File 02 considers ordering alternatives within Phase 4. File 03 considers fewer types and rejects. |
| **Confirmation bias** | Assuming exemplars are representative | File 00 names this risk; file 03 worked-detection table validates against all 6 exemplars; file 08 explicitly handles the long tail (Bugs, Spikes, Initiatives, new product lines) where exemplars don't cover. |
| **Missed complexity** | Under-handling regulatory, multi-system, hotfix, contradiction, collision | File 07 has 18 failure modes; file 08 has 10 edge cases + 4 acknowledged limits. Categories O (regulatory), F8 (collision), E4 (hotfix), F2/F10 (contradiction) all explicit. |
| **Executor-unfriendly output** | These files are too rationale-heavy for the synthesis pass to act on | Each file is structured: punchline → mechanism → tables. The synthesis pass (this file) gives the executor the skill folder layout, the gates, the deliverables, and the priorities. |

## Priority for the executor session that builds the skill

If the executor is time-constrained and can only build a subset, this is the order:

1. **SKILL.md + spine-WC + spine-BO + spine-SF** — covers the 3 most common types from the exemplar set. Skill is usable for ≈ 70% of the team's tickets.
2. **spine-MX + spine-RD** — covers the remaining 25%.
3. **8 reference files** — the skill works without them but they're load-bearing for behavioural consistency. Build these as the team starts using the skill and quirks emerge.
4. **Hand-off templates (Bug / Spike / container-Epic)** — needed for the 5–10% long tail. Can be initially stubbed as "this skill doesn't handle X — file manually" and later upgraded.
5. **ADF conversion script** — only needed for Jira push destination. If the team is happy with markdown-first delivery (write file, paste into Jira), this can be deferred entirely.

## What a typical PM session looks like (illustrative, not literal)

```
PM:    "I want to file a ticket: we're going to allow BCMs to skip uploading
        salary slips when income is from rent only."

Skill: [Phase 0] Markdown or push to Jira?
PM:    push to Jira

Skill: [Phase 0] Story / Epic / Task?
PM:    story

Skill: [Phase 0] OK — reserved LAP-2367. Loading session state.
       [Phase 1] Searching… found 3 related tickets and 1 Confluence page.
                LAP-2046 (PAN re-verification ETB), LAP-2039 (Income Considered
                move), LAP-2280 (Salary Slip mandatoriness — open). Confluence
                page 1088716805 (LAP LOS canonical).
       [Phase 2] Are these the right related tickets?
PM:    LAP-2280 yes (parent), LAP-2039 sibling, LAP-2046 unrelated

Skill: [Phase 2] Logged. One-paragraph intent — confirm:
       "Allow BCMs to skip salary-slip upload at the Credit PD task when the
        co-applicant's income source is rent-only, removing a redundant
        document upload that doesn't affect underwriting."
PM:    yes

Skill: [Phase 3] Detected SF (Single-form behaviour change). Signals: S3
       (toggle-like behaviour on Credit PD form), S7 (current workaround:
       BCMs upload garbage scans). Override?
PM:    no, SF is right

Skill: [Phase 4 A] Done — A1 + A2 already in your intent. Skipping to B.
       [Phase 4 B1] Walk me through what the BCM does today, step by step.
PM:    [answers]

Skill: [Phase 4 B2] Where's the friction?
... (continues through categories)

Skill: [Phase 4 N] Reporter you, assignee Mohini, sponsor Paras — confirm?
PM:    yes

Skill: [Phase 5] Drafting into SF spine… DRAFT.md ready.
       [Phase 6] Found 2 repetitions. Auto-applied 1 DELETE, 1 TRANSFORM.
       [Phase 7] Validating… 14/16 universal + 6/6 SF checks pass. Looping
       back: SF5 needs a state-refresh QA bullet — does the rent-source
       toggle update Final Sanction in real-time?
PM:    yes, real-time

Skill: [Phase 7] Re-validating… PASS. [Phase 8] Pushing to LAP-2367…
       posted. ADF diff clean. Session archived. Done.
```

## Confirmation

99-synthesis.md is ready. The synthesis hands the executor session:

- An 8-phase workflow with one-line summaries.
- A folder layout for the skill.
- A prioritised build order.
- Direct mapping from rationale (this folder) to skill artifacts.
- The 5 architectural risks and the 6 deep-thinker failure modes, both explicitly addressed.

The executor can build SKILL.md and the 5 core spine templates from this synthesis without re-reading the rationale files, but the rationale files exist for any decision the executor needs to defend.
