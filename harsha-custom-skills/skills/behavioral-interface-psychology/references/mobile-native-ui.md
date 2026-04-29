# Mobile Native UI Psychology Reference

Comprehensive research on platform-specific mobile patterns, iOS (SwiftUI/UIKit) and Android (Jetpack Compose/Material Design) guidelines, with empirically validated thresholds and effect sizes.

---

## Platform Expectation Differences

### iOS vs Android Mental Models

**Brand Perception** (PMC, Frontiers in Psychology 2023):
| Platform | Brand Image | User Expectation |
|----------|-------------|------------------|
| iOS | "Consistency, convenience, security" | Streamlined, simple, predictable |
| Android | "Diversification, personalization, freedom" | Customizable, flexible, open |

**Navigation Paradigm Differences**:
| Pattern | iOS | Android |
|---------|-----|---------|
| Primary navigation | Bottom tab bar | Bottom navigation OR navigation drawer |
| Back navigation | Edge swipe gesture | System back button + predictive back |
| Notification handling | Auto-disappear | Persist until action |
| Customization | Limited, consistent | Extensive (widgets, launchers) |

### Back Button Behavior

**Android Predictive Back Gesture** (Android 13+):
- Users preview destination before completing back gesture
- Reduces accidental app exits
- Required opt-in from Android 15 for system animations
- User preference: Strong desire to know where back gesture leads

**iOS Back Gesture**:
- Edge swipe from left universally expected
- Deeply ingrained in muscle memory
- Apps violating this pattern face user frustration

### Tab Bar vs Navigation Drawer

**NNGroup Research** (N=179 participants, 6 sites):
| Navigation Type | Discoverability | Task Completion |
|-----------------|-----------------|-----------------|
| Visible (tab bar) | Baseline | Baseline |
| Hidden (hamburger) | **-20%+ drop** | Significantly worse |
| Combo | Moderate | Moderate |

**Engagement Impact** (Industry Case Studies):
- Redbooth: Hamburger → Tab bar = **65% increase in DAU**, **70% increase in session time**
- Zeebox: Tab bar → Hamburger = Sharp engagement drop

**Design Recommendation**:
- Use bottom tab bar for 3-5 top-level destinations
- Reserve hamburger menu for secondary/settings navigation
- Research shows 72% of users prefer easily accessible options in main view

### Platform Switcher Adaptation

**Learning Curve Research**:
- iPhone users search **58% more** on Google for basic function instructions
- Many iOS users struggle with: voicemail setup, app removal, location sharing
- iOS-to-Android and Android-to-iOS both present learning curves
- Adaptation time: Variable, but most users adapt within weeks with regular use

---

## iOS-Specific Patterns

### Swipe Gestures

**User Expectations** (UX Research):
- Left/right swipes for page transitions: **Universal expectation**
- Swipe-from-left to go back: **Muscle memory ingrained**
- Swipe gestures mirror physical actions (flipping pages, sliding)

**Swipe Gesture Awareness**: 18-85% (highly variable based on context)

**Design Implications**:
- Hidden gestures are accessibility barriers
- Always provide visible alternatives
- Dynamic guides reduce error rate: **43% → 27%** (37% improvement)

### Pull-to-Refresh

**History & Adoption**:
- Invented by Loren Brichter for Tweetie (2008)
- Now universal - users implicitly expect it in:
  - Social feeds
  - Email apps
  - News apps
  - Lists sorted by recency

**Appropriate Use Cases**:
- Content sorted by recent/time-based ordering
- NOT appropriate for: non-ordered lists, static content, search results

### Dynamic Type Adoption

**WHO Projection**: 2.7 billion people with visual impairment by 2025

**Implementation Status**:
- iOS 7: Initial introduction (difficult with custom fonts)
- iOS 11+: Easy implementation with custom fonts via UIFontMetrics
- SwiftUI: Automatic support with system text styles

**User Impact**:
- Body text sizes can scale over **300%**
- Research indicates **20-25% increase in user retention** for accessible projects
- Common developer failure: Not testing at largest accessibility sizes

