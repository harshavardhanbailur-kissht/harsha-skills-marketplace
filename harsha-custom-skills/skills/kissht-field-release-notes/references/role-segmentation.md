# Role Segmentation — "What This Means For You" Patterns

> The fourth beat of every release note ("What this means for you") is the operationally most critical. Operators read THEIR role section and skim the rest. This file documents the patterns each role section should follow.

---

## The Universal Rule

Each role section is **one H2** + **2–5 imperative second-person bullets** + (optional) **one edge-case bypass paragraph**.

```markdown
## <RoleAbbreviation>s

- <Imperative verb> <object> <constraint>.
- <Imperative verb> <object> <constraint>.
- <Edge case>: <bypass description>.
```

Bullets must:
- Start with an action verb in imperative mood.
- Tell the operator what THEY do, not what the system does.
- Reference the new flow / new stages by name (use stage names in `'single quotes'`).
- Carry the constraint (deadline, mandatory field, gating requirement) inline.

Bullets must NOT:
- Be passive ("rejection notes will be required" → use "Rejection note is mandatory").
- Be hedged ("you may want to act quickly" → use "Act within 30 days").
- Restate Beat 3 rules verbatim. The role section should LOCALIZE the rule to the persona.

---

## Role Ordering

Order roles by **who touches the case first in the new flow**. Not alphabetical. Not by hierarchy.

For Relook Approval Revamp:
- BCMs (raise the relook) → CCMs (first approver) → NCMs (second approver). ✓
- NCMs → CCMs → BCMs (alphabetical-ish). ✗
- BCMs → NCMs → CCMs (random). ✗

For DigiLocker Journey Revamp:
- Sales (sets expectation with applicants) → BCMs (case-level effects) → CCPA (panel-level new fields). ✓

If two roles touch the case simultaneously, ordering them by criticality of their action is acceptable.

---

## Per-Role Patterns (LAP)

Use these as starting templates. Adapt to the feature.

### BCM (Branch Credit Manager)

What BCMs always need to know:
- What new action they can take (raise, edit, flip a flag).
- Where to find new info (which tab, which form).
- What the SLA is and what hard-rejects them.
- What the failure mode is (Reject Queue, hard reject, send-back).

Template snippets:
- "Raise X directly in the system. They route to Y automatically."
- "Open the <Tab Name> tab in <Stage Name> to read <doc/comment>."
- "If a case lands in the Reject Queue, act quickly. Get the case approved within <N> days."
- "In case of hard reject (case status will be `'<system string>'`), the only option is to <action>."

### CCM / SCM (Cluster / State Credit Manager)

What CCMs always need to know:
- Are they newly inserted into the flow, or skipped?
- What's their bucket name now?
- What the rejection comment / approval-comment requirement is.
- What the SLA is.

Template snippets:
- "You are now the <first / second / third> approver on every <feature>."
- "Act within <N> days. Inaction will hard reject the case."
- "Rejection note is mandatory. Approving sends the case to <next role>. Rejecting sends it to <next stage>."

### NCM (National Credit Manager)

What NCMs always need to know:
- Are they still the final approver, or has the final approver changed?
- What the bypass / shortcut to NCM looks like.
- What approval / rejection comment rules apply.

Template snippets:
- "You are now the <Nth> approver. Cases reach you only after <prior approval>."
- "If the <prior role> is unavailable, you can view the case and forward the request directly to yourself. This bypasses the <prior bucket> and the case lands in your bucket directly."

### CCPA (Central Credit Processing Associate)

What CCPAs always need to know:
- New fields on the panel (Submit App Check, CAM fields, KYC flag display).
- New checklist items added or removed.
- Saral vs Normal split — does this change behave differently?
- New validations on submit.

Template snippets:
- "New fields on the <Tab Name> tab: `<Field 1>`, `<Field 2>`."
- "<Validation> is now blocking on submit. The form will not let you proceed if <condition>."
- "For Saral cases, this means <Saral-specific delta>. For all others, no change."

### BCPA (Branch Credit Processing Associate)

