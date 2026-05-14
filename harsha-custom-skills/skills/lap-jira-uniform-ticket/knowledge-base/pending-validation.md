# Pending Validation — items the canonical KB does NOT yet assert

> **Why this file exists.** The skill's spine is "never assume." Every entry in `lap-glossary.md`, `lap-stages.md`, `lap-roles.md`, and `lap-confluence-sources.md` is asserted as canonical. Items where canonical-status is uncertain DO NOT live in those files; they live here.
>
> When a PM asks the skill about an item below, the skill must say "I have a working hypothesis but it's not validated — please confirm or correct" rather than treating the working hypothesis as truth.
>
> When an item below is confirmed, move it OUT of this file and INTO the relevant canonical KB file (with citation). When refuted, delete the entry and add a "rejected" line in the §Resolved section at the bottom.

---

## Open items (4)

### V1 — RM (Relationship Manager) is in `lap-roles.md` but its distinctness vs SM is unconfirmed

**What we have:** `lap-roles.md` lists RM as "Relationship Manager (Sales) — field-facing sales contact, subordinate of SM/BM."
**What's uncertain:** Is RM a distinct system role in the LSQ panel (with its own permissions and queue) or just an organizational alias for SM with no panel presence?
**Why it matters:** The skill's role-detection logic (Phase 4 question D1) lists both RM and SM as separate options. If they're the same panel role, asking the PM to pick between them creates noise.
**Working hypothesis:** RM is distinct (some Sales-led journeys have RM ownership of the Sourcing pre-LOS step). But this hasn't been verified against the LSQ panel.
**To confirm:** Open the LSQ panel as a Sales user; check whether RM appears as an assignable role distinct from SM in the lead-routing dropdown.

### V2 — `Auditor` may resolve into `First Auditor` + `Second Auditor` as distinct panel roles

**What we have:** `lap-roles.md` lists Auditor as "KYC / VCIP Auditor — reviews Video KYC, issues Soft Reject / Hard Reject."
**What's uncertain:** LAP-2048 §3 describes a "First Auditor Review" followed by a "Second Auditor Review" with different verdict vocabularies (Soft/Hard Reject vs Approved/Rejected). Are these two distinct panel roles, or one role doing two sequential reviews?
**Why it matters:** Affects how the skill enumerates roles in BO/MX tickets that touch VCIP. If distinct roles, skill must offer both in Phase 4 D1.
**Working hypothesis:** Sequential reviews by the same role (one Auditor team with two-stage workflow). LAP-2048 reads more like a process specification than a role specification.
**To confirm:** Ask any PM who has filed a VCIP-related ticket post-LAP-2048 LIVE.

### V3 — Paras Arora's Atlassian accountId is not on file

**What we have:** `lap-confluence-sources.md` cites Paras Arora as a content author but the accountId field is empty.
**What's uncertain:** Just the data point — accountId is needed for any scripted CQL or JQL query that filters by this user.
**Why it matters:** NOT load-bearing for v1.0.1 markdown-only beta. Becomes load-bearing in v1.1 when the Atlassian MCP integration is bundled and the skill auto-search Phase 1 may want to filter "show me content authored by the original feature owner."
**Working hypothesis:** N/A — just need the value.
**To confirm:** Run `lookupJiraAccountId` against `paras.arora@kissht.com` once Atlassian MCP is bundled, OR check the `creator.accountId` field on any LAP ticket Paras has reported (e.g., LAP-1812, LAP-2048, LAP-2242).

### V4 — Veriphy's role in the current LAP flow is unconfirmed

**What we have:** `lap-glossary.md` originally listed Veriphy as a "KYC verification vendor" with a TODO marker. The TODO has been moved here.
**What's uncertain:** Is Veriphy currently in the LAP flow at all? It was in the kissht-field-release-notes sister-skill SKILL.md as a likely vendor, but no LAP exemplar references it. May be (a) a current vendor that exemplars happen not to mention, (b) a legacy vendor since replaced, or (c) used by sister products (Ring / PL) but not LAP.
**Why it matters:** If Veriphy is actively in LAP, PMs writing KYC tickets need to know to reference it. If it's not, the skill should not auto-suggest the term.
**Working hypothesis:** Used by sister products (Ring / PL) but not currently in LAP. This is a guess.
**To confirm:** Ask any LAP PM who has filed a KYC-related ticket post-LAP-2048 LIVE, OR check the LSQ vendor-config screen for active KYC vendors on the LAP product.

---

## Resolved (since v1.0.0)

| Item | Resolution date | Outcome | Where it landed |
|---|---|---|---|
| `Branch Verification` stage | 2026-05-14 | REJECTED — fabricated by Wave 1C subagent; no canonical source | Removed from both `lap-stages.md` and `lap-glossary.md` |
| `Lead Initiation` and `Sourcing` as LOS stages | 2026-05-14 | REJECTED — these are pre-LOS LSQ leadgen steps, not LOS opportunity stages per Confluence pageId 1088716805 | Removed from `lap-stages.md` |
| `Rate Approval Pending`, `Financier Review`, `Relook Approval Pending` (legacy), `Partially Disbursed` | 2026-05-14 | CONFIRMED — all four exist per Confluence pageId 1088716805 | Kept in `lap-stages.md`, TODO markers cleared |
| `Relook CCM Approval Pending` and `Relook NCM Approval Pending` (Revamp two-step) | 2026-05-14 | CONFIRMED LIVE in production — Confluence is stale, sister skill is canonical | Kept in `lap-stages.md` with note |
| `Disbursed by Financier` owner role | 2026-05-14 | DEFERRED — built in advance; no financier currently onboarded so stage has no current owner | Kept in `lap-stages.md` with explicit "no current owner" note |
| `CPA User` (LAP-1812 verbiage) | 2026-05-14 | CONFIRMED — maps verbatim to BCPA | Updated in both `lap-glossary.md` and `lap-roles.md` |
| OSV / OKYC / CKYC / eKYC / NTB / AA / OD acronyms | 2026-05-14 | CONFIRMED — standard fintech / RBI usage | Updated in `lap-glossary.md` |
| `Disbursal Details` Post Sanction subtab | 2026-05-14 | INFERRED from LAP-1879 / LAP-1868 / LAP-1505 / LAP-1663 | Documented in `lap-stages.md` §5 with "inferred — validate" footer |

---

## Update protocol

1. New uncertainty discovered: add as a numbered item above with the 5-field template (What we have / What's uncertain / Why it matters / Working hypothesis / To confirm).
2. Item confirmed: move to §Resolved with outcome = CONFIRMED + destination file.
3. Item refuted: move to §Resolved with outcome = REJECTED + reasoning. Delete from the canonical KB file if it was there.
4. Skill workflow change: when a ghost-term is encountered at Phase 4, the skill should check this file FIRST before asking the PM. If the term is here with a working hypothesis, present the hypothesis and ask the PM to confirm.

---

> **Pending-validation file version 1.0 — 2026-05-14.** Next review date: 4 weeks after first marketplace install (concurrent with the no-fast-path principle re-evaluation per SKILL.md §2).