**Apple Accessibility Evaluation Criteria**:
- App Store now evaluates apps for larger text support
- Text must remain readable and usable at all Dynamic Type sizes

### iOS Haptic Feedback Guidelines

**Apple's Three Guiding Principles**:
1. **Causality**: Feedback must clearly relate to triggering action
2. **Harmony**: Haptics complement visual/audio feedback
3. **Utility**: Haptics serve functional purpose

**UIFeedbackGenerator Types**:
| Type | Use Case |
|------|----------|
| `.impact` (light/medium/heavy) | Physical collisions, UI interactions |
| `.selection` | Picker scrolling, segment changes |
| `.notification` (success/warning/error) | Task completion states |

**Timing Thresholds**:
| Parameter | Value |
|-----------|-------|
| Maximum latency | **<50ms** |
| Minimum pulse duration | 25-30ms |
| Minimum inter-pulse gap | 15-20ms |

**Distinguishable Patterns**: 5-9 maximum (Azadi et al. 2014)

**Accessibility Benefit**:
- Blind/low-vision users: Vital non-visual confirmation
- Deaf/hard-of-hearing: Alternative to audio alerts

### Sheet Presentation Psychology

**Bottom Sheet Advantages** (NNGroup Research):
- **25-30% higher engagement** than traditional modals
- Less intrusive, easier to dismiss
- Preserves visibility of underlying content

**Modal vs Non-Modal**:
| Type | Behavior | Best For |
|------|----------|----------|
| Modal | Blocks background interaction | Critical actions, focused tasks |
| Non-Modal | Allows background interaction | Detailed info, parallel reference |

**Common Misconception**: Bottom sheets improve reachability
- **Reality**: Middle of screen is most easily tappable area
- Users hold phones in various ways; bottom isn't always most reachable

**iOS Sheet Presentation (UISheetPresentationController)**:
- Detents: .medium, .large, custom heights
- Grabber indicator for affordance
- Dimming for modal context

---

## Android-Specific Patterns

### Material Design 3 Research

**Google's Research Scale** (Material 3 Expressive):
- **46 separate research studies**
- **18,000+ participants** worldwide
- **3+ years** of collaborative inquiry (2022-2025)

**Research Methods Used**:
- Eye tracking for attention analysis
- Surveys and focus groups for emotional response
- Usability studies for task completion
- A/B testing for button sizes and progress indicators

**Key Findings**:
| Metric | Improvement |
|--------|-------------|
| UI element identification | **Up to 4x faster** in expressive layouts |
| Perceived modernity | **+34%** |
| Subculture relevance | **+32%** |
| Age gap closure | Users 45+ perform as efficiently as younger users |

**Expressive Design Attributes**: Playfulness, creativity, energy, friendliness

### Bottom Navigation Bar

**Adoption**: Implemented in most mainstream apps (Instagram, YouTube, LinkedIn, Spotify)

**Material Design Recommendations**:
- **3-5 destinations** maximum
- Avoid >5 destinations (tap targets too close)
- Always show labels for selected AND unselected items
- Icons without labels: Lower engagement due to guessing

**Thumb Zone Alignment**: Bottom placement aligns with Hoober's thumb zone research

### FAB (Floating Action Button) Effectiveness

**Research Findings** (N=40 users + additional studies):

**First Use vs Repeated Use**:
| Usage | Finding |
|-------|---------|
| First use | Slight negative usability impact |
| Repeated use | More efficient than traditional buttons |
| Preference | Majority prefer FAB over top-right "+" icon |

**Quality of Experience Study** (N=10):
- Usability hypothesis: **Not confirmed**
- Hedonic/aesthetic enhancement: **Confirmed**
- Animation adds perceived modernity

**Google Research**: Users rely on FAB to navigate unfamiliar screens

**Best Practices**:
- Use for primary, constructive action only
- One FAB per screen
- Consider extended FAB with label for clarity

### Predictive Back Gesture

**User Problem Solved**: Accidental app exits from uncertainty about back destination

**Implementation Timeline**:
- Android 13: Foundation APIs introduced
- Android 14: Developer preview of animations
- Android 15: System animations enabled by default for opted-in apps

