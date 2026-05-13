# Voice & Pattern — The Relook Anatomy

> Reverse-engineered from `examples/relook-approval-revamp.md` (the canonical artifact). This is the contract every release note this skill produces must satisfy.

---

## The Five Beats (Always In This Order)

```
1. TITLE              "Release Note: <Feature Name>"
2. THE NEW FLOW       One-line arrow diagram + "Stages in the system" list
3. KEY RULES          Bulleted hard rules with consequences
4. WHAT THIS          One H2 per role with imperative second-person bullets
   MEANS FOR YOU
5. CONTACTS           Named humans + channel fallback
```

If any beat is missing, the release note FAILS. If the order is changed, the release note FAILS. If a beat is added (e.g. an executive summary, a "why we built this" preamble, an FAQ), the release note FAILS.

The order matters. The operator scans top-down and stops reading when they have what they need. The flow line + stages give them the new mental model in 5 seconds. Key rules then load the constraints. Their own role section tells them what to do today. Contacts tell them where to escalate. Everything else is noise.

---

## Beat 1 — Title

**Format**: `Release Note: <Feature Name>`

- Title is plain prose. No version numbers unless the user explicitly asks. No dates.
- The feature name is what the operators will call it in Slack/G-Chat. Match the colloquial name, not the Jira epic title.
  - `Relook Approval Revamp` (✓ — what BCMs call it)
  - `LAP-1445 Send-Back Enhancement` (✗ — Jira-speak)
  - `Approval Process Optimization Initiative v2.1` (✗ — corporate-speak)

---

## Beat 2 — The New Flow

**Two parts** in this exact order:

### Part 2a — One-line arrow diagram

```
BCM raises relook  →  CCM reviews  →  NCM reviews  →  Approved or Reject Queue
```

Rules:
- One line. No multi-line. No mermaid. No markdown table.
- Use `→` (right-arrow). Not `->`, not `>`, not `|`.
- Start with the role/event, not the system.
- End with the terminal outcomes, separated by " or ".
- 6–10 nodes maximum. If you need more, the diagram is too detailed for this beat — abstract upward.

### Part 2b — Stages in the system

A bulleted list. Every stage carries its owner:

```
- Relook CCM Approval Pending  (with CCM)
- Relook NCM Approval Pending  (with NCM)
- Reject Queue  (rejected by CCM or NCM, owner: BCM)
```

Rules:
- Stage name first, then owner annotation in parens.
- Owner annotation can be `(with X)`, `(owner: X)`, or `(rejected by X or Y, owner: Z)` — whatever is most explicit.
- Stage names must match the LSQ panel UI verbatim. Treat them as proper nouns.
- Quote system status names like `'Lost Rejected'` in single quotes when referencing what the operator will see.

---

## Beat 3 — Key Rules

A bulleted list of the new behaviours operators must obey.

**Every rule has a CONSEQUENCE attached.** This is the single most important property of the Relook pattern.

Examples (from the canonical artifact):

> Rejection sends the case to the Reject Queue. **No returns.** The BCM has to raise the approval again.

The rule is "rejection routes to Reject Queue". The consequence is "no returns — BCM re-raises". A rule without a consequence is information; a rule WITH a consequence is operational.

> After 30 days the case will be hard rejected by the system (case status will be 'Lost Rejected') if it is still in any of these three stages: Relook CCM Approval Pending, Relook NCM Approval Pending, or Reject Queue. Once hard rejected, the only option is to ask the SM to repunch the case.

The rule is "30-day SLA". The consequence is "system hard-rejects, status becomes 'Lost Rejected', and the only escape is SM repunch". The operator now knows what happens AND what they can do about it.

Rules:
- 4–8 bullets. If you need more, group them under sub-headings.
- Use **mandatory** / **must** / **only** / **never** for hard rules. These words are load-bearing.
- Quote system strings in `'single quotes'`.
- Name the consequence explicitly. Avoid hedging language ("typically", "in most cases", "may result in").
- New CAM/database fields go here, not in role sections.

---

## Beat 4 — What This Means For You

