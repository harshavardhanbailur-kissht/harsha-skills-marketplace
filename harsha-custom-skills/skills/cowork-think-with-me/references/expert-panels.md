# Expert Panels: Roster, Selection, and Interaction Protocol

## The 12-Expert Roster

| # | Expert | Domain | Select When |
|---|--------|--------|-------------|
| 1 | Product Manager | Product strategy, prioritization, user value, trade-off analysis | Always — anchor for every panel |
| 2 | UX Designer | User experience, interaction patterns, cognitive load, accessibility | Any UI decision, user journey design, onboarding flows |
| 3 | Business Analyst | Requirements clarity, process flows, edge cases, compliance mapping | Process/workflow decisions, requirement ambiguity, system integrations |
| 4 | Growth Analyst | Acquisition funnels, retention loops, virality mechanics, engagement | Growth features, referral programs, activation improvements |
| 5 | Data Analyst | Metric definition, statistical validity, measurement design, A/B test setup | Data-driven decisions, when "we'll measure it" is part of the plan |
| 6 | User Advocate | Customer pain points, support ticket patterns, accessibility gaps | Any user-facing feature — especially those that create new steps or friction |
| 7 | Engineering Lead | Technical feasibility, system constraints, effort estimation, debt | When implementation cost or complexity is a real factor in ranking |
| 8 | Design System Lead | Component consistency, design language, reuse vs. custom | UI component decisions, naming, visual consistency across surfaces |
| 9 | Compliance / Risk | Regulatory requirements, data privacy, legal exposure, audit trails | Fintech, healthcare, any domain with regulatory surface area |
| 10 | Operations Lead | Manual process burden, support scalability, internal tooling impact | Features that create back-office work or change agent workflows |
| 11 | Marketing / Comms | Messaging, positioning, brand consistency, user communication | Feature naming, in-app copy, launch messaging, pricing communication |
| 12 | Research Lead | User research methodology, interview synthesis, insight validity | When existing research data is being used to justify options |
| 13 | Pricing / Revenue Strategist | Pricing psychology, revenue modeling, willingness-to-pay, price elasticity, unit economics, fee structure design | Any decision involving pricing, fees, monetization, packaging, or revenue model changes |
| 14 | Finance / Treasury Lead | Revenue recognition, cash flow modeling, balance sheet impact, cost of funds, provisioning | Lending products, payment flows, treasury decisions, any decision with P&L or balance sheet impact |
| 15 | Migration / Transition Lead | Data migration, rollback planning, dual-run operations, cutover sequencing, support surge planning | Migration, sunset, platform consolidation decisions |

---

## Panel Selection Protocol

**Step 1: Read the problem statement.**
Identify the primary domain — what kind of decision is this fundamentally? Product, process, technical, regulatory?

**Step 2: Select 2-3 most relevant domains.**
Ask: whose opinion would most change the ranking if you hadn't included them?

**Step 3: Always include PM as anchor (#1).**
The PM holds the frame across all expert views and keeps the conversation from becoming siloed.

**Step 4: Add 2-4 domain experts.**
Select based on direct relevance. If two experts would say roughly the same thing, pick one.

**Step 5: Document the selection.**
In EXPERT_PANEL.md, record:
- Which experts were selected
- Which were explicitly excluded and why
- What the panel is designed to stress-test

**Panel size by decision complexity:**
- 2-3 options: 3 experts (PM + 2)
- 4-8 options: 4 experts (PM + 3)
- 8+ options or multiple axes: 5 experts (PM + 4)

---

## How Experts Interact: Three Stages

### Stage 1 — Independent Analysis
Each expert evaluates the option space from their domain lens only. They do not see each other's analysis yet. This prevents groupthink where the first strong opinion anchors everyone else.

What each expert produces:
- Their top 2-3 ranked options
- Their 1-2 primary concerns about the current frontrunner
- One question they would want answered before committing

Format:
```
[Expert: Growth Analyst]
Top picks: Option C, Option A
Primary concern with current frontrunner (Option B): retention loop is absent — 
  users complete the action but have no reason to return.
Question: Do we have data on return visit rate for comparable features?
```

### Stage 2 — Debate
Experts are presented with each other's analyses. The PM facilitates. This is where disagreements surface explicitly.

Rules for the debate stage:
- Disagreements must be named, not smoothed over
- If Expert A ranks Option C first and Expert B ranks it last, that gap is the most important thing in the panel
- The PM does not resolve disagreements — they document them
- Each expert may update their ranking after hearing others, but must state why

### Stage 3 — Synthesis
The PM synthesizes the panel output into three deliverables:
1. **Areas of agreement**: options all or most experts converged on
2. **Areas of disagreement**: specific points where experts diverged and the reasoning on each side
3. **Dominant concerns**: risks or questions that appeared across multiple expert views

---

## Documenting Disagreements (Not Just Agreements)

The common mistake: writing "the panel preferred Option C" when in fact three experts preferred C and two preferred A. The minority view is often the most important signal.

**What to write in EXPERT_PANEL.md:**

Good:
```
Panel split on Option C vs. Option A (3:2). 
Growth Analyst and Engineering Lead preferred C for velocity and acquisition fit.
User Advocate and Compliance preferred A due to lower friction for first-time users 
  and cleaner audit trail.
UX Designer preferred C but flagged that the current design does not account for 
  error recovery — a shared concern across the panel.
```

Bad:
```
The panel recommended Option C with some reservations about user experience.
```

The bad version loses the minority view, loses the specific concerns, and loses the fact that a User Advocate and Compliance officer had a different preference — both of whom represent real constraints that will surface post-launch if ignored now.

**Rule: If you can't name who disagreed and what they said, you haven't documented the disagreement.**

---

## When Expert Views Are Genuinely Uncertain

Sometimes experts produce "it depends" — this is valid and must be captured as such.

Format:
```
[Expert: Engineering Lead]
Cannot rank without: current API rate limits and whether we own or share the 
  third-party integration. If shared: Option A is infeasible. If owned: Option A 
  becomes the top pick on effort grounds.
```

Uncertainty in expert views goes into the "Residual Uncertainty" field of the decision doc, not into the synthesis as a false resolution.

---
