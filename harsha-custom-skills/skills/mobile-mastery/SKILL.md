---
name: mobile-app-mastery
description: >
  Comprehensive mobile app development skill for building production-grade iOS, Android,
  and cross-platform applications. Covers React Native (Expo + bare), Flutter, Swift/SwiftUI,
  Kotlin/Jetpack Compose, Kotlin Multiplatform, Capacitor/Ionic, .NET MAUI, and PWAs.
  Includes architecture (MVVM, MVI, Clean), state management, UI/UX, animations, networking,
  data persistence, auth, security (OWASP), testing, CI/CD, push notifications, deep linking,
  monetization, accessibility, localization, AI/ML, AR/camera/maps, wearables/IoT, media,
  observability, and app store publishing. Features decision trees for every choice point,
  domain-specific priority matrices for 10 app types, pre-launch checklists (408 items),
  62 anti-pattern detectors, code generation templates, and migration playbooks.

  USE THIS SKILL WHENEVER the user mentions mobile app, iOS, Android, React Native, Flutter,
  SwiftUI, Jetpack Compose, Kotlin Multiplatform, Expo, native app, cross-platform, hybrid app,
  mobile UI, app store, TestFlight, Play Store, push notifications, deep linking, in-app purchases,
  mobile testing, mobile CI/CD, mobile security, mobile performance, mobile accessibility,
  mobile animations, mobile state management, mobile architecture, app monetization, wearable app,
  watchOS, Wear OS, mobile AR, mobile camera, mobile maps, mobile authentication, crash reporting,
  feature flags, server-driven UI, on-device AI, app migration, or ANY task involving building,
  designing, reviewing, testing, deploying, or maintaining mobile applications.

  Do NOT use this skill for: web-only applications with no mobile component, backend API development
  (unless it's a mobile-specific BFF), desktop-only software, embedded systems without a mobile
  companion, or general UI/UX reviews of non-mobile interfaces.
---

# Mobile App Mastery

36 deep-dive reference files with decision trees, domain matrices, checklists, code templates, and anti-pattern detection. Load references selectively based on the task type below.

## Task Type Detection

Identify the task type FIRST, then load only the references needed. This prevents loading irrelevant content and keeps responses focused.

```python
TASK_MODES = {
    "review":    ["anti-patterns.md", "checklists.md", "[framework].md", "performance.md", "security.md", "accessibility.md"],
    "build":     ["decision-trees.md", "app-type-matrices.md", "code-templates.md", "project-setup.md", "[framework].md"],
    "decide":    ["decision-trees.md", "app-type-matrices.md"],
    "migrate":   ["migration-strategies.md", "decision-trees.md", "[source-framework].md", "[target-framework].md"],
    "launch":    ["checklists.md", "ci-cd-devops.md", "observability.md"],
    "monitor":   ["observability.md", "checklists.md"],
    "trends":    ["emerging-trends.md"],
    "feature":   ["[topic].md", "[framework].md"],  # e.g. auth → authentication.md
}

# Detection logic:
if user_shares_code_or_screenshot:
    mode = "review"  # Always treat shared code as review request
elif keywords_match(["review", "audit", "debug", "fix", "optimize", "analyze", "what's wrong"]):
    mode = "review"
elif keywords_match(["build", "create", "implement", "scaffold", "start", "new app", "make me"]):
    mode = "build"
elif keywords_match(["choose", "compare", "decide", "which", "should I use", "vs", "better"]):
    mode = "decide"
elif keywords_match(["migrate", "upgrade", "convert", "move from", "switch to"]):
    mode = "migrate"
elif keywords_match(["launch", "deploy", "submit", "publish", "release", "app store"]):
    mode = "launch"
elif keywords_match(["monitor", "crash", "analytics", "logging", "alert", "observability"]):
    mode = "monitor"
elif keywords_match(["trend", "future", "modern", "latest", "2025", "2026", "what's new"]):
    mode = "trends"
else:
    mode = "feature"  # Default: load topic-specific + framework reference
```

## Quick-Start Decision Tree

Provides defaults so responses aren't blocked by indecision. When the user hasn't specified preferences, use these defaults.

```
User needs help with mobile app?
│
├─ "Which framework?" → READ decision-trees.md
│   Default: Expo (React Native) for cross-platform, SwiftUI for iOS-only, Compose for Android-only
│
├─ "Build me a [type] app" → PLAN-VALIDATE-EXECUTE workflow below
│   1. Detect domain → app-type-matrices.md
│   2. Choose stack → decision-trees.md
│   3. Scaffold → code-templates.md + project-setup.md
│   4. Build iteratively → framework reference + cross-cutting references as needed
│
├─ "Review/fix my code" → REVIEW workflow
│   1. Detect framework from code
│   2. Scan → anti-patterns.md (62 patterns with severity + fix)
│   3. Audit → checklists.md (408 systematic items)
│   4. Fix → framework reference for platform-specific solutions
│
├─ "Help with [feature]" (auth, push, maps, etc.)
│   → Load the specific cross-cutting reference + framework reference
│
├─ "Migrate from X to Y" → migration-strategies.md (12 playbooks)
│
├─ "Deploy / launch" → checklists.md (pre-launch) + ci-cd-devops.md + observability.md
│
└─ General question → Answer from this file's quick references, load deeper refs if needed
```

## App Domain Detection

Different app types have radically different priorities. A fintech app prioritizes security; a social app prioritizes feed performance. Detect the domain early to weight recommendations correctly.

```python
DOMAIN_PRIORITIES = {
    "social":      ["Feed_Perf", "Real_Time", "Media", "Engagement", "Notifications"],
    "fintech":     ["Security", "Compliance", "Accuracy", "Trust", "Biometrics"],
    "healthcare":  ["Safety", "HIPAA", "Accessibility", "Error_Prevention", "Accuracy"],
    "ecommerce":   ["Conversion", "Checkout", "Product_Display", "Payments", "Trust"],
    "media":       ["Playback", "DRM", "Downloads", "Adaptive_Bitrate", "Offline"],
    "enterprise":  ["Efficiency", "SSO", "Offline_Sync", "RBAC", "Data_Density"],
    "education":   ["Engagement", "Progress_Track", "Offline_Content", "Accessibility"],
    "iot":         ["BLE_Reliability", "Real_Time", "Device_Pairing", "Background"],
    "fitness":     ["HealthKit", "Real_Time_Tracking", "Wearable_Sync", "Motivation"],
    "travel":      ["Offline_Maps", "Localization", "Booking_Flow", "Location_Services"],
}
# Default if unclear: ["Usability", "Performance", "Security", "Accessibility"]
```

For weighted matrices with specific metrics and implementation patterns per domain → READ `references/app-type-matrices.md`

## Conflict Resolution

When recommendations conflict, this hierarchy resolves them (highest priority first):

```
1. SAFETY / ACCESSIBILITY    — Non-negotiable. WCAG 2.2 AA minimum.
2. CORE TASK COMPLETION       — The app must work correctly.
3. PLATFORM CONVENTIONS       — iOS back swipe, Android back button, system bars.
4. DOMAIN PRIORITY            — From domain detection above.
5. PERFORMANCE                — 60fps, <2s cold start, responsive touch.
6. DEVELOPER EXPERIENCE       — Maintainability, testability, team velocity.
7. AESTHETICS                 — Visual polish, animations, delight.
```

Common tradeoffs with defaults:

| Conflict | Default Resolution |
|----------|-------------------|
| Native perf vs cross-platform speed | Cross-platform for MVP/startup; native for fintech/healthcare |
| Offline-first vs complexity | Offline-first if >30% users have poor connectivity |
| Platform conventions vs brand consistency | Platform conventions win unless unified brand is critical |
| Code sharing vs native UX | Share business logic; keep UI layer native |
| Startup speed vs feature count | Lazy-load non-critical; show content in <2s |

## Plan-Validate-Execute Workflow

For BUILD tasks, follow this feedback loop to avoid wasted effort:

```
PLAN → VALIDATE → EXECUTE → VERIFY
  │        │          │         │
  │        │          │         └─ Run verification checklist (below)
  │        │          └─ Generate code using framework reference + code-templates.md
  │        └─ Confirm plan with user before generating large amounts of code
  └─ Detect domain + choose framework + choose architecture + plan phases
```

### Build Phases

| Phase | Action | References to Load |
|-------|--------|-------------------|
| **1. Plan** | Domain detection, framework + architecture choice | `decision-trees.md`, `app-type-matrices.md` |
| **2. Scaffold** | Project structure, environments, DI, CI/CD | `project-setup.md`, `code-templates.md`, `[framework].md` |
| **3. Foundation** | Auth, networking, data layer, error handling | `authentication.md`, `networking.md`, `data-storage.md` |
| **4. Features** | UI, state, lists, forms, push, deep links, offline | `state-management.md`, `ui-ux-design.md`, `[topic].md` |
| **5. Polish** | Performance, security, accessibility, localization | `performance.md`, `security.md`, `accessibility.md`, `localization.md` |
| **6. Verify** | Checklists, testing, code review, anti-pattern scan | `checklists.md`, `testing.md`, `anti-patterns.md` |
| **7. Launch** | Store submission, monitoring, feature flags | `checklists.md`, `ci-cd-devops.md`, `observability.md` |

## Code Generation Rules

These rules exist because mobile apps face unique constraints (limited memory, battery, unreliable networks, strict platform review) that web apps don't.

```python
RULES = {
    "type_safety":    "TypeScript strict / Swift strict concurrency / Kotlin null safety",
    "error_handling": "Result types or sealed classes — never swallow errors silently",
    "di":             "Constructor injection; Hilt/Koin (Android), manual DI (iOS), context (RN)",
    "testability":    "Program to interfaces/protocols; repository pattern; pure functions",
    "performance":    "Lazy load, virtualize lists, minimize re-renders, cache aggressively",
    "accessibility":  "Every interactive element needs semantic label + role",
    "security":       "Never hardcode secrets; Keychain/Keystore for tokens; validate all inputs",
    "offline":        "Cache critical data locally; show meaningful offline state",
    "platform":       "Respect safe areas, back gesture, system bars, dynamic type/font scaling",
}
```

For reusable scaffolding patterns → READ `references/code-templates.md` (10 template categories)

## Key Metrics

```
STARTUP:        Cold <2s, Warm <1s, Hot <500ms
FRAME RATE:     60fps minimum (120fps on ProMotion/high-refresh)
CRASH-FREE:     >99.5% (>99.9% for fintech/healthcare)
ANR RATE:       <0.47% (Android vitals threshold)
TOUCH TARGET:   44×44pt (Apple HIG) / 48×48dp (Material 3)
CONTRAST:       4.5:1 normal text, 3:1 large text (WCAG AA)
BUNDLE SIZE:    <50MB initial download
MEMORY:         <200MB peak for typical app
BATTERY:        <10% per hour active use
API RESPONSE:   <400ms perceived (Doherty Threshold)
```

## Anti-Pattern Quick Reference

Top 10 critical patterns to flag in ANY mobile code review:

| Anti-Pattern | Severity | Why It Matters |
|-------------|----------|----------------|
| Hardcoded secrets/API keys | CRITICAL | Extractable from app binary; instant security breach |
| Business logic in UI layer | HIGH | Untestable, unmaintainable, duplicated across screens |
| Missing error boundary | HIGH | Unhandled async errors crash the app silently |
| Zombie subscriptions | HIGH | Memory leaks → OOM crashes, especially on older devices |
| Main thread blocking | CRITICAL | Instant ANR on Android, frozen UI on iOS |
| No loading/error/empty states | HIGH | Users see blank screens, assume app is broken |
| Missing accessibility labels | HIGH | Excludes 15%+ of users; fails app store review guidelines |
| Hardcoded dimensions | MEDIUM | Breaks on different screen sizes, foldables, tablets |
| Process death ignorance | HIGH | Android kills backgrounded activities; state lost |
| Plain-text token storage | CRITICAL | Rooted/jailbroken device reads tokens trivially |

Full catalog with detection patterns and fix code → READ `references/anti-patterns.md`

## Verification Checklist

Run after generating ANY mobile code. This catches the most common issues before the user has to find them.

```
□ Type-safe?       (no `any`, no force unwrap, no `!!`)
□ Errors handled?  (Result/sealed class, user-facing error messages)
□ Lifecycle-aware? (cleanup in onDispose/deinit/onCleared)
□ Accessible?      (labels, roles, contrast ≥4.5:1, touch targets ≥44pt)
□ Offline-safe?    (graceful degradation with no network)
□ Secure?          (no hardcoded secrets, encrypted token storage)
□ Platform-correct?(safe areas, back gesture, system bars, dynamic type)
□ Testable?        (injectable dependencies, pure functions, no singletons)
```

For systematic verification (408 items) → READ `references/checklists.md`

## Production Gotchas (Hard-Won Knowledge)

These are non-obvious traps that only surface in production. Most tutorials and documentation skip these entirely.

### App Store Review Killers
```
iOS REJECTION TRIGGERS (top causes, not in official docs):
- Using UIWebView (deprecated) instead of WKWebView → instant reject
- Requesting location/camera/contacts without clear in-app justification string
- App that "could have been a website" with no native features → 4.2 rejection
- Login-required app without demo account credentials in review notes
- Mentioning "beta" or "test" anywhere visible in the UI
- In-app purchase that unlocks content available free on your website
- Privacy manifest missing after iOS 17 (required for all third-party SDKs)
- Background modes declared but not actually used → reject + slow future reviews

Android GOTCHAS:
- Target SDK must be within 1 year of latest (Google enforces annually)
- Foreground service type declarations required since Android 14
- Photo picker mandatory for photo access (no full gallery permission)
- Data safety section must match actual behavior exactly (audited)
- 150MB AAB limit (use Play Asset Delivery for larger assets)
```

### Cross-Feature Interaction Bugs (The Integration Nightmares)
These bugs only appear when two features interact. No single-feature doc covers them:

```
AUTH + DEEP LINKS:   Deep link arrives while user is logged out → must queue the
                     deep link, complete auth flow, THEN navigate. Most apps lose
                     the deep link. Solution: persist pending deep link in secure storage.

PUSH + IN-APP MSG:   Push arrives while app is foregrounded → don't show both the
                     push banner AND in-app handler. Use willPresent (iOS) /
                     onMessageReceived (Android) to suppress duplicate.

ANALYTICS + CONSENT: Analytics SDK initializes before consent screen appears →
                     fires events before user consents → GDPR/CCPA violation.
                     Solution: lazy-init analytics SDK AFTER consent granted.

OFFLINE + AUTH:      Auth token expires while offline → all queued requests fail
                     when reconnecting. Solution: refresh token FIRST on reconnect,
                     then replay queue. Don't show login screen if refresh succeeds.

FEATURE FLAGS + REVIEW: Apple reviews the LIVE version. If a feature flag hides
                        unreleased UI, reviewer might not see it. But if they DO
                        discover hidden UI, it's a rejection. Solution: use separate
                        build configs for review vs production, not runtime flags.

BIOMETRICS + PROCESS DEATH: Android kills your activity. User returns, biometric
                            prompt shows, but the callback is orphaned. Solution:
                            re-register biometric callback in onCreate, not just in
                            the fragment that originally triggered it.
```

### Invisible Platform Bugs
Issues that don't crash but silently degrade the user experience:

```
ANDROID PROCESS DEATH:
  The #1 invisible Android bug. System kills backgrounded activities to reclaim
  memory. When user returns, Activity recreates but ALL in-memory state is gone.
  Symptom: user fills a 5-step form, switches to another app, returns to blank form.
  Fix: SavedStateHandle (Jetpack) or onSaveInstanceState. Test with "Don't keep
  activities" in Developer Options — EVERY screen must survive this.

iOS BACKGROUND EXECUTION:
  iOS gives you ~30 seconds of background time, then suspends. If you start a
  network request and the user backgrounds, the request may be killed mid-flight.
  Fix: beginBackgroundTask(withName:) for critical operations. But Apple audits
  background usage — abuse it and they'll reject future updates.

REACT NATIVE JS BRIDGE COST:
  Every cross-bridge call serializes to JSON. Passing large arrays (1000+ items)
  or calling bridge frequently (60fps animation data) creates visible jank.
  Fix: Use Reanimated 3 for animations (runs on UI thread), FlashList for lists,
  and batch bridge calls. New Architecture (TurboModules/Fabric) reduces this.

FLUTTER IMAGE CACHE:
  Default ImageCache holds only 100 images / 100MB. Feed-heavy apps blow through
  this instantly, causing constant re-downloads and visible flickering.
  Fix: Set ImageCache().maximumSize and use cached_network_image with custom
  cache manager. For feeds: preload next page images during scroll idle.

KEYBOARD + BOTTOM SHEET:
  On Android, showing keyboard while bottom sheet is open causes layout jump.
  The bottom sheet animates to accommodate keyboard, but the animation is jarring.
  Fix: Use WindowInsets.isImeVisible to detect keyboard, adjust bottom sheet
  peek height BEFORE keyboard appears using WindowInsetsAnimationCompat.

WEBVIEW COOKIE SYNC:
  Native auth token ≠ WebView session cookie. User logs in natively, opens a
  WebView, and appears logged out. Fix: Inject auth cookies into WKWebView
  HTTPCookieStore (iOS) or CookieManager (Android) BEFORE loading the URL.
```

### Performance Cliff Edges
```
RN BRIDGE SERIALIZATION:  >1MB JSON payload → 200ms+ freeze. Paginate.
FLUTTER REBUILD STORM:    setState at root widget → entire tree rebuilds. Use
                          Provider/Riverpod selectors or const constructors.
IOS MAIN THREAD CHECKER:  Core Data fetch on main thread is silent until it's not.
                          10ms fetch × 100 cells = 1s scroll stutter.
ANDROID RECYCLERVIEW:     notifyDataSetChanged() on 1000+ items → frame drop.
                          Use DiffUtil or ListAdapter for O(n) diffing.
MEMORY PRESSURE (iOS):    No swap file. At ~1.5GB, system sends memory warnings.
                          At ~2GB, OOM kill — no crash log, no trace. Monitor with
                          os_proc_available_memory().
LARGE NAVIGATION STACK:   50+ screens in stack = 50 retained view trees.
                          Symptoms: gradual slowdown, OOM on older devices.
                          Fix: Clear stack on major navigation (e.g., after login).
```

### Indian Market Specifics (User's Context)
```
UPI INTEGRATION:       Use PSP SDKs (PhonePe, GPay, Paytm) not raw UPI intent.
                       Raw intent has 30%+ failure rate on some OEMs.
JUSPAY/RAZORPAY:       Razorpay for quick setup; Juspay for high-volume.
                       Both need server-side order creation — never client-side.
OEM BATTERY KILLERS:   Xiaomi/MIUI, Samsung, OnePlus aggressively kill background
                       processes. dontkillmyapp.com has OEM-specific workarounds.
                       Show users how to disable battery optimization for your app.
LOW-END DEVICES:       50%+ Indian users on 2-3GB RAM devices. Test on Android Go.
                       Use R8/ProGuard aggressively. Target API images, not real images.
NETWORK CONDITIONS:    Design for 2G/3G fallback. Average mobile speed ~20Mbps but
                       varies wildly. Use adaptive image loading (low-res → high-res).
AADHAAR/KYC:           Never store Aadhaar number. Use DigiLocker API for verification.
                       UIDAI mandates virtual ID for most use cases.
REGIONAL LANGUAGES:    Support Hindi + regional at minimum for mass-market apps.
                       Use String Catalogs (iOS) / strings.xml (Android) from day 1.
                       RTL support needed for Urdu.
```

### Framework Guides (6) — Load based on user's framework
| File | Framework |
|------|-----------|
| `references/react-native.md` | React Native / Expo |
| `references/flutter.md` | Flutter / Dart ¹ |
| `references/ios-native.md` | Swift / SwiftUI |
| `references/android-native.md` | Kotlin / Jetpack Compose |
| `references/kotlin-multiplatform.md` | KMP / Compose Multiplatform |
| `references/hybrid-pwa.md` | Capacitor, Ionic, PWA, .NET MAUI, Tauri |

¹ **Flutter Note:** For comprehensive, actively-maintained Flutter development guidance covering Flutter 3.38+, advanced features, and deep platform-specific optimization, use the dedicated **flutter-master** skill (89+ specialized reference files). This file provides a generalist overview for comparison with other frameworks.

### Structural Guides (8) — Load based on task mode
| File | Purpose | Load When |
|------|---------|-----------|
| `references/decision-trees.md` | 8 flowcharts for every decision point | Choosing framework, arch, state mgmt, testing, API, storage |
| `references/app-type-matrices.md` | Weighted priorities for 10 app domains | Starting a new project or reviewing architecture fit |
| `references/checklists.md` | 10 checklists, 408 items total | Pre-launch, code review, security audit, accessibility |
| `references/code-templates.md` | 10 reusable scaffolding patterns | Building new features, project setup, standard screens |
| `references/anti-patterns.md` | 62 anti-patterns with fix guidance | Code review, debugging, optimization |
| `references/emerging-trends.md` | Server-driven UI, on-device AI, edge, privacy-first | Questions about modern patterns or future direction |
| `references/observability.md` | Crash reporting, analytics, feature flags, alerting | Post-launch monitoring, debugging production issues |
| `references/migration-strategies.md` | 12 migration playbooks | Switching frameworks, upgrading versions, refactoring |

### Cross-Cutting Guides (22) — Load by topic
| File | Topic |
|------|-------|
| `references/architecture.md` | Clean Architecture, MVVM, MVI, modular |
| `references/ui-ux-design.md` | Apple HIG, Material 3, responsive, adaptive |
| `references/state-management.md` | State solutions across all platforms |
| `references/networking.md` | REST, GraphQL, WebSocket, caching, interceptors |
| `references/data-storage.md` | Room, SwiftData, Realm, SQLDelight, encrypted |
| `references/authentication.md` | OAuth2/PKCE, biometrics, passkeys, social auth |
| `references/security.md` | OWASP MASTG, cert pinning, RASP, data protection |
| `references/testing.md` | Testing pyramid, E2E, device farms, coverage |
| `references/performance.md` | Startup, memory, battery, rendering, profiling |
| `references/animations.md` | Spring physics, gestures, Lottie/Rive, transitions |
| `references/ci-cd-devops.md` | GitHub Actions, Fastlane, code signing, distribution |
| `references/push-notifications.md` | APNs, FCM, Live Activities, rich notifications |
| `references/deep-linking.md` | Universal Links, App Links, deferred deep links |
| `references/monetization.md` | IAP, subscriptions, ads, ASO, paywalls |
| `references/accessibility.md` | VoiceOver, TalkBack, WCAG 2.2, Dynamic Type |
| `references/localization.md` | i18n, String Catalogs, RTL, locale-aware formatting |
| `references/ai-ml-mobile.md` | Core ML, ML Kit, TFLite, on-device LLMs |
| `references/ar-camera-maps.md` | ARKit, ARCore, Maps, geofencing |
| `references/wearables-iot.md` | watchOS, Wear OS, BLE, Matter, HealthKit |
| `references/media-social.md` | Audio/video playback, DRM, social sharing, chat |
| `references/offline-first.md` | CRDTs, sync, conflict resolution, optimistic UI |
| `references/project-setup.md` | Scaffolding, monorepos, linting, env config |