One H2 per role. Each H2 contains 2–5 imperative second-person bullets.

**Voice rules**:

- Imperative second person. "You are now the first approver." NOT "BCMs will be the first approvers."
- Action verbs at the start of bullets: "Raise", "Open", "Act", "Drop", "Approve", "Forward".
- Tell them what they DO, not what the system does. The system stuff is in Beat 3.
- Edge-case bypasses are spelled out HERE, in the role that uses them.
  - Example: "If the CCM is unavailable, you can view the case and forward the request directly to yourself. This bypasses the CCM bucket and the case lands in your bucket directly. Please use accordingly."

**Role ordering**: in the order they touch the case in the new flow. For Relook: BCMs (raise) → CCMs (first approver) → NCMs (second approver). NOT alphabetical.

**Roles to consider** (in the LAP context):
- Sales: SM, BM
- Credit: BCPA, BCM, CCPA, CCM, SCM, NCM
- Operations: BOM, COM
- Central: NSM, Financier Reviewer, C-BCM, C-BOM, COPs

**Don't include a role section for personas the change doesn't affect.** If the change doesn't change anything for, say, Sales, skip them. The release note is shorter for it.

---

## Beat 5 — Contacts

```
For any issues or clarifications

Please contact product support: <Named Human 1>, <Named Human 2>, … or <Named Human N>.
You can also drop a message in your relevant <channel> for further assistance.
```

Rules:
- Real human first names. The team can decode them. ("Prem, Kiran, Vinesh, Anjali, or Mahesh".)
- Department names are forbidden. ("Contact the credit ops team" is not a contact, it is a black hole.)
- Channel fallback (G-Chat group / WhatsApp / Slack) is named generically — operators know which one.

---

## Voice Rules — Universal

| Do | Don't |
|---|---|
| Imperative second person | Passive voice |
| Short sentences | Compound sentences with three commas |
| Quote system strings in `'single quotes'` | Paraphrase panel labels |
| Name humans | Name departments |
| Attach consequences to rules | Leave rules abstract |
| Use action verbs ("Act within 30 days") | Use vague verbs ("Be aware of the 30-day window") |
| Single document, role-segmented inside | One doc per role |
| Plain English | Corporate-speak, jargon, marketing voice |
| Words that change behaviour | Words that decorate |

---

## Anti-Patterns (Things This Pattern Forbids)

1. **Executive summary at the top** — operators skip it. The flow diagram IS the summary.
2. **"Why we built this" preamble** — operators don't care. They care about what changes.
3. **Confidence tags in the body** — `[H]`, `[VERIFIED]`, `[?]` may be useful in BA artefacts but break readability for operators. Keep them in a hidden footer if needed.
4. **Marketing language** — "Excited to announce", "Improved experience", "Streamlined workflow". All forbidden.
5. **Multi-paragraph rules** — if a rule needs three paragraphs to explain, it's actually three rules.
6. **Numbered lists when bullets work** — bullets carry no priority signal, which is what we want for unordered constraints.
7. **Tables of new fields when bullets work** — tables only for matrix relationships (role × stage). Single-axis info is bullets.
8. **Footnotes** — operators don't follow footnotes. Inline the consequence.

---

## Length Discipline

| Note type | Target word count |
|---|---|
| Single-feature, single-flow change (Relook) | 250–400 words |
| Single-feature, multi-flow change (DigiLocker journey revamp) | 400–600 words |
| Bundled multi-ticket release | 600–900 words |
| Anything over 900 words | Split into multiple notes |

The Relook Approval Revamp release note is **287 words**. That is the gold standard.

---

## Test: Read It Aloud

A field release note passes the voice test if you can read it aloud to a BCM in 90 seconds and they know what to do tomorrow morning. If you trip on a sentence, rewrite it. If a rule sounds vague when spoken, attach a consequence. If a role section sounds like a memo, switch to imperative.

---

## Voice Levels (A and B)

The skill supports two voice levels. Pick one before drafting; do not mix.

