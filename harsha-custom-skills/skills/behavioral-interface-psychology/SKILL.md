---
name: behavioral-interface-psychology
description: Comprehensive behavioral psychology knowledge base for analyzing software interfaces and codebases. Triggers when analyzing UI/UX code, reviewing interface implementations, evaluating design decisions, identifying dark patterns, assessing accessibility compliance, optimizing conversion flows, designing AI/chatbot interfaces, building dashboards or data visualizations, designing onboarding flows, or evaluating enterprise software UX. Also triggers when user mentions behavioral design, interface psychology, perceptual psychology, cognitive load, user experience analysis, design patterns, myth-busting, evidence-based design, dark mode, skeleton screens, gamification psychology, search UX, notification fatigue, checkout optimization, or asks to evaluate/critique/analyze interface code through the lens of human psychology. Use for evidence-based interface design decisions backed by quantified research from ACM CHI, Nielsen Norman Group, Baymard Institute, and cognitive psychology literature. Provides specific effect sizes, study citations, and myth-busting contradictions to common design assumptions.
---

# Behavioral Interface Psychology Skill v3

Analyze interfaces through human psychology research with quantified thresholds, effect sizes, evidence-based recommendations, and myth-busting contradictions to common design assumptions.

**What makes this skill unique**: Every recommendation includes quantified data (effect sizes, N values, p-values) and replication status (STRONG/MODERATE/DEBUNKED). This skill actively flags widely-repeated design myths that lack peer-reviewed support.

## Core Principle

**Perception routinely overrides reality in interface evaluation.** Progress bars with backwards-moving ribbing reduce perceived duration by 11%. "True" randomness feels broken to users. First impressions form in 50ms. Design for human cognitive architecture, not technical correctness.

## Analysis Framework

When analyzing interface code, evaluate these domains in order of relevance:

### 1. Perceptual Mapping
Check if implementations honor human perception laws:
- **Volume/brightness controls** → Must use logarithmic curves, not linear (Weber-Fechner Law)
- **Progress bars** → Should accelerate toward completion (peak-end effect)
- **Animations** → Require easing functions, 200-400ms duration
- **Shuffle algorithms** → Need quasi-random with spacing, not true random

### 2. Response Time Thresholds
Validate against neurological constants:
| Threshold | User Perception | Required Feedback |
|-----------|-----------------|-------------------|
| <100ms | Instantaneous | None needed |
| 100ms-1s | Flow maintained | Activity indicator |
| 1-10s | Attention at risk | Progress indicator |
| >10s | Task abandoned | Percent-done + estimate |

### 3. Touch & Input Targets
Verify accessibility compliance:
- iOS: 44×44pt minimum
- Android: 48×48dp (~9mm)
- WCAG AA: 24×24px minimum
- WCAG AAA: 44×44px recommended

### 4. Cognitive Load
Assess working memory respect:
- Working memory: 4±1 chunks (Cowan), not 7±2
- Menu items: 8-16 per level, 2-3 levels deep
- Form fields: 12-14 optimal, 23+ creates friction
- Navigation depth: Error rates increase 4%→34% from 1→6 levels

### 5. Typography & Readability
Validate text presentation:
- Line length: 50-75 characters (up to 95 on screens)
- Line height: 1.4-1.6× font size (WCAG mandates ≥1.5×)
- Minimum body font: 16px (iOS 17pt, Material 16sp)
- Contrast: 4.5:1 AA, 7:1 AAA for normal text

### 6. Conversational & AI Interfaces
For chatbots, voice assistants, and AI-powered features:
- **Response time**: <1s for chat, <500ms for voice (300ms feels natural)
- **Typing indicators**: Effective for novice users only
- **Memory expectation**: 69% of users expect context retention
- **Human handoff**: 80% want option available (paradoxically increases chatbot engagement)
- **AI confidence display**: >=85% green, 60-84% yellow, <60% red
- **Hallucination warnings**: Labels alone don't induce skepticism

### 7. Search & Filtering
For search interfaces and faceted navigation:
- **Autocomplete timing**: <100ms feels instantaneous, >200ms feels laggy
- **Suggestion limits**: 8-10 desktop, 4-8 mobile (choice paralysis)
- **Position bias**: First result gets 27-40% of clicks, top 3 get 68.7%
- **Filter facets**: 5-7 maximum to avoid overwhelm
- **Zero-results**: 68% of sites have dead-end pages (provide alternatives)
- **Search conversion**: Searchers convert 2-3x higher than browsers

### 8. Onboarding & Empty States
For first-run experiences and empty states:
- **First impression**: Forms in 50ms, value proposition in 2.6s
- **Product tours**: 4 steps = 40.5% completion, 5 steps = 21% (near 50% drop)
- **Time-to-value**: Best SaaS achieves <5 minutes
- **Form fields**: 3 optimal, each additional loses conversions
- **Habit formation**: ~2 months average (not 21 days myth)
- **Empty states**: Always provide guidance, motivation, and next steps

