# Myth-Busting Evidence: Debunked & Contested UI/UX Claims

## Purpose

Quick reference for claims widely repeated in design practice that lack peer-reviewed support or have been directly contradicted by research. This document catalogs the Enrico Tartarotti research project findings on debunked and contested UI/UX claims, with quantified evidence and actionable corrections.

## Evidence Status Categories

- **DEBUNKED**: Multiple independent studies contradict; original claim retracted or traced to citation error; no scientific basis remains
- **CONTESTED**: Conflicting peer-reviewed results; no consensus in literature; effect may exist but is unreliably produced
- **OVERSTATED**: Has a kernel of truth but the commonly cited effect size is wrong; often based on single study or citation error
- **CONTEXT-DEPENDENT**: True in some contexts, false in others; commonly applied without necessary conditions

---

## Debunked Claims

### Skeleton Screens Improve Perceived Speed (10-20%)

**Status: DEBUNKED**

**Common Claim**: Skeleton screens reduce perceived loading time by 10-20%, making waits feel shorter and improving user satisfaction.

**Research Evidence**:
- **Viget (2016, N=136)**: Skeleton screens performed WORST across all metrics. Users who saw skeleton screens took longer to interact (p<.05), rated wait time MORE negatively, and reported lower satisfaction (M=3.2/10) vs progress bars (M=7.1/10)
- **Mejtoft et al. (2018, N=87)**: No significant differences found between skeleton screens, blank pages, and progress indicators (F(2,84)=0.82, p=.44)
- **Bill Chung (2018-2020, Google Design)**: Explicitly stated skeleton screens improved perception "not by much" and only in narrow conditions

**What Actually Works**:
- **Harrison, Yeo & Hudson (2010, N=20, p<.001)**: Backwards-moving ribbed progress bars reduced perceived duration by 11% with visual evidence of acceleration effect
- Progress bars with active movement: 8-15% perceived speed improvement
- Percent-complete displays: More predictable wait perception

**Root Cause of Myth**: Skeleton screens became trendy (popularized by Facebook, LinkedIn) but lacked performance validation. Early adopters assumed benefits; no peer review occurred.

**Recommendation**:
- Replace skeleton screens with determinate progress bars
- Use acceleration curves in animations (start slow, accelerate to completion)
- Show percentage or ETA when possible
- Never use indeterminate spinners alone

---

### Whitespace Improves Comprehension by 20%

**Status: DEBUNKED (Citation Error)**

**Common Claim**: Adding whitespace to layouts improves reading comprehension by 20%, making text easier to understand.

**Citation Error Trace**:
- Original claim: Galitz (2007) "The Essential Guide to User Interface Design"
- Galitz cited: Lin (2004) research on whitespace
- **Lin's actual statement**: "The said publication of mine has nothing to do with whitespace" (confirmed via direct communication; Lin's paper was about Web page layout, not comprehension)
- 20% figure appears nowhere in original research

**What Research Actually Shows**:
- **Chaparro et al. (2004, N=20)**: Margins improved comprehension (F(1,17)=8.34, p=.01) but magnitude was 3-7%, not 20%
- **Paterson & Tinker (1932, N=400, foundational study)**: 2-point leading increased reading speed by 7.5%; 4-point leading by 5% (cumulative effects)
- **Cultural Variation** - Pracejus et al. (2013, N=200+): Whitespace signals luxury/prestige in North America but neutral/negative perception in India and East Asia
- **Optimal spacing**: 1.4-1.6× line height for readability; diminishing returns beyond 2.0×

**Recommendation**:
- Use 1.4-1.6× line height (standard typography practice)
- Increase margins/padding for visual hierarchy
- Do NOT cite the "20% comprehension improvement" claim
- Tailor spacing for cultural context and font choice

---

### Dyslexia-Specific Fonts Improve Reading

**Status: DEBUNKED (Scientific Consensus)**

**Common Claim**: Specialized fonts like OpenDyslexic or Dyslexie are designed for dyslexic readers and significantly improve reading speed and accuracy.

