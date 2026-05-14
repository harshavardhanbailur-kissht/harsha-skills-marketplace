# VOICE AND STYLE

The voice rules that prevent LLM-written ticket smell. If the skill writes in marketing voice, the skill is dead on arrival. If a PM writes in marketing voice, the skill rewrites it.

For section structure, see `PATTERN.md`. For the principles behind each rule, see `PRINCIPLES.md`.

---

## Plain English principle

Write the way a senior LAP PM writes after she has filed her 200th ticket. Short sentences. Active voice. Second-person for instructions ("BCM clicks Mark as Complete" — not "the user is required to click"). No hedges. No throat-clearing. No "we believe this should help."

The four rules:

1. **Short sentences.** Most under 20 words. Long sentences earn their length by carrying a single idea that cannot be split.
2. **Active voice.** "The system routes the case to NCM." Not "The case will be routed by the system." Passive is allowed only when the actor is genuinely unknown or unimportant.
3. **Second-person for operator instructions.** "BCM opens the activity. BCM fills the form." Not "The user opens..." or "One should open..." Name the role.
4. **No marketing voice.** Forbidden: "we believe", "this should help", "this aims to", "we are introducing", "exciting new", "innovative", "robust", "seamless", "leverage", "enable", "facilitate", "in order to", "going forward". Each of these is a tell that the writer has not committed to a concrete claim.

The smell test: read the paragraph aloud. If you sound like a vendor brochure, rewrite.

---

## No pseudocode

The audience is a BCM at 9am, not an engineer at code review.

**Forbidden:**

- Code blocks longer than five lines.
- JSON schemas.
- SQL.
- Function signatures.
- API endpoint specifications with request / response bodies.
- Database table schemas.
- Regex patterns longer than one inline phrase.

**Allowed:**

- Inline `'system_string'` quoting (single quotes, verbatim from the UI).
- Matrix tables (slab / approver / fallback — see LAP-2242).
- Per-system breakdown lists (Leadgen / LOS / SARAL — see LAP-2052).
- One-line inline references to a config key when no other shorthand exists (`feature_flag.income_considered_top = true`).

If the ticket genuinely cannot be expressed without pseudocode, the ticket is for the wrong audience. Split it: a PM ticket and a separate engineering spec.

---

## No repetition discipline

The body says it once. If you find yourself restating, the structure is wrong.

The discipline is built into the spine. Each section in `PATTERN.md` has one job. If you write the rule "system routes to NCM" in §6 Proposed Solution and again in §16 AC, one of those is wrong — and per the dedup rule, AC is wrong because AC is the observable outcome, not the rule.

The skill's Phase 6 dedup pass catches:

- Intent paragraph restating Proposed Solution step 1 (DELETE the Intent restatement).
- AC bullet restating Proposed Solution rule (DELETE the AC bullet, replace with observable outcome).
- Current Flow describing an action that is unchanged in Proposed Solution (DELETE the Proposed Solution mention).
- System string echoed three or more times (TRANSFORM — first mention quotes, rest reference by name).
- Out-of-scope hedge in Intent paragraph (DELETE the Intent hedge, keep `Out of scope`).

If the dedup pass cannot decide, it asks. But almost always, the answer is delete.

---

## Numbered sections with consequences

Every Logic rule, every Proposed Solution step, names what the system does in response.

A rule without a consequence is half a rule. "The system identifies the slab." → so what? Did it route? Did it log? Did it gate the next step? Names the system action.

Compare:

- BAD: "5. Configurable matrix."
- GOOD: "5. The matrix should be configurable — business / ops should be able to update slab thresholds, approver roles, and default fallbacks through a config screen without a code deploy."

The good version names what the consequence is: ops can change config without engineering. The bad version is a noun, not a rule.

LAP-2242's 10-rule Logic section is the model. Read it. Every rule names a trigger and a consequence.

---

## System strings discipline

Every panel label, dropdown value, status name, button label, error message, and SMS body that appears in the UI gets quoted verbatim. Single quotes. Exact case. Exact punctuation.

Why: the release-notes skill extracts these strings into the Cheat-sheet block of the field release note. The BCM searches for `'Approval Pending'` in the LAP UI and finds it because we typed it exactly. If we typed `'Approval pending'` (lowercase p) and the UI says `'Approval Pending'`, the BCM does not find it.

Three rules:

1. **First mention quotes verbatim.** `'Mark as Complete'`, `'Income Considered'`, `'Final Sanction Pending'`, `'Renach'`.
2. **Subsequent mentions reference by quoted name without re-quoting** if the same exact string appears three or more times. "After the BCM clicks Mark as Complete (`'Mark as Complete'`), the form... When Mark as Complete fires again..."
3. **Old → New rename pairs always go in a table.** Old quoted, new quoted, side by side.

For SMS / email / notification bodies, paste the entire template including `{{variable}}` placeholders, exactly as it sits in the system. LAP-1812's SMS string is the canonical example: *"Dear [Customer Name], your loan is approved. Please click on the link [Link] to review and complete your secure e-signing of your loan documents. Do not share your OTP with anyone." Team Si Creva*.

---

## Ghost-term handling

A ghost term is any LAP-domain noun that appears in the ticket and is NOT in the canonical glossary OR defined inline at first use.

Examples of ghost terms: `'Renach'`, `'NIC tab'`, `'Saral journey'`, `'Third Party Trigger Pending'`, `'CCM'`, `'BCPA'`.

The rule:

1. The skill loads the glossary at session start.
2. If a term in your answer matches the glossary, the skill is silent.
3. If a term is a near-match (e.g., "SARAL" vs "Saral"), the skill silently normalises to canonical.
4. If a term is unknown, the skill asks: "I don't have `<term>` in the glossary. Is this a new acronym? Give me a one-line definition." The answer goes into `LOCAL_GLOSSARY.md` and into the ticket footer.

Ghost terms BLOCK the draft. The skill will not let you ship a ticket with `'XYZ stage'` undefined. The footer is then complete: every named role, stage, and string traceable to a definition.

---

## Voice anti-patterns gallery

Seven before-and-after pairs. Read them. Internalise them.

### 1. Marketing voice → Concrete voice

- BAD: "We are introducing a new approval workflow that should improve efficiency for our credit team."
- GOOD: "CCM now approves loans up to 7L; SCH approves 7L to 10L; NCM approves 10L+."

### 2. Hedging → Decisive

- BAD: "It is suggested that the system might route the case to NCM in cases where SCH is not available."
- GOOD: "If SCH is unavailable, the system routes the case to NCM."

### 3. Passive abstraction → Named operator

- BAD: "The form is filled out and submitted by the user."
- GOOD: "BCM fills every income field on the form. BCM clicks Mark as Complete."

### 4. Bloated AC restating the body → Lean AC stating the gate

- BAD AC: "The system should validate that income is greater than 0 before allowing the form to be submitted, and if income is 0 or negative, the form should display an error message and prevent submission."
- GOOD AC: "Form rejects income ≤ 0 with the inline error `'Income must be greater than 0'`."

### 5. Pseudocode pretending to be a rule → Plain rule

- BAD: "`if (case.amount > 700000 && approver.role != 'CCM') { route_to('SCH'); }`"
- GOOD: "For loan amounts above 7L, the case routes to SCH (CCM does not have approval rights above 7L)."

### 6. Ghost term → Defined or referenced

- BAD: "The case moves to Renach if the DOB doesn't match."
- GOOD: "The case moves to Renach (`'Renach'` = the LAP-internal status for cases sent back to the operator for re-fill, see glossary) if the DOB doesn't match the bureau record."

### 7. Restated outcome → Single canonical mention

- BAD (Intent): "This ticket adds a new approval stage for cases over 7L." (Proposed step 1): "Add a new approval stage that triggers for cases over 7L."
- GOOD (Intent): "Cases over 7L now require an extra approval at the SCH level before disbursal." (Proposed step 1): "When a case crosses 7L at IPA, the system routes it to SCH instead of completing IPA at CCM."

The Intent paragraph names what + why. The Proposed step names how. They never overlap.

---

## Honor the LAP exemplars' voice

These three exemplars are the voice reference. Quote them when training new PMs.

### LAP-2039 (SC, gold)

Two lines worth memorising:

> *"This forces the BCM to fill a lot of irrelevant fields and then come back to edit the same activity just to flip one toggle. It wastes time and adds extra steps that have no business value."*

> *"Items where BA needs to confirm an assumption or close a gap: 1. Primary applicant scope. The Credit PD activity is also generated for the primary applicant with default Yes. Allowing the BCM to set No on the primary applicant would break eligibility because LAP relies on the applicant's own income. Proposal: keep the Income Considered field visible on the primary applicant's form but lock it to Yes with no option to switch. Impact: protects eligibility calculation and prevents accidental sanction breakage."*

What to internalise: pain is named in operator-cost terms ("wastes time", "no business value"). Open Consideration uses the canonical assumption + proposal + impact format with bold lead-in.

### LAP-2242 (RD, 10-rule Logic)

> *"Fallback logic: If no active user is mapped to the designated approver role for the applicable case (e.g., role is vacant, user is inactive, user is on leave with no delegate set, or no user exists for that role at the applicable branch / region), the case should automatically route to the Default Approver for that slab."*

> *"Approver unavailability is simulated in UAT by inactivating the user at the relevant role / hierarchy level and submitting IPA or FA."*

What to internalise: every rule names the trigger conditions concretely (vacant, inactive, on leave with no delegate, no user at branch/region) AND the consequence. The QA note tells you exactly how to simulate the hard-to-trigger case.

### LAP-2052 (RD, per-system breakdown)

> *"The idea is to make the list of the Property Document (type of ownership document) and Property Type (property occupancy status) to be same across LSQ."*

> *"Document replacement functionality for 'Type of ownership document / Property Document' should be provided at Document Upload and cleanup tab at Post sanction stage with proper name as per the dropdown list for new and current values. Also selection of the dropdown values will remain freezed."*

What to internalise: the Intent paragraph is one sentence and complete. The body names the touchpoint (`Document Upload and cleanup tab`), the stage (`Post sanction`), and the resulting behaviour (`selection... will remain freezed`). No hedge. No throat-clearing.

---

## When the skill rewrites you

The skill will, at draft time:

- Strip "we believe" / "this should help" / "going forward" automatically.
- Convert passive constructions to active where the actor is named.
- Surface ghost terms as questions before the body is drafted.
- Quote system strings in single quotes; flag unquoted UI strings for confirmation.
- Collapse Intent ↔ Proposed Solution restatements (DELETE the Intent restatement).
- Trim AC bullets that re-list Proposed Solution rules.

You can override any of these. The skill will mark the override in the dedup log so the team can learn from it.

The voice rules in this file are not stylistic preferences. They are the operator-grade constraints that keep the LAP ticket pipeline working.
