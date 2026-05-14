# 00 — Blueprint (single-page architectural summary)

A 5-minute read for a PM who wants to understand how `lap-jira-uniform-ticket` works without reading the 9 detailed files. Each section maps to one detailed file.

---

## What this skill is

A Socratic Jira-ticket builder for the Kissht LAP team. Produces uniformly structured Story / Epic / Task tickets that the downstream `kissht-field-release-notes` skill can mechanically convert into a field release note (Pattern A Workflow Change / Pattern B Branching Outcome) with no extra PM input.

Same skill behaviour for every PM. No fast path. Same flow for a 5-line dropdown change as for a multi-stakeholder workflow rebuild. Quality over speed is locked.

---

## How a session feels (illustrative)

```
PM     "/lap-ticket — let BCMs skip salary slips when income is rent-only"
SKILL  Markdown or push to Jira?
PM     push
SKILL  Story / Epic / Task?
PM     Story
SKILL  OK — reserved LAP-2367. Searching related tickets...
       Found 3 tickets, 1 Confluence page. Tag each: parent / sibling / etc?
PM     LAP-2280 parent, LAP-2039 sibling, LAP-2046 unrelated.
SKILL  Drafted intent paragraph: "<...>". Sign off?
PM     yes
SKILL  Detected SC (Simple Change) — signals S3 + S7 fired. Override?
PM     no
SKILL  [Phase 4 begins — 12 questions in the SC question set]
       ...
SKILL  Phase 4 complete. Drafting into SC spine...
       Phase 6: found 2 repetitions, auto-cleaned.
       Phase 7: validated. Pushing to LAP-2367. Done.
```

---

## The 8 phases (file 01)

```
0 Activate         destination + issue type, reserve Jira key
1 Auto-search      JQL + CQL + glossary load
2 Verify context   PM tags related tickets + signs off intent paragraph
3 Classify type    8-signal heuristic → WC / BO / SC / RD / MX
4 Decompose        Socratic, 14 categories, MUST + CONDITIONAL questions
5 Draft            substitute answers into spine template (no generation freedom)
6 Anti-rep sweep   assertion index → DELETE / TRANSFORM / JUSTIFY
7 Validate         universal + type-specific + destination-specific gates
8 Deliver          markdown file OR push via editJiraIssue with round-trip diff
```

State persists in `.lap-ticket-session/<key>/` so compactions and resumes work.

---

## The 4 ticket types (file 02)

| Type | Maps to release-note | Detection (one line) | Exemplar |
|---|---|---|---|
| **WC** Workflow Change | Pattern A (Relook) | New stage / approval / SLA / mandatory action | LAP-1812, LAP-2048 |
| **BO** Branching Outcome | Pattern B (Renach) | One operator action with ≥2 if-branches, no new stage | LAP-2046 |
| **SC** Simple Change | Either pattern | Single-form / toggle / field move + workaround being killed | LAP-2039 (gold) |
| **RD** Reference Data | Mostly Pattern A | Dropdown / matrix / config / slab change | LAP-2052, LAP-2242 |
| **MX** Mixed (bridge) | Pattern A with Cases | Both WC + BO signals fire on same intent | (no pure exemplar) |

Plus a fallback spine for tickets that match no signal.

---

## The 14 question categories (file 03)

A intent · B current state · C surface area · D vocabulary · E proposed change · F matrix · G system strings · H auto-comm + silent · I edge cases · J QA scope · K BA open considerations · L AC · M sources · N contacts.

MUST per type, CONDITIONAL when triggered, DEFER until after first draft, NEVER (auto-filled from glossary or out of scope). One question per turn. Cap of 100 turns total before partial-draft fallback (file 08 F1).

---

## The 6 gates that close Phase 4 (file 04)

1. Mandatory categories complete for the detected type.
2. Triggered conditionals all answered.
3. Glossary fully matched (no ghost terms).
4. No unresolved contradictions.
5. Every rule has a system consequence.
6. Contacts are named humans, not departments.

All six pass simultaneously → exit Phase 4. None override.

---

## Glossary (file 05)

Reuses `kissht-field-release-notes/references/lap-glossary.md` + `lap-stages.md` + `lap-roles.md`. Three states for any term: known (silent), inferable variant (silent normalisation), unknown (inline question + add to LOCAL_GLOSSARY.md). Footer auto-renders the glossary entries used + new terms for periodic promotion to canonical.

