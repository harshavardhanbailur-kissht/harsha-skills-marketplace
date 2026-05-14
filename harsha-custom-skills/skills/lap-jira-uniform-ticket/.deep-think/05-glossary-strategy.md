# 05 — Glossary Surfacing Strategy

## The contract with `kissht-field-release-notes`

The release-notes skill owns the canonical LAP vocabulary in three files:

- `kissht-field-release-notes/references/lap-glossary.md` — domain terms, system strings, Renach vocabulary, buffer policy.
- `kissht-field-release-notes/knowledge-base/lap-stages.md` — every LAP stage with owners, including the Post Sanction substructure and Push-to-LMS contract.
- `kissht-field-release-notes/knowledge-base/lap-roles.md` — role roster (BCM, CCM, NCM, BCPA, CCPA, BOM, COM, NSM, SM, BM, Sales RM, Auditor, Applicant, Co-applicant).

`lap-jira-uniform-ticket` **reuses** these files. It does not re-build the vocabulary. It MAY extend them via the `LOCAL_GLOSSARY.md` mechanism described below — extensions are eventually promoted to the canonical files via a periodic glossary-health pass (out of scope for the skill itself; flagged in file 08 as an ops responsibility).

This is the same pattern other skills in the marketplace use to share `references/`: the release-notes skill is the source of truth, the ticket skill is a consumer, and a downstream PR can promote local extensions upstream.

---

## The three states of any term mentioned by the PM

When a PM types a term during Phase 4, the skill classifies it into one of three states:

### State 1 — Known (in canonical glossary)

Action: silent. The term is rendered consistently in the draft (preferred form from glossary), and on first mention in the ticket body the term is linked to the glossary footer entry. No question asked.

Examples: BCM, CCM, NCM, Credit PD, Final Sanction Pending, Mark as Complete, Renach, e-Mandate, Push to LMS, Lost Rejected.

### State 2 — Inferable (synonym / variant of a known term)

Action: silent normalisation. The skill detects "Branch Credit Manager" as a verbose form of "BCM," "Credit Personal Discussion" as a verbose form of "Credit PD," and normalises to the preferred form. The variant is logged in the session for the periodic glossary-health pass.

Detection cue: case-insensitive match to a known acronym expansion, or a prefix/suffix match (e.g., "PD activity" ≈ "Credit PD activity"). The skill's confidence threshold is conservative — when in doubt, treat as State 3.

### State 3 — Unknown (ghost term)

Action: pause Phase 4 main flow, ask question D2 inline:

> "You mentioned `<term>`. I don't have it in the LAP glossary. In one sentence: what is it? Is it a stage / role / system string / abbreviation / concept? I'll add it to the local glossary for this session and flag it for the team glossary."

The PM's answer is written to `LOCAL_GLOSSARY.md` (one entry: `<term> | <type> | <definition> | first mentioned: <category>.<question>`). The main Phase 4 flow resumes immediately after.

A ghost term blocks Gate 3 (file 04) until defined. The skill does not invent definitions, does not skip-and-continue, does not hand-wave.

---

## When to surface the full glossary vs inline a single definition

### Surface a single inline definition

When the PM mentions a known term that's likely unfamiliar to other PMs on the team — typically anything more obscure than the top-tier roles (BCM/CCM/NCM) and stages (Credit PD / Final Sanction). The skill renders the term followed by a parenthetical on first mention, then links to the glossary footer:

```
The CCPA (Compliance Credit Process Associate, see footer) reviews the case after CCM approval.
```

The trigger is glossary metadata: each entry is tagged `tier: A | B | C` (A = universal, no inline gloss needed; B = role-specific, gloss on first mention; C = niche, gloss + footer link). The ticket renders B and C inline; A only in the footer.

### Surface the full glossary as a reference

Never inside the ticket body. The full glossary lives behind a single link in the Sources footer:

> Glossary: `kissht-field-release-notes/references/lap-glossary.md`

Surfacing the full glossary inline would bloat the ticket and violate the no-repetition discipline. The footer link is enough — every LAP team member knows where the canonical glossary lives.

### Surface the full role roster

For RD-type tickets that involve role acronyms (LAP-2242 pattern), the skill embeds a **Role Definitions appendix** at the end of the ticket body — a 5–10 line table extracted from `lap-roles.md` covering only the roles mentioned. This is an exception to "never inline the full glossary" because routing-matrix tickets are read by ops/training audiences who don't have the glossary file open.

---

## Interaction with the Phase 4 question flow