**Technical Implementation**:
```kotlin
// AndroidX OnBackPressedCallback (backward compatible)
onBackPressedDispatcher.addCallback(this) {
    // Handle back with preview capability
}
```

### Android Widget Psychology

**Penn State University Study** (ACM Conference 2016):
- Widget users **more likely** to enter daily diary information
- Widgets provide **shortcuts for frequent self-reflection**
- Lock screen and home screen widgets serve as **behavioral reminders**

**User Research Study** (100+ users):
- Key insight: Widgets keep apps "top of mind"
- Average user: 80 apps installed, regularly engages with only **9**

**Engagement Benefits**:
- Increased retention through home screen visibility
- Re-engagement of inactive users via personalized information
- Reduced friction for frequent actions

---

## Mobile Form Factors

### Thumb Zone Research (Steven Hoober)

**Observation Study** (N=1,333 observations, urban areas):
| Hold Type | Percentage |
|-----------|------------|
| One-handed | **49%** |
| Cradled (one hand holds, other interacts) | **36%** |
| Two-handed | **15%** |

**Thumb Zone Heat Map**:
| Zone | Reachability |
|------|--------------|
| Bottom center | **Easy** (natural thumb arc) |
| Middle center | **Easy to moderate** |
| Top corners | **Hard** (requires grip shift) |
| Bottom corners | **Moderate** |

**Critical Finding**: Thumbs don't scale with screen size
- Larger screens = more unreachable areas
- User compensation: Device tilting toward thumb

### One-Handed Usage Patterns

**Research Findings** (ResearchGate, ACM):
- One-handed use is **widespread** and preferred
- Under one-hand operation, screen size **significantly affects** performance
- Thumb mobility decreases as device size increases
- Localized movements remain effective even on large devices

**Target Size for One-Handed Use** (Parhi et al., Microsoft Research):
| Task Type | Minimum Target Size |
|-----------|---------------------|
| Discrete tasks | **9.2mm** |
| Serial tasks | **7.6mm** |

### Large Phone vs Small Phone Design

**Screen Size Impact Research**:
| Factor | Small Phone | Large Phone |
|--------|-------------|-------------|
| One-handed operation | Easier | Compromised |
| Content visibility | Less | More |
| Thumb reach | Full screen | Limited to arc |
| User adaptation | Minimal | Tilting, repositioning |

**Performance Plateau**: Non-disabled users plateau at button size **20mm**

**Design Strategies for Large Phones**:
- Place primary actions in thumb-friendly zones
- Use reachability features (iOS Reachability, Samsung One UI)
- Consider floating/movable action buttons
- Bottom sheets for important interactions

### Foldable Device Considerations

**Samsung Foldable UX Evolution** (Galaxy Fold 2019+):

**Key Challenges**:
- Two screens require fluid UX transitions
- Traditional static layouts don't translate
- Hinge can physically split content

**Design Principles**:
| Principle | Implementation |
|-----------|----------------|
| Screen continuity | Seamless transitions between cover/main screen |
| Hinge awareness | Don't place buttons/inputs over hinge |
| Adaptive layouts | Respond to orientation and fold state |
| Multi-window support | Leverage split-screen capabilities |

**Samsung's Approach**: "Moving devices with two screens require more fluid UX"

---

## Mobile-Specific Performance

### App Launch Time Expectations

**User Expectations** (Multiple Studies):
| Threshold | User Response |
|-----------|---------------|
| **<2 seconds** | 49% expect this minimum |
| **<3 seconds** | 71% expect, 63% abandon if exceeded |
| **<5 seconds** | Maximum tolerance (61% will uninstall if exceeded) |
| **>5 seconds** | App abandoned/uninstalled |

**Top App Benchmarks** (Top 100 apps study):
- 39% achieve cold launch <2 seconds
- 73% complete launch <3 seconds

**Immediate Response Expectation**:
- Users expect response within **100ms**
- Opinions formed within **50ms**

**Business Impact**:
- **1 second** improvement = **20% increase** in user retention

### Background Refresh Expectations

