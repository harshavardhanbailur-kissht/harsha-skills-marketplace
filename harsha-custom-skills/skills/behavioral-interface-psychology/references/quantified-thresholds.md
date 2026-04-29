# Quantified Thresholds Reference

Quick reference for all empirically validated numbers, effect sizes, and benchmarks from peer-reviewed research. Numbers without citations are industry conventions, not validated research.

---

## Response Time Thresholds (Miller 1968, Nielsen 1993)

| Threshold | User Perception | Required Feedback |
|-----------|-----------------|-------------------|
| **<100ms** | Instantaneous | None needed |
| **100ms-1s** | Flow maintained | Activity indicator |
| **1-10s** | Attention at risk | Progress indicator |
| **>10s** | Task abandoned | Percent-done + estimate |

**Validation**: Forch et al. 2017 found latency perception thresholds: 34-137ms, mean 65ms.

---

## Core Web Vitals (Google)

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** | <2.5s | 2.5-4.0s | >4.0s |
| **INP** | <200ms | 200-500ms | >500ms |
| **CLS** | <0.1 | 0.1-0.25 | >0.25 |

### Business Impact (Documented Cases)
- Vodafone: LCP 31% faster → **8% sales increase**
- Lazada: LCP 3× faster → **16.9% mobile conversion increase**
- Akamai/SOASTA (N=10B visits): 100ms delay → **7% conversion decrease**
- Google (2017): 53% mobile visits abandoned if >3s load

---

## Frame Rate & Animation

| Metric | Value | Source |
|--------|-------|--------|
| Frame budget (60fps) | **16.67ms** | Physical constant |
| App work budget | ~10ms | Browser needs ~6ms |
| Acceptable dropped frames | 1-2% | Industry consensus |
| Animation duration | **200-400ms** | UX research |
| Easing function | `cubic-bezier(0.4, 0, 0.2, 1)` | Material Design |

### Input Latency Perception (Jota et al. 2013, CHI)
| Task | Threshold |
|------|-----------|
| Dragging | **1-7ms** |
| Scribbling | 7-40ms |
| Tapping | **40-64ms** |
| Typing | **20-30ms** |

---

## Touch Target Sizes

| Standard | Minimum Size | Notes |
|----------|-------------|-------|
| Apple iOS | **44×44pt** | ~7.7mm |
| Android Material | **48×48dp** | ~9mm |
| WCAG 2.5.8 (AA) | **24×24px** | With adequate spacing |
| WCAG 2.5.5 (AAA) | **44×44px** | Recommended |
| Spatial/VR | **60+pt** | Extended reach |

**Research**: Parhi et al. 2006 (MobileHCI) - 9.2mm minimum for acceptable error rates.
**MIT Touch Lab**: Average fingertip 10-14mm width.
**Error rates**: 15% at 24px vs 3% at 44px (5× difference).

---

## Fitts's Law Throughput

| Input Method | Throughput (bits/s) |
|--------------|---------------------|
| Direct touch (1D) | **7.52** |
| Touch (smartphone) | **6.95** |
| Mouse (typical) | **3.7-4.9** |
| Trackpad | **1.89-2.16** |

**Formula (Shannon)**: MT = a + b × log₂(D/W + 1)
**Edge/Corner Advantage**: Screen edges are "infinite depth" targets - ~5× faster (Tognazzini).
**Note**: Edge advantage does NOT apply to touchscreens.

---

## Cognitive Load & Memory

| Metric | Value | Source |
|--------|-------|--------|
| Working memory capacity | **4±1 chunks** | Cowan 2001 |
| Menu items (per level) | **8-16** | Hick's Law research |
| Navigation depth | **2-3 levels** | Norman & Chin 1988 |
| Form fields optimal | **12-14** | Baymard Institute |
| Context menu items | **5-10** | NNGroup |

### Navigation Error Rates
| Depth | Error Rate |
|-------|------------|
| 1 level | 4% |
| 6 levels | **34%** |

---

## Typography

| Metric | Value | Source |
|--------|-------|--------|
| Line length optimal | **50-75 characters** | Tinker; screens tolerate 80-95 |
| Line height | **1.4-1.6×** font size | WCAG mandates ≥1.5× |
| Minimum body font | **16px** | iOS 17pt, Material 16sp |
| All-caps reading speed | **10-19% slower** | Tinker |
| Font speed difference | **35%** between fastest/slowest | Wallace et al. 2022 (N=386+) |