| Level | Use for | Sentence length | Vocabulary |
|---|---|---|---|
| **A — Operator-grade dense** | Multi-role main release notes (Workflow Change pattern, Branching Outcome pattern) | 8–15 words | Panel UI strings + role abbreviations + LAP domain terms, all assumed known |
| **B — Field-grade plain** | Single-role one-pagers | 6–12 words; frequent contrast structures ("If yes / If no") | Panel strings verbatim, but everything else in school-level English (Grade 7 target) |

### Voice A — operator-grade dense (current Relook tone)

Reader: BCM/CCM/NCM/BCPA on shift, processing a case.
Imperative second person throughout. No hedging. Quote system strings in `'single quotes'` verbatim.

Example (from `examples/lsq-renach-handling-multi-role.md`):

> Open the Repayment Details subtab on the Repayment & Disbursal Details Capture - v5 form. Selecting Yes on `'Initiate E-Mandate Registration?'` is the only action that triggers the new logic.

### Voice B — field-grade plain

Reader: a role-holder who is new to the team, on probation, or reading the doc after a long shift.
Imperative second person + a touch warmer. Allow phrases like "Better safe than sorry" sparingly. **Bold** the single click / decision word per paragraph. Use frequent "If yes / If no" contrast bullets.

Example (from `examples/lsq-renach-handling-bcpa-pager.md`):

> Go to the case and open: Stage / Tab / Subtab / Form / Dropdown. Click **Yes** on the dropdown. That is your only step. The system does the rest.

### Conversion rules — Voice A → Voice B

When deriving a single-role one-pager from an already-verified multi-role document, apply these seven rules in order:

1. **Split compound sentences.** Anything joined by a semicolon, em-dash, or "and" + clause becomes two sentences.
2. **Drop conditional adverbs.** Remove "typically", "may", "usually", "in most cases". Replace with explicit cases ("Case 1 / Case 2 / Case 3") if they were hedging branching outcomes.
3. **Latinate verbs → Anglo-Saxon.** "Confirm" → "check". "Validate" → "check". "Override" → "change". "Ascertain" → "find out". "Reconcile" → "fix" (or keep if technical term).
4. **Abstract nouns → concrete actions.** "The auto-apply behaviour" → "The system uses the old mandate." "The mandate-eligibility check" → "The system checks if the old mandate fits."
5. **Inline lists in prose → bulleted lists.** "X, Y, and Z" inside a sentence becomes a 3-bullet list.
6. **Add bold on the single click / decision word per paragraph.** Helps the eye find the action.
7. **Add explicit "If yes / If no" contrast bullets** wherever the original used a "depending on whether…" clause.

### Plain-mode anti-patterns (Voice B only)

In Voice B, additionally forbid:

1. **Inline jargon definitions.** If the term needs defining, dedicate a sub-heading to it ("What is Renach?") rather than parenthetical asides.
2. **Triple-nested bullets.** Two levels max. If a third level is creeping in, the case probably needs its own H3.
3. **Conditional connectors at sentence-start.** "However", "Notwithstanding", "Furthermore" are out.
4. **Latinate connectors.** "Subsequently" → "Then". "Prior to" → "Before". "In the event that" → "If".
5. **Passive voice anywhere.** Voice A allows it sparingly; Voice B does not.

### Read-it-aloud test for Voice B

Same as the universal test, but stricter. A single-role one-pager passes Voice B if:
- A new joiner in the role can read it aloud in under 60 seconds.
- They can repeat the "Quick reminder" steps from memory after one read.
- No sentence trips them on first reading.

---

## Voice B-strict — for non-developer field roles (BCPA, BOM, COM, BCM, CCM, NCM, Sales)

A second-tier discipline applies when the single-role pager is for a non-developer field role. These readers consume the doc on a phone in WhatsApp, between cases, often with one hand on a keyboard. They do not work with JSON, API responses, callback payloads, or panel data fields. They work with **scenarios**.

Use Voice B-strict when the single-role pager target is BCPA, BOM, COM, BCM, CCM, NCM, SM, BM, or any other field-grade operator who is not a developer or a product-support technician.

### What Voice B-strict drops on top of Voice B