**User Expectations**:
- Real-time updates when app opens
- Fresh content immediately available
- Seamless sync across devices

**Energy Consumption Research**:
- Background activities: Up to **40%** of app's total energy
- Advanced features (real-time monitoring): **+30%** energy vs simple apps
- GPS tracking, frequent sync, graphical interfaces: Primary energy drivers

**Design Balance**:
- Provide user toggles for background data/battery use
- Optimize sync frequency based on content freshness needs
- Use intelligent scheduling (low-power modes, WiFi-only options)

### Battery and Performance Perception

**User Impact Research** (Tech My Trend 2025):
- **65%** will consider uninstalling apps that consistently drain battery
- Leading cause: Unoptimized background processes

**User Behavior Research**:
- Battery drain = Direct usability undermining
- Users will: uninstall, choose alternatives, leave low ratings
- Low ratings affect other users' download decisions

**Developer Tools**:
- Android: Battery Historian, Android Studio Profiler
- iOS: Instruments Energy Log, Xcode Energy Diagnostics

### Network Status Communication

**Google Design Guidelines** (Offline UX):

**Communication Best Practices**:
| Scenario | Communication |
|----------|---------------|
| Server issue | "The network is down" |
| User disconnected | "You are disconnected" |
| Airplane mode | Show airplane icon + text label |

**UI Design Components** (Use Multiple Together):
- Informative language
- Icons (with labels)
- Notifications/snackbars
- Color indicators
- Imagery

**Offline-First Architecture**:
- Treat network as optional feature
- Prioritize local data persistence
- Employ sync strategies for reconnection
- Communicate available offline actions clearly

---

## Mobile Accessibility

### VoiceOver/TalkBack Usage Patterns

**WebAIM Survey #10** (N=1,539, December 2023-January 2024):
| Metric | Value |
|--------|-------|
| Mobile screen reader usage | **90%** of respondents |
| iOS preference | **70.6%** |
| Android (TalkBack) | **34.7%** (many use both) |
| Mobile app preference | **58%** (up from 51.8% in 2021) |

**Platform Comparison**:
| Feature | iOS VoiceOver | Android TalkBack |
|---------|---------------|------------------|
| Gesture complexity | Multi-touch, multi-finger | Single-finger focused |
| One-handed operation | More difficult | Easier |
| Motor impairment accommodation | Challenging | Better |
| Keyboard accessibility | Limited | Full support |

**Expert User Patterns** (Microsoft Research):
- Extensive use of directional gestures
- Reliance on voice and external keyboard for text input
- Repurposed explore-by-touch for single-tap actions

**Usability Findings**:
- VoiceOver makes iOS accessible but usability issues remain
- Long text writing: Too time-consuming
- Users appreciate VoiceOver as important innovation

### Large Text Accommodation

**Dynamic Type Scaling**:
| Size Category | Scale Factor |
|---------------|--------------|
| Extra Small | 0.82x |
| Small | 0.88x |
| Medium | 0.94x |
| Large (Default) | 1.0x |
| Extra Large | 1.12x |
| XXL | 1.24x |
| XXXL | 1.35x |
| Accessibility sizes | 1.6x - 3.1x+ |

**Implementation Requirements**:
- Test at all accessibility text sizes
- Ensure layouts adapt without truncation/overlap
- Use scrollable containers for potentially long content
- Avoid fixed heights that truncate large text

### Reduce Motion on Mobile

**Vestibular Disorder Prevalence**:
- By age 40: **>35%** have experienced vestibular dysfunction
- Motion sickness susceptibility: **10%** of population

**Platform Settings**:
| Platform | Setting Location |
|----------|------------------|
| iOS | Settings > Accessibility > Motion |
| Android 9+ | Settings > Accessibility > Remove animations |
| Android 13+ | Accessibility > Color and motion (toggles all animations) |

**Motion Triggers** (Val Head research):
1. Relative size of movement
2. Mismatched directions
3. Distance covered on screen

**Design Response**:
- Check `UIAccessibility.isReduceMotionEnabled` (iOS)
- Check `Settings.System.ANIMATOR_DURATION_SCALE` (Android)
- Provide instant state changes as alternative
- Reduce parallax and zoom effects