Auto-suggest mode: when asking "which roles affected?" the skill renders the glossary roles inline as a picker — saves PM time and forces normalisation across PMs.

---

## Anti-repetition (file 06)

Phase 4 inline detector catches restatements at input. Phase 6 dedup pass builds an assertion index (canonical form per claim, tagged by section + entity), pairwise matches, and dispositions: auto DELETE / auto TRANSFORM / ask PM on JUSTIFY. Cap of 5 PM prompts and 2 dedup iterations.

LAP-2242's 10 non-repeating rules are the model: each rule canonicalises to a unique skeleton.

---

## System strings (file 07)

Verbatim, single-quoted, every panel label / dropdown / status / button / SMS body. Three triggers: inline (after E1), old/new pair (when rename/add/remove), auto-comm (when H1 fires). Optional OCR auto-extract from screenshots. Mandatory "System Strings Used" footer for the release-notes skill to extract en masse.

---

## Failure modes (file 08, top 3)

1. **PM rage-quits** → partial draft with `[BLOCKED]` markers; ship or hold; never fake completeness.
2. **Auto-search returns 50 noisy tickets** → after 7 unrelated tags, re-run with PM-supplied phrase; if still bad, accept empty.
3. **Two PMs file overlapping tickets** → collision detector at Phase 1 → 3-option chooser (continue same / sibling / independent) → COLLISION.md log.

Plus 7 more: thin answers, Loom dumps, empty glossary, no-template ticket types, compaction loss, Jira API failures, unresolved contradictions.

---

## Output schema (file 09)

Universal header (key, title, type, status, reporter, assignee, link, release-note line). Body sections in fixed order with required/forbidden/optional per type. Universal footer: System Strings → Glossary → Sources → Bug fan-out → Contacts.

Phase 7 gates: U1–U16 universal, type-specific (WC1–8 / BO1–7 / SC1–6 / RD1–6 / MX1–4), destination-specific (MD1–3 / JR1–6). Three hard-stops: empty intent, empty proposal, no type.

---

## The locked principles, restated

- **Plain English narrative + numbered structure.** No pseudocode, no JSON, no SQL.
- **Zero repetition.** Each section a unique job; the dedup pass is mandatory.
- **Lean AC** (3–5 bullets, observable). Body covers behaviour; AC just lists done gates.
- **Feeds release-notes skill cleanly.** Named stages with owners, rules with consequences, verbatim quoted system strings, branch outcomes, named human contacts.
- **Socratic, no fast path.** 50–100 questions if needed. Same flow for everyone.
- **Auto-search before asking PM about related tickets.**
- **PM picks destination per session** (markdown or Jira push).
- **Glossary reuses + extends** the release-notes skill's canonical files.

---

## What the executor session must build (handoff)

| Priority | Artifact |
|---|---|
| 1 | `SKILL.md` encoding 8-phase workflow + gates + anti-pattern list |
| 2 | `templates/` — spine-WC, spine-BO, spine-SC, spine-RD, spine-MX, spine-fallback, plus a Bug hand-off message |
| 3 | `references/` — question-taxonomy.md (file 03), output-gating-checklist.md (file 09), failure-recovery.md (file 08), anti-repetition.md (file 06), glossary-contract.md (file 05), system-strings-discipline.md (file 07) |
| 4 | Optional: ADF conversion script for Jira-push mode; markdown-first ships without it |

The 6 exemplars in `examples/` stay; PRINCIPLES.md in `reference/` stays; this `.deep-think/` folder is the rationale archive the executor consults when defending design decisions.

---

## The unresolved tension flagged for the synthesis pass

**The "no fast path" principle vs PM time-pressure reality.** The locked principles say every PM, every ticket, same flow — even a 5-line dropdown change goes through Phases 0–8 with its full question set (just trimmed by type). In practice, a senior PM filing the 50th SC ticket of the quarter will hit the rage-quit failure mode F1 frequently. The architecture handles this with partial drafts + BLOCKED markers, but the principle still bites: PMs may abandon the skill entirely for trivial tickets, defeating the cross-PM uniformity goal.

The architecture cannot resolve this without weakening the principle. Surfaced explicitly so the team can decide whether to (a) hold the line and accept some skill abandonment for trivial tickets, (b) introduce a "trivial change" express type that ships in 5 questions but ships SC-grade output, or (c) make BLOCKED-marker partial drafts the explicit norm for trivial tickets and lean into them as a feature rather than a fallback.

This is the single architectural decision the team should weigh in on before the executor session locks SKILL.md.
