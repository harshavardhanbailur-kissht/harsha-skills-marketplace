# 08 — Edge Cases + Extensions

## Where the pattern stretches gracefully

These are the cases where the 5-type detection + uniform spine accommodates the unusual ticket without breaking. The skill handles them with documented adjustments.

### E1 — Multi-stakeholder tickets (LSQ + LAP + LMS, or LAP + LSQ + Finbox + Digio)

**Example shape**: a ticket that requires changes in 3 systems with cross-system contracts. LAP-1812 is partially this (LAP + LSQ + Digio + Kissht consent). LAP-2046 is partially this (LAP + LSQ).

**How the pattern holds**: 
- Type detection still picks WC or BO based on the operator-facing change. The cross-system aspect is captured in Category C (which systems) and surfaces in the Functional Flow as system-tagged sub-steps ("LSQ triggers ___ → Kissht returns ___").
- The Functional Flow numbering may include system tags: `1.1 (LSQ) ___ / 1.2 (Kissht) ___ / 1.3 (Digio) ___`.
- Sources section explicitly enumerates each system's owning team's contact.
- BA Scope captures the system-contract assumptions ("assumed the LMS push payload is the existing schema; if it changes, downstream NACH will break").

**Where it can break**: when the operator-facing change is genuinely different per system (e.g., BCM does X in LSQ AND CCM does Y in LOS). In that case the skill detects it as MX (workflow change with branches by-system) and prompts: "Are these one ticket or two? If the BCM and CCM changes are independent, file two."

### E2 — Bug-fix tickets

**Pattern hold**: NO. Bug tickets follow a different structure (RCA / Steps to reproduce / Expected vs Actual / Root cause / Fix / Regression scope). Our skill is for forward-looking change tickets, not for incident remediation.