### WCAG Contrast Requirements
| Type | AA | AAA |
|------|-----|-----|
| Normal text | **4.5:1** | **7:1** |
| Large text (≥18pt) | **3:1** | **4.5:1** |
| Non-text elements | **3:1** | - |

### APCA (WCAG 3.0 Candidate)
| Lc Value | Use Case |
|----------|----------|
| **Lc 90** | Preferred body text |
| **Lc 75** | Minimum body text |
| **Lc 60** | UI text, content text |
| **Lc 45** | Headlines |

---

## Typing Speed

| Population | Speed (WPM) | Source |
|------------|-------------|--------|
| Desktop average | **52** | Dhakal et al. 2018 (N=168,000+) |
| Mobile two-thumb | **38** | Palin et al. 2019 |
| Mobile one-thumb | **30** | Palin et al. 2019 |
| Hunt-and-peck | 27-37 | Dhakal et al. 2018 |
| Expert typists | **100+** | Various |
| Age 10-19 (mobile) | **39.6** | Palin et al. 2019 |
| Age 50-59 (mobile) | **26.3** | Palin et al. 2019 |

### Autocorrect vs Prediction
| Feature | Effect | Source |
|---------|--------|--------|
| Autocorrect | **+8.6 WPM** | Palin et al. 2019 |
| Word prediction | **-2.0 WPM** | Palin et al. 2019 |

---

## Voice Input

| Metric | Value | Source |
|--------|-------|--------|
| Voice vs typing speed | **3× faster** | Ruan et al. 2017 (Stanford) |
| English voice WPM | **153-161** | Ruan et al. 2017 |
| Critical latency threshold | **300-500ms** | Industry research |
| WER disparity (racial) | 19% (white) vs **35%** (Black) | Koenecke et al. 2020 (PNAS) |
| Privacy concern (public) | **78%** avoid in public | SecureDataRecovery |

---

## Progress Bar Psychology (Harrison et al. 2007, 2010)

| Finding | Effect |
|---------|--------|
| Accelerating progress | Perceived significantly faster |
| Backwards-moving ribbing | **11% perceived duration reduction** |
| Peak-end effect | Pauses near end dramatically worsen perception |

---

## E-commerce & Conversion

### Cart Abandonment (Baymard Institute, 50 studies)
- Average rate: **70.22%**
- Mobile: **85.7%**
- Recoverable losses: **$260 billion**

### Abandonment Causes
| Cause | Rate |
|-------|------|
| Extra costs (late reveal) | **48%** |
| Mandatory account creation | **19-26%** |
| Checkout too complex | **18-22%** |
| Didn't trust site | **19%** |

### Form Optimization
| Metric | Effect |
|--------|--------|
| Fields 22→14 | **20% conversion increase** |
| Phone number field | **48-52% conversion decrease** |
| Inline validation | **22% higher success, 42% faster** |

### Product Reviews (Spiegel, N=15.5M page views)
| Reviews | Effect |
|---------|--------|
| 5 reviews | **270% greater purchase likelihood** |
| Optimal rating | **4.0-4.7 stars** (5.0 triggers suspicion) |
| Photo reviews | **106.3% conversion lift** |

### Product Images (Di et al. 2014, eBay)
- 1 photo → doubles conversion
- 2 photos → doubles again
- >2 photos → diminishing returns

---

## Default Effect (Johnson & Goldstein 2003, Science)

| System | Registration Rate |
|--------|-------------------|
| Opt-out (presumed consent) | **85-100%** |
| Opt-in (explicit consent) | **4-27%** |

**Effect size**: 50-70 percentage points difference.

---

## Notification Psychology

| Metric | Value | Source |
|--------|-------|--------|
| Average daily notifications | **46** | CleverTap 2023 |
| Teen daily notifications | **240** | Michigan Medicine |
| Attention span on screen | **47 seconds** | Gloria Mark 2023 |
| Refocus after interruption | **~23 minutes** | Mark et al. (interview data) |
| Cognitive disruption | **~7 seconds** transient slowdown | PubMed Central |
| Optimal frequency | **≤3/week** | Engagement research |

### Intelligent Timing (Yahoo! JAPAN, N=680,000+)
- **49.7% improvement** in response time when delayed to interruptible moments.

