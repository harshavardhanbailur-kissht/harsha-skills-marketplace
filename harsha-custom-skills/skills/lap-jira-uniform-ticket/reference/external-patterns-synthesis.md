# External Patterns — One-Page Synthesis

**The punchline:** The 6 LAP exemplars are already a defensible middle path between Linear's anti-template minimalism and GitLab's heavy 12-section template. Don't import any whole external pattern. Adopt 3-4 atoms. Reject 5-6 known bad imports.

---

## Top 3 to ADOPT (ranked by impact)

1. **GitLab's "Release-note line" at the top of the ticket.** A single operator-readable sentence the writer drafts up-front. Direct feed into `kissht-field-release-notes`. Example: *"CCM cases up to 7L now auto-route to SCH if CCM is unavailable."* Lift verbatim into release notes.

2. **Shape Up's "No-gos" + Notion's "Non-goals" — collapsed into one "Out of scope" line inside BA Scope.** Prevents regression scope-creep. Example: *"Out of scope: We are NOT changing the Edit-form behaviour for the primary applicant — that path stays Yes-locked."*

3. **Google Design Doc's "Alternatives considered."** Optional 2-3 sentence paragraph inside BA Scope, used when the design picks one of several plausible approaches. Pre-empts later "why didn't you just..." reviews.

## Top 3 to REJECT (ranked by damage if adopted)

1. **Given-When-Then AC** (Atlassian's recommended form). Bloats AC into a regression script. Violates lean-AC principle. The body's numbered logic IS the truth; AC is a thin derived view.

2. **Connextra "As a / I want / so that" as MANDATORY opening.** Breaks the LAP-2052 / LAP-2046 voice. Allow it (LAP-1812 uses it well) but never require it. Allow Job Story format as the trigger-led alternative.

3. **PR-FAQ press-release format.** Marketing prose for an internal feature ticket — wrong audience and wrong register. Borrow the "readable cold" gate, reject the format.

## Unexpected finding

Linear's anti-template doctrine AND GitLab's heavy-template doctrine BOTH score lower than the LAP exemplars on no-repetition fit. The middle path the LAP exemplars already walk — 6-7 named sections each with a unique job — is structurally more anti-repetition than either extreme. The new skill's framing should NOT be "we should adopt X external pattern" but "we already have a defensible middle path; harden it with 3-4 atomic borrowings, and explicitly forbid 5-6 known bad imports."

## Where LAP already MEETS or EXCEEDS world's best practice (do not over-correct)

- **Open Considerations for BA** (assumption + proposal + impact) is BETTER than Notion's bare "Open questions" because it forces the writer to commit to a default and name the cost of being wrong.
- **Numbered Logic with consequences** is BETTER than GitLab's flat "Functional requirements" because every rule names the system behaviour.
- **Verbatim system strings** (LAP-1812 SMS verbiage) is rare in any external pattern — most gesture at "messaging" without quoting. The LAP practice of pasting the exact string is operator gold.
- **Bug fan-out as quality signal** is unique to the LAP exemplars and proves the ticket survived contact with reality.

## Write-time gates the new skill should enforce (borrowed atoms)

| Gate | Source |
|---|---|
| "If a sentence does not change reader behaviour, delete it." | Linear Method |
| "If a new PM joining tomorrow can't grasp the intent paragraph cold, rewrite." | Amazon PR-FAQ |
| "If you cannot write the 1-paragraph intent in plain English without bullets, the ticket is not ready." | Stripe culture |
| "Every AC bullet must be observable in UAT." | INVEST "Testable" |
| "If your ticket changes user-facing copy, paste the exact string verbatim." | LAP-1812 (own canon, codify it) |

## 3 C's vocabulary to teach the LAP team

| Layer | Name | What's there |
|---|---|---|
| Card | The intent | 1-paragraph plain-English summary + optional Connextra/Job Story |
| Conversation | The body | Current/Proposed (when killing a workaround), Numbered Logic with consequences, Tables for matrices, QA Scope, BA Scope (with Out-of-scope, Open Considerations, Alternatives Considered when applicable), verbatim system strings |
| Confirmation | The AC | 3-5 lean bullets, named sub-areas, derived view of body, never a re-listing |

---

*Backed by full research in `external-patterns-research.md`.*