**Skill behaviour**: detect at Phase 0 (issue type = Bug) and hand off cleanly. The hand-off message names the sister skill (`kissht-bug-rca` — to be built; not part of this skill's scope) and the alternative manual flow.

**One nuance**: if a "bug" ticket is actually a small enhancement disguised as a bug ("the panel says X but it should say Y"), the PM can override the issue type at Phase 0 and proceed. The skill flags: "This was filed as a Bug but it looks like a copy / config change — proceed as RD or SF? You can also re-file as Story in Jira."

### E3 — Epic-level tickets

**Pattern hold**: YES, with a tweak.

LAP-2048 is an Epic and was successfully captured as a multi-act WC. So Epics that have functional content of their own use the WC spine.

But there's a second class of Epic — the **container Epic** that exists only to group related Stories (LAP-1897 is mentioned as the parent of LAP-2039; presumably LAP-1897 has no functional content of its own). For container Epics, the spine is reduced:

```
Theme         (1 paragraph — what this Epic groups and why)
Sub-stories   (bullet list of expected stories, with one-line descriptors)
Success       (the outcome that all sub-stories collectively deliver)
Sources
Contacts
```

The skill detects container vs functional Epic by asking once: "Does this Epic have functional content of its own, or is it a container for sub-stories?" PM picks; the question count and spine adapt.

### E4 — Hotfix / urgent tickets — does the rigour flex?

**Default position**: NO. Same flow for everyone, including urgent tickets. The locked constraint is non-negotiable.

**However**: an urgent ticket usually means the PM has very limited time. The skill's behaviour is to keep the SAME phase structure but **front-load the most critical questions** when the PM signals urgency:

- PM intent contains "urgent" / "hotfix" / "production issue" / "regulatory deadline" → skill announces: "Urgency noted. I'll keep the same flow but I'll front-load the critical questions. Estimated 5-7 minutes."
- Phase 4 is reordered: A → B → E → J → L → C → D → K → M → N (intent + current + scenarios + QA + AC first; vocabulary, BA, sources after). The PM can ship after the first 6 categories if they explicitly say "ship now," producing a markdown draft. Push-to-Jira still requires all categories.

**Why not a true fast-path**: because the entire team uses this skill to produce uniform tickets. If urgent tickets get a shorter spine, downstream the release-notes skill has to special-case them. Better to keep the spine uniform and accept that urgent tickets take 5-7 minutes instead of 3.

### E5 — Tickets that need a regulatory citation (RBI guidelines, SEBI, GST)

**Pattern hold**: YES, with an extension.

The skill adds **Category O — Regulatory Citation** when any prior answer contains keywords: "RBI" / "SEBI" / "regulator" / "compliance" / "RBI-DLG" / "circular" / "RBI guideline" / "PMLA" / "KYC norms" / "GDPR" / "data localisation" / "Aadhaar Act."

| O1 | "What's the regulatory source? RBI circular number, SEBI guideline, or specific Act + section." | Citation captured verbatim in Sources block AND quoted in the body where the rule is introduced. |
| O2 | "Is the regulatory rule already in our Confluence compliance hub?" | Page-id captured if yes; flagged for ops to add if no. |

**Validation extension**: U3 (every rule has a consequence) is supplemented with U17 (every regulatory rule has a citation). A rule labelled "RBI requires ___" without a citation fails Phase 7 and loops back.

### E6 — Tickets that introduce new vocabulary the team doesn't yet have

**Example**: a ticket introduces a new role ("CCM-Senior") or a new stage ("Pre-Sanction Verification") that has never existed in LAP before.

**How the pattern holds**: Phase 4 D handles this — Option (b) "new term, here's the owner." The new term is added to the canonical glossary. The Role Definitions appendix in the ticket includes the new term.

**Where it stretches**: if the new term is fundamental to the change (the whole ticket is about introducing CCM-Senior), the skill ensures the term is defined in the **Intent paragraph itself**, not just the appendix. The PM is asked: "CCM-Senior is new — give me a one-line definition we'll put in the Intent."

### E7 — Tickets that are partially out-of-band — they reference a Slack thread or a meeting decision

**Example**: "Per yesterday's PM-sync, we're going to flip Income Considered. See Slack #lap-product."

**How the pattern holds**: the Sources block accepts non-Jira / non-Confluence sources but they're flagged: "External source: Slack thread (not archivable)." The skill suggests: "Want to convert that Slack thread into a Confluence decision-doc? It'll outlive the thread."

This is a soft nudge, not a gate. Tickets ship with Slack references; the team learns to convert important threads to Confluence over time.

### E8 — Tickets that revert / undo a previous ticket

**Example**: "Revert LAP-2039 — the Income Considered move broke X."

**How the pattern holds**: type detection picks SF or WC depending on the original. The skill auto-pulls LAP-2039 into Phase 1 and the Intent paragraph is structured as: "Reverts the change introduced in LAP-2039 because ___."

**Special slot**: a **Revert Scope** block appears between Intent and Proposed solution: "Restore: ___. Preserve: ___. Cleanup: ___." This captures what's reverted, what's kept (because it has audit value or downstream depends on it), and what's cleaned up.

### E9 — Tickets that span multiple sprints / phases (Phase 1, Phase 2, Phase 3 of a feature)

**Example**: LAP-1812 is "E-Sign Phase 2" — Phase 1 was a separate ticket.

**How the pattern holds**: the title naturally carries the phase tag ("Phase 2"). The Intent paragraph cites the prior phase ("Phase 1 introduced X; Phase 2 adds Y"). The skill auto-finds the prior-phase ticket(s) in Phase 1 search.

**Validation extension**: U18 (added when title or intent contains "Phase N"): a previous-phase ticket (Phase N-1) is linked in Sources. ✗ → loop back to Phase 4 M to add it.

### E10 — Tickets that are spike / research / exploration

**Example**: "Spike: investigate whether Finbox can return income data faster than LSQ."

**How the pattern holds**: NOT WELL. Spikes are not feature tickets and don't deserve the full spine.

**Skill behaviour**: detect at Phase 0 (intent contains "spike" / "investigate" / "research" / "explore" / "evaluate" / "POC" / "PoC") and offer the **Spike spine**: Question / Hypotheses / Approach / Success criteria / Time-box / Sources. This is a 3-question Phase 4, not the full taxonomy. Spikes are not feedable to the release-notes skill (no operator-facing change), and the ticket is flagged accordingly.

## Where the pattern genuinely breaks (acknowledged limits)

These are cases the skill explicitly does NOT handle well, and we accept that.

### B1 — Multi-team multi-Epic platform initiatives

If the change is "rebuild the entire LOS approval engine," the ticket is too large for any single PM session. The skill detects this when Phase 4 question E1 produces ≥ 8 distinct outcomes AND Phase 4 question C1 names ≥ 4 systems. It announces: "This is platform-scale, not feature-scale. The lap-jira-uniform-ticket skill produces a Story or Epic; what you're describing needs a multi-Epic Initiative. Let me draft a one-paragraph Initiative summary you can use to seed a planning session, then file the constituent Epics through this skill one by one." Skill produces the summary; doesn't try to produce the Initiative.

### B2 — Tickets with major undecided scope

If at Phase 2 verify, the PM says "I'm not sure if this is one ticket or three — let's figure that out as we go," the skill cannot produce a uniform output. It pivots: "Let's pause the ticket draft and run a `cowork-think-with-me` session to scope this. I'll resume this skill once the scope is locked." This is a soft hand-off to a sister skill, not a refusal.

### B3 — Tickets in a brand-new domain the LAP glossary doesn't cover

If the ticket is for a new product line ("starting Auto Loans"), the LAP glossary is irrelevant. The skill warns: "This is for a new product line. The LAP glossary doesn't apply. I can produce a uniform ticket but you'll be defining all vocabulary from scratch — this'll take longer." PM can proceed; everything in Phase 4 D is treated as Option (b). The output is a uniform ticket but with a heavy Glossary Extension footer that needs ops attention before the next ticket in the new product.

### B4 — Tickets that depend on a decision that hasn't been made yet

"We'll route this to either CCM or NCM depending on what compliance says." The skill captures this in BA Scope as an Open Consideration with an explicit "blocked-pending-decision" tag. The ticket ships but is flagged not-feedable to the release-notes skill until the decision is made and the ticket updated.

## Extensions to consider (not in MVP, flagged for v2)

| # | Extension | Why deferred to v2 |
|---|---|---|
| X1 | Auto-detection of duplicate tickets across the team (file 07 F8 collision detection extended to look at draft sessions across PMs in the last 7 days) | Requires shared state across PM sessions; needs infra |
| X2 | Auto-suggest of the canonical assignee based on the named systems (e.g., if Digio is named, route to the integrations team's lead) | Requires a maintained system-to-team map |
| X3 | Multi-language support — the skill operates in Hindi for non-native-English PMs | Out of MVP; plain-language fallback (file 07 F7) covers the immediate need |
| X4 | Voice-input mode where PM speaks the ticket and the skill structures it | Out of MVP; nice-to-have but not on the critical path |
| X5 | Integration with sprint planning — the skill suggests sprint placement based on team capacity | Different surface, different skill |
| X6 | A "ticket health" passive observer that watches Jira for tickets created outside this skill and scores them against the spine | Useful but invasive; needs cultural buy-in first |

## Summary: how the pattern handles the long tail

The 5 types + universal spine + 14 question categories cover ≈ 90% of the LAP team's typical ticket workload (estimated from the exemplar set, which spans Story/Epic/process/branching/reference-data/single-form). The remaining ≈ 10% — Bugs, Spikes, container Epics, Initiatives, brand-new product lines — are handled by either (a) graceful hand-off to a sister skill or (b) a reduced spine flagged as not-feedable.

Crucially, the skill never refuses to produce SOMETHING. It either produces a uniform feedable ticket, a uniform non-feedable ticket (Bug/Spike/Initiative-summary), or a hand-off message to a sister flow. There is no "I can't help with this."
