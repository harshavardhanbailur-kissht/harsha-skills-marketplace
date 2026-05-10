# Axis Enumeration

## What Is Morphological Analysis?

Morphological analysis is a structured technique for generating a complete option space by first
identifying the independent dimensions (axes) of a decision, then enumerating distinct values on
each axis. Instead of brainstorming options in a flat list — which tends to cluster around obvious
ideas — you decompose the decision space systematically.

The result: options you would not have thought of by free association, because they come from
combining axis values rather than from intuition.

**How it works:**
1. Identify 3-7 independent axes that together describe the full decision space
2. For each axis, enumerate the distinct positions (typically 2-5 per axis)
3. The full option space is the cross-product of all axis values
4. Not every combination is worth pursuing — that's what ranking is for — but enumeration should
   precede filtering

---

## Common Axes by Decision Type

### UI Placement Decisions

| Axis | Example Values |
|------|---------------|
| **Location** | Inline (in content), sidebar, modal/overlay, bottom sheet, separate page, notification tray |
| **Trigger** | Automatic (on load), user-initiated (explicit tap/click), event-driven (on completion), passive (on scroll) |
| **Visual prominence** | Primary CTA, secondary action, tertiary/link, hidden behind toggle, ambient/persistent |
| **Timing** | Before task, during task, immediately after task, deferred (next session), never (opt-in only) |
| **User state** | First-time user, returning user, power user, user who has completed action N times, user who has failed action |

### Feature Design Decisions

| Axis | Example Values |
|------|---------------|
| **Scope** | Single use case, multiple use cases, full workflow replacement |
| **Users served** | All users, segment A only, new users only, opted-in users, users above threshold X |
| **Implementation effort** | 1 sprint, 1 quarter, 1 cycle, multi-team dependency |
| **Reversibility** | Fully reversible (feature flag off), partially reversible (data migration needed), irreversible (schema change) |
| **Data requirements** | No new data, new events only, new APIs, new data stores, external data source |
| **Ownership** | Self-contained in one team, shared ownership, platform dependency, third-party |

### Architecture Decisions

| Axis | Example Values |
|------|---------------|
| **Coupling** | Tight (shared database), loose (API contract), decoupled (event-driven), independent (separate service) |
| **Scalability** | Handles 10x load with no change, requires re-architecture at 10x, requires re-architecture at 2x |
| **Team familiarity** | Team has shipped this before, team has read about it, team is learning, requires new hire |
| **Migration cost** | Zero migration, backward-compatible migration, breaking migration with downtime, data migration required |
| **Maintenance burden** | Self-maintaining, low (quarterly review), medium (monthly), high (constant attention) |

### Pricing / Monetization Decisions

| Axis | Example Values |
|------|---------------|
| **Collection timing** | Upfront (pre-disbursal deduction), at disbursal (separate payment), spread across EMIs, back-loaded (final EMI), deferred (on prepayment/default) |
| **Fee visibility** | Fully transparent (line item), bundled into interest rate, partially disclosed, zero-fee positioning with rate adjustment |
| **Fee structure** | Flat fee, percentage of principal, tiered by loan size, risk-based pricing, hybrid (flat + percentage) |
| **Revenue recognition** | Recognized at origination, amortized over tenure, recognized on accrual basis |
| **Customer segmentation** | Same for all, differentiated by credit score, differentiated by channel (digital vs. DSA), differentiated by loan size |
| **Competitive positioning** | Price leader (lowest fees), value leader (moderate fees, best experience), premium (high fees, premium service) |

**Domain-specific analogy prompts for pricing:** Consider analogies from SaaS (freemium, usage-based), insurance (premium structures), credit cards (annual fees vs. transaction fees), telecom (inclusive vs. itemized billing), e-commerce (shipping fee models).

### Migration / Sunset / Consolidation Decisions

