# Mobile App Development: Actionable Checklists

## Table of Contents

- [1. Pre-Launch Checklist (iOS)](#1-pre-launch-checklist-ios)
- [2. Pre-Launch Checklist (Android)](#2-pre-launch-checklist-android)
- [3. Code Review Checklist (Mobile)](#3-code-review-checklist-mobile)
- [4. Security Audit Checklist](#4-security-audit-checklist)
- [5. Performance Audit Checklist](#5-performance-audit-checklist)
- [6. Accessibility Audit Checklist](#6-accessibility-audit-checklist)
- [7. Offline Readiness Checklist](#7-offline-readiness-checklist)
- [8. API Integration Checklist](#8-api-integration-checklist)
- [9. CI/CD Pipeline Checklist](#9-cicd-pipeline-checklist)
- [10. Post-Launch Monitoring Checklist](#10-post-launch-monitoring-checklist)

## 1. Pre-Launch Checklist (iOS)

### App Store Review Guidelines Compliance
- [ ] [CRITICAL] Verify app follows all 93+ App Store Review Guidelines sections — Failure results in app rejection and delay to market launch
- [ ] [CRITICAL] Confirm app name matches bundle identifier in all build configurations — Inconsistency causes app submission rejection
- [ ] [CRITICAL] Test all user-facing features function as described in App Store listing — Misrepresentation violates guideline 4.3
- [ ] [HIGH] Verify app does not contain excessive ads or sponsorships — Review guideline 4.7 for acceptable ad frequency
- [ ] [HIGH] Confirm no links to external payment systems outside App Store IAP — Circumventing IAP violates guideline 3.1.1
- [ ] [MEDIUM] Check for compliance with kid-safe guidelines if targeting under 13 — COPPA compliance required for Children category

### Info.plist Configuration
- [ ] [CRITICAL] Set NSAllowsArbitraryLoads to false (use HTTPS only) — Security requirement; allows exceptions only if justified
- [ ] [CRITICAL] Configure NSPrivacyTracking and NSPrivacyTrackingDomains correctly — Required by App Tracking Transparency (ATT) policy
- [ ] [HIGH] Add all required NSPermissionUsageDescription keys for permissions — Missing descriptions cause app rejection
- [ ] [HIGH] Include NSBonjourServices if using mDNS or Bonjour discovery — Bonjour privacy requires explicit declaration
- [ ] [HIGH] Set UISupportedInterfaceOrientations for all supported device orientations — Mismatch causes layout crashes
- [ ] [MEDIUM] Configure NSLocalNetworkUsageDescription for local network access — Required iOS 14+ for .local network queries
- [ ] [MEDIUM] Add NSPhotoLibraryAddOnlyUsageDescription if only adding photos — Different from read/write permission descriptor

### Privacy Manifest Compliance
- [ ] [CRITICAL] Create PrivacyInfo.xcprivacy with complete API declarations — Privacy manifest is now required for App Store submission
- [ ] [CRITICAL] Declare all NSPrivacyTracking purposes in privacy manifest — Failure to declare tracking prevents app submission
- [ ] [HIGH] Document all NSPrivacyAccessedAPICategoryType entries used by frameworks — Third-party SDK compliance verification needed
- [ ] [HIGH] Verify no undeclared APIs in PrivacyInfo.xcprivacy against actual implementation — Mismatches cause automatic rejection
- [ ] [MEDIUM] Include NSPrivacyTracking boolean and tracking domain list — Transparency requirement for user privacy

### Screenshots and Metadata
- [ ] [CRITICAL] Create 5 localized screenshots for each device size (iPhone 6.7", iPhone 5.5", iPad 12.9") — Missing or wrong sizes cause rejection
- [ ] [CRITICAL] Write compelling app preview text in 170 characters max per screenshot — First screenshot is most critical for ASO
- [ ] [HIGH] Provide accurate app description (4000 chars max) matching actual functionality — Marketing description must be truthful
- [ ] [HIGH] Set correct app category and subcategory matching primary purpose — Wrong categorization affects discoverability
- [ ] [MEDIUM] Add promotional artwork (1024x768px) if submitting to top charts — Improves marketing and store visibility
- [ ] [MEDIUM] Configure keyword field (100 chars) with high-intent search terms — Avoid keyword stuffing; focus on discoverability

### TestFlight Testing
- [ ] [CRITICAL] Test on physical devices (not simulator) for final validation — Simulator performance differs significantly from real hardware
- [ ] [CRITICAL] Run full TestFlight beta with minimum 100 internal testers or App Store Connect device testing — Real-world testing reveals edge cases
- [ ] [HIGH] Test all sign-in methods and account recovery flows on TestFlight — Live environment testing essential before launch
- [ ] [HIGH] Verify all IAP and subscription flows complete successfully — Sandbox testing differs from production behavior
- [ ] [MEDIUM] Test on minimum supported iOS version (e.g., iOS 13 if targeting 13+) — Backward compatibility verification required

### Crash-Free Rate and Performance
- [ ] [CRITICAL] Achieve 99.5%+ crash-free rate across TestFlight beta period — Below this indicates critical stability issues
- [ ] [CRITICAL] Verify app handles low memory conditions gracefully (test with memory warnings) — Memory pressure crashes common in real-world use
- [ ] [HIGH] Monitor ANR (Application Not Responding) equivalent: main thread blocked >5 seconds causes hangs — Test with profiler
- [ ] [HIGH] Verify all network operations timeout after 30 seconds maximum — Hung network requests drain battery
- [ ] [MEDIUM] Test background tasks complete within allotted time budgets — Background processing timeouts cause silent failures

### Accessibility Audit
- [ ] [CRITICAL] Enable VoiceOver and test all screens with gestures alone — Screen reader compatibility is legal requirement
- [ ] [CRITICAL] Verify all interactive elements have accessibility labels and hints — Missing labels prevent VoiceOver users from using app
- [ ] [HIGH] Ensure minimum touch target size of 44x44 points (standard is 44 for Apple guidelines) — Smaller targets violate accessibility standards
- [ ] [HIGH] Verify color contrast ratio of 4.5:1 for all text and controls — WCAG AA standard required
- [ ] [MEDIUM] Test with Dynamic Type sizes up to xxL and verify layout integrity — Font scaling affects accessibility

### App Tracking Transparency (ATT)
- [ ] [CRITICAL] Implement ATT permission prompt before tracking user across apps — Required if using tracking identifiers
- [ ] [CRITICAL] Request IDFA permission only if necessary for core functionality — Tracking permission scope must be justified
- [ ] [HIGH] Configure privacy tracking in Info.plist and PrivacyInfo.xcprivacy correctly — Mismatch causes rejection
- [ ] [MEDIUM] Handle user declining ATT gracefully without degraded experience — Never punish privacy-conscious users

### Export Compliance
- [ ] [CRITICAL] Complete App Privacy section in App Store Connect — Required for all apps; must be accurate
- [ ] [CRITICAL] Add NSExceptionDomains for any HTTP exceptions with justification — HTTP exceptions require technical explanation
- [ ] [HIGH] Declare encryption usage if using custom cryptography — Some encryption triggers export regulations
- [ ] [MEDIUM] Verify compliance with regional privacy laws (GDPR, CCPA, LGPD) — Data residency requirements vary by region

---

## 2. Pre-Launch Checklist (Android)

### Play Store Policies
- [ ] [CRITICAL] Review all 13 Google Play Core Policies sections for violations — Policy violation results in app removal and account strikes
- [ ] [CRITICAL] Test app on minimum target API level specified in manifest — Google Play enforces target API level minimum (currently 34+)
- [ ] [CRITICAL] Verify app does not request unnecessary permissions — Over-permissioning violates policy 5.2
- [ ] [HIGH] Confirm no deceptive ads, imagery, or descriptions that mislead users — Misleading content violates policy 4.1
- [ ] [HIGH] Test app stability on at least 2-3 different device types and API levels — Crash reports from real devices impact rating
- [ ] [MEDIUM] Add proper app icon meeting design guidelines (192x192dp minimum) — Low quality icon affects discoverability

### Target SDK and Compilations
- [ ] [CRITICAL] Set targetSdkVersion to Google Play minimum (currently Android 34+) — Older targets rejected; use latest available
- [ ] [CRITICAL] Build and test with compileSdkVersion matching targetSdkVersion — Mismatch causes runtime issues on latest Android versions
- [ ] [HIGH] Test app on target API level minimum with all required permissions requested at runtime — Permission flow essential for target SDK 31+
- [ ] [HIGH] Verify app does not depend on deprecated APIs removed in target SDK — Deprecated APIs cause crashes on newer OS versions
- [ ] [MEDIUM] Review and implement all Android version-specific changes (scoped storage, package visibility, etc.) — OS version changes require code adaptation

### Permissions Management
- [ ] [CRITICAL] Request runtime permissions only when feature is accessed, not at app launch — Upfront permission requests reduce install rate
- [ ] [CRITICAL] Implement runtime permission handling with rationale dialogs for sensitive permissions — PHONE_STATE, READ_CONTACTS, etc. require explanation
- [ ] [HIGH] Declare all requested permissions in AndroidManifest.xml with clear rationale — Undeclared permission usage violates policy
- [ ] [HIGH] Request only permissions necessary for app functionality — Over-permissioning violates policy 5.2
- [ ] [MEDIUM] Handle permission denial gracefully with fallback behavior — Never crash when permission denied

### Code Obfuscation (ProGuard/R8)
- [ ] [CRITICAL] Enable R8 minification in release builds (default via Gradle) — Obfuscation required to meet code reduction standards
- [ ] [CRITICAL] Create proper keep rules for libraries, classes, and methods that need reflection access — Improper keeps cause runtime crashes
- [ ] [HIGH] Test obfuscated app thoroughly for crashes and unexpected behavior — Minification can introduce subtle bugs
- [ ] [HIGH] Configure keep rules to preserve public API and dependency injection frameworks — Common issue: Retrofit, Gson, Dagger classes stripped incorre- [ ] [MEDIUM] Enable shrinking and optimize options alongside obfuscation — Reduces APK size 20-50%

### ANR Rate and Crash-Free Rate
- [ ] [CRITICAL] Achieve 99.5%+ crash-free rate across beta testing — Below this indicates serious stability issues
- [ ] [CRITICAL] Maintain ANR (Application Not Responding) rate below 0.2% — >5 second main thread blocks cause ANRs and crashes
- [ ] [HIGH] Move all network, database, and file I/O operations off main thread — Main thread I/O is primary ANR cause
- [ ] [HIGH] Use strict mode in debug builds to catch ANR-causing violations — StrictMode.enableDefaults() catches main thread issues
- [ ] [MEDIUM] Test with profiler to verify main thread takes <16ms per frame (60fps target) — Frame rate drops to <60fps when main thread blocked

### Store Listing Quality
- [ ] [CRITICAL] Create minimum 2 screenshots in each supported language (must show core features) — Missing screenshots hurt discoverability
- [ ] [CRITICAL] Write 80-character title and 4000-character description accurately describing functionality — Misleading descriptions violate policy
- [ ] [HIGH] Add high-quality promotional banner (1024x500px) and icon (512x512px) — Imagery affects store conversion rate
- [ ] [HIGH] Configure app category, content rating, and target audience correctly — Wrong categorization reduces visibility
- [ ] [MEDIUM] Fill in all localization fields for primary markets (language and region) — Localization improves global reach

### Content Rating
- [ ] [CRITICAL] Complete Google Play content rating questionnaire accurately for target audience — False ratings cause app removal
- [ ] [CRITICAL] Ensure app maturity rating matches actual content (violence, language, sexual content, etc.) — Rating mismatch violates policy
- [ ] [HIGH] Classify target audience age group correctly (kids, teens, mature audiences) — Age classification required for distribution
- [ ] [MEDIUM] Review IARC rating system alignment with ESRB/PEGI standards — Rating should be consistent across systems

### Data Safety Section
- [ ] [CRITICAL] Declare all personal data categories collected by app (contacts, location, payment info, etc.) — Incomplete declaration violates transparency policy
- [ ] [CRITICAL] Specify data retention practices and whether data is deleted when user deletes app — Data safety transparency required
- [ ] [HIGH] Declare whether data is shared with third-party services and for what purposes — Third-party sharing must be disclosed
- [ ] [HIGH] Confirm app practices encryption in transit and at rest for sensitive data — Security declaration required
- [ ] [MEDIUM] List all permissions requested and justify each in data safety section — Permission justification needed for sensitive permissions

### Large Screen Support
- [ ] [CRITICAL] Test app on tablet devices (7" and 10"+ screens) if targeting large screens — Large screen support now expected by Play Store
- [ ] [CRITICAL] Verify UI layout scales properly and uses available screen real estate on tablets — Stretched or broken layouts violate quality guidelines
- [ ] [HIGH] Use responsive layouts (ConstraintLayout, Jetpack Compose) that adapt to screen size — Fixed-size layouts don't scale
- [ ] [HIGH] Test landscape and portrait orientations on tablets and phones — Orientation changes must not crash or lose state
- [ ] [MEDIUM] Implement proper multi-pane layouts for tablets if applicable — Tablets expect optimized UIs, not phone layouts stretched

---

## 3. Code Review Checklist (Mobile)

### Memory Management
- [ ] [CRITICAL] Search codebase for leaked listeners, callbacks, and event subscriptions — Leaked listeners accumulate and consume memory
- [ ] [CRITICAL] Verify all Observable/Flow subscriptions are disposed in onDestroy/onCleared lifecycle methods — Undisposed subscriptions leak memory
- [ ] [HIGH] Check for circular references between ViewModels, repositories, and UI components — Circular references prevent garbage collection
- [ ] [HIGH] Verify Bitmap resources are recycled and not stored in static fields — Large Bitmaps in static fields cause OOM crashes
- [ ] [MEDIUM] Confirm no Context references stored in static fields or long-lived objects — Context leaks prevent Activity/Fragment destruction

### Lifecycle Awareness
- [ ] [CRITICAL] Verify all subscriptions respect Activity/Fragment lifecycle (stop when paused) — Subscriptions continuing when paused cause memory bloat
- [ ] [CRITICAL] Confirm background operations (network, database) stop when app paused or destroyed — Running operations after destruction cause crashes
- [ ] [HIGH] Use LifecycleOwner pattern for observers and listeners — Manual lifecycle tracking is error-prone
- [ ] [HIGH] Verify UI updates only happen when lifecycle state is STARTED/RESUMED — Updating paused UI causes crash
- [ ] [MEDIUM] Test app state restoration after process death (configuration changes, low memory) — State must survive OS-initiated process death

### Thread Safety
- [ ] [CRITICAL] Verify all shared mutable state is protected by synchronization (mutex, AtomicReference, etc.) — Data races cause unpredictable crashes
- [ ] [CRITICAL] Ensure database queries and writes use appropriate threading (Room with suspend functions, proper Dispatchers) — Unprotected DB access causes crashes
- [ ] [HIGH] Confirm UI modifications only happen on main thread — Non-main-thread UI updates cause crashes
- [ ] [HIGH] Use proper Dispatchers for coroutines (Dispatchers.Main for UI, Dispatchers.IO for I/O) — Wrong dispatcher causes thread errors
- [ ] [MEDIUM] Verify no blocking operations on main thread (network, database, file I/O) — Main thread blocking causes ANRs

### Error Handling
- [ ] [CRITICAL] Verify all network requests handle failures (timeout, 5xx, no connectivity) — Unhandled network errors crash app
- [ ] [CRITICAL] Confirm all try-catch blocks rethrow or log errors; no silent failures — Silent error swallowing hides bugs
- [ ] [HIGH] Verify all database transactions handle integrity constraint violations — DB errors must be caught and handled gracefully
- [ ] [HIGH] Check all file operations handle FileNotFoundException, IOException gracefully — File operation errors must not crash
- [ ] [MEDIUM] Verify JSON parsing includes fallback defaults for missing fields — Missing fields in JSON responses cause crashes

### Accessibility Labels
- [ ] [CRITICAL] Verify all interactive buttons have contentDescription set (Android) or accessibilityLabel (iOS) — Missing labels prevent screen reader access
- [ ] [CRITICAL] Confirm images used as controls have non-empty contentDescription — Decorative images must have null description
- [ ] [HIGH] Ensure all EditTexts have hints or labels in UI (not just contentDescription) — Hint text helps both accessibility and UX
- [ ] [HIGH] Verify semantic structure: use semantic HTML/composables, not just visual arrangement — Semantic structure essential for screen readers
- [ ] [MEDIUM] Check that all form inputs are marked with correct inputType and IME options — Helps keyboard selection and accessibility

### Hardcoded Strings and Configuration
- [ ] [CRITICAL] Verify no hardcoded API keys, tokens, or secrets anywhere in code or config files — Hardcoded secrets are exploitable
- [ ] [CRITICAL] Confirm all user-facing strings are in localization files (strings.xml, Localizable.strings) — Hardcoded strings prevent localization
- [ ] [HIGH] Check for hardcoded URLs, API endpoints, or environment-specific values in code — Environment-specific values should be in config
- [ ] [HIGH] Verify no hardcoded feature flags or debug settings in production code — Feature flags should be centralized
- [ ] [MEDIUM] Confirm all numeric constants (timeouts, retry counts, thresholds) are named constants — Magic numbers are unmaintainable

### Secret Management
- [ ] [CRITICAL] Verify secrets are never logged or exposed in error messages — Secrets in logs are accessible via adb logcat
- [ ] [CRITICAL] Confirm API keys stored in secure storage (Keystore on Android, Keychain on iOS) — Secrets in SharedPreferences/UserDefaults are readable
- [ ] [HIGH] Use obfuscated API keys or environment-specific configurations — Plaintext keys in code are exploitable
- [ ] [HIGH] Verify no secrets in build configs, strings.xml, or .plist files — Build config secrets accessible via reverse engineering
- [ ] [MEDIUM] Confirm authentication tokens are short-lived with refresh mechanism — Long-lived tokens increase compromise risk

### Proper Disposal and Cleanup
- [ ] [CRITICAL] Verify all resources (streams, database cursors, file handles) are closed in finally blocks or try-with-resources — Unclosed resources leak file handles
- [ ] [CRITICAL] Confirm all background threads/coroutines are cancelled on lifecycle disposal — Orphaned threads consume resources
- [ ] [HIGH] Check that all View/View Model subscriptions are disposed when component destroyed — Undisposed subscriptions leak memory
- [ ] [HIGH] Verify all timers, alarms, and scheduled tasks are cancelled in cleanup — Cancelled scheduled tasks prevent wakeups
- [ ] [MEDIUM] Confirm all listeners registered in onResume are unregistered in onPause — Unbalanced listener registration causes leaks

### State Restoration
- [ ] [CRITICAL] Verify app state is saved in savedInstanceState/Bundle or ViewModel during configuration change — Lost state after rotation is poor UX
- [ ] [CRITICAL] Test app after process death: stop process via Android Studio and verify state restored — State loss after process death is critical bug
- [ ] [HIGH] Confirm all UI state (scroll position, input values, selections) is restored after recreation — Lost UI state is major UX regression
- [ ] [HIGH] Verify no transient state (API results, temporary data) persisted across app restarts — Stale cached state causes bugs
- [ ] [MEDIUM] Check that focus and scroll position are restored for accessibility — Focus restoration important for accessibility users

---

## 4. Security Audit Checklist

### OWASP Mobile Top 10 Coverage
- [ ] [CRITICAL] Audit code for injection vulnerabilities (SQL injection via string concat, command injection) — Injection attacks compromise data integrity
- [ ] [CRITICAL] Verify all APIs enforce authentication and authorization (no missing permission checks) — Missing auth allows unauthorized access
- [ ] [CRITICAL] Check for insecure data storage (no sensitive data in SharedPreferences, plaintext, or unencrypted files) — Unencrypted storage readable via backup or root
- [ ] [HIGH] Verify all API communication uses TLS/SSL with certificate validation (no ignoring cert errors) — MITM attacks possible with unvalidated certs
- [ ] [HIGH] Scan for insecure cryptography (weak algorithms, hardcoded keys, ECB mode) — Weak crypto compromises encryption
- [ ] [MEDIUM] Check for reverse engineering risks (no unobfuscated sensitive logic) — Reverse engineering exposes business logic

### Certificate Pinning
- [ ] [CRITICAL] Implement certificate pinning for all backend API domains — Certificate pinning prevents MITM attacks via compromised CAs
- [ ] [CRITICAL] Pin to multiple certificates (primary + backup) to allow rotation without app update — Single-pin certificates create emergency scenarios
- [ ] [HIGH] Test certificate pinning works in production and development environments — Development overrides often accidentally left in
- [ ] [HIGH] Document pin rotation process and backup certificate strategy — Pin rotation must be planned to avoid app breakage
- [ ] [MEDIUM] Consider using public key pinning over certificate pinning for flexibility — Public key pinning survives certificate renewals

### Biometric Authentication Implementation
- [ ] [CRITICAL] Verify BiometricPrompt is used (not deprecated deprecated BiometricManager) — Deprecated APIs lack security updates
- [ ] [CRITICAL] Confirm biometric data never stored locally; used only to unlock cryptographic keys — Storing biometric data is major security risk
- [ ] [HIGH] Test fallback to password/PIN when biometric unavailable or fails — Biometric should not be only auth method
- [ ] [HIGH] Verify crypto operations triggered by biometric unlock happen within secure context — Biometric auth must protect subsequent operations
- [ ] [MEDIUM] Confirm enrollment verification: app checks biometric enrollment within grace period — Prevents attacks via changed enrollments

### Token Storage
- [ ] [CRITICAL] Store authentication tokens only in Keychain (iOS) or Keystore (Android) — Memory and SharedPreferences storage is insecure
- [ ] [CRITICAL] Implement token refresh mechanism: refresh tokens before expiry — Expired token handling must be graceful
- [ ] [HIGH] Verify tokens cleared from secure storage on logout — Tokens remaining in storage after logout allow unauthorized access
- [ ] [HIGH] Ensure refresh token secrets are never exposed in logs or error messages — Refresh token compromise allows credential theft
- [ ] [MEDIUM] Implement token expiry monitoring and refresh before expiry — Waiting for token to expire creates window of failures

### Screenshot Prevention
- [ ] [CRITICAL] Enable FLAG_SECURE on Activities containing sensitive data (banking, passwords) — Screenshots accessible via device backup
- [ ] [CRITICAL] Test that screenshots are actually prevented on lockscreen and recent apps screen — FLAG_SECURE sometimes ineffective
- [ ] [HIGH] Verify sensitive data removed from UI when app backgrounded — UI still visible in recent apps/lock screen
- [ ] [MEDIUM] Consider hiding sensitive fields (passwords, PINs) during input — Masked input reduces screenshot exposure

### Debugger Detection
- [ ] [HIGH] Implement debugger detection to prevent step-through debugging of sensitive code — Debugger access allows runtime manipulation
- [ ] [HIGH] Test that debug protections are disabled in debug builds but enabled in release — Debug builds should allow debugging for development
- [ ] [MEDIUM] Verify jailbreak/root detection implemented (if user data at risk) — Rooted/jailbroken devices bypass security measures
- [ ] [MEDIUM] Test that detection doesn't break legitimate development or testing workflows — Detection should not prevent QA testing

### Input Validation
- [ ] [CRITICAL] Validate all user inputs (length, type, format, allowed characters) before processing — Invalid input causes crashes or enables exploits
- [ ] [CRITICAL] Verify all API responses validated before use (not assuming correct structure) — Malicious API responses cause parsing crashes
- [ ] [HIGH] Check that file paths and URLs are validated before opening/loading — Path traversal and URL open attacks possible with unvalidated input
- [ ] [HIGH] Verify SQL queries use parameterized queries, not string concatenation — SQL injection possible with string concatenation
- [ ] [MEDIUM] Confirm numeric inputs are bounds-checked — Out-of-bounds values cause crashes

### WebView Security
- [ ] [CRITICAL] Verify JavaScript disabled if not needed (setJavaScriptEnabled(false)) — Enabled JavaScript enables script injection attacks
- [ ] [CRITICAL] Disable file access if not needed (setAllowFileAccess(false)) — File access allows reading local files
- [ ] [HIGH] Implement WebViewClient.onReceivedSslError to validate SSL (never ignore cert errors) — Ignoring SSL errors enables MITM
- [ ] [HIGH] Disable DOM storage if not needed (setDomStorageEnabled(false)) — DOM storage is accessible to injected scripts
- [ ] [MEDIUM] Configure WebView cache settings appropriately for data sensitivity — Cache may persist sensitive data

---

## 5. Performance Audit Checklist

### Startup Time
- [ ] [CRITICAL] Measure cold start time and verify <2 seconds from tap to app interactive — >2s cold start causes user frustration and app abandonment
- [ ] [CRITICAL] Profile app startup with Android Profiler / Instruments to identify bottlenecks — Profiling reveals slow initializations
- [ ] [HIGH] Move non-essential initializations to background or lazy-loading — Upfront initializations block startup
- [ ] [HIGH] Defer database migrations, analytics initialization, and non-critical libraries to background — These commonly block startup
- [ ] [MEDIUM] Verify warm start (app backgrounded and restored) <1 second — Warm start should be significantly faster

### Frame Rate and Jank
- [ ] [CRITICAL] Maintain 60fps on target devices (test on low-end device of minimum OS) — Frame drops below 60fps cause visible jank
- [ ] [CRITICAL] Profile list scrolling performance (RecyclerView, Compose LazyColumn) with Profiler — List jank is most noticeable jank
- [ ] [HIGH] Verify no dropped frames during animations (track with Profiler frame time) — Animation jank destroys UX feel
- [ ] [HIGH] Check for layout thrashing (repeated layout passes) during scroll or animation — Layout thrashing causes frame drops
- [ ] [MEDIUM] Verify image loading doesn't block scroll (always async/off-thread) — Sync image loading causes jank

### Memory Leaks and Usage
- [ ] [CRITICAL] Run Profiler (Instruments on iOS, Profiler on Android) and verify no memory growth over 5-minute session — Memory growth indicates leaks
- [ ] [CRITICAL] Monitor heap on low-end devices (1GB RAM) and verify no OOM crashes — Low-end devices expose memory issues
- [ ] [HIGH] Verify memory usage drops when navigating away from heavy screens — Memory should be freed when screen cleared
- [ ] [HIGH] Profile memory usage on each main screen and verify <80MB per screen — High per-screen memory limits number of screens usable
- [ ] [MEDIUM] Check for bitmap memory leaks (use Profiler bitmap view) — Bitmaps are largest heap contributors

### Battery Drain
- [ ] [CRITICAL] Measure battery drain over 1 hour with typical usage (monitor with profiler battery tool) — Excessive drain causes bad ratings
- [ ] [CRITICAL] Verify excessive wakeups are not caused by app (check with Battery Historian on Android) — Wakeups drain battery significantly
- [ ] [HIGH] Confirm location services only active when needed — Continuous location drains battery rapidly
- [ ] [HIGH] Verify background sync does not wake device excessively — Background sync should batch requests
- [ ] [MEDIUM] Check for unnecessary wake locks held during data processing — Wake locks prevent device sleep

### Network Efficiency
- [ ] [CRITICAL] Implement request batching and compression (gzip) for all network calls — Network is major battery drain
- [ ] [CRITICAL] Cache API responses appropriately (1 minute for volatile, 1 hour+ for stable data) — Every request costs battery and data
- [ ] [HIGH] Verify no re-requested data unnecessarily (check network tab during typical use) — Duplicate requests waste bandwidth and battery
- [ ] [HIGH] Implement request coalescing (combine multiple requests into single call) — Multiple small requests inefficient
- [ ] [MEDIUM] Use HTTP/2 and compression for all endpoints — HTTP/1.1 without compression is inefficient

### Image Optimization
- [ ] [CRITICAL] Resize images to display size before loading (never load full resolution for thumbnails) — Full-res images waste memory and bandwidth
- [ ] [CRITICAL] Use appropriate image formats (WebP on supported devices, JPEG for photos, PNG for icons) — Wrong formats waste space
- [ ] [HIGH] Implement lazy-loading for images (load on-screen only) — Off-screen images waste memory
- [ ] [HIGH] Verify image cache is cleared appropriately (not unlimited growth) — Uncapped image cache grows unbounded
- [ ] [MEDIUM] Compress images at build time (100% vs 90% quality difference often imperceptible) — High-quality source images waste space

### Bundle Size
- [ ] [CRITICAL] Measure app bundle size and target <100MB download size (install size often 2-3x compressed) — Large apps have lower install rate
- [ ] [CRITICAL] Identify largest dependencies and evaluate necessity (use Gradle build analyzer on Android) — Heavy dependencies impact size
- [ ] [HIGH] Remove unused dependencies and code (ProGuard shrinking must be enabled) — Unused code inflates APK
- [ ] [HIGH] Use dynamic feature modules or on-demand delivery for optional features — Heavy optional features should be downloadable
- [ ] [MEDIUM] Evaluate image and asset usage; replace heavy assets with lighter alternatives — Assets often largest contributors

### Scroll Performance
- [ ] [CRITICAL] Profile list/scroll view framerate and ensure 60fps smooth scrolling (test with Profiler) — Jank during scroll is most-noticed
- [ ] [CRITICAL] Verify list items render in <5ms per frame on target device — >5ms per item causes scroll jank
- [ ] [HIGH] Use ViewHolder pattern (RecyclerView) or object reuse (Compose) to avoid allocation jank — Object allocation during scroll causes GC pauses
- [ ] [HIGH] Implement image caching and async loading in list items — Sync image loading blocks scroll thread
- [ ] [MEDIUM] Verify no expensive computations in onBindViewHolder / list item composition — Expensive work blocks scroll rendering

---

## 6. Accessibility Audit Checklist

### Screen Reader Compatibility
- [ ] [CRITICAL] Enable VoiceOver (iOS) or TalkBack (Android) and traverse entire app using only screen reader — Screen reader navigation is essential
- [ ] [CRITICAL] Verify all interactive elements are reachable and activatable via screen reader — Hidden elements and inactive controls break accessibility
- [ ] [HIGH] Test that screen reader pronunciation is correct (no mispronounced words or abbreviations) — Mispronunciation confuses users
- [ ] [HIGH] Verify images have meaningful alt text (not empty, not "image of...") — Alt text should describe purpose
- [ ] [MEDIUM] Check that decorative images have empty alt text (contentDescription="") — Decorative images shouldn't be announced

### Touch Target Size
- [ ] [CRITICAL] Measure all interactive elements and verify 44px minimum (Apple standard) or 48dp (Android standard) — Smaller targets impossible to reliably tap
- [ ] [CRITICAL] Test target size with accessibility inspector (verify bounding box, not just visual size) — Visual size differs from touch target
- [ ] [HIGH] Verify spacing between targets prevents accidental adjacent taps — Targets too close together cause mis-taps
- [ ] [MEDIUM] Confirm touch targets visible and distinguishable from surrounding content — Targets must be identifiable

### Color Contrast
- [ ] [CRITICAL] Verify color contrast ratio 4.5:1 for normal text, 3:1 for large text (WCAG AA) — Low contrast unreadable for low vision
- [ ] [CRITICAL] Use contrast analyzer tool to audit entire app UI — Manual inspection often misses low-contrast areas
- [ ] [HIGH] Verify important information not conveyed by color alone — Color-only information inaccessible to colorblind users
- [ ] [HIGH] Check button and interactive element contrast (not just text) — Buttons need sufficient contrast
- [ ] [MEDIUM] Test contrast in high-brightness environments (sunny day) — Contrast looks different in bright light

### Dynamic Type / Font Scaling
- [ ] [CRITICAL] Test app with maximum accessibility font size (xxL on iOS, 200% on Android) — Max font size common accessibility need
- [ ] [CRITICAL] Verify UI layout integrity at all text sizes (no clipping, overlapping, or broken layouts) — Enlarged text breaks many apps
- [ ] [HIGH] Test that all UI text scales proportionally (not hardcoded pixel sizes) — Hardcoded sizes don't scale
- [ ] [HIGH] Verify minimum font size of 12pt for body text (larger for older users) — Small text unreadable for low vision
- [ ] [MEDIUM] Confirm line spacing sufficient (1.5x line height minimum) — Tight line spacing affects readability

### Reduced Motion Support
- [ ] [CRITICAL] Check prefers-reduced-motion setting and disable animations for users who set it — Animations cause motion sickness for some users
- [ ] [CRITICAL] Test app with reduce motion enabled (Settings > Accessibility > Motion) — Visual verification essential
- [ ] [HIGH] Verify core functionality not blocked by disabled animations — Animated transitions shouldn't prevent access
- [ ] [MEDIUM] Provide non-animated alternative to critical animated interactions — No animations should block functionality

### Keyboard Navigation
- [ ] [CRITICAL] Traverse entire app using only keyboard (Tab key, arrow keys, Enter/Space) — Keyboard-only navigation essential for motor accessibility
- [ ] [CRITICAL] Verify logical tab order (left-to-right, top-to-bottom) without jumps — Non-logical tab order confuses users
- [ ] [HIGH] Test keyboard navigation without mouse/trackpad access — Keyboard-only users must be able to access all features
- [ ] [HIGH] Confirm all interactive elements keyboard-accessible (buttons, links, inputs, menus) — Some elements often miss keyboard support
- [ ] [MEDIUM] Verify visible focus indicator on all focused elements — Focus must be clearly visible

### Focus Management
- [ ] [CRITICAL] Verify focus moves logically after interactive actions (e.g., modal opens, item selected) — Incorrect focus placement confuses screen reader users
- [ ] [CRITICAL] Test that focus not lost after state changes or data loads — Lost focus disorients accessibility users
- [ ] [HIGH] Confirm modals trap focus (Tab cycles within modal, not outside) — Focus escape from modals allows unintended interaction
- [ ] [HIGH] Verify back button or close action returns focus to opening element — Focus restoration important for workflow
- [ ] [MEDIUM] Check that focus visible on all platforms (not hidden by design) — Focus must be visible

### Semantic Structure
- [ ] [CRITICAL] Verify semantic HTML/layout: use proper heading hierarchy (h1, h2, h3...) — Heading structure enables navigation for screen readers
- [ ] [CRITICAL] Test with accessibility inspector: structure should make sense without visual layout — Semantic structure independent of visual
- [ ] [HIGH] Confirm landmark regions identified (nav, main, aside) for navigation — Landmarks enable quick section navigation
- [ ] [HIGH] Verify form inputs associated with labels (not just placeholder text) — Labels associate inputs for accessibility
- [ ] [MEDIUM] Check that lists marked semantically (list, listitem) not just visually — Semantic lists enable list navigation

---

## 7. Offline Readiness Checklist

### Graceful Degradation
- [ ] [CRITICAL] Verify app remains functional without network (shows cached/offline state) — App must not crash without connectivity
- [ ] [CRITICAL] Test app behavior when losing network mid-operation (pull-to-refresh, form submit) — Network loss must be handled gracefully
- [ ] [HIGH] Ensure cached data displays with "stale" indicator or last-updated timestamp — Users should know when viewing offline data
- [ ] [HIGH] Verify UI shows appropriate message when offline (not generic error) — Users should understand offline state
- [ ] [MEDIUM] Confirm critical features remain accessible without network (e.g., offline mode in maps) — Core features should work offline

### Cached Data Freshness
- [ ] [CRITICAL] Implement cache expiration (configure TTL per endpoint: volatile 1 min, stable 1+ hour) — Stale cache causes bugs and misinformation
- [ ] [CRITICAL] Verify cache invalidation on user-triggered refresh or data mutation — Stale cache after actions confuses users
- [ ] [HIGH] Test cache age display and refresh prompts (notify users of stale data) — Users should know cache age
- [ ] [HIGH] Confirm old cache cleaned up periodically (LRU eviction or time-based cleanup) — Unbounded cache grows indefinitely
- [ ] [MEDIUM] Verify cache not used when user explicitly requested refresh — Force-refresh should bypass cache

### Sync Queue
- [ ] [CRITICAL] Implement reliable offline queue for user mutations (form submits, data changes) — Lost mutations cause data loss
- [ ] [CRITICAL] Verify queued items persist across app restart — Queue lost on app exit causes data loss
- [ ] [HIGH] Test queue processing when connectivity restored (automatic retry) — Queue must auto-process when online
- [ ] [HIGH] Verify queue order preserved (FIFO) for dependent operations — Out-of-order sync causes data corruption
- [ ] [MEDIUM] Monitor queue size and alert if queue grows uncontrollably — Stuck queue indicates sync failure

### Conflict Resolution
- [ ] [CRITICAL] Handle sync conflicts when offline changes conflict with server changes — Conflicts must be detected and resolved
- [ ] [CRITICAL] Provide conflict resolution UI (merge, local, server, custom merge) — Users must control conflict resolution
- [ ] [HIGH] Verify conflict detection uses timestamps or version numbers — Conflicts detected via metadata
- [ ] [HIGH] Test rare scenario: user edits A, someone else edits A concurrently — Concurrent edits must be detected
- [ ] [MEDIUM] Log all conflicts for debugging and analytics — Conflict logging helps identify sync issues

### Offline-First UI
- [ ] [CRITICAL] Design UI to indicate sync status (syncing, synced, conflict, failed) — Users must understand data state
- [ ] [CRITICAL] Show sync progress or estimated sync time for large uploads — Users should know sync progress
- [ ] [HIGH] Provide manual sync/retry button for failed items — Users should be able to manually retry
- [ ] [HIGH] Verify optimistic updates (show change immediately, sync in background) for responsiveness — Optimistic updates improve perceived speed
- [ ] [MEDIUM] Display warning before destructive actions if offline (cannot undo if sync fails) — Users should understand offline risks

### Connectivity Detection
- [ ] [CRITICAL] Implement connectivity detection using platform APIs (ConnectivityManager on Android, NWPathMonitor on iOS) — App must know connectivity state
- [ ] [CRITICAL] Distinguish between WiFi, cellular, and offline — Different networks have different reliability
- [ ] [HIGH] Test connectivity detection accuracy (avoid false positives/negatives) — Connectivity must be correctly detected
- [ ] [HIGH] Verify app responds to connectivity changes (transition online/offline/online seamlessly) — Connectivity changes must trigger appropriate behavior
- [ ] [MEDIUM] Avoid expensive connectivity checks in hot paths — Frequent checks impact performance

### Retry Strategies
- [ ] [CRITICAL] Implement exponential backoff for retries (1s, 2s, 4s, 8s...) — Linear retries create thundering herd
- [ ] [CRITICAL] Set maximum retry count (typically 3-5) and fallback behavior after exhaustion — Infinite retries waste resources
- [ ] [HIGH] Differentiate retry strategies by error type (temporary 5xx retries, permanent 4xx don't) — Wrong errors retried cause hangs
- [ ] [HIGH] Test timeout configuration (reasonable timeout per request type) — Timeouts must balance responsiveness and reliability
- [ ] [MEDIUM] Implement request deduplication to prevent duplicate syncs — Duplicate requests cause duplicate operations

---

## 8. API Integration Checklist

### Error Handling
- [ ] [CRITICAL] Handle all HTTP error codes (4xx, 5xx, network errors, timeouts) — Unhandled errors crash app
- [ ] [CRITICAL] Distinguish error types: client error (4xx), server error (5xx), network error — Different errors require different handling
- [ ] [HIGH] Implement user-friendly error messages (not raw HTTP status) — Users shouldn't see "503 Service Unavailable"
- [ ] [HIGH] Log errors with sufficient context for debugging (request, response, timestamp) — Error logs must be debuggable
- [ ] [MEDIUM] Show retry option for transient errors (5xx, network timeout) — Users should be able to retry

### Timeout Configuration
- [ ] [CRITICAL] Set reasonable request timeouts (typically 30s default, shorter for critical paths) — Infinite hangs frustrate users
- [ ] [CRITICAL] Configure different timeouts for different operations (image load <5s, form submit 30s) — Different operations need different timeouts
- [ ] [HIGH] Test timeout behavior (timeout fires, user notified, app recovers) — Timeouts must be handled gracefully
- [ ] [HIGH] Verify timeout prevents resource exhaustion (cancelled requests freed) — Hung requests waste resources
- [ ] [MEDIUM] Implement read vs. connect timeout separately — Connect timeout <5s, read timeout 30s typical

### Retry with Exponential Backoff
- [ ] [CRITICAL] Implement exponential backoff (1s, 2s, 4s, 8s, 16s max) for retries — Linear retries overload servers
- [ ] [CRITICAL] Add jitter to prevent thundering herd (randomize retry delay ±20%) — Synchronized retries cause server spikes
- [ ] [HIGH] Only retry idempotent operations and specific error codes (5xx, network errors) — Don't retry 4xx or non-idempotent operations
- [ ] [HIGH] Test retry behavior: verify requests eventually succeed or fail gracefully — Retries must work end-to-end
- [ ] [MEDIUM] Cap maximum retry count (typically 3-5) — Infinite retries waste resources

### Response Caching
- [ ] [CRITICAL] Implement HTTP caching headers (Cache-Control, ETag) — Caching reduces bandwidth and latency
- [ ] [CRITICAL] Respect server cache directives (max-age, no-cache, no-store) — Overriding cache directives causes issues
- [ ] [HIGH] Use local cache for expensive queries (database queries cache from API) — Caching reduces network load
- [ ] [HIGH] Implement cache expiration and invalidation (TTL-based or event-based) — Stale cache causes bugs
- [ ] [MEDIUM] Validate cache before using (check freshness, integrity) — Invalid cache causes corruption

### Pagination
- [ ] [CRITICAL] Implement pagination for large lists (offset-based or cursor-based) — Loading all items at once is inefficient
- [ ] [CRITICAL] Test pagination edge cases: empty list, single page, multiple pages, last page — Pagination must handle all cases
- [ ] [HIGH] Implement infinite scroll or load-more pattern appropriately — Pagination UX should match app design
- [ ] [HIGH] Verify pagination tokens/cursors valid and handle pagination cursor expiry — Expired cursors cause failed pagination
- [ ] [MEDIUM] Cache pages appropriately to avoid re-fetching — Page cache reduces network load

### Authentication Token Refresh
- [ ] [CRITICAL] Implement proactive token refresh (refresh before expiry, not after) — Waiting for expiry creates failures
- [ ] [CRITICAL] Handle expired token during request (automatic refresh and retry) — Token expiry must be handled transparently
- [ ] [HIGH] Store refresh tokens securely (Keychain/Keystore only) — Refresh tokens are long-lived secrets
- [ ] [HIGH] Implement logout on persistent token errors (server revoked token) — Persistent auth failures require logout
- [ ] [MEDIUM] Monitor refresh token expiry and require re-login if expired — Refresh token must not outlive user session

### Rate Limiting
- [ ] [CRITICAL] Implement client-side rate limiting (respect server's advertised limits) — Exceeding rate limits causes 429 errors
- [ ] [CRITICAL] Handle 429 (Too Many Requests) responses: back off and retry — 429 responses must trigger back-off
- [ ] [HIGH] Understand API rate limits (requests per minute, per hour) and stay under — Exceeding limits causes API suspension
- [ ] [HIGH] Batch requests appropriately (combine multiple requests if possible) — Batching reduces API call count
- [ ] [MEDIUM] Monitor API usage and alert if approaching limits — Usage tracking prevents limit surprises

### Request Cancellation
- [ ] [CRITICAL] Cancel pending requests when view destroyed or user navigates away — Orphaned requests waste resources
- [ ] [CRITICAL] Verify cancellation actually aborts network operation (check with profiler) — Cancelled requests must not complete
- [ ] [HIGH] Avoid processing responses for cancelled requests — Cancelled response handling avoids crashes
- [ ] [HIGH] Test cancellation during different request stages (connecting, downloading) — Cancellation must work at all stages
- [ ] [MEDIUM] Confirm cancellation doesn't leave partial data or corrupted state — Cancellation must clean up properly

---

## 9. CI/CD Pipeline Checklist

### Automated Testing
- [ ] [CRITICAL] Run unit tests on every commit (target 70%+ code coverage for critical paths) — Unit tests catch regressions early
- [ ] [CRITICAL] Run integration tests before merge (test major features end-to-end) — Integration tests verify system behavior
- [ ] [HIGH] Implement UI tests for critical user flows (login, main features) — UI tests catch UI regressions
- [ ] [HIGH] Run tests on multiple Android API levels / iOS versions — Compatibility testing across versions
- [ ] [MEDIUM] Implement flaky test detection and quarantine — Flaky tests undermine CI confidence

### Code Signing
- [ ] [CRITICAL] Automate code signing certificate management (avoid manual cert handling) — Manual certs error-prone
- [ ] [CRITICAL] Store signing keys in secure vault (not in git repo, not in plaintext) — Signing keys are critical secrets
- [ ] [HIGH] Implement signing key rotation process (rotate every 12-24 months) — Key rotation required for security
- [ ] [HIGH] Verify signed builds correctly (check signatures before distribution) — Signing must be verified
- [ ] [MEDIUM] Maintain backup signing keys for emergency scenarios — Backup keys needed for disaster recovery

### Environment Configurations
- [ ] [CRITICAL] Implement build variants for dev, staging, production environments — Environment separation prevents mistakes
- [ ] [CRITICAL] Verify correct API endpoints used in each build — Wrong endpoints cause critical bugs
- [ ] [HIGH] Configure environment-specific settings (logging level, feature flags) — Environment config centralizes settings
- [ ] [HIGH] Test build variants thoroughly before release — Build variant misconfigurations cause runtime errors
- [ ] [MEDIUM] Document environment setup and configuration — Documentation prevents configuration mistakes

### Build Variants
- [ ] [CRITICAL] Create separate build flavors/schemes for debug/release (debug: large APK with symbols, release: minified/obfuscated) — Build variants enable flexibility
- [ ] [CRITICAL] Verify release builds are obfuscated and optimized (R8 enabled) — Release builds must be optimized
- [ ] [HIGH] Configure appropriate ProGuard/R8 rules for each variant — Wrong keep rules cause crashes
- [ ] [HIGH] Test release builds thoroughly before distribution — Release build testing critical
- [ ] [MEDIUM] Configure signing certificates correctly for each variant — Cert mismatch prevents installation

### Distribution Channels
- [ ] [CRITICAL] Test all distribution channels (internal testing, TestFlight/Firebase Testers, store staging) — Each channel has unique requirements
- [ ] [CRITICAL] Verify correct app version and build number in each distribution — Version mismatch causes confusion
- [ ] [HIGH] Implement separate deployment pipelines for alpha/beta/production — Gradual rollout reduces blast radius
- [ ] [HIGH] Automate upload to stores (Firebase App Distribution for Android, TestFlight for iOS) — Automation reduces errors
- [ ] [MEDIUM] Document distribution process and rollback procedures — Documentation prevents deployment mistakes

### Version Bumping
- [ ] [CRITICAL] Automate version number bumping based on semantic versioning — Manual version bumping error-prone
- [ ] [CRITICAL] Verify version numbers consistent across all build configs — Version mismatch causes confusion
- [ ] [HIGH] Document versioning scheme and release schedule — Versioning strategy should be clear
- [ ] [HIGH] Tag releases in git with version number — Git tags enable quick version lookup
- [ ] [MEDIUM] Update version numbers in documentation and marketing materials — Marketing materials should reflect version

### Changelog Generation
- [ ] [CRITICAL] Automatically generate changelogs from git commit messages — Manual changelog error-prone and outdated
- [ ] [CRITICAL] Format changelogs for user readability (not raw git commits) — Changelogs should be user-facing
- [ ] [HIGH] Include all significant changes (features, fixes, breaking changes) — Complete changelog important for users
- [ ] [HIGH] Publish changelog in App Store / Play Store release notes — Release notes inform users of updates
- [ ] [MEDIUM] Archive changelogs for historical reference — Changelog history useful for users

### Rollback Plan
- [ ] [CRITICAL] Document rollback procedures (how to revert to previous version) — Rollback plan essential for emergencies
- [ ] [CRITICAL] Test rollback procedures in staging environment — Rollback must work when needed
- [ ] [HIGH] Implement feature flags for quick disable/rollback of problematic features — Feature flags enable rollback without app update
- [ ] [HIGH] Maintain previous version builds for emergency rollback — Previous builds needed for rollback
- [ ] [MEDIUM] Establish rollback triggers (crash rate threshold, critical bugs) — Rollback triggers should be defined

---

## 10. Post-Launch Monitoring Checklist

### Crash Reporting Setup
- [ ] [CRITICAL] Integrate crash reporting service (Firebase Crashlytics, Sentry, etc.) — Crash reporting essential for identifying issues
- [ ] [CRITICAL] Verify crash reports received and symbolicated correctly (symbols uploaded to service) — Unsymbolicated crashes unreadable
- [ ] [HIGH] Configure crash alerts (notify on new crash types or spike in crash rate) — Alerts enable quick response
- [ ] [HIGH] Test crash reporting works (trigger test crash and verify reported) — Reporting must function end-to-end
- [ ] [MEDIUM] Implement breadcrumb logging for crash context (track user actions leading to crash) — Breadcrumbs help reproduction

### Performance Monitoring
- [ ] [CRITICAL] Monitor startup time (cold start, warm start) trends over releases — Startup time directly impacts retention
- [ ] [CRITICAL] Track frame rate drops and jank (percentage of frames <60fps) — Jank is most-noticed performance issue
- [ ] [HIGH] Monitor memory usage trends and alert on memory growth — Memory bloat causes crashes on low-end devices
- [ ] [HIGH] Track battery drain metrics (CPU usage, wakeups, location activity) — Battery performance affects user satisfaction
- [ ] [MEDIUM] Monitor network request volume and data usage — Network efficiency impacts battery and data plans

### User Analytics
- [ ] [CRITICAL] Implement analytics event tracking for critical user flows (signup, purchase, primary features) — Analytics reveal feature usage
- [ ] [CRITICAL] Track user retention metrics (day 1, day 7, day 30) by version — Retention indicates app quality
- [ ] [HIGH] Monitor feature adoption (which features used, how often) — Feature usage data guides development priorities
- [ ] [HIGH] Track funnel metrics (signup funnel, purchase funnel) to identify drop-off points — Funnel analysis optimizes conversion
- [ ] [MEDIUM] Implement event filtering to respect user privacy (no PII in analytics) — Analytics must be privacy-respectful

### Error Tracking
- [ ] [CRITICAL] Configure error/exception tracking separately from crashes — Non-fatal errors important for stability
- [ ] [CRITICAL] Set error alert thresholds and notify team on spikes — Error spikes indicate problems
- [ ] [HIGH] Group errors by type and track trends — Error grouping reveals patterns
- [ ] [HIGH] Implement custom error context (user ID, app state, request details) — Context helps debugging
- [ ] [MEDIUM] Track error rates by feature and release — Feature-specific error tracking guides fixes

### A/B Testing Framework
- [ ] [CRITICAL] Implement experiment framework for testing features with subsets of users — A/B testing validates changes before full rollout
- [ ] [CRITICAL] Ensure experiments don't conflict (user assigned to single experiment per factor) — Conflicting experiments confound results
- [ ] [HIGH] Implement statistical significance testing (don't ship until p<0.05) — Underpowered experiments produce false positives
- [ ] [HIGH] Randomize user assignment (consistent, not biased) — Biased assignment invalidates results
- [ ] [MEDIUM] Implement experiment holdout groups for measuring long-term impact — Holdouts reveal delayed effects

### Feature Flags
- [ ] [CRITICAL] Implement feature flags for all major features (enable/disable without app update) — Feature flags enable quick rollback
- [ ] [CRITICAL] Use remote config service for server-side flag control — Flags must be configurable post-launch
- [ ] [HIGH] Implement flag kill switches for problematic features — Kill switches enable emergency disables
- [ ] [HIGH] Monitor feature flag state and alert on unexpected changes — Flag state changes should be monitored
- [ ] [MEDIUM] Document all feature flags and their purposes — Flag documentation prevents confusion

### Remote Configuration
- [ ] [CRITICAL] Implement remote config for server-controlled settings (API URLs, timeouts, cache TTLs) — Remote config enables post-launch adjustments
- [ ] [CRITICAL] Cache remote config locally with fallback defaults — Config must work offline
- [ ] [HIGH] Implement config versioning and rollback capability — Config changes must be reversible
- [ ] [HIGH] Monitor config change impact on user behavior and errors — Config changes may have unintended consequences
- [ ] [MEDIUM] Validate config values before applying (prevent invalid config from breaking app) — Config validation prevents misconfiguration

### Alerting Rules
- [ ] [CRITICAL] Set crash rate alert threshold (>0.5% crash rate alerts immediately) — Crash spikes require immediate investigation
- [ ] [CRITICAL] Configure alerts for critical errors or exceptions — Critical errors must alert the team
- [ ] [HIGH] Implement ANR rate alerts (>0.2% ANR rate triggers alert) — ANR spikes indicate stability issues
- [ ] [HIGH] Set memory usage alerts for low-end devices — Memory issues primarily affect low-end devices
- [ ] [MEDIUM] Configure release health scoring (combines crash rate, ANR rate, error rate) — Health score provides quick status overview
