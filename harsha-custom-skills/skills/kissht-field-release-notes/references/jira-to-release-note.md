# Jira → Release Note Mapping

> How to translate a Jira ticket (or a bundle) into the five beats of the release note.

---

## Step 0 — Should This Ticket Get A Release Note At All?

A ticket warrants a field release note ONLY IF the change is visible to a human operator at the panel / SOP / customer-facing level.

Use this filter:

| Ticket type | Field release note? |
|---|---|
| New stage added to LSQ panel | ✓ Yes |
| New mandatory field on a form | ✓ Yes |
| New rule that gates a submission | ✓ Yes |
| New SLA / timer with a hard-reject consequence | ✓ Yes |
| New role inserted into approval chain | ✓ Yes |
| New customer-facing requirement (e.g. mandatory KYC step) | ✓ Yes |
| New CAM field visible to credit users | ✓ Yes |
| Existing flag's display label changed | ✓ Yes (small note) |
| Bug fix where a validation was firing wrongly | ✗ No (operator behaviour doesn't change) |
| Backend refactor / data migration / hygiene | ✗ No |
| Integration / API contract change | ✗ No (unless it changes panel behaviour) |
| Performance optimisation | ✗ No |
| Internal logging / monitoring | ✗ No |

If you're unsure, ask: **"What does the BCM / CCM / Sales RM do differently tomorrow because this shipped?"** If the answer is "nothing", skip it.

---

## Step 1 — Pull The Source

Use the Atlassian MCP:

```
getJiraIssue(
  cloudId: 76a6058f-c3ec-4764-8c15-e7d4a3e8aae2,
  issueIdOrKey: "LAP-XXXX",
  fields: ["summary", "description", "status", "issuetype", "priority",
           "resolutiondate", "labels", "components", "fixVersions",
           "assignee", "reporter", "parent"],
  responseContentFormat: "markdown"
)
```

For multi-ticket bundles, fetch each ticket in parallel.

---

## Step 2 — Decompose Into Beat-Level Material

Map Jira fields to release-note beats. Use this checklist per ticket:

### → Beat 1: Title

| Source | How to use |
|---|---|
| `summary` | Strip Jira-isms ("LAP <> LSQ - …") and convert to colloquial feature name. "LAP <> LSQ - Changes in Digilocker flow (Client Side)" → "DigiLocker Journey Revamp" |
| `parent.summary` | If the parent epic has a more colloquial name, use it. Often the epic title IS the feature name. |
| `labels` | Look for `release_name:*` or similar custom labels — sometimes ops/PMs leave the colloquial name there. |

### → Beat 2: The new flow

| Source | How to use |
|---|---|
| `description` (sections labelled "Flow", "Journey", "Sequence") | Extract the step-by-step. Compress to 6-10 nodes. Convert to one-line arrow diagram. |
| `description` mentions of stage names | Cross-reference with `lap-glossary.md`. Write each new/affected stage with owner annotation. |
| Multiple tickets | Reconcile: pick the most authoritative description; flag contradictions. |

If the Jira ticket doesn't describe the flow explicitly, derive it from the new stages introduced + the role chain.

### → Beat 3: Key rules

| Source | How to use |
|---|---|
| `description` numbered/bulleted requirements | Each requirement is a candidate rule. |
| Phrases like "must be", "mandatory", "should not", "no skip", "block" | Hard rules. Always make it into Beat 3. |
| Phrases like "if X then Y", "when X happens, Y" | Pre-formed consequences. Use the language directly. |
| New fields named in `description` | New CAM/database fields go here, not in role sections. |
| SLAs / timers / deadlines | Always include with consequence. |
| API response flags or error messages | Quote verbatim. They are panel UI strings. |

For each rule extracted, ASK: "What is the consequence if the operator violates this?" If you can't answer it, the rule is incomplete — go back to the ticket or ask the reporter / assignee.

### → Beat 4: What this means for you

| Source | How to use |
|---|---|
| `description` "User must …" / "<role> should …" | Direct mapping to imperative bullets. |
| `description` mentions specific roles (BCM, CCM, CCPA, Sales) | Group bullets under those roles' H2s. |
| `description` edge cases ("if X is unavailable, then …") | Place under the role that uses the bypass. |
| Multiple tickets affecting same role | Consolidate bullets under one role section. |

If a ticket describes only system behaviour with no role-specific action, you have a problem: the ticket is light on operator detail. Either pull more context from Confluence or escalate to the reporter.

### → Beat 5: Contacts

| Source | How to use |
|---|---|
| `reporter.displayName` | Almost always the PM. Use first name. |
| `assignee.displayName` | The dev. Sometimes useful as an escalation. |
| Mentions in `description` (`@<name>`) | Often other relevant humans. |
| `parent` epic's reporter | If the epic has a different PM than the story, list both. |

For multi-ticket bundles, list the unique reporters. If they're the same, just list them once.

---

## Step 3 — Multi-Ticket Bundling

When a feature spans multiple tickets, group them into ONE release note. Common bundle patterns:

| Pattern | Example |
|---|---|
| Client-side + server-side pair | LAP-2180 (client) + LAP-2181 (server) |
| Feature + follow-on bug fix | LAP-2180 + LAP-2222 (auto-update Underwriter Status) |
| Story under a sprint epic | LAP-1903 (Dropdown 2.0 rename) — multiple stories under the epic, one release note for the whole rename |

Bundling rules:

- All tickets must describe ONE coherent operator-facing change. If they don't, write multiple release notes.
- The flow diagram must work for the bundle as a whole. If you have to draw two diagrams, you have two features.
- The role sections must consolidate cleanly. If a BCM has 3 bullets from one ticket and 4 contradicting bullets from another, the bundle is wrong.

To confirm with the user before bundling, list the candidate tickets and the proposed feature name.

---

## Step 4 — Reconcile Against Confluence

For any operator-facing release note, cross-check at least these Confluence pages:

| Page | When to consult |
|---|---|
| `LOAN ORIGINATION SYSTEM - LAP` (1088716805) | Always — for stage names + owner mapping |
| Stage-specific child pages (1089568836, 1089568947, 1089569179) | When the change is within a specific stage |
| `LAP Query Module — User Guide` (1101660180) | When the change touches Query / Send-Back |
| `LOS for LAP` PRD (900431885) | When the change touches sanction / deviation / PDD |
| `Initial PRD: Concurrent / Internal Top-Up LAP` (1020199073) | When the change is Top-Up specific |

If the ticket references a stage / role / system string that contradicts the canonical Confluence page, the Confluence page wins. Update the ticket understanding (or flag the gap) before writing.

---

## Step 5 — Generate The Draft

Pick the right template per the (pattern, shape) matrix in `SKILL.md` §5 Phase 5: `templates/release-note-template.md` (Workflow Change × multi-role), `templates/branching-outcome-template.md` (Branching Outcome × multi-role), or `templates/single-role-one-pager-template.md` (single-role pager). Fill in using the extracted material. Then run the §5 Phase 7 verification gate (in `SKILL.md`).

---

## Worked Example — DigiLocker Journey Revamp

**Source tickets**: LAP-2180, LAP-2181, LAP-2222 (all status `LIVE`, all under epic LAP-2169 "LAP <> LSQ - April adhoc changes").

**Decomposition**:

| Beat | Material from tickets |
|---|---|
| Title | "DigiLocker Journey Revamp" (LAP-2169 epic = "April adhoc changes" — generic, so renamed to colloquial). |
| New flow | DigiLocker URL is requested → server checks `'Underwriter Status'` → if `'Not Seen'`, auto-flip to `'Rework'` and proceed → if a prior selfie is in `'Not Seen'` for ANOTHER reason, reject link gen → applicant + every co-applicant must complete DigiLocker → KYC results parsed → 7 KYC flags drive rejection routing → rejection comes back via LSQ → Kissht rejects on its end. |
| Key rules | (1) DigiLocker mandatory for all applicants AND co-applicants — no skip. (2) Link gen blocked if any applicant has a prior selfie in `'Not Seen'`; UI message displayed. (3) `'Not Seen'` selfie auto-converts to `'Rework'` (or `'is_discarded = true'`) on link gen. (4) `'check_status = FAILED'` if any of 5 specific KYC flags fail; LSQ rejects + Kissht rejects. (5) 7 rejection-reason flags + 9 KYC display flags, all visible in the More Details section of the Application Details tab. (6) Rejection only at LSQ confirmation, not pre-emptively at Kissht. |
| What this means for you | **Sales (SM, BM)**: Set expectations — DigiLocker is mandatory for every applicant + co-applicant. **CCPA**: New 9-flag KYC display in More Details; new rejection messaging on the panel. **BCMs**: Rejection routing now driven by KYC flags — read the rejection reason from the displayed flag. |
| Contacts | Reporters: Paras Arora (LAP-2180/2181), Shweta Iyengar (LAP-2222). Assignees: Neeraj Shah, Amar Dedhia, Sujit Poojary. List Paras + Shweta in Contacts; product support roster as fallback. |

This decomposition feeds directly into the canonical example at `examples/digilocker-journey-revamp.md`.

---

## Common Decomposition Failures (And How To Fix)

| Failure | Fix |
|---|---|
| Ticket description is sparse — no rules visible | Pull the parent epic. Pull the sibling tickets. Pull the Confluence reference. If still sparse, ask the reporter directly via comment. |
| Ticket has 12 numbered requirements, all looking equally important | Group by theme. Most release notes need 4–8 rules; consolidate sub-requirements into single rules. |
| Ticket mentions a stage name that's not in the glossary | Verify against canonical Confluence (1088716805). Either add to glossary with citation, or flag the gap. |
| Multiple tickets contradict on a rule | Take the latest-resolved ticket as authoritative; flag the contradiction in a hidden footer; ping the PM. |
| Ticket describes the new flow as a 30-line API sequence | The flow diagram is OPERATOR-LEVEL, not API-level. Compress to who-does-what nodes. |
| Ticket is purely backend (e.g. DB schema change) | Rejection — no field release note. See Step 0 filter. |

---

## Pattern Detection (Workflow Change vs Branching Outcome)

The skill supports two patterns. Run this check during Phase 2 decomposition to pick one.

### Detection heuristic

```
count_if_branches = number of "If <X>" / "If the <Y>" / "If <Z>, then" clauses
                    found in the ticket description
has_new_stage    = any stage name in the ticket NOT already in lap-stages.md
has_new_sla      = any phrase like "after N days" / "hard reject" / "auto-close" /
                   "expires" / "lost rejected" found in the description
has_new_role     = ticket inserts a role into an approval chain or removes one

if count_if_branches >= 2 AND not has_new_stage AND not has_new_sla AND not has_new_role:
    pattern = "Branching Outcome"   # use templates/branching-outcome-template.md
else:
    pattern = "Workflow Change"     # use templates/release-note-template.md (Relook spine)
```

When in doubt, default to **Workflow Change** — the Relook pattern is the canonical fallback. Branching Outcome is the rarer pattern and should only be picked when the heuristic clearly fits.

### Worked examples

| Ticket | Branches? | New stage? | New SLA? | Pattern |
|---|---|---|---|---|
| LAP-1445 (Send-Back Enhancement) | 1-2 | yes (sub-state stage values) | no | **Workflow Change** |
| LAP-1665 (Saral 2.0 Positive & Send-Back) | several | yes (Saral 2.0 stages) | no | **Workflow Change** |
| LAP-2180 / 2181 / 2222 (DigiLocker Journey Revamp) | several | yes (no new stages but altered behaviour at Sales PD Completed + CPA Verified) | no | **Workflow Change** (multi-stage flow change) |
| Relook Approval Revamp | minimal | yes (Relook CCM Approval Pending, Relook NCM Approval Pending) | yes (30-day hard reject) | **Workflow Change** (canonical) |
| LAP-2154 (LSQ Renach Handling) | 3 | no (Post Sanction unchanged) | no | **Branching Outcome** (canonical) |

### When the heuristic is ambiguous

Some tickets are mixed: a Workflow Change with branching inside one stage. In that case:

- Use **Workflow Change** as the document spine (preserve the flow diagram + stages + key rules).
- Embed a "What happens next" sub-block inside the relevant role section, with H3-level Case 1 / Case 2 / Case 3 sub-headings.
- Do NOT split into two release notes — that fragments the operator's mental model.

### Decomposing for Branching Outcome

When the pattern is Branching Outcome, the Phase 2 decomposition extracts different artefacts than Workflow Change:

| Beat | Material to extract for Branching Outcome |
|---|---|
| What this is about | The trigger event (one operator action) + a one-line summary per branch outcome |
| What you do | Stage / Tab / Subtab / Form / Dropdown locator path + the single click |
| Cases | One case per "If" branch in the ticket. Each case needs: what you see, what you do, how to verify if the action is silent |
| After | Downstream side-effects (Push to LMS contract, NACH validation, sanction state changes) |
| Role sections | Same as Workflow Change — only roles whose behaviour changes |
| Contacts | Same as Workflow Change |

Do NOT extract a flow diagram or a "stages in the system" list — these would be wrong for this pattern. The stage is unchanged.

### Recognising the three domain mini-patterns

While decomposing, also flag:

1. **Auto-action + manual backup.** Anywhere the ticket says "the system sends an SMS / email / notification automatically" or "auto-trigger" or "callback fired", note that the role section needs a sibling bullet recommending a manual fallback. Auto-comms in LAP have ~5–15% silent failure rate; manual backup is cheap insurance. Confirm with the author per release.
2. **Silent action + verification checklist.** When the system performs an action without UI confirmation (e.g. "callback applied", "field auto-populated", "internal flag flipped"), extract the specific fields/states the operator should see populated to confirm the action succeeded. List them as a bullet list.
3. **Non-overridable backend rule.** Phrases like "evaluated in the backend", "developed in the backend not in LSQ", "the system decides", "automatic", or "cannot be changed from the panel" trigger an explicit "you cannot change this from the panel" line in the role section.

These are content-level patterns; they affect what bullets appear, not which document pattern is used.