| Axis | Example Values |
|------|---------------|
| **Migration timing** | Big-bang (all users, one date), rolling (cohort-by-cohort over months), indefinite (no deadline, organic) |
| **User segment sequencing** | New users first, power users first, low-activity users first, all simultaneously |
| **Coercion level** | Fully voluntary (marketing only), nudged (in-app prompts), soft-forced (old app goes read-only), hard-forced (old app killed) |
| **Data migration scope** | Full history (loans, transactions, KYC), active data only, fresh start (re-onboard) |
| **Feature parity at launch** | Full parity, core parity (80% features), MVP parity (critical flows only, rest backfilled) |
| **Identity/auth handling** | Auto-SSO (same credentials), link accounts manually, re-register with data prefill, fully new account |
| **Old app disposition** | Immediate sunset, maintenance mode, read-only archive, redirect wrapper |
| **Incentive structure** | No incentive, fee waiver, cashback/credit, gamified (streak transfer, loyalty points) |
| **Rollback plan** | No rollback (one-way door), partial rollback (revert within N days), full dual-run (both apps live) |

### Partnership / Integration Decisions

| Axis | Example Values |
|------|---------------|
| **Integration depth** | API-only, embedded widget, white-label, full co-build |
| **Data sharing scope** | Minimal (transaction data only), moderate (user profiles), full (all behavioral data) |
| **Revenue model** | Revenue share, flat licensing fee, per-transaction fee, equity swap |
| **Exclusivity** | Non-exclusive, category-exclusive, fully exclusive |
| **Termination cost** | Zero-cost exit, moderate migration, high lock-in |

---

## How to Identify the Right Axes

**Start with the decision's natural tensions.** Every real decision has things pulling in opposite
directions: speed vs. correctness, reach vs. personalization, simplicity vs. power. Each tension
often maps to an axis.

**Ask: "What would change if I chose differently here?"** If you imagine two very different
solutions, what are the dimensions along which they differ? Those are your axes.

**Check for stakeholder-specific axes.** Different stakeholders care about different dimensions.
Engineering cares about effort and reversibility. Product cares about user reach and impact.
Design cares about consistency. Each stakeholder's primary concern often reveals an axis you hadn't
named.

**The axis is independent when:** changing your position on it doesn't automatically determine your
position on any other axis. If "mobile-first" automatically implies "bottom sheet placement," those
might not be independent axes — or one might be a sub-axis of the other.

**You have the right axes when:**
- Every option you care about is describable using some combination of your axes
- No two options are identical across all axis values
- You can't collapse two axes into one without losing meaningful distinctions

---

## MECE Verification for Option Spaces

MECE stands for Mutually Exclusive, Collectively Exhaustive. It's the check that your option space
neither double-counts nor has gaps.

### Mutually Exclusive Check

For each pair of options, ask: could a team implement both simultaneously without contradiction?
- If yes, they're not mutually exclusive on the axis that defines them — you may have an axis
  definition problem
- Exception: options on different axes can be compatible; the mutual exclusivity applies within a
  single axis, not across axes

### Collectively Exhaustive Check

For each axis, ask: is there a position I haven't named that a stakeholder might advocate for?
- Walk the spectrum from minimum to maximum (e.g., "zero" to "full")
- Consider the "inversion" of each named position (if you have "proactive push," have you named
  "reactive pull"?)
- Check whether the "don't do this axis at all" position is represented

### Common MECE Failures

**Gap:** You've named "immediate" and "daily batch" for notification timing, but missed "session-end
batch." A user who wanted to minimize interruptions but still get same-day updates has no home.

**Overlap:** You've named "light modal" and "full-screen takeover" and "dialog." Light modal and
dialog are likely the same position on the prominence axis, just with different terminology.

**False exhaustion:** You've named 3 options on an axis and assumed that's all. The test is not
"I can't think of another" — it's "there is no structurally distinct position I haven't covered."

---

## Axis Count Guidelines

| Decision Complexity | Axes | Options per Axis | Typical Total Options |
|--------------------|------|------------------|-----------------------|
| Simple (1 feature, 1 team) | 3-4 | 2-3 | 6-10 |
| Medium (cross-team, multiple flows) | 4-6 | 2-4 | 10-18 |
| Complex (platform, architecture, multi-product) | 5-7 | 3-5 | 15-30 |

More axes is not automatically better. An axis that generates only one meaningful option isn't an
axis — it's a constraint. Name it as a constraint and remove it from the enumeration.
