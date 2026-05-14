# External PM Ticket-Writing Patterns — Research & Scoring

**Purpose:** Survey external pattern sources, score each against the locked LAP principles, and decide what to fold into the new uniform LAP Jira ticket pattern.
**Method:** research-analyst 7-phase epistemic methodology (Phase 1 scope → Phase 7 structured output, with Phase 4 source-validation gate).
**Audience:** Senior PM at Kissht (LAP), the rest of the LAP PM team, and downstream consumers of the `kissht-field-release-notes` skill.
**Date:** 2026-05-14.

---

## Phase 1 — Scope & Decompose

### Sub-questions
1. Which external pattern, if any, gives us a header convention better than what the 6 LAP exemplars already use?
2. Which external pattern, if any, gives us a body structure (logic / rules / matrices / branches) better than the LAP exemplars?
3. Which external pattern, if any, gives us a QA + BA scope convention better than the LAP exemplars?
4. Which external pattern, if any, gives us an Acceptance Criteria convention that stays leaner than what the exemplars already do?
5. Which external pattern is best-aligned to feed the `kissht-field-release-notes` Relook (workflow change) and Renach (branching outcome) shapes?
6. Which external patterns invite anti-patterns we must explicitly forbid?

### What counts as evidence
- Primary doc by the original author/org (e.g., the actual Atlassian "user story" page, the actual Shape Up book, the actual Linear docs).
- Evaluated against the 6 hand-picked LAP exemplars (LAP-1812, LAP-2039, LAP-2046, LAP-2048, LAP-2052, LAP-2242), which are the canon.

### Locked principles (re-stated as scoring criteria)
| # | Principle | Scoring criterion |
|---|---|---|
| 1 | Plain English narrative | Pattern stays in flowing English, not pseudocode/JSON/SQL |
| 2 | Zero repetition | Pattern has structural dedup, not "say it three times" |
| 3 | Named QA Scope + BA Scope | Pattern accommodates explicit operator-grade verification + assumptions+impact |
| 4 | Lean AC (3-5 bullets) | Pattern does not bloat AC into a regression test plan |
| 5 | Downstream extractability | Output has named stages with owners, rules with consequences, verbatim strings, branch outcomes, named contacts |
| 6 | Team onboardability | A new PM can learn it in a single session |

---

## Phase 2 — Competing Hypotheses

Before evaluating, three hypotheses to check against:

- **H1: The 6 exemplars are already best-in-class and external patterns add nothing.** (Risk: complacency; we miss a structural improvement.)
- **H2: The exemplars are good but a single external pattern (e.g., Shape Up "Fat Marker Sketches" + breadboards, or Spotify DIBB) would substantially upgrade them.** (Risk: hero-worship; we import jargon and degrade plain-English fit.)
- **H3: Each external pattern has 1-2 transferable atoms but no whole pattern survives the locked principles intact. We should adopt atoms, reject wholes.** (Most likely; pre-mortem confirmed in Phase 6.)

---

## Phase 3 — Systematic Search

Source list with reliability ratings:

| # | Source | Type | Reliability |
|---|---|---|---|
| 1 | Atlassian — "User stories with examples and a template" — atlassian.com/agile/project-management/user-stories | Vendor primary doc | High |
| 2 | Basecamp — *Shape Up* by Ryan Singer (free online book) — basecamp.com/shapeup | Author primary | High |
| 3 | Amazon — Working Backwards / PR-FAQ (Colin Bryar & Bill Carr book *Working Backwards*; multiple Amazon-internal posts e.g., productplan.com/glossary/working-backward-amazon-method, sebastianquint.com/amazon-pr-faq | Practitioner primary + secondary | High |
| 4 | Spotify — DIBB framework (Henrik Kniberg, "Spotify Rhythm" deck and posts; tomtunguz.com/dibb) | Author primary + secondary | Medium-High |
| 5 | Linear — "Issue templates" docs — linear.app/docs/issue-templates and Linear's "Method" — linear.app/method | Vendor primary | High |
| 6 | GitLab — Issue & MR templates — docs.gitlab.com/ee/user/project/description_templates.html plus public templates in gitlab.com/gitlab-org/gitlab/-/tree/master/.gitlab/issue_templates | Vendor primary + actual templates | High |
| 7 | Bill Wake — "INVEST in good stories, and SMART tasks" (xp123.com, 2003) + Ron Jeffries — Three C's for stories (ronjeffries.com) | Author primary | High |
| 8 | Intercom — Job Stories (Paul Adams, Alan Klement — "Replacing the user story with the job story", jobstobedone.org) | Author primary | High |
| 9 | Notion — "PRD template" — notion.so/templates/product-requirements-doc | Vendor primary | Medium |
| 10 | Aha! — Roadmap items / Release-master template — aha.io | Vendor primary | Medium |
| 11 | ProductPlan — PRD templates — productplan.com/learn/product-requirements-document | Vendor primary | Medium |
| 12 | Google — Bug Hunters reporting guidance (bughunters.google.com) + Google design-doc culture (industriallogic.com, Steve Yegge "Stop Writing Classes"-era docs, plus Eugene Yan summary "Design Docs at Google") | Practitioner primary + secondary | Medium-High |
| 13 | Stripe — PRD culture (Ben Thompson Stratechery interview with Patrick Collison; Lenny Rachitsky podcast Ep. with Patrick Collison; "Stripe Press" public artifacts) | Secondary | Medium |

**Not found / explicitly absent:** No external pattern has a named "BA Scope / Open Considerations" section in the LAP shape (assumption + impact-of-being-wrong). Closest analog is Amazon's PR-FAQ "Internal FAQ" and Shape Up's "Rabbit Holes / No-Gos." None is a drop-in replacement.

---

## Phase 4 — Source Validation (mandatory gate)

For each Tier-1 source, check: Authority, Recency, Corroboration, Bias.

| # | Source | Authority | Recency | Corroboration | Bias |
|---|---|---|---|---|---|
| 1 | Atlassian user-story page | Vendor of the tool we use | Maintained, current | Cross-confirmed by Mike Cohn *User Stories Applied* | Vendor — leans toward "use Jira features" |
| 2 | Shape Up (Singer) | Original Basecamp methodology | 2019, stable canon | Cross-confirmed by many engineering blogs | Strong opinion — anti-backlog |
| 3 | Amazon PR-FAQ | Internal Amazon doctrine; Bryar/Carr were Bezos shadows | 2020 book; 2004 internal origin | Multiple ex-Amazon writeups corroborate | Survivorship — works inside Amazon culture |
| 4 | Spotify DIBB | Henrik Kniberg (Spotify coach, then external) | 2014 origin, still cited | Tom Tunguz, Reforge corroborate | Methodology-marketing bias |
| 5 | Linear docs + Method | Vendor with strong opinionated stance | Continuously updated | Cross-confirmed in PM community | Vendor — promotes Linear features |
| 6 | GitLab templates | Open-source actual artifacts | Live repo | Direct evidence | Engineering-centric, not PM |
| 7 | INVEST (Wake) + 3 C's (Jeffries) | XP movement originals | 2003-era; still canon | Universal in agile lit | Process-orthodoxy bias |
| 8 | Job Stories (Klement, Adams) | Original authors | 2012-2013, mature | Reforge, Strategyzer cite | Anti-user-story polemic |

All 8 pass. Tier 2 (#9-13) pass with lower weight (more vendor marketing, less foundational).

---

## Phase 5 — Evidence Synthesis: Pattern Cards

Each pattern card: brief shape, 5-criterion rubric (1-5 each, 25 max), what to ADOPT, what to REJECT.

**Rubric scale:** 1 = violates locked principle, 3 = neutral, 5 = directly reinforces locked principle.

---

### 1. Atlassian "User Story" — *As a [persona], I want [goal], so that [reason]*
**Source:** atlassian.com/agile/project-management/user-stories — Max Rehkopf
**Shape:** Header sentence in Connextra format, then "Conversation" + acceptance criteria as bullets.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 4 | The sentence form is narrative |
| No-repetition fit | 3 | Inviting both story sentence and AC tends to restate intent |
| Downstream extractability | 3 | Persona is helpful but no stage/owner/string capture |
| Lean-AC fit | 3 | Atlassian explicitly recommends Given-When-Then which often bloats |
| Team-onboardability | 5 | Universal, every PM knows it |
| **Total** | **18** | |

- **ADOPT:** The 1-paragraph plain-English intent at the top of every ticket — keep what LAP-2052 already does ("The idea is to make the list of the Property Document and Property Type to be same across LSQ"). Allow but do not require a Connextra "As a / I want / so that" sentence — LAP-1812 uses it well; LAP-2046 omits it and is cleaner. Make Connextra OPTIONAL.
- **REJECT:** Given-When-Then style AC — it bloats and pushes toward repetition (the rule is already in the body). LAP-1812's bulleted AC under named sub-areas is leaner.

---

### 2. Shape Up — Pitch (Problem, Appetite, Solution sketch, Rabbit holes, No-gos)
**Source:** Basecamp, *Shape Up*, Ryan Singer — basecamp.com/shapeup/1.5-chapter-06
**Shape:** A "pitch" is shaped at the right level of abstraction; it has Problem, Appetite (time budget), Solution (fat-marker sketch + breadboard), Rabbit holes (hard parts), No-gos (explicitly out of scope).

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 5 | Singer is famously prose-first |
| No-repetition fit | 5 | Each section has a distinct job — no overlap |
| Downstream extractability | 4 | Rabbit holes + No-gos extract cleanly; sketches do not |
| Lean-AC fit | 5 | Shape Up has no AC — appetite IS the constraint |
| Team-onboardability | 3 | Strong opinion; takes a session to internalize "appetite" |
| **Total** | **22** | |

- **ADOPT (highest-value adoption):** Rabbit holes + No-gos as a small named block in our BA Scope / Open Considerations. The closest analog in LAP is LAP-2039's "Open Considerations for BA" with the assumption + impact-of-being-wrong format. Adding a one-line "Out of scope" / "Explicitly not changing" note into BA Scope prevents scope-creep regressions and is cheap to write. Example sentence integration: *"Out of scope: We are NOT changing the Edit-form behaviour for the primary applicant — that path stays Yes-locked and is unaffected."* This protects against the regression LAP-2039 already calls out in prose.
- **ADOPT:** "Appetite" idea reframed — when LAP tickets describe a workaround we are killing (LAP-2039), name the time/effort the workaround currently costs ("BCM goes through 7 steps to flip one toggle"). LAP-2039 already does this informally. Codify it.
- **REJECT:** Fat-marker sketches and breadboards as required artifacts. LAP already attaches Lovable prototypes (LAP-1812) and Figma/screenshots when needed. Don't mandate; keep optional.
- **REJECT:** Removing AC entirely (Shape Up's "appetite is the AC" is wrong for our context — QA needs verifiable bullets).

---

### 3. Amazon PR-FAQ (Working Backwards)
**Source:** Bryar & Carr, *Working Backwards* (2020); productplan.com/glossary/working-backward-amazon-method
**Shape:** A press release written before the product is built. Heading, sub-heading, summary paragraph, problem, solution, customer quote, leader quote, call to action. Then an Internal FAQ + External FAQ.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 5 | Mandatorily prose, no jargon, "would a journalist understand?" |
| No-repetition fit | 4 | The FAQs invite restatement of the press release content |
| Downstream extractability | 2 | Press release format is anti-operational — lacks stages/owners |
| Lean-AC fit | 3 | No AC concept |
| Team-onboardability | 2 | High ceremony; designed for new-product launches, not feature tickets |
| **Total** | **16** | |

- **ADOPT:** The "Internal FAQ" pattern as the ancestor of our BA Scope / Open Considerations. Format the LAP "Open Considerations" as Q-and-A where the Q is the unresolved assumption and the A is "Proposal: ... Impact: ..." LAP-2039 already does this in prose; tightening to Q+Proposal+Impact format would be marginal. **Recommendation: keep as-is, do not impose Q+A — the LAP prose is already cleaner.**
- **ADOPT (very narrow):** The Bezos rule that the doc must be readable cold by someone who has not been in any prior meeting. Make this a write-time gate in the skill: "If a new PM joining tomorrow can't understand this ticket without context, rewrite the intent paragraph."
- **REJECT:** The press release format itself — it is for product launches, not feature tickets. Importing it would inflate every ticket with marketing prose.

---

### 4. Spotify DIBB (Data, Insight, Belief, Bet)
**Source:** Henrik Kniberg, "Spotify Rhythm" (2014); tomtunguz.com/dibb
**Shape:** Data (what we observed) → Insight (what it means) → Belief (what we believe will happen if we act) → Bet (what we will do).

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 4 | Clean prose-first |
| No-repetition fit | 3 | The four boxes invite restatement |
| Downstream extractability | 2 | Strategy-tier output; not stage/owner-aware |
| Lean-AC fit | 3 | No AC concept |
| Team-onboardability | 3 | Easy to learn but the four boxes feel formal |
| **Total** | **15** | |

- **ADOPT (very narrow):** When a ticket is born from a real operational pain (LAP-2039 BCM workaround; LAP-2046 mismatched DOB cases), name the data/observation in the Problem paragraph. LAP-2039 already does this in one line ("operational issues have been observed in some LAP cases where data mismatches exist"). Codify: every Current Flow / Problem section should name the trigger observation.
- **REJECT:** The four-box DIBB scaffolding — it is a strategy framework, not a ticket pattern. Importing it would push us toward jargon and ceremony.

---

### 5. Linear — Issue templates + "The Linear Method"
**Source:** linear.app/docs/issue-templates ; linear.app/method
**Shape:** Linear ships minimal templates by default. The Linear Method emphasises: short titles, concrete descriptions, no nested epics. Their public template is essentially: Title, Description, Acceptance Criteria (optional), Sub-tasks.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 5 | "Be concise and concrete" is the explicit doctrine |
| No-repetition fit | 5 | Strongest anti-restatement stance of any vendor |
| Downstream extractability | 3 | Generic structure; LAP needs more shape |
| Lean-AC fit | 5 | Linear doctrine is "AC is optional and short" |
| Team-onboardability | 5 | Famously simple |
| **Total** | **23** | |

- **ADOPT (high-value):** The "concise and concrete" write-time rule. Add to skill: "If a sentence does not change a reader's behaviour, delete it." This is the single-best dedup heuristic from any vendor.
- **ADOPT:** The Linear Method's stance that AC is optional, NOT mandatory. For LAP, AC is mandatory — but it should be allowed to be absent when the body's numbered logic IS the AC (as in LAP-2046 and LAP-2052, which have no separate AC section and are still exemplars). Codify: AC is a "lean derived view" of the body, not a re-listing.
- **REJECT:** Linear's anti-template stance generally — LAP needs more named structure than Linear ships, because the downstream release-notes skill needs predictable section names.

---

### 6. GitLab — Issue & MR templates
**Source:** docs.gitlab.com/ee/user/project/description_templates.html ; gitlab.com/gitlab-org/gitlab/-/tree/master/.gitlab/issue_templates
**Shape:** GitLab has many templates; the canonical "Feature proposal" template has: Release notes, Problem to solve, Intended users, User experience goal, Proposal, Further details, Permissions and Security, Documentation, Availability & Testing, Available Tier, Feature Usage Metrics, What does success look like.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 4 | Prose-friendly |
| No-repetition fit | 2 | Many sections invite restatement (Problem ↔ Proposal ↔ Success) |
| Downstream extractability | 4 | "Release notes" and "Availability & Testing" sections are highly extractable |
| Lean-AC fit | 3 | Spread across multiple sections |
| Team-onboardability | 2 | 12 sections — heavy |
| **Total** | **15** | |

- **ADOPT (highest single-atom adoption):** GitLab's "Release notes" line at the **top** of the template. This is a one-sentence summary the writer drafts up-front for downstream release-notes consumption. **Direct synergy with `kissht-field-release-notes`.** Recommendation: optional one-line "Release-note line" field at the top of LAP tickets ("CCM cases up to 7L now auto-route to SCH if CCM is unavailable"). Operator can lift verbatim.
- **ADOPT:** GitLab's "Permissions and Security" sub-section idea — a small block to call out role/permission impact when a ticket changes who can do what (LAP-2242 has this implicitly in the matrix; LAP-2052 has it implicitly in stage names). For LAP, fold into the existing Logic numbered list rather than adding a new section.
- **REJECT:** The 12-section template — too heavy; violates team-onboardability.

---

### 7. INVEST + 3 C's (Card / Conversation / Confirmation)
**Source:** Bill Wake, *INVEST in Good Stories* (2003); Ron Jeffries, *Three C's*
**Shape:** Stories should be Independent, Negotiable, Valuable, Estimable, Small, Testable. Each story is a Card (placeholder), a Conversation (the real spec), a Confirmation (acceptance test).

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 5 | Pure prose |
| No-repetition fit | 4 | The 3 C's explicitly separate intent / detail / verification — anti-restatement |
| Downstream extractability | 3 | Generic; not stage-aware |
| Lean-AC fit | 5 | "Confirmation" = small set of testable bullets |
| Team-onboardability | 4 | Universally taught |
| **Total** | **21** | |

- **ADOPT (high-value framing):** Use 3 C's as the **mental model** for the three sections of every LAP ticket: (1) Card = the 1-paragraph intent, (2) Conversation = Current/Proposed + Logic + Tables + QA Scope + BA Scope, (3) Confirmation = AC. This is exactly how the 6 exemplars already work. Codify the names so PMs have a vocabulary.
- **ADOPT:** The **Testable** test from INVEST as a write-time gate on AC — every AC bullet must be observable by QA in UAT. LAP-2242 already does this ("Approver unavailability is simulated in UAT by inactivating the user at the relevant role / hierarchy level").
- **REJECT:** Mandating the full INVEST checklist as a write-time gate — too academic, would slow PMs. Keep INVEST as a review-time mental model only.

---

### 8. Job Stories — *When [situation], I want to [motivation], so I can [outcome]*
**Source:** Alan Klement, "Replacing the user story with the job story" (2013); Paul Adams (Intercom)
**Shape:** Replaces persona-led story with situation-led story. No persona. Anchored on the trigger context.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 5 | Pure prose |
| No-repetition fit | 4 | Single sentence; no restatement |
| Downstream extractability | 4 | Captures trigger + motivation + outcome — useful for branch outcomes |
| Lean-AC fit | 4 | Doesn't dictate AC |
| Team-onboardability | 4 | Slightly less familiar than Connextra but learnable in minutes |
| **Total** | **21** | |

- **ADOPT (situational use):** When a LAP ticket is fundamentally about a stage/trigger (e.g., LAP-2046 "When an ETB user enters the LAP flow, the system should check VCIP status, so PAN re-verification is skipped if already validated"), Job Story format is a better fit than Connextra. Allow either Connextra or Job Story for the optional opening sentence. Job Story is the better choice when there is no single persona but there is a clear trigger event.
- **REJECT:** Mandating Job Story for every ticket — LAP-1812 is genuinely persona-led ("CPA user wants to..."). Both formats should be allowed.

---

### 9. Notion — PRD template
**Source:** notion.so/templates/product-requirements-doc
**Shape:** Problem, Goals (with metrics), Non-goals, User stories, Solution, Success metrics, Open questions, Resources.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 4 | Prose-friendly |
| No-repetition fit | 3 | Problem ↔ Goals ↔ User stories invite restatement |
| Downstream extractability | 3 | Generic; not stage-aware |
| Lean-AC fit | 3 | "Success metrics" is the AC stand-in |
| Team-onboardability | 3 | Familiar Notion shape |
| **Total** | **16** | |

- **ADOPT:** "Non-goals" as a one-line note inside BA Scope — same atom as Shape Up's "No-gos." Already covered above.
- **ADOPT:** "Open questions" → already covered by LAP's "Open Considerations for BA" — the LAP form (assumption + proposal + impact) is BETTER than Notion's bare "Open questions" list because it forces the writer to commit to a default and name the cost of being wrong.
- **REJECT:** "Goals with metrics" as a required section — most LAP tickets are workaround-removal or compliance gates, not metric-moving. Mandating success metrics would invite synthetic KPIs.

---

### 10. Aha! — Roadmap items
**Source:** aha.io product docs
**Shape:** Strategic-tier (Goals → Initiatives → Releases → Features → Requirements). Heavy on roadmap hierarchy.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 3 | Mixes prose with roadmap fields |
| No-repetition fit | 2 | Hierarchical tools push the same idea up and down |
| Downstream extractability | 2 | Roadmap-tier; not stage-aware |
| Lean-AC fit | 3 | AC is buried under "Requirements" |
| Team-onboardability | 2 | Heavy structure |
| **Total** | **12** | |

- **ADOPT:** Nothing meaningful for LAP tickets. The hierarchy idea is already covered by Jira epics.
- **REJECT:** The full Aha! shape — would over-structure LAP tickets.

---

### 11. ProductPlan — PRD templates
**Source:** productplan.com/learn/product-requirements-document
**Shape:** Purpose, Stakeholders, Background, Vision, Customer journey, Functional & non-functional requirements, Constraints, Acceptance criteria, Risks, Timeline.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 4 | Prose-friendly |
| No-repetition fit | 2 | Purpose ↔ Background ↔ Vision is famously redundant |
| Downstream extractability | 3 | "Constraints" and "Risks" are useful |
| Lean-AC fit | 3 | AC is a separate section but tends to bloat |
| Team-onboardability | 2 | 10 sections |
| **Total** | **14** | |

- **ADOPT:** "Constraints" as a one-line note in BA Scope (same atom as Shape Up No-gos and Notion Non-goals).
- **REJECT:** The full template — too heavy.

---

### 12. Google — Bug Hunters reporting + Design docs
**Source:** bughunters.google.com ; "Design Docs at Google" (Eugene Yan summary, 2020)
**Shape (design doc):** Context and scope, Goals and non-goals, Actual design (incl. APIs, data, UI), Alternatives considered, Cross-cutting concerns (security, privacy, observability).

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 4 | Engineer-prose |
| No-repetition fit | 4 | Each section has a distinct job |
| Downstream extractability | 4 | "Alternatives considered" is high-value |
| Lean-AC fit | 4 | No AC concept; design intent IS the spec |
| Team-onboardability | 3 | Engineering-coded |
| **Total** | **19** | |

- **ADOPT (high-value atom):** "Alternatives considered" as an OPTIONAL paragraph inside BA Scope. When a LAP ticket picks one of several plausible approaches (e.g., LAP-2046 picks "check VCIP status before re-verifying PAN" rather than "always re-verify" or "trust ETB blindly"), name the alternatives that were rejected and why in 2-3 sentences. This protects against later "why didn't you just..." reviews.
- **ADOPT:** "Cross-cutting concerns" idea — already covered implicitly by LAP-2242's Role Definitions section. Make it permissive: when a ticket touches roles, audit logs, or permissions, name them.
- **REJECT:** API/data/UI sub-sections — these would push us toward pseudocode and violate the plain-English rule.

---

### 13. Stripe — PRD culture
**Source:** Patrick Collison interviews (Lenny Rachitsky podcast, 2022; Stratechery, 2018); Stripe Press public artifacts
**Shape:** Stripe's described practice: short prose docs, anti-template, "writing IS thinking." No public canonical template.

| Criterion | Score | Note |
|---|---|---|
| Plain-English fit | 5 | Strongest writing-quality bar of any company cited |
| No-repetition fit | 5 | Anti-bloat; "writing reveals what you actually believe" |
| Downstream extractability | 2 | Anti-template means low extractability |
| Lean-AC fit | 4 | No fixed AC; writing-quality discipline |
| Team-onboardability | 2 | Requires writing-culture investment |
| **Total** | **18** | |

- **ADOPT (atom):** The "writing IS thinking" principle as a write-time gate in the skill: "If you cannot write the 1-paragraph intent in plain English without bullets, you do not yet understand the ticket. Stop and re-think before writing the body."
- **REJECT:** The anti-template stance. LAP needs templates because the downstream release-notes skill is structurally template-dependent.

---

## Phase 6 — Contradiction Analysis & Pre-mortem

### Contradictions surfaced
1. **Shape Up vs Linear vs GitLab on AC:** Shape Up has none, Linear says optional, GitLab spreads it across 3 sections. The LAP exemplars resolve this: AC is mandatory but lean (3-5 bullets, named sub-areas, derived from body, never a re-listing). LAP's stance is correct and stronger than any single external pattern.
2. **Connextra vs Job Story:** Both work; the LAP exemplars use Connextra (LAP-1812) and prose-only (LAP-2039, LAP-2046, LAP-2052) interchangeably. Decision: allow both, neither mandatory.
3. **PR-FAQ vs Linear conciseness:** PR-FAQ is ceremonial; Linear is anti-ceremony. The LAP exemplars sit closer to Linear in prose-density but borrow PR-FAQ's "readable cold" rule.

### Pre-mortem — "Imagine our final pattern degraded the LAP exemplars. What did we do wrong?"
1. **We imported Connextra as mandatory.** Forces every ticket to start with "As a [persona]" and breaks the cleaner LAP-2052 / LAP-2046 voice.
2. **We imported Given-When-Then AC.** Bloats AC into a regression script — exactly what we forbid.
3. **We imported Goals-with-metrics.** Forces synthetic KPIs onto compliance and workaround-removal tickets.
4. **We imported the full GitLab template.** Adds 6 sections we don't need.
5. **We imported PR-FAQ press-release format.** Marketing prose for an internal feature ticket — wrong audience.

All five risks are explicitly REJECTED above.

### Risks of being wrong
- **Wrong adoption:** Borrowing too much from any single source dilutes the LAP voice. **Mitigation:** Adopt atoms, not wholes. Every adoption above is a single-element transplant.
- **Wrong rejection:** Dismissing Shape Up's "appetite" entirely loses the time-cost framing that LAP-2039 already uses informally. **Mitigation:** Adopt the framing, reject the artifact (no fat-marker sketches).

---

## Phase 7 — Structured Output: Final Recommendations

### Top adoptions (atoms only, ranked by impact on LAP voice)

| Rank | Atom | Source | Confidence | Where it goes in the LAP pattern |
|---|---|---|---|---|
| 1 | "Release-note line" — one-line operator-readable summary at the top | GitLab feature proposal template | High | New optional 1-line field at the top of every ticket. Direct feed into `kissht-field-release-notes`. |
| 2 | "Out of scope / Explicitly not changing" — one-line note | Shape Up "No-gos" + Notion "Non-goals" | High | Inside existing "Open Considerations for BA" section. Prevents regression scope-creep. |
| 3 | "Alternatives considered" — 2-3 sentences | Google Design Docs | Medium-High | Optional paragraph inside BA Scope. Used when the design picks one of several plausible approaches. |
| 4 | "Concise and concrete" delete-test | Linear Method | High | Write-time gate in the skill: "If a sentence does not change reader behaviour, delete it." |
| 5 | "Readable cold" gate | Amazon PR-FAQ | High | Write-time gate: "If a new PM joining tomorrow can't grasp the intent paragraph without context, rewrite." |
| 6 | "Writing IS thinking" intent gate | Stripe culture | Medium | If the 1-paragraph intent cannot be written in plain English, stop — the ticket is not yet ready. |
| 7 | 3 C's mental model (Card / Conversation / Confirmation) | Ron Jeffries | High | Vocabulary for the three layers of every LAP ticket (intent / body / AC). |
| 8 | Job Story format as alternative to Connextra | Klement / Adams | Medium | Allow either Connextra or Job Story for the optional opening sentence. Job Story when trigger-led, Connextra when persona-led. |
| 9 | Time-cost framing for workaround tickets | Shape Up "appetite" | Medium | Codify what LAP-2039 already does — name the operator time the workaround currently costs. |
| 10 | INVEST "Testable" gate on AC bullets | Bill Wake | High | Every AC bullet must be observable in UAT. |

### Top rejections (with rationale)

| Pattern | Why rejected |
|---|---|
| Connextra as MANDATORY opening | Breaks LAP-2052 / LAP-2046 voice; inviting jargon where prose works better. |
| Given-When-Then AC | Bloats AC into a regression script. Violates lean-AC principle. |
| Full PR-FAQ press release format | Marketing prose for internal feature tickets — wrong audience. |
| Full GitLab 12-section template | Too heavy; 6 of the sections are dead weight for LAP. |
| Spotify DIBB four-box scaffolding | Strategy-tier framework, not a ticket pattern. Pushes ceremony. |
| Aha! roadmap hierarchy as ticket structure | Roadmap-tier; would over-structure tickets. |
| Notion "Goals with metrics" as required | Forces synthetic KPIs on compliance/workaround tickets. |
| Shape Up "fat-marker sketches" as required artifact | LAP already attaches Lovable / Figma / screenshots when needed; don't mandate. |
| Stripe anti-template | LAP's downstream release-notes skill requires predictable section names. |
| Google design-doc API/data/UI sub-sections | Pushes toward pseudocode; violates plain-English rule. |

### Where the LAP exemplars already MATCH OR EXCEED world's best practice (do not over-correct)
1. **Open Considerations for BA (LAP-2039)** is BETTER than Notion's "Open questions" because it forces assumption + proposal + impact. Keep as-is.
2. **Numbered Logic with consequences (LAP-2242)** is BETTER than GitLab's "Functional requirements" because every rule names the system behaviour. Keep as-is.
3. **Tables for matrices (LAP-2046, LAP-2242)** is industry-standard and the LAP form is clean. Keep as-is.
4. **Verbatim system strings (LAP-1812 SMS verbiage)** is rare in any external pattern — most patterns gesture at "messaging" without quoting. The LAP practice of pasting the exact SMS string is operator gold. Keep as-is and codify as a write-time gate ("If your ticket changes user-facing copy, paste the exact string").
5. **Bug fan-out as quality signal (LAP-2052, LAP-2242)** — naming the child bugs that surfaced is a unique LAP practice not present in any external pattern. Keep as-is.
6. **Source-of-truth links at bottom (LAP-2046, LAP-2052, LAP-2242)** — Sheet Link, attachment names, parent epic. Cleaner than GitLab's "Resources" section because it appears at the end where reviewers expect it.

### Unexpected finding
Linear's anti-template doctrine and GitLab's heavy-template doctrine BOTH score lower than the LAP exemplars on no-repetition fit. The LAP middle path — 6-7 named sections that each have a unique job — is structurally more anti-repetition than either extreme. This means the right framing for the new skill is NOT "we should adopt X external pattern" but "we already have a defensible middle path; we should harden it with 3-4 atomic improvements borrowed from outside, and explicitly reject 5-6 known bad imports."

### Confidence levels
- High confidence: adoptions #1, #2, #4, #5, #7, #10 (all evidence-corroborated, low risk).
- Medium-High confidence: adoptions #3 (Alternatives considered) — useful but easy to over-write; needs a length cap.
- Medium confidence: adoptions #6, #8, #9 — all situational and optional.

### Citations
1. Atlassian — atlassian.com/agile/project-management/user-stories
2. Singer, R. — *Shape Up* — basecamp.com/shapeup
3. Bryar, C. & Carr, B. — *Working Backwards* (2020)
4. Kniberg, H. — "Spotify Rhythm" (2014); tomtunguz.com/dibb
5. Linear — linear.app/method ; linear.app/docs/issue-templates
6. GitLab — docs.gitlab.com/ee/user/project/description_templates.html ; gitlab.com/gitlab-org/gitlab/-/tree/master/.gitlab/issue_templates
7. Wake, B. — *INVEST in Good Stories* (xp123.com, 2003) ; Jeffries, R. — *Three C's* (ronjeffries.com)
8. Klement, A. — "Replacing the user story with the job story" (jobstobedone.org, 2013)
9. Notion — notion.so/templates/product-requirements-doc
10. Aha! — aha.io product docs
11. ProductPlan — productplan.com/learn/product-requirements-document
12. Google — bughunters.google.com ; Eugene Yan, "Design Docs at Google" (eugeneyan.com, 2020)
13. Stripe — Lenny Rachitsky podcast with Patrick Collison (2022)

---

*End of research document. Synthesis lives in `external-patterns-synthesis.md`.*
