# 05 — Glossary Surfacing

## The contract with kissht-field-release-notes

That skill ships with `references/lap-glossary.md` and `knowledge-base/lap-stages.md` already curated. Our skill **re-uses** that glossary as its source of truth — it does not maintain a parallel one. When the ticket-skill needs a term, it loads from the release-notes skill's glossary path. When the PM uses a new term, the ticket-skill **extends** the same glossary file (writing back to the canonical location), not a local copy.

This means: a stage name added by Paras while drafting LAP-2300 is available to Mohini drafting LAP-2310 the next day, AND to the release-notes skill when it generates the operator-facing note.

## When the glossary loads

Three loading moments, each with a different scope:

### Moment 1 — Phase 1 auto-search (full glossary loaded into the skill's working context)

Before asking the PM anything, the skill loads:

- `kissht-field-release-notes/references/lap-glossary.md` — all terms
- `kissht-field-release-notes/knowledge-base/lap-stages.md` — all stages with owners
- `kissht-field-release-notes/knowledge-base/lap-roles.md` — all role acronyms

This is one read at session start. The skill keeps these in context for the rest of the session.

### Moment 2 — Phase 2 verify (used for context summaries)

When the skill summarises the related-tickets back to the PM, it uses canonical glossary terms for stages and roles. If the related ticket's body uses a non-canonical term, the skill normalises and notes "this related ticket called it 'Approval Pending' — that's our 'Final Sanction Approval Pending' stage."

This subtly teaches the PM the canonical vocabulary without lecturing.

### Moment 3 — Phase 4 vocabulary category (Category D — active enforcement)

When the PM uses a term during answers, the skill checks against the loaded glossary:

- **Term matches glossary** → silent acceptance; skill records the canonical form in `ANSWERS.md`.
- **Term is a known synonym** (glossary lists alternates) → silent normalisation; skill rewrites to canonical form in `ANSWERS.md` and shows the normalisation in the next message ("I'll use 'Final Sanction Pending' — that's the canonical name for what you called 'FSP'").
- **Term is unknown** → the skill asks: "I don't have 'XYZ' in the LAP glossary. Three options: (a) it's a typo / paraphrase of an existing stage — pick from the list; (b) it's a new stage we should add to the glossary — give me the owner role; (c) it's a temporary internal name and we'll use the canonical version — pick from the list."

The PM picks (a), (b), or (c). If (b), the glossary is extended in the canonical location with a comment `# added by <PM> on <date> from <ticket-key>`.

## How the skill teaches without lecturing

The PM never sees a "here's the glossary, please learn it" message. They only ever see:

1. **Inline normalisation** — the skill writes the canonical term and shows the change ("noted as 'Post Sanction' — that's our canonical name").
2. **Implicit demonstration** — when summarising related tickets back, canonical terms are used.
3. **One-prompt-per-unknown** — a single multiple-choice prompt when a term doesn't match.

This is the same pedagogical stance as cowork-think-with-me's Socratic style: don't tell the user the answer, structure the conversation so the answer becomes obvious.

## Glossary citations in the final ticket

The final ticket body does NOT cite the glossary inline (no footnotes, no parenthetical "see glossary" tags — that would clutter the body). Instead:

- **Stage names** appear in the body verbatim (canonical form).
- **Role acronyms** appear in the body verbatim. If the ticket introduces a role acronym for the first time, the skill auto-adds a **Role Definitions (for reference — please confirm / correct)** appendix at the bottom of the ticket (the LAP-2242 pattern). Each acronym in the ticket gets one line with its expansion.
- **System strings** appear in the body in `'single quotes'`, exactly as the panel shows them.

The Role Definitions appendix is conditional: only added when the ticket introduces a role acronym not previously seen in the project. This avoids the LAP-1812 case (where every reader knows what CPA means) being padded with definitions.

## What if the kissht-field-release-notes glossary isn't available

The skill is designed to be tightly coupled to that glossary, but must degrade gracefully if it's not loadable (e.g., the PM is running the skill in an environment without that plugin installed):

1. **Phase 1**: skill detects glossary absence and warns: "I can't find the LAP glossary — I'll work without it but I'll be more cautious about new terms. Confirm any vocabulary changes manually."
2. **Phase 4 D**: every term the PM uses is treated as "unknown" and asked about. The session writes a local `LOCAL_GLOSSARY.md` to `.lap-ticket-session/` for the duration of this ticket.
3. **Delivery**: when the ticket lands, the skill writes a comment on the Jira ticket summarising the new vocabulary terms used, so they can be back-ported to the canonical glossary later.

This isn't expected to be the common case — the skill is shipped as part of the LAP plugin pack alongside kissht-field-release-notes — but it must not hard-fail.

## The "glossary inflation" risk

Every PM who adds a new term inflates the glossary. Over a quarter, the glossary could double in size with redundant terms ("Approval Pending Stage" + "Approval Pending" + "Approval Stage" all meaning the same thing).

Mitigation:

- The skill, in Phase 4 D, prefers normalisation over addition. Option (a) is presented before option (b).
- A periodic glossary-health pass (out of scope for this skill but flagged for ops) consolidates synonyms.
- The glossary file itself supports a **synonyms** list per term, so when an alternate phrasing is added, it goes under the canonical term, not as a new top-level entry.

## What the skill does NOT do with the glossary

- It does NOT auto-correct a PM's casual phrasing to glossary terms in their incoming messages. The skill normalises in `ANSWERS.md` and in the final ticket, not in the chat history.
- It does NOT lecture. There is no "by the way, the canonical term is X" without the PM having used the term first.
- It does NOT enforce vocabulary on prose explanations in the Intent paragraph or Problem statement. The Intent and Problem are allowed to use natural language; only structural slots (stage names, role names, system strings) get enforced.
- It does NOT block progress on a vocabulary mismatch. The Phase 4 D prompt is a 1-question pause, not a gate failure.

## Glossary-driven validation in Phase 7

The Phase 7 validator runs these glossary-related checks:

- Every named stage in the body matches the canonical form in `lap-stages.md`. ✗ → loop back to Phase 5 with a one-sentence fix prompt.
- Every named stage that is `new` (per Phase 4 D option (b)) has an owner role in `lap-stages.md`. ✗ → loop back to Phase 4 D to capture the owner.
- Every role acronym in the body either appears in `lap-roles.md` OR is defined in the Role Definitions appendix.
- Every `'single-quoted system string'` is unique to one specific UI element (no two strings refer to the same element).

These checks catch the failure mode where the PM and the skill agree on a term but the released ticket goes out with the non-canonical form because of a Phase 5 typo.