### Switch Control Design

**User Population**: People with limited motor skills who cannot use standard touch/keyboard

**Key UX Challenges**:
| Pattern | Problem |
|---------|---------|
| Swipe gestures | Cannot be performed with switches |
| Bottom sheets | May trap focus or be inaccessible |
| Infinite scroll | No clear endpoint for scanning |
| Gesture-only actions | Complete barrier |

**Design Requirements**:
- Provide button alternatives for all gestures
- Ensure sequential navigation reaches all elements
- Include clear focus indicators
- Allow adequate time for switch activation
- Support external switch hardware

**User Research Finding**: Users prioritize **independence and control** over activities

---

## Mobile Conversion & Engagement

### App vs Web Preference

**User Preference Data** (2024 Research):
| Metric | App | Web |
|--------|-----|-----|
| User preference | **64%** prefer apps | 36% prefer mobile web |
| Mobile commerce purchases | **78%** via apps | 22% via mobile web |
| Banking access | **73%** via apps | 27% via web |
| Overall smartphone time | **90%** in apps | 10% in browsers |

**Preference Drivers**:
| Factor | Percentage |
|--------|------------|
| Time savings | **68%** |
| Convenience/speed | **57%** |
| Easier navigation | Part of 85% preferring apps |

**Conversion Rate Advantage**:
- Mobile apps: **157% higher** conversion rates than web apps
- Growth rate (2024): Apps +15%, Web apps +8%

### Push Notification Fatigue

**Daily Notification Volume**:
- Average US user: **46 notifications/day**
- Teenagers: **240 notifications/day** (Michigan Medicine)

**Opt-Out Thresholds**:
| Frequency | User Response |
|-----------|---------------|
| 1/week | 10% disable notifications |
| 3-6/week | **40%** disable notifications |
| >6/week | 46% disable, **32% uninstall app** |

**Platform Opt-In Rates**:
| Platform | Opt-In Rate | Trend |
|----------|-------------|-------|
| iOS | 43.9% (avg) | Slight decline (58%→56%) |
| Android | 91.1% (historically) → 67% | -18% in one year |
| Overall average | 61-67.5% | Declining |

**Retention Impact**:
- Users with 1+ notifications in first 90 days: **~3x higher retention**

**Design Recommendation**: Optimal frequency **<3/week** for engagement

### App Store Psychology

**Rating Impact on Conversion**:
| Rating Change | Conversion Impact |
|---------------|-------------------|
| 3 stars → 4 stars | **+89%** |
| 1-2 stars → 4-5 stars | **6-7x more downloads** |
| <3 stars | **-50% potential downloads** |

**User Behavior** (Apptentive Research):
| Rating | User Response |
|--------|---------------|
| 3 stars | 50% won't consider |
| 2 stars | **85%** won't consider |

**Review Reading Behavior**:
- Free apps: **77%** read at least 1 review
- Paid apps: **80%** read at least 1 review
- **90%** consider star ratings valuable

**Psychological Mechanisms**:
1. **Social Proof**: "If others like it, it must be good"
2. **Risk Aversion**: 79% check ratings before download
3. **Herd Mentality**: High ratings signal popularity/quality

### Rating Prompt Timing (SKStoreReviewController)

**Apple Guidelines**:
- Maximum: **3 prompts per 365-day period**
- Timing: When users feel satisfaction (completed action/level/task)

**Best Practices**:
| Practice | Rationale |
|----------|-----------|
| Wait 7+ days after install | Indicates returning, satisfied user |
| After meaningful action completion | Positive emotional state |
| After 3-4 uses minimum | User has formed opinion |
| Wait 1-2 weeks between prompts | Avoid fatigue |

**Negative Timing** (Avoid):
- On app launch
- During time-sensitive tasks
- Mid-flow interruptions
- After errors or frustrations

**Timing affects review quality**: Right moment = more detailed, thoughtful reviews

---

## Touch Target & Form Optimization

### Touch Target Size Research

