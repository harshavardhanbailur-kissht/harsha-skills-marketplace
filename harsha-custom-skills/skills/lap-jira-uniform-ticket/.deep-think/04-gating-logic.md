# 04 — Gating Logic

## When can the skill stop asking and start drafting?

The skill exits Phase 4 (Socratic Decompose) and enters Phase 5 (Draft) when **all six gates** below pass simultaneously. Until they all pass, the skill keeps asking. There is no fast path. There is no "good enough" override.

The gates are checked after every new answer is written to `ANSWERS.md`. The first answer that flips the last failing gate triggers the transition.

---

## The six gates

### Gate 1 — Mandatory categories complete

Every category marked **MUST** for the detected type (file 03 matrix) has at least one answer recorded in `ANSWERS.md`.

| Type | MUST categories that must be filled |
|---|---|
| WC | A, B, C, D, E, G, I, J, K, L, M, N |
| BO | A, B, C, D, E, G, H, I, J, K, L, M, N |
| SC | A, B, C, D, E, G, J, K, L, M, N |
| RD | A, C, D, E, F, G, I, J, K, L, M, N |
| MX | A, B, C, D, E, G, H, I, J, K, L, M, N |

Empty is empty — a one-word answer ("yes" / "no") is allowed only on yes/no questions; for narrative questions, a one-word answer triggers a follow-up (file 03's max-5-follow-ups cap applies).

### Gate 2 — Triggered conditionals complete

For every CONDITIONAL question that fired (because a prior answer matched the trigger), an answer is recorded.

If a CONDITIONAL fires and the PM declines to answer ("not applicable" / "skip"), the skill records the decline in ANSWERS.md as `<question>: PM declined: <reason>`. This counts as answered for gating, but Phase 7 will surface it for review.

### Gate 3 — Glossary fully matched

Every named stage / role / system string mentioned in any answer is either:

- Found verbatim in `lap-glossary.md` / `lap-stages.md` / `lap-roles.md`, OR
- Defined inline by the PM in this session and recorded in `LOCAL_GLOSSARY.md`.

No "ghost" terms — words that appear in the answers but neither the glossary nor LOCAL_GLOSSARY can resolve. A ghost term blocks the gate.

### Gate 4 — No unresolved contradictions

`CONTRADICTIONS.md` has zero open items. Every detected contradiction (file 06 mechanism) has a resolution recorded — either the PM clarified which version is correct, or the PM marked both as scoped (e.g., "behaviour differs between primary applicant and co-applicant; both are correct").

### Gate 5 — At least one consequence per rule (E2 satisfied)

For every step / case / row in the proposed change (Category E), the answer carries a system consequence. A bare operator action with no system response is a fail. The skill auto-detects by scanning E answers for "the system ___" / "and then ___" / "this triggers ___" / "case status becomes ___" patterns. If a step has no consequence pattern, the skill loops back to the E2 question for that step.

This gate is the most important uniformity discipline — it's what makes the downstream release-notes skill able to ship "rules with consequences" (its locked principle).

### Gate 6 — Contacts named (not departments)

Category N has produced ≥1 named human for reporter, ≥1 named human for assignee, and (for Epics or cross-team tickets) ≥1 named sponsor. "Product team" / "QA" / "Ops" alone fail this gate. Each contact also has a Jira account ID resolvable via `lookupJiraAccountId` (so Phase 8 push doesn't fail on assignee).

---

## Gate evaluation cadence

After each answer is written to ANSWERS.md, the skill runs all six gates:

```
new_answer → write to ANSWERS.md
           → re-run G1..G6
           → if all pass: announce "Phase 4 complete — drafting now."
           → if any fail: pick the next unanswered MUST or triggered CONDITIONAL
                          (or follow-up on a contradictory / consequence-less / ghost-term answer)
                          and ask the next question.
```

The skill announces gate progress every 5 questions ("3 of 6 gates pass; remaining: G3 ghost term 'XYZ', G5 missing consequence on step E1.4, G6 unnamed assignee"). Keeps the PM oriented.

---

## Hard-stop vs soft-stop

The gate evaluator distinguishes:

- **Soft fail** — the gate could pass with one more answer. Skill keeps asking.
- **Hard fail** — the gate is structurally unanswerable in this session (e.g., PM doesn't know the assignee yet because team allocation hasn't happened). Skill records `BLOCKED: <reason>` against that gate, asks the PM whether to defer the gate or pause the session.

A deferred gate ships the ticket with an explicit `[BLOCKED]` marker in the relevant slot (e.g., assignee = `[BLOCKED — to be filled at sprint planning]`). The downstream release-notes skill detects these markers and refuses to consume the ticket until they're resolved. This is by design — partial tickets are visible failures, not invisible ones.

---

## Re-entry after Phase 7 failure

When Phase 7 validation fails and routes back to Phase 4, the gating logic re-applies — but only the gate(s) that the failed validation check correspond to:

| Phase 7 check failed | Re-opens gate |
|---|---|
| Universal U-system-strings | G3 (glossary / strings) + Phase 4 G |
| Universal U-consequences | G5 (consequence per rule) + Phase 4 E2 |
| Universal U-contacts | G6 + Phase 4 N |
| Type-specific WC1 (actor block missing) | G1 (D missing) + Phase 4 D |
| Type-specific BO2 (Case missing See/Do/Verify) | Phase 4 E1 BO variant |
| Etc. | (See file 09 for full mapping) |

This is the surgical re-entry rule from file 01 — never re-run the whole phase.

---

## Worked example: gating walk-through on LAP-2039 (SC type)

| After answer | G1 | G2 | G3 | G4 | G5 | G6 | Ready? |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| A1 + A2 (intent + why) | partial | n/a | yes | yes | n/a | no | no |
| B1 (current 6 steps) | partial | n/a | yes | yes | n/a | no | no |
| B3 (workaround detail) | partial | n/a | yes | yes | n/a | no | no |
| C1 + C2 (Credit PD form) | partial | n/a | yes | yes | n/a | no | no |
| D1 (BCM only) | partial | n/a | yes | yes | n/a | no | no |
| E1 (proposed flow, both directions) | partial | n/a | yes | yes | partial | no | no |
| E2 (consequences per step) | partial | n/a | yes | yes | yes | no | no |
| G1 + G2 (NIC tab, Income Considered, Mark as Complete strings) | partial | n/a | yes | yes | yes | no | no |
| J1–J3 (QA scope incl. state-refresh + back-to-back) | partial | n/a | yes | yes | yes | no | no |
| K1–K2 (out-of-scope + primary-applicant lock assumption) | partial | n/a | yes | yes | yes | no | no |
| L1 (3 lean AC bullets) | yes | n/a | yes | yes | yes | no | no |
| M1 (Loom + screenshots) | yes | n/a | yes | yes | yes | no | no |
| N1 (Mohini, Paras) | yes | yes | yes | yes | yes | yes | **YES** → Phase 5 |

12 questions to draft. The actual session for an SC ticket should land in 10–20 questions; WC and BO sit at 25–50; RD around 20–35; MX is the worst case at 40–80. The 100-turn cap from file 03 is the absolute outer bound.