### 9. Collaborative & Real-Time
For multiplayer and collaborative features:
- **Latency threshold**: <200ms for collaborative interactions
- **Presence indicators**: +47% productivity with workspace awareness (Gutwin & Greenberg)
- **Notification disruption**: Error rate 3x higher when receiving notifications; Gloria Mark: 23m 15s average recovery
- **Permission requests**: 12% higher grant rate when reason provided
- **Focus time**: Average 3 minutes before interruption

### 10. Error Handling & Validation
For form validation and error recovery:
- **Inline validation**: +22% success rate, -42% completion time
- **Validation timing**: After field blur, not during typing
- **Error position**: Next to field (minimizes working memory load)
- **Recovery paradox**: Post-recovery satisfaction can exceed error-free
- **Frustration**: 84% of frustrating episodes are recurring

## ⚠️ Myth-Busting Quick Reference

**ALWAYS check these before giving design advice.** Common claims that lack evidence:

| Myth | Status | Corrected Guidance |
|------|--------|-------------------|
| Skeleton screens +10-20% speed | **DEBUNKED** (Viget N=136: worst metrics) | Use progress bars with acceleration |
| Whitespace +20% comprehension | **DEBUNKED** (citation error, Lin denied) | Use 1.4-1.6× line height |
| Dyslexia fonts help reading | **DEBUNKED** (5 studies, BDA stance) | Use letter-spacing +18% instead |
| Red increases appetite | **DEBUNKED** (Schlintl N=448: no effect) | Color choices by brand/contrast |
| F-pattern is optimal layout | **OVERSTATED** (Pernice 2017: indicates poor design) | Design to PREVENT F-pattern |
| Dark mode = less eye strain | **CONTESTED** (4+ conflicting RCTs) | Provide both; #E0E0E0 on #121212 |
| Choice overload (jam study) | **CONTESTED** (99-study meta: near-zero) | Context-dependent on expertise |
| 7±2 memory limit | **OVERSTATED** (Cowan 2001: 4±1) | Design for 4±1 chunks |
| 21 days for habits | **DEBUNKED** (Lally 2010: ~66 days) | Design for 2+ months |
| Rainbow colormaps acceptable | **DEBUNKED** (Borkin: 52pp accuracy loss) | Use viridis/cividis |
| Confirmation dialogs prevent errors | **OVERSTATED** (habituation defeats) | Prefer undo pattern |
| Digital natives = tech-savvy | **DEBUNKED** (Kirschner 2017) | Design for all ages |
| Learning styles (VAK) | **DEBUNKED** (Pashler 2008: zero effect) | Multi-modal for everyone |

→ Full details: [myth-busting-evidence.md](references/myth-busting-evidence.md)

## Reference Files

### Core Reference Files

Consult these files for detailed research by domain:

| Domain | Reference File | When to Use |
|--------|---------------|-------------|
| Specific numbers | [quantified-thresholds.md](references/quantified-thresholds.md) | Need exact values |
| Perception laws | [perceptual-psychology.md](references/perceptual-psychology.md) | Audio, visual, time, probability perception |
| Memory & attention | [cognitive-architecture.md](references/cognitive-architecture.md) | Cognitive load, learning, flow |
| Keyboard/voice/pointer | [input-modalities.md](references/input-modalities.md) | Input device analysis |
| Typography & color | [typography-color.md](references/typography-color.md) | Visual design decisions |
| Checkout & conversion | [ecommerce-conversion.md](references/ecommerce-conversion.md) | E-commerce optimization |
| Security UX | [authentication-security.md](references/authentication-security.md) | Auth flows, warnings |
| Loading & notifications | [notification-performance.md](references/notification-performance.md) | Performance perception |
| WCAG & ethics | [accessibility-ethics.md](references/accessibility-ethics.md) | Accessibility, dark patterns |
| Cultural & age | [cultural-lifespan.md](references/cultural-lifespan.md) | Cross-cultural, age considerations |
| Code signals | [code-patterns.md](references/code-patterns.md) | Detection patterns in code |
| Mobile native UI | [mobile-native-ui.md](references/mobile-native-ui.md) | iOS/Android platform patterns |
| **Myth-busting** | [myth-busting-evidence.md](references/myth-busting-evidence.md) | **Verify any design claim; debunked/contested research** |
| **Enterprise & metrics** | [enterprise-measurement-psychology.md](references/enterprise-measurement-psychology.md) | **Enterprise UX, Goodhart's Law, pricing psychology, narrative UX** |

### Deep Research Reports

Extended research compilations with comprehensive findings, effect sizes, and sources:

| Topic | Research Report | Key Coverage |
|-------|----------------|--------------|
| AI/ML Interfaces | [ai-ml-interface-psychology.md](research-reports/ai-ml-interface-psychology.md) | Confidence indicators, XAI, hallucination handling, human-AI collaboration |
| Conversational UI | [conversational-ui-psychology-research.md](research-reports/conversational-ui-psychology-research.md) | Turn-taking, chatbot personality, error recovery, voice UI, trust |
| Data Visualization | [data-visualization-psychology.md](research-reports/data-visualization-psychology.md) | Chart types, perceptual encoding, color, animation, dashboards |
| Error Messages | [error-message-psychology.md](research-reports/error-message-psychology.md) | Tone, validation timing (+22% success), recovery, emotional impact |
| Gamification | [gamification-psychology-research.md](research-reports/gamification-psychology-research.md) | Points/badges/leaderboards, variable rewards, ethics, self-determination |
| Onboarding | [onboarding-empty-state-psychology.md](research-reports/onboarding-empty-state-psychology.md) | First-run UX, 50ms impressions, tutorial completion, habit formation |
| Search UX | [search-ux-psychology-research.md](research-reports/search-ux-psychology-research.md) | Query behavior, autocomplete (<100ms), position bias (27-40% CTR), filters |
| Collaborative UX | [collaborative-realtime-ux.md](research-reports/collaborative-realtime-ux.md) | Presence, cursors, social presence theory, latency (<200ms), sync state |
| VR/AR/XR | [vr-ar-xr-interface-psychology.md](research-reports/vr-ar-xr-interface-psychology.md) | Spatial UI, motion sickness, hand tracking, platform guidelines |

## Quick Detection Patterns

### Good Patterns (Evidence-Based)
```javascript
// Logarithmic volume scaling
volume = Math.pow(sliderValue, 2);
volume = Math.exp(b * sliderValue);

// Proper animation easing
transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);

// Quasi-random shuffle with spacing
shuffleWithSpacing(array, artistKey, minDistance);

// Haptic preparation for low latency
impactGenerator.prepare();
```

### Violation Indicators
```javascript
// Linear perceptual mapping (BAD)
volume = sliderValue;
animation: all 300ms linear;

// True random (feels broken)
array.sort(() => Math.random() - 0.5);

// Undersized touch targets
button.size = 32; // Below 44pt minimum

// Excessive form fields
fields.length > 14; // Optimal is 12-14
```

### Dark Pattern Signals
```html
<!-- Pre-selected consent -->
<input type="checkbox" checked name="marketing">

<!-- Unequal button hierarchy -->
<button class="primary large">Accept All</button>
<button class="text-only tiny gray">Manage</button>

<!-- Fake urgency -->
if (countdown === 0) countdown = 3600; // Resets!
```

## Evidence Quality Hierarchy

When citing findings, note evidence strength:

**STRONG** (replicated, large N, meta-analyses):
- Response time thresholds (100ms/1s/10s)
- Working memory 4±1 chunks
- Default effects (50-70 percentage points)
- Fitts's Law throughput
- First impression timing (50ms)
- Icon + label recognition (+28 percentage points)

**MODERATE** (peer-reviewed, limited replication):
- Progress bar perception (11% improvement)
- Skeleton screen effects (context-dependent)
- F-pattern (indicates poor design, not goal)

**DEBUNKED/WEAK**:
- Whitespace 20% comprehension (citation error)
- Dyslexia fonts (no benefit vs standard fonts with spacing)
- Learning styles matching (zero effect size)
- 38% opacity for disabled states (convention only)

## Output Format

When analyzing code, structure findings as:

1. **Critical Issues** - Violations likely causing user harm/friction
2. **Myth Alerts** - Flag any design decisions based on debunked claims (consult myth-busting-evidence.md)
3. **Opportunities** - Evidence-based improvements with expected effect size and study citation
4. **Good Practices** - Patterns that honor human psychology
5. **Research Gaps** - Areas lacking strong empirical backing; note replication status

**Always include**: specific thresholds, effect sizes (%, pp, Cohen's d), sample sizes (N=), p-values where available, and evidence status (STRONG/MODERATE/DEBUNKED).

## Integration with Other Skills

This skill provides the **research foundation ("why")** while UI/UX skills provide **structural frameworks ("how")**:

| Task | Use This Skill For | Combine With |
|------|-------------------|--------------|
| Component design | Interaction timing, cognitive load thresholds | ui-ux-mastery (component patterns) |
| Interface audit | Quantified issues, myth-busting, effect sizes | ui-ux-mastery-modular (domain matrices) |
| E-commerce checkout | Abandonment data, trust signal research | ui-ux-mastery-modular (conversion ethics) |
| Dashboard/data viz | Cleveland-McGill hierarchy, colormap research | ui-ux-mastery-modular (SaaS domain) |
| AI/chatbot interface | ELIZA effect, response timing, trust calibration | ui-ux-mastery (component patterns) |
| Research-backed argument | Peer-reviewed citations with N values and p-values | Any skill for implementation |

## Version History
- **v1**: 5 analysis domains, 11 reference files (original behavioral psychology skill)
- **v2**: +5 domains (AI, Search, Onboarding, Collaborative, Error), +1 reference (mobile-native-ui), +9 deep research reports
- **v3 (current)**: +2 references (myth-busting-evidence, enterprise-measurement-psychology), enhanced SKILL.md with myth-busting quick reference, integration guidance, improved description for better auto-triggering