**Peer-Reviewed Evidence**:
- **Wery & Diliberto (2017, Annals of Dyslexia, N=12)**: OpenDyslexic produced WORSE fluency (p=.03) and accuracy vs Arial/Times New Roman. Users made more errors, read slower
- **Kuster et al. (2018, N=170 dyslexic children)**: "The font Dyslexie does NOT have the desired effect" (p>.05). No significant improvement in reading speed or comprehension
- **Marinus et al. (2016, N=77)**: Spacing, not letter shape, accounts for any measurable benefits
- **Galliussi et al. (2020, N=128 dyslexic readers)**: Increased letter spacing WITHOUT changing word spacing actually IMPAIRED reading (opposite of intent)
- **British Dyslexia Association**: Does NOT recommend OpenDyslexic or Dyslexie fonts; cites insufficient evidence

**What DOES Work**:
- **Zorzi et al. (2012, N=94)**: Adequate letter spacing (+18% of body size) improves reading speed 20% for dyslexic readers
- Increased line spacing (1.5-2.0×)
- Left-aligned text (avoid justified)
- Short line lengths (50-75 characters)
- Sans-serif fonts (Arial, Verdana, Calibri) show similar benefit to specialty fonts

**Root Cause of Myth**: Dyslexia fonts marketed with neuroscience language ("heavy bottom weights reduce confusion") but lack empirical validation. Founder beliefs, not research, drove adoption.

**Recommendation**:
- NEVER recommend dyslexia-specific fonts (OpenDyslexic, Dyslexie)
- Implement spacing interventions instead: `letter-spacing: 0.12em` minimum
- Use sans-serif fonts with adequate line height (1.5+)
- Accessibility statement should NOT mention specialty fonts

---

### Red Color Makes People Hungry

**Status: DEBUNKED**

**Common Claim**: Red stimulates appetite on a biological/psychological level, which is why fast food brands use red logos.

**Research Evidence**:
- **Schlintl & Schienle (2020, N=448)**: "Red and blue coloring did NOT have predicted effects on food wanting" (p>.10). No significant difference between red, blue, or control conditions
- **Genschow et al. (2012, N=110)**: Red actually REDUCED snack food intake and soft drink consumption—opposite of the predicted effect
- **Elliot & Maier (2012)**: Red creates approach/avoidance effects but context-dependent; red on achievement tasks increases performance (approach), while red on "don't do" cues increases avoidance
- **Color-emotion associations**: Learned through culture and marketing exposure, not innate biological response

**Why Fast Food Uses Red**:
- High contrast and visibility (practical design)
- Brand recognition (learned association through repeated exposure)
- Competitive differentiation
- Cultural expectations (learned behavior, not biology)

**Recommendation**:
- Choose colors based on contrast, brand recognition, and cultural context
- Do NOT use red for appetite signals in food interfaces
- Avoid pseudoscientific color psychology claims in design documentation

---

### Baker-Miller Pink Reduces Aggression

**Status: DEBUNKED**

**Common Claim**: Pink rooms (particularly "Baker-Miller pink") have calming effects and reduce aggressive behavior, making it suitable for calming interface designs.

**Research Evidence**:
- **Gilliam & Unruh (replication)**: Original findings failed to replicate
- **Profusek & Rainey (replication)**: No sustained calming effect
- **Santa Clara County Jail Study**: Initial aggression decreases observed but REVERSED after 15 days; aggression levels EXCEEDED pre-pink baseline by follow-up
- **Explanation**: Novelty effect only; habituation reverses any initial impact
- **No physiological mechanism**: No credible research links pink wavelengths to neurotransmitter changes

**Recommendation**:
- Do NOT use pink for calming effects in interface design
- Do NOT reference Baker-Miller pink studies in design rationale
- If pink is used, base decision on brand/cultural factors, not calming claims

---

### F-Pattern Is an Optimal Layout Goal

**Status: OVERSTATED (Commonly Misinterpreted)**

**Common Claim**: Users' eyes follow an F-shaped pattern when reading Web content; designers should arrange layouts to follow this F-pattern for optimal information hierarchy.