### Permission Opt-in Rates
| Platform | Rate |
|----------|------|
| iOS | **51%** |
| Android 13+ | **67%** |
| Pre-permission prompts | **65%** vs 25-35% baseline |

---

## Icon Recognition

| Presentation | Accuracy | Source |
|--------------|----------|--------|
| Icon + label | **88%** | UX research |
| Icon only | **60%** | UX research |
| Unlabeled unique icons | **34%** | UX research |

**Universal icons** (near-universal recognition): Home, Print, Magnifying glass (search).

---

## Color Vision Deficiency

| Type | Prevalence (Males) |
|------|-------------------|
| All red-green | **~8%** |
| Deuteranomaly (weak green) | **~5%** |
| Protanomaly (weak red) | ~1% |
| Female prevalence | **~0.5%** |

---

## Authentication & Security

### Password Behavior
| Metric | Value | Source |
|--------|-------|--------|
| Reuse passwords | **78%** | Bitwarden 2024 |
| Password manager adoption | **36%** | Security.org 2024 |
| Recovery flow abandonment | **75%** | Stytch |
| Security questions failure | **40%** can't recall | Bonneau et al. (Google) |
| SMS recovery success | **>80%** | Google study |

### Passkeys
| Metric | Value | Source |
|--------|-------|--------|
| Consumer awareness | **57%** | FIDO Alliance 2024 |
| Sign-in success improvement | **30% higher** | Google |
| Speed improvement | **20% faster** | Google |

### 2FA Adoption
| Year | Rate |
|------|------|
| 2017 | 28% |
| 2021 | **79%** |

**Google auto-enrollment**: 50% reduction in compromised accounts.
**Microsoft MFA**: Blocks 99.9% of account compromise attacks.

---

## Security Warning Effectiveness

| Finding | Value | Source |
|---------|-------|--------|
| Padlock understanding | Only **11%** correct | Felt et al. 2016 (N=1,329) |
| SSL warning click-through | **70.2%** | Akhawe & Felt 2013 |
| Permission attention | Only **17%** | Felt et al. 2012 |
| Warning habituation | **Dramatic drop after 2nd exposure** | Anderson et al. 2015 |

---

## Digital Wellbeing

### "One Sec" App (Grüning et al. 2023, PNAS, N=280)
- **57% reduction** in unwanted app openings (6 weeks)
- **36%** of attempts dismissed after intervention
- **37% reduction** in overall opening attempts

---

## Cultural Variations

### High-Context vs Low-Context
| Culture | Information from Context |
|---------|-------------------------|
| Japanese users | **60%** (McLaren Group) |
| Western users | Much lower |

### Color Symbolism
| Region | Gains Color | Losses Color |
|--------|-------------|--------------|
| US/Europe | Green | Red |
| Japan/Korea/China | **Red** | **Green** |

---

## Lifespan Psychology

### Older Adults & Voice (JMIR mHealth 2021, age 74+)
- **90%** found voice assistants easy to learn/use
- Voice usage: health questions (38.9%), music (28.2%), directions (12.8%)

### Screen Time & Wellbeing (Twenge et al. 2018, N=40,337)
- 7+ hours/day: **2.4× more likely** to be diagnosed with depression

---

## Research Debunked

| Claim | Reality |
|-------|---------|
| Whitespace +20% comprehension | Citation error - not validated |
| Dyslexia fonts help reading | **No benefit** (Wery & Diliberto 2017, Kuster et al. 2018) |
| Learning styles matching | **Zero effect size** (Pashler et al. 2009) |
| "Red makes you hungry" | Contradicted (Schlintl & Schienle 2020, N=448) |
| Baker-Miller pink reduces aggression | Failed replication (Genschow et al. 2015) |
| Pink-blue gender preferences innate | Culturally learned (Davis et al. 2021, N=232) |

---

## Evidence Quality Tiers

### STRONG (Replicated, Large N, Meta-analyses)
- Response time thresholds (100ms/1s/10s)
- Working memory 4±1 chunks
- Default effects (50-70 pp)
- Fitts's Law throughput
- First impression timing (50ms)

### MODERATE (Peer-reviewed, Limited Replication)
- Progress bar perception (11%)
- Icon + label advantage (28 pp)
- Skeleton screen effects (context-dependent)

### WEAK/ABSENT
- Typography scale ratios (no empirical validation)
- 38% opacity for disabled states (convention only)
- Tooltip delay 300-500ms (practitioner guidance)
