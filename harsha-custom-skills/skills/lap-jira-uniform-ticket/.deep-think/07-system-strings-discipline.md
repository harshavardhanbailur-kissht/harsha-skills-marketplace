# 07 — System Strings Discipline

## Why system strings matter

The downstream `kissht-field-release-notes` skill has a non-negotiable rule: every panel label, dropdown value, status name, button label, error message, and SMS/email body that appears in a release note must be quoted **verbatim** in single quotes (`'Initiate E-Mandate Registration?'`, `'Lost Rejected'`, `'mandate_amount'`). The release note's value to the BCM/CCM/NCM at 9am depends on this — if the operator can't ctrl-F the quoted string in the panel, the release note is useless.

For the release-notes skill to feed cleanly, the upstream Jira ticket must already contain those verbatim strings. So `lap-jira-uniform-ticket` must extract them from the PM during Phase 4 and render them with single-quote discipline in the draft.

This file specifies (a) when the skill prompts for system strings, (b) how it auto-detects them when the PM uploads screenshots/Looms, (c) the rendering rules in the draft, and (d) the final "system strings used" footer.

---

## When the skill prompts (Category G in question taxonomy)

Category G is MUST for every ticket type. It runs in Phase 4 at three trigger points:

### G1 — Inline trigger (always)

After the PM has answered the proposed-change question (E1) for any type, the skill scans the answer for likely system-string candidates:

- Capitalised multi-word phrases ("Approval Pending", "Mark as Complete")
- Title-case noun phrases that look like UI ("Income Considered", "Final Sanction Pending")
- Words that appear in the loaded glossary's `system_strings` section
- Any phrase the PM put in quotes themselves (single, double, or backticks)

For each candidate, the skill asks:

> "I see `<candidate>` in your description. Is this the EXACT label as it appears in the panel? If yes, I'll quote it verbatim. If no, what's the exact text — even if it's awkward or has typos in the system?"

Awkward strings and system typos are kept verbatim — the operator's recognition of the string matters more than the linguistic quality.

### G2 — Old / new pair trigger (when change involves rename / add / remove)

If E1 contains words like "rename / new label / change the dropdown / replace / new status," the skill asks:

> "If this change adds, removes, or renames any panel label / dropdown value / status / button / message — list both the OLD string and the NEW string side by side. Use single quotes."

Result format:

```
| Old | New |
|---|---|
| 'Lost Rejected' | 'Lost Renach Rejected' |
| (none) | 'Renach Auto-Closed' |
| 'Income Considered Y/N' | (removed; now 'Income Considered' on Mark as Complete form) |
```

This table feeds the release-notes skill's "what changed in the panel" extraction directly.

### G3 — Auto-comm trigger (when H1 fires)

If the PM said any auto-comm fires (H1), the skill asks:

> "Quote the SMS / email / WhatsApp / in-app notification text verbatim — including dynamic variables in their template form (e.g., `{{applicant_name}}`, `{{loan_amount}}`). Even partial drafts are fine; flag anything not finalised."

This is the LAP-1812 lesson — the SMS verbatim is operator gold.

---

## Auto-detection from screenshots / Looms

If the PM drops a screenshot or Loom in the session, the skill:

1. **OCRs the screenshot** (or reads transcript / video frames for a Loom) using whatever the host environment provides (Claude's vision in chat, or a `lap-screen-analyzer`-style helper if installed).
2. **Extracts likely system strings**: button labels, headings, dropdown values, status badges, error toasts.
3. **Surfaces them as a checklist** to the PM:

> "From your screenshot I extracted these candidates as system strings: [`'Mark as Complete'`, `'Income Considered'`, `'Yes / No'`, `'Save'`]. Confirm which are part of THIS change (quoted in the ticket) vs ambient UI (skipped)."

4. PM ticks the relevant ones; the skill quotes them in the draft.

If no OCR / vision is available (the skill is running in a tool-restricted environment), G1's inline trigger is the only mechanism and the PM must type strings manually.

---

## Rendering rules in the draft

The Phase 5 drafter applies these rules when writing system strings into the spine:

| Rule | Detail |
|---|---|
| **R1 Single quotes always** | `'Approval Pending'`. Never double quotes (which Markdown often re-renders as smart quotes); never backticks (which imply code). |
| **R2 First mention quotes verbatim** | `The case status flips to 'Lost Rejected'.` Subsequent mentions in the same section may use the bare term once introduced. |
| **R3 No paraphrase, ever** | If the panel says `'Initiate E-Mandate Registration?'` the ticket must say `'Initiate E-Mandate Registration?'` — not `'Initiate E-Mandate Registration'` (missing question mark) and not `'Start E-Mandate'` (paraphrase). |
| **R4 Dynamic variables in template form** | SMS/email bodies retain `{{applicant_name}}` and `{{loan_amount}}` — do NOT substitute example values inline. |
| **R5 Group quoted strings in the System Strings footer** | All system strings used in the body are deduplicated into a footer block (see below) for the release-notes skill to extract en masse. |
| **R6 Old/new strings rendered as a side-by-side table** | When G2 fired, the rendering uses the table form, not flowing prose, so the release-notes skill can detect the change as a structured rename. |
| **R7 Panel-vs-system distinction** | Some strings are panel labels (operator-visible); some are backend identifiers (e.g., `mandate_amount` field name in the API contract). Both get single quotes; the System Strings footer tags each as `panel` or `backend`. |

---

## The mandatory "System Strings Used" footer

Every ticket ends with this footer block (after the Glossary footer, before the Sources footer):

```
---
**System strings referenced in this ticket** (verbatim, for downstream use):

Panel labels & dropdown values:
- 'Mark as Complete'
- 'Income Considered'
- 'Edit'

Status names:
- 'Final Sanction Pending'
- 'Post Sanction'

Tab labels:
- 'NIC' (Non Income Considered)

Button / action labels:
- 'Save'

(no SMS / email templates in this ticket)

Old → New rename pairs:
- (none in this ticket)
```

The footer is auto-generated from the body during Phase 5 — the drafter doesn't ask the PM to compile it; it walks the draft, extracts every single-quoted string, classifies it (heuristic from loaded glossary + suffix patterns: `Pending` / `Rejected` → status name; `tab` / `Tab` → tab label; etc.), and writes the footer.

The PM sees the footer in the draft and can correct misclassifications. Any uncertainty defaults to the most general bucket (`Panel labels & dropdown values`), which is correct often enough.

This footer is the single most important contract artifact for the release-notes skill — Phase 2 of that skill extracts the full system-strings set from this footer in one pass instead of hunting through the body.

---

## Verification at Phase 7

The output gating checklist (file 09) includes these system-string checks:

- **U-G1.** Every quoted string in the body uses single quotes (no smart quotes, no backticks).
- **U-G2.** Every quoted string in the body appears in the System Strings footer.
- **U-G3.** Every entry in the System Strings footer appears in the body at least once.
- **U-G4.** No bare phrase that looks like a panel label (capitalised multi-word, glossary `system_strings` match) appears unquoted in the body.
- **U-G5.** When G2 fired (rename / add / remove), the Old → New table is present and complete.
- **U-G6.** Every SMS / email / notification body in the ticket retains its `{{template}}` variables.

A failure routes back to Phase 4 G or Phase 5 rendering depending on the failure mode.

---

## What the skill never asks

- "Should we quote this?" → If it looks like a system string, quote it. If the PM disagrees on review, they unquote it. The skill's default is to over-quote, not under-quote.
- "What does this string mean?" → That's a glossary question (file 05), not a system-strings question. The two flows are kept separate.
- "Can you redact the screenshot?" → Out of scope; the skill assumes the PM dropped a shareable screenshot.