### Glossary-driven question construction

When the skill asks D1 ("Which roles are affected?"), it auto-suggests the inline picker from the glossary:

> Pick from: BCM, CCM, NCM, SCH, BCPA, CCPA, BOM, COM, NSM, SM, BM, Sales RM, Auditor, Applicant, Co-applicant. Add any role that's not in this list and define it now.

This:
1. Saves PM time (they recognise their own acronyms instead of typing them out).
2. Forces normalisation (PM picks "BCM" not "branch manager").
3. Signals to the PM what the skill considers normal (training effect over many sessions).

The same auto-suggest pattern applies to:

- C1 stage names (auto-list from `lap-stages.md`).
- C3 system names (LSQ, LMS, Digio, CIBIL, NSDL).
- E1 BO Case structure (auto-suggest "Case 1, Case 2, …" naming).
- G1 system strings (auto-list common ones already in glossary — Lost Rejected, Initiate E-Mandate Registration?, mandate_amount, etc., as recall prompts).

### Glossary-driven contradiction detection

If a PM uses two different terms for the same concept across answers (e.g., "approval queue" in B1 and "Approval Pending" in E1), the contradiction detector (file 06) catches the divergence and asks:

> "You've used both `approval queue` and `Approval Pending` for what looks like the same concept. The glossary has `Approval Pending` as the canonical name. Should I normalise both to `Approval Pending`, or are these actually different things?"

PM picks. Resolution logged. This is the source of cross-PM uniformity at the vocabulary layer.

---

## Footer rendering

Every ticket ends with a glossary footer in two parts:

```
---
**Glossary used in this ticket** (auto-generated):
- BCM — Branch Credit Manager (canonical)
- Credit PD — Credit Personal Discussion stage (canonical)
- NIC — Non Income Considered tab (canonical)
- SCH — State Credit Head (canonical, tier B)

**New terms added by this session** (for promotion to canonical glossary):
- (none)

Full glossary: kissht-field-release-notes/references/lap-glossary.md
```

The "New terms" sub-section signals to the team that this ticket extended the vocabulary. A weekly glossary-health pass reviews new terms across all tickets and promotes the keepers; the rest are aliases or one-offs.

---

## What happens on first install (empty glossary)

Edge case: PM installs `lap-jira-uniform-ticket` before `kissht-field-release-notes`, or the glossary files are unreadable.

Detection: at Phase 1, the skill tries to load `lap-glossary.md` etc. If load fails:

1. Skill banner-warns: "I can't load the LAP glossary. Falling back to local-only mode — every term you mention will be treated as new and asked about. This is going to be slow."
2. Skill creates `LOCAL_GLOSSARY.md` as the session glossary, seeded with a hardcoded minimal list (BCM, CCM, NCM, Credit PD, Final Sanction Pending — the 5 most universal).
3. After delivery, the skill writes a `GLOSSARY_BOOTSTRAP.md` with every term defined this session, and prompts the PM to either (a) install `kissht-field-release-notes` and re-run, or (b) hand `GLOSSARY_BOOTSTRAP.md` to the team for review.

This is the file 08 F-Empty-Glossary handling.

---

## What happens on glossary collision

If the PM defines a term that conflicts with an existing glossary entry (e.g., PM says "BCM = Branch Customer Manager" when glossary says "BCM = Branch Credit Manager"):

1. Skill flags the collision: "The glossary has `BCM` defined as `Branch Credit Manager`. You said `Branch Customer Manager`. Are these the same role with different names, or genuinely different roles?"
2. PM picks: same / different.
3. **If same:** PM picks the canonical name; skill normalises and logs an alias in `LOCAL_GLOSSARY.md`.
4. **If different:** PM provides a disambiguating qualifier (e.g., "BCM-Customer" vs "BCM-Credit"); both go into `LOCAL_GLOSSARY.md`; the skill flags this for the glossary-health pass as a naming conflict to resolve at the team level.

The skill never silently overrides the canonical glossary.

---

## Summary

| Term state | Action | Question to PM |
|---|---|---|
| Known | Silent + render consistently | None |
| Inferable variant | Silent normalisation | None (logged for review) |
| Unknown (ghost) | Pause flow | D2 inline, define in one sentence |
| Collision | Flag | Disambiguate same/different |
| Glossary unreachable | Bootstrap mode | Per-term inline (slow) |

Glossary work is silent when it can be silent and explicit when it must be. The PM never sees the full vocabulary file dumped into chat — only what's needed at the question point.