What BCPAs always need to know:
- Vendor handoff changes (Legal/Technical/RCU/FI).
- Send-back categories that affect them.
- Pre-trigger requirements at Third Party Trigger Pending.

Template snippets:
- "Pre-trigger <Legal / Technical / RCU / FI> at <Stage> to compress TAT."
- "Send-Backs from <Final Sanction Pending> with category `<Category>` will land in your bucket. Recommendation activity stays / is deleted accordingly."

### Sales (SM, BM, NSM)

What Sales always need to know:
- New gating requirements that block their submission.
- New customer-side requirements they must set expectations on (e.g. "all applicants must complete DigiLocker — no skip").
- Communications they receive (e.g. "Move to Credit" SMS, panel notifications).

Template snippets:
- "Set the customer's expectation early: <new mandatory step> applies to all applicants AND co-applicants — no skip."
- "<Stage> cannot be submitted until <gating condition>. Cases that hit this gate will sit at <Stage> until <action>."
- "You will see a new <notification / SMS / panel alert> when <event>. Action: <what to do>."

### Operations (BOM, COM, C-BOM, COPs)

What Ops always need to know:
- New ops handoff conditions.
- Disbursement kit / NACH / mortgage creation deltas.
- New send-back categories that route to them.

Template snippets:
- "Disbursement Kit Released cases now require <new artefact>. Without it, kit cannot be closed."
- "Cases at <Stage> that fail <validation> will route to your bucket. Resolution is via <action>."

---

## Edge Cases & Bypasses

Always include the bypass in the role section that uses it — not as a footnote. Operators won't follow footnotes.

Format:

> If the <other role> is unavailable, you can <action>. This <effect>. <When to use>.

Example (from Relook Approval Revamp):

> If the CCM is unavailable, you can view the case and forward the request directly to yourself. This bypasses the CCM bucket and the case lands in your bucket directly. Please use accordingly.

Three sentences. Edge case named, action stated, when-to-use guidance given.

---

## Length Per Role Section

| Section length | When to use |
|---|---|
| 2 bullets | Role behaviour barely changes (e.g. just a new validation) |
| 3 bullets | Standard — one new action, one new constraint, one heads-up |
| 4–5 bullets + optional bypass | Role gains a new responsibility or bucket |
| > 5 bullets | The role changed too much for one section. Split the feature into multiple release notes, OR reconsider whether you're collapsing too much. |

---

## When To Skip A Role Entirely

If the change has zero behavioural impact on a persona, **skip them**. Do not write "BCMs: no impact" — operators will read that and waste 5 seconds confirming it doesn't apply to them.

The Relook Approval Revamp release note has only THREE role sections (BCMs, CCMs, NCMs). Sales / Ops are not mentioned because their behaviour didn't change. That's correct.

---

## Anti-Patterns (Things Role Sections Must Not Do)

1. **Restating Beat 3 rules**. The rule is in Beat 3 ("rejection comment is mandatory"). The role section says what the operator DOES because of the rule ("write a rejection note when you reject — without it, you cannot submit").
2. **Cross-referencing other role sections**. Each role section is self-contained. ("CCMs see the comments BCMs left earlier" → ✗; "Open the Approval tab to read CCM and NCM rejection comments" → ✓.)
3. **Talking about future work or backlog**. Future tickets / "coming soon" go in a separate "What's next" beat (which the Relook pattern doesn't use). Do not pollute role sections with non-shipped behaviour.
4. **Talking to "the team"**. The release note is addressed to the operator. "Your team" is fine. "The team" is not.
5. **Listing every new field**. New CAM fields go in Beat 3 (Key rules). The role section says how to USE them.

---

## Test: The 9am Test

For each role section, imagine the operator reading it at 9am with one coffee and three open cases on their panel. They should be able to:

1. Identify their section in <3 seconds.
2. Read it in <30 seconds.
3. Open the first case on their panel and act differently than they did yesterday.

If the section fails any of these — too long, too vague, too generic, too systems-level — rewrite it.