**Platform Guidelines**:
| Platform | Minimum Size | Physical Size |
|----------|--------------|---------------|
| Apple iOS | **44x44pt** | ~7.7mm |
| Android Material | **48x48dp** | ~9mm |
| WCAG 2.5.8 (AA) | **24x24px** | ~4.2mm |
| WCAG 2.5.5 (AAA) | **44x44px** | ~7.7mm |

**MIT Touch Lab Research**:
- Average fingertip: **10-14mm** contact area
- Thumb contact: **12-20mm**
- Precision drops **40%** for targets under 7mm (20px)

**Error Rate by Target Size** (Empirical Research):
| Target Size | Error Rate | Notes |
|-------------|------------|-------|
| 44px+ | ~3% | Acceptable |
| 24px | ~15% | 5x worse |
| <24px | >20% | Unusable |
| <32x32px | **60% drop** in success rate | Critical threshold |

**One-Handed Optimization** (Parhi et al.):
- 9.2mm for discrete tasks
- 7.6mm for serial tasks
- No significant error difference above these thresholds

**Rage Tap Prevention** (Steven Hoober):
- Top of screen: **11mm** (31pt / 42px)
- Bottom of screen: **12mm** (34pt / 46px)

### Mobile Form Field Optimization

**Keyboard Type Impact** (Baymard Institute):
- **60%** of top 50 mobile e-commerce sites fail 2 of 5 keyboard optimizations
- Most common error: Using "text" type for all fields

**Optimal Input Types**:
| Field | Input Type | Keyboard Provided |
|-------|------------|-------------------|
| Email | `email` | @ and . characters prominent |
| Phone | `tel` | Numeric keypad |
| URL | `url` | . / and .com keys |
| Number | `number` | Numeric with decimal |
| Credit card | `cc-number` | Numeric, card formatting |

**Auto-Correction Settings** (Baymard):
| Setting | Sites Neglecting | Impact |
|---------|------------------|--------|
| Auto-correction appropriate use | **79%** | Typos in names, addresses |
| Auto-capitalization appropriate use | **27%** | Incorrect capitalization |

**Form Field Best Practice**: Don't split single input entities (e.g., phone number into 3 fields)

---

## Animation & Frame Rate

### 60fps Target

**Frame Budget**:
- 60fps = **16.67ms** per frame
- App work budget: ~10ms (browser needs ~6ms)

**Perception Research**:
- Drops below 60fps: Increases perceived lag
- User retention impact: **-27%** with consistent frame drops

**Animation Duration Guidelines**:
- **200-400ms** optimal for UI transitions
- Material Design easing: `cubic-bezier(0.4, 0, 0.2, 1)`

**Microinteraction Impact**:
- Smooth transitions + instant feedback = **+23%** perceived usability
- Subtle movement reduces cognitive load by **up to 36%**

### Input Latency Thresholds (Jota et al. 2013, CHI)

| Task | Perceptible Threshold |
|------|----------------------|
| Dragging | **1-7ms** |
| Scribbling | 7-40ms |
| Tapping | **40-64ms** |
| Typing | **20-30ms** |

---

## SwiftUI/UIKit & Jetpack Compose

### iOS Framework Research

**SwiftUI Adoption Benefits**:
- Code complexity reduction: **Up to 50%**
- Load time improvement: **Up to 30%** decrease
- Live preview: Faster design iteration

**Design-Related User Impact**:
- **94%** of first impressions are design-related
- Interface tweaks: **15-20%** user retention increase (NNGroup heatmap analysis)

### Jetpack Compose Adoption

**Google Play Statistics**:
- **24%** of top 1000 apps use Compose
- **125,000+** apps published with Jetpack Compose

**Developer Benefits**:
| Metric | Improvement |
|--------|-------------|
| Code size reduction | **-25%** average |
| Developer satisfaction (state management) | **+40%** |
| Design time efficiency | **+30%** |
| Development time (Google Drive) | **Nearly 50% reduction** |

**Material Design 3 Integration**: Native implementation of Material You and Material 3 Expressive

---

## Quick Detection Signals

