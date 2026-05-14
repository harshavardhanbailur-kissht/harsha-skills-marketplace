# 06 — Output Gating

## The validation checklist (Phase 7)

Every check is binary (pass / fail). Every fail has a defined **loop-back target** — the phase the skill returns to in order to fix the issue. The skill does NOT ship with warnings; if a check fails, it loops. Maximum 3 validation iterations; after that, the skill flags the residual issue to the PM and asks for an explicit override.

The checklist is divided into **universal** (every ticket type), **type-specific** (per detected type), and **destination-specific** (markdown vs. Jira) groups.

## Universal checks (all 5 types)

| # | Check | Loop-back target if failed |
|---|---|---|
| U1 | Title is non-empty and follows `<Area> — <One-line action>` (e.g., "LAP <> LSQ : E-Sign LAP documents - Phase 2") | Phase 5 |
| U2 | Intent paragraph exists, ≤ 3 sentences, names the change verb + the why | Phase 4 A |
| U3 | Every numbered rule in the Proposed solution carries a CONSEQUENCE (the word "if/then/so/because" or equivalent must appear in the same bullet OR an immediate follow-on bullet) | Phase 4 E or Phase 5 |
| U4 | Every named stage appears in the canonical glossary OR is documented in the Role Definitions / Glossary extension footer | Phase 4 D |
| U5 | Every role acronym in the body either appears in lap-roles.md OR has a definition in the Role Definitions appendix | Phase 4 D |
| U6 | All UI / system strings appear in `'single quotes'` exactly as on the panel — no paraphrasing | Phase 4 D |
| U7 | No JSON blobs, no pseudocode, no SQL, no API request bodies in the body. (Sample request bodies belong in Confluence; the ticket links to them.) | Phase 5 |
| U8 | AC block has ≤ 5 bullets per area; total AC ≤ 15 bullets across all areas | Phase 4 L |
| U9 | AC bullets do NOT verbatim-restate Proposed-solution rules (caught by Phase 6 dedup; this is a re-check) | Phase 6 |
| U10 | QA Scope block exists and has ≥ 3 bullets | Phase 4 J |
| U11 | BA Scope / Open Considerations block exists with at least 1 item OR an explicit "no open BA items for this ticket" line | Phase 4 K |
| U12 | Sources section exists at the bottom (links, sheets, prototypes, parent epic, bug fan-out OR explicit "none") | Phase 4 M |
| U13 | Contacts (reporter / assignee / sponsors) are humans, not departments | Phase 4 N |
| U14 | Word count is within type-band: WC 800-2500, BO 600-1800, MX 1000-2800, RD 400-1500, SF 600-1500 | Phase 5 (re-tighten) |
| U15 | No marketing voice ("we are excited," "improved experience," "delight users," "world-class") | Phase 5 |
| U16 | No hedging language ("could potentially," "should mostly," "may help") in the Proposed solution | Phase 5 |

## Type-specific checks

### WC (Workflow Change)

| # | Check | Loop-back target |
|---|---|---|
| WC1 | Primary Actor + Secondary Actors block exists | Phase 4 C |
| WC2 | Preconditions block exists and lists ≥ 1 precondition | Phase 4 B |
| WC3 | Functional Flow is numbered with sub-steps (1.1 / 1.2 / 1.3 etc.) when any top-level step has more than 2 paragraphs | Phase 5 |
| WC4 | Drop-off / resume logic is explicitly handled OR explicitly out-of-scope | Phase 4 E |
| WC5 | Expiry handling is explicitly addressed OR explicitly out-of-scope | Phase 4 E |
| WC6 | AC is **organised by area** (Document Generation / Consent / Signing / etc.), not flat | Phase 4 L2 |
| WC7 | Every named new stage has an owner role | Phase 4 D / Phase 5 |
| WC8 | Every SLA mentioned has a unit (hours / days) and a breach behaviour | Phase 4 E |

### BO (Branching Outcome)

| # | Check | Loop-back target |
|---|---|---|
| BO1 | At least 2 Cases exist, each with the See / Do / Verify triplet | Phase 4 E |
| BO2 | Each Case has a name (Case 1: descriptor, Case 2: descriptor) — not just "Case 1 / Case 2 / Case 3" | Phase 5 |
| BO3 | Summary table exists OR ticket has ≤ 2 Cases | Phase 4 F |
| BO4 | Auto-comm Cases are paired with manual-backup instruction | Phase 4 G2 |
| BO5 | Silent-action Cases have an explicit "you don't have to verify, the system handles it" note OR a verification mechanism named | Phase 4 H |
| BO6 | Non-overridable rules explicitly named ("you cannot change this from the panel") with escalation path | Phase 4 I |
| BO7 | NO new stage introduced (otherwise the type should have been MX) | Phase 3 — re-detect |

### MX (Mixed)

All WC checks PLUS all BO checks, with one exception: BO7 is inverted — MX MUST have ≥ 1 new stage AND ≥ 2 branches inside one stage.

| MX1 | Exactly one stage in the Functional Flow has embedded Case 1 / Case 2 sub-blocks (multiple branching stages → split into two tickets) | Phase 3 — review scope, possibly split |

### RD (Reference-data)

