# Worked Example: LAP Journey — Apply Now Button Placement

**Scenario:** Harsha is designing the Kissht LAP (Loan Against Property) web journey.

---

**User:** Where should I place the Apply Now button on the LAP web journey?

---

**Claude:** Before we answer that, let me reframe the question — because "where" is only one of six things that determine whether the button works.

The real question is: **what combination of location, trigger, prominence, journey timing, user eligibility state, and CTA context produces the highest quality application starts?**

Let me open the option space across all six axes before we converge on one.

---

## Axes of Enumeration

**Axis 1 — Location on page**
Above fold → After hero section → After benefits block → After eligibility calculator → Sticky footer → Floating sidebar → Bottom of page (above footer)

**Axis 2 — Trigger condition**
Always visible → After 30% scroll → After 60% scroll → After time-on-page (45s+) → After eligibility check completed → After engagement signal (hover on EMI calculator)

**Axis 3 — Visual prominence**
Full-width primary CTA → Hero-size primary → Secondary button → Contextual inline link → Animated pulse → Ghost button

**Axis 4 — Journey stage**
Landing page → After property details entered → After income/employment entered → Post approval-in-principle → Returning user re-entry

**Axis 5 — User eligibility state**
Unknown (fresh visitor) → Pre-qualified (came via campaign with params) → Qualified (completed eligibility check on page) → Returning (partial application) → Rejected (previous application declined)

**Axis 6 — Placement relative to other CTAs**
Standalone → Paired with "Check Eligibility First" → In a comparison table row → In FAQ answer ("Yes, you can apply here") → After testimonial block

---

## 13 Specific Placement Options

| # | Option | Location | Trigger | Prominence | Stage | Eligibility State | CTA Context |
|---|--------|----------|---------|------------|-------|-------------------|-------------|
| 1 | Above-fold primary | Hero | Always | Full-width primary | Landing | Unknown | Standalone |
| 2 | Post-hero with eligibility nudge | After hero | Always | Primary + "Check eligibility first" ghost | Landing | Unknown | Paired |
| 3 | Sticky footer — always on | Sticky footer | Always | Secondary | Landing | Unknown | Standalone |
| 4 | Sticky footer — scroll-triggered | Sticky footer | After 30% scroll | Primary | Landing | Unknown | Standalone |
| 5 | Post-eligibility unlock | After eligibility calculator | After check completed | Animated pulse unlocking | Landing | Qualified | Standalone |
| 6 | Campaign pre-qual CTA | Above fold | Always | Full-width primary | Landing | Pre-qualified | Standalone |
| 7 | Inline in EMI calculator | Inside calculator | After EMI displayed | Contextual inline link | Landing | Unknown | Inside tool |
| 8 | Comparison table apply row | Inside comparison table | Always | Secondary per row | Landing | Unknown | In table |
| 9 | Post-testimonial anchor | After testimonials | Always | Primary | Landing | Unknown | After social proof |
| 10 | Returning user banner | Top of page | Always | Banner CTA | Landing | Returning | Resume prompt |
| 11 | Rejected user re-entry | After rejection message | Always | Secondary | Post-rejection | Rejected | "Try again" context |
| 12 | Approval-in-principle CTA | Post-AIP screen | Always | Full-width primary | Post-AIP | Qualified | Standalone |
| 13 | FAQ contextual link | Inside FAQ answer | Always | Inline link | Landing | Unknown | Inline in content |

---

## Expert Panel for This Decision

Selected: PM (anchor), UX Designer, Growth Analyst, Compliance/Risk (fintech context), User Advocate.

**UX Designer:** Options 3 and 4 (sticky footer) risk banner blindness on desktop. On mobile they work because thumb reach is natural. Sticky footers also compete with browser chrome on iOS.

**Growth Analyst:** Option 5 (post-eligibility unlock) is the highest-intent moment in the entire page. If someone has confirmed they are eligible, the window to convert is under 90 seconds. Friction at that exact moment is where most LAP journeys leak.

**Compliance/Risk:** Option 11 (rejected user re-entry) needs legal review — communicating "try again" to rejected applicants may conflict with NBFC fair practice codes. Must show reason for rejection and cooling-off period before re-prompting.

**User Advocate:** Users who land without pre-qualification context are overwhelmed by a full-width primary CTA above the fold. They have not yet understood what a LAP is or whether they qualify. Option 2 (paired with "Check Eligibility First") respects where they are mentally.

---

## Stack-Rank