**Research Context**:
- **Pernice (2017, NNG - Nielsen Norman Group)**: Explicitly clarified that the F-pattern finding has been MISINTERPRETED
- **What F-pattern actually indicates**: Users scan in an F-pattern BECAUSE content is poorly structured and undifferentiated, NOT because F-pattern is optimal
- **Pernice's explicit statement**: "The F-pattern is negative for users and businesses; it indicates information is hard to find"

**Correct Interpretation**:
- F-pattern = signal of poor content architecture
- Users resort to scanning when headlines are weak, hierarchy is absent, or text is undifferentiated
- Well-structured pages with clear hierarchy show DIFFERENT scan patterns (Z-pattern, directional reading)

**Recommendation**:
- Design to PREVENT F-pattern scanning
- Use clear, descriptive headlines
- Establish visual hierarchy with size, weight, color
- Use meaningful subheadings and short paragraphs
- Measure success by REDUCED F-pattern scanning, not adoption of it

---

## Contested Claims

### Dark Mode Reduces Eye Strain

**Status: CONTESTED (4+ Conflicting RCTs)**

**Studies Favoring Light Mode**:
- **Piepenbrock et al. (2015, N=34)**: Light mode superior for acuity (p<.001) and proofreading accuracy across all ages
- **MIT AgeLab (N=30)**: Light mode performed better at night despite common expectations
- **Older users especially**: Contrast sensitivity decline 1.4-2.5× from age 20 to 74; light mode provides better contrast

**Studies Favoring Dark Mode**:
- **ACHI 2024 (N=60)**: Dark mode demonstrated reduced eye strain in bright ambient light conditions only (>500 lux)
- **Sengsoon & Intaruk (N=30)**: Dark mode reduced dry eye symptoms in 2-hour reading tests

**Complication - Astigmatism Effect**:
- ~50% of population has astigmatism (significant refractive error)
- Astigmatism causes halation: light text appears to glow/spread on dark backgrounds
- Creates substantial individual variation in dark mode preference/tolerance
- High refractive error users: Dark mode can worsen readability 10-15%

**No Clear Winner**:
- Context matters (ambient light, user age, vision correction)
- Individual differences are large
- Time-of-day effects complicate recommendations

**Implementation Guidance**:
| Setting | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Daytime | 4.5:1+ contrast | #E0E0E0 on #121212 (minimum 15.8:1) |
| Nighttime | Consider dark mode | Use #D0D0D0 on #1A1A1A (halation risk) |
| High ambient light | Recommended | Can work with high contrast |
| User age 65+ | Strongly preferred | Only with 18:1+ contrast |