In addition to the seven Voice A → Voice B conversion rules:

1. **No data field references at all.** No `enach_reference_number`, no `mandate_amount`, no `'status' = APPROVED`, no JSON keys, no callback payloads. Even quoted in single-quotes — drop them.
2. **No backend conditions in formula form.** Replace `Sanction Loan amount ≤ 'mandate_amount'` with "the new loan fits inside the old e-mandate." Replace `Last EMI date + 5 years ≤ 'mandate_expiry_date'` with "the old e-mandate has enough time left to cover all EMIs."
3. **No mention of the API surface.** No "Push to LMS API request body", no "callback fired", no "request validated". Replace with "the case moves forward" / "the case gets stuck" / "the system sends".
4. **No verification checklists keyed to fields.** Replace "check that these five fields are populated" with "you don't have to check anything — the system uses the old e-mandate on its own" or "if the case moves forward to the next step, you know it worked."
5. **No buffer policy / timing arithmetic in the body.** "5-year buffer" / "4-year buffer" / "tenure + 4 years" stays out of the operator's pager. The system applies these rules; the operator does not. If the reader needs to know why a link appeared, give the cause in plain English ("the new loan is bigger than the old mandate covers, or the old mandate is going to expire too soon").
6. **Trust-the-system framing.** Where Voice A says "the system evaluates conditions in the backend; the BCPA cannot override", Voice B-strict says "the system decides on its own. You don't have to check anything." Same content, very different reader experience.

### What Voice B-strict keeps

- **UI labels the operator literally clicks.** Stage names, tab names, subtab names, dropdown labels, button labels. These are navigation, not data — the operator must see them on screen verbatim. Format with **bold** or `"double quotes"` (whichever the panel uses; bold is fine for label text).
- **Plain-English causes for branches.** When the system shows a link instead of re-using the old mandate, say *why* in plain words ("the new loan is bigger", "the old e-mandate is going to expire too soon"). The operator does not need to know the formula; they may want to know what the customer-facing reason looks like.
- **Scenario-first structure.** One H2 per scenario (Scenario 1, Scenario 2, Scenario 3). Each scenario opens with a one-line characterisation of the customer ("Brand new customer", "Old e-mandate is good for this loan", "Old e-mandate doesn't work for this loan") then the operator's actions.
- **Auto-action + manual backup pattern.** Wherever an SMS / email / notification fires, pair it with "Also send manually as a backup." This is universal in Voice B and survives intact in B-strict.
- **Non-overridable rule in plain English.** "Do not try to fix it from the panel — there is nothing you can change from your end." Replaces the technical "the BCPA cannot override the decision from the panel."

### Anti-patterns specific to Voice B-strict (additional to Voice B's)

1. **Backend logic in disguise.** "If the loan amount divided by the mandate amount exceeds 1, send the link" is a formula. Drop it. Use "if the new loan is bigger than the old mandate covers".
2. **Field-name name-dropping.** Even mentioning a field once "for context" is too much. The reader will stop reading.
3. **Verification-by-fields language.** Anything that asks the operator to "check that field X is populated" / "confirm the callback shows status = APPROVED" / "validate the reference number". Replace with "you don't have to check anything" or "the case will move forward on its own".
4. **API / system-architecture language.** "Push to LMS", "request body", "callback", "endpoint", "session ID". All out.

### When Voice B is enough vs when B-strict is required

| Reader | Voice |
|---|---|
| Product support / Tech ops / QA / SRE | B (single-quoted field references are fine — they look at panels and dashboards) |
| Field operator (BCPA / BOM / COM / BCM / CCM / NCM / Sales) | **B-strict** (no field references; scenarios only) |
| New joiner on probation in any field role | **B-strict** (regardless of role seniority elsewhere) |

Default for single-role pagers targeting any role in `lap-roles.md` Sales / Credit / Operations sections: **B-strict**.

Canonical artifact in B-strict: `examples/lsq-renach-handling-bcpa-pager.md` (rewritten 2026-05-04 from reviewer feedback "scenarios in plain English without mention of any fields etc").