### Rank 1: Option 5 — Post-Eligibility Unlock (animated pulse, after check completes)
**Best case:** Converts the highest-intent moment. User has confirmed eligibility, EMI looks acceptable, trust is built. Conversion rate at this point is structurally higher than any above-fold placement.
**Worst case:** If eligibility tool has high abandonment (users start but don't complete), the button appears for too few users. You are optimizing a rare event.
**Why this rank:** Only placement where user intent AND eligibility are both confirmed simultaneously.
**Who would hate this:** Marketing — it requires users to engage with the eligibility tool first, which is an additional step before the funnel. Will look bad in top-of-funnel click metrics.

### Rank 2: Option 6 — Campaign Pre-Qual CTA (above fold, pre-qualified users)
**Best case:** User arrives via SMS/email campaign with loan amount and property type pre-filled. Above-fold CTA is appropriate because they already know why they are here. High conversion expected.
**Worst case:** Requires campaign URL params to be correctly passed and read. If params are missing (link forwarded by user, etc.), the page shows a primary CTA to an unqualified visitor — same problem as Option 1.
**Why this rank:** Best option for known-qualified users. Degrades gracefully only if you have a fallback state.
**Who would hate this:** Engineering — requires parameter-based personalization and a default fallback state, which is extra implementation work.

### Rank 3: Option 4 — Scroll-Triggered Sticky Footer (after 30% scroll)
**Best case:** Always present once user has shown intent to read. Works on all user types. Easy to implement. Low cognitive load — the button doesn't demand attention before user is ready.
**Worst case:** Sticky elements on mobile eat screen real estate. Users on small screens lose 60-80px of viewport permanently after the trigger fires. On iOS Safari the URL bar collapse/expand interacts badly with fixed footers.
**Why this rank:** Best default fallback for unknown eligibility state. Should run in parallel with Rank 1 and 2, not instead of them.
**Who would hate this:** Mobile UX — viewport impact is real. Needs A/B test specifically on iOS Safari.

### Rank 4: Option 2 — Post-Hero Paired CTA ("Apply Now" + "Check Eligibility First")
**Best case:** Respects user who doesn't yet know if they qualify. The secondary CTA funnels uncertain users into the eligibility tool, warming them up for Rank 1.
**Worst case:** Two CTAs side-by-side dilute click-through on the primary. If the user always clicks "Check Eligibility First," you have turned the Apply Now button into a secondary action — it will look bad in isolation but is actually correct behavior.
**Why this rank:** The right placement for cold traffic, but requires accepting that Apply Now clicks will be lower.
**Who would hate this:** Growth — lower immediate CTA clicks will trigger concern even if downstream conversion is higher. Need to measure application completion rate, not just button clicks.

### Rank 5: Option 10 — Returning User Banner (resume prompt, top of page)
**Best case:** Users who dropped off mid-application are high-intent. A specific "Resume your application — you left off at property details" banner converts extremely well in re-engagement campaigns.
**Worst case:** Requires session/account state to be read on page load. If the user is not logged in, you cannot show this. Implementation requires a login check + application state API call on every page load.
**Why this rank:** High value, but conditional on having the infrastructure to detect returning users.
**Who would hate this:** Users who do not want to be reminded of an incomplete application (e.g., their financial situation changed). Needs a dismiss option.

### Rank 6: Option 7 — Inline in EMI Calculator
**Best case:** Contextually perfect — user has just seen their potential EMI and can act immediately. Removes the step of "now where do I apply?"
**Worst case:** If EMI is higher than expected, the inline CTA placement means the button appears immediately after a moment of sticker shock. Presenting Apply Now when the user is negatively surprised is exactly wrong.
**Why this rank:** High ceiling, but emotionally risky. Needs UX copy to cushion before the CTA appears.
**Who would hate this:** Users with high property value but low income — they will see an EMI they cannot afford and your CTA will feel tone-deaf.

### Rank 7: Option 9 — Post-Testimonial Anchor
**Best case:** Social proof is directly adjacent to conversion action. Well-established pattern for trust-building journeys.
**Worst case:** Users who scroll to testimonials are already near the bottom of the page. Most high-intent users have either already clicked above or bounced. This placement catches the "still unconvinced" segment, which is a real segment but not the largest one.
**Why this rank:** Good secondary placement, not a primary one. Worth including but should not be the only CTA.
**Who would hate this:** No strong hater. Mild concern: if testimonials are thin or not credible, this placement inherits that weakness.

### Rank 8: Option 8 — Comparison Table Apply Row
**Best case:** Useful for users who came to compare LAP vs. personal loan vs. home equity. Contextual apply in a comparison table is clean.
**Worst case:** Comparison tables on the LAP page mean you are showing the user other loan types. If they are not already considering LAP specifically, you may convert them to the wrong product.
**Why this rank:** Only appropriate if the page already has a comparison section by design. Do not add a comparison table just to justify this CTA placement.
**Who would hate this:** Product — showing competitors or alternative loan types on the LAP journey page is a business decision, not just a UX one.

### Rank 9: Option 3 — Sticky Footer Always-On
**Best case:** Maximum visibility. Button is always in view. Good for short, low-scroll pages.
**Worst case:** On a content-rich LAP landing page, an always-visible footer CTA is present before the user has read anything. It signals urgency before trust is built, which in a high-ticket financial product (LAP amounts typically Rs. 10-50L) creates friction, not conversion.
**Why this rank:** Appropriate for short pages and returning users. On a first-visit content page, it is too early. Strictly inferior to the scroll-triggered version (Rank 3).
**Who would hate this:** Any user who has not yet decided to apply. That is most first-visit users.

### Rank 10: Option 13 — FAQ Inline Link
**Best case:** Helpful for users reading "How do I apply?" in the FAQ. A contextual link there is genuinely useful and reduces search friction.
**Worst case:** FAQ is rarely a high-traffic section. This placement will have very low click volume. It is a fine inclusion but should never be a primary placement strategy.
**Why this rank:** Include it — it is low-cost and catches a real intent signal. But do not measure success by it.
**Who would hate this:** No one. This is the least controversial placement. Also the least impactful.

### Rank 11: Option 12 — Post-AIP Full-Width CTA
**Best case:** The user has received approval-in-principle. This is the only moment in the journey where the bank has already said yes. Conversion should approach 80%+ if the AIP page is well-designed.
**Worst case:** This is not a landing page placement — it is a mid-journey page. If the team conflates "Apply Now" on the landing page with "Proceed to Full Application" on the AIP screen, they will build two different things.
**Why this rank:** This should definitely exist, but it answers a different question than "where on the landing page." Flagged as a separate decision.
**Who would hate this:** No one, at this stage. The friction here should be nearly zero.

### Rank 12: Option 1 — Above-Fold Primary (cold traffic, unknown state)
**Best case:** Maximum first-impression visibility. If the user arrives already knowing they want a LAP and has done their research elsewhere, this works.
**Worst case:** Most LAP applicants are first-generation borrowers or property owners unfamiliar with the product. An above-fold "Apply Now" before they understand the product or their eligibility is a leaky bucket — high clicks, low completions, and wasted KYC pipeline load.
**Why this rank:** This is the most common choice and one of the worst for a high-ticket, low-familiarity product like LAP. It optimizes for the metric that feels good (clicks) while degrading the metric that matters (completed applications).
**Who would hate this:** Ops team — they process applications that come in. A high volume of unqualified applications from above-fold clicks creates manual review load with no corresponding revenue.

### Rank 13 (Worst): Option 11 — Rejected User Re-Entry CTA
**Best case:** Re-engages users whose situation has changed (income increased, property value reassessed) after the standard cooling-off period.
**Worst case:** Showing "Apply Again" to a freshly rejected user without a clear explanation of why they were rejected, what has to change, and how long they must wait violates RBI Fair Practices Code for NBFCs. This is not a UX problem — it is a compliance problem. This option as described is not implementable without significant legal scaffolding.
**Why this rank:** Worst option not because the user need is invalid but because it cannot be shipped without legal review, a defined cooling-off period UX, rejection reason disclosure, and a complaint escalation path. Do not build this without those in place.
**Who would hate this:** Compliance team, and rightly so. Any user who receives a re-application prompt immediately after rejection will experience it as harassment.

---

## Decision Doc Snippet

**Problem Statement:** On the Kissht LAP web journey landing page, determine the optimal Apply Now button placement strategy to maximize quality application starts (not raw click-throughs).

**Selected Approach:** Three-layer CTA strategy, not a single placement:
1. **Layer 1 — Default state (unknown user):** Rank 4 (post-hero paired CTA) + Rank 3 (scroll-triggered sticky footer after 30% scroll). Do not place a standalone primary CTA above the fold for cold traffic.
2. **Layer 2 — Post-eligibility (qualified user):** Rank 1 (post-eligibility unlock, animated pulse). This is the primary conversion event. Measure this separately from Layer 1 clicks.
3. **Layer 3 — Campaign traffic (pre-qualified user):** Rank 2 (above-fold primary, parameter-triggered). Only show this state when campaign params are present and valid.

**Rejected:** Above-fold standalone primary for cold traffic (Rank 12). Rejected user re-entry CTA without compliance scaffolding (Rank 13).

**Unexplored:** Mobile-specific placements (thumb zone, iOS Safari sticky footer behavior), progressive disclosure patterns where button text changes based on scroll depth ("See if you qualify" → "Check your eligibility" → "Apply Now"), and WhatsApp CTA as an alternative conversion path for users who abandon the web form.

**Residual Uncertainty:** We do not know the traffic mix between campaign (pre-qualified) and organic (unknown) visitors. If >60% of traffic is campaign, the above-fold primary (Rank 2) should be promoted to the default. This should be the first thing measured.

**Key metric to track:** Application completion rate per CTA source, not button click-through rate.