| # | Check | Loop-back target |
|---|---|---|
| RD1 | A matrix table OR per-system bulleted breakdown exists | Phase 4 F |
| RD2 | Every dropdown value enumerated matches the source-of-truth sheet (link present in Sources) | Phase 4 D / Phase 4 M |
| RD3 | Every touchpoint stage where the values appear is named | Phase 4 C |
| RD4 | NO Current flow block (the flow doesn't change) — if present, removed | Phase 5 |
| RD5 | NO Cases / See-Do-Verify (no operator decision) — if present, ticket should be re-typed | Phase 3 |
| RD6 | Role Definitions appendix exists when role acronyms appear in matrix | Phase 4 D |

### SF (Single-form)

| # | Check | Loop-back target |
|---|---|---|
| SF1 | Problem statement is ≤ 2 paragraphs | Phase 4 A |
| SF2 | "Current flow that we want to fix" block is numbered with ≥ 3 steps when there is a meaningful current flow (≥ 2 PM-described pain steps) | Phase 4 B |
| SF3 | Proposed solution is numbered with consequences in each step | Phase 4 E |
| SF4 | Bidirectional behaviour (e.g., Yes → No AND No → Yes) is explicitly handled when the ticket touches a toggle / switch | Phase 4 E |
| SF5 | State-refresh check appears in QA Scope (real-time vs. logout vs. stage re-entry) | Phase 4 J4 |
| SF6 | Primary-applicant vs. co-applicant distinction explicitly addressed in BA Scope | Phase 4 K2 |

## Destination-specific checks

### Markdown destination

| MD1 | File path is set and writable | Phase 8 |
| MD2 | File doesn't already exist (or PM confirmed overwrite) | Phase 8 |
| MD3 | Markdown renders without table-syntax errors (every `|` row has matching cells) | Phase 5 |

### Jira destination (push via editJiraIssue or createJiraIssue)

| JR1 | Ticket key is reserved (createJiraIssue stub returned a key in Phase 0) OR existing ticket key is valid | Phase 0 |
| JR2 | Markdown body converts cleanly to Atlassian Document Format (ADF) — no nested tables, no >3-level lists, no inline HTML | Phase 5 |
| JR3 | Issue type matches the detected type's allowed Jira type (Story / Epic / Task — not Bug, Sub-task) | Phase 0 |
| JR4 | All required Jira custom fields populated (per project schema — sprint, fix version, etc., if mandatory) | Phase 0 / Phase 4 |
| JR5 | Reporter and Assignee resolve to valid Jira accountIds | Phase 4 N |
| JR6 | Linked issues block (parent epic, related tickets, bug fan-out from Phase 1) is included as Jira issue links, not just text mentions | Phase 8 |

## Loop-back behaviour

When a check fails:

1. The skill announces: "Validation failed: [check #]: [check name]. Looping back to [target phase] to fix."
2. The skill jumps to the target phase with a focused prompt — NOT a full phase replay. E.g., for U3 (rule missing consequence), the prompt is: "Step 4 of your Proposed solution doesn't carry a consequence. The current text is: '___'. What's the consequence — what happens if this rule fires?"
3. The PM provides the missing piece. The skill incorporates it. Phase 5 re-renders.
4. Re-run validation.

After 3 iterations on the same check, the skill flags it: "I've looped 3 times on [check]. I'll ship with this gap, marked in the ticket as `[BA TODO: ___]`. Confirm?" — PM confirms or re-engages.

## What the skill does NOT loop on

Some checks are warnings, not gates. The skill notes them but doesn't loop:

- **Word count just over band** (e.g., 1550 for an SF, when band is 600-1500) — flagged in `VALIDATION.md`, but ticket ships if PM confirms.
- **Hedging language in the Intent paragraph** (the Intent is allowed slight softness — "this addresses the friction where ___" is fine, even though it would fail in §3).
- **Sources section has only the parent epic and no external link** — flagged but ships.

These are documented in `VALIDATION.md` so the PM sees what was let through.

## What the skill REFUSES to ship under any condition

Three failures are unrecoverable — they do NOT loop, they do NOT warn — they hard-stop:

1. **Empty Intent paragraph** — without intent, the release-notes skill cannot frame the change. Hard stop until A1 + A2 are answered.
2. **Empty Proposed solution** — without proposed change, there is no ticket. Hard stop.
3. **No type detected after both Phase 3 passes AND PM declined to override to a default** — hard stop, asking PM to expand the intent.

These three are the irreducible minimum for a Jira ticket to exist at all.

## Validation summary in `VALIDATION.md`

After Phase 7 completes, `VALIDATION.md` looks like:

```
## Universal checks
[x] U1 Title format
[x] U2 Intent paragraph
[x] U3 Consequences attached
... etc.

## Type-specific checks (SF)
[x] SF1 Problem statement length
[x] SF2 Current flow numbered
[!] SF4 Bidirectional behaviour — initially missing, fixed in iteration 2 (Yes→No→Yes test added to QA Scope J3)
... etc.

## Destination checks (Jira)
[x] JR1 Ticket key reserved (LAP-2351)
[x] JR2 ADF conversion clean
... etc.

## Warnings (non-blocking)
- Word count 1620, type band 600-1500. PM confirmed (clarity demands it).

## Iteration count: 2 / 3 max
## Result: PASS — ready for delivery
```

This file is part of the session archive and is what a future session (or a colleague) reads to understand what the skill validated and what it let through.