### iOS Pattern Compliance
- Dynamic Type supported at all sizes
- 44x44pt minimum touch targets
- Haptic feedback for interactions
- Edge swipe back navigation works
- Pull-to-refresh in appropriate contexts
- Reduce motion respected

### Android Pattern Compliance
- Material Design 3 components used
- 48x48dp minimum touch targets
- Predictive back gesture supported
- Bottom navigation for 3-5 destinations
- FAB for primary action only
- Widget support for frequent actions

### Cross-Platform Accessibility
- VoiceOver/TalkBack tested
- Large text accommodation
- Reduce motion alternatives
- Switch control compatible
- All gestures have alternatives

---

## Code Patterns

### iOS (SwiftUI)
```swift
// Dynamic Type support
Text("Body text")
    .font(.body) // Automatically scales

// Custom font with Dynamic Type
@ScaledMetric var fontSize: CGFloat = 16
Text("Scaled text")
    .font(.system(size: fontSize))

// Haptic feedback
let generator = UIImpactFeedbackGenerator(style: .medium)
generator.impactOccurred()

// Touch target (44pt minimum)
Button(action: { }) {
    Image(systemName: "plus")
}
.frame(minWidth: 44, minHeight: 44)

// Reduce motion check
@Environment(\.accessibilityReduceMotion) var reduceMotion

// Sheet presentation
.sheet(isPresented: $showSheet) {
    SheetContent()
        .presentationDetents([.medium, .large])
}
```

### Android (Jetpack Compose)
```kotlin
// Material 3 theme
MaterialTheme {
    // Components automatically follow M3 guidelines
}

// Touch target (48dp minimum)
IconButton(
    onClick = { },
    modifier = Modifier.size(48.dp)
) {
    Icon(Icons.Default.Add, contentDescription = "Add")
}

// Haptic feedback
val view = LocalView.current
view.performHapticFeedback(HapticFeedbackConstants.CONFIRM)

// Bottom navigation
NavigationBar {
    items.forEach { item ->
        NavigationBarItem(
            selected = currentRoute == item.route,
            onClick = { navigate(item.route) },
            icon = { Icon(item.icon, contentDescription = item.label) },
            label = { Text(item.label) } // Always show labels
        )
    }
}

// Predictive back
BackHandler(enabled = true) {
    // Handle with preview capability
}
```

### Warning Patterns
```kotlin
// Tiny touch targets (VIOLATION)
IconButton(modifier = Modifier.size(24.dp)) // Too small

// No gesture alternative (VIOLATION)
SwipeToDismiss(onDismiss = { }) // No button fallback

// Hidden navigation (PROBLEMATIC)
DrawerNavigation() // Consider bottom nav for primary destinations

// Ignoring reduce motion (VIOLATION)
AnimatedVisibility() // Without reduceMotion check
```

---

## Key Thresholds Summary

| Category | iOS | Android |
|----------|-----|---------|
| Touch target minimum | **44x44pt** | **48x48dp** |
| App launch expectation | **<2-3 seconds** | **<2-3 seconds** |
| Haptic latency | **<50ms** | **<50ms** |
| Animation duration | 200-400ms | 200-400ms |
| Bottom nav destinations | 3-5 max | 3-5 max |
| Notification frequency | <3/week optimal | <3/week optimal |
| Rating prompt limit | 3/year | N/A (no system limit) |

---

## Sources

### Academic Research
- Hoober, S. - Thumb zone research (N=1,333 observations)
- Parhi et al. - Target size study (Microsoft Research)
- Google Material Design Research - 46 studies, N=18,000+
- WebAIM Screen Reader Survey #10 - N=1,539
- MIT Touch Lab - Fingertip contact area research

### Industry Research
- NNGroup - Mobile usability studies, navigation patterns (N=179)
- Baymard Institute - Mobile e-commerce UX (4,400+ test sessions)
- Apptentive - App store psychology research
- Penn State University - Widget engagement study

### Platform Guidelines
- Apple Human Interface Guidelines
- Material Design 3 Guidelines
- WCAG 2.2 Success Criteria
- Android Developers Documentation