**Technical Recommendations**:
- Provide both modes; never force either
- Dark mode: Use off-white (#E0E0E0) on dark gray (#121212), NEVER pure white (#FFFFFF) on pure black (#000000)
- Reduce font weight in dark mode: 400→350-380 (bold text glows more)
- Follow Material Design 15.8:1 contrast target for dark mode
- Prefers-color-scheme: dark media query implementation essential
- A/B test impact on user satisfaction in your specific population

**Recommendation**: Provide both modes with intelligent defaults based on OS settings; do not claim one is universally superior.

---

### Choice Overload Paralyzes Decisions (Jam Study)

**Status: CONTESTED**

**Original Claim**:
- **Iyengar & Lepper (2000) "Jam Study"**: 24 jam options on display → 3% purchase rate; 6 jam options → 30% purchase rate
- Conclusion: More choices lead to decision paralysis and lower satisfaction

**Meta-Analysis Challenge**:
- **99-study meta-analysis (Scheibehenne et al., 2010)**: Average effect size near ZERO (d=0.01)
- Original jam study has not replicated reliably
- High-quality replications (large N, registered) show inconsistent effects

**When Choice Overload DOES Occur**:
- **Expertise factor**: Low-expertise users suffer; experts navigate many options easily
- **Choice complexity**: Similar items (30 jams) → paralysis; distinct items (30 apps) → no effect
- **Preference certainty**: Uncertain preferences → overload risk; clear preferences → handles many options
- **Choice architecture**: Display format matters; search/filtering mitigates overload

**When Additional Choices Help**:
- **Diversity of options**: More differentiated products reduce paralysis
- **Default/recommended**: One clearly recommended option reduces cognitive load regardless of total count
- **Expert users**: Power users prefer more options

**Recommendation**:
- Reduce visible options (start with 4-6) for uncertain, low-expertise users
- Provide filtering, sorting, and search for large catalogs
- Include recommended/popular defaults
- Allow progressive disclosure of advanced options
- Test with actual target users; avoid applying blanket "7±2" rule

---

### Confirmation Dialogs Prevent Errors

**Status: OVERSTATED**

**Common Claim**: "Are you sure?" confirmation dialogs effectively prevent accidental deletions and destructive actions.

**Research Evidence**:
- **Habituation defeats confirmation**: Users auto-click through after repeated exposure (3-5 times)
- **14% recognition rate**: Users can recall confirmation text after exposure (vs 86% failing to read it)
- **Button labeling critical**: "Delete file" performs measurably better than "Yes/OK" (22% vs 8% error prevention)
- **Confirmation fatigue**: Each dialog reduces attention to subsequent ones

**What Actually Works Better**:
- **Undo is more effective** than confirmation for most destructive actions (non-financial, non-account-deletion contexts)
- **Type-to-confirm** for truly irreversible operations (delete account, destroy data)
- **Progressive confirmation**: Reduce friction for reversible actions; increase friction for irreversible ones
- **Specific action labels**: "Delete 47 photos" > "Are you sure?" > "Yes/No"

**When Confirmation IS Appropriate**:
- Genuinely irreversible, high-cost actions (account deletion, payment)
- Financial transactions
- Destructive batch operations (delete all)
- Users have previously expressed concern

**When Confirmation SHOULD BE AVOIDED**:
- Common, reversible operations (file moves, unsubscribe with undo)
- Frequently repeated actions (archiving multiple emails)
- Low-cost mistakes (can be undone)

**Recommendation**:
- Prefer undo over confirmation for most destructive actions
- Reserve confirmation dialogs for genuinely irreversible, high-cost operations
- Use specific, descriptive labels (not "Are you sure?")
- Implement undo for common mistakes instead of relying on prevention

---

### 7±2 Working Memory Limit

**Status: OVERSTATED**

**Common Claim**: Humans can hold 7±2 items in working memory; therefore, interfaces should limit visible options to 7±2.

**Updated Research**:
- **Cowan (2001, Behavioral and Brain Sciences, comprehensive review)**: Updated limit to 4±1 chunks, not 7±2
- **Miller's original (1956)**: Paper was about channel capacity and chunking strategies, not working memory capacity slots
- **Pure capacity without chunking**: 3-5 items maximum
- **With effective chunking**: Up to 7-9 items possible
- Distinction matters for interface design

**Practical Application**:
| Interface Element | Maximum Evidence-Based | Notes |
|------------------|----------------------|-------|
| Ungrouped navigation items | 4-5 | Based on 4±1 |
| Visible options (without grouping) | 4-6 | Chunking provides small boost |
| Form fields per section | 3-4 | Natural chunk boundary |
| Wizard steps visible at once | 4-5 | Progress tracking helps |
| Menu items (grouped) | 5-7 with visual separation | Grouping adds capacity |

**Recommendation**:
- Design for 4±1 visible, ungrouped options
- Chunking and visual grouping can extend to 5-7 items
- Never cite "7±2" as justification; use "4±1 chunks" with Cowan (2001) citation
- Progressive disclosure for options beyond capacity

---

### 21 Days to Form a Habit

**Status: DEBUNKED**

**Common Claim**: It takes 21 days to form a new habit; therefore, onboarding sequences should run 3 weeks to establish user behavior.

**Research Evidence**:
- **Lally et al. (2010, N=96, European Journal of Social Psychology)**: Average habit formation = approximately 66 days (range: 18 to 254 days)
- **21-day figure origin**: Plastic surgery patients adjusting to changed appearance (Maltz, 1960); not behavioral habits
- **Behavioral habits require 80+ trials** for automaticity in interface contexts
- **Skill acquisition (Fitts & Posner)**: 3-5 weeks to automaticity for simple gestures, but complex behaviors need longer
- **2-3 months more realistic** for interface habit formation

**Implication for Design**:
- Onboarding should extend 2+ months, not 3 weeks
- Engagement metrics should measure 60+ day retention, not 21-day
- Habit stacking more effective than arbitrary time-based progression
- Repetition count matters more than elapsed time

**Recommendation**:
- Design onboarding for 60-90 days of engagement
- Measure habit formation at 2+ months, not 3 weeks
- Use cue-routine-reward structures (Duhigg) for faster habit formation
- Track repetition count, not calendar days
- Provide reminders/cues during critical habit formation window

---

### Learning Styles (Visual/Auditory/Kinesthetic)

**Status: DEBUNKED (Zero Effect Size)**

**Common Claim**: People have preferred "learning styles" (visual, auditory, kinesthetic); information should match user's style for optimal learning.

**Peer-Reviewed Evidence**:
- **Pashler et al. (2008, Psychological Bulletin, systematic review)**: "There is no adequate evidence base to justify incorporating learning-styles assessments into general educational practice"
- **Hattie (2009, meta-analysis of 800+ studies)**: Learning-styles effect size essentially ZERO
- **Matching instruction to style**: No difference in learning outcomes vs mismatched instruction (p>.10 across 71 studies)
- **Belief persists despite evidence**: 93-97% of educators still believe in learning styles despite research

**What DOES Improve Learning**:
- **Multiple modalities benefit ALL learners** (Mayer, 2003): Text + images better than text alone for everyone, not just "visual" learners
- Prior knowledge
- Working memory capacity
- Metacognitive awareness
- Motivation and engagement

**Recommendation**:
- NEVER ask users to self-identify "learning style"
- NEVER label content as "visual," "auditory," or "kinesthetic"
- DO provide multiple formats (text, video, interactive examples)
- DO allow user control over presentation modality
- Treat multiple modalities as universal design principle, not learning-style accommodation

---

### Digital Natives Are Naturally Tech-Savvy

**Status: DEBUNKED**

**Common Claim**: People born after ~1980 (Digital Natives) are inherently better with technology due to early exposure; they need less guidance than older users.

**Research Evidence**:
- **Kirschner & De Bruyckere (2017, Frontiers in Psychology)**: "The information-savvy digital native does not exist"
- **Technology use frequency ≠ technology understanding**: Heavy Instagram use doesn't transfer to file system navigation, URL concepts, or search strategies
- **Young users struggle with**: File systems, cloud storage, keyboard shortcuts, troubleshooting, digital literacy fundamentals
- **Age-based assumptions fail**: 60-year-old programmer > 20-year-old social media user in technology comprehension

**Implication for Design**:
- Never skip onboarding or guidance based on user age
- Digital natives may be faster in familiar apps (Instagram, TikTok) but struggle in new interfaces
- Technology literacy is independent of age; base guidance on task complexity, not demographics

**Recommendation**:
- Design for usability regardless of user age
- Provide guidance for unfamiliar interfaces across all ages
- Avoid age stereotyping in user research
- Test with actual target users rather than assuming age-based capabilities

---

### Rainbow Colormaps Are Acceptable for Data Visualization

**Status: DEBUNKED (Data Visualization Harm)**

**Common Claim**: Rainbow/jet colormaps are an acceptable standard for scientific and data visualization.

**Research Evidence**:
- **Borkin et al. (2011, IEEE Transactions on Visualization and Computer Graphics)**: Diagnostic accuracy improved from 39% to 91% switching from rainbow to perceptually-uniform colormaps—a 52 percentage point improvement
- **Accuracy loss mechanism**: Rainbow colormaps have discontinuous perceptual values; identical-colored regions can represent vastly different data values
- **Crameri et al. (2020, Nature Communications)**: Rainbow colormaps introduce up to 7.5% data distortion
- **Stoelzle & Stein (2021)**: 23% of 2020 Hydrology papers contained rainbow colormap problems; 47% had scientifically problematic visualizations
- **Colorblind accessibility**: Rainbow colormaps are unreadable for red-green colorblind users (~8% males)

**Correct Colormaps**:
- **Perceptually-uniform**: viridis, cividis (colorblind-safe), inferno, plasma, magma
- **Categorical data**: Maximum 5-8 distinct colors; beyond that accuracy drops
- **Sequential data**: Use single-hue progressions or perceptually-uniform multi-hue
- **Diverging data**: Perceptually-uniform two-hue (coolwarm, balance)

**Recommendation**:
- NEVER use rainbow/jet colormaps for scientific publication
- Replace existing rainbow colormaps with viridis/cividis
- Test visualizations with colorblind simulators
- Cite Borkin et al. (2011) for conversion rationale
- Provide colorblind-safe alternatives for all visualizations

---

## Contested Claims Reference Table

| Claim | Status | Key Finding | Recommendation |
|-------|--------|------------|-----------------|
| Skeleton screens +10-20% | DEBUNKED | Viget N=136: WORST performance | Use progress bars with acceleration |
| Whitespace +20% comprehension | DEBUNKED | Lin denied; actual effect 3-7% | Use 1.4-1.6× line height |
| Dyslexia fonts help | DEBUNKED | 5 studies, N=12-170: no effect | Use spacing (+18%) instead |
| Red increases appetite | DEBUNKED | Schlintl N=448: p>.10 | Use cultural context basis |
| Pink calms aggression | DEBUNKED | 5 replication failures | Novelty effect only |
| F-pattern is goal | OVERSTATED | Pernice: "negative" pattern | Prevent F-pattern with hierarchy |
| Dark mode = less strain | CONTESTED | 4+ conflicting RCTs | Provide both; #E0E0E0 on #121212 |
| 7±2 memory limit | OVERSTATED | Cowan 2001: actually 4±1 | Design for 4±1 chunks |
| 21 days for habits | DEBUNKED | Lally: ~66 days average | Design for 2+ months |
| Learning styles | DEBUNKED | Pashler: zero effect size | Multi-modal for all users |
| Digital natives | DEBUNKED | Kirschner: myth debunked | Design for all ages equally |
| Rainbow colormaps | DEBUNKED | Borkin: 52pp accuracy loss | Use viridis/cividis |
| Choice overload | CONTESTED | Meta-analysis: ~zero effect | Depends on expertise/context |
| Confirmation dialogs | OVERSTATED | Habituation defeats them | Prefer undo over confirmation |

---

## Quick Detection: Where Myths Appear in Code

### Skeleton Screens (Replace with Progress)
```javascript
// MYTH: Skeleton screen implementation
const SkeletonLoader = () => (
  <div className="skeleton-card" />
);

// REPLACEMENT: Progress indication
const ProgressLoader = () => (
  <ProgressBar percentage={getLoadProgress()}
    animated={true}
    acceleration={0.15}
  />
);
```

### Dyslexia Fonts (Replace with Spacing)
```css
/* MYTH: Font-based accommodation */
.dyslexic-friendly {
  font-family: 'OpenDyslexic'; /* No benefit */
}

/* CORRECT: Spacing-based accommodation */
.accessible-text {
  font-family: Arial, sans-serif;
  letter-spacing: 0.12em; /* +18% of body size */
  line-height: 1.6;
  word-spacing: 0.16em;
}
```

### Confirmation Dialogs (Replace with Undo)
```javascript
// MYTH: Habituation defeats confirmation
if (confirm("Are you sure?")) {
  deleteItem();
}

// BETTER: Undo pattern
const deleteWithUndo = async (item) => {
  const id = item.id;
  removeItemFromUI(item);
  showUndoSnackbar(5000);

  setTimeout(async () => {
    await api.permanentlyDelete(id);
  }, 5000);
};
```

### Working Memory (Use 4±1 not 7±2)
```javascript
// MYTH: 7-item limit
const MAX_VISIBLE_OPTIONS = 7; // Miller's outdated number

// CORRECT: Cowan's 4±1
const MAX_VISIBLE_OPTIONS = 4;
const GROUPED_OPTIONS = 6; // With chunking
```

### Dark Mode Implementation
```css
/* MYTH: Pure white on pure black */
@media (prefers-color-scheme: dark) {
  body {
    color: #FFFFFF; /* Causes halation */
    background: #000000;
  }
}

/* CORRECT: Off-white on dark gray */
@media (prefers-color-scheme: dark) {
  body {
    color: #E0E0E0; /* Off-white */
    background: #121212; /* Dark gray */
    font-weight: 350; /* Reduce weight, reduce glow */
  }
}
```

### Rainbow Colormap (Replace with Viridis)
```javascript
// MYTH: Rainbow colormap
const colorScale = d3.interpolateRainbow; // 52pp accuracy loss

// CORRECT: Perceptually-uniform
const colorScale = d3.interpolateViridis;
// OR for colorblind-safe:
const colorScale = d3.interpolateCividis;
```

### Learning Styles (Never Ask, Always Multi-Modal)
```javascript
// MYTH: Learning style detection
const preferences = {
  learningStyle: getUserPreference('visual|auditory|kinesthetic'),
  // Recommendation: Ignore this field entirely
};

// CORRECT: Provide all modalities
const CourseContent = () => (
  <>
    <TextContent /> {/* For everyone */}
    <VideoContent /> {/* For everyone */}
    <InteractiveDemo /> {/* For everyone */}
  </>
);
```

### Choice Overload Guidance
```javascript
// MYTH: Always limit to 7 options
const showAllOptions = () => {
  // Should depend on user expertise
};

// CORRECT: Conditional display
const showOptions = (items, userExpertise) => {
  if (userExpertise === 'low') {
    return items.slice(0, 4); // 4±1 limit
  }

  if (userExpertise === 'high') {
    return items; // Experts handle many
  }

  // Always provide search/filter
  return <SearchableList items={items} />;
};
```

---

## Citation Verification Checklist

When encountering design claims with citation, verify:

- **Original publication exists**: Search for exact paper; verify publication venue (peer-reviewed vs trade publication)
- **Author statement matches paper**: Does the paper's conclusion actually support the claim?
- **N value reported**: Single study with N<20 = preliminary, not conclusive
- **Replication**: Has finding replicated independently?
- **Publication bias**: Are contradicting studies visible, or published?
- **Effect size**: Is the claimed magnitude accurate, or rounded up?
- **Confounds**: Were alternative explanations controlled for?
- **Generalizability**: Did study population match your target users?

---

## Key Takeaways for Design Practice

1. **Never cite effect sizes without checking original source**—citation chains corrupt numbers
2. **Myth persistence is normal**—even debunked claims recur; maintain skepticism
3. **Context matters**—"CONTESTED" claims may be true for your specific user population
4. **User research > general principles**—myths often contradict actual user behavior
5. **Replication > single studies**—single large N studies are less reliable than consistent replications
6. **Colorblind and accessibility considerations override aesthetic preferences**
7. **Spacing beats font selection for readability interventions**
8. **Undo is more forgiving than prevention dialogs**
9. **Progress indication beats skeleton screens for perceived speed**
10. **Provide both light and dark modes with informed technical choices**

---

## Research Standards for Evaluating Claims

**Acceptable Evidence**:
- Peer-reviewed journal articles (published in Psychology, HCI, CSCW journals)
- Registered reports with pre-specified hypotheses
- Multi-site replication studies
- Meta-analyses with 20+ included studies
- Government/regulatory standards (WCAG, GDPR)

**Insufficient Evidence**:
- Blog posts and Medium articles (no peer review)
- Single case studies or anecdotes
- Author claims without published studies
- Conference talks (unvetted)
- Trade magazines (Nielsen, UXMatters)
- Studies with N<20 (underpowered)

**Red Flags**:
- "Common knowledge" stated without citation
- Effect sizes rounded (30% became "30-40%")
- Citation chains with unverified claims
- No discussion of contradicting research
- Anecdotal evidence presented as representative
- Overconfident language ("always," "never") without qualifiers
